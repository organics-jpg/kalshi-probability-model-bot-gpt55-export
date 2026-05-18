"""Observable source-risk notional shrink watch for v28 feature-gate rows.

Research-only; no live bot changes or orders.

The broad feature-gate row is source-quality blocked, but its weakest
rejected-actionable losses share observable traits: cheap tail price, low
model-side probability, thin depth, weaker boundary distance, thin raw edge,
and early observations. This probe freezes a notional shrink watch using only
those observable features. Row-count source gates are still reported as hard
promotion blockers.
"""
from __future__ import annotations

import json
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

from probe_v28_boundary_clock_feature_gate_candidate import (
    RULES,
    as_float,
    best_per_market,
    load_json,
    market,
    net,
    passes,
    raw_edge,
    recross,
    source,
)
from probe_v28_coverage_repair_pool_diagnostic import COVERAGE_FLOOR
from probe_v28_frozen_boundary_clock_fv_entry_bridge import future_surfaces as bridge_surfaces
from probe_v28_frozen_boundary_clock_repair_entry import future_surfaces as entry_surfaces


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
FEATURE_STATE_JSON = OUT_DIR / "v28_boundary_clock_feature_gate_candidate_state.json"
STATE_JSON = OUT_DIR / "v28_feature_gate_source_risk_shrink_watch_state.json"
OUT_JSON = OUT_DIR / "v28_feature_gate_source_risk_shrink_watch_latest.json"
OUT_MD = OUT_DIR / "v28_feature_gate_source_risk_shrink_watch_latest.md"

RULE_NAME = "raw03_recross70_abs075"
MIN_SETTLED = 30
MAX_ROW_SOURCE_SHARE = 0.35
MAX_EXPOSURE_SOURCE_SHARE = 0.35
MIN_FULL_LOSS_CUSHION = 3

