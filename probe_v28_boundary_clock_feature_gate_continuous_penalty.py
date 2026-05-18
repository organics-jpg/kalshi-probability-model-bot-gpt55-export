"""Continuous cheap-side penalty for the boundary-clock feature gate.

Research-only; no live bot changes or orders.

This starts a new frozen watch lane derived from the ask-floor mechanism audit.
It does not replace the live bot. Rows before this probe's birth timestamp are
diagnostic only; promotion evidence must come from post-penalty-birth rows.
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
STATE_JSON = OUT_DIR / "v28_boundary_clock_feature_gate_continuous_penalty_state.json"
OUT_JSON = OUT_DIR / "v28_boundary_clock_feature_gate_continuous_penalty_latest.json"
OUT_MD = OUT_DIR / "v28_boundary_clock_feature_gate_continuous_penalty_latest.md"

MIN_SETTLED = 30
MAX_RECONSTRUCTED_SHARE = 0.35
MIN_FULL_LOSS_CUSHION = 3

BASE_RULE = {
    "raw_edge_min": 0.05,
    "recross_max": 0.60,
    "abs_d_min": 0.85,
}

PENALTIES = {
    "cheap_penalty025_rank_only": {"lambda": 0.25, "adjusted_edge_min": None},
    "cheap_penalty050_rank_only": {"lambda": 0.50, "adjusted_edge_min": None},
    "cheap_penalty100_rank_only": {"lambda": 1.00, "adjusted_edge_min": None},
    "cheap_penalty050_floor05": {"lambda": 0.50, "adjusted_edge_min": 0.05},
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
        "candidate_family": "boundary_clock_feature_gate_continuous_cheap_side_penalty",
        "origin": "Derived after ask-floor mechanism audit; earlier rows are diagnostic only.",
        "base_rule": BASE_RULE,
        "penalties": PENALTIES,
    }
    STATE_JSON.write_text(json.dumps(state, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return state


def eligible(row: dict[str, Any]) -> bool:
    edge = raw_edge(row)
    row_recross = recross(row)
    abs_d = as_float(row.get("abs_d_sigma"))
    if edge is None or row_recross is None or abs_d is None:
        return False
    return (
        edge >= BASE_RULE["raw_edge_min"]
        and row_recross <= BASE_RULE["recross_max"]
        and abs_d >= BASE_RULE["abs_d_min"]
    )


def cheap_gap(row: dict[str, Any]) -> float:
    ask = as_float(row.get("ask_prob"))
    if ask is None:
        return 0.0
    return max(0.0, 0.65 - ask)


def adjusted_edge(row: dict[str, Any], penalty: dict[str, Any]) -> float | None:
    edge = raw_edge(row)
    if edge is None:
        return None
    return edge - float(penalty["lambda"]) * cheap_gap(row)


def selected_rows(rows: list[dict[str, Any]], penalty: dict[str, Any]) -> list[dict[str, Any]]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        if eligible(row) and market(row):
            adjusted = adjusted_edge(row, penalty)
            floor = penalty.get("adjusted_edge_min")
            if adjusted is not None and (floor is None or adjusted >= float(floor)):
                grouped[market(row)].append(row)
    return [
        max(items, key=lambda row: adjusted_edge(row, penalty) if adjusted_edge(row, penalty) is not None else -999.0)
        for items in grouped.values()
    ]


def source_counts(rows: list[dict[str, Any]]) -> dict[str, int]:
    return dict(Counter(source(row) for row in rows))


def blockers(summary: dict[str, Any], share: float | None) -> list[str]:
    out = []
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


def compact_row(row: dict[str, Any], penalty: dict[str, Any]) -> dict[str, Any]:
    return {
        "market": market(row),
        "source": source(row),
        "side": row.get("side"),
        "side_won": row.get("side_won"),
        "net_cents": net(row),
        "raw_edge": raw_edge(row),
        "cheap_gap": cheap_gap(row),
        "adjusted_edge": adjusted_edge(row, penalty),
        "recross_hazard_score": recross(row),
        "abs_d_sigma": as_float(row.get("abs_d_sigma")),
        "ask_prob": as_float(row.get("ask_prob")),
    }


def evaluate_lane(label: str, freeze_ts: str, surfaces_fn: Any) -> dict[str, Any]:
    all_rows, _, denominator = surfaces_fn(freeze_ts)
    variants = []
    for name, penalty in PENALTIES.items():
        selected = selected_rows(all_rows, penalty)
        summary = summarize(selected, denominator)
        counts = source_counts(selected)
        share = reconstructed_share(counts)
        variants.append(
            {
                "candidate": f"{label}_{name}",
                "penalty": penalty,
                "candidate_summary": summary,
                "source_counts": counts,
                "reconstructed_share": share,
                "full_loss_cushion_estimate": int(max(0.0, float(summary.get("net_cents") or 0.0)) // 100.0),
                "blockers": blockers(summary, share),
                "rows": [compact_row(row, penalty) for row in sorted(selected, key=lambda item: net(item))],
            }
        )
    variants.sort(
        key=lambda row: (
            len(row.get("blockers") or []),
            -float((row.get("candidate_summary") or {}).get("net_cents") or -999999.0),
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
        lanes.append(evaluate_lane("pre_penalty_birth_feature_entry", str(feature_state["freeze_ts_utc"]), entry_surfaces))
        lanes.append(evaluate_lane("pre_penalty_birth_feature_bridge", str(feature_state["freeze_ts_utc"]), bridge_surfaces))
    lanes.append(evaluate_lane("post_penalty_birth_entry", str(state["freeze_ts_utc"]), entry_surfaces))
    lanes.append(evaluate_lane("post_penalty_birth_bridge", str(state["freeze_ts_utc"]), bridge_surfaces))
    report = {
        "generated_at_utc": utc_now_iso(),
        "state": state,
        "interpretation": interpretation(lanes),
        "lanes": lanes,
    }
    return report


def interpretation(lanes: list[dict[str, Any]]) -> list[str]:
    notes = [
        "Continuous penalties rank eligible rows by raw_edge minus lambda times cheap-side gap max(0, 0.65 - ask_prob).",
        "Only post_penalty_birth lanes are strict forward evidence for this new challenger.",
    ]
    for lane in lanes:
        best = (lane.get("variants") or [{}])[0]
        summary = best.get("candidate_summary") or {}
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


def write_md(report: dict[str, Any]) -> None:
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8")
    lines = [
        "# v28 Boundary-Clock Feature-Gate Continuous Penalty",
        "",
        "Research-only; no live bot changes or orders.",
        "",
        f"- Generated UTC: `{report.get('generated_at_utc')}`",
        f"- Penalty freeze UTC: `{(report.get('state') or {}).get('freeze_ts_utc')}`",
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
                "| rank | candidate | settled/den | W/L | coverage | net c | recon | cushion | blockers |",
                "|---:|---|---:|---:|---:|---:|---:|---:|---|",
            ]
        )
        for idx, row in enumerate(lane.get("variants") or [], start=1):
            summary = row.get("candidate_summary") or {}
            blockers_text = ", ".join(str(item) for item in row.get("blockers") or []) or "none"
            lines.append(
                f"| {idx} | {row.get('candidate')} | {summary.get('settled')}/{lane.get('future_denominator')} | "
                f"{summary.get('wins')}/{summary.get('losses')} | {fmt(summary.get('coverage_pct'))} | "
                f"{fmt(summary.get('net_cents'))} | {fmt(row.get('reconstructed_share'))} | "
                f"{row.get('full_loss_cushion_estimate')} | {blockers_text} |"
            )
        best = (lane.get("variants") or [{}])[0]
        lines.extend(["", "### Best-Lane Worst Rows", ""])
        lines.extend(
            [
                "| market | source | side | won | net c | raw edge | cheap gap | adjusted edge | recross | abs d | ask |",
                "|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|",
            ]
        )
        for row in (best.get("rows") or [])[:10]:
            lines.append(
                f"| {row.get('market')} | {row.get('source')} | {row.get('side')} | {row.get('side_won')} | "
                f"{fmt(row.get('net_cents'))} | {fmt(row.get('raw_edge'))} | {fmt(row.get('cheap_gap'))} | "
                f"{fmt(row.get('adjusted_edge'))} | {fmt(row.get('recross_hazard_score'))} | "
                f"{fmt(row.get('abs_d_sigma'))} | {fmt(row.get('ask_prob'))} |"
            )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    report = build_report()
    write_md(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
