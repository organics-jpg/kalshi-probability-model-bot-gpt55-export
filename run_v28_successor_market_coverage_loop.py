"""Run repeated research-only sidecar coverage cycles for v28 successor evidence.

This is an operator convenience wrapper around the existing sidecar collection
cycle plus the canonical forward-evidence refresh:

1. optionally collect public REST BTC15M sidecar bundles before close;
2. freeze/label/score sidecar batch evidence;
3. stage valid frozen rows into the canonical forward ledger;
4. refresh registry, label join, evidence score, source contract, verifier, and
   goal audit reports.

The default collection mode is ``none``. Use ``--collect-mode public-rest``
explicitly for public market/book/BTC capture. This script never touches live
bot state, secrets, thresholds, orders, or processes.
"""
from __future__ import annotations

import argparse
import json
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from audit_v28_successor_forward_source_readiness import build as build_forward_source_readiness
from audit_v28_successor_forward_source_readiness import write_outputs as write_forward_source_readiness_outputs
from audit_v28_successor_goal_completion import build_checklist as build_goal_completion_checklist
from audit_v28_successor_goal_completion import write_outputs as write_goal_completion_outputs
from join_v28_successor_forward_labels import build as build_forward_label_join
from join_v28_successor_forward_labels import write_outputs as write_forward_label_join_outputs
from register_v28_successor_forward_predictions import build_registry_rows
from register_v28_successor_forward_predictions import write_outputs as write_forward_registry_outputs
from run_v28_successor_research_pipeline import run_pipeline
from run_v28_successor_research_pipeline import write_outputs as write_pipeline_outputs
from run_v28_successor_sidecar_collection_cycle import run_cycle
from run_v28_successor_sidecar_collection_cycle import write_outputs as write_cycle_outputs
from score_v28_successor_forward_evidence import build as build_forward_evidence_score
from score_v28_successor_forward_evidence import write_outputs as write_forward_evidence_outputs
from stage_v28_successor_sidecar_forward_evidence import build as build_sidecar_forward_stage
from stage_v28_successor_sidecar_forward_evidence import write_outputs as write_sidecar_forward_stage_outputs
from validate_v28_successor_source_contract import build as build_source_contract
from validate_v28_successor_source_contract import write_outputs as write_source_contract_outputs
from verify_v28_successor_promotion import build as build_promotion_verifier
from verify_v28_successor_promotion import write_outputs as write_promotion_verifier_outputs


ROOT = Path(__file__).resolve().parent
EDGE_DIR = ROOT / "logs" / "edge_research"

LOOP_JSON = EDGE_DIR / "v28_successor_market_coverage_loop_latest.json"
LOOP_MD = EDGE_DIR / "v28_successor_market_coverage_loop_latest.md"

MIN_FORWARD_ROWS = 200
MIN_FORWARD_MARKETS = 40
SAMPLE_ONLY_FAIL_REASONS = {"insufficient_forward_rows", "insufficient_forward_markets"}

