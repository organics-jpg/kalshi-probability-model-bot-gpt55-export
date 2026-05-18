from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Callable, Literal, Sequence

from .empirical_current_anchor_diagnostic import (
    EmpiricalCurrentAnchorSpec,
    _specs as _current_anchor_specs,
    materialize_empirical_current_anchor_rows,
)
from .empirical_next_second_particle_diagnostic import (
    EmpiricalSecondParticleSpec,
    _load_eligible_run,
    _specs as _empirical_specs,
    materialize_empirical_second_particle_rows,
)
from .replay_runner import ReplayConfig, ReplayDecision, ReplayInput, ReplayReport, evaluate_replay
from .validation import brier_score, log_loss, pairwise_rank_correlation_sign, top_bucket_mean_pnl


Family = Literal["empirical", "current_anchor"]


@dataclass(frozen=True)
class EmpiricalMarketOpportunityRunInput:
    name: str
    root: str
    row_count: int
    market_count: int
    spot_tick_count: int


@dataclass(frozen=True)
class EmpiricalMarketOpportunityRunRow:
    run: str
    family: str
    spec: str
    candidate_count: int
    market_count: int
    selected_market_count: int
    total_counterfactual_pnl_cents: float
    avg_counterfactual_pnl_cents_per_market: float
    brier: float
    log_loss: float
    beats_brownian: bool
    beats_market: bool
    beats_current_calibrated: bool
    ev_rank_correlation_sign: float
    top_ev_bucket_pnl_cents: float
    strict_gate_pass: bool


@dataclass(frozen=True)
class EmpiricalMarketOpportunityChoiceRow:
    run: str
    family: str
    spec: str
    market_ticker: str
    candidate_count: int
    decision_ts_utc: str
    selected: bool
    side: str
    predicted_ev_cents: float
    pnl_cents: float
    won: bool | None
    settlement_result_yes: bool
    particle_p_yes: float
    brownian_p_yes: float
    market_p_yes: float
    current_calibrated_p_yes: float
    ev_yes_cents: float
    ev_no_cents: float
    abs_particle_current_gap: float
    abs_particle_market_gap: float


@dataclass(frozen=True)
class EmpiricalMarketOpportunitySummaryRow:
    family: str
    spec: str
    run_count: int
    market_count: int
    selected_market_count: int
    total_counterfactual_pnl_cents: float
    mean_brier: float
    mean_log_loss: float
    positive_pnl_count: int
    beats_brownian_count: int
    beats_market_count: int
    beats_current_count: int
    positive_ev_rank_count: int
    positive_top_bucket_count: int
    strict_gate_count: int
    strict_all_runs: bool


@dataclass(frozen=True)
class EmpiricalMarketOpportunityDiagnosticReport:
    run_inputs: tuple[EmpiricalMarketOpportunityRunInput, ...]
    skipped_run_roots: tuple[str, ...]
    families: tuple[str, ...]
    run_rows: tuple[EmpiricalMarketOpportunityRunRow, ...]
    opportunity_rows: tuple[EmpiricalMarketOpportunityChoiceRow, ...]
    summary_rows: tuple[EmpiricalMarketOpportunitySummaryRow, ...]
    candidate_ready_for_predeclared_shadow: bool
    promotion_safe: bool
    conclusion: str


