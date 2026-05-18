"""Priority tests from the latest Truffle synthesis.

Research-only. This script tests the concrete recommendations that can be
evaluated with the current v28 logs:

- self-calibrating / rolling isotonic probability calibration
- ACI-style online bias and coverage adjustment
- S-CRC-style rolling selective risk control with target risk
- stricter e-process checks for the robust hybrid gate
- sparse IOC fill probability baseline vs extended logistic model
- partial post-fill BTC adverse-selection diagnostic where cached bars exist

It writes reports under logs/edge_research and never touches live order logic.
"""
from __future__ import annotations

import csv
import json
import math
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from statistics import mean, median
from typing import Any, Callable

import probe_arxiv_strategy_projection as projection
import probe_arxiv_strategy_promotion_gates as gates
import probe_arxiv_strategy_remaining_ideas as remaining


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
OUT_JSON = OUT_DIR / "arxiv_strategy_priority_tests_latest.json"
OUT_MD = OUT_DIR / "arxiv_strategy_priority_tests_latest.md"
SHADOW_SCHEMA_MD = OUT_DIR / "v28_forward_shadow_registry_schema_latest.md"
SHADOW_SCHEMA_CSV = OUT_DIR / "v28_forward_shadow_registry_columns_latest.csv"

Predicate = Callable[[dict[str, Any]], bool]


def fnum(value: Any, default: float = 0.0) -> float:
    parsed = projection.as_float(value)
    return default if parsed is None else parsed


def maybe_float(value: Any) -> float | None:
    return projection.as_float(value)


def clamp(value: float, low: float = 1e-6, high: float = 1.0 - 1e-6) -> float:
    return min(high, max(low, value))


def logit(p: float) -> float:
    p = clamp(p)
    return math.log(p / (1.0 - p))


def sigmoid(x: float) -> float:
    if x >= 0:
        z = math.exp(-x)
        return 1.0 / (1.0 + z)
    z = math.exp(x)
    return z / (1.0 + z)


def normal_cdf(x: float) -> float:
    return 0.5 * (1.0 + math.erf(x / math.sqrt(2.0)))


def ge(value: Any, threshold: float) -> bool:
    parsed = maybe_float(value)
    return parsed is not None and parsed >= threshold


def le(value: Any, threshold: float) -> bool:
    parsed = maybe_float(value)
    return parsed is not None and parsed <= threshold


def between(value: Any, low: float, high: float) -> bool:
    parsed = maybe_float(value)
    return parsed is not None and low <= parsed <= high


def selected(rows: list[dict[str, Any]], predicate: Predicate) -> list[dict[str, Any]]:
    return [row for row in rows if predicate(row)]


def stats(rows: list[dict[str, Any]], denominator: int) -> dict[str, Any]:
    return projection.trade_stats(rows, denominator)


def net_cents(rows: list[dict[str, Any]]) -> float:
    return sum(fnum(row.get("pnl_cents")) for row in rows)


def quantile(values: list[float], q: float) -> float | None:
    if not values:
        return None
    ordered = sorted(values)
    idx = int(round((len(ordered) - 1) * q))
    return ordered[min(len(ordered) - 1, max(0, idx))]


def pearson(xs: list[float], ys: list[float]) -> float | None:
    if len(xs) < 3 or len(xs) != len(ys):
        return None
    mx = mean(xs)
    my = mean(ys)
    vx = sum((x - mx) ** 2 for x in xs)
    vy = sum((y - my) ** 2 for y in ys)
    if vx <= 0 or vy <= 0:
        return None
    return sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / math.sqrt(vx * vy)


def ranks(values: list[float]) -> list[float]:
    indexed = sorted(enumerate(values), key=lambda item: item[1])
    out = [0.0] * len(values)
    i = 0
    while i < len(indexed):
        j = i + 1
        while j < len(indexed) and indexed[j][1] == indexed[i][1]:
            j += 1
        rank = (i + j - 1) / 2.0
        for k in range(i, j):
            out[indexed[k][0]] = rank
        i = j
    return out


def spearman(xs: list[float], ys: list[float]) -> float | None:
    if len(xs) < 3 or len(xs) != len(ys):
        return None
    return pearson(ranks(xs), ranks(ys))


def probability_scores(rows: list[dict[str, Any]], key: str, *, start: int = 1, end: int | None = None) -> dict[str, Any]:
    usable: list[tuple[float, float]] = []
    for idx, row in enumerate(rows, start=1):
        if idx < start:
            continue
        if end is not None and idx > end:
            continue
        p = maybe_float(row.get(key))
        y = maybe_float(row.get("side_correct"))
        if p is None or y is None:
            continue
        p = clamp(p)
        usable.append((p, y))
    if not usable:
        return {"rows": 0}
    brier = mean([(p - y) ** 2 for p, y in usable])
    log_loss = mean([-(y * math.log(p) + (1.0 - y) * math.log(1.0 - p)) for p, y in usable])
    return {"rows": len(usable), "brier": brier, "log_loss": log_loss}


