from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable, Mapping

from .v28_context_source import v28_context_event_schema


@dataclass(frozen=True)
class V28EventSourceSummary:
    path: str
    exists: bool
    mtime_utc: str
    size_bytes: int
    checked_tail_rows: int
    compatible_tail_rows: int
    schema_counts: dict[str, int]
    preferred_live_source: bool


def latest_execution_events_path(workspace: Path) -> Path | None:
    candidates = discover_execution_events_paths(workspace)
    if not candidates:
        return None
    candidates.sort(key=_event_source_sort_key, reverse=True)
    return candidates[0]


def describe_execution_event_source(path: Path | None) -> dict[str, Any]:
    if path is None:
        return {}
    return asdict(_summarize_source(path))


def discover_execution_events_paths(workspace: Path) -> list[Path]:
    workspace = workspace.resolve()
    roots = [workspace / "logs"]
    sibling_90 = workspace.parent / "kalshi 90 +v28" / "logs"
    if sibling_90 not in roots:
        roots.append(sibling_90)
    paths: dict[str, Path] = {}
    for root in roots:
        if not root.exists():
            continue
        for path in root.rglob("execution_events.ndjson"):
            lower = str(path).lower()
            if "\\archive" in lower or "/archive" in lower or "trial_archive" in lower:
                continue
            paths[str(path.resolve()).lower()] = path.resolve()
    return list(paths.values())


def _event_source_sort_key(path: Path) -> tuple[int, int, int, int, float]:
    summary = _summarize_source(path)
    lower = str(path).lower()
    compatible = 1 if summary.compatible_tail_rows > 0 else 0
    live_not_shadow = 1 if ("live" in lower and "shadow" not in lower) else 0
    touch90 = 1 if "v28_90_touch" in lower else 0
    nonempty = 1 if summary.size_bytes > 0 else 0
    return (compatible, live_not_shadow, touch90, nonempty, path.stat().st_mtime if path.exists() else 0.0)


def _summarize_source(path: Path) -> V28EventSourceSummary:
    exists = path.exists()
    stat = path.stat() if exists else None
    schema_counts: dict[str, int] = {}
    checked = 0
    compatible = 0
    for event in _tail_json_objects(path):
        checked += 1
        schema = v28_context_event_schema(event)
        if schema:
            compatible += 1
            schema_counts[schema] = schema_counts.get(schema, 0) + 1
    mtime_utc = ""
    if stat is not None:
        mtime_utc = datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc).isoformat()
    lower = str(path).lower()
    return V28EventSourceSummary(
        path=str(path),
        exists=exists,
        mtime_utc=mtime_utc,
        size_bytes=0 if stat is None else int(stat.st_size),
        checked_tail_rows=checked,
        compatible_tail_rows=compatible,
        schema_counts=schema_counts,
        preferred_live_source=bool("live" in lower and "shadow" not in lower),
    )


def _tail_json_objects(path: Path, *, max_bytes: int = 1_048_576, max_rows: int = 2_000) -> Iterable[Mapping[str, Any]]:
    if not path.exists() or path.stat().st_size <= 0:
        return []
    with path.open("rb") as handle:
        size = path.stat().st_size
        handle.seek(max(0, size - max_bytes))
        data = handle.read().decode("utf-8", errors="replace")
    lines = data.splitlines()
    if lines and not lines[0].lstrip().startswith("{"):
        lines = lines[1:]
    rows: list[Mapping[str, Any]] = []
    for line in lines[-max_rows:]:
        line = line.strip()
        if not line:
            continue
        try:
            payload = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(payload, dict):
            rows.append(payload)
    return rows
