"""Source-denominator audit for the boundary-clock feature-gate candidate.

Research-only; no live bot changes or orders.

The feature-gate post-freeze lanes currently fail total coverage, but the row
ledger shows many omitted rows are reconstructed/rejected-actionable losers.
This audit separates denominator, selected, and omitted markets by source so
coverage can be interpreted without using source labels for selection.
"""
from __future__ import annotations

import json
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from probe_v28_boundary_clock_feature_gate_candidate import (
    RULES,
    as_float,
    best_per_market,
    load_or_create_state,
    market,
    net,
    passes,
    source,
)
from probe_v28_coverage_repair_pool_diagnostic import raw_edge, summarize
from probe_v28_frozen_boundary_clock_fv_entry_bridge import future_surfaces as bridge_surfaces
from probe_v28_frozen_boundary_clock_repair_entry import future_surfaces as entry_surfaces


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
OUT_JSON = OUT_DIR / "v28_boundary_clock_feature_gate_source_denominator_audit_latest.json"
OUT_MD = OUT_DIR / "v28_boundary_clock_feature_gate_source_denominator_audit_latest.md"


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def source_group(value: str) -> str:
    if value == "approved_entry":
        return "approved_entry"
    if value:
        return "reconstructed_or_rejected"
    return "unknown"


def source_counts(rows: list[dict[str, Any]]) -> dict[str, int]:
    return dict(Counter(source_group(source(row)) for row in rows))


def source_net(rows: list[dict[str, Any]]) -> dict[str, float]:
    totals: dict[str, float] = defaultdict(float)
    for row in rows:
        totals[source_group(source(row))] += net(row)
    return dict(sorted(totals.items()))


