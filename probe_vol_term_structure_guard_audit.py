"""Volatility term-structure guard audit for BTC 15m book/score priors.

The existing score/book guards test volatility level, touch risk, momentum, and
previous-market state. This probe tests a distinct question: whether short-term
realized volatility is compressed or expanded relative to 30m/60m realized
volatility, and whether that state stabilizes the high-coverage priors.

Research-only: no orders are submitted and no bot files or live processes are
modified. A robust diagnostic row would still require strict pre-registered
forward evidence before any promotion.
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Dict, List, Tuple

import pandas as pd

from probe_book_edge_gate_robustness_audit import (
    MIN_SLICE_MARKETS,
    POSITIVE_BLOCK_RATE_FLOOR,
    block_rows,
    slice_rows,
    supported_block_summary,
)
from probe_cross_dataset_interval_frontier import load_v21_side_rows
from probe_cross_dataset_profit_frontier import (
    enrich_selected,
    estimated_order_fee_cents,
    fmt_cents,
    fmt_roi,
    metrics_for,
)
from probe_market_interval_80coverage import (
    MARKET_COVERAGE_FLOOR,
    OUT_DIR,
    choose_decision_sides,
    clean_json,
    load_side_rows,
    market_base,
    pct,
)


REPORT_MD = OUT_DIR / "vol_term_structure_guard_audit_latest.md"
REPORT_JSON = OUT_DIR / "vol_term_structure_guard_audit_latest.json"
SUMMARY_CSV = OUT_DIR / "vol_term_structure_guard_summary_latest.csv"
BLOCKS_CSV = OUT_DIR / "vol_term_structure_guard_blocks_latest.csv"
SLICES_CSV = OUT_DIR / "vol_term_structure_guard_slices_latest.csv"

Filter = Tuple[str, str, float]


@dataclass(frozen=True)
class Candidate:
    name: str
    chooser: str
    min_score: float
    edge_floor_cents: float = -100.0
    ask_max: float = 95.0
    min_seconds_to_close: float = 120.0
    margin_gate: bool = False
    filters: Tuple[Filter, ...] = ()

    @property
    def label(self) -> str:
        parts = [
            f"choose={self.chooser}",
            f"{self.chooser}>={self.min_score:g}",
            f"fee_edge>={self.edge_floor_cents:g}c",
            f"ask<={self.ask_max:g}",
            f"sec>={self.min_seconds_to_close:g}",
        ]
        if self.margin_gate:
            parts.append("margin_rv15>=0")
        for feature, op, threshold in self.filters:
            parts.append(f"{feature}{op}{threshold:g}")
        return "; ".join(parts)


BASE_SPECS = [
    ("book_margin", "book_p_side", 0.60, -100.0, 95.0, 120.0, True),
    ("book_edge_m5", "book_p_side", 0.60, -5.0, 95.0, 120.0, True),
    ("score_m60", "score_min_book_rv15", 0.60, -100.0, 95.0, 120.0, False),
    ("score_edge_m5", "score_min_book_rv15", 0.60, -5.0, 95.0, 120.0, False),
]

FILTER_SETS: List[Tuple[Filter, ...]] = [
    (),
    (("rv15_over_rv30", "<=", 0.80),),
    (("rv15_over_rv30", "<=", 1.00),),
    (("rv15_over_rv30", "<=", 1.20),),
    (("rv15_over_rv30", ">=", 0.80),),
    (("rv15_over_rv30", ">=", 1.00),),
    (("rv15_over_rv30", ">=", 1.20),),
    (("rv30_over_rv60", "<=", 0.80),),
    (("rv30_over_rv60", "<=", 1.00),),
    (("rv30_over_rv60", ">=", 1.00),),
    (("rv30_over_rv60", ">=", 1.20),),
    (("rv15_over_rv60", "<=", 0.80),),
    (("rv15_over_rv60", "<=", 1.00),),
    (("rv15_over_rv60", ">=", 1.00),),
    (("rv15_over_rv60", ">=", 1.20),),
    (("rv15_minus_rv30", "<=", -10.0),),
    (("rv15_minus_rv30", "<=", 0.0),),
    (("rv15_minus_rv30", ">=", 0.0),),
    (("rv15_minus_rv30", ">=", 10.0),),
    (("rv15_over_rv30", "<=", 1.00), ("rv30_over_rv60", "<=", 1.00)),
    (("rv15_over_rv30", ">=", 1.00), ("rv30_over_rv60", ">=", 1.00)),
    (("rv15_over_rv30", "<=", 0.80), ("rv_sigma_t_15m", "<=", 100.0)),
    (("rv15_over_rv30", ">=", 1.20), ("rv_sigma_t_15m", ">=", 75.0)),
]


def filter_name(filters: Tuple[Filter, ...]) -> str:
    if not filters:
        return "none"
    tokens = []
    for feature, op, threshold in filters:
        token = f"{feature}_{op}_{threshold:g}"
        token = token.replace("<=", "le").replace(">=", "ge").replace(".", "p").replace("-", "m")
        tokens.append(token)
    return "__".join(tokens)


def make_candidates() -> List[Candidate]:
    candidates: List[Candidate] = []
    for prefix, chooser, min_score, edge_floor, ask_max, min_sec, margin_gate in BASE_SPECS:
        for filters in FILTER_SETS:
            suffix = filter_name(filters)
            name = prefix if suffix == "none" else f"{prefix}__{suffix}"
            candidates.append(
                Candidate(
                    name=name,
                    chooser=chooser,
                    min_score=min_score,
                    edge_floor_cents=edge_floor,
                    ask_max=ask_max,
                    min_seconds_to_close=min_sec,
                    margin_gate=margin_gate,
                    filters=filters,
                )
            )
    return candidates


CANDIDATES = make_candidates()


def clean_json_local(value: Any) -> Any:
    if isinstance(value, pd.Timestamp):
        return value.isoformat()
    if isinstance(value, dict):
        return {str(k): clean_json_local(v) for k, v in value.items()}
    if isinstance(value, list):
        return [clean_json_local(v) for v in value]
    return clean_json(value)


def add_vol_features(side_rows: pd.DataFrame) -> pd.DataFrame:
    out = side_rows.copy()
    for col in ["rv_sigma_t_15m", "rv_sigma_t_30m", "rv_sigma_t_60m"]:
        if col not in out.columns:
            out[col] = pd.NA
        out[col] = pd.to_numeric(out[col], errors="coerce")
    rv15 = out["rv_sigma_t_15m"]
    rv30 = out["rv_sigma_t_30m"]
    rv60 = out["rv_sigma_t_60m"]
    out["rv15_over_rv30"] = rv15 / rv30.where(rv30.gt(0))
    out["rv30_over_rv60"] = rv30 / rv60.where(rv60.gt(0))
    out["rv15_over_rv60"] = rv15 / rv60.where(rv60.gt(0))
    out["rv15_minus_rv30"] = rv15 - rv30
    out["rv30_minus_rv60"] = rv30 - rv60
    return out


def selected_for_candidate(side_rows: pd.DataFrame, base: pd.DataFrame, candidate: Candidate) -> pd.DataFrame:
    rows = side_rows.drop(columns=["split"], errors="ignore").merge(base[["market", "split"]], on="market", how="inner")
    chosen = choose_decision_sides(rows, candidate.chooser)
    if chosen.empty:
        return enrich_selected(chosen)

    chosen = chosen.copy()
    numeric_cols = {
        candidate.chooser,
        "ask_cents",
        "seconds_to_close",
        "margin_per_rv_sigma_15m",
        *(feature for feature, _, _ in candidate.filters),
    }
    for col in numeric_cols:
        if col in chosen.columns:
            chosen[col] = pd.to_numeric(chosen[col], errors="coerce")

    score = pd.to_numeric(chosen[candidate.chooser], errors="coerce")
    fees = pd.Series(
        [estimated_order_fee_cents(value, 1) for value in chosen["ask_cents"].fillna(100.0)],
        index=chosen.index,
    )
    edge = 100.0 * score - (chosen["ask_cents"] + fees)

    mask = (
        score.ge(candidate.min_score)
        & chosen["ask_cents"].le(candidate.ask_max)
        & chosen["seconds_to_close"].ge(candidate.min_seconds_to_close)
        & edge.ge(candidate.edge_floor_cents)
    )
    if candidate.margin_gate:
        mask &= pd.to_numeric(chosen["margin_per_rv_sigma_15m"], errors="coerce").ge(0.0)
    for feature, op, threshold in candidate.filters:
        values = pd.to_numeric(chosen.get(feature), errors="coerce")
        if op == "<=":
            mask &= values.le(threshold)
        elif op == ">=":
            mask &= values.ge(threshold)
        else:
            raise ValueError(f"unknown filter op: {op}")

    chosen["candidate_score"] = score
    chosen["candidate_fair_edge_cents"] = edge
    selected = (
        chosen[mask.fillna(False)]
        .sort_values(["market", "entry_dt"])
        .groupby("market", as_index=False, sort=False)
        .first()
        .sort_values(["entry_dt", "market"])
        .reset_index(drop=True)
    )
    selected["candidate"] = candidate.name
    selected["candidate_label"] = candidate.label
    return enrich_selected(selected)


def flatten_summary(dataset: str, candidate: Candidate, base: pd.DataFrame, selected: pd.DataFrame) -> Dict[str, Any]:
    metrics = metrics_for(base, selected)
    row: Dict[str, Any] = {
        "dataset": dataset,
        "candidate": candidate.name,
        "label": candidate.label,
        "filter_count": len(candidate.filters),
    }
    for split, values in metrics.items():
        for key, value in values.items():
            row[f"{split}_{key}"] = value
    row["coverage_pass"] = all(
        (metrics[split]["coverage"] or 0.0) >= MARKET_COVERAGE_FLOOR
        for split in ["all", "train", "validation", "holdout"]
    )
    row["all_splits_positive"] = all(
        (metrics[split]["net_pnl_cents"] or 0.0) > 0.0
        for split in ["all", "train", "validation", "holdout"]
    )
    row["oos_positive"] = all(
        (metrics[split]["net_pnl_cents"] or 0.0) > 0.0
        for split in ["validation", "holdout"]
    )
    return row


def vol_slice_rows(dataset: str, candidate: str, selected: pd.DataFrame) -> List[Dict[str, Any]]:
    rows = slice_rows(dataset, candidate, selected)
    if selected.empty:
        return rows
    work = selected.copy()
    for col in ["rv15_over_rv30", "rv30_over_rv60", "rv15_over_rv60", "rv15_minus_rv30"]:
        work[col] = pd.to_numeric(work.get(col), errors="coerce")
    definitions = {
        "rv15_over_rv30": pd.cut(work["rv15_over_rv30"], [-10, 0.8, 1.0, 1.2, 10], include_lowest=True).astype(str),
        "rv30_over_rv60": pd.cut(work["rv30_over_rv60"], [-10, 0.8, 1.0, 1.2, 10], include_lowest=True).astype(str),
        "rv15_over_rv60": pd.cut(work["rv15_over_rv60"], [-10, 0.8, 1.0, 1.2, 10], include_lowest=True).astype(str),
        "rv15_minus_rv30": pd.cut(work["rv15_minus_rv30"], [-500, -10, 0, 10, 500], include_lowest=True).astype(str),
    }
    for family, labels in definitions.items():
        for label, part in work.groupby(labels, sort=True):
            n = int(len(part))
            if n < MIN_SLICE_MARKETS:
                continue
            wins = int(part["win"].astype(bool).sum())
            net = float(pd.to_numeric(part["net_pnl_cents"], errors="coerce").sum())
            rows.append(
                {
                    "dataset": dataset,
                    "candidate": candidate,
                    "slice": f"{family}={label}",
                    "markets": n,
                    "wins": wins,
                    "losses": n - wins,
                    "accuracy": wins / n,
                    "net_pnl_cents": net,
                    "net_per_market_cents": net / n,
                    "median_ask": float(pd.to_numeric(part["ask_cents"], errors="coerce").median()),
                    "median_edge": float(pd.to_numeric(part["candidate_fair_edge_cents"], errors="coerce").median()),
                }
            )
    return rows


def build_combined(summary: pd.DataFrame, block_summary: Dict[tuple[str, str], Dict[str, Any]]) -> pd.DataFrame:
    rows: List[Dict[str, Any]] = []
    for candidate in CANDIDATES:
        cur = summary[(summary["dataset"].eq("current")) & summary["candidate"].eq(candidate.name)]
        v21 = summary[(summary["dataset"].eq("v21")) & summary["candidate"].eq(candidate.name)]
        if cur.empty or v21.empty:
            continue
        cur_row = cur.iloc[0]
        v21_row = v21.iloc[0]
        cur_block = block_summary.get(("current", candidate.name), {})
        v21_block = block_summary.get(("v21", candidate.name), {})
        min_block_rate = min(
            float(cur_block.get("positive_coverage_rate", 0.0)),
            float(v21_block.get("positive_coverage_rate", 0.0)),
        )
        worst_block = min(
            float(cur_block.get("worst_block_net_pnl_cents", 0.0)),
            float(v21_block.get("worst_block_net_pnl_cents", 0.0)),
        )
        coverage = bool(cur_row["coverage_pass"]) and bool(v21_row["coverage_pass"])
        all_splits = bool(cur_row["all_splits_positive"]) and bool(v21_row["all_splits_positive"])
        oos = bool(cur_row["oos_positive"]) and bool(v21_row["oos_positive"])
        robust = coverage and all_splits and oos and min_block_rate >= POSITIVE_BLOCK_RATE_FLOOR
        rows.append(
            {
                "candidate": candidate.name,
                "label": str(cur_row["label"]),
                "combined_all_net_pnl_cents": float(cur_row["all_net_pnl_cents"] or 0.0)
                + float(v21_row["all_net_pnl_cents"] or 0.0),
                "combined_oos_net_pnl_cents": float(cur_row["validation_net_pnl_cents"] or 0.0)
                + float(cur_row["holdout_net_pnl_cents"] or 0.0)
                + float(v21_row["validation_net_pnl_cents"] or 0.0)
                + float(v21_row["holdout_net_pnl_cents"] or 0.0),
                "current_net_pnl_cents": float(cur_row["all_net_pnl_cents"] or 0.0),
                "v21_net_pnl_cents": float(v21_row["all_net_pnl_cents"] or 0.0),
                "current_accuracy": cur_row["all_accuracy"],
                "v21_accuracy": v21_row["all_accuracy"],
                "current_coverage": cur_row["all_coverage"],
                "v21_coverage": v21_row["all_coverage"],
                "coverage": coverage,
                "all_splits": all_splits,
                "oos": oos,
                "min_positive_coverage_block_rate": min_block_rate,
                "worst_block_net_pnl_cents": worst_block,
                "robust": robust,
            }
        )
    return pd.DataFrame(rows).sort_values(
        ["robust", "combined_all_net_pnl_cents"], ascending=[False, False]
    ).reset_index(drop=True)


def write_report(
    generated: str,
    combined: pd.DataFrame,
    summary: pd.DataFrame,
) -> None:
    lines = [
        "# Volatility Term-Structure Guard Audit",
        "",
        f"Generated UTC: `{generated}`",
        "",
        "## Scope",
        "",
        "- Research-only audit; no orders are submitted and no bot files or live processes are touched.",
        "- Tests fixed short/medium/long realized-volatility ratio guards on high-coverage book/score priors.",
        "- Strict pass requires current+v21 coverage, positive validation/holdout, positive all splits, and block stability.",
        "",
        "## Combined Read",
        "",
        "| candidate | combined net | combined OOS | current/v21 net | current/v21 acc | current/v21 cov | coverage | all splits | OOS | min block+ | worst block | robust |",
        "|---|---:|---:|---:|---:|---:|---|---|---|---:|---:|---|",
    ]
    if combined.empty:
        lines.append("| none | 0.0c | 0.0c | NA | NA | NA | False | False | False | 0.00% | 0.0c | False |")
    else:
        for _, row in combined.head(40).iterrows():
            lines.append(
                f"| `{row['candidate']}` | {fmt_cents(row['combined_all_net_pnl_cents'])} | "
                f"{fmt_cents(row['combined_oos_net_pnl_cents'])} | "
                f"{fmt_cents(row['current_net_pnl_cents'])}/{fmt_cents(row['v21_net_pnl_cents'])} | "
                f"{pct(row['current_accuracy'])}/{pct(row['v21_accuracy'])} | "
                f"{pct(row['current_coverage'])}/{pct(row['v21_coverage'])} | "
                f"{bool(row['coverage'])} | {bool(row['all_splits'])} | {bool(row['oos'])} | "
                f"{pct(row['min_positive_coverage_block_rate'])} | {fmt_cents(row['worst_block_net_pnl_cents'])} | "
                f"{bool(row['robust'])} |"
            )
    lines += [
        "",
        "## Split Summary",
        "",
        "| dataset | candidate | all net/ROI | all acc/cov | train net | validation net | holdout net | coverage | all splits | OOS |",
        "|---|---|---:|---:|---:|---:|---:|---|---|---|",
    ]
    for _, row in summary.sort_values(["candidate", "dataset"]).iterrows():
        lines.append(
            f"| {row['dataset']} | `{row['candidate']}` | "
            f"{fmt_cents(row['all_net_pnl_cents'])}/{fmt_roi(row['all_net_roi_on_cost'])} | "
            f"{pct(row['all_accuracy'])}/{pct(row['all_coverage'])} | "
            f"{fmt_cents(row['train_net_pnl_cents'])} | {fmt_cents(row['validation_net_pnl_cents'])} | "
            f"{fmt_cents(row['holdout_net_pnl_cents'])} | "
            f"{bool(row['coverage_pass'])} | {bool(row['all_splits_positive'])} | {bool(row['oos_positive'])} |"
        )
    robust = combined[combined["robust"].astype(bool)] if not combined.empty else pd.DataFrame()
    lines += ["", "## Read", ""]
    if robust.empty:
        lines.append("- No volatility term-structure guard clears the cross-dataset robustness gates.")
    else:
        names = ", ".join(f"`{name}`" for name in robust["candidate"].head(10))
        lines.append(f"- Robust diagnostic candidates found: {names}. They still require frozen strict forward validation.")
    REPORT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    generated = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%SZ")
    datasets = [
        ("current", add_vol_features(load_side_rows())),
        ("v21", add_vol_features(load_v21_side_rows())),
    ]
    summary_rows: List[Dict[str, Any]] = []
    block_rows_all: List[Dict[str, Any]] = []
    slice_rows_all: List[Dict[str, Any]] = []
    for dataset, side_rows in datasets:
        base = market_base(side_rows)
        for candidate in CANDIDATES:
            selected = selected_for_candidate(side_rows, base, candidate)
            summary_rows.append(flatten_summary(dataset, candidate, base, selected))
            block_rows_all.extend(block_rows(dataset, candidate.name, base, selected))
            slice_rows_all.extend(vol_slice_rows(dataset, candidate.name, selected))

    summary = pd.DataFrame(summary_rows)
    blocks = pd.DataFrame(block_rows_all)
    slices = pd.DataFrame(slice_rows_all)
    block_summary = supported_block_summary(blocks)
    combined = build_combined(summary, block_summary)

    write_report(generated, combined, summary)
    payload = {
        "generated_utc": generated,
        "thresholds": {
            "market_coverage_floor": MARKET_COVERAGE_FLOOR,
            "positive_block_rate_floor": POSITIVE_BLOCK_RATE_FLOOR,
        },
        "combined": combined.to_dict(orient="records"),
        "summary": summary.to_dict(orient="records"),
    }
    REPORT_JSON.write_text(json.dumps(clean_json_local(payload), indent=2), encoding="utf-8")
    summary.to_csv(SUMMARY_CSV, index=False)
    blocks.to_csv(BLOCKS_CSV, index=False)
    slices.to_csv(SLICES_CSV, index=False)
    print("Volatility term-structure guard audit complete")
    print(f"robust={int(combined['robust'].sum()) if not combined.empty else 0}")
    print(f"report={REPORT_MD}")


if __name__ == "__main__":
    main()
