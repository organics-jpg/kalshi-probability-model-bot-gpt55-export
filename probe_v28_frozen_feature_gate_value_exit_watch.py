"""Frozen feature-gate value-over-hold exit watch.

Research-only; no live bot changes or orders.

The broader value-only exit watch is not enough by itself. This freezes the
narrower overlap suggested by the feature-gate exit/state frontier: evaluate
feature-gate selected-side live entries, and suppress only value-over-hold
exits while leaving probability-reduce/collapse loss control intact.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

from probe_v28_feature_gate_exit_state_repair_frontier import (
    VARIANTS,
    build_report as build_frontier_report,
    fnum,
    selected,
)


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
STATE_JSON = OUT_DIR / "v28_frozen_feature_gate_value_exit_watch_state.json"
OUT_JSON = OUT_DIR / "v28_frozen_feature_gate_value_exit_watch_latest.json"
OUT_MD = OUT_DIR / "v28_frozen_feature_gate_value_exit_watch_latest.md"

PRIMARY_VARIANTS = {
    "suppress_value_over_hold",
    "suppress_value_or_reduce_p_hold80",
}
MIN_SETTLED = 30
MIN_FULL_LOSS_CUSHION = 3


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
    return payload if isinstance(payload, dict) else {}


def load_or_create_state() -> dict[str, Any]:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    if STATE_JSON.exists():
        state = load_json(STATE_JSON)
        if state.get("freeze_ts_utc"):
            return state
    state = {
        "freeze_ts_utc": utc_now_iso(),
        "candidate_family": "frozen_feature_gate_value_exit_watch",
        "primary_candidate": "suppress_value_over_hold",
        "rule": (
            "Within post_feature_freeze_entry_raw03_recross70_abs075 selected-side live overlap, "
            "suppress value_over_hold exits only; keep probability_reduce and probability_collapse exits active."
        ),
        "physics": (
            "Feature-gate selected rows show live exits clipped many settlement winners, while reduce/collapse exits "
            "still saved several losers. The narrow value-over-hold class is the cleanest observed clip mode."
        ),
        "strict_forward_note": "Rows before this timestamp are diagnostic only.",
    }
    STATE_JSON.write_text(json.dumps(state, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return state


def parse_ts(value: Any) -> datetime | None:
    if not value:
        return None
    try:
        dt = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except ValueError:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def is_after_freeze(row: dict[str, Any], freeze_ts: str) -> bool:
    freeze_dt = parse_ts(freeze_ts)
    row_dt = parse_ts(row.get("selected_entry_ts_min") or row.get("selected_exit_ts_max"))
    return bool(freeze_dt and row_dt and row_dt >= freeze_dt)


def score_value(row: dict[str, Any], predicate: Callable[[dict[str, Any]], bool]) -> float:
    return fnum(row.get("hold_net_cents")) if predicate(row) else fnum(row.get("live_net_cents"))


def score_variant(rows: list[dict[str, Any]], variant_name: str, predicate: Callable[[dict[str, Any]], bool], strict_forward: bool) -> dict[str, Any]:
    scored = [row for row in rows if selected(row)]
    candidate_values = [score_value(row, predicate) for row in scored]
    suppressed = [row for row in scored if predicate(row)]
    suppressed_winners = [row for row in suppressed if row.get("side_won")]
    suppressed_losers = [row for row in suppressed if not row.get("side_won")]
    net = sum(candidate_values)
    blockers: list[str] = []
    if strict_forward and len(scored) < MIN_SETTLED:
        blockers.append("settled_lt_30")
    if net <= 0.0:
        blockers.append("net_not_positive")
    if int(max(0.0, net) // 100.0) < MIN_FULL_LOSS_CUSHION:
        blockers.append("full_loss_cushion_lt_3")
    if variant_name not in PRIMARY_VARIANTS:
        blockers.append("diagnostic_variant_not_primary")
    blockers.extend(
        [
            "selected_side_live_overlap_only",
            "hold_to_settlement_assumption",
            "not_live_bot_logic",
        ]
    )
    return {
        "variant": variant_name,
        "strict_forward": strict_forward,
        "settled": len(scored),
        "candidate_net_cents": net,
        "baseline_live_net_cents": sum(fnum(row.get("live_net_cents")) for row in scored),
        "hold_all_net_cents": sum(fnum(row.get("hold_net_cents")) for row in scored),
        "delta_vs_live_cents": net - sum(fnum(row.get("live_net_cents")) for row in scored),
        "wins": sum(1 for value in candidate_values if value >= 0.0),
        "losses": sum(1 for value in candidate_values if value < 0.0),
        "suppressed": len(suppressed),
        "suppressed_winners": len(suppressed_winners),
        "suppressed_losers": len(suppressed_losers),
        "full_loss_cushion_estimate": int(max(0.0, net) // 100.0),
        "blockers": blockers,
        "live_ready": False,
    }


def score_lane(rows: list[dict[str, Any]], label: str, strict_forward: bool) -> dict[str, Any]:
    scored = [
        score_variant(rows, name, predicate, strict_forward)
        for name, _description, predicate in VARIANTS
        if name in PRIMARY_VARIANTS or name == "suppress_value_over_hold"
    ]
    scored.sort(key=lambda row: fnum(row.get("candidate_net_cents")), reverse=True)
    return {
        "label": label,
        "strict_forward": strict_forward,
        "variants": scored,
    }


def build_report() -> dict[str, Any]:
    state = load_or_create_state()
    freeze_ts = str(state.get("freeze_ts_utc") or "")
    frontier = build_frontier_report()
    market_rows = [row for row in frontier.get("markets") or [] if selected(row)]
    diagnostic_rows = [row for row in market_rows if not is_after_freeze(row, freeze_ts)]
    post_rows = [row for row in market_rows if is_after_freeze(row, freeze_ts)]
    lanes = [
        score_lane(diagnostic_rows, "diagnostic_prefreeze_context", False),
        score_lane(post_rows, "post_value_exit_birth", True),
    ]
    post_best = (lanes[1].get("variants") or [{}])[0]
    interpretation = [
        "Research-only frozen watch; no live orders or live bot changes.",
        (
            f"Primary post-birth best is {post_best.get('variant')} with {post_best.get('settled')} rows, "
            f"{post_best.get('candidate_net_cents')}c, W/L {post_best.get('wins')}/{post_best.get('losses')}."
        ),
        "This is not live-ready because it is selected-side overlap only and assumes suppressed exits hold to settlement.",
    ]
    return {
        "generated_at_utc": utc_now_iso(),
        "state": state,
        "frontier_source": str(OUT_DIR / "v28_feature_gate_exit_state_repair_frontier_latest.json"),
        "interpretation": interpretation,
        "lanes": lanes,
    }


def fmt(value: Any) -> str:
    if value is None:
        return "n/a"
    if isinstance(value, float):
        return f"{value:.2f}"
    return str(value)


def write_md(report: dict[str, Any]) -> None:
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8")
    state = report.get("state") or {}
    lines = [
        "# v28 Frozen Feature-Gate Value Exit Watch",
        "",
        "Research-only frozen watch. No live bot changes or orders.",
        "",
        f"- Generated UTC: `{report.get('generated_at_utc')}`",
        f"- Freeze timestamp UTC: `{state.get('freeze_ts_utc')}`",
        f"- Primary candidate: `{state.get('primary_candidate')}`",
        f"- Rule: `{state.get('rule')}`",
        "",
        "## Interpretation",
        "",
    ]
    lines.extend(f"- {note}" for note in report.get("interpretation") or [])
    for lane in report.get("lanes") or []:
        lines.extend(
            [
                "",
                f"## {lane.get('label')}",
                "",
                "| variant | settled | W/L | candidate c | live c | delta c | suppressed | suppressed W/L | cushion | blockers |",
                "|---|---:|---:|---:|---:|---:|---:|---:|---:|---|",
            ]
        )
        for row in lane.get("variants") or []:
            lines.append(
                f"| `{row.get('variant')}` | {row.get('settled')} | {row.get('wins')}/{row.get('losses')} | "
                f"{fmt(row.get('candidate_net_cents'))} | {fmt(row.get('baseline_live_net_cents'))} | "
                f"{fmt(row.get('delta_vs_live_cents'))} | {row.get('suppressed')} | "
                f"{row.get('suppressed_winners')}/{row.get('suppressed_losers')} | "
                f"{row.get('full_loss_cushion_estimate')} | {', '.join(row.get('blockers') or [])} |"
            )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    report = build_report()
    write_md(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
