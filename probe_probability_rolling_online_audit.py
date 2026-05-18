"""Rolling past-only probability audit for BTC 15m interval candidates.

This probe asks whether a compact learned fair-value model improves when it is
re-fit only on markets that closed before the test block. It is designed to
catch split artifacts from static train/validation/holdout scans:

- group markets into chronological blocks;
- fit each model on prior blocks only;
- choose the EV floor from prior blocks only, preserving high coverage;
- score the next block and move forward.

Research-only: no orders are submitted and no bot files or live processes are
modified. Passing rows are diagnostics only, not promotion evidence.
"""
from __future__ import annotations

import json
import math
from datetime import datetime, timezone
from typing import Any, Dict, List

import numpy as np
import pandas as pd

from probe_cross_dataset_interval_frontier import load_v21_side_rows
from probe_cross_dataset_profit_frontier import fmt_cents, fmt_roi
from probe_market_interval_80coverage import OUT_DIR, choose_decision_sides, clean_json, load_side_rows, market_base, pct
from probe_probability_multifeature_logit_audit import (
    C_VALUES,
    FEATURE_SETS,
    add_fee_pnl,
    first_market_rows,
    fit_model,
    usable_feature_frame,
)


REPORT_MD = OUT_DIR / "probability_rolling_online_audit_latest.md"
REPORT_JSON = OUT_DIR / "probability_rolling_online_audit_latest.json"
BLOCK_CSV = OUT_DIR / "probability_rolling_online_blocks_latest.csv"
SUMMARY_CSV = OUT_DIR / "probability_rolling_online_summary_latest.csv"

BLOCK_MARKETS = 20
MIN_TRAIN_BLOCKS = 4
MIN_SECONDS_TO_CLOSE = 120.0
ASK_MAX = 95.0
COVERAGE_FLOOR = 0.75
MIN_NET_PER_SELECTED_CENTS = 2.0
MIN_POSITIVE_COVERAGE_BLOCK_RATE = 0.75
EDGE_FLOORS = [-20.0, -15.0, -10.0, -5.0, 0.0, 2.0, 5.0, 10.0, 15.0, 20.0]


def clean_json_local(value: Any) -> Any:
    if isinstance(value, pd.Timestamp):
        return value.isoformat()
    if isinstance(value, dict):
        return {str(k): clean_json_local(v) for k, v in value.items()}
    if isinstance(value, list):
        return [clean_json_local(v) for v in value]
    return clean_json(value)


def add_blocks(base: pd.DataFrame) -> pd.DataFrame:
    out = base.copy()
    out["close_dt"] = pd.to_datetime(out["close_dt"], utc=True, errors="coerce")
    out = out.sort_values(["close_dt", "market"]).reset_index(drop=True)
    out["block_index"] = out.index // BLOCK_MARKETS
    return out


