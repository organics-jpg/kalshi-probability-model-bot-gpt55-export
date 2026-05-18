"""Strict-forward raw03-vs-raw05 autopsy for boundary-clock feature gate.

Research-only; no live bot changes or orders.

The compact feature-gate status says the clean raw05 lane is under-covered
while the broad raw03 lane reaches or nearly reaches target coverage by taking
too much reconstructed/rejected-actionable exposure. This probe inspects the
strict post-freeze marginal rows added by raw03 versus raw05.
"""
from __future__ import annotations

import json
import math
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

from probe_v28_boundary_clock_feature_gate_candidate import (
    RULES,
    STATE_JSON,
    as_float,
    load_json,
    market,
    passes,
    raw_edge,
    recross,
    source,
)
from probe_v28_boundary_clock_feature_gate_quick_status import best_per_market, gate_gap
from probe_v28_coverage_repair_pool_diagnostic import COVERAGE_FLOOR, row_net_after_fee, summarize
from probe_v28_frozen_boundary_clock_fv_entry_bridge import future_surfaces as bridge_surfaces
from probe_v28_frozen_boundary_clock_repair_entry import future_surfaces as entry_surfaces


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
LIVE_SUMMARY_JSON = ROOT / "stats" / "live_mushroom_v28_size2" / "summary.json"
OUT_JSON = OUT_DIR / "v28_feature_gate_raw03_vs_raw05_autopsy_latest.json"
OUT_MD = OUT_DIR / "v28_feature_gate_raw03_vs_raw05_autopsy_latest.md"

RAW03 = "raw03_recross70_abs075"
RAW05 = "raw05_recross60_abs085"
MAX_RECON_SHARE = 0.35
MIN_CUSHION_CENTS = 300.0


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def net(row: dict[str, Any]) -> float:
    return float(row_net_after_fee(row) or 0.0)


def is_settled(row: dict[str, Any]) -> bool:
    return row.get("side_won") is not None


def is_approved(row: dict[str, Any]) -> bool:
    return source(row) == "approved_entry"


def reconstructed_share(rows: list[dict[str, Any]]) -> float | None:
    if not rows:
        return None
    return sum(1 for row in rows if not is_approved(row)) / len(rows)


def source_counts(rows: list[dict[str, Any]]) -> dict[str, int]:
    return dict(Counter(source(row) for row in rows))


def feature_tags(row: dict[str, Any]) -> list[str]:
    tags: list[str] = []
    edge = raw_edge(row)
    row_recross = recross(row)
    abs_d = as_float(row.get("abs_d_sigma"))
    ask = as_float(row.get("ask_prob"))
    if edge is not None:
        if edge < 0.05:
            tags.append("thin_raw_edge_03_05")
        elif edge < 0.07:
            tags.append("raw_edge_05_07")
        else:
            tags.append("raw_edge_ge_07")
    if row_recross is not None:
        if row_recross > 0.60:
            tags.append("relaxed_recross_60_70")
        elif row_recross > 0.50:
            tags.append("moderate_recross_50_60")
        else:
            tags.append("low_recross_lte_50")
    if abs_d is not None:
        if abs_d < 0.85:
            tags.append("weak_abs_d_075_085")
        elif abs_d < 1.15:
            tags.append("mid_abs_d_085_115")
        else:
            tags.append("strong_abs_d_ge_115")
    if ask is not None:
        if ask < 0.65:
            tags.append("ask_below_65")
        else:
            tags.append("ask_ge_65")
    if not is_approved(row):
        tags.append("source_quality_risk")
    if is_settled(row):
        tags.append("realized_win" if net(row) > 0 else "realized_loss")
    return tags


def compact_row(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "market": market(row),
        "source": source(row),
        "side": row.get("side"),
        "side_won": row.get("side_won"),
        "net_cents": net(row) if is_settled(row) else None,
        "raw_edge": raw_edge(row),
        "recross_hazard_score": row.get("recross_hazard_score"),
        "abs_d_sigma": row.get("abs_d_sigma"),
        "ask_prob": row.get("ask_prob"),
        "tags": feature_tags(row),
    }


def summarize_subset(rows: list[dict[str, Any]], denominator: int) -> dict[str, Any]:
    summary = summarize(rows, denominator)
    return {
        **summary,
        "source_counts": source_counts(rows),
        "reconstructed_share": reconstructed_share(rows),
        "feature_tag_counts": dict(Counter(tag for row in rows for tag in feature_tags(row))),
    }


def select_rows(all_rows: list[dict[str, Any]], rule_name: str) -> list[dict[str, Any]]:
    rule = RULES[rule_name]
    return best_per_market([row for row in all_rows if passes(row, rule)])


