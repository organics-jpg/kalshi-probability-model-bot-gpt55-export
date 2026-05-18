from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping, Sequence

from .meta_probability_loro import _find_label_path
from .replay_runner import _parse_candidate_payload, _read_jsonl, load_settlement_labels_jsonl


@dataclass(frozen=True)
class DenominatorIntegrityRunRow:
    run: str
    root: str
    candidate_path: str
    label_path: str
    report_path: str
    candidate_file_count: int
    candidate_market_count: int
    label_count: int
    report_candidate_count: int
    report_source_candidate_count: int
    report_decision_count: int
    report_skipped_unlabeled_count: int
    report_denominator_scope: str
    report_all_candidate_denominator: bool
    missing_label_market_count: int
    count_mismatch: bool
    issue_count: int
    pass_denominator_integrity: bool


@dataclass(frozen=True)
class DenominatorIntegrityAuditReport:
    generated_utc: str
    report_name: str
    run_rows: tuple[DenominatorIntegrityRunRow, ...]
    skipped_run_roots: tuple[str, ...]
    run_count: int
    candidate_count: int
    market_count: int
    issue_count: int
    pass_denominator_integrity: bool
    conclusion: str


def build_denominator_integrity_audit(
    run_roots: Sequence[Path],
    *,
    report_name: str = "passive_particle_replay_locked_oos.json",
) -> DenominatorIntegrityAuditReport:
    if not run_roots:
        raise ValueError("at least one run root is required")
    rows: list[DenominatorIntegrityRunRow] = []
    skipped: list[str] = []
    for root in run_roots:
        candidate_path = root / "candidate_snapshots" / "candidate_snapshots.ndjson"
        report_path = root / "reports" / report_name
        if not candidate_path.exists() or not report_path.exists():
            skipped.append(str(root))
            continue
        try:
            label_path = _find_label_path(root)
        except FileNotFoundError:
            skipped.append(str(root))
            continue
        rows.append(_audit_run(root, candidate_path, label_path, report_path))
    total_issues = sum(row.issue_count for row in rows)
    passed = bool(rows) and total_issues == 0
    conclusion = (
        "All audited replay reports preserve the all-candidate denominator."
        if passed
        else "One or more audited replay reports do not preserve the all-candidate denominator."
    )
    return DenominatorIntegrityAuditReport(
        generated_utc=datetime.now(timezone.utc).isoformat(),
        report_name=report_name,
        run_rows=tuple(rows),
        skipped_run_roots=tuple(skipped),
        run_count=len(rows),
        candidate_count=sum(row.candidate_file_count for row in rows),
        market_count=sum(row.candidate_market_count for row in rows),
        issue_count=total_issues,
        pass_denominator_integrity=passed,
        conclusion=conclusion,
    )


def write_denominator_integrity_audit(
    report: DenominatorIntegrityAuditReport,
    output_dir: Path,
    stem: str,
) -> tuple[Path, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    json_path = output_dir / f"{stem}.json"
    md_path = output_dir / f"{stem}.md"
    json_path.write_text(json.dumps(asdict(report), indent=2, sort_keys=True), encoding="utf-8")
    md_path.write_text(_markdown(report), encoding="utf-8")
    return json_path, md_path


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Audit replay reports for strict all-candidate denominator integrity."
    )
    parser.add_argument("--run-root", action="append", required=True, type=Path)
    parser.add_argument("--report-name", default="passive_particle_replay_locked_oos.json")
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--stem", default="denominator_integrity_audit")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    report = build_denominator_integrity_audit(args.run_root, report_name=args.report_name)
    json_path, md_path = write_denominator_integrity_audit(report, args.output_dir, args.stem)
    print(f"run_count={report.run_count}")
    print(f"skipped_run_count={len(report.skipped_run_roots)}")
    print(f"candidate_count={report.candidate_count}")
    print(f"market_count={report.market_count}")
    print(f"issue_count={report.issue_count}")
    print(f"pass_denominator_integrity={report.pass_denominator_integrity}")
    print(f"json_report={json_path}")
    print(f"md_report={md_path}")
    return 0


