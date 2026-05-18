from __future__ import annotations

import argparse
import json
import math
from dataclasses import asdict, dataclass, replace
from datetime import datetime
from pathlib import Path
from typing import Sequence

from .replay_runner import (
    ReplayConfig,
    ReplayInput,
    evaluate_replay,
    load_replay_inputs_from_jsonl,
)
from .terminal_projection import brownian_terminal_probability


SECONDS_PER_YEAR = 365.0 * 24.0 * 60.0 * 60.0


@dataclass(frozen=True)
class DynamicParticleSpec:
    name: str
    lookback_seconds: float
    fallback_annualized_vol: float
    min_annualized_vol: float
    max_annualized_vol: float
    min_distinct_observations: int
    market_weight: float = 0.0


@dataclass(frozen=True)
class DynamicParticleRow:
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
    avg_annualized_vol: float
    min_annualized_vol: float
    max_annualized_vol: float


@dataclass(frozen=True)
class DynamicParticleReport:
    candidate_count: int
    source_candidate_count: int | None
    skipped_unlabeled_count: int
    denominator_scope: str
    all_candidate_denominator: bool
    rows: tuple[DynamicParticleRow, ...]
    best_by_brier: DynamicParticleRow
    best_by_pnl: DynamicParticleRow
    promotion_safe: bool
    note: str


class RollingVolEstimator:
    def __init__(self, spec: DynamicParticleSpec) -> None:
        self.spec = spec
        self._observations: list[tuple[datetime, float]] = []

    def observe_and_estimate(self, ts: datetime, spot: float) -> float:
        if spot <= 0.0:
            raise ValueError("spot must be positive")
        log_spot = math.log(spot)
        if not self._observations or self._observations[-1][1] != log_spot:
            self._observations.append((ts, log_spot))
        self._observations = [
            (obs_ts, obs_log_spot)
            for obs_ts, obs_log_spot in self._observations
            if (ts - obs_ts).total_seconds() <= self.spec.lookback_seconds
        ]
        return self._estimate()

    def _estimate(self) -> float:
        if len(self._observations) < self.spec.min_distinct_observations:
            return self.spec.fallback_annualized_vol
        realized_variance = 0.0
        elapsed = 0.0
        for (prev_ts, prev_log), (ts, log_spot) in zip(self._observations, self._observations[1:]):
            dt = (ts - prev_ts).total_seconds()
            if dt <= 0.0:
                continue
            realized_variance += (log_spot - prev_log) ** 2
            elapsed += dt
        if realized_variance <= 0.0 or elapsed <= 0.0:
            return self.spec.fallback_annualized_vol
        annualized = math.sqrt((realized_variance / elapsed) * SECONDS_PER_YEAR)
        return _clamp(
            annualized,
            self.spec.min_annualized_vol,
            self.spec.max_annualized_vol,
        )


def evaluate_dynamic_particle_variants(
    rows: Sequence[ReplayInput],
    config: ReplayConfig | None = None,
) -> DynamicParticleReport:
    if not rows:
        raise ValueError("at least one replay row is required")
    cfg = config or ReplayConfig()
    sorted_rows = sorted(rows, key=lambda row: (row.snapshot.decision_ts_utc, row.snapshot.market_ticker))
    summaries: list[DynamicParticleRow] = []
    for spec in _spec_registry():
        estimator = RollingVolEstimator(spec)
        variant_rows: list[ReplayInput] = []
        vols: list[float] = []
        for row in sorted_rows:
            vol = estimator.observe_and_estimate(row.snapshot.decision_ts_utc, row.snapshot.spot)
            seconds_to_close = max(
                0.0,
                (row.label.settlement_ts_utc - row.snapshot.decision_ts_utc).total_seconds(),
            )
            p_dynamic = brownian_terminal_probability(
                row.snapshot.spot,
                row.snapshot.strike,
                seconds_to_close,
                vol,
            )
            p_variant = (1.0 - spec.market_weight) * p_dynamic + spec.market_weight * row.market_p_yes
            variant_rows.append(replace(row, particle_p_yes=_clamp01(p_variant)))
            vols.append(vol)
        report = evaluate_replay(variant_rows, cfg)
        summaries.append(
            DynamicParticleRow(
                name=spec.name,
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
                avg_annualized_vol=sum(vols) / len(vols),
                min_annualized_vol=min(vols),
                max_annualized_vol=max(vols),
            )
        )
    best_by_brier = min(summaries, key=lambda row: (row.brier, row.log_loss))
    best_by_pnl = max(summaries, key=lambda row: row.total_counterfactual_pnl_cents)
    return DynamicParticleReport(
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
            "Dynamic-vol particles are same-sample diagnostics only. They use "
            "only chronological spot observations at or before each decision, "
            "but are not promotion-safe until predeclared on fresh locked OOS/shadow data."
        ),
    )


