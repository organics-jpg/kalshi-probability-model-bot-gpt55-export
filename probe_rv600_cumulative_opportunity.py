from __future__ import annotations

import argparse
from datetime import datetime, timezone
from pathlib import Path

from probe_rv600_bounded_cumulative_audit import _int, _load_json, _refresh_path
from probe_rv600_native_forward_opportunity import build_report, write_report


DEFAULT_REAL_SHADOW_DIR = Path("logs/particle_research/real_shadow")
DEFAULT_REPORTS_DIR = Path("logs/particle_research/reports")
DEFAULT_ROOT_PREFIX = "rv600_next_evidence_shadow_"
DEFAULT_MIN_ROOT_NAME = "rv600_next_evidence_shadow_20260513T195001Z"
DEFAULT_MIN_DECISION_TS_UTC = "2026-05-13T19:50:00+00:00"
DEFAULT_OUTPUT_JSON = Path(
    "logs/particle_research/reports/rv600_next_evidence_shadow_cumulative_latest_opportunity.json"
)
DEFAULT_OUTPUT_MD = Path(
    "logs/particle_research/reports/rv600_next_evidence_shadow_cumulative_latest_opportunity.md"
)


def discover_roots(base_dir: Path, reports_dir: Path, min_root_name: str) -> tuple[Path, ...]:
    if not base_dir.exists():
        return ()
    roots: list[Path] = []
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
            root / "pipeline_work" / "label_contexts_full_refresh.ndjson",
        )
        if all(path.exists() for path in required):
            roots.append(root)
    return tuple(roots)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build an RV600 cumulative opportunity report from settled bounded roots."
    )
    parser.add_argument("--root", action="append", type=Path, default=[])
    parser.add_argument("--base-dir", type=Path, default=DEFAULT_REAL_SHADOW_DIR)
    parser.add_argument("--reports-dir", type=Path, default=DEFAULT_REPORTS_DIR)
    parser.add_argument("--min-root-name", default=DEFAULT_MIN_ROOT_NAME)
    parser.add_argument("--min-decision-ts-utc", default=DEFAULT_MIN_DECISION_TS_UTC)
    parser.add_argument("--output-json", type=Path, default=DEFAULT_OUTPUT_JSON)
    parser.add_argument("--output-md", type=Path, default=DEFAULT_OUTPUT_MD)
    parser.add_argument("--write", action="store_true")
    return parser.parse_args(argv)


def _parse_dt(value: str) -> datetime:
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    roots = tuple(
        args.root
        or discover_roots(args.base_dir, args.reports_dir, args.min_root_name)
    )
    report = build_report(
        roots,
        min_decision_ts_utc=(_parse_dt(args.min_decision_ts_utc) if args.min_decision_ts_utc else None),
        output_json=args.output_json,
        output_md=args.output_md,
    )
    if args.write:
        write_report(report)
    print(f"roots={len(report.roots)}")
    print(f"total_candidate_rows={report.total_candidate_rows}")
    print(f"total_settled_markets={report.total_settled_markets}")
    print(f"locked_total_entries={report.locked_total_entries}")
    print(f"locked_total_pnl_cents={report.locked_total_pnl_cents:.4f}")
    if report.best_grid_candidate:
        print(f"best_grid_candidate={report.best_grid_candidate.variant}")
        print(f"best_grid_pnl_cents={report.best_grid_candidate.selected_pnl_cents:.4f}")
        print(f"best_grid_rejection={report.best_grid_candidate.rejection_reason}")
    print(f"conclusion={report.conclusion}")
    if args.write:
        print(f"output_json={args.output_json}")
        print(f"output_md={args.output_md}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
