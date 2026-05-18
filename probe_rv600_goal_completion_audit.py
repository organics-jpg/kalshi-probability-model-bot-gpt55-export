"""Strict completion audit for the RV600 strategy-variation goal.

Research-only. This probe reads docs and research reports, writes an audit
report, and never touches live bot state, launchers, orders, or v28 logic.
"""
from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable, Mapping


ROOT = Path(__file__).resolve().parent
REPORT_DIR = ROOT / "logs" / "particle_research" / "reports"
REAL_SHADOW_DIR = ROOT / "logs" / "particle_research" / "real_shadow"

PLAN_MD = ROOT / "docs" / "research" / "RV600_VARIATION_TEST_PLAN.md"
LOCKED_NOTE_MD = ROOT / "docs" / "research" / "RV600_LOCKED_CANDIDATES_2026-05-13.md"
HARNESS_PY = ROOT / "research_particle" / "rv600_variation_test.py"
TEST_PY = ROOT / "test_research_particle_synthetic.py"

FIRST_JSON = REPORT_DIR / "rv600_variation_test_latest.json"
GRID_JSON = REPORT_DIR / "rv600_variation_grid_latest.json"
LOCKED_JSON = REPORT_DIR / "rv600_variation_locked_latest.json"
FORWARD_JSON = REPORT_DIR / "rv600_variation_forward_latest.json"

AUDIT_JSON = REPORT_DIR / "rv600_goal_completion_audit_latest.json"
AUDIT_MD = REPORT_DIR / "rv600_goal_completion_audit_latest.md"


@dataclass(frozen=True)
class ChecklistItem:
    requirement: str
    status: str
    evidence: str
    next_action: str


def audit(root: Path = ROOT) -> dict[str, Any]:
    first = _load_json(root / _rel(FIRST_JSON))
    grid = _load_json(root / _rel(GRID_JSON))
    locked = _load_json(root / _rel(LOCKED_JSON))
    forward_report = _load_json(root / _rel(FORWARD_JSON))
    root_census = _real_shadow_census(root / _rel(REAL_SHADOW_DIR))
    locked_forward = _forward_sample_stats(root, forward_report)
    locked_best = _best_locked_row(locked)
    locked_candidates = locked.get("locked_candidates") or []
    checklist = _build_checklist(
        root=root,
        first=first,
        grid=grid,
        locked=locked,
        locked_best=locked_best,
        locked_candidates=locked_candidates,
        root_census=root_census,
        locked_forward=locked_forward,
    )
    status_counts = _status_counts(checklist)
    achieved = bool(checklist) and all(item.status == "pass" for item in checklist)
    return {
        "schema_version": "rv600-goal-completion-audit-v1",
        "generated_utc": _utc_now(),
        "objective": (
            "Build and validate RV600 strategy variations from "
            "docs/research/RV600_VARIATION_TEST_PLAN.md with research-only "
            "execution, fair repeated-entry accounting after fees/fills, "
            "matched v28 controls, anti-overfitting gates, and moderate "
            "incoming-market shadow validation before completion."
        ),
        "goal_complete": achieved,
        "status_counts": status_counts,
        "best_locked_candidate": locked.get("best_locked_candidate", ""),
        "forward_report": _rel(FORWARD_JSON).as_posix(),
        "locked_candidate_count": len(locked_candidates),
        "best_locked_row": locked_best,
        "forward_shadow_sample": locked_forward,
        "real_shadow_census": root_census,
        "checklist": [asdict(item) for item in checklist],
        "conclusion": _conclusion(achieved, checklist, locked_best, locked_forward),
    }


