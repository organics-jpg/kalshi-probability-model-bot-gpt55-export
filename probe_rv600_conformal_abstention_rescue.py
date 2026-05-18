from __future__ import annotations

import argparse
import json
import math
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from probe_rv600_probability_calibration_rescue import (
    AcceptedDecision,
    CandidateRow,
    StrategySpec,
    _aggregate_rejection,
    _clamp01,
    _expected_ev,
    _load_json,
    _load_root_rows,
    _one_per_side,
    _passes_entry_rule,
    _passes_gate,
    _position_capped,
    _realized_pnl,
    _rejection_reason,
    _score_decisions,
    _side_eval,
    _strategy_specs,
)


DEFAULT_NATIVE_JSON = Path("logs/particle_research/reports/rv600_native_forward_opportunity_latest.json")
DEFAULT_ROOT_BASE = Path("logs/particle_research/real_shadow")
DEFAULT_OUTPUT_JSON = Path("logs/particle_research/reports/rv600_conformal_abstention_rescue_latest.json")
DEFAULT_OUTPUT_MD = Path("logs/particle_research/reports/rv600_conformal_abstention_rescue_latest.md")

MODELING_OPTIONS = [
    {
        "method": "split_conformal_abstention",
        "source": "Xu and Xie 2020/2023, Conformal prediction for time series",
        "source_url": "https://arxiv.org/abs/2010.09107",
        "fit": "Use prior-root residual quantiles as a conservative RV600 probability error band before accepting EV.",
        "decision": "chosen",
    },
    {
        "method": "sequential_conformal_inference",
        "source": "Xu and Xie 2022, Sequential Predictive Conformal Inference for Time Series",
        "source_url": "https://arxiv.org/abs/2212.03463",
        "fit": "More adaptive, but heavier than needed for a first rescue and needs more stable residual history.",
        "decision": "deferred",
    },
    {
        "method": "meta_label_filter",
        "source": "Joubert 2022, Meta-Labeling: Theory and Framework",
        "source_url": "https://ssrn.com/abstract=4032018",
        "fit": "Already tested; failed prequential gates on the current RV600 sample.",
        "decision": "previously_rejected",
    },
]


@dataclass(frozen=True)
class ConformalFit:
    name: str
    coverage: float
    q_abs_error: float


def _fit_conformal(train_rows: list[CandidateRow]) -> list[ConformalFit]:
    market_rows: dict[str, CandidateRow] = {}
    for row in train_rows:
        market_rows.setdefault(row.market_ticker, row)
    errors = sorted(abs((1.0 if row.result == "yes" else 0.0) - row.rv600_p_yes) for row in market_rows.values())
    if not errors:
        return []
    fits: list[ConformalFit] = []
    for coverage in (0.60, 0.70, 0.80, 0.90):
        index = min(len(errors) - 1, max(0, math.ceil(coverage * (len(errors) + 1)) - 1))
        fits.append(ConformalFit(f"conformal_q{int(coverage * 100)}", coverage, errors[index]))
    return fits


def _accepted_decisions(rows: list[CandidateRow], fit: ConformalFit, spec: StrategySpec) -> list[AcceptedDecision]:
    accepted: list[AcceptedDecision] = []
    state: dict[str, list[AcceptedDecision]] = defaultdict(list)
    for row in sorted(rows, key=lambda item: (item.decision_ts_utc, item.market_ticker)):
        if not spec.min_seconds_to_close <= row.seconds_to_close <= spec.max_seconds_to_close:
            continue
        side, robust_ev, ask, fill_prob = _robust_side_eval(row, fit.q_abs_error)
        if robust_ev < spec.min_ev_cents:
            continue
        previous = state[row.market_ticker]
        if not _passes_entry_rule(previous, side, robust_ev, ask, row.decision_ts_utc, spec):
            continue
        matched_side, matched_ev, matched_ask, matched_fill = _side_eval(row, row.current_p_yes)
        pnl = _realized_pnl(row, side, ask, fill_prob)
        matched_pnl = _realized_pnl(row, matched_side, matched_ask, matched_fill)
        decision = AcceptedDecision(
            root_name=row.root_name,
            market_ticker=row.market_ticker,
            decision_ts_utc=row.decision_ts_utc,
            side=side,
            ask_cents=ask,
            risk_cents=ask,
            selected_ev_cents=robust_ev,
            matched_v28_ev_cents=matched_ev,
            pnl_cents=pnl,
            matched_v28_pnl_cents=matched_pnl,
            is_added_entry=bool(previous),
        )
        previous.append(decision)
        accepted.append(decision)
    return accepted


def _robust_side_eval(row: CandidateRow, q_abs_error: float) -> tuple[str, float, float, float]:
    lo = _clamp01(row.rv600_p_yes - q_abs_error)
    hi = _clamp01(row.rv600_p_yes + q_abs_error)
    ev_yes = _expected_ev(lo, row.yes_ask_cents, row.fee_cents, row.yes_fill_prob)
    ev_no = _expected_ev(1.0 - hi, row.no_ask_cents, row.fee_cents, row.no_fill_prob)
    if ev_yes >= ev_no:
        return "yes", ev_yes, row.yes_ask_cents, row.yes_fill_prob
    return "no", ev_no, row.no_ask_cents, row.no_fill_prob


