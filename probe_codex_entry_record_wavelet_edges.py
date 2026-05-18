from __future__ import annotations

import argparse
import json
import math
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from probe_codex_entry_path_geometry_edges import (
    StrategySpec,
    robust_positive_scan,
    run_strategy,
    select_family_best,
    sensitivity,
    walk_forward_summary,
)
from probe_codex_entry_timing_edges import delayed_entry_pnl
from probe_codex_terminal_salvage_all_trades import (
    EDGE_DIR,
    discover_datasets,
    load_dataset_cases,
    run_baseline,
)
from probe_stop_touch_confirmation import (
    append_ledger,
    idea_key,
    strategy_id,
    update_strategy_memory,
)


UTC = timezone.utc


def safe_float(value: Any) -> float:
    try:
        parsed = float(value)
    except (TypeError, ValueError):
        return math.nan
    return parsed if not math.isnan(parsed) else math.nan


def pressure(point: dict[str, Any]) -> float:
    own_bid = safe_float(point.get("own_bid"))
    opp_bid = safe_float(point.get("opp_bid"))
    denom = own_bid + opp_bid
    return opp_bid / denom if denom > 0 else math.nan


def spread(point: dict[str, Any]) -> float:
    own_bid = safe_float(point.get("own_bid"))
    own_ask = safe_float(point.get("own_ask"))
    return own_ask - own_bid if not math.isnan(own_bid) and not math.isnan(own_ask) else math.nan


def mean(values: list[float]) -> float:
    clean = [value for value in values if not math.isnan(value)]
    return sum(clean) / len(clean) if clean else math.nan


def quote_features(points: list[dict[str, Any]]) -> dict[str, Any] | None:
    valid = [
        point
        for point in points
        if not math.isnan(safe_float(point.get("elapsed"))) and not math.isnan(safe_float(point.get("held_ask")))
    ]
    if len(valid) < 3:
        return None

    asks = [safe_float(point["held_ask"]) for point in valid]
    times = [safe_float(point["elapsed"]) for point in valid]
    current = asks[-1]
    start = asks[0]
    elapsed = times[-1]
    span = max(1.0, elapsed - times[0])
    high = max(asks)
    low = min(asks)
    last_high_idx = max(idx for idx, ask in enumerate(asks) if ask == high)
    last_low_idx = max(idx for idx, ask in enumerate(asks) if ask == low)
    age_high = elapsed - times[last_high_idx]
    age_low = elapsed - times[last_low_idx]
    range_cents = high - low
    location = (current - low) / (range_cents + 1.0)
    record_pressure = (age_low - age_high) / span
    drawup_from_low = current - low
    drawdown_from_high = high - current

    deltas = [asks[idx] - asks[idx - 1] for idx in range(1, len(asks))]
    path_len = sum(abs(delta) for delta in deltas)
    net = current - start
    roughness_dim = 1.0 + math.log((path_len + 1.0) / (abs(net) + 1.0)) / math.log(max(3, len(asks)))
    roughness_dim = max(1.0, roughness_dim)

    mid = len(asks) // 2
    first_mean = mean(asks[:mid])
    second_mean = mean(asks[mid:])
    coarse_momentum = second_mean - first_mean if not math.isnan(first_mean) and not math.isnan(second_mean) else 0.0
    pair_energy_terms = [(asks[idx] - asks[idx - 1]) ** 2 for idx in range(1, len(asks))]
    high_freq_energy = mean(pair_energy_terms)
    if math.isnan(high_freq_energy):
        high_freq_energy = 0.0
    noise_ratio = high_freq_energy / (coarse_momentum * coarse_momentum + 1.0)
    directional_snr = coarse_momentum / (math.sqrt(high_freq_energy) + 1.0)

    end_pressure = pressure(valid[-1])
    return {
        "elapsed": elapsed,
        "held_ask": current,
        "start_ask": start,
        "high": high,
        "low": low,
        "range": range_cents,
        "location": location,
        "record_pressure": record_pressure,
        "age_high": age_high,
        "age_low": age_low,
        "drawup_from_low": drawup_from_low,
        "drawdown_from_high": drawdown_from_high,
        "roughness_dim": roughness_dim,
        "path_len": path_len,
        "net": net,
        "coarse_momentum": coarse_momentum,
        "high_freq_energy": high_freq_energy,
        "noise_ratio": noise_ratio,
        "directional_snr": directional_snr,
        "pressure_end": end_pressure,
        "spread": spread(valid[-1]),
        "bid_sum": safe_float(valid[-1].get("bid_sum")),
    }


