"""Payoff-aware uncertainty lower-bound FV diagnostic for v28.

Research-only; no live bot changes or orders.

Physics hypothesis:
    A 15-minute BTC boundary contract is not priced by a point estimate alone.
    Near the strike, high recross hazard, first observation, and thin edge
    make the fair value estimate fragile. A profitable broad policy should
    require the lower confidence version of FV to still beat executable price.
"""
from __future__ import annotations

import csv
import json
import math
import random
from pathlib import Path
from typing import Any

from probe_v28_continuous_scorecard import watched_markets
from probe_v28_rmt_forgetting_entry_bakeoff import estimate_entry_fee_cents
from probe_v28_rmt_regime_diagnostic import attach_regime_rows
from probe_v28_shadow_entry_policy_bakeoff import base_tradeable, observation_pool
from probe_v28_state_aware_fv_candidates import enrich_state, p_raw


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
OUT_JSON = OUT_DIR / "v28_uncertainty_lower_bound_fv_latest.json"
OUT_CSV = OUT_DIR / "v28_uncertainty_lower_bound_fv_latest.csv"
OUT_MD = OUT_DIR / "v28_uncertainty_lower_bound_fv_latest.md"

BOOTSTRAP_SEED = 28111
BOOTSTRAP_RUNS = 2000


def as_float(value: Any) -> float | None:
    if value is None or value == "":
        return None
    try:
        out = float(value)
    except (TypeError, ValueError):
        return None
    return out if math.isfinite(out) else None


def ask_prob(row: dict[str, Any]) -> float | None:
    ask = as_float(row.get("ask_prob"))
    if ask is None:
        return None
    return ask if ask <= 1.0 else ask / 100.0


def observation_index(row: dict[str, Any]) -> float:
    value = as_float(row.get("market_side_observation_index"))
    return 0.0 if value is None else max(0.0, value)


def uncertainty_tags(row: dict[str, Any]) -> list[str]:
    tags: list[str] = []
    p = p_raw(row)
    abs_d = as_float(row.get("abs_d_sigma")) or 0.0
    recross = as_float(row.get("recross_hazard_score")) or 0.0
    ask = ask_prob(row)
    edge = None if ask is None else p - ask
    depth = as_float(row.get("eligible_depth"))
    if observation_index(row) <= 0.0:
        tags.append("first_observation")
    if p < 0.60:
        tags.append("weak_raw")
    if abs_d <= 0.25:
        tags.append("near_boundary")
    if recross >= 0.80:
        tags.append("high_recross")
    if edge is not None and edge < 0.03:
        tags.append("thin_edge")
    if ask is not None and ask >= 0.75 and edge is not None and edge < 0.06:
        tags.append("expensive_thin_edge")
    if depth is not None and depth <= 150.0:
        tags.append("thin_depth")
    return tags


def effective_sample_size(row: dict[str, Any]) -> float:
    """Heuristic information mass behind the point estimate.

    This is intentionally low-complexity and monotone: distance from boundary
    and repeated same-side observations add confidence; high recross and thin
    edge remove confidence.
    """
    p = p_raw(row)
    abs_d = as_float(row.get("abs_d_sigma")) or 0.0
    recross = as_float(row.get("recross_hazard_score")) or 0.0
    ask = ask_prob(row)
    edge = 0.0 if ask is None else max(0.0, p - ask)
    repeated = min(4.0, observation_index(row))
    n_eff = 18.0 + 32.0 * min(1.5, abs_d) + 10.0 * repeated + 120.0 * min(0.08, edge)
    if recross >= 0.90:
        n_eff *= 0.55
    elif recross >= 0.75:
        n_eff *= 0.75
    if edge < 0.02:
        n_eff *= 0.70
    if p < 0.60 and abs_d <= 0.25:
        n_eff *= 0.65
    return max(6.0, min(120.0, n_eff))


