from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable

from project_os.adapters import ALL_ADAPTERS
from project_os.curation import Overrides
from project_os.family import EVIDENCE_RANK, STATUS_LABELS, best_evidence, infer_family, slugify
from project_os.models import AdapterResult, ProjectEdge, ProjectNode, ProjectRegistry, utc_now_iso


REGISTRY_DIR = Path("logs") / "project_os"
LATEST_NAME = "registry_latest.json"
STANDARD_PNL_DAYS = 7.0
BTC15M_MARKETS_PER_DAY = 96.0


def _merge_status(existing: str, incoming: str) -> str:
    if incoming == "health_issue" or existing == "health_issue":
        return "health_issue"
    if incoming == "rejected" or existing == "rejected":
        return "rejected"
    if incoming == "blocked" or existing == "blocked":
        return "blocked"
    order = {
        "unknown": 0,
        "archived": 1,
        "diagnostic_only": 2,
        "needs_more_proof": 3,
        "active": 4,
        "worth_watching": 5,
        "strong_candidate": 6,
    }
    return incoming if order.get(incoming, 0) > order.get(existing, 0) else existing


def _merge_nodes(existing: ProjectNode, incoming: ProjectNode) -> ProjectNode:
    readiness_override = incoming.source_adapter == "candidate_readiness_adapter"
    live_testing_override = incoming.source_adapter == "live_testing_status_adapter" and incoming.status == "active"
    if readiness_override or live_testing_override:
        existing.status = incoming.status
    else:
        existing.status = _merge_status(existing.status, incoming.status)
    existing.evidence_level = best_evidence(existing.evidence_level, incoming.evidence_level)
    if not existing.path and incoming.path:
        existing.path = incoming.path
    if incoming.updated_at_utc and (not existing.updated_at_utc or incoming.updated_at_utc > existing.updated_at_utc):
        existing.updated_at_utc = incoming.updated_at_utc
    if incoming.size_bytes is not None:
        existing.size_bytes = max(existing.size_bytes or 0, incoming.size_bytes)
    existing.metrics = {**(existing.metrics or {}), **(incoming.metrics or {})}
    existing.blockers = list(dict.fromkeys([*(existing.blockers or []), *(incoming.blockers or [])]))[:20]
    if incoming.next_action and (
        not existing.next_action
        or incoming.source_adapter in {"next_step_outcomes_adapter", "candidate_readiness_adapter"}
    ):
        existing.next_action = incoming.next_action
    existing.tags = sorted(set(existing.tags or []) | set(incoming.tags or []))
    if incoming.source_adapter and incoming.source_adapter not in existing.source_adapter.split(","):
        existing.source_adapter = ",".join([x for x in [existing.source_adapter, incoming.source_adapter] if x])
    existing.sensitive = existing.sensitive or incoming.sensitive
    if incoming.summary and len(incoming.summary) > len(existing.summary or ""):
        existing.summary = incoming.summary
    if incoming.raw_preview and not existing.raw_preview:
        existing.raw_preview = incoming.raw_preview
    if existing.confidence != "exact" and incoming.confidence == "exact":
        existing.confidence = "exact"
    return existing


def _limited_str(value: object, limit: int = 500) -> str:
    text = str(value or "")
    return text if len(text) <= limit else text[: limit - 3] + "..."


def _safe_issue(label: str, summary: str, adapter: str = "registry") -> ProjectNode:
    return ProjectNode(
        id=f"health_issue:registry:{slugify(label)}",
        kind="health_issue",
        label=label,
        family="unclassified",
        status="health_issue",
        evidence_level="metadata_only",
        summary=summary,
        source_adapter=adapter,
        confidence="exact",
    )


def _apply_verdict_constraints(node: ProjectNode) -> ProjectNode:
    if node.status == "strong_candidate" and EVIDENCE_RANK.get(node.evidence_level, 0) < EVIDENCE_RANK["forward_shadow"]:
        node.status = "worth_watching"
        if "downgraded_replay_only" not in node.tags:
            node.tags.append("downgraded_replay_only")
    if not node.next_action:
        node.next_action = infer_next_action(node)
    return node


