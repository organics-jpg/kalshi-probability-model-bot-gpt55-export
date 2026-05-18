"""Stability probe for the v28 exit-clock row source.

Research-only; no live bot changes or orders.

Several exit-watch reports call build_scored_rows(), which reconstructs shadow
trades and scores market outcomes. This probe checks whether repeated reads in
one run produce the same denominator before using that source for a new frozen
watch.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from probe_v28_exit_policy_common_clock_watch import build_scored_rows


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
OUT_JSON = OUT_DIR / "v28_exit_clock_source_stability_latest.json"
OUT_MD = OUT_DIR / "v28_exit_clock_source_stability_latest.md"

SAMPLES = 5


def row_key(row: dict[str, Any]) -> tuple[Any, Any, Any]:
    return (row.get("market"), row.get("side"), row.get("entry_ts"))


def build_report() -> dict[str, Any]:
    samples = []
    key_sets: list[set[tuple[Any, Any, Any]]] = []
    for index in range(SAMPLES):
        rows = list(build_scored_rows())
        keys = {row_key(row) for row in rows}
        key_sets.append(keys)
        samples.append({
            "sample_index": index,
            "rows": len(rows),
            "unique_keys": len(keys),
            "first_key": list(next(iter(keys))) if keys else None,
            "last_entry_ts": max((str(row.get("entry_ts") or "") for row in rows), default=""),
        })
    counts = [sample["rows"] for sample in samples]
    common_keys = set.intersection(*key_sets) if key_sets else set()
    union_keys = set.union(*key_sets) if key_sets else set()
    stable = len(set(counts)) == 1 and len(common_keys) == len(union_keys)
    blockers = []
    if not stable:
        blockers.append("exit_clock_source_not_stable_across_repeated_reads")
    return {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "samples": samples,
        "row_count_values": counts,
        "min_rows": min(counts) if counts else 0,
        "max_rows": max(counts) if counts else 0,
        "common_key_count": len(common_keys),
        "union_key_count": len(union_keys),
        "stable_for_new_freeze": stable,
        "blockers": blockers,
        "interpretation": [
            "This checks the exit-clock source used by common-clock exit reports.",
            "If repeated reads differ, new watches should use a materialized snapshot or wait until the source settles before freezing a denominator-sensitive rule.",
        ],
    }


def write_outputs(report: dict[str, Any]) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8")
    lines = [
        "# v28 Exit-Clock Source Stability",
        "",
        "Research-only. No live bot logic changes, no orders.",
        "",
        f"- Generated UTC: `{report.get('generated_at_utc')}`",
        f"- Stable for new freeze: `{report.get('stable_for_new_freeze')}`",
        f"- Row count values: `{report.get('row_count_values')}`",
        f"- Common / union keys: `{report.get('common_key_count')}` / `{report.get('union_key_count')}`",
        f"- Blockers: `{', '.join(report.get('blockers') or []) or 'none'}`",
        "",
        "## Samples",
        "",
        "| sample | rows | unique keys | last entry ts |",
        "|---:|---:|---:|---|",
    ]
    for sample in report.get("samples") or []:
        lines.append(
            f"| {sample.get('sample_index')} | {sample.get('rows')} | "
            f"{sample.get('unique_keys')} | `{sample.get('last_entry_ts')}` |"
        )
    lines.extend(["", "## Read", ""])
    lines.extend(f"- {item}" for item in report.get("interpretation") or [])
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    report = build_report()
    write_outputs(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
