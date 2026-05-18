from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass, replace
from pathlib import Path
from typing import Callable, Sequence

from .replay_runner import ReplayConfig, ReplayInput, ReplayReport, evaluate_replay
from .spot_rv_anchor_switch_loro import (
    HypothesisId,
    SpotRVAnchorRunInput,
    _AnchorRow,
    _load_eligible_run,
    _market_ev_metrics,
    _moneyness_bucket,
    _rv_disagreement_bucket,
    _time_bucket,
)
from .validation import brier_score, log_loss


COEFFICIENTS = (-0.50, -0.25, 0.0, 0.25, 0.50, 0.75, 1.0)
BucketFn = Callable[[_AnchorRow], str]


@dataclass(frozen=True)
class SpotRVResidualSpec:
    name: str
    bucket_fn: BucketFn


@dataclass(frozen=True)
class TrainedSpotRVResidual:
    spec: str
    train_run_count: int
    train_cluster_count: int
    min_bucket_clusters: int
    global_coefficient: float
    bucket_coefficients: dict[str, float]
    bucket_training_brier: dict[str, float]
    bucket_current_brier: dict[str, float]


@dataclass(frozen=True)
class SpotRVResidualHoldoutRow:
    holdout_run: str
    spec: str
    train_run_count: int
    train_cluster_count: int
    min_bucket_clusters: int
    global_coefficient: float
    bucket_count: int
    nudged_bucket_count: int
    holdout_candidate_count: int
    holdout_market_count: int
    selected_count: int
    total_counterfactual_pnl_cents: float
    brier: float
    log_loss: float
    beats_brownian: bool
    beats_market: bool
    beats_current_calibrated: bool
    ev_rank_correlation_sign: float
    top_ev_bucket_pnl_cents: float
    market_ev_rank_correlation_sign: float
    top_market_ev_bucket_avg_pnl_cents: float
    strict_gate_pass: bool


@dataclass(frozen=True)
class SpotRVResidualSummaryRow:
    spec: str
    holdout_count: int
    total_counterfactual_pnl_cents: float
    mean_brier: float
    mean_log_loss: float
    positive_pnl_count: int
    beats_brownian_count: int
    beats_market_count: int
    beats_current_count: int
    positive_ev_rank_count: int
    positive_top_bucket_count: int
    positive_market_ev_rank_count: int
    positive_market_top_bucket_count: int
    strict_gate_count: int
    strict_all_holdouts: bool


@dataclass(frozen=True)
class SpotRVCurrentResidualLOROReport:
    run_inputs: tuple[SpotRVAnchorRunInput, ...]
    skipped_run_roots: tuple[str, ...]
    hypothesis_id: HypothesisId
    coefficients: tuple[float, ...]
    specs: tuple[str, ...]
    min_bucket_clusters: int
    holdout_rows: tuple[SpotRVResidualHoldoutRow, ...]
    summary_rows: tuple[SpotRVResidualSummaryRow, ...]
    candidate_ready_for_predeclared_shadow: bool
    promotion_safe: bool
    conclusion: str


@dataclass(frozen=True)
class _ClusterSample:
    bucket: str
    label: int
    current_p_yes: float
    rv_terminal_p_yes: float


