"""Cross-dataset empirical survival model for BTC 15m intervals.

This probe questions the parametric Brownian prior by replacing it with an
empirical survival table: comparable live states are binned by normalized
distance-to-strike, clock, book probability, drift, and adverse path features.
Tables are trained on one capture's chronological train split, then applied
without retuning to the other live capture.

Research-only: no orders are submitted and no bot files or live processes are
modified.
"""
from __future__ import annotations

import json
import math
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Dict, Iterable, List, Optional

import numpy as np
import pandas as pd

from probe_cross_dataset_interval_frontier import load_v21_side_rows
from probe_interval_policy_degeneracy_audit import wilson_lower
from probe_market_interval_80coverage import (
    MARKET_COVERAGE_FLOOR,
    MIN_HOLDOUT_SELECTED_MARKETS,
    MIN_SELECTED_MARKETS,
    OUT_DIR,
    TARGET_ACCURACY,
    add_scores,
    clean_json,
    load_side_rows,
    market_base,
    pct,
)


ASK_CAPS = [95.0, 100.0]
MIN_SECONDS = [0.0, 60.0, 120.0]
PROB_THRESHOLDS = [0.70, 0.75, 0.80, 0.85, 0.90, 0.95]
LOWER_THRESHOLDS = [0.50, 0.60, 0.70, 0.80]
MIN_CELL_NS = [10, 25, 50, 100]


@dataclass(frozen=True)
class Scheme:
    name: str
    features: tuple[str, ...]


SCHEMES = [
    Scheme("z15_time", ("z15_bin", "sec_bin")),
    Scheme("z30_time", ("z30_bin", "sec_bin")),
    Scheme("book_z15_time", ("book_bin", "z15_bin", "sec_bin")),
    Scheme("book_z30_time", ("book_bin", "z30_bin", "sec_bin")),
    Scheme("minscore_time", ("score_min_bin", "sec_bin")),
    Scheme("z15_time_adv5", ("z15_bin", "sec_bin", "adv5_bin")),
    Scheme("book_z15_time_adv5", ("book_bin", "z15_bin", "sec_bin", "adv5_bin")),
    Scheme("book_z15_time_drift5", ("book_bin", "z15_bin", "sec_bin", "drift5_bin")),
]


def clean_json_local(value: Any) -> Any:
    if isinstance(value, pd.Timestamp):
        return value.isoformat()
    if isinstance(value, dict):
        return {str(k): clean_json_local(v) for k, v in value.items()}
    if isinstance(value, list):
        return [clean_json_local(v) for v in value]
    return clean_json(value)


def fmt(value: Optional[float]) -> str:
    if value is None or not math.isfinite(float(value)):
        return "NA"
    return f"{float(value):.1f}"


def add_bins(rows: pd.DataFrame) -> pd.DataFrame:
    out = add_scores(rows).copy()
    for col in [
        "margin_per_rv_sigma_15m",
        "margin_per_rv_sigma_30m",
        "seconds_to_close",
        "book_p_side",
        "score_min_book_rv15",
        "adverse_move_5m",
        "drift_p_5m_rv_15m",
        "ask_cents",
    ]:
        if col not in out.columns:
            out[col] = np.nan
        out[col] = pd.to_numeric(out[col], errors="coerce")

    out["z15_bin"] = pd.cut(
        out["margin_per_rv_sigma_15m"],
        [-np.inf, 0.0, 0.25, 0.50, 0.75, 1.0, 1.25, 1.5, 2.0, np.inf],
        labels=False,
    )
    out["z30_bin"] = pd.cut(
        out["margin_per_rv_sigma_30m"],
        [-np.inf, 0.0, 0.25, 0.50, 0.75, 1.0, 1.25, 1.5, 2.0, np.inf],
        labels=False,
    )
    out["sec_bin"] = pd.cut(
        out["seconds_to_close"],
        [-np.inf, 60.0, 120.0, 240.0, 480.0, 900.0, np.inf],
        labels=False,
    )
    out["book_bin"] = pd.cut(out["book_p_side"], [-np.inf, 0.70, 0.80, 0.85, 0.90, 0.95, np.inf], labels=False)
    out["score_min_bin"] = pd.cut(
        out["score_min_book_rv15"], [-np.inf, 0.60, 0.70, 0.80, 0.85, 0.90, 0.95, np.inf], labels=False
    )
    out["adv5_bin"] = pd.cut(out["adverse_move_5m"], [-np.inf, 0.0, 5.0, 10.0, 20.0, np.inf], labels=False)
    out["drift5_bin"] = pd.cut(
        out["drift_p_5m_rv_15m"], [-np.inf, 0.55, 0.70, 0.85, 0.95, np.inf], labels=False
    )
    return out


