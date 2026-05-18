"""Fee-aware edge gate audit for book/score probability priors.

The locked book-margin family currently admits rows from a probability
threshold alone. A recent strict miss showed a common problem with that:
`book_p_side` can clear 0.60 while the displayed ask plus fee is still above
the implied fair value. This probe tests fixed fee-aware edge gates on top of
book/score side choice across current and v21 datasets.

Research-only: no orders are submitted and no bot files or live processes are
modified. Any passing row is diagnostic only until strict pre-registered
forward evidence exists.
"""
from __future__ import annotations

import json
import math
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Dict, List

import pandas as pd

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


REPORT_MD = OUT_DIR / "book_edge_gate_robustness_audit_latest.md"
REPORT_JSON = OUT_DIR / "book_edge_gate_robustness_audit_latest.json"
SUMMARY_CSV = OUT_DIR / "book_edge_gate_robustness_summary_latest.csv"
BLOCKS_CSV = OUT_DIR / "book_edge_gate_robustness_blocks_latest.csv"
SLICES_CSV = OUT_DIR / "book_edge_gate_robustness_slices_latest.csv"

BLOCK_MARKETS = 20
MIN_BLOCK_MARKETS = 10
MIN_SLICE_MARKETS = 12
POSITIVE_BLOCK_RATE_FLOOR = 0.70


@dataclass(frozen=True)
class Candidate:
    name: str
    chooser: str
    min_score: float
    edge_floor_cents: float
    ask_max: float = 95.0
    min_seconds_to_close: float = 120.0
    margin_gate: bool = False

    @property
    def label(self) -> str:
        gate = "margin_rv15>=0" if self.margin_gate else "none"
        return (
            f"choose={self.chooser}; {self.chooser}>={self.min_score:g}; "
            f"fair_edge>={self.edge_floor_cents:g}c; ask<={self.ask_max:g}; "
            f"sec>={self.min_seconds_to_close:g}; gate={gate}"
        )


CANDIDATES = [
    # Baselines expressed in this audit's fair-edge frame.
    Candidate("book_margin_locked_equiv", "book_p_side", 0.60, -100.0, margin_gate=True),
    Candidate("score_min60_locked_equiv", "score_min_book_rv15", 0.60, -100.0),
    # Fee-aware edge floors around the observed book/ask friction band.
    Candidate("book_margin_edge_ge_m5", "book_p_side", 0.60, -5.0, margin_gate=True),
    Candidate("book_margin_edge_ge_m3", "book_p_side", 0.60, -3.0, margin_gate=True),
    Candidate("book_margin_edge_ge_0", "book_p_side", 0.60, 0.0, margin_gate=True),
    Candidate("book_margin_edge_ge_2", "book_p_side", 0.60, 2.0, margin_gate=True),
    Candidate("book_margin_edge_ge_5", "book_p_side", 0.60, 5.0, margin_gate=True),
    Candidate("book_p625_edge_ge_m3", "book_p_side", 0.625, -3.0, margin_gate=True),
    Candidate("book_p625_edge_ge_0", "book_p_side", 0.625, 0.0, margin_gate=True),
    Candidate("book_p65_edge_ge_m3", "book_p_side", 0.65, -3.0, margin_gate=True),
    Candidate("book_p65_edge_ge_0", "book_p_side", 0.65, 0.0, margin_gate=True),
    Candidate("score_min60_edge_ge_m5", "score_min_book_rv15", 0.60, -5.0),
    Candidate("score_min60_edge_ge_m3", "score_min_book_rv15", 0.60, -3.0),
    Candidate("score_min60_edge_ge_0", "score_min_book_rv15", 0.60, 0.0),
    Candidate("score_min60_edge_ge_2", "score_min_book_rv15", 0.60, 2.0),
    Candidate("score_min60_edge_ge_5", "score_min_book_rv15", 0.60, 5.0),
]


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
    chosen[candidate.chooser] = pd.to_numeric(chosen[candidate.chooser], errors="coerce")
    chosen["ask_cents"] = pd.to_numeric(chosen["ask_cents"], errors="coerce")
    chosen["seconds_to_close"] = pd.to_numeric(chosen["seconds_to_close"], errors="coerce")
    chosen["entry_fee_cents_tmp"] = [
        estimated_order_fee_cents(ask, 1) for ask in chosen["ask_cents"].fillna(100.0)
    ]
    chosen["candidate_fair_edge_cents"] = 100.0 * chosen[candidate.chooser] - (
        chosen["ask_cents"] + chosen["entry_fee_cents_tmp"]
    )
    mask = (
        chosen[candidate.chooser].ge(candidate.min_score)
        & chosen["ask_cents"].le(candidate.ask_max)
        & chosen["seconds_to_close"].ge(candidate.min_seconds_to_close)
        & chosen["candidate_fair_edge_cents"].ge(candidate.edge_floor_cents)
    )
    if candidate.margin_gate:
        mask &= pd.to_numeric(chosen["margin_per_rv_sigma_15m"], errors="coerce").ge(0.0)
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
    selected["candidate_score"] = pd.to_numeric(selected[candidate.chooser], errors="coerce") if not selected.empty else []
    return enrich_selected(selected.drop(columns=["entry_fee_cents_tmp"], errors="ignore"))


