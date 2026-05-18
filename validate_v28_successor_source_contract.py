"""Validate source contracts for the v28 successor FV research pipeline.

Research-only. This script turns the spec's source-quality rules into an
executable gate. It does not touch live bot state, order logic, thresholds,
secrets, or processes.

Current diagnostic artifacts are expected to be blocked: they are useful for
audits and scaffolding, but they are not frozen forward evidence.
"""
from __future__ import annotations

import argparse
import csv
import json
import math
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "research_particle" / "v28_successor"
EDGE_DIR = ROOT / "logs" / "edge_research"

SEED_ROWS_CSV = OUT_DIR / "causal_rows_seed_latest.csv"
LOGGED_ROWS_CSV = OUT_DIR / "causal_rows_logged_events_latest.csv"
SEED_FEATURES_CSV = OUT_DIR / "features_latest.csv"
LOGGED_FEATURES_CSV = OUT_DIR / "features_logged_events_latest.csv"
SEED_FEATURE_MANIFEST_JSON = OUT_DIR / "feature_manifest_latest.json"
LOGGED_FEATURE_MANIFEST_JSON = OUT_DIR / "feature_manifest_logged_events_latest.json"
FORWARD_REGISTRY_CSV = OUT_DIR / "forward_registry_latest.csv"
FORWARD_REGISTRY_JSON = EDGE_DIR / "v28_successor_forward_registry_latest.json"
PASSIVE_SNAPSHOTS_CSV = OUT_DIR / "passive_forward_snapshots_latest.csv"
SHADOW_FORWARD_LABELED_CSV = OUT_DIR / "shadow_forward_labeled_rows_latest.csv"
FORWARD_LABELED_PREDICTIONS_CSV = OUT_DIR / "forward_labeled_predictions_latest.csv"
SIDECAR_BATCH_LABELED_PREDICTIONS_CSV = OUT_DIR / "sidecar_bundle_batch_labeled_latest.csv"

CONTRACT_JSON = EDGE_DIR / "v28_successor_source_contract_latest.json"
CONTRACT_MD = EDGE_DIR / "v28_successor_source_contract_latest.md"
CONTRACT_CSV = EDGE_DIR / "v28_successor_source_contract_latest.csv"

MIN_FORWARD_ROWS = 200
MIN_FORWARD_MARKETS = 40
FAIR_SUM_TOLERANCE_CENTS = 0.05
MIN_RELIABILITY_COVERAGE = 0.95

LEAKY_TOKENS = {
    "brier",
    "label",
    "logloss",
    "outcome",
    "pnl",
    "profit",
    "resolved",
    "resolution",
    "result",
    "settled",
    "settlement",
    "target",
    "win",
    "won",
}

