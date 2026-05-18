from __future__ import annotations

import argparse
import itertools
import json
import math
import random
from collections import Counter, defaultdict
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
DEFAULT_OUTPUT_JSON = Path("logs/particle_research/reports/rv600_stability_selection_rescue_latest.json")
DEFAULT_OUTPUT_MD = Path("logs/particle_research/reports/rv600_stability_selection_rescue_latest.md")


SOURCES_CONSIDERED = [
    {
        "method": "stability_selection",
        "source": "Meinshausen and Buehlmann, Stability Selection",
        "source_url": "https://arxiv.org/abs/0809.2932",
        "decision": "chosen",
        "fit": "Directly tests whether a candidate remains selected across many root subsamples.",
    },
    {
        "method": "superior_predictive_ability",
        "source": "Hansen, A Test for Superior Predictive Ability",
        "source_url": "https://papers.ssrn.com/sol3/papers.cfm?abstract_id=264569",
        "decision": "not_selected",
        "fit": "Useful for data-snooping-adjusted existence tests, but less direct for selecting one simple forward-shadow candidate.",
    },
    {
        "method": "deflated_sharpe_ratio",
        "source": "Bailey and Lopez de Prado, The Deflated Sharpe Ratio",
        "source_url": "https://papers.ssrn.com/sol3/Delivery.cfm/SSRN_ID2460551_code87814.pdf?abstractid=2460551&mirid=1",
        "decision": "not_selected",
        "fit": "Sharpe-style selection-bias correction is less natural than per-entry/root accounting for binary settlement trades.",
    },
    {
        "method": "pbo_cscv",
        "source": "Bailey, Borwein, Lopez de Prado, and Zhu, The Probability of Backtest Overfitting",
        "source_url": "https://www.carmamaths.org/resources/jon/backtest2.pdf",
        "decision": "already_tested",
        "fit": "Already implemented as the split-rank PBO audit; current grid was rejected there.",
    },
    {
        "method": "empirical_bernstein_lcb",
        "source": "Maurer and Pontil, Empirical Bernstein Bounds and Sample Variance Penalization",
        "source_url": "https://arxiv.org/abs/0907.3740",
        "decision": "deferred",
        "fit": "A lower-confidence-bound selector is plausible, but current root count is small enough that bounds are likely vacuous.",
    },
]


@dataclass(frozen=True)
class CandidateAggregate:
    variant: str
    accounting_mode: str
    gate_count: int
    root_count: int
    accepted_entries: int
    distinct_markets: int
    selected_pnl_cents: float
    no_fill_penalty_pnl_cents: float
    matched_v28_control_pnl_cents: float
    matched_v28_delta_cents: float
    avg_pnl_per_entry_cents: float
    avg_pnl_per_market_cents: float
    positive_root_rate: float
    positive_market_rate: float
    max_single_market_pnl_share: float
    last_window_pnl_cents: float
    train_gate_pass: bool
    rejection_reason: str


@dataclass(frozen=True)
class SplitRow:
    split_index: int
    train_root_count: int
    test_root_count: int
    selection_basis: str
    selected_variant: str
    selected_accounting_mode: str
    train_gate_pass: bool
    train_selected_pnl_cents: float
    train_accepted_entries: int
    train_positive_root_rate: float
    train_positive_market_rate: float
    train_rejection_reason: str
    test_selected_pnl_cents: float
    test_matched_v28_control_pnl_cents: float
    test_matched_v28_delta_cents: float
    test_accepted_entries: int
    test_avg_pnl_per_entry_cents: float


