from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


DEFAULT_REAL_SHADOW_DIR = Path("logs/particle_research/real_shadow")
DEFAULT_REPORTS_DIR = Path("logs/particle_research/reports")
DEFAULT_ROOT_PREFIX = "rv600_next_evidence_shadow_"
DEFAULT_MIN_ROOT_NAME = "rv600_next_evidence_shadow_20260513T195001Z"
DEFAULT_OUTPUT_JSON = Path("logs/particle_research/reports/rv600_shadow_bounded_cumulative_audit_latest.json")
DEFAULT_OUTPUT_MD = Path("logs/particle_research/reports/rv600_shadow_bounded_cumulative_audit_latest.md")


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


def _refresh_path(root: Path, reports_dir: Path) -> Path:
    return reports_dir / f"{root.name}_refresh.json"


def _latest_cumulative_opportunity(reports_dir: Path) -> Path | None:
    paths = sorted(
        reports_dir.glob("rv600_next_evidence_shadow_cumulative_*_opportunity.json"),
        key=lambda path: path.stat().st_mtime,
    )
    return paths[-1] if paths else None


def _discover_roots(base_dir: Path, reports_dir: Path, min_root_name: str) -> tuple[Path, ...]:
    if not base_dir.exists():
        return ()
    roots = []
    for root in sorted(base_dir.iterdir(), key=lambda path: path.name):
        if not root.is_dir():
            continue
        if not root.name.startswith(DEFAULT_ROOT_PREFIX) or "smoke" in root.name:
            continue
        if root.name < min_root_name:
            continue
        refresh = _load_json(_refresh_path(root, reports_dir))
        if _int(refresh.get("total_labels_written")) <= 0 or _int(refresh.get("total_issues")) != 0:
            continue
        required = (
            root / "paired_passive_run_manifest.json",
            root / "offline_v28_context_summary.json",
            root / "pipeline_work" / "pipeline_manifest.json",
            root / "candidate_snapshots" / "candidate_snapshots.ndjson",
        )
        if all(path.exists() for path in required):
            roots.append(root)
    return tuple(roots)


