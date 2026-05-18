"""Causal touch/book state frontier for BTC 15m fair value.

The non-causal continuation/exhaustion scan found that earlier same-side touch
prices can be much better than later book prices. This probe removes that
intra-market hindsight: it can only enter at the first row where touch and book
are already aligned at that moment, otherwise it falls back to broad
book-margin.

Research-only: no orders are submitted and no bot files or live processes are
modified.
"""
from __future__ import annotations

import json
import math
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import pandas as pd

from probe_cross_dataset_interval_frontier import load_v21_side_rows
from probe_cross_dataset_profit_frontier import enrich_selected, fmt_cents, fmt_roi, metrics_for
from probe_impulse_reversal_regime_frontier import BLOCK_MARKETS, MIN_BLOCK_MARKETS, POSITIVE_BLOCK_RATE_FLOOR
from probe_market_interval_80coverage import (
    MARKET_COVERAGE_FLOOR,
    OUT_DIR,
    Policy,
    choose_decision_sides,
    clean_json,
    load_side_rows,
    market_base,
    pct,
    select_markets_from_chosen,
)
from probe_profit_touch_hazard_frontier import add_touch_hazard_scores


REPORT_MD = OUT_DIR / "causal_touch_book_state_frontier_latest.md"
REPORT_JSON = OUT_DIR / "causal_touch_book_state_frontier_latest.json"
CSV_LATEST = OUT_DIR / "causal_touch_book_state_frontier_latest.csv"
BLOCKS_LATEST = OUT_DIR / "causal_touch_book_state_blocks_latest.csv"

BASE_POLICY = Policy("book_p_side", 0.60, 95.0, 120.0, "margin_rv15>=0")


@dataclass(frozen=True)
class TouchBookSpec:
    name: str
    min_touch_score: float
    max_touch_ask: float
    min_book_at_touch: float
    fallback_to_book: bool = True

    @property
    def label(self) -> str:
        mode = "touch-first + book fallback" if self.fallback_to_book else "touch-only"
        return (
            f"{mode}; touch>= {self.min_touch_score:g}; touch_ask<={self.max_touch_ask:g}; "
            f"book_at_touch>={self.min_book_at_touch:g}; sec>=120; margin_rv15>=0"
        )


def clean_json_local(value: Any) -> Any:
    if isinstance(value, pd.Timestamp):
        return value.isoformat()
    if isinstance(value, dict):
        return {str(k): clean_json_local(v) for k, v in value.items()}
    if isinstance(value, list):
        return [clean_json_local(v) for v in value]
    return clean_json(value)


def fmt_num(value: Optional[float], digits: int = 3) -> str:
    if value is None:
        return "NA"
    try:
        number = float(value)
    except (TypeError, ValueError):
        return "NA"
    if not math.isfinite(number):
        return "NA"
    return f"{number:.{digits}f}"


def make_specs() -> List[TouchBookSpec]:
    specs = [TouchBookSpec("baseline_book_margin", 1.0, 0.0, 1.0, True)]
    for min_touch in [0.40, 0.45, 0.50, 0.55]:
        for max_ask in [55.0, 60.0, 65.0]:
            for min_book in [0.50, 0.55, 0.60, 0.65]:
                specs.append(
                    TouchBookSpec(
                        f"touch_first_t{min_touch:g}_ask{max_ask:g}_book{min_book:g}",
                        min_touch,
                        max_ask,
                        min_book,
                        True,
                    )
                )
    return specs


def prepare(side_rows: pd.DataFrame, base: pd.DataFrame) -> pd.DataFrame:
    rows = add_touch_hazard_scores(side_rows).merge(base[["market", "split"]], on="market", how="inner")
    rows["entry_dt"] = pd.to_datetime(rows["entry_dt"], utc=True, errors="coerce")
    for col in ["ask_cents", "book_p_side", "book_touch_blend_15", "seconds_to_close", "margin_per_rv_sigma_15m"]:
        if col not in rows.columns:
            rows[col] = np.nan
        rows[col] = pd.to_numeric(rows[col], errors="coerce")
    return rows.sort_values(["market", "entry_dt", "side"]).reset_index(drop=True)


