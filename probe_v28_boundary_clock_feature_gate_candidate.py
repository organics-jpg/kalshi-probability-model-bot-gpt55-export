"""Frozen boundary-clock feature-gate candidate.

Research-only; no live bot changes or orders.

This turns the approved-source feature contrast into actual observable gates:
raw edge, recross hazard, distance from strike, and optional ask floor. The
rules do not use source labels for selection. Source labels are only audited
after selection to check evidence quality.
"""
from __future__ import annotations

import json
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from probe_v28_coverage_repair_pool_diagnostic import COVERAGE_FLOOR, raw_edge, row_net_after_fee, summarize
from probe_v28_frozen_boundary_clock_fv_entry_bridge import (
    future_surfaces as bridge_surfaces,
    load_json as bridge_load_json,
)
from probe_v28_frozen_boundary_clock_repair_entry import (
    future_surfaces as entry_surfaces,
    load_json as entry_load_json,
)


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
STATE_JSON = OUT_DIR / "v28_boundary_clock_feature_gate_candidate_state.json"
ENTRY_STATE_JSON = OUT_DIR / "v28_frozen_boundary_clock_repair_entry_state.json"
BRIDGE_STATE_JSON = OUT_DIR / "v28_frozen_boundary_clock_fv_entry_bridge_state.json"
OUT_JSON = OUT_DIR / "v28_boundary_clock_feature_gate_candidate_latest.json"
OUT_MD = OUT_DIR / "v28_boundary_clock_feature_gate_candidate_latest.md"

MIN_SETTLED = 30
MAX_RECONSTRUCTED_SHARE = 0.35
MIN_FULL_LOSS_CUSHION = 3

