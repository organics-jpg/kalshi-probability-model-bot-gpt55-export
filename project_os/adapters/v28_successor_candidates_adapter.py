from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from project_os.curation import Overrides
from project_os.models import AdapterResult, ProjectNode, path_mtime_iso

from .base import apply_node_overrides, contains_family_edge, family_node, file_size, node_id, result, safe_load_json


FAMILY = "v28_successor"


def _safe_float(value: Any) -> float | None:
    if value in (None, "") or isinstance(value, bool):
        return None
    try:
        return float(str(value).strip().replace(",", "").replace("$", "").replace("%", ""))
    except (TypeError, ValueError):
        return None


def _extract_number(text: str, name: str) -> float | None:
    match = re.search(rf"\b{re.escape(name)}=([-+]?\d+(?:\.\d+)?)", text)
    return _safe_float(match.group(1)) if match else None


def _slug(text: str) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9]+", "_", str(text or "").strip()).strip("_")
    return cleaned or "unknown"


def _gate_maps(candidate: dict[str, Any]) -> tuple[dict[str, bool], dict[str, str]]:
    states: dict[str, bool] = {}
    evidence: dict[str, str] = {}
    for gate in candidate.get("gates") or []:
        if not isinstance(gate, dict):
            continue
        name = str(gate.get("gate") or "")
        if not name:
            continue
        states[name] = bool(gate.get("passed"))
        evidence[name] = str(gate.get("evidence") or "")
    return states, evidence


def _forward_gate_lookup(root: Path) -> dict[str, dict[str, Any]]:
    path = root / "logs" / "edge_research" / "v28_successor_forward_evidence_score_latest.json"
    parsed, _note = safe_load_json(path, max_bytes=10_000_000) if path.exists() else ({}, "")
    payload = parsed if isinstance(parsed, dict) else {}
    summary = payload.get("summary") if isinstance(payload.get("summary"), dict) else {}
    rows = summary.get("candidate_gates") if isinstance(summary, dict) else []
    out: dict[str, dict[str, Any]] = {}
    for row in rows or []:
        if isinstance(row, dict) and row.get("candidate_id"):
            out[str(row["candidate_id"])] = row
    return out


def _candidate_metrics(candidate: dict[str, Any], forward_gate: dict[str, Any]) -> dict[str, Any]:
    gate_states, gate_evidence = _gate_maps(candidate)
    failed_gates = [str(gate) for gate in candidate.get("failed_gates") or []]
    passed_gates = [str(gate) for gate in candidate.get("passed_gates") or []]
    metrics: dict[str, Any] = {
        "candidate_id": candidate.get("candidate_id"),
        "candidate_variant": candidate.get("variant"),
        "model_hash": candidate.get("model_hash"),
        "model_track": candidate.get("model_track"),
        "model_type": candidate.get("model_type"),
        "promotion_verifier_verdict": candidate.get("verdict"),
        "promotion_verifier_failed_gates": failed_gates,
        "promotion_verifier_passed_gates": passed_gates,
        "promotion_verifier_passed_gate_count": len(passed_gates),
        "promotion_verifier_failed_gate_count": len(failed_gates),
    }

    for gate_name, passed in gate_states.items():
        metrics[f"gate_{_slug(gate_name)}_passed"] = passed

    holdout = gate_evidence.get("holdout_coverage", "")
    if holdout:
        metrics["holdout_rows"] = _extract_number(holdout, "rows")
        metrics["holdout_markets"] = _extract_number(holdout, "markets")
        metrics["holdout_required_rows"] = _extract_number(holdout, "required_rows")
        metrics["holdout_required_markets"] = _extract_number(holdout, "required_markets")

    shadow = gate_evidence.get("shadow_economics_reported", "")
    shadow_net = _extract_number(shadow, "shadow_net_pnl_cents")
    if shadow_net is not None:
        metrics.update(
            {
                "shadow_net_pnl_cents": shadow_net,
                "shadow_expected_ev_cents": _extract_number(shadow, "shadow_expected_ev_cents"),
                "net_pnl": shadow_net,
                "net_pnl_source_key": "promotion_verifier.shadow_economics_reported.shadow_net_pnl_cents",
                "net_pnl_unit_hint": "cents",
                "pnl_provenance": "v28_successor_promotion_verifier",
                "pnl_status": "normalized_from_promotion_verifier_shadow_economics",
            }
        )

    source_quality = gate_evidence.get("source_quality_forward_registered", "")
    if source_quality:
        metrics["source_quality_clean_rows"] = _extract_number(source_quality, "clean_rows")
        metrics["source_quality_clean_markets"] = _extract_number(source_quality, "clean_markets")

    frozen = gate_evidence.get("frozen_forward_registry_present", "")
    if frozen:
        metrics["frozen_forward_registry_rows"] = _extract_number(frozen, "rows")
        metrics["frozen_forward_registry_required_rows"] = _extract_number(frozen, "required_rows")

    forward_coverage = gate_evidence.get("forward_market_coverage", "")
    if forward_coverage:
        metrics["forward_markets"] = _extract_number(forward_coverage, "forward_markets")
        metrics["forward_required_markets"] = _extract_number(forward_coverage, "required_markets")

    for key, value in (forward_gate or {}).items():
        metrics[f"forward_gate_{key}"] = value
    if forward_gate:
        metrics.setdefault("rows", forward_gate.get("rows"))
        metrics.setdefault("markets", forward_gate.get("markets"))

    return {key: value for key, value in metrics.items() if value not in (None, "")}