def prepare_dataset(side_rows: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    base = add_blocks(market_base(side_rows))
    rows = side_rows.drop(columns=[col for col in ["split", "block_index"] if col in side_rows.columns], errors="ignore")
    rows = rows.merge(base[["market", "split", "block_index"]], on="market", how="inner")
    return base, rows


def score_chosen(rows: pd.DataFrame, model: Any, x: pd.DataFrame, model_name: str) -> pd.DataFrame:
    if rows.empty:
        return rows.copy()
    out = rows.copy()
    out["p_model"] = model.predict_proba(x)[:, 1]
    chosen = choose_decision_sides(out, "p_model")
    if chosen.empty:
        return chosen
    chosen = chosen[
        pd.to_numeric(chosen["ask_cents"], errors="coerce").le(ASK_MAX)
        & pd.to_numeric(chosen["seconds_to_close"], errors="coerce").ge(MIN_SECONDS_TO_CLOSE)
    ].copy()
    if chosen.empty:
        return chosen
    chosen["model"] = model_name
    chosen = add_fee_pnl(chosen)
    chosen["fair_edge_cents"] = 100.0 * pd.to_numeric(chosen["p_model"], errors="coerce") - chosen["entry_cost_cents"]
    return chosen.sort_values(["market", "entry_dt"]).reset_index(drop=True)


def summarize_selected(base_markets: int, selected: pd.DataFrame) -> Dict[str, Any]:
    n = int(len(selected))
    wins = int(selected["win"].astype(bool).sum()) if n else 0
    net = float(pd.to_numeric(selected.get("net_pnl_cents"), errors="coerce").sum()) if n else 0.0
    cost = float(pd.to_numeric(selected.get("entry_cost_cents"), errors="coerce").sum()) if n else 0.0
    return {
        "base_markets": int(base_markets),
        "selected_markets": n,
        "wins": wins,
        "losses": n - wins,
        "accuracy": wins / n if n else None,
        "coverage": n / base_markets if base_markets else None,
        "net_pnl_cents": net,
        "net_roi_on_cost": net / cost if cost else None,
        "median_ask": float(pd.to_numeric(selected.get("ask_cents"), errors="coerce").median()) if n else None,
        "median_edge_cents": float(pd.to_numeric(selected.get("fair_edge_cents"), errors="coerce").median()) if n else None,
    }


def choose_edge_floor(train_base_count: int, train_chosen: pd.DataFrame) -> Dict[str, Any]:
    choices: List[Dict[str, Any]] = []
    for edge_floor in EDGE_FLOORS:
        selected = first_market_rows(train_chosen[train_chosen["fair_edge_cents"].ge(edge_floor)].copy())
        metrics = summarize_selected(train_base_count, selected)
        choices.append({"edge_floor_cents": float(edge_floor), **metrics})
    eligible = [row for row in choices if float(row["coverage"] or 0.0) >= COVERAGE_FLOOR]
    if not eligible:
        eligible = choices
    eligible.sort(
        key=lambda row: (
            float(row["net_pnl_cents"] or 0.0),
            float(row["coverage"] or 0.0),
            -abs(float(row["edge_floor_cents"])),
        ),
        reverse=True,
    )
    return eligible[0]


def run_dataset(dataset: str, side_rows: pd.DataFrame) -> tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    base, rows = prepare_dataset(side_rows)
    block_rows: List[Dict[str, Any]] = []
    summary_rows: List[Dict[str, Any]] = []
    max_block = int(base["block_index"].max()) if not base.empty else -1

    for feature_set, specs in FEATURE_SETS.items():
        for c_value in C_VALUES:
            model_name = f"{feature_set}_C{c_value:g}"
            for block_index in range(MIN_TRAIN_BLOCKS, max_block + 1):
                train_base = base[base["block_index"].lt(block_index)]
                test_base = base[base["block_index"].eq(block_index)]
                if len(test_base) < max(5, BLOCK_MARKETS // 2):
                    continue
                train_rows = rows[rows["market"].isin(train_base["market"])].copy()
                test_rows = rows[rows["market"].isin(test_base["market"])].copy()
                if train_rows.empty or test_rows.empty or train_rows["win"].astype(bool).nunique() < 2:
                    continue
                train_x, all_x, feature_names = usable_feature_frame(
                    train_rows,
                    pd.concat([train_rows.assign(_part="train"), test_rows.assign(_part="test")], ignore_index=True, sort=False),
                    specs,
                )
                model = fit_model(train_x, train_rows["win"], c_value)
                all_rows = pd.concat([train_rows.assign(_part="train"), test_rows.assign(_part="test")], ignore_index=True, sort=False)
                train_mask = all_rows["_part"].eq("train").to_numpy()
                train_chosen = score_chosen(
                    all_rows[train_mask].drop(columns=["_part"]).reset_index(drop=True),
                    model,
                    all_x[train_mask].reset_index(drop=True),
                    model_name,
                )
                edge_choice = choose_edge_floor(len(train_base), train_chosen)
                test_chosen = score_chosen(
                    all_rows[~train_mask].drop(columns=["_part"]).reset_index(drop=True),
                    model,
                    all_x[~train_mask].reset_index(drop=True),
                    model_name,
                )
                selected = first_market_rows(test_chosen[test_chosen["fair_edge_cents"].ge(edge_choice["edge_floor_cents"])].copy())
                metrics = summarize_selected(len(test_base), selected)
                block_rows.append(
                    {
                        "dataset": dataset,
                        "model": model_name,
                        "feature_set": feature_set,
                        "c_value": float(c_value),
                        "block_index": int(block_index),
                        "train_base_markets": int(len(train_base)),
                        "block_start_close_dt": pd.to_datetime(test_base["close_dt"].min(), utc=True, errors="coerce"),
                        "block_end_close_dt": pd.to_datetime(test_base["close_dt"].max(), utc=True, errors="coerce"),
                        "edge_floor_cents": float(edge_choice["edge_floor_cents"]),
                        "train_edge_net_pnl_cents": edge_choice["net_pnl_cents"],
                        "train_edge_coverage": edge_choice["coverage"],
                        "features": ",".join(feature_names),
                        **metrics,
                    }
                )

    block_df = pd.DataFrame(block_rows)
    if block_df.empty:
        return block_rows, summary_rows
    for (model_name, feature_set, c_value), part in block_df.groupby(["model", "feature_set", "c_value"], sort=False):
        selected_sum = int(part["selected_markets"].sum())
        base_sum = int(part["base_markets"].sum())
        wins = int(part["wins"].sum())
        net = float(part["net_pnl_cents"].sum())
        cost_proxy = None
        positive_blocks = int(part["net_pnl_cents"].gt(0.0).sum())
        coverage_blocks = int(part["coverage"].fillna(0.0).ge(COVERAGE_FLOOR).sum())
        both_blocks = int((part["net_pnl_cents"].gt(0.0) & part["coverage"].fillna(0.0).ge(COVERAGE_FLOOR)).sum())
        summary_rows.append(
            {
                "dataset": dataset,
                "model": model_name,
                "feature_set": feature_set,
                "c_value": float(c_value),
                "blocks": int(len(part)),
                "base_markets": base_sum,
                "selected_markets": selected_sum,
                "coverage": selected_sum / base_sum if base_sum else None,
                "wins": wins,
                "losses": selected_sum - wins,
                "accuracy": wins / selected_sum if selected_sum else None,
                "net_pnl_cents": net,
                "net_per_selected_cents": net / selected_sum if selected_sum else None,
                "net_roi_on_cost": cost_proxy,
                "positive_blocks": positive_blocks,
                "coverage_pass_blocks": coverage_blocks,
                "positive_coverage_pass_blocks": both_blocks,
                "positive_block_rate": positive_blocks / len(part) if len(part) else None,
                "positive_coverage_pass_rate": both_blocks / len(part) if len(part) else None,
                "worst_block_net_pnl_cents": float(part["net_pnl_cents"].min()),
                "worst_block_coverage": float(part["coverage"].min()),
                "median_edge_floor_cents": float(part["edge_floor_cents"].median()),
                "robust_pass": (
                    selected_sum / base_sum >= COVERAGE_FLOOR
                    and net > 0.0
                    and (net / selected_sum if selected_sum else -math.inf) >= MIN_NET_PER_SELECTED_CENTS
                    and (both_blocks / len(part) if len(part) else 0.0) >= MIN_POSITIVE_COVERAGE_BLOCK_RATE
                )
                if base_sum
                else False,
            }
        )
    return block_rows, summary_rows


def combined_summary(summary: pd.DataFrame) -> pd.DataFrame:
    rows: List[Dict[str, Any]] = []
    if summary.empty:
        return pd.DataFrame()
    for model_name, part in summary.groupby("model", sort=False):
        datasets = sorted(part["dataset"].unique())
        rows.append(
            {
                "model": model_name,
                "datasets": ",".join(datasets),
                "dataset_count": int(len(datasets)),
                "both_dataset_robust_pass": bool(part["robust_pass"].all()) and len(datasets) >= 2,
                "min_coverage": float(part["coverage"].min()),
                "min_positive_coverage_pass_rate": float(part["positive_coverage_pass_rate"].min()),
                "combined_net_pnl_cents": float(part["net_pnl_cents"].sum()),
                "combined_selected_markets": int(part["selected_markets"].sum()),
                "combined_base_markets": int(part["base_markets"].sum()),
                "combined_accuracy": float(part["wins"].sum() / part["selected_markets"].sum()) if int(part["selected_markets"].sum()) else None,
                "worst_dataset_block_cents": float(part["worst_block_net_pnl_cents"].min()),
            }
        )
    return pd.DataFrame(rows).sort_values(
        ["both_dataset_robust_pass", "combined_net_pnl_cents", "min_positive_coverage_pass_rate", "min_coverage"],
        ascending=[False, False, False, False],
    )


def write_report(generated: str, block_df: pd.DataFrame, summary_df: pd.DataFrame, combined_df: pd.DataFrame) -> None:
    lines = [
        "# Rolling Online Probability Audit",
        "",
        f"Generated UTC: `{generated}`",
        "",
        "## Scope",
        "",
        "- Research-only audit; no orders are submitted and no bot files or live processes are touched.",
        "- Each block is scored by a model fit only on earlier closed markets from the same dataset.",
        "- EV floor is selected from earlier markets only, with a high-coverage preference.",
        "- This is diagnostic anti-overfit evidence, not strict pre-registered live promotion evidence.",
        "",
        "## Protocol",
        "",
        f"- Block size: `{BLOCK_MARKETS}` recurring BTC 15m markets.",
        f"- Minimum prior blocks before scoring: `{MIN_TRAIN_BLOCKS}`.",
        f"- Tradeability filters: `ask<={ASK_MAX:g}`, `seconds_to_close>={MIN_SECONDS_TO_CLOSE:g}`.",
        f"- Prior edge floors scanned: `{', '.join(f'{edge:g}c' for edge in EDGE_FLOORS)}`.",
        f"- Diagnostic robust gate also requires net per selected market >= `{MIN_NET_PER_SELECTED_CENTS:g}c` "
        f"and positive+coverage block rate >= `{pct(MIN_POSITIVE_COVERAGE_BLOCK_RATE)}`.",
        "",
        "## Combined Model Ranking",
        "",
        "| rank | model | robust both datasets | combined net | combined acc/cov | min block pass rate | worst block |",
        "|---:|---|---|---:|---:|---:|---:|",
    ]
    if combined_df.empty:
        lines.append("| 0 | none | False | 0.0c | NA/NA | NA | 0.0c |")
    else:
        for rank, (_, row) in enumerate(combined_df.head(20).iterrows(), start=1):
            combined_cov = row["combined_selected_markets"] / row["combined_base_markets"] if row["combined_base_markets"] else None
            lines.append(
                f"| {rank} | `{row['model']}` | {bool(row['both_dataset_robust_pass'])} | "
                f"{fmt_cents(row['combined_net_pnl_cents'])} | "
                f"{pct(row['combined_accuracy'])}/{pct(combined_cov)} | "
                f"{pct(row['min_positive_coverage_pass_rate'])} | "
                f"{fmt_cents(row['worst_dataset_block_cents'])} |"
            )
    lines += [
        "",
        "## Dataset Summary",
        "",
        "| dataset | model | blocks | selected/base | acc | coverage | net | net/sel | positive+coverage blocks | worst block | robust |",
        "|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---|",
    ]
    for _, row in summary_df.sort_values(["dataset", "robust_pass", "net_pnl_cents"], ascending=[True, False, False]).iterrows():
        lines.append(
            f"| {row['dataset']} | `{row['model']}` | {int(row['blocks'])} | "
            f"{int(row['selected_markets'])}/{int(row['base_markets'])} | "
            f"{pct(row['accuracy'])} | {pct(row['coverage'])} | "
            f"{fmt_cents(row['net_pnl_cents'])} | "
            f"{fmt_cents(row['net_per_selected_cents'])} | "
            f"{int(row['positive_coverage_pass_blocks'])}/{pct(row['positive_coverage_pass_rate'])} | "
            f"{fmt_cents(row['worst_block_net_pnl_cents'])} | {bool(row['robust_pass'])} |"
        )

    worst = block_df.sort_values("net_pnl_cents", ascending=True).head(15) if not block_df.empty else block_df
    lines += [
        "",
        "## Worst Blocks",
        "",
        "| dataset | model | block | selected/base | acc | coverage | edge | net |",
        "|---|---|---:|---:|---:|---:|---:|---:|",
    ]
    for _, row in worst.iterrows():
        lines.append(
            f"| {row['dataset']} | `{row['model']}` | {int(row['block_index'])} | "
            f"{int(row['selected_markets'])}/{int(row['base_markets'])} | "
            f"{pct(row['accuracy'])} | {pct(row['coverage'])} | "
            f"{fmt_cents(row['edge_floor_cents'])} | {fmt_cents(row['net_pnl_cents'])} |"
        )

    lines += ["", "## Read", ""]
    if combined_df.empty or not bool(combined_df["both_dataset_robust_pass"].any()):
        lines.append("- No rolling online probability model clears the robust diagnostic gate on both datasets.")
    else:
        best = combined_df[combined_df["both_dataset_robust_pass"]].iloc[0]
        lines.append(
            f"- `{best['model']}` clears the diagnostic gate on both datasets, but still needs strict forward registration before promotion."
        )
    lines.append("- The live strict registered-signal gate remains the only promotion gate.")
    REPORT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    generated = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%SZ")
    block_rows: List[Dict[str, Any]] = []
    summary_rows: List[Dict[str, Any]] = []
    for dataset, loader in [("current", load_side_rows), ("v21", load_v21_side_rows)]:
        blocks, summary = run_dataset(dataset, loader())
        block_rows.extend(blocks)
        summary_rows.extend(summary)
    block_df = pd.DataFrame(block_rows)
    summary_df = pd.DataFrame(summary_rows)
    combined_df = combined_summary(summary_df)

    block_df.to_csv(BLOCK_CSV, index=False)
    summary_df.to_csv(SUMMARY_CSV, index=False)
    block_stamp = OUT_DIR / f"probability_rolling_online_blocks_{generated}.csv"
    summary_stamp = OUT_DIR / f"probability_rolling_online_summary_{generated}.csv"
    block_df.to_csv(block_stamp, index=False)
    summary_df.to_csv(summary_stamp, index=False)
    payload = {
        "generated_utc": generated,
        "block_markets": BLOCK_MARKETS,
        "min_train_blocks": MIN_TRAIN_BLOCKS,
        "coverage_floor": COVERAGE_FLOOR,
        "blocks": clean_json_local(block_df.to_dict(orient="records")),
        "summary": clean_json_local(summary_df.to_dict(orient="records")),
        "combined": clean_json_local(combined_df.to_dict(orient="records")),
    }
    json_stamp = OUT_DIR / f"probability_rolling_online_audit_{generated}.json"
    for path in [REPORT_JSON, json_stamp]:
        path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    write_report(generated, block_df, summary_df, combined_df)
    md_stamp = OUT_DIR / f"probability_rolling_online_audit_{generated}.md"
    md_stamp.write_text(REPORT_MD.read_text(encoding="utf-8"), encoding="utf-8")

    print("Rolling online probability audit complete")
    print(f"blocks={len(block_df)} summary_rows={len(summary_df)}")
    print(f"robust_both_dataset={int(combined_df['both_dataset_robust_pass'].sum()) if not combined_df.empty else 0}")
    print(f"report={REPORT_MD}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
