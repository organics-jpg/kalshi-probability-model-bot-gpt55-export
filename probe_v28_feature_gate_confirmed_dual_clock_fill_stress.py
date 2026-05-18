"""Fragility stress for confirmed dual-clock fill diagnostic composite.

Research-only; no live bot changes or orders.

The confirmed dual-clock fill composite is the first diagnostic branch that
clears coverage, source share, cushion, and the refreshed live baseline
together. This probe audits whether that result is robust or mostly carried by
one/two rescued markets.
"""
from __future__ import annotations

import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
SOURCE_JSON = OUT_DIR / "v28_feature_gate_confirmed_dual_clock_fill_latest.json"
OUT_JSON = OUT_DIR / "v28_feature_gate_confirmed_dual_clock_fill_stress_latest.json"
OUT_MD = OUT_DIR / "v28_feature_gate_confirmed_dual_clock_fill_stress_latest.md"

LIVE_SUMMARY_JSON = ROOT / "stats" / "live_mushroom_v28_size2" / "summary.json"


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
        return float(value)
    except (TypeError, ValueError):
        return default


def diagnostic_lane(payload: dict[str, Any]) -> dict[str, Any]:
    for lane in payload.get("lanes") or []:
        if isinstance(lane, dict) and lane.get("lane") == "diagnostic_prefreeze_context":
            return lane
    return {}


def best_variant(lane: dict[str, Any]) -> dict[str, Any]:
    return lane.get("best") if isinstance(lane.get("best"), dict) else {}


def top_contributions(rows: list[dict[str, Any]], key: str, reverse: bool = True) -> list[dict[str, Any]]:
    return sorted(rows, key=lambda row: fnum(row.get(key)), reverse=reverse)


