from __future__ import annotations

import argparse
import json
from collections import Counter
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Literal, Sequence

from probe_rv600_native_forward_opportunity import discover_native_roots
from research_particle.replay_runner import ReplayConfig, load_replay_inputs_from_jsonl
from research_particle.rv600_variation_test import (
    RV600VariantRunRow,
    RV600VariantSummaryRow,
    _candidate_path,
    _extras_by_key,
    _label_path,
    _summarize,
    evaluate_variant_specs,
    grid_specs,
    materialize_rv600_metrics,
)


ROOT = Path(__file__).resolve().parent
DEFAULT_OUTPUT_JSON = (
    ROOT / "logs" / "particle_research" / "reports" / "rv600_prequential_selection_latest.json"
)
DEFAULT_OUTPUT_MD = (
    ROOT / "logs" / "particle_research" / "reports" / "rv600_prequential_selection_latest.md"
)
DEFAULT_MIN_DECISION_TS_UTC = "2026-05-13T05:37:07+00:00"

SelectorPolicy = Literal["locked_then_diagnostic", "locked_only", "best_all_entries"]


@dataclass(frozen=True)
class RootEvaluationSummary:
    root_name: str
    candidate_rows: int
    settled_markets: int
    first_decision_ts_utc: str
    last_decision_ts_utc: str


@dataclass(frozen=True)
class SplitSelectionRow:
    split_index: int
    train_root_count: int
    train_roots: tuple[str, ...]
    test_root: str
    selection_basis: str
    train_locked_gate_pass: bool
    selected_variant: str
    selected_accounting_mode: str
    selected_gate_count: int
    train_accepted_entries: int
    train_distinct_markets: int
    train_selected_pnl_cents: float
    train_matched_v28_control_pnl_cents: float
    train_matched_v28_delta_cents: float
    train_positive_root_rate: float
    train_positive_market_rate: float
    train_max_single_market_pnl_share: float
    train_last_window_pnl_cents: float
    train_rejection_reason: str
    test_accepted_entries: int
    test_distinct_markets: int
    test_selected_pnl_cents: float
    test_matched_v28_control_pnl_cents: float
    test_matched_v28_delta_cents: float
    test_avg_pnl_per_entry_cents: float
    test_positive_market_rate: float
    test_max_single_market_pnl_share: float
    test_last_window_pnl_cents: float
    test_rejection_reason: str


@dataclass(frozen=True)
class PrequentialAggregate:
    split_count: int
    skipped_split_count: int
    locked_gate_selection_count: int
    diagnostic_fallback_selection_count: int
    test_total_entries: int
    test_total_distinct_markets: int
    test_selected_pnl_cents: float
    test_matched_v28_control_pnl_cents: float
    test_matched_v28_delta_cents: float
    test_avg_pnl_per_entry_cents: float
    positive_test_split_count: int
    positive_test_split_rate: float
    max_single_test_root_pnl_share: float
    selected_variant_counts: dict[str, int]
    preliminary_prequential_gate_pass: bool
    rejection_reason: str


@dataclass(frozen=True)
class PrequentialSelectionReport:
    generated_utc: str
    schema_version: str
    selector_policy: SelectorPolicy
    min_train_roots: int
    gap_roots: int
    min_decision_ts_utc: str
    roots: tuple[str, ...]
    root_summaries: tuple[RootEvaluationSummary, ...]
    split_rows: tuple[SplitSelectionRow, ...]
    aggregate: PrequentialAggregate
    method_choice: str
    conclusion: str
    output_json: str
    output_md: str


@dataclass(frozen=True)
class _RootBundle:
    root: Path
    summary: RootEvaluationSummary
    run_rows: tuple[RV600VariantRunRow, ...]


