"""Strict post-birth failure drilldown for the soft-frontier feature gate.

Research-only; no live bot changes or orders.

This focuses on the current best strict soft-frontier branch so failure
classification stays current without rerunning every broad exploratory watch.
It uses the already-frozen soft-frontier timestamp and the observable
raw03/recross50/abs65/ask35 rule.
"""
from __future__ import annotations

import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from probe_v28_boundary_clock_feature_gate_candidate import as_float, market, net, source
from probe_v28_boundary_clock_feature_gate_soft_frontier_watch import (
    SOFT_RULES,
    load_or_create_state,
    selected_rows,
)
from probe_v28_coverage_repair_pool_diagnostic import raw_edge, summarize
from probe_v28_frozen_boundary_clock_fv_entry_bridge import future_surfaces as bridge_surfaces
from probe_v28_frozen_boundary_clock_repair_entry import future_surfaces as entry_surfaces


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
OUT_JSON = OUT_DIR / "v28_soft_frontier_post_birth_failure_drilldown_latest.json"
OUT_MD = OUT_DIR / "v28_soft_frontier_post_birth_failure_drilldown_latest.md"

RULE_NAME = "soft_raw03_recross50_abs65_ask35"
RULE = SOFT_RULES[RULE_NAME]
MIN_SETTLED = 30
MIN_FULL_LOSS_CUSHION = 3
TARGET_COVERAGE = 75.0
MAX_RECONSTRUCTED_SHARE = 0.35
FULL_LOSS_CENTS = 100.0


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def full_loss_cushion(net_cents: float) -> int:
    return int(max(0.0, net_cents) // FULL_LOSS_CENTS)


def row_value(row: dict[str, Any], key: str) -> float | None:
    return as_float(row.get(key))


def source_counts(rows: list[dict[str, Any]]) -> dict[str, int]:
    return dict(Counter(source(row) for row in rows))


def reconstructed_share(rows: list[dict[str, Any]]) -> float | None:
    counts = source_counts(rows)
    total = sum(counts.values())
    if total <= 0:
        return None
    return (total - int(counts.get("approved_entry") or 0)) / total


def row_tags(row: dict[str, Any]) -> list[str]:
    tags: list[str] = []
    row_net = net(row)
    edge = raw_edge(row)
    ask = row_value(row, "ask_prob")
    abs_d = row_value(row, "abs_d_sigma")
    recross = row_value(row, "recross_hazard_score")
    hold_gross = row_value(row, "hold_gross_cents")
    gross = row_value(row, "gross_cents")
    side_won = row.get("side_won")

    if source(row) != "approved_entry":
        tags.append("source_quality_error")
    if side_won is False:
        tags.append("fv_error")
    if side_won is False and edge is not None and edge >= 0.12:
        tags.append("fv_overconfidence")
    if side_won is False and ask is not None and ask >= 0.65:
        tags.append("entry_timing_error")
    if side_won is False and ask is not None and ask < 0.65:
        tags.append("mid_cheap_tail_failure")
    if recross is not None and recross >= 0.25:
        tags.append("boundary_churn_risk")
    if abs_d is not None and abs_d < 0.85:
        tags.append("near_boundary_risk")
    if row_net <= 5.0:
        tags.append("execution_friction_or_thin_edge")
    if gross is not None and hold_gross is not None:
        if gross > hold_gross:
            tags.append("exit_helped_vs_hold")
        elif gross < hold_gross:
            tags.append("exit_policy_error")
    if row_net < 0:
        tags.append("fragility_error")
    return sorted(set(tags)) or ["clean_or_unclassified"]


def compact_row(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "market": market(row),
        "source": source(row),
        "side": row.get("side"),
        "side_won": row.get("side_won"),
        "status": row.get("status"),
        "result": row.get("result"),
        "ts_wall": row.get("ts_wall"),
        "seconds_to_close": row.get("seconds_to_close"),
        "book_age_ms": row.get("book_age_ms"),
        "net_cents": net(row),
        "gross_cents": row.get("gross_cents"),
        "hold_gross_cents": row.get("hold_gross_cents"),
        "exit_delta_vs_hold_cents": (
            (row_value(row, "gross_cents") or 0.0) - (row_value(row, "hold_gross_cents") or 0.0)
            if row_value(row, "gross_cents") is not None and row_value(row, "hold_gross_cents") is not None
            else None
        ),
        "raw_edge": raw_edge(row),
        "recross_hazard_score": row.get("recross_hazard_score"),
        "abs_d_sigma": row.get("abs_d_sigma"),
        "ask_prob": row.get("ask_prob"),
        "p_side": row.get("p_side"),
        "top_eigenvalue": row.get("top_eigenvalue"),
        "top_over_mp_edge": row.get("top_over_mp_edge"),
        "failure_tags": row_tags(row),
    }


def blockers(summary: dict[str, Any], share: float | None) -> list[str]:
    out: list[str] = []
    settled = int(as_float(summary.get("settled")) or 0)
    coverage = as_float(summary.get("coverage_pct"))
    net_cents = as_float(summary.get("net_cents")) or 0.0
    if settled < MIN_SETTLED:
        out.append("settled_lt_30")
    if coverage is None or coverage < TARGET_COVERAGE:
        out.append("coverage_too_low")
    if net_cents <= 0:
        out.append("net_not_positive")
    if share is not None and share > MAX_RECONSTRUCTED_SHARE:
        out.append("reconstructed_share_gt_35pct")
    if full_loss_cushion(net_cents) < MIN_FULL_LOSS_CUSHION:
        out.append("full_loss_cushion_lt_3")
    return out


def evaluate_lane(label: str, surfaces_fn: Any, freeze_ts: str) -> dict[str, Any]:
    rows, _, denominator = surfaces_fn(freeze_ts)
    selected = selected_rows(rows, RULE)
    selected_sorted = sorted(selected, key=lambda row: net(row))
    settled = [row for row in selected_sorted if row.get("side_won") is not None]
    losses = [row for row in settled if net(row) < 0]
    thin = [row for row in settled if 0 <= net(row) <= 5]
    pending = [row for row in selected_sorted if row.get("side_won") is None]
    summary = summarize(selected, int(denominator or 0))
    share = reconstructed_share(selected)
    tag_counts = Counter(tag for row in selected_sorted for tag in row_tags(row))
    loss_tag_counts = Counter(tag for row in losses for tag in row_tags(row))
    exit_delta_total = sum(
        float((row_value(row, "gross_cents") or 0.0) - (row_value(row, "hold_gross_cents") or 0.0))
        for row in losses
        if row_value(row, "gross_cents") is not None and row_value(row, "hold_gross_cents") is not None
    )
    return {
        "lane": label,
        "freeze_ts_utc": freeze_ts,
        "rule": RULE_NAME,
        "future_denominator": int(denominator or 0),
        "summary": summary,
        "source_counts": source_counts(selected),
        "reconstructed_share": share,
        "full_loss_cushion": full_loss_cushion(float(summary.get("net_cents") or 0.0)),
        "blockers": blockers(summary, share),
        "selected_tag_counts": dict(sorted(tag_counts.items())),
        "loss_tag_counts": dict(sorted(loss_tag_counts.items())),
        "loss_exit_delta_vs_hold_cents": exit_delta_total,
        "loss_rows": [compact_row(row) for row in losses],
        "thin_rows": [compact_row(row) for row in thin],
        "pending_rows": [compact_row(row) for row in pending],
        "selected_rows": [compact_row(row) for row in selected_sorted],
    }


def build_report() -> dict[str, Any]:
    state = load_or_create_state()
    freeze_ts = str(state["freeze_ts_utc"])
    lanes = [
        evaluate_lane("post_soft_frontier_birth_entry", entry_surfaces, freeze_ts),
        evaluate_lane("post_soft_frontier_birth_bridge", bridge_surfaces, freeze_ts),
    ]
    report = {
        "generated_at_utc": utc_now_iso(),
        "soft_frontier_freeze_ts_utc": freeze_ts,
        "rule": RULE_NAME,
        "rule_params": RULE,
        "lanes": lanes,
    }
    report["interpretation"] = interpretation(report)
    return report


def interpretation(report: dict[str, Any]) -> list[str]:
    notes = [
        "This is a strict post-birth failure drilldown; it is not a new candidate and does not change live logic.",
        "The rule is observable-only. Source labels are used only for evidence-quality audit.",
    ]
    for lane in report.get("lanes") or []:
        summary = lane.get("summary") or {}
        notes.append(
            f"{lane.get('lane')} has {summary.get('entries')}/{lane.get('future_denominator')} entries, "
            f"{summary.get('settled')} settled, coverage {summary.get('coverage_pct')}%, net "
            f"{summary.get('net_cents')}c, reconstructed share {lane.get('reconstructed_share')}, "
            f"cushion {lane.get('full_loss_cushion')}, blockers {lane.get('blockers')}."
        )
        notes.append(
            f"{lane.get('lane')} loss tags are {lane.get('loss_tag_counts')} and current exits changed loss rows by "
            f"{lane.get('loss_exit_delta_vs_hold_cents')}c versus holding to settlement."
        )
    notes.append("Physical read: if loss rows are mostly exit_helped_vs_hold, the next repair is FV/entry timing, not looser exits.")
    return notes


def fmt(value: Any) -> str:
    if value is None:
        return "None"
    if isinstance(value, float):
        return f"{value:.6f}"
    return str(value)


def write_md(report: dict[str, Any]) -> None:
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8")
    lines = [
        "# v28 Soft-Frontier Post-Birth Failure Drilldown",
        "",
        "Research-only; no live bot changes or orders.",
        "",
        f"- Generated UTC: `{report.get('generated_at_utc')}`",
        f"- Soft-frontier freeze UTC: `{report.get('soft_frontier_freeze_ts_utc')}`",
        f"- Rule: `{report.get('rule')}` / `{report.get('rule_params')}`",
        "",
        "## Interpretation",
        "",
    ]
    lines.extend(f"- {note}" for note in report.get("interpretation") or [])
    for lane in report.get("lanes") or []:
        summary = lane.get("summary") or {}
        lines.extend([
            "",
            f"## {lane.get('lane')}",
            "",
            f"- Summary: `{summary}`",
            f"- Source counts: `{lane.get('source_counts')}`",
            f"- Reconstructed share: `{fmt(lane.get('reconstructed_share'))}`",
            f"- Full-loss cushion: `{lane.get('full_loss_cushion')}`",
            f"- Blockers: `{', '.join(lane.get('blockers') or []) or 'none'}`",
            f"- Selected tag counts: `{lane.get('selected_tag_counts')}`",
            f"- Loss tag counts: `{lane.get('loss_tag_counts')}`",
            f"- Loss exit delta vs hold: `{fmt(lane.get('loss_exit_delta_vs_hold_cents'))}c`",
            "",
            "### Loss Rows",
            "",
            "| market | source | side | result | net c | gross c | hold gross c | exit delta vs hold | edge | recross | abs d | ask | tags |",
            "|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---|",
        ])
        for row in lane.get("loss_rows") or []:
            lines.append(
                f"| {row.get('market')} | {row.get('source')} | {row.get('side')} | {row.get('result')} | "
                f"{fmt(row.get('net_cents'))} | {fmt(row.get('gross_cents'))} | {fmt(row.get('hold_gross_cents'))} | "
                f"{fmt(row.get('exit_delta_vs_hold_cents'))} | {fmt(row.get('raw_edge'))} | "
                f"{fmt(row.get('recross_hazard_score'))} | {fmt(row.get('abs_d_sigma'))} | "
                f"{fmt(row.get('ask_prob'))} | {', '.join(row.get('failure_tags') or [])} |"
            )
        lines.extend([
            "",
            "### Pending Rows",
            "",
            "| market | source | side | net c | edge | recross | abs d | ask | tags |",
            "|---|---|---|---:|---:|---:|---:|---:|---|",
        ])
        for row in lane.get("pending_rows") or []:
            lines.append(
                f"| {row.get('market')} | {row.get('source')} | {row.get('side')} | "
                f"{fmt(row.get('net_cents'))} | {fmt(row.get('raw_edge'))} | {fmt(row.get('recross_hazard_score'))} | "
                f"{fmt(row.get('abs_d_sigma'))} | {fmt(row.get('ask_prob'))} | {', '.join(row.get('failure_tags') or [])} |"
            )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    report = build_report()
    write_md(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
