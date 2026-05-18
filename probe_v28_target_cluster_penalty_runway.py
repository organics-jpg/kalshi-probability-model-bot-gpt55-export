"""Runway audit for the frozen target-coverage cluster-penalty watch.

Research-only; no live bot changes or orders.

The cluster-penalty watch is a broad-entry repair candidate. This report
quantifies whether it is blocked by sample size, source dilution, coverage, or
full-loss cushion instead of treating a small positive post-birth row as
promotion evidence.
"""
from __future__ import annotations

import json
import math
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
SOURCE_JSON = OUT_DIR / "v28_target_coverage_cluster_penalty_watch_latest.json"
OUT_JSON = OUT_DIR / "v28_target_cluster_penalty_runway_latest.json"
OUT_MD = OUT_DIR / "v28_target_cluster_penalty_runway_latest.md"

COVERAGE_FLOOR = 75.0
MIN_SETTLED = 30
MAX_RECONSTRUCTED_SHARE = 0.35
MIN_FULL_LOSS_CUSHION_CENTS = 300.0


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


def best_variant(source: dict[str, Any], lane_name: str) -> dict[str, Any]:
    lanes = source.get("lanes") if isinstance(source.get("lanes"), list) else []
    lane = next((row for row in lanes if row.get("lane") == lane_name), {})
    variants = lane.get("variants") if isinstance(lane.get("variants"), list) else []
    best = variants[0] if variants else {}
    return {"lane": lane, "variant": best}


def required_entries_for_coverage(denominator: int) -> int:
    if denominator <= 0:
        return 0
    return math.ceil((COVERAGE_FLOOR / 100.0) * denominator)


def source_runway(source_counts: dict[str, Any]) -> dict[str, Any]:
    approved = int(as_float(source_counts.get("approved_entry")) or 0)
    total = sum(int(as_float(value) or 0) for value in source_counts.values())
    reconstructed = max(0, total - approved)
    share = None if total <= 0 else reconstructed / total
    clean_needed = 0
    if total <= 0:
        clean_needed = 0
    elif share is not None and share > MAX_RECONSTRUCTED_SHARE:
        clean_needed = math.ceil((reconstructed / MAX_RECONSTRUCTED_SHARE) - total)
    return {
        "approved_rows": approved,
        "selected_rows": total,
        "reconstructed_or_rejected_rows": reconstructed,
        "reconstructed_share": share,
        "future_clean_approved_rows_needed_for_source_gate": max(0, clean_needed),
    }


def lane_runway(label: str, lane: dict[str, Any], variant: dict[str, Any]) -> dict[str, Any]:
    summary = variant.get("candidate_summary") or {}
    denominator = int(as_float(lane.get("future_denominator")) or 0)
    entries = int(as_float(summary.get("entries")) or 0)
    settled = int(as_float(summary.get("settled")) or 0)
    net = float(as_float(summary.get("net_cents")) or 0.0)
    required_entries = required_entries_for_coverage(denominator)
    source = source_runway(variant.get("source_counts") or {})
    blockers = list(variant.get("blockers") or [])
    return {
        "lane": label,
        "candidate": variant.get("candidate"),
        "freeze_ts_utc": lane.get("freeze_ts_utc"),
        "future_denominator": denominator,
        "entries": entries,
        "settled": settled,
        "coverage_pct": summary.get("coverage_pct"),
        "net_cents": net,
        "delta_vs_target_cents": variant.get("delta_vs_target_cents"),
        "wins": summary.get("wins"),
        "losses": summary.get("losses"),
        "required_entries_for_75pct_coverage": required_entries,
        "future_entries_needed_for_coverage": max(0, required_entries - entries),
        "future_settled_rows_needed_for_sample": max(0, MIN_SETTLED - settled),
        "future_net_cents_needed_for_cushion3": max(0.0, MIN_FULL_LOSS_CUSHION_CENTS - net),
        "source_runway": source,
        "blockers": blockers,
        "ready_for_promotion_review": not blockers,
    }


def build_report() -> dict[str, Any]:
    source = load_json(SOURCE_JSON)
    diagnostic = best_variant(source, "diagnostic_target_window")
    post = best_variant(source, "post_cluster_penalty_birth")
    diag_runway = lane_runway("diagnostic_target_window", diagnostic["lane"], diagnostic["variant"])
    post_runway = lane_runway("post_cluster_penalty_birth", post["lane"], post["variant"])
    report = {
        "generated_at_utc": utc_now_iso(),
        "source_artifact": str(SOURCE_JSON),
        "freeze_ts_utc": (source.get("state") or {}).get("freeze_ts_utc"),
        "diagnostic_runway": diag_runway,
        "post_birth_runway": post_runway,
    }
    report["interpretation"] = interpretation(report)
    return report


def interpretation(report: dict[str, Any]) -> list[str]:
    post = report.get("post_birth_runway") or {}
    post_source = post.get("source_runway") or {}
    diag = report.get("diagnostic_runway") or {}
    diag_source = diag.get("source_runway") or {}
    return [
        "This is a runway/source-quality audit only; it does not change the frozen cluster-penalty watch.",
        (
            f"Post-birth {post.get('candidate')} has {post.get('settled')} settled rows, "
            f"{post.get('coverage_pct')}% coverage, {post.get('net_cents')}c net, and "
            f"{post_source.get('reconstructed_share')} reconstructed share."
        ),
        (
            f"Post-birth still needs {post.get('future_settled_rows_needed_for_sample')} settled rows, "
            f"{post_source.get('future_clean_approved_rows_needed_for_source_gate')} clean approved selected rows for source, "
            f"and {post.get('future_net_cents_needed_for_cushion3')}c for a three-full-loss cushion."
        ),
        (
            f"Diagnostic best remains source-blocked too: {diag_source.get('reconstructed_share')} reconstructed share "
            f"and {diag_source.get('future_clean_approved_rows_needed_for_source_gate')} clean rows needed for source."
        ),
    ]


def fmt(value: Any) -> str:
    if value is None:
        return "None"
    if isinstance(value, float):
        return f"{value:.6f}"
    return str(value)


def write_md(report: dict[str, Any]) -> None:
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8")
    lines = [
        "# v28 Target Cluster-Penalty Runway",
        "",
        "Research-only; no live bot changes or orders.",
        "",
        f"- Generated UTC: `{report.get('generated_at_utc')}`",
        f"- Freeze UTC: `{report.get('freeze_ts_utc')}`",
        "",
        "## Interpretation",
        "",
    ]
    lines.extend(f"- {note}" for note in report.get("interpretation") or [])
    lines.extend([
        "",
        "## Runway",
        "",
        "| lane | candidate | settled | coverage | net c | recon share | rows needed | clean rows needed | cushion c needed | blockers |",
        "|---|---|---:|---:|---:|---:|---:|---:|---:|---|",
    ])
    for row in (report.get("post_birth_runway"), report.get("diagnostic_runway")):
        row = row or {}
        source = row.get("source_runway") or {}
        lines.append(
            f"| `{row.get('lane')}` | `{row.get('candidate')}` | {row.get('settled')} | "
            f"{fmt(row.get('coverage_pct'))} | {fmt(row.get('net_cents'))} | "
            f"{fmt(source.get('reconstructed_share'))} | {row.get('future_settled_rows_needed_for_sample')} | "
            f"{source.get('future_clean_approved_rows_needed_for_source_gate')} | "
            f"{fmt(row.get('future_net_cents_needed_for_cushion3'))} | "
            f"{', '.join(row.get('blockers') or []) or 'none'} |"
        )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    report = build_report()
    write_md(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
