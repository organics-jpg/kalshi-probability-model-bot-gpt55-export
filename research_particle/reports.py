from __future__ import annotations

import argparse
from dataclasses import replace
from pathlib import Path

from .replay_runner import (
    ReplayConfig,
    evaluate_online_calibrated_replay,
    evaluate_replay,
    load_replay_inputs_from_jsonl,
    write_online_replay_report,
    write_replay_report,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run a strict research-only particle replay report from JSONL artifacts."
    )
    parser.add_argument("--candidates", required=True, type=Path, help="candidate_snapshots.ndjson path")
    parser.add_argument("--labels", required=True, type=Path, help="settlement_labels.ndjson path")
    parser.add_argument(
        "--output-dir",
        default=Path("logs") / "particle_research" / "reports",
        type=Path,
        help="directory for JSON and Markdown reports",
    )
    parser.add_argument("--stem", default="particle_replay_report", help="output filename stem")
    parser.add_argument("--min-ev-cents", default=0.0, type=float)
    parser.add_argument("--min-fill-prob", default=0.0, type=float)
    parser.add_argument("--no-fill-penalty-cents", default=0.0, type=float)
    parser.add_argument(
        "--counterfactual-fill-policy",
        choices=["threshold", "always_fill", "never_fill"],
        default="threshold",
    )
    parser.add_argument("--counterfactual-fill-threshold", default=0.5, type=float)
    parser.add_argument(
        "--default-annualized-vol",
        default=None,
        type=float,
        help="used only when candidate rows omit brownian_p_yes",
    )
    parser.add_argument(
        "--online-calibrated",
        action="store_true",
        help="run label-gated online calibration replay instead of static particle replay",
    )
    parser.add_argument(
        "--allow-missing-labels",
        action="store_true",
        help="explicitly run on the resolved/labeled subset and report skipped unlabeled candidate rows",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    rows = load_replay_inputs_from_jsonl(
        args.candidates,
        args.labels,
        default_annualized_vol=args.default_annualized_vol,
        allow_missing_labels=bool(args.allow_missing_labels),
    )
    source_candidate_count = _line_count(args.candidates)
    skipped_unlabeled_count = max(0, source_candidate_count - len(rows))
    denominator_scope = "resolved_labeled_subset" if args.allow_missing_labels else "all_labeled_candidates"
    config = ReplayConfig(
        min_ev_cents=args.min_ev_cents,
        min_fill_prob=args.min_fill_prob,
        no_fill_penalty_cents=args.no_fill_penalty_cents,
        counterfactual_fill_policy=args.counterfactual_fill_policy,
        counterfactual_fill_threshold=args.counterfactual_fill_threshold,
    )
    if args.online_calibrated:
        report = replace(
            evaluate_online_calibrated_replay(rows, config),
            source_candidate_count=source_candidate_count,
            skipped_unlabeled_count=skipped_unlabeled_count,
            denominator_scope=denominator_scope,
        )
        json_path, md_path = write_online_replay_report(report, args.output_dir, args.stem)
        print(f"candidate_count={report.candidate_count}")
        print(f"source_candidate_count={report.source_candidate_count}")
        print(f"skipped_unlabeled_count={report.skipped_unlabeled_count}")
        print(f"denominator_scope={report.denominator_scope}")
        print(f"selected_count={report.selected_count}")
        print(f"total_counterfactual_pnl_cents={report.total_counterfactual_pnl_cents:.4f}")
        print(f"coverage_rate={report.coverage_rate:.6f}")
        print(f"online_beats_raw_particle={report.online_beats_raw_particle}")
        print(f"online_beats_brownian={report.online_beats_brownian}")
        print(f"online_beats_market={report.online_beats_market}")
        print(f"online_beats_current_calibrated={report.online_beats_current_calibrated}")
        print(f"ev_rank_correlation_sign={report.ev_rank_correlation_sign:.6f}")
        print(f"top_ev_bucket_pnl_cents={report.top_ev_bucket_pnl_cents:.4f}")
        print(f"json_report={json_path}")
        print(f"md_report={md_path}")
        return 0
    report = replace(
        evaluate_replay(rows, config),
        source_candidate_count=source_candidate_count,
        skipped_unlabeled_count=skipped_unlabeled_count,
        denominator_scope=denominator_scope,
    )
    json_path, md_path = write_replay_report(report, args.output_dir, args.stem)
    print(f"candidate_count={report.candidate_count}")
    print(f"source_candidate_count={report.source_candidate_count}")
    print(f"skipped_unlabeled_count={report.skipped_unlabeled_count}")
    print(f"denominator_scope={report.denominator_scope}")
    print(f"selected_count={report.selected_count}")
    print(f"total_counterfactual_pnl_cents={report.total_counterfactual_pnl_cents:.4f}")
    print(f"particle_beats_brownian={report.particle_beats_brownian}")
    print(f"particle_beats_market={report.particle_beats_market}")
    print(f"particle_beats_current_calibrated={report.particle_beats_current_calibrated}")
    print(f"ev_rank_correlation_sign={report.ev_rank_correlation_sign:.6f}")
    print(f"top_ev_bucket_pnl_cents={report.top_ev_bucket_pnl_cents:.4f}")
    print(f"json_report={json_path}")
    print(f"md_report={md_path}")
    return 0


def _line_count(path: Path) -> int:
    with path.open("r", encoding="utf-8", errors="replace") as handle:
        return sum(1 for line in handle if line.strip())


if __name__ == "__main__":
    raise SystemExit(main())