def source_gate_clean_needed(rows: list[dict[str, Any]]) -> int:
    reconstructed = sum(1 for row in rows if not is_approved(row))
    total = len(rows)
    if total == 0 or reconstructed / total <= MAX_RECON_SHARE:
        return 0
    return max(0, math.ceil(reconstructed / MAX_RECON_SHARE - total))


def drop_reconstructed_losses_scenario(rows: list[dict[str, Any]], denominator: int) -> dict[str, Any]:
    selected = list(rows)
    dropped: list[dict[str, Any]] = []
    candidates = sorted(
        [row for row in selected if not is_approved(row) and is_settled(row)],
        key=lambda row: net(row),
    )
    for row in candidates:
        if reconstructed_share(selected) is not None and reconstructed_share(selected) <= MAX_RECON_SHARE:
            break
        selected.remove(row)
        dropped.append(row)
    summary = summarize_subset(selected, denominator)
    coverage = as_float(summary.get("coverage_pct")) or 0.0
    blockers = []
    if coverage < COVERAGE_FLOOR:
        blockers.append("coverage_too_low_after_drop")
    share = summary.get("reconstructed_share")
    if share is not None and share > MAX_RECON_SHARE:
        blockers.append("source_still_high_after_drop")
    if (as_float(summary.get("net_cents")) or 0.0) < MIN_CUSHION_CENTS:
        blockers.append("cushion_lt_3_after_drop")
    return {
        "dropped_rows": len(dropped),
        "dropped_net_cents": sum(net(row) for row in dropped if is_settled(row)),
        "dropped": [compact_row(row) for row in dropped[:12]],
        "remaining_summary": summary,
        "blockers": blockers,
    }


def evaluate_lane(
    lane: str,
    freeze_ts: str,
    surfaces_fn: Callable[[str], tuple[list[dict[str, Any]], list[dict[str, Any]], int]],
) -> dict[str, Any]:
    all_rows, _target, denominator = surfaces_fn(freeze_ts)
    raw03_rows = select_rows(all_rows, RAW03)
    raw05_rows = select_rows(all_rows, RAW05)
    raw05_markets = {market(row) for row in raw05_rows}
    raw03_markets = {market(row) for row in raw03_rows}
    marginal = [row for row in raw03_rows if market(row) not in raw05_markets]
    omitted_by_raw03 = [row for row in raw05_rows if market(row) not in raw03_markets]
    raw03_summary = summarize_subset(raw03_rows, denominator)
    raw05_summary = summarize_subset(raw05_rows, denominator)
    marginal_summary = summarize_subset(marginal, denominator)
    settled_marginal = [row for row in marginal if is_settled(row)]
    losses = [row for row in settled_marginal if net(row) < 0]
    wins = [row for row in settled_marginal if net(row) > 0]
    return {
        "lane": lane,
        "future_denominator": denominator,
        "raw03": {
            "candidate": f"{lane}_{RAW03}",
            "summary": raw03_summary,
            "gate_gap": gate_gap(raw03_summary, raw03_summary.get("reconstructed_share"), int(denominator or 0)),
            "clean_rows_needed_for_source_gate": source_gate_clean_needed(raw03_rows),
            "drop_reconstructed_losses": drop_reconstructed_losses_scenario(raw03_rows, denominator),
        },
        "raw05": {
            "candidate": f"{lane}_{RAW05}",
            "summary": raw05_summary,
            "gate_gap": gate_gap(raw05_summary, raw05_summary.get("reconstructed_share"), int(denominator or 0)),
        },
        "marginal_raw03_minus_raw05": {
            "summary": marginal_summary,
            "source_counts": source_counts(marginal),
            "wins": len(wins),
            "losses": len(losses),
            "net_cents": sum(net(row) for row in settled_marginal),
            "feature_tag_counts": dict(Counter(tag for row in marginal for tag in feature_tags(row))),
            "worst_rows": [compact_row(row) for row in sorted(settled_marginal, key=net)[:12]],
            "best_rows": [compact_row(row) for row in sorted(settled_marginal, key=net, reverse=True)[:12]],
        },
        "raw05_not_in_raw03": [compact_row(row) for row in omitted_by_raw03[:12]],
    }


def build_report() -> dict[str, Any]:
    state = load_json(STATE_JSON)
    freeze_ts = str(state.get("freeze_ts_utc") or "")
    live = load_json(LIVE_SUMMARY_JSON)
    live_cents = float(live.get("net_pnl_total_dollars") or 0.0) * 100.0
    lanes = [
        evaluate_lane("post_feature_freeze_entry", freeze_ts, entry_surfaces),
        evaluate_lane("post_feature_freeze_bridge", freeze_ts, bridge_surfaces),
    ]
    return {
        "generated_at_utc": utc_now_iso(),
        "state": state,
        "live_baseline_cents": live_cents,
        "lanes": lanes,
        "interpretation": interpretation(lanes, live_cents),
    }


