"""Ask-floor mechanism audit for the frozen boundary-clock feature gate.

Research-only; no live bot changes or orders.

This does not search thresholds. It compares the already-frozen
raw05/recross60/abs085 rule to its already-frozen ask>=0.65 variant and
describes which rows the ask floor keeps or omits.
"""
from __future__ import annotations

import json
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from statistics import mean
from typing import Any

from probe_v28_boundary_clock_feature_gate_candidate import (
    BRIDGE_STATE_JSON,
    ENTRY_STATE_JSON,
    STATE_JSON,
    as_float,
    best_per_market,
    load_json,
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
OUT_JSON = OUT_DIR / "v28_boundary_clock_feature_gate_ask_floor_mechanism_latest.json"
OUT_MD = OUT_DIR / "v28_boundary_clock_feature_gate_ask_floor_mechanism_latest.md"

BASE_RULE = {
    "raw_edge_min": 0.05,
    "recross_max": 0.60,
    "abs_d_min": 0.85,
    "ask_min": None,
}
ASK_FLOOR_RULE = {
    "raw_edge_min": 0.05,
    "recross_max": 0.60,
    "abs_d_min": 0.85,
    "ask_min": 0.65,
}


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def as_bool(value: Any) -> bool | None:
    if value is None:
        return None
    if isinstance(value, bool):
        return value
    return bool(value)


def side(row: dict[str, Any]) -> str:
    return str(row.get("side") or "")


def signed_outcome(row: dict[str, Any]) -> str:
    won = as_bool(row.get("side_won"))
    if won is True:
        return "win"
    if won is False:
        return "loss"
    return "unsettled"


def compact_row(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "market": market(row),
        "source": source(row),
        "side": side(row),
        "side_won": row.get("side_won"),
        "outcome": signed_outcome(row),
        "net_cents": net(row),
        "raw_edge": raw_edge(row),
        "recross_hazard_score": recross(row),
        "abs_d_sigma": as_float(row.get("abs_d_sigma")),
        "ask_prob": as_float(row.get("ask_prob")),
    }


def edge_value(row: dict[str, Any]) -> float | None:
    edge = raw_edge(row)
    if edge is not None:
        return edge
    return as_float(row.get("raw_edge"))


def summarize_rows(rows: list[dict[str, Any]], denominator: int) -> dict[str, Any]:
    base = summarize(rows, denominator)
    settled = [row for row in rows if as_bool(row.get("side_won")) is not None]
    fields = {
        "raw_edge": [edge_value(row) for row in rows],
        "recross_hazard_score": [recross(row) for row in rows],
        "abs_d_sigma": [as_float(row.get("abs_d_sigma")) for row in rows],
        "ask_prob": [as_float(row.get("ask_prob")) for row in rows],
    }
    feature_means = {
        key: mean([float(value) for value in values if value is not None])
        for key, values in fields.items()
        if any(value is not None for value in values)
    }
    base.update(
        {
            "rows": len(rows),
            "settled_rows": len(settled),
            "source_counts": dict(Counter(source(row) for row in rows)),
            "side_counts": dict(Counter(side(row) for row in rows)),
            "outcome_counts": dict(Counter(signed_outcome(row) for row in rows)),
            "feature_means": feature_means,
        }
    )
    return base


def selected_by_market(rows: list[dict[str, Any]], rule: dict[str, Any]) -> dict[str, dict[str, Any]]:
    selected = best_per_market([row for row in rows if passes(row, rule)])
    return {market(row): row for row in selected if market(row)}


def row_signature(row: dict[str, Any]) -> tuple[Any, ...]:
    return (
        source(row),
        side(row),
        as_bool(row.get("side_won")),
        round(float(raw_edge(row) or 0.0), 9),
        round(float(recross(row) or 0.0), 9),
        round(float(as_float(row.get("abs_d_sigma")) or 0.0), 9),
        round(float(as_float(row.get("ask_prob")) or 0.0), 9),
    )


def omitted_failure_tags(row: dict[str, Any]) -> list[str]:
    tags: list[str] = []
    ask = as_float(row.get("ask_prob"))
    abs_d = as_float(row.get("abs_d_sigma"))
    edge = raw_edge(row)
    if ask is not None and ask < 0.65:
        tags.append("cheap_touch_or_contrarian_side")
    if abs_d is not None and abs_d < 0.85:
        tags.append("near_strike_boundary_pull")
    if edge is not None and edge >= 0.10:
        tags.append("large_raw_edge_on_cheap_side")
    if source(row) != "approved_entry":
        tags.append("source_quality_risk")
    if signed_outcome(row) == "loss":
        tags.append("realized_loss")
    elif signed_outcome(row) == "unsettled":
        tags.append("unsettled")
    return tags or ["ordinary_omission"]


def evaluate_lane(label: str, freeze_ts: str, surfaces_fn: Any) -> dict[str, Any]:
    all_rows, _, denominator = surfaces_fn(freeze_ts)
    denominator = int(denominator or 0)
    base_by_market = selected_by_market(all_rows, BASE_RULE)
    ask_by_market = selected_by_market(all_rows, ASK_FLOOR_RULE)
    kept = [ask_by_market[key] for key in sorted(ask_by_market)]
    omitted = [base_by_market[key] for key in sorted(set(base_by_market) - set(ask_by_market))]
    switched = []
    for row_market in sorted(set(base_by_market) & set(ask_by_market)):
        base_row = base_by_market[row_market]
        ask_row = ask_by_market[row_market]
        if row_signature(base_row) == row_signature(ask_row):
            continue
        switched.append(
            {
                "market": row_market,
                "base_row": compact_row(base_row) | {"mechanism_tags": omitted_failure_tags(base_row)},
                "ask_floor_row": compact_row(ask_row),
                "delta_net_cents": net(ask_row) - net(base_row),
                "side_changed": side(base_row) != side(ask_row),
                "source_changed": source(base_row) != source(ask_row),
            }
        )
    added = [ask_by_market[key] for key in sorted(set(ask_by_market) - set(base_by_market))]
    omitted_tags = Counter(tag for row in omitted for tag in omitted_failure_tags(row))
    switched_tags = Counter(tag for item in switched for tag in item["base_row"].get("mechanism_tags", []))
    base_summary = summarize_rows(list(base_by_market.values()), denominator)
    ask_summary = summarize_rows(list(ask_by_market.values()), denominator)
    omitted_summary = summarize_rows(omitted, denominator)
    switched_out_summary = summarize_rows([item["base_row"] for item in switched], denominator)
    switched_in_summary = summarize_rows([item["ask_floor_row"] for item in switched], denominator)
    return {
        "lane": label,
        "freeze_ts_utc": freeze_ts,
        "future_denominator": denominator,
        "base_rule": BASE_RULE,
        "ask_floor_rule": ASK_FLOOR_RULE,
        "base_summary": base_summary,
        "ask_floor_summary": ask_summary,
        "delta_net_cents": (as_float(ask_summary.get("net_cents")) or 0.0) - (as_float(base_summary.get("net_cents")) or 0.0),
        "delta_entries": int(ask_summary.get("entries") or 0) - int(base_summary.get("entries") or 0),
        "omitted_summary": omitted_summary,
        "omitted_failure_tag_counts": dict(omitted_tags),
        "switched_out_summary": switched_out_summary,
        "switched_in_summary": switched_in_summary,
        "switched_failure_tag_counts": dict(switched_tags),
        "switched_delta_net_cents": sum(float(item["delta_net_cents"]) for item in switched),
        "kept_examples": [compact_row(row) for row in sorted(kept, key=lambda item: net(item), reverse=False)[:12]],
        "omitted_rows": [compact_row(row) | {"mechanism_tags": omitted_failure_tags(row)} for row in sorted(omitted, key=lambda item: net(item))],
        "switched_rows": sorted(switched, key=lambda item: float(item.get("delta_net_cents") or 0.0), reverse=True),
        "added_rows": [compact_row(row) for row in added],
    }


def build_report() -> dict[str, Any]:
    state = load_json(STATE_JSON)
    entry_state = load_json(ENTRY_STATE_JSON)
    bridge_state = load_json(BRIDGE_STATE_JSON)
    lanes: list[dict[str, Any]] = []
    if entry_state.get("freeze_ts_utc"):
        lanes.append(evaluate_lane("diagnostic_entry", str(entry_state["freeze_ts_utc"]), entry_surfaces))
    if bridge_state.get("freeze_ts_utc"):
        lanes.append(evaluate_lane("diagnostic_bridge", str(bridge_state["freeze_ts_utc"]), bridge_surfaces))
    if state.get("freeze_ts_utc"):
        freeze_ts = str(state["freeze_ts_utc"])
        lanes.append(evaluate_lane("post_feature_freeze_entry", freeze_ts, entry_surfaces))
        lanes.append(evaluate_lane("post_feature_freeze_bridge", freeze_ts, bridge_surfaces))
    report = {
        "generated_at_utc": utc_now_iso(),
        "feature_gate_freeze_ts_utc": state.get("freeze_ts_utc"),
        "interpretation": interpretation(lanes),
        "lanes": lanes,
    }
    return report


def interpretation(lanes: list[dict[str, Any]]) -> list[str]:
    notes = [
        "This is a mechanism audit of the already-frozen ask>=0.65 variant; it does not search or propose a new threshold.",
    ]
    for lane in lanes:
        ask_summary = lane.get("ask_floor_summary") or {}
        omitted_summary = lane.get("omitted_summary") or {}
        switched_out = lane.get("switched_out_summary") or {}
        switched_in = lane.get("switched_in_summary") or {}
        notes.append(
            f"{lane.get('lane')}: ask floor changes net by {lane.get('delta_net_cents')}c with "
            f"entry delta {lane.get('delta_entries')}; omitted rows net {omitted_summary.get('net_cents')}c "
            f"and tags {lane.get('omitted_failure_tag_counts')}; same-market switched base/ask rows net "
            f"{switched_out.get('net_cents')}c/{switched_in.get('net_cents')}c with tags "
            f"{lane.get('switched_failure_tag_counts')}; ask-floor selected coverage {ask_summary.get('coverage_pct')}%."
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
        "# v28 Boundary-Clock Feature-Gate Ask-Floor Mechanism",
        "",
        "Research-only; no live bot changes or orders.",
        "",
        f"- Generated UTC: `{report.get('generated_at_utc')}`",
        f"- Feature-gate freeze UTC: `{report.get('feature_gate_freeze_ts_utc')}`",
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
                "| slice | entries | settled | W/L | coverage | net c | sources | sides | feature means |",
                "|---|---:|---:|---:|---:|---:|---|---|---|",
            ]
        )
        for label, key in [
            ("base_raw05_recross60_abs085", "base_summary"),
            ("ask_floor_raw05_recross60_abs085_ask65", "ask_floor_summary"),
            ("omitted_by_ask_floor", "omitted_summary"),
            ("switched_out_base_rows", "switched_out_summary"),
            ("switched_in_ask_floor_rows", "switched_in_summary"),
        ]:
            summary = lane.get(key) or {}
            lines.append(
                f"| {label} | {summary.get('entries')} | {summary.get('settled')} | "
                f"{summary.get('wins')}/{summary.get('losses')} | {fmt(summary.get('coverage_pct'))} | "
                f"{fmt(summary.get('net_cents'))} | {summary.get('source_counts')} | "
                f"{summary.get('side_counts')} | {summary.get('feature_means')} |"
            )
        lines.extend(["", "### Omitted By Ask Floor", ""])
        lines.extend(
            [
                "| market | source | side | outcome | net c | edge | recross | abs d | ask | tags |",
                "|---|---|---|---|---:|---:|---:|---:|---:|---|",
            ]
        )
        omitted = lane.get("omitted_rows") or []
        if omitted:
            for row in omitted:
                lines.append(
                    f"| {row.get('market')} | {row.get('source')} | {row.get('side')} | {row.get('outcome')} | "
                    f"{fmt(row.get('net_cents'))} | {fmt(row.get('raw_edge'))} | "
                    f"{fmt(row.get('recross_hazard_score'))} | {fmt(row.get('abs_d_sigma'))} | "
                    f"{fmt(row.get('ask_prob'))} | {', '.join(row.get('mechanism_tags') or [])} |"
                )
        else:
            lines.append("| none |  |  |  |  |  |  |  |  |  |")
        lines.extend(["", "### Same-Market Switches", ""])
        lines.extend(
            [
                "| market | base source | base side | base outcome | base net c | base edge | base ask | ask source | ask side | ask outcome | ask net c | ask edge | ask ask | delta c | tags |",
                "|---|---|---|---|---:|---:|---:|---|---|---|---:|---:|---:|---:|---|",
            ]
        )
        switched = lane.get("switched_rows") or []
        if switched:
            for item in switched:
                base = item.get("base_row") or {}
                ask = item.get("ask_floor_row") or {}
                tags = ", ".join(base.get("mechanism_tags") or []) or "none"
                lines.append(
                    f"| {item.get('market')} | {base.get('source')} | {base.get('side')} | {base.get('outcome')} | "
                    f"{fmt(base.get('net_cents'))} | {fmt(base.get('raw_edge'))} | {fmt(base.get('ask_prob'))} | "
                    f"{ask.get('source')} | {ask.get('side')} | {ask.get('outcome')} | {fmt(ask.get('net_cents'))} | "
                    f"{fmt(ask.get('raw_edge'))} | {fmt(ask.get('ask_prob'))} | {fmt(item.get('delta_net_cents'))} | {tags} |"
                )
        else:
            lines.append("| none |  |  |  |  |  |  |  |  |  |  |  |  |  |  |")
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    report = build_report()
    write_md(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
