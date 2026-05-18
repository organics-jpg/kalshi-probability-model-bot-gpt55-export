"""Tail-calibrated physics scan for BTC 15m interval policies.

The current raw interval passes mostly come from expensive near-settlement
states. This probe questions the Brownian prior itself by inflating the
realized-volatility terminal distribution, then testing whether any calibrated
physics-only policy clears 95% realized accuracy while selecting at least 80%
of recurring BTC 15-minute markets on both the current live heartbeat capture
and the independent v21 passive websocket capture.

Research-only: no orders are submitted and no bot files or live processes are
modified.
"""
from __future__ import annotations

import json
import math
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

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
    clean_json,
    load_side_rows,
    market_base,
    pct,
)


TAIL_MULTS = [1.0, 1.5, 2.0, 3.0, 4.0]
HORIZONS = ["15m", "30m", "60m"]
THRESHOLDS = [0.55, 0.60, 0.65, 0.70, 0.75, 0.80, 0.85, 0.90, 0.95]
ASK_CAPS = [90.0, 95.0, 100.0]
MIN_SECONDS = [0.0, 60.0, 120.0]
GATES = ["none", "spread<=4", "adverse15<=10", "margin_rv15>=0"]
CALIBRATION_BINS = [0.50, 0.60, 0.70, 0.80, 0.90, 0.95, 0.975, 1.001]


@dataclass(frozen=True)
class TailPolicy:
    chooser: str
    min_score: float
    ask_max: float
    min_seconds_to_close: float
    gate: str

    @property
    def label(self) -> str:
        return (
            f"tail={self.chooser}; {self.chooser}>={self.min_score:g}; "
            f"ask<={self.ask_max:g}; sec>={self.min_seconds_to_close:g}; gate={self.gate}"
        )


def mult_label(mult: float) -> str:
    return f"{int(round(mult * 100)):03d}"


def norm_cdf(z: pd.Series) -> pd.Series:
    values = pd.to_numeric(z, errors="coerce").astype(float)
    erf = np.vectorize(lambda x: math.erf(x / math.sqrt(2.0)) if math.isfinite(x) else np.nan)
    return pd.Series(0.5 * (1.0 + erf(values.to_numpy())), index=values.index)


def add_tail_calibrated_scores(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    for horizon in HORIZONS:
        margin_col = f"margin_per_rv_sigma_{horizon}"
        if margin_col not in out.columns:
            out[margin_col] = np.nan
        for mult in TAIL_MULTS:
            label = mult_label(mult)
            out[f"tail_p_rv_{horizon}_{label}"] = norm_cdf(out[margin_col] / mult)
    for mult in TAIL_MULTS:
        label = mult_label(mult)
        cols = [f"tail_p_rv_{horizon}_{label}" for horizon in HORIZONS]
        out[f"tail_p_mean_rv_{label}"] = out[cols].mean(axis=1)
        out[f"tail_p_min_rv_{label}"] = out[cols].min(axis=1)
    return out


def chooser_columns() -> List[str]:
    cols: List[str] = []
    for mult in TAIL_MULTS:
        label = mult_label(mult)
        cols.extend([f"tail_p_rv_{horizon}_{label}" for horizon in HORIZONS])
        cols.extend([f"tail_p_mean_rv_{label}", f"tail_p_min_rv_{label}"])
    return cols


def make_policies() -> List[TailPolicy]:
    return [
        TailPolicy(chooser, threshold, ask_cap, min_sec, gate)
        for chooser in chooser_columns()
        for threshold in THRESHOLDS
        for ask_cap in ASK_CAPS
        for min_sec in MIN_SECONDS
        for gate in GATES
    ]


def gate_mask(chosen: pd.DataFrame, policy: TailPolicy) -> pd.Series:
    mask = (
        chosen[policy.chooser].ge(policy.min_score)
        & chosen["ask_cents"].le(policy.ask_max)
        & chosen["seconds_to_close"].ge(policy.min_seconds_to_close)
    )
    if policy.gate == "none":
        return mask.fillna(False)
    if policy.gate == "spread<=4":
        mask &= chosen["spread_cents"].le(4)
    elif policy.gate == "adverse15<=10":
        mask &= chosen["adverse_move_15m"].le(10)
    elif policy.gate == "margin_rv15>=0":
        mask &= chosen["margin_per_rv_sigma_15m"].ge(0)
    elif policy.gate == "rv15<=150":
        mask &= chosen["rv_sigma_t_15m"].le(150)
    else:
        raise ValueError(f"unknown gate: {policy.gate}")
    return mask.fillna(False)


def choose_decision_sides(side_rows: pd.DataFrame, chooser: str) -> pd.DataFrame:
    usable = side_rows[side_rows[chooser].notna()].copy()
    if usable.empty:
        return usable
    return (
        usable.sort_values(
            ["decision_key", chooser, "margin_per_rv_sigma_30m", "seconds_to_close"],
            ascending=[True, False, False, True],
        )
        .groupby("decision_key", as_index=False, sort=False)
        .first()
        .sort_values(["market", "entry_dt"])
        .reset_index(drop=True)
    )


def select_markets(chosen: pd.DataFrame, policy: TailPolicy) -> pd.DataFrame:
    if chosen.empty:
        return chosen.copy()
    eligible = chosen[gate_mask(chosen, policy)].copy()
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
        "ask_ge_95": int(selected_part["ask_cents"].ge(95).sum()) if n else 0,
        "ask_eq_100": int(selected_part["ask_cents"].ge(100).sum()) if n else 0,
        "median_seconds_to_close": float(selected_part["seconds_to_close"].median()) if n else None,
        "gross_pnl_cents": pnl,
        "gross_roi": pnl / stake if stake else None,
    }