def build_empirical_market_opportunity_diagnostic(
    run_roots: Sequence[Path],
    *,
    families: Sequence[Family] = ("empirical", "current_anchor"),
    replay_config: ReplayConfig | None = None,
    max_spot_age_ms: float = 5_000.0,
) -> EmpiricalMarketOpportunityDiagnosticReport:
    cfg = replay_config or ReplayConfig(min_fill_prob=0.5, counterfactual_fill_threshold=0.5)
    loaded_runs: list[tuple[EmpiricalMarketOpportunityRunInput, tuple[ReplayInput, ...], tuple]] = []
    skipped: list[str] = []
    for root in run_roots:
        loaded = _load_eligible_run(root)
        if loaded is None:
            skipped.append(str(root))
            continue
        meta, rows, ticks = loaded
        loaded_runs.append(
            (
                EmpiricalMarketOpportunityRunInput(
                    name=meta.name,
                    root=meta.root,
                    row_count=meta.row_count,
                    market_count=meta.market_count,
                    spot_tick_count=meta.spot_tick_count,
                ),
                rows,
                ticks,
            )
        )
    plan = _family_plan(families)
    run_rows: list[EmpiricalMarketOpportunityRunRow] = []
    opportunity_rows: list[EmpiricalMarketOpportunityChoiceRow] = []
    for meta, rows, ticks in loaded_runs:
        times = [tick.available_ts_utc for tick in ticks]
        prices = [float(tick.price) for tick in ticks]
        for family, spec_name, materializer in plan:
            materialized = materializer(rows, ticks, times, prices, meta.name, max_spot_age_ms)
            replay = evaluate_replay(materialized, cfg)
            market_report = _evaluate_market_opportunities(replay)
            opportunity_rows.extend(_choice_rows(meta.name, family, spec_name, market_report.choices))
            run_rows.append(
                EmpiricalMarketOpportunityRunRow(
                    run=meta.name,
                    family=family,
                    spec=spec_name,
                    candidate_count=replay.candidate_count,
                    market_count=market_report.market_count,
                    selected_market_count=market_report.selected_market_count,
                    total_counterfactual_pnl_cents=market_report.total_counterfactual_pnl_cents,
                    avg_counterfactual_pnl_cents_per_market=market_report.avg_counterfactual_pnl_cents_per_market,
                    brier=market_report.brier,
                    log_loss=market_report.log_loss,
                    beats_brownian=market_report.beats_brownian,
                    beats_market=market_report.beats_market,
                    beats_current_calibrated=market_report.beats_current_calibrated,
                    ev_rank_correlation_sign=market_report.ev_rank_correlation_sign,
                    top_ev_bucket_pnl_cents=market_report.top_ev_bucket_pnl_cents,
                    strict_gate_pass=market_report.strict_gate_pass,
                )
            )
    summaries = tuple(_summarize(run_rows))
    candidate_ready = any(row.strict_all_runs for row in summaries)
    conclusion = (
        "At least one empirical market-opportunity spec cleared every eligible locked run. "
        "Because this is same-evidence research, it only nominates a fresh predeclared shadow run."
        if candidate_ready
        else "No empirical market-opportunity spec cleared strict eligible locked-run gates."
    )
    return EmpiricalMarketOpportunityDiagnosticReport(
        run_inputs=tuple(meta for meta, _, _ in loaded_runs),
        skipped_run_roots=tuple(skipped),
        families=tuple(families),
        run_rows=tuple(run_rows),
        opportunity_rows=tuple(opportunity_rows),
        summary_rows=summaries,
        candidate_ready_for_predeclared_shadow=candidate_ready,
        promotion_safe=False,
        conclusion=conclusion,
    )


def write_empirical_market_opportunity_diagnostic(
    report: EmpiricalMarketOpportunityDiagnosticReport,
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
        description="Collapse empirical-family replays to one best predicted-EV opportunity per market."
    )
    parser.add_argument("--run-root", action="append", required=True, type=Path)
    parser.add_argument(
        "--family",
        action="append",
        choices=["empirical", "current_anchor"],
        default=None,
        help="optional family subset; defaults to both",
    )
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--stem", default="empirical_market_opportunity_diagnostic")
    parser.add_argument("--max-spot-age-ms", default=5_000.0, type=float)
    parser.add_argument("--min-fill-prob", default=0.5, type=float)
    parser.add_argument("--counterfactual-fill-threshold", default=0.5, type=float)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    families = tuple(args.family or ("empirical", "current_anchor"))
    report = build_empirical_market_opportunity_diagnostic(
        args.run_root,
        families=families,
        replay_config=ReplayConfig(
            min_fill_prob=args.min_fill_prob,
            counterfactual_fill_threshold=args.counterfactual_fill_threshold,
        ),
        max_spot_age_ms=args.max_spot_age_ms,
    )
    json_path, md_path = write_empirical_market_opportunity_diagnostic(report, args.output_dir, args.stem)
    print(f"eligible_run_count={len(report.run_inputs)}")
    print(f"skipped_run_count={len(report.skipped_run_roots)}")
    print(f"family_count={len(report.families)}")
    print(f"run_row_count={len(report.run_rows)}")
    print(f"opportunity_row_count={len(report.opportunity_rows)}")
    print(f"summary_row_count={len(report.summary_rows)}")
    print(f"candidate_ready_for_predeclared_shadow={report.candidate_ready_for_predeclared_shadow}")
    print(f"promotion_safe={report.promotion_safe}")
    print(f"json_report={json_path}")
    print(f"md_report={md_path}")
    return 0


