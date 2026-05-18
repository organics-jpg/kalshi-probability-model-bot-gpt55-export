"""Drift audit for the boundary-clock clean-broad frontier.

Research-only. This compares the parent feature-gate frontier window against
the separately frozen clean-broad watch so the older +PnL frontier is not
mistaken for deployable fresh evidence.
"""
from __future__ import annotations

import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
CLEAN_WATCH_JSON = OUT_DIR / "v28_boundary_clock_feature_gate_clean_broad_frontier_watch_latest.json"
OUTLIER_STRESS_JSON = OUT_DIR / "v28_boundary_clock_feature_gate_outlier_stress_latest.json"
OUT_JSON = OUT_DIR / "v28_feature_gate_frontier_drift_audit_latest.json"
OUT_MD = OUT_DIR / "v28_feature_gate_frontier_drift_audit_latest.md"

RULE = "raw03_recross50_abs50_ask35"


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


def lane_by_name(payload: dict[str, Any], name: str) -> dict[str, Any]:
    return next(
        (
            lane for lane in payload.get("lanes") or []
            if isinstance(lane, dict) and lane.get("lane") == name
        ),
        {},
    )


def source_share(source_counts: dict[str, Any]) -> float | None:
    total = sum(int(value or 0) for value in source_counts.values())
    if total <= 0:
        return None
    approved = int(source_counts.get("approved_entry") or 0)
    return (total - approved) / total


def compact_parent(lane: dict[str, Any]) -> dict[str, Any]:
    return {
        "lane": lane.get("lane"),
        "rule": lane.get("frontier_rule"),
        "entries": lane.get("entries"),
        "future_denominator": lane.get("future_denominator"),
        "settled": lane.get("settled"),
        "wins": lane.get("wins"),
        "losses": lane.get("losses"),
        "coverage_pct": lane.get("coverage_pct"),
        "net_cents": lane.get("net_cents"),
        "reconstructed_share": lane.get("reconstructed_share"),
        "source_counts": lane.get("source_counts") or {},
        "approved_only_net_cents": lane.get("approved_only_net_cents"),
        "reconstructed_only_net_cents": lane.get("reconstructed_only_net_cents"),
        "top_win_net_cents": lane.get("top_win_net_cents"),
        "net_without_top_win_cents": lane.get("net_without_top_win_cents"),
        "net_after_one_full_loss_cents": lane.get("net_after_one_full_loss_cents"),
        "stress_blockers": lane.get("stress_blockers") or [],
        "mechanism_tag_counts": lane.get("mechanism_tag_counts") or {},
        "worst_loss_row": lane.get("worst_loss_row") or {},
    }


def compact_strict(lane: dict[str, Any]) -> dict[str, Any]:
    summary = lane.get("candidate_summary") or {}
    rows = lane.get("rows") or []
    source_counts = lane.get("source_counts") or {}
    nets = [as_float(row.get("net_cents")) or 0.0 for row in rows]
    source_net: Counter[str] = Counter()
    for row in rows:
        source_net[str(row.get("source") or "unknown")] += as_float(row.get("net_cents")) or 0.0
    return {
        "lane": lane.get("lane"),
        "candidate": lane.get("candidate"),
        "entries": summary.get("entries"),
        "future_denominator": lane.get("future_denominator"),
        "settled": summary.get("settled"),
        "wins": summary.get("wins"),
        "losses": summary.get("losses"),
        "coverage_pct": summary.get("coverage_pct"),
        "net_cents": summary.get("net_cents"),
        "reconstructed_share": lane.get("reconstructed_share"),
        "source_counts": source_counts,
        "source_net_cents": dict(source_net),
        "avg_net_cents": (sum(nets) / len(nets)) if nets else None,
        "blockers": lane.get("blockers") or [],
        "rows": rows,
    }


