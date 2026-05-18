from __future__ import annotations

import re
import math
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Iterable

from project_os.family import EVIDENCE_RANK, STATUS_LABELS, STATUS_RANK
from project_os.models import ProjectNode, ProjectRegistry


MOTIF_RULES: tuple[tuple[str, str, tuple[str, ...]], ...] = (
    ("forward_oos", "Forward/OOS proof", ("forward", "shadow", "oos", "locked", "lock")),
    ("live_stats", "Live/stat evidence", ("live", "stats", "score", "scorer", "exchange")),
    ("rv_vol", "Realized-vol / RV", ("rv600", "realized", "residual", "terminal", "rvterm", "vol")),
    ("sidecar_slice", "Sidecar / slice", ("sidecar", "slice", "pslice", "paired")),
    ("consensus_vote", "Consensus / ensemble", ("consensus", "ensemble", "vote", "gauss", "blend")),
    ("common_clock", "Common-clock v28", ("common_clock", "mushroom_v28", "v28", "clock")),
    ("phi_memory", "Phi reward memory", ("phi_reward", "memory", "lifecycle", "reward")),
    ("exit_risk", "Exit / risk control", ("exit", "guard", "toll", "risk", "kill", "policy", "lifecycle")),
    ("fill_quality", "Fillability / source quality", ("fill", "fillability", "source_quality", "source quality", "book", "reconcile")),
    ("accounting", "Accounting / fee integrity", ("accounting", "fee", "fees", "pnl_rule", "settlement", "raw_fill")),
    ("touch_threshold", "Touch / threshold", ("90_touch", "ninety", "touch", "threshold")),
    ("mispricing_ou", "OU / mispricing", ("ou_", "ou-", "mispricing", "carr", "lopez")),
    ("backtest_replay", "Replay / backtest", ("replay", "backtest", "sweep", "probe", "diagnostic", "audit")),
    ("baseline_compare", "Baseline comparison", ("baseline", "matched_v28", "beat_v28", "brier", "logloss")),
    ("underpowered", "Underpowered sample", ("underpowered", "fewer_than", "below_60", "single_market", "low_positive")),
)

MOTIF_COLORS = {
    "forward_oos": "#39d2ff",
    "live_stats": "#2dd4bf",
    "rv_vol": "#38bdf8",
    "sidecar_slice": "#a78bfa",
    "consensus_vote": "#fbbf24",
    "common_clock": "#22c55e",
    "phi_memory": "#84cc16",
    "exit_risk": "#fb7185",
    "fill_quality": "#f97316",
    "accounting": "#f59e0b",
    "touch_threshold": "#2dd4bf",
    "mispricing_ou": "#f59e0b",
    "backtest_replay": "#94a3b8",
    "baseline_compare": "#c084fc",
    "underpowered": "#f43f5e",
}

FAILURE_RULES: tuple[tuple[str, tuple[str, ...], str, str], ...] = (
    ("positive_roots_below_60pct", ("positive_roots_below_60pct", "positive roots below 60", "roots_below_60"), "Root-level edge is too concentrated or inconsistent.", "Raise positive root fraction with a pre-registered rule."),
    ("positive_markets_below_60pct", ("positive_markets_below_60pct", "positive markets below 60", "markets_below_60"), "Market breadth is too weak for proof.", "Improve breadth before treating P&L as evidence."),
    ("single_market_share_above_25pct", ("single_market_share_above_25pct", "single market share", "concentration"), "Result may be carried by one market.", "Cap concentration or retest on a broader window."),
    ("avg_entry_below_10c", ("avg_entry_below_10c", "avg entry below 10", "entry_below_10"), "Average entry count is too small.", "Increase fillable entry count before comparing families."),
    ("last_window_nonpositive", ("last_window_nonpositive", "last window nonpositive", "recent window nonpositive"), "The newest evidence window did not stay positive.", "Collect a cleaner forward window or change the timing rule."),
    ("nonpositive_pnl", ("nonpositive_pnl", "negative pnl", "nonpositive pnl", "pnl <= 0"), "Profitability is not positive after the reported accounting.", "Do not repeat without changing the core mechanism."),
    ("fewer_than_25_entries", ("fewer_than_25_entries", "fewer than 25", "entries < 25"), "Sample has too few entries.", "Get a larger pre-registered sample."),
    ("does_not_beat_matched_v28_by_20pct", ("does_not_beat_matched_v28_by_20pct", "does_not_beat_v28", "matched_v28_by_20", "beat matched v28"), "It did not clear the matched baseline hurdle.", "Change the edge source or baseline comparison, not just parameters."),
    ("beats_baseline_brier", ("beats_baseline_brier", "brier"), "Baseline comparison depends on Brier behavior.", "Separate calibration win from tradeable P&L proof."),
    ("beats_baseline_logloss", ("beats_baseline_logloss", "logloss"), "Baseline comparison depends on logloss behavior.", "Separate probability-quality evidence from execution evidence."),
    ("low_positive_market_fraction", ("low_positive_market_fraction", "low positive market", "positive_market_fraction"), "Too few markets are positive.", "Broaden the rule or pre-define a narrower eligible set."),
    ("underpowered_markets", ("underpowered_markets", "underpowered", "too few markets"), "Market sample is underpowered.", "Collect more markets before ranking this family."),
    ("trajectory_blocked_shadow_only", ("trajectory_blocked_shadow_only", "trajectory blocked", "shadow only trajectory"), "Shadow evidence is not enough to claim readiness.", "Run a forward validation path with explicit accounting."),
    ("shadow_only", ("shadow_only", "shadow only", "forward shadow only"), "Evidence is shadow-only.", "Add live/stat or exchange-reconciled validation."),
    ("source_quality", ("source_quality", "source quality", "stale book", "native passive", "backfill"), "Input source quality is limiting confidence.", "Fix or isolate the source-quality assumption."),
    ("fillability", ("fillability", "would_fill", "liquidity", "book gap", "spread"), "Fillability is not proven.", "Validate fills or model slippage before expansion."),
    ("accounting", ("accounting", "fee", "fees", "reconcile", "settlement"), "Accounting or fee treatment is unresolved.", "Reconcile fees/fills before treating the result as proof."),
)

POSITIVE_STATUSES = {"strong_candidate", "worth_watching", "active"}
NEGATIVE_STATUSES = {"blocked", "rejected"}
BLOCKING_STATUSES = {"blocked", "rejected", "diagnostic_only"}
DECISION_KINDS = {"candidate", "report", "stats"}
SEMANTIC_EDGE_TYPES = {"blocks", "rejects", "supersedes", "validates", "depends_on", "documents", "uses", "scores"}
SUPPORT_FAMILIES = {"dashboard_ui", "infrastructure", "research_os"}


