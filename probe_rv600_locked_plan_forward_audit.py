from __future__ import annotations

import argparse
import json
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from probe_rv600_cumulative_opportunity import discover_roots
from research_particle.replay_runner import ReplayConfig, load_replay_inputs_from_jsonl
from research_particle.rv600_variation_test import (
    RV600VariantSpec,
    _candidate_path,
    _extras_by_key,
    _label_path,
    _single_market_baseline_name,
    _summarize,
    evaluate_variant_specs,
    materialize_rv600_metrics,
)


DEFAULT_PLAN_JSON = Path(
    "logs/particle_research/locked_oos_plans/rv600_revision_RV600REV001_locked_plan.json"
)
DEFAULT_BASE_DIR = Path("logs/particle_research/real_shadow")
DEFAULT_REPORTS_DIR = Path("logs/particle_research/reports")
DEFAULT_MIN_ROOT_NAME = "rv600_next_evidence_shadow_20260513T195001Z"
DEFAULT_OUTPUT_JSON = Path("logs/particle_research/reports/rv600_locked_plan_forward_audit_latest.json")
DEFAULT_OUTPUT_MD = Path("logs/particle_research/reports/rv600_locked_plan_forward_audit_latest.md")


def _load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8-sig"))


def _parse_dt(value: Any) -> datetime:
    parsed = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def _spec_from_plan(plan: dict[str, Any]) -> RV600VariantSpec:
    candidate = plan.get("candidate") or {}
    return RV600VariantSpec(
        name=str(candidate.get("variant") or ""),
        probability_mode=str(candidate.get("probability_mode") or "rv600_primary"),  # type: ignore[arg-type]
        min_seconds_to_close=float(candidate.get("min_seconds_to_close") or 70.0),
        max_seconds_to_close=float(candidate.get("max_seconds_to_close") or 600.0),
        min_ev_cents=float(candidate.get("min_ev_cents") or 0.0),
        entry_rule=str(candidate.get("entry_rule") or "single_market"),  # type: ignore[arg-type]
        max_entries_per_market=int(candidate.get("max_entries_per_market") or 1),
        risk_cap_cents=candidate.get("risk_cap_cents"),
    )


def _single_market_spec_for(spec: RV600VariantSpec) -> RV600VariantSpec | None:
    baseline_name = _single_market_baseline_name(spec.name)
    if not baseline_name:
        return None
    return RV600VariantSpec(
        name=baseline_name,
        probability_mode=spec.probability_mode,
        min_seconds_to_close=spec.min_seconds_to_close,
        max_seconds_to_close=spec.max_seconds_to_close,
        min_ev_cents=spec.min_ev_cents,
        entry_rule="single_market",
        max_entries_per_market=1,
        risk_cap_cents=None,
    )


def build_report(args: argparse.Namespace) -> dict[str, Any]:
    plan = _load_json(args.plan_json)
    if not plan:
        raise SystemExit(f"plan not found or invalid: {args.plan_json}")
    start_utc = _parse_dt((plan.get("pre_registration") or {}).get("forward_evidence_starts_after_utc"))
    spec = _spec_from_plan(plan)
    baseline_spec = _single_market_spec_for(spec)
    specs = [spec] + ([baseline_spec] if baseline_spec is not None else [])
    roots = tuple(args.root or discover_roots(args.base_dir, args.reports_dir, args.min_root_name))
    run_rows = []
    root_rows = []
    calendar_days: set[str] = set()
    weekend_days: set[str] = set()
    for root in roots:
        rows = load_replay_inputs_from_jsonl(_candidate_path(root), _label_path(root))
        rows = [row for row in rows if row.snapshot.decision_ts_utc > start_utc]
        if not rows:
            continue
        decision_times = [row.snapshot.decision_ts_utc for row in rows]
        for dt in decision_times:
            local_day = dt.astimezone(timezone.utc).date().isoformat()
            calendar_days.add(local_day)
            if dt.weekday() >= 5:
                weekend_days.add(local_day)
        metrics = materialize_rv600_metrics(rows, extras_by_key=_extras_by_key(_candidate_path(root)))
        evaluated = evaluate_variant_specs(
            metrics,
            specs,
            root_name=root.name,
            config=ReplayConfig(min_fill_prob=0.0, counterfactual_fill_threshold=0.5),
        )
        run_rows.extend(evaluated)
        root_rows.append(
            {
                "root": str(root),
                "candidate_rows_after_start": len(rows),
                "first_decision_ts_utc": min(decision_times).isoformat(),
                "last_decision_ts_utc": max(decision_times).isoformat(),
                "run_rows": [asdict(row) for row in evaluated],
            }
        )
    summary_rows = [asdict(row) for row in _summarize(run_rows)]
    primary_mode = str((plan.get("candidate") or {}).get("primary_accounting_mode") or "position_capped")
    primary = next(
        (
            row
            for row in summary_rows
            if row.get("variant") == spec.name and row.get("accounting_mode") == primary_mode
        ),
        None,
    )
    baseline_primary = next(
        (
            row
            for row in summary_rows
            if baseline_spec is not None
            and row.get("variant") == baseline_spec.name
            and row.get("accounting_mode") == primary_mode
        ),
        None,
    )
    target = plan.get("forward_gates") or {}
    target_entries = int(target.get("target_accepted_entries") or 100)
    target_markets = int(target.get("target_distinct_markets") or 40)
    target_days = int(target.get("target_calendar_days") or 10)
    target_weekends = int(target.get("target_weekend_sessions") or 2)
    sample_gates = {
        "accepted_entries": int((primary or {}).get("accepted_entries") or 0) >= target_entries,
        "distinct_markets": int((primary or {}).get("distinct_markets") or 0) >= target_markets,
        "calendar_days": len(calendar_days) >= target_days,
        "weekend_sessions": len(weekend_days) >= target_weekends,
    }
    primary_rejection = str((primary or {}).get("rejection_reason") or "")
    gate_pass = bool(primary) and not primary_rejection and all(sample_gates.values())
    report = {
        "schema_version": "rv600-locked-plan-forward-audit-v1",
        "generated_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "research_only": True,
        "decision": "locked_plan_forward_gate_pass" if gate_pass else "locked_plan_forward_incomplete_or_failed",
        "plan_id": plan.get("plan_id"),
        "plan_json": str(args.plan_json),
        "variant": spec.name,
        "single_market_benchmark_variant": baseline_spec.name if baseline_spec is not None else None,
        "forward_evidence_starts_after_utc": start_utc.isoformat(),
        "root_count": len(root_rows),
        "calendar_day_count": len(calendar_days),
        "weekend_day_count": len(weekend_days),
        "sample_gates": sample_gates,
        "primary_accounting_mode": primary_mode,
        "primary_summary": primary,
        "single_market_benchmark_summary": baseline_primary,
        "summary_rows": summary_rows,
        "root_rows": root_rows,
        "inputs": {
            "base_dir": str(args.base_dir),
            "reports_dir": str(args.reports_dir),
            "min_root_name": args.min_root_name,
        },
    }
    return report


