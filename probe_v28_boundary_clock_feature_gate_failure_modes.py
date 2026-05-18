"""Failure-mode classifier for the boundary-clock feature-gate candidate.

Research-only; no live bot changes or orders.

This report classifies selected feature-gate rows into the objective's named
failure-mode families. It is deliberately descriptive, not a threshold search.
"""
from __future__ import annotations

import json
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
FEATURE_JSON = OUT_DIR / "v28_boundary_clock_feature_gate_candidate_latest.json"
RUNWAY_JSON = OUT_DIR / "v28_boundary_clock_feature_gate_runway_latest.json"
OUT_JSON = OUT_DIR / "v28_boundary_clock_feature_gate_failure_modes_latest.json"
OUT_MD = OUT_DIR / "v28_boundary_clock_feature_gate_failure_modes_latest.md"


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


def classify_row(row: dict[str, Any]) -> list[str]:
    tags: list[str] = []
    net = as_float(row.get("net_cents"))
    edge = as_float(row.get("raw_edge"))
    recross = as_float(row.get("recross_hazard_score"))
    abs_d = as_float(row.get("abs_d_sigma"))
    ask = as_float(row.get("ask_prob"))
    side_won = row.get("side_won")
    source = str(row.get("source") or "")
    weak_outcome = side_won is False or (net is not None and net <= 5.0)

    if source and source != "approved_entry":
        tags.append("source_quality_error")
    if side_won is False and edge is not None and edge >= 0.08:
        tags.append("fv_error")
    if side_won is False and ask is not None and ask >= 0.75:
        tags.append("entry_timing_error")
    if weak_outcome and recross is not None and recross >= 0.45:
        tags.append("market_regime_error")
    if weak_outcome and abs_d is not None and abs_d < 1.0:
        tags.append("market_regime_error")
    if weak_outcome and edge is not None and edge <= 0.06:
        tags.append("execution_friction_error")
    if net is not None and net <= 5.0:
        tags.append("execution_friction_error")
    if side_won is False:
        tags.append("fragility_error")
    return sorted(set(tags)) or ["clean_or_unclassified"]


def classify_variant(lane_name: str, variant: dict[str, Any], denominator: int) -> dict[str, Any]:
    summary = variant.get("candidate_summary") if isinstance(variant.get("candidate_summary"), dict) else {}
    rows = [row for row in variant.get("rows") or [] if isinstance(row, dict)]
    tag_counts: Counter[str] = Counter()
    loss_rows: list[dict[str, Any]] = []
    thin_rows: list[dict[str, Any]] = []
    source_rows: list[dict[str, Any]] = []
    for row in rows:
        tags = classify_row(row)
        tag_counts.update(tags)
        enriched = {
            **row,
            "failure_tags": tags,
        }
        if row.get("side_won") is False:
            loss_rows.append(enriched)
        if (as_float(row.get("net_cents")) or 0.0) <= 5.0:
            thin_rows.append(enriched)
        if str(row.get("source") or "") != "approved_entry":
            source_rows.append(enriched)

    net = as_float(summary.get("net_cents")) or 0.0
    settled = int(as_float(summary.get("settled")) or 0)
    coverage = as_float(summary.get("coverage_pct"))
    full_loss_cushion = int(max(0.0, net) // 100.0)
    structural_blockers: list[str] = []
    if settled < 30:
        structural_blockers.append("sample_size_error")
    if coverage is None or coverage < 75.0:
        structural_blockers.append("coverage_error")
    if full_loss_cushion < 3:
        structural_blockers.append("fragility_error")
    if variant.get("reconstructed_share") is not None and float(variant.get("reconstructed_share") or 0.0) > 0.35:
        structural_blockers.append("source_quality_error")

    return {
        "lane": lane_name,
        "candidate": variant.get("candidate"),
        "denominator": denominator,
        "summary": summary,
        "reconstructed_share": variant.get("reconstructed_share"),
        "full_loss_cushion": full_loss_cushion,
        "blockers": variant.get("blockers") or [],
        "structural_failure_modes": sorted(set(structural_blockers)),
        "selected_row_failure_counts": dict(sorted(tag_counts.items())),
        "loss_rows": loss_rows,
        "thin_rows": thin_rows[:20],
        "source_quality_rows": source_rows[:20],
    }


def build_report() -> dict[str, Any]:
    feature = load_json(FEATURE_JSON)
    runway = load_json(RUNWAY_JSON)
    variants: list[dict[str, Any]] = []
    for lane in feature.get("lanes") or []:
        if not isinstance(lane, dict):
            continue
        lane_name = str(lane.get("lane") or "")
        denominator = int(as_float(lane.get("future_denominator")) or 0)
        for variant in lane.get("variants") or []:
            if isinstance(variant, dict):
                variants.append(classify_variant(lane_name, variant, denominator))

    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in variants:
        grouped[str(row.get("lane") or "")].append(row)
    for rows in grouped.values():
        rows.sort(
            key=lambda row: (
                len(row.get("structural_failure_modes") or []),
                len(row.get("blockers") or []),
                -(as_float((row.get("summary") or {}).get("net_cents")) or -999999.0),
            )
        )
    report = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "feature_gate_path": str(FEATURE_JSON),
        "runway_path": str(RUNWAY_JSON),
        "freeze_ts_utc": (feature.get("state") or {}).get("freeze_ts_utc"),
        "runway_best_post_freeze": (runway.get("post_freeze_top") or [{}])[0],
        "lanes": {name: rows for name, rows in sorted(grouped.items())},
    }
    report["interpretation"] = interpretation(report)
    return report


