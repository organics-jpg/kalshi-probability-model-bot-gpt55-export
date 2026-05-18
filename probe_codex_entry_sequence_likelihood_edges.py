from __future__ import annotations

import argparse
import json
import math
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

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
    result_distance,
    strategy_id,
    update_strategy_memory,
)


UTC = timezone.utc


@dataclass(frozen=True)
class StrategySpec:
    family: str
    theorem: str
    equation: str
    params: dict[str, Any]
    simulator: Callable[
        [dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any] | None],
        tuple[float, dict[str, Any]],
    ]
    model_builder: Callable[[list[tuple[dict[str, Any], dict[str, Any]]], dict[str, Any]], dict[str, Any]] | None = None
    model_updater: Callable[[dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any]], None] | None = None


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


def prefix_points(case: dict[str, Any], delay_seconds: int) -> list[dict[str, Any]]:
    points: list[dict[str, Any]] = []
    reached = False
    for point in case.get("path", []):
        elapsed = safe_float(point.get("elapsed"))
        held_ask = safe_float(point.get("held_ask"))
        if math.isnan(elapsed) or math.isnan(held_ask):
            continue
        points.append(point)
        if elapsed >= float(delay_seconds):
            reached = True
            break
    return points if reached else []


def prepare_case(case: dict[str, Any], delays: tuple[int, ...]) -> dict[str, Any]:
    return {str(delay): prefix_points(case, delay) for delay in delays}


def ask_token(delta: float, band: float) -> str:
    if delta >= band:
        return "U"
    if delta <= -band:
        return "D"
    return "F"


def pressure_token(delta: float, band: float) -> str:
    if math.isnan(delta):
        return "N"
    if delta >= band:
        return "P"
    if delta <= -band:
        return "Q"
    return "Z"


def path_features(prepared: dict[str, Any], params: dict[str, Any]) -> dict[str, Any] | None:
    delay = str(int(params["delay_seconds"]))
    points = prepared.get(delay) or []
    valid = [
        point
        for point in points
        if not math.isnan(safe_float(point.get("elapsed"))) and not math.isnan(safe_float(point.get("held_ask")))
    ]
    if len(valid) < 2:
        return None

    asks = [safe_float(point["held_ask"]) for point in valid]
    times = [safe_float(point["elapsed"]) for point in valid]
    pressures = [pressure(point) for point in valid]
    bid_sums = [safe_float(point.get("bid_sum")) for point in valid]
    current = asks[-1]
    start = asks[0]
    high = max(asks)
    low = min(asks)
    elapsed = times[-1]
    span = max(1.0, elapsed - times[0])
    deltas = [asks[idx] - asks[idx - 1] for idx in range(1, len(asks))]
    pressure_deltas = [pressures[idx] - pressures[idx - 1] for idx in range(1, len(pressures))]

    token_band = float(params.get("token_band_cents", 1.0))
    pressure_band = float(params.get("pressure_token_band", 0.05))
    tokens = [
        ask_token(delta, token_band) + pressure_token(p_delta, pressure_band)
        for delta, p_delta in zip(deltas, pressure_deltas)
    ]
    ask_tokens = [ask_token(delta, token_band) for delta in deltas]
    up_semivar = sum(max(0.0, delta) ** 2 for delta in deltas) / max(1, len(deltas))
    down_semivar = sum(max(0.0, -delta) ** 2 for delta in deltas) / max(1, len(deltas))
    path_len = sum(abs(delta) for delta in deltas)
    down_penalty = float(params.get("downside_penalty", 1.0))
    semivar_score = (up_semivar - down_penalty * down_semivar) / (path_len + 1.0)
    drawdown = max(0.0, start - low)
    rebound = current - low

    slack_pairs = [
        (100.0 - bid_sum, ask)
        for bid_sum, ask in zip(bid_sums, asks)
        if not math.isnan(bid_sum) and bid_sum > 0
    ]
    if len(slack_pairs) >= 2:
        slack_values = [item[0] for item in slack_pairs]
        ask_values = [item[1] for item in slack_pairs]
        slack_mean = mean(slack_values)
        ask_mean = mean(ask_values)
        var_slack = sum((value - slack_mean) ** 2 for value in slack_values) / len(slack_values)
        cov = sum((slack - slack_mean) * (ask - ask_mean) for slack, ask in slack_pairs) / len(slack_pairs)
        slack_beta = cov / var_slack if var_slack > 1e-9 else 0.0
    else:
        slack_beta = 0.0
    bid_sum_end = safe_float(valid[-1].get("bid_sum"))
    slack_end = 100.0 - bid_sum_end if not math.isnan(bid_sum_end) else math.nan
    discount_gain = max(0.0, start - current) / (1.0 + max(0.0, slack_end if not math.isnan(slack_end) else 99.0))
    elasticity_score = discount_gain - slack_beta

    return {
        "elapsed": elapsed,
        "held_ask": current,
        "start_ask": start,
        "high": high,
        "low": low,
        "range": high - low,
        "span": span,
        "token_count": len(tokens),
        "tokens": tokens,
        "ask_tokens": ask_tokens,
        "up_semivar": up_semivar,
        "down_semivar": down_semivar,
        "semivar_score": semivar_score,
        "drawdown": drawdown,
        "rebound": rebound,
        "slack_beta": slack_beta,
        "slack_end": slack_end,
        "elasticity_score": elasticity_score,
        "pressure_end": pressures[-1],
        "bid_sum_end": bid_sum_end,
        "spread_end": spread(valid[-1]),
    }


