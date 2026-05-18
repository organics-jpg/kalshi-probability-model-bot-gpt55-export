"""Delayed-entry path-veto scan for leading high-coverage BTC 15m locks.

The existing veto scans apply path filters to the first selected row and skip
the market if that row fails. This probe tests a different, still causal,
physics rule: wait within the same market until the locked book-margin policy
is eligible and the path-pressure clause is satisfied.

Research-only: no orders are submitted and no bot files or live processes are
modified. Passing rows are diagnostic candidates only; strict pre-resolution
forward registration is still required before any promotion.
"""
from __future__ import annotations

import json
import math
from dataclasses import dataclass
from datetime import datetime, timezone
from itertools import combinations
from typing import Any, Dict, List

import pandas as pd

from probe_cross_dataset_interval_frontier import load_v21_side_rows
from probe_cross_dataset_profit_frontier import enrich_selected, fmt_cents, fmt_roi, metrics_for
from probe_frontier_candidate_v2_diagnostic import load_lock, load_lock_policy, select_policy as select_locked_policy
from probe_market_interval_80coverage import (
    MARKET_COVERAGE_FLOOR,
    MIN_HOLDOUT_SELECTED_MARKETS,
    MIN_SELECTED_MARKETS,
    OUT_DIR,
    choose_decision_sides,
    clean_json,
    gate_mask,
    load_side_rows,
    market_base,
    pct,
)
from probe_candidate_tradeable_pair_veto_scan import block_stability


REPORT_MD = OUT_DIR / "candidate_tradeable_delayed_path_veto_scan_latest.md"
REPORT_JSON = OUT_DIR / "candidate_tradeable_delayed_path_veto_scan_latest.json"
REPORT_CSV = OUT_DIR / "candidate_tradeable_delayed_path_veto_scan_latest.csv"

CANDIDATES = ["book_margin", "book_margin_early"]
MIN_POS_COV_BLOCK_RATE = 0.75
MIN_OOS_ROI = 0.0
PATH_FEATURES = {"adverse_move_15m", "signed_move_5m", "signed_move_15m"}


@dataclass(frozen=True)
class Clause:
    feature: str
    op: str
    threshold: float

    @property
    def label(self) -> str:
        return f"{self.feature}{self.op}{self.threshold:g}"

    def keep(self, rows: pd.DataFrame) -> pd.Series:
        if self.feature not in rows.columns:
            return pd.Series(False, index=rows.index)
        values = pd.to_numeric(rows[self.feature], errors="coerce")
        if self.op == "<=":
            return values.le(self.threshold).fillna(False)
        if self.op == ">=":
            return values.ge(self.threshold).fillna(False)
        raise ValueError(self.op)


@dataclass(frozen=True)
class DelayRule:
    candidate: str
    clauses: tuple[Clause, ...]

    @property
    def label(self) -> str:
        if not self.clauses:
            return f"{self.candidate}: no extra delay clause"
        return f"{self.candidate}: wait until " + " AND ".join(clause.label for clause in self.clauses)


def clean_json_local(value: Any) -> Any:
    if isinstance(value, pd.Timestamp):
        return value.isoformat()
    if isinstance(value, dict):
        return {str(k): clean_json_local(v) for k, v in value.items()}
    if isinstance(value, list):
        return [clean_json_local(v) for v in value]
    return clean_json(value)


def make_clauses(rows: pd.DataFrame) -> List[Clause]:
    specs = [
        ("adverse_move_15m", "<=", [0, 10, 25, 50, 75, 100, 150]),
        ("signed_move_5m", ">=", [-10, 0, 10]),
        ("signed_move_15m", ">=", [-50, 0, 50]),
        ("abs_book_rv15_gap", "<=", [0.10, 0.15, 0.20, 0.30]),
        ("brownian_p_rv_15m", ">=", [0.50, 0.55, 0.60]),
        ("margin_per_rv_sigma_15m", ">=", [0.0, 0.10, 0.25, 0.50]),
        ("spread_cents", "<=", [2, 4]),
        ("ask_cents", "<=", [85, 90, 95]),
    ]
    clauses: List[Clause] = []
    for feature, op, thresholds in specs:
        if feature not in rows.columns:
            continue
        for threshold in thresholds:
            clauses.append(Clause(feature=feature, op=op, threshold=float(threshold)))
    return clauses


def compatible(left: Clause, right: Clause) -> bool:
    if left.feature != right.feature:
        return True
    if left.op == right.op:
        return False
    if left.op == ">=" and right.op == "<=":
        return left.threshold <= right.threshold
    if left.op == "<=" and right.op == ">=":
        return right.threshold <= left.threshold
    return True