def build_report(args: argparse.Namespace) -> dict[str, Any]:
    roots = tuple(args.root or discover_roots(args.base_dir, args.reports_dir, args.min_root_name))
    root_names = tuple(root.name for root in roots)
    variation = build_rv600_variation_report(
        roots,
        phase="grid",
        output_json=args.output_json,
        output_md=args.output_md,
        config=ReplayConfig(min_fill_prob=0.0, counterfactual_fill_threshold=0.5),
    )
    root_index = {name: idx for idx, name in enumerate(root_names)}
    candidates = _candidate_arrays(variation.run_rows, root_index)
    splits = _balanced_splits(len(root_names), max_splits=args.max_splits, seed=args.seed)
    split_rows: list[SplitRow] = []
    skipped = 0
    selected_counts: Counter[str] = Counter()
    diagnostic_counts: Counter[str] = Counter()
    for split_index, train_indices in enumerate(splits):
        train_indices = tuple(train_indices)
        test_indices = tuple(idx for idx in range(len(root_names)) if idx not in set(train_indices))
        scaled_min_entries = max(1, math.ceil(args.full_min_entries * len(train_indices) / max(1, len(root_names))))
        selected = _select_candidate(
            candidates,
            train_indices,
            min_entries=scaled_min_entries,
            full_min_entries=args.full_min_entries,
            min_positive_rate=args.min_positive_rate,
        )
        if selected is None:
            skipped += 1
            continue
        train_agg, basis = selected
        key = f"{train_agg.variant}|{train_agg.accounting_mode}"
        if basis == "train_gate_pass":
            selected_counts[key] += 1
        else:
            diagnostic_counts[key] += 1
        test_agg = _aggregate_candidate(
            candidates[(train_agg.variant, train_agg.accounting_mode)],
            test_indices,
            min_entries=1,
            full_min_entries=args.full_min_entries,
            min_positive_rate=args.min_positive_rate,
        )
        split_rows.append(
            SplitRow(
                split_index=split_index,
                train_root_count=len(train_indices),
                test_root_count=len(test_indices),
                selection_basis=basis,
                selected_variant=train_agg.variant,
                selected_accounting_mode=train_agg.accounting_mode,
                train_gate_pass=train_agg.train_gate_pass,
                train_selected_pnl_cents=train_agg.selected_pnl_cents,
                train_accepted_entries=train_agg.accepted_entries,
                train_positive_root_rate=train_agg.positive_root_rate,
                train_positive_market_rate=train_agg.positive_market_rate,
                train_rejection_reason=train_agg.rejection_reason,
                test_selected_pnl_cents=test_agg.selected_pnl_cents,
                test_matched_v28_control_pnl_cents=test_agg.matched_v28_control_pnl_cents,
                test_matched_v28_delta_cents=test_agg.matched_v28_delta_cents,
                test_accepted_entries=test_agg.accepted_entries,
                test_avg_pnl_per_entry_cents=test_agg.avg_pnl_per_entry_cents,
            )
        )

    full_rows = [
        _aggregate_candidate(
            candidate,
            tuple(range(len(root_names))),
            min_entries=args.full_min_entries,
            full_min_entries=args.full_min_entries,
            min_positive_rate=args.min_positive_rate,
        )
        for candidate in candidates.values()
    ]
    full_support_rows = [row for row in full_rows if row.train_gate_pass]
    best_full_diagnostic = max(full_rows, key=_diagnostic_score, default=None)
    locked_selection_count = sum(1 for row in split_rows if row.selection_basis == "train_gate_pass")
    valid_split_count = len(split_rows)
    top_selected = _selection_rows(selected_counts, valid_split_count)
    top_diagnostic = _selection_rows(diagnostic_counts, valid_split_count)
    selected_tests = [row for row in split_rows if row.selection_basis == "train_gate_pass"]
    total_entries = sum(row.test_accepted_entries for row in selected_tests)
    total_pnl = sum(row.test_selected_pnl_cents for row in selected_tests)
    total_matched = sum(row.test_matched_v28_control_pnl_cents for row in selected_tests)
    positive_test_rate = (
        sum(1 for row in selected_tests if row.test_selected_pnl_cents > 0.0) / len(selected_tests)
        if selected_tests
        else 0.0
    )
    top_selection_rate = top_selected[0]["selection_rate"] if top_selected else 0.0
    aggregate_gate_pass = (
        bool(full_support_rows)
        and locked_selection_count > 0
        and top_selection_rate >= args.min_selection_rate
        and total_entries >= args.full_min_entries
        and total_pnl > 0.0
        and _beats_matched(total_pnl, total_matched)
        and (total_pnl / total_entries if total_entries else 0.0) >= args.min_avg_entry_cents
        and positive_test_rate >= args.min_positive_rate
    )
    decision = "stability_selection_support_found" if aggregate_gate_pass else "stability_selection_rescue_failed"
    report = {
        "schema_version": "rv600-stability-selection-rescue-v1",
        "generated_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "research_only": True,
        "decision": decision,
        "method_choice": (
            "Stability selection over existing RV600 grid candidates. Each split selects only from "
            "simple non-all-entries candidates that pass scaled prior-root gates; diagnostics are "
            "reported separately and are not promotable."
        ),
        "sources_considered": SOURCES_CONSIDERED,
        "roots": list(root_names),
        "root_count": len(root_names),
        "candidate_count": len(candidates),
        "split_count": len(splits),
        "valid_split_count": valid_split_count,
        "skipped_split_count": skipped,
        "locked_selection_count": locked_selection_count,
        "diagnostic_selection_count": valid_split_count - locked_selection_count,
        "top_selected_candidates": top_selected,
        "top_diagnostic_candidates": top_diagnostic,
        "full_support_count": len(full_support_rows),
        "best_full_support": asdict(max(full_support_rows, key=_diagnostic_score)) if full_support_rows else None,
        "best_full_diagnostic": asdict(best_full_diagnostic) if best_full_diagnostic else None,
        "selected_test_aggregate": {
            "test_total_entries": total_entries,
            "test_selected_pnl_cents": total_pnl,
            "test_matched_v28_control_pnl_cents": total_matched,
            "test_matched_v28_delta_cents": total_pnl - total_matched,
            "test_avg_pnl_per_entry_cents": total_pnl / total_entries if total_entries else 0.0,
            "positive_test_split_rate": positive_test_rate,
            "preliminary_gate_pass": aggregate_gate_pass,
            "rejection_reason": _aggregate_rejection(
                aggregate_gate_pass,
                len(full_support_rows),
                locked_selection_count,
                top_selection_rate,
                total_entries,
                total_pnl,
                total_matched,
                positive_test_rate,
                args,
            ),
        },
        "sample_split_rows": [asdict(row) for row in split_rows[: args.sample_split_rows]],
        "thresholds": {
            "full_min_entries": args.full_min_entries,
            "min_avg_entry_cents": args.min_avg_entry_cents,
            "min_positive_rate": args.min_positive_rate,
            "min_selection_rate": args.min_selection_rate,
            "max_splits": args.max_splits,
            "seed": args.seed,
        },
        "inputs": {
            "base_dir": str(args.base_dir),
            "reports_dir": str(args.reports_dir),
            "min_root_name": args.min_root_name,
        },
    }
    return report