def money(value: Any) -> str:
    parsed = maybe_float(value)
    return "n/a" if parsed is None else f"${parsed:,.2f}"


def cents(value: Any) -> str:
    parsed = maybe_float(value)
    return "n/a" if parsed is None else f"{parsed:,.1f}c"


def pct(value: Any) -> str:
    parsed = maybe_float(value)
    return "n/a" if parsed is None else f"{100.0 * parsed:.1f}%"


def wl(row: dict[str, Any]) -> str:
    flats = int(row.get("flats") or 0)
    suffix = f" (+{flats} flat)" if flats else ""
    return f"{int(row.get('wins') or 0)}/{int(row.get('losses') or 0)}{suffix}"


def load_rows() -> tuple[list[dict[str, Any]], dict[str, Any]]:
    rows, diagnostics = remaining.load_detailed_rows()
    enriched = []
    for row in rows:
        row = dict(row)
        btc = maybe_float(row.get("btc_price"))
        strike = maybe_float(row.get("strike"))
        sigma = maybe_float(row.get("sigma_t_dollars"))
        side = str(row.get("side") or "").lower()
        if btc is not None and strike is not None and sigma is not None and sigma > 0:
            p_yes = normal_cdf((btc - strike) / sigma)
            row["brownian_terminal_p_yes"] = p_yes
            row["brownian_terminal_p_side"] = p_yes if side == "yes" else 1.0 - p_yes
        enriched.append(row)
    return enriched, diagnostics


class IsotonicModel:
    def __init__(self, blocks: list[dict[str, float]], fallback: float) -> None:
        self.blocks = blocks
        self.fallback = fallback

    def predict(self, x: float) -> float:
        if not self.blocks:
            return self.fallback
        for block in self.blocks:
            if x <= block["x_max"]:
                return clamp(block["y"])
        return clamp(self.blocks[-1]["y"])


def fit_isotonic(xs: list[float], ys: list[float]) -> IsotonicModel:
    pairs = sorted((x, y) for x, y in zip(xs, ys) if math.isfinite(x) and math.isfinite(y))
    if not pairs:
        return IsotonicModel([], 0.5)
    blocks: list[dict[str, float]] = []
    for x, y in pairs:
        blocks.append({"x_min": x, "x_max": x, "sum_y": y, "count": 1.0, "y": y})
        while len(blocks) >= 2 and blocks[-2]["y"] > blocks[-1]["y"]:
            right = blocks.pop()
            left = blocks.pop()
            merged = {
                "x_min": left["x_min"],
                "x_max": right["x_max"],
                "sum_y": left["sum_y"] + right["sum_y"],
                "count": left["count"] + right["count"],
                "y": 0.0,
            }
            merged["y"] = merged["sum_y"] / merged["count"]
            blocks.append(merged)
    fallback = mean([y for _, y in pairs])
    return IsotonicModel(blocks, fallback)


def rolling_isotonic_calibration(rows: list[dict[str, Any]], window: int, *, key: str = "p28") -> list[float | None]:
    preds: list[float | None] = []
    for idx, row in enumerate(rows):
        p = maybe_float(row.get(key))
        if p is None or idx < window:
            preds.append(None)
            continue
        hist = rows[idx - window : idx]
        xs = [fnum(item.get(key)) for item in hist if item.get(key) is not None and item.get("side_correct") is not None]
        ys = [fnum(item.get("side_correct")) for item in hist if item.get(key) is not None and item.get("side_correct") is not None]
        preds.append(fit_isotonic(xs, ys).predict(p))
    return preds


def fixed_isotonic_apply(rows: list[dict[str, Any]], train_end: int, apply_end: int, *, key: str = "p28") -> list[float | None]:
    train = rows[:train_end]
    xs = [fnum(item.get(key)) for item in train if item.get(key) is not None and item.get("side_correct") is not None]
    ys = [fnum(item.get("side_correct")) for item in train if item.get(key) is not None and item.get("side_correct") is not None]
    model = fit_isotonic(xs, ys)
    out: list[float | None] = []
    for idx, row in enumerate(rows, start=1):
        p = maybe_float(row.get(key))
        if p is None or idx <= train_end or idx > apply_end:
            out.append(None)
        else:
            out.append(model.predict(p))
    return out


def aci_adjusted_probabilities(rows: list[dict[str, Any]], eta: float, *, target_coverage: float = 0.90) -> dict[str, Any]:
    q = 0.50
    bias = 0.0
    alpha = 1.0 - target_coverage
    trace = []
    for idx, row in enumerate(rows, start=1):
        p = maybe_float(row.get("p28"))
        y = maybe_float(row.get("side_correct"))
        if p is None or y is None:
            trace.append({"idx": idx, "p": p, "p_adj": None, "q": q, "covered": None})
            continue
        p_adj = clamp(p + bias)
        score = abs(y - p_adj)
        covered = score <= q
        miss = 0.0 if covered else 1.0
        trace.append({"idx": idx, "p": p, "p_adj": p_adj, "q": q, "covered": covered, "score": score})
        q = clamp(q + eta * (miss - alpha), 0.01, 1.0)
        bias = max(-0.35, min(0.35, bias + eta * (y - p - bias)))
    return {
        "eta": eta,
        "target_coverage": target_coverage,
        "trace": trace,
        "final_q": q,
        "final_bias": bias,
    }


