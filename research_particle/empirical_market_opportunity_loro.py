from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Sequence

from .validation import brier_score, log_loss, pairwise_rank_correlation_sign, top_bucket_mean_pnl


@dataclass(frozen=True)
class OpportunityScoreTransform:
    name: str
    current_gap_penalty_cents: float
    market_gap_penalty_cents: float


@dataclass(frozen=True)
class MarketOpportunityLOROChoice:
    selector: str
    family: str
    spec: str
    transform: str
    train_run_count: int
    train_market_count: int
    train_total_pnl_cents: float
    train_positive_pnl_run_count: int
    train_positive_ev_rank_run_count: int
    train_positive_top_bucket_run_count: int
    train_beats_current_run_count: int
    train_mean_brier: float
    train_mean_log_loss: float


@dataclass(frozen=True)
class MarketOpportunityLOROHoldoutRow:
    selector: str
    holdout_run: str
    family: str
    spec: str
    transform: str
    train_run_count: int
    train_market_count: int
    train_total_pnl_cents: float
    train_positive_pnl_run_count: int
    train_positive_ev_rank_run_count: int
    train_positive_top_bucket_run_count: int
    train_beats_current_run_count: int
    holdout_market_count: int
    holdout_selected_market_count: int
    holdout_total_pnl_cents: float
    holdout_avg_pnl_cents_per_market: float
    holdout_brier: float
    holdout_log_loss: float
    holdout_beats_brownian: bool
    holdout_beats_market: bool
    holdout_beats_current: bool
    holdout_ev_rank_correlation_sign: float
    holdout_top_bucket_pnl_cents: float
    holdout_strict_gate_pass: bool


@dataclass(frozen=True)
class MarketOpportunityLOROSummaryRow:
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
class MarketOpportunityLOROReport:
    source_report: str
    source_run_count: int
    source_opportunity_row_count: int
    transforms: tuple[str, ...]
    selector: str
    choices: tuple[MarketOpportunityLOROChoice, ...]
    holdout_rows: tuple[MarketOpportunityLOROHoldoutRow, ...]
    summary_rows: tuple[MarketOpportunityLOROSummaryRow, ...]
    candidate_ready_for_predeclared_shadow: bool
    promotion_safe: bool
    conclusion: str


def build_market_opportunity_loro_report(
    source_report: Path,
    *,
    transforms: Sequence[OpportunityScoreTransform] | None = None,
) -> MarketOpportunityLOROReport:
    payload = _load_source_report(source_report)
    rows = tuple(_OpportunityRow(row) for row in payload.get("opportunity_rows") or ())
    if not rows:
        raise ValueError("source report has no opportunity_rows; rerun empirical_market_opportunity_diagnostic first")
    transform_specs = tuple(transforms or _default_transforms())
    run_names = tuple(sorted({row.run for row in rows}))
    if len(run_names) < 2:
        raise ValueError("at least two runs are required for leave-one-run-out validation")
    selector = "train_strict_ev_bucket_score"
    choices: list[MarketOpportunityLOROChoice] = []
    holdouts: list[MarketOpportunityLOROHoldoutRow] = []
    for holdout_run in run_names:
        train_rows = [row for row in rows if row.run != holdout_run]
        train_choices = _build_choices(train_rows, transform_specs, selector=selector)
        choice = _select_choice(train_choices)
        choices.append(choice)
        holdout_rows = [
            row
            for row in rows
            if row.run == holdout_run and row.family == choice.family and row.spec == choice.spec
        ]
        transform = _transform_by_name(transform_specs, choice.transform)
        metrics = _evaluate_rows(holdout_rows, transform)
        holdouts.append(
            MarketOpportunityLOROHoldoutRow(
                selector=selector,
                holdout_run=holdout_run,
                family=choice.family,
                spec=choice.spec,
                transform=choice.transform,
                train_run_count=choice.train_run_count,
                train_market_count=choice.train_market_count,
                train_total_pnl_cents=choice.train_total_pnl_cents,
                train_positive_pnl_run_count=choice.train_positive_pnl_run_count,
                train_positive_ev_rank_run_count=choice.train_positive_ev_rank_run_count,
                train_positive_top_bucket_run_count=choice.train_positive_top_bucket_run_count,
                train_beats_current_run_count=choice.train_beats_current_run_count,
                holdout_market_count=metrics.market_count,
                holdout_selected_market_count=metrics.selected_market_count,
                holdout_total_pnl_cents=metrics.total_pnl_cents,
                holdout_avg_pnl_cents_per_market=metrics.avg_pnl_cents_per_market,
                holdout_brier=metrics.brier,
                holdout_log_loss=metrics.log_loss,
                holdout_beats_brownian=metrics.beats_brownian,
                holdout_beats_market=metrics.beats_market,
                holdout_beats_current=metrics.beats_current,
                holdout_ev_rank_correlation_sign=metrics.ev_rank_correlation_sign,
                holdout_top_bucket_pnl_cents=metrics.top_bucket_pnl_cents,
                holdout_strict_gate_pass=_strict(metrics),
            )
        )
    summaries = tuple(_summarize_holdouts(holdouts))
    candidate_ready = any(summary.strict_all_holdouts for summary in summaries)
    conclusion = (
        "A leave-one-run-out market-opportunity transform cleared every strict holdout; "
        "this only nominates a fresh predeclared shadow packet, not live promotion."
        if candidate_ready
        else "No leave-one-run-out market-opportunity transform cleared strict holdout gates."
    )
    return MarketOpportunityLOROReport(
        source_report=str(source_report),
        source_run_count=len(run_names),
        source_opportunity_row_count=len(rows),
        transforms=tuple(transform.name for transform in transform_specs),
        selector=selector,
        choices=tuple(choices),
        holdout_rows=tuple(holdouts),
        summary_rows=summaries,
        candidate_ready_for_predeclared_shadow=candidate_ready,
        promotion_safe=False,
        conclusion=conclusion,
    )


