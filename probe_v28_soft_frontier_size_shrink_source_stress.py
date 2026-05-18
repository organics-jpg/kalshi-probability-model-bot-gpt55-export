"""Source and fragility stress for soft-frontier size-shrink portfolio lanes.

Research-only; no live bot changes or orders.

The size-shrink portfolio is an exposure overlay on the broad soft-frontier
entry branch. This report is keyed by exact policy so the candidate integrity
scorecard can distinguish diagnostic-only rows, source-heavy rows, and strict
post-shrink-birth rows without treating the whole family as unaudited.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
PORTFOLIO_JSON = OUT_DIR / "v28_soft_frontier_size_shrink_portfolio_latest.json"
OUT_JSON = OUT_DIR / "v28_soft_frontier_size_shrink_source_stress_latest.json"
OUT_MD = OUT_DIR / "v28_soft_frontier_size_shrink_source_stress_latest.md"

MAX_RECONSTRUCTED_SHARE = 0.35
MIN_FULL_LOSS_CUSHION = 3
MIN_SETTLED = 30
TARGET_COVERAGE_MIN = 75.0


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


def as_float(value: Any) -> float | None:
    if value is None or value == "":
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def as_int(value: Any) -> int:
    try:
        return int(value or 0)
    except (TypeError, ValueError):
        return 0


def source_share(counts: dict[str, Any]) -> float | None:
    total = sum(as_int(value) for value in counts.values())
    if total <= 0:
        return None
    approved = as_int(counts.get("approved_entry"))
    return (total - approved) / total


def clean_rows_needed(counts: dict[str, Any]) -> int:
    total = sum(as_int(value) for value in counts.values())
    approved = as_int(counts.get("approved_entry"))
    if total <= 0:
        return 0
    needed = 0
    while (total - approved) / total > MAX_RECONSTRUCTED_SHARE:
        needed += 1
        total += 1
        approved += 1
    return needed


def full_loss_cushion(summary: dict[str, Any]) -> int:
    direct = summary.get("full_loss_cushion_estimate")
    if direct is not None:
        return as_int(direct)
    net_cents = as_float(summary.get("net_cents")) or 0.0
    return int(max(0.0, net_cents) // 100.0)


def blockers(summary: dict[str, Any], share: float | None, cushion: int, strict_forward: bool) -> list[str]:
    out: list[str] = []
    settled = as_int(summary.get("settled"))
    coverage = as_float(summary.get("coverage_pct"))
    net_cents = as_float(summary.get("net_cents")) or 0.0
    if not strict_forward:
        out.append("diagnostic_only_prefreeze")
    if settled < MIN_SETTLED:
        out.append("settled_lt_30")
    if coverage is None or coverage < TARGET_COVERAGE_MIN:
        out.append("coverage_too_low")
    if net_cents <= 0.0:
        out.append("net_not_positive")
    if share is not None and share > MAX_RECONSTRUCTED_SHARE:
        out.append("reconstructed_share_gt_35pct")
    if cushion < MIN_FULL_LOSS_CUSHION:
        out.append("full_loss_cushion_lt_3")
    return out


def evaluate_variant(lane: dict[str, Any], variant: dict[str, Any]) -> dict[str, Any]:
    summary = variant.get("summary") if isinstance(variant.get("summary"), dict) else {}
    counts = variant.get("source_counts") if isinstance(variant.get("source_counts"), dict) else {}
    share = source_share(counts)
    cushion = full_loss_cushion(summary)
    strict_forward = bool(lane.get("strict_forward"))
    return {
        "gate": "soft_frontier_size_shrink_portfolio",
        "lane": lane.get("lane"),
        "policy": variant.get("candidate"),
        "weight_policy": variant.get("weight_policy"),
        "strict_forward": strict_forward,
        "summary": summary,
        "source_counts": {"candidate": counts},
        "reconstructed_share": share,
        "clean_approved_rows_needed_for_source_gate": clean_rows_needed(counts),
        "full_loss_cushion_estimate": cushion,
        "blockers": blockers(summary, share, cushion, strict_forward),
        "variant_blockers": variant.get("blockers") or [],
        "tag_counts": summary.get("tag_counts") or {},
    }


def build_report() -> dict[str, Any]:
    payload = load_json(PORTFOLIO_JSON)
    policies: list[dict[str, Any]] = []
    for lane in payload.get("lanes") or []:
        if not isinstance(lane, dict):
            continue
        for variant in lane.get("variants") or []:
            if isinstance(variant, dict):
                policies.append(evaluate_variant(lane, variant))
    policies.sort(
        key=lambda row: (
            len(row.get("blockers") or []),
            -float((row.get("summary") or {}).get("net_cents") or -999999.0),
            -float((row.get("summary") or {}).get("coverage_pct") or 0.0),
        )
    )
    return {
        "generated_at_utc": utc_now_iso(),
        "portfolio_generated_at_utc": payload.get("generated_at_utc"),
        "portfolio_freeze_ts_utc": (payload.get("state") or {}).get("freeze_ts_utc"),
        "purpose": "Policy-specific source and full-loss stress for soft-frontier size-shrink portfolio rows.",
        "policies": policies,
        "interpretation": interpretation(policies),
    }


def interpretation(policies: list[dict[str, Any]]) -> list[str]:
    notes = [
        "Policy-specific audit only; no live logic changes and no promotion by itself.",
        "Diagnostic lanes remain diagnostic even when their source share is clean enough.",
    ]
    if policies:
        best = policies[0]
        summary = best.get("summary") or {}
        notes.append(
            f"Best stress row {best.get('policy')} has strict_forward={best.get('strict_forward')}, "
            f"{summary.get('settled')} settled, coverage {summary.get('coverage_pct')}%, "
            f"net {summary.get('net_cents')}c, reconstructed share {best.get('reconstructed_share')}, "
            f"cushion {best.get('full_loss_cushion_estimate')}, blockers {best.get('blockers')}."
        )
        strict = [row for row in policies if row.get("strict_forward")]
        if strict:
            top_strict = strict[0]
            top_summary = top_strict.get("summary") or {}
            notes.append(
                f"Best strict post-shrink row {top_strict.get('policy')} has "
                f"{top_summary.get('settled')} settled, coverage {top_summary.get('coverage_pct')}%, "
                f"net {top_summary.get('net_cents')}c, reconstructed share "
                f"{top_strict.get('reconstructed_share')}, blockers {top_strict.get('blockers')}."
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
        "# v28 Soft-Frontier Size-Shrink Source Stress",
        "",
        "Research-only; no live bot changes or orders.",
        "",
        f"- Generated UTC: `{report.get('generated_at_utc')}`",
        f"- Portfolio freeze UTC: `{report.get('portfolio_freeze_ts_utc')}`",
        "",
        "## Interpretation",
        "",
    ]
    lines.extend(f"- {note}" for note in report.get("interpretation") or [])
    lines.extend([
        "",
        "## Policies",
        "",
        "| policy | strict | settled | W/L | coverage | net c | recon | clean rows needed | cushion | blockers |",
        "|---|---|---:|---:|---:|---:|---:|---:|---:|---|",
    ])
    for row in report.get("policies") or []:
        summary = row.get("summary") or {}
        lines.append(
            f"| {row.get('policy')} | {row.get('strict_forward')} | {summary.get('settled')} | "
            f"{summary.get('wins')}/{summary.get('losses')} | {fmt(summary.get('coverage_pct'))} | "
            f"{fmt(summary.get('net_cents'))} | {fmt(row.get('reconstructed_share'))} | "
            f"{row.get('clean_approved_rows_needed_for_source_gate')} | "
            f"{row.get('full_loss_cushion_estimate')} | {', '.join(row.get('blockers') or []) or 'none'} |"
        )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    report = build_report()
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8")
    write_md(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