def write_dynamic_particle_report(
    report: DynamicParticleReport,
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
        description="Evaluate fixed rolling-vol next-second particle variants on a strict labeled denominator."
    )
    parser.add_argument("--candidates", required=True, type=Path)
    parser.add_argument("--labels", required=True, type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--stem", default="dynamic_particle_replay")
    parser.add_argument("--min-ev-cents", default=0.0, type=float)
    parser.add_argument("--min-fill-prob", default=0.0, type=float)
    parser.add_argument("--no-fill-penalty-cents", default=0.0, type=float)
    parser.add_argument(
        "--counterfactual-fill-policy",
        choices=["threshold", "always_fill", "never_fill"],
        default="threshold",
    )
    parser.add_argument("--counterfactual-fill-threshold", default=0.5, type=float)
    parser.add_argument(
        "--default-annualized-vol",
        default=None,
        type=float,
        help="used only when candidate rows omit brownian_p_yes",
    )
    parser.add_argument(
        "--allow-missing-labels",
        action="store_true",
        help="explicitly run on the resolved/labeled subset and report skipped unlabeled candidate rows",
    )
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
        evaluate_dynamic_particle_variants(
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
    json_path, md_path = write_dynamic_particle_report(report, args.output_dir, args.stem)
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


def _spec_registry() -> tuple[DynamicParticleSpec, ...]:
    return (
        DynamicParticleSpec(
            name="rolling_vol_120s",
            lookback_seconds=120.0,
            fallback_annualized_vol=0.65,
            min_annualized_vol=0.20,
            max_annualized_vol=2.50,
            min_distinct_observations=3,
        ),
        DynamicParticleSpec(
            name="rolling_vol_300s",
            lookback_seconds=300.0,
            fallback_annualized_vol=0.65,
            min_annualized_vol=0.20,
            max_annualized_vol=2.50,
            min_distinct_observations=3,
        ),
        DynamicParticleSpec(
            name="rolling_vol_600s",
            lookback_seconds=600.0,
            fallback_annualized_vol=0.65,
            min_annualized_vol=0.20,
            max_annualized_vol=2.50,
            min_distinct_observations=3,
        ),
        DynamicParticleSpec(
            name="rolling_vol_300s_market25",
            lookback_seconds=300.0,
            fallback_annualized_vol=0.65,
            min_annualized_vol=0.20,
            max_annualized_vol=2.50,
            min_distinct_observations=3,
            market_weight=0.25,
        ),
    )


def _markdown(report: DynamicParticleReport) -> str:
    lines = [
        "# Dynamic Particle Replay Report",
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
        "| variant | brier | log_loss | pnl_cents | selected | coverage | avg_candidate_pnl | avg_selected_pnl | beats_brownian | beats_market | beats_current | ev_rank | top_ev_bucket_pnl | avg_vol | min_vol | max_vol |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---|---|---|---:|---:|---:|---:|---:|",
    ]
    for row in report.rows:
        lines.append(
            "| {name} | {brier:.6f} | {log_loss:.6f} | {total_counterfactual_pnl_cents:.4f} | "
            "{selected_count} | {coverage_rate:.4f} | "
            "{avg_counterfactual_pnl_cents_per_candidate:.4f} | "
            "{avg_counterfactual_pnl_cents_per_selected:.4f} | "
            "{beats_brownian} | {beats_market} | {beats_current_calibrated} | "
            "{ev_rank_correlation_sign:.6f} | {top_ev_bucket_pnl_cents:.4f} | "
            "{avg_annualized_vol:.4f} | {min_annualized_vol:.4f} | {max_annualized_vol:.4f} |".format(
                **asdict(row)
            )
        )
    return "\n".join(lines) + "\n"


def _line_count(path: Path) -> int:
    with path.open("r", encoding="utf-8", errors="replace") as handle:
        return sum(1 for line in handle if line.strip())


def _clamp(value: float, lower: float, upper: float) -> float:
    return max(lower, min(upper, float(value)))


def _clamp01(value: float) -> float:
    return _clamp(value, 0.0, 1.0)


if __name__ == "__main__":
    raise SystemExit(main())
