"""Tradeable v2 veto scan.

This probe tests whether a simple one-feature veto can improve the high-volume
v2 frontier while preserving at least 80% market coverage. Unlike the path-flip
replacement diagnostic, a veto is tradable: if the row fails the veto, skip the
market.

Research-only: no orders are submitted and no bot files or live processes are
modified.
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Dict, List

import numpy as np
import pandas as pd

from probe_cross_dataset_interval_frontier import load_v21_side_rows
from probe_cross_dataset_profit_frontier import enrich_selected, fmt_cents, fmt_roi, metrics_for
from probe_market_interval_80coverage import (
    MARKET_COVERAGE_FLOOR,
    MIN_HOLDOUT_SELECTED_MARKETS,
    MIN_SELECTED_MARKETS,
    OUT_DIR,
    choose_decision_sides,
    clean_json,
    load_side_rows,
    market_base,
    pct,
    select_markets_from_chosen,
)
from probe_profit_frontier_fresh_validation import policy_from_record
from probe_profit_frontier_v2_fresh_validation import FRONTIER_V2_LOCK_PATH
from probe_profit_touch_hazard_frontier import add_touch_hazard_scores


REPORT_MD = OUT_DIR / "v2_tradeable_veto_scan_latest.md"
REPORT_JSON = OUT_DIR / "v2_tradeable_veto_scan_latest.json"
REPORT_CSV = OUT_DIR / "v2_tradeable_veto_scan_latest.csv"


@dataclass(frozen=True)
class VetoRule:
    feature: str
    op: str
    threshold: float

    @property
    def label(self) -> str:
        return f"{self.feature}{self.op}{self.threshold:g}"


def clean_json_local(value: Any) -> Any:
    if isinstance(value, pd.Timestamp):
        return value.isoformat()
    if isinstance(value, dict):
        return {str(k): clean_json_local(v) for k, v in value.items()}
    if isinstance(value, list):
        return [clean_json_local(v) for v in value]
    return clean_json(value)


def select_v2(side_rows: pd.DataFrame, base: pd.DataFrame) -> pd.DataFrame:
    lock = json.loads(FRONTIER_V2_LOCK_PATH.read_text(encoding="utf-8"))
    policy = policy_from_record(lock["policy"])
    rows = side_rows.merge(base[["market", "split"]], on="market", how="inner")
    chosen = choose_decision_sides(rows, policy.chooser)
    return enrich_selected(select_markets_from_chosen(chosen, policy))


def make_rules(selected: pd.DataFrame) -> List[VetoRule]:
    specs = [
        ("ask_cents", "<=", [55, 60, 65, 70, 75, 80, 85, 90]),
        ("seconds_to_close", "<=", [840, 780, 720, 660, 600, 540, 480]),
        ("seconds_to_close", ">=", [240, 300, 360, 420, 480, 540, 600]),
        ("brownian_p_rv_15m", ">=", [0.55, 0.60, 0.65, 0.70, 0.75]),
        ("brownian_p_rv_30m", ">=", [0.55, 0.60, 0.65, 0.70, 0.75]),
        ("book_p_side", ">=", [0.50, 0.55, 0.60, 0.65, 0.70]),
        ("score_mean_book_rv15", ">=", [0.55, 0.60, 0.65, 0.70, 0.75]),
        ("score_min_book_rv15", ">=", [0.50, 0.55, 0.60, 0.65, 0.70]),
        ("adverse_move_15m", "<=", [0, 10, 25, 50, 75, 100]),
        ("touch_loss_rv_15m", "<=", [0.25, 0.50, 0.75, 1.00, 1.25]),
        ("touch_survival_rv_15m", ">=", [0.25, 0.35, 0.45, 0.55, 0.65]),
        ("kinetic_touch_score_15", ">=", [0.45, 0.50, 0.55, 0.60, 0.65]),
        ("spread_cents", "<=", [0, 1, 2, 3, 4, 5]),
    ]
    rules: List[VetoRule] = [VetoRule("none", ">=", 0.0)]
    for feature, op, thresholds in specs:
        if feature not in selected.columns:
            continue
        for threshold in thresholds:
            rules.append(VetoRule(feature, op, float(threshold)))
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


def flatten(rule: VetoRule, current: Dict[str, Dict[str, Any]], v21: Dict[str, Dict[str, Any]], base_current: float, base_v21: float) -> Dict[str, Any]:
    row: Dict[str, Any] = {
        "label": rule.label,
        "feature": rule.feature,
        "op": rule.op,
        "threshold": rule.threshold,
        "current_coverage_pass": coverage_pass(current),
        "v21_coverage_pass": coverage_pass(v21),
        "both_coverage_pass": coverage_pass(current) and coverage_pass(v21),
        "current_oos_positive": oos_positive(current),
        "v21_oos_positive": oos_positive(v21),
        "both_oos_positive": oos_positive(current) and oos_positive(v21),
    }
    row["current_delta_vs_v2_cents"] = (current["all"]["net_pnl_cents"] or 0.0) - base_current
    row["v21_delta_vs_v2_cents"] = (v21["all"]["net_pnl_cents"] or 0.0) - base_v21
    row["combined_delta_vs_v2_cents"] = row["current_delta_vs_v2_cents"] + row["v21_delta_vs_v2_cents"]
    row["min_oos_roi"] = min(
        current["validation"]["net_roi_on_cost"] or -1.0,
        current["holdout"]["net_roi_on_cost"] or -1.0,
        v21["validation"]["net_roi_on_cost"] or -1.0,
        v21["holdout"]["net_roi_on_cost"] or -1.0,
    )
    for prefix, metrics in [("current", current), ("v21", v21)]:
        for split, values in metrics.items():
            for key, value in values.items():
                row[f"{prefix}_{split}_{key}"] = value
    return row


def write_report(generated: str, rows: pd.DataFrame, base_current: float, base_v21: float) -> None:
    top = rows[rows["both_coverage_pass"]].copy()
    top = top.sort_values(["both_oos_positive", "combined_delta_vs_v2_cents", "min_oos_roi"], ascending=[False, False, False]).head(20)
    lines: List[str] = [
        "# V2 Tradeable Veto Scan",
        "",
        f"Generated UTC: `{generated}`",
        "",
        "## Scope",
        "",
        "- Research-only scan; no orders are submitted and no bot files or live processes are touched.",
        "- Tests one-feature abstention rules on top of v2 while preserving >=80% coverage.",
        "- This is diagnostic; any winner needs a forward lock and strict pre-resolution validation.",
        "",
        "## Baseline",
        "",
        f"- Current v2 baseline: {fmt_cents(base_current)}",
        f"- V21 v2 baseline: {fmt_cents(base_v21)}",
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
            f"{fmt_cents(row['current_delta_vs_v2_cents'])}/{fmt_cents(row['v21_delta_vs_v2_cents'])} | "
            f"{fmt_cents(row['current_all_net_pnl_cents'])}/{pct(row['current_all_accuracy'])}/{pct(row['current_all_coverage'])} | "
            f"{fmt_cents(row['v21_all_net_pnl_cents'])}/{pct(row['v21_all_accuracy'])}/{pct(row['v21_all_coverage'])} | "
            f"{fmt_roi(row['min_oos_roi'])} |"
        )
    lines += ["", "## Read", ""]
    if top.empty:
        lines.append("- No one-feature veto preserved 80% coverage on both datasets.")
    else:
        best = top.iloc[0]
        lines.append(
            f"- Best veto row: `{best['label']}` with current/v21 delta "
            f"{fmt_cents(best['current_delta_vs_v2_cents'])}/{fmt_cents(best['v21_delta_vs_v2_cents'])}."
        )
        if bool(best["both_oos_positive"]) and best["combined_delta_vs_v2_cents"] > 0:
            lines.append("- Candidate is worth forward-lock consideration, not promotion.")
        else:
            lines.append("- No veto improves v2 robustly enough to lock.")
    REPORT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    generated = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%SZ")
    current_side = add_touch_hazard_scores(load_side_rows())
    v21_side = add_touch_hazard_scores(load_v21_side_rows())
    current_base = market_base(current_side)
    v21_base = market_base(v21_side)
    current_v2 = select_v2(current_side, current_base)
    v21_v2 = select_v2(v21_side, v21_base)
    base_current = float(current_v2["net_pnl_cents"].sum())
    base_v21 = float(v21_v2["net_pnl_cents"].sum())
    all_rules = make_rules(current_v2)
    rows: List[Dict[str, Any]] = []
    for rule in all_rules:
        current_selected = apply_rule(current_v2, rule)
        v21_selected = apply_rule(v21_v2, rule)
        rows.append(flatten(rule, metrics_for(current_base, current_selected), metrics_for(v21_base, v21_selected), base_current, base_v21))
    df = pd.DataFrame(rows)
    df.to_csv(REPORT_CSV, index=False)
    REPORT_JSON.write_text(
        json.dumps({"generated_utc": generated, "rows": clean_json_local(df.to_dict(orient="records"))}, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    write_report(generated, df, base_current, base_v21)
    print("V2 tradeable veto scan complete")
    print(f"rules={len(df)} coverage_pass={int(df['both_coverage_pass'].sum())}")
    print(f"report={REPORT_MD}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