def apply_prediction_column(rows: list[dict[str, Any]], values: list[float | None], key: str) -> list[dict[str, Any]]:
    out = []
    for row, value in zip(rows, values):
        row = dict(row)
        if value is not None:
            row[key] = value
        out.append(row)
    return out


def probability_calibration_report(rows: list[dict[str, Any]]) -> dict[str, Any]:
    working = [dict(row) for row in rows]
    rolling_outputs = {}
    for window in (30, 50, 80, 120):
        values = rolling_isotonic_calibration(working, window)
        key = f"rolling_iso_w{window}"
        working = apply_prediction_column(working, values, key)
        rolling_outputs[key] = {
            "window": window,
            "all_after_warmup": probability_scores(working, key),
            "first_400": probability_scores(working, key, start=window + 1, end=400),
            "rows_201_400": probability_scores(working, key, start=201, end=400),
            "rows_401_600": probability_scores(working, key, start=401, end=600),
            "last_232": probability_scores(working, key, start=401),
        }
    fixed_values = fixed_isotonic_apply(working, 200, 600)
    working = apply_prediction_column(working, fixed_values, "fixed_iso_train200_apply201_600")
    aci_outputs = {}
    for eta in (0.01, 0.03, 0.05, 0.08):
        aci = aci_adjusted_probabilities(working, eta)
        aci_values = [item.get("p_adj") for item in aci["trace"]]
        key = f"aci_bias_eta_{str(eta).replace('.', 'p')}"
        working = apply_prediction_column(working, aci_values, key)
        usable = [item for item in aci["trace"] if item.get("covered") is not None]
        coverage = sum(1 for item in usable if item["covered"]) / len(usable) if usable else None
        first_400 = [item for item in usable if int(item["idx"]) <= 400]
        aci_outputs[key] = {
            "eta": eta,
            "coverage": coverage,
            "first_400_coverage": sum(1 for item in first_400 if item["covered"]) / len(first_400) if first_400 else None,
            "final_q": aci["final_q"],
            "final_bias": aci["final_bias"],
            "all": probability_scores(working, key),
            "first_400": probability_scores(working, key, end=400),
            "last_232": probability_scores(working, key, start=401),
            "passes_aci_gate": bool(
                coverage is not None
                and 0.85 <= coverage <= 0.95
                and probability_scores(working, key).get("brier", 99.0) < probability_scores(working, "p28").get("brier", 0.0)
            ),
        }
    baseline = {
        "raw_v28": {
            "all": probability_scores(working, "p28"),
            "first_400": probability_scores(working, "p28", end=400),
            "rows_201_400": probability_scores(working, "p28", start=201, end=400),
            "rows_401_600": probability_scores(working, "p28", start=401, end=600),
            "last_232": probability_scores(working, "p28", start=401),
        },
        "brownian_terminal": {
            "all": probability_scores(working, "brownian_terminal_p_side"),
            "first_400": probability_scores(working, "brownian_terminal_p_side", end=400),
            "rows_201_400": probability_scores(working, "brownian_terminal_p_side", start=201, end=400),
            "rows_401_600": probability_scores(working, "brownian_terminal_p_side", start=401, end=600),
            "last_232": probability_scores(working, "brownian_terminal_p_side", start=401),
        },
        "fixed_iso_train200_apply201_600": {
            "rows_201_400": probability_scores(working, "fixed_iso_train200_apply201_600", start=201, end=400),
            "rows_201_600": probability_scores(working, "fixed_iso_train200_apply201_600", start=201, end=600),
            "rows_401_600": probability_scores(working, "fixed_iso_train200_apply201_600", start=401, end=600),
        },
    }
    candidates = []
    for name, row in rolling_outputs.items():
        first = row["first_400"]
        candidates.append((fnum(first.get("brier"), 99.0), fnum(first.get("log_loss"), 99.0), name, row))
    for name, row in aci_outputs.items():
        first = row["first_400"]
        candidates.append((fnum(first.get("brier"), 99.0), fnum(first.get("log_loss"), 99.0), name, row))
    candidates.sort()
    best_name = candidates[0][2] if candidates else None
    best_first = candidates[0][3].get("first_400") if candidates else {}
    return {
        "idea": "Self-calibrating probability tests over p28 with rolling isotonic and ACI-style online adjustment.",
        "baselines": baseline,
        "rolling_isotonic": rolling_outputs,
        "aci_bias": aci_outputs,
        "best_first_400_candidate": best_name,
        "best_first_400_scores": best_first,
        "promotion_gate": {"brier_lt": 0.165, "log_loss_lt": 0.50, "window": "first_400"},
        "passes_promotion_gate": bool(fnum(best_first.get("brier"), 99.0) < 0.165 and fnum(best_first.get("log_loss"), 99.0) < 0.50),
        "calibrated_rows": working,
    }


