"""Triage positive v28 candidates behind the control-risk blocker.

Research-only; no live bot changes or orders.

The consolidated tracker can make some rows look blocked only by the global
control risk stop. This report unions in the integrity scorecard before asking
whether any candidate would be locally clean if the global control-risk blocker
were cleared. That keeps source-quality and cushion problems visible.
"""
from __future__ import annotations

import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
TRACKER_JSON = OUT_DIR / "v28_candidate_pnl_tracker_latest.json"
INTEGRITY_JSON = OUT_DIR / "v28_candidate_integrity_scorecard_latest.json"
RISK_AUDIT_JSON = OUT_DIR / "v28_control_risk_stop_audit_latest.json"
OUT_JSON = OUT_DIR / "v28_control_risk_candidate_triage_latest.json"
OUT_MD = OUT_DIR / "v28_control_risk_candidate_triage_latest.md"

GLOBAL_BLOCKERS = {"control_risk_stop_active", "live_ready_false"}
MIN_SETTLED = 30
MIN_COVERAGE = 75.0
MAX_COVERAGE = 90.0
MAX_RECONSTRUCTED_SHARE = 0.35
MIN_FULL_LOSS_CUSHION = 3


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


def key(row: dict[str, Any]) -> str:
    return f"{row.get('gate')}::{row.get('policy')}"


def integrity_index(payload: dict[str, Any]) -> dict[str, dict[str, Any]]:
    rows = payload.get("candidates") or []
    return {key(row): row for row in rows if isinstance(row, dict)}


def merged_row(row: dict[str, Any], integrity_by_key: dict[str, dict[str, Any]]) -> dict[str, Any]:
    merged = dict(row)
    integrity = integrity_by_key.get(key(row))
    tracker_blockers = list(row.get("blockers") or [])
    merged["tracker_only_blockers"] = tracker_blockers
    blockers = list(tracker_blockers)
    if integrity:
        merged["integrity_pass"] = integrity.get("integrity_pass")
        merged["stress_warnings"] = list(integrity.get("stress_warnings") or [])
        if integrity.get("stress_full_loss_cushion") is not None:
            merged["full_loss_cushion_estimate"] = integrity.get("stress_full_loss_cushion")
        if "stress_reconstructed_share" in integrity:
            merged["stress_reconstructed_share"] = integrity.get("stress_reconstructed_share")
        for blocker in integrity.get("blockers") or []:
            if blocker not in blockers:
                blockers.append(blocker)
    merged["blockers"] = blockers
    return merged


def net_cents(row: dict[str, Any]) -> float:
    return as_float(row.get("net_cents_after_entry_fee")) or 0.0


def coverage_pct(row: dict[str, Any]) -> float | None:
    return as_float(row.get("coverage_pct"))


def reconstructed_share(row: dict[str, Any]) -> float | None:
    if "stress_reconstructed_share" in row:
        return as_float(row.get("stress_reconstructed_share"))
    share = as_float(row.get("simulated_share"))
    if share is not None:
        return share
    approved = as_float(row.get("approved_entry_count"))
    rejected = as_float(row.get("added_reject_count"))
    if approved is None or rejected is None:
        return None
    total = approved + rejected
    return rejected / total if total > 0 else None


def full_loss_cushion(row: dict[str, Any]) -> int | None:
    value = as_float(row.get("full_loss_cushion_estimate"))
    return int(value) if value is not None else None


def local_missing_gates(row: dict[str, Any]) -> list[str]:
    missing: list[str] = []
    settled = int(as_float(row.get("settled")) or 0)
    if settled < MIN_SETTLED:
        missing.append(f"settled+{MIN_SETTLED - settled}")
    if net_cents(row) <= 0:
        missing.append("positive_pnl")
    coverage = coverage_pct(row)
    if row.get("target_coverage") is False and coverage is not None:
        if coverage < MIN_COVERAGE:
            missing.append(f"coverage_low_by_{MIN_COVERAGE - coverage:.1f}pp")
        elif coverage > MAX_COVERAGE:
            missing.append(f"coverage_high_by_{coverage - MAX_COVERAGE:.1f}pp")
    share = reconstructed_share(row)
    if share is not None and share > MAX_RECONSTRUCTED_SHARE:
        missing.append(f"source_share_high_{share:.2f}")
    cushion = full_loss_cushion(row)
    if cushion is not None and cushion < MIN_FULL_LOSS_CUSHION:
        missing.append(f"cushion+{MIN_FULL_LOSS_CUSHION - cushion}")
    elif cushion is None:
        missing.append("cushion_unknown")
    for blocker in row.get("blockers") or []:
        if blocker in GLOBAL_BLOCKERS:
            continue
        if blocker not in missing:
            missing.append(blocker)
    return missing