def build_spot_rv_current_residual_loro_report(
    run_roots: Sequence[Path],
    *,
    hypothesis_id: HypothesisId = "rv233_blend50_fixed65_terminal_v1",
    min_bucket_clusters: int = 3,
    replay_config: ReplayConfig | None = None,
) -> SpotRVCurrentResidualLOROReport:
    if len(run_roots) < 2:
        raise ValueError("at least two run roots are required")
    if min_bucket_clusters < 1:
        raise ValueError("min_bucket_clusters must be positive")
    cfg = replay_config or ReplayConfig(min_fill_prob=0.5, counterfactual_fill_threshold=0.5)
    loaded_runs: list[tuple[SpotRVAnchorRunInput, tuple[_AnchorRow, ...]]] = []
    skipped: list[str] = []
    for root in run_roots:
        loaded = _load_eligible_run(root, hypothesis_id=hypothesis_id)
        if loaded is None:
            skipped.append(str(root))
        else:
            loaded_runs.append(loaded)
    if len(loaded_runs) < 2:
        raise ValueError("at least two run roots with candidate snapshots and independent spot ticks are required")
    specs = _specs()
    holdout_rows: list[SpotRVResidualHoldoutRow] = []
    for holdout_meta, holdout_rows_raw in loaded_runs:
        train_rows = [
            item
            for train_meta, rows in loaded_runs
            if train_meta.name != holdout_meta.name
            for item in rows
        ]
        for spec in specs:
            model = _train_residual(
                spec,
                train_rows,
                train_run_count=len(loaded_runs) - 1,
                min_bucket_clusters=min_bucket_clusters,
            )
            variant_rows = _apply_residual(model, spec, holdout_rows_raw)
            replay = evaluate_replay(variant_rows, cfg)
            market_ev_rank, top_market_bucket = _market_ev_metrics(replay)
            strict = _strict_gate(replay)
            nudged = sum(1 for coef in model.bucket_coefficients.values() if coef != 0.0)
            holdout_rows.append(
                SpotRVResidualHoldoutRow(
                    holdout_run=holdout_meta.name,
                    spec=spec.name,
                    train_run_count=model.train_run_count,
                    train_cluster_count=model.train_cluster_count,
                    min_bucket_clusters=model.min_bucket_clusters,
                    global_coefficient=model.global_coefficient,
                    bucket_count=len(model.bucket_coefficients),
                    nudged_bucket_count=nudged,
                    holdout_candidate_count=replay.candidate_count,
                    holdout_market_count=holdout_meta.market_count,
                    selected_count=replay.selected_count,
                    total_counterfactual_pnl_cents=replay.total_counterfactual_pnl_cents,
                    brier=replay.particle.brier,
                    log_loss=replay.particle.log_loss,
                    beats_brownian=replay.particle_beats_brownian,
                    beats_market=replay.particle_beats_market,
                    beats_current_calibrated=replay.particle_beats_current_calibrated,
                    ev_rank_correlation_sign=replay.ev_rank_correlation_sign,
                    top_ev_bucket_pnl_cents=replay.top_ev_bucket_pnl_cents,
                    market_ev_rank_correlation_sign=market_ev_rank,
                    top_market_ev_bucket_avg_pnl_cents=top_market_bucket,
                    strict_gate_pass=strict,
                )
            )
    summaries = tuple(_summarize(holdout_rows))
    candidate_ready = any(row.strict_all_holdouts for row in summaries)
    conclusion = (
        "At least one conservative RV residual correction cleared every eligible locked holdout. "
        "Because this was selected after capture, it still only nominates a fresh predeclared shadow run."
        if candidate_ready
        else "No conservative RV residual correction cleared strict eligible locked holdout gates."
    )
    return SpotRVCurrentResidualLOROReport(
        run_inputs=tuple(meta for meta, _ in loaded_runs),
        skipped_run_roots=tuple(skipped),
        hypothesis_id=hypothesis_id,
        coefficients=COEFFICIENTS,
        specs=tuple(spec.name for spec in specs),
        min_bucket_clusters=min_bucket_clusters,
        holdout_rows=tuple(holdout_rows),
        summary_rows=summaries,
        candidate_ready_for_predeclared_shadow=candidate_ready,
        promotion_safe=False,
        conclusion=conclusion,
    )


