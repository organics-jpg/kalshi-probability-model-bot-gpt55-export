"""Compare standard, log-spaced, and phi-spaced BTC lookback features.

Research-only. This probe tests whether geometric/Fibonacci "phi-frame"
lookbacks add forward-stable signal to the current v28 probability lane.

It does not change live bot logic, state, config, or orders. It uses filled
historical rows only, so PnL numbers are replay projections rather than a live
tradable denominator.
"""
from __future__ import annotations

import argparse
import json
import math
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from statistics import mean, median, stdev
from typing import Any

import numpy as np
import pandas as pd
from scipy.optimize import minimize
from scipy.special import expit, logit

import probe_arxiv_strategy_priority_tests as priority
import probe_arxiv_strategy_remaining_ideas as remaining
import probe_self_calibrating_aci_pnl_projection as aci_projection
from probe_live_9070_v28_replay import fetch_coinbase_btc_1m


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
BTC_CACHE = OUT_DIR / "coinbase_btc_usd_1m_cache.parquet"
OUT_JSON = OUT_DIR / "phi_frame_feature_comparison_latest.json"
OUT_MD = OUT_DIR / "phi_frame_feature_comparison_latest.md"
OUT_SUMMARY_CSV = OUT_DIR / "phi_frame_feature_comparison_summary_latest.csv"

EPS = 1e-6
L2_REG = 1.0
THRESHOLDS = tuple(round(x, 2) for x in np.arange(0.50, 0.91, 0.02))
WFA_SPLITS = (
    {"name": "wfa_201_270", "train": (1, 200), "test": (201, 270)},
    {"name": "wfa_271_340", "train": (71, 270), "test": (271, 340)},
    {"name": "wfa_341_410", "train": (141, 340), "test": (341, 410)},
    {"name": "wfa_411_end", "train": (211, 410), "test": (411, None)},
)

FRAME_FAMILIES = {
    "base_only": (),
    "standard_3": (1, 5, 15),
    "log_3": (1, 4, 16),
    "phi_3": (1, 3, 8),
    "standard_6": (1, 2, 3, 5, 10, 15),
    "log_6": (1, 2, 4, 8, 16, 32),
    "phi_6": (1, 2, 3, 5, 8, 13),
    # Minute-bar approximation of the user's 1s..610s Fibonacci ladder.
    "phi_seconds_rounded": (1, 2, 3, 5, 8, 10),
    # Minute-bar approximation of 15s,24s,...,699s.
    "phi_15s_seed_rounded": (1, 2, 3, 4, 5, 7, 12),
}

BASE_FEATURES = (
    "logit_p_calibrated",
    "logit_brownian_terminal",
    "edge28_10c",
    "log_depth_ratio",
    "ask_cents_100",
    "seconds_to_close_900",
    "abs_d_sigma",
)


def fnum(value: Any, default: float = 0.0) -> float:
    parsed = priority.maybe_float(value)
    return default if parsed is None else float(parsed)


def clamp(value: float, low: float = EPS, high: float = 1.0 - EPS) -> float:
    return min(high, max(low, float(value)))


def log_loss_np(y: np.ndarray, p: np.ndarray) -> float:
    p = np.clip(p, EPS, 1.0 - EPS)
    return float(np.mean(-(y * np.log(p) + (1.0 - y) * np.log(1.0 - p))))


def brier_np(y: np.ndarray, p: np.ndarray) -> float:
    return float(np.mean((p - y) ** 2))


def auc_np(y: np.ndarray, p: np.ndarray) -> float | None:
    return priority.auc_score([int(v) for v in y.tolist()], [float(v) for v in p.tolist()])


def safe_cv(values: list[float]) -> float | None:
    positives = [v for v in values if math.isfinite(v)]
    if len(positives) < 2:
        return None
    avg = mean(positives)
    if abs(avg) < 1e-9:
        return None
    return abs(stdev(positives) / avg)


