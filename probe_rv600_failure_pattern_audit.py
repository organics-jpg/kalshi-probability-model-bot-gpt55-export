from __future__ import annotations

import argparse
import json
from collections import Counter
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from probe_rv600_cumulative_opportunity import discover_roots
from research_particle.replay_runner import ReplayConfig
from research_particle.rv600_variation_test import build_rv600_variation_report


DEFAULT_GRID_JSON = Path("logs/particle_research/reports/rv600_variation_forward_grid_latest.json")
DEFAULT_FAMILY_JSON = Path("logs/particle_research/reports/rv600_plan_family_rejection_latest.json")
DEFAULT_FUTILITY_JSON = Path("logs/particle_research/reports/rv600_forward_futility_latest.json")
DEFAULT_OBJECTIVE_JSON = Path("logs/particle_research/reports/rv600_objective_state_latest.json")
DEFAULT_RESCUE_JSONS = [
    Path("logs/particle_research/reports/rv600_meta_label_rescue_latest.json"),
    Path("logs/particle_research/reports/rv600_probability_calibration_rescue_latest.json"),
    Path("logs/particle_research/reports/rv600_conformal_abstention_rescue_latest.json"),
    Path("logs/particle_research/reports/rv600_online_expert_rescue_latest.json"),
    Path("logs/particle_research/reports/rv600_market_balance_rescue_latest.json"),
    Path("logs/particle_research/reports/rv600_regime_filter_rescue_latest.json"),
    Path("logs/particle_research/reports/rv600_group_dro_rescue_latest.json"),
]
DEFAULT_REAL_SHADOW_DIR = Path("logs/particle_research/real_shadow")
DEFAULT_REPORTS_DIR = Path("logs/particle_research/reports")
DEFAULT_MIN_ROOT_NAME = "rv600_next_evidence_shadow_20260513T195001Z"
DEFAULT_MIN_DECISION_TS_UTC = "2026-05-13T19:50:00+00:00"
DEFAULT_OUTPUT_JSON = Path("logs/particle_research/reports/rv600_failure_pattern_audit_latest.json")
DEFAULT_OUTPUT_MD = Path("logs/particle_research/reports/rv600_failure_pattern_audit_latest.md")


def _load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
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


def _parse_dt(value: str) -> datetime:
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def _grid_payload(args: argparse.Namespace) -> tuple[dict[str, Any], dict[str, Any]]:
    if args.grid_json is not None:
        return _load_json(args.grid_json), {"grid_json": str(args.grid_json)}
    roots = tuple(
        args.root
        or discover_roots(args.base_dir, args.reports_dir, args.min_root_name)
    )
    variation_report = build_rv600_variation_report(
        roots,
        phase="grid",
        config=ReplayConfig(min_fill_prob=0.0, counterfactual_fill_threshold=0.5),
        min_decision_ts_utc=(
            _parse_dt(args.min_decision_ts_utc) if args.min_decision_ts_utc else None
        ),
    )
    return (
        {
            "generated_utc": variation_report.generated_utc,
            "phase": variation_report.phase,
            "root_count": variation_report.root_count,
            "roots": list(variation_report.roots),
            "variant_count": variation_report.variant_count,
            "summary_rows": [asdict(row) for row in variation_report.summary_rows],
        },
        {
            "source": "settled_bounded_roots",
            "roots": [str(root) for root in roots],
            "base_dir": str(args.base_dir),
            "reports_dir": str(args.reports_dir),
            "min_root_name": args.min_root_name,
            "min_decision_ts_utc": args.min_decision_ts_utc,
        },
    )


def _rejection_counter(rows: list[dict[str, Any]]) -> dict[str, int]:
    counter: Counter[str] = Counter()
    for row in rows:
        for item in str(row.get("rejection_reason") or "").split(";"):
            if item:
                counter[item] += 1
    return dict(counter.most_common())


