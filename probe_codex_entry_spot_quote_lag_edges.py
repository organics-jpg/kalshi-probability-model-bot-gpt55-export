from __future__ import annotations

import argparse
import json
import math
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

import pandas as pd

from probe_codex_terminal_salvage_all_trades import (
    EDGE_DIR,
    discover_datasets,
    load_dataset_cases,
    run_baseline,
)
from probe_stop_touch_confirmation import (
    append_ledger,
    estimated_order_fee_cents,
    idea_key,
    result_distance,
    strategy_id,
    update_strategy_memory,
)
from research_pipeline import add_btc_technical_columns
from validate_btc_spot_synthetic_ev_broad import (
    PRIOR_SYNTHETIC_EV_PARAMS,
    candle_cache_path,
    clamp,
    entry_meta,
    load_or_fetch_candles,
    mean,
    prepare_case,
    quote_gate,
    safe_float,
    side_sign,
    sigmoid,
    synthetic_ev_score,
)


UTC = timezone.utc


@dataclass(frozen=True)
class StrategySpec:
    family: str
    theorem: str
    equation: str
    params: dict[str, Any]
    simulator: Callable[[dict[str, Any], dict[str, Any], dict[str, Any]], tuple[float, dict[str, Any]]] | None = None
    online: bool = False


def logit(p: float) -> float:
    bounded = clamp(p, 0.01, 0.99)
    return math.log(bounded / (1.0 - bounded))


def quote_logit(features: dict[str, Any]) -> float:
    return logit(safe_float(features.get("held_ask")) / 100.0)


def load_cached_candles(cases: list[dict[str, Any]], refresh_cache: bool) -> pd.DataFrame:
    if refresh_cache:
        return load_or_fetch_candles(cases, refresh_cache=True)
    entry_times = pd.to_datetime([case["entry_ts"] for case in cases], utc=True, errors="coerce")
    start = (entry_times.min() - pd.Timedelta(hours=3)).floor("min")
    end = (entry_times.max() + pd.Timedelta(minutes=15)).ceil("min")
    candidates = [candle_cache_path(start, end), EDGE_DIR / "btc_1m_candles_broad_validation_latest.csv"]
    for path in candidates:
        if path.exists():
            raw = pd.read_csv(path)
            for col in ("open_dt", "close_dt"):
                if col in raw.columns:
                    raw[col] = pd.to_datetime(raw[col], utc=True, errors="coerce")
            enriched = add_btc_technical_columns(raw)
            enriched["close_dt"] = pd.to_datetime(enriched["close_dt"], utc=True, errors="coerce")
            return enriched[enriched["close_dt"].notna()].sort_values("close_dt").reset_index(drop=True)
    return load_or_fetch_candles(cases, refresh_cache=False)


def augment_btc_windows(prepared: dict[str, Any], candles: pd.DataFrame) -> dict[str, Any]:
    for features in prepared.values():
        if not features:
            continue
        source_dt = pd.to_datetime(features.get("btc_source_close_dt"), utc=True, errors="coerce")
        if pd.isna(source_dt):
            continue
        idx = int(candles["close_dt"].searchsorted(source_dt, side="right") - 1)
        if idx < 1:
            continue
        window = candles.iloc[max(0, idx - 5) : idx + 1]
        closes = [safe_float(value) for value in window["close"].tolist()]
        closes = [value for value in closes if not math.isnan(value) and value > 0]
        if len(closes) < 2:
            continue
        returns = [
            (closes[pos] - closes[pos - 1]) / closes[pos - 1] * 10000.0
            for pos in range(1, len(closes))
            if closes[pos - 1] > 0
        ]
        if not returns:
            continue
        net_bps = (closes[-1] - closes[0]) / closes[0] * 10000.0
        abs_path = sum(abs(value) for value in returns)
        realized_vol = math.sqrt(sum(value * value for value in returns))
        features["btc_window_net_5m_bps"] = net_bps
        features["btc_window_abs_path_5m_bps"] = abs_path
        features["btc_window_realized_vol_5m_bps"] = realized_vol
        features["btc_window_efficiency_5m"] = abs(net_bps) / abs_path if abs_path > 0 else 0.0
    return prepared