def row_window(rows: list[dict[str, Any]], start: int, end: int | None) -> list[dict[str, Any]]:
    out = []
    for idx, row in enumerate(rows, start=1):
        if idx < start:
            continue
        if end is not None and idx > end:
            continue
        out.append(row)
    return out


def recompute_candle_returns(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["open_dt"] = pd.to_datetime(df["open_dt"], utc=True, errors="coerce")
    df["close_dt"] = pd.to_datetime(df["close_dt"], utc=True, errors="coerce")
    df = df.dropna(subset=["open_dt", "close_dt", "open", "high", "low", "close"])
    df = df.sort_values("close_dt").drop_duplicates("close_dt", keep="last").reset_index(drop=True)
    df["prev_close"] = df["close"].shift(1)
    df["log_ret"] = np.log(df["close"].astype(float) / df["prev_close"].astype(float))
    df["dollar_ret"] = df["close"].astype(float) - df["prev_close"].astype(float)
    return df


def load_candles(rows: list[dict[str, Any]], *, fetch_missing: bool) -> tuple[pd.DataFrame, dict[str, Any]]:
    frames: list[pd.DataFrame] = []
    if BTC_CACHE.exists():
        frames.append(pd.read_parquet(BTC_CACHE))

    entry_times = [remaining.row_entry_utc(row) for row in rows]
    entry_times = [dt for dt in entry_times if dt is not None]
    fetch_stats: dict[str, Any] = {"fetch_missing": fetch_missing, "fetched_rows": 0}
    if fetch_missing and entry_times:
        start = pd.Timestamp(min(entry_times)).tz_convert("UTC") - pd.Timedelta(hours=12)
        end = pd.Timestamp(max(entry_times)).tz_convert("UTC") + pd.Timedelta(minutes=2)
        fetched = fetch_coinbase_btc_1m(start, end)
        fetch_stats["fetched_rows"] = int(len(fetched))
        if not fetched.empty:
            frames.append(fetched)

    if not frames:
        raise FileNotFoundError(BTC_CACHE)

    df = recompute_candle_returns(pd.concat(frames, ignore_index=True))
    if fetch_missing and not df.empty:
        OUT_DIR.mkdir(parents=True, exist_ok=True)
        df.to_parquet(BTC_CACHE, index=False)

    fetch_stats.update(
        {
            "cache_path": str(BTC_CACHE),
            "candle_rows": int(len(df)),
            "candle_min_utc": str(df["open_dt"].min()) if len(df) else None,
            "candle_max_utc": str(df["open_dt"].max()) if len(df) else None,
        }
    )
    return df, fetch_stats


def asof_close(candles: pd.DataFrame, ts: pd.Timestamp) -> dict[str, float] | None:
    idx = candles["close_dt"].searchsorted(ts, side="right") - 1
    if idx < 0:
        return None
    row = candles.iloc[int(idx)]
    return {
        "close": float(row["close"]),
        "high": float(row["high"]),
        "low": float(row["low"]),
        "open_dt_ns": int(pd.Timestamp(row["open_dt"]).value),
        "close_dt_ns": int(pd.Timestamp(row["close_dt"]).value),
    }


def candle_slice(candles: pd.DataFrame, start: pd.Timestamp, end: pd.Timestamp) -> pd.DataFrame:
    start_idx = candles["close_dt"].searchsorted(start, side="right")
    end_idx = candles["close_dt"].searchsorted(end, side="right")
    return candles.iloc[int(start_idx) : int(end_idx)]


def add_base_features(row: dict[str, Any]) -> None:
    p_cal = clamp(fnum(row.get("p_calibrated"), 0.5))
    p_brownian = clamp(fnum(row.get("brownian_terminal_p_side"), 0.5))
    row["logit_p_calibrated"] = float(logit(p_cal))
    row["logit_brownian_terminal"] = float(logit(p_brownian))
    row["edge28_10c"] = fnum(row.get("edge28_cents")) / 10.0
    row["log_depth_ratio"] = math.log1p(max(0.0, fnum(row.get("depth_ratio"))))
    row["ask_cents_100"] = fnum(row.get("ask_cents")) / 100.0
    row["seconds_to_close_900"] = fnum(row.get("seconds_to_close")) / 900.0
    row["abs_d_sigma"] = fnum(row.get("abs_d_sigma"))


def add_frame_features(row: dict[str, Any], candles: pd.DataFrame, max_lookback_minutes: int) -> bool:
    entry_dt = remaining.row_entry_utc(row)
    if entry_dt is None:
        return False
    entry_ts = pd.Timestamp(entry_dt)
    current = fnum(row.get("btc_price"))
    if current <= 0:
        current_candle = asof_close(candles, entry_ts)
        if current_candle is None:
            return False
        current = current_candle["close"]

    side = str(row.get("side") or "").lower()
    side_sign = 1.0 if side == "yes" else -1.0 if side == "no" else 0.0
    if side_sign == 0.0:
        return False

    warmup_start = entry_ts - pd.Timedelta(minutes=max_lookback_minutes + 3)
    if candles["close_dt"].iloc[0] > warmup_start:
        return False

    for minutes in sorted({m for frames in FRAME_FAMILIES.values() for m in frames}):
        past = asof_close(candles, entry_ts - pd.Timedelta(minutes=int(minutes)))
        if past is None or past["close"] <= 0:
            return False
        window = candle_slice(candles, entry_ts - pd.Timedelta(minutes=int(minutes)), entry_ts)
        if len(window) < max(1, int(minutes) - 1):
            return False
        log_move = math.log(current / past["close"])
        dollar_move = current - past["close"]
        returns = window["log_ret"].dropna().astype(float)
        sigma = float(returns.std()) if len(returns) >= 2 else 0.0
        sigma_scaled = max(1e-8, sigma * math.sqrt(max(1.0, float(minutes))))
        high = float(max(window["high"].max(), current))
        low = float(min(window["low"].min(), current))
        key = f"{minutes}m"
        row[f"frame_{key}_side_ret_z"] = side_sign * log_move / sigma_scaled
        row[f"frame_{key}_abs_ret_z"] = abs(log_move) / sigma_scaled
        row[f"frame_{key}_range_pct"] = (high - low) / current
        row[f"frame_{key}_side_dollar"] = side_sign * dollar_move
    return True


def feature_names_for_family(family: str) -> list[str]:
    names = list(BASE_FEATURES)
    for minutes in FRAME_FAMILIES[family]:
        key = f"{minutes}m"
        names.extend(
            [
                f"frame_{key}_side_ret_z",
                f"frame_{key}_abs_ret_z",
                f"frame_{key}_range_pct",
                f"frame_{key}_side_dollar",
            ]
        )
    return names


@dataclass
class RidgeLogitModel:
    feature_names: list[str]
    means: np.ndarray
    stds: np.ndarray
    weights: np.ndarray
    train_nll: float
    success: bool

    def predict(self, rows: list[dict[str, Any]]) -> np.ndarray:
        x = make_matrix(rows, self.feature_names)
        z = (x - self.means) / self.stds
        x_aug = np.column_stack([np.ones(len(z)), z])
        return np.clip(expit(x_aug @ self.weights), EPS, 1.0 - EPS)


def make_matrix(rows: list[dict[str, Any]], feature_names: list[str]) -> np.ndarray:
    data = []
    for row in rows:
        data.append([fnum(row.get(name)) for name in feature_names])
    return np.array(data, dtype=float)


def fit_ridge_logit(rows: list[dict[str, Any]], feature_names: list[str]) -> RidgeLogitModel:
    x = make_matrix(rows, feature_names)
    y = np.array([fnum(row.get("side_correct")) for row in rows], dtype=float)
    means = np.mean(x, axis=0)
    stds = np.std(x, axis=0)
    stds = np.where(stds < 1e-8, 1.0, stds)
    z = (x - means) / stds
    x_aug = np.column_stack([np.ones(len(z)), z])
    start = np.zeros(x_aug.shape[1], dtype=float)
    prior_p = clamp(float(np.mean(y)) if len(y) else 0.5)
    start[0] = float(logit(prior_p))

    def objective(weights: np.ndarray) -> tuple[float, np.ndarray]:
        logits = x_aug @ weights
        pred = expit(logits)
        nll = float(np.mean(np.logaddexp(0.0, logits) - y * logits))
        penalty = 0.5 * L2_REG * float(np.sum(weights[1:] ** 2)) / max(1, len(y))
        grad = (x_aug.T @ (pred - y)) / max(1, len(y))
        grad[1:] += L2_REG * weights[1:] / max(1, len(y))
        return nll + penalty, grad

    res = minimize(lambda w: objective(w), start, jac=True, method="L-BFGS-B", options={"maxiter": 500})
    train_nll, _ = objective(np.array(res.x, dtype=float))
    return RidgeLogitModel(
        feature_names=feature_names,
        means=means,
        stds=stds,
        weights=np.array(res.x, dtype=float),
        train_nll=float(train_nll),
        success=bool(res.success),
    )


def probability_metrics(rows: list[dict[str, Any]], preds: np.ndarray) -> dict[str, Any]:
    y = np.array([fnum(row.get("side_correct")) for row in rows], dtype=float)
    return {
        "rows": int(len(rows)),
        "brier": brier_np(y, preds),
        "log_loss": log_loss_np(y, preds),
        "auc": auc_np(y, preds),
    }


def pnl_stats(rows: list[dict[str, Any]]) -> dict[str, Any]:
    wins = sum(1 for row in rows if fnum(row.get("pnl_cents")) > 0)
    losses = sum(1 for row in rows if fnum(row.get("pnl_cents")) < 0)
    flats = sum(1 for row in rows if fnum(row.get("pnl_cents")) == 0)
    net = sum(fnum(row.get("pnl_cents")) for row in rows)
    return {
        "entries": int(len(rows)),
        "wins": int(wins),
        "losses": int(losses),
        "flats": int(flats),
        "win_rate_ex_flat": wins / (wins + losses) if wins + losses else None,
        "net_cents": net,
        "net_dollars": net / 100.0,
        "avg_cents_per_entry": net / len(rows) if rows else None,
    }


def choose_threshold(rows: list[dict[str, Any]], preds: np.ndarray, *, robust_only: bool) -> dict[str, Any]:
    min_entries = max(12, int(math.ceil(0.08 * len(rows))))
    candidates = []
    for threshold in THRESHOLDS:
        selected = [
            row
            for row, pred in zip(rows, preds)
            if pred >= threshold and (not robust_only or priority.robust_hybrid(row))
        ]
        if len(selected) < min_entries:
            continue
        stats = pnl_stats(selected)
        avg_cents = fnum(stats.get("avg_cents_per_entry"))
        score = avg_cents * math.sqrt(len(selected))
        candidates.append({"threshold": threshold, "stats": stats, "score": score})
    if not candidates:
        return {"threshold": 0.70, "stats": pnl_stats([]), "score": None, "fallback": True}
    candidates.sort(key=lambda item: (item["score"], item["stats"]["net_cents"]), reverse=True)
    chosen = dict(candidates[0])
    chosen["fallback"] = False
    return chosen


def select_by_threshold(
    rows: list[dict[str, Any]],
    preds: np.ndarray,
    threshold: float,
    *,
    robust_only: bool,
) -> list[dict[str, Any]]:
    return [
        row
        for row, pred in zip(rows, preds)
        if pred >= threshold and (not robust_only or priority.robust_hybrid(row))
    ]


def frame_redundancy(rows: list[dict[str, Any]], family: str) -> dict[str, Any]:
    frame_names = [name for name in feature_names_for_family(family) if name not in BASE_FEATURES]
    if len(frame_names) < 2:
        return {"feature_count": len(frame_names), "mean_abs_corr": None, "condition_number": None}
    x = make_matrix(rows, frame_names)
    stds = np.std(x, axis=0)
    keep = stds > 1e-8
    x = x[:, keep]
    if x.shape[1] < 2:
        return {"feature_count": int(x.shape[1]), "mean_abs_corr": None, "condition_number": None}
    z = (x - np.mean(x, axis=0)) / np.std(x, axis=0)
    corr = np.corrcoef(z, rowvar=False)
    upper = np.abs(corr[np.triu_indices(corr.shape[0], k=1)])
    return {
        "feature_count": int(x.shape[1]),
        "mean_abs_corr": float(np.nanmean(upper)),
        "median_abs_corr": float(np.nanmedian(upper)),
        "condition_number": float(np.linalg.cond(z)),
    }


def evaluate_family(rows: list[dict[str, Any]], family: str) -> dict[str, Any]:
    feature_names = feature_names_for_family(family)
    split_reports = []
    all_test_rows: list[dict[str, Any]] = []
    all_test_preds: list[float] = []
    all_selected: dict[str, list[dict[str, Any]]] = {"model_all": [], "robust_overlay": []}

    for split in WFA_SPLITS:
        train = row_window(rows, *split["train"])
        test = row_window(rows, *split["test"])
        model = fit_ridge_logit(train, feature_names)
        train_preds = model.predict(train)
        test_preds = model.predict(test)
        gates = {
            "model_all": choose_threshold(train, train_preds, robust_only=False),
            "robust_overlay": choose_threshold(train, train_preds, robust_only=True),
        }
        split_gate_reports: dict[str, Any] = {}
        for gate_name, gate in gates.items():
            selected = select_by_threshold(
                test,
                test_preds,
                float(gate["threshold"]),
                robust_only=gate_name == "robust_overlay",
            )
            all_selected[gate_name].extend(selected)
            split_gate_reports[gate_name] = {
                "threshold": gate["threshold"],
                "train_stats": gate["stats"],
                "test_stats": pnl_stats(selected),
                "fallback_threshold": gate["fallback"],
            }
        split_reports.append(
            {
                "name": split["name"],
                "train_rows": len(train),
                "test_rows": len(test),
                "model_success": model.success,
                "train_nll": model.train_nll,
                "probability": probability_metrics(test, test_preds),
                "gates": split_gate_reports,
            }
        )
        all_test_rows.extend(test)
        all_test_preds.extend(float(v) for v in test_preds)

    aggregate_probability = probability_metrics(all_test_rows, np.array(all_test_preds, dtype=float))
    aggregate_gates = {}
    for gate_name, selected in all_selected.items():
        nets = [fnum(split["gates"][gate_name]["test_stats"]["net_cents"]) for split in split_reports]
        entries = [int(split["gates"][gate_name]["test_stats"]["entries"]) for split in split_reports]
        aggregate_gates[gate_name] = {
            "stats": pnl_stats(selected),
            "positive_windows": int(sum(1 for value in nets if value > 0)),
            "traded_windows": int(sum(1 for value in entries if value > 0)),
            "window_net_cents": nets,
            "window_entries": entries,
            "pnl_cv_abs": safe_cv(nets),
            "max_window_share_abs": max((abs(v) for v in nets), default=0.0) / max(1e-9, sum(abs(v) for v in nets)),
        }

    return {
        "family": family,
        "frames_minutes": list(FRAME_FAMILIES[family]),
        "feature_names": feature_names,
        "probability": aggregate_probability,
        "gates": aggregate_gates,
        "locked_train200": evaluate_locked_train200(rows, feature_names),
        "splits": split_reports,
        "redundancy": frame_redundancy(rows, family),
    }


def evaluate_locked_train200(rows: list[dict[str, Any]], feature_names: list[str]) -> dict[str, Any]:
    train = row_window(rows, 1, 200)
    test = row_window(rows, 201, None)
    model = fit_ridge_logit(train, feature_names)
    train_preds = model.predict(train)
    test_preds = model.predict(test)
    out: dict[str, Any] = {
        "train_rows": len(train),
        "test_rows": len(test),
        "probability": probability_metrics(test, test_preds),
        "gates": {},
    }
    for gate_name, robust_only in (("model_all", False), ("robust_overlay", True)):
        gate = choose_threshold(train, train_preds, robust_only=robust_only)
        selected = select_by_threshold(test, test_preds, float(gate["threshold"]), robust_only=robust_only)
        out["gates"][gate_name] = {
            "threshold": gate["threshold"],
            "train_stats": gate["stats"],
            "test_stats": pnl_stats(selected),
            "fallback_threshold": gate["fallback"],
        }
    return out


def raw_probability_score(rows: list[dict[str, Any]], key: str, start: int = 201) -> dict[str, Any]:
    test = row_window(rows, start, None)
    y = np.array([fnum(row.get("side_correct")) for row in test], dtype=float)
    p = np.array([clamp(fnum(row.get(key), 0.5)) for row in test], dtype=float)
    return probability_metrics(test, p)


def fixed_gate_report(rows: list[dict[str, Any]], key: str, threshold: float, *, robust_only: bool, start: int = 201) -> dict[str, Any]:
    test = row_window(rows, start, None)
    selected = [
        row
        for row in test
        if fnum(row.get(key), 0.0) >= threshold and (not robust_only or priority.robust_hybrid(row))
    ]
    return pnl_stats(selected)


def build_rows(fetch_btc_candles: bool) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    rows, diagnostics, locked, _deep = aci_projection.annotate_rows()
    candles, candle_stats = load_candles(rows, fetch_missing=fetch_btc_candles)
    max_lookback = max(max(frames) if frames else 0 for frames in FRAME_FAMILIES.values())
    usable = []
    dropped = {"missing_label": 0, "missing_btc_frame": 0}
    for idx, row in enumerate(rows, start=1):
        if priority.maybe_float(row.get("side_correct")) is None:
            dropped["missing_label"] += 1
            continue
        row = dict(row)
        row["row_idx"] = idx
        add_base_features(row)
        if not add_frame_features(row, candles, max_lookback):
            dropped["missing_btc_frame"] += 1
            continue
        usable.append(row)
    return usable, {
        "row_diagnostics": diagnostics,
        "aci_locked_calibrator": locked,
        "candle_stats": candle_stats,
        "raw_rows": len(rows),
        "usable_rows": len(usable),
        "dropped": dropped,
        "usable_row_idx_min": min((row["row_idx"] for row in usable), default=None),
        "usable_row_idx_max": max((row["row_idx"] for row in usable), default=None),
    }


def build_report(fetch_btc_candles: bool) -> dict[str, Any]:
    rows, diagnostics = build_rows(fetch_btc_candles)
    if len(rows) < 260:
        raise RuntimeError(f"Need at least 260 usable rows for WFA; found {len(rows)}")
    families = {family: evaluate_family(rows, family) for family in FRAME_FAMILIES}
    baseline = {
        "p_calibrated_forward_after_200": raw_probability_score(rows, "p_calibrated"),
        "brownian_terminal_forward_after_200": raw_probability_score(rows, "brownian_terminal_p_side"),
        "robust_p_cal_ge_0p70_forward_after_200": fixed_gate_report(rows, "p_calibrated", 0.70, robust_only=True),
        "robust_p_cal_ge_0p80_forward_after_200": fixed_gate_report(rows, "p_calibrated", 0.80, robust_only=True),
        "robust_hybrid_base_forward_after_200": pnl_stats([row for row in row_window(rows, 201, None) if priority.robust_hybrid(row)]),
    }
    summary_rows = []
    for family, report in families.items():
        for gate_name, gate in report["gates"].items():
            stats = gate["stats"]
            summary_rows.append(
                {
                    "family": family,
                    "gate": gate_name,
                    "frames_minutes": ",".join(str(v) for v in report["frames_minutes"]),
                    "feature_count": len(report["feature_names"]),
                    "brier": report["probability"]["brier"],
                    "log_loss": report["probability"]["log_loss"],
                    "auc": report["probability"]["auc"],
                    "entries": stats["entries"],
                    "wins": stats["wins"],
                    "losses": stats["losses"],
                    "flats": stats["flats"],
                    "win_rate_ex_flat": stats["win_rate_ex_flat"],
                    "net_dollars": stats["net_dollars"],
                    "avg_cents_per_entry": stats["avg_cents_per_entry"],
                    "positive_windows": gate["positive_windows"],
                    "traded_windows": gate["traded_windows"],
                    "pnl_cv_abs": gate["pnl_cv_abs"],
                    "mean_abs_corr": report["redundancy"]["mean_abs_corr"],
                    "condition_number": report["redundancy"]["condition_number"],
                    "locked_robust_entries": report["locked_train200"]["gates"]["robust_overlay"]["test_stats"]["entries"],
                    "locked_robust_net_dollars": report["locked_train200"]["gates"]["robust_overlay"]["test_stats"]["net_dollars"],
                    "locked_robust_avg_cents_per_entry": report["locked_train200"]["gates"]["robust_overlay"]["test_stats"]["avg_cents_per_entry"],
                    "locked_robust_threshold": report["locked_train200"]["gates"]["robust_overlay"]["threshold"],
                }
            )
    summary_rows.sort(
        key=lambda row: (
            fnum(row.get("positive_windows")),
            fnum(row.get("net_dollars")),
            -fnum(row.get("log_loss"), 999.0),
        ),
        reverse=True,
    )
    return {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "scope": "research_only_filled_trade_replay",
        "hypothesis": "Phi/geometric lookback features reduce redundant timeframe noise and improve forward stability versus standard calendar frames.",
        "limitations": [
            "Local source is 1-minute Coinbase candles, so true 1-second/15-second phi frames are approximated by rounded minute lookbacks.",
            "PnL uses historical filled rows only; this does not include all skipped candidates or counterfactual fill probability.",
            "All frame models use the same fixed ridge penalty and the same train-only threshold selection grid.",
        ],
        "diagnostics": diagnostics,
        "baseline": baseline,
        "families": families,
        "summary_rows": summary_rows,
    }


def write_report(report: dict[str, Any]) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True, default=str), encoding="utf-8")
    pd.DataFrame(report["summary_rows"]).to_csv(OUT_SUMMARY_CSV, index=False)

    lines = [
        "# Phi-Frame Feature Comparison",
        "",
        "Research-only filled-trade replay. No live bot logic/state/order path was changed.",
        "",
        "## Data",
        f"- Usable rows: `{report['diagnostics']['usable_rows']}` / raw rows `{report['diagnostics']['raw_rows']}`.",
        f"- Row idx range: `{report['diagnostics']['usable_row_idx_min']}` to `{report['diagnostics']['usable_row_idx_max']}`.",
        f"- BTC candles: `{report['diagnostics']['candle_stats']['candle_min_utc']}` to `{report['diagnostics']['candle_stats']['candle_max_utc']}`.",
        "",
        "## Probability Score, Forward Rows 201+",
        f"- Raw capped-ACI p_calibrated: Brier `{report['baseline']['p_calibrated_forward_after_200']['brier']:.5f}`, log loss `{report['baseline']['p_calibrated_forward_after_200']['log_loss']:.5f}`.",
        f"- Brownian terminal: Brier `{report['baseline']['brownian_terminal_forward_after_200']['brier']:.5f}`, log loss `{report['baseline']['brownian_terminal_forward_after_200']['log_loss']:.5f}`.",
        "",
        "## Top WFA PnL Rows",
        "| rank | family | gate | frames | brier | log_loss | entries | W/L | pnl | avg/entry | pos windows | mean abs corr |",
        "|---:|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for rank, row in enumerate(report["summary_rows"][:14], start=1):
        wl = f"{int(row['wins'])}/{int(row['losses'])}"
        if int(row["flats"]):
            wl += f" +{int(row['flats'])} flat"
        corr = row.get("mean_abs_corr")
        lines.append(
            "| "
            + " | ".join(
                [
                    str(rank),
                    str(row["family"]),
                    str(row["gate"]),
                    str(row["frames_minutes"] or "base"),
                    f"{fnum(row['brier']):.5f}",
                    f"{fnum(row['log_loss']):.5f}",
                    str(int(row["entries"])),
                    wl,
                    f"${fnum(row['net_dollars']):.2f}",
                    f"{fnum(row['avg_cents_per_entry']):.1f}c",
                    f"{int(row['positive_windows'])}/{int(row['traded_windows'])}",
                    "n/a" if corr is None else f"{float(corr):.3f}",
                ]
            )
            + " |"
        )
    lines.extend(
        [
            "",
            "## Locked Train-200 Robust Overlay",
            "| family | frames | threshold | entries | W/L | pnl | avg/entry |",
            "|---|---|---:|---:|---:|---:|---:|",
        ]
    )
    locked_rows = sorted(
        (
            {
                "family": family,
                "frames": ",".join(str(v) for v in report["frames_minutes"]),
                "gate": report["locked_train200"]["gates"]["robust_overlay"],
            }
            for family, report in report["families"].items()
        ),
        key=lambda row: fnum(row["gate"]["test_stats"]["net_dollars"]),
        reverse=True,
    )
    for row in locked_rows:
        stats = row["gate"]["test_stats"]
        wl = f"{stats['wins']}/{stats['losses']}"
        if stats["flats"]:
            wl += f" +{stats['flats']} flat"
        lines.append(
            "| "
            + " | ".join(
                [
                    str(row["family"]),
                    str(row["frames"] or "base"),
                    f"{fnum(row['gate']['threshold']):.2f}",
                    str(stats["entries"]),
                    wl,
                    f"${stats['net_dollars']:.2f}",
                    f"{fnum(stats['avg_cents_per_entry']):.1f}c",
                ]
            )
            + " |"
        )
    lines.extend(
        [
            "",
            "## Baseline Gates",
        ]
    )
    for name in (
        "robust_hybrid_base_forward_after_200",
        "robust_p_cal_ge_0p70_forward_after_200",
        "robust_p_cal_ge_0p80_forward_after_200",
    ):
        stats = report["baseline"][name]
        wl = f"{stats['wins']}/{stats['losses']}"
        if stats["flats"]:
            wl += f" +{stats['flats']} flat"
        lines.append(
            f"- {name}: entries `{stats['entries']}`, W/L `{wl}`, PnL `${stats['net_dollars']:.2f}`, avg `{fnum(stats['avg_cents_per_entry']):.1f}c`."
        )
    lines.extend(
        [
            "",
            "## Interpretation",
            "- Promotion needs better probability score and more stable WFA PnL than the capped-ACI/robust baselines, not just a prettier frame list.",
            "- Since this is filled-trade replay, any promising row still needs all-candidate shadow validation before live use.",
        ]
    )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--fetch-btc-candles", action="store_true", help="Fetch missing Coinbase BTC-USD 1m candles into the research cache.")
    args = parser.parse_args()
    report = build_report(fetch_btc_candles=bool(args.fetch_btc_candles))
    write_report(report)
    print(f"wrote {OUT_MD}")
    print(f"wrote {OUT_JSON}")
    print(f"wrote {OUT_SUMMARY_CSV}")


if __name__ == "__main__":
    main()
