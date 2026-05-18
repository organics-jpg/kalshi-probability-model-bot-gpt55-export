"""Entry-policy bakeoff using RMT-conditioned forgetting probabilities.

This asks whether the RMT+forgetting FV candidates can support broad BTC 15m
coverage without simply replaying raw v28 overconfidence. It is shadow-only and
uses the same approved/rejected-actionable observation pool as the v28 bakeoff.
"""
from __future__ import annotations

import csv
import json
import random
from pathlib import Path
from typing import Any, Callable

from probe_v28_continuous_scorecard import watched_markets
from probe_v28_rmt_regime_diagnostic import attach_regime_rows
from probe_v28_shadow_entry_policy_bakeoff import base_tradeable, observation_pool
from probe_v28_state_aware_fv_candidates import (
    enrich_state,
    p_book,
    p_first_side_raw_later_book,
    p_raw,
    p_rmt_aggressive_forget,
    p_rmt_memory_gate,
    p_rmt_repetition_forget,
)


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
OUT_JSON = OUT_DIR / "v28_rmt_forgetting_entry_bakeoff_latest.json"
OUT_CSV = OUT_DIR / "v28_rmt_forgetting_entry_bakeoff_latest.csv"
OUT_MD = OUT_DIR / "v28_rmt_forgetting_entry_bakeoff_latest.md"
BOOTSTRAP_SEED = 28060
BOOTSTRAP_RUNS = 2000
KALSHI_TAKER_FEE_RATE = 0.07


def as_float(value: Any) -> float | None:
    if value is None or value == "":
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


FV: dict[str, Callable[[dict[str, Any]], float]] = {
    "v28_raw": p_raw,
    "book_ask_prior": p_book,
    "first_side_raw_later_book": p_first_side_raw_later_book,
    "rmt_aggressive_forget": p_rmt_aggressive_forget,
    "rmt_repetition_forget": p_rmt_repetition_forget,
    "rmt_memory_gate": p_rmt_memory_gate,
}

THRESHOLDS = [
    ("p50_edge0", 0.50, 0.00),
    ("p52_edge0", 0.52, 0.00),
    ("p55_edge0", 0.55, 0.00),
    ("p58_edge0", 0.58, 0.00),
    ("p60_edge0", 0.60, 0.00),
    ("p52_edge2", 0.52, 0.02),
    ("p55_edge2", 0.55, 0.02),
    ("p58_edge2", 0.58, 0.02),
]


def effective_edge(row: dict[str, Any], p_eff: float) -> float | None:
    ask_prob = as_float(row.get("ask_prob"))
    if ask_prob is None:
        return None
    return p_eff - ask_prob


def infer_quantity(row: dict[str, Any]) -> int:
    gross = as_float(row.get("gross_cents"))
    ask = as_float(row.get("ask_cents"))
    side_won = row.get("side_won")
    if gross is None or ask is None or ask <= 0:
        return 1
    per_contract = (100.0 - ask) if side_won is True else -ask
    if abs(per_contract) < 1e-9:
        return 1
    qty = int(round(abs(gross / per_contract)))
    return max(1, qty)


def estimate_entry_fee_cents(row: dict[str, Any]) -> float:
    ask = as_float(row.get("ask_cents"))
    if ask is None or ask <= 0.0 or ask >= 100.0:
        return 0.0
    qty = infer_quantity(row)
    probability = ask / 100.0
    raw_fee_dollars = KALSHI_TAKER_FEE_RATE * qty * probability * (1.0 - probability)
    return float(int(raw_fee_dollars * 100.0 + 0.999999))


def policy_name(fv_name: str, threshold_name: str) -> str:
    return f"{fv_name}_{threshold_name}"


def selected_rows(rows: list[dict[str, Any]], fv_name: str, fn: Callable[[dict[str, Any]], float], min_p: float, min_edge: float) -> list[dict[str, Any]]:
    picked: dict[str, dict[str, Any]] = {}
    for row in sorted(rows, key=lambda item: str(item.get("ts_wall") or "")):
        if not base_tradeable(row):
            continue
        try:
            p_eff = fn(row)
        except (KeyError, TypeError, ValueError):
            continue
        edge = effective_edge(row, p_eff)
        if edge is None or p_eff < min_p or edge < min_edge:
            continue
        market = str(row.get("market") or "")
        if market and market not in picked:
            picked[market] = {
                **row,
                "fv": fv_name,
                "p_eff": p_eff,
                "eff_edge_prob": edge,
                "estimated_entry_fee_cents": estimate_entry_fee_cents(row),
                "net_gross_cents_after_entry_fee": None if row.get("gross_cents") is None else float(row.get("gross_cents") or 0.0) - estimate_entry_fee_cents(row),
            }
    return [picked[key] for key in sorted(picked)]


