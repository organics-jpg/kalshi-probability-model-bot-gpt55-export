from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass, replace
from pathlib import Path
from typing import Literal, Sequence

from .fixed_terminal_oos import (
    EvaluationScope,
    FixedTerminalGateConfig,
    FixedTerminalGateResults,
    FixedTerminalVariantRow,
    _gate_results,
    _variant_by_name,
)
from .probability_variants import ProbabilityVariantRow, evaluate_probability_variants
from .replay_runner import ReplayConfig, ReplayInput, evaluate_replay, load_replay_inputs_from_jsonl
from .replay_runner import write_replay_report
from .spot_context_merge import SpotTickRow, load_spot_ticks
from .spot_realized_vol_terminal_diagnostic import (
    SpotRealizedVolSpec,
    realized_annualized_vol_at_decision,
)
from .terminal_projection import brownian_terminal_probability


HypothesisId = Literal["rv233_blend50_fixed65_terminal_v1"]

HYPOTHESIS_TO_SPEC: dict[HypothesisId, SpotRealizedVolSpec] = {
    "rv233_blend50_fixed65_terminal_v1": SpotRealizedVolSpec(
        name="rv233_blend50_fixed65",
        window_seconds=233,
        floor_annualized_vol=0.20,
        cap_annualized_vol=1.50,
        fallback_annualized_vol=0.65,
        fixed_blend_weight=0.50,
    ),
}


@dataclass(frozen=True)
class SpotRealizedVolTerminalOOSReport:
    hypothesis_id: HypothesisId
    variant_name: str
    evaluation_scope: EvaluationScope
    candidate_count: int
    source_candidate_count: int | None
    skipped_unlabeled_count: int
    denominator_scope: str
    market_count: int
    spot_tick_count: int
    fallback_row_count: int
    mean_annualized_vol: float
    selected_variant: FixedTerminalVariantRow
    static_particle_baseline: ProbabilityVariantRow
    current_calibrated_baseline: ProbabilityVariantRow
    gate_config: FixedTerminalGateConfig
    gate_results: FixedTerminalGateResults
    promotion_safe: bool
    note: str


def evaluate_spot_realized_vol_terminal_oos(
    rows: Sequence[ReplayInput],
    ticks: Sequence[SpotTickRow],
    config: ReplayConfig | None = None,
    *,
    hypothesis_id: HypothesisId = "rv233_blend50_fixed65_terminal_v1",
    evaluation_scope: EvaluationScope = "same_sample_diagnostic",
    denominator_scope: str = "all_labeled_candidates",
    gate_config: FixedTerminalGateConfig | None = None,
) -> SpotRealizedVolTerminalOOSReport:
    if not rows:
        raise ValueError("at least one replay row is required")
    cfg = config or ReplayConfig()
    gates = gate_config or FixedTerminalGateConfig()
    spec = HYPOTHESIS_TO_SPEC[hypothesis_id]
    variant_rows, vols, fallback_count = materialize_spot_realized_vol_terminal_rows(
        rows,
        ticks,
        hypothesis_id=hypothesis_id,
    )
    replay = evaluate_replay(variant_rows, cfg)
    probability_report = evaluate_probability_variants(rows, cfg)
    selected = FixedTerminalVariantRow(
        name=spec.name,
        candidate_count=replay.candidate_count,
        selected_count=replay.selected_count,
        total_counterfactual_pnl_cents=replay.total_counterfactual_pnl_cents,
        avg_counterfactual_pnl_cents_per_selected=replay.avg_counterfactual_pnl_cents_per_selected,
        brier=replay.particle.brier,
        log_loss=replay.particle.log_loss,
        beats_brownian=replay.particle_beats_brownian,
        beats_market=replay.particle_beats_market,
        beats_current_calibrated=replay.particle_beats_current_calibrated,
        ev_rank_correlation_sign=replay.ev_rank_correlation_sign,
        top_ev_bucket_pnl_cents=replay.top_ev_bucket_pnl_cents,
    )
    static_particle = _variant_by_name(probability_report.rows, "particle")
    current_calibrated = _variant_by_name(probability_report.rows, "current_calibrated")
    market_count = len({row.snapshot.market_ticker for row in rows})
    gate_results = _gate_results(
        selected=selected,
        static_particle=static_particle,
        current_calibrated=current_calibrated,
        market_count=market_count,
        evaluation_scope=evaluation_scope,
        denominator_scope=denominator_scope,
        gates=gates,
    )
    return SpotRealizedVolTerminalOOSReport(
        hypothesis_id=hypothesis_id,
        variant_name=spec.name,
        evaluation_scope=evaluation_scope,
        candidate_count=len(rows),
        source_candidate_count=None,
        skipped_unlabeled_count=0,
        denominator_scope=denominator_scope,
        market_count=market_count,
        spot_tick_count=len(ticks),
        fallback_row_count=fallback_count,
        mean_annualized_vol=_mean(vols),
        selected_variant=selected,
        static_particle_baseline=static_particle,
        current_calibrated_baseline=current_calibrated,
        gate_config=gates,
        gate_results=gate_results,
        promotion_safe=bool(gate_results.all_passed),
        note=(
            "Spot realized-vol terminal OOS reports are promotion-safe only when "
            "the hypothesis and gates were locked before capture, the spot ticks "
            "are timestamp-available at decision time, the evaluation scope is "
            "locked_oos_shadow, and every gate passes. This is research-only and "
            "must not touch live trading."
        ),
    )


