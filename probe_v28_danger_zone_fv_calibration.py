"""Danger-zone FV calibration diagnostics for v28 approved entries.

Research-only; no live bot changes or orders.

Tests whether the same raw/book disagreement that hurts entry P&L is also a
probability-calibration failure. This keeps the candidate physics simple:
when raw FV is much richer than the executable book, reduce confidence rather
than inventing a new side.
"""
from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any, Callable

from probe_v28_approved_entry_state_valves import book_prob, raw_book_gap, raw_prob, sorted_rows, with_state


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
OUT_JSON = OUT_DIR / "v28_danger_zone_fv_calibration_latest.json"
OUT_MD = OUT_DIR / "v28_danger_zone_fv_calibration_latest.md"

MIN_SETTLED = 30


def clamp_prob(value: float) -> float:
    return max(0.000001, min(0.999999, value))


def logloss(p: float, outcome: float) -> float:
    p = clamp_prob(p)
    return -(outcome * math.log(p) + (1.0 - outcome) * math.log(1.0 - p))


def avg(values: list[float]) -> float | None:
    return sum(values) / len(values) if values else None


def is_same_side_reentry(row: dict[str, Any]) -> bool:
    return int(row.get("market_side_entry_index") or 0) > 0


def danger_zone(row: dict[str, Any]) -> bool:
    gap = raw_book_gap(row)
    if gap is None:
        return False
    return gap > 0.30 or (is_same_side_reentry(row) and gap > 0.15)


def raw_or_book(row: dict[str, Any]) -> float | None:
    return raw_prob(row)


def book_only(row: dict[str, Any]) -> float | None:
    return book_prob(row)


def danger_to_book(row: dict[str, Any]) -> float | None:
    raw = raw_prob(row)
    book = book_prob(row)
    if raw is None:
        return None
    if danger_zone(row) and book is not None:
        return book
    return raw


def danger_halfway_to_book(row: dict[str, Any]) -> float | None:
    raw = raw_prob(row)
    book = book_prob(row)
    if raw is None:
        return None
    if danger_zone(row) and book is not None:
        return 0.5 * raw + 0.5 * book
    return raw


def danger_cap_gap15(row: dict[str, Any]) -> float | None:
    raw = raw_prob(row)
    book = book_prob(row)
    if raw is None:
        return None
    if danger_zone(row) and book is not None:
        return min(raw, book + 0.15)
    return raw


def danger_cap_gap20(row: dict[str, Any]) -> float | None:
    raw = raw_prob(row)
    book = book_prob(row)
    if raw is None:
        return None
    if danger_zone(row) and book is not None:
        return min(raw, book + 0.20)
    return raw


def danger_haircut_10pp(row: dict[str, Any]) -> float | None:
    raw = raw_prob(row)
    if raw is None:
        return None
    if danger_zone(row):
        return raw - 0.10
    return raw


OVERLAYS: dict[str, Callable[[dict[str, Any]], float | None]] = {
    "raw_probability": raw_or_book,
    "book_probability": book_only,
    "danger_to_book": danger_to_book,
    "danger_halfway_to_book": danger_halfway_to_book,
    "danger_cap_gap15": danger_cap_gap15,
    "danger_cap_gap20": danger_cap_gap20,
    "danger_haircut_10pp": danger_haircut_10pp,
}


def score_overlay(rows: list[dict[str, Any]], name: str, fn: Callable[[dict[str, Any]], float | None]) -> dict[str, Any]:
    scored = []
    for row in rows:
        p = fn(row)
        if p is None or row.get("side_won") is None:
            continue
        outcome = 1.0 if row.get("side_won") is True else 0.0
        p = clamp_prob(float(p))
        scored.append({
            "market": row.get("market"),
            "side": row.get("side"),
            "p": p,
            "outcome": outcome,
            "won": row.get("side_won"),
            "brier": (p - outcome) ** 2,
            "logloss": logloss(p, outcome),
            "actual_gross_cents": row.get("actual_gross_cents"),
            "danger_zone": danger_zone(row),
        })
    briers = [float(row["brier"]) for row in scored]
    loglosses = [float(row["logloss"]) for row in scored]
    outcomes = [float(row["outcome"]) for row in scored]
    probs = [float(row["p"]) for row in scored]
    return {
        "overlay": name,
        "settled": len(scored),
        "wins": sum(1 for row in scored if row.get("won") is True),
        "losses": sum(1 for row in scored if row.get("won") is False),
        "avg_p": avg(probs),
        "win_rate": avg(outcomes),
        "calibration_error": None if avg(probs) is None or avg(outcomes) is None else avg(outcomes) - avg(probs),
        "avg_brier": avg(briers),
        "avg_logloss": avg(loglosses),
        "gross_cents": sum(float(row.get("actual_gross_cents") or 0.0) for row in scored),
        "danger_rows": sum(1 for row in scored if row.get("danger_zone")),
    }


