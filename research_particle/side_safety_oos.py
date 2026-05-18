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
HypothesisId = Literal["side_safe_yes_only_v1"]


@dataclass(frozen=True)
class PredeclaredGateConfig:
    min_candidate_count: int = 500
    min_market_count: int = 4
    min_selected_count: int = 100
    min_total_pnl_cents: float = 1.0
    min_avg_pnl_per_selected_cents: float = 0.01
    require_positive_ev_rank: bool = True
    require_positive_top_ev_bucket: bool = True
    require_beats_base_pnl: bool = True


@dataclass(frozen=True)
class SideSafetyGateResults:
    enough_candidates: bool
    enough_markets: bool
    enough_selected: bool
    positive_total_pnl: bool
    positive_avg_pnl: bool
    positive_ev_rank: bool
    positive_top_ev_bucket: bool
    beats_base_pnl: bool
    locked_oos_scope: bool
    all_passed: bool


@dataclass(frozen=True)
class SideSafetyOOSReport:
    hypothesis_id: HypothesisId
    evaluation_scope: EvaluationScope
    candidate_count: int
    source_candidate_count: int | None
    skipped_unlabeled_count: int
    denominator_scope: str
    market_count: int
    base_selected_count: int
    base_total_counterfactual_pnl_cents: float
    side_safe_selected_count: int
    side_safe_total_counterfactual_pnl_cents: float
    side_safe_avg_counterfactual_pnl_cents_per_selected: float
    side_safe_win_rate: float
    blocked_no_count: int
    blocked_no_counterfactual_pnl_cents: float
    blocked_no_loss_avoided_cents: float
    side_safe_ev_rank_correlation_sign: float
    side_safe_top_ev_bucket_pnl_cents: float
    gate_config: PredeclaredGateConfig
    gate_results: SideSafetyGateResults
    promotion_safe: bool
    note: str


def evaluate_side_safety_oos(
    rows: Sequence[ReplayInput],
    config: ReplayConfig | None = None,
    *,
    hypothesis_id: HypothesisId = "side_safe_yes_only_v1",
    evaluation_scope: EvaluationScope = "same_sample_diagnostic",
    gate_config: PredeclaredGateConfig | None = None,
) -> SideSafetyOOSReport:
    if not rows:
        raise ValueError("at least one replay row is required")
    cfg = config or ReplayConfig()
    gates = gate_config or PredeclaredGateConfig()
    sorted_rows = sorted(rows, key=lambda row: (row.snapshot.decision_ts_utc, row.snapshot.market_ticker))
    base = evaluate_replay(sorted_rows, cfg)
    if hypothesis_id != "side_safe_yes_only_v1":
        raise ValueError(f"unsupported hypothesis_id {hypothesis_id}")
    selected = [decision for decision in base.decisions if decision.selected and decision.side == "yes"]
    blocked_no = [decision for decision in base.decisions if decision.selected and decision.side == "no"]
    side_safe_pnl = sum(float(decision.counterfactual_pnl_cents) for decision in selected)
    blocked_no_pnl = sum(float(decision.counterfactual_pnl_cents) for decision in blocked_no)
    selected_ev = [float(decision.ev_yes_cents) for decision in selected]
    selected_pnl = [float(decision.counterfactual_pnl_cents) for decision in selected]
    wins = sum(1 for decision in selected if decision.won)
    market_count = len({row.snapshot.market_ticker for row in sorted_rows})
    ev_rank = pairwise_rank_correlation_sign(selected_ev, selected_pnl) if selected else 0.0
    top_bucket = top_bucket_mean_pnl(selected_ev, selected_pnl, top_fraction=0.25) if selected else 0.0
    gate_results = _gate_results(
        candidate_count=len(sorted_rows),
        market_count=market_count,
        selected_count=len(selected),
        total_pnl=side_safe_pnl,
        avg_pnl=(side_safe_pnl / len(selected) if selected else 0.0),
        ev_rank=ev_rank,
        top_bucket=top_bucket,
        base_total_pnl=base.total_counterfactual_pnl_cents,
        evaluation_scope=evaluation_scope,
        gates=gates,
    )
    promotion_safe = bool(gate_results.all_passed)
    return SideSafetyOOSReport(
        hypothesis_id=hypothesis_id,
        evaluation_scope=evaluation_scope,
        candidate_count=len(sorted_rows),
        source_candidate_count=None,
        skipped_unlabeled_count=0,
        denominator_scope="all_labeled_candidates",
        market_count=market_count,
        base_selected_count=base.selected_count,
        base_total_counterfactual_pnl_cents=base.total_counterfactual_pnl_cents,
        side_safe_selected_count=len(selected),
        side_safe_total_counterfactual_pnl_cents=side_safe_pnl,
        side_safe_avg_counterfactual_pnl_cents_per_selected=(
            side_safe_pnl / len(selected) if selected else 0.0
        ),
        side_safe_win_rate=(wins / len(selected) if selected else 0.0),
        blocked_no_count=len(blocked_no),
        blocked_no_counterfactual_pnl_cents=blocked_no_pnl,
        blocked_no_loss_avoided_cents=max(0.0, -blocked_no_pnl),
        side_safe_ev_rank_correlation_sign=ev_rank,
        side_safe_top_ev_bucket_pnl_cents=top_bucket,
        gate_config=gates,
        gate_results=gate_results,
        promotion_safe=promotion_safe,
        note=(
            "side_safe_yes_only_v1 is a predeclared OOS hypothesis derived from "
            "prior same-sample diagnostics. Same-sample reports must not be used "
            "for promotion. Locked OOS/shadow reports are still research-only and "
            "cannot affect live trading until all project promotion gates pass."
        ),
    )


