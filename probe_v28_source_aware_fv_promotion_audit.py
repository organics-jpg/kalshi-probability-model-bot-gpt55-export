"""Promotion-style audit for the source-aware v28 FV overlay.

Research-only; no live bot changes or orders.

This does not promote the model. It checks whether the new source-aware FV
candidate has enough evidence quality to deserve continued focused monitoring
or implementation planning.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
SOURCE_AWARE_JSON = OUT_DIR / "v28_source_aware_fv_overlay_validator_latest.json"
FREEZE_AUDIT_JSON = OUT_DIR / "v28_anti_overfit_freeze_audit_latest.json"
ROBUSTNESS_JSON = OUT_DIR / "v28_source_aware_fv_robustness_audit_latest.json"
OUT_JSON = OUT_DIR / "v28_source_aware_fv_promotion_audit_latest.json"
OUT_MD = OUT_DIR / "v28_source_aware_fv_promotion_audit_latest.md"

EXPECTED_OVERLAY = "source_aware_approved_book_target_logit125_p60_only"
MIN_SETTLED = 30
MIN_APPROVED = 10
MAX_SIMULATED_SHARE = 0.35


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


def check(name: str, passed: bool, actual: Any, required: Any, evidence: str) -> dict[str, Any]:
    return {
        "name": name,
        "passed": bool(passed),
        "actual": actual,
        "required": required,
        "evidence": evidence,
    }


def build_report() -> dict[str, Any]:
    source = load_json(SOURCE_AWARE_JSON)
    freeze = load_json(FREEZE_AUDIT_JSON)
    robustness = load_json(ROBUSTNESS_JSON)
    best = next((row for row in source.get("ranked") or [] if row.get("overlay") == source.get("best_overlay")), {})
    brier_delta = as_float(best.get("brier_delta_vs_raw"))
    logloss_delta = as_float(best.get("logloss_delta_vs_raw"))
    settled = int(as_float(source.get("settled")) or 0)
    approved = int(as_float(source.get("approved_settled")) or 0)
    sim_share = as_float(source.get("simulated_share"))
    checks = [
        check("expected_overlay_is_best", source.get("best_overlay") == EXPECTED_OVERLAY, source.get("best_overlay"), EXPECTED_OVERLAY, str(SOURCE_AWARE_JSON)),
        check("settled_rows_gte_30", settled >= MIN_SETTLED, settled, f">= {MIN_SETTLED}", str(SOURCE_AWARE_JSON)),
        check("approved_rows_gte_10", approved >= MIN_APPROVED, approved, f">= {MIN_APPROVED}", str(SOURCE_AWARE_JSON)),
        check("simulated_share_lte_35pct", sim_share is not None and sim_share <= MAX_SIMULATED_SHARE, sim_share, f"<= {MAX_SIMULATED_SHARE}", str(SOURCE_AWARE_JSON)),
        check("brier_better_than_raw", brier_delta is not None and brier_delta < 0.0, brier_delta, "< 0", str(SOURCE_AWARE_JSON)),
        check("logloss_better_than_raw", logloss_delta is not None and logloss_delta < 0.0, logloss_delta, "< 0", str(SOURCE_AWARE_JSON)),
        check("freeze_audit_no_failures", freeze.get("fail_count") == 0, freeze.get("fail_count"), "0", str(FREEZE_AUDIT_JSON)),
        check("robustness_audit_no_blockers", not robustness.get("blockers"), robustness.get("blockers"), "none", str(ROBUSTNESS_JSON)),
    ]
    ready_for_review = all(item["passed"] for item in checks)
    return {
        "candidate": {
            "overlay": source.get("best_overlay"),
            "entry_surface": source.get("entry_surface"),
            "settled": settled,
            "approved_settled": approved,
            "simulated_settled": source.get("simulated_settled"),
            "simulated_share": sim_share,
            "avg_brier": best.get("avg_brier"),
            "brier_delta_vs_raw": brier_delta,
            "avg_logloss": best.get("avg_logloss"),
            "logloss_delta_vs_raw": logloss_delta,
            "calibration_error": best.get("calibration_error"),
            "robustness_blockers": robustness.get("blockers"),
            "leave_one_market_failures": robustness.get("leave_one_market_failures"),
            "dominant_market_brier_delta_share": robustness.get("dominant_market_brier_delta_share"),
        },
        "ready_for_implementation_planning": ready_for_review,
        "checks": checks,
        "notes": [
            "This is not live bot approval; it says whether the FV candidate has enough evidence quality to deserve planning/continued monitoring.",
            "The candidate is source-aware: approved rows use book anchoring; target-coverage rejected rows use strong-row logit sharpening.",
            "Robustness blockers mean the candidate remains a watch candidate, not an implementation candidate.",
            "A true live deployment would still need an implementation plan, tests, and a no-trade dry validation against current live telemetry.",
        ],
    }


def fmt(value: Any) -> str:
    if value is None:
        return "None"
    if isinstance(value, float):
        return f"{value:.6f}"
    return str(value)


def write_md(report: dict[str, Any]) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8")
    c = report.get("candidate") or {}
    lines = [
        "# v28 Source-Aware FV Promotion Audit",
        "",
        f"- Ready for implementation planning: `{report.get('ready_for_implementation_planning')}`",
        f"- Overlay: `{c.get('overlay')}`",
        f"- Settled/approved/simulated/share: `{c.get('settled')}/{c.get('approved_settled')}/{c.get('simulated_settled')}/{fmt(c.get('simulated_share'))}`",
        f"- Brier/delta: `{fmt(c.get('avg_brier'))}/{fmt(c.get('brier_delta_vs_raw'))}`",
        f"- Logloss/delta: `{fmt(c.get('avg_logloss'))}/{fmt(c.get('logloss_delta_vs_raw'))}`",
        f"- Calibration error: `{fmt(c.get('calibration_error'))}`",
        f"- Robustness blockers: `{', '.join(c.get('robustness_blockers') or []) or 'none'}`",
        f"- Leave-one-market failures / dominant share: `{c.get('leave_one_market_failures')}/{fmt(c.get('dominant_market_brier_delta_share'))}`",
        "",
        "## Checks",
        "",
        "| check | pass | actual | required | evidence |",
        "|---|---:|---|---|---|",
    ]
    for item in report.get("checks") or []:
        lines.append(
            f"| {item.get('name')} | {item.get('passed')} | `{item.get('actual')}` | `{item.get('required')}` | {item.get('evidence')} |"
        )
    lines.extend(["", "## Notes", ""])
    for note in report.get("notes") or []:
        lines.append(f"- {note}")
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    report = build_report()
    write_md(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
