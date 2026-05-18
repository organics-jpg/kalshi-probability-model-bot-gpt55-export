from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Any, Mapping, Sequence

from project_os.family import EVIDENCE_RANK
from project_os.models import ProjectNode, ProjectRegistry, utc_now_iso
from project_os.patterns import normalized_metric_snapshot


SCHEMA = "project_os_candidate_readiness_reevaluation_v1"
REPORT_DIR = Path("logs") / "project_os"
JSON_NAME = "candidate_readiness_reevaluation_latest.json"
MD_NAME = "candidate_readiness_reevaluation_latest.md"
RUBRIC_VERSION = "candidate_readiness_v1_balanced_2026_05_18"

FORWARD_EVIDENCE = {"forward_shadow", "live_forward", "live_stats"}
BASELINE_TOKENS = ("baseline", "brier", "logloss", "brownian", "matched_v28", "beats_current", "candidate_is_not_baseline")
SOURCE_TOKENS = ("source_quality", "stale", "fill", "fillability", "accounting", "fee", "reconcile")
SAMPLE_TOKENS = ("underpowered", "insufficient", "fewer_than", "sample_", "markets", "entries", "rows")
NEGATIVE_TOKENS = ("nonpositive", "negative", "pnl_nonpositive", "net_not_positive")


def _safe_float(value: Any) -> float | None:
    if value in (None, "") or isinstance(value, bool):
        return None
    try:
        return float(str(value).strip().replace(",", "").replace("$", "").replace("%", ""))
    except (TypeError, ValueError):
        return None


def _metric(metrics: Mapping[str, Any], *keys: str) -> float | None:
    for key in keys:
        if key in metrics:
            value = _safe_float(metrics.get(key))
            if value is not None:
                return value
    return None


def _metric_bool(metrics: Mapping[str, Any], key: str) -> bool | None:
    value = metrics.get(key)
    if isinstance(value, bool):
        return value
    if isinstance(value, str) and value.lower() in {"true", "false"}:
        return value.lower() == "true"
    return None


def _failure_names(node: ProjectNode) -> list[str]:
    metrics = node.metrics or {}
    failures: list[str] = []
    for key in (
        "promotion_verifier_failed_gates",
        "linked_oos_failed_gates",
        "rv_forward_failed_gates",
        "forward_gate_fail_reasons",
    ):
        value = metrics.get(key)
        if isinstance(value, list):
            failures.extend(str(item) for item in value)
        elif isinstance(value, str) and value:
            failures.extend(part.strip() for part in value.split(";") if part.strip())
    failures.extend(
        str(blocker)
        for blocker in node.blockers or []
        if not str(blocker).startswith("readiness:")
    )
    return list(dict.fromkeys(failures))


def _contains_any(values: Sequence[str], tokens: Sequence[str]) -> bool:
    haystack = " ".join(str(value).lower() for value in values)
    return any(token in haystack for token in tokens)


def _rows_markets_entries(node: ProjectNode, snapshot: Mapping[str, Any]) -> tuple[float | None, float | None, float | None]:
    metrics = node.metrics or {}
    rows = _metric(
        metrics,
        "rows",
        "forward_gate_rows",
        "holdout_rows",
        "source_quality_clean_rows",
        "primary_rows_after_policy_hash",
        "frozen_forward_registry_rows",
    )
    markets = _metric(
        metrics,
        "markets",
        "forward_gate_markets",
        "forward_markets",
        "holdout_markets",
        "source_quality_clean_markets",
        "primary_markets_after_policy_hash",
        "rv_forward_distinct_markets",
    ) or _safe_float(snapshot.get("markets"))
    entries = _metric(
        metrics,
        "entries",
        "entered_rows",
        "primary_entered_rows_after_policy_hash",
        "rv_forward_accepted_entries",
    ) or _safe_float(snapshot.get("entries"))
    return rows, markets, entries


def _pnl_values(node: ProjectNode, snapshot: Mapping[str, Any]) -> tuple[float | None, float | None]:
    metrics = node.metrics or {}
    pnl = _safe_float(snapshot.get("pnl_value"))
    if pnl is None:
        pnl = _metric(metrics, "actual_pnl_source_dollars", "net_pnl_dollars")
    pnl_7d = _safe_float(snapshot.get("pnl_7d_value"))
    return pnl, pnl_7d


