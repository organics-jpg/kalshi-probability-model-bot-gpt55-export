from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


DEFAULT_OVERRIDES = {
    "families": {},
    "nodes": {},
    "aliases": {},
    "hidden": [],
    "pinned": [],
    "status_overrides": {},
    "edge_overrides": [],
}


@dataclass(slots=True)
class Overrides:
    families: dict[str, str] = field(default_factory=dict)
    nodes: dict[str, dict[str, Any]] = field(default_factory=dict)
    aliases: dict[str, str] = field(default_factory=dict)
    hidden: list[str] = field(default_factory=list)
    pinned: list[str] = field(default_factory=list)
    status_overrides: dict[str, str] = field(default_factory=dict)
    edge_overrides: list[dict[str, Any]] = field(default_factory=list)

    @classmethod
    def load(cls, root: Path) -> "Overrides":
        path = root / "project_os" / "overrides.json"
        if not path.exists():
            return cls()
        try:
            payload = json.loads(path.read_text(encoding="utf-8", errors="ignore") or "{}")
        except Exception:
            return cls()
        merged = dict(DEFAULT_OVERRIDES)
        merged.update(payload if isinstance(payload, dict) else {})
        return cls(
            families=dict(merged.get("families") or {}),
            nodes=dict(merged.get("nodes") or {}),
            aliases=dict(merged.get("aliases") or {}),
            hidden=list(merged.get("hidden") or []),
            pinned=list(merged.get("pinned") or []),
            status_overrides=dict(merged.get("status_overrides") or {}),
            edge_overrides=list(merged.get("edge_overrides") or []),
        )

    def family_for(self, family: str, label: str = "") -> str:
        if family in self.families:
            return self.families[family]
        lowered = str(label or "").lower()
        for needle, override in self.aliases.items():
            if needle.lower() in lowered:
                return override
        return family

    def is_hidden(self, node_id: str) -> bool:
        return node_id in set(self.hidden)

    def node_overrides(self, node_id: str) -> dict[str, Any]:
        return dict(self.nodes.get(node_id) or {})
