from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass, replace
from pathlib import Path
from statistics import median
from typing import Callable, Mapping, Sequence

from .dynamic_particle_replay import DynamicParticleSpec, RollingVolEstimator
from .replay_runner import (
    ReplayConfig,
    ReplayInput,
    evaluate_replay,
    load_replay_inputs_from_jsonl,
)
from .terminal_projection import brownian_terminal_probability


VariantContext = Mapping[str, float]
EnsembleFn = Callable[[VariantContext], float]


@dataclass(frozen=True)
class EnsembleParticleRow:
    name: str
    candidate_count: int
    selected_count: int
    coverage_rate: float
    total_counterfactual_pnl_cents: float
    avg_counterfactual_pnl_cents_per_candidate: float
    avg_counterfactual_pnl_cents_per_selected: float
    brier: float
    log_loss: float
    beats_brownian: bool
    beats_market: bool
    beats_current_calibrated: bool
    ev_rank_correlation_sign: float
    top_ev_bucket_pnl_cents: float


@dataclass(frozen=True)
class EnsembleParticleReport:
    candidate_count: int
    source_candidate_count: int | None
    skipped_unlabeled_count: int
    denominator_scope: str
    all_candidate_denominator: bool
    rows: tuple[EnsembleParticleRow, ...]
    best_by_brier: EnsembleParticleRow
    best_by_pnl: EnsembleParticleRow
    promotion_safe: bool
    note: str


def evaluate_ensemble_particle_variants(
    rows: Sequence[ReplayInput],
    config: ReplayConfig | None = None,
) -> EnsembleParticleReport:
    if not rows:
        raise ValueError("at least one replay row is required")
    cfg = config or ReplayConfig()
    sorted_rows = sorted(rows, key=lambda row: (row.snapshot.decision_ts_utc, row.snapshot.market_ticker))
    contexts = _variant_contexts(sorted_rows)
    summaries: list[EnsembleParticleRow] = []
    for name, fn in _ensemble_registry():
        variant_rows = [
            replace(row, particle_p_yes=_clamp01(fn(context)))
            for row, context in zip(sorted_rows, contexts)
        ]
        report = evaluate_replay(variant_rows, cfg)
        summaries.append(
            EnsembleParticleRow(
                name=name,
                candidate_count=report.candidate_count,
                selected_count=report.selected_count,
                coverage_rate=report.selected_count / report.candidate_count,
                total_counterfactual_pnl_cents=report.total_counterfactual_pnl_cents,
                avg_counterfactual_pnl_cents_per_candidate=(
                    report.avg_counterfactual_pnl_cents_per_candidate
                ),
                avg_counterfactual_pnl_cents_per_selected=(
                    report.avg_counterfactual_pnl_cents_per_selected
                ),
                brier=report.particle.brier,
                log_loss=report.particle.log_loss,
                beats_brownian=report.particle_beats_brownian,
                beats_market=report.particle_beats_market,
                beats_current_calibrated=report.particle_beats_current_calibrated,
                ev_rank_correlation_sign=report.ev_rank_correlation_sign,
                top_ev_bucket_pnl_cents=report.top_ev_bucket_pnl_cents,
            )
        )
    best_by_brier = min(summaries, key=lambda row: (row.brier, row.log_loss))
    best_by_pnl = max(summaries, key=lambda row: row.total_counterfactual_pnl_cents)
    return EnsembleParticleReport(
        candidate_count=len(sorted_rows),
        source_candidate_count=None,
        skipped_unlabeled_count=0,
        denominator_scope="all_labeled_candidates",
        all_candidate_denominator=True,
        rows=tuple(summaries),
        best_by_brier=best_by_brier,
        best_by_pnl=best_by_pnl,
        promotion_safe=False,
        note=(
            "Ensemble variants are stability diagnostics only. Selecting one "
            "from locked-run summaries creates a new hypothesis that still "
            "requires a fresh predeclared locked OOS run."
        ),
    )


