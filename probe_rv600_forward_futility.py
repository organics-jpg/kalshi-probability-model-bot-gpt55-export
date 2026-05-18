from __future__ import annotations

import argparse
import json
import random
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


DEFAULT_FORWARD_JSON = Path("logs/particle_research/reports/rv600_variation_forward_latest.json")
DEFAULT_NATIVE_JSON = Path("logs/particle_research/reports/rv600_native_forward_opportunity_latest.json")
DEFAULT_PREQUENTIAL_JSON = Path("logs/particle_research/reports/rv600_prequential_selection_latest.json")
DEFAULT_AUDIT_JSON = Path("logs/particle_research/reports/rv600_goal_completion_audit_latest.json")
DEFAULT_OUTPUT_JSON = Path("logs/particle_research/reports/rv600_forward_futility_latest.json")
DEFAULT_OUTPUT_MD = Path("logs/particle_research/reports/rv600_forward_futility_latest.md")


@dataclass(frozen=True)
class RecoveryMath:
    current_entries: int
    current_markets: int
    current_pnl_cents: float
    current_avg_pnl_per_entry_cents: float
    target_entries: int
    target_markets: int
    target_total_pnl_cents: float
    remaining_entries_to_target: int
    remaining_markets_to_target: int
    required_remaining_avg_pnl_per_entry_cents: float | None
    required_remaining_avg_to_positive_cents: float | None