@dataclass(frozen=True)
class _MarketOpportunityScore:
    market_count: int
    selected_market_count: int
    total_counterfactual_pnl_cents: float
    avg_counterfactual_pnl_cents_per_market: float
    brier: float
    log_loss: float
    beats_brownian: bool
    beats_market: bool
    beats_current_calibrated: bool
    ev_rank_correlation_sign: float
    top_ev_bucket_pnl_cents: float
    strict_gate_pass: bool
    choices: tuple["_ChosenMarketOpportunity", ...]


@dataclass(frozen=True)
class _ChosenMarketOpportunity:
    decision: ReplayDecision
    candidate_count: int


def _evaluate_market_opportunities(replay: ReplayReport) -> _MarketOpportunityScore:
    grouped: dict[str, list[ReplayDecision]] = {}
    for decision in replay.decisions:
        grouped.setdefault(decision.market_ticker, []).append(decision)
    choices: list[_ChosenMarketOpportunity] = []
    for market in sorted(grouped):
        decisions = grouped[market]
        selected = [decision for decision in decisions if decision.selected]
        if selected:
            chosen = max(selected, key=_predicted_ev)
        else:
            chosen = max(decisions, key=_predicted_ev)
        choices.append(_ChosenMarketOpportunity(decision=chosen, candidate_count=len(decisions)))
    chosen_decisions = [choice.decision for choice in choices]
    labels = [1 if decision.settlement_result_yes else 0 for decision in chosen_decisions]
    particle = [decision.particle_p_yes for decision in chosen_decisions]
    brownian = [decision.brownian_p_yes for decision in chosen_decisions]
    market = [decision.market_p_yes for decision in chosen_decisions]
    current = [decision.current_calibrated_p_yes for decision in chosen_decisions]
    predicted_ev = [_predicted_ev(decision) for decision in chosen_decisions]
    pnl = [decision.counterfactual_pnl_cents if decision.selected else 0.0 for decision in chosen_decisions]
    particle_brier = brier_score(particle, labels)
    particle_log_loss = log_loss(particle, labels)
    brownian_brier = brier_score(brownian, labels)
    brownian_log_loss = log_loss(brownian, labels)
    market_brier = brier_score(market, labels)
    market_log_loss = log_loss(market, labels)
    current_brier = brier_score(current, labels)
    current_log_loss = log_loss(current, labels)
    total_pnl = sum(pnl)
    ev_rank = pairwise_rank_correlation_sign(predicted_ev, pnl)
    top_bucket = top_bucket_mean_pnl(predicted_ev, pnl, top_fraction=0.25)
    beats_brownian = particle_brier < brownian_brier and particle_log_loss < brownian_log_loss
    beats_market = particle_brier < market_brier and particle_log_loss < market_log_loss
    beats_current = particle_brier < current_brier and particle_log_loss < current_log_loss
    strict = total_pnl > 0.0 and beats_brownian and beats_market and beats_current and ev_rank > 0.0 and top_bucket > 0.0
    return _MarketOpportunityScore(
        market_count=len(chosen_decisions),
        selected_market_count=sum(1 for decision in chosen_decisions if decision.selected),
        total_counterfactual_pnl_cents=total_pnl,
        avg_counterfactual_pnl_cents_per_market=total_pnl / len(chosen_decisions) if chosen_decisions else 0.0,
        brier=particle_brier,
        log_loss=particle_log_loss,
        beats_brownian=beats_brownian,
        beats_market=beats_market,
        beats_current_calibrated=beats_current,
        ev_rank_correlation_sign=ev_rank,
        top_ev_bucket_pnl_cents=top_bucket,
        strict_gate_pass=strict,
        choices=tuple(choices),
    )


