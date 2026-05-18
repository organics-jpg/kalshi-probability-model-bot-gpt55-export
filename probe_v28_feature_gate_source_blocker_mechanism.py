"""Mechanism drilldown for the feature-gate source-quality blocker.

Research-only; no live bot changes or orders.

The near-gate size-shrink branch is positive and broad, but misses the
row-source gate by one selected row. This probe explains that blocker: what the
rejected/reconstructed selected rows look like, whether same-market approved
substitutes exist, and how much source-label oracle replacement would be needed.
Source labels are used only for audit/oracle bounds, never as a deployable rule.
"""
from __future__ import annotations

import json
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

from probe_v28_boundary_clock_feature_gate_candidate import as_float, load_or_create_state, market, net, source
from probe_v28_boundary_clock_feature_gate_coverage_source_frontier import passes_rule, raw_edge, rule_name
from probe_v28_feature_gate_coverage_size_shrink import ANCHOR_RULE, REPAIR_RULE, repair_weight, row_key, summarize_policy
from probe_v28_frozen_boundary_clock_fv_entry_bridge import future_surfaces as bridge_surfaces
from probe_v28_frozen_boundary_clock_repair_entry import future_surfaces as entry_surfaces


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
OUT_JSON = OUT_DIR / "v28_feature_gate_source_blocker_mechanism_latest.json"
OUT_MD = OUT_DIR / "v28_feature_gate_source_blocker_mechanism_latest.md"

POLICY = "repair_low_absd_quarter_else_half"


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def fnum(value: Any, default: float = 0.0) -> float:
    parsed = as_float(value)
    return default if parsed is None else parsed


def recross(row: dict[str, Any]) -> float:
    return fnum(row.get("recross_hazard_score"), 1.0)


def abs_d(row: dict[str, Any]) -> float:
    return fnum(row.get("abs_d_sigma"))


def ask(row: dict[str, Any]) -> float:
    return fnum(row.get("ask_prob"))


def p_side(row: dict[str, Any]) -> float:
    return fnum(row.get("p_side"))


def seconds_to_close(row: dict[str, Any]) -> float:
    return fnum(row.get("seconds_to_close"))


def raw_score(row: dict[str, Any]) -> float:
    return fnum(raw_edge(row), -999.0)


def source_counts(rows: list[dict[str, Any]]) -> dict[str, int]:
    return dict(Counter(source(row) for row in rows))


def selected_by_market(rows: list[dict[str, Any]], ranker: Callable[[dict[str, Any]], tuple[Any, ...]]) -> list[dict[str, Any]]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        if market(row):
            grouped[market(row)].append(row)
    return [max(items, key=ranker) for items in grouped.values()]


def rank_raw(row: dict[str, Any]) -> tuple[float, float, float, str]:
    return (raw_score(row), abs_d(row), -recross(row), str(row.get("ts_wall") or ""))


def mechanism_tags(row: dict[str, Any]) -> list[str]:
    tags: list[str] = []
    if source(row) != "approved_entry":
        tags.append("source_quality_error")
    if abs_d(row) < 0.65:
        tags.append("weak_boundary_distance_lt065")
    elif abs_d(row) < 0.85:
        tags.append("moderate_boundary_distance_lt085")
    if ask(row) < 0.50:
        tags.append("cheap_tail_ask_lt050")
    elif ask(row) < 0.65:
        tags.append("mid_ask_lt065")
    if p_side(row) < 0.75:
        tags.append("low_p_side_lt075")
    elif p_side(row) < 0.85:
        tags.append("moderate_p_side_lt085")
    if raw_score(row) < 0.05:
        tags.append("thin_raw_edge_lt005")
    if recross(row) > 0.30:
        tags.append("higher_recross_gt030")
    if seconds_to_close(row) < 240.0:
        tags.append("early_observation_stc_lt240")
    if fnum(row.get("eligible_depth")) < 100.0:
        tags.append("thin_depth_lt100")
    if fnum(row.get("book_age_ms")) > 1000.0 or fnum(row.get("btc_age_ms")) > 1000.0:
        tags.append("stale_feed_age_gt1000")
    if not tags:
        tags.append("clean_or_unclassified")
    return tags