def cell_table(train_rows: pd.DataFrame, scheme: Scheme) -> pd.DataFrame:
    grouped = (
        train_rows.dropna(subset=list(scheme.features))
        .groupby(list(scheme.features), dropna=False)
        .agg(n=("win", "size"), wins=("win", "sum"), median_ask=("ask_cents", "median"))
        .reset_index()
    )
    grouped["emp_p"] = (grouped["wins"] + 1.0) / (grouped["n"] + 2.0)
    grouped["emp_lower"] = [wilson_lower(int(w), int(n)) for w, n in zip(grouped["wins"], grouped["n"])]
    return grouped


def apply_table(rows: pd.DataFrame, table: pd.DataFrame, scheme: Scheme) -> pd.DataFrame:
    cols = list(scheme.features)
    scored = rows.merge(table[cols + ["n", "wins", "emp_p", "emp_lower"]], on=cols, how="left")
    scored = scored.rename(
        columns={
            "n": "emp_cell_n",
            "wins": "emp_cell_wins",
        }
    )
    return scored


def choose_decision_sides(scored: pd.DataFrame, score_col: str) -> pd.DataFrame:
    usable = scored[scored[score_col].notna()].copy()
    if usable.empty:
        return usable
    return (
        usable.sort_values(
            ["decision_key", score_col, "emp_cell_n", "book_p_side"],
            ascending=[True, False, False, False],
        )
        .groupby("decision_key", as_index=False, sort=False)
        .first()
        .sort_values(["market", "entry_dt"])
        .reset_index(drop=True)
    )


def select_markets(chosen: pd.DataFrame, score_col: str, threshold: float, min_cell_n: int, ask_cap: float, min_sec: float) -> pd.DataFrame:
    eligible = chosen[
        chosen[score_col].ge(threshold)
        & chosen["emp_cell_n"].ge(min_cell_n)
        & chosen["ask_cents"].le(ask_cap)
        & chosen["seconds_to_close"].ge(min_sec)
    ].copy()
    if eligible.empty:
        return eligible
    selected = (
        eligible.sort_values(["market", "entry_dt"])
        .groupby("market", as_index=False, sort=False)
        .first()
        .sort_values(["entry_dt", "market"])
        .reset_index(drop=True)
    )
    selected["settlement_pnl_cents"] = np.where(selected["win"], 100.0 - selected["ask_cents"], -selected["ask_cents"])
    return selected


def split_metric(base: pd.DataFrame, selected: pd.DataFrame, split: str) -> Dict[str, Any]:
    base_part = base if split == "all" else base[base["split"] == split]
    selected_part = selected if split == "all" else selected[selected["split"] == split]
    n = int(len(selected_part))
    wins = int(selected_part["win"].sum()) if n else 0
    total = int(len(base_part))
    stake = float(selected_part["ask_cents"].sum()) if n else 0.0
    pnl = float(selected_part["settlement_pnl_cents"].sum()) if n else 0.0
    return {
        "base_markets": total,
        "markets": n,
        "wins": wins,
        "losses": n - wins,
        "accuracy": wins / n if n else None,
        "coverage": n / total if total else None,
        "wilson95_lower": wilson_lower(wins, n),
        "median_ask": float(selected_part["ask_cents"].median()) if n else None,
        "ask_eq_100": int(selected_part["ask_cents"].ge(100).sum()) if n else 0,
        "median_seconds_to_close": float(selected_part["seconds_to_close"].median()) if n else None,
        "gross_pnl_cents": pnl,
        "gross_roi": pnl / stake if stake else None,
    }