def _audit_run(
    root: Path,
    candidate_path: Path,
    label_path: Path,
    report_path: Path,
) -> DenominatorIntegrityRunRow:
    candidate_markets = _candidate_markets(candidate_path)
    label_markets = {label.market_ticker for label in load_settlement_labels_jsonl(label_path)}
    payload = json.loads(report_path.read_text(encoding="utf-8", errors="replace"))
    report_candidate_count = int(payload.get("candidate_count", 0) or 0)
    source_value = payload.get("source_candidate_count")
    report_source_candidate_count = (
        report_candidate_count
        if source_value in (None, "")
        else int(source_value)
    )
    decisions = payload.get("decisions") or []
    report_decision_count = len(decisions) if isinstance(decisions, list) else 0
    skipped_unlabeled = int(payload.get("skipped_unlabeled_count", 0) or 0)
    denominator_scope = str(payload.get("denominator_scope") or "all_labeled_candidates")
    all_candidate_denominator = bool(payload.get("all_candidate_denominator"))
    missing_label_count = len(candidate_markets - label_markets)
    candidate_file_count = _line_count(candidate_path)
    count_mismatch = not (
        candidate_file_count
        == report_source_candidate_count
        == report_candidate_count
        == report_decision_count
    )
    issue_count = sum(
        (
            int(count_mismatch),
            int(skipped_unlabeled != 0),
            int(denominator_scope != "all_labeled_candidates"),
            int(not all_candidate_denominator),
            int(missing_label_count != 0),
        )
    )
    return DenominatorIntegrityRunRow(
        run=root.name,
        root=str(root),
        candidate_path=str(candidate_path),
        label_path=str(label_path),
        report_path=str(report_path),
        candidate_file_count=candidate_file_count,
        candidate_market_count=len(candidate_markets),
        label_count=len(label_markets),
        report_candidate_count=report_candidate_count,
        report_source_candidate_count=report_source_candidate_count,
        report_decision_count=report_decision_count,
        report_skipped_unlabeled_count=skipped_unlabeled,
        report_denominator_scope=denominator_scope,
        report_all_candidate_denominator=all_candidate_denominator,
        missing_label_market_count=missing_label_count,
        count_mismatch=count_mismatch,
        issue_count=issue_count,
        pass_denominator_integrity=(issue_count == 0 and candidate_file_count > 0),
    )


def _candidate_markets(path: Path) -> set[str]:
    markets: set[str] = set()
    for payload in _read_jsonl(path):
        snapshot, _ = _parse_candidate_payload(payload)
        markets.add(snapshot.market_ticker)
    return markets


def _line_count(path: Path) -> int:
    with path.open("r", encoding="utf-8", errors="replace") as handle:
        return sum(1 for line in handle if line.strip())


def _markdown(report: DenominatorIntegrityAuditReport) -> str:
    lines = [
        "# Denominator Integrity Audit",
        "",
        f"- generated_utc: {report.generated_utc}",
        f"- report_name: {report.report_name}",
        f"- run_count: {report.run_count}",
        f"- skipped_run_count: {len(report.skipped_run_roots)}",
        f"- candidate_count: {report.candidate_count}",
        f"- market_count: {report.market_count}",
        f"- issue_count: {report.issue_count}",
        f"- pass_denominator_integrity: {report.pass_denominator_integrity}",
        f"- conclusion: {report.conclusion}",
        "",
        "## Runs",
        "",
        "| run | candidate_file | report_source | report_candidates | decisions | markets | labels | skipped_unlabeled | scope | all_candidate | missing_label_markets | count_mismatch | issues | pass |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---|---|---:|---|---:|---|",
    ]
    for row in report.run_rows:
        lines.append(
            "| "
            f"{row.run} | "
            f"{row.candidate_file_count} | "
            f"{row.report_source_candidate_count} | "
            f"{row.report_candidate_count} | "
            f"{row.report_decision_count} | "
            f"{row.candidate_market_count} | "
            f"{row.label_count} | "
            f"{row.report_skipped_unlabeled_count} | "
            f"{row.report_denominator_scope} | "
            f"{row.report_all_candidate_denominator} | "
            f"{row.missing_label_market_count} | "
            f"{row.count_mismatch} | "
            f"{row.issue_count} | "
            f"{row.pass_denominator_integrity} |"
        )
    if report.skipped_run_roots:
        lines.extend(["", "## Skipped Runs", ""])
        for root in report.skipped_run_roots:
            lines.append(f"- `{root}`")
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    raise SystemExit(main())
