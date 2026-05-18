"""Research-only market-interval coverage probe for BTC 15m markets.

The user-level volume requirement is at least 80% of recurring BTC 15-minute
markets, not 80% of fills or heartbeat rows. This probe evaluates that unit.

For each resolved BTC 15m ticker seen in the live heartbeat stream, a policy may
fire once. Coverage is selected markets / resolved markets. The policy is
causal within a market: at each heartbeat it chooses one side by a score, applies
an interpretable physics/book/price gate, and the first passing heartbeat
becomes the market's trade.

This is research-only. It reads the two-sided heartbeat ledger and writes under
logs/edge_research. It does not import or modify the live bot.
"""
from __future__ import annotations

import json
import math
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

import numpy as np
import pandas as pd


OUT_DIR = Path("logs/edge_research")
LEDGER = OUT_DIR / "live_heartbeat_two_side_fv_ledger_latest.csv"
MODE = "two_side_all_heartbeats"
LOCK_PATH = OUT_DIR / "market_interval_80coverage_lock.json"

TARGET_ACCURACY = 0.95
MARKET_COVERAGE_FLOOR = 0.80
MIN_SELECTED_MARKETS = 75
MIN_HOLDOUT_SELECTED_MARKETS = 15


def pct(value: Optional[float]) -> str:
    if value is None or not math.isfinite(float(value)):
        return "NA"
    return f"{100.0 * float(value):.2f}%"


def bool_series(series: pd.Series) -> pd.Series:
    if series.dtype == bool:
        return series
    return series.astype(str).str.lower().isin({"true", "1", "yes"})


def clean_json(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(k): clean_json(v) for k, v in value.items()}
    if isinstance(value, list):
        return [clean_json(v) for v in value]
    if isinstance(value, tuple):
        return [clean_json(v) for v in value]
    if isinstance(value, (np.integer,)):
        return int(value)
    if isinstance(value, (np.floating,)):
        if not math.isfinite(float(value)):
            return None
        return float(value)
    if isinstance(value, (np.bool_,)):
        return bool(value)
    if pd.isna(value):
        return None
    return value


