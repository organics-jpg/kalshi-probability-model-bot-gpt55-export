"""Frozen watch for target-coverage cluster-penalty entry ranking.

Research-only; no live bot changes or orders.

This turns the mutually exclusive target-loss clusters into continuous penalties
instead of hard skip rules. The rule ranks tradeable rows by:

    raw_edge - early_no_penalty - recross_penalty - thin_edge_penalty

and selects the best row per market until the broad coverage floor is met.
Diagnostic rows are only mechanism evidence; promotion evidence must come from
the post-cluster-penalty birth window.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from probe_v28_coverage_repair_pool_diagnostic import COVERAGE_FLOOR, raw_edge, row_net_after_fee, summarize
from probe_v28_frozen_forward_candidates import market_timing, parse_ts
from probe_v28_raw_entry_coverage_valve import selected_base_rows
from probe_v28_rmt_regime_diagnostic import attach_regime_rows
from probe_v28_shadow_entry_policy_bakeoff import base_tradeable, observation_pool
from probe_v28_state_aware_fv_candidates import enrich_state
from probe_v28_target_coverage_fv_overlay_validator import STATE_JSON as TARGET_STATE_JSON, apply_policy


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
STATE_JSON = OUT_DIR / "v28_target_coverage_cluster_penalty_watch_state.json"
OUT_JSON = OUT_DIR / "v28_target_coverage_cluster_penalty_watch_latest.json"
OUT_MD = OUT_DIR / "v28_target_coverage_cluster_penalty_watch_latest.md"

POLICY = "raw_p50_turbulence_valve_edge4_p60_recross75_near25"
MIN_SETTLED = 30
MAX_RECONSTRUCTED_SHARE = 0.35
MIN_FULL_LOSS_CUSHION = 3

VARIANTS = {
    "cluster_penalty_light": {
        "early_no_lambda": 0.06,
        "recross_lambda": 0.05,
        "thin_edge_lambda": 0.05,
    },
    "cluster_penalty_medium": {
        "early_no_lambda": 0.10,
        "recross_lambda": 0.08,
        "thin_edge_lambda": 0.08,
    },
    "cluster_penalty_heavy": {
        "early_no_lambda": 0.15,
        "recross_lambda": 0.12,
        "thin_edge_lambda": 0.12,
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
        "base_policy": POLICY,
        "candidate_family": "target_coverage_cluster_penalty_watch",
        "coverage_floor": COVERAGE_FLOOR,
        "physics": (
            "Penalize early NO near-boundary decay, high-recross near-boundary instability, "
            "and high-confidence thin-edge rows continuously instead of using hard exclusions."
        ),
        "variants": VARIANTS,
    }
    STATE_JSON.write_text(json.dumps(state, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return state


def target_freeze_ts() -> str:
    state = load_json(TARGET_STATE_JSON)
    return str(state.get("source_coverage_freeze_ts") or state.get("freeze_ts") or utc_now_iso())


def probability(row: dict[str, Any]) -> float | None:
    return as_float(row.get("p_side") if row.get("p_side") is not None else row.get("p_raw"))


def seconds_to_close(row: dict[str, Any]) -> float | None:
    for key in ("seconds_to_close", "stc", "seconds_to_expiry"):
        value = as_float(row.get(key))
        if value is not None:
            return value
    return None


def recross(row: dict[str, Any]) -> float:
    return float(as_float(row.get("recross_hazard_score")) or 0.0)


def abs_d(row: dict[str, Any]) -> float:
    return float(as_float(row.get("abs_d_sigma")) or 0.0)


def ask_prob(row: dict[str, Any]) -> float:
    return float(as_float(row.get("ask_prob")) or 0.0)


def early_no_decay_score(row: dict[str, Any]) -> float:
    if str(row.get("side") or "").lower() != "no":
        return 0.0
    stc = seconds_to_close(row) or 0.0
    if stc < 720.0:
        return 0.0
    near = max(0.0, (0.45 - abs_d(row)) / 0.45)
    churn = min(1.0, recross(row) / 0.75)
    return near * churn


def recross_instability_score(row: dict[str, Any]) -> float:
    near = max(0.0, (0.35 - abs_d(row)) / 0.35)
    churn = max(0.0, (recross(row) - 0.60) / 0.60)
    return min(1.0, near * churn)


def thin_edge_price_score(row: dict[str, Any]) -> float:
    edge = raw_edge(row)
    p = probability(row)
    if edge is None or p is None or p < 0.60:
        return 0.0
    thin = max(0.0, (0.02 - edge) / 0.02)
    paid = max(0.0, (ask_prob(row) - 0.60) / 0.25)
    return min(1.0, thin * paid)


def adjusted_edge(row: dict[str, Any], params: dict[str, float]) -> float | None:
    edge = raw_edge(row)
    if edge is None:
        return None
    return (
        edge
        - float(params["early_no_lambda"]) * early_no_decay_score(row)
        - float(params["recross_lambda"]) * recross_instability_score(row)
        - float(params["thin_edge_lambda"]) * thin_edge_price_score(row)
    )


def clean_forward_rows(freeze_ts: str) -> tuple[list[dict[str, Any]], list[dict[str, Any]], int]:
    freeze_dt = parse_ts(freeze_ts)
    timing = market_timing(freeze_dt)
    forward_markets = set(timing["clean_forward_markets"])
    all_rows = enrich_state(attach_regime_rows(observation_pool()))
    all_rows = [row for row in all_rows if str(row.get("market") or "") in forward_markets]
    target = apply_policy(selected_base_rows(), POLICY)
    target = [row for row in target if str(row.get("market") or "") in forward_markets]
    return all_rows, target, len(forward_markets)


def ceil_entries_for_floor(denominator: int) -> int:
    return int((COVERAGE_FLOOR * denominator + 99.999999) // 100)


def selected_rows(rows: list[dict[str, Any]], denominator: int, params: dict[str, float]) -> list[dict[str, Any]]:
    grouped: dict[str, list[dict[str, Any]]] = {}
    for row in rows:
        market = str(row.get("market") or "")
        if not market or not base_tradeable(row):
            continue
        score = adjusted_edge(row, params)
        if score is None:
            continue
        enriched = {
            **row,
            "raw_edge_prob": raw_edge(row),
            "adjusted_edge": score,
            "cluster_penalty": (raw_edge(row) or 0.0) - score,
            "net_gross_cents_after_entry_fee": row_net_after_fee(row),
            "early_no_decay_score": early_no_decay_score(row),
            "recross_instability_score": recross_instability_score(row),
            "thin_edge_price_score": thin_edge_price_score(row),
        }
        grouped.setdefault(market, []).append(enriched)
    best = [max(items, key=lambda row: row.get("adjusted_edge") or -999.0) for items in grouped.values()]
    best.sort(key=lambda row: (float(row.get("adjusted_edge") or -999.0), str(row.get("ts_wall") or "")), reverse=True)
    return best[:ceil_entries_for_floor(denominator)]


def source_counts(rows: list[dict[str, Any]]) -> dict[str, int]:
    out: dict[str, int] = {}
    for row in rows:
        label = str(row.get("source") or "unknown")
        out[label] = out.get(label, 0) + 1
    return out


def reconstructed_share(counts: dict[str, int]) -> float | None:
    total = sum(counts.values())
    if total <= 0:
        return None
    recon = sum(value for key, value in counts.items() if key != "approved_entry")
    return recon / total


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


def compact(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "market": row.get("market"),
        "source": row.get("source"),
        "side": row.get("side"),
        "side_won": row.get("side_won"),
        "net_cents": row.get("net_gross_cents_after_entry_fee") or row_net_after_fee(row),
        "p_side": row.get("p_side"),
        "ask_prob": row.get("ask_prob"),
        "raw_edge_prob": row.get("raw_edge_prob") if row.get("raw_edge_prob") is not None else raw_edge(row),
        "adjusted_edge": row.get("adjusted_edge"),
        "cluster_penalty": row.get("cluster_penalty"),
        "seconds_to_close": seconds_to_close(row),
        "abs_d_sigma": row.get("abs_d_sigma"),
        "recross_hazard_score": row.get("recross_hazard_score"),
        "early_no_decay_score": row.get("early_no_decay_score"),
        "recross_instability_score": row.get("recross_instability_score"),
        "thin_edge_price_score": row.get("thin_edge_price_score"),
    }


def evaluate_lane(label: str, freeze_ts: str) -> dict[str, Any]:
    rows, target, denominator = clean_forward_rows(freeze_ts)
    target_summary = summarize(target, denominator)
    variants = []
    for name, params in VARIANTS.items():
        selected = selected_rows(rows, denominator, params)
        summary = summarize(selected, denominator)
        counts = source_counts(selected)
        share = reconstructed_share(counts)
        variants.append(
            {
                "candidate": f"{label}_{name}",
                "params": params,
                "candidate_summary": summary,
                "target_summary": target_summary,
                "delta_vs_target_cents": float(summary.get("net_cents") or 0.0) - float(target_summary.get("net_cents") or 0.0),
                "source_counts": counts,
                "reconstructed_share": share,
                "full_loss_cushion_estimate": int(max(0.0, float(summary.get("net_cents") or 0.0)) // 100.0),
                "blockers": blockers(summary, share),
                "worst_rows": [compact(row) for row in sorted(selected, key=lambda item: row_net_after_fee(item) or 0.0)[:10]],
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
        "freeze_ts_utc": freeze_ts,
        "future_denominator": denominator,
        "variants": variants,
    }


def build_report() -> dict[str, Any]:
    state = load_or_create_state()
    lanes = [
        evaluate_lane("diagnostic_target_window", target_freeze_ts()),
        evaluate_lane("post_cluster_penalty_birth", str(state["freeze_ts_utc"])),
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
        "Continuous cluster penalties are watch-only; post_cluster_penalty_birth is the only strict forward evidence for this new family.",
    ]
    for lane in report.get("lanes") or []:
        best = (lane.get("variants") or [{}])[0]
        summary = best.get("candidate_summary") or {}
        notes.append(
            f"{lane.get('lane')}: best {best.get('candidate')} settled {summary.get('settled')}, "
            f"coverage {summary.get('coverage_pct')}%, net {summary.get('net_cents')}c, "
            f"delta vs target {best.get('delta_vs_target_cents')}c, recon {best.get('reconstructed_share')}, "
            f"blockers {best.get('blockers')}."
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
        "# v28 Target-Coverage Cluster Penalty Watch",
        "",
        "Research-only; no live bot changes or orders.",
        "",
        f"- Generated UTC: `{report.get('generated_at_utc')}`",
        f"- Cluster penalty freeze UTC: `{state.get('freeze_ts_utc')}`",
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
                f"| {idx} | {variant.get('candidate')} | {summary.get('settled')}/{lane.get('future_denominator')} | "
                f"{summary.get('wins')}/{summary.get('losses')} | {fmt(summary.get('coverage_pct'))} | "
                f"{fmt(summary.get('net_cents'))} | {fmt(variant.get('delta_vs_target_cents'))} | "
                f"{fmt(variant.get('reconstructed_share'))} | {variant.get('full_loss_cushion_estimate')} | "
                f"{', '.join(variant.get('blockers') or []) or 'none'} |"
            )
        best = (lane.get("variants") or [{}])[0]
        lines.extend(["", "### Best Variant Worst Rows", ""])
        lines.extend([
            "| market | source | side | won | net c | p | ask | raw edge | adj edge | penalty | stc | abs d | recross |",
            "|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
        ])
        for row in best.get("worst_rows") or []:
            lines.append(
                f"| {row.get('market')} | {row.get('source')} | {row.get('side')} | {row.get('side_won')} | "
                f"{fmt(row.get('net_cents'))} | {fmt(row.get('p_side'))} | {fmt(row.get('ask_prob'))} | "
                f"{fmt(row.get('raw_edge_prob'))} | {fmt(row.get('adjusted_edge'))} | {fmt(row.get('cluster_penalty'))} | "
                f"{fmt(row.get('seconds_to_close'))} | {fmt(row.get('abs_d_sigma'))} | {fmt(row.get('recross_hazard_score'))} |"
            )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    report = build_report()
    write_md(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
