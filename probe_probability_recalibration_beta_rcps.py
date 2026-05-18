"""Beta/temperature calibration and RCPS-style threshold tests.

Research-only. This probe takes the latest Truffle suggestions and evaluates
whether smooth train-locked recalibration or risk-controlled thresholds improve
the current capped-ACI probability lane.

Nothing here changes live bot logic or places orders.
"""
from __future__ import annotations

import json
import math
from datetime import datetime, timezone
from pathlib import Path
from statistics import mean
from typing import Any, Callable

import numpy as np
from scipy.optimize import minimize, minimize_scalar
from scipy.special import expit, logit
from scipy.stats import kendalltau

import probe_arxiv_strategy_priority_tests as priority
import probe_self_calibrating_aci_pnl_projection as aci_projection


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
OUT_JSON = OUT_DIR / "probability_recalibration_beta_rcps_latest.json"
OUT_MD = OUT_DIR / "probability_recalibration_beta_rcps_latest.md"

WINDOWS = {
    "train_1_200": (1, 200),
    "validation_201_400": (201, 400),
    "holdout_401_end": (401, None),
    "forward_after_200": (201, None),
    "all": (1, None),
}
SOURCE_KEYS = ("p28", "brownian_terminal_p_side")
ALPHA_TARGETS = (0.20, 0.35, 0.45, 0.50, 0.60)
P_THRESHOLDS = (0.70, 0.75, 0.78, 0.80, 0.82, 0.85, 0.88)
E_PROCESS_LAMBDAS = (0.02, 0.05, 0.10, 0.20, 0.35)
E_PROCESS_THRESHOLDS = (20.0, 100.0)
WFA_SPLITS = (
    (1, 200, 201, 270),
    (71, 270, 271, 340),
    (141, 340, 341, 410),
    (211, 410, 411, None),
)

Predicate = Callable[[dict[str, Any]], bool]


def fnum(value: Any, default: float = 0.0) -> float:
    parsed = priority.maybe_float(value)
    return default if parsed is None else parsed


def clamp(value: float, low: float = 1e-6, high: float = 1.0 - 1e-6) -> float:
    return min(high, max(low, value))


def row_window(rows: list[dict[str, Any]], start: int, end: int | None) -> list[dict[str, Any]]:
    out = []
    for idx, row in enumerate(rows, start=1):
        if idx < start:
            continue
        if end is not None and idx > end:
            continue
        out.append(row)
    return out


def selected(rows: list[dict[str, Any]], predicate: Predicate) -> list[dict[str, Any]]:
    return [row for row in rows if predicate(row)]


def stats(rows: list[dict[str, Any]], denominator: int) -> dict[str, Any]:
    return priority.stats(rows, denominator)


def label_and_score(rows: list[dict[str, Any]], key: str) -> tuple[np.ndarray, np.ndarray]:
    labels = []
    scores = []
    for row in rows:
        y = priority.maybe_float(row.get("side_correct"))
        p = priority.maybe_float(row.get(key))
        if y is None or p is None:
            continue
        labels.append(float(y))
        scores.append(clamp(float(p)))
    return np.array(labels, dtype=float), np.array(scores, dtype=float)


def log_loss_np(y: np.ndarray, p: np.ndarray) -> float:
    p = np.clip(p, 1e-6, 1.0 - 1e-6)
    return float(np.mean(-(y * np.log(p) + (1.0 - y) * np.log(1.0 - p))))


def brier_np(y: np.ndarray, p: np.ndarray) -> float:
    return float(np.mean((p - y) ** 2))


def fit_temperature(y: np.ndarray, p: np.ndarray) -> dict[str, Any]:
    z = logit(np.clip(p, 1e-6, 1.0 - 1e-6))

    def objective(t: float) -> float:
        pred = expit(z / t)
        return log_loss_np(y, pred) + 0.001 * (math.log(t) ** 2)

    res = minimize_scalar(objective, bounds=(0.05, 10.0), method="bounded")
    temp = float(res.x)
    return {
        "model_type": "temperature",
        "temperature": temp,
        "success": bool(res.success),
        "train_objective": float(res.fun),
    }


def apply_temperature(model: dict[str, Any], p: float) -> float:
    t = max(0.05, float(model.get("temperature") or 1.0))
    return clamp(float(expit(logit(clamp(p)) / t)))


