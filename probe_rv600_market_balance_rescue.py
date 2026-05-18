from __future__ import annotations

import argparse
import json
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from probe_rv600_cumulative_opportunity import discover_roots
from research_particle.replay_runner import ReplayConfig
from research_particle.rv600_variation_test import (
    RV600VariantRunRow,
    RV600VariantSummaryRow,
    _summarize,
    build_rv600_variation_report,
)


DEFAULT_BASE_DIR = Path("logs/particle_research/real_shadow")
DEFAULT_REPORTS_DIR = Path("logs/particle_research/reports")
DEFAULT_MIN_ROOT_NAME = "rv600_next_evidence_shadow_20260513T195001Z"
DEFAULT_MIN_DECISION_TS_UTC = "2026-05-13T19:50:00+00:00"
DEFAULT_OUTPUT_JSON = Path("logs/particle_research/reports/rv600_market_balance_rescue_latest.json")
DEFAULT_OUTPUT_MD = Path("logs/particle_research/reports/rv600_market_balance_rescue_latest.md")


SOURCES = (
    {
        "name": "Return-diversification portfolio selection",
        "url": "https://arxiv.org/abs/2312.09707",
        "use": "Motivates optimizing return jointly with diversification rather than total PnL alone.",
    },
    {
        "name": "Mean-CVaR with cardinality/rebalancing constraints",
        "url": "https://link.springer.com/article/10.1007/s11831-020-09522-1",
        "use": "Motivates explicit risk constraints and cardinality limits when return-only selection is too concentrated.",
    },
    {
        "name": "Deflated Sharpe Ratio",
        "url": "https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2460551",
        "use": "Motivates treating best-row discovery as multiple-testing-prone until forward evidence survives.",
    },
    {
        "name": "Purged and embargoed validation",
        "url": "https://en.wikipedia.org/wiki/Purged_cross-validation",
        "use": "Motivates time-ordered validation instead of random folds for event-driven financial labels.",
    },
    {
        "name": "Concentration-risk constraints",
        "url": "https://en.wikipedia.org/wiki/Portfolio_optimization#Concentration_risk",
        "use": "Motivates hard upper bounds on single-component contribution/exposure.",
    },
)


def _load_dt(value: str) -> datetime:
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def _is_core_positive(row: RV600VariantSummaryRow) -> bool:
    return (
        row.selected_pnl_cents > 0.0
        and row.avg_pnl_per_entry_cents >= 10.0
        and row.matched_v28_delta_cents > 0.0
        and row.no_fill_penalty_pnl_cents > 0.0
        and row.last_window_pnl_cents > 0.0
    )


def _balance_penalty(row: RV600VariantSummaryRow) -> float:
    concentration_penalty = max(0.0, row.max_single_market_pnl_share - 0.25) * max(row.selected_pnl_cents, 0.0)
    market_penalty = max(0.0, 0.60 - row.positive_market_rate) * 250.0
    root_penalty = max(0.0, 0.60 - row.positive_root_rate) * 150.0
    entry_penalty = max(0, 25 - row.accepted_entries) * 10.0
    return concentration_penalty + market_penalty + root_penalty + entry_penalty


def _selector_key(row: RV600VariantSummaryRow) -> tuple[bool, bool, float, float, float, float]:
    return (
        _is_core_positive(row),
        row.accounting_mode == "position_capped",
        row.selected_pnl_cents - _balance_penalty(row),
        row.positive_market_rate,
        -row.max_single_market_pnl_share,
        row.matched_v28_delta_cents,
    )


def _choose_market_balanced(rows: list[RV600VariantSummaryRow]) -> RV600VariantSummaryRow | None:
    candidates = [
        row
        for row in rows
        if row.gate_count <= 4
        and row.accounting_mode in {"position_capped", "all_entries", "one_per_side_per_market"}
        and row.selected_pnl_cents > 0.0
    ]
    if not candidates:
        return None
    return max(candidates, key=_selector_key)


def _row_payload(row: RV600VariantSummaryRow | RV600VariantRunRow | None) -> dict[str, Any]:
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