def _passes_revision_support(row: dict[str, Any]) -> bool:
    if str(row.get("accounting_mode")) != "position_capped":
        return False
    if _int(row.get("gate_count")) > 3:
        return False
    if _int(row.get("accepted_entries")) < 25:
        return False
    if _float(row.get("selected_pnl_cents")) <= 0.0:
        return False
    if _float(row.get("matched_v28_delta_cents")) <= 0.0:
        return False
    if _float(row.get("avg_pnl_per_entry_cents")) < 10.0:
        return False
    if _float(row.get("avg_pnl_per_market_cents")) <= 0.0:
        return False
    if _float(row.get("positive_root_rate")) < 0.60:
        return False
    if _float(row.get("positive_market_rate")) < 0.60:
        return False
    if _float(row.get("max_single_market_pnl_share")) > 0.25:
        return False
    if _float(row.get("last_window_pnl_cents")) <= 0.0:
        return False
    if _float(row.get("added_entry_count")) and _float(row.get("added_entry_pnl_cents")) <= 0.0:
        return False
    return True


def _compact_grid_row(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "variant": row.get("variant"),
        "accounting_mode": row.get("accounting_mode"),
        "gate_count": _int(row.get("gate_count")),
        "accepted_entries": _int(row.get("accepted_entries")),
        "distinct_markets": _int(row.get("distinct_markets")),
        "selected_pnl_cents": _float(row.get("selected_pnl_cents")),
        "matched_v28_delta_cents": _float(row.get("matched_v28_delta_cents")),
        "avg_pnl_per_entry_cents": _float(row.get("avg_pnl_per_entry_cents")),
        "positive_root_rate": _float(row.get("positive_root_rate")),
        "positive_market_rate": _float(row.get("positive_market_rate")),
        "max_single_market_pnl_share": _float(row.get("max_single_market_pnl_share")),
        "last_window_pnl_cents": _float(row.get("last_window_pnl_cents")),
        "rejection_reason": row.get("rejection_reason") or "",
    }


def _rescue_row(path: Path) -> dict[str, Any]:
    payload = _load_json(path)
    aggregate = payload.get("aggregate") or {}
    prequential = payload.get("prequential") or {}
    decision = payload.get("decision") or ""
    pass_decision = decision.endswith("_pass")
    if prequential:
        return {
            "report": str(path),
            "schema_version": payload.get("schema_version") or "",
            "preliminary_gate_pass": pass_decision,
            "train_gate_selection_count": _int(prequential.get("selection_count")),
            "test_total_entries": _int(prequential.get("test_entry_count")),
            "test_selected_pnl_cents": _float(prequential.get("test_selected_pnl_cents")),
            "test_matched_v28_delta_cents": _float(prequential.get("test_matched_v28_delta_cents")),
            "positive_test_split_rate": _float(prequential.get("positive_test_root_rate")),
            "rejection_reason": "" if pass_decision else str(decision),
        }
    return {
        "report": str(path),
        "schema_version": payload.get("schema_version") or "",
        "preliminary_gate_pass": aggregate.get("preliminary_gate_pass") is True,
        "train_gate_selection_count": _int(aggregate.get("train_gate_selection_count")),
        "test_total_entries": _int(aggregate.get("test_total_entries")),
        "test_selected_pnl_cents": _float(aggregate.get("test_selected_pnl_cents")),
        "test_matched_v28_delta_cents": _float(aggregate.get("test_matched_v28_delta_cents")),
        "positive_test_split_rate": _float(aggregate.get("positive_test_split_rate")),
        "rejection_reason": aggregate.get("rejection_reason") or "",
    }


