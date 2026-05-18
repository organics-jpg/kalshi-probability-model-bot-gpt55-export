"""Current strict-forward raw05 coverage-gap audit for feature gate.

Research-only; no live bot changes or orders.

raw05 is the source-cleaner feature-gate lane but under-covers. This audit
checks the current strict post-freeze denominator and asks whether the missing
coverage is available from approved/source-clean rows in principle. Source
labels and realized outcomes are audit-only; this does not define a deployable
rule.
"""
from __future__ import annotations

import json
import math
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

from probe_v28_boundary_clock_feature_gate_candidate import (
    RULES,
    STATE_JSON,
    as_float,
    load_json,
    market,
    passes,
    raw_edge,
    recross,
    source,
)
from probe_v28_boundary_clock_feature_gate_quick_status import best_per_market
from probe_v28_coverage_repair_pool_diagnostic import row_net_after_fee, summarize
from probe_v28_frozen_boundary_clock_fv_entry_bridge import future_surfaces as bridge_surfaces
from probe_v28_frozen_boundary_clock_repair_entry import future_surfaces as entry_surfaces


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
LIVE_SUMMARY_JSON = ROOT / "stats" / "live_mushroom_v28_size2" / "summary.json"
OUT_JSON = OUT_DIR / "v28_feature_gate_raw05_coverage_gap_audit_latest.json"
OUT_MD = OUT_DIR / "v28_feature_gate_raw05_coverage_gap_audit_latest.md"

RAW05 = "raw05_recross60_abs085"
TARGET_COVERAGE = 75.0
MAX_RECON_SHARE = 0.35


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def net(row: dict[str, Any]) -> float:
    return float(row_net_after_fee(row) or 0.0)


def is_settled(row: dict[str, Any]) -> bool:
    return row.get("side_won") is not None


def is_approved(row: dict[str, Any]) -> bool:
    return source(row) == "approved_entry"


def fail_reasons(row: dict[str, Any], rule: dict[str, Any]) -> list[str]:
    reasons: list[str] = []
    edge = raw_edge(row)
    row_recross = recross(row)
    abs_d = as_float(row.get("abs_d_sigma"))
    ask = as_float(row.get("ask_prob"))
    if edge is None:
        reasons.append("raw_edge_missing")
    elif edge < float(rule["raw_edge_min"]):
        reasons.append("raw_edge_below_min")
    if row_recross is None:
        reasons.append("recross_missing")
    elif row_recross > float(rule["recross_max"]):
        reasons.append("recross_above_max")
    if abs_d is None:
        reasons.append("abs_d_missing")
    elif abs_d < float(rule["abs_d_min"]):
        reasons.append("abs_d_below_min")
    ask_min = rule.get("ask_min")
    if ask_min is not None:
        if ask is None:
            reasons.append("ask_missing")
        elif ask < float(ask_min):
            reasons.append("ask_below_min")
    return reasons or ["passes_rule_but_not_selected"]


def source_counts(rows: list[dict[str, Any]]) -> dict[str, int]:
    return dict(Counter(source(row) for row in rows))


def reconstructed_share(rows: list[dict[str, Any]]) -> float | None:
    if not rows:
        return None
    return sum(1 for row in rows if not is_approved(row)) / len(rows)


def compact(row: dict[str, Any], rule: dict[str, Any]) -> dict[str, Any]:
    return {
        "market": market(row),
        "source": source(row),
        "side": row.get("side"),
        "side_won": row.get("side_won"),
        "net_cents": net(row) if is_settled(row) else None,
        "raw_edge": raw_edge(row),
        "recross_hazard_score": row.get("recross_hazard_score"),
        "abs_d_sigma": row.get("abs_d_sigma"),
        "ask_prob": row.get("ask_prob"),
        "p_side": row.get("p_side"),
        "seconds_to_close": row.get("seconds_to_close"),
        "eligible_depth": row.get("eligible_depth"),
        "fail_reasons": fail_reasons(row, rule),
    }


def required_entries(denominator: int) -> int:
    return int(math.ceil((TARGET_COVERAGE / 100.0) * denominator))


def summarize_rows(rows: list[dict[str, Any]], denominator: int) -> dict[str, Any]:
    base = summarize(rows, denominator)
    return {
        **base,
        "source_counts": source_counts(rows),
        "reconstructed_share": reconstructed_share(rows),
    }


