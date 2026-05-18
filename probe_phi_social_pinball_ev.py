"""Bake off phi frames, social/microstructure states, and pinball EV models.

Research-only. This tests the user's combined idea:

    phi-frame features + social/microstructure state + pinball pegs
    -> predict expected PnL, then trade only positive expected value rows.

The replay uses historical filled rows only. That makes this a useful signal
triage, not a live-ready strategy proof, because skipped candidates and true
counterfactual fill outcomes are not present in this table.
"""
from __future__ import annotations

import argparse
import json
import math
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from statistics import mean, stdev
from typing import Any

import numpy as np
import pandas as pd
from scipy.stats import spearmanr

import probe_arxiv_strategy_priority_tests as priority
import probe_phi_frame_feature_comparison as phi


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
OUT_JSON = OUT_DIR / "phi_social_pinball_ev_latest.json"
OUT_MD = OUT_DIR / "phi_social_pinball_ev_latest.md"
OUT_SUMMARY_CSV = OUT_DIR / "phi_social_pinball_ev_summary_latest.csv"

RIDGE_REG = 25.0
THRESHOLDS_CENTS = (-20, -15, -10, -5, 0, 2, 4, 6, 8, 10, 12, 15, 20, 25, 30, 40)
WFA_SPLITS = phi.WFA_SPLITS

PHI_FRAME_FEATURES = [
    name for name in phi.feature_names_for_family("phi_6") if name not in phi.BASE_FEATURES
]
STANDARD_FRAME_FEATURES = [
    name for name in phi.feature_names_for_family("standard_6") if name not in phi.BASE_FEATURES
]

SOCIAL_FEATURES = (
    "state_liquidity_trust",
    "state_stale_book_risk",
    "state_stale_btc_risk",
    "state_stale_mm_gap",
    "state_chase_pressure",
    "state_panic_vol",
    "state_crowding_depth",
    "state_late_boundary_pressure",
    "state_model_disagreement",
    "state_price_expensive",
    "state_social_attention",
)

PINBALL_PEGS = (
    "peg_p_cal_ge_70",
    "peg_p_cal_ge_75",
    "peg_p_cal_ge_80",
    "peg_p_cal_ge_85",
    "peg_brownian_ge_70",
    "peg_brownian_ge_80",
    "peg_cal_edge_pos",
    "peg_cal_edge_ge_2c",
    "peg_cal_edge_ge_5c",
    "peg_raw_edge_ge_3c",
    "peg_raw_edge_ge_8c",
    "peg_depth_ge_8",
    "peg_depth_ge_20",
    "peg_depth_lt_8",
    "peg_book_fresh_250ms",
    "peg_book_fresh_500ms",
    "peg_book_stale_750ms",
    "peg_btc_fresh_250ms",
    "peg_btc_stale_750ms",
    "peg_absd_70_110",
    "peg_absd_80_120",
    "peg_seconds_ge_120",
    "peg_seconds_ge_300",
    "peg_late_le_300",
    "peg_ask_le_70",
    "peg_ask_le_80",
    "peg_ask_ge_85",
    "peg_volshock_abs_ge_80",
    "peg_model_agree_close",
    "peg_phi_1m_with_side",
    "peg_phi_3m_with_side",
    "peg_phi_8m_with_side",
    "peg_phi_13m_with_side",
    "peg_social_liquidity_good",
    "peg_social_stale_gap",
    "peg_social_chase",
    "peg_social_panic",
)

FEATURE_SETS = {
    "base_ev": list(phi.BASE_FEATURES),
    "phi_only": list(phi.BASE_FEATURES) + PHI_FRAME_FEATURES,
    "social_only": list(phi.BASE_FEATURES) + list(SOCIAL_FEATURES),
    "pinball_only": list(PINBALL_PEGS),
    "phi_social": list(phi.BASE_FEATURES) + PHI_FRAME_FEATURES + list(SOCIAL_FEATURES),
    "phi_pinball": list(phi.BASE_FEATURES) + PHI_FRAME_FEATURES + list(PINBALL_PEGS),
    "social_pinball": list(phi.BASE_FEATURES) + list(SOCIAL_FEATURES) + list(PINBALL_PEGS),
    "all3_phi_social_pinball": list(phi.BASE_FEATURES)
    + PHI_FRAME_FEATURES
    + list(SOCIAL_FEATURES)
    + list(PINBALL_PEGS),
    # Control: the same social/pinball layer but with human-standard minute frames.
    "standard6_social_pinball_control": list(phi.BASE_FEATURES)
    + STANDARD_FRAME_FEATURES
    + list(SOCIAL_FEATURES)
    + list(PINBALL_PEGS),
}