def sim_spot_quote_lag_residual(
    case: dict[str, Any], prepared: dict[str, Any], params: dict[str, Any]
) -> tuple[float, dict[str, Any]]:
    now = prepared.get(str(int(params["delay_seconds"])))
    start = prepared.get(str(int(params.get("anchor_delay_seconds", 0))))
    if not now or not start or not quote_gate(now, params):
        return 0.0, {"enter": False, "skip_reason": "missing_or_gate_failed"}
    btc_now = safe_float(now.get("btc_close"))
    btc_start = safe_float(start.get("btc_close"))
    if any(math.isnan(value) or value <= 0 for value in (btc_now, btc_start)):
        return 0.0, {"enter": False, "skip_reason": "missing_btc_close"}
    spot_impulse_bps = side_sign(case, params) * (btc_now - btc_start) / btc_start * 10000.0
    quote_move_score = (quote_logit(now) - quote_logit(start)) * 100.0
    scored = synthetic_ev_score(case, now, params)
    if scored is None:
        return 0.0, {"enter": False, "skip_reason": "missing_spot_score"}
    lag_score = (
        spot_impulse_bps
        - float(params["quote_beta"]) * quote_move_score
        - float(params["pressure_penalty"]) * safe_float(now.get("pressure"))
        - float(params["spread_penalty"]) * safe_float(now.get("spread"))
    )
    if spot_impulse_bps < float(params["min_spot_impulse_bps"]):
        return 0.0, {"enter": False, "skip_reason": "spot_impulse_too_low", "score": round(lag_score, 6)}
    if scored["ev_cents"] < float(params["min_ev_cents"]):
        return 0.0, {"enter": False, "skip_reason": "raw_ev_too_low", "score": round(lag_score, 6)}
    if lag_score < float(params["min_lag_score"]):
        return 0.0, {"enter": False, "skip_reason": "lag_residual_too_low", "score": round(lag_score, 6)}
    return entry_meta(
        case,
        now,
        {
            "score": round(lag_score, 6),
            "spot_impulse_bps": round(spot_impulse_bps, 6),
            "quote_move_score": round(quote_move_score, 6),
            "raw_ev_cents": round(scored["ev_cents"], 6),
            "q_spot": round(scored["q_spot"], 6),
        },
    )


def sim_btc_realized_efficiency(
    case: dict[str, Any], prepared: dict[str, Any], params: dict[str, Any]
) -> tuple[float, dict[str, Any]]:
    features = prepared.get(str(int(params["delay_seconds"])))
    if not features or not quote_gate(features, params):
        return 0.0, {"enter": False, "skip_reason": "missing_or_gate_failed"}
    net_bps = safe_float(features.get("btc_window_net_5m_bps"))
    realized_vol = safe_float(features.get("btc_window_realized_vol_5m_bps"))
    efficiency = safe_float(features.get("btc_window_efficiency_5m"))
    if any(math.isnan(value) for value in (net_bps, realized_vol, efficiency)):
        return 0.0, {"enter": False, "skip_reason": "missing_btc_window"}
    scored = synthetic_ev_score(case, features, params)
    if scored is None:
        return 0.0, {"enter": False, "skip_reason": "missing_spot_score"}
    side_net_bps = side_sign(case, params) * net_bps
    trend_score = (
        side_net_bps / max(float(params["vol_floor_bps"]), realized_vol)
        * efficiency
        - float(params["pressure_penalty"]) * safe_float(features.get("pressure"))
        - float(params["spread_penalty"]) * safe_float(features.get("spread"))
    )
    if realized_vol > float(params["max_realized_vol_bps"]):
        return 0.0, {"enter": False, "skip_reason": "realized_vol_too_high", "score": round(trend_score, 6)}
    if side_net_bps < float(params["min_side_net_bps"]):
        return 0.0, {"enter": False, "skip_reason": "side_net_too_low", "score": round(trend_score, 6)}
    if scored["ev_cents"] < float(params["min_ev_cents"]):
        return 0.0, {"enter": False, "skip_reason": "raw_ev_too_low", "score": round(trend_score, 6)}
    if trend_score < float(params["min_trend_score"]):
        return 0.0, {"enter": False, "skip_reason": "trend_efficiency_too_low", "score": round(trend_score, 6)}
    return entry_meta(
        case,
        features,
        {
            "score": round(trend_score, 6),
            "side_net_bps": round(side_net_bps, 6),
            "realized_vol_bps": round(realized_vol, 6),
            "efficiency": round(efficiency, 6),
            "raw_ev_cents": round(scored["ev_cents"], 6),
            "q_spot": round(scored["q_spot"], 6),
        },
    )


def bucket_key(case: dict[str, Any], features: dict[str, Any], scored: dict[str, float], params: dict[str, Any]) -> tuple[Any, ...]:
    q_width = float(params["q_bucket_width"])
    ask_width = float(params["ask_bucket_width"])
    q_bin = math.floor(scored["q_spot"] / q_width) * q_width
    ask_bin = math.floor(safe_float(features.get("held_ask")) / ask_width) * ask_width
    if bool(params.get("side_specific", True)):
        return (round(q_bin, 4), int(ask_bin), str(case.get("side")))
    return (round(q_bin, 4), int(ask_bin))


def wilson_lower_bound(wins: int, n: int, z: float, prior_strength: float, prior_mean: float) -> float:
    if n <= 0:
        return prior_mean
    p_hat = (wins + prior_strength * prior_mean) / (n + prior_strength)
    n_eff = n + prior_strength
    if z <= 0:
        return p_hat
    denom = 1.0 + z * z / n_eff
    center = p_hat + z * z / (2.0 * n_eff)
    radius = z * math.sqrt((p_hat * (1.0 - p_hat) + z * z / (4.0 * n_eff)) / n_eff)
    return max(0.0, (center - radius) / denom)