def delta(parent: dict[str, Any], strict: dict[str, Any]) -> dict[str, Any]:
    parent_net = as_float(parent.get("net_cents"))
    strict_net = as_float(strict.get("net_cents"))
    parent_share = as_float(parent.get("reconstructed_share"))
    strict_share = as_float(strict.get("reconstructed_share"))
    parent_cov = as_float(parent.get("coverage_pct"))
    strict_cov = as_float(strict.get("coverage_pct"))
    blockers: list[str] = []
    if strict.get("settled") is None or int(strict.get("settled") or 0) < 30:
        blockers.append("strict_settled_lt_30")
    if strict_net is None or strict_net <= 0:
        blockers.append("strict_net_not_positive")
    if strict_share is not None and strict_share > 0.35:
        blockers.append("strict_reconstructed_share_gt_35pct")
    if strict_cov is None or strict_cov < 75.0:
        blockers.append("strict_coverage_below_75pct")
    if int(max(0.0, strict_net or 0.0) // 100.0) < 3:
        blockers.append("strict_full_loss_cushion_lt_3")
    return {
        "net_delta_cents": (strict_net - parent_net) if parent_net is not None and strict_net is not None else None,
        "coverage_delta_pct": (strict_cov - parent_cov) if parent_cov is not None and strict_cov is not None else None,
        "reconstructed_share_delta": (
            strict_share - parent_share
            if parent_share is not None and strict_share is not None
            else None
        ),
        "blockers": blockers,
    }


def build_report() -> dict[str, Any]:
    clean = load_json(CLEAN_WATCH_JSON)
    stress = load_json(OUTLIER_STRESS_JSON)
    pairs = [
        (
            "entry",
            compact_parent(lane_by_name(stress, "post_feature_freeze_entry")),
            compact_strict(lane_by_name(clean, "post_clean_broad_freeze_entry")),
        ),
        (
            "bridge",
            compact_parent(lane_by_name(stress, "post_feature_freeze_bridge")),
            compact_strict(lane_by_name(clean, "post_clean_broad_freeze_bridge")),
        ),
    ]
    lanes = []
    for label, parent, strict in pairs:
        lanes.append({
            "label": label,
            "parent_frontier": parent,
            "strict_watch": strict,
            "delta": delta(parent, strict),
        })
    report = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "rule": RULE,
        "parent_source": str(OUTLIER_STRESS_JSON),
        "strict_watch_source": str(CLEAN_WATCH_JSON),
        "lanes": lanes,
    }
    report["interpretation"] = interpretation(report)
    return report


def interpretation(report: dict[str, Any]) -> list[str]:
    notes = [
        "The parent frontier remains useful as mechanism evidence only.",
        "The clean-broad rule is not promotable unless the strict watch clears its own gates.",
    ]
    for lane in report.get("lanes") or []:
        parent = lane.get("parent_frontier") or {}
        strict = lane.get("strict_watch") or {}
        d = lane.get("delta") or {}
        notes.append(
            f"{lane.get('label')}: parent {parent.get('settled')} settled/"
            f"{parent.get('net_cents')}c/recon {parent.get('reconstructed_share')} versus "
            f"strict {strict.get('settled')} settled/{strict.get('net_cents')}c/recon "
            f"{strict.get('reconstructed_share')}; blockers {d.get('blockers')}."
        )
    return notes


def fmt(value: Any) -> str:
    if value is None:
        return "n/a"
    if isinstance(value, float):
        return f"{value:.6f}"
    return str(value)


def write_md(report: dict[str, Any]) -> None:
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    lines = [
        "# v28 Feature-Gate Frontier Drift Audit",
        "",
        "Research-only. Compares the original feature-gate frontier audit to the strict clean-broad watch.",
        "",
        f"- Generated UTC: `{report.get('generated_at_utc')}`",
        f"- Rule: `{report.get('rule')}`",
        "",
        "## Interpretation",
        "",
    ]
    lines.extend(f"- {note}" for note in report.get("interpretation") or [])
    lines.extend([
        "",
        "## Parent Vs Strict",
        "",
        "| lane | parent settled | parent W/L | parent cov | parent net | parent recon | strict settled | strict W/L | strict cov | strict net | strict recon | net delta | recon delta | blockers |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|",
    ])
    for lane in report.get("lanes") or []:
        parent = lane.get("parent_frontier") or {}
        strict = lane.get("strict_watch") or {}
        d = lane.get("delta") or {}
        lines.append(
            f"| {lane.get('label')} | {parent.get('settled')} | {parent.get('wins')}/{parent.get('losses')} | "
            f"{fmt(parent.get('coverage_pct'))} | {fmt(parent.get('net_cents'))} | "
            f"{fmt(parent.get('reconstructed_share'))} | {strict.get('settled')} | "
            f"{strict.get('wins')}/{strict.get('losses')} | {fmt(strict.get('coverage_pct'))} | "
            f"{fmt(strict.get('net_cents'))} | {fmt(strict.get('reconstructed_share'))} | "
            f"{fmt(d.get('net_delta_cents'))} | {fmt(d.get('reconstructed_share_delta'))} | "
            f"{', '.join(d.get('blockers') or []) or 'none'} |"
        )
    lines.extend([
        "",
        "## Strict Rows",
        "",
        "| lane | market | source | side | won | net c | raw edge | ask | abs d | recross |",
        "|---|---|---|---|---|---:|---:|---:|---:|---:|",
    ])
    for lane in report.get("lanes") or []:
        strict = lane.get("strict_watch") or {}
        for row in strict.get("rows") or []:
            lines.append(
                f"| {lane.get('label')} | {row.get('market')} | {row.get('source')} | "
                f"{row.get('side')} | {row.get('side_won')} | {fmt(row.get('net_cents'))} | "
                f"{fmt(row.get('raw_edge'))} | {fmt(row.get('ask_prob'))} | "
                f"{fmt(row.get('abs_d_sigma'))} | {fmt(row.get('recross_hazard_score'))} |"
            )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    report = build_report()
    write_md(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
