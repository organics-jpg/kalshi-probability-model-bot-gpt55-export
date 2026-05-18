"""Cross-dataset validation for fixed physics-prior BTC15M rules.

This is research-only. It tests a small set of rules discovered from the
physics-prior scan against other resolved live ledgers. It is intentionally not
a broad search: the point is to reduce overfit risk by checking whether the
same physics survives outside the live_90_70 discovery tape.
"""
from __future__ import annotations

import argparse
import csv
import json
import math
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional
from zoneinfo import ZoneInfo

import numpy as np
import pandas as pd

from probe_live_9070_v28_replay import (
    COINBASE_BTC_CACHE,
    METADATA_CACHE,
    fetch_coinbase_btc_1m,
    fetch_market_metadata,
    load_json,
    write_json,
)
from btc_mushroom_forecaster_v28_fast import FastMushroomFVEngineV28, FastMushroomV28Config


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
STATS_DIR = ROOT / "stats"

LOCAL_TZ = ZoneInfo("America/New_York")

DISCOVERY_DATASET = "live_90_70"
VALIDATION_DATASETS = [
    "entry_90_stop_78",
    "live_90_78",
    "live_87_77_67",
    "live_90_truffle_exit_size2",
    "live_liquidity_dwell_size2",
]

FIXED_RULES = [
    {
        "rule_id": "adverse15_gt10_v28_cushion_0p5",
        "family": "adverse_drift_guard",
        "label": "ask<=100; block 15m adverse>10 unless v28 cushion>0.5",
        "ask_max": 100.0,
        "lag": 15,
        "adverse_min": 10.0,
        "cushion_feature": "margin_per_v28_sigma",
        "cushion_min": 0.5,
    },
    {
        "rule_id": "adverse15_gt10_v28_cushion_0p75",
        "family": "adverse_drift_guard",
        "label": "ask<=100; block 15m adverse>10 unless v28 cushion>0.75",
        "ask_max": 100.0,
        "lag": 15,
        "adverse_min": 10.0,
        "cushion_feature": "margin_per_v28_sigma",
        "cushion_min": 0.75,
    },
    {
        "rule_id": "adverse15_gt10_v28_cushion_1p0",
        "family": "adverse_drift_guard",
        "label": "ask<=100; block 15m adverse>10 unless v28 cushion>1.0",
        "ask_max": 100.0,
        "lag": 15,
        "adverse_min": 10.0,
        "cushion_feature": "margin_per_v28_sigma",
        "cushion_min": 1.0,
    },
    {
        "rule_id": "rv30_cushion_0p5",
        "family": "realized_vol_cushion",
        "label": "ask<=100; margin/rv30>=0.5",
        "ask_max": 100.0,
        "feature": "margin_per_rv_sigma_30m",
        "min": 0.5,
    },
    {
        "rule_id": "rv60_cushion_0p5",
        "family": "realized_vol_cushion",
        "label": "ask<=100; margin/rv60>=0.5",
        "ask_max": 100.0,
        "feature": "margin_per_rv_sigma_60m",
        "min": 0.5,
    },
    {
        "rule_id": "rv15_cushion_0p5",
        "family": "realized_vol_cushion",
        "label": "ask<=100; margin/rv15>=0.5",
        "ask_max": 100.0,
        "feature": "margin_per_rv_sigma_15m",
        "min": 0.5,
    },
    {
        "rule_id": "rv15_brownian_p_0p7",
        "family": "brownian_realized_vol",
        "label": "ask<=100; Phi(margin/rv15)>=0.7",
        "ask_max": 100.0,
        "feature": "brownian_p_rv_15m",
        "min": 0.7,
    },
    {
        "rule_id": "rv30_brownian_p_0p7",
        "family": "brownian_realized_vol",
        "label": "ask<=100; Phi(margin/rv30)>=0.7",
        "ask_max": 100.0,
        "feature": "brownian_p_rv_30m",
        "min": 0.7,
    },
]


def normal_cdf_np(z: np.ndarray | pd.Series | float) -> np.ndarray:
    arr = np.asarray(z, dtype=float)
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
    if isinstance(value, pd.Timestamp):
        return value.isoformat()
    return value


def pct(value: Optional[float]) -> str:
    if value is None or not math.isfinite(float(value)):
        return "NA"
    return f"{100.0 * float(value):.2f}%"


