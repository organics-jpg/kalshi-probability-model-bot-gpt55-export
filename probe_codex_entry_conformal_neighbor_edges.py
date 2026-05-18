from __future__ import annotations

import argparse
import json
import math
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from probe_codex_entry_timing_edges import delayed_entry_pnl
from probe_codex_terminal_salvage_all_trades import discover_datasets, load_dataset_cases
from probe_stop_touch_confirmation import (
    append_ledger,
    estimated_order_fee_cents,
    idea_key,
    result_distance,
    strategy_id,
    update_strategy_memory,
)
from refine_btc_spot_synthetic_ev_candidate import BASE_CANDIDATE_PARAMS
from validate_btc_spot_synthetic_ev_broad import (
    EDGE_DIR,
    baseline_payload,
    load_or_fetch_candles,
    mean,
    prepare_case,
    quality_dwell_share,
    quote_gate,
    safe_float,
    side_location_score,
    side_move_score,
    summarize_by_group,
    summarize_entry_rows,
    synthetic_ev_score,
)


UTC = timezone.utc


@dataclass(frozen=True)
class StrategySpec:
    family: str
    theorem: str
    equation: str
    params: dict[str, Any]


def load_cases(datasets: list[str] | None) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    selected = datasets or discover_datasets()
    payloads = [load_dataset_cases(dataset, refresh_cache=False) for dataset in selected]
    cases: list[dict[str, Any]] = []
    for payload in payloads:
        dataset = payload.get("dataset")
        for case in payload.get("cases", []):
            case.setdefault("dataset", dataset)
            cases.append(case)
    return sorted(cases, key=lambda item: (item["entry_ts"], item["market"], item["side"])), payloads


def quote_path_features(features: dict[str, Any], params: dict[str, Any]) -> dict[str, float]:
    history = features.get("quality_history") or []
    dwell_share, quality_seconds = quality_dwell_share(history, params)
    if len(history) >= 2:
        asks = [safe_float(point.get("held_ask")) for point in history]
        clean_asks = [ask for ask in asks if not math.isnan(ask)]
        quote_net = clean_asks[-1] - clean_asks[0] if len(clean_asks) >= 2 else 0.0
        quote_range = max(clean_asks) - min(clean_asks) if clean_asks else 0.0
        state_changes = sum(1 for idx in range(1, len(clean_asks)) if abs(clean_asks[idx] - clean_asks[idx - 1]) > 1e-9)
    else:
        quote_net = 0.0
        quote_range = 0.0
        state_changes = 0
    return {
        "quality_share": dwell_share,
        "quality_seconds": quality_seconds,
        "quote_net": quote_net,
        "quote_range": quote_range,
        "state_changes": float(state_changes),
    }


def feature_row(case: dict[str, Any], prepared: dict[str, Any], params: dict[str, Any]) -> dict[str, Any] | None:
    delay = int(params["delay_seconds"])
    features = prepared.get(str(delay))
    if not features or not quote_gate(features, params):
        return None

    score_params = {
        **BASE_CANDIDATE_PARAMS,
        "delay_seconds": delay,
        "max_entry_ask": params["max_entry_ask"],
        "max_opp_pressure": params["max_opp_pressure"],
        "max_spread": params["max_spread"],
        "min_bid_sum": params["min_bid_sum"],
    }
    scored = synthetic_ev_score(case, features, score_params)
    if scored is None:
        return None

    ask = safe_float(features.get("held_ask"))
    pressure = safe_float(features.get("pressure"))
    spread = safe_float(features.get("spread"))
    bid_sum = safe_float(features.get("bid_sum"))
    btc_range = safe_float(features.get("btc_range_15m_bps"))
    if any(math.isnan(value) for value in (ask, pressure, spread, bid_sum, btc_range)):
        return None

    qty = max(1, int(case["qty"]))
    fee_per_contract = estimated_order_fee_cents(ask, qty) / qty
    outcome_cents = 100.0 - ask - fee_per_contract if bool(case["settlement_win"]) else -ask - fee_per_contract
    path_stats = quote_path_features(features, params)
    move_score = side_move_score(case, features, score_params)
    location_score = side_location_score(case, features, score_params)
    row = {
        "case": case,
        "features": features,
        "delay": delay,
        "ask": ask,
        "pressure": pressure,
        "spread": spread,
        "bid_sum": bid_sum,
        "btc_range": btc_range,
        "btc_move_5m": safe_float(features.get("btc_move_5m_bps")),
        "btc_move_15m": safe_float(features.get("btc_move_15m_bps")),
        "move_score": move_score if not math.isnan(move_score) else 0.0,
        "location_score": location_score if not math.isnan(location_score) else 0.0,
        "q_spot": safe_float(scored.get("q_spot")),
        "ev_cents": safe_float(scored.get("ev_cents")),
        "roi": safe_float(scored.get("ev_cents")) / max(1.0, ask + fee_per_contract),
        "fee_per_contract": fee_per_contract,
        "outcome_cents": outcome_cents,
        **path_stats,
    }
    if any(math.isnan(safe_float(row.get(key))) for key in ("q_spot", "ev_cents", "roi")):
        return None
    return row


