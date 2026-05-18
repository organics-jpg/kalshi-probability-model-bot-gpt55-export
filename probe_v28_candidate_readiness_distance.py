"""Compact readiness-distance digest for v28 candidates.

Research-only; no live bot changes or orders.

The normal tracker is intentionally broad. This report answers a narrower
question: which candidates are closest to promotion gates, and what exact gate
is still missing? It is a reporting aid, not a readiness override.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
TRACKER_JSON = OUT_DIR / "v28_candidate_pnl_tracker_latest.json"
INTEGRITY_JSON = OUT_DIR / "v28_candidate_integrity_scorecard_latest.json"
LIVE_READY_JSON = OUT_DIR / "v28_live_trade_readiness_latest.json"
OUT_JSON = OUT_DIR / "v28_candidate_readiness_distance_latest.json"
OUT_MD = OUT_DIR / "v28_candidate_readiness_distance_latest.md"

MIN_SETTLED = 30
MIN_COVERAGE = 75.0
MAX_COVERAGE = 90.0
MAX_SIMULATED_SHARE = 0.35
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


def as_int(value: Any) -> int | None:
    number = as_float(value)
    if number is None:
        return None
    return int(number)


def key(row: dict[str, Any]) -> str:
    return f"{row.get('gate')}::{row.get('policy')}"


def integrity_index(payload: dict[str, Any]) -> dict[str, dict[str, Any]]:
    rows = payload.get("candidates") or []
    return {key(row): row for row in rows if isinstance(row, dict)}


def with_integrity(row: dict[str, Any], index: dict[str, dict[str, Any]]) -> dict[str, Any]:
    integrity = index.get(key(row))
    if not integrity:
        return row
    merged = dict(row)
    blockers = list(row.get("blockers") or [])
    for blocker in integrity.get("blockers") or []:
        if blocker not in blockers:
            blockers.append(blocker)
    merged["blockers"] = blockers
    merged["integrity_pass"] = integrity.get("integrity_pass")
    merged["stress_warnings"] = list(integrity.get("stress_warnings") or [])
    if integrity.get("stress_full_loss_cushion") is not None:
        merged["full_loss_cushion_estimate"] = integrity.get("stress_full_loss_cushion")
    if "stress_reconstructed_share" in integrity:
        merged["stress_reconstructed_share"] = integrity.get("stress_reconstructed_share")
    if integrity.get("live_ready") is False:
        merged["live_ready"] = False
    return merged


def source_share(row: dict[str, Any]) -> float | None:
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
    if total <= 0:
        return None
    return rejected / total


def is_pure_exit_policy(row: dict[str, Any]) -> bool:
    gate = str(row.get("gate") or "")
    return gate.startswith("exit_") or gate == "dual_exit_book_gap_else_reduce"


def clean_rows_needed_for_source(rejected: int, selected: int) -> int | None:
    if selected <= 0:
        return None
    for rows in range(0, 500):
        if rejected / (selected + rows) <= MAX_SIMULATED_SHARE:
            return rows
    return 500


def classify(row: dict[str, Any]) -> dict[str, Any]:
    pure_exit = is_pure_exit_policy(row)
    settled = as_int(row.get("settled")) or 0
    entries = as_int(row.get("entries")) or settled
    net = as_float(row.get("net_cents_after_entry_fee"))
    coverage = as_float(row.get("coverage_pct"))
    share = source_share(row)
    cushion = as_int(row.get("full_loss_cushion_estimate"))
    blockers = list(row.get("blockers") or [])
    approved = as_int(row.get("approved_entry_count"))
    rejected = as_int(row.get("added_reject_count"))
    suppressed_exits = as_int(row.get("suppressed_exits"))
    loss_control_cost = as_float(row.get("loss_control_cost_cents"))
    stress_warnings = list(row.get("stress_warnings") or [])
    post_stack_sample_blocked = "post_stack_joined_exit_rows_lt_30" in blockers
    post_stack_cushion_blocked = "post_stack_weighted_exit_full_loss_cushion_lt_3" in blockers

    sample_gap = max(0, MIN_SETTLED - settled)
    coverage_gap = None
    coverage_status = "not_applicable" if pure_exit else "unknown"
    if not pure_exit and coverage is not None:
        if coverage < MIN_COVERAGE:
            coverage_gap = MIN_COVERAGE - coverage
            coverage_status = "low"
        elif coverage > MAX_COVERAGE:
            coverage_gap = coverage - MAX_COVERAGE
            coverage_status = "high"
        else:
            coverage_gap = 0.0
            coverage_status = "pass"

    source_status = "not_applicable" if pure_exit else "unknown"
    source_clean_rows_needed = None
    if not pure_exit and share is not None:
        source_status = "pass" if share <= MAX_SIMULATED_SHARE else "high_reconstructed"
        if share > MAX_SIMULATED_SHARE and rejected is not None:
            source_clean_rows_needed = as_int(row.get("source_clean_rows_needed"))
            if source_clean_rows_needed is None:
                source_clean_rows_needed = clean_rows_needed_for_source(rejected, entries)

    cushion_gap = None
    if cushion is not None:
        cushion_gap = max(0, MIN_FULL_LOSS_CUSHION - cushion)

    missing = []
    if sample_gap:
        missing.append(f"sample+{sample_gap}")
    if net is None or net <= 0:
        missing.append("positive_pnl")
    if pure_exit:
        if suppressed_exits is not None and suppressed_exits < MIN_SETTLED:
            missing.append(f"suppressed_decisions+{MIN_SETTLED - suppressed_exits}")
        if loss_control_cost is not None and loss_control_cost < 0:
            missing.append("loss_control_cost_negative")
    elif coverage_status == "low":
        missing.append(f"coverage_low_by_{coverage_gap:.1f}pp")
    elif coverage_status == "high":
        missing.append(f"coverage_high_by_{coverage_gap:.1f}pp")
    elif coverage_status == "unknown":
        missing.append("coverage_unknown")
    if source_status == "high_reconstructed":
        missing.append(f"source_clean_rows+{source_clean_rows_needed}")
    elif source_status == "unknown":
        if "post_stack_source_sample_empty" in stress_warnings:
            missing.append("post_stack_source_sample_empty")
        else:
            missing.append("source_unknown")
    if post_stack_sample_blocked:
        missing.append("post_stack_joined_rows+30")
    if "post_stack_weighted_exit_net_not_positive" in blockers:
        missing.append("post_stack_positive_pnl")
    if post_stack_cushion_blocked:
        missing.append("post_stack_cushion+300c")
    if cushion_gap is not None and cushion_gap:
        missing.append(f"cushion+{cushion_gap}")
    elif cushion_gap is None:
        missing.append("cushion_unknown")
    if not row.get("live_ready"):
        missing.append("live_ready_false")

    score = 0
    score += min(sample_gap, 30)
    score += 20 if net is None or net <= 0 else 0
    if pure_exit:
        if suppressed_exits is not None:
            score += min(max(0, MIN_SETTLED - suppressed_exits), 30)
        if loss_control_cost is not None and loss_control_cost < 0:
            score += 10
    else:
        score += 0 if coverage_status == "pass" else 8
        score += 0 if source_status == "pass" else 8
    score += 0 if cushion_gap == 0 else 6
    if post_stack_sample_blocked:
        score += 30
    if post_stack_cushion_blocked:
        score += 12
    score += min(len(blockers), 8)
    if net is not None and net > 0:
        score -= min(net / 100.0, 8.0)

    return {
        "gate": row.get("gate"),
        "policy": row.get("policy"),
        "entries": entries,
        "settled": settled,
        "wins": row.get("wins"),
        "losses": row.get("losses"),
        "coverage_pct": coverage,
        "net_cents": net,
        "simulated_share": share,
        "approved_entry_count": approved,
        "rejected_actionable_count": rejected,
        "full_loss_cushion_estimate": cushion,
        "suppressed_exits": suppressed_exits,
        "loss_control_cost_cents": loss_control_cost,
        "candidate_type": "exit_policy" if pure_exit else "entry_or_fv",
        "live_ready": bool(row.get("live_ready")),
        "blockers": blockers,
        "missing_gates": missing,
        "sample_gap": sample_gap,
        "coverage_status": coverage_status,
        "source_status": source_status,
        "source_clean_rows_needed": source_clean_rows_needed,
        "cushion_gap": cushion_gap,
        "stress_warnings": stress_warnings,
        "integrity_pass": row.get("integrity_pass"),
        "readiness_distance_score": score,
    }


def build_report() -> dict[str, Any]:
    tracker = load_json(TRACKER_JSON)
    integrity = load_json(INTEGRITY_JSON)
    live_ready = load_json(LIVE_READY_JSON)
    rows = [row for row in tracker.get("rows") or [] if isinstance(row, dict)]
    integrity_by_key = integrity_index(integrity)
    classified = [classify(with_integrity(row, integrity_by_key)) for row in rows]
    positive = [row for row in classified if (as_float(row.get("net_cents")) or 0.0) > 0.0]
    broad_positive = [
        row for row in positive
        if (coverage := as_float(row.get("coverage_pct"))) is not None and MIN_COVERAGE <= coverage <= MAX_COVERAGE
    ]
    closest = sorted(
        positive,
        key=lambda row: (
            row["readiness_distance_score"],
            -(as_float(row.get("settled")) or 0.0),
            -(as_float(row.get("net_cents")) or 0.0),
        ),
    )[:15]
    closest_broad = sorted(
        broad_positive,
        key=lambda row: (
            row["readiness_distance_score"],
            -(as_float(row.get("settled")) or 0.0),
            -(as_float(row.get("net_cents")) or 0.0),
        ),
    )[:15]
    top_pnl = sorted(
        positive,
        key=lambda row: as_float(row.get("net_cents")) or -999999.0,
        reverse=True,
    )[:15]
    return {
        "generated_at_utc": utc_now_iso(),
        "summary": {
            "tracker_rows": len(rows),
            "positive_rows": len(positive),
            "broad_positive_rows": len(broad_positive),
            "live_ready_rows": sum(1 for row in classified if row.get("live_ready")),
            "integrity_pass_count": integrity.get("integrity_pass_count"),
            "live_readiness_any_live_ready": live_ready.get("any_live_ready"),
        },
        "closest_positive": closest,
        "closest_broad_positive": closest_broad,
        "top_pnl": top_pnl,
    }


def fmt_cents(value: Any) -> str:
    number = as_float(value)
    if number is None:
        return "n/a"
    return f"{number:.0f}c"


def fmt_pct(value: Any) -> str:
    number = as_float(value)
    if number is None:
        return "n/a"
    return f"{number:.2f}%"


def fmt_share(value: Any) -> str:
    number = as_float(value)
    if number is None:
        return "n/a"
    return f"{number * 100.0:.1f}%"


def write_table(lines: list[str], rows: list[dict[str, Any]]) -> None:
    lines.extend(
        [
            "| gate | policy | settled | W/L | coverage | net | sim share | distance | missing gates |",
            "|---|---|---:|---:|---:|---:|---:|---:|---|",
        ]
    )
    for row in rows:
        wl = "n/a"
        if row.get("wins") is not None and row.get("losses") is not None:
            wl = f"{row.get('wins')}/{row.get('losses')}"
        lines.append(
            f"| `{row.get('gate')}` | `{row.get('policy')}` | {row.get('settled')} | {wl} | "
            f"{fmt_pct(row.get('coverage_pct'))} | {fmt_cents(row.get('net_cents'))} | "
            f"{fmt_share(row.get('simulated_share'))} | {row.get('readiness_distance_score'):.1f} | "
            f"{', '.join(row.get('missing_gates') or [])} |"
        )


def write_md(report: dict[str, Any]) -> None:
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    summary = report["summary"]
    lines = [
        "# v28 Candidate Readiness Distance",
        "",
        "Research-only digest; no live bot changes or orders.",
        "",
        f"- Generated UTC: `{report.get('generated_at_utc')}`",
        f"- Positive rows: `{summary['positive_rows']}` / `{summary['tracker_rows']}`",
        f"- Broad positive rows: `{summary['broad_positive_rows']}`",
        f"- Live-ready rows: `{summary['live_ready_rows']}`",
        f"- Integrity-pass rows: `{summary['integrity_pass_count']}`",
        "",
        "## Closest Broad Positive",
        "",
    ]
    write_table(lines, report.get("closest_broad_positive") or [])
    lines.extend(["", "## Closest Positive", ""])
    write_table(lines, report.get("closest_positive") or [])
    lines.extend(["", "## Top PnL", ""])
    write_table(lines, report.get("top_pnl") or [])
    lines.extend(
        [
            "",
            "## Notes",
            "",
            "- Distance is a sorting aid only; it does not override live readiness or integrity gates.",
            "- `source_unknown` means no source-stress field exists in the consolidated tracker row, so the lane remains weakly verified.",
        ]
    )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    report = build_report()
    write_md(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
