"""Build leakage-safe feature artifacts for the v28 successor FV seed dataset.

This script reads research_particle/v28_successor/causal_rows_seed_latest.csv
and writes:
- research_particle/v28_successor/features_latest.csv
- research_particle/v28_successor/feature_manifest_latest.json
- logs/edge_research/v28_successor_feature_audit_latest.json
- logs/edge_research/v28_successor_feature_audit_latest.md

The output table can contain target/metadata columns for joining and scoring, but
only columns listed in the feature manifest are model features. Settlement,
outcome, Brier, logloss, and P&L columns are deliberately excluded from the
manifest.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
from collections import Counter
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "research_particle" / "v28_successor"
EDGE_DIR = ROOT / "logs" / "edge_research"

ROWS_CSV = OUT_DIR / "causal_rows_seed_latest.csv"
FEATURES_CSV = OUT_DIR / "features_latest.csv"
FEATURES_JSON = OUT_DIR / "features_latest.json"
FEATURE_MANIFEST_JSON = OUT_DIR / "feature_manifest_latest.json"
FEATURE_AUDIT_JSON = EDGE_DIR / "v28_successor_feature_audit_latest.json"
FEATURE_AUDIT_MD = EDGE_DIR / "v28_successor_feature_audit_latest.md"

LEAKY_NAME_TOKENS = [
    "outcome",
    "label",
    "settlement",
    "pnl",
    "gross",
    "brier",
    "logloss",
    "win",
    "won",
    "result",
]

FINAL_AVG_WINDOW_SECONDS = 90.0


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


def has_leaky_token(name: str) -> bool:
    tokens = [part for part in re_split_name(name.lower()) if part]
    return any(token in LEAKY_NAME_TOKENS for token in tokens)


def re_split_name(name: str) -> list[str]:
    out: list[str] = []
    current: list[str] = []
    for char in name:
        if char.isalnum():
            current.append(char)
        else:
            if current:
                out.append("".join(current))
                current = []
    if current:
        out.append("".join(current))
    return out


def as_float(value: Any) -> float | None:
    if value is None:
        return None
    text = str(value).strip()
    if text == "":
        return None
    try:
        out = float(text)
    except ValueError:
        return None
    if not math.isfinite(out):
        return None
    return out


def as_bool(value: Any) -> bool | None:
    if isinstance(value, bool):
        return value
    if value is None:
        return None
    text = str(value).strip().lower()
    if text in {"true", "1", "yes", "y"}:
        return True
    if text in {"false", "0", "no", "n"}:
        return False
    return None


def bool01(value: Any) -> int:
    return 1 if as_bool(value) is True else 0


def safe_float(value: Any, default: float = 0.0) -> float:
    parsed = as_float(value)
    return default if parsed is None else parsed


def safe_probability(value: Any) -> float:
    parsed = as_float(value)
    if parsed is None:
        return 0.5
    return min(1.0 - 1e-9, max(1e-9, parsed))


def logit(value: Any) -> float:
    p = safe_probability(value)
    return math.log(p / (1.0 - p))


def log1p_nonnegative(value: Any) -> float:
    parsed = as_float(value)
    if parsed is None:
        return 0.0
    return math.log1p(max(0.0, parsed))


def missing01(value: Any) -> int:
    return 1 if as_float(value) is None else 0


def strike_minus_btc_dollars(row: dict[str, Any]) -> float:
    strike = as_float(row.get("strike"))
    btc = as_float(row.get("btc_price"))
    if strike is None or btc is None:
        return 0.0
    return strike - btc


def final_avg_raw_horizon_minutes(row: dict[str, Any]) -> float:
    return max(safe_float(row.get("seconds_to_close")) / 60.0, 1e-6)


def final_avg_effective_horizon_minutes_for_seconds(
    seconds_to_close: Any,
    avg_window_seconds: float = FINAL_AVG_WINDOW_SECONDS,
) -> float:
    h_min = max(safe_float(seconds_to_close) / 60.0, 1e-6)
    avg_min = max(float(avg_window_seconds), 0.0) / 60.0
    if avg_min <= 0.0:
        return h_min
    if h_min >= avg_min:
        return max(h_min - (2.0 / 3.0) * avg_min, 0.02)
    return max((h_min * h_min * h_min) / (3.0 * avg_min * avg_min), 0.002)


def final_avg_effective_horizon_minutes(row: dict[str, Any]) -> float:
    return final_avg_effective_horizon_minutes_for_seconds(row.get("seconds_to_close"))


def final_avg_variance_compression(row: dict[str, Any]) -> float:
    raw_h = final_avg_raw_horizon_minutes(row)
    eff_h = final_avg_effective_horizon_minutes(row)
    return min(1.0, max(0.0, eff_h / max(raw_h, 1e-9)))


def final_avg_uncertainty_scale(row: dict[str, Any]) -> float:
    return math.sqrt(final_avg_variance_compression(row))


def final_avg_elapsed_window_fraction(row: dict[str, Any]) -> float:
    avg_min = FINAL_AVG_WINDOW_SECONDS / 60.0
    if avg_min <= 0.0:
        return 0.0
    h_min = final_avg_raw_horizon_minutes(row)
    return min(1.0, max(0.0, (avg_min - h_min) / avg_min))


def final_avg_sigma_proxy_dollars(row: dict[str, Any]) -> float:
    sigma = safe_float(row.get("sigma_t_dollars"))
    return max(0.0, sigma * final_avg_uncertainty_scale(row))


def final_avg_d_sigma_proxy(row: dict[str, Any]) -> float:
    sigma = final_avg_sigma_proxy_dollars(row)
    if sigma <= 1e-9:
        return 0.0
    return strike_minus_btc_dollars(row) / sigma


def final_avg_abs_d_sigma_proxy(row: dict[str, Any]) -> float:
    return abs(final_avg_d_sigma_proxy(row))


@dataclass(frozen=True)
class FeatureDef:
    name: str
    family: str
    model_tracks: tuple[str, ...]
    timestamp_basis: str
    source_columns: tuple[str, ...]
    missing_value_policy: str
    leakage_risk: str
    transform: str
    fn: Callable[[dict[str, Any]], float]

    def manifest_row(self) -> dict[str, Any]:
        return {
            "feature_name": self.name,
            "feature_family": self.family,
            "model_track_allowed": list(self.model_tracks),
            "timestamp_basis": self.timestamp_basis,
            "source_columns": list(self.source_columns),
            "missing_value_policy": self.missing_value_policy,
            "leakage_risk": self.leakage_risk,
            "normalization_or_transform": self.transform,
        }


FEATURES: tuple[FeatureDef, ...] = (
    FeatureDef(
        "v28_logit_yes",
        "v28_derived",
        ("pure_physics", "book_aware", "reliability"),
        "v28 prediction logged before the source decision row; seed decision_ts inferred from seconds_to_close",
        ("v28_p_yes",),
        "missing p_yes is imputed to 0.5",
        "low",
        "logit(clamp(v28_p_yes))",
        lambda row: logit(row.get("v28_p_yes")),
    ),
    FeatureDef(
        "v28_p_yes_centered",
        "v28_derived",
        ("pure_physics", "book_aware", "reliability"),
        "v28 prediction logged before the source decision row; seed decision_ts inferred from seconds_to_close",
        ("v28_p_yes",),
        "missing p_yes is imputed to 0.5",
        "low",
        "v28_p_yes - 0.5",
        lambda row: safe_probability(row.get("v28_p_yes")) - 0.5,
    ),
    FeatureDef(
        "v28_abs_logit_yes",
        "v28_derived",
        ("pure_physics", "book_aware", "reliability"),
        "v28 prediction logged before the source decision row; seed decision_ts inferred from seconds_to_close",
        ("v28_p_yes",),
        "missing p_yes is imputed to 0.5",
        "low",
        "abs(logit(clamp(v28_p_yes)))",
        lambda row: abs(logit(row.get("v28_p_yes"))),
    ),
    FeatureDef(
        "v28_side_probability",
        "v28_derived",
        ("book_aware", "reliability"),
        "v28 side probability from source row",
        ("v28_p_side",),
        "missing p_side is imputed to 0.5",
        "medium",
        "clamp(v28_p_side)",
        lambda row: safe_probability(row.get("v28_p_side")),
    ),
    FeatureDef(
        "seconds_to_close",
        "time_geometry",
        ("pure_physics", "book_aware", "reliability"),
        "source row seconds_to_close at decision time",
        ("seconds_to_close",),
        "missing seconds_to_close is imputed to 0",
        "low",
        "float(seconds_to_close)",
        lambda row: safe_float(row.get("seconds_to_close")),
    ),
    FeatureDef(
        "minutes_to_close",
        "time_geometry",
        ("pure_physics", "book_aware", "reliability"),
        "source row seconds_to_close at decision time",
        ("seconds_to_close",),
        "missing seconds_to_close is imputed to 0",
        "low",
        "seconds_to_close / 60",
        lambda row: safe_float(row.get("seconds_to_close")) / 60.0,
    ),
    FeatureDef(
        "time_frac_15m",
        "time_geometry",
        ("pure_physics", "book_aware", "reliability"),
        "source row seconds_to_close at decision time",
        ("seconds_to_close",),
        "missing seconds_to_close is imputed to 0",
        "low",
        "clip(seconds_to_close / 900, 0, 1)",
        lambda row: min(1.0, max(0.0, safe_float(row.get("seconds_to_close")) / 900.0)),
    ),
    FeatureDef(
        "late_window_lte_180s",
        "time_geometry",
        ("pure_physics", "book_aware", "reliability"),
        "source row seconds_to_close at decision time",
        ("seconds_to_close",),
        "missing seconds_to_close maps to 0",
        "low",
        "1 if seconds_to_close <= 180 and present else 0",
        lambda row: 1 if (as_float(row.get("seconds_to_close")) is not None and as_float(row.get("seconds_to_close")) <= 180.0) else 0,
    ),
    FeatureDef(
        "final_avg_effective_horizon_minutes",
        "final_avg_physics",
        ("pure_physics", "book_aware", "reliability"),
        "decision-time clock transformed with a predeclared 90s final-average Brownian variance proxy",
        ("seconds_to_close",),
        "missing seconds_to_close maps to the minimum horizon floor",
        "low",
        "if h >= avg: h - 2avg/3 else h^3/(3avg^2), avg=90s",
        final_avg_effective_horizon_minutes,
    ),
    FeatureDef(
        "final_avg_variance_compression",
        "final_avg_physics",
        ("pure_physics", "book_aware", "reliability"),
        "decision-time clock transformed with a predeclared 90s final-average Brownian variance proxy",
        ("seconds_to_close",),
        "missing seconds_to_close maps to the minimum horizon floor",
        "low",
        "effective final-average horizon / raw horizon, clipped to [0, 1]",
        final_avg_variance_compression,
    ),
    FeatureDef(
        "final_avg_uncertainty_scale",
        "final_avg_physics",
        ("pure_physics", "book_aware", "reliability"),
        "decision-time clock transformed with a predeclared 90s final-average Brownian variance proxy",
        ("seconds_to_close",),
        "missing seconds_to_close maps to the minimum horizon floor",
        "low",
        "sqrt(final_avg_variance_compression)",
        final_avg_uncertainty_scale,
    ),
    FeatureDef(
        "final_avg_elapsed_window_fraction",
        "final_avg_physics",
        ("pure_physics", "book_aware", "reliability"),
        "decision-time clock only; no future final-average samples are read",
        ("seconds_to_close",),
        "missing seconds_to_close maps to 0",
        "low",
        "clip((90s - seconds_to_close) / 90s, 0, 1)",
        final_avg_elapsed_window_fraction,
    ),
    FeatureDef(
        "final_avg_sigma_proxy_dollars",
        "final_avg_physics",
        ("pure_physics", "book_aware", "reliability"),
        "decision-time clock and v28 sigma transformed with a predeclared 90s final-average Brownian variance proxy",
        ("seconds_to_close", "sigma_t_dollars"),
        "missing sigma maps to 0",
        "low",
        "sigma_t_dollars * final_avg_uncertainty_scale",
        final_avg_sigma_proxy_dollars,
    ),
    FeatureDef(
        "final_avg_d_sigma_proxy",
        "final_avg_physics",
        ("pure_physics", "book_aware", "reliability"),
        "decision-time strike, BTC, clock, and v28 sigma; no future final-average samples are read",
        ("seconds_to_close", "sigma_t_dollars", "strike", "btc_price"),
        "missing strike/BTC/sigma maps to 0",
        "low",
        "(strike - btc_price) / final_avg_sigma_proxy_dollars",
        final_avg_d_sigma_proxy,
    ),
    FeatureDef(
        "final_avg_abs_d_sigma_proxy",
        "final_avg_physics",
        ("pure_physics", "book_aware", "reliability"),
        "decision-time strike, BTC, clock, and v28 sigma; no future final-average samples are read",
        ("seconds_to_close", "sigma_t_dollars", "strike", "btc_price"),
        "missing strike/BTC/sigma maps to 0",
        "low",
        "abs(final_avg_d_sigma_proxy)",
        final_avg_abs_d_sigma_proxy,
    ),
    FeatureDef(
        "sigma_t_dollars",
        "v28_derived",
        ("pure_physics", "book_aware", "reliability"),
        "v28 sigma at source decision row",
        ("sigma_t_dollars",),
        "missing sigma is imputed to 0 with companion missing flag",
        "low",
        "float(sigma_t_dollars)",
        lambda row: safe_float(row.get("sigma_t_dollars")),
    ),
    FeatureDef(
        "log1p_sigma_t_dollars",
        "v28_derived",
        ("pure_physics", "book_aware", "reliability"),
        "v28 sigma at source decision row",
        ("sigma_t_dollars",),
        "missing sigma is imputed to 0 with companion missing flag",
        "low",
        "log1p(max(sigma_t_dollars, 0))",
        lambda row: log1p_nonnegative(row.get("sigma_t_dollars")),
    ),
    FeatureDef(
        "sigma_t_missing",
        "missingness",
        ("pure_physics", "book_aware", "reliability"),
        "observed missingness in source row",
        ("sigma_t_dollars",),
        "missingness indicator",
        "low",
        "1 if sigma_t_dollars missing else 0",
        lambda row: missing01(row.get("sigma_t_dollars")),
    ),
    FeatureDef(
        "recross_hazard_score",
        "boundary_reliability",
        ("pure_physics", "book_aware", "reliability"),
        "predeclared recross score stored in source calibration row",
        ("recross_hazard_score",),
        "missing recross score is imputed to 0 with companion missing flag",
        "medium",
        "float(recross_hazard_score)",
        lambda row: safe_float(row.get("recross_hazard_score")),
    ),
    FeatureDef(
        "recross_hazard_missing",
        "missingness",
        ("pure_physics", "book_aware", "reliability"),
        "observed missingness in source row",
        ("recross_hazard_score",),
        "missingness indicator",
        "low",
        "1 if recross_hazard_score missing else 0",
        lambda row: missing01(row.get("recross_hazard_score")),
    ),
    FeatureDef(
        "recross_hazard_high",
        "boundary_reliability",
        ("pure_physics", "book_aware", "reliability"),
        "predeclared recross high flag stored in source calibration row",
        ("h6_recross_hazard_high",),
        "missing maps to 0",
        "medium",
        "1 if h6_recross_hazard_high true else 0",
        lambda row: bool01(row.get("h6_recross_hazard_high")),
    ),
    FeatureDef(
        "ask_cents",
        "book_aware_execution",
        ("book_aware",),
        "executable ask recorded in source row",
        ("ask_cents",),
        "missing ask is imputed to 100 with companion missing flag",
        "medium",
        "float(ask_cents), missing=>100",
        lambda row: safe_float(row.get("ask_cents"), default=100.0),
    ),
    FeatureDef(
        "ask_missing",
        "missingness",
        ("book_aware", "reliability"),
        "observed missingness in source row",
        ("ask_cents",),
        "missingness indicator",
        "low",
        "1 if ask_cents missing else 0",
        lambda row: missing01(row.get("ask_cents")),
    ),
    FeatureDef(
        "ask_frac",
        "book_aware_execution",
        ("book_aware",),
        "executable ask recorded in source row",
        ("ask_cents",),
        "missing ask is imputed to 100",
        "medium",
        "ask_cents / 100",
        lambda row: safe_float(row.get("ask_cents"), default=100.0) / 100.0,
    ),
    FeatureDef(
        "edge_cents",
        "book_aware_execution",
        ("book_aware",),
        "v28 model edge after executable price in source row",
        ("edge_cents",),
        "missing edge is imputed to 0 with companion missing flag",
        "medium",
        "float(edge_cents)",
        lambda row: safe_float(row.get("edge_cents")),
    ),
    FeatureDef(
        "edge_missing",
        "missingness",
        ("book_aware", "reliability"),
        "observed missingness in source row",
        ("edge_cents",),
        "missingness indicator",
        "low",
        "1 if edge_cents missing else 0",
        lambda row: missing01(row.get("edge_cents")),
    ),
    FeatureDef(
        "side_is_yes",
        "row_context",
        ("book_aware", "reliability"),
        "side considered by the row; not a settlement label",
        ("side",),
        "missing/NO maps to 0",
        "low",
        "1 if side == yes else 0",
        lambda row: 1 if str(row.get("side") or "").lower() == "yes" else 0,
    ),
    FeatureDef(
        "source_is_entry",
        "source_reliability",
        ("reliability",),
        "source type assigned by seed builder",
        ("source_type",),
        "missing maps to 0",
        "low",
        "1 if source_type == entry else 0",
        lambda row: 1 if row.get("source_type") == "entry" else 0,
    ),
    FeatureDef(
        "source_is_rejected_actionable",
        "source_reliability",
        ("reliability",),
        "source type assigned by seed builder",
        ("source_type",),
        "missing maps to 0",
        "low",
        "1 if source_type == rejected_actionable else 0",
        lambda row: 1 if row.get("source_type") == "rejected_actionable" else 0,
    ),
)


METADATA_COLUMNS = [
    "row_id",
    "market_ticker",
    "decision_ts_utc",
    "market_close_ts_utc",
    "source_type",
    "source_reason",
    "source_quality_tier",
    "side",
    "allowed_for_training",
    "allowed_for_validation",
    "allowed_for_holdout",
    "allowed_for_forward_promotion",
]

TARGET_COLUMNS = [
    "target_y_yes_win",
    "target_v28_p_yes",
    "target_brier_yes",
    "target_logloss_yes",
]


def read_rows(path: Path, limit_rows: int | None = None) -> list[dict[str, Any]]:
    if not path.exists():
        raise FileNotFoundError(f"Missing causal row seed: {path}")
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        for raw in reader:
            rows.append(raw)
            if limit_rows is not None and len(rows) >= limit_rows:
                break
    return rows


def build_feature_row(row: dict[str, Any]) -> dict[str, Any]:
    out = {col: row.get(col, "") for col in METADATA_COLUMNS}
    out.update(
        {
            "target_y_yes_win": row.get("y_yes_win", ""),
            "target_v28_p_yes": row.get("v28_p_yes", ""),
            "target_brier_yes": row.get("brier_yes", ""),
            "target_logloss_yes": row.get("logloss_yes", ""),
            "row_is_posthoc": bool01(row.get("is_recomputed_after_resolution")),
            "row_is_simulated": bool01(row.get("is_simulated")),
        }
    )
    for feature in FEATURES:
        out[feature.name] = feature.fn(row)
    return out


def build_feature_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [build_feature_row(row) for row in rows]


def manifest_rows() -> list[dict[str, Any]]:
    return [feature.manifest_row() for feature in FEATURES]


def leakage_audit(manifest: list[dict[str, Any]], feature_rows: list[dict[str, Any]]) -> dict[str, Any]:
    feature_names = [row["feature_name"] for row in manifest]
    leaky_by_name = [
        name for name in feature_names
        if has_leaky_token(name)
    ]
    leaky_by_source = []
    for row in manifest:
        sources = [str(col) for col in row.get("source_columns", [])]
        if any(has_leaky_token(col) for col in sources):
            leaky_by_source.append(row["feature_name"])
    nan_or_inf = []
    for name in feature_names:
        for idx, row in enumerate(feature_rows):
            value = as_float(row.get(name))
            if value is None or not math.isfinite(value):
                nan_or_inf.append({"feature": name, "row_index": idx})
                break
    status = "pass" if not leaky_by_name and not leaky_by_source and not nan_or_inf else "fail"
    return {
        "status": status,
        "feature_count": len(feature_names),
        "leaky_feature_names": leaky_by_name,
        "leaky_source_columns": leaky_by_source,
        "features_with_nan_or_inf": nan_or_inf,
        "label_columns_present_but_not_features": TARGET_COLUMNS,
        "notes": [
            "Target columns are included for scoring joins but are not in the feature manifest.",
            "P&L/gross, Brier, logloss, settlement, outcome, and win/result columns are excluded from feature columns.",
            "Book-aware execution features are isolated to the book_aware track.",
            "All features in this first seed inherit the posthoc source caveat from the seed rows.",
        ],
    }


def missing_summary(feature_rows: list[dict[str, Any]], manifest: list[dict[str, Any]]) -> dict[str, int]:
    out: dict[str, int] = {}
    for row in manifest:
        name = row["feature_name"]
        out[name] = sum(1 for item in feature_rows if as_float(item.get(name)) is None)
    return out


def track_summary(manifest: list[dict[str, Any]]) -> dict[str, int]:
    counts: Counter[str] = Counter()
    for row in manifest:
        for track in row.get("model_track_allowed", []):
            counts[str(track)] += 1
    return dict(sorted(counts.items()))


def summarize(rows: list[dict[str, Any]], feature_rows: list[dict[str, Any]], manifest: list[dict[str, Any]]) -> dict[str, Any]:
    dataset_hash = sha256_file(ROWS_CSV)
    feature_manifest_hash = stable_hash(manifest)
    tracks = track_summary(manifest)
    leakage = leakage_audit(manifest, feature_rows)
    source_counts = Counter(row.get("source_type", "") for row in rows)
    return {
        "created_utc": datetime.now(tz=timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "builder_script": rel_path(Path(__file__)),
        "input_rows_path": rel_path(ROWS_CSV),
        "input_rows_hash": dataset_hash,
        "row_count": len(rows),
        "feature_row_count": len(feature_rows),
        "feature_count": len(manifest),
        "feature_manifest_hash": feature_manifest_hash,
        "track_feature_counts": tracks,
        "source_counts": dict(sorted(source_counts.items())),
        "metadata_columns": METADATA_COLUMNS,
        "target_columns": TARGET_COLUMNS,
        "feature_columns": [row["feature_name"] for row in manifest],
        "missing_feature_values": missing_summary(feature_rows, manifest),
        "leakage_audit": leakage,
        "outputs": {
            "features_csv": rel_path(FEATURES_CSV),
            "features_json": rel_path(FEATURES_JSON),
            "feature_manifest_json": rel_path(FEATURE_MANIFEST_JSON),
            "feature_audit_json": rel_path(FEATURE_AUDIT_JSON),
            "feature_audit_md": rel_path(FEATURE_AUDIT_MD),
        },
    }


def write_csv_rows(rows: list[dict[str, Any]], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    fieldnames = list(rows[0].keys())
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def write_markdown(summary: dict[str, Any], manifest: list[dict[str, Any]], path: Path) -> None:
    lines = [
        "# v28 Successor Feature Audit",
        "",
        "Research-only feature artifact for the v28 successor FV pipeline. This script reads the seed dataset and writes model-ready features plus a manifest; it does not touch live bot state or processes.",
        "",
        "## Summary",
        "",
        f"- Created UTC: `{summary['created_utc']}`",
        f"- Builder: `{summary['builder_script']}`",
        f"- Input rows: `{summary['input_rows_path']}`",
        f"- Input row hash: `{summary['input_rows_hash']}`",
        f"- Rows: `{summary['row_count']}`",
        f"- Feature rows: `{summary['feature_row_count']}`",
        f"- Features: `{summary['feature_count']}`",
        f"- Feature manifest hash: `{summary['feature_manifest_hash']}`",
        "",
        "## Track Coverage",
        "",
        "| track | feature count |",
        "|---|---:|",
    ]
    for track, count in summary["track_feature_counts"].items():
        lines.append(f"| {track} | {count} |")

    lines.extend(["", "## Source Rows", "", "| source | rows |", "|---|---:|"])
    for source, count in summary["source_counts"].items():
        lines.append(f"| {source} | {count} |")

    lines.extend(["", "## Leakage Audit", "", f"- Status: `{summary['leakage_audit']['status']}`"])
    if summary["leakage_audit"]["leaky_feature_names"]:
        lines.append(f"- Leaky feature names: `{summary['leakage_audit']['leaky_feature_names']}`")
    if summary["leakage_audit"]["leaky_source_columns"]:
        lines.append(f"- Leaky source columns: `{summary['leakage_audit']['leaky_source_columns']}`")
    if summary["leakage_audit"]["features_with_nan_or_inf"]:
        lines.append(f"- Features with NaN/Inf: `{summary['leakage_audit']['features_with_nan_or_inf']}`")
    for note in summary["leakage_audit"]["notes"]:
        lines.append(f"- {note}")

    lines.extend(["", "## Feature Manifest", "", "| feature | family | tracks | source columns | leakage risk | transform |", "|---|---|---|---|---|---|"])
    for item in manifest:
        lines.append(
            f"| `{item['feature_name']}` | {item['feature_family']} | {', '.join(item['model_track_allowed'])} | "
            f"{', '.join(item['source_columns'])} | {item['leakage_risk']} | {item['normalization_or_transform']} |"
        )

    lines.extend(["", "## Missing Feature Values", "", "| feature | missing values |", "|---|---:|"])
    for feature, count in summary["missing_feature_values"].items():
        lines.append(f"| `{feature}` | {count} |")

    lines.extend([
        "",
        "## Read",
        "",
        "- This feature table is suitable for smoke-test calibration work only; the underlying seed rows remain posthoc diagnostic rows.",
        "- The manifest cleanly separates pure-physics, book-aware, and reliability features.",
        "- No feature names or source columns include settlement/outcome/P&L/Brier/logloss/win/result fields.",
    ])
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def build(limit_rows: int | None = None) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]], dict[str, Any]]:
    rows = read_rows(ROWS_CSV, limit_rows=limit_rows)
    feature_rows = build_feature_rows(rows)
    manifest = manifest_rows()
    summary = summarize(rows, feature_rows, manifest)
    return rows, feature_rows, manifest, summary


def write_outputs(feature_rows: list[dict[str, Any]], manifest: list[dict[str, Any]], summary: dict[str, Any]) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    EDGE_DIR.mkdir(parents=True, exist_ok=True)
    write_csv_rows(feature_rows, FEATURES_CSV)
    FEATURES_JSON.write_text(json.dumps({"rows": feature_rows}, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    FEATURE_MANIFEST_JSON.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    FEATURE_AUDIT_JSON.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_markdown(summary, manifest, FEATURE_AUDIT_MD)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true", help="Write feature artifacts.")
    parser.add_argument("--dry-run", action="store_true", help="Build and summarize without writing.")
    parser.add_argument("--limit-rows", type=int, default=None, help="Limit rows for smoke testing.")
    args = parser.parse_args()

    _rows, feature_rows, manifest, summary = build(limit_rows=args.limit_rows)
    if args.write and not args.dry_run:
        write_outputs(feature_rows, manifest, summary)
    print(
        json.dumps(
            {
                "row_count": summary["row_count"],
                "feature_count": summary["feature_count"],
                "leakage_status": summary["leakage_audit"]["status"],
                "track_feature_counts": summary["track_feature_counts"],
                "written": bool(args.write and not args.dry_run),
                "features_csv": rel_path(FEATURES_CSV),
                "feature_audit_md": rel_path(FEATURE_AUDIT_MD),
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