def write_ensemble_particle_report(
    report: EnsembleParticleReport,
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
        description="Evaluate fixed conservative ensemble probability variants on a strict labeled denominator."
    )
    parser.add_argument("--candidates", required=True, type=Path)
    parser.add_argument("--labels", required=True, type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--stem", default="ensemble_particle_replay")
    parser.add_argument("--min-ev-cents", default=0.0, type=float)
    parser.add_argument("--min-fill-prob", default=0.0, type=float)
    parser.add_argument("--no-fill-penalty-cents", default=0.0, type=float)
    parser.add_argument(
        "--counterfactual-fill-policy",
        choices=["threshold", "always_fill", "never_fill"],
        default="threshold",
    )
    parser.add_argument("--counterfactual-fill-threshold", default=0.5, type=float)
    parser.add_argument("--default-annualized-vol", default=None, type=float)
    parser.add_argument("--allow-missing-labels", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    rows = load_replay_inputs_from_jsonl(
        args.candidates,
        args.labels,
        default_annualized_vol=args.default_annualized_vol,
        allow_missing_labels=bool(args.allow_missing_labels),
    )
    source_candidate_count = _line_count(args.candidates)
    skipped_unlabeled_count = max(0, source_candidate_count - len(rows))
    denominator_scope = "resolved_labeled_subset" if args.allow_missing_labels else "all_labeled_candidates"
    report = replace(
        evaluate_ensemble_particle_variants(
            rows,
            ReplayConfig(
                min_ev_cents=args.min_ev_cents,
                min_fill_prob=args.min_fill_prob,
                no_fill_penalty_cents=args.no_fill_penalty_cents,
                counterfactual_fill_policy=args.counterfactual_fill_policy,
                counterfactual_fill_threshold=args.counterfactual_fill_threshold,
            ),
        ),
        source_candidate_count=source_candidate_count,
        skipped_unlabeled_count=skipped_unlabeled_count,
        denominator_scope=denominator_scope,
    )
    json_path, md_path = write_ensemble_particle_report(report, args.output_dir, args.stem)
    print(f"candidate_count={report.candidate_count}")
    print(f"source_candidate_count={report.source_candidate_count}")
    print(f"skipped_unlabeled_count={report.skipped_unlabeled_count}")
    print(f"denominator_scope={report.denominator_scope}")
    print(f"best_by_brier={report.best_by_brier.name}")
    print(f"best_by_brier_brier={report.best_by_brier.brier:.6f}")
    print(f"best_by_pnl={report.best_by_pnl.name}")
    print(f"best_by_pnl_total_counterfactual_pnl_cents={report.best_by_pnl.total_counterfactual_pnl_cents:.4f}")
    print(f"promotion_safe={report.promotion_safe}")
    print(f"json_report={json_path}")
    print(f"md_report={md_path}")
    return 0


def _variant_contexts(rows: Sequence[ReplayInput]) -> list[dict[str, float]]:
    specs = (
        DynamicParticleSpec(
            name="rv300",
            lookback_seconds=300.0,
            fallback_annualized_vol=0.65,
            min_annualized_vol=0.20,
            max_annualized_vol=2.50,
            min_distinct_observations=3,
        ),
        DynamicParticleSpec(
            name="rv600",
            lookback_seconds=600.0,
            fallback_annualized_vol=0.65,
            min_annualized_vol=0.20,
            max_annualized_vol=2.50,
            min_distinct_observations=3,
        ),
    )
    estimators = {spec.name: RollingVolEstimator(spec) for spec in specs}
    contexts: list[dict[str, float]] = []
    for row in rows:
        seconds_to_close = max(
            0.0,
            (row.label.settlement_ts_utc - row.snapshot.decision_ts_utc).total_seconds(),
        )
        dynamic: dict[str, float] = {}
        for spec in specs:
            vol = estimators[spec.name].observe_and_estimate(
                row.snapshot.decision_ts_utc,
                row.snapshot.spot,
            )
            dynamic[spec.name] = brownian_terminal_probability(
                row.snapshot.spot,
                row.snapshot.strike,
                seconds_to_close,
                vol,
            )
        contexts.append(
            {
                "particle": row.particle_p_yes,
                "brownian": row.brownian_p_yes,
                "market": row.market_p_yes,
                "current": row.current_calibrated_p_yes,
                **dynamic,
            }
        )
    return contexts


def _ensemble_registry() -> tuple[tuple[str, EnsembleFn], ...]:
    return (
        (
            "median_current_rv300_rv600",
            lambda ctx: median((ctx["current"], ctx["rv300"], ctx["rv600"])),
        ),
        (
            "mean_current_rv300_rv600",
            lambda ctx: (ctx["current"] + ctx["rv300"] + ctx["rv600"]) / 3.0,
        ),
        (
            "blend_40current_30rv300_30rv600",
            lambda ctx: 0.40 * ctx["current"] + 0.30 * ctx["rv300"] + 0.30 * ctx["rv600"],
        ),
        (
            "blend_50rv600_30current_20market",
            lambda ctx: 0.50 * ctx["rv600"] + 0.30 * ctx["current"] + 0.20 * ctx["market"],
        ),
        (
            "blend_40rv600_30rv300_20current_10market",
            lambda ctx: (
                0.40 * ctx["rv600"]
                + 0.30 * ctx["rv300"]
                + 0.20 * ctx["current"]
                + 0.10 * ctx["market"]
            ),
        ),
        (
            "median_market_current_rv600",
            lambda ctx: median((ctx["market"], ctx["current"], ctx["rv600"])),
        ),
        (
            "mean_market_current_rv300_rv600",
            lambda ctx: (ctx["market"] + ctx["current"] + ctx["rv300"] + ctx["rv600"]) / 4.0,
        ),
        (
            "blend_50current_25particle_25rv600",
            lambda ctx: 0.50 * ctx["current"] + 0.25 * ctx["particle"] + 0.25 * ctx["rv600"],
        ),
    )


def _markdown(report: EnsembleParticleReport) -> str:
    lines = [
        "# Ensemble Particle Replay Report",
        "",
        f"- candidate_count: {report.candidate_count}",
        f"- source_candidate_count: {report.source_candidate_count}",
        f"- skipped_unlabeled_count: {report.skipped_unlabeled_count}",
        f"- denominator_scope: {report.denominator_scope}",
        f"- all_candidate_denominator: {report.all_candidate_denominator}",
        f"- best_by_brier: {report.best_by_brier.name}",
        f"- best_by_pnl: {report.best_by_pnl.name}",
        f"- promotion_safe: {report.promotion_safe}",
        f"- note: {report.note}",
        "",
        "| variant | brier | log_loss | pnl_cents | selected | coverage | avg_candidate_pnl | avg_selected_pnl | beats_brownian | beats_market | beats_current | ev_rank | top_ev_bucket_pnl |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---|---|---|---:|---:|",
    ]
    for row in report.rows:
        lines.append(
            "| {name} | {brier:.6f} | {log_loss:.6f} | {total_counterfactual_pnl_cents:.4f} | "
            "{selected_count} | {coverage_rate:.4f} | "
            "{avg_counterfactual_pnl_cents_per_candidate:.4f} | "
            "{avg_counterfactual_pnl_cents_per_selected:.4f} | "
            "{beats_brownian} | {beats_market} | {beats_current_calibrated} | "
            "{ev_rank_correlation_sign:.6f} | {top_ev_bucket_pnl_cents:.4f} |".format(
                **asdict(row)
            )
        )
    return "\n".join(lines) + "\n"


def _line_count(path: Path) -> int:
    with path.open("r", encoding="utf-8", errors="replace") as handle:
        return sum(1 for line in handle if line.strip())


def _clamp01(value: float) -> float:
    return max(0.0, min(1.0, float(value)))


if __name__ == "__main__":
    raise SystemExit(main())