def fnum(value: Optional[float], digits: int = 3) -> str:
    if value is None or not math.isfinite(float(value)):
        return "NA"
    return f"{float(value):.{digits}f}"


def parse_local_entry_ts(series: pd.Series) -> pd.Series:
    raw = pd.to_datetime(series, errors="coerce")
    localized = raw.dt.tz_localize(LOCAL_TZ, ambiguous="NaT", nonexistent="NaT")
    return localized.dt.tz_convert("UTC")


def load_stats_dataset(dataset: str) -> pd.DataFrame:
    path = STATS_DIR / dataset / "trades.csv"
    if not path.exists() or path.stat().st_size == 0:
        return pd.DataFrame()
    df = pd.read_csv(path)
    if df.empty:
        return df
    market_result = df.get("market_result")
    if market_result is None:
        return pd.DataFrame()
    out = pd.DataFrame(
        {
            "dataset": dataset,
            "entry_dt": parse_local_entry_ts(df["entry_ts"]),
            "market": df["market"].astype(str),
            "side": df["side"].astype(str).str.lower(),
            "outcome": market_result.astype(str).str.lower(),
            "win": df["outcome"].astype(str).str.lower().eq("win"),
            "qty": pd.to_numeric(df["qty"], errors="coerce"),
            "ask_cents": pd.to_numeric(df["entry_fill_cents_used"], errors="coerce"),
            "stats_btc_close": pd.to_numeric(df.get("btc_close"), errors="coerce"),
            "source_file": str(path),
        }
    )
    out = out[out["outcome"].isin(["yes", "no"])].copy()
    out = out[out["side"].isin(["yes", "no"])].copy()
    out = out[out["qty"] > 0].copy()
    out = out.dropna(subset=["entry_dt", "ask_cents"])
    return out


def load_market_results(dataset: str) -> Dict[str, Any]:
    path = STATS_DIR / dataset / "market_results.csv"
    if not path.exists() or path.stat().st_size == 0:
        return {}
    df = pd.read_csv(path)
    if df.empty or "market" not in df.columns:
        return {}
    df = df[df["market"].astype(str).str.startswith("KXBTC15M-", na=False)].copy()
    if "close_time" in df.columns:
        df["close_dt"] = pd.to_datetime(df["close_time"], utc=True, errors="coerce")
    else:
        df["close_dt"] = pd.NaT
    return {str(row["market"]): row.to_dict() for _, row in df.iterrows()}


def ensure_metadata(markets: List[str], fetch_missing: bool) -> Dict[str, Any]:
    cache = load_json(METADATA_CACHE)
    changed = False
    for market in sorted(set(markets)):
        current = cache.get(market) or {}
        if current.get("floor_strike") is not None:
            continue
        if fetch_missing:
            cache[market] = fetch_market_metadata(market)
            changed = True
    if changed:
        write_json(METADATA_CACHE, cache)
    return cache


def load_or_fetch_candles(entries: pd.DataFrame, fetch_missing: bool) -> pd.DataFrame:
    frames: List[pd.DataFrame] = []
    if COINBASE_BTC_CACHE.exists():
        frames.append(pd.read_parquet(COINBASE_BTC_CACHE))
    if fetch_missing and not entries.empty:
        start = entries["entry_dt"].min() - pd.Timedelta(hours=2)
        end = entries["entry_dt"].max() + pd.Timedelta(minutes=5)
        existing = pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()
        missing_fetch = True
        if not existing.empty and "close_dt" in existing.columns:
            existing["close_dt"] = pd.to_datetime(existing["close_dt"], utc=True, errors="coerce")
            covered_start = existing["close_dt"].min()
            covered_end = existing["close_dt"].max()
            missing_fetch = bool(pd.isna(covered_start) or pd.isna(covered_end) or covered_start > start or covered_end < end)
        if missing_fetch:
            fetched = fetch_coinbase_btc_1m(start, end)
            if not fetched.empty:
                frames.append(fetched)
                cache_df = pd.concat(frames, ignore_index=True)
                cache_df["close_dt"] = pd.to_datetime(cache_df["close_dt"], utc=True, errors="coerce")
                cache_df = cache_df.dropna(subset=["close_dt", "open", "high", "low", "close"])
                cache_df = cache_df.sort_values("close_dt").drop_duplicates("close_dt", keep="last").reset_index(drop=True)
                cache_df.to_parquet(COINBASE_BTC_CACHE, index=False)
                return prepare_candles(cache_df)
    if not frames:
        return pd.DataFrame()
    return prepare_candles(pd.concat(frames, ignore_index=True))


