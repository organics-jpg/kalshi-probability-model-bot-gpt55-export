from __future__ import annotations

import json
import re
from collections import Counter
from pathlib import Path
from typing import Any, Mapping, Sequence

from project_os.family import EVIDENCE_RANK, STATUS_LABELS, STATUS_RANK
from project_os.models import ProjectNode, ProjectRegistry, utc_now_iso


REPORT_NAME = "research_os_v2_overnight_report.md"
PATTERNS_NAME = "research_os_v2_patterns_latest.json"
REPORT_DIR = Path("logs") / "project_os"

_SECRET_KEY_RE = re.compile(
    r"(?i)\b(api[_-]?key|secret|token|password|passwd|private[_-]?key|access[_-]?key|refresh[_-]?token)\b"
)
_SECRET_ASSIGNMENT_RE = re.compile(
    r"(?i)\b(api[_-]?key|secret|token|password|passwd|private[_-]?key|access[_-]?key|refresh[_-]?token)\b\s*[:=]\s*([^\s,;]+)"
)
_LONG_SECRETISH_RE = re.compile(r"\b(?:sk-[A-Za-z0-9]{20,}|[A-Za-z0-9]{40,})\b")


def output_paths(root: str | Path) -> tuple[Path, Path]:
    """Return the default markdown and JSON output paths for a registry root."""
    root_path = Path(root)
    report_dir = root_path / REPORT_DIR
    return report_dir / REPORT_NAME, report_dir / PATTERNS_NAME


def build_patterns_payload(registry: ProjectRegistry) -> dict[str, Any]:
    """Build the machine-readable pattern payload without touching disk."""
    calls = {
        "motifs": _call_pattern_func("motif_summaries", registry),
        "repetition_clusters": _call_pattern_func("repetition_clusters", registry),
        "families": _call_pattern_func("family_pattern_rows", registry),
        "family_gaps": _call_pattern_func("family_gap_rows", registry),
        "positive_blocked": _call_pattern_func("positive_blocked_rows", registry),
        "failure_motifs": _call_pattern_func("failure_motif_rows", registry),
        "lineage_gaps": _call_pattern_func("lineage_gap_rows", registry),
        "nearest_prior": _call_pattern_func("nearest_prior_rows", registry),
        "frontier_cards": _call_pattern_func("frontier_cards", registry),
        "research_moves": _call_pattern_func("research_move_cards", registry),
    }
    sections: dict[str, Any] = {}
    errors: dict[str, str] = {}
    for name, result in calls.items():
        rows, error = result
        sections[name] = _sanitize_json(rows)
        if error:
            errors[name] = error

    return {
        "schema": "research_os_v2_patterns_latest",
        "generated_at_utc": utc_now_iso(),
        "registry_generated_at_utc": registry.generated_at_utc,
        "registry_root": _sanitize_text(registry.root),
        "research_only": True,
        "note": "Registry-derived pattern summary only; this payload does not authorize live orders.",
        "sections": sections,
        "pattern_errors": errors,
        "source_counts": _registry_counts(registry),
    }


