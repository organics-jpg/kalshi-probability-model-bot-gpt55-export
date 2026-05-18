"""Physics-bucket attribution for the frozen v28 +5pp FV challenger.

This consumes the clean forward monitor and asks a narrow question: where does
the entry-conditioned +5pp probability overlay beat or lose to raw v28 on fresh
settled rows? Buckets are predeclared diagnostics, not optimization knobs.

Research-only; no live bot changes or orders.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Callable


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
MONITOR_JSON = OUT_DIR / "v28_calibrated_fv_forward_monitor_latest.json"
OUT_JSON = OUT_DIR / "v28_calibrated_fv_physics_attribution_latest.json"
OUT_MD = OUT_DIR / "v28_calibrated_fv_physics_attribution_latest.md"

BucketTest = Callable[[dict[str, Any]], bool]


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


def selected_rows(report: dict[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for item in report.get("clean_details") or []:
        selected = item.get("selected_row") or {}
        if not selected:
            continue
        row = dict(selected)
        row["market"] = item.get("market")
        rows.append(row)
    return rows


def settled(row: dict[str, Any]) -> bool:
    return row.get("side_won") is not None


def bucket_definitions() -> list[tuple[str, str, BucketTest]]:
    return [
        ("all_selected", "All selected clean forward rows.", lambda row: True),
        ("settled_only", "Rows that already have a known outcome.", settled),
        (
            "near_strike_abs_d_lte_025",
            "Selected when spot geometry was close enough that recross risk should matter.",
            lambda row: (as_float(row.get("abs_d_sigma")) or 999.0) <= 0.25,
        ),
        (
            "away_from_strike_abs_d_gt_025",
            "Selected when the side had more distance from the strike.",
            lambda row: (as_float(row.get("abs_d_sigma")) or 0.0) > 0.25,
        ),
        (
            "high_recross_hazard_gte_075",
            "Selected in high recross-hazard geometry.",
            lambda row: (as_float(row.get("recross_hazard_score")) or 0.0) >= 0.75,
        ),
        (
            "moderate_recross_hazard_025_075",
            "Selected in moderate recross-hazard geometry.",
            lambda row: 0.25 <= (as_float(row.get("recross_hazard_score")) or -1.0) < 0.75,
        ),
        (
            "raw_edge_lt_05pp",
            "Barely executable raw edge; useful for detecting false confidence.",
            lambda row: (as_float(row.get("raw_edge_prob")) or 999.0) < 0.05,
        ),
        (
            "raw_edge_05_10pp",
            "Moderate executable raw edge.",
            lambda row: 0.05 <= (as_float(row.get("raw_edge_prob")) or -999.0) < 0.10,
        ),
        (
            "raw_edge_gte_10pp",
            "Large executable raw edge.",
            lambda row: (as_float(row.get("raw_edge_prob")) or -999.0) >= 0.10,
        ),
        (
            "raw_p_50_60",
            "Raw v28 only barely liked the selected side.",
            lambda row: 0.50 <= (as_float(row.get("p_raw")) or -1.0) < 0.60,
        ),
        (
            "raw_p_60_plus",
            "Raw v28 already had stronger selected-side conviction.",
            lambda row: (as_float(row.get("p_raw")) or 0.0) >= 0.60,
        ),
        (
            "ask_lte_60",
            "Selected side was not expensive at entry.",
            lambda row: (as_float(row.get("ask_prob")) or 999.0) <= 0.60,
        ),
        (
            "ask_gt_60",
            "Selected side was expensive at entry.",
            lambda row: (as_float(row.get("ask_prob")) or 0.0) > 0.60,
        ),
        (
            "early_market_stc_gt_600",
            "More than ten minutes to close at selected row.",
            lambda row: (as_float(row.get("seconds_to_close")) or -1.0) > 600.0,
        ),
        (
            "spectral_dominant_factor",
            "RMT diagnostic saw a dominant broad-market factor.",
            lambda row: row.get("spectral_tag") == "spectral_dominant_factor",
        ),
    ]


def summarize_bucket(name: str, description: str, rows: list[dict[str, Any]]) -> dict[str, Any]:
    settled_rows = [row for row in rows if settled(row)]
    brier_deltas = [
        float(row["brier_delta_plus05_minus_raw"])
        for row in settled_rows
        if row.get("brier_delta_plus05_minus_raw") is not None
    ]
    logloss_deltas = [
        float(row["logloss_delta_plus05_minus_raw"])
        for row in settled_rows
        if row.get("logloss_delta_plus05_minus_raw") is not None
    ]
    net_rows = [
        float(row["net_gross_cents_after_entry_fee"])
        for row in settled_rows
        if row.get("net_gross_cents_after_entry_fee") is not None
    ]
    return {
        "bucket": name,
        "description": description,
        "selected": len(rows),
        "settled": len(settled_rows),
        "wins": sum(1 for row in settled_rows if row.get("side_won") is True),
        "losses": sum(1 for row in settled_rows if row.get("side_won") is False),
        "net_cents": sum(net_rows),
        "brier_delta_sum_plus05_minus_raw": sum(brier_deltas),
        "brier_delta_mean_plus05_minus_raw": sum(brier_deltas) / len(brier_deltas) if brier_deltas else None,
        "brier_improved_count": sum(1 for value in brier_deltas if value < 0),
        "brier_worsened_count": sum(1 for value in brier_deltas if value > 0),
        "logloss_delta_sum_plus05_minus_raw": sum(logloss_deltas),
        "logloss_delta_mean_plus05_minus_raw": sum(logloss_deltas) / len(logloss_deltas) if logloss_deltas else None,
        "logloss_improved_count": sum(1 for value in logloss_deltas if value < 0),
        "logloss_worsened_count": sum(1 for value in logloss_deltas if value > 0),
        "markets": [str(row.get("market") or "") for row in rows],
    }


def build_report() -> dict[str, Any]:
    monitor = load_json(MONITOR_JSON)
    rows = selected_rows(monitor)
    bucket_rows = []
    for name, description, predicate in bucket_definitions():
        matching = [row for row in rows if predicate(row)]
        bucket_rows.append(summarize_bucket(name, description, matching))
    blockers = []
    settled_count = sum(1 for row in rows if settled(row))
    if settled_count < 5:
        blockers.append("bucket_sample_lt_5")
    if settled_count < 30:
        blockers.append("promotion_sample_lt_30")
    return {
        "source_monitor": str(MONITOR_JSON),
        "freeze_ts": monitor.get("freeze_ts"),
        "clean_forward_market_count": monitor.get("clean_forward_market_count"),
        "selected_clean_count": monitor.get("selected_clean_count"),
        "settled_selected_count": settled_count,
        "pending_selected_count": monitor.get("pending_selected_count"),
        "coverage_pct": monitor.get("coverage_pct"),
        "blockers": blockers,
        "buckets": bucket_rows,
    }


def fmt(value: Any) -> str:
    if value is None:
        return "None"
    if isinstance(value, float):
        return f"{value:.6f}"
    return str(value)


def write_report(report: dict[str, Any]) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    lines = [
        "# v28 Calibrated FV Physics Attribution",
        "",
        "Predeclared physics-bucket attribution for the frozen raw-entry +5pp FV overlay.",
        "",
        f"- Freeze timestamp UTC: `{report.get('freeze_ts')}`",
        f"- Clean forward markets: `{report.get('clean_forward_market_count')}`",
        f"- Selected/settled/pending: `{report.get('selected_clean_count')}/{report.get('settled_selected_count')}/{report.get('pending_selected_count')}`",
        f"- Coverage: `{fmt(report.get('coverage_pct'))}`",
        f"- Blockers: `{', '.join(report.get('blockers') or []) or 'none'}`",
        "",
        "## Buckets",
        "",
        "| bucket | selected | settled | W/L | net c | brier d mean | brier +/- | logloss d mean | logloss +/- |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for row in report.get("buckets") or []:
        lines.append(
            f"| {row.get('bucket')} | {row.get('selected')} | {row.get('settled')} | "
            f"{row.get('wins')}/{row.get('losses')} | {fmt(row.get('net_cents'))} | "
            f"{fmt(row.get('brier_delta_mean_plus05_minus_raw'))} | "
            f"{row.get('brier_improved_count')}/{row.get('brier_worsened_count')} | "
            f"{fmt(row.get('logloss_delta_mean_plus05_minus_raw'))} | "
            f"{row.get('logloss_improved_count')}/{row.get('logloss_worsened_count')} |"
        )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    report = build_report()
    write_report(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