def prepare_candles(candles: pd.DataFrame) -> pd.DataFrame:
    if candles.empty:
        return candles
    candles = candles.copy()
    candles["close_dt"] = pd.to_datetime(candles["close_dt"], utc=True, errors="coerce")
    for col in ["open", "high", "low", "close"]:
        candles[col] = pd.to_numeric(candles[col], errors="coerce")
    candles = candles.dropna(subset=["close_dt", "open", "high", "low", "close"])
    candles = candles.sort_values("close_dt").drop_duplicates("close_dt", keep="last").reset_index(drop=True)
    candles["log_ret"] = np.log(candles["close"] / candles["close"].shift(1))
    for window in [15, 30, 60]:
        candles[f"sigma_min_log_{window}m"] = candles["log_ret"].rolling(window).std() * candles["close"]
    return candles


def asof_values(candles: pd.DataFrame, target_dt: pd.Series, column: str, max_age_seconds: float) -> np.ndarray:
    if candles.empty or column not in candles.columns:
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
    positions = np.where(valid)[0][fresh]
    if len(positions):
        values[positions] = candles[column].to_numpy()[idx[positions]]
    return values


def build_feature_rows(entries: pd.DataFrame, metadata: Dict[str, Any], market_results: Dict[str, Dict[str, Any]], candles: pd.DataFrame) -> tuple[pd.DataFrame, Dict[str, int]]:
    skipped = {
        "missing_metadata": 0,
        "missing_strike": 0,
        "missing_close": 0,
        "missing_spot": 0,
        "missing_horizon": 0,
    }
    rows: List[Dict[str, Any]] = []
    if entries.empty:
        return pd.DataFrame(), skipped
    spot = asof_values(candles, entries["entry_dt"], "close", 120.0)
    entries = entries.copy()
    entries["spot"] = np.where(np.isfinite(spot), spot, entries["stats_btc_close"])
    for _, row in entries.iterrows():
        market = str(row["market"])
        meta = metadata.get(market) or {}
        if not meta:
            skipped["missing_metadata"] += 1
            continue
        strike = meta.get("floor_strike")
        if strike is None:
            skipped["missing_strike"] += 1
            continue
        close_time = meta.get("close_time")
        if close_time is None and market in market_results:
            close_time = market_results[market].get("close_time")
        close_dt = pd.to_datetime(close_time, utc=True, errors="coerce")
        if pd.isna(close_dt):
            skipped["missing_close"] += 1
            continue
        entry_dt = pd.Timestamp(row["entry_dt"])
        seconds_to_close = (close_dt - entry_dt).total_seconds()
        if not math.isfinite(seconds_to_close) or seconds_to_close <= 0:
            skipped["missing_horizon"] += 1
            continue
        row_spot = float(row["spot"]) if pd.notna(row["spot"]) else math.nan
        if not math.isfinite(row_spot):
            skipped["missing_spot"] += 1
            continue
        side_sign = 1.0 if str(row["side"]).lower() == "yes" else -1.0
        margin = side_sign * (row_spot - float(strike))
        rows.append(
            {
                "dataset": row["dataset"],
                "entry_dt": entry_dt,
                "market": market,
                "side": row["side"],
                "outcome": row["outcome"],
                "win": bool(row["win"]),
                "qty": int(row["qty"]),
                "ask_cents": float(row["ask_cents"]),
                "spot": row_spot,
                "strike": float(strike),
                "close_dt": close_dt,
                "seconds_to_close": float(seconds_to_close),
                "side_sign": side_sign,
                "margin_dollars": float(margin),
                "source_file": row["source_file"],
            }
        )
    out = pd.DataFrame(rows)
    if out.empty:
        return out, skipped
    for window in [15, 30, 60]:
        sigma_min = asof_values(candles, out["entry_dt"], f"sigma_min_log_{window}m", 120.0)
        out[f"rv_sigma_t_{window}m"] = sigma_min * np.sqrt(out["seconds_to_close"] / 60.0)
        out[f"margin_per_rv_sigma_{window}m"] = out["margin_dollars"] / out[f"rv_sigma_t_{window}m"]
        out[f"brownian_p_rv_{window}m"] = normal_cdf_np(out[f"margin_per_rv_sigma_{window}m"])
    return out.sort_values(["dataset", "entry_dt", "market"]).reset_index(drop=True), skipped