def render_morning_report(
    registry: ProjectRegistry,
    *,
    files_changed: Sequence[str] | None = None,
    tests_run: Sequence[str | Mapping[str, Any]] | None = None,
    browser_qa: Sequence[str | Mapping[str, Any]] | None = None,
    residual_risks: Sequence[str] | None = None,
    metadata: Mapping[str, Any] | None = None,
    patterns_payload: Mapping[str, Any] | None = None,
) -> str:
    """Render the Research OS V2 morning report without touching disk."""
    payload = dict(patterns_payload or build_patterns_payload(registry))
    sections = payload.get("sections") if isinstance(payload.get("sections"), Mapping) else {}
    pattern_errors = payload.get("pattern_errors") if isinstance(payload.get("pattern_errors"), Mapping) else {}
    anchors = _source_anchors(registry)
    counts = _registry_counts(registry)
    meta = _sanitize_json(dict(metadata or {}))

    lines: list[str] = [
        "# Research OS V2 Overnight Report",
        "",
        f"Generated UTC: {_sanitize_text(str(payload.get('generated_at_utc') or utc_now_iso()))}",
        f"Registry snapshot UTC: {_sanitize_text(registry.generated_at_utc or 'unknown')}",
        "",
        "Scope: research-only registry report. No scorer, bot, order, threshold, secret, state, stats, or dashboard action is implied by this file.",
        "",
        "## Executive Snapshot",
        "",
        f"- Registry nodes: {counts['nodes']} across {counts['families']} families.",
        f"- Candidates: {counts['candidates']}; reports: {counts['reports']}; datasets: {counts['datasets']}; health issues: {counts['health_issues']}.",
        f"- Evidence mix: {_counter_phrase(counts['evidence_levels'])}.",
        f"- Status mix: {_counter_phrase(counts['statuses'])}.",
        "",
    ]

    if meta:
        lines.extend(["## Run Metadata", ""])
        lines.extend(_mapping_bullets(meta))
        lines.append("")

    lines.extend(_metadata_section("Files Changed", files_changed))
    lines.extend(_metadata_section("Tests Run", tests_run))
    lines.extend(_metadata_section("Browser QA", browser_qa))

    lines.extend(
        _cards_section(
            "Top Research Moves",
            sections.get("research_moves") or sections.get("frontier_cards", []),
            ["Lane", "Title", "Family", "Signal", "Evidence", "Why", "Next Action", "Risk", "Source Nodes", "Move"],
            empty="No research move cards were available from the current pattern module.",
        )
    )
    lines.extend(
        _table_section(
            "Reusable Motifs",
            sections.get("motifs", []),
            ["Motif", "Families", "Nodes", "Candidates", "Watch/active", "Blocked/rejected", "Best Evidence", "Best P&L/7d", "Guidance"],
            limit=8,
        )
    )
    lines.extend(
        _table_section(
            "Patterns Not To Rerun Blindly",
            sections.get("repetition_clusters", []),
            ["Family", "Pattern", "Attempts", "Watch/active", "Blocked/rejected", "Best Evidence", "Best P&L/7d", "Risk", "Guidance"],
            limit=8,
        )
    )
    lines.extend(
        _table_section(
            "Positive But Blocked",
            sections.get("positive_blocked", []),
            ["Label", "Family", "Kind", "Status", "Evidence", "P&L/7d", "P&L", "Window", "Primary Blocker", "Do Next"],
            limit=8,
        )
    )
    lines.extend(
        _table_section(
            "Failure Motifs",
            sections.get("failure_motifs", []),
            ["Family", "Failure Motif", "Count", "Affected Nodes", "Example", "Likely Meaning", "Required Change"],
            limit=10,
        )
    )
    lines.extend(
        _table_section(
            "Lineage Gaps",
            sections.get("lineage_gaps", []),
            ["Label", "Family", "Kind", "Status", "Evidence", "Motifs", "Missing Link", "Priority"],
            limit=12,
        )
    )
    lines.extend(
        _table_section(
            "Nearest Prior Lineage",
            sections.get("nearest_prior", []),
            ["Label", "Family", "Kind", "Nearest Prior", "Similarity", "Prior Status", "Prior Evidence", "Changed Assumption", "Repeat Warning"],
            limit=10,
        )
    )
    lines.extend(
        _table_section(
            "Family Gaps",
            sections.get("family_gaps") or sections.get("families", []),
            ["Family", "Nodes", "Candidates", "Reports", "Stats", "Forward Evidence", "Live Evidence", "Blocked/Rejected", "Watch/Active", "Best P&L/7d", "Dominant Motifs", "Gap Flags", "Next Move"],
            limit=12,
        )
    )

    if pattern_errors:
        lines.extend(["## Pattern Function Gaps", ""])
        for name, error in pattern_errors.items():
            lines.append(f"- `{_sanitize_text(str(name))}`: {_sanitize_text(str(error), limit=220)}")
        lines.append("")

    lines.extend(["## Source Anchors", ""])
    if anchors:
        for node in anchors:
            lines.append(_node_anchor_line(node))
    else:
        lines.append("- No source anchors were available in the registry snapshot.")
    lines.append("")

    lines.extend(["## Residual Risks", ""])
    if residual_risks:
        for risk in residual_risks:
            lines.append(f"- {_sanitize_text(str(risk), limit=260)}")
    else:
        lines.append("- No additional residual risks were supplied by the caller.")
    lines.append("")

    lines.extend(
        [
            "## Research Guardrail",
            "",
            "This report summarizes registry evidence and pattern pressure only. It is not a live-order, deployment, sizing, or threshold-change recommendation.",
            "",
        ]
    )
    return "\n".join(lines).rstrip() + "\n"