def base_quote_gate(features: dict[str, Any], params: dict[str, Any]) -> bool:
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
        and features["token_count"] >= int(params.get("min_tokens", 1))
    )


def entry_meta(case: dict[str, Any], ask: float, features: dict[str, Any], extra: dict[str, Any]) -> tuple[float, dict[str, Any]]:
    pnl = delayed_entry_pnl(case, ask)
    return pnl, {
        "enter": True,
        "entry_ask": ask,
        "entry_elapsed": features["elapsed"],
        "contracts": int(case["qty"]),
        "pressure_end": round(safe_float(features.get("pressure_end")), 6),
        "spread_end": round(safe_float(features.get("spread_end")), 4),
        "bid_sum_end": round(safe_float(features.get("bid_sum_end")), 4),
        **extra,
    }


def empty_token_model() -> dict[str, Any]:
    return {
        "docs_win": 0,
        "docs_loss": 0,
        "total_win": 0,
        "total_loss": 0,
        "token_win": {},
        "token_loss": {},
        "vocab": [],
    }


def update_token_model(model: dict[str, Any], case: dict[str, Any], prepared: dict[str, Any], params: dict[str, Any]) -> None:
    features = path_features(prepared, params)
    if not features or features["token_count"] < int(params.get("min_tokens", 1)):
        return
    win = bool(case["settlement_win"])
    doc_key = "docs_win" if win else "docs_loss"
    total_key = "total_win" if win else "total_loss"
    token_key = "token_win" if win else "token_loss"
    model[doc_key] = int(model.get(doc_key, 0)) + 1
    token_counts = model.setdefault(token_key, {})
    vocab = set(model.get("vocab", []))
    for token in features["tokens"]:
        token_counts[token] = int(token_counts.get(token, 0)) + 1
        model[total_key] = int(model.get(total_key, 0)) + 1
        vocab.add(token)
    model["vocab"] = sorted(vocab)


def build_token_model(prepped: list[tuple[dict[str, Any], dict[str, Any]]], params: dict[str, Any]) -> dict[str, Any]:
    model = empty_token_model()
    for case, prepared in sorted(prepped, key=lambda item: item[0]["entry_ts"]):
        update_token_model(model, case, prepared, params)
    return model