def lower_bound_probability(row: dict[str, Any], z: float) -> float:
    p = p_raw(row)
    n_eff = effective_sample_size(row)
    sigma = math.sqrt(max(0.0, p * (1.0 - p)) / n_eff)
    return max(0.0, min(1.0, p - z * sigma))


def fee_prob(row: dict[str, Any]) -> float:
    qty = max(1, int(row.get("qty") or 2))
    return estimate_entry_fee_cents(row) / (100.0 * qty)


def picked_rows(rows: list[dict[str, Any]], z: float, min_p: float, min_edge: float, fee_mult: float) -> list[dict[str, Any]]:
    picked: dict[str, dict[str, Any]] = {}
    for row in sorted(rows, key=lambda item: str(item.get("ts_wall") or "")):
        if not base_tradeable(row):
            continue
        ask = ask_prob(row)
        if ask is None:
            continue
        p_lb = lower_bound_probability(row, z)
        edge = p_lb - ask - fee_mult * fee_prob(row)
        if p_lb < min_p or edge < min_edge:
            continue
        market = str(row.get("market") or "")
        if market and market not in picked:
            picked[market] = {
                **row,
                "p_raw": p_raw(row),
                "p_eff": p_lb,
                "uncertainty_z": z,
                "n_eff": effective_sample_size(row),
                "ask_prob_norm": ask,
                "eff_edge_prob_after_fee": edge,
                "uncertainty_tags": ",".join(uncertainty_tags(row)),
                "net_gross_cents_after_entry_fee": None
                if row.get("gross_cents") is None
                else float(row.get("gross_cents") or 0.0) - estimate_entry_fee_cents(row),
            }
    return [picked[key] for key in sorted(picked)]


def summarize(policy: str, rows: list[dict[str, Any]], watched_count: int) -> dict[str, Any]:
    resolved = [row for row in rows if row.get("gross_cents") is not None]
    settled = [row for row in rows if row.get("side_won") is not None]
    net = sum(float(row.get("net_gross_cents_after_entry_fee") or 0.0) for row in resolved)
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
        "coverage_pct": 100.0 * len(rows) / watched_count if watched_count else None,
        "net_cents_after_entry_fee": net,
        "avg_net_cents_after_entry_fee": net / len(resolved) if resolved else None,
        "avg_brier": sum(briers) / len(briers) if briers else None,
        "approved_entry_count": sum(1 for row in rows if row.get("source") == "approved_entry"),
        "added_reject_count": sum(1 for row in rows if row.get("source") == "rejected_actionable"),
        "avg_n_eff": avg(row.get("n_eff") for row in rows),
    }


def avg(values: Any) -> float | None:
    nums = [float(value) for value in values if value is not None]
    return sum(nums) / len(nums) if nums else None


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
    rng = random.Random(BOOTSTRAP_SEED + len(markets))
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


