"""Path-risk audit for the common-clock residual exit child.

Research-only; no live bot changes or orders.

The residual child holds selected 70-79c exits that the parent loss guard did
not suppress. Settlement deltas are not enough for account survival, so this
audit joins child-suppressed rows to the captured post-exit path ledger and
measures adverse mark-to-market exposure after the skipped exit.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
CHILD_JSON = OUT_DIR / "v28_frozen_exit_common_clock_residual_child_watch_latest.json"
POST_EXIT_PATH_JSON = OUT_DIR / "v28_post_exit_path_latest.json"
OUT_JSON = OUT_DIR / "v28_exit_common_clock_residual_child_path_risk_latest.json"
OUT_MD = OUT_DIR / "v28_exit_common_clock_residual_child_path_risk_latest.md"

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


def fnum(value: Any, default: float = 0.0) -> float:
    if value is None or value == "":
        return default
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def fmt(value: Any) -> str:
    if value is None:
        return "n/a"
    if isinstance(value, float):
        return f"{value:.2f}"
    return str(value)


def path_rows() -> list[dict[str, Any]]:
    payload = load_json(POST_EXIT_PATH_JSON)
    return [row for row in payload.get("rows") or [] if isinstance(row, dict)]


def lane_rows(lane: dict[str, Any]) -> list[dict[str, Any]]:
    return [row for row in lane.get("child_rows") or [] if isinstance(row, dict)]


def match_path(child: dict[str, Any], paths: list[dict[str, Any]]) -> dict[str, Any] | None:
    market = str(child.get("market") or "")
    side = str(child.get("side") or "")
    current = fnum(child.get("current_cents"))
    hold = fnum(child.get("hold_cents"))
    candidates = [
        row for row in paths
        if str(row.get("market") or "") == market
        and str(row.get("side") or "") == side
    ]
    exact = [
        row for row in candidates
        if abs(fnum(row.get("actual_gross_cents")) - current) < 0.001
        and abs(fnum(row.get("hold_gross_cents")) - hold) < 0.001
    ]
    if exact:
        return exact[0]
    if candidates:
        return min(
            candidates,
            key=lambda row: (
                abs(fnum(row.get("actual_gross_cents")) - current)
                + abs(fnum(row.get("hold_gross_cents")) - hold)
            ),
        )
    return None


def enrich_child(child: dict[str, Any], paths: list[dict[str, Any]]) -> dict[str, Any]:
    path = match_path(child, paths)
    current = fnum(child.get("current_cents"))
    hold = fnum(child.get("hold_cents"))
    worst_mark = None if path is None else fnum(path.get("min_unrealized_hold_gross_cents"))
    best_mark = None if path is None else fnum(path.get("max_unrealized_hold_gross_cents"))
    min_bid = None if path is None else path.get("min_post_exit_bid")
    adverse_vs_exit = None if worst_mark is None else worst_mark - current
    adverse_vs_settlement = None if worst_mark is None else worst_mark - hold
    return {
        "market": child.get("market"),
        "side": child.get("side"),
        "result": child.get("result"),
        "exit_reason": child.get("exit_reason"),
        "current_cents": current,
        "parent_cents": fnum(child.get("parent_cents")),
        "hold_cents": hold,
        "child_delta_vs_parent_cents": fnum(child.get("child_delta_vs_parent_cents")),
        "candidate_delta_vs_current_cents": fnum(child.get("candidate_delta_vs_current_cents")),
        "p_hold": child.get("p_hold"),
        "hold_book_gap": child.get("hold_book_gap"),
        "fair_drawdown_cents": child.get("fair_drawdown_cents"),
        "exit_price_cents": child.get("exit_price_cents"),
        "side_won": child.get("side_won"),
        "tags": child.get("tags") or [],
        "path_matched": path is not None,
        "post_exit_points": None if path is None else path.get("post_exit_points"),
        "min_post_exit_bid": min_bid,
        "min_unrealized_hold_gross_cents": worst_mark,
        "max_unrealized_hold_gross_cents": best_mark,
        "adverse_vs_exit_cents": adverse_vs_exit,
        "adverse_vs_settlement_cents": adverse_vs_settlement,
        "adverse_10c": adverse_vs_exit is not None and adverse_vs_exit <= -10.0,
        "adverse_25c": adverse_vs_exit is not None and adverse_vs_exit <= -25.0,
        "adverse_50c": adverse_vs_exit is not None and adverse_vs_exit <= -50.0,
        "mark_below_zero": worst_mark is not None and worst_mark < 0.0,
        "mark_below_full_loss": worst_mark is not None and worst_mark <= -100.0,
    }


def summarize_lane(lane: dict[str, Any], paths: list[dict[str, Any]]) -> dict[str, Any]:
    rows = [enrich_child(row, paths) for row in lane_rows(lane)]
    with_path = [row for row in rows if row.get("path_matched")]
    adverse_values = [fnum(row.get("adverse_vs_exit_cents")) for row in with_path]
    mark_values = [fnum(row.get("min_unrealized_hold_gross_cents")) for row in with_path]
    blockers: list[str] = []
    settled = int(fnum(lane.get("settled")))
    if settled < MIN_SETTLED:
        blockers.append("settled_lt_30")
    if len(rows) < MIN_SUPPRESSED:
        blockers.append("child_suppressed_decisions_lt_30")
    if int(fnum(lane.get("full_loss_cushion_estimate"))) < MIN_FULL_LOSS_CUSHION:
        blockers.append("full_loss_cushion_lt_3")
    if any(row.get("adverse_25c") for row in with_path):
        blockers.append("post_exit_adverse_25c_present")
    if any(row.get("mark_below_zero") for row in with_path):
        blockers.append("post_exit_mark_below_zero_present")
    if len(with_path) < len(rows):
        blockers.append("missing_post_exit_path_rows")
    return {
        "label": lane.get("label"),
        "strict_forward": lane.get("strict_forward"),
        "settled": settled,
        "child_suppressed": len(rows),
        "rows_with_path": len(with_path),
        "child_helpful": lane.get("child_helpful"),
        "child_harmful": lane.get("child_harmful"),
        "child_delta_vs_parent_cents": lane.get("child_delta_vs_parent_cents"),
        "candidate_net_cents": lane.get("candidate_net_cents"),
        "full_loss_cushion_estimate": lane.get("full_loss_cushion_estimate"),
        "worst_adverse_vs_exit_cents": min(adverse_values) if adverse_values else None,
        "avg_adverse_vs_exit_cents": (sum(adverse_values) / len(adverse_values)) if adverse_values else None,
        "worst_unrealized_hold_mark_cents": min(mark_values) if mark_values else None,
        "adverse_10c_rows": sum(1 for row in with_path if row.get("adverse_10c")),
        "adverse_25c_rows": sum(1 for row in with_path if row.get("adverse_25c")),
        "adverse_50c_rows": sum(1 for row in with_path if row.get("adverse_50c")),
        "mark_below_zero_rows": sum(1 for row in with_path if row.get("mark_below_zero")),
        "mark_below_full_loss_rows": sum(1 for row in with_path if row.get("mark_below_full_loss")),
        "blockers": blockers,
        "rows": sorted(rows, key=lambda row: fnum(row.get("adverse_vs_exit_cents"), 999.0)),
    }


def build_report() -> dict[str, Any]:
    child = load_json(CHILD_JSON)
    paths = path_rows()
    lanes = [summarize_lane(lane, paths) for lane in child.get("lanes") or []]
    post = next((lane for lane in lanes if lane.get("label") == "post_child_birth"), {})
    interpretation = [
        "Research-only path-risk audit; no live bot changes or orders.",
        "This audit checks whether residual-child held exits required surviving large adverse marks after the skipped exit.",
    ]
    if post:
        interpretation.append(
            f"Strict post-child path rows {post.get('rows_with_path')}/{post.get('child_suppressed')}; "
            f"worst adverse vs exit {post.get('worst_adverse_vs_exit_cents')}c, "
            f"adverse 10/25/50 rows {post.get('adverse_10c_rows')}/"
            f"{post.get('adverse_25c_rows')}/{post.get('adverse_50c_rows')}, "
            f"blockers {post.get('blockers')}."
        )
    return {
        "generated_at_utc": utc_now_iso(),
        "child_watch_source": str(CHILD_JSON),
        "post_exit_path_source": str(POST_EXIT_PATH_JSON),
        "lanes": lanes,
        "interpretation": interpretation,
    }


def write_md(report: dict[str, Any]) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8")
    lines = [
        "# v28 Exit Common-Clock Residual Child Path Risk",
        "",
        "Research-only path-risk audit. No live bot changes or orders.",
        "",
        f"- Generated UTC: `{report.get('generated_at_utc')}`",
        f"- Child watch source: `{report.get('child_watch_source')}`",
        f"- Post-exit path source: `{report.get('post_exit_path_source')}`",
        "",
        "## Interpretation",
        "",
    ]
    lines.extend(f"- {note}" for note in report.get("interpretation") or [])
    lines.extend([
        "",
        "## Lane Summary",
        "",
        "| lane | strict | settled | child suppressed | path rows | child delta | candidate net | cushion | worst adverse | avg adverse | worst mark | adverse 10/25/50 | below zero | blockers |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|---:|---|",
    ])
    for lane in report.get("lanes") or []:
        lines.append(
            f"| `{lane.get('label')}` | {lane.get('strict_forward')} | {lane.get('settled')} | "
            f"{lane.get('child_suppressed')} | {lane.get('rows_with_path')} | "
            f"{fmt(lane.get('child_delta_vs_parent_cents'))} | {fmt(lane.get('candidate_net_cents'))} | "
            f"{lane.get('full_loss_cushion_estimate')} | {fmt(lane.get('worst_adverse_vs_exit_cents'))} | "
            f"{fmt(lane.get('avg_adverse_vs_exit_cents'))} | {fmt(lane.get('worst_unrealized_hold_mark_cents'))} | "
            f"{lane.get('adverse_10c_rows')}/{lane.get('adverse_25c_rows')}/{lane.get('adverse_50c_rows')} | "
            f"{lane.get('mark_below_zero_rows')} | {', '.join(lane.get('blockers') or []) or 'none'} |"
        )
    lines.extend(["", "## Child Rows", ""])
    for lane in report.get("lanes") or []:
        rows = lane.get("rows") or []
        if not rows:
            continue
        lines.extend([
            f"### {lane.get('label')}",
            "",
            "| market | side | current | parent | hold | child delta | worst mark | adverse vs exit | min bid | points | tags |",
            "|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---|",
        ])
        for row in rows[:12]:
            lines.append(
                f"| `{row.get('market')}` | `{row.get('side')}` | {fmt(row.get('current_cents'))} | "
                f"{fmt(row.get('parent_cents'))} | {fmt(row.get('hold_cents'))} | "
                f"{fmt(row.get('child_delta_vs_parent_cents'))} | "
                f"{fmt(row.get('min_unrealized_hold_gross_cents'))} | "
                f"{fmt(row.get('adverse_vs_exit_cents'))} | {fmt(row.get('min_post_exit_bid'))} | "
                f"{row.get('post_exit_points')} | {', '.join(row.get('tags') or [])} |"
            )
        lines.append("")
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    report = build_report()
    write_md(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
