"""Promotion runway for the frozen boundary-clock feature-gate candidate.

Research-only; no live bot changes or orders.

This reads the frozen feature-gate artifact and the refreshed live-only
baseline, then writes a compact gate/runway report for post-freeze rows.
"""
from __future__ import annotations

import json
import math
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
FEATURE_JSON = OUT_DIR / "v28_boundary_clock_feature_gate_candidate_latest.json"
SOURCE_DENOMINATOR_JSON = OUT_DIR / "v28_boundary_clock_feature_gate_source_denominator_audit_latest.json"
LIVE_SUMMARY_JSON = ROOT / "stats" / "live_mushroom_v28_size2" / "summary.json"
OUT_JSON = OUT_DIR / "v28_boundary_clock_feature_gate_runway_latest.json"
OUT_MD = OUT_DIR / "v28_boundary_clock_feature_gate_runway_latest.md"

MIN_SETTLED = 30
COVERAGE_FLOOR = 75.0
COVERAGE_CEILING = 90.0
MAX_RECONSTRUCTED_SHARE = 0.35
MIN_FULL_LOSS_CUSHION_CENTS = 300.0


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
    return int(as_float(value) or 0)


def source_parts(variant: dict[str, Any]) -> tuple[int, int, int]:
    counts = variant.get("source_counts")
    if not isinstance(counts, dict):
        counts = {}
    approved = as_int(counts.get("approved_entry"))
    total = sum(as_int(value) for value in counts.values())
    selected = as_int((variant.get("candidate_summary") or {}).get("settled"))
    total = max(total, selected)
    reconstructed = max(0, total - approved)
    return total, approved, reconstructed


def rule_name_from_candidate(lane_name: str, candidate: Any) -> str:
    text = str(candidate or "")
    prefix = f"{lane_name}_"
    if text.startswith(prefix):
        return text[len(prefix):]
    return text


def source_audit_lookup(source_audit: dict[str, Any]) -> dict[tuple[str, str], dict[str, Any]]:
    lookup: dict[tuple[str, str], dict[str, Any]] = {}
    for lane in source_audit.get("lanes") or []:
        if not isinstance(lane, dict):
            continue
        lane_name = str(lane.get("lane") or "")
        for rule in lane.get("rules") or []:
            if isinstance(rule, dict):
                lookup[(lane_name, str(rule.get("rule") or ""))] = rule
    return lookup


def approved_needed_for_recon(total: int, reconstructed: int) -> int:
    if total <= 0:
        return 0
    if reconstructed / total <= MAX_RECONSTRUCTED_SHARE:
        return 0
    return int(math.ceil((reconstructed / MAX_RECONSTRUCTED_SHARE) - total))


def selected_needed_for_coverage(entries: int, denominator: int) -> int:
    if denominator <= 0:
        return 0
    if 100.0 * entries / denominator >= COVERAGE_FLOOR:
        return 0
    # Assumes every additional future market is selected by the same lane.
    needed = ((COVERAGE_FLOOR / 100.0) * denominator - entries) / (1.0 - COVERAGE_FLOOR / 100.0)
    return max(0, int(math.ceil(needed)))


