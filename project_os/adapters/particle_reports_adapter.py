from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from project_os.curation import Overrides
from project_os.family import evidence_from_name, infer_family, slugify
from project_os.models import AdapterResult, ProjectNode, path_mtime_iso

from .base import apply_node_overrides, contains_family_edge, family_node, file_size, health_issue, node_id, result, safe_load_json, safe_read_text


ID_PATTERN = re.compile(r"(?<![A-Za-z0-9])(?:RV600[A-Z0-9]+|PSLICELOCK\d+|GAUSS\d+LOCK\d+|RESIDLOCK\d+|CONSENSUSLOCK\d+|RVTERMLOCK\d+)(?![A-Za-z0-9])")


def _find_candidate_ids(text: str) -> list[str]:
    ids = set(ID_PATTERN.findall(text))
    return sorted(ids)


def _safe_numeric(value: Any) -> float | None:
    if value in (None, "") or isinstance(value, bool):
        return None
    try:
        text = str(value).strip().replace(",", "").replace("$", "").replace("%", "")
        if text.startswith("(") and text.endswith(")"):
            text = "-" + text[1:-1]
        return float(text)
    except (TypeError, ValueError):
        return None


def _unit_hint(path: str) -> str:
    lowered = path.lower()
    if "cent" in lowered:
        return "cents"
    if "dollar" in lowered or "usd" in lowered:
        return "dollars"
    return ""


def _pnl_score(path: str, value: Any) -> int | None:
    if _safe_numeric(value) is None:
        return None
    lowered = path.lower()
    key = lowered.rsplit(".", 1)[-1]
    if not any(token in key for token in ("pnl", "profit")):
        return None
    if "count" in key:
        return None
    if any(token in lowered for token in ("gate_config.", "forward_gates.", "minimum_completion_sample.")):
        return None
    if key.startswith(("min_", "require_", "positive_pnl_after_fees")):
        return None

    score = 10
    if "actual_net_pnl" in key or "net_pnl_total" in key or key == "net_pnl":
        score += 180
    if "cent" in key or "dollar" in key or "usd" in key:
        score += 25
    if "total_counterfactual_pnl" in key or "total_pnl" in key or "locked_total_pnl" in key:
        score += 145
    if "locked_plan_forward_selected_pnl" in key:
        score += 140
    if "selected_pnl" in key or "best_selected_pnl" in key or "best_grid_selected_pnl" in key:
        score += 125
    if "gross" in key:
        score += 70
    if "summary." in lowered:
        score += 35
    if "best_by_total_pnl." in lowered or "best_global_exact." in lowered:
        score += 30
    if "best_by_mean_brier." in lowered:
        score -= 25
    if ".rows[" in lowered or "root_rows[" in lowered or "variant_rows[" in lowered:
        score -= 35
    if any(token in key for token in ("avg_", "mean_", "per_entry", "per_run", "delta")):
        score -= 60
    return score


def _extract_metrics(payload: dict[str, Any]) -> dict[str, Any]:
    wanted = {
        "entries": ("entries", "entry_count", "locked_entries", "selected_entries", "selected_count", "total_selected_count"),
        "markets": ("markets", "market_count", "settled_markets", "distinct_markets"),
        "roots": ("roots", "root_count"),
        "win_rate": ("win_rate", "positive_root_rate", "positive_market_rate"),
    }
    found: dict[str, Any] = {}
    pnl_candidates: list[tuple[int, str, Any, str]] = []

    def walk(value: Any, path: str = "", depth: int = 0) -> None:
        if depth > 6:
            return
        if isinstance(value, dict):
            for key, val in value.items():
                key_l = str(key).lower()
                metric_path = f"{path}.{key_l}" if path else key_l
                score = _pnl_score(metric_path, val)
                if score is not None:
                    pnl_candidates.append((score, metric_path, val, _unit_hint(metric_path)))
                for metric_name, names in wanted.items():
                    if metric_name not in found and key_l in names:
                        if metric_name == "roots" and isinstance(val, list):
                            found[metric_name] = len(val)
                        else:
                            found[metric_name] = val
                        found[f"{metric_name}_source_key"] = metric_path
                        if "cent" in key_l:
                            found[f"{metric_name}_unit_hint"] = "cents"
                        elif "dollar" in key_l or key_l in {"net_pnl", "selected_pnl", "best_grid_pnl", "locked_pnl"}:
                            found[f"{metric_name}_unit_hint"] = "dollars"
                if isinstance(val, (dict, list)):
                    walk(val, metric_path, depth + 1)
        elif isinstance(value, list):
            for item in value[:30]:
                walk(item, path, depth + 1)

    walk(payload)
    if pnl_candidates:
        pnl_candidates.sort(key=lambda item: (item[0], -len(item[1])), reverse=True)
        _score, source_key, value, unit_hint = pnl_candidates[0]
        found["net_pnl"] = value
        found["net_pnl_source_key"] = source_key
        if unit_hint:
            found["net_pnl_unit_hint"] = unit_hint
        found["pnl_candidate_count"] = len(pnl_candidates)
        found["pnl_alternative_keys"] = "; ".join(path for _score, path, _value, _unit in pnl_candidates[1:6])
        found.setdefault("pnl_status", "normalized_from_report_metric")
    else:
        found.setdefault("pnl_status", "no_pnl_metric_in_report")
        found.setdefault("pnl_missing_reason", "no numeric P&L/profit metric found outside gate thresholds")
    return found


