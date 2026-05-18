"""Source/fragility audit for the nearest strict target-coverage v28 candidates.

Research-only; no live bot changes or orders.

The strict-forward leaderboard can show a candidate as positive and broad while
still marking source quality unknown. This probe reconstructs the actual row
sets for the current nearest target-coverage candidates and scores source mix,
full-loss cushion, pending rows, and loss mechanisms.
"""
from __future__ import annotations

import json
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from probe_v28_frozen_forward_candidates import market_timing, parse_ts
from probe_v28_frozen_raw_p52_boundary_turbulence_skip import (
    BASE_POLICY as RAW_P52_BASE_POLICY,
    load_json as load_json_raw_p52,
    should_skip as should_raw_p52_skip,
    summarize as summarize_raw_p52,
)
from probe_v28_frozen_early_no_boundary_decay_repair_entry import (
    build_candidate as build_early_candidate,
    compact as compact_early_row,
    future_surfaces as early_future_surfaces,
    load_json as load_json_early,
    summarize as summarize_early,
)
from probe_v28_raw_physics_penalty_candidates import build_report as build_raw_physics_report


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
OUT_JSON = OUT_DIR / "v28_top_strict_target_source_fragility_latest.json"
OUT_MD = OUT_DIR / "v28_top_strict_target_source_fragility_latest.md"

RAW_P52_STATE_JSON = OUT_DIR / "v28_frozen_raw_p52_boundary_turbulence_skip_state.json"
EARLY_STATE_JSON = OUT_DIR / "v28_frozen_early_no_boundary_decay_repair_entry_state.json"
SCORECARD_JSON = OUT_DIR / "v28_continuous_scorecard_latest.json"

MIN_SETTLED = 30
COVERAGE_FLOOR = 75.0
MAX_RECONSTRUCTED_SHARE = 0.35
MIN_FULL_LOSS_CUSHION = 3


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


def net_cents(row: dict[str, Any]) -> float:
    for key in ("net_gross_cents_after_entry_fee", "net_cents"):
        value = row.get(key)
        if value is not None:
            try:
                return float(value)
            except (TypeError, ValueError):
                return 0.0
    return 0.0


def source_label(row: dict[str, Any]) -> str:
    return str(row.get("source") or "unknown")


def is_approved_source(label: str) -> bool:
    return label == "approved_entry"


def row_won(row: dict[str, Any]) -> bool | None:
    value = row.get("side_won")
    if value is True or value is False:
        return value
    return None


def as_summary_value(summary: dict[str, Any], key: str) -> Any:
    if key in summary:
        return summary.get(key)
    if key == "net_cents":
        return summary.get("net_cents_after_entry_fee")
    return None


def source_stats(rows: list[dict[str, Any]]) -> dict[str, Any]:
    entries_by_source = Counter(source_label(row) for row in rows)
    settled_rows = [row for row in rows if row_won(row) is not None]
    settled_by_source = Counter(source_label(row) for row in settled_rows)
    source_rows: dict[str, dict[str, Any]] = {}
    for label in sorted(entries_by_source):
        selected = [row for row in settled_rows if source_label(row) == label]
        source_rows[label] = {
            "entries": entries_by_source[label],
            "settled": settled_by_source[label],
            "wins": sum(1 for row in selected if row_won(row) is True),
            "losses": sum(1 for row in selected if row_won(row) is False),
            "net_cents": sum(net_cents(row) for row in selected),
        }
    total = len(rows)
    approved = sum(count for label, count in entries_by_source.items() if is_approved_source(label))
    reconstructed_share = None if total <= 0 else (total - approved) / total
    return {
        "entry_source_counts": dict(entries_by_source),
        "settled_source_counts": dict(settled_by_source),
        "reconstructed_share": reconstructed_share,
        "by_source": source_rows,
    }