def fnum(value: Any, default: float = 0.0) -> float:
    parsed = priority.maybe_float(value)
    return default if parsed is None else float(parsed)


def clamp(value: float, low: float = 0.0, high: float = 1.0) -> float:
    return max(low, min(high, float(value)))


def tanh_scaled(value: float, scale: float) -> float:
    if scale <= 0:
        return 0.0
    return math.tanh(value / scale)


def safe_cv(values: list[float]) -> float | None:
    vals = [v for v in values if math.isfinite(v)]
    if len(vals) < 2:
        return None
    avg = mean(vals)
    if abs(avg) < 1e-9:
        return None
    return abs(stdev(vals) / avg)


def spearman_safe(x: list[float], y: list[float]) -> float | None:
    if len(x) < 5 or len(y) < 5:
        return None
    stat = spearmanr(x, y).statistic
    if stat is None or not math.isfinite(float(stat)):
        return None
    return float(stat)


def row_window(rows: list[dict[str, Any]], start: int, end: int | None) -> list[dict[str, Any]]:
    return phi.row_window(rows, start, end)


def add_social_state_features(row: dict[str, Any]) -> None:
    p_cal = fnum(row.get("p_calibrated"), 0.5)
    p_raw = fnum(row.get("p28"), 0.5)
    p_brownian = fnum(row.get("brownian_terminal_p_side"), 0.5)
    side = str(row.get("side") or "").lower()
    market_p_yes = fnum(row.get("market_p_yes"), 0.5)
    market_p_side = market_p_yes if side == "yes" else 1.0 - market_p_yes
    depth_ratio = max(0.0, fnum(row.get("depth_ratio")))
    book_age = max(0.0, fnum(row.get("book_age_ms")))
    btc_age = max(0.0, fnum(row.get("btc_age_ms")))
    seconds = max(0.0, fnum(row.get("seconds_to_close")))
    ask = fnum(row.get("ask_cents"))
    absd = abs(fnum(row.get("abs_d_sigma")))
    volshock = fnum(row.get("volshock"))
    recent_momentum = max(
        abs(fnum(row.get("frame_1m_side_ret_z"))),
        abs(fnum(row.get("frame_2m_side_ret_z"))),
        abs(fnum(row.get("frame_3m_side_ret_z"))),
    )
    chase_pressure = max(0.0, fnum(row.get("frame_1m_side_ret_z"))) * 0.50
    chase_pressure += max(0.0, fnum(row.get("frame_3m_side_ret_z"))) * 0.30
    chase_pressure += max(0.0, fnum(row.get("frame_8m_side_ret_z"))) * 0.20

    liquidity_trust = clamp(math.log1p(depth_ratio) / math.log(41.0), 0.0, 1.0)
    liquidity_trust *= math.exp(-book_age / 900.0)
    liquidity_trust *= math.exp(-btc_age / 900.0)

    stale_gap = abs(p_cal - market_p_side)
    model_disagreement = abs(p_raw - p_brownian)
    late_pressure = clamp((900.0 - seconds) / 900.0) * math.exp(-((absd - 1.0) ** 2) / 0.25)
    panic_vol = clamp(abs(volshock) / 1.5) + clamp(recent_momentum / 3.0)
    panic_vol = clamp(panic_vol / 2.0)
    crowding_depth = clamp(tanh_scaled(depth_ratio - 8.0, 16.0) * 0.5 + 0.5)
    price_expensive = clamp((ask - 50.0) / 45.0)
    social_attention = clamp(0.45 * liquidity_trust + 0.35 * stale_gap / 0.25 + 0.20 * crowding_depth)

    row["state_liquidity_trust"] = liquidity_trust
    row["state_stale_book_risk"] = clamp(book_age / 1000.0)
    row["state_stale_btc_risk"] = clamp(btc_age / 1000.0)
    row["state_stale_mm_gap"] = clamp(stale_gap / 0.25)
    row["state_chase_pressure"] = chase_pressure
    row["state_panic_vol"] = panic_vol
    row["state_crowding_depth"] = crowding_depth
    row["state_late_boundary_pressure"] = late_pressure
    row["state_model_disagreement"] = clamp(model_disagreement / 0.25)
    row["state_price_expensive"] = price_expensive
    row["state_social_attention"] = social_attention


