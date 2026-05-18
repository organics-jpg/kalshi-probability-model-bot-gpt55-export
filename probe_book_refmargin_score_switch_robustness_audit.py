"""Robustness audit for the locked book/reference-margin score switch.

The locked rule is a forward-test candidate, not promotion evidence. This probe
stress-tests the exact locked selector across the current and v21 ledgers with
chronological block, split, and source-slice checks so an aggregate-positive
scan cannot hide unstable periods.

Research-only: no orders are submitted and no bot files or live processes are
modified.
"""
from __future__ import annotations

import json
import math
from datetime import datetime, timezone
from typing import Any, Dict, List

import numpy as np
import pandas as pd

from probe_cross_dataset_interval_frontier import load_v21_side_rows
from probe_cross_dataset_profit_frontier import enrich_selected, fmt_cents, fmt_roi, metrics_for, split_metric
from probe_frontier_candidate_v2_diagnostic import select_policy
from probe_market_interval_80coverage import MARKET_COVERAGE_FLOOR, OUT_DIR, clean_json, load_side_rows, market_base, pct
from probe_profit_lock_pending_signal_monitor import BOOK_REFMARGIN_SCORE_SWITCH_LOCK_PATH, select_session_switch_rows


REPORT_MD = OUT_DIR / "book_refmargin_score_switch_robustness_audit_latest.md"
REPORT_JSON = OUT_DIR / "book_refmargin_score_switch_robustness_audit_latest.json"
BLOCK_CSV = OUT_DIR / "book_refmargin_score_switch_robustness_blocks_latest.csv"
SLICE_CSV = OUT_DIR / "book_refmargin_score_switch_robustness_slices_latest.csv"

LOCK_NAME = "book_refmargin_score_switch"
ANCHOR_NAME = "book_margin"
REFERENCE_NAME = "score_min60_gap020"
BLOCKS = 8


def clean_json_local(value: Any) -> Any:
    if isinstance(value, pd.Timestamp):
        return value.isoformat()
    if isinstance(value, dict):
        return {str(k): clean_json_local(v) for k, v in value.items()}
    if isinstance(value, list):
        return [clean_json_local(v) for v in value]
    return clean_json(value)


def select_locked(side_rows: pd.DataFrame, base: pd.DataFrame, lock: Dict[str, Any]) -> pd.DataFrame:
    rows = side_rows.merge(base[["market", "split"]], on="market", how="inner")
    return enrich_selected(select_session_switch_rows(rows, lock))


def all_metric_row(dataset: str, policy: str, selected: pd.DataFrame, base: pd.DataFrame) -> Dict[str, Any]:
    row: Dict[str, Any] = {"dataset": dataset, "policy": policy}
    for split, values in metrics_for(base, selected).items():
        for key, value in values.items():
            row[f"{split}_{key}"] = value
    row["split_positive_pass"] = all((row.get(f"{split}_net_pnl_cents") or 0.0) > 0.0 for split in ["train", "validation", "holdout"])
    row["split_coverage_pass"] = all((row.get(f"{split}_coverage") or 0.0) >= MARKET_COVERAGE_FLOOR for split in ["train", "validation", "holdout"])
    return row


def metric_for_subset(base_subset: pd.DataFrame, selected: pd.DataFrame) -> Dict[str, Any]:
    markets = set(base_subset["market"].astype(str))
    selected_subset = selected[selected["market"].astype(str).isin(markets)].copy()
    return split_metric(base_subset, selected_subset, "all")


def add_block_ids(base: pd.DataFrame, blocks: int = BLOCKS) -> pd.DataFrame:
    out = base.sort_values(["close_dt", "market"]).reset_index(drop=True).copy()
    if out.empty:
        out["chron_block"] = []
        return out
    out["chron_block"] = (np.floor(np.arange(len(out)) * blocks / len(out)).astype(int) + 1).clip(1, blocks)
    return out