def infer_next_action(node: ProjectNode) -> str:
    if node.kind == "health_issue":
        return "Repair parser/input data or classify the artifact so it no longer appears as an unresolved health notice."
    if node.status == "rejected":
        return "Archive unless new evidence appears."
    if node.blockers:
        return "Inspect blocker report."
    if node.evidence_level in {"replay", "backtest", "diagnostic"} and node.kind in {"candidate", "report"}:
        return "Freeze candidate before counting future evidence."
    if node.kind == "dataset" and "missing_manifest" in " ".join(node.tags):
        return "Repair or classify dataset."
    if node.kind == "stats":
        return "Refresh scorer outside this dashboard if stale."
    if node.kind == "candidate":
        return "Collect more forward/shadow rows."
    return "Classify linked artifacts or connect them to a candidate/report."


PNL_METADATA_KEYS = {
    "pnl_status",
    "pnl_missing_reason",
    "pnl_provenance",
    "pnl_source_node_id",
    "pnl_source_label",
    "pnl_source_relation",
    "pnl_candidate_count",
    "pnl_alternative_keys",
    "pnl_inferred_from_node",
    "pnl_inferred_relation",
    "pnl_standardization_status",
    "pnl_observed_window_source",
    "pnl_observed_window_confidence",
    "pnl_7d_basis",
    "pnl_7d_method",
    "pnl_7d_warning",
}


def _is_actual_pnl_key(key: str) -> bool:
    lowered = key.lower()
    if lowered in PNL_METADATA_KEYS or lowered.endswith(("_source_key", "_unit_hint")):
        return False
    if not any(token in lowered for token in ("pnl", "profit")):
        return False
    if any(token in lowered for token in ("min_", "require_", "threshold", "gate_config")):
        return False
    return True


def _has_actual_pnl(metrics: dict[str, object] | None) -> bool:
    return any(value not in (None, "") and _is_actual_pnl_key(key) for key, value in (metrics or {}).items())


def _copy_pnl_metrics(target: ProjectNode, source: ProjectNode, relation: str) -> None:
    copied_keys = {
        "net_pnl",
        "net_pnl_source_key",
        "net_pnl_unit_hint",
        "selected_pnl",
        "selected_pnl_source_key",
        "selected_pnl_unit_hint",
        "selected_pnl_cents",
        "entries",
        "entries_source_key",
        "markets",
        "markets_source_key",
        "roots",
        "roots_source_key",
        "win_rate",
        "win_rate_source_key",
        "market_count",
        "calendar_day_count",
        "window_days",
        "source_window_days",
        "duration_days",
        "rv_forward_calendar_day_count",
        "rv_forward_distinct_markets",
        "pnl_observed_window_days",
        "pnl_observed_window_source",
        "pnl_observed_window_confidence",
    }
    for key in copied_keys:
        if key in (source.metrics or {}) and key not in (target.metrics or {}):
            target.metrics[key] = source.metrics[key]
    target.metrics.setdefault("pnl_status", "inherited_from_linked_evidence")
    target.metrics.setdefault("pnl_source_node_id", source.id)
    target.metrics.setdefault("pnl_source_label", source.label)
    target.metrics.setdefault("pnl_source_relation", relation)
    target.metrics.setdefault("pnl_provenance", f"linked_{source.kind}:{source.source_adapter}")
    status = str(target.metrics.get("pnl_status", "") or "")
    if not status or status.startswith("no_"):
        target.metrics["pnl_status"] = "inherited_from_linked_evidence"


def _missing_pnl_reason(node: ProjectNode) -> str:
    if node.kind == "candidate" and "locked_plan" in set(node.tags or []):
        return "locked plan stores gates/thresholds but no realized or diagnostic P&L metric"
    if node.kind == "stats":
        return "stats folder has no readable net P&L metric in summary.json"
    if node.kind == "report":
        return "report has no numeric P&L/profit metric outside gate thresholds"
    return "no P&L-like metric found for this decision node"


def _complete_decision_pnl_metadata(nodes: dict[str, ProjectNode], edges: dict[str, ProjectEdge]) -> None:
    incoming: dict[str, list[ProjectEdge]] = {}
    for edge in edges.values():
        incoming.setdefault(edge.target, []).append(edge)

    def edge_rank(edge: ProjectEdge) -> tuple[int, int]:
        relation_rank = {"validates": 5, "scores": 4, "blocks": 3, "rejects": 3, "documents": 2, "mentions": 1}.get(edge.relation, 0)
        return relation_rank, EVIDENCE_RANK.get(edge.evidence_level, 0)

    for node in nodes.values():
        if node.kind not in {"candidate", "report", "stats"}:
            continue
        if _has_actual_pnl(node.metrics):
            status = str(node.metrics.get("pnl_status", "") or "")
            if not status or status.startswith("no_"):
                node.metrics["pnl_status"] = "normalized_from_source_metric"
            node.metrics.setdefault("pnl_provenance", node.source_adapter or "registry")
            continue
        if node.kind == "candidate":
            for edge in sorted(incoming.get(node.id, []), key=edge_rank, reverse=True):
                source = nodes.get(edge.source)
                if source and source.kind in {"report", "stats", "candidate"} and _has_actual_pnl(source.metrics):
                    _copy_pnl_metrics(node, source, edge.relation)
                    break
        if not _has_actual_pnl(node.metrics):
            node.metrics.setdefault("pnl_status", "no_source_pnl")
            node.metrics.setdefault("pnl_missing_reason", _missing_pnl_reason(node))