def _summary_counts(rows: list[RV600VariantSummaryRow]) -> dict[str, int]:
    return {
        "summary_rows": len(rows),
        "gate_pass_rows": sum(1 for row in rows if not row.rejection_reason),
        "positive_concentration_ok_rows": sum(
            1 for row in rows if row.selected_pnl_cents > 0.0 and row.max_single_market_pnl_share <= 0.25
        ),
        "positive_market_rate_ok_rows": sum(
            1 for row in rows if row.selected_pnl_cents > 0.0 and row.positive_market_rate >= 0.60
        ),
        "positive_both_balance_ok_rows": sum(
            1
            for row in rows
            if row.selected_pnl_cents > 0.0
            and row.max_single_market_pnl_share <= 0.25
            and row.positive_market_rate >= 0.60
        ),
        "entry_delta_concentration_ok_rows": sum(
            1
            for row in rows
            if row.accepted_entries >= 25
            and row.selected_pnl_cents > 0.0
            and row.matched_v28_delta_cents > 0.0
            and row.max_single_market_pnl_share <= 0.25
        ),
    }


def _prequential_probe(
    run_rows: tuple[RV600VariantRunRow, ...],
    root_names: tuple[str, ...],
    *,
    min_train_roots: int,
) -> dict[str, Any]:
    selections: list[dict[str, Any]] = []
    test_rows: list[RV600VariantRunRow] = []
    for split_idx in range(min_train_roots, len(root_names)):
        train_roots = set(root_names[:split_idx])
        test_root = root_names[split_idx]
        train_summary = list(_summarize([row for row in run_rows if row.root_name in train_roots]))
        selected = _choose_market_balanced(train_summary)
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
                "selected": _row_payload(selected),
                "test": _row_payload(test_row),
            }
        )
    total_pnl = sum(row.selected_pnl_cents for row in test_rows)
    total_v28_delta = sum(row.matched_v28_delta_cents for row in test_rows)
    total_entries = sum(row.accepted_entries for row in test_rows)
    positive_roots = sum(1 for row in test_rows if row.selected_pnl_cents > 0.0)
    return {
        "min_train_roots": min_train_roots,
        "split_count": len(selections),
        "selection_count": sum(1 for row in selections if row["selected"]),
        "test_entry_count": total_entries,
        "test_selected_pnl_cents": total_pnl,
        "test_matched_v28_delta_cents": total_v28_delta,
        "positive_test_root_rate": (positive_roots / len(test_rows) if test_rows else 0.0),
        "prequential_gate_pass": (
            bool(test_rows)
            and total_entries >= 25
            and total_pnl > 0.0
            and total_v28_delta > 0.0
            and positive_roots / len(test_rows) >= 0.60
        ),
        "selections": selections,
    }


def build_report(args: argparse.Namespace) -> dict[str, Any]:
    roots = tuple(args.root or discover_roots(args.base_dir, args.reports_dir, args.min_root_name))
    variation_report = build_rv600_variation_report(
        roots,
        phase="grid",
        config=ReplayConfig(min_fill_prob=0.0, counterfactual_fill_threshold=0.5),
        min_decision_ts_utc=_load_dt(args.min_decision_ts_utc) if args.min_decision_ts_utc else None,
    )
    summary_rows = list(variation_report.summary_rows)
    best_total = summary_rows[0] if summary_rows else None
    balanced_rows = [
        row
        for row in summary_rows
        if row.selected_pnl_cents > 0.0
        and row.accepted_entries >= 25
        and row.matched_v28_delta_cents > 0.0
    ]
    best_balanced = max(balanced_rows, key=_selector_key) if balanced_rows else None
    concentration_ok = [
        row
        for row in summary_rows
        if row.selected_pnl_cents > 0.0 and row.max_single_market_pnl_share <= 0.25
    ]
    market_rate_ok = [
        row
        for row in summary_rows
        if row.selected_pnl_cents > 0.0 and row.positive_market_rate >= 0.60
    ]
    prequential = _prequential_probe(
        variation_report.run_rows,
        variation_report.roots,
        min_train_roots=args.min_train_roots,
    )
    decision = (
        "market_balance_rescue_pass"
        if best_balanced is not None
        and not best_balanced.rejection_reason
        and prequential.get("prequential_gate_pass") is True
        else "market_balance_rescue_failed"
    )
    return {
        "schema_version": "rv600-market-balance-rescue-v1",
        "generated_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "research_only": True,
        "decision": decision,
        "modeling_choice": (
            "Use existing RV600 grid variants only, rank them with a concentration- and market-stability-aware "
            "utility, and verify with anchored forward splits. This implements diversification/position-limit "
            "ideas without changing live logic or introducing a new broad model family."
        ),
        "sources": list(SOURCES),
        "roots": [root.name for root in roots],
        "counts": _summary_counts(summary_rows),
        "best_total_pnl_row": _row_payload(best_total),
        "best_market_balanced_row": _row_payload(best_balanced),
        "best_concentration_ok_positive_row": _row_payload(
            max(concentration_ok, key=lambda row: row.selected_pnl_cents) if concentration_ok else None
        ),
        "best_market_rate_ok_positive_row": _row_payload(
            max(market_rate_ok, key=lambda row: row.selected_pnl_cents) if market_rate_ok else None
        ),
        "prequential": prequential,
        "interpretation": _interpretation(decision, best_balanced, prequential),
    }