def metrics_for(base: pd.DataFrame, selected: pd.DataFrame) -> Dict[str, Dict[str, Any]]:
    return {split: split_metric(base, selected, split) for split in ["all", "train", "validation", "holdout"]}


def coverage_pass(metrics: Dict[str, Dict[str, Any]]) -> bool:
    return all((metrics[split]["coverage"] or 0.0) >= MARKET_COVERAGE_FLOOR for split in metrics)


def target_pass(metrics: Dict[str, Dict[str, Any]]) -> bool:
    return (
        coverage_pass(metrics)
        and all((metrics[split]["accuracy"] or 0.0) >= TARGET_ACCURACY for split in metrics)
        and metrics["all"]["markets"] >= MIN_SELECTED_MARKETS
        and metrics["holdout"]["markets"] >= MIN_HOLDOUT_SELECTED_MARKETS
    )


def wilson_pass(metrics: Dict[str, Dict[str, Any]]) -> bool:
    return target_pass(metrics) and all(
        (metrics[split]["wilson95_lower"] or 0.0) >= TARGET_ACCURACY for split in metrics
    )


def nondegenerate(policy: TailPolicy, current_metrics: Dict[str, Dict[str, Any]], v21_metrics: Dict[str, Dict[str, Any]]) -> bool:
    return (
        policy.ask_max <= 95.0
        and policy.min_seconds_to_close >= 60.0
        and (current_metrics["all"]["median_ask"] or 100.0) <= 90.0
        and (v21_metrics["all"]["median_ask"] or 100.0) <= 90.0
        and current_metrics["all"]["ask_eq_100"] == 0
        and v21_metrics["all"]["ask_eq_100"] == 0
    )


def min_metric(metrics_list: List[Dict[str, Dict[str, Any]]], key: str) -> float:
    values = [
        metrics[split][key] or 0.0
        for metrics in metrics_list
        for split in ["all", "train", "validation", "holdout"]
    ]
    return min(values) if values else 0.0