def _candidate_arrays(
    run_rows: Sequence[RV600VariantRunRow],
    root_index: dict[str, int],
) -> dict[tuple[str, str], dict[str, Any]]:
    root_count = len(root_index)
    candidates: dict[tuple[str, str], dict[str, Any]] = {}
    for row in run_rows:
        if row.accounting_mode == "all_entries":
            continue
        if row.gate_count > 3:
            continue
        if row.variant.startswith("v28_primary_"):
            continue
        key = (row.variant, row.accounting_mode)
        candidate = candidates.setdefault(
            key,
            {
                "variant": row.variant,
                "accounting_mode": row.accounting_mode,
                "gate_count": int(row.gate_count),
                "entries": [0] * root_count,
                "markets": [0] * root_count,
                "pnl": [0.0] * root_count,
                "no_fill_pnl": [0.0] * root_count,
                "matched": [0.0] * root_count,
                "positive_market_numer": [0.0] * root_count,
                "max_market_contribution": [0.0] * root_count,
                "last_window": [0.0] * root_count,
            },
        )
        idx = root_index[row.root_name]
        candidate["entries"][idx] += int(row.accepted_entries)
        candidate["markets"][idx] += int(row.distinct_markets)
        candidate["pnl"][idx] += float(row.selected_pnl_cents)
        candidate["no_fill_pnl"][idx] += float(row.no_fill_penalty_pnl_cents)
        candidate["matched"][idx] += float(row.matched_v28_control_pnl_cents)
        candidate["positive_market_numer"][idx] += float(row.positive_market_rate) * int(row.distinct_markets)
        if row.selected_pnl_cents > 0.0:
            candidate["max_market_contribution"][idx] = max(
                candidate["max_market_contribution"][idx],
                float(row.max_single_market_pnl_share) * float(row.selected_pnl_cents),
            )
        candidate["last_window"][idx] = float(row.last_window_pnl_cents)
    return candidates