def build_report(
    roots: Sequence[Path],
    *,
    selector_policy: SelectorPolicy,
    min_train_roots: int,
    gap_roots: int,
    min_decision_ts_utc: datetime | None,
    output_json: Path,
    output_md: Path,
) -> PrequentialSelectionReport:
    selected_roots = tuple(roots) if roots else discover_native_roots()
    config = ReplayConfig(min_fill_prob=0.0, counterfactual_fill_threshold=0.5)
    specs = grid_specs()
    bundles = tuple(
        bundle
        for root in selected_roots
        if (bundle := _evaluate_root(root, specs, config, min_decision_ts_utc)) is not None
    )
    split_rows: list[SplitSelectionRow] = []
    skipped = 0
    for test_index in range(min_train_roots, len(bundles)):
        train_end = test_index - gap_roots
        if train_end < min_train_roots:
            skipped += 1
            continue
        train = bundles[:train_end]
        test = bundles[test_index]
        train_summary = _summarize(_flatten_run_rows(train))
        selection = _select_candidate(train_summary, selector_policy)
        if selection is None:
            skipped += 1
            continue
        selected, basis, locked_gate_pass = selection
        test_row = _summary_lookup(_summarize(test.run_rows), selected.variant, selected.accounting_mode)
        if test_row is None:
            skipped += 1
            continue
        split_rows.append(
            SplitSelectionRow(
                split_index=len(split_rows) + skipped,
                train_root_count=len(train),
                train_roots=tuple(bundle.root.name for bundle in train),
                test_root=test.root.name,
                selection_basis=basis,
                train_locked_gate_pass=locked_gate_pass,
                selected_variant=selected.variant,
                selected_accounting_mode=selected.accounting_mode,
                selected_gate_count=selected.gate_count,
                train_accepted_entries=selected.accepted_entries,
                train_distinct_markets=selected.distinct_markets,
                train_selected_pnl_cents=selected.selected_pnl_cents,
                train_matched_v28_control_pnl_cents=selected.matched_v28_control_pnl_cents,
                train_matched_v28_delta_cents=selected.matched_v28_delta_cents,
                train_positive_root_rate=selected.positive_root_rate,
                train_positive_market_rate=selected.positive_market_rate,
                train_max_single_market_pnl_share=selected.max_single_market_pnl_share,
                train_last_window_pnl_cents=selected.last_window_pnl_cents,
                train_rejection_reason=selected.rejection_reason,
                test_accepted_entries=test_row.accepted_entries,
                test_distinct_markets=test_row.distinct_markets,
                test_selected_pnl_cents=test_row.selected_pnl_cents,
                test_matched_v28_control_pnl_cents=test_row.matched_v28_control_pnl_cents,
                test_matched_v28_delta_cents=test_row.matched_v28_delta_cents,
                test_avg_pnl_per_entry_cents=test_row.avg_pnl_per_entry_cents,
                test_positive_market_rate=test_row.positive_market_rate,
                test_max_single_market_pnl_share=test_row.max_single_market_pnl_share,
                test_last_window_pnl_cents=test_row.last_window_pnl_cents,
                test_rejection_reason=test_row.rejection_reason,
            )
        )
    aggregate = _aggregate(split_rows, skipped)
    conclusion = _conclusion(aggregate, selector_policy)
    return PrequentialSelectionReport(
        generated_utc=datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        schema_version="rv600-prequential-selection-v1",
        selector_policy=selector_policy,
        min_train_roots=min_train_roots,
        gap_roots=gap_roots,
        min_decision_ts_utc=min_decision_ts_utc.isoformat() if min_decision_ts_utc else "",
        roots=tuple(bundle.root.name for bundle in bundles),
        root_summaries=tuple(bundle.summary for bundle in bundles),
        split_rows=tuple(split_rows),
        aggregate=aggregate,
        method_choice=(
            "Anchored prequential selection: select a variant/accounting mode "
            "using only prior native roots, then score that frozen selection on "
            "the next root. Locked-candidate selections preserve the RV600 "
            "anti-overfitting gates; diagnostic fallbacks are reported but are "
            "never promotable."
        ),
        conclusion=conclusion,
        output_json=str(output_json),
        output_md=str(output_md),
    )