def summarize_policy(name: str, rows: list[dict[str, Any]], watched_count: int) -> dict[str, Any]:
    settled = [row for row in rows if row.get("side_won") is not None]
    resolved = [row for row in rows if row.get("gross_cents") is not None]
    briers = [
        (float(row["p_eff"]) - (1.0 if row.get("side_won") is True else 0.0)) ** 2
        for row in settled
    ]
    gross = sum(float(row.get("gross_cents") or 0.0) for row in resolved)
    net_gross = sum(float(row.get("net_gross_cents_after_entry_fee") or 0.0) for row in resolved)
    fees = sum(float(row.get("estimated_entry_fee_cents") or 0.0) for row in resolved)
    return {
        "policy": name,
        "entries": len(rows),
        "resolved": len(resolved),
        "settled": len(settled),
        "wins": sum(1 for row in settled if row.get("side_won") is True),
        "losses": sum(1 for row in settled if row.get("side_won") is False),
        "coverage_pct": (len(rows) / watched_count * 100.0) if watched_count else None,
        "gross_cents": gross,
        "estimated_entry_fee_cents": fees,
        "net_gross_cents_after_entry_fee": net_gross,
        "avg_gross_cents": gross / len(resolved) if resolved else None,
        "avg_net_gross_cents_after_entry_fee": net_gross / len(resolved) if resolved else None,
        "avg_brier": sum(briers) / len(briers) if briers else None,
        "approved_entry_count": sum(1 for row in rows if row.get("source") == "approved_entry"),
        "added_reject_count": sum(1 for row in rows if row.get("source") == "rejected_actionable"),
    }