def token_llr(features: dict[str, Any], model: dict[str, Any], params: dict[str, Any]) -> tuple[float, dict[str, Any]]:
    docs_win = int(model.get("docs_win", 0))
    docs_loss = int(model.get("docs_loss", 0))
    history = docs_win + docs_loss
    if history < int(params["min_history"]):
        return math.nan, {"history": history, "skip_reason": "insufficient_history"}
    alpha = float(params["token_alpha"])
    vocab = set(model.get("vocab", [])) | set(features["tokens"])
    vocab_size = max(1, len(vocab))
    total_win = int(model.get("total_win", 0))
    total_loss = int(model.get("total_loss", 0))
    token_win = model.get("token_win", {})
    token_loss = model.get("token_loss", {})
    prior = math.log((docs_win + alpha) / (docs_loss + alpha))
    llr = prior
    for token in features["tokens"]:
        pw = (float(token_win.get(token, 0)) + alpha) / (total_win + alpha * vocab_size)
        pl = (float(token_loss.get(token, 0)) + alpha) / (total_loss + alpha * vocab_size)
        llr += math.log(pw / pl)
    norm = math.sqrt(max(1.0, float(len(features["tokens"]))))
    return llr / norm, {"history": history, "token_vocab": vocab_size, "raw_llr": llr}


def sim_quote_token_likelihood_admission(
    case: dict[str, Any], prepared: dict[str, Any], params: dict[str, Any], model: dict[str, Any] | None
) -> tuple[float, dict[str, Any]]:
    if model is None:
        raise ValueError("quote token likelihood requires a model")
    features = path_features(prepared, params)
    if not features or not base_quote_gate(features, params):
        return 0.0, {"enter": False, "skip_reason": "missing_or_failed_quote_gate"}
    score, score_meta = token_llr(features, model, params)
    if math.isnan(score):
        return 0.0, {"enter": False, **score_meta}
    if score >= float(params["min_token_llr"]):
        return entry_meta(
            case,
            safe_float(features["held_ask"]),
            features,
            {
                "token_llr": round(score, 6),
                "token_history": score_meta["history"],
                "raw_llr": round(score_meta["raw_llr"], 6),
            },
        )
    return 0.0, {"enter": False, "skip_reason": "token_likelihood_below_cut", "token_llr": round(score, 6)}


def sim_quote_semivariance_asymmetry_admission(
    case: dict[str, Any], prepared: dict[str, Any], params: dict[str, Any], model: dict[str, Any] | None
) -> tuple[float, dict[str, Any]]:
    del model
    features = path_features(prepared, params)
    if not features or not base_quote_gate(features, params):
        return 0.0, {"enter": False, "skip_reason": "missing_or_failed_quote_gate"}
    if (
        features["semivar_score"] >= float(params["min_semivar_score"])
        and features["drawdown"] <= float(params["max_drawdown"])
        and features["rebound"] >= float(params["min_rebound"])
    ):
        return entry_meta(
            case,
            safe_float(features["held_ask"]),
            features,
            {
                "semivar_score": round(safe_float(features["semivar_score"]), 6),
                "up_semivar": round(safe_float(features["up_semivar"]), 6),
                "down_semivar": round(safe_float(features["down_semivar"]), 6),
                "drawdown": round(safe_float(features["drawdown"]), 4),
                "rebound": round(safe_float(features["rebound"]), 4),
            },
        )
    return 0.0, {"enter": False, "skip_reason": "semivariance_gate_failed"}


def sim_slack_elasticity_discount_admission(
    case: dict[str, Any], prepared: dict[str, Any], params: dict[str, Any], model: dict[str, Any] | None
) -> tuple[float, dict[str, Any]]:
    del model
    features = path_features(prepared, params)
    if not features or not base_quote_gate(features, params):
        return 0.0, {"enter": False, "skip_reason": "missing_or_failed_quote_gate"}
    slack_end = safe_float(features["slack_end"])
    if (
        features["elasticity_score"] >= float(params["min_elasticity_score"])
        and slack_end <= float(params["max_slack_end"])
        and features["start_ask"] - features["held_ask"] >= float(params["min_discount_cents"])
    ):
        return entry_meta(
            case,
            safe_float(features["held_ask"]),
            features,
            {
                "elasticity_score": round(safe_float(features["elasticity_score"]), 6),
                "slack_beta": round(safe_float(features["slack_beta"]), 6),
                "slack_end": round(slack_end, 4),
                "discount_cents": round(safe_float(features["start_ask"] - features["held_ask"]), 4),
            },
        )
    return 0.0, {"enter": False, "skip_reason": "elasticity_gate_failed"}


