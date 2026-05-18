from __future__ import annotations

import argparse
import json
import math
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Sequence

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
DEFAULT_OUTPUT_JSON = Path("logs/particle_research/reports/rv600_group_dro_rescue_latest.json")
DEFAULT_OUTPUT_MD = Path("logs/particle_research/reports/rv600_group_dro_rescue_latest.md")


SOURCES = (
    {
        "name": "Group DRO for worst-group generalization",
        "url": "https://arxiv.org/abs/1911.08731",
        "use": "Motivates optimizing against weak groups instead of average performance only.",
    },
    {
        "name": "Cardinality-constrained distributionally robust portfolio optimization",
        "url": "https://arxiv.org/abs/2112.12454",
        "use": "Motivates combining robust objectives with limits on selected positions.",
    },
    {
        "name": "Cardinality-constrained mean/CVaR portfolio optimization",
        "url": "https://arxiv.org/abs/1810.10563",
        "use": "Motivates lower-tail risk control and cardinality constraints under costs.",
    },
    {
        "name": "Online lazy portfolio updates with transaction costs",
        "url": "https://ojs.aaai.org/index.php/AAAI/article/view/8693",
        "use": "Motivates avoiding churn unless an update is worth transaction costs.",
    },
    {
        "name": "Backtest overfitting in the machine learning era",
        "url": "https://www.sciencedirect.com/science/article/abs/pii/S0950705124011110",
        "use": "Motivates anchored, purged-style validation and false-discovery skepticism.",
    },
)


def _parse_dt(value: str) -> datetime:
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


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
            "matched_v28_control_pnl_cents",
            "matched_v28_delta_cents",
            "avg_pnl_per_entry_cents",
            "avg_pnl_per_market_cents",
            "positive_root_rate",
            "positive_market_rate",
            "max_single_market_pnl_share",
            "last_window_pnl_cents",
            "added_entry_count",
            "added_entry_pnl_cents",
            "avg_added_entry_pnl_cents",
            "worst_market_pnl_cents",
            "no_fill_penalty_pnl_cents",
            "rejection_reason",
        )
        if key in payload
    }


def _rows_by_key(rows: Sequence[RV600VariantRunRow]) -> dict[tuple[str, str], list[RV600VariantRunRow]]:
    grouped: dict[tuple[str, str], list[RV600VariantRunRow]] = {}
    for row in rows:
        grouped.setdefault((row.variant, row.accounting_mode), []).append(row)
    return grouped


def _root_pnls(row: RV600VariantSummaryRow, grouped: dict[tuple[str, str], list[RV600VariantRunRow]]) -> list[float]:
    return [item.selected_pnl_cents for item in grouped.get((row.variant, row.accounting_mode), [])]


def _downside_deviation(values: Sequence[float]) -> float:
    if not values:
        return 0.0
    losses = [min(0.0, value) for value in values]
    return math.sqrt(sum(value * value for value in losses) / len(losses))


def _lower_tail_mean(values: Sequence[float]) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    count = max(1, math.ceil(0.25 * len(ordered)))
    return sum(ordered[:count]) / count


def _single_market_gate_ok(row: RV600VariantSummaryRow) -> bool:
    if row.matched_v28_control_pnl_cents > 0.0:
        beats_control = row.selected_pnl_cents >= 1.20 * row.matched_v28_control_pnl_cents
    else:
        beats_control = row.matched_v28_delta_cents > 0.0
    return (
        row.accounting_mode == "position_capped"
        and row.gate_count <= 3
        and row.accepted_entries >= 25
        and row.distinct_markets >= 10
        and row.selected_pnl_cents > 0.0
        and beats_control
        and row.avg_pnl_per_entry_cents >= 10.0
        and row.avg_pnl_per_market_cents > 0.0
        and row.positive_root_rate >= 0.60
        and row.positive_market_rate >= 0.60
        and row.max_single_market_pnl_share <= 0.25
        and row.last_window_pnl_cents > 0.0
        and row.no_fill_penalty_pnl_cents > 0.0
        and (row.added_entry_count == 0 or row.added_entry_pnl_cents > 0.0)
    )