def add_v28_and_drift_features(features: pd.DataFrame, candles: pd.DataFrame) -> pd.DataFrame:
    if features.empty:
        return features
    out = features.sort_values("entry_dt").reset_index(drop=True).copy()
    for lag in [3, 5, 10, 15]:
        lag_dt = out["entry_dt"] - pd.to_timedelta(lag, unit="min")
        lag_close = asof_values(candles, lag_dt, "close", 120.0)
        move = out["spot"] - lag_close
        out[f"signed_move_{lag}m"] = out["side_sign"] * move
        out[f"adverse_move_{lag}m"] = np.maximum(-out[f"signed_move_{lag}m"], 0.0)

    out["v28_sigma_t_dollars"] = np.nan
    out["v28_p_side"] = np.nan
    out["margin_per_v28_sigma"] = np.nan
    out["brownian_p_v28_sigma"] = np.nan
    if candles.empty:
        return out

    engine = FastMushroomFVEngineV28(FastMushroomV28Config())
    bar_index = 0
    candles = candles.sort_values("close_dt").reset_index(drop=True)
    for idx, row in out.iterrows():
        entry_dt = pd.Timestamp(row["entry_dt"])
        while bar_index < len(candles) and candles.iloc[bar_index]["close_dt"] <= entry_dt:
            bar = candles.iloc[bar_index]
            engine.update_bar(
                open=float(bar["open"]),
                high=float(bar["high"]),
                low=float(bar["low"]),
                close=float(bar["close"]),
                volume=float(bar.get("volume", 0.0) or 0.0),
                ts=bar["close_dt"].to_pydatetime(),
            )
            bar_index += 1
        if not engine.ready():
            continue
        try:
            pred = engine.predict_many(strikes=[float(row["strike"])], horizon_seconds=float(row["seconds_to_close"]))
        except Exception:
            continue
        sigma = float(pred.sigma_t_dollars)
        p_yes = float(pred.p_yes[0])
        p_side = p_yes if str(row["side"]).lower() == "yes" else 1.0 - p_yes
        out.at[idx, "v28_sigma_t_dollars"] = sigma
        out.at[idx, "v28_p_side"] = p_side
        if sigma > 0:
            z = float(row["margin_dollars"]) / sigma
            out.at[idx, "margin_per_v28_sigma"] = z
            out.at[idx, "brownian_p_v28_sigma"] = float(normal_cdf_np(z)[()])
    return out


def apply_rule(df: pd.DataFrame, rule: Dict[str, Any]) -> pd.Series:
    if df.empty:
        return pd.Series(dtype=bool)
    mask = df["ask_cents"].notna() & (df["ask_cents"] <= float(rule["ask_max"]))
    if rule["family"] == "adverse_drift_guard":
        lag = int(rule["lag"])
        adverse_feature = f"adverse_move_{lag}m"
        cushion_feature = str(rule["cushion_feature"])
        if adverse_feature not in df.columns or cushion_feature not in df.columns:
            return pd.Series(False, index=df.index)
        adverse = df[adverse_feature].fillna(np.inf)
        cushion = df[cushion_feature].fillna(-np.inf)
        blocked = (adverse >= float(rule["adverse_min"])) & (cushion <= float(rule["cushion_min"]))
        return (mask & ~blocked).fillna(False)
    feature = str(rule["feature"])
    if feature not in df.columns:
        return pd.Series(False, index=df.index)
    mask &= df[feature].notna() & (df[feature] >= float(rule["min"]))
    return mask.fillna(False)


def metrics(df: pd.DataFrame, mask: Optional[pd.Series] = None) -> Dict[str, Any]:
    if mask is None:
        selected = df
    else:
        selected = df[mask.reindex(df.index).fillna(False)]
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
        "total_trades": total_trades,
        "total_contracts": total_contracts,
    }


def evaluate(features: pd.DataFrame) -> Dict[str, Any]:
    groups: Dict[str, pd.DataFrame] = {name: part for name, part in features.groupby("dataset")}
    independent = features[features["dataset"] != DISCOVERY_DATASET].copy()
    if not independent.empty:
        groups["pooled_independent_ex_live_90_70"] = independent
    all_sets = dict(groups)
    all_sets["pooled_all"] = features

    evaluations: Dict[str, Any] = {}
    for name, part in all_sets.items():
        base = metrics(part)
        rules: List[Dict[str, Any]] = []
        for rule in FIXED_RULES:
            m = metrics(part, apply_rule(part, rule))
            rules.append({"rule": rule, "metrics": m})
        evaluations[name] = {"baseline": base, "rules": rules}
    return evaluations