@dataclass(frozen=True)
class MotifSummary:
    motif: str
    label: str
    families: str
    nodes: int
    candidates: int
    positive: int
    blocked_rejected: int
    best_status: str
    best_evidence: str
    best_pnl: float
    repeat_pressure: float
    examples: str
    guidance: str


def _safe_numeric(value: Any) -> float | None:
    if value in (None, ""):
        return None
    try:
        text = str(value).strip().replace(",", "").replace("$", "").replace("%", "")
        if text.startswith("(") and text.endswith(")"):
            text = "-" + text[1:-1]
        return float(text)
    except (TypeError, ValueError):
        return None


def _numeric_or_zero(value: Any) -> float:
    return _safe_numeric(value) or 0.0


def _flatten_metrics(metrics: dict[str, Any], prefix: str = "") -> dict[str, Any]:
    flat: dict[str, Any] = {}
    for key, value in (metrics or {}).items():
        full_key = f"{prefix}.{key}" if prefix else str(key)
        if isinstance(value, dict):
            flat.update(_flatten_metrics(value, full_key))
        else:
            flat[full_key] = value
    return flat


def _is_auxiliary_metric_key(key: str) -> bool:
    lowered = key.lower()
    return any(token in lowered for token in ("required", "shortfall", "additional", "estimated", "_needed", "minimum"))


def _first_metric(flat: dict[str, Any], needles: tuple[str, ...]) -> tuple[str | None, Any]:
    for needle in needles:
        for key in sorted(flat):
            lowered = key.lower()
            leaf = lowered.rsplit(".", 1)[-1]
            if leaf == needle:
                value = flat[key]
                if _safe_numeric(value) is not None:
                    return key, value
        for key in sorted(flat):
            lowered = key.lower()
            if needle in lowered and not _is_auxiliary_metric_key(lowered):
                value = flat[key]
                if _safe_numeric(value) is not None:
                    return key, value
    return None, None


def _format_decimal(value: float) -> str:
    return f"{value:.2f}".rstrip("0").rstrip(".")


def _format_days(value: float | None) -> str:
    if value is None:
        return ""
    if value >= 1:
        return f"{_format_decimal(value)}d"
    return f"{_format_decimal(value * 24)}h"


def _is_standardized_pnl_key(key: str) -> bool:
    lowered = key.lower()
    return (
        lowered.startswith(("pnl_7d", "actual_pnl_7d", "projected_pnl_7d"))
        or lowered in {"pnl_observed_window_days", "pnl_7d_basis", "pnl_7d_method", "pnl_7d_warning"}
        or lowered.startswith("pnl_observed_window_")
        or lowered.startswith("pnl_standardization_")
    )


def _is_comparison_pnl_key(key: str) -> bool:
    lowered = key.lower()
    return any(
        token in lowered
        for token in (
            "v28_net_pnl",
            "baseline_net_pnl",
            "always_skip_net_pnl",
            "book_only_net_pnl",
            "successor_fv_only_net_pnl",
            "delta_net",
            "delta_vs",
            "matched_v28_delta",
        )
    )


def normalized_metric_snapshot(node: ProjectNode) -> dict[str, Any]:
    flat = _flatten_metrics(node.metrics or {})
    raw_flat = {key: value for key, value in flat.items() if not _is_standardized_pnl_key(key)}
    pnl_flat = {key: value for key, value in raw_flat.items() if not _is_comparison_pnl_key(key)}
    warnings: list[str] = []

    pnl_priorities = (
        ("net_after_fee", "after_fee", "after_fees", "net_pnl_total_dollars", "net_pnl_dollars", "selected_pnl_dollars"),
        ("selected_pnl_cents", "net_pnl_cents", "pnl_cents", "profit_cents"),
        ("net_pnl", "selected_pnl", "pnl", "profit"),
        ("gross_pnl", "gross_profit"),
    )
    pnl_key: str | None = None
    raw_value: Any = None
    for needles in pnl_priorities:
        pnl_key, raw_value = _first_metric(pnl_flat, needles)
        if pnl_key:
            break

    pnl_value: float | None = None
    pnl_unit = "missing"
    pnl_display = "n/a"
    pnl_confidence = "none"

    if pnl_key:
        raw_num = _safe_numeric(raw_value)
        lowered = pnl_key.lower()
        base_key = lowered.rsplit(".", 1)[-1]
        source_key = str(raw_flat.get(f"{pnl_key}_source_key", "") or raw_flat.get(f"{base_key}_source_key", "") or "").lower()
        unit_hint = str(raw_flat.get(f"{pnl_key}_unit_hint", "") or raw_flat.get(f"{base_key}_unit_hint", "") or "").lower()
        unit_text = " ".join([lowered, source_key, unit_hint])
        is_gross = "gross" in lowered and "net" not in lowered
        if raw_num is not None:
            if "cent" in unit_text:
                pnl_value = raw_num / 100.0
                pnl_unit = "cents"
                pnl_display = f"{_format_decimal(raw_num)}c (~${pnl_value:.2f})"
                pnl_confidence = "high"
            elif any(unit in unit_text for unit in ("dollar", "usd")) or "after_fee" in lowered or "after_fees" in lowered:
                pnl_value = raw_num
                pnl_unit = "dollars"
                pnl_display = f"${pnl_value:.2f}"
                pnl_confidence = "high"
            elif is_gross:
                pnl_value = raw_num
                pnl_unit = "ambiguous"
                pnl_display = f"{_format_decimal(raw_num)} raw"
                pnl_confidence = "low"
                warnings.append(f"gross P&L metric {pnl_key} is not net-after-fee proof")
            else:
                pnl_value = raw_num
                pnl_unit = "ambiguous"
                pnl_display = f"{_format_decimal(raw_num)} raw"
                pnl_confidence = "low"
                warnings.append(f"ambiguous P&L unit for {pnl_key}={raw_value!r}")

    entries_key, entries_raw = _first_metric(flat, ("entries_total", "entry_count", "entries", "fills", "trade_count", "trades"))
    markets_key, markets_raw = _first_metric(flat, ("markets_total", "market_count", "markets", "positive_markets"))
    roots_key, roots_raw = _first_metric(flat, ("roots_total", "root_count", "roots"))
    win_key, win_raw = _first_metric(flat, ("win_rate", "positive_market_fraction", "hit_rate"))
    win_rate = _safe_numeric(win_raw)
    if win_rate is not None and 0 < win_rate <= 1:
        win_rate *= 100.0

    pnl_status = str(flat.get("pnl_status", "") or "")
    pnl_missing_reason = str(flat.get("pnl_missing_reason", "") or "")
    pnl_provenance = str(flat.get("pnl_provenance", "") or "")
    pnl_source_node_id = str(flat.get("pnl_source_node_id", "") or flat.get("pnl_inferred_from_node", "") or "")
    pnl_standardization_status = str(flat.get("pnl_standardization_status", "") or "")
    pnl_7d_basis = str(flat.get("pnl_7d_basis", "") or "")
    pnl_7d_warning = str(flat.get("pnl_7d_warning", "") or "")
    pnl_7d_value = _safe_numeric(
        flat.get("pnl_7d_dollars")
        if flat.get("pnl_7d_dollars") not in (None, "")
        else flat.get("projected_pnl_7d_dollars")
        if flat.get("projected_pnl_7d_dollars") not in (None, "")
        else flat.get("actual_pnl_7d_dollars")
    )
    pnl_7d_display = str(flat.get("pnl_7d_display", "") or "")
    if pnl_7d_value is not None and not pnl_7d_display:
        pnl_7d_display = f"${pnl_7d_value:.2f}"
    pnl_observed_window_days = _safe_numeric(flat.get("pnl_observed_window_days"))
    pnl_observed_window_source = str(flat.get("pnl_observed_window_source", "") or "")
    pnl_observed_window_confidence = str(flat.get("pnl_observed_window_confidence", "") or "")
    window_display = _format_days(pnl_observed_window_days)
    if window_display and pnl_observed_window_confidence:
        window_display = f"{window_display} ({pnl_observed_window_confidence})"
    if pnl_7d_warning and pnl_7d_warning not in warnings:
        warnings.append(pnl_7d_warning)

    if not pnl_key and (flat or node.kind in DECISION_KINDS):
        warnings.append(pnl_missing_reason or pnl_status or "no P&L-like metric found")

    return {
        "pnl_value": pnl_value,
        "pnl_display": pnl_display,
        "pnl_unit": pnl_unit,
        "pnl_key": pnl_key or "",
        "pnl_confidence": pnl_confidence,
        "pnl_7d_value": pnl_7d_value,
        "pnl_7d_display": pnl_7d_display,
        "pnl_7d_basis": pnl_7d_basis,
        "pnl_7d_method": str(flat.get("pnl_7d_method", "") or ""),
        "pnl_7d_warning": pnl_7d_warning,
        "pnl_standardization_status": pnl_standardization_status,
        "pnl_observed_window_days": pnl_observed_window_days,
        "pnl_observed_window_source": pnl_observed_window_source,
        "pnl_observed_window_confidence": pnl_observed_window_confidence,
        "pnl_window_display": window_display,
        "pnl_status": pnl_status,
        "pnl_provenance": pnl_provenance,
        "pnl_source_node_id": pnl_source_node_id,
        "entries": int(_numeric_or_zero(entries_raw)) if entries_key else None,
        "markets": int(_numeric_or_zero(markets_raw)) if markets_key else None,
        "roots": int(_numeric_or_zero(roots_raw)) if roots_key else None,
        "win_rate": round(win_rate, 2) if win_rate is not None else None,
        "metric_warnings": warnings,
    }


