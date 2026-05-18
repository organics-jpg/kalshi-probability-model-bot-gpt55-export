from __future__ import annotations

import argparse
import json
import math
import random
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Sequence

from probe_rv600_cumulative_opportunity import discover_roots
from research_particle.replay_runner import ReplayConfig
from research_particle.rv600_variation_test import (
    RV600VariantRunRow,
    build_rv600_variation_report,
)


DEFAULT_BASE_DIR = Path("logs/particle_research/real_shadow")
DEFAULT_REPORTS_DIR = Path("logs/particle_research/reports")
DEFAULT_MIN_ROOT_NAME = "rv600_next_evidence_shadow_20260513T195001Z"
DEFAULT_MIN_DECISION_TS_UTC = "2026-05-13T19:50:00+00:00"
DEFAULT_OUTPUT_JSON = Path("logs/particle_research/reports/rv600_spa_benchmark_audit_latest.json")
DEFAULT_OUTPUT_MD = Path("logs/particle_research/reports/rv600_spa_benchmark_audit_latest.md")


@dataclass(frozen=True)
class CandidateArray:
    variant: str
    accounting_mode: str
    selected_pnl: tuple[float, ...]
    matched_delta: tuple[float, ...]
    matched_control: tuple[float, ...]
    entries: tuple[int, ...]
    summary: dict[str, Any]


@dataclass(frozen=True)
class CandidateSpaStats:
    variant: str
    accounting_mode: str
    total_selected_pnl_cents: float
    total_matched_v28_delta_cents: float
    total_matched_v28_control_pnl_cents: float
    accepted_entries: int
    distinct_markets: int
    avg_pnl_per_entry_cents: float
    positive_root_rate: float
    positive_market_rate: float
    max_single_market_pnl_share: float
    last_window_pnl_cents: float
    rejection_reason: str
    mean_delta_cents_per_root: float
    studentized_delta_t: float
    spa_screen_pass: bool


def build_report(args: argparse.Namespace) -> dict[str, Any]:
    roots = tuple(args.root or discover_roots(args.base_dir, args.reports_dir, args.min_root_name))
    root_names = tuple(root.name for root in roots)
    variation = build_rv600_variation_report(
        roots,
        phase="grid",
        output_json=args.output_json,
        output_md=args.output_md,
        config=ReplayConfig(min_fill_prob=0.0, counterfactual_fill_threshold=0.5),
        min_decision_ts_utc=_parse_dt(args.min_decision_ts_utc) if args.min_decision_ts_utc else None,
    )
    summaries = {
        (row.variant, str(row.accounting_mode)): asdict(row)
        for row in variation.summary_rows
    }
    root_index = {name: idx for idx, name in enumerate(root_names)}
    candidates = _candidate_arrays(
        variation.run_rows,
        root_index,
        summaries,
        min_total_entries=args.min_total_entries,
    )
    stats = [_candidate_stats(candidate, args) for candidate in candidates]
    positive_delta = [row for row in stats if row.total_matched_v28_delta_cents > 0.0]
    spa_screened = [row for row in stats if row.spa_screen_pass]
    best_delta = max(stats, key=lambda row: row.total_matched_v28_delta_cents, default=None)
    best_spa = max(stats, key=lambda row: row.studentized_delta_t, default=None)
    bootstrap = _spa_bootstrap(
        candidates,
        bootstrap_count=args.bootstrap_count,
        seed=args.seed,
        screen_poor_alternatives=args.screen_poor_alternatives,
    )
    support = (
        best_spa is not None
        and best_spa.spa_screen_pass
        and best_spa.rejection_reason == ""
        and bootstrap["studentized_p_value"] <= args.max_p_value
    )
    decision = "spa_benchmark_supports_current_grid" if support else "spa_benchmark_rejects_current_grid"
    report = {
        "schema_version": "rv600-spa-benchmark-audit-v1",
        "generated_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "research_only": True,
        "decision": decision,
        "root_count": len(root_names),
        "roots": list(root_names),
        "candidate_count": len(candidates),
        "positive_delta_candidate_count": len(positive_delta),
        "spa_screen_candidate_count": len(spa_screened),
        "best_by_spa_stat": asdict(best_spa) if best_spa else None,
        "best_by_matched_v28_delta": asdict(best_delta) if best_delta else None,
        "bootstrap": bootstrap,
        "chosen_method": {
            "name": "Hansen-style superior predictive ability benchmark audit",
            "reason": (
                "The current RV600 blocker is not raw PnL but failure to beat matched v28 "
                "after searching thousands of variants. A studentized root-block bootstrap "
                "over matched-v28 deltas tests whether any candidate has superior predictive "
                "ability versus the benchmark while screening irrelevant poor alternatives."
            ),
        },
        "sources_considered": [
            {
                "label": "selected: Hansen Superior Predictive Ability test",
                "url": "https://papers.ssrn.com/sol3/papers.cfm?abstract_id=264569",
                "reason": "Directly targets whether any searched rule beats a benchmark after multiple-comparison adjustment.",
            },
            {
                "label": "supporting: White Reality Check",
                "url": "https://www.fmg.ac.uk/publications/discussion-papers/data-snooping-technical-trading-rule-performance-and-bootstrap",
                "reason": "Existing audit already uses the max-statistic idea; SPA is more focused on benchmark superiority.",
            },
            {
                "label": "supporting: false discovery rate for trading rules",
                "url": "https://papers.ssrn.com/sol3/Delivery.cfm/SSRN_ID1095202_code517200.pdf?abstractid=1095202",
                "reason": "Reinforces treating apparent winners as possible data-snooping discoveries after transaction costs.",
            },
            {
                "label": "supporting: Bayesian backtest overfitting",
                "url": "https://www.mdpi.com/2227-9091/9/1/18",
                "reason": "Motivates estimating whether the selected best strategy is likely a true discovery.",
            },
            {
                "label": "not selected: hierarchical partial pooling",
                "url": "https://mc-stan.org/rstanarm/articles/pooling.html",
                "reason": "Useful for shrinkage, but less direct than a matched-v28 superior-predictive-ability test.",
            },
        ],
        "thresholds": {
            "min_total_entries": args.min_total_entries,
            "min_selected_pnl_cents": args.min_selected_pnl_cents,
            "min_matched_delta_cents": args.min_matched_delta_cents,
            "min_positive_root_rate": args.min_positive_root_rate,
            "min_positive_market_rate": args.min_positive_market_rate,
            "max_p_value": args.max_p_value,
            "bootstrap_count": args.bootstrap_count,
            "screen_poor_alternatives": args.screen_poor_alternatives,
        },
        "inputs": {
            "base_dir": str(args.base_dir),
            "reports_dir": str(args.reports_dir),
            "min_root_name": args.min_root_name,
            "min_decision_ts_utc": args.min_decision_ts_utc,
            "seed": args.seed,
        },
    }
    return report


