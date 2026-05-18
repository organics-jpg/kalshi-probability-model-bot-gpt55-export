"""Linked-outcome source runway for post-freeze v28 feature-gate variants.

Research-only; no live bot changes or orders.

This probe starts from the frozen feature-gate candidate rows, overlays finalized
market results where the research surface is still pending, then measures the
source-quality blocker directly: approved-vs-rejected PnL, approved-only
coverage, and how many future clean approved selected rows would be needed to
clear the <=35% reconstructed/rejected-actionable source-share gate.
"""
from __future__ import annotations

import csv
import json
import math
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from probe_v28_boundary_clock_feature_gate_candidate import (
    MAX_RECONSTRUCTED_SHARE,
    MIN_FULL_LOSS_CUSHION,
    MIN_SETTLED,
)
from probe_v28_coverage_repair_pool_diagnostic import COVERAGE_FLOOR
from probe_v28_danger_tag_replacement_diagnostic import row_net_after_fee


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
FEATURE_JSON = OUT_DIR / "v28_boundary_clock_feature_gate_candidate_latest.json"
MARKET_RESULTS_CSV = ROOT / "stats" / "live_mushroom_v28_size2" / "market_results.csv"
OUT_JSON = OUT_DIR / "v28_feature_gate_linked_source_runway_latest.json"
OUT_MD = OUT_DIR / "v28_feature_gate_linked_source_runway_latest.md"

TARGET_LANES = {"post_feature_freeze_entry", "post_feature_freeze_bridge"}


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


def load_market_results(path: Path) -> dict[str, dict[str, str]]:
    out: dict[str, dict[str, str]] = {}
    if not path.exists():
        return out
    with path.open("r", encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle):
            market = str(row.get("market") or "")
            if market:
                out[market] = row
    return out


def as_float(value: Any) -> float | None:
    if value is None or value == "":
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def side_won(side: str, result: str) -> bool | None:
    if side not in {"yes", "no"} or result not in {"yes", "no"}:
        return None
    return side == result


def row_net_cents(row: dict[str, Any]) -> float:
    stored = as_float(row.get("net_cents"))
    if stored is not None:
        return stored
    return float(row_net_after_fee(row) or 0.0)


def linked_row(row: dict[str, Any], market_results: dict[str, dict[str, str]]) -> tuple[dict[str, Any], bool]:
    if row.get("side_won") is not None:
        return dict(row), False
    market = str(row.get("market") or "")
    result_row = market_results.get(market) or {}
    result = str(result_row.get("result") or "")
    won = side_won(str(row.get("side") or ""), result)
    if won is None:
        return dict(row), False
    out = dict(row)
    out["side_won"] = won
    out["net_cents"] = row_net_after_fee(out)
    out["linked_market_result"] = result
    out["linked_market_status"] = result_row.get("status")
    out["linked_settlement_ts"] = result_row.get("settlement_ts")
    return out, True


def reconstructed_count(rows: list[dict[str, Any]]) -> int:
    return sum(1 for row in rows if str(row.get("source") or "") != "approved_entry")


def approved_rows_needed_for_source_gate(rows: list[dict[str, Any]]) -> int:
    total = len(rows)
    reconstructed = reconstructed_count(rows)
    if total <= 0 or reconstructed / total <= MAX_RECONSTRUCTED_SHARE:
        return 0
    return max(0, math.floor(reconstructed / MAX_RECONSTRUCTED_SHARE - total) + 1)


