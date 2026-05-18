"""Physics-penalty candidates around raw v28 fair value.

This is a deliberately small, interpretable candidate family. It starts from
raw v28 and subtracts only costs with a market-mechanics argument: taker fee,
fragile touch depth, crowded touch, and expensive-low-edge asymmetry. It is
not a threshold search and it does not touch the live bot.
"""
from __future__ import annotations

import csv
import json
import random
from pathlib import Path
from typing import Any, Callable

from probe_v28_continuous_scorecard import watched_markets
from probe_v28_rmt_forgetting_entry_bakeoff import estimate_entry_fee_cents
from probe_v28_rmt_regime_diagnostic import attach_regime_rows
from probe_v28_shadow_entry_policy_bakeoff import base_tradeable, observation_pool
from probe_v28_state_aware_fv_candidates import enrich_state, p_raw


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
OUT_JSON = OUT_DIR / "v28_raw_physics_penalty_candidates_latest.json"
OUT_CSV = OUT_DIR / "v28_raw_physics_penalty_candidates_latest.csv"
OUT_MD = OUT_DIR / "v28_raw_physics_penalty_candidates_latest.md"
BOOTSTRAP_SEED = 28078
BOOTSTRAP_RUNS = 2000


def as_float(value: Any) -> float | None:
    if value is None or value == "":
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def ask_prob(row: dict[str, Any]) -> float | None:
    return as_float(row.get("ask_prob"))


def raw_edge(row: dict[str, Any]) -> float | None:
    ask = ask_prob(row)
    if ask is None:
        return None
    return p_raw(row) - ask


def fee_friction_prob(row: dict[str, Any]) -> float:
    # Convert estimated cents fee for the inferred order into per-contract probability.
    return estimate_entry_fee_cents(row) / (100.0 * max(1, int(row.get("qty") or 2)))


def depth_friction(row: dict[str, Any]) -> float:
    depth = as_float(row.get("eligible_depth"))
    if depth is None:
        return 0.0
    if depth < 25.0:
        return 0.020
    if depth > 1300.0:
        return 0.012
    return 0.0


def expensive_low_edge_friction(row: dict[str, Any]) -> float:
    ask = ask_prob(row)
    edge = raw_edge(row)
    if ask is None or edge is None:
        return 0.0
    if ask >= 0.75 and edge < 0.05:
        return 0.030
    if ask >= 0.80 and edge < 0.08:
        return 0.020
    return 0.0


def repeated_side_friction(row: dict[str, Any]) -> float:
    idx = as_float(row.get("market_side_observation_index"))
    if idx is None or idx <= 0:
        return 0.0
    return min(0.030, 0.006 * idx)


def p_fee(row: dict[str, Any]) -> float:
    return max(0.0, min(1.0, p_raw(row) - fee_friction_prob(row)))


def p_touch(row: dict[str, Any]) -> float:
    return max(0.0, min(1.0, p_fee(row) - depth_friction(row)))


def p_expensive(row: dict[str, Any]) -> float:
    return max(0.0, min(1.0, p_fee(row) - expensive_low_edge_friction(row)))


def p_full(row: dict[str, Any]) -> float:
    penalty = fee_friction_prob(row) + depth_friction(row) + expensive_low_edge_friction(row) + repeated_side_friction(row)
    return max(0.0, min(1.0, p_raw(row) - penalty))


def p_full_no_repeat(row: dict[str, Any]) -> float:
    penalty = fee_friction_prob(row) + depth_friction(row) + expensive_low_edge_friction(row)
    return max(0.0, min(1.0, p_raw(row) - penalty))


FV: dict[str, Callable[[dict[str, Any]], float]] = {
    "v28_raw": p_raw,
    "raw_fee_friction": p_fee,
    "raw_touch_friction": p_touch,
    "raw_expensive_friction": p_expensive,
    "raw_full_physics_friction": p_full,
    "raw_full_no_repeat_friction": p_full_no_repeat,
}

THRESHOLDS = [
    ("p50_edge0", 0.50, 0.00),
    ("p50_edge1", 0.50, 0.01),
    ("p52_edge0", 0.52, 0.00),
]