def normalized_vector(row: dict[str, Any], feature_set: str) -> tuple[float, ...]:
    base = [
        safe_float(row.get("ev_cents")) / 10.0,
        (safe_float(row.get("q_spot")) - 0.5) * 4.0,
        (safe_float(row.get("ask")) - 84.0) / 10.0,
        (safe_float(row.get("pressure")) - 0.25) / 0.15,
        safe_float(row.get("spread")) / 4.0,
        safe_float(row.get("move_score")),
        safe_float(row.get("location_score")),
    ]
    if feature_set == "ev_quote_dwell":
        base.extend(
            [
                safe_float(row.get("quality_share")) * 2.0,
                safe_float(row.get("quality_seconds")) / 120.0,
                safe_float(row.get("quote_net")) / 15.0,
                safe_float(row.get("quote_range")) / 15.0,
            ]
        )
    elif feature_set == "ev_quote_risk":
        base.extend(
            [
                safe_float(row.get("roi")) * 20.0,
                safe_float(row.get("btc_range")) / 80.0,
                safe_float(row.get("btc_move_15m")) / 40.0,
            ]
        )
    return tuple(0.0 if math.isnan(value) else float(value) for value in base)


def neighbor_stats(current: dict[str, Any], history: list[dict[str, Any]], params: dict[str, Any]) -> dict[str, Any] | None:
    min_history = int(params["min_history"])
    if len(history) < min_history:
        return None
    k = int(params["k"])
    current_vec = normalized_vector(current, str(params["feature_set"]))
    distances: list[tuple[float, dict[str, Any]]] = []
    for prior in history:
        prior_vec = normalized_vector(prior, str(params["feature_set"]))
        distance = math.sqrt(sum((a - b) * (a - b) for a, b in zip(current_vec, prior_vec)))
        distances.append((distance, prior))
    nearest = sorted(distances, key=lambda item: item[0])[:k]
    if len(nearest) < k:
        return None
    max_avg_distance = params.get("max_avg_distance")
    avg_distance = mean([item[0] for item in nearest])
    if max_avg_distance is not None and avg_distance > float(max_avg_distance):
        return None

    # Compact tri-cube kernel: close analogues dominate, but all selected neighbors count.
    scale = max(nearest[-1][0], 1e-6)
    weighted_sum = 0.0
    weight_total = 0.0
    weighted_sq = 0.0
    outcomes = []
    for distance, prior in nearest:
        ratio = min(1.0, distance / scale)
        weight = max(1e-6, (1.0 - ratio**3) ** 3)
        outcome = float(prior["outcome_cents"])
        outcomes.append(outcome)
        weighted_sum += weight * outcome
        weighted_sq += weight * outcome * outcome
        weight_total += weight
    mu = weighted_sum / weight_total
    variance = max(0.0, weighted_sq / weight_total - mu * mu)
    n_eff = weight_total * weight_total / sum(
        max(1e-6, (1.0 - min(1.0, distance / scale) ** 3) ** 3) ** 2 for distance, _ in nearest
    )
    lcb = mu - float(params["lcb_z"]) * math.sqrt(variance / max(1.0, n_eff))
    sorted_outcomes = sorted(outcomes)
    tail_n = max(1, math.ceil(len(sorted_outcomes) * 0.2))
    cvar20 = mean(sorted_outcomes[:tail_n])
    win_rate = sum(1 for outcome in outcomes if outcome > 0.0) / len(outcomes)
    return {
        "neighbor_mu_cents": mu,
        "neighbor_lcb_cents": lcb,
        "neighbor_cvar20_cents": cvar20,
        "neighbor_win_rate": win_rate,
        "neighbor_avg_distance": avg_distance,
        "neighbor_count": len(nearest),
        "neighbor_n_eff": n_eff,
    }


