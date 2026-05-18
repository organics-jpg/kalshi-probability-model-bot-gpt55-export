"""Compact strict-forward status for the boundary-clock feature-gate branch.

Research-only; no live bot changes or orders.

The full feature-gate candidate report is useful but can be slow because it
rebuilds diagnostic lanes and writes selected row payloads. This probe only
refreshes the frozen post-feature entry/bridge lanes and emits promotion-gate
metrics needed for quick continuation checks.
"""
from __future__ import annotations

import json
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

from probe_v28_boundary_clock_feature_gate_candidate import (
    RULES,
    STATE_JSON,
    as_float,
    blockers,
    load_json,
    market,
    passes,
    raw_edge,
    reconstructed_share,
    source,
    source_counts,
)
from probe_v28_coverage_repair_pool_diagnostic import row_net_after_fee, summarize
from probe_v28_frozen_boundary_clock_fv_entry_bridge import future_surfaces as bridge_surfaces
from probe_v28_frozen_boundary_clock_repair_entry import future_surfaces as entry_surfaces


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
OUT_JSON = OUT_DIR / "v28_boundary_clock_feature_gate_quick_status_latest.json"
OUT_MD = OUT_DIR / "v28_boundary_clock_feature_gate_quick_status_latest.md"


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def net(row: dict[str, Any]) -> float:
    return float(row_net_after_fee(row) or 0.0)


def best_per_market(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        row_market = market(row)
        if row_market:
            grouped[row_market].append(row)
    return [max(items, key=lambda row: raw_edge(row) or -999.0) for items in grouped.values()]


def compact_source_slice(rows: list[dict[str, Any]]) -> dict[str, Any]:
    by_source: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        by_source[source(row)].append(row)
    return {
        name: {
            "rows": len(items),
            "settled": sum(1 for row in items if row.get("side_won") is not None),
            "net_cents": sum(net(row) for row in items if row.get("side_won") is not None),
        }
        for name, items in sorted(by_source.items())
    }


def gate_gap(summary: dict[str, Any], share: float | None, denominator: int) -> dict[str, Any]:
    entries = int(as_float(summary.get("entries")) or 0)
    settled = int(as_float(summary.get("settled")) or 0)
    net_cents = float(as_float(summary.get("net_cents")) or 0.0)
    required_75 = int((0.75 * denominator) + 0.999999) if denominator else 0
    reconstructed = 0
    total = 0
    if share is not None and entries:
        reconstructed = round(share * entries)
        total = entries
    clean_needed_for_source = 0
    if total and share is not None and share > 0.35:
        clean_needed_for_source = max(0, int((reconstructed / 0.35 - total) + 0.999999))
    return {
        "rows_needed_for_75pct_coverage": max(0, required_75 - entries),
        "settled_needed_for_30": max(0, 30 - settled),
        "clean_rows_needed_for_source_gate": clean_needed_for_source,
        "cents_needed_for_cushion3": max(0.0, 300.0 - net_cents),
    }


def evaluate_lane(
    lane: str,
    freeze_ts: str,
    surfaces_fn: Callable[[str], tuple[list[dict[str, Any]], list[dict[str, Any]], int]],
) -> dict[str, Any]:
    all_rows, _target, denominator = surfaces_fn(freeze_ts)
    variants = []
    for rule_name, rule in RULES.items():
        selected = best_per_market([row for row in all_rows if passes(row, rule)])
        summary = summarize(selected, denominator)
        counts = source_counts(selected)
        share = reconstructed_share(counts)
        lane_blockers = blockers(summary, share)
        variants.append(
            {
                "candidate": f"{lane}_{rule_name}",
                "rule": rule_name,
                "summary": summary,
                "source_counts": counts,
                "source_slices": compact_source_slice(selected),
                "reconstructed_share": share,
                "full_loss_cushion_estimate": int(max(0.0, float(summary.get("net_cents") or 0.0)) // 100.0),
                "gate_gap": gate_gap(summary, share, int(denominator or 0)),
                "blockers": lane_blockers,
            }
        )
    variants.sort(
        key=lambda row: (
            len(row.get("blockers") or []),
            -float((row.get("summary") or {}).get("net_cents") or -999999.0),
        )
    )
    return {
        "lane": lane,
        "freeze_ts_utc": freeze_ts,
        "future_denominator": denominator,
        "variants": variants,
    }


def build_report() -> dict[str, Any]:
    state = load_json(STATE_JSON)
    freeze_ts = str(state.get("freeze_ts_utc") or "")
    lanes = [
        evaluate_lane("post_feature_freeze_entry", freeze_ts, entry_surfaces),
        evaluate_lane("post_feature_freeze_bridge", freeze_ts, bridge_surfaces),
    ]
    return {
        "generated_at_utc": utc_now_iso(),
        "state": state,
        "lanes": lanes,
        "interpretation": interpretation(lanes),
    }


def interpretation(lanes: list[dict[str, Any]]) -> list[str]:
    notes = [
        "Compact refresh only; diagnostic lanes are intentionally excluded.",
        "Selection uses observable feature gates; source labels are audit-only.",
    ]
    for lane in lanes:
        best = (lane.get("variants") or [{}])[0]
        summary = best.get("summary") or {}
        notes.append(
            f"{lane.get('lane')}: best {best.get('candidate')} settled {summary.get('settled')}, "
            f"coverage {summary.get('coverage_pct')}%, net {summary.get('net_cents')}c, "
            f"recon {best.get('reconstructed_share')}, blockers {best.get('blockers')}."
        )
    return notes


def fmt(value: Any) -> str:
    if value is None:
        return "None"
    if isinstance(value, float):
        return f"{value:.6f}"
    return str(value)


def write_report(report: dict[str, Any]) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8")
    state = report.get("state") or {}
    lines = [
        "# v28 Boundary-Clock Feature-Gate Quick Status",
        "",
        "Research-only; compact strict-forward refresh, no live logic changes.",
        "",
        f"- Generated UTC: `{report.get('generated_at_utc')}`",
        f"- Feature-gate freeze UTC: `{state.get('freeze_ts_utc')}`",
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
                f"- Future denominator: `{lane.get('future_denominator')}`",
                "",
                "| rank | candidate | settled | coverage | net c | W/L | recon share | cushion | gap | blockers |",
                "|---:|---|---:|---:|---:|---:|---:|---:|---|---|",
            ]
        )
        for idx, row in enumerate(lane.get("variants") or [], start=1):
            summary = row.get("summary") or {}
            gap = row.get("gate_gap") or {}
            lines.append(
                f"| {idx} | {row.get('candidate')} | {summary.get('settled')} | {fmt(summary.get('coverage_pct'))} | "
                f"{fmt(summary.get('net_cents'))} | {summary.get('wins')}/{summary.get('losses')} | "
                f"{fmt(row.get('reconstructed_share'))} | {row.get('full_loss_cushion_estimate')} | "
                f"cov+{gap.get('rows_needed_for_75pct_coverage')}, source+{gap.get('clean_rows_needed_for_source_gate')}, "
                f"cushion+{fmt(gap.get('cents_needed_for_cushion3'))}c | "
                f"{', '.join(row.get('blockers') or []) or 'none'} |"
            )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    report = build_report()
    write_report(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
