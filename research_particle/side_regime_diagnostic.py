from __future__ import annotations

import argparse
import json
import re
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence
from zoneinfo import ZoneInfo


@dataclass(frozen=True)
class BucketRow:
    bucket_type: str
    bucket: str
    selected_count: int
    win_count: int
    win_rate: float
    total_counterfactual_pnl_cents: float
    avg_counterfactual_pnl_cents: float


@dataclass(frozen=True)
class RuleRunRow:
    run: str
    rule: str
    selected_count: int
    win_count: int
    win_rate: float
    total_counterfactual_pnl_cents: float


@dataclass(frozen=True)
class RuleSummaryRow:
    rule: str
    run_count: int
    positive_run_count: int
    nonzero_run_count: int
    selected_count: int
    total_counterfactual_pnl_cents: float
    min_run_pnl_cents: float
    stable_positive: bool


@dataclass(frozen=True)
class SideRegimeDiagnosticReport:
    source_reports: tuple[str, ...]
    run_count: int
    selected_count: int
    total_counterfactual_pnl_cents: float
    bucket_rows: tuple[BucketRow, ...]
    rule_run_rows: tuple[RuleRunRow, ...]
    rule_summary_rows: tuple[RuleSummaryRow, ...]
    stable_positive_rules: tuple[str, ...]
    conclusion: str


def build_side_regime_diagnostic(report_paths: Sequence[Path]) -> SideRegimeDiagnosticReport:
    if not report_paths:
        raise ValueError("at least one replay report is required")
    run_decisions = [
        (_run_name(path), _load_decisions(path))
        for path in report_paths
    ]
    if any(not decisions for _, decisions in run_decisions):
        raise ValueError("each replay report must include decisions")
    selected = [
        decision
        for _, decisions in run_decisions
        for decision in decisions
        if decision.get("selected")
    ]
    bucket_rows = tuple(_build_bucket_rows(selected))
    rule_run_rows = tuple(_build_rule_run_rows(run_decisions))
    rule_summary_rows = tuple(_summarize_rules(rule_run_rows, run_count=len(run_decisions)))
    stable_rules = tuple(row.rule for row in rule_summary_rows if row.stable_positive)
    conclusion = (
        "At least one diagnostic rule is positive in every supplied run; treat it as a "
        "candidate for a fresh locked OOS plan, not as promotion evidence."
        if stable_rules
        else "No predeclared side/regime diagnostic rule is positive in every supplied run."
    )
    return SideRegimeDiagnosticReport(
        source_reports=tuple(str(path) for path in report_paths),
        run_count=len(run_decisions),
        selected_count=len(selected),
        total_counterfactual_pnl_cents=_sum_pnl(selected),
        bucket_rows=bucket_rows,
        rule_run_rows=rule_run_rows,
        rule_summary_rows=rule_summary_rows,
        stable_positive_rules=stable_rules,
        conclusion=conclusion,
    )