def contracts_for_entry(case: dict[str, Any], stats: dict[str, Any], params: dict[str, Any]) -> int:
    base_qty = max(1, int(case["qty"]))
    if "max_multiplier" not in params:
        return base_qty
    edge = max(0.0, float(stats["neighbor_lcb_cents"]) - float(params["min_lcb_cents"]))
    raw_multiplier = 1.0 + edge / max(1.0, float(params["size_unit_cents"]))
    multiplier = min(float(params["max_multiplier"]), raw_multiplier)
    return min(int(params["max_contracts"]), max(1, int(math.floor(base_qty * multiplier))))


def simulate_rows(prepped: list[tuple[dict[str, Any], dict[str, Any]]], strategy: StrategySpec) -> list[dict[str, Any]]:
    sid = strategy_id(strategy.family, strategy.params)
    history: list[dict[str, Any]] = []
    rows: list[dict[str, Any]] = []
    ordered = sorted(prepped, key=lambda item: (item[0]["entry_ts"], item[0]["market"], item[0]["side"]))
    for case, prepared in ordered:
        row = feature_row(case, prepared, strategy.params)
        meta: dict[str, Any]
        pnl = 0.0
        if row is None:
            meta = {"enter": False, "skip_reason": "missing_or_gate_failed"}
        elif row["ev_cents"] < float(strategy.params["min_model_ev_cents"]):
            meta = {
                "enter": False,
                "skip_reason": "synthetic_ev_too_low",
                "score": round(float(row["ev_cents"]), 6),
            }
        else:
            stats = neighbor_stats(row, history, strategy.params)
            if stats is None:
                meta = {
                    "enter": False,
                    "skip_reason": "insufficient_or_distant_neighbors",
                    "score": round(float(row["ev_cents"]), 6),
                }
            elif stats["neighbor_lcb_cents"] < float(strategy.params["min_lcb_cents"]):
                meta = {
                    "enter": False,
                    "skip_reason": "neighbor_lcb_too_low",
                    "score": round(float(stats["neighbor_lcb_cents"]), 6),
                    **{key: round(float(value), 6) for key, value in stats.items()},
                }
            elif stats["neighbor_win_rate"] < float(strategy.params["min_neighbor_win_rate"]):
                meta = {
                    "enter": False,
                    "skip_reason": "neighbor_win_rate_too_low",
                    "score": round(float(stats["neighbor_lcb_cents"]), 6),
                    **{key: round(float(value), 6) for key, value in stats.items()},
                }
            else:
                contracts = contracts_for_entry(case, stats, strategy.params)
                pnl = delayed_entry_pnl(case, float(row["ask"]), contracts=contracts)
                meta = {
                    "enter": True,
                    "entry_ask": round(float(row["ask"]), 4),
                    "entry_elapsed": round(float(row["features"]["actual_quote_elapsed"]), 4),
                    "contracts": contracts,
                    "pressure": round(float(row["pressure"]), 6),
                    "spread": round(float(row["spread"]), 4),
                    "bid_sum": round(float(row["bid_sum"]), 4),
                    "score": round(float(stats["neighbor_lcb_cents"]), 6),
                    "model_ev_cents": round(float(row["ev_cents"]), 6),
                    **{key: round(float(value), 6) for key, value in stats.items()},
                }

        rows.append(
            {
                "label": sid,
                "dataset": case["dataset"],
                "market": case["market"],
                "side": case.get("side"),
                "entry_day_et": case["entry_day_et"],
                "entry_ts": case["entry_ts"],
                "settlement_win": bool(case["settlement_win"]),
                "actual_net_pnl": float(case["actual_net_pnl"]),
                "hold_pnl": float(case["hold_pnl"]),
                "sim_pnl": float(pnl),
                "action": "enter" if meta.get("enter") else "skip",
                "entry_ask": meta.get("entry_ask") if meta.get("enter") else None,
                "entry_elapsed": meta.get("entry_elapsed") if meta.get("enter") else None,
                "contracts": int(meta.get("contracts") or 0) if meta.get("enter") else 0,
                "base_contracts": int(case["qty"]),
                "skip_reason": meta.get("skip_reason"),
                "score": meta.get("score"),
                "model_ev_cents": meta.get("model_ev_cents"),
                "neighbor_mu_cents": meta.get("neighbor_mu_cents"),
                "neighbor_cvar20_cents": meta.get("neighbor_cvar20_cents"),
                "neighbor_win_rate": meta.get("neighbor_win_rate"),
                "neighbor_avg_distance": meta.get("neighbor_avg_distance"),
            }
        )

        if row is not None and row["ev_cents"] >= float(strategy.params["pool_min_ev_cents"]):
            history.append(row)
    return rows


