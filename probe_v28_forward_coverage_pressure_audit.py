"""Forward coverage-pressure audit for v28 candidate gates.

The active goal wants broad BTC 15m participation, but forcing trades to meet a
coverage number is exactly how weak edge sneaks in. This audit tracks each
forward market missed by frozen candidates, scores the best near-miss row once
the market resolves, and separates healthy abstentions from coverage mistakes.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from probe_v28_reactivated_shadow_status import market_result


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
SOURCES = [
    OUT_DIR / "v28_frozen_forward_candidates_latest.json",
    OUT_DIR / "v28_frozen_threshold_challengers_latest.json",
    OUT_DIR / "v28_frozen_side_agreement_challengers_latest.json",
    OUT_DIR / "v28_frozen_convex_escape_challengers_latest.json",
    OUT_DIR / "v28_frozen_raw_physics_challengers_latest.json",
    OUT_DIR / "v28_frozen_raw_p52_sideflip_challenger_latest.json",
]
OUT_JSON = OUT_DIR / "v28_forward_coverage_pressure_audit_latest.json"
OUT_MD = OUT_DIR / "v28_forward_coverage_pressure_audit_latest.md"
KALSHI_TAKER_FEE_RATE = 0.07


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


def estimate_fee_cents(ask_prob: float | None, qty: int = 2) -> float:
    if ask_prob is None or ask_prob <= 0.0 or ask_prob >= 1.0:
        return 0.0
    raw_fee_dollars = KALSHI_TAKER_FEE_RATE * qty * ask_prob * (1.0 - ask_prob)
    return float(int(raw_fee_dollars * 100.0 + 0.999999))


def near_miss_score(row: dict[str, Any], result: str) -> dict[str, Any]:
    side = str(row.get("side") or "").lower()
    ask_prob = as_float(row.get("ask_prob"))
    p_eff = as_float(row.get("p_eff"))
    edge = as_float(row.get("eff_edge_prob"))
    won = result in {"yes", "no"} and side == result
    gross = None
    net = None
    if result in {"yes", "no"} and side in {"yes", "no"} and ask_prob is not None:
        ask_cents = ask_prob * 100.0
        gross = 2.0 * ((100.0 - ask_cents) if won else -ask_cents)
        net = gross - estimate_fee_cents(ask_prob, qty=2)
    return {
        "side": side,
        "p_eff": p_eff,
        "ask_prob": ask_prob,
        "edge_prob": edge,
        "won": won if result in {"yes", "no"} else None,
        "gross_cents": gross,
        "net_cents_after_fee": net,
        "source": row.get("source"),
        "reason": row.get("reason"),
        "ts_wall": row.get("ts_wall"),
        "spectral_tag": row.get("spectral_tag"),
        "market_side_observation_index": row.get("market_side_observation_index"),
    }


def classify_abstention(score: dict[str, Any], status: str, result: str) -> str:
    if status not in {"finalized", "settled"} or result not in {"yes", "no"}:
        return "pending_resolution"
    net = as_float(score.get("net_cents_after_fee"))
    edge = as_float(score.get("edge_prob"))
    if net is None:
        return "unscorable"
    if net < 0:
        return "healthy_abstention_saved_loss"
    if edge is not None and edge < 0:
        return "profitable_negative_edge_miss"
    return "coverage_mistake_missed_profit"


def source_rows(payload: dict[str, Any], source_name: str) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for policy_row in payload.get("summary") or []:
        policy = str(policy_row.get("policy") or "")
        for detail in policy_row.get("missed_forward_market_details") or []:
            market = str(detail.get("market") or "")
            best = detail.get("best_candidate")
            if not market or not isinstance(best, dict):
                continue
            status, result = market_result(market)
            score = near_miss_score(best, result)
            out.append({
                "source": source_name,
                "policy": policy,
                "market": market,
                "miss_reason": detail.get("reason"),
                "market_status": status,
                "market_result": result,
                "best_near_miss": score,
                "abstention_class": classify_abstention(score, status, result),
            })
    return out


def summarize(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    keys = sorted({(row["source"], row["policy"]) for row in rows})
    for source, policy in keys:
        bucket = [row for row in rows if row["source"] == source and row["policy"] == policy]
        resolved = [
            row for row in bucket
            if row.get("market_status") in {"finalized", "settled"}
            and row.get("market_result") in {"yes", "no"}
        ]
        net = sum(float((row.get("best_near_miss") or {}).get("net_cents_after_fee") or 0.0) for row in resolved)
        out.append({
            "source": source,
            "policy": policy,
            "misses": len(bucket),
            "resolved": len(resolved),
            "pending": len(bucket) - len(resolved),
            "near_miss_net_cents": net,
            "healthy_abstentions": sum(1 for row in resolved if row.get("abstention_class") == "healthy_abstention_saved_loss"),
            "coverage_mistakes": sum(1 for row in resolved if row.get("abstention_class") == "coverage_mistake_missed_profit"),
            "profitable_negative_edge_misses": sum(1 for row in resolved if row.get("abstention_class") == "profitable_negative_edge_miss"),
        })
    return out


def build_report() -> dict[str, Any]:
    rows: list[dict[str, Any]] = []
    for path in SOURCES:
        payload = load_json(path)
        if not payload:
            continue
        rows.extend(source_rows(payload, path.stem.replace("_latest", "")))
    return {
        "sources": [str(path) for path in SOURCES],
        "summary": summarize(rows),
        "rows": rows,
    }


def fmt(value: Any) -> str:
    if value is None:
        return "None"
    if isinstance(value, float):
        return f"{value:.6f}"
    return str(value)


def write_md(report: dict[str, Any]) -> None:
    lines = [
        "# v28 Forward Coverage Pressure Audit",
        "",
        "Tracks missed forward markets so coverage pressure does not turn into forced bad trades.",
        "",
        "## Summary",
        "",
        "| source | policy | misses | resolved | pending | near-miss net c | saved losses | missed profits | profitable negative-edge misses |",
        "|---|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for row in report["summary"]:
        lines.append(
            f"| {row['source']} | {row['policy']} | {row['misses']} | {row['resolved']} | {row['pending']} | "
            f"{fmt(row['near_miss_net_cents'])} | {row['healthy_abstentions']} | {row['coverage_mistakes']} | "
            f"{row['profitable_negative_edge_misses']} |"
        )
    lines.extend([
        "",
        "## Missed Forward Markets",
        "",
        "| source | policy | market | status | result | class | miss reason | side | p | ask | edge | near-miss net c |",
        "|---|---|---|---|---|---|---|---|---:|---:|---:|---:|",
    ])
    for row in report["rows"][-80:]:
        best = row.get("best_near_miss") or {}
        lines.append(
            f"| {row.get('source')} | {row.get('policy')} | {row.get('market')} | {row.get('market_status')} | "
            f"{row.get('market_result')} | {row.get('abstention_class')} | {row.get('miss_reason')} | "
            f"{best.get('side')} | {fmt(best.get('p_eff'))} | {fmt(best.get('ask_prob'))} | "
            f"{fmt(best.get('edge_prob'))} | {fmt(best.get('net_cents_after_fee'))} |"
        )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    report = build_report()
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_md(report)
    print(str(OUT_MD))


if __name__ == "__main__":
    main()