def build_report(args: argparse.Namespace) -> dict[str, Any]:
    roots = tuple(
        args.root
        or _discover_roots(args.base_dir, args.reports_dir, args.min_root_name)
    )
    refresh_jsons = tuple(args.refresh_json or [_refresh_path(root, args.reports_dir) for root in roots])
    opportunity_path = args.opportunity_json or _latest_cumulative_opportunity(args.reports_dir)
    opportunity = _load_json(opportunity_path) if opportunity_path is not None else {}
    root_rows = []
    collection_ok = True
    offline_ok = True
    pipeline_ok = True
    for root in roots:
        manifest = _load_json(root / "paired_passive_run_manifest.json")
        offline = _load_json(root / "offline_v28_context_summary.json")
        pipeline = _load_json(root / "pipeline_work" / "pipeline_manifest.json")
        checkpoint_rows = _int(manifest.get("checkpoint_row_count"))
        spot_issues = _int(manifest.get("independent_spot_issue_count"))
        tailer_ok = (
            manifest.get("tailer_returncode") == 0
            or (
                manifest.get("matched_control_mode") == "offline_v28_public_btc_replay"
                and manifest.get("tailer_returncode") is None
            )
        )
        root_collection_ok = (
            manifest.get("recorder_returncode") == 0
            and tailer_ok
            and manifest.get("independent_spot_returncode") == 0
            and checkpoint_rows >= int(args.min_checkpoint_rows)
            and spot_issues == 0
        )
        offline_contexts = _int(offline.get("contexts_written"))
        offline_issues = _int(offline.get("issue_count"))
        root_offline_ok = offline_contexts > 0 and offline_contexts + offline_issues >= checkpoint_rows
        root_pipeline_ok = _int(pipeline.get("contexts_written")) > 0 and _int(pipeline.get("context_issues")) == 0
        collection_ok = collection_ok and root_collection_ok
        offline_ok = offline_ok and root_offline_ok
        pipeline_ok = pipeline_ok and root_pipeline_ok
        root_rows.append(
            {
                "root": str(root),
                "collection_ok": root_collection_ok,
                "offline_v28_context_ok": root_offline_ok,
                "pipeline_ok": root_pipeline_ok,
                "checkpoint_row_count": checkpoint_rows,
                "independent_spot_row_count": _int(manifest.get("independent_spot_row_count")),
                "independent_spot_issue_count": spot_issues,
                "offline_contexts_written": offline_contexts,
                "offline_context_issues": offline_issues,
                "pipeline_contexts_written": _int(pipeline.get("contexts_written")),
                "pipeline_context_issues": _int(pipeline.get("context_issues")),
            }
        )
    refresh_rows = [_load_json(path) for path in refresh_jsons]
    labels_ok = bool(refresh_rows) and all(
        _int(row.get("total_labels_written")) > 0 and _int(row.get("total_issues")) == 0
        for row in refresh_rows
    )
    scored_ok = bool(opportunity.get("schema_version")) and _int(opportunity.get("total_candidate_rows")) > 0
    best_grid = opportunity.get("best_grid_candidate") or {}
    best_locked = opportunity.get("best_locked_candidate") or {}
    best_rejection = best_grid.get("rejection_reason") or ""
    locked_entries = _int(opportunity.get("locked_total_entries"))
    locked_pnl = _float(opportunity.get("locked_total_pnl_cents"))
    best_entries = _int(best_grid.get("accepted_entries"))
    best_pnl = _float(best_grid.get("selected_pnl_cents"))
    best_delta = _float(best_grid.get("matched_v28_delta_cents"))
    ready = collection_ok and offline_ok and pipeline_ok
    fully_scored = ready and labels_ok and scored_ok
    gate_pass = (
        fully_scored
        and best_entries > 0
        and best_pnl > 0.0
        and best_delta > 0.0
        and not best_rejection
    )
    if gate_pass:
        decision = "cumulative_bounded_gate_pass"
    elif fully_scored and (locked_entries > 0 or best_entries > 0):
        decision = "cumulative_bounded_scored_with_entries"
    elif fully_scored:
        decision = "cumulative_bounded_scored_no_rv600_entries"
    elif ready and not labels_ok:
        decision = "cumulative_bounded_pending_settlement_or_scoring"
    else:
        decision = "cumulative_bounded_incomplete_or_failed"
    report = {
        "schema_version": "rv600-bounded-cumulative-audit-v1",
        "generated_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "research_only": True,
        "decision": decision,
        "collection_ok": collection_ok,
        "offline_v28_context_ok": offline_ok,
        "pipeline_ok": pipeline_ok,
        "labels_ok": labels_ok,
        "scored_ok": scored_ok,
        "root_rows": root_rows,
        "summary": {
            "root_count": len(roots),
            "candidate_rows": _int(opportunity.get("total_candidate_rows")),
            "settled_markets": _int(opportunity.get("total_settled_markets")),
            "locked_total_entries": locked_entries,
            "locked_total_pnl_cents": locked_pnl,
            "best_grid_variant": best_grid.get("variant"),
            "best_grid_accepted_entries": best_entries,
            "best_grid_distinct_markets": _int(best_grid.get("distinct_markets")),
            "best_grid_selected_pnl_cents": best_pnl,
            "best_grid_matched_v28_delta_cents": best_delta,
            "best_grid_rejection": best_rejection,
            "best_locked_variant": best_locked.get("variant"),
            "best_locked_accepted_entries": _int(best_locked.get("accepted_entries")),
            "best_locked_selected_pnl_cents": _float(best_locked.get("selected_pnl_cents")),
            "best_locked_matched_v28_delta_cents": _float(best_locked.get("matched_v28_delta_cents")),
            "best_locked_rejection": best_locked.get("rejection_reason") or "",
        },
        "interpretation": _interpretation(decision, locked_pnl, best_pnl, best_rejection),
        "inputs": {
            "roots": [str(root) for root in roots],
            "refresh_jsons": [str(path) for path in refresh_jsons],
            "opportunity_json": str(opportunity_path) if opportunity_path is not None else "",
            "min_checkpoint_rows": int(args.min_checkpoint_rows),
        },
    }
    return report


def _interpretation(decision: str, locked_pnl: float, best_pnl: float, best_rejection: str) -> str:
    if decision == "cumulative_bounded_gate_pass":
        return (
            "Cumulative bounded read-only evidence has a positive RV600-style candidate with no current "
            "gate rejection. Run the full objective completion audit before treating it as complete."
        )
    if decision == "cumulative_bounded_scored_with_entries":
        return (
            "Cumulative bounded read-only evidence has accepted RV600-style entries "
            f"(locked_pnl_cents={locked_pnl}, best_grid_pnl_cents={best_pnl}), but the best row is still "
            f"gate-rejected: {best_rejection or 'none'}."
        )
    if decision == "cumulative_bounded_pending_settlement_or_scoring":
        return "Cumulative bounded evidence is collected, but labels or opportunity scoring are incomplete."
    if decision == "cumulative_bounded_scored_no_rv600_entries":
        return "Cumulative bounded evidence is fully scored but produced zero accepted RV600 entries."
    return "Cumulative bounded evidence failed collection, offline-context, pipeline, label, or scoring checks."


