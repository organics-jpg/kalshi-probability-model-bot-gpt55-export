from __future__ import annotations

import argparse
import json
import uuid
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path

from .side_safety_oos import PredeclaredGateConfig


@dataclass(frozen=True)
class LockedOOSRunPlan:
    schema_version: str
    generated_utc: str
    hypothesis_id: str
    evaluation_scope: str
    run_id: str
    dataset: str
    artifact_root: str
    run_seconds: float
    checkpoint_interval_seconds: float
    checkpoint_depth: int
    gate_config: PredeclaredGateConfig
    paired_capture_command: str
    pipeline_command: str
    market_results_command_template: str
    label_join_command: str
    static_replay_command: str
    online_replay_command: str
    selection_sweep_command: str
    side_failure_command: str
    side_safety_oos_command: str
    notes: tuple[str, ...]


def build_locked_oos_plan(
    *,
    run_id: str,
    dataset: str,
    artifact_root: Path,
    run_seconds: float,
    checkpoint_interval_seconds: float,
    checkpoint_depth: int,
    gate_config: PredeclaredGateConfig | None = None,
) -> LockedOOSRunPlan:
    gates = gate_config or PredeclaredGateConfig()
    checkpoint_glob = Path("research_data") / dataset / "book_checkpoints" / "**" / "*.ndjson"
    context_path = artifact_root / "passive_contexts.ndjson"
    candidate_path = artifact_root / "candidate_snapshots" / "candidate_snapshots.ndjson"
    market_results_path = artifact_root / "market_results_full_refresh.json"
    market_result_issues_path = artifact_root / "market_result_issues_full_refresh.json"
    label_context_path = artifact_root / "pipeline_work" / "label_contexts_full_refresh.ndjson"
    reports_dir = artifact_root / "reports"
    labels_path = label_context_path
    return LockedOOSRunPlan(
        schema_version="locked-oos-run-plan-v1",
        generated_utc=datetime.now(timezone.utc).isoformat(),
        hypothesis_id="side_safe_yes_only_v1",
        evaluation_scope="locked_oos_shadow",
        run_id=run_id,
        dataset=dataset,
        artifact_root=str(artifact_root),
        run_seconds=float(run_seconds),
        checkpoint_interval_seconds=float(checkpoint_interval_seconds),
        checkpoint_depth=int(checkpoint_depth),
        gate_config=gates,
        paired_capture_command=(
            "python -m research_particle.paired_passive_shadow_run "
            f"--dataset {dataset} "
            f"--run-id {run_id} "
            f"--run-seconds {run_seconds:.0f} "
            f"--checkpoint-interval-seconds {checkpoint_interval_seconds:g} "
            f"--checkpoint-depth {checkpoint_depth} "
            "--status-interval-seconds 10"
        ),
        pipeline_command=(
            "python -m research_particle.shadow_pipeline "
            "--source-type passive_checkpoint "
            f"--checkpoints \"{checkpoint_glob}\" "
            f"--contexts \"{context_path}\" "
            f"--root \"{artifact_root}\" "
            "--annualized-vol 0.65 "
            "--sample-count 2000 "
            "--seed 1 "
            "--min-fill-prob 0.5 "
            "--counterfactual-fill-threshold 0.5"
        ),
        market_results_command_template=(
            "python -m research_particle.kalshi_market_results "
            "--ticker <TICKER_1> --ticker <TICKER_2> --ticker <TICKER_3> --ticker <TICKER_4> "
            f"--output \"{market_results_path}\" "
            f"--issues \"{market_result_issues_path}\""
        ),
        label_join_command=(
            "python -m research_particle.market_result_labels "
            f"--candidates \"{candidate_path}\" "
            f"--market-results \"{market_results_path}\" "
            f"--output \"{label_context_path}\""
        ),
        static_replay_command=(
            "python -m research_particle.reports "
            f"--candidates \"{candidate_path}\" "
            f"--labels \"{labels_path}\" "
            f"--output-dir \"{reports_dir}\" "
            "--stem passive_particle_replay_locked_oos "
            "--min-fill-prob 0.5 "
            "--counterfactual-fill-threshold 0.5"
        ),
        online_replay_command=(
            "python -m research_particle.reports "
            f"--candidates \"{candidate_path}\" "
            f"--labels \"{labels_path}\" "
            f"--output-dir \"{reports_dir}\" "
            "--stem online_calibrated_particle_replay_locked_oos "
            "--online-calibrated "
            "--min-fill-prob 0.5 "
            "--counterfactual-fill-threshold 0.5"
        ),
        selection_sweep_command=(
            "python -m research_particle.selection_sweep "
            f"--candidates \"{candidate_path}\" "
            f"--labels \"{labels_path}\" "
            f"--output-dir \"{reports_dir}\" "
            "--stem passive_particle_selection_sweep_locked_oos "
            "--min-ev-grid 0,1,2,3,5,8,10,12,15,20 "
            "--min-fill-grid 0,0.25,0.5,0.75,1.0 "
            "--counterfactual-fill-threshold 0.5"
        ),
        side_failure_command=(
            "python -m research_particle.side_failure_analysis "
            f"--candidates \"{candidate_path}\" "
            f"--labels \"{labels_path}\" "
            f"--output-dir \"{reports_dir}\" "
            "--stem side_failure_locked_oos "
            "--min-fill-prob 0.5 "
            "--counterfactual-fill-threshold 0.5"
        ),
        side_safety_oos_command=(
            "python -m research_particle.side_safety_oos "
            f"--candidates \"{candidate_path}\" "
            f"--labels \"{labels_path}\" "
            f"--output-dir \"{reports_dir}\" "
            "--stem side_safety_oos_locked "
            "--evaluation-scope locked_oos_shadow "
            "--min-fill-prob 0.5 "
            "--counterfactual-fill-threshold 0.5 "
            f"--gate-min-candidates {gates.min_candidate_count} "
            f"--gate-min-markets {gates.min_market_count} "
            f"--gate-min-selected {gates.min_selected_count}"
        ),
        notes=(
            "This plan is research-only and starts no process by itself.",
            "Do not edit thresholds or gates after collection begins; create a new plan instead.",
            "Use all labeled candidates; unresolved-market subsets are not promotion evidence.",
            "Passing side_safety_oos_locked only makes the side-safety hypothesis eligible for the broader goal audit.",
        ),
    )


