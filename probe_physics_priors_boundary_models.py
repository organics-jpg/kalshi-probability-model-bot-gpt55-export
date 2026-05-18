"""Physics-first boundary model probes for BTC15M live trade ledgers.

This is research-only. It reads existing ledgers/caches and writes artifacts
under logs/edge_research. It does not import or modify the live bot.

The purpose is to question the priors behind the current fair-value surface:

- Is the raw distance from spot to strike enough?
- Is v28 sigma or local realized sigma the right clock?
- Does short-term adverse BTC flow explain the losers?
- Can any simple physics gate reach 95% realized accuracy while retaining
  at least 75% of trade volume on chronological validation/holdout splits?
"""
from __future__ import annotations

import csv
import argparse
import json
import math
import os
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

import numpy as np
import pandas as pd

from probe_live_9070_v28_replay import fetch_coinbase_btc_1m


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
CURRENT_LEDGER = OUT_DIR / "fv_accuracy_volume_trades_latest.csv"
REPLAY_LEDGER = OUT_DIR / "live_9070_v28_replay_trades_latest.csv"
COINBASE_BTC_CACHE = OUT_DIR / "coinbase_btc_usd_1m_cache.parquet"

MIN_TARGET_ACCURACY = 0.95
MIN_CONTRACT_RETENTION = 0.75
MIN_TRADE_RETENTION = 0.75
MIN_ALL_SELECTED_TRADES = 75
MIN_HOLDOUT_SELECTED_TRADES = 15
MIN_ALL_SELECTED_CONTRACTS = 150
MIN_HOLDOUT_SELECTED_CONTRACTS = 30


def quarantine_corrupt_cache(path: Path) -> None:
    if not path.exists():
        return
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    corrupt_path = path.with_name(f"{path.stem}.corrupt_{stamp}_{os.getpid()}{path.suffix}")
    try:
        path.replace(corrupt_path)
    except OSError:
        pass


def read_coinbase_cache(path: Path) -> pd.DataFrame:
    if not path.exists():
        return pd.DataFrame()
    try:
        return pd.read_parquet(path)
    except Exception:
        quarantine_corrupt_cache(path)
        return pd.DataFrame()


