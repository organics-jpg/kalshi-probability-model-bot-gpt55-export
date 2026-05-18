"""Frozen watch for soft-frontier size-shrink portfolio rules.

Research-only; no live bot changes or orders.

The soft-frontier feature gate is the broadest observable branch that is close
to target coverage, but its weak rows cluster around near-boundary and
mid-cheap states. This probe tests continuous exposure shrinkage instead of
hard exclusion: keep market participation, but reduce notional when the entry
physics say confidence is fragile.
"""
from __future__ import annotations

import json
from collections import Counter, defaultdict
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
STATE_JSON = OUT_DIR / "v28_soft_frontier_size_shrink_portfolio_state.json"
OUT_JSON = OUT_DIR / "v28_soft_frontier_size_shrink_portfolio_latest.json"
OUT_MD = OUT_DIR / "v28_soft_frontier_size_shrink_portfolio_latest.md"
COLLAPSE_REENTRY_JSON = OUT_DIR / "v28_live_collapse_reentry_registry_latest.json"

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
        "candidate_family": "soft_frontier_size_shrink_portfolio",
        "entry_rule": BROAD_RULE,
        "physics": (
            "Broad soft-frontier rows have useful directional signal but weak "
            "near-boundary/mid-cheap rows behave like over-sized confidence. "
            "The repair keeps participation and shrinks notional continuously "
            "instead of adding another hard source-like cutoff."
        ),
        "strict_forward_note": "Rows before this timestamp are diagnostic only; only post_shrink_birth rows count for promotion.",
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


def source_counts(rows: list[dict[str, Any]]) -> dict[str, int]:
    return dict(Counter(source(row) for row in rows))


def collapse_tags_by_market_side() -> dict[tuple[str, str], set[str]]:
    payload = load_json(COLLAPSE_REENTRY_JSON)
    out: dict[tuple[str, str], set[str]] = defaultdict(set)
    for row in payload.get("future_rows") or []:
        if not isinstance(row, dict):
            continue
        key = (str(row.get("market") or ""), str(row.get("side") or ""))
        if not key[0] or not key[1]:
            continue
        out[key].update(str(tag) for tag in row.get("tags") or [])
    return out


def fragility_tags(row: dict[str, Any], collapse_tags: dict[tuple[str, str], set[str]]) -> list[str]:
    tags: list[str] = []
    abs_d = as_float(row.get("abs_d_sigma"))
    ask = as_float(row.get("ask_prob"))
    edge = raw_edge(row)
    row_recross = recross(row)
    if abs_d is not None and abs_d < 0.65:
        tags.append("near_boundary_absd_lt_065")
    if ask is not None and ask < 0.50:
        tags.append("mid_cheap_ask_lt_050")
    if edge is not None and edge < 0.05:
        tags.append("thin_raw_edge_lt_005")
    if row_recross is not None and row_recross > 0.30:
        tags.append("higher_recross_gt_030")
    entry_tags = collapse_tags.get((market(row), str(row.get("side") or ""))) or set()
    if "same_side_reentry" in entry_tags:
        tags.append("collapse_same_side_reentry")
    if "thin_edge_lt_4c" in entry_tags:
        tags.append("collapse_thin_edge_reentry")
    return tags


def weight_none(row: dict[str, Any], tags: list[str]) -> float:
    return 1.0


def weight_half_near_boundary(row: dict[str, Any], tags: list[str]) -> float:
    if "near_boundary_absd_lt_065" in tags or "mid_cheap_ask_lt_050" in tags:
        return 0.5
    return 1.0


def weight_quarter_near_boundary(row: dict[str, Any], tags: list[str]) -> float:
    if "near_boundary_absd_lt_065" in tags:
        return 0.25
    if "mid_cheap_ask_lt_050" in tags:
        return 0.5
    return 1.0


def weight_continuous_boundary(row: dict[str, Any], tags: list[str]) -> float:
    abs_d = as_float(row.get("abs_d_sigma")) or 0.50
    ask = as_float(row.get("ask_prob")) or 0.35
    distance_weight = min(1.0, max(0.35, (abs_d - 0.50) / 0.35))
    ask_weight = min(1.0, max(0.50, (ask - 0.35) / 0.30))
    return min(distance_weight, ask_weight)


