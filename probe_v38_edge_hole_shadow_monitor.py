"""Strict-forward shadow monitor for the v38 edge-hole candidate.

Candidate:
- v38 FV surface;
- first market signal with edge >= 0, p_side >= 0.65, ask <= 100, 0-600s to close;
- if that first signal has edge in (8c, 20c], block the whole market;
- otherwise shadow-enter and shadow-exit when p_side <= 0.52;
- rows may be late-ingested, but only if entry_dt is after the lock time;
- no orders are submitted and no live bot files/processes are touched.
"""
from __future__ import annotations

import json
import math
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from btc_mushroom_forecaster_v38_fast import FastMushroomFVEngineV38, FastMushroomV38Config
from probe_live_heartbeat_two_side_fv import group_candidates, heartbeat_two_side_rows
from probe_live_heartbeat_physics_priors import attach_physics
from probe_live_v28_fv_accuracy_volume import BOT_LOG, OUT_DIR, parse_bot_log
from probe_market_interval_80coverage import clean_json
from probe_mushroom_v29_fv_surface import EngineSpec, load_candles, replay_predictions
from probe_physics_priors_boundary_models import load_coinbase_candles
from shadow_live_v28_physics_validator import closed_market_outcomes_only


POLICY = "v38_edgehole_block_first_8_20_p65_prob52"
MODEL = "v38_long60_antipersist"
MODE = "two_side_all_heartbeats"
QTY = 2
ENTRY_EDGE_FLOOR_CENTS = 0.0
ENTRY_P_SIDE_FLOOR = 0.65
ENTRY_ASK_FLOOR_CENTS = 1.0
ENTRY_ASK_CAP_CENTS = 100.0
ENTRY_MAX_STC = 600.0
ENTRY_MIN_STC = 0.0
EDGE_HOLE_LOW = 8.0
EDGE_HOLE_HIGH = 20.0
EXIT_PROB_FLOOR = 0.52
KALSHI_TAKER_FEE_RATE = 0.07

LOCK_PATH = OUT_DIR / "v38_edge_hole_shadow_lock.json"
REGISTRY_PATH = OUT_DIR / "v38_edge_hole_shadow_registry_latest.csv"
REPORT_MD = OUT_DIR / "v38_edge_hole_shadow_monitor_latest.md"
REPORT_JSON = OUT_DIR / "v38_edge_hole_shadow_monitor_latest.json"

REGISTRY_COLUMNS = [
    "policy",
    "market",
    "opportunity_key",
    "entry_dt",
    "close_time",
    "source_line_no",
    "selected_side",
    "selected_ask_cents",
    "selected_edge_cents",
    "selected_p_side",
    "p_yes",
    "spot",
    "margin_per_rv_sigma_15m",
    "signed_velocity_dps_1m",
    "signed_velocity_dps_3m",
    "brownian_p_rv_15m",
    "raw_p_yes",
    "book_mid_p_yes",
    "raw_selected_side",
    "raw_selected_edge_cents",
    "latent_hole_active",
    "latent_disagreement_book_switch",
    "recross_hazard_active",
    "recross_side_margin_sigma15",
    "recross_side_velocity_3m",
    "thin_edge_certainty_active",
    "registered_utc",
    "exit_dt",
    "exit_bid_cents",
    "exit_p_side",
    "exit_fee_cents",
    "outcome",
    "resolved_utc",
    "win",
    "gross_pnl_cents",
    "entry_fee_cents",
    "total_fee_cents",
    "fee_net_cents",
    "fee_net_1c_entry_cents",
    "status",
]

