"""Stress validation for arXiv-inspired v28 strategy gates.

Research-only. This script imports the live-entry replay helpers from
`probe_arxiv_strategy_projection.py` and adds overfit checks:

- chronological and daily split consistency
- market-block bootstrap confidence intervals
- random same-coverage placebo comparisons
- parameter-neighborhood stability
- simple purged walk-forward lockout selection

It never submits orders and never edits live bot logic.
"""
from __future__ import annotations

import json
import random
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Iterable

import probe_arxiv_strategy_projection as projection


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
OUT_JSON = OUT_DIR / "arxiv_strategy_stress_validation_latest.json"
OUT_MD = OUT_DIR / "arxiv_strategy_stress_validation_latest.md"

SEED = 20260507
BOOTSTRAP_ITERATIONS = 2000
PLACEBO_ITERATIONS = 5000


Predicate = Callable[[dict[str, Any]], bool]


def fnum(value: Any, default: float = 0.0) -> float:
    parsed = projection.as_float(value)
    return default if parsed is None else parsed


def net_cents(rows: Iterable[dict[str, Any]]) -> float:
    return sum(fnum(row.get("pnl_cents")) for row in rows)


def stats(rows: list[dict[str, Any]], denominator: int) -> dict[str, Any]:
    return projection.trade_stats(rows, denominator)


def selected(rows: list[dict[str, Any]], predicate: Predicate) -> list[dict[str, Any]]:
    return [row for row in rows if predicate(row)]


def quantile(values: list[float], q: float) -> float | None:
    if not values:
        return None
    ordered = sorted(values)
    idx = min(len(ordered) - 1, max(0, int(round((len(ordered) - 1) * q))))
    return ordered[idx]


def percentile_rank(values: list[float], value: float) -> float | None:
    if not values:
        return None
    return sum(1 for item in values if item <= value) / len(values)


def pct(value: Any) -> str:
    parsed = projection.as_float(value)
    if parsed is None:
        return "n/a"
    return f"{100.0 * parsed:.1f}%"


def money(value: Any) -> str:
    parsed = projection.as_float(value)
    if parsed is None:
        return "n/a"
    return f"${parsed:,.2f}"


def cents(value: Any) -> str:
    parsed = projection.as_float(value)
    if parsed is None:
        return "n/a"
    return f"{parsed:,.1f}c"


def wl(row: dict[str, Any]) -> str:
    flats = int(row.get("flats") or 0)
    suffix = f" (+{flats} flat)" if flats else ""
    return f"{int(row.get('wins') or 0)}/{int(row.get('losses') or 0)}{suffix}"


def split_rows(rows: list[dict[str, Any]], parts: int) -> list[list[dict[str, Any]]]:
    out: list[list[dict[str, Any]]] = []
    n = len(rows)
    for i in range(parts):
        start = int(i * n / parts)
        end = int((i + 1) * n / parts)
        out.append(rows[start:end])
    return out