def base_selected(prepared: pd.DataFrame) -> pd.DataFrame:
    selected = select_markets_from_chosen(choose_decision_sides(prepared, BASE_POLICY.chooser), BASE_POLICY)
    if selected.empty:
        return selected.copy()
    selected = selected.copy()
    selected["chooser"] = BASE_POLICY.chooser
    selected["score_value"] = selected[BASE_POLICY.chooser]
    selected["action_taken"] = "book_fallback"
    selected["overlay"] = "book_margin_base"
    return selected


def touch_first_selected(prepared: pd.DataFrame, spec: TouchBookSpec) -> pd.DataFrame:
    chosen = choose_decision_sides(prepared, "book_touch_blend_15")
    if chosen.empty:
        return chosen.copy()
    selected = chosen[
        pd.to_numeric(chosen["book_touch_blend_15"], errors="coerce").ge(spec.min_touch_score)
        & pd.to_numeric(chosen["ask_cents"], errors="coerce").le(spec.max_touch_ask)
        & pd.to_numeric(chosen["book_p_side"], errors="coerce").ge(spec.min_book_at_touch)
        & pd.to_numeric(chosen["seconds_to_close"], errors="coerce").ge(120.0)
        & pd.to_numeric(chosen["margin_per_rv_sigma_15m"], errors="coerce").ge(0.0)
    ].copy()
    if selected.empty:
        return selected
    selected = (
        selected.sort_values(["market", "entry_dt", "side"])
        .groupby("market", as_index=False, sort=False)
        .first()
        .sort_values(["entry_dt", "market"])
        .reset_index(drop=True)
    )
    selected["chooser"] = "book_touch_blend_15"
    selected["score_value"] = selected["book_touch_blend_15"]
    selected["action_taken"] = "touch_first"
    selected["overlay"] = spec.name
    return selected


def select_spec(prepared: pd.DataFrame, base_rows: pd.DataFrame, spec: TouchBookSpec) -> pd.DataFrame:
    if spec.name == "baseline_book_margin":
        return enrich_selected(base_rows.copy())
    touch = touch_first_selected(prepared, spec)
    if spec.fallback_to_book:
        selected = pd.concat([touch, base_rows], ignore_index=True, sort=False)
        if selected.empty:
            return enrich_selected(selected)
        selected = (
            selected.sort_values(["market", "entry_dt", "side"])
            .groupby("market", as_index=False, sort=False)
            .first()
            .sort_values(["entry_dt", "market"])
            .reset_index(drop=True)
        )
    else:
        selected = touch
    selected["candidate"] = spec.name
    return enrich_selected(selected)


def flatten(dataset: str, spec: TouchBookSpec, base: pd.DataFrame, selected: pd.DataFrame) -> Dict[str, Any]:
    metrics = metrics_for(base, selected)
    actions = selected.get("action_taken", pd.Series(dtype=object)).fillna("book_fallback").astype(str)
    row: Dict[str, Any] = {
        "dataset": dataset,
        "candidate": spec.name,
        "label": spec.label,
        "min_touch_score": spec.min_touch_score,
        "max_touch_ask": spec.max_touch_ask,
        "min_book_at_touch": spec.min_book_at_touch,
        "touch_first_rows": int(actions.eq("touch_first").sum()) if not actions.empty else 0,
        "book_fallback_rows": int(actions.eq("book_fallback").sum()) if not actions.empty else 0,
    }
    for split, values in metrics.items():
        for key, value in values.items():
            row[f"{split}_{key}"] = value
    row["coverage_pass"] = all((metrics[split]["coverage"] or 0.0) >= MARKET_COVERAGE_FLOOR for split in ["all", "train", "validation", "holdout"])
    row["all_splits_positive"] = all((metrics[split]["net_pnl_cents"] or 0.0) > 0.0 for split in ["all", "train", "validation", "holdout"])
    row["oos_positive"] = all((metrics[split]["net_pnl_cents"] or 0.0) > 0.0 for split in ["validation", "holdout"])
    row["min_split_coverage"] = min((metrics[split]["coverage"] or 0.0) for split in ["train", "validation", "holdout"])
    return row


