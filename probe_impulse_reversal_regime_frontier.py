"""Impulse-over-margin reversal frontier for BTC 15m fair value.

The recent live failures point to a specific physical failure mode: the chosen
side can become expensive right after a short-horizon BTC impulse that is
larger than the remaining side-specific distance to the strike. In that state,
the book and Brownian terminal model can be marking the current displacement as
stable when it may be a transient shove with enough time left to revert.

This research-only probe tests small, interpretable overlays on high-coverage
book/physics policies:

1. veto: wait for the same base policy after impulse-over-margin clears.
2. fade: buy the opposite side when the overreaction state is extreme and the
   opposite side is still cheap.

Rows are evaluated on the current two-sided heartbeat ledger and the independent
v21 ledger with train/validation/holdout splits and block stability. No orders
are submitted and no live bot files or processes are touched.
"""
from __future__ import annotations

import json
import math
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Dict, Iterable, List, Optional

import numpy as np
import pandas as pd

from probe_cross_dataset_interval_frontier import load_v21_side_rows
from probe_cross_dataset_profit_frontier import enrich_selected, fmt_cents, fmt_roi, metrics_for
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


REPORT_MD = OUT_DIR / "impulse_reversal_regime_frontier_latest.md"
REPORT_JSON = OUT_DIR / "impulse_reversal_regime_frontier_latest.json"
CSV_LATEST = OUT_DIR / "impulse_reversal_regime_frontier_latest.csv"
BLOCKS_LATEST = OUT_DIR / "impulse_reversal_regime_blocks_latest.csv"
SLICES_LATEST = OUT_DIR / "impulse_reversal_regime_slices_latest.csv"

BLOCK_MARKETS = 20
MIN_BLOCK_MARKETS = 10
POSITIVE_BLOCK_RATE_FLOOR = 0.70


BASE_POLICIES = {
    "book_margin": Policy("book_p_side", 0.60, 95.0, 120.0, "margin_rv15>=0"),
    "book55_margin": Policy("book_p_side", 0.55, 95.0, 120.0, "margin_rv15>=0"),
    "mean55": Policy("score_mean_book_rv15", 0.55, 95.0, 120.0, "none"),
    "min55": Policy("score_min_book_rv15", 0.55, 95.0, 120.0, "none"),
    "regime55": Policy("score_regime_blend", 0.55, 95.0, 120.0, "none"),
}


