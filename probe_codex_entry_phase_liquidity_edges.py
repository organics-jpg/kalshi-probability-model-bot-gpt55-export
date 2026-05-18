from __future__ import annotations

import argparse
import json
import math
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from probe_codex_entry_sequence_likelihood_edges import (
    StrategySpec,
    delayed_entry_pnl,
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


def mean(values: list[float]) -> float:
    clean = [value for value in values if not math.isnan(value)]
    return sum(clean) / len(clean) if clean else math.nan


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


def path_features(prepared: dict[str, Any], params: dict[str, Any]) -> dict[str, Any] | None:
    points = valid_prefix(prepared, params)
    if len(points) < int(params.get("min_points", 2)):
        return None

    asks = [safe_float(point["held_ask"]) for point in points]
    pressures = [pressure(point) for point in points]
    pressure100 = [100.0 * value for value in pressures]
    bid_sums = [safe_float(point["bid_sum"]) for point in points]
    slacks = [100.0 - value for value in bid_sums]
    spreads = [spread(point) for point in points]

    current = asks[-1]
    start = asks[0]
    discount = max(0.0, start - current)
    pressure_relief = pressure100[0] - pressure100[-1]
    ask_path = sum(abs(asks[idx] - asks[idx - 1]) for idx in range(1, len(asks)))
    pressure_path = sum(abs(pressure100[idx] - pressure100[idx - 1]) for idx in range(1, len(pressure100)))
    loop_area = 0.0
    for idx in range(1, len(asks)):
        loop_area += (asks[idx - 1] - start) * (pressure100[idx] - pressure100[idx - 1])
        loop_area -= (pressure100[idx - 1] - pressure100[0]) * (asks[idx] - asks[idx - 1])
    loop_norm = loop_area / (ask_path + pressure_path + 1.0)
    phase_relief_score = discount * pressure_relief - abs(loop_norm)

    spread_start = spreads[0]
    spread_end = spreads[-1]
    spread_compression = spread_start - spread_end
    bid_sum_min = min(bid_sums)
    bid_recovery = bid_sums[-1] - bid_sum_min
    absorption_score = (
        discount
        * max(0.0, spread_compression)
        * max(0.0, bid_recovery)
        / (1.0 + max(0.0, pressure100[-1]))
    )

    residual_score = math.nan
    residual_points = 0
    if len(points) >= int(params.get("min_reg_points", 4)):
        x_rows = [[pressure100[idx], slacks[idx], spreads[idx]] for idx in range(len(points))]
        means = [mean([row[col] for row in x_rows]) for col in range(3)]
        y_mean = mean(asks)
        centered_x = [[row[col] - means[col] for col in range(3)] for row in x_rows]
        centered_y = [ask - y_mean for ask in asks]
        ridge = float(params.get("ridge_lambda", 2.0))
        xtx = [[0.0 for _ in range(3)] for _ in range(3)]
        xty = [0.0 for _ in range(3)]
        for row, y_value in zip(centered_x, centered_y):
            for i in range(3):
                xty[i] += row[i] * y_value
                for j in range(3):
                    xtx[i][j] += row[i] * row[j]
        for idx in range(3):
            xtx[idx][idx] += ridge
        beta = solve_linear(xtx, xty)
        if beta is not None:
            end_x = [x_rows[-1][col] - means[col] for col in range(3)]
            predicted = y_mean + sum(beta[col] * end_x[col] for col in range(3))
            residual_score = predicted - current
            residual_points = len(points)

    return {
        "held_ask": current,
        "start_ask": start,
        "discount": discount,
        "pressure_end": pressures[-1],
        "pressure_relief_cents": pressure_relief,
        "spread_end": spread_end,
        "spread_compression": spread_compression,
        "bid_sum_end": bid_sums[-1],
        "bid_recovery": bid_recovery,
        "phase_loop_norm": loop_norm,
        "phase_relief_score": phase_relief_score,
        "absorption_score": absorption_score,
        "book_state_residual_score": residual_score,
        "residual_points": residual_points,
        "elapsed": safe_float(points[-1]["elapsed"]),
    }


def base_gate(features: dict[str, Any], params: dict[str, Any]) -> bool:
    values = (
        safe_float(features.get("held_ask")),
        safe_float(features.get("pressure_end")),
        safe_float(features.get("spread_end")),
        safe_float(features.get("bid_sum_end")),
    )
    if any(math.isnan(value) for value in values):
        return False
    return (
        features["held_ask"] <= float(params["max_entry_ask"])
        and features["pressure_end"] <= float(params["max_opp_pressure"])
        and features["spread_end"] <= float(params["max_spread"])
        and features["bid_sum_end"] >= float(params["min_bid_sum"])
    )


def entry_with_score(case: dict[str, Any], features: dict[str, Any], extra: dict[str, Any]) -> tuple[float, dict[str, Any]]:
    ask = safe_float(features["held_ask"])
    return entry_meta(case, ask, features, extra)


def sim_phase_loop_pressure_admission(
    case: dict[str, Any], prepared: dict[str, Any], params: dict[str, Any], model: dict[str, Any] | None
) -> tuple[float, dict[str, Any]]:
    del model
    features = path_features(prepared, params)
    if not features or not base_gate(features, params):
        return 0.0, {"enter": False, "skip_reason": "missing_or_failed_gate"}
    if (
        features["discount"] >= float(params["min_discount_cents"])
        and features["phase_relief_score"] >= float(params["min_phase_relief"])
        and abs(features["phase_loop_norm"]) <= float(params["max_abs_loop_norm"])
    ):
        return entry_with_score(
            case,
            features,
            {
                "phase_relief_score": round(safe_float(features["phase_relief_score"]), 6),
                "phase_loop_norm": round(safe_float(features["phase_loop_norm"]), 6),
                "pressure_relief_cents": round(safe_float(features["pressure_relief_cents"]), 4),
                "discount_cents": round(safe_float(features["discount"]), 4),
            },
        )
    return 0.0, {"enter": False, "skip_reason": "phase_loop_gate_failed"}


def sim_liquidity_absorption_discount_admission(
    case: dict[str, Any], prepared: dict[str, Any], params: dict[str, Any], model: dict[str, Any] | None
) -> tuple[float, dict[str, Any]]:
    del model
    features = path_features(prepared, params)
    if not features or not base_gate(features, params):
        return 0.0, {"enter": False, "skip_reason": "missing_or_failed_gate"}
    if (
        features["discount"] >= float(params["min_discount_cents"])
        and features["bid_recovery"] >= float(params["min_bid_recovery"])
        and features["spread_compression"] >= float(params["min_spread_compression"])
        and features["absorption_score"] >= float(params["min_absorption_score"])
    ):
        return entry_with_score(
            case,
            features,
            {
                "absorption_score": round(safe_float(features["absorption_score"]), 6),
                "bid_recovery": round(safe_float(features["bid_recovery"]), 4),
                "spread_compression": round(safe_float(features["spread_compression"]), 4),
                "discount_cents": round(safe_float(features["discount"]), 4),
            },
        )
    return 0.0, {"enter": False, "skip_reason": "absorption_gate_failed"}


def sim_book_state_residual_admission(
    case: dict[str, Any], prepared: dict[str, Any], params: dict[str, Any], model: dict[str, Any] | None
) -> tuple[float, dict[str, Any]]:
    del model
    features = path_features(prepared, params)
    if not features or not base_gate(features, params):
        return 0.0, {"enter": False, "skip_reason": "missing_or_failed_gate"}
    residual_score = safe_float(features["book_state_residual_score"])
    if (
        not math.isnan(residual_score)
        and features["discount"] >= float(params["min_discount_cents"])
        and residual_score >= float(params["min_negative_residual_cents"])
    ):
        return entry_with_score(
            case,
            features,
            {
                "book_state_residual_score": round(residual_score, 6),
                "residual_points": int(features["residual_points"]),
                "discount_cents": round(safe_float(features["discount"]), 4),
            },
        )
    return 0.0, {"enter": False, "skip_reason": "book_state_residual_gate_failed"}


def build_strategy_grid() -> list[StrategySpec]:
    strategies: list[StrategySpec] = []

    def add(family: str, theorem: str, equation: str, params: dict[str, Any], simulator: Any) -> None:
        strategies.append(StrategySpec(family, theorem, equation, params, simulator))

    phase_equation = (
        "C=(H0-HD)*(100*p0-100*pD)-abs(sum((H_i-H0)d(100p_i)-(100p_i-100p0)dH_i))/(sum|dH|+sum|d100p|+1); "
        "enter if H_D<=A, C>=c, |loop|<=L, discount>=d, p_D<=P, spread<=S, and bid_sum>=B."
    )
    absorption_equation = (
        "A=(H0-HD)*max(0,bid_sum_D-min(bid_sum))*max(0,spread_0-spread_D)/(1+100*p_D); "
        "enter if A>=a, discount>=d, bid recovery>=r, spread compression>=s, and final book gates pass."
    )
    residual_equation = (
        "Fit H=a+b1*(100*p_opp)+b2*(100-bid_sum)+b3*spread on the prefix using ridge regression; "
        "R=H_hat_D-H_D; enter if R>=r, discount>=d, and final book gates pass."
    )

    for delay_seconds in (60, 120):
        for max_entry_ask in (84, 88, 92):
            for max_opp_pressure in (0.25, 0.50):
                for min_bid_sum in (0, 96):
                    for min_discount_cents in (0, 4):
                        for min_phase_relief in (-20, 20):
                            add(
                                "phase_loop_pressure_admission",
                                "A quote discount is more credible when opposing pressure has discharged and the quote-pressure trajectory does not trace a large hysteresis loop.",
                                phase_equation,
                                {
                                    "delay_seconds": delay_seconds,
                                    "max_entry_ask": max_entry_ask,
                                    "max_opp_pressure": max_opp_pressure,
                                    "max_spread": 4,
                                    "min_bid_sum": min_bid_sum,
                                    "min_points": 2,
                                    "min_discount_cents": min_discount_cents,
                                    "min_phase_relief": min_phase_relief,
                                    "max_abs_loop_norm": 999,
                                },
                                sim_phase_loop_pressure_admission,
                            )

    for delay_seconds in (60, 120):
        for max_entry_ask in (84, 88, 92):
            for max_opp_pressure in (0.25, 0.50):
                for min_bid_sum in (0, 96):
                    for min_discount_cents in (0, 4):
                        for min_absorption_score in (0, 4):
                            for min_bid_recovery in (0, 2):
                                add(
                                    "liquidity_absorption_discount_admission",
                                    "A lower ask is safer when the book appears to absorb the move: bid depth recovers from the interval low while the spread compresses into the delayed quote.",
                                    absorption_equation,
                                    {
                                        "delay_seconds": delay_seconds,
                                        "max_entry_ask": max_entry_ask,
                                        "max_opp_pressure": max_opp_pressure,
                                        "max_spread": 4,
                                        "min_bid_sum": min_bid_sum,
                                        "min_points": 2,
                                        "min_discount_cents": min_discount_cents,
                                        "min_absorption_score": min_absorption_score,
                                        "min_bid_recovery": min_bid_recovery,
                                        "min_spread_compression": 0,
                                    },
                                    sim_liquidity_absorption_discount_admission,
                                )

    for delay_seconds in (60, 120):
        for max_entry_ask in (84, 88, 92):
            for max_opp_pressure in (0.25, 0.50):
                for min_bid_sum in (0, 96):
                    for min_discount_cents in (0, 2):
                        for min_negative_residual_cents in (0.5, 2.0):
                            add(
                                "book_state_residual_admission",
                                "A delayed ask can be mispriced relative to the same prefix's pressure, slack, and spread state; require a negative ask residual instead of raw cheapness.",
                                residual_equation,
                                {
                                    "delay_seconds": delay_seconds,
                                    "max_entry_ask": max_entry_ask,
                                    "max_opp_pressure": max_opp_pressure,
                                    "max_spread": 4,
                                    "min_bid_sum": min_bid_sum,
                                    "min_points": 4,
                                    "min_reg_points": 4,
                                    "ridge_lambda": 2.0,
                                    "min_discount_cents": min_discount_cents,
                                    "min_negative_residual_cents": min_negative_residual_cents,
                                },
                                sim_book_state_residual_admission,
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
        "# Codex Entry Phase/Liquidity Edge Research",
        "",
        f"- Generated: `{payload['generated_at']}`",
        f"- Datasets: `{', '.join(payload['datasets'])}`",
        f"- Quote-path cases: `{payload['case_count']}`",
        "- Scope: research-only entry/no-trade simulation; live bot logic, configs, run scripts, and processes were not changed.",
        "- Non-repetition: this tests quote-pressure hysteresis, liquidity absorption, and intra-book residual equations rather than prior pressure impulse, dwell integrity, slack elasticity, token likelihood, BTC lag, or neighbor/Bayes families.",
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
            "- Phase-loop pressure is not another pressure impulse threshold: it scores the signed quote-pressure path plus endpoint relief and penalizes hysteresis.",
            "- Liquidity absorption is not dwell integrity: it requires the cheaper ask to arrive with spread compression and recovery from the bid-sum low.",
            "- Book-state residual is an intra-Kalshi mispricing check: the delayed ask must be below the prefix-implied ask from pressure, slack, and spread.",
            "- Treat positive rows as research candidates only; live entry, exit, config, and process state were not touched.",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Research-only phase/liquidity entry probes.")
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
    json_path = EDGE_DIR / f"codex_entry_phase_liquidity_research_{stamp}.json"
    md_path = EDGE_DIR / f"codex_entry_phase_liquidity_research_{stamp}.md"
    latest_json = EDGE_DIR / "codex_entry_phase_liquidity_research_latest.json"
    latest_md = EDGE_DIR / "codex_entry_phase_liquidity_research_latest.md"
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
            "phase_loop_pressure_admission": "held ask, own/opposite bids, spread, bid_sum, and elapsed quote path through the configured delay",
            "liquidity_absorption_discount_admission": "held ask discount, spread compression, bid_sum recovery, pressure, and final spread through the configured delay",
            "book_state_residual_admission": "prefix-only held ask, pressure, bid_sum slack, and spread for ridge residual at the configured delay",
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
