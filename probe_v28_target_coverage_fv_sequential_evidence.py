"""Sequential evidence for target-coverage FV overlays.

Research-only; no live bot changes or orders.

This consumes the target-coverage FV validator and asks whether the current
best overlay is actually improving calibration versus raw on the same selected
rows. The target-coverage surface matters because it is closest to the user's
75-80%+ market participation goal.
"""
from __future__ import annotations

import json
import math
import random
from pathlib import Path
from typing import Any, Callable

from probe_v28_raw_entry_calibrated_probability import OVERLAYS
from probe_v28_target_coverage_fv_overlay_validator import boundary_recross_shrink_probability


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
TARGET_JSON = OUT_DIR / "v28_target_coverage_fv_overlay_validator_latest.json"
OUT_JSON = OUT_DIR / "v28_target_coverage_fv_sequential_evidence_latest.json"
OUT_MD = OUT_DIR / "v28_target_coverage_fv_sequential_evidence_latest.md"

BOOTSTRAP_RUNS = 5000
BOOTSTRAP_SEED = 28611
MIN_ROWS_FOR_INTERVAL = 5
MIN_ROWS_FOR_USEFUL = 30


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


def logloss(p: float, outcome: float) -> float:
    p = clamp_prob(p)
    return -(outcome * math.log(p) + (1.0 - outcome) * math.log(1.0 - p))


def danger_to_book_probability(row: dict[str, Any]) -> float:
    raw = as_float(row.get("p_side") if row.get("p_side") is not None else row.get("p_raw"))
    book = as_float(row.get("ask_prob"))
    if book is None and row.get("ask_cents") is not None:
        ask_cents = as_float(row.get("ask_cents"))
        book = None if ask_cents is None else ask_cents / 100.0
    if raw is None:
        raise ValueError("missing raw probability")
    if book is None:
        return raw
    if raw - book > 0.30:
        return book
    return raw


LOCAL_OVERLAYS: dict[str, Callable[[dict[str, Any]], float]] = {
    **OVERLAYS,
    "danger_to_book_probability": danger_to_book_probability,
    "boundary_recross_shrink_probability": boundary_recross_shrink_probability,
}


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
        total = 0.0
        for _ in values:
            total += rng.choice(values)
        samples.append(total / len(values))
    samples.sort()
    return {
        "runs": BOOTSTRAP_RUNS,
        "p05": percentile(samples, 0.05),
        "p50": percentile(samples, 0.50),
        "p95": percentile(samples, 0.95),
        "prob_negative": sum(1 for value in samples if value < 0.0) / len(samples),
    }


def score_row(row: dict[str, Any], overlay_fn: Callable[[dict[str, Any]], float]) -> dict[str, Any] | None:
    if row.get("side_won") is None:
        return None
    source_row = dict(row)
    if "p_side" not in source_row and source_row.get("p_raw") is not None:
        source_row["p_side"] = source_row.get("p_raw")
    raw_fn = OVERLAYS["raw_probability"]
    try:
        p_raw = clamp_prob(float(raw_fn(source_row)))
        p_overlay = clamp_prob(float(overlay_fn(source_row)))
    except (KeyError, TypeError, ValueError):
        return None
    outcome = 1.0 if row.get("side_won") is True else 0.0
    return {
        "market": row.get("market"),
        "side": row.get("side"),
        "side_won": row.get("side_won"),
        "net_cents": row.get("net_gross_cents_after_entry_fee"),
        "p_raw": p_raw,
        "p_overlay": p_overlay,
        "ask_prob": row.get("ask_prob"),
        "raw_edge_prob": row.get("raw_edge_prob"),
        "reason": row.get("coverage_valve_reason"),
        "brier_delta": (p_overlay - outcome) ** 2 - (p_raw - outcome) ** 2,
        "logloss_delta": logloss(p_overlay, outcome) - logloss(p_raw, outcome),
    }


