"""Robustness audit for the Brownian-70 high-coverage profit candidate.

The refreshed cross-dataset profit frontier currently favors a pure
Brownian/RV15 policy. This audit keeps that hypothesis separate from the live
bot and asks whether it is stable enough to justify a separate future lock.

Research-only: no orders are submitted and no bot files or live processes are
modified.
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
from probe_market_interval_80coverage import (
    OUT_DIR,
    Policy,
    choose_decision_sides,
    clean_json,
    load_side_rows,
    market_base,
    pct,
    select_markets_from_chosen,
)


REPORT_MD = OUT_DIR / "brownian70_candidate_robustness_audit_latest.md"
REPORT_JSON = OUT_DIR / "brownian70_candidate_robustness_audit_latest.json"
SUMMARY_CSV = OUT_DIR / "brownian70_candidate_robustness_summary_latest.csv"
BLOCK_CSV = OUT_DIR / "brownian70_candidate_robustness_blocks_latest.csv"
SLICE_CSV = OUT_DIR / "brownian70_candidate_robustness_slices_latest.csv"
HISTORY_CSV = OUT_DIR / "brownian70_candidate_robustness_history_latest.csv"

BLOCK_MARKETS = 20
MIN_BLOCK_MARKETS = 10
MIN_SLICE_MARKETS = 12
COVERAGE_FLOOR = 0.80
POSITIVE_BLOCK_RATE_FLOOR = 0.70


CANDIDATES = {
    "brownian70_sec120": Policy("brownian_p_rv_15m", 0.70, 95.0, 120.0, "none"),
    "brownian70_sec60": Policy("brownian_p_rv_15m", 0.70, 95.0, 60.0, "none"),
    "brownian70_ask90_sec120": Policy("brownian_p_rv_15m", 0.70, 90.0, 120.0, "none"),
    "score_min60_lock_equiv": Policy("score_min_book_rv15", 0.60, 95.0, 120.0, "none"),
}


def clean_json_local(value: Any) -> Any:
    if isinstance(value, pd.Timestamp):
        return value.isoformat()
    if isinstance(value, dict):
        return {str(k): clean_json_local(v) for k, v in value.items()}
    if isinstance(value, list):
        return [clean_json_local(v) for v in value]
    return clean_json(value)


def select_for_policy(side_rows: pd.DataFrame, base: pd.DataFrame, policy: Policy) -> pd.DataFrame:
    rows = side_rows.drop(columns=["split"], errors="ignore").merge(base[["market", "split"]], on="market", how="inner")
    chosen = choose_decision_sides(rows, policy.chooser)
    return enrich_selected(select_markets_from_chosen(chosen, policy))


def flatten_summary(dataset: str, name: str, policy: Policy, base: pd.DataFrame, selected: pd.DataFrame) -> Dict[str, Any]:
    metrics = metrics_for(base, selected)
    row: Dict[str, Any] = {
        "dataset": dataset,
        "candidate": name,
        "label": policy.label,
    }
    for split, values in metrics.items():
        for key, value in values.items():
            row[f"{split}_{key}"] = value
    row["coverage_pass"] = all((metrics[split]["coverage"] or 0.0) >= COVERAGE_FLOOR for split in ["all", "train", "validation", "holdout"])
    row["all_splits_positive"] = all((metrics[split]["net_pnl_cents"] or 0.0) > 0.0 for split in ["all", "train", "validation", "holdout"])
    row["oos_positive"] = all((metrics[split]["net_pnl_cents"] or 0.0) > 0.0 for split in ["validation", "holdout"])
    return row


def block_base(base: pd.DataFrame) -> pd.DataFrame:
    out = base.copy()
    out["close_dt"] = pd.to_datetime(out["close_dt"], utc=True, errors="coerce")
    out = out.sort_values(["close_dt", "market"]).reset_index(drop=True)
    out["block_index"] = out.index // BLOCK_MARKETS
    return out


def block_rows(dataset: str, name: str, base: pd.DataFrame, selected: pd.DataFrame) -> List[Dict[str, Any]]:
    base_blocks = block_base(base)
    if selected.empty:
        selected_blocks = selected.copy()
    else:
        selected_blocks = selected.drop(columns=["block_index"], errors="ignore").merge(
            base_blocks[["market", "block_index"]], on="market", how="inner"
        )
    rows: List[Dict[str, Any]] = []
    for block_index, block in base_blocks.groupby("block_index", sort=True):
        part = selected_blocks[selected_blocks["block_index"].eq(block_index)] if not selected_blocks.empty else selected_blocks
        n = int(len(part))
        wins = int(part["win"].astype(bool).sum()) if n else 0
        net = float(pd.to_numeric(part.get("net_pnl_cents"), errors="coerce").sum()) if n else 0.0
        cost = float(pd.to_numeric(part.get("entry_cost_cents"), errors="coerce").sum()) if n else 0.0
        base_n = int(len(block))
        rows.append(
            {
                "dataset": dataset,
                "candidate": name,
                "block_index": int(block_index),
                "block_start_close_dt": pd.to_datetime(block["close_dt"].min(), utc=True, errors="coerce"),
                "block_end_close_dt": pd.to_datetime(block["close_dt"].max(), utc=True, errors="coerce"),
                "base_markets": base_n,
                "selected_markets": n,
                "coverage": n / base_n if base_n else None,
                "wins": wins,
                "losses": n - wins,
                "accuracy": wins / n if n else None,
                "net_pnl_cents": net,
                "net_roi_on_cost": net / cost if cost else None,
                "median_ask": float(pd.to_numeric(part.get("ask_cents"), errors="coerce").median()) if n else None,
                "positive_net": net > 0.0,
                "coverage_pass": (n / base_n if base_n else 0.0) >= COVERAGE_FLOOR,
            }
        )
    return rows


def bucket(value: Any, cuts: list[float], labels: list[str]) -> str:
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


def slice_rows(dataset: str, name: str, selected: pd.DataFrame) -> List[Dict[str, Any]]:
    if selected.empty:
        return []
    frame = selected.copy()
    frame["entry_dt"] = pd.to_datetime(frame["entry_dt"], utc=True, errors="coerce")
    frame["entry_hour_utc"] = frame["entry_dt"].dt.hour.astype("Int64").astype(str)
    frame["ask_bucket"] = [
        bucket(value, [65, 75, 85, 95], ["ask<=65", "ask<=75", "ask<=85", "ask<=95", "ask>95"])
        for value in pd.to_numeric(frame["ask_cents"], errors="coerce")
    ]
    frame["time_bucket"] = [
        bucket(value, [300, 600, 900], ["sec<=300", "sec<=600", "sec<=900", "sec>900"])
        for value in pd.to_numeric(frame["seconds_to_close"], errors="coerce")
    ]
    out: List[Dict[str, Any]] = []
    for group_type, col in [("split", "split"), ("side", "side"), ("hour", "entry_hour_utc"), ("ask", "ask_bucket"), ("time", "time_bucket")]:
        for group, part in frame.groupby(col, dropna=False, sort=True):
            n = int(len(part))
            wins = int(part["win"].astype(bool).sum())
            net = float(pd.to_numeric(part["net_pnl_cents"], errors="coerce").sum())
            out.append(
                {
                    "dataset": dataset,
                    "candidate": name,
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
    return out


def history_rows() -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    labels = {name: policy.label for name, policy in CANDIDATES.items()}
    for path in sorted(OUT_DIR.glob("cross_dataset_profit_frontier_*.csv")):
        try:
            frame = pd.read_csv(path)
        except Exception:
            continue
        for name, label in labels.items():
            part = frame[frame["label"].eq(label)]
            if part.empty:
                continue
            row = part.iloc[0]
            rows.append(
                {
                    "file": path.name,
                    "candidate": name,
                    "current_all_net_pnl_cents": row.get("current_all_net_pnl_cents"),
                    "current_validation_net_pnl_cents": row.get("current_validation_net_pnl_cents"),
                    "current_holdout_net_pnl_cents": row.get("current_holdout_net_pnl_cents"),
                    "v21_all_net_pnl_cents": row.get("v21_all_net_pnl_cents"),
                    "v21_train_net_pnl_cents": row.get("v21_train_net_pnl_cents"),
                    "v21_validation_net_pnl_cents": row.get("v21_validation_net_pnl_cents"),
                    "v21_holdout_net_pnl_cents": row.get("v21_holdout_net_pnl_cents"),
                }
            )
    return rows


def write_report(generated: str, summary: pd.DataFrame, blocks: pd.DataFrame, slices: pd.DataFrame, history: pd.DataFrame) -> None:
    block_summary_rows: List[Dict[str, Any]] = []
    supported_blocks = blocks[blocks["base_markets"].ge(MIN_BLOCK_MARKETS)].copy() if not blocks.empty else blocks
    for (dataset, candidate), part in supported_blocks.groupby(["dataset", "candidate"], sort=True):
        positive = int(part["positive_net"].sum())
        both = int((part["positive_net"] & part["coverage_pass"]).sum())
        block_summary_rows.append(
            {
                "dataset": dataset,
                "candidate": candidate,
                "blocks": int(len(part)),
                "positive_block_rate": positive / len(part) if len(part) else None,
                "positive_coverage_block_rate": both / len(part) if len(part) else None,
                "worst_block_net_pnl_cents": float(part["net_pnl_cents"].min()) if len(part) else None,
            }
        )
    block_summary = pd.DataFrame(block_summary_rows)
    supported_slices = slices[slices["markets"].ge(MIN_SLICE_MARKETS)].copy() if not slices.empty else slices
    worst_slices = supported_slices.sort_values("net_pnl_cents", ascending=True).head(16) if not supported_slices.empty else supported_slices

    lines = [
        "# Brownian70 Candidate Robustness Audit",
        "",
        f"Generated UTC: `{generated}`",
        "",
        "## Scope",
        "",
        "- Research-only audit; no orders are submitted and no bot files or live processes are touched.",
        "- Tests whether the Brownian/RV15 70% frontier row is stable enough for a separate forward lock.",
        "- This is diagnostic only; strict pre-registered live evidence remains the promotion gate.",
        "",
        "## Split Summary",
        "",
        "| dataset | candidate | all net/ROI | all acc/cov | train net | validation net | holdout net | coverage pass | all splits positive | OOS positive |",
        "|---|---|---:|---:|---:|---:|---:|---|---|---|",
    ]
    for _, row in summary.sort_values(["candidate", "dataset"]).iterrows():
        lines.append(
            f"| {row['dataset']} | `{row['candidate']}` | "
            f"{fmt_cents(row['all_net_pnl_cents'])}/{fmt_roi(row['all_net_roi_on_cost'])} | "
            f"{pct(row['all_accuracy'])}/{pct(row['all_coverage'])} | "
            f"{fmt_cents(row['train_net_pnl_cents'])} | {fmt_cents(row['validation_net_pnl_cents'])} | "
            f"{fmt_cents(row['holdout_net_pnl_cents'])} | {bool(row['coverage_pass'])} | "
            f"{bool(row['all_splits_positive'])} | {bool(row['oos_positive'])} |"
        )

    lines += [
        "",
        "## Block Summary",
        "",
        "| dataset | candidate | blocks | positive blocks | positive+coverage blocks | worst block |",
        "|---|---|---:|---:|---:|---:|",
    ]
    for _, row in block_summary.sort_values(["candidate", "dataset"]).iterrows():
        lines.append(
            f"| {row['dataset']} | `{row['candidate']}` | {int(row['blocks'])} | "
            f"{pct(row['positive_block_rate'])} | {pct(row['positive_coverage_block_rate'])} | "
            f"{fmt_cents(row['worst_block_net_pnl_cents'])} |"
        )

    lines += [
        "",
        f"## Worst Supported Slices",
        "",
        f"Only slices with at least `{MIN_SLICE_MARKETS}` selected markets are shown.",
        "",
        "| dataset | candidate | slice | markets | wins/losses | net | net/market | median ask |",
        "|---|---|---|---:|---:|---:|---:|---:|",
    ]
    if worst_slices.empty:
        lines.append("| none | none | none | 0 | 0/0 | 0.0c | 0.0c | NA |")
    else:
        for _, row in worst_slices.iterrows():
            lines.append(
                f"| {row['dataset']} | `{row['candidate']}` | {row['group_type']}=`{row['group']}` | "
                f"{int(row['markets'])} | {int(row['wins'])}/{int(row['losses'])} | "
                f"{fmt_cents(row['net_pnl_cents'])} | {fmt_cents(row['net_per_market_cents'])} | "
                f"{fmt_cents(row['median_ask'])} |"
            )

    lines += [
        "",
        "## History",
        "",
        "| file | candidate | current all | current val | current holdout | v21 all | v21 train | v21 val | v21 holdout |",
        "|---|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for _, row in history[history["candidate"].eq("brownian70_sec120")].tail(8).iterrows() if not history.empty else []:
        lines.append(
            f"| `{row['file']}` | `{row['candidate']}` | "
            f"{fmt_cents(row['current_all_net_pnl_cents'])} | {fmt_cents(row['current_validation_net_pnl_cents'])} | "
            f"{fmt_cents(row['current_holdout_net_pnl_cents'])} | {fmt_cents(row['v21_all_net_pnl_cents'])} | "
            f"{fmt_cents(row['v21_train_net_pnl_cents'])} | {fmt_cents(row['v21_validation_net_pnl_cents'])} | "
            f"{fmt_cents(row['v21_holdout_net_pnl_cents'])} |"
        )

    lines += ["", "## Read", ""]
    for candidate in sorted(summary["candidate"].unique()):
        part = summary[summary["candidate"].eq(candidate)]
        blocks_part = block_summary[block_summary["candidate"].eq(candidate)] if not block_summary.empty else block_summary
        coverage_ok = bool(part["coverage_pass"].all()) if not part.empty else False
        all_splits_ok = bool(part["all_splits_positive"].all()) if not part.empty else False
        oos_ok = bool(part["oos_positive"].all()) if not part.empty else False
        min_block_rate = float(blocks_part["positive_coverage_block_rate"].min()) if not blocks_part.empty else 0.0
        robust = coverage_ok and all_splits_ok and oos_ok and min_block_rate >= POSITIVE_BLOCK_RATE_FLOOR
        lines.append(
            f"- `{candidate}` coverage/all-splits/OOS/min positive+coverage block rate/robust: "
            f"{coverage_ok}/{all_splits_ok}/{oos_ok}/{pct(min_block_rate)}/{robust}."
        )
    lines.append("- A candidate that fails all-split or block stability should remain observation-only, not promotion evidence.")
    REPORT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    generated = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%SZ")
    summary_rows: List[Dict[str, Any]] = []
    block_out: List[Dict[str, Any]] = []
    slice_out: List[Dict[str, Any]] = []
    for dataset, loader in [("current", load_side_rows), ("v21", load_v21_side_rows)]:
        side_rows = loader()
        base = market_base(side_rows)
        for name, policy in CANDIDATES.items():
            selected = select_for_policy(side_rows, base, policy)
            summary_rows.append(flatten_summary(dataset, name, policy, base, selected))
            block_out.extend(block_rows(dataset, name, base, selected))
            slice_out.extend(slice_rows(dataset, name, selected))

    summary = pd.DataFrame(summary_rows)
    blocks = pd.DataFrame(block_out)
    slices = pd.DataFrame(slice_out)
    history = pd.DataFrame(history_rows())
    summary.to_csv(SUMMARY_CSV, index=False)
    blocks.to_csv(BLOCK_CSV, index=False)
    slices.to_csv(SLICE_CSV, index=False)
    history.to_csv(HISTORY_CSV, index=False)
    payload = {
        "generated_utc": generated,
        "coverage_floor": COVERAGE_FLOOR,
        "positive_block_rate_floor": POSITIVE_BLOCK_RATE_FLOOR,
        "summary": clean_json_local(summary.to_dict(orient="records")),
        "blocks": clean_json_local(blocks.to_dict(orient="records")),
        "slices": clean_json_local(slices.to_dict(orient="records")),
        "history": clean_json_local(history.to_dict(orient="records")),
    }
    REPORT_JSON.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    stamp = OUT_DIR / f"brownian70_candidate_robustness_audit_{generated}.json"
    stamp.write_text(REPORT_JSON.read_text(encoding="utf-8"), encoding="utf-8")
    write_report(generated, summary, blocks, slices, history)
    md_stamp = OUT_DIR / f"brownian70_candidate_robustness_audit_{generated}.md"
    md_stamp.write_text(REPORT_MD.read_text(encoding="utf-8"), encoding="utf-8")
    print("Brownian70 candidate robustness audit complete")
    print(f"candidates={len(CANDIDATES)} summary_rows={len(summary)}")
    print(f"report={REPORT_MD}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