@dataclass(frozen=True)
class ReversalSpec:
    name: str
    base_name: str
    action: str
    impulse_col: str
    impulse_abs_min: float
    over_margin_min: float
    min_seconds_to_close: float
    max_margin_sigma: float
    max_chosen_score: float
    max_fade_ask: float = 45.0

    @property
    def base_policy(self) -> Policy:
        return BASE_POLICIES[self.base_name]

    @property
    def label(self) -> str:
        base = self.base_policy.label
        return (
            f"{self.action}; base={self.base_name}; {base}; "
            f"{self.impulse_col}>={self.impulse_abs_min:g}; "
            f"{self.impulse_col}-margin>={self.over_margin_min:g}; "
            f"sec>={self.min_seconds_to_close:g}; margin_sigma<={self.max_margin_sigma:g}; "
            f"score<={self.max_chosen_score:g}; fade_ask<={self.max_fade_ask:g}"
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


def coerce_extra_numeric(rows: pd.DataFrame) -> pd.DataFrame:
    out = rows.copy()
    for col in [
        "margin_dollars",
        "margin_per_rv_sigma_15m",
        "signed_move_1m",
        "signed_move_3m",
        "signed_move_5m",
        "signed_move_10m",
        "signed_move_15m",
        "signed_move_30m",
        "signed_move_60m",
        "drift_p_1m_rv_15m",
        "drift_p_3m_rv_15m",
        "drift_p_5m_rv_15m",
        "drift_p_10m_rv_15m",
        "drift_p_15m_rv_15m",
    ]:
        if col not in out.columns:
            out[col] = np.nan
        out[col] = pd.to_numeric(out[col], errors="coerce")
    out["impulse_3_5m"] = out[["signed_move_3m", "signed_move_5m"]].max(axis=1)
    out["impulse_1_3_5m"] = out[["signed_move_1m", "signed_move_3m", "signed_move_5m"]].max(axis=1)
    out["fresh_impulse_5v30"] = out["signed_move_5m"] - out["signed_move_30m"]
    out["fresh_impulse_3v15"] = out["signed_move_3m"] - out["signed_move_15m"]
    out["abs_margin_dollars"] = out["margin_dollars"].abs()
    for impulse_col in ["signed_move_3m", "signed_move_5m", "impulse_3_5m", "impulse_1_3_5m"]:
        out[f"{impulse_col}_over_margin"] = out[impulse_col] - out["abs_margin_dollars"]
        out[f"{impulse_col}_ratio"] = out[impulse_col] / out["abs_margin_dollars"].clip(lower=1.0)
    return out


def make_specs() -> List[ReversalSpec]:
    specs: List[ReversalSpec] = []

    # Baseline rows, expressed as no-overlay specs for common reporting.
    for base_name in BASE_POLICIES:
        specs.append(
            ReversalSpec(
                name=f"{base_name}_baseline",
                base_name=base_name,
                action="baseline",
                impulse_col="impulse_3_5m",
                impulse_abs_min=10_000.0,
                over_margin_min=10_000.0,
                min_seconds_to_close=120.0,
                max_margin_sigma=10_000.0,
                max_chosen_score=1.0,
            )
        )

    # A compact physics grid: only the variables needed to express
    # "fresh shove is larger than the current distance to strike".
    for base_name in ["book_margin", "book55_margin", "mean55", "min55", "regime55"]:
        for impulse_col in ["signed_move_5m", "impulse_3_5m"]:
            for impulse_abs_min in [40.0, 60.0, 80.0]:
                for over_margin_min in [0.0, 20.0, 40.0]:
                    for max_margin_sigma in [0.50, 0.75]:
                        specs.append(
                            ReversalSpec(
                                name=(
                                    f"{base_name}_veto_{impulse_col}_abs{impulse_abs_min:g}_"
                                    f"over{over_margin_min:g}_sig{max_margin_sigma:g}"
                                ),
                                base_name=base_name,
                                action="veto",
                                impulse_col=impulse_col,
                                impulse_abs_min=impulse_abs_min,
                                over_margin_min=over_margin_min,
                                min_seconds_to_close=600.0,
                                max_margin_sigma=max_margin_sigma,
                                max_chosen_score=0.82,
                            )
                        )
            # Fading is more fragile, so scan fewer, more extreme states.
            for over_margin_min in [20.0, 40.0]:
                specs.append(
                    ReversalSpec(
                        name=f"{base_name}_fade_{impulse_col}_abs60_over{over_margin_min:g}",
                        base_name=base_name,
                        action="fade",
                        impulse_col=impulse_col,
                        impulse_abs_min=60.0,
                        over_margin_min=over_margin_min,
                        min_seconds_to_close=600.0,
                        max_margin_sigma=0.75,
                        max_chosen_score=0.82,
                        max_fade_ask=45.0,
                    )
                )
    return specs


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


def overreaction_mask(rows: pd.DataFrame, spec: ReversalSpec) -> pd.Series:
    impulse = pd.to_numeric(rows.get(spec.impulse_col), errors="coerce")
    over_margin = pd.to_numeric(rows.get(f"{spec.impulse_col}_over_margin"), errors="coerce")
    score = pd.to_numeric(rows.get(spec.base_policy.chooser), errors="coerce")
    margin_sigma = pd.to_numeric(rows.get("margin_per_rv_sigma_15m"), errors="coerce")
    seconds = pd.to_numeric(rows.get("seconds_to_close"), errors="coerce")
    return (
        impulse.ge(spec.impulse_abs_min)
        & over_margin.ge(spec.over_margin_min)
        & seconds.ge(spec.min_seconds_to_close)
        & margin_sigma.le(spec.max_margin_sigma)
        & score.le(spec.max_chosen_score)
    ).fillna(False)


def opposite_rows(side_rows: pd.DataFrame) -> pd.DataFrame:
    key_cols = [
        "decision_key",
        "entry_dt",
        "entry_minute",
        "market",
        "side",
        "ask_cents",
        "bid_cents",
        "book_p_side",
        "brownian_p_rv_15m",
        "score_mean_book_rv15",
        "score_min_book_rv15",
        "score_regime_blend",
    ]
    keep = [col for col in key_cols if col in side_rows.columns]
    opp = side_rows[keep].copy()
    rename = {
        col: f"opp_{col}"
        for col in keep
        if col not in {"decision_key", "entry_dt", "entry_minute", "market"}
    }
    return opp.rename(columns=rename)


def select_for_spec(side_rows: pd.DataFrame, base: pd.DataFrame, spec: ReversalSpec) -> pd.DataFrame:
    rows = coerce_extra_numeric(side_rows).merge(base[["market", "split"]], on="market", how="inner")
    policy = spec.base_policy
    chosen = choose_decision_sides(rows, policy.chooser)
    if chosen.empty:
        return enrich_selected(chosen)
    base_mask = gate_mask(chosen, policy)
    chosen = chosen[base_mask.fillna(False)].copy()
    if chosen.empty:
        return enrich_selected(chosen)

    if spec.action == "baseline":
        selected = first_market_rows(chosen)
        selected["candidate"] = spec.name
        selected["action_taken"] = "baseline"
        return enrich_selected(selected)

    reaction = overreaction_mask(chosen, spec)

    if spec.action == "veto":
        eligible = chosen[~reaction].copy()
        if eligible.empty:
            return enrich_selected(eligible)
        selected = first_market_rows(eligible)
        selected["candidate"] = spec.name
        selected["action_taken"] = "base_after_veto"
        return enrich_selected(selected)

    if spec.action != "fade":
        raise ValueError(f"unknown action: {spec.action}")

    opp = opposite_rows(rows)
    faded = chosen[reaction].merge(
        opp,
        on=[col for col in ["decision_key", "entry_dt", "entry_minute", "market"] if col in opp.columns],
        how="left",
    )
    faded = faded[faded["opp_side"].notna() & faded["opp_side"].ne(faded["side"])].copy()
    if not faded.empty:
        faded = faded[pd.to_numeric(faded["opp_ask_cents"], errors="coerce").le(spec.max_fade_ask)].copy()
    if not faded.empty:
        for col in list(faded.columns):
            if col.startswith("opp_"):
                base_col = col[4:]
                if base_col in faded.columns:
                    faded[base_col] = faded[col]
        faded["action_taken"] = "fade"

    normal = chosen[~reaction].copy()
    normal["action_taken"] = "base"
    mixed = pd.concat([normal, faded], ignore_index=True, sort=False)
    if mixed.empty:
        return enrich_selected(mixed)
    selected = first_market_rows(mixed)
    selected["candidate"] = spec.name
    return enrich_selected(selected)


def summarize_metrics(dataset: str, spec: ReversalSpec, base: pd.DataFrame, selected: pd.DataFrame) -> Dict[str, Any]:
    metrics = metrics_for(base, selected)
    row: Dict[str, Any] = {
        "dataset": dataset,
        "candidate": spec.name,
        "label": spec.label,
        "base_name": spec.base_name,
        "action": spec.action,
        "impulse_col": spec.impulse_col,
        "impulse_abs_min": spec.impulse_abs_min,
        "over_margin_min": spec.over_margin_min,
        "min_seconds_to_close": spec.min_seconds_to_close,
        "max_margin_sigma": spec.max_margin_sigma,
        "max_chosen_score": spec.max_chosen_score,
        "max_fade_ask": spec.max_fade_ask,
        "fade_selected": int(selected.get("action_taken", pd.Series(dtype=object)).astype(str).eq("fade").sum())
        if not selected.empty
        else 0,
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


def block_rows(dataset: str, spec: ReversalSpec, base: pd.DataFrame, selected: pd.DataFrame) -> List[Dict[str, Any]]:
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
        rows.append(
            {
                "dataset": dataset,
                "candidate": spec.name,
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
                "fade_selected": int(part.get("action_taken", pd.Series(dtype=object)).astype(str).eq("fade").sum())
                if n
                else 0,
            }
        )
    return rows


def bucket(value: Any, cuts: List[float], labels: List[str]) -> str:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return "NA"
    if not math.isfinite(number):
        return "NA"
    for cut, label in zip(cuts, labels):
        if number <= cut:
            return label
    return labels[-1]


def slice_rows(dataset: str, spec: ReversalSpec, selected: pd.DataFrame) -> List[Dict[str, Any]]:
    if selected.empty:
        return []
    frame = coerce_extra_numeric(selected)
    frame["entry_dt"] = pd.to_datetime(frame["entry_dt"], utc=True, errors="coerce")
    frame["hour_utc"] = frame["entry_dt"].dt.hour.astype("Int64").astype(str)
    frame["impulse_bucket"] = [
        bucket(value, [0, 40, 80, 120], ["<=0", "<=40", "<=80", "<=120", ">120"])
        for value in pd.to_numeric(frame.get(spec.impulse_col), errors="coerce")
    ]
    frame["over_margin_bucket"] = [
        bucket(value, [-20, 0, 20, 40], ["<=-20", "<=0", "<=20", "<=40", ">40"])
        for value in pd.to_numeric(frame.get(f"{spec.impulse_col}_over_margin"), errors="coerce")
    ]
    frame["action_bucket"] = frame.get("action_taken", pd.Series("base", index=frame.index)).fillna("base").astype(str)
    out: List[Dict[str, Any]] = []
    for group_type, col in [
        ("split", "split"),
        ("side", "side"),
        ("hour", "hour_utc"),
        ("action", "action_bucket"),
        ("impulse", "impulse_bucket"),
        ("over_margin", "over_margin_bucket"),
    ]:
        for group, part in frame.groupby(col, dropna=False, sort=True):
            n = int(len(part))
            wins = int(part["win"].astype(bool).sum()) if n else 0
            net = float(pd.to_numeric(part.get("net_pnl_cents"), errors="coerce").sum()) if n else 0.0
            out.append(
                {
                    "dataset": dataset,
                    "candidate": spec.name,
                    "group_type": group_type,
                    "group": str(group),
                    "markets": n,
                    "wins": wins,
                    "losses": n - wins,
                    "accuracy": wins / n if n else None,
                    "net_pnl_cents": net,
                    "net_per_market_cents": net / n if n else None,
                    "median_ask": float(pd.to_numeric(part.get("ask_cents"), errors="coerce").median()) if n else None,
                    "median_seconds_to_close": float(pd.to_numeric(part.get("seconds_to_close"), errors="coerce").median())
                    if n
                    else None,
                }
            )
    return out


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
                "blocks": int(len(part)),
                "positive_blocks": int(part["positive_net"].sum()),
                "positive_block_rate": float(part["positive_net"].mean()) if len(part) else None,
                "coverage_pass_blocks": int(part["coverage_pass"].sum()),
                "coverage_block_rate": float(part["coverage_pass"].mean()) if len(part) else None,
                "worst_block_net_cents": float(part["net_pnl_cents"].min()) if len(part) else None,
                "median_block_net_cents": float(part["net_pnl_cents"].median()) if len(part) else None,
            }
        )
    return pd.DataFrame(rows)


