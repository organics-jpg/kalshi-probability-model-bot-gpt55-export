"""Synthesize why the current feature-gate branch misses promotion gates.

Research-only; no live bot changes, no process control, no orders.

This combines the current joint-gate gap with feature-gate exit attribution to
separate entry/source/coverage failure from exit-policy failure.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"

JOINT_GAP_JSON = OUT_DIR / "v28_feature_gate_joint_gate_gap_audit_latest.json"
NEAR_PROMO_EXIT_ATTR_JSON = OUT_DIR / "v28_feature_gate_near_promotion_exit_attribution_latest.json"
EXIT_STATE_FRONTIER_JSON = OUT_DIR / "v28_feature_gate_exit_state_repair_frontier_latest.json"
RAW03_RAW05_AUTOPSY_JSON = OUT_DIR / "v28_feature_gate_raw03_vs_raw05_autopsy_latest.json"
FORWARD_COLLECTION_JSON = OUT_DIR / "v28_forward_collection_blocker_audit_latest.json"

OUT_JSON = OUT_DIR / "v28_feature_gate_gap_mechanism_synthesis_latest.json"
OUT_MD = OUT_DIR / "v28_feature_gate_gap_mechanism_synthesis_latest.md"


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


def money(value: Any) -> str:
    cents = fnum(value)
    return f"{cents:.0f}c (${cents / 100.0:.2f})"


def find_row(rows: list[dict[str, Any]], candidate: str) -> dict[str, Any]:
    return next((row for row in rows if row.get("candidate") == candidate), {})


def best_exit_frontier(exit_state: dict[str, Any]) -> dict[str, Any]:
    variants = [row for row in (exit_state.get("variants") or []) if isinstance(row, dict)]
    if not variants:
        return {}
    return sorted(variants, key=lambda row: fnum(row.get("delta_live_cents")), reverse=True)[0]


def build_report() -> dict[str, Any]:
    joint = load_json(JOINT_GAP_JSON)
    near = load_json(NEAR_PROMO_EXIT_ATTR_JSON)
    exit_state = load_json(EXIT_STATE_FRONTIER_JSON)
    raw_autopsy = load_json(RAW03_RAW05_AUTOPSY_JSON)
    forward = load_json(FORWARD_COLLECTION_JSON)

    rows = joint.get("rows") or []
    raw05_bridge = find_row(rows, "post_feature_freeze_bridge_raw05_recross60_abs085")
    raw05_entry = find_row(rows, "post_feature_freeze_entry_raw05_recross60_abs085")
    raw03_bridge = find_row(rows, "post_feature_freeze_bridge_raw03_recross70_abs075")
    raw03_entry = find_row(rows, "post_feature_freeze_entry_raw03_recross70_abs075")
    exit_best = best_exit_frontier(exit_state)

    failure_counts = near.get("failure_class_counts") or {}
    loss_source_counts = near.get("loss_source_counts") or {}
    no_exit_losses = int(failure_counts.get("no_exit_observation") or 0)
    exit_helped_losses = int(failure_counts.get("entry_or_fv_failure_exit_helped") or 0)
    total_losses = sum(int(v or 0) for v in failure_counts.values())
    source_loss_share = None
    if total_losses:
        risky_losses = total_losses - int(loss_source_counts.get("approved_entry") or 0)
        source_loss_share = risky_losses / total_losses

    blockers = ["research_only", "not_promotion_evidence"]
    if no_exit_losses:
        blockers.append("raw05_losses_mostly_no_exit_observation")
    if exit_helped_losses:
        blockers.append("approved_losses_exit_helped_vs_hold")
    if raw05_bridge.get("entries_needed_for_75pct"):
        blockers.append("raw05_bridge_coverage_gap")
    if raw03_bridge.get("reconstructed_share") and fnum(raw03_bridge.get("reconstructed_share")) > 0.35:
        blockers.append("raw03_bridge_source_gap")
    if "live_watchdog_restart_failed" in (forward.get("blockers") or []):
        blockers.append("fresh_v28_live_collection_unhealthy")

    conclusion = (
        "Do not repair the current feature-gate gap with broad exit suppression. "
        "The raw05 bridge is cleaner but under-covered; its losing rows are mostly no-exit-observation/source rows, "
        "and the approved losing rows were helped by exits versus holding. "
        "Raw03 restores coverage by admitting risky rows and still fails source/cushion gates."
    )
    return {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "joint_gap_generated_at_utc": joint.get("generated_at_utc"),
        "near_promotion_exit_attribution_generated_at_utc": near.get("generated_at_utc"),
        "exit_state_frontier_generated_at_utc": exit_state.get("generated_at_utc"),
        "raw03_raw05_autopsy_generated_at_utc": raw_autopsy.get("generated_at_utc"),
        "raw05_bridge": raw05_bridge,
        "raw05_entry": raw05_entry,
        "raw03_bridge": raw03_bridge,
        "raw03_entry": raw03_entry,
        "near_promotion_exit_attribution": {
            "candidate": near.get("candidate"),
            "candidate_net_cents": near.get("candidate_net_cents"),
            "candidate_settled": near.get("candidate_settled"),
            "candidate_missing_gates": near.get("candidate_missing_gates"),
            "failure_class_counts": failure_counts,
            "loss_source_counts": loss_source_counts,
            "source_loss_share": source_loss_share,
        },
        "exit_state_frontier_best": exit_best,
        "raw03_raw05_interpretation": raw_autopsy.get("interpretation"),
        "forward_collection_blockers": forward.get("blockers"),
        "blockers": blockers,
        "conclusion": conclusion,
        "next": [
            "Treat raw05 as a clean-core coverage/source wait, not an exit-suppression repair.",
            "Do not relax to raw03 for coverage; raw03 marginal rows are source-risk and negative/weak.",
            "When v28 collection is healthy again, watch for clean raw05-eligible rows or a separately frozen continuous size/source-quality proxy.",
        ],
    }


def write_outputs(report: dict[str, Any]) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8")
    raw05_bridge = report.get("raw05_bridge") or {}
    raw03_bridge = report.get("raw03_bridge") or {}
    attr = report.get("near_promotion_exit_attribution") or {}
    exit_best = report.get("exit_state_frontier_best") or {}
    lines = [
        "# v28 Feature-Gate Gap Mechanism Synthesis",
        "",
        "Research-only. No live bot logic changes, no process control, no orders.",
        "",
        f"- Generated UTC: `{report.get('generated_at_utc')}`",
        f"- Raw05 bridge: entries/settled `{raw05_bridge.get('entries')}/{raw05_bridge.get('settled')}`, coverage `{fnum(raw05_bridge.get('coverage_pct')):.2f}%`, net `{money(raw05_bridge.get('net_cents'))}`, source `{fnum(raw05_bridge.get('reconstructed_share')):.3f}`, live-snapshot gap `{money(raw05_bridge.get('cents_needed_to_match_live_snapshot'))}`",
        f"- Raw03 bridge: entries/settled `{raw03_bridge.get('entries')}/{raw03_bridge.get('settled')}`, coverage `{fnum(raw03_bridge.get('coverage_pct')):.2f}%`, net `{money(raw03_bridge.get('net_cents'))}`, source `{fnum(raw03_bridge.get('reconstructed_share')):.3f}`, live-snapshot gap `{money(raw03_bridge.get('cents_needed_to_match_live_snapshot'))}`",
        f"- Raw05 loss classes: `{attr.get('failure_class_counts')}`",
        f"- Raw05 loss sources: `{attr.get('loss_source_counts')}`",
        f"- Exit-state frontier best: `{exit_best.get('variant')}` delta-live `{money(exit_best.get('delta_live_cents'))}`",
        f"- Blockers: `{', '.join(report.get('blockers') or [])}`",
        "",
        "## Conclusion",
        "",
        report.get("conclusion") or "",
        "",
        "## Next",
        "",
    ]
    lines.extend(f"- {item}" for item in report.get("next") or [])
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    report = build_report()
    write_outputs(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
