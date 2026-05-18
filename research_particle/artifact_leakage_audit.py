from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

from .meta_probability_loro import _find_label_path
from .replay_runner import _parse_candidate_payload, _parse_dt, _read_jsonl, load_settlement_labels_jsonl


@dataclass(frozen=True)
class ArtifactLeakageRunRow:
    run: str
    root: str
    candidate_path: str
    label_path: str
    candidate_count: int
    label_count: int
    market_count: int
    missing_label_count: int
    candidate_recv_after_decision_count: int
    label_available_at_or_before_decision_count: int
    settlement_at_or_before_decision_count: int
    future_extra_timestamp_count: int
    issue_count: int
    pass_no_future_leakage: bool


@dataclass(frozen=True)
class ArtifactLeakageAuditReport:
    generated_utc: str
    run_rows: tuple[ArtifactLeakageRunRow, ...]
    skipped_run_roots: tuple[str, ...]
    run_count: int
    candidate_count: int
    label_count: int
    market_count: int
    issue_count: int
    pass_no_future_leakage: bool
    conclusion: str


def build_artifact_leakage_audit(run_roots: Sequence[Path]) -> ArtifactLeakageAuditReport:
    if not run_roots:
        raise ValueError("at least one run root is required")
    rows: list[ArtifactLeakageRunRow] = []
    skipped: list[str] = []
    for root in run_roots:
        candidate_path = root / "candidate_snapshots" / "candidate_snapshots.ndjson"
        if not candidate_path.exists():
            skipped.append(str(root))
            continue
        try:
            label_path = _find_label_path(root)
        except FileNotFoundError:
            skipped.append(str(root))
            continue
        rows.append(_audit_run(root, candidate_path, label_path))
    total_issues = sum(row.issue_count for row in rows)
    passed = bool(rows) and total_issues == 0
    conclusion = (
        "All audited candidate/label artifacts passed strict no-future-leakage checks."
        if passed
        else "One or more audited candidate/label artifacts failed or were unavailable for strict no-future checks."
    )
    return ArtifactLeakageAuditReport(
        generated_utc=datetime.now(timezone.utc).isoformat(),
        run_rows=tuple(rows),
        skipped_run_roots=tuple(skipped),
        run_count=len(rows),
        candidate_count=sum(row.candidate_count for row in rows),
        label_count=sum(row.label_count for row in rows),
        market_count=len(
            {
                f"{row.run}:{market}"
                for row in rows
                for market in _markets_from_candidate_file(Path(row.candidate_path))
            }
        ),
        issue_count=total_issues,
        pass_no_future_leakage=passed,
        conclusion=conclusion,
    )


