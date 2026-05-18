"""Run one research-only v28 successor sidecar evidence cycle.

This is the repeatable broad-evidence loop around the sidecar path:

1. optionally collect active BTC15M public REST sidecar bundles;
2. freeze all ready sidecar bundles before close while preserving old frozen rows;
3. fetch post-close settlement labels for frozen markets;
4. join labels to frozen rows;
5. score probability-first sidecar evidence;
6. refresh downstream audits that keep promotion closed until all gates pass.

The default collect mode is ``none`` so scheduled/local reproducibility checks do
not accidentally depend on live public APIs. Use ``--collect-mode public-rest``
for an explicit pre-close capture attempt.

This script never touches live bot state, secrets, thresholds, orders, or
processes. It also never writes canonical promotion ledgers directly.
"""
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from audit_v28_successor_forward_source_readiness import build as build_forward_source_readiness
from audit_v28_successor_forward_source_readiness import write_outputs as write_forward_source_readiness_outputs
from audit_v28_successor_goal_completion import build_checklist as build_goal_completion_checklist
from audit_v28_successor_goal_completion import write_outputs as write_goal_completion_outputs
from build_v28_successor_public_rest_sidecar_batch import build as build_public_rest_sidecar_batch
from build_v28_successor_public_rest_sidecar_batch import write_outputs as write_public_rest_sidecar_batch_outputs
from fetch_v28_successor_sidecar_batch_settlement_labels import build as build_sidecar_batch_labels
from fetch_v28_successor_sidecar_batch_settlement_labels import write_outputs as write_sidecar_batch_label_outputs
from run_v28_successor_sidecar_batch_label_join_handoff import build as build_sidecar_batch_label_join
from run_v28_successor_sidecar_batch_label_join_handoff import write_outputs as write_sidecar_batch_label_join_outputs
from run_v28_successor_sidecar_bundle_batch_handoff import build as build_sidecar_bundle_batch_handoff
from run_v28_successor_sidecar_bundle_batch_handoff import write_outputs as write_sidecar_bundle_batch_handoff_outputs
from score_v28_successor_sidecar_batch_evidence import build as build_sidecar_batch_evidence
from score_v28_successor_sidecar_batch_evidence import write_outputs as write_sidecar_batch_evidence_outputs
from validate_v28_successor_source_contract import build as build_source_contract
from validate_v28_successor_source_contract import write_outputs as write_source_contract_outputs


ROOT = Path(__file__).resolve().parent
EDGE_DIR = ROOT / "logs" / "edge_research"

CYCLE_JSON = EDGE_DIR / "v28_successor_sidecar_collection_cycle_latest.json"
CYCLE_MD = EDGE_DIR / "v28_successor_sidecar_collection_cycle_latest.md"

MIN_FORWARD_ROWS = 200
MIN_FORWARD_MARKETS = 40

RESEARCH_ONLY_GUARDRAILS = [
    "does not start or stop live bot processes",
    "does not read or write secrets",
    "does not place orders",
    "does not mutate live thresholds or order logic",
    "does not write canonical promotion ledgers directly",
    "promotion_allowed is always false for this cycle report",
]


def rel_path(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(ROOT)).replace("\\", "/")
    except ValueError:
        return str(path)


