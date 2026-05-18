"""False-hold autopsy for the common-clock residual exit child.

Research-only; no live bot changes or orders.

The residual child looked promising when its strict sample was all clipped
winners. The newest rows added same-market false holds, so this probe makes the
failure mode explicit and durable for triage/review.
"""
from __future__ import annotations

import json
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
CHILD_JSON = OUT_DIR / "v28_frozen_exit_common_clock_residual_child_watch_latest.json"
PATH_RISK_JSON = OUT_DIR / "v28_exit_common_clock_residual_child_path_risk_latest.json"
OUT_JSON = OUT_DIR / "v28_exit_common_clock_residual_child_false_hold_autopsy_latest.json"
OUT_MD = OUT_DIR / "v28_exit_common_clock_residual_child_false_hold_autopsy_latest.md"


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


def lane_by_label(payload: dict[str, Any], label: str) -> dict[str, Any]:
    return next((row for row in payload.get("lanes") or [] if row.get("label") == label), {})


def row_key(row: dict[str, Any]) -> tuple[str, str, float, float]:
    return (
        str(row.get("market") or ""),
        str(row.get("side") or ""),
        round(fnum(row.get("current_cents")), 3),
        round(fnum(row.get("hold_cents")), 3),
    )


def band_row(row: dict[str, Any]) -> dict[str, Any]:
    p_hold = fnum(row.get("p_hold"))
    gap = fnum(row.get("hold_book_gap"))
    fair = fnum(row.get("fair_drawdown_cents"))
    exit_price = fnum(row.get("exit_price_cents"))
    return {
        "market": row.get("market"),
        "side": row.get("side"),
        "side_won": row.get("side_won"),
        "result": row.get("result"),
        "exit_reason": row.get("exit_reason"),
        "exit_price_cents": exit_price,
        "p_hold": p_hold,
        "hold_book_gap": gap,
        "fair_drawdown_cents": fair,
        "current_cents": fnum(row.get("current_cents")),
        "hold_cents": fnum(row.get("hold_cents")),
        "child_delta_vs_parent_cents": fnum(row.get("child_delta_vs_parent_cents")),
        "candidate_delta_vs_current_cents": fnum(row.get("candidate_delta_vs_current_cents")),
        "tags": row.get("tags") or [],
        "p_hold_band": (
            "lt75" if p_hold < 0.75 else
            "75_79" if p_hold < 0.80 else
            "80_85" if p_hold < 0.85 else
            "85_plus"
        ),
        "book_gap_band": (
            "positive_ge_5pp" if gap >= 0.05 else
            "positive_0_5pp" if gap > 0.0 else
            "flat_to_neg_1pp" if gap >= -0.01 else
            "negative_lt_1pp"
        ),
        "fair_drawdown_band": (
            "positive" if fair > 0 else
            "shallow_negative" if fair >= -2.5 else
            "deep_negative"
        ),
        "exit_price_band": (
            "70_74" if exit_price < 75 else
            "75_79" if exit_price < 80 else
            "other"
        ),
    }


def summarize_group(rows: list[dict[str, Any]]) -> dict[str, Any]:
    market_counts = Counter(str(row.get("market")) for row in rows)
    return {
        "rows": len(rows),
        "net_child_delta_cents": sum(fnum(row.get("child_delta_vs_parent_cents")) for row in rows),
        "market_counts": dict(market_counts),
        "exit_reason_counts": dict(Counter(str(row.get("exit_reason")) for row in rows)),
        "p_hold_band_counts": dict(Counter(str(row.get("p_hold_band")) for row in rows)),
        "book_gap_band_counts": dict(Counter(str(row.get("book_gap_band")) for row in rows)),
        "fair_drawdown_band_counts": dict(Counter(str(row.get("fair_drawdown_band")) for row in rows)),
        "exit_price_band_counts": dict(Counter(str(row.get("exit_price_band")) for row in rows)),
        "tag_counts": dict(Counter(tag for row in rows for tag in row.get("tags") or [])),
        "same_market_clusters": {
            market: count for market, count in market_counts.items() if count >= 2
        },
    }