def chronological_block_rows(
    dataset: str,
    base: pd.DataFrame,
    candidate: pd.DataFrame,
    anchor: pd.DataFrame,
) -> List[Dict[str, Any]]:
    out: List[Dict[str, Any]] = []
    block_base = add_block_ids(base)
    for block_id, base_part in block_base.groupby("chron_block", sort=True):
        cand_metric = metric_for_subset(base_part, candidate)
        anchor_metric = metric_for_subset(base_part, anchor)
        out.append(
            {
                "dataset": dataset,
                "block": int(block_id),
                "start_close_dt": pd.to_datetime(base_part["close_dt"], utc=True, errors="coerce").min(),
                "end_close_dt": pd.to_datetime(base_part["close_dt"], utc=True, errors="coerce").max(),
                "base_markets": int(cand_metric["base_markets"]),
                "candidate_markets": int(cand_metric["markets"]),
                "candidate_wins": int(cand_metric["wins"]),
                "candidate_losses": int(cand_metric["losses"]),
                "candidate_accuracy": cand_metric["accuracy"],
                "candidate_break_even": cand_metric["fee_aware_break_even_accuracy"],
                "candidate_coverage": cand_metric["coverage"],
                "candidate_net_pnl_cents": cand_metric["net_pnl_cents"],
                "candidate_roi": cand_metric["net_roi_on_cost"],
                "anchor_net_pnl_cents": anchor_metric["net_pnl_cents"],
                "candidate_minus_anchor_cents": (cand_metric["net_pnl_cents"] or 0.0) - (anchor_metric["net_pnl_cents"] or 0.0),
                "block_pass": (
                    (cand_metric["coverage"] or 0.0) >= MARKET_COVERAGE_FLOOR
                    and (cand_metric["net_pnl_cents"] or 0.0) > 0.0
                    and (
                        cand_metric["accuracy"] is not None
                        and cand_metric["fee_aware_break_even_accuracy"] is not None
                        and cand_metric["accuracy"] > cand_metric["fee_aware_break_even_accuracy"]
                    )
                ),
            }
        )
    return out


def selected_slice_metric(part: pd.DataFrame) -> Dict[str, Any]:
    n = int(len(part))
    wins = int(part["win"].sum()) if n else 0
    cost = float(part["entry_cost_cents"].sum()) if n else 0.0
    net = float(part["net_pnl_cents"].sum()) if n else 0.0
    break_even = float(part["fee_aware_break_even_p"].mean()) if n else None
    accuracy = wins / n if n else None
    return {
        "markets": n,
        "wins": wins,
        "losses": n - wins,
        "accuracy": accuracy,
        "break_even": break_even,
        "net_pnl_cents": net,
        "net_roi_on_cost": net / cost if cost else None,
        "median_ask": float(part["ask_cents"].median()) if n else None,
        "pass": n >= 20 and net > 0.0 and accuracy is not None and break_even is not None and accuracy > break_even,
    }


def source_slice_rows(dataset: str, selected: pd.DataFrame) -> List[Dict[str, Any]]:
    out: List[Dict[str, Any]] = []
    if selected.empty:
        return out
    work = selected.copy()
    work["entry_hour_utc"] = pd.to_datetime(work["entry_dt"], utc=True, errors="coerce").dt.hour
    work["ask_bucket"] = pd.cut(
        pd.to_numeric(work["ask_cents"], errors="coerce"),
        bins=[-math.inf, 60, 70, math.inf],
        labels=["ask<=60", "60<ask<=70", "ask>70"],
    )
    for group_name, col in [
        ("source", "overlay"),
        ("split", "split"),
        ("entry_hour_utc", "entry_hour_utc"),
        ("ask_bucket", "ask_bucket"),
    ]:
        for bucket, part in work.groupby(col, dropna=False, sort=True, observed=False):
            metric = selected_slice_metric(part)
            out.append(
                {
                    "dataset": dataset,
                    "group": group_name,
                    "bucket": str(bucket),
                    **metric,
                }
            )
    return out