def set_peg(row: dict[str, Any], name: str, value: bool) -> None:
    row[name] = 1.0 if value else 0.0


def add_pinball_pegs(row: dict[str, Any]) -> None:
    p_cal = fnum(row.get("p_calibrated"), 0.0)
    p_brownian = fnum(row.get("brownian_terminal_p_side"), 0.0)
    depth = fnum(row.get("depth_ratio"))
    book_age = fnum(row.get("book_age_ms"))
    btc_age = fnum(row.get("btc_age_ms"))
    absd = abs(fnum(row.get("abs_d_sigma")))
    seconds = fnum(row.get("seconds_to_close"))
    ask = fnum(row.get("ask_cents"))
    model_disagreement = fnum(row.get("state_model_disagreement"))

    thresholds = {
        "peg_p_cal_ge_70": p_cal >= 0.70,
        "peg_p_cal_ge_75": p_cal >= 0.75,
        "peg_p_cal_ge_80": p_cal >= 0.80,
        "peg_p_cal_ge_85": p_cal >= 0.85,
        "peg_brownian_ge_70": p_brownian >= 0.70,
        "peg_brownian_ge_80": p_brownian >= 0.80,
        "peg_cal_edge_pos": fnum(row.get("calibrated_edge_cents")) > 0.0,
        "peg_cal_edge_ge_2c": fnum(row.get("calibrated_edge_cents")) >= 2.0,
        "peg_cal_edge_ge_5c": fnum(row.get("calibrated_edge_cents")) >= 5.0,
        "peg_raw_edge_ge_3c": fnum(row.get("edge28_cents")) >= 3.0,
        "peg_raw_edge_ge_8c": fnum(row.get("edge28_cents")) >= 8.0,
        "peg_depth_ge_8": depth >= 8.0,
        "peg_depth_ge_20": depth >= 20.0,
        "peg_depth_lt_8": depth < 8.0,
        "peg_book_fresh_250ms": book_age <= 250.0,
        "peg_book_fresh_500ms": book_age <= 500.0,
        "peg_book_stale_750ms": book_age >= 750.0,
        "peg_btc_fresh_250ms": btc_age <= 250.0,
        "peg_btc_stale_750ms": btc_age >= 750.0,
        "peg_absd_70_110": 0.70 <= absd <= 1.10,
        "peg_absd_80_120": 0.80 <= absd <= 1.20,
        "peg_seconds_ge_120": seconds >= 120.0,
        "peg_seconds_ge_300": seconds >= 300.0,
        "peg_late_le_300": seconds <= 300.0,
        "peg_ask_le_70": ask <= 70.0,
        "peg_ask_le_80": ask <= 80.0,
        "peg_ask_ge_85": ask >= 85.0,
        "peg_volshock_abs_ge_80": abs(fnum(row.get("volshock"))) >= 0.80,
        "peg_model_agree_close": model_disagreement <= 0.20,
        "peg_phi_1m_with_side": fnum(row.get("frame_1m_side_ret_z")) > 0.0,
        "peg_phi_3m_with_side": fnum(row.get("frame_3m_side_ret_z")) > 0.0,
        "peg_phi_8m_with_side": fnum(row.get("frame_8m_side_ret_z")) > 0.0,
        "peg_phi_13m_with_side": fnum(row.get("frame_13m_side_ret_z")) > 0.0,
        "peg_social_liquidity_good": fnum(row.get("state_liquidity_trust")) >= 0.35,
        "peg_social_stale_gap": fnum(row.get("state_stale_mm_gap")) >= 0.50,
        "peg_social_chase": fnum(row.get("state_chase_pressure")) >= 0.50,
        "peg_social_panic": fnum(row.get("state_panic_vol")) >= 0.50,
    }
    for name, value in thresholds.items():
        set_peg(row, name, value)