def write_morning_report(
    registry: ProjectRegistry,
    *,
    files_changed: Sequence[str] | None = None,
    tests_run: Sequence[str | Mapping[str, Any]] | None = None,
    browser_qa: Sequence[str | Mapping[str, Any]] | None = None,
    residual_risks: Sequence[str] | None = None,
    metadata: Mapping[str, Any] | None = None,
    report_path: str | Path | None = None,
    patterns_path: str | Path | None = None,
) -> tuple[Path, Path]:
    """Write the morning report and latest patterns JSON when explicitly called."""
    default_report_path, default_patterns_path = output_paths(registry.root or ".")
    report_out = Path(report_path) if report_path is not None else default_report_path
    patterns_out = Path(patterns_path) if patterns_path is not None else default_patterns_path
    patterns_payload = build_patterns_payload(registry)
    report = render_morning_report(
        registry,
        files_changed=files_changed,
        tests_run=tests_run,
        browser_qa=browser_qa,
        residual_risks=residual_risks,
        metadata=metadata,
        patterns_payload=patterns_payload,
    )
    report_out.parent.mkdir(parents=True, exist_ok=True)
    patterns_out.parent.mkdir(parents=True, exist_ok=True)
    report_out.write_text(report, encoding="utf-8")
    patterns_out.write_text(json.dumps(patterns_payload, indent=2, sort_keys=True), encoding="utf-8")
    return report_out, patterns_out


def _call_pattern_func(name: str, registry: ProjectRegistry) -> tuple[list[dict[str, Any]], str | None]:
    try:
        from project_os import patterns
    except Exception as exc:  # defensive during concurrent edits
        return [], f"project_os.patterns import failed: {_sanitize_text(str(exc), limit=160)}"

    func = getattr(patterns, name, None)
    if not callable(func):
        return [], "function unavailable"
    try:
        rows = func(registry)
    except Exception as exc:  # pattern views should not block report generation
        return [], _sanitize_text(str(exc), limit=180)
    if rows is None:
        return [], None
    if not isinstance(rows, list):
        try:
            rows = list(rows)
        except TypeError:
            return [], f"unexpected return type {type(rows).__name__}"
    return [_coerce_mapping(row) for row in rows], None


def _coerce_mapping(row: Any) -> dict[str, Any]:
    if isinstance(row, Mapping):
        return dict(row)
    if hasattr(row, "__dict__"):
        return dict(vars(row))
    return {"value": row}


def _sanitize_json(value: Any) -> Any:
    if isinstance(value, Mapping):
        sanitized: dict[str, Any] = {}
        for key, item in value.items():
            safe_key = _sanitize_text(str(key), limit=120)
            if _SECRET_KEY_RE.search(safe_key):
                sanitized[safe_key] = "[redacted]"
            else:
                sanitized[safe_key] = _sanitize_json(item)
        return sanitized
    if isinstance(value, list):
        return [_sanitize_json(item) for item in value]
    if isinstance(value, tuple):
        return [_sanitize_json(item) for item in value]
    if isinstance(value, str):
        return _sanitize_text(value)
    return value


def _sanitize_text(value: str, limit: int = 500) -> str:
    text = str(value or "").replace("\r", " ").replace("\n", " ").strip()
    text = _SECRET_ASSIGNMENT_RE.sub(lambda match: f"{match.group(1)}=[redacted]", text)
    text = _LONG_SECRETISH_RE.sub("[redacted]", text)
    text = text.replace("|", "\\|")
    if len(text) > limit:
        return text[: max(0, limit - 3)] + "..."
    return text


def _registry_counts(registry: ProjectRegistry) -> dict[str, Any]:
    nodes = list(registry.nodes or [])
    kinds = Counter(node.kind for node in nodes)
    statuses = Counter(STATUS_LABELS.get(node.status, node.status) for node in nodes)
    evidence = Counter((node.evidence_level or "unknown").replace("_", " ").title() for node in nodes)
    families = {node.family for node in nodes if node.family and node.family != "unclassified"}
    return {
        "nodes": len(nodes),
        "families": len(families),
        "candidates": kinds.get("candidate", 0),
        "reports": kinds.get("report", 0),
        "datasets": kinds.get("dataset", 0),
        "health_issues": kinds.get("health_issue", 0),
        "kinds": dict(kinds),
        "statuses": dict(statuses),
        "evidence_levels": dict(evidence),
    }