def build_report() -> dict[str, Any]:
    child = load_json(CHILD_JSON)
    path_risk = load_json(PATH_RISK_JSON)
    strict_lane = lane_by_label(child, "post_child_birth")
    path_lane = lane_by_label(path_risk, "post_child_birth")
    path_rows = {row_key(row): row for row in path_lane.get("rows") or []}

    rows = [band_row(row) for row in strict_lane.get("child_rows") or []]
    for row in rows:
        path = path_rows.get(row_key(row))
        matched = bool(path and path.get("path_matched"))
        row["path_matched"] = matched
        row["worst_adverse_vs_exit_cents"] = None if not matched else path.get("adverse_vs_exit_cents")
        row["min_unrealized_hold_gross_cents"] = None if not matched else path.get("min_unrealized_hold_gross_cents")

    helpful = [row for row in rows if fnum(row.get("child_delta_vs_parent_cents")) > 0]
    harmful = [row for row in rows if fnum(row.get("child_delta_vs_parent_cents")) < 0]
    blockers = list(strict_lane.get("blockers") or [])
    if harmful:
        blockers.append("strict_false_holds_present")
    if any(count >= 2 for count in Counter(str(row.get("market")) for row in harmful).values()):
        blockers.append("same_market_false_hold_cluster")
    if any(row.get("p_hold_band") == "75_79" for row in harmful):
        blockers.append("p_hold_75_79_false_hold_risk")
    if any(row.get("exit_reason") == "mushroom_v28_probability_reduce" for row in harmful):
        blockers.append("probability_reduce_false_hold_risk")

    interpretation = [
        "Research-only autopsy; no live bot changes or orders.",
        (
            f"Strict post-child rows {strict_lane.get('settled')} settled, "
            f"{strict_lane.get('child_suppressed')} child suppressions, helpful/harmful "
            f"{strict_lane.get('child_helpful')}/{strict_lane.get('child_harmful')}, "
            f"child delta {strict_lane.get('child_delta_vs_parent_cents')}c."
        ),
    ]
    if harmful:
        interpretation.append(
            "False holds are concentrated in probability-reduce exits with p_hold 75-79; "
            "the harmful rows are a same-market cluster, so the child cannot be treated as "
            "a generic clipped-winner repair."
        )

    return {
        "generated_at_utc": utc_now_iso(),
        "child_watch_source": str(CHILD_JSON),
        "path_risk_source": str(PATH_RISK_JSON),
        "strict_lane_summary": {
            "settled": strict_lane.get("settled"),
            "child_suppressed": strict_lane.get("child_suppressed"),
            "child_helpful": strict_lane.get("child_helpful"),
            "child_harmful": strict_lane.get("child_harmful"),
            "child_delta_vs_parent_cents": strict_lane.get("child_delta_vs_parent_cents"),
            "candidate_net_cents": strict_lane.get("candidate_net_cents"),
            "current_net_cents": strict_lane.get("current_net_cents"),
            "delta_vs_current_cents": strict_lane.get("delta_vs_current_cents"),
            "child_loss_control_cost_cents": strict_lane.get("child_loss_control_cost_cents"),
            "full_loss_cushion_estimate": strict_lane.get("full_loss_cushion_estimate"),
            "original_blockers": strict_lane.get("blockers") or [],
            "autopsy_blockers": blockers,
        },
        "helpful_summary": summarize_group(helpful),
        "harmful_summary": summarize_group(harmful),
        "rows": sorted(rows, key=lambda row: fnum(row.get("child_delta_vs_parent_cents"))),
        "interpretation": interpretation,
    }


def write_md(report: dict[str, Any]) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8")
    summary = report.get("strict_lane_summary") or {}
    harmful = report.get("harmful_summary") or {}
    helpful = report.get("helpful_summary") or {}
    lines = [
        "# v28 Exit Common-Clock Residual Child False-Hold Autopsy",
        "",
        "Research-only autopsy. No live bot changes or orders.",
        "",
        f"- Generated UTC: `{report.get('generated_at_utc')}`",
        f"- Child watch source: `{report.get('child_watch_source')}`",
        f"- Path-risk source: `{report.get('path_risk_source')}`",
        "",
        "## Interpretation",
        "",
    ]
    lines.extend(f"- {note}" for note in report.get("interpretation") or [])
    lines.extend([
        "",
        "## Strict Summary",
        "",
        f"- Settled: `{summary.get('settled')}`",
        f"- Child suppressions: `{summary.get('child_suppressed')}`",
        f"- Helpful/harmful: `{summary.get('child_helpful')}/{summary.get('child_harmful')}`",
        f"- Child delta vs parent: `{summary.get('child_delta_vs_parent_cents')}c`",
        f"- Candidate/current/delta: `{summary.get('candidate_net_cents')}c` / `{summary.get('current_net_cents')}c` / `{summary.get('delta_vs_current_cents')}c`",
        f"- Loss-control cost: `{summary.get('child_loss_control_cost_cents')}c`",
        f"- Cushion: `{summary.get('full_loss_cushion_estimate')}`",
        f"- Autopsy blockers: `{summary.get('autopsy_blockers')}`",
        "",
        "## Helpful vs Harmful",
        "",
        f"- Helpful rows: `{helpful.get('rows')}`, net child delta `{helpful.get('net_child_delta_cents')}c`, markets `{helpful.get('market_counts')}`, p-hold bands `{helpful.get('p_hold_band_counts')}`, book-gap bands `{helpful.get('book_gap_band_counts')}`.",
        f"- Harmful rows: `{harmful.get('rows')}`, net child delta `{harmful.get('net_child_delta_cents')}c`, markets `{harmful.get('market_counts')}`, p-hold bands `{harmful.get('p_hold_band_counts')}`, book-gap bands `{harmful.get('book_gap_band_counts')}`.",
        f"- Harmful exit reasons: `{harmful.get('exit_reason_counts')}`",
        f"- Harmful same-market clusters: `{harmful.get('same_market_clusters')}`",
        "",
        "## Rows",
        "",
        "| market | side | won | reason | exit | p_hold | gap | fair dd | current | hold | child delta | path | worst adverse | tags |",
        "|---|---|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|",
    ])
    for row in report.get("rows") or []:
        lines.append(
            f"| `{row.get('market')}` | `{row.get('side')}` | {row.get('side_won')} | "
            f"`{row.get('exit_reason')}` | {fmt(row.get('exit_price_cents'))} | "
            f"{fmt(row.get('p_hold'))} | {fmt(row.get('hold_book_gap'))} | "
            f"{fmt(row.get('fair_drawdown_cents'))} | {fmt(row.get('current_cents'))} | "
            f"{fmt(row.get('hold_cents'))} | {fmt(row.get('child_delta_vs_parent_cents'))} | "
            f"{row.get('path_matched')} | {fmt(row.get('worst_adverse_vs_exit_cents'))} | "
            f"{', '.join(row.get('tags') or [])} |"
        )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    report = build_report()
    write_md(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