def robust_hybrid(row: dict[str, Any]) -> bool:
    return (
        ge(row.get("edge28_cents"), 3.0)
        and ge(row.get("depth_ratio"), 8.0)
        and le(row.get("book_age_ms"), 750.0)
        and le(row.get("ask_cents"), 85.0)
        and ge(row.get("seconds_to_close"), 120.0)
        and between(row.get("abs_d_sigma"), 0.80, 1.10)
    )


def e_process_on_values(values: list[float], lam: float, scale: float = 200.0, threshold: float = 100.0) -> dict[str, Any]:
    capital = 1.0
    max_capital = 1.0
    cross_at = None
    for idx, value in enumerate(values, start=1):
        x = max(-0.95 / lam, min(0.95 / lam, value / scale))
        factor = 1.0 + lam * x
        capital *= factor
        max_capital = max(max_capital, capital)
        if cross_at is None and capital >= threshold:
            cross_at = idx
    return {"lambda": lam, "final_capital": capital, "max_capital": max_capital, "cross_at": cross_at}


def e_process_report(rows: list[dict[str, Any]]) -> dict[str, Any]:
    selected_rows = [(idx, row) for idx, row in enumerate(rows, start=1) if robust_hybrid(row)]
    all_values = [fnum(row.get("pnl_cents")) for _, row in selected_rows]
    calibration_values = [fnum(row.get("pnl_cents")) for idx, row in selected_rows if idx <= 200]
    oos_values = [fnum(row.get("pnl_cents")) for idx, row in selected_rows if idx > len(rows) - 100]
    lambda_rows = []
    for lam in (0.02, 0.05, 0.10, 0.20, 0.35):
        lambda_rows.append(
            {
                "lambda": lam,
                "full": e_process_on_values(all_values, lam),
                "calibration_first_200": e_process_on_values(calibration_values, lam),
                "oos_last_100": e_process_on_values(oos_values, lam),
            }
        )
    best_oos = max(lambda_rows, key=lambda row: fnum((row.get("oos_last_100") or {}).get("max_capital")))
    crossed_oos = any((row.get("oos_last_100") or {}).get("cross_at") for row in lambda_rows)
    crossed_cal = any((row.get("calibration_first_200") or {}).get("cross_at") for row in lambda_rows)
    return {
        "idea": "Anytime-style e-process check over realized PnL for robust hybrid selected rows.",
        "selected_entries": len(selected_rows),
        "calibration_selected_entries_first_200": len(calibration_values),
        "oos_selected_entries_last_100": len(oos_values),
        "threshold": 100.0,
        "lambda_rows": lambda_rows,
        "best_oos_lambda": best_oos["lambda"],
        "best_oos_max_capital": (best_oos.get("oos_last_100") or {}).get("max_capital"),
        "passes_gate": bool(crossed_oos and not crossed_cal),
        "read": "Pass requires a threshold crossing in last-100 OOS and no crossing in first-200 calibration.",
    }


def score_for_row(row: dict[str, Any], score_name: str) -> float | None:
    if score_name == "edge28_cents":
        return maybe_float(row.get("edge28_cents"))
    if score_name == "depth_ratio":
        return maybe_float(row.get("depth_ratio"))
    if score_name == "brownian_terminal_p_side":
        return maybe_float(row.get("brownian_terminal_p_side"))
    if score_name == "absd_band_quality":
        absd = maybe_float(row.get("abs_d_sigma"))
        if absd is None:
            return None
        return -abs(absd - 0.95)
    if score_name == "hybrid_manual_score":
        if not robust_hybrid(row):
            return None
        return fnum(row.get("edge28_cents")) + min(20.0, fnum(row.get("depth_ratio"))) / 5.0
    return None


def scrc_rolling_selector(
    rows: list[dict[str, Any]],
    score_name: str,
    *,
    target_avg_cents: float = -0.5,
    warmup: int = 200,
    window: int = 200,
    min_cal_selected: int = 30,
) -> dict[str, Any]:
    accepted = []
    threshold_trace = []
    for idx, row in enumerate(rows):
        if idx < warmup:
            continue
        cal = rows[max(0, idx - window) : idx]
        scored_cal = [(score_for_row(item, score_name), fnum(item.get("pnl_cents"))) for item in cal]
        scored_cal = [(score, pnl) for score, pnl in scored_cal if score is not None]
        if len(scored_cal) < min_cal_selected:
            continue
        score_values = [score for score, _ in scored_cal]
        thresholds = sorted({quantile(score_values, q) for q in (0.0, 0.10, 0.20, 0.30, 0.40, 0.50, 0.60, 0.70, 0.80) if quantile(score_values, q) is not None})
        viable = []
        for threshold in thresholds:
            selected_cal = [pnl for score, pnl in scored_cal if score >= threshold]
            if len(selected_cal) < min_cal_selected:
                continue
            avg = mean(selected_cal)
            if avg >= target_avg_cents:
                viable.append((len(selected_cal), -threshold, threshold, avg))
        if not viable:
            continue
        viable.sort(reverse=True)
        _, _, threshold, cal_avg = viable[0]
        score = score_for_row(row, score_name)
        if score is not None and score >= threshold:
            accepted.append(row)
            threshold_trace.append({"idx": idx + 1, "threshold": threshold, "cal_avg_cents": cal_avg, "score": score})
    accepted_stats = stats(accepted, len(rows))
    return {
        "score_name": score_name,
        "target_avg_cents": target_avg_cents,
        "warmup": warmup,
        "window": window,
        "accepted": accepted_stats,
        "accepted_fraction": len(accepted) / len(rows) if rows else None,
        "passes_gate": bool((len(accepted) / len(rows) if rows else 0.0) > 0.30 and fnum(accepted_stats.get("avg_cents_per_entry")) > 0),
        "threshold_trace_tail": threshold_trace[-10:],
    }