def _robust_metrics(
    row: RV600VariantSummaryRow,
    grouped: dict[tuple[str, str], list[RV600VariantRunRow]],
) -> dict[str, float | bool]:
    pnls = _root_pnls(row, grouped)
    lower_tail = _lower_tail_mean(pnls)
    downside = _downside_deviation(pnls)
    worst_root = min(pnls) if pnls else 0.0
    concentration_penalty = max(0.0, row.max_single_market_pnl_share - 0.25) * max(row.selected_pnl_cents, 0.0)
    market_penalty = max(0.0, 0.60 - row.positive_market_rate) * 250.0
    root_penalty = max(0.0, 0.60 - row.positive_root_rate) * 150.0
    recent_penalty = max(0.0, -row.last_window_pnl_cents)
    churn_penalty = max(0, row.accepted_entries - max(row.distinct_markets * 3, row.distinct_markets)) * 1.0
    robust_score = (
        lower_tail
        + 0.15 * row.selected_pnl_cents
        + 0.05 * row.matched_v28_delta_cents
        - downside
        - concentration_penalty
        - market_penalty
        - root_penalty
        - recent_penalty
        - churn_penalty
    )
    return {
        "group_dro_support": _single_market_gate_ok(row) and lower_tail > 0.0 and worst_root > -100.0,
        "lower_tail_root_pnl_cents": lower_tail,
        "worst_root_pnl_cents": worst_root,
        "downside_deviation_cents": downside,
        "robust_score": robust_score,
        "concentration_penalty": concentration_penalty,
        "market_penalty": market_penalty,
        "root_penalty": root_penalty,
        "recent_penalty": recent_penalty,
        "churn_penalty": churn_penalty,
    }


def _selector_key(
    row: RV600VariantSummaryRow,
    grouped: dict[tuple[str, str], list[RV600VariantRunRow]],
) -> tuple[bool, float, float, float, float, float, float]:
    metrics = _robust_metrics(row, grouped)
    return (
        bool(metrics["group_dro_support"]),
        float(metrics["robust_score"]),
        float(metrics["lower_tail_root_pnl_cents"]),
        row.positive_market_rate,
        row.positive_root_rate,
        -row.max_single_market_pnl_share,
        row.matched_v28_delta_cents,
    )


def _choose_group_dro_row(
    rows: Sequence[RV600VariantSummaryRow],
    grouped: dict[tuple[str, str], list[RV600VariantRunRow]],
) -> RV600VariantSummaryRow | None:
    candidates = [
        row
        for row in rows
        if row.accounting_mode == "position_capped"
        and row.gate_count <= 3
        and row.accepted_entries >= 10
        and row.selected_pnl_cents > 0.0
        and row.matched_v28_delta_cents > 0.0
    ]
    return max(candidates, key=lambda row: _selector_key(row, grouped)) if candidates else None


def _prequential_probe(
    run_rows: Sequence[RV600VariantRunRow],
    root_names: Sequence[str],
    min_train_roots: int,
) -> dict[str, Any]:
    selections: list[dict[str, Any]] = []
    test_rows: list[RV600VariantRunRow] = []
    for split_idx in range(min_train_roots, len(root_names)):
        train_roots = set(root_names[:split_idx])
        test_root = root_names[split_idx]
        train_run_rows = [row for row in run_rows if row.root_name in train_roots]
        train_summary = _summarize(train_run_rows)
        train_grouped = _rows_by_key(train_run_rows)
        selected = _choose_group_dro_row(train_summary, train_grouped)
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
    total_markets = sum(row.distinct_markets for row in test_rows)
    positive_roots = sum(1 for row in test_rows if row.selected_pnl_cents > 0.0)
    positive_rate = positive_roots / len(test_rows) if test_rows else 0.0
    max_contribution = max(
        (
            row.max_single_market_pnl_share * row.selected_pnl_cents
            if row.selected_pnl_cents > 0.0
            else 0.0
        )
        for row in test_rows
    ) if test_rows else 0.0
    max_share = max_contribution / total_pnl if total_pnl > 0.0 else 0.0
    lower_tail = _lower_tail_mean([row.selected_pnl_cents for row in test_rows])
    return {
        "min_train_roots": min_train_roots,
        "split_count": len(selections),
        "selection_count": sum(1 for item in selections if item["selected"]),
        "test_entry_count": total_entries,
        "test_distinct_markets": total_markets,
        "test_selected_pnl_cents": total_pnl,
        "test_matched_v28_delta_cents": total_delta,
        "positive_test_root_rate": positive_rate,
        "max_single_market_pnl_share": max_share,
        "lower_tail_test_root_pnl_cents": lower_tail,
        "prequential_gate_pass": (
            len(test_rows) > 0
            and total_entries >= 25
            and total_pnl > 0.0
            and total_delta > 0.0
            and positive_rate >= 0.60
            and max_share <= 0.25
            and lower_tail > 0.0
        ),
        "selections": selections,
    }


