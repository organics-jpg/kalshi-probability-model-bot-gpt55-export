"""One-shot refresh for active strict-forward FV candidates.

Research-only helper. Runs active shadow monitors/denominators serially to avoid
shared candle/cache races, then rebuilds the consolidated comparison.

No live bot files, processes, order paths, or persistent loops are touched.
"""
from __future__ import annotations

import json
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from probe_market_interval_80coverage import clean_json


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
REPORT_MD = OUT_DIR / "active_forward_refresh_latest.md"
REPORT_JSON = OUT_DIR / "active_forward_refresh_latest.json"

STEPS = [
    ("v47_shadow", "probe_v47_recross_hazard_shadow_monitor.py"),
    ("v47_denominator", "probe_v47_recross_hazard_forward_denominator.py"),
    ("v50_shadow", "probe_v50_thin_edge_certainty_shadow_monitor.py"),
    ("v50_denominator", "probe_v50_thin_edge_certainty_forward_denominator.py"),
    ("v53_shadow", "probe_v53_weak_recross_thin_edge_shadow_monitor.py"),
    ("v53_denominator", "probe_v53_weak_recross_thin_edge_forward_denominator.py"),
    ("v55_shadow", "probe_v55_book_anchor_recross_shadow_monitor.py"),
    ("v55_denominator", "probe_v55_book_anchor_recross_forward_denominator.py"),
    ("v57_shadow", "probe_v57_v55_hold15_shadow_monitor.py"),
    ("v57_denominator", "probe_v57_v55_hold15_forward_denominator.py"),
    ("v58_shadow", "probe_v58_v55_margin_exit_shadow_monitor.py"),
    ("v58_denominator", "probe_v58_v55_margin_exit_forward_denominator.py"),
    ("v60_shadow", "probe_v60_v55_no_side_margin_exit_shadow_monitor.py"),
    ("v60_denominator", "probe_v60_v55_no_side_margin_exit_forward_denominator.py"),
    ("v61_shadow", "probe_v61_v55_no_side_prob56_margin_exit_shadow_monitor.py"),
    ("v61_denominator", "probe_v61_v55_no_side_prob56_margin_exit_forward_denominator.py"),
    ("v66_shadow", "probe_v66_no_bookgap_balanced_shadow_monitor.py"),
    ("v66_denominator", "probe_v66_no_bookgap_balanced_forward_denominator.py"),
    ("v69_shadow", "probe_v69_v55_entry_v66_exit_shadow_monitor.py"),
    ("v69_denominator", "probe_v69_v55_entry_v66_exit_forward_denominator.py"),
    ("v70_shadow", "probe_v70_v55_entry_v66_margin_exit_shadow_monitor.py"),
    ("v70_denominator", "probe_v70_v55_entry_v66_margin_exit_forward_denominator.py"),
    ("current_comparison", "probe_current_fv_candidate_comparison.py"),
]


def tail(text: str, max_lines: int = 8) -> str:
    lines = [line.rstrip() for line in text.splitlines() if line.strip()]
    return "\n".join(lines[-max_lines:])


def run_step(label: str, script: str) -> dict[str, Any]:
    start = time.monotonic()
    proc = subprocess.run(
        [sys.executable, str(ROOT / script)],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    elapsed = time.monotonic() - start
    return {
        "label": label,
        "script": script,
        "returncode": int(proc.returncode),
        "elapsed_seconds": elapsed,
        "stdout_tail": tail(proc.stdout),
        "stderr_tail": tail(proc.stderr),
    }


def write_report(generated: str, results: list[dict[str, Any]]) -> None:
    failures = [row for row in results if int(row["returncode"]) != 0]
    lines = [
        "# Active Forward Refresh",
        "",
        f"Generated UTC: `{generated}`",
        "",
        "## Scope",
        "",
        "- Research-only one-shot refresh of active strict-forward FV candidates.",
        "- Runs scripts serially to avoid shared candle/cache races.",
        "- Live bot and order paths untouched.",
        "",
        "## Steps",
        "",
        "| step | script | seconds | code |",
        "|---|---|---:|---:|",
    ]
    for row in results:
        lines.append(
            f"| `{row['label']}` | `{row['script']}` | {float(row['elapsed_seconds']):.1f} | {int(row['returncode'])} |"
        )
    lines += ["", "## Read", ""]
    if failures:
        lines.append(f"- Refresh completed with {len(failures)} failing step(s). Inspect JSON stdout/stderr tails.")
    else:
        lines.append("- Refresh completed successfully. Consolidated comparison was rebuilt.")
    REPORT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")
    REPORT_JSON.write_text(
        json.dumps(clean_json({"generated_utc": generated, "results": results}), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    generated = datetime.now(timezone.utc).isoformat()
    results = [run_step(label, script) for label, script in STEPS]
    write_report(generated, results)
    failures = [row for row in results if int(row["returncode"]) != 0]
    print("active forward refresh complete")
    print(f"report={REPORT_MD}")
    print(f"failed_steps={len(failures)}")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
