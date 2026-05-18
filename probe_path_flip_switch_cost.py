"""Switch-cost check for the path-flip override diagnostic.

The path-flip override scan is an upper bound because it keeps the early v2 row
when no flip appears but replaces it with the late opposite row when a flip
does appear. A live implementation would either wait, or enter v2 first and
pay to exit/reverse. This probe tests the second interpretation with local fee
estimates and contemporaneous bid prices from the opposite side row.

Research-only: no orders are submitted and no bot files or live processes are
modified.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any, Dict, List

import numpy as np
import pandas as pd

from probe_cross_dataset_interval_frontier import load_v21_side_rows
from probe_cross_dataset_profit_frontier import enrich_selected, estimated_order_fee_cents, fmt_cents, fmt_roi
from probe_market_interval_80coverage import (
    MARKET_COVERAGE_FLOOR,
    MIN_HOLDOUT_SELECTED_MARKETS,
    MIN_SELECTED_MARKETS,
    OUT_DIR,
    choose_decision_sides,
    clean_json,
    load_side_rows,
    market_base,
    pct,
)
from probe_path_flip_override_frontier import BASE_CHOOSER, FlipPolicy, base_selected, make_policies


REPORT_MD = OUT_DIR / "path_flip_switch_cost_latest.md"
REPORT_JSON = OUT_DIR / "path_flip_switch_cost_latest.json"
REPORT_CSV = OUT_DIR / "path_flip_switch_cost_latest.csv"


def clean_json_local(value: Any) -> Any:
    if isinstance(value, pd.Timestamp):
        return value.isoformat()
    if isinstance(value, dict):
        return {str(k): clean_json_local(v) for k, v in value.items()}
    if isinstance(value, list):
        return [clean_json_local(v) for v in value]
    return clean_json(value)


def prepare(side_rows: pd.DataFrame, base: pd.DataFrame) -> tuple[pd.DataFrame, Dict[str, pd.DataFrame], Dict[tuple[str, str], float]]:
    rows = side_rows.merge(base[["market", "split"]], on="market", how="inner")
    choosers = sorted({BASE_CHOOSER, *[policy.override_chooser for policy in make_policies()]})
    chosen = {chooser: choose_decision_sides(rows, chooser) for chooser in choosers}
    exit_bid_lookup: Dict[tuple[str, str], float] = {}
    if "decision_key" in rows.columns:
        work = rows[["decision_key", "side", "bid_cents"]].copy()
        work["bid_cents"] = pd.to_numeric(work["bid_cents"], errors="coerce")
        for _, row in work.dropna(subset=["decision_key", "side", "bid_cents"]).iterrows():
            exit_bid_lookup[(str(row["decision_key"]), str(row["side"]))] = float(row["bid_cents"])
    return rows, chosen, exit_bid_lookup


def grouped_override(chosen: pd.DataFrame, policy: FlipPolicy) -> Dict[str, pd.DataFrame]:
    override = chosen.copy()
    override["entry_dt"] = pd.to_datetime(override["entry_dt"], utc=True, errors="coerce")
    override["seconds_to_close"] = pd.to_numeric(override["seconds_to_close"], errors="coerce")
    override["ask_cents"] = pd.to_numeric(override["ask_cents"], errors="coerce")
    override[policy.override_chooser] = pd.to_numeric(override[policy.override_chooser], errors="coerce")
    return {str(market): part.sort_values("entry_dt").reset_index(drop=True) for market, part in override.groupby("market", sort=False)}


def select_with_switch_cost(
    base_rows: pd.DataFrame,
    override_chosen: pd.DataFrame,
    exit_bid_lookup: Dict[tuple[str, str], float],
    policy: FlipPolicy,
) -> pd.DataFrame:
    groups = grouped_override(override_chosen, policy)
    selected: List[pd.Series] = []
    for _, base in base_rows.sort_values(["market", "entry_dt"]).iterrows():
        base_dt = pd.to_datetime(base["entry_dt"], utc=True, errors="coerce")
        base_ask = float(base["ask_cents"])
        group = groups.get(str(base["market"]))
        if group is None or group.empty:
            chosen = base.copy()
            chosen["override_used"] = False
            selected.append(chosen)
            continue
        pool = group[
            group["side"].ne(base["side"])
            & group["entry_dt"].ge(base_dt + pd.Timedelta(seconds=policy.min_delay_sec))
            & group[policy.override_chooser].ge(policy.min_override_score)
            & group["ask_cents"].le(policy.override_ask_max)
            & group["seconds_to_close"].ge(120.0)
            & group["seconds_to_close"].le(policy.max_seconds_to_close)
        ].copy()
        if policy.max_ask_worse is not None:
            pool = pool[pool["ask_cents"].le(base_ask + policy.max_ask_worse)].copy()
        if pool.empty:
            chosen = base.copy()
            chosen["override_used"] = False
            selected.append(chosen)
            continue
        chosen = pool.iloc[0].copy()
        chosen["override_used"] = True
        chosen["base_side"] = base["side"]
        chosen["base_ask_cents"] = base_ask
        chosen["base_entry_fee_cents"] = estimated_order_fee_cents(base_ask, 1)
        chosen["base_entry_dt"] = base_dt
        chosen["base_exit_bid_cents"] = exit_bid_lookup.get((str(chosen.get("decision_key")), str(base["side"])), np.nan)
        selected.append(chosen)
    out = pd.DataFrame(selected).sort_values(["entry_dt", "market"]).reset_index(drop=True)
    out = enrich_selected(out)
    out["switch_net_pnl_cents"] = out["net_pnl_cents"]
    out["switch_cost_cents"] = out["entry_cost_cents"]
    if "override_used" in out.columns:
        mask = out["override_used"].fillna(False).astype(bool)
        for idx, row in out.loc[mask].iterrows():
            exit_bid = pd.to_numeric(pd.Series([row.get("base_exit_bid_cents")]), errors="coerce").iloc[0]
            if pd.isna(exit_bid):
                out.at[idx, "switch_net_pnl_cents"] = np.nan
                out.at[idx, "switch_cost_cents"] = np.nan
                continue
            base_ask = float(row["base_ask_cents"])
            base_fee = int(row["base_entry_fee_cents"])
            exit_fee = estimated_order_fee_cents(float(exit_bid), 1)
            initial_leg = float(exit_bid) - base_ask - base_fee - exit_fee
            out.at[idx, "switch_net_pnl_cents"] = initial_leg + float(row["net_pnl_cents"])
            out.at[idx, "switch_cost_cents"] = base_ask + base_fee + float(row["entry_cost_cents"])
    return out


def switch_metrics(base: pd.DataFrame, selected: pd.DataFrame) -> Dict[str, Dict[str, Any]]:
    out: Dict[str, Dict[str, Any]] = {}
    for split in ["all", "train", "validation", "holdout"]:
        base_part = base if split == "all" else base[base["split"] == split]
        part = selected if split == "all" else selected[selected["split"] == split]
        n = int(len(part))
        net = float(pd.to_numeric(part["switch_net_pnl_cents"], errors="coerce").sum()) if n else 0.0
        cost = float(pd.to_numeric(part["switch_cost_cents"], errors="coerce").sum()) if n else 0.0
        wins = int(part["win"].sum()) if n and "win" in part.columns else 0
        out[split] = {
            "base_markets": int(len(base_part)),
            "markets": n,
            "wins": wins,
            "losses": n - wins,
            "accuracy": wins / n if n else None,
            "coverage": n / len(base_part) if len(base_part) else None,
            "switch_net_pnl_cents": net,
            "switch_cost_cents": cost,
            "switch_roi_on_cost": net / cost if cost else None,
            "overrides": int(part["override_used"].fillna(False).astype(bool).sum()) if n and "override_used" in part.columns else 0,
        }
    return out


def coverage_pass(metrics: Dict[str, Dict[str, Any]]) -> bool:
    return (
        all((metrics[split]["coverage"] or 0.0) >= MARKET_COVERAGE_FLOOR for split in ["all", "train", "validation", "holdout"])
        and metrics["all"]["markets"] >= MIN_SELECTED_MARKETS
        and metrics["holdout"]["markets"] >= MIN_HOLDOUT_SELECTED_MARKETS
    )


def oos_positive(metrics: Dict[str, Dict[str, Any]]) -> bool:
    return all((metrics[split]["switch_net_pnl_cents"] or 0.0) > 0.0 for split in ["validation", "holdout"])


def flatten(policy: FlipPolicy, current: Dict[str, Dict[str, Any]], v21: Dict[str, Dict[str, Any]], base_current: float, base_v21: float) -> Dict[str, Any]:
    row: Dict[str, Any] = {
        "label": policy.label,
        "override_chooser": policy.override_chooser,
        "min_override_score": policy.min_override_score,
        "override_ask_max": policy.override_ask_max,
        "min_delay_sec": policy.min_delay_sec,
        "max_seconds_to_close": policy.max_seconds_to_close,
        "max_ask_worse": policy.max_ask_worse,
        "current_coverage_pass": coverage_pass(current),
        "v21_coverage_pass": coverage_pass(v21),
        "both_coverage_pass": coverage_pass(current) and coverage_pass(v21),
        "current_oos_positive": oos_positive(current),
        "v21_oos_positive": oos_positive(v21),
        "both_oos_positive": oos_positive(current) and oos_positive(v21),
        "current_delta_vs_v2_cents": current["all"]["switch_net_pnl_cents"] - base_current,
        "v21_delta_vs_v2_cents": v21["all"]["switch_net_pnl_cents"] - base_v21,
    }
    row["combined_delta_vs_v2_cents"] = row["current_delta_vs_v2_cents"] + row["v21_delta_vs_v2_cents"]
    row["min_oos_switch_roi"] = min(
        current["validation"]["switch_roi_on_cost"] or -1.0,
        current["holdout"]["switch_roi_on_cost"] or -1.0,
        v21["validation"]["switch_roi_on_cost"] or -1.0,
        v21["holdout"]["switch_roi_on_cost"] or -1.0,
    )
    for prefix, metrics in [("current", current), ("v21", v21)]:
        for split, values in metrics.items():
            for key, value in values.items():
                row[f"{prefix}_{split}_{key}"] = value
    return row


def write_report(generated: str, rows: pd.DataFrame, selected_by_label: Dict[str, pd.DataFrame], base_current: float, base_v21: float) -> None:
    top = rows[rows["both_coverage_pass"]].copy()
    top = top.sort_values(
        ["both_oos_positive", "combined_delta_vs_v2_cents", "min_oos_switch_roi"],
        ascending=[False, False, False],
    ).head(20)
    lines = [
        "# Path-Flip Switch-Cost Check",
        "",
        f"Generated UTC: `{generated}`",
        "",
        "## Scope",
        "",
        "- Research-only check; no orders are submitted and no bot files or live processes are touched.",
        "- Charges an early v2 entry, exit at contemporaneous bid, and late opposite-side entry when an override appears.",
        "- This is closer to tradable managed P&L than the replacement-only flip diagnostic.",
        "",
        "## Baseline",
        "",
        f"- Current v2 held-to-settlement baseline: {fmt_cents(base_current)}",
        f"- V21 v2 held-to-settlement baseline: {fmt_cents(base_v21)}",
        "",
        "## Summary",
        "",
        f"- Policies scanned: {len(rows)}",
        f"- Both-dataset 80% coverage policies: {int(rows['both_coverage_pass'].sum())}",
        f"- Both-dataset switch-cost OOS-positive policies: {int((rows['both_coverage_pass'] & rows['both_oos_positive']).sum())}",
        "",
        "## Top Rows",
        "",
        "| rank | policy | switch delta current/v21 | overrides current/v21 | switch net current/v21 | OOS ROI floor |",
        "|---:|---|---:|---:|---:|---:|",
    ]
    for rank, (_, row) in enumerate(top.iterrows(), start=1):
        lines.append(
            f"| {rank} | `{row['label']}` | "
            f"{fmt_cents(row['current_delta_vs_v2_cents'])}/{fmt_cents(row['v21_delta_vs_v2_cents'])} | "
            f"{int(row['current_all_overrides'])}/{int(row['v21_all_overrides'])} | "
            f"{fmt_cents(row['current_all_switch_net_pnl_cents'])}/{fmt_cents(row['v21_all_switch_net_pnl_cents'])} | "
            f"{fmt_roi(row['min_oos_switch_roi'])} |"
        )
    lines += [
        "",
        "## 14:30 UTC Split Case",
        "",
        "| policy | final side | ask | final net | switch net | override |",
        "|---|---|---:|---:|---:|---|",
    ]
    split_market = "KXBTC15M-26MAY031030-30"
    for _, row in top.head(8).iterrows():
        selected = selected_by_label.get(row["label"], pd.DataFrame())
        hit = selected[selected["market"].eq(split_market)] if not selected.empty else selected
        if hit.empty:
            lines.append(f"| `{row['label']}` | skipped |  |  |  |  |")
            continue
        item = hit.iloc[0]
        lines.append(
            f"| `{row['label']}` | {item.get('side')} | {fmt_cents(item.get('ask_cents'))} | "
            f"{fmt_cents(item.get('net_pnl_cents'))} | {fmt_cents(item.get('switch_net_pnl_cents'))} | "
            f"{bool(item.get('override_used'))} |"
        )
    lines += ["", "## Read", ""]
    if top.empty:
        lines.append("- No switch-cost row preserved coverage.")
    else:
        best = top.iloc[0]
        lines.append(
            f"- Best switch-cost row: `{best['label']}` with current/v21 delta "
            f"{fmt_cents(best['current_delta_vs_v2_cents'])}/{fmt_cents(best['v21_delta_vs_v2_cents'])}."
        )
        if bool(best["both_oos_positive"]):
            lines.append("- This is stronger than the replacement-only diagnostic, but still needs a forward lock before promotion.")
        else:
            lines.append("- Switch costs break the apparent edge; do not lock the flip override.")
    REPORT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    generated = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%SZ")
    current_side = load_side_rows()
    v21_side = load_v21_side_rows()
    current_base = market_base(current_side)
    v21_base = market_base(v21_side)
    _, current_chosen, current_exit_bid = prepare(current_side, current_base)
    _, v21_chosen, v21_exit_bid = prepare(v21_side, v21_base)
    current_base_rows = base_selected(current_chosen[BASE_CHOOSER])
    v21_base_rows = base_selected(v21_chosen[BASE_CHOOSER])
    current_base_selected = enrich_selected(current_base_rows)
    v21_base_selected = enrich_selected(v21_base_rows)
    base_current = float(current_base_selected["net_pnl_cents"].sum())
    base_v21 = float(v21_base_selected["net_pnl_cents"].sum())

    rows: List[Dict[str, Any]] = []
    selected_by_label: Dict[str, pd.DataFrame] = {}
    for policy in make_policies():
        current_selected = select_with_switch_cost(current_base_rows, current_chosen[policy.override_chooser], current_exit_bid, policy)
        v21_selected = select_with_switch_cost(v21_base_rows, v21_chosen[policy.override_chooser], v21_exit_bid, policy)
        current_metrics = switch_metrics(current_base, current_selected)
        v21_metrics = switch_metrics(v21_base, v21_selected)
        row = flatten(policy, current_metrics, v21_metrics, base_current, base_v21)
        rows.append(row)
        if row["both_coverage_pass"]:
            selected_by_label[row["label"]] = current_selected
    df = pd.DataFrame(rows)
    df.to_csv(REPORT_CSV, index=False)
    REPORT_JSON.write_text(
        json.dumps({"generated_utc": generated, "rows": clean_json_local(df.to_dict(orient="records"))}, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    write_report(generated, df, selected_by_label, base_current, base_v21)
    print("Path-flip switch-cost check complete")
    print(f"policies={len(df)} coverage_pass={int(df['both_coverage_pass'].sum())}")
    print(f"report={REPORT_MD}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