def build_report() -> dict[str, Any]:
    target = load_json(TARGET_JSON)
    ranked = target.get("forward") if isinstance(target.get("forward"), list) else []
    best = next((row for row in ranked if row.get("overlay") != "raw_probability"), ranked[0] if ranked else {})
    overlay_name = str(best.get("overlay") or "")
    overlay_fn = LOCAL_OVERLAYS.get(overlay_name)
    rows = target.get("forward_rows") if isinstance(target.get("forward_rows"), list) else []
    scored = [score_row(row, overlay_fn) for row in rows] if overlay_fn else []
    scored = [row for row in scored if row is not None]
    brier_deltas = [float(row["brier_delta"]) for row in scored]
    logloss_deltas = [float(row["logloss_delta"]) for row in scored]
    brier_mean = sum(brier_deltas) / len(brier_deltas) if brier_deltas else None
    logloss_mean = sum(logloss_deltas) / len(logloss_deltas) if logloss_deltas else None
    brier_boot = bootstrap_mean_interval(brier_deltas)
    logloss_boot = bootstrap_mean_interval(logloss_deltas)
    coverage = as_float(best.get("coverage_pct"))
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
        "overlay": overlay_name,
        "forward_denominator": target.get("forward_denominator"),
        "entries": best.get("entries"),
        "settled_rows": len(scored),
        "coverage_pct": best.get("coverage_pct"),
        "wins": best.get("wins"),
        "losses": best.get("losses"),
        "net_cents_after_entry_fee": best.get("net_cents_after_entry_fee"),
        "brier": {
            "mean_delta": brier_mean,
            "negative_count": sum(1 for value in brier_deltas if value < 0.0),
            "positive_count": sum(1 for value in brier_deltas if value >= 0.0),
            "bootstrap": brier_boot,
        },
        "logloss": {
            "mean_delta": logloss_mean,
            "negative_count": sum(1 for value in logloss_deltas if value < 0.0),
            "positive_count": sum(1 for value in logloss_deltas if value >= 0.0),
            "bootstrap": logloss_boot,
        },
        "settled_rows_to_30": max(0, MIN_ROWS_FOR_USEFUL - len(scored)),
        "evidence_status": "useful" if not blockers else "inconclusive_or_blocked",
        "blockers": blockers,
        "rows": scored,
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
        "# v28 Target-Coverage FV Sequential Evidence",
        "",
        "Paired evidence for the best target-coverage FV overlay versus raw FV on the same selected rows.",
        "",
        f"- Policy: `{report.get('policy')}`",
        f"- Overlay: `{report.get('overlay')}`",
        f"- Entries/settled/coverage: `{report.get('entries')}/{report.get('settled_rows')}/{fmt(report.get('coverage_pct'))}`",
        f"- W/L/net: `{report.get('wins')}/{report.get('losses')}/{fmt(report.get('net_cents_after_entry_fee'))}c`",
        f"- Evidence status: `{report.get('evidence_status')}`",
        f"- Blockers: `{', '.join(report.get('blockers') or []) or 'none'}`",
        f"- Settled rows still needed for 30: `{report.get('settled_rows_to_30')}`",
        "",
        "## Paired Deltas",
        "",
        f"- Brier mean delta: `{fmt(brier.get('mean_delta'))}`; negative/positive `{brier.get('negative_count')}/{brier.get('positive_count')}`",
        f"- Brier bootstrap p05/p50/p95/prob_negative: `{fmt(brier['bootstrap']['p05'])}/{fmt(brier['bootstrap']['p50'])}/{fmt(brier['bootstrap']['p95'])}/{fmt(brier['bootstrap']['prob_negative'])}`",
        f"- Logloss mean delta: `{fmt(logloss_report.get('mean_delta'))}`; negative/positive `{logloss_report.get('negative_count')}/{logloss_report.get('positive_count')}`",
        f"- Logloss bootstrap p05/p50/p95/prob_negative: `{fmt(logloss_report['bootstrap']['p05'])}/{fmt(logloss_report['bootstrap']['p50'])}/{fmt(logloss_report['bootstrap']['p95'])}/{fmt(logloss_report['bootstrap']['prob_negative'])}`",
        "",
        "## Settled Rows",
        "",
        "| market | side | won | p raw | p overlay | ask | edge | reason | net c | brier d | logloss d |",
        "|---|---|---|---:|---:|---:|---:|---|---:|---:|---:|",
    ]
    for row in report.get("rows") or []:
        lines.append(
            f"| {row.get('market')} | {row.get('side')} | {row.get('side_won')} | "
            f"{fmt(row.get('p_raw'))} | {fmt(row.get('p_overlay'))} | {fmt(row.get('ask_prob'))} | "
            f"{fmt(row.get('raw_edge_prob'))} | {row.get('reason')} | {fmt(row.get('net_cents'))} | "
            f"{fmt(row.get('brier_delta'))} | {fmt(row.get('logloss_delta'))} |"
        )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    report = build_report()
    write_md(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
