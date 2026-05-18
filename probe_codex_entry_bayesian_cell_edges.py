from __future__ import annotations

import argparse
import json
import math
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

from probe_codex_entry_conformal_neighbor_edges import feature_row, load_cases, risk_summary, slim_result
from probe_codex_entry_timing_edges import delayed_entry_pnl
from probe_stop_touch_confirmation import append_ledger, idea_key, result_distance, strategy_id, update_strategy_memory
from validate_btc_spot_synthetic_ev_broad import (
    EDGE_DIR,
    baseline_payload,
    load_or_fetch_candles,
    prepare_case,
    safe_float,
    summarize_by_group,
    summarize_entry_rows,
)


UTC = timezone.utc


@dataclass(frozen=True)
class StrategySpec:
    family: str
    theorem: str
    equation: str
    params: dict[str, Any]


def parse_utc(value: str) -> datetime:
    parsed = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=UTC)
    return parsed.astimezone(UTC)


def bucket(value: float, cuts: tuple[float, ...]) -> int:
    if math.isnan(value):
        return -1
    for idx, cut in enumerate(cuts):
        if value <= cut:
            return idx
    return len(cuts)


def side_part(row: dict[str, Any], params: dict[str, Any]) -> str:
    if params.get("side_mode") == "pooled":
        return "both"
    return str(row["case"].get("side") or "unknown").lower()


def cell_keys(row: dict[str, Any], params: dict[str, Any]) -> tuple[tuple[Any, ...], tuple[Any, ...]]:
    side = side_part(row, params)
    ev = bucket(safe_float(row.get("ev_cents")), (-2.0, 0.0, 2.0, 5.0, 8.0, 12.0))
    ask = bucket(safe_float(row.get("ask")), (78.0, 82.0, 85.0, 88.0, 90.0))
    pressure = bucket(safe_float(row.get("pressure")), (0.03, 0.08, 0.15, 0.25, 0.35))
    spread = bucket(safe_float(row.get("spread")), (1.0, 2.0, 3.0, 4.0))
    move = bucket(safe_float(row.get("move_score")), (-0.75, -0.25, 0.25, 0.75, 1.25))
    location = bucket(safe_float(row.get("location_score")), (-0.75, -0.25, 0.25, 0.75, 1.25))
    btc_range = bucket(safe_float(row.get("btc_range")), (20.0, 35.0, 55.0, 80.0, 120.0))
    quality = bucket(safe_float(row.get("quality_share")), (0.25, 0.50, 0.75, 0.90))
    shape = str(params["cell_shape"])
    if shape == "compact":
        return (side, ev, ask, pressure, move), (side, ev, move)
    if shape == "quote_pressure":
        return (side, ev, ask, pressure, spread, quality), (side, ev, pressure)
    if shape == "btc_shape":
        return (side, ev, move, location, btc_range), (side, ev, move)
    raise ValueError(f"unknown cell_shape={shape}")


def wilson_lower(successes: float, trials: float, z: float) -> float:
    if trials <= 0.0:
        return 0.0
    p = successes / trials
    denom = 1.0 + z * z / trials
    center = p + z * z / (2.0 * trials)
    spread = z * math.sqrt(max(0.0, p * (1.0 - p) / trials + z * z / (4.0 * trials * trials)))
    return max(0.0, min(1.0, (center - spread) / denom))


