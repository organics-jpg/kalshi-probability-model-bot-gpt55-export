from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Sequence

from research_particle.replay_runner import ReplayConfig, load_replay_inputs_from_jsonl
from research_particle.rv600_variation_test import (
    RV600VariantSpec,
    _accepted_decisions,
    _candidate_path,
    _extras_by_key,
    _label_path,
    build_rv600_variation_report,
    grid_specs,
    locked_candidate_specs,
    materialize_rv600_metrics,
)


ROOT = Path(__file__).resolve().parent
DEFAULT_REAL_SHADOW_DIR = ROOT / "logs" / "particle_research" / "real_shadow"
DEFAULT_OUTPUT_JSON = (
    ROOT / "logs" / "particle_research" / "reports" / "rv600_native_forward_opportunity_latest.json"
)
DEFAULT_OUTPUT_MD = (
    ROOT / "logs" / "particle_research" / "reports" / "rv600_native_forward_opportunity_latest.md"
)
DEFAULT_MIN_DECISION_TS_UTC = "2026-05-13T05:37:07+00:00"


@dataclass(frozen=True)
class DecisionRow:
    market_ticker: str
    decision_ts_utc: str
    seconds_to_close: float
    side: str
    ask_cents: float
    selected_ev_cents: float
    pnl_cents: float
    matched_v28_side: str
    matched_v28_ev_cents: float
    matched_v28_pnl_cents: float
    is_added_entry: bool


@dataclass(frozen=True)
class OpportunityCandidate:
    variant: str
    accounting_mode: str
    gate_count: int
    accepted_entries: int
    distinct_markets: int
    selected_pnl_cents: float
    matched_v28_delta_cents: float
    avg_pnl_per_entry_cents: float
    positive_root_rate: float
    positive_market_rate: float
    max_single_market_pnl_share: float
    last_window_pnl_cents: float
    early_gt_420s_entries: int
    locked_70_420s_entries: int
    late_lt_70s_entries: int
    rejection_reason: str
    decisions: tuple[DecisionRow, ...]


@dataclass(frozen=True)
class RootSummary:
    root_name: str
    candidate_rows: int
    settled_markets: int
    first_decision_ts_utc: str
    last_decision_ts_utc: str


@dataclass(frozen=True)
class NativeForwardOpportunityReport:
    generated_utc: str
    schema_version: str
    roots: tuple[str, ...]
    root_summaries: tuple[RootSummary, ...]
    min_decision_ts_utc: str
    total_candidate_rows: int
    total_settled_markets: int
    best_grid_candidate: OpportunityCandidate | None
    best_rv600_primary_candidate: OpportunityCandidate | None
    best_locked_candidate: OpportunityCandidate | None
    locked_total_entries: int
    locked_total_pnl_cents: float
    conclusion: str
    output_json: str
    output_md: str


