"""Robustness audit for approved-entry book-anchor FV calibration.

Research-only; no live bot changes or orders.

The approved-entry validator says book_probability is much better calibrated
than raw v28 on actual approved rows. This audit checks whether that result is
stable under leave-one-market and bootstrap resampling, so it cannot be waved
through as one lucky market.
"""
from __future__ import annotations

import json
import math
import random
from pathlib import Path
from typing import Any

from probe_v28_forward_physics_registry import build_rows as approved_entry_rows
from probe_v28_raw_entry_calibrated_probability import OVERLAYS


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
OUT_JSON = OUT_DIR / "v28_approved_entry_book_fv_robustness_latest.json"
OUT_MD = OUT_DIR / "v28_approved_entry_book_fv_robustness_latest.md"

BOOTSTRAP_SEED = 28601
BOOTSTRAP_RUNS = 5000
MIN_SETTLED = 30


def clamp_prob(value: float) -> float:
    return max(0.000001, min(0.999999, value))


def logloss(p: float, outcome: float) -> float:
    p = clamp_prob(p)
    return -(outcome * math.log(p) + (1.0 - outcome) * math.log(1.0 - p))


def normalize_row(row: dict[str, Any]) -> dict[str, Any]:
    out = dict(row)
    if out.get("ask_prob") is None and out.get("ask_cents") is not None:
        try:
            out["ask_prob"] = float(out["ask_cents"]) / 100.0
        except (TypeError, ValueError):
            pass
    out["source"] = "approved_entry"
    return out


def scored_rows() -> list[dict[str, Any]]:
    raw_fn = OVERLAYS["raw_probability"]
    book_fn = OVERLAYS["book_probability"]
    out = []
    for raw in approved_entry_rows():
        if raw.get("side_won") is None:
            continue
        row = normalize_row(raw)
        try:
            p_raw = clamp_prob(float(raw_fn(row)))
            p_book = clamp_prob(float(book_fn(row)))
        except (KeyError, TypeError, ValueError):
            continue
        outcome = 1.0 if row.get("side_won") is True else 0.0
        out.append({
            "market": row.get("market"),
            "side": row.get("side"),
            "won": row.get("side_won"),
            "outcome": outcome,
            "p_raw": p_raw,
            "p_book": p_book,
            "brier_delta_book_minus_raw": (p_book - outcome) ** 2 - (p_raw - outcome) ** 2,
            "logloss_delta_book_minus_raw": logloss(p_book, outcome) - logloss(p_raw, outcome),
            "gross_cents": row.get("actual_gross_cents"),
            "ask_cents": row.get("ask_cents"),
            "p_side": row.get("p_side"),
            "abs_d_sigma": row.get("abs_d_sigma"),
            "recross_hazard_score": row.get("recross_hazard_score"),
        })
    return out


def summarize(rows: list[dict[str, Any]]) -> dict[str, Any]:
    if not rows:
        return {
            "rows": 0,
            "wins": 0,
            "losses": 0,
            "brier_delta_mean": None,
            "logloss_delta_mean": None,
            "gross_cents": 0.0,
        }
    return {
        "rows": len(rows),
        "wins": sum(1 for row in rows if row.get("won") is True),
        "losses": sum(1 for row in rows if row.get("won") is False),
        "brier_delta_mean": sum(float(row["brier_delta_book_minus_raw"]) for row in rows) / len(rows),
        "logloss_delta_mean": sum(float(row["logloss_delta_book_minus_raw"]) for row in rows) / len(rows),
        "gross_cents": sum(float(row.get("gross_cents") or 0.0) for row in rows),
    }


def bootstrap(rows: list[dict[str, Any]]) -> dict[str, Any]:
    if not rows:
        return {}
    rng = random.Random(BOOTSTRAP_SEED)
    brier = []
    loglosses = []
    for _ in range(BOOTSTRAP_RUNS):
        sample = [rows[rng.randrange(len(rows))] for _ in range(len(rows))]
        summary = summarize(sample)
        brier.append(float(summary["brier_delta_mean"]))
        loglosses.append(float(summary["logloss_delta_mean"]))
    brier.sort()
    loglosses.sort()
    return {
        "runs": BOOTSTRAP_RUNS,
        "brier_p05": percentile(brier, 0.05),
        "brier_p50": percentile(brier, 0.50),
        "brier_p95": percentile(brier, 0.95),
        "logloss_p05": percentile(loglosses, 0.05),
        "logloss_p50": percentile(loglosses, 0.50),
        "logloss_p95": percentile(loglosses, 0.95),
        "brier_prob_negative": sum(1 for value in brier if value < 0.0) / len(brier),
        "logloss_prob_negative": sum(1 for value in loglosses if value < 0.0) / len(loglosses),
    }


