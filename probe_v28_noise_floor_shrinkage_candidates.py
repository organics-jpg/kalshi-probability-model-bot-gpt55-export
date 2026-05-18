"""Noise-floor shrinkage candidates for v28 fair value.

The hypothesis is deliberately physical rather than fitted:
- v28's raw side probability is useful as a direction signal.
- Some states make that probability less reliable without proving the opposite
  side: near-strike recross hazard, stale feeds, repeated same-side evidence,
  and RMT-dominant/noisy feature geometry.
- In those states, shrink conviction toward 50 instead of anchoring to the
  book or flipping sides.

This is research-only. It writes reports under logs/edge_research and does not
touch live bot logic or orders.
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
from probe_v28_state_aware_fv_candidates import enrich_state, p_raw, p_rmt_memory_gate, p_rmt_repetition_forget


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
OUT_JSON = OUT_DIR / "v28_noise_floor_shrinkage_candidates_latest.json"
OUT_CSV = OUT_DIR / "v28_noise_floor_shrinkage_candidates_latest.csv"
OUT_MD = OUT_DIR / "v28_noise_floor_shrinkage_candidates_latest.md"
BOOTSTRAP_SEED = 28117
BOOTSTRAP_RUNS = 2000


def as_float(value: Any) -> float | None:
    if value is None or value == "":
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def clamp01(value: float) -> float:
    return max(0.000001, min(0.999999, value))


def ask_prob(row: dict[str, Any]) -> float | None:
    return as_float(row.get("ask_prob"))


def shrink_to_half(p: float, reliability: float) -> float:
    return clamp01(0.5 + (p - 0.5) * max(0.0, min(1.0, reliability)))


def near_strike_penalty(row: dict[str, Any]) -> float:
    abs_d = as_float(row.get("abs_d_sigma"))
    if abs_d is None:
        return 0.0
    if abs_d <= 0.10:
        return 0.22
    if abs_d <= 0.25:
        return 0.14
    if abs_d <= 0.50:
        return 0.07
    return 0.0


def recross_penalty(row: dict[str, Any]) -> float:
    hazard = as_float(row.get("recross_hazard_score"))
    if hazard is None:
        return 0.0
    # Recross hazard is most damaging when the strike is still close enough to
    # be crossed repeatedly. Far from strike, the same hazard estimate is less
    # informative about terminal direction.
    multiplier = 1.0 if (as_float(row.get("abs_d_sigma")) or 999.0) <= 0.75 else 0.45
    return min(0.24, max(0.0, hazard) * 0.12 * multiplier)


def stale_penalty(row: dict[str, Any]) -> float:
    btc_age = as_float(row.get("btc_age_ms"))
    book_age = as_float(row.get("book_age_ms"))
    penalty = 0.0
    if btc_age is not None:
        if btc_age >= 750.0:
            penalty += 0.10
        elif btc_age >= 350.0:
            penalty += 0.05
    if book_age is not None:
        if book_age >= 1200.0:
            penalty += 0.08
        elif book_age >= 650.0:
            penalty += 0.04
    return min(0.14, penalty)


def rmt_noise_penalty(row: dict[str, Any]) -> float:
    tag = str(row.get("spectral_tag") or "")
    side_idx = int(row.get("market_side_observation_index") or 0)
    outlier_share = as_float(row.get("outlier_share")) or 0.0
    if tag == "spectral_factor" and side_idx == 0:
        return 0.0
    if tag == "spectral_dominant_factor":
        return min(0.16, 0.08 + 0.08 * outlier_share)
    if tag == "spectral_noise":
        return 0.12
    return 0.0


def repetition_penalty(row: dict[str, Any]) -> float:
    side_idx = int(row.get("market_side_observation_index") or 0)
    if side_idx <= 0:
        return 0.0
    return min(0.14, 0.035 * side_idx)


def time_penalty(row: dict[str, Any]) -> float:
    stc = as_float(row.get("seconds_to_close"))
    if stc is None:
        return 0.0
    if stc <= 60.0:
        return 0.08
    if stc <= 120.0:
        return 0.04
    return 0.0


def reliability_light(row: dict[str, Any]) -> float:
    penalty = near_strike_penalty(row) + recross_penalty(row) + 0.5 * stale_penalty(row)
    return 1.0 - min(0.45, penalty)


def reliability_full(row: dict[str, Any]) -> float:
    penalty = (
        near_strike_penalty(row)
        + recross_penalty(row)
        + stale_penalty(row)
        + rmt_noise_penalty(row)
        + repetition_penalty(row)
        + time_penalty(row)
    )
    return 1.0 - min(0.65, penalty)


def reliability_rmt_recency(row: dict[str, Any]) -> float:
    penalty = rmt_noise_penalty(row) + repetition_penalty(row) + stale_penalty(row)
    return 1.0 - min(0.48, penalty)


def weakraw_rmt_margin_penalty(row: dict[str, Any], rmt_p: float) -> float:
    ask = ask_prob(row)
    if ask is None or p_raw(row) >= 0.60:
        return 0.0
    margin = rmt_p - ask
    if margin < 0.00:
        return 0.34
    if margin < 0.01:
        return 0.24
    if margin < 0.02:
        return 0.14
    return 0.0


def reliability_weakraw_rmt_memory(row: dict[str, Any]) -> float:
    penalty = near_strike_penalty(row) + recross_penalty(row) + weakraw_rmt_margin_penalty(row, p_rmt_memory_gate(row))
    return 1.0 - min(0.62, penalty)


def reliability_weakraw_rmt_repetition(row: dict[str, Any]) -> float:
    penalty = near_strike_penalty(row) + recross_penalty(row) + weakraw_rmt_margin_penalty(row, p_rmt_repetition_forget(row))
    return 1.0 - min(0.62, penalty)


def p_light(row: dict[str, Any]) -> float:
    return shrink_to_half(p_raw(row), reliability_light(row))


def p_full(row: dict[str, Any]) -> float:
    return shrink_to_half(p_raw(row), reliability_full(row))


def p_rmt_recency(row: dict[str, Any]) -> float:
    return shrink_to_half(p_raw(row), reliability_rmt_recency(row))


def p_weakraw_rmt_memory(row: dict[str, Any]) -> float:
    return shrink_to_half(p_raw(row), reliability_weakraw_rmt_memory(row))


def p_weakraw_rmt_repetition(row: dict[str, Any]) -> float:
    return shrink_to_half(p_raw(row), reliability_weakraw_rmt_repetition(row))


FV: dict[str, Callable[[dict[str, Any]], float]] = {
    "v28_raw": p_raw,
    "noise_shrink_light": p_light,
    "noise_shrink_full": p_full,
    "noise_shrink_rmt_recency": p_rmt_recency,
    "noise_shrink_weakraw_rmt_memory": p_weakraw_rmt_memory,
    "noise_shrink_weakraw_rmt_repetition": p_weakraw_rmt_repetition,
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
        ask = ask_prob(row)
        if ask is None:
            continue
        try:
            p_eff = fn(row)
        except (KeyError, TypeError, ValueError):
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
                "reliability_light": reliability_light(row),
                "reliability_full": reliability_full(row),
                "reliability_rmt_recency": reliability_rmt_recency(row),
                "reliability_weakraw_rmt_memory": reliability_weakraw_rmt_memory(row),
                "reliability_weakraw_rmt_repetition": reliability_weakraw_rmt_repetition(row),
                "near_strike_penalty": near_strike_penalty(row),
                "recross_penalty": recross_penalty(row),
                "stale_penalty": stale_penalty(row),
                "rmt_noise_penalty": rmt_noise_penalty(row),
                "repetition_penalty": repetition_penalty(row),
                "time_penalty": time_penalty(row),
                "weakraw_rmt_memory_margin_penalty": weakraw_rmt_margin_penalty(row, p_rmt_memory_gate(row)),
                "weakraw_rmt_repetition_margin_penalty": weakraw_rmt_margin_penalty(row, p_rmt_repetition_forget(row)),
                "net_gross_cents_after_entry_fee": None if row.get("gross_cents") is None else float(row.get("gross_cents") or 0.0) - estimate_entry_fee_cents(row),
            }
    return [picked[key] for key in sorted(picked)]


def avg(values: Any) -> float | None:
    nums = [float(value) for value in values if value is not None]
    return sum(nums) / len(nums) if nums else None


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
        "avg_reliability_light": avg(row.get("reliability_light") for row in rows),
        "avg_reliability_full": avg(row.get("reliability_full") for row in rows),
        "avg_reliability_rmt_recency": avg(row.get("reliability_rmt_recency") for row in rows),
    }


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


def penalty_attribution(selected: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for tag, fn in [
        ("near_strike", lambda row: row.get("near_strike_penalty")),
        ("recross", lambda row: row.get("recross_penalty")),
        ("stale", lambda row: row.get("stale_penalty")),
        ("rmt_noise", lambda row: row.get("rmt_noise_penalty")),
        ("repetition", lambda row: row.get("repetition_penalty")),
        ("late", lambda row: row.get("time_penalty")),
    ]:
        bucket = [row for row in selected if float(fn(row) or 0.0) > 0.0]
        if not bucket:
            continue
        rows.append(
            {
                "tag": tag,
                "count": len(bucket),
                "settled": sum(1 for row in bucket if row.get("side_won") is not None),
                "wins": sum(1 for row in bucket if row.get("side_won") is True),
                "losses": sum(1 for row in bucket if row.get("side_won") is False),
                "net_cents_after_entry_fee": sum(float(row.get("net_gross_cents_after_entry_fee") or 0.0) for row in bucket if row.get("gross_cents") is not None),
                "avg_raw_p": avg(row.get("raw_p_eff") for row in bucket),
                "avg_p_eff": avg(row.get("p_eff") for row in bucket),
            }
        )
    return rows


def build_report() -> dict[str, Any]:
    rows = enrich_state(attach_regime_rows(observation_pool()))
    watched = sorted(watched_markets())
    selected: list[dict[str, Any]] = []
    summary: list[dict[str, Any]] = []
    boot: dict[str, Any] = {}
    attribution: dict[str, Any] = {}
    for fv_name, fn in FV.items():
        for suffix, min_p, min_edge in THRESHOLDS:
            policy = f"{fv_name}_{suffix}"
            picked = selected_rows(rows, fv_name, fn, min_p, min_edge)
            for row in picked:
                row["policy"] = policy
            selected.extend(picked)
            summary.append(summarize_policy(policy, picked, len(watched)))
            boot[policy] = bootstrap(picked)
            attribution[policy] = penalty_attribution(picked)
    ranked = sorted(
        summary,
        key=lambda row: (
            -float(row.get("net_cents_after_entry_fee") or -10**9),
            abs(float(row.get("coverage_pct") or 0.0) - 78.0),
            float(row.get("avg_brier") or 999.0),
        ),
    )
    return {
        "physics": {
            "hypothesis": "Shrink raw v28 toward 50 in noisy states instead of using book/RMT to flip sides.",
            "not_overfit_by_design": [
                "No coefficients are fitted to realized PnL.",
                "Penalties are monotone reliability discounts from market mechanics.",
                "Promotion still requires frozen forward validation.",
            ],
        },
        "watched_markets": len(watched),
        "summary": summary,
        "ranked": ranked,
        "bootstrap": boot,
        "penalty_attribution": attribution,
        "selected_rows": selected,
    }


def write_report(report: dict[str, Any]) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True, default=str), encoding="utf-8")
    selected = report["selected_rows"]
    if selected:
        with OUT_CSV.open("w", newline="", encoding="utf-8") as fh:
            fieldnames = sorted({key for row in selected for key in row})
            writer = csv.DictWriter(fh, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(selected)
    lines = [
        "# v28 Noise-Floor Shrinkage Candidates",
        "",
        "Research-only FV candidates. The model keeps raw v28 direction but shrinks confidence toward 50 in noisy physical states.",
        "",
        "| rank | policy | entries | settled | W/L | coverage | net c | avg c | brier | boot p10 | boot p>0 |",
        "|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for idx, row in enumerate(report["ranked"][:12], start=1):
        boot = report["bootstrap"].get(row["policy"], {})
        lines.append(
            f"| {idx} | {row['policy']} | {row['entries']} | {row['settled']} | "
            f"{row['wins']}/{row['losses']} | {row['coverage_pct']} | {row['net_cents_after_entry_fee']} | "
            f"{row['avg_net_cents_after_entry_fee']} | {row['avg_brier']} | {boot.get('net_p10')} | {boot.get('prob_positive')} |"
        )
    lines.extend(["", "## Penalty Attribution"])
    for policy in [row["policy"] for row in report["ranked"][:4]]:
        lines.append("")
        lines.append(f"### {policy}")
        rows = report["penalty_attribution"].get(policy, [])
        if not rows:
            lines.append("- No penalty tags fired.")
            continue
        for row in rows:
            lines.append(
                f"- `{row['tag']}`: count `{row['count']}`, settled `{row['settled']}`, "
                f"W/L `{row['wins']}/{row['losses']}`, net `{row['net_cents_after_entry_fee']}c`, "
                f"avg raw/p `{row['avg_raw_p']}/{row['avg_p_eff']}`"
            )
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "- This is a discovery diagnostic, not a promotion gate.",
            "- A useful candidate must keep roughly 75-80% coverage, improve Brier or net against raw v28, and then survive frozen forward validation.",
        ]
    )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    report = build_report()
    write_report(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