DATASETS = [
    {
        "dataset_id": "seed_causal_rows",
        "artifact_type": "causal_rows",
        "path": SEED_ROWS_CSV,
        "label_fields_any": ["y_yes_win"],
        "probability_fields": ["v28_p_yes", "v28_p_no"],
        "fair_fields": ["v28_fair_yes_cents", "v28_fair_no_cents"],
        "boundary_fields_any": ["d_sigma", "abs_d_sigma", "strike_distance_dollars_abs", "distance_per_sigma_from_prices"],
        "strike_fields_any": ["strike"],
        "book_fields_any": ["ask_cents", "book_implied_yes_from_side_ask"],
        "physics_fields_any": ["recross_hazard_score", "h6_recross_hazard_high"],
        "needs_feature_manifest": False,
    },
    {
        "dataset_id": "logged_event_causal_rows",
        "artifact_type": "causal_rows",
        "path": LOGGED_ROWS_CSV,
        "label_fields_any": ["y_yes_win"],
        "probability_fields": ["v28_p_yes", "v28_p_no"],
        "fair_fields": ["v28_fair_yes_cents", "v28_fair_no_cents"],
        "boundary_fields_any": ["d_sigma", "abs_d_sigma", "strike_distance_dollars_abs", "distance_per_sigma_from_prices"],
        "strike_fields_any": ["strike"],
        "book_fields_any": ["ask_cents", "book_implied_yes_from_side_ask"],
        "physics_fields_any": ["recross_hazard_score", "h6_recross_hazard_high", "prior_recross_seen"],
        "needs_feature_manifest": False,
    },
    {
        "dataset_id": "seed_feature_table",
        "artifact_type": "feature_table",
        "path": SEED_FEATURES_CSV,
        "feature_manifest": SEED_FEATURE_MANIFEST_JSON,
        "label_fields_any": ["target_y_yes_win"],
        "probability_fields": ["target_v28_p_yes"],
        "fair_fields": [],
        "boundary_fields_any": ["d_sigma", "abs_d_sigma", "strike_distance_dollars_abs", "distance_per_sigma_from_prices"],
        "strike_fields_any": ["strike"],
        "book_fields_any": ["ask_cents", "book_implied_yes_from_side_ask"],
        "physics_fields_any": ["recross_hazard_score", "recross_hazard_high"],
        "needs_feature_manifest": True,
    },
    {
        "dataset_id": "logged_event_feature_table",
        "artifact_type": "feature_table",
        "path": LOGGED_FEATURES_CSV,
        "feature_manifest": LOGGED_FEATURE_MANIFEST_JSON,
        "label_fields_any": ["target_y_yes_win"],
        "probability_fields": ["target_v28_p_yes"],
        "fair_fields": [],
        "boundary_fields_any": ["d_sigma", "abs_d_sigma", "strike_distance_dollars_abs", "distance_per_sigma_from_prices"],
        "strike_fields_any": ["strike"],
        "book_fields_any": ["ask_cents", "book_implied_yes_from_side_ask"],
        "physics_fields_any": ["recross_hazard_score", "recross_hazard_high", "prior_recross_seen"],
        "needs_feature_manifest": True,
    },
    {
        "dataset_id": "passive_forward_snapshots",
        "artifact_type": "passive_forward_snapshots",
        "path": PASSIVE_SNAPSHOTS_CSV,
        "label_fields_any": [],
        "probability_fields": [],
        "fair_fields": [],
        "boundary_fields_any": [],
        "strike_fields_any": ["strike"],
        "book_fields_any": ["ask_cents", "book_implied_yes_from_side_ask"],
        "physics_fields_any": [],
        "needs_feature_manifest": False,
    },
    {
        "dataset_id": "shadow_forward_labeled_rows",
        "artifact_type": "shadow_forward_labeled_rows",
        "path": SHADOW_FORWARD_LABELED_CSV,
        "label_fields_any": ["y_yes_win"],
        "probability_fields": ["v28_p_yes", "candidate_p_yes"],
        "fair_fields": ["candidate_fair_yes_cents", "candidate_fair_no_cents"],
        "boundary_fields_any": ["v28_d_sigma", "abs_v28_d_sigma", "strike_distance_dollars_abs"],
        "strike_fields_any": ["strike"],
        "book_fields_any": ["ask_cents", "book_implied_yes_from_side_ask"],
        "physics_fields_any": ["recross_hazard_score", "max_adverse_move_3m"],
        "needs_feature_manifest": False,
    },
    {
        "dataset_id": "forward_registry",
        "artifact_type": "forward_registry",
        "path": FORWARD_REGISTRY_CSV,
        "label_fields_any": [],
        "probability_fields": ["candidate_p_yes", "v28_p_yes"],
        "fair_fields": ["candidate_fair_yes_cents", "candidate_fair_no_cents"],
        "boundary_fields_any": [],
        "strike_fields_any": [],
        "book_fields_any": ["ask_cents"],
        "physics_fields_any": [],
        "needs_feature_manifest": False,
    },
    {
        "dataset_id": "forward_labeled_predictions",
        "artifact_type": "forward_labeled_predictions",
        "path": FORWARD_LABELED_PREDICTIONS_CSV,
        "label_fields_any": ["y_yes_win"],
        "probability_fields": ["candidate_p_yes", "v28_p_yes"],
        "fair_fields": ["candidate_fair_yes_cents", "candidate_fair_no_cents"],
        "boundary_fields_any": ["v28_d_sigma"],
        "strike_fields_any": ["strike"],
        "book_fields_any": ["ask_cents", "book_implied_yes_from_side_ask"],
        "physics_fields_any": ["v28_sigma_t_dollars"],
        "needs_feature_manifest": False,
    },
    {
        "dataset_id": "sidecar_batch_labeled_predictions",
        "artifact_type": "forward_labeled_predictions",
        "path": SIDECAR_BATCH_LABELED_PREDICTIONS_CSV,
        "label_fields_any": ["y_yes_win"],
        "probability_fields": ["candidate_p_yes", "v28_p_yes"],
        "fair_fields": ["candidate_fair_yes_cents", "candidate_fair_no_cents"],
        "boundary_fields_any": ["v28_d_sigma"],
        "strike_fields_any": ["strike"],
        "book_fields_any": ["ask_cents", "book_implied_yes_from_side_ask"],
        "physics_fields_any": ["v28_sigma_t_dollars"],
        "needs_feature_manifest": False,
    },
]


def rel_path(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(ROOT)).replace("\\", "/")
    except ValueError:
        return str(path)


def as_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() in {"true", "1", "yes", "y"}


def as_float(value: Any) -> float | None:
    if value is None:
        return None
    text = str(value).strip()
    if not text:
        return None
    try:
        out = float(text)
    except ValueError:
        return None
    if not math.isfinite(out):
        return None
    return out


def nonempty(value: Any) -> bool:
    return value is not None and str(value).strip() != ""