def beta_features(p: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    p = np.clip(p, 1e-6, 1.0 - 1e-6)
    return np.log(p), -np.log1p(-p)


def fit_beta(y: np.ndarray, p: np.ndarray, *, include_intercept: bool) -> dict[str, Any]:
    x1, x2 = beta_features(p)
    if include_intercept:
        start = np.array([1.0, 1.0, 0.0])
        bounds = [(0.0, 10.0), (0.0, 10.0), (-10.0, 10.0)]
    else:
        start = np.array([1.0, 1.0])
        bounds = [(0.0, 10.0), (0.0, 10.0)]

    def predict(params: np.ndarray) -> np.ndarray:
        if include_intercept:
            a, b, c = params
        else:
            a, b = params
            c = 0.0
        return expit(a * x1 + b * x2 + c)

    def objective(params: np.ndarray) -> float:
        identity = np.array([1.0, 1.0, 0.0]) if include_intercept else np.array([1.0, 1.0])
        return log_loss_np(y, predict(params)) + 0.001 * float(np.sum((params - identity) ** 2))

    res = minimize(objective, start, method="L-BFGS-B", bounds=bounds)
    params = np.array(res.x, dtype=float)
    return {
        "model_type": "beta3" if include_intercept else "beta2",
        "a": float(params[0]),
        "b": float(params[1]),
        "c": float(params[2]) if include_intercept else 0.0,
        "success": bool(res.success),
        "train_objective": float(res.fun),
    }


def apply_beta(model: dict[str, Any], p: float) -> float:
    x1 = math.log(clamp(p))
    x2 = -math.log1p(-clamp(p))
    z = float(model.get("a") or 0.0) * x1 + float(model.get("b") or 0.0) * x2 + float(model.get("c") or 0.0)
    return clamp(float(expit(z)))


def apply_model(model: dict[str, Any], p: float) -> float:
    if model.get("model_type") == "temperature":
        return apply_temperature(model, p)
    return apply_beta(model, p)


def probability_scores(rows: list[dict[str, Any]], key: str) -> dict[str, Any]:
    out = {}
    for name, (start, end) in WINDOWS.items():
        chunk = row_window(rows, start, end)
        y, p = label_and_score(chunk, key)
        if len(y) == 0:
            out[name] = {"rows": 0}
            continue
        tau = kendalltau(p, np.arange(len(p))).statistic if len(p) > 2 else None
        out[name] = {
            "rows": int(len(y)),
            "brier": brier_np(y, p),
            "log_loss": log_loss_np(y, p),
            "auc": priority.auc_score([int(v) for v in y.tolist()], [float(v) for v in p.tolist()]),
            "time_rank_kendall_tau": None if tau is None or math.isnan(float(tau)) else float(tau),
        }
    return out


def fit_recalibrators(rows: list[dict[str, Any]]) -> dict[str, Any]:
    train = row_window(rows, 1, 200)
    out: dict[str, Any] = {}
    for source_key in SOURCE_KEYS:
        y, p = label_and_score(train, source_key)
        if len(y) < 50:
            continue
        for model in (
            fit_temperature(y, p),
            fit_beta(y, p, include_intercept=False),
            fit_beta(y, p, include_intercept=True),
        ):
            name = f"{model['model_type']}_{source_key}"
            key = f"p_{name}"
            values = []
            source_values = []
            calibrated_values = []
            for row in rows:
                raw = priority.maybe_float(row.get(source_key))
                if raw is None:
                    values.append(None)
                    continue
                p_cal = apply_model(model, float(raw))
                values.append(p_cal)
                source_values.append(float(raw))
                calibrated_values.append(p_cal)
            for row, value in zip(rows, values):
                row[key] = value
            tau = kendalltau(source_values, calibrated_values).statistic if len(source_values) > 2 else None
            out[name] = {
                "output_key": key,
                "source_key": source_key,
                "model": model,
                "rank_preservation_kendall_tau": None if tau is None or math.isnan(float(tau)) else float(tau),
                "scores": probability_scores(rows, key),
            }
    out["locked_capped_aci"] = {
        "output_key": "p_calibrated",
        "source_key": "brownian_terminal_p_side",
        "model": {"model_type": "capped_aci"},
        "rank_preservation_kendall_tau": None,
        "scores": probability_scores(rows, "p_calibrated"),
    }
    out["raw_p28"] = {"output_key": "p28", "source_key": "p28", "model": {"model_type": "raw"}, "scores": probability_scores(rows, "p28")}
    out["raw_brownian"] = {
        "output_key": "brownian_terminal_p_side",
        "source_key": "brownian_terminal_p_side",
        "model": {"model_type": "raw"},
        "scores": probability_scores(rows, "brownian_terminal_p_side"),
    }
    return out


def pnl_table_for_score(rows: list[dict[str, Any]], key: str) -> dict[str, Any]:
    out = {}
    for threshold in P_THRESHOLDS:
        name = f"robust_plus_{key}_ge_{threshold:.2f}"
        predicate = lambda row, t=threshold: priority.robust_hybrid(row) and fnum(row.get(key), -1.0) >= t
        windows = {}
        for window_name, (start, end) in WINDOWS.items():
            chunk = row_window(rows, start, end)
            chosen = selected(chunk, predicate)
            windows[window_name] = stats(chosen, len(chunk))
        out[name] = {"score_key": key, "threshold": threshold, "windows": windows}
    return out


def wilson_upper(losses: int, n: int, z: float = 1.64) -> float | None:
    if n <= 0:
        return None
    phat = losses / n
    denom = 1.0 + z * z / n
    centre = phat + z * z / (2.0 * n)
    margin = z * math.sqrt((phat * (1.0 - phat) + z * z / (4.0 * n)) / n)
    return (centre + margin) / denom


def loss_rate(rows: list[dict[str, Any]]) -> dict[str, Any]:
    losses = sum(1 for row in rows if fnum(row.get("pnl_cents")) < 0.0)
    wins = sum(1 for row in rows if fnum(row.get("pnl_cents")) > 0.0)
    flats = sum(1 for row in rows if fnum(row.get("pnl_cents")) == 0.0)
    n = len(rows)
    return {
        "rows": n,
        "wins": wins,
        "losses": losses,
        "flats": flats,
        "loss_rate": losses / (wins + losses) if wins + losses else None,
        "loss_rate_including_flats": losses / n if n else None,
        "wilson_loss_rate_upper_95": wilson_upper(losses, wins + losses),
    }


def rcps_threshold_for_score(
    rows: list[dict[str, Any]],
    key: str,
    alpha: float,
    *,
    base_predicate: Predicate | None = None,
    min_train_entries: int = 20,
) -> dict[str, Any]:
    train = row_window(rows, 1, 200)
    base = base_predicate or (lambda row: True)
    train_scores = sorted({fnum(row.get(key), -1.0) for row in train if row.get(key) is not None and base(row)})
    candidates = []
    for threshold in train_scores:
        chosen = [row for row in train if base(row) and fnum(row.get(key), -1.0) >= threshold]
        if len(chosen) < min_train_entries:
            continue
        risk = loss_rate(chosen)
        if fnum(risk.get("loss_rate"), 1.0) <= alpha:
            train_stats = stats(chosen, len(train))
            candidates.append(
                {
                    "threshold": threshold,
                    "train_entries": len(chosen),
                    "train_loss_rate": risk.get("loss_rate"),
                    "train_wilson_upper_95": risk.get("wilson_loss_rate_upper_95"),
                    "train_avg_cents": train_stats.get("avg_cents_per_entry"),
                    "train_net_dollars": train_stats.get("net_dollars"),
                }
            )
    if not candidates:
        return {"score_key": key, "alpha": alpha, "selected": None, "reason": "no train threshold met risk and count constraints"}
    candidates.sort(key=lambda row: (row["train_entries"], fnum(row.get("train_avg_cents"))), reverse=True)
    locked = candidates[0]
    threshold = float(locked["threshold"])
    predicate = lambda row: base(row) and fnum(row.get(key), -1.0) >= threshold
    windows = {}
    for window_name, (start, end) in WINDOWS.items():
        chunk = row_window(rows, start, end)
        chosen = selected(chunk, predicate)
        row_stats = stats(chosen, len(chunk))
        row_stats.update({f"risk_{k}": v for k, v in loss_rate(chosen).items()})
        windows[window_name] = row_stats
    return {
        "score_key": key,
        "alpha": alpha,
        "selected": locked,
        "candidate_count": len(candidates),
        "windows": windows,
        "passes_truffle_gate": bool(
            fnum((windows.get("forward_after_200") or {}).get("coverage_of_live_entries")) >= 0.20
            and fnum((windows.get("forward_after_200") or {}).get("win_rate_ex_flats")) >= 0.55
            and fnum((windows.get("forward_after_200") or {}).get("avg_cents_per_entry")) > 0.0
            and fnum((windows.get("forward_after_200") or {}).get("risk_loss_rate"), 1.0) <= alpha
        ),
    }


def rcps_report(rows: list[dict[str, Any]], score_keys: list[str]) -> dict[str, Any]:
    variants = {}
    for key in score_keys:
        for alpha in ALPHA_TARGETS:
            variants[f"all_{key}_alpha_{alpha:.2f}"] = rcps_threshold_for_score(rows, key, alpha)
            variants[f"robust_{key}_alpha_{alpha:.2f}"] = rcps_threshold_for_score(rows, key, alpha, base_predicate=priority.robust_hybrid)
    return variants


def e_process_path(values: list[float], lam: float, scale: float = 200.0) -> dict[str, Any]:
    capital = 1.0
    max_capital = 1.0
    crosses = {str(int(threshold)): None for threshold in E_PROCESS_THRESHOLDS}
    for idx, value in enumerate(values, start=1):
        clipped = max(-0.95 / lam, min(0.95 / lam, value / scale))
        capital *= 1.0 + lam * clipped
        max_capital = max(max_capital, capital)
        for threshold in E_PROCESS_THRESHOLDS:
            key = str(int(threshold))
            if crosses[key] is None and capital >= threshold:
                crosses[key] = idx
    return {"lambda": lam, "final_capital": capital, "max_capital": max_capital, "cross_at": crosses}


def e_process_for_strategy(rows: list[dict[str, Any]], predicate: Predicate) -> dict[str, Any]:
    out = {}
    for window_name in ("train_1_200", "forward_after_200", "all"):
        start, end = WINDOWS[window_name]
        chosen = selected(row_window(rows, start, end), predicate)
        values = [fnum(row.get("pnl_cents")) for row in chosen]
        paths = [e_process_path(values, lam) for lam in E_PROCESS_LAMBDAS]
        best = max(paths, key=lambda row: fnum(row.get("max_capital"))) if paths else {}
        out[window_name] = {
            "entries": len(chosen),
            "net_dollars": sum(values) / 100.0,
            "best_by_max_capital": best,
            "crossed_20": any((path.get("cross_at") or {}).get("20") is not None for path in paths),
            "crossed_100": any((path.get("cross_at") or {}).get("100") is not None for path in paths),
        }
    return out


def best_forward_overlays(rows: list[dict[str, Any]], pnl_tables: dict[str, Any]) -> list[dict[str, Any]]:
    candidates = []
    for model_name, table in pnl_tables.items():
        for strategy_name, result in table.items():
            train = (result.get("windows") or {}).get("train_1_200") or {}
            forward = (result.get("windows") or {}).get("forward_after_200") or {}
            if fnum(train.get("avg_cents_per_entry")) <= 0 or fnum(forward.get("entries")) < 10:
                continue
            candidates.append(
                {
                    "model_name": model_name,
                    "strategy_name": strategy_name,
                    "score_key": result.get("score_key"),
                    "threshold": result.get("threshold"),
                    "train": train,
                    "forward_after_200": forward,
                    "score": (fnum(forward.get("net_dollars")), fnum(forward.get("avg_cents_per_entry")), fnum(forward.get("entries"))),
                }
            )
    candidates.sort(key=lambda row: row["score"], reverse=True)
    return candidates[:15]


def score_split_rows(
    train_rows: list[dict[str, Any]],
    test_rows: list[dict[str, Any]],
    candidate_name: str,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], dict[str, Any]]:
    train = [dict(row) for row in train_rows]
    test = [dict(row) for row in test_rows]
    meta: dict[str, Any] = {"candidate": candidate_name}
    if candidate_name == "aci_p_calibrated":
        for row in train + test:
            row["wf_score"] = row.get("p_calibrated")
        return train, test, meta
    if candidate_name == "raw_brownian":
        for row in train + test:
            row["wf_score"] = row.get("brownian_terminal_p_side")
        return train, test, meta

    y, p = label_and_score(train, "brownian_terminal_p_side")
    if candidate_name == "beta2_brownian":
        model = fit_beta(y, p, include_intercept=False)
    elif candidate_name == "beta3_brownian":
        model = fit_beta(y, p, include_intercept=True)
    elif candidate_name == "temperature_brownian":
        model = fit_temperature(y, p)
    else:
        raise ValueError(f"unknown WFA candidate {candidate_name}")
    meta["model"] = model
    for row in train + test:
        raw = priority.maybe_float(row.get("brownian_terminal_p_side"))
        row["wf_score"] = apply_model(model, raw) if raw is not None else None
    return train, test, meta


