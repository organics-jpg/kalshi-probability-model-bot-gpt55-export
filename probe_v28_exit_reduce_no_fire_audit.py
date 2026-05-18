"""No-fire audit for frozen v28 probability-reduce exit watches.

Research-only; no live bot changes or orders.

The denominator audit shows reduce-depth, reduce-refinement, and reduce-geometry
are collecting rows but firing no suppressions. This probe explains whether the
problem is absent probability-reduce exits, overly strict guards, or guard logic
correctly refusing harmful suppressions.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
DEPTH_OPP_JSON = OUT_DIR / "v28_exit_reduce_depth_gate_opportunity_latest.json"
GEOMETRY_OPP_JSON = OUT_DIR / "v28_exit_reduce_geometry_opportunity_latest.json"
REFINEMENT_JSON = OUT_DIR / "v28_frozen_exit_reduce_loss_control_refinement_latest.json"
DENOM_JSON = OUT_DIR / "v28_exit_watch_denominator_audit_latest.json"
OUT_JSON = OUT_DIR / "v28_exit_reduce_no_fire_audit_latest.json"
OUT_MD = OUT_DIR / "v28_exit_reduce_no_fire_audit_latest.md"


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


def fnum(value: Any, default: float = 0.0) -> float:
    if value is None or value == "":
        return default
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def summarize_depth(payload: dict[str, Any]) -> dict[str, Any]:
    rules = [row for row in payload.get("rules") or [] if isinstance(row, dict)]
    strict = next(
        (row for row in rules if row.get("candidate") == "reduce_suppress_p_hold_ge_079_entry_depth_lte_384"),
        {},
    )
    loose = next(
        (row for row in rules if row.get("candidate") == "reduce_suppress_p_hold_ge_075_entry_depth_lte_384"),
        {},
    )
    loose_examples = loose.get("would_suppress_examples") or []
    loose_delta = sum(fnum(row.get("delta_if_suppressed_cents")) for row in loose_examples)
    return {
        "freeze_ts_utc": payload.get("depth_gate_freeze_ts_utc"),
        "post_birth_rows": payload.get("post_birth_rows"),
        "probability_reduce_rows": strict.get("probability_reduce_rows") or loose.get("probability_reduce_rows"),
        "strict_candidate": strict.get("candidate"),
        "strict_would_suppress_rows": strict.get("would_suppress_rows"),
        "strict_fail_reasons": strict.get("fail_reason_counts") or {},
        "loose_candidate": loose.get("candidate"),
        "loose_would_suppress_rows": loose.get("would_suppress_rows"),
        "loose_would_suppress_delta_cents": loose_delta,
        "loose_would_suppress_examples": loose_examples,
        "read": (
            "Strict p_hold>=0.79 avoids the only observed post-birth reduce candidate; "
            "looser p_hold>=0.75 would fire once but that row is harmful."
        ),
    }


def summarize_geometry(payload: dict[str, Any]) -> dict[str, Any]:
    summary = payload.get("summary") if isinstance(payload.get("summary"), dict) else {}
    near = payload.get("near_miss_rows") or []
    rejected = [
        row for row in near
        if "no_positive_drawdown_reject" in (row.get("fail_reasons") or [])
        or "yes_negative_drawdown_reject" in (row.get("fail_reasons") or [])
    ]
    base_reduce_rejected = [
        row for row in rejected
        if row.get("exit_reason") == "mushroom_v28_probability_reduce"
    ]
    return {
        "freeze_ts_utc": (payload.get("freeze") or {}).get("freeze_ts_utc"),
        "post_freeze_rows": summary.get("post_freeze_rows"),
        "probability_reduce_rows": summary.get("probability_reduce_rows"),
        "base_p_hold_candidates": summary.get("base_p_hold_candidates"),
        "geometry_would_suppress_rows": summary.get("geometry_would_suppress_rows"),
        "geometry_rejected_base_candidates": summary.get("geometry_rejected_base_candidates"),
        "geometry_rejected_base_delta_cents": summary.get("geometry_rejected_base_delta_cents"),
        "reason_counts": summary.get("reason_counts") or {},
        "rejected_by_geometry_summary": summary.get("rejected_by_geometry_summary") or {},
        "geometry_rows": payload.get("geometry_rows") or [],
        "base_reduce_rejected_examples": base_reduce_rejected,
        "read": (
            "Geometry is loss-conservative but density-starved: it rejected one helpful "
            "and one harmful base p-hold reduce candidate, net -74c for the broad base opportunity."
        ),
    }


def summarize_refinement(payload: dict[str, Any]) -> dict[str, Any]:
    post = next(
        (lane for lane in payload.get("lanes") or [] if isinstance(lane, dict) and lane.get("lane") == "post_refinement_birth"),
        {},
    )
    variants = []
    for item in post.get("variants") or []:
        summary = item.get("summary") if isinstance(item.get("summary"), dict) else {}
        variants.append({
            "candidate": item.get("candidate"),
            "settled": summary.get("settled", summary.get("rows")),
            "suppressed_exits": summary.get("suppressed_exits"),
            "delta_vs_current_cents": summary.get("delta_vs_current_cents"),
            "blockers": item.get("blockers") or [],
        })
    return {
        "freeze_ts_utc": post.get("freeze_ts_utc"),
        "variants": variants,
        "read": "Every post-refinement variant has zero suppressions, so refinement cannot be judged until new probability-reduce opportunities arrive.",
    }


def denominator_context(payload: dict[str, Any]) -> dict[str, Any]:
    rows = {
        row.get("lane"): row
        for row in payload.get("rows") or []
        if isinstance(row, dict)
    }
    keys = ["reduce_depth_gate", "reduce_loss_control_refinement", "reduce_side_geometry"]
    return {key: rows.get(key, {}) for key in keys}


def build_report() -> dict[str, Any]:
    depth = summarize_depth(load_json(DEPTH_OPP_JSON))
    geometry = summarize_geometry(load_json(GEOMETRY_OPP_JSON))
    refinement = summarize_refinement(load_json(REFINEMENT_JSON))
    denominator = denominator_context(load_json(DENOM_JSON))
    report = {
        "generated_at_utc": utc_now_iso(),
        "sources": {
            "depth_opportunity": str(DEPTH_OPP_JSON),
            "geometry_opportunity": str(GEOMETRY_OPP_JSON),
            "refinement": str(REFINEMENT_JSON),
            "denominator_audit": str(DENOM_JSON),
        },
        "depth_gate": depth,
        "geometry": geometry,
        "refinement": refinement,
        "denominator_context": denominator,
    }
    report["interpretation"] = interpretation(report)
    return report


def interpretation(report: dict[str, Any]) -> list[str]:
    depth = report.get("depth_gate") or {}
    geometry = report.get("geometry") or {}
    refinement = report.get("refinement") or {}
    return [
        "Research-only no-fire audit; no live bot changes or orders.",
        "The reduce branch is not currently a leading repair because post-freeze probability-reduce opportunities are too sparse.",
        (
            f"Depth gate saw {depth.get('probability_reduce_rows')} probability-reduce row in "
            f"{depth.get('post_birth_rows')} post-birth rows; strict p_hold>=0.79 fires 0 times."
        ),
        (
            f"A looser depth rule would fire {depth.get('loose_would_suppress_rows')} time for "
            f"{depth.get('loose_would_suppress_delta_cents')}c, so widening would currently add loss-control harm."
        ),
        (
            f"Geometry saw {geometry.get('probability_reduce_rows')} probability-reduce rows and "
            f"{geometry.get('base_p_hold_candidates')} base p-hold candidates, but 0 geometry suppressions; "
            f"the rejected base opportunity was {geometry.get('geometry_rejected_base_delta_cents')}c."
        ),
        refinement.get("read"),
        "Actionable read: keep reduce watches running, but prioritize exit watches with active denominator and clean suppression evidence over widening reduce rules.",
    ]


def fmt(value: Any) -> str:
    if isinstance(value, float):
        return f"{value:.2f}"
    return str(value)


def write_md(report: dict[str, Any]) -> None:
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8")
    lines = [
        "# v28 Exit Reduce No-Fire Audit",
        "",
        "Research-only no-fire audit. No live bot changes or orders.",
        "",
        f"- Generated UTC: `{report.get('generated_at_utc')}`",
        "",
        "## Interpretation",
        "",
    ]
    lines.extend(f"- {note}" for note in report.get("interpretation") or [])
    depth = report.get("depth_gate") or {}
    geometry = report.get("geometry") or {}
    refinement = report.get("refinement") or {}
    lines.extend([
        "",
        "## Depth Gate",
        "",
        f"- Post-birth rows: `{depth.get('post_birth_rows')}`",
        f"- Probability-reduce rows: `{depth.get('probability_reduce_rows')}`",
        f"- Strict would-suppress rows: `{depth.get('strict_would_suppress_rows')}`",
        f"- Loose would-suppress rows/delta: `{depth.get('loose_would_suppress_rows')}` / `{fmt(depth.get('loose_would_suppress_delta_cents'))}c`",
        f"- Strict fail reasons: `{depth.get('strict_fail_reasons')}`",
        "",
        "## Geometry",
        "",
        f"- Post-freeze rows: `{geometry.get('post_freeze_rows')}`",
        f"- Probability-reduce rows: `{geometry.get('probability_reduce_rows')}`",
        f"- Base p-hold candidates: `{geometry.get('base_p_hold_candidates')}`",
        f"- Geometry would-suppress rows: `{geometry.get('geometry_would_suppress_rows')}`",
        f"- Rejected base opportunity delta: `{fmt(geometry.get('geometry_rejected_base_delta_cents'))}c`",
        f"- Reason counts: `{geometry.get('reason_counts')}`",
        "",
        "## Refinement",
        "",
        "| candidate | settled | suppressed | delta c | blockers |",
        "|---|---:|---:|---:|---|",
    ])
    for row in refinement.get("variants") or []:
        lines.append(
            f"| `{row.get('candidate')}` | {row.get('settled')} | {row.get('suppressed_exits')} | "
            f"{fmt(row.get('delta_vs_current_cents'))} | {', '.join(row.get('blockers') or []) or 'none'} |"
        )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    report = build_report()
    write_md(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
