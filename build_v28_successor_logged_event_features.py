"""Build richer leakage-safe features from logged v28 event rows.

Research-only. This consumes
research_particle/v28_successor/causal_rows_logged_events_latest.csv and writes
separate logged-event feature artifacts. The rows are pre-resolution by event
clock but diagnostic-only because their labels come from the posthoc seed label
lookup.
"""
from __future__ import annotations

import argparse
import csv
import json
import math
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from build_v28_successor_features import (
    EDGE_DIR,
    OUT_DIR,
    ROOT,
    FeatureDef,
    FEATURES as BASE_FEATURES,
    TARGET_COLUMNS,
    as_bool,
    as_float,
    bool01,
    has_leaky_token,
    log1p_nonnegative,
    logit,
    missing01,
    rel_path,
    safe_float,
    safe_probability,
    sha256_file,
    stable_hash,
    track_summary,
    write_csv_rows,
)


LOGGED_ROWS_CSV = OUT_DIR / "causal_rows_logged_events_latest.csv"
API_REPLAY_CSV = OUT_DIR / "v28_logged_event_api_replay_latest.csv"
FEATURES_CSV = OUT_DIR / "features_logged_events_latest.csv"
FEATURES_JSON = OUT_DIR / "features_logged_events_latest.json"
FEATURE_MANIFEST_JSON = OUT_DIR / "feature_manifest_logged_events_latest.json"
FEATURE_AUDIT_JSON = EDGE_DIR / "v28_successor_logged_event_feature_audit_latest.json"
FEATURE_AUDIT_MD = EDGE_DIR / "v28_successor_logged_event_feature_audit_latest.md"


METADATA_COLUMNS = [
    "row_id",
    "dataset_role",
    "market_ticker",
    "decision_ts_utc",
    "market_close_ts_utc",
    "source_type",
    "source_quality_tier",
    "side",
    "strike",
    "label_source",
    "allowed_for_training",
    "allowed_for_validation",
    "allowed_for_holdout",
    "allowed_for_forward_promotion",
]


def side_book_implied_yes(row: dict[str, Any]) -> float:
    ask = as_float(row.get("ask_cents"))
    side = str(row.get("side") or "").lower()
    if ask is None:
        return 0.5
    ask_p = min(1.0, max(0.0, ask / 100.0))
    if side == "yes":
        return ask_p
    if side == "no":
        return 1.0 - ask_p
    return 0.5


def strike_minus_btc(row: dict[str, Any]) -> float:
    strike = as_float(row.get("strike"))
    btc = as_float(row.get("btc_price"))
    if strike is None or btc is None:
        return 0.0
    return strike - btc


def distance_per_sigma(row: dict[str, Any]) -> float:
    sigma = as_float(row.get("sigma_t_dollars"))
    if sigma is None or abs(sigma) < 1e-9:
        return 0.0
    return strike_minus_btc(row) / sigma


def freshness_max(row: dict[str, Any]) -> float:
    values = [
        as_float(row.get("btc_age_ms")),
        as_float(row.get("book_age_ms")),
        as_float(row.get("feed_age_ms")),
    ]
    finite = [value for value in values if value is not None]
    return max(finite) if finite else 0.0


