from __future__ import annotations

import argparse
import json
import math
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from probe_codex_entry_sequence_likelihood_edges import (
    StrategySpec,
    entry_meta,
    prepare_case,
    run_strategy,
    select_family_best,
    sensitivity,
    spread,
    safe_float,
    walk_forward_summary,
    robust_positive_scan,
)
from probe_codex_terminal_salvage_all_trades import EDGE_DIR, discover_datasets, load_dataset_cases, run_baseline
from probe_stop_touch_confirmation import append_ledger, idea_key, update_strategy_memory


UTC = timezone.utc


def pressure(point: dict[str, Any]) -> float:
    own_bid = safe_float(point.get("own_bid"))
    opp_bid = safe_float(point.get("opp_bid"))
    denom = own_bid + opp_bid
    return opp_bid / denom if denom > 0 else math.nan


def valid_prefix(prepared: dict[str, Any], params: dict[str, Any]) -> list[dict[str, Any]]:
    delay = str(int(params["delay_seconds"]))
    points = prepared.get(delay) or []
    valid: list[dict[str, Any]] = []
    for point in points:
        held_ask = safe_float(point.get("held_ask"))
        own_bid = safe_float(point.get("own_bid"))
        opp_bid = safe_float(point.get("opp_bid"))
        own_ask = safe_float(point.get("own_ask"))
        bid_sum = safe_float(point.get("bid_sum"))
        elapsed = safe_float(point.get("elapsed"))
        if any(math.isnan(value) for value in (held_ask, own_bid, opp_bid, own_ask, bid_sum, elapsed)):
            continue
        valid.append(point)
    return valid


def solve_linear(system: list[list[float]], rhs: list[float]) -> list[float] | None:
    n = len(rhs)
    aug = [row[:] + [rhs[idx]] for idx, row in enumerate(system)]
    for col in range(n):
        pivot = max(range(col, n), key=lambda row: abs(aug[row][col]))
        if abs(aug[pivot][col]) < 1e-9:
            return None
        aug[col], aug[pivot] = aug[pivot], aug[col]
        scale = aug[col][col]
        for jdx in range(col, n + 1):
            aug[col][jdx] /= scale
        for row in range(n):
            if row == col:
                continue
            factor = aug[row][col]
            for jdx in range(col, n + 1):
                aug[row][jdx] -= factor * aug[col][jdx]
    return [aug[row][n] for row in range(n)]


def fit_quadratic(times: list[float], values: list[float]) -> list[float] | None:
    if len(times) < 3:
        return None
    start = times[0]
    span = max(1.0, times[-1] - start)
    xs = [(value - start) / span for value in times]
    xtx = [[0.0 for _ in range(3)] for _ in range(3)]
    xty = [0.0 for _ in range(3)]
    for x, y in zip(xs, values):
        row = [1.0, x, x * x]
        for i in range(3):
            xty[i] += row[i] * y
            for j in range(3):
                xtx[i][j] += row[i] * row[j]
    return solve_linear(xtx, xty)


def spectral_stats(deltas: list[float]) -> dict[str, float]:
    n = len(deltas)
    if n < 2:
        return {"low_share": math.nan, "entropy": math.nan, "score": math.nan}
    energies: list[float] = []
    for k in range(1, n + 1):
        coeff = 0.0
        for idx, delta in enumerate(deltas):
            coeff += delta * math.cos(math.pi * k * (idx + 0.5) / n)
        energies.append(coeff * coeff)
    total = sum(energies)
    if total <= 1e-9:
        return {"low_share": 0.0, "entropy": 0.0, "score": 0.0}
    low_count = min(2, len(energies))
    low_share = sum(energies[:low_count]) / total
    probs = [energy / total for energy in energies if energy > 1e-12]
    entropy = -sum(prob * math.log(prob) for prob in probs) / math.log(len(energies))
    realized_var = sum(delta * delta for delta in deltas) / max(1, len(deltas))
    trend = sum(deltas)
    score = trend * low_share / math.sqrt(realized_var + 1.0) - entropy
    return {"low_share": low_share, "entropy": entropy, "score": score}