def flatten_evaluations(evaluations: Dict[str, Any]) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    for dataset, evaluation in evaluations.items():
        base = evaluation["baseline"]
        rows.append({"dataset": dataset, "rule_id": "baseline", "family": "baseline", "label": "all resolved trades", **base})
        for item in evaluation["rules"]:
            rule = item["rule"]
            rows.append({"dataset": dataset, "rule_id": rule["rule_id"], "family": rule["family"], "label": rule["label"], **item["metrics"]})
    return rows


def write_csv(rows: List[Dict[str, Any]], path: Path) -> None:
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    fields = sorted({key for row in rows for key in row})
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def write_report(
    path: Path,
    generated: str,
    features: pd.DataFrame,
    evaluations: Dict[str, Any],
    skipped: Dict[str, Dict[str, int]],
    metadata_missing_after: int,
    candle_info: Dict[str, Any],
) -> None:
    lines: List[str] = []
    lines.append("# Physics Cross-Dataset Validation")
    lines.append("")
    lines.append(f"Generated UTC: `{generated}`")
    lines.append("")
    lines.append("## Scope")
    lines.append("")
    lines.append("- Fixed rules are taken from the `live_90_70` physics-prior scan; this script does not run a broad rule search.")
    lines.append("- Independent validation excludes `live_90_70` from the pooled independent view.")
    lines.append("- Only resolved settlement rows are included; exited-before-settlement rows are excluded.")
    lines.append("")
    lines.append("## Coverage")
    lines.append("")
    lines.append(f"- Feature rows: {len(features)}")
    lines.append(f"- Contracts: {int(features['qty'].sum()) if not features.empty else 0}")
    lines.append(f"- Metadata missing after load/fetch: {metadata_missing_after}")
    for key, value in candle_info.items():
        lines.append(f"- {key}: {value}")
    lines.append("")
    lines.append("### Skips")
    lines.append("")
    lines.append("| dataset | missing metadata | missing strike | missing close | missing spot | missing horizon |")
    lines.append("|---|---:|---:|---:|---:|---:|")
    for dataset, counts in skipped.items():
        lines.append(
            f"| {dataset} | {counts.get('missing_metadata', 0)} | {counts.get('missing_strike', 0)} | "
            f"{counts.get('missing_close', 0)} | {counts.get('missing_spot', 0)} | {counts.get('missing_horizon', 0)} |"
        )
    lines.append("")
    lines.append("## Results")
    lines.append("")
    for dataset, evaluation in evaluations.items():
        lines.append(f"### `{dataset}`")
        lines.append("")
        base = evaluation["baseline"]
        lines.append(
            f"Baseline: {base['contract_wins']}/{base['contracts']} contracts "
            f"({pct(base['contract_accuracy'])}), trades {base['trade_wins']}/{base['trades']} ({pct(base['trade_accuracy'])})."
        )
        lines.append("")
        lines.append("| rule | contracts | contract acc | contract ret | trades | trade acc |")
        lines.append("|---|---:|---:|---:|---:|---:|")
        for item in evaluation["rules"]:
            rule = item["rule"]
            m = item["metrics"]
            lines.append(
                f"| `{rule['label']}` | {m['contracts']} | {pct(m['contract_accuracy'])} | "
                f"{pct(m['contract_retention'])} | {m['trades']} | {pct(m['trade_accuracy'])} |"
            )
        lines.append("")
    lines.append("## Completion Read")
    lines.append("")
    independent = evaluations.get("pooled_independent_ex_live_90_70")
    if independent:
        best = max(
            independent["rules"],
            key=lambda item: (
                item["metrics"]["contract_accuracy"] or 0.0,
                item["metrics"]["contract_retention"] or 0.0,
            ),
        )
        m = best["metrics"]
        if (
            (m["contract_accuracy"] or 0.0) >= 0.95
            and (m["trade_accuracy"] or 0.0) >= 0.95
            and (m["contract_retention"] or 0.0) >= 0.75
            and (m["trade_retention"] or 0.0) >= 0.75
            and m["contracts"] >= 150
            and m["trades"] >= 75
        ):
            lines.append("The pooled independent set supports a fixed physics rule at the requested accuracy/volume/sample gates.")
        else:
            lines.append("The pooled independent set does not yet support a fixed physics rule at the requested accuracy/volume/sample gates.")
    else:
        lines.append("No independent validation set was available after skips.")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--fetch-metadata", action="store_true")
    parser.add_argument("--fetch-btc-candles", action="store_true")
    args = parser.parse_args()

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    datasets = [DISCOVERY_DATASET, *VALIDATION_DATASETS]
    loaded = [load_stats_dataset(dataset) for dataset in datasets]
    entries = pd.concat([df for df in loaded if not df.empty], ignore_index=True)
    if entries.empty:
        raise SystemExit("No resolved stats entries found.")

    metadata = ensure_metadata(entries["market"].astype(str).tolist(), fetch_missing=bool(args.fetch_metadata))
    market_results_by_dataset = {dataset: load_market_results(dataset) for dataset in datasets}
    candles = load_or_fetch_candles(entries, fetch_missing=bool(args.fetch_btc_candles))

    feature_frames: List[pd.DataFrame] = []
    skipped: Dict[str, Dict[str, int]] = {}
    for dataset in datasets:
        part = entries[entries["dataset"] == dataset]
        features, counts = build_feature_rows(part, metadata, market_results_by_dataset.get(dataset, {}), candles)
        skipped[dataset] = counts
        if not features.empty:
            feature_frames.append(features)
    features = pd.concat(feature_frames, ignore_index=True) if feature_frames else pd.DataFrame()
    if features.empty:
        raise SystemExit("No feature rows after metadata/candle joins.")
    features = add_v28_and_drift_features(features, candles)

    evaluations = evaluate(features)
    generated = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%SZ")
    metadata_missing_after = int(sum(1 for m in entries["market"].astype(str).unique() if (metadata.get(m) or {}).get("floor_strike") is None))
    candle_info = (
        {"coinbase_cache": "missing"}
        if candles.empty
        else {
            "coinbase_cache": str(COINBASE_BTC_CACHE),
            "candle_rows": int(len(candles)),
            "candle_start": candles["close_dt"].min().isoformat(),
            "candle_end": candles["close_dt"].max().isoformat(),
        }
    )

    payload = {
        "generated_utc": generated,
        "discovery_dataset": DISCOVERY_DATASET,
        "validation_datasets": VALIDATION_DATASETS,
        "fixed_rules": FIXED_RULES,
        "metadata_missing_after": metadata_missing_after,
        "candle_info": candle_info,
        "skipped": skipped,
        "evaluations": evaluations,
    }

    json_latest = OUT_DIR / "physics_cross_dataset_validation_latest.json"
    json_stamp = OUT_DIR / f"physics_cross_dataset_validation_{generated}.json"
    md_latest = OUT_DIR / "physics_cross_dataset_validation_latest.md"
    md_stamp = OUT_DIR / f"physics_cross_dataset_validation_{generated}.md"
    csv_latest = OUT_DIR / "physics_cross_dataset_validation_candidates_latest.csv"
    csv_stamp = OUT_DIR / f"physics_cross_dataset_validation_candidates_{generated}.csv"
    ledger_latest = OUT_DIR / "physics_cross_dataset_validation_trades_latest.csv"
    ledger_stamp = OUT_DIR / f"physics_cross_dataset_validation_trades_{generated}.csv"

    for path in [json_latest, json_stamp]:
        path.write_text(json.dumps(clean_json(payload), indent=2, sort_keys=True), encoding="utf-8")
    rows = flatten_evaluations(evaluations)
    write_csv(rows, csv_latest)
    write_csv(rows, csv_stamp)
    features.to_csv(ledger_latest, index=False)
    features.to_csv(ledger_stamp, index=False)
    write_report(md_latest, generated, features, evaluations, skipped, metadata_missing_after, candle_info)
    write_report(md_stamp, generated, features, evaluations, skipped, metadata_missing_after, candle_info)

    print("Physics cross-dataset validation complete")
    print(f"feature_rows={len(features)} contracts={int(features['qty'].sum())}")
    print(f"metadata_missing_after={metadata_missing_after}")
    for name, evaluation in evaluations.items():
        base = evaluation["baseline"]
        print(f"{name}: baseline_contract_acc={base['contract_accuracy']} contracts={base['contracts']}")
    print(f"report={md_latest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