LOGGED_EVENT_FEATURES: tuple[FeatureDef, ...] = (
    FeatureDef(
        "v28_api_replay_available",
        "v28_api_replay",
        ("pure_physics", "reliability"),
        "research-only v28 API replay joined by row_id; uses predecision BTC cache and logged market geometry",
        ("api_replay_available",),
        "missing maps to 0",
        "medium",
        "1 if reconstructed v28 API replay is available for this row",
        lambda row: bool01(row.get("api_replay_available")),
    ),
    FeatureDef(
        "v28_api_replay_p_anchor",
        "v28_api_replay",
        ("pure_physics", "book_aware", "reliability"),
        "research-only v28 API replay joined by row_id",
        ("replay_p_anchor",),
        "missing maps to 0.5",
        "medium",
        "clamped replay p_anchor",
        lambda row: safe_probability(row.get("replay_p_anchor")),
    ),
    FeatureDef(
        "v28_api_replay_p_static_boundary_field",
        "v28_api_replay",
        ("pure_physics", "book_aware", "reliability"),
        "research-only v28 API replay joined by row_id",
        ("replay_p_static_boundary_field",),
        "missing maps to 0.5",
        "medium",
        "clamped replay p_static_boundary_field",
        lambda row: safe_probability(row.get("replay_p_static_boundary_field")),
    ),
    FeatureDef(
        "v28_api_replay_p_recent_transport",
        "v28_api_replay",
        ("pure_physics", "book_aware", "reliability"),
        "research-only v28 API replay joined by row_id",
        ("replay_p_recent_transport",),
        "missing maps to 0.5",
        "medium",
        "clamped replay p_recent_transport",
        lambda row: safe_probability(row.get("replay_p_recent_transport")),
    ),
    FeatureDef(
        "v28_api_replay_p_long_transport",
        "v28_api_replay",
        ("pure_physics", "book_aware", "reliability"),
        "research-only v28 API replay joined by row_id",
        ("replay_p_long_transport",),
        "missing maps to 0.5",
        "medium",
        "clamped replay p_long_transport",
        lambda row: safe_probability(row.get("replay_p_long_transport")),
    ),
    FeatureDef(
        "v28_api_replay_edge_gate",
        "v28_api_replay",
        ("pure_physics", "reliability"),
        "research-only v28 API replay joined by row_id",
        ("replay_edge_gate",),
        "missing maps to 0.5",
        "medium",
        "clamped replay transport edge gate",
        lambda row: safe_probability(row.get("replay_edge_gate")),
    ),
    FeatureDef(
        "v28_api_replay_static_gate",
        "v28_api_replay",
        ("pure_physics", "reliability"),
        "research-only v28 API replay joined by row_id",
        ("replay_static_gate",),
        "missing maps to 0.5",
        "medium",
        "clamped replay static boundary gate",
        lambda row: safe_probability(row.get("replay_static_gate")),
    ),
    FeatureDef(
        "log1p_v28_api_replay_transport_recent_n",
        "v28_api_replay",
        ("pure_physics", "reliability"),
        "research-only v28 API replay joined by row_id",
        ("replay_transport_recent_n",),
        "missing maps to 0",
        "medium",
        "log1p(replay transport recent sample count)",
        lambda row: log1p_nonnegative(row.get("replay_transport_recent_n")),
    ),
    FeatureDef(
        "log1p_v28_api_replay_transport_long_n",
        "v28_api_replay",
        ("pure_physics", "reliability"),
        "research-only v28 API replay joined by row_id",
        ("replay_transport_long_n",),
        "missing maps to 0",
        "medium",
        "log1p(replay transport long sample count)",
        lambda row: log1p_nonnegative(row.get("replay_transport_long_n")),
    ),
    FeatureDef(
        "v28_api_replay_minus_logged_p_yes",
        "v28_api_replay",
        ("reliability",),
        "research-only v28 API replay joined by row_id",
        ("replay_minus_logged_v28_p_yes",),
        "missing maps to 0",
        "medium",
        "replay p_yes minus originally logged p_yes",
        lambda row: safe_float(row.get("replay_minus_logged_v28_p_yes")),
    ),
    FeatureDef(
        "v28_api_replay_abs_p_delta",
        "v28_api_replay",
        ("reliability",),
        "research-only v28 API replay joined by row_id",
        ("replay_minus_logged_v28_p_yes",),
        "missing maps to 0",
        "medium",
        "abs(replay p_yes minus originally logged p_yes)",
        lambda row: abs(safe_float(row.get("replay_minus_logged_v28_p_yes"))),
    ),
    FeatureDef(
        "v28_api_replay_minus_logged_sigma",
        "v28_api_replay",
        ("reliability",),
        "research-only v28 API replay joined by row_id",
        ("replay_minus_logged_sigma_t_dollars",),
        "missing maps to 0",
        "medium",
        "replay sigma_t minus originally logged sigma_t",
        lambda row: safe_float(row.get("replay_minus_logged_sigma_t_dollars")),
    ),
    FeatureDef(
        "v28_api_replay_minus_logged_d_sigma",
        "v28_api_replay",
        ("reliability",),
        "research-only v28 API replay joined by row_id",
        ("replay_minus_logged_d_sigma",),
        "missing maps to 0",
        "medium",
        "replay d_sigma minus originally logged d_sigma",
        lambda row: safe_float(row.get("replay_minus_logged_d_sigma")),
    ),
    FeatureDef(
        "d_sigma",
        "boundary_geometry",
        ("pure_physics", "book_aware", "reliability"),
        "logged v28 output before event decision resolution",
        ("d_sigma",),
        "missing d_sigma is imputed to 0 with companion missing flag",
        "low",
        "float(d_sigma)",
        lambda row: safe_float(row.get("d_sigma")),
    ),
    FeatureDef(
        "abs_d_sigma",
        "boundary_geometry",
        ("pure_physics", "book_aware", "reliability"),
        "logged v28 output before event decision resolution",
        ("abs_d_sigma", "d_sigma"),
        "missing distance is imputed to abs(d_sigma) or 0",
        "low",
        "abs_d_sigma if present else abs(d_sigma)",
        lambda row: safe_float(row.get("abs_d_sigma"), default=abs(safe_float(row.get("d_sigma")))),
    ),
    FeatureDef(
        "d_sigma_missing",
        "missingness",
        ("pure_physics", "book_aware", "reliability"),
        "observed missingness in logged event",
        ("d_sigma",),
        "missingness indicator",
        "low",
        "1 if d_sigma missing else 0",
        lambda row: missing01(row.get("d_sigma")),
    ),
    FeatureDef(
        "boundary_zone_abs_d_lte_1",
        "boundary_geometry",
        ("pure_physics", "book_aware", "reliability"),
        "logged v28 distance to strike before event decision resolution",
        ("abs_d_sigma", "d_sigma"),
        "missing maps to 0",
        "low",
        "1 if abs_d_sigma <= 1 else 0",
        lambda row: 1 if safe_float(row.get("abs_d_sigma"), default=abs(safe_float(row.get("d_sigma")))) <= 1.0 else 0,
    ),
    FeatureDef(
        "strike_minus_btc_dollars",
        "boundary_geometry",
        ("pure_physics", "book_aware", "reliability"),
        "logged strike and BTC price before event decision resolution",
        ("strike", "btc_price"),
        "missing strike/BTC maps to 0 with companion missing flags",
        "low",
        "strike - btc_price",
        strike_minus_btc,
    ),
    FeatureDef(
        "strike_distance_dollars_abs",
        "boundary_geometry",
        ("pure_physics", "book_aware", "reliability"),
        "logged strike and BTC price before event decision resolution",
        ("strike", "btc_price"),
        "missing strike/BTC maps to 0 with companion missing flags",
        "low",
        "abs(strike - btc_price)",
        lambda row: abs(strike_minus_btc(row)),
    ),
    FeatureDef(
        "distance_per_sigma_from_prices",
        "boundary_geometry",
        ("pure_physics", "book_aware", "reliability"),
        "logged strike, BTC price, and v28 sigma before event decision resolution",
        ("strike", "btc_price", "sigma_t_dollars"),
        "missing or zero sigma maps to 0",
        "low",
        "(strike - btc_price) / sigma_t_dollars",
        distance_per_sigma,
    ),
    FeatureDef(
        "strike_missing",
        "missingness",
        ("pure_physics", "book_aware", "reliability"),
        "observed missingness in logged event",
        ("strike",),
        "missingness indicator",
        "low",
        "1 if strike missing else 0",
        lambda row: missing01(row.get("strike")),
    ),
    FeatureDef(
        "btc_price_missing",
        "missingness",
        ("pure_physics", "book_aware", "reliability"),
        "observed missingness in logged event",
        ("btc_price",),
        "missingness indicator",
        "low",
        "1 if btc_price missing else 0",
        lambda row: missing01(row.get("btc_price")),
    ),
    FeatureDef(
        "arrow",
        "v28_derived",
        ("pure_physics", "book_aware", "reliability"),
        "logged v28 boundary arrow before event decision resolution",
        ("arrow",),
        "missing arrow maps to 0",
        "low",
        "float(arrow)",
        lambda row: safe_float(row.get("arrow")),
    ),
    FeatureDef(
        "arrow_x_d_sigma",
        "v28_derived",
        ("pure_physics", "book_aware", "reliability"),
        "logged v28 arrow and distance before event decision resolution",
        ("arrow", "d_sigma"),
        "missing values map to 0",
        "low",
        "arrow * d_sigma",
        lambda row: safe_float(row.get("arrow")) * safe_float(row.get("d_sigma")),
    ),
    FeatureDef(
        "btc_age_ms",
        "feed_freshness",
        ("book_aware", "reliability"),
        "logged feed age before event decision resolution",
        ("btc_age_ms",),
        "missing age maps to 0 with companion missing flag",
        "low",
        "float(btc_age_ms)",
        lambda row: safe_float(row.get("btc_age_ms")),
    ),
    FeatureDef(
        "book_age_ms",
        "feed_freshness",
        ("book_aware", "reliability"),
        "logged book age before event decision resolution",
        ("book_age_ms",),
        "missing age maps to 0 with companion missing flag",
        "low",
        "float(book_age_ms)",
        lambda row: safe_float(row.get("book_age_ms")),
    ),
    FeatureDef(
        "feed_age_ms",
        "feed_freshness",
        ("book_aware", "reliability"),
        "logged feed age before event decision resolution",
        ("feed_age_ms",),
        "missing age maps to 0 with companion missing flag",
        "low",
        "float(feed_age_ms)",
        lambda row: safe_float(row.get("feed_age_ms")),
    ),
    FeatureDef(
        "freshness_max_age_ms",
        "feed_freshness",
        ("book_aware", "reliability"),
        "logged BTC/book/feed ages before event decision resolution",
        ("btc_age_ms", "book_age_ms", "feed_age_ms"),
        "missing ages are ignored; all missing maps to 0",
        "low",
        "max(btc_age_ms, book_age_ms, feed_age_ms)",
        freshness_max,
    ),
    FeatureDef(
        "log1p_freshness_max_age_ms",
        "feed_freshness",
        ("book_aware", "reliability"),
        "logged BTC/book/feed ages before event decision resolution",
        ("btc_age_ms", "book_age_ms", "feed_age_ms"),
        "missing ages are ignored; all missing maps to 0",
        "low",
        "log1p(max_age_ms)",
        lambda row: math.log1p(max(0.0, freshness_max(row))),
    ),
    FeatureDef(
        "btc_age_missing",
        "missingness",
        ("book_aware", "reliability"),
        "observed missingness in logged event",
        ("btc_age_ms",),
        "missingness indicator",
        "low",
        "1 if btc_age_ms missing else 0",
        lambda row: missing01(row.get("btc_age_ms")),
    ),
    FeatureDef(
        "book_age_missing",
        "missingness",
        ("book_aware", "reliability"),
        "observed missingness in logged event",
        ("book_age_ms",),
        "missingness indicator",
        "low",
        "1 if book_age_ms missing else 0",
        lambda row: missing01(row.get("book_age_ms")),
    ),
    FeatureDef(
        "freshness_gt_1000ms",
        "feed_freshness",
        ("book_aware", "reliability"),
        "logged BTC/book/feed ages before event decision resolution",
        ("btc_age_ms", "book_age_ms", "feed_age_ms"),
        "missing ages map to 0",
        "low",
        "1 if max_age_ms > 1000 else 0",
        lambda row: 1 if freshness_max(row) > 1000.0 else 0,
    ),
    FeatureDef(
        "book_implied_yes_from_side_ask",
        "book_aware_execution",
        ("book_aware",),
        "logged side ask before event decision resolution",
        ("ask_cents", "side"),
        "missing ask maps to 0.5",
        "medium",
        "YES ask / 100 for YES side, 1 - NO ask / 100 for NO side",
        side_book_implied_yes,
    ),
    FeatureDef(
        "v28_minus_book_implied_yes",
        "book_aware_execution",
        ("book_aware", "reliability"),
        "logged v28 probability and side ask before event decision resolution",
        ("v28_p_yes", "ask_cents", "side"),
        "missing values map to neutral 0.5",
        "medium",
        "v28_p_yes - book_implied_yes_from_side_ask",
        lambda row: safe_probability(row.get("v28_p_yes")) - side_book_implied_yes(row),
    ),
    FeatureDef(
        "v28_book_disagreement_abs",
        "book_aware_execution",
        ("book_aware", "reliability"),
        "logged v28 probability and side ask before event decision resolution",
        ("v28_p_yes", "ask_cents", "side"),
        "missing values map to neutral 0.5",
        "medium",
        "abs(v28_p_yes - book_implied_yes)",
        lambda row: abs(safe_probability(row.get("v28_p_yes")) - side_book_implied_yes(row)),
    ),
    FeatureDef(
        "history_bars_log1p",
        "source_reliability",
        ("reliability",),
        "logged v28 history count before event decision resolution",
        ("history_bars",),
        "missing history maps to 0",
        "low",
        "log1p(history_bars)",
        lambda row: log1p_nonnegative(row.get("history_bars")),
    ),
    FeatureDef(
        "prior_logged_event_count",
        "path_memory",
        ("pure_physics", "book_aware", "reliability"),
        "derived only from earlier logged events in the same market",
        ("prior_logged_event_count",),
        "missing count maps to 0",
        "low",
        "count of prior logged rows for this market",
        lambda row: safe_float(row.get("prior_logged_event_count")),
    ),
    FeatureDef(
        "log1p_prior_logged_event_count",
        "path_memory",
        ("pure_physics", "book_aware", "reliability"),
        "derived only from earlier logged events in the same market",
        ("prior_logged_event_count",),
        "missing count maps to 0",
        "low",
        "log1p(prior_logged_event_count)",
        lambda row: log1p_nonnegative(row.get("prior_logged_event_count")),
    ),
    FeatureDef(
        "btc_drift_from_prev_event_dollars",
        "short_term_drift",
        ("pure_physics", "book_aware", "reliability"),
        "current logged BTC minus previous earlier logged BTC in the same market",
        ("btc_drift_from_prev_event_dollars",),
        "missing drift maps to 0",
        "low",
        "current btc - prior event btc",
        lambda row: safe_float(row.get("btc_drift_from_prev_event_dollars")),
    ),
    FeatureDef(
        "btc_drift_from_first_event_dollars",
        "short_term_drift",
        ("pure_physics", "book_aware", "reliability"),
        "current logged BTC minus first earlier logged BTC in the same market",
        ("btc_drift_from_first_event_dollars",),
        "missing drift maps to 0",
        "low",
        "current btc - first market event btc",
        lambda row: safe_float(row.get("btc_drift_from_first_event_dollars")),
    ),
    FeatureDef(
        "prior_btc_path_range_dollars",
        "realized_vol_regime",
        ("pure_physics", "book_aware", "reliability"),
        "range of earlier logged BTC values in the same market",
        ("prior_btc_path_range_dollars",),
        "missing range maps to 0",
        "low",
        "prior max btc - prior min btc",
        lambda row: safe_float(row.get("prior_btc_path_range_dollars")),
    ),
    FeatureDef(
        "prior_btc_path_range_per_sigma",
        "realized_vol_regime",
        ("pure_physics", "book_aware", "reliability"),
        "range of earlier logged BTC values in the same market scaled by current v28 sigma",
        ("prior_btc_path_range_per_sigma",),
        "missing or zero sigma maps to 0",
        "low",
        "prior path range / sigma_t",
        lambda row: safe_float(row.get("prior_btc_path_range_per_sigma")),
    ),
    FeatureDef(
        "prior_adverse_path_memory_dollars",
        "adverse_path_memory",
        ("pure_physics", "book_aware", "reliability"),
        "prior-only same-market BTC excursion against the row side",
        ("prior_adverse_path_memory_dollars",),
        "missing adverse memory maps to 0",
        "low",
        "YES: max(0, strike-prior_min_btc); NO: max(0, prior_max_btc-strike)",
        lambda row: safe_float(row.get("prior_adverse_path_memory_dollars")),
    ),
    FeatureDef(
        "prior_adverse_path_memory_per_sigma",
        "adverse_path_memory",
        ("pure_physics", "book_aware", "reliability"),
        "prior-only same-market BTC excursion against the row side scaled by sigma",
        ("prior_adverse_path_memory_per_sigma",),
        "missing or zero sigma maps to 0",
        "low",
        "prior adverse path memory / sigma_t",
        lambda row: safe_float(row.get("prior_adverse_path_memory_per_sigma")),
    ),
    FeatureDef(
        "prior_recross_seen",
        "recross_hazard",
        ("pure_physics", "book_aware", "reliability"),
        "prior-only same-market BTC range crossing the strike before the row",
        ("prior_recross_seen",),
        "missing maps to 0",
        "low",
        "1 if prior min btc <= strike <= prior max btc else 0",
        lambda row: bool01(row.get("prior_recross_seen")),
    ),
    FeatureDef(
        "btc_event_dt_seconds",
        "feed_freshness",
        ("book_aware", "reliability"),
        "elapsed seconds since previous earlier logged event in the same market",
        ("btc_event_dt_seconds",),
        "missing elapsed time maps to 0",
        "low",
        "decision_ts - previous same-market event ts",
        lambda row: safe_float(row.get("btc_event_dt_seconds")),
    ),
    FeatureDef(
        "source_is_logged_approved",
        "source_reliability",
        ("reliability",),
        "logged event type",
        ("source_type",),
        "missing maps to 0",
        "low",
        "1 if source_type == mushroom_v28_approved else 0",
        lambda row: 1 if row.get("source_type") == "mushroom_v28_approved" else 0,
    ),
    FeatureDef(
        "source_is_signal_seen",
        "source_reliability",
        ("reliability",),
        "logged event type",
        ("source_type",),
        "missing maps to 0",
        "low",
        "1 if source_type == signal_seen else 0",
        lambda row: 1 if row.get("source_type") == "signal_seen" else 0,
    ),
    FeatureDef(
        "source_is_plan_built",
        "source_reliability",
        ("reliability",),
        "logged event type",
        ("source_type",),
        "missing maps to 0",
        "low",
        "1 if source_type == plan_built else 0",
        lambda row: 1 if row.get("source_type") == "plan_built" else 0,
    ),
)

