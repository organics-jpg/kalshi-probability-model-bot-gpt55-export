"""Readiness table for raw-entry FV overlay challengers.

Research-only; no live bot changes or orders.

The original raw-entry calibrated FV candidate centered on +5pp. Fresh forward
rows now show that +5pp is too blunt, so this report evaluates every frozen
probability overlay on the same raw-v28 p50 entry surface.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
DISCOVERY_JSON = OUT_DIR / "v28_raw_entry_calibrated_probability_latest.json"
FROZEN_JSON = OUT_DIR / "v28_frozen_raw_entry_calibrated_probability_latest.json"
DATA_QUALITY_JSON = OUT_DIR / "v28_entry_conditioned_data_quality_latest.json"
PATH_CONTRADICTION_JSON = OUT_DIR / "v28_calibrated_fv_path_contradiction_latest.json"
OUT_JSON = OUT_DIR / "v28_fv_overlay_challenger_readiness_latest.json"
OUT_MD = OUT_DIR / "v28_fv_overlay_challenger_readiness_latest.md"

MIN_SETTLED = 30
COVERAGE_MIN = 70.0
COVERAGE_MAX = 90.0

PHYSICS_NOTES = {
    "raw_probability": "Control. Raw v28 FV on the fixed broad p50 entry surface.",
    "entry_conditioned_plus03_probability": "Small posterior lift after executable raw edge clears.",
    "entry_conditioned_plus05_probability": "Original posterior lift candidate; fresh rows suggest it over-lifts weak states.",
    "entry_conditioned_logit125_probability": "Conviction sharpening: lift high-confidence rows more than weak rows without changing side.",
    "entry_conditioned_logit125_p60_only_probability": "Conditional conviction sharpening: keep weak 50-60% rows raw, sharpen only p>=60% rows.",
    "noise_shrink_light_probability": "Noise-floor shrinkage toward 50 in RMT/recross/stale states.",
    "book_probability": "Kalshi book-implied probability used as an external calibration anchor.",
}


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


def by_overlay(rows: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    return {str(row.get("overlay") or ""): row for row in rows if row.get("overlay")}


def blockers(row: dict[str, Any], discovery_row: dict[str, Any], data_quality: dict[str, Any], path: dict[str, Any]) -> list[str]:
    out: list[str] = []
    settled = as_float(row.get("settled") or row.get("count")) or 0.0
    coverage = as_float(row.get("coverage_pct"))
    brier_delta = as_float(row.get("brier_delta_vs_raw"))
    logloss_delta = as_float(row.get("logloss_delta_vs_raw"))
    discovery_brier_delta = as_float(discovery_row.get("brier_delta_vs_raw"))
    discovery_logloss_delta = as_float(discovery_row.get("logloss_delta_vs_raw"))
    if settled < MIN_SETTLED:
        out.append("forward_settled_lt_30")
    if coverage is None or coverage < COVERAGE_MIN:
        out.append("forward_coverage_too_low")
    if coverage is not None and coverage > COVERAGE_MAX:
        out.append("forward_coverage_too_high")
    if row.get("overlay") != "raw_probability":
        if brier_delta is None or brier_delta >= 0.0:
            out.append("forward_brier_not_better_than_raw")
        if logloss_delta is None or logloss_delta >= 0.0:
            out.append("forward_logloss_not_better_than_raw")
        if discovery_brier_delta is None or discovery_brier_delta >= 0.0:
            out.append("discovery_brier_not_better_than_raw")
        if discovery_logloss_delta is None or discovery_logloss_delta >= 0.0:
            out.append("discovery_logloss_not_better_than_raw")
        if row.get("bucket_stability_failures"):
            out.append("forward_bucket_failure")
    if data_quality.get("data_quality_pass") is not True:
        out.append("data_quality_not_passing")
    if float(path.get("settled_later_opposite_selected_losses") or 0.0) > 0.0:
        out.append("forward_path_contradiction_loss")
    if float(path.get("later_opposite_approval_rows") or 0.0) > 0.0 and float(path.get("settled_later_opposite_approval_rows") or 0.0) < 5.0:
        out.append("forward_path_contradiction_sample_lt_5")
    return out


def build_report() -> dict[str, Any]:
    discovery = load_json(DISCOVERY_JSON)
    frozen = load_json(FROZEN_JSON)
    data_quality = load_json(DATA_QUALITY_JSON)
    path = load_json(PATH_CONTRADICTION_JSON)
    discovery_rows = by_overlay(discovery.get("ranked") if isinstance(discovery.get("ranked"), list) else [])
    frozen_rows = frozen.get("ranked") if isinstance(frozen.get("ranked"), list) else []
    candidates: list[dict[str, Any]] = []
    for row in frozen_rows:
        overlay = str(row.get("overlay") or "")
        discovery_row = discovery_rows.get(overlay, {})
        row_blockers = blockers(row, discovery_row, data_quality, path)
        candidates.append({
            "overlay": overlay,
            "physics": PHYSICS_NOTES.get(overlay, "Unlabeled FV overlay."),
            "forward": row,
            "discovery": discovery_row,
            "ready": not row_blockers,
            "blockers": row_blockers,
        })
    candidates.sort(key=lambda item: (
        bool(item["blockers"]),
        float(as_float((item.get("forward") or {}).get("avg_brier")) if as_float((item.get("forward") or {}).get("avg_brier")) is not None else 999.0),
        float(as_float((item.get("forward") or {}).get("avg_logloss")) if as_float((item.get("forward") or {}).get("avg_logloss")) is not None else 999.0),
    ))
    return {
        "entry_surface": "v28_raw_p50_edge0_fixed_selection",
        "freeze_ts": frozen.get("freeze_ts"),
        "forward_market_denominator": frozen.get("forward_market_denominator"),
        "future_entry_rows": frozen.get("future_entry_rows"),
        "data_quality_pass": data_quality.get("data_quality_pass"),
        "path_contradiction": {
            "later_opposite_approval_rows": path.get("later_opposite_approval_rows"),
            "settled_later_opposite_selected_losses": path.get("settled_later_opposite_selected_losses"),
            "blockers": path.get("blockers") or [],
        },
        "requirements": [
            "same fixed raw-v28 p50 entry surface",
            "at least 30 settled forward rows",
            "70-90% forward market coverage",
            "forward Brier and logloss better than raw",
            "discovery Brier and logloss better than raw",
            "no eligible forward physics bucket failure",
            "data-quality pass",
            "no unresolved/losing later-opposite path contradiction",
        ],
        "candidates": candidates,
        "best_forward_overlay": candidates[0].get("overlay") if candidates else None,
        "any_ready": any(item.get("ready") for item in candidates),
    }


def fmt(value: Any) -> str:
    if value is None:
        return "None"
    if isinstance(value, float):
        return f"{value:.6f}"
    return str(value)


def write_report(report: dict[str, Any]) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8")
    lines = [
        "# v28 FV Overlay Challenger Readiness",
        "",
        "Forward-only readiness table for calibrated FV overlays on the fixed raw-v28 p50 entry surface.",
        "",
        f"- Entry surface: `{report.get('entry_surface')}`",
        f"- Freeze timestamp UTC: `{report.get('freeze_ts')}`",
        f"- Forward denominator/entry rows: `{report.get('forward_market_denominator')}/{report.get('future_entry_rows')}`",
        f"- Best forward overlay by current ranking: `{report.get('best_forward_overlay')}`",
        f"- Any ready: `{report.get('any_ready')}`",
        f"- Path contradiction rows/losses: `{(report.get('path_contradiction') or {}).get('later_opposite_approval_rows')}/{(report.get('path_contradiction') or {}).get('settled_later_opposite_selected_losses')}`",
        "",
        "## Candidates",
        "",
        "| overlay | ready | entries | settled | coverage | fwd brier d | fwd logloss d | disc brier d | disc logloss d | blockers |",
        "|---|---|---:|---:|---:|---:|---:|---:|---:|---|",
    ]
    for item in report.get("candidates") or []:
        fwd = item.get("forward") or {}
        disc = item.get("discovery") or {}
        lines.append(
            f"| {item.get('overlay')} | {item.get('ready')} | {fwd.get('entries')} | {fwd.get('settled')} | "
            f"{fmt(fwd.get('coverage_pct'))} | {fmt(fwd.get('brier_delta_vs_raw'))} | "
            f"{fmt(fwd.get('logloss_delta_vs_raw'))} | {fmt(disc.get('brier_delta_vs_raw'))} | "
            f"{fmt(disc.get('logloss_delta_vs_raw'))} | {', '.join(item.get('blockers') or []) or 'none'} |"
        )
    lines.extend(["", "## Physics Notes", ""])
    for item in report.get("candidates") or []:
        lines.append(f"- `{item.get('overlay')}`: {item.get('physics')}")
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    report = build_report()
    write_report(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