def selected_rows(rows: list[dict[str, Any]], fv_name: str, fn: Callable[[dict[str, Any]], float], min_p: float, min_edge: float) -> list[dict[str, Any]]:
    picked: dict[str, dict[str, Any]] = {}
    for row in sorted(rows, key=lambda item: str(item.get("ts_wall") or "")):
        if not base_tradeable(row):
            continue
        try:
            p_eff = fn(row)
        except (KeyError, TypeError, ValueError):
            continue
        ask = ask_prob(row)
        if ask is None:
            continue
        edge = p_eff - ask
        if p_eff < min_p or edge < min_edge:
            continue
        market = str(row.get("market") or "")
        if market and market not in picked:
            picked[market] = {
                **row,
                "fv": fv_name,
                "p_eff": p_eff,
                "eff_edge_prob": edge,
                "raw_p_eff": p_raw(row),
                "raw_edge_prob": p_raw(row) - ask,
                "fee_friction_prob": fee_friction_prob(row),
                "depth_friction_prob": depth_friction(row),
                "expensive_low_edge_friction_prob": expensive_low_edge_friction(row),
                "repeated_side_friction_prob": repeated_side_friction(row),
                "net_gross_cents_after_entry_fee": None if row.get("gross_cents") is None else float(row.get("gross_cents") or 0.0) - estimate_entry_fee_cents(row),
            }
    return [picked[key] for key in sorted(picked)]


def summarize_policy(policy: str, rows: list[dict[str, Any]], watched_count: int) -> dict[str, Any]:
    resolved = [row for row in rows if row.get("gross_cents") is not None]
    settled = [row for row in rows if row.get("side_won") is not None]
    net = sum(float(row.get("net_gross_cents_after_entry_fee") or row.get("gross_cents") or 0.0) for row in resolved)
    briers = [
        (float(row["p_eff"]) - (1.0 if row.get("side_won") is True else 0.0)) ** 2
        for row in settled
        if row.get("p_eff") is not None
    ]
    return {
        "policy": policy,
        "entries": len(rows),
        "resolved": len(resolved),
        "settled": len(settled),
        "wins": sum(1 for row in settled if row.get("side_won") is True),
        "losses": sum(1 for row in settled if row.get("side_won") is False),
        "coverage_pct": len(rows) / watched_count * 100.0 if watched_count else None,
        "net_cents_after_entry_fee": net,
        "avg_net_cents_after_entry_fee": net / len(resolved) if resolved else None,
        "avg_brier": sum(briers) / len(briers) if briers else None,
        "approved_entry_count": sum(1 for row in rows if row.get("source") == "approved_entry"),
        "added_reject_count": sum(1 for row in rows if row.get("source") == "rejected_actionable"),
        "avg_fee_friction_prob": avg(row.get("fee_friction_prob") for row in rows),
        "avg_depth_friction_prob": avg(row.get("depth_friction_prob") for row in rows),
        "avg_expensive_low_edge_friction_prob": avg(row.get("expensive_low_edge_friction_prob") for row in rows),
        "avg_repeated_side_friction_prob": avg(row.get("repeated_side_friction_prob") for row in rows),
    }


def avg(values: Any) -> float | None:
    nums = [float(value) for value in values if value is not None]
    return sum(nums) / len(nums) if nums else None


