"""Near-strike breakout/reversion frontier for BTC 15m book-margin signals.

Recent live rows exposed two different states that looked similar if we only
looked at short-horizon impulse:

- strong breakout continuation: the book is expensive, confidence is high, and
  fading the move is dangerous;
- fragile near-strike flip: the book barely favors one side, the remaining
  distance-to-strike cushion is tiny, and the cheap opposite side may be the
  better convex entry.

This research-only probe keeps the high-coverage book-margin baseline and tests
small overlays for the second state. It evaluates veto/defer and fade actions on
the current two-sided heartbeat ledger and the independent v21 ledger with
train/validation/holdout splits and block stability.

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
from probe_cross_dataset_profit_frontier import enrich_selected, fmt_cents, fmt_roi, metrics_for
from probe_impulse_reversal_regime_frontier import (
    BLOCK_MARKETS,
    MIN_BLOCK_MARKETS,
    POSITIVE_BLOCK_RATE_FLOOR,
    coerce_extra_numeric,
    first_market_rows,
)
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


REPORT_MD = OUT_DIR / "near_strike_breakout_regime_frontier_latest.md"
REPORT_JSON = OUT_DIR / "near_strike_breakout_regime_frontier_latest.json"
CSV_LATEST = OUT_DIR / "near_strike_breakout_regime_frontier_latest.csv"
BLOCKS_LATEST = OUT_DIR / "near_strike_breakout_regime_blocks_latest.csv"

BASE_POLICY = Policy("book_p_side", 0.60, 95.0, 120.0, "margin_rv15>=0")


@dataclass(frozen=True)
class NearStrikeSpec:
    name: str
    action: str
    max_abs_margin: float
    max_margin_sigma: float
    max_score: float
    min_impulse_over_margin: float
    min_seconds_to_close: float
    max_fade_ask: float

    @property
    def label(self) -> str:
        if self.action == "baseline":
            return BASE_POLICY.label
        return (
            f"base={BASE_POLICY.label}; action={self.action}; "
            f"abs_margin<={self.max_abs_margin:g}; margin_sigma<={self.max_margin_sigma:g}; "
            f"book_score<={self.max_score:g}; impulse_over_margin>={self.min_impulse_over_margin:g}; "
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


def make_specs() -> List[NearStrikeSpec]:
    specs: List[NearStrikeSpec] = [
        NearStrikeSpec(
            name="book_margin_baseline",
            action="baseline",
            max_abs_margin=-1.0,
            max_margin_sigma=-1.0,
            max_score=-1.0,
            min_impulse_over_margin=10_000.0,
            min_seconds_to_close=120.0,
            max_fade_ask=100.0,
        )
    ]

    # Compact, physics-first grid. The variables describe a weakly confirmed
    # book side near the strike after enough favorable motion to erase the
    # distance cushion. This is intentionally narrower than a generic ML scan.
    for action in ["veto", "fade"]:
        for max_abs_margin in [5.0, 10.0, 25.0]:
            for max_margin_sigma in [0.10, 0.25, 0.50]:
                for max_score in [0.65, 0.70]:
                    for min_over in [0.0, 10.0, 20.0]:
                        for min_sec in [300.0, 600.0]:
                            fade_caps = [45.0, 50.0] if action == "fade" else [100.0]
                            for max_fade_ask in fade_caps:
                                specs.append(
                                    NearStrikeSpec(
                                        name=(
                                            f"{action}_abs{max_abs_margin:g}_sig{max_margin_sigma:g}_"
                                            f"score{max_score:g}_over{min_over:g}_sec{min_sec:g}_"
                                            f"fade{max_fade_ask:g}"
                                        ),
                                        action=action,
                                        max_abs_margin=max_abs_margin,
                                        max_margin_sigma=max_margin_sigma,
                                        max_score=max_score,
                                        min_impulse_over_margin=min_over,
                                        min_seconds_to_close=min_sec,
                                        max_fade_ask=max_fade_ask,
                                    )
                                )
    return specs


def near_strike_mask(chosen: pd.DataFrame, spec: NearStrikeSpec) -> pd.Series:
    abs_margin = pd.to_numeric(chosen.get("abs_margin_dollars"), errors="coerce")
    margin_sigma = pd.to_numeric(chosen.get("margin_per_rv_sigma_15m"), errors="coerce")
    score = pd.to_numeric(chosen.get(BASE_POLICY.chooser), errors="coerce")
    impulse_over = pd.to_numeric(chosen.get("impulse_3_5m_over_margin"), errors="coerce")
    seconds = pd.to_numeric(chosen.get("seconds_to_close"), errors="coerce")
    return (
        abs_margin.le(spec.max_abs_margin)
        & margin_sigma.le(spec.max_margin_sigma)
        & score.le(spec.max_score)
        & impulse_over.ge(spec.min_impulse_over_margin)
        & seconds.ge(spec.min_seconds_to_close)
    ).fillna(False)


def trigger_columns(triggers: pd.DataFrame) -> pd.DataFrame:
    keys = [col for col in ["decision_key", "entry_dt", "entry_minute", "market"] if col in triggers.columns]
    cols = [
        "side",
        "ask_cents",
        BASE_POLICY.chooser,
        "margin_dollars",
        "abs_margin_dollars",
        "margin_per_rv_sigma_15m",
        "signed_move_3m",
        "signed_move_5m",
        "impulse_3_5m",
        "impulse_3_5m_over_margin",
    ]
    cols = [col for col in cols if col in triggers.columns]
    return triggers[keys + cols].rename(
        columns={
            "side": "near_trigger_side",
            "ask_cents": "near_trigger_ask_cents",
            BASE_POLICY.chooser: "near_trigger_score_value",
            "margin_dollars": "near_trigger_margin_dollars",
            "abs_margin_dollars": "near_trigger_abs_margin_dollars",
            "margin_per_rv_sigma_15m": "near_trigger_margin_sigma",
            "signed_move_3m": "near_trigger_signed_move_3m",
            "signed_move_5m": "near_trigger_signed_move_5m",
            "impulse_3_5m": "near_trigger_impulse_3_5m",
            "impulse_3_5m_over_margin": "near_trigger_impulse_3_5m_over_margin",
        }
    )


def opposite_fades(rows: pd.DataFrame, triggers: pd.DataFrame, spec: NearStrikeSpec) -> pd.DataFrame:
    if rows.empty or triggers.empty:
        return rows.iloc[0:0].copy()
    key_cols = [col for col in ["decision_key", "entry_dt", "entry_minute", "market"] if col in rows.columns]
    trigger = trigger_columns(triggers)
    faded = rows.merge(trigger, on=key_cols, how="inner")
    faded = faded[faded["side"].astype(str).ne(faded["near_trigger_side"].astype(str))].copy()
    if faded.empty:
        return faded
    faded = faded[pd.to_numeric(faded["ask_cents"], errors="coerce").le(spec.max_fade_ask)].copy()
    if not faded.empty:
        faded["action_taken"] = "fade"
        faded["overlay"] = spec.name
    return faded


def select_spec(side_rows: pd.DataFrame, base: pd.DataFrame, spec: NearStrikeSpec) -> pd.DataFrame:
    rows = coerce_extra_numeric(side_rows).merge(base[["market", "split"]], on="market", how="inner")
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

    fragile = chosen[near_strike_mask(chosen, spec)].copy()
    normal = chosen[~chosen.index.isin(fragile.index)].copy()
    if not normal.empty:
        normal["action_taken"] = "base"
        normal["overlay"] = "book_margin_base"

    if spec.action == "veto":
        mixed = normal
    elif spec.action == "fade":
        mixed = pd.concat([normal, opposite_fades(rows, fragile, spec)], ignore_index=True, sort=False)
    else:
        raise ValueError(f"unknown action: {spec.action}")

    if mixed.empty:
        return enrich_selected(mixed)
    selected = first_market_rows(mixed)
    selected["candidate"] = spec.name
    return enrich_selected(selected)


def flatten(dataset: str, spec: NearStrikeSpec, base: pd.DataFrame, selected: pd.DataFrame) -> Dict[str, Any]:
    metrics = metrics_for(base, selected)
    actions = selected.get("action_taken", pd.Series(dtype=object)).fillna("base").astype(str) if not selected.empty else pd.Series(dtype=object)
    row: Dict[str, Any] = {
        "dataset": dataset,
        "candidate": spec.name,
        "label": spec.label,
        "action": spec.action,
        "max_abs_margin": spec.max_abs_margin,
        "max_margin_sigma": spec.max_margin_sigma,
        "max_score": spec.max_score,
        "min_impulse_over_margin": spec.min_impulse_over_margin,
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
        cost = float(pd.to_numeric(part.get("entry_cost_cents"), errors="coerce").sum()) if n else 0.0
        base_n = int(len(block))
        coverage = n / base_n if base_n else None
        actions = part.get("action_taken", pd.Series(dtype=object)).fillna("base").astype(str) if n else pd.Series(dtype=object)
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
                "positive_net": net > 0.0,
                "coverage_pass": (coverage or 0.0) >= MARKET_COVERAGE_FLOOR,
                "fade_selected": int(actions.eq("fade").sum()) if n else 0,
            }
        )
    return rows


def block_stability(blocks: pd.DataFrame) -> pd.DataFrame:
    if blocks.empty:
        return pd.DataFrame()
    supported = blocks[blocks["base_markets"].ge(MIN_BLOCK_MARKETS)].copy()
    if supported.empty:
        return pd.DataFrame()
    rows: List[Dict[str, Any]] = []
    for (dataset, candidate), part in supported.groupby(["dataset", "candidate"], sort=True):
        rows.append(
            {
                "dataset": dataset,
                "candidate": candidate,
                "blocks": int(len(part)),
                "positive_block_rate": float(part["positive_net"].mean()) if len(part) else None,
                "coverage_block_rate": float(part["coverage_pass"].mean()) if len(part) else None,
                "worst_block_net_cents": float(part["net_pnl_cents"].min()) if len(part) else None,
                "median_block_net_cents": float(part["net_pnl_cents"].median()) if len(part) else None,
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

    frame["combined_all_net_pnl_cents"] = (
        pd.to_numeric(frame["all_net_pnl_cents_current"], errors="coerce").fillna(0.0)
        + pd.to_numeric(frame["all_net_pnl_cents_v21"], errors="coerce").fillna(0.0)
    )
    frame["combined_oos_net_pnl_cents"] = (
        pd.to_numeric(frame["validation_net_pnl_cents_current"], errors="coerce").fillna(0.0)
        + pd.to_numeric(frame["holdout_net_pnl_cents_current"], errors="coerce").fillna(0.0)
        + pd.to_numeric(frame["validation_net_pnl_cents_v21"], errors="coerce").fillna(0.0)
        + pd.to_numeric(frame["holdout_net_pnl_cents_v21"], errors="coerce").fillna(0.0)
    )
    frame["both_coverage_pass"] = frame["coverage_pass_current"].astype(bool) & frame["coverage_pass_v21"].astype(bool)
    frame["both_oos_positive"] = frame["oos_positive_current"].astype(bool) & frame["oos_positive_v21"].astype(bool)
    frame["both_all_splits_positive"] = (
        frame["all_splits_positive_current"].astype(bool) & frame["all_splits_positive_v21"].astype(bool)
    )
    frame["block_stability_pass"] = (
        pd.to_numeric(frame["min_positive_block_rate"], errors="coerce").fillna(0.0).ge(POSITIVE_BLOCK_RATE_FLOOR)
        & pd.to_numeric(frame["min_coverage_block_rate"], errors="coerce").fillna(0.0).ge(POSITIVE_BLOCK_RATE_FLOOR)
    )
    frame["strict_pass"] = (
        frame["both_coverage_pass"]
        & frame["both_oos_positive"]
        & frame["both_all_splits_positive"]
        & frame["block_stability_pass"]
    )
    frame["min_split_coverage"] = frame[["min_split_coverage_current", "min_split_coverage_v21"]].min(axis=1)
    frame["min_oos_edge_cents"] = frame[["min_oos_edge_cents_current", "min_oos_edge_cents_v21"]].min(axis=1)
    frame["min_oos_roi"] = frame[["min_oos_roi_current", "min_oos_roi_v21"]].min(axis=1)
    return frame.sort_values(
        [
            "strict_pass",
            "both_coverage_pass",
            "both_oos_positive",
            "combined_oos_net_pnl_cents",
            "combined_all_net_pnl_cents",
            "min_split_coverage",
        ],
        ascending=[False, False, False, False, False, False],
    ).reset_index(drop=True)


def scan() -> tuple[pd.DataFrame, pd.DataFrame, Dict[str, Any]]:
    current_side = coerce_extra_numeric(load_side_rows())
    v21_side = coerce_extra_numeric(load_v21_side_rows())
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
        "# Near-Strike Breakout Regime Frontier",
        "",
        f"Generated UTC: `{generated}`",
        "",
        "## Scope",
        "",
        "- Research-only scan; no orders are submitted and no bot files or live processes are touched.",
        "- Keeps `book_margin` as the high-coverage base and tests only weak near-strike overlays.",
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
        lines.append("- No near-strike breakout/reversion overlay clears the strict gate.")
    else:
        best = strict.iloc[0]
        lines.append(
            f"- Best strict diagnostic row is `{best['label_current']}` with combined all-ledger net "
            f"{fmt_cents(best['combined_all_net_pnl_cents'])}."
        )
        lines.append("- This is still post-hoc research and must be forward-locked before any promotion.")
    for path in [REPORT_MD, OUT_DIR / f"near_strike_breakout_regime_frontier_{generated}.md"]:
        path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    generated = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%SZ")
    frame, blocks, diagnostics = scan()
    frame.to_csv(CSV_LATEST, index=False)
    frame.to_csv(OUT_DIR / f"near_strike_breakout_regime_frontier_{generated}.csv", index=False)
    blocks.to_csv(BLOCKS_LATEST, index=False)
    blocks.to_csv(OUT_DIR / f"near_strike_breakout_regime_blocks_{generated}.csv", index=False)
    write_report(generated, frame, diagnostics)
    payload = {"generated_utc": generated, "diagnostics": diagnostics, "rows": frame.to_dict("records")}
    for path in [REPORT_JSON, OUT_DIR / f"near_strike_breakout_regime_frontier_{generated}.json"]:
        path.write_text(json.dumps(clean_json_local(payload), indent=2, sort_keys=True), encoding="utf-8")
    print("Near-strike breakout regime frontier complete")
    print(f"rows={len(frame)}")
    print(f"strict_pass={diagnostics['strict_pass_rows']}")
    print(f"report={REPORT_MD}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