def candidate_visual_quality(node: ProjectNode) -> dict[str, Any]:
    """Return a deterministic visual quality score for candidate atlas rendering."""
    if node.kind != "candidate":
        return {
            "score": 0.0,
            "label": "",
            "pnl_display": "",
            "pnl_confidence": "none",
            "has_pnl": False,
            "blocked_positive": False,
        }
    snapshot = normalized_metric_snapshot(node)
    raw_pnl_value = snapshot.get("pnl_value")
    pnl_value = snapshot.get("pnl_7d_value")
    if pnl_value is None:
        pnl_value = raw_pnl_value
    has_pnl = pnl_value is not None
    pnl_score = 0.0
    if has_pnl:
        magnitude = min(1.0, math.log1p(abs(float(pnl_value))) / math.log1p(250.0))
        pnl_score = magnitude if float(pnl_value) > 0 else -magnitude
        if snapshot.get("pnl_confidence") != "high":
            pnl_score *= 0.45
    status_score = {
        "strong_candidate": 0.38,
        "worth_watching": 0.28,
        "active": 0.16,
        "needs_more_proof": 0.06,
        "diagnostic_only": -0.02,
        "unknown": 0.0,
        "archived": -0.10,
        "blocked": -0.18,
        "rejected": -0.38,
    }.get(node.status, 0.0)
    evidence_rank = EVIDENCE_RANK.get(node.evidence_level, 0)
    evidence_score = min(0.18, max(0, evidence_rank - EVIDENCE_RANK["metadata_only"]) * 0.03)
    blocker_penalty = min(0.30, 0.12 * len(node.blockers or []))
    tags = set(node_pattern_tags(node))
    blocked_positive = bool(
        has_pnl
        and float(pnl_value) > 0
        and (
            node.status in BLOCKING_STATUSES
            or node.blockers
            or tags.intersection({"source_quality", "fill_quality", "fillability", "accounting", "underpowered", "baseline_compare"})
        )
    )
    trap_penalty = 0.22 if blocked_positive else 0.0
    score = max(-1.0, min(1.0, pnl_score * 0.66 + status_score + evidence_score - blocker_penalty - trap_penalty))
    if score >= 0.72:
        label = "excellent"
    elif score >= 0.38:
        label = "positive"
    elif score >= 0.14:
        label = "watch"
    elif score > -0.14:
        label = "neutral"
    elif score > -0.38:
        label = "weak"
    elif score > -0.72:
        label = "bad"
    else:
        label = "awful"
    return {
        "score": round(score, 3),
        "label": label,
        "pnl_display": snapshot.get("pnl_display") or "n/a",
        "pnl_7d_display": snapshot.get("pnl_7d_display") or "",
        "pnl_confidence": snapshot.get("pnl_confidence") or "none",
        "has_pnl": has_pnl,
        "blocked_positive": blocked_positive,
    }


def _pnl_value(node: ProjectNode) -> float:
    snapshot = normalized_metric_snapshot(node)
    value = snapshot.get("pnl_7d_value")
    if value is None:
        value = snapshot.get("pnl_value")
    return float(value or 0.0)


def _node_text(node: ProjectNode) -> str:
    metric_keys = " ".join((node.metrics or {}).keys())
    metric_values = " ".join(str(value) for value in (node.metrics or {}).values())
    values = [
        node.id,
        node.label,
        node.family,
        node.kind,
        node.status,
        node.evidence_level,
        node.source_adapter,
        node.summary,
        node.next_action,
        node.path or "",
        " ".join(node.tags or []),
        " ".join(node.blockers or []),
        metric_keys,
        metric_values,
    ]
    return _normalize_text(" ".join(values))