def risk_summary(rows: list[dict[str, Any]]) -> dict[str, Any]:
    entered = [row for row in rows if row["action"] == "enter"]
    losses = [float(row["sim_pnl"]) for row in entered if float(row["sim_pnl"]) < 0.0]
    running = 0.0
    peak = 0.0
    max_drawdown = 0.0
    by_day: dict[str, float] = {}
    for row in rows:
        running += float(row["sim_pnl"])
        peak = max(peak, running)
        max_drawdown = min(max_drawdown, running - peak)
        by_day[row["entry_day_et"]] = by_day.get(row["entry_day_et"], 0.0) + float(row["sim_pnl"])
    active_days = [value for value in by_day.values() if abs(value) > 1e-9]
    return {
        "loss_count": len(losses),
        "loss_sum": round(sum(losses), 2),
        "avg_loss": round(mean(losses), 4) if losses else 0.0,
        "worst_3_loss_sum": round(sum(sorted(losses)[:3]), 2) if losses else 0.0,
        "max_drawdown": round(max_drawdown, 2),
        "active_day_count": len(active_days),
        "negative_active_days": sum(1 for value in active_days if value < 0.0),
        "worst_day_pnl": round(min(active_days), 2) if active_days else 0.0,
        "best_day_pnl": round(max(active_days), 2) if active_days else 0.0,
    }


def run_strategy(prepped: list[tuple[dict[str, Any], dict[str, Any]]], strategy: StrategySpec) -> dict[str, Any]:
    sid = strategy_id(strategy.family, strategy.params)
    rows = simulate_rows(prepped, strategy)
    entered = [row for row in rows if row["action"] == "enter"]
    return {
        "strategy_id": sid,
        "family": strategy.family,
        "theorem": strategy.theorem,
        "equation": strategy.equation,
        "params": strategy.params,
        "summary": summarize_entry_rows(sid, rows),
        "risk": risk_summary(rows),
        "by_dataset": summarize_by_group(sid, rows, "dataset"),
        "by_side": summarize_by_group(sid, rows, "side"),
        "interesting_examples": sorted(entered, key=lambda row: float(row["sim_pnl"]))[:10],
        "_rows": rows,
    }


def build_strategy_grid() -> list[StrategySpec]:
    admission_theorem = (
        "A parametric BTC EV score is more trustworthy when nearby prior decision-time states also had positive "
        "fee-adjusted settlement payoff; sparse or locally lossy neighborhoods should become no-trades."
    )
    admission_equation = (
        "For x_t=(EV_spot,q_spot,H,pressure,spread,momentum,location,...), take the k nearest prior cases j<t. "
        "K_j=(1-(d_j/d_k)^3)^3, mu=sum(K_j*y_j)/sum(K_j), LCB=mu-z*sqrt(var_K(y)/n_eff); enter only if EV>=e, "
        "LCB>=L, and neighbor win_rate>=w."
    )
    sizing_theorem = (
        "If local empirical payoff has a positive lower bound, size can be tied to that lower bound rather than to "
        "the raw model score, clipping exposure when analogues are weaker."
    )
    sizing_equation = (
        "Use the same online neighbor LCB admission, then contracts=min(Cmax,floor(qty*min(Mmax,1+max(0,LCB-L)/u)))."
    )
    strategies: list[StrategySpec] = []
    base_params = {
        "max_opp_pressure": 0.30,
        "min_bid_sum": 0,
        "max_spread": 4,
        "pool_min_ev_cents": -2.0,
        "min_neighbor_win_rate": 0.78,
    }
    for delay_seconds in (120, 150):
        for feature_set in ("ev_quote_dwell", "ev_quote_risk"):
            for max_entry_ask in (88, 90):
                for min_model_ev_cents in (0.0, 2.0, 4.0):
                    for k in (25, 45):
                        for min_history in (80, 120):
                            for lcb_z in (0.5, 1.0):
                                for min_lcb_cents in (0.0, 1.0):
                                    params = {
                                        **base_params,
                                        "delay_seconds": delay_seconds,
                                        "feature_set": feature_set,
                                        "max_entry_ask": max_entry_ask,
                                        "min_model_ev_cents": min_model_ev_cents,
                                        "k": k,
                                        "min_history": min_history,
                                        "lcb_z": lcb_z,
                                        "min_lcb_cents": min_lcb_cents,
                                        "max_avg_distance": None,
                                    }
                                    strategies.append(
                                        StrategySpec(
                                            "online_neighbor_lcb_admission",
                                            admission_theorem,
                                            admission_equation,
                                            params,
                                        )
                                    )
                                    if min_history == 80 and k == 25 and lcb_z in (0.5, 1.0):
                                        size_params = {
                                            **params,
                                            "max_multiplier": 2.0,
                                            "max_contracts": 20,
                                            "size_unit_cents": 4.0,
                                        }
                                        strategies.append(
                                            StrategySpec(
                                                "online_neighbor_lcb_sizer",
                                                sizing_theorem,
                                                sizing_equation,
                                                size_params,
                                            )
                                        )
    return strategies


