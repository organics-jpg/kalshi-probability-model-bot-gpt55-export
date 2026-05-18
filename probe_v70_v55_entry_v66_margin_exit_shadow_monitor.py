"""Strict-forward shadow monitor for v70 balanced candidate.

Research-only. Entry uses the broad v55 FV surface. Exit uses the v66 balanced
probability surface plus the v60 NO-side YES-axis margin gate.

No live bot files, processes, or order paths are touched.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

import probe_v55_book_anchor_recross_shadow_monitor as v55_monitor
import probe_v66_no_bookgap_balanced_shadow_monitor as v66_monitor
from probe_market_interval_80coverage import clean_json


OUT_DIR = Path(__file__).resolve().parent / "logs" / "edge_research"
v42 = v66_monitor.v42
shadow = v42.shadow
ENTRY_OPPORTUNITY_TABLE = v55_monitor.opportunity_table
EXIT_OPPORTUNITY_TABLE = v66_monitor.opportunity_table
ORIGINAL_LOAD_OR_CREATE_LOCK = v42.load_or_create_lock

EXIT_YES_AXIS_MARGIN_CEILING_SIGMA15 = 0.25

v42.POLICY = "v70_v55_entry_v66_bal_hold15_prob52_noside_marginlte0p25"
v42.REPORT_PREFIX = "v70_v55_entry_v66_margin_exit_shadow"
shadow.POLICY = v42.POLICY
shadow.ENTRY_EDGE_FLOOR_CENTS = 0.0
shadow.ENTRY_P_SIDE_FLOOR = 0.65
shadow.ENTRY_ASK_FLOOR_CENTS = 1.0
shadow.ENTRY_ASK_CAP_CENTS = 100.0
shadow.ENTRY_MIN_STC = 0.0
shadow.ENTRY_MAX_STC = 600.0
shadow.EXIT_PROB_FLOOR = 0.52
shadow.EXIT_MIN_HOLD_SECONDS = 15.0
shadow.LOCK_PATH = OUT_DIR / "v70_v55_entry_v66_margin_exit_shadow_lock.json"
shadow.REGISTRY_PATH = OUT_DIR / "v70_v55_entry_v66_margin_exit_shadow_registry_latest.csv"
shadow.REPORT_MD = OUT_DIR / "v70_v55_entry_v66_margin_exit_shadow_monitor_latest.md"
shadow.REPORT_JSON = OUT_DIR / "v70_v55_entry_v66_margin_exit_shadow_monitor_latest.json"


def yes_axis_margin_sigma15(rows: pd.DataFrame) -> pd.Series:
    sign = np.where(rows["side"].astype(str).eq("yes"), 1.0, -1.0)
    margin = pd.to_numeric(rows.get("margin_per_rv_sigma_15m"), errors="coerce")
    fallback = pd.to_numeric(rows.get("recross_side_margin_sigma15"), errors="coerce")
    return pd.Series(sign * margin, index=rows.index).fillna(fallback)


def load_or_create_lock() -> dict[str, Any]:
    lock = ORIGINAL_LOAD_OR_CREATE_LOCK()
    lock["lock_id"] = "v70_v55_entry_v66_margin_exit_shadow_v1"
    lock["policy"] = v42.POLICY
    lock["entry_surface"] = "v55_bookanchor_m10_v20_g05_book_plus2"
    lock["exit_surface"] = "v66_no_bookgap_g08_blend75"
    lock["entry"] = {
        "edge_floor_cents": 0.0,
        "p_side_floor": 0.65,
        "ask_floor_cents": 1.0,
        "ask_cap_cents": 100.0,
        "min_seconds_to_close": 0.0,
        "max_seconds_to_close": 600.0,
    }
    lock["exit"] = {
        "probability_floor": 0.52,
        "min_hold_seconds": 15.0,
        "exit_yes_axis_margin_ceiling_sigma15": EXIT_YES_AXIS_MARGIN_CEILING_SIGMA15,
        "exit_rule": (
            "YES positions use hold15/prob52 on v66_bal; NO positions exit only when "
            "v66_bal p_side <= floor and YES-axis spot margin <= ceiling"
        ),
    }
    lock["purpose"] = (
        "Strict-forward shadow validation of v70 v55-entry/v66-balanced-exit "
        "NO-side margin-gated robustness candidate."
    )
    shadow.LOCK_PATH.write_text(json.dumps(clean_json(lock), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return lock


def opportunity_table(predictions: pd.DataFrame, lock: dict[str, Any]) -> pd.DataFrame:
    out = ENTRY_OPPORTUNITY_TABLE(predictions, lock).copy()
    if not out.empty:
        out["v70_entry_surface"] = "v55"
        out["v70_exit_surface"] = "v66_bal"
    return out


def adjusted_prediction_rows(predictions: pd.DataFrame, lock: dict[str, Any]) -> pd.DataFrame:
    opps = EXIT_OPPORTUNITY_TABLE(predictions, lock)[
        ["opportunity_key", "p_yes", "no_bookgap_shrink_active", "no_bookgap_model_book_gap"]
    ]
    out = predictions.merge(opps, on="opportunity_key", how="left")
    out["p_yes"] = pd.to_numeric(out["p_yes"], errors="coerce").fillna(
        pd.to_numeric(out[f"{shadow.MODEL}_p_yes"], errors="coerce")
    ).clip(1e-6, 1.0 - 1e-6)
    out["entry_dt"] = pd.to_datetime(out["entry_dt"], utc=True, errors="coerce")
    out["bid_cents"] = pd.to_numeric(out["bid_cents"], errors="coerce")
    out["exit_yes_axis_margin_sigma15"] = yes_axis_margin_sigma15(out)
    return out


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
    adjusted = adjusted_prediction_rows(predictions, lock)
    resolved_at = shadow.utc_now()
    for idx, row in out.iterrows():
        status = str(row.get("status") or "open").lower()
        if status in {"exited", "settled"}:
            continue
        market = str(row["market"])
        selected_side = str(row["selected_side"]).lower()
        entry_dt = pd.Timestamp(row["entry_dt"])
        ask = float(row["selected_ask_cents"])
        min_exit_dt = entry_dt + pd.Timedelta(seconds=float(shadow.EXIT_MIN_HOLD_SECONDS or 0.0))
        future = adjusted[
            adjusted["market"].astype(str).eq(market)
            & adjusted["side"].astype(str).eq(selected_side)
            & adjusted["entry_dt"].ge(min_exit_dt)
            & adjusted["bid_cents"].notna()
            & adjusted["bid_cents"].ge(1.0)
        ].copy()
        if not future.empty:
            future["exit_p_side"] = np.where(
                future["side"].astype(str).eq("yes"),
                future["p_yes"],
                1.0 - future["p_yes"],
            )
            trigger_mask = future["exit_p_side"].le(shadow.EXIT_PROB_FLOOR)
            if selected_side == "no":
                trigger_mask &= future["exit_yes_axis_margin_sigma15"].le(EXIT_YES_AXIS_MARGIN_CEILING_SIGMA15)
            trigger = future[trigger_mask].sort_values("entry_dt").head(1)
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


def write_report(lock: dict[str, Any], registry: pd.DataFrame, denom: dict[str, Any], new_count: int) -> None:
    final = (
        registry[registry["status"].astype(str).str.lower().isin(["exited", "settled"])].copy()
        if not registry.empty
        else registry
    )
    open_rows = (
        registry[~registry["status"].astype(str).str.lower().isin(["exited", "settled"])].copy()
        if not registry.empty
        else registry
    )
    fee_net = float(pd.to_numeric(final.get("fee_net_cents"), errors="coerce").fillna(0.0).sum()) if not final.empty else 0.0
    gross = float(pd.to_numeric(final.get("gross_pnl_cents"), errors="coerce").fillna(0.0).sum()) if not final.empty else 0.0
    fee_net_1c = (
        float(pd.to_numeric(final.get("fee_net_1c_entry_cents"), errors="coerce").fillna(0.0).sum())
        if not final.empty
        else 0.0
    )
    cost = (
        float(pd.to_numeric(final.get("selected_ask_cents"), errors="coerce").fillna(0.0).sum() * shadow.QTY)
        if not final.empty
        else 0.0
    )
    exited = int(final["status"].astype(str).str.lower().eq("exited").sum()) if not final.empty else 0
    settled = int(final["status"].astype(str).str.lower().eq("settled").sum()) if not final.empty else 0
    wins = int(final["win"].astype(str).str.lower().eq("true").sum()) if not final.empty else 0
    losses = int(settled - wins)
    roi = (fee_net / cost) if cost else None
    lines = [
        "# v70 v55 Entry / v66 Margin Exit Shadow Monitor",
        "",
        f"Generated UTC: `{datetime.now(timezone.utc).isoformat()}`",
        "",
        "## Scope",
        "",
        "- Strict-forward shadow validation of the v70 balanced candidate.",
        "- Registers only rows after the lock/model-defined timestamp. Late ingestion is allowed, but pre-lock backfill is not.",
        "- No live bot code/process/orders are touched.",
        "",
        "## Lock",
        "",
        f"- Created UTC: `{lock.get('created_utc')}`",
        f"- Model defined UTC: `{lock.get('model_defined_utc')}`",
        f"- Policy: `{v42.POLICY}`",
        "",
        "## Registry",
        "",
        f"- Registered shadow entries: {len(registry)}",
        f"- New entries this run: {new_count}",
        f"- Finalized / open: {len(final)} / {len(open_rows)}",
        f"- Exited / settled: {exited} / {settled}",
        f"- Observed candidate markets after lock: {denom.get('observed_candidate_markets')}",
        f"- Resolved / pending candidate markets after lock: {denom.get('resolved_candidate_markets')} / {denom.get('pending_candidate_markets')}",
        "",
        "## Finalized Performance",
        "",
        f"- Settlement W/L for settled rows: {wins}/{losses}",
        f"- Gross P&L: ${gross / 100.0:.2f}",
        f"- Fee-adjusted P&L: ${fee_net / 100.0:.2f}",
        f"- Fee-adjusted with 1c entry haircut: ${fee_net_1c / 100.0:.2f}",
        f"- Fee-adjusted ROI on entry cost: {'NA' if roi is None else f'{100.0 * roi:.2f}%'}",
        "",
        "## Read",
        "",
        "- Too few strict-forward finalized rows for a model decision."
        if len(final) < 30
        else "- Review live-forward sample size and stability before any promotion.",
    ]
    shadow.REPORT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


v42.opportunity_table = opportunity_table
v42.adjusted_prediction_rows = adjusted_prediction_rows
v42.update_exits_and_outcomes = update_exits_and_outcomes
v42.load_or_create_lock = load_or_create_lock
shadow.write_report = write_report


if __name__ == "__main__":
    raise SystemExit(v42.main())