def row_view(row: dict[str, Any], anchor_keys: set[tuple[str, str]] | None = None) -> dict[str, Any]:
    anchor_keys = anchor_keys or set()
    weight = repair_weight(POLICY, row, anchor_keys)
    return {
        "market": market(row),
        "side": row.get("side"),
        "source": source(row),
        "reason": row.get("reason"),
        "net_cents": net(row),
        "weight": weight,
        "weighted_net_cents": weight * net(row),
        "raw_edge": raw_edge(row),
        "p_side": row.get("p_side"),
        "ask_prob": row.get("ask_prob"),
        "abs_d_sigma": row.get("abs_d_sigma"),
        "recross_hazard_score": row.get("recross_hazard_score"),
        "seconds_to_close": row.get("seconds_to_close"),
        "eligible_depth": row.get("eligible_depth"),
        "book_age_ms": row.get("book_age_ms"),
        "btc_age_ms": row.get("btc_age_ms"),
        "side_won": row.get("side_won"),
        "anchor_row": row_key(row) in anchor_keys,
        "tags": mechanism_tags(row),
    }


def class_attribution(rows: list[dict[str, Any]], anchor_keys: set[tuple[str, str]]) -> dict[str, Any]:
    counts: Counter[str] = Counter()
    weighted_net: Counter[str] = Counter()
    raw_net: Counter[str] = Counter()
    losses: Counter[str] = Counter()
    wins: Counter[str] = Counter()
    for row in rows:
        weight = repair_weight(POLICY, row, anchor_keys)
        for tag in mechanism_tags(row):
            counts[tag] += 1
            weighted_net[tag] += weight * net(row)
            raw_net[tag] += net(row)
            if net(row) < 0:
                losses[tag] += 1
            elif net(row) > 0:
                wins[tag] += 1
    return {
        "counts": dict(counts),
        "weighted_net_cents": dict(weighted_net),
        "raw_net_cents": dict(raw_net),
        "wins": dict(wins),
        "losses": dict(losses),
    }


def same_market_alternates(
    all_rows: list[dict[str, Any]],
    selected_sources: list[dict[str, Any]],
    anchor_keys: set[tuple[str, str]],
) -> list[dict[str, Any]]:
    by_market: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in all_rows:
        if passes_rule(row, REPAIR_RULE):
            by_market[market(row)].append(row)
    out = []
    for row in selected_sources:
        approved = [alt for alt in by_market.get(market(row), []) if source(alt) == "approved_entry"]
        approved.sort(key=rank_raw, reverse=True)
        out.append({
            "selected": row_view(row, anchor_keys),
            "approved_alternates": [row_view(alt, anchor_keys) for alt in approved[:5]],
            "same_market_approved_exists": bool(approved),
        })
    return out


def source_oracle_replacement(
    all_rows: list[dict[str, Any]],
    selected: list[dict[str, Any]],
    anchor_keys: set[tuple[str, str]],
    denominator: int,
) -> dict[str, Any]:
    selected_markets = {market(row) for row in selected}
    selected_sources = [row for row in selected if source(row) != "approved_entry"]
    selected_sources.sort(key=lambda row: (repair_weight(POLICY, row, anchor_keys) * net(row), net(row)))
    omitted_approved = [
        row for row in selected_by_market([row for row in all_rows if passes_rule(row, REPAIR_RULE) and source(row) == "approved_entry"], rank_raw)
        if market(row) not in selected_markets
    ]
    omitted_approved.sort(key=lambda row: repair_weight(POLICY, row, anchor_keys) * net(row), reverse=True)

    variants = []
    for n in range(1, min(len(selected_sources), len(omitted_approved)) + 1):
        drop_markets = {market(row) for row in selected_sources[:n]}
        candidate = [row for row in selected if market(row) not in drop_markets] + omitted_approved[:n]
        summary = summarize_policy("source_oracle", POLICY, candidate, denominator, anchor_keys)
        variants.append({
            "replacements": n,
            "dropped": [row_view(row, anchor_keys) for row in selected_sources[:n]],
            "added": [row_view(row, anchor_keys) for row in omitted_approved[:n]],
            "summary": summary,
        })
    first_clear = next((row for row in variants if not row["summary"].get("blockers")), None)
    return {
        "omitted_approved_available": len(omitted_approved),
        "selected_source_rows": len(selected_sources),
        "first_oracle_clear": first_clear,
        "variants": variants[:8],
        "note": "Non-deployable source-label oracle bound; source labels are not observable live selection features.",
    }


