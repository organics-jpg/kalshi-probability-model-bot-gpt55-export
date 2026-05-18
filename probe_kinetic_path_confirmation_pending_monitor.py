"""Pre-resolution registry for the kinetic path-confirmation lock.

This monitor records delayed same-side confirmation signals before outcome is
known. It is separate from the main profit-lock registry because the
confirmation rule was discovered later and has its own lock boundary.

Research-only: no orders are submitted and no bot files or live processes are
modified.
"""
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

import numpy as np
import pandas as pd

from probe_cross_dataset_profit_frontier import estimated_order_fee_cents, fmt_cents
from probe_kinetic_path_confirmation import select_confirmed
from probe_kinetic_path_confirmation_fresh_validation import PATH_CONFIRM_LOCK_PATH, ensure_lock, spec_from_lock
from probe_market_interval_80coverage import OUT_DIR, clean_json, market_base, pct
from probe_profit_lock_pending_signal_monitor import raw_side_rows
from probe_profit_lock_time_boundary import effective_lock_dt
from probe_profit_touch_hazard_fresh_validation import policy_from_record
from probe_profit_touch_hazard_frontier import add_touch_hazard_scores
from probe_live_v28_fv_accuracy_volume import BOT_LOG, parse_bot_log
from shadow_live_v28_physics_validator import closed_market_outcomes_only


REGISTRY_PATH = OUT_DIR / "kinetic_path_confirmation_pending_registry_latest.csv"
REPORT_LATEST = OUT_DIR / "kinetic_path_confirmation_pending_monitor_latest.md"
JSON_LATEST = OUT_DIR / "kinetic_path_confirmation_pending_monitor_latest.json"


SIGNAL_COLS = [
    "lock_name",
    "market",
    "registered_utc",
    "lock_close_dt",
    "initial_entry_dt",
    "entry_dt",
    "close_dt",
    "confirm_delay_sec",
    "side",
    "initial_ask_cents",
    "ask_cents",
    "bid_cents",
    "seconds_to_close",
    "source_line_no",
    "decision_key",
    "chooser",
    "score_value",
    "confirmation",
    "book_p_side",
    "brownian_p_rv_15m",
    "adverse_move_15m",
    "touch_loss_rv_15m",
    "kinetic_touch_score_15",
    "outcome_available",
    "outcome",
    "win",
    "entry_fee_cents",
    "net_pnl_cents",
]


def clean_json_local(value: Any) -> Any:
    if isinstance(value, pd.Timestamp):
        return value.isoformat()
    if isinstance(value, dict):
        return {str(k): clean_json_local(v) for k, v in value.items()}
    if isinstance(value, list):
        return [clean_json_local(v) for v in value]
    return clean_json(value)