def _candidate_arrays(
    rows: Sequence[RV600VariantRunRow],
    root_index: dict[str, int],
    summaries: dict[tuple[str, str], dict[str, Any]],
    *,
    min_total_entries: int,
) -> list[CandidateArray]:
    grouped: dict[tuple[str, str], dict[str, list[float] | list[int]]] = {}
    root_count = len(root_index)
    for row in rows:
        key = (row.variant, str(row.accounting_mode))
        if key not in grouped:
            grouped[key] = {
                "selected_pnl": [0.0] * root_count,
                "matched_delta": [0.0] * root_count,
                "matched_control": [0.0] * root_count,
                "entries": [0] * root_count,
            }
        idx = root_index[row.root_name]
        grouped[key]["selected_pnl"][idx] += float(row.selected_pnl_cents)  # type: ignore[index]
        grouped[key]["matched_delta"][idx] += float(row.matched_v28_delta_cents)  # type: ignore[index]
        grouped[key]["matched_control"][idx] += float(row.matched_v28_control_pnl_cents)  # type: ignore[index]
        grouped[key]["entries"][idx] += int(row.accepted_entries)  # type: ignore[index]

    candidates: list[CandidateArray] = []
    for key, values in grouped.items():
        entries = tuple(int(value) for value in values["entries"])
        if sum(entries) < min_total_entries:
            continue
        candidates.append(
            CandidateArray(
                variant=key[0],
                accounting_mode=key[1],
                selected_pnl=tuple(float(value) for value in values["selected_pnl"]),
                matched_delta=tuple(float(value) for value in values["matched_delta"]),
                matched_control=tuple(float(value) for value in values["matched_control"]),
                entries=entries,
                summary=summaries.get(key, {}),
            )
        )
    return candidates