def _safe_float(value: object) -> float | None:
    if value in (None, "") or isinstance(value, bool):
        return None
    try:
        return float(str(value).strip().replace(",", "").replace("$", "").replace("%", ""))
    except (TypeError, ValueError):
        return None


def _metric_float(metrics: dict[str, object], key: str) -> float | None:
    return _safe_float(metrics.get(key))


def _pnl_metric_dollars(metrics: dict[str, object]) -> tuple[float | None, str, str]:
    keys = (
        "rv_forward_selected_pnl_cents",
        "selected_pnl_cents",
        "net_pnl_cents",
        "pnl_cents",
        "profit_cents",
        "net_pnl",
        "selected_pnl",
        "pnl",
        "profit",
        "gross_pnl",
    )
    for key in keys:
        value = _metric_float(metrics, key)
        if value is None:
            continue
        unit_text = " ".join(
            [
                key.lower(),
                str(metrics.get(f"{key}_source_key", "") or "").lower(),
                str(metrics.get(f"{key}_unit_hint", "") or "").lower(),
            ]
        )
        if "cent" in unit_text:
            return value / 100.0, key, "cents"
        if any(token in unit_text for token in ("dollar", "usd")):
            return value, key, "dollars"
        return value, key, "ambiguous"
    return None, "", "missing"


def _observed_window_days(metrics: dict[str, object]) -> tuple[float | None, str, str, str]:
    explicit_day_keys = (
        "pnl_observed_window_days",
        "actual_pnl_window_days",
        "projected_pnl_window_days",
        "rv_forward_calendar_day_count",
        "calendar_day_count",
        "window_days",
        "source_window_days",
        "duration_days",
    )
    for key in explicit_day_keys:
        days = _metric_float(metrics, key)
        if days and days > 0:
            return days, key, "exact", ""

    market_keys = (
        "rv_forward_distinct_markets",
        "markets",
        "market_count",
        "markets_total",
        "resolved_markets",
        "distinct_markets",
    )
    for key in market_keys:
        markets = _metric_float(metrics, key)
        if markets and markets > 0:
            days = markets / BTC15M_MARKETS_PER_DAY
            return (
                days,
                f"{key}/96_15m_markets_per_day",
                "assumed",
                "Observed window inferred from BTC 15-minute market count; weekly value is a rate-normalized comparison, not a promise of one-week realized P&L.",
            )

    return None, "", "missing", "No source window or market count was available, so weekly P&L could not be standardized."


def _format_dollars(value: float) -> str:
    return f"${value:.2f}"


def _standardize_candidate_pnl(node: ProjectNode) -> None:
    if node.kind != "candidate":
        return
    metrics = node.metrics or {}
    pnl_dollars, pnl_key, pnl_unit = _pnl_metric_dollars(metrics)
    metrics["pnl_7d_basis"] = f"{STANDARD_PNL_DAYS:g}d"
    if pnl_dollars is None:
        metrics.setdefault("pnl_standardization_status", "missing_source_pnl")
        metrics.setdefault("pnl_7d_warning", str(metrics.get("pnl_missing_reason") or "No numeric source P&L was available."))
        return

    window_days, window_source, confidence, warning = _observed_window_days(metrics)
    metrics["actual_pnl_source_dollars"] = round(pnl_dollars, 6)
    metrics["actual_pnl_source_key"] = pnl_key
    metrics["actual_pnl_source_unit"] = pnl_unit
    if window_days is None or window_days <= 0:
        metrics.setdefault("pnl_standardization_status", "missing_window")
        metrics.setdefault("pnl_7d_warning", warning)
        return

    factor = STANDARD_PNL_DAYS / window_days
    projected = pnl_dollars * factor
    metrics["pnl_observed_window_days"] = round(window_days, 8)
    metrics["pnl_observed_window_source"] = window_source
    metrics["pnl_observed_window_confidence"] = confidence
    metrics["actual_pnl_7d_dollars"] = round(projected, 6)
    metrics["projected_pnl_7d_dollars"] = round(projected, 6)
    metrics["pnl_7d_dollars"] = round(projected, 6)
    metrics["pnl_7d_display"] = _format_dollars(projected)
    metrics["pnl_7d_method"] = f"source_pnl_scaled_to_{STANDARD_PNL_DAYS:g}d"
    metrics["pnl_standardization_status"] = "standardized"
    if warning:
        metrics["pnl_7d_warning"] = warning