def bool_value(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    return str(value).lower() in {"true", "1", "yes"}


def load_registry() -> pd.DataFrame:
    if not REGISTRY_PATH.exists():
        return pd.DataFrame(columns=SIGNAL_COLS)
    df = pd.read_csv(REGISTRY_PATH)
    for col in SIGNAL_COLS:
        if col not in df.columns:
            df[col] = np.nan
    return df[SIGNAL_COLS].copy()


def filter_registry_to_lock(registry: pd.DataFrame, boundary: pd.Timestamp) -> pd.DataFrame:
    if registry.empty or pd.isna(boundary):
        return registry
    out = registry.copy()
    out["entry_dt_tmp"] = pd.to_datetime(out["entry_dt"], utc=True, errors="coerce")
    out = out[out["entry_dt_tmp"].gt(boundary)].drop(columns=["entry_dt_tmp"])
    return out.reindex(columns=SIGNAL_COLS)


def filter_registry_to_pre_resolution(registry: pd.DataFrame) -> tuple[pd.DataFrame, int]:
    if registry.empty:
        return registry, 0
    out = registry.copy()
    registered_dt = pd.to_datetime(out["registered_utc"], utc=True, errors="coerce")
    close_dt = pd.to_datetime(out["close_dt"], utc=True, errors="coerce")
    keep = registered_dt.notna() & close_dt.notna() & registered_dt.lt(close_dt)
    removed = int((~keep).sum())
    return out.loc[keep].reindex(columns=SIGNAL_COLS), removed


def signal_record(row: pd.Series, lock: Dict[str, Any], registered_utc: str) -> Dict[str, Any]:
    outcome_available = bool_value(row.get("outcome_available"))
    outcome = row.get("outcome")
    side = str(row.get("side"))
    ask = float(row.get("ask_cents"))
    fee = estimated_order_fee_cents(ask, 1)
    win = bool(side == outcome) if outcome_available and outcome in {"yes", "no"} else None
    net = (100.0 - ask - fee) if win is True else (-ask - fee) if win is False else None
    return {
        "lock_name": "kinetic_path_confirm",
        "market": row.get("market"),
        "registered_utc": registered_utc,
        "lock_close_dt": effective_lock_dt(lock).isoformat(),
        "initial_entry_dt": pd.to_datetime(row.get("initial_entry_dt"), utc=True, errors="coerce").isoformat(),
        "entry_dt": pd.to_datetime(row.get("entry_dt"), utc=True, errors="coerce").isoformat(),
        "close_dt": pd.to_datetime(row.get("close_dt"), utc=True, errors="coerce").isoformat(),
        "confirm_delay_sec": row.get("confirm_delay_sec"),
        "side": side,
        "initial_ask_cents": row.get("initial_ask_cents"),
        "ask_cents": ask,
        "bid_cents": row.get("bid_cents"),
        "seconds_to_close": row.get("seconds_to_close"),
        "source_line_no": row.get("source_line_no"),
        "decision_key": row.get("decision_key"),
        "chooser": lock["policy"]["chooser"],
        "score_value": row.get(lock["policy"]["chooser"]),
        "confirmation": lock["confirmation"]["label"],
        "book_p_side": row.get("book_p_side"),
        "brownian_p_rv_15m": row.get("brownian_p_rv_15m"),
        "adverse_move_15m": row.get("adverse_move_15m"),
        "touch_loss_rv_15m": row.get("touch_loss_rv_15m"),
        "kinetic_touch_score_15": row.get("kinetic_touch_score_15"),
        "outcome_available": outcome_available,
        "outcome": outcome if outcome_available else "",
        "win": win,
        "entry_fee_cents": fee,
        "net_pnl_cents": net,
    }


def update_outcomes(registry: pd.DataFrame, outcomes: Dict[str, Dict[str, Any]]) -> pd.DataFrame:
    if registry.empty:
        return registry
    out = registry.copy()
    for idx, row in out.iterrows():
        outcome = outcomes.get(str(row["market"]), {}).get("outcome")
        if outcome not in {"yes", "no"}:
            out.at[idx, "outcome_available"] = False
            out.at[idx, "outcome"] = ""
            out.at[idx, "win"] = ""
            out.at[idx, "net_pnl_cents"] = np.nan
            continue
        side = str(row["side"])
        ask = float(row["ask_cents"])
        fee = int(float(row["entry_fee_cents"])) if not pd.isna(row.get("entry_fee_cents")) else estimated_order_fee_cents(ask, 1)
        win = side == outcome
        out.at[idx, "outcome_available"] = True
        out.at[idx, "outcome"] = outcome
        out.at[idx, "win"] = win
        out.at[idx, "entry_fee_cents"] = fee
        out.at[idx, "net_pnl_cents"] = (100.0 - ask - fee) if win else (-ask - fee)
    return out


def summarize(registry: pd.DataFrame) -> Dict[str, Any]:
    if registry.empty:
        return {
            "registered": 0,
            "pending": 0,
            "resolved": 0,
            "wins": 0,
            "losses": 0,
            "accuracy": None,
            "net_pnl_cents": 0.0,
            "first_pending": "",
        }
    work = registry.copy()
    work["outcome_available"] = work["outcome_available"].map(bool_value)
    work["win"] = work["win"].map(bool_value)
    work["net_pnl_cents"] = pd.to_numeric(work["net_pnl_cents"], errors="coerce")
    resolved = work[work["outcome_available"]].copy()
    pending = work[~work["outcome_available"]].copy()
    wins = int(resolved["win"].sum()) if not resolved.empty else 0
    first_pending = ""
    if not pending.empty:
        first_pending = str(pending.sort_values("entry_dt").iloc[0]["market"])
    return {
        "registered": int(len(work)),
        "pending": int(len(pending)),
        "resolved": int(len(resolved)),
        "wins": wins,
        "losses": int(len(resolved)) - wins,
        "accuracy": wins / len(resolved) if len(resolved) else None,
        "net_pnl_cents": float(resolved["net_pnl_cents"].sum()) if len(resolved) else 0.0,
        "first_pending": first_pending,
    }


def write_report(generated: str, lock: Dict[str, Any], new_records: int, removed_post_close_records: int, summary: Dict[str, Any]) -> None:
    lines: List[str] = [
        "# Kinetic Path-Confirmation Pending Monitor",
        "",
        f"Generated UTC: `{generated}`",
        "",
        "## Scope",
        "",
        "- Research-only pre-resolution registry; no orders are submitted and no bot files or live processes are touched.",
        "- Applies the frozen delayed same-side confirmation policy to raw heartbeat rows, including unresolved markets.",
        "- Registers a signal only after the confirmation condition appears in the log, before outcome is known.",
        "",
        f"- Confirmation: `{lock['confirmation']['label']}`",
        f"- Effective entry boundary: `{effective_lock_dt(lock)}`",
        f"- New records registered this run: {new_records}",
        f"- Post-close/non-causal registry records removed this run: {removed_post_close_records}",
        "",
        "## Registry Summary",
        "",
        "| registered | pending | resolved | wins/losses | acc | resolved net P&L | first pending |",
        "|---:|---:|---:|---:|---:|---:|---|",
        (
            f"| {summary['registered']} | {summary['pending']} | {summary['resolved']} | "
            f"{summary['wins']}/{summary['losses']} | {pct(summary['accuracy'])} | "
            f"{fmt_cents(summary['net_pnl_cents'])} | `{summary['first_pending']}` |"
        ),
        "",
        "## Read",
        "",
    ]
    if summary["pending"]:
        lines.append("- At least one path-confirmation signal is pre-registered and waiting for settlement.")
    else:
        lines.append("- No unresolved path-confirmation signal is currently pending.")
    REPORT_LATEST.write_text("\n".join(lines) + "\n", encoding="utf-8")
    JSON_LATEST.write_text(
        json.dumps(
            {
                "generated_utc": generated,
                "lock": clean_json_local(lock),
                "new_records": new_records,
                "removed_post_close_records": removed_post_close_records,
                "summary": clean_json_local(summary),
            },
            indent=2,
            sort_keys=True,
        ),
        encoding="utf-8",
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--fetch-btc-candles", action="store_true")
    args = parser.parse_args()

    generated = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%SZ")
    registered_utc = datetime.now(timezone.utc).isoformat()
    lock = ensure_lock()
    policy = policy_from_record(lock["policy"])
    spec = spec_from_lock(lock)
    boundary = effective_lock_dt(lock)

    markets, outcomes = parse_bot_log(BOT_LOG)
    outcomes = closed_market_outcomes_only(markets, outcomes)

    registry = filter_registry_to_lock(load_registry(), boundary)
    registry, removed_post_close_records = filter_registry_to_pre_resolution(registry)
    registry = update_outcomes(registry, outcomes)

    rows = add_touch_hazard_scores(raw_side_rows(fetch_btc_candles=args.fetch_btc_candles))
    base = market_base(rows)
    selected = select_confirmed(rows, base, policy, spec)
    if not selected.empty and pd.notna(boundary):
        selected = selected[
            pd.to_datetime(selected["entry_dt"], utc=True, errors="coerce").gt(boundary)
            & pd.to_datetime(selected["close_dt"], utc=True, errors="coerce").gt(boundary)
        ].copy()
    now_dt = pd.Timestamp.now(tz="UTC")
    if not selected.empty:
        selected = selected[
            pd.to_datetime(selected["close_dt"], utc=True, errors="coerce").gt(now_dt)
            & ~selected["outcome_available"].map(bool_value)
        ].copy()

    existing_keys = set(zip(registry["lock_name"].astype(str), registry["market"].astype(str))) if not registry.empty else set()
    new_rows: List[Dict[str, Any]] = []
    for _, row in selected.iterrows():
        key = ("kinetic_path_confirm", str(row["market"]))
        if key in existing_keys:
            continue
        new_rows.append(signal_record(row, lock, registered_utc))
        existing_keys.add(key)

    if new_rows:
        new_df = pd.DataFrame(new_rows).reindex(columns=SIGNAL_COLS)
        registry = (
            new_df
            if registry.empty
            else pd.concat([registry.dropna(axis=1, how="all"), new_df.dropna(axis=1, how="all")], ignore_index=True)
        )
        registry = registry.reindex(columns=SIGNAL_COLS)
        registry = update_outcomes(registry, outcomes)
    if registry.empty:
        registry = pd.DataFrame(columns=SIGNAL_COLS)
    registry = registry.reindex(columns=SIGNAL_COLS)
    registry.to_csv(REGISTRY_PATH, index=False)
    archive = OUT_DIR / f"kinetic_path_confirmation_pending_registry_{generated}.csv"
    registry.to_csv(archive, index=False)

    summary = summarize(registry)
    write_report(generated, lock, len(new_rows), removed_post_close_records, summary)
    print("Kinetic path-confirmation pending monitor complete")
    print(f"new_records={len(new_rows)} registered={len(registry)}")
    print(f"removed_post_close_records={removed_post_close_records}")
    print(f"report={REPORT_LATEST}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
