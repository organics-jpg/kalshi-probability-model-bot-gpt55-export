"""Score/book physics guard audit for high-coverage BTC 15m priors.

The strongest high-coverage historical rows are still vulnerable to unstable
chronological blocks. This audit tests a small, predeclared set of simple
physics guards on top of the score/book families: touch risk, realized-vol
cushion, short-memory drift, adverse movement, book/Brownian disagreement, and
realized-vol regime.

Research-only: no orders are submitted and no bot files or live processes are
modified. A diagnostic pass here would still require strict pre-registered
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
    market_base,
    pct,
    load_side_rows,
)
from probe_profit_touch_hazard_frontier import add_touch_hazard_scores


REPORT_MD = OUT_DIR / "score_physics_guard_audit_latest.md"
REPORT_JSON = OUT_DIR / "score_physics_guard_audit_latest.json"
SUMMARY_CSV = OUT_DIR / "score_physics_guard_summary_latest.csv"
BLOCKS_CSV = OUT_DIR / "score_physics_guard_blocks_latest.csv"
SLICES_CSV = OUT_DIR / "score_physics_guard_slices_latest.csv"

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


def filter_name(filters: Tuple[Filter, ...]) -> str:
    if not filters:
        return "none"
    tokens = []
    for feature, op, threshold in filters:
        token = f"{feature}_{op}_{threshold:g}"
        token = token.replace("<=", "le").replace(">=", "ge").replace(".", "p").replace("-", "m")
        tokens.append(token)
    return "__".join(tokens)


BASE_SPECS = [
    ("score_m60_edge_m5", "score_min_book_rv15", 0.60, -5.0, 95.0, 120.0, False),
    ("score_m60", "score_min_book_rv15", 0.60, -100.0, 95.0, 120.0, False),
    ("book_margin", "book_p_side", 0.60, -100.0, 95.0, 120.0, True),
    ("hazard45_touch80", "hazard_discounted_mean_15", 0.45, -100.0, 80.0, 60.0, False),
]

SINGLE_FILTERS: List[Tuple[Filter, ...]] = [
    (),
    (("touch_loss_rv_15m", "<=", 0.95),),
    (("touch_loss_rv_15m", "<=", 0.90),),
    (("touch_loss_rv_15m", "<=", 0.85),),
    (("touch_loss_rv_15m", "<=", 0.80),),
    (("touch_loss_rv_15m", ">=", 0.80),),
    (("touch_loss_rv_15m", ">=", 0.90),),
    (("margin_per_rv_sigma_15m", ">=", 0.10),),
    (("margin_per_rv_sigma_15m", ">=", 0.25),),
    (("margin_per_rv_sigma_15m", ">=", 0.50),),
    (("brownian_p_rv_15m", ">=", 0.55),),
    (("brownian_p_rv_15m", ">=", 0.60),),
    (("drift_p_5m_rv_15m", ">=", 0.55),),
    (("drift_p_5m_rv_15m", ">=", 0.60),),
    (("adverse_move_15m", "<=", 10.0),),
    (("adverse_move_15m", "<=", 50.0),),
    (("abs_book_rv15_gap", "<=", 0.20),),
    (("abs_book_rv15_gap", "<=", 0.30),),
    (("rv_sigma_t_15m", "<=", 75.0),),
    (("rv_sigma_t_15m", "<=", 100.0),),
]

PAIR_PREFIXES = [
    ("touch_loss_rv_15m", "<=", 0.90),
    ("margin_per_rv_sigma_15m", ">=", 0.10),
    ("brownian_p_rv_15m", ">=", 0.55),
    ("drift_p_5m_rv_15m", ">=", 0.55),
]
PAIR_SUFFIXES = [
    ("adverse_move_15m", "<=", 50.0),
    ("abs_book_rv15_gap", "<=", 0.30),
    ("rv_sigma_t_15m", "<=", 100.0),
]


def make_candidates() -> List[Candidate]:
    filter_sets: List[Tuple[Filter, ...]] = list(SINGLE_FILTERS)
    for first in PAIR_PREFIXES:
        for second in PAIR_SUFFIXES:
            filter_sets.append((first, second))

    candidates: List[Candidate] = []
    for prefix, chooser, min_score, edge_floor, ask_max, min_sec, margin_gate in BASE_SPECS:
        for filters in filter_sets:
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
    fees = pd.Series([estimated_order_fee_cents(value, 1) for value in chosen["ask_cents"].fillna(100.0)], index=chosen.index)
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
    row["coverage_pass"] = all((metrics[split]["coverage"] or 0.0) >= MARKET_COVERAGE_FLOOR for split in ["all", "train", "validation", "holdout"])
    row["all_splits_positive"] = all((metrics[split]["net_pnl_cents"] or 0.0) > 0.0 for split in ["all", "train", "validation", "holdout"])
    row["oos_positive"] = all((metrics[split]["net_pnl_cents"] or 0.0) > 0.0 for split in ["validation", "holdout"])
    row["all_median_edge"] = (
        float(pd.to_numeric(selected.get("candidate_fair_edge_cents"), errors="coerce").median()) if not selected.empty else None
    )
    return row


def build_combined(summary: pd.DataFrame, block_summary: Dict[tuple[str, str], Dict[str, Any]]) -> pd.DataFrame:
    rows: List[Dict[str, Any]] = []
    for candidate in CANDIDATES:
        cur = summary[(summary["dataset"].eq("current")) & summary["candidate"].eq(candidate.name)]
        v21 = summary[(summary["dataset"].eq("v21")) & summary["candidate"].eq(candidate.name)]
        if cur.empty or v21.empty:
            continue
        cur_row = cur.iloc[0]
        v21_row = v21.iloc[0]
        min_block_rate = min(
            float(block_summary.get(("current", candidate.name), {}).get("positive_coverage_rate", 0.0)),
            float(block_summary.get(("v21", candidate.name), {}).get("positive_coverage_rate", 0.0)),
        )
        worst_block = min(
            float(block_summary.get(("current", candidate.name), {}).get("worst_block_net_pnl_cents", 0.0)),
            float(block_summary.get(("v21", candidate.name), {}).get("worst_block_net_pnl_cents", 0.0)),
        )
        coverage = bool(cur_row["coverage_pass"]) and bool(v21_row["coverage_pass"])
        all_splits = bool(cur_row["all_splits_positive"]) and bool(v21_row["all_splits_positive"])
        oos = bool(cur_row["oos_positive"]) and bool(v21_row["oos_positive"])
        robust = coverage and all_splits and oos and min_block_rate >= POSITIVE_BLOCK_RATE_FLOOR
        rows.append(
            {
                "candidate": candidate.name,
                "label": candidate.label,
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
    return pd.DataFrame(rows).sort_values(["robust", "combined_all_net_pnl_cents"], ascending=[False, False]).reset_index(drop=True)


def write_report(generated: str, combined: pd.DataFrame, summary: pd.DataFrame, blocks: pd.DataFrame, slices: pd.DataFrame) -> None:
    lines = [
        "# Score Physics Guard Audit",
        "",
        f"Generated UTC: `{generated}`",
        "",
        "## Scope",
        "",
        "- Research-only audit; no orders are submitted and no bot files or live processes are touched.",
        "- Tests a small, predeclared set of simple physics guards on high-coverage score/book priors.",
        "- Strict diagnostic pass requires current+v21 coverage, positive validation/holdout, positive all splits, and block stability.",
        "",
        "## Combined Read",
        "",
        "| candidate | robust | combined net | OOS net | current/v21 net | current/v21 acc | current/v21 cov | min block+ | worst block |",
        "|---|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    if combined.empty:
        lines.append("| none | False | 0.0c | 0.0c | NA | NA | NA | 0.00% | 0.0c |")
    else:
        for _, row in combined.head(30).iterrows():
            lines.append(
                f"| `{row['candidate']}` | {bool(row['robust'])} | "
                f"{fmt_cents(row['combined_all_net_pnl_cents'])} | {fmt_cents(row['combined_oos_net_pnl_cents'])} | "
                f"{fmt_cents(row['current_net_pnl_cents'])}/{fmt_cents(row['v21_net_pnl_cents'])} | "
                f"{pct(row['current_accuracy'])}/{pct(row['v21_accuracy'])} | "
                f"{pct(row['current_coverage'])}/{pct(row['v21_coverage'])} | "
                f"{pct(row['min_positive_coverage_block_rate'])} | {fmt_cents(row['worst_block_net_pnl_cents'])} |"
            )

    lines += [
        "",
        "## Split Summary",
        "",
        "| dataset | candidate | all net/ROI | all acc/cov | train net | validation net | holdout net | median edge | coverage | all splits | OOS |",
        "|---|---|---:|---:|---:|---:|---:|---:|---|---|---|",
    ]
    for _, row in summary.sort_values(["candidate", "dataset"]).iterrows():
        if str(row["candidate"]) not in set(combined.head(30)["candidate"].astype(str)):
            continue
        lines.append(
            f"| {row['dataset']} | `{row['candidate']}` | "
            f"{fmt_cents(row['all_net_pnl_cents'])}/{fmt_roi(row['all_net_roi_on_cost'])} | "
            f"{pct(row['all_accuracy'])}/{pct(row['all_coverage'])} | "
            f"{fmt_cents(row['train_net_pnl_cents'])} | {fmt_cents(row['validation_net_pnl_cents'])} | "
            f"{fmt_cents(row['holdout_net_pnl_cents'])} | {fmt_cents(row.get('all_median_edge'))} | "
            f"{bool(row['coverage_pass'])} | {bool(row['all_splits_positive'])} | {bool(row['oos_positive'])} |"
        )

    lines += ["", "## Block Summary", ""]
    block_summary = supported_block_summary(blocks)
    if not block_summary:
        lines.append("- No supported block rows.")
    else:
        top_candidates = set(combined.head(30)["candidate"].astype(str))
        lines += [
            "| dataset | candidate | blocks | positive+coverage blocks | worst block |",
            "|---|---|---:|---:|---:|",
        ]
        for (dataset, candidate), data in sorted(block_summary.items()):
            if candidate not in top_candidates:
                continue
            lines.append(
                f"| {dataset} | `{candidate}` | {data['blocks']} | "
                f"{pct(data['positive_coverage_rate'])} | {fmt_cents(data['worst_block_net_pnl_cents'])} |"
            )

    lines += [
        "",
        "## Worst Supported Slices",
        "",
        f"Only slices with at least `{MIN_SLICE_MARKETS}` selected markets are shown.",
        "",
    ]
    if slices.empty:
        lines.append("- No supported slices.")
    else:
        lines += [
            "| dataset | candidate | slice | markets | wins/losses | net | net/market | median ask | median edge |",
            "|---|---|---|---:|---:|---:|---:|---:|---:|",
        ]
        for _, row in slices.sort_values("net_pnl_cents").head(18).iterrows():
            lines.append(
                f"| {row['dataset']} | `{row['candidate']}` | {row['slice']} | {int(row['markets'])} | "
                f"{int(row['wins'])}/{int(row['losses'])} | {fmt_cents(row['net_pnl_cents'])} | "
                f"{fmt_cents(row['net_per_market_cents'])} | {fmt_cents(row['median_ask'])} | "
                f"{fmt_cents(row['median_edge'])} |"
            )

    robust_count = int(combined["robust"].sum()) if not combined.empty else 0
    lines += ["", "## Read", ""]
    if robust_count:
        lines.append("- At least one physics-guard row clears diagnostic robustness; it still needs strict forward registration.")
    else:
        lines.append("- No physics-guard row clears the full robustness gate.")

    REPORT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")
    (OUT_DIR / f"score_physics_guard_audit_{generated}.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    generated = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%SZ")
    datasets = {
        "current": add_touch_hazard_scores(load_side_rows()),
        "v21": add_touch_hazard_scores(load_v21_side_rows()),
    }

    summary_rows: List[Dict[str, Any]] = []
    block_out: List[Dict[str, Any]] = []
    slice_out: List[Dict[str, Any]] = []
    for dataset, side_rows in datasets.items():
        base = market_base(side_rows)
        for candidate in CANDIDATES:
            selected = selected_for_candidate(side_rows, base, candidate)
            summary_rows.append(flatten_summary(dataset, candidate, base, selected))
            block_out.extend(block_rows(dataset, candidate.name, base, selected))
            slice_out.extend(slice_rows(dataset, candidate.name, selected))

    summary = pd.DataFrame(summary_rows)
    blocks = pd.DataFrame(block_out)
    slices = pd.DataFrame(slice_out)
    combined = build_combined(summary, supported_block_summary(blocks))

    summary.to_csv(SUMMARY_CSV, index=False)
    blocks.to_csv(BLOCKS_CSV, index=False)
    slices.to_csv(SLICES_CSV, index=False)
    payload = {
        "generated_utc": generated,
        "market_coverage_floor": MARKET_COVERAGE_FLOOR,
        "positive_block_rate_floor": POSITIVE_BLOCK_RATE_FLOOR,
        "candidates": [
            {
                "name": candidate.name,
                "label": candidate.label,
                "filters": candidate.filters,
            }
            for candidate in CANDIDATES
        ],
        "combined": combined.to_dict(orient="records"),
        "summary": summary.to_dict(orient="records"),
    }
    REPORT_JSON.write_text(json.dumps(clean_json_local(payload), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (OUT_DIR / f"score_physics_guard_audit_{generated}.json").write_text(
        json.dumps(clean_json_local(payload), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    write_report(generated, combined, summary, blocks, slices)
    print("Score physics guard audit complete")
    print(f"robust={int(combined['robust'].sum()) if not combined.empty else 0}")
    print(f"report={REPORT_MD}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
