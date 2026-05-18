"""Denominator-gap audit for the nearest feature-gate promotion watch row.

Research-only; no live bot changes or orders.

This does not search thresholds. It explains why the already-frozen
near-promotion feature-gate row is still short of target coverage by auditing
omitted post-freeze denominator markets and their observable fail reasons.
"""
from __future__ import annotations

import json
import math
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from probe_v28_boundary_clock_feature_gate_candidate import (
    RULES,
    best_per_market,
    load_or_create_state,
    market,
    net,
    passes,
    raw_edge,
    recross,
    source,
)
from probe_v28_frozen_boundary_clock_fv_entry_bridge import future_surfaces as bridge_surfaces
from probe_v28_frozen_boundary_clock_repair_entry import future_surfaces as entry_surfaces


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
WATCH_JSON = OUT_DIR / "v28_feature_gate_near_promotion_watch_latest.json"
OUT_JSON = OUT_DIR / "v28_feature_gate_near_promotion_denominator_gap_latest.json"
OUT_MD = OUT_DIR / "v28_feature_gate_near_promotion_denominator_gap_latest.md"

COVERAGE_FLOOR = 75.0
MAX_RECONSTRUCTED_SHARE = 0.35
MIN_CUSHION_CENTS = 300.0


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


def as_float(value: Any) -> float | None:
    if value is None or value == "":
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


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
    return reasons or ["passes_rule_but_not_selected_best_market"]


def selected_candidate() -> dict[str, Any]:
    watch = load_json(WATCH_JSON)
    rows = [row for row in watch.get("rows") or [] if isinstance(row, dict)]
    if rows:
        return rows[0]
    return {}


def source_share(rows: list[dict[str, Any]]) -> float | None:
    if not rows:
        return None
    reconstructed = sum(1 for row in rows if not is_approved(row))
    return reconstructed / len(rows)


def rows_for_coverage(entries: int, denominator: int) -> int:
    if denominator <= 0:
        return 0
    required = math.ceil(COVERAGE_FLOOR * denominator / 100.0)
    return max(0, required - entries)


def approved_rows_needed_for_source_gate(rows: list[dict[str, Any]]) -> int:
    """Rows needed if the future additions are all approved selected rows."""
    if not rows:
        return 0
    reconstructed = sum(1 for row in rows if not is_approved(row))
    if reconstructed / len(rows) <= MAX_RECONSTRUCTED_SHARE:
        return 0
    needed = math.ceil((reconstructed / MAX_RECONSTRUCTED_SHARE) - len(rows))
    return max(0, needed)


def summarize_rows(rows: list[dict[str, Any]]) -> dict[str, Any]:
    settled = [row for row in rows if is_settled(row)]
    wins = sum(1 for row in settled if net(row) > 0)
    losses = sum(1 for row in settled if net(row) < 0)
    return {
        "rows": len(rows),
        "settled": len(settled),
        "wins": wins,
        "losses": losses,
        "net_cents": sum(net(row) for row in settled),
        "source_counts": dict(Counter(source(row) for row in rows)),
        "reconstructed_share": source_share(rows),
    }


def row_detail(row: dict[str, Any], rule: dict[str, Any] | None = None) -> dict[str, Any]:
    detail = {
        "market": market(row),
        "source": source(row),
        "side": row.get("side"),
        "settled": is_settled(row),
        "side_won": row.get("side_won"),
        "net_cents": net(row) if is_settled(row) else None,
        "raw_edge": raw_edge(row),
        "recross_hazard_score": row.get("recross_hazard_score"),
        "abs_d_sigma": row.get("abs_d_sigma"),
        "ask_prob": row.get("ask_prob"),
    }
    if rule is not None:
        detail["fail_reasons"] = fail_reasons(row, rule)
    return detail


