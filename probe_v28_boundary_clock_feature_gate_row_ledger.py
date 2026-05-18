"""Row ledger for the frozen boundary-clock feature-gate candidate.

Research-only; no live bot changes or orders.

This explains post-freeze feature-gate coverage by reporting which observable
rule each available row passes and why available rows are omitted.
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
    recross,
    source,
)
from probe_v28_coverage_repair_pool_diagnostic import raw_edge, summarize
from probe_v28_frozen_boundary_clock_fv_entry_bridge import future_surfaces as bridge_surfaces
from probe_v28_frozen_boundary_clock_repair_entry import future_surfaces as entry_surfaces


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
OUT_JSON = OUT_DIR / "v28_boundary_clock_feature_gate_row_ledger_latest.json"
OUT_MD = OUT_DIR / "v28_boundary_clock_feature_gate_row_ledger_latest.md"


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


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
    return reasons


def row_digest(row: dict[str, Any], rule: dict[str, Any], selected: bool) -> dict[str, Any]:
    return {
        "market": market(row),
        "source": source(row),
        "side": row.get("side"),
        "side_won": row.get("side_won"),
        "net_cents": net(row),
        "raw_edge": raw_edge(row),
        "recross_hazard_score": recross(row),
        "abs_d_sigma": as_float(row.get("abs_d_sigma")),
        "ask_prob": as_float(row.get("ask_prob")),
        "selected": selected,
        "fail_reasons": [] if selected else fail_reasons(row, rule),
    }


def evaluate_rule(lane: str, all_rows: list[dict[str, Any]], denominator: int, rule_name: str, rule: dict[str, Any]) -> dict[str, Any]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in all_rows:
        row_market = market(row)
        if row_market:
            grouped[row_market].append(row)

    selected = best_per_market([row for row in all_rows if passes(row, rule)])
    selected_markets = {market(row) for row in selected}
    omitted_representatives: list[dict[str, Any]] = []
    reason_counts: Counter[str] = Counter()
    for row_market, rows in grouped.items():
        if row_market in selected_markets:
            continue
        representative = max(rows, key=lambda item: raw_edge(item) or -999.0)
        reasons = fail_reasons(representative, rule)
        reason_counts.update(reasons or ["unknown"])
        omitted_representatives.append(representative)

    omitted_representatives.sort(key=lambda row: raw_edge(row) or -999.0, reverse=True)
    selected_sorted = sorted(selected, key=lambda row: raw_edge(row) or -999.0, reverse=True)
    summary = summarize(selected, denominator)
    observed_markets = len(grouped)
    unobserved = max(0, denominator - observed_markets)
    if unobserved:
        reason_counts.update({"unobserved_denominator_market": unobserved})

    return {
        "lane": lane,
        "rule": rule_name,
        "future_denominator": denominator,
        "observed_markets": observed_markets,
        "unobserved_denominator_markets": unobserved,
        "summary": summary,
        "omission_reason_counts": dict(reason_counts),
        "selected_rows": [row_digest(row, rule, True) for row in selected_sorted],
        "omitted_examples": [row_digest(row, rule, False) for row in omitted_representatives[:12]],
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
        "This ledger uses only observable gate features for pass/fail reasons; source labels are shown only for evidence-quality audit.",
    ]
    for lane in report.get("lanes") or []:
        rules = lane.get("rules") or []
        if not rules:
            continue
        best = rules[0]
        summary = best.get("summary") or {}
        reasons = best.get("omission_reason_counts") or {}
        notes.append(
            f"{lane.get('lane')} best current rule {best.get('rule')} selects {summary.get('entries')} of "
            f"{best.get('future_denominator')} denominator markets, net {summary.get('net_cents')}c, "
            f"with omission reasons {reasons}."
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
        "# v28 Boundary-Clock Feature-Gate Row Ledger",
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
                "| rule | selected/den | settled | W/L | coverage | net c | observed markets | unobserved | omission reasons |",
                "|---|---:|---:|---:|---:|---:|---:|---:|---|",
            ]
        )
        for row in lane.get("rules") or []:
            summary = row.get("summary") or {}
            reasons = ", ".join(f"{key}:{value}" for key, value in (row.get("omission_reason_counts") or {}).items()) or "none"
            lines.append(
                f"| {row.get('rule')} | {summary.get('entries')}/{row.get('future_denominator')} | "
                f"{summary.get('settled')} | {summary.get('wins')}/{summary.get('losses')} | "
                f"{fmt(summary.get('coverage_pct'))} | {fmt(summary.get('net_cents'))} | "
                f"{row.get('observed_markets')} | {row.get('unobserved_denominator_markets')} | {reasons} |"
            )
        lines.extend(["", "### Omitted Examples", ""])
        lines.extend(
            [
                "| rule | market | source | side | net c | edge | recross | abs d | ask | fail reasons |",
                "|---|---|---|---|---:|---:|---:|---:|---:|---|",
            ]
        )
        for row in lane.get("rules") or []:
            for example in row.get("omitted_examples") or []:
                reasons = ", ".join(example.get("fail_reasons") or []) or "none"
                lines.append(
                    f"| {row.get('rule')} | {example.get('market')} | {example.get('source')} | {example.get('side')} | "
                    f"{fmt(example.get('net_cents'))} | {fmt(example.get('raw_edge'))} | "
                    f"{fmt(example.get('recross_hazard_score'))} | {fmt(example.get('abs_d_sigma'))} | "
                    f"{fmt(example.get('ask_prob'))} | {reasons} |"
                )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    report = build_report()
    write_md(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