@dataclass(frozen=True)
class BootstrapResult:
    iterations: int
    seed: int
    usable_root_blocks: int
    success_count: int
    success_probability: float
    median_final_pnl_cents: float
    p90_final_pnl_cents: float
    median_final_entries: float
    median_final_markets: float
    success_definition: str


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _int(value: Any, default: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def _best_forward_row(forward_report: dict[str, Any]) -> dict[str, Any]:
    rows = forward_report.get("summary_rows") or []
    if not rows:
        return {}
    return max(rows, key=lambda row: _float(row.get("selected_pnl_cents")))


def _matching_run_rows(forward_report: dict[str, Any], summary_row: dict[str, Any]) -> list[dict[str, Any]]:
    variant = summary_row.get("variant")
    accounting_mode = summary_row.get("accounting_mode")
    rows = forward_report.get("run_rows") or []
    return [
        row
        for row in rows
        if row.get("variant") == variant and row.get("accounting_mode") == accounting_mode
    ]


def _percentile(values: list[float], pct: float) -> float:
    if not values:
        return 0.0
    values = sorted(values)
    idx = min(len(values) - 1, max(0, round((len(values) - 1) * pct)))
    return values[idx]


def _recovery_math(
    row: dict[str, Any],
    *,
    target_entries: int,
    target_markets: int,
    target_avg_entry_cents: float,
) -> RecoveryMath:
    current_entries = _int(row.get("accepted_entries"))
    current_markets = _int(row.get("distinct_markets"))
    current_pnl = _float(row.get("selected_pnl_cents"))
    target_total = target_entries * target_avg_entry_cents
    remaining_entries = max(0, target_entries - current_entries)
    remaining_markets = max(0, target_markets - current_markets)
    required_to_target = None
    required_to_positive = None
    if remaining_entries > 0:
        required_to_target = (target_total - current_pnl) / remaining_entries
        required_to_positive = (0.0 - current_pnl) / remaining_entries
    return RecoveryMath(
        current_entries=current_entries,
        current_markets=current_markets,
        current_pnl_cents=current_pnl,
        current_avg_pnl_per_entry_cents=_float(row.get("avg_pnl_per_entry_cents")),
        target_entries=target_entries,
        target_markets=target_markets,
        target_total_pnl_cents=target_total,
        remaining_entries_to_target=remaining_entries,
        remaining_markets_to_target=remaining_markets,
        required_remaining_avg_pnl_per_entry_cents=required_to_target,
        required_remaining_avg_to_positive_cents=required_to_positive,
    )


def _bootstrap_predictive_probability(
    row: dict[str, Any],
    run_rows: list[dict[str, Any]],
    *,
    target_entries: int,
    target_markets: int,
    target_avg_entry_cents: float,
    iterations: int,
    seed: int,
) -> BootstrapResult:
    blocks = [
        {
            "entries": _int(root_row.get("accepted_entries")),
            "markets": _int(root_row.get("distinct_markets")),
            "pnl": _float(root_row.get("selected_pnl_cents")),
            "delta": _float(root_row.get("matched_v28_delta_cents")),
        }
        for root_row in run_rows
        if _int(root_row.get("accepted_entries")) > 0
    ]
    current_entries = _int(row.get("accepted_entries"))
    current_markets = _int(row.get("distinct_markets"))
    current_pnl = _float(row.get("selected_pnl_cents"))
    current_delta = _float(row.get("matched_v28_delta_cents"))
    target_total = target_entries * target_avg_entry_cents

    if not blocks or iterations <= 0:
        return BootstrapResult(
            iterations=0,
            seed=seed,
            usable_root_blocks=len(blocks),
            success_count=0,
            success_probability=0.0,
            median_final_pnl_cents=current_pnl,
            p90_final_pnl_cents=current_pnl,
            median_final_entries=float(current_entries),
            median_final_markets=float(current_markets),
            success_definition="no usable root blocks",
        )

    rng = random.Random(seed)
    success_count = 0
    final_pnls: list[float] = []
    final_entries: list[float] = []
    final_markets: list[float] = []
    for _ in range(iterations):
        entries = current_entries
        markets = current_markets
        pnl = current_pnl
        delta = current_delta
        guard = 0
        while entries < target_entries and guard < target_entries * 5:
            block = rng.choice(blocks)
            entries += block["entries"]
            markets += block["markets"]
            pnl += block["pnl"]
            delta += block["delta"]
            guard += 1
        final_pnls.append(pnl)
        final_entries.append(float(entries))
        final_markets.append(float(markets))
        if (
            entries >= target_entries
            and markets >= target_markets
            and pnl >= target_total
            and (pnl / entries) >= target_avg_entry_cents
            and delta > 0.0
        ):
            success_count += 1

    return BootstrapResult(
        iterations=iterations,
        seed=seed,
        usable_root_blocks=len(blocks),
        success_count=success_count,
        success_probability=success_count / iterations,
        median_final_pnl_cents=_percentile(final_pnls, 0.50),
        p90_final_pnl_cents=_percentile(final_pnls, 0.90),
        median_final_entries=_percentile(final_entries, 0.50),
        median_final_markets=_percentile(final_markets, 0.50),
        success_definition=(
            "final entries >= target, markets >= target, selected PnL >= "
            "target_entries * target_avg_entry_cents, avg entry >= target, "
            "and matched-v28 delta > 0"
        ),
    )


def _recommendation(
    *,
    row: dict[str, Any],
    native_report: dict[str, Any],
    prequential_report: dict[str, Any],
    bootstrap: BootstrapResult,
    futility_probability_threshold: float,
) -> tuple[str, list[str]]:
    reasons: list[str] = []
    if _float(row.get("selected_pnl_cents")) <= 0.0:
        reasons.append("forward_locked_selected_pnl_nonpositive")
    if _float(row.get("avg_pnl_per_entry_cents")) < 0.0:
        reasons.append("forward_locked_avg_entry_negative")
    if _float(row.get("matched_v28_delta_cents")) <= 0.0:
        reasons.append("does_not_beat_matched_v28_on_forward_timestamps")
    if _int(native_report.get("locked_total_entries")) >= 100 and _float(native_report.get("locked_total_pnl_cents")) <= 0.0:
        reasons.append("native_locked_entries_ge_100_and_negative")
    aggregate = prequential_report.get("aggregate") or {}
    if _int(aggregate.get("locked_gate_selection_count")) == 0:
        reasons.append("prequential_locked_gate_selection_count_zero")
    if bootstrap.success_probability <= futility_probability_threshold:
        reasons.append("bootstrap_predictive_success_probability_below_threshold")

    if len(reasons) >= 5:
        decision = "reject_current_locked_family_for_promotion"
    else:
        decision = "continue_collecting_current_locked_family"
    return decision, reasons


def _markdown(report: dict[str, Any]) -> str:
    recovery = report["recovery_math"]
    bootstrap = report["bootstrap"]
    lines = [
        "# RV600 Forward Futility Probe",
        "",
        f"- generated_utc: {report['generated_utc']}",
        f"- research_only: {report['research_only']}",
        f"- decision: {report['decision']}",
        f"- reasons: {', '.join(report['reasons']) if report['reasons'] else 'none'}",
        "",
        "## Current Locked Family",
        "",
        f"- variant: `{report['current_forward_row']['variant']}`",
        f"- accounting_mode: `{report['current_forward_row']['accounting_mode']}`",
        f"- accepted_entries: {recovery['current_entries']}",
        f"- distinct_markets: {recovery['current_markets']}",
        f"- selected_pnl_cents: {recovery['current_pnl_cents']:.1f}",
        f"- avg_pnl_per_entry_cents: {recovery['current_avg_pnl_per_entry_cents']:.3f}",
        f"- matched_v28_delta_cents: {report['current_forward_row']['matched_v28_delta_cents']:.1f}",
        "",
        "## Recovery Math",
        "",
        f"- target_entries: {recovery['target_entries']}",
        f"- target_markets: {recovery['target_markets']}",
        f"- target_total_pnl_cents: {recovery['target_total_pnl_cents']:.1f}",
        f"- remaining_entries_to_target: {recovery['remaining_entries_to_target']}",
        f"- remaining_markets_to_target: {recovery['remaining_markets_to_target']}",
        f"- required_remaining_avg_pnl_per_entry_cents: {recovery['required_remaining_avg_pnl_per_entry_cents']:.3f}",
        f"- required_remaining_avg_to_positive_cents: {recovery['required_remaining_avg_to_positive_cents']:.3f}",
        "",
        "## Native And Prequential Evidence",
        "",
        f"- native_roots: {report['native']['roots']}",
        f"- native_settled_markets: {report['native']['total_settled_markets']}",
        f"- native_candidate_rows: {report['native']['total_candidate_rows']}",
        f"- native_locked_total_entries: {report['native']['locked_total_entries']}",
        f"- native_locked_total_pnl_cents: {report['native']['locked_total_pnl_cents']:.1f}",
        f"- prequential_split_count: {report['prequential']['split_count']}",
        f"- prequential_locked_gate_selection_count: {report['prequential']['locked_gate_selection_count']}",
        f"- prequential_test_selected_pnl_cents: {report['prequential']['test_selected_pnl_cents']:.1f}",
        "",
        "## Bootstrap Predictive Check",
        "",
        f"- iterations: {bootstrap['iterations']}",
        f"- usable_root_blocks: {bootstrap['usable_root_blocks']}",
        f"- success_probability: {bootstrap['success_probability']:.4f}",
        f"- median_final_pnl_cents: {bootstrap['median_final_pnl_cents']:.1f}",
        f"- p90_final_pnl_cents: {bootstrap['p90_final_pnl_cents']:.1f}",
        f"- success_definition: {bootstrap['success_definition']}",
        "",
        "## Method Choice",
        "",
        "Chosen method: pre-specified interim futility check with recovery math and bootstrap predictive probability.",
        "",
        "Options considered:",
        "",
        "- Bayesian predictive-probability futility: best fit for an interim stop/continue decision.",
        "- Sequential probability ratio testing: useful for binary win-rate tests, but less aligned with fee-adjusted PnL targets.",
        "- Deflated Sharpe ratio: useful for multiple tested strategies, but current blocker is one locked family in live-forward shadow.",
        "- CSCV / probability of backtest overfitting: useful for retrospective grid selection risk, already addressed by prequential reports.",
        "- White reality-check style multiple-testing control: useful before selecting a new grid winner, not needed to reject this frozen family.",
        "",
        "References:",
        "",
        "- FDA guidance, Bayesian statistics in medical device clinical trials: predictive probability and interim planning.",
        "- Wald sequential probability ratio test: classic sequential decision framing.",
        "- Bailey and Lopez de Prado, Deflated Sharpe Ratio.",
        "- Bailey, Borwein, Lopez de Prado, and Zhu, Probability of Backtest Overfitting.",
        "- White, A Reality Check for Data Snooping.",
        "",
        "## Interpretation",
        "",
        "The current locked family should be rejected for promotion and should not keep consuming forward-shadow collection by itself.",
        "RV600 work can continue only by formally freezing a new candidate from existing evidence, then subjecting that new candidate to the same forward gates.",
        "",
    ]
    return "\n".join(lines)


def build_report(args: argparse.Namespace) -> dict[str, Any]:
    forward = _load_json(args.forward_json)
    native = _load_json(args.native_json)
    prequential = _load_json(args.prequential_json)
    audit = _load_json(args.audit_json)
    row = _best_forward_row(forward)
    if not row:
        raise SystemExit("forward report has no summary_rows")
    run_rows = _matching_run_rows(forward, row)
    recovery = _recovery_math(
        row,
        target_entries=args.target_entries,
        target_markets=args.target_markets,
        target_avg_entry_cents=args.target_avg_entry_cents,
    )
    bootstrap = _bootstrap_predictive_probability(
        row,
        run_rows,
        target_entries=args.target_entries,
        target_markets=args.target_markets,
        target_avg_entry_cents=args.target_avg_entry_cents,
        iterations=args.bootstrap_iterations,
        seed=args.seed,
    )
    decision, reasons = _recommendation(
        row=row,
        native_report=native,
        prequential_report=prequential,
        bootstrap=bootstrap,
        futility_probability_threshold=args.futility_probability_threshold,
    )
    aggregate = prequential.get("aggregate") or {}
    report = {
        "schema_version": "rv600-forward-futility-v1",
        "generated_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "research_only": True,
        "decision": decision,
        "reasons": reasons,
        "futility_probability_threshold": args.futility_probability_threshold,
        "current_forward_row": {
            key: row.get(key)
            for key in [
                "variant",
                "accounting_mode",
                "accepted_entries",
                "distinct_markets",
                "selected_pnl_cents",
                "avg_pnl_per_entry_cents",
                "matched_v28_control_pnl_cents",
                "matched_v28_delta_cents",
                "rejection_reason",
            ]
        },
        "recovery_math": asdict(recovery),
        "bootstrap": asdict(bootstrap),
        "native": {
            "roots": len(native.get("roots") or []),
            "total_settled_markets": _int(native.get("total_settled_markets")),
            "total_candidate_rows": _int(native.get("total_candidate_rows")),
            "locked_total_entries": _int(native.get("locked_total_entries")),
            "locked_total_pnl_cents": _float(native.get("locked_total_pnl_cents")),
        },
        "prequential": {
            "split_count": _int(aggregate.get("split_count")),
            "locked_gate_selection_count": _int(aggregate.get("locked_gate_selection_count")),
            "diagnostic_fallback_selection_count": _int(aggregate.get("diagnostic_fallback_selection_count")),
            "test_selected_pnl_cents": _float(aggregate.get("test_selected_pnl_cents")),
            "test_matched_v28_delta_cents": _float(aggregate.get("test_matched_v28_delta_cents")),
            "positive_test_split_rate": _float(aggregate.get("positive_test_split_rate")),
        },
        "audit": {
            "goal_complete": bool(audit.get("goal_complete")),
            "status_counts": audit.get("status_counts") or {},
        },
        "inputs": {
            "forward_json": str(args.forward_json),
            "native_json": str(args.native_json),
            "prequential_json": str(args.prequential_json),
            "audit_json": str(args.audit_json),
        },
    }
    return report


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--forward-json", type=Path, default=DEFAULT_FORWARD_JSON)
    parser.add_argument("--native-json", type=Path, default=DEFAULT_NATIVE_JSON)
    parser.add_argument("--prequential-json", type=Path, default=DEFAULT_PREQUENTIAL_JSON)
    parser.add_argument("--audit-json", type=Path, default=DEFAULT_AUDIT_JSON)
    parser.add_argument("--output-json", type=Path, default=DEFAULT_OUTPUT_JSON)
    parser.add_argument("--output-md", type=Path, default=DEFAULT_OUTPUT_MD)
    parser.add_argument("--target-entries", type=int, default=100)
    parser.add_argument("--target-markets", type=int, default=40)
    parser.add_argument("--target-avg-entry-cents", type=float, default=10.0)
    parser.add_argument("--bootstrap-iterations", type=int, default=20000)
    parser.add_argument("--seed", type=int, default=600)
    parser.add_argument("--futility-probability-threshold", type=float, default=0.05)
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
    print(f"decision={report['decision']}")
    print(f"reasons={';'.join(report['reasons'])}")
    print(f"success_probability={report['bootstrap']['success_probability']:.4f}")
    print(f"required_remaining_avg_pnl_per_entry_cents={report['recovery_math']['required_remaining_avg_pnl_per_entry_cents']:.3f}")
    print(f"output_json={args.output_json}")
    print(f"output_md={args.output_md}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
