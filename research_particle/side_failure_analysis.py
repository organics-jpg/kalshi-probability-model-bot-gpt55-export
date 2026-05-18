from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass, replace
from pathlib import Path
from typing import Iterable, Literal, Sequence

from .replay_runner import (
    ReplayConfig,
    ReplayDecision,
    ReplayInput,
    evaluate_replay,
    load_replay_inputs_from_jsonl,
)
from .schemas import CandidateSnapshot, Side


FillPolicy = Literal["threshold", "always_fill", "never_fill"]


@dataclass(frozen=True)
class ForcedSideSummary:
    side: Side
    candidate_count: int
    selected_count: int
    filled_count: int
    win_count: int
    win_rate: float
    total_counterfactual_pnl_cents: float
    avg_counterfactual_pnl_cents_per_selected: float
    avg_selected_ev_cents: float


@dataclass(frozen=True)
class SelectedSideSummary:
    side: Side
    selected_count: int
    win_count: int
    win_rate: float
    total_counterfactual_pnl_cents: float
    avg_counterfactual_pnl_cents: float
    avg_selected_ev_cents: float
    avg_ev_margin_cents: float
    avg_particle_p_yes: float
    avg_market_p_yes: float
    avg_current_calibrated_p_yes: float
    opposite_side_total_pnl_cents: float
    selected_minus_opposite_pnl_cents: float
    worse_than_opposite_count: int


@dataclass(frozen=True)
class MarketSideFailure:
    market_ticker: str
    candidate_count: int
    selected_count: int
    settlement_result_yes: bool
    selected_yes_count: int
    selected_no_count: int
    selected_yes_pnl_cents: float
    selected_no_pnl_cents: float
    forced_yes_pnl_cents: float
    forced_no_pnl_cents: float
    selected_minus_opposite_pnl_cents: float


@dataclass(frozen=True)
class MarginBucketSummary:
    bucket: str
    candidate_count: int
    selected_count: int
    avg_abs_ev_margin_cents: float
    selected_yes_count: int
    selected_no_count: int
    total_counterfactual_pnl_cents: float
    selected_minus_opposite_pnl_cents: float


@dataclass(frozen=True)
class SideFailureReport:
    candidate_count: int
    source_candidate_count: int | None
    skipped_unlabeled_count: int
    denominator_scope: str
    selected_count: int
    base_total_counterfactual_pnl_cents: float
    base_avg_counterfactual_pnl_cents_per_selected: float
    forced_yes: ForcedSideSummary
    forced_no: ForcedSideSummary
    selected_yes: SelectedSideSummary
    selected_no: SelectedSideSummary
    market_summaries: tuple[MarketSideFailure, ...]
    margin_buckets: tuple[MarginBucketSummary, ...]
    promotion_safe: bool
    note: str


def build_side_failure_report(
    rows: Sequence[ReplayInput],
    config: ReplayConfig | None = None,
) -> SideFailureReport:
    if not rows:
        raise ValueError("at least one replay row is required")
    cfg = config or ReplayConfig()
    sorted_rows = sorted(rows, key=lambda row: (row.snapshot.decision_ts_utc, row.snapshot.market_ticker))
    replay = evaluate_replay(sorted_rows, cfg)
    pairs = list(zip(sorted_rows, replay.decisions))
    forced_yes = _forced_side_summary(pairs, cfg, "yes")
    forced_no = _forced_side_summary(pairs, cfg, "no")
    selected_yes = _selected_side_summary(pairs, cfg, "yes")
    selected_no = _selected_side_summary(pairs, cfg, "no")
    return SideFailureReport(
        candidate_count=len(sorted_rows),
        source_candidate_count=None,
        skipped_unlabeled_count=0,
        denominator_scope="all_labeled_candidates",
        selected_count=replay.selected_count,
        base_total_counterfactual_pnl_cents=replay.total_counterfactual_pnl_cents,
        base_avg_counterfactual_pnl_cents_per_selected=replay.avg_counterfactual_pnl_cents_per_selected,
        forced_yes=forced_yes,
        forced_no=forced_no,
        selected_yes=selected_yes,
        selected_no=selected_no,
        market_summaries=tuple(_market_summaries(pairs, cfg)),
        margin_buckets=tuple(_margin_buckets(pairs, cfg, bucket_count=5)),
        promotion_safe=False,
        note=(
            "Side failure analysis is diagnostic only. Forced-side and side-flip "
            "counterfactuals are not a trading rule unless predeclared and validated "
            "on fresh locked OOS/shadow data."
        ),
    )