def _baseline_ok(metrics: Mapping[str, Any], failures: Sequence[str]) -> bool:
    if _contains_any(failures, BASELINE_TOKENS):
        return False
    delta_brier = _metric(metrics, "forward_gate_delta_brier_candidate_minus_v28")
    delta_logloss = _metric(metrics, "forward_gate_delta_logloss_candidate_minus_v28")
    near_boundary = _metric(metrics, "forward_gate_near_boundary_delta_brier_candidate_minus_v28")
    matched_delta = _metric(metrics, "rv_forward_matched_v28_delta_cents", "primary_delta_vs_v28_cents")
    checks = [value <= 0 for value in (delta_brier, delta_logloss, near_boundary) if value is not None]
    if matched_delta is not None:
        checks.append(matched_delta >= 0)
    return all(checks) if checks else True


def _source_ok(failures: Sequence[str]) -> bool:
    return not _contains_any(failures, SOURCE_TOKENS)


def _sample_quality(rows: float | None, markets: float | None, entries: float | None) -> tuple[str, bool, bool]:
    enough_for_controlled = (
        (markets is not None and markets >= 20 and rows is not None and rows >= 100)
        or (markets is not None and markets >= 12 and entries is not None and entries >= 20)
    )
    enough_for_shadow = (
        (markets is not None and markets >= 8)
        or (rows is not None and rows >= 50)
        or (entries is not None and entries >= 10)
    )
    if enough_for_controlled:
        return "controlled_sample_ok", True, True
    if enough_for_shadow:
        return "shadow_sample_ok", False, True
    return "sample_too_thin", False, False


