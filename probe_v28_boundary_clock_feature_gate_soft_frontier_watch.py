"""Forward watch for the boundary-clock soft-frontier mechanism.

Research-only; no live bot changes or orders.

The coverage/source frontier audit found a soft observable rule that improves
the current tiny post-freeze sample but still fails coverage/readiness. This
probe freezes that mechanism from its own birth timestamp so future rows can
test it without letting the discovery rows count as promotion evidence.
"""
from __future__ import annotations

import json
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from probe_v28_boundary_clock_feature_gate_candidate import (
    BRIDGE_STATE_JSON,
    ENTRY_STATE_JSON,
    STATE_JSON as FEATURE_STATE_JSON,
    as_float,
    load_json,
    market,
    net,
    recross,
    reconstructed_share,
    source,
)
from probe_v28_coverage_repair_pool_diagnostic import COVERAGE_FLOOR, raw_edge, summarize
from probe_v28_frozen_boundary_clock_fv_entry_bridge import future_surfaces as bridge_surfaces
from probe_v28_frozen_boundary_clock_repair_entry import future_surfaces as entry_surfaces


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
STATE_JSON = OUT_DIR / "v28_boundary_clock_feature_gate_soft_frontier_watch_state.json"
OUT_JSON = OUT_DIR / "v28_boundary_clock_feature_gate_soft_frontier_watch_latest.json"
OUT_MD = OUT_DIR / "v28_boundary_clock_feature_gate_soft_frontier_watch_latest.md"

MIN_SETTLED = 30
MAX_RECONSTRUCTED_SHARE = 0.35
MIN_FULL_LOSS_CUSHION = 3