def materialize_spot_realized_vol_terminal_rows(
    rows: Sequence[ReplayInput],
    ticks: Sequence[SpotTickRow],
    *,
    hypothesis_id: HypothesisId = "rv233_blend50_fixed65_terminal_v1",
) -> tuple[list[ReplayInput], list[float], int]:
    if not rows:
        raise ValueError("at least one replay row is required")
    spec = HYPOTHESIS_TO_SPEC[hypothesis_id]
    times = [tick.available_ts_utc for tick in ticks]
    prices = [float(tick.price) for tick in ticks]
    variant_rows: list[ReplayInput] = []
    vols: list[float] = []
    fallback_count = 0
    for row in sorted(rows, key=lambda item: (item.snapshot.decision_ts_utc, item.snapshot.market_ticker)):
        ann_vol, used_fallback = realized_annualized_vol_at_decision(
            row.snapshot.decision_ts_utc,
            times,
            prices,
            spec.window_seconds,
            fallback_annualized_vol=spec.fallback_annualized_vol,
            floor_annualized_vol=spec.floor_annualized_vol,
            cap_annualized_vol=spec.cap_annualized_vol,
        )
        vols.append(ann_vol)
        fallback_count += int(used_fallback)
        rv_prob = brownian_terminal_probability(
            row.snapshot.spot,
            row.snapshot.strike,
            max(0.0, (row.label.settlement_ts_utc - row.snapshot.decision_ts_utc).total_seconds()),
            ann_vol,
        )
        p_yes = spec.fixed_blend_weight * row.brownian_p_yes + (1.0 - spec.fixed_blend_weight) * rv_prob
        variant_rows.append(replace(row, particle_p_yes=_clamp01(p_yes)))
    return variant_rows, vols, fallback_count


