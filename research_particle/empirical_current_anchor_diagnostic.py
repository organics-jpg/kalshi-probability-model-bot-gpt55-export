from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass, replace
from pathlib import Path
from typing import Sequence

from .empirical_next_second_particle_diagnostic import (
    EmpiricalSecondParticleSpec,
    build_second_return_cache,
    empirical_second_particle_probability,
    _load_eligible_run,
)
from .replay_runner import ReplayConfig, ReplayInput, ReplayReport, evaluate_replay
from .spot_context_merge import SpotTickRow
from .spot_rv_anchor_switch_loro import _market_ev_metrics


@dataclass(frozen=True)
class EmpiricalCurrentAnchorSpec:
    name: str
    empirical_spec: EmpiricalSecondParticleSpec
    empirical_weight: float


@dataclass(frozen=True)
class EmpiricalCurrentAnchorRunInput:
    name: str
    root: str
    candidate_path: str
    label_path: str
    spot_tick_path: str
    row_count: int
    market_count: int
    spot_tick_count: int


@dataclass(frozen=True)
class EmpiricalCurrentAnchorRunRow:
    run: str
    spec: str
    candidate_count: int
    market_count: int
    selected_count: int
    fallback_to_current_count: int
    avg_return_count: float
    avg_spot_age_ms: float
    avg_empirical_ann_vol: float
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
class EmpiricalCurrentAnchorSummaryRow:
    spec: str
    run_count: int
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
    strict_all_runs: bool
    fallback_to_current_count: int
    avg_return_count: float
    avg_spot_age_ms: float
    avg_empirical_ann_vol: float


@dataclass(frozen=True)
class EmpiricalCurrentAnchorDiagnosticReport:
    run_inputs: tuple[EmpiricalCurrentAnchorRunInput, ...]
    skipped_run_roots: tuple[str, ...]
    specs: tuple[EmpiricalCurrentAnchorSpec, ...]
    run_rows: tuple[EmpiricalCurrentAnchorRunRow, ...]
    summary_rows: tuple[EmpiricalCurrentAnchorSummaryRow, ...]
    candidate_ready_for_predeclared_shadow: bool
    promotion_safe: bool
    conclusion: str


def build_empirical_current_anchor_diagnostic(
    run_roots: Sequence[Path],
    *,
    replay_config: ReplayConfig | None = None,
    max_spot_age_ms: float = 5_000.0,
) -> EmpiricalCurrentAnchorDiagnosticReport:
    cfg = replay_config or ReplayConfig(min_fill_prob=0.5, counterfactual_fill_threshold=0.5)
    loaded_runs: list[tuple[EmpiricalCurrentAnchorRunInput, tuple[ReplayInput, ...], tuple[SpotTickRow, ...]]] = []
    skipped: list[str] = []
    for root in run_roots:
        loaded = _load_eligible_run(root)
        if loaded is None:
            skipped.append(str(root))
            continue
        meta, rows, ticks = loaded
        loaded_runs.append(
            (
                EmpiricalCurrentAnchorRunInput(
                    name=meta.name,
                    root=meta.root,
                    candidate_path=meta.candidate_path,
                    label_path=meta.label_path,
                    spot_tick_path=meta.spot_tick_path,
                    row_count=meta.row_count,
                    market_count=meta.market_count,
                    spot_tick_count=meta.spot_tick_count,
                ),
                rows,
                ticks,
            )
        )

    specs = _specs()
    run_rows: list[EmpiricalCurrentAnchorRunRow] = []
    for meta, rows, ticks in loaded_runs:
        times = [tick.available_ts_utc for tick in ticks]
        prices = [float(tick.price) for tick in ticks]
        for spec in specs:
            materialized, diagnostics = materialize_empirical_current_anchor_rows(
                rows,
                ticks,
                spec,
                run_name=meta.name,
                max_spot_age_ms=max_spot_age_ms,
            )
            replay = evaluate_replay(materialized, cfg)
            market_ev_rank, top_market_bucket = _market_ev_metrics(replay)
            run_rows.append(
                EmpiricalCurrentAnchorRunRow(
                    run=meta.name,
                    spec=spec.name,
                    candidate_count=replay.candidate_count,
                    market_count=meta.market_count,
                    selected_count=replay.selected_count,
                    fallback_to_current_count=int(diagnostics["fallback_to_current_count"]),
                    avg_return_count=float(diagnostics["avg_return_count"]),
                    avg_spot_age_ms=float(diagnostics["avg_spot_age_ms"]),
                    avg_empirical_ann_vol=float(diagnostics["avg_empirical_ann_vol"]),
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
                    strict_gate_pass=_strict_gate(replay),
                )
            )
    summaries = tuple(_summarize(run_rows))
    candidate_ready = any(row.strict_all_runs for row in summaries)
    conclusion = (
        "At least one current-anchored empirical next-second spec cleared every eligible locked run. "
        "Because this is same-evidence research, it only nominates a fresh predeclared shadow run."
        if candidate_ready
        else "No current-anchored empirical next-second spec cleared strict eligible locked-run gates."
    )
    return EmpiricalCurrentAnchorDiagnosticReport(
        run_inputs=tuple(meta for meta, _, _ in loaded_runs),
        skipped_run_roots=tuple(skipped),
        specs=specs,
        run_rows=tuple(run_rows),
        summary_rows=summaries,
        candidate_ready_for_predeclared_shadow=candidate_ready,
        promotion_safe=False,
        conclusion=conclusion,
    )