def _interpretation(
    decision: str,
    best_balanced: RV600VariantSummaryRow | None,
    prequential: dict[str, Any],
) -> str:
    if decision == "market_balance_rescue_pass":
        return (
            "A market-balanced existing RV600 variant cleared cumulative gates and anchored forward checks. "
            "Run the full objective audit before any completion decision."
        )
    if best_balanced is None:
        return "No existing RV600 grid row has enough entries, positive PnL, and positive matched-v28 delta."
    return (
        "The best market-balanced existing row is still gate-rejected, and anchored forward selection is "
        f"not sufficient for completion: prequential_gate_pass={prequential.get('prequential_gate_pass')}."
    )


def _markdown(report: dict[str, Any]) -> str:
    lines = [
        "# RV600 Market-Balance Rescue",
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
        ]
    )
    for key, value in report["counts"].items():
        lines.append(f"- {key}: {value}")
    for title, key in (
        ("Best Total PnL Row", "best_total_pnl_row"),
        ("Best Market-Balanced Row", "best_market_balanced_row"),
        ("Best Concentration-OK Positive Row", "best_concentration_ok_positive_row"),
        ("Best Market-Rate-OK Positive Row", "best_market_rate_ok_positive_row"),
    ):
        lines.extend(["", f"## {title}", ""])
        row = report.get(key) or {}
        if not row:
            lines.append("none")
        else:
            for row_key, value in row.items():
                lines.append(f"- {row_key}: `{value}`")
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
            f"- prequential_gate_pass: {pre['prequential_gate_pass']}",
            "",
            "## Interpretation",
            "",
            report["interpretation"],
            "",
        ]
    )
    return "\n".join(lines)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Market-balance rescue audit for cumulative RV600 bounded roots.")
    parser.add_argument("--root", action="append", type=Path, default=[])
    parser.add_argument("--base-dir", type=Path, default=DEFAULT_BASE_DIR)
    parser.add_argument("--reports-dir", type=Path, default=DEFAULT_REPORTS_DIR)
    parser.add_argument("--min-root-name", default=DEFAULT_MIN_ROOT_NAME)
    parser.add_argument("--min-decision-ts-utc", default=DEFAULT_MIN_DECISION_TS_UTC)
    parser.add_argument("--min-train-roots", type=int, default=3)
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
    print(f"root_count={len(report['roots'])}")
    print(f"gate_pass_rows={report['counts']['gate_pass_rows']}")
    print(f"positive_concentration_ok_rows={report['counts']['positive_concentration_ok_rows']}")
    print(f"positive_both_balance_ok_rows={report['counts']['positive_both_balance_ok_rows']}")
    print(f"prequential_gate_pass={report['prequential']['prequential_gate_pass']}")
    print(f"prequential_test_pnl_cents={report['prequential']['test_selected_pnl_cents']:.4f}")
    if args.write:
        print(f"output_json={args.output_json}")
        print(f"output_md={args.output_md}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