def run_online_spot_score_lcb(
    prepped: list[tuple[dict[str, Any], dict[str, Any]]],
    params: dict[str, Any],
    label: str,
    seed_prepped: list[tuple[dict[str, Any], dict[str, Any]]] | None = None,
) -> dict[str, Any]:
    stats: dict[tuple[Any, ...], list[int]] = {}
    global_stats = [0, 0]

    def update_history(items: list[tuple[dict[str, Any], dict[str, Any]]]) -> None:
        for case, prepared in sorted(items, key=lambda item: (item[0]["entry_ts"], item[0]["market"], item[0]["side"])):
            features = prepared.get(str(int(params["delay_seconds"])))
            if not features or not quote_gate(features, params):
                continue
            scored = synthetic_ev_score(case, features, params)
            if scored is None:
                continue
            key = bucket_key(case, features, scored, params)
            bucket = stats.setdefault(key, [0, 0])
            bucket[0] += 1
            bucket[1] += 1 if bool(case["settlement_win"]) else 0
            global_stats[0] += 1
            global_stats[1] += 1 if bool(case["settlement_win"]) else 0

    def decide(case: dict[str, Any], prepared: dict[str, Any]) -> tuple[float, dict[str, Any]]:
        features = prepared.get(str(int(params["delay_seconds"])))
        if not features or not quote_gate(features, params):
            return 0.0, {"enter": False, "skip_reason": "missing_or_gate_failed"}
        scored = synthetic_ev_score(case, features, params)
        if scored is None:
            return 0.0, {"enter": False, "skip_reason": "missing_spot_score"}
        if scored["ev_cents"] < float(params["min_raw_ev_cents"]):
            return 0.0, {"enter": False, "skip_reason": "raw_ev_too_low", "score": round(scored["ev_cents"], 6)}
        key = bucket_key(case, features, scored, params)
        n, wins = stats.get(key, [0, 0])
        if n < int(params["min_bucket_n"]):
            n, wins = global_stats
        if n < int(params["min_history_n"]):
            return 0.0, {"enter": False, "skip_reason": "insufficient_online_history", "score": round(scored["ev_cents"], 6)}
        q_lcb = wilson_lower_bound(
            wins,
            n,
            float(params["lcb_z"]),
            float(params["prior_strength"]),
            scored["q_spot"],
        )
        ask = safe_float(features.get("held_ask"))
        fee_per_contract = estimated_order_fee_cents(ask, max(1, int(case["qty"]))) / max(1, int(case["qty"]))
        lcb_ev = 100.0 * q_lcb - ask - fee_per_contract
        if lcb_ev < float(params["min_lcb_ev_cents"]):
            return 0.0, {"enter": False, "skip_reason": "lcb_ev_too_low", "score": round(lcb_ev, 6)}
        return entry_meta(
            case,
            features,
            {
                "score": round(lcb_ev, 6),
                "raw_ev_cents": round(scored["ev_cents"], 6),
                "q_spot": round(scored["q_spot"], 6),
                "q_lcb": round(q_lcb, 6),
                "history_n": n,
            },
        )

    if seed_prepped:
        update_history(seed_prepped)

    rows: list[dict[str, Any]] = []
    for case, prepared in sorted(prepped, key=lambda item: (item[0]["entry_ts"], item[0]["market"], item[0]["side"])):
        pnl, meta = decide(case, prepared)
        rows.append(row_for(case, pnl, meta, label))
        update_history([(case, prepared)])
    return {
        "strategy_id": label,
        "family": "online_spot_score_lcb_admission",
        "theorem": ONLINE_THEOREM,
        "equation": ONLINE_EQUATION,
        "params": params,
        "summary": summarize_entry_rows(label, rows),
        "by_dataset": summarize_by_group(label, rows, "dataset"),
        "by_side": summarize_by_group(label, rows, "side"),
        "by_day": summarize_by_group(label, rows, "entry_day_et"),
        "interesting_examples": sorted(rows, key=lambda row: (float(row["sim_pnl"]), row["market"]))[:10],
    }


def row_for(case: dict[str, Any], pnl: float, meta: dict[str, Any], label: str) -> dict[str, Any]:
    entered = bool(meta.get("enter"))
    return {
        "label": label,
        "dataset": case["dataset"],
        "market": case["market"],
        "side": case.get("side"),
        "entry_day_et": case["entry_day_et"],
        "entry_ts": case["entry_ts"],
        "settlement_win": bool(case["settlement_win"]),
        "actual_net_pnl": float(case["actual_net_pnl"]),
        "hold_pnl": float(case["hold_pnl"]),
        "sim_pnl": float(pnl),
        "action": "enter" if entered else "skip",
        "entry_ask": meta.get("entry_ask") if entered else None,
        "entry_elapsed": meta.get("entry_elapsed") if entered else None,
        "contracts": int(meta.get("contracts") or 0) if entered else 0,
        "base_contracts": int(case["qty"]),
        "skip_reason": meta.get("skip_reason"),
        "score": meta.get("score"),
    }


