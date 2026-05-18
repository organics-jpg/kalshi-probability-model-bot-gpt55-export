"""Residual failure modes for the broad delayed-recheck candidate.

Research-only; no live bot changes or orders.

The broad soft-frontier/mid-price delayed-recheck branch has strong diagnostic
PnL. This probe classifies its remaining losses so the next repair targets the
physical failure mode rather than another leaderboard shuffle.
"""
from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Any

from probe_v28_soft_frontier_midprice_delayed_recheck_path_risk import OUT_DIR, fnum, load_json, utc_now_iso


WATCH_JSON = OUT_DIR / "v28_frozen_soft_frontier_midprice_delayed_recheck_exit_latest.json"
ENTRY_JSON = OUT_DIR / "v28_soft_frontier_midprice_boundary_shrink_latest.json"
OUT_JSON = OUT_DIR / "v28_soft_frontier_midprice_delayed_recheck_failure_modes_latest.json"
OUT_MD = OUT_DIR / "v28_soft_frontier_midprice_delayed_recheck_failure_modes_latest.md"


def entry_rows_by_key() -> dict[tuple[str, str], dict[str, Any]]:
    payload = load_json(ENTRY_JSON)
    for lane in payload.get("lanes") or []:
        if lane.get("lane") != "diagnostic_entry":
            continue
        for variant in lane.get("variants") or []:
            if variant.get("candidate") != "diagnostic_entry_quarter_midprice_boundary":
                continue
            summary = variant.get("summary") if isinstance(variant.get("summary"), dict) else {}
            return {
                (str(row.get("market") or ""), str(row.get("side") or "")): row
                for row in summary.get("rows") or []
                if isinstance(row, dict)
            }
    return {}


def diagnostic_rows() -> list[dict[str, Any]]:
    payload = load_json(WATCH_JSON)
    for lane in payload.get("lanes") or []:
        if lane.get("lane") == "diagnostic_prefreeze_context":
            return [row for row in lane.get("rows") or [] if isinstance(row, dict)]
    return []


def classify(row: dict[str, Any], entry: dict[str, Any]) -> list[str]:
    tags: list[str] = []
    if str(row.get("source") or "") != "approved_entry":
        tags.append("source_quality_error")
    abs_d = fnum(entry.get("abs_d_sigma"))
    if abs_d < 0.85:
        tags.append("weak_boundary_distance")
    if abs_d < 0.65:
        tags.append("very_weak_boundary_distance")
    ask_prob = fnum(entry.get("ask_prob"))
    if ask_prob < 0.65:
        tags.append("thin_or_cheap_touch")
    raw_edge = fnum(entry.get("raw_edge"))
    if raw_edge < 0.15:
        tags.append("thin_raw_edge")
    p_hold = fnum(row.get("p_hold"), None)
    if p_hold is not None and p_hold < 0.60:
        tags.append("fv_error_low_p_hold_exit")
    fair_drawdown = fnum(row.get("fair_drawdown_cents"), None)
    if fair_drawdown is not None and fair_drawdown > 10:
        tags.append("exit_signal_large_fv_drawdown")
    if row.get("suppressed"):
        if fnum(row.get("weighted_delta_cents")) < 0:
            tags.append("exit_policy_error_bad_suppression")
        else:
            tags.append("exit_policy_repair_helped")
    else:
        hold = fnum(row.get("hold_cents"))
        current = fnum(row.get("current_cents"))
        if hold > current and hold > 0:
            tags.append("exit_policy_error_false_negative_suppression")
        elif hold < current:
            tags.append("exit_policy_correct_loss_control")
    if fnum(row.get("weighted_candidate_cents")) < 0:
        tags.append("candidate_loss")
    if not tags:
        tags.append("clean_or_unclassified")
    return tags


