"""Promotion readiness audit for v28 FV/strategy candidates.

This does not promote or change anything. It encodes the minimum evidence
standard for considering a model/strategy patch so we do not fool ourselves
with tiny live-shadow samples.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
SCORECARD_JSON = OUT_DIR / "v28_continuous_scorecard_latest.json"
VARIANTS_JSON = OUT_DIR / "v28_shadow_fv_variants_latest.json"
BOOK_JSON = OUT_DIR / "v28_book_disagreement_calibration_latest.json"
CALIBRATION_JSON = OUT_DIR / "v28_forward_calibration_latest.json"
ENTRY_POLICY_JSON = OUT_DIR / "v28_shadow_entry_policy_bakeoff_latest.json"
OUT_JSON = OUT_DIR / "v28_promotion_readiness_latest.json"
OUT_MD = OUT_DIR / "v28_promotion_readiness_latest.md"


DEFAULT_MIN_SETTLED_OBSERVATIONS = 100
DEFAULT_MIN_WATCHED_MARKETS = 50
DEFAULT_MIN_COVERAGE_PCT = 75.0
DEFAULT_MIN_BRIER_IMPROVEMENT_VS_BOOK = 0.001
DEFAULT_MAX_ABS_CALIBRATION_ERROR = 0.05
DEFAULT_MIN_NONNEGATIVE_GROSS_CENTS = 0.0


def load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}


def env_float(name: str, default: float) -> float:
    value = os.environ.get(name)
    if value is None or value == "":
        return default
    try:
        return float(value)
    except ValueError:
        return default


def env_int(name: str, default: int) -> int:
    value = os.environ.get(name)
    if value is None or value == "":
        return default
    try:
        return int(value)
    except ValueError:
        return default


def check(name: str, passed: bool, actual: Any, required: Any, evidence: str) -> dict[str, Any]:
    return {
        "name": name,
        "passed": bool(passed),
        "actual": actual,
        "required": required,
        "evidence": evidence,
    }


def build_audit() -> dict[str, Any]:
    scorecard = load_json(SCORECARD_JSON)
    variants = load_json(VARIANTS_JSON)
    book = load_json(BOOK_JSON)
    calibration = load_json(CALIBRATION_JSON)
    entry_policy = load_json(ENTRY_POLICY_JSON)

    score_summary = scorecard.get("summary", {}) if isinstance(scorecard, dict) else {}
    variant_summary = variants.get("summary", {}) if isinstance(variants, dict) else {}
    variant_ranked = variant_summary.get("ranked", []) if isinstance(variant_summary, dict) else []
    raw_variant = next((row for row in variant_ranked if row.get("variant") == "v28_raw"), {})
    top_variant = variant_ranked[0] if variant_ranked else {}
    book_summary = book.get("summary", {}) if isinstance(book, dict) else {}
    book_overall = book_summary.get("overall", {}) if isinstance(book_summary, dict) else {}
    calibration_summary = calibration.get("summary", {}) if isinstance(calibration, dict) else {}
    calibration_overall = calibration_summary.get("overall", {}) if isinstance(calibration_summary, dict) else {}
    entry_policy_ranked = entry_policy.get("ranked", []) if isinstance(entry_policy, dict) else []
    best_policy = entry_policy_ranked[0] if entry_policy_ranked else {}

    min_observations = env_int("V28_PROMOTION_MIN_SETTLED_OBSERVATIONS", DEFAULT_MIN_SETTLED_OBSERVATIONS)
    min_watched = env_int("V28_PROMOTION_MIN_WATCHED_MARKETS", DEFAULT_MIN_WATCHED_MARKETS)
    min_coverage = env_float("V28_PROMOTION_MIN_COVERAGE_PCT", DEFAULT_MIN_COVERAGE_PCT)
    min_brier_improvement = env_float("V28_PROMOTION_MIN_BRIER_IMPROVEMENT_VS_BOOK", DEFAULT_MIN_BRIER_IMPROVEMENT_VS_BOOK)
    max_abs_cal_error = env_float("V28_PROMOTION_MAX_ABS_CALIBRATION_ERROR", DEFAULT_MAX_ABS_CALIBRATION_ERROR)
    min_gross = env_float("V28_PROMOTION_MIN_NONNEGATIVE_GROSS_CENTS", DEFAULT_MIN_NONNEGATIVE_GROSS_CENTS)

    obs = int(variant_summary.get("observation_count") or 0)
    watched = int(score_summary.get("watched_markets") or 0)
    coverage = score_summary.get("coverage_pct")
    gross = float(score_summary.get("gross_cents") or 0.0)
    risk_stop = bool(score_summary.get("risk_stop"))
    top_name = str(top_variant.get("variant") or "")
    best_policy_name = str(best_policy.get("policy") or "")
    best_policy_coverage = best_policy.get("coverage_pct")
    best_policy_resolved = int(best_policy.get("resolved") or 0)
    best_policy_gross = float(best_policy.get("gross_cents") or 0.0)
    best_policy_losses = int(best_policy.get("losses") or 0)
    raw_brier = raw_variant.get("avg_brier")
    top_brier = top_variant.get("avg_brier")
    raw_vs_book = raw_variant.get("brier_minus_book_prior")
    top_vs_book = top_variant.get("brier_minus_book_prior")
    book_v28_minus_book = book_overall.get("avg_v28_brier_minus_book_brier")
    cal_error = calibration_overall.get("calibration_error")

    checks = [
        check(
            "settled_forward_observation_sample",
            obs >= min_observations,
            obs,
            f">= {min_observations}",
            str(VARIANTS_JSON),
        ),
        check(
            "watched_market_sample",
            watched >= min_watched,
            watched,
            f">= {min_watched}",
            str(SCORECARD_JSON),
        ),
        check(
            "coverage_target",
            coverage is not None and float(coverage) >= min_coverage,
            coverage,
            f">= {min_coverage}%",
            str(SCORECARD_JSON),
        ),
        check(
            "risk_stop_clear",
            not risk_stop,
            risk_stop,
            "False",
            str(SCORECARD_JSON),
        ),
        check(
            "nonnegative_forward_pnl",
            gross >= min_gross,
            gross,
            f">= {min_gross}",
            str(SCORECARD_JSON),
        ),
        check(
            "v28_beats_book_brier",
            raw_vs_book is not None and float(raw_vs_book) <= -min_brier_improvement,
            raw_vs_book,
            f"<= -{min_brier_improvement}",
            str(VARIANTS_JSON),
        ),
        check(
            "top_candidate_beats_book_brier",
            top_vs_book is not None and float(top_vs_book) <= -min_brier_improvement,
            {"variant": top_name, "brier_minus_book_prior": top_vs_book},
            f"<= -{min_brier_improvement}",
            str(VARIANTS_JSON),
        ),
        check(
            "book_disagreement_confirms_v28",
            book_v28_minus_book is not None and float(book_v28_minus_book) <= -min_brier_improvement,
            book_v28_minus_book,
            f"<= -{min_brier_improvement}",
            str(BOOK_JSON),
        ),
        check(
            "calibration_error_bounded",
            cal_error is not None and abs(float(cal_error)) <= max_abs_cal_error,
            cal_error,
            f"abs <= {max_abs_cal_error}",
            str(CALIBRATION_JSON),
        ),
        check(
            "candidate_not_worse_than_raw_v28",
            top_name == "v28_raw" or (top_brier is not None and raw_brier is not None and float(top_brier) < float(raw_brier)),
            {"top_variant": top_name, "top_brier": top_brier, "raw_brier": raw_brier},
            "top is raw v28 or strictly improves raw v28",
            str(VARIANTS_JSON),
        ),
        check(
            "broad_entry_policy_has_sample",
            best_policy_resolved >= min_observations,
            {"policy": best_policy_name, "resolved": best_policy_resolved},
            f"resolved >= {min_observations}",
            str(ENTRY_POLICY_JSON),
        ),
        check(
            "broad_entry_policy_reaches_coverage",
            best_policy_coverage is not None and float(best_policy_coverage) >= min_coverage,
            {"policy": best_policy_name, "coverage_pct": best_policy_coverage},
            f">= {min_coverage}%",
            str(ENTRY_POLICY_JSON),
        ),
        check(
            "broad_entry_policy_nonnegative",
            best_policy_gross >= min_gross and best_policy_losses <= max(1, int(best_policy_resolved * 0.45)),
            {"policy": best_policy_name, "gross_cents": best_policy_gross, "losses": best_policy_losses},
            "nonnegative gross and losses not dominant",
            str(ENTRY_POLICY_JSON),
        ),
    ]
    ready = all(item["passed"] for item in checks)
    return {
        "ready_for_promotion_review": ready,
        "reason": "all_checks_passed" if ready else "evidence_incomplete_or_failed",
        "checks": checks,
        "current_best_variant": top_name,
        "current_best_entry_policy": best_policy_name,
        "notes": [
            "This audit only permits review; it does not approve live deployment.",
            "Coverage is checked because the original goal asked for 75-80% market participation.",
            "The updated v28 mandate treats coverage as soft, but low coverage still needs explicit ROI justification.",
        ],
    }


def write_md(audit: dict[str, Any]) -> None:
    lines = [
        "# v28 Promotion Readiness",
        "",
        f"- Ready for promotion review: `{audit['ready_for_promotion_review']}`",
        f"- Reason: `{audit['reason']}`",
        f"- Current best variant: `{audit['current_best_variant']}`",
        f"- Current best entry policy: `{audit['current_best_entry_policy']}`",
        "",
        "## Checks",
        "",
        "| check | pass | actual | required | evidence |",
        "|---|---:|---|---|---|",
    ]
    for item in audit["checks"]:
        lines.append(
            f"| {item['name']} | {item['passed']} | `{item['actual']}` | `{item['required']}` | {item['evidence']} |"
        )
    lines.extend(["", "## Notes", ""])
    for note in audit["notes"]:
        lines.append(f"- {note}")
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    audit = build_audit()
    OUT_JSON.write_text(json.dumps(audit, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_md(audit)
    print(str(OUT_MD))


if __name__ == "__main__":
    main()
