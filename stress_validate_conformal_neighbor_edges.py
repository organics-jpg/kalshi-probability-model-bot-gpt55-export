from __future__ import annotations

import argparse
import json
import math
import random
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd

from probe_codex_entry_conformal_neighbor_edges import (
    StrategySpec,
    build_strategy_grid,
    contracts_for_entry,
    feature_row,
    load_cases,
    neighbor_stats,
    risk_summary,
)
from probe_codex_entry_timing_edges import delayed_entry_pnl
from probe_stop_touch_confirmation import append_ledger, idea_key, strategy_id, update_strategy_memory
from validate_btc_spot_synthetic_ev_broad import (
    EDGE_DIR,
    baseline_payload,
    load_or_fetch_candles,
    mean,
    prepare_case,
    safe_float,
    summarize_by_group,
    summarize_entry_rows,
)


ROOT = Path(__file__).resolve().parent
UTC = timezone.utc


def case_key(case: dict[str, Any]) -> str:
    return "|".join(str(case.get(key, "")) for key in ("dataset", "market", "side", "entry_ts"))


def load_settlement_times(datasets: list[str]) -> dict[tuple[str, str], pd.Timestamp]:
    settlement: dict[tuple[str, str], pd.Timestamp] = {}
    for dataset in datasets:
        path = ROOT / "stats" / dataset / "market_results.csv"
        if not path.exists():
            continue
        frame = pd.read_csv(path)
        if "market" not in frame.columns:
            continue
        for _, row in frame.iterrows():
            market = str(row.get("market") or "")
            if not market or market.lower() == "none":
                continue
            ts = pd.to_datetime(row.get("settlement_ts"), utc=True, errors="coerce")
            if pd.isna(ts):
                ts = pd.to_datetime(row.get("close_time"), utc=True, errors="coerce")
            if not pd.isna(ts):
                settlement[(dataset, market)] = pd.Timestamp(ts)
    return settlement


def enrich_settlement_times(cases: list[dict[str, Any]]) -> dict[str, Any]:
    datasets = sorted({str(case["dataset"]) for case in cases})
    settlement = load_settlement_times(datasets)
    missing = 0
    for case in cases:
        entry_ts = pd.Timestamp(case["entry_ts"])
        if entry_ts.tzinfo is None:
            entry_ts = entry_ts.tz_localize("UTC")
        else:
            entry_ts = entry_ts.tz_convert("UTC")
        settled = settlement.get((str(case["dataset"]), str(case["market"])))
        if settled is None or pd.isna(settled):
            missing += 1
            settled = entry_ts + pd.Timedelta(minutes=15)
        case["settlement_ts"] = pd.Timestamp(settled).isoformat()
    return {"datasets": datasets, "settlement_missing_fallback_count": missing}


def decision_ts_for(case: dict[str, Any], row: dict[str, Any] | None, params: dict[str, Any]) -> pd.Timestamp:
    entry_ts = pd.Timestamp(case["entry_ts"])
    if entry_ts.tzinfo is None:
        entry_ts = entry_ts.tz_localize("UTC")
    else:
        entry_ts = entry_ts.tz_convert("UTC")
    elapsed = safe_float((row or {}).get("features", {}).get("actual_quote_elapsed"))
    if math.isnan(elapsed):
        elapsed = float(params["delay_seconds"])
    return entry_ts + pd.Timedelta(seconds=elapsed)


def settlement_ts_for(case: dict[str, Any]) -> pd.Timestamp:
    ts = pd.Timestamp(case["settlement_ts"])
    if ts.tzinfo is None:
        return ts.tz_localize("UTC")
    return ts.tz_convert("UTC")


def row_with_times(case: dict[str, Any], prepared: dict[str, Any], params: dict[str, Any]) -> dict[str, Any] | None:
    row = feature_row(case, prepared, params)
    if row is None:
        return None
    row["key"] = case_key(case)
    row["dataset"] = str(case["dataset"])
    row["market"] = str(case["market"])
    row["side"] = str(case.get("side") or "")
    row["decision_ts"] = decision_ts_for(case, row, params)
    row["settlement_ts"] = settlement_ts_for(case)
    row["true_outcome_cents"] = float(row["outcome_cents"])
    return row


