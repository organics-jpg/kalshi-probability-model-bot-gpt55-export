"""Cross-dataset path-stability gates for BTC 15m interval policies.

The economical interval frontier loses because terminal/book probabilities can
be favorable while the path is unstable. This probe tests that prior directly:
it adds causal pre-entry stability gates to economical base policies, allowing
the policy to wait for a later heartbeat in the same recurring market.

Research-only: no orders are submitted and no bot files or live processes are
modified.
"""
from __future__ import annotations

import itertools
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
    Policy,
    add_scores,
    choose_decision_sides,
    clean_json,
    gate_mask,
    load_side_rows,
    market_base,
    pct,
)


BASE_POLICIES = [
    Policy("book_p_side", 0.80, 95.0, 60.0, "adverse15<=10_or_margin_rv15>=0.5"),
    Policy("score_mean_book_rv15", 0.80, 95.0, 60.0, "none"),
    Policy("score_min_book_rv15", 0.80, 95.0, 60.0, "none"),
    Policy("score_regime_blend", 0.80, 95.0, 60.0, "none"),
]


@dataclass(frozen=True)
class Gate:
    feature: str
    op: str
    threshold: float

    @property
    def label(self) -> str:
        return f"{self.feature}{self.op}{self.threshold:g}"

    def mask(self, rows: pd.DataFrame) -> pd.Series:
        values = pd.to_numeric(rows.get(self.feature), errors="coerce")
        if self.op == ">=":
            return values.ge(self.threshold).fillna(False)
        if self.op == "<=":
            return values.le(self.threshold).fillna(False)
        raise ValueError(f"unknown op {self.op}")


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


def add_path_stability_features(rows: pd.DataFrame) -> pd.DataFrame:
    out = add_scores(rows).copy()
    for col in ["book_p_side", "ask_cents", "signed_move_1m", "signed_move_3m", "signed_move_5m", "adverse_move_5m", "adverse_move_15m"]:
        if col not in out.columns:
            out[col] = np.nan
        out[col] = pd.to_numeric(out[col], errors="coerce")

    out = out.sort_values(["market", "side", "entry_dt", "decision_key"]).reset_index(drop=True)
    grouped = out.groupby(["market", "side"], sort=False)
    for window in [4, 8, 12]:
        roll_book = grouped["book_p_side"].rolling(window=window, min_periods=1)
        out[f"book_min_{window}"] = roll_book.min().reset_index(level=[0, 1], drop=True)
        out[f"book_max_{window}"] = roll_book.max().reset_index(level=[0, 1], drop=True)
        out[f"book_range_{window}"] = out[f"book_max_{window}"] - out[f"book_min_{window}"]
        out[f"book_drawdown_{window}"] = out[f"book_max_{window}"] - out["book_p_side"]
        out[f"book_runup_{window}"] = out["book_p_side"] - out[f"book_min_{window}"]

        roll_ask = grouped["ask_cents"].rolling(window=window, min_periods=1)
        out[f"ask_range_{window}"] = (
            roll_ask.max().reset_index(level=[0, 1], drop=True)
            - roll_ask.min().reset_index(level=[0, 1], drop=True)
        )

    for lag in [1, 4, 8, 12]:
        out[f"book_delta_{lag}"] = out["book_p_side"] - grouped["book_p_side"].shift(lag)
        out[f"ask_delta_{lag}"] = out["ask_cents"] - grouped["ask_cents"].shift(lag)

    out["fav_move_count_1_3_5"] = (
        out[["signed_move_1m", "signed_move_3m", "signed_move_5m"]].ge(0).sum(axis=1)
    )
    out["adv_move_max_1_3_5"] = (
        -out[["signed_move_1m", "signed_move_3m", "signed_move_5m"]].clip(upper=0)
    ).max(axis=1)
    out["trend_consistent_1_3_5"] = out["fav_move_count_1_3_5"].isin([0, 3]).astype(float)

    if {"rv_sigma_t_5m", "rv_sigma_t_15m"}.issubset(out.columns):
        out["rv_ratio_5_15"] = pd.to_numeric(out["rv_sigma_t_5m"], errors="coerce") / pd.to_numeric(
            out["rv_sigma_t_15m"], errors="coerce"
        ).replace(0, np.nan)
    if {"rv_sigma_t_15m", "rv_sigma_t_30m"}.issubset(out.columns):
        out["rv_ratio_15_30"] = pd.to_numeric(out["rv_sigma_t_15m"], errors="coerce") / pd.to_numeric(
            out["rv_sigma_t_30m"], errors="coerce"
        ).replace(0, np.nan)
    return out