def build_report() -> dict[str, Any]:
    watch_row = selected_candidate()
    candidate = str(watch_row.get("candidate") or "")
    lane = str(watch_row.get("lane") or "")
    rule_name = str(watch_row.get("rule") or "")
    rule = RULES.get(rule_name) or {}
    freeze_ts = str(load_or_create_state().get("freeze_ts_utc") or "")
    surfaces = bridge_surfaces if lane.endswith("_bridge") else entry_surfaces
    all_rows, _, denominator = surfaces(freeze_ts)
    selected = best_per_market([row for row in all_rows if passes(row, rule)])
    selected_markets = {market(row) for row in selected}
    denominator_reps = best_per_market(all_rows)
    omitted = [row for row in denominator_reps if market(row) not in selected_markets]
    pending_selected = [row for row in selected if not is_settled(row)]
    settled_selected = [row for row in selected if is_settled(row)]
    selected_entries = len(selected)
    coverage_needed = rows_for_coverage(selected_entries, int(denominator or 0))
    cushion_needed = max(0.0, MIN_CUSHION_CENTS - sum(net(row) for row in settled_selected))
    approved_for_source_needed = approved_rows_needed_for_source_gate(selected)

    omitted_details = []
    reason_counter: Counter[str] = Counter()
    source_counter: Counter[str] = Counter()
    reason_source_counter: Counter[str] = Counter()
    for row in omitted:
        reasons = fail_reasons(row, rule)
        reason_counter.update(reasons)
        row_source = source(row)
        source_counter[row_source] += 1
        for reason in reasons:
            reason_source_counter[f"{reason}::{row_source}"] += 1
        omitted_details.append(row_detail(row, rule))

    top_counterfactual = sorted(
        [row for row in omitted if is_settled(row)],
        key=lambda row: net(row),
        reverse=True,
    )[: max(coverage_needed, 1)]
    counterfactual_rows = selected + top_counterfactual
    counterfactual = summarize_rows(counterfactual_rows)
    counterfactual["added_rows"] = [
        {
            "market": market(row),
            "source": source(row),
            "side": row.get("side"),
            "net_cents": net(row),
            "fail_reasons": fail_reasons(row, rule),
        }
        for row in top_counterfactual
    ]
    counterfactual["coverage_pct_if_added_to_current_denominator"] = (
        100.0 * len(counterfactual_rows) / denominator if denominator else None
    )
    counterfactual["source_gate_if_added"] = (
        counterfactual.get("reconstructed_share") is not None
        and counterfactual.get("reconstructed_share") <= MAX_RECONSTRUCTED_SHARE
    )
    counterfactual["cushion_gate_if_added"] = (counterfactual.get("net_cents") or 0) >= MIN_CUSHION_CENTS

    report = {
        "generated_at_utc": utc_now_iso(),
        "candidate": candidate,
        "lane": lane,
        "rule": rule_name,
        "freeze_ts_utc": freeze_ts,
        "future_denominator": denominator,
        "selected_summary": summarize_rows(selected),
        "selected_entries": selected_entries,
        "settled_selected": len(settled_selected),
        "pending_selected_summary": summarize_rows(pending_selected),
        "pending_selected_rows": [row_detail(row) for row in pending_selected],
        "coverage_entries_needed": coverage_needed,
        "approved_selected_rows_needed_for_source_gate": approved_for_source_needed,
        "cushion_cents_needed": cushion_needed,
        "omitted_summary": summarize_rows(omitted),
        "omitted_fail_reason_counts": dict(reason_counter),
        "omitted_source_counts": dict(source_counter),
        "omitted_reason_source_counts": dict(reason_source_counter),
        "top_counterfactual_added_omitted_rows": counterfactual,
        "omitted_rows": omitted_details,
    }
    report["interpretation"] = interpretation(report)
    return report


