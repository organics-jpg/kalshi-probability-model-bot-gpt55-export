"""Research-only physics audit on live websocket heartbeat states.

This probe widens the evidence set beyond v28-approved `signal_seen` rows by
using the bot's live heartbeat stream. Each heartbeat contributes the current
book favorite as a candidate state, then cached Coinbase BTC candles supply the
spot/realized-vol physics features.

It is intentionally separate from the running bot: no orders are submitted, no
bot files are imported, and no process is touched.
"""
from __future__ import annotations

import argparse
import json
import math
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional
from zoneinfo import ZoneInfo

import numpy as np
import pandas as pd

from probe_live_v28_fv_accuracy_volume import (
    BOT_LOG,
    OUT_DIR,
    as_float,
    parse_bot_log,
    parse_quote_token,
)
from probe_physics_priors_boundary_models import (
    MIN_TARGET_ACCURACY,
    asof_values,
    clean_json,
    load_coinbase_candles,
    normal_cdf_np,
    oracle_bound,
)
from shadow_live_v28_physics_validator import closed_market_outcomes_only


LOCAL_TZ = ZoneInfo("America/New_York")
PRIMARY_MODE = "favorite_minute_bucket"
MIN_RETENTION = 0.75
RETENTION_FLOORS = [0.75, 0.80]
MIN_SELECTED_ROWS = 75
MIN_HOLDOUT_ROWS = 15


def pct(value: Optional[float]) -> str:
    if value is None or not math.isfinite(float(value)):
        return "NA"
    return f"{100.0 * float(value):.2f}%"


def local_log_ts_to_utc(text: str) -> Optional[pd.Timestamp]:
    try:
        dt = datetime.strptime(text, "%Y-%m-%d %H:%M:%S,%f")
    except ValueError:
        return None
    return pd.Timestamp(dt.replace(tzinfo=LOCAL_TZ).astimezone(timezone.utc))


def safe_mid(bid: Optional[int], ask: Optional[int]) -> Optional[float]:
    if bid is None or ask is None:
        return None
    return (float(bid) + float(ask)) / 2.0


def heartbeat_favorite_rows(
    markets: Dict[str, Dict[str, Any]],
    outcomes: Dict[str, Dict[str, Any]],
) -> pd.DataFrame:
    heartbeat_re = re.compile(
        r"^(?P<log_ts>\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d{3}) \| .*?Heartbeat \| "
        r"watch=(?P<market>\S+) yes_bid=(?P<yes_bid>\S+) yes_ask=(?P<yes_ask>\S+) "
        r"no_bid=(?P<no_bid>\S+) no_ask=(?P<no_ask>\S+) "
        r"book_ready=(?P<book_ready>\S+) position=(?P<position>\S+) "
        r"pending=(?P<pending>\S+) dry_run=(?P<dry_run>\S+) trust=(?P<trust>\S+)"
    )
    rows: List[Dict[str, Any]] = []
    with BOT_LOG.open("r", encoding="utf-8", errors="replace") as handle:
        for line_no, line in enumerate(handle, start=1):
            match = heartbeat_re.search(line)
            if not match:
                continue
            if match.group("book_ready") != "True":
                continue
            market = match.group("market")
            market_info = markets.get(market) or {}
            close_dt = pd.to_datetime(market_info.get("close_time"), utc=True, errors="coerce")
            strike = as_float(market_info.get("strike"))
            entry_dt = local_log_ts_to_utc(match.group("log_ts"))
            if entry_dt is None or pd.isna(close_dt) or strike is None:
                continue
            seconds_to_close = (close_dt - entry_dt).total_seconds()
            if seconds_to_close <= 0:
                continue

            yes_bid = parse_quote_token(match.group("yes_bid"))
            yes_ask = parse_quote_token(match.group("yes_ask"))
            no_bid = parse_quote_token(match.group("no_bid"))
            no_ask = parse_quote_token(match.group("no_ask"))
            yes_mid = safe_mid(yes_bid, yes_ask)
            no_mid = safe_mid(no_bid, no_ask)
            if yes_mid is None or no_mid is None:
                continue
            if yes_mid >= no_mid:
                side = "yes"
                bid = yes_bid
                ask = yes_ask
                mid = yes_mid
                other_mid = no_mid
            else:
                side = "no"
                bid = no_bid
                ask = no_ask
                mid = no_mid
                other_mid = yes_mid
            if bid is None or ask is None:
                continue
            outcome = outcomes.get(market, {}).get("outcome")
            rows.append(
                {
                    "dataset": "live_heartbeat_book_favorite",
                    "entry_key": f"heartbeat:{line_no}",
                    "entry_dt": entry_dt,
                    "market": market,
                    "side": side,
                    "outcome": outcome,
                    "outcome_available": outcome in {"yes", "no"},
                    "win": bool(side == outcome) if outcome in {"yes", "no"} else None,
                    "qty": 1,
                    "ask_cents": float(ask),
                    "bid_cents": float(bid),
                    "book_mid_cents": float(mid),
                    "book_p_side": float(mid) / 100.0,
                    "book_other_mid_cents": float(other_mid),
                    "book_margin_cents": float(mid - other_mid),
                    "spread_cents": float(ask - bid),
                    "entry_minute": entry_dt.floor("min"),
                    "spot": np.nan,
                    "strike": strike,
                    "seconds_to_close": float(seconds_to_close),
                    "v28_sigma_t_dollars": np.nan,
                    "source_line_no": line_no,
                    "position_open_logged": match.group("position") == "True",
                    "pending_logged": match.group("pending") == "True",
                    "trust_state": match.group("trust"),
                    "outcome_method": outcomes.get(market, {}).get("method"),
                    "outcome_source": outcomes.get(market, {}).get("source"),
                }
            )
    if not rows:
        return pd.DataFrame()
    return pd.DataFrame(rows).sort_values(["entry_dt", "source_line_no"]).reset_index(drop=True)