def parse_ts(value: Any) -> datetime | None:
    if not nonempty(value):
        return None
    text = str(value).strip()
    if text.endswith("Z"):
        text = text[:-1] + "+00:00"
    try:
        parsed = datetime.fromisoformat(text)
    except ValueError:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def read_csv_rows(path: Path, limit_rows: int | None = None) -> tuple[list[dict[str, Any]], list[str]]:
    if not path.exists():
        return [], []
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        fieldnames = list(reader.fieldnames or [])
        rows: list[dict[str, Any]] = []
        for idx, row in enumerate(reader):
            if limit_rows is not None and idx >= limit_rows:
                break
            rows.append(dict(row))
    return rows, fieldnames


def read_json(path: Path) -> Any:
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def field_missing_count(rows: list[dict[str, Any]], field: str) -> int:
    return sum(1 for row in rows if not nonempty(row.get(field)))


def group_present_count(rows: list[dict[str, Any]], fields: list[str]) -> int:
    if not fields:
        return len(rows)
    return sum(1 for row in rows if any(nonempty(row.get(field)) for field in fields))


def group_numeric_present_count(rows: list[dict[str, Any]], fields: list[str]) -> int:
    if not fields:
        return len(rows)
    return sum(1 for row in rows if any(as_float(row.get(field)) is not None for field in fields))


def coverage(count: int, total: int) -> float:
    if total <= 0:
        return 0.0
    return count / total


def gate(name: str, passed: bool, evidence: str, severity: str = "hard") -> dict[str, Any]:
    return {
        "gate": name,
        "passed": bool(passed),
        "severity": severity,
        "evidence": evidence,
    }


def leaky_token(value: Any) -> bool:
    tokens = [token for token in re.split(r"[^a-z0-9]+", str(value).lower()) if token]
    return any(token in LEAKY_TOKENS for token in tokens)


def evaluate_feature_manifest(path: Path | None) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    if path is None:
        return [], {"feature_count": 0, "leaky_feature_names": [], "leaky_source_columns": []}
    manifest = read_json(path) or []
    if not isinstance(manifest, list):
        manifest = []
    leaky_feature_names: list[str] = []
    leaky_source_columns: list[str] = []
    for row in manifest:
        feature_name = str(row.get("feature_name", ""))
        if leaky_token(feature_name):
            leaky_feature_names.append(feature_name)
        for source_column in row.get("source_columns", []) or []:
            if leaky_token(source_column):
                leaky_source_columns.append(str(source_column))
    details = {
        "feature_count": len(manifest),
        "leaky_feature_names": sorted(set(leaky_feature_names)),
        "leaky_source_columns": sorted(set(leaky_source_columns)),
        "manifest_path": rel_path(path),
    }
    gates = [
        gate("feature_manifest_exists", path.exists(), f"path={rel_path(path)}"),
        gate("feature_manifest_not_empty", len(manifest) > 0, f"feature_count={len(manifest)}"),
        gate(
            "feature_manifest_no_leaky_names",
            not leaky_feature_names,
            f"leaky_feature_names={details['leaky_feature_names']}",
        ),
        gate(
            "feature_manifest_no_leaky_source_columns",
            not leaky_source_columns,
            f"leaky_source_columns={details['leaky_source_columns']}",
        ),
    ]
    return gates, details


def count_clock_violations(rows: list[dict[str, Any]]) -> tuple[int, int, int]:
    missing_or_unparseable = 0
    violations = 0
    checked = 0
    for row in rows:
        decision_ts = parse_ts(row.get("decision_ts_utc"))
        close_ts = parse_ts(row.get("market_close_ts_utc"))
        if decision_ts is None or close_ts is None:
            missing_or_unparseable += 1
            continue
        checked += 1
        if decision_ts > close_ts:
            violations += 1
    return checked, missing_or_unparseable, violations


def count_probability_violations(rows: list[dict[str, Any]], fields: list[str]) -> int:
    violations = 0
    for row in rows:
        for field in fields:
            value = as_float(row.get(field))
            if value is None or value < 0.0 or value > 1.0:
                violations += 1
                break
    return violations


def count_fair_sum_violations(rows: list[dict[str, Any]], yes_field: str, no_field: str) -> tuple[int, int]:
    checked = 0
    violations = 0
    for row in rows:
        yes = as_float(row.get(yes_field))
        no = as_float(row.get(no_field))
        if yes is None or no is None:
            continue
        checked += 1
        if abs((yes + no) - 100.0) > FAIR_SUM_TOLERANCE_CENTS:
            violations += 1
    return checked, violations


def count_flag(rows: list[dict[str, Any]], field: str, value: bool = True) -> int:
    if not rows or field not in rows[0]:
        return 0
    return sum(1 for row in rows if as_bool(row.get(field)) is value)