def interpretation(report: dict[str, Any]) -> list[str]:
    selected = report.get("selected_summary") or {}
    omitted = report.get("omitted_summary") or {}
    pending = report.get("pending_selected_summary") or {}
    counter = report.get("top_counterfactual_added_omitted_rows") or {}
    notes = [
        "This is a denominator audit of an already-frozen watch row, not a threshold search.",
        (
            f"{report.get('candidate')} has {selected.get('rows')} selected denominator markets, "
            f"{selected.get('settled')} settled, {pending.get('rows')} pending, and needs "
            f"{report.get('coverage_entries_needed')} more selected denominator markets for 75% coverage."
        ),
        (
            f"It also needs {report.get('approved_selected_rows_needed_for_source_gate')} additional clean approved selected "
            f"row(s), assuming no new rejected selected rows, to dilute reconstructed/share quality back under 35%."
        ),
        (
            f"Omitted markets are mainly blocked by {report.get('omitted_fail_reason_counts')} "
            f"with source mix {report.get('omitted_source_counts')}."
        ),
    ]
    if pending.get("rows"):
        notes.append(
            f"Pending selected rows can help sample/cushion if they settle well, but they are already counted in coverage."
        )
    if counter.get("added_rows"):
        notes.append(
            f"Best-settled omitted-row counterfactual for the coverage gap would bring coverage to "
            f"{counter.get('coverage_pct_if_added_to_current_denominator')}%, net to {counter.get('net_cents')}c, "
            f"source gate {counter.get('source_gate_if_added')}, cushion gate {counter.get('cushion_gate_if_added')}; "
            "this is diagnostic only and cannot promote a relaxation."
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
        "# v28 Feature-Gate Near-Promotion Denominator Gap",
        "",
        "Research-only denominator audit. No live bot changes or orders.",
        "",
        f"- Generated UTC: `{report.get('generated_at_utc')}`",
        f"- Candidate: `{report.get('candidate')}`",
        f"- Rule: `{report.get('rule')}`",
        f"- Freeze UTC: `{report.get('freeze_ts_utc')}`",
        "",
        "## Interpretation",
        "",
    ]
    for note in report.get("interpretation") or []:
        lines.append(f"- {note}")
    lines.extend(
        [
            "",
            "## Gate Snapshot",
            "",
            f"- Future denominator: `{report.get('future_denominator')}`",
            f"- Selected entries / coverage-needed entries: `{report.get('selected_entries')}` / `{report.get('coverage_entries_needed')}`",
            f"- Clean approved selected rows needed for source gate: `{report.get('approved_selected_rows_needed_for_source_gate')}`",
            f"- Settled selected / pending selected: `{report.get('settled_selected')}` / `{(report.get('pending_selected_summary') or {}).get('rows')}`",
            f"- Cushion cents needed: `{fmt(report.get('cushion_cents_needed'))}`",
            f"- Selected summary: `{report.get('selected_summary')}`",
            f"- Pending selected summary: `{report.get('pending_selected_summary')}`",
            f"- Omitted summary: `{report.get('omitted_summary')}`",
            "",
            "## Pending Selected Rows",
            "",
            "| market | source | side | edge | recross | abs d | ask |",
            "|---|---|---|---:|---:|---:|---:|",
        ]
    )
    for row in report.get("pending_selected_rows") or []:
        lines.append(
            f"| {row.get('market')} | {row.get('source')} | {row.get('side')} | "
            f"{fmt(row.get('raw_edge'))} | {fmt(row.get('recross_hazard_score'))} | "
            f"{fmt(row.get('abs_d_sigma'))} | {fmt(row.get('ask_prob'))} |"
        )
    lines.extend(
        [
            "",
            "## Omitted Fail Reasons",
            "",
            f"- By reason: `{report.get('omitted_fail_reason_counts')}`",
            f"- By source: `{report.get('omitted_source_counts')}`",
            f"- By reason/source: `{report.get('omitted_reason_source_counts')}`",
            "",
            "## Best Settled Omitted-Row Counterfactual",
            "",
            f"- Summary: `{report.get('top_counterfactual_added_omitted_rows')}`",
            "",
            "## Omitted Rows",
            "",
            "| market | source | side | settled | net c | edge | recross | abs d | ask | fail reasons |",
            "|---|---|---|---:|---:|---:|---:|---:|---:|---|",
        ]
    )
    for row in report.get("omitted_rows") or []:
        lines.append(
            f"| {row.get('market')} | {row.get('source')} | {row.get('side')} | {row.get('settled')} | "
            f"{fmt(row.get('net_cents'))} | {fmt(row.get('raw_edge'))} | {fmt(row.get('recross_hazard_score'))} | "
            f"{fmt(row.get('abs_d_sigma'))} | {fmt(row.get('ask_prob'))} | {', '.join(row.get('fail_reasons') or [])} |"
        )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    report = build_report()
    write_md(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
