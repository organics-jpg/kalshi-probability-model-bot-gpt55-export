"""Research-only fresh validation requirement calculator.

Summarizes how much post-lock interval evidence is still required before any
locked interval candidate can support the 95% realized-accuracy / 80%
recurring-market coverage goal with a Wilson lower-bound check.

No orders are submitted and no bot files are modified.
"""
from __future__ import annotations

import json
import math
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

import pandas as pd

from probe_interval_policy_degeneracy_audit import wilson_lower
from probe_market_interval_80coverage import OUT_DIR, TARGET_ACCURACY, MARKET_COVERAGE_FLOOR, clean_json, pct


SOURCES = [
    ("locked_interval_candidates", OUT_DIR / "locked_interval_candidates_latest.json"),
    ("locked_interval_pure_physics", OUT_DIR / "locked_interval_pure_physics_latest.json"),
    ("locked_interval_logit", OUT_DIR / "locked_interval_logit_latest.json"),
]


def clean_json_local(value: Any) -> Any:
    if isinstance(value, pd.Timestamp):
        return value.isoformat()
    if isinstance(value, dict):
        return {str(k): clean_json_local(v) for k, v in value.items()}
    if isinstance(value, list):
        return [clean_json_local(v) for v in value]
    return clean_json(value)


def min_total_successes_for_wilson(target: float = TARGET_ACCURACY) -> int:
    n = 1
    while wilson_lower(n, n) < target:
        n += 1
    return n


def additional_perfect_wins_needed(wins: int, losses: int, target: float = TARGET_ACCURACY) -> Optional[int]:
    if losses > 0:
        # With one or more losses, eventually the observed rate can approach 1.0,
        # but this keeps the report conservative and local to the current sample.
        n = wins + losses
        add = 0
        while add <= 10000:
            total = n + add
            if total and (wins + add) / total >= target and wilson_lower(wins + add, total) >= target:
                return add
            add += 1
        return None
    required = min_total_successes_for_wilson(target)
    return max(0, required - wins)


def load_rows() -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    for source_name, path in SOURCES:
        if not path.exists():
            continue
        payload = json.loads(path.read_text(encoding="utf-8"))
        if source_name in {"locked_interval_candidates", "locked_interval_pure_physics"}:
            for summary in payload.get("summaries", []):
                fresh = summary.get("metrics", {}).get("fresh", {})
                rows.append(row_from_metric(source_name, summary.get("name", "unknown"), fresh))
        elif source_name == "locked_interval_logit":
            fresh = payload.get("metrics", {}).get("fresh", {})
            candidate = payload.get("lock", {}).get("candidate", {}).get("name", "locked_logit")
            rows.append(row_from_metric(source_name, candidate, fresh))
    return rows


def row_from_metric(source: str, candidate: str, fresh: Dict[str, Any]) -> Dict[str, Any]:
    base = int(fresh.get("base_markets") or 0)
    markets = int(fresh.get("markets") or 0)
    wins = int(fresh.get("wins") or 0)
    losses = int(fresh.get("losses") or 0)
    acc = wins / markets if markets else None
    coverage = markets / base if base else None
    lower = wilson_lower(wins, markets)
    add_wins = additional_perfect_wins_needed(wins, losses)
    return {
        "source": source,
        "candidate": candidate,
        "fresh_base_markets": base,
        "fresh_selected_markets": markets,
        "fresh_wins": wins,
        "fresh_losses": losses,
        "fresh_accuracy": acc,
        "fresh_coverage": coverage,
        "fresh_wilson95_lower": lower,
        "additional_perfect_wins_for_wilson95": add_wins,
        "coverage_gate_now": coverage is not None and coverage >= MARKET_COVERAGE_FLOOR,
        "accuracy_gate_now": acc is not None and acc >= TARGET_ACCURACY,
        "wilson_gate_now": lower is not None and lower >= TARGET_ACCURACY,
    }


def fmt_int(value: Optional[int]) -> str:
    return "NA" if value is None else str(value)


def write_report(path: Path, generated: str, rows: List[Dict[str, Any]]) -> None:
    lines = [
        "# Interval Fresh Validation Requirements",
        "",
        f"Generated UTC: `{generated}`",
        "",
        "## Scope",
        "",
        "- Research-only report; no orders are submitted and no bot files are modified.",
        "- Reads locked interval monitor outputs and quantifies post-lock sample-size gaps.",
        "- Wilson lower-bound target is 95% realized accuracy.",
        "",
        "## Requirement",
        "",
        f"- With zero fresh losses, a candidate needs {min_total_successes_for_wilson()} selected fresh wins for a 95% Wilson lower bound at 100% observed accuracy.",
        "- The candidate must also select at least 80% of fresh recurring market intervals.",
        "",
        "## Locked Candidate Fresh State",
        "",
        "| source | candidate | fresh markets | acc | coverage | Wilson low | extra perfect wins needed |",
        "|---|---|---:|---:|---:|---:|---:|",
    ]
    for row in rows:
        lines.append(
            f"| `{row['source']}` | `{row['candidate']}` | "
            f"{row['fresh_selected_markets']}/{row['fresh_base_markets']} | "
            f"{pct(row['fresh_accuracy'])} | {pct(row['fresh_coverage'])} | "
            f"{pct(row['fresh_wilson95_lower'])} | {fmt_int(row['additional_perfect_wins_for_wilson95'])} |"
        )
    lines += ["", "## Read", ""]
    if not rows:
        lines.append("No locked monitor rows were available.")
    else:
        best = min(
            (row for row in rows if row["additional_perfect_wins_for_wilson95"] is not None),
            key=lambda row: row["additional_perfect_wins_for_wilson95"],
            default=None,
        )
        if best:
            lines.append(
                f"- Closest locked candidate still needs {best['additional_perfect_wins_for_wilson95']} additional perfect selected fresh wins for the Wilson gate."
            )
        lines.append("- Current post-lock evidence is monitoring evidence only; it cannot complete the live sample-size requirement.")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    generated = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%SZ")
    rows = load_rows()
    df = pd.DataFrame(rows)
    csv_latest = OUT_DIR / "interval_fresh_validation_requirements_latest.csv"
    csv_stamp = OUT_DIR / f"interval_fresh_validation_requirements_{generated}.csv"
    md_latest = OUT_DIR / "interval_fresh_validation_requirements_latest.md"
    md_stamp = OUT_DIR / f"interval_fresh_validation_requirements_{generated}.md"
    json_latest = OUT_DIR / "interval_fresh_validation_requirements_latest.json"
    json_stamp = OUT_DIR / f"interval_fresh_validation_requirements_{generated}.json"

    df.to_csv(csv_latest, index=False)
    df.to_csv(csv_stamp, index=False)
    write_report(md_latest, generated, rows)
    write_report(md_stamp, generated, rows)
    payload = {
        "generated_utc": generated,
        "min_total_successes_for_wilson95": min_total_successes_for_wilson(),
        "rows": rows,
    }
    for path in [json_latest, json_stamp]:
        path.write_text(json.dumps(clean_json_local(payload), indent=2, sort_keys=True), encoding="utf-8")
    print("Interval fresh validation requirements complete")
    print(f"rows={len(rows)} min_total_successes={min_total_successes_for_wilson()}")
    print(f"report={md_latest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