def slim_result(result: dict[str, Any]) -> dict[str, Any]:
    return {key: value for key, value in result.items() if key != "_rows"}


def select_family_best(results: list[dict[str, Any]], *, min_entries: int = 20) -> dict[str, dict[str, Any]]:
    output: dict[str, dict[str, Any]] = {}
    for family in sorted({result["family"] for result in results}):
        family_results = [result for result in results if result["family"] == family]
        eligible = [result for result in family_results if result["summary"]["entries"] >= min_entries] or family_results
        output[family] = max(
            eligible,
            key=lambda result: (
                result["summary"]["sim_pnl"],
                result["summary"]["entry_win_rate"],
                -result["risk"]["max_drawdown"],
            ),
        )
    return output


def walk_forward_summary(results: list[dict[str, Any]]) -> dict[str, Any]:
    if not results:
        return {}
    rows = results[0]["_rows"]
    split = int(len(rows) * 0.7)
    output: dict[str, Any] = {
        "train_n": split,
        "holdout_n": len(rows) - split,
        "split_entry_ts": rows[split]["entry_ts"] if split < len(rows) else None,
        "selection_basis": "Max train simulated PnL per family among variants with at least 15 train entries; holdout decisions keep the online prior-history rule.",
        "families": {},
    }
    for family in sorted({result["family"] for result in results}):
        family_results = [result for result in results if result["family"] == family]
        train_scored = []
        for result in family_results:
            train_rows = result["_rows"][:split]
            summary = summarize_entry_rows(result["strategy_id"], train_rows)
            train_scored.append((result, summary))
        eligible = [item for item in train_scored if item[1]["entries"] >= 15] or train_scored
        selected, train_summary = max(
            eligible,
            key=lambda item: (
                item[1]["sim_pnl"],
                item[1]["entry_win_rate"],
                -item[0]["risk"]["max_drawdown"],
            ),
        )
        holdout_rows = selected["_rows"][split:]
        output["families"][family] = {
            "selected_strategy_id": selected["strategy_id"],
            "selected_params": selected["params"],
            "train_summary": train_summary,
            "holdout_summary": summarize_entry_rows(selected["strategy_id"], holdout_rows),
            "holdout_risk": risk_summary(holdout_rows),
        }
    return output