def _aggregate_candidate(
    candidate: dict[str, Any],
    indices: Sequence[int],
    *,
    min_entries: int,
    full_min_entries: int,
    min_positive_rate: float,
) -> CandidateAggregate:
    entries = sum(candidate["entries"][idx] for idx in indices)
    markets = sum(candidate["markets"][idx] for idx in indices)
    pnl = sum(candidate["pnl"][idx] for idx in indices)
    no_fill_pnl = sum(candidate["no_fill_pnl"][idx] for idx in indices)
    matched = sum(candidate["matched"][idx] for idx in indices)
    positive_roots = sum(1 for idx in indices if candidate["pnl"][idx] > 0.0)
    positive_market_numer = sum(candidate["positive_market_numer"][idx] for idx in indices)
    max_market_contribution = max((candidate["max_market_contribution"][idx] for idx in indices), default=0.0)
    max_share = max_market_contribution / pnl if pnl > 0.0 else 0.0
    last_index = max(indices) if indices else -1
    last_window = candidate["last_window"][last_index] if last_index >= 0 else 0.0
    avg_entry = pnl / entries if entries else 0.0
    avg_market = pnl / markets if markets else 0.0
    positive_root_rate = positive_roots / len(indices) if indices else 0.0
    positive_market_rate = positive_market_numer / markets if markets else 0.0
    rejection = _rejection_reason(
        accounting_mode=candidate["accounting_mode"],
        gate_count=candidate["gate_count"],
        accepted_entries=entries,
        min_entries=min_entries,
        full_min_entries=full_min_entries,
        selected_pnl=pnl,
        no_fill_pnl=no_fill_pnl,
        matched_v28=matched,
        avg_entry=avg_entry,
        positive_root_rate=positive_root_rate,
        positive_market_rate=positive_market_rate,
        max_share=max_share,
        last_window=last_window,
        min_positive_rate=min_positive_rate,
    )
    return CandidateAggregate(
        variant=str(candidate["variant"]),
        accounting_mode=str(candidate["accounting_mode"]),
        gate_count=int(candidate["gate_count"]),
        root_count=len(indices),
        accepted_entries=entries,
        distinct_markets=markets,
        selected_pnl_cents=pnl,
        no_fill_penalty_pnl_cents=no_fill_pnl,
        matched_v28_control_pnl_cents=matched,
        matched_v28_delta_cents=pnl - matched,
        avg_pnl_per_entry_cents=avg_entry,
        avg_pnl_per_market_cents=avg_market,
        positive_root_rate=positive_root_rate,
        positive_market_rate=positive_market_rate,
        max_single_market_pnl_share=max_share,
        last_window_pnl_cents=last_window,
        train_gate_pass=(rejection == ""),
        rejection_reason=rejection,
    )


def _select_candidate(
    candidates: dict[tuple[str, str], dict[str, Any]],
    train_indices: Sequence[int],
    *,
    min_entries: int,
    full_min_entries: int,
    min_positive_rate: float,
) -> tuple[CandidateAggregate, str] | None:
    aggregates = [
        _aggregate_candidate(
            candidate,
            train_indices,
            min_entries=min_entries,
            full_min_entries=full_min_entries,
            min_positive_rate=min_positive_rate,
        )
        for candidate in candidates.values()
    ]
    passing = [row for row in aggregates if row.train_gate_pass]
    if passing:
        return max(passing, key=_selection_score), "train_gate_pass"
    diagnostic = max(aggregates, key=_diagnostic_score, default=None)
    if diagnostic is None:
        return None
    return diagnostic, "diagnostic_nearest_train"


def _selection_score(row: CandidateAggregate) -> tuple[float, float, int]:
    return (row.selected_pnl_cents, row.matched_v28_delta_cents, row.accepted_entries)


def _diagnostic_score(row: CandidateAggregate) -> tuple[float, float, float, float, float, float, int]:
    return (
        min(row.positive_root_rate, 0.60),
        min(row.positive_market_rate, 0.60),
        min(row.avg_pnl_per_entry_cents / 10.0, 1.0),
        1.0 if row.max_single_market_pnl_share <= 0.25 else 0.25 / max(row.max_single_market_pnl_share, 1e-9),
        1.0 if _beats_matched(row.selected_pnl_cents, row.matched_v28_control_pnl_cents) else 0.0,
        row.selected_pnl_cents,
        row.accepted_entries,
    )


