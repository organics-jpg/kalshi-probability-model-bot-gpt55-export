"""Diagnostic for v2 versus touch-geometry disagreement.

Recent strict cases show that the high-coverage Brownian v2 side can be wrong
when local touch/path geometry points the other way. This probe asks whether
that disagreement is a broad physical signal or just a few memorable cases.

Research-only: no orders are submitted and no bot files or live processes are
modified.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any, Dict, List

import pandas as pd

from probe_cross_dataset_interval_frontier import load_v21_side_rows
from probe_cross_dataset_profit_frontier import enrich_selected, fmt_cents, fmt_roi
from probe_market_interval_80coverage import (
    OUT_DIR,
    choose_decision_sides,
    clean_json,
    load_side_rows,
    market_base,
    pct,
    select_markets_from_chosen,
)
from probe_profit_frontier_fresh_validation import policy_from_record as base_policy_from_record
from probe_profit_frontier_v2_fresh_validation import FRONTIER_V2_LOCK_PATH
from probe_profit_touch_hazard_fresh_validation import TOUCH_LOCK_PATH, policy_from_record as touch_policy_from_record
from probe_profit_touch_hazard_frontier import add_touch_hazard_scores, gate_mask as touch_gate_mask


REPORT_MD = OUT_DIR / "v2_touch_disagreement_diagnostic_latest.md"
REPORT_JSON = OUT_DIR / "v2_touch_disagreement_diagnostic_latest.json"
REPORT_CSV = OUT_DIR / "v2_touch_disagreement_diagnostic_latest.csv"


def clean_json_local(value: Any) -> Any:
    if isinstance(value, pd.Timestamp):
        return value.isoformat()
    if isinstance(value, dict):
        return {str(k): clean_json_local(v) for k, v in value.items()}
    if isinstance(value, list):
        return [clean_json_local(v) for v in value]
    return clean_json(value)


def select_base(side_rows: pd.DataFrame, base: pd.DataFrame) -> pd.DataFrame:
    lock = json.loads(FRONTIER_V2_LOCK_PATH.read_text(encoding="utf-8"))
    policy = base_policy_from_record(lock["policy"])
    rows = side_rows.merge(base[["market", "split"]], on="market", how="inner")
    chosen = choose_decision_sides(rows, policy.chooser)
    return enrich_selected(select_markets_from_chosen(chosen, policy))


def select_touch(side_rows: pd.DataFrame, base: pd.DataFrame) -> pd.DataFrame:
    lock = json.loads(TOUCH_LOCK_PATH.read_text(encoding="utf-8"))
    policy = touch_policy_from_record(lock["policy"])
    rows = side_rows.merge(base[["market", "split"]], on="market", how="inner")
    chosen = choose_decision_sides(rows, policy.chooser)
    selected = chosen[touch_gate_mask(chosen, policy)].copy()
    if selected.empty:
        return enrich_selected(selected)
    selected = (
        selected.sort_values(["market", "entry_dt"])
        .groupby("market", as_index=False, sort=False)
        .first()
        .sort_values(["entry_dt", "market"])
        .reset_index(drop=True)
    )
    return enrich_selected(selected)


def paired_rows(side_rows: pd.DataFrame) -> pd.DataFrame:
    side_rows = add_touch_hazard_scores(side_rows)
    base = market_base(side_rows)
    v2 = select_base(side_rows, base)
    touch = select_touch(side_rows, base)
    cols = [
        "market",
        "split",
        "side",
        "entry_dt",
        "ask_cents",
        "outcome",
        "outcome_available",
        "win",
        "net_pnl_cents",
    ]
    pair = v2[cols].merge(touch[cols], on=["market", "split"], suffixes=("_v2", "_touch"))
    pair["disagree"] = pair["side_v2"].astype(str) != pair["side_touch"].astype(str)
    pair["touch_minus_v2_cents"] = pd.to_numeric(pair["net_pnl_cents_touch"], errors="coerce") - pd.to_numeric(pair["net_pnl_cents_v2"], errors="coerce")
    pair["v2_win"] = pair["win_v2"].fillna(False).astype(bool)
    pair["touch_win"] = pair["win_touch"].fillna(False).astype(bool)
    return pair


def metric(pair: pd.DataFrame, split: str, disagree: bool | None) -> Dict[str, Any]:
    part = pair if split == "all" else pair[pair["split"] == split]
    if disagree is not None:
        part = part[part["disagree"].eq(disagree)]
    n = int(len(part))
    v2_net = float(pd.to_numeric(part["net_pnl_cents_v2"], errors="coerce").sum()) if n else 0.0
    touch_net = float(pd.to_numeric(part["net_pnl_cents_touch"], errors="coerce").sum()) if n else 0.0
    return {
        "rows": n,
        "v2_wins": int(part["v2_win"].sum()) if n else 0,
        "touch_wins": int(part["touch_win"].sum()) if n else 0,
        "v2_accuracy": float(part["v2_win"].mean()) if n else None,
        "touch_accuracy": float(part["touch_win"].mean()) if n else None,
        "v2_net_pnl_cents": v2_net,
        "touch_net_pnl_cents": touch_net,
        "touch_minus_v2_cents": touch_net - v2_net,
        "mean_touch_minus_v2_cents": (touch_net - v2_net) / n if n else None,
    }


def metrics_for(pair: pd.DataFrame) -> Dict[str, Dict[str, Any]]:
    out: Dict[str, Dict[str, Any]] = {}
    for split in ["all", "train", "validation", "holdout"]:
        out[f"{split}_all_pairs"] = metric(pair, split, None)
        out[f"{split}_agree"] = metric(pair, split, False)
        out[f"{split}_disagree"] = metric(pair, split, True)
    return out


def flatten(dataset: str, metrics: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
    row: Dict[str, Any] = {"dataset": dataset}
    for name, values in metrics.items():
        for key, value in values.items():
            row[f"{name}_{key}"] = value
    return row


def write_report(generated: str, current: Dict[str, Dict[str, Any]], v21: Dict[str, Dict[str, Any]]) -> None:
    lines: List[str] = [
        "# V2 Touch-Disagreement Diagnostic",
        "",
        f"Generated UTC: `{generated}`",
        "",
        "## Scope",
        "",
        "- Research-only diagnostic; no orders are submitted and no bot files or live processes are touched.",
        "- Compares v2 first selected side against the locked touch-hazard first selected side on markets where both select.",
        "- This is not forward promotion evidence; it tests whether touch disagreement is physically informative.",
        "",
        "## Metrics",
        "",
        "| dataset | bucket | rows | v2 acc/net | touch acc/net | touch-v2 delta | mean delta |",
        "|---|---|---:|---:|---:|---:|---:|",
    ]
    for dataset, metrics in [("current", current), ("v21", v21)]:
        for bucket in ["all_pairs", "agree", "disagree"]:
            row = metrics[f"all_{bucket}"]
            lines.append(
                f"| {dataset} | {bucket} | {row['rows']} | "
                f"{pct(row['v2_accuracy'])}/{fmt_cents(row['v2_net_pnl_cents'])} | "
                f"{pct(row['touch_accuracy'])}/{fmt_cents(row['touch_net_pnl_cents'])} | "
                f"{fmt_cents(row['touch_minus_v2_cents'])} | {fmt_cents(row['mean_touch_minus_v2_cents'])} |"
            )
    lines += [
        "",
        "## Read",
        "",
    ]
    cur_dis = current["all_disagree"]
    v21_dis = v21["all_disagree"]
    if cur_dis["rows"] and v21_dis["rows"]:
        lines.append(
            f"- Disagreement delta current/v21: {fmt_cents(cur_dis['touch_minus_v2_cents'])}/"
            f"{fmt_cents(v21_dis['touch_minus_v2_cents'])} across {cur_dis['rows']}/{v21_dis['rows']} paired markets."
        )
        if cur_dis["touch_minus_v2_cents"] > 0 and v21_dis["touch_minus_v2_cents"] > 0:
            lines.append("- Touch disagreement is directionally informative on both datasets, but still needs a tradable price/coverage rule.")
        else:
            lines.append("- Touch disagreement is not robustly positive across both datasets.")
    else:
        lines.append("- Not enough disagreement rows to evaluate.")
    REPORT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    generated = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%SZ")
    current_pair = paired_rows(load_side_rows())
    v21_pair = paired_rows(load_v21_side_rows())
    current_metrics = metrics_for(current_pair)
    v21_metrics = metrics_for(v21_pair)
    rows = [flatten("current", current_metrics), flatten("v21", v21_metrics)]
    pd.DataFrame(rows).to_csv(REPORT_CSV, index=False)
    REPORT_JSON.write_text(
        json.dumps(
            {
                "generated_utc": generated,
                "current_metrics": clean_json_local(current_metrics),
                "v21_metrics": clean_json_local(v21_metrics),
            },
            indent=2,
            sort_keys=True,
        ),
        encoding="utf-8",
    )
    write_report(generated, current_metrics, v21_metrics)
    print("V2 touch-disagreement diagnostic complete")
    print(f"current_pairs={len(current_pair)} v21_pairs={len(v21_pair)}")
    print(f"report={REPORT_MD}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
