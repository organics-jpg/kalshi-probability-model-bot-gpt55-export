"""Fresh loss attribution for locked BTC 15m profit candidates.

This diagnostic reads the pre-resolution registry and asks what the already
settled forward rows are saying about losses. It does not tune a new rule. The
point is to keep the physics story honest while sample size accumulates.

Research-only: no orders are submitted and no bot files or live processes are
modified.
"""
from __future__ import annotations

import json
import math
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

import numpy as np
import pandas as pd

from probe_cross_dataset_profit_frontier import fmt_cents
from probe_market_interval_80coverage import OUT_DIR, clean_json, pct
from probe_profit_lock_pending_signal_monitor import REGISTRY_PATH, bool_value


NUMERIC_FEATURES = [
    "ask_cents",
    "seconds_to_close",
    "score_value",
    "book_p_side",
    "brownian_p_rv_15m",
    "brownian_p_rv_30m",
    "margin_per_rv_sigma_15m",
    "adverse_move_15m",
    "touch_loss_rv_15m",
    "touch_survival_rv_15m",
    "book_touch_blend_15",
    "kinetic_touch_score_15",
]


def clean_json_local(value: Any) -> Any:
    if isinstance(value, pd.Timestamp):
        return value.isoformat()
    if isinstance(value, dict):
        return {str(k): clean_json_local(v) for k, v in value.items()}
    if isinstance(value, list):
        return [clean_json_local(v) for v in value]
    return clean_json(value)


def fmt_num(value: Optional[float], digits: int = 3) -> str:
    if value is None or not math.isfinite(float(value)):
        return "NA"
    return f"{float(value):.{digits}f}"


