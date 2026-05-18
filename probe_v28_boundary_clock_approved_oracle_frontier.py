"""Approved-source frontier for boundary-clock repair lanes.

Research-only; no live bot changes or orders.

This is deliberately an upper-bound diagnostic. It asks whether the
boundary-clock windows contain enough actual approved-entry rows to form a
broad, source-clean, profitable lane. Because "approved_entry" is a source
label, these rows are not a deployable rule by themselves; they are a target
for feature discovery.
"""
from __future__ import annotations

import json
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from probe_v28_coverage_repair_pool_diagnostic import COVERAGE_FLOOR, raw_edge, row_net_after_fee, summarize
from probe_v28_frozen_boundary_clock_fv_entry_bridge import (
    future_surfaces as bridge_surfaces,
    load_json as bridge_load_json,
)
from probe_v28_frozen_boundary_clock_repair_entry import (
    future_surfaces as entry_surfaces,
    load_json as entry_load_json,
)


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
ENTRY_STATE_JSON = OUT_DIR / "v28_frozen_boundary_clock_repair_entry_state.json"
BRIDGE_STATE_JSON = OUT_DIR / "v28_frozen_boundary_clock_fv_entry_bridge_state.json"
OUT_JSON = OUT_DIR / "v28_boundary_clock_approved_oracle_frontier_latest.json"
OUT_MD = OUT_DIR / "v28_boundary_clock_approved_oracle_frontier_latest.md"

MIN_SETTLED = 30
MAX_RECONSTRUCTED_SHARE = 0.35
MIN_FULL_LOSS_CUSHION = 3


def as_float(value: Any) -> float | None:
    if value is None or value == "":
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def market(row: dict[str, Any]) -> str:
    return str(row.get("market") or "")


def source(row: dict[str, Any]) -> str:
    return str(row.get("source") or "unknown")


def recross(row: dict[str, Any]) -> float:
    value = as_float(row.get("recross_hazard_score"))
    return value if value is not None else 999.0


def net(row: dict[str, Any]) -> float:
    value = row_net_after_fee(row)
    return float(value or 0.0)


def score(row: dict[str, Any], mode: str) -> float:
    if mode == "realized_oracle":
        return net(row)
    if mode == "raw_edge":
        value = raw_edge(row)
        return float(value if value is not None else -999.0)
    if mode == "low_recross":
        return -recross(row)
    # ISO-ish timestamp strings sort in chronological order.
    if mode == "first_ts":
        return -float(str(row.get("ts_wall") or "99999999999999999999").replace("-", "").replace(":", "").replace(".", "").replace("+", "").replace("T", "").replace("Z", "")[:14] or 0)
    return 0.0


def best_per_market(rows: list[dict[str, Any]], mode: str) -> list[dict[str, Any]]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        if market(row):
            grouped[market(row)].append(row)
    return [max(items, key=lambda row: score(row, mode)) for items in grouped.values()]