def write_spot_rv_current_residual_loro_report(
    report: SpotRVCurrentResidualLOROReport,
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
        description="Leave-one-run-out conservative current + RV residual correction diagnostic."
    )
    parser.add_argument("--run-root", action="append", required=True, type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--stem", default="spot_rv_current_residual_loro")
    parser.add_argument("--hypothesis-id", default="rv233_blend50_fixed65_terminal_v1")
    parser.add_argument("--min-bucket-clusters", default=3, type=int)
    parser.add_argument("--min-fill-prob", default=0.5, type=float)
    parser.add_argument("--counterfactual-fill-threshold", default=0.5, type=float)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    report = build_spot_rv_current_residual_loro_report(
        args.run_root,
        hypothesis_id=args.hypothesis_id,
        min_bucket_clusters=args.min_bucket_clusters,
        replay_config=ReplayConfig(
            min_fill_prob=args.min_fill_prob,
            counterfactual_fill_threshold=args.counterfactual_fill_threshold,
        ),
    )
    json_path, md_path = write_spot_rv_current_residual_loro_report(report, args.output_dir, args.stem)
    print(f"eligible_run_count={len(report.run_inputs)}")
    print(f"skipped_run_count={len(report.skipped_run_roots)}")
    print(f"spec_count={len(report.specs)}")
    print(f"holdout_row_count={len(report.holdout_rows)}")
    print(f"summary_row_count={len(report.summary_rows)}")
    print(f"candidate_ready_for_predeclared_shadow={report.candidate_ready_for_predeclared_shadow}")
    print(f"promotion_safe={report.promotion_safe}")
    print(f"json_report={json_path}")
    print(f"md_report={md_path}")
    return 0


def _train_residual(
    spec: SpotRVResidualSpec,
    rows: Sequence[_AnchorRow],
    *,
    train_run_count: int,
    min_bucket_clusters: int,
) -> TrainedSpotRVResidual:
    samples = _cluster_samples(spec, rows)
    if not samples:
        raise ValueError("no training clusters")
    global_coefficient, global_brier, global_current_brier = _best_coefficient(samples)
    by_bucket: dict[str, list[_ClusterSample]] = {}
    for sample in samples:
        by_bucket.setdefault(sample.bucket, []).append(sample)
    bucket_coefficients: dict[str, float] = {}
    bucket_training_brier: dict[str, float] = {}
    bucket_current_brier: dict[str, float] = {}
    for bucket, bucket_samples in by_bucket.items():
        if len(bucket_samples) < min_bucket_clusters:
            continue
        coefficient, brier, current_brier = _best_coefficient(bucket_samples)
        bucket_coefficients[bucket] = coefficient
        bucket_training_brier[bucket] = brier
        bucket_current_brier[bucket] = current_brier
    return TrainedSpotRVResidual(
        spec=spec.name,
        train_run_count=train_run_count,
        train_cluster_count=len(samples),
        min_bucket_clusters=min_bucket_clusters,
        global_coefficient=global_coefficient,
        bucket_coefficients=bucket_coefficients,
        bucket_training_brier={"global": global_brier, **bucket_training_brier},
        bucket_current_brier={"global": global_current_brier, **bucket_current_brier},
    )


def _cluster_samples(spec: SpotRVResidualSpec, rows: Sequence[_AnchorRow]) -> list[_ClusterSample]:
    grouped: dict[tuple[str, str], list[_AnchorRow]] = {}
    for item in rows:
        grouped.setdefault((item.row.snapshot.market_ticker, spec.bucket_fn(item)), []).append(item)
    samples: list[_ClusterSample] = []
    for (_, bucket), bucket_rows in grouped.items():
        samples.append(
            _ClusterSample(
                bucket=bucket,
                label=1 if bucket_rows[0].row.label.result_yes else 0,
                current_p_yes=_mean(item.row.current_calibrated_p_yes for item in bucket_rows),
                rv_terminal_p_yes=_mean(item.rv_terminal_p_yes for item in bucket_rows),
            )
        )
    return samples


def _best_coefficient(samples: Sequence[_ClusterSample]) -> tuple[float, float, float]:
    labels = [sample.label for sample in samples]
    current_probs = [sample.current_p_yes for sample in samples]
    current_brier = brier_score(current_probs, labels)
    candidates: list[tuple[float, float, float]] = []
    for coefficient in COEFFICIENTS:
        probs = [_residual_probability(sample.current_p_yes, sample.rv_terminal_p_yes, coefficient) for sample in samples]
        candidates.append((brier_score(probs, labels), abs(coefficient), coefficient))
    best_brier, _, best_coefficient = min(candidates)
    if best_brier >= current_brier:
        return 0.0, current_brier, current_brier
    return best_coefficient, best_brier, current_brier


def _apply_residual(
    model: TrainedSpotRVResidual,
    spec: SpotRVResidualSpec,
    rows: Sequence[_AnchorRow],
) -> list[ReplayInput]:
    variant: list[ReplayInput] = []
    for item in rows:
        bucket = spec.bucket_fn(item)
        # Conservative default: if this bucket did not have enough training
        # clusters, do not let a global residual nudge leak into it.
        coefficient = model.bucket_coefficients.get(bucket, 0.0)
        p_yes = _residual_probability(item.row.current_calibrated_p_yes, item.rv_terminal_p_yes, coefficient)
        variant.append(replace(item.row, particle_p_yes=p_yes))
    return variant


def _residual_probability(current_p_yes: float, rv_terminal_p_yes: float, coefficient: float) -> float:
    return min(1.0, max(0.0, current_p_yes + coefficient * (rv_terminal_p_yes - current_p_yes)))


def _strict_gate(report: ReplayReport) -> bool:
    return (
        report.total_counterfactual_pnl_cents > 0.0
        and report.particle_beats_brownian
        and report.particle_beats_market
        and report.particle_beats_current_calibrated
        and report.ev_rank_correlation_sign > 0.0
        and report.top_ev_bucket_pnl_cents > 0.0
    )


def _summarize(rows: Sequence[SpotRVResidualHoldoutRow]) -> list[SpotRVResidualSummaryRow]:
    grouped: dict[str, list[SpotRVResidualHoldoutRow]] = {}
    for row in rows:
        grouped.setdefault(row.spec, []).append(row)
    summaries: list[SpotRVResidualSummaryRow] = []
    for spec in sorted(grouped):
        spec_rows = grouped[spec]
        strict_count = sum(1 for row in spec_rows if row.strict_gate_pass)
        summaries.append(
            SpotRVResidualSummaryRow(
                spec=spec,
                holdout_count=len(spec_rows),
                total_counterfactual_pnl_cents=sum(row.total_counterfactual_pnl_cents for row in spec_rows),
                mean_brier=_mean(row.brier for row in spec_rows),
                mean_log_loss=_mean(row.log_loss for row in spec_rows),
                positive_pnl_count=sum(1 for row in spec_rows if row.total_counterfactual_pnl_cents > 0.0),
                beats_brownian_count=sum(1 for row in spec_rows if row.beats_brownian),
                beats_market_count=sum(1 for row in spec_rows if row.beats_market),
                beats_current_count=sum(1 for row in spec_rows if row.beats_current_calibrated),
                positive_ev_rank_count=sum(1 for row in spec_rows if row.ev_rank_correlation_sign > 0.0),
                positive_top_bucket_count=sum(1 for row in spec_rows if row.top_ev_bucket_pnl_cents > 0.0),
                positive_market_ev_rank_count=sum(1 for row in spec_rows if row.market_ev_rank_correlation_sign > 0.0),
                positive_market_top_bucket_count=sum(
                    1 for row in spec_rows if row.top_market_ev_bucket_avg_pnl_cents > 0.0
                ),
                strict_gate_count=strict_count,
                strict_all_holdouts=(strict_count == len(spec_rows) and bool(spec_rows)),
            )
        )
    return sorted(
        summaries,
        key=lambda row: (
            row.strict_all_holdouts,
            row.strict_gate_count,
            row.beats_current_count,
            row.total_counterfactual_pnl_cents,
        ),
        reverse=True,
    )


def _specs() -> tuple[SpotRVResidualSpec, ...]:
    return (
        SpotRVResidualSpec("global", lambda item: "all"),
        SpotRVResidualSpec("time", lambda item: _time_bucket(item.row)),
        SpotRVResidualSpec("moneyness", lambda item: _moneyness_bucket(item.row)),
        SpotRVResidualSpec("rv_disagreement", lambda item: _rv_disagreement_bucket(item)),
        SpotRVResidualSpec("time_rv_disagreement", lambda item: f"{_time_bucket(item.row)}|{_rv_disagreement_bucket(item)}"),
        SpotRVResidualSpec(
            "time_moneyness_rv_disagreement",
            lambda item: f"{_time_bucket(item.row)}|{_moneyness_bucket(item.row)}|{_rv_disagreement_bucket(item)}",
        ),
    )


def _mean(values) -> float:
    seq = [float(value) for value in values]
    return sum(seq) / len(seq) if seq else 0.0


def _markdown(report: SpotRVCurrentResidualLOROReport) -> str:
    lines = [
        "# Spot RV Current Residual LORO Report",
        "",
        f"- eligible_run_count: {len(report.run_inputs)}",
        f"- skipped_run_count: {len(report.skipped_run_roots)}",
        f"- hypothesis_id: {report.hypothesis_id}",
        f"- coefficients: {', '.join(str(value) for value in report.coefficients)}",
        f"- spec_count: {len(report.specs)}",
        f"- min_bucket_clusters: {report.min_bucket_clusters}",
        f"- candidate_ready_for_predeclared_shadow: {report.candidate_ready_for_predeclared_shadow}",
        f"- promotion_safe: {report.promotion_safe}",
        f"- conclusion: {report.conclusion}",
        "",
        "## Summary",
        "",
        "| spec | holdouts | pnl_cents | mean_brier | mean_log_loss | positive_pnl | beats_brownian | beats_market | beats_current | ev_rank | top_bucket | market_ev_rank | market_top_bucket | strict | strict_all |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|",
    ]
    for row in report.summary_rows:
        lines.append(
            "| "
            f"{row.spec} | "
            f"{row.holdout_count} | "
            f"{row.total_counterfactual_pnl_cents:.4f} | "
            f"{row.mean_brier:.6f} | "
            f"{row.mean_log_loss:.6f} | "
            f"{row.positive_pnl_count}/{row.holdout_count} | "
            f"{row.beats_brownian_count}/{row.holdout_count} | "
            f"{row.beats_market_count}/{row.holdout_count} | "
            f"{row.beats_current_count}/{row.holdout_count} | "
            f"{row.positive_ev_rank_count}/{row.holdout_count} | "
            f"{row.positive_top_bucket_count}/{row.holdout_count} | "
            f"{row.positive_market_ev_rank_count}/{row.holdout_count} | "
            f"{row.positive_market_top_bucket_count}/{row.holdout_count} | "
            f"{row.strict_gate_count}/{row.holdout_count} | "
            f"{row.strict_all_holdouts} |"
        )
    lines.extend(
        [
            "",
            "## Holdouts",
            "",
            "| holdout | spec | global_coef | buckets | nudged | selected | pnl_cents | brier | beats_current | ev_rank | top_bucket | market_ev_rank | market_top_bucket | strict |",
            "|---|---|---:|---:|---:|---:|---:|---:|---|---:|---:|---:|---:|---|",
        ]
    )
    for row in report.holdout_rows:
        lines.append(
            "| "
            f"{row.holdout_run} | "
            f"{row.spec} | "
            f"{row.global_coefficient:.2f} | "
            f"{row.bucket_count} | "
            f"{row.nudged_bucket_count} | "
            f"{row.selected_count} | "
            f"{row.total_counterfactual_pnl_cents:.4f} | "
            f"{row.brier:.6f} | "
            f"{row.beats_current_calibrated} | "
            f"{row.ev_rank_correlation_sign:.6f} | "
            f"{row.top_ev_bucket_pnl_cents:.4f} | "
            f"{row.market_ev_rank_correlation_sign:.6f} | "
            f"{row.top_market_ev_bucket_avg_pnl_cents:.4f} | "
            f"{row.strict_gate_pass} |"
        )
    lines.extend(["", "## Run Inputs", "", "| run | rows | markets | spot_ticks | fallback_rows |", "|---|---:|---:|---:|---:|"])
    for row in report.run_inputs:
        lines.append(
            "| "
            f"{row.name} | "
            f"{row.row_count} | "
            f"{row.market_count} | "
            f"{row.spot_tick_count} | "
            f"{row.rv_fallback_row_count} |"
        )
    if report.skipped_run_roots:
        lines.extend(["", "## Skipped Runs", ""])
        for root in report.skipped_run_roots:
            lines.append(f"- `{root}`")
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    raise SystemExit(main())