def _markdown(report: dict[str, Any]) -> str:
    primary = report.get("primary_summary") or {}
    benchmark = report.get("single_market_benchmark_summary") or {}
    lines = [
        "# RV600 Locked Plan Forward Audit",
        "",
        f"- generated_utc: {report['generated_utc']}",
        f"- research_only: {report['research_only']}",
        f"- decision: {report['decision']}",
        f"- plan_id: `{report['plan_id']}`",
        f"- variant: `{report['variant']}`",
        f"- single_market_benchmark_variant: `{report['single_market_benchmark_variant']}`",
        f"- forward_evidence_starts_after_utc: `{report['forward_evidence_starts_after_utc']}`",
        f"- root_count: {report['root_count']}",
        f"- calendar_day_count: {report['calendar_day_count']}",
        f"- weekend_day_count: {report['weekend_day_count']}",
        "",
        "## Primary Summary",
        "",
    ]
    if primary:
        lines.extend(
            [
                f"- accounting_mode: `{primary.get('accounting_mode')}`",
                f"- accepted_entries: {primary.get('accepted_entries')}",
                f"- distinct_markets: {primary.get('distinct_markets')}",
                f"- selected_pnl_cents: {primary.get('selected_pnl_cents')}",
                f"- matched_v28_delta_cents: {primary.get('matched_v28_delta_cents')}",
                f"- avg_pnl_per_entry_cents: {primary.get('avg_pnl_per_entry_cents')}",
                f"- positive_root_rate: {primary.get('positive_root_rate')}",
                f"- positive_market_rate: {primary.get('positive_market_rate')}",
                f"- max_single_market_pnl_share: {primary.get('max_single_market_pnl_share')}",
                f"- last_window_pnl_cents: {primary.get('last_window_pnl_cents')}",
                f"- rejection_reason: `{primary.get('rejection_reason')}`",
            ]
        )
    else:
        lines.append("No primary summary row was produced.")
    lines.extend(["", "## Single-Market Benchmark", ""])
    if benchmark:
        lines.extend(
            [
                f"- accounting_mode: `{benchmark.get('accounting_mode')}`",
                f"- accepted_entries: {benchmark.get('accepted_entries')}",
                f"- distinct_markets: {benchmark.get('distinct_markets')}",
                f"- selected_pnl_cents: {benchmark.get('selected_pnl_cents')}",
                f"- matched_v28_delta_cents: {benchmark.get('matched_v28_delta_cents')}",
                f"- avg_pnl_per_entry_cents: {benchmark.get('avg_pnl_per_entry_cents')}",
                f"- rejection_reason: `{benchmark.get('rejection_reason')}`",
            ]
        )
    else:
        lines.append("No matching single-market benchmark summary row was produced.")
    lines.extend(["", "## Sample Gates", ""])
    for key, value in report["sample_gates"].items():
        lines.append(f"- {key}: {value}")
    lines.extend(["", "## Roots", ""])
    for row in report["root_rows"]:
        lines.append(
            f"- `{Path(row['root']).name}`: candidate_rows_after_start={row['candidate_rows_after_start']}; "
            f"first={row['first_decision_ts_utc']}; last={row['last_decision_ts_utc']}"
        )
    lines.append("")
    return "\n".join(lines)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Audit a frozen RV600 locked plan using future-only evidence.")
    parser.add_argument("--plan-json", type=Path, default=DEFAULT_PLAN_JSON)
    parser.add_argument("--root", action="append", type=Path, default=[])
    parser.add_argument("--base-dir", type=Path, default=DEFAULT_BASE_DIR)
    parser.add_argument("--reports-dir", type=Path, default=DEFAULT_REPORTS_DIR)
    parser.add_argument("--min-root-name", default=DEFAULT_MIN_ROOT_NAME)
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
    primary = report.get("primary_summary") or {}
    print(f"decision={report['decision']}")
    print(f"plan_id={report['plan_id']}")
    print(f"root_count={report['root_count']}")
    print(f"accepted_entries={primary.get('accepted_entries')}")
    print(f"selected_pnl_cents={primary.get('selected_pnl_cents')}")
    print(f"avg_pnl_per_entry_cents={primary.get('avg_pnl_per_entry_cents')}")
    print(f"rejection_reason={primary.get('rejection_reason')}")
    print(f"output_json={args.output_json}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