def path_features(prepared: dict[str, Any], params: dict[str, Any]) -> dict[str, Any] | None:
    points = valid_prefix(prepared, params)
    if len(points) < int(params.get("min_points", 2)):
        return None

    asks = [safe_float(point["held_ask"]) for point in points]
    times = [safe_float(point["elapsed"]) for point in points]
    pressures = [pressure(point) for point in points]
    bid_sums = [safe_float(point["bid_sum"]) for point in points]
    spreads = [spread(point) for point in points]
    current = asks[-1]
    start = asks[0]
    low = min(asks)
    high = max(asks)
    deltas = [asks[idx] - asks[idx - 1] for idx in range(1, len(asks))]
    spec = spectral_stats(deltas)

    coeffs = fit_quadratic(times, asks)
    if coeffs is None:
        intercept = slope = curvature = projected_gain = curvature_rebound_score = math.nan
    else:
        intercept, slope, curvature = coeffs
        next_x = 1.0 + float(params.get("projection_fraction", 0.5))
        projected = intercept + slope * next_x + curvature * next_x * next_x
        projected_gain = projected - current
        curvature_rebound_score = curvature + max(0.0, current - low) - max(0.0, -projected_gain)

    spread_start = spreads[0]
    spread_end = spreads[-1]
    spread_compression = spread_start - spread_end
    bid_sum_min = min(bid_sums)
    bid_recovery = bid_sums[-1] - bid_sum_min
    discount = max(0.0, start - current)
    pressure_end = pressures[-1]
    absorption_score = (
        discount
        * max(0.0, bid_recovery)
        * max(0.0, spread_compression)
        / (1.0 + max(0.0, 100.0 * pressure_end))
    )

    return {
        "held_ask": current,
        "start_ask": start,
        "low": low,
        "high": high,
        "discount": discount,
        "pressure_end": pressure_end,
        "spread_end": spread_end,
        "spread_compression": spread_compression,
        "bid_sum_end": bid_sums[-1],
        "bid_recovery": bid_recovery,
        "elapsed": times[-1],
        "point_count": len(points),
        "quad_slope": slope,
        "quad_curvature": curvature,
        "quad_projected_gain": projected_gain,
        "quad_rebound_score": curvature_rebound_score,
        "spectral_low_share": spec["low_share"],
        "spectral_entropy": spec["entropy"],
        "spectral_score": spec["score"],
        "absorption_score": absorption_score,
    }


def base_gate(features: dict[str, Any], params: dict[str, Any]) -> bool:
    required = (
        safe_float(features.get("held_ask")),
        safe_float(features.get("pressure_end")),
        safe_float(features.get("spread_end")),
        safe_float(features.get("bid_sum_end")),
    )
    if any(math.isnan(value) for value in required):
        return False
    return (
        features["held_ask"] <= float(params["max_entry_ask"])
        and features["pressure_end"] <= float(params["max_opp_pressure"])
        and features["spread_end"] <= float(params["max_spread"])
        and features["bid_sum_end"] >= float(params["min_bid_sum"])
    )


def entry_with_features(case: dict[str, Any], features: dict[str, Any], extra: dict[str, Any]) -> tuple[float, dict[str, Any]]:
    ask = safe_float(features["held_ask"])
    return entry_meta(case, ask, features, extra)


def sim_quadratic_rebound_curvature_admission(
    case: dict[str, Any], prepared: dict[str, Any], params: dict[str, Any], model: dict[str, Any] | None
) -> tuple[float, dict[str, Any]]:
    del model
    features = path_features(prepared, params)
    if not features or not base_gate(features, params):
        return 0.0, {"enter": False, "skip_reason": "missing_or_failed_gate"}
    score = safe_float(features["quad_rebound_score"])
    projected_gain = safe_float(features["quad_projected_gain"])
    if (
        not math.isnan(score)
        and not math.isnan(projected_gain)
        and score >= float(params["min_rebound_score"])
        and projected_gain >= float(params["min_projected_gain"])
    ):
        return entry_with_features(
            case,
            features,
            {
                "quad_rebound_score": round(score, 6),
                "quad_curvature": round(safe_float(features["quad_curvature"]), 6),
                "quad_projected_gain": round(projected_gain, 4),
                "point_count": int(features["point_count"]),
            },
        )
    return 0.0, {"enter": False, "skip_reason": "quadratic_gate_failed"}