def filter_history(history: list[dict[str, Any]], current: dict[str, Any], scope: str) -> list[dict[str, Any]]:
    if scope == "all":
        return history
    if scope == "same_dataset":
        return [row for row in history if row["dataset"] == current["dataset"]]
    if scope == "cross_dataset":
        return [row for row in history if row["dataset"] != current["dataset"]]
    if scope == "no_live_90_70":
        return [row for row in history if row["dataset"] != "live_90_70"]
    if scope == "live_90_70_only":
        return [row for row in history if row["dataset"] == "live_90_70"]
    raise ValueError(f"unknown history scope: {scope}")


def output_row(
    case: dict[str, Any],
    sid: str,
    pnl: float,
    meta: dict[str, Any],
) -> dict[str, Any]:
    entered = bool(meta.get("enter"))
    return {
        "label": sid,
        "dataset": case["dataset"],
        "market": case["market"],
        "side": case.get("side"),
        "entry_day_et": case["entry_day_et"],
        "entry_ts": case["entry_ts"],
        "settlement_ts": case.get("settlement_ts"),
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
        "model_ev_cents": meta.get("model_ev_cents"),
        "neighbor_mu_cents": meta.get("neighbor_mu_cents"),
        "neighbor_cvar20_cents": meta.get("neighbor_cvar20_cents"),
        "neighbor_win_rate": meta.get("neighbor_win_rate"),
        "neighbor_avg_distance": meta.get("neighbor_avg_distance"),
        "history_available": meta.get("history_available"),
    }