def scrc_report(rows: list[dict[str, Any]]) -> dict[str, Any]:
    score_names = ["edge28_cents", "depth_ratio", "brownian_terminal_p_side", "absd_band_quality", "hybrid_manual_score"]
    variants = [scrc_rolling_selector(rows, score_name) for score_name in score_names]
    return {
        "idea": "Rolling S-CRC-style selection with target average risk >= -0.5c per accepted trade.",
        "target_risk_cents": -0.5,
        "baseline_robust_hybrid": stats(selected(rows, robust_hybrid), len(rows)),
        "variants": variants,
    }


def auc_score(labels: list[int], scores: list[float]) -> float | None:
    if len(labels) != len(scores) or not labels:
        return None
    positives = sum(labels)
    negatives = len(labels) - positives
    if positives == 0 or negatives == 0:
        return None
    ranked = sorted(zip(scores, labels), key=lambda item: item[0])
    rank_sum_pos = 0.0
    i = 0
    while i < len(ranked):
        j = i + 1
        while j < len(ranked) and ranked[j][0] == ranked[i][0]:
            j += 1
        avg_rank = (i + 1 + j) / 2.0
        for k in range(i, j):
            if ranked[k][1] == 1:
                rank_sum_pos += avg_rank
        i = j
    return (rank_sum_pos - positives * (positives + 1) / 2.0) / (positives * negatives)


def precision_at_recall(labels: list[int], scores: list[float], recall_target: float = 0.50) -> float | None:
    positives = sum(labels)
    if positives <= 0:
        return None
    needed = math.ceil(positives * recall_target)
    tp = 0
    fp = 0
    for score, label in sorted(zip(scores, labels), key=lambda item: item[0], reverse=True):
        if label == 1:
            tp += 1
        else:
            fp += 1
        if tp >= needed:
            return tp / (tp + fp)
    return None


def fill_feature_row(row: dict[str, Any]) -> dict[str, float] | None:
    depth_ratio = maybe_float(row.get("depth_ratio"))
    book_age = maybe_float(row.get("book_age_ms_num"))
    seconds = maybe_float(row.get("seconds_to_close_num"))
    ask = maybe_float(row.get("ask_cents_num"))
    if depth_ratio is None or book_age is None or seconds is None or ask is None:
        return None
    yes_ask = maybe_float(row.get("derived_yes_ask") or row.get("yes_ask_cents"))
    no_ask = maybe_float(row.get("derived_no_ask") or row.get("no_ask_cents"))
    spread_proxy = (yes_ask + no_ask - 100.0) if yes_ask is not None and no_ask is not None else 0.0
    return {
        "log_depth_ratio": math.log1p(max(0.0, depth_ratio)),
        "book_age_s": book_age / 1000.0,
        "seconds_to_close_100s": seconds / 100.0,
        "ask_cents": ask,
        "spread_proxy": spread_proxy,
        "late_x_depth": math.log1p(max(0.0, depth_ratio)) / math.sqrt(max(1.0, seconds)),
    }


def fit_logistic(train_x: list[list[float]], train_y: list[int], *, l2: float = 0.05, iters: int = 1800, lr: float = 0.08) -> dict[str, Any]:
    if not train_x:
        return {"weights": [], "bias": 0.0, "means": [], "stds": []}
    m = len(train_x[0])
    means = [mean([row[j] for row in train_x]) for j in range(m)]
    stds = []
    for j in range(m):
        var = mean([(row[j] - means[j]) ** 2 for row in train_x])
        stds.append(math.sqrt(var) if var > 1e-12 else 1.0)
    xz = [[(row[j] - means[j]) / stds[j] for j in range(m)] for row in train_x]
    prevalence = clamp(sum(train_y) / len(train_y))
    bias = logit(prevalence)
    weights = [0.0] * m
    n = len(train_y)
    for _ in range(iters):
        grad_w = [0.0] * m
        grad_b = 0.0
        for row, y in zip(xz, train_y):
            pred = sigmoid(bias + sum(w * x for w, x in zip(weights, row)))
            err = pred - y
            grad_b += err
            for j in range(m):
                grad_w[j] += err * row[j]
        bias -= lr * grad_b / n
        for j in range(m):
            weights[j] -= lr * ((grad_w[j] / n) + l2 * weights[j])
    return {"weights": weights, "bias": bias, "means": means, "stds": stds}