def build_report() -> dict[str, Any]:
    entries = entry_rows_by_key()
    rows = []
    for row in diagnostic_rows():
        entry = entries.get((str(row.get("market") or ""), str(row.get("side") or "")), {})
        tags = classify(row, entry)
        merged = dict(row)
        merged.update(
            {
                "abs_d_sigma": entry.get("abs_d_sigma"),
                "ask_prob": entry.get("ask_prob"),
                "raw_edge": entry.get("raw_edge"),
                "recross_hazard_score": entry.get("recross_hazard_score"),
                "midprice_boundary_band": entry.get("midprice_boundary_band"),
                "tags": tags,
            }
        )
        rows.append(merged)
    losses = [row for row in rows if fnum(row.get("weighted_candidate_cents")) < 0]
    wins = [row for row in rows if fnum(row.get("weighted_candidate_cents")) >= 0]
    tag_counts = Counter(tag for row in rows for tag in row.get("tags") or [])
    loss_tag_counts = Counter(tag for row in losses for tag in row.get("tags") or [])
    source_loss_counts = Counter(str(row.get("source") or "unknown") for row in losses)
    exit_reason_loss_counts = Counter(str(row.get("exit_reason") or "unknown") for row in losses)
    unsuppressed_false_negative = [
        row for row in losses
        if "exit_policy_error_false_negative_suppression" in (row.get("tags") or [])
    ]
    summary = {
        "rows": len(rows),
        "wins": len(wins),
        "losses": len(losses),
        "net_cents": sum(fnum(row.get("weighted_candidate_cents")) for row in rows),
        "loss_cents": sum(fnum(row.get("weighted_candidate_cents")) for row in losses),
        "suppressed_losses": sum(1 for row in losses if row.get("suppressed")),
        "unsuppressed_losses": sum(1 for row in losses if not row.get("suppressed")),
        "source_loss_counts": dict(source_loss_counts),
        "exit_reason_loss_counts": dict(exit_reason_loss_counts),
        "tag_counts": dict(tag_counts),
        "loss_tag_counts": dict(loss_tag_counts),
        "false_negative_suppression_losses": len(unsuppressed_false_negative),
        "false_negative_suppression_recoverable_cents": sum(
            max(0.0, fnum(row.get("hold_cents")) - fnum(row.get("current_cents")))
            for row in unsuppressed_false_negative
        ),
    }
    interpretation = [
        "Research-only residual failure audit; no live bot changes or orders.",
        (
            f"All {summary['losses']} diagnostic candidate losses are unsuppressed; "
            f"suppressed losses = {summary['suppressed_losses']}."
        ),
        (
            "Residual losses are mainly source/entry/FV quality issues if source_quality_error, "
            "weak_boundary_distance, or low p_hold tags dominate; they are exit false negatives "
            "only where hold_cents would have recovered the loss."
        ),
    ]
    return {
        "generated_at_utc": utc_now_iso(),
        "watch_source": str(WATCH_JSON),
        "entry_source": str(ENTRY_JSON),
        "summary": summary,
        "interpretation": interpretation,
        "loss_rows": sorted(losses, key=lambda row: fnum(row.get("weighted_candidate_cents"))),
        "rows": rows,
    }


def fmt(value: Any) -> str:
    if value is None:
        return "n/a"
    if isinstance(value, float):
        return f"{value:.2f}"
    return str(value)


def write_md(report: dict[str, Any]) -> None:
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8")
    summary = report.get("summary") or {}
    lines = [
        "# v28 Soft-Frontier Mid-Price Delayed-Recheck Failure Modes",
        "",
        "Research-only failure-mode audit. No live bot changes or orders.",
        "",
        f"- Generated UTC: `{report.get('generated_at_utc')}`",
        "",
        "## Interpretation",
        "",
    ]
    lines.extend(f"- {note}" for note in report.get("interpretation") or [])
    lines.extend(
        [
            "",
            "## Summary",
            "",
            f"- Rows: `{summary.get('rows')}`",
            f"- W/L: `{summary.get('wins')}/{summary.get('losses')}`",
            f"- Net: `{fmt(summary.get('net_cents'))}c`",
            f"- Loss cents: `{fmt(summary.get('loss_cents'))}c`",
            f"- Suppressed/unsuppressed losses: `{summary.get('suppressed_losses')}/{summary.get('unsuppressed_losses')}`",
            f"- Source loss counts: `{summary.get('source_loss_counts')}`",
            f"- Exit-reason loss counts: `{summary.get('exit_reason_loss_counts')}`",
            f"- Loss tag counts: `{summary.get('loss_tag_counts')}`",
            f"- False-negative suppression losses: `{summary.get('false_negative_suppression_losses')}`",
            f"- False-negative recoverable cents: `{fmt(summary.get('false_negative_suppression_recoverable_cents'))}c`",
            "",
            "## Loss Rows",
            "",
            "| market | side | source | candidate c | current c | hold c | suppress | p_hold | fair dd | abs_d | ask | raw edge | recross | tags |",
            "|---|---|---|---:|---:|---:|---|---:|---:|---:|---:|---:|---:|---|",
        ]
    )
    for row in report.get("loss_rows") or []:
        lines.append(
            f"| {row.get('market')} | {row.get('side')} | {row.get('source')} | "
            f"{fmt(row.get('weighted_candidate_cents'))} | {fmt(row.get('current_cents'))} | {fmt(row.get('hold_cents'))} | "
            f"{row.get('suppressed')} | {fmt(row.get('p_hold'))} | {fmt(row.get('fair_drawdown_cents'))} | "
            f"{fmt(row.get('abs_d_sigma'))} | {fmt(row.get('ask_prob'))} | {fmt(row.get('raw_edge'))} | "
            f"{fmt(row.get('recross_hazard_score'))} | {', '.join(row.get('tags') or [])} |"
        )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    report = build_report()
    write_md(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
