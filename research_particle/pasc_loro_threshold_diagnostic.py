from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Mapping, Sequence

from .materialized_variant_replay import materialize_variant_rows
from .meta_probability_loro import RunInputSet, _load_run
from .replay_runner import ReplayConfig, ReplayInput, ReplayReport, evaluate_replay
from .selection_sweep import _parse_float_grid


DEFAULT_VARIANTS = (
    "particle",
    "brownian",
    "current_calibrated",
    "market_current_50_50",
    "market_particle_75_25",
    "current_particle_75_25",
    "market_current_particle_40_40_20",
    "rolling_vol_600s",
    "blend_50current_25particle_25rv600",
)


@dataclass(frozen=True)
class PASCThresholdChoice:
    variant: str
    min_ev_cents: float
    min_fill_prob: float
    train_run_count: int
    train_selected_count: int
    train_total_counterfactual_pnl_cents: float
    train_positive_pnl_run_count: int
    train_positive_ev_rank_run_count: int
    train_positive_top_bucket_run_count: int
    train_beats_current_run_count: int
    train_mean_brier: float
    train_mean_log_loss: float


@dataclass(frozen=True)
class PASCHoldoutRow:
    selector: str
    holdout_run: str
    variant: str
    min_ev_cents: float
    min_fill_prob: float
    train_run_count: int
    train_selected_count: int
    train_total_counterfactual_pnl_cents: float
    train_positive_pnl_run_count: int
    train_positive_ev_rank_run_count: int
    train_positive_top_bucket_run_count: int
    train_beats_current_run_count: int
    holdout_candidate_count: int
    holdout_market_count: int
    holdout_selected_count: int
    holdout_total_counterfactual_pnl_cents: float
    holdout_avg_counterfactual_pnl_cents_per_selected: float
    holdout_brier: float
    holdout_log_loss: float
    holdout_beats_brownian: bool
    holdout_beats_market: bool
    holdout_beats_current_calibrated: bool
    holdout_ev_rank_correlation_sign: float
    holdout_top_ev_bucket_pnl_cents: float
    holdout_passes_strict_gates: bool


@dataclass(frozen=True)
class PASCSelectorSummaryRow:
    selector: str
    holdout_count: int
    total_holdout_pnl_cents: float
    mean_holdout_brier: float
    mean_holdout_log_loss: float
    positive_pnl_holdout_count: int
    beats_brownian_holdout_count: int
    beats_market_holdout_count: int
    beats_current_holdout_count: int
    positive_ev_rank_holdout_count: int
    positive_top_bucket_holdout_count: int
    strict_gate_holdout_count: int
    strict_all_holdouts: bool


@dataclass(frozen=True)
class PASCThresholdLOROReport:
    run_inputs: tuple[RunInputSet, ...]
    variants: tuple[str, ...]
    min_ev_grid: tuple[float, ...]
    min_fill_grid: tuple[float, ...]
    holdout_rows: tuple[PASCHoldoutRow, ...]
    selector_summary_rows: tuple[PASCSelectorSummaryRow, ...]
    promotion_safe: bool
    conclusion: str


