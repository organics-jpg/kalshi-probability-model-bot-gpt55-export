"""Forward denominator for the v70 balanced candidate."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd

import probe_v70_v55_entry_v66_margin_exit_shadow_monitor as monitor
from probe_live_v28_fv_accuracy_volume import BOT_LOG, parse_bot_log
from probe_market_interval_80coverage import clean_json
from shadow_live_v28_physics_validator import closed_market_outcomes_only


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
REPORT_MD = OUT_DIR / "v70_v55_entry_v66_margin_exit_forward_denominator_latest.md"
REPORT_JSON = OUT_DIR / "v70_v55_entry_v66_margin_exit_forward_denominator_latest.json"
TABLE_CSV = OUT_DIR / "v70_v55_entry_v66_margin_exit_forward_denominator_latest.csv"


def load_registry() -> pd.DataFrame:
    path = monitor.shadow.REGISTRY_PATH
    if not path.exists() or path.stat().st_size == 0:
        return pd.DataFrame()
    try:
        rows = pd.read_csv(path, low_memory=False)
    except pd.errors.EmptyDataError:
        return pd.DataFrame()
    if "entry_dt" in rows.columns:
        rows["entry_dt"] = pd.to_datetime(rows["entry_dt"], utc=True, errors="coerce")
    return rows


def build() -> tuple[pd.DataFrame, dict[str, Any]]:
    markets, outcomes_all = parse_bot_log(BOT_LOG)
    outcomes = closed_market_outcomes_only(markets, outcomes_all)
    frame = monitor.shadow.raw_rows(markets, outcomes)
    if frame.empty:
        return pd.DataFrame(), {"market_count": 0}
    lock = monitor.load_or_create_lock()
    predictions = monitor.shadow.build_predictions(frame)
    opps = monitor.opportunity_table(predictions, lock)
    model_dt = pd.to_datetime(lock.get("model_defined_utc"), utc=True, errors="coerce")
    if not pd.isna(model_dt):
        opps = opps[opps["entry_dt"].gt(model_dt)].copy()
    if opps.empty:
        payload = {
            "generated_utc": datetime.now(timezone.utc).isoformat(),
            "lock_model_defined_utc": lock.get("model_defined_utc"),
            "market_count": 0,
            "registered_count": 0,
            "registered_coverage": None,
            "classification_counts": {},
        }
        return pd.DataFrame(), payload

    opps["entry_filters_ok"] = (
        opps["selected_edge_cents"].ge(monitor.shadow.ENTRY_EDGE_FLOOR_CENTS)
        & opps["selected_ask_cents"].ge(monitor.shadow.ENTRY_ASK_FLOOR_CENTS)
        & opps["selected_ask_cents"].le(monitor.shadow.ENTRY_ASK_CAP_CENTS)
        & opps["selected_p_side"].ge(monitor.shadow.ENTRY_P_SIDE_FLOOR)
        & opps["seconds_to_close"].le(monitor.shadow.ENTRY_MAX_STC)
        & opps["seconds_to_close"].ge(monitor.shadow.ENTRY_MIN_STC)
    )
    table = (
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
    table = table.merge(
        first_eligible[
            [
                "market",
                "entry_dt",
                "selected_side",
                "selected_ask_cents",
                "selected_edge_cents",
                "selected_p_side",
                "seconds_to_close",
            ]
        ].rename(columns={"entry_dt": "first_eligible_dt", "seconds_to_close": "first_eligible_stc"}),
        on="market",
        how="left",
    )
    registry = load_registry()
    if not registry.empty:
        reg_cols = ["market", "entry_dt", "status", "fee_net_cents", "fee_net_1c_entry_cents", "outcome", "win"]
        reg = registry[[c for c in reg_cols if c in registry.columns]].copy().rename(columns={"entry_dt": "registered_entry_dt"})
        table = table.merge(reg, on="market", how="left")
    else:
        table["status"] = pd.NA

    table["classification"] = "no_entry_filters"
    table.loc[table["first_eligible_dt"].notna(), "classification"] = "eligible_unregistered"
    table.loc[table["status"].notna(), "classification"] = "registered"
    market_count = int(table["market"].nunique())
    registered_count = int(table["classification"].eq("registered").sum())
    payload = {
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "lock_model_defined_utc": lock.get("model_defined_utc"),
        "market_count": market_count,
        "registered_count": registered_count,
        "registered_coverage": float(registered_count / market_count) if market_count else None,
        "classification_counts": {str(k): int(v) for k, v in table["classification"].value_counts().to_dict().items()},
    }
    return table.sort_values("first_seen_dt").reset_index(drop=True), payload


def fmt(value: Any, digits: int = 2) -> str:
    try:
        if pd.isna(value):
            return ""
        return f"{float(value):.{digits}f}"
    except (TypeError, ValueError):
        return ""


def write_report(table: pd.DataFrame, payload: dict[str, Any]) -> None:
    lines = [
        "# v70 v55 Entry / v66 Margin Exit Forward Denominator",
        "",
        f"Generated UTC: `{payload.get('generated_utc')}`",
        f"Model defined UTC: `{payload.get('lock_model_defined_utc')}`",
        "",
        "## Summary",
        "",
        f"- Post-lock observed markets: {payload.get('market_count')}",
        f"- Registered coverage: {monitor.shadow.pct(payload.get('registered_coverage'))}",
    ]
    for key, count in payload.get("classification_counts", {}).items():
        lines.append(f"- {key}: {count}")
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
            f"{fmt(row.get('selected_ask_cents'), 1)} | {fmt(row.get('selected_edge_cents'), 2)} | "
            f"{fmt(row.get('selected_p_side'), 3)} | {fmt(row.get('first_eligible_stc'), 1)} | "
            f"`{row.get('status', '')}` | {fee_text} |"
        )
    REPORT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")
    REPORT_JSON.write_text(json.dumps(clean_json(payload), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    table.to_csv(TABLE_CSV, index=False)


def main() -> int:
    table, payload = build()
    write_report(table, payload)
    print("v70 v55 entry / v66 margin exit forward denominator complete")
    print(f"markets={payload.get('market_count')} coverage={payload.get('registered_coverage')} report={REPORT_MD}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