PHYSICS_COLUMNS = [
    "spot",
    "side_sign",
    "margin_dollars",
    "margin_per_sqrt_sec",
    "margin_per_sqrt_min",
    "rv_sigma_t_5m",
    "rv_sigma_t_15m",
    "rv_sigma_t_30m",
    "rv_sigma_t_60m",
    "margin_per_rv_sigma_5m",
    "margin_per_rv_sigma_15m",
    "margin_per_rv_sigma_30m",
    "margin_per_rv_sigma_60m",
    "brownian_p_rv_5m",
    "brownian_p_rv_15m",
    "brownian_p_rv_30m",
    "brownian_p_rv_60m",
    "btc_close_lag_1m",
    "btc_close_lag_3m",
    "btc_close_lag_5m",
    "btc_close_lag_10m",
    "btc_close_lag_15m",
    "btc_close_lag_30m",
    "btc_close_lag_60m",
    "signed_move_1m",
    "signed_move_3m",
    "signed_move_5m",
    "signed_move_10m",
    "signed_move_15m",
    "signed_move_30m",
    "signed_move_60m",
    "signed_velocity_dps_1m",
    "signed_velocity_dps_3m",
    "signed_velocity_dps_5m",
    "signed_velocity_dps_10m",
    "signed_velocity_dps_15m",
    "signed_velocity_dps_30m",
    "signed_velocity_dps_60m",
    "adverse_move_1m",
    "adverse_move_3m",
    "adverse_move_5m",
    "adverse_move_10m",
    "adverse_move_15m",
    "adverse_move_30m",
    "adverse_move_60m",
    "drift_projected_margin_1m",
    "drift_projected_margin_3m",
    "drift_projected_margin_5m",
    "drift_projected_margin_10m",
    "drift_projected_margin_15m",
    "drift_projected_margin_30m",
    "drift_projected_margin_60m",
    "drift_p_1m_rv_15m",
    "drift_p_3m_rv_15m",
    "drift_p_5m_rv_15m",
    "drift_p_10m_rv_15m",
    "drift_p_15m_rv_15m",
    "drift_p_30m_rv_15m",
    "drift_p_60m_rv_15m",
    "book_minus_brownian_rv15",
    "physics_confirmed_book",
]


def utc_now() -> pd.Timestamp:
    return pd.Timestamp(datetime.now(timezone.utc))


def pct(value: Any) -> str:
    if value is None:
        return "NA"
    try:
        number = float(value)
    except (TypeError, ValueError):
        return "NA"
    if not math.isfinite(number):
        return "NA"
    return f"{100.0 * number:.2f}%"


def dollars_from_cents(value: Any) -> str:
    if value is None:
        return "NA"
    try:
        number = float(value) / 100.0
    except (TypeError, ValueError):
        return "NA"
    if not math.isfinite(number):
        return "NA"
    return f"${number:.2f}"


def estimate_fee_cents(price_cents: Any, contracts: int = QTY) -> float:
    try:
        price = float(price_cents)
        qty = int(round(float(contracts)))
    except (TypeError, ValueError):
        return 0.0
    if qty <= 0 or price <= 0.0 or price >= 100.0:
        return 0.0
    probability = price / 100.0
    return float(np.ceil(KALSHI_TAKER_FEE_RATE * qty * probability * (1.0 - probability) * 100.0))


def raw_rows(markets: dict[str, dict[str, Any]], outcomes: dict[str, dict[str, Any]]) -> pd.DataFrame:
    raw = heartbeat_two_side_rows(markets, outcomes)
    if raw.empty:
        return raw
    frame = group_candidates(raw, MODE)
    closes = pd.DataFrame(
        [
            {
                "market": market,
                "close_time": pd.to_datetime(info.get("close_time"), utc=True, errors="coerce"),
            }
            for market, info in markets.items()
        ]
    )
    frame = frame.merge(closes, on="market", how="left")
    return frame.sort_values(["entry_dt", "opportunity_key", "side"]).reset_index(drop=True)


def build_predictions(frame: pd.DataFrame) -> pd.DataFrame:
    engines = [
        EngineSpec(
            MODEL,
            FastMushroomFVEngineV38(FastMushroomV38Config()),
            "v38 long-memory anti-persistence FV surface",
        )
    ]
    if frame.empty:
        return frame.copy()
    try:
        candles = load_coinbase_candles(frame, fetch_missing=True)
    except Exception:
        candles = load_candles()
    predictions = replay_predictions(frame, candles, engines)

    try:
        physics, _ = attach_physics(frame, fetch_btc_candles=False)
    except Exception:
        physics = pd.DataFrame()
    if physics.empty:
        out = predictions.iloc[0:0].copy()
        out["btc_physics_fresh"] = False
        return out

    key_cols = ["entry_key"] if "entry_key" in predictions.columns and "entry_key" in physics.columns else [
        "opportunity_key",
        "side",
        "source_line_no",
    ]
    feature_cols = [col for col in PHYSICS_COLUMNS if col in physics.columns]
    merged = predictions.drop(columns=[col for col in feature_cols if col in predictions.columns], errors="ignore")
    merged = merged.merge(
        physics[key_cols + feature_cols].drop_duplicates(key_cols, keep="last"),
        on=key_cols,
        how="left",
    )
    merged["btc_physics_fresh"] = pd.to_numeric(merged.get("spot"), errors="coerce").notna()
    return merged[merged["btc_physics_fresh"]].sort_values(["entry_dt", "opportunity_key", "side"]).reset_index(drop=True)