def block_rows(dataset: str, candidate: str, base: pd.DataFrame, selected: pd.DataFrame) -> List[Dict[str, Any]]:
    base_blocks = base.sort_values(["close_dt", "market"]).reset_index(drop=True).copy()
    base_blocks["block_index"] = base_blocks.index // BLOCK_MARKETS
    selected_blocks = selected.drop(columns=["block_index"], errors="ignore").merge(
        base_blocks[["market", "block_index"]], on="market", how="inner"
    )
    rows: List[Dict[str, Any]] = []
    for block_index, block in base_blocks.groupby("block_index", sort=True):
        part = selected_blocks[selected_blocks["block_index"].eq(block_index)]
        n = int(len(part))
        wins = int(part["win"].astype(bool).sum()) if n else 0
        net = float(pd.to_numeric(part.get("net_pnl_cents"), errors="coerce").sum()) if n else 0.0
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
                "net_pnl_cents": net,
                "positive_net": net > 0.0,
                "coverage_pass": (coverage or 0.0) >= MARKET_COVERAGE_FLOOR,
            }
        )
    return rows


def block_stability(blocks: pd.DataFrame) -> pd.DataFrame:
    if blocks.empty:
        return pd.DataFrame()
    supported = blocks[blocks["base_markets"].ge(MIN_BLOCK_MARKETS)].copy()
    rows: List[Dict[str, Any]] = []
    for (dataset, candidate), part in supported.groupby(["dataset", "candidate"], sort=True):
        rows.append(
            {
                "dataset": dataset,
                "candidate": candidate,
                "positive_block_rate": float(part["positive_net"].mean()) if len(part) else None,
                "coverage_block_rate": float(part["coverage_pass"].mean()) if len(part) else None,
                "worst_block_net_cents": float(part["net_pnl_cents"].min()) if len(part) else None,
            }
        )
    return pd.DataFrame(rows)


def combine(current: pd.DataFrame, v21: pd.DataFrame, stability: pd.DataFrame) -> pd.DataFrame:
    frame = current.merge(v21, on="candidate", suffixes=("_current", "_v21"))
    if not stability.empty:
        stab_rows = []
        for candidate, part in stability.groupby("candidate", sort=True):
            stab_rows.append(
                {
                    "candidate": candidate,
                    "min_positive_block_rate": float(part["positive_block_rate"].min()),
                    "min_coverage_block_rate": float(part["coverage_block_rate"].min()),
                    "worst_block_net_cents": float(part["worst_block_net_cents"].min()),
                }
            )
        frame = frame.merge(pd.DataFrame(stab_rows), on="candidate", how="left")
    else:
        frame["min_positive_block_rate"] = np.nan
        frame["min_coverage_block_rate"] = np.nan
        frame["worst_block_net_cents"] = np.nan
    frame["combined_all_net_pnl_cents"] = pd.to_numeric(frame["all_net_pnl_cents_current"], errors="coerce").fillna(0.0) + pd.to_numeric(frame["all_net_pnl_cents_v21"], errors="coerce").fillna(0.0)
    frame["combined_oos_net_pnl_cents"] = (
        pd.to_numeric(frame["validation_net_pnl_cents_current"], errors="coerce").fillna(0.0)
        + pd.to_numeric(frame["holdout_net_pnl_cents_current"], errors="coerce").fillna(0.0)
        + pd.to_numeric(frame["validation_net_pnl_cents_v21"], errors="coerce").fillna(0.0)
        + pd.to_numeric(frame["holdout_net_pnl_cents_v21"], errors="coerce").fillna(0.0)
    )
    frame["both_coverage_pass"] = frame["coverage_pass_current"].astype(bool) & frame["coverage_pass_v21"].astype(bool)
    frame["both_oos_positive"] = frame["oos_positive_current"].astype(bool) & frame["oos_positive_v21"].astype(bool)
    frame["both_all_splits_positive"] = frame["all_splits_positive_current"].astype(bool) & frame["all_splits_positive_v21"].astype(bool)
    frame["block_stability_pass"] = (
        pd.to_numeric(frame["min_positive_block_rate"], errors="coerce").fillna(0.0).ge(POSITIVE_BLOCK_RATE_FLOOR)
        & pd.to_numeric(frame["min_coverage_block_rate"], errors="coerce").fillna(0.0).ge(POSITIVE_BLOCK_RATE_FLOOR)
    )
    frame["strict_pass"] = frame["both_coverage_pass"] & frame["both_oos_positive"] & frame["both_all_splits_positive"] & frame["block_stability_pass"]
    frame["min_split_coverage"] = frame[["min_split_coverage_current", "min_split_coverage_v21"]].min(axis=1)
    return frame.sort_values(
        ["strict_pass", "both_coverage_pass", "both_oos_positive", "combined_oos_net_pnl_cents", "combined_all_net_pnl_cents"],
        ascending=[False, False, False, False, False],
    ).reset_index(drop=True)


