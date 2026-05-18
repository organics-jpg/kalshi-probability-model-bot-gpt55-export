"""Strict-forward shadow monitor for v58: v55 FV with YES-axis margin-gated exit.

Research-only. Entry is the v55 book-anchor FV candidate. Exit uses the v57
hold15/prob52 trigger, but only exits when the YES-axis spot geometry is no more
than +0.25 sigma above the strike. This is intentionally labeled as an
asymmetric market-structure candidate, not a symmetric held-side physics law.

No live bot files, processes, or order paths are touched.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

import probe_v55_book_anchor_recross_shadow_monitor as v55_monitor
from probe_market_interval_80coverage import clean_json


OUT_DIR = Path(__file__).resolve().parent / "logs" / "edge_research"
v42 = v55_monitor.v42
shadow = v42.shadow
ORIGINAL_LOAD_OR_CREATE_LOCK = v42.load_or_create_lock

EXIT_YES_AXIS_MARGIN_CEILING_SIGMA15 = 0.25

v42.POLICY = "v58_v55_bookanchor_hold15_prob52_marginlte0p25_edge0_p65_stc0_600"
v42.REPORT_PREFIX = "v58_v55_margin_exit_shadow"
shadow.POLICY = v42.POLICY
shadow.EXIT_PROB_FLOOR = 0.52
shadow.EXIT_MIN_HOLD_SECONDS = 15.0
shadow.LOCK_PATH = OUT_DIR / "v58_v55_margin_exit_shadow_lock.json"
shadow.REGISTRY_PATH = OUT_DIR / "v58_v55_margin_exit_shadow_registry_latest.csv"
shadow.REPORT_MD = OUT_DIR / "v58_v55_margin_exit_shadow_monitor_latest.md"
shadow.REPORT_JSON = OUT_DIR / "v58_v55_margin_exit_shadow_monitor_latest.json"


def yes_axis_margin_sigma15(rows: pd.DataFrame) -> pd.Series:
    sign = np.where(rows["side"].astype(str).eq("yes"), 1.0, -1.0)
    margin = pd.to_numeric(rows.get("margin_per_rv_sigma_15m"), errors="coerce")
    fallback = pd.to_numeric(rows.get("recross_side_margin_sigma15"), errors="coerce")
    return pd.Series(sign * margin, index=rows.index).fillna(fallback)


def load_or_create_lock() -> dict[str, Any]:
    lock = ORIGINAL_LOAD_OR_CREATE_LOCK()
    lock["lock_id"] = "v58_v55_margin_exit_shadow_v1"
    lock["policy"] = v42.POLICY
    lock["exit"] = {
        "probability_floor": 0.52,
        "min_hold_seconds": 15.0,
        "exit_yes_axis_margin_ceiling_sigma15": EXIT_YES_AXIS_MARGIN_CEILING_SIGMA15,
        "exit_rule": "exit only when p_side <= floor and YES-axis spot margin <= ceiling",
    }
    lock["purpose"] = "Strict-forward shadow validation of v58 v55 FV with asymmetric YES-axis margin-gated probability exit."
    shadow.LOCK_PATH.write_text(json.dumps(clean_json(lock), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return lock


def update_exits_and_outcomes(
    registry: pd.DataFrame,
    predictions: pd.DataFrame,
    outcomes: dict[str, dict[str, Any]],
    lock: dict[str, Any],
) -> pd.DataFrame:
    if registry.empty:
        return registry
    out = registry.copy()
    out["status"] = out["status"].fillna("open").astype(str)
    for timestamp_col in ["exit_dt", "resolved_utc"]:
        if timestamp_col in out.columns:
            out[timestamp_col] = out[timestamp_col].astype("object")
    adjusted = v42.adjusted_prediction_rows(predictions, lock)
    adjusted["exit_yes_axis_margin_sigma15"] = yes_axis_margin_sigma15(adjusted)
    resolved_at = shadow.utc_now()
    for idx, row in out.iterrows():
        status = str(row.get("status") or "open").lower()
        if status in {"exited", "settled"}:
            continue
        market = str(row["market"])
        selected_side = str(row["selected_side"]).lower()
        entry_dt = pd.Timestamp(row["entry_dt"])
        ask = float(row["selected_ask_cents"])
        min_hold_seconds = float(getattr(shadow, "EXIT_MIN_HOLD_SECONDS", 0.0) or 0.0)
        min_exit_dt = entry_dt + pd.Timedelta(seconds=min_hold_seconds)
        time_mask = adjusted["entry_dt"].ge(min_exit_dt) if min_hold_seconds > 0.0 else adjusted["entry_dt"].gt(entry_dt)
        future = adjusted[
            adjusted["market"].astype(str).eq(market)
            & adjusted["side"].astype(str).eq(selected_side)
            & time_mask
            & adjusted["bid_cents"].notna()
            & adjusted["bid_cents"].ge(1.0)
        ].copy()
        if not future.empty:
            future["exit_p_side"] = np.where(
                future["side"].astype(str).eq("yes"),
                future["p_yes"],
                1.0 - future["p_yes"],
            )
            trigger = future[
                future["exit_p_side"].le(shadow.EXIT_PROB_FLOOR)
                & future["exit_yes_axis_margin_sigma15"].le(EXIT_YES_AXIS_MARGIN_CEILING_SIGMA15)
            ].sort_values("entry_dt").head(1)
            if not trigger.empty:
                hit = trigger.iloc[0]
                bid = float(hit["bid_cents"])
                gross = (bid - ask) * shadow.QTY
                updates = shadow.finalize_row(row, gross, shadow.estimate_fee_cents(bid), "exited")
                for key, value in updates.items():
                    out.at[idx, key] = value
                out.at[idx, "exit_dt"] = hit["entry_dt"]
                out.at[idx, "exit_bid_cents"] = bid
                out.at[idx, "exit_p_side"] = float(hit["exit_p_side"])
                out.at[idx, "exit_yes_axis_margin_sigma15"] = float(hit["exit_yes_axis_margin_sigma15"])
                continue
        outcome = str(outcomes.get(market, {}).get("outcome") or "").lower()
        if outcome in {"yes", "no"}:
            win = selected_side == outcome
            settlement = 100.0 if win else 0.0
            gross = (settlement - ask) * shadow.QTY
            updates = shadow.finalize_row(row, gross, 0.0, "settled")
            for key, value in updates.items():
                out.at[idx, key] = value
            out.at[idx, "outcome"] = outcome
            out.at[idx, "resolved_utc"] = resolved_at
            out.at[idx, "win"] = bool(win)
    return out


v42.load_or_create_lock = load_or_create_lock
v42.update_exits_and_outcomes = update_exits_and_outcomes


if __name__ == "__main__":
    raise SystemExit(v42.main())