def _build_checklist(
    *,
    root: Path,
    first: Mapping[str, Any],
    grid: Mapping[str, Any],
    locked: Mapping[str, Any],
    locked_best: Mapping[str, Any],
    locked_candidates: list[Any],
    root_census: Mapping[str, Any],
    locked_forward: Mapping[str, Any],
) -> list[ChecklistItem]:
    items: list[ChecklistItem] = []

    items.append(
        _item(
            "Named RV600 variation plan exists and is the source of truth",
            "pass" if (root / _rel(PLAN_MD)).exists() else "fail",
            f"plan={_rel(PLAN_MD)} exists={(root / _rel(PLAN_MD)).exists()}",
            "Restore or write the RV600 variation plan before auditing implementation.",
        )
    )
    items.append(
        _item(
            "Research-only implementation path exists; no live launcher/v28 order logic is required",
            "pass" if (root / _rel(HARNESS_PY)).exists() and (root / _rel(LOCKED_NOTE_MD)).exists() else "fail",
            (
                f"harness={_rel(HARNESS_PY)} exists={(root / _rel(HARNESS_PY)).exists()}; "
                f"locked_note={_rel(LOCKED_NOTE_MD)} exists={(root / _rel(LOCKED_NOTE_MD)).exists()}; "
                "audit probe is read/report only"
            ),
            "Keep RV600 work in research reports and shadow scoring; do not edit live launchers or order logic.",
        )
    )
    items.append(
        _item(
            "First candidate set from the plan was built and scored",
            "pass" if first.get("phase") == "first_candidates" and int(first.get("variant_count") or 0) >= 6 else "fail",
            (
                f"report={_rel(FIRST_JSON)} phase={first.get('phase')}; "
                f"variant_count={first.get('variant_count')}; root_count={first.get('root_count')}"
            ),
            "Run `python -m research_particle.rv600_variation_test --phase first_candidates --write`.",
        )
    )
    items.append(
        _item(
            "Phase 1 grid explored timing, EV, repeated-entry, side/control/regime/micro/price variants",
            "pass" if grid.get("phase") == "grid" and int(grid.get("variant_count") or 0) >= 100 else "fail",
            (
                f"report={_rel(GRID_JSON)} phase={grid.get('phase')}; "
                f"variant_count={grid.get('variant_count')}; root_count={grid.get('root_count')}"
            ),
            "Run the grid phase and inspect rejected high-PnL rows with gate reasons.",
        )
    )
    items.append(
        _item(
            "Locked Phase 2 candidate set contains at most five simple candidates",
            "pass" if locked.get("phase") == "locked" and 1 <= len(locked_candidates) <= 5 else "fail",
            (
                f"report={_rel(LOCKED_JSON)} phase={locked.get('phase')}; "
                f"locked_candidate_count={len(locked_candidates)}; candidates={locked_candidates}"
            ),
            "Freeze at most five simple candidates from the grid before any forward-shadow scoring.",
        )
    )
    items.append(
        _item(
            "Fair repeated-entry accounting is present for all_entries, one_per_side_per_market, and position_capped",
            "pass" if _has_accounting_modes(locked, {"all_entries", "one_per_side_per_market", "position_capped"}) else "fail",
            f"accounting_modes={sorted(_accounting_modes(locked))}",
            "Extend the report to emit all three repeated-entry accounting modes.",
        )
    )
    items.append(
        _item(
            "Best locked candidate is profitable after fees/fills and not only profitable under all_entries",
            "pass"
            if locked_best.get("accounting_mode") != "all_entries" and float(locked_best.get("selected_pnl_cents") or 0.0) > 0.0
            else "fail",
            (
                f"variant={locked_best.get('variant')}; accounting={locked_best.get('accounting_mode')}; "
                f"selected_pnl_cents={locked_best.get('selected_pnl_cents')}; "
                f"fill_adjusted_expected_pnl_cents={locked_best.get('fill_adjusted_expected_pnl_cents')}"
            ),
            "Keep the candidate research-only until non-all_entries accounting remains positive.",
        )
    )
    items.append(
        _item(
            "Matched v28/current control is scored on the same accepted timestamps and beaten by at least 20%",
            "pass" if _beats_v28_by_20pct(locked_best) else "fail",
            (
                f"selected_pnl_cents={locked_best.get('selected_pnl_cents')}; "
                f"matched_v28_control_pnl_cents={locked_best.get('matched_v28_control_pnl_cents')}; "
                f"matched_v28_delta_cents={locked_best.get('matched_v28_delta_cents')}"
            ),
            "Keep matched timestamp controls in every locked and forward-shadow report.",
        )
    )
    items.append(
        _item(
            "Anti-overfitting gates pass retrospectively: roots/markets, recent window, concentration, added entries",
            "pass" if _retrospective_gates_pass(locked_best) else "fail",
            (
                f"positive_root_rate={locked_best.get('positive_root_rate')}; "
                f"positive_market_rate={locked_best.get('positive_market_rate')}; "
                f"max_single_market_pnl_share={locked_best.get('max_single_market_pnl_share')}; "
                f"last_window_pnl_cents={locked_best.get('last_window_pnl_cents')}; "
                f"avg_added_entry_pnl_cents={locked_best.get('avg_added_entry_pnl_cents')}; "
                f"rejection_reason={locked_best.get('rejection_reason')!r}"
            ),
            "Reject or simplify any candidate that fails the anti-overfitting gates.",
        )
    )
    items.append(
        _item(
            "Incoming live markets are moderately validated in shadow mode",
            "pass" if _forward_shadow_pass(locked_forward) else "fail",
            (
                f"accepted_entries={locked_forward.get('accepted_entries')}; "
                f"distinct_markets={locked_forward.get('distinct_markets')}; "
                f"calendar_days={locked_forward.get('calendar_days')}; "
                f"weekend_days={locked_forward.get('weekend_days')}; "
                f"source={locked_forward.get('source')}; "
                f"latest_labeled_root_update={root_census.get('latest_labeled_root_update')}"
            ),
            "Collect/label fresh RV600 locked forward-shadow markets until the plan's sample gates pass.",
        )
    )
    items.append(
        _item(
            "Forward-shadow evidence is not only sparse sidecar or fallback-vol artifacts",
            "pass" if _forward_source_quality_pass(locked_forward) else "fail",
            (
                f"native_candidate_rows={locked_forward.get('native_candidate_rows')}; "
                f"native_distinct_markets={locked_forward.get('native_distinct_markets')}; "
                f"sidecar_candidate_rows={locked_forward.get('sidecar_candidate_rows')}; "
                f"sidecar_distinct_markets={locked_forward.get('sidecar_distinct_markets')}; "
                f"source_quality_note={locked_forward.get('source_quality_note')}"
            ),
            (
                "Collect native/continuous RV600 forward roots with matching current-control "
                "contexts; sparse sidecar snapshots are diagnostic only for completion."
            ),
        )
    )
    items.append(
        _item(
            "Forward-shadow PnL is positive and passes the same artifact checks",
            "pass" if _forward_shadow_pnl_pass(locked_forward) else "fail",
            (
                f"selected_pnl_cents={locked_forward.get('selected_pnl_cents')}; "
                f"matched_v28_control_pnl_cents={locked_forward.get('matched_v28_control_pnl_cents')}; "
                f"avg_pnl_per_entry_cents={locked_forward.get('avg_pnl_per_entry_cents')}; "
                f"max_single_market_pnl_share={locked_forward.get('max_single_market_pnl_share')}; "
                f"last_window_pnl_cents={locked_forward.get('last_window_pnl_cents')}"
            ),
            "Do not mark the goal complete until fresh shadow PnL clears all promotion gates.",
        )
    )
    items.append(
        _item(
            "Regression coverage verifies repeated-entry and matched-control accounting",
            "pass" if _test_mentions_rv600(root / _rel(TEST_PY)) else "fail",
            f"test_file={_rel(TEST_PY)} mentions_rv600_variation={_test_mentions_rv600(root / _rel(TEST_PY))}",
            "Add or restore the synthetic RV600 accounting regression test.",
        )
    )
    return items