RULES = {
    "raw05_recross60_abs085": {
        "raw_edge_min": 0.05,
        "recross_max": 0.60,
        "abs_d_min": 0.85,
        "ask_min": None,
    },
    "raw05_recross60_abs085_ask65": {
        "raw_edge_min": 0.05,
        "recross_max": 0.60,
        "abs_d_min": 0.85,
        "ask_min": 0.65,
    },
    "raw03_recross70_abs075": {
        "raw_edge_min": 0.03,
        "recross_max": 0.70,
        "abs_d_min": 0.75,
        "ask_min": None,
    },
    "raw07_recross60_abs085": {
        "raw_edge_min": 0.07,
        "recross_max": 0.60,
        "abs_d_min": 0.85,
        "ask_min": None,
    },
}


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
    state = {
        "freeze_ts_utc": utc_now_iso(),
        "candidate_family": "boundary_clock_feature_gate",
        "origin": "Derived from boundary-clock approved-source feature contrast; frozen before promotion use.",
        "rules": RULES,
    }
    STATE_JSON.write_text(json.dumps(state, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return state


def as_float(value: Any) -> float | None:
    if value is None or value == "":
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def market(row: dict[str, Any]) -> str:
    return str(row.get("market") or "")


def source(row: dict[str, Any]) -> str:
    return str(row.get("source") or "unknown")


def recross(row: dict[str, Any]) -> float | None:
    return as_float(row.get("recross_hazard_score"))


def net(row: dict[str, Any]) -> float:
    return float(row_net_after_fee(row) or 0.0)


def passes(row: dict[str, Any], rule: dict[str, Any]) -> bool:
    edge = raw_edge(row)
    row_recross = recross(row)
    abs_d = as_float(row.get("abs_d_sigma"))
    ask = as_float(row.get("ask_prob"))
    if edge is None or row_recross is None or abs_d is None:
        return False
    if edge < float(rule["raw_edge_min"]):
        return False
    if row_recross > float(rule["recross_max"]):
        return False
    if abs_d < float(rule["abs_d_min"]):
        return False
    ask_min = rule.get("ask_min")
    if ask_min is not None and (ask is None or ask < float(ask_min)):
        return False
    return True


def best_per_market(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        if market(row):
            grouped[market(row)].append(row)
    return [max(items, key=lambda row: raw_edge(row) or -999.0) for items in grouped.values()]


def source_counts(rows: list[dict[str, Any]]) -> dict[str, int]:
    return dict(Counter(source(row) for row in rows))


def reconstructed_share(counts: dict[str, int]) -> float | None:
    total = sum(counts.values())
    if total <= 0:
        return None
    return (total - int(counts.get("approved_entry") or 0)) / total


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
    cushion = int(max(0.0, float(net_cents or 0.0)) // 100.0)
    if cushion < MIN_FULL_LOSS_CUSHION:
        out.append("full_loss_cushion_lt_3")
    return out


def evaluate_lane(label: str, freeze_ts: str, surfaces_fn: Any) -> dict[str, Any]:
    all_rows, _, denominator = surfaces_fn(freeze_ts)
    variants = []
    for name, rule in RULES.items():
        selected = best_per_market([row for row in all_rows if passes(row, rule)])
        summary = summarize(selected, denominator)
        counts = source_counts(selected)
        share = reconstructed_share(counts)
        variants.append(
            {
                "candidate": f"{label}_{name}",
                "rule": rule,
                "candidate_summary": summary,
                "source_counts": counts,
                "reconstructed_share": share,
                "full_loss_cushion_estimate": int(max(0.0, float(summary.get("net_cents") or 0.0)) // 100.0),
                "blockers": blockers(summary, share),
                "rows": [
                    {
                        "market": market(row),
                        "source": source(row),
                        "side": row.get("side"),
                        "side_won": row.get("side_won"),
                        "net_cents": net(row),
                        "raw_edge": raw_edge(row),
                        "recross_hazard_score": row.get("recross_hazard_score"),
                        "abs_d_sigma": row.get("abs_d_sigma"),
                        "ask_prob": row.get("ask_prob"),
                    }
                    for row in selected
                ],
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
        "freeze_ts": freeze_ts,
        "future_denominator": denominator,
        "variants": variants,
    }


def build_report() -> dict[str, Any]:
    state = load_or_create_state()
    entry_state = entry_load_json(ENTRY_STATE_JSON)
    bridge_state = bridge_load_json(BRIDGE_STATE_JSON)
    lanes = []
    if entry_state.get("freeze_ts_utc"):
        lanes.append(evaluate_lane("diagnostic_entry", str(entry_state["freeze_ts_utc"]), entry_surfaces))
    if bridge_state.get("freeze_ts_utc"):
        lanes.append(evaluate_lane("diagnostic_bridge", str(bridge_state["freeze_ts_utc"]), bridge_surfaces))
    lanes.append(evaluate_lane("post_feature_freeze_entry", str(state["freeze_ts_utc"]), entry_surfaces))
    lanes.append(evaluate_lane("post_feature_freeze_bridge", str(state["freeze_ts_utc"]), bridge_surfaces))
    return {
        "generated_at_utc": utc_now_iso(),
        "state": state,
        "purpose": "Frozen feature-gate candidate derived from boundary-clock approved-source contrast.",
        "lanes": lanes,
        "interpretation": interpretation(lanes),
    }


def interpretation(lanes: list[dict[str, Any]]) -> list[str]:
    notes = ["Selection uses only observable features; source labels are audit-only."]
    for lane in lanes:
        best = (lane.get("variants") or [{}])[0]
        summary = best.get("candidate_summary") or {}
        notes.append(
            f"{lane.get('lane')}: best {best.get('candidate')} settled {summary.get('settled')}, coverage {summary.get('coverage_pct')}%, net {summary.get('net_cents')}c, recon {best.get('reconstructed_share')}, blockers {best.get('blockers')}."
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
        "# v28 Boundary-Clock Feature-Gate Candidate",
        "",
        "Research-only; frozen candidate, no live logic changes.",
        "",
        f"- Generated UTC: `{report.get('generated_at_utc')}`",
        f"- Feature-gate freeze UTC: `{state.get('freeze_ts_utc')}`",
        "",
        "## Interpretation",
        "",
    ]
    for note in report.get("interpretation") or []:
        lines.append(f"- {note}")
    for lane in report.get("lanes") or []:
        lines.extend(
            [
                "",
                f"## {lane.get('lane')}",
                "",
                f"- Freeze UTC: `{lane.get('freeze_ts')}`",
                f"- Future denominator: `{lane.get('future_denominator')}`",
                "",
                "| rank | candidate | settled | coverage | net c | W/L | recon share | source counts | cushion | blockers |",
                "|---:|---|---:|---:|---:|---:|---:|---|---:|---|",
            ]
        )
        for idx, row in enumerate(lane.get("variants") or [], start=1):
            summary = row.get("candidate_summary") or {}
            lines.append(
                f"| {idx} | {row.get('candidate')} | {summary.get('settled')} | {fmt(summary.get('coverage_pct'))} | "
                f"{fmt(summary.get('net_cents'))} | {summary.get('wins')}/{summary.get('losses')} | "
                f"{fmt(row.get('reconstructed_share'))} | {row.get('source_counts')} | "
                f"{row.get('full_loss_cushion_estimate')} | {', '.join(row.get('blockers') or []) or 'none'} |"
            )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    report = build_report()
    write_md(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