def evaluate_lane(label: str, freeze_ts: str, surfaces_fn: Callable[[str], Any]) -> dict[str, Any]:
    all_rows, _, denominator_raw = surfaces_fn(freeze_ts)
    denominator = int(denominator_raw or 0)
    anchor_rows = selected_by_market([row for row in all_rows if passes_rule(row, ANCHOR_RULE)], rank_raw)
    selected = selected_by_market([row for row in all_rows if passes_rule(row, REPAIR_RULE)], rank_raw)
    anchor_keys = {row_key(row) for row in anchor_rows}
    selected_sources = [row for row in selected if source(row) != "approved_entry"]
    selected_approved = [row for row in selected if source(row) == "approved_entry"]
    summary = summarize_policy(label, POLICY, selected, denominator, anchor_keys)
    source_summary = summarize_policy(label, POLICY, selected_sources, denominator, anchor_keys)
    approved_summary = summarize_policy(label, POLICY, selected_approved, denominator, anchor_keys)
    return {
        "lane": label,
        "freeze_ts_utc": freeze_ts,
        "future_denominator": denominator,
        "anchor_rule": rule_name(ANCHOR_RULE),
        "repair_rule": rule_name(REPAIR_RULE),
        "selected_summary": summary,
        "approved_selected_summary": approved_summary,
        "source_selected_summary": source_summary,
        "source_counts": source_counts(selected),
        "mechanism_attribution_all": class_attribution(selected, anchor_keys),
        "mechanism_attribution_source_only": class_attribution(selected_sources, anchor_keys),
        "source_rows": sorted([row_view(row, anchor_keys) for row in selected_sources], key=lambda row: row["weighted_net_cents"]),
        "approved_rows": sorted([row_view(row, anchor_keys) for row in selected_approved], key=lambda row: row["weighted_net_cents"]),
        "same_market_alternates": same_market_alternates(all_rows, selected_sources, anchor_keys),
        "source_oracle_replacement": source_oracle_replacement(all_rows, selected, anchor_keys, denominator),
    }


def build_report() -> dict[str, Any]:
    state = load_or_create_state()
    freeze_ts = str(state["freeze_ts_utc"])
    report = {
        "generated_at_utc": utc_now_iso(),
        "freeze_ts_utc": freeze_ts,
        "purpose": "Explain the source-quality blocker for the near-gate feature-gate size-shrink branch.",
        "lanes": [
            evaluate_lane("post_feature_freeze_entry", freeze_ts, entry_surfaces),
            evaluate_lane("post_feature_freeze_bridge", freeze_ts, bridge_surfaces),
        ],
    }
    report["interpretation"] = interpretation(report)
    return report


def interpretation(report: dict[str, Any]) -> list[str]:
    notes = [
        "Source labels are used here only for blocker attribution and non-deployable oracle bounds.",
    ]
    for lane in report.get("lanes") or []:
        summary = lane.get("selected_summary") or {}
        source_summary = lane.get("source_selected_summary") or {}
        oracle = lane.get("source_oracle_replacement") or {}
        first = oracle.get("first_oracle_clear")
        if first:
            first_note = (
                f"A source-label oracle would clear gates after {first.get('replacements')} replacement(s), "
                f"with net {(first.get('summary') or {}).get('weighted_net_cents')}c."
            )
        else:
            first_note = "Even the limited source-label replacement oracle did not clear all gates."
        notes.append(
            f"{lane.get('lane')}: selected net {summary.get('weighted_net_cents')}c, "
            f"row recon {summary.get('row_reconstructed_share')}; source-only weighted net "
            f"{source_summary.get('weighted_net_cents')}c on {source_summary.get('entries')} rows. {first_note}"
        )
    return notes


