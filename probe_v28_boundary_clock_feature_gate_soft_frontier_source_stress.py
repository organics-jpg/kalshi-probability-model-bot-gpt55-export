"""Source and fragility stress for the boundary-clock soft-frontier watch.

Research-only; no live bot changes or orders.

This audit is keyed by exact soft-frontier policy so the integrity scorecard
can distinguish target-coverage variants that are source-stressed from
lower-coverage variants that are cleaner but not broad enough yet.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
SOFT_FRONTIER_JSON = OUT_DIR / "v28_boundary_clock_feature_gate_soft_frontier_watch_latest.json"
OUT_JSON = OUT_DIR / "v28_boundary_clock_feature_gate_soft_frontier_source_stress_latest.json"
OUT_MD = OUT_DIR / "v28_boundary_clock_feature_gate_soft_frontier_source_stress_latest.md"

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
    while total > 0 and (total - approved) / total > MAX_RECONSTRUCTED_SHARE:
        needed += 1
        approved += 1
        total += 1
    return needed


def full_loss_runway(net_cents: float) -> list[dict[str, Any]]:
    rows = []
    for losses in range(0, 6):
        net_after = net_cents - 100.0 * losses
        rows.append(
            {
                "added_full_losses": losses,
                "net_after_losses_cents": net_after,
                "still_positive": net_after > 0.0,
            }
        )
    return rows


def blockers(summary: dict[str, Any], share: float | None, cushion: int) -> list[str]:
    out = []
    settled = as_int(summary.get("settled"))
    coverage = as_float(summary.get("coverage_pct"))
    net_cents = as_float(summary.get("net_cents")) or 0.0
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


def evaluate_variant(lane_name: str, variant: dict[str, Any]) -> dict[str, Any]:
    summary = variant.get("candidate_summary") or {}
    counts = variant.get("source_counts") if isinstance(variant.get("source_counts"), dict) else {}
    share = source_share(counts)
    clean_needed = clean_rows_needed(counts)
    net_cents = as_float(summary.get("net_cents")) or 0.0
    runway = full_loss_runway(net_cents)
    cushion = max((row["added_full_losses"] for row in runway if row["still_positive"]), default=0)
    return {
        "gate": "boundary_clock_feature_gate_soft_frontier",
        "lane": lane_name,
        "policy": variant.get("candidate") or lane_name,
        "summary": summary,
        "source_counts": {"candidate": counts},
        "reconstructed_share": share,
        "clean_approved_rows_needed_for_source_gate": clean_needed,
        "full_loss_runway": runway,
        "full_loss_cushion_estimate": cushion,
        "blockers": blockers(summary, share, cushion),
        "variant_blockers": variant.get("blockers") or [],
        "mechanism_tag_counts": variant.get("mechanism_tag_counts") or {},
    }


def build_report() -> dict[str, Any]:
    payload = load_json(SOFT_FRONTIER_JSON)
    rows = []
    for lane in payload.get("lanes") or []:
        if not isinstance(lane, dict):
            continue
        lane_name = str(lane.get("lane") or "")
        if not lane_name.startswith("post_soft_frontier_birth_"):
            continue
        for variant in lane.get("variants") or []:
            if isinstance(variant, dict):
                rows.append(evaluate_variant(lane_name, variant))
    rows.sort(
        key=lambda row: (
            len(row.get("blockers") or []),
            -float((row.get("summary") or {}).get("net_cents") or -999999.0),
            -float((row.get("summary") or {}).get("coverage_pct") or 0.0),
        )
    )
    return {
        "generated_at_utc": utc_now_iso(),
        "soft_frontier_generated_at_utc": payload.get("generated_at_utc"),
        "freeze_ts_utc": (payload.get("state") or {}).get("freeze_ts_utc"),
        "purpose": "Policy-specific source and full-loss stress for strict soft-frontier forward rows.",
        "policies": rows,
        "interpretation": interpretation(rows),
    }


def interpretation(rows: list[dict[str, Any]]) -> list[str]:
    notes = [
        "Policy-specific audit only; no live logic changes and no promotion by itself.",
    ]
    if rows:
        best = rows[0]
        summary = best.get("summary") or {}
        notes.append(
            f"Best stress row {best.get('policy')} has {summary.get('settled')} settled, "
            f"coverage {summary.get('coverage_pct')}%, net {summary.get('net_cents')}c, "
            f"reconstructed share {best.get('reconstructed_share')}, clean rows needed "
            f"{best.get('clean_approved_rows_needed_for_source_gate')}, cushion "
            f"{best.get('full_loss_cushion_estimate')}, blockers {best.get('blockers')}."
        )
        target = [
            row for row in rows
            if (as_float((row.get("summary") or {}).get("coverage_pct")) or 0.0) >= TARGET_COVERAGE_MIN
        ]
        if target:
            top_target = target[0]
            top_summary = top_target.get("summary") or {}
            notes.append(
                f"Best target-coverage row {top_target.get('policy')} has net "
                f"{top_summary.get('net_cents')}c and reconstructed share "
                f"{top_target.get('reconstructed_share')}."
            )
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
        "# v28 Boundary-Clock Feature-Gate Soft-Frontier Source Stress",
        "",
        "Research-only; no live bot changes or orders.",
        "",
        f"- Generated UTC: `{report.get('generated_at_utc')}`",
        f"- Soft-frontier freeze UTC: `{report.get('freeze_ts_utc')}`",
        "",
        "## Interpretation",
        "",
    ]
    lines.extend(f"- {note}" for note in report.get("interpretation") or [])
    lines.extend(
        [
            "",
            "## Policies",
            "",
            "| policy | settled | W/L | coverage | net c | recon | clean rows needed | cushion | blockers |",
            "|---|---:|---:|---:|---:|---:|---:|---:|---|",
        ]
    )
    for row in report.get("policies") or []:
        summary = row.get("summary") or {}
        lines.append(
            f"| {row.get('policy')} | {summary.get('settled')} | {summary.get('wins')}/{summary.get('losses')} | "
            f"{fmt(summary.get('coverage_pct'))} | {fmt(summary.get('net_cents'))} | "
            f"{fmt(row.get('reconstructed_share'))} | {row.get('clean_approved_rows_needed_for_source_gate')} | "
            f"{row.get('full_loss_cushion_estimate')} | {', '.join(row.get('blockers') or []) or 'none'} |"
        )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    report = build_report()
    write_md(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
