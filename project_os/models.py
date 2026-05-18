from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


NODE_KINDS = {
    "family",
    "candidate",
    "run",
    "dataset",
    "report",
    "log",
    "stats",
    "script",
    "doc",
    "artifact",
    "health_issue",
    "secret",
    "archive",
    "unknown",
}

EDGE_KINDS = {
    "contains",
    "produced",
    "uses",
    "scores",
    "validates",
    "rejects",
    "supersedes",
    "depends_on",
    "documents",
    "feeds",
    "mentions",
    "blocks",
}

STATUS_VALUES = {
    "strong_candidate",
    "worth_watching",
    "needs_more_proof",
    "blocked",
    "rejected",
    "active",
    "archived",
    "diagnostic_only",
    "unknown",
    "health_issue",
}

EVIDENCE_LEVELS = {
    "live_forward",
    "forward_shadow",
    "live_stats",
    "replay",
    "backtest",
    "diagnostic",
    "metadata_only",
    "unknown",
}


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def path_mtime_iso(path: Path) -> str | None:
    try:
        return datetime.fromtimestamp(path.stat().st_mtime, timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    except OSError:
        return None


@dataclass(slots=True)
class ProjectNode:
    id: str
    kind: str
    label: str
    family: str = "unclassified"
    status: str = "unknown"
    evidence_level: str = "unknown"
    path: str | None = None
    updated_at_utc: str | None = None
    size_bytes: int | None = None
    metrics: dict[str, Any] = field(default_factory=dict)
    blockers: list[str] = field(default_factory=list)
    next_action: str = ""
    tags: list[str] = field(default_factory=list)
    source_adapter: str = ""
    confidence: str = "inferred"
    sensitive: bool = False
    summary: str = ""
    raw_preview: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "kind": self.kind if self.kind in NODE_KINDS else "unknown",
            "label": self.label,
            "family": self.family or "unclassified",
            "status": self.status if self.status in STATUS_VALUES else "unknown",
            "evidence_level": self.evidence_level if self.evidence_level in EVIDENCE_LEVELS else "unknown",
            "path": self.path,
            "updated_at_utc": self.updated_at_utc,
            "size_bytes": self.size_bytes,
            "metrics": self.metrics or {},
            "blockers": self.blockers or [],
            "next_action": self.next_action or "",
            "tags": self.tags or [],
            "source_adapter": self.source_adapter or "",
            "confidence": self.confidence or "inferred",
            "sensitive": bool(self.sensitive),
            "summary": self.summary or "",
            "raw_preview": self.raw_preview or "",
        }

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "ProjectNode":
        return cls(
            id=str(payload.get("id", "")),
            kind=str(payload.get("kind", "unknown")),
            label=str(payload.get("label", "")),
            family=str(payload.get("family", "unclassified") or "unclassified"),
            status=str(payload.get("status", "unknown") or "unknown"),
            evidence_level=str(payload.get("evidence_level", "unknown") or "unknown"),
            path=payload.get("path"),
            updated_at_utc=payload.get("updated_at_utc"),
            size_bytes=payload.get("size_bytes"),
            metrics=dict(payload.get("metrics") or {}),
            blockers=list(payload.get("blockers") or []),
            next_action=str(payload.get("next_action", "") or ""),
            tags=list(payload.get("tags") or []),
            source_adapter=str(payload.get("source_adapter", "") or ""),
            confidence=str(payload.get("confidence", "inferred") or "inferred"),
            sensitive=bool(payload.get("sensitive", False)),
            summary=str(payload.get("summary", "") or ""),
            raw_preview=str(payload.get("raw_preview", "") or ""),
        )


@dataclass(slots=True)
class ProjectEdge:
    source: str
    target: str
    relation: str
    evidence_level: str = "unknown"
    confidence: str = "inferred"
    reason: str = ""

    @property
    def id(self) -> str:
        return f"{self.source}->{self.relation}->{self.target}"

    def to_dict(self) -> dict[str, Any]:
        return {
            "source": self.source,
            "target": self.target,
            "relation": self.relation if self.relation in EDGE_KINDS else "mentions",
            "evidence_level": self.evidence_level if self.evidence_level in EVIDENCE_LEVELS else "unknown",
            "confidence": self.confidence or "inferred",
            "reason": self.reason or "",
        }

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "ProjectEdge":
        return cls(
            source=str(payload.get("source", "")),
            target=str(payload.get("target", "")),
            relation=str(payload.get("relation", "mentions") or "mentions"),
            evidence_level=str(payload.get("evidence_level", "unknown") or "unknown"),
            confidence=str(payload.get("confidence", "inferred") or "inferred"),
            reason=str(payload.get("reason", "") or ""),
        )


@dataclass(slots=True)
class AdapterResult:
    name: str
    nodes: list[ProjectNode] = field(default_factory=list)
    edges: list[ProjectEdge] = field(default_factory=list)
    issues: list[ProjectNode] = field(default_factory=list)
    summary: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class ProjectRegistry:
    generated_at_utc: str
    root: str
    nodes: list[ProjectNode] = field(default_factory=list)
    edges: list[ProjectEdge] = field(default_factory=list)
    issues: list[ProjectNode] = field(default_factory=list)
    adapter_summaries: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "generated_at_utc": self.generated_at_utc,
            "root": self.root,
            "nodes": [node.to_dict() for node in self.nodes],
            "edges": [edge.to_dict() for edge in self.edges],
            "issues": [issue.to_dict() for issue in self.issues],
            "adapter_summaries": self.adapter_summaries,
        }

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "ProjectRegistry":
        return cls(
            generated_at_utc=str(payload.get("generated_at_utc", "")),
            root=str(payload.get("root", "")),
            nodes=[ProjectNode.from_dict(item) for item in payload.get("nodes", [])],
            edges=[ProjectEdge.from_dict(item) for item in payload.get("edges", [])],
            issues=[ProjectNode.from_dict(item) for item in payload.get("issues", [])],
            adapter_summaries=dict(payload.get("adapter_summaries") or {}),
        )