def build_strategy_grid() -> list[StrategySpec]:
    strategies: list[StrategySpec] = []

    def add(
        family: str,
        theorem: str,
        equation: str,
        params: dict[str, Any],
        simulator: Callable[
            [dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any] | None],
            tuple[float, dict[str, Any]],
        ],
        model_builder: Callable[[list[tuple[dict[str, Any], dict[str, Any]]], dict[str, Any]], dict[str, Any]] | None = None,
        model_updater: Callable[[dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any]], None] | None = None,
    ) -> None:
        strategies.append(StrategySpec(family, theorem, equation, params, simulator, model_builder, model_updater))

    # Coarse grid by design: each family is new here, so prefer coverage across
    # equation shape and walk-forward checks over dense threshold duplication.
    for delay_seconds in (30, 60, 90):
        for max_entry_ask in (88, 90, 92):
            for max_opp_pressure in (0.25, 0.50):
                for max_spread in (4,):
                    for min_bid_sum in (0, 96):
                        for token_band_cents in (1.0, 2.0):
                            for min_token_llr in (0.0, 0.5):
                                for min_history in (40, 80):
                                    add(
                                        "online_quote_token_likelihood_admission",
                                        "The order and direction of early quote ticks should carry settlement information beyond the terminal ask; use only prior settled prefixes to score the current prefix.",
                                        "LLR=(log((W+a)/(L+a))+sum_t log(P(token_t|win)/P(token_t|loss)))/sqrt(n); enter at D only if H_D<=A, p_opp<=P, spread<=S, bid_sum>=B, and LLR>=k.",
                                        {
                                            "delay_seconds": delay_seconds,
                                            "max_entry_ask": max_entry_ask,
                                            "max_opp_pressure": max_opp_pressure,
                                            "max_spread": max_spread,
                                            "min_bid_sum": min_bid_sum,
                                            "min_tokens": 1,
                                            "token_band_cents": token_band_cents,
                                            "pressure_token_band": 0.05,
                                            "token_alpha": 0.5,
                                            "min_history": min_history,
                                            "min_token_llr": min_token_llr,
                                        },
                                        sim_quote_token_likelihood_admission,
                                        build_token_model,
                                        update_token_model,
                                    )

    for delay_seconds in (30, 60, 90):
        for max_entry_ask in (88, 90, 92):
            for max_opp_pressure in (0.25, 0.50):
                for max_spread in (4,):
                    for min_bid_sum in (0, 96):
                        for downside_penalty in (1.0, 2.0):
                            for min_semivar_score in (-0.25, 0.25):
                                for max_drawdown in (4, 999):
                                    for min_rebound in (0,):
                                        add(
                                            "quote_semivariance_asymmetry_admission",
                                            "A cheap or delayed quote is safer when squared upside quote increments dominate squared downside increments, not just when the final ask is low.",
                                            "S=(mean(max(dH,0)^2)-lambda*mean(max(-dH,0)^2))/(sum(|dH|)+1); enter if H_D<=A, S>=s, drawdown<=M, rebound>=R, p_opp<=P, spread<=Z, and bid_sum>=B.",
                                            {
                                                "delay_seconds": delay_seconds,
                                                "max_entry_ask": max_entry_ask,
                                                "max_opp_pressure": max_opp_pressure,
                                                "max_spread": max_spread,
                                                "min_bid_sum": min_bid_sum,
                                                "min_tokens": 1,
                                                "token_band_cents": 1.0,
                                                "pressure_token_band": 0.05,
                                                "downside_penalty": downside_penalty,
                                                "min_semivar_score": min_semivar_score,
                                                "max_drawdown": max_drawdown,
                                                "min_rebound": min_rebound,
                                            },
                                            sim_quote_semivariance_asymmetry_admission,
                                        )

    for delay_seconds in (30, 60, 90, 120):
        for max_entry_ask in (84, 88, 90):
            for max_opp_pressure in (0.25, 0.50):
                for max_spread in (4,):
                    for min_bid_sum in (0, 96):
                        for min_discount_cents in (1, 4):
                            for max_slack_end in (2, 8):
                                for min_elasticity_score in (-1.0, 0.5):
                                    add(
                                        "book_slack_elasticity_discount_admission",
                                        "A lower entry ask is useful only if the discount is not explained by a loose two-sided book; regress quote against book slack before accepting the discount.",
                                        "beta=cov(H,100-bid_sum)/var(100-bid_sum), E=max(0,H_0-H_D)/(1+slack_D)-beta; enter if H_D<=A, H_0-H_D>=d, E>=e, slack_D<=m, p_opp<=P, spread<=S, and bid_sum>=B.",
                                        {
                                            "delay_seconds": delay_seconds,
                                            "max_entry_ask": max_entry_ask,
                                            "max_opp_pressure": max_opp_pressure,
                                            "max_spread": max_spread,
                                            "min_bid_sum": min_bid_sum,
                                            "min_tokens": 1,
                                            "token_band_cents": 1.0,
                                            "pressure_token_band": 0.05,
                                            "min_discount_cents": min_discount_cents,
                                            "max_slack_end": max_slack_end,
                                            "min_elasticity_score": min_elasticity_score,
                                        },
                                        sim_slack_elasticity_discount_admission,
                                    )

    return strategies