def posterior_stats(
    row: dict[str, Any],
    global_counts: dict[str, float],
    parent_counts: dict[tuple[Any, ...], dict[str, float]],
    cell_counts: dict[tuple[Any, ...], dict[str, float]],
    params: dict[str, Any],
) -> dict[str, Any] | None:
    cell, parent = cell_keys(row, params)
    global_n = float(global_counts.get("n", 0.0))
    if global_n < float(params["min_global_count"]):
        return None
    parent_count = parent_counts.get(parent, {"n": 0.0, "wins": 0.0})
    cell_count = cell_counts.get(cell, {"n": 0.0, "wins": 0.0})
    parent_n = float(parent_count["n"])
    cell_n = float(cell_count["n"])
    if parent_n < float(params["min_parent_count"]):
        return None

    global_p = (float(global_counts["wins"]) + 1.0) / (global_n + 2.0)
    parent_strength = float(params["parent_strength"])
    global_strength = float(params["global_strength"])
    parent_w = float(parent_count["wins"])
    parent_p = (parent_w + global_strength * global_p + 1.0) / (parent_n + global_strength + 2.0)
    if params.get("posterior_scope") == "parent":
        cell_n = parent_n
        alpha = parent_w + global_strength * global_p + 1.0
        beta = (parent_n - parent_w) + global_strength * (1.0 - global_p) + 1.0
    else:
        if cell_n < float(params["min_cell_count"]):
            return None
        cell_w = float(cell_count["wins"])
        alpha = cell_w + parent_strength * parent_p + 1.0
        beta = (cell_n - cell_w) + parent_strength * (1.0 - parent_p) + 1.0
    posterior_n = alpha + beta
    posterior_p = alpha / posterior_n
    p_lcb = wilson_lower(alpha, posterior_n, float(params["lcb_z"]))

    ask = safe_float(row.get("ask"))
    fee = safe_float(row.get("fee_per_contract"))
    if any(math.isnan(value) for value in (ask, fee)):
        return None
    ev_mean = 100.0 * posterior_p - ask - fee
    ev_lcb = 100.0 * p_lcb - ask - fee
    return {
        "cell": cell,
        "parent": parent,
        "global_n": global_n,
        "parent_n": parent_n,
        "cell_n": cell_n,
        "posterior_scope": str(params.get("posterior_scope", "cell")),
        "posterior_p": posterior_p,
        "p_lcb": p_lcb,
        "ev_mean_cents": ev_mean,
        "ev_lcb_cents": ev_lcb,
    }


def update_counts(
    row: dict[str, Any],
    global_counts: dict[str, float],
    parent_counts: dict[tuple[Any, ...], dict[str, float]],
    cell_counts: dict[tuple[Any, ...], dict[str, float]],
    params: dict[str, Any],
) -> None:
    cell, parent = cell_keys(row, params)
    win = 1.0 if bool(row["case"].get("settlement_win")) else 0.0
    global_counts["n"] = global_counts.get("n", 0.0) + 1.0
    global_counts["wins"] = global_counts.get("wins", 0.0) + win
    parent_bucket = parent_counts.setdefault(parent, {"n": 0.0, "wins": 0.0})
    parent_bucket["n"] += 1.0
    parent_bucket["wins"] += win
    cell_bucket = cell_counts.setdefault(cell, {"n": 0.0, "wins": 0.0})
    cell_bucket["n"] += 1.0
    cell_bucket["wins"] += win


def contracts_for_entry(case: dict[str, Any], row: dict[str, Any], stats: dict[str, Any], params: dict[str, Any]) -> int:
    base_qty = max(1, int(case["qty"]))
    if "max_multiplier" not in params:
        return base_qty
    ask = max(1.0, safe_float(row.get("ask")))
    fee = max(0.0, safe_float(row.get("fee_per_contract")))
    win_gain = max(0.01, 100.0 - ask - fee)
    loss = max(0.01, ask + fee)
    odds = win_gain / loss
    p = float(stats["p_lcb"])
    kelly = max(0.0, (p * odds - (1.0 - p)) / max(0.01, odds))
    multiplier = min(float(params["max_multiplier"]), 1.0 + kelly / max(0.01, float(params["kelly_unit"])))
    return min(int(params["max_contracts"]), max(1, int(math.floor(base_qty * multiplier))))


