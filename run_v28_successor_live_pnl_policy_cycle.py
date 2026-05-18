"""Run one research-only v28 successor live-P&L policy cycle.

This is the goal-facing wrapper for the v28 successor live-P&L lab:

1. refresh the existing sidecar freeze/label/score artifacts;
2. rebuild frozen live-P&L policy rows from those sidecar artifacts;
3. score the policy versus regular v28 and successor-FV-only on the same rows;
4. write readiness/capture/fill/source reports while preserving no-retroactive-credit.

Default collection mode is ``none`` so local checks do not accidentally depend
on live public APIs. Use ``--collect-mode public-rest --write`` only for an
explicit pre-close research sidecar capture attempt. This runner never touches
live bot state, order logic, thresholds, secrets, or orders.
"""
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from build_v28_successor_live_pnl_policy_lab import build as build_live_pnl_policy_lab
from build_v28_successor_live_pnl_policy_lab import write_outputs as write_live_pnl_policy_outputs
from run_v28_successor_sidecar_collection_cycle import run_cycle as run_sidecar_collection_cycle
from run_v28_successor_sidecar_collection_cycle import write_outputs as write_sidecar_collection_outputs


ROOT = Path(__file__).resolve().parent
EDGE_DIR = ROOT / "logs" / "edge_research"

CYCLE_JSON = EDGE_DIR / "v28_successor_live_pnl_policy_cycle_latest.json"
CYCLE_MD = EDGE_DIR / "v28_successor_live_pnl_policy_cycle_latest.md"
MIN_PROFIT_GOAL_MARKETS = 5
MIN_PROFIT_GOAL_PRIMARY_ROWS = 75

RESEARCH_ONLY_GUARDRAILS = [
    "does not start or stop live bot processes",
    "does not read or write secrets",
    "does not place orders",
    "does not mutate live thresholds or order logic",
    "uses public/recorded sidecar artifacts only",
    "keeps rows before the policy hash as diagnostic only",
]


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


def rel_path(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(ROOT)).replace("\\", "/")
    except ValueError:
        return str(path)


def live_pnl_cycle_status(
    *,
    sidecar_summary: dict[str, Any],
    live_pnl_summary: dict[str, Any],
    readiness: dict[str, Any],
) -> tuple[str, list[str], list[str]]:
    blockers: list[str] = []
    next_actions: list[str] = []
    primary_rows = int(live_pnl_summary.get("primary_live_forward_rows_after_policy_hash") or 0)
    primary_policy_rows = int(live_pnl_summary.get("primary_policy_rows_after_hash") or 0)
    primary_markets = int(live_pnl_summary.get("primary_markets_after_policy_hash") or 0)
    primary_entered = int(live_pnl_summary.get("primary_entered_rows_after_policy_hash") or 0)
    primary_net = float(live_pnl_summary.get("primary_net_pnl_cents") or 0.0)
    primary_delta = float(live_pnl_summary.get("primary_delta_vs_v28_cents") or 0.0)
    diagnostic_rows = int(live_pnl_summary.get("diagnostic_rows_not_primary_credit") or 0)
    registry_rows = int(live_pnl_summary.get("registry_rows") or 0)

    if registry_rows <= 0:
        blockers.append("no_live_pnl_policy_registry_rows")
        next_actions.append("Run sidecar collection before close, then rebuild live-P&L policy rows.")
    if primary_rows <= 0 and primary_policy_rows <= 0:
        blockers.append("no_primary_rows_after_policy_hash")
        next_actions.append("Collect future sidecar rows after the frozen policy hash timestamp.")
    elif primary_rows <= 0 and primary_policy_rows > 0:
        blockers.append("primary_rows_pending_settlement_labels")
        next_actions.append("Rerun the cycle after the newly captured post-hash market closes and labels are available.")
    if sidecar_summary.get("cycle_status") in {"blocked_no_frozen_sidecar_rows", "blocked_collection_error"}:
        blockers.append(str(sidecar_summary.get("cycle_status")))
        next_actions.append("Inspect the sidecar cycle report before trusting live-P&L denominators.")
    if not readiness.get("level_1_complete"):
        blockers.append("level_1_bootstrap_not_complete")
    if primary_rows > 0 and primary_rows < MIN_PROFIT_GOAL_PRIMARY_ROWS:
        blockers.append("profit_goal_primary_rows_below_floor")
    if primary_markets < MIN_PROFIT_GOAL_MARKETS:
        blockers.append("profit_goal_markets_below_floor")
    if primary_rows > 0 and primary_entered <= 0:
        blockers.append("no_primary_entries_after_policy_hash")
        next_actions.append("Continue collecting future rows until the policy finds a valid entry opportunity.")
    if primary_rows > 0 and primary_entered > 0 and primary_net <= 0:
        blockers.append("profit_goal_net_pnl_not_positive")
    if primary_rows > 0 and primary_entered > 0 and primary_delta <= 0:
        blockers.append("profit_goal_delta_vs_v28_not_positive")
        if primary_net > 0 and primary_delta == 0:
            next_actions.append("Keep collecting: positive P&L with zero v28 delta blocks promotion but is not a negative-delta failure yet.")

    if registry_rows <= 0:
        status = "blocked_no_policy_rows"
    elif primary_rows <= 0 and primary_policy_rows > 0:
        status = "primary_rows_captured_waiting_for_settlement_labels"
    elif primary_rows <= 0:
        status = "ready_to_collect_future_primary_rows"
    elif (
        primary_rows >= MIN_PROFIT_GOAL_PRIMARY_ROWS
        and primary_markets >= MIN_PROFIT_GOAL_MARKETS
        and primary_entered > 0
        and primary_net > 0
        and primary_delta > 0
        and readiness.get("level_1_complete")
    ):
        status = "profit_goal_candidate_forward_ready"
    elif primary_rows > 0 and primary_entered <= 0:
        status = "profit_goal_incomplete_no_entries_yet_collect_more_evidence"
    elif primary_rows > 0 and (primary_net <= 0 or primary_delta < 0):
        status = "profit_goal_incomplete_candidate_failed_forward_pnl"
    elif primary_markets < MIN_PROFIT_GOAL_MARKETS:
        status = "profit_goal_incomplete_collect_more_markets"
    elif not readiness.get("level_1_complete"):
        status = "primary_rows_collecting_below_bootstrap_floor"
    else:
        status = "profit_goal_incomplete_collect_more_evidence"
    return status, sorted(set(blockers)), list(dict.fromkeys(next_actions))


