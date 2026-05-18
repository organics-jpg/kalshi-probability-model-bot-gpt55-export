"""Stability audit for locked high-coverage profit candidates.

Backfilled profit can be dominated by a small regime, side, hour, or price
bucket. This diagnostic compares the locked high-coverage candidates on the
current heartbeat ledger and the independent v21 ledger, then surfaces the
worst supported slices.

Research-only: no orders are submitted and no bot files or live processes are
modified. This is not promotion evidence.
"""
from __future__ import annotations

import json
import math
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

import pandas as pd

from probe_cross_dataset_interval_frontier import load_v21_side_rows
from probe_cross_dataset_profit_frontier import enrich_selected, fmt_cents, fmt_roi, metrics_for
from probe_frontier_candidate_v2_diagnostic import select_policy as select_locked_policy
from probe_market_interval_80coverage import OUT_DIR, clean_json, load_side_rows, market_base, pct
from probe_profit_frontier_v2_fresh_validation import FRONTIER_V2_LOCK_PATH
from probe_v2_conditional_wait_forward_validation import (
    CONDITIONAL_WAIT_LOCK_PATH,
    ensure_lock as ensure_conditional_wait_lock,
    select_for_validation as select_conditional_wait_for_validation,
)
from probe_v2_rich_conditional_wait_forward_validation import (
    RICH_CONDITIONAL_WAIT_LOCK_PATH,
    ensure_lock as ensure_rich_conditional_wait_lock,
)


LOCKS = {
    "frontier_v2": FRONTIER_V2_LOCK_PATH,
    "book_margin": OUT_DIR / "profit_frontier_book_margin_lock.json",
    "book_margin_early": OUT_DIR / "profit_frontier_book_margin_early_lock.json",
    "book_margin_gap015": OUT_DIR / "profit_frontier_book_margin_gap015_lock.json",
    "score_min60": OUT_DIR / "profit_frontier_score_min60_lock.json",
    "score_min60_gap020": OUT_DIR / "profit_frontier_score_min60_gap020_lock.json",
}

CONDITIONAL_NAME = "v2_wait_score_min60_early"
RICH_CONDITIONAL_NAME = "v2_wait_score_min60_brownian70_early"
REPORT_MD = OUT_DIR / "profit_lock_candidate_stability_audit_latest.md"
REPORT_JSON = OUT_DIR / "profit_lock_candidate_stability_audit_latest.json"
SUMMARY_CSV = OUT_DIR / "profit_lock_candidate_stability_summary_latest.csv"
SLICE_CSV = OUT_DIR / "profit_lock_candidate_stability_slices_latest.csv"

MIN_SLICE_MARKETS = 8


def clean_json_local(value: Any) -> Any:
    if isinstance(value, pd.Timestamp):
        return value.isoformat()
    if isinstance(value, dict):
        return {str(k): clean_json_local(v) for k, v in value.items()}
    if isinstance(value, list):
        return [clean_json_local(v) for v in value]
    return clean_json(value)


def slice_bucket(value: Any, cuts: list[float], labels: list[str]) -> str:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return "NA"
    if not math.isfinite(number):
        return "NA"
    for cut, label in zip(cuts, labels):
        if number <= cut:
            return label
    return labels[-1]


def prepare_selected(dataset: str, side_rows: pd.DataFrame) -> tuple[pd.DataFrame, Dict[str, pd.DataFrame]]:
    base = market_base(side_rows)
    selected: Dict[str, pd.DataFrame] = {}
    for name in LOCKS:
        selected[name] = select_locked_policy(side_rows, base, name)
    if not CONDITIONAL_WAIT_LOCK_PATH.exists():
        ensure_conditional_wait_lock(side_rows)
    lock = json.loads(CONDITIONAL_WAIT_LOCK_PATH.read_text(encoding="utf-8"))
    selected[CONDITIONAL_NAME] = select_conditional_wait_for_validation(side_rows, base, lock)
    if not RICH_CONDITIONAL_WAIT_LOCK_PATH.exists():
        ensure_rich_conditional_wait_lock(side_rows)
    rich_lock = json.loads(RICH_CONDITIONAL_WAIT_LOCK_PATH.read_text(encoding="utf-8"))
    selected[RICH_CONDITIONAL_NAME] = select_conditional_wait_for_validation(side_rows, base, rich_lock)
    for name, frame in selected.items():
        if frame.empty:
            selected[name] = frame.copy()
            selected[name]["policy_name"] = name
        elif "policy_name" not in frame.columns:
            selected[name] = frame.copy()
            selected[name]["policy_name"] = name
    return base, selected