def blank_row(case: dict[str, Any], sid: str, meta: dict[str, Any], pnl: float = 0.0) -> dict[str, Any]:
    entered = bool(meta.get("enter"))
    return {
        "label": sid,
        "dataset": case["dataset"],
        "market": case["market"],
        "side": case.get("side"),
        "entry_day_et": case["entry_day_et"],
        "entry_ts": case["entry_ts"],
        "decision_ts": meta.get("decision_ts"),
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
        "posterior_p": meta.get("posterior_p"),
        "cell_n": meta.get("cell_n"),
        "parent_n": meta.get("parent_n"),
        "ev_mean_cents": meta.get("ev_mean_cents"),
    }


def simulate_rows(prepped: list[tuple[dict[str, Any], dict[str, Any]]], strategy: StrategySpec) -> list[dict[str, Any]]:
    sid = strategy_id(strategy.family, strategy.params)
    params = strategy.params
    pending: list[tuple[datetime, dict[str, Any]]] = []
    global_counts: dict[str, float] = {"n": 0.0, "wins": 0.0}
    parent_counts: dict[tuple[Any, ...], dict[str, float]] = {}
    cell_counts: dict[tuple[Any, ...], dict[str, float]] = {}
    rows: list[dict[str, Any]] = []
    lag = timedelta(minutes=float(params["settlement_lag_minutes"]))
    ordered = sorted(prepped, key=lambda item: (item[0]["entry_ts"], item[0]["market"], item[0]["side"]))

    for case, prepared in ordered:
        row = feature_row(case, prepared, params)
        decision_ts = parse_utc(case["entry_ts"])
        if row is not None:
            decision_ts += timedelta(seconds=float(row["features"]["actual_quote_elapsed"]))
        while pending and pending[0][0] <= decision_ts:
            _known_at, known_row = pending.pop(0)
            update_counts(known_row, global_counts, parent_counts, cell_counts, params)

        if row is None:
            rows.append(blank_row(case, sid, {"enter": False, "skip_reason": "missing_or_gate_failed", "decision_ts": decision_ts.isoformat()}))
            continue
        known_at = parse_utc(case["entry_ts"]) + lag
        insert_at = len(pending)
        while insert_at > 0 and pending[insert_at - 1][0] > known_at:
            insert_at -= 1
        pending.insert(insert_at, (known_at, row))

        if row["ev_cents"] < float(params["min_model_ev_cents"]):
            rows.append(
                blank_row(
                    case,
                    sid,
                    {
                        "enter": False,
                        "skip_reason": "synthetic_ev_too_low",
                        "decision_ts": decision_ts.isoformat(),
                        "score": round(float(row["ev_cents"]), 6),
                    },
                )
            )
            continue
        stats = posterior_stats(row, global_counts, parent_counts, cell_counts, params)
        if stats is None:
            rows.append(
                blank_row(
                    case,
                    sid,
                    {
                        "enter": False,
                        "skip_reason": "insufficient_confirmed_cell_history",
                        "decision_ts": decision_ts.isoformat(),
                        "score": round(float(row["ev_cents"]), 6),
                    },
                )
            )
            continue
        if stats["ev_lcb_cents"] < float(params["min_lcb_ev_cents"]):
            rows.append(
                blank_row(
                    case,
                    sid,
                    {
                        "enter": False,
                        "skip_reason": "posterior_lcb_ev_too_low",
                        "decision_ts": decision_ts.isoformat(),
                        "score": round(float(stats["ev_lcb_cents"]), 6),
                        **{k: round(float(v), 6) for k, v in stats.items() if isinstance(v, (int, float))},
                    },
                )
            )
            continue

        contracts = contracts_for_entry(case, row, stats, params)
        pnl = delayed_entry_pnl(case, float(row["ask"]), contracts=contracts)
        rows.append(
            blank_row(
                case,
                sid,
                {
                    "enter": True,
                    "decision_ts": decision_ts.isoformat(),
                    "entry_ask": round(float(row["ask"]), 4),
                    "entry_elapsed": round(float(row["features"]["actual_quote_elapsed"]), 4),
                    "contracts": contracts,
                    "score": round(float(stats["ev_lcb_cents"]), 6),
                    "posterior_p": round(float(stats["posterior_p"]), 6),
                    "cell_n": round(float(stats["cell_n"]), 2),
                    "parent_n": round(float(stats["parent_n"]), 2),
                    "ev_mean_cents": round(float(stats["ev_mean_cents"]), 6),
                },
                pnl,
            )
        )
    return rows


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
        "interesting_examples": sorted(entered, key=lambda item: float(item["sim_pnl"]))[:10],
        "_rows": rows,
    }


