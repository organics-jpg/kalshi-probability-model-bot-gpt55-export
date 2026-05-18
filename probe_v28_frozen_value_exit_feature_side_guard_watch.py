"""Frozen value-exit feature-side guard watch.

Research-only; no live bot changes or orders.

The global value-over-hold exit watch picked up a post-birth suppressed loser.
The feature-gate contrast showed that the loser was opposite the feature-gate
selected side. This freezes an observable guard: suppress a value-over-hold
exit only when the value-exit side agrees with the frozen feature-gate side.
"""
from __future__ import annotations

import json
from collections import Counter
from datetime import datetime, timezone
from math import floor
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
VALUE_ONLY_JSON = OUT_DIR / "v28_frozen_exit_book_gap_value_only_latest.json"
FEATURE_ALIGNMENT_JSON = OUT_DIR / "v28_feature_gate_live_outcome_alignment_latest.json"
STATE_JSON = OUT_DIR / "v28_frozen_value_exit_feature_side_guard_state.json"
OUT_JSON = OUT_DIR / "v28_frozen_value_exit_feature_side_guard_latest.json"
OUT_MD = OUT_DIR / "v28_frozen_value_exit_feature_side_guard_latest.md"

TARGET_FEATURE_CANDIDATE = "post_feature_freeze_entry_raw03_recross70_abs075"
TARGET_VALUE_VARIANT = "value_only_gap15_or_p75"
MIN_SETTLED = 30
MIN_SUPPRESSED = 30
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


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8")


def load_or_create_state() -> dict[str, Any]:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    if STATE_JSON.exists():
        state = load_json(STATE_JSON)
        if state.get("freeze_ts_utc"):
            defaults = default_state(str(state.get("freeze_ts_utc")))
            changed = False
            for key, value in defaults.items():
                if key not in state or state.get(key) in {None, ""}:
                    state[key] = value
                    changed = True
            if changed:
                write_json(STATE_JSON, state)
            return state

    state = default_state(utc_now_iso())
    write_json(STATE_JSON, state)
    return state


def default_state(freeze_ts_utc: str) -> dict[str, Any]:
    return {
        "freeze_ts_utc": freeze_ts_utc,
        "candidate_family": "frozen_value_exit_feature_side_guard_watch",
        "primary_candidate": "value_exit_feature_side_guard",
        "value_variant": TARGET_VALUE_VARIANT,
        "feature_candidate": TARGET_FEATURE_CANDIDATE,
        "rule": (
            "For value_only_gap15_or_p75 value-over-hold exits, suppress only when the "
            "value-exit side matches the frozen feature-gate selected side; otherwise keep the live exit."
        ),
        "physics": (
            "A value-over-hold exit on the same side as a clean feature-gate thesis can be transient winner clipping. "
            "An opposite-side feature-gate thesis is evidence that the exit may be real loss control."
        ),
        "research_only": True,
        "strict_forward_note": "Only rows with exit/entry timestamps after this freeze count as forward evidence.",
    }


def fnum(value: Any, default: float = 0.0) -> float:
    if value is None or value == "":
        return default
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


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


def row_ts(row: dict[str, Any]) -> datetime | None:
    return parse_ts(row.get("exit_ts")) or parse_ts(row.get("entry_ts"))


def feature_rows_by_market() -> dict[str, dict[str, Any]]:
    payload = load_json(FEATURE_ALIGNMENT_JSON)
    for variant in payload.get("variants") or []:
        if variant.get("candidate") != TARGET_FEATURE_CANDIDATE:
            continue
        return {
            str(row.get("market") or ""): row
            for row in variant.get("rows") or []
            if isinstance(row, dict) and row.get("market")
        }
    return {}


def feature_class(row: dict[str, Any], feature: dict[str, Any] | None) -> str:
    if not feature:
        return "no_feature_gate_row"
    if str(row.get("side") or "").lower() == str(feature.get("side") or "").lower():
        return "feature_gate_same_side"
    return "feature_gate_opposite_side"


def side_won(row: dict[str, Any]) -> bool:
    return str(row.get("side") or "").lower() == str(row.get("result") or "").lower()