def make_gates() -> List[Gate]:
    specs = {
        "book_min_4": (">=", [0.70, 0.75, 0.80, 0.85]),
        "book_min_8": (">=", [0.65, 0.70, 0.75, 0.80]),
        "book_range_4": ("<=", [0.08, 0.12, 0.16, 0.20]),
        "book_range_8": ("<=", [0.12, 0.18, 0.25, 0.30]),
        "book_drawdown_4": ("<=", [0.03, 0.05, 0.08, 0.10]),
        "book_drawdown_8": ("<=", [0.05, 0.08, 0.12, 0.16]),
        "book_delta_4": (">=", [-0.05, 0.00, 0.05]),
        "book_delta_8": (">=", [-0.05, 0.00, 0.05]),
        "ask_range_8": ("<=", [5.0, 8.0, 10.0, 15.0]),
        "fav_move_count_1_3_5": (">=", [2.0, 3.0]),
        "adv_move_max_1_3_5": ("<=", [0.0, 5.0, 10.0, 20.0]),
        "adverse_move_5m": ("<=", [0.0, 5.0, 10.0, 20.0]),
        "adverse_move_15m": ("<=", [0.0, 10.0, 20.0, 35.0]),
        "rv_ratio_5_15": ("<=", [0.75, 1.0, 1.25, 1.5]),
        "rv_ratio_15_30": ("<=", [0.75, 1.0, 1.25, 1.5]),
    }
    gates: List[Gate] = []
    for feature, (op, values) in specs.items():
        for threshold in values:
            gates.append(Gate(feature, op, float(threshold)))
    return gates


def gate_combos() -> List[tuple[Gate, ...]]:
    gates = make_gates()
    book_features = {
        "book_min_4",
        "book_min_8",
        "book_range_4",
        "book_range_8",
        "book_drawdown_4",
        "book_drawdown_8",
        "book_delta_4",
        "book_delta_8",
        "ask_range_8",
    }
    path_features = {
        "fav_move_count_1_3_5",
        "adv_move_max_1_3_5",
        "adverse_move_5m",
        "adverse_move_15m",
        "rv_ratio_5_15",
        "rv_ratio_15_30",
    }
    combos: List[tuple[Gate, ...]] = [tuple()]
    combos.extend((gate,) for gate in gates)
    for first, second in itertools.combinations(gates, 2):
        if (first.feature in book_features and second.feature in path_features) or (
            second.feature in book_features and first.feature in path_features
        ):
            combos.append((first, second))
    return combos


def combo_label(combo: tuple[Gate, ...]) -> str:
    return "none" if not combo else " AND ".join(gate.label for gate in combo)


def combo_mask(rows: pd.DataFrame, combo: tuple[Gate, ...]) -> pd.Series:
    mask = pd.Series(True, index=rows.index)
    for gate in combo:
        mask &= gate.mask(rows)
    return mask.fillna(False)


def select_with_gates(side_rows: pd.DataFrame, base: pd.DataFrame, policy: Policy, combo: tuple[Gate, ...]) -> pd.DataFrame:
    rows = side_rows.merge(base[["market", "split"]], on="market", how="inner")
    chosen = choose_decision_sides(rows, policy.chooser)
    return select_from_chosen(chosen, policy, combo)


def select_from_chosen(chosen: pd.DataFrame, policy: Policy, combo: tuple[Gate, ...]) -> pd.DataFrame:
    eligible = chosen[gate_mask(chosen, policy) & combo_mask(chosen, combo)].copy()
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


