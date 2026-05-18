"""Cost/score hole audit for book/score probability priors.

Recent strict misses and robustness slices show a repeated weak region: rows
with only moderate side probability but expensive asks. This probe tests fixed
veto rules for that region on top of the high-coverage book/score priors.

Research-only: no orders are submitted and no bot files or live processes are
modified. Any passing row is diagnostic only until strict pre-registered
forward evidence exists.
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

import pandas as pd

from probe_book_edge_gate_robustness_audit import (
    BLOCK_MARKETS,
    MIN_BLOCK_MARKETS,
    MIN_SLICE_MARKETS,
    POSITIVE_BLOCK_RATE_FLOOR,
    block_rows,
    clean_json_local,
    flatten_summary,
    slice_rows,
    supported_block_summary,
)
from probe_cross_dataset_interval_frontier import load_v21_side_rows
from probe_cross_dataset_profit_frontier import enrich_selected, estimated_order_fee_cents, fmt_cents, fmt_roi
from probe_market_interval_80coverage import (
    MARKET_COVERAGE_FLOOR,
    OUT_DIR,
    choose_decision_sides,
    load_side_rows,
    market_base,
    pct,
)


REPORT_MD = OUT_DIR / "book_cost_score_hole_audit_latest.md"
REPORT_JSON = OUT_DIR / "book_cost_score_hole_audit_latest.json"
SUMMARY_CSV = OUT_DIR / "book_cost_score_hole_summary_latest.csv"
BLOCKS_CSV = OUT_DIR / "book_cost_score_hole_blocks_latest.csv"
SLICES_CSV = OUT_DIR / "book_cost_score_hole_slices_latest.csv"


@dataclass(frozen=True)
class Candidate:
    name: str
    chooser: str
    min_score: float
    ask_max: float = 95.0
    min_seconds_to_close: float = 120.0
    margin_gate: bool = False
    low_score_ceiling: Optional[float] = None
    costly_ask_floor: Optional[float] = None
    near_score_floor: Optional[float] = None
    near_score_ceiling: Optional[float] = None
    near_ask_floor: Optional[float] = None
    near_ask_ceiling: Optional[float] = None
    high_ask_score_floor: Optional[float] = None
    high_ask_floor: Optional[float] = None

    @property
    def label(self) -> str:
        gates = []
        if self.margin_gate:
            gates.append("margin_rv15>=0")
        if self.low_score_ceiling is not None and self.costly_ask_floor is not None:
            gates.append(f"not(score<{self.low_score_ceiling:g} and ask>={self.costly_ask_floor:g})")
        if (
            self.near_score_floor is not None
            and self.near_score_ceiling is not None
            and self.near_ask_floor is not None
            and self.near_ask_ceiling is not None
        ):
            gates.append(
                f"not({self.near_score_floor:g}<=score<{self.near_score_ceiling:g} "
                f"and {self.near_ask_floor:g}<=ask<={self.near_ask_ceiling:g})"
            )
        if self.high_ask_score_floor is not None and self.high_ask_floor is not None:
            gates.append(f"ask<{self.high_ask_floor:g} or score>={self.high_ask_score_floor:g}")
        gate_text = "; ".join(gates) if gates else "none"
        return (
            f"choose={self.chooser}; score>={self.min_score:g}; ask<={self.ask_max:g}; "
            f"sec>={self.min_seconds_to_close:g}; gates={gate_text}"
        )


CANDIDATES = [
    Candidate("book_margin_locked_equiv", "book_p_side", 0.60, margin_gate=True),
    Candidate("score_min60_locked_equiv", "score_min_book_rv15", 0.60),
    Candidate("book_skip_score_lt65_ask_ge70", "book_p_side", 0.60, margin_gate=True, low_score_ceiling=0.65, costly_ask_floor=70.0),
    Candidate("book_skip_score_lt70_ask_ge70", "book_p_side", 0.60, margin_gate=True, low_score_ceiling=0.70, costly_ask_floor=70.0),
    Candidate("book_skip_score625_65_ask60_80", "book_p_side", 0.60, margin_gate=True, near_score_floor=0.625, near_score_ceiling=0.65, near_ask_floor=60.0, near_ask_ceiling=80.0),
    Candidate("book_skip_score60_65_ask60_80", "book_p_side", 0.60, margin_gate=True, near_score_floor=0.60, near_score_ceiling=0.65, near_ask_floor=60.0, near_ask_ceiling=80.0),
    Candidate("book_highask_needs_score70", "book_p_side", 0.60, margin_gate=True, high_ask_floor=70.0, high_ask_score_floor=0.70),
    Candidate("book_highask_needs_score75", "book_p_side", 0.60, margin_gate=True, high_ask_floor=70.0, high_ask_score_floor=0.75),
    Candidate("book_ask_le70", "book_p_side", 0.60, ask_max=70.0, margin_gate=True),
    Candidate("book_ask_le65", "book_p_side", 0.60, ask_max=65.0, margin_gate=True),
    Candidate("score_skip_score_lt65_ask_ge70", "score_min_book_rv15", 0.60, low_score_ceiling=0.65, costly_ask_floor=70.0),
    Candidate("score_skip_score_lt70_ask_ge70", "score_min_book_rv15", 0.60, low_score_ceiling=0.70, costly_ask_floor=70.0),
    Candidate("score_skip_score625_65_ask60_80", "score_min_book_rv15", 0.60, near_score_floor=0.625, near_score_ceiling=0.65, near_ask_floor=60.0, near_ask_ceiling=80.0),
    Candidate("score_skip_score60_65_ask60_80", "score_min_book_rv15", 0.60, near_score_floor=0.60, near_score_ceiling=0.65, near_ask_floor=60.0, near_ask_ceiling=80.0),
    Candidate("score_highask_needs_score70", "score_min_book_rv15", 0.60, high_ask_floor=70.0, high_ask_score_floor=0.70),
    Candidate("score_highask_needs_score75", "score_min_book_rv15", 0.60, high_ask_floor=70.0, high_ask_score_floor=0.75),
    Candidate("score_ask_le70", "score_min_book_rv15", 0.60, ask_max=70.0),
    Candidate("score_ask_le65", "score_min_book_rv15", 0.60, ask_max=65.0),
]


def selected_for_candidate(side_rows: pd.DataFrame, base: pd.DataFrame, candidate: Candidate) -> pd.DataFrame:
    rows = side_rows.drop(columns=["split"], errors="ignore").merge(base[["market", "split"]], on="market", how="inner")
    chosen = choose_decision_sides(rows, candidate.chooser)
    if chosen.empty:
        return enrich_selected(chosen)
    chosen = chosen.copy()
    score = pd.to_numeric(chosen[candidate.chooser], errors="coerce")
    ask = pd.to_numeric(chosen["ask_cents"], errors="coerce")
    seconds = pd.to_numeric(chosen["seconds_to_close"], errors="coerce")
    mask = score.ge(candidate.min_score) & ask.le(candidate.ask_max) & seconds.ge(candidate.min_seconds_to_close)
    if candidate.margin_gate:
        mask &= pd.to_numeric(chosen["margin_per_rv_sigma_15m"], errors="coerce").ge(0.0)
    if candidate.low_score_ceiling is not None and candidate.costly_ask_floor is not None:
        mask &= ~(score.lt(candidate.low_score_ceiling) & ask.ge(candidate.costly_ask_floor))
    if (
        candidate.near_score_floor is not None
        and candidate.near_score_ceiling is not None
        and candidate.near_ask_floor is not None
        and candidate.near_ask_ceiling is not None
    ):
        mask &= ~(
            score.ge(candidate.near_score_floor)
            & score.lt(candidate.near_score_ceiling)
            & ask.ge(candidate.near_ask_floor)
            & ask.le(candidate.near_ask_ceiling)
        )
    if candidate.high_ask_score_floor is not None and candidate.high_ask_floor is not None:
        mask &= ask.lt(candidate.high_ask_floor) | score.ge(candidate.high_ask_score_floor)
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
    if not selected.empty:
        fees = [estimated_order_fee_cents(value, 1) for value in pd.to_numeric(selected["ask_cents"], errors="coerce").fillna(100.0)]
        selected["candidate_fair_edge_cents"] = 100.0 * selected["candidate_score"] - (
            pd.to_numeric(selected["ask_cents"], errors="coerce") + pd.Series(fees, index=selected.index)
        )
    return enrich_selected(selected)


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
    path: Any,
    generated: str,
    combined: pd.DataFrame,
    summary: pd.DataFrame,
    blocks: pd.DataFrame,
    slices: pd.DataFrame,
) -> None:
    lines = [
        "# Book Cost/Score Hole Audit",
        "",
        f"Generated UTC: `{generated}`",
        "",
        "## Scope",
        "",
        "- Research-only audit; no orders are submitted and no bot files or live processes are touched.",
        "- Tests fixed cost/score vetoes on high-coverage book/score priors.",
        "- Strict pass requires current+v21 coverage, positive validation/holdout, positive all splits, and block stability.",
        "",
        "## Combined Read",
        "",
        "| candidate | robust | combined net | OOS net | current/v21 net | current/v21 acc | current/v21 cov | min block+ | worst block |",
        "|---|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    if combined.empty:
        lines.append("| none | False | 0.0c | 0.0c | NA | NA | NA | 0.00% | 0.0c |")
    else:
        for _, row in combined.iterrows():
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
    lines += ["", "## Block Summary", ""]
    if blocks.empty:
        lines.append("- No block rows.")
    else:
        block_summary = supported_block_summary(blocks)
        lines += [
            "| dataset | candidate | blocks | positive+coverage blocks | worst block |",
            "|---|---|---:|---:|---:|",
        ]
        for (dataset, candidate), data in sorted(block_summary.items()):
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
        worst = slices.sort_values("net_pnl_cents").head(18)
        lines += [
            "| dataset | candidate | slice | markets | wins/losses | net | net/market | median ask |",
            "|---|---|---|---:|---:|---:|---:|---:|",
        ]
        for _, row in worst.iterrows():
            lines.append(
                f"| {row['dataset']} | `{row['candidate']}` | {row['slice']} | {int(row['markets'])} | "
                f"{int(row['wins'])}/{int(row['losses'])} | {fmt_cents(row['net_pnl_cents'])} | "
                f"{fmt_cents(row['net_per_market_cents'])} | {fmt_cents(row['median_ask'])} |"
            )
    robust_count = int(combined["robust"].sum()) if not combined.empty else 0
    lines += ["", "## Read", ""]
    if robust_count:
        lines.append("- At least one cost/score veto clears the diagnostic robustness gate; strict forward validation is still required.")
    else:
        lines.append("- No cost/score veto clears the full robustness gate.")
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
        "block_markets": BLOCK_MARKETS,
        "min_block_markets": MIN_BLOCK_MARKETS,
        "positive_block_rate_floor": POSITIVE_BLOCK_RATE_FLOOR,
        "candidates": [candidate.__dict__ | {"label": candidate.label} for candidate in CANDIDATES],
        "selected_counts": selected_payload,
        "combined": combined.to_dict(orient="records"),
        "summary": summary.to_dict(orient="records"),
    }
    REPORT_JSON.write_text(json.dumps(clean_json_local(payload), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (OUT_DIR / f"book_cost_score_hole_audit_{generated}.json").write_text(
        json.dumps(clean_json_local(payload), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    write_report(REPORT_MD, generated, combined, summary, blocks, slices)
    stamped_md = OUT_DIR / f"book_cost_score_hole_audit_{generated}.md"
    write_report(stamped_md, generated, combined, summary, blocks, slices)
    print("Book cost/score hole audit complete")
    print(f"robust={int(combined['robust'].sum()) if not combined.empty else 0}")
    print(f"report={REPORT_MD}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
