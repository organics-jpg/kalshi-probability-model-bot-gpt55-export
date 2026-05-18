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
from probe_stop_touch_confirmation import append_ledger, idea_key, strategy_id, update_strategy_memory


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
        required = (
            safe_float(point.get("elapsed")),
            safe_float(point.get("held_ask")),
            safe_float(point.get("own_bid")),
            safe_float(point.get("opp_bid")),
            safe_float(point.get("own_ask")),
            safe_float(point.get("bid_sum")),
        )
        if any(math.isnan(value) for value in required):
            continue
        valid.append(point)
    return valid


def mean(values: list[float]) -> float:
    return sum(values) / len(values) if values else math.nan


def stdev(values: list[float]) -> float:
    if len(values) < 2:
        return 0.0
    avg = mean(values)
    return math.sqrt(sum((value - avg) ** 2 for value in values) / len(values))


def dot(left: list[float], right: list[float]) -> float:
    return sum(a * b for a, b in zip(left, right))


def norm(values: list[float]) -> float:
    return math.sqrt(dot(values, values))


def first_pc(cov: list[list[float]]) -> tuple[list[float], float, float]:
    n = len(cov)
    vector = [1.0 / math.sqrt(n) for _ in range(n)]
    for _ in range(20):
        nxt = [sum(cov[row][col] * vector[col] for col in range(n)) for row in range(n)]
        length = norm(nxt)
        if length <= 1e-12:
            return vector, 0.0, sum(cov[i][i] for i in range(n))
        vector = [value / length for value in nxt]
    eigen = dot(vector, [sum(cov[row][col] * vector[col] for col in range(n)) for row in range(n)])
    trace = sum(cov[i][i] for i in range(n))
    return vector, max(0.0, eigen), max(0.0, trace)


def base_gate(case: dict[str, Any], features: dict[str, Any], params: dict[str, Any]) -> bool:
    side_filter = str(params.get("side_filter", "all")).lower()
    if side_filter != "all" and str(case.get("side", "")).lower() != side_filter:
        return False
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