def write_market_opportunity_loro_report(
    report: MarketOpportunityLOROReport,
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
            "Leave-one-run-out score-correction diagnostic for empirical market opportunities. "
            "Requires an empirical_market_opportunity_diagnostic JSON with opportunity_rows."
        )
    )
    parser.add_argument("--source-report", required=True, type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--stem", default="empirical_market_opportunity_loro")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    report = build_market_opportunity_loro_report(args.source_report)
    json_path, md_path = write_market_opportunity_loro_report(report, args.output_dir, args.stem)
    print(f"source_run_count={report.source_run_count}")
    print(f"source_opportunity_row_count={report.source_opportunity_row_count}")
    print(f"transform_count={len(report.transforms)}")
    print(f"holdout_row_count={len(report.holdout_rows)}")
    print(f"candidate_ready_for_predeclared_shadow={report.candidate_ready_for_predeclared_shadow}")
    print(f"promotion_safe={report.promotion_safe}")
    print(f"json_report={json_path}")
    print(f"md_report={md_path}")
    return 0


@dataclass(frozen=True)
class _OpportunityMetrics:
    market_count: int
    selected_market_count: int
    total_pnl_cents: float
    avg_pnl_cents_per_market: float
    brier: float
    log_loss: float
    beats_brownian: bool
    beats_market: bool
    beats_current: bool
    ev_rank_correlation_sign: float
    top_bucket_pnl_cents: float


class _OpportunityRow:
    def __init__(self, raw: dict[str, Any]) -> None:
        self.raw = raw
        self.run = str(raw.get("run", ""))
        self.family = str(raw.get("family", ""))
        self.spec = str(raw.get("spec", ""))
        self.market_ticker = str(raw.get("market_ticker", ""))
        self.selected = bool(raw.get("selected"))
        self.settlement_result_yes = bool(raw.get("settlement_result_yes"))
        self.predicted_ev_cents = float(raw.get("predicted_ev_cents", 0.0) or 0.0)
        self.pnl_cents = float(raw.get("pnl_cents", 0.0) or 0.0)
        self.particle_p_yes = _clamp01(float(raw.get("particle_p_yes", 0.5) or 0.5))
        self.brownian_p_yes = _clamp01(float(raw.get("brownian_p_yes", 0.5) or 0.5))
        self.market_p_yes = _clamp01(float(raw.get("market_p_yes", 0.5) or 0.5))
        self.current_calibrated_p_yes = _clamp01(float(raw.get("current_calibrated_p_yes", 0.5) or 0.5))
        self.abs_particle_current_gap = abs(self.particle_p_yes - self.current_calibrated_p_yes)
        self.abs_particle_market_gap = abs(self.particle_p_yes - self.market_p_yes)


def _load_source_report(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("source report must be a JSON object")
    return payload


def _default_transforms() -> tuple[OpportunityScoreTransform, ...]:
    return (
        OpportunityScoreTransform("raw_ev", 0.0, 0.0),
        OpportunityScoreTransform("current_gap_penalty_10", 10.0, 0.0),
        OpportunityScoreTransform("current_gap_penalty_25", 25.0, 0.0),
        OpportunityScoreTransform("market_gap_penalty_10", 0.0, 10.0),
        OpportunityScoreTransform("market_gap_penalty_25", 0.0, 25.0),
        OpportunityScoreTransform("dual_gap_penalty_10", 10.0, 10.0),
        OpportunityScoreTransform("dual_gap_penalty_25", 25.0, 25.0),
    )


def _build_choices(
    rows: Sequence[_OpportunityRow],
    transforms: Sequence[OpportunityScoreTransform],
    *,
    selector: str,
) -> list[MarketOpportunityLOROChoice]:
    choices: list[MarketOpportunityLOROChoice] = []
    for family, spec in sorted({(row.family, row.spec) for row in rows}):
        family_spec_rows = [row for row in rows if row.family == family and row.spec == spec]
        for transform in transforms:
            by_run = _metrics_by_run(family_spec_rows, transform)
            run_metrics = list(by_run.values())
            choices.append(
                MarketOpportunityLOROChoice(
                    selector=selector,
                    family=family,
                    spec=spec,
                    transform=transform.name,
                    train_run_count=len(run_metrics),
                    train_market_count=sum(metric.market_count for metric in run_metrics),
                    train_total_pnl_cents=sum(metric.total_pnl_cents for metric in run_metrics),
                    train_positive_pnl_run_count=sum(1 for metric in run_metrics if metric.total_pnl_cents > 0.0),
                    train_positive_ev_rank_run_count=sum(
                        1 for metric in run_metrics if metric.ev_rank_correlation_sign > 0.0
                    ),
                    train_positive_top_bucket_run_count=sum(
                        1 for metric in run_metrics if metric.top_bucket_pnl_cents > 0.0
                    ),
                    train_beats_current_run_count=sum(1 for metric in run_metrics if metric.beats_current),
                    train_mean_brier=_mean(metric.brier for metric in run_metrics),
                    train_mean_log_loss=_mean(metric.log_loss for metric in run_metrics),
                )
            )
    return choices


def _select_choice(choices: Sequence[MarketOpportunityLOROChoice]) -> MarketOpportunityLOROChoice:
    if not choices:
        raise ValueError("no train choices")
    return max(
        choices,
        key=lambda choice: (
            choice.train_positive_pnl_run_count,
            choice.train_positive_ev_rank_run_count,
            choice.train_positive_top_bucket_run_count,
            choice.train_beats_current_run_count,
            choice.train_total_pnl_cents,
            -choice.train_mean_brier,
            -choice.train_mean_log_loss,
            choice.family,
            choice.spec,
            choice.transform,
        ),
    )


def _metrics_by_run(
    rows: Sequence[_OpportunityRow],
    transform: OpportunityScoreTransform,
) -> dict[str, _OpportunityMetrics]:
    grouped: dict[str, list[_OpportunityRow]] = {}
    for row in rows:
        grouped.setdefault(row.run, []).append(row)
    return {run: _evaluate_rows(run_rows, transform) for run, run_rows in grouped.items()}


def _evaluate_rows(
    rows: Sequence[_OpportunityRow],
    transform: OpportunityScoreTransform,
) -> _OpportunityMetrics:
    if not rows:
        return _OpportunityMetrics(
            market_count=0,
            selected_market_count=0,
            total_pnl_cents=0.0,
            avg_pnl_cents_per_market=0.0,
            brier=1.0,
            log_loss=1.0,
            beats_brownian=False,
            beats_market=False,
            beats_current=False,
            ev_rank_correlation_sign=0.0,
            top_bucket_pnl_cents=0.0,
        )
    labels = [1 if row.settlement_result_yes else 0 for row in rows]
    particle = [row.particle_p_yes for row in rows]
    brownian = [row.brownian_p_yes for row in rows]
    market = [row.market_p_yes for row in rows]
    current = [row.current_calibrated_p_yes for row in rows]
    scores = [_score(row, transform) for row in rows]
    pnl = [row.pnl_cents if row.selected else 0.0 for row in rows]
    particle_brier = brier_score(particle, labels)
    particle_log_loss = log_loss(particle, labels)
    brownian_brier = brier_score(brownian, labels)
    brownian_log_loss = log_loss(brownian, labels)
    market_brier = brier_score(market, labels)
    market_log_loss = log_loss(market, labels)
    current_brier = brier_score(current, labels)
    current_log_loss = log_loss(current, labels)
    total_pnl = sum(pnl)
    return _OpportunityMetrics(
        market_count=len(rows),
        selected_market_count=sum(1 for row in rows if row.selected),
        total_pnl_cents=total_pnl,
        avg_pnl_cents_per_market=total_pnl / len(rows),
        brier=particle_brier,
        log_loss=particle_log_loss,
        beats_brownian=particle_brier < brownian_brier and particle_log_loss < brownian_log_loss,
        beats_market=particle_brier < market_brier and particle_log_loss < market_log_loss,
        beats_current=particle_brier < current_brier and particle_log_loss < current_log_loss,
        ev_rank_correlation_sign=pairwise_rank_correlation_sign(scores, pnl),
        top_bucket_pnl_cents=top_bucket_mean_pnl(scores, pnl, top_fraction=0.25),
    )


def _score(row: _OpportunityRow, transform: OpportunityScoreTransform) -> float:
    return (
        row.predicted_ev_cents
        - transform.current_gap_penalty_cents * row.abs_particle_current_gap
        - transform.market_gap_penalty_cents * row.abs_particle_market_gap
    )


def _strict(metrics: _OpportunityMetrics) -> bool:
    return (
        metrics.total_pnl_cents > 0.0
        and metrics.beats_brownian
        and metrics.beats_market
        and metrics.beats_current
        and metrics.ev_rank_correlation_sign > 0.0
        and metrics.top_bucket_pnl_cents > 0.0
    )


def _summarize_holdouts(rows: Sequence[MarketOpportunityLOROHoldoutRow]) -> list[MarketOpportunityLOROSummaryRow]:
    grouped: dict[str, list[MarketOpportunityLOROHoldoutRow]] = {}
    for row in rows:
        grouped.setdefault(row.selector, []).append(row)
    summaries: list[MarketOpportunityLOROSummaryRow] = []
    for selector, selector_rows in grouped.items():
        strict_count = sum(1 for row in selector_rows if row.holdout_strict_gate_pass)
        summaries.append(
            MarketOpportunityLOROSummaryRow(
                selector=selector,
                holdout_count=len(selector_rows),
                total_holdout_pnl_cents=sum(row.holdout_total_pnl_cents for row in selector_rows),
                mean_holdout_brier=_mean(row.holdout_brier for row in selector_rows),
                mean_holdout_log_loss=_mean(row.holdout_log_loss for row in selector_rows),
                positive_pnl_holdout_count=sum(
                    1 for row in selector_rows if row.holdout_total_pnl_cents > 0.0
                ),
                beats_brownian_holdout_count=sum(1 for row in selector_rows if row.holdout_beats_brownian),
                beats_market_holdout_count=sum(1 for row in selector_rows if row.holdout_beats_market),
                beats_current_holdout_count=sum(1 for row in selector_rows if row.holdout_beats_current),
                positive_ev_rank_holdout_count=sum(
                    1 for row in selector_rows if row.holdout_ev_rank_correlation_sign > 0.0
                ),
                positive_top_bucket_holdout_count=sum(
                    1 for row in selector_rows if row.holdout_top_bucket_pnl_cents > 0.0
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
            row.positive_ev_rank_holdout_count,
            row.positive_top_bucket_holdout_count,
            row.total_holdout_pnl_cents,
        ),
        reverse=True,
    )


def _transform_by_name(
    transforms: Sequence[OpportunityScoreTransform],
    name: str,
) -> OpportunityScoreTransform:
    for transform in transforms:
        if transform.name == name:
            return transform
    raise KeyError(name)


def _markdown(report: MarketOpportunityLOROReport) -> str:
    lines = [
        "# Empirical Market Opportunity LORO",
        "",
        f"- source_report: `{report.source_report}`",
        f"- source_run_count: {report.source_run_count}",
        f"- source_opportunity_row_count: {report.source_opportunity_row_count}",
        f"- transforms: {', '.join(report.transforms)}",
        f"- selector: {report.selector}",
        f"- candidate_ready_for_predeclared_shadow: {report.candidate_ready_for_predeclared_shadow}",
        f"- promotion_safe: {report.promotion_safe}",
        f"- conclusion: {report.conclusion}",
        "",
        "## Summary",
        "",
        "| selector | holdouts | pnl_cents | mean_brier | mean_log_loss | positive_pnl | beats_brownian | beats_market | beats_current | ev_rank | top_bucket | strict | strict_all |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|",
    ]
    for row in report.summary_rows:
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
            "| holdout | family | spec | transform | train_pnl | markets | selected | holdout_pnl | brier | beats_current | ev_rank | top_bucket | strict |",
            "|---|---|---|---|---:|---:|---:|---:|---:|---|---:|---:|---|",
        ]
    )
    for row in report.holdout_rows:
        lines.append(
            "| "
            f"{row.holdout_run} | "
            f"{row.family} | "
            f"{row.spec} | "
            f"{row.transform} | "
            f"{row.train_total_pnl_cents:.4f} | "
            f"{row.holdout_market_count} | "
            f"{row.holdout_selected_market_count} | "
            f"{row.holdout_total_pnl_cents:.4f} | "
            f"{row.holdout_brier:.6f} | "
            f"{row.holdout_beats_current} | "
            f"{row.holdout_ev_rank_correlation_sign:.6f} | "
            f"{row.holdout_top_bucket_pnl_cents:.4f} | "
            f"{row.holdout_strict_gate_pass} |"
        )
    return "\n".join(lines) + "\n"


def _mean(values) -> float:
    seq = [float(value) for value in values]
    return sum(seq) / len(seq) if seq else 0.0


def _clamp01(value: float) -> float:
    return max(0.0, min(1.0, float(value)))


if __name__ == "__main__":
    raise SystemExit(main())
