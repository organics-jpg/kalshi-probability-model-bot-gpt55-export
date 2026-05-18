"""Physics-motivated probability blend audit for BTC 15m markets.

This research probe asks whether fair value improves when terminal probability
is blended with first-passage/touch survival and penalized for disagreement
between priors. Hyperparameters are intentionally tiny and fixed. The only
selected knob is the EV floor, chosen from train splits only, then evaluated on
validation/holdout for current and v21 ledgers.

Research-only: no orders are submitted and no bot files or live processes are
modified.
"""
from __future__ import annotations

import json
import math
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

import numpy as np
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
from probe_profit_touch_hazard_frontier import add_touch_hazard_scores


REPORT_MD = OUT_DIR / "physics_probability_blend_audit_latest.md"
REPORT_JSON = OUT_DIR / "physics_probability_blend_audit_latest.json"
ALL_ROWS_CSV = OUT_DIR / "physics_probability_blend_audit_all_latest.csv"
TRAIN_SELECTED_CSV = OUT_DIR / "physics_probability_blend_audit_train_selected_latest.csv"

MIN_SECONDS_TO_CLOSE = 60.0
ASK_MAX = 95.0
OOS_COVERAGE_FLOOR = 0.75
EDGE_FLOORS = [-70.0, -60.0, -50.0, -40.0, -30.0, -20.0, -15.0, -10.0, -5.0, 0.0, 2.0, 5.0, 10.0]


@dataclass(frozen=True)
class ModelSpec:
    name: str
    column: str
    thesis: str


MODEL_SPECS = [
    ModelSpec("book", "book_p_side", "market-implied terminal probability"),
    ModelSpec("brownian15", "brownian_p_rv_15m", "realized-vol terminal Brownian prior"),
    ModelSpec("min_book_rv15", "score_min_book_rv15", "conservative min(book, Brownian) prior"),
    ModelSpec("mean_book_rv15", "score_mean_book_rv15", "simple book/Brownian terminal average"),
    ModelSpec("hazard_discounted_mean15", "hazard_discounted_mean_15", "terminal confidence discounted by touch risk"),
    ModelSpec("book_hazard_50_50", "blend_book_hazard_50_50", "equal mix of book terminal and first-passage survival"),
    ModelSpec("book_hazard_70_30", "blend_book_hazard_70_30", "book-heavy first-passage blend"),
    ModelSpec("book_hazard_30_70", "blend_book_hazard_30_70", "hazard-heavy first-passage blend"),
    ModelSpec("book_rv_hazard_mean", "blend_book_rv_hazard_mean", "mean of book, Brownian terminal, and touch hazard"),
    ModelSpec("book_rv_hazard_min", "blend_book_rv_hazard_min", "worst-case consensus across book/Brownian/hazard"),
    ModelSpec("mean_minus_half_disagreement", "blend_mean_minus_half_disagreement", "consensus mean penalized by half prior disagreement"),
    ModelSpec("mean_minus_disagreement", "blend_mean_minus_disagreement", "consensus mean penalized by full prior disagreement"),
    ModelSpec("logit_book_hazard_mean", "blend_logit_book_hazard_mean", "geometric/logit pooling of book and hazard"),
    ModelSpec("logit_book_rv_hazard_mean", "blend_logit_book_rv_hazard_mean", "geometric/logit pooling of all three priors"),
    ModelSpec("scoremin_hazard_min", "blend_scoremin_hazard_min", "min of conservative terminal score and hazard score"),
    ModelSpec("hazard_kinetic_mean", "blend_hazard_kinetic_mean", "first-passage score averaged with short-path kinetic confirmation"),
    ModelSpec("hazard_kinetic_min", "blend_hazard_kinetic_min", "first-passage score requiring kinetic confirmation"),
]


def clean_json_local(value: Any) -> Any:
    if isinstance(value, pd.Timestamp):
        return value.isoformat()
    if isinstance(value, dict):
        return {str(k): clean_json_local(v) for k, v in value.items()}
    if isinstance(value, list):
        return [clean_json_local(v) for v in value]
    return clean_json(value)