def market_split_map(markets: list[str]) -> dict[str, str]:
    ordered = sorted(markets)
    split_at = max(1, len(ordered) // 2)
    return {
        market: ("early" if idx < split_at else "late")
        for idx, market in enumerate(ordered)
    }


def summarize_temporal(name: str, rows: list[dict[str, Any]], split_by_market: dict[str, str]) -> dict[str, Any]:
    early = [row for row in rows if split_by_market.get(str(row.get("market") or "")) == "early"]
    late = [row for row in rows if split_by_market.get(str(row.get("market") or "")) == "late"]
    early_summary = summarize_policy(name, early, max(1, sum(1 for value in split_by_market.values() if value == "early")))
    late_summary = summarize_policy(name, late, max(1, sum(1 for value in split_by_market.values() if value == "late")))
    return {
        "early": early_summary,
        "late": late_summary,
        "both_halves_nonnegative": early_summary["gross_cents"] >= 0 and late_summary["gross_cents"] >= 0,
        "late_minus_early_avg_gross_cents": (
            None
            if early_summary["avg_gross_cents"] is None or late_summary["avg_gross_cents"] is None
            else late_summary["avg_gross_cents"] - early_summary["avg_gross_cents"]
        ),
    }


def percentile(sorted_values: list[float], q: float) -> float | None:
    if not sorted_values:
        return None
    idx = min(len(sorted_values) - 1, max(0, int(round((len(sorted_values) - 1) * q))))
    return sorted_values[idx]


def bootstrap_market_gross(rows: list[dict[str, Any]]) -> dict[str, Any]:
    resolved_by_market: dict[str, float] = {}
    for row in rows:
        if row.get("gross_cents") is None:
            continue
        market = str(row.get("market") or "")
        if not market:
            continue
        resolved_by_market[market] = resolved_by_market.get(market, 0.0) + float(row.get("net_gross_cents_after_entry_fee") or row.get("gross_cents") or 0.0)
    markets = sorted(resolved_by_market)
    if len(markets) < 5:
        return {
            "market_count": len(markets),
            "runs": 0,
            "gross_p05": None,
            "gross_p10": None,
            "gross_p50": None,
            "gross_p90": None,
            "prob_gross_positive": None,
        }
    rng = random.Random(BOOTSTRAP_SEED + sum(ord(ch) for ch in "|".join(markets)))
    samples: list[float] = []
    for _ in range(BOOTSTRAP_RUNS):
        total = 0.0
        for _ in markets:
            total += resolved_by_market[rng.choice(markets)]
        samples.append(total)
    samples.sort()
    return {
        "market_count": len(markets),
        "runs": BOOTSTRAP_RUNS,
        "gross_p05": percentile(samples, 0.05),
        "gross_p10": percentile(samples, 0.10),
        "gross_p50": percentile(samples, 0.50),
        "gross_p90": percentile(samples, 0.90),
        "prob_gross_positive": sum(1 for value in samples if value > 0.0) / len(samples),
    }


def build_report() -> dict[str, Any]:
    rows = enrich_state(attach_regime_rows(observation_pool()))
    watched = sorted(watched_markets())
    watched_count = len(watched)
    split_by_market = market_split_map(watched)
    selected: list[dict[str, Any]] = []
    summary: list[dict[str, Any]] = []
    temporal: dict[str, dict[str, Any]] = {}
    bootstrap: dict[str, dict[str, Any]] = {}
    for fv_name, fn in FV.items():
        for threshold_name, min_p, min_edge in THRESHOLDS:
            name = policy_name(fv_name, threshold_name)
            policy_rows = selected_rows(rows, fv_name, fn, min_p, min_edge)
            selected.extend({"policy": name, **row} for row in policy_rows)
            summary.append(summarize_policy(name, policy_rows, watched_count))
            temporal[name] = summarize_temporal(name, policy_rows, split_by_market)
            bootstrap[name] = bootstrap_market_gross(policy_rows)
    ranked_by_pnl = sorted(summary, key=lambda row: (-(float(row.get("net_gross_cents_after_entry_fee") or 0.0)), -(float(row.get("coverage_pct") or 0.0)), row["policy"]))
    broad = [
        row for row in summary
        if row.get("coverage_pct") is not None and 70.0 <= float(row["coverage_pct"]) <= 90.0
    ]
    ranked_broad = sorted(broad, key=lambda row: (-(float(row.get("net_gross_cents_after_entry_fee") or 0.0)), float(row.get("avg_brier") or 999.0), row["policy"]))
    robust_broad = [
        row for row in broad
        if temporal.get(str(row.get("policy") or ""), {}).get("both_halves_nonnegative") is True
    ]
    ranked_robust_broad = sorted(robust_broad, key=lambda row: (-(float(row.get("net_gross_cents_after_entry_fee") or 0.0)), float(row.get("avg_brier") or 999.0), row["policy"]))
    return {
        "watched_markets": watched_count,
        "observation_rows": len(rows),
        "summary": summary,
        "temporal": temporal,
        "bootstrap": bootstrap,
        "ranked_by_pnl": ranked_by_pnl,
        "ranked_broad_coverage": ranked_broad,
        "ranked_robust_broad_coverage": ranked_robust_broad,
        "rows": selected,
    }


def write_csv(rows: list[dict[str, Any]]) -> None:
    if not rows:
        OUT_CSV.write_text("", encoding="utf-8")
        return
    keys = sorted({key for row in rows for key in row.keys()})
    with OUT_CSV.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=keys, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def fmt(value: Any) -> str:
    if value is None:
        return "None"
    if isinstance(value, float):
        return f"{value:.6f}"
    return str(value)


def write_table(lines: list[str], rows: list[dict[str, Any]], limit: int = 12) -> None:
    lines.append("| rank | policy | entries | settled | wins | losses | coverage | gross c | net c | avg brier | actual/sim | early/late net | boot net p10/p50 | boot p>0 |")
    lines.append("|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|")
    for idx, row in enumerate(rows[:limit], start=1):
        temporal = row.get("_temporal") or {}
        bootstrap = row.get("_bootstrap") or {}
        early = (temporal.get("early") or {}).get("net_gross_cents_after_entry_fee")
        late = (temporal.get("late") or {}).get("net_gross_cents_after_entry_fee")
        lines.append(
            f"| {idx} | {row['policy']} | {row['entries']} | {row['settled']} | {row['wins']} | {row['losses']} | "
            f"{fmt(row['coverage_pct'])} | {row['gross_cents']} | {row.get('net_gross_cents_after_entry_fee')} | {fmt(row['avg_brier'])} | "
            f"{row['approved_entry_count']}/{row['added_reject_count']} | {fmt(early)}/{fmt(late)} | "
            f"{fmt(bootstrap.get('gross_p10'))}/{fmt(bootstrap.get('gross_p50'))} | {fmt(bootstrap.get('prob_gross_positive'))} |"
        )


def with_diagnostics(rows: list[dict[str, Any]], report: dict[str, Any]) -> list[dict[str, Any]]:
    temporal = report["temporal"]
    bootstrap = report["bootstrap"]
    return [
        {
            **row,
            "_temporal": temporal.get(str(row.get("policy") or ""), {}),
            "_bootstrap": bootstrap.get(str(row.get("policy") or ""), {}),
        }
        for row in rows
    ]


def write_md(report: dict[str, Any]) -> None:
    lines = [
        "# v28 RMT Forgetting Entry Bakeoff",
        "",
        "Shadow-only entry-policy bakeoff using RMT-conditioned catastrophic forgetting FV candidates.",
        "",
        f"- Watched markets: `{report['watched_markets']}`",
        f"- Observation rows: `{report['observation_rows']}`",
        "",
        "## Ranked By P&L",
        "",
    ]
    write_table(lines, with_diagnostics(report["ranked_by_pnl"], report))
    lines.extend(["", "## Broad Coverage Candidates", ""])
    if report["ranked_broad_coverage"]:
        write_table(lines, with_diagnostics(report["ranked_broad_coverage"], report))
    else:
        lines.append("No 70-90% coverage candidates in this forward sample.")
    lines.extend(["", "## Broad Coverage With Nonnegative Early And Late Halves", ""])
    if report["ranked_robust_broad_coverage"]:
        write_table(lines, with_diagnostics(report["ranked_robust_broad_coverage"], report))
    else:
        lines.append("No broad-coverage candidates are nonnegative in both temporal halves yet.")
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    report = build_report()
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_csv(report["rows"])
    write_md(report)
    print(str(OUT_MD))


if __name__ == "__main__":
    main()