def summarize(rows: list[dict[str, Any]], denominator: int) -> dict[str, Any]:
    settled = [row for row in rows if row.get("side_won") is not None]
    net_cents = sum(row_net_cents(row) for row in settled)
    source_counts = Counter(str(row.get("source") or "unknown") for row in rows)
    reconstructed = sum(count for src, count in source_counts.items() if src != "approved_entry")
    return {
        "entries": len(rows),
        "settled": len(settled),
        "wins": sum(1 for row in settled if row.get("side_won") is True),
        "losses": sum(1 for row in settled if row.get("side_won") is False),
        "coverage_pct": 100.0 * len(rows) / denominator if denominator else None,
        "net_cents": net_cents,
        "avg_net_cents": net_cents / len(settled) if settled else None,
        "source_counts": dict(source_counts),
        "reconstructed_share": reconstructed / len(rows) if rows else None,
        "full_loss_cushion_estimate": int(max(0.0, net_cents) // 100.0),
    }


def source_summaries(rows: list[dict[str, Any]], denominator: int) -> dict[str, dict[str, Any]]:
    grouped: dict[str, list[dict[str, Any]]] = {}
    for row in rows:
        grouped.setdefault(str(row.get("source") or "unknown"), []).append(row)
    return {source: summarize(items, denominator) for source, items in sorted(grouped.items())}


def blockers(summary: dict[str, Any]) -> list[str]:
    out = []
    if int(summary.get("settled") or 0) < MIN_SETTLED:
        out.append("settled_lt_30")
    if summary.get("coverage_pct") is None or float(summary.get("coverage_pct") or 0.0) < COVERAGE_FLOOR:
        out.append("coverage_too_low")
    if float(summary.get("net_cents") or 0.0) <= 0.0:
        out.append("net_not_positive")
    if summary.get("reconstructed_share") is not None and float(summary["reconstructed_share"]) > MAX_RECONSTRUCTED_SHARE:
        out.append("reconstructed_share_gt_35pct")
    if int(summary.get("full_loss_cushion_estimate") or 0) < MIN_FULL_LOSS_CUSHION:
        out.append("full_loss_cushion_lt_3")
    return out


def row_for_variant(lane: dict[str, Any], variant: dict[str, Any], market_results: dict[str, dict[str, str]]) -> dict[str, Any]:
    denominator = int(as_float(lane.get("future_denominator")) or 0)
    original_rows = [row for row in variant.get("rows") or [] if isinstance(row, dict)]
    linked_rows = []
    linked_count = 0
    for row in original_rows:
        linked, did_link = linked_row(row, market_results)
        linked_rows.append(linked)
        linked_count += int(did_link)
    summary = summarize(linked_rows, denominator)
    approved_rows = [row for row in linked_rows if str(row.get("source") or "") == "approved_entry"]
    rejected_rows = [row for row in linked_rows if str(row.get("source") or "") != "approved_entry"]
    approved_needed = approved_rows_needed_for_source_gate(linked_rows)
    if approved_needed:
        diluted_rows = linked_rows + [{"source": "approved_entry"} for _ in range(approved_needed)]
    else:
        diluted_rows = linked_rows
    diluted_summary = summarize(diluted_rows, denominator + approved_needed)
    return {
        "lane": lane.get("lane"),
        "candidate": variant.get("candidate"),
        "future_denominator": denominator,
        "linked_rows_count": linked_count,
        "linked_summary": summary,
        "approved_summary": summarize(approved_rows, denominator),
        "rejected_or_reconstructed_summary": summarize(rejected_rows, denominator),
        "source_summaries": source_summaries(linked_rows, denominator),
        "approved_only_blockers": blockers(summarize(approved_rows, denominator)),
        "linked_blockers": blockers(summary),
        "approved_future_rows_needed_for_source_gate": approved_needed,
        "summary_after_clean_approved_dilution": diluted_summary,
        "blockers_after_clean_approved_dilution": blockers(diluted_summary),
        "interpretation": variant_interpretation(summary, approved_rows, rejected_rows, approved_needed),
    }


def variant_interpretation(
    summary: dict[str, Any],
    approved_rows: list[dict[str, Any]],
    rejected_rows: list[dict[str, Any]],
    approved_needed: int,
) -> str:
    approved_net = summarize(approved_rows, 1).get("net_cents")
    rejected_net = summarize(rejected_rows, 1).get("net_cents")
    return (
        f"Linked net {summary.get('net_cents')}c splits approved {approved_net}c vs rejected/reconstructed "
        f"{rejected_net}c; {approved_needed} future clean approved selected rows are needed to dilute source share."
    )


def build_report() -> dict[str, Any]:
    feature = load_json(FEATURE_JSON)
    market_results = load_market_results(MARKET_RESULTS_CSV)
    rows = []
    for lane in feature.get("lanes") or []:
        if lane.get("lane") not in TARGET_LANES:
            continue
        for variant in lane.get("variants") or []:
            if isinstance(variant, dict):
                rows.append(row_for_variant(lane, variant, market_results))
    rows.sort(
        key=lambda row: (
            len(row.get("linked_blockers") or []),
            row.get("approved_future_rows_needed_for_source_gate") or 999,
            -float((row.get("linked_summary") or {}).get("net_cents") or -999999.0),
        )
    )
    return {
        "generated_at_utc": utc_now_iso(),
        "feature_source": str(FEATURE_JSON),
        "market_results_source": str(MARKET_RESULTS_CSV),
        "purpose": "Source-quality runway after linking finalized market results into pending feature-gate rows.",
        "rows": rows,
        "interpretation": interpretation(rows),
    }


def interpretation(rows: list[dict[str, Any]]) -> list[str]:
    notes = [
        "This is an audit overlay; it does not change official candidate scoring or promotion status.",
    ]
    if rows:
        best = rows[0]
        summary = best.get("linked_summary") or {}
        notes.append(
            f"Best linked source-runway row is {best.get('candidate')} with net {summary.get('net_cents')}c, "
            f"coverage {summary.get('coverage_pct')}%, reconstructed share {summary.get('reconstructed_share')}, "
            f"and blockers {best.get('linked_blockers')}."
        )
        notes.append(
            f"It needs {best.get('approved_future_rows_needed_for_source_gate')} future clean approved selected rows "
            "to clear the source gate if no new rejected selected rows are added."
        )
    return notes


def fmt(value: Any) -> str:
    if value is None:
        return "None"
    if isinstance(value, float):
        return f"{value:.6f}"
    return str(value)


def write_md(report: dict[str, Any]) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8")
    lines = [
        "# v28 Feature-Gate Linked Source Runway",
        "",
        "Research-only audit overlay. No live bot changes or orders.",
        "",
        f"- Generated UTC: `{report.get('generated_at_utc')}`",
        "",
        "## Interpretation",
        "",
    ]
    for note in report.get("interpretation") or []:
        lines.append(f"- {note}")
    lines.extend(
        [
            "",
            "## Variants",
            "",
            "| rank | lane | candidate | linked settled/net | coverage | recon | approved net | rejected net | clean rows needed | linked blockers |",
            "|---:|---|---|---:|---:|---:|---:|---:|---:|---|",
        ]
    )
    for idx, row in enumerate(report.get("rows") or [], start=1):
        linked = row.get("linked_summary") or {}
        approved = row.get("approved_summary") or {}
        rejected = row.get("rejected_or_reconstructed_summary") or {}
        lines.append(
            f"| {idx} | {row.get('lane')} | {row.get('candidate')} | "
            f"{linked.get('settled')}/{fmt(linked.get('net_cents'))}c | {fmt(linked.get('coverage_pct'))} | "
            f"{fmt(linked.get('reconstructed_share'))} | {fmt(approved.get('net_cents'))} | "
            f"{fmt(rejected.get('net_cents'))} | {row.get('approved_future_rows_needed_for_source_gate')} | "
            f"{', '.join(row.get('linked_blockers') or []) or 'none'} |"
        )
    lines.extend(
        [
            "",
            "## Source Split",
            "",
            "| candidate | source | entries | settled | W/L | net c | coverage contribution |",
            "|---|---|---:|---:|---:|---:|---:|",
        ]
    )
    for row in report.get("rows") or []:
        for source, summary in (row.get("source_summaries") or {}).items():
            lines.append(
                f"| {row.get('candidate')} | {source} | {summary.get('entries')} | {summary.get('settled')} | "
                f"{summary.get('wins')}/{summary.get('losses')} | {fmt(summary.get('net_cents'))} | "
                f"{fmt(summary.get('coverage_pct'))} |"
            )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    report = build_report()
    write_md(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