def clamp_prob(values: Any) -> np.ndarray:
    return np.clip(np.asarray(values, dtype=float), 1e-4, 1.0 - 1e-4)


def logit(values: Any) -> np.ndarray:
    p = clamp_prob(values)
    return np.log(p / (1.0 - p))


def sigmoid(values: Any) -> np.ndarray:
    return 1.0 / (1.0 + np.exp(-np.clip(np.asarray(values, dtype=float), -40.0, 40.0)))


def row_mean(*cols: pd.Series) -> np.ndarray:
    return np.nanmean(np.vstack([pd.to_numeric(col, errors="coerce").to_numpy(dtype=float) for col in cols]), axis=0)


def row_min(*cols: pd.Series) -> np.ndarray:
    return np.nanmin(np.vstack([pd.to_numeric(col, errors="coerce").to_numpy(dtype=float) for col in cols]), axis=0)


def add_blend_scores(rows: pd.DataFrame) -> pd.DataFrame:
    out = add_touch_hazard_scores(rows)
    required = [
        "book_p_side",
        "brownian_p_rv_15m",
        "score_min_book_rv15",
        "score_mean_book_rv15",
        "hazard_discounted_mean_15",
        "kinetic_touch_score_15",
    ]
    for col in required:
        if col not in out.columns:
            out[col] = np.nan
        out[col] = pd.to_numeric(out[col], errors="coerce")

    book = out["book_p_side"]
    rv15 = out["brownian_p_rv_15m"]
    hazard = out["hazard_discounted_mean_15"]
    score_min = out["score_min_book_rv15"]
    kinetic = out["kinetic_touch_score_15"]

    out["blend_book_hazard_50_50"] = 0.50 * book + 0.50 * hazard
    out["blend_book_hazard_70_30"] = 0.70 * book + 0.30 * hazard
    out["blend_book_hazard_30_70"] = 0.30 * book + 0.70 * hazard
    out["blend_book_rv_hazard_mean"] = row_mean(book, rv15, hazard)
    out["blend_book_rv_hazard_min"] = row_min(book, rv15, hazard)

    trio = np.vstack([book.to_numpy(dtype=float), rv15.to_numpy(dtype=float), hazard.to_numpy(dtype=float)])
    trio_mean = np.nanmean(trio, axis=0)
    trio_std = np.nanstd(trio, axis=0)
    out["blend_mean_minus_half_disagreement"] = np.clip(trio_mean - 0.5 * trio_std, 0.0, 1.0)
    out["blend_mean_minus_disagreement"] = np.clip(trio_mean - trio_std, 0.0, 1.0)

    out["blend_logit_book_hazard_mean"] = sigmoid(0.5 * logit(book) + 0.5 * logit(hazard))
    out["blend_logit_book_rv_hazard_mean"] = sigmoid((logit(book) + logit(rv15) + logit(hazard)) / 3.0)
    out["blend_scoremin_hazard_min"] = row_min(score_min, hazard)
    out["blend_hazard_kinetic_mean"] = row_mean(hazard, kinetic)
    out["blend_hazard_kinetic_min"] = row_min(hazard, kinetic)

    for spec in MODEL_SPECS:
        if spec.column in out.columns:
            out[spec.column] = np.clip(pd.to_numeric(out[spec.column], errors="coerce"), 0.0, 1.0)
    return out


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


def chosen_rows(side_rows: pd.DataFrame, base: pd.DataFrame, spec: ModelSpec) -> pd.DataFrame:
    rows = side_rows.merge(base[["market", "split"]], on="market", how="inner")
    chosen = choose_decision_sides(rows, spec.column)
    if chosen.empty:
        return chosen.copy()
    chosen = chosen[
        chosen[spec.column].notna()
        & pd.to_numeric(chosen["ask_cents"], errors="coerce").le(ASK_MAX)
        & pd.to_numeric(chosen["seconds_to_close"], errors="coerce").ge(MIN_SECONDS_TO_CLOSE)
    ].copy()
    if chosen.empty:
        return chosen
    chosen["model"] = spec.name
    chosen["p_model"] = pd.to_numeric(chosen[spec.column], errors="coerce")
    chosen = enrich_selected(chosen)
    chosen["fair_edge_cents"] = 100.0 * chosen["p_model"] - chosen["entry_cost_cents"]
    return chosen.sort_values(["market", "entry_dt"]).reset_index(drop=True)