def scan() -> Tuple[pd.DataFrame, pd.DataFrame, Dict[str, Any]]:
    current_side = load_side_rows()
    v21_side = load_v21_side_rows()
    current_base = market_base(add_touch_hazard_scores(current_side))
    v21_base = market_base(add_touch_hazard_scores(v21_side))
    current_prepared = prepare(current_side, current_base)
    v21_prepared = prepare(v21_side, v21_base)
    current_base_rows = base_selected(current_prepared)
    v21_base_rows = base_selected(v21_prepared)
    specs = make_specs()
    current_rows: List[Dict[str, Any]] = []
    v21_rows: List[Dict[str, Any]] = []
    block_out: List[Dict[str, Any]] = []
    for spec in specs:
        current_selected = select_spec(current_prepared, current_base_rows, spec)
        v21_selected = select_spec(v21_prepared, v21_base_rows, spec)
        current_rows.append(flatten("current", spec, current_base, current_selected))
        v21_rows.append(flatten("v21", spec, v21_base, v21_selected))
        block_out.extend(block_rows("current", spec.name, current_base, current_selected))
        block_out.extend(block_rows("v21", spec.name, v21_base, v21_selected))
    blocks = pd.DataFrame(block_out)
    frame = combine(pd.DataFrame(current_rows), pd.DataFrame(v21_rows), block_stability(blocks))
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
        f"{int(row['touch_first_rows_current'])}/{int(row['touch_first_rows_v21'])} | "
        f"{fmt_num(row['min_positive_block_rate'])} | {fmt_cents(row['worst_block_net_cents'])} |"
    )


def write_report(generated: str, frame: pd.DataFrame, diagnostics: Dict[str, Any]) -> None:
    strict = frame[frame["strict_pass"]]
    lines = [
        "# Causal Touch/Book State Frontier",
        "",
        f"Generated UTC: `{generated}`",
        "",
        "## Scope",
        "",
        "- Research-only scan; no orders are submitted and no bot files or live processes are touched.",
        "- Causal rule: trade touch only when touch/book alignment exists at that row; otherwise fall back to book-margin.",
        "- Strict pass requires current+v21 80% split coverage, positive validation/holdout, positive all splits, and block stability.",
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
        "| policy | strict | combined all net | combined OOS net | min split cov | current/v21 net | current/v21 acc | touch-first current/v21 | min block+ | worst block |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for _, row in frame.head(30).iterrows():
        lines.append(table_row(row.to_dict()))
    lines += ["", "## Read", ""]
    if strict.empty:
        lines.append("- No causal touch/book row clears the full strict gate. Do not promote a row from this scan.")
    else:
        best = strict.iloc[0]
        lines.append(
            f"- Best strict diagnostic row is `{best['label_current']}` with combined all-ledger net "
            f"{fmt_cents(best['combined_all_net_pnl_cents'])}."
        )
        lines.append("- This is post-hoc diagnostic evidence and must be forward-locked before live use.")
    for path in [REPORT_MD, OUT_DIR / f"causal_touch_book_state_frontier_{generated}.md"]:
        path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    generated = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%SZ")
    frame, blocks, diagnostics = scan()
    frame.to_csv(CSV_LATEST, index=False)
    frame.to_csv(OUT_DIR / f"causal_touch_book_state_frontier_{generated}.csv", index=False)
    blocks.to_csv(BLOCKS_LATEST, index=False)
    blocks.to_csv(OUT_DIR / f"causal_touch_book_state_blocks_{generated}.csv", index=False)
    write_report(generated, frame, diagnostics)
    payload = {"generated_utc": generated, "diagnostics": diagnostics, "rows": frame.to_dict("records")}
    for path in [REPORT_JSON, OUT_DIR / f"causal_touch_book_state_frontier_{generated}.json"]:
        path.write_text(json.dumps(clean_json_local(payload), indent=2, sort_keys=True), encoding="utf-8")
    print("Causal touch/book state frontier complete")
    print(f"rows={len(frame)}")
    print(f"strict_pass={diagnostics['strict_pass_rows']}")
    print(f"report={REPORT_MD}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
