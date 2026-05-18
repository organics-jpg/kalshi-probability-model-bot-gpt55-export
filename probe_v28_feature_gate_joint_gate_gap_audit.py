"""Joint promotion-gate gap audit for the boundary-clock feature-gate branch.

Research-only; no live bot changes, no process control, no orders.

This uses the current feature-gate artifact directly so the coverage/source/
cushion gaps are not inherited from older moving side reports.
"""
from __future__ import annotations

import json
import math
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"

FEATURE_GATE_JSON = OUT_DIR / "v28_boundary_clock_feature_gate_candidate_latest.json"
CANDIDATE_VS_LIVE_JSON = OUT_DIR / "v28_candidate_vs_live_full_table_latest.json"
FORWARD_COLLECTION_JSON = OUT_DIR / "v28_forward_collection_blocker_audit_latest.json"

OUT_JSON = OUT_DIR / "v28_feature_gate_joint_gate_gap_audit_latest.json"
OUT_MD = OUT_DIR / "v28_feature_gate_joint_gate_gap_audit_latest.md"

TARGET_COVERAGE = 0.75
MAX_SOURCE_SHARE = 0.35
MIN_SETTLED = 30
MIN_FULL_LOSS_CUSHION = 3


def load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
    return payload if isinstance(payload, dict) else {}


def fnum(value: Any, default: float = 0.0) -> float:
    try:
        if value is None or value == "":
            return default
        return float(value)
    except (TypeError, ValueError):
        return default