def choose_train_threshold(rows: list[dict[str, Any]], min_entries: int = 10) -> dict[str, Any] | None:
    candidates = []
    for threshold in P_THRESHOLDS:
        chosen = [row for row in rows if priority.robust_hybrid(row) and fnum(row.get("wf_score"), -1.0) >= threshold]
        if len(chosen) < min_entries:
            continue
        row_stats = stats(chosen, len(rows))
        if fnum(row_stats.get("avg_cents_per_entry")) <= 0.0:
            continue
        candidates.append(
            {
                "threshold": threshold,
                "entries": len(chosen),
                "net_dollars": row_stats.get("net_dollars"),
                "avg_cents_per_entry": row_stats.get("avg_cents_per_entry"),
                "win_rate_ex_flats": row_stats.get("win_rate_ex_flats"),
                "score": (
                    fnum(row_stats.get("net_dollars")),
                    fnum(row_stats.get("avg_cents_per_entry")),
                    len(chosen),
                ),
            }
        )
    if not candidates:
        return None
    candidates.sort(key=lambda row: row["score"], reverse=True)
    return candidates[0]


def walk_forward_threshold_tests(rows: list[dict[str, Any]]) -> dict[str, Any]:
    candidate_names = ("aci_p_calibrated", "raw_brownian", "beta2_brownian", "beta3_brownian", "temperature_brownian")
    by_candidate: dict[str, dict[str, Any]] = {
        name: {"selected_rows": [], "test_denominator": 0, "windows": []} for name in candidate_names
    }
    for split_idx, (train_start, train_end, test_start, test_end) in enumerate(WFA_SPLITS, start=1):
        train_base = row_window(rows, train_start, train_end)
        test_base = row_window(rows, test_start, test_end)
        for candidate_name in candidate_names:
            train, test, meta = score_split_rows(train_base, test_base, candidate_name)
            lock = choose_train_threshold(train)
            window: dict[str, Any] = {
                "split_idx": split_idx,
                "train_start": train_start,
                "train_end": train_end,
                "test_start": test_start,
                "test_end": test_end,
                "test_rows": len(test),
                "lock": lock,
                "model": meta.get("model"),
            }
            by_candidate[candidate_name]["test_denominator"] += len(test)
            if lock is None:
                window["test"] = stats([], len(test))
                by_candidate[candidate_name]["windows"].append(window)
                continue
            threshold = float(lock["threshold"])
            chosen_test = [row for row in test if priority.robust_hybrid(row) and fnum(row.get("wf_score"), -1.0) >= threshold]
            window["test"] = stats(chosen_test, len(test))
            by_candidate[candidate_name]["selected_rows"].extend(chosen_test)
            by_candidate[candidate_name]["windows"].append(window)

    out = {}
    for candidate_name, row in by_candidate.items():
        selected_rows = row.pop("selected_rows")
        denominator = int(row.get("test_denominator") or 0)
        window_stats = [window.get("test") or {} for window in row.get("windows") or []]
        out[candidate_name] = {
            **row,
            "aggregate": stats(selected_rows, denominator),
            "positive_windows": sum(1 for item in window_stats if fnum(item.get("net_dollars")) > 0.0),
            "windows_with_trades": sum(1 for item in window_stats if fnum(item.get("entries")) > 0.0),
        }
    return out


