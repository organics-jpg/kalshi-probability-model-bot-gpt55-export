"""Build the forward collection spec for the v28 successor FV pipeline.

Research-only. This converts the packet contract, collection candidate
manifests, and latest blocker reports into an executable handoff for future
passive capture runs. It does not touch live bot state, orders, thresholds,
secrets, or processes.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "research_particle" / "v28_successor"
EDGE_DIR = ROOT / "logs" / "edge_research"

PACKET_TEMPLATE_JSON = OUT_DIR / "forward_packet_template_latest.json"
CANDIDATE_MANIFESTS_JSON = OUT_DIR / "candidate_manifests_latest.json"
LOGGED_CANDIDATE_MANIFESTS_JSON = OUT_DIR / "candidate_manifests_logged_events_latest.json"
PACKET_CONTRACT_JSON = EDGE_DIR / "v28_successor_forward_packet_contract_latest.json"
SHADOW_PACKET_JSON = EDGE_DIR / "v28_successor_shadow_forward_packets_latest.json"
PACKET_SCORING_JSON = EDGE_DIR / "v28_successor_forward_packet_candidate_scoring_latest.json"
FORWARD_PREFLIGHT_JSON = EDGE_DIR / "v28_successor_forward_freeze_preflight_latest.json"
FROZEN_FORWARD_JSON = EDGE_DIR / "v28_successor_frozen_forward_predictions_latest.json"
PACKET_ADAPTER_JSON = EDGE_DIR / "v28_successor_forward_packet_adapter_latest.json"
PUBLIC_REST_SIDECAR_BUNDLE_JSON = EDGE_DIR / "v28_successor_public_rest_sidecar_bundle_latest.json"
PUBLIC_REST_SIDECAR_BATCH_JSON = EDGE_DIR / "v28_successor_public_rest_sidecar_batch_latest.json"
SIDECAR_INPUT_BUNDLE_CONTRACT_JSON = EDGE_DIR / "v28_successor_sidecar_input_bundle_contract_latest.json"
SIDECAR_PACKET_COLLECTOR_JSON = EDGE_DIR / "v28_successor_sidecar_packet_collector_latest.json"
SIDECAR_BUNDLE_FREEZE_HANDOFF_JSON = EDGE_DIR / "v28_successor_sidecar_bundle_freeze_handoff_latest.json"
SIDECAR_BUNDLE_BATCH_HANDOFF_JSON = EDGE_DIR / "v28_successor_sidecar_bundle_batch_handoff_latest.json"
SIDECAR_BUNDLE_BATCH_SETTLEMENT_LABELS_JSON = EDGE_DIR / "v28_successor_sidecar_bundle_batch_settlement_labels_latest.json"
SIDECAR_BUNDLE_BATCH_LABEL_JOIN_JSON = EDGE_DIR / "v28_successor_sidecar_bundle_batch_label_join_latest.json"
SIDECAR_BATCH_EVIDENCE_SCORE_JSON = EDGE_DIR / "v28_successor_sidecar_batch_evidence_score_latest.json"
SIDECAR_COLLECTION_CYCLE_JSON = EDGE_DIR / "v28_successor_sidecar_collection_cycle_latest.json"
FORWARD_PACKET_FREEZE_HANDOFF_JSON = EDGE_DIR / "v28_successor_forward_packet_freeze_handoff_latest.json"
FORWARD_LABEL_JOIN_JSON = EDGE_DIR / "v28_successor_forward_label_join_latest.json"
FORWARD_EVIDENCE_SCORE_JSON = EDGE_DIR / "v28_successor_forward_evidence_score_latest.json"

SPEC_JSON = OUT_DIR / "forward_collection_spec_latest.json"
SPEC_AUDIT_JSON = EDGE_DIR / "v28_successor_forward_collection_spec_latest.json"
SPEC_MD = EDGE_DIR / "v28_successor_forward_collection_spec_latest.md"


SOURCE_MAP = {
    "identity_and_clock": {
        "source": "native passive market metadata plus checkpoint clock",
        "collector_rule": "Write every watched market/side row with decision_ts_utc and market_close_ts_utc before close.",
    },
    "causality": {
        "source": "collector runtime flags",
        "collector_rule": "Set pre-resolution flags at write time; settlement fields must be absent before freeze.",
    },
    "market_and_book": {
        "source": "Kalshi passive orderbook checkpoint",
        "collector_rule": "Capture top of book, side ask/bid, derived YES book price, width, raw_capture_ts_utc, and source event count.",
    },
    "btc_and_feed": {
        "source": "BTC tick/history buffer",
        "collector_rule": "Persist current BTC spot/tick age plus 15s/60s/180s/300s/900s returns and side-aware adverse moves using only ticks earlier than decision_ts_utc.",
    },
    "v28_baseline": {
        "source": "v28 FV API called at decision time",
        "collector_rule": "Call predict_many/edge_many before close and store p_yes/fair cents plus native components: p_anchor, static boundary, recent/long transport, gates, counts, sigma, d_sigma, arrow, volshock.",
    },
    "candidate_prediction": {
        "source": "frozen collection candidate manifests",
        "collector_rule": "Score all allowed_for_forward_collection manifests against the packet before close; store model_hash, candidate probability, fair cents, and feature/table hashes.",
    },
}


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


def read_json(path: Path) -> Any:
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def as_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() in {"true", "1", "yes", "y"}


def collection_candidates(path: Path) -> list[dict[str, Any]]:
    manifests = read_json(path) or []
    if not isinstance(manifests, list):
        return []
    out: list[dict[str, Any]] = []
    for row in manifests:
        if not as_bool(row.get("allowed_for_forward_collection")):
            continue
        out.append(
            {
                "candidate_id": row.get("candidate_id"),
                "model_hash": row.get("model_hash"),
                "model_type": row.get("model_type"),
                "model_track": row.get("model_track"),
                "feature_columns": row.get("feature_columns", []),
                "allowed_for_forward_collection": True,
                "allowed_for_forward_registry": as_bool(row.get("allowed_for_forward_registry")),
                "promotion_gate_status": (row.get("promotion_gate") or {}).get("status"),
                "promotion_fail_reasons": (row.get("promotion_gate") or {}).get("fail_reasons", []),
                "collection_gate": row.get("forward_collection_gate"),
            }
        )
    return out


def build() -> tuple[dict[str, Any], dict[str, Any]]:
    template = read_json(PACKET_TEMPLATE_JSON) or {}
    field_groups = template.get("field_groups") or {}
    packet_contract = read_json(PACKET_CONTRACT_JSON) or {}
    shadow_packets = read_json(SHADOW_PACKET_JSON) or {}
    packet_scoring = read_json(PACKET_SCORING_JSON) or {}
    preflight = read_json(FORWARD_PREFLIGHT_JSON) or {}
    frozen_forward = read_json(FROZEN_FORWARD_JSON) or {}
    packet_adapter = read_json(PACKET_ADAPTER_JSON) or {}
    packet_adapter_summary = packet_adapter.get("summary", {}) if isinstance(packet_adapter, dict) else {}
    public_rest_sidecar_bundle = read_json(PUBLIC_REST_SIDECAR_BUNDLE_JSON) or {}
    public_rest_sidecar_bundle_summary = public_rest_sidecar_bundle.get("summary", {}) if isinstance(public_rest_sidecar_bundle, dict) else {}
    public_rest_sidecar_batch = read_json(PUBLIC_REST_SIDECAR_BATCH_JSON) or {}
    public_rest_sidecar_batch_summary = public_rest_sidecar_batch.get("summary", {}) if isinstance(public_rest_sidecar_batch, dict) else {}
    sidecar_input_bundle = read_json(SIDECAR_INPUT_BUNDLE_CONTRACT_JSON) or {}
    sidecar_input_bundle_summary = sidecar_input_bundle.get("summary", {}) if isinstance(sidecar_input_bundle, dict) else {}
    sidecar_collector = read_json(SIDECAR_PACKET_COLLECTOR_JSON) or {}
    sidecar_collector_summary = sidecar_collector.get("summary", {}) if isinstance(sidecar_collector, dict) else {}
    sidecar_bundle_freeze_handoff = read_json(SIDECAR_BUNDLE_FREEZE_HANDOFF_JSON) or {}
    sidecar_bundle_freeze_handoff_summary = sidecar_bundle_freeze_handoff.get("summary", {}) if isinstance(sidecar_bundle_freeze_handoff, dict) else {}
    sidecar_bundle_batch_handoff = read_json(SIDECAR_BUNDLE_BATCH_HANDOFF_JSON) or {}
    sidecar_bundle_batch_handoff_summary = sidecar_bundle_batch_handoff.get("summary", {}) if isinstance(sidecar_bundle_batch_handoff, dict) else {}
    sidecar_bundle_batch_settlement_labels = read_json(SIDECAR_BUNDLE_BATCH_SETTLEMENT_LABELS_JSON) or {}
    sidecar_bundle_batch_settlement_labels_summary = sidecar_bundle_batch_settlement_labels.get("summary", {}) if isinstance(sidecar_bundle_batch_settlement_labels, dict) else {}
    sidecar_bundle_batch_label_join = read_json(SIDECAR_BUNDLE_BATCH_LABEL_JOIN_JSON) or {}
    sidecar_bundle_batch_label_join_summary = sidecar_bundle_batch_label_join.get("summary", {}) if isinstance(sidecar_bundle_batch_label_join, dict) else {}
    sidecar_batch_evidence_score = read_json(SIDECAR_BATCH_EVIDENCE_SCORE_JSON) or {}
    sidecar_batch_evidence_summary = sidecar_batch_evidence_score.get("summary", {}) if isinstance(sidecar_batch_evidence_score, dict) else {}
    sidecar_collection_cycle = read_json(SIDECAR_COLLECTION_CYCLE_JSON) or {}
    sidecar_collection_cycle_summary = sidecar_collection_cycle.get("summary", {}) if isinstance(sidecar_collection_cycle, dict) else {}
    freeze_handoff = read_json(FORWARD_PACKET_FREEZE_HANDOFF_JSON) or {}
    freeze_handoff_summary = freeze_handoff.get("summary", {}) if isinstance(freeze_handoff, dict) else {}
    forward_label_join = read_json(FORWARD_LABEL_JOIN_JSON) or {}
    forward_label_join_summary = forward_label_join.get("summary", {}) if isinstance(forward_label_join, dict) else {}
    forward_evidence_score = read_json(FORWARD_EVIDENCE_SCORE_JSON) or {}
    forward_evidence_summary = forward_evidence_score.get("summary", {}) if isinstance(forward_evidence_score, dict) else {}
    seed_candidates = collection_candidates(CANDIDATE_MANIFESTS_JSON)
    logged_candidates = collection_candidates(LOGGED_CANDIDATE_MANIFESTS_JSON)

    field_requirements: list[dict[str, Any]] = []
    for group, fields in field_groups.items():
        source_info = SOURCE_MAP.get(group, {})
        for field in fields:
            field_requirements.append(
                {
                    "field": field,
                    "group": group,
                    "required_before_freeze": True,
                    "source": source_info.get("source"),
                    "collector_rule": source_info.get("collector_rule"),
                }
            )

    latest_blockers = {
        "packet_contract": (packet_contract.get("summary") or {}).get("group_missing_counts", {}),
        "shadow_packets": (shadow_packets.get("summary") or {}).get("group_missing_counts", {}),
        "packet_scoring": (packet_scoring.get("summary") or {}).get("blocker_counts", {}),
        "forward_preflight": (preflight.get("summary") or {}).get("readiness_blockers", []),
        "frozen_forward": frozen_forward.get("blocker_counts", {}),
        "packet_adapter": packet_adapter_summary.get("group_missing_counts", {}),
        "public_rest_sidecar_bundle": public_rest_sidecar_bundle_summary.get("blocker_counts", {}),
        "public_rest_sidecar_batch": public_rest_sidecar_batch_summary.get("blocker_counts", {}),
        "sidecar_bundle_batch_settlement_labels": sidecar_bundle_batch_settlement_labels_summary.get("blocker_counts", {}),
        "sidecar_bundle_batch_label_join": sidecar_bundle_batch_label_join_summary.get("blocker_counts", {}),
        "sidecar_batch_evidence_score": sidecar_batch_evidence_summary.get("candidate_gates", []),
        "sidecar_collection_cycle": sidecar_collection_cycle_summary.get("blockers", []),
    }

    spec = {
        "spec_version": "v28_successor_forward_collection_spec_v1",
        "generated_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "purpose": "Handoff for collecting complete pre-resolution packet rows and frozen collection-candidate predictions for later post-lock scoring.",
        "research_only_guardrails": [
            "Do not change live order logic, strategy thresholds, secrets, live state, or processes.",
            "Do not place trades.",
            "Capture and score sidecar rows only.",
            "Settlement labels are forbidden before freeze and must be joined only after resolution.",
            "allowed_for_forward_collection is not promotion approval.",
            "allowed_for_forward_registry remains false until settled forward evidence clears promotion verifier.",
        ],
        "packet_contract": {
            "template": rel_path(PACKET_TEMPLATE_JSON),
            "field_group_count": len(field_groups),
            "field_count": len(field_requirements),
            "forbidden_before_freeze": template.get("forbidden_before_freeze", []),
        },
        "field_groups": {
            group: {
                "fields": fields,
                "source": SOURCE_MAP.get(group, {}).get("source"),
                "collector_rule": SOURCE_MAP.get(group, {}).get("collector_rule"),
                "latest_missing_count_passive": (packet_contract.get("summary") or {}).get("group_missing_counts", {}).get(group),
                "latest_missing_count_shadow": (shadow_packets.get("summary") or {}).get("group_missing_counts", {}).get(group),
            }
            for group, fields in field_groups.items()
        },
        "field_requirements": field_requirements,
        "sidecar_adapter": {
            "script": "build_v28_successor_forward_packet_adapter.py",
            "audit_json": rel_path(PACKET_ADAPTER_JSON),
            "adapter_status": packet_adapter_summary.get("adapter_status"),
            "demo_packet_ready_rows": packet_adapter_summary.get("demo_packet_ready_rows"),
            "promotion_allowed": (packet_adapter_summary.get("promotion_status") or {}).get("allowed"),
            "purpose": "Reference implementation for turning passive book checkpoints plus decision-time BTC/v28/candidate inputs into packet-contract rows before close.",
        },
        "sidecar_input_bundle_contract": {
            "script": "validate_v28_successor_sidecar_input_bundle.py",
            "audit_json": rel_path(SIDECAR_INPUT_BUNDLE_CONTRACT_JSON),
            "template_json": (sidecar_input_bundle_summary.get("outputs") or {}).get("template_json"),
            "bundle_status": sidecar_input_bundle_summary.get("bundle_status"),
            "bundle_ready": sidecar_input_bundle_summary.get("bundle_ready"),
            "promotion_allowed": sidecar_input_bundle_summary.get("promotion_allowed"),
            "purpose": "Validate the serialized market/checkpoint/BTC/v28/candidate input bundle before packet collection.",
        },
        "public_rest_sidecar_bundle": {
            "script": "build_v28_successor_public_rest_sidecar_bundle.py",
            "audit_json": rel_path(PUBLIC_REST_SIDECAR_BUNDLE_JSON),
            "mode": public_rest_sidecar_bundle_summary.get("mode"),
            "bundle_status": public_rest_sidecar_bundle_summary.get("bundle_status"),
            "bundle_ready": public_rest_sidecar_bundle_summary.get("bundle_ready"),
            "packet_rows": public_rest_sidecar_bundle_summary.get("packet_rows"),
            "promotion_allowed": public_rest_sidecar_bundle_summary.get("promotion_allowed"),
            "purpose": "Research-only one-shot builder for turning current public Kalshi market/orderbook snapshots plus BTC candles into a sidecar input bundle.",
        },
        "public_rest_sidecar_batch": {
            "script": "build_v28_successor_public_rest_sidecar_batch.py",
            "audit_json": rel_path(PUBLIC_REST_SIDECAR_BATCH_JSON),
            "mode": public_rest_sidecar_batch_summary.get("mode"),
            "batch_status": public_rest_sidecar_batch_summary.get("batch_status"),
            "markets_selected": public_rest_sidecar_batch_summary.get("markets_selected"),
            "bundle_ready_files": public_rest_sidecar_batch_summary.get("bundle_ready_files"),
            "packet_rows": public_rest_sidecar_batch_summary.get("packet_rows"),
            "packet_markets": public_rest_sidecar_batch_summary.get("packet_markets"),
            "promotion_allowed": public_rest_sidecar_batch_summary.get("promotion_allowed"),
            "purpose": "Research-only batch builder for turning active nearest-close BTC15M public markets into separate sidecar input bundles.",
        },
        "sidecar_packet_collector": {
            "script": "collect_v28_successor_forward_packets.py",
            "audit_json": rel_path(SIDECAR_PACKET_COLLECTOR_JSON),
            "collector_status": sidecar_collector_summary.get("collector_status"),
            "input_modes": sidecar_collector_summary.get("input_modes"),
            "demo_packet_ready_rows": sidecar_collector_summary.get("demo_packet_ready_rows"),
            "input_bundle_csv": (sidecar_collector_summary.get("outputs") or {}).get("input_bundle_csv"),
            "promotion_allowed": (sidecar_collector_summary.get("promotion_status") or {}).get("allowed"),
            "purpose": "Executable research-only bridge for emitting complete YES/NO candidate packet rows from an open-market checkpoint or serialized input bundle before freeze.",
        },
        "sidecar_bundle_freeze_handoff": {
            "script": "run_v28_successor_sidecar_bundle_freeze_handoff.py",
            "audit_json": rel_path(SIDECAR_BUNDLE_FREEZE_HANDOFF_JSON),
            "bundle_handoff_status": sidecar_bundle_freeze_handoff_summary.get("bundle_handoff_status"),
            "packet_rows": (sidecar_bundle_freeze_handoff_summary.get("packet_rows") or {}).get("rows"),
            "frozen_prediction_rows": (sidecar_bundle_freeze_handoff_summary.get("freeze_handoff") or {}).get("frozen_prediction_rows"),
            "registry_rows": (sidecar_bundle_freeze_handoff_summary.get("freeze_handoff") or {}).get("registry_rows"),
            "promotion_allowed": sidecar_bundle_freeze_handoff_summary.get("promotion_allowed"),
            "purpose": "One-command research handoff from sidecar input bundle to packet rows and non-promoting freeze/registry-shaped artifacts.",
        },
        "sidecar_bundle_batch_handoff": {
            "script": "run_v28_successor_sidecar_bundle_batch_handoff.py",
            "audit_json": rel_path(SIDECAR_BUNDLE_BATCH_HANDOFF_JSON),
            "batch_handoff_status": sidecar_bundle_batch_handoff_summary.get("batch_handoff_status"),
            "input_bundle_files": sidecar_bundle_batch_handoff_summary.get("input_bundle_files"),
            "packet_rows": (sidecar_bundle_batch_handoff_summary.get("packet_rows") or {}).get("rows"),
            "packet_markets": (sidecar_bundle_batch_handoff_summary.get("packet_rows") or {}).get("markets"),
            "frozen_prediction_rows": (sidecar_bundle_batch_handoff_summary.get("freeze_handoff") or {}).get("frozen_prediction_rows"),
            "registry_rows": (sidecar_bundle_batch_handoff_summary.get("freeze_handoff") or {}).get("registry_rows"),
            "promotion_allowed": sidecar_bundle_batch_handoff_summary.get("promotion_allowed"),
            "purpose": "Batch research handoff for broad-market sidecar bundle directories before label join and forward evidence scoring.",
        },
        "sidecar_bundle_batch_settlement_labels": {
            "script": "fetch_v28_successor_sidecar_batch_settlement_labels.py",
            "audit_json": rel_path(SIDECAR_BUNDLE_BATCH_SETTLEMENT_LABELS_JSON),
            "label_fetch_status": sidecar_bundle_batch_settlement_labels_summary.get("label_fetch_status"),
            "frozen_rows": sidecar_bundle_batch_settlement_labels_summary.get("frozen_rows"),
            "frozen_markets": sidecar_bundle_batch_settlement_labels_summary.get("frozen_markets"),
            "label_rows": sidecar_bundle_batch_settlement_labels_summary.get("label_rows"),
            "label_markets": sidecar_bundle_batch_settlement_labels_summary.get("label_markets"),
            "promotion_allowed": sidecar_bundle_batch_settlement_labels_summary.get("promotion_allowed"),
            "purpose": "Post-close public Kalshi settlement label fetch for sidecar batch frozen rows, written to a separate label CSV.",
        },
        "sidecar_bundle_batch_label_join": {
            "script": "run_v28_successor_sidecar_batch_label_join_handoff.py",
            "audit_json": rel_path(SIDECAR_BUNDLE_BATCH_LABEL_JOIN_JSON),
            "batch_label_join_status": sidecar_bundle_batch_label_join_summary.get("batch_label_join_status"),
            "frozen_rows": sidecar_bundle_batch_label_join_summary.get("frozen_rows"),
            "labeled_rows": sidecar_bundle_batch_label_join_summary.get("labeled_rows"),
            "joined_rows": sidecar_bundle_batch_label_join_summary.get("joined_rows"),
            "joined_markets": sidecar_bundle_batch_label_join_summary.get("joined_markets"),
            "promotion_allowed": sidecar_bundle_batch_label_join_summary.get("promotion_allowed"),
            "purpose": "Post-resolution label join for non-canonical sidecar batch frozen rows, kept separate from the promotion ledger.",
        },
        "sidecar_batch_evidence_score": {
            "script": "score_v28_successor_sidecar_batch_evidence.py",
            "audit_json": rel_path(SIDECAR_BATCH_EVIDENCE_SCORE_JSON),
            "evidence_status": sidecar_batch_evidence_summary.get("evidence_status"),
            "clean_forward_rows": sidecar_batch_evidence_summary.get("clean_forward_rows"),
            "clean_forward_markets": sidecar_batch_evidence_summary.get("clean_forward_markets"),
            "promotable_candidate_count": sidecar_batch_evidence_summary.get("promotable_candidate_count"),
            "promotion_allowed": (sidecar_batch_evidence_summary.get("promotion_status") or {}).get("allowed"),
            "purpose": "Apply probability-first evidence scoring to non-canonical sidecar batch labeled rows without granting promotion.",
        },
        "sidecar_collection_cycle": {
            "script": "run_v28_successor_sidecar_collection_cycle.py",
            "audit_json": rel_path(SIDECAR_COLLECTION_CYCLE_JSON),
            "cycle_status": sidecar_collection_cycle_summary.get("cycle_status"),
            "collect_mode": sidecar_collection_cycle_summary.get("collect_mode"),
            "sidecar_frozen_rows": sidecar_collection_cycle_summary.get("sidecar_frozen_rows"),
            "sidecar_frozen_markets": sidecar_collection_cycle_summary.get("sidecar_frozen_markets"),
            "sidecar_joined_rows": sidecar_collection_cycle_summary.get("sidecar_joined_rows"),
            "sidecar_clean_forward_rows": sidecar_collection_cycle_summary.get("sidecar_clean_forward_rows"),
            "sidecar_clean_forward_markets": sidecar_collection_cycle_summary.get("sidecar_clean_forward_markets"),
            "promotion_allowed": sidecar_collection_cycle_summary.get("promotion_allowed"),
            "purpose": "Repeatable one-cycle sidecar collector/freeze/label/score/audit runner for accumulating forward evidence without writing canonical promotion ledgers.",
        },
        "forward_packet_freeze_handoff": {
            "script": "run_v28_successor_forward_packet_freeze.py",
            "audit_json": rel_path(FORWARD_PACKET_FREEZE_HANDOFF_JSON),
            "handoff_status": freeze_handoff_summary.get("handoff_status"),
            "packet_ready_rows": (freeze_handoff_summary.get("packet_contract") or {}).get("packet_ready_rows"),
            "frozen_prediction_rows": (freeze_handoff_summary.get("freeze") or {}).get("frozen_prediction_rows"),
            "registry_rows": (freeze_handoff_summary.get("registry") or {}).get("row_count"),
            "promotion_allowed": freeze_handoff_summary.get("promotion_allowed"),
            "purpose": "One-command research handoff for validating a real sidecar packet CSV, freezing eligible rows, and materializing a registry-shaped handoff without promotion.",
        },
        "post_resolution_label_join": {
            "script": "join_v28_successor_forward_labels.py",
            "audit_json": rel_path(FORWARD_LABEL_JOIN_JSON),
            "join_status": forward_label_join_summary.get("join_status"),
            "joined_rows": forward_label_join_summary.get("joined_rows"),
            "joined_markets": forward_label_join_summary.get("joined_markets"),
            "promotion_allowed": (forward_label_join_summary.get("promotion_status") or {}).get("allowed"),
            "purpose": "Attach labels only after frozen predictions and market resolution, then compute row-level probability metrics.",
        },
        "forward_evidence_score": {
            "script": "score_v28_successor_forward_evidence.py",
            "audit_json": rel_path(FORWARD_EVIDENCE_SCORE_JSON),
            "evidence_status": forward_evidence_summary.get("evidence_status"),
            "clean_forward_rows": forward_evidence_summary.get("clean_forward_rows"),
            "clean_forward_markets": forward_evidence_summary.get("clean_forward_markets"),
            "promotable_candidate_count": forward_evidence_summary.get("promotable_candidate_count"),
            "promotion_allowed": (forward_evidence_summary.get("promotion_status") or {}).get("allowed"),
            "purpose": "Score settled frozen-forward rows candidate-vs-v28 on probability quality before economics or promotion.",
        },
        "collection_candidates": {
            "seed_manifest_path": rel_path(CANDIDATE_MANIFESTS_JSON),
            "seed_collection_candidates": seed_candidates,
            "logged_manifest_path": rel_path(LOGGED_CANDIDATE_MANIFESTS_JSON),
            "logged_collection_candidates": logged_candidates,
            "recommended_manifest": "logged_events_diagnostic",
            "recommended_candidates": logged_candidates,
        },
        "freeze_acceptance_gates": [
            "row is written before market_close_ts_utc",
            "all packet contract groups are complete",
            "row has no temporal blockers",
            "candidate prediction comes from allowed_for_forward_collection manifest and frozen model_hash",
            "settlement fields are absent before freeze",
            "frozen prediction ledger is written before resolution",
        ],
        "promotion_acceptance_gates": [
            "settled labels joined only after freeze and resolution",
            "source contract reports promotion-grade forward rows",
            "chronological holdout and post-lock forward rows beat v28 on Brier/log loss/calibration",
            "near-boundary and recross slices improve or do not degrade",
            "broad market coverage floor is met",
            "promotion verifier reports promotable",
        ],
        "latest_blockers": latest_blockers,
        "inputs": {
            "packet_template_json": rel_path(PACKET_TEMPLATE_JSON),
            "packet_template_hash": sha256_file(PACKET_TEMPLATE_JSON),
            "candidate_manifests_json": rel_path(CANDIDATE_MANIFESTS_JSON),
            "candidate_manifests_hash": sha256_file(CANDIDATE_MANIFESTS_JSON),
            "logged_candidate_manifests_json": rel_path(LOGGED_CANDIDATE_MANIFESTS_JSON),
            "logged_candidate_manifests_hash": sha256_file(LOGGED_CANDIDATE_MANIFESTS_JSON),
            "packet_contract_json": rel_path(PACKET_CONTRACT_JSON),
            "shadow_packet_json": rel_path(SHADOW_PACKET_JSON),
            "packet_scoring_json": rel_path(PACKET_SCORING_JSON),
            "forward_preflight_json": rel_path(FORWARD_PREFLIGHT_JSON),
            "frozen_forward_json": rel_path(FROZEN_FORWARD_JSON),
            "packet_adapter_json": rel_path(PACKET_ADAPTER_JSON),
            "packet_adapter_hash": sha256_file(PACKET_ADAPTER_JSON),
            "public_rest_sidecar_bundle_json": rel_path(PUBLIC_REST_SIDECAR_BUNDLE_JSON),
            "public_rest_sidecar_bundle_hash": sha256_file(PUBLIC_REST_SIDECAR_BUNDLE_JSON),
            "public_rest_sidecar_batch_json": rel_path(PUBLIC_REST_SIDECAR_BATCH_JSON),
            "public_rest_sidecar_batch_hash": sha256_file(PUBLIC_REST_SIDECAR_BATCH_JSON),
            "sidecar_input_bundle_contract_json": rel_path(SIDECAR_INPUT_BUNDLE_CONTRACT_JSON),
            "sidecar_input_bundle_contract_hash": sha256_file(SIDECAR_INPUT_BUNDLE_CONTRACT_JSON),
            "sidecar_packet_collector_json": rel_path(SIDECAR_PACKET_COLLECTOR_JSON),
            "sidecar_packet_collector_hash": sha256_file(SIDECAR_PACKET_COLLECTOR_JSON),
            "sidecar_bundle_freeze_handoff_json": rel_path(SIDECAR_BUNDLE_FREEZE_HANDOFF_JSON),
            "sidecar_bundle_freeze_handoff_hash": sha256_file(SIDECAR_BUNDLE_FREEZE_HANDOFF_JSON),
            "sidecar_bundle_batch_handoff_json": rel_path(SIDECAR_BUNDLE_BATCH_HANDOFF_JSON),
            "sidecar_bundle_batch_handoff_hash": sha256_file(SIDECAR_BUNDLE_BATCH_HANDOFF_JSON),
            "sidecar_bundle_batch_settlement_labels_json": rel_path(SIDECAR_BUNDLE_BATCH_SETTLEMENT_LABELS_JSON),
            "sidecar_bundle_batch_settlement_labels_hash": sha256_file(SIDECAR_BUNDLE_BATCH_SETTLEMENT_LABELS_JSON),
            "sidecar_bundle_batch_label_join_json": rel_path(SIDECAR_BUNDLE_BATCH_LABEL_JOIN_JSON),
            "sidecar_bundle_batch_label_join_hash": sha256_file(SIDECAR_BUNDLE_BATCH_LABEL_JOIN_JSON),
            "sidecar_batch_evidence_score_json": rel_path(SIDECAR_BATCH_EVIDENCE_SCORE_JSON),
            "sidecar_batch_evidence_score_hash": sha256_file(SIDECAR_BATCH_EVIDENCE_SCORE_JSON),
            "sidecar_collection_cycle_json": rel_path(SIDECAR_COLLECTION_CYCLE_JSON),
            "sidecar_collection_cycle_hash": sha256_file(SIDECAR_COLLECTION_CYCLE_JSON),
            "forward_packet_freeze_handoff_json": rel_path(FORWARD_PACKET_FREEZE_HANDOFF_JSON),
            "forward_packet_freeze_handoff_hash": sha256_file(FORWARD_PACKET_FREEZE_HANDOFF_JSON),
            "forward_label_join_json": rel_path(FORWARD_LABEL_JOIN_JSON),
            "forward_label_join_hash": sha256_file(FORWARD_LABEL_JOIN_JSON),
            "forward_evidence_score_json": rel_path(FORWARD_EVIDENCE_SCORE_JSON),
            "forward_evidence_score_hash": sha256_file(FORWARD_EVIDENCE_SCORE_JSON),
        },
        "outputs": {
            "spec_json": rel_path(SPEC_JSON),
            "audit_json": rel_path(SPEC_AUDIT_JSON),
            "markdown": rel_path(SPEC_MD),
        },
    }
    summary = {
        "generated_utc": spec["generated_utc"],
        "builder_script": Path(__file__).name,
        "spec_version": spec["spec_version"],
        "field_count": len(field_requirements),
        "field_group_count": len(field_groups),
        "seed_collection_candidate_count": len(seed_candidates),
        "logged_collection_candidate_count": len(logged_candidates),
        "recommended_candidate_count": len(logged_candidates),
        "passive_packet_ready_rows": (packet_contract.get("summary") or {}).get("packet_ready_rows"),
        "shadow_packet_ready_rows": (shadow_packets.get("summary") or {}).get("packet_ready_rows"),
        "packet_scoring_freeze_eligible_rows": (packet_scoring.get("summary") or {}).get("freeze_eligible_prediction_rows"),
        "frozen_prediction_rows": frozen_forward.get("frozen_prediction_rows"),
        "adapter_status": packet_adapter_summary.get("adapter_status"),
        "adapter_demo_packet_ready_rows": packet_adapter_summary.get("demo_packet_ready_rows"),
        "public_rest_sidecar_bundle_status": public_rest_sidecar_bundle_summary.get("bundle_status"),
        "public_rest_sidecar_bundle_ready": public_rest_sidecar_bundle_summary.get("bundle_ready"),
        "public_rest_sidecar_bundle_packet_rows": public_rest_sidecar_bundle_summary.get("packet_rows"),
        "public_rest_sidecar_batch_status": public_rest_sidecar_batch_summary.get("batch_status"),
        "public_rest_sidecar_batch_markets_selected": public_rest_sidecar_batch_summary.get("markets_selected"),
        "public_rest_sidecar_batch_packet_rows": public_rest_sidecar_batch_summary.get("packet_rows"),
        "sidecar_input_bundle_status": sidecar_input_bundle_summary.get("bundle_status"),
        "sidecar_input_bundle_ready": sidecar_input_bundle_summary.get("bundle_ready"),
        "sidecar_collector_status": sidecar_collector_summary.get("collector_status"),
        "sidecar_collector_demo_packet_ready_rows": sidecar_collector_summary.get("demo_packet_ready_rows"),
        "sidecar_bundle_freeze_handoff_status": sidecar_bundle_freeze_handoff_summary.get("bundle_handoff_status"),
        "sidecar_bundle_freeze_handoff_frozen_rows": (sidecar_bundle_freeze_handoff_summary.get("freeze_handoff") or {}).get("frozen_prediction_rows"),
        "sidecar_bundle_batch_handoff_status": sidecar_bundle_batch_handoff_summary.get("batch_handoff_status"),
        "sidecar_bundle_batch_input_files": sidecar_bundle_batch_handoff_summary.get("input_bundle_files"),
        "sidecar_bundle_batch_frozen_rows": (sidecar_bundle_batch_handoff_summary.get("freeze_handoff") or {}).get("frozen_prediction_rows"),
        "sidecar_bundle_batch_label_fetch_status": sidecar_bundle_batch_settlement_labels_summary.get("label_fetch_status"),
        "sidecar_bundle_batch_label_rows": sidecar_bundle_batch_settlement_labels_summary.get("label_rows"),
        "sidecar_bundle_batch_label_markets": sidecar_bundle_batch_settlement_labels_summary.get("label_markets"),
        "sidecar_bundle_batch_label_join_status": sidecar_bundle_batch_label_join_summary.get("batch_label_join_status"),
        "sidecar_bundle_batch_labeled_rows": sidecar_bundle_batch_label_join_summary.get("labeled_rows"),
        "sidecar_bundle_batch_joined_rows": sidecar_bundle_batch_label_join_summary.get("joined_rows"),
        "sidecar_batch_evidence_status": sidecar_batch_evidence_summary.get("evidence_status"),
        "sidecar_batch_evidence_clean_rows": sidecar_batch_evidence_summary.get("clean_forward_rows"),
        "sidecar_batch_evidence_clean_markets": sidecar_batch_evidence_summary.get("clean_forward_markets"),
        "sidecar_collection_cycle_status": sidecar_collection_cycle_summary.get("cycle_status"),
        "sidecar_collection_cycle_clean_rows": sidecar_collection_cycle_summary.get("sidecar_clean_forward_rows"),
        "sidecar_collection_cycle_clean_markets": sidecar_collection_cycle_summary.get("sidecar_clean_forward_markets"),
        "freeze_handoff_status": freeze_handoff_summary.get("handoff_status"),
        "freeze_handoff_frozen_prediction_rows": (freeze_handoff_summary.get("freeze") or {}).get("frozen_prediction_rows"),
        "freeze_handoff_registry_rows": (freeze_handoff_summary.get("registry") or {}).get("row_count"),
        "label_join_status": forward_label_join_summary.get("join_status"),
        "label_joined_rows": forward_label_join_summary.get("joined_rows"),
        "forward_evidence_status": forward_evidence_summary.get("evidence_status"),
        "forward_evidence_clean_rows": forward_evidence_summary.get("clean_forward_rows"),
        "status": "ready_for_future_collection_not_promotion",
        "outputs": spec["outputs"],
    }
    return spec, summary


def write_markdown(spec: dict[str, Any], summary: dict[str, Any], path: Path) -> None:
    lines = [
        "# v28 Successor Forward Collection Spec",
        "",
        "Research-only handoff for collecting complete future forward packets. This report does not touch live bot state, orders, thresholds, secrets, or processes.",
        "",
        "## Summary",
        "",
        f"- Generated UTC: `{summary['generated_utc']}`",
        f"- Spec version: `{summary['spec_version']}`",
        f"- Required fields: `{summary['field_count']}` across `{summary['field_group_count']}` groups",
        f"- Recommended collection candidates: `{summary['recommended_candidate_count']}`",
        f"- Passive packet-ready rows now: `{summary['passive_packet_ready_rows']}`",
        f"- Shadow packet-ready rows now: `{summary['shadow_packet_ready_rows']}`",
        f"- Freeze-eligible scored packet predictions now: `{summary['packet_scoring_freeze_eligible_rows']}`",
        f"- Frozen prediction rows now: `{summary['frozen_prediction_rows']}`",
        f"- Sidecar adapter status: `{summary['adapter_status']}`",
        f"- Sidecar adapter demo packet-ready rows: `{summary['adapter_demo_packet_ready_rows']}`",
        f"- Public REST sidecar bundle status: `{summary['public_rest_sidecar_bundle_status']}`",
        f"- Public REST sidecar bundle ready: `{summary['public_rest_sidecar_bundle_ready']}`",
        f"- Public REST sidecar bundle packet rows: `{summary['public_rest_sidecar_bundle_packet_rows']}`",
        f"- Public REST sidecar batch status: `{summary['public_rest_sidecar_batch_status']}`",
        f"- Public REST sidecar batch markets selected: `{summary['public_rest_sidecar_batch_markets_selected']}`",
        f"- Public REST sidecar batch packet rows: `{summary['public_rest_sidecar_batch_packet_rows']}`",
        f"- Sidecar input bundle status: `{summary['sidecar_input_bundle_status']}`",
        f"- Sidecar input bundle ready: `{summary['sidecar_input_bundle_ready']}`",
        f"- Sidecar collector status: `{summary['sidecar_collector_status']}`",
        f"- Sidecar collector demo packet-ready rows: `{summary['sidecar_collector_demo_packet_ready_rows']}`",
        f"- Sidecar bundle freeze handoff status: `{summary['sidecar_bundle_freeze_handoff_status']}`",
        f"- Sidecar bundle freeze handoff frozen rows: `{summary['sidecar_bundle_freeze_handoff_frozen_rows']}`",
        f"- Sidecar bundle batch handoff status: `{summary['sidecar_bundle_batch_handoff_status']}`",
        f"- Sidecar bundle batch input files: `{summary['sidecar_bundle_batch_input_files']}`",
        f"- Sidecar bundle batch frozen rows: `{summary['sidecar_bundle_batch_frozen_rows']}`",
        f"- Sidecar bundle batch label fetch status: `{summary['sidecar_bundle_batch_label_fetch_status']}`",
        f"- Sidecar bundle batch label rows: `{summary['sidecar_bundle_batch_label_rows']}`",
        f"- Sidecar bundle batch label markets: `{summary['sidecar_bundle_batch_label_markets']}`",
        f"- Sidecar bundle batch label join status: `{summary['sidecar_bundle_batch_label_join_status']}`",
        f"- Sidecar bundle batch labeled rows: `{summary['sidecar_bundle_batch_labeled_rows']}`",
        f"- Sidecar bundle batch joined rows: `{summary['sidecar_bundle_batch_joined_rows']}`",
        f"- Sidecar batch evidence score status: `{summary['sidecar_batch_evidence_status']}`",
        f"- Sidecar batch evidence clean rows: `{summary['sidecar_batch_evidence_clean_rows']}`",
        f"- Sidecar batch evidence clean markets: `{summary['sidecar_batch_evidence_clean_markets']}`",
        f"- Sidecar collection cycle status: `{summary['sidecar_collection_cycle_status']}`",
        f"- Sidecar collection cycle clean rows: `{summary['sidecar_collection_cycle_clean_rows']}`",
        f"- Sidecar collection cycle clean markets: `{summary['sidecar_collection_cycle_clean_markets']}`",
        f"- Freeze handoff status: `{summary['freeze_handoff_status']}`",
        f"- Freeze handoff frozen prediction rows: `{summary['freeze_handoff_frozen_prediction_rows']}`",
        f"- Freeze handoff registry rows: `{summary['freeze_handoff_registry_rows']}`",
        f"- Forward label join status: `{summary['label_join_status']}`",
        f"- Forward joined label rows now: `{summary['label_joined_rows']}`",
        f"- Forward evidence score status: `{summary['forward_evidence_status']}`",
        f"- Forward evidence clean rows now: `{summary['forward_evidence_clean_rows']}`",
        "",
        "## Field Groups",
        "",
        "| group | fields | source | current passive missing | current shadow missing |",
        "|---|---:|---|---:|---:|",
    ]
    for group, info in spec["field_groups"].items():
        lines.append(
            f"| `{group}` | {len(info['fields'])} | {info['source']} | {info['latest_missing_count_passive']} | {info['latest_missing_count_shadow']} |"
        )
    lines.extend(["", "## Collection Candidates", "", "| candidate | model type | track | model hash | promotion registry allowed |", "|---|---|---|---|---:|"])
    for candidate in spec["collection_candidates"]["recommended_candidates"]:
        lines.append(
            f"| `{candidate['candidate_id']}` | `{candidate['model_type']}` | `{candidate['model_track']}` | `{candidate['model_hash']}` | {candidate['allowed_for_forward_registry']} |"
        )
    lines.extend(["", "## Freeze Acceptance Gates", ""])
    for gate in spec["freeze_acceptance_gates"]:
        lines.append(f"- {gate}")
    lines.extend(["", "## Promotion Acceptance Gates", ""])
    for gate in spec["promotion_acceptance_gates"]:
        lines.append(f"- {gate}")
    lines.extend(["", "## Latest Blockers", ""])
    for name, blockers in spec["latest_blockers"].items():
        lines.append(f"- `{name}`: `{blockers}`")
    lines.extend(
        [
            "",
            "## Read",
            "",
            "- This spec is the exact collection handoff for the next passive forward run.",
            "- It separates forward collection from promotion: collection candidates can be recorded prospectively, but registry promotion remains closed.",
            "- The shortest path to freeze-ready rows is to capture BTC history and native v28 component fields at decision time, then score the listed candidates before close.",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_outputs(spec: dict[str, Any], summary: dict[str, Any]) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    EDGE_DIR.mkdir(parents=True, exist_ok=True)
    SPEC_JSON.write_text(json.dumps(spec, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    SPEC_AUDIT_JSON.write_text(json.dumps({"summary": summary, "spec": spec}, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_markdown(spec, summary, SPEC_MD)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    spec, summary = build()
    if args.write and not args.dry_run:
        write_outputs(spec, summary)
    print(
        json.dumps(
            {
                "field_count": summary["field_count"],
                "field_group_count": summary["field_group_count"],
                "recommended_candidate_count": summary["recommended_candidate_count"],
                "passive_packet_ready_rows": summary["passive_packet_ready_rows"],
                "shadow_packet_ready_rows": summary["shadow_packet_ready_rows"],
                "packet_scoring_freeze_eligible_rows": summary["packet_scoring_freeze_eligible_rows"],
                "status": summary["status"],
                "written": bool(args.write and not args.dry_run),
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
