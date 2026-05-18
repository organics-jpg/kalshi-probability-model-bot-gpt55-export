from __future__ import annotations

from pathlib import Path

from project_os.curation import Overrides
from project_os.family import evidence_from_name, infer_family
from project_os.models import AdapterResult, ProjectNode, path_mtime_iso

from .base import apply_node_overrides, contains_family_edge, family_node, file_size, health_issue, node_id, result, safe_read_text


SCRIPT_PREFIXES = (
    "probe_",
    "run_",
    "build_",
    "score_",
    "audit_",
    "backtest_",
    "research_",
    "validate_",
    "train_",
    "collect_",
    "fetch_",
    "freeze_",
    "join_",
    "register_",
    "stage_",
    "preflight_",
)


def scan(root: Path, overrides: Overrides) -> AdapterResult:
    adapter = "scripts_adapter"
    out = result(adapter)
    count = 0
    unknown = 0
    for script_path in sorted(root.glob("*.py"), key=lambda p: p.name.lower()):
        if not script_path.name.startswith(SCRIPT_PREFIXES):
            continue
        count += 1
        family = infer_family(script_path.name)
        if family == "unclassified":
            family = "strategy_research"
            unknown += 1
        evidence = evidence_from_name(script_path.name)
        preview = safe_read_text(script_path, limit=1200)
        status = "diagnostic_only" if script_path.name.startswith(("probe_", "backtest_", "audit_")) else "needs_more_proof"
        node = ProjectNode(
            id=node_id("script", family, script_path.stem),
            kind="script",
            label=script_path.name,
            family=family,
            status=status,
            evidence_level=evidence,
            path=str(script_path),
            updated_at_utc=path_mtime_iso(script_path),
            size_bytes=file_size(script_path),
            tags=["script", script_path.name.split("_", 1)[0]],
            source_adapter=adapter,
            confidence="inferred",
            summary=f"Root research/probe script classified as {family}.",
            raw_preview=preview,
        )
        out.nodes.extend([family_node(family, adapter), apply_node_overrides(node, overrides)])
        out.edges.append(contains_family_edge(family, node, "script grouped by filename family"))
    out.summary = {"scripts": count, "strategy_research_fallback_scripts": unknown}
    return out
