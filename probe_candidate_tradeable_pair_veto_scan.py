"""Two-clause tradeable veto scan for leading high-coverage BTC 15m locks.

The one-feature veto scan did not produce a promotion-quality improvement. This
probe tests small, interpretable pairs of physical/book clauses on the current
leading high-coverage locked candidates while preserving recurring-market
coverage on both the current and v21 ledgers.

This is intentionally conservative: clauses are applied to the already selected
first market row for each locked policy, so a market whose first eligible row is
vetoed is treated as skipped rather than re-entered later.

Research-only: no orders are submitted and no bot files or live processes are
modified. Passing rows are diagnostic candidates only; strict forward
registration is still required before any promotion.
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


REPORT_MD = OUT_DIR / "candidate_tradeable_pair_veto_scan_latest.md"
REPORT_JSON = OUT_DIR / "candidate_tradeable_pair_veto_scan_latest.json"
REPORT_CSV = OUT_DIR / "candidate_tradeable_pair_veto_scan_latest.csv"

CANDIDATES = ["book_margin", "book_margin_early"]
BLOCK_MARKETS = 20
MIN_BLOCK_BASE_MARKETS = 10
MIN_POS_COV_BLOCK_RATE = 0.70
MIN_OOS_ROI = 0.0


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
class PairRule:
    candidate: str
    clauses: tuple[Clause, ...]

    @property
    def label(self) -> str:
        if not self.clauses:
            return f"{self.candidate}: none"
        return f"{self.candidate}: " + " AND ".join(clause.label for clause in self.clauses)


def clean_json_local(value: Any) -> Any:
    if isinstance(value, pd.Timestamp):
        return value.isoformat()
    if isinstance(value, dict):
        return {str(k): clean_json_local(v) for k, v in value.items()}
    if isinstance(value, list):
        return [clean_json_local(v) for v in value]
    return clean_json(value)


def make_clauses(selected: pd.DataFrame) -> List[Clause]:
    specs = [
        ("ask_cents", "<=", [85, 90, 95]),
        ("seconds_to_close", ">=", [360, 480, 600]),
        ("seconds_to_close", "<=", [780, 900]),
        ("book_p_side", ">=", [0.60, 0.65, 0.70]),
        ("brownian_p_rv_15m", ">=", [0.50, 0.55, 0.60]),
        ("score_min_book_rv15", ">=", [0.60, 0.65]),
        ("abs_book_rv15_gap", "<=", [0.15, 0.20, 0.30]),
        ("adverse_move_15m", "<=", [50, 75, 100]),
        ("margin_per_rv_sigma_15m", ">=", [0, 0.25, 0.50]),
        ("spread_cents", "<=", [2, 4]),
        ("signed_move_5m", ">=", [-10, 0]),
    ]
    clauses: List[Clause] = []
    for feature, op, thresholds in specs:
        if feature not in selected.columns:
            continue
        for threshold in thresholds:
            clauses.append(Clause(feature, op, float(threshold)))
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


def make_rules(candidate: str, selected: pd.DataFrame) -> List[PairRule]:
    clauses = make_clauses(selected)
    rules = [PairRule(candidate, tuple())]
    rules.extend(PairRule(candidate, (clause,)) for clause in clauses)
    for left, right in combinations(clauses, 2):
        if compatible(left, right):
            rules.append(PairRule(candidate, (left, right)))
    return rules


def apply_rule(selected: pd.DataFrame, rule: PairRule) -> pd.DataFrame:
    if not rule.clauses:
        return selected.copy()
    mask = pd.Series(True, index=selected.index)
    for clause in rule.clauses:
        mask &= clause.keep(selected)
    return selected[mask.fillna(False)].copy()


def prepare_selected(side_rows: pd.DataFrame) -> tuple[pd.DataFrame, Dict[str, pd.DataFrame]]:
    base = market_base(side_rows)
    selected: Dict[str, pd.DataFrame] = {}
    for candidate in CANDIDATES:
        selected[candidate] = select_locked_policy(side_rows, base, candidate)
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


def block_stability(base: pd.DataFrame, selected: pd.DataFrame) -> Dict[str, Any]:
    if base.empty:
        return {
            "blocks": 0,
            "positive_blocks": 0,
            "coverage_pass_blocks": 0,
            "positive_coverage_pass_blocks": 0,
            "positive_coverage_pass_rate": None,
            "worst_block_net_pnl_cents": None,
        }
    base_blocks = base.sort_values(["close_dt", "market"]).reset_index(drop=True).copy()
    base_blocks["block_index"] = base_blocks.index // BLOCK_MARKETS
    selected_blocks = selected.merge(base_blocks[["market", "block_index"]], on="market", how="right")
    rows: List[Dict[str, Any]] = []
    for block_index, part in selected_blocks.groupby("block_index", sort=True):
        base_n = int(len(part))
        if base_n < MIN_BLOCK_BASE_MARKETS:
            continue
        kept = part[part["entry_dt"].notna()].copy()
        n = int(len(kept))
        net = float(pd.to_numeric(kept.get("net_pnl_cents"), errors="coerce").sum()) if n else 0.0
        rows.append(
            {
                "block_index": int(block_index),
                "base_markets": base_n,
                "selected_markets": n,
                "coverage": n / base_n if base_n else None,
                "net_pnl_cents": net,
            }
        )
    if not rows:
        return {
            "blocks": 0,
            "positive_blocks": 0,
            "coverage_pass_blocks": 0,
            "positive_coverage_pass_blocks": 0,
            "positive_coverage_pass_rate": None,
            "worst_block_net_pnl_cents": None,
        }
    positive = [row for row in rows if float(row["net_pnl_cents"]) > 0.0]
    coverage = [row for row in rows if float(row["coverage"] or 0.0) >= MARKET_COVERAGE_FLOOR]
    both = [row for row in rows if float(row["net_pnl_cents"]) > 0.0 and float(row["coverage"] or 0.0) >= MARKET_COVERAGE_FLOOR]
    worst = min(rows, key=lambda row: float(row["net_pnl_cents"]))
    return {
        "blocks": len(rows),
        "positive_blocks": len(positive),
        "coverage_pass_blocks": len(coverage),
        "positive_coverage_pass_blocks": len(both),
        "positive_coverage_pass_rate": len(both) / len(rows),
        "worst_block_net_pnl_cents": float(worst["net_pnl_cents"]),
    }


def flatten(
    rule: PairRule,
    current_metrics: Dict[str, Dict[str, Any]],
    v21_metrics: Dict[str, Dict[str, Any]],
    current_blocks: Dict[str, Any],
    v21_blocks: Dict[str, Any],
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
    row["block_stable"] = row["min_block_positive_coverage_rate"] >= MIN_POS_COV_BLOCK_RATE and row["worst_block_net_pnl_cents"] > -250.0
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
    return row


def write_report(generated: str, rows: pd.DataFrame) -> None:
    top = rows[rows["both_coverage_pass"]].copy()
    top = top.sort_values(
        ["diagnostic_pass", "both_all_splits_positive", "both_oos_positive", "combined_delta_vs_candidate_cents", "min_oos_roi"],
        ascending=[False, False, False, False, False],
    ).head(30)
    lines = [
        "# Candidate Tradeable Pair-Veto Scan",
        "",
        f"Generated UTC: `{generated}`",
        "",
        "## Scope",
        "",
        "- Research-only scan; no orders are submitted and no bot files or live processes are touched.",
        "- Tests one- and two-clause physical/book vetoes on current leading high-coverage locks.",
        "- Vetoes are applied to each lock's first selected row per market; skipped markets are not re-entered later.",
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
        "| rank | rule | diagnostic | delta current/v21 | current net/acc/cov | v21 net/acc/cov | OOS ROI floor | block pass | worst block |",
        "|---:|---|---|---:|---:|---:|---:|---:|---:|",
    ]
    for rank, (_, row) in enumerate(top.iterrows(), start=1):
        lines.append(
            f"| {rank} | `{row['label']}` | {bool(row['diagnostic_pass'])} | "
            f"{fmt_cents(row['current_delta_vs_candidate_cents'])}/{fmt_cents(row['v21_delta_vs_candidate_cents'])} | "
            f"{fmt_cents(row['current_all_net_pnl_cents'])}/{pct(row['current_all_accuracy'])}/{pct(row['current_all_coverage'])} | "
            f"{fmt_cents(row['v21_all_net_pnl_cents'])}/{pct(row['v21_all_accuracy'])}/{pct(row['v21_all_coverage'])} | "
            f"{fmt_roi(row['min_oos_roi'])} | {pct(row['min_block_positive_coverage_rate'])} | "
            f"{fmt_cents(row['worst_block_net_pnl_cents'])} |"
        )
    lines += ["", "## Read", ""]
    if int(rows["diagnostic_pass"].sum()) == 0:
        lines.append("- No pair-veto rule clears the diagnostic robustness screen.")
    else:
        best = rows[rows["diagnostic_pass"]].sort_values("combined_delta_vs_candidate_cents", ascending=False).iloc[0]
        lines.append(
            f"- Best diagnostic row is `{best['label']}`, but it remains forward-test only until strict registered evidence exists."
        )
    lines.append("- Strict registered-signal readiness remains the promotion gate.")
    REPORT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    generated = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%SZ")
    current_base, current_selected = prepare_selected(load_side_rows())
    v21_base, v21_selected = prepare_selected(load_v21_side_rows())
    rows: List[Dict[str, Any]] = []
    for candidate in CANDIDATES:
        current_base_selected = enrich_selected(current_selected[candidate])
        v21_base_selected = enrich_selected(v21_selected[candidate])
        base_current_net = float(pd.to_numeric(current_base_selected.get("net_pnl_cents"), errors="coerce").sum())
        base_v21_net = float(pd.to_numeric(v21_base_selected.get("net_pnl_cents"), errors="coerce").sum())
        for rule in make_rules(candidate, current_base_selected):
            current_rule = enrich_selected(apply_rule(current_base_selected, rule))
            v21_rule = enrich_selected(apply_rule(v21_base_selected, rule))
            current_metrics = metrics_for(current_base, current_rule)
            v21_metrics = metrics_for(v21_base, v21_rule)
            rows.append(
                flatten(
                    rule,
                    current_metrics,
                    v21_metrics,
                    block_stability(current_base, current_rule),
                    block_stability(v21_base, v21_rule),
                    base_current_net,
                    base_v21_net,
                )
            )
    df = pd.DataFrame(rows)
    df.to_csv(REPORT_CSV, index=False)
    REPORT_JSON.write_text(
        json.dumps({"generated_utc": generated, "rows": clean_json_local(df.to_dict(orient="records"))}, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    write_report(generated, df)
    print("Candidate tradeable pair-veto scan complete")
    print(f"rules={len(df)} coverage_pass={int(df['both_coverage_pass'].sum())}")
    print(f"diagnostic_pass={int(df['diagnostic_pass'].sum())}")
    print(f"report={REPORT_MD}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
