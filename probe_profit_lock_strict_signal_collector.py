"""Research-only strict signal collector for locked BTC 15m profit policies.

The registered-signal evidence is only useful if the monitor is running while
markets are still unresolved. This utility runs the strict pre-resolution
monitors repeatedly and writes a compact heartbeat report so forward evidence
can accumulate against the recurring-market denominator.

No orders are submitted and no live bot code, state, or processes are touched.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

from probe_market_interval_80coverage import OUT_DIR, clean_json


POST_CAPTURE_COMMANDS = [
    ("market_denominator_audit", ["probe_profit_lock_market_denominator_audit.py"]),
    ("registered_signal_readiness", ["probe_profit_lock_registered_signal_readiness.py"]),
    ("registered_signal_delta", ["probe_profit_lock_registered_signal_delta.py"]),
]

STRICT_ATTRIBUTION = ("strict_failure_attribution", ["probe_profit_lock_strict_failure_attribution.py"])
DEFAULT_COMMAND_TIMEOUT_SECONDS = 120.0


def clean_json_local(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(k): clean_json_local(v) for k, v in value.items()}
    if isinstance(value, list):
        return [clean_json_local(v) for v in value]
    return clean_json(value)


def run_command(name: str, args: List[str], timeout_seconds: float) -> Dict[str, Any]:
    started = datetime.now(timezone.utc)
    try:
        proc = subprocess.run(
            [sys.executable, *args],
            cwd=Path(__file__).resolve().parent,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
            timeout=max(1.0, float(timeout_seconds)),
        )
        returncode = int(proc.returncode)
        stdout_tail = proc.stdout.strip().splitlines()[-8:]
        stderr_tail = proc.stderr.strip().splitlines()[-8:]
    except subprocess.TimeoutExpired as exc:
        returncode = 124
        stdout = exc.stdout or ""
        stderr = exc.stderr or ""
        if isinstance(stdout, bytes):
            stdout = stdout.decode("utf-8", errors="replace")
        if isinstance(stderr, bytes):
            stderr = stderr.decode("utf-8", errors="replace")
        stdout_tail = str(stdout).strip().splitlines()[-8:]
        stderr_tail = [*str(stderr).strip().splitlines()[-7:], f"timed out after {timeout_seconds:.1f}s"]
    ended = datetime.now(timezone.utc)
    return {
        "name": name,
        "args": args,
        "returncode": returncode,
        "started_utc": started.isoformat(),
        "ended_utc": ended.isoformat(),
        "stdout_tail": stdout_tail,
        "stderr_tail": stderr_tail,
    }


def load_json(path: Path) -> Dict[str, Any]:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}


def build_commands(iteration: int, fetch_every: int, attribution_every: int, metadata_every: int) -> List[tuple[str, List[str]]]:
    commands: List[tuple[str, List[str]]] = []
    if metadata_every > 0 and iteration % metadata_every == 0:
        commands.append(("watched_market_metadata_refresh", ["probe_refresh_watched_market_metadata.py", "--latest", "3"]))
    fetch_this_iteration = fetch_every > 0 and iteration % fetch_every == 0
    fetch_args = ["--fetch-btc-candles"] if fetch_this_iteration else []
    commands.extend(
        [
            (
                "pending_signal_monitor_fetch" if fetch_this_iteration else "pending_signal_monitor",
                ["probe_profit_lock_pending_signal_monitor.py", *fetch_args],
            ),
            (
                "path_pending_monitor_fetch" if fetch_this_iteration else "path_pending_monitor",
                ["probe_kinetic_path_confirmation_pending_monitor.py", *fetch_args],
            ),
        ]
    )
    commands.extend(POST_CAPTURE_COMMANDS)
    if attribution_every > 0 and iteration % attribution_every == 0:
        commands.append(STRICT_ATTRIBUTION)
    return commands


def write_report(path: Path, generated: str, iteration: int, results: List[Dict[str, Any]]) -> None:
    readiness = load_json(OUT_DIR / "profit_lock_registered_signal_readiness_latest.json")
    denominator = load_json(OUT_DIR / "profit_lock_market_denominator_audit_latest.json")
    pending = load_json(OUT_DIR / "profit_lock_pending_signal_monitor_latest.json")
    path_pending = load_json(OUT_DIR / "kinetic_path_confirmation_pending_monitor_latest.json")

    rows = readiness.get("rows", [])
    best_registered = sorted(
        rows,
        key=lambda row: (
            float(row.get("registered_coverage") or 0.0),
            float(row.get("net_pnl_cents") or -1e9),
        ),
        reverse=True,
    )[:5]

    lines = [
        "# Profit Lock Strict Signal Collector",
        "",
        f"Generated UTC: `{generated}`",
        "",
        "## Scope",
        "",
        "- Research-only collector; no orders are submitted and no bot files or live processes are touched.",
        "- Runs strict pre-resolution monitors so future evidence is registered before outcomes are known.",
        "- Denominator is recurring BTC 15-minute markets, not fills or selected heartbeat rows.",
        "",
        f"- Iteration: {iteration}",
        f"- Failed steps: {sum(1 for result in results if result['returncode'] != 0)}",
        f"- Main monitor new records: {pending.get('new_records')}",
        f"- Path monitor new records: {path_pending.get('new_records')}",
        f"- Strict registered coverage failures: {denominator.get('registered_coverage_fail_count')}",
        "",
        "## Command Results",
        "",
        "| step | return code | stdout tail | stderr tail |",
        "|---|---:|---|---|",
    ]
    for result in results:
        stdout = "<br>".join(result["stdout_tail"]) if result["stdout_tail"] else ""
        stderr = "<br>".join(result["stderr_tail"]) if result["stderr_tail"] else ""
        lines.append(f"| `{result['name']}` | {result['returncode']} | {stdout} | {stderr} |")
    lines += [
        "",
        "## Top Registered Coverage Rows",
        "",
        "| lock | registered/resolved/pending | registered coverage | resolved coverage | net P&L | ready |",
        "|---|---:|---:|---:|---:|---|",
    ]
    for row in best_registered:
        lines.append(
            f"| {row.get('name')} | {row.get('registered')}/{row.get('resolved')}/{row.get('pending')} | "
            f"{row.get('registered_coverage')} | {row.get('resolved_coverage')} | "
            f"{row.get('net_pnl_cents')}c | {row.get('registered_ready')} |"
        )
    if not best_registered:
        lines.append("| none | 0/0/0 | NA | NA | 0c | False |")
    lines += ["", "## Read", ""]
    if any(result["returncode"] != 0 for result in results):
        lines.append("- One or more collector steps failed; inspect stderr before relying on this iteration.")
    else:
        lines.append("- Collector iteration completed; strict evidence was refreshed without changing live trading code.")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def run_iteration(
    iteration: int,
    fetch_every: int,
    attribution_every: int,
    metadata_every: int,
    command_timeout_seconds: float,
) -> Dict[str, Any]:
    generated = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%SZ")
    results = [
        run_command(name, args, command_timeout_seconds)
        for name, args in build_commands(iteration, fetch_every, attribution_every, metadata_every)
    ]
    md_latest = OUT_DIR / "profit_lock_strict_signal_collector_latest.md"
    md_stamp = OUT_DIR / f"profit_lock_strict_signal_collector_{generated}.md"
    json_latest = OUT_DIR / "profit_lock_strict_signal_collector_latest.json"
    json_stamp = OUT_DIR / f"profit_lock_strict_signal_collector_{generated}.json"
    write_report(md_latest, generated, iteration, results)
    write_report(md_stamp, generated, iteration, results)
    payload = {
        "generated_utc": generated,
        "iteration": iteration,
        "commands": results,
        "failed_steps": sum(1 for result in results if result["returncode"] != 0),
    }
    for path in [json_latest, json_stamp]:
        path.write_text(json.dumps(clean_json_local(payload), indent=2, sort_keys=True), encoding="utf-8")
    return payload


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--iterations",
        type=int,
        default=1,
        help="Number of collector iterations. Use 0 for an infinite research-only loop.",
    )
    parser.add_argument("--interval-seconds", type=float, default=60.0)
    parser.add_argument(
        "--fetch-btc-candles-every",
        type=int,
        default=1,
        help="Pass --fetch-btc-candles to pending monitors every N iterations. Default 1 keeps active-market physics fresh.",
    )
    parser.add_argument(
        "--strict-attribution-every",
        type=int,
        default=5,
        help="Run strict failure attribution every N iterations. Default 5.",
    )
    parser.add_argument(
        "--refresh-metadata-every",
        type=int,
        default=1,
        help="Refresh watched Kalshi market metadata every N iterations. Default 1 prevents strike=NA watch lines from dropping active markets.",
    )
    parser.add_argument("--command-timeout-seconds", type=float, default=DEFAULT_COMMAND_TIMEOUT_SECONDS)
    args = parser.parse_args()

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    iteration = 1
    failures = 0
    while args.iterations == 0 or iteration <= args.iterations:
        payload = run_iteration(
            iteration,
            max(0, int(args.fetch_btc_candles_every)),
            max(0, int(args.strict_attribution_every)),
            max(0, int(args.refresh_metadata_every)),
            max(1.0, float(args.command_timeout_seconds)),
        )
        failures += int(payload["failed_steps"])
        print(
            "collector_iteration={iteration} failed_steps={failed} report={report}".format(
                iteration=iteration,
                failed=payload["failed_steps"],
                report=OUT_DIR / "profit_lock_strict_signal_collector_latest.md",
            )
        )
        if args.iterations != 0 and iteration >= args.iterations:
            break
        iteration += 1
        time.sleep(max(1.0, float(args.interval_seconds)))
    return 0 if failures == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
