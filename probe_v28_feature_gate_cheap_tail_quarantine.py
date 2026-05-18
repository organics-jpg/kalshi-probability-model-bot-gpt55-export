"""Cheap-tail quarantine watch for boundary-clock feature-gate rows.

Research-only; no live bot changes or orders.

The current feature-gate frontier becomes broad only by admitting very cheap
tail rows. Those rows include one large win but are source-quality fragile. This
probe separates clean core rows from cheap-tail rows so tail wins cannot mask
broad-entry readiness.
"""
from __future__ import annotations

import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from probe_v28_boundary_clock_feature_gate_candidate import (
    STATE_JSON as FEATURE_STATE_JSON,
    as_float,
    best_per_market,
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
STATE_JSON = OUT_DIR / "v28_feature_gate_cheap_tail_quarantine_state.json"
OUT_JSON = OUT_DIR / "v28_feature_gate_cheap_tail_quarantine_latest.json"
OUT_MD = OUT_DIR / "v28_feature_gate_cheap_tail_quarantine_latest.md"

MIN_SETTLED = 30
MAX_RECONSTRUCTED_SHARE = 0.35
MIN_FULL_LOSS_CUSHION = 3

CORE_RULES = {
    "core_raw03_recross50_abs65_ask35": {"raw": 0.03, "recross": 0.50, "abs_d": 0.65, "ask_min": 0.35},
    "core_raw03_recross50_abs65_ask50": {"raw": 0.03, "recross": 0.50, "abs_d": 0.65, "ask_min": 0.50},
    "core_raw05_recross60_abs085_ask65": {"raw": 0.05, "recross": 0.60, "abs_d": 0.85, "ask_min": 0.65},
}

TAIL_RULES = {
    "tail_raw03_recross50_abs75_asklt35": {"raw": 0.03, "recross": 0.50, "abs_d": 0.75, "ask_max": 0.35},
    "tail_raw05_recross50_abs85_asklt35": {"raw": 0.05, "recross": 0.50, "abs_d": 0.85, "ask_max": 0.35},
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
        "candidate_family": "feature_gate_cheap_tail_quarantine",
        "physics": (
            "Very cheap boundary-tail rows are asymmetric lottery exposures. They can produce large wins, "
            "but they should not count as broad-entry coverage repair until they independently clear "
            "sample, source-quality, and fragility gates."
        ),
        "core_rules": CORE_RULES,
        "tail_rules": TAIL_RULES,
    }
    STATE_JSON.write_text(json.dumps(state, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return state


def passes_core(row: dict[str, Any], rule: dict[str, float]) -> bool:
    edge = raw_edge(row)
    row_recross = recross(row)
    abs_d = as_float(row.get("abs_d_sigma"))
    ask = as_float(row.get("ask_prob"))
    return (
        edge is not None and edge >= rule["raw"]
        and row_recross is not None and row_recross <= rule["recross"]
        and abs_d is not None and abs_d >= rule["abs_d"]
        and ask is not None and ask >= rule["ask_min"]
    )


def passes_tail(row: dict[str, Any], rule: dict[str, float]) -> bool:
    edge = raw_edge(row)
    row_recross = recross(row)
    abs_d = as_float(row.get("abs_d_sigma"))
    ask = as_float(row.get("ask_prob"))
    return (
        edge is not None and edge >= rule["raw"]
        and row_recross is not None and row_recross <= rule["recross"]
        and abs_d is not None and abs_d >= rule["abs_d"]
        and ask is not None and ask < rule["ask_max"]
    )


def select_best(rows: list[dict[str, Any]], predicate: Any) -> list[dict[str, Any]]:
    return best_per_market([row for row in rows if predicate(row)])


def source_counts(rows: list[dict[str, Any]]) -> dict[str, int]:
    return dict(Counter(source(row) for row in rows))


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
    }


def quality(summary: dict[str, Any], share: float | None, broad_required: bool) -> dict[str, Any]:
    settled = int(as_float(summary.get("settled")) or 0)
    coverage = as_float(summary.get("coverage_pct"))
    net_cents = as_float(summary.get("net_cents")) or 0.0
    cushion = int(max(0.0, net_cents) // 100.0)
    blockers: list[str] = []
    if settled < MIN_SETTLED:
        blockers.append("settled_lt_30")
    if broad_required and (coverage is None or coverage < COVERAGE_FLOOR):
        blockers.append("coverage_too_low")
    if net_cents <= 0.0:
        blockers.append("net_not_positive")
    if share is not None and share > MAX_RECONSTRUCTED_SHARE:
        blockers.append("reconstructed_share_gt_35pct")
    if cushion < MIN_FULL_LOSS_CUSHION:
        blockers.append("full_loss_cushion_lt_3")
    return {
        "full_loss_cushion_estimate": cushion,
        "blockers": blockers,
        "ready": not blockers,
    }


def summarize_selection(
    label: str,
    rows: list[dict[str, Any]],
    denominator: int,
    broad_required: bool,
) -> dict[str, Any]:
    summary = summarize(rows, denominator)
    counts = source_counts(rows)
    share = reconstructed_share(counts)
    row_nets = [net(row) for row in rows]
    top_win = max(row_nets) if row_nets else 0.0
    total_net = sum(row_nets)
    result = {
        "label": label,
        "future_denominator": denominator,
        "summary": summary,
        "source_counts": counts,
        "reconstructed_share": share,
        "top_win_cents": top_win,
        "net_without_top_win_cents": total_net - top_win,
        "rows": [compact_row(row) for row in sorted(rows, key=lambda item: net(item))],
    }
    result.update(quality(summary, share, broad_required))
    if total_net > 0.0 and top_win / max(total_net, 1.0) >= 0.50:
        result["blockers"].append("top_win_concentration_ge_50pct_net")
        result["ready"] = False
    return result


def evaluate_lane(
    label: str,
    freeze_ts: str,
    all_rows: list[dict[str, Any]],
    denominator: int,
) -> dict[str, Any]:
    denominator = int(denominator or 0)
    core = []
    for name, rule in CORE_RULES.items():
        selected = select_best(all_rows, lambda row, rule=rule: passes_core(row, rule))
        core.append(summarize_selection(name, selected, denominator, broad_required=True))
    tails = []
    for name, rule in TAIL_RULES.items():
        selected = select_best(all_rows, lambda row, rule=rule: passes_tail(row, rule))
        tails.append(summarize_selection(name, selected, denominator, broad_required=False))
    core.sort(
        key=lambda row: (
            len(row.get("blockers") or []),
            -float((row.get("summary") or {}).get("net_cents") or -999999.0),
            -float((row.get("summary") or {}).get("coverage_pct") or 0.0),
        )
    )
    tails.sort(
        key=lambda row: (
            len(row.get("blockers") or []),
            -float((row.get("summary") or {}).get("net_cents") or -999999.0),
        )
    )
    return {
        "lane": label,
        "freeze_ts_utc": freeze_ts,
        "future_denominator": denominator,
        "core_rules": core,
        "tail_rules": tails,
    }


def build_report() -> dict[str, Any]:
    state = load_or_create_state()
    feature_state = load_json(FEATURE_STATE_JSON)
    feature_freeze = str(feature_state.get("freeze_ts_utc") or state["freeze_ts_utc"])
    quarantine_freeze = str(state["freeze_ts_utc"])
    feature_entry_rows, _, feature_entry_denominator = entry_surfaces(feature_freeze)
    feature_bridge_rows, _, feature_bridge_denominator = bridge_surfaces(feature_freeze)
    quarantine_entry_rows, _, quarantine_entry_denominator = entry_surfaces(quarantine_freeze)
    quarantine_bridge_rows, _, quarantine_bridge_denominator = bridge_surfaces(quarantine_freeze)
    lanes = [
        evaluate_lane(
            "diagnostic_feature_window_entry",
            feature_freeze,
            feature_entry_rows,
            int(feature_entry_denominator or 0),
        ),
        evaluate_lane(
            "diagnostic_feature_window_bridge",
            feature_freeze,
            feature_bridge_rows,
            int(feature_bridge_denominator or 0),
        ),
        evaluate_lane(
            "post_quarantine_freeze_entry",
            quarantine_freeze,
            quarantine_entry_rows,
            int(quarantine_entry_denominator or 0),
        ),
        evaluate_lane(
            "post_quarantine_freeze_bridge",
            quarantine_freeze,
            quarantine_bridge_rows,
            int(quarantine_bridge_denominator or 0),
        ),
    ]
    return {
        "generated_at_utc": utc_now_iso(),
        "state": state,
        "feature_gate_freeze_ts_utc": feature_freeze,
        "interpretation": interpretation(lanes),
        "lanes": lanes,
    }


def interpretation(lanes: list[dict[str, Any]]) -> list[str]:
    notes = [
        "Core rules are judged as broad-entry candidates; cheap-tail rules are judged only as sidecars.",
        "Cheap-tail rows are not allowed to repair core coverage in this report.",
    ]
    for lane in lanes:
        core = (lane.get("core_rules") or [{}])[0]
        tail = (lane.get("tail_rules") or [{}])[0]
        core_summary = core.get("summary") or {}
        tail_summary = tail.get("summary") or {}
        notes.append(
            f"{lane.get('lane')}: best core {core.get('label')} has {core_summary.get('settled')} settled, "
            f"coverage {core_summary.get('coverage_pct')}%, net {core_summary.get('net_cents')}c, blockers {core.get('blockers')}; "
            f"best tail {tail.get('label')} has {tail_summary.get('settled')} settled, net {tail_summary.get('net_cents')}c, blockers {tail.get('blockers')}."
        )
    return notes


def fmt(value: Any) -> str:
    if value is None:
        return "None"
    if isinstance(value, float):
        return f"{value:.6f}"
    return str(value)


def write_group(lines: list[str], rows: list[dict[str, Any]]) -> None:
    lines.extend([
        "| rule | settled/den | W/L | coverage | net c | recon | cushion | top win | net ex top | ready | blockers |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---|---|",
    ])
    for row in rows:
        summary = row.get("summary") or {}
        lines.append(
            f"| `{row.get('label')}` | {summary.get('settled')}/{row.get('future_denominator')} | "
            f"{summary.get('wins')}/{summary.get('losses')} | {fmt(summary.get('coverage_pct'))} | "
            f"{fmt(summary.get('net_cents'))} | {fmt(row.get('reconstructed_share'))} | "
            f"{row.get('full_loss_cushion_estimate')} | {fmt(row.get('top_win_cents'))} | "
            f"{fmt(row.get('net_without_top_win_cents'))} | {row.get('ready')} | "
            f"{', '.join(row.get('blockers') or []) or 'none'} |"
        )


def write_report(report: dict[str, Any]) -> None:
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8")
    state = report.get("state") or {}
    lines = [
        "# v28 Feature-Gate Cheap-Tail Quarantine",
        "",
        "Research-only; no live bot changes or orders.",
        "",
        f"- Generated UTC: `{report.get('generated_at_utc')}`",
        f"- Quarantine freeze UTC: `{state.get('freeze_ts_utc')}`",
        f"- Feature-gate freeze UTC: `{report.get('feature_gate_freeze_ts_utc')}`",
        "",
        "## Interpretation",
        "",
    ]
    lines.extend(f"- {note}" for note in report.get("interpretation") or [])
    for lane in report.get("lanes") or []:
        lines.extend(["", f"## {lane.get('lane')}", "", "### Core Rules", ""])
        write_group(lines, lane.get("core_rules") or [])
        lines.extend(["", "### Cheap-Tail Sidecar Rules", ""])
        write_group(lines, lane.get("tail_rules") or [])
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    report = build_report()
    write_report(report)
    print(OUT_MD)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