def simulate_strategy(
    prepped: list[tuple[dict[str, Any], dict[str, Any]]],
    strategy: StrategySpec,
    *,
    history_mode: str,
    history_scope: str = "all",
    slippage_cents: float = 0.0,
    extra_fee_cents_per_contract: float = 0.0,
    current_datasets: set[str] | None = None,
    outcome_override: dict[str, float] | None = None,
    row_cache: dict[str, dict[str, Any] | None] | None = None,
) -> list[dict[str, Any]]:
    if history_mode not in {"entry_proxy", "settlement_available"}:
        raise ValueError(f"unknown history mode: {history_mode}")
    sid = strategy_id(strategy.family, strategy.params)
    ordered: list[tuple[pd.Timestamp, dict[str, Any], dict[str, Any], dict[str, Any] | None]] = []
    for case, prepared in prepped:
        row = row_cache.get(case_key(case)) if row_cache is not None else row_with_times(case, prepared, strategy.params)
        ordered.append((decision_ts_for(case, row, strategy.params), case, prepared, row))
    ordered.sort(key=lambda item: (item[0], item[1]["market"], item[1]["side"]))

    entry_history: list[dict[str, Any]] = []
    settled_history: list[dict[str, Any]] = []
    pending_history: list[dict[str, Any]] = []
    rows: list[dict[str, Any]] = []

    for decision_ts, case, _, row in ordered:
        if history_mode == "settlement_available":
            ready = [prior for prior in pending_history if prior["settlement_ts"] <= decision_ts]
            if ready:
                settled_history.extend(ready)
                ready_keys = {prior["key"] for prior in ready}
                pending_history = [prior for prior in pending_history if prior["key"] not in ready_keys]

        should_output = current_datasets is None or str(case["dataset"]) in current_datasets
        pnl = 0.0
        meta: dict[str, Any] = {"enter": False, "skip_reason": "not_in_current_dataset_filter"}
        if row is None:
            meta = {"enter": False, "skip_reason": "missing_or_gate_failed"}
        elif row["ev_cents"] < float(strategy.params["min_model_ev_cents"]):
            meta = {
                "enter": False,
                "skip_reason": "synthetic_ev_too_low",
                "score": round(float(row["ev_cents"]), 6),
            }
        else:
            base_history = entry_history if history_mode == "entry_proxy" else settled_history
            scoped_history = filter_history(base_history, row, history_scope)
            stats = neighbor_stats(row, scoped_history, strategy.params)
            if stats is None:
                meta = {
                    "enter": False,
                    "skip_reason": "insufficient_or_distant_neighbors",
                    "score": round(float(row["ev_cents"]), 6),
                    "history_available": len(scoped_history),
                }
            elif stats["neighbor_lcb_cents"] < float(strategy.params["min_lcb_cents"]):
                meta = {
                    "enter": False,
                    "skip_reason": "neighbor_lcb_too_low",
                    "score": round(float(stats["neighbor_lcb_cents"]), 6),
                    "history_available": len(scoped_history),
                    **{key: round(float(value), 6) for key, value in stats.items()},
                }
            elif stats["neighbor_win_rate"] < float(strategy.params["min_neighbor_win_rate"]):
                meta = {
                    "enter": False,
                    "skip_reason": "neighbor_win_rate_too_low",
                    "score": round(float(stats["neighbor_lcb_cents"]), 6),
                    "history_available": len(scoped_history),
                    **{key: round(float(value), 6) for key, value in stats.items()},
                }
            else:
                contracts = contracts_for_entry(case, stats, strategy.params)
                ask = min(99.0, float(row["ask"]) + float(slippage_cents))
                pnl = delayed_entry_pnl(case, ask, contracts=contracts)
                pnl = round(pnl - contracts * float(extra_fee_cents_per_contract) / 100.0, 4)
                meta = {
                    "enter": True,
                    "entry_ask": round(ask, 4),
                    "entry_elapsed": round(float(row["features"]["actual_quote_elapsed"]), 4),
                    "contracts": contracts,
                    "score": round(float(stats["neighbor_lcb_cents"]), 6),
                    "model_ev_cents": round(float(row["ev_cents"]), 6),
                    "history_available": len(scoped_history),
                    **{key: round(float(value), 6) for key, value in stats.items()},
                }

        if should_output:
            rows.append(output_row(case, sid, pnl, meta))

        if row is not None and row["ev_cents"] >= float(strategy.params["pool_min_ev_cents"]):
            history_row = dict(row)
            if outcome_override and history_row["key"] in outcome_override:
                history_row["outcome_cents"] = float(outcome_override[history_row["key"]])
            if history_mode == "entry_proxy":
                entry_history.append(history_row)
            else:
                pending_history.append(history_row)

    return rows


def summarize_run(label: str, rows: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "label": label,
        "summary": summarize_entry_rows(label, rows),
        "risk": risk_summary(rows),
        "by_dataset": summarize_by_group(label, rows, "dataset"),
        "by_side": summarize_by_group(label, rows, "side"),
    }


def load_selected_strategies() -> dict[str, StrategySpec]:
    latest = EDGE_DIR / "codex_entry_conformal_neighbor_research_latest.json"
    payload = json.loads(latest.read_text(encoding="utf-8"))
    selected: dict[str, StrategySpec] = {}
    for family, result in payload["best_by_family"].items():
        selected[family] = StrategySpec(family, result["theorem"], result["equation"], result["params"])
    return selected


def build_row_cache(
    prepped: list[tuple[dict[str, Any], dict[str, Any]]], params: dict[str, Any]
) -> dict[str, dict[str, Any] | None]:
    return {case_key(case): row_with_times(case, prepared, params) for case, prepared in prepped}


def shuffled_outcomes(row_cache: dict[str, dict[str, Any] | None], seed: int) -> dict[str, float]:
    items = [(key, row) for key, row in row_cache.items() if row is not None]
    outcomes = [float(row["true_outcome_cents"]) for _, row in items if row is not None]
    rng = random.Random(seed)
    rng.shuffle(outcomes)
    return {key: outcomes[idx] for idx, (key, _) in enumerate(items)}