def row_for(case: dict[str, Any], pnl: float, meta: dict[str, Any], label: str) -> dict[str, Any]:
    return {
        "label": label,
        "dataset": case["dataset"],
        "market": case["market"],
        "side": case.get("side"),
        "entry_day_et": case["entry_day_et"],
        "settlement_win": bool(case["settlement_win"]),
        "actual_net_pnl": float(case["actual_net_pnl"]),
        "hold_pnl": float(case["hold_pnl"]),
        "sim_pnl": float(pnl),
        "action": "enter" if meta.get("enter") else "skip",
        "entry_ask": meta.get("entry_ask"),
        "entry_elapsed": meta.get("entry_elapsed"),
        "contracts": int(meta.get("contracts") or 0),
        "base_contracts": int(case["qty"]),
        "skip_reason": meta.get("skip_reason"),
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
        "avg_entry_ask": round(sum(float(row["entry_ask"]) for row in entered) / len(entered), 2) if entered else None,
        "total_contracts": total_contracts,
        "base_contracts": base_contracts,
        "contract_fraction": round(total_contracts / base_contracts, 4) if base_contracts else 0.0,
        "worst_trade": round(min(float(row["sim_pnl"]) for row in rows), 2) if rows else None,
    }


def summarize_by_dataset(label: str, rows: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    return {
        dataset: summarize_entry_rows(label, [row for row in rows if row["dataset"] == dataset])
        for dataset in sorted({row["dataset"] for row in rows})
    }


def summarize_by_side(label: str, rows: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    return {
        side: summarize_entry_rows(label, [row for row in rows if str(row.get("side")) == side])
        for side in sorted({str(row.get("side")) for row in rows})
    }


def model_summary(model: dict[str, Any] | None) -> dict[str, Any]:
    if model is None:
        return {"available": False}
    docs_win = int(model.get("docs_win", 0))
    docs_loss = int(model.get("docs_loss", 0))
    return {
        "available": True,
        "docs": docs_win + docs_loss,
        "docs_win": docs_win,
        "docs_loss": docs_loss,
        "tokens": int(model.get("total_win", 0)) + int(model.get("total_loss", 0)),
        "vocab": len(model.get("vocab", [])),
    }


def run_strategy(
    prepped: list[tuple[dict[str, Any], dict[str, Any]]],
    strategy: StrategySpec,
    *,
    model_prepped: list[tuple[dict[str, Any], dict[str, Any]]] | None = None,
    online_model: bool = False,
) -> dict[str, Any]:
    sid = strategy_id(strategy.family, strategy.params)
    ordered = sorted(prepped, key=lambda item: (item[0]["entry_ts"], item[0]["market"], item[0]["side"]))
    rows: list[dict[str, Any]] = []
    model: dict[str, Any] | None = None
    if strategy.model_builder is not None:
        if online_model:
            model = empty_token_model()
        else:
            model = strategy.model_builder(model_prepped or prepped, strategy.params)
    for case, prepared in ordered:
        pnl, meta = strategy.simulator(case, prepared, strategy.params, model)
        rows.append(row_for(case, pnl, meta, sid))
        if online_model and model is not None and strategy.model_updater is not None:
            strategy.model_updater(model, case, prepared, strategy.params)
    return {
        "strategy_id": sid,
        "family": strategy.family,
        "theorem": strategy.theorem,
        "equation": strategy.equation,
        "params": strategy.params,
        "summary": summarize_entry_rows(sid, rows),
        "by_dataset": summarize_by_dataset(sid, rows),
        "by_side": summarize_by_side(sid, rows),
        "model_summary": model_summary(model),
        "interesting_examples": sorted(rows, key=lambda row: (float(row["sim_pnl"]), row["market"]))[:10],
    }


def select_family_best(results: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    best: dict[str, dict[str, Any]] = {}
    for result in results:
        family = result["family"]
        summary = result["summary"]
        key = (summary["sim_pnl"], summary["entries"], summary["entry_win_rate"])
        if family not in best:
            best[family] = result
            continue
        old = best[family]["summary"]
        old_key = (old["sim_pnl"], old["entries"], old["entry_win_rate"])
        if key > old_key:
            best[family] = result
    return best


def walk_forward_summary(
    prepped: list[tuple[dict[str, Any], dict[str, Any]]],
    strategies: list[StrategySpec],
) -> dict[str, Any]:
    ordered = sorted(prepped, key=lambda item: (item[0]["entry_ts"], item[0]["market"], item[0]["side"]))
    split = int(len(ordered) * 0.7)
    train = ordered[:split]
    holdout = ordered[split:]
    by_family: dict[str, list[StrategySpec]] = {}
    for strategy in strategies:
        by_family.setdefault(strategy.family, []).append(strategy)
    output: dict[str, Any] = {
        "train_n": len(train),
        "holdout_n": len(holdout),
        "split_entry_ts": ordered[split][0]["entry_ts"] if holdout else None,
        "selection_basis": "Max train sim PnL; model families use prior-only online train scoring and fixed train-only holdout scoring.",
        "families": {},
    }
    for family, family_strategies in by_family.items():
        train_results = [
            run_strategy(train, strategy, model_prepped=train, online_model=bool(strategy.model_builder))
            for strategy in family_strategies
        ]
        selected_train = max(train_results, key=lambda result: result["summary"]["sim_pnl"])
        selected_spec = next(
            strategy
            for strategy in family_strategies
            if strategy_id(strategy.family, strategy.params) == selected_train["strategy_id"]
        )
        holdout_result = run_strategy(holdout, selected_spec, model_prepped=train, online_model=False)
        output["families"][family] = {
            "selected_strategy_id": selected_train["strategy_id"],
            "selected_params": selected_train["params"],
            "train_summary": selected_train["summary"],
            "holdout_summary": holdout_result["summary"],
            "holdout_by_dataset": holdout_result["by_dataset"],
            "holdout_by_side": holdout_result["by_side"],
            "holdout_model_summary": holdout_result["model_summary"],
        }
    return output


def robust_positive_scan(
    strategies: list[StrategySpec],
    prepped: list[tuple[dict[str, Any], dict[str, Any]]],
) -> dict[str, list[dict[str, Any]]]:
    ordered = sorted(prepped, key=lambda item: (item[0]["entry_ts"], item[0]["market"], item[0]["side"]))
    split = int(len(ordered) * 0.7)
    train = ordered[:split]
    holdout = ordered[split:]
    output: dict[str, list[dict[str, Any]]] = {}
    for family in sorted({strategy.family for strategy in strategies}):
        rows: list[dict[str, Any]] = []
        for strategy in [item for item in strategies if item.family == family]:
            train_result = run_strategy(train, strategy, model_prepped=train, online_model=bool(strategy.model_builder))
            holdout_result = run_strategy(holdout, strategy, model_prepped=train, online_model=False)
            train_pnl = train_result["summary"]["sim_pnl"]
            holdout_pnl = holdout_result["summary"]["sim_pnl"]
            if train_pnl <= 0 or holdout_pnl <= 0:
                continue
            rows.append(
                {
                    "strategy_id": train_result["strategy_id"],
                    "params": train_result["params"],
                    "train_sim_pnl": train_pnl,
                    "holdout_sim_pnl": holdout_pnl,
                    "min_split_pnl": min(train_pnl, holdout_pnl),
                    "holdout_entries": holdout_result["summary"]["entries"],
                    "holdout_entry_win_rate": holdout_result["summary"]["entry_win_rate"],
                }
            )
        output[family] = sorted(rows, key=lambda row: (row["min_split_pnl"], row["holdout_sim_pnl"]), reverse=True)[:10]
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
                "delta_vs_no_trade_all": result["summary"]["delta_vs_no_trade_all"],
                "entries": result["summary"]["entries"],
                "entry_win_rate": result["summary"]["entry_win_rate"],
                "skipped_winners": result["summary"]["skipped_settlement_winners"],
                "skipped_losers": result["summary"]["skipped_settlement_losers"],
            }
            for result in ranked[:12]
        ]
    return output


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
        "# Codex Entry Sequence/Likelihood Edge Research",
        "",
        f"- Generated: `{payload['generated_at']}`",
        f"- Datasets: `{', '.join(payload['datasets'])}`",
        f"- Quote-path cases: `{payload['case_count']}`",
        "- Scope: research-only entry/no-trade simulation; live bot logic, configs, run scripts, and processes were not changed.",
        "- Non-repetition: this tests quote-token likelihood ratios, semivariance asymmetry, and book-slack elasticity, not prior neighbor LCB, Bayesian-cell, BTC synthetic EV, Haar energy, record-age, pressure impulse, or delayed-entry threshold families.",
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
            "- The token-likelihood family is causal in full-sample scoring: each full replay decision sees only prior cases, and the holdout uses a fixed train-only model.",
            "- Semivariance asks whether quote-path upside energy dominates downside energy before entry.",
            "- Slack elasticity asks whether lower entry prices are real discounts or artifacts of a loose two-sided book.",
            "- Treat positive results as research candidates only; live entry, exit, config, and process state were not touched.",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Research-only sequence likelihood and slack-elasticity entry probes.")
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
    results = [run_strategy(prepped, strategy, online_model=bool(strategy.model_builder)) for strategy in strategies]
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
    json_path = EDGE_DIR / f"codex_entry_sequence_likelihood_research_{stamp}.json"
    md_path = EDGE_DIR / f"codex_entry_sequence_likelihood_research_{stamp}.md"
    latest_json = EDGE_DIR / "codex_entry_sequence_likelihood_research_latest.json"
    latest_md = EDGE_DIR / "codex_entry_sequence_likelihood_research_latest.md"
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
            "online_quote_token_likelihood_admission": "held ask, own/opposite bids, spread, bid_sum, and prior settled path prefixes through the configured delay",
            "quote_semivariance_asymmetry_admission": "held ask increments and book snapshot through the configured delay",
            "book_slack_elasticity_discount_admission": "held ask, bid_sum-derived slack, pressure, and spread through the configured delay",
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