def enrich(scores: list[dict[str, Any]]) -> list[dict[str, Any]]:
    raw = next((row for row in scores if row.get("overlay") == "raw_probability"), {})
    raw_brier = raw.get("avg_brier")
    raw_logloss = raw.get("avg_logloss")
    out = []
    for row in scores:
        brier = row.get("avg_brier")
        loss = row.get("avg_logloss")
        enriched = {
            **row,
            "brier_delta_vs_raw": None if brier is None or raw_brier is None else float(brier) - float(raw_brier),
            "logloss_delta_vs_raw": None if loss is None or raw_logloss is None else float(loss) - float(raw_logloss),
        }
        blockers = []
        if int(enriched.get("settled") or 0) < MIN_SETTLED:
            blockers.append("settled_lt_30")
        if row.get("overlay") != "raw_probability":
            if enriched["brier_delta_vs_raw"] is None or enriched["brier_delta_vs_raw"] >= 0:
                blockers.append("brier_not_better_than_raw")
            if enriched["logloss_delta_vs_raw"] is None or enriched["logloss_delta_vs_raw"] >= 0:
                blockers.append("logloss_not_better_than_raw")
        enriched["blockers"] = blockers
        out.append(enriched)
    out.sort(key=lambda row: (float(row.get("avg_brier") or 999.0), float(row.get("avg_logloss") or 999.0)))
    return out


def bucket_summary(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    buckets = {
        "danger_zone": [row for row in rows if danger_zone(row)],
        "not_danger_zone": [row for row in rows if not danger_zone(row)],
        "same_side_reentry": [row for row in rows if is_same_side_reentry(row)],
        "raw_book_gap_gt30": [row for row in rows if (raw_book_gap(row) is not None and float(raw_book_gap(row)) > 0.30)],
    }
    out = []
    for name, subset in buckets.items():
        if not subset:
            continue
        outcomes = [1.0 if row.get("side_won") is True else 0.0 for row in subset]
        raw_probs = [float(raw_prob(row)) for row in subset if raw_prob(row) is not None]
        book_probs = [float(book_prob(row)) for row in subset if book_prob(row) is not None]
        out.append({
            "bucket": name,
            "rows": len(subset),
            "wins": sum(1 for row in subset if row.get("side_won") is True),
            "losses": sum(1 for row in subset if row.get("side_won") is False),
            "win_rate": avg(outcomes),
            "avg_raw_p": avg(raw_probs),
            "avg_book_p": avg(book_probs),
            "actual_gross_cents": sum(float(row.get("actual_gross_cents") or 0.0) for row in subset),
            "hold_gross_cents": sum(float(row.get("hold_gross_cents") or 0.0) for row in subset),
        })
    return out


def build_report() -> dict[str, Any]:
    rows = with_state(sorted_rows())
    ranked = enrich([score_overlay(rows, name, fn) for name, fn in OVERLAYS.items()])
    return {
        "surface": "actual_v28_approved_entries_only",
        "rows": len(rows),
        "markets": len({row.get("market") for row in rows}),
        "best_overlay": ranked[0].get("overlay") if ranked else None,
        "ranked": ranked,
        "buckets": bucket_summary(rows),
        "interpretation": current_read(ranked, rows),
    }


def current_read(ranked: list[dict[str, Any]], rows: list[dict[str, Any]]) -> list[str]:
    notes = []
    danger_rows = [row for row in rows if danger_zone(row)]
    if ranked:
        best = ranked[0]
        notes.append(
            f"Best danger-zone FV overlay is {best.get('overlay')} with Brier/logloss deltas {best.get('brier_delta_vs_raw')}/{best.get('logloss_delta_vs_raw')}."
        )
    notes.append(
        f"Danger-zone rows are {len(danger_rows)}/{len(rows)} with gross {sum(float(row.get('actual_gross_cents') or 0.0) for row in danger_rows)}c."
    )
    notes.append("Discovery-only: any useful overlay needs a frozen forward validator before promotion.")
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
        "# v28 Danger-Zone FV Calibration",
        "",
        f"- Surface: `{report.get('surface')}`",
        f"- Rows/markets: `{report.get('rows')}/{report.get('markets')}`",
        f"- Best overlay: `{report.get('best_overlay')}`",
        "",
        "## Current Read",
        "",
    ]
    for note in report.get("interpretation") or []:
        lines.append(f"- {note}")
    lines.extend([
        "",
        "## Ranking",
        "",
        "| rank | overlay | settled | W/L | avg p | win rate | brier | d brier | logloss | d logloss | blockers |",
        "|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---|",
    ])
    for idx, row in enumerate(report.get("ranked") or [], start=1):
        lines.append(
            f"| {idx} | `{row.get('overlay')}` | {row.get('settled')} | {row.get('wins')}/{row.get('losses')} | "
            f"{fmt(row.get('avg_p'))} | {fmt(row.get('win_rate'))} | {fmt(row.get('avg_brier'))} | "
            f"{fmt(row.get('brier_delta_vs_raw'))} | {fmt(row.get('avg_logloss'))} | "
            f"{fmt(row.get('logloss_delta_vs_raw'))} | {', '.join(row.get('blockers') or []) or 'none'} |"
        )
    lines.extend(["", "## Buckets", "", "| bucket | rows | W/L | win rate | avg raw p | avg book p | actual c | hold c |", "|---|---:|---:|---:|---:|---:|---:|---:|"])
    for row in report.get("buckets") or []:
        lines.append(
            f"| `{row.get('bucket')}` | {row.get('rows')} | {row.get('wins')}/{row.get('losses')} | "
            f"{fmt(row.get('win_rate'))} | {fmt(row.get('avg_raw_p'))} | {fmt(row.get('avg_book_p'))} | "
            f"{fmt(row.get('actual_gross_cents'))} | {fmt(row.get('hold_gross_cents'))} |"
        )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    report = build_report()
    write_md(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
