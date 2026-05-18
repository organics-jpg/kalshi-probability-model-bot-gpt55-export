"""Run a bounded research-only forward loop for the v28 successor live-P&L policy.

This is an operator convenience wrapper around the live-P&L policy cycle and
strict goal-completion audit. It repeatedly:

1. optionally captures public REST BTC15M sidecar rows before resolution;
2. rebuilds the frozen live-P&L policy registry and paired baselines;
3. fetches labels when available;
4. reruns the strict profit-goal audit.

It never touches live bot processes, order logic, thresholds, secrets, state,
sizing, positions, or orders.
"""
from __future__ import annotations

import argparse
import json
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from audit_v28_successor_live_pnl_goal_completion import build_checklist
from audit_v28_successor_live_pnl_goal_completion import run_tests
from audit_v28_successor_live_pnl_goal_completion import write_outputs as write_audit_outputs
from run_v28_successor_live_pnl_policy_cycle import run_live_pnl_policy_cycle
from run_v28_successor_live_pnl_policy_cycle import write_outputs as write_policy_cycle_outputs


ROOT = Path(__file__).resolve().parent
EDGE_DIR = ROOT / "logs" / "edge_research"

LOOP_JSON = EDGE_DIR / "v28_successor_live_pnl_policy_forward_loop_latest.json"
LOOP_MD = EDGE_DIR / "v28_successor_live_pnl_policy_forward_loop_latest.md"

RESEARCH_ONLY_GUARDRAILS = [
    "does not start or stop live bot processes",
    "does not read or write secrets",
    "does not place orders",
    "does not mutate live thresholds, order logic, state, or sizing",
    "uses public/recorded sidecar artifacts only",
    "keeps pre-policy-hash rows diagnostic only",
    "keeps controlled live authorization false unless the strict audit eventually passes",
]