def write_spot_realized_vol_terminal_oos_report(
    report: SpotRealizedVolTerminalOOSReport,
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
        description="Evaluate a predeclared independent-spot realized-vol terminal OOS shadow hypothesis."
    )
    parser.add_argument("--candidates", required=True, type=Path)
    parser.add_argument("--labels", required=True, type=Path)
    parser.add_argument("--spot-ticks", required=True, type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--stem", default="spot_realized_vol_terminal_oos")
    parser.add_argument(
        "--hypothesis-id",
        choices=tuple(HYPOTHESIS_TO_SPEC),
        default="rv233_blend50_fixed65_terminal_v1",
    )
    parser.add_argument(
        "--evaluation-scope",
        choices=["same_sample_diagnostic", "locked_oos_shadow"],
        default="same_sample_diagnostic",
    )
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
    parser.add_argument("--gate-min-candidates", default=1000, type=int)
    parser.add_argument("--gate-min-markets", default=5, type=int)
    parser.add_argument("--gate-min-selected", default=250, type=int)
    parser.add_argument(
        "--materialized-stem",
        default="",
        help="optional stem for a full replay decision report using the realized-vol probability",
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
    ticks = load_spot_ticks(args.spot_ticks)
    replay_config = ReplayConfig(
        min_ev_cents=args.min_ev_cents,
        min_fill_prob=args.min_fill_prob,
        no_fill_penalty_cents=args.no_fill_penalty_cents,
        counterfactual_fill_policy=args.counterfactual_fill_policy,
        counterfactual_fill_threshold=args.counterfactual_fill_threshold,
    )
    report = replace(
        evaluate_spot_realized_vol_terminal_oos(
            rows,
            ticks,
            replay_config,
            hypothesis_id=args.hypothesis_id,
            evaluation_scope=args.evaluation_scope,
            denominator_scope=denominator_scope,
            gate_config=FixedTerminalGateConfig(
                min_candidate_count=args.gate_min_candidates,
                min_market_count=args.gate_min_markets,
                min_selected_count=args.gate_min_selected,
            ),
        ),
        source_candidate_count=source_candidate_count,
        skipped_unlabeled_count=skipped_unlabeled_count,
        denominator_scope=denominator_scope,
    )
    json_path, md_path = write_spot_realized_vol_terminal_oos_report(
        report,
        args.output_dir,
        args.stem,
    )
    print(f"hypothesis_id={report.hypothesis_id}")
    print(f"variant_name={report.variant_name}")
    print(f"evaluation_scope={report.evaluation_scope}")
    print(f"candidate_count={report.candidate_count}")
    print(f"source_candidate_count={report.source_candidate_count}")
    print(f"skipped_unlabeled_count={report.skipped_unlabeled_count}")
    print(f"denominator_scope={report.denominator_scope}")
    print(f"market_count={report.market_count}")
    print(f"spot_tick_count={report.spot_tick_count}")
    print(f"fallback_row_count={report.fallback_row_count}")
    print(f"mean_annualized_vol={report.mean_annualized_vol:.6f}")
    print(f"selected_count={report.selected_variant.selected_count}")
    print(f"total_counterfactual_pnl_cents={report.selected_variant.total_counterfactual_pnl_cents:.4f}")
    print(f"brier={report.selected_variant.brier:.6f}")
    print(f"log_loss={report.selected_variant.log_loss:.6f}")
    print(f"promotion_safe={report.promotion_safe}")
    print(f"json_report={json_path}")
    print(f"md_report={md_path}")
    if args.materialized_stem:
        materialized_rows, _, _ = materialize_spot_realized_vol_terminal_rows(
            rows,
            ticks,
            hypothesis_id=args.hypothesis_id,
        )
        materialized_report = replace(
            evaluate_replay(materialized_rows, replay_config),
            source_candidate_count=source_candidate_count,
            skipped_unlabeled_count=skipped_unlabeled_count,
            denominator_scope=denominator_scope,
        )
        materialized_json, materialized_md = write_replay_report(
            materialized_report,
            args.output_dir,
            args.materialized_stem,
        )
        print(f"materialized_json_report={materialized_json}")
        print(f"materialized_md_report={materialized_md}")
    return 0


def _line_count(path: Path) -> int:
    with path.open("r", encoding="utf-8", errors="replace") as handle:
        return sum(1 for line in handle if line.strip())


def _mean(values) -> float:
    seq = [float(value) for value in values]
    if not seq:
        return 0.0
    return sum(seq) / len(seq)


def _clamp01(value: float) -> float:
    return min(1.0, max(0.0, float(value)))


def _markdown(report: SpotRealizedVolTerminalOOSReport) -> str:
    gate_rows = "\n".join(
        f"- {name}: {value}"
        for name, value in asdict(report.gate_results).items()
    )
    return (
        "# Spot Realized-Vol Terminal OOS Report\n\n"
        f"- hypothesis_id: {report.hypothesis_id}\n"
        f"- variant_name: {report.variant_name}\n"
        f"- evaluation_scope: {report.evaluation_scope}\n"
        f"- candidate_count: {report.candidate_count}\n"
        f"- source_candidate_count: {report.source_candidate_count}\n"
        f"- skipped_unlabeled_count: {report.skipped_unlabeled_count}\n"
        f"- denominator_scope: {report.denominator_scope}\n"
        f"- market_count: {report.market_count}\n"
        f"- spot_tick_count: {report.spot_tick_count}\n"
        f"- fallback_row_count: {report.fallback_row_count}\n"
        f"- mean_annualized_vol: {report.mean_annualized_vol:.6f}\n"
        f"- selected_count: {report.selected_variant.selected_count}\n"
        f"- total_counterfactual_pnl_cents: {report.selected_variant.total_counterfactual_pnl_cents:.4f}\n"
        f"- avg_counterfactual_pnl_cents_per_selected: {report.selected_variant.avg_counterfactual_pnl_cents_per_selected:.6f}\n"
        f"- brier: {report.selected_variant.brier:.6f}\n"
        f"- log_loss: {report.selected_variant.log_loss:.6f}\n"
        f"- ev_rank_correlation_sign: {report.selected_variant.ev_rank_correlation_sign:.6f}\n"
        f"- top_ev_bucket_pnl_cents: {report.selected_variant.top_ev_bucket_pnl_cents:.4f}\n"
        f"- beats_brownian: {report.selected_variant.beats_brownian}\n"
        f"- beats_market: {report.selected_variant.beats_market}\n"
        f"- beats_current_calibrated: {report.selected_variant.beats_current_calibrated}\n"
        f"- static_particle_pnl_cents: {report.static_particle_baseline.total_counterfactual_pnl_cents:.4f}\n"
        f"- current_calibrated_pnl_cents: {report.current_calibrated_baseline.total_counterfactual_pnl_cents:.4f}\n"
        f"- promotion_safe: {report.promotion_safe}\n"
        f"- note: {report.note}\n\n"
        "## Gate Results\n\n"
        f"{gate_rows}\n"
    )


if __name__ == "__main__":
    raise SystemExit(main())
