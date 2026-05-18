"""Funnel diagnostic for the v38 edge-hole strict-forward shadow monitor.

Research-only. Reads logs and saved lock state; does not touch live bot logic,
processes, or orders.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

import probe_v38_edge_hole_shadow_monitor as shadow
from probe_market_interval_80coverage import clean_json


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
REPORT_MD = OUT_DIR / "v38_edge_hole_shadow_funnel_latest.md"
REPORT_JSON = OUT_DIR / "v38_edge_hole_shadow_funnel_latest.json"


def pct(value: Any) -> str:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return "NA"
    if not np.isfinite(number):
        return "NA"
    return f"{100.0 * number:.2f}%"


def count_rows(rows: pd.DataFrame) -> dict[str, Any]:
    if rows.empty:
        return {"rows": 0, "markets": 0, "min_entry_dt": None, "max_entry_dt": None}
    return {
        "rows": int(len(rows)),
        "markets": int(rows["market"].astype(str).nunique()) if "market" in rows.columns else 0,
        "min_entry_dt": str(pd.to_datetime(rows["entry_dt"], utc=True, errors="coerce").min())
        if "entry_dt" in rows.columns
        else None,
        "max_entry_dt": str(pd.to_datetime(rows["entry_dt"], utc=True, errors="coerce").max())
        if "entry_dt" in rows.columns
        else None,
    }


def candidate_funnel(predictions: pd.DataFrame, lock: dict[str, Any]) -> tuple[dict[str, Any], pd.DataFrame]:
    now = shadow.utc_now()
    model_dt = pd.to_datetime(lock.get("model_defined_utc"), utc=True, errors="coerce")
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
    for col in ["yes_ask_cents", "no_ask_cents", "seconds_to_close", f"{shadow.MODEL}_p_yes"]:
        out[col] = pd.to_numeric(out[col], errors="coerce")
    out["entry_dt"] = pd.to_datetime(out["entry_dt"], utc=True, errors="coerce")
    out["close_time"] = pd.to_datetime(out["close_time"], utc=True, errors="coerce")
    p_yes = out[f"{shadow.MODEL}_p_yes"].clip(1e-6, 1.0 - 1e-6)
    out["p_yes"] = p_yes
    out["yes_edge_cents"] = 100.0 * p_yes - out["yes_ask_cents"]
    out["no_edge_cents"] = 100.0 * (1.0 - p_yes) - out["no_ask_cents"]
    yes_better = out["yes_edge_cents"].ge(out["no_edge_cents"])
    out["selected_side"] = np.where(yes_better, "yes", "no")
    out["selected_ask_cents"] = np.where(yes_better, out["yes_ask_cents"], out["no_ask_cents"])
    out["selected_edge_cents"] = np.where(yes_better, out["yes_edge_cents"], out["no_edge_cents"])
    out["selected_p_side"] = np.where(yes_better, p_yes, 1.0 - p_yes)

    post = out[out["entry_dt"].gt(model_dt)].copy() if not pd.isna(model_dt) else out.copy()
    future_post = post[post["close_time"].gt(now)].copy()
    edge_ok = post[post["selected_edge_cents"].ge(shadow.ENTRY_EDGE_FLOOR_CENTS)].copy()
    ask_ok = edge_ok[edge_ok["selected_ask_cents"].le(shadow.ENTRY_ASK_CAP_CENTS)].copy()
    pside_ok = ask_ok[ask_ok["selected_p_side"].ge(shadow.ENTRY_P_SIDE_FLOOR)].copy()
    stc_ok = pside_ok[
        pside_ok["seconds_to_close"].le(shadow.ENTRY_MAX_STC) & pside_ok["seconds_to_close"].ge(0.0)
    ].copy()
    first = stc_ok.sort_values(["market", "entry_dt"]).drop_duplicates("market", keep="first").reset_index(drop=True)
    if first.empty:
        after_block = first
        blocked = first
    else:
        in_hole = first["selected_edge_cents"].gt(shadow.EDGE_HOLE_LOW) & first["selected_edge_cents"].le(
            shadow.EDGE_HOLE_HIGH
        )
        blocked = first[in_hole].copy()
        after_block = first[~in_hole].copy()
    after_block_future = after_block[after_block["close_time"].gt(now)].copy()

    payload = {
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "now_utc": str(now),
        "model_defined_utc": str(model_dt),
        "all_opportunities": count_rows(out),
        "post_lock_opportunities": count_rows(post),
        "post_lock_future_close_opportunities": count_rows(future_post),
        "post_lock_edge_ok": count_rows(edge_ok),
        "post_lock_edge_ask_ok": count_rows(ask_ok),
        "post_lock_edge_ask_pside_ok": count_rows(pside_ok),
        "post_lock_all_entry_filters_ok": count_rows(stc_ok),
        "first_eligible_by_market": count_rows(first),
        "first_eligible_blocked_edge_hole": count_rows(blocked),
        "first_eligible_after_block": count_rows(after_block),
        "first_eligible_after_block_future_close": count_rows(after_block_future),
        "blocked_fraction": float(len(blocked) / len(first)) if len(first) else None,
    }
    cols = [
        "market",
        "entry_dt",
        "close_time",
        "selected_side",
        "selected_ask_cents",
        "selected_edge_cents",
        "selected_p_side",
        "seconds_to_close",
    ]
    return payload, after_block_future[[c for c in cols if c in after_block_future.columns]].head(20)


def write_report(payload: dict[str, Any], sample: pd.DataFrame) -> None:
    lines = [
        "# v38 Edge-Hole Shadow Funnel",
        "",
        f"Generated UTC: `{payload['generated_utc']}`",
        f"Now UTC: `{payload['now_utc']}`",
        f"Model defined UTC: `{payload['model_defined_utc']}`",
        "",
        "## Funnel",
        "",
        "| stage | rows | markets | min entry | max entry |",
        "|---|---:|---:|---|---|",
    ]
    for key in [
        "all_opportunities",
        "post_lock_opportunities",
        "post_lock_future_close_opportunities",
        "post_lock_edge_ok",
        "post_lock_edge_ask_ok",
        "post_lock_edge_ask_pside_ok",
        "post_lock_all_entry_filters_ok",
        "first_eligible_by_market",
        "first_eligible_blocked_edge_hole",
        "first_eligible_after_block",
        "first_eligible_after_block_future_close",
    ]:
        row = payload[key]
        lines.append(f"| `{key}` | {row['rows']} | {row['markets']} | `{row['min_entry_dt']}` | `{row['max_entry_dt']}` |")
    lines += [
        "",
        f"- Blocked fraction among first eligible markets: {pct(payload.get('blocked_fraction'))}",
        "",
        "## Sample Future Candidates",
        "",
    ]
    if sample.empty:
        lines.append("- None.")
    else:
        lines += [
            "| market | entry dt | close | side | ask | edge | p_side | stc |",
            "|---|---|---|---:|---:|---:|---:|---:|",
        ]
        for _, row in sample.iterrows():
            lines.append(
                f"| `{row['market']}` | `{row['entry_dt']}` | `{row['close_time']}` | `{row['selected_side']}` | "
                f"{float(row['selected_ask_cents']):.1f} | {float(row['selected_edge_cents']):.2f} | "
                f"{float(row['selected_p_side']):.3f} | {float(row['seconds_to_close']):.1f} |"
            )
    REPORT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")
    REPORT_JSON.write_text(json.dumps(clean_json(payload), indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main() -> int:
    markets, outcomes_all = shadow.parse_bot_log(shadow.BOT_LOG)
    outcomes = shadow.closed_market_outcomes_only(markets, outcomes_all)
    frame = shadow.raw_rows(markets, outcomes)
    if frame.empty:
        raise SystemExit("No heartbeat rows found.")
    lock = shadow.load_or_create_lock()
    predictions = shadow.build_predictions(frame)
    payload, sample = candidate_funnel(predictions, lock)
    write_report(payload, sample)
    print("v38 edge-hole shadow funnel complete")
    print(f"report={REPORT_MD}")
    print(
        "post_lock="
        f"{payload['post_lock_opportunities']['rows']} "
        "eligible="
        f"{payload['post_lock_all_entry_filters_ok']['rows']} "
        "after_block_future="
        f"{payload['first_eligible_after_block_future_close']['rows']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
