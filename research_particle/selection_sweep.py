from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass, replace
from pathlib import Path
from typing import Any, Sequence

from .replay_runner import (
    FillPolicy,
    ReplayConfig,
    ReplayInput,
    evaluate_replay,
    load_replay_inputs_from_jsonl,
)


@dataclass(frozen=True)
class SelectionSweepRow:
    min_ev_cents: float
    min_fill_prob: float
    candidate_count: int
    selected_count: int
    coverage_rate: float
    total_counterfactual_pnl_cents: float
    avg_counterfactual_pnl_cents_per_selected: float
    selected_win_rate: float
    top_ev_bucket_pnl_cents: float
    ev_rank_correlation_sign: float
    particle_beats_brownian: bool
    particle_beats_market: bool
    particle_beats_current_calibrated: bool


@dataclass(frozen=True)
class SelectionSweepReport:
    all_candidate_denominator: bool
    source_candidate_count: int | None
    skipped_unlabeled_count: int
    denominator_scope: str
    min_ev_grid: tuple[float, ...]
    min_fill_grid: tuple[float, ...]
    rows: tuple[SelectionSweepRow, ...]
    best_positive_row: SelectionSweepRow | None
    positive_nonzero_rows: int


def evaluate_selection_sweep(
    rows: Sequence[ReplayInput],
    *,
    min_ev_grid: Sequence[float],
    min_fill_grid: Sequence[float],
    no_fill_penalty_cents: float = 0.0,
    counterfactual_fill_policy: FillPolicy = "threshold",
    counterfactual_fill_threshold: float = 0.5,
) -> SelectionSweepReport:
    if not rows:
        raise ValueError("at least one replay row is required")
    if not min_ev_grid:
        raise ValueError("min_ev_grid cannot be empty")
    if not min_fill_grid:
        raise ValueError("min_fill_grid cannot be empty")
    sweep_rows: list[SelectionSweepRow] = []
    for min_fill in min_fill_grid:
        for min_ev in min_ev_grid:
            report = evaluate_replay(
                rows,
                ReplayConfig(
                    min_ev_cents=float(min_ev),
                    min_fill_prob=float(min_fill),
                    no_fill_penalty_cents=no_fill_penalty_cents,
                    counterfactual_fill_policy=counterfactual_fill_policy,
                    counterfactual_fill_threshold=counterfactual_fill_threshold,
                ),
            )
            selected = [decision for decision in report.decisions if decision.selected]
            wins = sum(1 for decision in selected if decision.won)
            sweep_rows.append(
                SelectionSweepRow(
                    min_ev_cents=float(min_ev),
                    min_fill_prob=float(min_fill),
                    candidate_count=report.candidate_count,
                    selected_count=report.selected_count,
                    coverage_rate=report.selected_count / report.candidate_count,
                    total_counterfactual_pnl_cents=report.total_counterfactual_pnl_cents,
                    avg_counterfactual_pnl_cents_per_selected=(
                        report.avg_counterfactual_pnl_cents_per_selected
                    ),
                    selected_win_rate=(wins / len(selected) if selected else 0.0),
                    top_ev_bucket_pnl_cents=report.top_ev_bucket_pnl_cents,
                    ev_rank_correlation_sign=report.ev_rank_correlation_sign,
                    particle_beats_brownian=report.particle_beats_brownian,
                    particle_beats_market=report.particle_beats_market,
                    particle_beats_current_calibrated=report.particle_beats_current_calibrated,
                )
            )
    positive_rows = [
        row
        for row in sweep_rows
        if row.selected_count > 0 and row.total_counterfactual_pnl_cents > 0.0
    ]
    best = max(
        positive_rows,
        key=lambda row: (
            row.total_counterfactual_pnl_cents,
            row.coverage_rate,
            row.avg_counterfactual_pnl_cents_per_selected,
        ),
        default=None,
    )
    return SelectionSweepReport(
        all_candidate_denominator=True,
        source_candidate_count=len(rows),
        skipped_unlabeled_count=0,
        denominator_scope="all_labeled_candidates",
        min_ev_grid=tuple(float(value) for value in min_ev_grid),
        min_fill_grid=tuple(float(value) for value in min_fill_grid),
        rows=tuple(sweep_rows),
        best_positive_row=best,
        positive_nonzero_rows=len(positive_rows),
    )