def _extract_blockers(payload: dict[str, Any], preview: str) -> list[str]:
    blockers: list[str] = []
    for key in ("blocked_by", "blockers", "rejection", "rejections", "failed_gates", "rejection_reasons"):
        val = payload.get(key)
        if isinstance(val, str):
            blockers.extend([part.strip() for part in re.split(r"[;,]", val) if part.strip()])
        elif isinstance(val, list):
            blockers.extend(str(item) for item in val[:8])
    for match in re.findall(r"`([^`]*(?:below|failed|nonpositive|blocked|rejection)[^`]*)`", preview, flags=re.I)[:8]:
        blockers.append(match)
    return list(dict.fromkeys(blockers))[:10]


def _status_from_report(name: str, payload: dict[str, Any], metrics: dict[str, Any], blockers: list[str]) -> str:
    text = f"{name} {payload.get('decision', '')} {payload.get('verdict', '')} {payload.get('status', '')}".lower()
    promotion_allowed = payload.get("promotion_allowed")
    if any(word in text for word in ("rejected", "retired", "failed", "futility")):
        return "rejected"
    if promotion_allowed is False or blockers:
        return "blocked"
    evidence = evidence_from_name(name)
    if evidence in {"replay", "backtest", "diagnostic"}:
        return "diagnostic_only"
    try:
        pnl = float(metrics.get("net_pnl", 0))
        if pnl > 0 and evidence in {"live_forward", "forward_shadow", "live_stats"}:
            return "worth_watching"
    except (TypeError, ValueError):
        pass
    return "needs_more_proof"


def scan(root: Path, overrides: Overrides) -> AdapterResult:
    adapter = "particle_reports_adapter"
    out = result(adapter)
    reports_root = root / "logs" / "particle_research" / "reports"
    if not reports_root.exists():
        out.issues.append(health_issue(adapter, "unclassified", "particle reports missing", "logs/particle_research/reports does not exist", reports_root))
        return out

    report_count = 0
    for report_path in sorted(reports_root.glob("*latest.json"), key=lambda p: p.name.lower()):
        report_count += 1
        parsed, parse_note = safe_load_json(report_path, max_bytes=25_000_000)
        payload = parsed if isinstance(parsed, dict) else {}
        md_path = report_path.with_suffix(".md")
        preview = safe_read_text(md_path if md_path.exists() else report_path)
        if parse_note and not payload:
            out.issues.append(health_issue(adapter, infer_family(report_path.name), f"limited report parse: {report_path.name}", parse_note, report_path))
        family = infer_family(report_path.name, preview, payload.get("family"), payload.get("plan_id"), payload.get("variant"))
        evidence = evidence_from_name(report_path.name)
        metrics = _extract_metrics(payload)
        blockers = _extract_blockers(payload, preview)
        status = _status_from_report(report_path.name, payload, metrics, blockers)
        candidate_ids = _find_candidate_ids(preview + " " + str(payload)[:10_000])
        tags = ["report", "latest"]
        if candidate_ids:
            tags.append("candidate_link")
        node = ProjectNode(
            id=node_id("report", family, report_path.stem),
            kind="report",
            label=report_path.stem,
            family=family,
            status=status,
            evidence_level=evidence,
            path=str(report_path),
            updated_at_utc=path_mtime_iso(report_path),
            size_bytes=file_size(report_path),
            metrics=metrics,
            blockers=blockers,
            next_action="Inspect blocker report" if blockers else "Link to a frozen candidate and require forward/shadow confirmation before ranking.",
            tags=tags + candidate_ids,
            source_adapter=adapter,
            confidence="exact",
            summary=(preview.splitlines()[0] if preview.strip() else f"Particle research report {report_path.name}")[:500],
            raw_preview=preview[:2000],
        )
        out.nodes.extend([family_node(family, adapter), apply_node_overrides(node, overrides)])
        out.edges.append(contains_family_edge(family, node, "latest report grouped by inferred family"))

    out.summary = {"latest_reports": report_count}
    return out
