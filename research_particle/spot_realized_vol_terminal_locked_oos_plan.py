from __future__ import annotations

import argparse
import json
import uuid
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path

from .fixed_terminal_oos import FixedTerminalGateConfig
from .spot_realized_vol_terminal_oos import HypothesisId


@dataclass(frozen=True)
class SpotRealizedVolTerminalLockedOOSRunPlan:
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
    baseline_pipeline_annualized_vol: float
    gate_config: FixedTerminalGateConfig
    paired_capture_command: str
    pipeline_command: str
    market_results_command_template: str
    label_join_command: str
    static_replay_command: str
    probability_variants_command: str
    spot_realized_vol_terminal_oos_command: str
    notes: tuple[str, ...]


def build_spot_realized_vol_terminal_locked_oos_plan(
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
    baseline_pipeline_annualized_vol: float,
    gate_config: FixedTerminalGateConfig | None = None,
) -> SpotRealizedVolTerminalLockedOOSRunPlan:
    gates = gate_config or FixedTerminalGateConfig()
    checkpoint_glob = Path("research_data") / dataset / "book_checkpoints" / "**" / "*.ndjson"
    context_path = artifact_root / "passive_contexts_independent_spot.ndjson"
    candidate_path = artifact_root / "candidate_snapshots" / "candidate_snapshots.ndjson"
    spot_tick_path = artifact_root / "independent_spot_ticks.ndjson"
    market_results_path = artifact_root / "market_results_full_refresh.json"
    market_result_issues_path = artifact_root / "market_result_issues_full_refresh.json"
    label_context_path = artifact_root / "pipeline_work" / "label_contexts_full_refresh.ndjson"
    reports_dir = artifact_root / "reports"
    return SpotRealizedVolTerminalLockedOOSRunPlan(
        schema_version="spot-realized-vol-terminal-locked-oos-run-plan-v1",
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
        baseline_pipeline_annualized_vol=float(baseline_pipeline_annualized_vol),
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
            f"--annualized-vol {baseline_pipeline_annualized_vol:g} "
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
        spot_realized_vol_terminal_oos_command=(
            "python -m research_particle.spot_realized_vol_terminal_oos "
            f"--candidates \"{candidate_path}\" "
            f"--labels \"{label_context_path}\" "
            f"--spot-ticks \"{spot_tick_path}\" "
            f"--output-dir \"{reports_dir}\" "
            "--stem spot_realized_vol_terminal_oos_locked "
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
            "The local realized-vol terminal hypothesis was derived from prior diagnostics and must be tested only on a fresh locked capture.",
            "The baseline pipeline remains at annualized vol 0.65 so the local-vol OOS evaluator is compared against the existing static particle baseline.",
            "Do not edit the hypothesis, fill assumptions, gates, spot source, or evaluation scope after collection begins.",
            "Use independent spot ticks only at or before each decision timestamp; the evaluator enforces this by construction.",
            "Use all labeled candidates; unresolved-market subsets are not promotion evidence.",
            "Passing this report only makes the hypothesis eligible for the broader goal audit.",
        ),
    )


def write_spot_realized_vol_terminal_locked_oos_plan(
    plan: SpotRealizedVolTerminalLockedOOSRunPlan,
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
        description="Write a predeclared research-only locked OOS run plan for a local realized-vol terminal hypothesis."
    )
    parser.add_argument(
        "--hypothesis-id",
        choices=["rv233_blend50_fixed65_terminal_v1"],
        default="rv233_blend50_fixed65_terminal_v1",
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
    parser.add_argument("--baseline-pipeline-annualized-vol", type=float, default=0.65)
    parser.add_argument("--gate-min-candidates", type=int, default=1000)
    parser.add_argument("--gate-min-markets", type=int, default=5)
    parser.add_argument("--gate-min-selected", type=int, default=250)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    run_id = args.run_id or datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ") + "-" + uuid.uuid4().hex[:8]
    dataset = args.dataset or f"particle_spot_rv_terminal_oos_{run_id}"
    artifact_root = args.artifact_root or Path("logs") / "particle_research" / "real_shadow" / dataset
    stem = args.stem or f"{dataset}_locked_oos_plan"
    plan = build_spot_realized_vol_terminal_locked_oos_plan(
        hypothesis_id=args.hypothesis_id,
        run_id=run_id,
        dataset=dataset,
        artifact_root=artifact_root,
        run_seconds=args.run_seconds,
        checkpoint_interval_seconds=args.checkpoint_interval_seconds,
        checkpoint_depth=args.checkpoint_depth,
        independent_spot_feed=args.independent_spot_feed,
        independent_spot_max_age_ms=args.independent_spot_max_age_ms,
        baseline_pipeline_annualized_vol=args.baseline_pipeline_annualized_vol,
        gate_config=FixedTerminalGateConfig(
            min_candidate_count=args.gate_min_candidates,
            min_market_count=args.gate_min_markets,
            min_selected_count=args.gate_min_selected,
        ),
    )
    json_path, md_path = write_spot_realized_vol_terminal_locked_oos_plan(plan, args.output_dir, stem)
    print(f"hypothesis_id={plan.hypothesis_id}")
    print(f"evaluation_scope={plan.evaluation_scope}")
    print(f"dataset={plan.dataset}")
    print(f"run_id={plan.run_id}")
    print(f"run_seconds={plan.run_seconds:.0f}")
    print(f"artifact_root={plan.artifact_root}")
    print(f"json_plan={json_path}")
    print(f"md_plan={md_path}")
    return 0


def _markdown(plan: SpotRealizedVolTerminalLockedOOSRunPlan) -> str:
    lines = [
        "# Spot Realized-Vol Terminal Locked OOS Run Plan",
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
        f"- baseline_pipeline_annualized_vol: {plan.baseline_pipeline_annualized_vol:g}",
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
            plan.spot_realized_vol_terminal_oos_command,
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