def summarize_metric(dataset: str, policy: str, base: pd.DataFrame, selected: pd.DataFrame) -> Dict[str, Any]:
    metrics = metrics_for(base, selected)
    row: Dict[str, Any] = {"dataset": dataset, "policy": policy}
    for split, values in metrics.items():
        for key, value in values.items():
            row[f"{split}_{key}"] = value
    val_net = float(metrics["validation"]["net_pnl_cents"] or 0.0)
    holdout_net = float(metrics["holdout"]["net_pnl_cents"] or 0.0)
    row["oos_positive"] = val_net > 0.0 and holdout_net > 0.0
    row["all_coverage_ok"] = (metrics["all"]["coverage"] or 0.0) >= 0.80
    return row


def add_slice_fields(frame: pd.DataFrame) -> pd.DataFrame:
    out = frame.copy()
    if out.empty:
        return out
    out["entry_dt"] = pd.to_datetime(out["entry_dt"], utc=True, errors="coerce")
    out["entry_hour_utc"] = out["entry_dt"].dt.hour.astype("Int64").astype(str)
    out["ask_bucket"] = [
        slice_bucket(value, [55, 65, 75, 85, 95], ["ask<=55", "ask<=65", "ask<=75", "ask<=85", "ask<=95", "ask>95"])
        for value in pd.to_numeric(out["ask_cents"], errors="coerce")
    ]
    out["time_bucket"] = [
        slice_bucket(value, [300, 600, 900], ["sec<=300", "sec<=600", "sec<=900", "sec>900"])
        for value in pd.to_numeric(out["seconds_to_close"], errors="coerce")
    ]
    return out


def summarize_slices(dataset: str, policy: str, selected: pd.DataFrame) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    frame = add_slice_fields(enrich_selected(selected))
    if frame.empty:
        return rows
    specs = [
        ("split", "split"),
        ("side", "side"),
        ("entry_hour_utc", "entry_hour_utc"),
        ("ask_bucket", "ask_bucket"),
        ("time_bucket", "time_bucket"),
    ]
    for group_type, col in specs:
        if col not in frame.columns:
            continue
        for group, part in frame.groupby(col, dropna=False, sort=True):
            n = int(len(part))
            if n == 0:
                continue
            wins = int(part["win"].sum())
            net = float(pd.to_numeric(part["net_pnl_cents"], errors="coerce").sum())
            rows.append(
                {
                    "dataset": dataset,
                    "policy": policy,
                    "group_type": group_type,
                    "group": str(group),
                    "markets": n,
                    "wins": wins,
                    "losses": n - wins,
                    "accuracy": wins / n if n else None,
                    "net_pnl_cents": net,
                    "net_per_market_cents": net / n if n else None,
                    "median_ask": float(pd.to_numeric(part["ask_cents"], errors="coerce").median()) if n else None,
                }
            )
    return rows


