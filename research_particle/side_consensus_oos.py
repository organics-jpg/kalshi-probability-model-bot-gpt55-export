from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass, replace
from pathlib import Path
from typing import Literal, Sequence

from .replay_runner import (
    ReplayConfig,
    ReplayDecision,
    ReplayInput,
    evaluate_replay,
    load_replay_inputs_from_jsonl,
)
from .validation import pairwise_rank_correlation_sign, top_bucket_mean_pnl


EvaluationScope = Literal["same_sample_diagnostic", "locked_oos_shadow"]
HypothesisId = Literal["skip_against_market_current_consensus_10_v1"]


@dataclass(frozen=True)
class SideConsensusGateConfig:
    min_candidate_count: int = 1000
    min_market_count: int = 5
    min_selected_count: int = 100
    min_total_pnl_cents: float = 1.0
    min_avg_pnl_per_selected_cents: float = 0.01
    consensus_min_confidence: float = 0.10
    require_positive_ev_rank: bool = True
    require_positive_top_ev_bucket: bool = True
    require_beats_base_pnl: bool = True


@dataclass(frozen=True)
class SideConsensusGateResults:
    enough_candidates: bool
    enough_markets: bool
    enough_selected: bool
    positive_total_pnl: bool
    positive_avg_pnl: bool
    positive_ev_rank: bool
    positive_top_ev_bucket: bool
    beats_base_pnl: bool
    all_candidate_denominator: bool
    locked_oos_scope: bool
    all_passed: bool


@dataclass(frozen=True)
class SideConsensusOOSReport:
    hypothesis_id: HypothesisId
    evaluation_scope: EvaluationScope
    candidate_count: int
    source_candidate_count: int | None
    skipped_unlabeled_count: int
    denominator_scope: str
    market_count: int
    base_selected_count: int
    base_total_counterfactual_pnl_cents: float
    consensus_selected_count: int
    consensus_total_counterfactual_pnl_cents: float
    consensus_avg_counterfactual_pnl_cents_per_selected: float
    consensus_win_rate: float
    blocked_against_consensus_count: int
    blocked_against_consensus_counterfactual_pnl_cents: float
    blocked_against_consensus_loss_avoided_cents: float
    consensus_ev_rank_correlation_sign: float
    consensus_top_ev_bucket_pnl_cents: float
    gate_config: SideConsensusGateConfig
    gate_results: SideConsensusGateResults
    promotion_safe: bool
    note: str


