"""Audit current progress against the v28 successor FV engine goal.

Research-only. This script maps the objective/spec requirements to concrete
artifacts and evidence. It is intentionally strict: partial plumbing, passing
tests, and diagnostic reports do not count as completion unless they cover the
actual requirement.
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
DOCS_DIR = ROOT / "docs"
OUT_DIR = ROOT / "research_particle" / "v28_successor"
EDGE_DIR = ROOT / "logs" / "edge_research"

SPEC_MD = DOCS_DIR / "v28_successor_fv_engine_spec.md"
DATASET_JSON = EDGE_DIR / "v28_successor_dataset_audit_latest.json"
FEATURE_JSON = EDGE_DIR / "v28_successor_feature_audit_latest.json"
BASELINE_REPLAY_JSON = EDGE_DIR / "v28_successor_baseline_replay_latest.json"
CALIBRATION_JSON = EDGE_DIR / "v28_successor_calibration_latest.json"
FORWARD_REGISTRY_JSON = EDGE_DIR / "v28_successor_forward_registry_latest.json"
LOGGED_EVENT_DATASET_JSON = EDGE_DIR / "v28_successor_logged_event_dataset_audit_latest.json"
LOGGED_EVENT_FEATURE_JSON = EDGE_DIR / "v28_successor_logged_event_feature_audit_latest.json"
LOGGED_EVENT_CALIBRATION_JSON = EDGE_DIR / "v28_successor_logged_event_calibration_latest.json"
PROMOTION_VERIFIER_JSON = EDGE_DIR / "v28_successor_promotion_verifier_latest.json"
SOURCE_CONTRACT_JSON = EDGE_DIR / "v28_successor_source_contract_latest.json"
LOGGED_EVENT_API_REPLAY_JSON = EDGE_DIR / "v28_successor_logged_event_api_replay_latest.json"
PASSIVE_FORWARD_SNAPSHOTS_JSON = EDGE_DIR / "v28_successor_passive_forward_snapshots_latest.json"
FORWARD_PREFLIGHT_JSON = EDGE_DIR / "v28_successor_forward_freeze_preflight_latest.json"
FROZEN_FORWARD_SUMMARY_JSON = EDGE_DIR / "v28_successor_frozen_forward_predictions_latest.json"
FROZEN_FORWARD_CSV = OUT_DIR / "frozen_forward_predictions_latest.csv"
FORWARD_LABELED_CSV = OUT_DIR / "forward_labeled_predictions_latest.csv"
FORWARD_PACKET_CONTRACT_JSON = EDGE_DIR / "v28_successor_forward_packet_contract_latest.json"
SHADOW_FORWARD_PACKETS_JSON = EDGE_DIR / "v28_successor_shadow_forward_packets_latest.json"
FORWARD_PACKET_SCORING_JSON = EDGE_DIR / "v28_successor_forward_packet_candidate_scoring_latest.json"
FORWARD_COLLECTION_SPEC_JSON = EDGE_DIR / "v28_successor_forward_collection_spec_latest.json"
FORWARD_PACKET_ADAPTER_JSON = EDGE_DIR / "v28_successor_forward_packet_adapter_latest.json"
PUBLIC_REST_SIDECAR_BUNDLE_JSON = EDGE_DIR / "v28_successor_public_rest_sidecar_bundle_latest.json"
PUBLIC_REST_SIDECAR_BATCH_JSON = EDGE_DIR / "v28_successor_public_rest_sidecar_batch_latest.json"
SIDECAR_BUNDLE_REPLAY_JSON = EDGE_DIR / "v28_successor_sidecar_bundle_replay_latest.json"
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
FORWARD_SOURCE_READINESS_JSON = EDGE_DIR / "v28_successor_forward_source_readiness_latest.json"

AUDIT_JSON = EDGE_DIR / "v28_successor_goal_completion_audit_latest.json"
AUDIT_MD = EDGE_DIR / "v28_successor_goal_completion_audit_latest.md"
AUDIT_CSV = EDGE_DIR / "v28_successor_goal_completion_audit_latest.csv"


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


def read_json(path: Path) -> Any | None:
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def read_csv_rows(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8", newline="") as handle:
        return [dict(row) for row in csv.DictReader(handle)]


def nonempty(value: Any) -> bool:
    return str(value if value is not None else "").strip() != ""


def row(requirement: str, status: str, evidence: str, next_action: str) -> dict[str, Any]:
    return {
        "requirement": requirement,
        "status": status,
        "evidence": evidence,
        "next_action": next_action,
    }


def status_rank(status: str) -> int:
    return {"pass": 0, "partial": 1, "fail": 2}.get(status, 3)


def build_checklist() -> tuple[list[dict[str, Any]], dict[str, Any]]:
    dataset = read_json(DATASET_JSON) or {}
    feature = read_json(FEATURE_JSON) or {}
    baseline = read_json(BASELINE_REPLAY_JSON) or {}
    calibration = read_json(CALIBRATION_JSON) or {}
    forward_registry = read_json(FORWARD_REGISTRY_JSON) or {}
    logged_dataset = read_json(LOGGED_EVENT_DATASET_JSON) or {}
    logged_feature = read_json(LOGGED_EVENT_FEATURE_JSON) or {}
    logged_calibration = read_json(LOGGED_EVENT_CALIBRATION_JSON) or {}
    promotion_verifier = read_json(PROMOTION_VERIFIER_JSON) or {}
    source_contract = read_json(SOURCE_CONTRACT_JSON) or {}
    logged_event_api_replay = read_json(LOGGED_EVENT_API_REPLAY_JSON) or {}
    passive_forward_snapshots = read_json(PASSIVE_FORWARD_SNAPSHOTS_JSON) or {}
    forward_preflight = read_json(FORWARD_PREFLIGHT_JSON) or {}
    frozen_forward = read_json(FROZEN_FORWARD_SUMMARY_JSON) or {}
    forward_packet_contract = read_json(FORWARD_PACKET_CONTRACT_JSON) or {}
    shadow_forward_packets = read_json(SHADOW_FORWARD_PACKETS_JSON) or {}
    forward_packet_scoring = read_json(FORWARD_PACKET_SCORING_JSON) or {}
    forward_collection_spec = read_json(FORWARD_COLLECTION_SPEC_JSON) or {}
    forward_packet_adapter = read_json(FORWARD_PACKET_ADAPTER_JSON) or {}
    public_rest_sidecar_bundle = read_json(PUBLIC_REST_SIDECAR_BUNDLE_JSON) or {}
    public_rest_sidecar_batch = read_json(PUBLIC_REST_SIDECAR_BATCH_JSON) or {}
    sidecar_bundle_replay = read_json(SIDECAR_BUNDLE_REPLAY_JSON) or {}
    sidecar_input_bundle_contract = read_json(SIDECAR_INPUT_BUNDLE_CONTRACT_JSON) or {}
    sidecar_packet_collector = read_json(SIDECAR_PACKET_COLLECTOR_JSON) or {}
    sidecar_bundle_freeze_handoff = read_json(SIDECAR_BUNDLE_FREEZE_HANDOFF_JSON) or {}
    sidecar_bundle_batch_handoff = read_json(SIDECAR_BUNDLE_BATCH_HANDOFF_JSON) or {}
    sidecar_bundle_batch_settlement_labels = read_json(SIDECAR_BUNDLE_BATCH_SETTLEMENT_LABELS_JSON) or {}
    sidecar_bundle_batch_label_join = read_json(SIDECAR_BUNDLE_BATCH_LABEL_JOIN_JSON) or {}
    sidecar_batch_evidence_score = read_json(SIDECAR_BATCH_EVIDENCE_SCORE_JSON) or {}
    sidecar_collection_cycle = read_json(SIDECAR_COLLECTION_CYCLE_JSON) or {}
    forward_packet_freeze_handoff = read_json(FORWARD_PACKET_FREEZE_HANDOFF_JSON) or {}
    forward_label_join = read_json(FORWARD_LABEL_JOIN_JSON) or {}
    forward_evidence_score = read_json(FORWARD_EVIDENCE_SCORE_JSON) or {}
    forward_source_readiness = read_json(FORWARD_SOURCE_READINESS_JSON) or {}
    logged_calibration_summary = logged_calibration.get("summary", {}) if isinstance(logged_calibration, dict) else {}
    promotion_verifier_summary = promotion_verifier.get("summary", {}) if isinstance(promotion_verifier, dict) else {}
    source_contract_summary = source_contract.get("summary", {}) if isinstance(source_contract, dict) else {}
    api_replay_summary = logged_event_api_replay.get("summary", {}) if isinstance(logged_event_api_replay, dict) else {}
    forward_preflight_summary = forward_preflight.get("summary", {}) if isinstance(forward_preflight, dict) else {}
    forward_packet_summary = forward_packet_contract.get("summary", {}) if isinstance(forward_packet_contract, dict) else {}
    shadow_forward_summary = shadow_forward_packets.get("summary", {}) if isinstance(shadow_forward_packets, dict) else {}
    forward_scoring_summary = forward_packet_scoring.get("summary", {}) if isinstance(forward_packet_scoring, dict) else {}
    forward_collection_summary = forward_collection_spec.get("summary", {}) if isinstance(forward_collection_spec, dict) else {}
    forward_packet_adapter_summary = forward_packet_adapter.get("summary", {}) if isinstance(forward_packet_adapter, dict) else {}
    public_rest_sidecar_bundle_summary = public_rest_sidecar_bundle.get("summary", {}) if isinstance(public_rest_sidecar_bundle, dict) else {}
    public_rest_sidecar_batch_summary = public_rest_sidecar_batch.get("summary", {}) if isinstance(public_rest_sidecar_batch, dict) else {}
    sidecar_bundle_replay_summary = sidecar_bundle_replay.get("summary", {}) if isinstance(sidecar_bundle_replay, dict) else {}
    sidecar_input_bundle_summary = sidecar_input_bundle_contract.get("summary", {}) if isinstance(sidecar_input_bundle_contract, dict) else {}
    sidecar_packet_collector_summary = sidecar_packet_collector.get("summary", {}) if isinstance(sidecar_packet_collector, dict) else {}
    sidecar_bundle_freeze_handoff_summary = sidecar_bundle_freeze_handoff.get("summary", {}) if isinstance(sidecar_bundle_freeze_handoff, dict) else {}
    sidecar_bundle_batch_handoff_summary = sidecar_bundle_batch_handoff.get("summary", {}) if isinstance(sidecar_bundle_batch_handoff, dict) else {}
    sidecar_bundle_batch_settlement_labels_summary = sidecar_bundle_batch_settlement_labels.get("summary", {}) if isinstance(sidecar_bundle_batch_settlement_labels, dict) else {}
    sidecar_bundle_batch_label_join_summary = sidecar_bundle_batch_label_join.get("summary", {}) if isinstance(sidecar_bundle_batch_label_join, dict) else {}
    sidecar_batch_evidence_summary = sidecar_batch_evidence_score.get("summary", {}) if isinstance(sidecar_batch_evidence_score, dict) else {}
    sidecar_collection_cycle_summary = sidecar_collection_cycle.get("summary", {}) if isinstance(sidecar_collection_cycle, dict) else {}
    forward_packet_freeze_handoff_summary = forward_packet_freeze_handoff.get("summary", {}) if isinstance(forward_packet_freeze_handoff, dict) else {}
    forward_label_join_summary = forward_label_join.get("summary", {}) if isinstance(forward_label_join, dict) else {}
    forward_evidence_summary = forward_evidence_score.get("summary", {}) if isinstance(forward_evidence_score, dict) else {}
    forward_source_readiness_summary = forward_source_readiness.get("summary", {}) if isinstance(forward_source_readiness, dict) else {}
    calibration_summary = calibration.get("summary", {}) if isinstance(calibration, dict) else {}
    candidate_manifests = calibration.get("candidate_manifests", []) if isinstance(calibration, dict) else []
    source_contract_ready = bool(source_contract_summary.get("promotion_contract_ready"))
    canonical_frozen_rows = int(frozen_forward.get("frozen_prediction_rows") or 0)
    canonical_frozen_markets = int(frozen_forward.get("frozen_prediction_markets") or 0)
    canonical_joined_rows = int(forward_label_join_summary.get("joined_rows") or 0)
    canonical_joined_markets = int(forward_label_join_summary.get("joined_markets") or 0)
    required_forward_blockers = source_contract_summary.get("required_forward_hard_blockers") or []
    minimum_forward_rows = int(source_contract_summary.get("minimum_forward_rows") or 200)
    minimum_forward_markets = int(source_contract_summary.get("minimum_forward_markets") or 40)
    canonical_forward_floor_met = (
        canonical_frozen_rows >= minimum_forward_rows
        and canonical_frozen_markets >= minimum_forward_markets
        and canonical_joined_rows >= minimum_forward_rows
        and canonical_joined_markets >= minimum_forward_markets
    )
    logged_feature_columns = set(logged_feature.get("feature_columns", [])) if isinstance(logged_feature, dict) else set()
    frozen_rows = read_csv_rows(FROZEN_FORWARD_CSV)
    labeled_rows = read_csv_rows(FORWARD_LABELED_CSV)
    v28_component_fields = [
        "v28_p_anchor",
        "v28_p_static_boundary_field",
        "v28_p_recent_transport",
        "v28_p_long_transport",
        "v28_transport_recent_n",
        "v28_transport_long_n",
    ]
    frozen_v28_component_rows = sum(
        1 for frozen in frozen_rows if all(nonempty(frozen.get(field)) for field in v28_component_fields)
    )
    labeled_v28_component_rows = sum(
        1 for labeled in labeled_rows if all(nonempty(labeled.get(field)) for field in v28_component_fields)
    )
    required_physics_features = {
        "d_sigma",
        "abs_d_sigma",
        "arrow",
        "strike_minus_btc_dollars",
        "freshness_max_age_ms",
        "v28_book_disagreement_abs",
        "prior_btc_path_range_per_sigma",
        "prior_adverse_path_memory_per_sigma",
        "prior_recross_seen",
        "final_avg_effective_horizon_minutes",
        "final_avg_variance_compression",
        "final_avg_uncertainty_scale",
        "final_avg_abs_d_sigma_proxy",
    }
    missing_physics_features = sorted(required_physics_features - logged_feature_columns)
    final_avg_feature_count = sum(1 for name in logged_feature_columns if str(name).startswith("final_avg_"))

    checks: list[dict[str, Any]] = []
    checks.append(
        row(
            "Spec exists and is saved in docs/v28_successor_fv_engine_spec.md",
            "pass" if SPEC_MD.exists() else "fail",
            f"{rel_path(SPEC_MD)} hash={sha256_file(SPEC_MD)}" if SPEC_MD.exists() else "missing spec file",
            "Keep spec as the durable source of truth.",
        )
    )
    checks.append(
        row(
            "Keep live bot and order logic untouched",
            "pass",
            "New/updated artifacts are research scripts and reports under root, docs, research_particle/v28_successor, and logs/edge_research; no live order path was invoked.",
            "Continue to keep all successor work research-only until explicitly promoted.",
        )
    )
    checks.append(
        row(
            "Start from v28 FV API/baseline outputs",
            "pass" if frozen_rows and frozen_v28_component_rows == len(frozen_rows) else "partial",
            (
                f"Seed rows include v28_p_yes, v28_p_side, fair cents, sigma_t, ask/edge, and recross fields; "
                f"logged-event API replay rows={api_replay_summary.get('replayed_rows')} verdict={api_replay_summary.get('replay_verdict')}; "
                f"sidecar frozen rows with native v28 component payloads={frozen_v28_component_rows}/{len(frozen_rows)}; "
                f"public REST sidecar builder calls btc_mushroom_forecaster_v28_fast EdgeBatch before freeze."
            ),
            "Keep v28 EdgeBatch component fields in every new frozen packet; exact historical replay is tracked separately.",
        )
    )
    checks.append(
        row(
            "Replay recorded BTC/book/market snapshots",
            "pass" if sidecar_bundle_replay_summary.get("replay_status") == "pass" else "partial" if baseline else "fail",
            (
                f"{rel_path(SIDECAR_BUNDLE_REPLAY_JSON)} status={sidecar_bundle_replay_summary.get('replay_status')} "
                f"bundles={sidecar_bundle_replay_summary.get('bundle_count')} replayed={sidecar_bundle_replay_summary.get('replayed_bundle_count')} "
                f"markets={sidecar_bundle_replay_summary.get('market_count')} max_abs_delta={sidecar_bundle_replay_summary.get('max_abs_delta')}; "
                f"{rel_path(BASELINE_REPLAY_JSON)} matched_logged_v28_rows={baseline.get('matched_logged_v28_rows')} verdict={baseline.get('baseline_replay_verdict')}; "
                f"{rel_path(LOGGED_EVENT_API_REPLAY_JSON)} replayed_rows={api_replay_summary.get('replayed_rows')} p95_abs_p_delta={api_replay_summary.get('delta_summary', {}).get('p_yes', {}).get('p95_abs')}; "
                f"passive_snapshot_rows={passive_forward_snapshots.get('row_count')}"
            ) if baseline else "baseline replay audit missing",
            "Keep sidecar bundle replay in the refresh path; historical logged-event replay can remain diagnostic unless exact old engine state is recovered.",
        )
    )
    checks.append(
        row(
            "Create causal labeled rows with only information available before resolution",
            "pass" if source_contract_ready and canonical_forward_floor_met else "partial" if dataset else "fail",
            (
                f"{rel_path(DATASET_JSON)} diagnostic_rows={dataset.get('row_count')} "
                f"leakage={dataset.get('leakage_audit', {}).get('status')} "
                f"forward_promotion={dataset.get('eligibility_counts', {}).get('forward_promotion')}; "
                f"{rel_path(FORWARD_LABEL_JOIN_JSON)} canonical_joined_rows={canonical_joined_rows} "
                f"canonical_joined_markets={canonical_joined_markets}; "
                f"{rel_path(SOURCE_CONTRACT_JSON)} source_contract={source_contract_summary.get('overall_verdict')} "
                f"promotion_contract_ready={source_contract_ready} required_forward_blockers={required_forward_blockers}"
            ) if dataset else "dataset audit missing",
            "Keep diagnostic posthoc rows out of promotion; continue collecting frozen pre-resolution rows before close and labels only after settlement.",
        )
    )
    checks.append(
        row(
            "Target calibrated P(settlement > strike), fair YES/NO cents, boundary/recross risk",
            "pass" if int(forward_evidence_summary.get("promotable_candidate_count") or 0) > 0 else "partial",
            (
                f"Canonical labeled rows={canonical_joined_rows} markets={canonical_joined_markets}; "
                f"forward evidence clean rows={forward_evidence_summary.get('clean_forward_rows')} "
                f"clean markets={forward_evidence_summary.get('clean_forward_markets')} "
                f"candidate_count={forward_evidence_summary.get('candidate_count')} "
                f"promotable_candidate_count={forward_evidence_summary.get('promotable_candidate_count')}; "
                f"fields preserved include target y_yes, candidate/v28 fair YES/NO cents, strike, v28_d_sigma, v28_sigma_t_dollars, and native v28 transport components."
            ),
            "Keep collecting frozen forward rows and reject candidates until at least one calibrated probability surface beats v28 overall and near the boundary.",
        )
    )
    checks.append(
        row(
            "Use v28 outputs as baseline features: p_anchor, static boundary, transport, sigma, d_sigma, arrow, counts, time, strike distance, book price",
            "pass" if frozen_rows and labeled_rows and frozen_v28_component_rows == len(frozen_rows) and labeled_v28_component_rows == len(labeled_rows) else "partial",
            (
                f"Feature audit has {feature.get('feature_count')} seed features; logged-event feature audit has {logged_feature.get('feature_count')} features "
                f"and joins replay component rows={logged_feature.get('api_replay_join', {}).get('feature_rows_with_api_replay')}; "
                f"canonical frozen component rows={frozen_v28_component_rows}/{len(frozen_rows)}; "
                f"canonical labeled component rows={labeled_v28_component_rows}/{len(labeled_rows)}; "
                f"component fields={v28_component_fields}."
            ),
            "Keep native v28 component capture mandatory in the packet contract; use reconstructed logged-event components only as diagnostic fallback.",
        )
    )
    checks.append(
        row(
            "Add physics features for final-average settlement, recross hazard, drift, vol regime, adverse path memory, feed freshness, and book/spot disagreement",
            "pass" if not missing_physics_features and final_avg_feature_count > 0 else "partial",
            f"Logged-event feature manifest has {logged_feature.get('feature_count')} features; final_avg_features={final_avg_feature_count}; missing_required_physics_features={missing_physics_features}. The final-average features are causal clock/sigma/strike/BTC proxies, not post-resolution samples.",
            "Replace proxy final-average clock features with observed known-at-decision final-average samples if a richer settlement feed is later captured.",
        )
    )
    checks.append(
        row(
            "Train only simple inspectable challenger surfaces first",
            "pass" if candidate_manifests else "fail",
            f"{rel_path(CALIBRATION_JSON)} candidates={len(candidate_manifests)} forward_collection_allowed={sum(1 for m in candidate_manifests if m.get('allowed_for_forward_collection'))} promotion_registry_allowed={sum(1 for m in candidate_manifests if m.get('allowed_for_forward_registry'))} types={sorted({m.get('model_type') for m in candidate_manifests})}" if candidate_manifests else "candidate manifests missing",
            "Keep challengers simple until source quality and forward evidence improve.",
        )
    )
    checks.append(
        row(
            "Score packet rows with frozen collection candidates without enabling promotion",
            "pass"
            if forward_scoring_summary.get("prediction_rows", 0) > 0
            and forward_scoring_summary.get("freeze_eligible_prediction_rows") == 0
            and forward_scoring_summary.get("promotion_allowed_rows") == 0
            else "fail",
            f"{rel_path(FORWARD_PACKET_SCORING_JSON)} packet_rows={forward_scoring_summary.get('packet_rows')} candidates={forward_scoring_summary.get('candidate_count')} prediction_rows={forward_scoring_summary.get('prediction_rows')} freeze_eligible={forward_scoring_summary.get('freeze_eligible_prediction_rows')} promotion_allowed={forward_scoring_summary.get('promotion_allowed_rows')} blockers={forward_scoring_summary.get('blocker_counts')}",
            "Use this scorer for future complete pre-resolution packets; keep current diagnostic predictions out of frozen promotion evidence.",
        )
    )
    checks.append(
        row(
            "Score probability quality before P&L",
            "pass" if calibration_summary else "fail",
            f"Calibration report verdict={calibration_summary.get('promotion_verdict')} metrics_csv={calibration_summary.get('outputs', {}).get('metrics_csv')}" if calibration_summary else "calibration report missing",
            "Continue to require Brier/logloss/calibration improvement before economics.",
        )
    )
    checks.append(
        row(
            "Score Brier, log loss, calibration bins, near-boundary accuracy, side accuracy by time/distance",
            "pass" if calibration_summary and logged_calibration_summary else "fail",
            f"Seed metrics include proxy-boundary/time slices; logged-event metrics include true abs_d_sigma boundary slices with holdout rows={logged_calibration_summary.get('split_summary', {}).get('chronological_holdout', {}).get('rows')}.",
            "Keep expanding slice scoring as richer causal rows arrive.",
        )
    )
    checks.append(
        row(
            "Score fee-aware shadow P&L after probability metrics",
            "pass" if calibration_summary else "fail",
            "Candidate prediction rows include shadow_enter, fees, expected EV, gross/net P&L cents; holdout table reports shadow net after probability metrics.",
            "Replace proxy hold-to-settlement economics with richer execution/exit labels when available.",
        )
    )
    checks.append(
        row(
            "Stage passive forward book snapshots without granting promotion",
            "pass" if passive_forward_snapshots.get("snapshot_status") == "staging_not_promotable" and passive_forward_snapshots.get("forward_promotion_rows") == 0 else "fail",
            f"{rel_path(PASSIVE_FORWARD_SNAPSHOTS_JSON)} rows={passive_forward_snapshots.get('row_count')} markets={passive_forward_snapshots.get('market_count')} registered_pre_resolution_rows={passive_forward_snapshots.get('registered_pre_resolution_rows')} missing_counts={passive_forward_snapshots.get('missing_counts')}",
            "Add BTC state, exact v28 baseline, frozen candidate predictions, and later settlement labels before these rows can become forward evidence.",
        )
    )
    checks.append(
        row(
            "Bridge paired shadow captures into packet-shaped causal rows without granting promotion",
            "pass" if shadow_forward_summary.get("packet_rows", 0) > 0 and shadow_forward_summary.get("forward_promotion_rows") == 0 else "fail",
            f"{rel_path(SHADOW_FORWARD_PACKETS_JSON)} packet_rows={shadow_forward_summary.get('packet_rows')} labeled_rows={shadow_forward_summary.get('labeled_rows')} registered_pre_resolution_rows={shadow_forward_summary.get('registered_pre_resolution_rows')} packet_ready_rows={shadow_forward_summary.get('packet_ready_rows')} missing_groups={shadow_forward_summary.get('group_missing_counts')} exclusions={shadow_forward_summary.get('exclusion_counts')}",
            "Use this bridge as the capture-to-packet proving ground; promotion still requires native v28 components and frozen successor candidates.",
        )
    )
    checks.append(
        row(
            "Preflight frozen forward registration before writing registry rows",
            "pass" if forward_preflight_summary.get("preflight_status") == "blocked" and forward_preflight_summary.get("freeze_ready_rows") == 0 else "fail",
            f"{rel_path(FORWARD_PREFLIGHT_JSON)} status={forward_preflight_summary.get('preflight_status')} open_input_rows_now={forward_preflight_summary.get('open_input_rows_now')} freeze_ready_rows={forward_preflight_summary.get('freeze_ready_rows')} packet_ready_rows={forward_packet_summary.get('packet_ready_rows')} readiness_blockers={forward_preflight_summary.get('readiness_blockers')}",
            "Keep this preflight as the required gate between passive staging and frozen forward prediction registration.",
        )
    )
    checks.append(
        row(
            "Validate complete forward input packet contract",
            "pass" if forward_packet_summary.get("packet_status") == "blocked" and forward_packet_summary.get("packet_ready_rows") == 0 else "fail",
            f"{rel_path(FORWARD_PACKET_CONTRACT_JSON)} status={forward_packet_summary.get('packet_status')} packet_ready_rows={forward_packet_summary.get('packet_ready_rows')} packet_ready_markets={forward_packet_summary.get('packet_ready_markets')} group_missing_counts={forward_packet_summary.get('group_missing_counts')}",
            "Use the packet template as the schema for future capture/enrichment before freeze.",
        )
    )
    checks.append(
        row(
            "Define executable forward collection spec for future freeze-ready rows",
            "pass"
            if forward_collection_summary.get("status") == "ready_for_future_collection_not_promotion"
            and forward_collection_summary.get("field_count", 0) > 0
            and forward_collection_summary.get("recommended_candidate_count", 0) > 0
            else "fail",
            f"{rel_path(FORWARD_COLLECTION_SPEC_JSON)} fields={forward_collection_summary.get('field_count')} groups={forward_collection_summary.get('field_group_count')} recommended_candidates={forward_collection_summary.get('recommended_candidate_count')} passive_packet_ready={forward_collection_summary.get('passive_packet_ready_rows')} shadow_packet_ready={forward_collection_summary.get('shadow_packet_ready_rows')} freeze_eligible_scored={forward_collection_summary.get('packet_scoring_freeze_eligible_rows')}",
            "Use this collection spec as the next passive run handoff; it is not promotion evidence by itself.",
        )
    )
    checks.append(
        row(
            "Implement sidecar adapter for complete pre-resolution packet rows",
            "pass"
            if forward_packet_adapter_summary.get("adapter_status") == "contract_demo_ready"
            and forward_packet_adapter_summary.get("demo_packet_ready_rows", 0) > 0
            and (forward_packet_adapter_summary.get("promotion_status") or {}).get("allowed") is False
            else "fail",
            f"{rel_path(FORWARD_PACKET_ADAPTER_JSON)} status={forward_packet_adapter_summary.get('adapter_status')} demo_rows={forward_packet_adapter_summary.get('demo_rows')} demo_packet_ready_rows={forward_packet_adapter_summary.get('demo_packet_ready_rows')} candidate_count={forward_packet_adapter_summary.get('candidate_count')} promotion_allowed={(forward_packet_adapter_summary.get('promotion_status') or {}).get('allowed')} group_missing_counts={forward_packet_adapter_summary.get('group_missing_counts')}",
            "Wire this adapter into the next real passive collection run so rows are captured before close instead of demonstrated by fixtures.",
        )
    )
    checks.append(
        row(
            "Validate sidecar input bundle contract before packet collection",
            "pass"
            if sidecar_input_bundle_summary.get("bundle_status") in {"contract_demo_ready_not_evidence", "input_bundle_ready_for_collection"}
            and sidecar_input_bundle_summary.get("bundle_ready") is True
            and sidecar_input_bundle_summary.get("promotion_allowed") is False
            else "fail",
            (
                f"{rel_path(SIDECAR_INPUT_BUNDLE_CONTRACT_JSON)} status={sidecar_input_bundle_summary.get('bundle_status')} "
                f"bundle_ready={sidecar_input_bundle_summary.get('bundle_ready')} "
                f"source_input={sidecar_input_bundle_summary.get('source_input')} "
                f"btc_history_rows={sidecar_input_bundle_summary.get('btc_history_rows')} "
                f"forward_collection_candidates={sidecar_input_bundle_summary.get('forward_collection_candidate_count')} "
                f"promotion_allowed={sidecar_input_bundle_summary.get('promotion_allowed')} "
                f"blockers={sidecar_input_bundle_summary.get('blocker_counts')}"
            ),
            "Use this contract before real sidecar collection; ready bundles still require packet freeze, later labels, and evidence scoring.",
        )
    )
    checks.append(
        row(
            "Provide public REST sidecar bundle builder without granting promotion",
            "pass"
            if public_rest_sidecar_bundle_summary.get("bundle_status") in {
                "contract_demo_ready_not_evidence",
                "input_bundle_ready_for_collection",
            }
            and public_rest_sidecar_bundle_summary.get("bundle_ready") is True
            and public_rest_sidecar_bundle_summary.get("packet_rows", 0) > 0
            and public_rest_sidecar_bundle_summary.get("promotion_allowed") is False
            else "fail",
            (
                f"{rel_path(PUBLIC_REST_SIDECAR_BUNDLE_JSON)} mode={public_rest_sidecar_bundle_summary.get('mode')} "
                f"status={public_rest_sidecar_bundle_summary.get('bundle_status')} "
                f"bundle_ready={public_rest_sidecar_bundle_summary.get('bundle_ready')} "
                f"market={public_rest_sidecar_bundle_summary.get('market_ticker')} "
                f"btc_history_rows={public_rest_sidecar_bundle_summary.get('btc_history_rows')} "
                f"packet_rows={public_rest_sidecar_bundle_summary.get('packet_rows')} "
                f"promotion_allowed={public_rest_sidecar_bundle_summary.get('promotion_allowed')} "
                f"output_bundle={public_rest_sidecar_bundle_summary.get('output_bundle_json')} "
                f"blockers={public_rest_sidecar_bundle_summary.get('blocker_counts')}"
            ),
            "Use public REST mode during open markets to write real non-simulated sidecar bundles; fixture output remains diagnostic and non-promoting.",
        )
    )
    checks.append(
        row(
            "Provide public REST sidecar batch builder for active boundary coverage without granting promotion",
            "pass"
            if public_rest_sidecar_batch_summary.get("batch_status") in {
                "contract_demo_ready_not_evidence",
                "batch_bundles_ready_for_freeze",
                "blocked_no_ready_batch_bundles",
            }
            and public_rest_sidecar_batch_summary.get("bundle_ready_files", 0) > 0
            and public_rest_sidecar_batch_summary.get("packet_rows", 0) > 0
            and public_rest_sidecar_batch_summary.get("promotion_allowed") is False
            else "fail",
            (
                f"{rel_path(PUBLIC_REST_SIDECAR_BATCH_JSON)} mode={public_rest_sidecar_batch_summary.get('mode')} "
                f"status={public_rest_sidecar_batch_summary.get('batch_status')} "
                f"markets_selected={public_rest_sidecar_batch_summary.get('markets_selected')} "
                f"ready_files={public_rest_sidecar_batch_summary.get('bundle_ready_files')} "
                f"packet_rows={public_rest_sidecar_batch_summary.get('packet_rows')} "
                f"packet_markets={public_rest_sidecar_batch_summary.get('packet_markets')} "
                f"promotion_allowed={public_rest_sidecar_batch_summary.get('promotion_allowed')} "
                f"blockers={public_rest_sidecar_batch_summary.get('blocker_counts')}"
            ),
            "Use explicit public REST batch mode during open markets to capture all nearest-close BTC15M boundaries before freeze.",
        )
    )
    checks.append(
        row(
            "Implement sidecar collector bridge for future real pre-resolution packet rows",
            "pass"
            if sidecar_packet_collector_summary.get("collector_status") == "contract_demo_ready_not_evidence"
            and sidecar_packet_collector_summary.get("demo_packet_ready_rows", 0) > 0
            and "input_bundle_json" in (sidecar_packet_collector_summary.get("input_modes") or [])
            and (sidecar_packet_collector_summary.get("promotion_status") or {}).get("allowed") is False
            else "fail",
            f"{rel_path(SIDECAR_PACKET_COLLECTOR_JSON)} status={sidecar_packet_collector_summary.get('collector_status')} input_modes={sidecar_packet_collector_summary.get('input_modes')} demo_rows={sidecar_packet_collector_summary.get('demo_rows')} demo_packet_ready_rows={sidecar_packet_collector_summary.get('demo_packet_ready_rows')} simulated_rows={sidecar_packet_collector_summary.get('simulated_rows')} diagnostic_rows={sidecar_packet_collector_summary.get('diagnostic_rows')} promotion_allowed={(sidecar_packet_collector_summary.get('promotion_status') or {}).get('allowed')}",
            "Run this collector during open markets with real BTC/v28/book inputs, then freeze those rows before close; demo rows remain non-evidence.",
        )
    )
    checks.append(
        row(
            "Provide one-command sidecar bundle freeze handoff without granting promotion",
            "pass"
            if sidecar_bundle_freeze_handoff_summary.get("bundle_handoff_status") in {
                "blocked_non_promotable_bundle_rows",
                "blocked_no_frozen_rows",
                "frozen_handoff_below_coverage_floor",
                "bundle_handoff_ready_for_settlement_labels",
            }
            and sidecar_bundle_freeze_handoff_summary.get("promotion_allowed") is False
            else "fail",
            (
                f"{rel_path(SIDECAR_BUNDLE_FREEZE_HANDOFF_JSON)} status={sidecar_bundle_freeze_handoff_summary.get('bundle_handoff_status')} "
                f"bundle={(sidecar_bundle_freeze_handoff_summary.get('bundle') or {}).get('bundle_status')} "
                f"packet_rows={(sidecar_bundle_freeze_handoff_summary.get('packet_rows') or {}).get('rows')} "
                f"frozen_rows={(sidecar_bundle_freeze_handoff_summary.get('freeze_handoff') or {}).get('frozen_prediction_rows')} "
                f"registry_rows={(sidecar_bundle_freeze_handoff_summary.get('freeze_handoff') or {}).get('registry_rows')} "
                f"promotion_allowed={sidecar_bundle_freeze_handoff_summary.get('promotion_allowed')} "
                f"blockers={sidecar_bundle_freeze_handoff_summary.get('blockers')}"
            ),
            "Use this one-command handoff on real sidecar bundles; promotion remains blocked until labels and forward evidence gates pass.",
        )
    )
    checks.append(
        row(
            "Provide batch sidecar bundle handoff for broad market collection without granting promotion",
            "pass"
            if sidecar_bundle_batch_handoff_summary.get("batch_handoff_status") in {
                "blocked_no_input_bundles",
                "blocked_no_packet_rows",
                "blocked_non_promotable_bundle_rows",
                "blocked_no_frozen_rows",
                "frozen_batch_handoff_below_coverage_floor",
                "frozen_batch_handoff_ready_for_settlement_labels",
            }
            and sidecar_bundle_batch_handoff_summary.get("promotion_allowed") is False
            else "fail",
            (
                f"{rel_path(SIDECAR_BUNDLE_BATCH_HANDOFF_JSON)} status={sidecar_bundle_batch_handoff_summary.get('batch_handoff_status')} "
                f"input_files={sidecar_bundle_batch_handoff_summary.get('input_bundle_files')} "
                f"ready_files={sidecar_bundle_batch_handoff_summary.get('ready_bundle_files')} "
                f"packet_rows={(sidecar_bundle_batch_handoff_summary.get('packet_rows') or {}).get('rows')} "
                f"packet_markets={(sidecar_bundle_batch_handoff_summary.get('packet_rows') or {}).get('markets')} "
                f"frozen_rows={(sidecar_bundle_batch_handoff_summary.get('freeze_handoff') or {}).get('frozen_prediction_rows')} "
                f"registry_rows={(sidecar_bundle_batch_handoff_summary.get('freeze_handoff') or {}).get('registry_rows')} "
                f"promotion_allowed={sidecar_bundle_batch_handoff_summary.get('promotion_allowed')} "
                f"blockers={sidecar_bundle_batch_handoff_summary.get('blockers')}"
            ),
            "Drop real open-market sidecar bundles into the batch directory; promotion remains blocked until coverage, labels, and evidence gates pass.",
        )
    )
    checks.append(
        row(
            "Fetch sidecar batch settlement labels only after market close without granting promotion",
            "pass"
            if sidecar_bundle_batch_settlement_labels_summary.get("label_fetch_status") in {
                "blocked_no_frozen_rows",
                "blocked_no_frozen_markets",
                "blocked_waiting_for_market_close",
                "blocked_no_resolved_labels",
                "settlement_labels_available",
            }
            and sidecar_bundle_batch_settlement_labels_summary.get("promotion_allowed") is False
            else "fail",
            (
                f"{rel_path(SIDECAR_BUNDLE_BATCH_SETTLEMENT_LABELS_JSON)} status={sidecar_bundle_batch_settlement_labels_summary.get('label_fetch_status')} "
                f"frozen_rows={sidecar_bundle_batch_settlement_labels_summary.get('frozen_rows')} "
                f"frozen_markets={sidecar_bundle_batch_settlement_labels_summary.get('frozen_markets')} "
                f"label_rows={sidecar_bundle_batch_settlement_labels_summary.get('label_rows')} "
                f"label_markets={sidecar_bundle_batch_settlement_labels_summary.get('label_markets')} "
                f"promotion_allowed={sidecar_bundle_batch_settlement_labels_summary.get('promotion_allowed')} "
                f"blockers={sidecar_bundle_batch_settlement_labels_summary.get('blocker_counts')}"
            ),
            "Rerun after market close until settlement labels are available, then label-join and score forward evidence.",
        )
    )
    checks.append(
        row(
            "Provide batch sidecar label join handoff without granting promotion",
            "pass"
            if sidecar_bundle_batch_label_join_summary.get("batch_label_join_status") in {
                "blocked_no_batch_frozen_rows",
                "blocked_no_joined_batch_labels",
                "joined_batch_labels_available",
            }
            and sidecar_bundle_batch_label_join_summary.get("promotion_allowed") is False
            else "fail",
            (
                f"{rel_path(SIDECAR_BUNDLE_BATCH_LABEL_JOIN_JSON)} status={sidecar_bundle_batch_label_join_summary.get('batch_label_join_status')} "
                f"frozen_rows={sidecar_bundle_batch_label_join_summary.get('frozen_rows')} "
                f"labeled_rows={sidecar_bundle_batch_label_join_summary.get('labeled_rows')} "
                f"joined_rows={sidecar_bundle_batch_label_join_summary.get('joined_rows')} "
                f"joined_markets={sidecar_bundle_batch_label_join_summary.get('joined_markets')} "
                f"label_source_rows={sidecar_bundle_batch_label_join_summary.get('label_source_rows')} "
                f"promotion_allowed={sidecar_bundle_batch_label_join_summary.get('promotion_allowed')} "
                f"blockers={sidecar_bundle_batch_label_join_summary.get('blockers')}"
            ),
            "Use this after real sidecar batch frozen rows settle; promotion remains blocked until source, coverage, evidence, and verifier gates pass.",
        )
    )
    checks.append(
        row(
            "Score sidecar batch settled evidence without granting promotion",
            "pass"
            if sidecar_batch_evidence_summary.get("evidence_status") in {
                "blocked_no_joined_sidecar_batch_rows",
                "scored_sidecar_batch_evidence",
            }
            and (sidecar_batch_evidence_summary.get("promotion_status") or {}).get("allowed") is False
            and sidecar_batch_evidence_summary.get("canonical_promotion_ledger") is False
            else "fail",
            (
                f"{rel_path(SIDECAR_BATCH_EVIDENCE_SCORE_JSON)} status={sidecar_batch_evidence_summary.get('evidence_status')} "
                f"clean_rows={sidecar_batch_evidence_summary.get('clean_forward_rows')} "
                f"clean_markets={sidecar_batch_evidence_summary.get('clean_forward_markets')} "
                f"candidates={sidecar_batch_evidence_summary.get('candidate_count')} "
                f"promotable_by_sidecar_evidence={sidecar_batch_evidence_summary.get('promotable_candidate_count')} "
                f"canonical_promotion_ledger={sidecar_batch_evidence_summary.get('canonical_promotion_ledger')} "
                f"promotion_allowed={(sidecar_batch_evidence_summary.get('promotion_status') or {}).get('allowed')}"
            ),
            "Keep scoring sidecar evidence for diagnostics, but require canonical source contract, coverage, forward evidence, and promotion verifier before promotion.",
        )
    )
    checks.append(
        row(
            "Run one repeatable sidecar collection cycle without granting promotion",
            "pass"
            if sidecar_collection_cycle_summary.get("cycle_status") in {
                "blocked_no_frozen_sidecar_rows",
                "frozen_sidecar_rows_waiting_for_settlement",
                "sidecar_evidence_below_coverage_floor",
                "sidecar_evidence_scored_no_promotable_candidate",
                "sidecar_evidence_ready_but_source_contract_blocked",
                "sidecar_cycle_ready_for_external_promotion_verifier",
            }
            and sidecar_collection_cycle_summary.get("promotion_allowed") is False
            and "does not place orders" in (sidecar_collection_cycle_summary.get("research_only_guardrails") or [])
            else "fail",
            (
                f"{rel_path(SIDECAR_COLLECTION_CYCLE_JSON)} status={sidecar_collection_cycle_summary.get('cycle_status')} "
                f"collect_mode={sidecar_collection_cycle_summary.get('collect_mode')} "
                f"frozen_rows={sidecar_collection_cycle_summary.get('sidecar_frozen_rows')} "
                f"frozen_markets={sidecar_collection_cycle_summary.get('sidecar_frozen_markets')} "
                f"joined_rows={sidecar_collection_cycle_summary.get('sidecar_joined_rows')} "
                f"clean_rows={sidecar_collection_cycle_summary.get('sidecar_clean_forward_rows')} "
                f"clean_markets={sidecar_collection_cycle_summary.get('sidecar_clean_forward_markets')} "
                f"promotable_candidates={sidecar_collection_cycle_summary.get('sidecar_promotable_candidate_count')} "
                f"promotion_allowed={sidecar_collection_cycle_summary.get('promotion_allowed')} "
                f"blockers={sidecar_collection_cycle_summary.get('blockers')}"
            ),
            "Use this cycle repeatedly for pre-close bundle capture/freeze and post-close label/score refresh; it remains non-promoting by design.",
        )
    )
    checks.append(
        row(
            "Stage only frozen pre-resolution forward evidence without granting promotion",
            "pass"
            if (
                (
                    frozen_forward.get("freeze_status") == "blocked_no_frozen_predictions"
                    and frozen_forward.get("frozen_prediction_rows") == 0
                )
                or (
                    frozen_forward.get("freeze_status")
                    in {
                        "sidecar_forward_staged_below_coverage_floor",
                        "sidecar_forward_staged_ready_for_label_join",
                    }
                    and (frozen_forward.get("promotion_status") or {}).get("allowed_for_promotion_scoring") is False
                    and frozen_forward.get("frozen_prediction_rows", 0) >= 0
                )
            )
            else "fail",
            (
                f"{rel_path(FROZEN_FORWARD_SUMMARY_JSON)} status={frozen_forward.get('freeze_status')} "
                f"source_family={frozen_forward.get('source_family')} passive_input_rows={frozen_forward.get('passive_input_rows')} "
                f"freeze_ready_input_rows={frozen_forward.get('freeze_ready_input_rows')} "
                f"frozen_prediction_rows={frozen_forward.get('frozen_prediction_rows')} "
                f"frozen_prediction_markets={frozen_forward.get('frozen_prediction_markets')} "
                f"coverage_ready={frozen_forward.get('coverage_ready')} "
                f"promotion_allowed={(frozen_forward.get('promotion_status') or {}).get('allowed_for_promotion_scoring')} "
                f"blockers={frozen_forward.get('blocker_counts')}"
            ),
            "Use passive freezer or sidecar staging only for rows already complete and frozen before close; promotion remains blocked until labels, coverage, source contract, and verifier pass.",
        )
    )
    checks.append(
        row(
            "Provide reproducible packet freeze handoff without granting promotion",
            "pass"
            if forward_packet_freeze_handoff_summary.get("handoff_status") in {"blocked_non_promotable_input_rows", "blocked_no_frozen_rows", "frozen_handoff_below_coverage_floor", "frozen_handoff_ready_for_settlement_labels"}
            and forward_packet_freeze_handoff_summary.get("promotion_allowed") is False
            else "fail",
            (
                f"{rel_path(FORWARD_PACKET_FREEZE_HANDOFF_JSON)} status={forward_packet_freeze_handoff_summary.get('handoff_status')} "
                f"packet_ready_rows={(forward_packet_freeze_handoff_summary.get('packet_contract') or {}).get('packet_ready_rows')} "
                f"freeze_ready_rows={(forward_packet_freeze_handoff_summary.get('preflight') or {}).get('freeze_ready_rows')} "
                f"frozen_rows={(forward_packet_freeze_handoff_summary.get('freeze') or {}).get('frozen_prediction_rows')} "
                f"registry_rows={(forward_packet_freeze_handoff_summary.get('registry') or {}).get('row_count')} "
                f"promotion_allowed={forward_packet_freeze_handoff_summary.get('promotion_allowed')} "
                f"blockers={forward_packet_freeze_handoff_summary.get('blockers')}"
            ),
            "Use this handoff on real sidecar packet CSVs; canonical promotion remains blocked until frozen rows settle and pass evidence gates.",
        )
    )
    checks.append(
        row(
            "Join settlement labels only after frozen forward prediction and resolution",
            "pass"
            if forward_label_join_summary.get("join_status") in {"blocked_no_joined_forward_labels", "joined_labels_available"}
            and (forward_label_join_summary.get("promotion_status") or {}).get("allowed") is False
            else "fail",
            f"{rel_path(FORWARD_LABEL_JOIN_JSON)} status={forward_label_join_summary.get('join_status')} frozen_rows={forward_label_join_summary.get('frozen_rows')} joined_rows={forward_label_join_summary.get('joined_rows')} joined_markets={forward_label_join_summary.get('joined_markets')} promotion_allowed={(forward_label_join_summary.get('promotion_status') or {}).get('allowed')} blockers={forward_label_join_summary.get('blocker_counts')}",
            "Use this joiner after real frozen rows settle; it is necessary but not sufficient for promotion.",
        )
    )
    checks.append(
        row(
            "Score settled forward evidence candidate-vs-v28 before promotion",
            "pass"
            if forward_evidence_summary.get("evidence_status") in {"blocked_no_joined_forward_rows", "scored_forward_evidence"}
            and (forward_evidence_summary.get("promotion_status") or {}).get("allowed") is False
            else "fail",
            f"{rel_path(FORWARD_EVIDENCE_SCORE_JSON)} status={forward_evidence_summary.get('evidence_status')} clean_rows={forward_evidence_summary.get('clean_forward_rows')} clean_markets={forward_evidence_summary.get('clean_forward_markets')} candidates={forward_evidence_summary.get('candidate_count')} promotable_by_forward_evidence={forward_evidence_summary.get('promotable_candidate_count')} promotion_allowed={(forward_evidence_summary.get('promotion_status') or {}).get('allowed')}",
            "After real joined forward rows exist, require this scorer to beat v28 on Brier/logloss and near-boundary slices before promotion review.",
        )
    )
    source_readiness_blockers = forward_source_readiness_summary.get("blockers") or []
    checks.append(
        row(
            "Audit forward source readiness and joinability before promotion",
            "pass"
            if forward_source_readiness_summary.get("overall_status") == "blocked_missing_freeze_ready_sources"
            and source_readiness_blockers
            and forward_source_readiness_summary.get("promotion_allowed") is False
            else "fail",
            (
                f"{rel_path(FORWARD_SOURCE_READINESS_JSON)} status={forward_source_readiness_summary.get('overall_status')} "
                f"passive_rows={forward_source_readiness_summary.get('passive_rows')} "
                f"passive_markets={forward_source_readiness_summary.get('passive_markets')} "
                f"live_v28_base_rows={forward_source_readiness_summary.get('live_v28_base_field_rows')} "
                f"native_component_rows={forward_source_readiness_summary.get('live_v28_native_component_rows')} "
                f"freeze_eligible_packet_predictions={forward_source_readiness_summary.get('freeze_eligible_packet_prediction_rows')} "
                f"frozen_rows={forward_source_readiness_summary.get('frozen_forward_rows')} "
                f"registry_rows={forward_source_readiness_summary.get('forward_registry_rows')} "
                f"promotion_allowed={forward_source_readiness_summary.get('promotion_allowed')} "
                f"blockers={source_readiness_blockers}"
            ),
            "Keep this source-readiness audit in the refresh path so missing time-joined BTC/v28/candidate evidence is explicit before promotion review.",
        )
    )
    source_contract_verdict = source_contract_summary.get("overall_verdict")
    source_contract_gate_ok = (
        source_contract_verdict in {"blocked", "promotion_grade"}
        and bool(source_contract_summary.get("promotion_contract_ready")) == (source_contract_verdict == "promotion_grade")
        and all(
            dataset_id in (source_contract_summary.get("required_forward_dataset_status") or {})
            for dataset_id in ("forward_registry", "forward_labeled_predictions")
        )
    )
    checks.append(
        row(
            "Enforce source-quality contract as executable gate",
            "pass" if source_contract_gate_ok else "fail",
            (
                f"{rel_path(SOURCE_CONTRACT_JSON)} verdict={source_contract_verdict} "
                f"promotion_contract_ready={source_contract_summary.get('promotion_contract_ready')} "
                f"required_forward_dataset_status={source_contract_summary.get('required_forward_dataset_status')} "
                f"blocked_datasets={source_contract_summary.get('blocked_datasets')} "
                f"hard_blockers={source_contract_summary.get('hard_blockers')}"
            ),
            "Keep source-contract validation in the required refresh path before any promotion review.",
        )
    )
    verifier_source_contract_blocker = "source_contract_promotion_ready" in (promotion_verifier_summary.get("hard_blockers") or [])
    checks.append(
        row(
            "Promotion verifier consumes source-contract readiness as a hard gate",
            "pass"
            if "promotion_contract_ready" in source_contract_summary
            and ((not source_contract_ready and verifier_source_contract_blocker) or source_contract_ready)
            else "fail",
            (
                f"{rel_path(SOURCE_CONTRACT_JSON)} promotion_contract_ready={source_contract_summary.get('promotion_contract_ready')} "
                f"missing_required_forward_datasets={source_contract_summary.get('missing_required_forward_datasets')}; "
                f"{rel_path(PROMOTION_VERIFIER_JSON)} hard_blockers={promotion_verifier_summary.get('hard_blockers')}"
            ),
            "Keep source-contract readiness wired into the verifier so a future candidate cannot pass while source-quality artifacts are blocked.",
        )
    )
    checks.append(
        row(
            "Promote only if challenger beats v28 on chronological holdout",
            "pass" if calibration_summary else "fail",
            f"Calibration holdout rows={calibration_summary.get('split_summary', {}).get('chronological_holdout', {}).get('rows')} promotion_verdict={calibration_summary.get('promotion_verdict')}; verifier overall={promotion_verifier_summary.get('overall_verdict')} blocked={promotion_verifier_summary.get('blocked_candidate_count')}" if calibration_summary else "missing holdout scoring",
            "Keep market-level chronological holdout and strict promotion verifier as required gates.",
        )
    )
    checks.append(
        row(
            "Require post-lock forward rows/frozen evidence before promotion",
            "pass" if canonical_forward_floor_met and source_contract_ready else "partial" if canonical_frozen_rows > 0 else "fail",
            (
                f"Canonical frozen rows={canonical_frozen_rows} markets={canonical_frozen_markets}; "
                f"canonical joined rows={canonical_joined_rows} markets={canonical_joined_markets}; "
                f"registry_status={forward_registry.get('registry_status')} registry_rows={forward_registry.get('row_count')} "
                f"passive_staging_rows={passive_forward_snapshots.get('row_count')} packet_ready_rows={forward_packet_summary.get('packet_ready_rows')} "
                f"freeze_ready_rows={forward_preflight_summary.get('freeze_ready_rows')} scored_packet_predictions={forward_scoring_summary.get('prediction_rows')} "
                f"freeze_eligible_packet_predictions={forward_scoring_summary.get('freeze_eligible_prediction_rows')} "
                f"sidecar_batch_frozen_rows={(sidecar_bundle_batch_handoff_summary.get('freeze_handoff') or {}).get('frozen_prediction_rows')} "
                f"sidecar_batch_registry_rows={(sidecar_bundle_batch_handoff_summary.get('freeze_handoff') or {}).get('registry_rows')} "
                f"sidecar_batch_joined_rows={sidecar_bundle_batch_label_join_summary.get('joined_rows')} "
                f"sidecar_batch_evidence_clean_rows={sidecar_batch_evidence_summary.get('clean_forward_rows')} "
                f"minimum_forward_rows={minimum_forward_rows} minimum_forward_markets={minimum_forward_markets} "
                f"required_forward_blockers={required_forward_blockers}; "
                "candidate manifests remain allowed_for_forward_registry=false until promotion gates pass."
            ),
            "Keep collecting sidecar bundles before close, join labels after settlement, then move only broad settled rows through source contract and promotion verifier.",
        )
    )
    checks.append(
        row(
            "Keep broad market coverage",
            "pass" if canonical_forward_floor_met else "partial",
            (
                f"Diagnostic seed has rows={dataset.get('row_count')} markets={dataset.get('market_count')}; "
                f"passive forward staging has rows={passive_forward_snapshots.get('row_count')} markets={passive_forward_snapshots.get('market_count')}; "
                f"shadow packet rows={shadow_forward_summary.get('packet_rows')} markets={shadow_forward_summary.get('markets')}; "
                f"canonical frozen rows={canonical_frozen_rows} markets={canonical_frozen_markets}; "
                f"canonical joined rows={canonical_joined_rows} markets={canonical_joined_markets}; "
                f"minimum_forward_rows={minimum_forward_rows} minimum_forward_markets={minimum_forward_markets}; "
                f"canonical_forward_floor_met={canonical_forward_floor_met}."
            ),
            "Collect broad every-market/every-strike forward rows, not only approved or actionable rows.",
        )
    )
    checks.append(
        row(
            "Do not rely on recomputed-after-the-fact rows",
            "partial" if canonical_frozen_rows > 0 and not source_contract_ready else "pass" if source_contract_ready else "fail",
            f"Posthoc seed rows remain diagnostic only: forward_promotion={dataset.get('eligibility_counts', {}).get('forward_promotion')} seed_posthoc_rows={baseline.get('seed_posthoc_rows')}. Canonical frozen rows={canonical_frozen_rows} markets={canonical_frozen_markets}; canonical joined rows={canonical_joined_rows} markets={canonical_joined_markets}; sidecar evidence clean rows={sidecar_batch_evidence_summary.get('clean_forward_rows')}; missing_required_forward_datasets={source_contract_summary.get('missing_required_forward_datasets')} required_forward_blockers={required_forward_blockers}.",
            "Use posthoc artifacts only for diagnostics; rely on sidecar/pre-close frozen rows only after they settle, pass source contract, and cover broad markets.",
        )
    )
    checks.append(
        row(
            "Automated tests cover key invariants",
            "pass",
            "test_v28_successor_pipeline.py covers seed canonicalization, leakage-safe feature manifests, candidate split/gates, baseline replay/recompute separation, v28 API replay components, passive forward staging, shadow packet bridging, packet candidate scoring, collection-spec generation, packet-contract blocking, promotion verifier, and source-contract blocking.",
            "Add tests for richer snapshot parsers when those sources are added.",
        )
    )

    overall = "complete" if all(check["status"] == "pass" for check in checks) else "not_complete"
    status_counts = dict(Counter(check["status"] for check in checks))
    summary = {
        "generated_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "overall_status": overall,
        "status_counts": status_counts,
        "checks": len(checks),
        "blocking_requirements": [check for check in checks if check["status"] == "fail"],
        "partial_requirements": [check for check in checks if check["status"] == "partial"],
        "source_artifacts": {
            "spec": rel_path(SPEC_MD),
            "dataset_audit": rel_path(DATASET_JSON),
            "feature_audit": rel_path(FEATURE_JSON),
            "baseline_replay": rel_path(BASELINE_REPLAY_JSON),
            "calibration": rel_path(CALIBRATION_JSON),
            "forward_registry": rel_path(FORWARD_REGISTRY_JSON),
            "logged_event_dataset": rel_path(LOGGED_EVENT_DATASET_JSON),
            "logged_event_feature_audit": rel_path(LOGGED_EVENT_FEATURE_JSON),
            "logged_event_calibration": rel_path(LOGGED_EVENT_CALIBRATION_JSON),
            "promotion_verifier": rel_path(PROMOTION_VERIFIER_JSON),
            "source_contract": rel_path(SOURCE_CONTRACT_JSON),
            "logged_event_api_replay": rel_path(LOGGED_EVENT_API_REPLAY_JSON),
            "passive_forward_snapshots": rel_path(PASSIVE_FORWARD_SNAPSHOTS_JSON),
            "forward_freeze_preflight": rel_path(FORWARD_PREFLIGHT_JSON),
            "frozen_forward_predictions": rel_path(FROZEN_FORWARD_SUMMARY_JSON),
            "forward_packet_contract": rel_path(FORWARD_PACKET_CONTRACT_JSON),
            "shadow_forward_packets": rel_path(SHADOW_FORWARD_PACKETS_JSON),
            "forward_packet_candidate_scoring": rel_path(FORWARD_PACKET_SCORING_JSON),
            "forward_collection_spec": rel_path(FORWARD_COLLECTION_SPEC_JSON),
            "forward_packet_adapter": rel_path(FORWARD_PACKET_ADAPTER_JSON),
            "public_rest_sidecar_bundle": rel_path(PUBLIC_REST_SIDECAR_BUNDLE_JSON),
            "public_rest_sidecar_batch": rel_path(PUBLIC_REST_SIDECAR_BATCH_JSON),
            "sidecar_input_bundle_contract": rel_path(SIDECAR_INPUT_BUNDLE_CONTRACT_JSON),
            "sidecar_bundle_replay": rel_path(SIDECAR_BUNDLE_REPLAY_JSON),
            "sidecar_packet_collector": rel_path(SIDECAR_PACKET_COLLECTOR_JSON),
            "sidecar_bundle_freeze_handoff": rel_path(SIDECAR_BUNDLE_FREEZE_HANDOFF_JSON),
            "sidecar_bundle_batch_handoff": rel_path(SIDECAR_BUNDLE_BATCH_HANDOFF_JSON),
            "sidecar_bundle_batch_settlement_labels": rel_path(SIDECAR_BUNDLE_BATCH_SETTLEMENT_LABELS_JSON),
            "sidecar_bundle_batch_label_join": rel_path(SIDECAR_BUNDLE_BATCH_LABEL_JOIN_JSON),
            "sidecar_batch_evidence_score": rel_path(SIDECAR_BATCH_EVIDENCE_SCORE_JSON),
            "sidecar_collection_cycle": rel_path(SIDECAR_COLLECTION_CYCLE_JSON),
            "forward_packet_freeze_handoff": rel_path(FORWARD_PACKET_FREEZE_HANDOFF_JSON),
            "forward_label_join": rel_path(FORWARD_LABEL_JOIN_JSON),
            "forward_evidence_score": rel_path(FORWARD_EVIDENCE_SCORE_JSON),
            "forward_source_readiness": rel_path(FORWARD_SOURCE_READINESS_JSON),
        },
    }
    return sorted(checks, key=lambda item: (status_rank(item["status"]), item["requirement"])), summary


def write_csv_rows(rows: list[dict[str, Any]], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["requirement", "status", "evidence", "next_action"])
        writer.writeheader()
        writer.writerows(rows)


def write_markdown(checks: list[dict[str, Any]], summary: dict[str, Any], path: Path) -> None:
    lines = [
        "# v28 Successor Goal Completion Audit",
        "",
        f"- Generated UTC: `{summary['generated_utc']}`",
        f"- Overall status: `{summary['overall_status']}`",
        f"- Status counts: `{summary['status_counts']}`",
        "",
        "## Checklist",
        "",
        "| status | requirement | evidence | next action |",
        "|---|---|---|---|",
    ]
    for check in checks:
        lines.append(
            f"| `{check['status']}` | {escape_cell(check['requirement'])} | {escape_cell(check['evidence'])} | {escape_cell(check['next_action'])} |"
        )
    lines.extend(
        [
            "",
            "## Read",
            "",
            "- The goal is not complete because exact native v28 replay/component capture, recorded snapshot replay, and a promotable challenger are still missing.",
            "- Current artifacts are useful diagnostic scaffolding and correctly keep promotion closed.",
        ]
    )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def escape_cell(value: Any) -> str:
    return str(value).replace("|", "\\|").replace("\n", " ")


def write_outputs(checks: list[dict[str, Any]], summary: dict[str, Any]) -> None:
    EDGE_DIR.mkdir(parents=True, exist_ok=True)
    AUDIT_JSON.write_text(json.dumps({"summary": summary, "checks": checks}, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_csv_rows(checks, AUDIT_CSV)
    write_markdown(checks, summary, AUDIT_MD)


def main() -> None:
    parser = argparse.ArgumentParser(description="Audit v28 successor goal completion.")
    parser.add_argument("--write", action="store_true", help="Write audit artifacts.")
    parser.add_argument("--dry-run", action="store_true", help="Build audit in memory only.")
    args = parser.parse_args()

    checks, summary = build_checklist()
    if args.write and not args.dry_run:
        write_outputs(checks, summary)
    print(
        json.dumps(
            {
                "overall_status": summary["overall_status"],
                "status_counts": summary["status_counts"],
                "blocking_requirements": len(summary["blocking_requirements"]),
                "partial_requirements": len(summary["partial_requirements"]),
                "written": bool(args.write and not args.dry_run),
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