def compact_lane(lane: dict[str, Any], live_net_cents: float, source_lookup: dict[tuple[str, str], dict[str, Any]]) -> list[dict[str, Any]]:
    lane_name = str(lane.get("lane") or "")
    denominator = as_int(lane.get("future_denominator"))
    rows: list[dict[str, Any]] = []
    for variant in lane.get("variants") or []:
        if not isinstance(variant, dict):
            continue
        summary = variant.get("candidate_summary")
        if not isinstance(summary, dict):
            continue
        entries = as_int(summary.get("entries"))
        settled = as_int(summary.get("settled"))
        net = as_float(summary.get("net_cents")) or 0.0
        rule_name = rule_name_from_candidate(lane_name, variant.get("candidate"))
        source_audit = source_lookup.get((lane_name, rule_name), {})
        total, approved, reconstructed = source_parts(variant)
        recon_share = None if total <= 0 else reconstructed / total
        needed_sample = max(0, MIN_SETTLED - settled)
        needed_coverage = selected_needed_for_coverage(entries, denominator)
        needed_recon = approved_needed_for_recon(total, reconstructed)
        needed_gate = max(needed_sample, needed_coverage, needed_recon)
        coverage_after_gate = None
        if denominator + needed_gate > 0:
            coverage_after_gate = 100.0 * (entries + needed_gate) / (denominator + needed_gate)
        avg_needed_positive = None
        avg_needed_cushion = None
        if needed_gate > 0:
            avg_needed_positive = (0.01 - net) / needed_gate
            avg_needed_cushion = (MIN_FULL_LOSS_CUSHION_CENTS - net) / needed_gate
        rows.append(
            {
                "lane": lane_name,
                "candidate": variant.get("candidate"),
                "rule": rule_name,
                "settled": settled,
                "entries": entries,
                "future_denominator": denominator,
                "coverage_pct": summary.get("coverage_pct"),
                "net_cents": net,
                "wins": summary.get("wins"),
                "losses": summary.get("losses"),
                "approved_entry": approved,
                "reconstructed": reconstructed,
                "reconstructed_share": recon_share,
                "source_denominator_selected_reconstructed_share": source_audit.get("selected_reconstructed_share"),
                "approved_source_market_coverage_pct": source_audit.get("approved_observed_coverage_pct"),
                "reconstructed_source_market_coverage_pct": source_audit.get("reconstructed_observed_coverage_pct"),
                "omitted_source_net_cents": source_audit.get("omitted_source_net_cents"),
                "full_loss_cushion": int(max(0.0, net) // 100.0),
                "delta_vs_live_cents": net - live_net_cents,
                "future_selected_needed_for_30": needed_sample,
                "future_selected_needed_for_coverage75": needed_coverage,
                "future_approved_needed_for_recon35": needed_recon,
                "future_clean_selected_needed_for_all_gates": needed_gate,
                "coverage_after_gate_if_all_selected": coverage_after_gate,
                "avg_future_net_needed_positive_cents": avg_needed_positive,
                "avg_future_net_needed_cushion3_cents": avg_needed_cushion,
                "blockers": variant.get("blockers") or [],
            }
        )
    return rows


def build_report() -> dict[str, Any]:
    feature = load_json(FEATURE_JSON)
    source_audit = load_json(SOURCE_DENOMINATOR_JSON)
    source_lookup = source_audit_lookup(source_audit)
    live = load_json(LIVE_SUMMARY_JSON)
    live_net_cents = round(float(live.get("net_pnl_total_dollars") or 0.0) * 100.0)
    post_rows: list[dict[str, Any]] = []
    diagnostic_rows: list[dict[str, Any]] = []
    for lane in feature.get("lanes") or []:
        if not isinstance(lane, dict):
            continue
        lane_name = str(lane.get("lane") or "")
        compact = compact_lane(lane, live_net_cents, source_lookup)
        if lane_name.startswith("post_feature_freeze_"):
            post_rows.extend(compact)
        elif lane_name.startswith("diagnostic_"):
            diagnostic_rows.extend(compact)
    post_rows.sort(
        key=lambda row: (
            row["future_clean_selected_needed_for_all_gates"],
            -(as_float(row.get("net_cents")) or -999999.0),
        )
    )
    diagnostic_rows.sort(
        key=lambda row: (
            len(row.get("blockers") or []),
            -(as_float(row.get("net_cents")) or -999999.0),
        )
    )
    clean_source_rows = [
        row for row in post_rows
        if as_float(row.get("source_denominator_selected_reconstructed_share")) == 0.0
    ]
    clean_source_rows.sort(
        key=lambda row: (
            -(as_float(row.get("net_cents")) or -999999.0),
            -(as_float(row.get("approved_source_market_coverage_pct")) or 0.0),
            row["future_clean_selected_needed_for_all_gates"],
        )
    )
    report = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "feature_gate_path": str(FEATURE_JSON),
        "live_summary_path": str(LIVE_SUMMARY_JSON),
        "freeze_ts_utc": (feature.get("state") or {}).get("freeze_ts_utc"),
        "live_net_cents": live_net_cents,
        "requirements": {
            "min_settled": MIN_SETTLED,
            "coverage_floor": COVERAGE_FLOOR,
            "coverage_ceiling": COVERAGE_CEILING,
            "max_reconstructed_share": MAX_RECONSTRUCTED_SHARE,
            "min_full_loss_cushion_cents": MIN_FULL_LOSS_CUSHION_CENTS,
        },
        "diagnostic_top": diagnostic_rows[:8],
        "post_freeze_top": post_rows[:8],
        "post_freeze_clean_source_top": clean_source_rows[:8],
    }
    report["interpretation"] = interpretation(report)
    return report