def build_report(args: argparse.Namespace) -> dict[str, Any]:
    grid, grid_input = _grid_payload(args)
    family = _load_json(args.family_json)
    futility = _load_json(args.futility_json)
    objective = _load_json(args.objective_json)
    rows = list(grid.get("summary_rows") or [])
    if not rows:
        raise SystemExit("grid report has no summary_rows")
    position_rows = [row for row in rows if row.get("accounting_mode") == "position_capped"]
    simple_position_rows = [row for row in position_rows if _int(row.get("gate_count")) <= 3]
    positive_position_rows = [row for row in position_rows if _float(row.get("selected_pnl_cents")) > 0.0]
    positive_delta_rows = [row for row in position_rows if _float(row.get("matched_v28_delta_cents")) > 0.0]
    support_rows = [row for row in position_rows if _passes_revision_support(row)]
    best_soft_rows = sorted(
        positive_position_rows,
        key=lambda row: (
            _float(row.get("matched_v28_delta_cents")),
            _float(row.get("selected_pnl_cents")),
            _float(row.get("avg_pnl_per_entry_cents")),
        ),
        reverse=True,
    )[:10]
    rescue_rows = [_rescue_row(path) for path in args.rescue_json]
    rescue_gate_pass_count = sum(1 for row in rescue_rows if row["preliminary_gate_pass"])
    rescue_reason_counter: Counter[str] = Counter()
    for row in rescue_rows:
        for item in str(row["rejection_reason"]).split(";"):
            if item:
                rescue_reason_counter[item] += 1
    plan_revision_supported = bool(support_rows) or rescue_gate_pass_count > 0
    decision = "candidate_revision_supported" if plan_revision_supported else "no_current_plan_revision_supported"
    report = {
        "schema_version": "rv600-failure-pattern-audit-v1",
        "generated_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "research_only": True,
        "decision": decision,
        "plan_revision_supported": plan_revision_supported,
        "grid": {
            "generated_utc": grid.get("generated_utc") or "",
            "phase": grid.get("phase") or "",
            "root_count": _int(grid.get("root_count")),
            "roots": grid.get("roots") or [],
            "variant_count": _int(grid.get("variant_count")),
            "summary_row_count": len(rows),
            "position_capped_row_count": len(position_rows),
            "simple_position_capped_row_count": len(simple_position_rows),
            "positive_position_capped_row_count": len(positive_position_rows),
            "positive_matched_v28_delta_row_count": len(positive_delta_rows),
            "support_row_count": len(support_rows),
            "top_rejection_reasons": _rejection_counter(position_rows),
            "best_soft_rows": [_compact_grid_row(row) for row in best_soft_rows],
            "support_rows": [_compact_grid_row(row) for row in support_rows[:20]],
        },
        "rescues": {
            "rows": rescue_rows,
            "gate_pass_count": rescue_gate_pass_count,
            "top_rejection_reasons": dict(rescue_reason_counter.most_common()),
        },
        "family_decision": family.get("decision") or "",
        "futility_decision": futility.get("decision") or "",
        "objective_decision": objective.get("decision") or "",
        "objective_blocked_by": objective.get("blocked_by") or [],
        "interpretation": _interpretation(plan_revision_supported, support_rows, rescue_gate_pass_count),
        "inputs": {
            "grid": grid_input,
            "family_json": str(args.family_json),
            "futility_json": str(args.futility_json),
            "objective_json": str(args.objective_json),
            "rescue_json": [str(path) for path in args.rescue_json],
        },
    }
    return report


def _interpretation(plan_revision_supported: bool, support_rows: list[dict[str, Any]], rescue_gate_pass_count: int) -> str:
    if plan_revision_supported:
        return (
            f"Found {len(support_rows)} grid support rows and {rescue_gate_pass_count} rescue gate-pass rows; "
            "freeze the simplest surviving candidate and run a fresh forward-shadow cycle before any live test."
        )
    return (
        "No current artifact supports a new RV600 plan revision. Positive grid rows are sparse or concentrated, "
        "matched-v28 delta is not positive enough, and every literature-backed rescue has zero train-gate selections. "
        "The next valid progress requires materially new shadow evidence or a genuinely new RV600 clue, not another "
        "promotion attempt from this sample."
    )


