"""Research-only prior failure analysis for current v28.

The goal is not another threshold search. This probe asks which physical priors
actually separate winners from losers on:

- current v28 filled entries,
- current v28 websocket opportunities,
- the supplemental live_90_70 replay where physics rules did pass.

It writes explanatory artifacts only under logs/edge_research.
"""
from __future__ import annotations

import json
import math
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

import numpy as np
import pandas as pd

from probe_live_v28_fv_accuracy_volume import OUT_DIR
from probe_physics_priors_boundary_models import clean_json


PHYSICS_TRADES = OUT_DIR / "physics_priors_boundary_trades_latest.csv"
OPPORTUNITY_TRADES = OUT_DIR / "live_v28_websocket_opportunity_physics_trades_latest.csv"

FEATURES = [
    ("ask_cents", "Ask price"),
    ("v28_p_side", "v28 side probability"),
    ("v28_edge_cents", "v28 edge cents"),
    ("seconds_to_close", "Seconds to close"),
    ("margin_dollars", "Spot-strike margin"),
    ("margin_per_sqrt_sec", "Margin / sqrt(seconds)"),
    ("margin_per_v28_sigma", "Margin / v28 sigma"),
    ("brownian_p_v28_sigma", "Brownian p via v28 sigma"),
    ("margin_per_rv_sigma_15m", "Margin / realized-vol sigma 15m"),
    ("brownian_p_rv_15m", "Brownian p via realized vol 15m"),
    ("signed_move_3m", "Signed BTC move 3m"),
    ("signed_move_5m", "Signed BTC move 5m"),
    ("signed_move_15m", "Signed BTC move 15m"),
    ("adverse_move_3m", "Adverse BTC move 3m"),
    ("adverse_move_5m", "Adverse BTC move 5m"),
    ("adverse_move_15m", "Adverse BTC move 15m"),
    ("drift_projected_margin_3m", "3m drift-projected margin"),
    ("drift_projected_margin_5m", "5m drift-projected margin"),
]

PRIOR_RULES = [
    {
        "label": "v28 p_side>=0.85 and ask<=90",
        "conditions": [("v28_p_side", ">=", 0.85), ("ask_cents", "<=", 90.0)],
    },
    {
        "label": "v28 edge>=2c and ask<=90",
        "conditions": [("v28_edge_cents", ">=", 2.0), ("ask_cents", "<=", 90.0)],
    },
    {
        "label": "margin/v28_sigma>=0.5",
        "conditions": [("margin_per_v28_sigma", ">=", 0.5), ("ask_cents", "<=", 100.0)],
    },
    {
        "label": "margin/v28_sigma>=1.0",
        "conditions": [("margin_per_v28_sigma", ">=", 1.0), ("ask_cents", "<=", 100.0)],
    },
    {
        "label": "margin/rv15>=0.5",
        "conditions": [("margin_per_rv_sigma_15m", ">=", 0.5), ("ask_cents", "<=", 100.0)],
    },
    {
        "label": "Brownian rv15 p>=0.70",
        "conditions": [("brownian_p_rv_15m", ">=", 0.70), ("ask_cents", "<=", 100.0)],
    },
    {
        "label": "projected_margin_3m>=50",
        "conditions": [("drift_projected_margin_3m", ">=", 50.0), ("ask_cents", "<=", 100.0)],
    },
    {
        "label": "adverse15<10 or v28 cushion>0.5",
        "conditions": [("adverse_move_15m", "<", 10.0, "or", "margin_per_v28_sigma", ">", 0.5), ("ask_cents", "<=", 100.0)],
    },
]


def pct(value: Optional[float]) -> str:
    if value is None or not math.isfinite(float(value)):
        return "NA"
    return f"{100.0 * float(value):.2f}%"


def as_bool_series(series: pd.Series) -> pd.Series:
    if series.dtype == bool:
        return series
    return series.astype(str).str.lower().isin(["true", "1", "yes"])


