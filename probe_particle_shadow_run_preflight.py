"""Preflight for the first real particle all-candidate shadow run.

Research-only: this script inspects local prerequisites and writes command
templates. It does not start the live bot, recorder, websocket, or any orders.
"""
from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable


REPORT_DIR = Path("logs") / "particle_research" / "reports"
LATEST_JSON = REPORT_DIR / "particle_shadow_run_preflight_latest.json"
LATEST_MD = REPORT_DIR / "particle_shadow_run_preflight_latest.md"


@dataclass(frozen=True)
class PreflightResult:
    generated_utc: str
    dataset: str
    artifact_root: str
    env_file_exists: bool
    api_key_present: bool
    private_key_path_present: bool
    private_key_file_exists: bool
    passive_recorder_exists: bool
    context_tailer_exists: bool
    paired_runner_exists: bool
    checkpoint_file_count: int
    checkpoint_row_count: int
    context_file_exists: bool
    context_row_count: int
    market_results_exists: bool
    market_results_row_count: int
    ready_to_collect: bool
    ready_to_pipeline: bool
    recorder_command: str
    context_tailer_command: str
    paired_run_command: str
    pipeline_command: str
    online_report_command: str
    notes: tuple[str, ...]


def build_preflight(
    *,
    dataset: str,
    artifact_root: Path,
    context_path: Path,
    market_results_path: Path,
    workspace: Path = Path("."),
) -> PreflightResult:
    workspace = workspace.resolve()
    env = _read_env_file(workspace / ".env")
    private_key_path_raw = env.get("KALSHI_PRIVATE_KEY_PATH", "")
    private_key_path = _resolve_workspace_path(workspace, private_key_path_raw) if private_key_path_raw else None
    checkpoint_root = workspace / "research_data" / dataset / "book_checkpoints"
    checkpoint_files = sorted(checkpoint_root.rglob("*.ndjson")) if checkpoint_root.exists() else []
    checkpoint_rows = _line_count(checkpoint_files)
    context_rows = _line_count([context_path]) if context_path.exists() else 0
    market_rows = _count_market_results(market_results_path) if market_results_path.exists() else 0
    passive_recorder = workspace / "research_native_passive_ws_recorder.py"
    context_tailer = workspace / "research_particle" / "v28_context_tailer.py"
    paired_runner = workspace / "research_particle" / "paired_passive_shadow_run.py"
    latest_v28_log = _latest_execution_events_path(workspace)
    api_key_present = bool(env.get("KALSHI_API_KEY_ID", "").strip())
    private_key_file_exists = bool(private_key_path and private_key_path.exists())
    ready_to_collect = (
        passive_recorder.exists()
        and context_tailer.exists()
        and api_key_present
        and bool(private_key_path_raw)
        and private_key_file_exists
    )
    ready_to_pipeline = checkpoint_rows > 0 and context_rows > 0 and market_rows > 0
    notes = _notes(
        ready_to_collect=ready_to_collect,
        ready_to_pipeline=ready_to_pipeline,
        checkpoint_rows=checkpoint_rows,
        context_rows=context_rows,
        market_rows=market_rows,
        private_key_path_present=bool(private_key_path_raw),
        private_key_file_exists=private_key_file_exists,
    )
    checkpoint_glob = workspace / "research_data" / dataset / "book_checkpoints" / "**" / "*.ndjson"
    raw_candidates = artifact_root / "pipeline_work" / "raw_candidates.ndjson"
    candidates = artifact_root / "candidate_snapshots" / "candidate_snapshots.ndjson"
    labels = artifact_root / "settlement_labels" / "settlement_labels.ndjson"
    return PreflightResult(
        generated_utc=datetime.now(timezone.utc).isoformat(),
        dataset=dataset,
        artifact_root=str(artifact_root),
        env_file_exists=(workspace / ".env").exists(),
        api_key_present=api_key_present,
        private_key_path_present=bool(private_key_path_raw),
        private_key_file_exists=private_key_file_exists,
        passive_recorder_exists=passive_recorder.exists(),
        context_tailer_exists=context_tailer.exists(),
        paired_runner_exists=paired_runner.exists(),
        checkpoint_file_count=len(checkpoint_files),
        checkpoint_row_count=checkpoint_rows,
        context_file_exists=context_path.exists(),
        context_row_count=context_rows,
        market_results_exists=market_results_path.exists(),
        market_results_row_count=market_rows,
        ready_to_collect=ready_to_collect,
        ready_to_pipeline=ready_to_pipeline,
        recorder_command=(
            "python research_native_passive_ws_recorder.py "
            f"--dataset {dataset} "
            "--strategy-tag particle_shadow_readonly "
            "--bot-tag particle_shadow_readonly "
            "--checkpoint-interval-seconds 1 "
            "--checkpoint-depth 5"
        ),
        context_tailer_command=(
            "python -m research_particle.v28_context_tailer "
            f"--input \"{latest_v28_log if latest_v28_log else '<v28_execution_events.ndjson>'}\" "
            f"--output \"{context_path}\" "
            f"--issues \"{artifact_root / 'passive_context_issues.ndjson'}\" "
            f"--status \"{artifact_root / 'passive_context_tailer_status.json'}\" "
            "--follow "
            "--start-at-end "
            "--seed-last-contexts "
            "--append-ok"
        ),
        paired_run_command=(
            "python -m research_particle.paired_passive_shadow_run "
            "--run-seconds 900 "
            "--checkpoint-interval-seconds 1 "
            "--checkpoint-depth 5 "
            "--record-independent-spot "
            "--independent-spot-feed coinbase "
            "--independent-spot-max-age-ms 5000"
        ),
        pipeline_command=(
            "python -m research_particle.shadow_pipeline "
            "--source-type passive_checkpoint "
            f"--checkpoints \"{checkpoint_glob}\" "
            f"--contexts \"{context_path}\" "
            f"--market-results \"{market_results_path}\" "
            f"--root \"{artifact_root}\" "
            "--annualized-vol 0.65 "
            "--sample-count 2000 "
            "--seed 1 "
            "--min-fill-prob 0.5 "
            "--counterfactual-fill-threshold 0.5"
        ),
        online_report_command=(
            "python -m research_particle.reports "
            f"--candidates \"{candidates}\" "
            f"--labels \"{labels}\" "
            f"--output-dir \"{artifact_root / 'reports'}\" "
            "--stem online_calibrated_particle_replay "
            "--online-calibrated "
            "--min-fill-prob 0.5 "
            "--counterfactual-fill-threshold 0.5"
        ),
        notes=notes,
    )


