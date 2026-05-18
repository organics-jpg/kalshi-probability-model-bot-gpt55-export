"""Train simple diagnostic candidates for the v28 successor FV pipeline.

Research-only. This consumes the leakage-safe feature table produced by
build_v28_successor_features.py, trains only small inspectable challenger
surfaces, and writes calibration/economics artifacts. It does not touch live
bot state, processes, order logic, thresholds, or secrets.

The current seed dataset is posthoc diagnostic evidence, so every candidate
manifest produced here is deliberately marked not promotable unless future
frozen-forward rows are present and pass the gates.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "research_particle" / "v28_successor"
EDGE_DIR = ROOT / "logs" / "edge_research"

FEATURES_CSV = OUT_DIR / "features_latest.csv"
FEATURE_MANIFEST_JSON = OUT_DIR / "feature_manifest_latest.json"
PREDICTIONS_CSV = OUT_DIR / "candidate_predictions_latest.csv"
PREDICTIONS_JSON = OUT_DIR / "candidate_predictions_latest.json"
CANDIDATE_MANIFEST_JSON = OUT_DIR / "candidate_manifests_latest.json"

CALIBRATION_JSON = EDGE_DIR / "v28_successor_calibration_latest.json"
CALIBRATION_MD = EDGE_DIR / "v28_successor_calibration_latest.md"
METRICS_CSV = EDGE_DIR / "v28_successor_calibration_metrics_latest.csv"
BINS_CSV = EDGE_DIR / "v28_successor_calibration_bins_latest.csv"

EPS = 1e-9
MIN_FORWARD_ROWS_FOR_PROMOTION = 200
SHADOW_MIN_EDGE_CENTS = 1.0


def rel_path(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(ROOT)).replace("\\", "/")
    except ValueError:
        return str(path)


def sha256_file(path: Path) -> str | None:
    if not path.exists():
        return None
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def stable_hash(payload: Any) -> str:
    return hashlib.sha256(json.dumps(payload, sort_keys=True, default=str).encode("utf-8")).hexdigest()[:24]


def as_float(value: Any, default: float | None = None) -> float | None:
    if value is None:
        return default
    text = str(value).strip()
    if not text:
        return default
    try:
        out = float(text)
    except ValueError:
        return default
    if not math.isfinite(out):
        return default
    return out


def as_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    text = str(value).strip().lower()
    return text in {"true", "1", "yes", "y"}


def clamp_probability(value: Any) -> float:
    parsed = as_float(value, 0.5)
    assert parsed is not None
    return min(1.0 - EPS, max(EPS, parsed))


def logit(value: Any) -> float:
    p = clamp_probability(value)
    return math.log(p / (1.0 - p))


def sigmoid(value: float) -> float:
    if value >= 40.0:
        return 1.0 - EPS
    if value <= -40.0:
        return EPS
    return 1.0 / (1.0 + math.exp(-value))


def brier(p: float, y: float) -> float:
    return (p - y) ** 2


def logloss(p: float, y: float) -> float:
    p = min(1.0 - EPS, max(EPS, p))
    return -(y * math.log(p) + (1.0 - y) * math.log(1.0 - p))


def read_csv_rows(path: Path, limit_rows: int | None = None) -> list[dict[str, Any]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        rows = []
        for idx, row in enumerate(reader):
            if limit_rows is not None and idx >= limit_rows:
                break
            rows.append(dict(row))
    return rows


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_csv_rows(rows: list[dict[str, Any]], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    fieldnames: list[str] = []
    seen: set[str] = set()
    for row in rows:
        for key in row:
            if key not in seen:
                fieldnames.append(key)
                seen.add(key)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def feature_names(manifest: list[dict[str, Any]]) -> set[str]:
    return {str(row["feature_name"]) for row in manifest}


def assign_market_chronological_splits(rows: list[dict[str, Any]]) -> None:
    markets: dict[str, str] = {}
    for row in rows:
        market = str(row.get("market_ticker") or "")
        close_ts = str(row.get("market_close_ts_utc") or row.get("decision_ts_utc") or "")
        if market and market not in markets:
            markets[market] = close_ts
        elif market:
            markets[market] = min(markets[market], close_ts)

    ordered = sorted(markets.items(), key=lambda item: (item[1], item[0]))
    total = len(ordered)
    train_cut = max(1, int(total * 0.60))
    validation_cut = max(train_cut + 1, int(total * 0.80)) if total > 2 else total

    split_by_market: dict[str, str] = {}
    for idx, (market, _close_ts) in enumerate(ordered):
        if idx < train_cut:
            split = "train"
        elif idx < validation_cut:
            split = "validation"
        else:
            split = "chronological_holdout"
        split_by_market[market] = split

    for row in rows:
        market = str(row.get("market_ticker") or "")
        row["chronological_split"] = split_by_market.get(market, "chronological_holdout")
        if as_bool(row.get("allowed_for_forward_promotion")):
            row["forward_split"] = "post_freeze_forward"
        else:
            row["forward_split"] = ""


def matrix_from_rows(rows: list[dict[str, Any]], columns: list[str]) -> list[list[float]]:
    return [[as_float(row.get(column), 0.0) or 0.0 for column in columns] for row in rows]


def target_vector(rows: list[dict[str, Any]]) -> list[float]:
    return [1.0 if (as_float(row.get("target_y_yes_win"), 0.0) or 0.0) >= 0.5 else 0.0 for row in rows]


def fit_standardizer(x: list[list[float]]) -> tuple[list[float], list[float]]:
    if not x:
        return [], []
    width = len(x[0])
    means = []
    scales = []
    for j in range(width):
        values = [row[j] for row in x]
        mean = sum(values) / len(values)
        variance = sum((value - mean) ** 2 for value in values) / max(1, len(values))
        scale = math.sqrt(variance)
        if scale < 1e-9:
            scale = 1.0
        means.append(mean)
        scales.append(scale)
    return means, scales


def apply_standardizer(x: list[list[float]], means: list[float], scales: list[float]) -> list[list[float]]:
    return [[(value - means[j]) / scales[j] for j, value in enumerate(row)] for row in x]


def solve_linear_system(a: list[list[float]], b: list[float]) -> list[float]:
    n = len(b)
    aug = [list(a[i]) + [b[i]] for i in range(n)]
    for col in range(n):
        pivot = max(range(col, n), key=lambda row: abs(aug[row][col]))
        if abs(aug[pivot][col]) < 1e-12:
            aug[col][col] += 1e-6
            pivot = col
        aug[col], aug[pivot] = aug[pivot], aug[col]
        pivot_value = aug[col][col]
        if abs(pivot_value) < 1e-12:
            continue
        for item in range(col, n + 1):
            aug[col][item] /= pivot_value
        for row in range(n):
            if row == col:
                continue
            factor = aug[row][col]
            if factor == 0.0:
                continue
            for item in range(col, n + 1):
                aug[row][item] -= factor * aug[col][item]
    return [aug[row][n] for row in range(n)]


def fit_logistic_weights(x: list[list[float]], y: list[float], l2_strength: float) -> list[float]:
    if not x:
        return [0.0]
    width = len(x[0]) + 1
    weights = [0.0 for _ in range(width)]
    n = len(x)
    for _iteration in range(60):
        gradient = [0.0 for _ in range(width)]
        hessian = [[0.0 for _ in range(width)] for _ in range(width)]
        for row, label in zip(x, y):
            xi = [1.0] + row
            p = sigmoid(sum(weights[j] * xi[j] for j in range(width)))
            diff = p - label
            curve = max(1e-6, p * (1.0 - p))
            for j in range(width):
                gradient[j] += diff * xi[j] / n
                for k in range(width):
                    hessian[j][k] += curve * xi[j] * xi[k] / n
        for j in range(1, width):
            gradient[j] += l2_strength * weights[j]
            hessian[j][j] += l2_strength
        hessian[0][0] += 1e-6
        try:
            delta = solve_linear_system(hessian, gradient)
        except ZeroDivisionError:
            break
        max_step = max(abs(value) for value in delta) if delta else 0.0
        for j in range(width):
            weights[j] -= max(-5.0, min(5.0, delta[j]))
        if max_step < 1e-6:
            break
    return weights


def fit_logistic_candidate(
    train_rows: list[dict[str, Any]],
    feature_columns: list[str],
    l2_strength: float,
) -> dict[str, Any]:
    x_raw = matrix_from_rows(train_rows, feature_columns)
    y = target_vector(train_rows)
    means, scales = fit_standardizer(x_raw)
    x = apply_standardizer(x_raw, means, scales)
    weights = fit_logistic_weights(x, y, l2_strength)
    return {
        "feature_columns": feature_columns,
        "means": means,
        "scales": scales,
        "weights": weights,
        "intercept": weights[0] if weights else 0.0,
        "coefficients": dict(zip(feature_columns, weights[1:])),
        "l2_strength": l2_strength,
    }


def predict_logistic(model: dict[str, Any], row: dict[str, Any]) -> float:
    columns = list(model["feature_columns"])
    raw = matrix_from_rows([row], columns)
    x = apply_standardizer(raw, list(model["means"]), list(model["scales"]))[0]
    weights = list(model["weights"])
    score = weights[0] + sum(weights[j + 1] * x[j] for j in range(len(x)))
    return min(1.0 - EPS, max(EPS, sigmoid(score)))


def fixed_time_gate(model: dict[str, Any], row: dict[str, Any]) -> float:
    time_gate = model.get("time_gate")
    if not isinstance(time_gate, dict) or not time_gate:
        return 1.0
    feature_name = str(time_gate.get("seconds_to_close_feature") or "seconds_to_close")
    seconds_to_close = as_float(row.get(feature_name))
    if seconds_to_close is None:
        return 0.0 if time_gate.get("missing_time_policy") == "zero_correction" else 1.0

    full_lte = as_float(time_gate.get("full_correction_seconds_lte"), 0.0)
    zero_gte = as_float(time_gate.get("zero_correction_seconds_gte"), 0.0)
    full_lte = 0.0 if full_lte is None else full_lte
    zero_gte = 0.0 if zero_gte is None else zero_gte
    if zero_gte <= full_lte:
        return 1.0 if seconds_to_close <= full_lte else 0.0
    if seconds_to_close <= full_lte:
        return 1.0
    if seconds_to_close >= zero_gte:
        return 0.0
    return (zero_gte - seconds_to_close) / (zero_gte - full_lte)


def fit_fixed_logit_residual(spec: dict[str, Any]) -> dict[str, Any]:
    return {
        "feature_columns": list(spec.get("feature_columns", [])),
        "base_probability_feature": spec.get("base_probability_feature", "target_v28_p_yes"),
        "residual_terms": list(spec.get("residual_terms", [])),
        "time_gate": dict(spec.get("time_gate", {})),
        "max_abs_logit_adjustment": float(spec.get("max_abs_logit_adjustment", 0.5)),
        "fit_source": "fixed_physics_hypothesis_no_retrospective_credit",
    }


def predict_fixed_logit_residual(model: dict[str, Any], row: dict[str, Any]) -> float:
    base_feature = str(model.get("base_probability_feature") or "target_v28_p_yes")
    p = clamp_probability(row.get(base_feature))
    adjustment = 0.0
    for term in model.get("residual_terms", []):
        if not isinstance(term, dict):
            continue
        feature_name = str(term.get("feature") or "")
        if not feature_name:
            continue
        value = as_float(row.get(feature_name), 0.0) or 0.0
        coefficient = as_float(term.get("coefficient"), 0.0) or 0.0
        adjustment += coefficient * value
    adjustment *= fixed_time_gate(model, row)
    cap = abs(as_float(model.get("max_abs_logit_adjustment"), 0.5) or 0.5)
    adjustment = max(-cap, min(cap, adjustment))
    return min(1.0 - EPS, max(EPS, sigmoid(logit(p) + adjustment)))


def pava(values: list[float], weights: list[float]) -> list[float]:
    blocks: list[dict[str, float | int]] = []
    for idx, (value, weight) in enumerate(zip(values, weights)):
        blocks.append({"start": idx, "end": idx, "weight": max(weight, 1e-9), "sum": value * max(weight, 1e-9)})
        while len(blocks) >= 2:
            left = blocks[-2]
            right = blocks[-1]
            left_avg = float(left["sum"]) / float(left["weight"])
            right_avg = float(right["sum"]) / float(right["weight"])
            if left_avg <= right_avg:
                break
            merged = {
                "start": left["start"],
                "end": right["end"],
                "weight": float(left["weight"]) + float(right["weight"]),
                "sum": float(left["sum"]) + float(right["sum"]),
            }
            blocks = blocks[:-2] + [merged]
    out = [0.5 for _ in values]
    for block in blocks:
        avg = float(block["sum"]) / float(block["weight"])
        for idx in range(int(block["start"]), int(block["end"]) + 1):
            out[idx] = avg
    return out


def p_bucket(p: float, bins: int) -> int:
    return min(bins - 1, max(0, int(math.floor(p * bins))))


def fit_monotonic_tabular(
    train_rows: list[dict[str, Any]],
    bins: int = 10,
    shrink_strength: float = 20.0,
    boundary_blend: dict[str, Any] | None = None,
) -> dict[str, Any]:
    bucket_rows: list[dict[str, Any]] = []
    for bucket in range(bins):
        lo = bucket / bins
        hi = (bucket + 1) / bins
        members = [row for row in train_rows if p_bucket(clamp_probability(row.get("target_v28_p_yes")), bins) == bucket]
        n = len(members)
        if n:
            wins = sum(target_vector(members))
            avg_base = sum(clamp_probability(row.get("target_v28_p_yes")) for row in members) / n
        else:
            wins = 0.0
            avg_base = (lo + hi) / 2.0
        shrunk = (wins + shrink_strength * avg_base) / (n + shrink_strength)
        bucket_rows.append(
            {
                "bucket": bucket,
                "p_min": lo,
                "p_max": hi,
                "rows": n,
                "wins": wins,
                "avg_v28_p_yes": avg_base,
                "shrunk_empirical_yes_rate": shrunk,
            }
        )
    monotonic_values = pava(
        [float(row["shrunk_empirical_yes_rate"]) for row in bucket_rows],
        [max(1.0, float(row["rows"])) for row in bucket_rows],
    )
    for row, value in zip(bucket_rows, monotonic_values):
        row["monotonic_p_yes"] = min(1.0 - EPS, max(EPS, value))
    model = {
        "feature_columns": ["target_v28_p_yes"],
        "bins": bins,
        "shrink_strength": shrink_strength,
        "bucket_table": bucket_rows,
    }
    if boundary_blend:
        model["boundary_blend"] = dict(boundary_blend)
    return model


def monotonic_boundary_weight(model: dict[str, Any], row: dict[str, Any]) -> float:
    config = model.get("boundary_blend")
    if not isinstance(config, dict) or not config:
        return 1.0

    feature_names = [str(config.get("distance_feature") or "abs_d_sigma")]
    feature_names.extend(str(name) for name in config.get("fallback_distance_features", []) if str(name))
    distance = None
    for feature_name in feature_names:
        distance = as_float(row.get(feature_name))
        if distance is not None:
            break
    if distance is None:
        return 0.0

    distance = abs(distance)
    inner = as_float(config.get("full_correction_abs_d_lte"), 1.0) or 1.0
    outer = as_float(config.get("zero_correction_abs_d_gte"), 2.0) or 2.0
    if outer <= inner:
        return 1.0 if distance <= inner else 0.0
    if distance <= inner:
        return 1.0
    if distance >= outer:
        return 0.0
    return (outer - distance) / (outer - inner)


def monotonic_time_weight(model: dict[str, Any], row: dict[str, Any]) -> float:
    config = model.get("boundary_blend")
    if not isinstance(config, dict) or not config:
        return 1.0
    time_gate = config.get("time_gate")
    if not isinstance(time_gate, dict) or not time_gate:
        return 1.0

    feature_names = [str(time_gate.get("seconds_to_close_feature") or "seconds_to_close")]
    feature_names.extend(str(name) for name in time_gate.get("fallback_seconds_to_close_features", []) if str(name))
    seconds_to_close = None
    for feature_name in feature_names:
        seconds_to_close = as_float(row.get(feature_name))
        if seconds_to_close is not None:
            break
    if seconds_to_close is None:
        return 1.0 if time_gate.get("missing_time_policy", "full_correction") == "full_correction" else 0.0

    zero_lte = as_float(time_gate.get("zero_correction_seconds_lte"), 0.0)
    full_gte = as_float(time_gate.get("full_correction_seconds_gte"), 0.0)
    zero_lte = 0.0 if zero_lte is None else zero_lte
    full_gte = 0.0 if full_gte is None else full_gte
    if full_gte <= zero_lte:
        return 1.0 if seconds_to_close > zero_lte else 0.0
    if seconds_to_close <= zero_lte:
        return 0.0
    if seconds_to_close >= full_gte:
        return 1.0
    return (seconds_to_close - zero_lte) / (full_gte - zero_lte)


def predict_monotonic_tabular(model: dict[str, Any], row: dict[str, Any]) -> float:
    p = clamp_probability(row.get("target_v28_p_yes"))
    bucket = p_bucket(p, int(model["bins"]))
    table = list(model["bucket_table"])
    calibrated = clamp_probability(table[bucket]["monotonic_p_yes"])
    # Blend lightly back toward v28 so empty or tiny bins cannot fully dominate.
    corrected = 0.80 * calibrated + 0.20 * p
    boundary_weight = monotonic_boundary_weight(model, row)
    time_weight = monotonic_time_weight(model, row)
    config = model.get("boundary_blend")
    correction_scale = 1.0
    if isinstance(config, dict):
        parsed_scale = as_float(config.get("correction_scale"), 1.0)
        correction_scale = 1.0 if parsed_scale is None else parsed_scale
    correction_scale = max(0.0, min(1.0, correction_scale))
    return min(1.0 - EPS, max(EPS, p + correction_scale * boundary_weight * time_weight * (corrected - p)))


def candidate_specs(manifest: list[dict[str, Any]]) -> list[dict[str, Any]]:
    names = feature_names(manifest)

    def keep(columns: list[str]) -> list[str]:
        return [column for column in columns if column in names]

    return [
        {
            "candidate_id": "v28_raw",
            "model_type": "baseline_v28_raw",
            "model_track": "baseline",
            "feature_columns": [],
            "description": "Raw v28 YES-axis probability from the feature table.",
        },
        {
            "candidate_id": "v28s_logistic_calibration_v001",
            "model_type": "regularized_logistic",
            "model_track": "pure_physics",
            "feature_columns": keep(["v28_logit_yes"]),
            "l2_strength": 0.20,
            "description": "One-dimensional train-only logistic recalibration of v28.",
        },
        {
            "candidate_id": "v28s_logistic_boundary_physics_v001",
            "model_type": "regularized_logistic",
            "model_track": "pure_physics",
            "feature_columns": keep(
                [
                    "v28_logit_yes",
                    "v28_abs_logit_yes",
                    "minutes_to_close",
                    "late_window_lte_180s",
                    "final_avg_effective_horizon_minutes",
                    "final_avg_variance_compression",
                    "final_avg_uncertainty_scale",
                    "final_avg_elapsed_window_fraction",
                    "final_avg_sigma_proxy_dollars",
                    "final_avg_d_sigma_proxy",
                    "final_avg_abs_d_sigma_proxy",
                    "log1p_sigma_t_dollars",
                    "recross_hazard_score",
                    "recross_hazard_high",
                    "v28_api_replay_p_anchor",
                    "v28_api_replay_p_static_boundary_field",
                    "v28_api_replay_p_recent_transport",
                    "v28_api_replay_p_long_transport",
                    "v28_api_replay_edge_gate",
                    "v28_api_replay_static_gate",
                    "log1p_v28_api_replay_transport_recent_n",
                    "log1p_v28_api_replay_transport_long_n",
                    "d_sigma",
                    "abs_d_sigma",
                    "boundary_zone_abs_d_lte_1",
                    "arrow",
                    "arrow_x_d_sigma",
                    "distance_per_sigma_from_prices",
                    "btc_drift_from_prev_event_dollars",
                    "btc_drift_from_first_event_dollars",
                    "prior_btc_path_range_per_sigma",
                    "prior_adverse_path_memory_per_sigma",
                    "prior_recross_seen",
                ]
            ),
            "l2_strength": 0.25,
            "description": "Small boundary/time/volatility regularized logistic surface.",
        },
        {
            "candidate_id": "v28s_logistic_book_reliability_diag_v001",
            "model_type": "regularized_logistic",
            "model_track": "book_aware_diagnostic",
            "feature_columns": keep(
                [
                    "v28_logit_yes",
                    "v28_abs_logit_yes",
                    "minutes_to_close",
                    "recross_hazard_score",
                    "ask_frac",
                    "edge_cents",
                    "book_implied_yes_from_side_ask",
                    "v28_minus_book_implied_yes",
                    "v28_book_disagreement_abs",
                    "btc_age_ms",
                    "book_age_ms",
                    "feed_age_ms",
                    "freshness_max_age_ms",
                    "v28_api_replay_available",
                    "v28_api_replay_abs_p_delta",
                    "v28_api_replay_minus_logged_sigma",
                    "v28_api_replay_minus_logged_d_sigma",
                    "side_is_yes",
                    "source_is_entry",
                    "source_is_rejected_actionable",
                    "source_is_logged_approved",
                    "source_is_signal_seen",
                    "source_is_plan_built",
                ]
            ),
            "l2_strength": 0.35,
            "description": "Book/source-aware diagnostic logistic surface; never pure FV evidence by itself.",
        },
        {
            "candidate_id": "v28s_monotonic_tabular_v001",
            "model_type": "monotonic_tabular_calibration",
            "model_track": "pure_physics",
            "feature_columns": ["target_v28_p_yes"],
            "bins": 10,
            "shrink_strength": 20.0,
            "description": "Ten-bin monotonic tabular calibration of v28 probability, fit on train only.",
        },
        {
            "candidate_id": "v28s_boundary_monotonic_blend_v001",
            "model_type": "monotonic_tabular_calibration",
            "model_track": "pure_physics",
            "feature_columns": ["target_v28_p_yes"] + keep(["abs_d_sigma", "final_avg_abs_d_sigma_proxy"]),
            "bins": 10,
            "shrink_strength": 20.0,
            "boundary_blend": {
                "distance_feature": "abs_d_sigma",
                "fallback_distance_features": ["final_avg_abs_d_sigma_proxy"],
                "full_correction_abs_d_lte": 1.0,
                "zero_correction_abs_d_gte": 2.0,
                "missing_distance_policy": "raw_v28",
            },
            "description": "Boundary-only monotonic correction: full inside abs(d_sigma)<=1, linearly tapered to raw v28 by abs(d_sigma)>=2.",
        },
        {
            "candidate_id": "v28s_boundary_monotonic_light_v001",
            "model_type": "monotonic_tabular_calibration",
            "model_track": "pure_physics",
            "feature_columns": ["target_v28_p_yes"] + keep(["abs_d_sigma", "final_avg_abs_d_sigma_proxy"]),
            "bins": 10,
            "shrink_strength": 20.0,
            "boundary_blend": {
                "distance_feature": "abs_d_sigma",
                "fallback_distance_features": ["final_avg_abs_d_sigma_proxy"],
                "full_correction_abs_d_lte": 1.0,
                "zero_correction_abs_d_gte": 2.0,
                "correction_scale": 0.33,
                "missing_distance_policy": "raw_v28",
            },
            "description": "Conservative one-third-strength boundary-only monotonic correction, frozen separately for future evidence.",
        },
        {
            "candidate_id": "v28s_boundary_monotonic_time_safe_v001",
            "model_type": "monotonic_tabular_calibration",
            "model_track": "pure_physics",
            "feature_columns": ["target_v28_p_yes"]
            + keep(["abs_d_sigma", "final_avg_abs_d_sigma_proxy", "seconds_to_close"]),
            "bins": 10,
            "shrink_strength": 20.0,
            "boundary_blend": {
                "distance_feature": "abs_d_sigma",
                "fallback_distance_features": ["final_avg_abs_d_sigma_proxy"],
                "full_correction_abs_d_lte": 1.0,
                "zero_correction_abs_d_gte": 2.0,
                "correction_scale": 0.10,
                "missing_distance_policy": "raw_v28",
                "time_gate": {
                    "seconds_to_close_feature": "seconds_to_close",
                    "zero_correction_seconds_lte": 240.0,
                    "full_correction_seconds_gte": 600.0,
                    "missing_time_policy": "full_correction",
                },
            },
            "description": "Tiny boundary monotonic correction that is disabled inside the final 240 seconds and fades in by 600 seconds, frozen separately for future evidence.",
        },
        {
            "candidate_id": "v28s_boundary_monotonic_micro_time_safe_v001",
            "model_type": "monotonic_tabular_calibration",
            "model_track": "pure_physics",
            "feature_columns": ["target_v28_p_yes"]
            + keep(["abs_d_sigma", "final_avg_abs_d_sigma_proxy", "seconds_to_close"]),
            "bins": 10,
            "shrink_strength": 20.0,
            "boundary_blend": {
                "distance_feature": "abs_d_sigma",
                "fallback_distance_features": ["final_avg_abs_d_sigma_proxy"],
                "full_correction_abs_d_lte": 1.0,
                "zero_correction_abs_d_gte": 2.0,
                "correction_scale": 0.03,
                "missing_distance_policy": "raw_v28",
                "time_gate": {
                    "seconds_to_close_feature": "seconds_to_close",
                    "zero_correction_seconds_lte": 240.0,
                    "full_correction_seconds_gte": 600.0,
                    "missing_time_policy": "full_correction",
                },
            },
            "description": "Micro-strength boundary monotonic correction using the same causal time gate as the time-safe candidate; frozen separately and starts forward evidence only after this manifest exists.",
        },
        {
            "candidate_id": "v28s_late_dsigma_residual_tilt_v001",
            "model_type": "fixed_logit_residual",
            "model_track": "pure_physics",
            "feature_columns": ["target_v28_p_yes"] + keep(["d_sigma", "seconds_to_close"]),
            "base_probability_feature": "target_v28_p_yes",
            "residual_terms": [
                {
                    "feature": "d_sigma",
                    "coefficient": -0.20,
                    "rationale": "Final-average settlement should be less sensitive to instantaneous signed boundary distance as close approaches.",
                }
            ],
            "time_gate": {
                "seconds_to_close_feature": "seconds_to_close",
                "full_correction_seconds_lte": 240.0,
                "zero_correction_seconds_gte": 600.0,
                "missing_time_policy": "zero_correction",
            },
            "max_abs_logit_adjustment": 0.75,
            "description": "Fixed late-window d_sigma logit residual: no change at or beyond 600 seconds, full conservative counter-tilt inside 240 seconds, and no retrospective credit before this manifest exists.",
        },
    ]


def fit_candidates(rows: list[dict[str, Any]], manifest: list[dict[str, Any]]) -> list[dict[str, Any]]:
    train_rows = [
        row
        for row in rows
        if row.get("chronological_split") == "train"
        and as_bool(row.get("allowed_for_training"))
        and as_float(row.get("target_y_yes_win")) is not None
    ]
    candidates: list[dict[str, Any]] = []
    manifest_names = feature_names(manifest)
    for spec in candidate_specs(manifest):
        model_type = spec["model_type"]
        feature_columns = list(spec.get("feature_columns", []))
        missing_features = [column for column in feature_columns if column not in manifest_names and not column.startswith("target_")]
        if missing_features:
            raise ValueError(f"Candidate {spec['candidate_id']} references missing feature columns: {missing_features}")
        if model_type == "baseline_v28_raw":
            model = {"feature_columns": [], "weights": [], "intercept": 0.0, "coefficients": {}}
        elif model_type == "regularized_logistic":
            model = fit_logistic_candidate(train_rows, feature_columns, float(spec["l2_strength"]))
        elif model_type == "monotonic_tabular_calibration":
            model = fit_monotonic_tabular(
                train_rows,
                bins=int(spec["bins"]),
                shrink_strength=float(spec["shrink_strength"]),
                boundary_blend=spec.get("boundary_blend"),
            )
        elif model_type == "fixed_logit_residual":
            model = fit_fixed_logit_residual(spec)
        else:
            raise ValueError(f"Unknown model type: {model_type}")
        candidates.append({**spec, "model": model})
    return candidates


def predict_candidate(candidate: dict[str, Any], row: dict[str, Any]) -> float:
    model_type = candidate["model_type"]
    if model_type == "baseline_v28_raw":
        return clamp_probability(row.get("target_v28_p_yes"))
    if model_type == "regularized_logistic":
        return predict_logistic(candidate["model"], row)
    if model_type == "monotonic_tabular_calibration":
        return predict_monotonic_tabular(candidate["model"], row)
    if model_type == "fixed_logit_residual":
        return predict_fixed_logit_residual(candidate["model"], row)
    raise ValueError(f"Unknown model type: {model_type}")


def kalshi_taker_fee_cents(price_cents: float, contracts: int = 1) -> int:
    probability = min(1.0, max(0.0, price_cents / 100.0))
    raw_fee_dollars = 0.07 * contracts * probability * (1.0 - probability)
    return int(math.ceil(raw_fee_dollars * 100.0 - 1e-12))


def prediction_long_rows(rows: list[dict[str, Any]], candidates: list[dict[str, Any]]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for row in rows:
        y_yes = 1.0 if (as_float(row.get("target_y_yes_win"), 0.0) or 0.0) >= 0.5 else 0.0
        side = str(row.get("side") or "").lower()
        ask = as_float(row.get("ask_cents"))
        for candidate in candidates:
            p_yes = predict_candidate(candidate, row)
            p_side = p_yes if side == "yes" else 1.0 - p_yes if side == "no" else max(p_yes, 1.0 - p_yes)
            fair_side_cents = 100.0 * p_side
            candidate_edge_cents = None if ask is None else fair_side_cents - ask
            shadow_enter = bool(candidate_edge_cents is not None and candidate_edge_cents >= SHADOW_MIN_EDGE_CENTS)
            side_win = y_yes if side == "yes" else 1.0 - y_yes if side == "no" else y_yes
            fee_cents = kalshi_taker_fee_cents(ask) if ask is not None and shadow_enter else 0
            gross_pnl = (100.0 * side_win - ask) if ask is not None and shadow_enter else 0.0
            net_pnl = gross_pnl - fee_cents if shadow_enter else 0.0
            expected_ev = (fair_side_cents - ask - fee_cents) if ask is not None and shadow_enter else 0.0
            out.append(
                {
                    "row_id": row.get("row_id"),
                    "market_ticker": row.get("market_ticker"),
                    "decision_ts_utc": row.get("decision_ts_utc"),
                    "chronological_split": row.get("chronological_split"),
                    "forward_split": row.get("forward_split"),
                    "source_type": row.get("source_type"),
                    "seconds_to_close": as_float(row.get("seconds_to_close")),
                    "recross_hazard_score": as_float(row.get("recross_hazard_score")),
                    "d_sigma": as_float(row.get("d_sigma")),
                    "abs_d_sigma": as_float(row.get("abs_d_sigma")),
                    "strike_distance_dollars_abs": as_float(row.get("strike_distance_dollars_abs")),
                    "btc_age_ms": as_float(row.get("btc_age_ms")),
                    "book_age_ms": as_float(row.get("book_age_ms")),
                    "feed_age_ms": as_float(row.get("feed_age_ms")),
                    "freshness_max_age_ms": as_float(row.get("freshness_max_age_ms")),
                    "prior_recross_seen": as_float(row.get("prior_recross_seen")),
                    "prior_adverse_path_memory_per_sigma": as_float(row.get("prior_adverse_path_memory_per_sigma")),
                    "candidate_id": candidate["candidate_id"],
                    "model_type": candidate["model_type"],
                    "model_track": candidate["model_track"],
                    "target_y_yes_win": y_yes,
                    "v28_p_yes": clamp_probability(row.get("target_v28_p_yes")),
                    "candidate_p_yes": p_yes,
                    "candidate_fair_yes_cents": 100.0 * p_yes,
                    "candidate_fair_no_cents": 100.0 * (1.0 - p_yes),
                    "side": side,
                    "candidate_fair_side_cents": fair_side_cents,
                    "ask_cents": ask,
                    "candidate_edge_cents": candidate_edge_cents,
                    "shadow_enter": shadow_enter,
                    "shadow_fee_cents": fee_cents,
                    "shadow_gross_pnl_cents": gross_pnl,
                    "shadow_net_pnl_cents": net_pnl,
                    "shadow_expected_ev_cents": expected_ev,
                    "allowed_for_forward_promotion": as_bool(row.get("allowed_for_forward_promotion")),
                    "row_is_posthoc": as_bool(row.get("row_is_posthoc")),
                }
            )
    return out


def calibration_bins(predictions: list[dict[str, Any]], split: str, candidate_id: str, bins: int = 10) -> list[dict[str, Any]]:
    selected = [row for row in predictions if row["candidate_id"] == candidate_id and split_matches(row, split)]
    out: list[dict[str, Any]] = []
    for bucket in range(bins):
        members = [row for row in selected if p_bucket(clamp_probability(row["candidate_p_yes"]), bins) == bucket]
        if not members:
            out.append(
                {
                    "candidate_id": candidate_id,
                    "split": split,
                    "bin": bucket,
                    "p_min": bucket / bins,
                    "p_max": (bucket + 1) / bins,
                    "rows": 0,
                    "avg_pred": None,
                    "win_rate": None,
                    "brier": None,
                }
            )
            continue
        avg_pred = sum(float(row["candidate_p_yes"]) for row in members) / len(members)
        win_rate = sum(float(row["target_y_yes_win"]) for row in members) / len(members)
        out.append(
            {
                "candidate_id": candidate_id,
                "split": split,
                "bin": bucket,
                "p_min": bucket / bins,
                "p_max": (bucket + 1) / bins,
                "rows": len(members),
                "avg_pred": avg_pred,
                "win_rate": win_rate,
                "brier": sum(brier(float(row["candidate_p_yes"]), float(row["target_y_yes_win"])) for row in members) / len(members),
            }
        )
    return out


def expected_calibration_error(predictions: list[dict[str, Any]], bins: int = 10) -> float | None:
    if not predictions:
        return None
    total = len(predictions)
    ece = 0.0
    for bucket in range(bins):
        members = [row for row in predictions if p_bucket(clamp_probability(row["candidate_p_yes"]), bins) == bucket]
        if not members:
            continue
        avg_pred = sum(float(row["candidate_p_yes"]) for row in members) / len(members)
        win_rate = sum(float(row["target_y_yes_win"]) for row in members) / len(members)
        ece += len(members) / total * abs(avg_pred - win_rate)
    return ece


def fit_calibration_intercept_slope(predictions: list[dict[str, Any]]) -> tuple[float | None, float | None]:
    if len(predictions) < 20:
        return None, None
    labels = [float(row["target_y_yes_win"]) for row in predictions]
    if sum(labels) in {0.0, float(len(labels))}:
        return None, None
    xs = [[logit(row["candidate_p_yes"])] for row in predictions]
    means = [0.0]
    scales = [1.0]
    x = apply_standardizer(xs, means, scales)
    weights = fit_logistic_weights(x, labels, 1e-5)
    return weights[0], weights[1] if len(weights) > 1 else None


def split_matches(row: dict[str, Any], split: str) -> bool:
    if split == "all":
        return True
    if split == "post_freeze_forward":
        return row.get("forward_split") == "post_freeze_forward"
    return row.get("chronological_split") == split


def row_slice_matches(row: dict[str, Any], slice_name: str) -> bool:
    if slice_name == "all_rows":
        return True
    p_v28 = clamp_probability(row.get("v28_p_yes"))
    if slice_name == "near_boundary_v28_40_60":
        return 0.40 <= p_v28 <= 0.60
    if slice_name == "near_boundary_abs_d_lte_1":
        abs_d = as_float(row.get("abs_d_sigma"))
        return abs_d is not None and abs_d <= 1.0
    if slice_name == "high_recross":
        return as_float(row.get("recross_hazard_score"), 0.0) is not None and (as_float(row.get("recross_hazard_score"), 0.0) or 0.0) >= 0.5
    if slice_name == "prior_recross_seen":
        return as_bool(row.get("prior_recross_seen")) or (as_float(row.get("prior_recross_seen"), 0.0) or 0.0) >= 0.5
    if slice_name == "adverse_memory_gt_1sigma":
        value = as_float(row.get("prior_adverse_path_memory_per_sigma"), 0.0)
        return value is not None and value > 1.0
    if slice_name == "late_lte_180s":
        return as_float(row.get("seconds_to_close"), 999999.0) is not None and (as_float(row.get("seconds_to_close"), 999999.0) or 999999.0) <= 180.0
    if slice_name == "stale_feed_gt_1000ms":
        age = as_float(row.get("freshness_max_age_ms"), as_float(row.get("feed_age_ms")))
        return age is not None and age > 1000.0
    if slice_name == "fresh_feed_lte_1000ms":
        age = as_float(row.get("freshness_max_age_ms"), as_float(row.get("feed_age_ms")))
        return age is not None and age <= 1000.0
    if slice_name == "entry_source":
        return str(row.get("source_type") or "") == "entry"
    if slice_name == "rejected_actionable_source":
        return str(row.get("source_type") or "") == "rejected_actionable"
    return False


def metric_record(predictions: list[dict[str, Any]], candidate_id: str, split: str, slice_name: str) -> dict[str, Any]:
    selected = [
        row
        for row in predictions
        if row["candidate_id"] == candidate_id and split_matches(row, split) and row_slice_matches(row, slice_name)
    ]
    if not selected:
        return {
            "candidate_id": candidate_id,
            "split": split,
            "slice": slice_name,
            "rows": 0,
            "markets": 0,
            "avg_pred": None,
            "win_rate": None,
            "brier": None,
            "logloss": None,
            "ece_10bin": None,
            "side_accuracy": None,
            "calibration_intercept": None,
            "calibration_slope": None,
            "shadow_trades": 0,
            "shadow_coverage": 0.0,
            "shadow_net_pnl_cents": 0.0,
            "shadow_expected_ev_cents": 0.0,
        }
    markets = {str(row.get("market_ticker") or "") for row in selected}
    probs = [float(row["candidate_p_yes"]) for row in selected]
    labels = [float(row["target_y_yes_win"]) for row in selected]
    intercept, slope = fit_calibration_intercept_slope(selected)
    shadow_trades = [row for row in selected if as_bool(row.get("shadow_enter"))]
    return {
        "candidate_id": candidate_id,
        "split": split,
        "slice": slice_name,
        "rows": len(selected),
        "markets": len(markets),
        "avg_pred": sum(probs) / len(probs),
        "win_rate": sum(labels) / len(labels),
        "brier": sum(brier(p, y) for p, y in zip(probs, labels)) / len(selected),
        "logloss": sum(logloss(p, y) for p, y in zip(probs, labels)) / len(selected),
        "ece_10bin": expected_calibration_error(selected),
        "side_accuracy": sum((p >= 0.5) == (y >= 0.5) for p, y in zip(probs, labels)) / len(selected),
        "calibration_intercept": intercept,
        "calibration_slope": slope,
        "shadow_trades": len(shadow_trades),
        "shadow_coverage": len(shadow_trades) / len(selected),
        "shadow_net_pnl_cents": sum(float(row["shadow_net_pnl_cents"]) for row in selected),
        "shadow_expected_ev_cents": sum(float(row["shadow_expected_ev_cents"]) for row in selected),
    }


def score_predictions(predictions: list[dict[str, Any]], candidate_ids: list[str]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    splits = ["all", "train", "validation", "chronological_holdout", "post_freeze_forward"]
    slices = [
        "all_rows",
        "near_boundary_v28_40_60",
        "near_boundary_abs_d_lte_1",
        "high_recross",
        "prior_recross_seen",
        "adverse_memory_gt_1sigma",
        "late_lte_180s",
        "fresh_feed_lte_1000ms",
        "stale_feed_gt_1000ms",
        "entry_source",
        "rejected_actionable_source",
    ]
    metrics = [
        metric_record(predictions, candidate_id, split, slice_name)
        for candidate_id in candidate_ids
        for split in splits
        for slice_name in slices
    ]
    bins = [
        row
        for candidate_id in candidate_ids
        for split in splits
        for row in calibration_bins(predictions, split, candidate_id)
    ]
    return metrics, bins


def find_metric(metrics: list[dict[str, Any]], candidate_id: str, split: str, slice_name: str) -> dict[str, Any] | None:
    for row in metrics:
        if row["candidate_id"] == candidate_id and row["split"] == split and row["slice"] == slice_name:
            return row
    return None


def metric_improved(candidate: dict[str, Any] | None, baseline: dict[str, Any] | None, key: str) -> bool:
    if not candidate or not baseline:
        return False
    cand = candidate.get(key)
    base = baseline.get(key)
    return cand is not None and base is not None and float(cand) < float(base)


def build_promotion_gate(candidate: dict[str, Any], metrics: list[dict[str, Any]], rows: list[dict[str, Any]]) -> dict[str, Any]:
    candidate_id = candidate["candidate_id"]
    if candidate_id == "v28_raw":
        return {
            "candidate_id": candidate_id,
            "allowed_for_forward_registry": False,
            "promotable": False,
            "status": "baseline_not_candidate",
            "fail_reasons": ["v28_raw_is_control_baseline"],
        }
    holdout = find_metric(metrics, candidate_id, "chronological_holdout", "all_rows")
    baseline_holdout = find_metric(metrics, "v28_raw", "chronological_holdout", "all_rows")
    boundary = find_metric(metrics, candidate_id, "chronological_holdout", "near_boundary_v28_40_60")
    baseline_boundary = find_metric(metrics, "v28_raw", "chronological_holdout", "near_boundary_v28_40_60")
    recross = find_metric(metrics, candidate_id, "chronological_holdout", "high_recross")
    baseline_recross = find_metric(metrics, "v28_raw", "chronological_holdout", "high_recross")
    true_boundary = find_metric(metrics, candidate_id, "chronological_holdout", "near_boundary_abs_d_lte_1")
    baseline_true_boundary = find_metric(metrics, "v28_raw", "chronological_holdout", "near_boundary_abs_d_lte_1")
    forward_rows = sum(1 for row in rows if as_bool(row.get("allowed_for_forward_promotion")))
    posthoc_rows = sum(1 for row in rows if as_bool(row.get("row_is_posthoc")))
    diagnostic_rows = sum(
        1
        for row in rows
        if as_bool(row.get("row_is_posthoc"))
        or as_bool(row.get("row_is_sidecar"))
        or as_bool(row.get("row_is_diagnostic_only"))
    )
    true_boundary_available = bool(baseline_true_boundary and int(baseline_true_boundary.get("rows") or 0) > 0)
    proxy_boundary_available = bool(baseline_boundary and int(baseline_boundary.get("rows") or 0) > 0)

    checks = {
        "holdout_brier_better_than_v28": metric_improved(holdout, baseline_holdout, "brier"),
        "holdout_logloss_better_than_v28": metric_improved(holdout, baseline_holdout, "logloss"),
        "near_boundary_brier_not_degraded": (
            bool(boundary and baseline_boundary and boundary.get("rows", 0) and baseline_boundary.get("rows", 0))
            and float(boundary["brier"]) <= float(baseline_boundary["brier"])
        ) if proxy_boundary_available else (
            bool(true_boundary and baseline_true_boundary and true_boundary.get("rows", 0) and baseline_true_boundary.get("rows", 0))
            and float(true_boundary["brier"]) <= float(baseline_true_boundary["brier"])
        ) if true_boundary_available else False,
        "high_recross_brier_not_degraded": (
            bool(recross and baseline_recross and recross.get("rows", 0) and baseline_recross.get("rows", 0))
            and float(recross["brier"]) <= float(baseline_recross["brier"])
        ),
        "true_boundary_abs_d_lte_1_brier_not_degraded": (
            bool(true_boundary and baseline_true_boundary and true_boundary.get("rows", 0) and baseline_true_boundary.get("rows", 0))
            and float(true_boundary["brier"]) <= float(baseline_true_boundary["brier"])
        ) if true_boundary_available else False,
        "post_freeze_forward_rows_present": forward_rows >= MIN_FORWARD_ROWS_FOR_PROMOTION,
        "source_quality_promotable": forward_rows > 0 and diagnostic_rows == 0,
        "broad_market_coverage": bool(holdout and int(holdout.get("markets") or 0) >= 20),
    }
    fail_reasons = [name for name, passed in checks.items() if not passed]
    if forward_rows == 0:
        fail_reasons.append("no_post_lock_forward_rows")
    if posthoc_rows:
        fail_reasons.append("seed_rows_are_posthoc_diagnostic")
    if diagnostic_rows:
        fail_reasons.append("source_rows_are_diagnostic_not_forward_registered")
    if not true_boundary_available:
        fail_reasons.append("strike_missing_in_current_seed_boundary_distance_is_proxy")
    promotable = not fail_reasons
    return {
        "candidate_id": candidate_id,
        "allowed_for_forward_registry": False,
        "promotable": promotable,
        "status": "pass" if promotable else "fail",
        "checks": checks,
        "fail_reasons": sorted(set(fail_reasons)),
        "minimum_forward_rows_required": MIN_FORWARD_ROWS_FOR_PROMOTION,
        "observed_forward_rows": forward_rows,
    }


def build_forward_collection_gate(candidate: dict[str, Any], rows: list[dict[str, Any]]) -> dict[str, Any]:
    """Decide whether a candidate can be frozen for future shadow collection.

    This is intentionally weaker than promotion. It allows simple, inspectable
    non-baseline surfaces to be recorded prospectively so post-lock evidence can
    exist later. It does not make the candidate promotable.
    """
    candidate_id = candidate["candidate_id"]
    if candidate_id == "v28_raw":
        return {
            "candidate_id": candidate_id,
            "allowed": False,
            "status": "baseline_not_collected_as_challenger",
            "fail_reasons": ["v28_raw_is_control_baseline"],
            "warnings": [],
        }
    split_counts = split_summary(rows)
    feature_columns = candidate.get("feature_columns", [])
    checks = {
        "simple_inspectable_model_type": candidate.get("model_type")
        in {"regularized_logistic", "monotonic_tabular_calibration", "fixed_logit_residual"},
        "has_frozen_model_payload": bool(candidate.get("model")),
        "has_training_rows": split_counts["train"]["rows"] > 0,
        "has_validation_rows": split_counts["validation"]["rows"] > 0,
        "has_holdout_rows": split_counts["chronological_holdout"]["rows"] > 0,
        "feature_surface_declared": isinstance(feature_columns, list),
    }
    fail_reasons = [name for name, passed in checks.items() if not passed]
    warnings = [
        "forward_collection_only_not_promotion",
        "current_fit_uses_diagnostic_rows_until_frozen_post_lock_evidence_exists",
    ]
    return {
        "candidate_id": candidate_id,
        "allowed": not fail_reasons,
        "status": "allowed_for_shadow_forward_collection" if not fail_reasons else "blocked_for_collection",
        "checks": checks,
        "fail_reasons": sorted(set(fail_reasons)),
        "warnings": warnings,
    }


def split_summary(rows: list[dict[str, Any]]) -> dict[str, Any]:
    out: dict[str, Any] = {}
    for split in ["train", "validation", "chronological_holdout"]:
        members = [row for row in rows if row.get("chronological_split") == split]
        out[split] = {
            "rows": len(members),
            "markets": len({row.get("market_ticker") for row in members}),
            "start_decision_ts_utc": min((str(row.get("decision_ts_utc") or "") for row in members), default=None),
            "end_decision_ts_utc": max((str(row.get("decision_ts_utc") or "") for row in members), default=None),
        }
    forward = [row for row in rows if as_bool(row.get("allowed_for_forward_promotion"))]
    out["post_freeze_forward"] = {
        "rows": len(forward),
        "markets": len({row.get("market_ticker") for row in forward}),
    }
    return out


def candidate_manifest_rows(
    candidates: list[dict[str, Any]],
    metrics: list[dict[str, Any]],
    rows: list[dict[str, Any]],
    feature_manifest_hash: str,
    feature_table_hash: str | None,
) -> list[dict[str, Any]]:
    split_counts = split_summary(rows)
    out: list[dict[str, Any]] = []
    created_utc = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    for candidate in candidates:
        model_payload = candidate["model"]
        model_hash = stable_hash({"candidate_id": candidate["candidate_id"], "model": model_payload})
        gate = build_promotion_gate(candidate, metrics, rows)
        collection_gate = build_forward_collection_gate(candidate, rows)
        holdout = find_metric(metrics, candidate["candidate_id"], "chronological_holdout", "all_rows") or {}
        out.append(
            {
                "candidate_id": candidate["candidate_id"],
                "created_utc": created_utc,
                "description": candidate["description"],
                "model_type": candidate["model_type"],
                "model_track": candidate["model_track"],
                "baseline": "v28_raw",
                "feature_columns": candidate.get("feature_columns", []),
                "feature_manifest_hash": feature_manifest_hash,
                "feature_table_hash": feature_table_hash,
                "training_rows": split_counts["train"]["rows"],
                "validation_rows": split_counts["validation"]["rows"],
                "holdout_rows": split_counts["chronological_holdout"]["rows"],
                "forward_rows": split_counts["post_freeze_forward"]["rows"],
                "holdout_brier": holdout.get("brier"),
                "holdout_logloss": holdout.get("logloss"),
                "model_hash": model_hash,
                "model_parameters": model_payload,
                "promotion_gate": gate,
                "forward_collection_gate": collection_gate,
                "allowed_for_forward_collection": collection_gate["allowed"],
                "allowed_for_forward_registry": False,
            }
        )
    return out


def write_markdown(summary: dict[str, Any], manifests: list[dict[str, Any]], metrics: list[dict[str, Any]], path: Path) -> None:
    lines = [
        "# v28 Successor Calibration Report",
        "",
        "Research-only candidate training/scoring artifact. Live trading code, state, orders, thresholds, and processes were not touched.",
        "",
        "## Summary",
        "",
        f"- Generated UTC: `{summary['generated_utc']}`",
        f"- Feature table: `{summary['inputs']['feature_table']}`",
        f"- Feature table hash: `{summary['inputs']['feature_table_hash']}`",
        f"- Feature manifest hash: `{summary['inputs']['feature_manifest_hash']}`",
        f"- Rows: `{summary['row_count']}`",
        f"- Candidates: `{summary['candidate_count']}`",
        f"- Promotion verdict: `{summary['promotion_verdict']}`",
        "",
        "## Splits",
        "",
        "| split | rows | markets | start decision UTC | end decision UTC |",
        "|---|---:|---:|---|---|",
    ]
    for split in ["train", "validation", "chronological_holdout"]:
        item = summary["split_summary"][split]
        lines.append(
            f"| `{split}` | {item['rows']} | {item['markets']} | `{item['start_decision_ts_utc']}` | `{item['end_decision_ts_utc']}` |"
        )
    forward = summary["split_summary"]["post_freeze_forward"]
    lines.append(f"| `post_freeze_forward` | {forward['rows']} | {forward['markets']} |  |  |")

    lines.extend(
        [
            "",
            "## Chronological Holdout",
            "",
            "| candidate | track | Brier | logloss | ECE | side acc | proxy-boundary Brier | true-boundary Brier | high-recross Brier | shadow net c | gate |",
            "|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---|",
        ]
    )
    by_id = {manifest["candidate_id"]: manifest for manifest in manifests}
    for manifest in manifests:
        cid = manifest["candidate_id"]
        all_holdout = find_metric(metrics, cid, "chronological_holdout", "all_rows") or {}
        boundary = find_metric(metrics, cid, "chronological_holdout", "near_boundary_v28_40_60") or {}
        true_boundary = find_metric(metrics, cid, "chronological_holdout", "near_boundary_abs_d_lte_1") or {}
        recross = find_metric(metrics, cid, "chronological_holdout", "high_recross") or {}
        gate = manifest["promotion_gate"]
        lines.append(
            f"| `{cid}` | `{manifest['model_track']}` | {fmt(all_holdout.get('brier'))} | {fmt(all_holdout.get('logloss'))} | "
            f"{fmt(all_holdout.get('ece_10bin'))} | {fmt_pct(all_holdout.get('side_accuracy'))} | "
            f"{fmt(boundary.get('brier'))} | {fmt(true_boundary.get('brier'))} | {fmt(recross.get('brier'))} | "
            f"{fmt(all_holdout.get('shadow_net_pnl_cents'), 1)} | "
            f"`{gate['status']}` |"
        )

    lines.extend(["", "## Gate Read", ""])
    for manifest in manifests:
        gate = manifest["promotion_gate"]
        if manifest["candidate_id"] == "v28_raw":
            continue
        reasons = ", ".join(f"`{reason}`" for reason in gate["fail_reasons"])
        lines.append(f"- `{manifest['candidate_id']}` is not promotable: {reasons}.")

    baseline_true_boundary = find_metric(metrics, "v28_raw", "chronological_holdout", "near_boundary_abs_d_lte_1") or {}
    true_boundary_rows = int(baseline_true_boundary.get("rows") or 0)

    lines.extend(
        [
            "",
            "## Candidate Manifests",
            "",
            "| candidate | type | features | model hash | forward collection allowed | promotion registry allowed |",
            "|---|---|---:|---|---:|---:|",
        ]
    )
    for manifest in manifests:
        lines.append(
            f"| `{manifest['candidate_id']}` | `{manifest['model_type']}` | {len(manifest['feature_columns'])} | "
            f"`{manifest['model_hash']}` | {manifest['allowed_for_forward_collection']} | {manifest['allowed_for_forward_registry']} |"
        )

    lines.extend(
        [
            "",
            "## Read",
            "",
            "- Probability quality is scored before shadow economics.",
            "- The holdout split is market-level chronological, so rows from the same market do not cross train/holdout.",
            "- True near-boundary metrics use logged abs(d_sigma) when present; otherwise the report falls back to the v28 40-60 probability proxy.",
            f"- True near-boundary holdout rows: `{true_boundary_rows}`.",
            "- Non-baseline simple candidates may be frozen for future shadow collection, but no candidate can be promoted from this run because the available rows are diagnostic and there are no post-lock forward rows.",
            "",
            "## Outputs",
            "",
            f"- Candidate predictions: `{rel_path(PREDICTIONS_CSV)}`",
            f"- Candidate manifests: `{rel_path(CANDIDATE_MANIFEST_JSON)}`",
            f"- Metrics CSV: `{rel_path(METRICS_CSV)}`",
            f"- Calibration bins CSV: `{rel_path(BINS_CSV)}`",
        ]
    )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def fmt(value: Any, digits: int = 6) -> str:
    parsed = as_float(value)
    if parsed is None:
        return "NA"
    return f"{parsed:.{digits}f}"


def fmt_pct(value: Any) -> str:
    parsed = as_float(value)
    if parsed is None:
        return "NA"
    return f"{100.0 * parsed:.2f}%"


def build(limit_rows: int | None = None) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]], dict[str, Any]]:
    rows = read_csv_rows(FEATURES_CSV, limit_rows=limit_rows)
    manifest = read_json(FEATURE_MANIFEST_JSON)
    assign_market_chronological_splits(rows)
    candidates = fit_candidates(rows, manifest)
    predictions = prediction_long_rows(rows, candidates)
    metrics, bins = score_predictions(predictions, [candidate["candidate_id"] for candidate in candidates])
    feature_manifest_hash = stable_hash(manifest)
    manifests = candidate_manifest_rows(candidates, metrics, rows, feature_manifest_hash, sha256_file(FEATURES_CSV))
    promotion_verdict = "not_promotable"
    if all(manifest_row["promotion_gate"]["promotable"] for manifest_row in manifests if manifest_row["candidate_id"] != "v28_raw"):
        promotion_verdict = "promotable"
    summary = {
        "generated_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "builder_script": Path(__file__).name,
        "row_count": len(rows),
        "candidate_count": len(candidates),
        "promotion_verdict": promotion_verdict,
        "split_summary": split_summary(rows),
        "inputs": {
            "feature_table": rel_path(FEATURES_CSV),
            "feature_table_hash": sha256_file(FEATURES_CSV),
            "feature_manifest": rel_path(FEATURE_MANIFEST_JSON),
            "feature_manifest_hash": feature_manifest_hash,
        },
        "outputs": {
            "predictions_csv": rel_path(PREDICTIONS_CSV),
            "candidate_manifest_json": rel_path(CANDIDATE_MANIFEST_JSON),
            "calibration_report_md": rel_path(CALIBRATION_MD),
            "calibration_report_json": rel_path(CALIBRATION_JSON),
            "metrics_csv": rel_path(METRICS_CSV),
            "bins_csv": rel_path(BINS_CSV),
        },
        "notes": [
            "Research-only diagnostic candidate scoring.",
            "Models are trained on train split only.",
            "Promotion is closed for posthoc source rows and zero post-lock forward rows.",
        ],
    }
    return rows, predictions, manifests, metrics, bins, summary


def write_outputs(
    predictions: list[dict[str, Any]],
    manifests: list[dict[str, Any]],
    metrics: list[dict[str, Any]],
    bins: list[dict[str, Any]],
    summary: dict[str, Any],
) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    EDGE_DIR.mkdir(parents=True, exist_ok=True)
    write_csv_rows(predictions, PREDICTIONS_CSV)
    PREDICTIONS_JSON.write_text(json.dumps({"rows": predictions}, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    CANDIDATE_MANIFEST_JSON.write_text(json.dumps(manifests, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_csv_rows(metrics, METRICS_CSV)
    write_csv_rows(bins, BINS_CSV)
    CALIBRATION_JSON.write_text(
        json.dumps({"summary": summary, "candidate_manifests": manifests, "metrics": metrics, "calibration_bins": bins}, indent=2, sort_keys=True)
        + "\n",
        encoding="utf-8",
    )
    write_markdown(summary, manifests, metrics, CALIBRATION_MD)


def main() -> None:
    parser = argparse.ArgumentParser(description="Train diagnostic v28 successor FV candidates.")
    parser.add_argument("--write", action="store_true", help="Write training/scoring artifacts.")
    parser.add_argument("--dry-run", action="store_true", help="Build artifacts in memory only.")
    parser.add_argument("--limit-rows", type=int, default=None, help="Optional smoke-test row limit.")
    args = parser.parse_args()

    _rows, predictions, manifests, metrics, bins, summary = build(limit_rows=args.limit_rows)
    if args.write and not args.dry_run:
        write_outputs(predictions, manifests, metrics, bins, summary)
    print(
        json.dumps(
            {
                "row_count": summary["row_count"],
                "candidate_count": summary["candidate_count"],
                "promotion_verdict": summary["promotion_verdict"],
                "split_summary": summary["split_summary"],
                "written": bool(args.write and not args.dry_run),
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