def build_report() -> dict[str, Any]:
    rows, diagnostics, locked, deep_report = aci_projection.annotate_rows()
    recalibrators = fit_recalibrators(rows)
    score_keys = [
        "p_calibrated",
        "p_beta2_brownian_terminal_p_side",
        "p_beta3_brownian_terminal_p_side",
        "p_temperature_brownian_terminal_p_side",
        "p_beta2_p28",
        "p_beta3_p28",
        "p_temperature_p28",
    ]
    pnl_tables = {name: pnl_table_for_score(rows, row["output_key"]) for name, row in recalibrators.items() if row.get("output_key") in score_keys}
    best_overlays = best_forward_overlays(rows, pnl_tables)
    rcps = rcps_report(rows, score_keys)
    eproc = {
        "robust_hybrid_base": e_process_for_strategy(rows, priority.robust_hybrid),
        "aci_robust_plus_p_cal_ge_0.80": e_process_for_strategy(
            rows, lambda row: priority.robust_hybrid(row) and fnum(row.get("p_calibrated"), -1.0) >= 0.80
        ),
    }
    for candidate in best_overlays[:5]:
        key = str(candidate.get("score_key"))
        threshold = float(candidate.get("threshold"))
        eproc[candidate["strategy_name"]] = e_process_for_strategy(
            rows, lambda row, k=key, t=threshold: priority.robust_hybrid(row) and fnum(row.get(k), -1.0) >= t
        )
    return {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "purpose": "Research-only beta/temperature calibration and RCPS-style threshold probe.",
        "diagnostics": diagnostics,
        "locked_aci_calibrator": locked,
        "deep_report_generated_at_utc": deep_report.get("generated_at_utc"),
        "recalibrators": recalibrators,
        "pnl_tables": pnl_tables,
        "best_forward_overlays": best_overlays,
        "walk_forward_thresholds": walk_forward_threshold_tests(rows),
        "rcps": rcps,
        "e_process": eproc,
        "read": [
            "Beta/temperature models are fit only on rows 1-200.",
            "RCPS-style thresholds are selected only on rows 1-200, then evaluated forward.",
            "The RCPS implementation controls observed train loss rate, not a formal finite-sample conformal bound; Wilson upper bounds are reported to expose small-sample fragility.",
            "All PnL is replay over recorded filled trades, not skipped opportunities.",
        ],
    }


