"""Strict-row failure audit for the clean-broad feature-gate watch.

Research-only; no live bot changes or orders.

The clean-broad watch is already frozen. This probe does not create a new
candidate. It asks whether the strict post-freeze loss is an expected physical
failure of the soft boundary rule and whether nearby observable variants would
have excluded it.
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
    market,
    net,
    reconstructed_share,
    source,
    source_counts,
)
from probe_v28_boundary_clock_feature_gate_clean_broad_frontier_watch import (
    RULE as WATCH_RULE,
    RULE_NAME as WATCH_RULE_NAME,
    load_or_create_state,
)
from probe_v28_boundary_clock_feature_gate_coverage_source_frontier import passes_rule
from probe_v28_coverage_repair_pool_diagnostic import raw_edge, summarize
from probe_v28_frozen_boundary_clock_fv_entry_bridge import future_surfaces as bridge_surfaces
from probe_v28_frozen_boundary_clock_repair_entry import future_surfaces as entry_surfaces


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
OUT_JSON = OUT_DIR / "v28_clean_broad_frontier_strict_failure_audit_latest.json"
OUT_MD = OUT_DIR / "v28_clean_broad_frontier_strict_failure_audit_latest.md"

VARIANTS = {
    WATCH_RULE_NAME: WATCH_RULE,
    "raw03_recross50_abs65_ask35": {
        "raw_edge_min": 0.03,
        "recross_max": 0.50,
        "abs_d_min": 0.65,
        "ask_min": 0.35,
    },
    "raw03_recross50_abs50_ask50": {
        "raw_edge_min": 0.03,
        "recross_max": 0.50,
        "abs_d_min": 0.50,
        "ask_min": 0.50,
    },
    "raw03_recross40_abs50_ask35": {
        "raw_edge_min": 0.03,
        "recross_max": 0.40,
        "abs_d_min": 0.50,
        "ask_min": 0.35,
    },
    "raw05_recross50_abs50_ask35": {
        "raw_edge_min": 0.05,
        "recross_max": 0.50,
        "abs_d_min": 0.50,
        "ask_min": 0.35,
    },
}


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def compact_row(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "market": market(row),
        "source": source(row),
        "side": row.get("side"),
        "side_won": row.get("side_won"),
        "status": row.get("status"),
        "result": row.get("result"),
        "ts_wall": row.get("ts_wall"),
        "seconds_to_close": as_float(row.get("seconds_to_close")),
        "net_cents": net(row),
        "raw_edge": raw_edge(row),
        "recross_hazard_score": as_float(row.get("recross_hazard_score")),
        "abs_d_sigma": as_float(row.get("abs_d_sigma")),
        "ask_prob": as_float(row.get("ask_prob")),
        "mechanism_tags": mechanism_tags(row),
    }


def mechanism_tags(row: dict[str, Any]) -> list[str]:
    tags: list[str] = []
    edge = raw_edge(row)
    recross = as_float(row.get("recross_hazard_score"))
    abs_d = as_float(row.get("abs_d_sigma"))
    ask = as_float(row.get("ask_prob"))
    row_net = net(row)
    if source(row) != "approved_entry":
        tags.append("source_quality_risk")
    if row.get("side_won") is False:
        tags.append("realized_loss")
    if row_net <= 5.0:
        tags.append("thin_or_negative_net")
    if edge is not None and edge < 0.05:
        tags.append("thin_raw_edge")
    if recross is not None and recross > 0.40:
        tags.append("elevated_recross_for_clean_broad")
    if abs_d is not None and abs_d < 0.65:
        tags.append("weak_boundary_distance_abs_lt_065")
    elif abs_d is not None and abs_d < 0.85:
        tags.append("near_boundary_distance_abs_lt_085")
    if ask is not None and ask < 0.50:
        tags.append("mid_or_cheap_touch_ask_lt_050")
    return tags or ["clean_or_unclassified"]


def selected_for_rule(rows: list[dict[str, Any]], rule: dict[str, Any]) -> list[dict[str, Any]]:
    return best_per_market([row for row in rows if passes_rule(row, rule)])


def evaluate_variant(rows: list[dict[str, Any]], denominator: int, name: str, rule: dict[str, Any]) -> dict[str, Any]:
    selected = selected_for_rule(rows, rule)
    summary = summarize(selected, denominator)
    counts = source_counts(selected)
    share = reconstructed_share(counts)
    selected_markets = {market(row) for row in selected}
    losses = [row for row in selected if net(row) < 0]
    return {
        "rule": name,
        "rule_params": rule,
        "summary": summary,
        "source_counts": counts,
        "reconstructed_share": share,
        "full_loss_cushion_estimate": int(max(0.0, float(summary.get("net_cents") or 0.0)) // 100.0),
        "blockers": blockers(summary, share),
        "loss_count": len(losses),
        "loss_net_cents": sum(net(row) for row in losses),
        "loss_tag_counts": dict(Counter(tag for row in losses for tag in mechanism_tags(row))),
        "selected_markets": sorted(selected_markets),
    }


def evaluate_lane(label: str, freeze_ts: str, surfaces_fn: Any) -> dict[str, Any]:
    rows, _, denominator_raw = surfaces_fn(freeze_ts)
    denominator = int(denominator_raw or 0)
    variants = [
        evaluate_variant(rows, denominator, name, rule)
        for name, rule in VARIANTS.items()
    ]
    base = next((row for row in variants if row.get("rule") == WATCH_RULE_NAME), {})
    base_selected = selected_for_rule(rows, WATCH_RULE)
    strict_losses = [row for row in base_selected if net(row) < 0]
    loss_membership = []
    for row in strict_losses:
        row_market = market(row)
        loss_membership.append(
            {
                "row": compact_row(row),
                "variant_inclusion": {
                    variant["rule"]: row_market in set(variant.get("selected_markets") or [])
                    for variant in variants
                },
            }
        )
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
        "future_denominator": denominator,
        "base_rule": WATCH_RULE_NAME,
        "base_summary": base.get("summary") or {},
        "base_reconstructed_share": base.get("reconstructed_share"),
        "base_blockers": base.get("blockers") or [],
        "variants": variants,
        "strict_loss_rows": loss_membership,
    }


def interpretation(lanes: list[dict[str, Any]]) -> list[str]:
    notes = [
        "This is a strict-row failure audit, not a new candidate freeze.",
    ]
    for lane in lanes:
        base = lane.get("base_summary") or {}
        losses = lane.get("strict_loss_rows") or []
        variants = lane.get("variants") or []
        best_variant = variants[0] if variants else {}
        notes.append(
            f"{lane.get('lane')} base {lane.get('base_rule')} has {base.get('settled')} settled, "
            f"coverage {base.get('coverage_pct')}%, net {base.get('net_cents')}c, "
            f"strict losses {len(losses)}; best nearby variant {best_variant.get('rule')} has "
            f"{(best_variant.get('summary') or {}).get('settled')} settled and "
            f"{(best_variant.get('summary') or {}).get('net_cents')}c."
        )
        if losses:
            tags = Counter(
                tag
                for loss in losses
                for tag in ((loss.get("row") or {}).get("mechanism_tags") or [])
            )
            notes.append(f"{lane.get('lane')} strict loss tags: {dict(tags)}.")
    return notes


def build_report() -> dict[str, Any]:
    state = load_or_create_state()
    freeze_ts = str(state["freeze_ts_utc"])
    lanes = [
        evaluate_lane("post_clean_broad_freeze_entry", freeze_ts, entry_surfaces),
        evaluate_lane("post_clean_broad_freeze_bridge", freeze_ts, bridge_surfaces),
    ]
    return {
        "generated_at_utc": utc_now_iso(),
        "freeze_ts_utc": freeze_ts,
        "watch_rule": WATCH_RULE_NAME,
        "purpose": "Diagnose strict clean-broad watch losses against nearby observable variants.",
        "lanes": lanes,
        "interpretation": interpretation(lanes),
    }


def fmt(value: Any) -> str:
    if value is None:
        return "None"
    if isinstance(value, float):
        return f"{value:.6f}"
    return str(value)


def write_md(report: dict[str, Any]) -> None:
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8")
    lines = [
        "# v28 Clean-Broad Frontier Strict Failure Audit",
        "",
        "Research-only; no live bot changes or orders.",
        "",
        f"- Generated UTC: `{report.get('generated_at_utc')}`",
        f"- Watch freeze UTC: `{report.get('freeze_ts_utc')}`",
        f"- Watch rule: `{report.get('watch_rule')}`",
        "",
        "## Interpretation",
        "",
    ]
    lines.extend(f"- {note}" for note in report.get("interpretation") or [])
    for lane in report.get("lanes") or []:
        lines.extend(["", f"## {lane.get('lane')}", ""])
        lines.extend(
            [
                "| rule | settled/den | W/L | coverage | net c | recon | cushion | losses/net | blockers |",
                "|---|---:|---:|---:|---:|---:|---:|---:|---|",
            ]
        )
        for variant in lane.get("variants") or []:
            summary = variant.get("summary") or {}
            lines.append(
                f"| {variant.get('rule')} | {summary.get('settled')}/{lane.get('future_denominator')} | "
                f"{summary.get('wins')}/{summary.get('losses')} | {fmt(summary.get('coverage_pct'))} | "
                f"{fmt(summary.get('net_cents'))} | {fmt(variant.get('reconstructed_share'))} | "
                f"{variant.get('full_loss_cushion_estimate')} | "
                f"{variant.get('loss_count')}/{fmt(variant.get('loss_net_cents'))} | "
                f"{', '.join(variant.get('blockers') or []) or 'none'} |"
            )
        lines.extend(["", "### Strict Loss Rows", ""])
        lines.extend(
            [
                "| market | source | side | net c | edge | recross | abs d | ask | tags | included by variants |",
                "|---|---|---|---:|---:|---:|---:|---:|---|---|",
            ]
        )
        for loss in lane.get("strict_loss_rows") or []:
            row = loss.get("row") or {}
            included = ", ".join(
                f"{name}:{value}"
                for name, value in (loss.get("variant_inclusion") or {}).items()
            )
            lines.append(
                f"| {row.get('market')} | {row.get('source')} | {row.get('side')} | "
                f"{fmt(row.get('net_cents'))} | {fmt(row.get('raw_edge'))} | "
                f"{fmt(row.get('recross_hazard_score'))} | {fmt(row.get('abs_d_sigma'))} | "
                f"{fmt(row.get('ask_prob'))} | {', '.join(row.get('mechanism_tags') or [])} | {included} |"
            )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    report = build_report()
    write_md(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
