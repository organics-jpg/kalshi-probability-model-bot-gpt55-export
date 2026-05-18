"""Conditional wait scan for v2 failure states.

The refreshed diagnostics suggest a timing problem:

- direct consensus candidates fix many v2 side failures;
- the same candidates lose edge when they wait on markets where v2 was already
  right and cheap.

This probe tests a tradable timing rule: take v2 immediately unless the first
v2 row has a simple instability flag; if flagged, skip v2 and wait for a later
book/Brownian consensus candidate in the same market.

Research-only: no orders are submitted and no bot files or live processes are
modified.
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

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


REPORT_MD = OUT_DIR / "v2_conditional_wait_scan_latest.md"
REPORT_JSON = OUT_DIR / "v2_conditional_wait_scan_latest.json"
REPORT_CSV = OUT_DIR / "v2_conditional_wait_scan_latest.csv"

CANDIDATE_LOCKS = {
    "book_margin": OUT_DIR / "profit_frontier_book_margin_lock.json",
    "score_min60": OUT_DIR / "profit_frontier_score_min60_lock.json",
}


@dataclass(frozen=True)
class WaitRule:
    candidate: str
    feature: str
    op: str
    threshold: float

    @property
    def label(self) -> str:
        return f"wait_for_{self.candidate}_if_v2_{self.feature}{self.op}{self.threshold:g}"


def clean_json_local(value: Any) -> Any:
    if isinstance(value, pd.Timestamp):
        return value.isoformat()
    if isinstance(value, dict):
        return {str(k): clean_json_local(v) for k, v in value.items()}
    if isinstance(value, list):
        return [clean_json_local(v) for v in value]
    return clean_json(value)


def load_policy(path: Path) -> Any:
    lock = json.loads(path.read_text(encoding="utf-8"))
    return policy_from_record(lock["policy"])


def select_policy(side_rows: pd.DataFrame, base: pd.DataFrame, path: Path) -> pd.DataFrame:
    policy = load_policy(path)
    rows = side_rows.merge(base[["market", "split"]], on="market", how="inner")
    chosen = choose_decision_sides(rows, policy.chooser)
    return enrich_selected(select_markets_from_chosen(chosen, policy))


def prepare_selected(side_rows: pd.DataFrame) -> tuple[pd.DataFrame, Dict[str, pd.DataFrame]]:
    base = market_base(side_rows)
    selected = {
        "frontier_v2": select_policy(side_rows, base, FRONTIER_V2_LOCK_PATH),
        **{name: select_policy(side_rows, base, path) for name, path in CANDIDATE_LOCKS.items()},
    }
    return base, selected


def make_rules(v2_rows: pd.DataFrame) -> List[WaitRule]:
    specs = [
        ("book_p_side", "<=", [0.50, 0.55, 0.60, 0.65, 0.70]),
        ("score_min_book_rv15", "<=", [0.55, 0.60, 0.65, 0.70, 0.75]),
        ("abs_book_rv15_gap", ">=", [0.05, 0.10, 0.15, 0.20, 0.25, 0.30]),
        ("adverse_move_15m", ">=", [25, 50, 75, 100, 125]),
        ("touch_loss_rv_15m", ">=", [0.50, 0.75, 1.00, 1.25]),
        ("ask_cents", ">=", [55, 60, 65, 70, 75, 80]),
        ("seconds_to_close", ">=", [600, 720, 840]),
    ]
    rules: List[WaitRule] = []
    for candidate in CANDIDATE_LOCKS:
        for feature, op, thresholds in specs:
            if feature not in v2_rows.columns:
                continue
            for threshold in thresholds:
                rules.append(WaitRule(candidate, feature, op, float(threshold)))
    return rules


def rule_mask(v2_rows: pd.DataFrame, rule: WaitRule) -> pd.Series:
    values = pd.to_numeric(v2_rows[rule.feature], errors="coerce")
    if rule.op == "<=":
        return values.le(rule.threshold).fillna(False)
    if rule.op == ">=":
        return values.ge(rule.threshold).fillna(False)
    raise ValueError(rule.op)


def apply_rule(v2_rows: pd.DataFrame, candidate_rows: pd.DataFrame, rule: WaitRule) -> pd.DataFrame:
    v2 = v2_rows.copy()
    candidate = candidate_rows.copy()
    wait_markets = set(v2.loc[rule_mask(v2, rule), "market"].astype(str))
    candidate["entry_dt"] = pd.to_datetime(candidate["entry_dt"], utc=True, errors="coerce")
    candidate_groups = {
        str(market): part.sort_values(["entry_dt", "market"]).copy()
        for market, part in candidate.groupby("market", sort=False)
    }
    rows: List[pd.Series] = []
    for _, row in v2.sort_values(["entry_dt", "market"]).iterrows():
        market = str(row["market"])
        if market in wait_markets and market in candidate_groups:
            trigger_dt = pd.to_datetime(row["entry_dt"], utc=True, errors="coerce")
            replacements = candidate_groups[market]
            if not pd.isna(trigger_dt):
                replacements = replacements[pd.to_datetime(replacements["entry_dt"], utc=True, errors="coerce").ge(trigger_dt)]
            if not replacements.empty:
                rows.append(replacements.iloc[0])
        elif market not in wait_markets:
            rows.append(row)
    if not rows:
        return v2.iloc[0:0].copy()
    selected = pd.DataFrame(rows).drop_duplicates(subset=["market"], keep="first")
    selected = selected.sort_values(["entry_dt", "market"]).reset_index(drop=True)
    selected["wait_rule"] = rule.label
    return selected


def coverage_pass(metrics: Dict[str, Dict[str, Any]]) -> bool:
    return (
        all((metrics[split]["coverage"] or 0.0) >= MARKET_COVERAGE_FLOOR for split in ["all", "train", "validation", "holdout"])
        and metrics["all"]["markets"] >= MIN_SELECTED_MARKETS
        and metrics["holdout"]["markets"] >= MIN_HOLDOUT_SELECTED_MARKETS
    )


def oos_positive(metrics: Dict[str, Dict[str, Any]]) -> bool:
    return all((metrics[split]["net_pnl_cents"] or 0.0) > 0.0 for split in ["validation", "holdout"])


def flatten(
    rule: WaitRule,
    current_metrics: Dict[str, Dict[str, Any]],
    v21_metrics: Dict[str, Dict[str, Any]],
    base_current: float,
    base_v21: float,
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
    row["current_delta_vs_v2_cents"] = (current_metrics["all"]["net_pnl_cents"] or 0.0) - base_current
    row["v21_delta_vs_v2_cents"] = (v21_metrics["all"]["net_pnl_cents"] or 0.0) - base_v21
    row["combined_delta_vs_v2_cents"] = row["current_delta_vs_v2_cents"] + row["v21_delta_vs_v2_cents"]
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


def write_report(generated: str, rows: pd.DataFrame, base_current: float, base_v21: float) -> None:
    top = rows[rows["both_coverage_pass"]].copy()
    top = top.sort_values(
        ["both_oos_positive", "combined_delta_vs_v2_cents", "min_oos_roi"],
        ascending=[False, False, False],
    ).head(20)
    lines = [
        "# V2 Conditional Wait Scan",
        "",
        f"Generated UTC: `{generated}`",
        "",
        "## Scope",
        "",
        "- Research-only scan; no orders are submitted and no bot files or live processes are touched.",
        "- Takes v2 unless the first v2 row shows a simple instability flag, then waits for a later consensus candidate.",
        "- Rules use only features visible on the first v2 row; later candidate rows are used only after the rule has committed to wait.",
        "",
        "## Baseline",
        "",
        f"- Current v2 baseline: {fmt_cents(base_current)}",
        f"- V21 v2 baseline: {fmt_cents(base_v21)}",
        "",
        "## Summary",
        "",
        f"- Wait rules scanned: {len(rows)}",
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
        lines.append("- No conditional wait rule preserved 80% coverage on both datasets.")
    else:
        best = top.iloc[0]
        lines.append(
            f"- Best conditional wait row: `{best['label']}` with current/v21 delta "
            f"{fmt_cents(best['current_delta_vs_v2_cents'])}/{fmt_cents(best['v21_delta_vs_v2_cents'])}."
        )
        if bool(best["both_oos_positive"]) and best["combined_delta_vs_v2_cents"] > 0:
            lines.append("- This is worth forward-lock consideration, not promotion.")
        else:
            lines.append("- No conditional wait rule beats v2 robustly enough to lock.")
    REPORT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    generated = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%SZ")
    current_base, current_selected = prepare_selected(load_side_rows())
    v21_base, v21_selected = prepare_selected(load_v21_side_rows())
    base_current = float(current_selected["frontier_v2"]["net_pnl_cents"].sum())
    base_v21 = float(v21_selected["frontier_v2"]["net_pnl_cents"].sum())
    rows: List[Dict[str, Any]] = []
    rules = make_rules(current_selected["frontier_v2"])
    for rule in rules:
        current_wait = enrich_selected(apply_rule(current_selected["frontier_v2"], current_selected[rule.candidate], rule))
        v21_wait = enrich_selected(apply_rule(v21_selected["frontier_v2"], v21_selected[rule.candidate], rule))
        rows.append(
            flatten(
                rule,
                metrics_for(current_base, current_wait),
                metrics_for(v21_base, v21_wait),
                base_current,
                base_v21,
            )
        )
    df = pd.DataFrame(rows)
    df.to_csv(REPORT_CSV, index=False)
    REPORT_JSON.write_text(
        json.dumps({"generated_utc": generated, "rows": clean_json_local(df.to_dict(orient="records"))}, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    write_report(generated, df, base_current, base_v21)
    print("V2 conditional wait scan complete")
    print(f"rules={len(df)} coverage_pass={int(df['both_coverage_pass'].sum())}")
    print(f"report={REPORT_MD}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