def write_side_failure_report(
    report: SideFailureReport,
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
        description="Analyze selected-side failures and same-threshold forced-side counterfactuals."
    )
    parser.add_argument("--candidates", required=True, type=Path)
    parser.add_argument("--labels", required=True, type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--stem", default="side_failure_analysis")
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
        build_side_failure_report(
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
    json_path, md_path = write_side_failure_report(report, args.output_dir, args.stem)
    print(f"candidate_count={report.candidate_count}")
    print(f"source_candidate_count={report.source_candidate_count}")
    print(f"skipped_unlabeled_count={report.skipped_unlabeled_count}")
    print(f"denominator_scope={report.denominator_scope}")
    print(f"selected_count={report.selected_count}")
    print(f"base_total_counterfactual_pnl_cents={report.base_total_counterfactual_pnl_cents:.4f}")
    print(f"forced_yes_total_counterfactual_pnl_cents={report.forced_yes.total_counterfactual_pnl_cents:.4f}")
    print(f"forced_no_total_counterfactual_pnl_cents={report.forced_no.total_counterfactual_pnl_cents:.4f}")
    print(f"selected_yes_pnl_cents={report.selected_yes.total_counterfactual_pnl_cents:.4f}")
    print(f"selected_no_pnl_cents={report.selected_no.total_counterfactual_pnl_cents:.4f}")
    print(f"promotion_safe={report.promotion_safe}")
    print(f"json_report={json_path}")
    print(f"md_report={md_path}")
    return 0


def _forced_side_summary(
    pairs: Sequence[tuple[ReplayInput, ReplayDecision]],
    cfg: ReplayConfig,
    side: Side,
) -> ForcedSideSummary:
    selected = []
    for row, decision in pairs:
        ev = decision.ev_yes_cents if side == "yes" else decision.ev_no_cents
        fill_prob = _fill_prob_for(row.snapshot, side)
        if fill_prob < cfg.min_fill_prob or ev < cfg.min_ev_cents:
            continue
        selected.append((row, decision, ev))
    pnls = [_side_pnl(row, cfg, side) for row, _decision, _ev in selected]
    wins = sum(1 for row, _decision, _ev in selected if _side_won(row, side))
    filled = sum(1 for row, _decision, _ev in selected if _counterfactual_filled(_fill_prob_for(row.snapshot, side), cfg))
    return ForcedSideSummary(
        side=side,
        candidate_count=len(pairs),
        selected_count=len(selected),
        filled_count=filled,
        win_count=wins,
        win_rate=(wins / len(selected) if selected else 0.0),
        total_counterfactual_pnl_cents=sum(pnls),
        avg_counterfactual_pnl_cents_per_selected=(sum(pnls) / len(selected) if selected else 0.0),
        avg_selected_ev_cents=_mean(ev for _row, _decision, ev in selected),
    )


def _selected_side_summary(
    pairs: Sequence[tuple[ReplayInput, ReplayDecision]],
    cfg: ReplayConfig,
    side: Side,
) -> SelectedSideSummary:
    selected = [(row, decision) for row, decision in pairs if decision.selected and decision.side == side]
    opposite: Side = "no" if side == "yes" else "yes"
    selected_pnls = [float(decision.counterfactual_pnl_cents) for _row, decision in selected]
    opposite_pnls = [_side_pnl(row, cfg, opposite) for row, _decision in selected]
    wins = sum(1 for _row, decision in selected if decision.won)
    worse = sum(
        1
        for selected_pnl, opposite_pnl in zip(selected_pnls, opposite_pnls)
        if selected_pnl < opposite_pnl
    )
    return SelectedSideSummary(
        side=side,
        selected_count=len(selected),
        win_count=wins,
        win_rate=(wins / len(selected) if selected else 0.0),
        total_counterfactual_pnl_cents=sum(selected_pnls),
        avg_counterfactual_pnl_cents=(sum(selected_pnls) / len(selected) if selected else 0.0),
        avg_selected_ev_cents=_mean(
            decision.ev_yes_cents if side == "yes" else decision.ev_no_cents
            for _row, decision in selected
        ),
        avg_ev_margin_cents=_mean(abs(decision.ev_yes_cents - decision.ev_no_cents) for _row, decision in selected),
        avg_particle_p_yes=_mean(decision.particle_p_yes for _row, decision in selected),
        avg_market_p_yes=_mean(decision.market_p_yes for _row, decision in selected),
        avg_current_calibrated_p_yes=_mean(decision.current_calibrated_p_yes for _row, decision in selected),
        opposite_side_total_pnl_cents=sum(opposite_pnls),
        selected_minus_opposite_pnl_cents=sum(selected_pnls) - sum(opposite_pnls),
        worse_than_opposite_count=worse,
    )


def _market_summaries(
    pairs: Sequence[tuple[ReplayInput, ReplayDecision]],
    cfg: ReplayConfig,
) -> list[MarketSideFailure]:
    grouped: dict[str, list[tuple[ReplayInput, ReplayDecision]]] = {}
    for row, decision in pairs:
        grouped.setdefault(row.snapshot.market_ticker, []).append((row, decision))
    summaries: list[MarketSideFailure] = []
    for market, market_pairs in grouped.items():
        selected = [(row, decision) for row, decision in market_pairs if decision.selected]
        yes_rows = [(row, decision) for row, decision in selected if decision.side == "yes"]
        no_rows = [(row, decision) for row, decision in selected if decision.side == "no"]
        selected_pnl = sum(float(decision.counterfactual_pnl_cents) for _row, decision in selected)
        opposite_pnl = sum(
            _side_pnl(row, cfg, "no" if decision.side == "yes" else "yes")
            for row, decision in selected
        )
        summaries.append(
            MarketSideFailure(
                market_ticker=market,
                candidate_count=len(market_pairs),
                selected_count=len(selected),
                settlement_result_yes=market_pairs[0][0].label.result_yes,
                selected_yes_count=len(yes_rows),
                selected_no_count=len(no_rows),
                selected_yes_pnl_cents=sum(float(decision.counterfactual_pnl_cents) for _row, decision in yes_rows),
                selected_no_pnl_cents=sum(float(decision.counterfactual_pnl_cents) for _row, decision in no_rows),
                forced_yes_pnl_cents=_forced_side_summary(market_pairs, cfg, "yes").total_counterfactual_pnl_cents,
                forced_no_pnl_cents=_forced_side_summary(market_pairs, cfg, "no").total_counterfactual_pnl_cents,
                selected_minus_opposite_pnl_cents=selected_pnl - opposite_pnl,
            )
        )
    return summaries


def _margin_buckets(
    pairs: Sequence[tuple[ReplayInput, ReplayDecision]],
    cfg: ReplayConfig,
    *,
    bucket_count: int,
) -> list[MarginBucketSummary]:
    selected_pairs = [
        (row, decision)
        for row, decision in pairs
        if decision.selected
    ]
    rows = sorted(
        selected_pairs,
        key=lambda pair: abs(pair[1].ev_yes_cents - pair[1].ev_no_cents),
        reverse=True,
    )
    buckets: list[MarginBucketSummary] = []
    for idx in range(bucket_count):
        start = idx * len(rows) // bucket_count
        end = (idx + 1) * len(rows) // bucket_count
        chunk = rows[start:end]
        selected_pnl = sum(float(decision.counterfactual_pnl_cents) for _row, decision in chunk)
        opposite_pnl = sum(
            _side_pnl(row, cfg, "no" if decision.side == "yes" else "yes")
            for row, decision in chunk
        )
        buckets.append(
            MarginBucketSummary(
                bucket=f"abs_ev_margin_rank_{idx + 1}_of_{bucket_count}",
                candidate_count=len(chunk),
                selected_count=len(chunk),
                avg_abs_ev_margin_cents=_mean(abs(decision.ev_yes_cents - decision.ev_no_cents) for _row, decision in chunk),
                selected_yes_count=sum(1 for _row, decision in chunk if decision.side == "yes"),
                selected_no_count=sum(1 for _row, decision in chunk if decision.side == "no"),
                total_counterfactual_pnl_cents=selected_pnl,
                selected_minus_opposite_pnl_cents=selected_pnl - opposite_pnl,
            )
        )
    return buckets


def _side_pnl(row: ReplayInput, cfg: ReplayConfig, side: Side) -> float:
    fill_prob = _fill_prob_for(row.snapshot, side)
    if not _counterfactual_filled(fill_prob, cfg):
        return -cfg.no_fill_penalty_cents
    ask_cents = row.snapshot.yes_ask_cents if side == "yes" else row.snapshot.no_ask_cents
    return 100.0 - ask_cents - row.snapshot.fee_cents if _side_won(row, side) else -ask_cents


def _side_won(row: ReplayInput, side: Side) -> bool:
    return row.label.result_yes if side == "yes" else not row.label.result_yes


def _fill_prob_for(snapshot: CandidateSnapshot, side: Side) -> float:
    if side == "yes" and snapshot.yes_fill_prob is not None:
        return snapshot.yes_fill_prob
    if side == "no" and snapshot.no_fill_prob is not None:
        return snapshot.no_fill_prob
    return snapshot.fill_prob


def _counterfactual_filled(fill_prob: float, cfg: ReplayConfig) -> bool:
    if cfg.counterfactual_fill_policy == "always_fill":
        return True
    if cfg.counterfactual_fill_policy == "never_fill":
        return False
    return fill_prob >= cfg.counterfactual_fill_threshold


def _markdown(report: SideFailureReport) -> str:
    lines = [
        "# Side Failure Analysis",
        "",
        f"- candidate_count: {report.candidate_count}",
        f"- source_candidate_count: {report.source_candidate_count}",
        f"- skipped_unlabeled_count: {report.skipped_unlabeled_count}",
        f"- denominator_scope: {report.denominator_scope}",
        f"- selected_count: {report.selected_count}",
        f"- base_total_counterfactual_pnl_cents: {report.base_total_counterfactual_pnl_cents:.4f}",
        f"- base_avg_counterfactual_pnl_cents_per_selected: {report.base_avg_counterfactual_pnl_cents_per_selected:.4f}",
        f"- forced_yes_total_counterfactual_pnl_cents: {report.forced_yes.total_counterfactual_pnl_cents:.4f}",
        f"- forced_no_total_counterfactual_pnl_cents: {report.forced_no.total_counterfactual_pnl_cents:.4f}",
        f"- selected_yes_total_counterfactual_pnl_cents: {report.selected_yes.total_counterfactual_pnl_cents:.4f}",
        f"- selected_no_total_counterfactual_pnl_cents: {report.selected_no.total_counterfactual_pnl_cents:.4f}",
        f"- promotion_safe: {report.promotion_safe}",
        f"- note: {report.note}",
        "",
        "## Selected Side Summary",
        "",
        "| side | selected | win_rate | pnl_cents | avg_pnl | avg_ev | avg_margin | opposite_pnl | selected_minus_opposite | worse_than_opposite | avg_particle | avg_market | avg_current |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for side in (report.selected_yes, report.selected_no):
        lines.append(
            "| {side} | {selected_count} | {win_rate:.4f} | {total_counterfactual_pnl_cents:.4f} | "
            "{avg_counterfactual_pnl_cents:.4f} | {avg_selected_ev_cents:.4f} | "
            "{avg_ev_margin_cents:.4f} | {opposite_side_total_pnl_cents:.4f} | "
            "{selected_minus_opposite_pnl_cents:.4f} | {worse_than_opposite_count} | "
            "{avg_particle_p_yes:.6f} | {avg_market_p_yes:.6f} | {avg_current_calibrated_p_yes:.6f} |".format(
                **asdict(side)
            )
        )
    lines.extend(
        [
            "",
            "## Forced Side Summary",
            "",
            "| side | selected | filled | win_rate | pnl_cents | avg_pnl | avg_ev |",
            "|---|---:|---:|---:|---:|---:|---:|",
        ]
    )
    for side in (report.forced_yes, report.forced_no):
        lines.append(
            "| {side} | {selected_count} | {filled_count} | {win_rate:.4f} | "
            "{total_counterfactual_pnl_cents:.4f} | "
            "{avg_counterfactual_pnl_cents_per_selected:.4f} | "
            "{avg_selected_ev_cents:.4f} |".format(**asdict(side))
        )
    lines.extend(
        [
            "",
            "## Markets",
            "",
            "| market | result_yes | candidates | selected | selected_yes | selected_no | yes_pnl | no_pnl | forced_yes_pnl | forced_no_pnl | selected_minus_opposite |",
            "|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
        ]
    )
    for market in report.market_summaries:
        lines.append(
            "| {market_ticker} | {settlement_result_yes} | {candidate_count} | {selected_count} | "
            "{selected_yes_count} | {selected_no_count} | {selected_yes_pnl_cents:.4f} | "
            "{selected_no_pnl_cents:.4f} | {forced_yes_pnl_cents:.4f} | "
            "{forced_no_pnl_cents:.4f} | {selected_minus_opposite_pnl_cents:.4f} |".format(
                **asdict(market)
            )
        )
    lines.extend(["", "## Absolute EV Margin Buckets", ""])
    for bucket in report.margin_buckets:
        lines.append(
            "- {bucket}: selected={selected_count}, avg_abs_margin={avg_abs_ev_margin_cents:.4f}, "
            "yes={selected_yes_count}, no={selected_no_count}, pnl={total_counterfactual_pnl_cents:.4f}, "
            "selected_minus_opposite={selected_minus_opposite_pnl_cents:.4f}".format(
                **asdict(bucket)
            )
        )
    return "\n".join(lines) + "\n"


def _line_count(path: Path) -> int:
    with path.open("r", encoding="utf-8", errors="replace") as handle:
        return sum(1 for line in handle if line.strip())


def _mean(values: Iterable[float]) -> float:
    rows = list(values)
    return sum(rows) / len(rows) if rows else 0.0


if __name__ == "__main__":
    raise SystemExit(main())