def fragility_tags(row: dict[str, Any]) -> list[str]:
    tags = []
    try:
        recross = float(row.get("recross_hazard_score")) if row.get("recross_hazard_score") is not None else None
    except (TypeError, ValueError):
        recross = None
    try:
        abs_d = float(row.get("abs_d_sigma")) if row.get("abs_d_sigma") is not None else None
    except (TypeError, ValueError):
        abs_d = None
    try:
        ask = float(row.get("ask_prob")) if row.get("ask_prob") is not None else None
    except (TypeError, ValueError):
        ask = None
    try:
        edge = float(row.get("raw_edge_prob")) if row.get("raw_edge_prob") is not None else None
    except (TypeError, ValueError):
        edge = None
    if recross is not None and recross >= 0.75:
        tags.append("high_recross")
    if recross is not None and recross >= 0.90:
        tags.append("extreme_recross")
    if abs_d is not None and abs_d <= 0.25:
        tags.append("near_strike")
    if abs_d is not None and abs_d <= 0.50:
        tags.append("weak_boundary_distance")
    if ask is not None and ask < 0.55:
        tags.append("cheap_touch")
    if edge is not None and edge < 0.03:
        tags.append("thin_edge_lt_3pp")
    if edge is not None and edge < 0.01:
        tags.append("razor_edge_lt_1pp")
    label = source_label(row)
    if not is_approved_source(label):
        tags.append("source_not_approved")
    return tags or ["unclassified"]


def loss_mechanisms(rows: list[dict[str, Any]]) -> dict[str, Any]:
    counter: Counter[str] = Counter()
    examples = []
    losses = [row for row in rows if row_won(row) is False]
    for row in losses:
        tags = fragility_tags(row)
        counter.update(tags)
        if len(examples) < 12:
            examples.append({
                "market": row.get("market"),
                "side": row.get("side"),
                "source": source_label(row),
                "net_cents": net_cents(row),
                "p": row.get("p_side") if row.get("p_side") is not None else row.get("p_raw"),
                "ask_prob": row.get("ask_prob"),
                "raw_edge_prob": row.get("raw_edge_prob"),
                "abs_d_sigma": row.get("abs_d_sigma"),
                "recross_hazard_score": row.get("recross_hazard_score"),
                "tags": tags,
            })
    return {
        "loss_count": len(losses),
        "tag_counts": dict(counter),
        "examples": examples,
    }


