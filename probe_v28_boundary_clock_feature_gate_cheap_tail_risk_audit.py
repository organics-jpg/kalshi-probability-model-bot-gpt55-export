"""Cheap-tail risk audit for the frozen boundary-clock feature gate.

Research-only; no live bot changes or orders.

The broad feature-gate row recovers coverage by admitting very cheap selected
contracts. This report tests whether those rows are a physical cheap-tail
failure mode, and whether continuous notional shrinkage would reduce fragility
without turning the branch into another brittle hard cutoff.
"""
from __future__ import annotations

import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from probe_v28_boundary_clock_feature_gate_candidate import (
    RULES,
    as_float,
    load_or_create_state,
    market,
    net,
    passes,
    reconstructed_share,
    source,
    source_counts,
)
from probe_v28_coverage_repair_pool_diagnostic import raw_edge, summarize
from probe_v28_frozen_boundary_clock_fv_entry_bridge import future_surfaces as bridge_surfaces
from probe_v28_frozen_boundary_clock_repair_entry import future_surfaces as entry_surfaces


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
OUT_JSON = OUT_DIR / "v28_boundary_clock_feature_gate_cheap_tail_risk_audit_latest.json"
OUT_MD = OUT_DIR / "v28_boundary_clock_feature_gate_cheap_tail_risk_audit_latest.md"

BROAD_RULE = "raw03_recross70_abs075"
STRICT_RULE = "raw05_recross60_abs085_ask65"
TARGET_COVERAGE = 0.75
MAX_RECONSTRUCTED_SHARE = 0.35


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def ask(row: dict[str, Any]) -> float | None:
    return as_float(row.get("ask_prob"))


def abs_d(row: dict[str, Any]) -> float | None:
    return as_float(row.get("abs_d_sigma"))


def recross(row: dict[str, Any]) -> float | None:
    return as_float(row.get("recross_hazard_score"))


def select_by_market(rows: list[dict[str, Any]], rule: dict[str, Any]) -> dict[str, dict[str, Any]]:
    selected: dict[str, dict[str, Any]] = {}
    for row in rows:
        row_market = market(row)
        if not row_market or not passes(row, rule):
            continue
        current = selected.get(row_market)
        if current is None or (raw_edge(row) or -999.0) > (raw_edge(current) or -999.0):
            selected[row_market] = row
    return selected


def row_digest(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "market": market(row),
        "source": source(row),
        "side": row.get("side"),
        "side_won": row.get("side_won"),
        "net_cents": net(row),
        "raw_edge": raw_edge(row),
        "recross_hazard_score": recross(row),
        "abs_d_sigma": abs_d(row),
        "ask_prob": ask(row),
    }


def wl(rows: list[dict[str, Any]]) -> dict[str, int]:
    return {
        "wins": sum(1 for row in rows if net(row) > 0),
        "losses": sum(1 for row in rows if net(row) < 0),
        "flats": sum(1 for row in rows if net(row) == 0),
    }


def avg(rows: list[dict[str, Any]], fn: Any) -> float | None:
    values = [fn(row) for row in rows]
    values = [float(value) for value in values if value is not None]
    if not values:
        return None
    return sum(values) / len(values)


def group_summary(rows: list[dict[str, Any]]) -> dict[str, Any]:
    counts = source_counts(rows)
    return {
        "rows": len(rows),
        "settled": sum(1 for row in rows if net(row) != 0 or row.get("side_won") is not None),
        "net_cents": sum(net(row) for row in rows),
        "wl": wl(rows),
        "source_counts": counts,
        "reconstructed_share": reconstructed_share(counts),
        "avg_ask": avg(rows, ask),
        "avg_raw_edge": avg(rows, raw_edge),
        "avg_recross": avg(rows, recross),
        "avg_abs_d": avg(rows, abs_d),
    }


