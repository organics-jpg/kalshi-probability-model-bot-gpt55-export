from __future__ import annotations

import argparse
import json
import math
import random
from collections import defaultdict
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
DEFAULT_OUTPUT_JSON = Path("logs/particle_research/reports/rv600_reality_check_audit_latest.json")
DEFAULT_OUTPUT_MD = Path("logs/particle_research/reports/rv600_reality_check_audit_latest.md")


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
class CandidateRealityStats:
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
    root_index = {name: idx for idx, name in enumerate(root_names)}
    summaries = {
        (row.variant, str(row.accounting_mode)): asdict(row)
        for row in variation.summary_rows
    }
    candidates = _candidate_arrays(
        variation.run_rows,
        root_index,
        summaries,
        min_total_entries=args.min_total_entries,
    )
    stats = [_candidate_stats(candidate) for candidate in candidates]
    best_by_delta = max(stats, key=lambda row: row.total_matched_v28_delta_cents, default=None)
    best_by_pnl = max(stats, key=lambda row: row.total_selected_pnl_cents, default=None)
    mean_result = _bootstrap_max_stat(
        candidates,
        metric="matched_delta",
        statistic="mean",
        bootstrap_count=args.bootstrap_count,
        seed=args.seed,
    )
    studentized_result = _bootstrap_max_stat(
        candidates,
        metric="matched_delta",
        statistic="studentized",
        bootstrap_count=args.bootstrap_count,
        seed=args.seed + 17,
    )
    best = best_by_delta
    gate_pass = (
        best is not None
        and best.total_matched_v28_delta_cents > 0.0
        and best.total_selected_pnl_cents > 0.0
        and not best.rejection_reason
        and mean_result["p_value"] <= args.max_p_value
        and studentized_result["p_value"] <= args.max_p_value
    )
    decision = "reality_check_supports_current_grid" if gate_pass else "reality_check_rejects_current_grid"
    report = {
        "schema_version": "rv600-reality-check-audit-v1",
        "generated_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "research_only": True,
        "decision": decision,
        "root_count": len(root_names),
        "roots": list(root_names),
        "candidate_count": len(candidates),
        "best_by_matched_v28_delta": asdict(best_by_delta) if best_by_delta else None,
        "best_by_selected_pnl": asdict(best_by_pnl) if best_by_pnl else None,
        "mean_reality_check": mean_result,
        "studentized_reality_check": studentized_result,
        "chosen_method": {
            "name": "Root bootstrap reality check over matched-v28 deltas",
            "reason": (
                "The current RV600 risk is data snooping across thousands of grid variants. "
                "A root-level bootstrap of the maximum matched-v28 delta tests whether the "
                "best apparent edge is larger than the selection effect expected from the "
                "full tested universe."
            ),
        },
        "sources_considered": [
            {
                "name": "White-style Reality Check for technical trading rules",
                "url": "https://www.fmg.ac.uk/publications/discussion-papers/data-snooping-technical-trading-rule-performance-and-bootstrap",
                "decision": "selected",
                "reason": "Direct fit for testing the best rule after searching a full universe of trading rules.",
            },
            {
                "name": "Hansen Superior Predictive Ability test",
                "url": "https://papers.ssrn.com/sol3/papers.cfm?abstract_id=264569",
                "decision": "partially_used",
                "reason": "Motivates the studentized companion statistic, but a full SPA implementation is unnecessary for this small root-level audit.",
            },
            {
                "name": "Deflated Sharpe Ratio",
                "url": "https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2460551",
                "decision": "not_selected",
                "reason": "Corrects Sharpe inflation, while RV600 has sparse binary-settlement PnL and a matched-v28 benchmark.",
            },
            {
                "name": "Backtest PnL discounting",
                "url": "https://arxiv.org/abs/1902.01802",
                "decision": "not_selected",
                "reason": "Useful for shrinkage, but less directly tied to selecting one candidate from the tested grid.",
            },
            {
                "name": "Optimal trading rules without backtesting",
                "url": "https://arxiv.org/abs/1408.1159",
                "decision": "not_selected",
                "reason": "Interesting direction, but RV600 lacks a closed-form process model reliable enough to replace shadow/replay evidence.",
            },
        ],
        "thresholds": {
            "max_p_value": args.max_p_value,
            "min_total_entries": args.min_total_entries,
            "bootstrap_count": args.bootstrap_count,
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


def _candidate_stats(candidate: CandidateArray) -> CandidateRealityStats:
    summary = candidate.summary
    total_delta = sum(candidate.matched_delta)
    std_delta = _sample_std(candidate.matched_delta)
    mean_delta = total_delta / len(candidate.matched_delta) if candidate.matched_delta else 0.0
    t_stat = (math.sqrt(len(candidate.matched_delta)) * mean_delta / std_delta) if std_delta > 0.0 else 0.0
    return CandidateRealityStats(
        variant=candidate.variant,
        accounting_mode=candidate.accounting_mode,
        total_selected_pnl_cents=sum(candidate.selected_pnl),
        total_matched_v28_delta_cents=total_delta,
        total_matched_v28_control_pnl_cents=sum(candidate.matched_control),
        accepted_entries=sum(candidate.entries),
        distinct_markets=int(summary.get("distinct_markets") or 0),
        avg_pnl_per_entry_cents=float(summary.get("avg_pnl_per_entry_cents") or 0.0),
        positive_root_rate=float(summary.get("positive_root_rate") or 0.0),
        positive_market_rate=float(summary.get("positive_market_rate") or 0.0),
        max_single_market_pnl_share=float(summary.get("max_single_market_pnl_share") or 0.0),
        last_window_pnl_cents=float(summary.get("last_window_pnl_cents") or 0.0),
        rejection_reason=str(summary.get("rejection_reason") or ""),
        mean_delta_cents_per_root=mean_delta,
        studentized_delta_t=t_stat,
    )


def _bootstrap_max_stat(
    candidates: Sequence[CandidateArray],
    *,
    metric: str,
    statistic: str,
    bootstrap_count: int,
    seed: int,
) -> dict[str, Any]:
    if not candidates:
        return {
            "statistic": statistic,
            "metric": metric,
            "observed_stat": 0.0,
            "p_value": 1.0,
            "bootstrap_count": bootstrap_count,
            "exceedance_count": bootstrap_count,
        }
    values_by_candidate = [
        tuple(float(value) for value in getattr(candidate, metric))
        for candidate in candidates
    ]
    root_count = len(values_by_candidate[0])
    means = [_mean(values) for values in values_by_candidate]
    stds = [_sample_std(values) for values in values_by_candidate]
    sqrt_n = math.sqrt(root_count)
    if statistic == "studentized":
        observed_values = [
            (sqrt_n * mean / std) if std > 0.0 else 0.0
            for mean, std in zip(means, stds)
        ]
    else:
        observed_values = [sqrt_n * mean for mean in means]
    observed_stat = max(observed_values)
    centered = [
        tuple(value - mean for value in values)
        for values, mean in zip(values_by_candidate, means)
    ]
    rng = random.Random(seed)
    exceedance_count = 0
    for _ in range(bootstrap_count):
        counts = [0] * root_count
        for _sample in range(root_count):
            counts[rng.randrange(root_count)] += 1
        max_boot = -math.inf
        for candidate_index, candidate_values in enumerate(centered):
            boot_sum = 0.0
            for idx, count in enumerate(counts):
                if count:
                    boot_sum += candidate_values[idx] * count
            boot_mean = boot_sum / root_count
            if statistic == "studentized":
                std = stds[candidate_index]
                boot_stat = (sqrt_n * boot_mean / std) if std > 0.0 else 0.0
            else:
                boot_stat = sqrt_n * boot_mean
            if boot_stat > max_boot:
                max_boot = boot_stat
        if max_boot >= observed_stat:
            exceedance_count += 1
    p_value = (exceedance_count + 1) / (bootstrap_count + 1)
    return {
        "statistic": statistic,
        "metric": metric,
        "observed_stat": observed_stat,
        "p_value": p_value,
        "bootstrap_count": bootstrap_count,
        "exceedance_count": exceedance_count,
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
    best_delta = report.get("best_by_matched_v28_delta") or {}
    best_pnl = report.get("best_by_selected_pnl") or {}
    lines = [
        "# RV600 Reality Check Audit",
        "",
        f"- generated_utc: {report['generated_utc']}",
        f"- research_only: {report['research_only']}",
        f"- decision: {report['decision']}",
        f"- root_count: {report['root_count']}",
        f"- candidate_count: {report['candidate_count']}",
        "",
        "## Best By Matched-v28 Delta",
        "",
        f"- variant: `{best_delta.get('variant')}`",
        f"- accounting_mode: `{best_delta.get('accounting_mode')}`",
        f"- selected_pnl_cents: {best_delta.get('total_selected_pnl_cents')}",
        f"- matched_v28_delta_cents: {best_delta.get('total_matched_v28_delta_cents')}",
        f"- accepted_entries: {best_delta.get('accepted_entries')}",
        f"- avg_pnl_per_entry_cents: {best_delta.get('avg_pnl_per_entry_cents')}",
        f"- positive_root_rate: {best_delta.get('positive_root_rate')}",
        f"- positive_market_rate: {best_delta.get('positive_market_rate')}",
        f"- last_window_pnl_cents: {best_delta.get('last_window_pnl_cents')}",
        f"- rejection_reason: `{best_delta.get('rejection_reason')}`",
        "",
        "## Best By Selected PnL",
        "",
        f"- variant: `{best_pnl.get('variant')}`",
        f"- accounting_mode: `{best_pnl.get('accounting_mode')}`",
        f"- selected_pnl_cents: {best_pnl.get('total_selected_pnl_cents')}",
        f"- matched_v28_delta_cents: {best_pnl.get('total_matched_v28_delta_cents')}",
        f"- rejection_reason: `{best_pnl.get('rejection_reason')}`",
        "",
        "## Bootstrap Checks",
        "",
        f"- mean_reality_check_p_value: {report['mean_reality_check']['p_value']:.4f}",
        f"- mean_reality_check_observed_stat: {report['mean_reality_check']['observed_stat']:.4f}",
        f"- studentized_reality_check_p_value: {report['studentized_reality_check']['p_value']:.4f}",
        f"- studentized_reality_check_observed_stat: {report['studentized_reality_check']['observed_stat']:.4f}",
        "",
        "## Chosen Method",
        "",
        report["chosen_method"]["reason"],
        "",
        "## Sources Considered",
        "",
    ]
    for row in report["sources_considered"]:
        lines.append(f"- {row['decision']}: [{row['name']}]({row['url']}) - {row['reason']}")
    lines.append("")
    return "\n".join(lines)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Root-bootstrap reality check for RV600 data-snooping risk.")
    parser.add_argument("--root", action="append", type=Path, default=[])
    parser.add_argument("--base-dir", type=Path, default=DEFAULT_BASE_DIR)
    parser.add_argument("--reports-dir", type=Path, default=DEFAULT_REPORTS_DIR)
    parser.add_argument("--min-root-name", default=DEFAULT_MIN_ROOT_NAME)
    parser.add_argument("--min-decision-ts-utc", default=DEFAULT_MIN_DECISION_TS_UTC)
    parser.add_argument("--min-total-entries", type=int, default=25)
    parser.add_argument("--bootstrap-count", type=int, default=1000)
    parser.add_argument("--seed", type=int, default=600)
    parser.add_argument("--max-p-value", type=float, default=0.05)
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
    best_delta = report.get("best_by_matched_v28_delta") or {}
    print(f"decision={report['decision']}")
    print(f"root_count={report['root_count']}")
    print(f"candidate_count={report['candidate_count']}")
    print(f"best_delta_variant={best_delta.get('variant')}")
    print(f"best_delta_cents={best_delta.get('total_matched_v28_delta_cents')}")
    print(f"mean_rc_p_value={report['mean_reality_check']['p_value']:.4f}")
    print(f"studentized_rc_p_value={report['studentized_reality_check']['p_value']:.4f}")
    if args.write:
        print(f"output_json={args.output_json}")
        print(f"output_md={args.output_md}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
