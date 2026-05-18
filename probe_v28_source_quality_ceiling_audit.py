"""Source-quality ceiling audit for v28 broad-entry candidates.

Research-only; no live bot changes or orders.

The current best broad candidates are profitable in some forward slices, but
many depend on reconstructed/rejected-actionable rows. This audit summarizes
whether the active feature families can simultaneously satisfy coverage,
profitability, and source-quality constraints using only observable rules.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
OUT_JSON = OUT_DIR / "v28_source_quality_ceiling_audit_latest.json"
OUT_MD = OUT_DIR / "v28_source_quality_ceiling_audit_latest.md"

FILES = {
    "feature_source_denominator": OUT_DIR / "v28_boundary_clock_feature_gate_source_denominator_audit_latest.json",
    "feature_coverage_frontier": OUT_DIR / "v28_boundary_clock_feature_gate_coverage_source_frontier_latest.json",
    "feature_soft_frontier": OUT_DIR / "v28_boundary_clock_feature_gate_soft_frontier_watch_latest.json",
    "hybrid_source_frontier": OUT_DIR / "v28_hybrid_boundary_source_frontier_latest.json",
    "hybrid_source_dilution": OUT_DIR / "v28_hybrid_boundary_source_dilution_runway_latest.json",
    "goal_audit": OUT_DIR / "v28_goal_completion_audit_latest.json",
}


def load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
    return payload if isinstance(payload, dict) else {}


def as_float(value: Any) -> float | None:
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def lane(payload: dict[str, Any], name: str) -> dict[str, Any]:
    for row in payload.get("lanes") or []:
        if isinstance(row, dict) and row.get("lane") == name:
            return row
    return {}


def best_rule(row: dict[str, Any]) -> dict[str, Any]:
    rules = row.get("rules")
    if isinstance(rules, list) and rules:
        return rules[0]
    frontier = row.get("pareto_frontier")
    if isinstance(frontier, list) and frontier:
        return frontier[0]
    return {}


def first_clean_broad(row: dict[str, Any]) -> dict[str, Any]:
    clean = row.get("clean_broad_positive")
    return clean[0] if isinstance(clean, list) and clean else {}


def window(payload: dict[str, Any], name: str) -> dict[str, Any]:
    for row in payload.get("windows") or []:
        if isinstance(row, dict) and row.get("window") == name:
            return row
    return {}


def first_variant(row: dict[str, Any]) -> dict[str, Any]:
    variants = row.get("variants")
    return variants[0] if isinstance(variants, list) and variants else {}


def source_counts_total(counts: dict[str, Any]) -> int:
    return sum(int(as_float(value) or 0) for value in counts.values())


def build_report() -> dict[str, Any]:
    data = {key: load_json(path) for key, path in FILES.items()}
    source_den = data["feature_source_denominator"]
    coverage_frontier = data["feature_coverage_frontier"]
    soft = data["feature_soft_frontier"]
    hybrid_frontier = data["hybrid_source_frontier"]
    dilution = data["hybrid_source_dilution"]

    source_entry = best_rule(lane(source_den, "post_feature_freeze_entry"))
    coverage_entry_lane = lane(coverage_frontier, "post_feature_freeze_entry")
    coverage_best = best_rule(coverage_entry_lane)
    coverage_clean = first_clean_broad(coverage_entry_lane)
    soft_post_entry = best_rule(lane(soft, "post_soft_frontier_birth_entry"))
    soft_diag_entry = best_rule(lane(soft, "diagnostic_entry"))
    hybrid_post = first_variant(window(hybrid_frontier, "post_stack_freeze_window"))
    hybrid_diag = first_variant(window(hybrid_frontier, "diagnostic_existing_target_window"))
    dilution_post = (dilution.get("post_freeze_frontier") or dilution.get("post_freeze_top") or [])
    dilution_diag = (dilution.get("diagnostic_frontier") or dilution.get("diagnostic_top") or [])
    dilution_post_best = dilution_post[0] if isinstance(dilution_post, list) and dilution_post else {}
    dilution_diag_best = dilution_diag[0] if isinstance(dilution_diag, list) and dilution_diag else {}

    source_available = source_entry.get("available_source_market_counts") or {}
    approved_available = int(as_float(source_available.get("approved_entry")) or 0)
    total_available = source_counts_total(source_available)
    approved_available_share = approved_available / total_available if total_available else None

    findings = [
        {
            "finding": "approved_only_is_profitable_but_too_narrow",
            "evidence": {
                "rule": source_entry.get("rule"),
                "coverage_pct": (source_entry.get("summary") or {}).get("coverage_pct"),
                "net_cents": (source_entry.get("summary") or {}).get("net_cents"),
                "selected_reconstructed_share": source_entry.get("selected_reconstructed_share"),
                "approved_available_share": approved_available_share,
                "available_source_market_counts": source_available,
            },
            "interpretation": "The cleanest currently observed source slice wins but cannot reach the 75% coverage target.",
        },
        {
            "finding": "best_observable_broad_frontier_still_misses_gates",
            "evidence": {
                "rule": coverage_best.get("rule"),
                "coverage_pct": (coverage_best.get("summary") or {}).get("coverage_pct"),
                "net_cents": (coverage_best.get("summary") or {}).get("net_cents"),
                "reconstructed_share": coverage_best.get("reconstructed_share"),
                "blockers": coverage_best.get("blockers"),
                "clean_broad_positive_exists": bool(coverage_clean),
            },
            "interpretation": "The best post-freeze observable frontier is close but still below coverage and just above the reconstructed-share ceiling.",
        },
        {
            "finding": "diagnostic_soft_frontier_is_promising_but_unproven",
            "evidence": {
                "diagnostic_rule": soft_diag_entry.get("candidate") or soft_diag_entry.get("rule"),
                "diagnostic_coverage_pct": (soft_diag_entry.get("summary") or {}).get("coverage_pct"),
                "diagnostic_net_cents": (soft_diag_entry.get("summary") or {}).get("net_cents"),
                "diagnostic_reconstructed_share": soft_diag_entry.get("reconstructed_share"),
                "post_rule": soft_post_entry.get("candidate") or soft_post_entry.get("rule"),
                "post_settled": (soft_post_entry.get("summary") or {}).get("settled"),
                "post_blockers": soft_post_entry.get("blockers"),
            },
            "interpretation": "The soft frontier is the most coherent repair idea, but its strict post-birth sample is basically empty.",
        },
        {
            "finding": "hybrid_boundary_stack_needs_clean_forward_dilution",
            "evidence": {
                "post_candidate": hybrid_post.get("candidate"),
                "post_coverage_pct": (hybrid_post.get("candidate_summary") or {}).get("coverage_pct"),
                "post_net_cents": (hybrid_post.get("candidate_summary") or {}).get("net_cents"),
                "post_reconstructed_share": hybrid_post.get("reconstructed_share"),
                "post_clean_rows_needed_for_source_gate": dilution_post_best.get("future_approved_selected_needed_for_gate"),
                "diagnostic_candidate": hybrid_diag.get("candidate"),
                "diagnostic_net_cents": (hybrid_diag.get("candidate_summary") or {}).get("net_cents"),
                "diagnostic_clean_rows_needed_for_source_gate": dilution_diag_best.get("future_approved_selected_needed_for_gate"),
            },
            "interpretation": "The combined stack can be promising, but current forward evidence is too reconstructed-heavy to trust.",
        },
    ]

    conclusion = classify(findings)
    return {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "audit": "source_quality_ceiling",
        "conclusion": conclusion,
        "findings": findings,
        "next": next_steps(conclusion),
        "inputs": {name: str(path) for name, path in FILES.items()},
    }


def classify(findings: list[dict[str, Any]]) -> dict[str, Any]:
    approved = findings[0]["evidence"]
    frontier = findings[1]["evidence"]
    soft = findings[2]["evidence"]
    broad_clean_exists = bool(frontier.get("clean_broad_positive_exists"))
    approved_cov = as_float(approved.get("coverage_pct"))
    frontier_cov = as_float(frontier.get("coverage_pct"))
    frontier_recon = as_float(frontier.get("reconstructed_share"))
    soft_post_settled = int(as_float(soft.get("post_settled")) or 0)
    return {
        "goal_ready": False,
        "source_quality_ceiling_active": not broad_clean_exists,
        "best_current_status": "promising_but_not_promotable",
        "why": (
            "No current observable post-freeze rule simultaneously clears broad coverage, positive net, "
            "source quality, sample size, and full-loss cushion. The nearest broad frontier is still below "
            "coverage or above the reconstructed-share ceiling, while cleaner approved-only rows are too narrow."
        ),
        "approved_only_coverage_pct": approved_cov,
        "best_frontier_coverage_pct": frontier_cov,
        "best_frontier_reconstructed_share": frontier_recon,
        "soft_frontier_post_settled": soft_post_settled,
    }


def next_steps(conclusion: dict[str, Any]) -> list[str]:
    return [
        "Keep the soft-frontier and combined-stack monitors running until post-birth rows reach real sample size.",
        "Do not promote broad candidates while source_quality_ceiling_active is true.",
        "Treat approved-only profitable rows as calibration hints, not a broad strategy, until they naturally cover more markets.",
        "Search for observable features that explain why reconstructed-heavy rows differ: cheap ask tails, weak abs-distance, thin edge, and moderate recross are the current suspects.",
    ]


def fmt(value: Any) -> str:
    if value is None:
        return "None"
    if isinstance(value, float):
        return f"{value:.6f}"
    return str(value)


def write_md(report: dict[str, Any]) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8")
    conclusion = report.get("conclusion") or {}
    lines = [
        "# v28 Source-Quality Ceiling Audit",
        "",
        "Research-only: checks whether current broad candidates can clear source-quality without losing coverage.",
        "",
        f"- Generated UTC: `{report.get('generated_at_utc')}`",
        f"- Goal ready: `{conclusion.get('goal_ready')}`",
        f"- Source-quality ceiling active: `{conclusion.get('source_quality_ceiling_active')}`",
        f"- Status: `{conclusion.get('best_current_status')}`",
        "",
        "## Conclusion",
        "",
        f"- {conclusion.get('why')}",
        "",
        "## Findings",
        "",
    ]
    for finding in report.get("findings") or []:
        lines.append(f"### {finding.get('finding')}")
        lines.append(f"- Interpretation: {finding.get('interpretation')}")
        for key, value in (finding.get("evidence") or {}).items():
            lines.append(f"- `{key}`: `{fmt(value)}`")
        lines.append("")
    lines.extend(["## Next", ""])
    for item in report.get("next") or []:
        lines.append(f"- {item}")
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    report = build_report()
    write_md(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