def count_rows_matching_text(rows: list[dict[str, Any]], field: str, needles: tuple[str, ...]) -> int:
    if not rows or field not in rows[0]:
        return 0
    return sum(1 for row in rows if any(needle in str(row.get(field, "")).lower() for needle in needles))


def evaluate_forward_cleanliness(rows: list[dict[str, Any]], artifact_type: str) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    if artifact_type == "forward_registry":
        market_count = len({str(row.get("market_ticker")) for row in rows if nonempty(row.get("market_ticker"))})
        summary_path = read_json(FORWARD_REGISTRY_JSON) or {}
        promotion_ready = as_bool(summary_path.get("promotion_ready"))
        registry_status = summary_path.get("registry_status", "missing_summary")
        non_frozen_sources = sum(
            1
            for row in rows
            if str(row.get("source_status") or "") != "frozen_pre_resolution_prediction"
        )
        missing_freeze_clock = 0
        freeze_after_close = 0
        for row in rows:
            frozen_ts = parse_ts(row.get("frozen_utc") or row.get("registered_utc"))
            close_ts = parse_ts(row.get("market_close_ts_utc"))
            if frozen_ts is None or close_ts is None:
                missing_freeze_clock += 1
                continue
            if frozen_ts > close_ts:
                freeze_after_close += 1
        registry_ids = [str(row.get("registry_id") or "") for row in rows if nonempty(row.get("registry_id"))]
        frozen_prediction_ids = [
            str(row.get("frozen_prediction_id") or "")
            for row in rows
            if nonempty(row.get("frozen_prediction_id"))
        ]
        duplicate_registry_ids = len(registry_ids) - len(set(registry_ids))
        duplicate_frozen_prediction_ids = len(frozen_prediction_ids) - len(set(frozen_prediction_ids))
        gates = [
            gate(
                "forward_registry_not_empty",
                len(rows) > 0,
                f"rows={len(rows)} registry_status={registry_status}",
            ),
            gate(
                "forward_registry_min_rows",
                len(rows) >= MIN_FORWARD_ROWS,
                f"rows={len(rows)} required_rows={MIN_FORWARD_ROWS}",
            ),
            gate(
                "forward_registry_min_markets",
                market_count >= MIN_FORWARD_MARKETS,
                f"markets={market_count} required_markets={MIN_FORWARD_MARKETS}",
            ),
            gate(
                "forward_registry_promotion_ready",
                promotion_ready,
                f"promotion_ready={promotion_ready} registry_status={registry_status}",
            ),
            gate(
                "forward_registry_from_frozen_predictions",
                len(rows) > 0 and non_frozen_sources == 0,
                f"non_frozen_source_rows={non_frozen_sources} rows={len(rows)}",
            ),
            gate(
                "forward_registry_frozen_before_close",
                len(rows) > 0 and missing_freeze_clock == 0 and freeze_after_close == 0,
                (
                    f"missing_or_unparseable_freeze_clock={missing_freeze_clock} "
                    f"freeze_after_close={freeze_after_close} rows={len(rows)}"
                ),
            ),
            gate(
                "forward_registry_unique_frozen_predictions",
                len(rows) > 0
                and len(registry_ids) == len(rows)
                and len(frozen_prediction_ids) == len(rows)
                and duplicate_registry_ids == 0
                and duplicate_frozen_prediction_ids == 0,
                (
                    f"registry_ids={len(registry_ids)}/{len(rows)} duplicates={duplicate_registry_ids} "
                    f"frozen_prediction_ids={len(frozen_prediction_ids)}/{len(rows)} "
                    f"duplicates={duplicate_frozen_prediction_ids}"
                ),
            ),
        ]
        details = {
            "forward_rows": len(rows),
            "forward_markets": market_count,
            "registry_status": registry_status,
            "promotion_ready": promotion_ready,
            "non_frozen_source_rows": non_frozen_sources,
            "missing_or_unparseable_freeze_clock": missing_freeze_clock,
            "freeze_after_close_rows": freeze_after_close,
            "duplicate_registry_ids": duplicate_registry_ids,
            "duplicate_frozen_prediction_ids": duplicate_frozen_prediction_ids,
        }
        return gates, details

    if artifact_type == "forward_labeled_predictions":
        joined_rows = [row for row in rows if str(row.get("label_join_status") or "") == "joined_post_resolution"]
        market_count = len({str(row.get("market_ticker")) for row in joined_rows if nonempty(row.get("market_ticker"))})
        blocked_join_rows = sum(1 for row in rows if nonempty(row.get("label_join_blockers")))
        non_frozen_sources = sum(
            1
            for row in joined_rows
            if str(row.get("source_status") or "") != "frozen_pre_resolution_prediction"
        )
        missing_freeze_clock = 0
        freeze_after_close = 0
        for row in joined_rows:
            frozen_ts = parse_ts(row.get("frozen_utc"))
            close_ts = parse_ts(row.get("market_close_ts_utc"))
            if frozen_ts is None or close_ts is None:
                missing_freeze_clock += 1
                continue
            if frozen_ts > close_ts:
                freeze_after_close += 1
        gates = [
            gate(
                "forward_labeled_rows_present",
                len(joined_rows) > 0,
                f"joined_rows={len(joined_rows)} total_rows={len(rows)}",
            ),
            gate(
                "forward_labeled_min_rows",
                len(joined_rows) >= MIN_FORWARD_ROWS,
                f"joined_rows={len(joined_rows)} required_rows={MIN_FORWARD_ROWS}",
            ),
            gate(
                "forward_labeled_min_markets",
                market_count >= MIN_FORWARD_MARKETS,
                f"joined_markets={market_count} required_markets={MIN_FORWARD_MARKETS}",
            ),
            gate(
                "forward_labels_joined_after_resolution",
                len(joined_rows) > 0 and blocked_join_rows == 0,
                f"blocked_join_rows={blocked_join_rows} joined_rows={len(joined_rows)}",
            ),
            gate(
                "forward_labels_from_frozen_predictions",
                len(joined_rows) > 0 and non_frozen_sources == 0,
                f"non_frozen_source_rows={non_frozen_sources} joined_rows={len(joined_rows)}",
            ),
            gate(
                "forward_labels_frozen_before_close",
                len(joined_rows) > 0 and missing_freeze_clock == 0 and freeze_after_close == 0,
                (
                    f"missing_or_unparseable_freeze_clock={missing_freeze_clock} "
                    f"freeze_after_close={freeze_after_close} joined_rows={len(joined_rows)}"
                ),
            ),
        ]
        details = {
            "joined_rows": len(joined_rows),
            "joined_markets": market_count,
            "blocked_join_rows": blocked_join_rows,
            "non_frozen_source_rows": non_frozen_sources,
            "missing_or_unparseable_freeze_clock": missing_freeze_clock,
            "freeze_after_close_rows": freeze_after_close,
        }
        return gates, details

    forward_rows = [row for row in rows if as_bool(row.get("allowed_for_forward_promotion"))]
    not_registered = sum(
        1
        for row in forward_rows
        if "is_pre_resolution_registered" in row and not as_bool(row.get("is_pre_resolution_registered"))
    )
    recomputed = sum(1 for row in forward_rows if as_bool(row.get("is_recomputed_after_resolution")))
    backfilled = sum(1 for row in forward_rows if as_bool(row.get("is_backfilled")))
    simulated = sum(1 for row in forward_rows if as_bool(row.get("is_simulated")) or as_bool(row.get("row_is_simulated")))
    sidecar = sum(1 for row in forward_rows if as_bool(row.get("is_sidecar")) or as_bool(row.get("row_is_sidecar")))
    diagnostic = sum(1 for row in forward_rows if as_bool(row.get("is_diagnostic_only")) or as_bool(row.get("row_is_diagnostic_only")))
    posthoc = sum(
        1
        for row in forward_rows
        if as_bool(row.get("row_is_posthoc"))
        or as_bool(row.get("is_recomputed_after_resolution"))
        or "posthoc" in str(row.get("source_type", "")).lower()
    )
    diagnostic_source = sum(
        1
        for row in forward_rows
        if "diagnostic" in str(row.get("source_quality_tier", "")).lower()
        or "posthoc" in str(row.get("source_quality_tier", "")).lower()
    )
    dirty = not_registered + recomputed + backfilled + simulated + sidecar + diagnostic + posthoc + diagnostic_source
    gates = [
        gate(
            "forward_promotion_rows_present",
            len(forward_rows) > 0,
            f"forward_rows={len(forward_rows)} total_rows={len(rows)}",
        ),
        gate(
            "forward_rows_pre_resolution_registered",
            len(forward_rows) > 0 and not_registered == 0,
            f"not_registered_forward_rows={not_registered} forward_rows={len(forward_rows)}",
        ),
        gate(
            "forward_rows_not_after_the_fact",
            len(forward_rows) > 0 and dirty == 0,
            (
                "recomputed={recomputed} backfilled={backfilled} simulated={simulated} "
                "sidecar={sidecar} diagnostic={diagnostic} posthoc={posthoc} "
                "diagnostic_source={diagnostic_source}"
            ).format(
                recomputed=recomputed,
                backfilled=backfilled,
                simulated=simulated,
                sidecar=sidecar,
                diagnostic=diagnostic,
                posthoc=posthoc,
                diagnostic_source=diagnostic_source,
            ),
        ),
    ]
    details = {
        "forward_rows": len(forward_rows),
        "not_registered_forward_rows": not_registered,
        "dirty_forward_rows": dirty,
    }
    return gates, details