def _normalize_text(value: str) -> str:
    return str(value or "").lower().replace("-", "_").replace("/", "_").replace("\\", "_")


def _tokens(value: str, limit: int = 14) -> tuple[str, ...]:
    raw = re.findall(r"[a-z0-9_]{3,}", _normalize_text(value))
    stop = {
        "the",
        "and",
        "for",
        "with",
        "from",
        "that",
        "this",
        "latest",
        "report",
        "candidate",
        "strategy",
        "research",
        "json",
        "score",
    }
    counts = Counter(token for token in raw if token not in stop and not re.fullmatch(r"\d{8,}", token))
    return tuple(token for token, _count in sorted(counts.items(), key=lambda item: (-item[1], item[0]))[:limit])


def _failure_motifs_for_text(text: str) -> list[str]:
    normalized = _normalize_text(text)
    motifs: list[str] = []
    for motif, needles, _meaning, _change in FAILURE_RULES:
        if any(_normalize_text(needle) in normalized for needle in needles):
            motifs.append(motif)
    return sorted(dict.fromkeys(motifs))


def _failure_motifs_for_node(node: ProjectNode) -> list[str]:
    blocker_text = " ".join(node.blockers or [])
    if not blocker_text and node.status in BLOCKING_STATUSES:
        blocker_text = f"{node.status} {node.summary} {node.next_action}"
    return _failure_motifs_for_text(blocker_text)


def node_pattern_tags(node: ProjectNode) -> list[str]:
    text = _node_text(node)
    tags: list[str] = []
    if node.evidence_level == "forward_shadow":
        tags.append("forward_oos")
    if node.evidence_level in {"live_stats", "live_forward"}:
        tags.append("live_stats")
    for motif, _label, needles in MOTIF_RULES:
        if motif in tags:
            continue
        if any(_normalize_text(needle) in text for needle in needles):
            tags.append(motif)
    for failure in _failure_motifs_for_node(node):
        if failure in {"source_quality", "fillability", "accounting"} and failure not in tags:
            tags.append(failure)
        elif failure in {"underpowered_markets", "fewer_than_25_entries", "positive_markets_below_60pct", "positive_roots_below_60pct"} and "underpowered" not in tags:
            tags.append("underpowered")
        elif failure in {"does_not_beat_matched_v28_by_20pct", "beats_baseline_brier", "beats_baseline_logloss"} and "baseline_compare" not in tags:
            tags.append("baseline_compare")
    if not tags and node.family and node.family != "unclassified":
        tags.append(node.family)
    return sorted(dict.fromkeys(tags))[:8]


def _best_status(nodes: Iterable[ProjectNode]) -> str:
    return max((node.status for node in nodes), key=lambda status: STATUS_RANK.get(status, 0), default="unknown")


def _best_evidence(nodes: Iterable[ProjectNode]) -> str:
    return max((node.evidence_level for node in nodes), key=lambda evidence: EVIDENCE_RANK.get(evidence, 0), default="unknown")


def _examples(nodes: list[ProjectNode], limit: int = 3) -> str:
    ranked = sorted(
        nodes,
        key=lambda node: (STATUS_RANK.get(node.status, 0), EVIDENCE_RANK.get(node.evidence_level, 0), _pnl_value(node), node.label),
        reverse=True,
    )
    return ", ".join(node.label[:42] for node in ranked[:limit])


def _motif_guidance(summary: MotifSummary | dict[str, Any]) -> str:
    if isinstance(summary, dict):
        positive = int(summary.get("positive", summary.get("Watch/active", 0)) or 0)
        blocked = int(summary.get("blocked_rejected", summary.get("Blocked/rejected", 0)) or 0)
        best_evidence = str(summary.get("best_evidence", summary.get("Best Evidence", "unknown")) or "unknown").lower().replace(" ", "_")
        candidates = int(summary.get("candidates", summary.get("Candidates", 0)) or 0)
    else:
        positive = summary.positive
        blocked = summary.blocked_rejected
        best_evidence = summary.best_evidence
        candidates = summary.candidates
    if positive and EVIDENCE_RANK.get(best_evidence, 0) >= EVIDENCE_RANK["live_stats"]:
        return "Reuse this motif, but vary one assumption and keep forward scoring strict."
    if positive:
        return "Promising motif; collect forward/live evidence before expanding variants."
    if blocked >= max(2, candidates):
        return "Do not rerun blindly; require a new mechanism or blocker fix first."
    if candidates == 0:
        return "Mostly artifact evidence; convert to a named candidate before judging."
    return "Sparse signal; map lineage before adding another variant."


def _evidence_bucket(evidence: str) -> str:
    if evidence in {"live_forward", "forward_shadow"}:
        return "forward"
    if evidence == "live_stats":
        return "live_stats"
    if evidence in {"replay", "backtest", "diagnostic"}:
        return "diagnostic"
    return evidence or "unknown"


def _metric_shape_tokens(node: ProjectNode) -> tuple[str, ...]:
    flat = _flatten_metrics(node.metrics or {})
    shape: list[str] = []
    for key in sorted(flat):
        lowered = key.lower()
        if any(piece in lowered for piece in ("pnl", "profit")):
            if "gross" in lowered:
                shape.append("gross_pnl")
            elif "cent" in lowered:
                shape.append("pnl_cents")
            elif "dollar" in lowered or "usd" in lowered:
                shape.append("pnl_dollars")
            else:
                shape.append("pnl_ambiguous")
        elif "market" in lowered:
            shape.append("markets")
        elif "entry" in lowered or "trade" in lowered or "fill" in lowered:
            shape.append("entries")
        elif "root" in lowered:
            shape.append("roots")
        elif "win" in lowered or "positive" in lowered:
            shape.append("win_rate")
    return tuple(sorted(set(shape))[:8])


def candidate_signature(node: ProjectNode) -> str:
    label_tokens = _tokens(node.label, 8)
    summary_tokens = _tokens(f"{node.summary} {node.next_action}", 8)
    blocker_tokens = _tokens(" ".join(node.blockers or []), 8)
    parts = {
        "family": node.family or "unclassified",
        "kind": node.kind or "unknown",
        "evidence": _evidence_bucket(node.evidence_level),
        "motifs": ",".join(node_pattern_tags(node)),
        "tokens": ",".join(sorted(set(label_tokens + summary_tokens))[:14]),
        "blockers": ",".join(blocker_tokens),
        "metrics": ",".join(_metric_shape_tokens(node)),
    }
    return "|".join(f"{key}={parts[key]}" for key in ("family", "kind", "evidence", "motifs", "tokens", "blockers", "metrics"))


