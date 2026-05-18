"""Promotion runway for the frozen side-asymmetry FV overlay.

Research-only; no live bot changes or orders.

The side-asymmetry overlay is a calibration lead, not a trade rule. It has a
small frozen sample with negative Brier/logloss deltas, so this artifact tracks
what would need to happen before it can be treated as a serious FV candidate.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
FROZEN_JSON = OUT_DIR / "v28_frozen_side_asymmetry_fv_overlay_latest.json"
DISCOVERY_JSON = OUT_DIR / "v28_side_asymmetry_fv_overlay_latest.json"
LIVE_READINESS_JSON = OUT_DIR / "v28_live_trade_readiness_latest.json"
OUT_JSON = OUT_DIR / "v28_side_asymmetry_promotion_runway_latest.json"
OUT_MD = OUT_DIR / "v28_side_asymmetry_promotion_runway_latest.md"

MIN_SETTLED = 30
MIN_ADJUSTED = 8
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


def check(name: str, passed: bool, actual: Any, required: str, note: str) -> dict[str, Any]:
    return {
        "name": name,
        "passed": bool(passed),
        "actual": actual,
        "required": required,
        "note": note,
    }


def readiness_row(live_ready: dict[str, Any]) -> dict[str, Any]:
    return next(
        (
            row for row in live_ready.get("candidates") or []
            if row.get("gate") == "side_asymmetry_fv_overlay"
        ),
        {},
    )


def build_report() -> dict[str, Any]:
    frozen = load_json(FROZEN_JSON)
    discovery = load_json(DISCOVERY_JSON)
    live_ready = load_json(LIVE_READINESS_JSON)
    candidate = frozen.get("candidate") or {}
    ready = readiness_row(live_ready)
    settled = int(as_float(candidate.get("settled")) or 0)
    adjusted = int(as_float(candidate.get("adjusted_rows")) or 0)
    coverage = as_float(candidate.get("coverage_pct"))
    if coverage is None:
        coverage = as_float(frozen.get("coverage_pct"))
    brier = as_float(candidate.get("brier_mean_delta"))
    logloss = as_float(candidate.get("logloss_mean_delta"))
    checks = [
        check("settled_rows", settled >= MIN_SETTLED, settled, f">={MIN_SETTLED}", f"need {gap(settled, MIN_SETTLED)} more settled rows"),
        check("adjusted_rows", adjusted >= MIN_ADJUSTED, adjusted, f">={MIN_ADJUSTED}", f"need {gap(adjusted, MIN_ADJUSTED)} more adjusted rows"),
        check("coverage_band", coverage is not None and COVERAGE_MIN <= coverage <= COVERAGE_MAX, coverage, f"{COVERAGE_MIN}-{COVERAGE_MAX}%", "coverage must stay compatible with the goal"),
        check("brier_better", brier is not None and brier < 0.0, brier, "<0 vs raw", "future Brier delta must remain negative"),
        check("logloss_better", logloss is not None and logloss < 0.0, logloss, "<0 vs raw", "future logloss delta must remain negative"),
        check("live_readiness_gate", ready.get("live_ready") is True, ready.get("live_ready"), "true", ", ".join(ready.get("blockers") or []) or "no readiness row yet"),
    ]
    return {
        "family": "side_asymmetry_fv_overlay",
        "freeze_ts": (frozen.get("freeze") or {}).get("freeze_ts_utc"),
        "variant": (frozen.get("freeze") or {}).get("variant"),
        "discovery_best_overlay": discovery.get("best_overlay"),
        "future_denominator": frozen.get("future_denominator"),
        "entries": frozen.get("entries"),
        "settled": settled,
        "adjusted": adjusted,
        "clock_adjusted": candidate.get("clock_adjusted_rows"),
        "side_adjusted": candidate.get("side_adjusted_rows"),
        "coverage_pct": coverage,
        "brier_mean_delta": brier,
        "logloss_mean_delta": logloss,
        "live_ready_blockers": ready.get("blockers") or [],
        "checks": checks,
        "ready_for_consideration": all(row["passed"] for row in checks),
        "interpretation": interpretation(checks, candidate, ready),
    }


def interpretation(checks: list[dict[str, Any]], candidate: dict[str, Any], ready: dict[str, Any]) -> list[str]:
    missing = [row for row in checks if not row["passed"]]
    return [
        f"Frozen side-asymmetry has {candidate.get('settled')} settled rows and {candidate.get('adjusted_rows')} adjusted rows.",
        f"Current Brier/logloss deltas are {candidate.get('brier_mean_delta')}/{candidate.get('logloss_mean_delta')}.",
        f"Promotion blockers remaining: {len(missing)}.",
        f"Live readiness blockers: {', '.join(ready.get('blockers') or []) or 'none'}.",
        "This lane can only improve FV calibration; it does not by itself fix negative broad-entry PnL.",
    ]


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
        "# v28 Side-Asymmetry Promotion Runway",
        "",
        "Research-only: no live bot changes and no orders.",
        "",
        f"- Freeze timestamp UTC: `{report.get('freeze_ts')}`",
        f"- Variant: `{report.get('variant')}`",
        f"- Future entries/settled/denominator: `{report.get('entries')}/{report.get('settled')}/{report.get('future_denominator')}`",
        f"- Adjusted rows clock/side/total: `{report.get('clock_adjusted')}/{report.get('side_adjusted')}/{report.get('adjusted')}`",
        f"- Brier/logloss delta: `{fmt(report.get('brier_mean_delta'))}/{fmt(report.get('logloss_mean_delta'))}`",
        f"- Ready for consideration: `{report.get('ready_for_consideration')}`",
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
    write_report(report)
    print(str(OUT_MD))


if __name__ == "__main__":
    main()