def metrics_for(base: pd.DataFrame, selected: pd.DataFrame) -> Dict[str, Dict[str, Any]]:
    return {split: split_metric(base, selected, split) for split in ["all", "train", "validation", "holdout"]}


def transfer_target_pass(source_metrics: Dict[str, Dict[str, Any]], target_metrics: Dict[str, Dict[str, Any]]) -> bool:
    source_splits = ["validation", "holdout"]
    target_splits = ["all", "train", "validation", "holdout"]
    return (
        all((source_metrics[split]["coverage"] or 0.0) >= MARKET_COVERAGE_FLOOR for split in source_splits)
        and all((source_metrics[split]["accuracy"] or 0.0) >= TARGET_ACCURACY for split in source_splits)
        and all((target_metrics[split]["coverage"] or 0.0) >= MARKET_COVERAGE_FLOOR for split in target_splits)
        and all((target_metrics[split]["accuracy"] or 0.0) >= TARGET_ACCURACY for split in target_splits)
        and target_metrics["all"]["markets"] >= MIN_SELECTED_MARKETS
        and target_metrics["holdout"]["markets"] >= MIN_HOLDOUT_SELECTED_MARKETS
    )


def transfer_wilson_pass(source_metrics: Dict[str, Dict[str, Any]], target_metrics: Dict[str, Dict[str, Any]]) -> bool:
    return transfer_target_pass(source_metrics, target_metrics) and all(
        (metrics[split]["wilson95_lower"] or 0.0) >= TARGET_ACCURACY
        for metrics, splits in [(source_metrics, ["validation", "holdout"]), (target_metrics, ["all", "train", "validation", "holdout"])]
        for split in splits
    )


def flatten(
    train_dataset: str,
    scheme: Scheme,
    score_col: str,
    threshold: float,
    min_cell_n: int,
    ask_cap: float,
    min_sec: float,
    source_metrics: Dict[str, Dict[str, Any]],
    target_metrics: Dict[str, Dict[str, Any]],
) -> Dict[str, Any]:
    row: Dict[str, Any] = {
        "train_dataset": train_dataset,
        "scheme": scheme.name,
        "features": ",".join(scheme.features),
        "score_col": score_col,
        "threshold": threshold,
        "min_cell_n": min_cell_n,
        "ask_cap": ask_cap,
        "min_seconds": min_sec,
        "transfer_target_pass": transfer_target_pass(source_metrics, target_metrics),
        "transfer_wilson_pass": transfer_wilson_pass(source_metrics, target_metrics),
        "min_oos_accuracy": min(
            source_metrics["validation"]["accuracy"] or 0.0,
            source_metrics["holdout"]["accuracy"] or 0.0,
            target_metrics["all"]["accuracy"] or 0.0,
            target_metrics["validation"]["accuracy"] or 0.0,
            target_metrics["holdout"]["accuracy"] or 0.0,
        ),
        "min_oos_coverage": min(
            source_metrics["validation"]["coverage"] or 0.0,
            source_metrics["holdout"]["coverage"] or 0.0,
            target_metrics["all"]["coverage"] or 0.0,
            target_metrics["validation"]["coverage"] or 0.0,
            target_metrics["holdout"]["coverage"] or 0.0,
        ),
        "max_median_ask": max(source_metrics["all"]["median_ask"] or 0.0, target_metrics["all"]["median_ask"] or 0.0),
        "max_ask_eq_100": max(source_metrics["all"]["ask_eq_100"], target_metrics["all"]["ask_eq_100"]),
    }
    for prefix, metrics in [("source", source_metrics), ("target", target_metrics)]:
        for split, metric in metrics.items():
            for key, value in metric.items():
                row[f"{prefix}_{split}_{key}"] = value
    return row


