"""Frozen watch for soft-frontier mid-price boundary size shrink.

Research-only; no live bot changes or orders.

The broad soft-frontier entry rule is close to the target strategy shape, but
its repeated diagnostic damage clusters in an observable state: near-boundary
rows that are not cheap lottery entries and not high-confidence expensive
entries. This probe freezes a continuous notional shrink for that state and
requires new forward rows from its own timestamp before any promotion claim.
"""
from __future__ import annotations

import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

from probe_v28_boundary_clock_feature_gate_candidate import (
    BRIDGE_STATE_JSON,
    ENTRY_STATE_JSON,
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
from probe_v28_boundary_clock_feature_gate_soft_frontier_watch import STATE_JSON as SOFT_FRONTIER_STATE_JSON
from probe_v28_coverage_repair_pool_diagnostic import COVERAGE_FLOOR, raw_edge
from probe_v28_frozen_boundary_clock_fv_entry_bridge import future_surfaces as bridge_surfaces
from probe_v28_frozen_boundary_clock_repair_entry import future_surfaces as entry_surfaces


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
STATE_JSON = OUT_DIR / "v28_soft_frontier_midprice_boundary_shrink_state.json"
PORTFOLIO_JSON = OUT_DIR / "v28_soft_frontier_size_shrink_portfolio_latest.json"
OUT_JSON = OUT_DIR / "v28_soft_frontier_midprice_boundary_shrink_latest.json"
OUT_MD = OUT_DIR / "v28_soft_frontier_midprice_boundary_shrink_latest.md"

MIN_SETTLED = 30
MAX_RECONSTRUCTED_SHARE = 0.35
MIN_FULL_LOSS_CUSHION = 3

BROAD_RULE = {
    "raw_edge_min": 0.03,
    "recross_max": 0.50,
    "abs_d_min": 0.50,
    "ask_min": 0.35,
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
        "candidate_family": "soft_frontier_midprice_boundary_shrink",
        "entry_rule": BROAD_RULE,
        "shrink_band": {
            "abs_d_lt": 0.65,
            "ask_gte": 0.55,
            "ask_lt": 0.65,
        },
        "physics": (
            "Near-boundary mid-price rows are ambiguous: price is high enough "
            "to carry real full-loss risk, but not high enough to represent a "
            "clear consensus/high-confidence side. The repair keeps broad "
            "selection but shrinks notional in that continuous confidence band."
        ),
        "strict_forward_note": "Rows before this timestamp are diagnostic only; only post_midprice_shrink_birth rows count for promotion.",
    }
    STATE_JSON.write_text(json.dumps(state, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return state


def passes_broad(row: dict[str, Any]) -> bool:
    edge = raw_edge(row)
    row_recross = recross(row)
    abs_d = as_float(row.get("abs_d_sigma"))
    ask = as_float(row.get("ask_prob"))
    if edge is None or row_recross is None or abs_d is None or ask is None:
        return False
    return (
        edge >= BROAD_RULE["raw_edge_min"]
        and row_recross <= BROAD_RULE["recross_max"]
        and abs_d >= BROAD_RULE["abs_d_min"]
        and ask >= BROAD_RULE["ask_min"]
    )


def in_midprice_boundary_band(row: dict[str, Any]) -> bool:
    abs_d = as_float(row.get("abs_d_sigma"))
    ask = as_float(row.get("ask_prob"))
    return abs_d is not None and ask is not None and abs_d < 0.65 and 0.55 <= ask < 0.65


def weight_control(row: dict[str, Any]) -> float:
    return 1.0


def weight_half_midprice_boundary(row: dict[str, Any]) -> float:
    return 0.5 if in_midprice_boundary_band(row) else 1.0


def weight_quarter_midprice_boundary(row: dict[str, Any]) -> float:
    return 0.25 if in_midprice_boundary_band(row) else 1.0


WEIGHT_POLICIES: dict[str, Callable[[dict[str, Any]], float]] = {
    "control_no_shrink": weight_control,
    "half_midprice_boundary": weight_half_midprice_boundary,
    "quarter_midprice_boundary": weight_quarter_midprice_boundary,
}


def source_counts(rows: list[dict[str, Any]]) -> dict[str, int]:
    return dict(Counter(source(row) for row in rows))


def summarize_weighted(rows: list[dict[str, Any]], denominator: int, policy: Callable[[dict[str, Any]], float]) -> dict[str, Any]:
    weighted_rows = []
    for row in rows:
        weight = max(0.0, min(1.0, float(policy(row))))
        raw_net = as_float(row.get("raw_net_cents"))
        if raw_net is None:
            raw_net = net(row)
        weighted_rows.append({
            "market": market(row),
            "side": row.get("side"),
            "source": source(row),
            "raw_net_cents": raw_net,
            "weighted_net_cents": raw_net * weight,
            "weight": weight,
            "raw_edge": as_float(row.get("raw_edge")) if row.get("raw_edge") is not None else raw_edge(row),
            "recross_hazard_score": as_float(row.get("recross_hazard_score")) if row.get("recross_hazard_score") is not None else recross(row),
            "abs_d_sigma": as_float(row.get("abs_d_sigma")),
            "ask_prob": as_float(row.get("ask_prob")),
            "side_won": row.get("side_won"),
            "midprice_boundary_band": in_midprice_boundary_band(row),
        })
    settled_rows = [row for row in weighted_rows if row["side_won"] is not None]
    wins = sum(1 for row in settled_rows if row["weighted_net_cents"] > 0)
    losses = sum(1 for row in settled_rows if row["weighted_net_cents"] < 0)
    selected = len(weighted_rows)
    active = sum(1 for row in weighted_rows if row["weight"] > 0)
    net_cents = sum(row["weighted_net_cents"] for row in weighted_rows)
    raw_net_cents = sum(row["raw_net_cents"] for row in weighted_rows)
    band_rows = [row for row in weighted_rows if row["midprice_boundary_band"]]
    return {
        "entries": selected,
        "active_entries": active,
        "settled": len(settled_rows),
        "wins": wins,
        "losses": losses,
        "coverage_pct": (100.0 * selected / denominator) if denominator else None,
        "active_coverage_pct": (100.0 * active / denominator) if denominator else None,
        "net_cents": net_cents,
        "raw_unweighted_net_cents": raw_net_cents,
        "delta_vs_unweighted_cents": net_cents - raw_net_cents,
        "avg_weight": (sum(row["weight"] for row in weighted_rows) / selected) if selected else None,
        "full_loss_cushion_estimate": int(max(0.0, net_cents) // 100.0),
        "midprice_boundary_rows": len(band_rows),
        "midprice_boundary_raw_net_cents": sum(row["raw_net_cents"] for row in band_rows),
        "midprice_boundary_weighted_net_cents": sum(row["weighted_net_cents"] for row in band_rows),
        "rows": sorted(weighted_rows, key=lambda row: row["weighted_net_cents"]),
    }


def evaluate_existing_portfolio_lane(lane: dict[str, Any]) -> dict[str, Any]:
    control = next(
        (
            variant
            for variant in lane.get("variants") or []
            if variant.get("weight_policy") == "no_size_shrink_control"
        ),
        {},
    )
    control_summary = control.get("summary") or {}
    rows = control_summary.get("rows") or []
    counts = control.get("source_counts") or {}
    share = control.get("reconstructed_share")
    denominator = int(lane.get("future_denominator") or 0)
    variants = []
    for name, policy in WEIGHT_POLICIES.items():
        summary = summarize_weighted(rows, denominator, policy)
        row_blockers = blockers(summary, share, False)
        variants.append({
            "candidate": f"{lane.get('lane')}_{name}",
            "weight_policy": name,
            "entry_rule": BROAD_RULE,
            "summary": summary,
            "source_counts": counts,
            "reconstructed_share": share,
            "blockers": row_blockers,
            "live_ready": False,
        })
    variants.sort(
        key=lambda row: (
            len(row.get("blockers") or []),
            -float((row.get("summary") or {}).get("net_cents") or -999999.0),
            -float((row.get("summary") or {}).get("coverage_pct") or 0.0),
        )
    )
    return {
        "lane": lane.get("lane"),
        "freeze_ts_utc": lane.get("freeze_ts_utc"),
        "strict_forward": False,
        "future_denominator": denominator,
        "variants": variants,
    }


def blockers(summary: dict[str, Any], share: float | None, strict_forward: bool) -> list[str]:
    out: list[str] = []
    settled = int(as_float(summary.get("settled")) or 0)
    coverage = as_float(summary.get("coverage_pct"))
    net_cents = as_float(summary.get("net_cents"))
    if strict_forward and settled < MIN_SETTLED:
        out.append("settled_lt_30")
    elif not strict_forward:
        out.append("diagnostic_only_prefreeze")
    if coverage is None or coverage < COVERAGE_FLOOR:
        out.append("coverage_too_low")
    if net_cents is None or net_cents <= 0:
        out.append("net_not_positive")
    if share is not None and share > MAX_RECONSTRUCTED_SHARE:
        out.append("reconstructed_share_gt_35pct")
    if int(max(0.0, float(net_cents or 0.0)) // 100.0) < MIN_FULL_LOSS_CUSHION:
        out.append("full_loss_cushion_lt_3")
    return out


def evaluate_lane(label: str, freeze_ts: str, surfaces_fn: Any, strict_forward: bool) -> dict[str, Any]:
    all_rows, _, denominator = surfaces_fn(freeze_ts)
    selected = best_per_market([row for row in all_rows if passes_broad(row)])
    counts = source_counts(selected)
    share = reconstructed_share(counts)
    variants = []
    for name, policy in WEIGHT_POLICIES.items():
        summary = summarize_weighted(selected, int(denominator or 0), policy)
        row_blockers = blockers(summary, share, strict_forward)
        variants.append({
            "candidate": f"{label}_{name}",
            "weight_policy": name,
            "entry_rule": BROAD_RULE,
            "summary": summary,
            "source_counts": counts,
            "reconstructed_share": share,
            "blockers": row_blockers,
            "live_ready": strict_forward and not row_blockers,
        })
    variants.sort(
        key=lambda row: (
            len(row.get("blockers") or []),
            -float((row.get("summary") or {}).get("net_cents") or -999999.0),
            -float((row.get("summary") or {}).get("coverage_pct") or 0.0),
        )
    )
    return {
        "lane": label,
        "freeze_ts_utc": freeze_ts,
        "strict_forward": strict_forward,
        "future_denominator": int(denominator or 0),
        "variants": variants,
    }


def build_report() -> dict[str, Any]:
    state = load_or_create_state()
    portfolio = load_json(PORTFOLIO_JSON)
    lanes: list[dict[str, Any]] = []
    for lane in portfolio.get("lanes") or []:
        if lane.get("lane") in {
            "diagnostic_entry",
            "diagnostic_bridge",
            "post_feature_freeze_entry",
            "post_soft_frontier_birth_entry",
        }:
            lanes.append(evaluate_existing_portfolio_lane(lane))
    lanes.append(evaluate_lane("post_midprice_shrink_birth_entry", str(state["freeze_ts_utc"]), entry_surfaces, True))
    return {
        "generated_at_utc": utc_now_iso(),
        "state": state,
        "diagnostic_source": str(PORTFOLIO_JSON),
        "strict_surface_note": "Only the entry surface is evaluated to keep the watch lightweight; bridge can be added if entry proves useful.",
        "interpretation": interpretation(lanes),
        "lanes": lanes,
    }


def interpretation(lanes: list[dict[str, Any]]) -> list[str]:
    notes = [
        "This freezes a continuous size/risk overlay, not a new hard entry cutoff.",
        "Only post_midprice_shrink_birth lanes are strict forward evidence for this candidate family.",
    ]
    for lane in lanes:
        best = (lane.get("variants") or [{}])[0]
        summary = best.get("summary") or {}
        notes.append(
            f"{lane.get('lane')}: best {best.get('candidate')} settled {summary.get('settled')}, "
            f"coverage {summary.get('coverage_pct')}%, active coverage {summary.get('active_coverage_pct')}%, "
            f"net {summary.get('net_cents')}c, raw {summary.get('raw_unweighted_net_cents')}c, "
            f"band rows {summary.get('midprice_boundary_rows')} raw/weighted "
            f"{summary.get('midprice_boundary_raw_net_cents')}/{summary.get('midprice_boundary_weighted_net_cents')}c, "
            f"recon {best.get('reconstructed_share')}, blockers {best.get('blockers')}."
        )
    return notes


def fmt_cents(value: Any) -> str:
    number = as_float(value)
    if number is None:
        return "n/a"
    return f"{number:.0f}c (${number / 100.0:.2f})"


def fmt_pct(value: Any) -> str:
    number = as_float(value)
    if number is None:
        return "n/a"
    return f"{number:.2f}%"


def write_md(report: dict[str, Any]) -> None:
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8")
    lines = [
        "# v28 Soft-Frontier Mid-Price Boundary Shrink Watch",
        "",
        "Research-only. No live bot logic changed and no orders placed.",
        "",
        f"- Generated UTC: `{report['generated_at_utc']}`",
        f"- Freeze UTC: `{(report.get('state') or {}).get('freeze_ts_utc')}`",
        "",
        "## Interpretation",
        "",
    ]
    lines.extend(f"- {note}" for note in report.get("interpretation") or [])
    lines.extend([
        "",
        "## Lanes",
        "",
        "| lane | strict | best policy | settled | W/L | coverage | active cov | net | raw net | band rows | band raw/weighted | avg weight | recon | blockers |",
        "|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|",
    ])
    for lane in report.get("lanes") or []:
        best = (lane.get("variants") or [{}])[0]
        summary = best.get("summary") or {}
        lines.append(
            "| {lane} | {strict} | `{policy}` | {settled} | {wins}/{losses} | {coverage} | {active_cov} | {net} | {raw_net} | {band_rows} | {band_raw}/{band_weighted} | {avg_weight} | {recon} | {blockers} |".format(
                lane=lane.get("lane"),
                strict=lane.get("strict_forward"),
                policy=best.get("weight_policy"),
                settled=summary.get("settled"),
                wins=summary.get("wins"),
                losses=summary.get("losses"),
                coverage=fmt_pct(summary.get("coverage_pct")),
                active_cov=fmt_pct(summary.get("active_coverage_pct")),
                net=fmt_cents(summary.get("net_cents")),
                raw_net=fmt_cents(summary.get("raw_unweighted_net_cents")),
                band_rows=summary.get("midprice_boundary_rows"),
                band_raw=fmt_cents(summary.get("midprice_boundary_raw_net_cents")),
                band_weighted=fmt_cents(summary.get("midprice_boundary_weighted_net_cents")),
                avg_weight=fmt_pct((summary.get("avg_weight") or 0.0) * 100.0),
                recon=fmt_pct((best.get("reconstructed_share") or 0.0) * 100.0),
                blockers=", ".join(best.get("blockers") or []) or "none",
            )
        )
    lines.extend([
        "",
        "## Variant Detail",
        "",
    ])
    for lane in report.get("lanes") or []:
        lines.extend([
            f"### {lane.get('lane')}",
            "",
            "| policy | settled | W/L | coverage | active cov | net | delta vs raw | band rows | band raw/weighted | avg weight | cushion | blockers |",
            "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|",
        ])
        for variant in lane.get("variants") or []:
            summary = variant.get("summary") or {}
            lines.append(
                "| `{policy}` | {settled} | {wins}/{losses} | {coverage} | {active_cov} | {net} | {delta} | {band_rows} | {band_raw}/{band_weighted} | {avg_weight} | {cushion} | {blockers} |".format(
                    policy=variant.get("weight_policy"),
                    settled=summary.get("settled"),
                    wins=summary.get("wins"),
                    losses=summary.get("losses"),
                    coverage=fmt_pct(summary.get("coverage_pct")),
                    active_cov=fmt_pct(summary.get("active_coverage_pct")),
                    net=fmt_cents(summary.get("net_cents")),
                    delta=fmt_cents(summary.get("delta_vs_unweighted_cents")),
                    band_rows=summary.get("midprice_boundary_rows"),
                    band_raw=fmt_cents(summary.get("midprice_boundary_raw_net_cents")),
                    band_weighted=fmt_cents(summary.get("midprice_boundary_weighted_net_cents")),
                    avg_weight=fmt_pct((summary.get("avg_weight") or 0.0) * 100.0),
                    cushion=summary.get("full_loss_cushion_estimate"),
                    blockers=", ".join(variant.get("blockers") or []) or "none",
                )
            )
        lines.append("")
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    report = build_report()
    write_md(report)
    print(str(OUT_MD))


if __name__ == "__main__":
    main()