def load_inputs() -> Dict[str, pd.DataFrame]:
    physics = pd.read_csv(PHYSICS_TRADES)
    physics["win"] = as_bool_series(physics["win"])
    physics["entry_dt"] = pd.to_datetime(physics["entry_dt"], utc=True, errors="coerce")
    add_missing_adverse_moves(physics)
    current_fills = physics[physics["dataset"] == "current_v28_live_fills"].copy()
    replay_9070 = physics[physics["dataset"] == "live_90_70_replay"].copy()

    opportunities = pd.read_csv(OPPORTUNITY_TRADES)
    opportunities["win"] = as_bool_series(opportunities["win"])
    opportunities["outcome_available"] = as_bool_series(opportunities["outcome_available"])
    opportunities["entry_dt"] = pd.to_datetime(opportunities["entry_dt"], utc=True, errors="coerce")
    add_missing_adverse_moves(opportunities)
    current_opportunities = opportunities[
        (opportunities["opportunity_mode"] == "first_per_market") & opportunities["outcome_available"]
    ].copy()

    return {
        "current_v28_live_fills": current_fills,
        "current_v28_first_opportunities": current_opportunities,
        "live_90_70_replay": replay_9070,
    }


def add_missing_adverse_moves(df: pd.DataFrame) -> None:
    for lag in [1, 3, 5, 10, 15, 30, 60]:
        signed = f"signed_move_{lag}m"
        adverse = f"adverse_move_{lag}m"
        if adverse not in df.columns and signed in df.columns:
            df[adverse] = np.maximum(-pd.to_numeric(df[signed], errors="coerce"), 0.0)


def auc_for_feature(df: pd.DataFrame, feature: str) -> Optional[float]:
    if feature not in df.columns:
        return None
    part = df[[feature, "win"]].copy()
    part[feature] = pd.to_numeric(part[feature], errors="coerce")
    part = part.dropna()
    if part.empty:
        return None
    wins = part[part["win"]]
    losses = part[~part["win"]]
    n_pos = len(wins)
    n_neg = len(losses)
    if n_pos == 0 or n_neg == 0:
        return None
    ranks = part[feature].rank(method="average")
    pos_rank_sum = float(ranks[part["win"]].sum())
    auc = (pos_rank_sum - n_pos * (n_pos + 1) / 2.0) / (n_pos * n_neg)
    return float(auc)


def quantile_text(values: pd.Series) -> str:
    numeric = pd.to_numeric(values, errors="coerce").dropna()
    if numeric.empty:
        return "NA"
    qs = numeric.quantile([0.25, 0.50, 0.75])
    return f"{qs.iloc[1]:.4g} [{qs.iloc[0]:.4g}, {qs.iloc[2]:.4g}]"


def summarize_features(df: pd.DataFrame) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    for feature, label in FEATURES:
        if feature not in df.columns:
            continue
        numeric = pd.to_numeric(df[feature], errors="coerce")
        if numeric.notna().sum() == 0:
            continue
        winners = df[df["win"]]
        losers = df[~df["win"]]
        auc = auc_for_feature(df, feature)
        separation = max(auc, 1.0 - auc) if auc is not None else None
        direction = None
        if auc is not None:
            direction = "higher_wins" if auc >= 0.5 else "lower_wins"
        rows.append(
            {
                "feature": feature,
                "label": label,
                "winner_median_iqr": quantile_text(winners[feature]),
                "loser_median_iqr": quantile_text(losers[feature]),
                "auc_higher_predicts_win": auc,
                "best_direction": direction,
                "separation": separation,
            }
        )
    rows.sort(key=lambda row: row["separation"] or 0.0, reverse=True)
    return rows


