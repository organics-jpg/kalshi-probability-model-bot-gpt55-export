"""Bucket reliability for the active target-coverage v28 FV overlay.

Research-only; no live bot changes or orders.

Average Brier can improve while a model remains poorly calibrated in a
particular probability region. This report compares raw FV versus the selected
target-coverage overlay by probability bucket, with simple Wilson intervals
around realized win rates so tiny buckets stay visibly uncertain.
"""
from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any

from probe_v28_target_coverage_fv_overlay_validator import LOCAL_OVERLAYS as OVERLAYS


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
VALIDATOR_JSON = OUT_DIR / "v28_target_coverage_fv_overlay_validator_latest.json"
SEQ_JSON = OUT_DIR / "v28_target_coverage_fv_sequential_evidence_latest.json"
OUT_JSON = OUT_DIR / "v28_target_coverage_fv_bucket_reliability_latest.json"
OUT_MD = OUT_DIR / "v28_target_coverage_fv_bucket_reliability_latest.md"

BUCKETS = [
    (0.50, 0.60, "50_60"),
    (0.60, 0.70, "60_70"),
    (0.70, 0.80, "70_80"),
    (0.80, 0.90, "80_90"),
    (0.90, 1.01, "90_100"),
]
MIN_BUCKET_ROWS = 10
MIN_TOTAL_ROWS = 30


def load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
    return payload if isinstance(payload, dict) else {}


def bucket_label(p: float) -> str:
    for low, high, label in BUCKETS:
        if low <= p < high:
            return label
    return "out_of_range"


def clamp_prob(value: float) -> float:
    return max(0.000001, min(0.999999, value))


def logloss(p: float, outcome: float) -> float:
    p = clamp_prob(p)
    return -(outcome * math.log(p) + (1.0 - outcome) * math.log(1.0 - p))


def normalize_row(row: dict[str, Any]) -> dict[str, Any]:
    out = dict(row)
    if "p_side" not in out and "p_raw" in out:
        out["p_side"] = out.get("p_raw")
    return out


def wilson_interval(wins: int, n: int, z: float = 1.96) -> tuple[float | None, float | None]:
    if n <= 0:
        return None, None
    phat = wins / n
    denom = 1.0 + z * z / n
    center = (phat + z * z / (2.0 * n)) / denom
    margin = z * math.sqrt((phat * (1.0 - phat) + z * z / (4.0 * n)) / n) / denom
    return max(0.0, center - margin), min(1.0, center + margin)


def score_rows(rows: list[dict[str, Any]], overlay_name: str) -> list[dict[str, Any]]:
    scored = []
    overlay_fn = OVERLAYS[overlay_name]
    raw_fn = OVERLAYS["raw_probability"]
    for row in rows:
        if row.get("side_won") is None:
            continue
        norm = normalize_row(row)
        raw_p = clamp_prob(float(raw_fn(norm)))
        p = clamp_prob(float(overlay_fn(norm)))
        outcome = 1.0 if row.get("side_won") is True else 0.0
        scored.append({
            "market": row.get("market"),
            "side": row.get("side"),
            "won": row.get("side_won"),
            "outcome": outcome,
            "p_raw": raw_p,
            "p_overlay": p,
            "raw_bucket": bucket_label(raw_p),
            "overlay_bucket": bucket_label(p),
            "raw_brier": (raw_p - outcome) ** 2,
            "overlay_brier": (p - outcome) ** 2,
            "raw_logloss": logloss(raw_p, outcome),
            "overlay_logloss": logloss(p, outcome),
            "reason": row.get("coverage_valve_reason"),
            "abs_d_sigma": row.get("abs_d_sigma"),
            "recross_hazard_score": row.get("recross_hazard_score"),
        })
    return scored


def summarize(scored: list[dict[str, Any]], p_key: str, bucket_key: str, brier_key: str, logloss_key: str) -> list[dict[str, Any]]:
    out = []
    labels = [label for _, _, label in BUCKETS]
    for label in labels:
        bucket_rows = [row for row in scored if row.get(bucket_key) == label]
        n = len(bucket_rows)
        wins = sum(1 for row in bucket_rows if row.get("won") is True)
        avg_p = sum(float(row[p_key]) for row in bucket_rows) / n if n else None
        win_rate = wins / n if n else None
        low, high = wilson_interval(wins, n)
        calibration_error = None if avg_p is None or win_rate is None else win_rate - avg_p
        out.append({
            "bucket": label,
            "count": n,
            "wins": wins,
            "losses": n - wins,
            "avg_p": avg_p,
            "win_rate": win_rate,
            "wilson_low": low,
            "wilson_high": high,
            "calibration_error": calibration_error,
            "avg_brier": sum(float(row[brier_key]) for row in bucket_rows) / n if n else None,
            "avg_logloss": sum(float(row[logloss_key]) for row in bucket_rows) / n if n else None,
            "bucket_reliable_enough": n >= MIN_BUCKET_ROWS,
        })
    return out


