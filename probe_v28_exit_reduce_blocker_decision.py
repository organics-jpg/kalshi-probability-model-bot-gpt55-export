"""Decision ledger for the v28 probability-reduce exit suppression branch.

Research-only; no live bot changes or orders.

This consolidates the frozen blanket reducer and its loss-control child
watches so the next review can see whether the exit repair is promotable,
invalidated, or still waiting for strict post-freeze suppressions.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"

BASE_JSON = OUT_DIR / "v28_frozen_exit_reduce_suppression_latest.json"
RISK_JSON = OUT_DIR / "v28_exit_reduce_suppression_risk_ledger_latest.json"
DEPTH_JSON = OUT_DIR / "v28_frozen_exit_reduce_depth_gate_latest.json"
OBS_JSON = OUT_DIR / "v28_frozen_exit_reduce_observable_loss_control_watch_latest.json"
GEOM_JSON = OUT_DIR / "v28_frozen_exit_reduce_geometry_relaxed_watch_latest.json"
RUNWAY_JSON = OUT_DIR / "v28_exit_reduce_promotion_runway_latest.json"

OUT_JSON = OUT_DIR / "v28_exit_reduce_blocker_decision_latest.json"
OUT_MD = OUT_DIR / "v28_exit_reduce_blocker_decision_latest.md"

MIN_SETTLED = 30
MIN_SUPPRESSED_DECISIONS = 30
MIN_CUSHION = 3


def load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
    return payload if isinstance(payload, dict) else {}


def as_float(value: Any) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def as_int(value: Any) -> int:
    return int(as_float(value))


def lane_variant(payload: dict[str, Any], lane_name: str, index: int = 0) -> dict[str, Any]:
    for lane in payload.get("lanes") or []:
        if isinstance(lane, dict) and lane.get("lane") == lane_name:
            variants = [row for row in lane.get("variants") or [] if isinstance(row, dict)]
            if len(variants) > index:
                return variants[index]
    return {}


def summarize_variant(source: str, variant: dict[str, Any], strict: bool) -> dict[str, Any]:
    summary = variant.get("summary") if isinstance(variant.get("summary"), dict) else {}
    blockers = list(variant.get("blockers") or [])
    settled = as_int(summary.get("settled"))
    suppressed = as_int(summary.get("suppressed_exits", summary.get("suppressed")))
    delta = as_float(summary.get("delta_vs_current_cents"))
    loss_cost = as_float(summary.get("loss_control_cost_cents"))
    cushion = as_int(summary.get("full_loss_cushion_estimate"))
    missing: list[str] = []
    if strict and settled < MIN_SETTLED:
        missing.append(f"settled+{MIN_SETTLED - settled}")
    if strict and suppressed < MIN_SUPPRESSED_DECISIONS:
        missing.append(f"suppressed+{MIN_SUPPRESSED_DECISIONS - suppressed}")
    if delta <= 0:
        missing.append("positive_delta")
    if loss_cost < 0:
        missing.append("no_loss_control_cost")
    if cushion < MIN_CUSHION:
        missing.append(f"cushion+{MIN_CUSHION - cushion}")
    return {
        "source": source,
        "candidate": variant.get("candidate"),
        "rule": variant.get("rule"),
        "strict_post_freeze": strict,
        "settled": settled,
        "delta_vs_current_cents": delta,
        "suppressed_exits": suppressed,
        "suppressed_winners": as_int(summary.get("suppressed_winners")),
        "suppressed_losers": as_int(summary.get("suppressed_losers")),
        "winner_recovery_cents": as_float(summary.get("winner_clip_recovered_cents", summary.get("winner_recovery_cents"))),
        "loss_control_cost_cents": loss_cost,
        "full_loss_cushion_estimate": cushion,
        "blockers": blockers,
        "missing_review_gates": missing,
        "ready_for_review": strict and not missing and not blockers,
    }


def summarize_base(base: dict[str, Any], runway: dict[str, Any]) -> dict[str, Any]:
    summary = base.get("summary") if isinstance(base.get("summary"), dict) else {}
    blockers = list(base.get("blockers") or [])
    invalidators = list(runway.get("invalidators_now") or [])
    suppressed_rows = [row for row in base.get("rows") or [] if isinstance(row, dict) and row.get("suppressed")]
    harmful = [row for row in suppressed_rows if as_float(row.get("delta_cents")) < 0]
    helpful = [row for row in suppressed_rows if as_float(row.get("delta_cents")) > 0]
    return {
        "candidate": (base.get("freeze") or {}).get("candidate"),
        "freeze_ts_utc": (base.get("freeze") or {}).get("freeze_ts_utc"),
        "rule": (base.get("freeze") or {}).get("rule"),
        "settled": as_int(summary.get("settled")),
        "delta_vs_current_cents": as_float(summary.get("delta_vs_current_cents")),
        "suppressed_exits": as_int(summary.get("suppressed_exits")),
        "suppressed_winner_recovery_cents": as_float(summary.get("winner_clip_recovered_cents")),
        "suppressed_loss_control_cost_cents": as_float(summary.get("loss_control_cost_cents")),
        "suppressed_harmful_rows": len(harmful),
        "suppressed_helpful_rows": len(helpful),
        "blockers": blockers,
        "invalidators_now": invalidators,
        "candidate_live_ready": bool(base.get("candidate_live_ready")),
        "harmful_rows": harmful,
    }


def physical_read(base_summary: dict[str, Any], child_rows: list[dict[str, Any]]) -> list[str]:
    notes = []
    if base_summary.get("suppressed_harmful_rows"):
        notes.append(
            "Blanket p_hold>=0.75 suppression is not promotable: it has positive delta, "
            "but at least one suppressed loser turned a controlled reduce exit into a large loss."
        )
    else:
        notes.append("Blanket suppression has no harmful suppressed rows in the current refresh.")
    clean_diagnostic = [
        row for row in child_rows
        if not row.get("strict_post_freeze")
        and row.get("delta_vs_current_cents", 0) > 0
        and row.get("loss_control_cost_cents", 0) >= 0
        and row.get("suppressed_losers", 0) == 0
    ]
    if clean_diagnostic:
        best = max(clean_diagnostic, key=lambda row: as_float(row.get("delta_vs_current_cents")))
        notes.append(
            f"Best clean diagnostic guard is {best.get('candidate')} with "
            f"{best.get('delta_vs_current_cents')}c delta, {best.get('suppressed_exits')} suppressions, "
            f"and no loss-control cost."
        )
    strict_with_suppression = [row for row in child_rows if row.get("strict_post_freeze") and row.get("suppressed_exits", 0) > 0]
    if not strict_with_suppression:
        notes.append("Strict child watches have not yet produced enough post-freeze suppressed decisions to judge the repair.")
    else:
        best_strict = max(strict_with_suppression, key=lambda row: as_float(row.get("delta_vs_current_cents")))
        notes.append(
            f"Best strict child with actual suppressions is {best_strict.get('candidate')} "
            f"at {best_strict.get('delta_vs_current_cents')}c with blockers {best_strict.get('blockers')}."
        )
    notes.append(
        "Action: keep the cleaner child watches collecting; do not promote blanket reduce suppression while "
        "loss-control cost or suppressed-loser blockers remain."
    )
    return notes


def build_report() -> dict[str, Any]:
    base = load_json(BASE_JSON)
    risk = load_json(RISK_JSON)
    depth = load_json(DEPTH_JSON)
    obs = load_json(OBS_JSON)
    geom = load_json(GEOM_JSON)
    runway = load_json(RUNWAY_JSON)

    child_rows = [
        summarize_variant("depth_gate_diagnostic", lane_variant(depth, "diagnostic_from_reduce_freeze", 0), False),
        summarize_variant("depth_gate_strict", lane_variant(depth, "post_depth_gate_birth", 0), True),
        summarize_variant("observable_loss_control_diagnostic", lane_variant(obs, "diagnostic_from_reduce_freeze", 0), False),
        summarize_variant("observable_loss_control_strict", lane_variant(obs, "post_observable_birth", 0), True),
    ]
    geom_diag = geom.get("diagnostic", {}).get("best") if isinstance(geom.get("diagnostic"), dict) else {}
    geom_strict = geom.get("strict_post_freeze", {}).get("best") if isinstance(geom.get("strict_post_freeze"), dict) else {}
    if isinstance(geom_diag, dict):
        child_rows.append(summarize_variant("side_geometry_diagnostic", {"candidate": geom_diag.get("policy"), "summary": geom_diag, "blockers": []}, False))
    if isinstance(geom_strict, dict):
        child_rows.append(summarize_variant("side_geometry_strict", {"candidate": geom_strict.get("policy"), "summary": geom_strict, "blockers": geom.get("blockers") or []}, True))

    base_summary = summarize_base(base, runway)
    report = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "purpose": "Research-only decision ledger for probability-reduce exit suppression blockers.",
        "source_paths": {
            "base": str(BASE_JSON),
            "risk": str(RISK_JSON),
            "depth": str(DEPTH_JSON),
            "observable": str(OBS_JSON),
            "geometry": str(GEOM_JSON),
            "runway": str(RUNWAY_JSON),
        },
        "requirements": {
            "min_settled": MIN_SETTLED,
            "min_suppressed_decisions": MIN_SUPPRESSED_DECISIONS,
            "min_full_loss_cushion": MIN_CUSHION,
            "loss_control_cost_must_be_nonnegative": True,
        },
        "base_blanket_suppression": base_summary,
        "risk_group_summaries": risk.get("suppressed_group_summaries") or {},
        "child_watch_summaries": child_rows,
    }
    report["interpretation"] = physical_read(base_summary, child_rows)
    report["decision"] = "watch_child_repairs_do_not_promote_blanket"
    return report


def fmt(value: Any) -> str:
    if isinstance(value, float):
        return f"{value:.3f}"
    if value is None:
        return "None"
    return str(value)


def write_md(report: dict[str, Any]) -> None:
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8")
    base = report.get("base_blanket_suppression") or {}
    lines = [
        "# v28 Exit Reduce Blocker Decision",
        "",
        "Research-only; no live bot changes or orders.",
        "",
        f"- Generated UTC: `{report.get('generated_at_utc')}`",
        f"- Decision: `{report.get('decision')}`",
        "",
        "## Interpretation",
        "",
    ]
    for note in report.get("interpretation") or []:
        lines.append(f"- {note}")
    lines.extend(
        [
            "",
            "## Blanket Reduce Suppression",
            "",
            f"- Candidate: `{base.get('candidate')}`",
            f"- Freeze UTC: `{base.get('freeze_ts_utc')}`",
            f"- Settled: `{base.get('settled')}`",
            f"- Delta vs current exits: `{fmt(base.get('delta_vs_current_cents'))}c`",
            f"- Suppressed exits: `{base.get('suppressed_exits')}`",
            f"- Winner recovery / loss-control cost: `{fmt(base.get('suppressed_winner_recovery_cents'))}c / {fmt(base.get('suppressed_loss_control_cost_cents'))}c`",
            f"- Helpful/harmful suppressed rows: `{base.get('suppressed_helpful_rows')}/{base.get('suppressed_harmful_rows')}`",
            f"- Blockers: `{base.get('blockers')}`",
            f"- Invalidators now: `{base.get('invalidators_now')}`",
            "",
            "## Child Watch Summary",
            "",
            "| source | candidate | strict | settled | suppressed | sup W/L | delta c | loss cost c | cushion | blockers | missing gates |",
            "|---|---|---:|---:|---:|---:|---:|---:|---:|---|---|",
        ]
    )
    for row in report.get("child_watch_summaries") or []:
        blockers = ", ".join(str(x) for x in row.get("blockers") or []) or "none"
        missing = ", ".join(str(x) for x in row.get("missing_review_gates") or []) or "none"
        lines.append(
            f"| {row.get('source')} | {row.get('candidate')} | {row.get('strict_post_freeze')} | "
            f"{row.get('settled')} | {row.get('suppressed_exits')} | "
            f"{row.get('suppressed_winners')}/{row.get('suppressed_losers')} | "
            f"{fmt(row.get('delta_vs_current_cents'))} | {fmt(row.get('loss_control_cost_cents'))} | "
            f"{row.get('full_loss_cushion_estimate')} | {blockers} | {missing} |"
        )
    harmful = base.get("harmful_rows") or []
    lines.extend(["", "## Harmful Blanket Rows", ""])
    if not harmful:
        lines.append("- None in this refresh.")
    else:
        lines.append("| market | side/result | p_hold | drawdown | exit | current c | hold c | delta c | worst mark |")
        lines.append("|---|---|---:|---:|---:|---:|---:|---:|---:|")
        for row in harmful:
            lines.append(
                f"| {row.get('market')} | {row.get('side')}/{row.get('result')} | "
                f"{fmt(row.get('p_hold'))} | {fmt(row.get('fair_drawdown_cents'))} | "
                f"{row.get('exit_cents')} | {fmt(row.get('current_cents'))} | "
                f"{fmt(row.get('hold_cents'))} | {fmt(row.get('delta_cents'))} | "
                f"{row.get('worst_post_exit_hold_mark_cents')} |"
            )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    report = build_report()
    write_md(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