def rank_key(row: Dict[str, Any]) -> tuple:
    return (
        int(row["transfer_wilson_pass"]),
        int(row["transfer_target_pass"]),
        row["min_oos_accuracy"],
        row["min_oos_coverage"],
        -(row["max_median_ask"] or 100.0),
        -row["max_ask_eq_100"],
    )


def prepare_dataset(name: str, rows: pd.DataFrame) -> Dict[str, Any]:
    rows = add_bins(rows)
    base = market_base(rows)
    rows = rows.merge(base[["market", "split"]], on="market", how="inner")
    return {"name": name, "rows": rows, "base": base}


def scan_direction(source: Dict[str, Any], target: Dict[str, Any]) -> List[Dict[str, Any]]:
    source_train = source["rows"][source["rows"]["split"] == "train"].copy()
    results: List[Dict[str, Any]] = []
    for scheme in SCHEMES:
        table = cell_table(source_train, scheme)
        if table.empty:
            continue
        source_scored = apply_table(source["rows"], table, scheme)
        target_scored = apply_table(target["rows"], table, scheme)
        for score_col, thresholds in [("emp_p", PROB_THRESHOLDS), ("emp_lower", LOWER_THRESHOLDS)]:
            source_chosen = choose_decision_sides(source_scored, score_col)
            target_chosen = choose_decision_sides(target_scored, score_col)
            for threshold in thresholds:
                for min_cell_n in MIN_CELL_NS:
                    for ask_cap in ASK_CAPS:
                        for min_sec in MIN_SECONDS:
                            source_selected = select_markets(source_chosen, score_col, threshold, min_cell_n, ask_cap, min_sec)
                            target_selected = select_markets(target_chosen, score_col, threshold, min_cell_n, ask_cap, min_sec)
                            results.append(
                                flatten(
                                    source["name"],
                                    scheme,
                                    score_col,
                                    threshold,
                                    min_cell_n,
                                    ask_cap,
                                    min_sec,
                                    metrics_for(source["base"], source_selected),
                                    metrics_for(target["base"], target_selected),
                                )
                            )
    return results