def _parse_signature(signature: str | ProjectNode | dict[str, Any]) -> dict[str, Any]:
    if isinstance(signature, ProjectNode):
        signature = candidate_signature(signature)
    if isinstance(signature, dict):
        return signature
    parsed: dict[str, Any] = {}
    for piece in str(signature or "").split("|"):
        if "=" not in piece:
            continue
        key, value = piece.split("=", 1)
        if key in {"motifs", "tokens", "blockers", "metrics"}:
            parsed[key] = set(filter(None, value.split(",")))
        else:
            parsed[key] = value
    for key in ("motifs", "tokens", "blockers", "metrics"):
        parsed.setdefault(key, set())
    return parsed


def _jaccard(a: set[str], b: set[str]) -> float:
    if not a and not b:
        return 0.0
    return len(a & b) / max(1, len(a | b))


def signature_similarity(a: str | ProjectNode | dict[str, Any], b: str | ProjectNode | dict[str, Any]) -> float:
    left = _parse_signature(a)
    right = _parse_signature(b)
    score = 0.0
    if left.get("family") and left.get("family") == right.get("family"):
        score += 0.25
    score += 0.25 * _jaccard(set(left.get("motifs", set())), set(right.get("motifs", set())))
    if left.get("evidence") and left.get("evidence") == right.get("evidence"):
        score += 0.15
    score += 0.15 * _jaccard(set(left.get("tokens", set())), set(right.get("tokens", set())))
    score += 0.10 * _jaccard(set(left.get("blockers", set())), set(right.get("blockers", set())))
    score += 0.10 * _jaccard(set(left.get("metrics", set())), set(right.get("metrics", set())))
    return round(min(1.0, max(0.0, score)), 3)


def _node_time(node: ProjectNode) -> datetime | None:
    value = node.updated_at_utc
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None


def _nearest_kind(node: ProjectNode, prior: ProjectNode) -> str:
    current_time = _node_time(node)
    prior_time = _node_time(prior)
    if current_time and prior_time and prior_time <= current_time:
        return "prior"
    return "sibling"


def _changed_assumption(node: ProjectNode, prior: ProjectNode, similarity: float) -> str:
    current = _parse_signature(node)
    previous = _parse_signature(prior)
    if similarity >= 0.82:
        return "No clear assumption delta detected"
    changed: list[str] = []
    if current.get("motifs") != previous.get("motifs"):
        changed.append("motif")
    if current.get("evidence") != previous.get("evidence"):
        changed.append("evidence")
    if current.get("blockers") != previous.get("blockers"):
        changed.append("blocker")
    return ", ".join(changed) + " delta detected" if changed else "Small token-level delta detected"


def nearest_prior_rows(registry: ProjectRegistry) -> list[dict[str, Any]]:
    nodes = [node for node in registry.nodes if node.kind in DECISION_KINDS]
    signatures = {node.id: candidate_signature(node) for node in nodes}
    rows: list[dict[str, Any]] = []
    for node in sorted(nodes, key=lambda item: (item.family, item.label, item.id)):
        best: tuple[float, ProjectNode] | None = None
        for other in nodes:
            if other.id == node.id:
                continue
            similarity = signature_similarity(signatures[node.id], signatures[other.id])
            if best is None or (similarity, other.label) > (best[0], best[1].label):
                best = (similarity, other)
        if not best:
            continue
        similarity, prior = best
        warning = ""
        if similarity >= 0.82:
            warning = "Do not repeat unchanged"
        elif similarity >= 0.65:
            warning = "Check assumption delta before retest"
        rows.append(
            {
                "Label": node.label,
                "Family": node.family,
                "Kind": node.kind,
                "Signature": signatures[node.id],
                "Nearest Prior": f"{prior.label} ({_nearest_kind(node, prior)})",
                "Similarity": similarity,
                "Prior Status": STATUS_LABELS.get(prior.status, prior.status),
                "Prior Evidence": prior.evidence_level.replace("_", " ").title(),
                "Prior Blocker": _primary_blocker(prior),
                "Changed Assumption": _changed_assumption(node, prior, similarity),
                "Repeat Warning": warning,
            }
        )
    return sorted(rows, key=lambda row: (row["Similarity"], row["Family"], row["Label"]), reverse=True)


def motif_summaries(registry: ProjectRegistry) -> list[dict[str, Any]]:
    motif_nodes: dict[str, list[ProjectNode]] = defaultdict(list)
    motif_labels = {motif: label for motif, label, _needles in MOTIF_RULES}
    for node in registry.nodes:
        if node.kind not in DECISION_KINDS and node.kind not in {"dataset", "doc"}:
            continue
        for motif in node_pattern_tags(node):
            motif_nodes[motif].append(node)

    rows: list[dict[str, Any]] = []
    for motif, nodes in motif_nodes.items():
        candidates = [node for node in nodes if node.kind == "candidate"]
        positive = [node for node in nodes if node.status in POSITIVE_STATUSES]
        blocked_rejected = [node for node in nodes if node.status in NEGATIVE_STATUSES]
        families = sorted({node.family for node in nodes if node.family})
        best_status = _best_status(nodes)
        best_evidence = _best_evidence(nodes)
        best_pnl = max((_pnl_value(node) for node in nodes), default=0.0)
        repeat_pressure = (len(nodes) + len(blocked_rejected) * 2 + max(0, len(candidates) - len(positive))) / max(1, len(positive) + 1)
        row = {
            "Motif": motif_labels.get(motif, motif.replace("_", " ").title()),
            "motif_id": motif,
            "Color": MOTIF_COLORS.get(motif, "#94a3b8"),
            "Families": ", ".join(families[:4]),
            "Nodes": len(nodes),
            "Candidates": len(candidates),
            "Watch/active": len(positive),
            "Blocked/rejected": len(blocked_rejected),
            "Best Status": STATUS_LABELS.get(best_status, best_status),
            "Best Evidence": best_evidence.replace("_", " ").title(),
            "Best P&L": round(best_pnl, 2),
            "Best P&L/7d": round(best_pnl, 2),
            "Repeat Pressure": round(repeat_pressure, 1),
            "Examples": _examples(nodes),
        }
        row["Guidance"] = _motif_guidance(row)
        rows.append(row)
    return sorted(
        rows,
        key=lambda row: (row["Watch/active"], EVIDENCE_RANK.get(str(row["Best Evidence"]).lower().replace(" ", "_"), 0), row["Best P&L"], -row["Repeat Pressure"]),
        reverse=True,
    )


