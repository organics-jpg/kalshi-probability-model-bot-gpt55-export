"""Run the v28 successor research pipeline in dependency order.

Research-only. This runner executes the local artifact builders sequentially so
reports cannot race each other while writing/reading shared latest files. It
does not start, stop, inspect, or mutate the live bot process, live state,
secrets, thresholds, or order logic.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "research_particle" / "v28_successor"
EDGE_DIR = ROOT / "logs" / "edge_research"

PIPELINE_MANIFEST_JSON = EDGE_DIR / "v28_successor_pipeline_run_latest.json"
PIPELINE_MANIFEST_MD = EDGE_DIR / "v28_successor_pipeline_run_latest.md"

RESEARCH_ONLY_GUARDRAILS = [
    "does not start or stop live bot processes",
    "does not read or write secrets",
    "does not place orders",
    "does not mutate live thresholds or order logic",
    "runs local research artifact builders sequentially",
]


@dataclass(frozen=True)
class Step:
    step_id: str
    script: str
    args: tuple[str, ...] = ("--write",)
    purpose: str = ""

    def command(self) -> list[str]:
        if self.script == "-m":
            return [sys.executable, "-m", *self.args]
        return [sys.executable, str(ROOT / self.script), *self.args]


PIPELINE_STEPS: tuple[Step, ...] = (
    Step("seed_dataset", "build_v28_successor_causal_dataset.py", purpose="canonical posthoc diagnostic seed rows"),
    Step("baseline_replay", "replay_v28_successor_baselines.py", purpose="audit logged/recomputed v28 baseline availability"),
    Step("logged_event_dataset", "build_v28_successor_logged_event_dataset.py", purpose="logged v28 event diagnostic rows"),
    Step("logged_event_api_replay", "replay_v28_successor_logged_event_api.py", purpose="research-only v28 component replay"),
    Step("seed_features", "build_v28_successor_features.py", purpose="leakage-safe seed feature table"),
    Step("logged_event_features", "build_v28_successor_logged_event_features.py", purpose="richer logged-event feature table"),
    Step("seed_candidates", "train_v28_successor_candidates.py", purpose="simple inspectable seed challengers"),
    Step("logged_event_candidates", "train_v28_successor_logged_event_candidates.py", purpose="simple inspectable logged-event challengers"),
    Step("passive_forward_snapshots", "build_v28_successor_passive_forward_snapshots.py", purpose="passive book staging rows"),
    Step("forward_packet_contract", "validate_v28_successor_forward_packet.py", purpose="packet contract validation"),
    Step("shadow_forward_packets", "build_v28_successor_shadow_forward_packets.py", purpose="paired shadow packet bridge"),
    Step("forward_packet_scoring", "score_v28_successor_forward_packets.py", purpose="score packet-shaped rows with collection candidates"),
    Step("forward_packet_adapter", "build_v28_successor_forward_packet_adapter.py", purpose="sidecar packet adapter fixture"),
    Step("public_rest_sidecar_bundle", "build_v28_successor_public_rest_sidecar_bundle.py", purpose="one-shot public REST sidecar bundle builder fixture"),
    Step("public_rest_sidecar_batch", "build_v28_successor_public_rest_sidecar_batch.py", purpose="batch public REST sidecar bundle builder fixture"),
    Step("sidecar_bundle_replay", "replay_v28_successor_sidecar_bundles.py", purpose="replay recorded sidecar market/book/BTC bundles through v28"),
    Step("sidecar_input_bundle_contract", "validate_v28_successor_sidecar_input_bundle.py", purpose="sidecar input bundle template and contract"),
    Step("sidecar_packet_collector", "collect_v28_successor_forward_packets.py", purpose="sidecar packet collector contract fixture"),
    Step("sidecar_bundle_freeze_handoff", "run_v28_successor_sidecar_bundle_freeze_handoff.py", purpose="bundle-to-freeze one-command handoff"),
    Step("sidecar_bundle_batch_handoff", "run_v28_successor_sidecar_bundle_batch_handoff.py", purpose="batch bundle-to-freeze handoff"),
    Step("sidecar_bundle_batch_settlement_labels", "fetch_v28_successor_sidecar_batch_settlement_labels.py", purpose="post-close settlement labels for sidecar batch frozen rows"),
    Step("sidecar_bundle_batch_label_join", "run_v28_successor_sidecar_batch_label_join_handoff.py", purpose="post-resolution label join for sidecar batch frozen rows"),
    Step("sidecar_batch_evidence_score", "score_v28_successor_sidecar_batch_evidence.py", purpose="probability-first scoring for sidecar batch evidence"),
    Step(
        "sidecar_collection_cycle",
        "run_v28_successor_sidecar_collection_cycle.py",
        args=("--write", "--collect-mode", "none"),
        purpose="one-cycle sidecar freeze/label/score/audit refresh without new public capture",
    ),
    Step(
        "live_pnl_policy_cycle",
        "run_v28_successor_live_pnl_policy_cycle.py",
        args=("--write", "--collect-mode", "none", "--skip-downstream-audits"),
        purpose="research-only live-P&L policy registry/label/score/readiness refresh",
    ),
    Step(
        "live_pnl_goal_completion_audit",
        "audit_v28_successor_live_pnl_goal_completion.py",
        args=("--write",),
        purpose="strict prompt-to-artifact audit for the live-P&L goal",
    ),
    Step("forward_packet_freeze_handoff", "run_v28_successor_forward_packet_freeze.py", purpose="validate/freeze/register sidecar packet handoff"),
    Step("forward_freeze_preflight", "preflight_v28_successor_forward_freeze.py", purpose="freeze readiness preflight"),
    Step("freeze_forward_candidates", "freeze_v28_successor_forward_candidates.py", purpose="strict frozen prediction ledger"),
    Step("stage_sidecar_forward_evidence", "stage_v28_successor_sidecar_forward_evidence.py", purpose="stage valid sidecar frozen rows as canonical forward evidence inputs"),
    Step("forward_registry", "register_v28_successor_forward_predictions.py", purpose="register strict frozen prediction ledger"),
    Step("forward_label_join", "join_v28_successor_forward_labels.py", purpose="post-resolution label join"),
    Step("forward_evidence_score", "score_v28_successor_forward_evidence.py", purpose="settled forward candidate-vs-v28 score"),
    Step("source_contract", "validate_v28_successor_source_contract.py", purpose="source-quality contract"),
    Step("forward_source_readiness", "audit_v28_successor_forward_source_readiness.py", purpose="source coverage and joinability audit"),
    Step("promotion_verifier", "verify_v28_successor_promotion.py", purpose="strict promotion verifier"),
    Step("forward_collection_spec", "build_v28_successor_forward_collection_spec.py", purpose="future collection handoff"),
    Step("goal_completion_audit", "audit_v28_successor_goal_completion.py", purpose="objective completion audit"),
    Step("unit_tests", "-m", args=("unittest", "test_v28_successor_pipeline.py"), purpose="pipeline invariant tests"),
)

KEY_ARTIFACTS = [
    EDGE_DIR / "v28_successor_goal_completion_audit_latest.json",
    EDGE_DIR / "v28_successor_source_contract_latest.json",
    EDGE_DIR / "v28_successor_forward_source_readiness_latest.json",
    EDGE_DIR / "v28_successor_promotion_verifier_latest.json",
    EDGE_DIR / "v28_successor_forward_registry_latest.json",
    EDGE_DIR / "v28_successor_forward_evidence_score_latest.json",
    EDGE_DIR / "v28_successor_forward_label_join_latest.json",
    EDGE_DIR / "v28_successor_forward_packet_adapter_latest.json",
    EDGE_DIR / "v28_successor_public_rest_sidecar_bundle_latest.json",
    EDGE_DIR / "v28_successor_public_rest_sidecar_batch_latest.json",
    EDGE_DIR / "v28_successor_sidecar_bundle_replay_latest.json",
    EDGE_DIR / "v28_successor_sidecar_input_bundle_contract_latest.json",
    EDGE_DIR / "v28_successor_sidecar_packet_collector_latest.json",
    EDGE_DIR / "v28_successor_sidecar_bundle_freeze_handoff_latest.json",
    EDGE_DIR / "v28_successor_sidecar_bundle_batch_handoff_latest.json",
    EDGE_DIR / "v28_successor_sidecar_bundle_batch_settlement_labels_latest.json",
    EDGE_DIR / "v28_successor_sidecar_bundle_batch_label_join_latest.json",
    EDGE_DIR / "v28_successor_sidecar_batch_evidence_score_latest.json",
    EDGE_DIR / "v28_successor_sidecar_collection_cycle_latest.json",
    EDGE_DIR / "v28_successor_live_pnl_policy_cycle_latest.json",
    EDGE_DIR / "v28_successor_live_pnl_policy_score_latest.json",
    EDGE_DIR / "v28_successor_live_pnl_readiness_latest.json",
    EDGE_DIR / "v28_successor_live_pnl_goal_completion_audit_latest.json",
    EDGE_DIR / "v28_successor_market_coverage_loop_latest.json",
    EDGE_DIR / "v28_successor_forward_packet_freeze_handoff_latest.json",
    EDGE_DIR / "v28_successor_forward_collection_spec_latest.json",
    EDGE_DIR / "v28_successor_frozen_forward_predictions_latest.json",
    OUT_DIR / "candidate_manifests_logged_events_latest.json",
    OUT_DIR / "public_rest_sidecar_bundle_demo_latest.json",
    OUT_DIR / "public_rest_sidecar_batch_demo_latest.json",
    OUT_DIR / "sidecar_bundle_batch_settlement_labels_latest.csv",
    OUT_DIR / "forward_labeled_predictions_latest.csv",
    OUT_DIR / "sidecar_bundle_batch_labeled_latest.csv",
    OUT_DIR / "live_pnl_policy_registry_latest.csv",
    OUT_DIR / "live_pnl_labeled_decisions_latest.csv",
    EDGE_DIR / "v28_successor_sidecar_batch_evidence_metrics_latest.csv",
    OUT_DIR / "frozen_forward_predictions_latest.csv",
    OUT_DIR / "forward_registry_latest.csv",
]


def rel_path(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(ROOT)).replace("\\", "/")
    except ValueError:
        return str(path)


def sha256_file(path: Path) -> str | None:
    if not path.exists():
        return None
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def artifact_state(path: Path) -> dict[str, Any]:
    exists = path.exists()
    stat = path.stat() if exists else None
    return {
        "path": rel_path(path),
        "exists": exists,
        "size_bytes": stat.st_size if stat else None,
        "sha256": sha256_file(path),
    }


def build_plan() -> list[dict[str, Any]]:
    return [
        {
            "ordinal": index,
            "step_id": step.step_id,
            "script": step.script,
            "purpose": step.purpose,
            "command": step.command(),
        }
        for index, step in enumerate(PIPELINE_STEPS, start=1)
    ]


def build_planned_step_result(plan_row: dict[str, Any]) -> dict[str, Any]:
    return {
        "step_id": plan_row["step_id"],
        "script": plan_row["script"],
        "purpose": plan_row["purpose"],
        "command": plan_row["command"],
        "returncode": None,
        "elapsed_seconds": 0.0,
        "stdout_tail": "",
        "stderr_tail": "",
        "status": "planned",
    }


def run_step(step: Step, timeout_seconds: int) -> dict[str, Any]:
    command = step.command()
    started = time.perf_counter()
    completed = subprocess.run(
        command,
        cwd=ROOT,
        text=True,
        capture_output=True,
        timeout=timeout_seconds,
        check=False,
    )
    elapsed = time.perf_counter() - started
    return {
        "step_id": step.step_id,
        "script": step.script,
        "purpose": step.purpose,
        "command": command,
        "returncode": completed.returncode,
        "elapsed_seconds": round(elapsed, 3),
        "stdout_tail": completed.stdout[-4000:],
        "stderr_tail": completed.stderr[-4000:],
        "status": "pass" if completed.returncode == 0 else "fail",
    }


def run_pipeline(*, dry_run: bool = False, stop_on_fail: bool = True, timeout_seconds: int = 180) -> dict[str, Any]:
    started_utc = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    plan = build_plan()
    if dry_run:
        step_results = [build_planned_step_result(row) for row in plan]
    else:
        step_results = []
        for step in PIPELINE_STEPS:
            result = run_step(step, timeout_seconds)
            step_results.append(result)
            if stop_on_fail and result["returncode"] != 0:
                break
    failed = [row for row in step_results if row["status"] == "fail"]
    completed_utc = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    return {
        "generated_utc": completed_utc,
        "started_utc": started_utc,
        "runner_script": Path(__file__).name,
        "research_only_guardrails": RESEARCH_ONLY_GUARDRAILS,
        "pipeline_status": "planned" if dry_run else ("pass" if not failed and len(step_results) == len(PIPELINE_STEPS) else "fail"),
        "dry_run": dry_run,
        "stop_on_fail": stop_on_fail,
        "step_count": len(PIPELINE_STEPS),
        "steps_run": len(step_results),
        "failed_steps": [row["step_id"] for row in failed],
        "plan": plan,
        "steps": step_results,
        "key_artifacts": [artifact_state(path) for path in KEY_ARTIFACTS],
        "outputs": {
            "manifest_json": rel_path(PIPELINE_MANIFEST_JSON),
            "manifest_md": rel_path(PIPELINE_MANIFEST_MD),
        },
    }


def write_markdown(manifest: dict[str, Any], path: Path) -> None:
    lines = [
        "# v28 Successor Research Pipeline Run",
        "",
        "Research-only sequential refresh manifest. This report does not touch live bot state, orders, thresholds, secrets, or processes.",
        "",
        "## Summary",
        "",
        f"- Generated UTC: `{manifest['generated_utc']}`",
        f"- Pipeline status: `{manifest['pipeline_status']}`",
        f"- Dry run: `{manifest['dry_run']}`",
        f"- Steps run: `{manifest['steps_run']}` / `{manifest['step_count']}`",
        f"- Failed steps: `{manifest['failed_steps']}`",
        "",
        "## Steps",
        "",
        "| step | status | seconds | purpose |",
        "|---|---|---:|---|",
    ]
    for step in manifest["steps"]:
        lines.append(
            f"| `{step['step_id']}` | `{step['status']}` | {step['elapsed_seconds']} | {step['purpose']} |"
        )
    lines.extend(["", "## Key Artifacts", "", "| artifact | exists | bytes | sha256 |", "|---|---:|---:|---|"])
    for artifact in manifest["key_artifacts"]:
        lines.append(
            f"| `{artifact['path']}` | {artifact['exists']} | {artifact['size_bytes']} | `{artifact['sha256']}` |"
        )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_outputs(manifest: dict[str, Any]) -> None:
    EDGE_DIR.mkdir(parents=True, exist_ok=True)
    PIPELINE_MANIFEST_JSON.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_markdown(manifest, PIPELINE_MANIFEST_MD)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true", help="Write pipeline run manifest.")
    parser.add_argument("--dry-run", action="store_true", help="Plan steps without executing them.")
    parser.add_argument("--stop-on-fail", action="store_true", help="Stop after the first failed step. This is the default.")
    parser.add_argument("--continue-on-fail", action="store_true", help="Continue after failed steps.")
    parser.add_argument("--timeout-seconds", type=int, default=180, help="Per-step timeout.")
    args = parser.parse_args()
    if args.stop_on_fail and args.continue_on_fail:
        parser.error("--stop-on-fail and --continue-on-fail are mutually exclusive.")
    manifest = run_pipeline(
        dry_run=args.dry_run,
        stop_on_fail=not args.continue_on_fail,
        timeout_seconds=args.timeout_seconds,
    )
    if args.write:
        write_outputs(manifest)
    print(
        json.dumps(
            {
                "pipeline_status": manifest["pipeline_status"],
                "dry_run": manifest["dry_run"],
                "steps_run": manifest["steps_run"],
                "step_count": manifest["step_count"],
                "failed_steps": manifest["failed_steps"],
                "written": bool(args.write),
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