def metrics_for_floor(base: pd.DataFrame, chosen: pd.DataFrame, edge_floor: float) -> Dict[str, Dict[str, Any]]:
    selected = first_market_rows(chosen[chosen["fair_edge_cents"].ge(edge_floor)].copy())
    return {split: split_metric(base, selected, split) for split in ["all", "train", "validation", "holdout"]}


def flatten_dataset(prefix: str, metrics: Dict[str, Dict[str, Any]], row: Dict[str, Any]) -> None:
    for split, metric in metrics.items():
        for key, value in metric.items():
            row[f"{prefix}_{split}_{key}"] = value


def eval_all() -> tuple[pd.DataFrame, Dict[str, Any]]:
    datasets = {
        "current": add_blend_scores(load_side_rows()),
        "v21": add_blend_scores(load_v21_side_rows()),
    }
    bases = {name: market_base(rows) for name, rows in datasets.items()}
    chosen_cache: Dict[tuple[str, str], pd.DataFrame] = {}
    rows: List[Dict[str, Any]] = []
    for spec in MODEL_SPECS:
        for dataset_name, side_rows in datasets.items():
            chosen_cache[(dataset_name, spec.name)] = chosen_rows(side_rows, bases[dataset_name], spec)
        for floor in EDGE_FLOORS:
            row: Dict[str, Any] = {
                "model": spec.name,
                "score_column": spec.column,
                "thesis": spec.thesis,
                "edge_floor_cents": floor,
            }
            for dataset_name in ["current", "v21"]:
                metrics = metrics_for_floor(bases[dataset_name], chosen_cache[(dataset_name, spec.name)], floor)
                flatten_dataset(dataset_name, metrics, row)
            row["combined_train_net_pnl_cents"] = (
                (row.get("current_train_net_pnl_cents") or 0.0)
                + (row.get("v21_train_net_pnl_cents") or 0.0)
            )
            row["combined_all_net_pnl_cents"] = (
                (row.get("current_all_net_pnl_cents") or 0.0)
                + (row.get("v21_all_net_pnl_cents") or 0.0)
            )
            row["min_train_coverage"] = min(
                row.get("current_train_coverage") or 0.0,
                row.get("v21_train_coverage") or 0.0,
            )
            row["min_oos_coverage"] = min(
                row.get("current_validation_coverage") or 0.0,
                row.get("current_holdout_coverage") or 0.0,
                row.get("v21_validation_coverage") or 0.0,
                row.get("v21_holdout_coverage") or 0.0,
            )
            row["min_all_coverage"] = min(
                row.get("current_all_coverage") or 0.0,
                row.get("v21_all_coverage") or 0.0,
            )
            row["strict_80_oos_coverage_pass"] = row["min_oos_coverage"] >= MARKET_COVERAGE_FLOOR
            row["loose_75_oos_coverage_pass"] = row["min_oos_coverage"] >= OOS_COVERAGE_FLOOR
            row["both_oos_positive"] = all(
                (row.get(f"{dataset}_{split}_net_pnl_cents") or 0.0) > 0.0
                for dataset in ["current", "v21"]
                for split in ["validation", "holdout"]
            )
            row["both_all_positive"] = (
                (row.get("current_all_net_pnl_cents") or 0.0) > 0.0
                and (row.get("v21_all_net_pnl_cents") or 0.0) > 0.0
            )
            row["train_selected"] = False
            rows.append(row)
    frame = pd.DataFrame(rows)
    diagnostics = {
        "current_markets": int(len(bases["current"])),
        "v21_markets": int(len(bases["v21"])),
        "models": int(len(MODEL_SPECS)),
        "edge_floors": int(len(EDGE_FLOORS)),
    }
    return frame, diagnostics


