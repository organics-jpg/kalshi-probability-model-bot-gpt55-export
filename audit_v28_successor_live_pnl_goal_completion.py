"""Audit progress against the v28 successor live-P&L goal.

Research-only. This turns the live-P&L goal plan into a concrete
prompt-to-artifact checklist. It does not touch live bot state, order logic,
thresholds, secrets, positions, or orders.
"""
from __future__ import annotations

import argparse
import csv
import json
import subprocess
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
DOCS_DIR = ROOT / "docs"
OUT_DIR = ROOT / "research_particle" / "v28_successor"
EDGE_DIR = ROOT / "logs" / "edge_research"

PLAN_MD = DOCS_DIR / "v28_successor_live_pnl_improvement_goal_plan.md"
POLICY_LAB_SCRIPT = ROOT / "build_v28_successor_live_pnl_policy_lab.py"
POLICY_CYCLE_SCRIPT = ROOT / "run_v28_successor_live_pnl_policy_cycle.py"
TEST_FILE = ROOT / "test_v28_successor_live_pnl_policy_lab.py"

POLICY_REGISTRY_CSV = OUT_DIR / "live_pnl_policy_registry_latest.csv"
LABELED_DECISIONS_CSV = OUT_DIR / "live_pnl_labeled_decisions_latest.csv"
POLICY_SCORE_JSON = EDGE_DIR / "v28_successor_live_pnl_policy_score_latest.json"
READINESS_JSON = EDGE_DIR / "v28_successor_live_pnl_readiness_latest.json"
SOURCE_CONTRACT_JSON = EDGE_DIR / "v28_successor_live_pnl_source_contract_latest.json"
CAPTURE_HEALTH_JSON = EDGE_DIR / "v28_successor_live_pnl_capture_health_latest.json"
FILL_MODEL_AUDIT_JSON = EDGE_DIR / "v28_successor_live_pnl_fill_model_audit_latest.json"
EXPERIMENT_LEDGER_CSV = EDGE_DIR / "v28_successor_live_pnl_policy_experiment_ledger_latest.csv"
POLICY_CYCLE_JSON = EDGE_DIR / "v28_successor_live_pnl_policy_cycle_latest.json"
VERIFIER_JSON = EDGE_DIR / "v28_successor_live_pnl_verifier_latest.json"
TEST_RUN_JSON = EDGE_DIR / "v28_successor_live_pnl_test_run_latest.json"

AUDIT_JSON = EDGE_DIR / "v28_successor_live_pnl_goal_completion_audit_latest.json"
AUDIT_MD = EDGE_DIR / "v28_successor_live_pnl_goal_completion_audit_latest.md"
AUDIT_CSV = EDGE_DIR / "v28_successor_live_pnl_goal_completion_audit_latest.csv"

MIN_PROFIT_GOAL_MARKETS = 5
MIN_PROFIT_GOAL_PRIMARY_ROWS = 75


def rel_path(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(ROOT)).replace("\\", "/")
    except ValueError:
        return str(path)


