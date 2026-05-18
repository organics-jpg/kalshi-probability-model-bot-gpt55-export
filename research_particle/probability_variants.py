from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass, replace
from pathlib import Path
from typing import Callable, Sequence

from .replay_runner import (
    ReplayConfig,
    ReplayInput,
    evaluate_replay,
    load_replay_inputs_from_jsonl,
)


VariantFn = Callable[[ReplayInput], float]


@dataclass(frozen=True)
class ProbabilityVariantRow:
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
class ProbabilityVariantReport:
    candidate_count: int
    source_candidate_count: int | None
    skipped_unlabeled_count: int
    denominator_scope: str
    all_candidate_denominator: bool
    rows: tuple[ProbabilityVariantRow, ...]
    best_by_brier: ProbabilityVariantRow
    best_by_pnl: ProbabilityVariantRow
    promotion_safe: bool
    note: str


def evaluate_probability_variants(
    rows: Sequence[ReplayInput],
    config: ReplayConfig | None = None,
) -> ProbabilityVariantReport:
    if not rows:
        raise ValueError("at least one replay row is required")
    cfg = config or ReplayConfig()
    variants = _variant_registry()
    summaries: list[ProbabilityVariantRow] = []
    for name, fn in variants:
        variant_rows = [
            replace(row, particle_p_yes=_clamp01(fn(row)))
            for row in rows
        ]
        report = evaluate_replay(variant_rows, cfg)
        summaries.append(
            ProbabilityVariantRow(
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
    return ProbabilityVariantReport(
        candidate_count=len(rows),
        source_candidate_count=None,
        skipped_unlabeled_count=0,
        denominator_scope="all_labeled_candidates",
        all_candidate_denominator=True,
        rows=tuple(summaries),
        best_by_brier=best_by_brier,
        best_by_pnl=best_by_pnl,
        promotion_safe=False,
        note=(
            "Fixed variants are same-sample diagnostics only. They are not "
            "promotion-safe until predeclared on a fresh locked OOS/shadow sample."
        ),
    )


def write_probability_variant_report(
    report: ProbabilityVariantReport,
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
        description="Evaluate fixed probability anchor variants on a strict labeled denominator."
    )
    parser.add_argument("--candidates", required=True, type=Path)
    parser.add_argument("--labels", required=True, type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--stem", default="probability_variants")
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
        evaluate_probability_variants(
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
    json_path, md_path = write_probability_variant_report(report, args.output_dir, args.stem)
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


def _variant_registry() -> tuple[tuple[str, VariantFn], ...]:
    return (
        ("particle", lambda row: row.particle_p_yes),
        ("brownian", lambda row: row.brownian_p_yes),
        ("market", lambda row: row.market_p_yes),
        ("current_calibrated", lambda row: row.current_calibrated_p_yes),
        ("market_current_50_50", lambda row: 0.5 * row.market_p_yes + 0.5 * row.current_calibrated_p_yes),
        ("market_particle_75_25", lambda row: 0.75 * row.market_p_yes + 0.25 * row.particle_p_yes),
        ("current_particle_75_25", lambda row: 0.75 * row.current_calibrated_p_yes + 0.25 * row.particle_p_yes),
        (
            "market_current_particle_40_40_20",
            lambda row: 0.4 * row.market_p_yes
            + 0.4 * row.current_calibrated_p_yes
            + 0.2 * row.particle_p_yes,
        ),
    )


def _clamp01(value: float) -> float:
    return max(0.0, min(1.0, float(value)))


def _markdown(report: ProbabilityVariantReport) -> str:
    lines = [
        "# Probability Variant Report",
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


if __name__ == "__main__":
    raise SystemExit(main())