def includes_path_clause(clauses: tuple[Clause, ...]) -> bool:
    return any(clause.feature in PATH_FEATURES for clause in clauses)


def make_rules(candidate: str, rows: pd.DataFrame) -> List[DelayRule]:
    clauses = make_clauses(rows)
    rules = [DelayRule(candidate, tuple())]
    for clause in clauses:
        if includes_path_clause((clause,)):
            rules.append(DelayRule(candidate, (clause,)))
    for left, right in combinations(clauses, 2):
        pair = (left, right)
        if compatible(left, right) and includes_path_clause(pair):
            rules.append(DelayRule(candidate, pair))
    return rules


def rule_mask(rows: pd.DataFrame, rule: DelayRule) -> pd.Series:
    mask = pd.Series(True, index=rows.index)
    for clause in rule.clauses:
        mask &= clause.keep(rows)
    return mask.fillna(False)


def select_delayed_policy(side_rows: pd.DataFrame, base: pd.DataFrame, candidate: str, rule: DelayRule) -> pd.DataFrame:
    policy = load_lock_policy(candidate)
    rows = side_rows.merge(base[["market", "split"]], on="market", how="inner")
    chosen = choose_decision_sides(rows, policy.chooser)
    if chosen.empty:
        return chosen
    eligible = chosen[gate_mask(chosen, policy) & rule_mask(chosen, rule)].copy()
    if eligible.empty:
        return eligible
    selected = (
        eligible.sort_values(["market", "entry_dt"])
        .groupby("market", as_index=False, sort=False)
        .first()
        .sort_values(["entry_dt", "market"])
        .reset_index(drop=True)
    )
    selected["policy_name"] = candidate
    selected["delay_rule"] = rule.label
    return enrich_selected(selected)


def prepare_dataset(side_rows: pd.DataFrame) -> tuple[pd.DataFrame, Dict[str, pd.DataFrame]]:
    base = market_base(side_rows)
    selected: Dict[str, pd.DataFrame] = {}
    for candidate in CANDIDATES:
        selected[candidate] = enrich_selected(select_locked_policy(side_rows, base, candidate))
    return base, selected


def coverage_pass(metrics: Dict[str, Dict[str, Any]]) -> bool:
    return (
        all((metrics[split]["coverage"] or 0.0) >= MARKET_COVERAGE_FLOOR for split in ["all", "train", "validation", "holdout"])
        and metrics["all"]["markets"] >= MIN_SELECTED_MARKETS
        and metrics["holdout"]["markets"] >= MIN_HOLDOUT_SELECTED_MARKETS
    )


def positive_oos(metrics: Dict[str, Dict[str, Any]]) -> bool:
    return all((metrics[split]["net_pnl_cents"] or 0.0) > 0.0 for split in ["validation", "holdout"])


def positive_all_splits(metrics: Dict[str, Dict[str, Any]]) -> bool:
    return all((metrics[split]["net_pnl_cents"] or 0.0) > 0.0 for split in ["all", "train", "validation", "holdout"])


def delay_stats(base_selected: pd.DataFrame, selected: pd.DataFrame) -> Dict[str, Any]:
    if base_selected.empty or selected.empty:
        return {"delayed_markets": 0, "median_delay_seconds": None, "p75_delay_seconds": None}
    base_entries = base_selected[["market", "entry_dt"]].rename(columns={"entry_dt": "base_entry_dt"})
    paired = selected[["market", "entry_dt"]].merge(base_entries, on="market", how="left")
    paired["entry_dt"] = pd.to_datetime(paired["entry_dt"], utc=True, errors="coerce")
    paired["base_entry_dt"] = pd.to_datetime(paired["base_entry_dt"], utc=True, errors="coerce")
    delay = (paired["entry_dt"] - paired["base_entry_dt"]).dt.total_seconds()
    delay = pd.to_numeric(delay, errors="coerce").dropna()
    if delay.empty:
        return {"delayed_markets": 0, "median_delay_seconds": None, "p75_delay_seconds": None}
    return {
        "delayed_markets": int(delay.gt(0).sum()),
        "median_delay_seconds": float(delay.median()),
        "p75_delay_seconds": float(delay.quantile(0.75)),
    }


