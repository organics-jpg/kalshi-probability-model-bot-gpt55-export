"""Adverse-future stress test for the p70 FV candidate.

Research-only; no live bot changes or orders.

The p70 diagnostic looks clean because all adjusted rows have improved
calibration so far. This probe measures how fragile that result is by adding
hypothetical future p70-adjusted losses and recalculating paired deltas versus
raw. It does not replace forward validation; it tells us how nervous to be.
"""
from __future__ import annotations

import json
import math
import random
from pathlib import Path
from typing import Any

from probe_v28_target_coverage_p70_sequential_evidence import (
    BOOTSTRAP_RUNS,
    raw_probability,
    p70_probability,
)


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
TARGET_JSON = OUT_DIR / "v28_target_coverage_fv_overlay_validator_latest.json"
OUT_JSON = OUT_DIR / "v28_target_coverage_p70_fragility_stress_latest.json"
OUT_MD = OUT_DIR / "v28_target_coverage_p70_fragility_stress_latest.md"

BOOTSTRAP_SEED = 28747
ADVERSE_RAW_PROBS = [0.70, 0.75, 0.80, 0.85, 0.90]
MAX_ADVERSE_ROWS = 8


def load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
    return payload if isinstance(payload, dict) else {}


def clamp_prob(value: float) -> float:
    return max(0.000001, min(0.999999, value))


def logloss(p: float, outcome: float) -> float:
    p = clamp_prob(p)
    return -(outcome * math.log(p) + (1.0 - outcome) * math.log(1.0 - p))


def percentile(sorted_values: list[float], q: float) -> float | None:
    if not sorted_values:
        return None
    idx = min(len(sorted_values) - 1, max(0, int(round((len(sorted_values) - 1) * q))))
    return sorted_values[idx]


def bootstrap(values: list[float], seed_offset: int) -> dict[str, Any]:
    if len(values) < 5:
        return {"runs": 0, "p05": None, "p50": None, "p95": None, "prob_negative": None}
    rng = random.Random(BOOTSTRAP_SEED + seed_offset + len(values))
    samples = []
    for _ in range(BOOTSTRAP_RUNS):
        samples.append(sum(rng.choice(values) for _ in values) / len(values))
    samples.sort()
    return {
        "runs": BOOTSTRAP_RUNS,
        "p05": percentile(samples, 0.05),
        "p50": percentile(samples, 0.50),
        "p95": percentile(samples, 0.95),
        "prob_negative": sum(1 for value in samples if value < 0.0) / len(samples),
    }


def paired_deltas() -> list[dict[str, Any]]:
    target = load_json(TARGET_JSON)
    rows = target.get("forward_rows") if isinstance(target.get("forward_rows"), list) else []
    out = []
    for row in rows:
        if row.get("side_won") is None:
            continue
        try:
            p_raw = raw_probability(row)
            p_p70 = p70_probability(row)
        except (TypeError, ValueError):
            continue
        outcome = 1.0 if row.get("side_won") is True else 0.0
        out.append({
            "market": row.get("market"),
            "p_raw": p_raw,
            "p_p70": p_p70,
            "outcome": outcome,
            "adjusted": abs(p_p70 - p_raw) > 1e-9,
            "brier_delta": (p_p70 - outcome) ** 2 - (p_raw - outcome) ** 2,
            "logloss_delta": logloss(p_p70, outcome) - logloss(p_raw, outcome),
        })
    return out


def adverse_delta(raw_p: float) -> dict[str, float]:
    row = {"p_raw": raw_p}
    p_raw = raw_probability(row)
    p_p70 = p70_probability(row)
    outcome = 0.0
    return {
        "raw_p": raw_p,
        "p_p70": p_p70,
        "brier_delta": (p_p70 - outcome) ** 2 - (p_raw - outcome) ** 2,
        "logloss_delta": logloss(p_p70, outcome) - logloss(p_raw, outcome),
    }


def summarize(values: list[float], seed_offset: int) -> dict[str, Any]:
    boot = bootstrap(values, seed_offset)
    return {
        "rows": len(values),
        "mean": sum(values) / len(values) if values else None,
        "p95": boot.get("p95"),
        "prob_negative": boot.get("prob_negative"),
    }