def _markdown(report: dict[str, Any]) -> str:
    grid = report["grid"]
    rescues = report["rescues"]
    lines = [
        "# RV600 Failure Pattern Audit",
        "",
        f"- generated_utc: {report['generated_utc']}",
        f"- research_only: {report['research_only']}",
        f"- decision: {report['decision']}",
        f"- plan_revision_supported: {report['plan_revision_supported']}",
        f"- family_decision: `{report['family_decision']}`",
        f"- futility_decision: `{report['futility_decision']}`",
        f"- objective_decision: `{report['objective_decision']}`",
        "",
        "## Grid Pattern",
        "",
        f"- grid_generated_utc: {grid['generated_utc']}",
        f"- phase: `{grid['phase']}`",
        f"- root_count: {grid['root_count']}",
        f"- roots: {', '.join(grid['roots']) if grid['roots'] else 'none'}",
        f"- variant_count: {grid['variant_count']}",
        f"- summary_row_count: {grid['summary_row_count']}",
        f"- position_capped_row_count: {grid['position_capped_row_count']}",
        f"- simple_position_capped_row_count: {grid['simple_position_capped_row_count']}",
        f"- positive_position_capped_row_count: {grid['positive_position_capped_row_count']}",
        f"- positive_matched_v28_delta_row_count: {grid['positive_matched_v28_delta_row_count']}",
        f"- support_row_count: {grid['support_row_count']}",
        "",
        "Top position-capped rejection reasons:",
    ]
    for reason, count in list(grid["top_rejection_reasons"].items())[:10]:
        lines.append(f"- `{reason}`: {count}")
    lines.extend(
        [
            "",
            "## Rescue Pattern",
            "",
            f"- rescue_gate_pass_count: {rescues['gate_pass_count']}",
            "",
            "| report | gate pass | train gates | test entries | test pnl | v28 delta | rejection |",
            "|---|---:|---:|---:|---:|---:|---|",
        ]
    )
    for row in rescues["rows"]:
        lines.append(
            "| `{report}` | {preliminary_gate_pass} | {train_gate_selection_count} | {test_total_entries} | {test_selected_pnl_cents:.1f} | {test_matched_v28_delta_cents:.1f} | `{rejection_reason}` |".format(
                **row
            )
        )
    lines.extend(
        [
            "",
            "## Best Soft Rows",
            "",
            "| variant | accounting | gates | entries | pnl | v28 delta | pos roots | pos markets | max share | rejection |",
            "|---|---|---:|---:|---:|---:|---:|---:|---:|---|",
        ]
    )
    for row in grid["best_soft_rows"]:
        lines.append(
            "| `{variant}` | {accounting_mode} | {gate_count} | {accepted_entries} | {selected_pnl_cents:.1f} | {matched_v28_delta_cents:.1f} | {positive_root_rate:.2f} | {positive_market_rate:.2f} | {max_single_market_pnl_share:.2f} | `{rejection_reason}` |".format(
                **row
            )
        )
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            report["interpretation"],
            "",
        ]
    )
    return "\n".join(lines)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Audit RV600 failure patterns across grid and rescue reports.")
    parser.add_argument(
        "--grid-json",
        type=Path,
        default=None,
        help=(
            "Optional prebuilt grid report. When omitted, rebuilds the grid from "
            "currently settled bounded next-evidence roots."
        ),
    )
    parser.add_argument("--root", action="append", type=Path, default=[])
    parser.add_argument("--base-dir", type=Path, default=DEFAULT_REAL_SHADOW_DIR)
    parser.add_argument("--reports-dir", type=Path, default=DEFAULT_REPORTS_DIR)
    parser.add_argument("--min-root-name", default=DEFAULT_MIN_ROOT_NAME)
    parser.add_argument("--min-decision-ts-utc", default=DEFAULT_MIN_DECISION_TS_UTC)
    parser.add_argument("--family-json", type=Path, default=DEFAULT_FAMILY_JSON)
    parser.add_argument("--futility-json", type=Path, default=DEFAULT_FUTILITY_JSON)
    parser.add_argument("--objective-json", type=Path, default=DEFAULT_OBJECTIVE_JSON)
    parser.add_argument("--rescue-json", action="append", type=Path, default=DEFAULT_RESCUE_JSONS.copy())
    parser.add_argument("--output-json", type=Path, default=DEFAULT_OUTPUT_JSON)
    parser.add_argument("--output-md", type=Path, default=DEFAULT_OUTPUT_MD)
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
    print(f"plan_revision_supported={report['plan_revision_supported']}")
    print(f"support_row_count={report['grid']['support_row_count']}")
    print(f"rescue_gate_pass_count={report['rescues']['gate_pass_count']}")
    print(f"output_json={args.output_json}")
    print(f"output_md={args.output_md}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