def attach_physics(raw: pd.DataFrame, fetch_btc_candles: bool) -> tuple[pd.DataFrame, Dict[str, Any]]:
    if raw.empty:
        return raw, {}
    candles = load_coinbase_candles(raw, fetch_missing=fetch_btc_candles)
    candle_info: Dict[str, Any] = {
        "rows": int(len(candles)),
        "start": None,
        "end": None,
    }
    if not candles.empty:
        candle_info["start"] = pd.to_datetime(candles["close_dt"], utc=True, errors="coerce").min().isoformat()
        candle_info["end"] = pd.to_datetime(candles["close_dt"], utc=True, errors="coerce").max().isoformat()

    out = raw.copy()
    if candles.empty:
        return out.iloc[0:0].copy(), candle_info
    out["spot"] = asof_values(candles, out["entry_dt"], "close", 120.0)
    out = out.dropna(subset=["spot", "strike", "seconds_to_close"]).copy()
    out["side_sign"] = np.where(out["side"] == "yes", 1.0, -1.0)
    out["margin_dollars"] = out["side_sign"] * (out["spot"] - out["strike"])
    out["margin_per_sqrt_sec"] = out["margin_dollars"] / np.sqrt(out["seconds_to_close"])
    out["margin_per_sqrt_min"] = out["margin_dollars"] / np.sqrt(out["seconds_to_close"] / 60.0)
    out["margin_per_v28_sigma"] = np.nan
    out["brownian_p_v28_sigma"] = np.nan

    # Replicate the candle-derived features without requiring v28 sigma.
    for window in [5, 15, 30, 60]:
        sigma_min = asof_values(candles, out["entry_dt"], f"sigma_min_log_{window}m", 120.0)
        out[f"rv_sigma_t_{window}m"] = sigma_min * np.sqrt(out["seconds_to_close"] / 60.0)
        out[f"margin_per_rv_sigma_{window}m"] = out["margin_dollars"] / out[f"rv_sigma_t_{window}m"]
        out[f"brownian_p_rv_{window}m"] = normal_cdf_np(out[f"margin_per_rv_sigma_{window}m"])

    for lag in [1, 3, 5, 10, 15, 30, 60]:
        lag_dt = out["entry_dt"] - pd.to_timedelta(lag, unit="min")
        lag_close = asof_values(candles, lag_dt, "close", 120.0)
        out[f"btc_close_lag_{lag}m"] = lag_close
        move = out["spot"] - lag_close
        out[f"signed_move_{lag}m"] = out["side_sign"] * move
        out[f"signed_velocity_dps_{lag}m"] = out[f"signed_move_{lag}m"] / float(lag * 60)
        out[f"adverse_move_{lag}m"] = np.maximum(-out[f"signed_move_{lag}m"], 0.0)
        out[f"drift_projected_margin_{lag}m"] = (
            out["margin_dollars"] + out[f"signed_velocity_dps_{lag}m"] * out["seconds_to_close"]
        )
        for window in [15, 30, 60]:
            z = out[f"drift_projected_margin_{lag}m"] / out[f"rv_sigma_t_{window}m"]
            out[f"drift_p_{lag}m_rv_{window}m"] = normal_cdf_np(z)
    out["book_minus_brownian_rv15"] = out["book_p_side"] - out["brownian_p_rv_15m"]
    out["physics_confirmed_book"] = out["brownian_p_rv_15m"] >= 0.5
    return out.sort_values(["entry_dt", "source_line_no"]).reset_index(drop=True), candle_info