def flatten(
    rule: DelayRule,
    current_metrics: Dict[str, Dict[str, Any]],
    v21_metrics: Dict[str, Dict[str, Any]],
    current_blocks: Dict[str, Any],
    v21_blocks: Dict[str, Any],
    current_delay: Dict[str, Any],
    v21_delay: Dict[str, Any],
    base_current_net: float,
    base_v21_net: float,
) -> Dict[str, Any]:
    row: Dict[str, Any] = {
        "label": rule.label,
        "candidate": rule.candidate,
        "clause_count": len(rule.clauses),
        "clause_1": rule.clauses[0].label if len(rule.clauses) >= 1 else "",
        "clause_2": rule.clauses[1].label if len(rule.clauses) >= 2 else "",
        "current_coverage_pass": coverage_pass(current_metrics),
        "v21_coverage_pass": coverage_pass(v21_metrics),
        "both_coverage_pass": coverage_pass(current_metrics) and coverage_pass(v21_metrics),
        "current_oos_positive": positive_oos(current_metrics),
        "v21_oos_positive": positive_oos(v21_metrics),
        "both_oos_positive": positive_oos(current_metrics) and positive_oos(v21_metrics),
        "current_all_splits_positive": positive_all_splits(current_metrics),
        "v21_all_splits_positive": positive_all_splits(v21_metrics),
        "both_all_splits_positive": positive_all_splits(current_metrics) and positive_all_splits(v21_metrics),
    }
    row["current_delta_vs_candidate_cents"] = (current_metrics["all"]["net_pnl_cents"] or 0.0) - base_current_net
    row["v21_delta_vs_candidate_cents"] = (v21_metrics["all"]["net_pnl_cents"] or 0.0) - base_v21_net
    row["combined_delta_vs_candidate_cents"] = row["current_delta_vs_candidate_cents"] + row["v21_delta_vs_candidate_cents"]
    row["combined_all_net_pnl_cents"] = (current_metrics["all"]["net_pnl_cents"] or 0.0) + (v21_metrics["all"]["net_pnl_cents"] or 0.0)
    row["min_oos_roi"] = min(
        current_metrics["validation"]["net_roi_on_cost"] or -1.0,
        current_metrics["holdout"]["net_roi_on_cost"] or -1.0,
        v21_metrics["validation"]["net_roi_on_cost"] or -1.0,
        v21_metrics["holdout"]["net_roi_on_cost"] or -1.0,
    )
    row["min_block_positive_coverage_rate"] = min(
        current_blocks["positive_coverage_pass_rate"] or 0.0,
        v21_blocks["positive_coverage_pass_rate"] or 0.0,
    )
    row["worst_block_net_pnl_cents"] = min(
        current_blocks["worst_block_net_pnl_cents"] or 0.0,
        v21_blocks["worst_block_net_pnl_cents"] or 0.0,
    )
    row["block_stable"] = (
        row["min_block_positive_coverage_rate"] >= MIN_POS_COV_BLOCK_RATE
        and row["worst_block_net_pnl_cents"] > -250.0
    )
    row["diagnostic_pass"] = (
        row["both_coverage_pass"]
        and row["both_oos_positive"]
        and row["combined_delta_vs_candidate_cents"] > 0.0
        and row["min_oos_roi"] > MIN_OOS_ROI
        and row["block_stable"]
    )
    for prefix, metrics in [("current", current_metrics), ("v21", v21_metrics)]:
        for split, values in metrics.items():
            for key, value in values.items():
                row[f"{prefix}_{split}_{key}"] = value
    for prefix, blocks in [("current_block", current_blocks), ("v21_block", v21_blocks)]:
        for key, value in blocks.items():
            row[f"{prefix}_{key}"] = value
    for prefix, values in [("current_delay", current_delay), ("v21_delay", v21_delay)]:
        for key, value in values.items():
            row[f"{prefix}_{key}"] = value
    return row


