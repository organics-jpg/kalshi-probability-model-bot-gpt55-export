"""Threshold-margin stress for loss-guarded v28 book-gap exit watches.

Research-only; no live bot changes or orders.

The current loss-guarded book-gap samples are clean but immature. This probe
replays stricter p-hold/book-gap floors against the already-frozen strict rows
to see whether the positive sample depends on threshold-edge suppressions.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
OUT_JSON = OUT_DIR / "v28_exit_loss_guard_threshold_margin_stress_latest.json"
OUT_MD = OUT_DIR / "v28_exit_loss_guard_threshold_margin_stress_latest.md"

SOURCES = {
    "book_gap_loss_guard": OUT_DIR / "v28_frozen_exit_book_gap_loss_guard_latest.json",
    "book_gap_loss_guard_v3": OUT_DIR / "v28_frozen_exit_book_gap_loss_guard_v3_latest.json",
}

V1_VARIANTS = [
    {"name": "as_frozen", "value_p_hold_floor": 0.85, "value_gap_floor": 0.0, "reduce_p_hold_floor": 0.79, "reduce_gap_floor": 0.0},
    {"name": "value_p86_reduce_p79", "value_p_hold_floor": 0.86, "value_gap_floor": 0.0, "reduce_p_hold_floor": 0.79, "reduce_gap_floor": 0.0},
    {"name": "value_p88_reduce_p79", "value_p_hold_floor": 0.88, "value_gap_floor": 0.0, "reduce_p_hold_floor": 0.79, "reduce_gap_floor": 0.0},
    {"name": "value_p90_reduce_p79", "value_p_hold_floor": 0.90, "value_gap_floor": 0.0, "reduce_p_hold_floor": 0.79, "reduce_gap_floor": 0.0},
    {"name": "value_p85_reduce_p80", "value_p_hold_floor": 0.85, "value_gap_floor": 0.0, "reduce_p_hold_floor": 0.80, "reduce_gap_floor": 0.0},
    {"name": "value_p88_reduce_p80", "value_p_hold_floor": 0.88, "value_gap_floor": 0.0, "reduce_p_hold_floor": 0.80, "reduce_gap_floor": 0.0},
    {"name": "gap_positive_2pct", "value_p_hold_floor": 0.85, "value_gap_floor": 0.02, "reduce_p_hold_floor": 0.79, "reduce_gap_floor": 0.02},
]

V3_VARIANTS = [
    {
        "name": "as_frozen",
        "value_p_hold_floor": 0.85,
        "value_gap_floor": 0.0,
        "value_fair_drawdown_floor_cents": -5.0,
        "value_extreme_p_hold_floor": 0.95,
        "reduce_p_hold_floor": 0.79,
        "reduce_gap_floor": 0.0,
    },
    {
        "name": "extreme_p96",
        "value_p_hold_floor": 0.85,
        "value_gap_floor": 0.0,
        "value_fair_drawdown_floor_cents": -5.0,
        "value_extreme_p_hold_floor": 0.96,
        "reduce_p_hold_floor": 0.79,
        "reduce_gap_floor": 0.0,
    },
    {
        "name": "extreme_p97",
        "value_p_hold_floor": 0.85,
        "value_gap_floor": 0.0,
        "value_fair_drawdown_floor_cents": -5.0,
        "value_extreme_p_hold_floor": 0.97,
        "reduce_p_hold_floor": 0.79,
        "reduce_gap_floor": 0.0,
    },
    {
        "name": "shallow_drawdown_0",
        "value_p_hold_floor": 0.85,
        "value_gap_floor": 0.0,
        "value_fair_drawdown_floor_cents": 0.0,
        "value_extreme_p_hold_floor": 0.95,
        "reduce_p_hold_floor": 0.79,
        "reduce_gap_floor": 0.0,
    },
    {
        "name": "value_p88_extreme_p96",
        "value_p_hold_floor": 0.88,
        "value_gap_floor": 0.0,
        "value_fair_drawdown_floor_cents": -5.0,
        "value_extreme_p_hold_floor": 0.96,
        "reduce_p_hold_floor": 0.79,
        "reduce_gap_floor": 0.0,
    },
]


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


def rows(payload: dict[str, Any]) -> list[dict[str, Any]]:
    out = []
    for row in payload.get("rows") or []:
        if isinstance(row, dict) and row.get("result") not in (None, "", "unknown"):
            out.append(row)
    return out


def is_soft(row: dict[str, Any]) -> bool:
    reason = str(row.get("exit_reason") or "")
    return reason in {"mushroom_v28_exit_value_over_hold", "mushroom_v28_probability_reduce"}


def is_value(row: dict[str, Any]) -> bool:
    return str(row.get("exit_reason") or "") == "mushroom_v28_exit_value_over_hold"


def is_reduce(row: dict[str, Any]) -> bool:
    return str(row.get("exit_reason") or "") == "mushroom_v28_probability_reduce"


def should_suppress_v1(row: dict[str, Any], rule: dict[str, Any]) -> bool:
    if not is_soft(row):
        return False
    p = row.get("p_hold")
    gap = row.get("hold_book_gap")
    if p is None or gap is None:
        return False
    p_val = fnum(p)
    gap_val = fnum(gap)
    if is_value(row):
        return p_val >= fnum(rule.get("value_p_hold_floor"), 0.85) or gap_val >= fnum(rule.get("value_gap_floor"), 0.0)
    if is_reduce(row):
        return p_val >= fnum(rule.get("reduce_p_hold_floor"), 0.79) and gap_val >= fnum(rule.get("reduce_gap_floor"), 0.0)
    return False


def should_suppress_v3(row: dict[str, Any], rule: dict[str, Any]) -> bool:
    if not is_soft(row):
        return False
    p = row.get("p_hold")
    gap = row.get("hold_book_gap")
    drawdown = row.get("fair_drawdown_cents")
    if p is None or gap is None:
        return False
    p_val = fnum(p)
    gap_val = fnum(gap)
    if is_value(row):
        if gap_val >= fnum(rule.get("value_gap_floor"), 0.0):
            return True
        if p_val >= fnum(rule.get("value_p_hold_floor"), 0.85) and fnum(drawdown) >= fnum(rule.get("value_fair_drawdown_floor_cents"), -5.0):
            return True
        return p_val >= fnum(rule.get("value_extreme_p_hold_floor"), 0.95)
    if is_reduce(row):
        return p_val >= fnum(rule.get("reduce_p_hold_floor"), 0.79) and gap_val >= fnum(rule.get("reduce_gap_floor"), 0.0)
    return False


def row_delta(row: dict[str, Any], suppressed: bool) -> float:
    current = fnum(row.get("current_cents"))
    candidate = fnum(row.get("hold_cents")) if suppressed else current
    return candidate - current


def candidate_value(row: dict[str, Any], suppressed: bool) -> float:
    return fnum(row.get("hold_cents")) if suppressed else fnum(row.get("current_cents"))


def summarize_variant(lane: str, lane_rows: list[dict[str, Any]], rule: dict[str, Any], suppress_fn) -> dict[str, Any]:
    decisions = [(row, bool(suppress_fn(row, rule))) for row in lane_rows]
    suppressed = [row for row, flag in decisions if flag]
    helpful = [row for row in suppressed if row_delta(row, True) > 0]
    harmful = [row for row in suppressed if row_delta(row, True) < 0]
    current_net = sum(fnum(row.get("current_cents")) for row in lane_rows)
    candidate_net = sum(candidate_value(row, flag) for row, flag in decisions)
    base_suppressed = {(
        row.get("market"),
        row.get("side"),
        row.get("entry_ts"),
        row.get("exit_ts"),
    ) for row in lane_rows if row.get("suppressed") is True}
    now_suppressed = {(
        row.get("market"),
        row.get("side"),
        row.get("entry_ts"),
        row.get("exit_ts"),
    ) for row in suppressed}
    dropped = base_suppressed - now_suppressed
    return {
        "lane": lane,
        "variant": rule.get("name"),
        "rows": len(lane_rows),
        "suppressed": len(suppressed),
        "helpful_suppressed": len(helpful),
        "harmful_suppressed": len(harmful),
        "candidate_net_cents": candidate_net,
        "current_net_cents": current_net,
        "delta_vs_current_cents": candidate_net - current_net,
        "suppression_delta_cents": sum(row_delta(row, True) for row in suppressed),
        "harmful_delta_cents": sum(row_delta(row, True) for row in harmful),
        "dropped_base_suppressions": len(dropped),
        "full_loss_cushion": int(candidate_net // 100) if candidate_net > 0 else 0,
        "rule": {key: value for key, value in rule.items() if key != "name"},
        "top_suppressed": [
            {
                "market": row.get("market"),
                "side": row.get("side"),
                "exit_reason": row.get("exit_reason"),
                "exit_cents": row.get("exit_cents"),
                "p_hold": row.get("p_hold"),
                "hold_book_gap": row.get("hold_book_gap"),
                "fair_drawdown_cents": row.get("fair_drawdown_cents"),
                "delta_cents": row_delta(row, True),
            }
            for row in sorted(suppressed, key=lambda item: row_delta(item, True), reverse=True)[:8]
        ],
    }


def build_report() -> dict[str, Any]:
    source_payloads = {lane: load_json(path) for lane, path in SOURCES.items()}
    lane_reports = []
    for lane, payload in source_payloads.items():
        lane_rows = rows(payload)
        variants = V3_VARIANTS if lane.endswith("_v3") else V1_VARIANTS
        suppress_fn = should_suppress_v3 if lane.endswith("_v3") else should_suppress_v1
        summaries = [summarize_variant(lane, lane_rows, rule, suppress_fn) for rule in variants]
        best = max(summaries, key=lambda item: (fnum(item.get("delta_vs_current_cents")), fnum(item.get("candidate_net_cents"))), default={})
        conservative = next((item for item in summaries if item.get("variant") != "as_frozen" and item.get("harmful_suppressed") == 0 and item.get("delta_vs_current_cents", 0) > 0), {})
        lane_reports.append({
            "lane": lane,
            "freeze_ts_utc": (payload.get("freeze") or {}).get("freeze_ts_utc"),
            "summaries": summaries,
            "best_by_delta": best,
            "first_positive_clean_conservative": conservative,
        })
    return {
        "generated_at_utc": utc_now_iso(),
        "sources": {lane: str(path) for lane, path in SOURCES.items()},
        "lanes": lane_reports,
        "interpretation": [
            "Research-only margin stress; it replays stricter thresholds on already-frozen strict rows.",
            "This is not a new candidate freeze and does not change any live or watch logic.",
            "If small threshold moves erase most recovery, the branch should keep collecting before any child-freeze discussion.",
        ],
    }


def fmt(value: Any) -> str:
    if value is None:
        return "n/a"
    if isinstance(value, float):
        return f"{value:.2f}"
    return str(value)


def write_markdown(report: dict[str, Any]) -> None:
    lines = [
        "# v28 Exit Loss-Guard Threshold Margin Stress",
        "",
        "Research-only. No live bot logic changes, no orders, no process control.",
        "",
        f"- Generated UTC: `{report.get('generated_at_utc')}`",
        "",
        "## Interpretation",
        "",
    ]
    lines.extend(f"- {note}" for note in report.get("interpretation") or [])
    for lane in report.get("lanes") or []:
        lines.extend(
            [
                "",
                f"## {lane.get('lane')}",
                "",
                f"- Freeze UTC: `{lane.get('freeze_ts_utc')}`",
                f"- Best by delta: `{(lane.get('best_by_delta') or {}).get('variant')}`",
                f"- First positive clean conservative: `{(lane.get('first_positive_clean_conservative') or {}).get('variant')}`",
                "",
                "| variant | suppressed | helpful | harmful | net c | delta c | suppression delta c | dropped base | cushion |",
                "|---|---:|---:|---:|---:|---:|---:|---:|---:|",
            ]
        )
        for row in lane.get("summaries") or []:
            lines.append(
                "| "
                + " | ".join(
                    [
                        f"`{row.get('variant')}`",
                        str(row.get("suppressed")),
                        str(row.get("helpful_suppressed")),
                        str(row.get("harmful_suppressed")),
                        fmt(row.get("candidate_net_cents")),
                        fmt(row.get("delta_vs_current_cents")),
                        fmt(row.get("suppression_delta_cents")),
                        str(row.get("dropped_base_suppressions")),
                        str(row.get("full_loss_cushion")),
                    ]
                )
                + " |"
            )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    report = build_report()
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
    write_markdown(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