FEATURES = BASE_FEATURES + LOGGED_EVENT_FEATURES


def read_rows(path: Path, limit_rows: int | None = None) -> list[dict[str, Any]]:
    if not path.exists():
        raise FileNotFoundError(f"Missing logged-event rows: {path}")
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        for raw in reader:
            rows.append(raw)
            if limit_rows is not None and len(rows) >= limit_rows:
                break
    return rows


def read_api_replay_rows(path: Path = API_REPLAY_CSV) -> dict[str, dict[str, Any]]:
    if not path.exists():
        return {}
    out: dict[str, dict[str, Any]] = {}
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        for replay_row in reader:
            row_id = str(replay_row.get("row_id") or "")
            if row_id:
                out[row_id] = dict(replay_row)
    return out


def enrich_with_api_replay(row: dict[str, Any], replay_by_id: dict[str, dict[str, Any]]) -> dict[str, Any]:
    enriched = dict(row)
    replay_row = replay_by_id.get(str(row.get("row_id") or ""))
    if not replay_row:
        enriched["api_replay_available"] = 0
        return enriched
    enriched["api_replay_available"] = 1 if replay_row.get("replay_status") == "replayed_v28_api_from_predecision_btc_cache" else 0
    for key, value in replay_row.items():
        if key.startswith("replay_"):
            enriched[key] = value
    return enriched


