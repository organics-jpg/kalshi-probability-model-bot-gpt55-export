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
DEFAULT_MIN_DECISION_TS_UTC = "2026-05-13T19:50:00+00:00"
DEFAULT_OUTPUT_JSON = Path("logs/particle_research/reports/rv600_pbo_stability_audit_latest.json")
DEFAULT_OUTPUT_MD = Path("logs/particle_research/reports/rv600_pbo_stability_audit_latest.md")


@dataclass(frozen=True)
class CandidateSplitStats:
    variant: str
    accounting_mode: str
    train_pnl_cents: float
    train_entries: int
    test_pnl_cents: float
    test_entries: int
    test_rank_percentile: float
    test_rank_logit: float


def build_report(args: argparse.Namespace) -> dict[str, Any]:
    roots = tuple(args.root or discover_roots(args.base_dir, args.reports_dir, args.min_root_name))
    root_names = tuple(root.name for root in roots)
    variation_report = build_rv600_variation_report(
        roots,
        phase="grid",
        output_json=args.output_json,
        output_md=args.output_md,
        config=ReplayConfig(min_fill_prob=0.0, counterfactual_fill_threshold=0.5),
        min_decision_ts_utc=_parse_dt(args.min_decision_ts_utc) if args.min_decision_ts_utc else None,
    )
    grouped = _group_rows(variation_report.run_rows)
    root_index = {name: idx for idx, name in enumerate(root_names)}
    candidates = _candidate_arrays(grouped, root_index, min_total_entries=args.min_total_entries)
    splits = _balanced_splits(
        len(root_names),
        max_splits=args.max_splits,
        seed=args.seed,
    )
    split_rows: list[dict[str, Any]] = []
    selected_counter: Counter[str] = Counter()
    overfit_count = 0
    selected_test_pnls: list[float] = []
    selected_test_entries: list[int] = []
    for train_indices in splits:
        train_set = set(train_indices)
        test_indices = tuple(idx for idx in range(len(root_names)) if idx not in train_set)
        selected = _evaluate_split(
            candidates,
            train_indices=tuple(train_indices),
            test_indices=test_indices,
            min_train_entries=args.min_train_entries,
        )
        if selected is None:
            continue
        selected_counter[f"{selected.variant}|{selected.accounting_mode}"] += 1
        selected_test_pnls.append(selected.test_pnl_cents)
        selected_test_entries.append(selected.test_entries)
        if selected.test_rank_percentile <= 0.5:
            overfit_count += 1
        split_rows.append(
            {
                **asdict(selected),
                "train_roots": [root_names[idx] for idx in train_indices],
                "test_roots": [root_names[idx] for idx in test_indices],
            }
        )
    valid_split_count = len(split_rows)
    pbo = overfit_count / valid_split_count if valid_split_count else 1.0
    positive_split_rate = (
        sum(1 for pnl in selected_test_pnls if pnl > 0.0) / valid_split_count
        if valid_split_count
        else 0.0
    )
    mean_test_pnl = _mean(selected_test_pnls)
    mean_test_entries = _mean(selected_test_entries)
    decision = (
        "pbo_supports_current_grid"
        if (
            valid_split_count > 0
            and pbo <= args.max_pbo
            and positive_split_rate >= args.min_positive_split_rate
            and mean_test_pnl > 0.0
        )
        else "pbo_rejects_current_grid"
    )
    selected_variants = [
        {
            "candidate": key,
            "selection_count": count,
            "selection_rate": count / valid_split_count if valid_split_count else 0.0,
        }
        for key, count in selected_counter.most_common(10)
    ]
    report = {
        "schema_version": "rv600-pbo-stability-audit-v1",
        "generated_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "research_only": True,
        "decision": decision,
        "roots": list(root_names),
        "root_count": len(root_names),
        "candidate_count": len(candidates),
        "split_count": len(splits),
        "valid_split_count": valid_split_count,
        "pbo": pbo,
        "positive_split_rate": positive_split_rate,
        "mean_selected_test_pnl_cents": mean_test_pnl,
        "median_selected_test_pnl_cents": _median(selected_test_pnls),
        "mean_selected_test_entries": mean_test_entries,
        "overfit_count": overfit_count,
        "selected_variants": selected_variants,
        "sample_splits": split_rows[: args.sample_split_rows],
        "chosen_method": {
            "name": "CSCV/PBO stability audit",
            "reason": (
                "The current blocker is positive average PnL with unstable root/market breadth. "
                "PBO directly checks whether variants selected in-sample keep above-median "
                "rank out of sample across root splits."
            ),
        },
        "sources_considered": [
            {
                "name": "Probability of Backtest Overfitting / CSCV",
                "url": "https://core.ac.uk/display/24041876",
                "decision": "selected",
            },
            {
                "name": "Deflated Sharpe Ratio",
                "url": "https://papers.ssrn.com/sol3/Delivery.cfm/SSRN_ID2460551_code87814.pdf?abstractid=2460551&mirid=1",
                "decision": "not_selected",
                "reason": "Useful for multiple-testing inflation, but less direct for root/market breadth than split-rank PBO.",
            },
            {
                "name": "Group DRO",
                "url": "https://arxiv.org/abs/1911.08731",
                "decision": "already_tested",
                "reason": "Existing group-DRO rescue still has zero support rows on the current sample.",
            },
            {
                "name": "Conformal Risk Control",
                "url": "https://arxiv.org/abs/2208.02814",
                "decision": "already_tested_adjacent",
                "reason": "Existing conformal abstention rescue did not produce a prequential gate pass.",
            },
        ],
        "thresholds": {
            "max_pbo": args.max_pbo,
            "min_positive_split_rate": args.min_positive_split_rate,
            "min_total_entries": args.min_total_entries,
            "min_train_entries": args.min_train_entries,
        },
        "inputs": {
            "base_dir": str(args.base_dir),
            "reports_dir": str(args.reports_dir),
            "min_root_name": args.min_root_name,
            "min_decision_ts_utc": args.min_decision_ts_utc,
            "max_splits": args.max_splits,
            "seed": args.seed,
        },
    }
    return report


