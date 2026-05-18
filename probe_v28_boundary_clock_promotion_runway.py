"""Promotion runway for boundary-clock v28 candidates.

Research-only; no live bot changes or orders.

This report is deliberately mechanical. Boundary-clock is the current best
physics-backed lead, but it should not be promoted until frozen future evidence
exists. This artifact tracks the exact remaining evidence gaps.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
FROZEN_FV_JSON = OUT_DIR / "v28_frozen_boundary_clock_fv_overlay_latest.json"
FROZEN_REPAIR_JSON = OUT_DIR / "v28_frozen_boundary_clock_repair_entry_latest.json"
FROZEN_FV_ENTRY_BRIDGE_JSON = OUT_DIR / "v28_frozen_boundary_clock_fv_entry_bridge_latest.json"
FROZEN_RESIDUAL_JSON = OUT_DIR / "v28_frozen_boundary_clock_residual_registry_latest.json"
FV_ROBUSTNESS_JSON = OUT_DIR / "v28_boundary_clock_fv_robustness_latest.json"
ENTRY_ROBUSTNESS_JSON = OUT_DIR / "v28_boundary_clock_robustness_audit_latest.json"
LIVE_READINESS_JSON = OUT_DIR / "v28_live_trade_readiness_latest.json"
OUT_JSON = OUT_DIR / "v28_boundary_clock_promotion_runway_latest.json"
OUT_MD = OUT_DIR / "v28_boundary_clock_promotion_runway_latest.md"

MIN_SETTLED = 30
MIN_ADJUSTED = 8
MIN_ENTRY_DENOMINATOR = 30
COVERAGE_MIN = 75.0
COVERAGE_MAX = 90.0


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


def gap(actual: int, required: int) -> int:
    return max(0, required - int(actual or 0))


def fv_checks(fv: dict[str, Any], live_ready: dict[str, Any]) -> list[dict[str, Any]]:
    cand = fv.get("candidate") or {}
    settled = int(as_float(cand.get("settled")) or 0)
    adjusted = int(as_float(cand.get("adjusted_rows")) or 0)
    brier = as_float(cand.get("brier_mean_delta"))
    logloss = as_float(cand.get("logloss_mean_delta"))
    readiness_row = next(
        (
            row for row in live_ready.get("candidates") or []
            if row.get("gate") == "boundary_clock_fv_overlay"
        ),
        {},
    )
    return [
        check("fv_settled_rows", settled >= MIN_SETTLED, settled, f">={MIN_SETTLED}", f"need {gap(settled, MIN_SETTLED)} more settled rows"),
        check("fv_adjusted_rows", adjusted >= MIN_ADJUSTED, adjusted, f">={MIN_ADJUSTED}", f"need {gap(adjusted, MIN_ADJUSTED)} more adjusted hazard rows"),
        check("fv_brier_better", brier is not None and brier < 0.0, brier, "<0 vs raw", "future Brier delta must be negative"),
        check("fv_logloss_better", logloss is not None and logloss < 0.0, logloss, "<0 vs raw", "future logloss delta must be negative"),
        check("fv_live_readiness_gate", readiness_row.get("live_ready") is True, readiness_row.get("live_ready"), "true", ", ".join(readiness_row.get("blockers") or []) or "no readiness row yet"),
    ]


def entry_checks(repair: dict[str, Any]) -> list[dict[str, Any]]:
    cand = repair.get("candidate_summary") or {}
    denominator = int(as_float(repair.get("future_denominator")) or 0)
    settled = int(as_float(cand.get("settled")) or 0)
    coverage = as_float(cand.get("coverage_pct"))
    net = as_float(cand.get("net_cents"))
    return [
        check("entry_denominator", denominator >= MIN_ENTRY_DENOMINATOR, denominator, f">={MIN_ENTRY_DENOMINATOR}", f"need {gap(denominator, MIN_ENTRY_DENOMINATOR)} more future markets"),
        check("entry_settled_rows", settled >= MIN_SETTLED, settled, f">={MIN_SETTLED}", f"need {gap(settled, MIN_SETTLED)} more settled rows"),
        check("entry_coverage", coverage is not None and COVERAGE_MIN <= coverage <= COVERAGE_MAX, coverage, f"{COVERAGE_MIN}-{COVERAGE_MAX}%", "coverage must stay near target"),
        check("entry_net_positive", net is not None and net > 0.0, net, ">0c", "future candidate net must be positive"),
    ]


def bridge_checks(bridge: dict[str, Any], live_ready: dict[str, Any]) -> list[dict[str, Any]]:
    cand = bridge.get("candidate_summary") or {}
    denominator = int(as_float(bridge.get("future_denominator")) or 0)
    settled = int(as_float(cand.get("settled")) or 0)
    coverage = as_float(cand.get("coverage_pct"))
    net = as_float(cand.get("net_cents"))
    readiness_row = next(
        (
            row for row in live_ready.get("candidates") or []
            if row.get("gate") == "boundary_clock_fv_entry_bridge"
        ),
        {},
    )
    return [
        check("bridge_denominator", denominator >= MIN_ENTRY_DENOMINATOR, denominator, f">={MIN_ENTRY_DENOMINATOR}", f"need {gap(denominator, MIN_ENTRY_DENOMINATOR)} more future markets"),
        check("bridge_settled_rows", settled >= MIN_SETTLED, settled, f">={MIN_SETTLED}", f"need {gap(settled, MIN_SETTLED)} more settled rows"),
        check("bridge_coverage", coverage is not None and COVERAGE_MIN <= coverage <= COVERAGE_MAX, coverage, f"{COVERAGE_MIN}-{COVERAGE_MAX}%", "coverage must stay near target"),
        check("bridge_net_positive", net is not None and net > 0.0, net, ">0c", "future bridge candidate net must be positive"),
        check("bridge_live_readiness_gate", readiness_row.get("live_ready") is True, readiness_row.get("live_ready"), "true", ", ".join(readiness_row.get("blockers") or []) or "no readiness row yet"),
    ]


def residual_checks(residual: dict[str, Any]) -> list[dict[str, Any]]:
    bucket = residual.get("bucket_summary") or {}
    settled = int(as_float(bucket.get("settled")) or 0)
    net = as_float(bucket.get("net_cents"))
    return [
        check("residual_registry_settled", settled >= MIN_ADJUSTED, settled, f">={MIN_ADJUSTED}", "registry only; enough rows decide whether to create a candidate"),
        check("residual_registry_direction", net is not None and net < 0.0, net, "<0c if harmful", "negative bucket net would support future modeling work"),
    ]


def check(name: str, passed: bool, actual: Any, required: str, note: str) -> dict[str, Any]:
    return {
        "name": name,
        "passed": bool(passed),
        "actual": actual,
        "required": required,
        "note": note,
    }


def build_report() -> dict[str, Any]:
    fv = load_json(FROZEN_FV_JSON)
    repair = load_json(FROZEN_REPAIR_JSON)
    bridge = load_json(FROZEN_FV_ENTRY_BRIDGE_JSON)
    residual = load_json(FROZEN_RESIDUAL_JSON)
    fv_robustness = load_json(FV_ROBUSTNESS_JSON)
    entry_robustness = load_json(ENTRY_ROBUSTNESS_JSON)
    live_ready = load_json(LIVE_READINESS_JSON)
    checks = [
        *fv_checks(fv, live_ready),
        *entry_checks(repair),
        *bridge_checks(bridge, live_ready),
        *residual_checks(residual),
    ]
    return {
        "purpose": "Track the evidence runway for boundary-clock FV/entry candidates without promoting early.",
        "family": "boundary_clock",
        "fv_freeze_ts": (fv.get("freeze") or {}).get("freeze_ts_utc"),
        "entry_freeze_ts": (repair.get("freeze") or {}).get("freeze_ts_utc"),
        "bridge_freeze_ts": (bridge.get("freeze") or {}).get("freeze_ts_utc"),
        "residual_freeze_ts": (residual.get("freeze") or {}).get("freeze_ts_utc"),
        "diagnostic_fv_robustness_pass": fv_robustness.get("passes_basic_robustness"),
        "diagnostic_entry_robustness_pass": entry_robustness.get("passes_basic_robustness"),
        "checks": checks,
        "ready_for_consideration": all(row["passed"] for row in checks if not row["name"].startswith("residual_registry")),
        "residual_registry_ready": all(row["passed"] for row in checks if row["name"].startswith("residual_registry")),
        "interpretation": interpretation(checks, fv_robustness, entry_robustness),
    }


def interpretation(checks: list[dict[str, Any]], fv_robustness: dict[str, Any], entry_robustness: dict[str, Any]) -> list[str]:
    missing = [row for row in checks if not row["passed"]]
    return [
        f"Diagnostic robustness: FV={fv_robustness.get('passes_basic_robustness')}, entry={entry_robustness.get('passes_basic_robustness')}.",
        f"Frozen promotion blockers remaining: {len([row for row in missing if not row['name'].startswith('residual_registry')])}.",
        "The FV entry bridge is tracked as a separate promotion path because it converts the probability correction into entry economics.",
        "Residual registry is informational only and should not block the boundary-clock FV candidate.",
    ]


def fmt(value: Any) -> str:
    if value is None:
        return "None"
    if isinstance(value, float):
        return f"{value:.6f}"
    return str(value)


def write_md(report: dict[str, Any]) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8")
    lines = [
        "# v28 Boundary-Clock Promotion Runway",
        "",
        "Research-only: no live bot changes and no orders.",
        "",
        f"- FV freeze: `{report.get('fv_freeze_ts')}`",
        f"- Entry freeze: `{report.get('entry_freeze_ts')}`",
        f"- FV entry bridge freeze: `{report.get('bridge_freeze_ts')}`",
        f"- Residual registry freeze: `{report.get('residual_freeze_ts')}`",
        f"- Diagnostic robustness FV/entry: `{report.get('diagnostic_fv_robustness_pass')}/{report.get('diagnostic_entry_robustness_pass')}`",
        f"- Ready for consideration: `{report.get('ready_for_consideration')}`",
        f"- Residual registry ready: `{report.get('residual_registry_ready')}`",
        "",
        "## Interpretation",
        "",
    ]
    for note in report.get("interpretation") or []:
        lines.append(f"- {note}")
    lines.extend([
        "",
        "## Checks",
        "",
        "| check | pass | actual | required | note |",
        "|---|---:|---:|---|---|",
    ])
    for row in report.get("checks") or []:
        lines.append(
            f"| {row.get('name')} | `{row.get('passed')}` | {fmt(row.get('actual'))} | {row.get('required')} | {row.get('note')} |"
        )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    report = build_report()
    write_md(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