def write_audit(report: Mapping[str, Any], *, json_path: Path = AUDIT_JSON, md_path: Path = AUDIT_MD) -> tuple[Path, Path]:
    json_path.parent.mkdir(parents=True, exist_ok=True)
    md_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    md_path.write_text(_markdown(report), encoding="utf-8")
    return json_path, md_path


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Audit RV600 goal completion against concrete artifacts.")
    parser.add_argument("--json", type=Path, default=AUDIT_JSON)
    parser.add_argument("--md", type=Path, default=AUDIT_MD)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    report = audit(ROOT)
    json_path, md_path = write_audit(report, json_path=args.json, md_path=args.md)
    print(f"goal_complete={report['goal_complete']}")
    print(f"best_locked_candidate={report['best_locked_candidate']}")
    print(f"status_counts={report['status_counts']}")
    print(f"conclusion={report['conclusion']}")
    print(f"json_report={json_path}")
    print(f"md_report={md_path}")
    return 0


def _best_locked_row(locked: Mapping[str, Any]) -> Mapping[str, Any]:
    rows = [
        row for row in locked.get("summary_rows", [])
        if row.get("locked_candidate_eligible")
    ]
    if not rows:
        rows = list(locked.get("summary_rows", []))
    if not rows:
        return {}
    return max(rows, key=lambda row: float(row.get("selected_pnl_cents") or 0.0))