def path_features(prepared: dict[str, Any], params: dict[str, Any]) -> dict[str, Any] | None:
    points = valid_prefix(prepared, params)
    if len(points) < int(params.get("min_points", 3)):
        return None

    asks = [safe_float(point["held_ask"]) for point in points]
    pressures = [pressure(point) for point in points]
    spreads = [spread(point) for point in points]
    bid_sums = [safe_float(point["bid_sum"]) for point in points]
    if any(math.isnan(value) for value in [*pressures, *spreads, *bid_sums]):
        return None

    series = [
        asks,
        [100.0 * (1.0 - item) for item in pressures],
        bid_sums,
        [100.0 - item for item in spreads],
    ]
    z_rows: list[list[float]] = []
    for idx in range(len(points)):
        row: list[float] = []
        for values in series:
            sigma = stdev(values)
            row.append(0.0 if sigma <= 1e-9 else (values[idx] - mean(values)) / sigma)
        z_rows.append(row)

    dim = len(z_rows[0])
    cov = [[0.0 for _ in range(dim)] for _ in range(dim)]
    for row in z_rows:
        for i in range(dim):
            for j in range(dim):
                cov[i][j] += row[i] * row[j]
    denom = max(1, len(z_rows) - 1)
    cov = [[value / denom for value in row] for row in cov]
    pc, lambda1, trace = first_pc(cov)
    favorable = [0.5, 0.5, 0.5, 0.5]
    if dot(pc, favorable) < 0:
        pc = [-value for value in pc]
    delta = [z_rows[-1][idx] - z_rows[0][idx] for idx in range(dim)]
    path_len = sum(norm([z_rows[idx][col] - z_rows[idx - 1][col] for col in range(dim)]) for idx in range(1, len(z_rows)))
    pca_flow_score = (lambda1 / (trace + 1e-9)) * dot(delta, pc) / math.sqrt(path_len + 1.0)

    ask_deltas = [asks[idx] - asks[idx - 1] for idx in range(1, len(asks))]
    rv = sum(delta_ask * delta_ask for delta_ask in ask_deltas)
    bv = 0.0
    for idx in range(1, len(ask_deltas)):
        bv += abs(ask_deltas[idx]) * abs(ask_deltas[idx - 1])
    bv *= math.pi / 2.0
    jump_excess = max(0.0, rv - bv)
    max_jump = max(ask_deltas, key=lambda value: abs(value)) if ask_deltas else 0.0
    signed_jump = math.copysign(jump_excess / (bv + 1.0), max_jump)
    jump_flow_score = (
        (asks[-1] - asks[0]) / math.sqrt(bv + 1.0)
        + float(params.get("jump_weight", 1.0)) * signed_jump
        - float(params.get("pressure_penalty", 0.0)) * pressures[-1]
        - float(params.get("spread_penalty", 0.0)) * spreads[-1]
    )

    relief_deltas = [100.0 * (pressures[idx - 1] - pressures[idx]) for idx in range(1, len(pressures))]
    lead_terms: list[float] = []
    lag_terms: list[float] = []
    for idx in range(1, min(len(ask_deltas), len(relief_deltas))):
        lead_terms.append(relief_deltas[idx - 1] * ask_deltas[idx])
        lag_terms.append(ask_deltas[idx - 1] * relief_deltas[idx])
    lead_scale = math.sqrt(sum(value * value for value in lead_terms) + sum(value * value for value in lag_terms) + 1.0)
    lead_lag_score = (sum(lead_terms) - sum(lag_terms)) / lead_scale
    lead_lag_score -= float(params.get("pressure_penalty", 0.0)) * pressures[-1]
    lead_lag_score -= float(params.get("spread_penalty", 0.0)) * spreads[-1]

    return {
        "held_ask": asks[-1],
        "start_ask": asks[0],
        "pressure_end": pressures[-1],
        "spread_end": spreads[-1],
        "bid_sum_end": bid_sums[-1],
        "pca_flow_score": pca_flow_score,
        "pca_lambda_share": lambda1 / (trace + 1e-9),
        "jump_flow_score": jump_flow_score,
        "jump_excess": jump_excess,
        "bipower_variation": bv,
        "realized_variation": rv,
        "lead_lag_score": lead_lag_score,
        "elapsed": safe_float(points[-1]["elapsed"]),
        "points": len(points),
    }


def entry_with_features(case: dict[str, Any], features: dict[str, Any], extra: dict[str, Any]) -> tuple[float, dict[str, Any]]:
    return entry_meta(case, safe_float(features["held_ask"]), features, extra)


def sim_pca_book_flow_admission(
    case: dict[str, Any], prepared: dict[str, Any], params: dict[str, Any], model: dict[str, Any] | None
) -> tuple[float, dict[str, Any]]:
    del model
    features = path_features(prepared, params)
    if not features or not base_gate(case, features, params):
        return 0.0, {"enter": False, "skip_reason": "missing_or_failed_gate"}
    if features["pca_flow_score"] >= float(params["min_pca_flow"]):
        return entry_with_features(
            case,
            features,
            {
                "pca_flow_score": round(safe_float(features["pca_flow_score"]), 6),
                "pca_lambda_share": round(safe_float(features["pca_lambda_share"]), 6),
                "side_filter": params.get("side_filter", "all"),
            },
        )
    return 0.0, {"enter": False, "skip_reason": "pca_flow_gate_failed"}


def sim_bipower_jump_flow_admission(
    case: dict[str, Any], prepared: dict[str, Any], params: dict[str, Any], model: dict[str, Any] | None
) -> tuple[float, dict[str, Any]]:
    del model
    features = path_features(prepared, params)
    if not features or not base_gate(case, features, params):
        return 0.0, {"enter": False, "skip_reason": "missing_or_failed_gate"}
    if features["jump_flow_score"] >= float(params["min_jump_flow"]):
        return entry_with_features(
            case,
            features,
            {
                "jump_flow_score": round(safe_float(features["jump_flow_score"]), 6),
                "jump_excess": round(safe_float(features["jump_excess"]), 6),
                "realized_variation": round(safe_float(features["realized_variation"]), 6),
                "bipower_variation": round(safe_float(features["bipower_variation"]), 6),
                "side_filter": params.get("side_filter", "all"),
            },
        )
    return 0.0, {"enter": False, "skip_reason": "jump_flow_gate_failed"}