def _status_for_verifier(candidate: dict[str, Any]) -> str:
    verdict = str(candidate.get("verdict") or "").lower()
    if verdict == "promotable":
        return "strong_candidate"
    if candidate.get("failed_gates"):
        return "blocked"
    return "worth_watching"


def _next_action_for_verifier(candidate: dict[str, Any]) -> str:
    verdict = str(candidate.get("verdict") or "").lower()
    failed = set(str(gate) for gate in candidate.get("failed_gates") or [])
    if verdict == "promotable":
        return "Queue for controlled live-test review; require explicit live-order authorization and a separate order gate before any orders."
    if "candidate_is_not_baseline" in failed:
        return "Keep as baseline/control only; do not treat as a successor candidate."
    if any("brier" in gate or "logloss" in gate for gate in failed):
        return "Repair probability-quality baseline failures before any live-test review."
    if "forward_evidence_scored_and_promotable" in failed:
        return "Collect or repair forward evidence before live-test review."
    return "Review failed verifier gates before collecting more rows."


def _scan_promotion_verifier(root: Path, overrides: Overrides, out: AdapterResult) -> None:
    path = root / "logs" / "edge_research" / "v28_successor_promotion_verifier_latest.json"
    parsed, note = safe_load_json(path, max_bytes=10_000_000) if path.exists() else ({}, "")
    payload = parsed if isinstance(parsed, dict) else {}
    if note or not payload:
        out.summary["promotion_verifier_present"] = False
        return

    forward_lookup = _forward_gate_lookup(root)
    count = 0
    for candidate in payload.get("candidates") or []:
        if not isinstance(candidate, dict) or not candidate.get("candidate_id"):
            continue
        count += 1
        candidate_id = str(candidate["candidate_id"])
        variant = str(candidate.get("variant") or "verifier")
        unique_label = f"{candidate_id}_{variant}"
        failed = [str(gate) for gate in candidate.get("failed_gates") or []]
        metrics = _candidate_metrics(candidate, forward_lookup.get(candidate_id, {}))
        node = ProjectNode(
            id=node_id("candidate", FAMILY, unique_label),
            kind="candidate",
            label=f"{candidate_id} / {variant}",
            family=FAMILY,
            status=_status_for_verifier(candidate),
            evidence_level="forward_shadow",
            path=str(path),
            updated_at_utc=path_mtime_iso(path),
            size_bytes=file_size(path),
            metrics=metrics,
            blockers=[f"promotion_verifier_gate_failed:{gate}" for gate in failed],
            next_action=_next_action_for_verifier(candidate),
            tags=["candidate", "v28_successor_verifier", variant],
            source_adapter="v28_successor_candidates_adapter",
            confidence="exact",
            summary=f"v28 successor verifier candidate {candidate_id} in variant {variant}.",
        )
        out.nodes.append(apply_node_overrides(node, overrides))
        out.edges.append(contains_family_edge(FAMILY, node, "v28 successor promotion verifier candidate"))
    out.summary["promotion_verifier_present"] = True
    out.summary["promotion_verifier_candidates"] = count