def _score(rows_by_root: dict[str, list[CandidateRow]], roots: list[str], fit: ConformalFit, spec: StrategySpec) -> dict[str, Any]:
    capped_entries: list[AcceptedDecision] = []
    root_rows: list[dict[str, Any]] = []
    for root in roots:
        accepted = _accepted_decisions(rows_by_root.get(root, []), fit, spec)
        capped = _position_capped(accepted, spec.declared_position_cap_cents)
        capped_entries.extend(capped)
        root_rows.append(
            {
                "root": root,
                "accepted_entries": len(capped),
                "distinct_markets": len({item.market_ticker for item in capped}),
                "selected_pnl_cents": sum(item.pnl_cents for item in capped),
                "matched_v28_control_pnl_cents": sum(item.matched_v28_pnl_cents for item in capped),
            }
        )
    all_entries = [item for root in roots for item in _accepted_decisions(rows_by_root.get(root, []), fit, spec)]
    mode_scores = {
        "all_entries": _score_decisions(all_entries),
        "one_per_side_per_market": _score_decisions(_one_per_side(capped_entries)),
        "position_capped": _score_decisions(capped_entries),
    }
    main = mode_scores["position_capped"]
    main.update(
        {
            "conformal": fit.name,
            "coverage": fit.coverage,
            "q_abs_error": fit.q_abs_error,
            "strategy": spec.name,
            "accounting_mode": "position_capped",
            "root_rows": root_rows,
            "accounting_modes": mode_scores,
            "train_gate_pass": _passes_gate(main, mode_scores, spec),
            "rejection_reason": _rejection_reason(main, mode_scores, spec),
        }
    )
    return main


def build_report(args: argparse.Namespace) -> dict[str, Any]:
    native = _load_json(args.native_json)
    roots = list(native.get("roots") or [])
    rows_by_root = {root: _load_root_rows(args.root_base, root) for root in roots}
    usable_roots = [root for root in roots if rows_by_root.get(root)]
    strategies = _strategy_specs()
    split_rows: list[dict[str, Any]] = []
    for test_index in range(args.min_train_roots, len(usable_roots)):
        train_roots = usable_roots[:test_index]
        test_root = usable_roots[test_index]
        train_rows = [row for root in train_roots for row in rows_by_root[root]]
        fits = _fit_conformal(train_rows)
        if not fits:
            continue
        train_scores = [_score(rows_by_root, train_roots, fit, spec) for fit in fits for spec in strategies]
        passing = [score for score in train_scores if score["train_gate_pass"]]
        if passing:
            selected = max(passing, key=lambda item: item["selected_pnl_cents"])
            selection_basis = "train_gate_pass"
        else:
            selected = max(train_scores, key=lambda item: item["selected_pnl_cents"])
            selection_basis = "diagnostic_best_train_pnl"
        selected_fit = next(item for item in fits if item.name == selected["conformal"])
        selected_spec = next(item for item in strategies if item.name == selected["strategy"])
        test_score = _score(rows_by_root, [test_root], selected_fit, selected_spec)
        split_rows.append(
            {
                "split_index": len(split_rows),
                "train_root_count": len(train_roots),
                "test_root": test_root,
                "selected_conformal": selected["conformal"],
                "selected_strategy": selected["strategy"],
                "selection_basis": selection_basis,
                "train_gate_pass": bool(passing),
                "train_selected_pnl_cents": selected["selected_pnl_cents"],
                "train_accepted_entries": selected["accepted_entries"],
                "train_distinct_markets": selected["distinct_markets"],
                "train_q_abs_error": selected["q_abs_error"],
                "train_rejection_reason": selected["rejection_reason"],
                "test_selected_pnl_cents": test_score["selected_pnl_cents"],
                "test_matched_v28_control_pnl_cents": test_score["matched_v28_control_pnl_cents"],
                "test_matched_v28_delta_cents": test_score["matched_v28_delta_cents"],
                "test_accepted_entries": test_score["accepted_entries"],
                "test_distinct_markets": test_score["distinct_markets"],
                "test_avg_pnl_per_entry_cents": test_score["avg_pnl_per_entry_cents"],
                "test_rejection_reason": test_score["rejection_reason"],
            }
        )
    total_entries = sum(row["test_accepted_entries"] for row in split_rows)
    total_pnl = sum(row["test_selected_pnl_cents"] for row in split_rows)
    total_matched = sum(row["test_matched_v28_control_pnl_cents"] for row in split_rows)
    locked_selection_count = sum(1 for row in split_rows if row["selection_basis"] == "train_gate_pass")
    positive_splits = sum(1 for row in split_rows if row["test_selected_pnl_cents"] > 0.0)
    gate_pass = (
        locked_selection_count > 0
        and total_entries >= 25
        and total_pnl > 0.0
        and total_pnl - total_matched > 0.0
        and (total_pnl / total_entries if total_entries else 0.0) >= 10.0
        and (positive_splits / len(split_rows) if split_rows else 0.0) >= 0.60
    )
    return {
        "schema_version": "rv600-conformal-abstention-rescue-v1",
        "generated_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "research_only": True,
        "method_choice": "Conformal abstention over RV600 probability using prior-root residual quantiles.",
        "modeling_options": MODELING_OPTIONS,
        "roots": usable_roots,
        "min_train_roots": args.min_train_roots,
        "strategy_count": len(strategies),
        "split_rows": split_rows,
        "aggregate": {
            "split_count": len(split_rows),
            "train_gate_selection_count": locked_selection_count,
            "diagnostic_selection_count": len(split_rows) - locked_selection_count,
            "test_total_entries": total_entries,
            "test_selected_pnl_cents": total_pnl,
            "test_matched_v28_control_pnl_cents": total_matched,
            "test_matched_v28_delta_cents": total_pnl - total_matched,
            "test_avg_pnl_per_entry_cents": total_pnl / total_entries if total_entries else 0.0,
            "positive_test_split_rate": positive_splits / len(split_rows) if split_rows else 0.0,
            "preliminary_gate_pass": gate_pass,
            "rejection_reason": _aggregate_rejection(gate_pass, locked_selection_count, total_entries, total_pnl, total_matched, positive_splits, len(split_rows)),
        },
        "inputs": {
            "native_json": str(args.native_json),
            "root_base": str(args.root_base),
        },
    }