def _row_with_metrics(
    row: RV600VariantSummaryRow | None,
    grouped: dict[tuple[str, str], list[RV600VariantRunRow]],
) -> dict[str, Any]:
    if row is None:
        return {}
    return {**_compact_row(row), **_robust_metrics(row, grouped)}


def build_report(args: argparse.Namespace) -> dict[str, Any]:
    roots = tuple(args.root or discover_roots(args.base_dir, args.reports_dir, args.min_root_name))
    variation_report = build_rv600_variation_report(
        roots,
        phase="grid",
        config=ReplayConfig(min_fill_prob=0.0, counterfactual_fill_threshold=0.5),
        min_decision_ts_utc=_parse_dt(args.min_decision_ts_utc) if args.min_decision_ts_utc else None,
    )
    run_rows = list(variation_report.run_rows)
    summary_rows = list(variation_report.summary_rows)
    grouped = _rows_by_key(run_rows)
    positive_position_rows = [
        row
        for row in summary_rows
        if row.accounting_mode == "position_capped"
        and row.selected_pnl_cents > 0.0
        and row.matched_v28_delta_cents > 0.0
    ]
    top_rows = sorted(positive_position_rows, key=lambda row: _selector_key(row, grouped), reverse=True)[:12]
    support_rows = [row for row in positive_position_rows if _robust_metrics(row, grouped)["group_dro_support"]]
    best_row = top_rows[0] if top_rows else None
    prequential = _prequential_probe(run_rows, variation_report.roots, args.min_train_roots)
    decision = (
        "group_dro_rescue_pass"
        if support_rows and prequential.get("prequential_gate_pass") is True
        else "group_dro_rescue_failed"
    )
    return {
        "schema_version": "rv600-group-dro-rescue-v1",
        "generated_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "research_only": True,
        "decision": decision,
        "modeling_choice": (
            "Evaluate existing RV600 grid variants with a group-DRO/minimax utility over bounded roots, "
            "using root lower-tail PnL, market concentration, recent-window PnL, and transaction-churn penalties. "
            "This is a selection/abstention audit only; it does not add a new live model or touch v28 logic."
        ),
        "solutions_considered": [
            {
                "solution": "Total-PnL re-ranking",
                "decision": "rejected",
                "reason": "Already failed by concentrating profit in too few roots/markets.",
            },
            {
                "solution": "Group-DRO/minimax root and market robustness",
                "decision": "selected",
                "reason": "Directly targets the observed worst-root and market-concentration failure.",
            },
            {
                "solution": "Cardinality/CVaR position selection",
                "decision": "included_as_penalties",
                "reason": "Mapped to position_capped accounting, lower-tail root PnL, and churn penalties.",
            },
            {
                "solution": "Online lazy updates",
                "decision": "included_as_penalties",
                "reason": "Mapped to a repeated-entry churn penalty rather than a new trading model.",
            },
            {
                "solution": "CPCV/PBO/DSR-style validation",
                "decision": "included_as_gate",
                "reason": "Mapped to anchored forward splits and rejection unless out-of-sample groups pass.",
            },
        ],
        "sources": list(SOURCES),
        "roots": list(variation_report.roots),
        "summary_row_count": len(summary_rows),
        "positive_position_row_count": len(positive_position_rows),
        "support_row_count": len(support_rows),
        "best_row": _row_with_metrics(best_row, grouped),
        "support_rows": [_row_with_metrics(row, grouped) for row in support_rows[:20]],
        "top_rows": [_row_with_metrics(row, grouped) for row in top_rows],
        "prequential": prequential,
        "interpretation": _interpretation(decision, support_rows, prequential),
        "inputs": {
            "base_dir": str(args.base_dir),
            "reports_dir": str(args.reports_dir),
            "min_root_name": args.min_root_name,
            "min_decision_ts_utc": args.min_decision_ts_utc,
            "roots": [str(root) for root in args.root],
        },
    }