def iso_z(value: datetime | None = None) -> str:
    value = value or datetime.now(timezone.utc)
    return value.astimezone(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def rel_path(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(ROOT)).replace("\\", "/")
    except ValueError:
        return str(path)


def as_int(value: Any) -> int:
    try:
        return int(float(value or 0))
    except (TypeError, ValueError):
        return 0


def as_float(value: Any) -> float:
    try:
        return float(value or 0.0)
    except (TypeError, ValueError):
        return 0.0


def iteration_row(
    *,
    index: int,
    cycle_report: dict[str, Any],
    audit_summary: dict[str, Any],
    test_status: str,
) -> dict[str, Any]:
    cycle = cycle_report["summary"]
    return {
        "iteration": index,
        "generated_utc": iso_z(),
        "cycle_status": cycle.get("cycle_status", ""),
        "policy_id": cycle.get("policy_id", ""),
        "policy_hash": cycle.get("policy_hash", ""),
        "registry_rows": as_int(cycle.get("registry_rows")),
        "primary_policy_rows_after_hash": as_int(cycle.get("primary_policy_rows_after_hash")),
        "joined_primary_rows": as_int(audit_summary.get("joined_primary_rows")),
        "joined_primary_markets": as_int(audit_summary.get("joined_primary_markets")),
        "primary_entered_rows": as_int(audit_summary.get("primary_entered_rows")),
        "primary_net_pnl_cents": as_float(audit_summary.get("primary_net_pnl_cents")),
        "primary_delta_vs_v28_cents": as_float(audit_summary.get("primary_delta_vs_v28_cents")),
        "profit_goal_complete": bool(audit_summary.get("profit_goal_complete")),
        "overall_status": audit_summary.get("overall_status", ""),
        "test_status": test_status,
        "blockers": cycle.get("blockers") or [],
        "next_actions": cycle.get("next_actions") or [],
    }


def run_loop(
    *,
    collect_mode: str,
    nearest_close_only: bool,
    iterations: int,
    sleep_seconds: float,
    timeout_seconds: float,
    max_markets: int,
    skip_label_fetch: bool,
    refresh_downstream_audits: bool,
    run_tests_each_iteration: bool,
    stop_when_profit_goal_complete: bool,
    write: bool,
    dry_run: bool,
) -> dict[str, Any]:
    started = iso_z()
    iteration_reports: list[dict[str, Any]] = []
    loop_status = "planned" if dry_run else "completed_iterations"

    if dry_run:
        return {
            "generated_utc": iso_z(),
            "started_utc": started,
            "loop_status": loop_status,
            "collect_mode": collect_mode,
            "collection_scope": "nearest_close" if nearest_close_only else "all_open_closes",
            "iterations_requested": iterations,
            "iterations_run": 0,
            "promotion_allowed": False,
            "controlled_live_test_authorized": False,
            "profit_goal_complete": False,
            "final": {},
            "research_only_guardrails": RESEARCH_ONLY_GUARDRAILS,
            "iterations": [],
            "outputs": {"json": rel_path(LOOP_JSON), "markdown": rel_path(LOOP_MD)},
        }

    for index in range(iterations):
        if index and sleep_seconds > 0:
            time.sleep(sleep_seconds)

        cycle_report = run_live_pnl_policy_cycle(
            collect_mode=collect_mode,
            timeout_seconds=timeout_seconds,
            max_markets=max_markets,
            nearest_close_only=nearest_close_only,
            write=write,
            skip_label_fetch=skip_label_fetch,
            refresh_downstream_audits=refresh_downstream_audits,
        )
        if write:
            write_policy_cycle_outputs(cycle_report)

        test_result = run_tests(run_tests_each_iteration)
        checklist, audit_summary = build_checklist(test_result=test_result)
        if write:
            write_audit_outputs(checklist, audit_summary)

        item = iteration_row(
            index=index + 1,
            cycle_report=cycle_report,
            audit_summary=audit_summary,
            test_status=str(test_result.get("status") or "unknown"),
        )
        iteration_reports.append(item)
        if stop_when_profit_goal_complete and item["profit_goal_complete"]:
            loop_status = "profit_goal_complete"
            break

    final = iteration_reports[-1] if iteration_reports else {}
    return {
        "generated_utc": iso_z(),
        "started_utc": started,
        "loop_status": loop_status,
        "collect_mode": collect_mode,
        "collection_scope": "nearest_close" if nearest_close_only else "all_open_closes",
        "iterations_requested": iterations,
        "iterations_run": len(iteration_reports),
        "promotion_allowed": False,
        "controlled_live_test_authorized": False,
        "profit_goal_complete": bool(final.get("profit_goal_complete")),
        "final": final,
        "research_only_guardrails": RESEARCH_ONLY_GUARDRAILS,
        "iterations": iteration_reports,
        "outputs": {"json": rel_path(LOOP_JSON), "markdown": rel_path(LOOP_MD)},
    }


def write_markdown(report: dict[str, Any], path: Path = LOOP_MD) -> None:
    final = report.get("final") or {}
    lines = [
        "# v28 Successor Live P&L Policy Forward Loop",
        "",
        "Research-only bounded loop for freezing live policy rows, labeling settled rows, scoring paired baselines, and rerunning the strict profit-goal audit.",
        "",
        "## Summary",
        "",
        f"- Generated UTC: `{report['generated_utc']}`",
        f"- Loop status: `{report['loop_status']}`",
        f"- Collect mode: `{report['collect_mode']}`",
        f"- Collection scope: `{report['collection_scope']}`",
        f"- Iterations run: `{report['iterations_run']}` / `{report['iterations_requested']}`",
        f"- Profit goal complete: `{report['profit_goal_complete']}`",
        f"- Promotion allowed: `{report['promotion_allowed']}`",
        f"- Controlled live test authorized: `{report['controlled_live_test_authorized']}`",
        "",
        "## Final State",
        "",
    ]
    if final:
        for key in [
            "cycle_status",
            "policy_id",
            "policy_hash",
            "registry_rows",
            "primary_policy_rows_after_hash",
            "joined_primary_rows",
            "joined_primary_markets",
            "primary_entered_rows",
            "primary_net_pnl_cents",
            "primary_delta_vs_v28_cents",
            "overall_status",
            "test_status",
        ]:
            lines.append(f"- {key}: `{final.get(key)}`")
    else:
        lines.append("- No iterations were run.")

    lines.extend(
        [
            "",
            "## Iterations",
            "",
            "| iteration | cycle status | primary policy rows | joined rows | joined markets | entries | net cents | delta vs v28 | audit |",
            "|---:|---|---:|---:|---:|---:|---:|---:|---|",
        ]
    )
    for item in report["iterations"]:
        lines.append(
            f"| {item['iteration']} | `{item['cycle_status']}` | "
            f"{item['primary_policy_rows_after_hash']} | {item['joined_primary_rows']} | "
            f"{item['joined_primary_markets']} | {item['primary_entered_rows']} | "
            f"{item['primary_net_pnl_cents']} | {item['primary_delta_vs_v28_cents']} | "
            f"`{item['overall_status']}` |"
        )

    lines.extend(
        [
            "",
            "## Guardrails",
            "",
            *[f"- {item}" for item in report["research_only_guardrails"]],
            "",
            "## Read",
            "",
            "- This loop is an evidence collector and auditor, not a promotion path.",
            "- A skipped policy row can still count as a primary observed opportunity; P&L proof requires settled joined rows and positive same-row economics.",
            "- Use `--collect-mode public-rest` only when public pre-resolution capture is intended.",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_outputs(report: dict[str, Any]) -> None:
    EDGE_DIR.mkdir(parents=True, exist_ok=True)
    LOOP_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_markdown(report, LOOP_MD)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--collect-mode", choices=["none", "public-rest"], default="none")
    parser.add_argument("--iterations", type=int, default=1)
    parser.add_argument("--sleep-seconds", type=float, default=0.0)
    parser.add_argument("--timeout-seconds", type=float, default=10.0)
    parser.add_argument("--max-markets", type=int, default=80)
    parser.add_argument("--all-open-closes", action="store_true")
    parser.add_argument("--skip-label-fetch", action="store_true")
    parser.add_argument("--skip-downstream-audits", action="store_true")
    parser.add_argument("--skip-tests", action="store_true")
    parser.add_argument("--stop-when-profit-goal-complete", action="store_true")
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    if args.iterations < 1:
        parser.error("--iterations must be >= 1")
    if args.sleep_seconds < 0:
        parser.error("--sleep-seconds must be >= 0")

    report = run_loop(
        collect_mode=args.collect_mode.replace("-", "_"),
        nearest_close_only=not args.all_open_closes,
        iterations=args.iterations,
        sleep_seconds=args.sleep_seconds,
        timeout_seconds=args.timeout_seconds,
        max_markets=args.max_markets,
        skip_label_fetch=args.skip_label_fetch,
        refresh_downstream_audits=not args.skip_downstream_audits,
        run_tests_each_iteration=not args.skip_tests,
        stop_when_profit_goal_complete=args.stop_when_profit_goal_complete,
        write=bool(args.write and not args.dry_run),
        dry_run=args.dry_run,
    )
    if args.write and not args.dry_run:
        write_outputs(report)
    print(
        json.dumps(
            {
                "loop_status": report["loop_status"],
                "collect_mode": report["collect_mode"],
                "collection_scope": report["collection_scope"],
                "iterations_run": report["iterations_run"],
                "profit_goal_complete": report["profit_goal_complete"],
                "final": report.get("final") or {},
                "promotion_allowed": report["promotion_allowed"],
                "controlled_live_test_authorized": report["controlled_live_test_authorized"],
                "written": bool(args.write and not args.dry_run),
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
