"""Source-aware frozen watch for target-coverage cluster penalties.

Research-only; no live bot changes or orders.

This tests whether the continuous cluster-penalty broad-entry idea survives
when reconstructed/rejected rows pay a soft evidence-quality penalty. The
source penalty is not a deployable live feature; it is a forward evidence
quality stress test that should later be translated back into observable
market features before any live promotion.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from probe_v28_coverage_repair_pool_diagnostic import COVERAGE_FLOOR, raw_edge, row_net_after_fee, summarize
from probe_v28_target_coverage_cluster_penalty_watch import (
    VARIANTS as CLUSTER_VARIANTS,
    adjusted_edge as cluster_adjusted_edge,
    clean_forward_rows,
    compact as base_compact,
    load_json,
    reconstructed_share,
    source_counts,
    target_freeze_ts,
)
from probe_v28_shadow_entry_policy_bakeoff import base_tradeable


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
STATE_JSON = OUT_DIR / "v28_target_cluster_penalty_source_aware_watch_state.json"
OUT_JSON = OUT_DIR / "v28_target_cluster_penalty_source_aware_watch_latest.json"
OUT_MD = OUT_DIR / "v28_target_cluster_penalty_source_aware_watch_latest.md"

MIN_SETTLED = 30
MAX_RECONSTRUCTED_SHARE = 0.35
MIN_FULL_LOSS_CUSHION = 3

SOURCE_AWARE_VARIANTS = {
    "medium_src_penalty025": {
        "cluster_variant": "cluster_penalty_medium",
        "source_penalty": 0.025,
    },
    "medium_src_penalty050": {
        "cluster_variant": "cluster_penalty_medium",
        "source_penalty": 0.050,
    },
    "medium_src_penalty100": {
        "cluster_variant": "cluster_penalty_medium",
        "source_penalty": 0.100,
    },
    "light_src_penalty050": {
        "cluster_variant": "cluster_penalty_light",
        "source_penalty": 0.050,
    },
    "heavy_src_penalty050": {
        "cluster_variant": "cluster_penalty_heavy",
        "source_penalty": 0.050,
    },
}


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def as_float(value: Any) -> float | None:
    try:
        if value is None or value == "":
            return None
        return float(value)
    except (TypeError, ValueError):
        return None


def load_or_create_state() -> dict[str, Any]:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    if STATE_JSON.exists():
        state = load_json(STATE_JSON)
        if state.get("freeze_ts_utc"):
            return state
    state = {
        "freeze_ts_utc": utc_now_iso(),
        "candidate_family": "target_cluster_penalty_source_aware_watch",
        "coverage_floor": COVERAGE_FLOOR,
        "source_quality_warning": (
            "The source penalty is a research evidence-quality stress only. "
            "It is not a deployable live-market feature."
        ),
        "variants": SOURCE_AWARE_VARIANTS,
    }
    STATE_JSON.write_text(json.dumps(state, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return state


def is_approved_entry(row: dict[str, Any]) -> bool:
    return str(row.get("source") or "") == "approved_entry"


def source_quality_penalty(row: dict[str, Any], params: dict[str, Any]) -> float:
    if is_approved_entry(row):
        return 0.0
    return float(params.get("source_penalty") or 0.0)


def source_adjusted_edge(row: dict[str, Any], params: dict[str, Any]) -> float | None:
    cluster_name = str(params.get("cluster_variant") or "")
    cluster_params = CLUSTER_VARIANTS.get(cluster_name)
    if not cluster_params:
        return None
    base = cluster_adjusted_edge(row, cluster_params)
    if base is None:
        return None
    return base - source_quality_penalty(row, params)


def ceil_entries_for_floor(denominator: int) -> int:
    if denominator <= 0:
        return 0
    return int((COVERAGE_FLOOR * denominator + 99.999999) // 100)


def selected_rows(rows: list[dict[str, Any]], denominator: int, params: dict[str, Any]) -> list[dict[str, Any]]:
    grouped: dict[str, list[dict[str, Any]]] = {}
    for row in rows:
        market = str(row.get("market") or "")
        if not market or not base_tradeable(row):
            continue
        score = source_adjusted_edge(row, params)
        if score is None:
            continue
        cluster_score = cluster_adjusted_edge(row, CLUSTER_VARIANTS[str(params["cluster_variant"])])
        enriched = {
            **row,
            "raw_edge_prob": raw_edge(row),
            "cluster_adjusted_edge": cluster_score,
            "source_adjusted_edge": score,
            "adjusted_edge": score,
            "source_quality_penalty": source_quality_penalty(row, params),
            "net_gross_cents_after_entry_fee": row_net_after_fee(row),
        }
        grouped.setdefault(market, []).append(enriched)
    best = [max(items, key=lambda item: float(item.get("source_adjusted_edge") or -999.0)) for items in grouped.values()]
    best.sort(
        key=lambda item: (
            float(item.get("source_adjusted_edge") or -999.0),
            is_approved_entry(item),
            str(item.get("ts_wall") or ""),
        ),
        reverse=True,
    )
    return best[:ceil_entries_for_floor(denominator)]


def blockers(summary: dict[str, Any], recon_share: float | None) -> list[str]:
    out: list[str] = ["source_penalty_research_only_not_live_feature"]
    settled = int(as_float(summary.get("settled")) or 0)
    coverage = as_float(summary.get("coverage_pct"))
    net_cents = as_float(summary.get("net_cents")) or 0.0
    if settled < MIN_SETTLED:
        out.append("settled_lt_30")
    if coverage is None or coverage < COVERAGE_FLOOR:
        out.append("coverage_too_low")
    if net_cents <= 0.0:
        out.append("net_not_positive")
    if recon_share is not None and recon_share > MAX_RECONSTRUCTED_SHARE:
        out.append("reconstructed_share_gt_35pct")
    if int(max(0.0, net_cents) // 100.0) < MIN_FULL_LOSS_CUSHION:
        out.append("full_loss_cushion_lt_3")
    return out


def compact(row: dict[str, Any]) -> dict[str, Any]:
    out = base_compact(row)
    out["cluster_adjusted_edge"] = row.get("cluster_adjusted_edge")
    out["source_adjusted_edge"] = row.get("source_adjusted_edge")
    out["source_quality_penalty"] = row.get("source_quality_penalty")
    return out


def evaluate_lane(label: str, freeze_ts: str) -> dict[str, Any]:
    rows, target, denominator = clean_forward_rows(freeze_ts)
    target_summary = summarize(target, denominator)
    variants = []
    for name, params in SOURCE_AWARE_VARIANTS.items():
        selected = selected_rows(rows, denominator, params)
        summary = summarize(selected, denominator)
        counts = source_counts(selected)
        share = reconstructed_share(counts)
        net_cents = float(summary.get("net_cents") or 0.0)
        variants.append(
            {
                "candidate": f"{label}_{name}",
                "params": params,
                "candidate_summary": summary,
                "target_summary": target_summary,
                "delta_vs_target_cents": net_cents - float(target_summary.get("net_cents") or 0.0),
                "source_counts": counts,
                "reconstructed_share": share,
                "full_loss_cushion_estimate": int(max(0.0, net_cents) // 100.0),
                "blockers": blockers(summary, share),
                "worst_rows": [compact(row) for row in sorted(selected, key=lambda item: row_net_after_fee(item) or 0.0)[:10]],
            }
        )
    variants.sort(
        key=lambda row: (
            row.get("reconstructed_share") if row.get("reconstructed_share") is not None else 999.0,
            len(row.get("blockers") or []),
            -float((row.get("candidate_summary") or {}).get("net_cents") or -999999.0),
        )
    )
    return {
        "lane": label,
        "freeze_ts_utc": freeze_ts,
        "future_denominator": denominator,
        "variants": variants,
    }


def build_report() -> dict[str, Any]:
    state = load_or_create_state()
    lanes = [
        evaluate_lane("diagnostic_target_window", target_freeze_ts()),
        evaluate_lane("post_source_aware_birth", str(state["freeze_ts_utc"])),
    ]
    report = {
        "generated_at_utc": utc_now_iso(),
        "state": state,
        "lanes": lanes,
    }
    report["interpretation"] = interpretation(report)
    return report


def interpretation(report: dict[str, Any]) -> list[str]:
    notes = [
        "Source-aware cluster penalties are watch-only and intentionally blocked from live promotion.",
        "The useful signal is whether target coverage, positive PnL, and <=35% reconstructed share can coexist under strict forward evidence.",
    ]
    for lane in report.get("lanes") or []:
        best = (lane.get("variants") or [{}])[0]
        summary = best.get("candidate_summary") or {}
        notes.append(
            f"{lane.get('lane')}: cleanest {best.get('candidate')} settled {summary.get('settled')}, "
            f"coverage {summary.get('coverage_pct')}%, net {summary.get('net_cents')}c, "
            f"recon {best.get('reconstructed_share')}, blockers {best.get('blockers')}."
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
        "# v28 Target Cluster-Penalty Source-Aware Watch",
        "",
        "Research-only; no live bot changes or orders.",
        "",
        f"- Generated UTC: `{report.get('generated_at_utc')}`",
        f"- Source-aware freeze UTC: `{state.get('freeze_ts_utc')}`",
        f"- Warning: `{state.get('source_quality_warning')}`",
        "",
        "## Interpretation",
        "",
    ]
    lines.extend(f"- {note}" for note in report.get("interpretation") or [])
    for lane in report.get("lanes") or []:
        lines.extend(["", f"## {lane.get('lane')}", ""])
        lines.extend([
            "| rank | candidate | settled/den | W/L | coverage | net c | delta vs target | recon | cushion | blockers |",
            "|---:|---|---:|---:|---:|---:|---:|---:|---:|---|",
        ])
        for idx, variant in enumerate(lane.get("variants") or [], start=1):
            summary = variant.get("candidate_summary") or {}
            lines.append(
                f"| {idx} | `{variant.get('candidate')}` | {summary.get('settled')}/{lane.get('future_denominator')} | "
                f"{summary.get('wins')}/{summary.get('losses')} | {fmt(summary.get('coverage_pct'))} | "
                f"{fmt(summary.get('net_cents'))} | {fmt(variant.get('delta_vs_target_cents'))} | "
                f"{fmt(variant.get('reconstructed_share'))} | {variant.get('full_loss_cushion_estimate')} | "
                f"{', '.join(variant.get('blockers') or []) or 'none'} |"
            )
        best = (lane.get("variants") or [{}])[0]
        lines.extend(["", "### Cleanest Variant Worst Rows", ""])
        lines.extend([
            "| market | source | side | won | net c | p | ask | cluster edge | source edge | source penalty | stc | abs d | recross |",
            "|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
        ])
        for row in best.get("worst_rows") or []:
            lines.append(
                f"| {row.get('market')} | {row.get('source')} | {row.get('side')} | {row.get('side_won')} | "
                f"{fmt(row.get('net_cents'))} | {fmt(row.get('p_side'))} | {fmt(row.get('ask_prob'))} | "
                f"{fmt(row.get('cluster_adjusted_edge'))} | {fmt(row.get('source_adjusted_edge'))} | "
                f"{fmt(row.get('source_quality_penalty'))} | {fmt(row.get('seconds_to_close'))} | "
                f"{fmt(row.get('abs_d_sigma'))} | {fmt(row.get('recross_hazard_score'))} |"
            )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    report = build_report()
    write_md(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