def _forward_sample_stats(root: Path, forward_report: Mapping[str, Any]) -> dict[str, Any]:
    best = _best_locked_row(forward_report)
    roots = list(forward_report.get("roots") or [])
    dates: set[str] = set()
    weekend_dates: set[str] = set()
    latest_root_update = ""
    for root_name in roots:
        run_root = root / "logs" / "particle_research" / "real_shadow" / str(root_name)
        candidate_path = run_root / "candidate_snapshots" / "candidate_snapshots.ndjson"
        if run_root.exists():
            latest_root_update = max(latest_root_update, _mtime_tree_iso(run_root))
        for ts in _candidate_timestamps(candidate_path):
            date = ts.date().isoformat()
            dates.add(date)
            if ts.weekday() >= 5:
                weekend_dates.add(date)
    source_stats = _candidate_source_stats(
        root / "logs" / "particle_research" / "real_shadow",
        roots,
    )
    return {
        "source": _rel(FORWARD_JSON).as_posix(),
        "report_exists": bool(forward_report),
        "report_phase": forward_report.get("phase", ""),
        "report_root_count": int(forward_report.get("root_count") or 0),
        "accepted_entries": int(best.get("accepted_entries") or 0),
        "distinct_markets": int(best.get("distinct_markets") or 0),
        "calendar_days": len(dates),
        "weekend_days": len(weekend_dates),
        "decision_dates": sorted(dates),
        "weekend_decision_dates": sorted(weekend_dates),
        "latest_root_update": latest_root_update,
        "selected_pnl_cents": float(best.get("selected_pnl_cents") or 0.0),
        "matched_v28_control_pnl_cents": float(best.get("matched_v28_control_pnl_cents") or 0.0),
        "avg_pnl_per_entry_cents": float(best.get("avg_pnl_per_entry_cents") or 0.0),
        "avg_pnl_per_market_cents": float(best.get("avg_pnl_per_market_cents") or 0.0),
        "max_single_market_pnl_share": float(best.get("max_single_market_pnl_share") or 0.0),
        "last_window_pnl_cents": float(best.get("last_window_pnl_cents") or 0.0),
        "positive_market_rate": float(best.get("positive_market_rate") or 0.0),
        **source_stats,
        "note": (
            "This forward report is intended to be generated with "
            "`--phase locked --min-decision-ts-utc <candidate-freeze-time>` so "
            "it contains only post-lock incoming-market shadow evidence."
        ),
    }


def _real_shadow_census(base_dir: Path) -> dict[str, Any]:
    roots = []
    latest_labeled_update = ""
    if base_dir.exists():
        for path in sorted(base_dir.iterdir(), key=lambda p: p.name):
            if not path.is_dir():
                continue
            candidates = path / "candidate_snapshots" / "candidate_snapshots.ndjson"
            labels = path / "pipeline_work" / "label_contexts_full_refresh.ndjson"
            has_candidates = candidates.exists()
            has_labels = labels.exists()
            updated = _mtime_tree_iso(path)
            if has_candidates and has_labels:
                latest_labeled_update = max(latest_labeled_update, updated)
            roots.append(
                {
                    "root": path.name,
                    "has_candidates": has_candidates,
                    "has_labels": has_labels,
                    "updated": updated,
                }
            )
    return {
        "root_count": len(roots),
        "candidate_and_label_root_count": sum(1 for row in roots if row["has_candidates"] and row["has_labels"]),
        "latest_labeled_root_update": latest_labeled_update,
        "roots": roots,
    }


def _item(requirement: str, status: str, evidence: str, next_action: str) -> ChecklistItem:
    if status not in {"pass", "partial", "fail"}:
        raise ValueError(f"invalid status: {status}")
    return ChecklistItem(requirement, status, evidence, next_action)


def _has_accounting_modes(report: Mapping[str, Any], required: set[str]) -> bool:
    return required.issubset(_accounting_modes(report))


def _accounting_modes(report: Mapping[str, Any]) -> set[str]:
    return {str(row.get("accounting_mode")) for row in report.get("summary_rows", []) if row.get("accounting_mode")}


def _beats_v28_by_20pct(row: Mapping[str, Any]) -> bool:
    selected = float(row.get("selected_pnl_cents") or 0.0)
    control = float(row.get("matched_v28_control_pnl_cents") or 0.0)
    if selected <= 0.0:
        return False
    if control <= 0.0:
        return True
    return selected >= 1.20 * control