def write_report(generated: str, rows: pd.DataFrame) -> None:
    top = rows[rows["both_coverage_pass"]].copy()
    top = top.sort_values(
        [
            "diagnostic_pass",
            "both_all_splits_positive",
            "both_oos_positive",
            "combined_delta_vs_candidate_cents",
            "min_oos_roi",
        ],
        ascending=[False, False, False, False, False],
    ).head(30)
    lines = [
        "# Candidate Tradeable Delayed Path-Veto Scan",
        "",
        f"Generated UTC: `{generated}`",
        "",
        "## Scope",
        "",
        "- Research-only scan; no orders are submitted and no bot files or live processes are touched.",
        "- Tests delayed entry within each market rather than skipping after the first path-veto failure.",
        "- Every row still must satisfy the locked candidate's original book/price/time gate.",
        "- Any apparent winner still needs strict pre-resolution forward registration and sample size.",
        "",
        "## Summary",
        "",
        f"- Rules scanned: {len(rows)}",
        f"- Both-dataset 80% coverage rules: {int(rows['both_coverage_pass'].sum())}",
        f"- Both-dataset OOS-positive rules: {int((rows['both_coverage_pass'] & rows['both_oos_positive']).sum())}",
        f"- Diagnostic pass rules: {int(rows['diagnostic_pass'].sum())}",
        "",
        "## Top Rows",
        "",
        "| rank | rule | diagnostic | delta current/v21 | current net/acc/cov | v21 net/acc/cov | OOS ROI floor | block pass | worst block | median delay cur/v21 |",
        "|---:|---|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for rank, (_, row) in enumerate(top.iterrows(), start=1):
        cur_delay = row.get("current_delay_median_delay_seconds")
        v21_delay = row.get("v21_delay_median_delay_seconds")
        delay_text = (
            f"{cur_delay:.1f}s/{v21_delay:.1f}s"
            if cur_delay is not None and v21_delay is not None and math.isfinite(float(cur_delay)) and math.isfinite(float(v21_delay))
            else "NA"
        )
        lines.append(
            f"| {rank} | `{row['label']}` | {bool(row['diagnostic_pass'])} | "
            f"{fmt_cents(row['current_delta_vs_candidate_cents'])}/{fmt_cents(row['v21_delta_vs_candidate_cents'])} | "
            f"{fmt_cents(row['current_all_net_pnl_cents'])}/{pct(row['current_all_accuracy'])}/{pct(row['current_all_coverage'])} | "
            f"{fmt_cents(row['v21_all_net_pnl_cents'])}/{pct(row['v21_all_accuracy'])}/{pct(row['v21_all_coverage'])} | "
            f"{fmt_roi(row['min_oos_roi'])} | {pct(row['min_block_positive_coverage_rate'])} | "
            f"{fmt_cents(row['worst_block_net_pnl_cents'])} | {delay_text} |"
        )
    lines += ["", "## Read", ""]
    if int(rows["diagnostic_pass"].sum()) == 0:
        lines.append("- No delayed path-veto rule clears the diagnostic robustness screen.")
    else:
        best = rows[rows["diagnostic_pass"]].sort_values("combined_delta_vs_candidate_cents", ascending=False).iloc[0]
        lines.append(
            f"- Best diagnostic row is `{best['label']}`, but it remains forward-test only until strict registered evidence exists."
        )
    lines.append("- Strict registered-signal readiness remains the promotion gate.")
    REPORT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    generated = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%SZ")
    current_side = load_side_rows()
    v21_side = load_v21_side_rows()
    current_base, current_locked = prepare_dataset(current_side)
    v21_base, v21_locked = prepare_dataset(v21_side)
    rows: List[Dict[str, Any]] = []
    for candidate in CANDIDATES:
        policy = load_lock_policy(candidate)
        current_rows = current_side.merge(current_base[["market", "split"]], on="market", how="inner")
        current_chosen = choose_decision_sides(current_rows, policy.chooser)
        rules = make_rules(candidate, current_chosen)
        base_current = current_locked[candidate]
        base_v21 = v21_locked[candidate]
        base_current_net = float(pd.to_numeric(base_current.get("net_pnl_cents"), errors="coerce").sum())
        base_v21_net = float(pd.to_numeric(base_v21.get("net_pnl_cents"), errors="coerce").sum())
        for rule in rules:
            current_selected = select_delayed_policy(current_side, current_base, candidate, rule)
            v21_selected = select_delayed_policy(v21_side, v21_base, candidate, rule)
            current_metrics = metrics_for(current_base, current_selected)
            v21_metrics = metrics_for(v21_base, v21_selected)
            rows.append(
                flatten(
                    rule,
                    current_metrics,
                    v21_metrics,
                    block_stability(current_base, current_selected),
                    block_stability(v21_base, v21_selected),
                    delay_stats(base_current, current_selected),
                    delay_stats(base_v21, v21_selected),
                    base_current_net,
                    base_v21_net,
                )
            )
    frame = pd.DataFrame(rows)
    frame = frame.sort_values(
        ["diagnostic_pass", "both_coverage_pass", "combined_delta_vs_candidate_cents", "min_oos_roi"],
        ascending=[False, False, False, False],
    ).reset_index(drop=True)
    REPORT_CSV.write_text(frame.to_csv(index=False), encoding="utf-8")
    REPORT_JSON.write_text(
        json.dumps(
            clean_json_local(
                {
                    "generated_utc": generated,
                    "rules_scanned": int(len(frame)),
                    "coverage_pass": int(frame["both_coverage_pass"].sum()),
                    "diagnostic_pass": int(frame["diagnostic_pass"].sum()),
                    "top": frame.head(20).to_dict(orient="records"),
                }
            ),
            indent=2,
            sort_keys=True,
        ),
        encoding="utf-8",
    )
    write_report(generated, frame)
    print("Candidate tradeable delayed path-veto scan complete")
    print(f"rules={len(frame)} coverage_pass={int(frame['both_coverage_pass'].sum())} diagnostic_pass={int(frame['diagnostic_pass'].sum())}")
    print(f"report={REPORT_MD}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