def tag_summary(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    by_tag: dict[str, list[dict[str, Any]]] = {}
    for row in rows:
        for tag in str(row.get("uncertainty_tags") or "untagged").split(","):
            by_tag.setdefault(tag or "untagged", []).append(row)
    out = []
    for tag, tagged in sorted(by_tag.items()):
        settled = [row for row in tagged if row.get("side_won") is not None]
        out.append({
            "tag": tag,
            "entries": len(tagged),
            "settled": len(settled),
            "wins": sum(1 for row in settled if row.get("side_won") is True),
            "losses": sum(1 for row in settled if row.get("side_won") is False),
            "net_cents": sum(float(row.get("net_gross_cents_after_entry_fee") or 0.0) for row in tagged if row.get("gross_cents") is not None),
        })
    return sorted(out, key=lambda row: float(row["net_cents"]))


def build_report() -> dict[str, Any]:
    rows = enrich_state(attach_regime_rows(observation_pool()))
    watched = sorted(watched_markets())
    selected: list[dict[str, Any]] = []
    summaries: list[dict[str, Any]] = []
    boots: dict[str, Any] = {}
    for z in [0.0, 0.25, 0.50, 0.75, 1.0]:
        for min_p, min_edge, fee_mult in [(0.50, 0.0, 0.0), (0.50, 0.0, 1.0), (0.52, 0.0, 0.0), (0.50, 0.01, 1.0)]:
            policy = f"ulb_z{z:.2f}_p{int(min_p * 100)}_edge{int(min_edge * 100)}_fee{int(fee_mult)}"
            picked = picked_rows(rows, z, min_p, min_edge, fee_mult)
            for row in picked:
                row["policy"] = policy
            selected.extend(picked)
            summaries.append(summarize(policy, picked, len(watched)))
            boots[policy] = bootstrap(picked)
    ranked = sorted(
        summaries,
        key=lambda row: (
            0 if 75.0 <= float(row.get("coverage_pct") or 0.0) <= 90.0 else 1,
            -float(row.get("net_cents_after_entry_fee") or -10**9),
            float(row.get("avg_brier") or 10**9),
        ),
    )
    best_policy = ranked[0]["policy"] if ranked else None
    best_rows = [row for row in selected if row.get("policy") == best_policy]
    return {
        "watched_markets": len(watched),
        "observation_rows": len(rows),
        "summary": ranked,
        "bootstrap": boots,
        "tag_summary_best": tag_summary(best_rows)[:20],
        "rows": selected,
    }


def fmt(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, float):
        return f"{value:.6f}"
    return str(value)


def write_outputs(report: dict[str, Any]) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8")
    with OUT_CSV.open("w", newline="", encoding="utf-8") as handle:
        fieldnames = [
            "policy", "market", "source", "side", "p_raw", "p_eff", "ask_prob_norm",
            "eff_edge_prob_after_fee", "n_eff", "uncertainty_tags", "side_won",
            "net_gross_cents_after_entry_fee",
        ]
        writer = csv.DictWriter(handle, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(report.get("rows") or [])
    lines = [
        "# v28 Uncertainty Lower-Bound FV",
        "",
        "Research-only diagnostic. Treats FV as a noisy estimate and trades only when the lower-bound probability still clears price.",
        "",
        f"- Watched markets: `{report.get('watched_markets')}`",
        f"- Observation rows: `{report.get('observation_rows')}`",
        "",
        "## Ranked Policies",
        "",
        "| rank | policy | entries | settled | W/L | coverage | net c | avg c | brier | actual/sim | n_eff | boot p10/p50 | boot p>0 |",
        "|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for idx, row in enumerate((report.get("summary") or [])[:20], start=1):
        boot = (report.get("bootstrap") or {}).get(row.get("policy"), {})
        lines.append(
            f"| {idx} | {row.get('policy')} | {row.get('entries')} | {row.get('settled')} | "
            f"{row.get('wins')}/{row.get('losses')} | {fmt(row.get('coverage_pct'))} | "
            f"{fmt(row.get('net_cents_after_entry_fee'))} | {fmt(row.get('avg_net_cents_after_entry_fee'))} | "
            f"{fmt(row.get('avg_brier'))} | {row.get('approved_entry_count')}/{row.get('added_reject_count')} | "
            f"{fmt(row.get('avg_n_eff'))} | {fmt(boot.get('net_p10'))}/{fmt(boot.get('net_p50'))} | {fmt(boot.get('prob_positive'))} |"
        )
    lines.extend([
        "",
        "## Best Policy Loss Tags",
        "",
        "| tag | entries | settled | W/L | net c |",
        "|---|---:|---:|---:|---:|",
    ])
    for row in report.get("tag_summary_best") or []:
        lines.append(
            f"| {row.get('tag')} | {row.get('entries')} | {row.get('settled')} | "
            f"{row.get('wins')}/{row.get('losses')} | {fmt(row.get('net_cents'))} |"
        )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    report = build_report()
    write_outputs(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