def _standardize_candidate_pnls(nodes: dict[str, ProjectNode]) -> None:
    for node in nodes.values():
        _standardize_candidate_pnl(node)


def _build_family_nodes(nodes: Iterable[ProjectNode]) -> list[ProjectNode]:
    families = sorted({node.family or "unclassified" for node in nodes if node.family})
    built: list[ProjectNode] = []
    for family in families:
        children = [node for node in nodes if node.family == family and node.kind != "family"]
        statuses = {node.status for node in children}
        status = "unknown"
        if "strong_candidate" in statuses:
            status = "strong_candidate"
        elif "worth_watching" in statuses:
            status = "worth_watching"
        elif "blocked" in statuses:
            status = "blocked"
        elif "active" in statuses:
            status = "active"
        elif "rejected" in statuses:
            status = "rejected"
        elif "archived" in statuses:
            status = "archived"
        metrics = {
            "nodes": len(children),
            "candidates": sum(1 for n in children if n.kind == "candidate"),
            "reports": sum(1 for n in children if n.kind == "report"),
            "health_issues": sum(1 for n in children if n.kind == "health_issue"),
        }
        built.append(
            ProjectNode(
                id=f"family:{family}",
                kind="family",
                label=family.replace("_", " ").title(),
                family=family,
                status=status,
                evidence_level="metadata_only",
                metrics=metrics,
                source_adapter="registry",
                confidence="exact",
                summary=f"{family} family with {len(children)} indexed nodes.",
                next_action="Prioritize blockers, missing forward evidence, and weekly P&L lineage for this family.",
            )
        )
    return built


def _candidate_text(node: ProjectNode) -> str:
    return " ".join([node.id, node.label, node.summary, " ".join(node.tags or [])])


def _add_inferred_edges(nodes: dict[str, ProjectNode], edges: dict[str, ProjectEdge]) -> None:
    candidates = [node for node in nodes.values() if node.kind == "candidate"]
    reports = [node for node in nodes.values() if node.kind in {"report", "doc"}]
    for node in list(nodes.values()):
        if node.kind != "family" and node.family:
            edge = ProjectEdge(source=f"family:{node.family}", target=node.id, relation="contains", evidence_level=node.evidence_level, confidence="exact", reason="registry family grouping")
            edges.setdefault(edge.id, edge)
    for report in reports:
        haystack = _candidate_text(report).lower()
        for candidate in candidates:
            token = candidate.label.lower()
            if token and token in haystack and candidate.family == report.family:
                relation = "rejects" if report.status == "rejected" else "blocks" if report.blockers else "mentions"
                edge = ProjectEdge(source=report.id, target=candidate.id, relation=relation, evidence_level=report.evidence_level, confidence="inferred", reason="candidate id appears in report/doc node")
                edges.setdefault(edge.id, edge)
    for node in list(nodes.values()):
        if node.kind not in {"candidate", "report", "stats"} or not node.family:
            continue
        family_id = f"family:{node.family}"
        if family_id not in nodes:
            continue
        if node.status == "rejected":
            relation = "rejects"
            reason = "decision node is rejected under current Research OS classification"
        elif node.status == "blocked" or node.blockers:
            relation = "blocks"
            reason = "decision node has blocker evidence under current Research OS classification"
        elif node.status in {"needs_more_proof", "diagnostic_only"}:
            relation = "depends_on"
            reason = "decision node needs more proof or lineage classification"
        else:
            continue
        edge = ProjectEdge(source=node.id, target=family_id, relation=relation, evidence_level=node.evidence_level, confidence="inferred", reason=reason)
        edges.setdefault(edge.id, edge)