def opportunity_candidates(predictions: pd.DataFrame) -> pd.DataFrame:
    base = predictions.drop_duplicates("opportunity_key", keep="first").copy()
    yes = (
        predictions[predictions["side"].astype(str).eq("yes")][["opportunity_key", "ask_cents", "bid_cents"]]
        .drop_duplicates("opportunity_key")
        .rename(columns={"ask_cents": "yes_ask_cents", "bid_cents": "yes_bid_cents"})
    )
    no = (
        predictions[predictions["side"].astype(str).eq("no")][["opportunity_key", "ask_cents", "bid_cents"]]
        .drop_duplicates("opportunity_key")
        .rename(columns={"ask_cents": "no_ask_cents", "bid_cents": "no_bid_cents"})
    )
    out = base.merge(yes, on="opportunity_key", how="left").merge(no, on="opportunity_key", how="left")
    for col in ["yes_ask_cents", "no_ask_cents", "seconds_to_close", f"{MODEL}_p_yes"]:
        out[col] = pd.to_numeric(out[col], errors="coerce")
    out["entry_dt"] = pd.to_datetime(out["entry_dt"], utc=True, errors="coerce")
    out["close_time"] = pd.to_datetime(out["close_time"], utc=True, errors="coerce")
    p_yes = pd.to_numeric(out[f"{MODEL}_p_yes"], errors="coerce").clip(1e-6, 1.0 - 1e-6)
    out["p_yes"] = p_yes
    out["fair_yes_cents"] = 100.0 * p_yes
    out["fair_no_cents"] = 100.0 * (1.0 - p_yes)
    out["yes_edge_cents"] = out["fair_yes_cents"] - out["yes_ask_cents"]
    out["no_edge_cents"] = out["fair_no_cents"] - out["no_ask_cents"]
    yes_better = out["yes_edge_cents"].ge(out["no_edge_cents"])
    out["selected_side"] = np.where(yes_better, "yes", "no")
    out["selected_ask_cents"] = np.where(yes_better, out["yes_ask_cents"], out["no_ask_cents"])
    out["selected_edge_cents"] = np.where(yes_better, out["yes_edge_cents"], out["no_edge_cents"])
    out["selected_p_side"] = np.where(yes_better, p_yes, 1.0 - p_yes)
    eligible = out[
        out["selected_edge_cents"].ge(ENTRY_EDGE_FLOOR_CENTS)
        & out["selected_ask_cents"].ge(ENTRY_ASK_FLOOR_CENTS)
        & out["selected_ask_cents"].le(ENTRY_ASK_CAP_CENTS)
        & out["selected_p_side"].ge(ENTRY_P_SIDE_FLOOR)
        & out["seconds_to_close"].le(ENTRY_MAX_STC)
        & out["seconds_to_close"].ge(ENTRY_MIN_STC)
    ].copy()
    if eligible.empty:
        return eligible
    first = eligible.sort_values(["market", "entry_dt"]).drop_duplicates("market", keep="first").reset_index(drop=True)
    in_hole = first["selected_edge_cents"].gt(EDGE_HOLE_LOW) & first["selected_edge_cents"].le(EDGE_HOLE_HIGH)
    return first[~in_hole].sort_values(["entry_dt", "market"]).reset_index(drop=True)