def write_report(generated: str, summary: pd.DataFrame, slices: pd.DataFrame) -> None:
    supported = slices[slices["markets"].ge(MIN_SLICE_MARKETS)].copy() if not slices.empty else slices
    worst = supported.sort_values("net_pnl_cents", ascending=True).head(20) if not supported.empty else supported
    lines = [
        "# Profit Lock Candidate Stability Audit",
        "",
        f"Generated UTC: `{generated}`",
        "",
        "## Scope",
        "",
        "- Research-only stability diagnostic; no orders are submitted and no bot files or live processes are touched.",
        "- Compares locked candidates on current and independent v21 ledgers.",
        "- Slice losses are diagnostic only; strict pre-registered live evidence remains the promotion gate.",
        "",
        "## Candidate Summary",
        "",
        "| dataset | policy | all net/ROI | all acc/cov | validation net | holdout net | OOS positive |",
        "|---|---|---:|---:|---:|---:|---|",
    ]
    for _, row in summary.sort_values(["dataset", "policy"]).iterrows():
        lines.append(
            f"| {row['dataset']} | `{row['policy']}` | "
            f"{fmt_cents(row['all_net_pnl_cents'])}/{fmt_roi(row['all_net_roi_on_cost'])} | "
            f"{pct(row['all_accuracy'])}/{pct(row['all_coverage'])} | "
            f"{fmt_cents(row['validation_net_pnl_cents'])} | {fmt_cents(row['holdout_net_pnl_cents'])} | "
            f"{bool(row['oos_positive'])} |"
        )

    lines += [
        "",
        f"## Worst Supported Slices",
        "",
        f"Only slices with at least `{MIN_SLICE_MARKETS}` markets are shown.",
        "",
        "| dataset | policy | slice | markets | wins/losses | net | net/market | median ask |",
        "|---|---|---|---:|---:|---:|---:|---:|",
    ]
    if worst.empty:
        lines.append("| none | none | none | 0 | 0/0 | 0.0c | 0.0c | NA |")
    else:
        for _, row in worst.iterrows():
            lines.append(
                f"| {row['dataset']} | `{row['policy']}` | {row['group_type']}=`{row['group']}` | "
                f"{int(row['markets'])} | {int(row['wins'])}/{int(row['losses'])} | "
                f"{fmt_cents(row['net_pnl_cents'])} | {fmt_cents(row['net_per_market_cents'])} | "
                f"{fmt_cents(row['median_ask'])} |"
            )

    lines += ["", "## Read", ""]
    for policy in sorted(summary["policy"].unique()):
        part = summary[summary["policy"].eq(policy)]
        oos_ok = bool(part["oos_positive"].all()) if not part.empty else False
        cov_ok = bool(part["all_coverage_ok"].all()) if not part.empty else False
        supported_losses = supported[
            supported["policy"].eq(policy) & supported["net_pnl_cents"].lt(0.0)
        ] if not supported.empty else supported
        lines.append(
            f"- `{policy}` coverage/OOS-positive/stressed-loss slices: "
            f"{cov_ok}/{oos_ok}/{len(supported_losses)}."
        )
    lines.append("- Candidates with supported losing slices or cross-dataset giveback should stay forward-test only.")

    REPORT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    generated = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%SZ")
    rows: List[Dict[str, Any]] = []
    slice_rows: List[Dict[str, Any]] = []
    for dataset, loader in [("current", load_side_rows), ("v21", load_v21_side_rows)]:
        side_rows = loader()
        base, selected = prepare_selected(dataset, side_rows)
        for policy, frame in selected.items():
            rows.append(summarize_metric(dataset, policy, base, frame))
            slice_rows.extend(summarize_slices(dataset, policy, frame))
    summary = pd.DataFrame(rows)
    slices = pd.DataFrame(slice_rows)
    summary.to_csv(SUMMARY_CSV, index=False)
    slices.to_csv(SLICE_CSV, index=False)
    stamp_summary = OUT_DIR / f"profit_lock_candidate_stability_summary_{generated}.csv"
    stamp_slices = OUT_DIR / f"profit_lock_candidate_stability_slices_{generated}.csv"
    summary.to_csv(stamp_summary, index=False)
    slices.to_csv(stamp_slices, index=False)
    payload = {
        "generated_utc": generated,
        "min_slice_markets": MIN_SLICE_MARKETS,
        "summary": clean_json_local(summary.to_dict(orient="records")),
        "slices": clean_json_local(slices.to_dict(orient="records")),
    }
    json_stamp = OUT_DIR / f"profit_lock_candidate_stability_audit_{generated}.json"
    for path in [REPORT_JSON, json_stamp]:
        path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    md_stamp = OUT_DIR / f"profit_lock_candidate_stability_audit_{generated}.md"
    write_report(generated, summary, slices)
    md_stamp.write_text(REPORT_MD.read_text(encoding="utf-8"), encoding="utf-8")
    print("Profit lock candidate stability audit complete")
    print(f"candidates={len(summary)} slices={len(slices)}")
    print(f"report={REPORT_MD}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