def evaluate_candidate(node: ProjectNode) -> dict[str, Any]:
    metrics = node.metrics or {}
    snapshot = normalized_metric_snapshot(node)
    failures = _failure_names(node)
    rows, markets, entries = _rows_markets_entries(node, snapshot)
    pnl, pnl_7d = _pnl_values(node, snapshot)
    evidence_ok = node.evidence_level in FORWARD_EVIDENCE
    live_forward = node.evidence_level == "live_forward"
    pnl_positive = pnl is not None and pnl > 0
    pnl_missing = pnl is None
    baseline_ok = _baseline_ok(metrics, failures)
    source_ok = _source_ok(failures)
    sample_label, controlled_sample_ok, shadow_sample_ok = _sample_quality(rows, markets, entries)
    explicit_promotable = str(metrics.get("promotion_verifier_verdict") or "").lower() == "promotable"
    forward_promotable = _metric_bool(metrics, "forward_gate_forward_evidence_promotable") is True
    level_2 = _metric_bool(metrics, "level_2_controlled_live_test_ready")
    level_1 = _metric_bool(metrics, "level_1_complete")
    baseline_control_only = any("candidate_is_not_baseline" in str(failure) for failure in failures)
    nonpositive_failure = _contains_any(failures, NEGATIVE_TOKENS) or (pnl is not None and pnl <= 0)
    sample_failure = _contains_any(failures, SAMPLE_TOKENS) and not controlled_sample_ok

    score = 0
    score += 25 if live_forward else 20 if evidence_ok else 0
    score += 20 if pnl_positive else 0
    score += 15 if controlled_sample_ok else 8 if shadow_sample_ok else 0
    score += 20 if baseline_ok else 0
    score += 10 if source_ok else 0
    score += 10 if explicit_promotable or forward_promotable else 0
    if pnl_7d is not None and pnl_7d > 0:
        score += 5
    if nonpositive_failure:
        score -= 30
    if not baseline_ok:
        score -= 20
    if not source_ok:
        score -= 15
    if sample_failure:
        score -= 8
    if baseline_control_only:
        score -= 35
    score = max(0, min(100, score))

    readiness_blockers: list[str] = []
    if not evidence_ok:
        readiness_blockers.append("readiness:evidence_not_forward_or_live")
    if pnl_missing:
        readiness_blockers.append("readiness:pnl_missing")
    elif not pnl_positive:
        readiness_blockers.append("readiness:pnl_not_positive")
    if not controlled_sample_ok:
        if shadow_sample_ok:
            readiness_blockers.append("readiness:sample_below_controlled_live_test_threshold")
        else:
            readiness_blockers.append("readiness:sample_too_thin")
    if not baseline_ok:
        readiness_blockers.append("readiness:baseline_or_calibration_failed")
    if not source_ok:
        readiness_blockers.append("readiness:source_fill_or_accounting_blocker")
    if level_2 is False:
        readiness_blockers.append("readiness:explicit_level_2_controlled_live_test_false")

    controlled_ready = (
        evidence_ok
        and pnl_positive
        and baseline_ok
        and source_ok
        and (controlled_sample_ok or explicit_promotable)
        and not nonpositive_failure
        and level_2 is not False
        and (explicit_promotable or forward_promotable or not failures)
    )
    live_shadow_ready = (
        not controlled_ready
        and evidence_ok
        and pnl_positive
        and baseline_ok
        and source_ok
        and shadow_sample_ok
        and not nonpositive_failure
    )
    if baseline_control_only:
        readiness_level = "baseline_control_only"
        status_update = "blocked"
        next_action = "Keep as a baseline/control row only; do not advance as a live-test candidate."
    elif controlled_ready:
        readiness_level = "controlled_live_test_ready"
        status_update = "strong_candidate"
        next_action = "Queue for controlled live-test review; keep order authorization as a separate explicit gate."
    elif live_shadow_ready:
        readiness_level = "live_shadow_ready"
        status_update = "worth_watching"
        next_action = "Continue no-order live-forward collection and resolve remaining readiness blockers before controlled live testing."
    elif pnl_positive and evidence_ok:
        readiness_level = "near_miss_review"
        status_update = "needs_more_proof"
        next_action = "Keep under review, but fix the named sample, baseline, or source blocker before live-test review."
    elif nonpositive_failure:
        readiness_level = "blocked_nonpositive"
        status_update = "blocked"
        next_action = "Do not repeat as-is; redesign the mechanism before collecting more evidence."
    else:
        readiness_level = "blocked"
        status_update = "blocked"
        next_action = "Do not advance until the readiness blockers are repaired or reclassified."

    if level_1 is True and level_2 is False and pnl_positive:
        next_action = "Level 1 bootstrap is complete; continue post-hash no-order collection until Level 2 controlled-live-test criteria are explicitly met."

    metric_update = {
        "readiness_rubric_version": RUBRIC_VERSION,
        "readiness_level": readiness_level,
        "readiness_score": round(score, 2),
        "live_ready_for_testing": controlled_ready,
        "controlled_live_test_ready": controlled_ready,
        "live_shadow_ready": live_shadow_ready,
        "live_order_ready": False,
        "readiness_evidence_ok": evidence_ok,
        "readiness_pnl_positive": pnl_positive,
        "readiness_baseline_ok": baseline_ok,
        "readiness_source_ok": source_ok,
        "readiness_sample_quality": sample_label,
        "readiness_rows": rows,
        "readiness_markets": markets,
        "readiness_entries": entries,
        "readiness_source_pnl_dollars": pnl,
        "readiness_pnl_7d_dollars": pnl_7d,
        "readiness_failure_count": len(failures),
        "readiness_original_status": node.status,
        "readiness_original_evidence_level": node.evidence_level,
        "readiness_blockers": readiness_blockers,
        "readiness_failed_metrics": failures[:20],
    }

    return {
        "node_id": node.id,
        "label": node.label,
        "family": node.family,
        "status_update": status_update,
        "evidence_level": node.evidence_level,
        "readiness_level": readiness_level,
        "readiness_score": round(score, 2),
        "live_ready_for_testing": controlled_ready,
        "controlled_live_test_ready": controlled_ready,
        "live_shadow_ready": live_shadow_ready,
        "live_order_ready": False,
        "metrics_update": {key: value for key, value in metric_update.items() if value is not None},
        "blockers": readiness_blockers,
        "source_failures": failures[:30],
        "next_action": next_action,
    }


def evaluate_candidates(registry: ProjectRegistry) -> list[dict[str, Any]]:
    rows = [evaluate_candidate(node) for node in registry.nodes if node.kind == "candidate"]
    return sorted(rows, key=lambda row: (-float(row["readiness_score"]), str(row["family"]), str(row["label"]).lower()))