def build_report(
    roots: Sequence[Path],
    *,
    min_decision_ts_utc: datetime | None,
    output_json: Path,
    output_md: Path,
) -> NativeForwardOpportunityReport:
    selected_roots = tuple(roots) if roots else discover_native_roots()
    grid_report = build_rv600_variation_report(
        selected_roots,
        phase="grid",
        output_json=output_json,
        output_md=output_md,
        config=ReplayConfig(min_fill_prob=0.0, counterfactual_fill_threshold=0.5),
        min_decision_ts_utc=min_decision_ts_utc,
    )
    root_summaries = tuple(_root_summary(root, min_decision_ts_utc) for root in selected_roots)
    all_entries_rows = [
        row
        for row in grid_report.summary_rows
        if row.accounting_mode == "all_entries"
    ]
    best_grid = all_entries_rows[0] if all_entries_rows else None
    best_primary = next(
        (row for row in all_entries_rows if row.variant.startswith("rv600_primary_")),
        None,
    )
    locked_report = build_rv600_variation_report(
        selected_roots,
        phase="locked",
        output_json=output_json,
        output_md=output_md,
        config=ReplayConfig(min_fill_prob=0.0, counterfactual_fill_threshold=0.5),
        min_decision_ts_utc=min_decision_ts_utc,
    )
    locked_rows = [
        row for row in locked_report.summary_rows if row.accounting_mode == "all_entries"
    ]
    best_locked = locked_rows[0] if locked_rows else None
    grid_spec_by_name = {spec.name: spec for spec in grid_specs()}
    locked_spec_by_name = {spec.name: spec for spec in locked_candidate_specs()}
    best_grid_candidate = (
        _candidate_from_summary(best_grid, grid_spec_by_name, selected_roots, min_decision_ts_utc)
        if best_grid is not None
        else None
    )
    best_primary_candidate = (
        _candidate_from_summary(best_primary, grid_spec_by_name, selected_roots, min_decision_ts_utc)
        if best_primary is not None
        else None
    )
    best_locked_candidate = (
        _candidate_from_summary(best_locked, locked_spec_by_name, selected_roots, min_decision_ts_utc)
        if best_locked is not None
        else None
    )
    locked_total_entries = sum(row.accepted_entries for row in locked_rows)
    locked_total_pnl = sum(row.selected_pnl_cents for row in locked_rows)
    conclusion = _conclusion(best_grid_candidate, best_primary_candidate, locked_total_entries)
    return NativeForwardOpportunityReport(
        generated_utc=datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        schema_version="rv600-native-forward-opportunity-v1",
        roots=tuple(root.name for root in selected_roots),
        root_summaries=root_summaries,
        min_decision_ts_utc=min_decision_ts_utc.isoformat() if min_decision_ts_utc else "",
        total_candidate_rows=sum(row.candidate_rows for row in root_summaries),
        total_settled_markets=sum(row.settled_markets for row in root_summaries),
        best_grid_candidate=best_grid_candidate,
        best_rv600_primary_candidate=best_primary_candidate,
        best_locked_candidate=best_locked_candidate,
        locked_total_entries=locked_total_entries,
        locked_total_pnl_cents=locked_total_pnl,
        conclusion=conclusion,
        output_json=str(output_json),
        output_md=str(output_md),
    )


def discover_native_roots(base_dir: Path = DEFAULT_REAL_SHADOW_DIR) -> tuple[Path, ...]:
    if not base_dir.exists():
        return ()
    roots = [
        path
        for path in base_dir.iterdir()
        if path.is_dir()
        and path.name.startswith("rv600_forward_native_shadow_offline_v28_")
        and _candidate_path(path).exists()
        and _label_path(path).exists()
    ]
    return tuple(sorted(roots, key=lambda path: path.name))