def build_pasc_threshold_loro_report(
    run_roots: Sequence[Path],
    *,
    variants: Sequence[str] = DEFAULT_VARIANTS,
    min_ev_grid: Sequence[float],
    min_fill_grid: Sequence[float],
    replay_config_base: ReplayConfig | None = None,
) -> PASCThresholdLOROReport:
    if len(run_roots) < 2:
        raise ValueError("at least two run roots are required")
    if not variants:
        raise ValueError("at least one variant is required")
    if not min_ev_grid:
        raise ValueError("min_ev_grid cannot be empty")
    if not min_fill_grid:
        raise ValueError("min_fill_grid cannot be empty")
    base_cfg = replay_config_base or ReplayConfig(counterfactual_fill_threshold=0.5)
    loaded_runs = [_load_run(root) for root in run_roots]
    materialized = _materialize_by_run(loaded_runs, variants)
    run_names = tuple(run_name for run_name, _, _ in loaded_runs)
    report_cache = _build_report_cache(
        run_names,
        materialized,
        variants=variants,
        min_ev_grid=min_ev_grid,
        min_fill_grid=min_fill_grid,
        base_config=base_cfg,
    )
    holdout_rows: list[PASCHoldoutRow] = []
    for holdout_name, holdout_meta, _ in loaded_runs:
        train_names = [run_name for run_name, _, _ in loaded_runs if run_name != holdout_name]
        choices = _build_threshold_choices(
            train_names,
            report_cache,
            variants=variants,
            min_ev_grid=min_ev_grid,
            min_fill_grid=min_fill_grid,
        )
        selected_choices = _select_choices(choices)
        for selector, choice in selected_choices.items():
            holdout_report = report_cache[
                (holdout_name, choice.variant, choice.min_ev_cents, choice.min_fill_prob)
            ]
            strict = _strict_gate(holdout_report)
            holdout_rows.append(
                PASCHoldoutRow(
                    selector=selector,
                    holdout_run=holdout_name,
                    variant=choice.variant,
                    min_ev_cents=choice.min_ev_cents,
                    min_fill_prob=choice.min_fill_prob,
                    train_run_count=choice.train_run_count,
                    train_selected_count=choice.train_selected_count,
                    train_total_counterfactual_pnl_cents=choice.train_total_counterfactual_pnl_cents,
                    train_positive_pnl_run_count=choice.train_positive_pnl_run_count,
                    train_positive_ev_rank_run_count=choice.train_positive_ev_rank_run_count,
                    train_positive_top_bucket_run_count=choice.train_positive_top_bucket_run_count,
                    train_beats_current_run_count=choice.train_beats_current_run_count,
                    holdout_candidate_count=holdout_report.candidate_count,
                    holdout_market_count=holdout_meta.market_count,
                    holdout_selected_count=holdout_report.selected_count,
                    holdout_total_counterfactual_pnl_cents=holdout_report.total_counterfactual_pnl_cents,
                    holdout_avg_counterfactual_pnl_cents_per_selected=(
                        holdout_report.avg_counterfactual_pnl_cents_per_selected
                    ),
                    holdout_brier=holdout_report.particle.brier,
                    holdout_log_loss=holdout_report.particle.log_loss,
                    holdout_beats_brownian=holdout_report.particle_beats_brownian,
                    holdout_beats_market=holdout_report.particle_beats_market,
                    holdout_beats_current_calibrated=holdout_report.particle_beats_current_calibrated,
                    holdout_ev_rank_correlation_sign=holdout_report.ev_rank_correlation_sign,
                    holdout_top_ev_bucket_pnl_cents=holdout_report.top_ev_bucket_pnl_cents,
                    holdout_passes_strict_gates=strict,
                )
            )
    summaries = tuple(_summarize_holdouts(holdout_rows))
    promotion_safe = any(row.strict_all_holdouts for row in summaries)
    conclusion = (
        "At least one PnL-aware threshold selector passed every strict held-out locked run; "
        "still require a fresh predeclared shadow run before promotion."
        if promotion_safe
        else "No PnL-aware threshold selector passed strict leave-one-run-out locked gates."
    )
    return PASCThresholdLOROReport(
        run_inputs=tuple(meta for _, meta, _ in loaded_runs),
        variants=tuple(variants),
        min_ev_grid=tuple(float(value) for value in min_ev_grid),
        min_fill_grid=tuple(float(value) for value in min_fill_grid),
        holdout_rows=tuple(holdout_rows),
        selector_summary_rows=summaries,
        promotion_safe=promotion_safe,
        conclusion=conclusion,
    )