def write_preflight(result: PreflightResult, *, output_dir: Path = REPORT_DIR) -> tuple[Path, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    json_path = output_dir / "particle_shadow_run_preflight_latest.json"
    md_path = output_dir / "particle_shadow_run_preflight_latest.md"
    payload = asdict(result)
    json_path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    md_path.write_text(_markdown(result), encoding="utf-8")
    return json_path, md_path


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Preflight the first real particle shadow run.")
    parser.add_argument("--dataset", default="particle_shadow_readonly")
    parser.add_argument(
        "--artifact-root",
        type=Path,
        default=Path("logs") / "particle_research" / "real_shadow" / "particle_shadow_readonly",
    )
    parser.add_argument(
        "--contexts",
        type=Path,
        default=Path("logs") / "particle_research" / "real_shadow" / "particle_shadow_readonly" / "passive_contexts.ndjson",
    )
    parser.add_argument(
        "--market-results",
        type=Path,
        default=Path("logs") / "particle_research" / "real_shadow" / "particle_shadow_readonly" / "market_results.json",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    result = build_preflight(
        dataset=args.dataset,
        artifact_root=args.artifact_root,
        context_path=args.contexts,
        market_results_path=args.market_results,
    )
    json_path, md_path = write_preflight(result)
    print("Particle shadow run preflight complete")
    print(f"ready_to_collect={result.ready_to_collect}")
    print(f"ready_to_pipeline={result.ready_to_pipeline}")
    print(f"checkpoint_row_count={result.checkpoint_row_count}")
    print(f"context_row_count={result.context_row_count}")
    print(f"market_results_row_count={result.market_results_row_count}")
    print(f"json={json_path}")
    print(f"report={md_path}")
    return 0


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


def _resolve_workspace_path(workspace: Path, value: str) -> Path:
    path = Path(value).expanduser()
    return path if path.is_absolute() else (workspace / path).resolve()


def _line_count(paths: Iterable[Path]) -> int:
    total = 0
    for path in paths:
        if not path.exists():
            continue
        with path.open("r", encoding="utf-8", errors="replace") as handle:
            total += sum(1 for line in handle if line.strip())
    return total


def _latest_execution_events_path(workspace: Path) -> Path | None:
    logs = workspace / "logs"
    if not logs.exists():
        return None
    candidates = sorted(
        logs.rglob("execution_events.ndjson"),
        key=lambda path: path.stat().st_mtime if path.exists() else 0.0,
        reverse=True,
    )
    return candidates[0] if candidates else None


def _count_market_results(path: Path) -> int:
    if not path.exists():
        return 0
    if path.suffix.lower() == ".csv":
        return max(0, _line_count([path]) - 1)
    try:
        payload = json.loads(path.read_text(encoding="utf-8", errors="replace"))
    except Exception:
        return 0
    if isinstance(payload, list):
        return sum(1 for row in payload if isinstance(row, dict))
    if isinstance(payload, dict):
        return len(payload)
    return 0


def _notes(
    *,
    ready_to_collect: bool,
    ready_to_pipeline: bool,
    checkpoint_rows: int,
    context_rows: int,
    market_rows: int,
    private_key_path_present: bool,
    private_key_file_exists: bool,
) -> tuple[str, ...]:
    notes: list[str] = []
    if not ready_to_collect:
        notes.append("Cannot start read-only passive collection until env/private-key/context-recorder prerequisites are present.")
    if private_key_path_present and not private_key_file_exists:
        notes.append("KALSHI_PRIVATE_KEY_PATH is set but the file was not found.")
    if checkpoint_rows <= 0:
        notes.append("No passive orderbook checkpoint rows found yet.")
    if context_rows <= 0:
        notes.append("No timestamped passive context rows found yet.")
    if market_rows <= 0:
        notes.append("No market result rows found yet; replay labels are not available.")
    if ready_to_pipeline:
        notes.append("Pipeline prerequisites are present; run the command template with a fresh artifact root.")
    return tuple(notes)


def _markdown(result: PreflightResult) -> str:
    return "\n".join(
        [
            "# Particle Shadow Run Preflight",
            "",
            f"Generated UTC: `{result.generated_utc}`",
            f"Dataset: `{result.dataset}`",
            f"Artifact root: `{result.artifact_root}`",
            "",
            "## Readiness",
            "",
            f"- ready_to_collect: `{result.ready_to_collect}`",
            f"- ready_to_pipeline: `{result.ready_to_pipeline}`",
            f"- env_file_exists: `{result.env_file_exists}`",
            f"- api_key_present: `{result.api_key_present}`",
            f"- private_key_path_present: `{result.private_key_path_present}`",
            f"- private_key_file_exists: `{result.private_key_file_exists}`",
            f"- passive_recorder_exists: `{result.passive_recorder_exists}`",
            f"- context_tailer_exists: `{result.context_tailer_exists}`",
            f"- paired_runner_exists: `{result.paired_runner_exists}`",
            f"- checkpoint_file_count: `{result.checkpoint_file_count}`",
            f"- checkpoint_row_count: `{result.checkpoint_row_count}`",
            f"- context_row_count: `{result.context_row_count}`",
            f"- market_results_row_count: `{result.market_results_row_count}`",
            "",
            "## Commands",
            "",
            "```powershell",
            result.recorder_command,
            "",
            result.context_tailer_command,
            "",
            result.paired_run_command,
            "",
            result.pipeline_command,
            "",
            result.online_report_command,
            "```",
            "",
            "## Notes",
            "",
            *[f"- {note}" for note in result.notes],
            "",
        ]
    )


if __name__ == "__main__":
    raise SystemExit(main())