def sim_spectral_persistence_discount_admission(
    case: dict[str, Any], prepared: dict[str, Any], params: dict[str, Any], model: dict[str, Any] | None
) -> tuple[float, dict[str, Any]]:
    del model
    features = path_features(prepared, params)
    if not features or not base_gate(features, params):
        return 0.0, {"enter": False, "skip_reason": "missing_or_failed_gate"}
    score = safe_float(features["spectral_score"])
    low_share = safe_float(features["spectral_low_share"])
    entropy = safe_float(features["spectral_entropy"])
    if (
        not math.isnan(score)
        and low_share >= float(params["min_low_frequency_share"])
        and entropy <= float(params["max_spectral_entropy"])
        and score >= float(params["min_spectral_score"])
        and features["discount"] >= float(params["min_discount_cents"])
    ):
        return entry_with_features(
            case,
            features,
            {
                "spectral_score": round(score, 6),
                "spectral_low_share": round(low_share, 6),
                "spectral_entropy": round(entropy, 6),
                "discount_cents": round(safe_float(features["discount"]), 4),
            },
        )
    return 0.0, {"enter": False, "skip_reason": "spectral_gate_failed"}


def sim_side_polarized_absorption_admission(
    case: dict[str, Any], prepared: dict[str, Any], params: dict[str, Any], model: dict[str, Any] | None
) -> tuple[float, dict[str, Any]]:
    del model
    side_gate = str(params["side_gate"]).lower()
    if side_gate != "both" and str(case.get("side", "")).lower() != side_gate:
        return 0.0, {"enter": False, "skip_reason": "side_gate_failed"}
    features = path_features(prepared, params)
    if not features or not base_gate(features, params):
        return 0.0, {"enter": False, "skip_reason": "missing_or_failed_gate"}
    if (
        features["discount"] >= float(params["min_discount_cents"])
        and features["bid_recovery"] >= float(params["min_bid_recovery"])
        and features["spread_compression"] >= float(params["min_spread_compression"])
        and features["absorption_score"] >= float(params["min_absorption_score"])
    ):
        return entry_with_features(
            case,
            features,
            {
                "side_gate": side_gate,
                "absorption_score": round(safe_float(features["absorption_score"]), 6),
                "bid_recovery": round(safe_float(features["bid_recovery"]), 4),
                "spread_compression": round(safe_float(features["spread_compression"]), 4),
                "discount_cents": round(safe_float(features["discount"]), 4),
            },
        )
    return 0.0, {"enter": False, "skip_reason": "side_absorption_gate_failed"}