def flatten_summary(dataset: str, candidate: Candidate, base: pd.DataFrame, selected: pd.DataFrame) -> Dict[str, Any]:
    metrics = metrics_for(base, selected)
    row: Dict[str, Any] = {"dataset": dataset, "candidate": candidate.name, "label": candidate.label}
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


def block_base(base: pd.DataFrame) -> pd.DataFrame:
    out = base.copy()
    out["close_dt"] = pd.to_datetime(out["close_dt"], utc=True, errors="coerce")
    out = out.sort_values(["close_dt", "market"]).reset_index(drop=True)
    out["block_index"] = out.index // BLOCK_MARKETS
    return out


def block_rows(dataset: str, candidate: str, base: pd.DataFrame, selected: pd.DataFrame) -> List[Dict[str, Any]]:
    base_blocks = block_base(base)
    selected_blocks = selected.drop(columns=["block_index"], errors="ignore").merge(
        base_blocks[["market", "block_index"]], on="market", how="inner"
    )
    rows: List[Dict[str, Any]] = []
    for block_index, block in base_blocks.groupby("block_index", sort=True):
        part = selected_blocks[selected_blocks["block_index"].eq(block_index)]
        n = int(len(part))
        wins = int(part["win"].astype(bool).sum()) if n else 0
        net = float(pd.to_numeric(part.get("net_pnl_cents"), errors="coerce").sum()) if n else 0.0
        cost = float(pd.to_numeric(part.get("entry_cost_cents"), errors="coerce").sum()) if n else 0.0
        base_n = int(len(block))
        coverage = n / base_n if base_n else None
        rows.append(
            {
                "dataset": dataset,
                "candidate": candidate,
                "block_index": int(block_index),
                "base_markets": base_n,
                "selected_markets": n,
                "coverage": coverage,
                "wins": wins,
                "losses": n - wins,
                "accuracy": wins / n if n else None,
                "net_pnl_cents": net,
                "net_roi_on_cost": net / cost if cost else None,
                "positive": net > 0.0,
                "coverage_pass": (coverage or 0.0) >= MARKET_COVERAGE_FLOOR,
                "positive_and_coverage": net > 0.0 and (coverage or 0.0) >= MARKET_COVERAGE_FLOOR,
            }
        )
    return rows


def supported_block_summary(blocks: pd.DataFrame) -> Dict[tuple[str, str], Dict[str, Any]]:
    out: Dict[tuple[str, str], Dict[str, Any]] = {}
    if blocks.empty:
        return out
    supported = blocks[pd.to_numeric(blocks["base_markets"], errors="coerce").ge(MIN_BLOCK_MARKETS)].copy()
    for (dataset, candidate), part in supported.groupby(["dataset", "candidate"], sort=False):
        total = int(len(part))
        out[(dataset, candidate)] = {
            "blocks": total,
            "positive_blocks": int(part["positive"].astype(bool).sum()),
            "positive_coverage_blocks": int(part["positive_and_coverage"].astype(bool).sum()),
            "positive_coverage_rate": float(part["positive_and_coverage"].astype(bool).mean()) if total else 0.0,
            "worst_block_net_pnl_cents": float(pd.to_numeric(part["net_pnl_cents"], errors="coerce").min()) if total else 0.0,
        }
    return out