def load_or_create_lock() -> dict[str, Any]:
    if LOCK_PATH.exists():
        try:
            payload = json.loads(LOCK_PATH.read_text(encoding="utf-8"))
            if isinstance(payload, dict):
                return payload
        except json.JSONDecodeError:
            pass
    lock = {
        "lock_id": "v38_edge_hole_shadow_v1",
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "model_defined_utc": datetime.now(timezone.utc).isoformat(),
        "policy": POLICY,
        "model": MODEL,
        "entry": {
            "edge_floor_cents": ENTRY_EDGE_FLOOR_CENTS,
            "p_side_floor": ENTRY_P_SIDE_FLOOR,
            "ask_floor_cents": ENTRY_ASK_FLOOR_CENTS,
            "ask_cap_cents": ENTRY_ASK_CAP_CENTS,
            "max_seconds_to_close": ENTRY_MAX_STC,
            "min_seconds_to_close": ENTRY_MIN_STC,
            "edge_hole_low": EDGE_HOLE_LOW,
            "edge_hole_high": EDGE_HOLE_HIGH,
        },
        "exit": {"probability_floor": EXIT_PROB_FLOOR},
        "purpose": "Strict-forward shadow validation of v38 edge-hole block candidate.",
    }
    LOCK_PATH.write_text(json.dumps(clean_json(lock), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return lock


def load_registry() -> pd.DataFrame:
    if not REGISTRY_PATH.exists() or REGISTRY_PATH.stat().st_size == 0:
        return pd.DataFrame(columns=REGISTRY_COLUMNS)
    try:
        rows = pd.read_csv(REGISTRY_PATH, low_memory=False)
    except pd.errors.EmptyDataError:
        return pd.DataFrame(columns=REGISTRY_COLUMNS)
    for col in REGISTRY_COLUMNS:
        if col not in rows.columns:
            rows[col] = pd.NA
    for col in ["entry_dt", "close_time", "registered_utc", "exit_dt", "resolved_utc"]:
        rows[col] = pd.to_datetime(rows[col], utc=True, errors="coerce")
    return rows[REGISTRY_COLUMNS]


def new_registry_rows(candidates: pd.DataFrame, lock: dict[str, Any], existing_markets: set[str]) -> pd.DataFrame:
    now = utc_now()
    rows = candidates.copy()
    model_dt = pd.to_datetime(lock.get("model_defined_utc"), utc=True, errors="coerce")
    if not pd.isna(model_dt):
        rows = rows[rows["entry_dt"].gt(model_dt)].copy()
    rows = rows[rows["close_time"].notna() & rows["close_time"].gt(rows["entry_dt"])].copy()
    rows = rows[~rows["market"].astype(str).isin(existing_markets)].copy()
    if rows.empty:
        return pd.DataFrame(columns=REGISTRY_COLUMNS)
    core_cols = [
        "market",
        "opportunity_key",
        "entry_dt",
        "close_time",
        "source_line_no",
        "selected_side",
        "selected_ask_cents",
        "selected_edge_cents",
        "selected_p_side",
        "p_yes",
    ]
    diagnostics = [
        "spot",
        "margin_per_rv_sigma_15m",
        "signed_velocity_dps_1m",
        "signed_velocity_dps_3m",
        "brownian_p_rv_15m",
        "raw_p_yes",
        "book_mid_p_yes",
        "raw_selected_side",
        "raw_selected_edge_cents",
        "latent_hole_active",
        "latent_disagreement_book_switch",
        "recross_hazard_active",
        "recross_side_margin_sigma15",
        "recross_side_velocity_3m",
        "thin_edge_certainty_active",
    ]
    out = rows[core_cols + [col for col in diagnostics if col in rows.columns]].copy()
    out.insert(0, "policy", POLICY)
    out["registered_utc"] = now
    out["exit_dt"] = pd.NaT
    out["exit_bid_cents"] = pd.NA
    out["exit_p_side"] = pd.NA
    out["exit_fee_cents"] = 0.0
    out["outcome"] = ""
    out["resolved_utc"] = pd.NaT
    out["win"] = pd.NA
    out["gross_pnl_cents"] = pd.NA
    out["entry_fee_cents"] = out["selected_ask_cents"].map(estimate_fee_cents)
    out["total_fee_cents"] = pd.NA
    out["fee_net_cents"] = pd.NA
    out["fee_net_1c_entry_cents"] = pd.NA
    out["status"] = np.where(out["close_time"].gt(now), "open", "late_registered")
    for col in REGISTRY_COLUMNS:
        if col not in out.columns:
            out[col] = pd.NA
    return out[REGISTRY_COLUMNS]


def canonical_registry_rows(candidates: pd.DataFrame, lock: dict[str, Any], existing: pd.DataFrame) -> tuple[pd.DataFrame, int]:
    existing_markets = set(existing["market"].astype(str)) if not existing.empty else set()
    rows = new_registry_rows(candidates, lock, set())
    if rows.empty:
        return rows, 0
    new_count = int((~rows["market"].astype(str).isin(existing_markets)).sum())
    if not existing.empty and "registered_utc" in existing.columns:
        registered_lookup = (
            existing[["market", "registered_utc"]]
            .dropna(subset=["market"])
            .drop_duplicates("market", keep="first")
            .assign(market=lambda frame: frame["market"].astype(str))
            .set_index("market")["registered_utc"]
        )
        mapped = rows["market"].astype(str).map(registered_lookup)
        rows.loc[mapped.notna(), "registered_utc"] = mapped[mapped.notna()].to_numpy()
    return rows[REGISTRY_COLUMNS], new_count


def finalize_row(row: pd.Series, gross_pnl_cents: float, exit_fee_cents: float, status: str) -> dict[str, Any]:
    entry_fee = estimate_fee_cents(row["selected_ask_cents"])
    total_fee = entry_fee + float(exit_fee_cents)
    fee_net = float(gross_pnl_cents) - total_fee
    return {
        "gross_pnl_cents": float(gross_pnl_cents),
        "entry_fee_cents": entry_fee,
        "exit_fee_cents": float(exit_fee_cents),
        "total_fee_cents": total_fee,
        "fee_net_cents": fee_net,
        "fee_net_1c_entry_cents": fee_net - QTY,
        "status": status,
    }


def update_exits_and_outcomes(registry: pd.DataFrame, predictions: pd.DataFrame, outcomes: dict[str, dict[str, Any]]) -> pd.DataFrame:
    if registry.empty:
        return registry
    out = registry.copy()
    out["status"] = out["status"].fillna("open").astype(str)
    predictions = predictions.copy()
    predictions["entry_dt"] = pd.to_datetime(predictions["entry_dt"], utc=True, errors="coerce")
    predictions[f"{MODEL}_p_yes"] = pd.to_numeric(predictions[f"{MODEL}_p_yes"], errors="coerce")
    predictions["bid_cents"] = pd.to_numeric(predictions["bid_cents"], errors="coerce")
    resolved_at = utc_now()
    for idx, row in out.iterrows():
        status = str(row.get("status") or "open").lower()
        if status in {"exited", "settled"}:
            continue
        market = str(row["market"])
        selected_side = str(row["selected_side"]).lower()
        entry_dt = pd.Timestamp(row["entry_dt"])
        ask = float(row["selected_ask_cents"])
        future = predictions[
            predictions["market"].astype(str).eq(market)
            & predictions["side"].astype(str).eq(selected_side)
            & predictions["entry_dt"].gt(entry_dt)
            & predictions["bid_cents"].notna()
            & predictions["bid_cents"].ge(1.0)
        ].copy()
        if not future.empty:
            p_yes = future[f"{MODEL}_p_yes"].clip(1e-6, 1.0 - 1e-6)
            future["exit_p_side"] = p_yes if selected_side == "yes" else (1.0 - p_yes)
            trigger = future[future["exit_p_side"].le(EXIT_PROB_FLOOR)].sort_values("entry_dt").head(1)
            if not trigger.empty:
                hit = trigger.iloc[0]
                bid = float(hit["bid_cents"])
                gross = (bid - ask) * QTY
                updates = finalize_row(row, gross, estimate_fee_cents(bid), "exited")
                for key, value in updates.items():
                    out.at[idx, key] = value
                out.at[idx, "exit_dt"] = hit["entry_dt"]
                out.at[idx, "exit_bid_cents"] = bid
                out.at[idx, "exit_p_side"] = float(hit["exit_p_side"])
                continue
        outcome = str(outcomes.get(market, {}).get("outcome") or "").lower()
        if outcome in {"yes", "no"}:
            win = selected_side == outcome
            settlement = 100.0 if win else 0.0
            gross = (settlement - ask) * QTY
            updates = finalize_row(row, gross, 0.0, "settled")
            for key, value in updates.items():
                out.at[idx, key] = value
            out.at[idx, "outcome"] = outcome
            out.at[idx, "resolved_utc"] = resolved_at
            out.at[idx, "win"] = bool(win)
    return out


def denominator(candidates: pd.DataFrame, lock: dict[str, Any], outcomes: dict[str, dict[str, Any]]) -> dict[str, Any]:
    if candidates.empty:
        return {
            "observed_candidate_markets": 0,
            "resolved_candidate_markets": 0,
            "pending_candidate_markets": 0,
        }
    rows = candidates.copy()
    model_dt = pd.to_datetime(lock.get("model_defined_utc"), utc=True, errors="coerce")
    if not pd.isna(model_dt):
        rows = rows[rows["entry_dt"].gt(model_dt)].copy()
    if rows.empty:
        return {
            "observed_candidate_markets": 0,
            "resolved_candidate_markets": 0,
            "pending_candidate_markets": 0,
        }
    markets = rows[["market", "close_time"]].drop_duplicates("market").copy()
    markets["resolved"] = markets["market"].astype(str).map(lambda m: outcomes.get(m, {}).get("outcome") in {"yes", "no"})
    return {
        "observed_candidate_markets": int(markets["market"].nunique()),
        "resolved_candidate_markets": int(markets[markets["resolved"]]["market"].nunique()),
        "pending_candidate_markets": int(markets[~markets["resolved"]]["market"].nunique()),
    }


def write_report(lock: dict[str, Any], registry: pd.DataFrame, denom: dict[str, Any], new_count: int) -> None:
    final = registry[registry["status"].astype(str).str.lower().isin(["exited", "settled"])].copy() if not registry.empty else registry
    open_rows = registry[~registry["status"].astype(str).str.lower().isin(["exited", "settled"])].copy() if not registry.empty else registry
    fee_net = float(pd.to_numeric(final.get("fee_net_cents"), errors="coerce").fillna(0.0).sum()) if not final.empty else 0.0
    gross = float(pd.to_numeric(final.get("gross_pnl_cents"), errors="coerce").fillna(0.0).sum()) if not final.empty else 0.0
    fee_net_1c = float(pd.to_numeric(final.get("fee_net_1c_entry_cents"), errors="coerce").fillna(0.0).sum()) if not final.empty else 0.0
    cost = float(pd.to_numeric(final.get("selected_ask_cents"), errors="coerce").fillna(0.0).sum() * QTY) if not final.empty else 0.0
    exited = int(final["status"].astype(str).str.lower().eq("exited").sum()) if not final.empty else 0
    settled = int(final["status"].astype(str).str.lower().eq("settled").sum()) if not final.empty else 0
    wins = int(final["win"].astype(str).str.lower().eq("true").sum()) if not final.empty else 0
    losses = int(settled - wins)
    lines = [
        "# v38 Edge-Hole Shadow Monitor",
        "",
        f"Generated UTC: `{datetime.now(timezone.utc).isoformat()}`",
        "",
        "## Scope",
        "",
        "- Strict-forward shadow validation of the v38 edge-hole candidate.",
        "- Registers only rows after the lock/model-defined timestamp. Late ingestion is allowed, but pre-lock backfill is not.",
        "- No live bot code/process/orders are touched.",
        "",
        "## Lock",
        "",
        f"- Created UTC: `{lock.get('created_utc')}`",
        f"- Model defined UTC: `{lock.get('model_defined_utc')}`",
        f"- Policy: `{POLICY}`",
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
        f"- Gross P&L: {dollars_from_cents(gross)}",
        f"- Fee-adjusted P&L: {dollars_from_cents(fee_net)}",
        f"- Fee-adjusted with 1c entry haircut: {dollars_from_cents(fee_net_1c)}",
        f"- Fee-adjusted ROI on entry cost: {pct(fee_net / cost if cost > 0 else None)}",
        "",
        "## Read",
        "",
        "- Too few strict-forward finalized rows for a model decision." if len(final) < 30 else "- Review live-forward sample size and stability before any promotion.",
    ]
    REPORT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    markets, outcomes_all = parse_bot_log(BOT_LOG)
    outcomes = closed_market_outcomes_only(markets, outcomes_all)
    frame = raw_rows(markets, outcomes)
    if frame.empty:
        raise SystemExit("No heartbeat rows found.")
    lock = load_or_create_lock()
    predictions = build_predictions(frame)
    candidates = opportunity_candidates(predictions)
    existing_registry = load_registry()
    registry, new_count = canonical_registry_rows(candidates, lock, existing_registry)
    registry = update_exits_and_outcomes(registry, predictions, outcomes)
    registry = registry.sort_values(["entry_dt", "market"]).reset_index(drop=True) if not registry.empty else registry
    registry.to_csv(REGISTRY_PATH, index=False)
    denom = denominator(candidates, lock, outcomes)
    payload = {
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "lock": lock,
        "registered": int(len(registry)),
        "new_rows": int(new_count),
        "denominator": denom,
    }
    REPORT_JSON.write_text(json.dumps(clean_json(payload), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_report(lock, registry, denom, int(new_count))
    print("v38 edge-hole shadow monitor complete")
    print(f"registered={len(registry)} new_rows={new_count} report={REPORT_MD}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