def dedupe_mode(df: pd.DataFrame, mode: str) -> pd.DataFrame:
    if df.empty:
        return df.copy()
    ordered = df.sort_values(["entry_dt", "source_line_no"]).reset_index(drop=True)
    if mode == "favorite_all_heartbeats":
        out = ordered.copy()
    elif mode == "favorite_minute_bucket":
        out = ordered.groupby(["market", "entry_minute"], as_index=False, sort=False).first()
    elif mode == "favorite_first_per_market":
        out = ordered.groupby(["market"], as_index=False, sort=False).first()
    else:
        raise ValueError(f"unknown mode: {mode}")
    out = out.sort_values(["entry_dt", "source_line_no"]).reset_index(drop=True)
    out["heartbeat_mode"] = mode
    return out


@dataclass(frozen=True)
class Rule:
    family: str
    label: str
    params: Dict[str, Any]


def make_rules() -> List[Rule]:
    rules: List[Rule] = []

    def add(family: str, label: str, params: Dict[str, Any]) -> None:
        rules.append(Rule(family=family, label=label, params=params))

    for book_min in [0.50, 0.55, 0.60, 0.65, 0.70, 0.75, 0.80, 0.85, 0.90, 0.95]:
        add("book_probability", f"book_mid>={book_min:.2f}", {"book_min": book_min})
        for spread_max in [2.0, 5.0, 10.0]:
            add(
                "book_probability_spread",
                f"book_mid>={book_min:.2f}; spread<={spread_max:g}",
                {"book_min": book_min, "spread_max": spread_max},
            )

    for p_min in [0.50, 0.55, 0.60, 0.65, 0.70, 0.75, 0.80, 0.85, 0.90, 0.95]:
        add("brownian_rv15", f"Phi(margin/rv15)>={p_min:.2f}", {"feature": "brownian_p_rv_15m", "min": p_min})
        add("brownian_rv30", f"Phi(margin/rv30)>={p_min:.2f}", {"feature": "brownian_p_rv_30m", "min": p_min})
        add(
            "drift_rv15",
            f"drift_p_5m_rv15>={p_min:.2f}",
            {"feature": "drift_p_5m_rv_15m", "min": p_min},
        )
        for book_min in [0.60, 0.70, 0.80, 0.90]:
            add(
                "book_physics_confirm",
                f"book_mid>={book_min:.2f}; Phi(margin/rv15)>={p_min:.2f}",
                {"book_min": book_min, "feature": "brownian_p_rv_15m", "min": p_min},
            )

    for sigma_min in [-1.0, -0.5, 0.0, 0.25, 0.5, 0.75, 1.0, 1.25, 1.5, 2.0]:
        add(
            "realized_vol_cushion",
            f"margin/rv15>={sigma_min:g}",
            {"feature": "margin_per_rv_sigma_15m", "min": sigma_min},
        )
        add(
            "sqrt_time_boundary",
            f"margin/sqrt(sec)>={sigma_min:g}",
            {"feature": "margin_per_sqrt_sec", "min": sigma_min},
        )

    for adverse in [10.0, 25.0, 50.0, 75.0, 100.0, 150.0]:
        add(
            "adverse_drift_guard",
            f"book_mid>=0.50; block adverse15>{adverse:g}",
            {"book_min": 0.50, "adverse_max": adverse},
        )
    return rules


