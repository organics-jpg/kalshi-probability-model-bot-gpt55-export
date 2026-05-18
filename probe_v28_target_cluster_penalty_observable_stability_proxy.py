"""Observable stability-proxy watch for target cluster penalties.

Research-only; no live bot changes or orders.

The source-displacement audit showed that current cluster-penalty ranking often
prefers cheap, near-boundary, high-recross rows while omitted approved rows are
farther from the boundary and calmer. This probe tests that physical hypothesis
with observable market features only. Source labels are used only after
selection to audit evidence quality.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from probe_v28_coverage_repair_pool_diagnostic import COVERAGE_FLOOR, raw_edge, row_net_after_fee, summarize
from probe_v28_target_coverage_cluster_penalty_watch import (
    VARIANTS as CLUSTER_VARIANTS,
    abs_d,
    adjusted_edge as cluster_adjusted_edge,
    ask_prob,
    clean_forward_rows,
    compact as base_compact,
    load_json,
    recross,
    reconstructed_share,
    source_counts,
    target_freeze_ts,
)
from probe_v28_shadow_entry_policy_bakeoff import base_tradeable


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
STATE_JSON = OUT_DIR / "v28_target_cluster_penalty_observable_stability_proxy_state.json"
OUT_JSON = OUT_DIR / "v28_target_cluster_penalty_observable_stability_proxy_latest.json"
OUT_MD = OUT_DIR / "v28_target_cluster_penalty_observable_stability_proxy_latest.md"

MIN_SETTLED = 30
MAX_RECONSTRUCTED_SHARE = 0.35
MIN_FULL_LOSS_CUSHION = 3

OBSERVABLE_VARIANTS = {
    "medium_far_calm_light": {
        "cluster_variant": "cluster_penalty_medium",
        "far_boundary_bonus": 0.025,
        "calm_recross_bonus": 0.020,
        "cheap_unstable_penalty": 0.040,
        "paid_stability_bonus": 0.000,
    },
    "medium_far_calm_medium": {
        "cluster_variant": "cluster_penalty_medium",
        "far_boundary_bonus": 0.045,
        "calm_recross_bonus": 0.035,
        "cheap_unstable_penalty": 0.070,
        "paid_stability_bonus": 0.000,
    },
    "medium_paid_stable": {
        "cluster_variant": "cluster_penalty_medium",
        "far_boundary_bonus": 0.040,
        "calm_recross_bonus": 0.030,
        "cheap_unstable_penalty": 0.050,
        "paid_stability_bonus": 0.020,
    },
    "heavy_far_calm": {
        "cluster_variant": "cluster_penalty_heavy",
        "far_boundary_bonus": 0.060,
        "calm_recross_bonus": 0.045,
        "cheap_unstable_penalty": 0.090,
        "paid_stability_bonus": 0.000,
    },
    "light_paid_stable": {
        "cluster_variant": "cluster_penalty_light",
        "far_boundary_bonus": 0.035,
        "calm_recross_bonus": 0.030,
        "cheap_unstable_penalty": 0.050,
        "paid_stability_bonus": 0.025,
    },
}


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def as_float(value: Any) -> float | None:
    if value is None or value == "":
        return None
    try:
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
        "candidate_family": "target_cluster_penalty_observable_stability_proxy",
        "coverage_floor": COVERAGE_FLOOR,
        "physics": (
            "Prefer rows farther from the settlement boundary with calmer recross behavior, "
            "and penalize cheap near-boundary churn that can look like false raw edge."
        ),
        "source_label_use": "audit_only_not_used_for_selection",
        "variants": OBSERVABLE_VARIANTS,
    }
    STATE_JSON.write_text(json.dumps(state, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return state


def far_boundary_score(row: dict[str, Any]) -> float:
    return min(1.0, max(0.0, abs_d(row) / 1.20))


def calm_recross_score(row: dict[str, Any]) -> float:
    return max(0.0, (0.60 - recross(row)) / 0.60)


def cheap_unstable_score(row: dict[str, Any]) -> float:
    cheap = max(0.0, (0.45 - ask_prob(row)) / 0.45)
    near = max(0.0, (0.65 - abs_d(row)) / 0.65)
    churn = min(1.0, recross(row) / 0.75)
    return cheap * near * churn


def paid_stability_score(row: dict[str, Any]) -> float:
    paid = min(1.0, max(0.0, (ask_prob(row) - 0.55) / 0.35))
    return paid * far_boundary_score(row) * calm_recross_score(row)


def observable_adjusted_edge(row: dict[str, Any], params: dict[str, Any]) -> float | None:
    cluster_name = str(params.get("cluster_variant") or "")
    cluster_params = CLUSTER_VARIANTS.get(cluster_name)
    if not cluster_params:
        return None
    base = cluster_adjusted_edge(row, cluster_params)
    if base is None:
        return None
    return (
        base
        + float(params.get("far_boundary_bonus") or 0.0) * far_boundary_score(row)
        + float(params.get("calm_recross_bonus") or 0.0) * calm_recross_score(row)
        + float(params.get("paid_stability_bonus") or 0.0) * paid_stability_score(row)
        - float(params.get("cheap_unstable_penalty") or 0.0) * cheap_unstable_score(row)
    )


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
        score = observable_adjusted_edge(row, params)
        if score is None:
            continue
        cluster_name = str(params["cluster_variant"])
        cluster_score = cluster_adjusted_edge(row, CLUSTER_VARIANTS[cluster_name])
        enriched = {
            **row,
            "raw_edge_prob": raw_edge(row),
            "cluster_adjusted_edge": cluster_score,
            "observable_adjusted_edge": score,
            "adjusted_edge": score,
            "far_boundary_score": far_boundary_score(row),
            "calm_recross_score": calm_recross_score(row),
            "cheap_unstable_score": cheap_unstable_score(row),
            "paid_stability_score": paid_stability_score(row),
            "net_gross_cents_after_entry_fee": row_net_after_fee(row),
        }
        grouped.setdefault(market, []).append(enriched)
    best = [max(items, key=lambda item: float(item.get("observable_adjusted_edge") or -999.0)) for items in grouped.values()]
    best.sort(key=lambda item: (float(item.get("observable_adjusted_edge") or -999.0), str(item.get("ts_wall") or "")), reverse=True)
    return best[:ceil_entries_for_floor(denominator)]


def blockers(summary: dict[str, Any], recon_share: float | None) -> list[str]:
    out: list[str] = []
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


def runway(summary: dict[str, Any], counts: dict[str, int], recon_share: float | None) -> dict[str, Any]:
    settled = int(as_float(summary.get("settled")) or 0)
    net_cents = as_float(summary.get("net_cents")) or 0.0
    total = sum(int(value or 0) for value in counts.values())
    approved = int(counts.get("approved_entry") or 0)
    max_recon = int(MAX_RECONSTRUCTED_SHARE * total)
    current_recon = total - approved
    clean_needed = 0
    if total > 0 and recon_share is not None and recon_share > MAX_RECONSTRUCTED_SHARE:
        # Solve current_recon / (total + x) <= MAX_RECONSTRUCTED_SHARE.
        clean_needed = int(max(0.0, (current_recon / MAX_RECONSTRUCTED_SHARE) - total) + 0.999999)
    return {
        "settled_rows_needed_for_sample": max(0, MIN_SETTLED - settled),
        "clean_approved_rows_needed_for_source_gate": clean_needed,
        "net_cents_needed_for_cushion3": max(0.0, MIN_FULL_LOSS_CUSHION * 100.0 - max(0.0, net_cents)),
        "current_reconstructed_rows": current_recon,
        "current_approved_rows": approved,
        "current_max_reconstructed_rows_at_gate_floor": max_recon,
    }


def compact(row: dict[str, Any]) -> dict[str, Any]:
    out = base_compact(row)
    out["cluster_adjusted_edge"] = row.get("cluster_adjusted_edge")
    out["observable_adjusted_edge"] = row.get("observable_adjusted_edge")
    out["far_boundary_score"] = row.get("far_boundary_score")
    out["calm_recross_score"] = row.get("calm_recross_score")
    out["cheap_unstable_score"] = row.get("cheap_unstable_score")
    out["paid_stability_score"] = row.get("paid_stability_score")
    return out


def evaluate_lane(label: str, freeze_ts: str) -> dict[str, Any]:
    rows, target, denominator = clean_forward_rows(freeze_ts)
    target_summary = summarize(target, denominator)
    variants = []
    for name, params in OBSERVABLE_VARIANTS.items():
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
                "runway": runway(summary, counts, share),
                "blockers": blockers(summary, share),
                "worst_rows": [compact(row) for row in sorted(selected, key=lambda item: row_net_after_fee(item) or 0.0)[:10]],
            }
        )
    variants.sort(
        key=lambda row: (
            len(row.get("blockers") or []),
            row.get("reconstructed_share") if row.get("reconstructed_share") is not None else 999.0,
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
        evaluate_lane("post_observable_proxy_birth", str(state["freeze_ts_utc"])),
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
        "This watch uses only observable market features for selection; source labels are audit-only.",
        "Promotion still requires strict post-birth rows, positive PnL, broad coverage, <=35% reconstructed share, and full-loss cushion.",
    ]
    for lane in report.get("lanes") or []:
        best = (lane.get("variants") or [{}])[0]
        summary = best.get("candidate_summary") or {}
        notes.append(
            f"{lane.get('lane')}: best {best.get('candidate')} settled {summary.get('settled')}, "
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
        "# v28 Target Cluster-Penalty Observable Stability Proxy",
        "",
        "Research-only; no live bot changes or orders.",
        "",
        f"- Generated UTC: `{report.get('generated_at_utc')}`",
        f"- Observable proxy freeze UTC: `{state.get('freeze_ts_utc')}`",
        f"- Source label use: `{state.get('source_label_use')}`",
        f"- Physics: {state.get('physics')}",
        "",
        "## Interpretation",
        "",
    ]
    lines.extend(f"- {note}" for note in report.get("interpretation") or [])
    for lane in report.get("lanes") or []:
        lines.extend(["", f"## {lane.get('lane')}", ""])
        lines.extend([
            "| rank | candidate | settled/den | W/L | coverage | net c | delta vs target | recon | cushion | rows/clean/cushion needed | blockers |",
            "|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---|",
        ])
        for idx, variant in enumerate(lane.get("variants") or [], start=1):
            summary = variant.get("candidate_summary") or {}
            run = variant.get("runway") or {}
            lines.append(
                f"| {idx} | `{variant.get('candidate')}` | {summary.get('settled')}/{lane.get('future_denominator')} | "
                f"{summary.get('wins')}/{summary.get('losses')} | {fmt(summary.get('coverage_pct'))} | "
                f"{fmt(summary.get('net_cents'))} | {fmt(variant.get('delta_vs_target_cents'))} | "
                f"{fmt(variant.get('reconstructed_share'))} | {variant.get('full_loss_cushion_estimate')} | "
                f"{run.get('settled_rows_needed_for_sample')}/{run.get('clean_approved_rows_needed_for_source_gate')}/{fmt(run.get('net_cents_needed_for_cushion3'))}c | "
                f"{', '.join(variant.get('blockers') or []) or 'none'} |"
            )
        best = (lane.get("variants") or [{}])[0]
        lines.extend(["", "### Best Variant Worst Rows", ""])
        lines.extend([
            "| market | source | side | won | net c | p | ask | cluster edge | observable edge | far | calm | cheap unstable | paid stable | abs d | recross |",
            "|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
        ])
        for row in best.get("worst_rows") or []:
            lines.append(
                f"| {row.get('market')} | {row.get('source')} | {row.get('side')} | {row.get('side_won')} | "
                f"{fmt(row.get('net_cents'))} | {fmt(row.get('p_side'))} | {fmt(row.get('ask_prob'))} | "
                f"{fmt(row.get('cluster_adjusted_edge'))} | {fmt(row.get('observable_adjusted_edge'))} | "
                f"{fmt(row.get('far_boundary_score'))} | {fmt(row.get('calm_recross_score'))} | "
                f"{fmt(row.get('cheap_unstable_score'))} | {fmt(row.get('paid_stability_score'))} | "
                f"{fmt(row.get('abs_d_sigma'))} | {fmt(row.get('recross_hazard_score'))} |"
            )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    report = build_report()
    write_md(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
