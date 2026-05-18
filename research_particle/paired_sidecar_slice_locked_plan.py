from __future__ import annotations

import argparse
import hashlib
import json
import uuid
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

from .paired_sidecar_blend_failure_analysis import DEFAULT_OUTPUT_JSON as DEFAULT_FAILURE_JSON
from .paired_sidecar_slice_oos import PairedSidecarSliceGateConfig


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT_DIR = ROOT / "logs" / "particle_research" / "locked_oos_plans"


@dataclass(frozen=True)
class PairedSidecarSliceLockedPlan:
    schema_version: str
    generated_utc: str
    hypothesis_id: str
    evaluation_scope: str
    run_id: str
    locked_after_utc: str
    model: str
    slice_type: str
    bucket: str
    fee_cents: float
    assumed_fill_probability: float
    no_fill_penalty_cents: float
    baseline_models: tuple[str, ...]
    selection_source_json: str
    selection_source_sha256: str
    gate_config: PairedSidecarSliceGateConfig
    capture_command_template: str
    refresh_command: str
    online_calibration_command: str
    failure_analysis_command: str
    slice_oos_command: str
    notes: tuple[str, ...]


def build_paired_sidecar_slice_locked_plan(
    *,
    run_id: str,
    locked_after_utc: str,
    hypothesis_id: str,
    model: str,
    slice_type: str,
    bucket: str,
    fee_cents: float,
    assumed_fill_probability: float,
    no_fill_penalty_cents: float,
    baseline_models: tuple[str, ...],
    selection_source_json: Path,
    gate_config: PairedSidecarSliceGateConfig | None = None,
) -> PairedSidecarSliceLockedPlan:
    gates = gate_config or PairedSidecarSliceGateConfig()
    source_hash = _sha256(selection_source_json)
    return PairedSidecarSliceLockedPlan(
        schema_version="paired-sidecar-slice-locked-plan-v1",
        generated_utc=datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        hypothesis_id=hypothesis_id,
        evaluation_scope="locked_forward_shadow",
        run_id=run_id,
        locked_after_utc=locked_after_utc,
        model=model,
        slice_type=slice_type,
        bucket=bucket,
        fee_cents=float(fee_cents),
        assumed_fill_probability=float(assumed_fill_probability),
        no_fill_penalty_cents=float(no_fill_penalty_cents),
        baseline_models=baseline_models,
        selection_source_json=str(selection_source_json),
        selection_source_sha256=source_hash,
        gate_config=gates,
        capture_command_template=(
            "python -m research_particle.paired_sidecar_spot_capture "
            "--collect-mode public-rest "
            "--spot-feed coinbase "
            "--spot-run-seconds 15 "
            "--spot-warmup-seconds 1 "
            "--spot-max-age-ms 2000 "
            "--timeout-seconds 10 "
            "--max-markets 80"
        ),
        refresh_command=(
            "python -m research_particle.paired_sidecar_spot_refresh "
            "--fetch-labels "
            "--write"
        ),
        online_calibration_command=(
            "python -m research_particle.paired_sidecar_online_calibration "
            "--write"
        ),
        failure_analysis_command=(
            "python -m research_particle.paired_sidecar_blend_failure_analysis "
            "--write"
        ),
        slice_oos_command=(
            "python -m research_particle.paired_sidecar_slice_oos "
            f"--plan-json \"logs/particle_research/locked_oos_plans/{run_id}_paired_sidecar_slice_locked_plan.json\" "
            "--stem paired_sidecar_slice_oos_latest "
            "--write"
        ),
        notes=(
            "This plan is research-only and starts no process by itself.",
            "The model and slice were selected from a post-hoc diagnostic; all rows at or before locked_after_utc are excluded from promotion gates.",
            "Do not edit model, slice, fee/fill assumptions, baselines, gates, or evaluation_scope after this plan is written.",
            "The evaluator recomputes fee-adjusted EV and PnL from p_yes, side, ask, and the predeclared assumptions.",
            "Fresh paired sidecar captures must remain public REST plus independent public spot; no live bot orders, thresholds, secrets, or processes are touched.",
            "Passing the slice OOS report is still research evidence only; live trading remains untouched until the broader goal audit clears.",
        ),
    )