def run_live_pnl_policy_cycle(
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
    sidecar_report = run_sidecar_collection_cycle(
        collect_mode=collect_mode,
        now_utc=now_utc,
        timeout_seconds=timeout_seconds,
        max_markets=max_markets,
        nearest_close_only=nearest_close_only,
        write=write,
        skip_label_fetch=skip_label_fetch,
        refresh_downstream_audits=refresh_downstream_audits,
    )
    if write:
        write_sidecar_collection_outputs(sidecar_report)

    live_pnl_bundle = build_live_pnl_policy_lab()
    if write:
        write_live_pnl_policy_outputs(live_pnl_bundle)

    live_pnl_summary = {
        "policy_id": live_pnl_bundle["registry_summary"].get("policy_id", ""),
        "policy_hash": live_pnl_bundle["registry_summary"].get("policy_hash", ""),
        "policy_created_utc": live_pnl_bundle["registry_summary"].get("policy_created_utc", ""),
        "registry_rows": live_pnl_bundle["registry_summary"].get("rows", 0),
        "primary_policy_rows_after_hash": live_pnl_bundle["registry_summary"].get("primary_evidence_rows", 0),
        "joined_rows": live_pnl_bundle["label_summary"].get("joined_rows", 0),
        "primary_live_forward_rows_after_policy_hash": live_pnl_bundle["score_summary"].get(
            "primary_live_forward_rows_after_policy_hash", 0
        ),
        "primary_markets_after_policy_hash": live_pnl_bundle["score_summary"].get("primary_markets", 0),
        "diagnostic_rows_not_primary_credit": live_pnl_bundle["score_summary"].get(
            "diagnostic_rows_not_primary_credit", 0
        ),
        "readiness_verdict": live_pnl_bundle["readiness"].get("readiness_verdict", ""),
    }
    primary_score = next(
        (
            row
            for row in live_pnl_bundle["score_rows"]
            if row.get("slice") == "primary_live_forward_rows_after_policy_hash"
        ),
        {},
    )
    live_pnl_summary["primary_net_pnl_cents"] = primary_score.get("net_pnl_cents", "0")
    live_pnl_summary["primary_delta_vs_v28_cents"] = primary_score.get("delta_net_cents_vs_v28", "0")
    live_pnl_summary["primary_v28_net_pnl_cents"] = primary_score.get("v28_net_pnl_cents", "0")
    live_pnl_summary["primary_entered_rows_after_policy_hash"] = primary_score.get("entered_rows", "0")
    status, blockers, next_actions = live_pnl_cycle_status(
        sidecar_summary=sidecar_report["summary"],
        live_pnl_summary=live_pnl_summary,
        readiness=live_pnl_bundle["readiness"],
    )
    summary = {
        "cycle_status": status,
        "collect_mode": collect_mode,
        "promotion_allowed": False,
        "controlled_live_test_authorized": False,
        "blockers": blockers,
        "next_actions": next_actions,
        **live_pnl_summary,
    }
    return {
        "summary": summary,
        "research_only_guardrails": RESEARCH_ONLY_GUARDRAILS,
        "sidecar_cycle_summary": sidecar_report["summary"],
        "live_pnl_score_summary": live_pnl_bundle["score_summary"],
        "live_pnl_readiness": live_pnl_bundle["readiness"],
        "artifacts": {
            "sidecar_cycle": rel_path(EDGE_DIR / "v28_successor_sidecar_collection_cycle_latest.json"),
            "policy_registry": "research_particle/v28_successor/live_pnl_policy_registry_latest.csv",
            "labeled_decisions": "research_particle/v28_successor/live_pnl_labeled_decisions_latest.csv",
            "policy_score": rel_path(EDGE_DIR / "v28_successor_live_pnl_policy_score_latest.json"),
            "readiness": rel_path(EDGE_DIR / "v28_successor_live_pnl_readiness_latest.json"),
            "cycle_report": rel_path(CYCLE_JSON),
        },
    }


def write_markdown(report: dict[str, Any], path: Path = CYCLE_MD) -> None:
    summary = report["summary"]
    lines = [
        "# v28 Successor Live P&L Policy Cycle",
        "",
        "Research-only wrapper around sidecar evidence refresh and live-P&L policy scoring.",
        "",
        "## Summary",
        "",
        f"- Cycle status: `{summary['cycle_status']}`",
        f"- Collect mode: `{summary['collect_mode']}`",
        f"- Policy id: `{summary['policy_id']}`",
        f"- Policy hash: `{summary['policy_hash']}`",
        f"- Policy created UTC: `{summary['policy_created_utc']}`",
        f"- Registry rows: `{summary['registry_rows']}`",
        f"- Primary policy rows after hash: `{summary['primary_policy_rows_after_hash']}`",
        f"- Joined rows: `{summary['joined_rows']}`",
        f"- Primary rows after policy hash: `{summary['primary_live_forward_rows_after_policy_hash']}`",
        f"- Primary markets after policy hash: `{summary['primary_markets_after_policy_hash']}`",
        f"- Primary entered rows after policy hash: `{summary['primary_entered_rows_after_policy_hash']}`",
        f"- Primary net P&L cents: `{summary['primary_net_pnl_cents']}`",
        f"- Primary delta vs v28 cents: `{summary['primary_delta_vs_v28_cents']}`",
        f"- Diagnostic rows not primary credit: `{summary['diagnostic_rows_not_primary_credit']}`",
        f"- Readiness verdict: `{summary['readiness_verdict']}`",
        f"- Controlled live test authorized: `{summary['controlled_live_test_authorized']}`",
        "",
        "## Blockers",
        "",
    ]
    if summary["blockers"]:
        for blocker in summary["blockers"]:
            lines.append(f"- `{blocker}`")
    else:
        lines.append("- None recorded.")
    lines.extend(["", "## Next Actions", ""])
    if summary["next_actions"]:
        for action in summary["next_actions"]:
            lines.append(f"- {action}")
    else:
        lines.append("- Continue forward validation.")
    lines.extend(
        [
            "",
            "## Guardrails",
            "",
            *[f"- {item}" for item in report["research_only_guardrails"]],
            "",
            "## Artifacts",
            "",
        ]
    )
    for name, artifact in report["artifacts"].items():
        lines.append(f"- `{name}`: `{artifact}`")
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
    parser.add_argument("--all-open-closes", action="store_true")
    parser.add_argument("--skip-label-fetch", action="store_true")
    parser.add_argument("--skip-downstream-audits", action="store_true")
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    now_utc = parse_ts(args.now_utc) if args.now_utc else None
    report = run_live_pnl_policy_cycle(
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
    print(
        json.dumps(
            {
                "cycle_status": report["summary"]["cycle_status"],
                "policy_id": report["summary"]["policy_id"],
                "policy_hash": report["summary"]["policy_hash"],
                "registry_rows": report["summary"]["registry_rows"],
                "primary_policy_rows_after_hash": report["summary"]["primary_policy_rows_after_hash"],
                "joined_rows": report["summary"]["joined_rows"],
                "primary_rows_after_policy_hash": report["summary"]["primary_live_forward_rows_after_policy_hash"],
                "primary_markets_after_policy_hash": report["summary"]["primary_markets_after_policy_hash"],
                "primary_entered_rows_after_policy_hash": report["summary"]["primary_entered_rows_after_policy_hash"],
                "primary_net_pnl_cents": report["summary"]["primary_net_pnl_cents"],
                "primary_delta_vs_v28_cents": report["summary"]["primary_delta_vs_v28_cents"],
                "diagnostic_rows_not_primary_credit": report["summary"]["diagnostic_rows_not_primary_credit"],
                "readiness_verdict": report["summary"]["readiness_verdict"],
                "written": bool(args.write and not args.dry_run),
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