def _markdown(report: dict[str, Any]) -> str:
    aggregate = report["aggregate"]
    lines = [
        "# RV600 Conformal Abstention Rescue Probe",
        "",
        f"- generated_utc: {report['generated_utc']}",
        f"- research_only: {report['research_only']}",
        f"- method_choice: {report['method_choice']}",
        f"- usable_roots: {len(report['roots'])}",
        f"- strategy_count: {report['strategy_count']}",
        f"- split_count: {aggregate['split_count']}",
        f"- train_gate_selection_count: {aggregate['train_gate_selection_count']}",
        f"- diagnostic_selection_count: {aggregate['diagnostic_selection_count']}",
        f"- test_total_entries: {aggregate['test_total_entries']}",
        f"- test_selected_pnl_cents: {aggregate['test_selected_pnl_cents']:.1f}",
        f"- test_matched_v28_delta_cents: {aggregate['test_matched_v28_delta_cents']:.1f}",
        f"- preliminary_gate_pass: {aggregate['preliminary_gate_pass']}",
        f"- rejection_reason: {aggregate['rejection_reason']}",
        "",
        "## Modeling Choice",
        "",
        "| method | decision | source | fit |",
        "|---|---|---|---|",
    ]
    for option in report["modeling_options"]:
        lines.append(
            f"| `{option['method']}` | {option['decision']} | [{option['source']}]({option['source_url']}) | {option['fit']} |"
        )
    lines.extend(
        [
            "",
            "## Split Rows",
            "",
            "| split | selected conformal | selected strategy | basis | test root | entries | pnl_c | v28_delta_c |",
            "|---:|---|---|---|---|---:|---:|---:|",
        ]
    )
    for row in report["split_rows"]:
        lines.append(
            "| {split_index} | `{selected_conformal}` | `{selected_strategy}` | {selection_basis} | `{test_root}` | {test_accepted_entries} | {test_selected_pnl_cents:.1f} | {test_matched_v28_delta_cents:.1f} |".format(
                **row
            )
        )
    lines.extend(
        [
            "",
            "## Method Notes",
            "",
            "This is a research-only abstention check: the prior-root absolute RV600 label error sets a probability band, and trades are accepted only if worst-case EV still clears the strategy threshold.",
            "Diagnostic selections are not promotable unless the prior-root window already passed anti-overfitting gates.",
            "",
        ]
    )
    return "\n".join(lines)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Research-only RV600 conformal abstention rescue probe.")
    parser.add_argument("--native-json", type=Path, default=DEFAULT_NATIVE_JSON)
    parser.add_argument("--root-base", type=Path, default=DEFAULT_ROOT_BASE)
    parser.add_argument("--output-json", type=Path, default=DEFAULT_OUTPUT_JSON)
    parser.add_argument("--output-md", type=Path, default=DEFAULT_OUTPUT_MD)
    parser.add_argument("--min-train-roots", type=int, default=5)
    parser.add_argument("--write", action="store_true")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    report = build_report(args)
    markdown = _markdown(report)
    if args.write:
        args.output_json.parent.mkdir(parents=True, exist_ok=True)
        args.output_json.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        args.output_md.write_text(markdown, encoding="utf-8")
    aggregate = report["aggregate"]
    print(f"preliminary_gate_pass={aggregate['preliminary_gate_pass']}")
    print(f"split_count={aggregate['split_count']}")
    print(f"train_gate_selection_count={aggregate['train_gate_selection_count']}")
    print(f"test_selected_pnl_cents={aggregate['test_selected_pnl_cents']:.1f}")
    print(f"rejection_reason={aggregate['rejection_reason']}")
    print(f"output_json={args.output_json}")
    print(f"output_md={args.output_md}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