SOFT_RULES = {
    "soft_raw03_recross50_abs50_ask35": {
        "raw_edge_min": 0.03,
        "recross_max": 0.50,
        "abs_d_min": 0.50,
        "ask_min": 0.35,
        "mechanism": "Admit mid-priced boundary rows while excluding cheap-tail very-near-strike failures.",
    },
    "soft_raw03_recross50_abs65_ask35": {
        "raw_edge_min": 0.03,
        "recross_max": 0.50,
        "abs_d_min": 0.65,
        "ask_min": 0.35,
        "mechanism": "Stricter distance version of the soft boundary rule.",
    },
    "soft_raw03_recross50_abs50_ask50": {
        "raw_edge_min": 0.03,
        "recross_max": 0.50,
        "abs_d_min": 0.50,
        "ask_min": 0.50,
        "mechanism": "Stricter price floor version of the soft boundary rule.",
    },
}


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def load_or_create_state() -> dict[str, Any]:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    if STATE_JSON.exists():
        state = load_json(STATE_JSON)
        if state.get("freeze_ts_utc"):
            return state
    state = {
        "freeze_ts_utc": utc_now_iso(),
        "candidate_family": "boundary_clock_feature_gate_soft_frontier_watch",
        "origin": "Derived from coverage/source frontier and frontier-mechanism audits; prior rows are diagnostic only.",
        "rules": SOFT_RULES,
        "strict_forward_note": "Only post_soft_frontier_birth lanes can count as forward evidence.",
    }
    STATE_JSON.write_text(json.dumps(state, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return state


def passes(row: dict[str, Any], rule: dict[str, Any]) -> bool:
    edge = raw_edge(row)
    row_recross = recross(row)
    abs_d = as_float(row.get("abs_d_sigma"))
    ask = as_float(row.get("ask_prob"))
    if edge is None or row_recross is None or abs_d is None or ask is None:
        return False
    return (
        edge >= float(rule["raw_edge_min"])
        and row_recross <= float(rule["recross_max"])
        and abs_d >= float(rule["abs_d_min"])
        and ask >= float(rule["ask_min"])
    )


def selected_rows(rows: list[dict[str, Any]], rule: dict[str, Any]) -> list[dict[str, Any]]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        if market(row) and passes(row, rule):
            grouped[market(row)].append(row)
    return [max(items, key=lambda row: raw_edge(row) or -999.0) for items in grouped.values()]


def source_counts(rows: list[dict[str, Any]]) -> dict[str, int]:
    return dict(Counter(source(row) for row in rows))


def blockers(summary: dict[str, Any], share: float | None) -> list[str]:
    out: list[str] = []
    settled = int(as_float(summary.get("settled")) or 0)
    coverage = as_float(summary.get("coverage_pct"))
    net_cents = as_float(summary.get("net_cents"))
    if settled < MIN_SETTLED:
        out.append("settled_lt_30")
    if coverage is None or coverage < COVERAGE_FLOOR:
        out.append("coverage_too_low")
    if net_cents is None or net_cents <= 0:
        out.append("net_not_positive")
    if share is not None and share > MAX_RECONSTRUCTED_SHARE:
        out.append("reconstructed_share_gt_35pct")
    if int(max(0.0, float(net_cents or 0.0)) // 100.0) < MIN_FULL_LOSS_CUSHION:
        out.append("full_loss_cushion_lt_3")
    return out


def mechanism_tags(row: dict[str, Any]) -> list[str]:
    tags: list[str] = []
    ask = as_float(row.get("ask_prob"))
    abs_d = as_float(row.get("abs_d_sigma"))
    edge = raw_edge(row)
    if source(row) != "approved_entry":
        tags.append("source_quality_risk")
    if row.get("side_won") is False:
        tags.append("realized_loss")
    if net(row) <= 5.0:
        tags.append("thin_or_negative_net")
    if edge is not None and edge < 0.05:
        tags.append("thin_raw_edge")
    if abs_d is not None and abs_d < 0.65:
        tags.append("near_strike_boundary_pull")
    if ask is not None and ask < 0.50:
        tags.append("mid_cheap_touch")
    return tags or ["clean_or_unclassified"]


def compact_row(row: dict[str, Any]) -> dict[str, Any]:
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
        "mechanism_tags": mechanism_tags(row),
    }


def evaluate_lane(label: str, freeze_ts: str, surfaces_fn: Any) -> dict[str, Any]:
    all_rows, _, denominator = surfaces_fn(freeze_ts)
    variants = []
    for name, rule in SOFT_RULES.items():
        selected = selected_rows(all_rows, rule)
        summary = summarize(selected, denominator)
        counts = source_counts(selected)
        share = reconstructed_share(counts)
        tag_counts = dict(Counter(tag for row in selected for tag in mechanism_tags(row)))
        variants.append(
            {
                "candidate": f"{label}_{name}",
                "rule": rule,
                "candidate_summary": summary,
                "source_counts": counts,
                "reconstructed_share": share,
                "full_loss_cushion_estimate": int(max(0.0, float(summary.get("net_cents") or 0.0)) // 100.0),
                "mechanism_tag_counts": tag_counts,
                "blockers": blockers(summary, share),
                "rows": [compact_row(row) for row in sorted(selected, key=lambda row: net(row))],
            }
        )
    variants.sort(
        key=lambda row: (
            len(row.get("blockers") or []),
            -float((row.get("candidate_summary") or {}).get("net_cents") or -999999.0),
            -float((row.get("candidate_summary") or {}).get("coverage_pct") or 0.0),
        )
    )
    return {
        "lane": label,
        "freeze_ts_utc": freeze_ts,
        "future_denominator": denominator,
        "variants": variants,
    }


def build_report() -> dict[str, Any]:
    state = load_or_create_state()
    feature_state = load_json(FEATURE_STATE_JSON)
    entry_state = load_json(ENTRY_STATE_JSON)
    bridge_state = load_json(BRIDGE_STATE_JSON)
    lanes: list[dict[str, Any]] = []
    if entry_state.get("freeze_ts_utc"):
        lanes.append(evaluate_lane("diagnostic_entry", str(entry_state["freeze_ts_utc"]), entry_surfaces))
    if bridge_state.get("freeze_ts_utc"):
        lanes.append(evaluate_lane("diagnostic_bridge", str(bridge_state["freeze_ts_utc"]), bridge_surfaces))
    if feature_state.get("freeze_ts_utc"):
        lanes.append(evaluate_lane("pre_soft_frontier_birth_entry", str(feature_state["freeze_ts_utc"]), entry_surfaces))
        lanes.append(evaluate_lane("pre_soft_frontier_birth_bridge", str(feature_state["freeze_ts_utc"]), bridge_surfaces))
    lanes.append(evaluate_lane("post_soft_frontier_birth_entry", str(state["freeze_ts_utc"]), entry_surfaces))
    lanes.append(evaluate_lane("post_soft_frontier_birth_bridge", str(state["freeze_ts_utc"]), bridge_surfaces))
    report = {
        "generated_at_utc": utc_now_iso(),
        "state": state,
        "interpretation": interpretation(lanes),
        "lanes": lanes,
    }
    return report


def interpretation(lanes: list[dict[str, Any]]) -> list[str]:
    notes = [
        "Soft-frontier rules are observable-only and exclude cheap-tail very-near-strike failures by ask/distance floors.",
        "Only post_soft_frontier_birth lanes are strict forward evidence for this watch.",
    ]
    for lane in lanes:
        best = (lane.get("variants") or [{}])[0]
        summary = best.get("candidate_summary") or {}
        notes.append(
            f"{lane.get('lane')}: best {best.get('candidate')} settled {summary.get('settled')}, "
            f"coverage {summary.get('coverage_pct')}%, net {summary.get('net_cents')}c, "
            f"recon {best.get('reconstructed_share')}, tags {best.get('mechanism_tag_counts')}, "
            f"blockers {best.get('blockers')}."
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
        "# v28 Boundary-Clock Feature-Gate Soft Frontier Watch",
        "",
        "Research-only; no live bot changes or orders.",
        "",
        f"- Generated UTC: `{report.get('generated_at_utc')}`",
        f"- Soft-frontier freeze UTC: `{(report.get('state') or {}).get('freeze_ts_utc')}`",
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
                "| rank | candidate | settled/den | W/L | coverage | net c | recon | cushion | tags | blockers |",
                "|---:|---|---:|---:|---:|---:|---:|---:|---|---|",
            ]
        )
        for idx, variant in enumerate(lane.get("variants") or [], start=1):
            summary = variant.get("candidate_summary") or {}
            lines.append(
                f"| {idx} | {variant.get('candidate')} | {summary.get('settled')}/{lane.get('future_denominator')} | "
                f"{summary.get('wins')}/{summary.get('losses')} | {fmt(summary.get('coverage_pct'))} | "
                f"{fmt(summary.get('net_cents'))} | {fmt(variant.get('reconstructed_share'))} | "
                f"{variant.get('full_loss_cushion_estimate')} | {variant.get('mechanism_tag_counts')} | "
                f"{', '.join(variant.get('blockers') or []) or 'none'} |"
            )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    report = build_report()
    write_md(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