def write_pasc_threshold_loro_report(
    report: PASCThresholdLOROReport,
    output_dir: Path,
    stem: str,
) -> tuple[Path, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    json_path = output_dir / f"{stem}.json"
    md_path = output_dir / f"{stem}.md"
    json_path.write_text(json.dumps(asdict(report), indent=2, sort_keys=True), encoding="utf-8")
    md_path.write_text(_markdown(report), encoding="utf-8")
    return json_path, md_path


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Leave-one-run-out diagnostic for PnL-aware selective classification "
            "thresholds on locked all-candidate particle replays."
        )
    )
    parser.add_argument("--run-root", action="append", required=True, type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--stem", default="pasc_loro_threshold_diagnostic")
    parser.add_argument("--variant", action="append", dest="variants", default=None)
    parser.add_argument("--min-ev-grid", default="0,1,2,3,5,8,10,12,15,20")
    parser.add_argument("--min-fill-grid", default="0,0.25,0.5,0.75,1.0")
    parser.add_argument("--no-fill-penalty-cents", default=0.0, type=float)
    parser.add_argument(
        "--counterfactual-fill-policy",
        choices=["threshold", "always_fill", "never_fill"],
        default="threshold",
    )
    parser.add_argument("--counterfactual-fill-threshold", default=0.5, type=float)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    report = build_pasc_threshold_loro_report(
        args.run_root,
        variants=tuple(args.variants) if args.variants else DEFAULT_VARIANTS,
        min_ev_grid=_parse_float_grid(args.min_ev_grid, "min_ev_grid"),
        min_fill_grid=_parse_float_grid(args.min_fill_grid, "min_fill_grid"),
        replay_config_base=ReplayConfig(
            no_fill_penalty_cents=args.no_fill_penalty_cents,
            counterfactual_fill_policy=args.counterfactual_fill_policy,
            counterfactual_fill_threshold=args.counterfactual_fill_threshold,
        ),
    )
    json_path, md_path = write_pasc_threshold_loro_report(report, args.output_dir, args.stem)
    print(f"run_count={len(report.run_inputs)}")
    print(f"variant_count={len(report.variants)}")
    print(f"holdout_row_count={len(report.holdout_rows)}")
    print(f"summary_row_count={len(report.selector_summary_rows)}")
    print(f"promotion_safe={report.promotion_safe}")
    print(f"json_report={json_path}")
    print(f"md_report={md_path}")
    return 0


def _materialize_by_run(
    loaded_runs: Sequence[tuple[str, RunInputSet, list[ReplayInput]]],
    variants: Sequence[str],
) -> dict[tuple[str, str], list[ReplayInput]]:
    rows: dict[tuple[str, str], list[ReplayInput]] = {}
    for run_name, _, replay_rows in loaded_runs:
        for variant in variants:
            rows[(run_name, variant)] = materialize_variant_rows(replay_rows, variant)
    return rows


def _build_report_cache(
    run_names: Sequence[str],
    materialized: Mapping[tuple[str, str], Sequence[ReplayInput]],
    *,
    variants: Sequence[str],
    min_ev_grid: Sequence[float],
    min_fill_grid: Sequence[float],
    base_config: ReplayConfig,
) -> dict[tuple[str, str, float, float], ReplayReport]:
    cache: dict[tuple[str, str, float, float], ReplayReport] = {}
    for run_name in run_names:
        for variant in variants:
            rows = materialized[(run_name, variant)]
            for min_fill in min_fill_grid:
                for min_ev in min_ev_grid:
                    key = (run_name, variant, float(min_ev), float(min_fill))
                    cache[key] = _evaluate_variant_threshold(
                        rows,
                        min_ev_cents=float(min_ev),
                        min_fill_prob=float(min_fill),
                        base_config=base_config,
                    )
    return cache


def _build_threshold_choices(
    train_names: Sequence[str],
    report_cache: Mapping[tuple[str, str, float, float], ReplayReport],
    *,
    variants: Sequence[str],
    min_ev_grid: Sequence[float],
    min_fill_grid: Sequence[float],
) -> list[PASCThresholdChoice]:
    choices: list[PASCThresholdChoice] = []
    for variant in variants:
        for min_fill in min_fill_grid:
            for min_ev in min_ev_grid:
                reports = [
                    report_cache[(run_name, variant, float(min_ev), float(min_fill))]
                    for run_name in train_names
                ]
                choices.append(
                    PASCThresholdChoice(
                        variant=variant,
                        min_ev_cents=float(min_ev),
                        min_fill_prob=float(min_fill),
                        train_run_count=len(reports),
                        train_selected_count=sum(report.selected_count for report in reports),
                        train_total_counterfactual_pnl_cents=sum(
                            report.total_counterfactual_pnl_cents for report in reports
                        ),
                        train_positive_pnl_run_count=sum(
                            1 for report in reports if report.total_counterfactual_pnl_cents > 0.0
                        ),
                        train_positive_ev_rank_run_count=sum(
                            1 for report in reports if report.ev_rank_correlation_sign > 0.0
                        ),
                        train_positive_top_bucket_run_count=sum(
                            1 for report in reports if report.top_ev_bucket_pnl_cents > 0.0
                        ),
                        train_beats_current_run_count=sum(
                            1 for report in reports if report.particle_beats_current_calibrated
                        ),
                        train_mean_brier=_mean(report.particle.brier for report in reports),
                        train_mean_log_loss=_mean(report.particle.log_loss for report in reports),
                    )
                )
    return choices


def _select_choices(choices: Sequence[PASCThresholdChoice]) -> dict[str, PASCThresholdChoice]:
    selectable = [choice for choice in choices if choice.train_selected_count > 0]
    if not selectable:
        raise ValueError("no threshold choice selected any training rows")
    return {
        "train_best_total_pnl": max(
            selectable,
            key=lambda row: (
                row.train_total_counterfactual_pnl_cents,
                row.train_positive_pnl_run_count,
                row.train_selected_count,
                -row.train_mean_brier,
            ),
        ),
        "train_best_stable_pnl": max(
            selectable,
            key=lambda row: (
                row.train_positive_pnl_run_count,
                row.train_positive_ev_rank_run_count,
                row.train_positive_top_bucket_run_count,
                row.train_total_counterfactual_pnl_cents,
                -row.train_mean_brier,
            ),
        ),
        "train_best_gate_score": max(
            selectable,
            key=lambda row: (
                row.train_beats_current_run_count,
                row.train_positive_top_bucket_run_count,
                row.train_positive_ev_rank_run_count,
                row.train_positive_pnl_run_count,
                row.train_total_counterfactual_pnl_cents,
                -row.train_mean_brier,
            ),
        ),
    }


def _evaluate_variant_threshold(
    rows: Sequence[ReplayInput],
    *,
    min_ev_cents: float,
    min_fill_prob: float,
    base_config: ReplayConfig,
) -> ReplayReport:
    return evaluate_replay(
        rows,
        ReplayConfig(
            min_ev_cents=min_ev_cents,
            min_fill_prob=min_fill_prob,
            no_fill_penalty_cents=base_config.no_fill_penalty_cents,
            counterfactual_fill_policy=base_config.counterfactual_fill_policy,
            counterfactual_fill_threshold=base_config.counterfactual_fill_threshold,
        ),
    )


def _strict_gate(report: ReplayReport) -> bool:
    return (
        report.total_counterfactual_pnl_cents > 0.0
        and report.particle_beats_brownian
        and report.particle_beats_market
        and report.particle_beats_current_calibrated
        and report.ev_rank_correlation_sign > 0.0
        and report.top_ev_bucket_pnl_cents > 0.0
    )


def _summarize_holdouts(rows: Sequence[PASCHoldoutRow]) -> list[PASCSelectorSummaryRow]:
    grouped: dict[str, list[PASCHoldoutRow]] = {}
    for row in rows:
        grouped.setdefault(row.selector, []).append(row)
    summaries: list[PASCSelectorSummaryRow] = []
    for selector in sorted(grouped):
        selector_rows = grouped[selector]
        strict_count = sum(1 for row in selector_rows if row.holdout_passes_strict_gates)
        summaries.append(
            PASCSelectorSummaryRow(
                selector=selector,
                holdout_count=len(selector_rows),
                total_holdout_pnl_cents=sum(
                    row.holdout_total_counterfactual_pnl_cents for row in selector_rows
                ),
                mean_holdout_brier=_mean(row.holdout_brier for row in selector_rows),
                mean_holdout_log_loss=_mean(row.holdout_log_loss for row in selector_rows),
                positive_pnl_holdout_count=sum(
                    1 for row in selector_rows if row.holdout_total_counterfactual_pnl_cents > 0.0
                ),
                beats_brownian_holdout_count=sum(
                    1 for row in selector_rows if row.holdout_beats_brownian
                ),
                beats_market_holdout_count=sum(
                    1 for row in selector_rows if row.holdout_beats_market
                ),
                beats_current_holdout_count=sum(
                    1 for row in selector_rows if row.holdout_beats_current_calibrated
                ),
                positive_ev_rank_holdout_count=sum(
                    1 for row in selector_rows if row.holdout_ev_rank_correlation_sign > 0.0
                ),
                positive_top_bucket_holdout_count=sum(
                    1 for row in selector_rows if row.holdout_top_ev_bucket_pnl_cents > 0.0
                ),
                strict_gate_holdout_count=strict_count,
                strict_all_holdouts=(strict_count == len(selector_rows) and bool(selector_rows)),
            )
        )
    return sorted(
        summaries,
        key=lambda row: (
            row.strict_all_holdouts,
            row.strict_gate_holdout_count,
            row.beats_current_holdout_count,
            row.total_holdout_pnl_cents,
        ),
        reverse=True,
    )


def _mean(values: Sequence[float] | object) -> float:
    vals = [float(value) for value in values]
    return sum(vals) / len(vals) if vals else 0.0


def _markdown(report: PASCThresholdLOROReport) -> str:
    lines = [
        "# PASC Threshold LORO Diagnostic",
        "",
        f"- run_count: {len(report.run_inputs)}",
        f"- variant_count: {len(report.variants)}",
        f"- holdout_row_count: {len(report.holdout_rows)}",
        f"- promotion_safe: {report.promotion_safe}",
        f"- conclusion: {report.conclusion}",
        "",
        "## Summary",
        "",
        "| selector | holdouts | total_pnl_cents | mean_brier | mean_log_loss | positive_pnl | beats_brownian | beats_market | beats_current | positive_ev_rank | positive_top_bucket | strict_gates | strict_all |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|",
    ]
    for row in report.selector_summary_rows:
        lines.append(
            "| "
            f"{row.selector} | "
            f"{row.holdout_count} | "
            f"{row.total_holdout_pnl_cents:.4f} | "
            f"{row.mean_holdout_brier:.6f} | "
            f"{row.mean_holdout_log_loss:.6f} | "
            f"{row.positive_pnl_holdout_count}/{row.holdout_count} | "
            f"{row.beats_brownian_holdout_count}/{row.holdout_count} | "
            f"{row.beats_market_holdout_count}/{row.holdout_count} | "
            f"{row.beats_current_holdout_count}/{row.holdout_count} | "
            f"{row.positive_ev_rank_holdout_count}/{row.holdout_count} | "
            f"{row.positive_top_bucket_holdout_count}/{row.holdout_count} | "
            f"{row.strict_gate_holdout_count}/{row.holdout_count} | "
            f"{row.strict_all_holdouts} |"
        )
    lines.extend(
        [
            "",
            "## Holdouts",
            "",
            "| selector | holdout | variant | min_ev | min_fill | train_pnl | train_pos_pnl | selected | holdout_pnl | brier | beats_brownian | beats_market | beats_current | ev_rank | top_bucket | strict |",
            "|---|---|---|---:|---:|---:|---:|---:|---:|---:|---|---|---|---:|---:|---|",
        ]
    )
    for row in report.holdout_rows:
        lines.append(
            "| "
            f"{row.selector} | "
            f"{row.holdout_run} | "
            f"{row.variant} | "
            f"{row.min_ev_cents:.4f} | "
            f"{row.min_fill_prob:.4f} | "
            f"{row.train_total_counterfactual_pnl_cents:.4f} | "
            f"{row.train_positive_pnl_run_count}/{row.train_run_count} | "
            f"{row.holdout_selected_count} | "
            f"{row.holdout_total_counterfactual_pnl_cents:.4f} | "
            f"{row.holdout_brier:.6f} | "
            f"{row.holdout_beats_brownian} | "
            f"{row.holdout_beats_market} | "
            f"{row.holdout_beats_current_calibrated} | "
            f"{row.holdout_ev_rank_correlation_sign:.6f} | "
            f"{row.holdout_top_ev_bucket_pnl_cents:.4f} | "
            f"{row.holdout_passes_strict_gates} |"
        )
    lines.extend(
        [
            "",
            "## Variants",
            "",
            ", ".join(f"`{variant}`" for variant in report.variants),
            "",
            "## Run Inputs",
            "",
            "| run | rows | markets | candidate_path | label_path |",
            "|---|---:|---:|---|---|",
        ]
    )
    for row in report.run_inputs:
        lines.append(
            "| "
            f"{row.name} | "
            f"{row.row_count} | "
            f"{row.market_count} | "
            f"`{row.candidate_path}` | "
            f"`{row.label_path}` |"
        )
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    raise SystemExit(main())