def write_side_regime_diagnostic(
    report: SideRegimeDiagnosticReport,
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
        description="Diagnose side/regime instability from strict particle replay report decisions."
    )
    parser.add_argument("--report", action="append", required=True, type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--stem", default="side_regime_diagnostic")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    report = build_side_regime_diagnostic(args.report)
    json_path, md_path = write_side_regime_diagnostic(report, args.output_dir, args.stem)
    print(f"run_count={report.run_count}")
    print(f"selected_count={report.selected_count}")
    print(f"total_counterfactual_pnl_cents={report.total_counterfactual_pnl_cents:.4f}")
    print(f"stable_positive_rules={len(report.stable_positive_rules)}")
    if report.stable_positive_rules:
        print("stable_rule_names=" + ",".join(report.stable_positive_rules))
    print(f"json_report={json_path}")
    print(f"md_report={md_path}")
    return 0


def _build_bucket_rows(selected: Sequence[Mapping[str, Any]]) -> list[BucketRow]:
    rows: list[BucketRow] = []
    for bucket_type, labeler in (
        ("side", lambda row: str(row.get("side") or "none")),
        ("consensus", _consensus_bucket),
        ("confidence", _confidence_bucket),
        ("time_to_close", _time_bucket),
    ):
        grouped: dict[str, list[Mapping[str, Any]]] = {}
        for decision in selected:
            grouped.setdefault(labeler(decision), []).append(decision)
        for bucket in sorted(grouped):
            rows.append(_bucket_row(bucket_type, bucket, grouped[bucket]))
    return rows


def _build_rule_run_rows(
    run_decisions: Sequence[tuple[str, Sequence[Mapping[str, Any]]]],
) -> list[RuleRunRow]:
    rules = {
        "base": lambda row: True,
        "require_market_agreement": _agrees_market,
        "require_current_agreement": _agrees_current,
        "require_market_current_consensus_alignment": _agrees_market_current_consensus,
        "skip_against_consensus_any": lambda row: not _against_market_current_consensus(row, 0.0),
        "skip_against_consensus_05": lambda row: not _against_market_current_consensus(row, 0.05),
        "skip_against_consensus_10": lambda row: not _against_market_current_consensus(row, 0.10),
        "skip_against_consensus_20": lambda row: not _against_market_current_consensus(row, 0.20),
        "skip_late_300s_against_consensus_05": (
            lambda row: not (
                _seconds_to_close(row) is not None
                and _seconds_to_close(row) <= 300.0
                and _against_market_current_consensus(row, 0.05)
            )
        ),
    }
    rows: list[RuleRunRow] = []
    for run, decisions in run_decisions:
        selected = [decision for decision in decisions if decision.get("selected")]
        for rule, keep in rules.items():
            kept = [decision for decision in selected if keep(decision)]
            wins = sum(1 for decision in kept if decision.get("won"))
            rows.append(
                RuleRunRow(
                    run=run,
                    rule=rule,
                    selected_count=len(kept),
                    win_count=wins,
                    win_rate=(wins / len(kept) if kept else 0.0),
                    total_counterfactual_pnl_cents=_sum_pnl(kept),
                )
            )
    return rows


def _summarize_rules(
    rows: Sequence[RuleRunRow],
    *,
    run_count: int,
) -> list[RuleSummaryRow]:
    grouped: dict[str, list[RuleRunRow]] = {}
    for row in rows:
        grouped.setdefault(row.rule, []).append(row)
    summaries: list[RuleSummaryRow] = []
    for rule in sorted(grouped):
        rule_rows = grouped[rule]
        total_pnl = sum(row.total_counterfactual_pnl_cents for row in rule_rows)
        min_pnl = min((row.total_counterfactual_pnl_cents for row in rule_rows), default=0.0)
        positive = sum(1 for row in rule_rows if row.total_counterfactual_pnl_cents > 0.0)
        nonzero = sum(1 for row in rule_rows if row.selected_count > 0)
        summaries.append(
            RuleSummaryRow(
                rule=rule,
                run_count=len(rule_rows),
                positive_run_count=positive,
                nonzero_run_count=nonzero,
                selected_count=sum(row.selected_count for row in rule_rows),
                total_counterfactual_pnl_cents=total_pnl,
                min_run_pnl_cents=min_pnl,
                stable_positive=(
                    len(rule_rows) == run_count
                    and nonzero == run_count
                    and positive == run_count
                ),
            )
        )
    return sorted(
        summaries,
        key=lambda row: (
            row.stable_positive,
            row.positive_run_count,
            row.total_counterfactual_pnl_cents,
        ),
        reverse=True,
    )


def _bucket_row(bucket_type: str, bucket: str, rows: Sequence[Mapping[str, Any]]) -> BucketRow:
    wins = sum(1 for row in rows if row.get("won"))
    pnl = _sum_pnl(rows)
    return BucketRow(
        bucket_type=bucket_type,
        bucket=bucket,
        selected_count=len(rows),
        win_count=wins,
        win_rate=(wins / len(rows) if rows else 0.0),
        total_counterfactual_pnl_cents=pnl,
        avg_counterfactual_pnl_cents=(pnl / len(rows) if rows else 0.0),
    )


def _consensus_bucket(row: Mapping[str, Any]) -> str:
    side = str(row.get("side") or "")
    market_side = _side_from_probability(row, "market_p_yes")
    current_side = _side_from_probability(row, "current_calibrated_p_yes")
    if market_side != current_side:
        return "market_current_disagree"
    if side == market_side:
        return "aligned_with_market_current"
    return "against_market_current"


def _confidence_bucket(row: Mapping[str, Any]) -> str:
    if _against_market_current_consensus(row, 0.20):
        return "against_strong_20pp_consensus"
    if _against_market_current_consensus(row, 0.10):
        return "against_strong_10pp_consensus"
    if _against_market_current_consensus(row, 0.05):
        return "against_strong_05pp_consensus"
    if _agrees_market_current_consensus(row):
        return "aligned_consensus"
    return "mixed_or_weak"


def _time_bucket(row: Mapping[str, Any]) -> str:
    seconds = _seconds_to_close(row)
    if seconds is None:
        return "unknown"
    if seconds <= 60:
        return "000_060s"
    if seconds <= 180:
        return "061_180s"
    if seconds <= 300:
        return "181_300s"
    if seconds <= 600:
        return "301_600s"
    return "gt_600s"


def _agrees_market(row: Mapping[str, Any]) -> bool:
    return str(row.get("side") or "") == _side_from_probability(row, "market_p_yes")


def _agrees_current(row: Mapping[str, Any]) -> bool:
    return str(row.get("side") or "") == _side_from_probability(row, "current_calibrated_p_yes")


def _agrees_market_current_consensus(row: Mapping[str, Any]) -> bool:
    market_side = _side_from_probability(row, "market_p_yes")
    current_side = _side_from_probability(row, "current_calibrated_p_yes")
    return market_side == current_side and str(row.get("side") or "") == market_side


def _against_market_current_consensus(row: Mapping[str, Any], min_confidence: float) -> bool:
    market_side = _side_from_probability(row, "market_p_yes")
    current_side = _side_from_probability(row, "current_calibrated_p_yes")
    if market_side != current_side:
        return False
    if str(row.get("side") or "") == market_side:
        return False
    return min(_prob_confidence(row, "market_p_yes"), _prob_confidence(row, "current_calibrated_p_yes")) >= min_confidence


def _side_from_probability(row: Mapping[str, Any], field: str) -> str:
    return "yes" if float(row.get(field) or 0.0) >= 0.5 else "no"


def _prob_confidence(row: Mapping[str, Any], field: str) -> float:
    return abs(float(row.get(field) or 0.0) - 0.5)


def _seconds_to_close(row: Mapping[str, Any]) -> float | None:
    decision_ts = _parse_dt(str(row.get("decision_ts_utc") or ""))
    close_ts = _close_time_from_market_ticker(str(row.get("market_ticker") or ""))
    if decision_ts is None or close_ts is None:
        return None
    return max(0.0, (close_ts - decision_ts).total_seconds())


def _close_time_from_market_ticker(ticker: str) -> datetime | None:
    match = re.search(r"-(\d{2})([A-Z]{3})(\d{2})(\d{4})-", ticker.upper())
    if not match:
        return None
    year = 2000 + int(match.group(1))
    month = {
        "JAN": 1,
        "FEB": 2,
        "MAR": 3,
        "APR": 4,
        "MAY": 5,
        "JUN": 6,
        "JUL": 7,
        "AUG": 8,
        "SEP": 9,
        "OCT": 10,
        "NOV": 11,
        "DEC": 12,
    }[match.group(2)]
    day = int(match.group(3))
    hhmm = match.group(4)
    local = datetime(
        year,
        month,
        day,
        int(hhmm[:2]),
        int(hhmm[2:]),
        tzinfo=ZoneInfo("America/New_York"),
    )
    return local.astimezone(timezone.utc)


def _parse_dt(value: str) -> datetime | None:
    if not value:
        return None
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def _load_decisions(path: Path) -> list[Mapping[str, Any]]:
    payload = json.loads(path.read_text(encoding="utf-8", errors="replace"))
    decisions = payload.get("decisions")
    if not isinstance(decisions, list):
        raise ValueError(f"{path} does not contain a decisions list")
    return [row for row in decisions if isinstance(row, Mapping)]


def _run_name(path: Path) -> str:
    try:
        return path.parent.parent.name
    except Exception:
        return path.stem


def _sum_pnl(rows: Iterable[Mapping[str, Any]]) -> float:
    return sum(float(row.get("counterfactual_pnl_cents") or 0.0) for row in rows)


def _markdown(report: SideRegimeDiagnosticReport) -> str:
    lines = [
        "# Side/Regime Diagnostic",
        "",
        f"- run_count: {report.run_count}",
        f"- selected_count: {report.selected_count}",
        f"- total_counterfactual_pnl_cents: {report.total_counterfactual_pnl_cents:.4f}",
        f"- stable_positive_rules: {len(report.stable_positive_rules)}",
        f"- conclusion: {report.conclusion}",
        "",
        "## Rule Summary",
        "",
        "| rule | positive_runs | selected | total_pnl_cents | min_run_pnl_cents | stable_positive |",
        "|---|---:|---:|---:|---:|---|",
    ]
    for row in report.rule_summary_rows:
        lines.append(
            "| "
            f"{row.rule} | "
            f"{row.positive_run_count}/{row.run_count} | "
            f"{row.selected_count} | "
            f"{row.total_counterfactual_pnl_cents:.4f} | "
            f"{row.min_run_pnl_cents:.4f} | "
            f"{row.stable_positive} |"
        )
    lines.extend(
        [
            "",
            "## Buckets",
            "",
            "| type | bucket | selected | win_rate | total_pnl_cents | avg_pnl_cents |",
            "|---|---|---:|---:|---:|---:|",
        ]
    )
    for row in report.bucket_rows:
        lines.append(
            "| "
            f"{row.bucket_type} | "
            f"{row.bucket} | "
            f"{row.selected_count} | "
            f"{row.win_rate:.4f} | "
            f"{row.total_counterfactual_pnl_cents:.4f} | "
            f"{row.avg_counterfactual_pnl_cents:.4f} |"
        )
    lines.extend(
        [
            "",
            "## Rule By Run",
            "",
            "| run | rule | selected | win_rate | pnl_cents |",
            "|---|---|---:|---:|---:|",
        ]
    )
    for row in report.rule_run_rows:
        lines.append(
            "| "
            f"{row.run} | "
            f"{row.rule} | "
            f"{row.selected_count} | "
            f"{row.win_rate:.4f} | "
            f"{row.total_counterfactual_pnl_cents:.4f} |"
        )
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    raise SystemExit(main())