def apply_rule(df: pd.DataFrame, rule: Rule) -> pd.Series:
    params = rule.params
    mask = pd.Series(True, index=df.index)
    if "book_min" in params:
        mask &= df["book_p_side"].notna() & (df["book_p_side"] >= float(params["book_min"]))
    if "spread_max" in params:
        mask &= df["spread_cents"].notna() & (df["spread_cents"] <= float(params["spread_max"]))
    if "feature" in params:
        feature = str(params["feature"])
        if feature not in df.columns:
            return pd.Series(False, index=df.index)
        mask &= df[feature].notna() & (df[feature] >= float(params["min"]))
    if "adverse_max" in params:
        mask &= df["adverse_move_15m"].notna() & (df["adverse_move_15m"] <= float(params["adverse_max"]))
    return mask.fillna(False)


def split_dataset(df: pd.DataFrame) -> pd.DataFrame:
    out = df.sort_values("entry_dt").reset_index(drop=True).copy()
    n = len(out)
    train_end = int(math.floor(n * 0.60))
    val_end = int(math.floor(n * 0.80))
    split = np.full(n, "holdout", dtype=object)
    split[:train_end] = "train"
    split[train_end:val_end] = "validation"
    out["split"] = split
    return out


def metrics_for_mask(df: pd.DataFrame, mask: pd.Series, base: pd.DataFrame) -> Dict[str, Any]:
    selected = df[mask].copy()
    total = int(len(base))
    rows = int(len(selected))
    wins = int(selected["win"].sum()) if rows else 0
    return {
        "rows": rows,
        "wins": wins,
        "accuracy": wins / rows if rows else None,
        "retention": rows / total if total else None,
        "total_rows": total,
        "contracts": rows,
        "contract_wins": wins,
        "trades": rows,
        "trade_wins": wins,
    }


def selected_metrics(df: pd.DataFrame, mask: pd.Series) -> Dict[str, Dict[str, Any]]:
    out = {"all": metrics_for_mask(df, mask, df)}
    for split in ["train", "validation", "holdout"]:
        part = df[df["split"] == split]
        out[split] = metrics_for_mask(part, mask.reindex(part.index).fillna(False), part)
    return out


def baseline_metrics(df: pd.DataFrame) -> Dict[str, Dict[str, Any]]:
    return selected_metrics(df, pd.Series(True, index=df.index))


def rule_passes(metrics: Dict[str, Dict[str, Any]], with_samples: bool) -> bool:
    for split in ["all", "validation", "holdout"]:
        metric = metrics[split]
        if (metric["accuracy"] or 0.0) < MIN_TARGET_ACCURACY:
            return False
        if (metric["retention"] or 0.0) < MIN_RETENTION:
            return False
    if with_samples:
        if metrics["all"]["rows"] < MIN_SELECTED_ROWS:
            return False
        if metrics["holdout"]["rows"] < MIN_HOLDOUT_ROWS:
            return False
    return True


def ranking_tuple(result: Dict[str, Any]) -> tuple:
    metrics = result["metrics"]
    all_m = metrics["all"]
    val_m = metrics["validation"]
    hold_m = metrics["holdout"]
    min_acc = min(all_m["accuracy"] or 0.0, val_m["accuracy"] or 0.0, hold_m["accuracy"] or 0.0)
    min_ret = min(all_m["retention"] or 0.0, val_m["retention"] or 0.0, hold_m["retention"] or 0.0)
    return (
        int(result["target_pass"]),
        int(result["observed_pass"]),
        min_acc,
        hold_m["accuracy"] or 0.0,
        min_ret,
        all_m["rows"],
    )