def write_report(report: NativeForwardOpportunityReport) -> None:
    output_json = Path(report.output_json)
    output_md = Path(report.output_md)
    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_json.write_text(
        json.dumps(asdict(report), indent=2, sort_keys=True),
        encoding="utf-8",
    )
    output_md.write_text(_markdown(report), encoding="utf-8")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Diagnose whether current native RV600 forward roots contain real "
            "RV600 opportunity or only small-sample/proxy-v28 positives."
        )
    )
    parser.add_argument("--root", action="append", type=Path, default=[])
    parser.add_argument("--output-json", type=Path, default=DEFAULT_OUTPUT_JSON)
    parser.add_argument("--output-md", type=Path, default=DEFAULT_OUTPUT_MD)
    parser.add_argument("--min-decision-ts-utc", default=DEFAULT_MIN_DECISION_TS_UTC)
    parser.add_argument("--write", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    report = build_report(
        tuple(args.root),
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
    if report.best_rv600_primary_candidate:
        print(f"best_rv600_primary_candidate={report.best_rv600_primary_candidate.variant}")
        print(f"best_rv600_primary_pnl_cents={report.best_rv600_primary_candidate.selected_pnl_cents:.4f}")
        print(f"best_rv600_primary_rejection={report.best_rv600_primary_candidate.rejection_reason}")
    print(f"conclusion={report.conclusion}")
    if args.write:
        print(f"output_json={args.output_json}")
        print(f"output_md={args.output_md}")
    return 0


def _root_summary(root: Path, min_decision_ts_utc: datetime | None) -> RootSummary:
    rows = load_replay_inputs_from_jsonl(_candidate_path(root), _label_path(root))
    if min_decision_ts_utc is not None:
        rows = [
            row
            for row in rows
            if row.snapshot.decision_ts_utc >= min_decision_ts_utc
        ]
    timestamps = [row.snapshot.decision_ts_utc for row in rows]
    return RootSummary(
        root_name=root.name,
        candidate_rows=len(rows),
        settled_markets=len({row.snapshot.market_ticker for row in rows}),
        first_decision_ts_utc=min(timestamps).isoformat() if timestamps else "",
        last_decision_ts_utc=max(timestamps).isoformat() if timestamps else "",
    )


def _candidate_from_summary(
    summary: object,
    spec_by_name: dict[str, RV600VariantSpec],
    roots: Sequence[Path],
    min_decision_ts_utc: datetime | None,
) -> OpportunityCandidate:
    spec = spec_by_name[getattr(summary, "variant")]
    decisions = []
    for root in roots:
        rows = load_replay_inputs_from_jsonl(_candidate_path(root), _label_path(root))
        if min_decision_ts_utc is not None:
            rows = [
                row
                for row in rows
                if row.snapshot.decision_ts_utc >= min_decision_ts_utc
            ]
        if not rows:
            continue
        metrics = materialize_rv600_metrics(rows, extras_by_key=_extras_by_key(_candidate_path(root)))
        metric_by_key = {
            (metric.row.snapshot.market_ticker, metric.row.snapshot.decision_ts_utc.isoformat()): metric
            for metric in metrics
        }
        for decision in _accepted_decisions(metrics, spec, ReplayConfig()):
            metric = metric_by_key.get((decision.market_ticker, decision.decision_ts_utc.isoformat()))
            decisions.append((decision, metric.seconds_to_close if metric else 0.0))
    decision_rows = tuple(
        DecisionRow(
            market_ticker=decision.market_ticker,
            decision_ts_utc=decision.decision_ts_utc.isoformat(),
            seconds_to_close=seconds_to_close,
            side=decision.side,
            ask_cents=decision.ask_cents,
            selected_ev_cents=decision.selected_ev_cents,
            pnl_cents=decision.pnl_cents,
            matched_v28_side=decision.matched_v28_side,
            matched_v28_ev_cents=decision.matched_v28_ev_cents,
            matched_v28_pnl_cents=decision.matched_v28_pnl_cents,
            is_added_entry=decision.is_added_entry,
        )
        for decision, seconds_to_close in decisions
    )
    return OpportunityCandidate(
        variant=getattr(summary, "variant"),
        accounting_mode=getattr(summary, "accounting_mode"),
        gate_count=getattr(summary, "gate_count"),
        accepted_entries=getattr(summary, "accepted_entries"),
        distinct_markets=getattr(summary, "distinct_markets"),
        selected_pnl_cents=getattr(summary, "selected_pnl_cents"),
        matched_v28_delta_cents=getattr(summary, "matched_v28_delta_cents"),
        avg_pnl_per_entry_cents=getattr(summary, "avg_pnl_per_entry_cents"),
        positive_root_rate=getattr(summary, "positive_root_rate"),
        positive_market_rate=getattr(summary, "positive_market_rate"),
        max_single_market_pnl_share=getattr(summary, "max_single_market_pnl_share"),
        last_window_pnl_cents=getattr(summary, "last_window_pnl_cents"),
        early_gt_420s_entries=sum(1 for row in decision_rows if row.seconds_to_close > 420.0),
        locked_70_420s_entries=sum(1 for row in decision_rows if 70.0 <= row.seconds_to_close <= 420.0),
        late_lt_70s_entries=sum(1 for row in decision_rows if row.seconds_to_close < 70.0),
        rejection_reason=getattr(summary, "rejection_reason"),
        decisions=decision_rows,
    )


def _conclusion(
    best_grid: OpportunityCandidate | None,
    best_primary: OpportunityCandidate | None,
    locked_entries: int,
) -> str:
    if locked_entries <= 0:
        if best_grid and best_grid.selected_pnl_cents > 0.0:
            return (
                "Native forward roots contain a small positive existing-grid candidate, "
                "but locked RV600 candidates still take zero entries. Treat the positive "
                "row as diagnostic only until it clears sample, concentration, and "
                "matched-v28 gates."
            )
        return "Native forward roots contain no locked RV600 entries and no positive existing-grid opportunity."
    if best_primary and best_primary.selected_pnl_cents <= 0.0:
        return "Locked entries exist, but RV600-primary native forward PnL is nonpositive."
    return "Native forward roots have entries; use the full completion audit before considering the goal complete."


def _markdown(report: NativeForwardOpportunityReport) -> str:
    lines = [
        "# RV600 Native Forward Opportunity Diagnostic",
        "",
        f"- generated_utc: {report.generated_utc}",
        f"- roots: {len(report.roots)}",
        f"- total_candidate_rows: {report.total_candidate_rows}",
        f"- total_settled_markets: {report.total_settled_markets}",
        f"- locked_total_entries: {report.locked_total_entries}",
        f"- locked_total_pnl_cents: {report.locked_total_pnl_cents}",
        f"- conclusion: {report.conclusion}",
        "",
        "## Roots",
        "",
        "| root | rows | markets | first | last |",
        "|---|---:|---:|---|---|",
    ]
    for row in report.root_summaries:
        lines.append(
            f"| `{row.root_name}` | {row.candidate_rows} | {row.settled_markets} | "
            f"{row.first_decision_ts_utc} | {row.last_decision_ts_utc} |"
        )
    lines.extend(["", "## Candidates", ""])
    for title, candidate in (
        ("Best Existing-Grid Candidate", report.best_grid_candidate),
        ("Best RV600-Primary Candidate", report.best_rv600_primary_candidate),
        ("Best Locked Candidate", report.best_locked_candidate),
    ):
        lines.extend(_candidate_markdown(title, candidate))
    return "\n".join(lines) + "\n"


def _candidate_markdown(title: str, candidate: OpportunityCandidate | None) -> list[str]:
    lines = [f"### {title}", ""]
    if candidate is None:
        return lines + ["none", ""]
    lines.extend(
        [
            f"- variant: `{candidate.variant}`",
            f"- accounting_mode: {candidate.accounting_mode}",
            f"- gate_count: {candidate.gate_count}",
            f"- accepted_entries: {candidate.accepted_entries}",
            f"- distinct_markets: {candidate.distinct_markets}",
            f"- selected_pnl_cents: {candidate.selected_pnl_cents}",
            f"- matched_v28_delta_cents: {candidate.matched_v28_delta_cents}",
            f"- avg_pnl_per_entry_cents: {candidate.avg_pnl_per_entry_cents}",
            f"- positive_root_rate: {candidate.positive_root_rate}",
            f"- positive_market_rate: {candidate.positive_market_rate}",
            f"- max_single_market_pnl_share: {candidate.max_single_market_pnl_share}",
            f"- last_window_pnl_cents: {candidate.last_window_pnl_cents}",
            f"- early_gt_420s_entries: {candidate.early_gt_420s_entries}",
            f"- locked_70_420s_entries: {candidate.locked_70_420s_entries}",
            f"- late_lt_70s_entries: {candidate.late_lt_70s_entries}",
            f"- rejection_reason: {candidate.rejection_reason or 'none'}",
            "",
            "| market | decision_ts | secs_to_close | side | ask | ev | pnl | v28_side | v28_ev | v28_pnl | added |",
            "|---|---|---:|---|---:|---:|---:|---|---:|---:|---|",
        ]
    )
    for decision in candidate.decisions[:25]:
        lines.append(
            f"| `{decision.market_ticker}` | {decision.decision_ts_utc} | "
            f"{decision.seconds_to_close:.1f} | {decision.side} | "
            f"{decision.ask_cents:.2f} | {decision.selected_ev_cents:.2f} | "
            f"{decision.pnl_cents:.2f} | {decision.matched_v28_side} | "
            f"{decision.matched_v28_ev_cents:.2f} | {decision.matched_v28_pnl_cents:.2f} | "
            f"{decision.is_added_entry} |"
        )
    lines.append("")
    return lines


def _parse_dt(value: str) -> datetime:
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


if __name__ == "__main__":
    raise SystemExit(main())