def selected_stress_suite(
    prepped: list[tuple[dict[str, Any], dict[str, Any]]], selected: dict[str, StrategySpec]
) -> tuple[list[dict[str, Any]], dict[str, dict[str, Any] | None]]:
    scenario_rows: list[dict[str, Any]] = []
    row_caches = {family: build_row_cache(prepped, strategy.params) for family, strategy in selected.items()}
    scenarios = [
        {"name": "entry_proxy_all", "history_mode": "entry_proxy", "history_scope": "all"},
        {"name": "settlement_available_all", "history_mode": "settlement_available", "history_scope": "all"},
        {"name": "settlement_same_dataset", "history_mode": "settlement_available", "history_scope": "same_dataset"},
        {"name": "settlement_cross_dataset", "history_mode": "settlement_available", "history_scope": "cross_dataset"},
        {"name": "settlement_no_live_90_70_history", "history_mode": "settlement_available", "history_scope": "no_live_90_70"},
        {
            "name": "settlement_live_90_70_history_only",
            "history_mode": "settlement_available",
            "history_scope": "live_90_70_only",
        },
        {
            "name": "settlement_live_90_70_current_only",
            "history_mode": "settlement_available",
            "history_scope": "all",
            "current_datasets": {"live_90_70"},
        },
        {
            "name": "settlement_non_live_90_70_current_only",
            "history_mode": "settlement_available",
            "history_scope": "all",
            "current_datasets": {"entry_90_stop_78", "live_87_77_67", "live_90_78"},
        },
    ]
    for slippage in (1.0, 2.0, 3.0, 5.0, 10.0):
        scenarios.append(
            {
                "name": f"settlement_available_slippage_{int(slippage)}c",
                "history_mode": "settlement_available",
                "history_scope": "all",
                "slippage_cents": slippage,
            }
        )
    for family, strategy in selected.items():
        for scenario in scenarios:
            rows = simulate_strategy(
                prepped,
                strategy,
                history_mode=scenario["history_mode"],
                history_scope=scenario.get("history_scope", "all"),
                slippage_cents=float(scenario.get("slippage_cents", 0.0)),
                current_datasets=scenario.get("current_datasets"),
                row_cache=row_caches[family],
            )
            summary = summarize_run(f"{family}:{scenario['name']}", rows)
            scenario_rows.append(
                {
                    "family": family,
                    "strategy_id": strategy_id(strategy.family, strategy.params),
                    "scenario": scenario["name"],
                    "history_mode": scenario["history_mode"],
                    "history_scope": scenario.get("history_scope", "all"),
                    "slippage_cents": float(scenario.get("slippage_cents", 0.0)),
                    **summary["summary"],
                    "max_drawdown": summary["risk"]["max_drawdown"],
                    "loss_count": summary["risk"]["loss_count"],
                    "negative_active_days": summary["risk"]["negative_active_days"],
                    "by_dataset": summary["by_dataset"],
                    "by_side": summary["by_side"],
                }
            )
    return scenario_rows, row_caches


def settlement_grid(prepped: list[tuple[dict[str, Any], dict[str, Any]]], selected: dict[str, StrategySpec]) -> list[dict[str, Any]]:
    # Keep this grid broad around the candidate, but bounded enough to run hourly.
    base_by_family = {family: strategy.params for family, strategy in selected.items()}
    theorem_by_family = {family: strategy.theorem for family, strategy in selected.items()}
    equation_by_family = {family: strategy.equation for family, strategy in selected.items()}
    specs: list[StrategySpec] = []
    for family in ("online_neighbor_lcb_admission", "online_neighbor_lcb_sizer"):
        base = base_by_family[family]
        for delay in (120, 150):
            for max_entry_ask in (88, 90):
                for min_model_ev in (2.0, 4.0):
                    for k in (25, 45):
                        for min_history in (80, 120):
                            for lcb_z in (0.5, 1.0, 1.5):
                                for min_lcb in (0.0, 1.0):
                                    for min_win in (0.78, 0.85):
                                        params = {
                                            **base,
                                            "delay_seconds": delay,
                                            "max_entry_ask": max_entry_ask,
                                            "min_model_ev_cents": min_model_ev,
                                            "k": k,
                                            "min_history": min_history,
                                            "lcb_z": lcb_z,
                                            "min_lcb_cents": min_lcb,
                                            "min_neighbor_win_rate": min_win,
                                        }
                                        specs.append(
                                            StrategySpec(
                                                family,
                                                theorem_by_family[family],
                                                equation_by_family[family],
                                                params,
                                            )
                                        )
    results: list[dict[str, Any]] = []
    for spec in specs:
        rows = simulate_strategy(prepped, spec, history_mode="settlement_available", history_scope="all")
        summary = summarize_entry_rows(strategy_id(spec.family, spec.params), rows)
        risk = risk_summary(rows)
        results.append(
            {
                "family": spec.family,
                "strategy_id": strategy_id(spec.family, spec.params),
                "params": spec.params,
                **summary,
                "max_drawdown": risk["max_drawdown"],
                "loss_count": risk["loss_count"],
                "negative_active_days": risk["negative_active_days"],
            }
        )
    return sorted(results, key=lambda row: (row["sim_pnl"], row["entry_win_rate"]), reverse=True)