def condition_mask(df: pd.DataFrame, condition: tuple) -> pd.Series:
    if len(condition) == 7:
        left_feature, left_op, left_value, joiner, right_feature, right_op, right_value = condition
        left = condition_mask(df, (left_feature, left_op, left_value))
        right = condition_mask(df, (right_feature, right_op, right_value))
        if joiner == "or":
            return left | right
        return left & right
    feature, op, value = condition
    if feature not in df.columns:
        return pd.Series(False, index=df.index)
    series = pd.to_numeric(df[feature], errors="coerce")
    if op == ">=":
        return series >= float(value)
    if op == ">":
        return series > float(value)
    if op == "<=":
        return series <= float(value)
    if op == "<":
        return series < float(value)
    raise ValueError(f"unknown op {op}")


def apply_prior_rule(df: pd.DataFrame, rule: Dict[str, Any]) -> pd.Series:
    mask = pd.Series(True, index=df.index)
    for condition in rule["conditions"]:
        mask &= condition_mask(df, condition)
    return mask.fillna(False)


def metrics_for_mask(df: pd.DataFrame, mask: pd.Series) -> Dict[str, Any]:
    selected = df[mask].copy()
    total_trades = int(len(df))
    total_contracts = int(df["qty"].sum()) if not df.empty else 0
    trades = int(len(selected))
    contracts = int(selected["qty"].sum()) if not selected.empty else 0
    wins = selected[selected["win"]]
    trade_wins = int(len(wins))
    contract_wins = int(wins["qty"].sum()) if not wins.empty else 0
    return {
        "trades": trades,
        "contracts": contracts,
        "trade_wins": trade_wins,
        "contract_wins": contract_wins,
        "trade_accuracy": trade_wins / trades if trades else None,
        "contract_accuracy": contract_wins / contracts if contracts else None,
        "trade_retention": trades / total_trades if total_trades else None,
        "contract_retention": contracts / total_contracts if total_contracts else None,
    }


def summarize_prior_rules(df: pd.DataFrame) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    for rule in PRIOR_RULES:
        mask = apply_prior_rule(df, rule)
        row = {"label": rule["label"], **metrics_for_mask(df, mask)}
        rows.append(row)
    return rows


def base_metrics(df: pd.DataFrame) -> Dict[str, Any]:
    return metrics_for_mask(df, pd.Series(True, index=df.index))


def summarize_dataset(df: pd.DataFrame) -> Dict[str, Any]:
    out = {
        "rows": int(len(df)),
        "contracts": int(df["qty"].sum()) if not df.empty else 0,
        "baseline": base_metrics(df),
        "feature_separation": summarize_features(df),
        "prior_rule_checks": summarize_prior_rules(df),
    }
    return out


def top_rows(rows: List[Dict[str, Any]], n: int = 8) -> List[Dict[str, Any]]:
    return rows[:n]