def build_strategy_grid() -> list[StrategySpec]:
    strategies: list[StrategySpec] = []

    for delay in (120, 180):
        for max_entry_ask in (84, 88):
            for max_opp_pressure in (0.25, 0.5):
                for min_rebound_score in (0, 5, 10):
                    for min_projected_gain in (0, 2, 5):
                        strategies.append(
                            StrategySpec(
                                family="quadratic_rebound_curvature_admission",
                                theorem=(
                                    "A low delayed ask is safer when a prefix-only quadratic fit has positive "
                                    "rebound curvature and projects the held ask upward after the entry delay."
                                ),
                                equation=(
                                    "Fit H(t)=a+b*t+c*t^2 on the prefix; "
                                    "Q=c+max(0,H_D-min(H))-max(0,-(H_proj-H_D)); enter if H_D<=A, "
                                    "Q>=q, H_proj-H_D>=g, p_opp<=P, spread<=S, and bid_sum>=B."
                                ),
                                params={
                                    "delay_seconds": delay,
                                    "max_entry_ask": max_entry_ask,
                                    "max_opp_pressure": max_opp_pressure,
                                    "max_spread": 4,
                                    "min_bid_sum": 0,
                                    "min_points": 3,
                                    "projection_fraction": 0.5,
                                    "min_rebound_score": min_rebound_score,
                                    "min_projected_gain": min_projected_gain,
                                },
                                simulator=sim_quadratic_rebound_curvature_admission,
                            )
                        )

    for delay in (120, 180):
        for max_entry_ask in (84, 88):
            for max_opp_pressure in (0.25, 0.5):
                for min_low_share in (0.25, 0.5):
                    for max_entropy in (0.85, 1.0):
                        for min_score in (-1.0, 0.0):
                            for min_discount in (0, 2):
                                strategies.append(
                                    StrategySpec(
                                        family="spectral_persistence_discount_admission",
                                        theorem=(
                                            "Quote moves with concentrated low-frequency energy are less likely to "
                                            "be random churn; cheap entries should require persistent prefix structure."
                                        ),
                                        equation=(
                                            "DCT energy E_k on held-ask increments; "
                                            "S=(H_D-H_0)*sum(E_low)/sum(E)/sqrt(QV+1)-entropy(E); enter if H_D<=A, "
                                            "low_share>=L, entropy<=M, S>=s, discount>=d, p_opp<=P, spread<=Z."
                                        ),
                                        params={
                                            "delay_seconds": delay,
                                            "max_entry_ask": max_entry_ask,
                                            "max_opp_pressure": max_opp_pressure,
                                            "max_spread": 4,
                                            "min_bid_sum": 0,
                                            "min_points": 3,
                                            "min_low_frequency_share": min_low_share,
                                            "max_spectral_entropy": max_entropy,
                                            "min_spectral_score": min_score,
                                            "min_discount_cents": min_discount,
                                        },
                                        simulator=sim_spectral_persistence_discount_admission,
                                    )
                                )

    for side_gate in ("yes", "no", "both"):
        for max_entry_ask in (84, 88):
            for max_opp_pressure in (0.25, 0.5):
                for min_absorption in (0, 1):
                    strategies.append(
                        StrategySpec(
                            family="side_polarized_absorption_admission",
                            theorem=(
                                "The prior liquidity-absorption candidate may be directionally asymmetric; "
                                "side-gated absorption tests whether YES and NO books should share a rule."
                            ),
                            equation=(
                                "A=(H0-HD)*max(0,bid_sum_D-min(bid_sum))*max(0,spread_0-spread_D)/(1+100*p_D); "
                                "enter only if side in G and A>=a, spread compression>=s, H_D<=Amax, p_D<=P."
                            ),
                            params={
                                "delay_seconds": 120,
                                "max_entry_ask": max_entry_ask,
                                "max_opp_pressure": max_opp_pressure,
                                "max_spread": 4,
                                "min_bid_sum": 0,
                                "min_points": 2,
                                "side_gate": side_gate,
                                "min_absorption_score": min_absorption,
                                "min_bid_recovery": 0,
                                "min_spread_compression": 0,
                                "min_discount_cents": 0,
                            },
                            simulator=sim_side_polarized_absorption_admission,
                        )
                    )

    return strategies


def status_for(family: str, result: dict[str, Any], payload: dict[str, Any]) -> str:
    summary = result["summary"]
    holdout = payload["walk_forward"]["families"][family]["holdout_summary"]
    robust_count = len(payload["robust_positive_scan"].get(family, []))
    if (
        summary["delta_vs_no_trade_all"] > 0
        and holdout["delta_vs_no_trade_all"] > 0
        and summary["entries"] >= 20
        and holdout["entries"] >= 5
        and robust_count >= 3
    ):
        return "candidate_for_human_review"
    if summary["delta_vs_no_trade_all"] > 0 and holdout["delta_vs_no_trade_all"] > 0:
        return "watchlist_positive_but_sparse_or_sensitive"
    return "tested_not_robust"