def write_artifact_leakage_audit(
    report: ArtifactLeakageAuditReport,
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
        description="Audit real candidate/label artifacts for strict timestamp-available replay safety."
    )
    parser.add_argument("--run-root", action="append", required=True, type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--stem", default="artifact_leakage_audit")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    report = build_artifact_leakage_audit(args.run_root)
    json_path, md_path = write_artifact_leakage_audit(report, args.output_dir, args.stem)
    print(f"run_count={report.run_count}")
    print(f"skipped_run_count={len(report.skipped_run_roots)}")
    print(f"candidate_count={report.candidate_count}")
    print(f"label_count={report.label_count}")
    print(f"market_count={report.market_count}")
    print(f"issue_count={report.issue_count}")
    print(f"pass_no_future_leakage={report.pass_no_future_leakage}")
    print(f"json_report={json_path}")
    print(f"md_report={md_path}")
    return 0


def _audit_run(root: Path, candidate_path: Path, label_path: Path) -> ArtifactLeakageRunRow:
    labels = {label.market_ticker: label for label in load_settlement_labels_jsonl(label_path)}
    candidate_count = 0
    markets: set[str] = set()
    missing_label_count = 0
    recv_after_count = 0
    label_available_count = 0
    settlement_count = 0
    future_extra_count = 0
    for payload in _read_jsonl(candidate_path):
        candidate_count += 1
        snapshot, extra = _parse_candidate_payload(payload)
        markets.add(snapshot.market_ticker)
        if snapshot.recv_ts_utc > snapshot.decision_ts_utc:
            recv_after_count += 1
        label = labels.get(snapshot.market_ticker)
        if label is None:
            missing_label_count += 1
        else:
            if label.label_available_ts_utc <= snapshot.decision_ts_utc:
                label_available_count += 1
            if label.settlement_ts_utc <= snapshot.decision_ts_utc:
                settlement_count += 1
        future_extra_count += _future_extra_timestamp_count(extra, snapshot.decision_ts_utc)
    issue_count = (
        missing_label_count
        + recv_after_count
        + label_available_count
        + settlement_count
        + future_extra_count
    )
    return ArtifactLeakageRunRow(
        run=root.name,
        root=str(root),
        candidate_path=str(candidate_path),
        label_path=str(label_path),
        candidate_count=candidate_count,
        label_count=len(labels),
        market_count=len(markets),
        missing_label_count=missing_label_count,
        candidate_recv_after_decision_count=recv_after_count,
        label_available_at_or_before_decision_count=label_available_count,
        settlement_at_or_before_decision_count=settlement_count,
        future_extra_timestamp_count=future_extra_count,
        issue_count=issue_count,
        pass_no_future_leakage=(issue_count == 0 and candidate_count > 0),
    )


def _future_extra_timestamp_count(extra: Mapping[str, Any], decision_ts_utc: datetime) -> int:
    count = 0
    for key, value in _walk_mapping(extra):
        if not _looks_like_timestamp_key(key):
            continue
        try:
            timestamp = _parse_dt(value)
        except Exception:
            continue
        if timestamp > decision_ts_utc:
            count += 1
    return count


def _walk_mapping(value: Any, prefix: str = "") -> Iterable[tuple[str, Any]]:
    if isinstance(value, Mapping):
        for key, item in value.items():
            key_text = f"{prefix}.{key}" if prefix else str(key)
            yield from _walk_mapping(item, key_text)
    elif isinstance(value, list):
        for idx, item in enumerate(value):
            yield from _walk_mapping(item, f"{prefix}[{idx}]")
    else:
        yield prefix, value


def _looks_like_timestamp_key(key: str) -> bool:
    lowered = key.lower()
    return lowered.endswith("ts_utc") or lowered.endswith("timestamp_utc") or lowered.endswith("_time_utc")


def _markets_from_candidate_file(path: Path) -> set[str]:
    markets: set[str] = set()
    for payload in _read_jsonl(path):
        raw = payload.get("snapshot", payload)
        market = raw.get("market_ticker")
        if market:
            markets.add(str(market))
    return markets


def _markdown(report: ArtifactLeakageAuditReport) -> str:
    lines = [
        "# Artifact Leakage Audit",
        "",
        f"- generated_utc: {report.generated_utc}",
        f"- run_count: {report.run_count}",
        f"- skipped_run_count: {len(report.skipped_run_roots)}",
        f"- candidate_count: {report.candidate_count}",
        f"- label_count: {report.label_count}",
        f"- market_count: {report.market_count}",
        f"- issue_count: {report.issue_count}",
        f"- pass_no_future_leakage: {report.pass_no_future_leakage}",
        f"- conclusion: {report.conclusion}",
        "",
        "## Runs",
        "",
        "| run | candidates | labels | markets | missing_labels | recv_after_decision | label_available_le_decision | settlement_le_decision | future_extra_ts | issues | pass |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|",
    ]
    for row in report.run_rows:
        lines.append(
            "| "
            f"{row.run} | "
            f"{row.candidate_count} | "
            f"{row.label_count} | "
            f"{row.market_count} | "
            f"{row.missing_label_count} | "
            f"{row.candidate_recv_after_decision_count} | "
            f"{row.label_available_at_or_before_decision_count} | "
            f"{row.settlement_at_or_before_decision_count} | "
            f"{row.future_extra_timestamp_count} | "
            f"{row.issue_count} | "
            f"{row.pass_no_future_leakage} |"
        )
    if report.skipped_run_roots:
        lines.extend(["", "## Skipped Runs", ""])
        for root in report.skipped_run_roots:
            lines.append(f"- `{root}`")
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    raise SystemExit(main())