def _interpretation(
    decision: str,
    support_rows: Sequence[RV600VariantSummaryRow],
    prequential: dict[str, Any],
) -> str:
    if decision == "group_dro_rescue_pass":
        return (
            "A group-DRO-selected existing RV600 row cleared cumulative support gates and anchored forward "
            "validation. Run the full objective audit before any completion decision."
        )
    if not support_rows:
        return (
            "No existing RV600 row clears the group-DRO support gate. The rescue remains rejected unless fresh "
            f"bounded evidence changes the root/market lower-tail profile; anchored forward pass={prequential.get('prequential_gate_pass')}."
        )
    return (
        "A cumulative group-DRO support row exists, but anchored forward validation failed; treat it as "
        "sample-mined until fresh forward evidence clears the gates."
    )


def _fmt(value: Any) -> str:
    if isinstance(value, float):
        return f"{value:.4f}"
    return str(value)


def _markdown(report: dict[str, Any]) -> str:
    pre = report["prequential"]
    lines = [
        "# RV600 Group-DRO Rescue",
        "",
        f"- generated_utc: {report['generated_utc']}",
        f"- research_only: {report['research_only']}",
        f"- decision: {report['decision']}",
        f"- modeling_choice: {report['modeling_choice']}",
        "",
        "## Solutions Considered",
        "",
    ]
    for item in report["solutions_considered"]:
        lines.append(f"- {item['solution']}: {item['decision']} - {item['reason']}")
    lines.extend(["", "## Sources Considered", ""])
    for source in report["sources"]:
        lines.append(f"- {source['name']}: {source['url']} - {source['use']}")
    lines.extend(
        [
            "",
            "## Counts",
            "",
            f"- roots: {len(report['roots'])}",
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
            lines.append(f"- {key}: `{_fmt(value)}`")
    else:
        lines.append("none")
    lines.extend(
        [
            "",
            "## Anchored Forward Probe",
            "",
            f"- split_count: {pre['split_count']}",
            f"- selection_count: {pre['selection_count']}",
            f"- test_entry_count: {pre['test_entry_count']}",
            f"- test_distinct_markets: {pre['test_distinct_markets']}",
            f"- test_selected_pnl_cents: {pre['test_selected_pnl_cents']}",
            f"- test_matched_v28_delta_cents: {pre['test_matched_v28_delta_cents']}",
            f"- positive_test_root_rate: {pre['positive_test_root_rate']}",
            f"- max_single_market_pnl_share: {pre['max_single_market_pnl_share']}",
            f"- lower_tail_test_root_pnl_cents: {pre['lower_tail_test_root_pnl_cents']}",
            f"- prequential_gate_pass: {pre['prequential_gate_pass']}",
            "",
            "## Top Rows",
            "",
            "| variant | accounting | gates | entries | pnl | v28 delta | lower-tail | worst root | score | pos roots | pos markets | max share | rejection |",
            "|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|",
        ]
    )
    for row in report["top_rows"]:
        lines.append(
            "| `{variant}` | {accounting_mode} | {gate_count} | {accepted_entries} | {selected_pnl_cents:.1f} | {matched_v28_delta_cents:.1f} | {lower_tail_root_pnl_cents:.1f} | {worst_root_pnl_cents:.1f} | {robust_score:.1f} | {positive_root_rate:.2f} | {positive_market_rate:.2f} | {max_single_market_pnl_share:.2f} | `{rejection_reason}` |".format(
                **row
            )
        )
    lines.extend(["", "## Interpretation", "", report["interpretation"], ""])
    return "\n".join(lines)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Group-DRO rescue audit for cumulative RV600 bounded roots.")
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
    print(f"roots={len(report['roots'])}")
    print(f"support_row_count={report['support_row_count']}")
    print(f"prequential_gate_pass={report['prequential']['prequential_gate_pass']}")
    print(f"prequential_test_pnl_cents={report['prequential']['test_selected_pnl_cents']:.4f}")
    if args.write:
        print(f"output_json={args.output_json}")
        print(f"output_md={args.output_md}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
