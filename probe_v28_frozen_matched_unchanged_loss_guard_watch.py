"""Frozen research watch for guarded matched-unchanged exit-loss suppression.

Research-only; no live bot changes or orders.

This freezes the guarded diagnostic separator found in
probe_v28_matched_unchanged_loss_guard_refinement.py. It asks whether rich-ish
exits near the boundary with shallow entry depth and sufficient exit p_hold are
mostly clipped winners when observed after the freeze.

Frozen rule:
    abs_d_sigma <= 0.888798
    exit_cents >= 51
    eligible_depth <= 326.6
    exit_p_hold >= 0.718799

The rule suppresses the current exit in counterfactual scoring and holds to
settlement. This is a research watch only; parent diagnostic evidence cannot
promote it.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from probe_v28_exit_book_gap_candidates import hold_book_gap
from probe_v28_exit_policy_common_clock_watch import build_scored_rows, parse_ts, row_ts


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
STATE_JSON = OUT_DIR / "v28_frozen_matched_unchanged_loss_guard_watch_state.json"
OUT_JSON = OUT_DIR / "v28_frozen_matched_unchanged_loss_guard_watch_latest.json"
OUT_MD = OUT_DIR / "v28_frozen_matched_unchanged_loss_guard_watch_latest.md"

MIN_SETTLED = 30
MIN_SUPPRESSED = 30
MIN_CUSHION_CENTS = 300

RULE = {
    "abs_d_sigma_max": 0.888798,
    "exit_cents_min": 51.0,
    "eligible_depth_max": 326.6,
    "exit_p_hold_min": 0.718799,
}


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


def ensure_state() -> dict[str, Any]:
    state = load_json(STATE_JSON)
    if state.get("freeze_ts_utc"):
        return state
    state = {
        "freeze_ts_utc": utc_now_iso(),
        "rule": RULE,
        "source_probe": "probe_v28_matched_unchanged_loss_guard_refinement.py",
        "source_artifact": str(OUT_DIR / "v28_matched_unchanged_loss_guard_refinement_latest.json"),
        "research_only": True,
        "not_live_bot_logic": True,
        "interpretation": (
            "Freeze timestamp for a research-only forward watch. Parent diagnostic rows do not count "
            "as promotion evidence."
        ),
    }
    STATE_JSON.write_text(json.dumps(state, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return state


def fnum(value: Any) -> float | None:
    if value is None or value == "":
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def row_feature(row: dict[str, Any], feature: str) -> float | None:
    entry = row.get("entry_features") if isinstance(row.get("entry_features"), dict) else {}
    exit_features = row.get("exit_features") if isinstance(row.get("exit_features"), dict) else {}
    mapping = {
        "abs_d_sigma": entry.get("mushroom_v28_abs_d_sigma"),
        "eligible_depth": entry.get("mushroom_v28_eligible_depth"),
        "exit_cents": exit_features.get("mushroom_v28_exit_bid_cents") or row.get("exit_cents"),
        "exit_p_hold": exit_features.get("mushroom_v28_p_hold"),
        "exit_fair_drawdown_cents": exit_features.get("mushroom_v28_fair_drawdown_cents"),
        "hold_book_gap": hold_book_gap(row),
        "p_side": entry.get("mushroom_v28_p_side"),
        "raw_edge_cents": entry.get("mushroom_v28_raw_edge_cents"),
        "ask_cents": entry.get("mushroom_v28_ask_cents"),
    }
    return fnum(mapping.get(feature))


def hold_delta(row: dict[str, Any]) -> float | None:
    current = fnum(row.get("actual_gross_cents"))
    hold = fnum(row.get("hold_gross_cents"))
    if current is None or hold is None:
        return None
    return hold - current


def should_suppress(row: dict[str, Any]) -> bool:
    abs_d = row_feature(row, "abs_d_sigma")
    exit_cents = row_feature(row, "exit_cents")
    depth = row_feature(row, "eligible_depth")
    p_hold = row_feature(row, "exit_p_hold")
    if abs_d is None or exit_cents is None or depth is None or p_hold is None:
        return False
    return (
        abs_d <= RULE["abs_d_sigma_max"]
        and exit_cents >= RULE["exit_cents_min"]
        and depth <= RULE["eligible_depth_max"]
        and p_hold >= RULE["exit_p_hold_min"]
    )


def after_freeze(row: dict[str, Any], freeze_ts: str | None) -> bool:
    freeze_dt = parse_ts(freeze_ts)
    if freeze_dt is None:
        return True
    ts = row_ts(row)
    return ts is not None and ts >= freeze_dt


def compact_row(row: dict[str, Any]) -> dict[str, Any]:
    current = fnum(row.get("actual_gross_cents")) or 0.0
    hold = fnum(row.get("hold_gross_cents")) or 0.0
    return {
        "market": row.get("market"),
        "side": row.get("side"),
        "result": row.get("result"),
        "entry_ts": row.get("entry_ts"),
        "exit_ts": row.get("exit_ts"),
        "exit_reason": row.get("exit_reason"),
        "current_cents": current,
        "hold_cents": hold,
        "delta_cents": hold - current,
        "ask_cents": row_feature(row, "ask_cents"),
        "abs_d_sigma": row_feature(row, "abs_d_sigma"),
        "eligible_depth": row_feature(row, "eligible_depth"),
        "exit_cents": row_feature(row, "exit_cents"),
        "exit_p_hold": row_feature(row, "exit_p_hold"),
        "exit_fair_drawdown_cents": row_feature(row, "exit_fair_drawdown_cents"),
        "hold_book_gap": row_feature(row, "hold_book_gap"),
        "p_side": row_feature(row, "p_side"),
        "raw_edge_cents": row_feature(row, "raw_edge_cents"),
    }


def summarize(rows: list[dict[str, Any]], label: str) -> dict[str, Any]:
    current_vals = [fnum(row.get("actual_gross_cents")) or 0.0 for row in rows]
    hold_vals = [fnum(row.get("hold_gross_cents")) or 0.0 for row in rows]
    selected = [row for row in rows if should_suppress(row)]
    helpful = [row for row in selected if (hold_delta(row) or 0.0) > 0.0]
    harmful = [row for row in selected if (hold_delta(row) or 0.0) < 0.0]
    flat = [row for row in selected if (hold_delta(row) or 0.0) == 0.0]
    candidate_vals = [
        (fnum(row.get("hold_gross_cents")) if should_suppress(row) else fnum(row.get("actual_gross_cents"))) or 0.0
        for row in rows
    ]
    selected_delta = sum((hold_delta(row) or 0.0) for row in selected)
    candidate_net = sum(candidate_vals)
    current_net = sum(current_vals)
    blockers = []
    if len(rows) < MIN_SETTLED:
        blockers.append("settled_lt_30")
    if len(selected) < MIN_SUPPRESSED:
        blockers.append("suppressed_decisions_lt_30")
    if candidate_net <= 0.0:
        blockers.append("net_not_positive")
    if candidate_net - current_net <= 0.0:
        blockers.append("delta_not_positive")
    if harmful:
        blockers.append("suppressed_losers_present")
        blockers.append("loss_control_cost_negative")
    if candidate_net < MIN_CUSHION_CENTS:
        blockers.append("full_loss_cushion_lt_3")
    if label != "post_freeze":
        blockers.append("diagnostic_prefreeze")
    return {
        "label": label,
        "rows": len(rows),
        "selected_rows": len(selected),
        "helpful_rows": len(helpful),
        "harmful_rows": len(harmful),
        "flat_rows": len(flat),
        "current_net_cents": current_net,
        "candidate_net_cents": candidate_net,
        "delta_vs_current_cents": candidate_net - current_net,
        "selected_hold_delta_cents": selected_delta,
        "current_losses": sum(1 for value in current_vals if value < 0.0),
        "candidate_losses": sum(1 for value in candidate_vals if value < 0.0),
        "loss_count_reduction": (
            sum(1 for value in current_vals if value < 0.0)
            - sum(1 for value in candidate_vals if value < 0.0)
        ),
        "worst_harm_cents": min([(hold_delta(row) or 0.0) for row in harmful] or [0.0]),
        "full_loss_cushion": int(candidate_net // 100.0) if candidate_net > 0.0 else 0,
        "blockers": blockers,
        "suppressed_examples": [compact_row(row) for row in selected[:12]],
        "harmful_examples": [compact_row(row) for row in harmful[:8]],
    }


def build_report() -> dict[str, Any]:
    state = ensure_state()
    scored_rows = [row for row in build_scored_rows() if hold_delta(row) is not None]
    post_rows = [row for row in scored_rows if after_freeze(row, state.get("freeze_ts_utc"))]
    report = {
        "generated_at_utc": utc_now_iso(),
        "state": state,
        "diagnostic_summary": summarize(scored_rows, "diagnostic_prefreeze"),
        "post_freeze_summary": summarize(post_rows, "post_freeze"),
    }
    report["interpretation"] = interpretation(report)
    return report


def interpretation(report: dict[str, Any]) -> list[str]:
    post = report.get("post_freeze_summary") or {}
    diag = report.get("diagnostic_summary") or {}
    return [
        "Research-only frozen watch; no live bot logic changes or orders.",
        (
            f"Diagnostic parent selected {diag.get('selected_rows')} rows with "
            f"{diag.get('helpful_rows')}/{diag.get('harmful_rows')} helpful/harmful and "
            f"{diag.get('selected_hold_delta_cents')}c selected hold delta."
        ),
        (
            f"Post-freeze has {post.get('rows')} scored exit rows and {post.get('selected_rows')} selected rows; "
            f"blockers are {post.get('blockers')}."
        ),
        "Only post-freeze rows count for future review. Diagnostic rows are mechanism context only.",
    ]


def money(value: Any) -> str:
    number = fnum(value)
    if number is None:
        return "None"
    return f"{number:.0f}c"


def fmt(value: Any) -> str:
    if isinstance(value, float):
        return f"{value:.6f}"
    if value is None:
        return "None"
    return str(value)


def write_md(report: dict[str, Any]) -> None:
    state = report.get("state") or {}
    lines = [
        "# v28 Frozen Matched-Unchanged Loss Guard Watch",
        "",
        "Research-only frozen watch. No live bot changes or orders.",
        "",
        f"- Generated UTC: `{report.get('generated_at_utc')}`",
        f"- Freeze UTC: `{state.get('freeze_ts_utc')}`",
        f"- Rule: `{state.get('rule')}`",
        "",
        "## Interpretation",
        "",
    ]
    lines.extend(f"- {item}" for item in report.get("interpretation") or [])
    lines.extend([
        "",
        "## Summaries",
        "",
        "| window | rows | selected | helpful/harmful/flat | current net | candidate net | delta | losses current -> candidate | cushion | blockers |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---|",
    ])
    for summary in [report.get("diagnostic_summary") or {}, report.get("post_freeze_summary") or {}]:
        lines.append(
            f"| `{summary.get('label')}` | {summary.get('rows')} | {summary.get('selected_rows')} | "
            f"{summary.get('helpful_rows')}/{summary.get('harmful_rows')}/{summary.get('flat_rows')} | "
            f"{money(summary.get('current_net_cents'))} | {money(summary.get('candidate_net_cents'))} | "
            f"{money(summary.get('delta_vs_current_cents'))} | {summary.get('current_losses')} -> {summary.get('candidate_losses')} | "
            f"{summary.get('full_loss_cushion')} | {', '.join(summary.get('blockers') or []) or 'none'} |"
        )
    post = report.get("post_freeze_summary") or {}
    if post.get("suppressed_examples"):
        lines.extend([
            "",
            "## Post-Freeze Selected Examples",
            "",
            "| market | side/result | current | hold | delta | exit | p_hold | fair dd | gap | p_side | raw edge | abs d | depth |",
            "|---|---|---:|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|",
        ])
        for row in post.get("suppressed_examples") or []:
            lines.append(
                f"| `{row.get('market')}` | {row.get('side')}/{row.get('result')} | "
                f"{money(row.get('current_cents'))} | {money(row.get('hold_cents'))} | {money(row.get('delta_cents'))} | "
                f"{row.get('exit_reason')}@{fmt(row.get('exit_cents'))} | {fmt(row.get('exit_p_hold'))} | "
                f"{fmt(row.get('exit_fair_drawdown_cents'))} | {fmt(row.get('hold_book_gap'))} | "
                f"{fmt(row.get('p_side'))} | {fmt(row.get('raw_edge_cents'))} | {fmt(row.get('abs_d_sigma'))} | "
                f"{fmt(row.get('eligible_depth'))} |"
            )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    report = build_report()
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8")
    write_md(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