RESEARCH_ONLY_GUARDRAILS = [
    "does not start or stop live bot processes",
    "does not read or write secrets",
    "does not place orders",
    "does not mutate live thresholds or order logic",
    "uses only the sidecar/public-data research path when collection is explicit",
    "keeps promotion_allowed false unless the downstream verifier eventually passes",
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
        return int(value or 0)
    except (TypeError, ValueError):
        return 0


def target_met(summary: dict[str, Any], *, target_clean_rows: int, target_clean_markets: int) -> bool:
    return (
        as_int(summary.get("clean_forward_rows")) >= target_clean_rows
        and as_int(summary.get("clean_forward_markets")) >= target_clean_markets
    )


def summarize_candidate_forward_gates(summary: dict[str, Any]) -> dict[str, Any]:
    gates = list(summary.get("candidate_gates") or [])
    if not gates:
        return {
            "candidate_gate_count": 0,
            "candidate_forward_sample_floor_met": False,
            "candidate_forward_promotable": False,
            "best_candidate_id_by_sample_shortfall": None,
            "best_candidate_rows": 0,
            "best_candidate_markets": 0,
            "best_candidate_row_shortfall": 0,
            "best_candidate_market_shortfall": 0,
            "best_candidate_estimated_additional_markets_needed": 0,
            "sample_only_candidate_count": 0,
            "best_sample_only_candidate_id": None,
            "best_sample_only_candidate_rows": 0,
            "best_sample_only_candidate_markets": 0,
            "best_sample_only_candidate_row_shortfall": 0,
            "best_sample_only_candidate_market_shortfall": 0,
            "best_sample_only_candidate_estimated_additional_markets_needed": 0,
        }

    def sort_key(gate: dict[str, Any]) -> tuple[int, int, int, str]:
        return (
            as_int(gate.get("estimated_additional_markets_needed")),
            as_int(gate.get("market_shortfall")),
            as_int(gate.get("row_shortfall")),
            str(gate.get("candidate_id") or ""),
        )

    best = sorted(gates, key=sort_key)[0]
    sample_only = [
        gate
        for gate in gates
        if set(gate.get("fail_reasons") or []).issubset(SAMPLE_ONLY_FAIL_REASONS)
        and (
            as_int(gate.get("row_shortfall")) > 0
            or as_int(gate.get("market_shortfall")) > 0
        )
    ]
    best_sample_only = sorted(sample_only, key=sort_key)[0] if sample_only else {}
    sample_floor_met = any(
        as_int(gate.get("row_shortfall")) == 0 and as_int(gate.get("market_shortfall")) == 0
        for gate in gates
    )
    return {
        "candidate_gate_count": len(gates),
        "candidate_forward_sample_floor_met": sample_floor_met,
        "candidate_forward_promotable": any(bool(gate.get("forward_evidence_promotable")) for gate in gates),
        "best_candidate_id_by_sample_shortfall": best.get("candidate_id"),
        "best_candidate_rows": as_int(best.get("rows")),
        "best_candidate_markets": as_int(best.get("markets")),
        "best_candidate_row_shortfall": as_int(best.get("row_shortfall")),
        "best_candidate_market_shortfall": as_int(best.get("market_shortfall")),
        "best_candidate_estimated_additional_markets_needed": as_int(
            best.get("estimated_additional_markets_needed")
        ),
        "sample_only_candidate_count": len(sample_only),
        "best_sample_only_candidate_id": best_sample_only.get("candidate_id"),
        "best_sample_only_candidate_rows": as_int(best_sample_only.get("rows")),
        "best_sample_only_candidate_markets": as_int(best_sample_only.get("markets")),
        "best_sample_only_candidate_row_shortfall": as_int(best_sample_only.get("row_shortfall")),
        "best_sample_only_candidate_market_shortfall": as_int(best_sample_only.get("market_shortfall")),
        "best_sample_only_candidate_estimated_additional_markets_needed": as_int(
            best_sample_only.get("estimated_additional_markets_needed")
        ),
    }


def canonical_refresh(*, write: bool) -> dict[str, Any]:
    staged_rows, stage_summary = build_sidecar_forward_stage()
    if write:
        write_sidecar_forward_stage_outputs(staged_rows, stage_summary)

    registry_rows, registry_summary = build_registry_rows()
    if write:
        write_forward_registry_outputs(registry_rows, registry_summary)

    labeled_rows, label_summary = build_forward_label_join()
    if write:
        write_forward_label_join_outputs(labeled_rows, label_summary)

    metrics, bins, evidence_summary = build_forward_evidence_score()
    if write:
        write_forward_evidence_outputs(metrics, bins, evidence_summary)
    candidate_gate_summary = summarize_candidate_forward_gates(evidence_summary)

    source_rows, source_summary = build_source_contract()
    if write:
        write_source_contract_outputs(source_rows, source_summary)

    readiness_report, readiness_summary = build_forward_source_readiness()
    if write:
        write_forward_source_readiness_outputs(readiness_report, readiness_summary)

    verifier_rows, verifier_summary = build_promotion_verifier()
    if write:
        write_promotion_verifier_outputs(verifier_rows, verifier_summary)

    goal_checks, goal_summary = build_goal_completion_checklist()
    if write:
        write_goal_completion_outputs(goal_checks, goal_summary)

    return {
        "stage_status": stage_summary.get("stage_status"),
        "frozen_prediction_rows": as_int(stage_summary.get("frozen_prediction_rows")),
        "frozen_prediction_markets": as_int(stage_summary.get("frozen_prediction_markets")),
        "registry_rows": as_int(registry_summary.get("row_count")),
        "registry_markets": as_int(registry_summary.get("market_count")),
        "joined_rows": as_int(label_summary.get("joined_rows")),
        "joined_markets": as_int(label_summary.get("joined_markets")),
        "clean_forward_rows": as_int(evidence_summary.get("clean_forward_rows")),
        "clean_forward_markets": as_int(evidence_summary.get("clean_forward_markets")),
        "promotable_candidate_count": as_int(evidence_summary.get("promotable_candidate_count")),
        **candidate_gate_summary,
        "source_contract_verdict": source_summary.get("overall_verdict"),
        "source_contract_ready": bool(source_summary.get("promotion_contract_ready")),
        "required_forward_hard_blockers": source_summary.get("required_forward_hard_blockers") or [],
        "promotion_verdict": verifier_summary.get("overall_verdict"),
        "goal_status": goal_summary.get("overall_status"),
    }


def run_loop(
    *,
    collect_mode: str,
    nearest_close_only: bool,
    iterations: int,
    sleep_seconds: float,
    timeout_seconds: float,
    max_markets: int,
    target_clean_rows: int,
    target_clean_markets: int,
    stop_when_target_met: bool,
    write: bool,
    dry_run: bool,
    run_full_pipeline_at_end: bool,
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
            "nearest_close_only": nearest_close_only,
            "collection_scope": "nearest_close" if nearest_close_only else "all_open_closes",
            "iterations_requested": iterations,
            "iterations_run": 0,
            "target_clean_rows": target_clean_rows,
            "target_clean_markets": target_clean_markets,
            "target_met": False,
            "promotion_allowed": False,
            "research_only_guardrails": RESEARCH_ONLY_GUARDRAILS,
            "iterations": iteration_reports,
            "outputs": {"json": rel_path(LOOP_JSON), "markdown": rel_path(LOOP_MD)},
        }

    last_refresh: dict[str, Any] = {}
    for index in range(iterations):
        if index and sleep_seconds > 0:
            time.sleep(sleep_seconds)

        cycle_report = run_cycle(
            collect_mode=collect_mode,
            timeout_seconds=timeout_seconds,
            max_markets=max_markets,
            nearest_close_only=nearest_close_only,
            write=write,
        )
        if write:
            write_cycle_outputs(cycle_report)

        refresh_summary = canonical_refresh(write=write)
        last_refresh = refresh_summary
        iteration_report = {
            "iteration": index + 1,
            "generated_utc": iso_z(),
            "cycle_status": cycle_report["summary"].get("cycle_status"),
            "collect_mode": collect_mode,
            "cycle_frozen_rows": cycle_report["summary"].get("sidecar_frozen_rows"),
            "cycle_frozen_markets": cycle_report["summary"].get("sidecar_frozen_markets"),
            "cycle_clean_rows": cycle_report["summary"].get("sidecar_clean_forward_rows"),
            "cycle_clean_markets": cycle_report["summary"].get("sidecar_clean_forward_markets"),
            "canonical": refresh_summary,
            "candidate_forward_sample_floor_met": refresh_summary.get("candidate_forward_sample_floor_met"),
            "best_candidate_id_by_sample_shortfall": refresh_summary.get("best_candidate_id_by_sample_shortfall"),
            "best_candidate_estimated_additional_markets_needed": refresh_summary.get(
                "best_candidate_estimated_additional_markets_needed"
            ),
            "best_sample_only_candidate_id": refresh_summary.get("best_sample_only_candidate_id"),
            "best_sample_only_candidate_estimated_additional_markets_needed": refresh_summary.get(
                "best_sample_only_candidate_estimated_additional_markets_needed"
            ),
            "target_met": target_met(
                refresh_summary,
                target_clean_rows=target_clean_rows,
                target_clean_markets=target_clean_markets,
            ),
        }
        iteration_reports.append(iteration_report)
        if stop_when_target_met and iteration_report["target_met"]:
            loop_status = "target_met"
            break

    final_pipeline_summary: dict[str, Any] | None = None
    if run_full_pipeline_at_end:
        manifest = run_pipeline(dry_run=False, stop_on_fail=True, timeout_seconds=240)
        if write:
            write_pipeline_outputs(manifest)
        final_pipeline_summary = {
            "pipeline_status": manifest.get("pipeline_status"),
            "steps_run": manifest.get("steps_run"),
            "step_count": manifest.get("step_count"),
            "failed_steps": manifest.get("failed_steps"),
        }
        if manifest.get("pipeline_status") != "pass":
            loop_status = "completed_with_pipeline_failure"

    return {
        "generated_utc": iso_z(),
        "started_utc": started,
        "loop_status": loop_status,
        "collect_mode": collect_mode,
        "nearest_close_only": nearest_close_only,
        "collection_scope": "nearest_close" if nearest_close_only else "all_open_closes",
        "iterations_requested": iterations,
        "iterations_run": len(iteration_reports),
        "target_clean_rows": target_clean_rows,
        "target_clean_markets": target_clean_markets,
        "target_met": bool(iteration_reports and iteration_reports[-1]["target_met"]),
        "promotion_allowed": False,
        "final_canonical": last_refresh,
        "final_pipeline": final_pipeline_summary,
        "research_only_guardrails": RESEARCH_ONLY_GUARDRAILS,
        "iterations": iteration_reports,
        "outputs": {"json": rel_path(LOOP_JSON), "markdown": rel_path(LOOP_MD)},
    }


def write_markdown(report: dict[str, Any], path: Path) -> None:
    lines = [
        "# v28 Successor Market Coverage Loop",
        "",
        "Research-only repeated sidecar coverage runner. This report does not touch live bot state, orders, thresholds, secrets, or processes.",
        "",
        "## Summary",
        "",
        f"- Generated UTC: `{report['generated_utc']}`",
        f"- Loop status: `{report['loop_status']}`",
        f"- Collect mode: `{report['collect_mode']}`",
        f"- Collection scope: `{report['collection_scope']}`",
        f"- Iterations run: `{report['iterations_run']}` / `{report['iterations_requested']}`",
        f"- Target clean rows / markets: `{report['target_clean_rows']}` / `{report['target_clean_markets']}`",
        f"- Target met: `{report['target_met']}`",
        f"- Promotion allowed: `{report['promotion_allowed']}`",
        "",
        "## Final Canonical State",
        "",
    ]
    final = report.get("final_canonical") or {}
    if final:
        for key in [
            "frozen_prediction_rows",
            "frozen_prediction_markets",
            "joined_rows",
            "joined_markets",
            "clean_forward_rows",
            "clean_forward_markets",
            "promotable_candidate_count",
            "candidate_gate_count",
            "candidate_forward_sample_floor_met",
            "best_candidate_id_by_sample_shortfall",
            "best_candidate_rows",
            "best_candidate_markets",
            "best_candidate_row_shortfall",
            "best_candidate_market_shortfall",
            "best_candidate_estimated_additional_markets_needed",
            "sample_only_candidate_count",
            "best_sample_only_candidate_id",
            "best_sample_only_candidate_rows",
            "best_sample_only_candidate_markets",
            "best_sample_only_candidate_row_shortfall",
            "best_sample_only_candidate_market_shortfall",
            "best_sample_only_candidate_estimated_additional_markets_needed",
            "source_contract_verdict",
            "required_forward_hard_blockers",
            "promotion_verdict",
            "goal_status",
        ]:
            lines.append(f"- {key}: `{final.get(key)}`")
    else:
        lines.append("- No canonical refresh was run.")
    if report.get("final_pipeline"):
        lines.extend(["", "## Final Pipeline", ""])
        for key, value in report["final_pipeline"].items():
            lines.append(f"- {key}: `{value}`")
    lines.extend(
        [
            "",
            "## Iterations",
            "",
            "| iteration | cycle status | frozen rows | clean rows | clean markets | best candidate | addl markets needed | candidate floor met | target met |",
            "|---:|---|---:|---:|---:|---|---:|---:|---:|",
        ]
    )
    for item in report["iterations"]:
        canonical = item.get("canonical") or {}
        lines.append(
            f"| {item['iteration']} | `{item['cycle_status']}` | "
            f"{canonical.get('frozen_prediction_rows')} | {canonical.get('clean_forward_rows')} | "
            f"{canonical.get('clean_forward_markets')} | "
            f"`{item.get('best_sample_only_candidate_id') or item.get('best_candidate_id_by_sample_shortfall')}` | "
            f"{item.get('best_sample_only_candidate_estimated_additional_markets_needed') if item.get('best_sample_only_candidate_id') else item.get('best_candidate_estimated_additional_markets_needed')} | "
            f"{item.get('candidate_forward_sample_floor_met')} | {item.get('target_met')} |"
        )
    lines.extend(
        [
            "",
            "## Read",
            "",
            "- The loop is an evidence collector, not a promotion path.",
            "- Use `--collect-mode public-rest` only when public market capture is intended.",
            "- Use `--all-open-closes` only when intentionally broadening the forward evidence population beyond the nearest close.",
            "- Promotion still requires source contract, market coverage, candidate evidence, and verifier approval.",
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
    parser.add_argument(
        "--all-open-closes",
        action="store_true",
        help="When collecting public REST rows, collect all open BTC15M closes returned by the API instead of only the nearest close.",
    )
    parser.add_argument("--target-clean-rows", type=int, default=MIN_FORWARD_ROWS)
    parser.add_argument("--target-clean-markets", type=int, default=MIN_FORWARD_MARKETS)
    parser.add_argument("--stop-when-target-met", action="store_true")
    parser.add_argument("--run-full-pipeline-at-end", action="store_true")
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
        target_clean_rows=args.target_clean_rows,
        target_clean_markets=args.target_clean_markets,
        stop_when_target_met=args.stop_when_target_met,
        write=bool(args.write and not args.dry_run),
        dry_run=args.dry_run,
        run_full_pipeline_at_end=args.run_full_pipeline_at_end,
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
                "target_met": report["target_met"],
                "final_canonical": report.get("final_canonical") or {},
                "final_pipeline": report.get("final_pipeline"),
                "promotion_allowed": report["promotion_allowed"],
                "written": bool(args.write and not args.dry_run),
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
