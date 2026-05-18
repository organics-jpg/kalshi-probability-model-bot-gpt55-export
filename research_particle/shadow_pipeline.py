from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Literal

from .candidate_contexts import normalize_candidate_contexts
from .market_result_labels import build_label_contexts_from_market_results
from .passive_checkpoint_source import convert_passive_checkpoints
from .read_only_candidate_source import convert_observations
from .replay_runner import (
    ReplayConfig,
    evaluate_replay,
    load_replay_inputs_from_jsonl,
    write_replay_report,
)
from .shadow_collect import record_candidates, record_labels


SourceType = Literal["raw", "top_book", "passive_checkpoint"]


@dataclass(frozen=True)
class PipelineResult:
    source_type: str
    root: str
    raw_candidate_path: str
    candidate_context_path: str
    candidate_issue_path: str
    candidate_snapshot_path: str
    label_context_path: str | None
    settlement_label_path: str | None
    replay_json_path: str | None
    replay_md_path: str | None
    manifest_path: str
    raw_written: int | None
    raw_issues: int | None
    contexts_written: int
    context_issues: int
    labels_written: int
    replay_candidate_count: int | None
    replay_selected_count: int | None
    replay_total_counterfactual_pnl_cents: float | None


def run_pipeline(args: argparse.Namespace) -> PipelineResult:
    root = Path(args.root)
    work_dir = root / "pipeline_work"
    work_dir.mkdir(parents=True, exist_ok=True)
    raw_candidate_path = work_dir / "raw_candidates.ndjson"
    candidate_context_path = work_dir / "candidate_contexts.ndjson"
    candidate_issue_path = work_dir / "candidate_context_issues.ndjson"
    source_issue_path = work_dir / "source_issues.ndjson"
    manifest_path = work_dir / "pipeline_manifest.json"

    _refuse_existing_collection(root, append_ok=bool(args.append_ok))

    raw_written: int | None = None
    raw_issues: int | None = None
    if args.source_type == "raw":
        raw_candidate_path = Path(args.input)
    elif args.source_type == "top_book":
        raw_written, raw_issues = convert_observations(
            Path(args.input),
            raw_candidate_path,
            source_issue_path,
        )
    elif args.source_type == "passive_checkpoint":
        raw_written, raw_issues = convert_passive_checkpoints(
            Path(args.checkpoints),
            Path(args.contexts),
            raw_candidate_path,
            source_issue_path,
        )
    else:
        raise ValueError(f"unknown source_type {args.source_type}")

    contexts_written, context_issues = normalize_candidate_contexts(
        raw_candidate_path,
        candidate_context_path,
        candidate_issue_path,
    )
    if contexts_written <= 0:
        raise ValueError("pipeline produced zero valid candidate contexts")

    candidate_args = argparse.Namespace(
        input=candidate_context_path,
        root=root,
        decision_shadow=args.decision_shadow,
        reason=args.reason,
        annualized_vol=args.annualized_vol,
        sample_count=args.sample_count,
        seed=args.seed,
    )
    record_candidates(candidate_args)

    candidate_snapshot_path = root / "candidate_snapshots" / "candidate_snapshots.ndjson"
    label_context_path: Path | None = None
    settlement_label_path: Path | None = None
    labels_written = 0
    replay_json_path: Path | None = None
    replay_md_path: Path | None = None
    replay_candidate_count: int | None = None
    replay_selected_count: int | None = None
    replay_total_pnl: float | None = None

    if args.label_contexts:
        label_context_path = Path(args.label_contexts)
    elif args.market_results:
        label_context_path = work_dir / "label_contexts.ndjson"
        build_label_contexts_from_market_results(
            candidate_snapshot_path,
            Path(args.market_results),
            label_context_path,
        )

    if label_context_path is not None:
        labels_written = _line_count(label_context_path)
        label_args = argparse.Namespace(input=label_context_path, root=root, source=args.label_source)
        record_labels(label_args)
        settlement_label_path = root / "settlement_labels" / "settlement_labels.ndjson"
        rows = load_replay_inputs_from_jsonl(candidate_snapshot_path, settlement_label_path)
        report = evaluate_replay(
            rows,
            ReplayConfig(
                min_ev_cents=args.min_ev_cents,
                min_fill_prob=args.min_fill_prob,
                no_fill_penalty_cents=args.no_fill_penalty_cents,
                counterfactual_fill_policy=args.counterfactual_fill_policy,
                counterfactual_fill_threshold=args.counterfactual_fill_threshold,
            ),
        )
        replay_json_path, replay_md_path = write_replay_report(report, root / "reports", args.stem)
        replay_candidate_count = report.candidate_count
        replay_selected_count = report.selected_count
        replay_total_pnl = report.total_counterfactual_pnl_cents

    result = PipelineResult(
        source_type=str(args.source_type),
        root=str(root),
        raw_candidate_path=str(raw_candidate_path),
        candidate_context_path=str(candidate_context_path),
        candidate_issue_path=str(candidate_issue_path),
        candidate_snapshot_path=str(candidate_snapshot_path),
        label_context_path=str(label_context_path) if label_context_path else None,
        settlement_label_path=str(settlement_label_path) if settlement_label_path else None,
        replay_json_path=str(replay_json_path) if replay_json_path else None,
        replay_md_path=str(replay_md_path) if replay_md_path else None,
        manifest_path=str(manifest_path),
        raw_written=raw_written,
        raw_issues=raw_issues,
        contexts_written=contexts_written,
        context_issues=context_issues,
        labels_written=labels_written,
        replay_candidate_count=replay_candidate_count,
        replay_selected_count=replay_selected_count,
        replay_total_counterfactual_pnl_cents=replay_total_pnl,
    )
    manifest_path.write_text(json.dumps(asdict(result), indent=2, sort_keys=True), encoding="utf-8")
    return result


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Research-only particle shadow pipeline: source -> contexts -> recorded candidates/labels -> replay."
    )
    parser.add_argument("--source-type", choices=["raw", "top_book", "passive_checkpoint"], required=True)
    parser.add_argument("--input", type=Path, help="raw candidate or top-book observation JSONL")
    parser.add_argument("--checkpoints", type=Path, help="passive orderbook checkpoint JSONL")
    parser.add_argument("--contexts", type=Path, help="passive checkpoint context JSON/JSONL")
    parser.add_argument("--label-contexts", type=Path, default=None)
    parser.add_argument("--market-results", type=Path, default=None)
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--stem", default="particle_shadow_pipeline_replay")
    parser.add_argument("--annualized-vol", required=True, type=float)
    parser.add_argument("--sample-count", default=2000, type=int)
    parser.add_argument("--seed", default=0, type=int)
    parser.add_argument("--decision-shadow", default="candidate")
    parser.add_argument("--reason", default="shadow_pipeline")
    parser.add_argument("--label-source", default="shadow_pipeline")
    parser.add_argument("--min-ev-cents", default=0.0, type=float)
    parser.add_argument("--min-fill-prob", default=0.0, type=float)
    parser.add_argument("--no-fill-penalty-cents", default=0.0, type=float)
    parser.add_argument(
        "--counterfactual-fill-policy",
        choices=["threshold", "always_fill", "never_fill"],
        default="threshold",
    )
    parser.add_argument("--counterfactual-fill-threshold", default=0.5, type=float)
    parser.add_argument("--append-ok", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    _validate_args(args)
    result = run_pipeline(args)
    print(f"contexts_written={result.contexts_written}")
    print(f"context_issues={result.context_issues}")
    print(f"labels_written={result.labels_written}")
    if result.replay_candidate_count is not None:
        print(f"replay_candidate_count={result.replay_candidate_count}")
        print(f"replay_selected_count={result.replay_selected_count}")
        print(f"replay_total_counterfactual_pnl_cents={result.replay_total_counterfactual_pnl_cents:.4f}")
    print(f"manifest={result.manifest_path}")
    return 0


def _validate_args(args: argparse.Namespace) -> None:
    if args.source_type in {"raw", "top_book"} and not args.input:
        raise ValueError(f"--input is required for source_type={args.source_type}")
    if args.source_type == "passive_checkpoint" and (not args.checkpoints or not args.contexts):
        raise ValueError("--checkpoints and --contexts are required for passive_checkpoint")
    if args.label_contexts and args.market_results:
        raise ValueError("use only one of --label-contexts or --market-results")


def _refuse_existing_collection(root: Path, *, append_ok: bool) -> None:
    if append_ok:
        return
    for path in (
        root / "candidate_snapshots" / "candidate_snapshots.ndjson",
        root / "settlement_labels" / "settlement_labels.ndjson",
    ):
        if path.exists():
            raise FileExistsError(f"{path} already exists; use --append-ok or a fresh --root")


def _line_count(path: Path) -> int:
    with path.open("r", encoding="utf-8", errors="replace") as handle:
        return sum(1 for line in handle if line.strip())


if __name__ == "__main__":
    raise SystemExit(main())