def table_lines(rows: List[Dict[str, Any]], limit: int = 15) -> List[str]:
    lines = [
        "| rank | train | scheme | score | gate | source val/holdout | target all/holdout | min oos acc | min oos cov | median ask | target |",
        "|---:|---|---|---|---|---:|---:|---:|---:|---:|---|",
    ]
    for idx, row in enumerate(rows[:limit], start=1):
        gate = f"{row['score_col']}>={row['threshold']}; n>={row['min_cell_n']}; ask<={row['ask_cap']}; sec>={row['min_seconds']}"
        lines.append(
            "| {rank} | {train} | `{scheme}` | `{score}` | `{gate}` | {sval}/{shold} | {tall}/{thold} | {minacc} | {mincov} | {ask} | {target} |".format(
                rank=idx,
                train=row["train_dataset"],
                scheme=row["scheme"],
                score=row["score_col"],
                gate=gate,
                sval=pct(row.get("source_validation_accuracy")),
                shold=pct(row.get("source_holdout_accuracy")),
                tall=pct(row.get("target_all_accuracy")),
                thold=pct(row.get("target_holdout_accuracy")),
                minacc=pct(row.get("min_oos_accuracy")),
                mincov=pct(row.get("min_oos_coverage")),
                ask=fmt(row.get("max_median_ask")),
                target=row["transfer_target_pass"],
            )
        )
    return lines


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    generated = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%SZ")
    current = prepare_dataset("current", load_side_rows())
    v21 = prepare_dataset("v21", load_v21_side_rows())
    rows = scan_direction(current, v21)
    rows.extend(scan_direction(v21, current))
    rows.sort(key=rank_key, reverse=True)

    df = pd.DataFrame(rows)
    csv_path = OUT_DIR / f"cross_dataset_empirical_survival_{generated}.csv"
    df.to_csv(csv_path, index=False)
    df.to_csv(OUT_DIR / "cross_dataset_empirical_survival_latest.csv", index=False)

    passes = [row for row in rows if row["transfer_target_pass"]]
    wilson = [row for row in rows if row["transfer_wilson_pass"]]
    summary = {
        "generated_utc": generated,
        "current_intervals": int(len(current["base"])),
        "v21_intervals": int(len(v21["base"])),
        "current_rows": int(len(current["rows"])),
        "v21_rows": int(len(v21["rows"])),
        "candidate_rows": int(len(rows)),
        "transfer_target_pass": int(len(passes)),
        "transfer_wilson_pass": int(len(wilson)),
        "top": rows[:25],
    }
    json_text = json.dumps(clean_json_local(summary), indent=2, sort_keys=True)
    json_path = OUT_DIR / f"cross_dataset_empirical_survival_{generated}.json"
    json_path.write_text(json_text, encoding="utf-8")
    (OUT_DIR / "cross_dataset_empirical_survival_latest.json").write_text(json_text, encoding="utf-8")

    md_path = OUT_DIR / f"cross_dataset_empirical_survival_{generated}.md"
    lines = [
        "# Cross-Dataset Empirical Survival",
        "",
        f"Generated UTC: `{generated}`",
        "",
        "## Scope",
        "",
        "- Research-only probe; no orders are submitted and no bot files are modified.",
        "- Replaces parametric Brownian probability with empirical live-state survival tables.",
        "- Tables train only on one capture's chronological train split, then transfer without retuning to the other capture.",
        "- Target requires source validation/holdout and target all/train/validation/holdout to clear 95% accuracy and 80% recurring-market coverage.",
        "",
        "## Data",
        "",
        f"- Current intervals: {len(current['base'])}; rows: {len(current['rows'])}",
        f"- V21 intervals: {len(v21['base'])}; rows: {len(v21['rows'])}",
        f"- Candidate rows evaluated: {len(rows)}",
        f"- Transfer target passes: {len(passes)}",
        f"- Transfer Wilson passes: {len(wilson)}",
        "",
        "## Top Empirical Survival Transfers",
        "",
    ]
    lines.extend(table_lines(rows))
    lines.extend(
        [
            "",
            "## Read",
            "",
        ]
    )
    if passes:
        lines.append("- At least one empirical survival transfer cleared the raw target; inspect Wilson and degeneracy before promotion.")
    else:
        lines.append("- No empirical survival transfer cleared the 95% accuracy / 80% recurring-market target.")
    best = rows[0]
    lines.append(
        "- Best row trained on {train} with scheme `{scheme}`; min OOS accuracy {acc}, min OOS coverage {cov}, max median ask {ask}c.".format(
            train=best["train_dataset"],
            scheme=best["scheme"],
            acc=pct(best["min_oos_accuracy"]),
            cov=pct(best["min_oos_coverage"]),
            ask=fmt(best["max_median_ask"]),
        )
    )
    lines.append("- If target passes remain zero, the empirical-state prior does not overcome the broad-coverage physics frontier.")
    md_text = "\n".join(lines) + "\n"
    md_path.write_text(md_text, encoding="utf-8")
    (OUT_DIR / "cross_dataset_empirical_survival_latest.md").write_text(md_text, encoding="utf-8")

    print("Cross-dataset empirical survival complete")
    print(f"candidate_rows={len(rows)} transfer_target_pass={len(passes)}")
    print(f"report={md_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