def ece(summary_rows: list[dict[str, Any]], total: int) -> float | None:
    if total <= 0:
        return None
    err = 0.0
    for row in summary_rows:
        count = int(row.get("count") or 0)
        cal = row.get("calibration_error")
        if cal is None:
            continue
        err += count / total * abs(float(cal))
    return err


def build_report() -> dict[str, Any]:
    validator = load_json(VALIDATOR_JSON)
    seq = load_json(SEQ_JSON)
    overlay = str(seq.get("overlay") or "entry_conditioned_logit125_p60_only_probability")
    rows = validator.get("forward_rows") if isinstance(validator.get("forward_rows"), list) else []
    scored = score_rows(rows, overlay)
    raw_summary = summarize(scored, "p_raw", "raw_bucket", "raw_brier", "raw_logloss")
    overlay_summary = summarize(scored, "p_overlay", "overlay_bucket", "overlay_brier", "overlay_logloss")
    total = len(scored)
    raw_ece = ece(raw_summary, total)
    overlay_ece = ece(overlay_summary, total)
    flags = []
    if total < MIN_TOTAL_ROWS:
        flags.append("total_settled_lt_30")
    if any((row.get("count") or 0) > 0 and not row.get("bucket_reliable_enough") for row in overlay_summary):
        flags.append("some_overlay_buckets_lt_10")
    if overlay_ece is not None and raw_ece is not None and overlay_ece > raw_ece:
        flags.append("overlay_ece_worse_than_raw")
    return {
        "policy": validator.get("policy"),
        "overlay": overlay,
        "freeze_ts": validator.get("freeze_ts"),
        "rows": total,
        "raw_ece": raw_ece,
        "overlay_ece": overlay_ece,
        "ece_delta_overlay_minus_raw": None if raw_ece is None or overlay_ece is None else overlay_ece - raw_ece,
        "raw_summary": raw_summary,
        "overlay_summary": overlay_summary,
        "flags": flags,
        "scored_rows": scored,
        "interpretation": interpretation(raw_ece, overlay_ece, flags),
    }


def interpretation(raw_ece: float | None, overlay_ece: float | None, flags: list[str]) -> list[str]:
    notes = []
    if raw_ece is not None and overlay_ece is not None:
        direction = "improves" if overlay_ece < raw_ece else "worsens" if overlay_ece > raw_ece else "matches"
        notes.append(f"Overlay {direction} bucket ECE versus raw in this tiny forward sample ({overlay_ece} vs {raw_ece}).")
    if "total_settled_lt_30" in flags:
        notes.append("Total settled sample is below 30, so bucket calibration is diagnostic only.")
    if "some_overlay_buckets_lt_10" in flags:
        notes.append("At least one non-empty bucket has fewer than 10 rows; Wilson intervals are wide.")
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
        "# v28 Target-Coverage FV Bucket Reliability",
        "",
        f"- Policy: `{report.get('policy')}`",
        f"- Overlay: `{report.get('overlay')}`",
        f"- Rows: `{report.get('rows')}`",
        f"- Raw/overlay ECE: `{fmt(report.get('raw_ece'))}/{fmt(report.get('overlay_ece'))}`",
        f"- ECE delta overlay-minus-raw: `{fmt(report.get('ece_delta_overlay_minus_raw'))}`",
        f"- Flags: `{', '.join(report.get('flags') or []) or 'none'}`",
        "",
        "## Interpretation",
        "",
    ]
    for note in report.get("interpretation") or []:
        lines.append(f"- {note}")
    for section, rows in [("Raw Buckets", report.get("raw_summary") or []), ("Overlay Buckets", report.get("overlay_summary") or [])]:
        lines.extend([
            "",
            f"## {section}",
            "",
            "| bucket | count | W/L | avg p | win rate | Wilson 95% | error | brier | reliable |",
            "|---|---:|---:|---:|---:|---|---:|---:|---:|",
        ])
        for row in rows:
            lines.append(
                f"| {row.get('bucket')} | {row.get('count')} | {row.get('wins')}/{row.get('losses')} | "
                f"{fmt(row.get('avg_p'))} | {fmt(row.get('win_rate'))} | "
                f"{fmt(row.get('wilson_low'))}-{fmt(row.get('wilson_high'))} | "
                f"{fmt(row.get('calibration_error'))} | {fmt(row.get('avg_brier'))} | {row.get('bucket_reliable_enough')} |"
            )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    report = build_report()
    write_md(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
