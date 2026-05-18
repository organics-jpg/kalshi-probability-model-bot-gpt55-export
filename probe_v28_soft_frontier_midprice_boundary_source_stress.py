"""Source/exposure stress for soft-frontier mid-price boundary shrink.

Research-only; no live bot changes or orders.

The mid-price boundary shrink is a size overlay, not a source-quality repair.
This audit keeps the official row-count reconstructed share separate from the
size-weighted reconstructed exposure share so promotion gates do not silently
change while account-risk evidence improves.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
SHRINK_JSON = OUT_DIR / "v28_soft_frontier_midprice_boundary_shrink_latest.json"
OUT_JSON = OUT_DIR / "v28_soft_frontier_midprice_boundary_source_stress_latest.json"
OUT_MD = OUT_DIR / "v28_soft_frontier_midprice_boundary_source_stress_latest.md"

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


def is_approved(source: Any) -> bool:
    return str(source or "") == "approved_entry"


def source_share(counts: dict[str, Any]) -> float | None:
    total = sum(as_int(value) for value in counts.values())
    if total <= 0:
        return None
    approved = as_int(counts.get("approved_entry"))
    return (total - approved) / total


def clean_rows_needed_for_share(counts: dict[str, Any], max_share: float = MAX_RECONSTRUCTED_SHARE) -> int:
    total = sum(as_int(value) for value in counts.values())
    approved = as_int(counts.get("approved_entry"))
    if total <= 0:
        return 0
    needed = 0
    while total > 0 and (total - approved) / total > max_share:
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


def exposure_metrics(summary: dict[str, Any]) -> dict[str, Any]:
    rows = summary.get("rows") if isinstance(summary.get("rows"), list) else []
    total_weight = 0.0
    approved_weight = 0.0
    reconstructed_weight = 0.0
    total_net = 0.0
    approved_net = 0.0
    reconstructed_net = 0.0
    boundary_weight = 0.0
    boundary_reconstructed_weight = 0.0
    boundary_raw_net = 0.0
    boundary_weighted_net = 0.0
    row_counts = {"approved_entry": 0, "rejected_actionable": 0, "other": 0}

    for row in rows:
        if not isinstance(row, dict):
            continue
        source = row.get("source")
        weight = as_float(row.get("weight"))
        if weight is None:
            weight = 1.0
        weighted_net = as_float(row.get("weighted_net_cents")) or 0.0
        raw_net = as_float(row.get("raw_net_cents")) or 0.0
        approved = is_approved(source)
        total_weight += weight
        total_net += weighted_net
        if approved:
            approved_weight += weight
            approved_net += weighted_net
            row_counts["approved_entry"] += 1
        else:
            reconstructed_weight += weight
            reconstructed_net += weighted_net
            if str(source or "") == "rejected_actionable":
                row_counts["rejected_actionable"] += 1
            else:
                row_counts["other"] += 1
        if bool(row.get("midprice_boundary_band")):
            boundary_weight += weight
            boundary_raw_net += raw_net
            boundary_weighted_net += weighted_net
            if not approved:
                boundary_reconstructed_weight += weight

    weighted_reconstructed_exposure_share = (
        reconstructed_weight / total_weight if total_weight > 0.0 else None
    )
    weighted_approved_exposure_share = approved_weight / total_weight if total_weight > 0.0 else None
    return {
        "row_counts_from_rows": row_counts,
        "total_weight": total_weight,
        "approved_weight": approved_weight,
        "reconstructed_weight": reconstructed_weight,
        "weighted_approved_exposure_share": weighted_approved_exposure_share,
        "weighted_reconstructed_exposure_share": weighted_reconstructed_exposure_share,
        "weighted_net_cents": total_net,
        "approved_weighted_net_cents": approved_net,
        "reconstructed_weighted_net_cents": reconstructed_net,
        "midprice_boundary_weight": boundary_weight,
        "midprice_boundary_reconstructed_weight": boundary_reconstructed_weight,
        "midprice_boundary_raw_net_cents": boundary_raw_net,
        "midprice_boundary_weighted_net_cents": boundary_weighted_net,
    }


def blockers(
    summary: dict[str, Any],
    row_share: float | None,
    weighted_share: float | None,
    cushion: int,
    strict_forward: bool,
) -> list[str]:
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
    if row_share is not None and row_share > MAX_RECONSTRUCTED_SHARE:
        out.append("row_reconstructed_share_gt_35pct")
    if weighted_share is not None and weighted_share > MAX_RECONSTRUCTED_SHARE:
        out.append("weighted_reconstructed_exposure_gt_35pct")
    if cushion < MIN_FULL_LOSS_CUSHION:
        out.append("full_loss_cushion_lt_3")
    return out


def evaluate_variant(lane: dict[str, Any], variant: dict[str, Any]) -> dict[str, Any]:
    summary = variant.get("summary") if isinstance(variant.get("summary"), dict) else {}
    counts = variant.get("source_counts") if isinstance(variant.get("source_counts"), dict) else {}
    row_share = source_share(counts)
    exposure = exposure_metrics(summary)
    weighted_share = exposure.get("weighted_reconstructed_exposure_share")
    cushion = full_loss_cushion(summary)
    strict_forward = bool(lane.get("strict_forward"))
    settled = as_int(summary.get("settled"))
    return {
        "gate": "soft_frontier_midprice_boundary_shrink",
        "lane": lane.get("lane"),
        "policy": variant.get("candidate"),
        "weight_policy": variant.get("weight_policy"),
        "strict_forward": strict_forward,
        "summary": {
            key: value
            for key, value in summary.items()
            if key != "rows"
        },
        "source_counts": {"candidate": counts},
        "row_reconstructed_share": row_share,
        "weighted_reconstructed_exposure_share": weighted_share,
        "weighted_approved_exposure_share": exposure.get("weighted_approved_exposure_share"),
        "exposure_metrics": exposure,
        "clean_approved_rows_needed_for_row_source_gate": clean_rows_needed_for_share(counts),
        "settled_rows_needed_for_sample_gate": max(0, MIN_SETTLED - settled),
        "full_loss_cushion_estimate": cushion,
        "blockers": blockers(summary, row_share, weighted_share, cushion, strict_forward),
        "variant_blockers": variant.get("blockers") or [],
    }


def build_report() -> dict[str, Any]:
    payload = load_json(SHRINK_JSON)
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
        "source_generated_at_utc": payload.get("generated_at_utc"),
        "freeze_ts_utc": (payload.get("state") or {}).get("freeze_ts_utc"),
        "purpose": (
            "Policy-specific source and notional exposure stress for the "
            "soft-frontier mid-price boundary shrink watch."
        ),
        "official_gate_note": (
            "Promotion source quality remains row-count reconstructed share <=35%; "
            "weighted exposure share is diagnostic account-risk evidence only."
        ),
        "policies": policies,
        "interpretation": interpretation(policies),
    }


def interpretation(policies: list[dict[str, Any]]) -> list[str]:
    notes = [
        "Policy-specific audit only; no live logic changes and no promotion by itself.",
        "Weighted reconstructed exposure can support the account-risk argument, but it does not replace the official row-count source gate.",
    ]
    if not policies:
        return notes

    best = policies[0]
    summary = best.get("summary") or {}
    notes.append(
        f"Best stress row {best.get('policy')} has strict_forward={best.get('strict_forward')}, "
        f"{summary.get('settled')} settled, coverage {summary.get('coverage_pct')}%, "
        f"net {summary.get('net_cents')}c, row reconstructed share "
        f"{best.get('row_reconstructed_share')}, weighted reconstructed exposure share "
        f"{best.get('weighted_reconstructed_exposure_share')}, cushion "
        f"{best.get('full_loss_cushion_estimate')}, blockers {best.get('blockers')}."
    )

    strict = [row for row in policies if row.get("strict_forward")]
    if strict:
        top_strict = strict[0]
        top_summary = top_strict.get("summary") or {}
        notes.append(
            f"Best strict post-birth row {top_strict.get('policy')} has "
            f"{top_summary.get('settled')} settled, net {top_summary.get('net_cents')}c, "
            f"row reconstructed share {top_strict.get('row_reconstructed_share')}, "
            f"weighted reconstructed exposure share "
            f"{top_strict.get('weighted_reconstructed_exposure_share')}, blockers "
            f"{top_strict.get('blockers')}."
        )

    near_miss = [
        row
        for row in policies
        if not row.get("strict_forward")
        and row.get("row_reconstructed_share") is not None
        and row.get("weighted_reconstructed_exposure_share") is not None
        and row["row_reconstructed_share"] > MAX_RECONSTRUCTED_SHARE
        and row["weighted_reconstructed_exposure_share"] <= MAX_RECONSTRUCTED_SHARE
    ]
    if near_miss:
        row = near_miss[0]
        summary = row.get("summary") or {}
        notes.append(
            f"Exposure-only near miss: {row.get('policy')} has row reconstructed "
            f"share {row.get('row_reconstructed_share')} but weighted exposure "
            f"share {row.get('weighted_reconstructed_exposure_share')} at "
            f"{summary.get('settled')} settled and {summary.get('net_cents')}c."
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
        "# v28 Soft-Frontier Mid-Price Boundary Source Stress",
        "",
        "Research-only; no live bot changes or orders.",
        "",
        f"- Generated UTC: `{report.get('generated_at_utc')}`",
        f"- Candidate freeze UTC: `{report.get('freeze_ts_utc')}`",
        f"- Official gate note: {report.get('official_gate_note')}",
        "",
        "## Interpretation",
        "",
    ]
    lines.extend(f"- {note}" for note in report.get("interpretation") or [])
    lines.extend([
        "",
        "## Policies",
        "",
        "| policy | strict | settled | W/L | coverage | net c | row recon | weighted recon exposure | clean rows needed | cushion | blockers |",
        "|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---|",
    ])
    for row in report.get("policies") or []:
        summary = row.get("summary") or {}
        lines.append(
            f"| {row.get('policy')} | {row.get('strict_forward')} | {summary.get('settled')} | "
            f"{summary.get('wins')}/{summary.get('losses')} | {fmt(summary.get('coverage_pct'))} | "
            f"{fmt(summary.get('net_cents'))} | {fmt(row.get('row_reconstructed_share'))} | "
            f"{fmt(row.get('weighted_reconstructed_exposure_share'))} | "
            f"{row.get('clean_approved_rows_needed_for_row_source_gate')} | "
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