def add_scores(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    for col in [
        "book_p_side",
        "brownian_p_rv_15m",
        "brownian_p_rv_30m",
        "brownian_p_rv_60m",
        "drift_p_5m_rv_15m",
        "drift_p_15m_rv_15m",
    ]:
        if col not in out.columns:
            out[col] = np.nan
    out["score_mean_book_rv15"] = out[["book_p_side", "brownian_p_rv_15m"]].mean(axis=1)
    out["score_mean_book_rv30"] = out[["book_p_side", "brownian_p_rv_30m"]].mean(axis=1)
    out["score_mean_book_rv15_drift5"] = out[
        ["book_p_side", "brownian_p_rv_15m", "drift_p_5m_rv_15m"]
    ].mean(axis=1)
    out["score_min_book_rv15"] = out[["book_p_side", "brownian_p_rv_15m"]].min(axis=1)
    out["score_min_book_rv15_drift5"] = out[
        ["book_p_side", "brownian_p_rv_15m", "drift_p_5m_rv_15m"]
    ].min(axis=1)
    out["score_regime_blend"] = (
        0.50 * out["book_p_side"]
        + 0.30 * out["brownian_p_rv_15m"]
        + 0.20 * out["drift_p_5m_rv_15m"]
    )
    out["abs_book_rv15_gap"] = (out["book_p_side"] - out["brownian_p_rv_15m"]).abs()
    out["abs_book_rv30_gap"] = (out["book_p_side"] - out["brownian_p_rv_30m"]).abs()
    out["close_dt"] = out["entry_dt"] + pd.to_timedelta(out["seconds_to_close"], unit="s")
    return out


def load_side_rows() -> pd.DataFrame:
    if not LEDGER.exists():
        raise SystemExit(f"Missing two-sided heartbeat ledger: {LEDGER}")
    df = pd.read_csv(LEDGER, low_memory=False)
    if "two_side_mode" not in df.columns:
        raise SystemExit(f"Ledger lacks two_side_mode: {LEDGER}")
    df = df[df["two_side_mode"] == MODE].copy()
    if df.empty:
        raise SystemExit(f"No rows for {MODE} in {LEDGER}")
    df["entry_dt"] = pd.to_datetime(df["entry_dt"], utc=True, errors="coerce")
    df = df.dropna(subset=["entry_dt", "market", "side", "decision_key"]).copy()
    df["win"] = bool_series(df["win"])
    df["outcome_available"] = bool_series(df["outcome_available"])
    df = df[df["outcome_available"]].copy()

    numeric_cols = [
        "ask_cents",
        "bid_cents",
        "book_mid_cents",
        "book_p_side",
        "book_other_mid_cents",
        "book_margin_cents",
        "spread_cents",
        "spot",
        "strike",
        "seconds_to_close",
        "margin_dollars",
        "margin_per_sqrt_sec",
        "margin_per_sqrt_min",
        "rv_sigma_t_15m",
        "rv_sigma_t_30m",
        "rv_sigma_t_60m",
        "margin_per_rv_sigma_15m",
        "margin_per_rv_sigma_30m",
        "brownian_p_rv_15m",
        "brownian_p_rv_30m",
        "brownian_p_rv_60m",
        "signed_move_1m",
        "signed_move_3m",
        "signed_move_5m",
        "signed_move_15m",
        "adverse_move_1m",
        "adverse_move_3m",
        "adverse_move_5m",
        "adverse_move_15m",
        "drift_projected_margin_5m",
        "drift_projected_margin_15m",
        "drift_p_5m_rv_15m",
        "drift_p_15m_rv_15m",
    ]
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    df = df.dropna(subset=["seconds_to_close"]).copy()
    df = df[df["seconds_to_close"] > 0].copy()
    df = add_scores(df)
    return df.sort_values(["entry_dt", "decision_key", "side"]).reset_index(drop=True)


def market_base(side_rows: pd.DataFrame) -> pd.DataFrame:
    base = (
        side_rows.sort_values(["entry_dt", "market"])
        .groupby("market", as_index=False, sort=False)
        .agg(first_entry_dt=("entry_dt", "min"), close_dt=("close_dt", "max"), outcome=("outcome", "first"))
        .sort_values(["close_dt", "market"])
        .reset_index(drop=True)
    )
    n = len(base)
    train_end = int(math.floor(n * 0.60))
    val_end = int(math.floor(n * 0.80))
    split = np.full(n, "holdout", dtype=object)
    split[:train_end] = "train"
    split[train_end:val_end] = "validation"
    base["split"] = split
    return base


@dataclass(frozen=True)
class Policy:
    chooser: str
    min_score: float
    ask_max: float
    min_seconds_to_close: float
    gate: str = "none"

    @property
    def label(self) -> str:
        parts = [
            f"choose={self.chooser}",
            f"{self.chooser}>={self.min_score:g}",
            f"ask<={self.ask_max:g}",
            f"sec_to_close>={self.min_seconds_to_close:g}",
        ]
        if self.gate != "none":
            parts.append(self.gate)
        return "; ".join(parts)


FIXED_INTERVAL_POLICY = Policy(
    chooser="score_min_book_rv15",
    min_score=0.90,
    ask_max=100.0,
    min_seconds_to_close=0.0,
    gate="none",
)


def make_policies() -> List[Policy]:
    policies: List[Policy] = []
    choosers = [
        "book_p_side",
        "brownian_p_rv_15m",
        "score_mean_book_rv15",
        "score_mean_book_rv15_drift5",
        "score_min_book_rv15",
        "score_regime_blend",
    ]
    thresholds = [0.50, 0.55, 0.60, 0.65, 0.70, 0.80, 0.90, 0.95]
    ask_caps = [90.0, 95.0, 100.0]
    min_seconds = [0.0, 60.0, 120.0]
    gates = [
        "none",
        "adverse15<=10_or_margin_rv15>=0.5",
        "brownian15>=0.55_and_brownian30>=0.55",
        "spread<=4",
        "margin_rv15>=0",
    ]
    for chooser in choosers:
        for threshold in thresholds:
            for ask_max in ask_caps:
                for min_sec in min_seconds:
                    for gate in gates:
                        policies.append(Policy(chooser, threshold, ask_max, min_sec, gate))
    return policies


def choose_decision_sides(side_rows: pd.DataFrame, chooser: str) -> pd.DataFrame:
    if chooser not in side_rows.columns:
        return side_rows.iloc[0:0].copy()
    usable = side_rows[side_rows[chooser].notna()].copy()
    if usable.empty:
        return usable
    chosen = (
        usable.sort_values(["decision_key", chooser, "book_p_side"], ascending=[True, False, False])
        .groupby("decision_key", as_index=False, sort=False)
        .first()
    )
    return chosen.sort_values(["market", "entry_dt"]).reset_index(drop=True)


def gate_mask(chosen: pd.DataFrame, policy: Policy) -> pd.Series:
    mask = (
        chosen[policy.chooser].ge(policy.min_score)
        & chosen["ask_cents"].le(policy.ask_max)
        & chosen["seconds_to_close"].ge(policy.min_seconds_to_close)
    )
    if policy.gate == "none":
        return mask.fillna(False)
    if policy.gate == "adverse15<=10_or_margin_rv15>=0.5":
        mask &= chosen["adverse_move_15m"].le(10) | chosen["margin_per_rv_sigma_15m"].ge(0.5)
    elif policy.gate == "brownian15>=0.55_and_brownian30>=0.55":
        mask &= chosen["brownian_p_rv_15m"].ge(0.55) & chosen["brownian_p_rv_30m"].ge(0.55)
    elif policy.gate == "spread<=4":
        mask &= chosen["spread_cents"].le(4)
    elif policy.gate == "abs_book_rv15_gap<=0.30":
        mask &= chosen["abs_book_rv15_gap"].le(0.30)
    elif policy.gate == "abs_book_rv15_gap<=0.20":
        mask &= chosen["abs_book_rv15_gap"].le(0.20)
    elif policy.gate == "abs_book_rv15_gap<=0.15":
        mask &= chosen["abs_book_rv15_gap"].le(0.15)
    elif policy.gate == "margin_rv15>=0_and_abs_book_rv15_gap<=0.15":
        mask &= chosen["margin_per_rv_sigma_15m"].ge(0) & chosen["abs_book_rv15_gap"].le(0.15)
    elif policy.gate == "rv15_sigma<=200":
        mask &= chosen["rv_sigma_t_15m"].le(200)
    elif policy.gate == "margin_rv15>=0":
        mask &= chosen["margin_per_rv_sigma_15m"].ge(0)
    else:
        raise ValueError(f"unknown gate: {policy.gate}")
    return mask.fillna(False)


def select_markets_from_chosen(chosen: pd.DataFrame, policy: Policy) -> pd.DataFrame:
    if chosen.empty:
        return chosen
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
    return selected


def split_metric(base: pd.DataFrame, selected: pd.DataFrame, split: str) -> Dict[str, Any]:
    base_part = base if split == "all" else base[base["split"] == split]
    selected_part = selected if split == "all" else selected[selected["split"] == split]
    rows = int(len(selected_part))
    wins = int(selected_part["win"].sum()) if rows else 0
    losses = rows - wins
    total = int(len(base_part))
    return {
        "markets": rows,
        "wins": wins,
        "losses": losses,
        "base_markets": total,
        "accuracy": wins / rows if rows else None,
        "coverage": rows / total if total else None,
        "median_ask": float(selected_part["ask_cents"].median()) if rows else None,
        "median_seconds_to_close": float(selected_part["seconds_to_close"].median()) if rows else None,
    }


def metrics_for(base: pd.DataFrame, selected: pd.DataFrame) -> Dict[str, Dict[str, Any]]:
    return {split: split_metric(base, selected, split) for split in ["all", "train", "validation", "holdout"]}


def coverage_pass(metrics: Dict[str, Dict[str, Any]]) -> bool:
    return all((metrics[split]["coverage"] or 0.0) >= MARKET_COVERAGE_FLOOR for split in ["all", "train", "validation", "holdout"])


def target_pass(metrics: Dict[str, Dict[str, Any]]) -> bool:
    if not coverage_pass(metrics):
        return False
    if not all((metrics[split]["accuracy"] or 0.0) >= TARGET_ACCURACY for split in ["all", "train", "validation", "holdout"]):
        return False
    if metrics["all"]["markets"] < MIN_SELECTED_MARKETS:
        return False
    if metrics["holdout"]["markets"] < MIN_HOLDOUT_SELECTED_MARKETS:
        return False
    return True


def nondegenerate_pass(policy: Policy, metrics: Dict[str, Dict[str, Any]]) -> bool:
    return (
        target_pass(metrics)
        and policy.ask_max <= 95.0
        and policy.min_seconds_to_close >= 60.0
        and (metrics["all"]["median_ask"] or 100.0) <= 90.0
    )


def flatten(policy: Policy, metrics: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
    row: Dict[str, Any] = {
        "chooser": policy.chooser,
        "min_score": policy.min_score,
        "ask_max": policy.ask_max,
        "min_seconds_to_close": policy.min_seconds_to_close,
        "gate": policy.gate,
        "label": policy.label,
        "coverage_pass": coverage_pass(metrics),
        "target_pass": target_pass(metrics),
        "nondegenerate_pass": nondegenerate_pass(policy, metrics),
    }
    row["min_test_accuracy"] = min(metrics["validation"]["accuracy"] or 0.0, metrics["holdout"]["accuracy"] or 0.0)
    row["min_test_coverage"] = min(metrics["validation"]["coverage"] or 0.0, metrics["holdout"]["coverage"] or 0.0)
    for split, metric in metrics.items():
        for key, value in metric.items():
            row[f"{split}_{key}"] = value
    return row


def rank_key(row: Dict[str, Any]) -> tuple:
    return (
        int(row["nondegenerate_pass"]),
        int(row["target_pass"]),
        int(row["coverage_pass"]),
        row["min_test_accuracy"],
        row["holdout_accuracy"] or 0.0,
        row["validation_accuracy"] or 0.0,
        row["all_accuracy"] or 0.0,
        row["min_test_coverage"],
        -(row["all_median_ask"] or 100.0),
        row["all_median_seconds_to_close"] or 0.0,
    )


def scan(base: pd.DataFrame, side_rows: pd.DataFrame) -> pd.DataFrame:
    rows: List[Dict[str, Any]] = []
    side_rows = side_rows.merge(base[["market", "split"]], on="market", how="inner")
    policies = make_policies()
    chosen_cache = {
        chooser: choose_decision_sides(side_rows, chooser)
        for chooser in sorted({policy.chooser for policy in policies})
    }
    for policy in policies:
        selected = select_markets_from_chosen(chosen_cache.get(policy.chooser, side_rows.iloc[0:0]), policy)
        metrics = metrics_for(base, selected)
        rows.append(flatten(policy, metrics))
    rows.sort(key=rank_key, reverse=True)
    return pd.DataFrame(rows)


def block_needed(metric: Dict[str, Any]) -> Optional[int]:
    markets = int(metric["markets"])
    wins = int(metric["wins"])
    if markets <= 0:
        return None
    if wins / markets >= TARGET_ACCURACY:
        return 0
    max_markets_at_target = math.floor(wins / TARGET_ACCURACY)
    return max(0, markets - max_markets_at_target)


def write_report(
    path: Path,
    generated: str,
    base: pd.DataFrame,
    results: pd.DataFrame,
    fixed_selected: pd.DataFrame,
) -> None:
    lines: List[str] = []
    lines.append("# BTC 15m Market-Interval 80% Coverage Probe")
    lines.append("")
    lines.append(f"Generated UTC: `{generated}`")
    lines.append("")
    lines.append("## Scope")
    lines.append("")
    lines.append("- Research-only probe; no orders are submitted and no bot files are modified.")
    lines.append(f"- Source: `{LEDGER}` / mode `{MODE}`.")
    lines.append("- Unit of volume is the recurring BTC 15-minute market ticker.")
    lines.append("- A policy can fire once per resolved market; coverage is selected markets / resolved markets.")
    lines.append("- Candidate selection is causal inside each market: first heartbeat that passes the gate becomes the trade.")
    lines.append("- `nondegenerate_pass` additionally requires `ask_max<=95`, `min_seconds_to_close>=60`, and median ask <=90.")
    lines.append(f"- Fixed fresh-shadow candidate: `{FIXED_INTERVAL_POLICY.label}`.")
    lines.append("")
    lines.append("## Coverage")
    lines.append("")
    lines.append(f"- Resolved market intervals: {len(base)}")
    for split in ["train", "validation", "holdout"]:
        lines.append(f"- {split.title()} intervals: {int((base['split'] == split).sum())}")
    lines.append(f"- Candidate policies scanned: {len(results)}")
    lines.append(f"- Policies covering >=80% of intervals on every split: {int(results['coverage_pass'].sum())}")
    lines.append(f"- Policies passing 95% accuracy and 80% interval coverage: {int(results['target_pass'].sum())}")
    lines.append(f"- Nondegenerate policies passing target: {int(results['nondegenerate_pass'].sum())}")
    lines.append("")

    def add_table(title: str, frame: pd.DataFrame) -> None:
        lines.append(title)
        lines.append("")
        if frame.empty:
            lines.append("No rows.")
            lines.append("")
            return
        lines.append(
            "| rank | policy | all acc | all cov | val acc | val cov | holdout acc | holdout cov | median ask | median sec | target | nondeg |"
        )
        lines.append("|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---|---|")
        for idx, row in enumerate(frame.head(15).to_dict("records"), start=1):
            lines.append(
                f"| {idx} | `{row['label']}` | {pct(row['all_accuracy'])} | {pct(row['all_coverage'])} | "
                f"{pct(row['validation_accuracy'])} | {pct(row['validation_coverage'])} | "
                f"{pct(row['holdout_accuracy'])} | {pct(row['holdout_coverage'])} | "
                f"{row['all_median_ask']:.1f} | {row['all_median_seconds_to_close']:.1f} | "
                f"{row['target_pass']} | {row['nondegenerate_pass']} |"
            )
        lines.append("")

    add_table("## Target-Passing Policies", results[results["target_pass"]])
    add_table("## Best 80%-Coverage Policies", results[results["coverage_pass"]])
    strict = results[
        (results["coverage_pass"])
        & (results["ask_max"] <= 95)
        & (results["min_seconds_to_close"] >= 60)
        & (results["all_median_ask"] <= 90)
    ]
    add_table("## Best Nondegenerate 80%-Coverage Policies", strict)

    best_cov = results[results["coverage_pass"]].head(1)
    if not best_cov.empty:
        best = best_cov.iloc[0].to_dict()
        lines.append("## Physics Read")
        lines.append("")
        lines.append(f"- Best 80%-coverage policy: `{best['label']}`.")
        lines.append(
            f"- It covered {int(best['all_markets'])}/{int(best['all_base_markets'])} intervals "
            f"({pct(best['all_coverage'])}) at {pct(best['all_accuracy'])} all accuracy."
        )
        lines.append(
            f"- Validation was {pct(best['validation_accuracy'])} at {pct(best['validation_coverage'])}; "
            f"holdout was {pct(best['holdout_accuracy'])} at {pct(best['holdout_coverage'])}."
        )
        lines.append(f"- Median selected ask was {best['all_median_ask']:.1f} cents.")
        lines.append(f"- Median selected time-to-close was {best['all_median_seconds_to_close']:.1f} seconds.")
        for split in ["validation", "holdout"]:
            metric = {
                "markets": best[f"{split}_markets"],
                "wins": best[f"{split}_wins"],
            }
            needed = block_needed(metric)
            lines.append(
                f"- To reach 95% on {split} from this policy without losing wins, another {needed} selected losses would need to be blocked."
            )
        lines.append("")

    fixed_rows = results[results["label"] == FIXED_INTERVAL_POLICY.label]
    if not fixed_rows.empty:
        fixed = fixed_rows.iloc[0].to_dict()
        try:
            lock = json.loads(LOCK_PATH.read_text(encoding="utf-8")) if LOCK_PATH.exists() else {}
        except json.JSONDecodeError:
            lock = {}
        lines.append("## Fixed Candidate Fresh Lock")
        lines.append("")
        lines.append(f"- Lock file: `{LOCK_PATH}`")
        lines.append(f"- Lock close time: `{lock.get('lock_close_dt')}`")
        lines.append(f"- Fixed candidate all accuracy: {pct(fixed['all_accuracy'])}")
        lines.append(f"- Fixed candidate all interval coverage: {pct(fixed['all_coverage'])}")
        lines.append(
            f"- Fixed candidate validation: {pct(fixed['validation_accuracy'])} at {pct(fixed['validation_coverage'])} coverage"
        )
        lines.append(
            f"- Fixed candidate holdout: {pct(fixed['holdout_accuracy'])} at {pct(fixed['holdout_coverage'])} coverage"
        )
        lines.append(
            "- Fresh post-lock rows are evaluated in `market_interval_80coverage_selected_latest.csv`; "
            "zero or tiny fresh counts are not completion evidence."
        )
        lock_close_dt = pd.to_datetime(lock.get("lock_close_dt"), utc=True, errors="coerce")
        if not pd.isna(lock_close_dt):
            fresh_base = base[pd.to_datetime(base["close_dt"], utc=True, errors="coerce") > lock_close_dt]
            fresh_selected = fixed_selected[fixed_selected["fresh_after_lock"]] if "fresh_after_lock" in fixed_selected else fixed_selected.iloc[0:0]
            fresh_n = int(len(fresh_selected))
            fresh_wins = int(fresh_selected["win"].sum()) if fresh_n else 0
            fresh_cov = fresh_n / len(fresh_base) if len(fresh_base) else None
            fresh_acc = fresh_wins / fresh_n if fresh_n else None
            lines.append(f"- Fresh resolved intervals after lock: {len(fresh_base)}")
            lines.append(f"- Fresh selected intervals after lock: {fresh_n}")
            lines.append(f"- Fresh selected accuracy: {pct(fresh_acc)}")
            lines.append(f"- Fresh interval coverage: {pct(fresh_cov)}")
            if fresh_n:
                lines.append(f"- Fresh median ask: {fresh_selected['ask_cents'].median():.1f} cents")
                lines.append(f"- Fresh median seconds to close: {fresh_selected['seconds_to_close'].median():.1f}")
        lines.append("")

    lines.append("## Conclusion")
    lines.append("")
    if int(results["nondegenerate_pass"].sum()) > 0:
        lines.append(
            "At least one nondegenerate interval policy cleared 95% accuracy while covering 80% of recurring 15-minute markets. This remains heartbeat telemetry and still needs fresh fill validation."
        )
    elif int(results["target_pass"].sum()) > 0:
        lines.append(
            "At least one interval policy clears the raw 95% / 80% target, but the pass is likely settlement-price leakage or expensive late-entry behavior unless it also appears in the nondegenerate table."
        )
    else:
        lines.append(
            "No scanned interval policy clears 95% accuracy while covering 80% of recurring 15-minute markets."
        )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    side_rows = load_side_rows()
    base = market_base(side_rows)
    results = scan(base, side_rows)
    generated = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%SZ")

    if not LOCK_PATH.exists():
        lock = {
            "lock_id": "market_interval_80coverage_lock_v1",
            "created_utc": datetime.now(timezone.utc).isoformat(),
            "lock_close_dt": base["close_dt"].max().isoformat() if not base.empty else None,
            "fixed_policy": {
                "chooser": FIXED_INTERVAL_POLICY.chooser,
                "min_score": FIXED_INTERVAL_POLICY.min_score,
                "ask_max": FIXED_INTERVAL_POLICY.ask_max,
                "min_seconds_to_close": FIXED_INTERVAL_POLICY.min_seconds_to_close,
                "gate": FIXED_INTERVAL_POLICY.gate,
                "label": FIXED_INTERVAL_POLICY.label,
            },
        }
        LOCK_PATH.write_text(json.dumps(clean_json(lock), indent=2, sort_keys=True), encoding="utf-8")
    try:
        lock_data = json.loads(LOCK_PATH.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        lock_data = {}
    lock_close_dt = pd.to_datetime(lock_data.get("lock_close_dt"), utc=True, errors="coerce")
    side_rows_with_split = side_rows.merge(base[["market", "split"]], on="market", how="inner")
    fixed_selected = select_markets_from_chosen(
        choose_decision_sides(side_rows_with_split, FIXED_INTERVAL_POLICY.chooser),
        FIXED_INTERVAL_POLICY,
    )
    if not fixed_selected.empty and not pd.isna(lock_close_dt):
        fixed_selected["fresh_after_lock"] = pd.to_datetime(
            fixed_selected["close_dt"], utc=True, errors="coerce"
        ) > lock_close_dt
    else:
        fixed_selected["fresh_after_lock"] = False

    csv_latest = OUT_DIR / "market_interval_80coverage_candidates_latest.csv"
    csv_stamp = OUT_DIR / f"market_interval_80coverage_candidates_{generated}.csv"
    md_latest = OUT_DIR / "market_interval_80coverage_latest.md"
    md_stamp = OUT_DIR / f"market_interval_80coverage_{generated}.md"
    json_latest = OUT_DIR / "market_interval_80coverage_latest.json"
    json_stamp = OUT_DIR / f"market_interval_80coverage_{generated}.json"
    selected_latest = OUT_DIR / "market_interval_80coverage_selected_latest.csv"
    selected_stamp = OUT_DIR / f"market_interval_80coverage_selected_{generated}.csv"

    results.to_csv(csv_latest, index=False)
    results.to_csv(csv_stamp, index=False)
    fixed_selected.to_csv(selected_latest, index=False)
    fixed_selected.to_csv(selected_stamp, index=False)
    write_report(md_latest, generated, base, results, fixed_selected)
    write_report(md_stamp, generated, base, results, fixed_selected)

    summary = {
        "generated_utc": generated,
        "source": str(LEDGER),
        "mode": MODE,
        "target_accuracy": TARGET_ACCURACY,
        "market_coverage_floor": MARKET_COVERAGE_FLOOR,
        "resolved_markets": int(len(base)),
        "split_counts": {split: int((base["split"] == split).sum()) for split in ["train", "validation", "holdout"]},
        "candidate_count": int(len(results)),
        "coverage_pass_count": int(results["coverage_pass"].sum()),
        "target_pass_count": int(results["target_pass"].sum()),
        "nondegenerate_pass_count": int(results["nondegenerate_pass"].sum()),
        "lock": lock_data,
        "fixed_policy": {
            "label": FIXED_INTERVAL_POLICY.label,
            "selected_markets": int(len(fixed_selected)),
            "fresh_selected_markets": int(fixed_selected["fresh_after_lock"].sum()),
        },
        "top_target": results[results["target_pass"]].head(10).to_dict("records"),
        "top_coverage": results[results["coverage_pass"]].head(10).to_dict("records"),
    }
    for path in [json_latest, json_stamp]:
        path.write_text(json.dumps(clean_json(summary), indent=2, sort_keys=True), encoding="utf-8")

    print("Market interval 80% coverage probe complete")
    print(f"resolved_markets={len(base)} candidates={len(results)}")
    print(
        f"coverage_pass={int(results['coverage_pass'].sum())} "
        f"target_pass={int(results['target_pass'].sum())} "
        f"nondegenerate_pass={int(results['nondegenerate_pass'].sum())}"
    )
    print(f"report={md_latest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