def build_feature_row(row: dict[str, Any], replay_by_id: dict[str, dict[str, Any]] | None = None) -> dict[str, Any]:
    enriched = enrich_with_api_replay(row, replay_by_id or {})
    out = {col: row.get(col, "") for col in METADATA_COLUMNS}
    out.update(
        {
            "target_y_yes_win": row.get("y_yes_win", ""),
            "target_v28_p_yes": row.get("v28_p_yes", ""),
            "target_brier_yes": row.get("brier_yes", ""),
            "target_logloss_yes": row.get("logloss_yes", ""),
            "row_is_posthoc": bool01(row.get("is_recomputed_after_resolution")),
            "row_is_simulated": bool01(row.get("is_simulated")),
            "row_is_sidecar": bool01(row.get("is_sidecar")),
            "row_is_diagnostic_only": bool01(row.get("is_diagnostic_only")),
        }
    )
    for feature in FEATURES:
        out[feature.name] = feature.fn(enriched)
    return out


def manifest_rows() -> list[dict[str, Any]]:
    return [feature.manifest_row() for feature in FEATURES]


def leakage_audit(manifest: list[dict[str, Any]], feature_rows: list[dict[str, Any]]) -> dict[str, Any]:
    feature_names = [row["feature_name"] for row in manifest]
    leaky_by_name = [name for name in feature_names if has_leaky_token(name)]
    leaky_by_source = []
    for row in manifest:
        if any(has_leaky_token(str(col)) for col in row.get("source_columns", [])):
            leaky_by_source.append(row["feature_name"])
    nan_or_inf = []
    for name in feature_names:
        for idx, row in enumerate(feature_rows):
            value = as_float(row.get(name))
            if value is None or not math.isfinite(value):
                nan_or_inf.append({"feature": name, "row_index": idx})
                break
    return {
        "status": "pass" if not leaky_by_name and not leaky_by_source and not nan_or_inf else "fail",
        "feature_count": len(feature_names),
        "leaky_feature_names": leaky_by_name,
        "leaky_source_columns": leaky_by_source,
        "features_with_nan_or_inf": nan_or_inf,
        "label_columns_present_but_not_features": TARGET_COLUMNS,
        "notes": [
            "Logged v28 outputs are used as features only when they were emitted before event resolution.",
            "Labels are included as target columns for scoring joins but not in the feature manifest.",
            "Rows remain diagnostic-only because labels are sourced from posthoc seed market outcomes.",
        ],
    }