def market_split_map(markets: list[str]) -> dict[str, str]:
    ordered = sorted(markets)
    split_at = max(1, len(ordered) // 2)
    return {market: ("early" if idx < split_at else "late") for idx, market in enumerate(ordered)}


def temporal_summary(policy: str, rows: list[dict[str, Any]], split: dict[str, str]) -> dict[str, Any]:
    early = [row for row in rows if split.get(str(row.get("market") or "")) == "early"]
    late = [row for row in rows if split.get(str(row.get("market") or "")) == "late"]
    early_s = summarize_policy(policy, early, max(1, sum(1 for value in split.values() if value == "early")))
    late_s = summarize_policy(policy, late, max(1, sum(1 for value in split.values() if value == "late")))
    return {"early": early_s, "late": late_s}


def percentile(sorted_values: list[float], q: float) -> float | None:
    if not sorted_values:
        return None
    idx = min(len(sorted_values) - 1, max(0, int(round((len(sorted_values) - 1) * q))))
    return sorted_values[idx]


def bootstrap(rows: list[dict[str, Any]]) -> dict[str, Any]:
    by_market: dict[str, float] = {}
    for row in rows:
        if row.get("gross_cents") is None:
            continue
        market = str(row.get("market") or "")
        by_market[market] = by_market.get(market, 0.0) + float(row.get("net_gross_cents_after_entry_fee") or 0.0)
    markets = sorted(by_market)
    if len(markets) < 5:
        return {"market_count": len(markets), "runs": 0, "net_p10": None, "net_p50": None, "prob_positive": None}
    rng = random.Random(BOOTSTRAP_SEED + sum(ord(ch) for ch in "|".join(markets)))
    samples: list[float] = []
    for _ in range(BOOTSTRAP_RUNS):
        total = 0.0
        for _ in markets:
            total += by_market[rng.choice(markets)]
        samples.append(total)
    samples.sort()
    return {
        "market_count": len(markets),
        "runs": BOOTSTRAP_RUNS,
        "net_p10": percentile(samples, 0.10),
        "net_p50": percentile(samples, 0.50),
        "prob_positive": sum(1 for value in samples if value > 0.0) / len(samples),
    }


def build_report() -> dict[str, Any]:
    rows = enrich_state(attach_regime_rows(observation_pool()))
    watched = sorted(watched_markets())
    split = market_split_map(watched)
    selected: list[dict[str, Any]] = []
    summary: list[dict[str, Any]] = []
    temporal: dict[str, Any] = {}
    boot: dict[str, Any] = {}
    for fv_name, fn in FV.items():
        for suffix, min_p, min_edge in THRESHOLDS:
            policy = f"{fv_name}_{suffix}"
            picked = selected_rows(rows, fv_name, fn, min_p, min_edge)
            for row in picked:
                row["policy"] = policy
            selected.extend(picked)
            summary.append(summarize_policy(policy, picked, len(watched)))
            temporal[policy] = temporal_summary(policy, picked, split)
            boot[policy] = bootstrap(picked)
    ranked = sorted(
        summary,
        key=lambda row: (
            row.get("coverage_pct") is not None and 70.0 <= float(row.get("coverage_pct") or 0.0) <= 90.0,
            float(row.get("net_cents_after_entry_fee") or -999999.0),
            -float(row.get("avg_brier") or 999.0),
        ),
        reverse=True,
    )
    return {
        "watched_markets": len(watched),
        "observation_rows": len(rows),
        "summary": summary,
        "ranked": ranked,
        "temporal": temporal,
        "bootstrap": boot,
        "rows": selected,
    }


def fmt(value: Any) -> str:
    if value is None:
        return "None"
    if isinstance(value, float):
        return f"{value:.6f}"
    return str(value)


def write_csv(rows: list[dict[str, Any]]) -> None:
    if not rows:
        OUT_CSV.write_text("", encoding="utf-8")
        return
    keys = sorted({key for row in rows for key in row})
    with OUT_CSV.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=keys)
        writer.writeheader()
        writer.writerows(rows)


def write_md(report: dict[str, Any]) -> None:
    lines = [
        "# v28 Raw Physics Penalty Candidates",
        "",
        "Shadow-only. Starts from raw v28 and subtracts interpretable execution/geometry frictions.",
        "",
        f"- Watched markets: `{report['watched_markets']}`",
        f"- Observation rows: `{report['observation_rows']}`",
        "",
        "## Ranked Candidates",
        "",
        "| rank | policy | entries | settled | W/L | coverage | net c | avg brier | actual/sim | frictions fee/depth/exp/repeat | boot p10/p50 | boot p>0 |",
        "|---:|---|---:|---:|---:|---:|---:|---:|---:|---|---:|---:|",
    ]
    for idx, row in enumerate(report["ranked"][:18], start=1):
        boot = report["bootstrap"].get(row["policy"], {})
        lines.append(
            f"| {idx} | {row['policy']} | {row['entries']} | {row['settled']} | {row['wins']}/{row['losses']} | "
            f"{fmt(row['coverage_pct'])} | {fmt(row['net_cents_after_entry_fee'])} | {fmt(row['avg_brier'])} | "
            f"{row['approved_entry_count']}/{row['added_reject_count']} | "
            f"{fmt(row['avg_fee_friction_prob'])}/{fmt(row['avg_depth_friction_prob'])}/{fmt(row['avg_expensive_low_edge_friction_prob'])}/{fmt(row['avg_repeated_side_friction_prob'])} | "
            f"{fmt(boot.get('net_p10'))}/{fmt(boot.get('net_p50'))} | {fmt(boot.get('prob_positive'))} |"
        )
    lines.extend([
        "",
        "## Broad Candidates With Nonnegative Early/Late Net",
        "",
    ])
    for row in report["ranked"]:
        coverage = row.get("coverage_pct")
        if coverage is None or not (70.0 <= float(coverage) <= 90.0):
            continue
        temp = report["temporal"].get(row["policy"], {})
        early_net = ((temp.get("early") or {}).get("net_cents_after_entry_fee"))
        late_net = ((temp.get("late") or {}).get("net_cents_after_entry_fee"))
        if early_net is None or late_net is None or float(early_net) < 0 or float(late_net) < 0:
            continue
        lines.append(
            f"- `{row['policy']}`: coverage `{fmt(coverage)}`, net `{fmt(row.get('net_cents_after_entry_fee'))}`, "
            f"brier `{fmt(row.get('avg_brier'))}`, early/late net `{fmt(early_net)}/{fmt(late_net)}`"
        )
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
