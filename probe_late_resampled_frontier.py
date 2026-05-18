"""Late-resampled high-coverage frontier scan.

The 14:30 UTC split exposed a concrete physics failure: an early Brownian
distance signal chose YES, while later path kinetics flipped to NO and won.
This probe tests a conservative alternative before inventing more structure:
keep the same broad side-choice priors, but first allow entries only after the
market has evolved past a maximum seconds-to-close boundary.

Research-only: no orders are submitted and no bot files or live processes are
modified.
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
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
)


REPORT_MD = OUT_DIR / "late_resampled_frontier_latest.md"
REPORT_JSON = OUT_DIR / "late_resampled_frontier_latest.json"
REPORT_CSV = OUT_DIR / "late_resampled_frontier_latest.csv"


@dataclass(frozen=True)
class LatePolicy:
    chooser: str
    min_score: float
    ask_max: float
    min_seconds_to_close: float
    max_seconds_to_close: float

    @property
    def label(self) -> str:
        return (
            f"choose={self.chooser}; {self.chooser}>={self.min_score:.2f}; "
            f"ask<={self.ask_max:g}; {self.min_seconds_to_close:g}<=sec_to_close<={self.max_seconds_to_close:g}"
        )


def clean_json_local(value: Any) -> Any:
    if isinstance(value, pd.Timestamp):
        return value.isoformat()
    if isinstance(value, dict):
        return {str(k): clean_json_local(v) for k, v in value.items()}
    if isinstance(value, list):
        return [clean_json_local(v) for v in value]
    return clean_json(value)


def make_policies() -> List[LatePolicy]:
    policies: List[LatePolicy] = []
    for chooser in [
        "book_p_side",
        "brownian_p_rv_15m",
        "brownian_p_rv_30m",
        "score_mean_book_rv15",
        "score_min_book_rv15",
    ]:
        for min_score in [0.50, 0.55, 0.60, 0.65]:
            for ask_max in [70.0, 80.0, 90.0, 95.0]:
                for max_sec in [900.0, 840.0, 780.0, 720.0, 660.0, 600.0, 540.0, 480.0, 420.0, 360.0, 300.0, 240.0]:
                    if max_sec <= 120.0:
                        continue
                    policies.append(LatePolicy(chooser, min_score, ask_max, 120.0, max_sec))
    return policies


def select_late_from_chosen(chosen: pd.DataFrame, policy: LatePolicy) -> pd.DataFrame:
    if chosen.empty:
        return enrich_selected(chosen)
    score = pd.to_numeric(chosen[policy.chooser], errors="coerce")
    ask = pd.to_numeric(chosen["ask_cents"], errors="coerce")
    seconds = pd.to_numeric(chosen["seconds_to_close"], errors="coerce")
    selected_rows = chosen[
        score.ge(policy.min_score)
        & ask.le(policy.ask_max)
        & seconds.ge(policy.min_seconds_to_close)
        & seconds.le(policy.max_seconds_to_close)
    ].copy()
    if selected_rows.empty:
        return enrich_selected(selected_rows)
    selected = (
        selected_rows.sort_values(["market", "entry_dt"])
        .groupby("market", as_index=False, sort=False)
        .first()
        .sort_values(["entry_dt", "market"])
        .reset_index(drop=True)
    )
    return enrich_selected(selected)


def coverage_pass(metrics: Dict[str, Dict[str, Any]]) -> bool:
    return (
        all((metrics[split]["coverage"] or 0.0) >= MARKET_COVERAGE_FLOOR for split in ["all", "train", "validation", "holdout"])
        and metrics["all"]["markets"] >= MIN_SELECTED_MARKETS
        and metrics["holdout"]["markets"] >= MIN_HOLDOUT_SELECTED_MARKETS
    )


def profitable_oos(metrics: Dict[str, Dict[str, Any]]) -> bool:
    return all((metrics[split]["net_pnl_cents"] or 0.0) > 0.0 for split in ["validation", "holdout"])


def flatten(policy: LatePolicy, current: Dict[str, Dict[str, Any]], v21: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
    row: Dict[str, Any] = {
        "label": policy.label,
        "chooser": policy.chooser,
        "min_score": policy.min_score,
        "ask_max": policy.ask_max,
        "min_seconds_to_close": policy.min_seconds_to_close,
        "max_seconds_to_close": policy.max_seconds_to_close,
        "current_coverage_pass": coverage_pass(current),
        "v21_coverage_pass": coverage_pass(v21),
        "both_coverage_pass": coverage_pass(current) and coverage_pass(v21),
        "current_profitable_oos": profitable_oos(current),
        "v21_profitable_oos": profitable_oos(v21),
        "both_profitable_oos": profitable_oos(current) and profitable_oos(v21),
    }
    row["combined_all_net_pnl_cents"] = (current["all"]["net_pnl_cents"] or 0.0) + (v21["all"]["net_pnl_cents"] or 0.0)
    row["min_all_coverage"] = min(current["all"]["coverage"] or 0.0, v21["all"]["coverage"] or 0.0)
    row["min_oos_net_roi"] = min(
        current["validation"]["net_roi_on_cost"] or -1.0,
        current["holdout"]["net_roi_on_cost"] or -1.0,
        v21["validation"]["net_roi_on_cost"] or -1.0,
        v21["holdout"]["net_roi_on_cost"] or -1.0,
    )
    row["min_accuracy_minus_break_even"] = min(
        current[split]["accuracy_minus_break_even"] or -1.0
        for split in ["all", "train", "validation", "holdout"]
    )
    row["min_accuracy_minus_break_even"] = min(
        row["min_accuracy_minus_break_even"],
        min(v21[split]["accuracy_minus_break_even"] or -1.0 for split in ["all", "train", "validation", "holdout"]),
    )
    for prefix, metrics in [("current", current), ("v21", v21)]:
        for split, values in metrics.items():
            for key, value in values.items():
                row[f"{prefix}_{split}_{key}"] = value
    return row


def write_report(generated: str, rows: pd.DataFrame) -> None:
    viable = rows[rows["both_coverage_pass"]].copy()
    viable = viable.sort_values(
        ["both_profitable_oos", "combined_all_net_pnl_cents", "min_oos_net_roi", "min_accuracy_minus_break_even"],
        ascending=[False, False, False, False],
    )
    top = viable.head(20)
    lines: List[str] = [
        "# Late-Resampled Frontier Scan",
        "",
        f"Generated UTC: `{generated}`",
        "",
        "## Scope",
        "",
        "- Research-only scan; no orders are submitted and no bot files or live processes are touched.",
        "- Tests whether delaying first eligibility by a max seconds-to-close boundary improves the high-coverage Brownian/book frontier.",
        "- The scan is diagnostic only; any candidate needs a separate forward lock and strict pre-resolution capture.",
        "",
        "## Summary",
        "",
        f"- Policies scanned: {len(rows)}",
        f"- Both-dataset 80% coverage policies: {int(rows['both_coverage_pass'].sum())}",
        f"- Both-dataset OOS-positive policies: {int((rows['both_coverage_pass'] & rows['both_profitable_oos']).sum())}",
        "",
        "## Top Rows",
        "",
        "| rank | policy | current net/acc/cov | v21 net/acc/cov | OOS ROI floor | BE edge floor |",
        "|---:|---|---:|---:|---:|---:|",
    ]
    for rank, (_, row) in enumerate(top.iterrows(), start=1):
        lines.append(
            f"| {rank} | `{row['label']}` | "
            f"{fmt_cents(row['current_all_net_pnl_cents'])}/{pct(row['current_all_accuracy'])}/{pct(row['current_all_coverage'])} | "
            f"{fmt_cents(row['v21_all_net_pnl_cents'])}/{pct(row['v21_all_accuracy'])}/{pct(row['v21_all_coverage'])} | "
            f"{fmt_roi(row['min_oos_net_roi'])} | {row['min_accuracy_minus_break_even']:.3f} |"
        )
    lines += [
        "",
        "## Read",
        "",
    ]
    if top.empty:
        lines.append("- No late-resampled row preserved the 80% coverage floor on both datasets.")
    else:
        best = top.iloc[0]
        lines.append(
            f"- Best diagnostic row: `{best['label']}` with current/v21 net "
            f"{fmt_cents(best['current_all_net_pnl_cents'])}/{fmt_cents(best['v21_all_net_pnl_cents'])}."
        )
        lines.append("- Treat this as a candidate generator, not promotion evidence; strict live registration still decides.")
    REPORT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    generated = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%SZ")
    current_side = load_side_rows()
    v21_side = load_v21_side_rows()
    current_base = market_base(current_side)
    v21_base = market_base(v21_side)
    policies = make_policies()
    choosers = sorted({policy.chooser for policy in policies})
    current_rows = current_side.merge(current_base[["market", "split"]], on="market", how="inner")
    v21_rows = v21_side.merge(v21_base[["market", "split"]], on="market", how="inner")
    current_chosen = {chooser: choose_decision_sides(current_rows, chooser) for chooser in choosers}
    v21_chosen = {chooser: choose_decision_sides(v21_rows, chooser) for chooser in choosers}
    rows: List[Dict[str, Any]] = []
    for policy in policies:
        current_selected = select_late_from_chosen(current_chosen[policy.chooser], policy)
        v21_selected = select_late_from_chosen(v21_chosen[policy.chooser], policy)
        rows.append(flatten(policy, metrics_for(current_base, current_selected), metrics_for(v21_base, v21_selected)))
    df = pd.DataFrame(rows)
    df.to_csv(REPORT_CSV, index=False)
    REPORT_JSON.write_text(
        json.dumps({"generated_utc": generated, "rows": clean_json_local(df.to_dict(orient="records"))}, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    write_report(generated, df)
    print("Late-resampled frontier scan complete")
    print(f"policies={len(df)} coverage_pass={int(df['both_coverage_pass'].sum())}")
    print(f"report={REPORT_MD}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