def missing_summary(feature_rows: list[dict[str, Any]], manifest: list[dict[str, Any]]) -> dict[str, int]:
    return {
        row["feature_name"]: sum(1 for item in feature_rows if as_float(item.get(row["feature_name"])) is None)
        for row in manifest
    }


def summarize(rows: list[dict[str, Any]], feature_rows: list[dict[str, Any]], manifest: list[dict[str, Any]]) -> dict[str, Any]:
    source_counts = Counter(row.get("source_type", "") for row in rows)
    return {
        "created_utc": datetime.now(tz=timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "builder_script": rel_path(Path(__file__)),
        "input_rows_path": rel_path(LOGGED_ROWS_CSV),
        "input_rows_hash": sha256_file(LOGGED_ROWS_CSV),
        "row_count": len(rows),
        "market_count": len({row.get("market_ticker") for row in rows}),
        "feature_row_count": len(feature_rows),
        "feature_count": len(manifest),
        "feature_manifest_hash": stable_hash(manifest),
        "track_feature_counts": track_summary(manifest),
        "source_counts": dict(sorted(source_counts.items())),
        "metadata_columns": METADATA_COLUMNS,
        "target_columns": TARGET_COLUMNS,
        "feature_columns": [row["feature_name"] for row in manifest],
        "missing_feature_values": missing_summary(feature_rows, manifest),
        "leakage_audit": leakage_audit(manifest, feature_rows),
        "eligibility_counts": {
            "training": sum(1 for row in rows if as_bool(row.get("allowed_for_training"))),
            "validation": sum(1 for row in rows if as_bool(row.get("allowed_for_validation"))),
            "holdout": sum(1 for row in rows if as_bool(row.get("allowed_for_holdout"))),
            "forward_promotion": sum(1 for row in rows if as_bool(row.get("allowed_for_forward_promotion"))),
        },
        "outputs": {
            "features_csv": rel_path(FEATURES_CSV),
            "features_json": rel_path(FEATURES_JSON),
            "feature_manifest_json": rel_path(FEATURE_MANIFEST_JSON),
            "feature_audit_json": rel_path(FEATURE_AUDIT_JSON),
            "feature_audit_md": rel_path(FEATURE_AUDIT_MD),
        },
    }


def write_markdown(summary: dict[str, Any], manifest: list[dict[str, Any]], path: Path) -> None:
    lines = [
        "# v28 Successor Logged Event Feature Audit",
        "",
        "Research-only logged-event feature artifact. It does not touch live bot state, orders, thresholds, or processes.",
        "",
        "## Summary",
        "",
        f"- Created UTC: `{summary['created_utc']}`",
        f"- Input rows: `{summary['input_rows_path']}`",
        f"- Input hash: `{summary['input_rows_hash']}`",
        f"- Rows: `{summary['row_count']}`",
        f"- Markets: `{summary['market_count']}`",
        f"- Features: `{summary['feature_count']}`",
        f"- Feature manifest hash: `{summary['feature_manifest_hash']}`",
        f"- Forward-promotion rows: `{summary['eligibility_counts']['forward_promotion']}`",
        f"- v28 API replay rows joined: `{summary.get('api_replay_join', {}).get('feature_rows_with_api_replay')}`",
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
    for note in summary["leakage_audit"]["notes"]:
        lines.append(f"- {note}")
    if summary["leakage_audit"]["leaky_feature_names"]:
        lines.append(f"- Leaky feature names: `{summary['leakage_audit']['leaky_feature_names']}`")
    if summary["leakage_audit"]["leaky_source_columns"]:
        lines.append(f"- Leaky source columns: `{summary['leakage_audit']['leaky_source_columns']}`")
    if summary["leakage_audit"]["features_with_nan_or_inf"]:
        lines.append(f"- Features with NaN/Inf: `{summary['leakage_audit']['features_with_nan_or_inf']}`")

    lines.extend(["", "## Feature Manifest", "", "| feature | family | tracks | source columns | leakage risk | transform |", "|---|---|---|---|---|---|"])
    for item in manifest:
        lines.append(
            f"| `{item['feature_name']}` | {item['feature_family']} | {', '.join(item['model_track_allowed'])} | "
            f"{', '.join(item['source_columns'])} | {item['leakage_risk']} | {item['normalization_or_transform']} |"
        )

    lines.extend(
        [
            "",
            "## Read",
            "",
            "- This feature set adds true logged boundary geometry, strike/BTC distance, arrow, freshness, book-v28 disagreement proxies, and research-only v28 API replay components.",
            "- It remains diagnostic-only because there are no frozen-forward rows.",
            "- Promotion gates must remain closed for any candidate trained on these features.",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def build(limit_rows: int | None = None) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]], dict[str, Any]]:
    rows = read_rows(LOGGED_ROWS_CSV, limit_rows=limit_rows)
    replay_by_id = read_api_replay_rows()
    feature_rows = [build_feature_row(row, replay_by_id) for row in rows]
    manifest = manifest_rows()
    summary = summarize(rows, feature_rows, manifest)
    summary["api_replay_join"] = {
        "api_replay_csv": rel_path(API_REPLAY_CSV),
        "api_replay_hash": sha256_file(API_REPLAY_CSV),
        "api_replay_rows_available": len(replay_by_id),
        "feature_rows_with_api_replay": sum(1 for row in feature_rows if as_bool(row.get("v28_api_replay_available"))),
    }
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
    parser.add_argument("--write", action="store_true", help="Write logged-event feature artifacts.")
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
                "market_count": summary["market_count"],
                "feature_count": summary["feature_count"],
                "leakage_status": summary["leakage_audit"]["status"],
                "forward_promotion_rows": summary["eligibility_counts"]["forward_promotion"],
                "written": bool(args.write and not args.dry_run),
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
