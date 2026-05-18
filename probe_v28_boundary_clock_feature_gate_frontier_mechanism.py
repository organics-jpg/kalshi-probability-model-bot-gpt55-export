"""Mechanism drilldown for the boundary-clock feature-gate frontier.

Research-only; no live bot changes or orders.

This explains the current best observable coverage/source frontier row. It is
not a new candidate freeze and does not use source labels for selection.
"""
from __future__ import annotations

import json
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from statistics import mean
from typing import Any

from probe_v28_boundary_clock_feature_gate_candidate import (
    RULES,
    as_float,
    best_per_market,
    load_or_create_state,
    market,
    net,
    recross,
    source,
)
from probe_v28_boundary_clock_feature_gate_coverage_source_frontier import (
    OUT_JSON as FRONTIER_JSON,
    passes_rule,
)
from probe_v28_coverage_repair_pool_diagnostic import raw_edge, summarize
from probe_v28_frozen_boundary_clock_fv_entry_bridge import future_surfaces as bridge_surfaces
from probe_v28_frozen_boundary_clock_repair_entry import future_surfaces as entry_surfaces


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
OUT_JSON = OUT_DIR / "v28_boundary_clock_feature_gate_frontier_mechanism_latest.json"
OUT_MD = OUT_DIR / "v28_boundary_clock_feature_gate_frontier_mechanism_latest.md"

REFERENCE_RULE_NAME = "raw05_recross60_abs085_ask65"
REFERENCE_RULE = RULES[REFERENCE_RULE_NAME]


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


def bool_outcome(row: dict[str, Any]) -> str:
    side_won = row.get("side_won")
    if side_won is True:
        return "win"
    if side_won is False:
        return "loss"
    return "unsettled"


def compact_row(row: dict[str, Any], rule: dict[str, Any] | None = None) -> dict[str, Any]:
    out = {
        "market": market(row),
        "source": source(row),
        "side": row.get("side"),
        "side_won": row.get("side_won"),
        "outcome": bool_outcome(row),
        "net_cents": net(row),
        "raw_edge": raw_edge(row),
        "recross_hazard_score": recross(row),
        "abs_d_sigma": as_float(row.get("abs_d_sigma")),
        "ask_prob": as_float(row.get("ask_prob")),
    }
    if rule is not None:
        out["fail_reasons"] = fail_reasons(row, rule)
        out["mechanism_tags"] = mechanism_tags(row)
    return out


def fail_reasons(row: dict[str, Any], rule: dict[str, Any]) -> list[str]:
    reasons: list[str] = []
    edge = raw_edge(row)
    row_recross = recross(row)
    abs_d = as_float(row.get("abs_d_sigma"))
    ask = as_float(row.get("ask_prob"))
    if edge is None or edge < float(rule["raw_edge_min"]):
        reasons.append("raw_edge_below_min")
    if row_recross is None or row_recross > float(rule["recross_max"]):
        reasons.append("recross_above_max")
    if abs_d is None or abs_d < float(rule["abs_d_min"]):
        reasons.append("abs_d_below_min")
    ask_min = rule.get("ask_min")
    if ask_min is not None and (ask is None or ask < float(ask_min)):
        reasons.append("ask_below_min")
    return reasons


def mechanism_tags(row: dict[str, Any]) -> list[str]:
    tags: list[str] = []
    edge = raw_edge(row)
    row_recross = recross(row)
    abs_d = as_float(row.get("abs_d_sigma"))
    ask = as_float(row.get("ask_prob"))
    row_net = net(row)
    if source(row) != "approved_entry":
        tags.append("source_quality_risk")
    if row.get("side_won") is False:
        tags.append("realized_loss")
    if row_net <= 5.0:
        tags.append("thin_or_negative_net")
    if edge is not None and edge < 0.05:
        tags.append("thin_raw_edge")
    if row_recross is not None and row_recross > 0.50:
        tags.append("high_recross_boundary_churn")
    if abs_d is not None and abs_d < 0.50:
        tags.append("very_near_strike")
    elif abs_d is not None and abs_d < 0.85:
        tags.append("near_strike_boundary_pull")
    if ask is not None and ask < 0.35:
        tags.append("cheap_tail_touch")
    elif ask is not None and ask < 0.65:
        tags.append("mid_cheap_touch")
    return tags or ["clean_or_unclassified"]


def selected_by_market(rows: list[dict[str, Any]], rule: dict[str, Any]) -> dict[str, dict[str, Any]]:
    selected = best_per_market([row for row in rows if passes_rule(row, rule)])
    return {market(row): row for row in selected if market(row)}