def build_report() -> dict[str, Any]:
    payload = load_json(SOURCE_JSON)
    lane = diagnostic_lane(payload)
    best = best_variant(lane)
    live_cents = 100.0 * fnum(load_json(LIVE_SUMMARY_JSON).get("net_pnl_total_dollars"))
    suppressed = [row for row in best.get("suppressed_rows_detail") or [] if isinstance(row, dict)]
    worst = [row for row in best.get("worst_rows") or [] if isinstance(row, dict)]
    candidate_net = fnum(best.get("candidate_net_cents"))
    delta_vs_live = candidate_net - live_cents
    positive_suppressed = [row for row in suppressed if fnum(row.get("weighted_delta_vs_current_exit_cents")) > 0]
    positive_suppressed.sort(key=lambda row: fnum(row.get("weighted_delta_vs_current_exit_cents")), reverse=True)
    sensitivity_rows = []
    for row in positive_suppressed[:10]:
        delta = fnum(row.get("weighted_delta_vs_current_exit_cents"))
        stressed_net = candidate_net - delta
        sensitivity_rows.append({
            "stress": f"remove_suppression_{row.get('market')}_{row.get('suppression_rule')}",
            "removed_market": row.get("market"),
            "removed_rule": row.get("suppression_rule"),
            "removed_delta_cents": delta,
            "stressed_net_cents": stressed_net,
            "stressed_delta_vs_live_cents": stressed_net - live_cents,
            "still_beats_live": stressed_net > live_cents,
        })
    rule_counts = Counter(row.get("suppression_rule") for row in suppressed)
    rule_delta = Counter()
    for row in suppressed:
        rule_delta[str(row.get("suppression_rule"))] += fnum(row.get("weighted_delta_vs_current_exit_cents"))
    rule_stresses = []
    for rule, delta in sorted(rule_delta.items(), key=lambda item: item[1], reverse=True):
        stressed_net = candidate_net - delta
        rule_stresses.append({
            "stress": f"remove_all_{rule}",
            "suppressed_rows_removed": int(rule_counts.get(rule) or 0),
            "removed_delta_cents": delta,
            "stressed_net_cents": stressed_net,
            "stressed_delta_vs_live_cents": stressed_net - live_cents,
            "still_beats_live": stressed_net > live_cents,
        })
    source_share = fnum(best.get("reconstructed_share"))
    coverage = fnum(best.get("coverage_pct"))
    source_margin_rows = None
    source_counts = best.get("source_counts") if isinstance(best.get("source_counts"), dict) else {}
    approved = fnum(source_counts.get("approved_entry"))
    reconstructed = fnum(best.get("entries")) - approved
    if approved + reconstructed:
        max_reconstructed_at_gate = int((0.35 * (approved + reconstructed)) // 1)
        source_margin_rows = max_reconstructed_at_gate - int(reconstructed)
    blockers = []
    if delta_vs_live <= 100.0:
        blockers.append("live_margin_le_1_full_loss")
    if sensitivity_rows and not sensitivity_rows[0]["still_beats_live"]:
        blockers.append("top_single_suppression_required_to_beat_live")
    if any(not row["still_beats_live"] for row in rule_stresses):
        blockers.append("component_required_to_beat_live")
    if source_margin_rows is not None and source_margin_rows <= 0:
        blockers.append("source_gate_zero_row_margin")
    if coverage < 77.0:
        blockers.append("coverage_margin_thin_lt_77pct")
    blockers.extend(best.get("blockers") or [])
    return {
        "generated_at_utc": utc_now_iso(),
        "source_artifact": str(SOURCE_JSON),
        "live_baseline_cents": live_cents,
        "candidate": {
            "policy": (best.get("variant") or {}).get("name"),
            "entries": best.get("entries"),
            "settled": best.get("settled"),
            "wins": best.get("wins"),
            "losses": best.get("losses"),
            "coverage_pct": coverage,
            "reconstructed_share": source_share,
            "source_counts": source_counts,
            "candidate_net_cents": candidate_net,
            "delta_vs_live_cents": delta_vs_live,
            "full_loss_cushion": best.get("full_loss_cushion"),
            "suppressed_rows": best.get("suppressed_rows"),
            "suppression_rule_counts": best.get("suppression_rule_counts"),
            "blockers": best.get("blockers") or [],
        },
        "rule_delta_cents": dict(rule_delta),
        "top_suppression_sensitivity": sensitivity_rows,
        "rule_component_stress": rule_stresses,
        "top_positive_suppressions": positive_suppressed[:8],
        "worst_rows": worst,
        "stress_blockers": blockers,
        "interpretation": interpretation(delta_vs_live, sensitivity_rows, rule_stresses, source_margin_rows, coverage, blockers),
    }


def interpretation(
    delta_vs_live: float,
    sensitivity_rows: list[dict[str, Any]],
    rule_stresses: list[dict[str, Any]],
    source_margin_rows: int | None,
    coverage: float,
    blockers: list[str],
) -> list[str]:
    notes = [
        "Research-only fragility stress; no live bot changes or orders.",
        f"Diagnostic live margin is {delta_vs_live:.1f}c.",
    ]
    if sensitivity_rows:
        top = sensitivity_rows[0]
        notes.append(
            f"Removing the largest single suppression ({top.get('removed_market')}, {top.get('removed_delta_cents')}c) "
            f"leaves {top.get('stressed_delta_vs_live_cents')}c vs live."
        )
    if rule_stresses:
        top_rule = rule_stresses[0]
        notes.append(
            f"Largest component is {top_rule.get('stress')} worth {top_rule.get('removed_delta_cents')}c; "
            f"without it the candidate is {top_rule.get('stressed_delta_vs_live_cents')}c vs live."
        )
    notes.append(f"Source gate row margin is {source_margin_rows}; coverage is {coverage:.2f}%.")
    notes.append(f"Stress blockers: {blockers}")
    return notes


def fmt(value: Any) -> str:
    if value is None:
        return "n/a"
    if isinstance(value, float):
        return f"{value:.3f}"
    return str(value)


def write_md(report: dict[str, Any]) -> None:
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8")
    candidate = report.get("candidate") or {}
    lines = [
        "# v28 Feature-Gate Confirmed Dual-Clock Fill Stress",
        "",
        "Research-only; no live bot changes or orders.",
        "",
        f"- Generated UTC: `{report.get('generated_at_utc')}`",
        f"- Source artifact: `{report.get('source_artifact')}`",
        f"- Policy: `{candidate.get('policy')}`",
        f"- Candidate net: `{fmt(candidate.get('candidate_net_cents'))}c`",
        f"- Delta vs live: `{fmt(candidate.get('delta_vs_live_cents'))}c`",
        f"- W/L: `{candidate.get('wins')}/{candidate.get('losses')}`",
        f"- Coverage/source: `{fmt(candidate.get('coverage_pct'))}%` / `{fmt(candidate.get('reconstructed_share'))}`",
        "",
        "## Interpretation",
        "",
    ]
    lines.extend(f"- {note}" for note in report.get("interpretation") or [])
    lines.extend([
        "",
        "## Rule Component Stress",
        "",
        "| stress | rows removed | removed delta | stressed net | stressed vs live | still beats live |",
        "|---|---:|---:|---:|---:|---|",
    ])
    for row in report.get("rule_component_stress") or []:
        lines.append(
            f"| `{row.get('stress')}` | {row.get('suppressed_rows_removed')} | "
            f"{fmt(row.get('removed_delta_cents'))} | {fmt(row.get('stressed_net_cents'))} | "
            f"{fmt(row.get('stressed_delta_vs_live_cents'))} | {row.get('still_beats_live')} |"
        )
    lines.extend([
        "",
        "## Top Single-Suppression Stress",
        "",
        "| stress | removed delta | stressed net | stressed vs live | still beats live |",
        "|---|---:|---:|---:|---|",
    ])
    for row in report.get("top_suppression_sensitivity") or []:
        lines.append(
            f"| `{row.get('stress')}` | {fmt(row.get('removed_delta_cents'))} | "
            f"{fmt(row.get('stressed_net_cents'))} | {fmt(row.get('stressed_delta_vs_live_cents'))} | "
            f"{row.get('still_beats_live')} |"
        )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    report = build_report()
    write_md(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
