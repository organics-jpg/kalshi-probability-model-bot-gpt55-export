"""Temporal stability audit for the v38 edge-hole candidate.

Research-only. Uses saved candidate trades; no live bot process/order path is touched.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

import probe_v39_entry_exit_strategy_projection as base
from probe_market_interval_80coverage import clean_json


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
INPUT = OUT_DIR / "v38_edge_hole_veto_candidate_trades_latest.csv"
REPORT_MD = OUT_DIR / "v38_edge_hole_temporal_stability_latest.md"
REPORT_JSON = OUT_DIR / "v38_edge_hole_temporal_stability_latest.json"

PRIMARY = "block_market_first_edge_8_20"
BASELINE = "baseline_no_veto"


def dollars_from_cents(value: Any) -> str:
    try:
        return f"${float(value) / 100.0:.2f}"
    except (TypeError, ValueError):
        return "NA"


def pct(value: Any) -> str:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return "NA"
    if not np.isfinite(number):
        return "NA"
    return f"{100.0 * number:.2f}%"


def load() -> pd.DataFrame:
    rows = pd.read_csv(INPUT, low_memory=False)
    rows["entry_dt"] = pd.to_datetime(rows["entry_dt"], utc=True, errors="coerce")
    for col in ["pnl_cents", "total_fee_cents", "cost_cents"]:
        rows[col] = pd.to_numeric(rows[col], errors="coerce").fillna(0.0)
    rows["fee_net_cents"] = rows["pnl_cents"] - rows["total_fee_cents"]
    rows["fee_net_1c_entry_cents"] = rows["fee_net_cents"] - base.QTY
    rows["entry_day_utc"] = rows["entry_dt"].dt.strftime("%Y-%m-%d")
    return rows


def aggregate(group: pd.DataFrame) -> dict[str, Any]:
    fee_net = float(group["fee_net_cents"].sum())
    fee_net_1c = float(group["fee_net_1c_entry_cents"].sum())
    gross = float(group["pnl_cents"].sum())
    cost = float(group["cost_cents"].sum())
    return {
        "trades": int(len(group)),
        "gross_cents": gross,
        "fee_net_cents": fee_net,
        "fee_net_1c_entry_cents": fee_net_1c,
        "cost_cents": cost,
        "fee_net_roi": float(fee_net / cost) if cost > 0 else None,
        "exits": int((~group["settled"].astype(bool)).sum()) if "settled" in group.columns else None,
    }


def by_dimension(rows: pd.DataFrame, dimension: str) -> list[dict[str, Any]]:
    records = []
    for key, group in rows.groupby(dimension, dropna=False):
        record = {"bucket": str(key)}
        record.update(aggregate(group))
        records.append(record)
    return records


def build() -> dict[str, Any]:
    rows = load()
    payload: dict[str, Any] = {
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "input": str(INPUT),
        "candidates": {},
    }
    for candidate in [BASELINE, PRIMARY]:
        part = rows[rows["candidate"].eq(candidate)].copy()
        candidate_payload = {
            "overall": aggregate(part),
            "by_day": by_dimension(part, "entry_day_utc"),
            "by_split": by_dimension(part, "split"),
            "by_side": by_dimension(part, "side"),
            "by_exit_type": by_dimension(part, "exit_type"),
        }
        day_nets = [row["fee_net_1c_entry_cents"] for row in candidate_payload["by_day"]]
        candidate_payload["positive_1c_days"] = int(sum(value > 0 for value in day_nets))
        candidate_payload["total_days"] = int(len(day_nets))
        candidate_payload["worst_1c_day_cents"] = float(min(day_nets)) if day_nets else None
        payload["candidates"][candidate] = candidate_payload
    return payload


def write_report(payload: dict[str, Any]) -> None:
    primary = payload["candidates"][PRIMARY]
    baseline = payload["candidates"][BASELINE]
    lines = [
        "# v38 Edge-Hole Temporal Stability",
        "",
        f"Generated UTC: `{payload['generated_utc']}`",
        "",
        "## Scope",
        "",
        "- Temporal audit of saved retrospective candidate trades.",
        "- Compares primary edge-hole candidate against the no-veto baseline.",
        "",
        "## Overall",
        "",
        "| candidate | trades | gross | fee net | fee+1c entry | fee ROI | positive days | worst 1c day |",
        "|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for name, data in [(BASELINE, baseline), (PRIMARY, primary)]:
        overall = data["overall"]
        lines.append(
            f"| `{name}` | {overall['trades']} | {dollars_from_cents(overall['gross_cents'])} | "
            f"{dollars_from_cents(overall['fee_net_cents'])} | "
            f"{dollars_from_cents(overall['fee_net_1c_entry_cents'])} | "
            f"{pct(overall['fee_net_roi'])} | {data['positive_1c_days']}/{data['total_days']} | "
            f"{dollars_from_cents(data['worst_1c_day_cents'])} |"
        )
    lines += [
        "",
        "## Primary By Day",
        "",
        "| day UTC | trades | gross | fee net | fee+1c entry | exits |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for row in primary["by_day"]:
        lines.append(
            f"| `{row['bucket']}` | {row['trades']} | {dollars_from_cents(row['gross_cents'])} | "
            f"{dollars_from_cents(row['fee_net_cents'])} | "
            f"{dollars_from_cents(row['fee_net_1c_entry_cents'])} | {row['exits']} |"
        )
    lines += [
        "",
        "## Primary By Split",
        "",
        "| split | trades | gross | fee net | fee+1c entry |",
        "|---|---:|---:|---:|---:|",
    ]
    for row in primary["by_split"]:
        lines.append(
            f"| `{row['bucket']}` | {row['trades']} | {dollars_from_cents(row['gross_cents'])} | "
            f"{dollars_from_cents(row['fee_net_cents'])} | {dollars_from_cents(row['fee_net_1c_entry_cents'])} |"
        )
    lines += [
        "",
        "## Read",
        "",
        f"- Primary candidate has {primary['positive_1c_days']}/{primary['total_days']} positive UTC days after fees plus a 1c entry haircut.",
        f"- Worst UTC day after fees plus 1c entry is {dollars_from_cents(primary['worst_1c_day_cents'])}.",
        "- This improves the retrospective case but does not replace strict-forward validation.",
    ]
    REPORT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")
    REPORT_JSON.write_text(json.dumps(clean_json(payload), indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main() -> int:
    payload = build()
    write_report(payload)
    primary = payload["candidates"][PRIMARY]
    print("v38 edge-hole temporal stability complete")
    print(f"report={REPORT_MD}")
    print(
        f"primary_positive_1c_days={primary['positive_1c_days']}/{primary['total_days']} "
        f"worst_1c_day_cents={primary['worst_1c_day_cents']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