def logistic_predict(model: dict[str, Any], row: list[float]) -> float:
    weights = model.get("weights") or []
    means = model.get("means") or []
    stds = model.get("stds") or []
    if not weights:
        return 0.5
    z = [(row[j] - means[j]) / stds[j] for j in range(len(weights))]
    return sigmoid(fnum(model.get("bias")) + sum(w * x for w, x in zip(weights, z)))


def fill_model_report() -> dict[str, Any]:
    rows = remaining.load_entry_submit_events()
    feature_names = ["log_depth_ratio", "book_age_s", "seconds_to_close_100s", "ask_cents", "spread_proxy", "late_x_depth"]
    usable = []
    for row in rows:
        features = fill_feature_row(row)
        if features is None:
            continue
        usable.append({"features": features, "label": int(fnum(row.get("filled_any")) > 0), "raw": row})
    train = usable[:-200]
    test = usable[-200:]
    train_x = [[item["features"][name] for name in feature_names] for item in train]
    train_y = [item["label"] for item in train]
    test_x = [[item["features"][name] for name in feature_names] for item in test]
    test_y = [item["label"] for item in test]
    model = fit_logistic(train_x, train_y)
    depth_scores = [item["features"]["log_depth_ratio"] for item in test]
    extended_scores = [logistic_predict(model, row) for row in test_x]
    baseline_auc = auc_score(test_y, depth_scores)
    extended_auc = auc_score(test_y, extended_scores)
    precision_50 = precision_at_recall(test_y, extended_scores, 0.50)
    coefficients = {name: weight for name, weight in zip(feature_names, model.get("weights") or [])}
    return {
        "idea": "Sparse IOC fill model: depth-ratio-only AUC vs regularized logistic model with available fields.",
        "rows": len(usable),
        "train_rows": len(train),
        "test_last_rows": len(test),
        "test_fill_rate": sum(test_y) / len(test_y) if test_y else None,
        "baseline_depth_auc": baseline_auc,
        "extended_auc": extended_auc,
        "auc_improvement": (extended_auc - baseline_auc) if extended_auc is not None and baseline_auc is not None else None,
        "precision_at_50pct_recall": precision_50,
        "coefficients_standardized": coefficients,
        "passes_gate": bool(
            extended_auc is not None
            and baseline_auc is not None
            and extended_auc - baseline_auc > 0.05
            and precision_50 is not None
            and precision_50 > 0.60
        ),
        "missing_for_next_model": ["recent_cancels_1s", "churn_rate", "recent_trades_1s", "true_queue_position", "order_flow_imbalance"],
    }


def post_fill_adverse_selection_report(rows: list[dict[str, Any]]) -> dict[str, Any]:
    df = remaining.load_btc_bars()
    if df is None:
        return {"rows": 0, "reason": "BTC 1m cache unavailable"}
    try:
        import pandas as pd  # type: ignore
    except Exception:
        return {"rows": 0, "reason": "pandas unavailable"}
    cache_min = str(df["open_dt"].min()) if len(df) else None
    cache_max = str(df["open_dt"].max()) if len(df) else None
    row_min = rows[0].get("_entry_dt") if rows else None
    row_max = rows[-1].get("_entry_dt") if rows else None
    usable = []
    for row in rows:
        if fnum(row.get("pnl_cents")) == 0:
            continue
        entry_utc = remaining.row_entry_utc(row)
        btc = maybe_float(row.get("btc_price"))
        side = str(row.get("side") or "").lower()
        if entry_utc is None or btc is None or side not in {"yes", "no"}:
            continue
        target_time = pd.Timestamp(entry_utc) + pd.Timedelta(minutes=5)
        future = df[df["open_dt"] >= target_time]
        if future.empty:
            continue
        future_price = float(future.iloc[0]["close"])
        signed_return = future_price - btc if side == "yes" else btc - future_price
        usable.append(
            {
                "pnl_cents": fnum(row.get("pnl_cents")),
                "depth_ratio": fnum(row.get("depth_ratio")),
                "ask_cents": fnum(row.get("ask_cents")),
                "signed_return_5m_dollars": signed_return,
            }
        )
    if not usable:
        return {
            "rows": 0,
            "btc_cache_min": cache_min,
            "btc_cache_max": cache_max,
            "trade_entry_min": str(row_min) if row_min is not None else None,
            "trade_entry_max": str(row_max) if row_max is not None else None,
            "reason": "No trade has a cached BTC bar at entry+5m in the currently loaded parquet.",
        }
    signed = [row["signed_return_5m_dollars"] for row in usable]
    depth = [row["depth_ratio"] for row in usable]
    ask = [row["ask_cents"] for row in usable]
    pnl = [row["pnl_cents"] for row in usable]
    return {
        "rows": len(usable),
        "btc_cache_min": cache_min,
        "btc_cache_max": cache_max,
        "trade_entry_min": str(row_min) if row_min is not None else None,
        "trade_entry_max": str(row_max) if row_max is not None else None,
        "median_signed_return_5m_dollars": median(signed),
        "depth_vs_signed_return_spearman": spearman(depth, signed),
        "ask_vs_signed_return_spearman": spearman(ask, signed),
        "signed_return_vs_pnl_spearman": spearman(signed, pnl),
        "caveat": "Partial because BTC 1m cache currently ends before the full v28 window.",
    }