def materialize_empirical_current_anchor_rows(
    rows: Sequence[ReplayInput],
    ticks: Sequence[SpotTickRow],
    spec: EmpiricalCurrentAnchorSpec,
    *,
    run_name: str = "",
    max_spot_age_ms: float = 5_000.0,
) -> tuple[tuple[ReplayInput, ...], dict[str, float | int]]:
    if not rows:
        raise ValueError("at least one replay row is required")
    if not 0.0 <= spec.empirical_weight <= 1.0:
        raise ValueError("empirical_weight must be in [0, 1]")
    times = [tick.available_ts_utc for tick in ticks]
    prices = [float(tick.price) for tick in ticks]
    return_cache = build_second_return_cache(times, prices)
    materialized: list[ReplayInput] = []
    fallback_count = 0
    return_counts: list[float] = []
    spot_ages: list[float] = []
    empirical_vols: list[float] = []
    for row in sorted(rows, key=lambda item: (item.snapshot.decision_ts_utc, item.snapshot.market_ticker)):
        result = empirical_second_particle_probability(
            row,
            times,
            prices,
            spec.empirical_spec,
            run_name=run_name,
            max_spot_age_ms=max_spot_age_ms,
            return_cache=return_cache,
        )
        fallback_count += int(result.used_fallback)
        return_counts.append(float(result.return_count))
        spot_ages.append(float(result.spot_age_ms))
        empirical_vols.append(float(result.empirical_ann_vol))
        if result.used_fallback:
            p_yes = row.current_calibrated_p_yes
        else:
            p_yes = (
                (1.0 - spec.empirical_weight) * row.current_calibrated_p_yes
                + spec.empirical_weight * result.probability_yes
            )
        materialized.append(replace(row, particle_p_yes=_clamp01(p_yes)))
    return (
        tuple(materialized),
        {
            "fallback_to_current_count": fallback_count,
            "avg_return_count": _mean(return_counts),
            "avg_spot_age_ms": _mean(spot_ages),
            "avg_empirical_ann_vol": _mean(empirical_vols),
        },
    )


