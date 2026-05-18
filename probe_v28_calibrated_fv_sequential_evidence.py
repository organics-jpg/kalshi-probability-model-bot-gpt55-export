"""Sequential forward evidence for the v28 calibrated FV overlay.

Each settled forward selected row gives a paired comparison:
    (+5pp probability score) - (raw probability score)
for Brier and logloss. Negative deltas mean +5pp is better.

This monitor is deliberately conservative: with tiny samples it says
inconclusive, even if early rows look good.

Research-only; no live bot changes or orders.
"""
from __future__ import annotations

import json
import random
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
MONITOR_JSON = OUT_DIR / "v28_calibrated_fv_forward_monitor_latest.json"
OUT_JSON = OUT_DIR / "v28_calibrated_fv_sequential_evidence_latest.json"
OUT_MD = OUT_DIR / "v28_calibrated_fv_sequential_evidence_latest.md"

BOOTSTRAP_RUNS = 5000
BOOTSTRAP_SEED = 28095
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
        return float(value)
    except (TypeError, ValueError):
        return None


def percentile(sorted_values: list[float], q: float) -> float | None:
    if not sorted_values:
        return None
    idx = min(len(sorted_values) - 1, max(0, int(round((len(sorted_values) - 1) * q))))
    return sorted_values[idx]


def bootstrap_mean_interval(values: list[float]) -> dict[str, Any]:
    if len(values) < MIN_ROWS_FOR_INTERVAL:
        return {"runs": 0, "p05": None, "p50": None, "p95": None, "prob_negative": None}
    rng = random.Random(BOOTSTRAP_SEED + len(values))
    samples: list[float] = []
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


def build_report() -> dict[str, Any]:
    monitor = load_json(MONITOR_JSON)
    details = monitor.get("clean_details") if isinstance(monitor.get("clean_details"), list) else []
    rows: list[dict[str, Any]] = []
    for item in details:
        selected = item.get("selected_row") or {}
        if selected.get("side_won") is None:
            continue
        brier_delta = as_float(selected.get("brier_delta_plus05_minus_raw"))
        logloss_delta = as_float(selected.get("logloss_delta_plus05_minus_raw"))
        if brier_delta is None or logloss_delta is None:
            continue
        rows.append({
            "market": item.get("market"),
            "side": selected.get("side"),
            "side_won": selected.get("side_won"),
            "net_cents": selected.get("net_gross_cents_after_entry_fee"),
            "p_raw": selected.get("p_raw"),
            "p_plus05": selected.get("p_plus05"),
            "ask_prob": selected.get("ask_prob"),
            "brier_delta": brier_delta,
            "logloss_delta": logloss_delta,
        })
    brier_deltas = [float(row["brier_delta"]) for row in rows]
    logloss_deltas = [float(row["logloss_delta"]) for row in rows]
    n = len(rows)
    brier_mean = sum(brier_deltas) / n if n else None
    logloss_mean = sum(logloss_deltas) / n if n else None
    brier_boot = bootstrap_mean_interval(brier_deltas)
    logloss_boot = bootstrap_mean_interval(logloss_deltas)
    blockers: list[str] = []
    if n < MIN_ROWS_FOR_USEFUL:
        blockers.append(f"settled_lt_{MIN_ROWS_FOR_USEFUL}")
    if n >= MIN_ROWS_FOR_INTERVAL:
        if brier_boot.get("p95") is None or float(brier_boot["p95"]) >= 0.0:
            blockers.append("brier_interval_not_strictly_negative")
        if logloss_boot.get("p95") is None or float(logloss_boot["p95"]) >= 0.0:
            blockers.append("logloss_interval_not_strictly_negative")
    else:
        blockers.append(f"interval_sample_lt_{MIN_ROWS_FOR_INTERVAL}")
    if brier_mean is None or brier_mean >= 0.0:
        blockers.append("mean_brier_delta_not_negative")
    if logloss_mean is None or logloss_mean >= 0.0:
        blockers.append("mean_logloss_delta_not_negative")
    return {
        "candidate": "v28_raw_entry_conditioned_plus05_fv",
        "settled_rows": n,
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
        "rows": rows,
        "evidence_status": "useful" if not blockers else "inconclusive_or_blocked",
        "blockers": blockers,
        "interpretation": "Negative paired deltas mean +5pp improves calibration versus raw on the same selected row.",
    }


def fmt(value: Any) -> str:
    if value is None:
        return "None"
    if isinstance(value, float):
        return f"{value:.6f}"
    return str(value)


def write_report(report: dict[str, Any]) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8")
    brier = report["brier"]
    logloss = report["logloss"]
    lines = [
        "# v28 Calibrated FV Sequential Evidence",
        "",
        "Paired forward evidence for +5pp FV versus raw FV on the same selected rows.",
        "",
        f"- Candidate: `{report['candidate']}`",
        f"- Settled rows: `{report['settled_rows']}`",
        f"- Evidence status: `{report['evidence_status']}`",
        f"- Blockers: `{', '.join(report['blockers']) or 'none'}`",
        "",
        "## Paired Deltas",
        "",
        f"- Brier mean delta: `{fmt(brier['mean_delta'])}`; negative/positive `{brier['negative_count']}/{brier['positive_count']}`",
        f"- Brier bootstrap p05/p50/p95/prob_negative: `{fmt(brier['bootstrap']['p05'])}/{fmt(brier['bootstrap']['p50'])}/{fmt(brier['bootstrap']['p95'])}/{fmt(brier['bootstrap']['prob_negative'])}`",
        f"- Logloss mean delta: `{fmt(logloss['mean_delta'])}`; negative/positive `{logloss['negative_count']}/{logloss['positive_count']}`",
        f"- Logloss bootstrap p05/p50/p95/prob_negative: `{fmt(logloss['bootstrap']['p05'])}/{fmt(logloss['bootstrap']['p50'])}/{fmt(logloss['bootstrap']['p95'])}/{fmt(logloss['bootstrap']['prob_negative'])}`",
        "",
        "## Settled Rows",
        "",
        "| market | side | won | p raw | p +5 | ask | net c | brier d | logloss d |",
        "|---|---|---|---:|---:|---:|---:|---:|---:|",
    ]
    for row in report["rows"]:
        lines.append(
            f"| {row['market']} | {row['side']} | {row['side_won']} | {fmt(row['p_raw'])} | "
            f"{fmt(row['p_plus05'])} | {fmt(row['ask_prob'])} | {fmt(row['net_cents'])} | "
            f"{fmt(row['brier_delta'])} | {fmt(row['logloss_delta'])} |"
        )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    report = build_report()
    write_report(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
