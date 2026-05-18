"""Audit source readiness for real v28 successor forward rows.

Research-only. This scanner inventories recorded passive book captures, v28
execution events, BTC/result caches, and latest successor artifacts to explain
why the pipeline can or cannot build freeze-ready forward packets right now.

It never reads live bot state, starts processes, places orders, or mutates live
strategy logic.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
RESEARCH_DATA = ROOT / "research_data"
OUT_DIR = ROOT / "research_particle" / "v28_successor"
EDGE_DIR = ROOT / "logs" / "edge_research"

PASSIVE_SNAPSHOTS_CSV = OUT_DIR / "passive_forward_snapshots_latest.csv"
SHADOW_PACKETS_CSV = OUT_DIR / "shadow_forward_packets_latest.csv"
FORWARD_PACKET_CANDIDATE_PREDICTIONS_CSV = OUT_DIR / "forward_packet_candidate_predictions_latest.csv"
FROZEN_FORWARD_CSV = OUT_DIR / "frozen_forward_predictions_latest.csv"
FORWARD_LABELED_CSV = OUT_DIR / "forward_labeled_predictions_latest.csv"
FORWARD_REGISTRY_CSV = OUT_DIR / "forward_registry_latest.csv"
SIDECAR_BATCH_LABELED_CSV = OUT_DIR / "sidecar_bundle_batch_labeled_latest.csv"
SIDECAR_PACKET_COLLECTION_DEMO_CSV = OUT_DIR / "forward_sidecar_packet_collection_demo_latest.csv"
LIVE_V28_EVENTS = ROOT / "logs" / "live_mushroom_v28_size2" / "execution_events.ndjson"
BTC_CACHE = EDGE_DIR / "coinbase_btc_usd_1m_cache.parquet"
MARKET_RESULT_CACHE = EDGE_DIR / "kalshi_market_result_cache.json"
MARKET_METADATA_CACHE = EDGE_DIR / "kalshi_market_metadata_cache.json"
FORWARD_COLLECTION_SPEC_JSON = EDGE_DIR / "v28_successor_forward_collection_spec_latest.json"
SIDECAR_PACKET_COLLECTOR_JSON = EDGE_DIR / "v28_successor_sidecar_packet_collector_latest.json"
SIDECAR_BATCH_EVIDENCE_JSON = EDGE_DIR / "v28_successor_sidecar_batch_evidence_score_latest.json"
SOURCE_CONTRACT_JSON = EDGE_DIR / "v28_successor_source_contract_latest.json"

READINESS_JSON = EDGE_DIR / "v28_successor_forward_source_readiness_latest.json"
READINESS_MD = EDGE_DIR / "v28_successor_forward_source_readiness_latest.md"

MIN_FORWARD_MARKETS = 40
MIN_FORWARD_ROWS = 200

V28_BASE_FIELDS = [
    "mushroom_v28_p_yes",
    "mushroom_v28_p_side",
    "mushroom_v28_fair_yes_cents",
    "mushroom_v28_fair_no_cents",
    "mushroom_v28_sigma_t_dollars",
    "mushroom_v28_d_sigma",
    "mushroom_v28_arrow",
    "mushroom_v28_strike",
    "mushroom_v28_btc_price",
]

V28_NATIVE_COMPONENT_FIELDS = [
    "mushroom_v28_p_anchor",
    "mushroom_v28_p_static_boundary_field",
    "mushroom_v28_p_recent_transport",
    "mushroom_v28_p_long_transport",
    "mushroom_v28_transport_recent_n",
    "mushroom_v28_transport_long_n",
]

LEGACY_COMPONENT_FIELDS = [
    "mushroom_p_anchor",
    "mushroom_p_recent_transport",
    "mushroom_p_long_transport",
    "mushroom_transport_recent_n",
    "mushroom_transport_long_n",
]


def rel_path(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(ROOT)).replace("\\", "/")
    except ValueError:
        return str(path)


def sha256_file(path: Path) -> str | None:
    if not path.exists() or path.stat().st_size > 25_000_000:
        return None
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def nonempty(value: Any) -> bool:
    return value is not None and str(value).strip() != ""


def as_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() in {"true", "1", "yes", "y"}


def read_json(path: Path) -> Any:
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def read_csv_rows(path: Path, limit_rows: int | None = None) -> tuple[list[dict[str, Any]], list[str]]:
    if not path.exists():
        return [], []
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        rows: list[dict[str, Any]] = []
        for idx, row in enumerate(reader):
            if limit_rows is not None and idx >= limit_rows:
                break
            rows.append(dict(row))
    return rows, list(reader.fieldnames or [])


def count_csv_rows(path: Path) -> int:
    if not path.exists():
        return 0
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.reader(handle)
        return max(0, sum(1 for _ in reader) - 1)


def iter_ndjson(path: Path, limit_rows: int | None = None) -> list[tuple[int, dict[str, Any]]]:
    rows: list[tuple[int, dict[str, Any]]] = []
    if not path.exists():
        return rows
    with path.open("r", encoding="utf-8", errors="replace") as handle:
        for line_number, line in enumerate(handle, start=1):
            if limit_rows is not None and len(rows) >= limit_rows:
                break
            line = line.strip()
            if not line:
                continue
            try:
                payload = json.loads(line)
            except json.JSONDecodeError:
                continue
            if isinstance(payload, dict):
                rows.append((line_number, payload))
    return rows


def summarize_passive_snapshots() -> dict[str, Any]:
    rows, fieldnames = read_csv_rows(PASSIVE_SNAPSHOTS_CSV)
    markets = {row.get("market_ticker") for row in rows if nonempty(row.get("market_ticker"))}
    def flag_count(field: str) -> int:
        return sum(1 for row in rows if as_bool(row.get(field)))

    missing_counts = {
        "btc_state": sum(1 for row in rows if not as_bool(row.get("has_btc_state"))),
        "v28_baseline": sum(1 for row in rows if not as_bool(row.get("has_v28_baseline"))),
        "candidate_prediction": sum(1 for row in rows if not as_bool(row.get("has_candidate_prediction"))),
        "settlement_label": sum(1 for row in rows if not as_bool(row.get("has_settlement_label"))),
        "top_book": sum(1 for row in rows if not as_bool(row.get("has_top_book"))),
    }
    return {
        "path": rel_path(PASSIVE_SNAPSHOTS_CSV),
        "exists": PASSIVE_SNAPSHOTS_CSV.exists(),
        "columns": len(fieldnames),
        "rows": len(rows),
        "markets": len(markets),
        "pre_resolution_rows": flag_count("is_pre_resolution"),
        "registered_pre_resolution_rows": flag_count("is_pre_resolution_registered"),
        "eligible_for_candidate_prediction_rows": flag_count("eligible_for_candidate_prediction"),
        "missing_counts": missing_counts,
        "sha256": sha256_file(PASSIVE_SNAPSHOTS_CSV),
    }


def summarize_shadow_packets() -> dict[str, Any]:
    rows, fieldnames = read_csv_rows(SHADOW_PACKETS_CSV)
    markets = {row.get("market_ticker") for row in rows if nonempty(row.get("market_ticker"))}
    packet_ready_like = sum(
        1
        for row in rows
        if all(nonempty(row.get(field)) for field in ("btc_spot", "v28_p_yes", "candidate_p_yes", "candidate_id"))
    )
    native_component_rows = sum(1 for row in rows if all(nonempty(row.get(field)) for field in ("v28_p_anchor", "v28_p_recent_transport", "v28_p_long_transport")))
    return {
        "path": rel_path(SHADOW_PACKETS_CSV),
        "exists": SHADOW_PACKETS_CSV.exists(),
        "columns": len(fieldnames),
        "rows": len(rows),
        "markets": len(markets),
        "rows_with_btc_v28_candidate_core": packet_ready_like,
        "rows_with_native_v28_component_triplet": native_component_rows,
        "sha256": sha256_file(SHADOW_PACKETS_CSV),
    }


def summarize_forward_packet_predictions() -> dict[str, Any]:
    rows, fieldnames = read_csv_rows(FORWARD_PACKET_CANDIDATE_PREDICTIONS_CSV)
    markets = {row.get("market_ticker") for row in rows if nonempty(row.get("market_ticker"))}
    candidate_ids = {row.get("candidate_id") for row in rows if nonempty(row.get("candidate_id"))}
    prediction_status_counts = Counter(str(row.get("prediction_status") or "") for row in rows)
    packet_input_status_counts = Counter(str(row.get("packet_input_status") or "") for row in rows)
    blocker_counts: Counter[str] = Counter()
    for row in rows:
        for blocker in str(row.get("blockers") or "").replace(",", ";").split(";"):
            blocker = blocker.strip()
            if blocker:
                blocker_counts[blocker] += 1
    return {
        "path": rel_path(FORWARD_PACKET_CANDIDATE_PREDICTIONS_CSV),
        "exists": FORWARD_PACKET_CANDIDATE_PREDICTIONS_CSV.exists(),
        "columns": len(fieldnames),
        "rows": len(rows),
        "markets": len(markets),
        "candidate_count": len(candidate_ids),
        "eligible_for_forward_freeze_rows": sum(1 for row in rows if as_bool(row.get("eligible_for_forward_freeze"))),
        "allowed_for_forward_collection_rows": sum(1 for row in rows if as_bool(row.get("allowed_for_forward_collection"))),
        "allowed_for_forward_registry_rows": sum(1 for row in rows if as_bool(row.get("allowed_for_forward_registry"))),
        "promotion_allowed_rows": sum(1 for row in rows if as_bool(row.get("promotion_allowed"))),
        "prediction_status_counts": dict(sorted(prediction_status_counts.items())),
        "packet_input_status_counts": dict(sorted(packet_input_status_counts.items())),
        "blocker_counts_top": dict(blocker_counts.most_common(20)),
        "sha256": sha256_file(FORWARD_PACKET_CANDIDATE_PREDICTIONS_CSV),
    }


def summarize_sidecar_packet_collector() -> dict[str, Any]:
    rows, fieldnames = read_csv_rows(SIDECAR_PACKET_COLLECTION_DEMO_CSV)
    markets = {row.get("market_ticker") for row in rows if nonempty(row.get("market_ticker"))}
    packet_ready_rows = sum(
        1
        for row in rows
        if all(
            nonempty(row.get(field))
            for field in ("btc_spot", "v28_p_yes", "v28_p_anchor", "candidate_p_yes", "candidate_id")
        )
    )
    collector = read_json(SIDECAR_PACKET_COLLECTOR_JSON) or {}
    collector_summary = collector.get("summary", {}) if isinstance(collector, dict) else {}
    return {
        "path": rel_path(SIDECAR_PACKET_COLLECTION_DEMO_CSV),
        "exists": SIDECAR_PACKET_COLLECTION_DEMO_CSV.exists(),
        "columns": len(fieldnames),
        "rows": len(rows),
        "markets": len(markets),
        "packet_ready_like_rows": packet_ready_rows,
        "simulated_rows": sum(1 for row in rows if as_bool(row.get("is_simulated"))),
        "diagnostic_rows": sum(1 for row in rows if as_bool(row.get("is_diagnostic_only"))),
        "audit_json": rel_path(SIDECAR_PACKET_COLLECTOR_JSON),
        "audit_exists": SIDECAR_PACKET_COLLECTOR_JSON.exists(),
        "collector_status": collector_summary.get("collector_status"),
        "demo_packet_ready_rows": collector_summary.get("demo_packet_ready_rows"),
        "promotion_allowed": (collector_summary.get("promotion_status") or {}).get("allowed"),
        "sha256": sha256_file(SIDECAR_PACKET_COLLECTION_DEMO_CSV),
    }


def summarize_sidecar_batch_evidence() -> dict[str, Any]:
    rows, fieldnames = read_csv_rows(SIDECAR_BATCH_LABELED_CSV)
    joined_rows = [row for row in rows if str(row.get("label_join_status") or "") == "joined_post_resolution"]
    markets = {row.get("market_ticker") for row in joined_rows if nonempty(row.get("market_ticker"))}
    evidence = read_json(SIDECAR_BATCH_EVIDENCE_JSON) or {}
    evidence_summary = evidence.get("summary", {}) if isinstance(evidence, dict) else {}
    return {
        "path": rel_path(SIDECAR_BATCH_LABELED_CSV),
        "exists": SIDECAR_BATCH_LABELED_CSV.exists(),
        "columns": len(fieldnames),
        "rows": len(rows),
        "joined_rows": len(joined_rows),
        "joined_markets": len(markets),
        "evidence_json": rel_path(SIDECAR_BATCH_EVIDENCE_JSON),
        "evidence_exists": SIDECAR_BATCH_EVIDENCE_JSON.exists(),
        "evidence_status": evidence_summary.get("evidence_status"),
        "clean_forward_rows": evidence_summary.get("clean_forward_rows"),
        "clean_forward_markets": evidence_summary.get("clean_forward_markets"),
        "candidate_count": evidence_summary.get("candidate_count"),
        "promotable_candidate_count": evidence_summary.get("promotable_candidate_count"),
        "promotion_allowed": (evidence_summary.get("promotion_status") or {}).get("allowed"),
        "sha256": sha256_file(SIDECAR_BATCH_LABELED_CSV),
    }


def summarize_research_datasets() -> dict[str, Any]:
    dataset_rows: list[dict[str, Any]] = []
    for manifest_path in sorted(RESEARCH_DATA.glob("particle*/metadata/dataset_manifest.json")):
        manifest = read_json(manifest_path) or {}
        dataset_dir = manifest_path.parents[1]
        checkpoint_files = list(dataset_dir.glob("book_checkpoints/**/*.ndjson"))
        raw_event_counts: Counter[str] = Counter()
        raw_event_files = list(dataset_dir.glob("raw_events/type=*/**/*.ndjson"))
        for path in raw_event_files:
            parts = path.parts
            event_type = next((part.split("=", 1)[1] for part in parts if part.startswith("type=")), "unknown")
            raw_event_counts[event_type] += 1
        checkpoint_rows = sum(len(iter_ndjson(path)) for path in checkpoint_files)
        dataset_rows.append(
            {
                "dataset_tag": manifest.get("dataset_tag") or dataset_dir.name,
                "path": rel_path(dataset_dir),
                "started_at_utc": manifest.get("started_at_utc"),
                "ended_at_utc": manifest.get("ended_at_utc"),
                "markets": len(manifest.get("market_tickers") or []),
                "market_tickers": manifest.get("market_tickers") or [],
                "records_book_checkpoints": bool(manifest.get("records_book_checkpoints")),
                "records_raw_market_feed": bool(manifest.get("records_raw_market_feed")),
                "records_settlement_labels": bool(manifest.get("records_settlement_labels")),
                "records_strategy_decisions": bool(manifest.get("records_strategy_decisions")),
                "book_checkpoint_files": len(checkpoint_files),
                "book_checkpoint_rows": checkpoint_rows,
                "raw_event_file_types": dict(sorted(raw_event_counts.items())),
            }
        )
    return {
        "dataset_count": len(dataset_rows),
        "total_markets_manifest": len({market for row in dataset_rows for market in row["market_tickers"]}),
        "total_book_checkpoint_rows": sum(row["book_checkpoint_rows"] for row in dataset_rows),
        "datasets": dataset_rows,
    }


def summarize_live_v28_events() -> dict[str, Any]:
    rows = iter_ndjson(LIVE_V28_EVENTS)
    event_counts: Counter[str] = Counter()
    market_set = set()
    base_complete = 0
    native_component_complete = 0
    legacy_component_complete = 0
    approved_rows = 0
    for _line, row in rows:
        event_type = str(row.get("event_type") or "")
        event_counts[event_type] += 1
        market = row.get("market") or row.get("market_ticker")
        if market:
            market_set.add(str(market))
        if as_bool(row.get("mushroom_v28_approved")):
            approved_rows += 1
        if all(nonempty(row.get(field)) for field in V28_BASE_FIELDS):
            base_complete += 1
        if all(nonempty(row.get(field)) for field in V28_NATIVE_COMPONENT_FIELDS):
            native_component_complete += 1
        if all(nonempty(row.get(field)) for field in LEGACY_COMPONENT_FIELDS):
            legacy_component_complete += 1
    return {
        "path": rel_path(LIVE_V28_EVENTS),
        "exists": LIVE_V28_EVENTS.exists(),
        "rows": len(rows),
        "markets": len(market_set),
        "approved_rows": approved_rows,
        "event_type_counts_top": dict(event_counts.most_common(20)),
        "rows_with_v28_base_fields": base_complete,
        "rows_with_v28_native_component_fields": native_component_complete,
        "rows_with_legacy_mushroom_component_fields": legacy_component_complete,
        "required_native_component_fields": V28_NATIVE_COMPONENT_FIELDS,
        "legacy_component_fields_seen": LEGACY_COMPONENT_FIELDS,
        "sha256": sha256_file(LIVE_V28_EVENTS),
    }


def summarize_cache(path: Path) -> dict[str, Any]:
    out = {
        "path": rel_path(path),
        "exists": path.exists(),
        "size_bytes": path.stat().st_size if path.exists() else None,
        "sha256": sha256_file(path),
    }
    if path.suffix.lower() in {".json"} and path.exists():
        data = read_json(path)
        if isinstance(data, dict):
            out["json_keys"] = len(data)
        elif isinstance(data, list):
            out["json_rows"] = len(data)
    return out


def build() -> tuple[dict[str, Any], dict[str, Any]]:
    passive = summarize_passive_snapshots()
    shadow = summarize_shadow_packets()
    packet_predictions = summarize_forward_packet_predictions()
    sidecar_collector = summarize_sidecar_packet_collector()
    sidecar_batch_evidence = summarize_sidecar_batch_evidence()
    research_datasets = summarize_research_datasets()
    live_v28 = summarize_live_v28_events()
    frozen_rows = count_csv_rows(FROZEN_FORWARD_CSV)
    labeled_rows = count_csv_rows(FORWARD_LABELED_CSV)
    forward_registry_rows = count_csv_rows(FORWARD_REGISTRY_CSV)
    collection_spec = read_json(FORWARD_COLLECTION_SPEC_JSON) or {}
    source_contract = read_json(SOURCE_CONTRACT_JSON) or {}
    source_contract_summary = source_contract.get("summary", {}) if isinstance(source_contract, dict) else {}

    blockers: list[str] = []
    if passive["rows"] <= 0:
        blockers.append("no_passive_book_snapshots")
    if passive["markets"] < MIN_FORWARD_MARKETS:
        blockers.append("passive_market_coverage_below_forward_floor")
    for field, missing in passive["missing_counts"].items():
        if missing:
            blockers.append(f"passive_rows_missing_{field}")
    if live_v28["rows_with_v28_native_component_fields"] <= 0:
        blockers.append("live_v28_events_missing_native_component_fields")
    if live_v28["rows_with_v28_base_fields"] <= 0:
        blockers.append("live_v28_events_missing_base_fields")
    if research_datasets["total_markets_manifest"] < MIN_FORWARD_MARKETS:
        blockers.append("recorded_research_dataset_market_coverage_below_forward_floor")
    if not any(row["records_settlement_labels"] for row in research_datasets["datasets"]):
        blockers.append("recorded_research_datasets_do_not_include_settlement_labels")
    if not any(row["records_strategy_decisions"] for row in research_datasets["datasets"]):
        blockers.append("recorded_research_datasets_do_not_include_strategy_decisions")
    if packet_predictions["rows"] <= 0:
        blockers.append("no_forward_packet_candidate_predictions")
    elif packet_predictions["eligible_for_forward_freeze_rows"] <= 0:
        blockers.append("no_freeze_eligible_forward_packet_candidate_predictions")
    if packet_predictions["allowed_for_forward_registry_rows"] <= 0:
        blockers.append("packet_predictions_not_allowed_for_forward_registry")
    if int(sidecar_collector.get("demo_packet_ready_rows") or 0) <= 0:
        blockers.append("sidecar_packet_collector_not_contract_ready")
    if sidecar_collector["simulated_rows"] > 0 or sidecar_collector["diagnostic_rows"] > 0:
        blockers.append("sidecar_packet_collector_rows_are_demo_not_forward_evidence")
    if sidecar_batch_evidence["joined_rows"] > 0 and (
        sidecar_batch_evidence["joined_rows"] < MIN_FORWARD_ROWS
        or sidecar_batch_evidence["joined_markets"] < MIN_FORWARD_MARKETS
    ):
        blockers.append("sidecar_batch_evidence_below_forward_floor")
    if frozen_rows == 0:
        blockers.append("no_frozen_forward_predictions")
    if forward_registry_rows == 0:
        blockers.append("forward_registry_empty")
    if labeled_rows == 0:
        blockers.append("no_forward_labeled_predictions")
    if source_contract_summary.get("promotion_contract_ready") is not True:
        blockers.append("source_contract_not_promotion_ready")
    if passive["rows"] > 0 and live_v28["rows"] > 0 and BTC_CACHE.exists() and frozen_rows == 0:
        blockers.append("source_families_not_time_joined_into_frozen_rows")

    summary = {
        "generated_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "builder_script": Path(__file__).name,
        "overall_status": "ready_for_freeze_collection" if not blockers else "blocked_missing_freeze_ready_sources",
        "blockers": sorted(set(blockers)),
        "minimum_forward_rows": MIN_FORWARD_ROWS,
        "minimum_forward_markets": MIN_FORWARD_MARKETS,
        "passive_rows": passive["rows"],
        "passive_markets": passive["markets"],
        "research_dataset_count": research_datasets["dataset_count"],
        "research_dataset_markets": research_datasets["total_markets_manifest"],
        "live_v28_event_rows": live_v28["rows"],
        "live_v28_base_field_rows": live_v28["rows_with_v28_base_fields"],
        "live_v28_native_component_rows": live_v28["rows_with_v28_native_component_fields"],
        "forward_packet_prediction_rows": packet_predictions["rows"],
        "freeze_eligible_packet_prediction_rows": packet_predictions["eligible_for_forward_freeze_rows"],
        "sidecar_collector_status": sidecar_collector["collector_status"],
        "sidecar_collector_demo_packet_ready_rows": sidecar_collector["demo_packet_ready_rows"],
        "sidecar_collector_promotion_allowed": sidecar_collector["promotion_allowed"],
        "sidecar_batch_joined_rows": sidecar_batch_evidence["joined_rows"],
        "sidecar_batch_joined_markets": sidecar_batch_evidence["joined_markets"],
        "sidecar_batch_evidence_status": sidecar_batch_evidence["evidence_status"],
        "sidecar_batch_evidence_promotable_candidate_count": sidecar_batch_evidence["promotable_candidate_count"],
        "sidecar_batch_evidence_promotion_allowed": sidecar_batch_evidence["promotion_allowed"],
        "frozen_forward_rows": frozen_rows,
        "forward_registry_rows": forward_registry_rows,
        "forward_labeled_rows": labeled_rows,
        "source_contract_promotion_ready": source_contract_summary.get("promotion_contract_ready"),
        "promotion_allowed": False,
        "promotion_status": {
            "allowed": False,
            "reason": "source readiness is an evidence audit only; promotion remains delegated to source contract, forward evidence scorer, and promotion verifier",
        },
        "outputs": {
            "json": rel_path(READINESS_JSON),
            "markdown": rel_path(READINESS_MD),
        },
    }
    report = {
        "summary": summary,
        "passive_snapshots": passive,
        "shadow_packets": shadow,
        "forward_packet_candidate_predictions": packet_predictions,
        "sidecar_packet_collector": sidecar_collector,
        "sidecar_batch_evidence": sidecar_batch_evidence,
        "research_datasets": research_datasets,
        "live_v28_events": live_v28,
        "caches": {
            "btc_cache": summarize_cache(BTC_CACHE),
            "market_result_cache": summarize_cache(MARKET_RESULT_CACHE),
            "market_metadata_cache": summarize_cache(MARKET_METADATA_CACHE),
        },
        "latest_artifacts": {
            "frozen_forward_csv": rel_path(FROZEN_FORWARD_CSV),
            "forward_registry_csv": rel_path(FORWARD_REGISTRY_CSV),
            "forward_labeled_csv": rel_path(FORWARD_LABELED_CSV),
            "forward_collection_spec_json": rel_path(FORWARD_COLLECTION_SPEC_JSON),
            "forward_collection_status": (collection_spec.get("summary") or {}).get("status") if isinstance(collection_spec, dict) else None,
            "sidecar_packet_collector_json": rel_path(SIDECAR_PACKET_COLLECTOR_JSON),
            "sidecar_packet_collector_status": sidecar_collector["collector_status"],
            "sidecar_batch_labeled_csv": rel_path(SIDECAR_BATCH_LABELED_CSV),
            "sidecar_batch_evidence_json": rel_path(SIDECAR_BATCH_EVIDENCE_JSON),
            "sidecar_batch_evidence_status": sidecar_batch_evidence["evidence_status"],
            "source_contract_json": rel_path(SOURCE_CONTRACT_JSON),
            "source_contract_promotion_ready": source_contract_summary.get("promotion_contract_ready"),
        },
    }
    return report, summary


def write_markdown(report: dict[str, Any], path: Path) -> None:
    summary = report["summary"]
    passive = report["passive_snapshots"]
    live_v28 = report["live_v28_events"]
    sidecar = report["sidecar_packet_collector"]
    sidecar_batch = report["sidecar_batch_evidence"]
    research = report["research_datasets"]
    lines = [
        "# v28 Successor Forward Source Readiness",
        "",
        "Research-only source readiness audit. This report does not touch live bot state, orders, thresholds, secrets, or processes.",
        "",
        "## Summary",
        "",
        f"- Generated UTC: `{summary['generated_utc']}`",
        f"- Overall status: `{summary['overall_status']}`",
        f"- Passive rows / markets: `{summary['passive_rows']}` / `{summary['passive_markets']}`",
        f"- Research datasets / markets: `{summary['research_dataset_count']}` / `{summary['research_dataset_markets']}`",
        f"- Live v28 event rows: `{summary['live_v28_event_rows']}`",
        f"- Live v28 base-field rows: `{summary['live_v28_base_field_rows']}`",
        f"- Live v28 native component rows: `{summary['live_v28_native_component_rows']}`",
        f"- Forward packet prediction rows: `{summary['forward_packet_prediction_rows']}`",
        f"- Freeze-eligible packet prediction rows: `{summary['freeze_eligible_packet_prediction_rows']}`",
        f"- Sidecar collector status: `{summary['sidecar_collector_status']}`",
        f"- Sidecar collector demo packet-ready rows: `{summary['sidecar_collector_demo_packet_ready_rows']}`",
        f"- Sidecar collector promotion allowed: `{summary['sidecar_collector_promotion_allowed']}`",
        f"- Sidecar batch joined rows / markets: `{summary['sidecar_batch_joined_rows']}` / `{summary['sidecar_batch_joined_markets']}`",
        f"- Sidecar batch evidence status: `{summary['sidecar_batch_evidence_status']}`",
        f"- Sidecar batch evidence promotion allowed: `{summary['sidecar_batch_evidence_promotion_allowed']}`",
        f"- Frozen forward rows: `{summary['frozen_forward_rows']}`",
        f"- Forward registry rows: `{summary['forward_registry_rows']}`",
        f"- Forward labeled rows: `{summary['forward_labeled_rows']}`",
        f"- Source contract promotion-ready: `{summary['source_contract_promotion_ready']}`",
        f"- Promotion allowed by this report: `{summary['promotion_allowed']}`",
        "",
        "## Blockers",
        "",
    ]
    for blocker in summary["blockers"]:
        lines.append(f"- `{blocker}`")
    lines.extend(
        [
            "",
            "## Passive Snapshot Coverage",
            "",
            f"- Path: `{passive['path']}`",
            f"- Rows: `{passive['rows']}`",
            f"- Markets: `{passive['markets']}`",
            f"- Registered pre-resolution rows: `{passive['registered_pre_resolution_rows']}`",
            f"- Missing counts: `{passive['missing_counts']}`",
            "",
            "## Live v28 Event Coverage",
            "",
            f"- Path: `{live_v28['path']}`",
            f"- Rows with v28 base fields: `{live_v28['rows_with_v28_base_fields']}`",
            f"- Rows with native v28 component fields: `{live_v28['rows_with_v28_native_component_fields']}`",
            f"- Rows with legacy component fields: `{live_v28['rows_with_legacy_mushroom_component_fields']}`",
            f"- Required native component fields: `{live_v28['required_native_component_fields']}`",
            "",
            "## Sidecar Collector",
            "",
            f"- Path: `{sidecar['path']}`",
            f"- Rows: `{sidecar['rows']}`",
            f"- Packet-ready-like rows: `{sidecar['packet_ready_like_rows']}`",
            f"- Simulated rows: `{sidecar['simulated_rows']}`",
            f"- Diagnostic rows: `{sidecar['diagnostic_rows']}`",
            f"- Collector status: `{sidecar['collector_status']}`",
            f"- Promotion allowed: `{sidecar['promotion_allowed']}`",
            "",
            "## Sidecar Batch Evidence",
            "",
            f"- Path: `{sidecar_batch['path']}`",
            f"- Joined rows: `{sidecar_batch['joined_rows']}`",
            f"- Joined markets: `{sidecar_batch['joined_markets']}`",
            f"- Evidence status: `{sidecar_batch['evidence_status']}`",
            f"- Candidate count: `{sidecar_batch['candidate_count']}`",
            f"- Promotable candidates by this evidence alone: `{sidecar_batch['promotable_candidate_count']}`",
            f"- Promotion allowed: `{sidecar_batch['promotion_allowed']}`",
            "",
            "## Research Datasets",
            "",
            "| dataset | markets | checkpoints | raw event types | labels | decisions |",
            "|---|---:|---:|---|---:|---:|",
        ]
    )
    for row in research["datasets"]:
        lines.append(
            f"| `{row['dataset_tag']}` | {row['markets']} | {row['book_checkpoint_rows']} | "
            f"`{row['raw_event_file_types']}` | {row['records_settlement_labels']} | {row['records_strategy_decisions']} |"
        )
    lines.extend(
        [
            "",
            "## Read",
            "",
            "- Passive book data exists, but current rows are not freeze-ready because they are not paired with BTC state, native v28 component packets, and candidate predictions at capture time.",
            "- Sidecar batch evidence is now scored separately, but it remains below coverage floors and does not replace the canonical promotion ledger.",
            "- Existing live v28 logs contain many base FV fields, but the native p_anchor/static/recent/long component fields are not present under the v28 names required for promotion-grade packets.",
            "- This report is diagnostic and does not grant promotion.",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_outputs(report: dict[str, Any], summary: dict[str, Any]) -> None:
    EDGE_DIR.mkdir(parents=True, exist_ok=True)
    READINESS_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_markdown(report, READINESS_MD)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true", help="Write readiness artifacts.")
    parser.add_argument("--dry-run", action="store_true", help="Build in memory only.")
    args = parser.parse_args()
    report, summary = build()
    if args.write and not args.dry_run:
        write_outputs(report, summary)
    print(
        json.dumps(
            {
                "overall_status": summary["overall_status"],
                "blockers": summary["blockers"],
                "passive_rows": summary["passive_rows"],
                "passive_markets": summary["passive_markets"],
                "live_v28_base_field_rows": summary["live_v28_base_field_rows"],
                "live_v28_native_component_rows": summary["live_v28_native_component_rows"],
                "forward_packet_prediction_rows": summary["forward_packet_prediction_rows"],
                "freeze_eligible_packet_prediction_rows": summary["freeze_eligible_packet_prediction_rows"],
                "sidecar_batch_joined_rows": summary["sidecar_batch_joined_rows"],
                "sidecar_batch_evidence_status": summary["sidecar_batch_evidence_status"],
                "frozen_forward_rows": summary["frozen_forward_rows"],
                "forward_registry_rows": summary["forward_registry_rows"],
                "written": bool(args.write and not args.dry_run),
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