def write_coinbase_cache_atomic(frame: pd.DataFrame, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S_%f")
    tmp_path = path.with_name(f"{path.stem}.{stamp}_{os.getpid()}.tmp{path.suffix}")
    frame.to_parquet(tmp_path, index=False)
    tmp_path.replace(path)


def utc_stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%SZ")


def as_bool_series(series: pd.Series) -> pd.Series:
    text = series.astype(str).str.strip().str.lower()
    return text.isin(["true", "1", "yes", "y"])


def normal_cdf_np(z: np.ndarray | pd.Series | float) -> np.ndarray:
    arr = np.asarray(z, dtype=float)
    if arr.size == 0:
        return np.asarray(arr, dtype=float)
    out = 0.5 * (1.0 + np.vectorize(math.erf)(arr / math.sqrt(2.0)))
    return np.asarray(out, dtype=float)


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
        value = float(value)
    if isinstance(value, float):
        if math.isnan(value) or math.isinf(value):
            return None
        return value
    if isinstance(value, (pd.Timestamp,)):
        return value.isoformat()
    return value


def pct(x: Optional[float]) -> str:
    if x is None or not math.isfinite(float(x)):
        return "NA"
    return f"{100.0 * float(x):.2f}%"


def fnum(x: Optional[float], digits: int = 3) -> str:
    if x is None or not math.isfinite(float(x)):
        return "NA"
    return f"{float(x):.{digits}f}"


def load_current_v28() -> pd.DataFrame:
    if not CURRENT_LEDGER.exists():
        return pd.DataFrame()
    df = pd.read_csv(CURRENT_LEDGER)
    if df.empty:
        return df
    out = pd.DataFrame(
        {
            "dataset": "current_v28_live_fills",
            "entry_dt": pd.to_datetime(df["ts_wall"], utc=True, errors="coerce"),
            "market": df["market"].astype(str),
            "side": df["side"].astype(str).str.lower(),
            "outcome": df["outcome"].astype(str).str.lower(),
            "win": as_bool_series(df["win"]),
            "qty": pd.to_numeric(df["qty"], errors="coerce"),
            "ask_cents": pd.to_numeric(df["ask_cents"], errors="coerce"),
            "spot": pd.to_numeric(df.get("v28_btc_price"), errors="coerce"),
            "strike": pd.to_numeric(df.get("v28_strike"), errors="coerce"),
            "seconds_to_close": pd.to_numeric(df.get("v28_seconds_to_close"), errors="coerce"),
            "v28_sigma_t_dollars": pd.to_numeric(df.get("v28_sigma_t_dollars"), errors="coerce"),
            "v28_p_side": pd.to_numeric(df.get("v28_p_side"), errors="coerce"),
            "v28_edge_cents": pd.to_numeric(df.get("v28_edge_cents"), errors="coerce"),
            "market_p_side": pd.to_numeric(df.get("market_p_side"), errors="coerce"),
            "source_file": str(CURRENT_LEDGER),
        }
    )
    return out


def load_replay_9070() -> pd.DataFrame:
    if not REPLAY_LEDGER.exists():
        return pd.DataFrame()
    df = pd.read_csv(REPLAY_LEDGER)
    if df.empty:
        return df
    out = pd.DataFrame(
        {
            "dataset": "live_90_70_replay",
            "entry_dt": pd.to_datetime(df["entry_dt"], utc=True, errors="coerce"),
            "market": df["market"].astype(str),
            "side": df["side"].astype(str).str.lower(),
            "outcome": df["market_result"].astype(str).str.lower(),
            "win": as_bool_series(df["win"]),
            "qty": pd.to_numeric(df["qty"], errors="coerce"),
            "ask_cents": pd.to_numeric(df["ask_cents"], errors="coerce"),
            "spot": pd.to_numeric(df["btc_close"], errors="coerce"),
            "strike": pd.to_numeric(df["strike"], errors="coerce"),
            "seconds_to_close": pd.to_numeric(df["seconds_to_close"], errors="coerce"),
            "v28_sigma_t_dollars": pd.to_numeric(df["v28_sigma_t_dollars"], errors="coerce"),
            "v28_p_side": pd.to_numeric(df["v28_p_side"], errors="coerce"),
            "v28_edge_cents": pd.to_numeric(df["v28_edge_cents"], errors="coerce"),
            "market_p_side": np.nan,
            "source_file": str(REPLAY_LEDGER),
        }
    )
    return out


def common_physics_features(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return df
    out = df.copy()
    out = out.dropna(subset=["entry_dt", "side", "win", "qty", "spot", "strike", "seconds_to_close"])
    out = out[out["side"].isin(["yes", "no"])].copy()
    out = out[out["qty"] > 0].copy()
    out = out[out["seconds_to_close"] > 0].copy()
    out["side_sign"] = np.where(out["side"] == "yes", 1.0, -1.0)
    out["margin_dollars"] = out["side_sign"] * (out["spot"] - out["strike"])
    out["margin_per_sqrt_sec"] = out["margin_dollars"] / np.sqrt(out["seconds_to_close"])
    out["margin_per_sqrt_min"] = out["margin_dollars"] / np.sqrt(out["seconds_to_close"] / 60.0)
    out["margin_per_v28_sigma"] = out["margin_dollars"] / out["v28_sigma_t_dollars"]
    out["brownian_p_v28_sigma"] = normal_cdf_np(out["margin_per_v28_sigma"])
    out["abs_margin_dollars"] = out["margin_dollars"].abs()
    out["itm_at_entry"] = out["margin_dollars"] >= 0
    out = out.sort_values(["dataset", "entry_dt", "market", "side"]).reset_index(drop=True)
    return out


def load_coinbase_candles(entries: pd.DataFrame, fetch_missing: bool) -> pd.DataFrame:
    frames: List[pd.DataFrame] = []
    candles = read_coinbase_cache(COINBASE_BTC_CACHE)
    if not candles.empty:
        frames.append(candles)
    if fetch_missing and not entries.empty:
        start = entries["entry_dt"].min() - pd.Timedelta(hours=2)
        end = entries["entry_dt"].max() + pd.Timedelta(minutes=5)
        need_fetch = True
        if not candles.empty and "close_dt" in candles.columns:
            probe = candles.copy()
            probe["close_dt"] = pd.to_datetime(probe["close_dt"], utc=True, errors="coerce")
            covered_start = probe["close_dt"].min()
            covered_end = probe["close_dt"].max()
            need_fetch = bool(pd.isna(covered_start) or pd.isna(covered_end) or covered_start > start or covered_end < end)
        if need_fetch:
            fetched = fetch_coinbase_btc_1m(start, end)
            if not fetched.empty:
                frames.append(fetched)
                cache_df = pd.concat(frames, ignore_index=True)
                cache_df["close_dt"] = pd.to_datetime(cache_df["close_dt"], utc=True, errors="coerce")
                cache_df = cache_df.dropna(subset=["close_dt", "open", "high", "low", "close"])
                cache_df = cache_df.sort_values("close_dt").drop_duplicates("close_dt", keep="last").reset_index(drop=True)
                write_coinbase_cache_atomic(cache_df, COINBASE_BTC_CACHE)
                candles = cache_df
    if frames and candles.empty:
        candles = pd.concat(frames, ignore_index=True)
    if candles.empty:
        return pd.DataFrame()
    candles["close_dt"] = pd.to_datetime(candles["close_dt"], utc=True, errors="coerce")
    for col in ["open", "high", "low", "close"]:
        candles[col] = pd.to_numeric(candles[col], errors="coerce")
    candles = candles.dropna(subset=["close_dt", "open", "high", "low", "close"])
    candles = candles.sort_values("close_dt").drop_duplicates("close_dt", keep="last").reset_index(drop=True)
    if candles.empty:
        return candles
    candles["log_ret"] = np.log(candles["close"] / candles["close"].shift(1))
    candles["dollar_ret"] = candles["close"].diff()
    for window in [5, 15, 30, 60]:
        candles[f"sigma_min_log_{window}m"] = candles["log_ret"].rolling(window).std() * candles["close"]
        candles[f"sigma_min_dollar_{window}m"] = candles["dollar_ret"].rolling(window).std()
    return candles


def asof_values(candles: pd.DataFrame, target_dt: pd.Series, column: str, max_age_seconds: float) -> np.ndarray:
    if candles.empty:
        return np.full(len(target_dt), np.nan)
    times = candles["close_dt"].astype("int64").to_numpy()
    target = pd.to_datetime(target_dt, utc=True, errors="coerce").astype("int64").to_numpy()
    idx = np.searchsorted(times, target, side="right") - 1
    values = np.full(len(target), np.nan)
    valid = idx >= 0
    if not valid.any():
        return values
    ages_ns = target[valid] - times[idx[valid]]
    fresh = ages_ns <= max_age_seconds * 1_000_000_000
    valid_positions = np.where(valid)[0][fresh]
    if len(valid_positions):
        values[valid_positions] = candles[column].to_numpy()[idx[valid_positions]]
    return values


def add_candle_physics(df: pd.DataFrame, candles: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    if out.empty:
        return out
    if candles.empty:
        return out

    out["candle_close_at_entry"] = asof_values(candles, out["entry_dt"], "close", 120.0)
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
            out[f"conservative_p_{lag}m_rv_{window}m"] = np.minimum(
                out["brownian_p_v28_sigma"], out[f"drift_p_{lag}m_rv_{window}m"]
            )
    return out


@dataclass(frozen=True)
class Rule:
    rule_id: str
    family: str
    label: str
    params: Dict[str, Any]


def make_rules() -> List[Rule]:
    rules: List[Rule] = []

    def add(family: str, label: str, params: Dict[str, Any]) -> None:
        rules.append(Rule(f"physics_rule_{len(rules):05d}", family, label, params))

    for ask_max in [85.0, 87.0, 90.0, 92.0, 95.0, 100.0]:
        add("baseline_ask_cap", f"ask<={ask_max:g}", {"ask_max": ask_max})

    for ask_max in [90.0, 92.0, 95.0, 100.0]:
        for margin_min in [-100.0, -50.0, 0.0, 25.0, 50.0, 75.0, 100.0, 125.0, 150.0, 200.0]:
            add(
                "boundary_margin",
                f"ask<={ask_max:g}; margin>={margin_min:g}",
                {"ask_max": ask_max, "margin_min": margin_min},
            )
        for mps_min in [-5.0, -2.0, 0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0]:
            add(
                "boundary_sqrt_time",
                f"ask<={ask_max:g}; margin/sqrt(sec)>={mps_min:g}",
                {"ask_max": ask_max, "margin_per_sqrt_sec_min": mps_min},
            )
        for sigma_min in [-1.0, -0.5, 0.0, 0.25, 0.5, 0.75, 1.0, 1.25, 1.5, 2.0]:
            add(
                "boundary_v28_sigma",
                f"ask<={ask_max:g}; margin/v28_sigma>={sigma_min:g}",
                {"ask_max": ask_max, "margin_per_v28_sigma_min": sigma_min},
            )
        for p_min in [0.50, 0.55, 0.60, 0.65, 0.70, 0.75, 0.80, 0.85, 0.90, 0.95]:
            add(
                "brownian_v28_sigma",
                f"ask<={ask_max:g}; Phi(margin/v28_sigma)>={p_min:g}",
                {"ask_max": ask_max, "p_feature": "brownian_p_v28_sigma", "p_min": p_min},
            )

    for ask_max in [90.0, 92.0, 95.0, 100.0]:
        for window in [15, 30, 60]:
            for p_min in [0.50, 0.55, 0.60, 0.65, 0.70, 0.75, 0.80, 0.85, 0.90, 0.95]:
                add(
                    "brownian_realized_vol",
                    f"ask<={ask_max:g}; Phi(margin/rv{window})>={p_min:g}",
                    {"ask_max": ask_max, "p_feature": f"brownian_p_rv_{window}m", "p_min": p_min},
                )
            for sigma_min in [-1.0, -0.5, 0.0, 0.25, 0.5, 0.75, 1.0, 1.25, 1.5, 2.0]:
                add(
                    "realized_vol_cushion",
                    f"ask<={ask_max:g}; margin/rv{window}>={sigma_min:g}",
                    {"ask_max": ask_max, "feature": f"margin_per_rv_sigma_{window}m", "min": sigma_min},
                )

    for ask_max in [90.0, 92.0, 95.0, 100.0]:
        for lag in [3, 5, 10, 15]:
            for adverse in [10.0, 25.0, 50.0, 75.0, 100.0, 150.0]:
                for cushion in [0.0, 0.25, 0.5, 0.75, 1.0]:
                    add(
                        "adverse_drift_guard",
                        f"ask<={ask_max:g}; block {lag}m adverse>{adverse:g} unless v28 cushion>{cushion:g}",
                        {
                            "ask_max": ask_max,
                            "lag": lag,
                            "adverse_min": adverse,
                            "cushion_min": cushion,
                        },
                    )
            for projected_min in [-100.0, -50.0, 0.0, 25.0, 50.0, 75.0, 100.0]:
                add(
                    "drift_projection",
                    f"ask<={ask_max:g}; projected_margin_{lag}m>={projected_min:g}",
                    {
                        "ask_max": ask_max,
                        "feature": f"drift_projected_margin_{lag}m",
                        "min": projected_min,
                    },
                )
            for window in [15, 30]:
                for p_min in [0.50, 0.55, 0.60, 0.65, 0.70, 0.75, 0.80, 0.85, 0.90]:
                    add(
                        "conservative_drift_prob",
                        f"ask<={ask_max:g}; min(v28_brownian, drift{lag}/rv{window})>={p_min:g}",
                        {
                            "ask_max": ask_max,
                            "p_feature": f"conservative_p_{lag}m_rv_{window}m",
                            "p_min": p_min,
                        },
                    )
    return rules


def apply_rule(df: pd.DataFrame, rule: Rule) -> pd.Series:
    params = rule.params
    mask = pd.Series(True, index=df.index)
    ask_max = params.get("ask_max")
    if ask_max is not None:
        mask &= df["ask_cents"].notna() & (df["ask_cents"] <= float(ask_max))
    if "margin_min" in params:
        mask &= df["margin_dollars"].notna() & (df["margin_dollars"] >= float(params["margin_min"]))
    if "margin_per_sqrt_sec_min" in params:
        mask &= df["margin_per_sqrt_sec"].notna() & (df["margin_per_sqrt_sec"] >= float(params["margin_per_sqrt_sec_min"]))
    if "margin_per_v28_sigma_min" in params:
        mask &= df["margin_per_v28_sigma"].notna() & (df["margin_per_v28_sigma"] >= float(params["margin_per_v28_sigma_min"]))
    if "feature" in params:
        feature = str(params["feature"])
        if feature not in df.columns:
            return pd.Series(False, index=df.index)
        mask &= df[feature].notna() & (df[feature] >= float(params["min"]))
    if "p_feature" in params:
        feature = str(params["p_feature"])
        if feature not in df.columns:
            return pd.Series(False, index=df.index)
        mask &= df[feature].notna() & (df[feature] >= float(params["p_min"]))
    if rule.family == "adverse_drift_guard":
        lag = int(params["lag"])
        adverse_feature = f"adverse_move_{lag}m"
        if adverse_feature not in df.columns:
            return pd.Series(False, index=df.index)
        adverse = df[adverse_feature].fillna(np.inf)
        cushion = df["margin_per_v28_sigma"].fillna(-np.inf)
        blocked = (adverse >= float(params["adverse_min"])) & (cushion <= float(params["cushion_min"]))
        mask &= ~blocked
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
    total_trades = int(len(base))
    total_contracts = int(base["qty"].sum()) if not base.empty else 0
    trades = int(len(selected))
    contracts = int(selected["qty"].sum()) if not selected.empty else 0
    winning = selected[selected["win"]]
    trade_wins = int(len(winning))
    contract_wins = int(winning["qty"].sum()) if not winning.empty else 0
    return {
        "trades": trades,
        "contracts": contracts,
        "trade_wins": trade_wins,
        "contract_wins": contract_wins,
        "trade_accuracy": trade_wins / trades if trades else None,
        "contract_accuracy": contract_wins / contracts if contracts else None,
        "trade_retention": trades / total_trades if total_trades else None,
        "contract_retention": contracts / total_contracts if total_contracts else None,
        "total_trades": total_trades,
        "total_contracts": total_contracts,
    }


def baseline_metrics(df: pd.DataFrame) -> Dict[str, Dict[str, Any]]:
    out: Dict[str, Dict[str, Any]] = {}
    all_mask = pd.Series(True, index=df.index)
    out["all"] = metrics_for_mask(df, all_mask, df)
    for split in ["train", "validation", "holdout"]:
        part = df[df["split"] == split]
        out[split] = metrics_for_mask(part, pd.Series(True, index=part.index), part)
    return out


def selected_metrics(df: pd.DataFrame, mask: pd.Series) -> Dict[str, Dict[str, Any]]:
    out: Dict[str, Dict[str, Any]] = {}
    out["all"] = metrics_for_mask(df, mask, df)
    for split in ["train", "validation", "holdout"]:
        part = df[df["split"] == split]
        out[split] = metrics_for_mask(part, mask.reindex(part.index).fillna(False), part)
    return out


def rule_passes(metrics: Dict[str, Dict[str, Any]], with_samples: bool) -> bool:
    for split in ["all", "validation", "holdout"]:
        m = metrics[split]
        if (m["trade_accuracy"] or 0.0) < MIN_TARGET_ACCURACY:
            return False
        if (m["contract_accuracy"] or 0.0) < MIN_TARGET_ACCURACY:
            return False
        if (m["trade_retention"] or 0.0) < MIN_TRADE_RETENTION:
            return False
        if (m["contract_retention"] or 0.0) < MIN_CONTRACT_RETENTION:
            return False
    if with_samples:
        if metrics["all"]["trades"] < MIN_ALL_SELECTED_TRADES:
            return False
        if metrics["all"]["contracts"] < MIN_ALL_SELECTED_CONTRACTS:
            return False
        if metrics["holdout"]["trades"] < MIN_HOLDOUT_SELECTED_TRADES:
            return False
        if metrics["holdout"]["contracts"] < MIN_HOLDOUT_SELECTED_CONTRACTS:
            return False
    return True


def ranking_tuple(result: Dict[str, Any]) -> tuple:
    metrics = result["metrics"]
    all_m = metrics["all"]
    val_m = metrics["validation"]
    hold_m = metrics["holdout"]
    min_acc = min(
        all_m["contract_accuracy"] or 0.0,
        val_m["contract_accuracy"] or 0.0,
        hold_m["contract_accuracy"] or 0.0,
    )
    min_ret = min(
        all_m["contract_retention"] or 0.0,
        val_m["contract_retention"] or 0.0,
        hold_m["contract_retention"] or 0.0,
    )
    return (
        int(result["target_pass"]),
        int(result["observed_pass"]),
        min_acc,
        hold_m["contract_accuracy"] or 0.0,
        min_ret,
        all_m["contracts"],
    )


def evaluate_dataset(df: pd.DataFrame, rules: Iterable[Rule]) -> Dict[str, Any]:
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
                "rule_id": rule.rule_id,
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
        "results": results,
        "target_pass_count": sum(1 for row in results if row["target_pass"]),
        "observed_pass_count": sum(1 for row in results if row["observed_pass"]),
        "row_count": int(len(split_df)),
        "contract_count": int(split_df["qty"].sum()),
    }


def flatten_result(dataset: str, result: Dict[str, Any]) -> Dict[str, Any]:
    row: Dict[str, Any] = {
        "dataset": dataset,
        "rule_id": result["rule_id"],
        "family": result["family"],
        "label": result["label"],
        "observed_pass": result["observed_pass"],
        "target_pass": result["target_pass"],
    }
    for split, metrics in result["metrics"].items():
        for key, value in metrics.items():
            row[f"{split}_{key}"] = value
    return row


def write_candidates_csv(evaluations: Dict[str, Any], path: Path) -> None:
    rows: List[Dict[str, Any]] = []
    for dataset, evaluation in evaluations.items():
        for result in evaluation["results"]:
            rows.append(flatten_result(dataset, result))
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    fields = sorted({key for row in rows for key in row})
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def write_feature_ledger(df: pd.DataFrame, path: Path) -> None:
    fields = [
        "dataset",
        "split",
        "entry_dt",
        "market",
        "side",
        "outcome",
        "win",
        "qty",
        "ask_cents",
        "spot",
        "strike",
        "seconds_to_close",
        "margin_dollars",
        "margin_per_sqrt_sec",
        "margin_per_v28_sigma",
        "brownian_p_v28_sigma",
        "rv_sigma_t_15m",
        "margin_per_rv_sigma_15m",
        "brownian_p_rv_15m",
        "signed_move_3m",
        "signed_move_5m",
        "signed_move_15m",
        "adverse_move_3m",
        "adverse_move_5m",
        "drift_projected_margin_3m",
        "drift_projected_margin_5m",
        "conservative_p_3m_rv_15m",
        "v28_p_side",
        "v28_edge_cents",
        "source_file",
    ]
    present = [field for field in fields if field in df.columns]
    df[present].to_csv(path, index=False)


def feature_loss_summary(df: pd.DataFrame) -> Dict[str, Any]:
    features = [
        "margin_dollars",
        "margin_per_sqrt_sec",
        "margin_per_v28_sigma",
        "brownian_p_v28_sigma",
        "margin_per_rv_sigma_15m",
        "signed_move_3m",
        "signed_move_5m",
        "adverse_move_3m",
        "adverse_move_5m",
    ]
    out: Dict[str, Any] = {}
    for dataset, part in df.groupby("dataset"):
        losses = part[~part["win"]].copy()
        wins = part[part["win"]].copy()
        ds: Dict[str, Any] = {
            "rows": int(len(part)),
            "contracts": int(part["qty"].sum()),
            "loss_trades": int(len(losses)),
            "loss_contracts": int(losses["qty"].sum()) if not losses.empty else 0,
            "features": {},
        }
        for feature in features:
            if feature not in part.columns:
                continue
            ds["features"][feature] = {
                "loss_median": float(losses[feature].median()) if not losses.empty and losses[feature].notna().any() else None,
                "winner_median": float(wins[feature].median()) if not wins.empty and wins[feature].notna().any() else None,
                "loss_min": float(losses[feature].min()) if not losses.empty and losses[feature].notna().any() else None,
                "loss_max": float(losses[feature].max()) if not losses.empty and losses[feature].notna().any() else None,
            }
        out[dataset] = ds
    return out


def oracle_bound(metrics: Dict[str, Any], retention_floor: float) -> Dict[str, Any]:
    total_trades = int(metrics["trades"])
    total_contracts = int(metrics["contracts"])
    trade_wins = int(metrics["trade_wins"])
    contract_wins = int(metrics["contract_wins"])
    req_trades = int(math.ceil(total_trades * retention_floor))
    req_contracts = int(math.ceil(total_contracts * retention_floor))
    return {
        "retention_floor": retention_floor,
        "required_trades": req_trades,
        "required_contracts": req_contracts,
        "max_trade_accuracy": min(trade_wins, req_trades) / req_trades if req_trades else None,
        "max_contract_accuracy": min(contract_wins, req_contracts) / req_contracts if req_contracts else None,
    }


def top_rows(results: List[Dict[str, Any]], n: int = 10) -> List[Dict[str, Any]]:
    return results[: min(n, len(results))]


def write_report(
    path: Path,
    generated_utc: str,
    evaluations: Dict[str, Any],
    loss_summary: Dict[str, Any],
    candle_info: Dict[str, Any],
) -> None:
    lines: List[str] = []
    lines.append("# Physics Priors Boundary Model Search")
    lines.append("")
    lines.append(f"Generated UTC: `{generated_utc}`")
    lines.append("")
    lines.append("## Status")
    if any(evaluation["target_pass_count"] > 0 for evaluation in evaluations.values()):
        lines.append("OBSERVED PASS: at least one physics-prior rule met the configured gates in this exploratory scan.")
    else:
        lines.append("FAIL: no physics-prior rule met the 95% accuracy plus 75% volume gate with sample checks.")
    lines.append("")
    lines.append("This probe tests physics-first features, not another v28 threshold tune: signed spot-strike cushion, time-to-close scaling, v28 sigma, realized local volatility, and adverse short-term BTC drift.")
    lines.append("")
    lines.append("## Candle Coverage")
    for key, value in candle_info.items():
        lines.append(f"- {key}: {value}")
    lines.append("")

    for dataset, evaluation in evaluations.items():
        lines.append(f"## Dataset: `{dataset}`")
        lines.append("")
        lines.append(f"- Rows: {evaluation['row_count']}")
        lines.append(f"- Contracts: {evaluation['contract_count']}")
        lines.append(f"- Candidate rules scanned: {len(evaluation['results'])}")
        lines.append(f"- Observed-pass rules before sample floor: {evaluation['observed_pass_count']}")
        lines.append(f"- Target-pass rules: {evaluation['target_pass_count']}")
        lines.append("")
        lines.append("### Baseline")
        lines.append("")
        lines.append("| split | trades | trade acc | contracts | contract acc | contract retention |")
        lines.append("|---|---:|---:|---:|---:|---:|")
        for split in ["all", "train", "validation", "holdout"]:
            m = evaluation["baseline"][split]
            lines.append(
                f"| {split} | {m['trade_wins']}/{m['trades']} | {pct(m['trade_accuracy'])} | "
                f"{m['contract_wins']}/{m['contracts']} | {pct(m['contract_accuracy'])} | {pct(m['contract_retention'])} |"
            )
        lines.append("")
        holdout_oracle = oracle_bound(evaluation["baseline"]["holdout"], MIN_CONTRACT_RETENTION)
        lines.append(
            "Holdout oracle at 75% contract retention: "
            f"required contracts={holdout_oracle['required_contracts']}, "
            f"max contract accuracy={pct(holdout_oracle['max_contract_accuracy'])}."
        )
        lines.append("")
        lines.append("### Top Ranked Rules")
        lines.append("")
        lines.append("| rank | family | rule | all acc | all ret | val acc | holdout acc | holdout ret | contracts | target |")
        lines.append("|---:|---|---|---:|---:|---:|---:|---:|---:|---|")
        for idx, result in enumerate(top_rows(evaluation["results"]), start=1):
            all_m = result["metrics"]["all"]
            val_m = result["metrics"]["validation"]
            hold_m = result["metrics"]["holdout"]
            lines.append(
                f"| {idx} | {result['family']} | `{result['label']}` | "
                f"{pct(all_m['contract_accuracy'])} | {pct(all_m['contract_retention'])} | "
                f"{pct(val_m['contract_accuracy'])} | {pct(hold_m['contract_accuracy'])} | "
                f"{pct(hold_m['contract_retention'])} | {all_m['contracts']} | {result['target_pass']} |"
            )
        lines.append("")
        hv = [
            row
            for row in evaluation["results"]
            if (row["metrics"]["all"]["contract_retention"] or 0.0) >= MIN_CONTRACT_RETENTION
            and (row["metrics"]["holdout"]["contract_retention"] or 0.0) >= MIN_CONTRACT_RETENTION
        ][:10]
        lines.append("### Top High-Volume Rules")
        lines.append("")
        if not hv:
            lines.append("No scanned rule retained at least 75% of all and holdout contract volume.")
        else:
            lines.append("| rank | family | rule | all acc | all ret | holdout acc | holdout ret | contracts |")
            lines.append("|---:|---|---|---:|---:|---:|---:|---:|")
            for idx, result in enumerate(hv, start=1):
                all_m = result["metrics"]["all"]
                hold_m = result["metrics"]["holdout"]
                lines.append(
                    f"| {idx} | {result['family']} | `{result['label']}` | "
                    f"{pct(all_m['contract_accuracy'])} | {pct(all_m['contract_retention'])} | "
                    f"{pct(hold_m['contract_accuracy'])} | {pct(hold_m['contract_retention'])} | {all_m['contracts']} |"
                )
        lines.append("")

    lines.append("## Loss Physics Summary")
    lines.append("")
    for dataset, summary in loss_summary.items():
        lines.append(f"### `{dataset}`")
        lines.append("")
        lines.append(f"- Loss trades/contracts: {summary['loss_trades']} / {summary['loss_contracts']}")
        lines.append("| feature | loser median | winner median | loser range |")
        lines.append("|---|---:|---:|---:|")
        for feature, vals in summary["features"].items():
            lines.append(
                f"| {feature} | {fnum(vals['loss_median'])} | {fnum(vals['winner_median'])} | "
                f"{fnum(vals['loss_min'])} to {fnum(vals['loss_max'])} |"
            )
        lines.append("")

    lines.append("## Prompt-To-Artifact Checklist")
    lines.append("")
    lines.append("| requirement | evidence | result |")
    lines.append("|---|---|---|")
    lines.append("| Use live websocket data | Current ledger is rebuilt from `logs/live_mushroom_v28_size2/execution_events.ndjson`; supplemental ledger uses `live_90_70` live labels | done |")
    lines.append("| Focus on underlying physics | Rules test signed boundary distance, time scaling, v28 sigma, realized vol, and adverse BTC drift | done |")
    lines.append("| Question priors | v28 probability is not the only selector; zero-drift Brownian, realized-vol, and drift-conservative alternatives are tested | done |")
    lines.append("| >=95% realized accuracy | Candidate reports include all/validation/holdout trade and contract accuracy | not met unless target-pass count is positive |")
    lines.append("| Keep >=75%-80% volume | Candidate reports enforce >=75% trade and contract retention in all/validation/holdout | not met unless target-pass count is positive |")
    lines.append("| Not overfit | Chronological train/validation/holdout splits are reported; holdout is not hidden | exploratory, not promotion by itself |")
    lines.append("| Do not change bot logic/code | This probe and the live-v28 parser are standalone research artifacts; live bot files were not edited | done |")
    lines.append("")
    lines.append("## Conclusion")
    lines.append("")
    current = evaluations.get("current_v28_live_fills")
    if current and current["target_pass_count"] == 0:
        lines.append("The active goal is still not complete on current v28 live fills. The current holdout remains too loss-heavy for a 95% / 75% verified rule on that filled-trade sample.")
    else:
        lines.append("A current-v28 physics rule needs separate review before any promotion because this scan is exploratory.")
    replay = evaluations.get("live_90_70_replay")
    if replay and replay["target_pass_count"] > 0:
        lines.append("The supplemental live_90_70 replay did produce observed physics-prior passes; those are hypotheses for shadow testing, not proof of current-v28 success.")
    elif replay:
        lines.append("The supplemental live_90_70 replay did not produce a high-retention physics-prior pass in this rule family.")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--fetch-btc-candles", action="store_true")
    args = parser.parse_args()

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    current = load_current_v28()
    replay = load_replay_9070()
    combined = pd.concat([current, replay], ignore_index=True)
    combined = common_physics_features(combined)
    candles = load_coinbase_candles(combined, fetch_missing=bool(args.fetch_btc_candles))
    combined = add_candle_physics(combined, candles)

    datasets: Dict[str, pd.DataFrame] = {}
    for dataset, part in combined.groupby("dataset"):
        datasets[str(dataset)] = split_dataset(part)

    rules = make_rules()
    evaluations: Dict[str, Any] = {}
    for dataset, part in datasets.items():
        evaluations[dataset] = evaluate_dataset(part.drop(columns=["split"], errors="ignore"), rules)

    loss_summary = feature_loss_summary(combined)
    candle_info: Dict[str, Any]
    if candles.empty:
        candle_info = {"coinbase_cache": "missing"}
    else:
        candle_info = {
            "coinbase_cache": str(COINBASE_BTC_CACHE),
            "rows": int(len(candles)),
            "start": candles["close_dt"].min().isoformat(),
            "end": candles["close_dt"].max().isoformat(),
        }

    generated = utc_stamp()
    json_latest = OUT_DIR / "physics_priors_boundary_search_latest.json"
    json_stamp = OUT_DIR / f"physics_priors_boundary_search_{generated}.json"
    md_latest = OUT_DIR / "physics_priors_boundary_search_latest.md"
    md_stamp = OUT_DIR / f"physics_priors_boundary_search_{generated}.md"
    csv_latest = OUT_DIR / "physics_priors_boundary_candidates_latest.csv"
    csv_stamp = OUT_DIR / f"physics_priors_boundary_candidates_{generated}.csv"
    ledger_latest = OUT_DIR / "physics_priors_boundary_trades_latest.csv"
    ledger_stamp = OUT_DIR / f"physics_priors_boundary_trades_{generated}.csv"

    payload = {
        "generated_utc": generated,
        "inputs": {
            "current_ledger": str(CURRENT_LEDGER),
            "replay_ledger": str(REPLAY_LEDGER),
            "coinbase_btc_cache": str(COINBASE_BTC_CACHE),
        },
        "gate": {
            "min_target_accuracy": MIN_TARGET_ACCURACY,
            "min_contract_retention": MIN_CONTRACT_RETENTION,
            "min_trade_retention": MIN_TRADE_RETENTION,
            "min_all_selected_trades": MIN_ALL_SELECTED_TRADES,
            "min_holdout_selected_trades": MIN_HOLDOUT_SELECTED_TRADES,
            "min_all_selected_contracts": MIN_ALL_SELECTED_CONTRACTS,
            "min_holdout_selected_contracts": MIN_HOLDOUT_SELECTED_CONTRACTS,
        },
        "candle_info": candle_info,
        "evaluations": evaluations,
        "loss_summary": loss_summary,
    }
    for path in [json_latest, json_stamp]:
        path.write_text(json.dumps(clean_json(payload), indent=2, sort_keys=True), encoding="utf-8")
    write_candidates_csv(evaluations, csv_latest)
    write_candidates_csv(evaluations, csv_stamp)
    write_feature_ledger(combined, ledger_latest)
    write_feature_ledger(combined, ledger_stamp)
    write_report(md_latest, generated, evaluations, loss_summary, candle_info)
    write_report(md_stamp, generated, evaluations, loss_summary, candle_info)

    print("Physics priors boundary model search complete")
    print(f"datasets={','.join(sorted(evaluations))}")
    for dataset, evaluation in evaluations.items():
        print(
            f"{dataset}: rows={evaluation['row_count']} contracts={evaluation['contract_count']} "
            f"observed_pass={evaluation['observed_pass_count']} target_pass={evaluation['target_pass_count']}"
        )
    print(f"report={md_latest}")
    print(f"candidates={csv_latest}")
    print(f"ledger={ledger_latest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