def iso_z(value: datetime) -> str:
    return value.astimezone(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def parse_ts(value: str) -> datetime | None:
    text = str(value or "").strip()
    if not text:
        return None
    if text.endswith("Z"):
        text = text[:-1] + "+00:00"
    parsed = datetime.fromisoformat(text)
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def as_int(value: Any) -> int:
    try:
        return int(value or 0)
    except (TypeError, ValueError):
        return 0


def step_record(step_id: str, status: str, summary: dict[str, Any] | None = None) -> dict[str, Any]:
    return {
        "step_id": step_id,
        "status": status,
        "summary": summary or {},
    }


def cycle_status(
    *,
    collect_status: str,
    handoff_summary: dict[str, Any],
    label_summary: dict[str, Any],
    join_summary: dict[str, Any],
    evidence_summary: dict[str, Any],
    source_summary: dict[str, Any] | None,
    goal_summary: dict[str, Any] | None,
) -> tuple[str, list[str], list[str]]:
    blockers: list[str] = []
    next_actions: list[str] = []
    frozen_rows = as_int((handoff_summary.get("freeze_handoff") or {}).get("frozen_prediction_rows"))
    frozen_markets = as_int((handoff_summary.get("freeze_handoff") or {}).get("registry_markets"))
    clean_rows = as_int(evidence_summary.get("clean_forward_rows"))
    clean_markets = as_int(evidence_summary.get("clean_forward_markets"))
    promotable_candidates = as_int(evidence_summary.get("promotable_candidate_count"))

    if collect_status.startswith("blocked"):
        blockers.append(collect_status)
        next_actions.append("Run again before the next BTC15M close or inspect the public REST collector error.")
    if frozen_rows <= 0:
        blockers.append("no_frozen_sidecar_rows")
        next_actions.append("Capture public REST sidecar bundles before close, then freeze them immediately.")
    if label_summary.get("label_fetch_status") == "blocked_waiting_for_market_close":
        blockers.append("waiting_for_market_close")
        next_actions.append("Rerun the cycle after the newest frozen market has settled.")
    if as_int(join_summary.get("joined_rows")) <= 0:
        blockers.append("no_joined_post_resolution_sidecar_rows")
        next_actions.append("Fetch settlement labels after close and rerun the label join.")
    if clean_rows < MIN_FORWARD_ROWS:
        blockers.append("sidecar_clean_rows_below_forward_floor")
        next_actions.append("Keep collecting more pre-close sidecar bundles until clean rows reach the forward floor.")
    if clean_markets < MIN_FORWARD_MARKETS:
        blockers.append("sidecar_clean_markets_below_forward_floor")
        next_actions.append("Keep collecting distinct BTC15M markets until market coverage reaches the forward floor.")
    if frozen_markets < MIN_FORWARD_MARKETS:
        blockers.append("sidecar_frozen_markets_below_forward_floor")
    if promotable_candidates <= 0:
        blockers.append("no_sidecar_candidate_beats_v28_under_gates")
        next_actions.append("Score more settled rows before interpreting candidate-vs-v28 deltas.")
    if source_summary and source_summary.get("overall_verdict") != "promotion_grade":
        blockers.append("source_contract_not_promotion_grade")
    if goal_summary and goal_summary.get("overall_status") != "complete":
        blockers.append("goal_audit_not_complete")

    if frozen_rows <= 0:
        status = "blocked_no_frozen_sidecar_rows"
    elif label_summary.get("label_fetch_status") == "blocked_waiting_for_market_close":
        status = "frozen_sidecar_rows_waiting_for_settlement"
    elif clean_rows < MIN_FORWARD_ROWS or clean_markets < MIN_FORWARD_MARKETS:
        status = "sidecar_evidence_below_coverage_floor"
    elif promotable_candidates <= 0:
        status = "sidecar_evidence_scored_no_promotable_candidate"
    elif source_summary and source_summary.get("overall_verdict") != "promotion_grade":
        status = "sidecar_evidence_ready_but_source_contract_blocked"
    else:
        status = "sidecar_cycle_ready_for_external_promotion_verifier"

    return status, sorted(set(blockers)), list(dict.fromkeys(next_actions))


def run_cycle(
    *,
    collect_mode: str = "none",
    now_utc: datetime | None = None,
    timeout_seconds: float = 10.0,
    max_markets: int = 80,
    nearest_close_only: bool = True,
    write: bool = False,
    skip_label_fetch: bool = False,
    refresh_downstream_audits: bool = True,
) -> dict[str, Any]:
    now_utc = (now_utc or datetime.now(timezone.utc)).astimezone(timezone.utc)
    steps: list[dict[str, Any]] = []
    collect_status = "skipped_existing_sidecar_bundles"
    collect_summary: dict[str, Any] = {
        "collect_mode": collect_mode,
        "reason": "default cycle uses existing sidecar bundles; pass --collect-mode public-rest for live public API capture",
    }

    if collect_mode != "none":
        try:
            collect_report, bundles = build_public_rest_sidecar_batch(
                mode=collect_mode,
                now_utc=now_utc,
                timeout_seconds=timeout_seconds,
                max_markets=max_markets,
                nearest_close_only=nearest_close_only,
            )
            collect_summary = collect_report["summary"]
            collect_status = str(collect_summary.get("batch_status") or "unknown_collect_status")
            if write:
                write_public_rest_sidecar_batch_outputs(collect_report, bundles)
        except Exception as exc:  # noqa: BLE001
            collect_status = "blocked_collection_error"
            collect_summary = {
                "collect_mode": collect_mode,
                "error": str(exc),
                "promotion_allowed": False,
            }
    steps.append(step_record("public_rest_sidecar_batch", collect_status, collect_summary))

    handoff_report, _packet_rows, _frozen_rows, _registry_rows = build_sidecar_bundle_batch_handoff(
        now_utc=now_utc,
        preserve_existing_frozen=True,
    )
    handoff_summary = handoff_report["summary"]
    if write:
        write_sidecar_bundle_batch_handoff_outputs(handoff_report, _packet_rows, _frozen_rows, _registry_rows)
    steps.append(step_record("sidecar_bundle_batch_handoff", str(handoff_summary.get("batch_handoff_status")), handoff_summary))

    if skip_label_fetch:
        label_summary = {
            "label_fetch_status": "skipped",
            "promotion_allowed": False,
            "reason": "skip_label_fetch=True",
        }
        steps.append(step_record("sidecar_bundle_batch_settlement_labels", "skipped", label_summary))
    else:
        label_report, labels = build_sidecar_batch_labels(timeout_seconds=timeout_seconds, now_utc=now_utc)
        label_summary = label_report["summary"]
        if write:
            write_sidecar_batch_label_outputs(label_report, labels)
        steps.append(step_record("sidecar_bundle_batch_settlement_labels", str(label_summary.get("label_fetch_status")), label_summary))

    join_report, joined_rows = build_sidecar_batch_label_join()
    join_summary = join_report["summary"]
    if write:
        write_sidecar_batch_label_join_outputs(join_report, joined_rows)
    steps.append(step_record("sidecar_bundle_batch_label_join", str(join_summary.get("batch_label_join_status")), join_summary))

    metrics, bins, evidence_summary = build_sidecar_batch_evidence()
    if write:
        write_sidecar_batch_evidence_outputs(metrics, bins, evidence_summary)
    steps.append(step_record("sidecar_batch_evidence_score", str(evidence_summary.get("evidence_status")), evidence_summary))

    source_summary: dict[str, Any] | None = None
    readiness_summary: dict[str, Any] | None = None
    goal_summary: dict[str, Any] | None = None
    if refresh_downstream_audits:
        source_rows, source_summary = build_source_contract()
        if write:
            write_source_contract_outputs(source_rows, source_summary)
        steps.append(step_record("source_contract", str(source_summary.get("overall_verdict")), source_summary))

        readiness_report, readiness_summary = build_forward_source_readiness()
        if write:
            write_forward_source_readiness_outputs(readiness_report, readiness_summary)
        steps.append(step_record("forward_source_readiness", str(readiness_summary.get("overall_status")), readiness_summary))

        goal_checks, goal_summary = build_goal_completion_checklist()
        if write:
            write_goal_completion_outputs(goal_checks, goal_summary)
        steps.append(step_record("goal_completion_audit", str(goal_summary.get("overall_status")), goal_summary))

    status, blockers, next_actions = cycle_status(
        collect_status=collect_status,
        handoff_summary=handoff_summary,
        label_summary=label_summary,
        join_summary=join_summary,
        evidence_summary=evidence_summary,
        source_summary=source_summary,
        goal_summary=goal_summary,
    )
    summary = {
        "generated_utc": iso_z(now_utc),
        "builder_script": Path(__file__).name,
        "cycle_status": status,
        "promotion_allowed": False,
        "promotion_status": {
            "allowed": False,
            "reason": "collection cycles can create forward evidence, but promotion still requires source contract, coverage, evidence, verifier, and frozen forward gates",
        },
        "collect_mode": collect_mode,
        "steps_run": len(steps),
        "sidecar_frozen_rows": as_int((handoff_summary.get("freeze_handoff") or {}).get("frozen_prediction_rows")),
        "sidecar_frozen_markets": as_int((handoff_summary.get("freeze_handoff") or {}).get("registry_markets")),
        "sidecar_joined_rows": as_int(join_summary.get("joined_rows")),
        "sidecar_joined_markets": as_int(join_summary.get("joined_markets")),
        "sidecar_clean_forward_rows": as_int(evidence_summary.get("clean_forward_rows")),
        "sidecar_clean_forward_markets": as_int(evidence_summary.get("clean_forward_markets")),
        "sidecar_promotable_candidate_count": as_int(evidence_summary.get("promotable_candidate_count")),
        "minimum_forward_rows": MIN_FORWARD_ROWS,
        "minimum_forward_markets": MIN_FORWARD_MARKETS,
        "blockers": blockers,
        "next_actions": next_actions,
        "research_only_guardrails": RESEARCH_ONLY_GUARDRAILS,
        "outputs": {
            "cycle_json": rel_path(CYCLE_JSON),
            "cycle_md": rel_path(CYCLE_MD),
        },
    }
    return {"summary": summary, "steps": steps}


def write_markdown(report: dict[str, Any], path: Path) -> None:
    summary = report["summary"]
    lines = [
        "# v28 Successor Sidecar Collection Cycle",
        "",
        "Research-only one-cycle runner for broad sidecar forward evidence. It does not touch live bot state, orders, thresholds, secrets, or processes.",
        "",
        "## Summary",
        "",
        f"- Generated UTC: `{summary['generated_utc']}`",
        f"- Cycle status: `{summary['cycle_status']}`",
        f"- Collect mode: `{summary['collect_mode']}`",
        f"- Promotion allowed: `{summary['promotion_allowed']}`",
        f"- Sidecar frozen rows / markets: `{summary['sidecar_frozen_rows']}` / `{summary['sidecar_frozen_markets']}`",
        f"- Sidecar joined rows / markets: `{summary['sidecar_joined_rows']}` / `{summary['sidecar_joined_markets']}`",
        f"- Sidecar clean rows / markets: `{summary['sidecar_clean_forward_rows']}` / `{summary['sidecar_clean_forward_markets']}`",
        f"- Sidecar promotable candidates: `{summary['sidecar_promotable_candidate_count']}`",
        "",
        "## Blockers",
        "",
    ]
    if summary["blockers"]:
        for blocker in summary["blockers"]:
            lines.append(f"- `{blocker}`")
    else:
        lines.append("- None recorded by this cycle.")
    lines.extend(["", "## Next Actions", ""])
    if summary["next_actions"]:
        for action in summary["next_actions"]:
            lines.append(f"- {action}")
    else:
        lines.append("- Continue to the source contract and promotion verifier.")
    lines.extend(["", "## Steps", "", "| step | status |", "|---|---|"])
    for step in report["steps"]:
        lines.append(f"| `{step['step_id']}` | `{step['status']}` |")
    lines.extend(
        [
            "",
            "## Read",
            "",
            "- Default collection mode is `none`; it refreshes existing bundle evidence without a new public API capture.",
            "- Use `--collect-mode public-rest --write` only during an explicit pre-close collection attempt.",
            "- This runner keeps sidecar evidence non-canonical and non-promoting by design.",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_outputs(report: dict[str, Any]) -> None:
    EDGE_DIR.mkdir(parents=True, exist_ok=True)
    CYCLE_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_markdown(report, CYCLE_MD)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--collect-mode", choices=["none", "fixture", "public-rest"], default="none")
    parser.add_argument("--now-utc", default="")
    parser.add_argument("--timeout-seconds", type=float, default=10.0)
    parser.add_argument("--max-markets", type=int, default=80)
    parser.add_argument("--all-open-closes", action="store_true", help="Collect all returned open closes instead of only the nearest close.")
    parser.add_argument("--skip-label-fetch", action="store_true")
    parser.add_argument("--skip-downstream-audits", action="store_true")
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    now_utc = parse_ts(args.now_utc) if args.now_utc else None
    report = run_cycle(
        collect_mode=args.collect_mode.replace("-", "_"),
        now_utc=now_utc,
        timeout_seconds=args.timeout_seconds,
        max_markets=args.max_markets,
        nearest_close_only=not args.all_open_closes,
        write=bool(args.write and not args.dry_run),
        skip_label_fetch=args.skip_label_fetch,
        refresh_downstream_audits=not args.skip_downstream_audits,
    )
    if args.write and not args.dry_run:
        write_outputs(report)
    summary = report["summary"]
    print(
        json.dumps(
            {
                "cycle_status": summary["cycle_status"],
                "collect_mode": summary["collect_mode"],
                "sidecar_frozen_rows": summary["sidecar_frozen_rows"],
                "sidecar_frozen_markets": summary["sidecar_frozen_markets"],
                "sidecar_joined_rows": summary["sidecar_joined_rows"],
                "sidecar_clean_forward_rows": summary["sidecar_clean_forward_rows"],
                "sidecar_clean_forward_markets": summary["sidecar_clean_forward_markets"],
                "sidecar_promotable_candidate_count": summary["sidecar_promotable_candidate_count"],
                "promotion_allowed": summary["promotion_allowed"],
                "written": bool(args.write and not args.dry_run),
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