def load_registry() -> pd.DataFrame:
    if not REGISTRY_PATH.exists():
        raise SystemExit(f"Missing pending registry: {REGISTRY_PATH}")
    df = pd.read_csv(REGISTRY_PATH)
    for col in ["entry_dt", "close_dt", "lock_close_dt", "registered_utc"]:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], utc=True, errors="coerce")
    for col in NUMERIC_FEATURES + ["entry_fee_cents", "net_pnl_cents"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    df["outcome_available"] = df["outcome_available"].map(bool_value)
    df["win"] = df["win"].map(bool_value)
    return df.sort_values(["lock_name", "entry_dt", "market"]).reset_index(drop=True)


def add_bins(rows: pd.DataFrame) -> pd.DataFrame:
    out = rows.copy()
    out["ask_bin"] = pd.cut(out["ask_cents"], [-np.inf, 50, 60, 70, 80, 90, np.inf], include_lowest=True)
    out["margin_bin"] = pd.cut(out["margin_per_rv_sigma_15m"], [-np.inf, 0, 0.25, 0.5, 1.0, np.inf])
    out["adverse15_bin"] = pd.cut(out["adverse_move_15m"], [-np.inf, 0, 10, 25, 50, np.inf])
    out["touch_loss_bin"] = pd.cut(out["touch_loss_rv_15m"], [-np.inf, 0.5, 0.75, 0.9, 0.99, np.inf])
    return out


def lock_summary(rows: pd.DataFrame) -> List[Dict[str, Any]]:
    out: List[Dict[str, Any]] = []
    for lock, part in rows.groupby("lock_name", sort=False):
        resolved = part[part["outcome_available"]].copy()
        pending = part[~part["outcome_available"]].copy()
        n = int(len(resolved))
        wins = int(resolved["win"].sum()) if n else 0
        out.append(
            {
                "lock_name": lock,
                "registered": int(len(part)),
                "resolved": n,
                "pending": int(len(pending)),
                "wins": wins,
                "losses": n - wins,
                "accuracy": wins / n if n else None,
                "net_pnl_cents": float(resolved["net_pnl_cents"].sum()) if n else 0.0,
                "median_ask": float(resolved["ask_cents"].median()) if n else None,
                "first_pending_market": str(pending.iloc[0]["market"]) if not pending.empty else "",
            }
        )
    return out


def feature_deltas(rows: pd.DataFrame) -> List[Dict[str, Any]]:
    out: List[Dict[str, Any]] = []
    resolved = rows[rows["outcome_available"]].copy()
    for lock, part in resolved.groupby("lock_name", sort=False):
        wins = part[part["win"]]
        losses = part[~part["win"]]
        for feature in NUMERIC_FEATURES:
            if feature not in part.columns:
                continue
            win_mean = float(wins[feature].mean()) if not wins.empty else None
            loss_mean = float(losses[feature].mean()) if not losses.empty else None
            out.append(
                {
                    "lock_name": lock,
                    "feature": feature,
                    "win_mean": win_mean,
                    "loss_mean": loss_mean,
                    "loss_minus_win": (loss_mean - win_mean) if win_mean is not None and loss_mean is not None else None,
                }
            )
    out.sort(key=lambda row: abs(row["loss_minus_win"] or 0.0), reverse=True)
    return out


def bin_rows(rows: pd.DataFrame, group_col: str) -> List[Dict[str, Any]]:
    out: List[Dict[str, Any]] = []
    resolved = rows[rows["outcome_available"]].copy()
    for (lock, group), part in resolved.groupby(["lock_name", group_col], observed=True, dropna=False):
        n = int(len(part))
        if n <= 0:
            continue
        wins = int(part["win"].sum())
        out.append(
            {
                "lock_name": lock,
                "group_col": group_col,
                "group": str(group),
                "markets": n,
                "wins": wins,
                "losses": n - wins,
                "accuracy": wins / n if n else None,
                "net_pnl_cents": float(part["net_pnl_cents"].sum()),
                "median_ask": float(part["ask_cents"].median()),
            }
        )
    out.sort(key=lambda row: (row["net_pnl_cents"], -row["markets"]))
    return out


def write_report(path, generated: str, rows: pd.DataFrame, summary: List[Dict[str, Any]], deltas: List[Dict[str, Any]], bins: List[Dict[str, Any]]) -> None:
    lines = [
        "# Profit Fresh Loss Attribution",
        "",
        f"Generated UTC: `{generated}`",
        "",
        "## Scope",
        "",
        "- Research-only diagnostic; no orders are submitted and no bot files or live processes are touched.",
        "- Uses the locked pending-signal registry, so rows were registered before settlement.",
        "- This is not a retune; it is a physics read on settled fresh evidence.",
        "",
        "## Lock Summary",
        "",
        "| lock | registered | resolved | pending | wins/losses | acc | net P&L | median ask | first pending |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---|",
    ]
    for row in summary:
        lines.append(
            f"| {row['lock_name']} | {row['registered']} | {row['resolved']} | {row['pending']} | "
            f"{row['wins']}/{row['losses']} | {pct(row['accuracy'])} | {fmt_cents(row['net_pnl_cents'])} | "
            f"{fmt_cents(row['median_ask'])} | `{row['first_pending_market']}` |"
        )

    resolved = rows[rows["outcome_available"]].copy()
    lines += [
        "",
        "## Fresh Resolved Rows",
        "",
        "| lock | market | side | ask | outcome | pnl | score | book | rv15 | margin15 | adverse15 | touch loss |",
        "|---|---|---|---:|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for _, row in resolved.tail(30).iterrows():
        lines.append(
            f"| {row['lock_name']} | `{row['market']}` | {row['side']} | {fmt_cents(row['ask_cents'])} | "
            f"{row['outcome']} | {fmt_cents(row['net_pnl_cents'])} | {fmt_num(row.get('score_value'))} | "
            f"{fmt_num(row.get('book_p_side'))} | {fmt_num(row.get('brownian_p_rv_15m'))} | "
            f"{fmt_num(row.get('margin_per_rv_sigma_15m'))} | {fmt_cents(row.get('adverse_move_15m'))} | "
            f"{fmt_num(row.get('touch_loss_rv_15m'))} |"
        )

    lines += [
        "",
        "## Largest Win/Loss Feature Deltas",
        "",
        "| lock | feature | win mean | loss mean | loss - win |",
        "|---|---|---:|---:|---:|",
    ]
    for row in deltas[:25]:
        lines.append(
            f"| {row['lock_name']} | `{row['feature']}` | {fmt_num(row['win_mean'])} | "
            f"{fmt_num(row['loss_mean'])} | {fmt_num(row['loss_minus_win'])} |"
        )

    lines += [
        "",
        "## Worst Fresh Bins",
        "",
        "| lock | feature bin | group | markets | wins/losses | acc | net P&L | median ask |",
        "|---|---|---|---:|---:|---:|---:|---:|",
    ]
    for row in bins[:25]:
        lines.append(
            f"| {row['lock_name']} | `{row['group_col']}` | `{row['group']}` | {row['markets']} | "
            f"{row['wins']}/{row['losses']} | {pct(row['accuracy'])} | {fmt_cents(row['net_pnl_cents'])} | "
            f"{fmt_cents(row['median_ask'])} |"
        )

    lines += ["", "## Read", ""]
    touch = next((row for row in summary if row["lock_name"] == "touch_hazard"), None)
    if touch:
        lines.append(
            f"- Touch-hazard is the only lock currently positive or near positive in fresh settled P&L: "
            f"{touch['wins']}/{touch['losses']} on {touch['resolved']} resolved rows, {fmt_cents(touch['net_pnl_cents'])} net."
        )
    lines.append("- Treat the bin/delta sections as hypothesis generation only; fresh sample size is still too small for rule changes.")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    generated = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%SZ")
    rows = add_bins(load_registry())
    summary = lock_summary(rows)
    deltas = feature_deltas(rows)
    bins: List[Dict[str, Any]] = []
    for group_col in ["ask_bin", "margin_bin", "adverse15_bin", "touch_loss_bin"]:
        bins.extend(bin_rows(rows, group_col))
    md_latest = OUT_DIR / "profit_fresh_loss_attribution_latest.md"
    md_stamp = OUT_DIR / f"profit_fresh_loss_attribution_{generated}.md"
    json_latest = OUT_DIR / "profit_fresh_loss_attribution_latest.json"
    json_stamp = OUT_DIR / f"profit_fresh_loss_attribution_{generated}.json"
    csv_latest = OUT_DIR / "profit_fresh_loss_attribution_latest.csv"
    csv_stamp = OUT_DIR / f"profit_fresh_loss_attribution_{generated}.csv"
    write_report(md_latest, generated, rows, summary, deltas, bins)
    write_report(md_stamp, generated, rows, summary, deltas, bins)
    pd.DataFrame(bins).to_csv(csv_latest, index=False)
    pd.DataFrame(bins).to_csv(csv_stamp, index=False)
    payload = {
        "generated_utc": generated,
        "summary": summary,
        "feature_deltas": deltas,
        "bins": bins,
    }
    for path in [json_latest, json_stamp]:
        path.write_text(json.dumps(clean_json_local(payload), indent=2, sort_keys=True), encoding="utf-8")
    print("Profit fresh loss attribution complete")
    print(f"locks={len(summary)} resolved={int(rows['outcome_available'].sum())}")
    print(f"report={md_latest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