@dataclass
class RidgeEvModel:
    feature_names: list[str]
    means: np.ndarray
    stds: np.ndarray
    weights: np.ndarray

    def predict(self, rows: list[dict[str, Any]]) -> np.ndarray:
        x = make_matrix(rows, self.feature_names)
        z = (x - self.means) / self.stds
        x_aug = np.column_stack([np.ones(len(z)), z])
        return x_aug @ self.weights


def make_matrix(rows: list[dict[str, Any]], feature_names: list[str]) -> np.ndarray:
    return np.array([[fnum(row.get(name)) for name in feature_names] for row in rows], dtype=float)


def fit_ridge_ev(rows: list[dict[str, Any]], feature_names: list[str]) -> RidgeEvModel:
    x = make_matrix(rows, feature_names)
    y = np.array([fnum(row.get("pnl_cents")) for row in rows], dtype=float)
    means = x.mean(axis=0)
    stds = x.std(axis=0)
    stds = np.where(stds < 1e-8, 1.0, stds)
    z = (x - means) / stds
    x_aug = np.column_stack([np.ones(len(z)), z])
    penalty = np.eye(x_aug.shape[1]) * RIDGE_REG
    penalty[0, 0] = 0.0
    weights = np.linalg.solve(x_aug.T @ x_aug + penalty, x_aug.T @ y)
    return RidgeEvModel(feature_names=feature_names, means=means, stds=stds, weights=weights)


def ev_model_metrics(rows: list[dict[str, Any]], preds: np.ndarray) -> dict[str, Any]:
    y = np.array([fnum(row.get("pnl_cents")) for row in rows], dtype=float)
    err = preds - y
    top_cut = np.quantile(preds, 0.75) if len(preds) else float("inf")
    top_rows = [row for row, pred in zip(rows, preds) if pred >= top_cut]
    return {
        "rows": int(len(rows)),
        "mean_pred_ev_cents": float(np.mean(preds)) if len(preds) else None,
        "mean_actual_pnl_cents": float(np.mean(y)) if len(y) else None,
        "rmse_cents": float(np.sqrt(np.mean(err**2))) if len(err) else None,
        "mae_cents": float(np.mean(np.abs(err))) if len(err) else None,
        "spearman_pred_vs_pnl": spearman_safe(preds.tolist(), y.tolist()),
        "top_quartile": phi.pnl_stats(top_rows),
    }


def choose_ev_threshold(rows: list[dict[str, Any]], preds: np.ndarray, *, robust_only: bool) -> dict[str, Any]:
    min_entries = max(10, int(math.ceil(0.08 * len(rows))))
    candidates = []
    for threshold in THRESHOLDS_CENTS:
        selected = [
            row
            for row, pred in zip(rows, preds)
            if pred >= threshold and (not robust_only or priority.robust_hybrid(row))
        ]
        if len(selected) < min_entries:
            continue
        stats = phi.pnl_stats(selected)
        avg = fnum(stats.get("avg_cents_per_entry"))
        score = avg * math.sqrt(len(selected))
        candidates.append({"threshold_ev_cents": threshold, "stats": stats, "score": score})
    if not candidates:
        return {"threshold_ev_cents": 0.0, "stats": phi.pnl_stats([]), "score": None, "fallback": True}
    candidates.sort(key=lambda item: (item["score"], item["stats"]["net_cents"]), reverse=True)
    chosen = dict(candidates[0])
    chosen["fallback"] = False
    return chosen