def evaluate_dataset(config: dict[str, Any], limit_rows: int | None = None) -> dict[str, Any]:
    path: Path = config["path"]
    artifact_type = str(config["artifact_type"])
    rows, fieldnames = read_csv_rows(path, limit_rows=limit_rows)
    row_count = len(rows)
    market_count = len({str(row.get("market_ticker")) for row in rows if nonempty(row.get("market_ticker"))})
    gates: list[dict[str, Any]] = [
        gate("artifact_exists", path.exists(), f"path={rel_path(path)}"),
        gate("artifact_has_header", bool(fieldnames), f"columns={len(fieldnames)}"),
    ]
    if artifact_type != "forward_registry":
        gates.append(gate("artifact_not_empty", row_count > 0, f"rows={row_count}"))
    required_identifiers = ["row_id", "market_ticker", "decision_ts_utc"]
    if artifact_type != "forward_registry":
        required_identifiers.append("market_close_ts_utc")
    missing_identifier_counts = {field: field_missing_count(rows, field) for field in required_identifiers}
    gates.append(
        gate(
            "identifier_fields_complete",
            row_count > 0 and all(count == 0 for count in missing_identifier_counts.values()),
            f"missing={missing_identifier_counts}",
        )
    )

    if artifact_type != "forward_registry":
        checked, missing_clock, clock_violations = count_clock_violations(rows)
        gates.append(
            gate(
                "pre_resolution_clock_valid",
                row_count > 0 and missing_clock == 0 and clock_violations == 0,
                f"checked={checked} missing_or_unparseable={missing_clock} decision_after_close={clock_violations}",
            )
        )
        gates.append(
            gate(
                "target_label_present",
                group_present_count(rows, config["label_fields_any"]) == row_count and row_count > 0,
                f"fields={config['label_fields_any']} coverage={group_present_count(rows, config['label_fields_any'])}/{row_count}",
            )
        )

    probability_violations = count_probability_violations(rows, config["probability_fields"])
    probability_coverage = group_numeric_present_count(rows, config["probability_fields"])
    gates.append(
        gate(
            "probability_fields_complete_and_bounded",
            row_count > 0 and probability_coverage == row_count and probability_violations == 0,
            f"fields={config['probability_fields']} coverage={probability_coverage}/{row_count} violations={probability_violations}",
        )
    )

    fair_fields = config["fair_fields"]
    if len(fair_fields) >= 2:
        fair_coverage = group_numeric_present_count(rows, fair_fields)
        checked_fair, fair_violations = count_fair_sum_violations(rows, fair_fields[0], fair_fields[1])
        gates.append(
            gate(
                "fair_yes_no_cents_complete_and_sum_to_100",
                row_count > 0 and fair_coverage == row_count and checked_fair == row_count and fair_violations == 0,
                (
                    f"fields={fair_fields} coverage={fair_coverage}/{row_count} "
                    f"sum_checked={checked_fair} sum_violations={fair_violations}"
                ),
            )
        )

    if config["strike_fields_any"]:
        strike_coverage = group_numeric_present_count(rows, config["strike_fields_any"])
        gates.append(
            gate(
                "strike_fields_complete",
                row_count > 0 and strike_coverage == row_count,
                f"fields={config['strike_fields_any']} coverage={strike_coverage}/{row_count}",
            )
        )
    if config["boundary_fields_any"]:
        boundary_coverage = group_numeric_present_count(rows, config["boundary_fields_any"])
        gates.append(
            gate(
                "boundary_geometry_complete",
                row_count > 0 and boundary_coverage == row_count,
                f"fields={config['boundary_fields_any']} coverage={boundary_coverage}/{row_count}",
            )
        )
    if config["book_fields_any"]:
        book_coverage = group_numeric_present_count(rows, config["book_fields_any"])
        gates.append(
            gate(
                "book_price_or_implied_price_available",
                row_count > 0 and coverage(book_coverage, row_count) >= MIN_RELIABILITY_COVERAGE,
                f"fields={config['book_fields_any']} coverage={book_coverage}/{row_count}",
            )
        )
    if config["physics_fields_any"]:
        physics_coverage = group_present_count(rows, config["physics_fields_any"])
        gates.append(
            gate(
                "recross_or_path_risk_signal_available",
                row_count > 0 and coverage(physics_coverage, row_count) >= MIN_RELIABILITY_COVERAGE,
                f"fields={config['physics_fields_any']} coverage={physics_coverage}/{row_count}",
            )
        )

    source_gates, source_details = evaluate_forward_cleanliness(rows, artifact_type)
    gates.extend(source_gates)

    manifest_details: dict[str, Any] = {}
    if config.get("needs_feature_manifest"):
        manifest_gates, manifest_details = evaluate_feature_manifest(config.get("feature_manifest"))
        gates.extend(manifest_gates)

    broad_coverage_pass = (
        row_count >= MIN_FORWARD_ROWS and market_count >= MIN_FORWARD_MARKETS
        if artifact_type != "forward_registry"
        else source_details.get("forward_rows", 0) >= MIN_FORWARD_ROWS
        and source_details.get("forward_markets", 0) >= MIN_FORWARD_MARKETS
    )
    gates.append(
        gate(
            "broad_market_coverage_floor",
            broad_coverage_pass,
            f"rows={row_count} markets={market_count} required_rows={MIN_FORWARD_ROWS} required_markets={MIN_FORWARD_MARKETS}",
        )
    )

    hard_failed = [item["gate"] for item in gates if item["severity"] == "hard" and not item["passed"]]
    status = "promotion_grade" if not hard_failed else "blocked"
    return {
        "dataset_id": config["dataset_id"],
        "artifact_type": artifact_type,
        "artifact_path": rel_path(path),
        "status": status,
        "row_count": row_count,
        "market_count": market_count,
        "columns": len(fieldnames),
        "hard_failed_gates": hard_failed,
        "passed_gates": [item["gate"] for item in gates if item["passed"]],
        "gates": gates,
        "source_details": source_details,
        "manifest_details": manifest_details,
        "diagnostic_counts": {
            "allowed_for_forward_promotion": count_flag(rows, "allowed_for_forward_promotion"),
            "is_recomputed_after_resolution": count_flag(rows, "is_recomputed_after_resolution"),
            "is_backfilled": count_flag(rows, "is_backfilled"),
            "is_simulated": count_flag(rows, "is_simulated") + count_flag(rows, "row_is_simulated"),
            "is_sidecar": count_flag(rows, "is_sidecar") + count_flag(rows, "row_is_sidecar"),
            "is_diagnostic_only": count_flag(rows, "is_diagnostic_only") + count_flag(rows, "row_is_diagnostic_only"),
            "posthoc_source_type": count_rows_matching_text(rows, "source_type", ("posthoc", "diagnostic")),
            "diagnostic_source_quality": count_rows_matching_text(rows, "source_quality_tier", ("posthoc", "diagnostic")),
        },
    }