def write_report(report: PrequentialSelectionReport) -> None:
    output_json = Path(report.output_json)
    output_md = Path(report.output_md)
    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_json.write_text(
        json.dumps(asdict(report), indent=2, sort_keys=True),
        encoding="utf-8",
    )
    output_md.write_text(_markdown(report), encoding="utf-8")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Run anchored prequential RV600 selection: choose from prior native "
            "roots and test the frozen choice on the next root."
        )
    )
    parser.add_argument("--root", action="append", type=Path, default=[])
    parser.add_argument("--selector-policy", choices=["locked_then_diagnostic", "locked_only", "best_all_entries"], default="locked_then_diagnostic")
    parser.add_argument("--min-train-roots", type=int, default=3)
    parser.add_argument("--gap-roots", type=int, default=0)
    parser.add_argument("--min-decision-ts-utc", default=DEFAULT_MIN_DECISION_TS_UTC)
    parser.add_argument("--output-json", type=Path, default=DEFAULT_OUTPUT_JSON)
    parser.add_argument("--output-md", type=Path, default=DEFAULT_OUTPUT_MD)
    parser.add_argument("--write", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    report = build_report(
        tuple(args.root),
        selector_policy=args.selector_policy,
        min_train_roots=max(1, args.min_train_roots),
        gap_roots=max(0, args.gap_roots),
        min_decision_ts_utc=(_parse_dt(args.min_decision_ts_utc) if args.min_decision_ts_utc else None),
        output_json=args.output_json,
        output_md=args.output_md,
    )
    if args.write:
        write_report(report)
    agg = report.aggregate
    print(f"roots={len(report.roots)}")
    print(f"selector_policy={report.selector_policy}")
    print(f"split_count={agg.split_count}")
    print(f"skipped_split_count={agg.skipped_split_count}")
    print(f"locked_gate_selection_count={agg.locked_gate_selection_count}")
    print(f"diagnostic_fallback_selection_count={agg.diagnostic_fallback_selection_count}")
    print(f"test_selected_pnl_cents={agg.test_selected_pnl_cents:.4f}")
    print(f"test_matched_v28_control_pnl_cents={agg.test_matched_v28_control_pnl_cents:.4f}")
    print(f"test_matched_v28_delta_cents={agg.test_matched_v28_delta_cents:.4f}")
    print(f"preliminary_prequential_gate_pass={agg.preliminary_prequential_gate_pass}")
    print(f"rejection_reason={agg.rejection_reason or 'none'}")
    print(f"conclusion={report.conclusion}")
    if args.write:
        print(f"output_json={report.output_json}")
        print(f"output_md={report.output_md}")
    return 0


def _evaluate_root(
    root: Path,
    specs: Sequence[object],
    config: ReplayConfig,
    min_decision_ts_utc: datetime | None,
) -> _RootBundle | None:
    rows = load_replay_inputs_from_jsonl(_candidate_path(root), _label_path(root))
    if min_decision_ts_utc is not None:
        rows = [
            row
            for row in rows
            if row.snapshot.decision_ts_utc >= min_decision_ts_utc
        ]
    if not rows:
        return None
    timestamps = [row.snapshot.decision_ts_utc for row in rows]
    metrics = materialize_rv600_metrics(rows, extras_by_key=_extras_by_key(_candidate_path(root)))
    run_rows = evaluate_variant_specs(metrics, specs, root_name=root.name, config=config)
    summary = RootEvaluationSummary(
        root_name=root.name,
        candidate_rows=len(rows),
        settled_markets=len({row.snapshot.market_ticker for row in rows}),
        first_decision_ts_utc=min(timestamps).isoformat(),
        last_decision_ts_utc=max(timestamps).isoformat(),
    )
    return _RootBundle(root=root, summary=summary, run_rows=run_rows)


def _flatten_run_rows(bundles: Sequence[_RootBundle]) -> tuple[RV600VariantRunRow, ...]:
    rows: list[RV600VariantRunRow] = []
    for bundle in bundles:
        rows.extend(bundle.run_rows)
    return tuple(rows)


def _select_candidate(
    summary_rows: Sequence[RV600VariantSummaryRow],
    selector_policy: SelectorPolicy,
) -> tuple[RV600VariantSummaryRow, str, bool] | None:
    if selector_policy in ("locked_then_diagnostic", "locked_only"):
        locked = [row for row in summary_rows if row.locked_candidate_eligible]
        if locked:
            return locked[0], "locked_candidate_eligible", True
        if selector_policy == "locked_only":
            return None
    if selector_policy == "locked_then_diagnostic":
        repeated = [
            row
            for row in summary_rows
            if row.accounting_mode == "all_entries" and row.repeated_entry_gate_pass
        ]
        if repeated:
            return repeated[0], "repeated_all_entries_diagnostic", False
    all_entries = [
        row
        for row in summary_rows
        if row.accounting_mode == "all_entries" and row.accepted_entries > 0
    ]
    if not all_entries:
        return None
    best = max(
        all_entries,
        key=lambda row: (
            row.selected_pnl_cents,
            row.matched_v28_delta_cents,
            row.accepted_entries,
        ),
    )
    return best, "best_all_entries_diagnostic", best.locked_candidate_eligible


def _summary_lookup(
    summary_rows: Sequence[RV600VariantSummaryRow],
    variant: str,
    accounting_mode: str,
) -> RV600VariantSummaryRow | None:
    return next(
        (
            row
            for row in summary_rows
            if row.variant == variant and row.accounting_mode == accounting_mode
        ),
        None,
    )


def _aggregate(split_rows: Sequence[SplitSelectionRow], skipped: int) -> PrequentialAggregate:
    split_count = len(split_rows)
    total_entries = sum(row.test_accepted_entries for row in split_rows)
    total_markets = sum(row.test_distinct_markets for row in split_rows)
    total_pnl = sum(row.test_selected_pnl_cents for row in split_rows)
    matched_v28 = sum(row.test_matched_v28_control_pnl_cents for row in split_rows)
    positive_splits = sum(1 for row in split_rows if row.test_selected_pnl_cents > 0.0)
    positive_root_pnls = [max(0.0, row.test_selected_pnl_cents) for row in split_rows]
    max_root_share = max(positive_root_pnls, default=0.0) / total_pnl if total_pnl > 0.0 else 0.0
    locked_selections = sum(1 for row in split_rows if row.train_locked_gate_pass)
    fallback_selections = split_count - locked_selections
    rejection_reasons: list[str] = []
    if split_count == 0:
        rejection_reasons.append("no_prequential_splits")
    if fallback_selections:
        rejection_reasons.append("diagnostic_fallback_used")
    if total_entries < 25:
        rejection_reasons.append("fewer_than_25_test_entries")
    if total_pnl <= 0.0:
        rejection_reasons.append("nonpositive_test_pnl")
    if total_entries and total_pnl / total_entries < 10.0:
        rejection_reasons.append("avg_test_entry_below_10c")
    if split_count and positive_splits / split_count < 0.60:
        rejection_reasons.append("positive_test_splits_below_60pct")
    if max_root_share > 0.25:
        rejection_reasons.append("single_test_root_share_above_25pct")
    if matched_v28 > 0.0 and total_pnl < 1.20 * matched_v28:
        rejection_reasons.append("does_not_beat_matched_v28_by_20pct")
    return PrequentialAggregate(
        split_count=split_count,
        skipped_split_count=skipped,
        locked_gate_selection_count=locked_selections,
        diagnostic_fallback_selection_count=fallback_selections,
        test_total_entries=total_entries,
        test_total_distinct_markets=total_markets,
        test_selected_pnl_cents=total_pnl,
        test_matched_v28_control_pnl_cents=matched_v28,
        test_matched_v28_delta_cents=total_pnl - matched_v28,
        test_avg_pnl_per_entry_cents=(total_pnl / total_entries if total_entries else 0.0),
        positive_test_split_count=positive_splits,
        positive_test_split_rate=(positive_splits / split_count if split_count else 0.0),
        max_single_test_root_pnl_share=max_root_share,
        selected_variant_counts=dict(Counter(row.selected_variant for row in split_rows)),
        preliminary_prequential_gate_pass=not rejection_reasons,
        rejection_reason=";".join(rejection_reasons),
    )


def _conclusion(aggregate: PrequentialAggregate, selector_policy: SelectorPolicy) -> str:
    if aggregate.split_count == 0:
        return "No prequential split could be scored from the current native RV600 roots."
    if aggregate.diagnostic_fallback_selection_count:
        return (
            "Prequential scoring needed diagnostic fallback selections, so the "
            "positive or negative aggregate cannot promote an RV600 strategy."
        )
    if aggregate.test_selected_pnl_cents <= 0.0:
        return "Locked-gate prequential selections lost money out of sample."
    if not aggregate.preliminary_prequential_gate_pass:
        return (
            "Locked-gate prequential selections were profitable, but at least one "
            f"preliminary gate failed: {aggregate.rejection_reason}."
        )
    return (
        "Locked-gate prequential selections passed this preliminary diagnostic; "
        "the full RV600 goal still requires the larger forward-shadow completion audit."
    )


def _markdown(report: PrequentialSelectionReport) -> str:
    agg = report.aggregate
    lines = [
        "# RV600 Prequential Selection Diagnostic",
        "",
        f"- generated_utc: {report.generated_utc}",
        f"- selector_policy: {report.selector_policy}",
        f"- min_train_roots: {report.min_train_roots}",
        f"- gap_roots: {report.gap_roots}",
        f"- min_decision_ts_utc: {report.min_decision_ts_utc}",
        f"- roots: {len(report.roots)}",
        f"- split_count: {agg.split_count}",
        f"- skipped_split_count: {agg.skipped_split_count}",
        f"- locked_gate_selection_count: {agg.locked_gate_selection_count}",
        f"- diagnostic_fallback_selection_count: {agg.diagnostic_fallback_selection_count}",
        f"- test_total_entries: {agg.test_total_entries}",
        f"- test_total_distinct_markets: {agg.test_total_distinct_markets}",
        f"- test_selected_pnl_cents: {agg.test_selected_pnl_cents}",
        f"- test_matched_v28_control_pnl_cents: {agg.test_matched_v28_control_pnl_cents}",
        f"- test_matched_v28_delta_cents: {agg.test_matched_v28_delta_cents}",
        f"- test_avg_pnl_per_entry_cents: {agg.test_avg_pnl_per_entry_cents}",
        f"- positive_test_split_rate: {agg.positive_test_split_rate}",
        f"- max_single_test_root_pnl_share: {agg.max_single_test_root_pnl_share}",
        f"- selected_variant_counts: {json.dumps(agg.selected_variant_counts, sort_keys=True)}",
        f"- preliminary_prequential_gate_pass: {agg.preliminary_prequential_gate_pass}",
        f"- rejection_reason: {agg.rejection_reason or 'none'}",
        f"- conclusion: {report.conclusion}",
        "",
        "## Method Choice",
        "",
        report.method_choice,
        "",
        "External options checked for the modeling blocker:",
        "",
        "- Deflated Sharpe / multiple-testing adjustment: useful for large return series, but current RV600 has too few native roots for a stable Sharpe-style correction.",
        "- CSCV / probability of backtest overfitting: strong for many trials across a return matrix, but it would reuse scarce roots combinatorially instead of mimicking the live sequence.",
        "- Purged or embargoed time-series CV: useful when labels overlap; this probe exposes `gap_roots` as a simple embargo, but keeps the default next-root test because roots are already settled market blocks.",
        "- Anchored walk-forward / prequential selection: best fit here because it tests exactly the action the research loop would take next: select from prior roots only, then evaluate the next incoming market block.",
        "- Synthetic/bootstrap replay: rejected for this completion gate because it would not be incoming-market shadow evidence.",
        "",
        "## Roots",
        "",
        "| root | rows | markets | first | last |",
        "|---|---:|---:|---|---|",
    ]
    for row in report.root_summaries:
        lines.append(
            f"| `{row.root_name}` | {row.candidate_rows} | {row.settled_markets} | "
            f"{row.first_decision_ts_utc} | {row.last_decision_ts_utc} |"
        )
    lines.extend(
        [
            "",
            "## Splits",
            "",
            "| split | train_roots | test_root | basis | locked_gate | variant | accounting | train_pnl | test_entries | test_pnl | test_v28 | test_delta | test_rejection |",
            "|---:|---:|---|---|---|---|---|---:|---:|---:|---:|---:|---|",
        ]
    )
    for row in report.split_rows:
        lines.append(
            f"| {row.split_index} | {row.train_root_count} | `{row.test_root}` | "
            f"{row.selection_basis} | {row.train_locked_gate_pass} | "
            f"`{row.selected_variant}` | {row.selected_accounting_mode} | "
            f"{row.train_selected_pnl_cents:.2f} | {row.test_accepted_entries} | "
            f"{row.test_selected_pnl_cents:.2f} | {row.test_matched_v28_control_pnl_cents:.2f} | "
            f"{row.test_matched_v28_delta_cents:.2f} | {row.test_rejection_reason or 'none'} |"
        )
    return "\n".join(lines) + "\n"


def _parse_dt(value: str) -> datetime:
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


if __name__ == "__main__":
    raise SystemExit(main())