def _retrospective_gates_pass(row: Mapping[str, Any]) -> bool:
    return (
        float(row.get("selected_pnl_cents") or 0.0) > 0.0
        and float(row.get("avg_pnl_per_entry_cents") or 0.0) >= 10.0
        and float(row.get("avg_pnl_per_market_cents") or 0.0) > 0.0
        and float(row.get("avg_added_entry_pnl_cents") or 0.0) > 0.0
        and float(row.get("positive_root_rate") or 0.0) >= 0.60
        and float(row.get("positive_market_rate") or 0.0) >= 0.60
        and float(row.get("max_single_market_pnl_share") or 0.0) <= 0.25
        and float(row.get("last_window_pnl_cents") or 0.0) > 0.0
        and str(row.get("rejection_reason") or "") == ""
    )


def _forward_shadow_pass(stats: Mapping[str, Any]) -> bool:
    return (
        int(stats.get("accepted_entries") or 0) >= 100
        and int(stats.get("distinct_markets") or 0) >= 40
        and int(stats.get("calendar_days") or 0) >= 10
        and int(stats.get("weekend_days") or 0) >= 2
    )


def _forward_source_quality_pass(stats: Mapping[str, Any]) -> bool:
    return (
        int(stats.get("native_candidate_rows") or 0) >= 100
        and int(stats.get("native_distinct_markets") or 0) >= 40
    )


def _forward_shadow_pnl_pass(stats: Mapping[str, Any]) -> bool:
    selected = float(stats.get("selected_pnl_cents") or 0.0)
    control = float(stats.get("matched_v28_control_pnl_cents") or 0.0)
    return (
        _forward_shadow_pass(stats)
        and selected > 0.0
        and (control <= 0.0 or selected >= 1.20 * control)
        and float(stats.get("avg_pnl_per_entry_cents") or 0.0) >= 10.0
        and float(stats.get("avg_pnl_per_market_cents") or 0.0) > 0.0
        and float(stats.get("max_single_market_pnl_share") or 0.0) <= 0.25
        and float(stats.get("last_window_pnl_cents") or 0.0) > 0.0
        and float(stats.get("positive_market_rate") or 0.0) >= 0.60
        and _forward_source_quality_pass(stats)
    )


def _test_mentions_rv600(path: Path) -> bool:
    if not path.exists():
        return False
    text = path.read_text(encoding="utf-8", errors="replace")
    return "test_rv600_variation_test_accounts_for_repeated_entries_and_matched_v28" in text


def _status_counts(checklist: Iterable[ChecklistItem]) -> dict[str, int]:
    counts = {"pass": 0, "partial": 0, "fail": 0}
    for item in checklist:
        counts[item.status] = counts.get(item.status, 0) + 1
    return counts


def _conclusion(
    achieved: bool,
    checklist: Iterable[ChecklistItem],
    best: Mapping[str, Any],
    forward: Mapping[str, Any],
) -> str:
    if achieved:
        return "RV600 objective is complete against the audited artifacts."
    failed = [item.requirement for item in checklist if item.status != "pass"]
    return (
        "RV600 objective is not complete. Retrospective locked candidate "
        f"{best.get('variant', 'none')} is available, but remaining blockers are: "
        f"{'; '.join(failed)}. Current forward-shadow sample is "
        f"{forward.get('accepted_entries')} entries, {forward.get('distinct_markets')} markets, "
        f"{forward.get('calendar_days')} calendar days, {forward.get('weekend_days')} weekend days."
    )


def _candidate_timestamps(path: Path) -> Iterable[datetime]:
    if not path.exists():
        return ()
    def gen() -> Iterable[datetime]:
        with path.open("r", encoding="utf-8", errors="replace") as handle:
            for line in handle:
                line = line.strip()
                if not line:
                    continue
                try:
                    payload = json.loads(line)
                    raw = payload.get("snapshot", payload)
                    yield _parse_dt(raw["decision_ts_utc"])
                except Exception:
                    continue
    return gen()


