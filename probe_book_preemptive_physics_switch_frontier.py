"""Preemptive physics switch frontier for BTC 15m book-margin markets.

The same-heartbeat weak-book switch did not fire on the recent instructive
failure because the cheaper opposite physics row appeared before book_margin
became eligible. This probe tests the causal version of that idea:

1. book_margin remains the default high-coverage market entry.
2. if the eventual book entry is weak, an earlier opposite physics entry in the
   same market may preempt it, provided it is cheap, recent, and strong enough.

Research-only: no orders are submitted and no live bot files or processes are
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
from probe_cross_dataset_profit_frontier import enrich_selected, fmt_cents, metrics_for
from probe_market_interval_80coverage import (
    MARKET_COVERAGE_FLOOR,
    OUT_DIR,
    Policy,
    add_scores,
    choose_decision_sides,
    clean_json,
    gate_mask,
    load_side_rows,
    market_base,
    pct,
    select_markets_from_chosen,
)
from probe_ridge_physics_fair_value_frontier import block_rows, block_stability, combine


REPORT_MD = OUT_DIR / "book_preemptive_physics_switch_frontier_latest.md"
REPORT_JSON = OUT_DIR / "book_preemptive_physics_switch_frontier_latest.json"
CSV_LATEST = OUT_DIR / "book_preemptive_physics_switch_frontier_latest.csv"
BLOCKS_LATEST = OUT_DIR / "book_preemptive_physics_switch_blocks_latest.csv"

BASE_POLICY = Policy("book_p_side", 0.60, 95.0, 120.0, "margin_rv15>=0")


@dataclass(frozen=True)
class PreemptSpec:
    name: str
    alt_chooser: str
    max_book_score: float
    min_alt_score: float
    max_alt_ask: float
    min_alt_cheaper_by: float
    max_alt_age_sec: float

    @property
    def label(self) -> str:
        if self.alt_chooser == "baseline":
            return BASE_POLICY.label
        return (
            f"base={BASE_POLICY.label}; preempt_if_book<={self.max_book_score:g}; "
            f"alt={self.alt_chooser}>={self.min_alt_score:g}; alt_ask<={self.max_alt_ask:g}; "
            f"alt_cheaper_by>={self.min_alt_cheaper_by:g}c; alt_age<={self.max_alt_age_sec:g}s"
        )


def clean_json_local(value: Any) -> Any:
    if isinstance(value, pd.Timestamp):
        return value.isoformat()
    if isinstance(value, dict):
        return {str(k): clean_json_local(v) for k, v in value.items()}
    if isinstance(value, list):
        return [clean_json_local(v) for v in value]
    return clean_json(value)


def fmt_num(value: Optional[float], digits: int = 4) -> str:
    if value is None or not math.isfinite(float(value)):
        return "NA"
    return f"{float(value):.{digits}f}"


def make_specs() -> List[PreemptSpec]:
    specs = [PreemptSpec("book_margin_baseline", "baseline", 0.0, 0.0, 100.0, 0.0, 0.0)]
    for alt in [
        "brownian_p_rv_15m",
        "score_mean_book_rv15",
        "score_regime_blend",
    ]:
        for max_book in [0.65, 0.70]:
            for min_alt in [0.55, 0.60]:
                for max_ask in [60.0, 70.0]:
                    for cheaper_by in [0.0, 5.0]:
                        for max_age in [120.0, 300.0]:
                            specs.append(
                                PreemptSpec(
                                    name=(
                                        f"preempt_{alt}_book{max_book:g}_alt{min_alt:g}_ask{max_ask:g}_"
                                        f"cheap{cheaper_by:g}_age{max_age:g}"
                                    ),
                                    alt_chooser=alt,
                                    max_book_score=max_book,
                                    min_alt_score=min_alt,
                                    max_alt_ask=max_ask,
                                    min_alt_cheaper_by=cheaper_by,
                                    max_alt_age_sec=max_age,
                                )
                            )
    return specs


def prepare_rows(rows: pd.DataFrame, base: pd.DataFrame) -> pd.DataFrame:
    out = add_scores(rows).merge(base[["market", "split"]], on="market", how="inner")
    out["entry_dt"] = pd.to_datetime(out["entry_dt"], utc=True, errors="coerce")
    for col in [
        "book_p_side",
        "brownian_p_rv_15m",
        "brownian_p_rv_30m",
        "score_mean_book_rv15",
        "score_mean_book_rv15_drift5",
        "score_regime_blend",
        "ask_cents",
        "seconds_to_close",
        "margin_per_rv_sigma_15m",
    ]:
        if col not in out.columns:
            out[col] = np.nan
        out[col] = pd.to_numeric(out[col], errors="coerce")
    return out


def select_book(prepared: pd.DataFrame) -> pd.DataFrame:
    chosen = choose_decision_sides(prepared, BASE_POLICY.chooser)
    if chosen.empty:
        return enrich_selected(chosen)
    return select_markets_from_chosen(chosen, BASE_POLICY)


def select_spec(prepared: pd.DataFrame, book_selected: pd.DataFrame, alt_chosen: pd.DataFrame, spec: PreemptSpec) -> pd.DataFrame:
    if book_selected.empty:
        return enrich_selected(book_selected)
    if spec.alt_chooser == "baseline" or alt_chosen.empty:
        selected = book_selected.copy()
        selected["candidate"] = spec.name
        selected["action_taken"] = "book"
        selected["overlay"] = "book_margin_base"
        return enrich_selected(selected)

    selected_rows: List[pd.Series] = []
    alt = alt_chosen.copy()
    alt["entry_dt"] = pd.to_datetime(alt["entry_dt"], utc=True, errors="coerce")
    alt[spec.alt_chooser] = pd.to_numeric(alt[spec.alt_chooser], errors="coerce")
    alt["ask_cents"] = pd.to_numeric(alt["ask_cents"], errors="coerce")

    for _, book in book_selected.sort_values(["market", "entry_dt"]).iterrows():
        book_score = float(book.get("book_p_side", np.nan))
        book_ask = float(book.get("ask_cents", np.nan))
        book_dt = pd.to_datetime(book.get("entry_dt"), utc=True, errors="coerce")
        use_book = book.copy()
        use_book["action_taken"] = "book"
        use_book["overlay"] = "book_margin_base"
        if not math.isfinite(book_score) or book_score > spec.max_book_score or pd.isna(book_dt):
            selected_rows.append(use_book)
            continue
        pool = alt[
            alt["market"].eq(book["market"])
            & alt["side"].astype(str).ne(str(book["side"]))
            & alt["entry_dt"].le(book_dt)
            & alt["entry_dt"].ge(book_dt - pd.Timedelta(seconds=spec.max_alt_age_sec))
            & alt[spec.alt_chooser].ge(spec.min_alt_score)
            & alt["ask_cents"].le(spec.max_alt_ask)
            & (book_ask - alt["ask_cents"]).ge(spec.min_alt_cheaper_by)
        ].copy()
        if pool.empty:
            selected_rows.append(use_book)
            continue
        chosen = pool.sort_values(["entry_dt", spec.alt_chooser], ascending=[True, False]).iloc[0].copy()
        chosen["action_taken"] = "preempt"
        chosen["overlay"] = spec.name
        chosen["book_entry_dt"] = book_dt
        chosen["book_side"] = book["side"]
        chosen["book_ask_cents"] = book_ask
        chosen["book_score_value"] = book_score
        chosen["alt_score_value"] = chosen[spec.alt_chooser]
        chosen["alt_age_sec"] = (book_dt - pd.to_datetime(chosen["entry_dt"], utc=True)).total_seconds()
        selected_rows.append(chosen)

    selected = pd.DataFrame(selected_rows).sort_values(["entry_dt", "market"]).reset_index(drop=True)
    selected["candidate"] = spec.name
    return enrich_selected(selected)


def row_for(dataset: str, spec: PreemptSpec, base: pd.DataFrame, selected: pd.DataFrame) -> Dict[str, Any]:
    metrics = metrics_for(base, selected)
    actions = selected.get("action_taken", pd.Series(dtype=object)).fillna("book").astype(str) if not selected.empty else pd.Series(dtype=object)
    row: Dict[str, Any] = {
        "dataset": dataset,
        "candidate": spec.name,
        "label": spec.label,
        "alt_chooser": spec.alt_chooser,
        "max_book_score": spec.max_book_score,
        "min_alt_score": spec.min_alt_score,
        "max_alt_ask": spec.max_alt_ask,
        "min_alt_cheaper_by": spec.min_alt_cheaper_by,
        "max_alt_age_sec": spec.max_alt_age_sec,
        "preempt_selected": int(actions.eq("preempt").sum()) if not actions.empty else 0,
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
    row["min_split_coverage"] = min((metrics[split]["coverage"] or 0.0) for split in ["train", "validation", "holdout"])
    row["min_oos_edge_cents"] = min(
        (metrics[split]["net_edge_per_selected_cents"] or -100.0) for split in ["validation", "holdout"]
    )
    return row


def scan_dataset(dataset: str, side_rows: pd.DataFrame, specs: List[PreemptSpec]) -> tuple[pd.DataFrame, List[Dict[str, Any]], pd.DataFrame]:
    base = market_base(add_scores(side_rows))
    prepared = prepare_rows(side_rows, base)
    book_selected = select_book(prepared)
    choosers = sorted({spec.alt_chooser for spec in specs if spec.alt_chooser != "baseline"})
    chosen_cache = {chooser: choose_decision_sides(prepared, chooser) for chooser in choosers}
    rows: List[Dict[str, Any]] = []
    block_out: List[Dict[str, Any]] = []
    for spec in specs:
        selected = select_spec(prepared, book_selected, chosen_cache.get(spec.alt_chooser, prepared.iloc[0:0]), spec)
        rows.append(row_for(dataset, spec, base, selected))
        block_out.extend(block_rows(dataset, spec.name, base, selected))
    return pd.DataFrame(rows), block_out, base


def scan() -> tuple[pd.DataFrame, pd.DataFrame, Dict[str, Any]]:
    specs = make_specs()
    current_rows, current_blocks, current_base = scan_dataset("current", load_side_rows(), specs)
    v21_rows, v21_blocks, v21_base = scan_dataset("v21", load_v21_side_rows(), specs)
    blocks = pd.DataFrame(current_blocks + v21_blocks)
    stability = block_stability(blocks)
    frame = combine(current_rows, v21_rows, stability)
    diagnostics = {
        "current_markets": int(len(current_base)),
        "v21_markets": int(len(v21_base)),
        "specs": int(len(specs)),
        "strict_pass_rows": int(frame["strict_pass"].sum()) if not frame.empty else 0,
    }
    return frame, blocks, diagnostics


def table_row(row: Dict[str, Any]) -> str:
    return (
        f"| `{row['label_current']}` | {row['strict_pass']} | {fmt_cents(row['combined_all_net_pnl_cents'])} | "
        f"{fmt_cents(row['combined_oos_net_pnl_cents'])} | {pct(row['min_split_coverage'])} | "
        f"{fmt_cents(row['all_net_pnl_cents_current'])}/{fmt_cents(row['all_net_pnl_cents_v21'])} | "
        f"{pct(row['all_accuracy_current'])}/{pct(row['all_accuracy_v21'])} | "
        f"{int(row['preempt_selected_current'])}/{int(row['preempt_selected_v21'])} | "
        f"{fmt_num(row['min_positive_block_rate'])} | {fmt_cents(row['worst_block_net_cents'])} |"
    )


def write_report(generated: str, frame: pd.DataFrame, diagnostics: Dict[str, Any]) -> None:
    strict = frame[frame["strict_pass"]]
    lines = [
        "# Preemptive Physics Switch Frontier",
        "",
        f"Generated UTC: `{generated}`",
        "",
        "## Scope",
        "",
        "- Research-only scan; no orders are submitted and no bot files or live processes are touched.",
        "- Preserves `book_margin` coverage but lets an earlier cheaper opposite physics row preempt a later weak book row.",
        "- Strict pass requires current+v21 coverage, positive validation/holdout, positive all splits, and block stability.",
        "",
        "## Diagnostics",
        "",
        f"- Current markets: {diagnostics['current_markets']}",
        f"- V21 markets: {diagnostics['v21_markets']}",
        f"- Candidate specs: {diagnostics['specs']}",
        f"- Strict pass rows: {diagnostics['strict_pass_rows']}",
        "",
        "## Top Rows",
        "",
        "| policy | strict | combined all net | combined OOS net | min split cov | current/v21 net | current/v21 acc | preempts current/v21 | min block+ | worst block |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for _, row in frame.head(30).iterrows():
        lines.append(table_row(row.to_dict()))
    lines += ["", "## Read", ""]
    if strict.empty:
        lines.append("- No preemptive physics switch clears the strict gate.")
    else:
        best = strict.iloc[0]
        lines.append(
            f"- Best strict diagnostic row is `{best['label_current']}` with combined all-ledger net "
            f"{fmt_cents(best['combined_all_net_pnl_cents'])}."
        )
        lines.append("- This is post-hoc research and must be forward-locked before any live use.")
    for path in [REPORT_MD, OUT_DIR / f"book_preemptive_physics_switch_frontier_{generated}.md"]:
        path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    generated = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%SZ")
    frame, blocks, diagnostics = scan()
    frame.to_csv(CSV_LATEST, index=False)
    frame.to_csv(OUT_DIR / f"book_preemptive_physics_switch_frontier_{generated}.csv", index=False)
    blocks.to_csv(BLOCKS_LATEST, index=False)
    blocks.to_csv(OUT_DIR / f"book_preemptive_physics_switch_blocks_{generated}.csv", index=False)
    write_report(generated, frame, diagnostics)
    payload = {"generated_utc": generated, "diagnostics": diagnostics, "rows": frame.to_dict("records")}
    for path in [REPORT_JSON, OUT_DIR / f"book_preemptive_physics_switch_frontier_{generated}.json"]:
        path.write_text(json.dumps(clean_json_local(payload), indent=2, sort_keys=True), encoding="utf-8")
    print("Preemptive physics switch frontier complete")
    print(f"rows={len(frame)}")
    print(f"strict_pass={diagnostics['strict_pass_rows']}")
    print(f"report={REPORT_MD}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