def min_metric(metrics_list: Iterable[Dict[str, Dict[str, Any]]], key: str) -> float:
    values = [
        metrics[split][key] or 0.0
        for metrics in metrics_list
        for split in ["all", "train", "validation", "holdout"]
    ]
    return min(values) if values else 0.0


def flatten(
    policy: Policy,
    combo: tuple[Gate, ...],
    current_metrics: Dict[str, Dict[str, Any]],
    v21_metrics: Dict[str, Dict[str, Any]],
) -> Dict[str, Any]:
    current_target = target_pass(current_metrics)
    v21_target = target_pass(v21_metrics)
    current_wilson = wilson_pass(current_metrics)
    v21_wilson = wilson_pass(v21_metrics)
    row: Dict[str, Any] = {
        "base_policy": policy.label,
        "gate_combo": combo_label(combo),
        "both_coverage_pass": coverage_pass(current_metrics) and coverage_pass(v21_metrics),
        "both_target_pass": current_target and v21_target,
        "both_wilson_pass": current_wilson and v21_wilson,
        "current_target_pass": current_target,
        "v21_target_pass": v21_target,
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


def rank_key(row: Dict[str, Any]) -> tuple:
    return (
        int(row["both_wilson_pass"]),
        int(row["both_target_pass"]),
        int(row["both_coverage_pass"]),
        row["min_split_accuracy"],
        row["min_split_coverage"],
        row["min_split_wilson"],
        -(row["max_median_ask"] or 100.0),
        -row["max_ask_eq_100"],
    )


def table_lines(rows: List[Dict[str, Any]], limit: int = 15) -> List[str]:
    lines = [
        "| rank | base policy | stability gates | current acc/cov | v21 acc/cov | min split acc | min split cov | max median ask | target |",
        "|---:|---|---|---:|---:|---:|---:|---:|---|",
    ]
    for idx, row in enumerate(rows[:limit], start=1):
        lines.append(
            "| {rank} | `{base}` | `{gate}` | {cur_acc}/{cur_cov} | {v21_acc}/{v21_cov} | {min_acc} | {min_cov} | {ask} | {target} |".format(
                rank=idx,
                base=row["base_policy"],
                gate=row["gate_combo"],
                cur_acc=pct(row.get("current_all_accuracy")),
                cur_cov=pct(row.get("current_all_coverage")),
                v21_acc=pct(row.get("v21_all_accuracy")),
                v21_cov=pct(row.get("v21_all_coverage")),
                min_acc=pct(row.get("min_split_accuracy")),
                min_cov=pct(row.get("min_split_coverage")),
                ask=fmt(row.get("max_median_ask")),
                target=row["both_target_pass"],
            )
        )
    return lines


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    generated = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%SZ")

    current_rows = add_path_stability_features(load_side_rows())
    v21_rows = add_path_stability_features(load_v21_side_rows())
    current_base = market_base(current_rows)
    v21_base = market_base(v21_rows)
    combos = gate_combos()

    rows: List[Dict[str, Any]] = []
    for policy in BASE_POLICIES:
        current_policy_rows = current_rows.merge(current_base[["market", "split"]], on="market", how="inner")
        v21_policy_rows = v21_rows.merge(v21_base[["market", "split"]], on="market", how="inner")
        current_chosen = choose_decision_sides(current_policy_rows, policy.chooser)
        v21_chosen = choose_decision_sides(v21_policy_rows, policy.chooser)
        for combo in combos:
            current_selected = select_from_chosen(current_chosen, policy, combo)
            v21_selected = select_from_chosen(v21_chosen, policy, combo)
            rows.append(
                flatten(
                    policy,
                    combo,
                    metrics_for(current_base, current_selected),
                    metrics_for(v21_base, v21_selected),
                )
            )
    rows.sort(key=rank_key, reverse=True)

    df = pd.DataFrame(rows)
    csv_path = OUT_DIR / f"cross_dataset_path_stability_gates_{generated}.csv"
    df.to_csv(csv_path, index=False)
    df.to_csv(OUT_DIR / "cross_dataset_path_stability_gates_latest.csv", index=False)

    both_target = [row for row in rows if row["both_target_pass"]]
    both_wilson = [row for row in rows if row["both_wilson_pass"]]
    both_coverage = [row for row in rows if row["both_coverage_pass"]]
    summary = {
        "generated_utc": generated,
        "current_intervals": int(len(current_base)),
        "v21_intervals": int(len(v21_base)),
        "current_rows": int(len(current_rows)),
        "v21_rows": int(len(v21_rows)),
        "base_policies": [policy.label for policy in BASE_POLICIES],
        "gate_combos": int(len(combos)),
        "candidate_rows": int(len(rows)),
        "both_coverage_pass": int(len(both_coverage)),
        "both_target_pass": int(len(both_target)),
        "both_wilson_pass": int(len(both_wilson)),
        "top": rows[:25],
    }
    json_path = OUT_DIR / f"cross_dataset_path_stability_gates_{generated}.json"
    json_payload = json.dumps(clean_json_local(summary), indent=2, sort_keys=True)
    json_path.write_text(json_payload, encoding="utf-8")
    (OUT_DIR / "cross_dataset_path_stability_gates_latest.json").write_text(json_payload, encoding="utf-8")

    md_path = OUT_DIR / f"cross_dataset_path_stability_gates_{generated}.md"
    lines = [
        "# Cross-Dataset Path-Stability Gates",
        "",
        f"Generated UTC: `{generated}`",
        "",
        "## Scope",
        "",
        "- Research-only probe; no orders are submitted and no bot files are modified.",
        "- Starts from economical interval policies and requires causal pre-entry path stability.",
        "- If a heartbeat fails the stability gate, the policy can wait for a later heartbeat in the same recurring market.",
        "- Tests the same base policies and gates on current live heartbeat data and independent v21 passive websocket data.",
        "",
        "## Data",
        "",
        f"- Current intervals: {len(current_base)}; rows: {len(current_rows)}",
        f"- V21 intervals: {len(v21_base)}; rows: {len(v21_rows)}",
        f"- Base policies: {len(BASE_POLICIES)}",
        f"- Stability gate combinations: {len(combos)}",
        f"- Candidate rows evaluated: {len(rows)}",
        f"- Both-dataset 80%-coverage rows: {len(both_coverage)}",
        f"- Both-dataset target passes: {len(both_target)}",
        f"- Both-dataset Wilson passes: {len(both_wilson)}",
        "",
        "## Top Shared Path-Stability Gates",
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
    if both_target:
        lines.append("- At least one shared path-stability gate cleared the target; inspect Wilson and degeneracy before promotion.")
    else:
        lines.append("- No shared path-stability gate cleared the 95% accuracy / 80% recurring-market target.")
    if both_coverage:
        best = both_coverage[0]
        lines.append(
            "- Best shared 80%-coverage row had current {cur_acc}/{cur_cov}, v21 {v21_acc}/{v21_cov}, and max median ask {ask}c.".format(
                cur_acc=pct(best.get("current_all_accuracy")),
                cur_cov=pct(best.get("current_all_coverage")),
                v21_acc=pct(best.get("v21_all_accuracy")),
                v21_cov=pct(best.get("v21_all_coverage")),
                ask=fmt(best.get("max_median_ask")),
            )
        )
    lines.append("- This rejects simple pre-entry path persistence as a standalone fix if target-pass rows remain zero.")
    md_text = "\n".join(lines) + "\n"
    md_path.write_text(md_text, encoding="utf-8")
    (OUT_DIR / "cross_dataset_path_stability_gates_latest.md").write_text(md_text, encoding="utf-8")

    print("Cross-dataset path-stability gates complete")
    print(f"candidate_rows={len(rows)} both_target_pass={len(both_target)}")
    print(f"report={md_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