def write_shadow_schema() -> None:
    columns = [
        ("decision_ts_utc", "Decision timestamp for every shadow candidate, not just filled trades."),
        ("market", "Kalshi ticker."),
        ("side", "yes/no side considered."),
        ("shadow_candidate", "Frozen candidate id, e.g. hybrid_fpt_depth_robust_rank1."),
        ("shadow_accept", "Whether candidate would trade."),
        ("p28_raw", "Raw v28 side probability."),
        ("p_brownian_terminal", "Terminal Brownian side probability."),
        ("p_calibrated", "Chosen calibrated/shrunk side probability."),
        ("calibrator_id", "Frozen calibrator version/window."),
        ("aci_q", "ACI threshold before outcome."),
        ("aci_bias", "Online bias before outcome."),
        ("edge_cents", "Fee/slippage-adjusted model edge."),
        ("ask_cents", "Executable ask/limit."),
        ("depth_ratio", "eligible_depth / required_depth."),
        ("eligible_depth", "Displayed executable depth."),
        ("depth_required", "Required contracts."),
        ("book_age_ms", "Order book age."),
        ("seconds_to_close", "Seconds to market close at decision."),
        ("abs_d_sigma", "Normalized distance proxy."),
        ("fill_probability", "Forward fill model estimate."),
        ("e_process_value_pre", "Anytime monitor value before decision."),
        ("fill_count", "Observed IOC fill count when sent or simulated as blank."),
        ("target_count", "Intended count."),
        ("settlement_side", "Finalized yes/no label."),
        ("realized_pnl_cents", "Resolved PnL for accepted shadow decision."),
        ("post_fill_return_5m", "Signed BTC move after fill where available."),
    ]
    SHADOW_SCHEMA_CSV.parent.mkdir(parents=True, exist_ok=True)
    with SHADOW_SCHEMA_CSV.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["column", "description"])
        writer.writerows(columns)
    lines = [
        "# v28 Forward Shadow Registry Schema",
        "",
        "Research-only schema for the next forward-shadow registry. This file is not wired into live trading.",
        "",
        "| column | description |",
        "|---|---|",
    ]
    for column, desc in columns:
        lines.append(f"| {column} | {desc} |")
    SHADOW_SCHEMA_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def build_report() -> dict[str, Any]:
    rows, diagnostics = load_rows()
    calibration = probability_calibration_report(rows)
    calibrated_rows = calibration.pop("calibrated_rows")
    report = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "purpose": "Priority tests from latest Truffle synthesis over recorded v28 data.",
        "diagnostics": diagnostics,
        "live_baseline": stats(rows, len(rows)),
        "probability_calibration": calibration,
        "e_process": e_process_report(rows),
        "scrc": scrc_report(rows),
        "fill_model": fill_model_report(),
        "post_fill_adverse_selection": post_fill_adverse_selection_report(rows),
        "shadow_registry_schema": {
            "markdown": str(SHADOW_SCHEMA_MD),
            "csv": str(SHADOW_SCHEMA_CSV),
        },
    }
    write_shadow_schema()
    return report