def best_rows_by_market(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        row_market = market(row)
        if row_market:
            grouped[row_market].append(row)
    return [max(items, key=lambda row: raw_edge(row) or -999.0) for items in grouped.values()]


def grouped_by_market(rows: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        row_market = market(row)
        if row_market:
            grouped[row_market].append(row)
    return grouped


def source_market_availability_counts(grouped: dict[str, list[dict[str, Any]]]) -> dict[str, int]:
    counts: Counter[str] = Counter()
    for rows in grouped.values():
        groups = {source_group(source(row)) for row in rows}
        for group in groups:
            counts[group] += 1
    return dict(counts)


def pct(part: int, whole: int) -> float | None:
    if whole <= 0:
        return None
    return 100.0 * part / whole


def evaluate_rule(lane: str, all_rows: list[dict[str, Any]], denominator: int, rule_name: str, rule: dict[str, Any]) -> dict[str, Any]:
    grouped = grouped_by_market(all_rows)
    denominator_reps = best_rows_by_market(all_rows)
    selected = best_per_market([row for row in all_rows if passes(row, rule)])
    selected_markets = {market(row) for row in selected}
    omitted = [row for row in denominator_reps if market(row) not in selected_markets]
    availability_counts = source_market_availability_counts(grouped)
    denom_counts = source_counts(denominator_reps)
    selected_counts = source_counts(selected)
    omitted_counts = source_counts(omitted)
    approved_den = int(availability_counts.get("approved_entry") or 0)
    rejected_den = int(availability_counts.get("reconstructed_or_rejected") or 0)
    approved_selected = int(selected_counts.get("approved_entry") or 0)
    rejected_selected = int(selected_counts.get("reconstructed_or_rejected") or 0)
    rejected_omitted = int(omitted_counts.get("reconstructed_or_rejected") or 0)
    observed = len(denominator_reps)
    unobserved = max(0, denominator - observed)
    summary = summarize(selected, denominator)
    selected_total = len(selected)
    selected_reconstructed_share = None if selected_total <= 0 else rejected_selected / selected_total
    return {
        "lane": lane,
        "rule": rule_name,
        "future_denominator": denominator,
        "observed_markets": observed,
        "unobserved_denominator_markets": unobserved,
        "summary": summary,
        "denominator_primary_source_counts": denom_counts,
        "available_source_market_counts": availability_counts,
        "selected_source_counts": selected_counts,
        "omitted_source_counts": omitted_counts,
        "selected_source_net_cents": source_net(selected),
        "omitted_source_net_cents": source_net(omitted),
        "approved_observed_coverage_pct": pct(approved_selected, approved_den),
        "reconstructed_observed_coverage_pct": pct(rejected_selected, rejected_den),
        "reconstructed_omission_share": None if len(omitted) <= 0 else rejected_omitted / len(omitted),
        "selected_reconstructed_share": selected_reconstructed_share,
    }


def evaluate_lane(label: str, freeze_ts: str, surfaces_fn: Any) -> dict[str, Any]:
    all_rows, _, denominator = surfaces_fn(freeze_ts)
    rules = [
        evaluate_rule(label, all_rows, int(denominator or 0), rule_name, rule)
        for rule_name, rule in RULES.items()
    ]
    rules.sort(
        key=lambda row: (
            -float((row.get("summary") or {}).get("net_cents") or -999999.0),
            -float((row.get("summary") or {}).get("coverage_pct") or 0.0),
        )
    )
    return {
        "lane": label,
        "freeze_ts_utc": freeze_ts,
        "future_denominator": int(denominator or 0),
        "rules": rules,
    }


def build_report() -> dict[str, Any]:
    state = load_or_create_state()
    freeze_ts = str(state["freeze_ts_utc"])
    lanes = [
        evaluate_lane("post_feature_freeze_entry", freeze_ts, entry_surfaces),
        evaluate_lane("post_feature_freeze_bridge", freeze_ts, bridge_surfaces),
    ]
    report = {
        "generated_at_utc": utc_now_iso(),
        "freeze_ts_utc": freeze_ts,
        "lanes": lanes,
    }
    report["interpretation"] = interpretation(report)
    return report


def interpretation(report: dict[str, Any]) -> list[str]:
    notes = [
        "Source labels are audit-only; no selection rule uses them.",
    ]
    for lane in report.get("lanes") or []:
        best = (lane.get("rules") or [{}])[0]
        summary = best.get("summary") or {}
        notes.append(
            f"{lane.get('lane')} best-by-PnL rule {best.get('rule')} selects {summary.get('entries')}/{best.get('future_denominator')} markets, "
            f"net {summary.get('net_cents')}c, selected reconstructed share {best.get('selected_reconstructed_share')}, "
            f"approved-source market coverage {best.get('approved_observed_coverage_pct')}%, reconstructed-source market coverage {best.get('reconstructed_observed_coverage_pct')}%, "
            f"omitted net by source {best.get('omitted_source_net_cents')}."
        )
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
        "# v28 Boundary-Clock Feature-Gate Source Denominator Audit",
        "",
        "Research-only; no live bot changes or orders.",
        "",
        f"- Generated UTC: `{report.get('generated_at_utc')}`",
        f"- Feature-gate freeze UTC: `{report.get('freeze_ts_utc')}`",
        "",
        "## Interpretation",
        "",
    ]
    for note in report.get("interpretation") or []:
        lines.append(f"- {note}")
    for lane in report.get("lanes") or []:
        lines.extend(["", f"## {lane.get('lane')}", ""])
        lines.extend(
            [
                "| rule | selected/den | net c | total cov | selected recon | approved-source cov | recon-source cov | available source markets | primary den sources | selected sources | omitted sources | omitted net by source |",
                "|---|---:|---:|---:|---:|---:|---:|---|---|---|---|",
            ]
        )
        for row in lane.get("rules") or []:
            summary = row.get("summary") or {}
            lines.append(
                f"| {row.get('rule')} | {summary.get('entries')}/{row.get('future_denominator')} | "
                f"{fmt(summary.get('net_cents'))} | {fmt(summary.get('coverage_pct'))} | "
                f"{fmt(row.get('selected_reconstructed_share'))} | {fmt(row.get('approved_observed_coverage_pct'))} | "
                f"{fmt(row.get('reconstructed_observed_coverage_pct'))} | {row.get('available_source_market_counts')} | "
                f"{row.get('denominator_primary_source_counts')} | {row.get('selected_source_counts')} | "
                f"{row.get('omitted_source_counts')} | {row.get('omitted_source_net_cents')} |"
            )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    report = build_report()
    write_md(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
