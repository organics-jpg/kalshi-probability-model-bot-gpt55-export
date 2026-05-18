"""Weak-book disagreement switch frontier for BTC 15m markets.

The broad book-margin baseline remains the best live high-coverage reference,
but recent failures show a specific mode: book barely clears the 0.60 threshold
while a cheaper opposite Brownian/consensus side is available and later wins.

This research-only probe preserves book-margin market coverage. It takes the
book-margin base side unless, at the same decision key, an opposite physics side
is cheaper and strong enough. The goal is to test whether "weak book, cheaper
opposite physics" is a real regime rather than another hand-fit story.

No orders are submitted and no live bot files or processes are touched.
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
)
from probe_ridge_physics_fair_value_frontier import block_rows, block_stability, combine


REPORT_MD = OUT_DIR / "book_weak_disagreement_switch_frontier_latest.md"
REPORT_JSON = OUT_DIR / "book_weak_disagreement_switch_frontier_latest.json"
CSV_LATEST = OUT_DIR / "book_weak_disagreement_switch_frontier_latest.csv"
BLOCKS_LATEST = OUT_DIR / "book_weak_disagreement_switch_blocks_latest.csv"

BASE_POLICY = Policy("book_p_side", 0.60, 95.0, 120.0, "margin_rv15>=0")


@dataclass(frozen=True)
class SwitchSpec:
    name: str
    alt_chooser: str
    max_book_score: float
    min_alt_score: float
    max_alt_ask: float
    min_alt_cheaper_by: float

    @property
    def label(self) -> str:
        if self.alt_chooser == "baseline":
            return BASE_POLICY.label
        return (
            f"base={BASE_POLICY.label}; switch_if_book<={self.max_book_score:g}; "
            f"alt={self.alt_chooser}>={self.min_alt_score:g}; alt_ask<={self.max_alt_ask:g}; "
            f"alt_cheaper_by>={self.min_alt_cheaper_by:g}c"
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


def make_specs() -> List[SwitchSpec]:
    specs = [SwitchSpec("book_margin_baseline", "baseline", 0.0, 0.0, 100.0, 0.0)]
    for alt in [
        "brownian_p_rv_15m",
        "brownian_p_rv_30m",
        "score_mean_book_rv15",
        "score_mean_book_rv15_drift5",
        "score_regime_blend",
    ]:
        for max_book in [0.62, 0.65, 0.70]:
            for min_alt in [0.55, 0.60, 0.65]:
                for max_ask in [60.0, 70.0, 80.0, 90.0]:
                    for cheaper_by in [0.0, 5.0, 10.0]:
                        specs.append(
                            SwitchSpec(
                                name=(
                                    f"switch_{alt}_book{max_book:g}_alt{min_alt:g}_"
                                    f"ask{max_ask:g}_cheap{cheaper_by:g}"
                                ),
                                alt_chooser=alt,
                                max_book_score=max_book,
                                min_alt_score=min_alt,
                                max_alt_ask=max_ask,
                                min_alt_cheaper_by=cheaper_by,
                            )
                        )
    return specs


def prepare_rows(rows: pd.DataFrame, base: pd.DataFrame) -> pd.DataFrame:
    out = add_scores(rows).merge(base[["market", "split"]], on="market", how="inner")
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


def first_market_rows(rows: pd.DataFrame) -> pd.DataFrame:
    if rows.empty:
        return rows.copy()
    return (
        rows.sort_values(["market", "entry_dt", "side"])
        .groupby("market", as_index=False, sort=False)
        .first()
        .sort_values(["entry_dt", "market"])
        .reset_index(drop=True)
    )


def select_spec(prepared: pd.DataFrame, chosen_cache: Dict[str, pd.DataFrame], spec: SwitchSpec) -> pd.DataFrame:
    book = chosen_cache["book_p_side"]
    if book.empty:
        return enrich_selected(book)
    base_rows = book[gate_mask(book, BASE_POLICY)].copy()
    if base_rows.empty:
        return enrich_selected(base_rows)
    if spec.alt_chooser == "baseline":
        selected = first_market_rows(base_rows)
        selected["candidate"] = spec.name
        selected["action_taken"] = "book"
        selected["overlay"] = "book_margin_base"
        return enrich_selected(selected)

    alt = chosen_cache.get(spec.alt_chooser, prepared.iloc[0:0]).copy()
    if alt.empty:
        selected = first_market_rows(base_rows)
        selected["candidate"] = spec.name
        selected["action_taken"] = "book"
        selected["overlay"] = "book_margin_base"
        return enrich_selected(selected)

    key_cols = [col for col in ["decision_key", "entry_dt", "entry_minute", "market"] if col in base_rows.columns]
    alt_cols = key_cols + ["side", "ask_cents", spec.alt_chooser]
    alt_view = alt[alt_cols].rename(
        columns={
            "side": "alt_side",
            "ask_cents": "alt_ask_cents",
            spec.alt_chooser: "alt_score_value",
        }
    )
    merged = base_rows.merge(alt_view, on=key_cols, how="left")
    switch = (
        merged["alt_side"].notna()
        & merged["alt_side"].astype(str).ne(merged["side"].astype(str))
        & pd.to_numeric(merged["book_p_side"], errors="coerce").le(spec.max_book_score)
        & pd.to_numeric(merged["alt_score_value"], errors="coerce").ge(spec.min_alt_score)
        & pd.to_numeric(merged["alt_ask_cents"], errors="coerce").le(spec.max_alt_ask)
        & (pd.to_numeric(merged["ask_cents"], errors="coerce") - pd.to_numeric(merged["alt_ask_cents"], errors="coerce")).ge(
            spec.min_alt_cheaper_by
        )
    ).fillna(False)

    normal = merged[~switch].copy()
    normal["action_taken"] = "book"
    normal["overlay"] = "book_margin_base"
    switched_keys = merged.loc[switch, key_cols].copy()
    switched = prepared.merge(switched_keys, on=key_cols, how="inner")
    if not switched.empty:
        switched = switched.merge(
            merged.loc[switch, key_cols + ["alt_side", "alt_ask_cents", "alt_score_value"]],
            on=key_cols,
            how="inner",
        )
        switched = switched[switched["side"].astype(str).eq(switched["alt_side"].astype(str))].copy()
        switched["action_taken"] = "switch"
        switched["overlay"] = spec.name
    selected = pd.concat([normal, switched], ignore_index=True, sort=False)
    if selected.empty:
        return enrich_selected(selected)
    selected = first_market_rows(selected)
    selected["candidate"] = spec.name
    return enrich_selected(selected)


def row_for(dataset: str, spec: SwitchSpec, base: pd.DataFrame, selected: pd.DataFrame) -> Dict[str, Any]:
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
        "switch_selected": int(actions.eq("switch").sum()) if not actions.empty else 0,
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


def scan_dataset(dataset: str, side_rows: pd.DataFrame, specs: List[SwitchSpec]) -> tuple[pd.DataFrame, List[Dict[str, Any]], pd.DataFrame]:
    base = market_base(add_scores(side_rows))
    prepared = prepare_rows(side_rows, base)
    choosers = sorted({spec.alt_chooser for spec in specs if spec.alt_chooser != "baseline"} | {"book_p_side"})
    chosen_cache = {chooser: choose_decision_sides(prepared, chooser) for chooser in choosers}
    rows: List[Dict[str, Any]] = []
    block_out: List[Dict[str, Any]] = []
    for spec in specs:
        selected = select_spec(prepared, chosen_cache, spec)
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
        f"{int(row['switch_selected_current'])}/{int(row['switch_selected_v21'])} | "
        f"{fmt_num(row['min_positive_block_rate'])} | {fmt_cents(row['worst_block_net_cents'])} |"
    )


def write_report(generated: str, frame: pd.DataFrame, diagnostics: Dict[str, Any]) -> None:
    strict = frame[frame["strict_pass"]]
    lines = [
        "# Weak-Book Disagreement Switch Frontier",
        "",
        f"Generated UTC: `{generated}`",
        "",
        "## Scope",
        "",
        "- Research-only scan; no orders are submitted and no bot files or live processes are touched.",
        "- Preserves `book_margin` coverage and only switches when an opposite physics side is cheaper and strong enough.",
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
        "| policy | strict | combined all net | combined OOS net | min split cov | current/v21 net | current/v21 acc | switches current/v21 | min block+ | worst block |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for _, row in frame.head(30).iterrows():
        lines.append(table_row(row.to_dict()))
    lines += ["", "## Read", ""]
    if strict.empty:
        lines.append("- No weak-book disagreement switch clears the strict gate.")
    else:
        best = strict.iloc[0]
        lines.append(
            f"- Best strict diagnostic row is `{best['label_current']}` with combined all-ledger net "
            f"{fmt_cents(best['combined_all_net_pnl_cents'])}."
        )
        lines.append("- This is post-hoc research and must be forward-locked before any live use.")
    for path in [REPORT_MD, OUT_DIR / f"book_weak_disagreement_switch_frontier_{generated}.md"]:
        path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    generated = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%SZ")
    frame, blocks, diagnostics = scan()
    frame.to_csv(CSV_LATEST, index=False)
    frame.to_csv(OUT_DIR / f"book_weak_disagreement_switch_frontier_{generated}.csv", index=False)
    blocks.to_csv(BLOCKS_LATEST, index=False)
    blocks.to_csv(OUT_DIR / f"book_weak_disagreement_switch_blocks_{generated}.csv", index=False)
    write_report(generated, frame, diagnostics)
    payload = {"generated_utc": generated, "diagnostics": diagnostics, "rows": frame.to_dict("records")}
    for path in [REPORT_JSON, OUT_DIR / f"book_weak_disagreement_switch_frontier_{generated}.json"]:
        path.write_text(json.dumps(clean_json_local(payload), indent=2, sort_keys=True), encoding="utf-8")
    print("Weak-book disagreement switch frontier complete")
    print(f"rows={len(frame)}")
    print(f"strict_pass={diagnostics['strict_pass_rows']}")
    print(f"report={REPORT_MD}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