def interpretation(report: dict[str, Any]) -> list[str]:
    notes = [
        "Classifier scope is selected rows only; omitted denominator rows are covered by coverage/sample blockers, not row-level tags.",
    ]
    post = report.get("lanes", {}).get("post_feature_freeze_entry", [])
    if post:
        best = post[0]
        notes.append(
            f"Post-freeze selected rows have structural blockers {best.get('structural_failure_modes')} and selected-row counts {best.get('selected_row_failure_counts')}."
        )
    diag = report.get("lanes", {}).get("diagnostic_entry", [])
    if diag:
        best = diag[0]
        notes.append(
            f"Best diagnostic entry lane has blockers {best.get('blockers')} but row-level failure counts {best.get('selected_row_failure_counts')}."
        )
    notes.append("Promotion still requires the live readiness gate; this report only explains failure modes.")
    return notes


def fmt(value: Any) -> str:
    if value is None:
        return "None"
    if isinstance(value, float):
        return f"{value:.6f}"
    return str(value)


def write_variant_table(lines: list[str], rows: list[dict[str, Any]]) -> None:
    lines.append("| candidate | settled/den | W/L | coverage | net c | recon | cushion | structural modes | row mode counts | blockers |")
    lines.append("|---|---:|---:|---:|---:|---:|---:|---|---|---|")
    for row in rows:
        summary = row.get("summary") or {}
        counts = ", ".join(f"{key}:{value}" for key, value in (row.get("selected_row_failure_counts") or {}).items())
        structural = ", ".join(row.get("structural_failure_modes") or []) or "none"
        blockers = ", ".join(row.get("blockers") or []) or "none"
        lines.append(
            f"| {row.get('candidate')} | {summary.get('settled')}/{row.get('denominator')} | "
            f"{summary.get('wins')}/{summary.get('losses')} | {fmt(summary.get('coverage_pct'))} | "
            f"{fmt(summary.get('net_cents'))} | {fmt(row.get('reconstructed_share'))} | "
            f"{row.get('full_loss_cushion')} | {structural} | {counts} | {blockers} |"
        )


def write_loss_rows(lines: list[str], rows: list[dict[str, Any]]) -> None:
    loss_rows = []
    for variant in rows:
        for row in variant.get("loss_rows") or []:
            loss_rows.append((variant.get("candidate"), row))
    if not loss_rows:
        lines.append("- No selected loss rows in this lane.")
        return
    lines.append("| candidate | market | source | side | net c | edge | recross | abs d | ask | tags |")
    lines.append("|---|---|---|---|---:|---:|---:|---:|---:|---|")
    for candidate, row in loss_rows[:40]:
        lines.append(
            f"| {candidate} | {row.get('market')} | {row.get('source')} | {row.get('side')} | "
            f"{fmt(row.get('net_cents'))} | {fmt(row.get('raw_edge'))} | {fmt(row.get('recross_hazard_score'))} | "
            f"{fmt(row.get('abs_d_sigma'))} | {fmt(row.get('ask_prob'))} | {', '.join(row.get('failure_tags') or [])} |"
        )


def write_md(report: dict[str, Any]) -> None:
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8")
    lines = [
        "# v28 Boundary-Clock Feature-Gate Failure Modes",
        "",
        "Research-only; no live bot changes or orders.",
        "",
        f"- Generated UTC: `{report.get('generated_at_utc')}`",
        f"- Feature-gate freeze UTC: `{report.get('freeze_ts_utc')}`",
        "",
        "## Interpretation",
        "",
    ]
    for note in report.get("interpretation") or []:
        lines.append(f"- {note}")
    for lane, rows in (report.get("lanes") or {}).items():
        lines.extend(["", f"## {lane}", ""])
        write_variant_table(lines, rows)
        lines.extend(["", "### Selected Loss Rows", ""])
        write_loss_rows(lines, rows)
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    report = build_report()
    write_md(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
