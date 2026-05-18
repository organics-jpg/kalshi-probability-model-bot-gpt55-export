"""Frozen watch for observable source-dilution on the midprice shrink lane.

Research-only; no live bot changes or orders.

The strict post-feature midprice lane is very close to the source-quality gate:
positive PnL, target coverage, cushion >=3, but reconstructed share is slightly
above 35%. This probe tests observable weak-boundary dilution rules, then
freezes the best physical idea from its own timestamp for future evidence.
Source labels are used only for audit after selection.
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
    load_json,
    market,
    net,
    recross,
    reconstructed_share,
    source,
)
from probe_v28_coverage_repair_pool_diagnostic import COVERAGE_FLOOR, raw_edge
from probe_v28_frozen_boundary_clock_fv_entry_bridge import future_surfaces as bridge_surfaces
from probe_v28_frozen_boundary_clock_repair_entry import future_surfaces as entry_surfaces
from probe_v28_soft_frontier_midprice_boundary_shrink_watch import BROAD_RULE, in_midprice_boundary_band


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
MIDPRICE_JSON = OUT_DIR / "v28_soft_frontier_midprice_boundary_shrink_latest.json"
STATE_JSON = OUT_DIR / "v28_midprice_source_dilution_watch_state.json"
OUT_JSON = OUT_DIR / "v28_midprice_source_dilution_watch_latest.json"
OUT_MD = OUT_DIR / "v28_midprice_source_dilution_watch_latest.md"

MIN_SETTLED = 30
MAX_RECON_SHARE = 0.35
MIN_CUSHION = 3

FILTERS = {
    "control_no_extra_filter": {
        "physics": "Baseline quarter-midprice shrink; no extra source-dilution rule.",
        "abs_d_min": None,
        "ask_min": None,
    },
    "weak_boundary_absd_gte_055": {
        "physics": "Drop only the closest boundary-touch rows; abs_d below 0.55 is too close to strike for reliable side conviction.",
        "abs_d_min": 0.55,
        "ask_min": None,
    },
    "weak_boundary_absd_gte_060": {
        "physics": "Stronger weak-boundary dilution; may over-prune coverage.",
        "abs_d_min": 0.60,
        "ask_min": None,
    },
    "mid_or_better_ask_gte_055": {
        "physics": "Drop very cheap touches where market price says this is lottery-like, not robust side conviction.",
        "abs_d_min": None,
        "ask_min": 0.55,
    },
    "absd_gte_055_or_ask_gte_065": {
        "physics": "Allow close-boundary rows only when the ask already shows stronger market confirmation.",
        "abs_d_min": 0.55,
        "ask_min": 0.65,
        "or_mode": True,
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
        "candidate_family": "midprice_source_dilution_watch",
        "parent": "soft_frontier_midprice_boundary_shrink",
        "candidate": "quarter_midprice_boundary_plus_weak_boundary_absd_gte_055",
        "rule": FILTERS["weak_boundary_absd_gte_055"],
        "physics": (
            "The parent lane is source-blocked by a very small number of weak-boundary rows. "
            "The dilution rule drops only rows whose observed distance to strike is too small "
            "to justify full side conviction, while keeping the continuous midprice notional shrink."
        ),
        "strict_forward_note": "Rows before this timestamp are diagnostic only; post_dilution_birth rows are promotion evidence.",
    }
    STATE_JSON.write_text(json.dumps(state, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return state


def fnum(value: Any, default: float = 0.0) -> float:
    parsed = as_float(value)
    return default if parsed is None else parsed


def passes_broad(row: dict[str, Any]) -> bool:
    edge = raw_edge(row)
    row_recross = recross(row)
    abs_d = as_float(row.get("abs_d_sigma"))
    ask = as_float(row.get("ask_prob"))
    return (
        edge is not None
        and row_recross is not None
        and abs_d is not None
        and ask is not None
        and edge >= BROAD_RULE["raw_edge_min"]
        and row_recross <= BROAD_RULE["recross_max"]
        and abs_d >= BROAD_RULE["abs_d_min"]
        and ask >= BROAD_RULE["ask_min"]
    )


def quarter_weight(row: dict[str, Any]) -> float:
    return 0.25 if in_midprice_boundary_band(row) else 1.0


def passes_filter(row: dict[str, Any], rule: dict[str, Any]) -> bool:
    abs_min = as_float(rule.get("abs_d_min"))
    ask_min = as_float(rule.get("ask_min"))
    row_abs = as_float(row.get("abs_d_sigma"))
    row_ask = as_float(row.get("ask_prob"))
    abs_ok = abs_min is None or (row_abs is not None and row_abs >= abs_min)
    ask_ok = ask_min is None or (row_ask is not None and row_ask >= ask_min)
    if rule.get("or_mode"):
        return abs_ok or ask_ok
    return abs_ok and ask_ok


def source_counts(rows: list[dict[str, Any]]) -> dict[str, int]:
    return dict(Counter(source(row) for row in rows))


def row_view(row: dict[str, Any], weight: float | None = None) -> dict[str, Any]:
    raw_net = as_float(row.get("raw_net_cents"))
    if raw_net is None:
        raw_net = net(row)
    row_weight = quarter_weight(row) if weight is None else weight
    return {
        "market": market(row),
        "side": row.get("side"),
        "source": source(row),
        "net_cents": raw_net,
        "weighted_net_cents": raw_net * row_weight,
        "weight": row_weight,
        "raw_edge": as_float(row.get("raw_edge")) if row.get("raw_edge") is not None else raw_edge(row),
        "recross_hazard_score": as_float(row.get("recross_hazard_score")) if row.get("recross_hazard_score") is not None else recross(row),
        "abs_d_sigma": as_float(row.get("abs_d_sigma")),
        "ask_prob": as_float(row.get("ask_prob")),
        "side_won": row.get("side_won"),
        "midprice_boundary_band": in_midprice_boundary_band(row),
    }


def summarize(rows: list[dict[str, Any]], denominator: int, filter_name: str, rule: dict[str, Any]) -> dict[str, Any]:
    base = [row_view(row) for row in rows]
    kept = [row for row in base if passes_filter(row, rule)]
    dropped = [row for row in base if not passes_filter(row, rule)]
    settled = [row for row in kept if row.get("side_won") is not None]
    net_cents = sum(fnum(row.get("weighted_net_cents")) for row in kept)
    counts = source_counts(kept)
    share = reconstructed_share(counts)
    return {
        "filter": filter_name,
        "entries": len(kept),
        "dropped_entries": len(dropped),
        "settled": len(settled),
        "wins": sum(1 for row in settled if fnum(row.get("weighted_net_cents")) > 0),
        "losses": sum(1 for row in settled if fnum(row.get("weighted_net_cents")) < 0),
        "coverage_pct": 100.0 * len(kept) / denominator if denominator else None,
        "net_cents": net_cents,
        "full_loss_cushion": int(max(0.0, net_cents) // 100.0),
        "source_counts": counts,
        "reconstructed_share": share,
        "dropped_net_cents": sum(fnum(row.get("weighted_net_cents")) for row in dropped),
        "dropped_source_counts": source_counts(dropped),
        "dropped_rows": sorted(dropped, key=lambda row: fnum(row.get("weighted_net_cents")))[:12],
        "worst_kept_rows": sorted(kept, key=lambda row: fnum(row.get("weighted_net_cents")))[:12],
        "blockers": blockers(len(settled), len(kept), denominator, net_cents, share),
    }


def blockers(settled: int, entries: int, denominator: int, net_cents: float, share: float | None) -> list[str]:
    out: list[str] = []
    coverage = 100.0 * entries / denominator if denominator else None
    if settled < MIN_SETTLED:
        out.append("settled_lt_30")
    if coverage is None or coverage < COVERAGE_FLOOR:
        out.append("coverage_too_low")
    if net_cents <= 0:
        out.append("net_not_positive")
    if share is None or share > MAX_RECON_SHARE:
        out.append("reconstructed_share_gt_35pct")
    if int(max(0.0, net_cents) // 100.0) < MIN_CUSHION:
        out.append("full_loss_cushion_lt_3")
    return out


def evaluate_rows(lane: str, strict_forward: bool, rows: list[dict[str, Any]], denominator: int) -> dict[str, Any]:
    variants = [summarize(rows, denominator, name, rule) for name, rule in FILTERS.items()]
    variants.sort(
        key=lambda row: (
            len(row.get("blockers") or []),
            -float(row.get("net_cents") or -999999.0),
            -float(row.get("coverage_pct") or 0.0),
        )
    )
    if not strict_forward:
        for variant in variants:
            variant["blockers"] = list(dict.fromkeys(["diagnostic_only_prefreeze", *(variant.get("blockers") or [])]))
    return {
        "lane": lane,
        "strict_forward": strict_forward,
        "future_denominator": denominator,
        "variants": variants,
    }


def rows_from_artifact(lane_name: str) -> tuple[list[dict[str, Any]], int]:
    payload = load_json(MIDPRICE_JSON)
    for lane in payload.get("lanes") or []:
        if lane.get("lane") != lane_name:
            continue
        denominator = int(as_float(lane.get("future_denominator")) or 0)
        for variant in lane.get("variants") or []:
            if variant.get("weight_policy") == "quarter_midprice_boundary":
                rows = ((variant.get("summary") or {}).get("rows") or [])
                return rows, denominator
    return [], 0


def rows_from_surface(freeze_ts: str, surface_fn: Any) -> tuple[list[dict[str, Any]], int]:
    all_rows, _, denominator = surface_fn(freeze_ts)
    selected = best_per_market([row for row in all_rows if passes_broad(row)])
    return selected, int(denominator or 0)


def build_report() -> dict[str, Any]:
    state = load_or_create_state()
    diag_entry_rows, diag_entry_denominator = rows_from_artifact("post_feature_freeze_entry")
    diag_bridge_rows, diag_bridge_denominator = rows_from_artifact("post_feature_freeze_bridge")
    strict_entry_rows, strict_entry_denominator = rows_from_surface(str(state["freeze_ts_utc"]), entry_surfaces)
    strict_bridge_rows, strict_bridge_denominator = rows_from_surface(str(state["freeze_ts_utc"]), bridge_surfaces)
    lanes = [
        evaluate_rows("diagnostic_parent_entry", False, diag_entry_rows, diag_entry_denominator),
        evaluate_rows("diagnostic_parent_bridge", False, diag_bridge_rows, diag_bridge_denominator),
        evaluate_rows("post_dilution_birth_entry", True, strict_entry_rows, strict_entry_denominator),
        evaluate_rows("post_dilution_birth_bridge", True, strict_bridge_rows, strict_bridge_denominator),
    ]
    return {
        "generated_at_utc": utc_now_iso(),
        "state": state,
        "interpretation": interpretation(lanes),
        "lanes": lanes,
    }


def interpretation(lanes: list[dict[str, Any]]) -> list[str]:
    notes = [
        "Source labels are audit-only; all tested filters use observable abs_d/ask fields.",
        "Only post_dilution_birth lanes are strict forward evidence for this new watch.",
    ]
    for lane in lanes:
        best = (lane.get("variants") or [{}])[0]
        notes.append(
            f"{lane.get('lane')}: best {best.get('filter')} entries {best.get('entries')}, "
            f"W/L {best.get('wins')}/{best.get('losses')}, coverage {best.get('coverage_pct')}%, "
            f"net {best.get('net_cents')}c, recon {best.get('reconstructed_share')}, "
            f"dropped {best.get('dropped_entries')} for {best.get('dropped_net_cents')}c, "
            f"blockers {best.get('blockers')}."
        )
    return notes


def money(value: Any) -> str:
    number = as_float(value)
    return "n/a" if number is None else f"{number:.1f}c"


def pct(value: Any) -> str:
    number = as_float(value)
    return "n/a" if number is None else f"{number:.2f}%"


def write_report(report: dict[str, Any]) -> None:
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8")
    lines = [
        "# v28 Midprice Source-Dilution Watch",
        "",
        "Research-only. No live bot logic changed and no orders placed.",
        "",
        f"- Generated UTC: `{report.get('generated_at_utc')}`",
        f"- Freeze UTC: `{(report.get('state') or {}).get('freeze_ts_utc')}`",
        "",
        "## Interpretation",
        "",
    ]
    lines.extend(f"- {note}" for note in report.get("interpretation") or [])
    for lane in report.get("lanes") or []:
        lines.extend([
            "",
            f"## {lane.get('lane')}",
            "",
            "| filter | strict | entries | dropped | W/L | coverage | net | recon | cushion | dropped net | blockers |",
            "|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---|",
        ])
        for variant in lane.get("variants") or []:
            lines.append(
                f"| `{variant.get('filter')}` | {lane.get('strict_forward')} | {variant.get('entries')} | "
                f"{variant.get('dropped_entries')} | {variant.get('wins')}/{variant.get('losses')} | "
                f"{pct(variant.get('coverage_pct'))} | {money(variant.get('net_cents'))} | "
                f"{pct((variant.get('reconstructed_share') or 0.0) * 100.0)} | {variant.get('full_loss_cushion')} | "
                f"{money(variant.get('dropped_net_cents'))} | {', '.join(variant.get('blockers') or []) or 'none'} |"
            )
        best = (lane.get("variants") or [{}])[0]
        lines.extend(["", "### Dropped Rows For Best Filter", ""])
        lines.extend([
            "| market | side | source | net | weight | abs_d | ask | recross |",
            "|---|---|---|---:|---:|---:|---:|---:|",
        ])
        for row in best.get("dropped_rows") or []:
            lines.append(
                f"| `{row.get('market')}` | `{row.get('side')}` | `{row.get('source')}` | "
                f"{money(row.get('weighted_net_cents'))} | {row.get('weight')} | "
                f"{row.get('abs_d_sigma')} | {row.get('ask_prob')} | {row.get('recross_hazard_score')} |"
            )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    report = build_report()
    write_report(report)
    print(OUT_MD)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