def build_report() -> dict[str, Any]:
    base = paired_deltas()
    base_briers = [float(row["brier_delta"]) for row in base]
    base_losses = [float(row["logloss_delta"]) for row in base]
    scenarios = []
    for raw_p in ADVERSE_RAW_PROBS:
        adverse = adverse_delta(raw_p)
        for count in range(1, MAX_ADVERSE_ROWS + 1):
            briers = base_briers + [float(adverse["brier_delta"])] * count
            losses = base_losses + [float(adverse["logloss_delta"])] * count
            b_summary = summarize(briers, int(raw_p * 1000) + count)
            l_summary = summarize(losses, int(raw_p * 2000) + count)
            scenarios.append({
                "adverse_raw_p": raw_p,
                "adverse_p70": adverse["p_p70"],
                "adverse_count": count,
                "total_rows": len(briers),
                "brier_mean_delta": b_summary["mean"],
                "brier_p95": b_summary["p95"],
                "brier_prob_negative": b_summary["prob_negative"],
                "logloss_mean_delta": l_summary["mean"],
                "logloss_p95": l_summary["p95"],
                "logloss_prob_negative": l_summary["prob_negative"],
                "still_mean_better": (b_summary["mean"] is not None and b_summary["mean"] < 0.0 and l_summary["mean"] is not None and l_summary["mean"] < 0.0),
                "still_interval_better": (b_summary["p95"] is not None and b_summary["p95"] < 0.0 and l_summary["p95"] is not None and l_summary["p95"] < 0.0),
            })
    first_breaks = {}
    for raw_p in ADVERSE_RAW_PROBS:
        rows = [row for row in scenarios if row["adverse_raw_p"] == raw_p]
        first_mean_break = next((row for row in rows if not row["still_mean_better"]), None)
        first_interval_break = next((row for row in rows if not row["still_interval_better"]), None)
        first_breaks[str(raw_p)] = {
            "first_mean_break_count": None if first_mean_break is None else first_mean_break["adverse_count"],
            "first_interval_break_count": None if first_interval_break is None else first_interval_break["adverse_count"],
        }
    return {
        "base_rows": len(base),
        "base_adjusted_rows": sum(1 for row in base if row.get("adjusted")),
        "base_brier": summarize(base_briers, 0),
        "base_logloss": summarize(base_losses, 1),
        "adverse_raw_probs": ADVERSE_RAW_PROBS,
        "first_breaks": first_breaks,
        "scenarios": scenarios,
        "interpretation": interpretation(first_breaks),
    }


def interpretation(first_breaks: dict[str, Any]) -> list[str]:
    notes = [
        "This is a pessimistic counterfactual, not live evidence: it appends hypothetical high-confidence losses to the current row set.",
        "If one or two adverse rows break interval evidence, p70 should remain watched only; if it survives several, the diagnostic edge is less fragile.",
    ]
    for raw_p, row in first_breaks.items():
        notes.append(
            f"At raw p={raw_p}, first mean break count={row.get('first_mean_break_count')}, first interval break count={row.get('first_interval_break_count')}."
        )
    return notes


def fmt(value: Any) -> str:
    if value is None:
        return "None"
    if isinstance(value, float):
        return f"{value:.6f}"
    return str(value)


def write_md(report: dict[str, Any]) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8")
    lines = [
        "# v28 Target-Coverage p70 Fragility Stress",
        "",
        f"- Base rows/adjusted rows: `{report.get('base_rows')}/{report.get('base_adjusted_rows')}`",
        f"- Base Brier mean/p95/prob-negative: `{fmt((report.get('base_brier') or {}).get('mean'))}/{fmt((report.get('base_brier') or {}).get('p95'))}/{fmt((report.get('base_brier') or {}).get('prob_negative'))}`",
        f"- Base logloss mean/p95/prob-negative: `{fmt((report.get('base_logloss') or {}).get('mean'))}/{fmt((report.get('base_logloss') or {}).get('p95'))}/{fmt((report.get('base_logloss') or {}).get('prob_negative'))}`",
        "",
        "## Current Read",
        "",
    ]
    for note in report.get("interpretation") or []:
        lines.append(f"- {note}")
    lines.extend([
        "",
        "## Adverse Scenarios",
        "",
        "| raw p | p70 p | adverse count | total rows | brier mean | brier p95 | logloss mean | logloss p95 | interval survives |",
        "|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ])
    for row in report.get("scenarios") or []:
        lines.append(
            f"| {fmt(row.get('adverse_raw_p'))} | {fmt(row.get('adverse_p70'))} | {row.get('adverse_count')} | "
            f"{row.get('total_rows')} | {fmt(row.get('brier_mean_delta'))} | {fmt(row.get('brier_p95'))} | "
            f"{fmt(row.get('logloss_mean_delta'))} | {fmt(row.get('logloss_p95'))} | {row.get('still_interval_better')} |"
        )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    report = build_report()
    write_md(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