def representative_denominator(rows: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        row_market = market(row)
        if row_market:
            grouped[row_market].append(row)
    return {
        row_market: max(items, key=lambda row: raw_edge(row) or -999.0)
        for row_market, items in grouped.items()
    }


def summarize_group(rows: list[dict[str, Any]], denominator: int) -> dict[str, Any]:
    summary = summarize(rows, denominator)
    features = {
        "raw_edge": [raw_edge(row) for row in rows],
        "recross_hazard_score": [recross(row) for row in rows],
        "abs_d_sigma": [as_float(row.get("abs_d_sigma")) for row in rows],
        "ask_prob": [as_float(row.get("ask_prob")) for row in rows],
    }
    summary["source_counts"] = dict(Counter(source(row) for row in rows))
    summary["mechanism_tag_counts"] = dict(Counter(tag for row in rows for tag in mechanism_tags(row)))
    summary["feature_means"] = {
        key: mean([float(value) for value in values if value is not None])
        for key, values in features.items()
        if any(value is not None for value in values)
    }
    return summary


def frontier_rule_for_lane(frontier: dict[str, Any], lane_name: str) -> dict[str, Any]:
    lanes = frontier.get("lanes") or []
    lane = next((row for row in lanes if row.get("lane") == lane_name), {})
    best = (lane.get("pareto_frontier") or [{}])[0]
    rule = best.get("rule_params") or {}
    if not rule:
        rule = {"raw_edge_min": 0.03, "recross_max": 0.50, "abs_d_min": 0.50, "ask_min": 0.35}
    return {
        "rule_name": best.get("rule") or "raw03_recross50_abs50_ask35",
        "rule_params": rule,
        "frontier_summary": best.get("summary") or {},
        "frontier_reconstructed_share": best.get("reconstructed_share"),
        "frontier_tags": best.get("frontier_tags") or [],
        "frontier_blockers": best.get("blockers") or [],
    }


def evaluate_lane(label: str, freeze_ts: str, surfaces_fn: Any, frontier: dict[str, Any]) -> dict[str, Any]:
    rows, _, denominator = surfaces_fn(freeze_ts)
    denominator = int(denominator or 0)
    frontier_rule = frontier_rule_for_lane(frontier, label)
    rule = frontier_rule["rule_params"]
    reference = selected_by_market(rows, REFERENCE_RULE)
    selected = selected_by_market(rows, rule)
    denominator_reps = representative_denominator(rows)

    gained_markets = sorted(set(selected) - set(reference))
    lost_markets = sorted(set(reference) - set(selected))
    shared_markets = sorted(set(selected) & set(reference))
    omitted_markets = sorted(set(denominator_reps) - set(selected))
    gained = [selected[key] for key in gained_markets]
    lost = [reference[key] for key in lost_markets]
    shared = [selected[key] for key in shared_markets]
    omitted = [denominator_reps[key] for key in omitted_markets]

    omitted_fail_counts = Counter(reason for row in omitted for reason in fail_reasons(row, rule))
    omitted_tag_counts = Counter(tag for row in omitted for tag in mechanism_tags(row))
    gained_tag_counts = Counter(tag for row in gained for tag in mechanism_tags(row))

    return {
        "lane": label,
        "freeze_ts_utc": freeze_ts,
        "future_denominator": denominator,
        "reference_rule": REFERENCE_RULE_NAME,
        "frontier_rule": frontier_rule,
        "reference_summary": summarize_group(list(reference.values()), denominator),
        "frontier_selected_summary": summarize_group(list(selected.values()), denominator),
        "shared_summary": summarize_group(shared, denominator),
        "gained_summary": summarize_group(gained, denominator),
        "lost_summary": summarize_group(lost, denominator),
        "omitted_summary": summarize_group(omitted, denominator),
        "omitted_fail_reason_counts": dict(omitted_fail_counts),
        "omitted_mechanism_tag_counts": dict(omitted_tag_counts),
        "gained_mechanism_tag_counts": dict(gained_tag_counts),
        "gained_rows": [compact_row(row, rule) for row in sorted(gained, key=lambda row: net(row), reverse=True)],
        "lost_rows": [compact_row(row, rule) for row in sorted(lost, key=lambda row: net(row))],
        "omitted_rows": [compact_row(row, rule) for row in sorted(omitted, key=lambda row: net(row))],
    }


def build_report() -> dict[str, Any]:
    state = load_or_create_state()
    frontier = load_json(FRONTIER_JSON)
    freeze_ts = str(state["freeze_ts_utc"])
    lanes = [
        evaluate_lane("post_feature_freeze_entry", freeze_ts, entry_surfaces, frontier),
        evaluate_lane("post_feature_freeze_bridge", freeze_ts, bridge_surfaces, frontier),
    ]
    report = {
        "generated_at_utc": utc_now_iso(),
        "freeze_ts_utc": freeze_ts,
        "purpose": "Drill down why the best observable frontier row improves PnL/source quality but still misses coverage/readiness.",
        "lanes": lanes,
    }
    report["interpretation"] = interpretation(report)
    return report


def interpretation(report: dict[str, Any]) -> list[str]:
    notes = [
        "This is a drilldown of the current frontier audit, not a new frozen promotion candidate.",
    ]
    for lane in report.get("lanes") or []:
        frontier = lane.get("frontier_selected_summary") or {}
        reference = lane.get("reference_summary") or {}
        gained = lane.get("gained_summary") or {}
        omitted = lane.get("omitted_summary") or {}
        notes.append(
            f"{lane.get('lane')}: frontier {((lane.get('frontier_rule') or {}).get('rule_name'))} selects "
            f"{frontier.get('entries')}/{lane.get('future_denominator')} for {frontier.get('net_cents')}c versus "
            f"reference {reference.get('entries')}/{lane.get('future_denominator')} for {reference.get('net_cents')}c; "
            f"gained rows net {gained.get('net_cents')}c with tags {lane.get('gained_mechanism_tag_counts')}; "
            f"omitted rows net {omitted.get('net_cents')}c with fail reasons {lane.get('omitted_fail_reason_counts')}."
        )
    return notes


def fmt(value: Any) -> str:
    if value is None:
        return "None"
    if isinstance(value, float):
        return f"{value:.6f}"
    return str(value)


def write_rows(lines: list[str], rows: list[dict[str, Any]]) -> None:
    if not rows:
        lines.append("- None.")
        return
    lines.extend(
        [
            "| market | source | side | net c | edge | recross | abs d | ask | outcome | fail reasons | tags |",
            "|---|---|---|---:|---:|---:|---:|---:|---|---|---|",
        ]
    )
    for row in rows:
        lines.append(
            f"| {row.get('market')} | {row.get('source')} | {row.get('side')} | {fmt(row.get('net_cents'))} | "
            f"{fmt(row.get('raw_edge'))} | {fmt(row.get('recross_hazard_score'))} | "
            f"{fmt(row.get('abs_d_sigma'))} | {fmt(row.get('ask_prob'))} | {row.get('outcome')} | "
            f"{', '.join(row.get('fail_reasons') or []) or 'none'} | {', '.join(row.get('mechanism_tags') or [])} |"
        )


def write_report(report: dict[str, Any]) -> None:
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8")
    lines = [
        "# v28 Boundary-Clock Feature-Gate Frontier Mechanism",
        "",
        "Research-only drilldown; no live bot changes or orders.",
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
        frontier_summary = lane.get("frontier_selected_summary") or {}
        reference_summary = lane.get("reference_summary") or {}
        gained_summary = lane.get("gained_summary") or {}
        omitted_summary = lane.get("omitted_summary") or {}
        lines.extend(
            [
                "",
                f"## {lane.get('lane')}",
                "",
                f"- Frontier rule: `{(lane.get('frontier_rule') or {}).get('rule_name')}`",
                f"- Reference rule: `{lane.get('reference_rule')}`",
                f"- Frontier selected: `{frontier_summary.get('entries')}/{lane.get('future_denominator')}`, net `{frontier_summary.get('net_cents')}c`, coverage `{frontier_summary.get('coverage_pct')}%`",
                f"- Reference selected: `{reference_summary.get('entries')}/{lane.get('future_denominator')}`, net `{reference_summary.get('net_cents')}c`, coverage `{reference_summary.get('coverage_pct')}%`",
                f"- Gained rows: `{gained_summary.get('entries')}`, net `{gained_summary.get('net_cents')}c`, tags `{lane.get('gained_mechanism_tag_counts')}`",
                f"- Omitted rows: `{omitted_summary.get('entries')}`, net `{omitted_summary.get('net_cents')}c`, fail reasons `{lane.get('omitted_fail_reason_counts')}`",
                f"- Omitted mechanism tags: `{lane.get('omitted_mechanism_tag_counts')}`",
                "",
                "### Gained Rows",
                "",
            ]
        )
        write_rows(lines, lane.get("gained_rows") or [])
        lines.extend(["", "### Omitted Rows", ""])
        write_rows(lines, lane.get("omitted_rows") or [])
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    report = build_report()
    write_report(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