def repetition_clusters(registry: ProjectRegistry) -> list[dict[str, Any]]:
    clusters: dict[tuple[str, tuple[str, ...]], list[ProjectNode]] = defaultdict(list)
    for node in registry.nodes:
        if node.kind not in DECISION_KINDS:
            continue
        tags = tuple(sorted(node_pattern_tags(node))[:4])
        if tags:
            clusters[(node.family or "unclassified", tags)].append(node)

    rows: list[dict[str, Any]] = []
    motif_labels = {motif: label for motif, label, _needles in MOTIF_RULES}
    for (family, tags), nodes in clusters.items():
        if len(nodes) < 3:
            continue
        positives = [node for node in nodes if node.status in POSITIVE_STATUSES]
        blocked = [node for node in nodes if node.status in NEGATIVE_STATUSES]
        pressure = len(nodes) + len(blocked) * 2 - len(positives)
        if pressure < 4:
            continue
        rows.append(
            {
                "Family": family,
                "Pattern": " + ".join(motif_labels.get(tag, tag.replace("_", " ").title()) for tag in tags),
                "Attempts": len(nodes),
                "Watch/active": len(positives),
                "Blocked/rejected": len(blocked),
                "Best Evidence": _best_evidence(nodes).replace("_", " ").title(),
                "Best P&L": round(max((_pnl_value(node) for node in nodes), default=0.0), 2),
                "Best P&L/7d": round(max((_pnl_value(node) for node in nodes), default=0.0), 2),
                "Risk": "High repeat risk" if len(blocked) >= len(positives) and len(nodes) >= 5 else "Needs lineage check",
                "Examples": _examples(nodes),
                "Guidance": "Do not create another sibling until blocker/assumption changed." if len(blocked) >= len(positives) else "Keep, but branch with a clearly different mechanism.",
            }
        )
    return sorted(rows, key=lambda row: (row["Risk"] == "High repeat risk", row["Attempts"], row["Blocked/rejected"]), reverse=True)


def family_pattern_rows(registry: ProjectRegistry) -> list[dict[str, Any]]:
    gap_by_family = {row["Family"]: row for row in family_gap_rows(registry)}
    by_family: dict[str, list[ProjectNode]] = defaultdict(list)
    for node in registry.nodes:
        by_family[node.family or "unclassified"].append(node)

    rows: list[dict[str, Any]] = []
    for family, nodes in sorted(by_family.items()):
        motif_counter: Counter[str] = Counter()
        for node in nodes:
            motif_counter.update(node_pattern_tags(node))
        candidates = [node for node in nodes if node.kind == "candidate"]
        positives = [node for node in nodes if node.status in POSITIVE_STATUSES]
        blocked = [node for node in nodes if node.status in NEGATIVE_STATUSES]
        top_motifs = ", ".join(tag.replace("_", " ") for tag, _count in motif_counter.most_common(4)) or "unmapped"
        gap = gap_by_family.get(family, {})
        next_move = gap.get("Do Next")
        if not next_move:
            if len(candidates) == 0 and positives:
                next_move = "Name the strongest artifact as a candidate before more variants."
            elif blocked and len(blocked) >= max(2, len(positives)):
                next_move = "Resolve blocker pattern before another sibling run."
            elif positives:
                next_move = "Exploit cautiously with stricter forward/live comparison."
            else:
                next_move = "Clarify hypothesis and collect first forward evidence."
        rows.append(
            {
                "Family": family,
                "Nodes": len(nodes),
                "Candidates": len(candidates),
                "Watch/active": len(positives),
                "Blocked/rejected": len(blocked),
                "Best Evidence": _best_evidence(nodes).replace("_", " ").title(),
                "Best P&L": round(max((_pnl_value(node) for node in nodes), default=0.0), 2),
                "Best P&L/7d": round(max((_pnl_value(node) for node in nodes), default=0.0), 2),
                "Dominant Motifs": top_motifs,
                "Next Move": next_move,
            }
        )
    return sorted(rows, key=lambda row: (row["Watch/active"], row["Best P&L"], row["Candidates"]), reverse=True)


def _primary_blocker(node: ProjectNode) -> str:
    if node.blockers:
        text = str(node.blockers[0]).replace("\n", " ").strip()
        if "rejection_reason:" in text:
            text = text.split("rejection_reason:", 1)[-1].strip()
        return text[:160]
    if node.status == "diagnostic_only":
        return "diagnostic only; not proof yet"
    if node.status in NEGATIVE_STATUSES:
        return "blocked/rejected without a structured blocker edge"
    return (node.next_action or node.summary[:160]).strip()


def _is_positive_warning_snapshot(snapshot: dict[str, Any]) -> bool:
    value = snapshot.get("pnl_7d_value")
    if value is None:
        value = snapshot.get("pnl_value")
    return value is not None and float(value) > 0


def positive_blocked_rows(registry: ProjectRegistry) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for node in registry.nodes:
        if node.kind not in DECISION_KINDS:
            continue
        snapshot = normalized_metric_snapshot(node)
        if not _is_positive_warning_snapshot(snapshot):
            continue
        blocked_by_status = node.status in BLOCKING_STATUSES
        blocked_by_gate = bool(node.blockers) or any(tag in node_pattern_tags(node) for tag in ("underpowered", "baseline_compare", "source_quality", "fillability", "accounting"))
        if not (blocked_by_status or blocked_by_gate):
            continue
        if node.status == "diagnostic_only":
            tempting = "Positive diagnostic P&L looks useful as a clue."
            blocked = "Diagnostic-only evidence is not forward/live proof."
            do_next = "Convert to a frozen candidate and collect forward evidence before reuse."
        elif snapshot["pnl_confidence"] != "high":
            tempting = "Positive raw P&L is tempting but unit confidence is low."
            blocked = "Metric unit/provenance is ambiguous, so it cannot rank as proof."
            do_next = "Reconcile net-after-fee accounting before retesting."
        else:
            tempting = "Positive net P&L can look like a win."
            blocked = "Status/blockers still say this is not proof."
            do_next = "Do not rerun as-is; change blocker mechanism or pre-register a clean variant."
        rows.append(
            {
                "Label": node.label,
                "Family": node.family,
                "Kind": node.kind,
                "Status": STATUS_LABELS.get(node.status, node.status),
                "Evidence": node.evidence_level.replace("_", " ").title(),
                "P&L/7d": snapshot.get("pnl_7d_display") or "",
                "P&L": snapshot["pnl_display"],
                "Window": snapshot.get("pnl_window_display") or "",
                "Markets": snapshot["markets"],
                "Entries": snapshot["entries"],
                "Primary Blocker": _primary_blocker(node),
                "Why It Is Tempting": tempting,
                "Why It Is Blocked": blocked,
                "Do Next": do_next,
                "_sort_pnl": float(snapshot.get("pnl_7d_value") if snapshot.get("pnl_7d_value") is not None else snapshot.get("pnl_value") or 0.0),
                "_confidence": snapshot["pnl_confidence"],
            }
        )
    rows = sorted(rows, key=lambda row: (row["_confidence"] == "high", row["_sort_pnl"], row["Label"]), reverse=True)
    for row in rows:
        row.pop("_sort_pnl", None)
        row.pop("_confidence", None)
    return rows


