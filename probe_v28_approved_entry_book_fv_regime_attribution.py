"""Regime attribution for approved-entry book-anchor FV.

Research-only; no live bot changes or orders.

The approved-entry book FV challenger is the cleanest current evidence stream
because it uses actual v28-approved entries instead of rejected-actionable
shadow rows. This probe asks where book_probability improves calibration over
raw v28 probability and where it fails.
"""
from __future__ import annotations

import json
import math
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

from probe_v28_forward_physics_registry import build_rows as approved_entry_rows
from probe_v28_frozen_approved_entry_book_fv import STATE_JSON, load_json
from probe_v28_raw_entry_calibrated_probability import OVERLAYS


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
OUT_JSON = OUT_DIR / "v28_approved_entry_book_fv_regime_attribution_latest.json"
OUT_MD = OUT_DIR / "v28_approved_entry_book_fv_regime_attribution_latest.md"


def parse_ts(value: Any) -> datetime | None:
    if not value:
        return None
    try:
        parsed = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except ValueError:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def clamp_prob(value: float) -> float:
    return max(0.000001, min(0.999999, value))


def logloss(p: float, outcome: float) -> float:
    p = clamp_prob(p)
    return -(outcome * math.log(p) + (1.0 - outcome) * math.log(1.0 - p))


def as_float(value: Any) -> float | None:
    if value is None or value == "":
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def normalize_row(row: dict[str, Any]) -> dict[str, Any]:
    out = dict(row)
    if out.get("ask_prob") is None and out.get("ask_cents") is not None:
        ask_cents = as_float(out.get("ask_cents"))
        if ask_cents is not None:
            out["ask_prob"] = ask_cents / 100.0
    out["source"] = "approved_entry"
    return out


def future_rows() -> list[dict[str, Any]]:
    state = load_json(STATE_JSON)
    freeze_dt = parse_ts(state.get("freeze_ts_utc"))
    rows: list[dict[str, Any]] = []
    for row in approved_entry_rows():
        entry_dt = parse_ts(row.get("entry_ts"))
        if freeze_dt is not None and entry_dt is not None and entry_dt < freeze_dt:
            continue
        if row.get("side_won") is None:
            continue
        rows.append(normalize_row(row))
    return rows


def scored_rows() -> list[dict[str, Any]]:
    raw_fn = OVERLAYS["raw_probability"]
    book_fn = OVERLAYS["book_probability"]
    scored: list[dict[str, Any]] = []
    for row in future_rows():
        try:
            raw_p = clamp_prob(float(raw_fn(row)))
            book_p = clamp_prob(float(book_fn(row)))
        except (KeyError, TypeError, ValueError):
            continue
        outcome = 1.0 if row.get("side_won") is True else 0.0
        raw_brier = (raw_p - outcome) ** 2
        book_brier = (book_p - outcome) ** 2
        raw_logloss = logloss(raw_p, outcome)
        book_logloss = logloss(book_p, outcome)
        scored.append({
            **row,
            "raw_p": raw_p,
            "book_p": book_p,
            "outcome": outcome,
            "raw_brier": raw_brier,
            "book_brier": book_brier,
            "raw_logloss": raw_logloss,
            "book_logloss": book_logloss,
            "brier_delta_book_minus_raw": book_brier - raw_brier,
            "logloss_delta_book_minus_raw": book_logloss - raw_logloss,
            "book_minus_raw_p": book_p - raw_p,
        })
    return scored


def mean(values: list[float]) -> float | None:
    return sum(values) / len(values) if values else None


def bucket_summary(name: str, rows: list[dict[str, Any]]) -> dict[str, Any]:
    settled = len(rows)
    wins = sum(1 for row in rows if row.get("side_won") is True)
    losses = sum(1 for row in rows if row.get("side_won") is False)
    gross = sum(float(row.get("actual_gross_cents") or 0.0) for row in rows)
    return {
        "bucket": name,
        "settled": settled,
        "wins": wins,
        "losses": losses,
        "win_rate": None if settled == 0 else wins / settled,
        "gross_cents": gross,
        "avg_raw_p": mean([float(row["raw_p"]) for row in rows]),
        "avg_book_p": mean([float(row["book_p"]) for row in rows]),
        "avg_book_minus_raw_p": mean([float(row["book_minus_raw_p"]) for row in rows]),
        "raw_brier": mean([float(row["raw_brier"]) for row in rows]),
        "book_brier": mean([float(row["book_brier"]) for row in rows]),
        "brier_delta": mean([float(row["brier_delta_book_minus_raw"]) for row in rows]),
        "raw_logloss": mean([float(row["raw_logloss"]) for row in rows]),
        "book_logloss": mean([float(row["book_logloss"]) for row in rows]),
        "logloss_delta": mean([float(row["logloss_delta_book_minus_raw"]) for row in rows]),
        "sample_tiny": settled < 10,
    }


def flag(name: str) -> Callable[[dict[str, Any]], bool]:
    return lambda row: bool(row.get(name))


def between(field: str, low: float | None, high: float | None) -> Callable[[dict[str, Any]], bool]:
    def predicate(row: dict[str, Any]) -> bool:
        value = as_float(row.get(field))
        if value is None:
            return False
        if low is not None and value < low:
            return False
        if high is not None and value >= high:
            return False
        return True
    return predicate


def equals(field: str, expected: Any) -> Callable[[dict[str, Any]], bool]:
    return lambda row: row.get(field) == expected


