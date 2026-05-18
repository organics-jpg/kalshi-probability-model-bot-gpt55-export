from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass, replace
from pathlib import Path
from typing import Literal, Sequence

from .dynamic_particle_replay import DynamicParticleRow, evaluate_dynamic_particle_variants
from .probability_variants import ProbabilityVariantRow, evaluate_probability_variants
from .replay_runner import ReplayConfig, ReplayInput, load_replay_inputs_from_jsonl


EvaluationScope = Literal["same_sample_diagnostic", "locked_oos_shadow"]
HypothesisId = Literal["rolling_vol_300s_v1", "rolling_vol_600s_v1"]

HYPOTHESIS_TO_VARIANT: dict[HypothesisId, str] = {
    "rolling_vol_300s_v1": "rolling_vol_300s",
    "rolling_vol_600s_v1": "rolling_vol_600s",
}


@dataclass(frozen=True)
class DynamicParticleGateConfig:
    min_candidate_count: int = 1000
    min_market_count: int = 5
    min_selected_count: int = 250
    min_total_pnl_cents: float = 1.0
    min_avg_pnl_per_selected_cents: float = 0.01
    require_positive_ev_rank: bool = True
    require_positive_top_ev_bucket: bool = True
    require_beats_brownian_probability: bool = True
    require_beats_market_probability: bool = True
    require_beats_current_probability: bool = True
    require_beats_static_particle_pnl: bool = True
    require_beats_current_calibrated_pnl: bool = True


@dataclass(frozen=True)
class DynamicParticleGateResults:
    enough_candidates: bool
    enough_markets: bool
    enough_selected: bool
    positive_total_pnl: bool
    positive_avg_pnl: bool
    positive_ev_rank: bool
    positive_top_ev_bucket: bool
    beats_brownian_probability: bool
    beats_market_probability: bool
    beats_current_probability: bool
    beats_static_particle_pnl: bool
    beats_current_calibrated_pnl: bool
    locked_oos_scope: bool
    all_passed: bool


@dataclass(frozen=True)
class DynamicParticleOOSReport:
    hypothesis_id: HypothesisId
    variant_name: str
    evaluation_scope: EvaluationScope
    candidate_count: int
    source_candidate_count: int | None
    skipped_unlabeled_count: int
    denominator_scope: str
    market_count: int
    selected_variant: DynamicParticleRow
    static_particle_baseline: ProbabilityVariantRow
    current_calibrated_baseline: ProbabilityVariantRow
    gate_config: DynamicParticleGateConfig
    gate_results: DynamicParticleGateResults
    promotion_safe: bool
    note: str


def evaluate_dynamic_particle_oos(
    rows: Sequence[ReplayInput],
    config: ReplayConfig | None = None,
    *,
    hypothesis_id: HypothesisId = "rolling_vol_300s_v1",
    evaluation_scope: EvaluationScope = "same_sample_diagnostic",
    gate_config: DynamicParticleGateConfig | None = None,
) -> DynamicParticleOOSReport:
    if not rows:
        raise ValueError("at least one replay row is required")
    cfg = config or ReplayConfig()
    gates = gate_config or DynamicParticleGateConfig()
    variant_name = HYPOTHESIS_TO_VARIANT[hypothesis_id]
    dynamic_report = evaluate_dynamic_particle_variants(rows, cfg)
    probability_report = evaluate_probability_variants(rows, cfg)
    selected_variant = _row_by_name(dynamic_report.rows, variant_name)
    static_particle = _variant_by_name(probability_report.rows, "particle")
    current_calibrated = _variant_by_name(probability_report.rows, "current_calibrated")
    market_count = len({row.snapshot.market_ticker for row in rows})
    gate_results = _gate_results(
        selected=selected_variant,
        static_particle=static_particle,
        current_calibrated=current_calibrated,
        market_count=market_count,
        evaluation_scope=evaluation_scope,
        gates=gates,
    )
    return DynamicParticleOOSReport(
        hypothesis_id=hypothesis_id,
        variant_name=variant_name,
        evaluation_scope=evaluation_scope,
        candidate_count=len(rows),
        source_candidate_count=None,
        skipped_unlabeled_count=0,
        denominator_scope="all_labeled_candidates",
        market_count=market_count,
        selected_variant=selected_variant,
        static_particle_baseline=static_particle,
        current_calibrated_baseline=current_calibrated,
        gate_config=gates,
        gate_results=gate_results,
        promotion_safe=bool(gate_results.all_passed),
        note=(
            "Dynamic rolling-vol particle OOS reports are promotion-safe only "
            "when the hypothesis and gates were locked before capture, the "
            "evaluation scope is locked_oos_shadow, and every gate passes. "
            "Same-sample diagnostics are useful for research direction only."
        ),
    )


