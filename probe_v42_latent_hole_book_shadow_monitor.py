"""Strict-forward shadow monitor for the v42 latent-hole book FV candidate.

Candidate:
- raw v38 FV surface until a latent edge-hole state is observed;
- latent state is triggered by the first post-lock raw-v38 qualifying signal
  with edge >= -2c, p_side >= 0.65, 60-600s to close, and edge in (8c,20c];
- after that trigger, the market's FV probability is shrunk to the two-sided
  book midpoint probability, treating the book as a hidden-state measurement;
- entry uses adjusted FV: edge >= 0c, p_side >= 0.64, ask 1-100c, 0-600s;
- exit when adjusted p_side <= 0.52.

Research-only. No live bot files, processes, or order paths are touched.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

import probe_v38_edge_hole_shadow_monitor as shadow
from probe_v31_book_calibrated_probability import logit, sigmoid
from probe_live_v28_fv_accuracy_volume import BOT_LOG, OUT_DIR, parse_bot_log
from probe_market_interval_80coverage import clean_json
from shadow_live_v28_physics_validator import closed_market_outcomes_only


POLICY = "v42_latent_hole_book_edge0_p64_stc0_600_prob52"
REPORT_PREFIX = "v42_latent_hole_book_shadow"

LATENT_EDGE_FLOOR = -2.0
LATENT_P_SIDE_FLOOR = 0.65
LATENT_MIN_STC = 60.0
LATENT_MAX_STC = 600.0
LATENT_HOLE_LOW = 8.0
LATENT_HOLE_HIGH = 20.0
LATENT_POSTERIOR_MODE = "book"
LATENT_BOOK_WEIGHT = 1.0

OUT_DIR = Path(__file__).resolve().parent / "logs" / "edge_research"
shadow.POLICY = POLICY
shadow.ENTRY_EDGE_FLOOR_CENTS = 0.0
shadow.ENTRY_P_SIDE_FLOOR = 0.64
shadow.ENTRY_ASK_FLOOR_CENTS = 1.0
shadow.ENTRY_ASK_CAP_CENTS = 100.0
shadow.ENTRY_MIN_STC = 0.0
shadow.ENTRY_MAX_STC = 600.0
shadow.EDGE_HOLE_LOW = -999.0
shadow.EDGE_HOLE_HIGH = -998.0
shadow.EXIT_PROB_FLOOR = 0.52
shadow.LOCK_PATH = OUT_DIR / f"{REPORT_PREFIX}_lock.json"
shadow.REGISTRY_PATH = OUT_DIR / f"{REPORT_PREFIX}_registry_latest.csv"
shadow.REPORT_MD = OUT_DIR / f"{REPORT_PREFIX}_monitor_latest.md"
shadow.REPORT_JSON = OUT_DIR / f"{REPORT_PREFIX}_monitor_latest.json"


def book_mid_probability(opps: pd.DataFrame) -> pd.Series:
    denom = opps["yes_book_mid_cents"] + opps["no_book_mid_cents"]
    return (opps["yes_book_mid_cents"] / denom).clip(1e-6, 1.0 - 1e-6)


def latent_posterior(raw_p_yes: pd.Series, book_p_yes: pd.Series) -> pd.Series:
    raw = pd.to_numeric(raw_p_yes, errors="coerce").clip(1e-6, 1.0 - 1e-6)
    book = pd.to_numeric(book_p_yes, errors="coerce").fillna(raw).clip(1e-6, 1.0 - 1e-6)
    if LATENT_POSTERIOR_MODE == "book":
        return book
    if LATENT_POSTERIOR_MODE == "book_blend":
        return pd.Series(
            sigmoid((1.0 - LATENT_BOOK_WEIGHT) * logit(raw) + LATENT_BOOK_WEIGHT * logit(book)),
            index=raw.index,
        ).clip(1e-6, 1.0 - 1e-6)
    if LATENT_POSTERIOR_MODE == "flat":
        return pd.Series(0.5, index=raw.index)
    raise ValueError(f"Unknown LATENT_POSTERIOR_MODE: {LATENT_POSTERIOR_MODE}")


def opportunity_table(predictions: pd.DataFrame, lock: dict[str, Any]) -> pd.DataFrame:
    base = predictions.drop_duplicates("opportunity_key", keep="first").copy()
    yes = (
        predictions[predictions["side"].astype(str).eq("yes")][
            ["opportunity_key", "ask_cents", "bid_cents", "book_mid_cents"]
        ]
        .drop_duplicates("opportunity_key")
        .rename(
            columns={
                "ask_cents": "yes_ask_cents",
                "bid_cents": "yes_bid_cents",
                "book_mid_cents": "yes_book_mid_cents",
            }
        )
    )
    no = (
        predictions[predictions["side"].astype(str).eq("no")][
            ["opportunity_key", "ask_cents", "bid_cents", "book_mid_cents"]
        ]
        .drop_duplicates("opportunity_key")
        .rename(
            columns={
                "ask_cents": "no_ask_cents",
                "bid_cents": "no_bid_cents",
                "book_mid_cents": "no_book_mid_cents",
            }
        )
    )
    out = base.merge(yes, on="opportunity_key", how="left").merge(no, on="opportunity_key", how="left")
    for col in [
        "yes_ask_cents",
        "no_ask_cents",
        "yes_book_mid_cents",
        "no_book_mid_cents",
        "seconds_to_close",
        f"{shadow.MODEL}_p_yes",
    ]:
        out[col] = pd.to_numeric(out[col], errors="coerce")
    out["entry_dt"] = pd.to_datetime(out["entry_dt"], utc=True, errors="coerce")
    out["close_time"] = pd.to_datetime(out["close_time"], utc=True, errors="coerce")
    raw_p_yes = pd.to_numeric(out[f"{shadow.MODEL}_p_yes"], errors="coerce").clip(1e-6, 1.0 - 1e-6)
    out["raw_p_yes"] = raw_p_yes
    out["book_mid_p_yes"] = book_mid_probability(out).fillna(raw_p_yes)
    out["raw_yes_edge_cents"] = 100.0 * raw_p_yes - out["yes_ask_cents"]
    out["raw_no_edge_cents"] = 100.0 * (1.0 - raw_p_yes) - out["no_ask_cents"]
    yes_better_raw = out["raw_yes_edge_cents"].ge(out["raw_no_edge_cents"])
    out["raw_selected_side"] = np.where(yes_better_raw, "yes", "no")
    out["raw_selected_ask_cents"] = np.where(yes_better_raw, out["yes_ask_cents"], out["no_ask_cents"])
    out["raw_selected_edge_cents"] = np.where(yes_better_raw, out["raw_yes_edge_cents"], out["raw_no_edge_cents"])
    out["raw_selected_p_side"] = np.where(yes_better_raw, raw_p_yes, 1.0 - raw_p_yes)

    model_dt = pd.to_datetime(lock.get("model_defined_utc"), utc=True, errors="coerce")
    latent_universe = out.copy()
    if not pd.isna(model_dt):
        latent_universe = latent_universe[latent_universe["entry_dt"].gt(model_dt)].copy()
    latent_ok = latent_universe[
        latent_universe["raw_selected_edge_cents"].ge(LATENT_EDGE_FLOOR)
        & latent_universe["raw_selected_ask_cents"].ge(shadow.ENTRY_ASK_FLOOR_CENTS)
        & latent_universe["raw_selected_ask_cents"].le(shadow.ENTRY_ASK_CAP_CENTS)
        & latent_universe["raw_selected_p_side"].ge(LATENT_P_SIDE_FLOOR)
        & latent_universe["seconds_to_close"].ge(LATENT_MIN_STC)
        & latent_universe["seconds_to_close"].le(LATENT_MAX_STC)
    ].copy()
    first = latent_ok.sort_values(["market", "entry_dt"]).drop_duplicates("market", keep="first")
    first_holes = first[first["raw_selected_edge_cents"].gt(LATENT_HOLE_LOW) & first["raw_selected_edge_cents"].le(LATENT_HOLE_HIGH)]
    hole_times = {str(row.market): pd.Timestamp(row.entry_dt) for row in first_holes.itertuples(index=False)}

    out["p_yes"] = raw_p_yes
    out["latent_hole_active"] = False
    for market, first_dt in hole_times.items():
        mask = out["market"].astype(str).eq(market) & out["entry_dt"].ge(first_dt)
        out.loc[mask, "p_yes"] = latent_posterior(out.loc[mask, "raw_p_yes"], out.loc[mask, "book_mid_p_yes"])
        out.loc[mask, "latent_hole_active"] = True

    p_yes = out["p_yes"].clip(1e-6, 1.0 - 1e-6)
    out["fair_yes_cents"] = 100.0 * p_yes
    out["fair_no_cents"] = 100.0 * (1.0 - p_yes)
    out["yes_edge_cents"] = out["fair_yes_cents"] - out["yes_ask_cents"]
    out["no_edge_cents"] = out["fair_no_cents"] - out["no_ask_cents"]
    yes_better = out["yes_edge_cents"].ge(out["no_edge_cents"])
    out["selected_side"] = np.where(yes_better, "yes", "no")
    out["selected_ask_cents"] = np.where(yes_better, out["yes_ask_cents"], out["no_ask_cents"])
    out["selected_edge_cents"] = np.where(yes_better, out["yes_edge_cents"], out["no_edge_cents"])
    out["selected_p_side"] = np.where(yes_better, p_yes, 1.0 - p_yes)
    out["latent_hole_markets"] = len(hole_times)
    return out


def opportunity_candidates(predictions: pd.DataFrame, lock: dict[str, Any]) -> pd.DataFrame:
    out = opportunity_table(predictions, lock)
    model_dt = pd.to_datetime(lock.get("model_defined_utc"), utc=True, errors="coerce")
    if not pd.isna(model_dt):
        out = out[out["entry_dt"].gt(model_dt)].copy()
    eligible = out[
        out["selected_edge_cents"].ge(shadow.ENTRY_EDGE_FLOOR_CENTS)
        & out["selected_ask_cents"].ge(shadow.ENTRY_ASK_FLOOR_CENTS)
        & out["selected_ask_cents"].le(shadow.ENTRY_ASK_CAP_CENTS)
        & out["selected_p_side"].ge(shadow.ENTRY_P_SIDE_FLOOR)
        & out["seconds_to_close"].le(shadow.ENTRY_MAX_STC)
        & out["seconds_to_close"].ge(shadow.ENTRY_MIN_STC)
    ].copy()
    if eligible.empty:
        return eligible
    return eligible.sort_values(["market", "entry_dt"]).drop_duplicates("market", keep="first").sort_values(
        ["entry_dt", "market"]
    ).reset_index(drop=True)


def adjusted_prediction_rows(predictions: pd.DataFrame, lock: dict[str, Any]) -> pd.DataFrame:
    opps = opportunity_table(predictions, lock)[["opportunity_key", "p_yes", "latent_hole_active"]]
    out = predictions.merge(opps, on="opportunity_key", how="left")
    out["p_yes"] = pd.to_numeric(out["p_yes"], errors="coerce").fillna(
        pd.to_numeric(out[f"{shadow.MODEL}_p_yes"], errors="coerce")
    ).clip(1e-6, 1.0 - 1e-6)
    out["entry_dt"] = pd.to_datetime(out["entry_dt"], utc=True, errors="coerce")
    out["bid_cents"] = pd.to_numeric(out["bid_cents"], errors="coerce")
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
        min_hold_seconds = float(getattr(shadow, "EXIT_MIN_HOLD_SECONDS", 0.0) or 0.0)
        min_exit_dt = entry_dt + pd.Timedelta(seconds=min_hold_seconds)
        if min_hold_seconds > 0.0:
            time_mask = adjusted["entry_dt"].ge(min_exit_dt)
        else:
            time_mask = adjusted["entry_dt"].gt(entry_dt)
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
            trigger = future[future["exit_p_side"].le(shadow.EXIT_PROB_FLOOR)].sort_values("entry_dt").head(1)
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


def load_or_create_lock() -> dict[str, Any]:
    if shadow.LOCK_PATH.exists():
        try:
            payload = json.loads(shadow.LOCK_PATH.read_text(encoding="utf-8"))
            if isinstance(payload, dict):
                return payload
        except json.JSONDecodeError:
            pass
    now = datetime.now(timezone.utc).isoformat()
    lock = {
        "lock_id": "v42_latent_hole_book_shadow_v1",
        "created_utc": now,
        "model_defined_utc": now,
        "policy": POLICY,
        "base_model": shadow.MODEL,
        "latent_state": {
            "edge_floor_cents": LATENT_EDGE_FLOOR,
            "p_side_floor": LATENT_P_SIDE_FLOOR,
            "min_seconds_to_close": LATENT_MIN_STC,
            "max_seconds_to_close": LATENT_MAX_STC,
            "edge_hole_low": LATENT_HOLE_LOW,
            "edge_hole_high": LATENT_HOLE_HIGH,
            "posterior": LATENT_POSTERIOR_MODE,
            "book_weight": LATENT_BOOK_WEIGHT,
        },
        "entry": {
            "edge_floor_cents": shadow.ENTRY_EDGE_FLOOR_CENTS,
            "p_side_floor": shadow.ENTRY_P_SIDE_FLOOR,
            "ask_floor_cents": shadow.ENTRY_ASK_FLOOR_CENTS,
            "ask_cap_cents": shadow.ENTRY_ASK_CAP_CENTS,
            "min_seconds_to_close": shadow.ENTRY_MIN_STC,
            "max_seconds_to_close": shadow.ENTRY_MAX_STC,
        },
        "exit": {
            "probability_floor": shadow.EXIT_PROB_FLOOR,
            "min_hold_seconds": float(getattr(shadow, "EXIT_MIN_HOLD_SECONDS", 0.0) or 0.0),
        },
        "purpose": "Strict-forward shadow validation of v42 latent edge-hole FV candidate.",
    }
    shadow.LOCK_PATH.write_text(json.dumps(clean_json(lock), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return lock


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    markets, outcomes_all = parse_bot_log(BOT_LOG)
    outcomes = closed_market_outcomes_only(markets, outcomes_all)
    frame = shadow.raw_rows(markets, outcomes)
    if frame.empty:
        raise SystemExit("No heartbeat rows found.")
    lock = load_or_create_lock()
    predictions = shadow.build_predictions(frame)
    candidates = opportunity_candidates(predictions, lock)
    existing_registry = shadow.load_registry()
    registry, new_count = shadow.canonical_registry_rows(candidates, lock, existing_registry)
    registry = update_exits_and_outcomes(registry, predictions, outcomes, lock)
    registry = registry.sort_values(["entry_dt", "market"]).reset_index(drop=True) if not registry.empty else registry
    registry.to_csv(shadow.REGISTRY_PATH, index=False)
    denom = shadow.denominator(candidates, lock, outcomes)
    payload = {
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "lock": lock,
        "registered": int(len(registry)),
        "new_rows": int(new_count),
        "denominator": denom,
        "latent_hole_markets_in_log": int(opportunity_table(predictions, lock).get("latent_hole_markets", pd.Series([0])).max() or 0),
    }
    shadow.REPORT_JSON.write_text(json.dumps(clean_json(payload), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    shadow.write_report(lock, registry, denom, int(new_count))
    print("v42 latent-hole book shadow monitor complete")
    print(f"registered={len(registry)} new_rows={new_count} report={shadow.REPORT_MD}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