def write_side_safety_oos_report(
    report: SideSafetyOOSReport,
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
        description="Evaluate the predeclared side_safe_yes_only_v1 OOS shadow hypothesis."
    )
    parser.add_argument("--candidates", required=True, type=Path)
    parser.add_argument("--labels", required=True, type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--stem", default="side_safety_oos")
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
    parser.add_argument("--gate-min-candidates", default=500, type=int)
    parser.add_argument("--gate-min-markets", default=4, type=int)
    parser.add_argument("--gate-min-selected", default=100, type=int)
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
        evaluate_side_safety_oos(
            rows,
            ReplayConfig(
                min_ev_cents=args.min_ev_cents,
                min_fill_prob=args.min_fill_prob,
                no_fill_penalty_cents=args.no_fill_penalty_cents,
                counterfactual_fill_policy=args.counterfactual_fill_policy,
                counterfactual_fill_threshold=args.counterfactual_fill_threshold,
            ),
            evaluation_scope=args.evaluation_scope,
            gate_config=PredeclaredGateConfig(
                min_candidate_count=args.gate_min_candidates,
                min_market_count=args.gate_min_markets,
                min_selected_count=args.gate_min_selected,
            ),
        ),
        source_candidate_count=source_candidate_count,
        skipped_unlabeled_count=skipped_unlabeled_count,
        denominator_scope=denominator_scope,
    )
    json_path, md_path = write_side_safety_oos_report(report, args.output_dir, args.stem)
    print(f"hypothesis_id={report.hypothesis_id}")
    print(f"evaluation_scope={report.evaluation_scope}")
    print(f"candidate_count={report.candidate_count}")
    print(f"source_candidate_count={report.source_candidate_count}")
    print(f"skipped_unlabeled_count={report.skipped_unlabeled_count}")
    print(f"denominator_scope={report.denominator_scope}")
    print(f"market_count={report.market_count}")
    print(f"base_total_counterfactual_pnl_cents={report.base_total_counterfactual_pnl_cents:.4f}")
    print(f"side_safe_selected_count={report.side_safe_selected_count}")
    print(f"side_safe_total_counterfactual_pnl_cents={report.side_safe_total_counterfactual_pnl_cents:.4f}")
    print(f"blocked_no_count={report.blocked_no_count}")
    print(f"blocked_no_loss_avoided_cents={report.blocked_no_loss_avoided_cents:.4f}")
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
    evaluation_scope: EvaluationScope,
    gates: PredeclaredGateConfig,
) -> SideSafetyGateResults:
    enough_candidates = candidate_count >= gates.min_candidate_count
    enough_markets = market_count >= gates.min_market_count
    enough_selected = selected_count >= gates.min_selected_count
    positive_total_pnl = total_pnl >= gates.min_total_pnl_cents
    positive_avg_pnl = avg_pnl >= gates.min_avg_pnl_per_selected_cents
    positive_ev_rank = (ev_rank > 0.0) if gates.require_positive_ev_rank else True
    positive_top_ev_bucket = (top_bucket > 0.0) if gates.require_positive_top_ev_bucket else True
    beats_base_pnl = (total_pnl > base_total_pnl) if gates.require_beats_base_pnl else True
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
            locked_oos_scope,
        )
    )
    return SideSafetyGateResults(
        enough_candidates=enough_candidates,
        enough_markets=enough_markets,
        enough_selected=enough_selected,
        positive_total_pnl=positive_total_pnl,
        positive_avg_pnl=positive_avg_pnl,
        positive_ev_rank=positive_ev_rank,
        positive_top_ev_bucket=positive_top_ev_bucket,
        beats_base_pnl=beats_base_pnl,
        locked_oos_scope=locked_oos_scope,
        all_passed=all_passed,
    )


def _markdown(report: SideSafetyOOSReport) -> str:
    lines = [
        "# Side Safety OOS Report",
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
        f"- side_safe_selected_count: {report.side_safe_selected_count}",
        f"- side_safe_total_counterfactual_pnl_cents: {report.side_safe_total_counterfactual_pnl_cents:.4f}",
        f"- side_safe_avg_counterfactual_pnl_cents_per_selected: {report.side_safe_avg_counterfactual_pnl_cents_per_selected:.4f}",
        f"- side_safe_win_rate: {report.side_safe_win_rate:.4f}",
        f"- blocked_no_count: {report.blocked_no_count}",
        f"- blocked_no_counterfactual_pnl_cents: {report.blocked_no_counterfactual_pnl_cents:.4f}",
        f"- blocked_no_loss_avoided_cents: {report.blocked_no_loss_avoided_cents:.4f}",
        f"- side_safe_ev_rank_correlation_sign: {report.side_safe_ev_rank_correlation_sign:.6f}",
        f"- side_safe_top_ev_bucket_pnl_cents: {report.side_safe_top_ev_bucket_pnl_cents:.4f}",
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
