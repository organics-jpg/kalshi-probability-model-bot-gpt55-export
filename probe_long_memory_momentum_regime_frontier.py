"""Long-memory momentum regime frontier for BTC 15m book-margin signals.

Strict failure attribution shows a physical separation in book-margin rows:
losses tend to have much worse side-relative 15m/30m path history than wins.
That suggests a possible failure mode where the book briefly leans across the
strike but the longer path inertia is still adverse.

This research-only probe keeps the high-coverage book-margin baseline and tests
small defer/fade overlays when 15m/30m signed movement is adverse to the chosen
side. It evaluates the current two-sided heartbeat ledger and the independent
v21 ledger with split and block-stability gates.

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
from probe_impulse_reversal_regime_frontier import coerce_extra_numeric, first_market_rows
from probe_market_interval_80coverage import (
    MARKET_COVERAGE_FLOOR,
    OUT_DIR,
    Policy,
    choose_decision_sides,
    clean_json,
    gate_mask,
    load_side_rows,
    market_base,
    pct,
)
from probe_near_strike_breakout_regime_frontier import (
    block_rows,
    block_stability,
    combine,
)


REPORT_MD = OUT_DIR / "long_memory_momentum_regime_frontier_latest.md"
REPORT_JSON = OUT_DIR / "long_memory_momentum_regime_frontier_latest.json"
CSV_LATEST = OUT_DIR / "long_memory_momentum_regime_frontier_latest.csv"
BLOCKS_LATEST = OUT_DIR / "long_memory_momentum_regime_blocks_latest.csv"

BASE_POLICY = Policy("book_p_side", 0.60, 95.0, 120.0, "margin_rv15>=0")


@dataclass(frozen=True)
class LongMemorySpec:
    name: str
    action: str
    momentum_col: str
    max_signed_move: float
    max_score: float
    min_seconds_to_close: float
    max_fade_ask: float

    @property
    def label(self) -> str:
        if self.action == "baseline":
            return BASE_POLICY.label
        return (
            f"base={BASE_POLICY.label}; action={self.action}; "
            f"{self.momentum_col}<={self.max_signed_move:g}; book_score<={self.max_score:g}; "
            f"sec>={self.min_seconds_to_close:g}; fade_ask<={self.max_fade_ask:g}"
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
    if value is None or not math.isfinite(float(value)):
        return "NA"
    return f"{float(value):.{digits}f}"


def coerce_long_memory(rows: pd.DataFrame) -> pd.DataFrame:
    out = coerce_extra_numeric(rows)
    for col in ["signed_move_15m", "signed_move_30m"]:
        if col not in out.columns:
            out[col] = np.nan
        out[col] = pd.to_numeric(out[col], errors="coerce")
    out["signed_move_min_15_30m"] = out[["signed_move_15m", "signed_move_30m"]].min(axis=1)
    return out


def make_specs() -> List[LongMemorySpec]:
    specs: List[LongMemorySpec] = [
        LongMemorySpec("book_margin_baseline", "baseline", "signed_move_min_15_30m", -10_000.0, 1.0, 120.0, 100.0)
    ]
    for action in ["veto", "fade"]:
        for momentum_col in ["signed_move_15m", "signed_move_30m", "signed_move_min_15_30m"]:
            for max_signed_move in [-50.0, -100.0, -200.0, -400.0]:
                for max_score in [0.65, 0.70, 0.80]:
                    for min_sec in [300.0, 600.0]:
                        fade_caps = [45.0, 50.0] if action == "fade" else [100.0]
                        for max_fade_ask in fade_caps:
                            specs.append(
                                LongMemorySpec(
                                    name=(
                                        f"{action}_{momentum_col}_le{abs(max_signed_move):g}_"
                                        f"score{max_score:g}_sec{min_sec:g}_fade{max_fade_ask:g}"
                                    ),
                                    action=action,
                                    momentum_col=momentum_col,
                                    max_signed_move=max_signed_move,
                                    max_score=max_score,
                                    min_seconds_to_close=min_sec,
                                    max_fade_ask=max_fade_ask,
                                )
                            )
    return specs


def adverse_momentum_mask(chosen: pd.DataFrame, spec: LongMemorySpec) -> pd.Series:
    momentum = pd.to_numeric(chosen.get(spec.momentum_col), errors="coerce")
    score = pd.to_numeric(chosen.get(BASE_POLICY.chooser), errors="coerce")
    seconds = pd.to_numeric(chosen.get("seconds_to_close"), errors="coerce")
    return (
        momentum.le(spec.max_signed_move)
        & score.le(spec.max_score)
        & seconds.ge(spec.min_seconds_to_close)
    ).fillna(False)


def trigger_columns(triggers: pd.DataFrame, spec: LongMemorySpec) -> pd.DataFrame:
    keys = [col for col in ["decision_key", "entry_dt", "entry_minute", "market"] if col in triggers.columns]
    cols = [
        "side",
        "ask_cents",
        BASE_POLICY.chooser,
        "margin_dollars",
        "signed_move_15m",
        "signed_move_30m",
        "signed_move_min_15_30m",
    ]
    cols = [col for col in cols if col in triggers.columns]
    renamed = triggers[keys + cols].rename(
        columns={
            "side": "long_trigger_side",
            "ask_cents": "long_trigger_ask_cents",
            BASE_POLICY.chooser: "long_trigger_score_value",
            "margin_dollars": "long_trigger_margin_dollars",
            "signed_move_15m": "long_trigger_signed_move_15m",
            "signed_move_30m": "long_trigger_signed_move_30m",
            "signed_move_min_15_30m": "long_trigger_signed_move_min_15_30m",
        }
    )
    renamed["long_trigger_momentum_col"] = spec.momentum_col
    return renamed


def opposite_fades(rows: pd.DataFrame, triggers: pd.DataFrame, spec: LongMemorySpec) -> pd.DataFrame:
    if rows.empty or triggers.empty:
        return rows.iloc[0:0].copy()
    key_cols = [col for col in ["decision_key", "entry_dt", "entry_minute", "market"] if col in rows.columns]
    trigger = trigger_columns(triggers, spec)
    faded = rows.merge(trigger, on=key_cols, how="inner")
    faded = faded[faded["side"].astype(str).ne(faded["long_trigger_side"].astype(str))].copy()
    if faded.empty:
        return faded
    faded = faded[pd.to_numeric(faded["ask_cents"], errors="coerce").le(spec.max_fade_ask)].copy()
    if not faded.empty:
        faded["action_taken"] = "fade"
        faded["overlay"] = spec.name
    return faded


def select_spec(side_rows: pd.DataFrame, base: pd.DataFrame, spec: LongMemorySpec) -> pd.DataFrame:
    rows = coerce_long_memory(side_rows).merge(base[["market", "split"]], on="market", how="inner")
    chosen = choose_decision_sides(rows, BASE_POLICY.chooser)
    if chosen.empty:
        return enrich_selected(chosen)
    chosen = chosen[gate_mask(chosen, BASE_POLICY)].copy()
    if chosen.empty:
        return enrich_selected(chosen)

    if spec.action == "baseline":
        selected = first_market_rows(chosen)
        selected["candidate"] = spec.name
        selected["action_taken"] = "base"
        selected["overlay"] = "book_margin_base"
        return enrich_selected(selected)

    adverse = chosen[adverse_momentum_mask(chosen, spec)].copy()
    normal = chosen[~chosen.index.isin(adverse.index)].copy()
    if not normal.empty:
        normal["action_taken"] = "base"
        normal["overlay"] = "book_margin_base"

    if spec.action == "veto":
        mixed = normal
    elif spec.action == "fade":
        mixed = pd.concat([normal, opposite_fades(rows, adverse, spec)], ignore_index=True, sort=False)
    else:
        raise ValueError(f"unknown action: {spec.action}")

    if mixed.empty:
        return enrich_selected(mixed)
    selected = first_market_rows(mixed)
    selected["candidate"] = spec.name
    return enrich_selected(selected)


def flatten(dataset: str, spec: LongMemorySpec, base: pd.DataFrame, selected: pd.DataFrame) -> Dict[str, Any]:
    metrics = metrics_for(base, selected)
    actions = selected.get("action_taken", pd.Series(dtype=object)).fillna("base").astype(str) if not selected.empty else pd.Series(dtype=object)
    row: Dict[str, Any] = {
        "dataset": dataset,
        "candidate": spec.name,
        "label": spec.label,
        "action": spec.action,
        "momentum_col": spec.momentum_col,
        "max_signed_move": spec.max_signed_move,
        "max_score": spec.max_score,
        "min_seconds_to_close": spec.min_seconds_to_close,
        "max_fade_ask": spec.max_fade_ask,
        "fade_selected": int(actions.eq("fade").sum()) if not actions.empty else 0,
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
    row["min_oos_roi"] = min((metrics[split]["net_roi_on_cost"] or -1.0) for split in ["validation", "holdout"])
    return row


def scan() -> tuple[pd.DataFrame, pd.DataFrame, Dict[str, Any]]:
    current_side = coerce_long_memory(load_side_rows())
    v21_side = coerce_long_memory(load_v21_side_rows())
    current_base = market_base(current_side)
    v21_base = market_base(v21_side)
    specs = make_specs()
    current_rows: List[Dict[str, Any]] = []
    v21_rows: List[Dict[str, Any]] = []
    block_out: List[Dict[str, Any]] = []
    for spec in specs:
        current_selected = select_spec(current_side, current_base, spec)
        v21_selected = select_spec(v21_side, v21_base, spec)
        current_rows.append(flatten("current", spec, current_base, current_selected))
        v21_rows.append(flatten("v21", spec, v21_base, v21_selected))
        block_out.extend(block_rows("current", spec.name, current_base, current_selected))
        block_out.extend(block_rows("v21", spec.name, v21_base, v21_selected))
    blocks = pd.DataFrame(block_out)
    stability = block_stability(blocks)
    frame = combine(pd.DataFrame(current_rows), pd.DataFrame(v21_rows), stability)
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
        f"{int(row['fade_selected_current'])}/{int(row['fade_selected_v21'])} | "
        f"{fmt_num(row['min_positive_block_rate'])} | {fmt_cents(row['worst_block_net_cents'])} |"
    )


def write_report(generated: str, frame: pd.DataFrame, diagnostics: Dict[str, Any]) -> None:
    strict = frame[frame["strict_pass"]]
    lines = [
        "# Long-Memory Momentum Regime Frontier",
        "",
        f"Generated UTC: `{generated}`",
        "",
        "## Scope",
        "",
        "- Research-only scan; no orders are submitted and no bot files or live processes are touched.",
        "- Keeps `book_margin` as the high-coverage base and tests 15m/30m adverse path-memory overlays.",
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
        "| policy | strict | combined all net | combined OOS net | min split cov | current/v21 net | current/v21 acc | fades current/v21 | min block+ | worst block |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for _, row in frame.head(30).iterrows():
        lines.append(table_row(row.to_dict()))
    lines += ["", "## Read", ""]
    if strict.empty:
        lines.append("- No long-memory momentum overlay clears the strict gate.")
    else:
        best = strict.iloc[0]
        lines.append(
            f"- Best strict diagnostic row is `{best['label_current']}` with combined all-ledger net "
            f"{fmt_cents(best['combined_all_net_pnl_cents'])}."
        )
        lines.append("- This is still post-hoc research and must be forward-locked before any promotion.")
    for path in [REPORT_MD, OUT_DIR / f"long_memory_momentum_regime_frontier_{generated}.md"]:
        path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    generated = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%SZ")
    frame, blocks, diagnostics = scan()
    frame.to_csv(CSV_LATEST, index=False)
    frame.to_csv(OUT_DIR / f"long_memory_momentum_regime_frontier_{generated}.csv", index=False)
    blocks.to_csv(BLOCKS_LATEST, index=False)
    blocks.to_csv(OUT_DIR / f"long_memory_momentum_regime_blocks_{generated}.csv", index=False)
    write_report(generated, frame, diagnostics)
    payload = {"generated_utc": generated, "diagnostics": diagnostics, "rows": frame.to_dict("records")}
    for path in [REPORT_JSON, OUT_DIR / f"long_memory_momentum_regime_frontier_{generated}.json"]:
        path.write_text(json.dumps(clean_json_local(payload), indent=2, sort_keys=True), encoding="utf-8")
    print("Long-memory momentum regime frontier complete")
    print(f"rows={len(frame)}")
    print(f"strict_pass={diagnostics['strict_pass_rows']}")
    print(f"report={REPORT_MD}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