def interpretation(report: dict[str, Any]) -> list[str]:
    notes = [
        "Feature-gate selection is observable-only; source labels remain audit-only.",
    ]
    post = report.get("post_freeze_top") or []
    if post:
        best = post[0]
        notes.append(
            f"Best post-freeze lane {best.get('candidate')} has {best.get('settled')} settled row(s), "
            f"{best.get('coverage_pct')}% coverage, {best.get('net_cents')}c net, "
            f"reconstructed share {best.get('reconstructed_share')}, and delta {best.get('delta_vs_live_cents')}c versus refreshed live."
        )
        notes.append(
            f"It needs {best.get('future_clean_selected_needed_for_all_gates')} future clean selected rows to satisfy "
            "sample/coverage/source gates under the all-future-selected runway assumption; "
            f"average future net for a 3-full-loss cushion is {best.get('avg_future_net_needed_cushion3_cents')}c."
        )
    clean = report.get("post_freeze_clean_source_top") or []
    if clean:
        best_clean = clean[0]
        notes.append(
            f"Best clean-source post-freeze lane {best_clean.get('candidate')} has selected reconstructed share "
            f"{best_clean.get('source_denominator_selected_reconstructed_share')}, approved-source market coverage "
            f"{best_clean.get('approved_source_market_coverage_pct')}%, total coverage {best_clean.get('coverage_pct')}%, "
            f"net {best_clean.get('net_cents')}c, and omitted source net {best_clean.get('omitted_source_net_cents')}."
        )
    else:
        notes.append("No fully clean-source post-freeze feature-gate row is available yet.")
    notes.append("This is watch-only until >=30 settled forward rows, positive PnL, target coverage, source quality, full-loss cushion, and live readiness all pass.")
    return notes


def fmt(value: Any) -> str:
    if value is None:
        return "None"
    if isinstance(value, float):
        return f"{value:.6f}"
    return str(value)


def write_table(lines: list[str], rows: list[dict[str, Any]]) -> None:
    lines.extend(
        [
            "| lane | candidate | settled/den | W/L | coverage | net c | delta live c | recon | approved-source cov | recon-source cov | cushion | future clean rows | avg c for cushion3 | blockers |",
            "|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|",
        ]
    )
    for row in rows:
        blockers = ", ".join(str(item) for item in row.get("blockers") or []) or "none"
        lines.append(
            f"| {row.get('lane')} | {row.get('candidate')} | "
            f"{row.get('settled')}/{row.get('future_denominator')} | "
            f"{row.get('wins')}/{row.get('losses')} | "
            f"{fmt(row.get('coverage_pct'))} | {fmt(row.get('net_cents'))} | "
            f"{fmt(row.get('delta_vs_live_cents'))} | {fmt(row.get('reconstructed_share'))} | "
            f"{fmt(row.get('approved_source_market_coverage_pct'))} | "
            f"{fmt(row.get('reconstructed_source_market_coverage_pct'))} | "
            f"{row.get('full_loss_cushion')} | {row.get('future_clean_selected_needed_for_all_gates')} | "
            f"{fmt(row.get('avg_future_net_needed_cushion3_cents'))} | {blockers} |"
        )


def write_md(report: dict[str, Any]) -> None:
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8")
    lines = [
        "# v28 Boundary-Clock Feature-Gate Runway",
        "",
        "Research-only; no live bot changes or orders.",
        "",
        f"- Generated UTC: `{report.get('generated_at_utc')}`",
        f"- Feature-gate freeze UTC: `{report.get('freeze_ts_utc')}`",
        f"- Refreshed live net: `{report.get('live_net_cents')}c`",
        "",
        "## Interpretation",
        "",
    ]
    for note in report.get("interpretation") or []:
        lines.append(f"- {note}")
    lines.extend(["", "## Post-Freeze Runway", ""])
    post_rows = report.get("post_freeze_top") or []
    if post_rows:
        write_table(lines, post_rows)
    else:
        lines.append("- No post-freeze rows yet.")
    lines.extend(["", "## Clean-Source Post-Freeze Runway", ""])
    clean_rows = report.get("post_freeze_clean_source_top") or []
    if clean_rows:
        write_table(lines, clean_rows)
    else:
        lines.append("- No clean-source post-freeze rows yet.")
    lines.extend(["", "## Diagnostic Reference", ""])
    diagnostic_rows = report.get("diagnostic_top") or []
    if diagnostic_rows:
        write_table(lines, diagnostic_rows)
    else:
        lines.append("- No diagnostic rows available.")
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    report = build_report()
    write_md(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
