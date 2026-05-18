"""Mechanism audit for loss-guarded v28 book-gap exit watches.

Research-only; no live bot changes or orders.

This explains why the loss-guarded book-gap rows are cleaner than the broad
book-gap suppression rows: which dangerous false-hold states were avoided by
observable thresholds, and how close current helpful suppressions sit to those
thresholds.
"""
from __future__ import annotations

import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
OUT_JSON = OUT_DIR / "v28_exit_loss_guard_mechanism_audit_latest.json"
OUT_MD = OUT_DIR / "v28_exit_loss_guard_mechanism_audit_latest.md"

SOURCES = {
    "book_gap_suppression": OUT_DIR / "v28_frozen_exit_book_gap_suppression_latest.json",
    "book_gap_loss_guard": OUT_DIR / "v28_frozen_exit_book_gap_loss_guard_latest.json",
    "book_gap_loss_guard_v3": OUT_DIR / "v28_frozen_exit_book_gap_loss_guard_v3_latest.json",
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


def fnum(value: Any, default: float = 0.0) -> float:
    if value is None or value == "":
        return default
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def row_delta(row: dict[str, Any]) -> float:
    if row.get("delta_cents") is not None:
        return fnum(row.get("delta_cents"))
    return fnum(row.get("candidate_cents")) - fnum(row.get("current_cents"))


def strict_rows(payload: dict[str, Any]) -> list[dict[str, Any]]:
    rows = payload.get("rows")
    if isinstance(rows, list):
        return [row for row in rows if isinstance(row, dict) and row.get("result") not in (None, "", "unknown")]
    out: list[dict[str, Any]] = []
    for lane in payload.get("lanes") or []:
        if not isinstance(lane, dict):
            continue
        lane_name = str(lane.get("lane") or "")
        if "diagnostic" in lane_name or "prefreeze" in lane_name:
            continue
        lane_rows = lane.get("rows")
        if isinstance(lane_rows, list):
            out.extend(row for row in lane_rows if isinstance(row, dict) and row.get("result") not in (None, "", "unknown"))
    return out


def freeze_thresholds(payload: dict[str, Any]) -> dict[str, float]:
    freeze = payload.get("freeze") or {}
    return {
        "value_p_hold_floor": fnum(freeze.get("value_p_hold_floor"), 0.85),
        "value_gap_floor": fnum(freeze.get("value_gap_floor"), 0.0),
        "reduce_p_hold_floor": fnum(freeze.get("reduce_p_hold_floor"), 0.79),
        "reduce_gap_floor": fnum(freeze.get("reduce_gap_floor"), 0.0),
        "value_extreme_p_hold_floor": fnum(freeze.get("value_extreme_p_hold_floor"), 0.0),
        "value_fair_drawdown_floor_cents": fnum(freeze.get("value_fair_drawdown_floor_cents"), -999.0),
    }


def danger_tags(row: dict[str, Any]) -> list[str]:
    tags: list[str] = []
    reason = str(row.get("exit_reason") or "")
    p_hold = row.get("p_hold")
    exit_cents = row.get("exit_cents")
    fair_drawdown = row.get("fair_drawdown_cents")
    gap = row.get("hold_book_gap")
    if p_hold is None or exit_cents is None:
        return tags
    p = fnum(p_hold)
    exit_px = fnum(exit_cents)
    fd = fnum(fair_drawdown)
    book_gap = fnum(gap)
    if 0.75 <= p < 0.85:
        tags.append("p_hold_75_85")
    if exit_px >= 60:
        tags.append("exit_cents_gte60")
    if exit_px >= 80:
        tags.append("rich_exit_80_plus")
    if fd > 0:
        tags.append("positive_fair_drawdown")
    if book_gap < 0:
        tags.append("negative_book_gap")
    if "value_over_hold" in reason and 0.75 <= p < 0.85 and fd > 0 and exit_px >= 60:
        tags.append("value_mid_p_positive_drawdown_richish")
    if "probability_reduce" in reason and 0.75 <= p < 0.80 and fd > 0 and exit_px >= 60:
        tags.append("reduce_mid_p_positive_drawdown_richish")
    return tags


def avoidance_reason(row: dict[str, Any], thresholds: dict[str, float]) -> list[str]:
    reason = str(row.get("exit_reason") or "")
    p = fnum(row.get("p_hold"))
    gap = fnum(row.get("hold_book_gap"))
    out: list[str] = []
    if "value_over_hold" in reason:
        if p < thresholds["value_p_hold_floor"]:
            out.append("value_p_hold_below_floor")
        if gap < thresholds["value_gap_floor"]:
            out.append("value_gap_below_floor")
        if thresholds["value_extreme_p_hold_floor"] and p < thresholds["value_extreme_p_hold_floor"]:
            out.append("value_extreme_p_hold_below_floor")
    elif "probability_reduce" in reason:
        if p < thresholds["reduce_p_hold_floor"]:
            out.append("reduce_p_hold_below_floor")
        if gap < thresholds["reduce_gap_floor"]:
            out.append("reduce_gap_below_floor")
    elif "collapse" in reason:
        out.append("collapse_exit_never_suppressed")
    else:
        out.append("not_soft_exit_or_no_exit")
    return out or ["rule_allowed_suppression"]


def margin(row: dict[str, Any], thresholds: dict[str, float]) -> dict[str, float | None]:
    reason = str(row.get("exit_reason") or "")
    p = row.get("p_hold")
    gap = row.get("hold_book_gap")
    if p is None or gap is None:
        return {"p_hold_margin": None, "gap_margin": None}
    if "probability_reduce" in reason:
        return {
            "p_hold_margin": fnum(p) - thresholds["reduce_p_hold_floor"],
            "gap_margin": fnum(gap) - thresholds["reduce_gap_floor"],
        }
    return {
        "p_hold_margin": fnum(p) - thresholds["value_p_hold_floor"],
        "gap_margin": fnum(gap) - thresholds["value_gap_floor"],
    }


def summarize_lane(lane: str, payload: dict[str, Any]) -> dict[str, Any]:
    thresholds = freeze_thresholds(payload)
    rows = strict_rows(payload)
    suppressed = [row for row in rows if row.get("suppressed") is True]
    harmful_suppressed = [row for row in suppressed if row_delta(row) < 0]
    helpful_suppressed = [row for row in suppressed if row_delta(row) > 0]
    danger = [row for row in rows if danger_tags(row)]
    danger_suppressed = [row for row in danger if row.get("suppressed") is True]
    danger_unsuppressed = [row for row in danger if row.get("suppressed") is not True]
    avoided_harm = [row for row in danger_unsuppressed if fnum(row.get("hold_cents")) < fnum(row.get("current_cents"))]
    avoid_reasons = Counter()
    for row in danger_unsuppressed:
        avoid_reasons.update(avoidance_reason(row, thresholds))
    helpful_margins = [margin(row, thresholds) for row in helpful_suppressed]
    p_margins = [item["p_hold_margin"] for item in helpful_margins if item["p_hold_margin"] is not None]
    gap_margins = [item["gap_margin"] for item in helpful_margins if item["gap_margin"] is not None]
    return {
        "lane": lane,
        "freeze_ts_utc": (payload.get("freeze") or {}).get("freeze_ts_utc"),
        "thresholds": thresholds,
        "rows": len(rows),
        "suppressed": len(suppressed),
        "helpful_suppressed": len(helpful_suppressed),
        "harmful_suppressed": len(harmful_suppressed),
        "suppressed_delta_cents": sum(row_delta(row) for row in suppressed),
        "harmful_delta_cents": sum(row_delta(row) for row in harmful_suppressed),
        "danger_rows": len(danger),
        "danger_suppressed": len(danger_suppressed),
        "danger_unsuppressed": len(danger_unsuppressed),
        "avoided_harm_rows": len(avoided_harm),
        "avoided_harm_cents": sum(fnum(row.get("hold_cents")) - fnum(row.get("current_cents")) for row in avoided_harm),
        "avoidance_reason_counts": dict(sorted(avoid_reasons.items())),
        "helpful_min_p_hold_margin": min(p_margins) if p_margins else None,
        "helpful_min_gap_margin": min(gap_margins) if gap_margins else None,
        "top_danger_unsuppressed": [
            {
                "market": row.get("market"),
                "side": row.get("side"),
                "exit_reason": row.get("exit_reason"),
                "exit_cents": row.get("exit_cents"),
                "p_hold": row.get("p_hold"),
                "hold_book_gap": row.get("hold_book_gap"),
                "fair_drawdown_cents": row.get("fair_drawdown_cents"),
                "current_cents": row.get("current_cents"),
                "hold_cents": row.get("hold_cents"),
                "hold_minus_current_cents": fnum(row.get("hold_cents")) - fnum(row.get("current_cents")),
                "danger_tags": danger_tags(row),
                "avoidance_reasons": avoidance_reason(row, thresholds),
            }
            for row in sorted(danger_unsuppressed, key=lambda item: fnum(item.get("hold_cents")) - fnum(item.get("current_cents")))[:8]
        ],
        "top_helpful_suppressed": [
            {
                "market": row.get("market"),
                "side": row.get("side"),
                "exit_reason": row.get("exit_reason"),
                "exit_cents": row.get("exit_cents"),
                "p_hold": row.get("p_hold"),
                "hold_book_gap": row.get("hold_book_gap"),
                "fair_drawdown_cents": row.get("fair_drawdown_cents"),
                "delta_cents": row_delta(row),
                "margins": margin(row, thresholds),
            }
            for row in sorted(helpful_suppressed, key=row_delta, reverse=True)[:8]
        ],
    }


def build_report() -> dict[str, Any]:
    lanes = [summarize_lane(lane, load_json(path)) for lane, path in SOURCES.items()]
    loss_guard = next((row for row in lanes if row["lane"] == "book_gap_loss_guard"), {})
    v3 = next((row for row in lanes if row["lane"] == "book_gap_loss_guard_v3"), {})
    interpretation = [
        "Research-only mechanism audit; no live bot changes or orders.",
        "Broad book-gap suppression still has observed harmful suppressions, so it remains rejected.",
        "Loss-guarded book-gap avoided the current dangerous false-hold rows by p_hold/gap floors, but its clean suppressions are still too few for promotion.",
        f"book_gap_loss_guard current strict suppressions: {loss_guard.get('helpful_suppressed')} helpful / {loss_guard.get('harmful_suppressed')} harmful, delta {loss_guard.get('suppressed_delta_cents')}c.",
        f"book_gap_loss_guard_v3 current strict suppressions: {v3.get('helpful_suppressed')} helpful / {v3.get('harmful_suppressed')} harmful, delta {v3.get('suppressed_delta_cents')}c.",
    ]
    return {
        "generated_at_utc": utc_now_iso(),
        "sources": {lane: str(path) for lane, path in SOURCES.items()},
        "lanes": lanes,
        "interpretation": interpretation,
    }


def fmt(value: Any) -> str:
    if value is None:
        return "n/a"
    if isinstance(value, float):
        return f"{value:.6f}"
    return str(value)


def write_markdown(report: dict[str, Any]) -> None:
    lines = [
        "# v28 Exit Loss-Guard Mechanism Audit",
        "",
        "Research-only. No live bot logic changes, no orders, no process control.",
        "",
        f"- Generated UTC: `{report.get('generated_at_utc')}`",
        "",
        "## Interpretation",
        "",
    ]
    lines.extend(f"- {note}" for note in report.get("interpretation") or [])
    lines.extend(
        [
            "",
            "## Lane Summary",
            "",
            "| lane | rows | suppressed | helpful | harmful | suppress delta | danger rows | danger suppressed | avoided harm rows | avoided harm c | avoid reasons | min p margin | min gap margin |",
            "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|---:|---:|",
        ]
    )
    for row in report.get("lanes") or []:
        lines.append(
            "| "
            + " | ".join(
                [
                    f"`{row.get('lane')}`",
                    str(row.get("rows")),
                    str(row.get("suppressed")),
                    str(row.get("helpful_suppressed")),
                    str(row.get("harmful_suppressed")),
                    fmt(row.get("suppressed_delta_cents")),
                    str(row.get("danger_rows")),
                    str(row.get("danger_suppressed")),
                    str(row.get("avoided_harm_rows")),
                    fmt(row.get("avoided_harm_cents")),
                    str(row.get("avoidance_reason_counts")),
                    fmt(row.get("helpful_min_p_hold_margin")),
                    fmt(row.get("helpful_min_gap_margin")),
                ]
            )
            + " |"
        )
    lines.extend(["", "## Dangerous Unsuppressed Rows", ""])
    for row in report.get("lanes") or []:
        examples = row.get("top_danger_unsuppressed") or []
        if not examples:
            continue
        lines.append(f"### {row.get('lane')}")
        for item in examples:
            lines.append(
                f"- `{item.get('market')}` `{item.get('side')}` hold-current `{fmt(item.get('hold_minus_current_cents'))}c`, "
                f"exit `{item.get('exit_reason')}` `{item.get('exit_cents')}`, p_hold `{item.get('p_hold')}`, "
                f"gap `{item.get('hold_book_gap')}`, fair_drawdown `{item.get('fair_drawdown_cents')}`, "
                f"avoided by `{', '.join(item.get('avoidance_reasons') or [])}`"
            )
        lines.append("")
    lines.extend(["", "## Helpful Suppressed Rows", ""])
    for row in report.get("lanes") or []:
        examples = row.get("top_helpful_suppressed") or []
        if not examples:
            continue
        lines.append(f"### {row.get('lane')}")
        for item in examples:
            margins = item.get("margins") or {}
            lines.append(
                f"- `{item.get('market')}` `{item.get('side')}` delta `{fmt(item.get('delta_cents'))}c`, "
                f"exit `{item.get('exit_reason')}` `{item.get('exit_cents')}`, p_hold `{item.get('p_hold')}`, "
                f"gap `{item.get('hold_book_gap')}`, p_margin `{fmt(margins.get('p_hold_margin'))}`, "
                f"gap_margin `{fmt(margins.get('gap_margin'))}`"
            )
        lines.append("")
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    report = build_report()
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
    write_markdown(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