def blockers(summary: dict[str, Any], stats: dict[str, Any], risk_stop: bool) -> list[str]:
    out = []
    settled = int(as_summary_value(summary, "settled") or 0)
    coverage = as_summary_value(summary, "coverage_pct")
    net = float(as_summary_value(summary, "net_cents") or 0.0)
    recon = stats.get("reconstructed_share")
    cushion = int(net // 100.0) if net > 0.0 else 0
    if settled < MIN_SETTLED:
        out.append("settled_lt_30")
    if coverage is None or float(coverage) < COVERAGE_FLOOR:
        out.append("coverage_too_low")
    if net <= 0.0:
        out.append("net_not_positive")
    if recon is None:
        out.append("source_share_unknown")
    elif float(recon) > MAX_RECONSTRUCTED_SHARE:
        out.append("reconstructed_share_gt_35pct")
    if cushion < MIN_FULL_LOSS_CUSHION:
        out.append("full_loss_cushion_lt_3")
    if risk_stop:
        out.append("control_risk_stop_active")
    return out


def compact_row(row: dict[str, Any], reason: str) -> dict[str, Any]:
    return {
        "market": row.get("market"),
        "side": row.get("side"),
        "source": source_label(row),
        "side_won": row_won(row),
        "net_cents": net_cents(row) if row_won(row) is not None else None,
        "p": row.get("p_side") if row.get("p_side") is not None else row.get("p_raw"),
        "ask_prob": row.get("ask_prob"),
        "raw_edge_prob": row.get("raw_edge_prob"),
        "abs_d_sigma": row.get("abs_d_sigma"),
        "recross_hazard_score": row.get("recross_hazard_score"),
        "reason": reason,
    }


def build_raw_p52_candidate() -> dict[str, Any]:
    state = load_json_raw_p52(RAW_P52_STATE_JSON)
    timing = market_timing(parse_ts(state.get("freeze_ts_utc")))
    forward_markets = set(timing["clean_forward_markets"])
    raw_report = build_raw_physics_report()
    all_rows = raw_report.get("rows") if isinstance(raw_report.get("rows"), list) else []
    base = [
        row for row in all_rows
        if row.get("policy") == RAW_P52_BASE_POLICY and str(row.get("market") or "") in forward_markets
    ]
    candidate = [row for row in base if not should_raw_p52_skip(row, state)]
    skipped = [row for row in base if should_raw_p52_skip(row, state)]
    summary = summarize_raw_p52(candidate, len(forward_markets))
    stats = source_stats(candidate)
    return {
        "gate": "raw_p52_boundary_turbulence_skip",
        "policy": "raw_p52_skip_weakraw_nearstrike_recross90",
        "freeze_ts_utc": state.get("freeze_ts_utc"),
        "summary": summary,
        "source_stats": stats,
        "full_loss_cushion_estimate": int(float(summary.get("net_cents") or 0.0) // 100.0) if float(summary.get("net_cents") or 0.0) > 0.0 else 0,
        "loss_mechanisms": loss_mechanisms(candidate),
        "pending_rows": [compact_row(row, "pending_candidate") for row in candidate if row_won(row) is None],
        "skipped_rows": [compact_row(row, "skipped_boundary_turbulence") for row in skipped],
    }


def build_early_candidate_row() -> dict[str, Any]:
    state = load_json_early(EARLY_STATE_JSON)
    all_rows, target, denominator = early_future_surfaces(str(state.get("freeze_ts_utc")))
    built = build_early_candidate(all_rows, target, denominator)
    candidate = built.get("candidate") or []
    summary = summarize_early(candidate, denominator)
    stats = source_stats(candidate)
    return {
        "gate": "early_no_boundary_decay_repair_entry",
        "policy": "skip_early_no_boundary_decay_repair_calm_geometry",
        "freeze_ts_utc": state.get("freeze_ts_utc"),
        "summary": summary,
        "source_stats": stats,
        "full_loss_cushion_estimate": int(float(summary.get("net_cents") or 0.0) // 100.0) if float(summary.get("net_cents") or 0.0) > 0.0 else 0,
        "loss_mechanisms": loss_mechanisms(candidate),
        "pending_rows": [compact_early_row(row) for row in candidate if row_won(row) is None],
        "danger_rows": [compact_early_row(row) for row in built.get("danger") or []],
        "repair_rows": [compact_early_row(row) for row in built.get("repairs") or []],
        "needed_repairs": built.get("needed_repairs"),
        "missed_repairs_available": built.get("missed_repairs_available"),
    }


def build_report() -> dict[str, Any]:
    scorecard = load_json(SCORECARD_JSON).get("summary") or {}
    risk_stop = scorecard.get("risk_stop") is True
    candidates = [build_raw_p52_candidate(), build_early_candidate_row()]
    for row in candidates:
        row["blockers"] = blockers(row.get("summary") or {}, row.get("source_stats") or {}, risk_stop)
        row["live_ready"] = not row["blockers"]
    candidates.sort(
        key=lambda row: (
            len(row.get("blockers") or []),
            -float((row.get("summary") or {}).get("net_cents") or 0.0),
        )
    )
    return {
        "generated_at_utc": utc_now_iso(),
        "risk_stop_active": risk_stop,
        "candidates": candidates,
        "interpretation": [
            "These rows are strict-forward and target-coverage candidates, but promotion still needs source-quality, cushion, and risk-stop gates.",
            "A source share computed here replaces the earlier source_unknown label for these two reconstructed row sets.",
        ],
    }


def fmt(value: Any) -> str:
    if value is None:
        return "n/a"
    if isinstance(value, float):
        return f"{value:.6f}"
    return str(value)


def money(cents: Any) -> str:
    try:
        value = float(cents)
    except (TypeError, ValueError):
        return "n/a"
    return f"{value:.0f}c (${value / 100.0:.2f})"


def write_outputs(report: dict[str, Any]) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8")
    lines = [
        "# v28 Top Strict Target Source/Fragility Audit",
        "",
        "Research-only. No live bot changes or orders.",
        "",
        f"- Generated UTC: `{report.get('generated_at_utc')}`",
        f"- Risk stop active: `{report.get('risk_stop_active')}`",
        "",
        "## Interpretation",
        "",
    ]
    for note in report.get("interpretation") or []:
        lines.append(f"- {note}")
    lines.extend([
        "",
        "## Candidate Gate Table",
        "",
        "| gate | policy | settled | W/L | coverage | net | recon share | cushion | live ready | blockers |",
        "|---|---|---:|---:|---:|---:|---:|---:|---|---|",
    ])
    for row in report.get("candidates") or []:
        summary = row.get("summary") or {}
        stats = row.get("source_stats") or {}
        lines.append(
            f"| {row.get('gate')} | `{row.get('policy')}` | {summary.get('settled')} | "
            f"{summary.get('wins')}/{summary.get('losses')} | {fmt(summary.get('coverage_pct'))}% | "
            f"{money(summary.get('net_cents'))} | {fmt(stats.get('reconstructed_share'))} | "
            f"{row.get('full_loss_cushion_estimate')} | {row.get('live_ready')} | "
            f"{', '.join(row.get('blockers') or []) or 'none'} |"
        )
    for row in report.get("candidates") or []:
        lines.extend([
            "",
            f"## {row.get('gate')} / {row.get('policy')}",
            "",
            f"- Freeze UTC: `{row.get('freeze_ts_utc')}`",
            f"- Entry source counts: `{(row.get('source_stats') or {}).get('entry_source_counts')}`",
            f"- Settled source counts: `{(row.get('source_stats') or {}).get('settled_source_counts')}`",
            "",
            "### Source PnL",
            "",
            "| source | entries | settled | W/L | net |",
            "|---|---:|---:|---:|---:|",
        ])
        for label, source_row in ((row.get("source_stats") or {}).get("by_source") or {}).items():
            lines.append(
                f"| {label} | {source_row.get('entries')} | {source_row.get('settled')} | "
                f"{source_row.get('wins')}/{source_row.get('losses')} | {money(source_row.get('net_cents'))} |"
            )
        mech = row.get("loss_mechanisms") or {}
        lines.extend([
            "",
            "### Loss Mechanisms",
            "",
            f"- Loss tag counts: `{mech.get('tag_counts')}`",
            "",
            "| market | side | source | net | p | ask | edge | abs d | recross | tags |",
            "|---|---|---|---:|---:|---:|---:|---:|---:|---|",
        ])
        for loss in mech.get("examples") or []:
            lines.append(
                f"| {loss.get('market')} | {loss.get('side')} | {loss.get('source')} | "
                f"{money(loss.get('net_cents'))} | {fmt(loss.get('p'))} | {fmt(loss.get('ask_prob'))} | "
                f"{fmt(loss.get('raw_edge_prob'))} | {fmt(loss.get('abs_d_sigma'))} | "
                f"{fmt(loss.get('recross_hazard_score'))} | {', '.join(loss.get('tags') or [])} |"
            )
        pending = row.get("pending_rows") or []
        lines.extend([
            "",
            "### Pending Rows",
            "",
            f"- Pending selected rows: `{len(pending)}`",
        ])
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    report = build_report()
    write_outputs(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