def write_markdown(path: Path, payload: dict[str, Any]) -> None:
    actual = payload["baselines"]["actual"]["summary"]
    no_stop = payload["baselines"]["no_stop"]["summary"]
    stop70 = payload["baselines"]["held_ask_stop_70"]["summary"]
    lines = [
        "# Codex Entry Curvature/Spectral Edge Research",
        "",
        f"- Generated: `{payload['generated_at']}`",
        f"- Datasets: `{', '.join(payload['datasets'])}`",
        f"- Quote-path cases: `{payload['case_count']}`",
        "- Scope: research-only entry/no-trade simulation; live bot logic, configs, run scripts, and processes were not changed.",
        "- Non-repetition: this tests prefix quadratic curvature and spectral energy concentration; side-polarized absorption is included only as a validation branch for the prior candidate's YES/NO asymmetry.",
        "",
        "## Baselines",
        "",
        f"- Actual recorded PnL: `${actual['sim_pnl']}`",
        f"- No-stop hold-to-settlement PnL using original entries: `${no_stop['sim_pnl']}`",
        f"- First held-ask <=70 exit baseline: `${stop70['sim_pnl']}`",
        "- Skip every opportunity baseline: `$0.0`",
        f"- Walk-forward split: `{payload['walk_forward']['split_entry_ts']}`",
        "",
        "## Equation Families",
        "",
    ]
    for family, result in payload["best_by_family"].items():
        summary = result["summary"]
        walk = payload["walk_forward"]["families"][family]
        holdout = walk["holdout_summary"]
        lines.extend(
            [
                f"### {family} `{result['strategy_id']}`",
                "",
                f"- Status: {status_for(family, result, payload)}",
                f"- Theorem: {result['theorem']}",
                f"- Equation: `{result['equation']}`",
                f"- Full-sample best params: `{json.dumps(result['params'], sort_keys=True)}`",
                f"- Full-sample PnL / delta vs actual / delta vs no-stop / delta vs skip-all: `${summary['sim_pnl']}` / `${summary['delta_vs_actual']}` / `${summary['delta_vs_no_stop']}` / `${summary['delta_vs_no_trade_all']}`",
                f"- Entries / skipped winners / skipped losers / win rate: `{summary['entries']} / {summary['skipped_settlement_winners']} / {summary['skipped_settlement_losers']} / {summary['entry_win_rate']}`",
                f"- Avg entry ask / contract fraction / worst trade: `{summary['avg_entry_ask']} / {summary['contract_fraction']} / {summary['worst_trade']}`",
                f"- Train-selected params: `{json.dumps(walk['selected_params'], sort_keys=True)}`",
                f"- Train-selected holdout PnL / delta vs actual / delta vs no-stop / delta vs skip-all: `${holdout['sim_pnl']}` / `${holdout['delta_vs_actual']}` / `${holdout['delta_vs_no_stop']}` / `${holdout['delta_vs_no_trade_all']}`",
                f"- Holdout entries / skipped winners / skipped losers / win rate: `{holdout['entries']} / {holdout['skipped_settlement_winners']} / {holdout['skipped_settlement_losers']} / {holdout['entry_win_rate']}`",
                "",
            ]
        )

    lines.extend(
        [
            "## By Dataset",
            "",
            "| Family | Dataset | PnL | Delta vs actual | Delta vs no-stop | Entries | Win rate |",
            "|---|---|---:|---:|---:|---:|---:|",
        ]
    )
    for family, result in payload["best_by_family"].items():
        for dataset, summary in result["by_dataset"].items():
            lines.append(
                f"| `{family}` | `{dataset}` | {summary['sim_pnl']} | {summary['delta_vs_actual']} | "
                f"{summary['delta_vs_no_stop']} | {summary['entries']} | {summary['entry_win_rate']} |"
            )

    lines.extend(
        [
            "",
            "## By Side",
            "",
            "| Family | Side | PnL | Delta vs skip-all | Entries | Win rate | Avg ask |",
            "|---|---|---:|---:|---:|---:|---:|",
        ]
    )
    for family, result in payload["best_by_family"].items():
        for side, summary in result["by_side"].items():
            lines.append(
                f"| `{family}` | `{side}` | {summary['sim_pnl']} | {summary['delta_vs_no_trade_all']} | "
                f"{summary['entries']} | {summary['entry_win_rate']} | {summary['avg_entry_ask']} |"
            )

    lines.extend(
        [
            "",
            "## Robust Positive Split Scan",
            "",
            "| Family | Strategy | Train PnL | Holdout PnL | Holdout entries | Holdout win rate | Params |",
            "|---|---|---:|---:|---:|---:|---|",
        ]
    )
    for family, rows in payload["robust_positive_scan"].items():
        if not rows:
            lines.append(f"| `{family}` | none |  |  |  |  | no train-positive and holdout-positive parameterization found |")
            continue
        for row in rows[:5]:
            lines.append(
                f"| `{family}` | `{row['strategy_id']}` | {row['train_sim_pnl']} | {row['holdout_sim_pnl']} | "
                f"{row['holdout_entries']} | {row['holdout_entry_win_rate']} | `{json.dumps(row['params'], sort_keys=True)}` |"
            )

    lines.extend(
        [
            "",
            "## Nearby Sensitivity",
            "",
            "| Family | Params | PnL | Delta vs skip-all | Entries | Win rate | Skipped W/L |",
            "|---|---|---:|---:|---:|---:|---:|",
        ]
    )
    for family, rows in payload["sensitivity"].items():
        for row in rows[:6]:
            lines.append(
                f"| `{family}` | `{json.dumps(row['params'], sort_keys=True)}` | {row['sim_pnl']} | "
                f"{row['delta_vs_no_trade_all']} | {row['entries']} | {row['entry_win_rate']} | "
                f"{row['skipped_winners']}/{row['skipped_losers']} |"
            )

    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "- Quadratic rebound curvature is a causal prefix-only path-shape test, not a fixed stop or simple delay threshold.",
            "- Spectral persistence checks whether quote changes are concentrated in low-frequency structure rather than noisy churn.",
            "- Side-polarized absorption validates the prior liquidity-absorption candidate's side asymmetry; it should not be treated as a new independent equation family.",
            "- Treat positive rows as research candidates only; live entry, exit, config, and process state were not touched.",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Research-only curvature, spectral, and side-absorption entry probes.")
    parser.add_argument("--refresh-cache", action="store_true")
    parser.add_argument("--datasets", nargs="*", default=None)
    args = parser.parse_args()

    datasets = args.datasets or discover_datasets()
    payloads = [load_dataset_cases(dataset, refresh_cache=args.refresh_cache) for dataset in datasets]
    cases: list[dict[str, Any]] = []
    for payload in payloads:
        dataset = payload.get("dataset")
        for case in payload.get("cases", []):
            case.setdefault("dataset", dataset)
            cases.append(case)
    cases = sorted(cases, key=lambda case: (case["entry_ts"], case["market"], case["side"]))

    strategies = build_strategy_grid()
    delays = tuple(sorted({int(strategy.params["delay_seconds"]) for strategy in strategies}))
    prepped = [(case, prepare_case(case, delays)) for case in cases]
    results = [run_strategy(prepped, strategy) for strategy in strategies]
    best_by_family = select_family_best(results)
    walk = walk_forward_summary(prepped, strategies)
    robust_scan = robust_positive_scan(strategies, prepped)
    baselines = {
        "actual": run_baseline(cases, "actual"),
        "no_stop": run_baseline(cases, "no_stop"),
        "held_ask_stop_70": run_baseline(cases, "held_ask_stop_70"),
    }

    generated_at = datetime.now(UTC).isoformat()
    stamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
    json_path = EDGE_DIR / f"codex_entry_curvature_spectral_research_{stamp}.json"
    md_path = EDGE_DIR / f"codex_entry_curvature_spectral_research_{stamp}.md"
    latest_json = EDGE_DIR / "codex_entry_curvature_spectral_research_latest.json"
    latest_md = EDGE_DIR / "codex_entry_curvature_spectral_research_latest.md"
    report_payload = {
        "generated_at": generated_at,
        "dataset": "all_quote_path_trades",
        "datasets": sorted({case["dataset"] for case in cases}),
        "requested_datasets": datasets,
        "dataset_payloads": [
            {
                "dataset": item.get("dataset"),
                "raw_trades_total": item.get("raw_trades_total"),
                "trades_total": item.get("trades_total"),
                "case_count": len(item.get("cases", [])),
                "cache_path": item.get("cache_path"),
            }
            for item in payloads
        ],
        "case_count": len(cases),
        "strategy_count": len(strategies),
        "baselines": baselines,
        "best_by_family": best_by_family,
        "walk_forward": walk,
        "robust_positive_scan": robust_scan,
        "sensitivity": sensitivity(results, best_by_family),
        "json_path": str(json_path),
        "markdown_path": str(md_path),
        "feature_availability": {
            "quadratic_rebound_curvature_admission": "held ask, own/opposite bids, spread, bid_sum, and elapsed quote path through the configured delay",
            "spectral_persistence_discount_admission": "held ask increments and final book snapshot through the configured delay",
            "side_polarized_absorption_admission": "side label plus prefix-only held ask discount, bid_sum recovery, spread compression, pressure, and final spread through the configured delay",
        },
        "live_logic_changed": False,
    }

    EDGE_DIR.mkdir(parents=True, exist_ok=True)
    json_text = json.dumps(report_payload, indent=2, sort_keys=True)
    json_path.write_text(json_text, encoding="utf-8")
    latest_json.write_text(json_text, encoding="utf-8")
    write_markdown(md_path, report_payload)
    write_markdown(latest_md, report_payload)

    ledger_records: list[dict[str, Any]] = []
    for family, result in best_by_family.items():
        walk_family = walk["families"][family]
        ledger_records.append(
            {
                "recorded_at": generated_at,
                "generated_at": generated_at,
                "source": Path(__file__).name,
                "status": status_for(family, result, report_payload),
                "dataset": "all_quote_path_trades",
                "datasets": report_payload["datasets"],
                "family": family,
                "theorem": result["theorem"],
                "equation": result["equation"],
                "params": result["params"],
                "strategy_id": result["strategy_id"],
                "idea_key": idea_key(family, result["equation"], result["params"]),
                "summary": result["summary"],
                "by_side": result["by_side"],
                "train_summary": walk_family["train_summary"],
                "holdout_summary": walk_family["holdout_summary"],
                "holdout_by_side": walk_family["holdout_by_side"],
                "walk_forward_selected_strategy_id": walk_family["selected_strategy_id"],
                "walk_forward_selected_params": walk_family["selected_params"],
                "robust_positive_count": len(robust_scan.get(family, [])),
                "json_path": str(json_path),
                "markdown_path": str(md_path),
            }
        )
    append_ledger(ledger_records)
    update_strategy_memory(report_payload, best_by_family)

    print(f"Saved JSON: {json_path}")
    print(f"Saved Markdown: {md_path}")
    print(
        f"Cases={len(cases)} strategies={len(strategies)} "
        f"actual={baselines['actual']['summary']['sim_pnl']} "
        f"no_stop={baselines['no_stop']['summary']['sim_pnl']} "
        f"stop70={baselines['held_ask_stop_70']['summary']['sim_pnl']} "
        f"split={walk['split_entry_ts']}"
    )
    for family, result in best_by_family.items():
        summary = result["summary"]
        holdout = walk["families"][family]["holdout_summary"]
        print(
            f"{family} {result['strategy_id']} status={status_for(family, result, report_payload)} "
            f"full_sim={summary['sim_pnl']} full_delta_actual={summary['delta_vs_actual']} "
            f"full_delta_skip={summary['delta_vs_no_trade_all']} entries={summary['entries']} "
            f"holdout_sim={holdout['sim_pnl']} holdout_delta_actual={holdout['delta_vs_actual']} "
            f"holdout_delta_skip={holdout['delta_vs_no_trade_all']} holdout_entries={holdout['entries']}"
        )


if __name__ == "__main__":
    main()
