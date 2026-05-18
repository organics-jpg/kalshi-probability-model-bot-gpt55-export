from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


DEFAULT_ROOT = Path("logs/particle_research/real_shadow/rv600_next_evidence_shadow_smoke_20260513T193315Z")
DEFAULT_REFRESH_JSON = Path("logs/particle_research/reports/rv600_next_evidence_shadow_smoke_refresh_latest.json")
DEFAULT_OPPORTUNITY_JSON = Path("logs/particle_research/reports/rv600_next_evidence_shadow_smoke_opportunity_latest.json")
DEFAULT_OUTPUT_JSON = Path("logs/particle_research/reports/rv600_shadow_smoke_audit_latest.json")
DEFAULT_OUTPUT_MD = Path("logs/particle_research/reports/rv600_shadow_smoke_audit_latest.md")


def _load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8-sig"))


def _int(value: Any, default: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def _float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def build_report(args: argparse.Namespace) -> dict[str, Any]:
    root = args.root
    is_smoke = "smoke" in root.name
    run_label = "smoke" if is_smoke else "bounded_run"
    manifest = _load_json(root / "paired_passive_run_manifest.json")
    pipeline = _load_json(root / "pipeline_work" / "pipeline_manifest.json")
    offline = _load_json(root / "offline_v28_context_summary.json")
    refresh = _load_json(args.refresh_json)
    opportunity = _load_json(args.opportunity_json)
    tailer_ok = (
        manifest.get("tailer_returncode") == 0
        or (
            manifest.get("matched_control_mode") == "offline_v28_public_btc_replay"
            and manifest.get("tailer_returncode") is None
        )
    )
    collection_ok = (
        manifest.get("recorder_returncode") == 0
        and tailer_ok
        and manifest.get("independent_spot_returncode") == 0
        and _int(manifest.get("checkpoint_row_count")) > 0
    )
    offline_contexts = _int(offline.get("contexts_written"))
    offline_issues = _int(offline.get("issue_count"))
    offline_ok = offline_contexts > 0 and offline_contexts + offline_issues >= _int(manifest.get("checkpoint_row_count"))
    pipeline_ok = _int(pipeline.get("contexts_written")) > 0 and _int(pipeline.get("context_issues")) == 0
    labels_ok = _int(refresh.get("total_labels_written")) > 0 and _int(refresh.get("total_issues")) == 0
    scored_ok = bool(opportunity.get("schema_version")) and _int(opportunity.get("total_candidate_rows")) > 0
    locked_entries = _int(opportunity.get("locked_total_entries"))
    locked_pnl = _float(opportunity.get("locked_total_pnl_cents"))
    best_grid = opportunity.get("best_grid_candidate") or {}
    accepted_entries = _int(best_grid.get("accepted_entries"))
    ready = collection_ok and offline_ok and pipeline_ok
    fully_scored = ready and labels_ok and scored_ok
    if fully_scored and (locked_entries > 0 or accepted_entries > 0):
        decision = f"{run_label}_scored_with_entries"
    elif fully_scored:
        decision = f"{run_label}_scored_no_rv600_entries"
    elif ready and not labels_ok:
        decision = f"{run_label}_pending_settlement_or_scoring"
    else:
        decision = f"{run_label}_incomplete_or_failed"
    report = {
        "schema_version": "rv600-shadow-smoke-audit-v1",
        "generated_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "research_only": True,
        "run_label": run_label,
        "decision": decision,
        "collection_ok": collection_ok,
        "offline_v28_context_ok": offline_ok,
        "pipeline_ok": pipeline_ok,
        "labels_ok": labels_ok,
        "scored_ok": scored_ok,
        "summary": {
            "root": str(root),
            "checkpoint_row_count": _int(manifest.get("checkpoint_row_count")),
            "context_row_count": _int(manifest.get("context_row_count")),
            "independent_spot_row_count": _int(manifest.get("independent_spot_row_count")),
            "merged_context_issue_count": _int(manifest.get("merged_context_issue_count")),
            "offline_contexts_written": offline_contexts,
            "offline_context_issues": offline_issues,
            "pipeline_contexts_written": _int(pipeline.get("contexts_written")),
            "pipeline_context_issues": _int(pipeline.get("context_issues")),
            "candidate_rows": _int(opportunity.get("total_candidate_rows")),
            "settled_markets": _int(opportunity.get("total_settled_markets")),
            "labels_written": _int(refresh.get("total_labels_written")),
            "locked_total_entries": locked_entries,
            "locked_total_pnl_cents": locked_pnl,
            "best_grid_variant": best_grid.get("variant"),
            "best_grid_accepted_entries": accepted_entries,
            "best_grid_selected_pnl_cents": _float(best_grid.get("selected_pnl_cents")),
            "best_grid_matched_v28_delta_cents": _float(best_grid.get("matched_v28_delta_cents")),
            "best_grid_rejection": best_grid.get("rejection_reason") or "",
        },
        "interpretation": (
            _interpretation(decision, locked_entries, locked_pnl, accepted_entries)
        ),
        "inputs": {
            "root": str(root),
            "refresh_json": str(args.refresh_json),
            "opportunity_json": str(args.opportunity_json),
        },
    }
    return report


def _interpretation(decision: str, locked_entries: int, locked_pnl: float, accepted_entries: int) -> str:
    if decision.endswith("_pending_settlement_or_scoring"):
        return (
            "The bounded read-only path is operational, but not all captured markets have settled or been scored yet. "
            "Treat this as collection evidence only until labels and opportunity scoring are complete."
        )
    if decision.endswith("_scored_with_entries"):
        return (
            "The bounded read-only path is fully scored and produced accepted RV600-style entries. "
            f"Locked entries={locked_entries}, locked_pnl_cents={locked_pnl}, best_grid_entries={accepted_entries}; "
            "this is still a small fresh-shadow slice and must be judged by the objective completion gates."
        )
    if decision.endswith("_scored_no_rv600_entries"):
        return (
            "The bounded read-only path is operational and fully scored, but it produced zero accepted RV600 entries. "
            "It is pipeline validation, not strategy validation."
        )
    return (
        "The bounded read-only path did not clear collection, offline-context, pipeline, label, or scoring checks. "
        "Inspect the referenced artifacts before using it as evidence."
    )


def _markdown(report: dict[str, Any]) -> str:
    summary = report["summary"]
    lines = [
        "# RV600 Shadow Smoke Audit",
        "",
        f"- generated_utc: {report['generated_utc']}",
        f"- research_only: {report['research_only']}",
        f"- run_label: {report['run_label']}",
        f"- decision: {report['decision']}",
        f"- collection_ok: {report['collection_ok']}",
        f"- offline_v28_context_ok: {report['offline_v28_context_ok']}",
        f"- pipeline_ok: {report['pipeline_ok']}",
        f"- labels_ok: {report['labels_ok']}",
        f"- scored_ok: {report['scored_ok']}",
        "",
        "## Summary",
        "",
        f"- root: `{summary['root']}`",
        f"- checkpoint_row_count: {summary['checkpoint_row_count']}",
        f"- context_row_count: {summary['context_row_count']}",
        f"- independent_spot_row_count: {summary['independent_spot_row_count']}",
        f"- merged_context_issue_count: {summary['merged_context_issue_count']}",
        f"- offline_contexts_written: {summary['offline_contexts_written']}",
        f"- offline_context_issues: {summary['offline_context_issues']}",
        f"- pipeline_contexts_written: {summary['pipeline_contexts_written']}",
        f"- pipeline_context_issues: {summary['pipeline_context_issues']}",
        f"- candidate_rows: {summary['candidate_rows']}",
        f"- settled_markets: {summary['settled_markets']}",
        f"- labels_written: {summary['labels_written']}",
        f"- locked_total_entries: {summary['locked_total_entries']}",
        f"- locked_total_pnl_cents: {summary['locked_total_pnl_cents']}",
        f"- best_grid_variant: `{summary['best_grid_variant']}`",
        f"- best_grid_accepted_entries: {summary['best_grid_accepted_entries']}",
        f"- best_grid_selected_pnl_cents: {summary['best_grid_selected_pnl_cents']}",
        f"- best_grid_matched_v28_delta_cents: {summary['best_grid_matched_v28_delta_cents']}",
        f"- best_grid_rejection: `{summary['best_grid_rejection']}`",
        "",
        "## Interpretation",
        "",
        report["interpretation"],
        "",
    ]
    return "\n".join(lines)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Audit the bounded RV600 next-evidence smoke run.")
    parser.add_argument("--root", type=Path, default=DEFAULT_ROOT)
    parser.add_argument("--refresh-json", type=Path, default=DEFAULT_REFRESH_JSON)
    parser.add_argument("--opportunity-json", type=Path, default=DEFAULT_OPPORTUNITY_JSON)
    parser.add_argument("--output-json", type=Path, default=DEFAULT_OUTPUT_JSON)
    parser.add_argument("--output-md", type=Path, default=DEFAULT_OUTPUT_MD)
    parser.add_argument("--write", action="store_true")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    report = build_report(args)
    markdown = _markdown(report)
    if args.write:
        args.output_json.parent.mkdir(parents=True, exist_ok=True)
        args.output_json.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        args.output_md.write_text(markdown, encoding="utf-8")
    print(f"decision={report['decision']}")
    print(f"collection_ok={report['collection_ok']}")
    print(f"pipeline_ok={report['pipeline_ok']}")
    print(f"labels_ok={report['labels_ok']}")
    print(f"candidate_rows={report['summary']['candidate_rows']}")
    print(f"locked_total_entries={report['summary']['locked_total_entries']}")
    print(f"output_json={args.output_json}")
    print(f"output_md={args.output_md}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