def blockers(summary: dict[str, Any]) -> list[str]:
    out = []
    settled = int(as_float(summary.get("settled")) or 0)
    coverage = as_float(summary.get("coverage_pct"))
    net_cents = as_float(summary.get("net_cents"))
    if settled < MIN_SETTLED:
        out.append("settled_lt_30")
    if coverage is None or coverage < COVERAGE_FLOOR:
        out.append("coverage_too_low")
    if net_cents is None or net_cents <= 0:
        out.append("net_not_positive")
    # Approved-only means reconstructed share is zero.
    if 0.0 > MAX_RECONSTRUCTED_SHARE:
        out.append("reconstructed_share_gt_35pct")
    cushion = int(max(0.0, float(net_cents or 0.0)) // 100.0)
    if cushion < MIN_FULL_LOSS_CUSHION:
        out.append("full_loss_cushion_lt_3")
    return out


def evaluate_lane(label: str, freeze_ts: str, surfaces_fn: Any) -> dict[str, Any]:
    all_rows, _, denominator = surfaces_fn(freeze_ts)
    approved = [row for row in all_rows if source(row) == "approved_entry"]
    variants = []
    for mode in ("first_ts", "raw_edge", "low_recross", "realized_oracle"):
        rows = best_per_market(approved, mode)
        summary = summarize(rows, denominator)
        net_cents = as_float(summary.get("net_cents"))
        variants.append(
            {
                "candidate": f"{label}_approved_source_{mode}",
                "selector": mode,
                "future_denominator": denominator,
                "candidate_summary": summary,
                "approved_market_count": len({market(row) for row in rows}),
                "reconstructed_share": 0.0 if rows else None,
                "full_loss_cushion_estimate": int(max(0.0, float(net_cents or 0.0)) // 100.0),
                "blockers": blockers(summary),
                "rows": [
                    {
                        "market": market(row),
                        "side": row.get("side"),
                        "side_won": row.get("side_won"),
                        "net_cents": net(row),
                        "raw_edge": raw_edge(row),
                        "recross_hazard_score": row.get("recross_hazard_score"),
                        "ts_wall": row.get("ts_wall"),
                    }
                    for row in rows
                ],
            }
        )
    variants.sort(
        key=lambda row: (
            len(row.get("blockers") or []),
            -float((row.get("candidate_summary") or {}).get("net_cents") or -999999.0),
        )
    )
    return {
        "lane": label,
        "freeze_ts": freeze_ts,
        "future_denominator": denominator,
        "approved_row_count": len(approved),
        "approved_market_count": len({market(row) for row in approved}),
        "variants": variants,
    }


def build_report() -> dict[str, Any]:
    entry_state = entry_load_json(ENTRY_STATE_JSON)
    bridge_state = bridge_load_json(BRIDGE_STATE_JSON)
    lanes = []
    if entry_state.get("freeze_ts_utc"):
        lanes.append(evaluate_lane("boundary_clock_repair_entry", str(entry_state["freeze_ts_utc"]), entry_surfaces))
    if bridge_state.get("freeze_ts_utc"):
        lanes.append(evaluate_lane("boundary_clock_fv_entry_bridge", str(bridge_state["freeze_ts_utc"]), bridge_surfaces))
    return {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "purpose": "Upper-bound approved-source frontier for boundary-clock lanes; not a deployable rule.",
        "lanes": lanes,
        "interpretation": interpretation(lanes),
    }


def interpretation(lanes: list[dict[str, Any]]) -> list[str]:
    notes = []
    for lane in lanes:
        best = (lane.get("variants") or [{}])[0]
        summary = best.get("candidate_summary") or {}
        notes.append(
            f"{lane.get('lane')}: approved-source frontier has {lane.get('approved_market_count')} approved markets; best {best.get('candidate')} settled {summary.get('settled')}, coverage {summary.get('coverage_pct')}%, net {summary.get('net_cents')}c, blockers {best.get('blockers')}."
        )
    notes.append("Use this as a feature-discovery target only: source labels are evidence quality, not live entry logic.")
    return notes


def fmt(value: Any) -> str:
    if value is None:
        return "None"
    if isinstance(value, float):
        return f"{value:.6f}"
    return str(value)


def write_md(report: dict[str, Any]) -> None:
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8")
    lines = [
        "# v28 Boundary-Clock Approved Oracle Frontier",
        "",
        "Research-only; source-label upper bound, not deployable live logic.",
        "",
        f"- Generated UTC: `{report.get('generated_at_utc')}`",
        "",
        "## Interpretation",
        "",
    ]
    for note in report.get("interpretation") or []:
        lines.append(f"- {note}")
    for lane in report.get("lanes") or []:
        lines.extend(
            [
                "",
                f"## {lane.get('lane')}",
                "",
                f"- Freeze UTC: `{lane.get('freeze_ts')}`",
                f"- Future denominator: `{lane.get('future_denominator')}`",
                f"- Approved rows/markets: `{lane.get('approved_row_count')}/{lane.get('approved_market_count')}`",
                "",
                "| rank | candidate | approved markets | settled | coverage | net c | W/L | recon share | cushion | blockers |",
                "|---:|---|---:|---:|---:|---:|---:|---:|---:|---|",
            ]
        )
        for idx, row in enumerate(lane.get("variants") or [], start=1):
            summary = row.get("candidate_summary") or {}
            lines.append(
                f"| {idx} | {row.get('candidate')} | {row.get('approved_market_count')} | "
                f"{summary.get('settled')} | {fmt(summary.get('coverage_pct'))} | {fmt(summary.get('net_cents'))} | "
                f"{summary.get('wins')}/{summary.get('losses')} | {fmt(row.get('reconstructed_share'))} | "
                f"{row.get('full_loss_cushion_estimate')} | {', '.join(row.get('blockers') or []) or 'none'} |"
            )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    report = build_report()
    write_md(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