def combined_summary(current: pd.DataFrame, v21: pd.DataFrame, stability: pd.DataFrame) -> pd.DataFrame:
    merged = current.merge(v21, on="candidate", suffixes=("_current", "_v21"))
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
        merged = merged.merge(pd.DataFrame(stab_rows), on="candidate", how="left")
    else:
        merged["min_positive_block_rate"] = np.nan
        merged["min_coverage_block_rate"] = np.nan
        merged["worst_block_net_cents"] = np.nan

    merged["combined_all_net_pnl_cents"] = (
        pd.to_numeric(merged["all_net_pnl_cents_current"], errors="coerce").fillna(0.0)
        + pd.to_numeric(merged["all_net_pnl_cents_v21"], errors="coerce").fillna(0.0)
    )
    merged["combined_oos_net_pnl_cents"] = (
        pd.to_numeric(merged["validation_net_pnl_cents_current"], errors="coerce").fillna(0.0)
        + pd.to_numeric(merged["holdout_net_pnl_cents_current"], errors="coerce").fillna(0.0)
        + pd.to_numeric(merged["validation_net_pnl_cents_v21"], errors="coerce").fillna(0.0)
        + pd.to_numeric(merged["holdout_net_pnl_cents_v21"], errors="coerce").fillna(0.0)
    )
    merged["both_coverage_pass"] = merged["coverage_pass_current"].astype(bool) & merged["coverage_pass_v21"].astype(bool)
    merged["both_oos_positive"] = merged["oos_positive_current"].astype(bool) & merged["oos_positive_v21"].astype(bool)
    merged["both_all_splits_positive"] = (
        merged["all_splits_positive_current"].astype(bool) & merged["all_splits_positive_v21"].astype(bool)
    )
    merged["block_stability_pass"] = (
        pd.to_numeric(merged["min_positive_block_rate"], errors="coerce").fillna(0.0).ge(POSITIVE_BLOCK_RATE_FLOOR)
        & pd.to_numeric(merged["min_coverage_block_rate"], errors="coerce").fillna(0.0).ge(POSITIVE_BLOCK_RATE_FLOOR)
    )
    merged["strict_pass"] = (
        merged["both_coverage_pass"]
        & merged["both_oos_positive"]
        & merged["both_all_splits_positive"]
        & merged["block_stability_pass"]
    )
    merged["min_split_coverage"] = merged[["min_split_coverage_current", "min_split_coverage_v21"]].min(axis=1)
    merged["min_oos_edge_cents"] = merged[["min_oos_edge_cents_current", "min_oos_edge_cents_v21"]].min(axis=1)
    merged["min_oos_roi"] = merged[["min_oos_roi_current", "min_oos_roi_v21"]].min(axis=1)
    return merged.sort_values(
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


def scan() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, Dict[str, Any]]:
    current_side = coerce_extra_numeric(load_side_rows())
    v21_side = coerce_extra_numeric(load_v21_side_rows())
    current_base = market_base(current_side)
    v21_base = market_base(v21_side)
    specs = make_specs()

    current_rows: List[Dict[str, Any]] = []
    v21_rows: List[Dict[str, Any]] = []
    block_out: List[Dict[str, Any]] = []
    slice_out: List[Dict[str, Any]] = []

    for spec in specs:
        current_selected = select_for_spec(current_side, current_base, spec)
        v21_selected = select_for_spec(v21_side, v21_base, spec)
        current_rows.append(summarize_metrics("current", spec, current_base, current_selected))
        v21_rows.append(summarize_metrics("v21", spec, v21_base, v21_selected))
        block_out.extend(block_rows("current", spec, current_base, current_selected))
        block_out.extend(block_rows("v21", spec, v21_base, v21_selected))
        # Slice only the baselines and promising overlays to keep output readable.
        if spec.action == "baseline" or (
            len(current_selected) >= int(0.75 * len(current_base))
            and len(v21_selected) >= int(0.75 * len(v21_base))
        ):
            slice_out.extend(slice_rows("current", spec, current_selected))
            slice_out.extend(slice_rows("v21", spec, v21_selected))

    current_summary = pd.DataFrame(current_rows)
    v21_summary = pd.DataFrame(v21_rows)
    blocks = pd.DataFrame(block_out)
    slices = pd.DataFrame(slice_out)
    stability = block_stability(blocks)
    combined = combined_summary(current_summary, v21_summary, stability)
    diagnostics = {
        "current_markets": int(len(current_base)),
        "v21_markets": int(len(v21_base)),
        "specs": int(len(specs)),
        "strict_pass_rows": int(combined["strict_pass"].sum()) if not combined.empty else 0,
    }
    return combined, blocks, slices, diagnostics


