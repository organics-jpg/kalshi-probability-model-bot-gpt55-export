from __future__ import annotations

import argparse
import json
import uuid
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path

from .residual_blend_oos import HypothesisId, ResidualBlendGateConfig


@dataclass(frozen=True)
class ResidualBlendLockedOOSRunPlan:
    schema_version: str
    generated_utc: str
    hypothesis_id: HypothesisId
    evaluation_scope: str
    run_id: str
    dataset: str
    artifact_root: str
    run_seconds: float
    checkpoint_interval_seconds: float
    checkpoint_depth: int
    independent_spot_feed: str
    independent_spot_max_age_ms: int
    gate_config: ResidualBlendGateConfig
    paired_capture_command: str
    pipeline_command: str
    market_results_command_template: str
    label_join_command: str
    static_replay_command: str
    probability_variants_command: str
    dynamic_diagnostic_command: str
    residual_blend_oos_command: str
    notes: tuple[str, ...]


def build_residual_blend_locked_oos_plan(
    *,
    hypothesis_id: HypothesisId,
    run_id: str,
    dataset: str,
    artifact_root: Path,
    run_seconds: float,
    checkpoint_interval_seconds: float,
    checkpoint_depth: int,
    independent_spot_feed: str,
    independent_spot_max_age_ms: int,
    gate_config: ResidualBlendGateConfig | None = None,
) -> ResidualBlendLockedOOSRunPlan:
    gates = gate_config or ResidualBlendGateConfig()
    checkpoint_glob = Path("research_data") / dataset / "book_checkpoints" / "**" / "*.ndjson"
    context_path = artifact_root / "passive_contexts_independent_spot.ndjson"
    candidate_path = artifact_root / "candidate_snapshots" / "candidate_snapshots.ndjson"
    market_results_path = artifact_root / "market_results_full_refresh.json"
    market_result_issues_path = artifact_root / "market_result_issues_full_refresh.json"
    label_context_path = artifact_root / "pipeline_work" / "label_contexts_full_refresh.ndjson"
    reports_dir = artifact_root / "reports"
    return ResidualBlendLockedOOSRunPlan(
        schema_version="residual-blend-locked-oos-run-plan-v1",
        generated_utc=datetime.now(timezone.utc).isoformat(),
        hypothesis_id=hypothesis_id,
        evaluation_scope="locked_oos_shadow",
        run_id=run_id,
        dataset=dataset,
        artifact_root=str(artifact_root),
        run_seconds=float(run_seconds),
        checkpoint_interval_seconds=float(checkpoint_interval_seconds),
        checkpoint_depth=int(checkpoint_depth),
        independent_spot_feed=independent_spot_feed,
        independent_spot_max_age_ms=int(independent_spot_max_age_ms),
        gate_config=gates,
        paired_capture_command=(
            "python -m research_particle.paired_passive_shadow_run "
            f"--dataset {dataset} "
            f"--run-id {run_id} "
            f"--run-seconds {run_seconds:.0f} "
            f"--checkpoint-interval-seconds {checkpoint_interval_seconds:g} "
            f"--checkpoint-depth {checkpoint_depth} "
            "--status-interval-seconds 10 "
            "--record-independent-spot "
            f"--independent-spot-feed {independent_spot_feed} "
            f"--independent-spot-max-age-ms {independent_spot_max_age_ms} "
            "--require-independent-spot"
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
            "--ticker <TICKER_1> --ticker <TICKER_2> --ticker <TICKER_3> --ticker <TICKER_4> --ticker <TICKER_5> "
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
            f"--labels \"{label_context_path}\" "
            f"--output-dir \"{reports_dir}\" "
            "--stem passive_particle_replay_locked_oos "
            "--min-fill-prob 0.5 "
            "--counterfactual-fill-threshold 0.5"
        ),
        probability_variants_command=(
            "python -m research_particle.probability_variants "
            f"--candidates \"{candidate_path}\" "
            f"--labels \"{label_context_path}\" "
            f"--output-dir \"{reports_dir}\" "
            "--stem probability_variants_locked_oos "
            "--min-fill-prob 0.5 "
            "--counterfactual-fill-threshold 0.5"
        ),
        dynamic_diagnostic_command=(
            "python -m research_particle.dynamic_particle_replay "
            f"--candidates \"{candidate_path}\" "
            f"--labels \"{label_context_path}\" "
            f"--output-dir \"{reports_dir}\" "
            "--stem dynamic_particle_locked_oos_diagnostic "
            "--min-fill-prob 0.5 "
            "--counterfactual-fill-threshold 0.5"
        ),
        residual_blend_oos_command=(
            "python -m research_particle.residual_blend_oos "
            f"--candidates \"{candidate_path}\" "
            f"--labels \"{label_context_path}\" "
            f"--output-dir \"{reports_dir}\" "
            "--stem residual_blend_oos_locked "
            f"--hypothesis-id {hypothesis_id} "
            "--evaluation-scope locked_oos_shadow "
            "--min-fill-prob 0.5 "
            "--counterfactual-fill-threshold 0.5 "
            f"--gate-min-candidates {gates.min_candidate_count} "
            f"--gate-min-markets {gates.min_market_count} "
            f"--gate-min-selected {gates.min_selected_count}"
        ),
        notes=(
            "This plan is research-only and starts no process by itself.",
            "The residual coefficient was selected from previous locked diagnostics and must be treated as a new hypothesis.",
            "Do not edit the coefficient, fill assumptions, gates, or evaluation scope after collection begins.",
            "Use the independent spot merged context; contexts without timestamp-available spot are excluded.",
            "Use all labeled candidates; unresolved-market subsets are not promotion evidence.",
            "Passing this report only makes the residual blend hypothesis eligible for the broader goal audit.",
        ),
    )


