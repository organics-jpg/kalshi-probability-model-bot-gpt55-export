"""Leave-one-day-out audit for v38 edge-hole veto candidates.

Research-only. Uses saved candidate trades only; no live bot code, process, or
order path is touched.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd

import probe_v39_entry_exit_strategy_projection as base
from probe_market_interval_80coverage import clean_json


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
INPUT = OUT_DIR / "v38_edge_hole_veto_candidate_trades_latest.csv"
REPORT_MD = OUT_DIR / "v38_edge_hole_lodo_audit_latest.md"
REPORT_JSON = OUT_DIR / "v38_edge_hole_lodo_audit_latest.json"

PRIMARY = "block_market_first_edge_8_20"


def dollars_cents(value: Any) -> str:
    try:
        return f"${float(value) / 100.0:.2f}"
    except (TypeError, ValueError):
        return "NA"


def load() -> pd.DataFrame:
    rows = pd.read_csv(INPUT, low_memory=False)
    rows["entry_dt"] = pd.to_datetime(rows["entry_dt"], utc=True, errors="coerce")
    rows["entry_day_utc"] = rows["entry_dt"].dt.strftime("%Y-%m-%d")
    for col in ["pnl_cents", "total_fee_cents"]:
        rows[col] = pd.to_numeric(rows[col], errors="coerce").fillna(0.0)
    rows["fee_net_1c_entry_cents"] = rows["pnl_cents"] - rows["total_fee_cents"] - base.QTY
    rows["fee_net_cents"] = rows["pnl_cents"] - rows["total_fee_cents"]
    return rows


def candidate_day_table(rows: pd.DataFrame) -> pd.DataFrame:
    table = (
        rows.groupby(["candidate", "entry_day_utc"], as_index=False)
        .agg(
            trades=("market", "count"),
            fee_net_1c_entry_cents=("fee_net_1c_entry_cents", "sum"),
            fee_net_cents=("fee_net_cents", "sum"),
            gross_cents=("pnl_cents", "sum"),
        )
        .sort_values(["candidate", "entry_day_utc"])
    )
    return table


def lodo(table: pd.DataFrame) -> list[dict[str, Any]]:
    days = sorted(table["entry_day_utc"].dropna().astype(str).unique())
    records: list[dict[str, Any]] = []
    for holdout_day in days:
        train = table[~table["entry_day_utc"].eq(holdout_day)].copy()
        hold = table[table["entry_day_utc"].eq(holdout_day)].copy()
        train_metrics = (
            train.groupby("candidate", as_index=False)
            .agg(
                train_days=("entry_day_utc", "nunique"),
                train_total_1c=("fee_net_1c_entry_cents", "sum"),
                train_min_day_1c=("fee_net_1c_entry_cents", "min"),
                train_positive_days=("fee_net_1c_entry_cents", lambda s: int((s > 0).sum())),
            )
            .sort_values(["train_min_day_1c", "train_total_1c"], ascending=[False, False])
        )
        if train_metrics.empty:
            continue
        selected = train_metrics.iloc[0]
        hold_row = hold[hold["candidate"].eq(selected["candidate"])]
        hold_1c = float(hold_row["fee_net_1c_entry_cents"].sum()) if not hold_row.empty else 0.0
        primary_hold = hold[hold["candidate"].eq(PRIMARY)]
        primary_1c = float(primary_hold["fee_net_1c_entry_cents"].sum()) if not primary_hold.empty else 0.0
        records.append(
            {
                "holdout_day": holdout_day,
                "selected_candidate": str(selected["candidate"]),
                "selected_train_min_day_1c": float(selected["train_min_day_1c"]),
                "selected_train_total_1c": float(selected["train_total_1c"]),
                "selected_train_positive_days": int(selected["train_positive_days"]),
                "selected_holdout_1c": hold_1c,
                "primary_holdout_1c": primary_1c,
            }
        )
    return records


def build() -> dict[str, Any]:
    rows = load()
    table = candidate_day_table(rows)
    records = lodo(table)
    primary = table[table["candidate"].eq(PRIMARY)].copy()
    return {
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "input": str(INPUT),
        "primary": PRIMARY,
        "lodo": records,
        "primary_by_day": primary.to_dict("records"),
    }


def write_report(payload: dict[str, Any]) -> None:
    records = payload["lodo"]
    positive_selected = sum(1 for row in records if row["selected_holdout_1c"] > 0)
    positive_primary = sum(1 for row in records if row["primary_holdout_1c"] > 0)
    lines = [
        "# v38 Edge-Hole Leave-One-Day-Out Audit",
        "",
        f"Generated UTC: `{payload['generated_utc']}`",
        "",
        "## Scope",
        "",
        "- Uses saved retrospective candidate trades.",
        "- For each UTC holdout day, selects the candidate with the best worst-day fee+1c-entry P&L on the other days.",
        "- This checks whether the edge-hole range is a one-day overfit.",
        "",
        "## LODO Selection",
        "",
        "| holdout day | selected candidate | train min day | train total | selected holdout | primary holdout |",
        "|---|---|---:|---:|---:|---:|",
    ]
    for row in records:
        lines.append(
            f"| `{row['holdout_day']}` | `{row['selected_candidate']}` | "
            f"{dollars_cents(row['selected_train_min_day_1c'])} | "
            f"{dollars_cents(row['selected_train_total_1c'])} | "
            f"{dollars_cents(row['selected_holdout_1c'])} | "
            f"{dollars_cents(row['primary_holdout_1c'])} |"
        )
    lines += [
        "",
        "## Read",
        "",
        f"- LODO-selected candidate positive on holdout day: {positive_selected}/{len(records)}.",
        f"- Fixed primary `{PRIMARY}` positive on holdout day: {positive_primary}/{len(records)}.",
    ]
    REPORT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")
    REPORT_JSON.write_text(json.dumps(clean_json(payload), indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main() -> int:
    payload = build()
    write_report(payload)
    records = payload["lodo"]
    print("v38 edge-hole LODO audit complete")
    print(f"report={REPORT_MD}")
    print(
        f"selected_positive={sum(1 for row in records if row['selected_holdout_1c'] > 0)}/{len(records)} "
        f"primary_positive={sum(1 for row in records if row['primary_holdout_1c'] > 0)}/{len(records)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