def _candidate_stats(candidate: CandidateArray, args: argparse.Namespace) -> CandidateSpaStats:
    summary = candidate.summary
    total_delta = sum(candidate.matched_delta)
    total_selected = sum(candidate.selected_pnl)
    total_control = sum(candidate.matched_control)
    std_delta = _sample_std(candidate.matched_delta)
    mean_delta = total_delta / len(candidate.matched_delta) if candidate.matched_delta else 0.0
    t_stat = (math.sqrt(len(candidate.matched_delta)) * mean_delta / std_delta) if std_delta > 0.0 else 0.0
    positive_root_rate = float(summary.get("positive_root_rate") or 0.0)
    positive_market_rate = float(summary.get("positive_market_rate") or 0.0)
    spa_screen_pass = (
        total_selected >= args.min_selected_pnl_cents
        and total_delta >= args.min_matched_delta_cents
        and positive_root_rate >= args.min_positive_root_rate
        and positive_market_rate >= args.min_positive_market_rate
    )
    return CandidateSpaStats(
        variant=candidate.variant,
        accounting_mode=candidate.accounting_mode,
        total_selected_pnl_cents=total_selected,
        total_matched_v28_delta_cents=total_delta,
        total_matched_v28_control_pnl_cents=total_control,
        accepted_entries=sum(candidate.entries),
        distinct_markets=int(summary.get("distinct_markets") or 0),
        avg_pnl_per_entry_cents=float(summary.get("avg_pnl_per_entry_cents") or 0.0),
        positive_root_rate=positive_root_rate,
        positive_market_rate=positive_market_rate,
        max_single_market_pnl_share=float(summary.get("max_single_market_pnl_share") or 0.0),
        last_window_pnl_cents=float(summary.get("last_window_pnl_cents") or 0.0),
        rejection_reason=str(summary.get("rejection_reason") or ""),
        mean_delta_cents_per_root=mean_delta,
        studentized_delta_t=t_stat,
        spa_screen_pass=spa_screen_pass,
    )


def _spa_bootstrap(
    candidates: Sequence[CandidateArray],
    *,
    bootstrap_count: int,
    seed: int,
    screen_poor_alternatives: bool,
) -> dict[str, Any]:
    if not candidates:
        return {
            "observed_studentized_max": 0.0,
            "studentized_p_value": 1.0,
            "bootstrap_count": bootstrap_count,
            "exceedance_count": bootstrap_count,
            "bootstrap_candidate_count": 0,
        }
    values_by_candidate = [tuple(float(value) for value in candidate.matched_delta) for candidate in candidates]
    root_count = len(values_by_candidate[0])
    sqrt_n = math.sqrt(root_count)
    means = [_mean(values) for values in values_by_candidate]
    stds = [_sample_std(values) for values in values_by_candidate]
    candidate_indices = [
        idx
        for idx, mean in enumerate(means)
        if (not screen_poor_alternatives or mean > 0.0 or idx == max(range(len(means)), key=lambda item: means[item]))
    ]
    observed_stats = [
        (sqrt_n * means[idx] / stds[idx]) if stds[idx] > 0.0 else 0.0
        for idx in candidate_indices
    ]
    observed_max = max(observed_stats, default=0.0)
    centered = [
        tuple(value - means[idx] for value in values_by_candidate[idx])
        for idx in range(len(values_by_candidate))
    ]
    rng = random.Random(seed)
    exceedance_count = 0
    for _ in range(bootstrap_count):
        counts = [0] * root_count
        for _sample in range(root_count):
            counts[rng.randrange(root_count)] += 1
        max_boot = -math.inf
        for idx in candidate_indices:
            boot_sum = 0.0
            for root_idx, count in enumerate(counts):
                if count:
                    boot_sum += centered[idx][root_idx] * count
            boot_mean = boot_sum / root_count
            std = stds[idx]
            boot_stat = (sqrt_n * boot_mean / std) if std > 0.0 else 0.0
            max_boot = max(max_boot, boot_stat)
        if max_boot >= observed_max:
            exceedance_count += 1
    return {
        "observed_studentized_max": observed_max,
        "studentized_p_value": (exceedance_count + 1) / (bootstrap_count + 1),
        "bootstrap_count": bootstrap_count,
        "exceedance_count": exceedance_count,
        "bootstrap_candidate_count": len(candidate_indices),
    }


def _mean(values: Sequence[float]) -> float:
    return float(sum(values) / len(values)) if values else 0.0


def _sample_std(values: Sequence[float]) -> float:
    if len(values) < 2:
        return 0.0
    mean = _mean(values)
    variance = sum((value - mean) ** 2 for value in values) / (len(values) - 1)
    return math.sqrt(max(0.0, variance))