def _family_plan(
    families: Sequence[Family],
) -> list[tuple[str, str, Callable[[Sequence[ReplayInput], tuple, list, list, str, float], tuple[ReplayInput, ...]]]]:
    requested = tuple(dict.fromkeys(families))
    unknown = sorted(set(requested) - {"empirical", "current_anchor"})
    if unknown:
        raise ValueError(f"unknown family/families: {', '.join(unknown)}")
    plan = []
    if "empirical" in requested:
        for spec in _empirical_specs():
            plan.append(("empirical", spec.name, _empirical_materializer(spec)))
    if "current_anchor" in requested:
        for spec in _current_anchor_specs():
            plan.append(("current_anchor", spec.name, _current_anchor_materializer(spec)))
    return plan


def _empirical_materializer(spec: EmpiricalSecondParticleSpec):
    def materializer(rows, ticks, times, prices, run_name, max_spot_age_ms):
        materialized, _ = materialize_empirical_second_particle_rows(
            rows,
            times,
            prices,
            spec,
            run_name=run_name,
            max_spot_age_ms=max_spot_age_ms,
        )
        return materialized

    return materializer


def _current_anchor_materializer(spec: EmpiricalCurrentAnchorSpec):
    def materializer(rows, ticks, times, prices, run_name, max_spot_age_ms):
        materialized, _ = materialize_empirical_current_anchor_rows(
            rows,
            ticks,
            spec,
            run_name=run_name,
            max_spot_age_ms=max_spot_age_ms,
        )
        return materialized

    return materializer


def _summarize(rows: Sequence[EmpiricalMarketOpportunityRunRow]) -> list[EmpiricalMarketOpportunitySummaryRow]:
    grouped: dict[tuple[str, str], list[EmpiricalMarketOpportunityRunRow]] = {}
    for row in rows:
        grouped.setdefault((row.family, row.spec), []).append(row)
    summaries: list[EmpiricalMarketOpportunitySummaryRow] = []
    for (family, spec), spec_rows in sorted(grouped.items()):
        strict_count = sum(1 for row in spec_rows if row.strict_gate_pass)
        summaries.append(
            EmpiricalMarketOpportunitySummaryRow(
                family=family,
                spec=spec,
                run_count=len(spec_rows),
                market_count=sum(row.market_count for row in spec_rows),
                selected_market_count=sum(row.selected_market_count for row in spec_rows),
                total_counterfactual_pnl_cents=sum(row.total_counterfactual_pnl_cents for row in spec_rows),
                mean_brier=_mean(row.brier for row in spec_rows),
                mean_log_loss=_mean(row.log_loss for row in spec_rows),
                positive_pnl_count=sum(1 for row in spec_rows if row.total_counterfactual_pnl_cents > 0.0),
                beats_brownian_count=sum(1 for row in spec_rows if row.beats_brownian),
                beats_market_count=sum(1 for row in spec_rows if row.beats_market),
                beats_current_count=sum(1 for row in spec_rows if row.beats_current_calibrated),
                positive_ev_rank_count=sum(1 for row in spec_rows if row.ev_rank_correlation_sign > 0.0),
                positive_top_bucket_count=sum(1 for row in spec_rows if row.top_ev_bucket_pnl_cents > 0.0),
                strict_gate_count=strict_count,
                strict_all_runs=(strict_count == len(spec_rows) and bool(spec_rows)),
            )
        )
    return sorted(
        summaries,
        key=lambda row: (
            row.strict_all_runs,
            row.strict_gate_count,
            row.beats_current_count,
            row.positive_ev_rank_count,
            row.total_counterfactual_pnl_cents,
        ),
        reverse=True,
    )