def interpretation(lanes: list[dict[str, Any]], live_cents: float) -> list[str]:
    notes = ["Autopsy compares strict post-freeze raw03 broad rows to raw05 clean rows."]
    for lane in lanes:
        raw03 = lane["raw03"]
        raw05 = lane["raw05"]
        marginal = lane["marginal_raw03_minus_raw05"]
        raw03_summary = raw03["summary"]
        raw05_summary = raw05["summary"]
        notes.append(
            f"{lane['lane']}: raw03 adds {marginal['summary'].get('entries')} market rows versus raw05, "
            f"marginal net {marginal['net_cents']}c with W/L {marginal['wins']}/{marginal['losses']}; "
            f"raw03 net {raw03_summary.get('net_cents')}c vs raw05 {raw05_summary.get('net_cents')}c and live {live_cents:.0f}c."
        )
        notes.append(
            f"{lane['lane']}: raw03 source share {raw03_summary.get('reconstructed_share')} needs "
            f"{raw03.get('clean_rows_needed_for_source_gate')} clean rows; dropping reconstructed losses has blockers "
            f"{raw03['drop_reconstructed_losses'].get('blockers')}."
        )
    return notes


def fmt(value: Any) -> str:
    if value is None:
        return "None"
    if isinstance(value, float):
        return f"{value:.6f}"
    return str(value)


def write_report(report: dict[str, Any]) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8")
    lines = [
        "# v28 Feature-Gate raw03 vs raw05 Autopsy",
        "",
        "Research-only; no live bot changes or orders.",
        "",
        f"- Generated UTC: `{report.get('generated_at_utc')}`",
        f"- Feature-gate freeze UTC: `{(report.get('state') or {}).get('freeze_ts_utc')}`",
        f"- Refreshed live baseline: `{fmt(report.get('live_baseline_cents'))}c`",
        "",
        "## Interpretation",
        "",
    ]
    for note in report.get("interpretation") or []:
        lines.append(f"- {note}")
    for lane in report.get("lanes") or []:
        raw03 = lane["raw03"]
        raw05 = lane["raw05"]
        marginal = lane["marginal_raw03_minus_raw05"]
        drop = raw03["drop_reconstructed_losses"]
        lines.extend(
            [
                "",
                f"## {lane.get('lane')}",
                "",
                "| candidate | entries | settled | coverage | net c | W/L | recon share | source counts |",
                "|---|---:|---:|---:|---:|---:|---:|---|",
            ]
        )
        for label, payload in [("raw05", raw05), ("raw03", raw03), ("raw03 marginal", marginal)]:
            summary = payload.get("summary") or {}
            lines.append(
                f"| {label} | {summary.get('entries')} | {summary.get('settled')} | "
                f"{fmt(summary.get('coverage_pct'))} | {fmt(summary.get('net_cents'))} | "
                f"{summary.get('wins')}/{summary.get('losses')} | {fmt(summary.get('reconstructed_share'))} | "
                f"{summary.get('source_counts') or payload.get('source_counts')} |"
            )
        lines.extend(
            [
                "",
                f"- raw03 source/cushion gap: `{raw03.get('gate_gap')}`",
                f"- raw03 clean rows needed for source gate: `{raw03.get('clean_rows_needed_for_source_gate')}`",
                f"- Drop reconstructed losses scenario blockers: `{', '.join(drop.get('blockers') or []) or 'none'}`",
                f"- Drop reconstructed losses remaining summary: `{drop.get('remaining_summary')}`",
                f"- Marginal feature tags: `{marginal.get('feature_tag_counts')}`",
                "",
                "### Worst Marginal Rows",
                "",
                "| market | source | side | won | net c | raw edge | recross | abs d | ask | tags |",
                "|---|---|---|---:|---:|---:|---:|---:|---:|---|",
            ]
        )
        for row in marginal.get("worst_rows") or []:
            lines.append(
                f"| {row.get('market')} | {row.get('source')} | {row.get('side')} | {row.get('side_won')} | "
                f"{fmt(row.get('net_cents'))} | {fmt(row.get('raw_edge'))} | {fmt(row.get('recross_hazard_score'))} | "
                f"{fmt(row.get('abs_d_sigma'))} | {fmt(row.get('ask_prob'))} | {', '.join(row.get('tags') or [])} |"
            )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    report = build_report()
    write_report(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
