from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
import uuid
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

from .spot_context_merge import merge_contexts_with_spot
from .v28_event_sources import latest_execution_events_path


@dataclass(frozen=True)
class PairedPassiveRunResult:
    schema_version: str
    generated_utc: str
    dataset: str
    run_id: str
    artifact_root: str
    matched_control_mode: str
    v28_events_input: str
    context_path: str
    context_issue_path: str
    context_status_path: str
    offline_v28_context_path: str
    offline_v28_context_issue_path: str
    offline_v28_context_summary_json: str
    offline_v28_context_summary_md: str
    offline_v28_returncode: int | None
    offline_v28_context_row_count: int
    offline_v28_context_issue_count: int
    offline_v28_stdout: str
    offline_v28_stderr: str
    independent_spot_path: str
    independent_spot_issue_path: str
    independent_spot_status_path: str
    independent_spot_returncode: int | None
    independent_spot_row_count: int
    independent_spot_issue_count: int
    independent_spot_feed: str
    independent_spot_max_age_ms: float
    merged_context_path: str
    merged_context_issue_path: str
    merged_context_row_count: int
    merged_context_issue_count: int
    context_path_for_pipeline: str
    checkpoint_glob: str
    run_seconds: float
    recorder_returncode: int | None
    tailer_returncode: int | None
    checkpoint_file_count: int
    checkpoint_row_count: int
    context_row_count: int
    context_issue_count: int
    recorder_stdout: str
    recorder_stderr: str
    tailer_stdout: str
    tailer_stderr: str
    independent_spot_stdout: str
    independent_spot_stderr: str
    pipeline_command: str