def slice_rows(dataset: str, candidate: str, selected: pd.DataFrame) -> List[Dict[str, Any]]:
    if selected.empty:
        return []
    work = selected.copy()
    work["candidate_score"] = pd.to_numeric(work.get("candidate_score"), errors="coerce")
    work["candidate_fair_edge_cents"] = pd.to_numeric(work.get("candidate_fair_edge_cents"), errors="coerce")
    work["ask_cents"] = pd.to_numeric(work["ask_cents"], errors="coerce")
    work["seconds_to_close"] = pd.to_numeric(work["seconds_to_close"], errors="coerce")
    definitions = {
        "split": work["split"].astype(str),
        "side": work["side"].astype(str),
        "score": pd.cut(work["candidate_score"], [-1, 0.625, 0.65, 0.70, 0.80, 2.0], include_lowest=True).astype(str),
        "edge": pd.cut(work["candidate_fair_edge_cents"], [-200, -5, -3, 0, 2, 5, 200], include_lowest=True).astype(str),
        "ask": pd.cut(work["ask_cents"], [-1, 60, 70, 80, 90, 101], include_lowest=True).astype(str),
        "time": pd.cut(work["seconds_to_close"], [-1, 600, 720, 840, 10000], include_lowest=True).astype(str),
    }
    rows: List[Dict[str, Any]] = []
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
                    "median_ask": float(part["ask_cents"].median()),
                    "median_edge": float(part["candidate_fair_edge_cents"].median()),
                }
            )
    return rows