def compact_row(row: dict[str, Any], feature: dict[str, Any] | None, lane: str) -> dict[str, Any]:
    classification = feature_class(row, feature)
    current = fnum(row.get("current_cents"))
    value_candidate = fnum(row.get("value_only_candidate_cents"), fnum(row.get("candidate_cents")))
    suppress_guarded = bool(row.get("value_only_suppressed")) and classification == "feature_gate_same_side"
    guarded = fnum(row.get("hold_cents")) if suppress_guarded else current
    return {
        "source_lane": lane,
        "market": row.get("market"),
        "side": row.get("side"),
        "result": row.get("result"),
        "side_won": side_won(row),
        "entry_ts": row.get("entry_ts"),
        "exit_ts": row.get("exit_ts"),
        "entry_cents": row.get("entry_cents"),
        "exit_cents": row.get("exit_cents"),
        "exit_reason": row.get("exit_reason"),
        "p_hold": row.get("p_hold"),
        "hold_book_gap": row.get("hold_book_gap"),
        "fair_drawdown_cents": row.get("fair_drawdown_cents"),
        "exit_bid_prob": row.get("exit_bid_prob"),
        "current_cents": current,
        "hold_cents": fnum(row.get("hold_cents")),
        "value_only_candidate_cents": value_candidate,
        "value_only_delta_cents": value_candidate - current,
        "value_only_suppressed": bool(row.get("value_only_suppressed")),
        "feature_side_guard_candidate_cents": guarded,
        "feature_side_guard_delta_cents": guarded - current,
        "feature_side_guard_suppressed": suppress_guarded,
        "feature_class": classification,
        "feature_gate_side": None if not feature else feature.get("side"),
        "feature_gate_source": None if not feature else feature.get("source"),
        "feature_gate_raw_edge": None if not feature else feature.get("raw_edge"),
        "feature_gate_recross_hazard_score": None if not feature else feature.get("recross_hazard_score"),
        "feature_gate_abs_d_sigma": None if not feature else feature.get("abs_d_sigma"),
        "feature_gate_ask_prob": None if not feature else feature.get("ask_prob"),
    }


def value_rows() -> list[dict[str, Any]]:
    payload = load_json(VALUE_ONLY_JSON)
    features = feature_rows_by_market()
    rows: list[dict[str, Any]] = []
    seen: set[tuple[str, str, str, str]] = set()
    for lane in payload.get("lanes") or []:
        if not isinstance(lane, dict):
            continue
        lane_name = str(lane.get("lane") or "")
        for variant in lane.get("variants") or []:
            if not isinstance(variant, dict) or variant.get("variant") != TARGET_VALUE_VARIANT:
                continue
            for row in variant.get("rows") or []:
                if not isinstance(row, dict):
                    continue
                compact = compact_row(row, features.get(str(row.get("market") or "")), lane_name)
                key = (
                    str(compact.get("market") or ""),
                    str(compact.get("side") or ""),
                    str(compact.get("entry_ts") or ""),
                    str(compact.get("exit_ts") or ""),
                )
                if key in seen:
                    continue
                seen.add(key)
                rows.append(compact)
    rows.sort(key=lambda row: str(row.get("entry_ts") or row.get("exit_ts") or ""))
    return rows


def rows_after(rows: list[dict[str, Any]], freeze_ts: str) -> list[dict[str, Any]]:
    freeze = parse_ts(freeze_ts)
    if freeze is None:
        return []
    return [row for row in rows if (ts := row_ts(row)) is not None and ts >= freeze]


def summarize(rows: list[dict[str, Any]], strict_forward: bool) -> dict[str, Any]:
    current_net = sum(fnum(row.get("current_cents")) for row in rows)
    value_net = sum(fnum(row.get("value_only_candidate_cents")) for row in rows)
    guard_net = sum(fnum(row.get("feature_side_guard_candidate_cents")) for row in rows)
    suppressed = [row for row in rows if row.get("feature_side_guard_suppressed")]
    suppressed_winners = [row for row in suppressed if row.get("side_won")]
    suppressed_losers = [row for row in suppressed if not row.get("side_won")]
    blockers: list[str] = []
    if len(rows) < MIN_SETTLED:
        blockers.append("settled_lt_30")
    if len(suppressed) < MIN_SUPPRESSED:
        blockers.append("suppressed_decisions_lt_30")
    if guard_net <= 0.0:
        blockers.append("net_not_positive")
    if guard_net - current_net <= 0.0:
        blockers.append("delta_not_positive")
    if suppressed_losers:
        blockers.append("suppressed_losers_present")
    if floor(max(0.0, guard_net) / 100.0) < MIN_FULL_LOSS_CUSHION:
        blockers.append("full_loss_cushion_lt_3")
    if not strict_forward:
        blockers.append("diagnostic_prefreeze")
    blockers.extend(["hold_to_settlement_assumption", "not_live_bot_logic"])
    return {
        "rows": len(rows),
        "settled": len(rows),
        "strict_forward": strict_forward,
        "current_net_cents": current_net,
        "value_only_net_cents": value_net,
        "feature_side_guard_net_cents": guard_net,
        "delta_vs_current_cents": guard_net - current_net,
        "delta_vs_value_only_cents": guard_net - value_net,
        "feature_side_guard_wins": sum(1 for row in rows if fnum(row.get("feature_side_guard_candidate_cents")) >= 0.0),
        "feature_side_guard_losses": sum(1 for row in rows if fnum(row.get("feature_side_guard_candidate_cents")) < 0.0),
        "wins": sum(1 for row in rows if fnum(row.get("feature_side_guard_candidate_cents")) >= 0.0),
        "losses": sum(1 for row in rows if fnum(row.get("feature_side_guard_candidate_cents")) < 0.0),
        "suppressed_exits": len(suppressed),
        "suppressed_winners": len(suppressed_winners),
        "suppressed_losers": len(suppressed_losers),
        "suppressed_loser_cost_cents": sum(fnum(row.get("feature_side_guard_delta_cents")) for row in suppressed_losers),
        "value_only_suppressed_exits": sum(1 for row in rows if row.get("value_only_suppressed")),
        "full_loss_cushion_estimate": floor(max(0.0, guard_net) / 100.0),
        "feature_class_counts": dict(Counter(row.get("feature_class") for row in rows)),
        "suppressed_feature_class_counts": dict(Counter(row.get("feature_class") for row in suppressed)),
        "blockers": blockers,
        "live_ready": False,
    }