def _parse_dt(value: str) -> datetime:
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def _markdown(report: dict[str, Any]) -> str:
    best_spa = report.get("best_by_spa_stat") or {}
    best_delta = report.get("best_by_matched_v28_delta") or {}
    bootstrap = report.get("bootstrap") or {}
    lines = [
        "# RV600 SPA Benchmark Audit",
        "",
        f"- generated_utc: {report['generated_utc']}",
        f"- research_only: {report['research_only']}",
        f"- decision: {report['decision']}",
        f"- root_count: {report['root_count']}",
        f"- candidate_count: {report['candidate_count']}",
        f"- positive_delta_candidate_count: {report['positive_delta_candidate_count']}",
        f"- spa_screen_candidate_count: {report['spa_screen_candidate_count']}",
        "",
        "## Best By SPA Statistic",
        "",
        f"- variant: `{best_spa.get('variant')}`",
        f"- accounting_mode: `{best_spa.get('accounting_mode')}`",
        f"- selected_pnl_cents: {best_spa.get('total_selected_pnl_cents')}",
        f"- matched_v28_delta_cents: {best_spa.get('total_matched_v28_delta_cents')}",
        f"- accepted_entries: {best_spa.get('accepted_entries')}",
        f"- positive_root_rate: {best_spa.get('positive_root_rate')}",
        f"- positive_market_rate: {best_spa.get('positive_market_rate')}",
        f"- studentized_delta_t: {best_spa.get('studentized_delta_t')}",
        f"- spa_screen_pass: {best_spa.get('spa_screen_pass')}",
        f"- rejection_reason: `{best_spa.get('rejection_reason')}`",
        "",
        "## Best By Matched-v28 Delta",
        "",
        f"- variant: `{best_delta.get('variant')}`",
        f"- accounting_mode: `{best_delta.get('accounting_mode')}`",
        f"- selected_pnl_cents: {best_delta.get('total_selected_pnl_cents')}",
        f"- matched_v28_delta_cents: {best_delta.get('total_matched_v28_delta_cents')}",
        f"- rejection_reason: `{best_delta.get('rejection_reason')}`",
        "",
        "## Bootstrap",
        "",
        f"- studentized_p_value: {bootstrap.get('studentized_p_value')}",
        f"- observed_studentized_max: {bootstrap.get('observed_studentized_max')}",
        f"- bootstrap_candidate_count: {bootstrap.get('bootstrap_candidate_count')}",
        f"- bootstrap_count: {bootstrap.get('bootstrap_count')}",
        "",
        "## Chosen Method",
        "",
        report["chosen_method"]["reason"],
        "",
        "## Sources Considered",
        "",
    ]
    for row in report["sources_considered"]:
        lines.append(f"- {row['label']}: [{row['url']}]({row['url']}) - {row['reason']}")
    lines.append("")
    return "\n".join(lines)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Hansen-style SPA benchmark audit for RV600 vs matched v28.")
    parser.add_argument("--root", action="append", type=Path, default=[])
    parser.add_argument("--base-dir", type=Path, default=DEFAULT_BASE_DIR)
    parser.add_argument("--reports-dir", type=Path, default=DEFAULT_REPORTS_DIR)
    parser.add_argument("--min-root-name", default=DEFAULT_MIN_ROOT_NAME)
    parser.add_argument("--min-decision-ts-utc", default=DEFAULT_MIN_DECISION_TS_UTC)
    parser.add_argument("--min-total-entries", type=int, default=25)
    parser.add_argument("--min-selected-pnl-cents", type=float, default=0.0)
    parser.add_argument("--min-matched-delta-cents", type=float, default=1.0)
    parser.add_argument("--min-positive-root-rate", type=float, default=0.60)
    parser.add_argument("--min-positive-market-rate", type=float, default=0.60)
    parser.add_argument("--bootstrap-count", type=int, default=1000)
    parser.add_argument("--seed", type=int, default=901)
    parser.add_argument("--max-p-value", type=float, default=0.05)
    parser.add_argument("--screen-poor-alternatives", action=argparse.BooleanOptionalAction, default=True)
    parser.add_argument("--output-json", type=Path, default=DEFAULT_OUTPUT_JSON)
    parser.add_argument("--output-md", type=Path, default=DEFAULT_OUTPUT_MD)
    parser.add_argument("--write", action="store_true")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    report = build_report(args)
    if args.write:
        args.output_json.parent.mkdir(parents=True, exist_ok=True)
        args.output_json.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        args.output_md.write_text(_markdown(report), encoding="utf-8")
    best = report.get("best_by_spa_stat") or {}
    bootstrap = report.get("bootstrap") or {}
    print(f"decision={report['decision']}")
    print(f"root_count={report['root_count']}")
    print(f"candidate_count={report['candidate_count']}")
    print(f"positive_delta_candidate_count={report['positive_delta_candidate_count']}")
    print(f"spa_screen_candidate_count={report['spa_screen_candidate_count']}")
    print(f"best_spa_variant={best.get('variant')}")
    print(f"best_spa_delta_cents={best.get('total_matched_v28_delta_cents')}")
    print(f"studentized_p_value={bootstrap.get('studentized_p_value')}")
    if args.write:
        print(f"output_json={args.output_json}")
        print(f"output_md={args.output_md}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