def build_combined(summary: pd.DataFrame, block_summary: Dict[tuple[str, str], Dict[str, Any]]) -> pd.DataFrame:
    rows: List[Dict[str, Any]] = []
    for candidate in [candidate.name for candidate in CANDIDATES]:
        cur = summary[(summary["dataset"].eq("current")) & summary["candidate"].eq(candidate)]
        v21 = summary[(summary["dataset"].eq("v21")) & summary["candidate"].eq(candidate)]
        if cur.empty or v21.empty:
            continue
        cur_row = cur.iloc[0]
        v21_row = v21.iloc[0]
        cur_block = block_summary.get(("current", candidate), {})
        v21_block = block_summary.get(("v21", candidate), {})
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
                "candidate": candidate,
                "label": str(cur_row["label"]),
                "combined_all_net_pnl_cents": float(cur_row["all_net_pnl_cents"] or 0.0)
                + float(v21_row["all_net_pnl_cents"] or 0.0),
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
    path: Any,
    generated: str,
    combined: pd.DataFrame,
    summary: pd.DataFrame,
    blocks: pd.DataFrame,
    slices: pd.DataFrame,
) -> None:
    lines = [
        "# Book/Score Fee-Aware Edge Gate Robustness Audit",
        "",
        f"Generated UTC: `{generated}`",
        "",
        "## Scope",
        "",
        "- Research-only audit; no orders are submitted and no bot files or live processes are touched.",
        "- Tests whether fee-aware fair-edge gates improve the book/score probability priors without losing high coverage.",
        "- Strict pass requires current+v21 coverage, positive validation/holdout, positive all splits, and block stability.",
        "",
        "## Combined Read",
        "",
        "| candidate | combined net | current/v21 net | current/v21 acc | current/v21 cov | coverage | all splits | OOS | min block+ | worst block | robust |",
        "|---|---:|---:|---:|---:|---|---|---|---:|---:|---|",
    ]
    if combined.empty:
        lines.append("| none | 0.0c | NA | NA | NA | False | False | False | 0.00% | 0.0c | False |")
    else:
        for _, row in combined.iterrows():
            lines.append(
                f"| `{row['candidate']}` | {fmt_cents(row['combined_all_net_pnl_cents'])} | "
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
        "| dataset | candidate | all net/ROI | all acc/cov | train net | validation net | holdout net | median edge | coverage | all splits | OOS |",
        "|---|---|---:|---:|---:|---:|---:|---:|---|---|---|",
    ]
    for _, row in summary.sort_values(["candidate", "dataset"]).iterrows():
        lines.append(
            f"| {row['dataset']} | `{row['candidate']}` | "
            f"{fmt_cents(row['all_net_pnl_cents'])}/{fmt_roi(row['all_net_roi_on_cost'])} | "
            f"{pct(row['all_accuracy'])}/{pct(row['all_coverage'])} | "
            f"{fmt_cents(row['train_net_pnl_cents'])} | {fmt_cents(row['validation_net_pnl_cents'])} | "
            f"{fmt_cents(row['holdout_net_pnl_cents'])} | {fmt_cents(row.get('all_median_edge'))} | "
            f"{bool(row['coverage_pass'])} | {bool(row['all_splits_positive'])} | {bool(row['oos_positive'])} |"
        )
    lines += ["", "## Block Summary", ""]
    if blocks.empty:
        lines.append("- No block rows.")
    else:
        block_summary = supported_block_summary(blocks)
        lines += [
            "| dataset | candidate | blocks | positive blocks | positive+coverage blocks | worst block |",
            "|---|---|---:|---:|---:|---:|",
        ]
        for (dataset, candidate), data in sorted(block_summary.items()):
            lines.append(
                f"| {dataset} | `{candidate}` | {data['blocks']} | "
                f"{pct(data['positive_blocks'] / data['blocks'] if data['blocks'] else 0.0)} | "
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
        worst = slices.sort_values("net_pnl_cents").head(18)
        lines += [
            "| dataset | candidate | slice | markets | wins/losses | net | net/market | median ask | median edge |",
            "|---|---|---|---:|---:|---:|---:|---:|---:|",
        ]
        for _, row in worst.iterrows():
            lines.append(
                f"| {row['dataset']} | `{row['candidate']}` | {row['slice']} | {int(row['markets'])} | "
                f"{int(row['wins'])}/{int(row['losses'])} | {fmt_cents(row['net_pnl_cents'])} | "
                f"{fmt_cents(row['net_per_market_cents'])} | {fmt_cents(row['median_ask'])} | "
                f"{fmt_cents(row['median_edge'])} |"
            )
    lines += ["", "## Read", ""]
    robust_count = int(combined["robust"].sum()) if not combined.empty else 0
    if robust_count:
        lines.append("- At least one fee-aware edge-gated row clears the diagnostic robustness gate; strict forward validation is still required.")
    else:
        lines.append("- No fee-aware edge-gated row clears the full robustness gate.")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    generated = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%SZ")
    current_side = load_side_rows()
    v21_side = load_v21_side_rows()
    datasets = {
        "current": (market_base(current_side), current_side),
        "v21": (market_base(v21_side), v21_side),
    }
    summary_rows: List[Dict[str, Any]] = []
    block_out: List[Dict[str, Any]] = []
    slice_out: List[Dict[str, Any]] = []
    selected_payload: Dict[str, Dict[str, int]] = {}
    for dataset, (base, side_rows) in datasets.items():
        selected_payload[dataset] = {}
        for candidate in CANDIDATES:
            selected = selected_for_candidate(side_rows, base, candidate)
            selected_payload[dataset][candidate.name] = int(len(selected))
            row = flatten_summary(dataset, candidate, base, selected)
            row["all_median_edge"] = (
                float(pd.to_numeric(selected.get("candidate_fair_edge_cents"), errors="coerce").median())
                if not selected.empty
                else None
            )
            summary_rows.append(row)
            block_out.extend(block_rows(dataset, candidate.name, base, selected))
            slice_out.extend(slice_rows(dataset, candidate.name, selected))
    summary = pd.DataFrame(summary_rows)
    blocks = pd.DataFrame(block_out)
    slices = pd.DataFrame(slice_out)
    block_summary = supported_block_summary(blocks)
    combined = build_combined(summary, block_summary)

    summary.to_csv(SUMMARY_CSV, index=False)
    blocks.to_csv(BLOCKS_CSV, index=False)
    slices.to_csv(SLICES_CSV, index=False)
    payload = {
        "generated_utc": generated,
        "market_coverage_floor": MARKET_COVERAGE_FLOOR,
        "positive_block_rate_floor": POSITIVE_BLOCK_RATE_FLOOR,
        "candidates": [candidate.__dict__ | {"label": candidate.label} for candidate in CANDIDATES],
        "selected_counts": selected_payload,
        "combined": combined.to_dict(orient="records"),
        "summary": summary.to_dict(orient="records"),
    }
    REPORT_JSON.write_text(json.dumps(clean_json_local(payload), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (OUT_DIR / f"book_edge_gate_robustness_audit_{generated}.json").write_text(
        json.dumps(clean_json_local(payload), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    write_report(REPORT_MD, generated, combined, summary, blocks, slices)
    stamped_md = OUT_DIR / f"book_edge_gate_robustness_audit_{generated}.md"
    write_report(stamped_md, generated, combined, summary, blocks, slices)
    print("Book/score fee-aware edge gate robustness audit complete")
    print(f"robust={int(combined['robust'].sum()) if not combined.empty else 0}")
    print(f"report={REPORT_MD}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
