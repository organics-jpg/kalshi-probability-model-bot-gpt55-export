"""Frozen clean-broad frontier watch for boundary-clock feature gates.

Research-only; no live bot changes or orders.

The coverage/source frontier found a softer observable rule that currently
clears coverage, source share, net, and full-loss cushion in a tiny post-freeze
sample. This probe freezes that rule from its own timestamp so future rows can
test it without reusing the discovery window as promotion evidence.
"""
from __future__ import annotations

import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from probe_v28_boundary_clock_feature_gate_candidate import (
    as_float,
    best_per_market,
    blockers,
    load_or_create_state as load_parent_state,
    market,
    net,
    reconstructed_share,
    source,
)
from probe_v28_boundary_clock_feature_gate_coverage_source_frontier import passes_rule
from probe_v28_coverage_repair_pool_diagnostic import raw_edge, summarize
from probe_v28_frozen_boundary_clock_fv_entry_bridge import future_surfaces as bridge_surfaces
from probe_v28_frozen_boundary_clock_repair_entry import future_surfaces as entry_surfaces


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
STATE_JSON = OUT_DIR / "v28_boundary_clock_feature_gate_clean_broad_frontier_watch_state.json"
OUT_JSON = OUT_DIR / "v28_boundary_clock_feature_gate_clean_broad_frontier_watch_latest.json"
OUT_MD = OUT_DIR / "v28_boundary_clock_feature_gate_clean_broad_frontier_watch_latest.md"
FRONTIER_JSON = OUT_DIR / "v28_boundary_clock_feature_gate_coverage_source_frontier_latest.json"

RULE = {
    "raw_edge_min": 0.03,
    "recross_max": 0.50,
    "abs_d_min": 0.50,
    "ask_min": 0.35,
}
RULE_NAME = "raw03_recross50_abs50_ask35"


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