def full_loss_cushion(net_cents: Any) -> int:
    return int(max(0.0, fnum(net_cents)) // 100.0)


def source_counts(rows: list[dict[str, Any]]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for row in rows:
        source = str(row.get("source") or "unknown")
        counts[source] = counts.get(source, 0) + 1
    return counts


def source_share_from_counts(counts: dict[str, int]) -> float | None:
    total = sum(counts.values())
    if not total:
        return None
    risky = total - int(counts.get("approved_entry", 0))
    return risky / total


def clean_rows_needed_for_source(entries: int, risky_rows: int) -> int:
    if entries <= 0:
        return 0
    needed = 0
    while risky_rows / max(1, entries + needed) > MAX_SOURCE_SHARE:
        needed += 1
    return needed


def drop_risky_losses_summary(rows: list[dict[str, Any]], denominator: int) -> dict[str, Any]:
    selected = list(rows)
    risky_losses = sorted(
        [
            row for row in selected
            if row.get("source") != "approved_entry" and fnum(row.get("net_cents")) < 0
        ],
        key=lambda row: fnum(row.get("net_cents")),
    )
    best = None
    for drop_count in range(len(risky_losses) + 1):
        dropped = risky_losses[:drop_count]
        dropped_ids = {(row.get("market"), row.get("side")) for row in dropped}
        remaining = [
            row for row in selected
            if (row.get("market"), row.get("side")) not in dropped_ids
        ]
        counts = source_counts(remaining)
        entries = len(remaining)
        coverage = (entries / denominator * 100.0) if denominator else None
        net = sum(fnum(row.get("net_cents")) for row in remaining)
        share = source_share_from_counts(counts)
        passes_source = share is not None and share <= MAX_SOURCE_SHARE
        passes_coverage = coverage is not None and coverage >= TARGET_COVERAGE * 100.0
        row = {
            "drop_count": drop_count,
            "entries": entries,
            "coverage_pct": coverage,
            "net_cents": net,
            "reconstructed_share": share,
            "source_counts": counts,
            "passes_source": passes_source,
            "passes_coverage": passes_coverage,
            "dropped_rows": [
                {
                    "market": item.get("market"),
                    "side": item.get("side"),
                    "source": item.get("source"),
                    "net_cents": item.get("net_cents"),
                    "raw_edge": item.get("raw_edge"),
                    "recross_hazard_score": item.get("recross_hazard_score"),
                    "abs_d_sigma": item.get("abs_d_sigma"),
                    "ask_prob": item.get("ask_prob"),
                }
                for item in dropped
            ],
        }
        if passes_source and best is None:
            best = row
        if passes_source and passes_coverage:
            return {**row, "read": "source_and_coverage_pass_after_dropping_risky_losses"}
    if best:
        return {**best, "read": "source_passes_only_by_breaking_coverage"}
    return {"read": "no_source_passing_drop_scenario", "drop_candidates": len(risky_losses)}


def summarize_variant(
    lane_name: str,
    denominator: int,
    variant: dict[str, Any],
    live_net_cents: float,
    live_collection_healthy: bool,
) -> dict[str, Any]:
    summary = variant.get("candidate_summary") or {}
    rows = [row for row in (variant.get("rows") or []) if isinstance(row, dict)]
    counts = source_counts(rows)
    entries = int(summary.get("entries") or len(rows))
    settled = int(summary.get("settled") or 0)
    net = fnum(summary.get("net_cents"))
    coverage = fnum(summary.get("coverage_pct"))
    risky_rows = entries - int(counts.get("approved_entry", 0))
    required_entries = math.ceil(denominator * TARGET_COVERAGE) if denominator else 0
    entries_needed = max(0, required_entries - entries)
    clean_needed_source = clean_rows_needed_for_source(entries, risky_rows)
    settled_needed = max(0, MIN_SETTLED - settled)
    cents_needed_cushion = max(0.0, (MIN_FULL_LOSS_CUSHION * 100.0) - net)
    cents_needed_live = max(0.0, live_net_cents - net)
    blockers = []
    if settled < MIN_SETTLED:
        blockers.append("settled_lt_30")
    if entries_needed:
        blockers.append("coverage_too_low")
    if (variant.get("reconstructed_share") is not None) and fnum(variant.get("reconstructed_share")) > MAX_SOURCE_SHARE:
        blockers.append("reconstructed_share_gt_35pct")
    if full_loss_cushion(net) < MIN_FULL_LOSS_CUSHION:
        blockers.append("full_loss_cushion_lt_3")
    if cents_needed_live > 0:
        blockers.append("does_not_beat_live_snapshot")
    if not live_collection_healthy:
        blockers.append("fresh_v28_live_collection_unhealthy")
    clean_rows_needed_joint = max(entries_needed, clean_needed_source)
    avg_cents_needed_per_clean_row_for_live = (
        cents_needed_live / clean_rows_needed_joint if clean_rows_needed_joint else cents_needed_live
    )
    avg_cents_needed_per_clean_row_for_cushion = (
        cents_needed_cushion / clean_rows_needed_joint if clean_rows_needed_joint else cents_needed_cushion
    )
    return {
        "lane": lane_name,
        "candidate": variant.get("candidate"),
        "future_denominator": denominator,
        "entries": entries,
        "settled": settled,
        "coverage_pct": coverage,
        "net_cents": net,
        "wins": summary.get("wins"),
        "losses": summary.get("losses"),
        "source_counts": counts,
        "reconstructed_share": variant.get("reconstructed_share"),
        "full_loss_cushion": full_loss_cushion(net),
        "required_entries_for_75pct": required_entries,
        "entries_needed_for_75pct": entries_needed,
        "settled_needed_for_30": settled_needed,
        "clean_rows_needed_for_source_gate": clean_needed_source,
        "clean_rows_needed_for_coverage_and_source": clean_rows_needed_joint,
        "cents_needed_for_cushion3": cents_needed_cushion,
        "live_snapshot_net_cents": live_net_cents,
        "cents_needed_to_match_live_snapshot": cents_needed_live,
        "avg_cents_needed_per_clean_row_for_live_snapshot": avg_cents_needed_per_clean_row_for_live,
        "avg_cents_needed_per_clean_row_for_cushion": avg_cents_needed_per_clean_row_for_cushion,
        "drop_risky_losses": drop_risky_losses_summary(rows, denominator),
        "original_blockers": variant.get("blockers") or [],
        "joint_blockers": blockers,
    }


def build_report() -> dict[str, Any]:
    feature_gate = load_json(FEATURE_GATE_JSON)
    live = load_json(CANDIDATE_VS_LIVE_JSON)
    forward = load_json(FORWARD_COLLECTION_JSON)
    live_net = fnum(live.get("live_net_cents"))
    live_blockers = forward.get("blockers") or []
    live_collection_healthy = (
        "live_watchdog_restart_failed" not in live_blockers
        and "live_lock_not_v28" not in live_blockers
    )
    rows = []
    for lane in feature_gate.get("lanes") or []:
        lane_name = lane.get("lane")
        if lane_name not in {"post_feature_freeze_entry", "post_feature_freeze_bridge"}:
            continue
        denominator = int(lane.get("future_denominator") or 0)
        for variant in lane.get("variants") or []:
            rows.append(summarize_variant(lane_name, denominator, variant, live_net, live_collection_healthy))
    rows.sort(
        key=lambda row: (
            len(row.get("joint_blockers") or []),
            fnum(row.get("cents_needed_to_match_live_snapshot")),
            -fnum(row.get("net_cents")),
        )
    )
    best_by_lane = {}
    for row in rows:
        best_by_lane.setdefault(row["lane"], row)
    blockers = ["research_only", "not_promotion_evidence"]
    if not live_collection_healthy:
        blockers.append("fresh_v28_live_collection_unhealthy")
    if not any(not row.get("joint_blockers") for row in rows):
        blockers.append("no_feature_gate_variant_clears_joint_gates")
    return {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "feature_gate_generated_at_utc": feature_gate.get("generated_at_utc"),
        "feature_gate_freeze_ts_utc": (feature_gate.get("state") or {}).get("freeze_ts_utc"),
        "candidate_vs_live_generated_at_utc": live.get("generated_at_utc"),
        "live_snapshot_net_cents": live_net,
        "live_collection_healthy": live_collection_healthy,
        "live_collection_blockers": live_blockers,
        "rows": rows,
        "best_by_lane": best_by_lane,
        "blockers": blockers,
        "interpretation": [
            "The current feature-gate branch is not one gate away from promotion; coverage, source share, cushion, and live-baseline gaps interact.",
            "Raw03-style broad rows buy coverage by adding risky/reconstructed rows and still lack cushion; dropping risky losses fixes source only by breaking coverage.",
            "Raw05-style rows are cleaner, but they need clean forward rows for coverage and still trail the live snapshot by far more than a normal small-row repair.",
            "Because v28 live collection is unhealthy, live-baseline deltas are log-snapshot context until the v28 live state is explicitly healthy again.",
        ],
    }


def money(value: Any) -> str:
    cents = fnum(value)
    return f"{cents:.0f}c (${cents / 100.0:.2f})"


def write_outputs(report: dict[str, Any]) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8")
    lines = [
        "# v28 Feature-Gate Joint Gate Gap Audit",
        "",
        "Research-only. No live bot logic changes, no process control, no orders.",
        "",
        f"- Generated UTC: `{report.get('generated_at_utc')}`",
        f"- Feature-gate generated UTC: `{report.get('feature_gate_generated_at_utc')}`",
        f"- Feature-gate freeze UTC: `{report.get('feature_gate_freeze_ts_utc')}`",
        f"- Candidate-vs-live generated UTC: `{report.get('candidate_vs_live_generated_at_utc')}`",
        f"- Live snapshot net: `{money(report.get('live_snapshot_net_cents'))}`",
        f"- Live collection healthy: `{report.get('live_collection_healthy')}`",
        f"- Blockers: `{', '.join(report.get('blockers') or [])}`",
        "",
        "## Read",
        "",
    ]
    lines.extend(f"- {item}" for item in report.get("interpretation") or [])
    lines.extend([
        "",
        "## Variant Gaps",
        "",
        "| lane | candidate | entries/settled | cov | net | source | cushion | clean rows needed cov/source | cents needed cushion/live | joint blockers |",
        "|---|---|---:|---:|---:|---:|---:|---:|---:|---|",
    ])
    for row in report.get("rows") or []:
        lines.append(
            f"| `{row.get('lane')}` | `{row.get('candidate')}` | "
            f"{row.get('entries')}/{row.get('settled')} | {fnum(row.get('coverage_pct')):.2f}% | "
            f"{money(row.get('net_cents'))} | {fnum(row.get('reconstructed_share')):.3f} | "
            f"{row.get('full_loss_cushion')} | "
            f"{row.get('entries_needed_for_75pct')}/{row.get('clean_rows_needed_for_source_gate')} | "
            f"{money(row.get('cents_needed_for_cushion3'))}/{money(row.get('cents_needed_to_match_live_snapshot'))} | "
            f"`{', '.join(row.get('joint_blockers') or [])}` |"
        )
    lines.extend([
        "",
        "## Drop Risky Losses Check",
        "",
        "| lane | candidate | read | drop count | remaining entries | coverage | source | net |",
        "|---|---|---|---:|---:|---:|---:|---:|",
    ])
    for row in report.get("rows") or []:
        drop = row.get("drop_risky_losses") or {}
        lines.append(
            f"| `{row.get('lane')}` | `{row.get('candidate')}` | `{drop.get('read')}` | "
            f"{drop.get('drop_count')} | {drop.get('entries')} | "
            f"{fnum(drop.get('coverage_pct')):.2f}% | {fnum(drop.get('reconstructed_share')):.3f} | "
            f"{money(drop.get('net_cents'))} |"
        )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    report = build_report()
    write_outputs(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