def scenario_add_rows(base_rows: list[dict[str, Any]], add_rows: list[dict[str, Any]], denominator: int) -> dict[str, Any]:
    rows = base_rows + add_rows
    summary = summarize_rows(rows, denominator)
    net_cents = float(summary.get("net_cents") or 0.0)
    share = summary.get("reconstructed_share")
    blockers: list[str] = []
    if float(summary.get("coverage_pct") or 0.0) < TARGET_COVERAGE:
        blockers.append("coverage_too_low")
    if share is not None and share > MAX_RECON_SHARE:
        blockers.append("reconstructed_share_gt_35pct")
    if net_cents <= 0.0:
        blockers.append("net_not_positive")
    if int(max(0.0, net_cents) // 100.0) < 3:
        blockers.append("full_loss_cushion_lt_3")
    return {
        "added_rows": len(add_rows),
        "added_net_cents": sum(net(row) for row in add_rows if is_settled(row)),
        "added_source_counts": source_counts(add_rows),
        "summary": summary,
        "blockers": blockers,
        "rows": add_rows,
    }


def evaluate_lane(
    lane: str,
    freeze_ts: str,
    surfaces_fn: Callable[[str], tuple[list[dict[str, Any]], list[dict[str, Any]], int]],
) -> dict[str, Any]:
    all_rows, _target, denominator_raw = surfaces_fn(freeze_ts)
    denominator = int(denominator_raw or 0)
    rule = RULES[RAW05]
    selected = best_per_market([row for row in all_rows if passes(row, rule)])
    selected_markets = {market(row) for row in selected}
    denominator_reps = best_per_market(all_rows)
    omitted = [row for row in denominator_reps if market(row) not in selected_markets]
    missing = max(0, required_entries(denominator) - len(selected))
    omitted_by_source: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in omitted:
        omitted_by_source[source(row)].append(row)
    approved_omitted = sorted(omitted_by_source.get("approved_entry", []), key=net, reverse=True)
    rejected_omitted = sorted(
        [row for row in omitted if not is_approved(row)],
        key=net,
        reverse=True,
    )
    top_approved = approved_omitted[:missing]
    top_any = sorted(omitted, key=net, reverse=True)[:missing]
    reason_counts = Counter()
    reason_source_counts = Counter()
    for row in omitted:
        reasons = fail_reasons(row, rule)
        reason_counts.update(reasons)
        for reason in reasons:
            reason_source_counts[f"{reason}::{source(row)}"] += 1
    approved_oracle = scenario_add_rows(selected, top_approved, denominator)
    any_oracle = scenario_add_rows(selected, top_any, denominator)
    return {
        "lane": lane,
        "future_denominator": denominator,
        "required_entries": required_entries(denominator),
        "raw05_selected": summarize_rows(selected, denominator),
        "missing_entries_for_75pct": missing,
        "omitted_summary": summarize_rows(omitted, denominator),
        "omitted_source_counts": source_counts(omitted),
        "omitted_fail_reason_counts": dict(reason_counts),
        "omitted_fail_reason_source_counts": dict(reason_source_counts),
        "approved_omitted_count": len(approved_omitted),
        "rejected_omitted_count": len(rejected_omitted),
        "approved_only_oracle_add_missing": {
            **{key: value for key, value in approved_oracle.items() if key != "rows"},
            "added_rows_detail": [compact(row, rule) for row in top_approved],
        },
        "best_any_source_oracle_add_missing": {
            **{key: value for key, value in any_oracle.items() if key != "rows"},
            "added_rows_detail": [compact(row, rule) for row in top_any],
        },
        "top_approved_omitted": [compact(row, rule) for row in approved_omitted[:12]],
        "top_rejected_omitted": [compact(row, rule) for row in rejected_omitted[:12]],
        "worst_approved_omitted": [compact(row, rule) for row in sorted(approved_omitted, key=net)[:8]],
    }


def build_report() -> dict[str, Any]:
    state = load_json(STATE_JSON)
    freeze_ts = str(state.get("freeze_ts_utc") or "")
    live = load_json(LIVE_SUMMARY_JSON)
    live_cents = float(live.get("net_pnl_total_dollars") or 0.0) * 100.0
    lanes = [
        evaluate_lane("post_feature_freeze_entry", freeze_ts, entry_surfaces),
        evaluate_lane("post_feature_freeze_bridge", freeze_ts, bridge_surfaces),
    ]
    return {
        "generated_at_utc": utc_now_iso(),
        "state": state,
        "live_baseline_cents": live_cents,
        "lanes": lanes,
        "interpretation": interpretation(lanes, live_cents),
    }


def interpretation(lanes: list[dict[str, Any]], live_cents: float) -> list[str]:
    notes = ["Audit-only source labels; approved-only oracle rows are not deployable evidence."]
    for lane in lanes:
        selected = lane["raw05_selected"]
        approved = lane["approved_only_oracle_add_missing"]
        any_source = lane["best_any_source_oracle_add_missing"]
        notes.append(
            f"{lane['lane']}: raw05 needs {lane['missing_entries_for_75pct']} entries for 75% coverage; "
            f"omitted approved/rejected counts are {lane['approved_omitted_count']}/{lane['rejected_omitted_count']}."
        )
        notes.append(
            f"{lane['lane']}: approved-only oracle after adding missing rows has net "
            f"{(approved.get('summary') or {}).get('net_cents')}c and blockers {approved.get('blockers')}; "
            f"best-any-source oracle has net {(any_source.get('summary') or {}).get('net_cents')}c and blockers {any_source.get('blockers')}; "
            f"live baseline is {live_cents:.0f}c."
        )
        notes.append(
            f"{lane['lane']}: raw05 selected net {selected.get('net_cents')}c, coverage {selected.get('coverage_pct')}%, "
            f"recon {selected.get('reconstructed_share')}."
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
    lines = [
        "# v28 Feature-Gate raw05 Coverage-Gap Audit",
        "",
        "Research-only; source labels and outcomes are audit-only.",
        "",
        f"- Generated UTC: `{report.get('generated_at_utc')}`",
        f"- Feature-gate freeze UTC: `{(report.get('state') or {}).get('freeze_ts_utc')}`",
        f"- Refreshed live baseline: `{fmt(report.get('live_baseline_cents'))}c`",
        "",
        "## Interpretation",
        "",
    ]
    for note in report.get("interpretation") or []:
        lines.append(f"- {note}")
    for lane in report.get("lanes") or []:
        selected = lane.get("raw05_selected") or {}
        approved = lane.get("approved_only_oracle_add_missing") or {}
        any_source = lane.get("best_any_source_oracle_add_missing") or {}
        lines.extend(
            [
                "",
                f"## {lane.get('lane')}",
                "",
                f"- Future denominator: `{lane.get('future_denominator')}`",
                f"- Required entries for 75%: `{lane.get('required_entries')}`",
                f"- raw05 missing entries: `{lane.get('missing_entries_for_75pct')}`",
                f"- Omitted source counts: `{lane.get('omitted_source_counts')}`",
                f"- Omitted fail reasons: `{lane.get('omitted_fail_reason_counts')}`",
                "",
                "| scenario | entries | settled | coverage | net c | W/L | recon share | added source | blockers |",
                "|---|---:|---:|---:|---:|---:|---:|---|---|",
            ]
        )
        for label, payload in [
            ("raw05", {"summary": selected, "added_source_counts": {}}),
            ("approved_only_oracle", approved),
            ("best_any_source_oracle", any_source),
        ]:
            summary = payload.get("summary") or {}
            lines.append(
                f"| {label} | {summary.get('entries')} | {summary.get('settled')} | "
                f"{fmt(summary.get('coverage_pct'))} | {fmt(summary.get('net_cents'))} | "
                f"{summary.get('wins')}/{summary.get('losses')} | {fmt(summary.get('reconstructed_share'))} | "
                f"{payload.get('added_source_counts') or {}} | {', '.join(payload.get('blockers') or []) or 'none'} |"
            )
        lines.extend(
            [
                "",
                "### Approved Omitted Rows",
                "",
                "| market | side | won | net c | raw edge | recross | abs d | ask | p_side | stc | depth | fail reasons |",
                "|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|",
            ]
        )
        for row in lane.get("top_approved_omitted") or []:
            lines.append(
                f"| {row.get('market')} | {row.get('side')} | {row.get('side_won')} | {fmt(row.get('net_cents'))} | "
                f"{fmt(row.get('raw_edge'))} | {fmt(row.get('recross_hazard_score'))} | {fmt(row.get('abs_d_sigma'))} | "
                f"{fmt(row.get('ask_prob'))} | {fmt(row.get('p_side'))} | {fmt(row.get('seconds_to_close'))} | "
                f"{fmt(row.get('eligible_depth'))} | {', '.join(row.get('fail_reasons') or [])} |"
            )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    report = build_report()
    write_report(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
