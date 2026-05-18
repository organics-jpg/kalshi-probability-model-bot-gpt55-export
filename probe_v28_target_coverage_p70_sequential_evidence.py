"""Sequential evidence for the p70 target-coverage FV candidate.

Research-only; no live bot changes or orders.

The broad target-coverage overlay still tracks the older p60 sharpening row.
This probe freezes the current diagnostic question more tightly: does sharpening
only raw-v28 probabilities >= 0.70 improve calibration versus raw on the same
target-coverage selected rows?
"""
from __future__ import annotations

import json
import math
import random
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
TARGET_JSON = OUT_DIR / "v28_target_coverage_fv_overlay_validator_latest.json"
OUT_JSON = OUT_DIR / "v28_target_coverage_p70_sequential_evidence_latest.json"
OUT_MD = OUT_DIR / "v28_target_coverage_p70_sequential_evidence_latest.md"

BOOTSTRAP_RUNS = 5000
BOOTSTRAP_SEED = 28703
MIN_ROWS_FOR_INTERVAL = 5
MIN_ROWS_FOR_USEFUL = 30
VARIANT = "logit125_p70"


def load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
    return payload if isinstance(payload, dict) else {}


def as_float(value: Any) -> float | None:
    if value is None or value == "":
        return None
    try:
        out = float(value)
    except (TypeError, ValueError):
        return None
    return out if math.isfinite(out) else None


def clamp_prob(value: float) -> float:
    return max(0.000001, min(0.999999, value))


def logit(p: float) -> float:
    p = clamp_prob(p)
    return math.log(p / (1.0 - p))


def inv_logit(x: float) -> float:
    return 1.0 / (1.0 + math.exp(-x))


def sharpen(p: float) -> float:
    return clamp_prob(inv_logit(1.25 * logit(p)))


def logloss(p: float, outcome: float) -> float:
    p = clamp_prob(p)
    return -(outcome * math.log(p) + (1.0 - outcome) * math.log(1.0 - p))


def raw_probability(row: dict[str, Any]) -> float:
    value = as_float(row.get("p_raw") if row.get("p_raw") is not None else row.get("p_side"))
    if value is None:
        raise ValueError("missing raw probability")
    return clamp_prob(value)


def p70_probability(row: dict[str, Any]) -> float:
    p = raw_probability(row)
    return sharpen(p) if p >= 0.70 else p


def percentile(sorted_values: list[float], q: float) -> float | None:
    if not sorted_values:
        return None
    idx = min(len(sorted_values) - 1, max(0, int(round((len(sorted_values) - 1) * q))))
    return sorted_values[idx]


def bootstrap_mean_interval(values: list[float]) -> dict[str, Any]:
    if len(values) < MIN_ROWS_FOR_INTERVAL:
        return {"runs": 0, "p05": None, "p50": None, "p95": None, "prob_negative": None}
    rng = random.Random(BOOTSTRAP_SEED + len(values))
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


def score_row(row: dict[str, Any]) -> dict[str, Any] | None:
    if row.get("side_won") is None:
        return None
    try:
        p_raw = raw_probability(row)
        p_variant = p70_probability(row)
    except (TypeError, ValueError):
        return None
    outcome = 1.0 if row.get("side_won") is True else 0.0
    adjusted = abs(p_variant - p_raw) > 0.0000001
    return {
        "market": row.get("market"),
        "side": row.get("side"),
        "side_won": row.get("side_won"),
        "net_cents": row.get("net_gross_cents_after_entry_fee"),
        "p_raw": p_raw,
        "p_variant": p_variant,
        "adjusted": adjusted,
        "ask_prob": row.get("ask_prob"),
        "raw_edge_prob": row.get("raw_edge_prob"),
        "recross_hazard_score": row.get("recross_hazard_score"),
        "reason": row.get("coverage_valve_reason"),
        "brier_delta": (p_variant - outcome) ** 2 - (p_raw - outcome) ** 2,
        "logloss_delta": logloss(p_variant, outcome) - logloss(p_raw, outcome),
    }