def summarize_entry_rows(label: str, rows: list[dict[str, Any]]) -> dict[str, Any]:
    entered = [row for row in rows if row["action"] == "enter"]
    skipped = [row for row in rows if row["action"] == "skip"]
    entered_winners = [row for row in entered if row["settlement_win"]]
    entered_losers = [row for row in entered if not row["settlement_win"]]
    skipped_winners = [row for row in skipped if row["settlement_win"]]
    skipped_losers = [row for row in skipped if not row["settlement_win"]]
    actual = sum(float(row["actual_net_pnl"]) for row in rows)
    no_stop = sum(float(row["hold_pnl"]) for row in rows)
    sim = sum(float(row["sim_pnl"]) for row in rows)
    total_contracts = sum(int(row["contracts"]) for row in entered)
    base_contracts = sum(int(row["base_contracts"]) for row in rows)
    return {
        "label": label,
        "n": len(rows),
        "actual_recorded_pnl": round(actual, 2),
        "no_stop_hold_pnl": round(no_stop, 2),
        "no_trade_all_pnl": 0.0,
        "sim_pnl": round(sim, 2),
        "delta_vs_actual": round(sim - actual, 2),
        "delta_vs_no_stop": round(sim - no_stop, 2),
        "delta_vs_no_trade_all": round(sim, 2),
        "entries": len(entered),
        "skips": len(skipped),
        "entered_settlement_winners": len(entered_winners),
        "entered_settlement_losers": len(entered_losers),
        "skipped_settlement_winners": len(skipped_winners),
        "skipped_settlement_losers": len(skipped_losers),
        "entry_win_rate": round(len(entered_winners) / len(entered), 4) if entered else 0.0,
        "avg_entry_ask": round(mean([float(row["entry_ask"]) for row in entered if row["entry_ask"] is not None]), 4)
        if entered
        else None,
        "avg_entry_elapsed": round(
            mean([float(row["entry_elapsed"]) for row in entered if row["entry_elapsed"] is not None]), 4
        )
        if entered
        else None,
        "avg_score": round(mean([safe_float(row.get("score")) for row in entered]), 6) if entered else None,
        "total_contracts": total_contracts,
        "base_contracts": base_contracts,
        "contract_fraction": round(total_contracts / base_contracts, 4) if base_contracts else 0.0,
        "worst_trade": round(min(float(row["sim_pnl"]) for row in entered), 4) if entered else 0.0,
    }


def summarize_by_group(label: str, rows: list[dict[str, Any]], key: str) -> dict[str, dict[str, Any]]:
    return {
        value: summarize_entry_rows(label, [row for row in rows if str(row.get(key)) == value])
        for value in sorted({str(row.get(key)) for row in rows})
    }


def run_strategy(
    prepped: list[tuple[dict[str, Any], dict[str, Any]]],
    strategy: StrategySpec,
    seed_prepped: list[tuple[dict[str, Any], dict[str, Any]]] | None = None,
) -> dict[str, Any]:
    sid = strategy_id(strategy.family, strategy.params)
    if strategy.online:
        return run_online_spot_score_lcb(prepped, strategy.params, sid, seed_prepped=seed_prepped)
    if strategy.simulator is None:
        raise ValueError(f"Missing simulator for {strategy.family}")
    rows = [row_for(case, *strategy.simulator(case, prepared, strategy.params), sid) for case, prepared in prepped]
    return {
        "strategy_id": sid,
        "family": strategy.family,
        "theorem": strategy.theorem,
        "equation": strategy.equation,
        "params": strategy.params,
        "summary": summarize_entry_rows(sid, rows),
        "by_dataset": summarize_by_group(sid, rows, "dataset"),
        "by_side": summarize_by_group(sid, rows, "side"),
        "by_day": summarize_by_group(sid, rows, "entry_day_et"),
        "interesting_examples": sorted(rows, key=lambda row: (float(row["sim_pnl"]), row["market"]))[:10],
    }


LAG_THEOREM = (
    "A delayed entry is attractive when BTC spot has moved in the held side's favor faster than the Kalshi quote has repriced; "
    "the residual tests cross-asset lead-lag instead of raw BTC momentum."
)
LAG_EQUATION = (
    "L=s*(BTC_D-BTC_0)/BTC_0*10000-beta*(logit(H_D/100)-logit(H_0/100))*100"
    "-lambda*p_opp-mu*spread; enter if spot impulse, raw spot EV, and L clear thresholds."
)

EFF_THEOREM = (
    "Side-consistent BTC movement should be more reliable when it arrives as an efficient low-variance trend; "
    "choppy realized variance is treated as adverse selection even if net momentum is favorable."
)
EFF_EQUATION = (
    "E=s*net_5m_bps/sqrt(sum(r_i^2))*abs(net_5m_bps)/sum(|r_i|)-lambda*p_opp-mu*spread; "
    "enter if realized volatility is bounded and E plus raw EV pass thresholds."
)

ONLINE_THEOREM = (
    "The raw BTC synthetic EV score should be trusted only where prior finalized markets with similar score and ask buckets "
    "show an online lower-confidence win probability sufficient to pay the ask and fees."
)
ONLINE_EQUATION = (
    "q_lcb=WilsonLCB(wins_bucket,n_bucket; prior=q_spot); EV_lcb=100*q_lcb-H_D-fee; "
    "enter if EV_raw and EV_lcb pass thresholds using only earlier markets."
)