def run_paired_passive_collection(
    *,
    workspace: Path,
    dataset: str,
    artifact_root: Path,
    v28_events_input: Path | None,
    run_seconds: float,
    run_id: str,
    checkpoint_interval_seconds: float = 1.0,
    checkpoint_depth: int = 5,
    market_refresh_seconds: float = 10.0,
    status_interval_seconds: float = 5.0,
    strategy_tag: str = "particle_shadow_readonly",
    bot_tag: str = "particle_shadow_readonly",
    start_context_at_end: bool = True,
    record_independent_spot: bool = False,
    independent_spot_feed: str = "coinbase",
    independent_spot_max_age_ms: float = 5_000.0,
    require_independent_spot: bool = False,
    offline_v28_control: bool = False,
) -> PairedPassiveRunResult:
    workspace = workspace.resolve()
    if offline_v28_control and not record_independent_spot:
        raise ValueError("--offline-v28-control requires --record-independent-spot")
    if not offline_v28_control and v28_events_input is None:
        raise FileNotFoundError("No v28 execution_events.ndjson found; pass --v28-events")
    artifact_root.mkdir(parents=True, exist_ok=True)
    context_path = artifact_root / "passive_contexts.ndjson"
    context_issue_path = artifact_root / "passive_context_issues.ndjson"
    context_status_path = artifact_root / "passive_context_tailer_status.json"
    offline_context_path = artifact_root / "offline_v28_contexts.ndjson"
    offline_issue_path = artifact_root / "offline_v28_context_issues.ndjson"
    offline_summary_json = artifact_root / "offline_v28_context_summary.json"
    offline_summary_md = artifact_root / "offline_v28_context_summary.md"
    spot_path = artifact_root / "independent_spot_ticks.ndjson"
    spot_issue_path = artifact_root / "independent_spot_issues.ndjson"
    spot_status_path = artifact_root / "independent_spot_status.json"
    merged_context_path = artifact_root / "passive_contexts_independent_spot.ndjson"
    merged_context_issue_path = artifact_root / "passive_contexts_independent_spot_issues.ndjson"
    recorder_stdout = artifact_root / "passive_recorder_stdout.log"
    recorder_stderr = artifact_root / "passive_recorder_stderr.log"
    tailer_stdout = artifact_root / "context_tailer_stdout.log"
    tailer_stderr = artifact_root / "context_tailer_stderr.log"
    spot_stdout = artifact_root / "independent_spot_stdout.log"
    spot_stderr = artifact_root / "independent_spot_stderr.log"
    offline_stdout = artifact_root / "offline_v28_stdout.log"
    offline_stderr = artifact_root / "offline_v28_stderr.log"
    env = _subprocess_env(workspace)
    tailer_cmd: list[str] = []
    if not offline_v28_control:
        tailer_cmd = [
            sys.executable,
            "-m",
            "research_particle.v28_context_tailer",
            "--input",
            str(v28_events_input),
            "--output",
            str(context_path),
            "--issues",
            str(context_issue_path),
            "--status",
            str(context_status_path),
            "--follow",
            "--run-seconds",
            f"{max(0.1, run_seconds + 5.0):.3f}",
            "--append-ok",
            "--enrich-missing-market-metadata",
        ]
        if start_context_at_end:
            tailer_cmd.append("--start-at-end")
            if not (record_independent_spot and require_independent_spot):
                tailer_cmd.append("--seed-last-contexts")
    recorder_cmd = [
        sys.executable,
        "research_native_passive_ws_recorder.py",
        "--dataset",
        dataset,
        "--strategy-tag",
        strategy_tag,
        "--bot-tag",
        bot_tag,
        "--checkpoint-interval-seconds",
        str(checkpoint_interval_seconds),
        "--market-refresh-seconds",
        str(market_refresh_seconds),
        "--checkpoint-depth",
        str(checkpoint_depth),
        "--status-interval-seconds",
        str(status_interval_seconds),
        "--run-id",
        run_id,
        "--run-seconds",
        str(run_seconds),
    ]
    spot_cmd = [
        sys.executable,
        "-m",
        "research_particle.spot_ticker_recorder",
        "--feed",
        independent_spot_feed,
        "--output",
        str(spot_path),
        "--issues",
        str(spot_issue_path),
        "--status",
        str(spot_status_path),
        "--run-seconds",
        f"{max(0.1, run_seconds + 5.0):.3f}",
    ]

    with tailer_stdout.open("w", encoding="utf-8") as tailer_out, tailer_stderr.open(
        "w", encoding="utf-8"
    ) as tailer_err, recorder_stdout.open("w", encoding="utf-8") as recorder_out, recorder_stderr.open(
        "w", encoding="utf-8"
    ) as recorder_err, spot_stdout.open("w", encoding="utf-8") as spot_out, spot_stderr.open(
        "w", encoding="utf-8"
    ) as spot_err:
        tailer = None
        if tailer_cmd:
            tailer = subprocess.Popen(
                tailer_cmd,
                cwd=workspace,
                env=env,
                stdout=tailer_out,
                stderr=tailer_err,
                text=True,
            )
        spot = None
        if record_independent_spot:
            spot = subprocess.Popen(
                spot_cmd,
                cwd=workspace,
                env=env,
                stdout=spot_out,
                stderr=spot_err,
                text=True,
            )
        # Let the context tailer attach before the websocket recorder begins writing checkpoints.
        if tailer is not None:
            time.sleep(0.5)
        recorder = subprocess.Popen(
            recorder_cmd,
            cwd=workspace,
            env=env,
            stdout=recorder_out,
            stderr=recorder_err,
            text=True,
        )
        recorder_returncode = _wait_or_terminate(recorder, timeout=max(10.0, run_seconds + 30.0))
        spot_returncode = (
            _wait_or_terminate(spot, timeout=max(10.0, run_seconds + 30.0))
            if spot is not None
            else None
        )
        tailer_returncode = (
            _wait_or_terminate(tailer, timeout=15.0) if tailer is not None else None
        )

    checkpoint_glob = workspace / "research_data" / dataset / "book_checkpoints" / "**" / "*.ndjson"
    context_for_pipeline = context_path
    merged_result = None
    if record_independent_spot and not offline_v28_control:
        merged_result = merge_contexts_with_spot(
            context_path=context_path,
            spot_path=spot_path,
            output_path=merged_context_path,
            issue_path=merged_context_issue_path,
            max_age_ms=independent_spot_max_age_ms,
            require_spot=require_independent_spot,
        )
        context_for_pipeline = merged_context_path
    offline_returncode = None
    if offline_v28_control:
        offline_cmd = [
            sys.executable,
            "probe_rv600_native_offline_v28_contexts.py",
            "--checkpoints",
            str(checkpoint_glob),
            "--spot-ticks",
            str(spot_path),
            "--output",
            str(offline_context_path),
            "--issues",
            str(offline_issue_path),
            "--summary-json",
            str(offline_summary_json),
            "--summary-md",
            str(offline_summary_md),
            "--max-spot-age-ms",
            str(independent_spot_max_age_ms),
        ]
        with offline_stdout.open("w", encoding="utf-8") as stdout, offline_stderr.open(
            "w", encoding="utf-8"
        ) as stderr:
            completed = subprocess.run(
                offline_cmd,
                cwd=workspace,
                env=env,
                stdout=stdout,
                stderr=stderr,
                text=True,
                check=False,
            )
        offline_returncode = completed.returncode
        context_for_pipeline = offline_context_path
    result = PairedPassiveRunResult(
        schema_version="paired-passive-shadow-run-v1",
        generated_utc=datetime.now(timezone.utc).isoformat(),
        dataset=dataset,
        run_id=run_id,
        artifact_root=str(artifact_root),
        matched_control_mode="offline_v28_public_btc_replay" if offline_v28_control else "live_v28_event_tailer",
        v28_events_input=str(v28_events_input) if v28_events_input is not None else "",
        context_path=str(context_path),
        context_issue_path=str(context_issue_path),
        context_status_path=str(context_status_path),
        offline_v28_context_path=str(offline_context_path) if offline_v28_control else "",
        offline_v28_context_issue_path=str(offline_issue_path) if offline_v28_control else "",
        offline_v28_context_summary_json=str(offline_summary_json) if offline_v28_control else "",
        offline_v28_context_summary_md=str(offline_summary_md) if offline_v28_control else "",
        offline_v28_returncode=offline_returncode,
        offline_v28_context_row_count=_line_count([offline_context_path]) if offline_v28_control else 0,
        offline_v28_context_issue_count=_line_count([offline_issue_path]) if offline_v28_control else 0,
        offline_v28_stdout=str(offline_stdout) if offline_v28_control else "",
        offline_v28_stderr=str(offline_stderr) if offline_v28_control else "",
        independent_spot_path=str(spot_path) if record_independent_spot else "",
        independent_spot_issue_path=str(spot_issue_path) if record_independent_spot else "",
        independent_spot_status_path=str(spot_status_path) if record_independent_spot else "",
        independent_spot_returncode=spot_returncode,
        independent_spot_row_count=_line_count([spot_path]) if record_independent_spot else 0,
        independent_spot_issue_count=_line_count([spot_issue_path]) if record_independent_spot else 0,
        independent_spot_feed=independent_spot_feed if record_independent_spot else "",
        independent_spot_max_age_ms=float(independent_spot_max_age_ms),
        merged_context_path=str(merged_context_path) if merged_result is not None else "",
        merged_context_issue_path=str(merged_context_issue_path) if merged_result is not None else "",
        merged_context_row_count=merged_result.contexts_written if merged_result is not None else 0,
        merged_context_issue_count=merged_result.issue_count if merged_result is not None else 0,
        context_path_for_pipeline=str(context_for_pipeline),
        checkpoint_glob=str(checkpoint_glob),
        run_seconds=float(run_seconds),
        recorder_returncode=recorder_returncode,
        tailer_returncode=tailer_returncode,
        checkpoint_file_count=len(_checkpoint_files(workspace, dataset)),
        checkpoint_row_count=_line_count(_checkpoint_files(workspace, dataset)),
        context_row_count=_line_count([context_path]),
        context_issue_count=_line_count([context_issue_path]),
        recorder_stdout=str(recorder_stdout),
        recorder_stderr=str(recorder_stderr),
        tailer_stdout=str(tailer_stdout),
        tailer_stderr=str(tailer_stderr),
        independent_spot_stdout=str(spot_stdout) if record_independent_spot else "",
        independent_spot_stderr=str(spot_stderr) if record_independent_spot else "",
        pipeline_command=_pipeline_command(checkpoint_glob, context_for_pipeline, artifact_root),
    )
    manifest_path = artifact_root / "paired_passive_run_manifest.json"
    manifest_path.write_text(json.dumps(asdict(result), indent=2, sort_keys=True), encoding="utf-8")
    return result


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Research-only bounded paired collector: passive Kalshi book checkpoints plus v28 context tailer."
    )
    parser.add_argument("--dataset", default="")
    parser.add_argument("--artifact-root", type=Path, default=None)
    parser.add_argument("--v28-events", type=Path, default=None)
    parser.add_argument("--run-seconds", type=float, default=60.0)
    parser.add_argument("--run-id", default="")
    parser.add_argument("--checkpoint-interval-seconds", type=float, default=1.0)
    parser.add_argument("--checkpoint-depth", type=int, default=5)
    parser.add_argument("--market-refresh-seconds", type=float, default=10.0)
    parser.add_argument("--status-interval-seconds", type=float, default=5.0)
    parser.add_argument("--strategy-tag", default="particle_shadow_readonly")
    parser.add_argument("--bot-tag", default="particle_shadow_readonly")
    parser.add_argument("--include-existing-context", action="store_true")
    parser.add_argument("--record-independent-spot", action="store_true")
    parser.add_argument("--independent-spot-feed", default="coinbase", choices=("coinbase", "binance"))
    parser.add_argument("--independent-spot-max-age-ms", default=5000.0, type=float)
    parser.add_argument("--require-independent-spot", action="store_true")
    parser.add_argument(
        "--offline-v28-control",
        action="store_true",
        help=(
            "Build matched v28 contexts after collection by causally replaying the v28 engine "
            "from public BTC candles and independent spot ticks, without using live bot telemetry."
        ),
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    workspace = Path(".").resolve()
    run_id = args.run_id or datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ") + "-" + uuid.uuid4().hex[:8]
    dataset = args.dataset or f"particle_shadow_forward_{run_id}"
    artifact_root = args.artifact_root or Path("logs") / "particle_research" / "real_shadow" / dataset
    v28_events = args.v28_events or (
        None if args.offline_v28_control else _latest_execution_events_path(workspace)
    )
    if v28_events is None and not args.offline_v28_control:
        raise FileNotFoundError("No v28 execution_events.ndjson found; pass --v28-events")
    result = run_paired_passive_collection(
        workspace=workspace,
        dataset=dataset,
        artifact_root=artifact_root,
        v28_events_input=v28_events,
        run_seconds=args.run_seconds,
        run_id=run_id,
        checkpoint_interval_seconds=args.checkpoint_interval_seconds,
        checkpoint_depth=args.checkpoint_depth,
        market_refresh_seconds=args.market_refresh_seconds,
        status_interval_seconds=args.status_interval_seconds,
        strategy_tag=args.strategy_tag,
        bot_tag=args.bot_tag,
        start_context_at_end=not bool(args.include_existing_context),
        record_independent_spot=bool(args.record_independent_spot),
        independent_spot_feed=args.independent_spot_feed,
        independent_spot_max_age_ms=args.independent_spot_max_age_ms,
        require_independent_spot=bool(args.require_independent_spot),
        offline_v28_control=bool(args.offline_v28_control),
    )
    print(f"dataset={result.dataset}")
    print(f"run_id={result.run_id}")
    print(f"recorder_returncode={result.recorder_returncode}")
    print(f"tailer_returncode={result.tailer_returncode}")
    print(f"checkpoint_file_count={result.checkpoint_file_count}")
    print(f"checkpoint_row_count={result.checkpoint_row_count}")
    print(f"context_row_count={result.context_row_count}")
    print(f"context_issue_count={result.context_issue_count}")
    print(f"matched_control_mode={result.matched_control_mode}")
    if result.offline_v28_context_path:
        print(f"offline_v28_returncode={result.offline_v28_returncode}")
        print(f"offline_v28_context_row_count={result.offline_v28_context_row_count}")
        print(f"offline_v28_context_issue_count={result.offline_v28_context_issue_count}")
        print(f"offline_v28_context_path={result.offline_v28_context_path}")
    if result.independent_spot_path:
        print(f"independent_spot_returncode={result.independent_spot_returncode}")
        print(f"independent_spot_row_count={result.independent_spot_row_count}")
        print(f"independent_spot_issue_count={result.independent_spot_issue_count}")
        print(f"merged_context_row_count={result.merged_context_row_count}")
        print(f"merged_context_issue_count={result.merged_context_issue_count}")
        print(f"context_path_for_pipeline={result.context_path_for_pipeline}")
    print(f"manifest={Path(result.artifact_root) / 'paired_passive_run_manifest.json'}")
    print(f"pipeline_command={result.pipeline_command}")
    return 0


def _subprocess_env(workspace: Path) -> dict[str, str]:
    env = dict(os.environ)
    env.update(_read_env_file(workspace / ".env"))
    python_path = str(workspace)
    if env.get("PYTHONPATH"):
        python_path = python_path + os.pathsep + env["PYTHONPATH"]
    env["PYTHONPATH"] = python_path
    return env


def _read_env_file(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    if not path.exists():
        return values
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "=" not in stripped:
            continue
        key, value = stripped.split("=", 1)
        values[key.strip()] = value.strip().strip('"').strip("'")
    return values


def _latest_execution_events_path(workspace: Path) -> Path | None:
    return latest_execution_events_path(workspace)


def _checkpoint_files(workspace: Path, dataset: str) -> list[Path]:
    root = workspace / "research_data" / dataset / "book_checkpoints"
    return sorted(root.rglob("*.ndjson")) if root.exists() else []


def _line_count(paths: Iterable[Path]) -> int:
    total = 0
    for path in paths:
        if not path.exists():
            continue
        with path.open("r", encoding="utf-8", errors="replace") as handle:
            total += sum(1 for line in handle if line.strip())
    return total


def _wait_or_terminate(process: subprocess.Popen[str], *, timeout: float) -> int | None:
    try:
        return process.wait(timeout=timeout)
    except subprocess.TimeoutExpired:
        process.terminate()
        try:
            return process.wait(timeout=5.0)
        except subprocess.TimeoutExpired:
            process.kill()
            return process.wait(timeout=5.0)


def _pipeline_command(checkpoint_glob: Path, context_path: Path, artifact_root: Path) -> str:
    return (
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
    )


if __name__ == "__main__":
    raise SystemExit(main())
