"""Goal completion audit for the BTC 15m probability-model research thread.

This report maps the active objective to concrete evidence from strict
pre-registered forward monitors. It is intentionally conservative: if no lock
clears strict coverage, Wilson, Bayesian, and positive-P&L gates, the goal is
not complete.

Research-only: no orders are submitted and no bot files or live processes are
modified.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

import pandas as pd


OUT_DIR = Path("logs/edge_research")
REPORT_MD = OUT_DIR / "goal_completion_audit_latest.md"
REPORT_JSON = OUT_DIR / "goal_completion_audit_latest.json"

READINESS_CSV = OUT_DIR / "profit_lock_registered_signal_readiness_latest.csv"
DENOM_CSV = OUT_DIR / "profit_lock_market_denominator_audit_latest.csv"
BAYES_CSV = OUT_DIR / "profit_lock_bayesian_ev_monitor_latest.csv"
SAMPLE_CSV = OUT_DIR / "profit_lock_sample_size_requirements_latest.csv"
REGISTRY_CSV = OUT_DIR / "profit_lock_pending_signal_registry_latest.csv"

ROBUST_REPORTS = [
    OUT_DIR / "market_interval_80coverage_latest.md",
    OUT_DIR / "cross_dataset_profit_frontier_latest.md",
    OUT_DIR / "brownian70_candidate_robustness_audit_latest.md",
    OUT_DIR / "book_brownian_arbitration_audit_latest.md",
    OUT_DIR / "book_edge_gate_robustness_audit_latest.md",
    OUT_DIR / "book_cost_score_hole_audit_latest.md",
    OUT_DIR / "score_physics_guard_audit_latest.md",
    OUT_DIR / "signed_momentum_exhaustion_guard_audit_latest.md",
    OUT_DIR / "previous_outcome_state_guard_audit_latest.md",
    OUT_DIR / "vol_term_structure_guard_audit_latest.md",
    OUT_DIR / "probability_rolling_online_audit_latest.md",
    OUT_DIR / "probability_calibration_audit_latest.md",
    OUT_DIR / "probability_multifeature_logit_audit_latest.md",
    OUT_DIR / "frontier_candidate_v2_diagnostic_latest.md",
    OUT_DIR / "book_refmargin_score_switch_robustness_audit_latest.md",
    OUT_DIR / "book_margin_time_window_stability_scan_latest.md",
    OUT_DIR / "temporal_side_flip_diagnostic_latest.md",
    OUT_DIR / "hazard_mean_touch80_robustness_audit_latest.md",
    OUT_DIR / "hazard_pricecap_granular_frontier_latest.md",
    OUT_DIR / "hazard_trigger_persistence_frontier_latest.md",
    OUT_DIR / "impulse_reversal_regime_frontier_latest.md",
    OUT_DIR / "hazard_causal_threshold_stability_scan_latest.md",
    OUT_DIR / "hazard_primary_timeband_stability_scan_latest.md",
    OUT_DIR / "hazard_price_cap_stability_scan_latest.md",
    OUT_DIR / "logit_blend_threshold_robustness_audit_latest.md",
    OUT_DIR / "hazard_fallback_robustness_audit_latest.md",
]


def read_csv(path: Path) -> pd.DataFrame:
    if not path.exists():
        return pd.DataFrame()
    return pd.read_csv(path, low_memory=False)


def bool_series(series: pd.Series) -> pd.Series:
    return series.astype(str).str.lower().isin({"true", "1", "yes"})


def pct(value: Any) -> str:
    try:
        if pd.isna(value):
            return "NA"
        return f"{100.0 * float(value):.2f}%"
    except (TypeError, ValueError):
        return "NA"


def cents(value: Any) -> str:
    try:
        if pd.isna(value):
            return "NA"
        return f"{float(value):.1f}c"
    except (TypeError, ValueError):
        return "NA"


def top_rows(readiness: pd.DataFrame, n: int = 8) -> pd.DataFrame:
    if readiness.empty:
        return readiness
    work = readiness.copy()
    work["net_pnl_cents_num"] = pd.to_numeric(work.get("net_pnl_cents"), errors="coerce").fillna(-10**9)
    return work.sort_values("net_pnl_cents_num", ascending=False).head(n)


def robust_report_state(path: Path) -> Dict[str, Any]:
    if not path.exists():
        return {"path": str(path), "exists": False, "pass_hint": False}
    text = path.read_text(encoding="utf-8", errors="replace")
    lower = text.lower()
    pass_hint = "best robust diagnostic row" in lower and "no " not in lower[-500:]
    reject_hint = "no " in lower[-800:] and ("robust" in lower[-800:] or "clears" in lower[-800:])
    return {
        "path": str(path),
        "exists": True,
        "pass_hint": pass_hint,
        "reject_hint": reject_hint,
        "modified_utc": datetime.fromtimestamp(path.stat().st_mtime, tz=timezone.utc).isoformat(),
    }


def audit() -> Dict[str, Any]:
    readiness = read_csv(READINESS_CSV)
    denom = read_csv(DENOM_CSV)
    bayes = read_csv(BAYES_CSV)
    sample = read_csv(SAMPLE_CSV)
    registry = read_csv(REGISTRY_CSV)

    promotable = pd.DataFrame()
    if not readiness.empty:
        reg_ready = bool_series(readiness.get("registered_ready", pd.Series(False, index=readiness.index)))
        bayes_ready = bool_series(readiness.get("registered_bayesian_ready", pd.Series(False, index=readiness.index)))
        positive = pd.to_numeric(readiness.get("net_pnl_cents"), errors="coerce").fillna(0).gt(0)
        coverage = pd.to_numeric(readiness.get("registered_coverage"), errors="coerce").fillna(0).ge(0.80)
        promotable = readiness[reg_ready & bayes_ready & positive & coverage].copy()

    ready_count = int(len(promotable))
    top = top_rows(readiness)
    coverage_fail_count = 0
    if not denom.empty and "coverage_state" in denom.columns:
        coverage_fail_count = int(denom["coverage_state"].astype(str).str.lower().eq("fail").sum())

    pending_count = 0
    if not registry.empty and "outcome_available" in registry.columns:
        pending_count = int((~bool_series(registry["outcome_available"])).sum())

    return {
        "generated_utc": datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%SZ"),
        "files": {
            "readiness_csv": str(READINESS_CSV),
            "denominator_csv": str(DENOM_CSV),
            "bayes_csv": str(BAYES_CSV),
            "sample_csv": str(SAMPLE_CSV),
            "registry_csv": str(REGISTRY_CSV),
        },
        "counts": {
            "readiness_rows": int(len(readiness)),
            "denominator_rows": int(len(denom)),
            "bayesian_rows": int(len(bayes)),
            "sample_rows": int(len(sample)),
            "registry_rows": int(len(registry)),
            "pending_registry_rows": pending_count,
            "strict_promotable_rows": ready_count,
            "coverage_fail_rows": coverage_fail_count,
        },
        "top_rows": top.to_dict(orient="records") if not top.empty else [],
        "promotable_rows": promotable.to_dict(orient="records") if not promotable.empty else [],
        "robust_reports": [robust_report_state(path) for path in ROBUST_REPORTS],
        "complete": ready_count > 0,
    }


def write_report(payload: Dict[str, Any]) -> None:
    top = payload["top_rows"]
    lines: List[str] = [
        "# Goal Completion Audit",
        "",
        f"Generated UTC: `{payload['generated_utc']}`",
        "",
        "## Objective Restatement",
        "",
        "- Build a BTC 15m Kalshi fair-value/probability model with high accuracy and positive EV.",
        "- Maintain roughly 75-80%+ recurring-market coverage.",
        "- Use strict pre-registered live forward evidence with enough sample size.",
        "- Avoid validation-visible overfit and require cross-split/cross-dataset robustness for new physics priors.",
        "- Do not modify live bot logic, stop the live bot, or place trades.",
        "",
        "## Prompt-to-Artifact Checklist",
        "",
        "| requirement | evidence artifact | current evidence | status |",
        "|---|---|---|---|",
        f"| Strict pre-registered proof | `{payload['files']['readiness_csv']}` | strict promotable rows: {payload['counts']['strict_promotable_rows']} | fail |",
        f"| High recurring-market coverage | `{payload['files']['denominator_csv']}` | coverage-fail rows: {payload['counts']['coverage_fail_rows']}; top positive rows checked below | mixed |",
        f"| Bayesian confidence | `{payload['files']['bayes_csv']}` | no row clears readiness because strict promotable rows are 0 | fail |",
        f"| Wilson/sample-size proof | `{payload['files']['sample_csv']}` | no row clears completion-ready gate | fail |",
        f"| Forward registry current | `{payload['files']['registry_csv']}` | registry rows: {payload['counts']['registry_rows']}; pending: {payload['counts']['pending_registry_rows']} | pass |",
        "| Overfit controls | robustness reports listed below | no robust scan is promotion evidence without fresh strict validation | fail |",
        "| Live safety | process/error checks in thread | live bot/recorder/collector observed running; no trades submitted by these probes | pass |",
        "",
        "## Top Strict Rows",
        "",
        "| lock | reg/res/pending | wins/losses | acc | break-even | Wilson low | P(p>BE) | p05 edge | coverage | net | ready |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|",
    ]
    for row in top:
        lines.append(
            f"| `{row.get('name')}` | {row.get('registered')}/{row.get('resolved')}/{row.get('pending')} | "
            f"{row.get('wins')}/{row.get('losses')} | {pct(row.get('accuracy'))} | "
            f"{pct(row.get('break_even'))} | {pct(row.get('wilson95_lower'))} | "
            f"{float(row.get('prob_win_rate_gt_break_even', 0) or 0):.3f} | "
            f"{cents(row.get('posterior_p05_edge_cents'))} | {pct(row.get('registered_coverage'))} | "
            f"{cents(row.get('net_pnl_cents'))} | "
            f"{row.get('registered_ready')}/{row.get('registered_bayesian_ready')} |"
        )

    lines += [
        "",
        "## Robustness Reports",
        "",
        "| report | exists | read |",
        "|---|---|---|",
    ]
    for report in payload["robust_reports"]:
        if not report["exists"]:
            read = "missing"
        elif report.get("pass_hint"):
            read = "has robust-pass language, still needs fresh strict validation"
        elif report.get("reject_hint"):
            read = "rejects promotion under robustness gates"
        else:
            read = "diagnostic only"
        lines.append(f"| `{report['path']}` | {report['exists']} | {read} |")

    lines += [
        "",
        "## Completion Decision",
        "",
    ]
    if payload["complete"]:
        lines.append("- Complete: at least one strict pre-registered row clears all promotion gates.")
    else:
        lines.append("- Not complete: no strict pre-registered row clears the promotion gates.")
        lines.append("- Continue collecting forward samples and only lock new candidates after robustness evidence improves.")
    REPORT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    payload = audit()
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_JSON.write_text(json.dumps(payload, indent=2, sort_keys=True, default=str), encoding="utf-8")
    (OUT_DIR / f"goal_completion_audit_{payload['generated_utc']}.json").write_text(
        REPORT_JSON.read_text(encoding="utf-8"),
        encoding="utf-8",
    )
    write_report(payload)
    (OUT_DIR / f"goal_completion_audit_{payload['generated_utc']}.md").write_text(
        REPORT_MD.read_text(encoding="utf-8"),
        encoding="utf-8",
    )
    print("Goal completion audit complete")
    print(f"complete={payload['complete']}")
    print(f"strict_promotable_rows={payload['counts']['strict_promotable_rows']}")
    print(f"report={REPORT_MD}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