def build_strategy_grid() -> list[StrategySpec]:
    admission_theorem = (
        "A delayed BTC spot EV signal should be traded only when a settlement-confirmed empirical-Bayes feature cell "
        "has a positive lower-bound terminal EV at the current ask."
    )
    admission_equation = (
        "For cell c(x) and parent p(x), update only prior cases older than lag L. "
        "p_g=(W_g+1)/(N_g+2); p_p=(W_p+s_g*p_g+1)/(N_p+s_g+2); "
        "p_c=(W_c+s_p*p_p+1)/(N_c+s_p+2); EV_L=100*WilsonLCB(p_c,N_c+s_p+2,z)-ask-fee. "
        "Enter only if modelEV>=m and EV_L>=e."
    )
    sizing_theorem = (
        "If the lower-bound cell posterior is positive, position size can be linked to conservative Kelly fraction "
        "rather than fixed historical size."
    )
    sizing_equation = (
        "Use the empirical-Bayes admission rule, then contracts=min(Cmax,floor(qty*min(Mmax,1+Kelly_LCB/u)))."
    )
    parent_theorem = (
        "Fine feature cells may be too sparse for 15-minute markets; a coarser parent posterior can test whether "
        "the same settlement-confirmed Bayesian signal has breadth before adding cell specificity."
    )
    parent_equation = (
        "For parent p(x), update only prior cases older than lag L. "
        "p_g=(W_g+1)/(N_g+2); p_p=(W_p+s_g*p_g+1)/(N_p+s_g+2); "
        "EV_L=100*WilsonLCB(p_p,N_p+s_g+2,z)-ask-fee. Enter only if modelEV>=m and EV_L>=e."
    )
    strategies: list[StrategySpec] = []
    base = {
        "max_opp_pressure": 0.30,
        "min_bid_sum": 0,
        "max_spread": 4,
        "global_strength": 12.0,
        "settlement_lag_minutes": 20,
        "min_global_count": 60,
    }
    for delay_seconds in (90, 120, 150):
        for max_entry_ask in (88, 90):
            for min_model_ev_cents in (0.0, 2.0):
                for side_mode in ("pooled", "side_specific"):
                    for cell_shape in ("compact", "quote_pressure", "btc_shape"):
                        for min_cell_count in (3, 5, 8):
                            for min_parent_count in (20, 40):
                                for parent_strength in (6.0, 12.0):
                                    for lcb_z in (0.5, 1.0, 1.5):
                                        for min_lcb_ev_cents in (0.0, 2.0):
                                            params = {
                                                **base,
                                                "delay_seconds": delay_seconds,
                                                "max_entry_ask": max_entry_ask,
                                                "min_model_ev_cents": min_model_ev_cents,
                                                "side_mode": side_mode,
                                                "cell_shape": cell_shape,
                                                "min_cell_count": min_cell_count,
                                                "min_parent_count": min_parent_count,
                                                "parent_strength": parent_strength,
                                                "lcb_z": lcb_z,
                                                "min_lcb_ev_cents": min_lcb_ev_cents,
                                            }
                                            strategies.append(
                                                StrategySpec(
                                                    "online_bayes_cell_ev_admission",
                                                    admission_theorem,
                                                    admission_equation,
                                                    params,
                                                )
                                            )
                                            if min_cell_count == 3 and parent_strength == 6.0:
                                                parent_params = {
                                                    **params,
                                                    "posterior_scope": "parent",
                                                }
                                                strategies.append(
                                                    StrategySpec(
                                                        "online_bayes_parent_ev_admission",
                                                        parent_theorem,
                                                        parent_equation,
                                                        parent_params,
                                                    )
                                                )
                                            if (
                                                delay_seconds == 120
                                                and min_cell_count in (3, 5)
                                                and parent_strength == 6.0
                                                and lcb_z in (0.5, 1.0)
                                            ):
                                                strategies.append(
                                                    StrategySpec(
                                                        "online_bayes_cell_kelly_sizer",
                                                        sizing_theorem,
                                                        sizing_equation,
                                                        {
                                                            **params,
                                                            "posterior_scope": "cell",
                                                            "max_multiplier": 2.0,
                                                            "max_contracts": 20,
                                                            "kelly_unit": 0.08,
                                                        },
                                                    )
                                                )
                                                parent_sizer_params = {
                                                    **params,
                                                    "posterior_scope": "parent",
                                                    "max_multiplier": 2.0,
                                                    "max_contracts": 20,
                                                    "kelly_unit": 0.08,
                                                }
                                                strategies.append(
                                                    StrategySpec(
                                                        "online_bayes_parent_kelly_sizer",
                                                        sizing_theorem,
                                                        sizing_equation,
                                                        parent_sizer_params,
                                                    )
                                                )
    return strategies


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
                -abs(result["risk"]["max_drawdown"]),
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
        "selection_basis": "Max train simulated PnL per family among variants with at least 15 train entries; online counts use only settlement-lagged prior cases.",
        "families": {},
    }
    for family in sorted({result["family"] for result in results}):
        train_scored = []
        for result in [item for item in results if item["family"] == family]:
            train_rows = result["_rows"][:split]
            train_summary = summarize_entry_rows(result["strategy_id"], train_rows)
            train_scored.append((result, train_summary))
        eligible = [item for item in train_scored if item[1]["entries"] >= 15] or train_scored
        selected, train_summary = max(
            eligible,
            key=lambda item: (
                item[1]["sim_pnl"],
                item[1]["entry_win_rate"],
                -abs(item[0]["risk"]["max_drawdown"]),
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
                "loss_count": result["risk"]["loss_count"],
            }
            for result in ranked[:12]
        ]
    return output