def build(limit_rows: int | None = None) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    evaluations = [evaluate_dataset(config, limit_rows=limit_rows) for config in DATASETS]
    promotion_grade = [row for row in evaluations if row["status"] == "promotion_grade"]
    hard_blockers = sorted({gate for row in evaluations for gate in row["hard_failed_gates"]})
    by_dataset = {row["dataset_id"]: row for row in evaluations}
    required_forward_datasets = ["forward_registry", "forward_labeled_predictions"]
    required_forward_dataset_status = {
        dataset_id: by_dataset.get(dataset_id, {}).get("status", "missing_evaluation")
        for dataset_id in required_forward_datasets
    }
    required_forward_hard_blockers = sorted(
        {
            gate
            for dataset_id in required_forward_datasets
            for gate in by_dataset.get(dataset_id, {}).get("hard_failed_gates", [])
        }
    )
    auxiliary_hard_blockers = sorted(
        {
            gate
            for row in evaluations
            if row["dataset_id"] not in required_forward_datasets
            for gate in row["hard_failed_gates"]
        }
    )
    required_artifact_exists = {
        row["dataset_id"]: any(item["gate"] == "artifact_exists" and item["passed"] for item in row["gates"])
        for row in evaluations
        if row["dataset_id"] in required_forward_datasets
    }
    missing_required_forward_datasets = [
        dataset_id
        for dataset_id in required_forward_datasets
        if not required_artifact_exists.get(dataset_id, False)
    ]
    non_promotion_ready_required_forward_datasets = [
        dataset_id
        for dataset_id in required_forward_datasets
        if by_dataset.get(dataset_id, {}).get("status") != "promotion_grade"
    ]
    promotion_contract_ready = (
        not missing_required_forward_datasets
        and not non_promotion_ready_required_forward_datasets
        and not required_forward_hard_blockers
    )
    summary = {
        "generated_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "builder_script": Path(__file__).name,
        "contract_version": "v28_successor_source_contract_v1",
        "overall_verdict": "promotion_grade" if promotion_contract_ready else "blocked",
        "promotion_contract_ready": promotion_contract_ready,
        "required_forward_datasets": required_forward_datasets,
        "required_forward_dataset_status": required_forward_dataset_status,
        "missing_required_forward_datasets": missing_required_forward_datasets,
        "non_promotion_ready_required_forward_datasets": non_promotion_ready_required_forward_datasets,
        "required_forward_hard_blockers": required_forward_hard_blockers,
        "auxiliary_hard_blockers": auxiliary_hard_blockers,
        "dataset_count": len(evaluations),
        "promotion_grade_datasets": [row["dataset_id"] for row in promotion_grade],
        "blocked_datasets": [row["dataset_id"] for row in evaluations if row["status"] == "blocked"],
        "hard_blockers": hard_blockers,
        "minimum_forward_rows": MIN_FORWARD_ROWS,
        "minimum_forward_markets": MIN_FORWARD_MARKETS,
        "inputs": {row["dataset_id"]: row["artifact_path"] for row in evaluations},
        "outputs": {
            "json": rel_path(CONTRACT_JSON),
            "markdown": rel_path(CONTRACT_MD),
            "csv": rel_path(CONTRACT_CSV),
        },
    }
    return evaluations, summary