def build_report() -> dict[str, Any]:
    target = load_json(TARGET_JSON)
    rows = target.get("forward_rows") if isinstance(target.get("forward_rows"), list) else []
    scored = [score_row(row) for row in rows]
    scored = [row for row in scored if row is not None]
    brier_deltas = [float(row["brier_delta"]) for row in scored]
    logloss_deltas = [float(row["logloss_delta"]) for row in scored]
    brier_boot = bootstrap_mean_interval(brier_deltas)
    logloss_boot = bootstrap_mean_interval(logloss_deltas)
    target_forward = target.get("forward") if isinstance(target.get("forward"), list) else []
    raw_row = next((row for row in target_forward if row.get("overlay") == "raw_probability"), {})
    coverage = as_float(raw_row.get("coverage_pct"))
    blockers: list[str] = []
    if len(scored) < MIN_ROWS_FOR_USEFUL:
        blockers.append(f"settled_lt_{MIN_ROWS_FOR_USEFUL}")
    if len(scored) < MIN_ROWS_FOR_INTERVAL:
        blockers.append(f"interval_sample_lt_{MIN_ROWS_FOR_INTERVAL}")
    else:
        if brier_boot.get("p95") is None or float(brier_boot["p95"]) >= 0.0:
            blockers.append("brier_interval_not_strictly_negative")
        if logloss_boot.get("p95") is None or float(logloss_boot["p95"]) >= 0.0:
            blockers.append("logloss_interval_not_strictly_negative")
    brier_mean = sum(brier_deltas) / len(brier_deltas) if brier_deltas else None
    logloss_mean = sum(logloss_deltas) / len(logloss_deltas) if logloss_deltas else None
    if brier_mean is None or brier_mean >= 0.0:
        blockers.append("mean_brier_delta_not_negative")
    if logloss_mean is None or logloss_mean >= 0.0:
        blockers.append("mean_logloss_delta_not_negative")
    if coverage is None or coverage < 75.0:
        blockers.append("coverage_below_75")
    if coverage is not None and coverage > 90.0:
        blockers.append("coverage_above_90")
    return {
        "source": str(TARGET_JSON),
        "policy": target.get("policy"),
        "variant": VARIANT,
        "forward_denominator": target.get("forward_denominator"),
        "entries": raw_row.get("entries") or len(rows),
        "settled_rows": len(scored),
        "adjusted_rows": sum(1 for row in scored if row.get("adjusted")),
        "coverage_pct": raw_row.get("coverage_pct"),
        "wins": sum(1 for row in scored if row.get("side_won") is True),
        "losses": sum(1 for row in scored if row.get("side_won") is False),
        "net_cents_after_entry_fee": sum(float(row.get("net_cents") or 0.0) for row in scored),
        "brier": {
            "mean_delta": brier_mean,
            "negative_count": sum(1 for value in brier_deltas if value < 0.0),
            "positive_count": sum(1 for value in brier_deltas if value > 0.0),
            "zero_count": sum(1 for value in brier_deltas if value == 0.0),
            "bootstrap": brier_boot,
        },
        "logloss": {
            "mean_delta": logloss_mean,
            "negative_count": sum(1 for value in logloss_deltas if value < 0.0),
            "positive_count": sum(1 for value in logloss_deltas if value > 0.0),
            "zero_count": sum(1 for value in logloss_deltas if value == 0.0),
            "bootstrap": logloss_boot,
        },
        "settled_rows_to_30": max(0, MIN_ROWS_FOR_USEFUL - len(scored)),
        "evidence_status": "useful" if not blockers else "inconclusive_or_blocked",
        "blockers": blockers,
        "rows": scored,
        "interpretation": [
            "p70 is a conservative selective-memory FV: keep boundary/mid-confidence probabilities unchanged, sharpen only stronger raw signals.",
            "This is diagnostic evidence on the current target-coverage surface; frozen post-declaration rows still control promotion.",
        ],
    }


def fmt(value: Any) -> str:
    if value is None:
        return "None"
    if isinstance(value, float):
        return f"{value:.6f}"
    return str(value)


def write_md(report: dict[str, Any]) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8")
    brier = report["brier"]
    logloss_report = report["logloss"]
    lines = [
        "# v28 Target-Coverage p70 Sequential Evidence",
        "",
        "Paired evidence for `logit125_p70` versus raw FV on the same target-coverage selected rows.",
        "",
        f"- Policy: `{report.get('policy')}`",
        f"- Variant: `{report.get('variant')}`",
        f"- Entries/settled/adjusted/coverage: `{report.get('entries')}/{report.get('settled_rows')}/{report.get('adjusted_rows')}/{fmt(report.get('coverage_pct'))}`",
        f"- W/L/net: `{report.get('wins')}/{report.get('losses')}/{fmt(report.get('net_cents_after_entry_fee'))}c`",
        f"- Evidence status: `{report.get('evidence_status')}`",
        f"- Blockers: `{', '.join(report.get('blockers') or []) or 'none'}`",
        f"- Settled rows still needed for 30: `{report.get('settled_rows_to_30')}`",
        "",
        "## Current Read",
        "",
    ]
    for note in report.get("interpretation") or []:
        lines.append(f"- {note}")
    lines.extend([
        "",
        "## Paired Deltas",
        "",
        f"- Brier mean delta: `{fmt(brier.get('mean_delta'))}`; negative/positive/zero `{brier.get('negative_count')}/{brier.get('positive_count')}/{brier.get('zero_count')}`",
        f"- Brier bootstrap p05/p50/p95/prob_negative: `{fmt(brier['bootstrap']['p05'])}/{fmt(brier['bootstrap']['p50'])}/{fmt(brier['bootstrap']['p95'])}/{fmt(brier['bootstrap']['prob_negative'])}`",
        f"- Logloss mean delta: `{fmt(logloss_report.get('mean_delta'))}`; negative/positive/zero `{logloss_report.get('negative_count')}/{logloss_report.get('positive_count')}/{logloss_report.get('zero_count')}`",
        f"- Logloss bootstrap p05/p50/p95/prob_negative: `{fmt(logloss_report['bootstrap']['p05'])}/{fmt(logloss_report['bootstrap']['p50'])}/{fmt(logloss_report['bootstrap']['p95'])}/{fmt(logloss_report['bootstrap']['prob_negative'])}`",
        "",
        "## Settled Rows",
        "",
        "| market | side | won | p raw | p p70 | adjusted | ask | edge | recross | reason | net c | brier d | logloss d |",
        "|---|---|---|---:|---:|---:|---:|---:|---:|---|---:|---:|---:|",
    ])
    for row in report.get("rows") or []:
        lines.append(
            f"| {row.get('market')} | {row.get('side')} | {row.get('side_won')} | "
            f"{fmt(row.get('p_raw'))} | {fmt(row.get('p_variant'))} | {row.get('adjusted')} | "
            f"{fmt(row.get('ask_prob'))} | {fmt(row.get('raw_edge_prob'))} | {fmt(row.get('recross_hazard_score'))} | "
            f"{row.get('reason')} | {fmt(row.get('net_cents'))} | {fmt(row.get('brier_delta'))} | {fmt(row.get('logloss_delta'))} |"
        )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    report = build_report()
    write_md(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