def weight_reentry_guarded_continuous(row: dict[str, Any], tags: list[str]) -> float:
    base = weight_continuous_boundary(row, tags)
    if "collapse_same_side_reentry" in tags and "collapse_thin_edge_reentry" in tags:
        return 0.0
    if "collapse_same_side_reentry" in tags:
        return min(base, 0.5)
    return base


WEIGHT_POLICIES: dict[str, Callable[[dict[str, Any], list[str]], float]] = {
    "no_size_shrink_control": weight_none,
    "half_near_boundary_or_midcheap": weight_half_near_boundary,
    "quarter_near_boundary_half_midcheap": weight_quarter_near_boundary,
    "continuous_absd_ask_shrink": weight_continuous_boundary,
    "continuous_plus_same_side_reentry_guard": weight_reentry_guarded_continuous,
}


def summarize_weighted(
    rows: list[dict[str, Any]],
    denominator: int,
    policy: Callable[[dict[str, Any], list[str]], float],
    collapse_tags: dict[tuple[str, str], set[str]],
) -> dict[str, Any]:
    weighted_rows = []
    tag_counts: Counter[str] = Counter()
    for row in rows:
        tags = fragility_tags(row, collapse_tags)
        weight = max(0.0, min(1.0, float(policy(row, tags))))
        weighted_net = net(row) * weight
        for tag in tags:
            tag_counts[tag] += 1
        weighted_rows.append({
            "market": market(row),
            "side": row.get("side"),
            "source": source(row),
            "raw_net_cents": net(row),
            "weighted_net_cents": weighted_net,
            "weight": weight,
            "raw_edge": raw_edge(row),
            "recross_hazard_score": recross(row),
            "abs_d_sigma": as_float(row.get("abs_d_sigma")),
            "ask_prob": as_float(row.get("ask_prob")),
            "side_won": row.get("side_won"),
            "fragility_tags": tags,
        })
    settled_rows = [row for row in weighted_rows if row["side_won"] is not None]
    wins = sum(1 for row in settled_rows if row["weighted_net_cents"] > 0)
    losses = sum(1 for row in settled_rows if row["weighted_net_cents"] < 0)
    flat = sum(1 for row in settled_rows if row["weighted_net_cents"] == 0)
    selected = len(weighted_rows)
    active = sum(1 for row in weighted_rows if row["weight"] > 0)
    net_cents = sum(row["weighted_net_cents"] for row in weighted_rows)
    raw_net_cents = sum(row["raw_net_cents"] for row in weighted_rows)
    return {
        "entries": selected,
        "active_entries": active,
        "settled": len(settled_rows),
        "wins": wins,
        "losses": losses,
        "flat": flat,
        "coverage_pct": (100.0 * selected / denominator) if denominator else None,
        "active_coverage_pct": (100.0 * active / denominator) if denominator else None,
        "net_cents": net_cents,
        "raw_unweighted_net_cents": raw_net_cents,
        "delta_vs_unweighted_cents": net_cents - raw_net_cents,
        "avg_weight": (sum(row["weight"] for row in weighted_rows) / selected) if selected else None,
        "full_loss_cushion_estimate": int(max(0.0, net_cents) // 100.0),
        "tag_counts": dict(tag_counts),
        "rows": sorted(weighted_rows, key=lambda row: row["weighted_net_cents"]),
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
    collapse_tags = collapse_tags_by_market_side()
    variants = []
    for name, policy in WEIGHT_POLICIES.items():
        summary = summarize_weighted(selected, int(denominator or 0), policy, collapse_tags)
        variants.append({
            "candidate": f"{label}_{name}",
            "weight_policy": name,
            "entry_rule": BROAD_RULE,
            "summary": summary,
            "source_counts": counts,
            "reconstructed_share": share,
            "blockers": blockers(summary, share, strict_forward),
            "live_ready": strict_forward and not blockers(summary, share, strict_forward),
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
    entry_state = load_json(ENTRY_STATE_JSON)
    bridge_state = load_json(BRIDGE_STATE_JSON)
    feature_state = load_json(FEATURE_STATE_JSON)
    soft_state = load_json(SOFT_FRONTIER_STATE_JSON)
    lanes: list[dict[str, Any]] = []
    if entry_state.get("freeze_ts_utc"):
        lanes.append(evaluate_lane("diagnostic_entry", str(entry_state["freeze_ts_utc"]), entry_surfaces, False))
    if bridge_state.get("freeze_ts_utc"):
        lanes.append(evaluate_lane("diagnostic_bridge", str(bridge_state["freeze_ts_utc"]), bridge_surfaces, False))
    if feature_state.get("freeze_ts_utc"):
        lanes.append(evaluate_lane("post_feature_freeze_entry", str(feature_state["freeze_ts_utc"]), entry_surfaces, False))
    if soft_state.get("freeze_ts_utc"):
        lanes.append(evaluate_lane("post_soft_frontier_birth_entry", str(soft_state["freeze_ts_utc"]), entry_surfaces, False))
    lanes.append(evaluate_lane("post_shrink_birth_entry", str(state["freeze_ts_utc"]), entry_surfaces, True))
    lanes.append(evaluate_lane("post_shrink_birth_bridge", str(state["freeze_ts_utc"]), bridge_surfaces, True))
    return {
        "generated_at_utc": utc_now_iso(),
        "state": state,
        "interpretation": interpretation(lanes),
        "lanes": lanes,
    }


def interpretation(lanes: list[dict[str, Any]]) -> list[str]:
    notes = [
        "This is a size/risk overlay, not a new hard entry cutoff.",
        "Only post_shrink_birth lanes are strict forward evidence for this candidate family.",
    ]
    for lane in lanes:
        best = (lane.get("variants") or [{}])[0]
        summary = best.get("summary") or {}
        notes.append(
            f"{lane.get('lane')}: best {best.get('candidate')} settled {summary.get('settled')}, "
            f"coverage {summary.get('coverage_pct')}%, active coverage {summary.get('active_coverage_pct')}%, "
            f"net {summary.get('net_cents')}c, raw {summary.get('raw_unweighted_net_cents')}c, "
            f"avg weight {summary.get('avg_weight')}, recon {best.get('reconstructed_share')}, "
            f"tags {summary.get('tag_counts')}, blockers {best.get('blockers')}."
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
        "# v28 Soft-Frontier Size-Shrink Portfolio",
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
        "| lane | strict | best policy | settled | W/L | coverage | active cov | net | raw net | avg weight | recon | blockers |",
        "|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---|",
    ])
    for lane in report.get("lanes") or []:
        best = (lane.get("variants") or [{}])[0]
        summary = best.get("summary") or {}
        lines.append(
            "| {lane} | {strict} | `{policy}` | {settled} | {wins}/{losses} | {coverage} | {active_cov} | {net} | {raw_net} | {avg_weight} | {recon} | {blockers} |".format(
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
            "| policy | settled | W/L | coverage | active cov | net | delta vs raw | avg weight | cushion | blockers |",
            "|---|---:|---:|---:|---:|---:|---:|---:|---:|---|",
        ])
        for variant in lane.get("variants") or []:
            summary = variant.get("summary") or {}
            lines.append(
                "| `{policy}` | {settled} | {wins}/{losses} | {coverage} | {active_cov} | {net} | {delta} | {avg_weight} | {cushion} | {blockers} |".format(
                    policy=variant.get("weight_policy"),
                    settled=summary.get("settled"),
                    wins=summary.get("wins"),
                    losses=summary.get("losses"),
                    coverage=fmt_pct(summary.get("coverage_pct")),
                    active_cov=fmt_pct(summary.get("active_coverage_pct")),
                    net=fmt_cents(summary.get("net_cents")),
                    delta=fmt_cents(summary.get("delta_vs_unweighted_cents")),
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