def permutation_suite(
    prepped: list[tuple[dict[str, Any], dict[str, Any]]],
    selected: dict[str, StrategySpec],
    row_caches: dict[str, dict[str, dict[str, Any] | None]],
    *,
    seeds: int,
) -> dict[str, Any]:
    output: dict[str, Any] = {}
    for family, strategy in selected.items():
        rows = []
        cache = row_caches[family]
        actual_rows = simulate_strategy(
            prepped,
            strategy,
            history_mode="settlement_available",
            history_scope="all",
            row_cache=cache,
        )
        actual_summary = summarize_entry_rows(strategy_id(strategy.family, strategy.params), actual_rows)
        for seed in range(seeds):
            override = shuffled_outcomes(cache, seed=1776 + seed)
            sim_rows = simulate_strategy(
                prepped,
                strategy,
                history_mode="settlement_available",
                history_scope="all",
                outcome_override=override,
                row_cache=cache,
            )
            summary = summarize_entry_rows(f"{family}:permutation:{seed}", sim_rows)
            rows.append(
                {
                    "seed": seed,
                    "sim_pnl": summary["sim_pnl"],
                    "entries": summary["entries"],
                    "entry_win_rate": summary["entry_win_rate"],
                    "worst_trade": summary["worst_trade"],
                }
            )
        pnls = sorted(float(row["sim_pnl"]) for row in rows)
        entries = sorted(int(row["entries"]) for row in rows)

        def pct(values: list[float | int], q: float) -> float:
            if not values:
                return 0.0
            pos = min(len(values) - 1, max(0, int(round((len(values) - 1) * q))))
            return round(float(values[pos]), 4)

        output[family] = {
            "actual_settlement_available_summary": actual_summary,
            "permutations": rows,
            "pnl_p05": pct(pnls, 0.05),
            "pnl_p50": pct(pnls, 0.50),
            "pnl_p95": pct(pnls, 0.95),
            "entries_p05": pct(entries, 0.05),
            "entries_p50": pct(entries, 0.50),
            "entries_p95": pct(entries, 0.95),
            "prob_permutation_ge_actual_pnl": round(
                sum(1 for row in rows if float(row["sim_pnl"]) >= actual_summary["sim_pnl"]) / max(1, len(rows)), 4
            ),
        }
    return output


