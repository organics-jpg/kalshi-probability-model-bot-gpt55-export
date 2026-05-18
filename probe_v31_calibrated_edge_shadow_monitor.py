"""Strict forward shadow monitor for calibrated book/FV edge capacity.

This monitor registers a research-only candidate:

    book_v31_platt_first_edge2

It walks live heartbeat rows causally and registers at most one hypothetical
trade per market: the first row where calibrated fair value has at least 2c
gross edge over the YES/NO ask. Rows are registered only while the market close
is still in the future. Later runs join resolved outcomes.

No orders are submitted and no live bot files/processes are touched.
"""
from __future__ import annotations

import json
import math
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from probe_fv_avg90_strict_probability_monitor import BOOK_V31_PLATT_COEF, clean_json, logit_series, sigmoid_series
from probe_live_heartbeat_two_side_fv import heartbeat_two_side_rows, group_candidates
from probe_live_v28_fv_accuracy_volume import BOT_LOG, OUT_DIR, parse_bot_log
from probe_mushroom_v29_fv_surface import EngineSpec, load_candles, replay_predictions
from btc_mushroom_forecaster_v31_fast import FastMushroomFVEngineV31, FastMushroomV31Config
from shadow_live_v28_physics_validator import closed_market_outcomes_only


MODE = "two_side_all_heartbeats"
POLICY = "book_v31_platt_first_edge2"
MIN_EDGE_CENTS = 2.0
CALIBRATION_JSON = OUT_DIR / "v31_book_calibrated_probability_latest.json"
LOCK_PATH = OUT_DIR / "v31_calibrated_edge_shadow_lock.json"
REGISTRY_PATH = OUT_DIR / "v31_calibrated_edge_shadow_registry_latest.csv"
REPORT_MD = OUT_DIR / "v31_calibrated_edge_shadow_monitor_latest.md"
REPORT_JSON = OUT_DIR / "v31_calibrated_edge_shadow_monitor_latest.json"
REGISTRY_COLUMNS = [
    "policy",
    "opportunity_key",
    "market",
    "entry_dt",
    "close_time",
    "source_line_no",
    "selected_side",
    "selected_ask_cents",
    "selected_edge_cents",
    "book_v31_platt_p_yes",
    "v31_p_yes",
    "book_mid_probability_p_yes",
    "registered_utc",
    "outcome",
    "resolved_utc",
    "win",
    "gross_net_cents",
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


def model_defined_utc() -> str:
    if CALIBRATION_JSON.exists():
        try:
            payload = json.loads(CALIBRATION_JSON.read_text(encoding="utf-8"))
            value = payload.get("generated_utc")
            if value:
                return str(value)
        except json.JSONDecodeError:
            pass
    return datetime.now(timezone.utc).isoformat()


def load_or_create_lock() -> dict[str, Any]:
    if LOCK_PATH.exists():
        try:
            payload = json.loads(LOCK_PATH.read_text(encoding="utf-8"))
            if isinstance(payload, dict):
                return payload
        except json.JSONDecodeError:
            pass
    lock = {
        "lock_id": "v31_calibrated_edge_shadow_v1",
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "model_defined_utc": model_defined_utc(),
        "mode": MODE,
        "policy": POLICY,
        "min_edge_cents": MIN_EDGE_CENTS,
        "coefficients": {
            "book_v31_platt": list(BOOK_V31_PLATT_COEF),
        },
        "purpose": "Strict forward shadow validation of calibrated v31/book FV edge capacity.",
    }
    LOCK_PATH.write_text(json.dumps(clean_json(lock), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return lock


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
            "v31_avg90_final60_exact",
            FastMushroomFVEngineV31(
                FastMushroomV31Config(settlement_average_seconds=90.0, exact_average_inside_seconds=60.0)
            ),
            "v31 proxy-aware final-minute exact settlement-average variance",
        ),
    ]
    return replay_predictions(frame, load_candles(), engines)


def opportunity_candidates(predictions: pd.DataFrame) -> pd.DataFrame:
    base = predictions.drop_duplicates("opportunity_key", keep="first").copy()
    yes = (
        predictions[predictions["side"].astype(str).eq("yes")][["opportunity_key", "ask_cents", "book_mid_cents"]]
        .drop_duplicates("opportunity_key")
        .rename(columns={"ask_cents": "yes_ask_cents", "book_mid_cents": "yes_mid_cents"})
    )
    no = (
        predictions[predictions["side"].astype(str).eq("no")][["opportunity_key", "ask_cents", "book_mid_cents"]]
        .drop_duplicates("opportunity_key")
        .rename(columns={"ask_cents": "no_ask_cents", "book_mid_cents": "no_mid_cents"})
    )
    out = base.merge(yes, on="opportunity_key", how="left").merge(no, on="opportunity_key", how="left")
    for col in ["yes_ask_cents", "no_ask_cents", "yes_mid_cents", "no_mid_cents", "v31_avg90_final60_exact_p_yes"]:
        out[col] = pd.to_numeric(out[col], errors="coerce")
    denom = out["yes_mid_cents"] + out["no_mid_cents"]
    out["book_mid_probability_p_yes"] = out["yes_mid_cents"] / denom
    book_logit = logit_series(out["book_mid_probability_p_yes"])
    v31_logit = logit_series(out["v31_avg90_final60_exact_p_yes"])
    out["book_v31_platt_p_yes"] = sigmoid_series(
        BOOK_V31_PLATT_COEF[0] + BOOK_V31_PLATT_COEF[1] * book_logit + BOOK_V31_PLATT_COEF[2] * v31_logit
    )
    p_yes = pd.to_numeric(out["book_v31_platt_p_yes"], errors="coerce").clip(1e-6, 1.0 - 1e-6)
    out["fair_yes_cents"] = 100.0 * p_yes
    out["fair_no_cents"] = 100.0 * (1.0 - p_yes)
    out["yes_edge_cents"] = out["fair_yes_cents"] - out["yes_ask_cents"]
    out["no_edge_cents"] = out["fair_no_cents"] - out["no_ask_cents"]
    yes_better = out["yes_edge_cents"].ge(out["no_edge_cents"])
    out["selected_side"] = np.where(yes_better, "yes", "no")
    out["selected_ask_cents"] = np.where(yes_better, out["yes_ask_cents"], out["no_ask_cents"])
    out["selected_edge_cents"] = np.where(yes_better, out["yes_edge_cents"], out["no_edge_cents"])
    out["v31_p_yes"] = out["v31_avg90_final60_exact_p_yes"]
    return out.sort_values(["entry_dt", "opportunity_key"]).reset_index(drop=True)


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
    for col in ["entry_dt", "close_time", "registered_utc", "resolved_utc"]:
        rows[col] = pd.to_datetime(rows[col], utc=True, errors="coerce")
    rows["outcome"] = rows["outcome"].fillna("").astype(str)
    return rows[REGISTRY_COLUMNS]


def new_registry_rows(candidates: pd.DataFrame, lock: dict[str, Any], existing_markets: set[str]) -> pd.DataFrame:
    now = utc_now()
    rows = candidates.copy()
    rows["entry_dt"] = pd.to_datetime(rows["entry_dt"], utc=True, errors="coerce")
    rows["close_time"] = pd.to_datetime(rows["close_time"], utc=True, errors="coerce")
    model_dt = pd.to_datetime(lock.get("model_defined_utc"), utc=True, errors="coerce")
    if not pd.isna(model_dt):
        rows = rows[rows["entry_dt"].gt(model_dt)].copy()
    rows = rows[
        rows["close_time"].notna()
        & rows["close_time"].gt(now)
        & rows["selected_edge_cents"].ge(MIN_EDGE_CENTS)
    ].copy()
    if rows.empty:
        return pd.DataFrame(columns=REGISTRY_COLUMNS)
    rows = rows[~rows["market"].astype(str).isin(existing_markets)].copy()
    if rows.empty:
        return pd.DataFrame(columns=REGISTRY_COLUMNS)
    first = rows.sort_values(["entry_dt", "opportunity_key"]).groupby("market", as_index=False, sort=False).first()
    out = first[
        [
            "opportunity_key",
            "market",
            "entry_dt",
            "close_time",
            "source_line_no",
            "selected_side",
            "selected_ask_cents",
            "selected_edge_cents",
            "book_v31_platt_p_yes",
            "v31_p_yes",
            "book_mid_probability_p_yes",
        ]
    ].copy()
    out.insert(0, "policy", POLICY)
    out["registered_utc"] = now
    out["outcome"] = ""
    out["resolved_utc"] = pd.NaT
    out["win"] = pd.NA
    out["gross_net_cents"] = pd.NA
    return out[REGISTRY_COLUMNS]


def update_outcomes(registry: pd.DataFrame, outcomes: dict[str, dict[str, Any]]) -> pd.DataFrame:
    if registry.empty:
        return registry
    out = registry.copy()
    out["outcome"] = out["outcome"].fillna("").astype(str)
    out["resolved_utc"] = pd.to_datetime(out["resolved_utc"], utc=True, errors="coerce")
    out["win"] = out["win"].astype(object)
    out["gross_net_cents"] = pd.to_numeric(out["gross_net_cents"], errors="coerce")
    resolved_at = utc_now()
    for idx, row in out.iterrows():
        if str(row.get("outcome") or "").lower() in {"yes", "no"}:
            continue
        outcome = str(outcomes.get(str(row["market"]), {}).get("outcome") or "").lower()
        if outcome not in {"yes", "no"}:
            continue
        selected_side = str(row["selected_side"]).lower()
        ask = float(row["selected_ask_cents"])
        win = selected_side == outcome
        out.at[idx, "outcome"] = outcome
        out.at[idx, "resolved_utc"] = resolved_at
        out.at[idx, "win"] = bool(win)
        out.at[idx, "gross_net_cents"] = (100.0 - ask) if win else -ask
    return out


def observed_denominator(candidates: pd.DataFrame, lock: dict[str, Any], outcomes: dict[str, dict[str, Any]]) -> dict[str, Any]:
    rows = candidates.copy()
    rows["entry_dt"] = pd.to_datetime(rows["entry_dt"], utc=True, errors="coerce")
    model_dt = pd.to_datetime(lock.get("model_defined_utc"), utc=True, errors="coerce")
    if not pd.isna(model_dt):
        rows = rows[rows["entry_dt"].gt(model_dt)].copy()
    markets = rows[["market", "close_time"]].drop_duplicates("market").copy()
    markets["resolved"] = markets["market"].astype(str).map(lambda m: outcomes.get(m, {}).get("outcome") in {"yes", "no"})
    return {
        "observed_markets": int(markets["market"].nunique()),
        "resolved_observed_markets": int(markets[markets["resolved"]]["market"].nunique()),
        "pending_observed_markets": int(markets[~markets["resolved"]]["market"].nunique()),
    }


def write_report(lock: dict[str, Any], registry: pd.DataFrame, denom: dict[str, Any], new_count: int) -> None:
    resolved = registry[registry["outcome"].astype(str).str.lower().isin(["yes", "no"])].copy() if not registry.empty else registry
    pending = len(registry) - len(resolved)
    wins = int(resolved["win"].astype(str).str.lower().eq("true").sum()) if not resolved.empty else 0
    losses = int(len(resolved) - wins)
    net = float(pd.to_numeric(resolved.get("gross_net_cents"), errors="coerce").sum()) if not resolved.empty else 0.0
    cost = float(pd.to_numeric(resolved.get("selected_ask_cents"), errors="coerce").sum()) if not resolved.empty else 0.0
    resolved_observed = int(denom.get("resolved_observed_markets") or 0)
    coverage = len(resolved) / resolved_observed if resolved_observed else None
    lines = [
        "# Calibrated Edge Shadow Monitor",
        "",
        f"Generated UTC: `{datetime.now(timezone.utc).isoformat()}`",
        "",
        "## Scope",
        "",
        "- Strict forward shadow validation of calibrated FV edge capacity.",
        "- Registers first qualifying edge row per market only while close is in the future.",
        "- No live bot code/process or orders are touched.",
        "",
        "## Lock",
        "",
        f"- Created UTC: `{lock.get('created_utc')}`",
        f"- Model defined UTC: `{lock.get('model_defined_utc')}`",
        f"- Policy: `{POLICY}`",
        f"- Min gross edge: `{MIN_EDGE_CENTS}` cents",
        "",
        "## Registry",
        "",
        f"- Registered selections: {len(registry)}",
        f"- New selections this run: {new_count}",
        f"- Resolved / pending selections: {len(resolved)} / {pending}",
        f"- Observed markets after model definition: {denom.get('observed_markets')}",
        f"- Resolved / pending observed markets: {denom.get('resolved_observed_markets')} / {denom.get('pending_observed_markets')}",
        f"- Resolved market coverage: {pct(coverage)}",
        "",
        "## Resolved Performance",
        "",
        f"- W/L: {wins}/{losses}",
        f"- Gross net: {net:.1f}c",
        f"- ROI on selected asks: {pct(net / cost if cost > 0 else None)}",
        "",
        "## Read",
        "",
        "- Too few strict-forward resolved selections for a model decision." if len(resolved) < 30 else "- Review sample size and split stability before any promotion.",
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

    registry = load_registry()
    existing_markets = set(registry["market"].astype(str)) if not registry.empty else set()
    new_rows = new_registry_rows(candidates, lock, existing_markets)
    if not new_rows.empty:
        if registry.empty:
            registry = new_rows.copy()
        else:
            concat_cols = [
                col
                for col in REGISTRY_COLUMNS
                if not (registry[col].isna().all() and new_rows[col].isna().all())
            ]
            registry = pd.concat(
                [registry[concat_cols].astype(object), new_rows[concat_cols].astype(object)],
                ignore_index=True,
                sort=False,
            ).reindex(columns=REGISTRY_COLUMNS)
    registry = update_outcomes(registry, outcomes)
    registry = registry.sort_values(["entry_dt", "market"]).reset_index(drop=True) if not registry.empty else registry
    registry.to_csv(REGISTRY_PATH, index=False)

    denom = observed_denominator(candidates, lock, outcomes)
    payload = {
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "lock": lock,
        "policy": POLICY,
        "registered": int(len(registry)),
        "new_rows": int(len(new_rows)),
        "denominator": denom,
    }
    REPORT_JSON.write_text(json.dumps(clean_json(payload), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_report(lock, registry, denom, int(len(new_rows)))
    print("calibrated edge shadow monitor complete")
    print(f"registered={len(registry)} new_rows={len(new_rows)} report={REPORT_MD}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