def tail_bucket(row: dict[str, Any]) -> str:
    row_ask = ask(row)
    if row_ask is None:
        return "unknown_ask"
    if row_ask < 0.05:
        return "ask_lt_05"
    if row_ask < 0.10:
        return "ask_05_10"
    if row_ask < 0.15:
        return "ask_10_15"
    if row_ask > 0.90:
        return "ask_gt_90"
    return "mid_ask"


def shrink_weight(row: dict[str, Any], policy: str) -> float:
    row_ask = ask(row)
    if row_ask is None:
        return 1.0
    if policy == "no_shrink":
        return 1.0
    if policy == "cheap_lt10_half":
        return 0.5 if row_ask < 0.10 else 1.0
    if policy == "cheap_lt10_quarter":
        return 0.25 if row_ask < 0.10 else 1.0
    if policy == "cheap_lt15_half":
        return 0.5 if row_ask < 0.15 else 1.0
    if policy == "cheap_lt15_quarter":
        return 0.25 if row_ask < 0.15 else 1.0
    if policy == "cheap_lt10_skip":
        return 0.0 if row_ask < 0.10 else 1.0
    if policy == "cheap_lt15_skip":
        return 0.0 if row_ask < 0.15 else 1.0
    raise ValueError(f"unknown policy {policy}")