def failure_motif_rows(registry: ProjectRegistry) -> list[dict[str, Any]]:
    grouped: dict[tuple[str, str], list[ProjectNode]] = defaultdict(list)
    metadata = {motif: (meaning, change) for motif, _needles, meaning, change in FAILURE_RULES}
    for node in registry.nodes:
        if node.kind not in DECISION_KINDS and not node.blockers:
            continue
        motifs = _failure_motifs_for_node(node)
        if not motifs and node.status in {"blocked", "rejected"}:
            motifs = ["unclassified_blocker"]
            metadata.setdefault("unclassified_blocker", ("Blocked/rejected node lacks a normalized motif.", "Classify the blocker before another sibling run."))
        for motif in motifs:
            grouped[(node.family or "unclassified", motif)].append(node)

    rows: list[dict[str, Any]] = []
    for (family, motif), nodes in grouped.items():
        meaning, change = metadata.get(motif, ("Blocker recurs across this family.", "Identify the changed assumption before retesting."))
        rows.append(
            {
                "Family": family,
                "Failure Motif": motif,
                "Count": len(nodes),
                "Affected Nodes": ", ".join(node.label[:34] for node in sorted(nodes, key=lambda item: item.label)[:4]),
                "Example": _primary_blocker(nodes[0]),
                "Likely Meaning": meaning,
                "Required Change": change,
            }
        )
    return sorted(rows, key=lambda row: (row["Count"], row["Family"], row["Failure Motif"]), reverse=True)


def _family_semantic_explained(registry: ProjectRegistry) -> set[str]:
    explained: set[str] = set()
    for edge in registry.edges:
        if edge.relation in SEMANTIC_EDGE_TYPES:
            explained.add(edge.source)
            explained.add(edge.target)
    return explained


def family_gap_rows(registry: ProjectRegistry) -> list[dict[str, Any]]:
    by_family: dict[str, list[ProjectNode]] = defaultdict(list)
    for node in registry.nodes:
        by_family[node.family or "unclassified"].append(node)
    explained = _family_semantic_explained(registry)
    repeat_families = {row["Family"] for row in repetition_clusters(registry) if row["Risk"] == "High repeat risk"}

    rows: list[dict[str, Any]] = []
    for family, nodes in sorted(by_family.items()):
        candidates = [node for node in nodes if node.kind == "candidate"]
        reports = [node for node in nodes if node.kind == "report"]
        stats = [node for node in nodes if node.kind == "stats"]
        scripts = [node for node in nodes if node.kind == "script"]
        positives = [node for node in nodes if _pnl_value(node) > 0 or node.status in POSITIVE_STATUSES]
        forward = [node for node in nodes if EVIDENCE_RANK.get(node.evidence_level, 0) >= EVIDENCE_RANK["forward_shadow"]]
        live_stat = [node for node in nodes if node.evidence_level in {"live_stats", "live_forward"}]
        blocked_rejected = [node for node in nodes if node.status in NEGATIVE_STATUSES or node.blockers]
        watch_active = [node for node in nodes if node.status in POSITIVE_STATUSES]
        blocked_with_no_lineage = [node for node in nodes if node.kind in DECISION_KINDS and (node.status in BLOCKING_STATUSES or node.blockers) and node.id not in explained]
        motif_counter: Counter[str] = Counter()
        for node in nodes:
            motif_counter.update(node_pattern_tags(node))
        dominant_motifs = ", ".join(tag.replace("_", " ") for tag, _count in motif_counter.most_common(4)) or "unmapped"
        flags: list[str] = []
        support_family = family in SUPPORT_FAMILIES
        if not candidates and not support_family:
            flags.append("NO_CANDIDATE")
        if not forward and not support_family:
            flags.append("NO_FORWARD_EVIDENCE")
        if not stats and not support_family:
            flags.append("NO_STATS")
        if len(nodes) >= 8 and not candidates and not support_family:
            flags.append("DATA_WITHOUT_CANDIDATE")
        if family == "unclassified" and len(scripts) >= 5:
            flags.append("SCRIPT_HEAVY_UNCLASSIFIED")
        if len(reports) >= 3 and not any(node.next_action for node in reports):
            flags.append("MANY_REPORTS_NO_NEXT_ACTION")
        if blocked_with_no_lineage:
            flags.append("LINEAGE_UNDER_SPECIFIED")
        if any(node.status == "diagnostic_only" and _pnl_value(node) > 0 for node in nodes) and not candidates:
            flags.append("POSITIVE_DIAGNOSTIC_NO_FREEZE")
        if family in repeat_families:
            flags.append("REPEAT_RISK_HIGH")

        if "LINEAGE_UNDER_SPECIFIED" in flags:
            priority = "High"
            do_next = "Repair blocker lineage before interpreting the family."
        elif "REPEAT_RISK_HIGH" in flags:
            priority = "High"
            do_next = "Stop sibling variants until the changed assumption is explicit."
        elif "NO_CANDIDATE" in flags:
            priority = "Medium"
            do_next = "Name the strongest artifact as a candidate or archive the family."
        elif "NO_FORWARD_EVIDENCE" in flags:
            priority = "Medium"
            do_next = "Collect forward evidence before branching."
        else:
            priority = "Low"
            do_next = "Monitor; no major family gap detected."

        rows.append(
            {
                "Family": family,
                "Nodes": len(nodes),
                "Candidates": len(candidates),
                "Reports": len(reports),
                "Stats": len(stats),
                "Scripts": len(scripts),
                "Forward Evidence": len(forward),
                "Live Evidence": len(live_stat),
                "Blocked/Rejected": len(blocked_rejected),
                "Watch/Active": len(watch_active),
                "Best Evidence": _best_evidence(nodes).replace("_", " ").title(),
                "Best P&L": round(max((_pnl_value(node) for node in nodes), default=0.0), 2),
                "Best P&L/7d": round(max((_pnl_value(node) for node in nodes), default=0.0), 2),
                "Dominant Motifs": dominant_motifs,
                "Gap Flags": ", ".join(flags) if flags else "NONE",
                "Priority": priority,
                "Do Next": do_next,
                "Next Move": do_next,
                "Positive Nodes": len(positives),
            }
        )
    priority_rank = {"High": 3, "Medium": 2, "Low": 1}
    return sorted(rows, key=lambda row: (priority_rank.get(row["Priority"], 0), row["Nodes"]), reverse=True)