def iso_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def read_json(path: Path) -> Any | None:
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def read_csv_rows(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8", newline="") as handle:
        return [dict(row) for row in csv.DictReader(handle)]


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


def check_row(
    requirement_id: str,
    requirement: str,
    status: str,
    evidence: str,
    next_action: str,
) -> dict[str, Any]:
    return {
        "requirement_id": requirement_id,
        "requirement": requirement,
        "status": status,
        "evidence": evidence,
        "next_action": next_action,
    }


def run_tests(enabled: bool) -> dict[str, Any]:
    if not enabled:
        return {
            "status": "not_run",
            "command": f"{sys.executable} -m unittest test_v28_successor_live_pnl_policy_lab.py -v",
            "returncode": None,
            "stdout_tail": "",
            "stderr_tail": "",
        }
    completed = subprocess.run(
        [sys.executable, "-m", "unittest", "test_v28_successor_live_pnl_policy_lab.py", "-v"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        timeout=60,
        check=False,
    )
    return {
        "status": "pass" if completed.returncode == 0 else "fail",
        "command": " ".join([sys.executable, "-m", "unittest", "test_v28_successor_live_pnl_policy_lab.py", "-v"]),
        "returncode": completed.returncode,
        "stdout_tail": completed.stdout[-2000:],
        "stderr_tail": completed.stderr[-4000:],
    }


def build_checklist(*, test_result: dict[str, Any] | None = None) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    registry = read_csv_rows(POLICY_REGISTRY_CSV)
    labeled = read_csv_rows(LABELED_DECISIONS_CSV)
    score = read_json(POLICY_SCORE_JSON) or {}
    readiness = read_json(READINESS_JSON) or {}
    source_contract = read_json(SOURCE_CONTRACT_JSON) or {}
    capture_health = read_json(CAPTURE_HEALTH_JSON) or {}
    fill_model = read_json(FILL_MODEL_AUDIT_JSON) or {}
    cycle = read_json(POLICY_CYCLE_JSON) or {}
    verifier = read_json(VERIFIER_JSON) or {}
    experiment_ledger = read_csv_rows(EXPERIMENT_LEDGER_CSV)

    cycle_summary = cycle.get("summary", {}) if isinstance(cycle, dict) else {}
    score_summary = score.get("summary", {}) if isinstance(score, dict) else {}
    score_rows = score.get("scores", []) if isinstance(score, dict) else []
    source_guardrails = source_contract.get("research_only_guardrails", {}) if isinstance(source_contract, dict) else {}

    registry_rows = len(registry)
    policy_hashes = {row.get("policy_hash", "") for row in registry if row.get("policy_hash")}
    primary_policy_rows = sum(row.get("allowed_for_primary_live_pnl_evidence") == "True" for row in registry)
    joined_primary = [
        row
        for row in labeled
        if row.get("allowed_for_primary_live_pnl_evidence") == "True"
        and row.get("label_join_status") == "joined_post_resolution"
    ]
    joined_primary_rows = len(joined_primary)
    joined_primary_markets = len({row.get("market_ticker") for row in joined_primary if row.get("market_ticker")})
    primary_score = next(
        (
            row
            for row in score_rows
            if isinstance(row, dict) and row.get("slice") == "primary_live_forward_rows_after_policy_hash"
        ),
        {},
    )
    primary_net_cents = as_float(primary_score.get("net_pnl_cents"))
    primary_v28_net_cents = as_float(primary_score.get("v28_net_pnl_cents"))
    primary_delta_vs_v28_cents = as_float(primary_score.get("delta_net_cents_vs_v28"))
    primary_max_drawdown_cents = as_float(primary_score.get("max_drawdown_cents"))
    primary_entered_rows = as_int(primary_score.get("entered_rows"))
    primary_market_lcb_cents = as_float(primary_score.get("market_level_lcb_net_cents"))
    remove_best_1_market_net = primary_score.get("remove_best_1_market_net_pnl_cents")
    remove_best_1_market_ok = joined_primary_markets >= 2 and as_float(remove_best_1_market_net) > 0.0
    label_status_counts = Counter(row.get("label_join_status", "") for row in labeled)
    current_policy_failed = primary_entered_rows > 0 and (
        primary_net_cents <= 0.0 or primary_delta_vs_v28_cents < 0.0
    )
    failed_current_policy_marked = any(
        row.get("policy_hash") in policy_hashes
        and row.get("status") == "replace_required_failed_primary_forward_pnl"
        and row.get("decision") == "retire_or_replace_before_next_forward_credit"
        for row in experiment_ledger
    )
    denominator_fields_present = all(
        key in cycle_summary
        for key in [
            "registry_rows",
            "primary_policy_rows_after_hash",
            "primary_live_forward_rows_after_policy_hash",
            "diagnostic_rows_not_primary_credit",
        ]
    )
    paired_baseline_fields_present = bool(score_rows) and all(
        all(
            key in row
            for key in [
                "v28_net_pnl_cents",
                "successor_fv_only_net_pnl_cents",
                "book_only_net_pnl_cents",
                "always_skip_net_pnl_cents",
                "delta_net_cents_vs_v28",
                "delta_net_cents_vs_successor_fv_only",
                "delta_net_cents_vs_book_only",
                "delta_net_cents_vs_always_skip",
            ]
        )
        for row in score_rows
        if isinstance(row, dict)
    )
    source_guardrail_pass = bool(source_guardrails) and not any(bool(value) for value in source_guardrails.values())
    tests_pass = bool(test_result and test_result.get("status") == "pass")

    checklist = [
        check_row(
            "plan_file",
            "Workspace contains the full live-P&L plan/spec.",
            "pass" if PLAN_MD.exists() else "fail",
            rel_path(PLAN_MD),
            "Create docs/v28_successor_live_pnl_improvement_goal_plan.md.",
        ),
        check_row(
            "research_only_guardrails",
            "Live trading/order logic remains untouched; no orders/secrets/state mutations.",
            "pass" if source_guardrail_pass else "partial",
            rel_path(SOURCE_CONTRACT_JSON),
            "Inspect source contract and keep all live-order integration out of this goal.",
        ),
        check_row(
            "reproducible_pipeline",
            "A reproducible research-only live policy capture/scoring pipeline exists.",
            "pass" if POLICY_LAB_SCRIPT.exists() and POLICY_CYCLE_SCRIPT.exists() and registry_rows > 0 else "fail",
            f"{rel_path(POLICY_LAB_SCRIPT)}; {rel_path(POLICY_CYCLE_SCRIPT)}; rows={registry_rows}",
            "Run run_v28_successor_live_pnl_policy_cycle.py --write.",
        ),
        check_row(
            "frozen_policy_version",
            "At least one frozen inspectable policy version has a stable hash.",
            "pass" if len(policy_hashes) == 1 and bool(policy_hashes) else "fail",
            f"policy_hashes={sorted(policy_hashes)}",
            "Freeze exactly one active policy hash before collecting primary rows.",
        ),
        check_row(
            "pre_resolution_policy_rows",
            "Frozen pre-resolution policy rows exist for incoming live markets.",
            "pass" if primary_policy_rows > 0 else "partial" if registry_rows > 0 else "fail",
            f"registry_rows={registry_rows}; primary_policy_rows_after_hash={primary_policy_rows}",
            "Collect more public REST sidecar rows before close after the policy hash exists.",
        ),
        check_row(
            "post_resolution_labels",
            "Post-resolution labels are joined after settlement for primary rows.",
            "pass" if joined_primary_rows > 0 else "partial" if primary_policy_rows > 0 else "fail",
            f"joined_primary_rows={joined_primary_rows}; label_status_counts={dict(label_status_counts)}",
            "Rerun after the post-hash markets settle and labels are available.",
        ),
        check_row(
            "paired_pnl_comparison",
            "Same-row fee-aware comparison exists against regular v28, successor FV-only, book-only, and always-skip.",
            "pass"
            if score_summary.get("score_status") == "scored" and registry_rows > 0 and paired_baseline_fields_present
            else "fail",
            rel_path(POLICY_SCORE_JSON),
            "Rebuild live-P&L policy score artifacts with all paired baselines.",
        ),
        check_row(
            "bootstrap_sample_floor",
            "Bootstrap sample floor: at least 25 finalized paired opportunities.",
            "pass" if joined_primary_rows >= 25 else "fail",
            f"joined_primary_markets={joined_primary_markets}; joined_primary_rows={joined_primary_rows}",
            "Continue collecting until enough post-hash rows are finalized and labeled.",
        ),
        check_row(
            "profit_goal_market_coverage",
            f"Profit goal coverage: at least {MIN_PROFIT_GOAL_MARKETS} finalized live close windows.",
            "pass" if joined_primary_markets >= MIN_PROFIT_GOAL_MARKETS else "fail",
            f"joined_primary_markets={joined_primary_markets}",
            "Continue collecting across more finalized BTC15M close windows.",
        ),
        check_row(
            "profit_goal_row_floor",
            f"Profit goal row floor: at least {MIN_PROFIT_GOAL_PRIMARY_ROWS} post-hash labeled primary opportunities.",
            "pass" if joined_primary_rows >= MIN_PROFIT_GOAL_PRIMARY_ROWS else "fail",
            f"joined_primary_rows={joined_primary_rows}",
            "Continue collecting post-hash primary opportunities.",
        ),
        check_row(
            "positive_net_pnl",
            "Candidate must have positive fee-aware one-contract net P&L on primary rows.",
            "partial"
            if joined_primary_rows <= 0 or primary_entered_rows <= 0
            else "pass"
            if primary_net_cents > 0
            else "fail",
            f"primary_net_pnl_cents={primary_net_cents}",
            "Collect settled primary rows, then retire or replace candidates with non-positive live-forward P&L.",
        ),
        check_row(
            "positive_delta_vs_v28",
            "Candidate must beat regular v28 on the same primary rows.",
            "partial"
            if joined_primary_rows <= 0 or primary_entered_rows <= 0
            else "pass"
            if primary_delta_vs_v28_cents > 0
            else "fail",
            f"policy_net={primary_net_cents}; v28_net={primary_v28_net_cents}; delta={primary_delta_vs_v28_cents}",
            "Do not advance candidates that merely match v28.",
        ),
        check_row(
            "drawdown_control",
            "Drawdown/loss clustering must be acceptable relative to realized edge.",
            "partial"
            if joined_primary_rows <= 0 or primary_entered_rows <= 0
            else "pass"
            if primary_net_cents > 0 and primary_max_drawdown_cents <= max(primary_net_cents * 2.0, 1.0)
            else "fail",
            f"primary_net={primary_net_cents}; max_drawdown_cents={primary_max_drawdown_cents}",
            "Reject or redesign candidates whose drawdown is large while net edge is absent.",
        ),
        check_row(
            "not_single_market_dependent",
            "Profit must not be driven by one market or one lucky slice.",
            "pass" if remove_best_1_market_ok and primary_market_lcb_cents > 0 else "fail",
            f"markets={joined_primary_markets}; remove_best_1_market_net={remove_best_1_market_net}; market_lcb={primary_market_lcb_cents}",
            "Collect more markets and require positive market-level robustness.",
        ),
        check_row(
            "failed_candidate_retirement",
            "A candidate that fails early live-forward P&L or negative delta is retired or marked replace-required; zero-delta candidates remain blocked from promotion until positive delta appears.",
            "pass"
            if not current_policy_failed or failed_current_policy_marked
            else "fail",
            (
                f"current_failed={current_policy_failed}; marked={failed_current_policy_marked}; "
                f"entered={primary_entered_rows}; primary_net={primary_net_cents}; "
                f"delta_vs_v28={primary_delta_vs_v28_cents}"
            ),
            "If the current policy fails, mark it replace-required and freeze a replacement only for future rows.",
        ),
        check_row(
            "denominator_reporting",
            "Observed/eligible/entered/skipped/missed/unscorable denominators are reported.",
            "pass" if denominator_fields_present and capture_health else "partial",
            f"{rel_path(POLICY_CYCLE_JSON)}; {rel_path(CAPTURE_HEALTH_JSON)}",
            "Keep cycle and capture-health reports current.",
        ),
        check_row(
            "source_quality",
            "Source-quality verification exists for policy rows.",
            "pass" if source_contract.get("contract_status") else "fail",
            rel_path(SOURCE_CONTRACT_JSON),
            "Rebuild live-P&L source contract.",
        ),
        check_row(
            "capture_health",
            "Capture-health evidence accounts for missed rows and current row growth.",
            "pass" if capture_health.get("capture_health_status") else "fail",
            rel_path(CAPTURE_HEALTH_JSON),
            "Refresh the live-P&L cycle after collection.",
        ),
        check_row(
            "fill_model_audit",
            "Fill-model audit or explicit assumptions report exists.",
            "pass" if fill_model.get("fill_model_status") else "fail",
            rel_path(FILL_MODEL_AUDIT_JSON),
            "Refresh fill-model audit and verify fees before live testing.",
        ),
        check_row(
            "tests",
            "Tests cover causality, fee math, policy hash freezing, and no retroactive credit.",
            "pass" if tests_pass else "partial" if TEST_FILE.exists() else "fail",
            test_result.get("command", rel_path(TEST_FILE)) if test_result else rel_path(TEST_FILE),
            "Run audit with --run-tests or run python -m unittest test_v28_successor_live_pnl_policy_lab.py -v.",
        ),
        check_row(
            "experiment_ledger",
            "Experiment ledger includes active/retired policies and decisions.",
            "pass" if len(experiment_ledger) >= 1 else "fail",
            rel_path(EXPERIMENT_LEDGER_CSV),
            "Write the policy experiment ledger.",
        ),
        check_row(
            "bootstrap_report",
            "Bootstrap report says continue, retire, or replace the first policy.",
            "pass" if readiness.get("readiness_verdict") else "fail",
            rel_path(READINESS_JSON),
            "Refresh readiness report.",
        ),
        check_row(
            "readiness_consistency",
            "The dedicated readiness artifact is fresh and does not authorize controlled live use.",
            "pass" if readiness.get("level_2_controlled_live_test_ready") is False else "fail",
            f"readiness_level_1_complete={readiness.get('level_1_complete')}; level_2={readiness.get('level_2_controlled_live_test_ready')}; verdict={readiness.get('readiness_verdict')}",
            "Keep controlled-live-test readiness false until profitable forward evidence passes.",
        ),
        check_row(
            "no_promotion_without_forward_evidence",
            "No candidate is advanced/promoted before forward evidence improves all gates.",
            "pass" if verifier.get("no_retroactive_credit_enforced") is True and not readiness.get("level_2_controlled_live_test_ready") else "partial",
            f"{rel_path(VERIFIER_JSON)}; level_2={readiness.get('level_2_controlled_live_test_ready')}",
            "Keep controlled-live-test authorization false until Level 2 gates pass.",
        ),
    ]
    status_counts = Counter(row["status"] for row in checklist)
    complete = all(row["status"] == "pass" for row in checklist)
    summary = {
        "generated_utc": iso_now(),
        "overall_status": "complete" if complete else "incomplete",
        "profit_goal_complete": complete,
        "legacy_level_1_bootstrap_complete": bool(readiness.get("level_1_complete")),
        "status_counts": dict(status_counts),
        "registry_rows": registry_rows,
        "primary_policy_rows_after_hash": primary_policy_rows,
        "joined_primary_rows": joined_primary_rows,
        "joined_primary_markets": joined_primary_markets,
        "primary_entered_rows": primary_entered_rows,
        "primary_net_pnl_cents": primary_net_cents,
        "primary_v28_net_pnl_cents": primary_v28_net_cents,
        "primary_delta_vs_v28_cents": primary_delta_vs_v28_cents,
        "primary_max_drawdown_cents": primary_max_drawdown_cents,
        "profit_goal_min_markets": MIN_PROFIT_GOAL_MARKETS,
        "profit_goal_min_primary_rows": MIN_PROFIT_GOAL_PRIMARY_ROWS,
        "readiness_verdict": readiness.get("readiness_verdict", ""),
        "cycle_status": cycle_summary.get("cycle_status", ""),
        "test_result": test_result or {"status": "not_run"},
        "artifacts": {
            "plan": rel_path(PLAN_MD),
            "policy_registry": rel_path(POLICY_REGISTRY_CSV),
            "labeled_decisions": rel_path(LABELED_DECISIONS_CSV),
            "policy_score": rel_path(POLICY_SCORE_JSON),
            "readiness": rel_path(READINESS_JSON),
            "cycle": rel_path(POLICY_CYCLE_JSON),
        },
    }
    return checklist, summary


def write_outputs(checklist: list[dict[str, Any]], summary: dict[str, Any]) -> None:
    EDGE_DIR.mkdir(parents=True, exist_ok=True)
    AUDIT_JSON.write_text(
        json.dumps({"summary": summary, "checklist": checklist}, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    with AUDIT_CSV.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=["requirement_id", "requirement", "status", "evidence", "next_action"],
        )
        writer.writeheader()
        writer.writerows(checklist)
    lines = [
        "# v28 Successor Live P&L Goal Completion Audit",
        "",
        f"- Overall status: `{summary['overall_status']}`",
        f"- Profit goal complete: `{summary['profit_goal_complete']}`",
        f"- Legacy Level 1 bootstrap complete: `{summary['legacy_level_1_bootstrap_complete']}`",
        f"- Cycle status: `{summary['cycle_status']}`",
        f"- Registry rows: `{summary['registry_rows']}`",
        f"- Primary policy rows after hash: `{summary['primary_policy_rows_after_hash']}`",
        f"- Joined primary rows: `{summary['joined_primary_rows']}`",
        f"- Joined primary markets: `{summary['joined_primary_markets']}`",
        f"- Primary net P&L cents: `{summary['primary_net_pnl_cents']}`",
        f"- Primary delta vs v28 cents: `{summary['primary_delta_vs_v28_cents']}`",
        "",
        "| id | status | evidence | next action |",
        "|---|---|---|---|",
    ]
    for item in checklist:
        lines.append(
            f"| `{item['requirement_id']}` | `{item['status']}` | `{item['evidence']}` | {item['next_action']} |"
        )
    AUDIT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--run-tests", action="store_true")
    args = parser.parse_args()
    test_result = run_tests(args.run_tests)
    if args.write:
        EDGE_DIR.mkdir(parents=True, exist_ok=True)
        TEST_RUN_JSON.write_text(json.dumps(test_result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    checklist, summary = build_checklist(test_result=test_result)
    if args.write:
        write_outputs(checklist, summary)
    print(
        json.dumps(
            {
                "overall_status": summary["overall_status"],
                "profit_goal_complete": summary["profit_goal_complete"],
                "legacy_level_1_bootstrap_complete": summary["legacy_level_1_bootstrap_complete"],
                "registry_rows": summary["registry_rows"],
                "primary_policy_rows_after_hash": summary["primary_policy_rows_after_hash"],
                "joined_primary_rows": summary["joined_primary_rows"],
                "joined_primary_markets": summary["joined_primary_markets"],
                "primary_net_pnl_cents": summary["primary_net_pnl_cents"],
                "primary_delta_vs_v28_cents": summary["primary_delta_vs_v28_cents"],
                "test_status": summary["test_result"]["status"],
                "written": bool(args.write),
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