def _group_rows(rows: Sequence[RV600VariantRunRow]) -> dict[tuple[str, str], list[RV600VariantRunRow]]:
    grouped: dict[tuple[str, str], list[RV600VariantRunRow]] = defaultdict(list)
    for row in rows:
        grouped[(row.variant, row.accounting_mode)].append(row)
    return grouped


def _candidate_arrays(
    grouped: dict[tuple[str, str], list[RV600VariantRunRow]],
    root_index: dict[str, int],
    *,
    min_total_entries: int,
) -> list[dict[str, Any]]:
    candidates: list[dict[str, Any]] = []
    root_count = len(root_index)
    for (variant, accounting), rows in grouped.items():
        pnls = [0.0] * root_count
        entries = [0] * root_count
        for row in rows:
            idx = root_index[row.root_name]
            pnls[idx] += float(row.selected_pnl_cents)
            entries[idx] += int(row.accepted_entries)
        if sum(entries) < min_total_entries:
            continue
        candidates.append(
            {
                "variant": variant,
                "accounting_mode": accounting,
                "pnls": pnls,
                "entries": entries,
            }
        )
    return candidates


def _balanced_splits(root_count: int, *, max_splits: int, seed: int) -> list[tuple[int, ...]]:
    train_size = root_count // 2
    all_combinations = itertools.combinations(range(root_count), train_size)
    if root_count <= 18:
        splits = list(all_combinations)
    else:
        rng = random.Random(seed)
        seen: set[tuple[int, ...]] = set()
        splits = []
        while len(splits) < max_splits:
            split = tuple(sorted(rng.sample(range(root_count), train_size)))
            if split in seen:
                continue
            seen.add(split)
            splits.append(split)
    return splits[:max_splits]


def _evaluate_split(
    candidates: Sequence[dict[str, Any]],
    *,
    train_indices: tuple[int, ...],
    test_indices: tuple[int, ...],
    min_train_entries: int,
) -> CandidateSplitStats | None:
    scored: list[tuple[dict[str, Any], float, int, float, int]] = []
    for candidate in candidates:
        pnls = candidate["pnls"]
        entries = candidate["entries"]
        train_pnl = sum(pnls[idx] for idx in train_indices)
        train_entries = sum(entries[idx] for idx in train_indices)
        if train_entries < min_train_entries:
            continue
        test_pnl = sum(pnls[idx] for idx in test_indices)
        test_entries = sum(entries[idx] for idx in test_indices)
        scored.append((candidate, train_pnl, train_entries, test_pnl, test_entries))
    if not scored:
        return None
    selected = max(scored, key=lambda item: (item[1], item[2]))
    test_pnls = sorted(item[3] for item in scored)
    percentile = _rank_percentile(test_pnls, selected[3])
    return CandidateSplitStats(
        variant=str(selected[0]["variant"]),
        accounting_mode=str(selected[0]["accounting_mode"]),
        train_pnl_cents=float(selected[1]),
        train_entries=int(selected[2]),
        test_pnl_cents=float(selected[3]),
        test_entries=int(selected[4]),
        test_rank_percentile=percentile,
        test_rank_logit=_logit(percentile),
    )