def write_empirical_current_anchor_diagnostic(
    report: EmpiricalCurrentAnchorDiagnosticReport,
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
        description="Evaluate current-anchored empirical next-second particle probabilities."
    )
    parser.add_argument("--run-root", action="append", required=True, type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--stem", default="empirical_current_anchor_diagnostic")
    parser.add_argument("--max-spot-age-ms", default=5_000.0, type=float)
    parser.add_argument("--min-fill-prob", default=0.5, type=float)
    parser.add_argument("--counterfactual-fill-threshold", default=0.5, type=float)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    report = build_empirical_current_anchor_diagnostic(
        args.run_root,
        replay_config=ReplayConfig(
            min_fill_prob=args.min_fill_prob,
            counterfactual_fill_threshold=args.counterfactual_fill_threshold,
        ),
        max_spot_age_ms=args.max_spot_age_ms,
    )
    json_path, md_path = write_empirical_current_anchor_diagnostic(report, args.output_dir, args.stem)
    print(f"eligible_run_count={len(report.run_inputs)}")
    print(f"skipped_run_count={len(report.skipped_run_roots)}")
    print(f"spec_count={len(report.specs)}")
    print(f"run_row_count={len(report.run_rows)}")
    print(f"summary_row_count={len(report.summary_rows)}")
    print(f"candidate_ready_for_predeclared_shadow={report.candidate_ready_for_predeclared_shadow}")
    print(f"promotion_safe={report.promotion_safe}")
    print(f"json_report={json_path}")
    print(f"md_report={md_path}")
    return 0


def _specs() -> tuple[EmpiricalCurrentAnchorSpec, ...]:
    return (
        EmpiricalCurrentAnchorSpec(
            "current_emp610_w10_center",
            EmpiricalSecondParticleSpec("inner_emp610_center", 610, 96, 48, 233.0, 5.0, 0.0, 0.0, 30),
            0.10,
        ),
        EmpiricalCurrentAnchorSpec(
            "current_emp610_w25_center",
            EmpiricalSecondParticleSpec("inner_emp610_center", 610, 96, 48, 233.0, 5.0, 0.0, 0.0, 30),
            0.25,
        ),
        EmpiricalCurrentAnchorSpec(
            "current_emp987_w10_mean25",
            EmpiricalSecondParticleSpec("inner_emp987_mean25", 987, 128, 64, 377.0, 7.5, 0.25, 0.0, 40),
            0.10,
        ),
        EmpiricalCurrentAnchorSpec(
            "current_emp987_w25_mean25",
            EmpiricalSecondParticleSpec("inner_emp987_mean25", 987, 128, 64, 377.0, 7.5, 0.25, 0.0, 40),
            0.25,
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


def _summarize(rows: Sequence[EmpiricalCurrentAnchorRunRow]) -> list[EmpiricalCurrentAnchorSummaryRow]:
    grouped: dict[str, list[EmpiricalCurrentAnchorRunRow]] = {}
    for row in rows:
        grouped.setdefault(row.spec, []).append(row)
    summaries: list[EmpiricalCurrentAnchorSummaryRow] = []
    for spec in sorted(grouped):
        spec_rows = grouped[spec]
        strict_count = sum(1 for row in spec_rows if row.strict_gate_pass)
        summaries.append(
            EmpiricalCurrentAnchorSummaryRow(
                spec=spec,
                run_count=len(spec_rows),
                total_counterfactual_pnl_cents=sum(row.total_counterfactual_pnl_cents for row in spec_rows),
                mean_brier=_mean(row.brier for row in spec_rows),
                mean_log_loss=_mean(row.log_loss for row in spec_rows),
                positive_pnl_count=sum(1 for row in spec_rows if row.total_counterfactual_pnl_cents > 0.0),
                beats_brownian_count=sum(1 for row in spec_rows if row.beats_brownian),
                beats_market_count=sum(1 for row in spec_rows if row.beats_market),
                beats_current_count=sum(1 for row in spec_rows if row.beats_current_calibrated),
                positive_ev_rank_count=sum(1 for row in spec_rows if row.ev_rank_correlation_sign > 0.0),
                positive_top_bucket_count=sum(1 for row in spec_rows if row.top_ev_bucket_pnl_cents > 0.0),
                positive_market_ev_rank_count=sum(
                    1 for row in spec_rows if row.market_ev_rank_correlation_sign > 0.0
                ),
                positive_market_top_bucket_count=sum(
                    1 for row in spec_rows if row.top_market_ev_bucket_avg_pnl_cents > 0.0
                ),
                strict_gate_count=strict_count,
                strict_all_runs=(strict_count == len(spec_rows) and bool(spec_rows)),
                fallback_to_current_count=sum(row.fallback_to_current_count for row in spec_rows),
                avg_return_count=_mean(row.avg_return_count for row in spec_rows),
                avg_spot_age_ms=_mean(row.avg_spot_age_ms for row in spec_rows),
                avg_empirical_ann_vol=_mean(row.avg_empirical_ann_vol for row in spec_rows),
            )
        )
    return sorted(
        summaries,
        key=lambda row: (
            row.strict_all_runs,
            row.strict_gate_count,
            row.beats_current_count,
            row.total_counterfactual_pnl_cents,
        ),
        reverse=True,
    )


def _markdown(report: EmpiricalCurrentAnchorDiagnosticReport) -> str:
    lines = [
        "# Empirical Current-Anchor Diagnostic",
        "",
        f"- eligible_run_count: {len(report.run_inputs)}",
        f"- skipped_run_count: {len(report.skipped_run_roots)}",
        f"- spec_count: {len(report.specs)}",
        f"- candidate_ready_for_predeclared_shadow: {report.candidate_ready_for_predeclared_shadow}",
        f"- promotion_safe: {report.promotion_safe}",
        f"- conclusion: {report.conclusion}",
        "",
        "## Summary",
        "",
        "| spec | runs | pnl_cents | mean_brier | mean_log_loss | positive_pnl | beats_brownian | beats_market | beats_current | ev_rank | top_bucket | market_ev_rank | market_top_bucket | strict | fallback_current | avg_returns | avg_spot_age_ms | avg_ann_vol | strict_all |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|",
    ]
    for row in report.summary_rows:
        lines.append(
            "| "
            f"{row.spec} | "
            f"{row.run_count} | "
            f"{row.total_counterfactual_pnl_cents:.4f} | "
            f"{row.mean_brier:.6f} | "
            f"{row.mean_log_loss:.6f} | "
            f"{row.positive_pnl_count}/{row.run_count} | "
            f"{row.beats_brownian_count}/{row.run_count} | "
            f"{row.beats_market_count}/{row.run_count} | "
            f"{row.beats_current_count}/{row.run_count} | "
            f"{row.positive_ev_rank_count}/{row.run_count} | "
            f"{row.positive_top_bucket_count}/{row.run_count} | "
            f"{row.positive_market_ev_rank_count}/{row.run_count} | "
            f"{row.positive_market_top_bucket_count}/{row.run_count} | "
            f"{row.strict_gate_count}/{row.run_count} | "
            f"{row.fallback_to_current_count} | "
            f"{row.avg_return_count:.2f} | "
            f"{row.avg_spot_age_ms:.2f} | "
            f"{row.avg_empirical_ann_vol:.6f} | "
            f"{row.strict_all_runs} |"
        )
    lines.extend(
        [
            "",
            "## Runs",
            "",
            "| run | spec | candidates | markets | selected | fallback_current | avg_returns | avg_spot_age_ms | avg_ann_vol | pnl_cents | brier | beats_current | ev_rank | top_bucket | market_ev_rank | market_top_bucket | strict |",
            "|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|---:|---:|---:|---:|---|",
        ]
    )
    for row in report.run_rows:
        lines.append(
            "| "
            f"{row.run} | "
            f"{row.spec} | "
            f"{row.candidate_count} | "
            f"{row.market_count} | "
            f"{row.selected_count} | "
            f"{row.fallback_to_current_count} | "
            f"{row.avg_return_count:.2f} | "
            f"{row.avg_spot_age_ms:.2f} | "
            f"{row.avg_empirical_ann_vol:.6f} | "
            f"{row.total_counterfactual_pnl_cents:.4f} | "
            f"{row.brier:.6f} | "
            f"{row.beats_current_calibrated} | "
            f"{row.ev_rank_correlation_sign:.6f} | "
            f"{row.top_ev_bucket_pnl_cents:.4f} | "
            f"{row.market_ev_rank_correlation_sign:.6f} | "
            f"{row.top_market_ev_bucket_avg_pnl_cents:.4f} | "
            f"{row.strict_gate_pass} |"
        )
    lines.extend(["", "## Run Inputs", "", "| run | rows | markets | spot_ticks |", "|---|---:|---:|---:|"])
    for row in report.run_inputs:
        lines.append(f"| {row.name} | {row.row_count} | {row.market_count} | {row.spot_tick_count} |")
    if report.skipped_run_roots:
        lines.extend(["", "## Skipped Runs", ""])
        lines.extend(f"- `{root}`" for root in report.skipped_run_roots)
    return "\n".join(lines) + "\n"


def _mean(values) -> float:
    seq = [float(value) for value in values]
    return sum(seq) / len(seq) if seq else 0.0


def _clamp01(value: float) -> float:
    return min(1.0, max(0.0, float(value)))


if __name__ == "__main__":
    raise SystemExit(main())