def _scan_live_pnl_policy(root: Path, overrides: Overrides, out: AdapterResult) -> None:
    score_path = root / "logs" / "edge_research" / "v28_successor_live_pnl_policy_score_latest.json"
    readiness_path = root / "logs" / "edge_research" / "v28_successor_live_pnl_readiness_latest.json"
    score_payload, _score_note = safe_load_json(score_path, max_bytes=10_000_000) if score_path.exists() else ({}, "")
    readiness_payload, _readiness_note = safe_load_json(readiness_path, max_bytes=5_000_000) if readiness_path.exists() else ({}, "")
    score = score_payload if isinstance(score_payload, dict) else {}
    readiness = readiness_payload if isinstance(readiness_payload, dict) else {}
    registry_summary = score.get("registry_summary") if isinstance(score.get("registry_summary"), dict) else {}
    policy_id = registry_summary.get("policy_id")
    if not policy_id:
        out.summary["live_pnl_policy_present"] = False
        return

    primary = {}
    for row in score.get("scores") or []:
        if isinstance(row, dict) and row.get("slice") == "primary_live_forward_rows_after_policy_hash":
            primary = row
            break
    metrics: dict[str, Any] = {
        "policy_id": policy_id,
        "policy_hash": registry_summary.get("policy_hash"),
        "policy_family": (registry_summary.get("policy_spec") or {}).get("policy_family") if isinstance(registry_summary.get("policy_spec"), dict) else "",
        "live_pnl_readiness_verdict": readiness.get("readiness_verdict"),
        "level_1_complete": readiness.get("level_1_complete"),
        "level_2_controlled_live_test_ready": readiness.get("level_2_controlled_live_test_ready"),
        "primary_rows_after_policy_hash": readiness.get("primary_rows_after_policy_hash") or primary.get("rows"),
        "primary_markets_after_policy_hash": readiness.get("primary_markets_after_policy_hash") or primary.get("markets"),
        "primary_entered_rows_after_policy_hash": primary.get("entered_rows"),
        "primary_wins": primary.get("wins"),
        "primary_losses": primary.get("losses"),
        "primary_win_rate": primary.get("win_rate"),
        "primary_delta_vs_v28_cents": primary.get("delta_net_cents_vs_v28"),
        "primary_v28_net_pnl_cents": primary.get("v28_net_pnl_cents"),
        "primary_market_level_lcb_net_cents": primary.get("market_level_lcb_net_cents"),
        "net_pnl": primary.get("net_pnl_cents"),
        "net_pnl_source_key": "v28_successor_live_pnl_policy_score_latest.scores.primary_live_forward_rows_after_policy_hash.net_pnl_cents",
        "net_pnl_unit_hint": "cents",
        "pnl_provenance": "v28_successor_live_pnl_policy_score",
        "pnl_status": "normalized_from_live_pnl_policy_primary_slice",
        "entries": primary.get("entered_rows"),
        "markets": primary.get("markets"),
        "rows": primary.get("rows"),
        "win_rate": primary.get("win_rate"),
    }
    blockers: list[str] = []
    if readiness.get("level_2_controlled_live_test_ready") is False:
        blockers.append("live_pnl_readiness_gate_failed:level_2_controlled_live_test_ready")
    if _safe_float(primary.get("net_pnl_cents")) is not None and (_safe_float(primary.get("net_pnl_cents")) or 0.0) <= 0:
        blockers.append("live_pnl_readiness_gate_failed:primary_net_pnl_nonpositive")
    status = "worth_watching" if readiness.get("level_1_complete") and not blockers[:1] else "blocked"
    node = ProjectNode(
        id=node_id("candidate", FAMILY, str(policy_id)),
        kind="candidate",
        label=str(policy_id),
        family=FAMILY,
        status=status,
        evidence_level="live_forward",
        path=str(score_path),
        updated_at_utc=path_mtime_iso(score_path),
        size_bytes=file_size(score_path),
        metrics={key: value for key, value in metrics.items() if value not in (None, "")},
        blockers=blockers,
        next_action="Continue post-hash no-order live-forward collection until the explicit Level 2 controlled-live-test gate clears.",
        tags=["candidate", "v28_successor_live_pnl_policy"],
        source_adapter="v28_successor_candidates_adapter",
        confidence="exact",
        summary=f"Research-only live-PnL policy candidate {policy_id}.",
    )
    out.nodes.append(apply_node_overrides(node, overrides))
    out.edges.append(contains_family_edge(FAMILY, node, "v28 successor live-PnL policy candidate"))
    out.summary["live_pnl_policy_present"] = True


def scan(root: Path, overrides: Overrides) -> AdapterResult:
    adapter = "v28_successor_candidates_adapter"
    out = result(adapter)
    out.nodes.append(family_node(FAMILY, adapter))
    _scan_promotion_verifier(root, overrides, out)
    _scan_live_pnl_policy(root, overrides, out)
    return out