def write_md(report: dict[str, Any]) -> None:
    cal = report.get("probability_calibration") or {}
    baselines = cal.get("baselines") or {}
    lines = [
        "# arXiv Priority Tests",
        "",
        "Research-only priority tests from the latest Truffle synthesis. These are retrospective diagnostics over recorded v28 data, not live-trading changes.",
        "",
        f"- Generated UTC: `{report.get('generated_at_utc')}`",
        f"- Matched trades: `{report.get('diagnostics', {}).get('matched_trade_count')}`",
        "",
        "## Probability Calibration",
        "",
        "| model | window | rows | Brier | log loss |",
        "|---|---|---:|---:|---:|",
    ]
    for model_name, windows in baselines.items():
        for window_name, row in windows.items():
            lines.append(f"| {model_name} | {window_name} | {row.get('rows')} | {fnum(row.get('brier')):.4f} | {fnum(row.get('log_loss')):.4f} |")
    for model_name, row in (cal.get("rolling_isotonic") or {}).items():
        first = row.get("first_400") or {}
        lines.append(f"| {model_name} | first_400 | {first.get('rows')} | {fnum(first.get('brier')):.4f} | {fnum(first.get('log_loss')):.4f} |")
    for model_name, row in (cal.get("aci_bias") or {}).items():
        first = row.get("first_400") or {}
        lines.append(f"| {model_name} | first_400 | {first.get('rows')} | {fnum(first.get('brier')):.4f} | {fnum(first.get('log_loss')):.4f} |")
    lines.extend(
        [
            "",
            f"- Best first-400 calibration candidate: `{cal.get('best_first_400_candidate')}`.",
            f"- Promotion gate Brier < `0.165` and log loss < `0.50`: `{cal.get('passes_promotion_gate')}`.",
            "",
            "## ACI Coverage",
            "",
            "| model | eta | coverage | first-400 coverage | all Brier | passes ACI gate |",
            "|---|---:|---:|---:|---:|---|",
        ]
    )
    for name, row in (cal.get("aci_bias") or {}).items():
        all_scores = row.get("all") or {}
        lines.append(
            f"| {name} | {row.get('eta')} | {pct(row.get('coverage'))} | {pct(row.get('first_400_coverage'))} | "
            f"{fnum(all_scores.get('brier')):.4f} | {row.get('passes_aci_gate')} |"
        )
    eproc = report.get("e_process") or {}
    lines.extend(
        [
            "",
            "## E-Process",
            "",
            f"- Robust hybrid selected entries: `{eproc.get('selected_entries')}`.",
            f"- First-200 selected entries: `{eproc.get('calibration_selected_entries_first_200')}`.",
            f"- Last-100 selected entries: `{eproc.get('oos_selected_entries_last_100')}`.",
            f"- Pass gate: `{eproc.get('passes_gate')}`.",
            "",
            "| lambda | full max | first-200 max | last-100 max | last-100 cross |",
            "|---:|---:|---:|---:|---|",
        ]
    )
    for row in eproc.get("lambda_rows") or []:
        lines.append(
            f"| {row.get('lambda')} | {fnum((row.get('full') or {}).get('max_capital')):.2f} | "
            f"{fnum((row.get('calibration_first_200') or {}).get('max_capital')):.2f} | "
            f"{fnum((row.get('oos_last_100') or {}).get('max_capital')):.2f} | "
            f"{(row.get('oos_last_100') or {}).get('cross_at')} |"
        )
    scrc = report.get("scrc") or {}
    base = scrc.get("baseline_robust_hybrid") or {}
    lines.extend(
        [
            "",
            "## S-CRC Target Risk",
            "",
            f"- Baseline robust hybrid: `{money(base.get('net_dollars'))}` from `{base.get('entries')}` rows, avg `{cents(base.get('avg_cents_per_entry'))}`.",
            "",
            "| score | accepted | W/L | PnL | avg/entry | accepted share | pass |",
            "|---|---:|---:|---:|---:|---:|---|",
        ]
    )
    for row in scrc.get("variants") or []:
        accepted = row.get("accepted") or {}
        lines.append(
            f"| {row.get('score_name')} | {accepted.get('entries')} | {wl(accepted)} | {money(accepted.get('net_dollars'))} | "
            f"{cents(accepted.get('avg_cents_per_entry'))} | {pct(row.get('accepted_fraction'))} | {row.get('passes_gate')} |"
        )
    fill = report.get("fill_model") or {}
    adverse = report.get("post_fill_adverse_selection") or {}
    lines.extend(
        [
            "",
            "## Fill Model",
            "",
            f"- Rows: `{fill.get('rows')}`; train `{fill.get('train_rows')}`; last-test `{fill.get('test_last_rows')}`.",
            f"- Depth-only AUC: `{fnum(fill.get('baseline_depth_auc')):.3f}`.",
            f"- Extended logistic AUC: `{fnum(fill.get('extended_auc')):.3f}`; improvement `{fnum(fill.get('auc_improvement')):.3f}`.",
            f"- Precision at 50% recall: `{pct(fill.get('precision_at_50pct_recall'))}`.",
            f"- Pass gate: `{fill.get('passes_gate')}`.",
            "",
            "## Post-Fill Adverse Selection",
            "",
            f"- Rows with cached 5m BTC return: `{adverse.get('rows')}`.",
            f"- BTC cache range: `{adverse.get('btc_cache_min')}` to `{adverse.get('btc_cache_max')}`.",
            f"- Trade entry range: `{adverse.get('trade_entry_min')}` to `{adverse.get('trade_entry_max')}`.",
            f"- Median signed 5m return: `{fnum(adverse.get('median_signed_return_5m_dollars')):.2f}` dollars.",
            f"- Depth vs signed 5m return Spearman: `{fnum(adverse.get('depth_vs_signed_return_spearman')):.3f}`.",
            f"- Ask vs signed 5m return Spearman: `{fnum(adverse.get('ask_vs_signed_return_spearman')):.3f}`.",
            "",
            "## Shadow Registry",
            "",
            f"- Schema markdown: `{report.get('shadow_registry_schema', {}).get('markdown')}`.",
            f"- Schema CSV: `{report.get('shadow_registry_schema', {}).get('csv')}`.",
            "",
            "## Read",
            "",
            "- Probability calibration is the immediate lane only if it beats Brownian and clears the strict first-400 gate.",
            "- The e-process is still the hardest promotion blocker because it asks for last-100 evidence without first-200 false discovery.",
            "- The fill model is only promotable if it beats the depth-ratio baseline by more than 0.05 AUC on the chronological last 200 submits.",
            "- The schema files are a forward-shadow registry blueprint, not a live-bot integration.",
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
