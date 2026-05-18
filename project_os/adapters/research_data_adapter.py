from __future__ import annotations

from pathlib import Path

from project_os.curation import Overrides
from project_os.family import infer_family
from project_os.models import AdapterResult, ProjectNode

from .base import apply_node_overrides, contains_family_edge, family_node, folder_stats, health_issue, node_id, result, safe_load_json


def scan(root: Path, overrides: Overrides) -> AdapterResult:
    adapter = "research_data_adapter"
    out = result(adapter)
    data_root = root / "research_data"
    if not data_root.exists():
        out.issues.append(health_issue(adapter, "unclassified", "research_data missing", "research_data/ does not exist", data_root))
        return out

    count = 0
    for dataset in sorted((p for p in data_root.iterdir() if p.is_dir()), key=lambda p: p.name.lower()):
        count += 1
        manifest = dataset / "metadata" / "dataset_manifest.json"
        recorder_status = dataset / "metadata" / "native_passive_recorder_status.json"
        schema_version = dataset / "metadata" / "schema_version.json"
        payload = {}
        if manifest.exists():
            parsed, parse_note = safe_load_json(manifest)
            if isinstance(parsed, dict):
                payload = parsed
            elif parse_note:
                out.issues.append(health_issue(adapter, infer_family(dataset.name), f"bad dataset manifest: {dataset.name}", parse_note, manifest))
        else:
            out.issues.append(health_issue(adapter, infer_family(dataset.name), f"missing manifest: {dataset.name}", "dataset has no metadata/dataset_manifest.json", dataset))
        stats = folder_stats(dataset)
        family = infer_family(dataset.name, payload.get("dataset_tag"), payload.get("strategy_tags"), payload.get("live_bot_run_tag"))
        evidence = "forward_shadow" if "shadow" in dataset.name.lower() or payload.get("recorder_type") else "metadata_only"
        tags = ["research_data"]
        for child_name in ("raw_events", "book_checkpoints", "replay_runs", "features", "trade_labels", "metadata"):
            if (dataset / child_name).exists():
                tags.append(child_name)
        node = ProjectNode(
            id=node_id("dataset", family, dataset.name),
            kind="dataset",
            label=dataset.name,
            family=family,
            status="active" if evidence == "forward_shadow" else "needs_more_proof",
            evidence_level=evidence,
            path=str(dataset),
            updated_at_utc=stats.get("updated_at_utc"),
            size_bytes=stats.get("size_bytes"),
            metrics={"files": stats.get("files", 0), "size_mb": round(float(stats.get("size_bytes", 0)) / 1_048_576, 2), "markets": len(payload.get("market_tickers", []) or [])},
            tags=tags,
            source_adapter=adapter,
            confidence="exact",
            summary=f"Research dataset. Manifest={manifest.exists()}, recorder={recorder_status.exists()}, schema={schema_version.exists()}.",
        )
        out.nodes.extend([family_node(family, adapter), apply_node_overrides(node, overrides)])
        out.edges.append(contains_family_edge(family, node, "research dataset grouped by inferred family"))

    out.summary = {"datasets": count}
    return out