def fmt(value: Any) -> str:
    if value is None:
        return "n/a"
    if isinstance(value, float):
        return f"{value:.3f}"
    return str(value)


def write_md(report: dict[str, Any]) -> None:
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8")
    lines = [
        "# v28 Feature-Gate Source Blocker Mechanism",
        "",
        "Research-only; no live bot changes or orders.",
        "",
        f"- Generated UTC: `{report.get('generated_at_utc')}`",
        f"- Feature-gate freeze UTC: `{report.get('freeze_ts_utc')}`",
        "",
        "## Interpretation",
        "",
    ]
    lines.extend(f"- {note}" for note in report.get("interpretation") or [])
    for lane in report.get("lanes") or []:
        selected = lane.get("selected_summary") or {}
        source_selected = lane.get("source_selected_summary") or {}
        approved_selected = lane.get("approved_selected_summary") or {}
        oracle = lane.get("source_oracle_replacement") or {}
        lines.extend([
            "",
            f"## {lane.get('lane')}",
            "",
            f"- Selected: `{selected.get('entries')}/{lane.get('future_denominator')}` rows, W/L `{selected.get('wins')}/{selected.get('losses')}`, weighted net `{fmt(selected.get('weighted_net_cents'))}c`, row recon `{fmt(selected.get('row_reconstructed_share'))}`",
            f"- Approved selected: `{approved_selected.get('entries')}` rows, weighted net `{fmt(approved_selected.get('weighted_net_cents'))}c`",
            f"- Source selected: `{source_selected.get('entries')}` rows, weighted net `{fmt(source_selected.get('weighted_net_cents'))}c`",
            f"- Same-market source rows with approved alternates: `{sum(1 for row in lane.get('same_market_alternates') or [] if row.get('same_market_approved_exists'))}`",
            f"- Omitted approved markets available to oracle: `{oracle.get('omitted_approved_available')}`",
            "",
            "### Source Mechanism Tags",
            "",
            "| tag | count | W/L | weighted net |",
            "|---|---:|---:|---:|",
        ])
        mech = lane.get("mechanism_attribution_source_only") or {}
        counts = mech.get("counts") or {}
        wins = mech.get("wins") or {}
        losses = mech.get("losses") or {}
        weighted = mech.get("weighted_net_cents") or {}
        for tag, count in sorted(counts.items(), key=lambda item: (-item[1], item[0])):
            lines.append(f"| {tag} | {count} | {wins.get(tag, 0)}/{losses.get(tag, 0)} | {fmt(weighted.get(tag))} |")
        lines.extend([
            "",
            "### Worst Source Rows",
            "",
            "| market | side | reason | net | weight | weighted | tags |",
            "|---|---|---|---:|---:|---:|---|",
        ])
        for row in (lane.get("source_rows") or [])[:10]:
            lines.append(
                f"| {row.get('market')} | {row.get('side')} | {row.get('reason')} | {fmt(row.get('net_cents'))} | "
                f"{fmt(row.get('weight'))} | {fmt(row.get('weighted_net_cents'))} | {', '.join(row.get('tags') or [])} |"
            )
        first = oracle.get("first_oracle_clear")
        if first:
            summ = first.get("summary") or {}
            lines.extend([
                "",
                "### Oracle Bound",
                "",
                f"- First source-label oracle clear uses `{first.get('replacements')}` replacement(s).",
                f"- Oracle summary: entries `{summ.get('entries')}`, W/L `{summ.get('wins')}/{summ.get('losses')}`, weighted net `{fmt(summ.get('weighted_net_cents'))}c`, row recon `{fmt(summ.get('row_reconstructed_share'))}`, blockers `{summ.get('blockers')}`.",
            ])
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    write_md(build_report())


if __name__ == "__main__":
    main()
