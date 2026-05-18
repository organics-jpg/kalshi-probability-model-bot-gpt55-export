"""FV-model readiness report for the active v28 improvement goal.

This is intentionally separate from live-trade readiness. It asks whether a
candidate fair-value model has enough forward evidence to be considered a real
model improvement, while live-trade readiness also depends on execution, risk
stops, account state, and operational gates.

Research-only; no live bot changes or orders.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
FROZEN_CALIBRATION_JSON = OUT_DIR / "v28_frozen_raw_entry_calibrated_probability_latest.json"
CALIBRATION_DISCOVERY_JSON = OUT_DIR / "v28_raw_entry_calibrated_probability_latest.json"
POSTERIOR_BUCKET_JSON = OUT_DIR / "v28_entry_conditioned_posterior_diagnostic_latest.json"
LIFT_PLATEAU_JSON = OUT_DIR / "v28_entry_conditioned_lift_plateau_latest.json"
JACKKNIFE_JSON = OUT_DIR / "v28_entry_conditioned_jackknife_latest.json"
DATA_QUALITY_JSON = OUT_DIR / "v28_entry_conditioned_data_quality_latest.json"
SEQUENTIAL_EVIDENCE_JSON = OUT_DIR / "v28_calibrated_fv_sequential_evidence_latest.json"
PATH_CONTRADICTION_JSON = OUT_DIR / "v28_calibrated_fv_path_contradiction_latest.json"
FROZEN_LEADERBOARD_JSON = OUT_DIR / "v28_frozen_candidate_leaderboard_latest.json"
OUT_JSON = OUT_DIR / "v28_fv_model_readiness_latest.json"
OUT_MD = OUT_DIR / "v28_fv_model_readiness_latest.md"


def load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
    return payload if isinstance(payload, dict) else {}


def row_by_name(rows: list[dict[str, Any]], key: str, value: str) -> dict[str, Any]:
    for row in rows:
        if str(row.get(key) or "") == value:
            return row
    return {}


def candidate_blockers(
    frozen_row: dict[str, Any],
    discovery_row: dict[str, Any],
    frozen_payload: dict[str, Any],
    data_quality: dict[str, Any],
    path_contradiction: dict[str, Any],
) -> list[str]:
    blockers: list[str] = []
    settled = float(frozen_row.get("settled") or frozen_row.get("count") or 0.0)
    coverage = frozen_row.get("coverage_pct")
    if settled < 30:
        blockers.append("forward_settled_lt_30")
    if coverage is None or float(coverage) < 70.0:
        blockers.append("forward_coverage_too_low")
    if coverage is not None and float(coverage) > 90.0:
        blockers.append("forward_coverage_too_high")
    if frozen_row.get("brier_delta_vs_raw") is None or float(frozen_row.get("brier_delta_vs_raw") or 0.0) >= 0.0:
        blockers.append("forward_brier_not_better_than_raw")
    if frozen_row.get("logloss_delta_vs_raw") is None or float(frozen_row.get("logloss_delta_vs_raw") or 0.0) >= 0.0:
        blockers.append("forward_logloss_not_better_than_raw")
    if frozen_row.get("bucket_stability_failures"):
        blockers.append("forward_bucket_failure")
    if not discovery_row:
        blockers.append("missing_discovery_baseline")
    if not frozen_payload.get("freeze_ts"):
        blockers.append("missing_freeze_timestamp")
    if data_quality.get("data_quality_pass") is not True:
        blockers.append("data_quality_not_passing")
    if float(path_contradiction.get("settled_later_opposite_selected_losses") or 0.0) > 0.0:
        blockers.append("forward_path_contradiction_loss")
    if float(path_contradiction.get("later_opposite_approval_rows") or 0.0) > 0.0 and float(path_contradiction.get("settled_later_opposite_approval_rows") or 0.0) < 5.0:
        blockers.append("forward_path_contradiction_sample_lt_5")
    return blockers


def build_report() -> dict[str, Any]:
    frozen = load_json(FROZEN_CALIBRATION_JSON)
    discovery = load_json(CALIBRATION_DISCOVERY_JSON)
    bucket_diag = load_json(POSTERIOR_BUCKET_JSON)
    plateau = load_json(LIFT_PLATEAU_JSON)
    jackknife = load_json(JACKKNIFE_JSON)
    data_quality = load_json(DATA_QUALITY_JSON)
    sequential = load_json(SEQUENTIAL_EVIDENCE_JSON)
    path_contradiction = load_json(PATH_CONTRADICTION_JSON)
    leaderboard = load_json(FROZEN_LEADERBOARD_JSON)

    frozen_ranked = frozen.get("ranked") if isinstance(frozen.get("ranked"), list) else []
    discovery_ranked = discovery.get("ranked") if isinstance(discovery.get("ranked"), list) else []
    plus05_frozen = row_by_name(frozen_ranked, "overlay", "entry_conditioned_plus05_probability")
    plus05_discovery = row_by_name(discovery_ranked, "overlay", "entry_conditioned_plus05_probability")
    raw_frozen = row_by_name(frozen_ranked, "overlay", "raw_probability")
    raw_discovery = row_by_name(discovery_ranked, "overlay", "raw_probability")
    blockers = candidate_blockers(plus05_frozen, plus05_discovery, frozen, data_quality, path_contradiction)

    weak_buckets = bucket_diag.get("plus05_weak_buckets") or []
    improving_lifts = plateau.get("improving_lift_pp") or []

    return {
        "candidate": {
            "name": "v28_raw_entry_conditioned_plus05_fv",
            "entry_surface": "v28_raw_p50_edge0_fixed_selection",
            "fv_probability": "clamp(raw_v28_probability + 0.05)",
            "intent": "Keep broad raw-v28 entry participation while improving FV calibration for selected entries.",
            "physics_argument": [
                "Clearing a positive executable edge gate is itself conditional evidence.",
                "The selected-entry slice is underconfident, so shrinkage toward 50 is the wrong direction there.",
                "+5pp is conservative inside a broad positive-lift discovery plateau, not the discovered optimum.",
            ],
        },
        "discovery": {
            "raw": raw_discovery,
            "plus05": plus05_discovery,
            "weak_buckets": weak_buckets,
            "improving_lift_pp": improving_lifts,
            "best_lift_pp": plateau.get("best_lift_pp"),
            "jackknife_pass": jackknife.get("jackknife_pass"),
            "jackknife_failure_count": jackknife.get("failure_count"),
            "jackknife_full_sample": jackknife.get("full_sample"),
            "data_quality_pass": data_quality.get("data_quality_pass"),
            "data_quality_flag_counts": data_quality.get("flag_counts"),
            "sequential_evidence_status": sequential.get("evidence_status"),
            "sequential_evidence_blockers": sequential.get("blockers"),
            "sequential_settled_rows": sequential.get("settled_rows"),
        },
        "frozen_forward": {
            "freeze_ts": frozen.get("freeze_ts"),
            "forward_market_denominator": frozen.get("forward_market_denominator"),
            "future_entry_rows": frozen.get("future_entry_rows"),
            "raw": raw_frozen,
            "plus05": plus05_frozen,
            "future_entry_details": frozen.get("future_entry_details") or [],
        },
        "path_contradiction": path_contradiction,
        "leaderboard_context": {
            "top_forward_rows": (leaderboard.get("ranked") or [])[:5],
        },
        "readiness": {
            "fv_model_ready": not blockers,
            "blockers": blockers,
            "promotion_requirements": [
                "at least 30 settled forward selected entries",
                "70-90% forward coverage",
                "forward Brier and logloss improve versus raw probability",
                "no eligible physics bucket has worse Brier than raw",
                "frozen timestamp exists before counted rows",
                "data-quality audit passes",
                "no unresolved or losing later-opposite v28 approval path contradiction",
            ],
        },
    }


def fmt(value: Any) -> str:
    if value is None:
        return "None"
    if isinstance(value, float):
        return f"{value:.6f}"
    return str(value)


def write_md(report: dict[str, Any]) -> None:
    candidate = report["candidate"]
    readiness = report["readiness"]
    discovery = report["discovery"]
    frozen = report["frozen_forward"]
    path_contradiction = report.get("path_contradiction") or {}
    lines = [
        "# v28 FV Model Readiness",
        "",
        f"- Candidate: `{candidate['name']}`",
        f"- Entry surface: `{candidate['entry_surface']}`",
        f"- FV probability: `{candidate['fv_probability']}`",
        f"- FV model ready: `{readiness['fv_model_ready']}`",
        f"- Blockers: `{', '.join(readiness['blockers']) or 'none'}`",
        "",
        "## Physics Argument",
        "",
    ]
    for item in candidate["physics_argument"]:
        lines.append(f"- {item}")
    raw_d = discovery.get("raw") or {}
    plus_d = discovery.get("plus05") or {}
    lines.extend([
        "",
        "## Discovery Slice",
        "",
        f"- Raw Brier/logloss/ECE: `{fmt(raw_d.get('avg_brier'))}` / `{fmt(raw_d.get('avg_logloss'))}` / `{fmt(raw_d.get('ece_10bucket'))}`",
        f"- +5pp Brier/logloss/ECE: `{fmt(plus_d.get('avg_brier'))}` / `{fmt(plus_d.get('avg_logloss'))}` / `{fmt(plus_d.get('ece_10bucket'))}`",
        f"- +5pp deltas: Brier `{fmt(plus_d.get('brier_delta_vs_raw'))}`, logloss `{fmt(plus_d.get('logloss_delta_vs_raw'))}`, ECE `{fmt(plus_d.get('ece_delta_vs_raw'))}`",
        f"- Weak buckets: `{discovery.get('weak_buckets')}`",
        f"- Improving lift plateau: `{discovery.get('improving_lift_pp')}`; best discovery lift `{discovery.get('best_lift_pp')}pp`",
        f"- Jackknife pass/failures: `{discovery.get('jackknife_pass')}` / `{discovery.get('jackknife_failure_count')}`",
        f"- Data-quality pass/flags: `{discovery.get('data_quality_pass')}` / `{discovery.get('data_quality_flag_counts')}`",
        f"- Sequential evidence status/rows/blockers: `{discovery.get('sequential_evidence_status')}` / `{discovery.get('sequential_settled_rows')}` / `{discovery.get('sequential_evidence_blockers')}`",
        "",
        "## Frozen Forward",
        "",
        f"- Freeze timestamp UTC: `{frozen.get('freeze_ts')}`",
        f"- Forward market denominator: `{frozen.get('forward_market_denominator')}`",
        f"- Future entry rows: `{frozen.get('future_entry_rows')}`",
    ])
    plus_f = frozen.get("plus05") or {}
    raw_f = frozen.get("raw") or {}
    lines.extend([
        f"- Raw forward Brier/logloss: `{fmt(raw_f.get('avg_brier'))}` / `{fmt(raw_f.get('avg_logloss'))}`",
        f"- +5pp forward Brier/logloss: `{fmt(plus_f.get('avg_brier'))}` / `{fmt(plus_f.get('avg_logloss'))}`",
        f"- +5pp forward blockers: `{', '.join(plus_f.get('blockers') or []) or 'none'}`",
        f"- Path contradiction rows/losses: `{path_contradiction.get('later_opposite_approval_rows')}/{path_contradiction.get('settled_later_opposite_selected_losses')}`",
        "",
        "## Forward Rows",
        "",
    ])
    details = frozen.get("future_entry_details") or []
    if not details:
        lines.append("none")
    else:
        lines.append("| market | side | p raw | ask | edge | won | net c |")
        lines.append("|---|---|---:|---:|---:|---|---:|")
        for row in details:
            lines.append(
                f"| {row.get('market')} | {row.get('side')} | {fmt(row.get('p_side'))} | "
                f"{fmt(row.get('ask_prob'))} | {fmt(row.get('raw_edge_prob'))} | "
                f"{row.get('side_won')} | {fmt(row.get('net_gross_cents_after_entry_fee'))} |"
            )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    report = build_report()
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8")
    write_md(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