def _apply_overrides(nodes: dict[str, ProjectNode], edges: dict[str, ProjectEdge], overrides: Overrides) -> None:
    for node_id, status in overrides.status_overrides.items():
        if node_id in nodes:
            nodes[node_id].status = status
    for edge_payload in overrides.edge_overrides:
        try:
            edge = ProjectEdge(
                source=str(edge_payload["source"]),
                target=str(edge_payload["target"]),
                relation=str(edge_payload.get("relation", "mentions")),
                evidence_level=str(edge_payload.get("evidence_level", "metadata_only")),
                confidence=str(edge_payload.get("confidence", "exact")),
                reason=str(edge_payload.get("reason", "manual override")),
            )
        except KeyError:
            continue
        edges[edge.id] = edge


def _run_adapter(adapter, root: Path, overrides: Overrides) -> AdapterResult:
    try:
        return adapter(root, overrides)
    except Exception as exc:  # defensive: one broken adapter should not kill the dashboard
        return AdapterResult(
            name=getattr(adapter, "__module__", "adapter"),
            issues=[_safe_issue(f"adapter failed: {getattr(adapter, '__module__', 'unknown')}", _limited_str(exc))],
            summary={"failed": True, "error": _limited_str(exc)},
        )


def build_registry(root: Path, write: bool = True) -> ProjectRegistry:
    root = root.resolve()
    overrides = Overrides.load(root)
    nodes: dict[str, ProjectNode] = {}
    edges: dict[str, ProjectEdge] = {}
    issues: dict[str, ProjectNode] = {}
    adapter_summaries: dict[str, object] = {}

    for adapter in ALL_ADAPTERS:
        adapter_result = _run_adapter(adapter, root, overrides)
        adapter_summaries[adapter_result.name] = adapter_result.summary
        for node in [*adapter_result.nodes, *adapter_result.issues]:
            if overrides.is_hidden(node.id):
                continue
            node.family = overrides.family_for(node.family, node.label)
            node = _apply_verdict_constraints(node)
            if node.id in nodes:
                nodes[node.id] = _merge_nodes(nodes[node.id], node)
            else:
                nodes[node.id] = node
            if node.kind == "health_issue":
                issues[node.id] = node
        for edge in adapter_result.edges:
            if edge.source and edge.target:
                edges.setdefault(edge.id, edge)

    for family_node in _build_family_nodes(nodes.values()):
        nodes[family_node.id] = _merge_nodes(nodes[family_node.id], family_node) if family_node.id in nodes else family_node

    _add_inferred_edges(nodes, edges)
    _apply_overrides(nodes, edges, overrides)
    for node_id, node in list(nodes.items()):
        nodes[node_id] = _apply_verdict_constraints(node)
    _complete_decision_pnl_metadata(nodes, edges)
    _standardize_candidate_pnls(nodes)

    valid_edges: dict[str, ProjectEdge] = {}
    for edge in edges.values():
        if edge.source in nodes and edge.target in nodes:
            valid_edges[edge.id] = edge
        else:
            missing = edge.source if edge.source not in nodes else edge.target
            issue = _safe_issue("edge references missing node", f"{edge.id} references missing node {missing}.")
            nodes[issue.id] = issue
            issues[issue.id] = issue

    registry = ProjectRegistry(
        generated_at_utc=utc_now_iso(),
        root=str(root),
        nodes=sorted(nodes.values(), key=lambda node: (node.kind, node.family, node.label.lower())),
        edges=sorted(valid_edges.values(), key=lambda edge: edge.id),
        issues=sorted(issues.values(), key=lambda node: node.label.lower()),
        adapter_summaries=adapter_summaries,
    )
    if write:
        write_registry(root, registry)
    return registry


def registry_paths(root: Path) -> tuple[Path, Path]:
    registry_dir = root / REGISTRY_DIR
    timestamp = utc_now_iso().replace(":", "").replace("-", "")
    snapshot = registry_dir / f"registry_{timestamp}.json"
    return registry_dir / LATEST_NAME, snapshot


def write_registry(root: Path, registry: ProjectRegistry) -> None:
    latest, snapshot = registry_paths(root)
    latest.parent.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(registry.to_dict(), indent=2, sort_keys=True)
    latest.write_text(payload, encoding="utf-8")
    snapshot.write_text(payload, encoding="utf-8")


def load_registry(path: Path) -> ProjectRegistry:
    payload = json.loads(path.read_text(encoding="utf-8", errors="ignore") or "{}")
    return ProjectRegistry.from_dict(payload)


def load_or_build_registry(root: Path, force: bool = False) -> ProjectRegistry:
    root = root.resolve()
    latest = root / REGISTRY_DIR / LATEST_NAME
    if latest.exists() and not force:
        try:
            return load_registry(latest)
        except Exception:
            return build_registry(root, write=True)
    return build_registry(root, write=True)