def money(value: Any) -> str:
    parsed = priority.maybe_float(value)
    return "n/a" if parsed is None else f"${parsed:,.2f}"


def cents(value: Any) -> str:
    parsed = priority.maybe_float(value)
    return "n/a" if parsed is None else f"{parsed:,.1f}c"


def pct(value: Any) -> str:
    parsed = priority.maybe_float(value)
    return "n/a" if parsed is None else f"{100.0 * parsed:.1f}%"


def num(value: Any, digits: int = 4) -> str:
    parsed = priority.maybe_float(value)
    return "n/a" if parsed is None else f"{parsed:.{digits}f}"


def wl(row: dict[str, Any]) -> str:
    flats = int(row.get("flats") or 0)
    suffix = f" (+{flats} flat)" if flats else ""
    return f"{int(row.get('wins') or 0)}/{int(row.get('losses') or 0)}{suffix}"


def write_md(report: dict[str, Any]) -> None:
    lines = [
        "# Probability Recalibration: Beta, Temperature, RCPS",
        "",
        "Research-only probe over recorded v28 filled trades. No live bot logic changed.",
        "",
        f"- Generated UTC: `{report.get('generated_at_utc')}`",
        f"- Matched trades: `{(report.get('diagnostics') or {}).get('matched_trade_count')}`",
        f"- Settled labels: `{(report.get('diagnostics') or {}).get('settled_label_rows')}`",
        "",
        "## Calibration Scores",
        "",
        "| model | source | window | rows | Brier | log loss | AUC | rank tau | passes Truffle score gate |",
        "|---|---|---|---:|---:|---:|---:|---:|---|",
    ]
    for name, row in report.get("recalibrators", {}).items():
        if name.startswith("raw_"):
            continue
        scores = row.get("scores") or {}
        for window in ("train_1_200", "validation_201_400", "holdout_401_end", "forward_after_200", "all"):
            score = scores.get(window) or {}
            passes = bool(
                window == "forward_after_200"
                and fnum(score.get("brier"), 99.0) < 0.165
                and fnum(score.get("log_loss"), 99.0) < 0.50
                and fnum(row.get("rank_preservation_kendall_tau"), 0.0) > 0.5
            )
            lines.append(
                f"| {name} | {row.get('source_key')} | {window} | {score.get('rows')} | "
                f"{num(score.get('brier'))} | {num(score.get('log_loss'))} | {num(score.get('auc'), 3)} | "
                f"{num(row.get('rank_preservation_kendall_tau'), 3)} | {passes} |"
            )
    lines.extend(
        [
            "",
            "## Best Forward Robust Overlays",
            "",
            "| rank | strategy | train W/L | train PnL | train avg | forward W/L | forward PnL | forward avg | forward coverage |",
            "|---:|---|---:|---:|---:|---:|---:|---:|---:|",
        ]
    )
    for idx, row in enumerate(report.get("best_forward_overlays") or [], start=1):
        train = row.get("train") or {}
        forward = row.get("forward_after_200") or {}
        lines.append(
            f"| {idx} | {row.get('strategy_name')} | {wl(train)} | {money(train.get('net_dollars'))} | "
            f"{cents(train.get('avg_cents_per_entry'))} | {wl(forward)} | {money(forward.get('net_dollars'))} | "
            f"{cents(forward.get('avg_cents_per_entry'))} | {pct(forward.get('coverage_of_live_entries'))} |"
        )
    lines.extend(
        [
            "",
            "## Rolling Walk-Forward Thresholds",
            "",
            "Each split fits/calibrates on a 200-row train window, picks the robust overlay threshold from train PnL only, then evaluates the next slice.",
            "",
            "| candidate | test entries | W/L | PnL | avg/entry | coverage | positive windows | windows with trades | locked thresholds |",
            "|---|---:|---:|---:|---:|---:|---:|---:|---|",
        ]
    )
    for name, row in (report.get("walk_forward_thresholds") or {}).items():
        agg = row.get("aggregate") or {}
        thresholds = [
            (window.get("lock") or {}).get("threshold")
            for window in row.get("windows") or []
            if window.get("lock") is not None
        ]
        lines.append(
            f"| {name} | {agg.get('entries')} | {wl(agg)} | {money(agg.get('net_dollars'))} | "
            f"{cents(agg.get('avg_cents_per_entry'))} | {pct(agg.get('coverage_of_live_entries'))} | "
            f"{row.get('positive_windows')}/4 | {row.get('windows_with_trades')}/4 | `{thresholds}` |"
        )
    lines.extend(
        [
            "",
            "## RCPS-Style Thresholds",
            "",
            "| variant | selected threshold | train loss | train Wilson upper | forward entries | forward W/L | forward loss | forward PnL | forward avg | passes gate |",
            "|---|---:|---:|---:|---:|---:|---:|---:|---:|---|",
        ]
    )
    for name, row in report.get("rcps", {}).items():
        selected_row = row.get("selected") or {}
        forward = ((row.get("windows") or {}).get("forward_after_200") or {})
        if row.get("selected") is None and "_alpha_0.20" not in name:
            continue
        if row.get("selected") is None:
            lines.append(f"| {name} | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | False |")
            continue
        lines.append(
            f"| {name} | {num(selected_row.get('threshold'), 4)} | {pct(selected_row.get('train_loss_rate'))} | "
            f"{pct(selected_row.get('train_wilson_upper_95'))} | {forward.get('entries')} | {wl(forward)} | "
            f"{pct(forward.get('risk_loss_rate'))} | {money(forward.get('net_dollars'))} | "
            f"{cents(forward.get('avg_cents_per_entry'))} | {row.get('passes_truffle_gate')} |"
        )
    lines.extend(
        [
            "",
            "## E-Process",
            "",
            "| strategy | window | entries | best lambda | final capital | max capital | crossed 20 | crossed 100 |",
            "|---|---|---:|---:|---:|---:|---|---|",
        ]
    )
    for name, windows in (report.get("e_process") or {}).items():
        for window in ("train_1_200", "forward_after_200", "all"):
            row = windows.get(window) or {}
            best = row.get("best_by_max_capital") or {}
            lines.append(
                f"| {name} | {window} | {row.get('entries')} | {num(best.get('lambda'), 2)} | "
                f"{num(best.get('final_capital'), 2)} | {num(best.get('max_capital'), 2)} | "
                f"{'yes' if row.get('crossed_20') else 'no'} | {'yes' if row.get('crossed_100') else 'no'} |"
            )
    lines.extend(
        [
            "",
            "## Read",
            "",
            "- Beta and temperature calibration are useful comparators, but their forward score gate must beat the locked capped-ACI candidate before replacing it.",
            "- RCPS with a strict 20% loss target is expected to be too conservative for this payoff stream; higher alpha rows are diagnostic only.",
            "- Any attractive replay overlay still needs fresh shadow accumulation because the e-process gate is the promotion brake.",
        ]
    )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    report = build_report()
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8")
    write_md(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
