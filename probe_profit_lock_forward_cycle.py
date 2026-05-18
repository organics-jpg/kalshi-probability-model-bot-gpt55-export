"""One-shot forward refresh cycle for locked BTC 15m profit candidates.

This script runs the research-only refresh/validation sequence for the existing
locked EV candidates. It intentionally does not run any retrospective optimizer
or update any locks. It only refreshes live-derived research data, evaluates the
existing locks, and writes a compact cycle report.

Research-only: no orders are submitted and no bot files or live processes are
modified.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

from probe_market_interval_80coverage import OUT_DIR, clean_json


COMMANDS = [
    ("heartbeat_refresh", ["probe_live_heartbeat_two_side_fv.py", "--fetch-btc-candles"]),
    ("pending_signal_monitor", ["probe_profit_lock_pending_signal_monitor.py"]),
    ("path_pending_monitor", ["probe_kinetic_path_confirmation_pending_monitor.py"]),
    ("original_fresh", ["probe_profit_frontier_fresh_validation.py"]),
    ("frontier_v2_fresh", ["probe_profit_frontier_v2_fresh_validation.py"]),
    ("frontier_locked_policy_validation", ["probe_profit_frontier_locked_policy_validation.py"]),
    ("book_to_score_wait_validation", ["probe_book_to_score_wait_forward_validation.py"]),
    ("book_hour04_v2_switch_validation", ["probe_book_v2_session_switch_forward_validation.py"]),
    ("book_refmargin_score_switch_validation", ["probe_book_score_reference_margin_switch_forward_validation.py"]),
    ("challenger_fresh", ["probe_profit_challenger_fresh_validation.py"]),
    ("touch_hazard_fresh", ["probe_profit_touch_hazard_fresh_validation.py"]),
    ("touch_overlay_fresh", ["probe_touch_hazard_overlay_fresh_validation.py"]),
    ("kinetic_touch_fresh", ["probe_profit_kinetic_touch_fresh_validation.py"]),
    ("hazard_mean_touch80_fresh", ["probe_hazard_mean_touch80_fresh_validation.py"]),
    ("logit_blend_edge10_fresh", ["probe_logit_blend_edge10_fresh_validation.py"]),
    ("logit_blend_thresh55_edge15_fresh", ["probe_logit_blend_thresh55_edge15_fresh_validation.py"]),
    ("hazard_fallback_logit55_fresh", ["probe_hazard_fallback_logit55_fresh_validation.py"]),
    ("hazard_fallback_logit55_wait8_fresh", ["probe_hazard_fallback_logit55_wait8_fresh_validation.py"]),
    ("hazard_fallback_score60_fresh", ["probe_hazard_fallback_score60_fresh_validation.py"]),
    ("kinetic_guard_fresh", ["probe_kinetic_guard_fresh_validation.py"]),
    ("kinetic_price_guard_fresh", ["probe_kinetic_price_guard_fresh_validation.py"]),
    ("kinetic_combo_price_guard_fresh", ["probe_kinetic_combo_price_guard_fresh_validation.py"]),
    ("kinetic_path_confirm_fresh", ["probe_kinetic_path_confirmation_fresh_validation.py"]),
    ("market_denominator_audit", ["probe_profit_lock_market_denominator_audit.py"]),
    ("registered_signal_readiness", ["probe_profit_lock_registered_signal_readiness.py"]),
    ("registry_fresh_validation", ["probe_profit_lock_registry_fresh_validation.py"]),
    ("sample_size", ["probe_profit_lock_sample_size_requirements.py"]),
    ("bayesian_ev", ["probe_profit_lock_bayesian_ev_monitor.py"]),
    ("registered_signal_delta", ["probe_profit_lock_registered_signal_delta.py"]),
    ("registry_recompute_divergence", ["probe_profit_lock_registry_recompute_divergence.py"]),
    ("strict_failure_attribution", ["probe_profit_lock_strict_failure_attribution.py"]),
]


def clean_json_local(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(k): clean_json_local(v) for k, v in value.items()}
    if isinstance(value, list):
        return [clean_json_local(v) for v in value]
    return clean_json(value)


def run_command(name: str, args: List[str]) -> Dict[str, Any]:
    start = datetime.now(timezone.utc)
    proc = subprocess.run(
        [sys.executable, *args],
        cwd=Path(__file__).resolve().parent,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    end = datetime.now(timezone.utc)
    return {
        "name": name,
        "args": args,
        "returncode": int(proc.returncode),
        "started_utc": start.isoformat(),
        "ended_utc": end.isoformat(),
        "stdout_tail": proc.stdout.strip().splitlines()[-10:],
        "stderr_tail": proc.stderr.strip().splitlines()[-10:],
    }


def load_json(path: Path) -> Dict[str, Any]:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}


def write_report(path: Path, generated: str, results: List[Dict[str, Any]], summary: Dict[str, Any]) -> None:
    lines = [
        "# Profit Lock Forward Cycle",
        "",
        f"Generated UTC: `{generated}`",
        "",
        "## Scope",
        "",
        "- Research-only one-shot cycle; no orders are submitted and no bot files or live processes are touched.",
        "- Runs refresh and validators for existing locked EV candidates, including separate combo price-guard and path-confirmation locks.",
        "- Does not run optimizers and does not update locks.",
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
        "## Lock Summary",
        "",
        "| lock | fresh selected/base | wins/losses | net P&L | coverage | Wilson ready | Bayesian ready |",
        "|---|---:|---:|---:|---:|---|---|",
    ]
    for row in summary.get("sample_size_rows", []):
        bayes = next((item for item in summary.get("bayesian_rows", []) if item.get("name") == row.get("name")), {})
        lines.append(
            f"| {row.get('name')} | {row.get('fresh_markets')}/{row.get('fresh_base_markets')} | "
            f"{row.get('fresh_wins')}/{row.get('fresh_losses')} | {row.get('fresh_net_pnl_cents')}c | "
            f"{row.get('fresh_coverage')} | {row.get('completion_ready')} | {bayes.get('posterior_ready')} |"
        )
    lines += [
        "",
        "## Registered Signal Summary",
        "",
        "| lock | registered/resolved/pending | wins/losses | net P&L | resolved coverage | registered coverage | Wilson ready | Bayesian ready |",
        "|---|---:|---:|---:|---:|---:|---|---|",
    ]
    for row in summary.get("registered_rows", []):
        lines.append(
            f"| {row.get('name')} | {row.get('registered')}/{row.get('resolved')}/{row.get('pending')} | "
            f"{row.get('wins')}/{row.get('losses')} | {row.get('net_pnl_cents')}c | "
            f"{row.get('resolved_coverage')} | {row.get('registered_coverage')} | "
            f"{row.get('registered_ready')} | {row.get('registered_bayesian_ready')} |"
        )
    lines += [
        "",
        "## Strict Failure Attribution",
        "",
        f"- Strict resolved rows: {summary.get('strict_failure_resolved_rows')}",
        f"- Diagnostic blocker rows scanned: {summary.get('strict_failure_blocker_count')}",
        f"- Positive blockers retaining >=80% of strict rows: {summary.get('strict_failure_positive_80ret_count')}",
    ]
    lines += ["", "## Read", ""]
    if any(result["returncode"] != 0 for result in results):
        lines.append("- One or more cycle commands failed; inspect stderr before relying on this cycle.")
    elif int(summary.get("denominator_coverage_fail_count") or 0) > 0:
        lines.append(
            f"- Cycle completed, but {summary.get('denominator_coverage_fail_count')} locks fail the strict registered recurring-market coverage audit."
        )
    elif not any(row.get("completion_ready") for row in summary.get("sample_size_rows", [])):
        lines.append("- Cycle completed, but no lock is sample-size ready.")
    else:
        lines.append("- At least one lock cleared the Wilson sample-size gate.")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--skip-heartbeat-refresh",
        action="store_true",
        help="Skip the live heartbeat/candle refresh and only rerun validators/monitors.",
    )
    args = parser.parse_args()
    generated = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%SZ")
    commands = COMMANDS[1:] if args.skip_heartbeat_refresh else COMMANDS
    results = [run_command(name, command_args) for name, command_args in commands]
    sample_payload = load_json(OUT_DIR / "profit_lock_sample_size_requirements_latest.json")
    bayes_payload = load_json(OUT_DIR / "profit_lock_bayesian_ev_monitor_latest.json")
    registered_payload = load_json(OUT_DIR / "profit_lock_registered_signal_readiness_latest.json")
    denominator_payload = load_json(OUT_DIR / "profit_lock_market_denominator_audit_latest.json")
    delta_payload = load_json(OUT_DIR / "profit_lock_registered_signal_delta_latest.json")
    attribution_payload = load_json(OUT_DIR / "profit_lock_strict_failure_attribution_latest.json")
    attribution_blockers = attribution_payload.get("blockers", [])
    positive_80ret_blockers = [
        row
        for row in attribution_blockers
        if float(row.get("retention") or 0.0) >= 0.80 and float(row.get("net_pnl_cents") or 0.0) > 0.0
    ]
    summary = {
        "sample_size_rows": sample_payload.get("rows", []),
        "bayesian_rows": bayes_payload.get("rows", []),
        "registered_rows": registered_payload.get("rows", []),
        "sample_size_ready_count": sample_payload.get("ready_count"),
        "bayesian_ready_count": bayes_payload.get("ready_count"),
        "registered_ready_count": registered_payload.get("ready_count"),
        "registered_bayesian_ready_count": registered_payload.get("bayesian_ready_count"),
        "denominator_coverage_fail_count": denominator_payload.get("registered_coverage_fail_count"),
        "registered_delta_changed_count": delta_payload.get("changed_count"),
        "strict_failure_resolved_rows": sum(int(row.get("resolved") or 0) for row in attribution_payload.get("summaries", [])),
        "strict_failure_blocker_count": len(attribution_blockers),
        "strict_failure_positive_80ret_count": len(positive_80ret_blockers),
    }
    md_latest = OUT_DIR / "profit_lock_forward_cycle_latest.md"
    md_stamp = OUT_DIR / f"profit_lock_forward_cycle_{generated}.md"
    json_latest = OUT_DIR / "profit_lock_forward_cycle_latest.json"
    json_stamp = OUT_DIR / f"profit_lock_forward_cycle_{generated}.json"
    write_report(md_latest, generated, results, summary)
    write_report(md_stamp, generated, results, summary)
    payload = {
        "generated_utc": generated,
        "commands": results,
        "summary": summary,
    }
    for path in [json_latest, json_stamp]:
        path.write_text(json.dumps(clean_json_local(payload), indent=2, sort_keys=True), encoding="utf-8")
    print("Profit lock forward cycle complete")
    print(f"failed_steps={sum(1 for result in results if result['returncode'] != 0)}")
    print(f"report={md_latest}")
    return 0 if all(result["returncode"] == 0 for result in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
