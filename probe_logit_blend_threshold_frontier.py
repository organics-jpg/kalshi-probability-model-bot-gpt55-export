"""Threshold scan for the logit book/RV/hazard blend.

The first live logit-blend trial lost on a cheap YES with physical probability
below 0.50. This probe tests whether a small explicit minimum-probability gate
improves robustness while preserving the 75-80% recurring-market trade rate.

Research-only: no orders are submitted and no bot files or live processes are
modified. Passing rows are forward-test candidates, not promotion evidence.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any, Dict, List

import pandas as pd

from probe_cross_dataset_interval_frontier import load_v21_side_rows
from probe_cross_dataset_profit_frontier import enrich_selected, fmt_cents, fmt_roi, split_metric
from probe_market_interval_80coverage import (
    MARKET_COVERAGE_FLOOR,
    OUT_DIR,
    choose_decision_sides,
    clean_json,
    load_side_rows,
    market_base,
    pct,
)
from probe_physics_probability_blend_audit import add_blend_scores


REPORT_MD = OUT_DIR / "logit_blend_threshold_frontier_latest.md"
REPORT_JSON = OUT_DIR / "logit_blend_threshold_frontier_latest.json"
CSV_LATEST = OUT_DIR / "logit_blend_threshold_frontier_latest.csv"

CHOOSER = "blend_logit_book_rv_hazard_mean"
MIN_SECONDS_TO_CLOSE = 60.0
ASK_MAX = 95.0
MIN_SCORES = [0.45, 0.50, 0.55, 0.60, 0.65]
EDGE_FLOORS = [-15.0, -10.0, -5.0, 0.0, 5.0]
LOOSE_COVERAGE_FLOOR = 0.75


def clean_json_local(value: Any) -> Any:
    if isinstance(value, pd.Timestamp):
        return value.isoformat()
    if isinstance(value, dict):
        return {str(k): clean_json_local(v) for k, v in value.items()}
    if isinstance(value, list):
        return [clean_json_local(v) for v in value]
    return clean_json(value)


def first_market_rows(rows: pd.DataFrame) -> pd.DataFrame:
    if rows.empty:
        return rows.copy()
    return (
        rows.sort_values(["market", "entry_dt"])
        .groupby("market", as_index=False, sort=False)
        .first()
        .sort_values(["entry_dt", "market"])
        .reset_index(drop=True)
    )


def selected_for(base: pd.DataFrame, side_rows: pd.DataFrame, min_score: float, edge_floor: float) -> pd.DataFrame:
    rows = side_rows.merge(base[["market", "split"]], on="market", how="inner")
    chosen = choose_decision_sides(rows, CHOOSER)
    if chosen.empty:
        return chosen.copy()
    chosen = enrich_selected(chosen)
    scores = pd.to_numeric(chosen[CHOOSER], errors="coerce")
    chosen["fair_edge_cents"] = 100.0 * scores - pd.to_numeric(chosen["entry_cost_cents"], errors="coerce")
    eligible = chosen[
        scores.ge(min_score)
        & pd.to_numeric(chosen["fair_edge_cents"], errors="coerce").ge(edge_floor)
        & pd.to_numeric(chosen["ask_cents"], errors="coerce").le(ASK_MAX)
        & pd.to_numeric(chosen["seconds_to_close"], errors="coerce").ge(MIN_SECONDS_TO_CLOSE)
    ].copy()
    return first_market_rows(eligible)


def metrics_for(base: pd.DataFrame, selected: pd.DataFrame) -> Dict[str, Dict[str, Any]]:
    return {split: split_metric(base, selected, split) for split in ["all", "train", "validation", "holdout"]}


def flatten(min_score: float, edge_floor: float, current: Dict[str, Dict[str, Any]], v21: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
    row: Dict[str, Any] = {
        "label": f"{CHOOSER}>={min_score:.2f}; fair_edge>={edge_floor:g}c; ask<={ASK_MAX:g}; sec>={MIN_SECONDS_TO_CLOSE:g}",
        "chooser": CHOOSER,
        "min_score": min_score,
        "edge_floor_cents": edge_floor,
    }
    for prefix, metrics in [("current", current), ("v21", v21)]:
        for split, metric in metrics.items():
            for key, value in metric.items():
                row[f"{prefix}_{split}_{key}"] = value
    row["combined_all_net_pnl_cents"] = (row["current_all_net_pnl_cents"] or 0.0) + (row["v21_all_net_pnl_cents"] or 0.0)
    row["combined_train_net_pnl_cents"] = (row["current_train_net_pnl_cents"] or 0.0) + (row["v21_train_net_pnl_cents"] or 0.0)
    row["min_all_coverage"] = min(row["current_all_coverage"] or 0.0, row["v21_all_coverage"] or 0.0)
    row["min_oos_coverage"] = min(
        row["current_validation_coverage"] or 0.0,
        row["current_holdout_coverage"] or 0.0,
        row["v21_validation_coverage"] or 0.0,
        row["v21_holdout_coverage"] or 0.0,
    )
    row["strict_80_oos_coverage_pass"] = row["min_oos_coverage"] >= MARKET_COVERAGE_FLOOR
    row["loose_75_oos_coverage_pass"] = row["min_oos_coverage"] >= LOOSE_COVERAGE_FLOOR
    row["both_oos_positive"] = all(
        (row[f"{dataset}_{split}_net_pnl_cents"] or 0.0) > 0.0
        for dataset in ["current", "v21"]
        for split in ["validation", "holdout"]
    )
    row["both_all_positive"] = (row["current_all_net_pnl_cents"] or 0.0) > 0.0 and (row["v21_all_net_pnl_cents"] or 0.0) > 0.0
    return row


def scan() -> tuple[pd.DataFrame, Dict[str, Any]]:
    current_side = add_blend_scores(load_side_rows())
    v21_side = add_blend_scores(load_v21_side_rows())
    current_base = market_base(current_side)
    v21_base = market_base(v21_side)
    rows: List[Dict[str, Any]] = []
    for min_score in MIN_SCORES:
        for edge_floor in EDGE_FLOORS:
            current_selected = selected_for(current_base, current_side, min_score, edge_floor)
            v21_selected = selected_for(v21_base, v21_side, min_score, edge_floor)
            rows.append(flatten(min_score, edge_floor, metrics_for(current_base, current_selected), metrics_for(v21_base, v21_selected)))
    frame = pd.DataFrame(rows)
    frame = frame.sort_values(
        ["both_oos_positive", "strict_80_oos_coverage_pass", "combined_all_net_pnl_cents", "min_oos_coverage"],
        ascending=[False, False, False, False],
    ).reset_index(drop=True)
    diagnostics = {
        "current_markets": int(len(current_base)),
        "v21_markets": int(len(v21_base)),
        "rows": int(len(frame)),
    }
    return frame, diagnostics


def table_row(row: Dict[str, Any]) -> str:
    return (
        f"| `{row['label']}` | {fmt_cents(row['combined_all_net_pnl_cents'])} | "
        f"{fmt_cents(row['current_all_net_pnl_cents'])}/{fmt_roi(row['current_all_net_roi_on_cost'])} | "
        f"{pct(row['current_all_accuracy'])}/{pct(row['current_all_coverage'])} | "
        f"{fmt_cents(row['v21_all_net_pnl_cents'])}/{fmt_roi(row['v21_all_net_roi_on_cost'])} | "
        f"{pct(row['v21_all_accuracy'])}/{pct(row['v21_all_coverage'])} | "
        f"{pct(row['min_oos_coverage'])} | {row['both_oos_positive']} | {row['strict_80_oos_coverage_pass']} |"
    )


def write_report(generated: str, frame: pd.DataFrame, diagnostics: Dict[str, Any]) -> None:
    strict = frame[frame["both_oos_positive"] & frame["strict_80_oos_coverage_pass"] & frame["both_all_positive"]]
    lines = [
        "# Logit Blend Threshold Frontier",
        "",
        f"Generated UTC: `{generated}`",
        "",
        "## Scope",
        "",
        "- Research-only scan; no orders are submitted and no bot files or live processes are touched.",
        "- Tests whether the logit book/RV/hazard blend needs a minimum physical-probability gate instead of pure cheap-price fair edge.",
        f"- Strict coverage target: `{pct(MARKET_COVERAGE_FLOOR)}`; loose diagnostic floor: `{pct(LOOSE_COVERAGE_FLOOR)}`.",
        "",
        "## Diagnostics",
        "",
        f"- Current markets: {diagnostics['current_markets']}",
        f"- V21 markets: {diagnostics['v21_markets']}",
        f"- Rows scanned: {diagnostics['rows']}",
        f"- Strict positive OOS rows: {len(strict)}",
        "",
        "## Top Rows",
        "",
        "| policy | combined net | current net/ROI | current acc/cov | v21 net/ROI | v21 acc/cov | min OOS cov | OOS positive | strict cov |",
        "|---|---:|---:|---:|---:|---:|---:|---|---|",
    ]
    for _, row in frame.head(15).iterrows():
        lines.append(table_row(row.to_dict()))
    lines += ["", "## Read", ""]
    if strict.empty:
        lines.append("- No thresholded logit-blend row is positive on validation/holdout for both datasets while keeping strict 80% OOS coverage.")
    else:
        best = strict.iloc[0]
        lines.append(
            f"- Best strict diagnostic row is `{best['label']}` with combined all-ledger net "
            f"{fmt_cents(best['combined_all_net_pnl_cents'])}."
        )
    lines.append("- Any row from this scan must be forward-locked before use because the scan sees validation/holdout.")
    for path in [REPORT_MD, OUT_DIR / f"logit_blend_threshold_frontier_{generated}.md"]:
        path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    generated = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%SZ")
    frame, diagnostics = scan()
    frame.to_csv(CSV_LATEST, index=False)
    (OUT_DIR / f"logit_blend_threshold_frontier_{generated}.csv").write_text(CSV_LATEST.read_text(encoding="utf-8"), encoding="utf-8")
    write_report(generated, frame, diagnostics)
    payload = {
        "generated_utc": generated,
        "diagnostics": diagnostics,
        "rows": frame.to_dict("records"),
    }
    for path in [REPORT_JSON, OUT_DIR / f"logit_blend_threshold_frontier_{generated}.json"]:
        path.write_text(json.dumps(clean_json_local(payload), indent=2, sort_keys=True), encoding="utf-8")
    print("Logit blend threshold frontier complete")
    print(f"rows={len(frame)}")
    print(f"report={REPORT_MD}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