def choose_train_selected(frame: pd.DataFrame) -> pd.DataFrame:
    selected_rows: List[pd.Series] = []
    for model, part in frame.groupby("model", sort=False):
        strict = part[part["min_train_coverage"].ge(MARKET_COVERAGE_FLOOR)].copy()
        pool = strict if not strict.empty else part[part["min_train_coverage"].ge(OOS_COVERAGE_FLOOR)].copy()
        if pool.empty:
            pool = part.copy()
        pool = pool.sort_values(
            ["combined_train_net_pnl_cents", "min_train_coverage", "edge_floor_cents"],
            ascending=[False, False, False],
        )
        row = pool.iloc[0].copy()
        row["train_selected"] = True
        row["train_selection_used_strict_80"] = not strict.empty
        selected_rows.append(row)
    return pd.DataFrame(selected_rows)


def fmt_num(value: Optional[float], digits: int = 3) -> str:
    if value is None or not math.isfinite(float(value)):
        return "NA"
    return f"{float(value):.{digits}f}"


def table_row(row: Dict[str, Any]) -> str:
    return (
        f"| `{row['model']}` | {fmt_cents(row['edge_floor_cents'])} | "
        f"{pct(row['min_train_coverage'])}/{pct(row['min_oos_coverage'])} | "
        f"{fmt_cents(row['combined_train_net_pnl_cents'])} | "
        f"{fmt_cents(row['current_all_net_pnl_cents'])}/{fmt_roi(row['current_all_net_roi_on_cost'])} | "
        f"{pct(row['current_all_accuracy'])}/{pct(row['current_all_coverage'])} | "
        f"{fmt_cents(row['v21_all_net_pnl_cents'])}/{fmt_roi(row['v21_all_net_roi_on_cost'])} | "
        f"{pct(row['v21_all_accuracy'])}/{pct(row['v21_all_coverage'])} | "
        f"{row['both_oos_positive']} | {row['strict_80_oos_coverage_pass']} |"
    )


