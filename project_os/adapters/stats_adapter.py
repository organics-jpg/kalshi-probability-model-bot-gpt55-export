from __future__ import annotations

from pathlib import Path
from typing import Any

from project_os.curation import Overrides
from project_os.family import evidence_from_name, infer_family
from project_os.models import AdapterResult, ProjectNode, path_mtime_iso

from .base import apply_node_overrides, contains_family_edge, family_node, file_size, health_issue, node_id, result, safe_load_json


def _metric_with_source(payload: dict[str, Any], *names: str) -> tuple[Any, str]:
    for name in names:
        if name in payload:
            return payload.get(name), name
    accounting = payload.get("accounting")
    if isinstance(accounting, dict):
        for name in names:
            if name in accounting:
                return accounting.get(name), f"accounting.{name}"
    return None, ""


def _add_metric(metrics: dict[str, Any], key: str, value: Any, source: str, *, unit_hint: str = "") -> None:
    if value is None:
        return
    metrics[key] = value
    if source:
        metrics[f"{key}_source_key"] = source
    if unit_hint:
        metrics[f"{key}_unit_hint"] = unit_hint


def scan(root: Path, overrides: Overrides) -> AdapterResult:
    adapter = "stats_adapter"
    out = result(adapter)
    stats_root = root / "stats"
    if not stats_root.exists():
        out.issues.append(health_issue(adapter, "unclassified", "stats folder missing", "stats/ does not exist", stats_root))
        return out

    for child in sorted((p for p in stats_root.iterdir() if p.is_dir()), key=lambda p: p.name.lower()):
        summary_path = child / "summary.json"
        payload: dict[str, Any] = {}
        parse_note = ""
        missing_summary = False
        if summary_path.exists():
            parsed, parse_note = safe_load_json(summary_path)
            if isinstance(parsed, dict):
                payload = parsed
            elif parse_note:
                out.issues.append(health_issue(adapter, infer_family(child.name), f"bad stats summary: {child.name}", parse_note, summary_path))
        else:
            missing_summary = True

        family = infer_family(child.name, payload.get("strategy_tag"), payload.get("log_source_tag"))
        evidence = "metadata_only" if missing_summary else "live_stats" if "live" in child.name.lower() or "live" in str(payload.get("score_mode", "")).lower() else evidence_from_name(child.name)
        metrics: dict[str, Any] = {"summary_json_present": not missing_summary}
        net_pnl, net_pnl_source = _metric_with_source(payload, "net_pnl_total_dollars", "actual_net_pnl_dollars", "gross_pnl_total_dollars")
        win_rate, win_rate_source = _metric_with_source(payload, "win_rate", "actual_win_rate")
        entries, entries_source = _metric_with_source(payload, "entries_total", "trade_count", "rows_total")
        markets, markets_source = _metric_with_source(payload, "markets_total", "resolved_markets", "market_count")
        cost_basis, cost_basis_source = _metric_with_source(payload, "cost_basis_total_dollars", "actual_entry_notional_dollars")
        _add_metric(metrics, "net_pnl", net_pnl, net_pnl_source, unit_hint="dollars")
        _add_metric(metrics, "win_rate", win_rate, win_rate_source)
        _add_metric(metrics, "entries", entries, entries_source)
        _add_metric(metrics, "markets", markets, markets_source)
        _add_metric(metrics, "cost_basis", cost_basis, cost_basis_source, unit_hint="dollars")
        trades_path = child / "trades.csv"
        market_results_path = child / "market_results.csv"
        reconciliation_path = child / "kalshi_accounting_reconciliation.json"
        status = "diagnostic_only" if missing_summary else "active" if "live" in child.name.lower() else "needs_more_proof"
        if metrics.get("net_pnl") is not None:
            try:
                status = "worth_watching" if float(metrics["net_pnl"]) > 0 else "needs_more_proof"
            except (TypeError, ValueError):
                pass
        tags = ["stats", "accounting" if reconciliation_path.exists() else "bot_log_estimate"]
        if missing_summary:
            tags.append("missing_summary")
            metrics.setdefault("pnl_status", "no_source_pnl")
            metrics.setdefault("pnl_missing_reason", "stats folder exists but summary.json is absent")
        summary = f"Scored output folder. Trades: {trades_path.exists()}; market results: {market_results_path.exists()}; accounting reconciliation: {reconciliation_path.exists()}."
        if missing_summary:
            summary = "Stats folder exists without summary.json; classified as metadata-only and not used as P&L evidence."
        node = ProjectNode(
            id=node_id("stats", family, child.name),
            kind="stats",
            label=child.name,
            family=family,
            status=status,
            evidence_level=evidence,
            path=str(child),
            updated_at_utc=path_mtime_iso(summary_path if summary_path.exists() else child),
            size_bytes=file_size(summary_path),
            metrics=metrics,
            tags=tags,
            source_adapter=adapter,
            confidence="exact",
            summary=summary,
            next_action="Regenerate summary.json before treating this folder as scored P&L evidence." if missing_summary else "",
        )
        out.nodes.extend([family_node(family, adapter), apply_node_overrides(node, overrides)])
        out.edges.append(contains_family_edge(family, node, "stats folder grouped by inferred strategy family"))

    out.summary = {"stats_folders": len([p for p in stats_root.iterdir() if p.is_dir()])}
    return out
