from __future__ import annotations

import argparse
from dataclasses import replace
from pathlib import Path

from .materialized_variant_replay import materialize_variant_rows
from .replay_runner import load_replay_inputs_from_jsonl
from .selection_sweep import (
    evaluate_selection_sweep,
    write_selection_sweep_report,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Sweep EV/fill thresholds after materializing a named diagnostic probability variant."
    )
    parser.add_argument("--candidates", required=True, type=Path)
    parser.add_argument("--labels", required=True, type=Path)
    parser.add_argument("--variant", required=True)
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--stem", default=None)
    parser.add_argument("--min-ev-grid", default="0,1,2,3,5,8,10,12,15,20")
    parser.add_argument("--min-fill-grid", default="0")
    parser.add_argument("--no-fill-penalty-cents", default=0.0, type=float)
    parser.add_argument(
        "--counterfactual-fill-policy",
        choices=["threshold", "always_fill", "never_fill"],
        default="threshold",
    )
    parser.add_argument("--counterfactual-fill-threshold", default=0.5, type=float)
    parser.add_argument("--default-annualized-vol", default=None, type=float)
    parser.add_argument("--allow-missing-labels", action="store_true")
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
    materialized_rows = materialize_variant_rows(replay_rows, args.variant)
    report = replace(
        evaluate_selection_sweep(
            materialized_rows,
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
    stem = args.stem or f"selection_sweep_{_safe_stem(args.variant)}"
    json_path, md_path = write_selection_sweep_report(report, args.output_dir, stem)
    print(f"variant={args.variant}")
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
    values = [float(item.strip()) for item in raw.split(",") if item.strip()]
    if not values:
        raise ValueError(f"{name} cannot be empty")
    return values


def _line_count(path: Path) -> int:
    with path.open("r", encoding="utf-8", errors="replace") as handle:
        return sum(1 for line in handle if line.strip())


def _safe_stem(value: str) -> str:
    return "".join(ch if ch.isalnum() or ch in {"_", "-"} else "_" for ch in value)


if __name__ == "__main__":
    raise SystemExit(main())