def compact_row(row: dict[str, Any]) -> dict[str, Any]:
    tracker_only = [
        blocker for blocker in row.get("tracker_only_blockers") or []
        if blocker not in GLOBAL_BLOCKERS
    ]
    merged_missing = local_missing_gates(row)
    return {
        "gate": row.get("gate"),
        "policy": row.get("policy"),
        "entries": row.get("entries"),
        "settled": row.get("settled"),
        "wins": row.get("wins"),
        "losses": row.get("losses"),
        "coverage_pct": coverage_pct(row),
        "net_cents": net_cents(row),
        "target_coverage": bool(row.get("target_coverage")),
        "strict_forward": bool(row.get("strict_forward")),
        "tracker_only_non_global_blockers": tracker_only,
        "merged_non_global_missing": merged_missing,
        "reconstructed_share": reconstructed_share(row),
        "full_loss_cushion": full_loss_cushion(row),
        "integrity_pass": row.get("integrity_pass"),
    }


def build_report() -> dict[str, Any]:
    tracker = load_json(TRACKER_JSON)
    integrity = load_json(INTEGRITY_JSON)
    risk = load_json(RISK_AUDIT_JSON)
    integrity_by_key = integrity_index(integrity)
    rows = [
        merged_row(row, integrity_by_key)
        for row in tracker.get("rows") or []
        if isinstance(row, dict)
    ]
    positive = [row for row in rows if net_cents(row) > 0]
    positive_target = [row for row in positive if row.get("target_coverage")]
    positive_strict = [row for row in positive if row.get("strict_forward")]
    positive_target_strict = [row for row in positive_target if row.get("strict_forward")]

    tracker_control_only = [
        row for row in positive
        if not [
            blocker for blocker in row.get("tracker_only_blockers") or []
            if blocker not in GLOBAL_BLOCKERS
        ]
    ]
    merged_control_only = [
        row for row in positive
        if not local_missing_gates(row)
    ]
    apparent_target_control_only = [row for row in tracker_control_only if row.get("target_coverage")]
    actual_target_control_only = [row for row in merged_control_only if row.get("target_coverage")]

    blocker_counts = Counter()
    target_blocker_counts = Counter()
    strict_blocker_counts = Counter()
    for row in positive:
        for blocker in local_missing_gates(row):
            blocker_counts[blocker] += 1
            if row.get("target_coverage"):
                target_blocker_counts[blocker] += 1
            if row.get("strict_forward"):
                strict_blocker_counts[blocker] += 1

    sort_key = lambda row: net_cents(row)
    return {
        "generated_at_utc": utc_now_iso(),
        "inputs": {
            "tracker_json": str(TRACKER_JSON),
            "integrity_json": str(INTEGRITY_JSON),
            "risk_audit_json": str(RISK_AUDIT_JSON),
        },
        "risk_summary": (risk.get("summary") or {}),
        "summary": {
            "tracker_rows": len(rows),
            "positive_rows": len(positive),
            "positive_target_rows": len(positive_target),
            "positive_strict_rows": len(positive_strict),
            "positive_target_strict_rows": len(positive_target_strict),
            "tracker_apparent_control_only_positive": len(tracker_control_only),
            "tracker_apparent_control_only_target": len(apparent_target_control_only),
            "integrity_merged_control_only_positive": len(merged_control_only),
            "integrity_merged_control_only_target": len(actual_target_control_only),
            "integrity_merged_control_only_target_strict": sum(
                1 for row in actual_target_control_only if row.get("strict_forward")
            ),
        },
        "top_apparent_tracker_control_only": [
            compact_row(row) for row in sorted(tracker_control_only, key=sort_key, reverse=True)[:15]
        ],
        "top_integrity_merged_control_only": [
            compact_row(row) for row in sorted(merged_control_only, key=sort_key, reverse=True)[:15]
        ],
        "top_positive_target_after_integrity": [
            compact_row(row) for row in sorted(positive_target, key=sort_key, reverse=True)[:20]
        ],
        "top_positive_strict_after_integrity": [
            compact_row(row) for row in sorted(positive_strict, key=sort_key, reverse=True)[:20]
        ],
        "blocker_counts_positive": dict(blocker_counts.most_common(30)),
        "blocker_counts_positive_target": dict(target_blocker_counts.most_common(30)),
        "blocker_counts_positive_strict": dict(strict_blocker_counts.most_common(30)),
        "interpretation": [],
    }


