from __future__ import annotations

import argparse
import json
from dataclasses import asdict, replace
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Sequence

from probe_rv600_cumulative_opportunity import discover_roots
from research_particle.replay_runner import ReplayConfig, load_replay_inputs_from_jsonl
from research_particle.rv600_variation_test import (
    CandidateDecision,
    RV600CandidateMetrics,
    RV600VariantRunRow,
    RV600VariantSummaryRow,
    _accepted_decisions,
    _candidate_path,
    _extras_by_key,
    _label_path,
    _row_key,
    _run_rows_for_accounting_modes,
    _summarize,
    grid_specs,
    materialize_rv600_metrics,
)


DEFAULT_BASE_DIR = Path("logs/particle_research/real_shadow")
DEFAULT_REPORTS_DIR = Path("logs/particle_research/reports")
DEFAULT_MIN_ROOT_NAME = "rv600_next_evidence_shadow_20260513T195001Z"
DEFAULT_MIN_DECISION_TS_UTC = "2026-05-13T19:50:00+00:00"
DEFAULT_OUTPUT_JSON = Path("logs/particle_research/reports/rv600_regime_filter_rescue_latest.json")
DEFAULT_OUTPUT_MD = Path("logs/particle_research/reports/rv600_regime_filter_rescue_latest.md")


SOURCES = (
    {
        "name": "Structural clustering of volatility regimes for dynamic trading strategies",
        "url": "https://arxiv.org/abs/2004.09963",
        "use": "Motivates volatility/regime-conditioned abstention and online risk avoidance.",
    },
    {
        "name": "Detecting bearish and bullish markets with hierarchical hidden Markov models",
        "url": "https://arxiv.org/abs/2007.14874",
        "use": "Motivates using market regimes as a trading-strategy filter rather than a stand-alone forecast.",
    },
    {
        "name": "Adaptive Conformal Inference Under Distribution Shift",
        "url": "https://arxiv.org/abs/2106.00170",
        "use": "Motivates treating nonstationarity as an online abstention/coverage problem.",
    },
    {
        "name": "Adaptive Conformal Predictions for Time Series",
        "url": "https://arxiv.org/abs/2202.07282",
        "use": "Motivates time-series-safe adaptive filtering with expert aggregation ideas.",
    },
    {
        "name": "Deflated Sharpe Ratio",
        "url": "https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2460551",
        "use": "Motivates rejecting best-row discoveries unless anchored forward evidence survives.",
    },
)


FeaturePredicate = Callable[[RV600CandidateMetrics, CandidateDecision], bool]


def _parse_dt(value: str) -> datetime:
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def _predicate_specs() -> dict[str, FeaturePredicate]:
    return {
        "all": lambda metric, decision: True,
        "vol_expanding": lambda metric, decision: metric.rv300_annualized_vol > 1.05 * metric.rv600_annualized_vol,
        "vol_not_expanding": lambda metric, decision: metric.rv300_annualized_vol <= 1.05 * metric.rv600_annualized_vol,
        "rv600_low_vol_le_65": lambda metric, decision: metric.rv600_annualized_vol <= 0.65,
        "rv600_high_vol_gt_65": lambda metric, decision: metric.rv600_annualized_vol > 0.65,
        "near_strike_10bp": lambda metric, decision: abs(metric.row.snapshot.spot - metric.row.snapshot.strike)
        / max(abs(metric.row.snapshot.spot), 1.0)
        <= 0.001,
        "far_strike_10bp": lambda metric, decision: abs(metric.row.snapshot.spot - metric.row.snapshot.strike)
        / max(abs(metric.row.snapshot.spot), 1.0)
        > 0.001,
        "market_uncertain_35_65": lambda metric, decision: 0.35 <= metric.row.market_p_yes <= 0.65,
        "market_tailed": lambda metric, decision: metric.row.market_p_yes < 0.35 or metric.row.market_p_yes > 0.65,
        "v28_side_agrees": lambda metric, decision: decision.side == decision.matched_v28_side,
        "v28_side_disagrees": lambda metric, decision: decision.side != decision.matched_v28_side,
    }