def _rejection_reason(
    *,
    accounting_mode: str,
    gate_count: int,
    accepted_entries: int,
    min_entries: int,
    full_min_entries: int,
    selected_pnl: float,
    no_fill_pnl: float,
    matched_v28: float,
    avg_entry: float,
    positive_root_rate: float,
    positive_market_rate: float,
    max_share: float,
    last_window: float,
    min_positive_rate: float,
) -> str:
    reasons: list[str] = []
    if accounting_mode == "all_entries":
        reasons.append("all_entries_not_promotable")
    if gate_count > 3:
        reasons.append("gate_count_above_3")
    if accepted_entries < min_entries:
        reasons.append("fewer_than_scaled_entries")
    if selected_pnl <= 0.0:
        reasons.append("nonpositive_pnl")
    if avg_entry < 10.0:
        reasons.append("avg_entry_below_10c")
    if positive_root_rate < min_positive_rate:
        reasons.append("positive_roots_below_60pct")
    if positive_market_rate < min_positive_rate:
        reasons.append("positive_markets_below_60pct")
    if max_share > 0.25:
        reasons.append("single_market_share_above_25pct")
    if last_window <= 0.0:
        reasons.append("last_window_nonpositive")
    if not _beats_matched(selected_pnl, matched_v28):
        reasons.append("does_not_beat_matched_v28_by_20pct")
    if no_fill_pnl <= 0.0:
        reasons.append("no_fill_penalty_nonpositive")
    return ";".join(reasons)


def _beats_matched(selected_pnl: float, matched_pnl: float) -> bool:
    if matched_pnl <= 0.0:
        return selected_pnl > matched_pnl
    return selected_pnl >= 1.20 * matched_pnl


def _balanced_splits(root_count: int, *, max_splits: int, seed: int) -> list[tuple[int, ...]]:
    train_size = root_count // 2
    if root_count <= 0 or train_size <= 0:
        return []
    combinations = itertools.combinations(range(root_count), train_size)
    if root_count <= 18:
        return list(combinations)[:max_splits]
    rng = random.Random(seed)
    seen: set[tuple[int, ...]] = set()
    splits: list[tuple[int, ...]] = []
    while len(splits) < max_splits:
        split = tuple(sorted(rng.sample(range(root_count), train_size)))
        if split in seen:
            continue
        seen.add(split)
        splits.append(split)
    return splits


def _selection_rows(counter: Counter[str], denominator: int) -> list[dict[str, Any]]:
    return [
        {
            "candidate": key,
            "selection_count": count,
            "selection_rate": count / denominator if denominator else 0.0,
        }
        for key, count in counter.most_common(10)
    ]


def _aggregate_rejection(
    gate_pass: bool,
    full_support_count: int,
    locked_selection_count: int,
    top_selection_rate: float,
    total_entries: int,
    total_pnl: float,
    total_matched: float,
    positive_test_rate: float,
    args: argparse.Namespace,
) -> str:
    if gate_pass:
        return ""
    reasons: list[str] = []
    if full_support_count <= 0:
        reasons.append("no_full_sample_support_row")
    if locked_selection_count <= 0:
        reasons.append("no_train_gate_selections")
    if top_selection_rate < args.min_selection_rate:
        reasons.append("selection_rate_below_threshold")
    if total_entries < args.full_min_entries:
        reasons.append("fewer_than_full_min_test_entries")
    if total_pnl <= 0.0:
        reasons.append("nonpositive_selected_test_pnl")
    if not _beats_matched(total_pnl, total_matched):
        reasons.append("does_not_beat_matched_v28_by_20pct")
    if total_entries and total_pnl / total_entries < args.min_avg_entry_cents:
        reasons.append("avg_test_entry_below_10c")
    if positive_test_rate < args.min_positive_rate:
        reasons.append("positive_test_splits_below_60pct")
    return ";".join(reasons)