def _markdown(report: EmpiricalMarketOpportunityDiagnosticReport) -> str:
    lines = [
        "# Empirical Market Opportunity Diagnostic",
        "",
        f"- eligible_run_count: {len(report.run_inputs)}",
        f"- skipped_run_count: {len(report.skipped_run_roots)}",
        f"- families: {', '.join(report.families)}",
        f"- opportunity_rows: {len(report.opportunity_rows)}",
        f"- candidate_ready_for_predeclared_shadow: {report.candidate_ready_for_predeclared_shadow}",
        f"- promotion_safe: {report.promotion_safe}",
        f"- conclusion: {report.conclusion}",
        "",
        "## Summary",
        "",
        "| family | spec | runs | markets | selected_markets | pnl_cents | mean_brier | mean_log_loss | positive_pnl | beats_brownian | beats_market | beats_current | ev_rank | top_bucket | strict | strict_all |",
        "|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|",
    ]
    for row in report.summary_rows:
        lines.append(
            "| "
            f"{row.family} | "
            f"{row.spec} | "
            f"{row.run_count} | "
            f"{row.market_count} | "
            f"{row.selected_market_count} | "
            f"{row.total_counterfactual_pnl_cents:.4f} | "
            f"{row.mean_brier:.6f} | "
            f"{row.mean_log_loss:.6f} | "
            f"{row.positive_pnl_count}/{row.run_count} | "
            f"{row.beats_brownian_count}/{row.run_count} | "
            f"{row.beats_market_count}/{row.run_count} | "
            f"{row.beats_current_count}/{row.run_count} | "
            f"{row.positive_ev_rank_count}/{row.run_count} | "
            f"{row.positive_top_bucket_count}/{row.run_count} | "
            f"{row.strict_gate_count}/{row.run_count} | "
            f"{row.strict_all_runs} |"
        )
    lines.extend(
        [
            "",
            "## Runs",
            "",
            "| run | family | spec | candidates | markets | selected_markets | pnl_cents | avg_pnl_market | brier | beats_current | ev_rank | top_bucket | strict |",
            "|---|---|---|---:|---:|---:|---:|---:|---:|---|---:|---:|---|",
        ]
    )
    for row in report.run_rows:
        lines.append(
            "| "
            f"{row.run} | "
            f"{row.family} | "
            f"{row.spec} | "
            f"{row.candidate_count} | "
            f"{row.market_count} | "
            f"{row.selected_market_count} | "
            f"{row.total_counterfactual_pnl_cents:.4f} | "
            f"{row.avg_counterfactual_pnl_cents_per_market:.4f} | "
            f"{row.brier:.6f} | "
            f"{row.beats_current_calibrated} | "
            f"{row.ev_rank_correlation_sign:.6f} | "
            f"{row.top_ev_bucket_pnl_cents:.4f} | "
            f"{row.strict_gate_pass} |"
        )
    lines.extend(["", "## Run Inputs", "", "| run | rows | markets | spot_ticks |", "|---|---:|---:|---:|"])
    for row in report.run_inputs:
        lines.append(f"| {row.name} | {row.row_count} | {row.market_count} | {row.spot_tick_count} |")
    if report.skipped_run_roots:
        lines.extend(["", "## Skipped Runs", ""])
        lines.extend(f"- `{root}`" for root in report.skipped_run_roots)
    return "\n".join(lines) + "\n"


def _choice_rows(
    run: str,
    family: str,
    spec: str,
    choices: Sequence[_ChosenMarketOpportunity],
) -> list[EmpiricalMarketOpportunityChoiceRow]:
    rows: list[EmpiricalMarketOpportunityChoiceRow] = []
    for choice in choices:
        decision = choice.decision
        side = decision.side if decision.side is not None else ""
        rows.append(
            EmpiricalMarketOpportunityChoiceRow(
                run=run,
                family=family,
                spec=spec,
                market_ticker=decision.market_ticker,
                candidate_count=choice.candidate_count,
                decision_ts_utc=decision.decision_ts_utc.isoformat(),
                selected=decision.selected,
                side=str(side),
                predicted_ev_cents=_predicted_ev(decision),
                pnl_cents=decision.counterfactual_pnl_cents if decision.selected else 0.0,
                won=decision.won,
                settlement_result_yes=decision.settlement_result_yes,
                particle_p_yes=decision.particle_p_yes,
                brownian_p_yes=decision.brownian_p_yes,
                market_p_yes=decision.market_p_yes,
                current_calibrated_p_yes=decision.current_calibrated_p_yes,
                ev_yes_cents=decision.ev_yes_cents,
                ev_no_cents=decision.ev_no_cents,
                abs_particle_current_gap=abs(decision.particle_p_yes - decision.current_calibrated_p_yes),
                abs_particle_market_gap=abs(decision.particle_p_yes - decision.market_p_yes),
            )
        )
    return rows


def _predicted_ev(decision: ReplayDecision) -> float:
    return max(float(decision.ev_yes_cents), float(decision.ev_no_cents))


def _mean(values) -> float:
    seq = [float(value) for value in values]
    return sum(seq) / len(seq) if seq else 0.0


if __name__ == "__main__":
    raise SystemExit(main())