def _filter_decisions(
    accepted: Sequence[CandidateDecision],
    metrics_by_key: dict[tuple[str, str], RV600CandidateMetrics],
    predicate: FeaturePredicate,
) -> list[CandidateDecision]:
    kept: list[CandidateDecision] = []
    for decision in accepted:
        metric = metrics_by_key.get((decision.market_ticker, decision.decision_ts_utc.isoformat()))
        if metric is not None and predicate(metric, decision):
            kept.append(decision)
    return kept


def _load_root_metrics(root: Path, *, min_decision_ts_utc: datetime | None) -> list[RV600CandidateMetrics]:
    candidate_path = _candidate_path(root)
    label_path = _label_path(root)
    rows = list(load_replay_inputs_from_jsonl(candidate_path, label_path))
    if min_decision_ts_utc is not None:
        rows = [row for row in rows if row.snapshot.decision_ts_utc >= min_decision_ts_utc]
    extras = _extras_by_key(candidate_path)
    return materialize_rv600_metrics(rows, extras_by_key=extras)


def _candidate_universe(args: argparse.Namespace) -> tuple:
    specs = grid_specs()
    requested = {str(name).strip() for name in args.variant if str(name).strip()}
    if requested:
        specs = tuple(spec for spec in specs if spec.name in requested)
    if args.max_specs and args.max_specs > 0:
        specs = specs[: args.max_specs]
    return specs


def _build_filtered_run_rows(args: argparse.Namespace) -> tuple[list[RV600VariantRunRow], tuple[str, ...]]:
    roots = tuple(args.root or discover_roots(args.base_dir, args.reports_dir, args.min_root_name))
    min_dt = _parse_dt(args.min_decision_ts_utc) if args.min_decision_ts_utc else None
    cfg = ReplayConfig(min_fill_prob=0.0, counterfactual_fill_threshold=0.5)
    predicates = _predicate_specs()
    if args.predicate:
        allowed = set(args.predicate)
        predicates = {name: pred for name, pred in predicates.items() if name in allowed}
    specs = _candidate_universe(args)
    run_rows: list[RV600VariantRunRow] = []
    for root in roots:
        metrics = _load_root_metrics(root, min_decision_ts_utc=min_dt)
        metrics_by_key = {_row_key(metric.row): metric for metric in metrics}
        for spec in specs:
            accepted = _accepted_decisions(metrics, spec, cfg)
            for predicate_name, predicate in predicates.items():
                filtered = accepted if predicate_name == "all" else _filter_decisions(accepted, metrics_by_key, predicate)
                filtered_name = f"{spec.name}__regime_{predicate_name}"
                filtered_spec = replace(spec, name=filtered_name)
                gate_extra = 0 if predicate_name == "all" else 1
                for row in _run_rows_for_accounting_modes(root.name, filtered_spec, len(metrics), filtered, cfg):
                    run_rows.append(replace(row, gate_count=row.gate_count + gate_extra))
    return run_rows, tuple(root.name for root in roots)


def _passes_support(row: RV600VariantSummaryRow) -> bool:
    return (
        row.accounting_mode == "position_capped"
        and row.gate_count <= 4
        and row.accepted_entries >= 25
        and row.selected_pnl_cents > 0.0
        and row.matched_v28_delta_cents > 0.0
        and row.avg_pnl_per_entry_cents >= 10.0
        and row.avg_pnl_per_market_cents > 0.0
        and row.positive_root_rate >= 0.60
        and row.positive_market_rate >= 0.60
        and row.max_single_market_pnl_share <= 0.25
        and row.last_window_pnl_cents > 0.0
        and row.no_fill_penalty_pnl_cents > 0.0
    )