def table_row(row: Dict[str, Any]) -> str:
    return (
        f"| `{row['label_current']}` | {row['strict_pass']} | {fmt_cents(row['combined_all_net_pnl_cents'])} | "
        f"{fmt_cents(row['combined_oos_net_pnl_cents'])} | {pct(row['min_split_coverage'])} | "
        f"{pct(row['all_coverage_current'])}/{pct(row['all_coverage_v21'])} | "
        f"{fmt_cents(row['all_net_pnl_cents_current'])}/{fmt_cents(row['all_net_pnl_cents_v21'])} | "
        f"{pct(row['all_accuracy_current'])}/{pct(row['all_accuracy_v21'])} | "
        f"{fmt_num(row['min_positive_block_rate'])} | {fmt_cents(row['worst_block_net_cents'])} | "
        f"{int(row['fade_selected_current'])}/{int(row['fade_selected_v21'])} |"
    )


def write_report(generated: str, frame: pd.DataFrame, diagnostics: Dict[str, Any]) -> None:
    strict = frame[frame["strict_pass"]]
    top = frame.head(30)
    baseline = frame[frame["action_current"].eq("baseline")]
    lines = [
        "# Impulse Reversal Regime Frontier",
        "",
        f"Generated UTC: `{generated}`",
        "",
        "## Scope",
        "",
        "- Research-only scan; no orders are submitted and no bot files or live processes are touched.",
        "- Tests whether short-horizon favorable impulse larger than distance-to-strike is an overreaction state.",
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
        "| policy | strict | combined all net | combined OOS net | min split cov | current/v21 cov | current/v21 net | current/v21 acc | min block+ rate | worst block | fades current/v21 |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for _, row in top.iterrows():
        lines.append(table_row(row.to_dict()))

    lines += ["", "## Baselines", ""]
    if baseline.empty:
        lines.append("- No baseline rows were produced.")
    else:
        lines += [
            "| policy | combined all net | combined OOS net | min split cov | current/v21 cov | current/v21 net | current/v21 acc |",
            "|---|---:|---:|---:|---:|---:|---:|",
        ]
        for _, row in baseline.sort_values("combined_all_net_pnl_cents", ascending=False).iterrows():
            lines.append(
                f"| `{row['label_current']}` | {fmt_cents(row['combined_all_net_pnl_cents'])} | "
                f"{fmt_cents(row['combined_oos_net_pnl_cents'])} | {pct(row['min_split_coverage'])} | "
                f"{pct(row['all_coverage_current'])}/{pct(row['all_coverage_v21'])} | "
                f"{fmt_cents(row['all_net_pnl_cents_current'])}/{fmt_cents(row['all_net_pnl_cents_v21'])} | "
                f"{pct(row['all_accuracy_current'])}/{pct(row['all_accuracy_v21'])} |"
            )

    lines += ["", "## Read", ""]
    if strict.empty:
        lines.append("- No impulse reversal overlay clears the full strict gate. Do not promote any row from this scan.")
    else:
        best = strict.iloc[0]
        lines.append(
            f"- Best strict diagnostic row is `{best['label_current']}` with combined all-ledger net "
            f"{fmt_cents(best['combined_all_net_pnl_cents'])} and combined OOS net "
            f"{fmt_cents(best['combined_oos_net_pnl_cents'])}."
        )
        lines.append("- This is still diagnostic because the overlay was selected after seeing historical outcomes; it needs a forward lock.")

    for path in [REPORT_MD, OUT_DIR / f"impulse_reversal_regime_frontier_{generated}.md"]:
        path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    generated = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%SZ")
    frame, blocks, slices, diagnostics = scan()
    frame.to_csv(CSV_LATEST, index=False)
    frame.to_csv(OUT_DIR / f"impulse_reversal_regime_frontier_{generated}.csv", index=False)
    blocks.to_csv(BLOCKS_LATEST, index=False)
    blocks.to_csv(OUT_DIR / f"impulse_reversal_regime_blocks_{generated}.csv", index=False)
    slices.to_csv(SLICES_LATEST, index=False)
    slices.to_csv(OUT_DIR / f"impulse_reversal_regime_slices_{generated}.csv", index=False)
    write_report(generated, frame, diagnostics)
    payload = {
        "generated_utc": generated,
        "diagnostics": diagnostics,
        "rows": frame.to_dict("records"),
    }
    for path in [REPORT_JSON, OUT_DIR / f"impulse_reversal_regime_frontier_{generated}.json"]:
        path.write_text(json.dumps(clean_json_local(payload), indent=2, sort_keys=True), encoding="utf-8")
    print("Impulse reversal regime frontier complete")
    print(f"rows={len(frame)}")
    print(f"strict_pass={diagnostics['strict_pass_rows']}")
    print(f"report={REPORT_MD}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