def write_locked_oos_plan(
    plan: LockedOOSRunPlan,
    output_dir: Path,
    stem: str,
) -> tuple[Path, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    json_path = output_dir / f"{stem}.json"
    md_path = output_dir / f"{stem}.md"
    json_path.write_text(json.dumps(asdict(plan), indent=2, sort_keys=True), encoding="utf-8")
    md_path.write_text(_markdown(plan), encoding="utf-8")
    return json_path, md_path


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Write a predeclared research-only locked OOS run plan for side_safe_yes_only_v1."
    )
    parser.add_argument("--run-id", default="")
    parser.add_argument("--dataset", default="")
    parser.add_argument("--artifact-root", type=Path, default=None)
    parser.add_argument("--output-dir", type=Path, default=Path("logs") / "particle_research" / "locked_oos_plans")
    parser.add_argument("--stem", default="")
    parser.add_argument("--run-seconds", type=float, default=3900.0)
    parser.add_argument("--checkpoint-interval-seconds", type=float, default=1.0)
    parser.add_argument("--checkpoint-depth", type=int, default=5)
    parser.add_argument("--gate-min-candidates", type=int, default=500)
    parser.add_argument("--gate-min-markets", type=int, default=4)
    parser.add_argument("--gate-min-selected", type=int, default=100)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    run_id = args.run_id or datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ") + "-" + uuid.uuid4().hex[:8]
    dataset = args.dataset or f"particle_side_safety_oos_{run_id}"
    artifact_root = args.artifact_root or Path("logs") / "particle_research" / "real_shadow" / dataset
    stem = args.stem or f"{dataset}_locked_oos_plan"
    plan = build_locked_oos_plan(
        run_id=run_id,
        dataset=dataset,
        artifact_root=artifact_root,
        run_seconds=args.run_seconds,
        checkpoint_interval_seconds=args.checkpoint_interval_seconds,
        checkpoint_depth=args.checkpoint_depth,
        gate_config=PredeclaredGateConfig(
            min_candidate_count=args.gate_min_candidates,
            min_market_count=args.gate_min_markets,
            min_selected_count=args.gate_min_selected,
        ),
    )
    json_path, md_path = write_locked_oos_plan(plan, args.output_dir, stem)
    print(f"hypothesis_id={plan.hypothesis_id}")
    print(f"evaluation_scope={plan.evaluation_scope}")
    print(f"dataset={plan.dataset}")
    print(f"run_id={plan.run_id}")
    print(f"run_seconds={plan.run_seconds:.0f}")
    print(f"artifact_root={plan.artifact_root}")
    print(f"json_plan={json_path}")
    print(f"md_plan={md_path}")
    return 0


def _markdown(plan: LockedOOSRunPlan) -> str:
    lines = [
        "# Locked OOS Run Plan",
        "",
        f"- schema_version: {plan.schema_version}",
        f"- generated_utc: {plan.generated_utc}",
        f"- hypothesis_id: {plan.hypothesis_id}",
        f"- evaluation_scope: {plan.evaluation_scope}",
        f"- dataset: {plan.dataset}",
        f"- run_id: {plan.run_id}",
        f"- artifact_root: `{plan.artifact_root}`",
        f"- run_seconds: {plan.run_seconds:.0f}",
        f"- checkpoint_interval_seconds: {plan.checkpoint_interval_seconds:g}",
        f"- checkpoint_depth: {plan.checkpoint_depth}",
        "",
        "## Gates",
        "",
    ]
    for name, value in asdict(plan.gate_config).items():
        lines.append(f"- {name}: {value}")
    lines.extend(
        [
            "",
            "## Commands",
            "",
            "```powershell",
            plan.paired_capture_command,
            "",
            plan.pipeline_command,
            "",
            plan.market_results_command_template,
            "",
            plan.label_join_command,
            "",
            plan.static_replay_command,
            "",
            plan.online_replay_command,
            "",
            plan.selection_sweep_command,
            "",
            plan.side_failure_command,
            "",
            plan.side_safety_oos_command,
            "```",
            "",
            "## Notes",
            "",
        ]
    )
    lines.extend(f"- {note}" for note in plan.notes)
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    raise SystemExit(main())
