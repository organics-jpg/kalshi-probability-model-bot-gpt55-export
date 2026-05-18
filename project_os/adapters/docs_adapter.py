from __future__ import annotations

from pathlib import Path

from project_os.curation import Overrides
from project_os.family import infer_family
from project_os.models import AdapterResult, ProjectNode, path_mtime_iso

from .base import apply_node_overrides, contains_family_edge, family_node, file_size, health_issue, node_id, result, safe_read_text


DOC_PATHS = [
    ("docs/research", "*.md"),
    ("docs", "*.md"),
]


def _title_and_snippet(text: str, fallback: str) -> tuple[str, str]:
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    title = fallback
    for line in lines[:20]:
        if line.startswith("#"):
            title = line.lstrip("#").strip() or fallback
            break
    snippet = " ".join(line.lstrip("#").strip() for line in lines[:8])[:700]
    return title, snippet


def scan(root: Path, overrides: Overrides) -> AdapterResult:
    adapter = "docs_adapter"
    out = result(adapter)
    seen: set[Path] = set()
    count = 0
    for rel, pattern in DOC_PATHS:
        folder = root / rel
        if not folder.exists():
            continue
        for doc_path in sorted(folder.glob(pattern), key=lambda p: str(p).lower()):
            if doc_path in seen:
                continue
            seen.add(doc_path)
            count += 1
            preview = safe_read_text(doc_path, limit=10_000)
            title, snippet = _title_and_snippet(preview, doc_path.stem)
            family = infer_family(doc_path.name, title, snippet)
            status = "archived" if "archive" in doc_path.name.lower() else "needs_more_proof"
            node = ProjectNode(
                id=node_id("doc", family, doc_path.stem),
                kind="doc",
                label=title,
                family=family,
                status=status,
                evidence_level="metadata_only",
                path=str(doc_path),
                updated_at_utc=path_mtime_iso(doc_path),
                size_bytes=file_size(doc_path),
                tags=["doc", "markdown"],
                source_adapter=adapter,
                confidence="inferred",
                summary=snippet,
                raw_preview=preview[:2000],
            )
            out.nodes.extend([family_node(family, adapter), apply_node_overrides(node, overrides)])
            out.edges.append(contains_family_edge(family, node, "documentation grouped by inferred family"))
    if count == 0:
        out.issues.append(health_issue(adapter, "unclassified", "no research docs found", "No docs markdown files were discovered.", root / "docs"))
    out.summary = {"docs": count}
    return out
