"""Tradeable veto scan for locked high-coverage candidates.

The refreshed candidates are promising but have supported losing slices. This
probe asks whether a simple one-feature veto can improve each locked candidate
while preserving at least 80% recurring-market coverage on both the current and
v21 ledgers.

Research-only: no orders are submitted and no bot files or live processes are
modified. Any passing row is only a forward-test candidate.
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Dict, List

import pandas as pd

from probe_cross_dataset_interval_frontier import load_v21_side_rows
from probe_cross_dataset_profit_frontier import enrich_selected, fmt_cents, fmt_roi, metrics_for
from probe_frontier_candidate_v2_diagnostic import select_policy as select_locked_policy
from probe_market_interval_80coverage import (
    MARKET_COVERAGE_FLOOR,
    MIN_HOLDOUT_SELECTED_MARKETS,
    MIN_SELECTED_MARKETS,
    OUT_DIR,
    clean_json,
    load_side_rows,
    market_base,
    pct,
)
from probe_v2_conditional_wait_forward_validation import (
    CONDITIONAL_WAIT_LOCK_PATH,
    ensure_lock as ensure_conditional_wait_lock,
    select_for_validation as select_conditional_wait_for_validation,
)


REPORT_MD = OUT_DIR / "candidate_tradeable_veto_scan_latest.md"
REPORT_JSON = OUT_DIR / "candidate_tradeable_veto_scan_latest.json"
REPORT_CSV = OUT_DIR / "candidate_tradeable_veto_scan_latest.csv"

CANDIDATES = ["book_margin", "score_min60", "v2_wait_score_min60_early"]


@dataclass(frozen=True)
class VetoRule:
    candidate: str
    feature: str
    op: str
    threshold: float

    @property
    def label(self) -> str:
        if self.feature == "none":
            return f"{self.candidate}: none"
        return f"{self.candidate}: {self.feature}{self.op}{self.threshold:g}"


def clean_json_local(value: Any) -> Any:
    if isinstance(value, pd.Timestamp):
        return value.isoformat()
    if isinstance(value, dict):
        return {str(k): clean_json_local(v) for k, v in value.items()}
    if isinstance(value, list):
        return [clean_json_local(v) for v in value]
    return clean_json(value)


def prepare_selected(side_rows: pd.DataFrame) -> tuple[pd.DataFrame, Dict[str, pd.DataFrame]]:
    base = market_base(side_rows)
    selected = {
        "book_margin": select_locked_policy(side_rows, base, "book_margin"),
        "score_min60": select_locked_policy(side_rows, base, "score_min60"),
    }
    if not CONDITIONAL_WAIT_LOCK_PATH.exists():
        ensure_conditional_wait_lock(side_rows)
    lock = json.loads(CONDITIONAL_WAIT_LOCK_PATH.read_text(encoding="utf-8"))
    selected["v2_wait_score_min60_early"] = select_conditional_wait_for_validation(side_rows, base, lock)
    return base, selected


def make_rules(candidate: str, selected: pd.DataFrame) -> List[VetoRule]:
    specs = [
        ("ask_cents", "<=", [55, 60, 65, 70, 75, 80, 85, 90]),
        ("seconds_to_close", ">=", [240, 360, 480, 600, 720, 840]),
        ("seconds_to_close", "<=", [840, 780, 720, 660, 600, 540, 480]),
        ("book_p_side", ">=", [0.55, 0.60, 0.65, 0.70]),
        ("brownian_p_rv_15m", ">=", [0.55, 0.60, 0.65, 0.70]),
        ("brownian_p_rv_30m", ">=", [0.55, 0.60, 0.65, 0.70]),
        ("score_min_book_rv15", ">=", [0.55, 0.60, 0.65, 0.70]),
        ("abs_book_rv15_gap", "<=", [0.05, 0.10, 0.15, 0.20, 0.25, 0.30]),
        ("adverse_move_15m", "<=", [0, 10, 25, 50, 75, 100, 125]),
        ("touch_loss_rv_15m", "<=", [0.50, 0.75, 1.00, 1.25]),
        ("spread_cents", "<=", [1, 2, 3, 4, 5]),
    ]
    rules = [VetoRule(candidate, "none", ">=", 0.0)]
    for feature, op, thresholds in specs:
        if feature not in selected.columns:
            continue
        for threshold in thresholds:
            rules.append(VetoRule(candidate, feature, op, float(threshold)))
    return rules


def apply_rule(selected: pd.DataFrame, rule: VetoRule) -> pd.DataFrame:
    if rule.feature == "none":
        return selected.copy()
    values = pd.to_numeric(selected[rule.feature], errors="coerce")
    if rule.op == "<=":
        return selected[values.le(rule.threshold)].copy()
    if rule.op == ">=":
        return selected[values.ge(rule.threshold)].copy()
    raise ValueError(rule.op)


def coverage_pass(metrics: Dict[str, Dict[str, Any]]) -> bool:
    return (
        all((metrics[split]["coverage"] or 0.0) >= MARKET_COVERAGE_FLOOR for split in ["all", "train", "validation", "holdout"])
        and metrics["all"]["markets"] >= MIN_SELECTED_MARKETS
        and metrics["holdout"]["markets"] >= MIN_HOLDOUT_SELECTED_MARKETS
    )


def oos_positive(metrics: Dict[str, Dict[str, Any]]) -> bool:
    return all((metrics[split]["net_pnl_cents"] or 0.0) > 0.0 for split in ["validation", "holdout"])


def flatten(
    rule: VetoRule,
    current_metrics: Dict[str, Dict[str, Any]],
    v21_metrics: Dict[str, Dict[str, Any]],
    base_current_net: float,
    base_v21_net: float,
) -> Dict[str, Any]:
    row: Dict[str, Any] = {
        "label": rule.label,
        "candidate": rule.candidate,
        "feature": rule.feature,
        "op": rule.op,
        "threshold": rule.threshold,
        "current_coverage_pass": coverage_pass(current_metrics),
        "v21_coverage_pass": coverage_pass(v21_metrics),
        "both_coverage_pass": coverage_pass(current_metrics) and coverage_pass(v21_metrics),
        "current_oos_positive": oos_positive(current_metrics),
        "v21_oos_positive": oos_positive(v21_metrics),
        "both_oos_positive": oos_positive(current_metrics) and oos_positive(v21_metrics),
    }
    row["current_delta_vs_candidate_cents"] = (current_metrics["all"]["net_pnl_cents"] or 0.0) - base_current_net
    row["v21_delta_vs_candidate_cents"] = (v21_metrics["all"]["net_pnl_cents"] or 0.0) - base_v21_net
    row["combined_delta_vs_candidate_cents"] = row["current_delta_vs_candidate_cents"] + row["v21_delta_vs_candidate_cents"]
    row["min_oos_roi"] = min(
        current_metrics["validation"]["net_roi_on_cost"] or -1.0,
        current_metrics["holdout"]["net_roi_on_cost"] or -1.0,
        v21_metrics["validation"]["net_roi_on_cost"] or -1.0,
        v21_metrics["holdout"]["net_roi_on_cost"] or -1.0,
    )
    for prefix, metrics in [("current", current_metrics), ("v21", v21_metrics)]:
        for split, values in metrics.items():
            for key, value in values.items():
                row[f"{prefix}_{split}_{key}"] = value
    return row


def write_report(generated: str, rows: pd.DataFrame) -> None:
    top = rows[rows["both_coverage_pass"]].copy()
    top = top.sort_values(
        ["both_oos_positive", "combined_delta_vs_candidate_cents", "min_oos_roi"],
        ascending=[False, False, False],
    ).head(25)
    lines = [
        "# Candidate Tradeable Veto Scan",
        "",
        f"Generated UTC: `{generated}`",
        "",
        "## Scope",
        "",
        "- Research-only scan; no orders are submitted and no bot files or live processes are touched.",
        "- Tests one-feature vetoes on locked high-coverage candidates while preserving >=80% recurring-market coverage.",
        "- Any apparent winner still needs forward registration and live sample size.",
        "",
        "## Summary",
        "",
        f"- Rules scanned: {len(rows)}",
        f"- Both-dataset 80% coverage rules: {int(rows['both_coverage_pass'].sum())}",
        f"- Both-dataset OOS-positive rules: {int((rows['both_coverage_pass'] & rows['both_oos_positive']).sum())}",
        "",
        "## Top Rows",
        "",
        "| rank | rule | delta current/v21 | current net/acc/cov | v21 net/acc/cov | OOS ROI floor |",
        "|---:|---|---:|---:|---:|---:|",
    ]
    for rank, (_, row) in enumerate(top.iterrows(), start=1):
        lines.append(
            f"| {rank} | `{row['label']}` | "
            f"{fmt_cents(row['current_delta_vs_candidate_cents'])}/{fmt_cents(row['v21_delta_vs_candidate_cents'])} | "
            f"{fmt_cents(row['current_all_net_pnl_cents'])}/{pct(row['current_all_accuracy'])}/{pct(row['current_all_coverage'])} | "
            f"{fmt_cents(row['v21_all_net_pnl_cents'])}/{pct(row['v21_all_accuracy'])}/{pct(row['v21_all_coverage'])} | "
            f"{fmt_roi(row['min_oos_roi'])} |"
        )
    lines += ["", "## Read", ""]
    if top.empty:
        lines.append("- No veto preserved 80% coverage on both datasets.")
    else:
        best = top.iloc[0]
        lines.append(
            f"- Best veto row: `{best['label']}` with current/v21 delta "
            f"{fmt_cents(best['current_delta_vs_candidate_cents'])}/{fmt_cents(best['v21_delta_vs_candidate_cents'])}."
        )
        if bool(best["both_oos_positive"]) and best["combined_delta_vs_candidate_cents"] > 0:
            lines.append("- Worth forward-lock consideration only if the rule is physically interpretable and live coverage remains high.")
        else:
            lines.append("- No simple veto improves the candidates robustly enough to lock.")
    REPORT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    generated = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%SZ")
    current_base, current_selected = prepare_selected(load_side_rows())
    v21_base, v21_selected = prepare_selected(load_v21_side_rows())
    rows: List[Dict[str, Any]] = []
    for candidate in CANDIDATES:
        base_current_net = float(enrich_selected(current_selected[candidate])["net_pnl_cents"].sum())
        base_v21_net = float(enrich_selected(v21_selected[candidate])["net_pnl_cents"].sum())
        rules = make_rules(candidate, current_selected[candidate])
        for rule in rules:
            current_rule = enrich_selected(apply_rule(current_selected[candidate], rule))
            v21_rule = enrich_selected(apply_rule(v21_selected[candidate], rule))
            rows.append(flatten(rule, metrics_for(current_base, current_rule), metrics_for(v21_base, v21_rule), base_current_net, base_v21_net))
    df = pd.DataFrame(rows)
    df.to_csv(REPORT_CSV, index=False)
    REPORT_JSON.write_text(
        json.dumps({"generated_utc": generated, "rows": clean_json_local(df.to_dict(orient="records"))}, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    write_report(generated, df)
    print("Candidate tradeable veto scan complete")
    print(f"rules={len(df)} coverage_pass={int(df['both_coverage_pass'].sum())}")
    print(f"report={REPORT_MD}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