def select_by_ev_threshold(
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


def evaluate_feature_set(rows: list[dict[str, Any]], feature_set: str, feature_names: list[str]) -> dict[str, Any]:
    split_reports = []
    all_test_rows: list[dict[str, Any]] = []
    all_test_preds: list[float] = []
    all_selected: dict[str, list[dict[str, Any]]] = {"ev_all": [], "robust_ev_overlay": []}

    for split in WFA_SPLITS:
        train = row_window(rows, *split["train"])
        test = row_window(rows, *split["test"])
        model = fit_ridge_ev(train, feature_names)
        train_preds = model.predict(train)
        test_preds = model.predict(test)
        gates = {
            "ev_all": choose_ev_threshold(train, train_preds, robust_only=False),
            "robust_ev_overlay": choose_ev_threshold(train, train_preds, robust_only=True),
        }
        gate_reports = {}
        for gate_name, gate in gates.items():
            selected = select_by_ev_threshold(
                test,
                test_preds,
                float(gate["threshold_ev_cents"]),
                robust_only=gate_name == "robust_ev_overlay",
            )
            all_selected[gate_name].extend(selected)
            gate_reports[gate_name] = {
                "threshold_ev_cents": gate["threshold_ev_cents"],
                "train_stats": gate["stats"],
                "test_stats": phi.pnl_stats(selected),
                "fallback_threshold": gate["fallback"],
            }
        all_test_rows.extend(test)
        all_test_preds.extend(float(v) for v in test_preds)
        split_reports.append(
            {
                "name": split["name"],
                "train_rows": len(train),
                "test_rows": len(test),
                "model_metrics": ev_model_metrics(test, test_preds),
                "gates": gate_reports,
            }
        )

    aggregate_gates = {}
    for gate_name, selected in all_selected.items():
        nets = [fnum(split["gates"][gate_name]["test_stats"]["net_cents"]) for split in split_reports]
        entries = [int(split["gates"][gate_name]["test_stats"]["entries"]) for split in split_reports]
        aggregate_gates[gate_name] = {
            "stats": phi.pnl_stats(selected),
            "positive_windows": int(sum(1 for value in nets if value > 0)),
            "traded_windows": int(sum(1 for value in entries if value > 0)),
            "window_net_cents": nets,
            "window_entries": entries,
            "pnl_cv_abs": safe_cv(nets),
            "max_window_share_abs": max((abs(v) for v in nets), default=0.0) / max(1e-9, sum(abs(v) for v in nets)),
        }

    return {
        "feature_set": feature_set,
        "feature_count": len(feature_names),
        "feature_names": feature_names,
        "aggregate_model_metrics": ev_model_metrics(all_test_rows, np.array(all_test_preds, dtype=float)),
        "gates": aggregate_gates,
        "splits": split_reports,
        "locked_train200": evaluate_locked_train200(rows, feature_names),
    }


def evaluate_locked_train200(rows: list[dict[str, Any]], feature_names: list[str]) -> dict[str, Any]:
    train = row_window(rows, 1, 200)
    test = row_window(rows, 201, None)
    model = fit_ridge_ev(train, feature_names)
    train_preds = model.predict(train)
    test_preds = model.predict(test)
    out = {
        "train_rows": len(train),
        "test_rows": len(test),
        "model_metrics": ev_model_metrics(test, test_preds),
        "gates": {},
    }
    for gate_name, robust_only in (("ev_all", False), ("robust_ev_overlay", True)):
        gate = choose_ev_threshold(train, train_preds, robust_only=robust_only)
        selected = select_by_ev_threshold(test, test_preds, float(gate["threshold_ev_cents"]), robust_only=robust_only)
        out["gates"][gate_name] = {
            "threshold_ev_cents": gate["threshold_ev_cents"],
            "train_stats": gate["stats"],
            "test_stats": phi.pnl_stats(selected),
            "fallback_threshold": gate["fallback"],
        }
    return out


def build_rows(fetch_btc_candles: bool) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    rows, diagnostics = phi.build_rows(fetch_btc_candles)
    usable = []
    for row in rows:
        row = dict(row)
        add_social_state_features(row)
        add_pinball_pegs(row)
        usable.append(row)
    diagnostics["social_features"] = list(SOCIAL_FEATURES)
    diagnostics["pinball_pegs"] = list(PINBALL_PEGS)
    return usable, diagnostics


def baseline_reports(rows: list[dict[str, Any]]) -> dict[str, Any]:
    forward = row_window(rows, 201, None)
    return {
        "live_all_recorded_forward_after_200": phi.pnl_stats(forward),
        "robust_hybrid_forward_after_200": phi.pnl_stats([row for row in forward if priority.robust_hybrid(row)]),
        "robust_p_cal_ge_0p70_forward_after_200": phi.fixed_gate_report(rows, "p_calibrated", 0.70, robust_only=True),
        "robust_p_cal_ge_0p80_forward_after_200": phi.fixed_gate_report(rows, "p_calibrated", 0.80, robust_only=True),
        "last_phi_probe_best_wfa_standard3": {
            "note": "For control context from the previous phi-frame feature comparison: standard_3 robust overlay was +$12.33 on 69 filled rows.",
        },
    }


def build_report(fetch_btc_candles: bool) -> dict[str, Any]:
    rows, diagnostics = build_rows(fetch_btc_candles)
    results = {name: evaluate_feature_set(rows, name, features) for name, features in FEATURE_SETS.items()}
    summary_rows = []
    for name, result in results.items():
        for gate_name, gate in result["gates"].items():
            stats = gate["stats"]
            locked = result["locked_train200"]["gates"][gate_name]["test_stats"]
            summary_rows.append(
                {
                    "feature_set": name,
                    "gate": gate_name,
                    "feature_count": result["feature_count"],
                    "spearman_pred_vs_pnl": result["aggregate_model_metrics"]["spearman_pred_vs_pnl"],
                    "top_quartile_net_dollars": result["aggregate_model_metrics"]["top_quartile"]["net_dollars"],
                    "entries": stats["entries"],
                    "wins": stats["wins"],
                    "losses": stats["losses"],
                    "flats": stats["flats"],
                    "win_rate_ex_flat": stats["win_rate_ex_flat"],
                    "net_dollars": stats["net_dollars"],
                    "avg_cents_per_entry": stats["avg_cents_per_entry"],
                    "positive_windows": gate["positive_windows"],
                    "traded_windows": gate["traded_windows"],
                    "window_net_cents": ",".join(f"{v:.1f}" for v in gate["window_net_cents"]),
                    "window_entries": ",".join(str(v) for v in gate["window_entries"]),
                    "locked_train200_entries": locked["entries"],
                    "locked_train200_net_dollars": locked["net_dollars"],
                    "locked_train200_avg_cents_per_entry": locked["avg_cents_per_entry"],
                    "locked_train200_wins": locked["wins"],
                    "locked_train200_losses": locked["losses"],
                }
            )
    summary_rows.sort(
        key=lambda row: (
            fnum(row.get("positive_windows")),
            fnum(row.get("net_dollars")),
            fnum(row.get("spearman_pred_vs_pnl"), -99),
        ),
        reverse=True,
    )
    return {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "scope": "research_only_filled_trade_replay",
        "hypothesis": "Test phi-frame features, social/microstructure state proxies, and pinball peg features for expected-PnL selection.",
        "limitations": [
            "Uses historical filled rows only; skipped candidates and no-fill IOC attempts are not represented.",
            "Social/microstructure states are proxies from logged depth/book age/BTC age/ask/edge/vol fields, not full order-flow psychology.",
            "BTC data is still 1-minute candles, so phi frames are minute approximations rather than true 1-second phi frames.",
            "EV thresholds are selected on each training window only, then applied forward.",
        ],
        "diagnostics": diagnostics,
        "baselines": baseline_reports(rows),
        "results": results,
        "summary_rows": summary_rows,
    }


def write_report(report: dict[str, Any]) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True, default=str), encoding="utf-8")
    pd.DataFrame(report["summary_rows"]).to_csv(OUT_SUMMARY_CSV, index=False)

    lines = [
        "# Phi + Social + Pinball EV Bakeoff",
        "",
        "Research-only filled-trade replay. No live bot logic/state/order path was changed.",
        "",
        "## Data",
        f"- Usable rows: `{report['diagnostics']['usable_rows']}` / raw rows `{report['diagnostics']['raw_rows']}`.",
        f"- Row idx range: `{report['diagnostics']['usable_row_idx_min']}` to `{report['diagnostics']['usable_row_idx_max']}`.",
        f"- BTC candles: `{report['diagnostics']['candle_stats']['candle_min_utc']}` to `{report['diagnostics']['candle_stats']['candle_max_utc']}`.",
        "",
        "## Baselines, Forward Rows 201+",
    ]
    for name, stats in report["baselines"].items():
        if "entries" not in stats:
            continue
        wl = f"{stats['wins']}/{stats['losses']}"
        if stats["flats"]:
            wl += f" +{stats['flats']} flat"
        lines.append(
            f"- {name}: entries `{stats['entries']}`, W/L `{wl}`, PnL `${stats['net_dollars']:.2f}`, avg `{fnum(stats['avg_cents_per_entry']):.1f}c`."
        )
    lines.extend(
        [
            "",
            "## WFA EV-Selection Results",
            "| rank | feature set | gate | features | pred-vs-PnL rho | top-Q pnl | entries | W/L | pnl | avg/entry | pos windows | window pnl c |",
            "|---:|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---|",
        ]
    )
    for rank, row in enumerate(report["summary_rows"][:18], start=1):
        wl = f"{int(row['wins'])}/{int(row['losses'])}"
        if int(row["flats"]):
            wl += f" +{int(row['flats'])} flat"
        rho = row.get("spearman_pred_vs_pnl")
        lines.append(
            "| "
            + " | ".join(
                [
                    str(rank),
                    str(row["feature_set"]),
                    str(row["gate"]),
                    str(row["feature_count"]),
                    "n/a" if rho is None else f"{float(rho):.3f}",
                    f"${fnum(row['top_quartile_net_dollars']):.2f}",
                    str(int(row["entries"])),
                    wl,
                    f"${fnum(row['net_dollars']):.2f}",
                    f"{fnum(row['avg_cents_per_entry']):.1f}c",
                    f"{int(row['positive_windows'])}/{int(row['traded_windows'])}",
                    str(row["window_net_cents"]),
                ]
            )
            + " |"
        )

    locked_rows = []
    for name, result in report["results"].items():
        for gate_name, gate in result["locked_train200"]["gates"].items():
            if gate_name != "robust_ev_overlay":
                continue
            locked_rows.append(
                {
                    "feature_set": name,
                    "threshold": gate["threshold_ev_cents"],
                    "stats": gate["test_stats"],
                    "rho": result["locked_train200"]["model_metrics"]["spearman_pred_vs_pnl"],
                }
            )
    locked_rows.sort(key=lambda item: fnum(item["stats"]["net_dollars"]), reverse=True)
    lines.extend(
        [
            "",
            "## Locked Train-200 Robust EV Overlay",
            "| feature set | threshold EV | rho | entries | W/L | pnl | avg/entry |",
            "|---|---:|---:|---:|---:|---:|---:|",
        ]
    )
    for item in locked_rows:
        stats = item["stats"]
        wl = f"{stats['wins']}/{stats['losses']}"
        if stats["flats"]:
            wl += f" +{stats['flats']} flat"
        rho = item.get("rho")
        lines.append(
            "| "
            + " | ".join(
                [
                    str(item["feature_set"]),
                    f"{fnum(item['threshold']):.1f}c",
                    "n/a" if rho is None else f"{float(rho):.3f}",
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
            "## Interpretation",
            "- A credible pass should beat the robust p_cal baseline, show positive predicted-EV ranking, and avoid one-window dependence.",
            "- Any replay-positive result here still needs all-candidate shadow logging because this table excludes skipped and unfilled opportunities.",
        ]
    )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--fetch-btc-candles", action="store_true")
    args = parser.parse_args()
    report = build_report(fetch_btc_candles=bool(args.fetch_btc_candles))
    write_report(report)
    print(f"wrote {OUT_MD}")
    print(f"wrote {OUT_JSON}")
    print(f"wrote {OUT_SUMMARY_CSV}")


if __name__ == "__main__":
    main()