def _candidate_source_stats(base_dir: Path, roots: Iterable[Any]) -> dict[str, Any]:
    counts = {
        "candidate_rows": 0,
        "native_candidate_rows": 0,
        "sidecar_candidate_rows": 0,
        "other_candidate_rows": 0,
    }
    markets = {
        "native": set(),
        "sidecar": set(),
        "other": set(),
    }
    for root_name in roots:
        root_name_str = str(root_name)
        candidate_path = base_dir / root_name_str / "candidate_snapshots" / "candidate_snapshots.ndjson"
        if not candidate_path.exists():
            continue
        with candidate_path.open("r", encoding="utf-8", errors="replace") as handle:
            for line in handle:
                line = line.strip()
                if not line:
                    continue
                try:
                    payload = json.loads(line)
                    raw = payload.get("snapshot", payload)
                    market = str(raw.get("market_ticker") or "")
                    decision_shadow = str(payload.get("decision_shadow") or "").lower()
                    extra = payload.get("extra") if isinstance(payload.get("extra"), Mapping) else {}
                    tier = str(extra.get("source_quality_tier") or "").lower()
                except Exception:
                    continue
                source = _candidate_source_bucket(root_name_str, decision_shadow, tier)
                counts["candidate_rows"] += 1
                counts[f"{source}_candidate_rows"] += 1
                if market:
                    markets[source].add(market)
    sidecar = counts["sidecar_candidate_rows"]
    native = counts["native_candidate_rows"]
    if sidecar and not native:
        note = "forward report currently relies on sparse sidecar snapshots; native continuous RV600 evidence is still missing"
    elif sidecar:
        note = "forward report mixes native and sidecar evidence; completion should rely on native continuous rows"
    elif native:
        note = "forward report includes native continuous candidate rows"
    else:
        note = "no forward candidate rows found in audited roots"
    return {
        **counts,
        "native_distinct_markets": len(markets["native"]),
        "sidecar_distinct_markets": len(markets["sidecar"]),
        "other_distinct_markets": len(markets["other"]),
        "source_quality_note": note,
    }


def _candidate_source_bucket(root_name: str, decision_shadow: str, tier: str) -> str:
    text = f"{root_name} {decision_shadow} {tier}".lower()
    if "sidecar" in text:
        return "sidecar"
    if "native" in text or "passive" in text:
        return "native"
    return "other"


def _parse_dt(value: Any) -> datetime:
    parsed = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def _mtime_iso(path: Path) -> str:
    if not path.exists():
        return ""
    return datetime.fromtimestamp(path.stat().st_mtime, tz=timezone.utc).replace(microsecond=0).isoformat()


def _mtime_tree_iso(path: Path) -> str:
    if not path.exists():
        return ""
    latest = path.stat().st_mtime
    if path.is_dir():
        for child in path.rglob("*"):
            try:
                latest = max(latest, child.stat().st_mtime)
            except OSError:
                continue
    return datetime.fromtimestamp(latest, tz=timezone.utc).replace(microsecond=0).isoformat()


def _load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8", errors="replace"))


def _rel(path: Path) -> Path:
    try:
        return path.resolve().relative_to(ROOT)
    except ValueError:
        return path


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _markdown(report: Mapping[str, Any]) -> str:
    lines = [
        "# RV600 Goal Completion Audit",
        "",
        f"- generated_utc: {report.get('generated_utc')}",
        f"- goal_complete: {report.get('goal_complete')}",
        f"- best_locked_candidate: {report.get('best_locked_candidate')}",
        f"- locked_candidate_count: {report.get('locked_candidate_count')}",
        f"- status_counts: {report.get('status_counts')}",
        f"- conclusion: {report.get('conclusion')}",
        "",
        "## Forward Shadow Sample",
        "",
    ]
    forward = report.get("forward_shadow_sample") or {}
    for key in (
        "accepted_entries",
        "distinct_markets",
        "calendar_days",
        "weekend_days",
        "selected_pnl_cents",
        "matched_v28_control_pnl_cents",
        "latest_root_update",
        "native_candidate_rows",
        "sidecar_candidate_rows",
        "source_quality_note",
    ):
        lines.append(f"- {key}: {forward.get(key)}")
    lines.extend(
        [
            "",
            "## Checklist",
            "",
            "| status | requirement | evidence | next action |",
            "|---|---|---|---|",
        ]
    )
    for item in report.get("checklist", []):
        lines.append(
            "| {status} | {requirement} | {evidence} | {next_action} |".format(
                status=item.get("status", ""),
                requirement=_escape_md(item.get("requirement", "")),
                evidence=_escape_md(item.get("evidence", "")),
                next_action=_escape_md(item.get("next_action", "")),
            )
        )
    return "\n".join(lines) + "\n"


def _escape_md(value: Any) -> str:
    return str(value).replace("|", "\\|").replace("\n", " ")


if __name__ == "__main__":
    raise SystemExit(main())