def bucket_definitions() -> list[tuple[str, Callable[[dict[str, Any]], bool]]]:
    return [
        ("all", lambda row: True),
        ("side_yes", equals("side", "yes")),
        ("side_no", equals("side", "no")),
        ("early_stc_ge_600", between("seconds_to_close", 600.0, None)),
        ("mid_stc_240_600", between("seconds_to_close", 240.0, 600.0)),
        ("late_stc_lt_240", between("seconds_to_close", None, 240.0)),
        ("near_boundary_absd_lt_025", between("abs_d_sigma", None, 0.25)),
        ("mid_boundary_absd_025_075", between("abs_d_sigma", 0.25, 0.75)),
        ("far_boundary_absd_ge_075", between("abs_d_sigma", 0.75, None)),
        ("recross_ge_075", between("recross_hazard_score", 0.75, None)),
        ("recross_lt_075", between("recross_hazard_score", None, 0.75)),
        ("ask_lt_55", between("ask_prob", None, 0.55)),
        ("ask_55_75", between("ask_prob", 0.55, 0.75)),
        ("ask_ge_75", between("ask_prob", 0.75, None)),
        ("book_discount_ge_10pp", lambda row: (as_float(row.get("raw_p")) or 0.0) - (as_float(row.get("book_p")) or 0.0) >= 0.10),
        ("book_premium_ge_05pp", lambda row: (as_float(row.get("book_p")) or 0.0) - (as_float(row.get("raw_p")) or 0.0) >= 0.05),
        ("thin_touch_depth", flag("h2_thin_touch_depth")),
        ("crowded_depth", flag("h2_crowded_depth")),
        ("large_model_disagreement", flag("h4_large_model_disagreement")),
        ("old_model_opposes", flag("h4_old_model_opposes_side")),
        ("late_high_sigma", flag("h5_late_high_sigma")),
        ("high_recross_hazard", flag("h6_recross_hazard_high")),
    ]


def build_report() -> dict[str, Any]:
    rows = scored_rows()
    buckets = []
    for name, predicate in bucket_definitions():
        selected = [row for row in rows if predicate(row)]
        if selected:
            buckets.append(bucket_summary(name, selected))
    helpful = sorted(
        [bucket for bucket in buckets if bucket.get("settled", 0) >= 5],
        key=lambda bucket: float(bucket.get("brier_delta") or 0.0),
    )
    harmful = sorted(
        [bucket for bucket in buckets if bucket.get("settled", 0) >= 5],
        key=lambda bucket: float(bucket.get("brier_delta") or 0.0),
        reverse=True,
    )
    return {
        "diagnostic": "approved_entry_book_fv_regime_attribution",
        "rows": len(rows),
        "overall": bucket_summary("all", rows),
        "buckets": buckets,
        "most_helpful_brier_buckets": helpful[:8],
        "most_harmful_brier_buckets": harmful[:8],
        "interpretation": interpretation(rows, helpful[:3], harmful[:3]),
    }


def interpretation(
    rows: list[dict[str, Any]],
    helpful: list[dict[str, Any]],
    harmful: list[dict[str, Any]],
) -> list[str]:
    notes = [
        f"Approved-entry attribution scored {len(rows)} frozen future settled rows.",
        "Negative delta means book_probability calibrated better than raw v28 probability in that bucket.",
    ]
    if helpful:
        best = helpful[0]
        notes.append(
            f"Most helpful bucket by Brier is {best['bucket']} with {best['settled']} rows and "
            f"delta {best['brier_delta']}."
        )
    if harmful:
        worst = harmful[0]
        notes.append(
            f"Most harmful bucket by Brier is {worst['bucket']} with {worst['settled']} rows and "
            f"delta {worst['brier_delta']}."
        )
    notes.append("This is attribution only; it does not promote a live rule.")
    return notes


def fmt(value: Any) -> str:
    if value is None:
        return "None"
    if isinstance(value, float):
        return f"{value:.6f}"
    return str(value)


def write_md(report: dict[str, Any]) -> None:
    lines = [
        "# v28 Approved-Entry Book FV Regime Attribution",
        "",
        "Research-only attribution for actual v28-approved entries.",
        "",
        "## Interpretation",
        "",
    ]
    for note in report.get("interpretation") or []:
        lines.append(f"- {note}")
    lines.extend([
        "",
        "## Overall",
        "",
        "| bucket | settled | W/L | gross c | raw p | book p | d p | raw brier | book brier | d brier | raw logloss | book logloss | d logloss |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ])
    write_bucket_line(lines, report["overall"])
    lines.extend([
        "",
        "## Helpful Buckets",
        "",
        "| bucket | settled | W/L | gross c | raw p | book p | d p | raw brier | book brier | d brier | raw logloss | book logloss | d logloss |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ])
    for bucket in report.get("most_helpful_brier_buckets") or []:
        write_bucket_line(lines, bucket)
    lines.extend([
        "",
        "## Harmful Buckets",
        "",
        "| bucket | settled | W/L | gross c | raw p | book p | d p | raw brier | book brier | d brier | raw logloss | book logloss | d logloss |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ])
    for bucket in report.get("most_harmful_brier_buckets") or []:
        write_bucket_line(lines, bucket)
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_bucket_line(lines: list[str], bucket: dict[str, Any]) -> None:
    lines.append(
        f"| `{bucket.get('bucket')}` | {bucket.get('settled')} | {bucket.get('wins')}/{bucket.get('losses')} | "
        f"{fmt(bucket.get('gross_cents'))} | {fmt(bucket.get('avg_raw_p'))} | {fmt(bucket.get('avg_book_p'))} | "
        f"{fmt(bucket.get('avg_book_minus_raw_p'))} | {fmt(bucket.get('raw_brier'))} | "
        f"{fmt(bucket.get('book_brier'))} | {fmt(bucket.get('brier_delta'))} | "
        f"{fmt(bucket.get('raw_logloss'))} | {fmt(bucket.get('book_logloss'))} | {fmt(bucket.get('logloss_delta'))} |"
    )


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    report = build_report()
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_md(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
