"""Multi-schedule walk-forward deepening for arXiv-inspired v28 candidates.

Research-only. This script tries to improve and de-fluke the candidate gates
from `probe_arxiv_strategy_projection.py` by evaluating each parameter family
across multiple walk-forward schedules and two parameter-selection modes.

The output is meant to decide which candidates deserve frozen-forward
collection. It is not a live-trading implementation.
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from statistics import median
from typing import Any, Callable

import probe_arxiv_strategy_projection as projection
import probe_arxiv_strategy_stress_validation as stress


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
OUT_JSON = OUT_DIR / "arxiv_strategy_walkforward_deepening_latest.json"
OUT_MD = OUT_DIR / "arxiv_strategy_walkforward_deepening_latest.md"

Predicate = Callable[[dict[str, Any]], bool]


@dataclass(frozen=True)
class WalkSchedule:
    name: str
    kind: str
    parts: int = 0
    min_train_parts: int = 0
    mode: str = "anchored"
    train_window_parts: int = 0
    purge_markets: int = 5
    min_eval_entries: int = 20
    min_train_days: int = 2


SCHEDULES = [
    WalkSchedule(name="anchored_5_purge5", kind="parts", parts=5, min_train_parts=2, mode="anchored", purge_markets=5),
    WalkSchedule(name="anchored_6_purge5", kind="parts", parts=6, min_train_parts=2, mode="anchored", purge_markets=5),
    WalkSchedule(name="anchored_8_purge10", kind="parts", parts=8, min_train_parts=3, mode="anchored", purge_markets=10),
    WalkSchedule(name="rolling_6_train2_purge5", kind="parts", parts=6, min_train_parts=2, mode="rolling", train_window_parts=2, purge_markets=5),
    WalkSchedule(name="rolling_8_train3_purge10", kind="parts", parts=8, min_train_parts=3, mode="rolling", train_window_parts=3, purge_markets=10),
    WalkSchedule(name="daily_expanding_purge5", kind="days", purge_markets=5, min_train_days=2, min_eval_entries=20),
]

SELECTION_MODES = ("max_train_net", "stable_subsplit")
POOL_LIMITS = {
    "consensus_probability_gap": 80,
    "depth_decay_fillability": 260,
    "brownian_fpt_sanity": 260,
    "hybrid_fpt_depth": 420,
}


def fnum(value: Any, default: float = 0.0) -> float:
    parsed = projection.as_float(value)
    return default if parsed is None else parsed


def rows_net(rows: list[dict[str, Any]]) -> float:
    return sum(fnum(row.get("pnl_cents")) for row in rows)


def stats(rows: list[dict[str, Any]], denominator: int) -> dict[str, Any]:
    return projection.trade_stats(rows, denominator)


def selected(rows: list[dict[str, Any]], predicate: Predicate) -> list[dict[str, Any]]:
    return [row for row in rows if predicate(row)]


def split_rows(rows: list[dict[str, Any]], parts: int) -> list[list[dict[str, Any]]]:
    return stress.split_rows(rows, parts)


def last_unique_markets(rows: list[dict[str, Any]], count: int) -> set[str]:
    return stress.last_unique_markets(rows, count)


def purge_tail_markets(rows: list[dict[str, Any]], count: int) -> tuple[list[dict[str, Any]], list[str]]:
    if count <= 0:
        return rows, []
    purged = last_unique_markets(rows, count)
    return [row for row in rows if str(row.get("market") or "") not in purged], sorted(purged)


def grouped_days(rows: list[dict[str, Any]]) -> list[tuple[str, list[dict[str, Any]]]]:
    by_day = stress.rows_by_day(rows)
    return sorted(by_day.items())


def build_folds(rows: list[dict[str, Any]], schedule: WalkSchedule) -> list[dict[str, Any]]:
    folds: list[dict[str, Any]] = []
    if schedule.kind == "parts":
        chunks = split_rows(rows, schedule.parts)
        for eval_idx in range(schedule.min_train_parts, schedule.parts):
            if schedule.mode == "rolling":
                train_start = max(0, eval_idx - schedule.train_window_parts)
                raw_train = [row for chunk in chunks[train_start:eval_idx] for row in chunk]
            else:
                raw_train = [row for chunk in chunks[:eval_idx] for row in chunk]
            train, purged = purge_tail_markets(raw_train, schedule.purge_markets)
            eval_rows = chunks[eval_idx]
            if len(eval_rows) < schedule.min_eval_entries:
                continue
            folds.append(
                {
                    "fold": len(folds) + 1,
                    "train": train,
                    "eval": eval_rows,
                    "raw_train_entries": len(raw_train),
                    "purged_markets": purged,
                    "schedule": schedule.name,
                }
            )
        return folds

    if schedule.kind == "days":
        days = grouped_days(rows)
        for eval_idx in range(schedule.min_train_days, len(days)):
            raw_train = [row for _, chunk in days[:eval_idx] for row in chunk]
            train, purged = purge_tail_markets(raw_train, schedule.purge_markets)
            eval_day, eval_rows = days[eval_idx]
            if len(eval_rows) < schedule.min_eval_entries:
                continue
            folds.append(
                {
                    "fold": len(folds) + 1,
                    "train": train,
                    "eval": eval_rows,
                    "raw_train_entries": len(raw_train),
                    "purged_markets": purged,
                    "schedule": schedule.name,
                    "eval_day": eval_day,
                }
            )
    return folds


def train_subsplit_nets(train: list[dict[str, Any]], predicate: Predicate) -> list[float]:
    chunks = split_rows(train, 3)
    return [rows_net(selected(chunk, predicate)) for chunk in chunks if chunk]


def selection_score(
    family: stress.Family,
    params: tuple[Any, ...],
    train: list[dict[str, Any]],
    mode: str,
) -> tuple[Any, ...] | None:
    predicate = family.builder(params)
    train_selected = selected(train, predicate)
    if len(train_selected) < family.min_train_entries:
        return None
    train_stats = stats(train_selected, len(train))
    train_net = fnum(train_stats.get("net_cents"))
    if train_net <= 0:
        return None
    avg = fnum(train_stats.get("avg_cents_per_entry"))
    if mode == "max_train_net":
        return (train_net, avg, len(train_selected))
    nets = train_subsplit_nets(train, predicate)
    positives = sum(1 for value in nets if value > 0)
    if positives < 2:
        return None
    return (positives, min(nets), median(nets), train_net, avg, len(train_selected))


def choose_params(
    family: stress.Family,
    params_list: list[tuple[Any, ...]],
    train: list[dict[str, Any]],
    mode: str,
) -> tuple[tuple[Any, ...] | None, dict[str, Any]]:
    best: tuple[tuple[Any, ...], tuple[Any, ...]] | None = None
    considered = 0
    eligible = 0
    for params in params_list:
        considered += 1
        score = selection_score(family, params, train, mode)
        if score is None:
            continue
        eligible += 1
        if best is None or score > best[1]:
            best = (params, score)
    if best is None:
        return None, {"considered": considered, "eligible": eligible, "score": None}
    return best[0], {"considered": considered, "eligible": eligible, "score": best[1]}


def summarize_fold_eval(
    family: stress.Family,
    params: tuple[Any, ...],
    fold: dict[str, Any],
) -> dict[str, Any]:
    predicate = family.builder(params)
    train_selected = selected(fold["train"], predicate)
    eval_selected = selected(fold["eval"], predicate)
    return {
        "fold": fold.get("fold"),
        "eval_day": fold.get("eval_day"),
        "raw_train_entries": fold.get("raw_train_entries"),
        "train_entries_after_purge": len(fold["train"]),
        "eval_entries": len(fold["eval"]),
        "params": {name: value for name, value in zip(family.param_names, params)},
        "train": stats(train_selected, len(fold["train"])),
        "eval": stats(eval_selected, len(fold["eval"])),
        "live_eval": stats(fold["eval"], len(fold["eval"])),
        "delta_vs_live_eval_cents": rows_net(eval_selected) - rows_net(fold["eval"]),
        "purged_markets": fold.get("purged_markets") or [],
    }


def combine_eval(folds: list[dict[str, Any]]) -> dict[str, Any]:
    eval_rows = [row for fold in folds for row in fold["eval_rows"]]
    live_rows = [row for fold in folds for row in fold["live_rows"]]
    return {
        "strategy": stats(eval_rows, len(live_rows)),
        "live": stats(live_rows, len(live_rows)),
        "delta_vs_live_cents": rows_net(eval_rows) - rows_net(live_rows),
        "positive_folds": sum(1 for fold in folds if fnum((fold.get("eval") or {}).get("net_cents")) > 0),
        "beat_live_folds": sum(1 for fold in folds if fnum(fold.get("delta_vs_live_eval_cents")) > 0),
        "folds": len(folds),
    }


def run_dynamic_schedule(
    rows: list[dict[str, Any]],
    family: stress.Family,
    params_list: list[tuple[Any, ...]],
    schedule: WalkSchedule,
    mode: str,
) -> dict[str, Any]:
    folds = build_folds(rows, schedule)
    fold_reports = []
    combined = []
    for fold in folds:
        params, selection = choose_params(family, params_list, fold["train"], mode)
        if params is None:
            eval_selected: list[dict[str, Any]] = []
            report = {
                "fold": fold.get("fold"),
                "eval_day": fold.get("eval_day"),
                "raw_train_entries": fold.get("raw_train_entries"),
                "train_entries_after_purge": len(fold["train"]),
                "eval_entries": len(fold["eval"]),
                "params": None,
                "selection": selection,
                "train": {},
                "eval": stats([], len(fold["eval"])),
                "live_eval": stats(fold["eval"], len(fold["eval"])),
                "delta_vs_live_eval_cents": -rows_net(fold["eval"]),
                "purged_markets": fold.get("purged_markets") or [],
            }
        else:
            report = summarize_fold_eval(family, params, fold)
            report["selection"] = selection
            eval_selected = selected(fold["eval"], family.builder(params))
        fold_reports.append(report)
        combined.append({"eval_rows": eval_selected, "live_rows": fold["eval"], **report})
    summary = combine_eval(combined)
    return {
        "family": family.name,
        "schedule": schedule.name,
        "selection_mode": mode,
        "summary": summary,
        "fold_reports": fold_reports,
    }


def evaluate_fixed_schedule(
    rows: list[dict[str, Any]],
    family: stress.Family,
    params: tuple[Any, ...],
    schedule: WalkSchedule,
) -> dict[str, Any]:
    folds = build_folds(rows, schedule)
    combined = []
    fold_reports = []
    predicate = family.builder(params)
    for fold in folds:
        eval_selected = selected(fold["eval"], predicate)
        report = summarize_fold_eval(family, params, fold)
        fold_reports.append(report)
        combined.append({"eval_rows": eval_selected, "live_rows": fold["eval"], **report})
    return {
        "family": family.name,
        "schedule": schedule.name,
        "params": {name: value for name, value in zip(family.param_names, params)},
        "summary": combine_eval(combined),
        "fold_reports": fold_reports,
    }


def evaluate_fixed_schedule_compact(
    rows: list[dict[str, Any]],
    family: stress.Family,
    params: tuple[Any, ...],
    schedule: WalkSchedule,
) -> dict[str, Any]:
    folds = build_folds(rows, schedule)
    predicate = family.builder(params)
    eval_selected = []
    live_rows = []
    fold_summaries = []
    for fold in folds:
        fold_selected = selected(fold["eval"], predicate)
        eval_selected.extend(fold_selected)
        live_rows.extend(fold["eval"])
        fold_summaries.append(
            {
                "fold": fold.get("fold"),
                "eval_day": fold.get("eval_day"),
                "eval": stats(fold_selected, len(fold["eval"])),
                "live_eval": stats(fold["eval"], len(fold["eval"])),
                "delta_vs_live_eval_cents": rows_net(fold_selected) - rows_net(fold["eval"]),
            }
        )
    strategy_stats = stats(eval_selected, len(live_rows))
    live_stats = stats(live_rows, len(live_rows))
    return {
        "family": family.name,
        "schedule": schedule.name,
        "params": {name: value for name, value in zip(family.param_names, params)},
        "summary": {
            "strategy": strategy_stats,
            "live": live_stats,
            "delta_vs_live_cents": rows_net(eval_selected) - rows_net(live_rows),
            "positive_folds": sum(1 for item in fold_summaries if fnum(item["eval"].get("net_cents")) > 0),
            "beat_live_folds": sum(1 for item in fold_summaries if fnum(item.get("delta_vs_live_eval_cents")) > 0),
            "folds": len(fold_summaries),
        },
        "fold_summaries": fold_summaries,
    }


def aggregate_fixed_schedules(schedule_reports: list[dict[str, Any]]) -> dict[str, Any]:
    nets = [fnum((item.get("summary") or {}).get("strategy", {}).get("net_cents")) for item in schedule_reports]
    deltas = [fnum((item.get("summary") or {}).get("delta_vs_live_cents")) for item in schedule_reports]
    entries = [fnum((item.get("summary") or {}).get("strategy", {}).get("entries")) for item in schedule_reports]
    return {
        "schedules": len(schedule_reports),
        "positive_schedules": sum(1 for value in nets if value > 0),
        "beat_live_schedules": sum(1 for value in deltas if value > 0),
        "net_cents_min": min(nets) if nets else None,
        "net_cents_median": median(nets) if nets else None,
        "net_cents_sum_repeated_windows": sum(nets),
        "delta_vs_live_cents_median": median(deltas) if deltas else None,
        "avg_eval_entries": sum(entries) / len(entries) if entries else None,
    }


def fixed_current_summary(rows: list[dict[str, Any]], family: stress.Family) -> dict[str, Any]:
    reports = [evaluate_fixed_schedule(rows, family, family.current_params, schedule) for schedule in SCHEDULES]
    all_predicate = family.builder(family.current_params)
    return {
        "family": family.name,
        "params": {name: value for name, value in zip(family.param_names, family.current_params)},
        "all_replay": stats(selected(rows, all_predicate), len(rows)),
        "schedule_reports": reports,
        "aggregate": aggregate_fixed_schedules(reports),
    }


def build_param_pool(rows: list[dict[str, Any]], family: stress.Family) -> list[tuple[Any, ...]]:
    scored = []
    for params in family.grid:
        predicate = family.builder(params)
        all_replay = stats(selected(rows, predicate), len(rows))
        entries = int(all_replay.get("entries") or 0)
        if entries < family.min_all_entries:
            continue
        scored.append(
            (
                fnum(all_replay.get("net_cents")),
                fnum(all_replay.get("avg_cents_per_entry")),
                entries,
                params,
            )
        )
    scored.sort(reverse=True)
    limit = POOL_LIMITS.get(family.name, 250)
    pool = [item[3] for item in scored[:limit]]
    if family.current_params not in pool:
        pool.append(family.current_params)
    return pool


def robust_fixed_leaders(
    rows: list[dict[str, Any]],
    family: stress.Family,
    params_list: list[tuple[Any, ...]],
    limit: int = 8,
) -> list[dict[str, Any]]:
    candidates = []
    for params in params_list:
        reports = [evaluate_fixed_schedule_compact(rows, family, params, schedule) for schedule in SCHEDULES]
        aggregate = aggregate_fixed_schedules(reports)
        predicate = family.builder(params)
        all_replay = stats(selected(rows, predicate), len(rows))
        if int(all_replay.get("entries") or 0) < family.min_all_entries:
            continue
        candidates.append(
            {
                "family": family.name,
                "params": {name: value for name, value in zip(family.param_names, params)},
                "param_tuple": params,
                "all_replay": all_replay,
                "aggregate": aggregate,
            }
        )
    candidates.sort(
        key=lambda item: (
            item["aggregate"]["beat_live_schedules"],
            item["aggregate"]["positive_schedules"],
            fnum(item["aggregate"]["net_cents_min"]),
            fnum(item["aggregate"]["net_cents_median"]),
            fnum(item["aggregate"]["net_cents_sum_repeated_windows"]),
            fnum(item["all_replay"].get("net_cents")),
        ),
        reverse=True,
    )
    return candidates[:limit]


def dynamic_rollup(schedule_runs: list[dict[str, Any]]) -> dict[str, Any]:
    summaries = [run["summary"] for run in schedule_runs]
    nets = [fnum((summary.get("strategy") or {}).get("net_cents")) for summary in summaries]
    deltas = [fnum(summary.get("delta_vs_live_cents")) for summary in summaries]
    return {
        "runs": len(schedule_runs),
        "positive_runs": sum(1 for value in nets if value > 0),
        "beat_live_runs": sum(1 for value in deltas if value > 0),
        "net_cents_min": min(nets) if nets else None,
        "net_cents_median": median(nets) if nets else None,
        "net_cents_sum_repeated_windows": sum(nets),
        "delta_vs_live_cents_median": median(deltas) if deltas else None,
    }


def build_report() -> dict[str, Any]:
    rows, diagnostics = projection.load_matched_live_trades()
    rows.sort(key=lambda row: row["_entry_dt"])
    families = stress.build_families()
    dynamic_runs: dict[str, dict[str, list[dict[str, Any]]]] = {}
    dynamic_rollups: dict[str, dict[str, dict[str, Any]]] = {}
    fixed_current: dict[str, dict[str, Any]] = {}
    leaders: dict[str, list[dict[str, Any]]] = {}
    param_pool_sizes: dict[str, int] = {}

    for family in families:
        params_list = build_param_pool(rows, family)
        param_pool_sizes[family.name] = len(params_list)
        dynamic_runs[family.name] = {}
        dynamic_rollups[family.name] = {}
        for mode in SELECTION_MODES:
            runs = [run_dynamic_schedule(rows, family, params_list, schedule, mode) for schedule in SCHEDULES]
            dynamic_runs[family.name][mode] = runs
            dynamic_rollups[family.name][mode] = dynamic_rollup(runs)
        fixed_current[family.name] = fixed_current_summary(rows, family)
        leaders[family.name] = robust_fixed_leaders(rows, family, params_list)

    return {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "purpose": "Research-only multi-schedule walk-forward deepening for arXiv-inspired v28 candidate gates.",
        "diagnostics": diagnostics,
        "live_baseline": stats(rows, len(rows)),
        "schedules": [schedule.__dict__ for schedule in SCHEDULES],
        "selection_modes": list(SELECTION_MODES),
        "param_pool_sizes": param_pool_sizes,
        "fixed_current": fixed_current,
        "dynamic_walk_forward": dynamic_runs,
        "dynamic_rollups": dynamic_rollups,
        "robust_fixed_leaders": leaders,
    }


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


def pct(value: Any) -> str:
    parsed = projection.as_float(value)
    if parsed is None:
        return "n/a"
    return f"{100.0 * parsed:.1f}%"


def wl(row: dict[str, Any]) -> str:
    flats = int(row.get("flats") or 0)
    suffix = f" (+{flats} flat)" if flats else ""
    return f"{int(row.get('wins') or 0)}/{int(row.get('losses') or 0)}{suffix}"


def write_md(report: dict[str, Any]) -> None:
    lines = [
        "# arXiv Candidate Walk-Forward Deepening",
        "",
        "Research-only. Multiple walk-forward layouts are used to test whether the candidate families are flukes and to find more stable variants worth freezing forward.",
        "",
        f"- Generated UTC: `{report.get('generated_at_utc')}`",
        f"- Matched live trades: `{report.get('diagnostics', {}).get('matched_trade_count')}`",
        f"- Schedules: `{len(report.get('schedules') or [])}`",
        "",
        "## Fixed Current Params Across Schedules",
        "",
        "| family | all replay PnL | W/L | positive schedules | beat-live schedules | min sched PnL | median sched PnL | params |",
        "|---|---:|---:|---:|---:|---:|---:|---|",
    ]
    for family, payload in (report.get("fixed_current") or {}).items():
        agg = payload.get("aggregate") or {}
        all_replay = payload.get("all_replay") or {}
        lines.append(
            f"| {family} | {money(all_replay.get('net_dollars'))} | {wl(all_replay)} | "
            f"{agg.get('positive_schedules')}/{agg.get('schedules')} | {agg.get('beat_live_schedules')}/{agg.get('schedules')} | "
            f"{cents(agg.get('net_cents_min'))} | {cents(agg.get('net_cents_median'))} | "
            f"`{json.dumps(payload.get('params'), sort_keys=True)}` |"
        )
    lines.extend(
        [
            "",
            "## Dynamic Walk-Forward Selection",
            "",
            "Each fold selects params using train-only data, then scores the next window. `stable_subsplit` requires positive evidence in at least two train subwindows.",
            "",
            "| family | selection | positive runs | beat-live runs | min run PnL | median run PnL | repeated-window PnL sum | median delta vs live |",
            "|---|---|---:|---:|---:|---:|---:|---:|",
        ]
    )
    for family, modes in (report.get("dynamic_rollups") or {}).items():
        for mode, rollup in modes.items():
            lines.append(
                f"| {family} | {mode} | {rollup.get('positive_runs')}/{rollup.get('runs')} | "
                f"{rollup.get('beat_live_runs')}/{rollup.get('runs')} | {cents(rollup.get('net_cents_min'))} | "
                f"{cents(rollup.get('net_cents_median'))} | {cents(rollup.get('net_cents_sum_repeated_windows'))} | "
                f"{cents(rollup.get('delta_vs_live_cents_median'))} |"
            )
    lines.extend(
        [
            "",
            "## Best Robust Replay Variants",
            "",
            "These leaders are selected with the full retrospective stress set, so treat them as freeze candidates, not proof.",
            "",
            "| family | rank | all replay PnL | W/L | positive schedules | beat-live schedules | min sched PnL | median sched PnL | params |",
            "|---|---:|---:|---:|---:|---:|---:|---:|---|",
        ]
    )
    for family, rows in (report.get("robust_fixed_leaders") or {}).items():
        for rank, row in enumerate(rows[:5], start=1):
            agg = row.get("aggregate") or {}
            all_replay = row.get("all_replay") or {}
            lines.append(
                f"| {family} | {rank} | {money(all_replay.get('net_dollars'))} | {wl(all_replay)} | "
                f"{agg.get('positive_schedules')}/{agg.get('schedules')} | {agg.get('beat_live_schedules')}/{agg.get('schedules')} | "
                f"{cents(agg.get('net_cents_min'))} | {cents(agg.get('net_cents_median'))} | "
                f"`{json.dumps(row.get('params'), sort_keys=True)}` |"
            )
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "- `fixed current` answers whether yesterday's chosen params were a fluke under alternate walk-forward layouts.",
            "- `dynamic` answers whether train-only selection can rediscover useful params without seeing the eval window.",
            "- `robust replay variants` are useful for deciding what to freeze forward next, but they are still retrospective search results.",
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
