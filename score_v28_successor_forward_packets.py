"""Score v28 successor collection candidates on packet-shaped rows.

Research-only. This applies frozen simple candidate manifests to packet rows so
future pre-resolution captures can produce candidate probabilities and fair
cents. Current rows may be scored diagnostically, but they are not freeze-ready
or promotable unless the packet is complete and still pre-resolution.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import train_v28_successor_candidates as trainer
from build_v28_successor_features import (
    final_avg_abs_d_sigma_proxy,
    final_avg_d_sigma_proxy,
    final_avg_effective_horizon_minutes,
    final_avg_elapsed_window_fraction,
    final_avg_sigma_proxy_dollars,
    final_avg_uncertainty_scale,
    final_avg_variance_compression,
)
from validate_v28_successor_forward_packet import FIELD_GROUPS, row_group_missing, row_temporal_blockers


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "research_particle" / "v28_successor"
EDGE_DIR = ROOT / "logs" / "edge_research"

PACKET_ROWS_CSV = OUT_DIR / "shadow_forward_packets_latest.csv"
CANDIDATE_MANIFESTS_JSON = OUT_DIR / "candidate_manifests_latest.json"

PREDICTIONS_CSV = OUT_DIR / "forward_packet_candidate_predictions_latest.csv"
PREDICTIONS_JSON = OUT_DIR / "forward_packet_candidate_predictions_latest.json"
AUDIT_JSON = EDGE_DIR / "v28_successor_forward_packet_candidate_scoring_latest.json"
AUDIT_MD = EDGE_DIR / "v28_successor_forward_packet_candidate_scoring_latest.md"


PREDICTION_FIELDS = [
    "prediction_id",
    "row_id",
    "market_ticker",
    "decision_ts_utc",
    "market_close_ts_utc",
    "side",
    "candidate_id",
    "model_hash",
    "model_type",
    "model_track",
    "candidate_p_yes",
    "candidate_fair_yes_cents",
    "candidate_fair_no_cents",
    "candidate_fair_side_cents",
    "candidate_edge_cents",
    "v28_p_yes",
    "ask_cents",
    "packet_input_status",
    "prediction_status",
    "eligible_for_forward_freeze",
    "allowed_for_forward_collection",
    "allowed_for_forward_registry",
    "promotion_allowed",
    "blockers",
]


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


def as_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() in {"true", "1", "yes", "y"}


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


def clamp_probability(value: Any) -> float:
    parsed = as_float(value, 0.5)
    assert parsed is not None
    return min(1.0 - trainer.EPS, max(trainer.EPS, parsed))


def logit(value: Any) -> float:
    p = clamp_probability(value)
    return math.log(p / (1.0 - p))


def read_csv_rows(path: Path, limit_rows: int | None = None) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8", newline="") as handle:
        rows: list[dict[str, Any]] = []
        for idx, row in enumerate(csv.DictReader(handle)):
            if limit_rows is not None and idx >= limit_rows:
                break
            rows.append(dict(row))
        return rows


def read_json(path: Path) -> Any:
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def packet_core_missing_groups(row: dict[str, Any]) -> list[str]:
    groups = ["identity_and_clock", "causality", "market_and_book", "btc_and_feed", "v28_baseline"]
    return [group for group in groups if row_group_missing(row, group)]


def feature_row(packet: dict[str, Any]) -> dict[str, Any]:
    p_yes = clamp_probability(packet.get("v28_p_yes"))
    sigma = as_float(packet.get("v28_sigma_t_dollars"), 0.0) or 0.0
    d_sigma = as_float(packet.get("v28_d_sigma"), 0.0) or 0.0
    abs_d = abs(d_sigma)
    ask = as_float(packet.get("ask_cents"), 100.0) or 100.0
    recross = as_float(packet.get("recross_hazard_score"), 0.0) or 0.0
    seconds_to_close = as_float(packet.get("seconds_to_close"), 0.0) or 0.0
    book_implied = as_float(packet.get("book_implied_yes_from_side_ask"), 0.5) or 0.5
    btc_age = as_float(packet.get("btc_tick_age_ms"), 0.0) or 0.0
    book_age = as_float(packet.get("book_age_ms"), 0.0) or 0.0
    feed_age = max(btc_age, book_age)
    strike_distance = as_float(packet.get("strike_distance_dollars"), 0.0) or 0.0
    final_avg_input = {
        "seconds_to_close": seconds_to_close,
        "sigma_t_dollars": sigma,
        "strike": packet.get("strike"),
        "btc_price": packet.get("btc_spot") or packet.get("reference_spot"),
    }
    prior_adverse = as_float(packet.get("max_adverse_move_3m"), 0.0) or 0.0
    path_range = max(
        as_float(packet.get("max_adverse_move_3m"), 0.0) or 0.0,
        as_float(packet.get("max_adverse_move_5m"), 0.0) or 0.0,
        as_float(packet.get("max_adverse_move_15m"), 0.0) or 0.0,
    )
    arrow = as_float(packet.get("v28_arrow"), 0.0) or 0.0
    v28_edge = as_float(packet.get("v28_yes_edge_cents") if str(packet.get("side")).lower() == "yes" else packet.get("v28_no_edge_cents"), 0.0) or 0.0
    sigma_den = max(abs(sigma), 1e-9)
    out = {
        "target_v28_p_yes": p_yes,
        "v28_logit_yes": logit(p_yes),
        "v28_p_yes_centered": p_yes - 0.5,
        "v28_abs_logit_yes": abs(logit(p_yes)),
        "v28_side_probability": clamp_probability(packet.get("v28_p_side")),
        "seconds_to_close": seconds_to_close,
        "minutes_to_close": seconds_to_close / 60.0,
        "time_frac_15m": min(1.0, max(0.0, seconds_to_close / 900.0)),
        "late_window_lte_180s": 1.0 if seconds_to_close <= 180.0 else 0.0,
        "final_avg_effective_horizon_minutes": final_avg_effective_horizon_minutes(final_avg_input),
        "final_avg_variance_compression": final_avg_variance_compression(final_avg_input),
        "final_avg_uncertainty_scale": final_avg_uncertainty_scale(final_avg_input),
        "final_avg_elapsed_window_fraction": final_avg_elapsed_window_fraction(final_avg_input),
        "final_avg_sigma_proxy_dollars": final_avg_sigma_proxy_dollars(final_avg_input),
        "final_avg_d_sigma_proxy": final_avg_d_sigma_proxy(final_avg_input),
        "final_avg_abs_d_sigma_proxy": final_avg_abs_d_sigma_proxy(final_avg_input),
        "sigma_t_dollars": sigma,
        "log1p_sigma_t_dollars": math.log1p(max(0.0, sigma)),
        "recross_hazard_score": recross,
        "recross_hazard_high": 1.0 if recross >= 1.0 else 0.0,
        "ask_cents": ask,
        "ask_frac": ask / 100.0,
        "edge_cents": v28_edge,
        "side_is_yes": 1.0 if str(packet.get("side") or "").lower() == "yes" else 0.0,
        "source_is_entry": 0.0,
        "source_is_rejected_actionable": 0.0,
        "source_is_logged_approved": 0.0,
        "source_is_signal_seen": 0.0,
        "source_is_plan_built": 0.0,
        "book_implied_yes_from_side_ask": book_implied,
        "v28_minus_book_implied_yes": p_yes - book_implied,
        "v28_book_disagreement_abs": abs(p_yes - book_implied),
        "btc_age_ms": btc_age,
        "book_age_ms": book_age,
        "feed_age_ms": feed_age,
        "freshness_max_age_ms": feed_age,
        "v28_api_replay_available": 0.0,
        "v28_api_replay_abs_p_delta": 0.0,
        "v28_api_replay_minus_logged_sigma": 0.0,
        "v28_api_replay_minus_logged_d_sigma": 0.0,
        "v28_api_replay_p_anchor": clamp_probability(packet.get("v28_p_anchor")),
        "v28_api_replay_p_static_boundary_field": clamp_probability(packet.get("v28_p_static_boundary_field")),
        "v28_api_replay_p_recent_transport": clamp_probability(packet.get("v28_p_recent_transport")),
        "v28_api_replay_p_long_transport": clamp_probability(packet.get("v28_p_long_transport")),
        "v28_api_replay_edge_gate": clamp_probability(packet.get("v28_edge_gate")),
        "v28_api_replay_static_gate": clamp_probability(packet.get("v28_static_gate")),
        "log1p_v28_api_replay_transport_recent_n": math.log1p(max(0.0, as_float(packet.get("v28_transport_recent_n"), 0.0) or 0.0)),
        "log1p_v28_api_replay_transport_long_n": math.log1p(max(0.0, as_float(packet.get("v28_transport_long_n"), 0.0) or 0.0)),
        "d_sigma": d_sigma,
        "abs_d_sigma": abs_d,
        "boundary_zone_abs_d_lte_1": 1.0 if abs_d <= 1.0 else 0.0,
        "arrow": arrow,
        "arrow_x_d_sigma": arrow * d_sigma,
        "distance_per_sigma_from_prices": strike_distance / sigma_den,
        "btc_drift_from_prev_event_dollars": as_float(packet.get("signed_move_1m_dollars"), 0.0) or 0.0,
        "btc_drift_from_first_event_dollars": strike_distance,
        "prior_btc_path_range_per_sigma": path_range / sigma_den,
        "prior_adverse_path_memory_per_sigma": prior_adverse / sigma_den,
        "prior_recross_seen": 1.0 if recross >= 1.0 else 0.0,
    }
    return out


def candidate_predict(manifest: dict[str, Any], features: dict[str, Any]) -> float:
    model_type = manifest.get("model_type")
    candidate = {
        "model_type": model_type,
        "model": manifest.get("model_parameters") or {},
    }
    if model_type == "baseline_v28_raw":
        return clamp_probability(features.get("target_v28_p_yes"))
    if model_type == "regularized_logistic":
        return trainer.predict_logistic(candidate["model"], features)
    if model_type == "monotonic_tabular_calibration":
        return trainer.predict_monotonic_tabular(candidate["model"], features)
    if model_type == "fixed_logit_residual":
        return trainer.predict_fixed_logit_residual(candidate["model"], features)
    raise ValueError(f"unsupported model_type={model_type}")


def candidate_blockers(packet: dict[str, Any], manifest: dict[str, Any]) -> list[str]:
    blockers: list[str] = []
    missing_groups = packet_core_missing_groups(packet)
    if missing_groups:
        blockers.append("incomplete_input_packet:" + ",".join(missing_groups))
    temporal = row_temporal_blockers(packet)
    if temporal:
        blockers.append("temporal_blockers:" + ",".join(temporal))
    if not as_bool(packet.get("is_pre_resolution_registered")):
        blockers.append("packet_not_registered_before_close")
    if not as_bool(manifest.get("allowed_for_forward_collection")):
        blockers.append("candidate_not_allowed_for_forward_collection")
    if as_bool(manifest.get("allowed_for_forward_registry")):
        blockers.append("unexpected_promotion_registry_allowed")
    return blockers


def build(
    packet_csv: Path = PACKET_ROWS_CSV,
    manifest_json: Path = CANDIDATE_MANIFESTS_JSON,
    limit_rows: int | None = None,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    packets = read_csv_rows(packet_csv, limit_rows=limit_rows)
    manifests = [
        row
        for row in (read_json(manifest_json) or [])
        if as_bool(row.get("allowed_for_forward_collection"))
    ]
    predictions: list[dict[str, Any]] = []
    status_counts: Counter[str] = Counter()
    blocker_counts: Counter[str] = Counter()
    for packet in packets:
        features = feature_row(packet)
        packet_missing = packet_core_missing_groups(packet)
        packet_input_status = "complete" if not packet_missing and not row_temporal_blockers(packet) else "incomplete"
        for manifest in manifests:
            blockers = candidate_blockers(packet, manifest)
            for blocker in blockers:
                blocker_counts[blocker] += 1
            status = "freeze_eligible" if not blockers else "diagnostic_scored_not_freeze_ready"
            status_counts[status] += 1
            p_yes = candidate_predict(manifest, features)
            side = str(packet.get("side") or "").lower()
            ask = as_float(packet.get("ask_cents"), 100.0) or 100.0
            fair_yes = 100.0 * p_yes
            fair_no = 100.0 * (1.0 - p_yes)
            fair_side = fair_yes if side == "yes" else fair_no
            predictions.append(
                {
                    "prediction_id": stable_hash([packet.get("row_id"), manifest.get("candidate_id"), manifest.get("model_hash")]),
                    "row_id": packet.get("row_id"),
                    "market_ticker": packet.get("market_ticker"),
                    "decision_ts_utc": packet.get("decision_ts_utc"),
                    "market_close_ts_utc": packet.get("market_close_ts_utc"),
                    "side": side,
                    "candidate_id": manifest.get("candidate_id"),
                    "model_hash": manifest.get("model_hash"),
                    "model_type": manifest.get("model_type"),
                    "model_track": manifest.get("model_track"),
                    "candidate_p_yes": f"{p_yes:.10g}",
                    "candidate_fair_yes_cents": f"{fair_yes:.6f}",
                    "candidate_fair_no_cents": f"{fair_no:.6f}",
                    "candidate_fair_side_cents": f"{fair_side:.6f}",
                    "candidate_edge_cents": f"{(fair_side - ask):.6f}",
                    "v28_p_yes": packet.get("v28_p_yes"),
                    "ask_cents": packet.get("ask_cents"),
                    "packet_input_status": packet_input_status,
                    "prediction_status": status,
                    "eligible_for_forward_freeze": str(not blockers),
                    "allowed_for_forward_collection": str(as_bool(manifest.get("allowed_for_forward_collection"))),
                    "allowed_for_forward_registry": str(as_bool(manifest.get("allowed_for_forward_registry"))),
                    "promotion_allowed": "False",
                    "blockers": ";".join(blockers),
                }
            )
    summary = {
        "generated_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "builder_script": Path(__file__).name,
        "packet_rows": len(packets),
        "candidate_count": len(manifests),
        "prediction_rows": len(predictions),
        "freeze_eligible_prediction_rows": sum(1 for row in predictions if row["eligible_for_forward_freeze"] == "True"),
        "promotion_allowed_rows": 0,
        "markets": len({str(row.get("market_ticker") or "") for row in packets if row.get("market_ticker")}),
        "status_counts": dict(sorted(status_counts.items())),
        "blocker_counts": dict(sorted(blocker_counts.items())),
        "inputs": {
            "packet_csv": rel_path(packet_csv),
            "packet_csv_hash": sha256_file(packet_csv),
            "manifest_json": rel_path(manifest_json),
            "manifest_hash": sha256_file(manifest_json),
        },
        "outputs": {
            "predictions_csv": rel_path(PREDICTIONS_CSV),
            "predictions_json": rel_path(PREDICTIONS_JSON),
            "audit_json": rel_path(AUDIT_JSON),
            "audit_md": rel_path(AUDIT_MD),
        },
    }
    return predictions, summary


def write_csv_rows(rows: list[dict[str, Any]], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=PREDICTION_FIELDS)
        writer.writeheader()
        writer.writerows(rows)


def write_markdown(summary: dict[str, Any], path: Path) -> None:
    lines = [
        "# v28 Successor Forward Packet Candidate Scoring",
        "",
        "Research-only scorer for frozen collection candidates on packet-shaped rows. This report does not touch live bot state, orders, thresholds, secrets, or processes.",
        "",
        "## Summary",
        "",
        f"- Generated UTC: `{summary['generated_utc']}`",
        f"- Packet rows: `{summary['packet_rows']}`",
        f"- Collection candidates: `{summary['candidate_count']}`",
        f"- Prediction rows: `{summary['prediction_rows']}`",
        f"- Freeze-eligible prediction rows: `{summary['freeze_eligible_prediction_rows']}`",
        f"- Promotion-allowed rows: `{summary['promotion_allowed_rows']}`",
        "",
        "## Status Counts",
        "",
        "| status | rows |",
        "|---|---:|",
    ]
    for status, count in summary["status_counts"].items():
        lines.append(f"| `{status}` | {count} |")
    lines.extend(["", "## Blockers", "", "| blocker | rows |", "|---|---:|"])
    for blocker, count in summary["blocker_counts"].items():
        lines.append(f"| `{blocker}` | {count} |")
    lines.extend(
        [
            "",
            "## Read",
            "",
            "- The scorer proves frozen simple candidate manifests can be applied to packet rows.",
            "- Current predictions are diagnostic because packet rows are incomplete and/or already closed.",
            "- Freeze and promotion remain blocked until rows are complete, pre-resolution registered, broad enough, and later settled.",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_outputs(predictions: list[dict[str, Any]], summary: dict[str, Any]) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    EDGE_DIR.mkdir(parents=True, exist_ok=True)
    write_csv_rows(predictions, PREDICTIONS_CSV)
    PREDICTIONS_JSON.write_text(json.dumps(predictions[:500], indent=2, sort_keys=True) + "\n", encoding="utf-8")
    AUDIT_JSON.write_text(json.dumps({"summary": summary, "sample_rows": predictions[:20]}, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_markdown(summary, AUDIT_MD)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--packet-csv", type=Path, default=PACKET_ROWS_CSV)
    parser.add_argument("--manifest-json", type=Path, default=CANDIDATE_MANIFESTS_JSON)
    parser.add_argument("--limit-rows", type=int, default=None)
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    predictions, summary = build(args.packet_csv, args.manifest_json, args.limit_rows)
    if args.write and not args.dry_run:
        write_outputs(predictions, summary)
    print(
        json.dumps(
            {
                "packet_rows": summary["packet_rows"],
                "candidate_count": summary["candidate_count"],
                "prediction_rows": summary["prediction_rows"],
                "freeze_eligible_prediction_rows": summary["freeze_eligible_prediction_rows"],
                "promotion_allowed_rows": summary["promotion_allowed_rows"],
                "status_counts": summary["status_counts"],
                "written": bool(args.write and not args.dry_run),
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