def prepare_case(case: dict[str, Any], delays: tuple[int, ...]) -> dict[str, Any]:
    path = [
        point
        for point in case.get("path", [])
        if not math.isnan(safe_float(point.get("elapsed"))) and not math.isnan(safe_float(point.get("held_ask")))
    ]
    snapshots: dict[str, dict[str, Any] | None] = {}
    for delay in delays:
        history: list[dict[str, Any]] = []
        found = False
        for point in path:
            history.append(point)
            if safe_float(point.get("elapsed")) >= delay:
                found = True
                break
        snapshots[str(delay)] = quote_features(history) if found else None
    return snapshots


def entry_meta(case: dict[str, Any], ask: float, features: dict[str, Any]) -> tuple[float, dict[str, Any]]:
    pnl = delayed_entry_pnl(case, ask)
    return pnl, {
        "enter": True,
        "entry_ask": ask,
        "entry_elapsed": features.get("elapsed"),
        "contracts": int(case["qty"]),
        "record_pressure": round(safe_float(features.get("record_pressure")), 6),
        "location": round(safe_float(features.get("location")), 6),
        "roughness_dim": round(safe_float(features.get("roughness_dim")), 6),
        "coarse_momentum": round(safe_float(features.get("coarse_momentum")), 6),
        "noise_ratio": round(safe_float(features.get("noise_ratio")), 6),
        "directional_snr": round(safe_float(features.get("directional_snr")), 6),
    }


def sim_record_age_reversal_admission(
    case: dict[str, Any], prepared: dict[str, Any], params: dict[str, Any]
) -> tuple[float, dict[str, Any]]:
    features = prepared.get(str(int(params["delay_seconds"])))
    if not features:
        return 0.0, {"enter": False, "skip_reason": "missing_delay_snapshot"}
    if (
        features["held_ask"] <= float(params["max_entry_ask"])
        and features["record_pressure"] >= float(params["min_record_pressure"])
        and features["location"] >= float(params["min_location"])
        and features["age_high"] <= float(params["max_high_age_seconds"])
        and features["age_low"] >= float(params["min_low_age_seconds"])
        and features["pressure_end"] <= float(params["max_opp_pressure"])
        and features["spread"] <= float(params["max_spread"])
    ):
        return entry_meta(case, safe_float(features["held_ask"]), features)
    return 0.0, {"enter": False, "skip_reason": "record_age_gate_failed"}


def sim_quote_haar_energy_admission(
    case: dict[str, Any], prepared: dict[str, Any], params: dict[str, Any]
) -> tuple[float, dict[str, Any]]:
    features = prepared.get(str(int(params["delay_seconds"])))
    if not features:
        return 0.0, {"enter": False, "skip_reason": "missing_delay_snapshot"}
    if (
        features["held_ask"] <= float(params["max_entry_ask"])
        and features["coarse_momentum"] >= float(params["min_coarse_momentum"])
        and features["noise_ratio"] <= float(params["max_noise_ratio"])
        and features["directional_snr"] >= float(params["min_directional_snr"])
        and features["roughness_dim"] <= float(params["max_roughness_dim"])
        and features["pressure_end"] <= float(params["max_opp_pressure"])
        and features["spread"] <= float(params["max_spread"])
    ):
        return entry_meta(case, safe_float(features["held_ask"]), features)
    return 0.0, {"enter": False, "skip_reason": "haar_energy_gate_failed"}