def write_report(path: Path, generated: str, summaries: Dict[str, Dict[str, Any]]) -> None:
    lines: List[str] = []
    lines.append("# Current v28 Prior Failure Modes")
    lines.append("")
    lines.append(f"Generated UTC: `{generated}`")
    lines.append("")
    lines.append("## Scope")
    lines.append("")
    lines.append("- Research-only analysis; no bot files or running processes are touched.")
    lines.append("- Compares current v28 filled entries, current v28 first websocket opportunities, and the supplemental live_90_70 replay.")
    lines.append("- Focus is falsification of physical priors: v28 probability, edge, boundary cushion, realized-vol cushion, and adverse drift.")
    lines.append("")
    for name, summary in summaries.items():
        base = summary["baseline"]
        lines.append(f"## `{name}`")
        lines.append("")
        lines.append(f"- Rows: {summary['rows']}")
        lines.append(f"- Contracts: {summary['contracts']}")
        lines.append(
            f"- Baseline: {base['contract_wins']}/{base['contracts']} contracts = {pct(base['contract_accuracy'])}; "
            f"{base['trade_wins']}/{base['trades']} trades = {pct(base['trade_accuracy'])}"
        )
        lines.append("")
        lines.append("### Prior Checks")
        lines.append("")
        lines.append("| prior | contracts | contract acc | contract ret | trades | trade acc |")
        lines.append("|---|---:|---:|---:|---:|---:|")
        for row in summary["prior_rule_checks"]:
            lines.append(
                f"| `{row['label']}` | {row['contract_wins']}/{row['contracts']} | {pct(row['contract_accuracy'])} | "
                f"{pct(row['contract_retention'])} | {row['trade_wins']}/{row['trades']} | {pct(row['trade_accuracy'])} |"
            )
        lines.append("")
        lines.append("### Strongest Single-Feature Separators")
        lines.append("")
        lines.append("| feature | winner median [IQR] | loser median [IQR] | direction | separation |")
        lines.append("|---|---:|---:|---|---:|")
        for row in top_rows(summary["feature_separation"], n=10):
            lines.append(
                f"| {row['label']} | {row['winner_median_iqr']} | {row['loser_median_iqr']} | "
                f"{row['best_direction']} | {row['separation']:.3f} |"
                if row["separation"] is not None
                else f"| {row['label']} | {row['winner_median_iqr']} | {row['loser_median_iqr']} | NA | NA |"
            )
        lines.append("")
    lines.append("## Readout")
    lines.append("")
    current = summaries["current_v28_live_fills"]["baseline"]
    opp = summaries["current_v28_first_opportunities"]["baseline"]
    replay = summaries["live_90_70_replay"]["baseline"]
    lines.append(
        f"- Current v28 fills are only {pct(current['contract_accuracy'])} on {current['contracts']} contracts; "
        f"first websocket opportunities are similarly weak at {pct(opp['contract_accuracy'])} on {opp['contracts']} contracts."
    )
    lines.append(
        f"- The supplemental live_90_70 replay is a different regime: {pct(replay['contract_accuracy'])} on "
        f"{replay['contracts']} contracts before filtering."
    )
    lines.append(
        "- The current-v28 failure is therefore not just order execution noise. The same overconfidence appears in the "
        "approved websocket opportunity set before fills."
    )
    lines.append(
        "- The adverse-drift prior is not sufficient on current v28 because many current losers already have favorable "
        "signed short-window movement; high-volume adverse filters mostly preserve the losing holdout."
    )
    lines.append(
        "- Several physical features flip direction across regimes. In current v28, higher signed movement and larger "
        "cushion weakly help; in live_90_70, the few losses often occur at larger cushions and longer time-to-close. "
        "That argues for regime gating before trusting a monotonic fair-value prior."
    )
    lines.append(
        "- This falsifies promotion of the current v28 fair-value prior. The honest next evidence is fresh post-lock "
        "shadow validation, not more threshold tuning on the old current-v28 holdout."
    )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    inputs = load_inputs()
    summaries = {name: summarize_dataset(df) for name, df in inputs.items()}
    generated = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%SZ")
    json_latest = OUT_DIR / "current_v28_prior_failure_modes_latest.json"
    json_stamp = OUT_DIR / f"current_v28_prior_failure_modes_{generated}.json"
    md_latest = OUT_DIR / "current_v28_prior_failure_modes_latest.md"
    md_stamp = OUT_DIR / f"current_v28_prior_failure_modes_{generated}.md"
    payload = {
        "generated_utc": generated,
        "source_files": {
            "physics_trades": str(PHYSICS_TRADES),
            "opportunity_trades": str(OPPORTUNITY_TRADES),
        },
        "summaries": summaries,
    }
    for path in [json_latest, json_stamp]:
        path.write_text(json.dumps(clean_json(payload), indent=2, sort_keys=True), encoding="utf-8")
    write_report(md_latest, generated, summaries)
    write_report(md_stamp, generated, summaries)
    current = summaries["current_v28_live_fills"]["baseline"]
    opp = summaries["current_v28_first_opportunities"]["baseline"]
    print("Current v28 prior failure analysis complete")
    print(f"fills={current['contract_wins']}/{current['contracts']} acc={current['contract_accuracy']}")
    print(f"opportunities={opp['contract_wins']}/{opp['contracts']} acc={opp['contract_accuracy']}")
    print(f"report={md_latest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