def write_paired_sidecar_slice_locked_plan(
    plan: PairedSidecarSliceLockedPlan,
    output_dir: Path,
    stem: str,
) -> tuple[Path, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    json_path = output_dir / f"{stem}.json"
    md_path = output_dir / f"{stem}.md"
    payload = asdict(plan)
    # Keep command templates self-consistent if the caller chose a non-default stem.
    payload["slice_oos_command"] = (
        "python -m research_particle.paired_sidecar_slice_oos "
        f"--plan-json \"{json_path}\" "
        "--stem paired_sidecar_slice_oos_latest "
        "--write"
    )
    json_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    md_path.write_text(_markdown(payload), encoding="utf-8")
    return json_path, md_path


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Write a predeclared research-only paired sidecar slice shadow plan."
    )
    parser.add_argument("--run-id", default="")
    parser.add_argument("--hypothesis-id", default="blend_v28_w20_time_gt_600s_v1")
    parser.add_argument("--locked-after-utc", default="")
    parser.add_argument("--model", default="blend_v28_online_lr010_w20")
    parser.add_argument("--slice-type", default="time_to_close_band")
    parser.add_argument("--bucket", default="600s_plus")
    parser.add_argument("--fee-cents", type=float, default=1.5)
    parser.add_argument("--assumed-fill-probability", type=float, default=1.0)
    parser.add_argument("--no-fill-penalty-cents", type=float, default=0.0)
    parser.add_argument("--baseline-model", action="append", default=None)
    parser.add_argument("--selection-source-json", type=Path, default=DEFAULT_FAILURE_JSON)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--stem", default="")
    parser.add_argument("--gate-min-fresh-candidate-rows", type=int, default=200)
    parser.add_argument("--gate-min-fresh-markets", type=int, default=20)
    parser.add_argument("--gate-min-slice-rows", type=int, default=100)
    parser.add_argument("--gate-min-slice-markets", type=int, default=15)
    parser.add_argument("--gate-min-selected", type=int, default=50)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    run_id = args.run_id or "PSLICELOCK001"
    locked_after_utc = args.locked_after_utc or datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    stem = args.stem or f"{run_id}_paired_sidecar_slice_locked_plan"
    plan = build_paired_sidecar_slice_locked_plan(
        run_id=run_id,
        locked_after_utc=locked_after_utc,
        hypothesis_id=args.hypothesis_id,
        model=args.model,
        slice_type=args.slice_type,
        bucket=args.bucket,
        fee_cents=args.fee_cents,
        assumed_fill_probability=args.assumed_fill_probability,
        no_fill_penalty_cents=args.no_fill_penalty_cents,
        baseline_models=tuple(args.baseline_model) if args.baseline_model else ("v28", "market_side_ask", "candle_brownian"),
        selection_source_json=args.selection_source_json,
        gate_config=PairedSidecarSliceGateConfig(
            min_fresh_candidate_rows=args.gate_min_fresh_candidate_rows,
            min_fresh_markets=args.gate_min_fresh_markets,
            min_slice_rows=args.gate_min_slice_rows,
            min_slice_markets=args.gate_min_slice_markets,
            min_selected_count=args.gate_min_selected,
        ),
    )
    json_path, md_path = write_paired_sidecar_slice_locked_plan(plan, args.output_dir, stem)
    print(f"hypothesis_id={plan.hypothesis_id}")
    print(f"evaluation_scope={plan.evaluation_scope}")
    print(f"run_id={plan.run_id}")
    print(f"locked_after_utc={plan.locked_after_utc}")
    print(f"model={plan.model}")
    print(f"slice={plan.slice_type}={plan.bucket}")
    print(f"json_plan={json_path}")
    print(f"md_plan={md_path}")
    return 0


def _sha256(path: Path) -> str:
    if not path.exists():
        return ""
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _markdown(payload: Mapping[str, Any]) -> str:
    gates = payload.get("gate_config")
    gates = gates if isinstance(gates, Mapping) else {}
    lines = [
        "# Paired Sidecar Slice Locked Shadow Plan",
        "",
        f"- schema_version: {payload.get('schema_version')}",
        f"- generated_utc: `{payload.get('generated_utc')}`",
        f"- hypothesis_id: `{payload.get('hypothesis_id')}`",
        f"- evaluation_scope: `{payload.get('evaluation_scope')}`",
        f"- run_id: `{payload.get('run_id')}`",
        f"- locked_after_utc: `{payload.get('locked_after_utc')}`",
        f"- model: `{payload.get('model')}`",
        f"- slice: `{payload.get('slice_type')}={payload.get('bucket')}`",
        f"- fee_cents: `{payload.get('fee_cents')}`",
        f"- assumed_fill_probability: `{payload.get('assumed_fill_probability')}`",
        f"- no_fill_penalty_cents: `{payload.get('no_fill_penalty_cents')}`",
        f"- baseline_models: `{', '.join(payload.get('baseline_models') or [])}`",
        f"- selection_source_json: `{payload.get('selection_source_json')}`",
        f"- selection_source_sha256: `{payload.get('selection_source_sha256')}`",
        "",
        "## Gates",
        "",
    ]
    for key, value in gates.items():
        lines.append(f"- {key}: {value}")
    lines.extend(
        [
            "",
            "## Commands",
            "",
            "```powershell",
            str(payload.get("capture_command_template") or ""),
            str(payload.get("refresh_command") or ""),
            str(payload.get("online_calibration_command") or ""),
            str(payload.get("failure_analysis_command") or ""),
            str(payload.get("slice_oos_command") or ""),
            "```",
            "",
            "## Notes",
            "",
        ]
    )
    for note in payload.get("notes") or []:
        lines.append(f"- {note}")
    lines.append("")
    return "\n".join(lines)


if __name__ == "__main__":
    raise SystemExit(main())