def _counter_phrase(values: Mapping[str, int], limit: int = 5) -> str:
    items = sorted(values.items(), key=lambda item: item[1], reverse=True)[:limit]
    return ", ".join(f"{_sanitize_text(str(key), limit=80)}={int(count)}" for key, count in items) or "none"


def _metadata_section(title: str, rows: Sequence[Any] | None) -> list[str]:
    lines = [f"## {title}", ""]
    if not rows:
        lines.extend(["- Not supplied.", ""])
        return lines
    for row in rows:
        if isinstance(row, Mapping):
            label = _sanitize_text(str(row.get("name") or row.get("path") or row.get("test") or row.get("url") or "entry"), limit=180)
            detail = _sanitize_text(str(row.get("result") or row.get("status") or row.get("detail") or ""), limit=240)
            lines.append(f"- {label}" + (f": {detail}" if detail else ""))
        else:
            lines.append(f"- {_sanitize_text(str(row), limit=260)}")
    lines.append("")
    return lines


def _mapping_bullets(mapping: Mapping[str, Any]) -> list[str]:
    lines: list[str] = []
    for key, value in mapping.items():
        lines.append(f"- {_sanitize_text(str(key), limit=120)}: {_sanitize_text(str(value), limit=260)}")
    return lines


def _cards_section(title: str, rows: Any, columns: Sequence[str], *, empty: str) -> list[str]:
    lines = [f"## {title}", ""]
    clean_rows = _rows(rows)
    if not clean_rows:
        lines.extend([f"- {empty}", ""])
        return lines
    for row in clean_rows[:9]:
        title_value = _sanitize_text(str(row.get("Title") or row.get("title") or "Pattern"), limit=140)
        lines.append(f"- {title_value}")
        for column in columns:
            if column.lower() == "title":
                continue
            value = row.get(column)
            if value not in (None, ""):
                lines.append(f"  - {column}: {_sanitize_text(str(value), limit=220)}")
    lines.append("")
    return lines


def _table_section(title: str, rows: Any, columns: Sequence[str], *, limit: int) -> list[str]:
    lines = [f"## {title}", ""]
    clean_rows = _rows(rows)
    if not clean_rows:
        lines.extend(["No rows available from the current registry snapshot.", ""])
        return lines
    lines.append("| " + " | ".join(columns) + " |")
    lines.append("| " + " | ".join("---" for _ in columns) + " |")
    for row in clean_rows[:limit]:
        values = [_sanitize_text(str(row.get(column, "")), limit=180) for column in columns]
        lines.append("| " + " | ".join(values) + " |")
    if len(clean_rows) > limit:
        lines.append("")
        lines.append(f"Showing {limit} of {len(clean_rows)} rows.")
    lines.append("")
    return lines


def _rows(value: Any) -> list[dict[str, Any]]:
    if not isinstance(value, list):
        return []
    return [dict(row) for row in value if isinstance(row, Mapping)]


def _source_anchors(registry: ProjectRegistry, limit: int = 12) -> list[ProjectNode]:
    candidates = [
        node
        for node in registry.nodes
        if node.kind in {"candidate", "report", "dataset", "stats", "health_issue", "doc"}
        and not node.sensitive
        and node.kind != "secret"
    ]
    return sorted(
        candidates,
        key=lambda node: (
            STATUS_RANK.get(node.status, 0),
            EVIDENCE_RANK.get(node.evidence_level, 0),
            node.updated_at_utc or "",
            node.path or "",
        ),
        reverse=True,
    )[:limit]


def _node_anchor_line(node: ProjectNode) -> str:
    label = _sanitize_text(node.label, limit=150)
    path = _sanitize_text(node.path or "no path recorded", limit=220)
    status = _sanitize_text(STATUS_LABELS.get(node.status, node.status), limit=80)
    evidence = _sanitize_text((node.evidence_level or "unknown").replace("_", " ").title(), limit=80)
    return f"- `{_sanitize_text(node.id, limit=180)}` | {label} | {node.kind} | {status} | {evidence} | {path}"


__all__ = [
    "PATTERNS_NAME",
    "REPORT_NAME",
    "build_patterns_payload",
    "output_paths",
    "render_morning_report",
    "write_morning_report",
]