def _balance_penalty(row: RV600VariantSummaryRow) -> float:
    concentration_penalty = max(0.0, row.max_single_market_pnl_share - 0.25) * max(row.selected_pnl_cents, 0.0)
    market_penalty = max(0.0, 0.60 - row.positive_market_rate) * 250.0
    root_penalty = max(0.0, 0.60 - row.positive_root_rate) * 150.0
    recent_penalty = max(0.0, -row.last_window_pnl_cents)
    entry_penalty = max(0, 25 - row.accepted_entries) * 10.0
    return concentration_penalty + market_penalty + root_penalty + recent_penalty + entry_penalty


def _selector_key(row: RV600VariantSummaryRow) -> tuple[bool, float, float, float, float, float]:
    return (
        _passes_support(row),
        row.selected_pnl_cents - _balance_penalty(row),
        row.matched_v28_delta_cents,
        row.positive_market_rate,
        row.positive_root_rate,
        -row.max_single_market_pnl_share,
    )


def _choose_row(rows: Sequence[RV600VariantSummaryRow]) -> RV600VariantSummaryRow | None:
    candidates = [
        row
        for row in rows
        if row.accounting_mode == "position_capped"
        and row.selected_pnl_cents > 0.0
        and row.matched_v28_delta_cents > 0.0
        and row.accepted_entries >= 10
    ]
    return max(candidates, key=_selector_key) if candidates else None


def _compact_row(row: RV600VariantSummaryRow | RV600VariantRunRow | None) -> dict[str, Any]:
    if row is None:
        return {}
    payload = asdict(row)
    return {
        key: payload.get(key)
        for key in (
            "root_name",
            "variant",
            "accounting_mode",
            "gate_count",
            "accepted_entries",
            "distinct_markets",
            "selected_pnl_cents",
            "matched_v28_delta_cents",
            "avg_pnl_per_entry_cents",
            "positive_root_rate",
            "positive_market_rate",
            "max_single_market_pnl_share",
            "last_window_pnl_cents",
            "no_fill_penalty_pnl_cents",
            "rejection_reason",
        )
        if key in payload
    }


def _prequential_probe(run_rows: Sequence[RV600VariantRunRow], root_names: Sequence[str], min_train_roots: int) -> dict[str, Any]:
    selections: list[dict[str, Any]] = []
    test_rows: list[RV600VariantRunRow] = []
    for split_idx in range(min_train_roots, len(root_names)):
        train_roots = set(root_names[:split_idx])
        test_root = root_names[split_idx]
        train_summary = _summarize([row for row in run_rows if row.root_name in train_roots])
        selected = _choose_row(train_summary)
        test_row = None
        if selected is not None:
            test_row = next(
                (
                    row
                    for row in run_rows
                    if row.root_name == test_root
                    and row.variant == selected.variant
                    and row.accounting_mode == selected.accounting_mode
                ),
                None,
            )
        if test_row is not None:
            test_rows.append(test_row)
        selections.append(
            {
                "split": f"{root_names[0]}..{root_names[split_idx - 1]} -> {test_root}",
                "selected": _compact_row(selected),
                "test": _compact_row(test_row),
            }
        )
    total_pnl = sum(row.selected_pnl_cents for row in test_rows)
    total_delta = sum(row.matched_v28_delta_cents for row in test_rows)
    total_entries = sum(row.accepted_entries for row in test_rows)
    positive_roots = sum(1 for row in test_rows if row.selected_pnl_cents > 0.0)
    test_count = len(test_rows)
    positive_rate = positive_roots / test_count if test_count else 0.0
    max_contribution = max(
        (
            row.max_single_market_pnl_share * row.selected_pnl_cents
            if row.selected_pnl_cents > 0.0
            else 0.0
        )
        for row in test_rows
    ) if test_rows else 0.0
    max_share = max_contribution / total_pnl if total_pnl > 0.0 else 0.0
    return {
        "min_train_roots": min_train_roots,
        "split_count": len(selections),
        "selection_count": sum(1 for item in selections if item["selected"]),
        "test_entry_count": total_entries,
        "test_selected_pnl_cents": total_pnl,
        "test_matched_v28_delta_cents": total_delta,
        "positive_test_root_rate": positive_rate,
        "max_single_market_pnl_share": max_share,
        "prequential_gate_pass": (
            test_count > 0
            and total_entries >= 25
            and total_pnl > 0.0
            and total_delta > 0.0
            and positive_rate >= 0.60
            and max_share <= 0.25
        ),
        "selections": selections,
    }