def _rank_percentile(sorted_values: Sequence[float], value: float) -> float:
    if not sorted_values:
        return 0.0
    below_or_equal = sum(1 for item in sorted_values if item <= value)
    return max(1e-6, min(1.0 - 1e-6, below_or_equal / len(sorted_values)))


def _mean(values: Sequence[float | int]) -> float:
    return float(sum(values) / len(values)) if values else 0.0


def _median(values: Sequence[float]) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    mid = len(ordered) // 2
    if len(ordered) % 2:
        return float(ordered[mid])
    return float((ordered[mid - 1] + ordered[mid]) / 2.0)


def _logit(value: float) -> float:
    p = max(1e-6, min(1.0 - 1e-6, value))
    return math.log(p / (1.0 - p))


def _parse_dt(value: str) -> datetime:
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def _markdown(report: dict[str, Any]) -> str:
    lines = [
        "# RV600 PBO Stability Audit",
        "",
        f"- generated_utc: {report['generated_utc']}",
        f"- decision: {report['decision']}",
        f"- root_count: {report['root_count']}",
        f"- candidate_count: {report['candidate_count']}",
        f"- valid_split_count: {report['valid_split_count']}",
        f"- pbo: {report['pbo']:.4f}",
        f"- positive_split_rate: {report['positive_split_rate']:.4f}",
        f"- mean_selected_test_pnl_cents: {report['mean_selected_test_pnl_cents']:.4f}",
        f"- median_selected_test_pnl_cents: {report['median_selected_test_pnl_cents']:.4f}",
        "",
        "## Chosen Method",
        "",
        report["chosen_method"]["reason"],
        "",
        "## Top Selected Variants",
        "",
        "| candidate | count | rate |",
        "|---|---:|---:|",
    ]
    for row in report["selected_variants"]:
        lines.append(
            f"| `{row['candidate']}` | {row['selection_count']} | {row['selection_rate']:.4f} |"
        )
    lines.extend(["", "## Sources Considered", ""])
    for row in report["sources_considered"]:
        extra = f" - {row.get('reason')}" if row.get("reason") else ""
        lines.append(f"- {row['decision']}: [{row['name']}]({row['url']}){extra}")
    lines.append("")
    return "\n".join(lines)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="CSCV/PBO stability audit for RV600 bounded roots.")
    parser.add_argument("--root", action="append", type=Path, default=[])
    parser.add_argument("--base-dir", type=Path, default=DEFAULT_BASE_DIR)
    parser.add_argument("--reports-dir", type=Path, default=DEFAULT_REPORTS_DIR)
    parser.add_argument("--min-root-name", default=DEFAULT_MIN_ROOT_NAME)
    parser.add_argument("--min-decision-ts-utc", default=DEFAULT_MIN_DECISION_TS_UTC)
    parser.add_argument("--min-total-entries", type=int, default=25)
    parser.add_argument("--min-train-entries", type=int, default=12)
    parser.add_argument("--max-splits", type=int, default=512)
    parser.add_argument("--seed", type=int, default=600)
    parser.add_argument("--max-pbo", type=float, default=0.20)
    parser.add_argument("--min-positive-split-rate", type=float, default=0.60)
    parser.add_argument("--sample-split-rows", type=int, default=20)
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
    print(f"decision={report['decision']}")
    print(f"root_count={report['root_count']}")
    print(f"candidate_count={report['candidate_count']}")
    print(f"valid_split_count={report['valid_split_count']}")
    print(f"pbo={report['pbo']:.4f}")
    print(f"positive_split_rate={report['positive_split_rate']:.4f}")
    print(f"mean_selected_test_pnl_cents={report['mean_selected_test_pnl_cents']:.4f}")
    if args.write:
        print(f"output_json={args.output_json}")
        print(f"output_md={args.output_md}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