POLICIES = [
    "no_shrink_control",
    "risk_half_step",
    "risk_quarter_step",
    "risk_linear_20",
    "risk_linear_30",
    "cheap_thin_quarter",
    "cheap_thin_fifth",
]


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def load_or_create_state() -> dict[str, Any]:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    if STATE_JSON.exists():
        state = load_json(STATE_JSON)
        if state.get("freeze_ts_utc"):
            if state.get("policies") != POLICIES:
                state["policies"] = POLICIES
                state["updated_at_utc"] = utc_now_iso()
                STATE_JSON.write_text(json.dumps(state, indent=2, sort_keys=True) + "\n", encoding="utf-8")
            return state
    state = {
        "freeze_ts_utc": utc_now_iso(),
        "candidate_family": "feature_gate_observable_source_risk_notional_shrink",
        "base_rule": RULE_NAME,
        "physics": (
            "Shrink notional, not row selection, for rows that look like the rejected-slice "
            "failure mechanism: cheap/low-p-side boundary tails with thin depth, thin edge, "
            "weaker boundary distance, or early observation timing."
        ),
        "policies": POLICIES,
        "promotion_note": (
            "This is not live-ready unless the official row-count source gate, sample gate, "
            "coverage gate, net gate, and full-loss cushion gate all pass on strict rows."
        ),
    }
    STATE_JSON.write_text(json.dumps(state, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return state


def fnum(value: Any, default: float = 0.0) -> float:
    parsed = as_float(value)
    return default if parsed is None else parsed


def ask_prob(row: dict[str, Any]) -> float:
    ask = as_float(row.get("ask_prob"))
    if ask is not None:
        return ask
    ask_cents = as_float(row.get("ask_cents"))
    return (ask_cents / 100.0) if ask_cents is not None else 0.0


def p_side(row: dict[str, Any]) -> float:
    value = as_float(row.get("p_side"))
    if value is not None:
        return value
    p_yes = as_float(row.get("p_yes"))
    if p_yes is None:
        return 0.0
    return p_yes if str(row.get("side") or "") == "yes" else 1.0 - p_yes


def abs_d(row: dict[str, Any]) -> float:
    return abs(fnum(row.get("abs_d_sigma")))


def seconds_to_close(row: dict[str, Any]) -> float:
    return fnum(row.get("seconds_to_close"), 9999.0)


def depth(row: dict[str, Any]) -> float:
    return fnum(row.get("eligible_depth"), 999999.0)


def risk_tags(row: dict[str, Any]) -> list[str]:
    tags: list[str] = []
    ask = ask_prob(row)
    side_prob = p_side(row)
    row_abs_d = abs_d(row)
    row_recross = fnum(recross(row))
    edge = raw_edge(row)
    if ask < 0.50:
        tags.append("cheap_tail_ask_lt50")
    if side_prob < 0.75:
        tags.append("low_p_side_lt75")
    if depth(row) < 100.0:
        tags.append("thin_depth_lt100")
    if row_abs_d < 0.65:
        tags.append("weak_boundary_distance_lt65")
    elif row_abs_d < 0.85:
        tags.append("moderate_boundary_distance_65_85")
    if edge is not None and edge < 0.05:
        tags.append("thin_raw_edge_lt05")
    if seconds_to_close(row) < 240.0:
        tags.append("early_observation_stc_lt240")
    if row_recross > 0.60:
        tags.append("high_recross_60_70")
    return tags


def risk_score(row: dict[str, Any]) -> float:
    tags = set(risk_tags(row))
    score = 0.0
    score += 1.00 if "cheap_tail_ask_lt50" in tags else 0.0
    score += 1.00 if "low_p_side_lt75" in tags else 0.0
    score += 1.00 if "thin_depth_lt100" in tags else 0.0
    score += 1.25 if "weak_boundary_distance_lt65" in tags else 0.0
    score += 0.75 if "moderate_boundary_distance_65_85" in tags else 0.0
    score += 1.00 if "thin_raw_edge_lt05" in tags else 0.0
    score += 0.50 if "early_observation_stc_lt240" in tags else 0.0
    score += 0.75 if "high_recross_60_70" in tags else 0.0
    return score


def weight(policy: str, row: dict[str, Any]) -> float:
    score = risk_score(row)
    tags = set(risk_tags(row))
    if policy == "no_shrink_control":
        return 1.0
    if policy == "risk_half_step":
        return 0.50 if score >= 2.0 else 1.0
    if policy == "risk_quarter_step":
        if score >= 3.0:
            return 0.25
        return 0.50 if score >= 2.0 else 1.0
    if policy == "risk_linear_20":
        return max(0.25, 1.0 - 0.20 * score)
    if policy == "risk_linear_30":
        return max(0.125, 1.0 - 0.30 * score)
    if policy == "cheap_thin_quarter":
        fragile = {
            "thin_depth_lt100",
            "thin_raw_edge_lt05",
            "weak_boundary_distance_lt65",
            "moderate_boundary_distance_65_85",
        }
        return 0.25 if "cheap_tail_ask_lt50" in tags and tags.intersection(fragile) else 1.0
    if policy == "cheap_thin_fifth":
        fragile = {
            "thin_depth_lt100",
            "thin_raw_edge_lt05",
            "weak_boundary_distance_lt65",
            "moderate_boundary_distance_65_85",
        }
        return 0.20 if "cheap_tail_ask_lt50" in tags and tags.intersection(fragile) else 1.0
    return 1.0


def selected_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return best_per_market([row for row in rows if passes(row, RULES[RULE_NAME])])


def row_summary(row: dict[str, Any], row_weight: float) -> dict[str, Any]:
    row_net = net(row)
    return {
        "market": market(row),
        "source": source(row),
        "side": row.get("side"),
        "side_won": row.get("side_won"),
        "net_cents": row_net,
        "weight": row_weight,
        "weighted_net_cents": row_net * row_weight if row.get("side_won") is not None else None,
        "risk_score": risk_score(row),
        "risk_tags": risk_tags(row),
        "ask_prob": ask_prob(row),
        "p_side": p_side(row),
        "raw_edge": raw_edge(row),
        "recross_hazard_score": recross(row),
        "abs_d_sigma": abs_d(row),
        "seconds_to_close": seconds_to_close(row),
        "eligible_depth": depth(row),
    }


def summarize_policy(lane: str, policy: str, rows: list[dict[str, Any]], denominator: int) -> dict[str, Any]:
    entries = len(rows)
    settled_rows = [row for row in rows if row.get("side_won") is not None]
    weighted_net = 0.0
    exposure = 0.0
    source_exposure = 0.0
    source_rows = 0
    tag_counts: Counter[str] = Counter()
    tag_weight: Counter[str] = Counter()
    tag_weighted_net: Counter[str] = Counter()
    compact_rows: list[dict[str, Any]] = []

    for row in rows:
        row_weight = weight(policy, row)
        row_source = source(row)
        row_net = net(row)
        exposure += row_weight
        if row_source != "approved_entry":
            source_rows += 1
            source_exposure += row_weight
        tags = risk_tags(row) or ["no_observable_source_risk"]
        for tag in tags:
            tag_counts[tag] += 1
            tag_weight[tag] += row_weight
            if row.get("side_won") is not None:
                tag_weighted_net[tag] += row_weight * row_net
        if row.get("side_won") is not None:
            weighted_net += row_weight * row_net
        compact_rows.append(row_summary(row, row_weight))

    coverage = 100.0 * entries / denominator if denominator else 0.0
    row_source_share = source_rows / entries if entries else 0.0
    exposure_source_share = source_exposure / exposure if exposure else 0.0
    cushion = int(max(0.0, weighted_net) // 100.0)
    blockers: list[str] = []
    if len(settled_rows) < MIN_SETTLED:
        blockers.append("settled_lt_30")
    if coverage < COVERAGE_FLOOR:
        blockers.append("coverage_too_low")
    if weighted_net <= 0.0:
        blockers.append("weighted_net_not_positive")
    if row_source_share > MAX_ROW_SOURCE_SHARE:
        blockers.append("row_source_share_gt_35pct")
    if exposure_source_share > MAX_EXPOSURE_SOURCE_SHARE:
        blockers.append("exposure_source_share_gt_35pct")
    if cushion < MIN_FULL_LOSS_CUSHION:
        blockers.append("weighted_full_loss_cushion_lt_3")

    return {
        "lane": lane,
        "policy": policy,
        "entries": entries,
        "settled": len(settled_rows),
        "wins": sum(1 for row in settled_rows if row.get("side_won") is True),
        "losses": sum(1 for row in settled_rows if row.get("side_won") is False),
        "coverage_pct": coverage,
        "weighted_net_cents": weighted_net,
        "avg_weighted_net_cents": weighted_net / len(settled_rows) if settled_rows else None,
        "row_source_share": row_source_share,
        "exposure_source_share": exposure_source_share,
        "notional_exposure_rows": exposure,
        "full_loss_cushion": cushion,
        "net_cents_needed_for_cushion3": max(0.0, 300.0 - weighted_net),
        "source_counts": dict(Counter(source(row) for row in rows)),
        "tag_counts": dict(tag_counts),
        "tag_weight": dict(tag_weight),
        "tag_weighted_net_cents": dict(tag_weighted_net),
        "blockers": blockers,
        "live_ready": not blockers,
        "worst_rows": sorted(compact_rows, key=lambda item: item.get("weighted_net_cents") or 0.0)[:10],
        "best_rows": sorted(compact_rows, key=lambda item: item.get("weighted_net_cents") or 0.0, reverse=True)[:8],
    }


def evaluate_lane(label: str, freeze_ts: str, surfaces_fn: Callable[[str], Any]) -> dict[str, Any]:
    rows, _, denominator = surfaces_fn(freeze_ts)
    denominator = int(denominator or 0)
    selected = selected_rows(rows)
    policy_rows = [summarize_policy(label, policy, selected, denominator) for policy in POLICIES]
    policy_rows.sort(
        key=lambda row: (
            len(row.get("blockers") or []),
            -float(row.get("weighted_net_cents") or -999999.0),
            float(row.get("exposure_source_share") or 999.0),
        )
    )
    return {
        "lane": label,
        "freeze_ts_utc": freeze_ts,
        "future_denominator": denominator,
        "base_rule": RULE_NAME,
        "selected_entries": len(selected),
        "policies": policy_rows,
    }


def build_report() -> dict[str, Any]:
    state = load_or_create_state()
    feature_state = load_json(FEATURE_STATE_JSON)
    feature_freeze = str(feature_state.get("freeze_ts_utc") or state["freeze_ts_utc"])
    watch_freeze = str(state["freeze_ts_utc"])
    lanes = [
        evaluate_lane("diagnostic_feature_window_entry", feature_freeze, entry_surfaces),
        evaluate_lane("diagnostic_feature_window_bridge", feature_freeze, bridge_surfaces),
        evaluate_lane("post_source_risk_birth_entry", watch_freeze, entry_surfaces),
        evaluate_lane("post_source_risk_birth_bridge", watch_freeze, bridge_surfaces),
    ]
    report = {
        "generated_at_utc": utc_now_iso(),
        "state": state,
        "feature_freeze_ts_utc": feature_freeze,
        "lanes": lanes,
    }
    report["interpretation"] = interpretation(report)
    return report


def interpretation(report: dict[str, Any]) -> list[str]:
    notes = [
        "This is a notional-shrink watch using only observable source-risk features; source labels remain audit-only.",
        "The official row-count source gate is still a hard promotion blocker even if exposure source share improves.",
    ]
    for lane in report.get("lanes") or []:
        best = (lane.get("policies") or [{}])[0]
        notes.append(
            f"{lane.get('lane')}: best {best.get('policy')} has {best.get('entries')}/"
            f"{lane.get('future_denominator')} entries, {best.get('settled')} settled, "
            f"W/L {best.get('wins')}/{best.get('losses')}, weighted net "
            f"{best.get('weighted_net_cents')}c, row/exposure source share "
            f"{best.get('row_source_share')}/{best.get('exposure_source_share')}, "
            f"cushion {best.get('full_loss_cushion')}, blockers {best.get('blockers')}."
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
        "# v28 Feature-Gate Source-Risk Shrink Watch",
        "",
        "Research-only; no live bot changes or orders.",
        "",
        f"- Generated UTC: `{report.get('generated_at_utc')}`",
        f"- Watch freeze UTC: `{(report.get('state') or {}).get('freeze_ts_utc')}`",
        f"- Feature freeze UTC: `{report.get('feature_freeze_ts_utc')}`",
        "",
        "## Interpretation",
        "",
    ]
    lines.extend(f"- {note}" for note in report.get("interpretation") or [])
    for lane in report.get("lanes") or []:
        lines.extend(
            [
                "",
                f"## {lane.get('lane')}",
                "",
                f"- Base rule: `{lane.get('base_rule')}`",
                f"- Selected entries: `{lane.get('selected_entries')}`",
                f"- Future denominator: `{lane.get('future_denominator')}`",
                "",
                "| rank | policy | settled | W/L | coverage | weighted net | row source | exposure source | exposure rows | cushion | blockers |",
                "|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---|",
            ]
        )
        for idx, row in enumerate(lane.get("policies") or [], start=1):
            lines.append(
                f"| {idx} | {row.get('policy')} | {row.get('settled')} | "
                f"{row.get('wins')}/{row.get('losses')} | {fmt(row.get('coverage_pct'))} | "
                f"{fmt(row.get('weighted_net_cents'))} | {fmt(row.get('row_source_share'))} | "
                f"{fmt(row.get('exposure_source_share'))} | {fmt(row.get('notional_exposure_rows'))} | "
                f"{row.get('full_loss_cushion')} | {', '.join(row.get('blockers') or []) or 'none'} |"
            )
        best = (lane.get("policies") or [{}])[0]
        lines.extend(
            [
                "",
                "### Best Policy Tag Attribution",
                "",
                f"- Policy: `{best.get('policy')}`",
                f"- Tag counts: `{best.get('tag_counts')}`",
                f"- Tag weight: `{best.get('tag_weight')}`",
                f"- Tag weighted net cents: `{best.get('tag_weighted_net_cents')}`",
                "",
                "### Worst Weighted Rows",
                "",
                "| market | source | side | won | net c | weight | weighted c | risk | tags | ask | p side | edge | recross | abs d | stc | depth |",
                "|---|---|---|---|---:|---:|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|",
            ]
        )
        for row in best.get("worst_rows") or []:
            lines.append(
                f"| {row.get('market')} | {row.get('source')} | {row.get('side')} | {row.get('side_won')} | "
                f"{fmt(row.get('net_cents'))} | {fmt(row.get('weight'))} | {fmt(row.get('weighted_net_cents'))} | "
                f"{fmt(row.get('risk_score'))} | {', '.join(row.get('risk_tags') or []) or 'none'} | "
                f"{fmt(row.get('ask_prob'))} | {fmt(row.get('p_side'))} | {fmt(row.get('raw_edge'))} | "
                f"{fmt(row.get('recross_hazard_score'))} | {fmt(row.get('abs_d_sigma'))} | "
                f"{fmt(row.get('seconds_to_close'))} | {fmt(row.get('eligible_depth'))} |"
            )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    report = build_report()
    write_md(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
