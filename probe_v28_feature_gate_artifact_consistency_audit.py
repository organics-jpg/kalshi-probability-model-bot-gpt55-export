"""Consistency audit for v28 feature-gate research artifacts.

Research-only; no live bot changes or orders.

This probe does not score a candidate. It checks whether the feature-gate
reports used for promotion discussion are describing the same row, denominator,
live baseline, and size-shrink policy. It is meant to catch stale dependency
chains before a candidate-vs-live claim is made.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"

FEATURE_JSON = OUT_DIR / "v28_boundary_clock_feature_gate_candidate_latest.json"
SOURCE_DENOM_JSON = OUT_DIR / "v28_boundary_clock_feature_gate_source_denominator_audit_latest.json"
LINKED_SOURCE_JSON = OUT_DIR / "v28_feature_gate_linked_source_runway_latest.json"
PROMOTION_GAP_JSON = OUT_DIR / "v28_feature_gate_promotion_gap_audit_latest.json"
SIZE_SHRINK_SOURCE_JSON = OUT_DIR / "v28_feature_gate_size_shrink_source_runway_latest.json"
COVERAGE_SIZE_RUNWAY_JSON = OUT_DIR / "v28_feature_gate_coverage_size_shrink_runway_latest.json"
CANDIDATE_VS_LIVE_JSON = OUT_DIR / "v28_candidate_vs_live_full_table_latest.json"
LIVE_SUMMARY_JSON = ROOT / "stats" / "live_mushroom_v28_size2" / "summary.json"

OUT_JSON = OUT_DIR / "v28_feature_gate_artifact_consistency_audit_latest.json"
OUT_MD = OUT_DIR / "v28_feature_gate_artifact_consistency_audit_latest.md"

BROAD_CANDIDATE = "post_feature_freeze_entry_raw03_recross70_abs075"
ENTRY_LANE = "post_feature_freeze_entry"
SIZE_POLICY = "repair_low_absd_quarter_else_half"

FLOAT_TOL = 1e-6


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


def fnum(value: Any) -> float | None:
    if value is None or value == "":
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def cents_from_live_summary(payload: dict[str, Any]) -> float | None:
    dollars = fnum(payload.get("net_pnl_total_dollars"))
    return None if dollars is None else round(dollars * 100.0, 6)


def feature_broad(payload: dict[str, Any]) -> dict[str, Any]:
    for lane in payload.get("lanes") or []:
        if not isinstance(lane, dict) or lane.get("lane") != ENTRY_LANE:
            continue
        for variant in lane.get("variants") or []:
            if isinstance(variant, dict) and variant.get("candidate") == BROAD_CANDIDATE:
                summary = variant.get("candidate_summary") or {}
                return {
                    "source": FEATURE_JSON.name,
                    "generated_at_utc": payload.get("generated_at_utc"),
                    "candidate": BROAD_CANDIDATE,
                    "future_denominator": lane.get("future_denominator"),
                    "entries": summary.get("entries"),
                    "settled": summary.get("settled"),
                    "coverage_pct": summary.get("coverage_pct"),
                    "net_cents": summary.get("net_cents"),
                    "wins": summary.get("wins"),
                    "losses": summary.get("losses"),
                    "reconstructed_share": variant.get("reconstructed_share"),
                    "blockers": variant.get("blockers") or [],
                }
    return {"source": FEATURE_JSON.name, "missing": True}


def source_denom_broad(payload: dict[str, Any]) -> dict[str, Any]:
    for lane in payload.get("lanes") or []:
        if not isinstance(lane, dict) or lane.get("lane") != ENTRY_LANE:
            continue
        for rule in lane.get("rules") or []:
            if isinstance(rule, dict) and rule.get("rule") == "raw03_recross70_abs075":
                summary = rule.get("summary") or {}
                return {
                    "source": SOURCE_DENOM_JSON.name,
                    "generated_at_utc": payload.get("generated_at_utc"),
                    "candidate": BROAD_CANDIDATE,
                    "future_denominator": rule.get("future_denominator"),
                    "entries": summary.get("entries"),
                    "settled": summary.get("settled"),
                    "coverage_pct": summary.get("coverage_pct"),
                    "net_cents": summary.get("net_cents"),
                    "wins": summary.get("wins"),
                    "losses": summary.get("losses"),
                    "reconstructed_share": rule.get("selected_reconstructed_share"),
                }
    return {"source": SOURCE_DENOM_JSON.name, "missing": True}


def linked_broad(payload: dict[str, Any]) -> dict[str, Any]:
    for row in payload.get("rows") or []:
        if not isinstance(row, dict):
            continue
        if row.get("lane") == ENTRY_LANE and row.get("candidate") == BROAD_CANDIDATE:
            summary = row.get("linked_summary") or {}
            return {
                "source": LINKED_SOURCE_JSON.name,
                "generated_at_utc": payload.get("generated_at_utc"),
                "candidate": BROAD_CANDIDATE,
                "future_denominator": row.get("future_denominator"),
                "entries": summary.get("entries"),
                "settled": summary.get("settled"),
                "coverage_pct": summary.get("coverage_pct"),
                "net_cents": summary.get("net_cents"),
                "wins": summary.get("wins"),
                "losses": summary.get("losses"),
                "reconstructed_share": summary.get("reconstructed_share"),
                "blockers": row.get("linked_blockers") or [],
            }
    return {"source": LINKED_SOURCE_JSON.name, "missing": True}


def promotion_broad(payload: dict[str, Any]) -> dict[str, Any]:
    for row in payload.get("official_feature_gate_rows") or []:
        if isinstance(row, dict) and row.get("candidate") == BROAD_CANDIDATE:
            return {
                "source": PROMOTION_GAP_JSON.name,
                "generated_at_utc": payload.get("generated_at_utc"),
                "candidate": BROAD_CANDIDATE,
                "future_denominator": None,
                "entries": row.get("entries"),
                "settled": row.get("settled"),
                "coverage_pct": row.get("coverage_pct"),
                "net_cents": row.get("net_cents"),
                "wins": row.get("wins"),
                "losses": row.get("losses"),
                "reconstructed_share": row.get("reconstructed_share"),
                "blockers": row.get("blockers") or [],
            }
    return {"source": PROMOTION_GAP_JSON.name, "missing": True}


def size_shrink_row(payload: dict[str, Any], source: str) -> dict[str, Any]:
    for row in payload.get("lanes") or []:
        if not isinstance(row, dict):
            continue
        if row.get("lane") == ENTRY_LANE and row.get("policy") == SIZE_POLICY:
            return {
                "source": source,
                "generated_at_utc": payload.get("generated_at_utc"),
                "lane": ENTRY_LANE,
                "policy": SIZE_POLICY,
                "settled": row.get("settled"),
                "coverage_pct": row.get("coverage_pct"),
                "weighted_net_cents": row.get("weighted_net_cents"),
                "delta_vs_live_cents": row.get("delta_vs_live_cents"),
                "row_reconstructed_share": row.get("row_reconstructed_share"),
                "blockers": row.get("blockers") or [],
            }
    return {"source": source, "missing": True}


def metric_mismatches(rows: list[dict[str, Any]], keys: list[str]) -> list[dict[str, Any]]:
    mismatches: list[dict[str, Any]] = []
    present = [row for row in rows if not row.get("missing")]
    if len(present) < 2:
        return mismatches
    ref = present[0]
    for key in keys:
        ref_value = ref.get(key)
        values = {str(ref.get("source")): ref_value}
        mismatch = False
        for row in present[1:]:
            value = row.get(key)
            values[str(row.get("source"))] = value
            a = fnum(ref_value)
            b = fnum(value)
            if a is not None and b is not None:
                if abs(a - b) > FLOAT_TOL:
                    mismatch = True
            elif value != ref_value:
                mismatch = True
        if mismatch:
            mismatches.append({"metric": key, "values": values})
    return mismatches


def build_report() -> dict[str, Any]:
    feature = load_json(FEATURE_JSON)
    source_denom = load_json(SOURCE_DENOM_JSON)
    linked = load_json(LINKED_SOURCE_JSON)
    promotion = load_json(PROMOTION_GAP_JSON)
    shrink_source = load_json(SIZE_SHRINK_SOURCE_JSON)
    coverage_runway = load_json(COVERAGE_SIZE_RUNWAY_JSON)
    candidate_vs_live = load_json(CANDIDATE_VS_LIVE_JSON)
    live_summary = load_json(LIVE_SUMMARY_JSON)

    broad_rows = [
        feature_broad(feature),
        source_denom_broad(source_denom),
        linked_broad(linked),
        promotion_broad(promotion),
    ]
    broad_mismatches = metric_mismatches(
        broad_rows,
        ["entries", "settled", "coverage_pct", "net_cents", "wins", "losses", "reconstructed_share"],
    )

    shrink_rows = [
        size_shrink_row(shrink_source, SIZE_SHRINK_SOURCE_JSON.name),
        size_shrink_row(coverage_runway, COVERAGE_SIZE_RUNWAY_JSON.name),
    ]
    shrink_mismatches = metric_mismatches(
        shrink_rows,
        ["settled", "coverage_pct", "weighted_net_cents", "delta_vs_live_cents", "row_reconstructed_share"],
    )

    live_rows = [
        {"source": LIVE_SUMMARY_JSON.name, "live_net_cents": cents_from_live_summary(live_summary)},
        {"source": CANDIDATE_VS_LIVE_JSON.name, "live_net_cents": candidate_vs_live.get("live_net_cents")},
        {"source": PROMOTION_GAP_JSON.name, "live_net_cents": promotion.get("live_net_cents")},
    ]
    live_mismatches = metric_mismatches(live_rows, ["live_net_cents"])

    blockers: list[str] = []
    if any(row.get("missing") for row in broad_rows):
        blockers.append("missing_broad_feature_gate_artifact")
    if broad_mismatches:
        blockers.append("broad_feature_gate_metrics_disagree")
    if any(row.get("missing") for row in shrink_rows):
        blockers.append("missing_size_shrink_artifact")
    if shrink_mismatches:
        blockers.append("size_shrink_runway_metrics_disagree")
    if live_mismatches:
        blockers.append("live_baseline_metrics_disagree")

    return {
        "generated_at_utc": utc_now_iso(),
        "purpose": "research_only_feature_gate_artifact_consistency_guardrail",
        "broad_candidate": BROAD_CANDIDATE,
        "size_policy": SIZE_POLICY,
        "broad_rows": broad_rows,
        "broad_mismatches": broad_mismatches,
        "size_shrink_rows": shrink_rows,
        "size_shrink_mismatches": shrink_mismatches,
        "live_baseline_rows": live_rows,
        "live_baseline_mismatches": live_mismatches,
        "blockers": blockers,
        "consistent_for_promotion_discussion": not blockers,
        "interpretation": interpretation(blockers, broad_mismatches, shrink_mismatches, live_mismatches),
    }


def interpretation(
    blockers: list[str],
    broad_mismatches: list[dict[str, Any]],
    shrink_mismatches: list[dict[str, Any]],
    live_mismatches: list[dict[str, Any]],
) -> list[str]:
    notes = [
        "Research-only audit; this does not score new rules, change live logic, or promote a candidate.",
    ]
    if not blockers:
        notes.append("Feature-gate promotion artifacts agree on the broad row, size-shrink row, and live baseline.")
    else:
        notes.append(f"Artifact consistency blockers: {blockers}.")
    if broad_mismatches:
        notes.append(f"Broad feature-gate mismatches: {[item.get('metric') for item in broad_mismatches]}.")
    if shrink_mismatches:
        notes.append(f"Size-shrink runway mismatches: {[item.get('metric') for item in shrink_mismatches]}.")
    if live_mismatches:
        notes.append(f"Live-baseline mismatches: {[item.get('metric') for item in live_mismatches]}.")
    return notes


def fmt(value: Any) -> str:
    if isinstance(value, float):
        return f"{value:.6f}"
    if value is None:
        return "n/a"
    return str(value)


def write_report(report: dict[str, Any]) -> None:
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8")
    lines = [
        "# v28 Feature-Gate Artifact Consistency Audit",
        "",
        "Research-only consistency guardrail. No live bot changes or orders.",
        "",
        f"- Generated UTC: `{report.get('generated_at_utc')}`",
        f"- Consistent for promotion discussion: `{report.get('consistent_for_promotion_discussion')}`",
        f"- Blockers: `{report.get('blockers')}`",
        "",
        "## Interpretation",
        "",
    ]
    lines.extend(f"- {note}" for note in report.get("interpretation") or [])
    lines.extend(
        [
            "",
            "## Broad Feature-Gate Row",
            "",
            "| source | entries | settled | coverage | net c | W/L | recon share | blockers |",
            "|---|---:|---:|---:|---:|---:|---:|---|",
        ]
    )
    for row in report.get("broad_rows") or []:
        lines.append(
            f"| `{row.get('source')}` | {fmt(row.get('entries'))} | {fmt(row.get('settled'))} | "
            f"{fmt(row.get('coverage_pct'))} | {fmt(row.get('net_cents'))} | "
            f"{fmt(row.get('wins'))}/{fmt(row.get('losses'))} | {fmt(row.get('reconstructed_share'))} | "
            f"{', '.join(row.get('blockers') or []) or ('missing' if row.get('missing') else 'n/a')} |"
        )
    lines.extend(
        [
            "",
            "## Size-Shrink Row",
            "",
            "| source | settled | coverage | weighted net c | delta vs live c | row recon share | blockers |",
            "|---|---:|---:|---:|---:|---:|---|",
        ]
    )
    for row in report.get("size_shrink_rows") or []:
        lines.append(
            f"| `{row.get('source')}` | {fmt(row.get('settled'))} | {fmt(row.get('coverage_pct'))} | "
            f"{fmt(row.get('weighted_net_cents'))} | {fmt(row.get('delta_vs_live_cents'))} | "
            f"{fmt(row.get('row_reconstructed_share'))} | "
            f"{', '.join(row.get('blockers') or []) or ('missing' if row.get('missing') else 'n/a')} |"
        )
    lines.extend(
        [
            "",
            "## Mismatches",
            "",
            f"- Broad row mismatches: `{report.get('broad_mismatches')}`",
            f"- Size-shrink mismatches: `{report.get('size_shrink_mismatches')}`",
            f"- Live-baseline mismatches: `{report.get('live_baseline_mismatches')}`",
        ]
    )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    report = build_report()
    write_report(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