def evaluate_side_consensus_oos(
    rows: Sequence[ReplayInput],
    config: ReplayConfig | None = None,
    *,
    hypothesis_id: HypothesisId = "skip_against_market_current_consensus_10_v1",
    evaluation_scope: EvaluationScope = "same_sample_diagnostic",
    denominator_scope: str = "all_labeled_candidates",
    gate_config: SideConsensusGateConfig | None = None,
) -> SideConsensusOOSReport:
    if not rows:
        raise ValueError("at least one replay row is required")
    cfg = config or ReplayConfig()
    gates = gate_config or SideConsensusGateConfig()
    if hypothesis_id != "skip_against_market_current_consensus_10_v1":
        raise ValueError(f"unsupported hypothesis_id {hypothesis_id}")
    sorted_rows = sorted(rows, key=lambda row: (row.snapshot.decision_ts_utc, row.snapshot.market_ticker))
    base = evaluate_replay(sorted_rows, cfg)
    base_selected = [decision for decision in base.decisions if decision.selected]
    kept = [
        decision
        for decision in base_selected
        if not _against_market_current_consensus(
            decision,
            min_confidence=gates.consensus_min_confidence,
        )
    ]
    kept_ids = {id(decision) for decision in kept}
    blocked = [decision for decision in base_selected if id(decision) not in kept_ids]
    selected_ev = [max(float(decision.ev_yes_cents), float(decision.ev_no_cents)) for decision in kept]
    selected_pnl = [float(decision.counterfactual_pnl_cents) for decision in kept]
    total_pnl = sum(selected_pnl)
    wins = sum(1 for decision in kept if decision.won)
    blocked_pnl = sum(float(decision.counterfactual_pnl_cents) for decision in blocked)
    market_count = len({row.snapshot.market_ticker for row in sorted_rows})
    ev_rank = pairwise_rank_correlation_sign(selected_ev, selected_pnl) if kept else 0.0
    top_bucket = top_bucket_mean_pnl(selected_ev, selected_pnl, top_fraction=0.25) if kept else 0.0
    gate_results = _gate_results(
        candidate_count=len(sorted_rows),
        market_count=market_count,
        selected_count=len(kept),
        total_pnl=total_pnl,
        avg_pnl=(total_pnl / len(kept) if kept else 0.0),
        ev_rank=ev_rank,
        top_bucket=top_bucket,
        base_total_pnl=base.total_counterfactual_pnl_cents,
        denominator_scope=denominator_scope,
        evaluation_scope=evaluation_scope,
        gates=gates,
    )
    return SideConsensusOOSReport(
        hypothesis_id=hypothesis_id,
        evaluation_scope=evaluation_scope,
        candidate_count=len(sorted_rows),
        source_candidate_count=None,
        skipped_unlabeled_count=0,
        denominator_scope=denominator_scope,
        market_count=market_count,
        base_selected_count=base.selected_count,
        base_total_counterfactual_pnl_cents=base.total_counterfactual_pnl_cents,
        consensus_selected_count=len(kept),
        consensus_total_counterfactual_pnl_cents=total_pnl,
        consensus_avg_counterfactual_pnl_cents_per_selected=(total_pnl / len(kept) if kept else 0.0),
        consensus_win_rate=(wins / len(kept) if kept else 0.0),
        blocked_against_consensus_count=len(blocked),
        blocked_against_consensus_counterfactual_pnl_cents=blocked_pnl,
        blocked_against_consensus_loss_avoided_cents=max(0.0, -blocked_pnl),
        consensus_ev_rank_correlation_sign=ev_rank,
        consensus_top_ev_bucket_pnl_cents=top_bucket,
        gate_config=gates,
        gate_results=gate_results,
        promotion_safe=bool(gate_results.all_passed),
        note=(
            "skip_against_market_current_consensus_10_v1 is a predeclared selection "
            "hypothesis derived from prior diagnostics. Same-sample reports are not "
            "promotion evidence. Locked OOS/shadow reports remain research-only and "
            "must not affect live trading until the broader particle goal gates pass."
        ),
    )


def write_side_consensus_oos_report(
    report: SideConsensusOOSReport,
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
        description="Evaluate the predeclared market/current consensus-veto OOS shadow hypothesis."
    )
    parser.add_argument("--candidates", required=True, type=Path)
    parser.add_argument("--labels", required=True, type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--stem", default="side_consensus_oos")
    parser.add_argument(
        "--hypothesis-id",
        choices=["skip_against_market_current_consensus_10_v1"],
        default="skip_against_market_current_consensus_10_v1",
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
    parser.add_argument("--gate-min-selected", default=100, type=int)
    parser.add_argument("--consensus-min-confidence", default=0.10, type=float)
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
    report = evaluate_side_consensus_oos(
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
        denominator_scope=denominator_scope,
        gate_config=SideConsensusGateConfig(
            min_candidate_count=args.gate_min_candidates,
            min_market_count=args.gate_min_markets,
            min_selected_count=args.gate_min_selected,
            consensus_min_confidence=args.consensus_min_confidence,
        ),
    )
    report = replace(
        report,
        source_candidate_count=source_candidate_count,
        skipped_unlabeled_count=skipped_unlabeled_count,
    )
    json_path, md_path = write_side_consensus_oos_report(report, args.output_dir, args.stem)
    print(f"hypothesis_id={report.hypothesis_id}")
    print(f"evaluation_scope={report.evaluation_scope}")
    print(f"candidate_count={report.candidate_count}")
    print(f"source_candidate_count={report.source_candidate_count}")
    print(f"skipped_unlabeled_count={report.skipped_unlabeled_count}")
    print(f"denominator_scope={report.denominator_scope}")
    print(f"market_count={report.market_count}")
    print(f"base_total_counterfactual_pnl_cents={report.base_total_counterfactual_pnl_cents:.4f}")
    print(f"consensus_selected_count={report.consensus_selected_count}")
    print(f"consensus_total_counterfactual_pnl_cents={report.consensus_total_counterfactual_pnl_cents:.4f}")
    print(f"blocked_against_consensus_count={report.blocked_against_consensus_count}")
    print(
        "blocked_against_consensus_loss_avoided_cents="
        f"{report.blocked_against_consensus_loss_avoided_cents:.4f}"
    )
    print(f"promotion_safe={report.promotion_safe}")
    print(f"json_report={json_path}")
    print(f"md_report={md_path}")
    return 0


def _gate_results(
    *,
    candidate_count: int,
    market_count: int,
    selected_count: int,
    total_pnl: float,
    avg_pnl: float,
    ev_rank: float,
    top_bucket: float,
    base_total_pnl: float,
    denominator_scope: str,
    evaluation_scope: EvaluationScope,
    gates: SideConsensusGateConfig,
) -> SideConsensusGateResults:
    enough_candidates = candidate_count >= gates.min_candidate_count
    enough_markets = market_count >= gates.min_market_count
    enough_selected = selected_count >= gates.min_selected_count
    positive_total_pnl = total_pnl >= gates.min_total_pnl_cents
    positive_avg_pnl = avg_pnl >= gates.min_avg_pnl_per_selected_cents
    positive_ev_rank = ev_rank > 0.0 if gates.require_positive_ev_rank else True
    positive_top_ev_bucket = top_bucket > 0.0 if gates.require_positive_top_ev_bucket else True
    beats_base_pnl = total_pnl > base_total_pnl if gates.require_beats_base_pnl else True
    all_candidate_denominator = denominator_scope == "all_labeled_candidates"
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
            beats_base_pnl,
            all_candidate_denominator,
            locked_oos_scope,
        )
    )
    return SideConsensusGateResults(
        enough_candidates=enough_candidates,
        enough_markets=enough_markets,
        enough_selected=enough_selected,
        positive_total_pnl=positive_total_pnl,
        positive_avg_pnl=positive_avg_pnl,
        positive_ev_rank=positive_ev_rank,
        positive_top_ev_bucket=positive_top_ev_bucket,
        beats_base_pnl=beats_base_pnl,
        all_candidate_denominator=all_candidate_denominator,
        locked_oos_scope=locked_oos_scope,
        all_passed=all_passed,
    )


