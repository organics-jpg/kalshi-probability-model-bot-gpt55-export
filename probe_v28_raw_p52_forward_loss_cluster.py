"""Forward loss-cluster diagnostic for the raw v28 p52 candidate.

This is research-only. It does not change the live bot or place orders.

The purpose is to keep the p52 investigation honest: when fresh forward rows
cluster into losses, score predeclared physical buckets instead of inventing a
single rule that perfectly excludes already-seen losers.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from probe_v28_frozen_forward_candidates import parse_ts
from probe_v28_rmt_regime_diagnostic import attach_regime_rows
from probe_v28_shadow_entry_policy_bakeoff import observation_pool
from probe_v28_state_aware_fv_candidates import enrich_state, p_raw, p_rmt_memory_gate, p_rmt_repetition_forget


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
RAW_PHYSICS_JSON = OUT_DIR / "v28_frozen_raw_physics_challengers_latest.json"
OUT_JSON = OUT_DIR / "v28_raw_p52_forward_loss_cluster_latest.json"
OUT_MD = OUT_DIR / "v28_raw_p52_forward_loss_cluster_latest.md"


def load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
    return payload if isinstance(payload, dict) else {}


def as_float(value: Any) -> float | None:
    if value is None or value == "":
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def selected_markets() -> list[dict[str, Any]]:
    payload = load_json(RAW_PHYSICS_JSON)
    for row in payload.get("summary") or []:
        if row.get("policy") == "v28_raw_p52_edge0":
            selected = row.get("selected_forward_rows")
            return selected if isinstance(selected, list) else []
    return []


def enrich_selected(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    observations = enrich_state(attach_regime_rows(observation_pool()))
    by_key: dict[tuple[str, str, str], dict[str, Any]] = {}
    for row in observations:
        key = (
            str(row.get("market") or ""),
            str(row.get("side") or ""),
            str(row.get("ts_wall") or ""),
        )
        by_key[key] = row
    enriched: list[dict[str, Any]] = []
    for row in rows:
        key = (
            str(row.get("market") or ""),
            str(row.get("side") or ""),
            str(row.get("ts_wall") or ""),
        )
        source = by_key.get(key, {})
        ask = as_float(source.get("ask_prob") if source else row.get("ask_prob"))
        p = p_raw(source) if source else as_float(row.get("p_eff"))
        if ask is None or p is None:
            continue
        enriched.append({
            **row,
            **{k: source.get(k) for k in [
                "abs_d_sigma",
                "recross_hazard_score",
                "spectral_tag",
                "outlier_share",
                "btc_age_ms",
                "book_age_ms",
                "eligible_depth",
                "market_side_observation_index",
            ]},
            "p_raw": p,
            "p_rmt_memory_gate": p_rmt_memory_gate(source) if source else None,
            "p_rmt_repetition_forget": p_rmt_repetition_forget(source) if source else None,
            "ask_prob": ask,
            "raw_edge_prob": p - ask,
        })
    return enriched


def bucket_tags(row: dict[str, Any]) -> list[str]:
    p = as_float(row.get("p_raw")) or 0.0
    ask = as_float(row.get("ask_prob")) or 0.0
    edge = as_float(row.get("raw_edge_prob")) or 0.0
    abs_d = as_float(row.get("abs_d_sigma")) or 999.0
    recross = as_float(row.get("recross_hazard_score")) or 0.0
    outlier = as_float(row.get("outlier_share")) or 0.0
    book_age = as_float(row.get("book_age_ms")) or 0.0
    depth = as_float(row.get("eligible_depth")) or 0.0
    idx = int(as_float(row.get("market_side_observation_index")) or 0)
    mem_margin = (as_float(row.get("p_rmt_memory_gate")) or 0.0) - ask
    rep_margin = (as_float(row.get("p_rmt_repetition_forget")) or 0.0) - ask
    tags = ["all"]
    if p < 0.60:
        tags.append("raw_p_lt_60")
    if p >= 0.60:
        tags.append("raw_p_gte_60")
    if ask >= 0.55:
        tags.append("ask_gte_55")
    if ask < 0.55:
        tags.append("ask_lt_55")
    if edge < 0.05:
        tags.append("edge_lt_5pp")
    if 0.05 <= edge < 0.10:
        tags.append("edge_5_10pp")
    if edge >= 0.10:
        tags.append("edge_gte_10pp")
    if abs_d <= 0.20:
        tags.append("near_strike_020")
    if recross >= 0.90:
        tags.append("recross_gte_090")
    if str(row.get("spectral_tag") or "") == "spectral_dominant_factor":
        tags.append("spectral_dominant")
    if outlier >= 0.85:
        tags.append("rmt_outlier_share_gte_085")
    if book_age >= 500.0:
        tags.append("book_age_gte_500ms")
    if depth <= 150.0:
        tags.append("thin_depth_lte_150")
    if idx == 0:
        tags.append("first_side_observation")
    if idx > 0:
        tags.append("repeated_side_observation")
    if mem_margin < 0.02:
        tags.append("memory_margin_lt_2pp")
    if rep_margin < 0.02:
        tags.append("repetition_margin_lt_2pp")
    if p < 0.60 and abs_d <= 0.20 and recross >= 0.90:
        tags.append("weakraw_nearstrike_highrecross")
    if p < 0.60 and edge >= 0.10:
        tags.append("weakraw_large_raw_edge")
    return tags


def summarize_bucket(rows: list[dict[str, Any]]) -> dict[str, Any]:
    settled = [row for row in rows if row.get("side_won") is not None]
    net = sum(float(row.get("net_gross_cents_after_entry_fee") or 0.0) for row in settled)
    briers = [
        ((as_float(row.get("p_raw")) or 0.5) - (1.0 if row.get("side_won") is True else 0.0)) ** 2
        for row in settled
    ]
    return {
        "count": len(rows),
        "settled": len(settled),
        "wins": sum(1 for row in settled if row.get("side_won") is True),
        "losses": sum(1 for row in settled if row.get("side_won") is False),
        "net_cents": net,
        "avg_brier": sum(briers) / len(briers) if briers else None,
    }


def build_report() -> dict[str, Any]:
    rows = enrich_selected(selected_markets())
    buckets: dict[str, list[dict[str, Any]]] = {}
    for row in rows:
        tags = bucket_tags(row)
        row["physics_tags"] = tags
        for tag in tags:
            buckets.setdefault(tag, []).append(row)
    summaries = [
        {"bucket": tag, **summarize_bucket(bucket_rows)}
        for tag, bucket_rows in sorted(buckets.items())
    ]
    summaries.sort(key=lambda item: (float(item.get("net_cents") or 0.0), -int(item.get("settled") or 0)))
    return {
        "source": str(RAW_PHYSICS_JSON),
        "policy": "v28_raw_p52_edge0",
        "rows": rows,
        "buckets": summaries,
    }


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
        "# v28 Raw p52 Forward Loss Cluster",
        "",
        "Forward-only diagnostic for the raw p52 candidate. Buckets are overlapping physical states, not promotion rules.",
        "",
        "## Worst Buckets",
        "",
        "| bucket | count | settled | W/L | net c | brier |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for row in report.get("buckets") or []:
        if int(row.get("settled") or 0) == 0:
            continue
        lines.append(
            f"| {row.get('bucket')} | {row.get('count')} | {row.get('settled')} | "
            f"{row.get('wins')}/{row.get('losses')} | {fmt(row.get('net_cents'))} | {fmt(row.get('avg_brier'))} |"
        )
    lines.extend([
        "",
        "## Selected Rows",
        "",
        "| market | side | p | ask | edge | abs d | recross | outlier | book age | depth | won | net c | tags |",
        "|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---|---:|---|",
    ])
    for row in report.get("rows") or []:
        lines.append(
            f"| {row.get('market')} | {row.get('side')} | {fmt(row.get('p_raw'))} | "
            f"{fmt(row.get('ask_prob'))} | {fmt(row.get('raw_edge_prob'))} | "
            f"{fmt(row.get('abs_d_sigma'))} | {fmt(row.get('recross_hazard_score'))} | "
            f"{fmt(row.get('outlier_share'))} | {fmt(row.get('book_age_ms'))} | "
            f"{fmt(row.get('eligible_depth'))} | {row.get('side_won')} | "
            f"{fmt(row.get('net_gross_cents_after_entry_fee'))} | {', '.join(row.get('physics_tags') or [])} |"
        )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    report = build_report()
    write_report(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