def build_strategy_grid() -> list[StrategySpec]:
    strategies: list[StrategySpec] = []

    def add(
        family: str,
        theorem: str,
        equation: str,
        params: dict[str, Any],
        simulator: Any,
    ) -> None:
        strategies.append(StrategySpec(family, theorem, equation, params, simulator))

    for delay_seconds in (30, 60, 90, 120):
        for max_entry_ask in (86, 88, 90, 92):
            for min_record_pressure in (0.0, 0.25, 0.5):
                for min_location in (0.55, 0.70, 0.85):
                    for max_high_age_seconds in (30, 60, 120):
                        for min_low_age_seconds in (15, 45, 90):
                            for max_spread in (4, 6):
                                for max_opp_pressure in (0.25, 0.35, 0.50):
                                    add(
                                        "record_age_reversal_admission",
                                        "A delayed entry is healthier when the current quote is near a fresh path high while the last path low is stale, indicating recovery rather than a fresh breakdown.",
                                        "R=(age_low-age_high)/T and L=(H_t-min(H))/(max(H)-min(H)+1); enter at delay D only if H_t<=A, R>=r, L>=l, age_high<=u, age_low>=v, p_opp<=p, and spread<=S.",
                                        {
                                            "delay_seconds": delay_seconds,
                                            "max_entry_ask": max_entry_ask,
                                            "min_record_pressure": min_record_pressure,
                                            "min_location": min_location,
                                            "max_high_age_seconds": max_high_age_seconds,
                                            "min_low_age_seconds": min_low_age_seconds,
                                            "max_spread": max_spread,
                                            "max_opp_pressure": max_opp_pressure,
                                        },
                                        sim_record_age_reversal_admission,
                                    )

    for delay_seconds in (30, 60, 90, 120):
        for max_entry_ask in (86, 88, 90, 92, 94):
            for min_coarse_momentum in (-2.0, 0.0, 1.0, 2.0):
                for max_noise_ratio in (0.5, 1.0, 2.0, 4.0):
                    for min_directional_snr in (0.0, 0.5, 1.0):
                        for max_roughness_dim in (1.15, 1.35, 1.60):
                            for max_spread in (4, 6):
                                for max_opp_pressure in (0.25, 0.35, 0.50):
                                    add(
                                        "quote_haar_energy_admission",
                                        "A pre-entry quote path with positive coarse-scale movement and low short-scale Haar energy should be safer than a noisy path with the same terminal ask.",
                                        "M=mean(H_second_half)-mean(H_first_half), E=mean(delta H^2), N=E/(M^2+1), Z=M/(sqrt(E)+1), F=1+log((sum|delta H|+1)/(|H_t-H_0|+1))/log(n); enter if H_t<=A, M>=m, N<=n, Z>=z, F<=f, p_opp<=p, and spread<=S.",
                                        {
                                            "delay_seconds": delay_seconds,
                                            "max_entry_ask": max_entry_ask,
                                            "min_coarse_momentum": min_coarse_momentum,
                                            "max_noise_ratio": max_noise_ratio,
                                            "min_directional_snr": min_directional_snr,
                                            "max_roughness_dim": max_roughness_dim,
                                            "max_spread": max_spread,
                                            "max_opp_pressure": max_opp_pressure,
                                        },
                                        sim_quote_haar_energy_admission,
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
        "# Codex Entry Record/Wavelet Edge Research",
        "",
        f"- Generated: `{payload['generated_at']}`",
        f"- Datasets: `{', '.join(payload['datasets'])}`",
        f"- Quote-path cases: `{payload['case_count']}`",
        "- Scope: research-only entry/no-trade simulation; live bot logic, configs, run scripts, and processes were not changed.",
        "- Non-repetition: this tests quote record-age renewal and Haar-style short-scale energy, not prior neighbor LCB, Bayesian-cell, BTC synthetic EV, pressure impulse, path coherence, or delayed-entry threshold families.",
        "",
        "## Baselines",
        "",
        f"- Actual recorded PnL: `${actual['sim_pnl']}`",
        f"- No-stop hold-to-settlement PnL using original entries: `${no_stop['sim_pnl']}`",
        f"- First held-ask <=70 exit baseline: `${stop70['sim_pnl']}`",
        "- Skip every opportunity baseline: `$0.0`",
        f"- Walk-forward split: `{payload['walk_forward']['split_entry_ts']}`",
        "",
        "## New Equation Families",
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
    lines.extend([""])

    lines.extend(
        [
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
            "- Record age asks whether recovery is confirmed by a fresh local quote high rather than just a low terminal ask.",
            "- Haar energy asks whether coarse quote movement dominates short-scale noise, so a noisy path and a clean path with the same delayed ask are treated differently.",
            "- The test is causal: every feature is computed from quote snapshots available no later than the simulated decision delay.",
            "- Treat positive results as research candidates only; live entry, exit, config, and process state were not touched.",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Research-only record-age and wavelet entry probes for Kalshi BTC 15m.")
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
    json_path = EDGE_DIR / f"codex_entry_record_wavelet_research_{stamp}.json"
    md_path = EDGE_DIR / f"codex_entry_record_wavelet_research_{stamp}.md"
    latest_json = EDGE_DIR / "codex_entry_record_wavelet_research_latest.json"
    latest_md = EDGE_DIR / "codex_entry_record_wavelet_research_latest.md"
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
            "record_age_reversal_admission": "held ask path, own/opposite bids, spread, and record timestamps through the configured delay",
            "quote_haar_energy_admission": "held ask increments, first/second half means, own/opposite bids, and spread through the configured delay",
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
                "train_summary": walk_family["train_summary"],
                "holdout_summary": walk_family["holdout_summary"],
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
