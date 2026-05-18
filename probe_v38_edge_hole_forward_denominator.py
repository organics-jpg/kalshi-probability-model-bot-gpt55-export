"""Per-market forward denominator table for the v38 edge-hole candidate.

Research-only. Reads live logs and the existing lock/registry; no live bot
logic, process, or order path is touched.
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
REPORT_MD = OUT_DIR / "v38_edge_hole_forward_denominator_latest.md"
REPORT_JSON = OUT_DIR / "v38_edge_hole_forward_denominator_latest.json"
TABLE_CSV = OUT_DIR / "v38_edge_hole_forward_denominator_latest.csv"


def build_candidate_opportunities(predictions: pd.DataFrame, lock: dict[str, Any]) -> pd.DataFrame:
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
    if not pd.isna(model_dt):
        out = out[out["entry_dt"].gt(model_dt)].copy()
    p_yes = out[f"{shadow.MODEL}_p_yes"].clip(1e-6, 1.0 - 1e-6)
    out["p_yes"] = p_yes
    out["yes_edge_cents"] = 100.0 * p_yes - out["yes_ask_cents"]
    out["no_edge_cents"] = 100.0 * (1.0 - p_yes) - out["no_ask_cents"]
    yes_better = out["yes_edge_cents"].ge(out["no_edge_cents"])
    out["selected_side"] = np.where(yes_better, "yes", "no")
    out["selected_ask_cents"] = np.where(yes_better, out["yes_ask_cents"], out["no_ask_cents"])
    out["selected_edge_cents"] = np.where(yes_better, out["yes_edge_cents"], out["no_edge_cents"])
    out["selected_p_side"] = np.where(yes_better, p_yes, 1.0 - p_yes)
    out["entry_filters_ok"] = (
        out["selected_edge_cents"].ge(shadow.ENTRY_EDGE_FLOOR_CENTS)
        & out["selected_ask_cents"].ge(shadow.ENTRY_ASK_FLOOR_CENTS)
        & out["selected_ask_cents"].le(shadow.ENTRY_ASK_CAP_CENTS)
        & out["selected_p_side"].ge(shadow.ENTRY_P_SIDE_FLOOR)
        & out["seconds_to_close"].le(shadow.ENTRY_MAX_STC)
        & out["seconds_to_close"].ge(shadow.ENTRY_MIN_STC)
    )
    return out


def classify_markets(opps: pd.DataFrame, registry: pd.DataFrame) -> pd.DataFrame:
    markets = (
        opps.groupby("market", as_index=False)
        .agg(
            first_seen_dt=("entry_dt", "min"),
            last_seen_dt=("entry_dt", "max"),
            close_time=("close_time", "max"),
            opportunity_rows=("opportunity_key", "count"),
            max_selected_p_side=("selected_p_side", "max"),
            max_selected_edge_cents=("selected_edge_cents", "max"),
            min_seconds_to_close=("seconds_to_close", "min"),
            max_seconds_to_close=("seconds_to_close", "max"),
        )
        .sort_values("first_seen_dt")
    )
    first_eligible = (
        opps[opps["entry_filters_ok"]]
        .sort_values(["market", "entry_dt"])
        .drop_duplicates("market", keep="first")
        .copy()
    )
    first_eligible["edge_hole_blocked"] = first_eligible["selected_edge_cents"].gt(shadow.EDGE_HOLE_LOW) & first_eligible[
        "selected_edge_cents"
    ].le(shadow.EDGE_HOLE_HIGH)
    elig_cols = [
        "market",
        "entry_dt",
        "selected_side",
        "selected_ask_cents",
        "selected_edge_cents",
        "selected_p_side",
        "seconds_to_close",
        "edge_hole_blocked",
    ]
    table = markets.merge(
        first_eligible[elig_cols].rename(
            columns={
                "entry_dt": "first_eligible_dt",
                "seconds_to_close": "first_eligible_stc",
            }
        ),
        on="market",
        how="left",
    )
    if not registry.empty:
        reg_cols = [
            "market",
            "entry_dt",
            "status",
            "fee_net_cents",
            "fee_net_1c_entry_cents",
            "outcome",
            "win",
        ]
        reg = registry[[c for c in reg_cols if c in registry.columns]].copy().rename(columns={"entry_dt": "registered_entry_dt"})
        table = table.merge(reg, on="market", how="left")
    else:
        table["status"] = pd.NA
    table["classification"] = "no_entry_filters"
    table.loc[table["first_eligible_dt"].notna(), "classification"] = "eligible_unregistered"
    table.loc[table["edge_hole_blocked"].fillna(False), "classification"] = "edge_hole_blocked"
    table.loc[table["status"].notna(), "classification"] = "registered"
    return table.sort_values("first_seen_dt").reset_index(drop=True)


def build() -> tuple[pd.DataFrame, dict[str, Any]]:
    markets, outcomes_all = shadow.parse_bot_log(shadow.BOT_LOG)
    outcomes = shadow.closed_market_outcomes_only(markets, outcomes_all)
    frame = shadow.raw_rows(markets, outcomes)
    lock = shadow.load_or_create_lock()
    predictions = shadow.build_predictions(frame)
    opps = build_candidate_opportunities(predictions, lock)
    registry = shadow.load_registry()
    table = classify_markets(opps, registry)
    counts = table["classification"].value_counts().to_dict() if not table.empty else {}
    payload = {
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "lock_model_defined_utc": lock.get("model_defined_utc"),
        "market_count": int(len(table)),
        "classification_counts": {str(k): int(v) for k, v in counts.items()},
        "registered_coverage": float((table["classification"].eq("registered")).sum() / len(table)) if len(table) else None,
    }
    return table, payload


def write_report(table: pd.DataFrame, payload: dict[str, Any]) -> None:
    lines = [
        "# v38 Edge-Hole Forward Denominator",
        "",
        f"Generated UTC: `{payload['generated_utc']}`",
        f"Model defined UTC: `{payload['lock_model_defined_utc']}`",
        "",
        "## Summary",
        "",
        f"- Post-lock observed markets: {payload['market_count']}",
        f"- Registered coverage: {100.0 * payload['registered_coverage']:.2f}%" if payload.get("registered_coverage") is not None else "- Registered coverage: NA",
    ]
    for key, value in sorted(payload["classification_counts"].items()):
        lines.append(f"- {key}: {value}")
    lines += [
        "",
        "## Markets",
        "",
        "| market | classification | first seen | first eligible | side | ask | edge | p_side | stc | status | fee+1c |",
        "|---|---|---|---|---:|---:|---:|---:|---:|---|---:|",
    ]
    for _, row in table.iterrows():
        fee_1c = row.get("fee_net_1c_entry_cents")
        fee_text = "" if pd.isna(fee_1c) else f"${float(fee_1c) / 100.0:.2f}"
        lines.append(
            f"| `{row['market']}` | `{row['classification']}` | `{row['first_seen_dt']}` | "
            f"`{row.get('first_eligible_dt', '')}` | `{row.get('selected_side', '')}` | "
            f"{'' if pd.isna(row.get('selected_ask_cents')) else f'{float(row.get('selected_ask_cents')):.1f}'} | "
            f"{'' if pd.isna(row.get('selected_edge_cents')) else f'{float(row.get('selected_edge_cents')):.2f}'} | "
            f"{'' if pd.isna(row.get('selected_p_side')) else f'{float(row.get('selected_p_side')):.3f}'} | "
            f"{'' if pd.isna(row.get('first_eligible_stc')) else f'{float(row.get('first_eligible_stc')):.1f}'} | "
            f"`{row.get('status', '')}` | {fee_text} |"
        )
    REPORT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")
    REPORT_JSON.write_text(json.dumps(clean_json(payload), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    table.to_csv(TABLE_CSV, index=False)


def main() -> int:
    table, payload = build()
    write_report(table, payload)
    print("v38 edge-hole forward denominator complete")
    print(f"markets={payload['market_count']} coverage={payload.get('registered_coverage')} report={REPORT_MD}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