def _against_market_current_consensus(
    decision: ReplayDecision,
    *,
    min_confidence: float,
) -> bool:
    market_side = _side_from_probability(decision.market_p_yes)
    current_side = _side_from_probability(decision.current_calibrated_p_yes)
    if market_side != current_side:
        return False
    if decision.side == market_side:
        return False
    return min(_prob_confidence(decision.market_p_yes), _prob_confidence(decision.current_calibrated_p_yes)) >= min_confidence


def _side_from_probability(probability: float) -> str:
    return "yes" if float(probability) >= 0.5 else "no"


def _prob_confidence(probability: float) -> float:
    return abs(float(probability) - 0.5)


def _line_count(path: Path) -> int:
    with path.open("r", encoding="utf-8", errors="replace") as handle:
        return sum(1 for line in handle if line.strip())


def _markdown(report: SideConsensusOOSReport) -> str:
    lines = [
        "# Side Consensus OOS Report",
        "",
        f"- hypothesis_id: {report.hypothesis_id}",
        f"- evaluation_scope: {report.evaluation_scope}",
        f"- candidate_count: {report.candidate_count}",
        f"- source_candidate_count: {report.source_candidate_count}",
        f"- skipped_unlabeled_count: {report.skipped_unlabeled_count}",
        f"- denominator_scope: {report.denominator_scope}",
        f"- market_count: {report.market_count}",
        f"- base_selected_count: {report.base_selected_count}",
        f"- base_total_counterfactual_pnl_cents: {report.base_total_counterfactual_pnl_cents:.4f}",
        f"- consensus_selected_count: {report.consensus_selected_count}",
        f"- consensus_total_counterfactual_pnl_cents: {report.consensus_total_counterfactual_pnl_cents:.4f}",
        f"- consensus_avg_counterfactual_pnl_cents_per_selected: {report.consensus_avg_counterfactual_pnl_cents_per_selected:.4f}",
        f"- consensus_win_rate: {report.consensus_win_rate:.4f}",
        f"- blocked_against_consensus_count: {report.blocked_against_consensus_count}",
        f"- blocked_against_consensus_counterfactual_pnl_cents: {report.blocked_against_consensus_counterfactual_pnl_cents:.4f}",
        f"- blocked_against_consensus_loss_avoided_cents: {report.blocked_against_consensus_loss_avoided_cents:.4f}",
        f"- consensus_ev_rank_correlation_sign: {report.consensus_ev_rank_correlation_sign:.6f}",
        f"- consensus_top_ev_bucket_pnl_cents: {report.consensus_top_ev_bucket_pnl_cents:.4f}",
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


if __name__ == "__main__":
    raise SystemExit(main())
