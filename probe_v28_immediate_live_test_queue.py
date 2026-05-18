"""Immediate live-test queue for v28-derived candidates.

Research-only audit; does not place orders, start processes, or change live
state.

This is the sequential launch ledger for the goal variant that says live testing
must start with the strongest existing candidate by PnL and win rate. It ranks
existing candidates by PnL first and win rate second, then formally defers each
candidate that cannot be live-tested as a complete policy.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"

CANDIDATE_VS_LIVE_JSON = OUT_DIR / "v28_candidate_vs_live_full_table_latest.json"
FULL_POLICY_JSON = OUT_DIR / "v28_full_policy_candidate_scorecard_latest.json"
CONTROLLED_GATE_JSON = OUT_DIR / "v28_controlled_live_test_gate_latest.json"
LIVE_TEST_SPEC_JSON = OUT_DIR / "v28_common_clock_exit_guard_live_test_spec_latest.json"
SAFETY_JSON = OUT_DIR / "v28_common_clock_exit_guard_safety_verifier_latest.json"
OUT_JSON = OUT_DIR / "v28_immediate_live_test_queue_latest.json"
OUT_MD = OUT_DIR / "v28_immediate_live_test_queue_latest.md"


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
    return payload if isinstance(payload, dict) else {}


def fnum(value: Any, default: float = 0.0) -> float:
    try:
        if value is None or value == "":
            return default
        return float(value)
    except (TypeError, ValueError):
        return default


def inum(value: Any) -> int:
    return int(fnum(value))


def row_key(row: dict[str, Any]) -> str:
    return f"{row.get('gate')}::{row.get('policy')}"


def win_rate(row: dict[str, Any]) -> float | None:
    wins = row.get("wins")
    losses = row.get("losses")
    if wins is None or losses is None:
        wl = str(row.get("wins_losses") or "")
        if "/" in wl:
            left, right = wl.split("/", 1)
            wins = fnum(left)
            losses = fnum(right)
    if wins is None or losses is None:
        return None
    denom = fnum(wins) + fnum(losses)
    if denom <= 0:
        return None
    return fnum(wins) / denom


def compact_candidate(row: dict[str, Any], full_policy: dict[str, Any] | None) -> dict[str, Any]:
    blockers = list(row.get("blockers") or [])
    missing = list((full_policy or {}).get("missing_gates") or [])
    evidence = (full_policy or {}).get("evidence") or {}
    live_ready = bool(row.get("live_ready")) or bool((full_policy or {}).get("live_test_allowed"))
    defer_reasons: list[str] = []
    if blockers:
        defer_reasons.extend(str(item) for item in blockers)
    if missing:
        defer_reasons.extend(str(item) for item in missing if str(item) not in defer_reasons)
    if not full_policy:
        defer_reasons.append("no_full_policy_card")
    if not live_ready:
        defer_reasons.append("live_ready_false")
    if full_policy and not (full_policy or {}).get("live_test_allowed"):
        defer_reasons.append("full_policy_live_test_not_allowed")
    return {
        "gate": row.get("gate"),
        "policy": row.get("policy"),
        "net_cents": row.get("net_cents"),
        "wins": row.get("wins"),
        "losses": row.get("losses"),
        "win_rate": win_rate(row),
        "settled": row.get("settled"),
        "coverage_pct": row.get("coverage_pct"),
        "delta_vs_live_cents": row.get("delta_vs_live_cents"),
        "source_share": row.get("simulated_share") or row.get("reconstructed_share"),
        "candidate_vs_live_live_ready": row.get("live_ready"),
        "full_policy_available": bool(full_policy),
        "full_policy_live_test_allowed": bool((full_policy or {}).get("live_test_allowed")),
        "full_policy_missing_gates": missing,
        "full_policy_type": (full_policy or {}).get("candidate_type"),
        "full_policy_evidence": evidence,
        "blockers": blockers,
        "defer_reasons": sorted(set(defer_reasons)),
        "launchable_now": bool(full_policy and (full_policy or {}).get("live_test_allowed") and not blockers),
    }


def build_report() -> dict[str, Any]:
    candidates = load_json(CANDIDATE_VS_LIVE_JSON)
    full = load_json(FULL_POLICY_JSON)
    controlled = load_json(CONTROLLED_GATE_JSON)
    spec = load_json(LIVE_TEST_SPEC_JSON)
    safety = load_json(SAFETY_JSON)

    full_cards = [
        row for row in (full.get("all_policy_cards") or full.get("candidate_cards") or [])
        if isinstance(row, dict)
    ]
    full_by_key = {row_key(row): row for row in full_cards}

    rows = [row for row in (candidates.get("rows") or []) if isinstance(row, dict)]
    ranked = sorted(
        rows,
        key=lambda row: (
            fnum(row.get("net_cents")),
            win_rate(row) if win_rate(row) is not None else -1.0,
            fnum(row.get("delta_vs_live_cents")),
            inum(row.get("settled")),
        ),
        reverse=True,
    )
    queue = [compact_candidate(row, full_by_key.get(row_key(row))) for row in ranked[:40]]
    launchable = [row for row in queue if row["launchable_now"]]
    active_candidate = launchable[0] if launchable else None

    top_deferred = queue[0] if queue else None
    if active_candidate:
        decision = "launch_candidate_after_operator_confirmation"
    elif full.get("live_test_allowed_count") == 0 or controlled.get("decision") == "no_live_test":
        decision = "no_immediate_live_launch_all_ranked_candidates_deferred"
    else:
        decision = "manual_review_required"

    return {
        "generated_at_utc": utc_now_iso(),
        "purpose": "Rank existing v28 candidates by PnL and win rate, then select the first complete policy that can be live-tested sequentially.",
        "decision": decision,
        "live_baseline_cents": candidates.get("live_net_cents"),
        "controlled_gate_decision": controlled.get("decision"),
        "full_policy_decision": full.get("decision"),
        "live_test_allowed_count": full.get("live_test_allowed_count"),
        "paper_shadow_safety_decision": safety.get("decision"),
        "common_clock_live_test_spec_decision": spec.get("decision"),
        "active_candidate": active_candidate,
        "top_deferred_candidate": top_deferred,
        "ranked_queue": queue,
        "formal_deferral": {
            "top_ranked_candidate": top_deferred,
            "reason": (
                "Highest-ranked candidates by PnL/win rate are not live-testable as complete policies under current controlled gates."
                if not active_candidate
                else ""
            ),
            "next_action": (
                "Do not place live candidate trades; collect missing strict-forward/live-readiness evidence or rerun after gates change."
                if not active_candidate
                else "Prepare the active candidate for operator-confirmed live launch."
            ),
        },
        "sources": {
            "candidate_vs_live": str(CANDIDATE_VS_LIVE_JSON),
            "full_policy": str(FULL_POLICY_JSON),
            "controlled_gate": str(CONTROLLED_GATE_JSON),
            "live_test_spec": str(LIVE_TEST_SPEC_JSON),
            "safety": str(SAFETY_JSON),
        },
    }


def money(cents: Any) -> str:
    value = fnum(cents)
    return f"{value:.0f}c (${value / 100.0:.2f})"


def pct(value: Any) -> str:
    if value is None:
        return "n/a"
    return f"{100.0 * fnum(value):.1f}%"


def write_outputs(report: dict[str, Any]) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8")
    lines = [
        "# v28 Immediate Live-Test Queue",
        "",
        "Research-only audit. No orders placed and no live process started.",
        "",
        f"- Generated UTC: `{report.get('generated_at_utc')}`",
        f"- Decision: `{report.get('decision')}`",
        f"- Live baseline: `{money(report.get('live_baseline_cents'))}`",
        f"- Controlled gate: `{report.get('controlled_gate_decision')}`",
        f"- Full-policy decision / allowed count: `{report.get('full_policy_decision')}` / `{report.get('live_test_allowed_count')}`",
        f"- Paper-shadow safety: `{report.get('paper_shadow_safety_decision')}`",
        "",
        "## Ranked Queue",
        "",
        "| rank | gate | policy | net | W/L | win rate | delta live | full policy | launchable | defer reasons |",
        "|---:|---|---|---:|---:|---:|---:|---|---|---|",
    ]
    for idx, row in enumerate(report.get("ranked_queue") or [], start=1):
        wl = f"{row.get('wins')}/{row.get('losses')}" if row.get("wins") is not None else "n/a"
        lines.append(
            f"| {idx} | `{row.get('gate')}` | `{row.get('policy')}` | {money(row.get('net_cents'))} | "
            f"`{wl}` | {pct(row.get('win_rate'))} | {money(row.get('delta_vs_live_cents'))} | "
            f"`{row.get('full_policy_available')}` | `{row.get('launchable_now')}` | "
            f"`{', '.join(row.get('defer_reasons') or [])}` |"
        )
    formal = report.get("formal_deferral") or {}
    lines.extend([
        "",
        "## Formal Deferral",
        "",
        f"- Reason: {formal.get('reason')}",
        f"- Next action: {formal.get('next_action')}",
    ])
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    report = build_report()
    write_outputs(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