def rows_by_day(rows: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    grouped: dict[str, list[dict[str, Any]]] = {}
    for row in rows:
        entry_dt = row.get("_entry_dt")
        key = entry_dt.date().isoformat() if hasattr(entry_dt, "date") else "unknown"
        grouped.setdefault(key, []).append(row)
    return grouped


def rows_by_market(rows: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    grouped: dict[str, list[dict[str, Any]]] = {}
    for row in rows:
        grouped.setdefault(str(row.get("market") or ""), []).append(row)
    return grouped


def stable_seed(name: str, offset: int = 0) -> int:
    return SEED + offset + sum((idx + 1) * ord(ch) for idx, ch in enumerate(name))


def split_consistency(rows: list[dict[str, Any]], strategy: projection.Strategy) -> dict[str, Any]:
    chrono = []
    for idx, chunk in enumerate(split_rows(rows, 5), start=1):
        base_stats = stats(chunk, len(chunk))
        strategy_stats = stats(selected(chunk, strategy.predicate), len(chunk))
        chrono.append(
            {
                "slice": idx,
                "live_entries": len(chunk),
                "strategy": strategy_stats,
                "live_baseline": base_stats,
                "delta_vs_slice_live_cents": fnum(strategy_stats.get("net_cents")) - fnum(base_stats.get("net_cents")),
            }
        )
    day_rows = []
    for day, chunk in sorted(rows_by_day(rows).items()):
        if len(chunk) < 20:
            continue
        day_rows.append(
            {
                "day": day,
                "live_entries": len(chunk),
                "strategy": stats(selected(chunk, strategy.predicate), len(chunk)),
                "live_baseline": stats(chunk, len(chunk)),
            }
        )
    market_groups = rows_by_market(rows)
    market_pnls = []
    selected_market_pnls = []
    for market, chunk in market_groups.items():
        market_pnls.append((market, net_cents(chunk)))
        strategy_chunk = selected(chunk, strategy.predicate)
        if strategy_chunk:
            selected_market_pnls.append((market, net_cents(strategy_chunk), len(strategy_chunk)))
    return {
        "chronological_5_slices": chrono,
        "positive_chrono_slices": sum(1 for item in chrono if fnum(item["strategy"].get("net_cents")) > 0),
        "days_min20": day_rows,
        "positive_days_min20": sum(1 for item in day_rows if fnum(item["strategy"].get("net_cents")) > 0),
        "selected_markets": len(selected_market_pnls),
        "positive_selected_markets": sum(1 for _, pnl, _ in selected_market_pnls if pnl > 0),
        "negative_selected_markets": sum(1 for _, pnl, _ in selected_market_pnls if pnl < 0),
        "worst_selected_markets": [
            {"market": market, "net_cents": pnl, "entries": count}
            for market, pnl, count in sorted(selected_market_pnls, key=lambda item: item[1])[:8]
        ],
        "best_selected_markets": [
            {"market": market, "net_cents": pnl, "entries": count}
            for market, pnl, count in sorted(selected_market_pnls, key=lambda item: item[1], reverse=True)[:8]
        ],
        "all_market_count": len(market_groups),
    }


def market_block_bootstrap(rows: list[dict[str, Any]], strategy: projection.Strategy) -> dict[str, Any]:
    rng = random.Random(stable_seed(strategy.name, 1000))
    groups = rows_by_market(rows)
    keys = list(groups)
    strategy_nets: list[float] = []
    live_nets: list[float] = []
    deltas: list[float] = []
    selected_counts: list[float] = []
    for _ in range(BOOTSTRAP_ITERATIONS):
        sample_keys = [rng.choice(keys) for _ in keys]
        sample_rows = [row for key in sample_keys for row in groups[key]]
        strategy_rows = selected(sample_rows, strategy.predicate)
        strategy_net = net_cents(strategy_rows)
        live_net = net_cents(sample_rows)
        strategy_nets.append(strategy_net)
        live_nets.append(live_net)
        deltas.append(strategy_net - live_net)
        selected_counts.append(len(strategy_rows))
    actual_rows = selected(rows, strategy.predicate)
    actual_net = net_cents(actual_rows)
    return {
        "iterations": BOOTSTRAP_ITERATIONS,
        "actual_net_cents": actual_net,
        "actual_entries": len(actual_rows),
        "net_cents_p05": quantile(strategy_nets, 0.05),
        "net_cents_p50": quantile(strategy_nets, 0.50),
        "net_cents_p95": quantile(strategy_nets, 0.95),
        "delta_vs_live_cents_p05": quantile(deltas, 0.05),
        "delta_vs_live_cents_p50": quantile(deltas, 0.50),
        "delta_vs_live_cents_p95": quantile(deltas, 0.95),
        "prob_net_positive": sum(1 for value in strategy_nets if value > 0) / len(strategy_nets),
        "prob_beats_same_sample_live": sum(1 for value in deltas if value > 0) / len(deltas),
        "avg_selected_entries": sum(selected_counts) / len(selected_counts),
    }


def random_same_coverage_placebo(rows: list[dict[str, Any]], strategy: projection.Strategy) -> dict[str, Any]:
    rng = random.Random(stable_seed(strategy.name, 2000))
    strategy_rows = selected(rows, strategy.predicate)
    n = len(strategy_rows)
    actual = net_cents(strategy_rows)
    if n <= 0:
        return {"iterations": PLACEBO_ITERATIONS, "actual_net_cents": actual, "entries": n}
    placebo_nets = []
    for _ in range(PLACEBO_ITERATIONS):
        placebo_nets.append(net_cents(rng.sample(rows, n)))
    return {
        "iterations": PLACEBO_ITERATIONS,
        "entries": n,
        "actual_net_cents": actual,
        "placebo_net_cents_p05": quantile(placebo_nets, 0.05),
        "placebo_net_cents_p50": quantile(placebo_nets, 0.50),
        "placebo_net_cents_p95": quantile(placebo_nets, 0.95),
        "placebo_mean_net_cents": sum(placebo_nets) / len(placebo_nets),
        "p_value_placebo_ge_actual": (sum(1 for value in placebo_nets if value >= actual) + 1) / (len(placebo_nets) + 1),
    }


def le(value: Any, threshold: float) -> bool:
    parsed = projection.as_float(value)
    return parsed is not None and parsed <= threshold


def ge(value: Any, threshold: float) -> bool:
    parsed = projection.as_float(value)
    return parsed is not None and parsed >= threshold


def between(value: Any, low: float, high: float) -> bool:
    parsed = projection.as_float(value)
    return parsed is not None and low <= parsed <= high


@dataclass(frozen=True)
class Family:
    name: str
    strategy_name: str
    current_params: tuple[Any, ...]
    param_names: tuple[str, ...]
    grid: list[tuple[Any, ...]]
    min_all_entries: int
    min_train_entries: int
    builder: Callable[[tuple[Any, ...]], Predicate]


def build_families() -> list[Family]:
    consensus_grid = [
        (gap, edge)
        for gap in (0.06, 0.08, 0.10, 0.12, 0.15, 0.20, 0.30)
        for edge in (2.0, 3.0, 4.0, 6.0, 8.0)
    ]
    fill_grid = [
        (depth_ratio, book_age, ask, min_seconds)
        for depth_ratio in (1.0, 2.0, 3.0, 5.0, 8.0, 10.0, 15.0, 20.0)
        for book_age in (500.0, 750.0, 1000.0)
        for ask in (80.0, 81.0, 83.0, 85.0, 90.0)
        for min_seconds in (120.0, 300.0, 450.0, 600.0, 750.0)
    ]
    fpt_grid = [
        (edge, min_seconds, low_absd, high_absd)
        for edge in (2.0, 3.0, 4.0, 6.0, 8.0)
        for min_seconds in (60.0, 120.0, 180.0, 300.0, 450.0)
        for low_absd in (0.55, 0.70, 0.80, 0.85)
        for high_absd in (1.10, 1.25, 1.50, 1.75)
        if low_absd < high_absd
    ]
    hybrid_grid = [
        (edge, depth_ratio, book_age, ask, min_seconds, low_absd, high_absd)
        for edge in (2.0, 3.0, 4.0, 6.0)
        for depth_ratio in (3.0, 5.0, 8.0, 10.0, 15.0)
        for book_age in (500.0, 750.0, 1000.0)
        for ask in (80.0, 83.0, 85.0)
        for min_seconds in (120.0, 300.0, 450.0, 600.0)
        for low_absd in (0.70, 0.80, 0.85)
        for high_absd in (1.10, 1.25, 1.50)
        if low_absd < high_absd
    ]
    return [
        Family(
            name="consensus_probability_gap",
            strategy_name="conformal_consensus_winrate_gate",
            current_params=(0.12, 4.0),
            param_names=("max_probability_gap", "min_edge_cents"),
            grid=consensus_grid,
            min_all_entries=30,
            min_train_entries=20,
            builder=lambda params: lambda row: le(row.get("probability_gap"), params[0]) and ge(row.get("edge28_cents"), params[1]),
        ),
        Family(
            name="depth_decay_fillability",
            strategy_name="depth_decay_fillability_gate",
            current_params=(3.0, 750.0, 80.0, 600.0),
            param_names=("min_depth_ratio", "max_book_age_ms", "max_ask_cents", "min_seconds_to_close"),
            grid=fill_grid,
            min_all_entries=30,
            min_train_entries=20,
            builder=lambda params: lambda row: (
                ge(row.get("depth_ratio"), params[0])
                and le(row.get("book_age_ms"), params[1])
                and le(row.get("ask_cents"), params[2])
                and ge(row.get("seconds_to_close"), params[3])
            ),
        ),
        Family(
            name="brownian_fpt_sanity",
            strategy_name="brownian_fpt_sanity_gate",
            current_params=(3.0, 120.0, 0.70, 1.10),
            param_names=("min_edge_cents", "min_seconds_to_close", "min_abs_d_sigma", "max_abs_d_sigma"),
            grid=fpt_grid,
            min_all_entries=30,
            min_train_entries=20,
            builder=lambda params: lambda row: (
                ge(row.get("edge28_cents"), params[0])
                and ge(row.get("seconds_to_close"), params[1])
                and between(row.get("abs_d_sigma"), params[2], params[3])
            ),
        ),
        Family(
            name="hybrid_fpt_depth",
            strategy_name="hybrid_fpt_depth_gate",
            current_params=(3.0, 8.0, 750.0, 83.0, 120.0, 0.85, 1.10),
            param_names=(
                "min_edge_cents",
                "min_depth_ratio",
                "max_book_age_ms",
                "max_ask_cents",
                "min_seconds_to_close",
                "min_abs_d_sigma",
                "max_abs_d_sigma",
            ),
            grid=hybrid_grid,
            min_all_entries=30,
            min_train_entries=20,
            builder=lambda params: lambda row: (
                ge(row.get("edge28_cents"), params[0])
                and ge(row.get("depth_ratio"), params[1])
                and le(row.get("book_age_ms"), params[2])
                and le(row.get("ask_cents"), params[3])
                and ge(row.get("seconds_to_close"), params[4])
                and between(row.get("abs_d_sigma"), params[5], params[6])
            ),
        ),
    ]


def split_positive(split_stats: dict[str, dict[str, Any]]) -> bool:
    return all(fnum(item.get("net_cents")) > 0 for item in split_stats.values())


def family_cell(rows: list[dict[str, Any]], family: Family, params: tuple[Any, ...]) -> dict[str, Any]:
    predicate = family.builder(params)
    all_selected = selected(rows, predicate)
    splits = {}
    for name, chunk in {
        "train_first_60pct": rows[: int(0.60 * len(rows))],
        "validation_next_20pct": rows[int(0.60 * len(rows)) : int(0.80 * len(rows))],
        "holdout_last_20pct": rows[int(0.80 * len(rows)) :],
    }.items():
        splits[name] = stats(selected(chunk, predicate), len(chunk))
    cell = {
        "params": {name: value for name, value in zip(family.param_names, params)},
        "param_tuple": params,
        "all": stats(all_selected, len(rows)),
        "splits": splits,
    }
    cell["split_positive"] = split_positive(splits)
    return cell


def parameter_stability(rows: list[dict[str, Any]], family: Family) -> dict[str, Any]:
    cells = [family_cell(rows, family, params) for params in family.grid]
    eligible = [cell for cell in cells if int(cell["all"].get("entries") or 0) >= family.min_all_entries]
    net_values = [fnum(cell["all"].get("net_cents")) for cell in eligible]
    current = family_cell(rows, family, family.current_params)
    current_net = fnum(current["all"].get("net_cents"))
    positive = [cell for cell in eligible if fnum(cell["all"].get("net_cents")) > 0]
    split_pos = [cell for cell in eligible if cell.get("split_positive")]
    top = sorted(eligible, key=lambda cell: fnum(cell["all"].get("net_cents")), reverse=True)[:8]
    return {
        "family": family.name,
        "strategy_name": family.strategy_name,
        "grid_cells": len(cells),
        "eligible_cells_min_entries": len(eligible),
        "min_all_entries": family.min_all_entries,
        "positive_cell_share": len(positive) / len(eligible) if eligible else None,
        "split_positive_cell_share": len(split_pos) / len(eligible) if eligible else None,
        "net_cents_p10": quantile(net_values, 0.10),
        "net_cents_p50": quantile(net_values, 0.50),
        "net_cents_p90": quantile(net_values, 0.90),
        "current_cell": current,
        "current_net_percentile": percentile_rank(net_values, current_net),
        "top_cells": top,
    }


def last_unique_markets(rows: list[dict[str, Any]], count: int) -> set[str]:
    seen: list[str] = []
    for row in reversed(rows):
        market = str(row.get("market") or "")
        if market and market not in seen:
            seen.append(market)
        if len(seen) >= count:
            break
    return set(seen)


def walk_forward_lockout(rows: list[dict[str, Any]], family: Family) -> dict[str, Any]:
    chunks = split_rows(rows, 5)
    folds = []
    combined_eval_rows: list[dict[str, Any]] = []
    combined_eval_selected: list[dict[str, Any]] = []
    for idx in range(2, 5):
        raw_train = [row for chunk in chunks[:idx] for row in chunk]
        purge_markets = last_unique_markets(raw_train, 5)
        train = [row for row in raw_train if str(row.get("market") or "") not in purge_markets]
        eval_rows = chunks[idx]
        candidates = []
        for params in family.grid:
            predicate = family.builder(params)
            train_selected = selected(train, predicate)
            if len(train_selected) < family.min_train_entries:
                continue
            train_stats = stats(train_selected, len(train))
            if fnum(train_stats.get("net_cents")) <= 0:
                continue
            candidates.append((fnum(train_stats.get("net_cents")), fnum(train_stats.get("avg_cents_per_entry")), params, train_stats))
        if not candidates:
            folds.append(
                {
                    "fold": idx - 1,
                    "train_entries": len(train),
                    "eval_entries": len(eval_rows),
                    "selected_params": None,
                    "train": {},
                    "eval": {},
                    "live_eval": stats(eval_rows, len(eval_rows)),
                    "purged_markets": sorted(purge_markets),
                }
            )
            continue
        candidates.sort(key=lambda item: (item[0], item[1]), reverse=True)
        _, _, params, train_stats = candidates[0]
        predicate = family.builder(params)
        eval_selected = selected(eval_rows, predicate)
        combined_eval_rows.extend(eval_rows)
        combined_eval_selected.extend(eval_selected)
        folds.append(
            {
                "fold": idx - 1,
                "train_entries": len(train),
                "eval_entries": len(eval_rows),
                "selected_params": {name: value for name, value in zip(family.param_names, params)},
                "train": train_stats,
                "eval": stats(eval_selected, len(eval_rows)),
                "live_eval": stats(eval_rows, len(eval_rows)),
                "purged_markets": sorted(purge_markets),
            }
        )
    return {
        "family": family.name,
        "strategy_name": family.strategy_name,
        "folds": folds,
        "combined_eval": stats(combined_eval_selected, len(combined_eval_rows)),
        "combined_live_eval": stats(combined_eval_rows, len(combined_eval_rows)),
    }


def overfit_read(strategy_name: str, validation: dict[str, Any], stability: dict[str, Any], walk: dict[str, Any]) -> dict[str, Any]:
    bootstrap = validation.get("bootstrap") or {}
    placebo = validation.get("placebo") or {}
    split = validation.get("split_consistency") or {}
    warnings = []
    strengths = []
    if fnum(bootstrap.get("prob_net_positive")) >= 0.90:
        strengths.append("bootstrap_net_positive")
    else:
        warnings.append("weak_bootstrap_positive_probability")
    if fnum(bootstrap.get("prob_beats_same_sample_live")) >= 0.70:
        strengths.append("often_beats_same_sample_live_bootstrap")
    else:
        warnings.append("does_not_reliably_beat_same_sample_live_bootstrap")
    if fnum(placebo.get("p_value_placebo_ge_actual"), 1.0) <= 0.10:
        strengths.append("beats_same_coverage_placebo")
    else:
        warnings.append("not_unusual_vs_random_same_coverage")
    if int(split.get("positive_chrono_slices") or 0) >= 4:
        strengths.append("positive_in_most_chrono_slices")
    else:
        warnings.append("chronological_slice_fragility")
    if fnum(stability.get("positive_cell_share")) >= 0.60:
        strengths.append("positive_parameter_neighborhood")
    else:
        warnings.append("thin_parameter_neighborhood")
    if fnum(stability.get("split_positive_cell_share")) >= 0.15:
        strengths.append("some_split_positive_neighbor_cells")
    else:
        warnings.append("few_split_positive_neighbor_cells")
    if fnum(stability.get("split_positive_cell_share")) >= 0.50:
        strengths.append("many_split_positive_neighbor_cells")
    else:
        warnings.append("limited_split_positive_neighbor_cells")
    if fnum(stability.get("current_net_percentile")) >= 0.98:
        warnings.append("current_params_near_grid_peak")
    walk_net = fnum((walk.get("combined_eval") or {}).get("net_cents"))
    if walk_net > 0:
        strengths.append("purged_walk_forward_positive")
        if walk_net < 500.0:
            warnings.append("thin_purged_walk_forward_margin")
    else:
        warnings.append("purged_walk_forward_failed")
    if (
        walk_net > 500.0
        and fnum(placebo.get("p_value_placebo_ge_actual"), 1.0) <= 0.05
        and fnum(bootstrap.get("prob_net_positive")) >= 0.95
        and fnum(bootstrap.get("prob_beats_same_sample_live")) >= 0.70
        and fnum(stability.get("positive_cell_share")) >= 0.80
        and fnum(stability.get("split_positive_cell_share")) >= 0.50
    ):
        risk = "lower_replay_overfit_risk_but_forward_needed"
    elif len(warnings) <= 4:
        risk = "medium_replay_overfit_risk"
    else:
        risk = "high_replay_overfit_risk"
    return {
        "strategy_name": strategy_name,
        "risk": risk,
        "strengths": strengths,
        "warnings": warnings,
    }


def build_report() -> dict[str, Any]:
    rows, diagnostics = projection.load_matched_live_trades()
    rows.sort(key=lambda row: row["_entry_dt"])
    strategies = [strategy for strategy in projection.STRATEGIES if strategy.name != "current_live_v28_replay"]
    families = {family.strategy_name: family for family in build_families()}

    strategy_validations = {}
    stabilities = {}
    walks = {}
    reads = []
    for strategy in strategies:
        validation = {
            "all": stats(selected(rows, strategy.predicate), len(rows)),
            "split_consistency": split_consistency(rows, strategy),
            "bootstrap": market_block_bootstrap(rows, strategy),
            "placebo": random_same_coverage_placebo(rows, strategy),
        }
        family = families[strategy.name]
        stability = parameter_stability(rows, family)
        walk = walk_forward_lockout(rows, family)
        strategy_validations[strategy.name] = validation
        stabilities[strategy.name] = stability
        walks[strategy.name] = walk
        reads.append(overfit_read(strategy.name, validation, stability, walk))

    return {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "purpose": "Research-only overfit stress validation for arXiv-inspired v28 replay gates.",
        "random_seed": SEED,
        "diagnostics": diagnostics,
        "live_baseline": stats(rows, len(rows)),
        "strategy_validations": strategy_validations,
        "parameter_stability": stabilities,
        "walk_forward_lockout": walks,
        "overfit_reads": reads,
    }


def write_md(report: dict[str, Any]) -> None:
    lines = [
        "# arXiv Strategy Stress Validation",
        "",
        "Research-only. These checks test whether the paper-inspired gates look stable, not whether they are ready for live promotion.",
        "",
        f"- Generated UTC: `{report.get('generated_at_utc')}`",
        f"- Matched live trades: `{report.get('diagnostics', {}).get('matched_trade_count')}`",
        f"- Bootstrap iterations: `{BOOTSTRAP_ITERATIONS}` market-block samples",
        f"- Placebo iterations: `{PLACEBO_ITERATIONS}` random same-coverage samples",
        "",
        "## Verdict",
        "",
        "| strategy | overfit read | all PnL | W/L | chrono + slices | bootstrap P(net>0) | placebo p | param + cells | split+ cells | walk-forward eval PnL | notes |",
        "|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---|",
    ]
    reads = {row["strategy_name"]: row for row in report.get("overfit_reads") or []}
    for name, validation in (report.get("strategy_validations") or {}).items():
        all_stats = validation.get("all") or {}
        split = validation.get("split_consistency") or {}
        bootstrap = validation.get("bootstrap") or {}
        placebo = validation.get("placebo") or {}
        stability = (report.get("parameter_stability") or {}).get(name) or {}
        walk = (report.get("walk_forward_lockout") or {}).get(name) or {}
        read = reads.get(name, {})
        notes = ", ".join(read.get("warnings") or [])
        lines.append(
            f"| {name} | {read.get('risk')} | {money(all_stats.get('net_dollars'))} | {wl(all_stats)} | "
            f"{split.get('positive_chrono_slices')}/5 | {pct(bootstrap.get('prob_net_positive'))} | "
            f"{projection.as_float(placebo.get('p_value_placebo_ge_actual')):.3f} | "
            f"{pct(stability.get('positive_cell_share'))} | {pct(stability.get('split_positive_cell_share'))} | "
            f"{money((walk.get('combined_eval') or {}).get('net_dollars'))} | {notes} |"
        )
    lines.extend(
        [
            "",
            "## Parameter Stability",
            "",
            "| family | eligible cells | current percentile | net p10/p50/p90 | current net | current split+ | top cell net |",
            "|---|---:|---:|---:|---:|---|---:|",
        ]
    )
    for stability in (report.get("parameter_stability") or {}).values():
        current = stability.get("current_cell") or {}
        top = (stability.get("top_cells") or [{}])[0]
        lines.append(
            f"| {stability.get('family')} | {stability.get('eligible_cells_min_entries')} | "
            f"{pct(stability.get('current_net_percentile'))} | "
            f"{cents(stability.get('net_cents_p10'))}/{cents(stability.get('net_cents_p50'))}/{cents(stability.get('net_cents_p90'))} | "
            f"{money((current.get('all') or {}).get('net_dollars'))} | {current.get('split_positive')} | "
            f"{money((top.get('all') or {}).get('net_dollars'))} |"
        )
    lines.extend(
        [
            "",
            "## Walk-Forward Lockout",
            "",
            "Each family picks the best positive parameter set on prior data, purges the last 5 train markets, then scores the next chronological chunk.",
            "",
            "| family | combined eval entries | combined eval W/L | combined eval PnL | live eval PnL | fold eval PnLs |",
            "|---|---:|---:|---:|---:|---|",
        ]
    )
    for walk in (report.get("walk_forward_lockout") or {}).values():
        combined = walk.get("combined_eval") or {}
        live = walk.get("combined_live_eval") or {}
        fold_pnls = ", ".join(money((fold.get("eval") or {}).get("net_dollars")) for fold in walk.get("folds") or [])
        lines.append(
            f"| {walk.get('family')} | {combined.get('entries')} | {wl(combined)} | "
            f"{money(combined.get('net_dollars'))} | {money(live.get('net_dollars'))} | {fold_pnls} |"
        )
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "- `placebo p` is the fraction of random same-size trade subsets with PnL at least as high as the candidate; lower is better.",
            "- `param + cells` means the share of nearby parameter cells with positive total PnL. `split+ cells` means train, validation, and holdout were all positive.",
            "- This is still retrospective live-log replay. The promotion gate should remain frozen forward collection, not immediate live logic changes.",
        ]
    )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    report = build_report()
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8")
    write_md(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