def cents(value: Any) -> str:
    number = as_float(value)
    return "n/a" if number is None else f"{number:.0f}c"


def pct(value: Any) -> str:
    number = as_float(value)
    return "n/a" if number is None else f"{number:.2f}%"


def share(value: Any) -> str:
    number = as_float(value)
    return "n/a" if number is None else f"{number * 100.0:.1f}%"


def wl(row: dict[str, Any]) -> str:
    if row.get("wins") is None or row.get("losses") is None:
        return "n/a"
    return f"{row.get('wins')}/{row.get('losses')}"


def write_table(lines: list[str], rows: list[dict[str, Any]]) -> None:
    lines.extend([
        "| gate | policy | settled | W/L | coverage | net | target | strict | recon | cushion | merged missing |",
        "|---|---|---:|---:|---:|---:|---|---|---:|---:|---|",
    ])
    for row in rows:
        missing = ", ".join(row.get("merged_non_global_missing") or [])
        if not missing:
            missing = "none_after_global"
        lines.append(
            f"| `{row.get('gate')}` | `{row.get('policy')}` | {row.get('settled')} | {wl(row)} | "
            f"{pct(row.get('coverage_pct'))} | {cents(row.get('net_cents'))} | {row.get('target_coverage')} | "
            f"{row.get('strict_forward')} | {share(row.get('reconstructed_share'))} | "
            f"{row.get('full_loss_cushion') if row.get('full_loss_cushion') is not None else 'n/a'} | {missing} |"
        )


def write_report(report: dict[str, Any]) -> None:
    summary = report["summary"]
    risk_summary = report.get("risk_summary") or {}
    interpretation = [
        "This is a promotion-safety report only; it does not weaken the live-readiness risk stop.",
        (
            "Tracker-only blockers can understate candidate risk. After integrity blockers are merged, "
            f"{summary['integrity_merged_control_only_target']} target-coverage positive rows are blocked only by "
            "the global control-risk/live-ready status."
        ),
        (
            f"Control risk remains active by {risk_summary.get('risk_stop_reason')}; the latest risk audit shows "
            f"{risk_summary.get('losing_trades')} losing scored trades, "
            f"{risk_summary.get('max_drawdown_pct')}% max drawdown, and "
            f"{risk_summary.get('full_loss_events')} full-loss events."
        ),
    ]
    report["interpretation"] = interpretation
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    lines = [
        "# v28 Control-Risk Candidate Triage",
        "",
        "Research-only; no live bot changes or orders.",
        "",
        f"- Generated UTC: `{report.get('generated_at_utc')}`",
        f"- Positive rows: `{summary['positive_rows']}` / `{summary['tracker_rows']}`",
        f"- Positive target-coverage rows: `{summary['positive_target_rows']}`",
        f"- Positive strict rows: `{summary['positive_strict_rows']}`",
        f"- Tracker-apparent control-only target rows: `{summary['tracker_apparent_control_only_target']}`",
        f"- Integrity-merged control-only target rows: `{summary['integrity_merged_control_only_target']}`",
        f"- Integrity-merged control-only strict target rows: `{summary['integrity_merged_control_only_target_strict']}`",
        "",
        "## Interpretation",
        "",
    ]
    lines.extend(f"- {note}" for note in interpretation)
    lines.extend(["", "## Tracker-Apparent Control-Only Positive", ""])
    write_table(lines, report.get("top_apparent_tracker_control_only") or [])
    lines.extend(["", "## Integrity-Merged Control-Only Positive", ""])
    write_table(lines, report.get("top_integrity_merged_control_only") or [])
    lines.extend(["", "## Top Positive Target Rows After Integrity", ""])
    write_table(lines, report.get("top_positive_target_after_integrity") or [])
    lines.extend(["", "## Top Positive Strict Rows After Integrity", ""])
    write_table(lines, report.get("top_positive_strict_after_integrity") or [])
    lines.extend(["", "## Top Missing Gates", ""])
    lines.append("| scope | missing gate | rows |")
    lines.append("|---|---|---:|")
    for scope, counts in [
        ("positive", report.get("blocker_counts_positive") or {}),
        ("positive_target", report.get("blocker_counts_positive_target") or {}),
        ("positive_strict", report.get("blocker_counts_positive_strict") or {}),
    ]:
        for blocker, count in list(counts.items())[:12]:
            lines.append(f"| `{scope}` | `{blocker}` | {count} |")
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    report = build_report()
    write_report(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