def status_for_result(result: dict[str, Any], wf: dict[str, Any], robust_rows: list[dict[str, Any]]) -> str:
    holdout = wf.get("families", {}).get(result["family"], {}).get("holdout_summary", {})
    if result["summary"]["entries"] < 20 or holdout.get("entries", 0) < 5:
        return "tested_too_sparse"
    positive_neighbors = sum(1 for row in robust_rows if row["sim_pnl"] > 0 and row["entries"] >= 10)
    if (
        result["summary"]["delta_vs_actual"] > 0
        and result["summary"]["delta_vs_no_stop"] > 0
        and holdout.get("sim_pnl", -1.0) > 0
        and result["summary"]["entries"] >= 20
        and positive_neighbors >= 5
    ):
        return "candidate_for_human_review"
    if result["summary"]["delta_vs_no_trade_all"] > 0 and holdout.get("sim_pnl", -1.0) > 0:
        return "watchlist_positive_holdout"
    if result["summary"]["delta_vs_no_trade_all"] > 0:
        return "watchlist_positive_but_not_robust"
    return "tested_negative"


def write_markdown(path: Path, payload: dict[str, Any]) -> None:
    base = payload["baselines"]
    lines = [
        "# Codex Entry Bayesian Cell Research",
        "",
        f"- Generated: `{payload['generated_at']}`",
        f"- Cases: `{payload['case_count']}` across `{', '.join(payload['datasets'])}`",
        f"- Variants tested: `{payload['variant_count']}`",
        "- Scope: research-only; live entry/exit logic, configs, run scripts, and bot processes were not changed.",
        "- History discipline: empirical counts only include prior rows after the configured settlement lag.",
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
        "- `online_bayes_cell_ev_admission`: hierarchical empirical-Bayes settlement posterior over discrete decision-time cells, converted into a Wilson lower-bound EV at the current ask.",
        "- `online_bayes_cell_kelly_sizer`: same admission rule, then contracts are clipped by a conservative Kelly fraction from the lower-bound posterior.",
        "- `online_bayes_parent_ev_admission`: coarser parent-cell posterior to test breadth when fine cells are too sparse.",
        "- `online_bayes_parent_kelly_sizer`: parent posterior plus the same clipped conservative Kelly sizing.",
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
    lines.extend(["## Sensitivity Near Best", ""])
    for family, rows in payload["sensitivity"].items():
        lines.append(f"### {family}")
        lines.append("")
        lines.append("| PnL | Entries | Win rate | Losses | Max DD | Params |")
        lines.append("|---:|---:|---:|---:|---:|---|")
        for row in rows[:8]:
            lines.append(
                f"| {row['sim_pnl']} | {row['entries']} | {row['win_rate']} | {row['loss_count']} | {row['max_drawdown']} | `{json.dumps(row['params'], sort_keys=True)}` |"
            )
        lines.append("")
    lines.extend(
        [
            "## Interpretation",
            "",
            "- This is not the prior nearest-neighbor LCB candidate: it compresses states into auditable feature cells and uses hierarchical shrinkage plus Wilson lower bounds.",
            "- The settlement-lagged history makes it more conservative than the previous chronological-history proxy, but it still needs human review before any live discussion.",
            "- If continued, compare the selected cells against live-fill availability and inspect whether the active cells are economically broad or just a few market-time pockets.",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Research-only empirical-Bayes cell entry tests.")
    parser.add_argument("--datasets", nargs="*", default=None)
    parser.add_argument("--refresh-btc-cache", action="store_true")
    args = parser.parse_args()

    cases, _payloads = load_cases(args.datasets)
    candles = load_or_fetch_candles(cases, refresh_cache=args.refresh_btc_cache)
    strategies = build_strategy_grid()
    delays = tuple(sorted({int(strategy.params["delay_seconds"]) for strategy in strategies}))
    prepped = [(case, prepare_case(case, candles, delays)) for case in cases]
    results = [run_strategy(prepped, strategy) for strategy in strategies]
    best_raw = select_family_best(results)
    wf = walk_forward_summary(results)
    sens = sensitivity(results, best_raw)

    stamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
    generated_at = datetime.now(UTC).isoformat()
    json_path = EDGE_DIR / f"codex_entry_bayesian_cell_research_{stamp}.json"
    md_path = EDGE_DIR / f"codex_entry_bayesian_cell_research_{stamp}.md"
    latest_json = EDGE_DIR / "codex_entry_bayesian_cell_research_latest.json"
    latest_md = EDGE_DIR / "codex_entry_bayesian_cell_research_latest.md"

    best_by_family = {
        family: {
            **slim_result(result),
            "status": status_for_result(result, wf, sens.get(family, [])),
        }
        for family, result in best_raw.items()
    }
    top_results = sorted(
        (slim_result(result) for result in results),
        key=lambda result: (result["summary"]["sim_pnl"], result["summary"]["entry_win_rate"]),
        reverse=True,
    )[:60]
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
            "new_family": "settlement-lagged hierarchical empirical-Bayes feature-cell posterior",
            "not_retesting": [
                "online nearest-neighbor LCB over continuous feature distance",
                "fixed BTC spot synthetic EV threshold",
                "raw EV score-scaled sizing",
                "path-geometry filters",
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