def oracle_bounds(metrics: Dict[str, Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
    out: Dict[str, List[Dict[str, Any]]] = {}
    for split in ["all", "validation", "holdout"]:
        split_bounds: List[Dict[str, Any]] = []
        for floor in RETENTION_FLOORS:
            raw = {
                "trades": metrics[split]["rows"],
                "contracts": metrics[split]["rows"],
                "trade_wins": metrics[split]["wins"],
                "contract_wins": metrics[split]["wins"],
            }
            bound = oracle_bound(raw, floor)
            bound["target_possible"] = (bound["max_contract_accuracy"] or 0.0) >= MIN_TARGET_ACCURACY
            split_bounds.append(bound)
        out[split] = split_bounds
    return out


def evaluate(df: pd.DataFrame, rules: Iterable[Rule]) -> Dict[str, Any]:
    split_df = split_dataset(df)
    base = baseline_metrics(split_df)
    results: List[Dict[str, Any]] = []
    for rule in rules:
        mask = apply_rule(split_df, rule)
        metrics = selected_metrics(split_df, mask)
        observed_pass = rule_passes(metrics, with_samples=False)
        target_pass = rule_passes(metrics, with_samples=True)
        results.append(
            {
                "family": rule.family,
                "label": rule.label,
                "params": rule.params,
                "metrics": metrics,
                "observed_pass": observed_pass,
                "target_pass": target_pass,
            }
        )
    results.sort(key=ranking_tuple, reverse=True)
    return {
        "baseline": base,
        "oracle_bounds": oracle_bounds(base),
        "results": results,
        "target_pass_count": sum(1 for row in results if row["target_pass"]),
        "observed_pass_count": sum(1 for row in results if row["observed_pass"]),
        "row_count": int(len(split_df)),
    }


def calibration_table(df: pd.DataFrame, feature: str, bins: List[float]) -> List[Dict[str, Any]]:
    if df.empty or feature not in df.columns:
        return []
    rows: List[Dict[str, Any]] = []
    values = pd.to_numeric(df[feature], errors="coerce")
    for lo, hi in zip(bins[:-1], bins[1:]):
        part = df[(values >= lo) & (values < hi)]
        if part.empty:
            continue
        rows.append(
            {
                "feature": feature,
                "bin": f"[{lo:g}, {hi:g})",
                "rows": int(len(part)),
                "wins": int(part["win"].sum()),
                "accuracy": float(part["win"].mean()),
            }
        )
    part = df[values >= bins[-1]]
    if not part.empty:
        rows.append(
            {
                "feature": feature,
                "bin": f">={bins[-1]:g}",
                "rows": int(len(part)),
                "wins": int(part["win"].sum()),
                "accuracy": float(part["win"].mean()),
            }
        )
    return rows


def flatten_candidates(evaluations: Dict[str, Any]) -> pd.DataFrame:
    rows: List[Dict[str, Any]] = []
    for mode, evaluation in evaluations.items():
        for result in evaluation["results"]:
            row: Dict[str, Any] = {
                "mode": mode,
                "family": result["family"],
                "label": result["label"],
                "observed_pass": result["observed_pass"],
                "target_pass": result["target_pass"],
            }
            for split, metrics in result["metrics"].items():
                for key, value in metrics.items():
                    row[f"{split}_{key}"] = value
            rows.append(row)
    return pd.DataFrame(rows)


def metric_line(evaluation: Dict[str, Any], split: str) -> str:
    metric = evaluation["baseline"][split]
    return f"{metric['wins']}/{metric['rows']} = {pct(metric['accuracy'])}"


def write_report(
    path: Path,
    generated: str,
    raw: pd.DataFrame,
    physics: pd.DataFrame,
    mode_frames: Dict[str, pd.DataFrame],
    evaluations: Dict[str, Any],
    candle_info: Dict[str, Any],
    calibration: Dict[str, List[Dict[str, Any]]],
) -> None:
    lines: List[str] = []
    lines.append("# Live Heartbeat Physics Prior Audit")
    lines.append("")
    lines.append(f"Generated UTC: `{generated}`")
    lines.append("")
    lines.append("## Scope")
    lines.append("")
    lines.append("- Research-only probe; no orders are submitted and no bot files are modified.")
    lines.append("- Source: live websocket heartbeat rows from `logs/live_mushroom_v28_size2/bot.log`.")
    lines.append("- Candidate side is the book favorite at each heartbeat, bucketed by mode.")
    lines.append("- BTC spot and realized-volatility physics use the cached Coinbase 1m candle file.")
    lines.append("- This is not filled-trade completion evidence; heartbeat rows are correlated market states.")
    lines.append("")
    lines.append("## Coverage")
    lines.append("")
    lines.append(f"- Raw favorite heartbeat rows: {len(raw)}")
    lines.append(f"- Rows with candle physics: {len(physics)}")
    lines.append(f"- Unique markets with physics: {physics['market'].nunique() if not physics.empty else 0}")
    lines.append(f"- Candle rows: {candle_info.get('rows', 0)}")
    lines.append(f"- Candle range: {candle_info.get('start')} to {candle_info.get('end')}")
    lines.append("")
    lines.append("## Mode Results")
    lines.append("")
    for mode in ["favorite_minute_bucket", "favorite_first_per_market", "favorite_all_heartbeats"]:
        frame = mode_frames.get(mode, pd.DataFrame())
        evaluation = evaluations.get(mode)
        if frame.empty or not evaluation:
            continue
        lines.append(f"### `{mode}`")
        lines.append("")
        lines.append(f"- Rows: {len(frame)}")
        lines.append(f"- Unique markets: {frame['market'].nunique()}")
        lines.append(f"- Baseline all favorite accuracy: {metric_line(evaluation, 'all')}")
        lines.append(f"- Baseline holdout favorite accuracy: {metric_line(evaluation, 'holdout')}")
        lines.append(f"- Target-pass rules: {evaluation['target_pass_count']}")
        lines.append("")
        lines.append("Perfect-selector oracle bounds:")
        lines.append("")
        lines.append("| split | retention floor | required rows | max accuracy | 95% possible |")
        lines.append("|---|---:|---:|---:|---|")
        for split in ["all", "validation", "holdout"]:
            for bound in evaluation["oracle_bounds"][split]:
                lines.append(
                    f"| {split} | {pct(bound['retention_floor'])} | {bound['required_contracts']} | "
                    f"{pct(bound['max_contract_accuracy'])} | {bound['target_possible']} |"
                )
        lines.append("")
        lines.append("Top high-retention rules:")
        lines.append("")
        lines.append("| rank | family | rule | all acc | all ret | validation acc | holdout acc | holdout ret | rows | target |")
        lines.append("|---:|---|---|---:|---:|---:|---:|---:|---:|---|")
        high_ret = [
            row
            for row in evaluation["results"]
            if (row["metrics"]["all"]["retention"] or 0.0) >= MIN_RETENTION
            and (row["metrics"]["holdout"]["retention"] or 0.0) >= MIN_RETENTION
        ][:10]
        for idx, result in enumerate(high_ret, start=1):
            all_m = result["metrics"]["all"]
            val_m = result["metrics"]["validation"]
            hold_m = result["metrics"]["holdout"]
            lines.append(
                f"| {idx} | {result['family']} | `{result['label']}` | {pct(all_m['accuracy'])} | "
                f"{pct(all_m['retention'])} | {pct(val_m['accuracy'])} | {pct(hold_m['accuracy'])} | "
                f"{pct(hold_m['retention'])} | {all_m['rows']} | {result['target_pass']} |"
            )
        if not high_ret:
            lines.append("|  |  | no rule retained at least 75% of all and holdout rows |  |  |  |  |  |  |  |")
        lines.append("")
    lines.append("## Calibration")
    lines.append("")
    for feature, rows in calibration.items():
        lines.append(f"### `{feature}`")
        lines.append("")
        lines.append("| bin | rows | wins | realized accuracy |")
        lines.append("|---|---:|---:|---:|")
        for row in rows:
            lines.append(f"| {row['bin']} | {row['rows']} | {row['wins']} | {pct(row['accuracy'])} |")
        lines.append("")
    lines.append("## Completion Read")
    lines.append("")
    primary = evaluations.get(PRIMARY_MODE)
    if primary and primary["target_pass_count"] > 0:
        lines.append(
            "The primary heartbeat tape has at least one exploratory selector meeting 95% accuracy "
            "and 75% retention on chronological splits, but it is still not filled-trade completion evidence."
        )
    else:
        lines.append(
            "The primary heartbeat tape does not produce a non-overfit 95% / 75% selector under the configured "
            "chronological split and sample checks."
        )
    lines.append(
        "Use this artifact to falsify priors and design the next FV surface; use locked fresh fills to complete the active goal."
    )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--fetch-btc-candles", action="store_true")
    args = parser.parse_args()

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    markets, outcomes = parse_bot_log(BOT_LOG)
    outcomes = closed_market_outcomes_only(markets, outcomes)
    raw = heartbeat_favorite_rows(markets, outcomes)
    if raw.empty:
        raise SystemExit("No usable heartbeat rows found.")
    physics, candle_info = attach_physics(raw, fetch_btc_candles=bool(args.fetch_btc_candles))
    physics = physics[physics["outcome_available"]].copy()
    if physics.empty:
        raise SystemExit("No resolved heartbeat rows with candle physics found.")

    rules = make_rules()
    mode_frames: Dict[str, pd.DataFrame] = {}
    evaluations: Dict[str, Any] = {}
    for mode in ["favorite_minute_bucket", "favorite_first_per_market", "favorite_all_heartbeats"]:
        frame = dedupe_mode(physics, mode)
        mode_frames[mode] = frame
        if not frame.empty:
            evaluations[mode] = evaluate(frame, rules)

    primary_frame = mode_frames.get(PRIMARY_MODE, pd.DataFrame())
    calibration = {
        "book_p_side": calibration_table(primary_frame, "book_p_side", [0.50, 0.60, 0.70, 0.80, 0.90]),
        "brownian_p_rv_15m": calibration_table(
            primary_frame,
            "brownian_p_rv_15m",
            [0.00, 0.25, 0.50, 0.75, 0.90],
        ),
        "book_minus_brownian_rv15": calibration_table(
            primary_frame,
            "book_minus_brownian_rv15",
            [-1.0, -0.25, 0.0, 0.25, 0.5],
        ),
    }

    generated = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%SZ")
    md_latest = OUT_DIR / "live_heartbeat_physics_prior_audit_latest.md"
    md_stamp = OUT_DIR / f"live_heartbeat_physics_prior_audit_{generated}.md"
    json_latest = OUT_DIR / "live_heartbeat_physics_prior_audit_latest.json"
    json_stamp = OUT_DIR / f"live_heartbeat_physics_prior_audit_{generated}.json"
    ledger_latest = OUT_DIR / "live_heartbeat_physics_prior_ledger_latest.csv"
    ledger_stamp = OUT_DIR / f"live_heartbeat_physics_prior_ledger_{generated}.csv"
    candidates_latest = OUT_DIR / "live_heartbeat_physics_prior_candidates_latest.csv"
    candidates_stamp = OUT_DIR / f"live_heartbeat_physics_prior_candidates_{generated}.csv"

    combined = pd.concat([frame for frame in mode_frames.values() if not frame.empty], ignore_index=True)
    combined.to_csv(ledger_latest, index=False)
    combined.to_csv(ledger_stamp, index=False)
    candidates = flatten_candidates(evaluations)
    candidates.to_csv(candidates_latest, index=False)
    candidates.to_csv(candidates_stamp, index=False)

    summary = {
        "generated_utc": generated,
        "raw_rows": int(len(raw)),
        "physics_rows": int(len(physics)),
        "candle_info": candle_info,
        "evaluations": evaluations,
        "calibration": calibration,
    }
    for path in [json_latest, json_stamp]:
        path.write_text(json.dumps(clean_json(summary), indent=2, sort_keys=True), encoding="utf-8")
    write_report(md_latest, generated, raw, physics, mode_frames, evaluations, candle_info, calibration)
    write_report(md_stamp, generated, raw, physics, mode_frames, evaluations, candle_info, calibration)

    primary = evaluations.get(PRIMARY_MODE, {})
    print("Live heartbeat physics prior audit complete")
    print(f"raw_rows={len(raw)} physics_rows={len(physics)}")
    if primary:
        base = primary["baseline"]["all"]
        hold = primary["baseline"]["holdout"]
        print(
            f"primary={PRIMARY_MODE} rows={primary['row_count']} "
            f"baseline={base['wins']}/{base['rows']} holdout={hold['wins']}/{hold['rows']} "
            f"target_pass={primary['target_pass_count']}"
        )
    print(f"report={md_latest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
