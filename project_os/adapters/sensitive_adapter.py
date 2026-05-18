from __future__ import annotations

from pathlib import Path

from project_os.curation import Overrides
from project_os.models import AdapterResult, ProjectNode, path_mtime_iso

from .base import apply_node_overrides, file_size, node_id, result


SENSITIVE_PATHS = (".env", "secrets")


def scan(root: Path, overrides: Overrides) -> AdapterResult:
    adapter = "sensitive_adapter"
    out = result(adapter)
    count = 0
    for rel in SENSITIVE_PATHS:
        path = root / rel
        if not path.exists():
            continue
        if path.is_dir():
            files = [p for p in path.rglob("*") if p.is_file()]
        else:
            files = [path]
        for sensitive_path in sorted(files, key=lambda p: str(p).lower()):
            count += 1
            family = "infrastructure"
            node = ProjectNode(
                id=node_id("secret", family, sensitive_path.relative_to(root)),
                kind="secret",
                label=str(sensitive_path.relative_to(root)),
                family=family,
                status="active",
                evidence_level="metadata_only",
                path=str(sensitive_path),
                updated_at_utc=path_mtime_iso(sensitive_path),
                size_bytes=file_size(sensitive_path),
                tags=["sensitive", "local_only"],
                source_adapter=adapter,
                confidence="exact",
                sensitive=True,
                summary="Sensitive local file. Path and metadata are indexed for local visibility; raw contents are not stored in Research OS.",
                next_action="Keep metadata-only visibility; do not render or copy secret contents into Research OS outputs.",
                raw_preview="",
            )
            out.nodes.append(apply_node_overrides(node, overrides))
    out.summary = {"sensitive_files": count, "classified_as_secret_nodes": count}
    return out