def run_dataset(dataset: str, side_rows: pd.DataFrame, lock: Dict[str, Any]) -> tuple[Dict[str, pd.DataFrame], List[Dict[str, Any]], List[Dict[str, Any]], List[Dict[str, Any]]]:
    base = market_base(side_rows)
    candidate = select_locked(side_rows, base, lock)
    anchor = select_policy(side_rows, base, ANCHOR_NAME)
    reference = select_policy(side_rows, base, REFERENCE_NAME)
    selected = {
        LOCK_NAME: candidate,
        ANCHOR_NAME: anchor,
        REFERENCE_NAME: reference,
    }
    metric_rows = [all_metric_row(dataset, name, frame, base) for name, frame in selected.items()]
    block_rows = chronological_block_rows(dataset, base, candidate, anchor)
    slice_rows = source_slice_rows(dataset, candidate)
    selected_with_base = {"base": base, **selected}
    return selected_with_base, metric_rows, block_rows, slice_rows


def format_metric_cell(row: Dict[str, Any], split: str) -> str:
    return (
        f"{fmt_cents(row.get(f'{split}_net_pnl_cents'))}/"
        f"{pct(row.get(f'{split}_accuracy'))}/"
        f"{pct(row.get(f'{split}_coverage'))}"
    )


def write_report(
    generated: str,
    lock: Dict[str, Any],
    metric_rows: List[Dict[str, Any]],
    block_df: pd.DataFrame,
    slice_df: pd.DataFrame,
) -> None:
    candidate_metrics = [row for row in metric_rows if row["policy"] == LOCK_NAME]
    split_pass = all(row["split_positive_pass"] and row["split_coverage_pass"] for row in candidate_metrics)
    block_pass = bool(not block_df.empty and block_df["block_pass"].all())
    source_pass = True
    if not slice_df.empty:
        source_rows = slice_df[slice_df["group"].eq("source")]
        source_pass = bool(not source_rows.empty and source_rows["pass"].all())
    offline_robust_pass = split_pass and block_pass and source_pass

    lines = [
        "# Book Reference-Margin Switch Robustness Audit",
        "",
        f"Generated UTC: `{generated}`",
        "",
        "## Scope",
        "",
        "- Research-only audit; no orders are submitted and no bot files or live processes are touched.",
        "- Replays the exact locked switch rule on current and v21 ledgers.",
        "- Promotion still requires strict pre-resolution live evidence; this audit can only reject or justify continued collection.",
        "",
        "## Locked Rule",
        "",
        f"- Lock file: `{BOOK_REFMARGIN_SCORE_SWITCH_LOCK_PATH}`",
        f"- Label: `{lock.get('switch_rule', {}).get('label')}`",
        f"- Condition source: `{lock.get('switch_rule', {}).get('condition_source')}`",
        f"- Condition: `{lock.get('switch_rule', {}).get('condition')}`",
        "",
        "## Split Metrics",
        "",
        "| dataset | policy | all net/acc/cov | train net/acc/cov | validation net/acc/cov | holdout net/acc/cov | split pass |",
        "|---|---|---:|---:|---:|---:|---|",
    ]
    for row in metric_rows:
        lines.append(
            f"| {row['dataset']} | `{row['policy']}` | {format_metric_cell(row, 'all')} | "
            f"{format_metric_cell(row, 'train')} | {format_metric_cell(row, 'validation')} | "
            f"{format_metric_cell(row, 'holdout')} | {row['split_positive_pass'] and row['split_coverage_pass']} |"
        )

    lines += [
        "",
        "## Chronological Blocks",
        "",
        "| dataset | block | markets | wins/losses | acc | break-even | coverage | net P&L | vs book_margin | pass |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---|",
    ]
    for _, row in block_df.iterrows():
        lines.append(
            f"| {row['dataset']} | {int(row['block'])} | {int(row['candidate_markets'])}/{int(row['base_markets'])} | "
            f"{int(row['candidate_wins'])}/{int(row['candidate_losses'])} | {pct(row['candidate_accuracy'])} | "
            f"{pct(row['candidate_break_even'])} | {pct(row['candidate_coverage'])} | "
            f"{fmt_cents(row['candidate_net_pnl_cents'])} | {fmt_cents(row['candidate_minus_anchor_cents'])} | "
            f"{bool(row['block_pass'])} |"
        )

    lines += [
        "",
        "## Source Slices",
        "",
        "| dataset | bucket | markets | wins/losses | acc | break-even | net P&L | ROI | median ask | pass |",
        "|---|---|---:|---:|---:|---:|---:|---:|---:|---|",
    ]
    source_df = slice_df[slice_df["group"].eq("source")] if not slice_df.empty else pd.DataFrame()
    for _, row in source_df.iterrows():
        lines.append(
            f"| {row['dataset']} | `{row['bucket']}` | {int(row['markets'])} | "
            f"{int(row['wins'])}/{int(row['losses'])} | {pct(row['accuracy'])} | "
            f"{pct(row['break_even'])} | {fmt_cents(row['net_pnl_cents'])} | "
            f"{fmt_roi(row['net_roi_on_cost'])} | {fmt_cents(row['median_ask'])} | {bool(row['pass'])} |"
        )

    lines += [
        "",
        "## Read",
        "",
        f"- Split gate pass: {split_pass}.",
        f"- Chronological block gate pass: {block_pass}.",
        f"- Source-slice gate pass: {source_pass}.",
        f"- Offline robustness pass: {offline_robust_pass}.",
    ]
    if offline_robust_pass:
        lines.append("- The locked switch remains worth collecting strict forward samples, but it is not promotion-ready without live registered evidence.")
    else:
        lines.append("- The locked switch is not robust enough for promotion evidence; keep it as diagnostic/forward-test only.")

    REPORT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    generated = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%SZ")
    lock = json.loads(BOOK_REFMARGIN_SCORE_SWITCH_LOCK_PATH.read_text(encoding="utf-8"))
    selected_current, metric_current, block_current, slice_current = run_dataset("current", load_side_rows(), lock)
    selected_v21, metric_v21, block_v21, slice_v21 = run_dataset("v21", load_v21_side_rows(), lock)

    metric_rows = metric_current + metric_v21
    block_df = pd.DataFrame(block_current + block_v21)
    slice_df = pd.DataFrame(slice_current + slice_v21)

    block_df.to_csv(BLOCK_CSV, index=False)
    slice_df.to_csv(SLICE_CSV, index=False)
    stamp_blocks = OUT_DIR / f"book_refmargin_score_switch_robustness_blocks_{generated}.csv"
    stamp_slices = OUT_DIR / f"book_refmargin_score_switch_robustness_slices_{generated}.csv"
    block_df.to_csv(stamp_blocks, index=False)
    slice_df.to_csv(stamp_slices, index=False)

    selected_current[LOCK_NAME].to_csv(OUT_DIR / "book_refmargin_score_switch_selected_current_latest.csv", index=False)
    selected_v21[LOCK_NAME].to_csv(OUT_DIR / "book_refmargin_score_switch_selected_v21_latest.csv", index=False)

    write_report(generated, lock, metric_rows, block_df, slice_df)
    payload = {
        "generated_utc": generated,
        "lock_name": LOCK_NAME,
        "lock": lock,
        "metric_rows": metric_rows,
        "block_rows": block_df.to_dict(orient="records"),
        "slice_rows": slice_df.to_dict(orient="records"),
    }
    REPORT_JSON.write_text(json.dumps(clean_json_local(payload), indent=2, sort_keys=True), encoding="utf-8")
    stamp_json = OUT_DIR / f"book_refmargin_score_switch_robustness_audit_{generated}.json"
    stamp_json.write_text(json.dumps(clean_json_local(payload), indent=2, sort_keys=True), encoding="utf-8")
    stamp_md = OUT_DIR / f"book_refmargin_score_switch_robustness_audit_{generated}.md"
    stamp_md.write_text(REPORT_MD.read_text(encoding="utf-8"), encoding="utf-8")

    block_pass = bool(not block_df.empty and block_df["block_pass"].all())
    source_df = slice_df[slice_df["group"].eq("source")] if not slice_df.empty else pd.DataFrame()
    source_pass = bool(not source_df.empty and source_df["pass"].all())
    print("Book reference-margin switch robustness audit complete")
    print(f"blocks={len(block_df)} block_pass={block_pass} source_pass={source_pass}")
    print(f"report={REPORT_MD}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