def write_selection_sweep_report(
    report: SelectionSweepReport,
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
        description="Sweep predeclared EV/fill thresholds on a strict particle replay denominator."
    )
    parser.add_argument("--candidates", required=True, type=Path)
    parser.add_argument("--labels", required=True, type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--stem", default="selection_sweep")
    parser.add_argument(
        "--min-ev-grid",
        default="0,1,2,3,5,8,10,15,20",
        help="comma-separated EV thresholds in cents",
    )
    parser.add_argument(
        "--min-fill-grid",
        default="0,0.25,0.5,0.75,1.0",
        help="comma-separated fill probability thresholds",
    )
    parser.add_argument("--no-fill-penalty-cents", default=0.0, type=float)
    parser.add_argument(
        "--counterfactual-fill-policy",
        choices=["threshold", "always_fill", "never_fill"],
        default="threshold",
    )
    parser.add_argument("--counterfactual-fill-threshold", default=0.5, type=float)
    parser.add_argument("--default-annualized-vol", default=None, type=float)
    parser.add_argument(
        "--allow-missing-labels",
        action="store_true",
        help="explicitly run on the resolved/labeled subset and report skipped unlabeled candidate rows",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    replay_rows = load_replay_inputs_from_jsonl(
        args.candidates,
        args.labels,
        default_annualized_vol=args.default_annualized_vol,
        allow_missing_labels=bool(args.allow_missing_labels),
    )
    source_candidate_count = _line_count(args.candidates)
    report = replace(
        evaluate_selection_sweep(
            replay_rows,
            min_ev_grid=_parse_float_grid(args.min_ev_grid, "min_ev_grid"),
            min_fill_grid=_parse_float_grid(args.min_fill_grid, "min_fill_grid"),
            no_fill_penalty_cents=args.no_fill_penalty_cents,
            counterfactual_fill_policy=args.counterfactual_fill_policy,
            counterfactual_fill_threshold=args.counterfactual_fill_threshold,
        ),
        source_candidate_count=source_candidate_count,
        skipped_unlabeled_count=max(0, source_candidate_count - len(replay_rows)),
        denominator_scope=(
            "resolved_labeled_subset" if args.allow_missing_labels else "all_labeled_candidates"
        ),
    )
    json_path, md_path = write_selection_sweep_report(report, args.output_dir, args.stem)
    print(f"grid_rows={len(report.rows)}")
    print(f"source_candidate_count={report.source_candidate_count}")
    print(f"skipped_unlabeled_count={report.skipped_unlabeled_count}")
    print(f"denominator_scope={report.denominator_scope}")
    print(f"positive_nonzero_rows={report.positive_nonzero_rows}")
    if report.best_positive_row is not None:
        print(f"best_positive_min_ev_cents={report.best_positive_row.min_ev_cents:.4f}")
        print(f"best_positive_min_fill_prob={report.best_positive_row.min_fill_prob:.4f}")
        print(
            "best_positive_total_counterfactual_pnl_cents="
            f"{report.best_positive_row.total_counterfactual_pnl_cents:.4f}"
        )
    print(f"json_report={json_path}")
    print(f"md_report={md_path}")
    return 0


def _parse_float_grid(raw: str, name: str) -> list[float]:
    values: list[float] = []
    for item in raw.split(","):
        item = item.strip()
        if not item:
            continue
        values.append(float(item))
    if not values:
        raise ValueError(f"{name} cannot be empty")
    return values


def _line_count(path: Path) -> int:
    with path.open("r", encoding="utf-8", errors="replace") as handle:
        return sum(1 for line in handle if line.strip())


def _markdown(report: SelectionSweepReport) -> str:
    lines = [
        "# Particle Selection Sweep",
        "",
        f"- all_candidate_denominator: {report.all_candidate_denominator}",
        f"- source_candidate_count: {report.source_candidate_count if report.source_candidate_count is not None else (report.rows[0].candidate_count if report.rows else 0)}",
        f"- skipped_unlabeled_count: {report.skipped_unlabeled_count}",
        f"- denominator_scope: {report.denominator_scope}",
        f"- grid_rows: {len(report.rows)}",
        f"- positive_nonzero_rows: {report.positive_nonzero_rows}",
    ]
    if report.best_positive_row is None:
        lines.append("- best_positive_row: none")
    else:
        row = report.best_positive_row
        lines.extend(
            [
                f"- best_positive_min_ev_cents: {row.min_ev_cents:.4f}",
                f"- best_positive_min_fill_prob: {row.min_fill_prob:.4f}",
                f"- best_positive_total_pnl_cents: {row.total_counterfactual_pnl_cents:.4f}",
                f"- best_positive_selected_count: {row.selected_count}",
            ]
        )
    lines.extend(
        [
            "",
            "| min_ev_cents | min_fill_prob | selected | coverage | total_pnl_cents | avg_selected_pnl | win_rate | top_ev_bucket_pnl |",
            "|---:|---:|---:|---:|---:|---:|---:|---:|",
        ]
    )
    for row in report.rows:
        lines.append(
            "| "
            f"{row.min_ev_cents:.4f} | "
            f"{row.min_fill_prob:.4f} | "
            f"{row.selected_count} | "
            f"{row.coverage_rate:.4f} | "
            f"{row.total_counterfactual_pnl_cents:.4f} | "
            f"{row.avg_counterfactual_pnl_cents_per_selected:.4f} | "
            f"{row.selected_win_rate:.4f} | "
            f"{row.top_ev_bucket_pnl_cents:.4f} |"
        )
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    raise SystemExit(main())