def sim_pressure_lead_lag_admission(
    case: dict[str, Any], prepared: dict[str, Any], params: dict[str, Any], model: dict[str, Any] | None
) -> tuple[float, dict[str, Any]]:
    del model
    features = path_features(prepared, params)
    if not features or not base_gate(case, features, params):
        return 0.0, {"enter": False, "skip_reason": "missing_or_failed_gate"}
    if features["lead_lag_score"] >= float(params["min_lead_lag"]):
        return entry_with_features(
            case,
            features,
            {
                "lead_lag_score": round(safe_float(features["lead_lag_score"]), 6),
                "side_filter": params.get("side_filter", "all"),
            },
        )
    return 0.0, {"enter": False, "skip_reason": "lead_lag_gate_failed"}


def build_strategy_grid() -> list[StrategySpec]:
    strategies: list[StrategySpec] = []

    def add(family: str, theorem: str, equation: str, params: dict[str, Any], simulator: Any) -> None:
        strategies.append(StrategySpec(family, theorem, equation, params, simulator))

    pca_equation = (
        "X_t=[H_t,100*(1-p_opp_t),bid_sum_t,100-spread_t]; compute first eigenvector v1 of prefix covariance, "
        "orient v1 toward favorable book quality, and C=(lambda1/trace)*(X_D-X_0).v1/sqrt(sum||dX||+1); enter if C>=c and final book gates pass."
    )
    jump_equation = (
        "RV=sum(dH^2), BV=(pi/2)*sum(|dH_i|*|dH_{i-1}|), J=(RV-BV)+/(BV+1); "
        "S=(H_D-H_0)/sqrt(BV+1)+w*sign(max|dH|)*J-lambda*p_opp-mu*spread; enter if S>=s and final book gates pass."
    )
    lead_lag_equation = (
        "R_t=100*(p_opp_{t-1}-p_opp_t); L=(sum R_{t-1}*dH_t - sum dH_{t-1}*R_t)/sqrt(sum lead^2+sum lag^2+1) "
        "-lambda*p_opp-mu*spread; enter if L>=l and final book gates pass."
    )

    for delay_seconds in (30, 120):
        for max_entry_ask in (88, 92):
            for max_opp_pressure in (0.25, 0.50):
                for side_filter in ("all", "yes", "no"):
                    for min_pca_flow in (0.0, 0.25):
                        add(
                            "pca_book_flow_admission",
                            "A delayed entry is healthier when held price, pressure relief, book support, and spread tightness move as one low-dimensional favorable flow.",
                            pca_equation,
                            {
                                "delay_seconds": delay_seconds,
                                "max_entry_ask": max_entry_ask,
                                "max_opp_pressure": max_opp_pressure,
                                "max_spread": 4,
                                "min_bid_sum": 0,
                                "min_points": 3,
                                "min_pca_flow": min_pca_flow,
                                "side_filter": side_filter,
                            },
                            sim_pca_book_flow_admission,
                        )

    for delay_seconds in (30, 120):
        for max_entry_ask in (88, 92):
            for max_opp_pressure in (0.25, 0.50):
                for side_filter in ("all", "yes", "no"):
                    for jump_weight in (1.0,):
                        for min_jump_flow in (-1.0, 0.0):
                            add(
                                "bipower_jump_flow_admission",
                                "A quote path with favorable jump variation should be priced differently from continuous churn with the same endpoint.",
                                jump_equation,
                                {
                                    "delay_seconds": delay_seconds,
                                    "max_entry_ask": max_entry_ask,
                                    "max_opp_pressure": max_opp_pressure,
                                    "max_spread": 4,
                                    "min_bid_sum": 0,
                                    "min_points": 4,
                                    "jump_weight": jump_weight,
                                    "min_jump_flow": min_jump_flow,
                                    "pressure_penalty": 0.0,
                                    "spread_penalty": 0.0,
                                    "side_filter": side_filter,
                                },
                                sim_bipower_jump_flow_admission,
                            )

    for delay_seconds in (30, 120):
        for max_entry_ask in (88, 92):
            for max_opp_pressure in (0.25, 0.50):
                for side_filter in ("all", "yes", "no"):
                    for min_lead_lag in (0.0, 0.5):
                        add(
                            "pressure_lead_lag_admission",
                            "Pressure relief that leads held-quote improvement is stronger evidence than quote improvement that appears before pressure relief.",
                            lead_lag_equation,
                            {
                                "delay_seconds": delay_seconds,
                                "max_entry_ask": max_entry_ask,
                                "max_opp_pressure": max_opp_pressure,
                                "max_spread": 4,
                                "min_bid_sum": 0,
                                "min_points": 5,
                                "min_lead_lag": min_lead_lag,
                                "pressure_penalty": 0.0,
                                "spread_penalty": 0.0,
                                "side_filter": side_filter,
                            },
                            sim_pressure_lead_lag_admission,
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
        "# Codex Entry Eigen/Jump Edge Research",
        "",
        f"- Generated: `{payload['generated_at']}`",
        f"- Datasets: `{', '.join(payload['datasets'])}`",
        f"- Quote-path cases: `{payload['case_count']}`",
        "- Scope: research-only entry/no-trade simulation; live bot logic, configs, run scripts, and processes were not changed.",
        "- Non-repetition: this tests PCA book-flow, bipower jump variation, and pressure/quote lead-lag equations rather than prior delayed-entry, dwell, logit-SNR, CUSUM, semivariance, slack, phase-loop, or liquidity-absorption families.",
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
            "## By Side",
            "",
            "| Family | Side | PnL | Delta vs actual | Delta vs no-stop | Entries | Win rate |",
            "|---|---|---:|---:|---:|---:|---:|",
        ]
    )
    for family, result in payload["best_by_family"].items():
        for side, summary in result["by_side"].items():
            lines.append(
                f"| `{family}` | `{side}` | {summary['sim_pnl']} | {summary['delta_vs_actual']} | "
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
            "- PCA book-flow asks whether several book-quality coordinates move together in a coherent favorable eigen-direction.",
            "- Bipower jump flow separates discrete favorable quote jumps from continuous churn with the same endpoint.",
            "- Pressure lead-lag checks whether opponent-pressure relief leads held-quote improvement rather than following it.",
            "- All strategy inputs are quote heartbeats observed at or before the simulated decision delay; settlement labels are used only for scoring.",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Research-only PCA, jump-variation, and lead-lag entry probes.")
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
    json_path = EDGE_DIR / f"codex_entry_eigenjump_research_{stamp}.json"
    md_path = EDGE_DIR / f"codex_entry_eigenjump_research_{stamp}.md"
    latest_json = EDGE_DIR / "codex_entry_eigenjump_research_latest.json"
    latest_md = EDGE_DIR / "codex_entry_eigenjump_research_latest.md"
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
            "pca_book_flow_admission": "prefix-only held ask, own/opposite bids, bid_sum, spread, and elapsed through the configured delay",
            "bipower_jump_flow_admission": "prefix-only held ask increments plus final book gates through the configured delay",
            "pressure_lead_lag_admission": "prefix-only held ask increments, opposite-pressure changes, and final book gates through the configured delay",
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
            f"holdout_delta_skip={holdout['delta_vs_no_trade_all']} holdout_entries={holdout['entries']} "
            f"robust_rows={len(robust_scan.get(family, []))}"
        )


if __name__ == "__main__":
    main()
