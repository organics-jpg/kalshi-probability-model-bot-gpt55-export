"""Approved-entry diagnostic for book/raw FV probability blends.

Research-only; no live bot changes or orders.

Physics hypothesis:
    v28 raw probability may contain directional "memory" from the BTC path,
    while executable book probability is the best current calibration anchor
    after v28 has already selected a trade. A convex blend tests whether raw
    adds residual signal after anchoring to the book, or whether it mostly adds
    stale overconfidence.
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
OUT_JSON = OUT_DIR / "v28_approved_entry_book_raw_blend_latest.json"
OUT_MD = OUT_DIR / "v28_approved_entry_book_raw_blend_latest.md"

BOOTSTRAP_SEED = 28617
BOOTSTRAP_RUNS = 5000
MIN_SETTLED = 30
ALPHAS = [0.0, 0.10, 0.20, 0.35, 0.50, 0.75, 1.0]


def clamp_prob(value: float) -> float:
    return max(0.000001, min(0.999999, value))


def logloss(p: float, outcome: float) -> float:
    p = clamp_prob(p)
    return -(outcome * math.log(p) + (1.0 - outcome) * math.log(1.0 - p))


def percentile(values: list[float], q: float) -> float | None:
    if not values:
        return None
    idx = min(len(values) - 1, max(0, int(round((len(values) - 1) * q))))
    return values[idx]


def normalize_row(row: dict[str, Any]) -> dict[str, Any]:
    out = dict(row)
    if out.get("ask_prob") is None and out.get("ask_cents") is not None:
        try:
            out["ask_prob"] = float(out["ask_cents"]) / 100.0
        except (TypeError, ValueError):
            pass
    out["source"] = "approved_entry"
    return out


def base_rows() -> list[dict[str, Any]]:
    raw_fn = OVERLAYS["raw_probability"]
    book_fn = OVERLAYS["book_probability"]
    rows = []
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
        rows.append({
            "market": row.get("market"),
            "side": row.get("side"),
            "won": row.get("side_won"),
            "outcome": outcome,
            "p_raw": p_raw,
            "p_book": p_book,
            "raw_minus_book": p_raw - p_book,
            "abs_raw_minus_book": abs(p_raw - p_book),
            "gross_cents": row.get("actual_gross_cents"),
            "ask_cents": row.get("ask_cents"),
            "abs_d_sigma": row.get("abs_d_sigma"),
            "recross_hazard_score": row.get("recross_hazard_score"),
        })
    return rows


def p_blend(row: dict[str, Any], alpha: float) -> float:
    return clamp_prob(float(row["p_book"]) + alpha * (float(row["p_raw"]) - float(row["p_book"])))


def score_rows(rows: list[dict[str, Any]], alpha: float) -> dict[str, Any]:
    if not rows:
        return {
            "alpha_raw_weight": alpha,
            "rows": 0,
            "wins": 0,
            "losses": 0,
            "avg_p": None,
            "win_rate": None,
            "avg_brier": None,
            "avg_logloss": None,
            "gross_cents": 0.0,
        }
    probs = [p_blend(row, alpha) for row in rows]
    outcomes = [float(row["outcome"]) for row in rows]
    briers = [(p - y) ** 2 for p, y in zip(probs, outcomes)]
    losses = [logloss(p, y) for p, y in zip(probs, outcomes)]
    return {
        "alpha_raw_weight": alpha,
        "rows": len(rows),
        "wins": sum(1 for row in rows if row.get("won") is True),
        "losses": sum(1 for row in rows if row.get("won") is False),
        "avg_p": sum(probs) / len(probs),
        "win_rate": sum(outcomes) / len(outcomes),
        "calibration_error": (sum(outcomes) / len(outcomes)) - (sum(probs) / len(probs)),
        "avg_brier": sum(briers) / len(briers),
        "avg_logloss": sum(losses) / len(losses),
        "gross_cents": sum(float(row.get("gross_cents") or 0.0) for row in rows),
    }


def bootstrap_delta(rows: list[dict[str, Any]], alpha: float, reference_alpha: float = 1.0) -> dict[str, Any]:
    if not rows:
        return {}
    rng = random.Random(BOOTSTRAP_SEED + int(alpha * 1000))
    briers = []
    loglosses = []
    for _ in range(BOOTSTRAP_RUNS):
        sample = [rows[rng.randrange(len(rows))] for _ in range(len(rows))]
        cand = score_rows(sample, alpha)
        ref = score_rows(sample, reference_alpha)
        briers.append(float(cand["avg_brier"]) - float(ref["avg_brier"]))
        loglosses.append(float(cand["avg_logloss"]) - float(ref["avg_logloss"]))
    briers.sort()
    loglosses.sort()
    return {
        "runs": BOOTSTRAP_RUNS,
        "reference_alpha_raw_weight": reference_alpha,
        "brier_delta_p05": percentile(briers, 0.05),
        "brier_delta_p50": percentile(briers, 0.50),
        "brier_delta_p95": percentile(briers, 0.95),
        "logloss_delta_p05": percentile(loglosses, 0.05),
        "logloss_delta_p50": percentile(loglosses, 0.50),
        "logloss_delta_p95": percentile(loglosses, 0.95),
        "brier_prob_negative": sum(1 for value in briers if value < 0.0) / len(briers),
        "logloss_prob_negative": sum(1 for value in loglosses if value < 0.0) / len(loglosses),
    }


def leave_one_market(rows: list[dict[str, Any]], alpha: float) -> list[dict[str, Any]]:
    markets = sorted({str(row.get("market") or "") for row in rows if row.get("market")})
    out = []
    for market in markets:
        kept = [row for row in rows if str(row.get("market") or "") != market]
        cand = score_rows(kept, alpha)
        raw = score_rows(kept, 1.0)
        out.append({
            "left_out_market": market,
            "rows": cand.get("rows"),
            "wins": cand.get("wins"),
            "losses": cand.get("losses"),
            "brier_delta_vs_raw": None if cand.get("avg_brier") is None else float(cand["avg_brier"]) - float(raw["avg_brier"]),
            "logloss_delta_vs_raw": None if cand.get("avg_logloss") is None else float(cand["avg_logloss"]) - float(raw["avg_logloss"]),
        })
    out.sort(key=lambda row: float(row.get("brier_delta_vs_raw") or 999.0), reverse=True)
    return out


def disagreement_buckets(rows: list[dict[str, Any]], best_alpha: float) -> list[dict[str, Any]]:
    buckets = [
        ("raw_below_book", lambda row: float(row["raw_minus_book"]) < -0.05),
        ("raw_near_book", lambda row: abs(float(row["raw_minus_book"])) <= 0.05),
        ("raw_above_book_5_15", lambda row: 0.05 < float(row["raw_minus_book"]) <= 0.15),
        ("raw_above_book_gt15", lambda row: float(row["raw_minus_book"]) > 0.15),
    ]
    out = []
    for name, pred in buckets:
        bucket = [row for row in rows if pred(row)]
        if not bucket:
            continue
        cand = score_rows(bucket, best_alpha)
        book = score_rows(bucket, 0.0)
        raw = score_rows(bucket, 1.0)
        out.append({
            "bucket": name,
            "rows": len(bucket),
            "wins": cand.get("wins"),
            "losses": cand.get("losses"),
            "avg_raw_minus_book": sum(float(row["raw_minus_book"]) for row in bucket) / len(bucket),
            "best_alpha_brier": cand.get("avg_brier"),
            "book_brier": book.get("avg_brier"),
            "raw_brier": raw.get("avg_brier"),
            "best_alpha_logloss": cand.get("avg_logloss"),
            "book_logloss": book.get("avg_logloss"),
            "raw_logloss": raw.get("avg_logloss"),
        })
    return out


def build_report() -> dict[str, Any]:
    rows = base_rows()
    scores = [score_rows(rows, alpha) for alpha in ALPHAS]
    raw = next((row for row in scores if row.get("alpha_raw_weight") == 1.0), {})
    for row in scores:
        if row.get("avg_brier") is not None and raw.get("avg_brier") is not None:
            row["brier_delta_vs_raw"] = float(row["avg_brier"]) - float(raw["avg_brier"])
            row["logloss_delta_vs_raw"] = float(row["avg_logloss"]) - float(raw["avg_logloss"])
            row["bootstrap_vs_raw"] = bootstrap_delta(rows, float(row["alpha_raw_weight"]), 1.0)
        else:
            row["brier_delta_vs_raw"] = None
            row["logloss_delta_vs_raw"] = None
            row["bootstrap_vs_raw"] = {}
    ranked = sorted(scores, key=lambda row: (float(row.get("avg_brier") or 999.0), float(row.get("avg_logloss") or 999.0)))
    best = ranked[0] if ranked else {}
    best_alpha = float(best.get("alpha_raw_weight") or 0.0)
    leave_one = leave_one_market(rows, best_alpha)
    failures = [
        row for row in leave_one
        if row.get("brier_delta_vs_raw") is None
        or float(row["brier_delta_vs_raw"]) >= 0.0
        or row.get("logloss_delta_vs_raw") is None
        or float(row["logloss_delta_vs_raw"]) >= 0.0
    ]
    blockers = []
    if len(rows) < MIN_SETTLED:
        blockers.append("settled_lt_30")
    if best.get("brier_delta_vs_raw") is None or float(best["brier_delta_vs_raw"]) >= 0.0:
        blockers.append("best_brier_not_better_than_raw")
    if best.get("logloss_delta_vs_raw") is None or float(best["logloss_delta_vs_raw"]) >= 0.0:
        blockers.append("best_logloss_not_better_than_raw")
    boot = best.get("bootstrap_vs_raw") or {}
    if boot and (boot.get("brier_delta_p95") is None or float(boot["brier_delta_p95"]) >= 0.0):
        blockers.append("bootstrap_brier_p95_not_negative")
    if boot and (boot.get("logloss_delta_p95") is None or float(boot["logloss_delta_p95"]) >= 0.0):
        blockers.append("bootstrap_logloss_p95_not_negative")
    if failures:
        blockers.append("leave_one_market_failure")
    return {
        "surface": "actual_v28_approved_entries_only",
        "hypothesis": "convex FV blend p = book + alpha * (raw - book)",
        "rows": len(rows),
        "alphas": ALPHAS,
        "ranked": ranked,
        "best": best,
        "best_leave_one_market": leave_one,
        "best_leave_one_failures": failures,
        "best_disagreement_buckets": disagreement_buckets(rows, best_alpha),
        "blockers": blockers,
        "interpretation": interpretation(best, blockers),
    }


def interpretation(best: dict[str, Any], blockers: list[str]) -> list[str]:
    alpha = best.get("alpha_raw_weight")
    notes = [
        f"Best blend uses raw weight alpha={alpha}; alpha=0 is pure book and alpha=1 is raw v28.",
        f"Best Brier/logloss deltas versus raw are {best.get('brier_delta_vs_raw')}/{best.get('logloss_delta_vs_raw')}.",
    ]
    if alpha == 0.0:
        notes.append("Raw v28 does not appear to add residual calibration value after the book anchor on this approved-entry surface.")
    elif alpha is not None and float(alpha) < 1.0:
        notes.append("Raw v28 appears useful only as a partial memory term after anchoring to the executable book.")
    else:
        notes.append("Raw v28 remains best on this surface; book anchoring would not be supported.")
    if blockers:
        notes.append(f"Promotion blockers: {', '.join(blockers)}.")
    return notes


def fmt(value: Any) -> str:
    if value is None:
        return "None"
    if isinstance(value, float):
        return f"{value:.6f}"
    return str(value)


def write_report(report: dict[str, Any]) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8")
    best = report.get("best") or {}
    boot = best.get("bootstrap_vs_raw") or {}
    lines = [
        "# v28 Approved-Entry Book/Raw FV Blend",
        "",
        f"- Surface: `{report.get('surface')}`",
        f"- Hypothesis: `{report.get('hypothesis')}`",
        f"- Rows: `{report.get('rows')}`",
        f"- Best alpha raw weight: `{fmt(best.get('alpha_raw_weight'))}`",
        f"- Best Brier/logloss deltas vs raw: `{fmt(best.get('brier_delta_vs_raw'))}/{fmt(best.get('logloss_delta_vs_raw'))}`",
        f"- Best bootstrap p95 Brier/logloss vs raw: `{fmt(boot.get('brier_delta_p95'))}/{fmt(boot.get('logloss_delta_p95'))}`",
        f"- Blockers: `{', '.join(report.get('blockers') or []) or 'none'}`",
        "",
        "## Interpretation",
        "",
    ]
    for note in report.get("interpretation") or []:
        lines.append(f"- {note}")
    lines.extend([
        "",
        "## Alpha Ranking",
        "",
        "| rank | alpha raw weight | rows | W/L | avg p | win rate | cal err | brier | d brier | brier p95 | logloss | d logloss | logloss p95 |",
        "|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ])
    for idx, row in enumerate(report.get("ranked") or [], start=1):
        boot = row.get("bootstrap_vs_raw") or {}
        lines.append(
            f"| {idx} | {fmt(row.get('alpha_raw_weight'))} | {row.get('rows')} | {row.get('wins')}/{row.get('losses')} | "
            f"{fmt(row.get('avg_p'))} | {fmt(row.get('win_rate'))} | {fmt(row.get('calibration_error'))} | "
            f"{fmt(row.get('avg_brier'))} | {fmt(row.get('brier_delta_vs_raw'))} | {fmt(boot.get('brier_delta_p95'))} | "
            f"{fmt(row.get('avg_logloss'))} | {fmt(row.get('logloss_delta_vs_raw'))} | {fmt(boot.get('logloss_delta_p95'))} |"
        )
    lines.extend([
        "",
        "## Raw/Book Disagreement Buckets",
        "",
        "| bucket | rows | W/L | avg raw-book | best brier | book brier | raw brier | best logloss | book logloss | raw logloss |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ])
    for row in report.get("best_disagreement_buckets") or []:
        lines.append(
            f"| {row.get('bucket')} | {row.get('rows')} | {row.get('wins')}/{row.get('losses')} | "
            f"{fmt(row.get('avg_raw_minus_book'))} | {fmt(row.get('best_alpha_brier'))} | "
            f"{fmt(row.get('book_brier'))} | {fmt(row.get('raw_brier'))} | "
            f"{fmt(row.get('best_alpha_logloss'))} | {fmt(row.get('book_logloss'))} | {fmt(row.get('raw_logloss'))} |"
        )
    lines.extend([
        "",
        "## Worst Leave-One-Market Slices For Best Alpha",
        "",
        "| left out | rows | W/L | d brier vs raw | d logloss vs raw |",
        "|---|---:|---:|---:|---:|",
    ])
    for row in (report.get("best_leave_one_market") or [])[:12]:
        lines.append(
            f"| {row.get('left_out_market')} | {row.get('rows')} | {row.get('wins')}/{row.get('losses')} | "
            f"{fmt(row.get('brier_delta_vs_raw'))} | {fmt(row.get('logloss_delta_vs_raw'))} |"
        )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    report = build_report()
    write_report(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
