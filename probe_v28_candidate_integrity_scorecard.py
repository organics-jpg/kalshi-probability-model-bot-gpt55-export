"""Integrity scorecard for positive v28 candidate lanes.

Research-only; no live bot changes and no orders.

This report separates "positive PnL in the tracker" from "credible enough to
consider." It reads current tracking artifacts plus source-mix stress audits and
adds explicit blockers for sample size, coverage, reconstructed-row dependence,
and full-loss fragility.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
PNL_JSON = OUT_DIR / "v28_candidate_pnl_tracker_latest.json"
EARLY_NO_STRESS_JSON = OUT_DIR / "v28_early_no_boundary_decay_repair_stress_latest.json"
COMPOSITE_STRESS_JSON = OUT_DIR / "v28_composite_false_conviction_repair_stress_latest.json"
BOUNDARY_CLOCK_SOURCE_STRESS_JSON = OUT_DIR / "v28_boundary_clock_source_stress_latest.json"
SOFT_FRONTIER_SOURCE_STRESS_JSON = OUT_DIR / "v28_boundary_clock_feature_gate_soft_frontier_source_stress_latest.json"
SOFT_FRONTIER_SIZE_SHRINK_SOURCE_STRESS_JSON = OUT_DIR / "v28_soft_frontier_size_shrink_source_stress_latest.json"
SOFT_FRONTIER_MIDPRICE_EXIT_STACK_RUNWAY_JSON = OUT_DIR / "v28_soft_frontier_midprice_boundary_exit_stack_runway_latest.json"
TOP_STRICT_TARGET_SOURCE_FRAGILITY_JSON = OUT_DIR / "v28_top_strict_target_source_fragility_latest.json"
LIVE_READINESS_JSON = OUT_DIR / "v28_live_trade_readiness_latest.json"
OUT_JSON = OUT_DIR / "v28_candidate_integrity_scorecard_latest.json"
OUT_MD = OUT_DIR / "v28_candidate_integrity_scorecard_latest.md"

MIN_SETTLED = 30
TARGET_COVERAGE_MIN = 75.0
TARGET_COVERAGE_MAX = 90.0
MAX_RECONSTRUCTED_SHARE = 0.35
MIN_FULL_LOSS_CUSHION = 3
MIN_SUPPRESSED_DECISIONS = 30


def load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
    return payload if isinstance(payload, dict) else {}


def as_float(value: Any) -> float | None:
    if value is None or value == "":
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def as_int(value: Any) -> int | None:
    number = as_float(value)
    if number is None:
        return None
    return int(number)


def net_cents(row: dict[str, Any]) -> float:
    return as_float(row.get("net_cents_after_entry_fee")) or as_float(row.get("net_cents")) or 0.0


def coverage(row: dict[str, Any]) -> float | None:
    return as_float(row.get("coverage_pct"))


def is_target_coverage(row: dict[str, Any]) -> bool:
    cov = coverage(row)
    return cov is not None and TARGET_COVERAGE_MIN <= cov <= TARGET_COVERAGE_MAX


def is_pure_exit_policy(row: dict[str, Any]) -> bool:
    gate = str(row.get("gate") or "")
    return gate.startswith("exit_") or gate in {
        "dual_exit_book_gap_else_reduce",
        "exit_book_gap_loss_guard",
    }


def source_counts(stress: dict[str, Any]) -> dict[str, int]:
    counts = stress.get("source_counts") or {}
    candidate = counts.get("candidate") if isinstance(counts, dict) else {}
    if isinstance(candidate, dict):
        return candidate
    return counts if isinstance(counts, dict) else {}


def reconstructed_share_from_stress(stress: dict[str, Any]) -> float | None:
    counts = source_counts(stress)
    if not counts:
        return None
    total = sum(int(v or 0) for v in counts.values())
    if total <= 0:
        return None
    reconstructed = sum(int(v or 0) for key, v in counts.items() if key != "approved_entry")
    return reconstructed / total


def full_loss_cushion_from_stress(stress: dict[str, Any]) -> int | None:
    direct = as_int(stress.get("full_loss_cushion_estimate"))
    if direct is not None:
        return direct
    runway = stress.get("future_loss_runway")
    if not isinstance(runway, list):
        runway = stress.get("full_loss_runway")
    if not isinstance(runway, list):
        return None
    cushion = 0
    for row in runway:
        losses = as_int(row.get("added_full_losses")) or 0
        if row.get("still_positive") is True:
            cushion = max(cushion, losses)
    return cushion


def stress_by_gate() -> dict[str, dict[str, Any]]:
    boundary_clock = load_json(BOUNDARY_CLOCK_SOURCE_STRESS_JSON)
    boundary_lanes = {
        str(row.get("lane") or ""): row
        for row in (boundary_clock.get("lanes") or [])
        if isinstance(row, dict)
    }
    soft_frontier = load_json(SOFT_FRONTIER_SOURCE_STRESS_JSON)
    stresses = {
        "early_no_boundary_decay_repair_entry": load_json(EARLY_NO_STRESS_JSON),
        "composite_false_conviction_repair_entry": load_json(COMPOSITE_STRESS_JSON),
        "boundary_clock_repair_entry": boundary_lanes.get("boundary_clock_repair_entry") or {},
        "boundary_clock_fv_entry_bridge": boundary_lanes.get("boundary_clock_fv_entry_bridge") or {},
    }
    for row in soft_frontier.get("policies") or []:
        if not isinstance(row, dict):
            continue
        gate = str(row.get("gate") or "")
        policy = str(row.get("policy") or "")
        if gate and policy:
            stresses[f"{gate}::{policy}"] = row
    size_shrink = load_json(SOFT_FRONTIER_SIZE_SHRINK_SOURCE_STRESS_JSON)
    for row in size_shrink.get("policies") or []:
        if not isinstance(row, dict):
            continue
        gate = str(row.get("gate") or "")
        policy = str(row.get("policy") or "")
        if gate and policy:
            stresses[f"{gate}::{policy}"] = row
    midprice_exit_stack_runway = load_json(SOFT_FRONTIER_MIDPRICE_EXIT_STACK_RUNWAY_JSON)
    for row in midprice_exit_stack_runway.get("rows") or []:
        if not isinstance(row, dict):
            continue
        candidate = str(row.get("candidate") or "")
        counts = row.get("post_stack_source_counts") if isinstance(row.get("post_stack_source_counts"), dict) else {}
        if candidate:
            stresses[f"soft_frontier_midprice_boundary_exit_stack::{candidate}"] = {
                "source_counts": {"candidate": counts},
                "full_loss_cushion_estimate": row.get("post_stack_full_loss_cushion_estimate"),
                "blockers": row.get("runway_blockers") or [],
                "warnings": [
                    "source_and_cushion_from_post_stack_runway",
                    *([] if counts else ["post_stack_source_sample_empty"]),
                ],
            }
    strict_target = load_json(TOP_STRICT_TARGET_SOURCE_FRAGILITY_JSON)
    for row in strict_target.get("candidates") or []:
        if not isinstance(row, dict):
            continue
        gate = str(row.get("gate") or "")
        policy = str(row.get("policy") or "")
        stats = row.get("source_stats") if isinstance(row.get("source_stats"), dict) else {}
        source_counts_row = stats.get("entry_source_counts") if isinstance(stats.get("entry_source_counts"), dict) else {}
        if gate and policy and source_counts_row:
            stresses[f"{gate}::{policy}"] = {
                "source_counts": {"candidate": source_counts_row},
                "full_loss_cushion_estimate": row.get("full_loss_cushion_estimate"),
                "blockers": row.get("blockers") or [],
                "warnings": ["source_fragility_from_top_strict_target_audit"],
            }
    return stresses


def stress_for_row(row: dict[str, Any], stresses: dict[str, dict[str, Any]]) -> dict[str, Any] | None:
    gate = str(row.get("gate") or "")
    policy = str(row.get("policy") or "")
    return stresses.get(f"{gate}::{policy}") or stresses.get(gate)


def integrity_for_row(row: dict[str, Any], stress: dict[str, Any] | None) -> dict[str, Any]:
    blockers = []
    for blocker in row.get("blockers") or []:
        blocker_s = str(blocker)
        if blocker_s and blocker_s not in blockers:
            blockers.append(blocker_s)
    settled = as_int(row.get("settled")) or 0
    cov = coverage(row)
    net = net_cents(row)
    if settled < MIN_SETTLED:
        blockers.append("settled_lt_30")
    if cov is None or cov < TARGET_COVERAGE_MIN:
        blockers.append("coverage_too_low")
    if cov is not None and cov > TARGET_COVERAGE_MAX:
        blockers.append("coverage_too_high")
    if net <= 0.0:
        blockers.append("net_not_positive")

    reconstructed_share = None
    full_loss_cushion = None
    stress_warnings: list[str] = []
    row_sim_share = as_float(row.get("simulated_share"))
    row_cushion = as_int(row.get("full_loss_cushion_estimate"))
    if row_cushion is None and net > 0.0:
        row_cushion = int(net // 100.0)
    if stress:
        reconstructed_share = reconstructed_share_from_stress(stress)
        full_loss_cushion = full_loss_cushion_from_stress(stress)
        stress_warnings = [str(item) for item in (stress.get("warnings") or [])]
        stress_warnings.extend(str(item) for item in (stress.get("blockers") or []))
        if reconstructed_share is not None and reconstructed_share > MAX_RECONSTRUCTED_SHARE:
            blockers.append("reconstructed_share_gt_35pct")
        if full_loss_cushion is not None and full_loss_cushion < MIN_FULL_LOSS_CUSHION:
            blockers.append("full_loss_cushion_lt_3")
    else:
        if row_sim_share is None:
            blockers.append("no_source_stress_audit")
        else:
            stress_warnings.append("source_mix_from_tracker_only")
        full_loss_cushion = row_cushion
    if row_sim_share is not None and row_sim_share > MAX_RECONSTRUCTED_SHARE:
        blockers.append("simulated_share_gt_35pct")
    if reconstructed_share is None and "post_stack_source_sample_empty" not in stress_warnings:
        reconstructed_share = row_sim_share
    if full_loss_cushion is None:
        full_loss_cushion = row_cushion
    if full_loss_cushion is not None and full_loss_cushion < MIN_FULL_LOSS_CUSHION:
        blockers.append("full_loss_cushion_lt_3")
    blockers = list(dict.fromkeys(blockers))

    return {
        "gate": row.get("gate"),
        "policy": row.get("policy"),
        "entries": row.get("entries"),
        "settled": settled,
        "wins": row.get("wins"),
        "losses": row.get("losses"),
        "coverage_pct": cov,
        "net_cents": net,
        "live_ready": row.get("live_ready"),
        "simulated_share": row.get("simulated_share"),
        "stress_reconstructed_share": reconstructed_share,
        "stress_full_loss_cushion": full_loss_cushion,
        "stress_warnings": stress_warnings,
        "integrity_pass": not blockers,
        "blockers": blockers,
    }


def exit_integrity_for_row(row: dict[str, Any]) -> dict[str, Any]:
    blockers = []
    settled = as_int(row.get("settled")) or 0
    net = net_cents(row)
    delta = as_float(row.get("delta_vs_current_cents"))
    suppressed = as_int(row.get("suppressed_exits")) or 0
    winner_recovery = as_float(row.get("winner_clip_recovered_cents"))
    loss_cost = as_float(row.get("loss_control_cost_cents"))
    cushion = as_int(row.get("full_loss_cushion_estimate"))
    if cushion is None and net > 0.0:
        cushion = int(net // 100.0)
    if settled < MIN_SETTLED:
        blockers.append("settled_lt_30")
    if suppressed < MIN_SUPPRESSED_DECISIONS:
        blockers.append("suppressed_decisions_lt_30")
    if net <= 0.0:
        blockers.append("net_not_positive")
    if delta is None or delta <= 0.0:
        blockers.append("delta_vs_current_not_positive")
    if loss_cost is not None and loss_cost < 0.0:
        blockers.append("loss_control_cost_negative")
    if cushion is None or cushion < MIN_FULL_LOSS_CUSHION:
        blockers.append("full_loss_cushion_lt_3")
    if row.get("live_ready") is not True:
        blockers.append("live_ready_false")
    return {
        "gate": row.get("gate"),
        "policy": row.get("policy"),
        "settled": settled,
        "wins": row.get("wins"),
        "losses": row.get("losses"),
        "net_cents": net,
        "delta_vs_current_cents": delta,
        "suppressed_exits": suppressed,
        "winner_clip_recovered_cents": winner_recovery,
        "loss_control_cost_cents": loss_cost,
        "full_loss_cushion_estimate": cushion,
        "live_ready": row.get("live_ready"),
        "exit_integrity_pass": not blockers,
        "blockers": blockers,
    }


def build_report() -> dict[str, Any]:
    pnl = load_json(PNL_JSON)
    live = load_json(LIVE_READINESS_JSON)
    stresses = stress_by_gate()
    rows = pnl.get("rows") or pnl.get("merged_rows") or pnl.get("lanes") or []
    if not isinstance(rows, list):
        rows = []
    candidates = [
        row for row in rows
        if is_target_coverage(row) and net_cents(row) > 0.0
    ]
    scored = [
        integrity_for_row(row, stress_for_row(row, stresses))
        for row in candidates
    ]
    exit_candidates = [
        row for row in rows
        if is_pure_exit_policy(row) and net_cents(row) > 0.0
    ]
    exit_scored = [exit_integrity_for_row(row) for row in exit_candidates]
    scored.sort(
        key=lambda row: (
            bool(row.get("integrity_pass")),
            as_float(row.get("net_cents")) or -999999.0,
            as_float(row.get("settled")) or 0.0,
        ),
        reverse=True,
    )
    exit_scored.sort(
        key=lambda row: (
            bool(row.get("exit_integrity_pass")),
            as_float(row.get("net_cents")) or -999999.0,
            as_float(row.get("delta_vs_current_cents")) or -999999.0,
            as_float(row.get("suppressed_exits")) or 0.0,
        ),
        reverse=True,
    )
    return {
        "purpose": "Integrity audit for positive target-coverage entry lanes and pure exit-policy lanes.",
        "requirements": {
            "min_settled": MIN_SETTLED,
            "coverage_band": [TARGET_COVERAGE_MIN, TARGET_COVERAGE_MAX],
            "max_reconstructed_share": MAX_RECONSTRUCTED_SHARE,
            "min_full_loss_cushion": MIN_FULL_LOSS_CUSHION,
            "min_suppressed_exit_decisions": MIN_SUPPRESSED_DECISIONS,
        },
        "control": (pnl.get("control") if isinstance(pnl.get("control"), dict) else {}),
        "any_live_ready": live.get("any_live_ready"),
        "candidate_count": len(scored),
        "integrity_pass_count": sum(1 for row in scored if row.get("integrity_pass")),
        "exit_candidate_count": len(exit_scored),
        "exit_integrity_pass_count": sum(1 for row in exit_scored if row.get("exit_integrity_pass")),
        "candidates": scored,
        "exit_candidates": exit_scored,
        "interpretation": interpretation(scored, exit_scored),
    }


def interpretation(rows: list[dict[str, Any]], exit_rows: list[dict[str, Any]]) -> list[str]:
    if not rows:
        notes = ["No positive target-coverage lanes are currently available."]
    else:
        notes = []
    passed = [row for row in rows if row.get("integrity_pass")]
    notes.extend([
        f"Positive target-coverage lanes scored: {len(rows)}.",
        f"Entry/FV integrity-pass lanes: {len(passed)}.",
    ])
    if rows:
        best = rows[0]
        notes.append(
            f"Top entry/FV lane is {best.get('gate')} / {best.get('policy')} with net {best.get('net_cents')}c, settled {best.get('settled')}, blockers {best.get('blockers')}."
        )
    if rows and not passed:
        notes.append("No positive lane currently clears sample, coverage, source-quality, and fragility gates.")
    exit_passed = [row for row in exit_rows if row.get("exit_integrity_pass")]
    notes.append(f"Positive pure exit-policy lanes scored: {len(exit_rows)}.")
    notes.append(f"Exit integrity-pass lanes: {len(exit_passed)}.")
    if exit_rows:
        best_exit = exit_rows[0]
        notes.append(
            f"Top exit lane is {best_exit.get('gate')} / {best_exit.get('policy')} with net {best_exit.get('net_cents')}c, delta {best_exit.get('delta_vs_current_cents')}c, suppressed {best_exit.get('suppressed_exits')}, blockers {best_exit.get('blockers')}."
        )
    return notes


def fmt(value: Any) -> str:
    if value is None:
        return "None"
    if isinstance(value, float):
        return f"{value:.6f}"
    return str(value)


def write_md(report: dict[str, Any]) -> None:
    lines = [
        "# v28 Candidate Integrity Scorecard",
        "",
        "Research-only; no live bot changes and no orders.",
        "",
        f"- Positive target-coverage lanes: `{report.get('candidate_count')}`",
        f"- Integrity-pass lanes: `{report.get('integrity_pass_count')}`",
        f"- Positive pure exit-policy lanes: `{report.get('exit_candidate_count')}`",
        f"- Exit integrity-pass lanes: `{report.get('exit_integrity_pass_count')}`",
        f"- Any live-ready candidate: `{report.get('any_live_ready')}`",
        "",
        "## Interpretation",
        "",
    ]
    for note in report.get("interpretation") or []:
        lines.append(f"- {note}")
    lines.extend([
        "",
        "## Candidates",
        "",
        "| gate | policy | settled | W/L | coverage | net c | recon share | loss cushion | pass | blockers |",
        "|---|---|---:|---:|---:|---:|---:|---:|---|---|",
    ])
    for row in report.get("candidates") or []:
        lines.append(
            f"| {row.get('gate')} | {row.get('policy')} | {row.get('settled')} | {row.get('wins')}/{row.get('losses')} | "
            f"{fmt(row.get('coverage_pct'))} | {fmt(row.get('net_cents'))} | {fmt(row.get('stress_reconstructed_share'))} | "
            f"{fmt(row.get('stress_full_loss_cushion'))} | {row.get('integrity_pass')} | {', '.join(row.get('blockers') or []) or 'none'} |"
        )
    lines.extend([
        "",
        "## Pure Exit Policies",
        "",
        "| gate | policy | settled | W/L | net c | delta c | suppressed | winner recovery | loss cost | cushion | pass | blockers |",
        "|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---|---|",
    ])
    for row in report.get("exit_candidates") or []:
        lines.append(
            f"| {row.get('gate')} | {row.get('policy')} | {row.get('settled')} | {row.get('wins')}/{row.get('losses')} | "
            f"{fmt(row.get('net_cents'))} | {fmt(row.get('delta_vs_current_cents'))} | {row.get('suppressed_exits')} | "
            f"{fmt(row.get('winner_clip_recovered_cents'))} | {fmt(row.get('loss_control_cost_cents'))} | "
            f"{fmt(row.get('full_loss_cushion_estimate'))} | {row.get('exit_integrity_pass')} | {', '.join(row.get('blockers') or []) or 'none'} |"
        )
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8")
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    report = build_report()
    write_md(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