def build_strategy_grid() -> list[StrategySpec]:
    strategies: list[StrategySpec] = []

    for delay_seconds in (120, 180):
        for max_entry_ask in (88, 90):
            for max_opp_pressure in (0.30, 0.50):
                for max_spread in (4, 10):
                    for min_spot_impulse_bps in (0.0, 2.0):
                        for quote_beta in (0.10, 0.25):
                            for min_lag_score in (0.0, 2.0):
                                for min_ev_cents in (-2.0, 2.0):
                                    params = {
                                        **PRIOR_SYNTHETIC_EV_PARAMS,
                                        "delay_seconds": delay_seconds,
                                        "anchor_delay_seconds": 0,
                                        "max_entry_ask": max_entry_ask,
                                        "max_opp_pressure": max_opp_pressure,
                                        "max_spread": max_spread,
                                        "min_spot_impulse_bps": min_spot_impulse_bps,
                                        "quote_beta": quote_beta,
                                        "min_lag_score": min_lag_score,
                                        "min_ev_cents": min_ev_cents,
                                        "side_polarity": 1,
                                    }
                                    strategies.append(
                                        StrategySpec(
                                            "spot_quote_lag_residual_admission",
                                            LAG_THEOREM,
                                            LAG_EQUATION,
                                            params,
                                            sim_spot_quote_lag_residual,
                                        )
                                    )

    for delay_seconds in (120, 180):
        for max_entry_ask in (88, 90):
            for max_opp_pressure in (0.30, 0.50):
                for max_spread in (4, 10):
                    for min_side_net_bps in (0.0, 2.0):
                        for min_trend_score in (-0.20, 0.0, 0.20):
                            for max_realized_vol_bps in (8.0, 15.0, 30.0):
                                for min_ev_cents in (-2.0, 2.0):
                                    params = {
                                        **PRIOR_SYNTHETIC_EV_PARAMS,
                                        "delay_seconds": delay_seconds,
                                        "max_entry_ask": max_entry_ask,
                                        "max_opp_pressure": max_opp_pressure,
                                        "max_spread": max_spread,
                                        "min_side_net_bps": min_side_net_bps,
                                        "min_trend_score": min_trend_score,
                                        "max_realized_vol_bps": max_realized_vol_bps,
                                        "vol_floor_bps": 1.0,
                                        "min_ev_cents": min_ev_cents,
                                        "side_polarity": 1,
                                    }
                                    strategies.append(
                                        StrategySpec(
                                            "btc_realized_efficiency_admission",
                                            EFF_THEOREM,
                                            EFF_EQUATION,
                                            params,
                                            sim_btc_realized_efficiency,
                                        )
                                    )

    for max_entry_ask in (88, 90):
        for max_opp_pressure in (0.30, 0.50):
            for max_spread in (4,):
                for min_raw_ev_cents in (-2.0, 2.0):
                    for min_lcb_ev_cents in (-2.0, 0.0):
                        for min_history_n in (20, 50):
                            for min_bucket_n in (3,):
                                for lcb_z in (0.0, 0.5, 1.0):
                                    params = {
                                        **PRIOR_SYNTHETIC_EV_PARAMS,
                                        "delay_seconds": 120,
                                        "max_entry_ask": max_entry_ask,
                                        "max_opp_pressure": max_opp_pressure,
                                        "max_spread": max_spread,
                                        "min_raw_ev_cents": min_raw_ev_cents,
                                        "min_lcb_ev_cents": min_lcb_ev_cents,
                                        "min_history_n": min_history_n,
                                        "min_bucket_n": min_bucket_n,
                                        "lcb_z": lcb_z,
                                        "prior_strength": 10.0,
                                        "q_bucket_width": 0.05,
                                        "ask_bucket_width": 5.0,
                                        "side_specific": True,
                                        "side_polarity": 1,
                                    }
                                    strategies.append(
                                        StrategySpec(
                                            "online_spot_score_lcb_admission",
                                            ONLINE_THEOREM,
                                            ONLINE_EQUATION,
                                            params,
                                            online=True,
                                        )
                                    )

    return strategies


def min_entries(holdout: bool = False) -> int:
    return 10 if holdout else 25