def sensitivity(results: list[dict[str, Any]], best_by_family: dict[str, dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    output: dict[str, list[dict[str, Any]]] = {}
    for family, best in best_by_family.items():
        ranked = sorted(
            [result for result in results if result["family"] == family],
            key=lambda result: (result_distance(result["params"], best["params"]), -result["summary"]["sim_pnl"]),
        )
        output[family] = [
            {
                "strategy_id": result["strategy_id"],
                "params": result["params"],
                "sim_pnl": result["summary"]["sim_pnl"],
                "delta_vs_actual": result["summary"]["delta_vs_actual"],
                "delta_vs_no_stop": result["summary"]["delta_vs_no_stop"],
                "entries": result["summary"]["entries"],
                "win_rate": result["summary"]["entry_win_rate"],
                "max_drawdown": result["risk"]["max_drawdown"],
            }
            for result in ranked[:12]
        ]
    return output


def status_for_result(result: dict[str, Any], wf: dict[str, Any], robust_rows: list[dict[str, Any]]) -> str:
    holdout = wf.get("families", {}).get(result["family"], {}).get("holdout_summary", {})
    if (
        result["summary"]["delta_vs_actual"] > 0
        and result["summary"]["delta_vs_no_stop"] > 0
        and holdout.get("sim_pnl", -1) > 0
        and result["summary"]["entries"] >= 20
        and len([row for row in robust_rows if row["sim_pnl"] > 0]) >= 5
    ):
        return "candidate_for_human_review"
    if result["summary"]["delta_vs_no_trade_all"] > 0 and holdout.get("sim_pnl", -1) > 0:
        return "watchlist_positive_holdout"
    if result["summary"]["delta_vs_no_trade_all"] > 0:
        return "watchlist_positive_but_not_robust"
    return "tested_negative"


def write_markdown(path: Path, payload: dict[str, Any]) -> None:
    base = payload["baselines"]
    lines = [
        "# Codex Entry Conformal Neighbor Research",
        "",
        f"- Generated: `{payload['generated_at']}`",
        f"- Cases: `{payload['case_count']}` across `{', '.join(payload['datasets'])}`",
        f"- Variants tested: `{payload['variant_count']}`",
        "- Scope: research-only; live entry/exit logic, configs, run scripts, and bot processes were not changed.",
        "",
        "## Baselines",
        "",
        f"- Actual recorded PnL: `${base['actual']['summary']['sim_pnl']}`",
        f"- No-stop hold-to-settlement PnL: `${base['no_stop']['summary']['sim_pnl']}`",
        f"- First held-ask <=70 baseline: `${base['held_ask_stop_70']['summary']['sim_pnl']}`",
        "- Skip-all baseline: `$0.0`",
        "",
        "## New Equation Families",
        "",
        "- `online_neighbor_lcb_admission`: online k-nearest-neighbor empirical payoff lower bound. It uses only prior cases in chronological order, so current-case settlement labels are not used for the decision.",
        "- `online_neighbor_lcb_sizer`: same admission rule, but position size is a clipped function of the empirical lower bound rather than fixed at the historical size.",
        "",
        "## Best Results",
        "",
    ]
    for family, result in payload["best_by_family"].items():
        summary = result["summary"]
        wf = payload["walk_forward"]["families"].get(family, {})
        lines.extend(
            [
                f"### {family} `{result['strategy_id']}`",
                "",
                f"- Status: `{result['status']}`",
                f"- Equation: `{result['equation']}`",
                f"- Params: `{json.dumps(result['params'], sort_keys=True)}`",
                f"- Full PnL / delta vs actual / delta vs no-stop / entries / win rate: `${summary['sim_pnl']}` / `${summary['delta_vs_actual']}` / `${summary['delta_vs_no_stop']}` / `{summary['entries']}` / `{summary['entry_win_rate']}`",
                f"- Risk: `{json.dumps(result['risk'], sort_keys=True)}`",
                f"- Walk-forward train PnL / entries: `${wf.get('train_summary', {}).get('sim_pnl')}` / `{wf.get('train_summary', {}).get('entries')}`",
                f"- Walk-forward holdout PnL / entries / win rate: `${wf.get('holdout_summary', {}).get('sim_pnl')}` / `{wf.get('holdout_summary', {}).get('entries')}` / `{wf.get('holdout_summary', {}).get('entry_win_rate')}`",
                "- By dataset: "
                + "; ".join(
                    f"`{dataset}`: ${stats['sim_pnl']} ({stats['entries']} entries)"
                    for dataset, stats in result["by_dataset"].items()
                ),
                "",
            ]
        )
    lines.extend(
        [
            "## Sensitivity Near Best",
            "",
        ]
    )
    for family, rows in payload["sensitivity"].items():
        lines.append(f"### {family}")
        lines.append("")
        lines.append("| PnL | Entries | Win rate | Max DD | Params |")
        lines.append("|---:|---:|---:|---:|---|")
        for row in rows[:8]:
            lines.append(
                f"| {row['sim_pnl']} | {row['entries']} | {row['win_rate']} | {row['max_drawdown']} | `{json.dumps(row['params'], sort_keys=True)}` |"
            )
        lines.append("")
    lines.extend(
        [
            "## Interpretation",
            "",
            "- This is not another fixed BTC EV threshold sweep: the entry score is a local empirical payoff lower bound over prior analogues.",
            "- A positive result still depends on historical analogue coverage; it should be reviewed as a research candidate, not patched into live behavior.",
            "- If this branch is continued, the next check should replace chronological prior-entry availability with confirmed prior-settlement availability to remove the last small timing approximation.",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Research-only online conformal neighbor entry tests.")
    parser.add_argument("--datasets", nargs="*", default=None)
    parser.add_argument("--refresh-btc-cache", action="store_true")
    args = parser.parse_args()

    cases, _ = load_cases(args.datasets)
    candles = load_or_fetch_candles(cases, refresh_cache=args.refresh_btc_cache)
    strategies = build_strategy_grid()
    delays = tuple(sorted({int(strategy.params["delay_seconds"]) for strategy in strategies}))
    prepped = [(case, prepare_case(case, candles, delays)) for case in cases]
    results = [run_strategy(prepped, strategy) for strategy in strategies]
    best_by_family_raw = select_family_best(results)
    wf = walk_forward_summary(results)
    sens = sensitivity(results, best_by_family_raw)

    stamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
    generated_at = datetime.now(UTC).isoformat()
    json_path = EDGE_DIR / f"codex_entry_conformal_neighbor_research_{stamp}.json"
    md_path = EDGE_DIR / f"codex_entry_conformal_neighbor_research_{stamp}.md"
    latest_json = EDGE_DIR / "codex_entry_conformal_neighbor_research_latest.json"
    latest_md = EDGE_DIR / "codex_entry_conformal_neighbor_research_latest.md"

    best_by_family = {
        family: {
            **slim_result(result),
            "status": status_for_result(result, wf, sens.get(family, [])),
        }
        for family, result in best_by_family_raw.items()
    }
    top_results = sorted(
        (slim_result(result) for result in results),
        key=lambda result: (result["summary"]["sim_pnl"], result["summary"]["entry_win_rate"]),
        reverse=True,
    )[:40]
    payload = {
        "generated_at": generated_at,
        "json_path": str(json_path),
        "markdown_path": str(md_path),
        "dataset": "all_quote_path_trades_with_closed_1m_btc",
        "datasets": sorted({case["dataset"] for case in cases}),
        "case_count": len(cases),
        "variant_count": len(strategies),
        "baselines": baseline_payload(cases),
        "non_repetition": {
            "new_family": "online conformal/nearest-neighbor empirical payoff lower bound over prior decision-time analogues",
            "not_retesting": [
                "fixed BTC spot synthetic EV threshold",
                "score-scaled sizing by raw model EV",
                "quote dwell/renewal gates",
                "path geometry/CUSUM/Omega/CVaR",
                "regime-transition priors",
            ],
        },
        "best_by_family": best_by_family,
        "walk_forward": wf,
        "sensitivity": sens,
        "top_results": top_results,
    }
    json_text = json.dumps(payload, indent=2, sort_keys=True)
    json_path.write_text(json_text, encoding="utf-8")
    latest_json.write_text(json_text, encoding="utf-8")
    write_markdown(md_path, payload)
    write_markdown(latest_md, payload)

    ledger_records = []
    for family, result in best_by_family.items():
        ledger_records.append(
            {
                "recorded_at": generated_at,
                "generated_at": generated_at,
                "source": Path(__file__).name,
                "status": result["status"],
                "dataset": payload["dataset"],
                "datasets": payload["datasets"],
                "family": family,
                "strategy_id": result["strategy_id"],
                "idea_key": idea_key(family, result["equation"], result["params"]),
                "theorem": result["theorem"],
                "equation": result["equation"],
                "params": result["params"],
                "summary": result["summary"],
                "risk": result["risk"],
                "walk_forward": wf.get("families", {}).get(family),
                "sensitivity_excerpt": sens.get(family, [])[:8],
                "json_path": str(json_path),
                "markdown_path": str(md_path),
            }
        )
    append_ledger(ledger_records)
    update_strategy_memory(payload, best_by_family)

    best = max(best_by_family.values(), key=lambda result: result["summary"]["sim_pnl"])
    print(
        f"Wrote {md_path} | best={best['strategy_id']} sim={best['summary']['sim_pnl']} "
        f"delta_actual={best['summary']['delta_vs_actual']} entries={best['summary']['entries']}"
    )


if __name__ == "__main__":
    main()