def load_or_create_state() -> dict[str, Any]:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    if STATE_JSON.exists():
        state = load_json(STATE_JSON)
        if state.get("freeze_ts_utc"):
            return state
    parent = load_parent_state()
    state = {
        "freeze_ts_utc": utc_now_iso(),
        "candidate_family": "boundary_clock_feature_gate_clean_broad_frontier_watch",
        "candidate": RULE_NAME,
        "rule": RULE,
        "parent_feature_gate_freeze_ts_utc": parent.get("freeze_ts_utc"),
        "origin": (
            "Frozen after the coverage/source frontier surfaced a clean broad positive "
            "observable rule. Parent-window rows are diagnostic only; only rows after "
            "this freeze count as strict evidence."
        ),
        "research_only": True,
    }
    STATE_JSON.write_text(json.dumps(state, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return state


def source_counts(rows: list[dict[str, Any]]) -> dict[str, int]:
    return dict(Counter(source(row) for row in rows))


def selected_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return best_per_market([row for row in rows if passes_rule(row, RULE)])


def evaluate_lane(label: str, freeze_ts: str, surfaces_fn: Any) -> dict[str, Any]:
    rows, _, denominator = surfaces_fn(freeze_ts)
    selected = selected_rows(rows)
    summary = summarize(selected, int(denominator or 0))
    counts = source_counts(selected)
    share = reconstructed_share(counts)
    pending_unsettled = [
        row for row in selected
        if row.get("side_won") is None
        or str(row.get("status") or "").lower() == "active"
        or str(row.get("result") or "") == ""
    ]
    return {
        "lane": label,
        "freeze_ts_utc": freeze_ts,
        "future_denominator": int(denominator or 0),
        "candidate": f"{label}_{RULE_NAME}",
        "rule": RULE,
        "candidate_summary": summary,
        "source_counts": counts,
        "reconstructed_share": share,
        "full_loss_cushion_estimate": int(max(0.0, float(summary.get("net_cents") or 0.0)) // 100.0),
        "pending_unsettled_rows": len(pending_unsettled),
        "blockers": blockers(summary, share),
        "rows": [
            {
                "market": market(row),
                "source": source(row),
                "side": row.get("side"),
                "side_won": row.get("side_won"),
                "status": row.get("status"),
                "result": row.get("result"),
                "ts_wall": row.get("ts_wall"),
                "seconds_to_close": row.get("seconds_to_close"),
                "market_observation_index": row.get("market_observation_index"),
                "market_side_observation_index": row.get("market_side_observation_index"),
                "net_cents": net(row),
                "gross_cents": row.get("gross_cents"),
                "hold_gross_cents": row.get("hold_gross_cents"),
                "raw_edge": raw_edge(row),
                "recross_hazard_score": row.get("recross_hazard_score"),
                "abs_d_sigma": row.get("abs_d_sigma"),
                "ask_prob": row.get("ask_prob"),
            }
            for row in selected
        ],
    }


def diagnostic_lane_from_frontier(label: str) -> dict[str, Any]:
    frontier = load_json(FRONTIER_JSON)
    source_lane = next(
        (
            lane for lane in frontier.get("lanes") or []
            if isinstance(lane, dict) and lane.get("lane") == label
        ),
        {},
    )
    candidates = [
        row for row in source_lane.get("clean_broad_positive") or []
        if isinstance(row, dict) and row.get("rule") == RULE_NAME
    ]
    if not candidates:
        candidates = [
            row for row in source_lane.get("pareto_frontier") or []
            if isinstance(row, dict) and row.get("rule") == RULE_NAME
        ]
    row = candidates[0] if candidates else {}
    summary = row.get("summary") if isinstance(row.get("summary"), dict) else {}
    counts = row.get("source_counts") if isinstance(row.get("source_counts"), dict) else {}
    return {
        "lane": f"diagnostic_parent_{label.removeprefix('post_feature_freeze_')}",
        "freeze_ts_utc": frontier.get("freeze_ts_utc"),
        "future_denominator": source_lane.get("future_denominator"),
        "candidate": f"diagnostic_parent_{label.removeprefix('post_feature_freeze_')}_{RULE_NAME}",
        "rule": RULE,
        "candidate_summary": summary,
        "source_counts": counts,
        "reconstructed_share": row.get("reconstructed_share"),
        "full_loss_cushion_estimate": row.get("full_loss_cushion_estimate"),
        "blockers": row.get("blockers") or ["frontier_rule_not_available"],
        "rows": [],
        "diagnostic_source_path": str(FRONTIER_JSON),
    }


def build_report() -> dict[str, Any]:
    state = load_or_create_state()
    watch_freeze = str(state["freeze_ts_utc"])
    lanes = [
        diagnostic_lane_from_frontier("post_feature_freeze_entry"),
        diagnostic_lane_from_frontier("post_feature_freeze_bridge"),
        evaluate_lane("post_clean_broad_freeze_entry", watch_freeze, entry_surfaces),
        evaluate_lane("post_clean_broad_freeze_bridge", watch_freeze, bridge_surfaces),
    ]
    report = {
        "generated_at_utc": utc_now_iso(),
        "state": state,
        "purpose": "Strict-forward watch for the clean broad feature-gate frontier rule.",
        "lanes": lanes,
    }
    report["interpretation"] = interpretation(report)
    return report


def interpretation(report: dict[str, Any]) -> list[str]:
    notes = [
        "This is a frozen watch-only branch; no live logic changes or orders.",
        "The rule uses observable features only. Source labels are audit-only.",
    ]
    for lane in report.get("lanes") or []:
        summary = lane.get("candidate_summary") or {}
        notes.append(
            f"{lane.get('lane')}: {summary.get('entries')}/{lane.get('future_denominator')} entries, "
            f"{summary.get('settled')} settled, coverage {summary.get('coverage_pct')}%, "
            f"net {summary.get('net_cents')}c, W/L {summary.get('wins')}/{summary.get('losses')}, "
            f"recon {lane.get('reconstructed_share')}, pending unsettled {lane.get('pending_unsettled_rows') or 0}, "
            f"blockers {lane.get('blockers')}."
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
    state = report.get("state") or {}
    lines = [
        "# v28 Boundary-Clock Feature-Gate Clean Broad Frontier Watch",
        "",
        "Research-only; frozen watch, no live logic changes.",
        "",
        f"- Generated UTC: `{report.get('generated_at_utc')}`",
        f"- Watch freeze UTC: `{state.get('freeze_ts_utc')}`",
        f"- Parent feature-gate freeze UTC: `{state.get('parent_feature_gate_freeze_ts_utc')}`",
        f"- Rule: `{RULE_NAME}` / `{RULE}`",
        "",
        "## Interpretation",
        "",
    ]
    lines.extend(f"- {note}" for note in report.get("interpretation") or [])
    lines.extend([
        "",
        "## Lanes",
        "",
        "| lane | entries/den | settled | pending | W/L | coverage | net c | recon | source counts | cushion | blockers |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---|---:|---|",
    ])
    for lane in report.get("lanes") or []:
        summary = lane.get("candidate_summary") or {}
        lines.append(
            f"| {lane.get('lane')} | {summary.get('entries')}/{lane.get('future_denominator')} | "
            f"{summary.get('settled')} | {lane.get('pending_unsettled_rows') or 0} | "
            f"{summary.get('wins')}/{summary.get('losses')} | "
            f"{fmt(summary.get('coverage_pct'))} | {fmt(summary.get('net_cents'))} | "
            f"{fmt(lane.get('reconstructed_share'))} | {lane.get('source_counts')} | "
            f"{lane.get('full_loss_cushion_estimate')} | {', '.join(lane.get('blockers') or []) or 'none'} |"
        )
    lines.extend([
        "",
        "## Strict Rows",
        "",
        "| lane | market | ts | status | result | side | won | stc | obs | net c | gross c | raw edge | ask | abs d | recross | source |",
        "|---|---|---|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---|",
    ])
    for lane in report.get("lanes") or []:
        if not str(lane.get("lane") or "").startswith("post_clean_broad_freeze"):
            continue
        for row in lane.get("rows") or []:
            obs = row.get("market_observation_index")
            side_obs = row.get("market_side_observation_index")
            obs_text = f"{obs}/{side_obs}"
            lines.append(
                f"| {lane.get('lane')} | {row.get('market')} | {row.get('ts_wall')} | "
                f"{row.get('status')} | {row.get('result')} | {row.get('side')} | {row.get('side_won')} | "
                f"{fmt(row.get('seconds_to_close'))} | {obs_text} | {fmt(row.get('net_cents'))} | "
                f"{fmt(row.get('gross_cents'))} | {fmt(row.get('raw_edge'))} | {fmt(row.get('ask_prob'))} | "
                f"{fmt(row.get('abs_d_sigma'))} | {fmt(row.get('recross_hazard_score'))} | {row.get('source')} |"
            )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    report = build_report()
    write_md(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