def build_report() -> dict[str, Any]:
    state = load_or_create_state()
    rows = value_rows()
    post_rows = rows_after(rows, str(state.get("freeze_ts_utc") or ""))
    report = {
        "generated_at_utc": utc_now_iso(),
        "state": state,
        "value_only_source": str(VALUE_ONLY_JSON),
        "feature_alignment_source": str(FEATURE_ALIGNMENT_JSON),
        "candidate_live_ready": False,
        "lanes": [
            {
                "label": "diagnostic_from_value_freeze",
                "lane": "diagnostic_from_value_freeze",
                "strict_forward": False,
                "summary": summarize(rows, strict_forward=False),
                "rows": rows,
            },
            {
                "label": "post_feature_side_guard_birth",
                "lane": "post_feature_side_guard_birth",
                "strict_forward": True,
                "summary": summarize(post_rows, strict_forward=True),
                "rows": post_rows,
            },
        ],
    }
    diag = report["lanes"][0]["summary"]
    post = report["lanes"][1]["summary"]
    report["interpretation"] = [
        "Research-only frozen watch; no live bot changes or orders.",
        (
            f"Diagnostic guard net {diag['feature_side_guard_net_cents']}c versus "
            f"value-only {diag['value_only_net_cents']}c and current {diag['current_net_cents']}c."
        ),
        (
            f"Post-birth guard has {post['settled']} rows, {post['suppressed_exits']} suppressions, "
            f"net {post['feature_side_guard_net_cents']}c, blockers {post['blockers']}."
        ),
        "Only the post_feature_side_guard_birth lane can count as forward evidence.",
    ]
    return report


def fmt(value: Any) -> str:
    if value is None:
        return "n/a"
    if isinstance(value, float):
        return f"{value:.2f}"
    return str(value)


def write_md(report: dict[str, Any]) -> None:
    write_json(OUT_JSON, report)
    state = report.get("state") or {}
    lines = [
        "# v28 Frozen Value-Exit Feature-Side Guard Watch",
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
        summary = lane.get("summary") or {}
        lines.extend(
            [
                "",
                f"## {lane.get('lane')}",
                "",
                "| settled | W/L | current c | value-only c | guarded c | delta vs current c | delta vs value c | suppressed | sup W/L | sup loser cost c | cushion | blockers |",
                "|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|",
                (
                    f"| {summary.get('settled')} | {summary.get('wins')}/{summary.get('losses')} | "
                    f"{fmt(summary.get('current_net_cents'))} | {fmt(summary.get('value_only_net_cents'))} | "
                    f"{fmt(summary.get('feature_side_guard_net_cents'))} | {fmt(summary.get('delta_vs_current_cents'))} | "
                    f"{fmt(summary.get('delta_vs_value_only_cents'))} | {summary.get('suppressed_exits')} | "
                    f"{summary.get('suppressed_winners')}/{summary.get('suppressed_losers')} | "
                    f"{fmt(summary.get('suppressed_loser_cost_cents'))} | "
                    f"{summary.get('full_loss_cushion_estimate')} | {', '.join(summary.get('blockers') or [])} |"
                ),
                "",
                f"- Feature classes: `{summary.get('feature_class_counts')}`",
                f"- Suppressed feature classes: `{summary.get('suppressed_feature_class_counts')}`",
            ]
        )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    report = build_report()
    write_md(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