def build_report(args: argparse.Namespace) -> dict[str, Any]:
    run_rows, root_names = _build_filtered_run_rows(args)
    summary_rows = list(_summarize(run_rows))
    support_rows = [row for row in summary_rows if _passes_support(row)]
    positive_position_rows = [
        row
        for row in summary_rows
        if row.accounting_mode == "position_capped" and row.selected_pnl_cents > 0.0
    ]
    top_rows = sorted(positive_position_rows, key=_selector_key, reverse=True)[:12]
    best_row = top_rows[0] if top_rows else None
    prequential = _prequential_probe(run_rows, root_names, args.min_train_roots)
    decision = (
        "regime_filter_rescue_pass"
        if support_rows and prequential.get("prequential_gate_pass") is True
        else "regime_filter_rescue_failed"
    )
    return {
        "schema_version": "rv600-regime-filter-rescue-v1",
        "generated_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "research_only": True,
        "decision": decision,
        "modeling_choice": (
            "Use a small predeclared set of causal regime predicates as abstention filters on existing RV600 grid "
            "variants, then require anchored forward validation. This targets the observed root/market instability "
            "without changing live logic or inventing a new broad entry model."
        ),
        "sources": list(SOURCES),
        "roots": list(root_names),
        "predicate_count": len(_predicate_specs()) if not args.predicate else len(args.predicate),
        "summary_row_count": len(summary_rows),
        "support_row_count": len(support_rows),
        "positive_position_row_count": len(positive_position_rows),
        "best_row": _compact_row(best_row),
        "support_rows": [_compact_row(row) for row in support_rows[:20]],
        "top_rows": [_compact_row(row) for row in top_rows],
        "prequential": prequential,
        "interpretation": _interpretation(decision, support_rows, prequential),
        "inputs": {
            "base_dir": str(args.base_dir),
            "reports_dir": str(args.reports_dir),
            "min_root_name": args.min_root_name,
            "min_decision_ts_utc": args.min_decision_ts_utc,
            "roots": [str(root) for root in args.root],
            "predicates": list(args.predicate),
            "max_specs": args.max_specs,
        },
    }


def _interpretation(decision: str, support_rows: Sequence[RV600VariantSummaryRow], prequential: dict[str, Any]) -> str:
    if decision == "regime_filter_rescue_pass":
        return (
            "At least one regime-filtered existing RV600 row cleared cumulative support gates and anchored forward "
            "validation. Run the full objective audit before considering any completion decision."
        )
    if not support_rows:
        return (
            "No predeclared causal regime filter produced a cumulative support row. The rescue remains rejected; "
            f"anchored forward pass={prequential.get('prequential_gate_pass')}."
        )
    return (
        "A cumulative support row exists, but anchored forward validation failed; treat it as sample-mined until "
        "fresh forward evidence clears the gates."
    )