def _markdown(report: dict[str, Any]) -> str:
    summary = report["summary"]
    lines = [
        "# RV600 Bounded Cumulative Audit",
        "",
        f"- generated_utc: {report['generated_utc']}",
        f"- research_only: {report['research_only']}",
        f"- decision: {report['decision']}",
        f"- collection_ok: {report['collection_ok']}",
        f"- offline_v28_context_ok: {report['offline_v28_context_ok']}",
        f"- pipeline_ok: {report['pipeline_ok']}",
        f"- labels_ok: {report['labels_ok']}",
        f"- scored_ok: {report['scored_ok']}",
        "",
        "## Summary",
        "",
        f"- root_count: {summary['root_count']}",
        f"- candidate_rows: {summary['candidate_rows']}",
        f"- settled_markets: {summary['settled_markets']}",
        f"- locked_total_entries: {summary['locked_total_entries']}",
        f"- locked_total_pnl_cents: {summary['locked_total_pnl_cents']}",
        f"- best_grid_variant: `{summary['best_grid_variant']}`",
        f"- best_grid_accepted_entries: {summary['best_grid_accepted_entries']}",
        f"- best_grid_distinct_markets: {summary['best_grid_distinct_markets']}",
        f"- best_grid_selected_pnl_cents: {summary['best_grid_selected_pnl_cents']}",
        f"- best_grid_matched_v28_delta_cents: {summary['best_grid_matched_v28_delta_cents']}",
        f"- best_grid_rejection: `{summary['best_grid_rejection']}`",
        f"- best_locked_variant: `{summary['best_locked_variant']}`",
        f"- best_locked_accepted_entries: {summary['best_locked_accepted_entries']}",
        f"- best_locked_selected_pnl_cents: {summary['best_locked_selected_pnl_cents']}",
        f"- best_locked_matched_v28_delta_cents: {summary['best_locked_matched_v28_delta_cents']}",
        f"- best_locked_rejection: `{summary['best_locked_rejection']}`",
        "",
        "## Roots",
        "",
        "| root | checkpoints | spot_ticks | spot_issues | offline_contexts | offline_issues | pipeline_contexts | pipeline_issues |",
        "|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for row in report["root_rows"]:
        lines.append(
            f"| `{row['root']}` | {row['checkpoint_row_count']} | {row['independent_spot_row_count']} | "
            f"{row['independent_spot_issue_count']} | "
            f"{row['offline_contexts_written']} | {row['offline_context_issues']} | "
            f"{row['pipeline_contexts_written']} | {row['pipeline_context_issues']} |"
        )
    lines.extend(["", "## Interpretation", "", report["interpretation"], ""])
    return "\n".join(lines)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Audit cumulative bounded RV600 next-evidence roots.")
    parser.add_argument("--root", action="append", type=Path, default=[])
    parser.add_argument("--refresh-json", action="append", type=Path, default=[])
    parser.add_argument("--opportunity-json", type=Path)
    parser.add_argument("--base-dir", type=Path, default=DEFAULT_REAL_SHADOW_DIR)
    parser.add_argument("--reports-dir", type=Path, default=DEFAULT_REPORTS_DIR)
    parser.add_argument("--min-root-name", default=DEFAULT_MIN_ROOT_NAME)
    parser.add_argument("--min-checkpoint-rows", type=int, default=300)
    parser.add_argument("--output-json", type=Path, default=DEFAULT_OUTPUT_JSON)
    parser.add_argument("--output-md", type=Path, default=DEFAULT_OUTPUT_MD)
    parser.add_argument("--write", action="store_true")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    report = build_report(args)
    if args.write:
        args.output_json.parent.mkdir(parents=True, exist_ok=True)
        args.output_json.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        args.output_md.write_text(_markdown(report), encoding="utf-8")
    summary = report["summary"]
    print(f"decision={report['decision']}")
    print(f"root_count={summary['root_count']}")
    print(f"candidate_rows={summary['candidate_rows']}")
    print(f"settled_markets={summary['settled_markets']}")
    print(f"locked_total_entries={summary['locked_total_entries']}")
    print(f"locked_total_pnl_cents={summary['locked_total_pnl_cents']:.4f}")
    print(f"best_grid_variant={summary['best_grid_variant']}")
    print(f"best_grid_pnl_cents={summary['best_grid_selected_pnl_cents']:.4f}")
    print(f"best_grid_rejection={summary['best_grid_rejection']}")
    if args.write:
        print(f"output_json={args.output_json}")
        print(f"output_md={args.output_md}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