def build_payload(registry: ProjectRegistry) -> dict[str, Any]:
    candidates = evaluate_candidates(registry)
    counts = Counter(row["readiness_level"] for row in candidates)
    live_ready = [row for row in candidates if row["controlled_live_test_ready"]]
    shadow_ready = [row for row in candidates if row["live_shadow_ready"]]
    return {
        "schema": SCHEMA,
        "generated_at_utc": utc_now_iso(),
        "registry_generated_at_utc": registry.generated_at_utc,
        "research_only": True,
        "rubric": {
            "version": RUBRIC_VERSION,
            "intent": "Balanced same-metric review for all Research OS candidate nodes.",
            "not_too_strict_notes": [
                "Forward-shadow evidence is acceptable for controlled live-test review; live_stats are not required at this stage.",
                "A controlled sample can pass with either 20 markets and 100 rows or 12 markets and 20 entries.",
                "Positive 7d P&L is used as a ranking rate, while source-window P&L, baseline comparison, source quality, and blockers decide readiness.",
                "Live-order readiness remains a separate explicit gate and is never inferred by this report.",
            ],
            "hard_requirements": [
                "forward or live evidence",
                "positive source P&L",
                "reasonable sample breadth",
                "no unresolved baseline/calibration failure",
                "no source, fillability, fee, or accounting blocker",
            ],
        },
        "summary": {
            "candidate_count": len(candidates),
            "controlled_live_test_ready_count": len(live_ready),
            "live_shadow_ready_count": len(shadow_ready),
            "readiness_level_counts": dict(counts),
            "live_order_ready_count": 0,
        },
        "candidates": candidates,
    }


def render_markdown(payload: Mapping[str, Any]) -> str:
    summary = payload.get("summary") if isinstance(payload.get("summary"), Mapping) else {}
    candidates = list(payload.get("candidates") or [])
    lines = [
        "# Candidate Readiness Reevaluation",
        "",
        f"Generated UTC: {payload.get('generated_at_utc', '')}",
        "",
        "Scope: research-only same-rubric reevaluation of every current Research OS candidate node. This file does not authorize live orders.",
        "",
        "## Summary",
        "",
        f"- Candidate nodes evaluated: {summary.get('candidate_count', 0)}",
        f"- Controlled live-test ready: {summary.get('controlled_live_test_ready_count', 0)}",
        f"- Live-shadow ready: {summary.get('live_shadow_ready_count', 0)}",
        f"- Live-order ready: {summary.get('live_order_ready_count', 0)}",
        "",
        "## Rubric",
        "",
    ]
    rubric = payload.get("rubric") if isinstance(payload.get("rubric"), Mapping) else {}
    for note in rubric.get("not_too_strict_notes") or []:
        lines.append(f"- {note}")
    lines.extend(["", "## Candidate Results", ""])
    lines.append("| readiness | score | candidate | family | next action |")
    lines.append("|---|---:|---|---|---|")
    for row in candidates:
        lines.append(
            "| {level} | {score:.1f} | `{label}` | `{family}` | {action} |".format(
                level=row.get("readiness_level", ""),
                score=float(row.get("readiness_score") or 0.0),
                label=row.get("label", ""),
                family=row.get("family", ""),
                action=str(row.get("next_action", "")).replace("|", "\\|"),
            )
        )
    lines.extend(["", "## Research Guardrail", "", "Live-order readiness is always false in this report unless a separate explicit live-order gate is implemented and approved."])
    return "\n".join(lines).rstrip() + "\n"


def output_paths(root: str | Path) -> tuple[Path, Path]:
    root_path = Path(root)
    return root_path / REPORT_DIR / JSON_NAME, root_path / REPORT_DIR / MD_NAME


def write_candidate_readiness(registry: ProjectRegistry, root: str | Path | None = None) -> tuple[Path, Path, dict[str, Any]]:
    root_path = Path(root or registry.root or ".")
    json_path, md_path = output_paths(root_path)
    payload = build_payload(registry)
    json_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    md_path.write_text(render_markdown(payload), encoding="utf-8")
    return json_path, md_path, payload