def write_residual_blend_locked_oos_plan(
    plan: ResidualBlendLockedOOSRunPlan,
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
        description="Write a predeclared research-only locked OOS run plan for a residual blend hypothesis."
    )
    parser.add_argument(
        "--hypothesis-id",
        choices=["resid_current_rv300n20_rv600p20_particle_n10_v1"],
        default="resid_current_rv300n20_rv600p20_particle_n10_v1",
    )
    parser.add_argument("--run-id", default="")
    parser.add_argument("--dataset", default="")
    parser.add_argument("--artifact-root", type=Path, default=None)
    parser.add_argument("--output-dir", type=Path, default=Path("logs") / "particle_research" / "locked_oos_plans")
    parser.add_argument("--stem", default="")
    parser.add_argument("--run-seconds", type=float, default=3900.0)
    parser.add_argument("--checkpoint-interval-seconds", type=float, default=1.0)
    parser.add_argument("--checkpoint-depth", type=int, default=5)
    parser.add_argument("--independent-spot-feed", choices=["coinbase", "binance"], default="coinbase")
    parser.add_argument("--independent-spot-max-age-ms", type=int, default=5000)
    parser.add_argument("--gate-min-candidates", type=int, default=1000)
    parser.add_argument("--gate-min-markets", type=int, default=5)
    parser.add_argument("--gate-min-selected", type=int, default=250)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    run_id = args.run_id or datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ") + "-" + uuid.uuid4().hex[:8]
    dataset = args.dataset or f"particle_residual_blend_oos_{run_id}"
    artifact_root = args.artifact_root or Path("logs") / "particle_research" / "real_shadow" / dataset
    stem = args.stem or f"{dataset}_locked_oos_plan"
    plan = build_residual_blend_locked_oos_plan(
        hypothesis_id=args.hypothesis_id,
        run_id=run_id,
        dataset=dataset,
        artifact_root=artifact_root,
        run_seconds=args.run_seconds,
        checkpoint_interval_seconds=args.checkpoint_interval_seconds,
        checkpoint_depth=args.checkpoint_depth,
        independent_spot_feed=args.independent_spot_feed,
        independent_spot_max_age_ms=args.independent_spot_max_age_ms,
        gate_config=ResidualBlendGateConfig(
            min_candidate_count=args.gate_min_candidates,
            min_market_count=args.gate_min_markets,
            min_selected_count=args.gate_min_selected,
        ),
    )
    json_path, md_path = write_residual_blend_locked_oos_plan(plan, args.output_dir, stem)
    print(f"hypothesis_id={plan.hypothesis_id}")
    print(f"evaluation_scope={plan.evaluation_scope}")
    print(f"dataset={plan.dataset}")
    print(f"run_id={plan.run_id}")
    print(f"run_seconds={plan.run_seconds:.0f}")
    print(f"artifact_root={plan.artifact_root}")
    print(f"json_plan={json_path}")
    print(f"md_plan={md_path}")
    return 0


def _markdown(plan: ResidualBlendLockedOOSRunPlan) -> str:
    lines = [
        "# Residual Blend Locked OOS Run Plan",
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
        f"- independent_spot_feed: {plan.independent_spot_feed}",
        f"- independent_spot_max_age_ms: {plan.independent_spot_max_age_ms}",
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
            plan.probability_variants_command,
            "",
            plan.dynamic_diagnostic_command,
            "",
            plan.residual_blend_oos_command,
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