def write_dynamic_particle_oos_report(
    report: DynamicParticleOOSReport,
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
        description="Evaluate a predeclared rolling-vol dynamic particle OOS hypothesis."
    )
    parser.add_argument("--candidates", required=True, type=Path)
    parser.add_argument("--labels", required=True, type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--stem", default="dynamic_particle_oos")
    parser.add_argument(
        "--hypothesis-id",
        choices=tuple(HYPOTHESIS_TO_VARIANT),
        default="rolling_vol_300s_v1",
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
        evaluate_dynamic_particle_oos(
            rows,
            ReplayConfig(
                min_ev_cents=args.min_ev_cents,
                min_fill_prob=args.min_fill_prob,
                no_fill_penalty_cents=args.no_fill_penalty_cents,
                counterfactual_fill_policy=args.counterfactual_fill_policy,
                counterfactual_fill_threshold=args.counterfactual_fill_threshold,
            ),
            hypothesis_id=args.hypothesis_id,
            evaluation_scope=args.evaluation_scope,
            gate_config=DynamicParticleGateConfig(
                min_candidate_count=args.gate_min_candidates,
                min_market_count=args.gate_min_markets,
                min_selected_count=args.gate_min_selected,
            ),
        ),
        source_candidate_count=source_candidate_count,
        skipped_unlabeled_count=skipped_unlabeled_count,
        denominator_scope=denominator_scope,
    )
    json_path, md_path = write_dynamic_particle_oos_report(report, args.output_dir, args.stem)
    print(f"hypothesis_id={report.hypothesis_id}")
    print(f"variant_name={report.variant_name}")
    print(f"evaluation_scope={report.evaluation_scope}")
    print(f"candidate_count={report.candidate_count}")
    print(f"source_candidate_count={report.source_candidate_count}")
    print(f"skipped_unlabeled_count={report.skipped_unlabeled_count}")
    print(f"denominator_scope={report.denominator_scope}")
    print(f"market_count={report.market_count}")
    print(f"selected_count={report.selected_variant.selected_count}")
    print(f"total_counterfactual_pnl_cents={report.selected_variant.total_counterfactual_pnl_cents:.4f}")
    print(f"brier={report.selected_variant.brier:.6f}")
    print(f"log_loss={report.selected_variant.log_loss:.6f}")
    print(f"promotion_safe={report.promotion_safe}")
    print(f"json_report={json_path}")
    print(f"md_report={md_path}")
    return 0


def _gate_results(
    *,
    selected: DynamicParticleRow,
    static_particle: ProbabilityVariantRow,
    current_calibrated: ProbabilityVariantRow,
    market_count: int,
    evaluation_scope: EvaluationScope,
    gates: DynamicParticleGateConfig,
) -> DynamicParticleGateResults:
    enough_candidates = selected.candidate_count >= gates.min_candidate_count
    enough_markets = market_count >= gates.min_market_count
    enough_selected = selected.selected_count >= gates.min_selected_count
    positive_total_pnl = selected.total_counterfactual_pnl_cents >= gates.min_total_pnl_cents
    positive_avg_pnl = (
        selected.avg_counterfactual_pnl_cents_per_selected >= gates.min_avg_pnl_per_selected_cents
    )
    positive_ev_rank = (
        selected.ev_rank_correlation_sign > 0.0 if gates.require_positive_ev_rank else True
    )
    positive_top_ev_bucket = (
        selected.top_ev_bucket_pnl_cents > 0.0 if gates.require_positive_top_ev_bucket else True
    )
    beats_brownian_probability = (
        selected.beats_brownian if gates.require_beats_brownian_probability else True
    )
    beats_market_probability = selected.beats_market if gates.require_beats_market_probability else True
    beats_current_probability = (
        selected.beats_current_calibrated if gates.require_beats_current_probability else True
    )
    beats_static_particle_pnl = (
        selected.total_counterfactual_pnl_cents > static_particle.total_counterfactual_pnl_cents
        if gates.require_beats_static_particle_pnl
        else True
    )
    beats_current_calibrated_pnl = (
        selected.total_counterfactual_pnl_cents
        > current_calibrated.total_counterfactual_pnl_cents
        if gates.require_beats_current_calibrated_pnl
        else True
    )
    locked_oos_scope = evaluation_scope == "locked_oos_shadow"
    all_passed = all(
        (
            enough_candidates,
            enough_markets,
            enough_selected,
            positive_total_pnl,
            positive_avg_pnl,
            positive_ev_rank,
            positive_top_ev_bucket,
            beats_brownian_probability,
            beats_market_probability,
            beats_current_probability,
            beats_static_particle_pnl,
            beats_current_calibrated_pnl,
            locked_oos_scope,
        )
    )
    return DynamicParticleGateResults(
        enough_candidates=enough_candidates,
        enough_markets=enough_markets,
        enough_selected=enough_selected,
        positive_total_pnl=positive_total_pnl,
        positive_avg_pnl=positive_avg_pnl,
        positive_ev_rank=positive_ev_rank,
        positive_top_ev_bucket=positive_top_ev_bucket,
        beats_brownian_probability=beats_brownian_probability,
        beats_market_probability=beats_market_probability,
        beats_current_probability=beats_current_probability,
        beats_static_particle_pnl=beats_static_particle_pnl,
        beats_current_calibrated_pnl=beats_current_calibrated_pnl,
        locked_oos_scope=locked_oos_scope,
        all_passed=all_passed,
    )


def _row_by_name(rows: Sequence[DynamicParticleRow], name: str) -> DynamicParticleRow:
    for row in rows:
        if row.name == name:
            return row
    raise ValueError(f"dynamic variant not found: {name}")


def _variant_by_name(rows: Sequence[ProbabilityVariantRow], name: str) -> ProbabilityVariantRow:
    for row in rows:
        if row.name == name:
            return row
    raise ValueError(f"probability variant not found: {name}")


def _markdown(report: DynamicParticleOOSReport) -> str:
    selected = report.selected_variant
    lines = [
        "# Dynamic Particle OOS Report",
        "",
        f"- hypothesis_id: {report.hypothesis_id}",
        f"- variant_name: {report.variant_name}",
        f"- evaluation_scope: {report.evaluation_scope}",
        f"- candidate_count: {report.candidate_count}",
        f"- source_candidate_count: {report.source_candidate_count}",
        f"- skipped_unlabeled_count: {report.skipped_unlabeled_count}",
        f"- denominator_scope: {report.denominator_scope}",
        f"- market_count: {report.market_count}",
        f"- selected_count: {selected.selected_count}",
        f"- total_counterfactual_pnl_cents: {selected.total_counterfactual_pnl_cents:.4f}",
        f"- avg_counterfactual_pnl_cents_per_selected: {selected.avg_counterfactual_pnl_cents_per_selected:.4f}",
        f"- brier: {selected.brier:.6f}",
        f"- log_loss: {selected.log_loss:.6f}",
        f"- ev_rank_correlation_sign: {selected.ev_rank_correlation_sign:.6f}",
        f"- top_ev_bucket_pnl_cents: {selected.top_ev_bucket_pnl_cents:.4f}",
        f"- static_particle_pnl_cents: {report.static_particle_baseline.total_counterfactual_pnl_cents:.4f}",
        f"- current_calibrated_pnl_cents: {report.current_calibrated_baseline.total_counterfactual_pnl_cents:.4f}",
        f"- promotion_safe: {report.promotion_safe}",
        f"- note: {report.note}",
        "",
        "## Gate Results",
        "",
    ]
    for name, value in asdict(report.gate_results).items():
        lines.append(f"- {name}: {value}")
    lines.extend(["", "## Gate Config", ""])
    for name, value in asdict(report.gate_config).items():
        lines.append(f"- {name}: {value}")
    return "\n".join(lines) + "\n"


def _line_count(path: Path) -> int:
    with path.open("r", encoding="utf-8", errors="replace") as handle:
        return sum(1 for line in handle if line.strip())


if __name__ == "__main__":
    raise SystemExit(main())