def percentile(values: list[float], q: float) -> float | None:
    if not values:
        return None
    idx = min(len(values) - 1, max(0, int(round((len(values) - 1) * q))))
    return values[idx]


def leave_one_market(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    markets = sorted({str(row.get("market") or "") for row in rows if row.get("market")})
    out = []
    for market in markets:
        kept = [row for row in rows if str(row.get("market") or "") != market]
        summary = summarize(kept)
        out.append({
            "left_out_market": market,
            **summary,
            "book_brier_still_better": summary.get("brier_delta_mean") is not None and float(summary["brier_delta_mean"]) < 0.0,
            "book_logloss_still_better": summary.get("logloss_delta_mean") is not None and float(summary["logloss_delta_mean"]) < 0.0,
        })
    out.sort(key=lambda row: float(row.get("brier_delta_mean") or 999.0), reverse=True)
    return out


def build_report() -> dict[str, Any]:
    rows = scored_rows()
    full = summarize(rows)
    leave_one = leave_one_market(rows)
    boot = bootstrap(rows)
    failures = [
        row for row in leave_one
        if not row.get("book_brier_still_better") or not row.get("book_logloss_still_better")
    ]
    blockers = []
    if len(rows) < MIN_SETTLED:
        blockers.append("settled_lt_30")
    if full.get("brier_delta_mean") is None or float(full["brier_delta_mean"]) >= 0.0:
        blockers.append("full_brier_not_better")
    if full.get("logloss_delta_mean") is None or float(full["logloss_delta_mean"]) >= 0.0:
        blockers.append("full_logloss_not_better")
    if failures:
        blockers.append("leave_one_market_failure")
    if boot and (boot.get("brier_p95") is None or float(boot["brier_p95"]) >= 0.0):
        blockers.append("bootstrap_brier_p95_not_negative")
    if boot and (boot.get("logloss_p95") is None or float(boot["logloss_p95"]) >= 0.0):
        blockers.append("bootstrap_logloss_p95_not_negative")
    return {
        "surface": "actual_v28_approved_entries_only",
        "candidate": "book_probability",
        "rows": len(rows),
        "full": full,
        "bootstrap": boot,
        "leave_one_market": leave_one,
        "leave_one_failures": failures,
        "blockers": blockers,
        "interpretation": interpretation(full, boot, failures, blockers),
    }


def interpretation(full: dict[str, Any], boot: dict[str, Any], failures: list[dict[str, Any]], blockers: list[str]) -> list[str]:
    notes = [
        f"Book probability full-sample Brier/logloss deltas are {full.get('brier_delta_mean')}/{full.get('logloss_delta_mean')} versus raw.",
    ]
    if boot:
        notes.append(
            f"Bootstrap p95 Brier/logloss deltas are {boot.get('brier_p95')}/{boot.get('logloss_p95')}."
        )
    if failures:
        notes.append(f"Leave-one-market failures: {len(failures)}.")
    else:
        notes.append("Book probability remains better than raw in every leave-one-market slice.")
    if blockers:
        notes.append(f"Promotion blockers: {', '.join(blockers)}.")
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
    full = report.get("full") or {}
    boot = report.get("bootstrap") or {}
    lines = [
        "# v28 Approved-Entry Book FV Robustness",
        "",
        f"- Surface: `{report.get('surface')}`",
        f"- Candidate: `{report.get('candidate')}`",
        f"- Rows: `{report.get('rows')}`",
        f"- Full Brier/logloss deltas: `{fmt(full.get('brier_delta_mean'))}/{fmt(full.get('logloss_delta_mean'))}`",
        f"- Bootstrap p95 Brier/logloss: `{fmt(boot.get('brier_p95'))}/{fmt(boot.get('logloss_p95'))}`",
        f"- Blockers: `{', '.join(report.get('blockers') or []) or 'none'}`",
        "",
        "## Interpretation",
        "",
    ]
    for note in report.get("interpretation") or []:
        lines.append(f"- {note}")
    lines.extend([
        "",
        "## Worst Leave-One-Market Slices",
        "",
        "| left out | rows | W/L | brier d | logloss d | brier better | logloss better |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ])
    for row in (report.get("leave_one_market") or [])[:12]:
        lines.append(
            f"| {row.get('left_out_market')} | {row.get('rows')} | {row.get('wins')}/{row.get('losses')} | "
            f"{fmt(row.get('brier_delta_mean'))} | {fmt(row.get('logloss_delta_mean'))} | "
            f"{row.get('book_brier_still_better')} | {row.get('book_logloss_still_better')} |"
        )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    report = build_report()
    write_md(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