def write_report(generated: str, frame: pd.DataFrame, train_selected: pd.DataFrame, diagnostics: Dict[str, Any]) -> None:
    strict_train_oos = train_selected[
        train_selected["both_oos_positive"] & train_selected["strict_80_oos_coverage_pass"]
    ].copy()
    loose_train_oos = train_selected[
        train_selected["both_oos_positive"] & train_selected["loose_75_oos_coverage_pass"]
    ].copy()
    diagnostic_oos = frame[
        frame["both_oos_positive"] & frame["strict_80_oos_coverage_pass"] & frame["both_all_positive"]
    ].copy()
    diagnostic_oos = diagnostic_oos.sort_values(
        ["combined_all_net_pnl_cents", "min_oos_coverage"],
        ascending=[False, False],
    )
    best = train_selected.sort_values(
        ["both_oos_positive", "strict_80_oos_coverage_pass", "combined_all_net_pnl_cents"],
        ascending=[False, False, False],
    )
    lines = [
        "# Physics Probability Blend Audit",
        "",
        f"Generated UTC: `{generated}`",
        "",
        "## Scope",
        "",
        "- Research-only audit; no orders are submitted and no bot files or live processes are touched.",
        "- Tests small fixed blends of book terminal probability, realized-vol Brownian terminal probability, first-passage/touch survival, and disagreement penalties.",
        "- For each blend, the EV floor is selected using train splits only; validation/holdout are not used for selection.",
        f"- Strict coverage target: `{pct(MARKET_COVERAGE_FLOOR)}`. Loose diagnostic floor: `{pct(OOS_COVERAGE_FLOOR)}`.",
        "",
        "## Diagnostics",
        "",
        f"- Current markets: {diagnostics['current_markets']}",
        f"- V21 markets: {diagnostics['v21_markets']}",
        f"- Models: {diagnostics['models']}",
        f"- EV floors per model: {diagnostics['edge_floors']}",
        f"- Train-selected strict 80% OOS pass rows: {len(strict_train_oos)}",
        f"- Train-selected loose 75% OOS pass rows: {len(loose_train_oos)}",
        f"- Diagnostic all-floor strict 80% OOS pass rows: {len(diagnostic_oos)}",
        "",
        "## Train-Selected Blends",
        "",
        "| model | EV floor | min train/oos cov | train net | current net/ROI | current acc/cov | v21 net/ROI | v21 acc/cov | OOS positive | strict OOS cov |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---|---|",
    ]
    for _, row in best.head(20).iterrows():
        lines.append(table_row(row.to_dict()))
    lines += [
        "",
        "## Diagnostic Strict OOS Rows",
        "",
    ]
    if diagnostic_oos.empty:
        lines.append("No all-floor diagnostic row is positive on validation and holdout for both datasets while keeping strict 80% OOS coverage.")
    else:
        lines += [
            "| model | EV floor | min train/oos cov | train net | current net/ROI | current acc/cov | v21 net/ROI | v21 acc/cov | OOS positive | strict OOS cov |",
            "|---|---:|---:|---:|---:|---:|---:|---:|---|---|",
        ]
        for _, row in diagnostic_oos.head(15).iterrows():
            lines.append(table_row(row.to_dict()))
        lines.append("")
        lines.append("- These rows are diagnostics, not locks, because the row itself is visible only after scanning validation/holdout.")
    lines += ["", "## Read", ""]
    if not strict_train_oos.empty:
        top = strict_train_oos.sort_values("combined_all_net_pnl_cents", ascending=False).iloc[0]
        lines.append(
            f"- Best train-selected strict row is `{top['model']}` at {fmt_cents(top['edge_floor_cents'])}, "
            f"combined all-ledger net {fmt_cents(top['combined_all_net_pnl_cents'])}."
        )
    elif not loose_train_oos.empty:
        top = loose_train_oos.sort_values("combined_all_net_pnl_cents", ascending=False).iloc[0]
        lines.append(
            f"- A train-selected row clears only the loose 75% OOS floor: `{top['model']}` at "
            f"{fmt_cents(top['edge_floor_cents'])}; keep it diagnostic until strict coverage is solved."
        )
    else:
        lines.append("- No train-selected blend clears positive validation/holdout P&L on both datasets at the required high coverage.")
    lines.append("- If the hazard trial survives forward samples, the useful physics prior is likely barrier/touch survival plus explicit uncertainty shrinkage, not raw Brownian terminal confidence.")
    for path in [REPORT_MD, OUT_DIR / f"physics_probability_blend_audit_{generated}.md"]:
        path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    generated = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%SZ")
    frame, diagnostics = eval_all()
    train_selected = choose_train_selected(frame)
    frame = frame.copy()
    selected_keys = set(zip(train_selected["model"], train_selected["edge_floor_cents"]))
    frame["train_selected"] = [
        (model, floor) in selected_keys
        for model, floor in zip(frame["model"], frame["edge_floor_cents"])
    ]
    frame.to_csv(ALL_ROWS_CSV, index=False)
    train_selected.to_csv(TRAIN_SELECTED_CSV, index=False)
    write_report(generated, frame, train_selected, diagnostics)
    payload = {
        "generated_utc": generated,
        "diagnostics": diagnostics,
        "strict_coverage_floor": MARKET_COVERAGE_FLOOR,
        "loose_coverage_floor": OOS_COVERAGE_FLOOR,
        "train_selected": train_selected.to_dict("records"),
        "strict_train_oos_pass_count": int(
            (train_selected["both_oos_positive"] & train_selected["strict_80_oos_coverage_pass"]).sum()
        ),
        "loose_train_oos_pass_count": int(
            (train_selected["both_oos_positive"] & train_selected["loose_75_oos_coverage_pass"]).sum()
        ),
        "all_rows_csv": str(ALL_ROWS_CSV),
        "train_selected_csv": str(TRAIN_SELECTED_CSV),
    }
    for path in [REPORT_JSON, OUT_DIR / f"physics_probability_blend_audit_{generated}.json"]:
        path.write_text(json.dumps(clean_json_local(payload), indent=2, sort_keys=True), encoding="utf-8")
    print("Physics probability blend audit complete")
    print(f"models={len(MODEL_SPECS)} rows={len(frame)}")
    print(f"report={REPORT_MD}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