def write_csv_rows(rows: list[dict[str, Any]], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = ["dataset_id", "artifact_type", "status", "gate", "passed", "severity", "evidence"]
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            for item in row["gates"]:
                writer.writerow(
                    {
                        "dataset_id": row["dataset_id"],
                        "artifact_type": row["artifact_type"],
                        "status": row["status"],
                        "gate": item["gate"],
                        "passed": item["passed"],
                        "severity": item["severity"],
                        "evidence": item["evidence"],
                    }
                )


def escape_cell(value: Any) -> str:
    return str(value).replace("|", "\\|").replace("\n", " ")


def write_markdown(rows: list[dict[str, Any]], summary: dict[str, Any], path: Path) -> None:
    lines = [
        "# v28 Successor Source Contract",
        "",
        "Research-only source-quality gate. This report does not touch live bot state, orders, thresholds, secrets, or processes.",
        "",
        "## Summary",
        "",
        f"- Generated UTC: `{summary['generated_utc']}`",
        f"- Overall verdict: `{summary['overall_verdict']}`",
        f"- Promotion contract ready: `{summary['promotion_contract_ready']}`",
        f"- Required forward datasets: `{summary['required_forward_datasets']}`",
        f"- Required forward dataset status: `{summary['required_forward_dataset_status']}`",
        f"- Missing required forward datasets: `{summary['missing_required_forward_datasets']}`",
        f"- Non-promotion-ready required forward datasets: `{summary['non_promotion_ready_required_forward_datasets']}`",
        f"- Required forward hard blockers: `{summary['required_forward_hard_blockers']}`",
        f"- Auxiliary hard blockers: `{summary['auxiliary_hard_blockers']}`",
        f"- Datasets checked: `{summary['dataset_count']}`",
        f"- Promotion-grade datasets: `{summary['promotion_grade_datasets']}`",
        f"- Blocked datasets: `{summary['blocked_datasets']}`",
        f"- Hard blockers: `{summary['hard_blockers']}`",
        "",
        "## Dataset Verdicts",
        "",
        "| dataset | artifact type | rows | markets | status | hard failed gates |",
        "|---|---|---:|---:|---|---|",
    ]
    for row in rows:
        lines.append(
            f"| `{row['dataset_id']}` | `{row['artifact_type']}` | {row['row_count']} | {row['market_count']} | "
            f"`{row['status']}` | {', '.join(f'`{gate}`' for gate in row['hard_failed_gates'])} |"
        )
    lines.extend(["", "## Gate Detail", ""])
    for row in rows:
        lines.extend([f"### {row['dataset_id']}", "", "| gate | pass | evidence |", "|---|---:|---|"])
        for item in row["gates"]:
            lines.append(f"| `{item['gate']}` | {item['passed']} | {escape_cell(item['evidence'])} |")
        lines.append("")
    lines.extend(
        [
            "## Read",
            "",
            "- A dataset is promotion grade only when every hard gate passes at once.",
            "- Current seed/logged-event artifacts can support diagnostics, but they remain blocked for promotion because no rows are frozen forward evidence.",
            "- Feature manifests are checked separately so target/outcome columns cannot enter the modeled feature surface.",
        ]
    )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_outputs(rows: list[dict[str, Any]], summary: dict[str, Any]) -> None:
    EDGE_DIR.mkdir(parents=True, exist_ok=True)
    CONTRACT_JSON.write_text(json.dumps({"summary": summary, "datasets": rows}, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_csv_rows(rows, CONTRACT_CSV)
    write_markdown(rows, summary, CONTRACT_MD)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true", help="Write source-contract artifacts.")
    parser.add_argument("--dry-run", action="store_true", help="Build in memory only.")
    parser.add_argument("--limit-rows", type=int, default=None, help="Optional row limit for quick checks.")
    args = parser.parse_args()
    rows, summary = build(limit_rows=args.limit_rows)
    if args.write and not args.dry_run:
        write_outputs(rows, summary)
    print(
        json.dumps(
            {
                "overall_verdict": summary["overall_verdict"],
                "dataset_count": summary["dataset_count"],
                "promotion_grade_datasets": summary["promotion_grade_datasets"],
                "blocked_datasets": summary["blocked_datasets"],
                "hard_blockers": summary["hard_blockers"],
                "required_forward_hard_blockers": summary["required_forward_hard_blockers"],
                "written": bool(args.write and not args.dry_run),
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