def flatten(policy: TailPolicy, current_metrics: Dict[str, Dict[str, Any]], v21_metrics: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
    current_target = target_pass(current_metrics)
    v21_target = target_pass(v21_metrics)
    current_wilson = wilson_pass(current_metrics)
    v21_wilson = wilson_pass(v21_metrics)
    current_cov = coverage_pass(current_metrics)
    v21_cov = coverage_pass(v21_metrics)
    row: Dict[str, Any] = {
        "label": policy.label,
        "chooser": policy.chooser,
        "min_score": policy.min_score,
        "ask_max": policy.ask_max,
        "min_seconds_to_close": policy.min_seconds_to_close,
        "gate": policy.gate,
        "current_target_pass": current_target,
        "v21_target_pass": v21_target,
        "both_target_pass": current_target and v21_target,
        "current_wilson_pass": current_wilson,
        "v21_wilson_pass": v21_wilson,
        "both_wilson_pass": current_wilson and v21_wilson,
        "both_coverage_pass": current_cov and v21_cov,
        "nondegenerate": nondegenerate(policy, current_metrics, v21_metrics),
        "min_split_accuracy": min_metric([current_metrics, v21_metrics], "accuracy"),
        "min_split_coverage": min_metric([current_metrics, v21_metrics], "coverage"),
        "min_split_wilson": min_metric([current_metrics, v21_metrics], "wilson95_lower"),
        "max_median_ask": max(current_metrics["all"]["median_ask"] or 0.0, v21_metrics["all"]["median_ask"] or 0.0),
        "max_ask_eq_100": max(current_metrics["all"]["ask_eq_100"], v21_metrics["all"]["ask_eq_100"]),
    }
    for prefix, metrics in [("current", current_metrics), ("v21", v21_metrics)]:
        for split, metric in metrics.items():
            for key, value in metric.items():
                row[f"{prefix}_{split}_{key}"] = value
    return row


def evaluate_dataset(side_rows: pd.DataFrame, base: pd.DataFrame, policies: List[TailPolicy]) -> Dict[str, Dict[str, Any]]:
    side_rows = side_rows.merge(base[["market", "split"]], on="market", how="inner")
    policies_by_chooser: Dict[str, List[TailPolicy]] = {}
    for policy in policies:
        policies_by_chooser.setdefault(policy.chooser, []).append(policy)
    out: Dict[str, Dict[str, Any]] = {}
    for chooser in chooser_columns():
        chosen = choose_decision_sides(side_rows, chooser)
        for policy in policies_by_chooser.get(chooser, []):
            selected = select_markets(chosen, policy)
            out[policy.label] = {"selected": selected, "metrics": metrics_for(base, selected)}
    return out


def calibration_rows(dataset: str, side_rows: pd.DataFrame, score_cols: List[str]) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    for score_col in score_cols:
        chosen = choose_decision_sides(side_rows, score_col)
        if chosen.empty:
            continue
        score = chosen[score_col].astype(float)
        bins = pd.cut(score, CALIBRATION_BINS, right=False, include_lowest=True)
        grouped = chosen.assign(score_bin=bins).groupby("score_bin", observed=False)
        for bucket, part in grouped:
            n = int(len(part))
            if not n:
                continue
            wins = int(part["win"].sum())
            rows.append(
                {
                    "dataset": dataset,
                    "score": score_col,
                    "bin": str(bucket),
                    "rows": n,
                    "wins": wins,
                    "accuracy": wins / n,
                    "mean_score": float(part[score_col].mean()),
                    "median_ask": float(part["ask_cents"].median()),
                    "median_seconds_to_close": float(part["seconds_to_close"].median()),
                }
            )
    return rows


def rank_key(row: Dict[str, Any]) -> tuple:
    return (
        int(row["both_wilson_pass"]),
        int(row["both_target_pass"]),
        int(row["both_coverage_pass"]),
        int(row["nondegenerate"]),
        row["min_split_accuracy"],
        row["min_split_coverage"],
        row["min_split_wilson"],
        -(row["max_median_ask"] or 100.0),
        -row["max_ask_eq_100"],
    )


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


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%SZ")

    current_rows = add_tail_calibrated_scores(load_side_rows())
    v21_rows = add_tail_calibrated_scores(load_v21_side_rows())
    current_base = market_base(current_rows)
    v21_base = market_base(v21_rows)
    policies = make_policies()

    current_eval = evaluate_dataset(current_rows, current_base, policies)
    v21_eval = evaluate_dataset(v21_rows, v21_base, policies)

    rows: List[Dict[str, Any]] = []
    for policy in policies:
        current_metrics = current_eval[policy.label]["metrics"]
        v21_metrics = v21_eval[policy.label]["metrics"]
        rows.append(flatten(policy, current_metrics, v21_metrics))
    rows.sort(key=rank_key, reverse=True)

    candidates_df = pd.DataFrame(rows)
    candidates_path = OUT_DIR / f"interval_tail_calibrated_physics_{ts}.csv"
    candidates_df.to_csv(candidates_path, index=False)
    candidates_df.to_csv(OUT_DIR / "interval_tail_calibrated_physics_latest.csv", index=False)

    calibration_scores = [
        "brownian_p_rv_30m",
        "tail_p_rv_30m_100",
        "tail_p_rv_30m_150",
        "tail_p_rv_30m_200",
        "tail_p_rv_30m_300",
        "tail_p_mean_rv_200",
        "tail_p_min_rv_200",
    ]
    calibration = calibration_rows("current", current_rows, calibration_scores)
    calibration.extend(calibration_rows("v21", v21_rows, calibration_scores))
    calibration_df = pd.DataFrame(calibration)
    calibration_path = OUT_DIR / f"interval_tail_calibration_bins_{ts}.csv"
    calibration_df.to_csv(calibration_path, index=False)
    calibration_df.to_csv(OUT_DIR / "interval_tail_calibration_bins_latest.csv", index=False)

    both_target = [row for row in rows if row["both_target_pass"]]
    both_wilson = [row for row in rows if row["both_wilson_pass"]]
    nondeg_target = [row for row in rows if row["both_target_pass"] and row["nondegenerate"]]
    coverage_rows = [row for row in rows if row["both_coverage_pass"]]
    best = rows[:25]

    summary = {
        "generated_utc": ts,
        "current_intervals": int(len(current_base)),
        "v21_intervals": int(len(v21_base)),
        "current_rows": int(len(current_rows)),
        "v21_rows": int(len(v21_rows)),
        "policies_scanned": int(len(rows)),
        "both_coverage_pass": int(len(coverage_rows)),
        "both_target_pass": int(len(both_target)),
        "both_wilson_pass": int(len(both_wilson)),
        "nondegenerate_both_target_pass": int(len(nondeg_target)),
        "best": best,
    }
    json_path = OUT_DIR / f"interval_tail_calibrated_physics_{ts}.json"
    json_path.write_text(json.dumps(clean_json_local(summary), indent=2), encoding="utf-8")
    (OUT_DIR / "interval_tail_calibrated_physics_latest.json").write_text(
        json.dumps(clean_json_local(summary), indent=2), encoding="utf-8"
    )

    md_path = OUT_DIR / f"interval_tail_calibrated_physics_{ts}.md"
    lines = [
        "# Tail-Calibrated Physics Interval Probe",
        "",
        f"Generated UTC: `{ts}`",
        "",
        "## Scope",
        "",
        "- Research-only scan; no orders are submitted and no bot files are modified.",
        "- Inflates realized-volatility terminal Brownian sigma before converting margin to probability.",
        "- Uses only physics-side scores for side choice; book probability is not a chooser or model feature.",
        "- Tests the same policy on the current live heartbeat interval ledger and independent v21 passive websocket interval ledger.",
        "- Unit of volume is recurring BTC 15-minute markets.",
        "",
        "## Data",
        "",
        f"- Current intervals: {len(current_base)}; rows: {len(current_rows)}",
        f"- V21 intervals: {len(v21_base)}; rows: {len(v21_rows)}",
        f"- Tail-calibrated policies scanned: {len(rows)}",
        f"- Policies preserving 80% coverage on both captures/splits: {len(coverage_rows)}",
        f"- Policies passing 95% / 80% on both captures: {len(both_target)}",
        f"- Policies with 95% Wilson lower bound on both captures: {len(both_wilson)}",
        f"- Nondegenerate both-capture target passes: {len(nondeg_target)}",
        "",
        "## Top Shared Policies",
        "",
        "| rank | policy | current acc/cov | v21 acc/cov | min split acc | min split cov | max median ask | ask=100 max | both target | nondeg |",
        "|---:|---|---:|---:|---:|---:|---:|---:|---|---|",
    ]
    for idx, row in enumerate(best[:15], start=1):
        lines.append(
            "| {rank} | `{label}` | {cur_acc}/{cur_cov} | {v21_acc}/{v21_cov} | {min_acc} | {min_cov} | {ask} | {ask100} | {target} | {nondeg} |".format(
                rank=idx,
                label=row["label"],
                cur_acc=pct(row.get("current_all_accuracy")),
                cur_cov=pct(row.get("current_all_coverage")),
                v21_acc=pct(row.get("v21_all_accuracy")),
                v21_cov=pct(row.get("v21_all_coverage")),
                min_acc=pct(row.get("min_split_accuracy")),
                min_cov=pct(row.get("min_split_coverage")),
                ask=fmt(row.get("max_median_ask")),
                ask100=int(row.get("max_ask_eq_100") or 0),
                target=row["both_target_pass"],
                nondeg=row["nondegenerate"],
            )
        )
    lines.extend(
        [
            "",
            "## Read",
            "",
        ]
    )
    if both_target:
        lines.append("- At least one tail-calibrated physics policy cleared the shared raw target; inspect degeneracy and Wilson rows before promotion.")
    else:
        lines.append("- No tail-calibrated physics-only policy cleared the 95% accuracy / 80% recurring-market target on both captures.")
    if coverage_rows:
        top_cov = coverage_rows[0]
        lines.append(
            "- Best shared 80%-coverage row had min split accuracy {acc} and max median ask {ask}c.".format(
                acc=pct(top_cov.get("min_split_accuracy")),
                ask=fmt(top_cov.get("max_median_ask")),
            )
        )
    lines.append("- Tail inflation is a useful prior audit, but it does not by itself solve the high-volume physics frontier.")
    md_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    (OUT_DIR / "interval_tail_calibrated_physics_latest.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"wrote {md_path}")
    print(f"wrote {candidates_path}")
    print(f"wrote {calibration_path}")


if __name__ == "__main__":
    main()