def weighted_summary(rows: list[dict[str, Any]], denominator: int, policy: str) -> dict[str, Any]:
    weighted_net = 0.0
    nonzero_rows = []
    total_weight = 0.0
    for row in rows:
        weight = shrink_weight(row, policy)
        if weight <= 0.0:
            continue
        nonzero_rows.append(row)
        total_weight += weight
        weighted_net += net(row) * weight
    counts = source_counts(nonzero_rows)
    return {
        "policy": policy,
        "participating_markets": len(nonzero_rows),
        "coverage_pct": (len(nonzero_rows) / denominator * 100.0) if denominator else 0.0,
        "total_notional_weight": total_weight,
        "weighted_net_cents": weighted_net,
        "weighted_full_loss_cushion_estimate": int(max(0.0, weighted_net) // 100.0),
        "source_counts": counts,
        "reconstructed_share": reconstructed_share(counts),
        "target_coverage": (len(nonzero_rows) / denominator) >= TARGET_COVERAGE if denominator else False,
    }


def evaluate_lane(label: str, surfaces_fn: Any, freeze_ts: str) -> dict[str, Any]:
    all_rows, _, denominator_raw = surfaces_fn(freeze_ts)
    denominator = int(denominator_raw or 0)
    broad = select_by_market(all_rows, RULES[BROAD_RULE])
    strict = select_by_market(all_rows, RULES[STRICT_RULE])
    broad_rows = list(broad.values())
    strict_markets = set(strict)
    added_rows = [row for row_market, row in broad.items() if row_market not in strict_markets]
    reconstructed_rows = [row for row in broad_rows if source(row) != "approved_entry"]
    cheap_rows = [row for row in broad_rows if (ask(row) is not None and ask(row) < 0.10)]
    cheap_added_rows = [row for row in added_rows if (ask(row) is not None and ask(row) < 0.10)]
    top_reconstructed_win = max((net(row) for row in reconstructed_rows), default=0.0)

    bucket_counts: dict[str, Any] = {}
    for bucket in sorted({tail_bucket(row) for row in broad_rows}):
        bucket_rows = [row for row in broad_rows if tail_bucket(row) == bucket]
        bucket_counts[bucket] = group_summary(bucket_rows)

    source_tail_counts: Counter[str] = Counter()
    for row in broad_rows:
        source_tail_counts[f"{source(row)}::{tail_bucket(row)}"] += 1

    policies = [
        "no_shrink",
        "cheap_lt10_half",
        "cheap_lt10_quarter",
        "cheap_lt15_half",
        "cheap_lt15_quarter",
        "cheap_lt10_skip",
        "cheap_lt15_skip",
    ]

    return {
        "lane": label,
        "freeze_ts_utc": freeze_ts,
        "future_denominator": denominator,
        "broad_rule": BROAD_RULE,
        "strict_rule": STRICT_RULE,
        "broad_summary": summarize(broad_rows, denominator),
        "broad_source_counts": source_counts(broad_rows),
        "broad_reconstructed_share": reconstructed_share(source_counts(broad_rows)),
        "strict_summary": summarize(list(strict.values()), denominator),
        "strict_source_counts": source_counts(list(strict.values())),
        "strict_reconstructed_share": reconstructed_share(source_counts(list(strict.values()))),
        "added_vs_strict_summary": group_summary(added_rows),
        "cheap_tail_summary": group_summary(cheap_rows),
        "cheap_added_vs_strict_summary": group_summary(cheap_added_rows),
        "tail_buckets": bucket_counts,
        "source_tail_counts": dict(source_tail_counts),
        "reconstructed_rows_net_cents": sum(net(row) for row in reconstructed_rows),
        "top_reconstructed_win_cents": top_reconstructed_win,
        "reconstructed_net_without_top_win_cents": sum(net(row) for row in reconstructed_rows) - top_reconstructed_win,
        "notional_shrink_policies": [weighted_summary(broad_rows, denominator, policy) for policy in policies],
        "added_examples": [row_digest(row) for row in added_rows],
    }


def interpretation(lanes: list[dict[str, Any]]) -> list[str]:
    notes = [
        "This is a failure-mode audit, not a promotion candidate.",
        "Selection policies below use only observable ask price; source labels are used only to audit whether cheap-tail rows explain the source-quality blocker.",
    ]
    for lane in lanes:
        broad = lane.get("broad_summary") or {}
        cheap = lane.get("cheap_added_vs_strict_summary") or {}
        shrink = {row.get("policy"): row for row in lane.get("notional_shrink_policies") or []}
        half = shrink.get("cheap_lt10_half") or {}
        skip = shrink.get("cheap_lt10_skip") or {}
        notes.append(
            f"{lane.get('lane')} broad {lane.get('broad_rule')} has {broad.get('settled')} settled, "
            f"coverage {broad.get('coverage_pct')}%, net {broad.get('net_cents')}c, reconstructed share "
            f"{lane.get('broad_reconstructed_share')}."
        )
        notes.append(
            f"{lane.get('lane')} cheap added rows versus strict ask-floor are {cheap.get('rows')} row(s), "
            f"net {cheap.get('net_cents')}c, W/L {cheap.get('wl')}, source counts {cheap.get('source_counts')}."
        )
        notes.append(
            f"{lane.get('lane')} reconstructed rows net {lane.get('reconstructed_rows_net_cents')}c; without the top reconstructed win "
            f"the reconstructed slice is {lane.get('reconstructed_net_without_top_win_cents')}c."
        )
        notes.append(
            f"{lane.get('lane')} cheap_lt10_half keeps coverage {half.get('coverage_pct')}% with weighted net "
            f"{half.get('weighted_net_cents')}c; cheap_lt10_skip coverage is {skip.get('coverage_pct')}%."
        )
    return notes


def build_report() -> dict[str, Any]:
    state = load_or_create_state()
    freeze_ts = str(state["freeze_ts_utc"])
    lanes = [
        evaluate_lane("post_feature_freeze_entry", entry_surfaces, freeze_ts),
        evaluate_lane("post_feature_freeze_bridge", bridge_surfaces, freeze_ts),
    ]
    return {
        "generated_at_utc": utc_now_iso(),
        "freeze_ts_utc": freeze_ts,
        "target_coverage": TARGET_COVERAGE,
        "max_reconstructed_share": MAX_RECONSTRUCTED_SHARE,
        "lanes": lanes,
        "interpretation": interpretation(lanes),
    }


def fmt(value: Any) -> str:
    if value is None:
        return "None"
    if isinstance(value, float):
        return f"{value:.6f}"
    return str(value)


def write_md(report: dict[str, Any]) -> None:
    lines = [
        "# v28 Boundary-Clock Feature-Gate Cheap-Tail Risk Audit",
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
        broad = lane.get("broad_summary") or {}
        strict = lane.get("strict_summary") or {}
        added = lane.get("added_vs_strict_summary") or {}
        cheap_added = lane.get("cheap_added_vs_strict_summary") or {}
        lines.extend(
            [
                f"- Broad rule: `{lane.get('broad_rule')}`",
                f"- Strict clean rule: `{lane.get('strict_rule')}`",
                f"- Broad settled/coverage/net/recon: `{broad.get('settled')}/{broad.get('coverage_pct')}/{broad.get('net_cents')}c/{lane.get('broad_reconstructed_share')}`",
                f"- Strict settled/coverage/net/recon: `{strict.get('settled')}/{strict.get('coverage_pct')}/{strict.get('net_cents')}c/{lane.get('strict_reconstructed_share')}`",
                f"- Added rows versus strict: `{added.get('rows')}` rows, `{added.get('net_cents')}c`, W/L `{added.get('wl')}`, sources `{added.get('source_counts')}`",
                f"- Cheap added rows versus strict: `{cheap_added.get('rows')}` rows, `{cheap_added.get('net_cents')}c`, W/L `{cheap_added.get('wl')}`, sources `{cheap_added.get('source_counts')}`",
                f"- Reconstructed rows net/top-win/net-without-top-win: `{lane.get('reconstructed_rows_net_cents')}/{lane.get('top_reconstructed_win_cents')}/{lane.get('reconstructed_net_without_top_win_cents')}c`",
                "",
                "### Tail Buckets",
                "",
                "| bucket | rows | net c | W/L | recon share | avg ask | avg edge | avg recross | avg abs d |",
                "|---|---:|---:|---|---:|---:|---:|---:|---:|",
            ]
        )
        for bucket, summary in (lane.get("tail_buckets") or {}).items():
            wl_text = summary.get("wl") or {}
            lines.append(
                f"| {bucket} | {summary.get('rows')} | {fmt(summary.get('net_cents'))} | "
                f"{wl_text.get('wins')}/{wl_text.get('losses')} | {fmt(summary.get('reconstructed_share'))} | "
                f"{fmt(summary.get('avg_ask'))} | {fmt(summary.get('avg_raw_edge'))} | "
                f"{fmt(summary.get('avg_recross'))} | {fmt(summary.get('avg_abs_d'))} |"
            )

        lines.extend(
            [
                "",
                "### Observable Notional Policies",
                "",
                "| policy | participating | coverage | weight | weighted net c | cushion | recon share | target cov |",
                "|---|---:|---:|---:|---:|---:|---:|---|",
            ]
        )
        for policy in lane.get("notional_shrink_policies") or []:
            lines.append(
                f"| {policy.get('policy')} | {policy.get('participating_markets')} | "
                f"{fmt(policy.get('coverage_pct'))} | {fmt(policy.get('total_notional_weight'))} | "
                f"{fmt(policy.get('weighted_net_cents'))} | {policy.get('weighted_full_loss_cushion_estimate')} | "
                f"{fmt(policy.get('reconstructed_share'))} | {policy.get('target_coverage')} |"
            )

        lines.extend(
            [
                "",
                "### Added Rows Versus Strict Ask-Floor",
                "",
                "| market | source | side | won | net c | edge | recross | abs d | ask |",
                "|---|---|---|---|---:|---:|---:|---:|---:|",
            ]
        )
        for row in lane.get("added_examples") or []:
            lines.append(
                f"| {row.get('market')} | {row.get('source')} | {row.get('side')} | {row.get('side_won')} | "
                f"{fmt(row.get('net_cents'))} | {fmt(row.get('raw_edge'))} | {fmt(row.get('recross_hazard_score'))} | "
                f"{fmt(row.get('abs_d_sigma'))} | {fmt(row.get('ask_prob'))} |"
            )

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    report = build_report()
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
    write_md(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