def _markdown(report: dict[str, Any]) -> str:
    agg = report["selected_test_aggregate"]
    lines = [
        "# RV600 Stability Selection Rescue",
        "",
        f"- generated_utc: {report['generated_utc']}",
        f"- research_only: {report['research_only']}",
        f"- decision: {report['decision']}",
        f"- root_count: {report['root_count']}",
        f"- candidate_count: {report['candidate_count']}",
        f"- split_count: {report['split_count']}",
        f"- locked_selection_count: {report['locked_selection_count']}",
        f"- full_support_count: {report['full_support_count']}",
        f"- test_total_entries: {agg['test_total_entries']}",
        f"- test_selected_pnl_cents: {agg['test_selected_pnl_cents']:.1f}",
        f"- test_matched_v28_delta_cents: {agg['test_matched_v28_delta_cents']:.1f}",
        f"- test_avg_pnl_per_entry_cents: {agg['test_avg_pnl_per_entry_cents']:.4f}",
        f"- preliminary_gate_pass: {agg['preliminary_gate_pass']}",
        f"- rejection_reason: {agg['rejection_reason']}",
        "",
        "## Modeling Choice",
        "",
        "| method | decision | source | fit |",
        "|---|---|---|---|",
    ]
    for source in report["sources_considered"]:
        lines.append(
            f"| `{source['method']}` | {source['decision']} | [{source['source']}]({source['source_url']}) | {source['fit']} |"
        )
    lines.extend(["", "## Top Stable Selections", ""])
    if report["top_selected_candidates"]:
        lines.extend(["| candidate | count | rate |", "|---|---:|---:|"])
        for row in report["top_selected_candidates"]:
            lines.append(f"| `{row['candidate']}` | {row['selection_count']} | {row['selection_rate']:.4f} |")
    else:
        lines.append("No split produced a gate-passing train selection.")
    lines.extend(["", "## Best Full Diagnostic", ""])
    best = report["best_full_diagnostic"]
    if best:
        lines.extend(
            [
                f"- variant: `{best['variant']}`",
                f"- accounting_mode: `{best['accounting_mode']}`",
                f"- entries: {best['accepted_entries']}",
                f"- selected_pnl_cents: {best['selected_pnl_cents']:.1f}",
                f"- matched_v28_delta_cents: {best['matched_v28_delta_cents']:.1f}",
                f"- avg_pnl_per_entry_cents: {best['avg_pnl_per_entry_cents']:.4f}",
                f"- positive_root_rate: {best['positive_root_rate']:.4f}",
                f"- positive_market_rate: {best['positive_market_rate']:.4f}",
                f"- max_single_market_pnl_share: {best['max_single_market_pnl_share']:.4f}",
                f"- rejection_reason: {best['rejection_reason']}",
            ]
        )
    lines.append("")
    return "\n".join(lines)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Research-only RV600 stability-selection rescue probe.")
    parser.add_argument("--root", action="append", type=Path, default=[])
    parser.add_argument("--base-dir", type=Path, default=DEFAULT_BASE_DIR)
    parser.add_argument("--reports-dir", type=Path, default=DEFAULT_REPORTS_DIR)
    parser.add_argument("--min-root-name", default=DEFAULT_MIN_ROOT_NAME)
    parser.add_argument("--output-json", type=Path, default=DEFAULT_OUTPUT_JSON)
    parser.add_argument("--output-md", type=Path, default=DEFAULT_OUTPUT_MD)
    parser.add_argument("--full-min-entries", type=int, default=25)
    parser.add_argument("--min-avg-entry-cents", type=float, default=10.0)
    parser.add_argument("--min-positive-rate", type=float, default=0.60)
    parser.add_argument("--min-selection-rate", type=float, default=0.60)
    parser.add_argument("--max-splits", type=int, default=512)
    parser.add_argument("--seed", type=int, default=600)
    parser.add_argument("--sample-split-rows", type=int, default=25)
    parser.add_argument("--write", action="store_true")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    report = build_report(args)
    markdown = _markdown(report)
    if args.write:
        args.output_json.parent.mkdir(parents=True, exist_ok=True)
        args.output_json.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        args.output_md.write_text(markdown, encoding="utf-8")
    agg = report["selected_test_aggregate"]
    print(f"decision={report['decision']}")
    print(f"root_count={report['root_count']}")
    print(f"candidate_count={report['candidate_count']}")
    print(f"locked_selection_count={report['locked_selection_count']}")
    print(f"full_support_count={report['full_support_count']}")
    print(f"test_selected_pnl_cents={agg['test_selected_pnl_cents']:.1f}")
    print(f"rejection_reason={agg['rejection_reason']}")
    print(f"output_json={args.output_json}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