def write_markdown(path: Path, payload: dict[str, Any]) -> None:
    lines = [
        "# Conformal Neighbor Stress Validation",
        "",
        f"- Generated: `{payload['generated_at']}`",
        f"- Cases: `{payload['case_count']}` across `{', '.join(payload['datasets'])}`",
        f"- Settlement timestamp fallback count: `{payload['settlement_info']['settlement_missing_fallback_count']}`",
        "- Scope: research-only; live entry/exit logic, configs, run scripts, and bot processes were not changed.",
        "",
        "## What Changed",
        "",
        "- The original candidate used prior entry chronology as its online history proxy.",
        "- This stress pass tests confirmed settlement-time label availability, dataset concentration, cross-dataset analogues, slippage, expanded nearby parameter grids, and randomized-history nulls.",
        "",
        "## Selected Candidate Stress",
        "",
        "| Family | Scenario | PnL | Delta Actual | Entries | Win Rate | Losses | Max DD |",
        "|---|---|---:|---:|---:|---:|---:|---:|",
    ]
    for row in payload["selected_scenarios"]:
        lines.append(
            f"| `{row['family']}` | `{row['scenario']}` | {row['sim_pnl']} | {row['delta_vs_actual']} | {row['entries']} | {row['entry_win_rate']} | {row['loss_count']} | {row['max_drawdown']} |"
        )
    lines.extend(["", "## Settlement-Aware Grid Top 12", "", "| Family | PnL | Entries | Win Rate | Losses | Max DD | Params |", "|---|---:|---:|---:|---:|---:|---|"])
    for row in payload["settlement_grid_top"][:12]:
        lines.append(
            f"| `{row['family']}` | {row['sim_pnl']} | {row['entries']} | {row['entry_win_rate']} | {row['loss_count']} | {row['max_drawdown']} | `{json.dumps(row['params'], sort_keys=True)}` |"
        )
    lines.extend(["", "## Randomized-History Null", "", "| Family | Actual PnL | Null p05 | Null p50 | Null p95 | P(null >= actual) |", "|---|---:|---:|---:|---:|---:|"])
    for family, item in payload["permutation"].items():
        actual = item["actual_settlement_available_summary"]
        lines.append(
            f"| `{family}` | {actual['sim_pnl']} | {item['pnl_p05']} | {item['pnl_p50']} | {item['pnl_p95']} | {item['prob_permutation_ge_actual_pnl']} |"
        )
    verdict = payload["verdict"]
    lines.extend(
        [
            "",
            "## Verdict",
            "",
            f"- Status: `{verdict['status']}`",
            f"- Main finding: {verdict['main_finding']}",
            f"- Next validation: {verdict['next_validation']}",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Stress validate online conformal neighbor entry candidates.")
    parser.add_argument("--datasets", nargs="*", default=None)
    parser.add_argument("--permutation-seeds", type=int, default=100)
    parser.add_argument("--refresh-btc-cache", action="store_true")
    args = parser.parse_args()

    cases, _ = load_cases(args.datasets)
    settlement_info = enrich_settlement_times(cases)
    selected = load_selected_strategies()
    candles = load_or_fetch_candles(cases, refresh_cache=args.refresh_btc_cache)
    delays = tuple(sorted({90, 120, 150, *[int(strategy.params["delay_seconds"]) for strategy in selected.values()]}))
    prepped = [(case, prepare_case(case, candles, delays)) for case in cases]

    selected_scenarios, row_caches = selected_stress_suite(prepped, selected)
    grid = settlement_grid(prepped, selected)
    permutation = permutation_suite(prepped, selected, row_caches, seeds=args.permutation_seeds)

    settlement_all = {
        row["family"]: row for row in selected_scenarios if row["scenario"] == "settlement_available_all"
    }
    sizer = settlement_all.get("online_neighbor_lcb_sizer")
    admission = settlement_all.get("online_neighbor_lcb_admission")
    if sizer and sizer["sim_pnl"] > 0 and sizer["entries"] >= 20 and sizer["loss_count"] == 0:
        status = "stress_survived_with_concentration_caveat"
        main_finding = (
            f"Settlement-aware history still produced ${sizer['sim_pnl']} on {sizer['entries']} entries, "
            "but most exposure remains concentrated in live_90_70."
        )
    elif admission and admission["sim_pnl"] > 0:
        status = "degraded_to_admission_watchlist"
        main_finding = (
            f"Sizing weakened under settlement-aware history, but admission remained positive at ${admission['sim_pnl']}."
        )
    else:
        status = "failed_settlement_available_stress"
        main_finding = "The candidate did not survive confirmed settlement-time label availability."

    stamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
    generated_at = datetime.now(UTC).isoformat()
    json_path = EDGE_DIR / f"conformal_neighbor_stress_validation_{stamp}.json"
    md_path = EDGE_DIR / f"conformal_neighbor_stress_validation_{stamp}.md"
    latest_json = EDGE_DIR / "conformal_neighbor_stress_validation_latest.json"
    latest_md = EDGE_DIR / "conformal_neighbor_stress_validation_latest.md"
    scenarios_csv = EDGE_DIR / f"conformal_neighbor_stress_scenarios_{stamp}.csv"
    grid_csv = EDGE_DIR / f"conformal_neighbor_stress_grid_{stamp}.csv"
    perm_csv = EDGE_DIR / f"conformal_neighbor_stress_permutations_{stamp}.csv"

    pd.DataFrame(selected_scenarios).drop(columns=["by_dataset", "by_side"], errors="ignore").to_csv(
        scenarios_csv, index=False
    )
    pd.DataFrame(grid).to_csv(grid_csv, index=False)
    permutation_rows = []
    for family, item in permutation.items():
        for row in item["permutations"]:
            permutation_rows.append({"family": family, **row})
    pd.DataFrame(permutation_rows).to_csv(perm_csv, index=False)

    payload = {
        "generated_at": generated_at,
        "json_path": str(json_path),
        "markdown_path": str(md_path),
        "case_count": len(cases),
        "datasets": sorted({case["dataset"] for case in cases}),
        "settlement_info": settlement_info,
        "baselines": baseline_payload(cases),
        "selected_scenarios": selected_scenarios,
        "settlement_grid_count": len(grid),
        "settlement_grid_top": grid[:40],
        "settlement_grid_positive_count": sum(1 for row in grid if row["sim_pnl"] > 0 and row["entries"] >= 10),
        "permutation": permutation,
        "csv_paths": {
            "scenarios": str(scenarios_csv),
            "grid": str(grid_csv),
            "permutations": str(perm_csv),
        },
        "verdict": {
            "status": status,
            "main_finding": main_finding,
            "next_validation": "Run a forward shadow pass on new trades; require non-live_90_70 entries before live consideration.",
        },
    }
    json_text = json.dumps(payload, indent=2, sort_keys=True)
    json_path.write_text(json_text, encoding="utf-8")
    latest_json.write_text(json_text, encoding="utf-8")
    write_markdown(md_path, payload)
    write_markdown(latest_md, payload)

    ledger_records = []
    for family, scenario in settlement_all.items():
        equation = selected[family].equation + " Stress overlay: history labels enter the neighbor pool only after settlement_ts <= decision_ts; slippage, dataset-scope, and permutation-null checks are evaluated separately."
        ledger_records.append(
            {
                "recorded_at": generated_at,
                "generated_at": generated_at,
                "source": Path(__file__).name,
                "status": status,
                "dataset": "all_quote_path_trades_with_closed_1m_btc",
                "datasets": payload["datasets"],
                "family": f"{family}_settlement_stress",
                "strategy_id": strategy_id(f"{family}_settlement_stress", selected[family].params),
                "idea_key": idea_key(f"{family}_settlement_stress", equation, selected[family].params),
                "theorem": selected[family].theorem,
                "equation": equation,
                "params": selected[family].params,
                "summary": {key: scenario[key] for key in scenario if key in summarize_entry_rows("x", []) or key in {"label"}},
                "scenario_summary": scenario,
                "permutation_summary": {
                    key: value
                    for key, value in permutation[family].items()
                    if key != "permutations"
                },
                "json_path": str(json_path),
                "markdown_path": str(md_path),
            }
        )
    append_ledger(ledger_records)

    memory_results = {
        record["family"]: {
            "strategy_id": record["strategy_id"],
            "summary": record["scenario_summary"],
        }
        for record in ledger_records
    }
    update_strategy_memory(payload, memory_results)

    print(
        f"Wrote {md_path} | status={status} | "
        f"sizer_settlement_pnl={(sizer or {}).get('sim_pnl')} entries={(sizer or {}).get('entries')}"
    )


if __name__ == "__main__":
    main()