def _markdown(report: dict[str, Any]) -> str:
    lines = [
        "# RV600 Regime-Filter Rescue",
        "",
        f"- generated_utc: {report['generated_utc']}",
        f"- research_only: {report['research_only']}",
        f"- decision: {report['decision']}",
        f"- modeling_choice: {report['modeling_choice']}",
        "",
        "## Sources Considered",
        "",
    ]
    for source in report["sources"]:
        lines.append(f"- {source['name']}: {source['url']} - {source['use']}")
    lines.extend(
        [
            "",
            "## Counts",
            "",
            f"- roots: {len(report['roots'])}",
            f"- predicate_count: {report['predicate_count']}",
            f"- summary_row_count: {report['summary_row_count']}",
            f"- positive_position_row_count: {report['positive_position_row_count']}",
            f"- support_row_count: {report['support_row_count']}",
            "",
            "## Best Row",
            "",
        ]
    )
    if report["best_row"]:
        for key, value in report["best_row"].items():
            lines.append(f"- {key}: `{value}`")
    else:
        lines.append("none")
    pre = report["prequential"]
    lines.extend(
        [
            "",
            "## Anchored Forward Probe",
            "",
            f"- split_count: {pre['split_count']}",
            f"- selection_count: {pre['selection_count']}",
            f"- test_entry_count: {pre['test_entry_count']}",
            f"- test_selected_pnl_cents: {pre['test_selected_pnl_cents']}",
            f"- test_matched_v28_delta_cents: {pre['test_matched_v28_delta_cents']}",
            f"- positive_test_root_rate: {pre['positive_test_root_rate']}",
            f"- max_single_market_pnl_share: {pre['max_single_market_pnl_share']}",
            f"- prequential_gate_pass: {pre['prequential_gate_pass']}",
            "",
            "## Top Rows",
            "",
            "| variant | accounting | gates | entries | pnl | v28 delta | pos roots | pos markets | max share | last window | rejection |",
            "|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---|",
        ]
    )
    for row in report["top_rows"]:
        lines.append(
            "| `{variant}` | {accounting_mode} | {gate_count} | {accepted_entries} | {selected_pnl_cents:.1f} | {matched_v28_delta_cents:.1f} | {positive_root_rate:.2f} | {positive_market_rate:.2f} | {max_single_market_pnl_share:.2f} | {last_window_pnl_cents:.1f} | `{rejection_reason}` |".format(
                **row
            )
        )
    lines.extend(["", "## Interpretation", "", report["interpretation"], ""])
    return "\n".join(lines)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Causal regime-filter rescue audit for current RV600 bounded roots.")
    parser.add_argument("--root", action="append", type=Path, default=[])
    parser.add_argument("--base-dir", type=Path, default=DEFAULT_BASE_DIR)
    parser.add_argument("--reports-dir", type=Path, default=DEFAULT_REPORTS_DIR)
    parser.add_argument("--min-root-name", default=DEFAULT_MIN_ROOT_NAME)
    parser.add_argument("--min-decision-ts-utc", default=DEFAULT_MIN_DECISION_TS_UTC)
    parser.add_argument("--min-train-roots", type=int, default=3)
    parser.add_argument("--variant", action="append", default=[])
    parser.add_argument("--predicate", action="append", default=[])
    parser.add_argument("--max-specs", type=int, default=0)
    parser.add_argument("--output-json", type=Path, default=DEFAULT_OUTPUT_JSON)
    parser.add_argument("--output-md", type=Path, default=DEFAULT_OUTPUT_MD)
    parser.add_argument("--write", action="store_true")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    report = build_report(args)
    if args.write:
        args.output_json.parent.mkdir(parents=True, exist_ok=True)
        args.output_json.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        args.output_md.write_text(_markdown(report), encoding="utf-8")
    print(f"decision={report['decision']}")
    print(f"roots={len(report['roots'])}")
    print(f"summary_row_count={report['summary_row_count']}")
    print(f"support_row_count={report['support_row_count']}")
    print(f"prequential_gate_pass={report['prequential']['prequential_gate_pass']}")
    print(f"prequential_test_pnl_cents={report['prequential']['test_selected_pnl_cents']:.4f}")
    if args.write:
        print(f"output_json={args.output_json}")
        print(f"output_md={args.output_md}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