def lineage_gap_rows(registry: ProjectRegistry) -> list[dict[str, Any]]:
    explained = _family_semantic_explained(registry)
    rows: list[dict[str, Any]] = []
    for node in registry.nodes:
        if node.kind not in {"candidate", "report"}:
            continue
        if node.id in explained:
            continue
        if node.status not in {"blocked", "rejected", "needs_more_proof", "diagnostic_only"} and not node.blockers:
            continue
        priority = "High" if node.status in {"blocked", "rejected"} or node.blockers else "Medium"
        rows.append(
            {
                "Label": node.label,
                "Family": node.family,
                "Kind": node.kind,
                "Status": STATUS_LABELS.get(node.status, node.status),
                "Evidence": node.evidence_level.replace("_", " ").title(),
                "Motifs": ", ".join(tag.replace("_", " ") for tag in node_pattern_tags(node)[:3]),
                "Missing Link": "add blocks/rejects/supersedes edge or classify nearest prior",
                "Priority": priority,
            }
        )
    priority_rank = {"High": 2, "Medium": 1}
    return sorted(rows, key=lambda row: (priority_rank.get(row["Priority"], 0), row["Family"], row["Kind"], row["Label"]), reverse=True)[:80]


def research_move_cards(registry: ProjectRegistry) -> list[dict[str, Any]]:
    cards: list[dict[str, Any]] = []
    for row in positive_blocked_rows(registry)[:3]:
        cards.append(
            {
                "Lane": "Do Not Repeat",
                "Title": row["Label"],
                "Family": row["Family"],
                "Signal": f"{row['Family']} | {row['Evidence']} | P&L/7d {row.get('P&L/7d') or 'n/a'} | source {row['P&L']}",
                "Evidence": row["Evidence"],
                "Why": row["Why It Is Blocked"],
                "Next Action": row["Do Next"],
                "Risk": "Positive P&L is not proof while blockers remain.",
                "Source Nodes": row.get("Source Node", row["Label"]),
                "Move": row["Do Next"],
            }
        )
    for row in failure_motif_rows(registry)[:3]:
        cards.append(
            {
                "Lane": "Repair Lineage",
                "Title": f"{row['Family']} / {row['Failure Motif']}",
                "Family": row["Family"],
                "Signal": f"{row['Count']} affected nodes",
                "Evidence": "blocker motif",
                "Why": row["Likely Meaning"],
                "Next Action": row["Required Change"],
                "Risk": "Repeating siblings without fixing this motif will blur conclusions.",
                "Source Nodes": row["Affected Nodes"],
                "Move": row["Required Change"],
            }
        )
    for row in nearest_prior_rows(registry):
        if row["Repeat Warning"]:
            cards.append(
                {
                    "Lane": "Do Not Repeat",
                    "Title": row["Label"],
                    "Family": row["Family"],
                    "Signal": f"{row['Similarity']} similar to {row['Nearest Prior']}",
                    "Evidence": row["Prior Evidence"],
                    "Why": row["Repeat Warning"],
                    "Next Action": "Document the changed assumption before another sibling test.",
                    "Risk": "Near-duplicate attempt can recycle a blocked prior.",
                    "Source Nodes": f"{row['Label']} | {row['Nearest Prior']}",
                    "Move": row["Repeat Warning"],
                }
            )
        if len([card for card in cards if card["Lane"] == "Do Not Repeat"]) >= 4:
            break
    for row in motif_summaries(registry)[:3]:
        lane = "Test Next" if row["Watch/active"] and row["Best Evidence"] in {"Live Forward", "Forward Shadow", "Live Stats"} else "Validate"
        cards.append(
            {
                "Lane": lane,
                "Title": row["Motif"],
                "Family": row["Families"],
                "Signal": f"{row['Watch/active']} watch/active | {row['Best Evidence']} | P&L/7d {row.get('Best P&L/7d', row['Best P&L'])}",
                "Evidence": row["Best Evidence"],
                "Why": "Existing motif evidence is stronger than the surrounding alternatives.",
                "Next Action": row["Guidance"],
                "Risk": "Validate with blockers and baseline comparison visible.",
                "Source Nodes": row["Examples"],
                "Move": row["Guidance"],
            }
        )
    for row in family_gap_rows(registry):
        if row["Priority"] in {"High", "Medium"} and any(flag in row["Gap Flags"] for flag in ("NO_CANDIDATE", "NO_FORWARD_EVIDENCE", "POSITIVE_DIAGNOSTIC_NO_FREEZE")):
            cards.append(
                {
                    "Lane": "Frontier",
                    "Title": row["Family"],
                    "Family": row["Family"],
                    "Signal": f"{row['Gap Flags']} | {row['Nodes']} nodes",
                    "Evidence": f"{row['Forward Evidence']} forward | {row['Live Evidence']} live",
                    "Why": "Family evidence is incomplete or under-classified.",
                    "Next Action": row["Do Next"],
                    "Risk": "This is a gap flag, not a new-family approval.",
                    "Source Nodes": row["Family"],
                    "Move": row["Do Next"],
                }
            )
        if len([card for card in cards if card["Lane"] == "Frontier"]) >= 2:
            break
    for row in repetition_clusters(registry)[:2]:
        if row["Blocked/rejected"] >= max(2, row["Watch/active"]):
            cards.append(
                {
                    "Lane": "Archive/Ignore",
                    "Title": row["Pattern"],
                    "Family": row["Family"],
                    "Signal": f"{row['Attempts']} attempts | {row['Blocked/rejected']} blocked/rejected",
                    "Evidence": row["Best Evidence"],
                    "Why": row["Risk"],
                    "Next Action": row["Guidance"],
                    "Risk": "Low value unless the next assumption is materially different.",
                    "Source Nodes": row["Examples"],
                    "Move": row["Guidance"],
                }
            )

    lane_rank = {"Do Not Repeat": 6, "Repair Lineage": 5, "Test Next": 4, "Validate": 3, "Frontier": 2, "Archive/Ignore": 1}
    deduped: list[dict[str, Any]] = []
    seen: set[tuple[str, str]] = set()
    for card in cards:
        key = (card["Lane"], card["Title"])
        if key not in seen:
            deduped.append(card)
            seen.add(key)
    return sorted(deduped, key=lambda card: (lane_rank.get(card["Lane"], 0), card["Title"]), reverse=True)[:12]


def frontier_cards(registry: ProjectRegistry) -> list[dict[str, Any]]:
    return research_move_cards(registry)[:9]