def select_family_best(results: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    output: dict[str, dict[str, Any]] = {}
    for family in sorted({result["family"] for result in results}):
        family_results = [result for result in results if result["family"] == family]
        candidates = [result for result in family_results if result["summary"]["entries"] >= min_entries()] or family_results
        output[family] = max(
            candidates,
            key=lambda result: (
                result["summary"]["sim_pnl"],
                result["summary"]["entry_win_rate"],
                -(result["summary"]["avg_entry_ask"] or 0.0),
            ),
        )
    return output


def ordered_split(prepped: list[tuple[dict[str, Any], dict[str, Any]]]) -> tuple[list[Any], list[Any], str | None]:
    ordered = sorted(prepped, key=lambda item: (item[0]["entry_ts"], item[0]["market"], item[0]["side"]))
    split = int(len(ordered) * 0.7)
    return ordered[:split], ordered[split:], ordered[split][0]["entry_ts"] if ordered[split:] else None


def walk_forward_summary(prepped: list[tuple[dict[str, Any], dict[str, Any]]], strategies: list[StrategySpec]) -> dict[str, Any]:
    train, holdout, split_ts = ordered_split(prepped)
    output: dict[str, Any] = {
        "train_n": len(train),
        "holdout_n": len(holdout),
        "split_entry_ts": split_ts,
        "selection_basis": "Max train simulated PnL among variants with at least 25 train entries; online holdout is seeded only with train history.",
        "families": {},
    }
    for family in sorted({strategy.family for strategy in strategies}):
        family_strategies = [strategy for strategy in strategies if strategy.family == family]
        train_results = [run_strategy(train, strategy) for strategy in family_strategies]
        train_candidates = [result for result in train_results if result["summary"]["entries"] >= min_entries()]
        selected = max(train_candidates or train_results, key=lambda result: result["summary"]["sim_pnl"])
        selected_spec = next(
            strategy
            for strategy in family_strategies
            if strategy_id(strategy.family, strategy.params) == selected["strategy_id"]
        )
        holdout_result = run_strategy(holdout, selected_spec, seed_prepped=train if selected_spec.online else None)
        output["families"][family] = {
            "selected_strategy_id": selected["strategy_id"],
            "selected_params": selected["params"],
            "train_summary": selected["summary"],
            "holdout_summary": holdout_result["summary"],
            "holdout_by_dataset": holdout_result["by_dataset"],
            "holdout_by_side": holdout_result["by_side"],
        }
    return output


def robust_positive_scan(
    prepped: list[tuple[dict[str, Any], dict[str, Any]]],
    strategies: list[StrategySpec],
    full_results: list[dict[str, Any]],
    max_candidates_per_family: int,
) -> dict[str, list[dict[str, Any]]]:
    train, holdout, _split_ts = ordered_split(prepped)
    full_by_id = {result["strategy_id"]: result for result in full_results}
    output: dict[str, list[dict[str, Any]]] = {}
    for family in sorted({strategy.family for strategy in strategies}):
        rows: list[dict[str, Any]] = []
        screened = sorted(
            [
                strategy
                for strategy in strategies
                if strategy.family == family
                and full_by_id.get(strategy_id(strategy.family, strategy.params), {})
                .get("summary", {})
                .get("sim_pnl", 0.0)
                > 0
                and full_by_id.get(strategy_id(strategy.family, strategy.params), {})
                .get("summary", {})
                .get("entries", 0)
                >= min_entries()
            ],
            key=lambda strategy: full_by_id[strategy_id(strategy.family, strategy.params)]["summary"]["sim_pnl"],
            reverse=True,
        )[:max_candidates_per_family]
        for strategy in screened:
            train_result = run_strategy(train, strategy)
            holdout_result = run_strategy(holdout, strategy, seed_prepped=train if strategy.online else None)
            train_summary = train_result["summary"]
            holdout_summary = holdout_result["summary"]
            if (
                train_summary["sim_pnl"] <= 0
                or holdout_summary["sim_pnl"] <= 0
                or train_summary["entries"] < min_entries()
                or holdout_summary["entries"] < min_entries(holdout=True)
            ):
                continue
            rows.append(
                {
                    "strategy_id": train_result["strategy_id"],
                    "params": train_result["params"],
                    "train_sim_pnl": train_summary["sim_pnl"],
                    "train_entries": train_summary["entries"],
                    "train_entry_win_rate": train_summary["entry_win_rate"],
                    "holdout_sim_pnl": holdout_summary["sim_pnl"],
                    "holdout_entries": holdout_summary["entries"],
                    "holdout_entry_win_rate": holdout_summary["entry_win_rate"],
                    "min_split_pnl": min(train_summary["sim_pnl"], holdout_summary["sim_pnl"]),
                }
            )
        output[family] = sorted(
            rows,
            key=lambda row: (row["min_split_pnl"], row["holdout_sim_pnl"], row["train_sim_pnl"]),
            reverse=True,
        )[:20]
    return output


def sensitivity(results: list[dict[str, Any]], best_by_family: dict[str, dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    output: dict[str, list[dict[str, Any]]] = {}
    for family, best in best_by_family.items():
        ranked = sorted(
            [
                result
                for result in results
                if result["family"] == family and result["summary"]["entries"] >= min_entries()
            ],
            key=lambda result: (result_distance(result["params"], best["params"]), -result["summary"]["sim_pnl"]),
        )
        output[family] = [
            {
                "strategy_id": result["strategy_id"],
                "params": result["params"],
                "sim_pnl": result["summary"]["sim_pnl"],
                "delta_vs_actual": result["summary"]["delta_vs_actual"],
                "delta_vs_no_stop": result["summary"]["delta_vs_no_stop"],
                "delta_vs_no_trade_all": result["summary"]["delta_vs_no_trade_all"],
                "entries": result["summary"]["entries"],
                "entry_win_rate": result["summary"]["entry_win_rate"],
                "avg_entry_ask": result["summary"]["avg_entry_ask"],
            }
            for result in ranked[:12]
        ]
    return output


def status_for(family: str, result: dict[str, Any], payload: dict[str, Any]) -> str:
    holdout = payload["walk_forward"]["families"].get(family, {}).get("holdout_summary", {})
    robust_rows = payload["robust_positive_scan"].get(family, [])
    if (
        result["summary"]["delta_vs_no_trade_all"] > 0
        and holdout.get("delta_vs_no_trade_all", 0) > 0
        and len(robust_rows) >= 5
    ):
        return "candidate_for_human_review"
    if result["summary"]["delta_vs_no_trade_all"] > 0 and robust_rows:
        return "watchlist_positive_but_selection_sensitive"
    if result["summary"]["delta_vs_no_trade_all"] > 0:
        return "watchlist_positive_but_not_robust"
    return "tested_negative"


def baseline_payload(cases: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "actual": run_baseline(cases, "actual"),
        "no_stop": run_baseline(cases, "no_stop"),
        "held_ask_stop_70": run_baseline(cases, "held_ask_stop_70"),
        "no_trade_all": {"summary": {"sim_pnl": 0.0}},
    }


def write_markdown(path: Path, payload: dict[str, Any]) -> None:
    base = payload["baselines"]
    lines = [
        "# Codex Entry Spot/Quote Lag Edge Research",
        "",
        f"- Generated: `{payload['generated_at']}`",
        f"- Datasets: `{', '.join(payload['datasets'])}`",
        f"- Quote-path cases with BTC closed-candle features: `{payload['case_count']}`",
        "- Scope: research-only entry/no-trade simulation; live entry logic, live exit logic, configs, run scripts, and bot processes were not changed.",
        "- Non-repetition: these families test cross-asset quote lag, BTC realized-variance trend efficiency, and online score calibration, not the prior raw BTC synthetic EV, dwell, path geometry, clock/Markov priors, or microstructure-only gates.",
        "",
        "## Baselines",
        "",
        f"- Actual recorded PnL: `${base['actual']['summary']['sim_pnl']}`",
        f"- No-stop hold-to-settlement PnL using original entries: `${base['no_stop']['summary']['sim_pnl']}`",
        f"- First held-ask <=70 exit baseline: `${base['held_ask_stop_70']['summary']['sim_pnl']}`",
        "- Skip every opportunity baseline: `$0.0`",
        "",
        "## New Equation Families",
        "",
    ]
    for family, result in payload["best_by_family"].items():
        summary = result["summary"]
        walk = payload["walk_forward"]["families"].get(family, {})
        holdout = walk.get("holdout_summary", {})
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
                f"- Avg entry ask / elapsed / avg score / contract fraction: `{summary['avg_entry_ask']} / {summary['avg_entry_elapsed']} / {summary['avg_score']} / {summary['contract_fraction']}`",
                f"- Train-selected params: `{json.dumps(walk.get('selected_params'), sort_keys=True)}`",
                f"- Train-selected holdout PnL / delta vs actual / delta vs no-stop / delta vs skip-all: `${holdout.get('sim_pnl')}` / `${holdout.get('delta_vs_actual')}` / `${holdout.get('delta_vs_no_stop')}` / `${holdout.get('delta_vs_no_trade_all')}`",
                f"- Holdout entries / skipped winners / skipped losers / win rate: `{holdout.get('entries')} / {holdout.get('skipped_settlement_winners')} / {holdout.get('skipped_settlement_losers')} / {holdout.get('entry_win_rate')}`",
            ]
        )
        dataset_bits = []
        for dataset, row in result["by_dataset"].items():
            dataset_bits.append(f"{dataset}: ${row['sim_pnl']} ({row['entries']} entries)")
        side_bits = []
        for side, row in result["by_side"].items():
            side_bits.append(f"{side}: ${row['sim_pnl']} ({row['entries']} entries)")
        lines.append(f"- By dataset: `{' ; '.join(dataset_bits)}`")
        lines.append(f"- By side: `{' ; '.join(side_bits)}`")
        lines.append("")

    lines.extend(["## Robust Positive Split Scan", ""])
    lines.append("| Family | Strategy | Train PnL | Holdout PnL | Holdout entries | Holdout win rate | Params |")
    lines.append("|---|---|---:|---:|---:|---:|---|")
    for family, rows in payload["robust_positive_scan"].items():
        if not rows:
            lines.append(f"| `{family}` | none |  |  |  |  | no train-positive and holdout-positive parameterization found |")
            continue
        for row in rows[:10]:
            lines.append(
                f"| `{family}` | `{row['strategy_id']}` | {row['train_sim_pnl']} | {row['holdout_sim_pnl']} | "
                f"{row['holdout_entries']} | {row['holdout_entry_win_rate']} | `{json.dumps(row['params'], sort_keys=True)}` |"
            )

    lines.extend(["", "## Nearby Sensitivity", ""])
    lines.append("| Family | Params | PnL | Entries | Win rate | Avg ask |")
    lines.append("|---|---|---:|---:|---:|---:|")
    for family, rows in payload["sensitivity"].items():
        for row in rows[:8]:
            lines.append(
                f"| `{family}` | `{json.dumps(row['params'], sort_keys=True)}` | {row['sim_pnl']} | "
                f"{row['entries']} | {row['entry_win_rate']} | {row['avg_entry_ask']} |"
            )

    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "- The lead-lag branch asks whether BTC spot has moved before Kalshi reprices, so it is not equivalent to simply buying high BTC synthetic EV.",
            "- The realized-efficiency branch penalizes choppy spot paths even when net BTC direction is favorable.",
            "- The online calibration branch uses prior finalized markets only; settlement labels are used for historical scoring and online history updates after each simulated decision.",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Research-only cross-asset spot/quote lag entry probes.")
    parser.add_argument("--refresh-cache", action="store_true")
    parser.add_argument("--datasets", nargs="*", default=None)
    args = parser.parse_args()

    datasets = args.datasets or discover_datasets()
    payloads = [load_dataset_cases(dataset, refresh_cache=False) for dataset in datasets]
    cases: list[dict[str, Any]] = []
    for payload in payloads:
        dataset = payload.get("dataset")
        for case in payload.get("cases", []):
            case.setdefault("dataset", dataset)
            cases.append(case)
    cases = sorted(cases, key=lambda item: (item["entry_ts"], item["market"], item["side"]))

    candles = load_cached_candles(cases, refresh_cache=args.refresh_cache)
    strategies = build_strategy_grid()
    delays = tuple(sorted({0, *[int(strategy.params["delay_seconds"]) for strategy in strategies]}))
    prepped_all = [
        (case, augment_btc_windows(prepare_case(case, candles, delays), candles))
        for case in cases
    ]
    prepped = [(case, prepared) for case, prepared in prepped_all if any(value is not None for value in prepared.values())]

    results = [run_strategy(prepped, strategy) for strategy in strategies]
    best_by_family = select_family_best(results)
    walk = walk_forward_summary(prepped, strategies)
    robust_scan = robust_positive_scan(prepped, strategies, results, max_candidates_per_family=250)
    sens = sensitivity(results, best_by_family)

    generated_at = datetime.now(UTC).isoformat()
    stamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
    json_path = EDGE_DIR / f"codex_entry_spot_quote_lag_research_{stamp}.json"
    md_path = EDGE_DIR / f"codex_entry_spot_quote_lag_research_{stamp}.md"
    latest_json = EDGE_DIR / "codex_entry_spot_quote_lag_research_latest.json"
    latest_md = EDGE_DIR / "codex_entry_spot_quote_lag_research_latest.md"

    report_payload = {
        "generated_at": generated_at,
        "dataset": "all_quote_path_trades_with_closed_1m_btc",
        "datasets": sorted({str(case.get("dataset")) for case, _prepared in prepped}),
        "requested_datasets": datasets,
        "dataset_payloads": [
            {
                "dataset": payload.get("dataset"),
                "raw_trades_total": payload.get("raw_trades_total"),
                "trades_total": payload.get("trades_total"),
                "case_count": len(payload.get("cases", [])),
                "cache_path": payload.get("cache_path"),
            }
            for payload in payloads
        ],
        "case_count": len(prepped),
        "raw_case_count": len(cases),
        "strategy_count": len(strategies),
        "btc_candle_source": "Cached Binance public 1m candles; latest closed candle before quote snapshot target",
        "baselines": baseline_payload([case for case, _prepared in prepped]),
        "best_by_family": best_by_family,
        "walk_forward": walk,
        "robust_positive_scan": robust_scan,
        "sensitivity": sens,
        "json_path": str(json_path),
        "markdown_path": str(md_path),
        "feature_availability": {
            "spot_quote_lag_residual_admission": "quote heartbeat snapshots at entry and delayed decision plus latest fully closed BTC 1m candles at those times",
            "btc_realized_efficiency_admission": "latest closed BTC 1m candle window ending before the delayed quote snapshot",
            "online_spot_score_lcb_admission": "quote heartbeat snapshot, BTC closed-candle spot score, and prior finalized market outcomes only",
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
        walk_family = walk["families"].get(family, {})
        ledger_records.append(
            {
                "recorded_at": generated_at,
                "generated_at": generated_at,
                "source": Path(__file__).name,
                "status": status_for(family, result, report_payload),
                "dataset": report_payload["dataset"],
                "datasets": report_payload["datasets"],
                "family": family,
                "theorem": result["theorem"],
                "equation": result["equation"],
                "params": result["params"],
                "strategy_id": result["strategy_id"],
                "idea_key": idea_key(family, result["equation"], result["params"]),
                "summary": result["summary"],
                "train_summary": walk_family.get("train_summary"),
                "holdout_summary": walk_family.get("holdout_summary"),
                "walk_forward_selected_strategy_id": walk_family.get("selected_strategy_id"),
                "walk_forward_selected_params": walk_family.get("selected_params"),
                "robust_positive_count": len(robust_scan.get(family, [])),
                "json_path": str(json_path),
                "markdown_path": str(md_path),
            }
        )
    append_ledger(ledger_records)
    update_strategy_memory(report_payload, best_by_family)

    print(f"Saved JSON: {json_path}")
    print(f"Saved Markdown: {md_path}")
    print(f"Cases={len(prepped)} raw_cases={len(cases)} strategies={len(strategies)}")
    for family, result in best_by_family.items():
        summary = result["summary"]
        holdout = walk["families"].get(family, {}).get("holdout_summary", {})
        print(
            f"{family} {result['strategy_id']} status={status_for(family, result, report_payload)} "
            f"full_sim={summary['sim_pnl']} full_delta_actual={summary['delta_vs_actual']} "
            f"full_delta_skip={summary['delta_vs_no_trade_all']} entries={summary['entries']} "
            f"holdout_sim={holdout.get('sim_pnl')} holdout_delta_skip={holdout.get('delta_vs_no_trade_all')} "
            f"holdout_entries={holdout.get('entries')}"
        )


if __name__ == "__main__":
    main()
