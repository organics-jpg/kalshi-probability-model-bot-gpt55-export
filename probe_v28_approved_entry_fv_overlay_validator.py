"""Approved-entry-only FV overlay validator for v28.

Research-only; no live bot changes or orders.

Several broad candidate reports include actionable rejected rows. This probe
scores FV probability overlays only on rows the live/shadow v28 strategy
actually approved, so we have a clean live-evidence calibration view.
"""
from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any

from probe_v28_forward_physics_registry import build_rows as approved_entry_rows
from probe_v28_raw_entry_calibrated_probability import OVERLAYS


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
OUT_JSON = OUT_DIR / "v28_approved_entry_fv_overlay_validator_latest.json"
OUT_MD = OUT_DIR / "v28_approved_entry_fv_overlay_validator_latest.md"

MIN_SETTLED = 30
OVERLAY_NAMES = [
    "raw_probability",
    "entry_conditioned_plus03_probability",
    "entry_conditioned_plus05_probability",
    "entry_conditioned_logit125_probability",
    "entry_conditioned_logit125_p60_only_probability",
    "entry_conditioned_plus05_noise_attenuated_probability",
    "noise_shrink_light_probability",
    "book_probability",
]


def clamp_prob(value: float) -> float:
    return max(0.000001, min(0.999999, value))


def logloss(p: float, outcome: float) -> float:
    p = clamp_prob(p)
    return -(outcome * math.log(p) + (1.0 - outcome) * math.log(1.0 - p))


def avg(values: list[float]) -> float | None:
    return sum(values) / len(values) if values else None


def normalize_row(row: dict[str, Any]) -> dict[str, Any]:
    out = dict(row)
    ask = out.get("ask_prob")
    if ask is None and out.get("ask_cents") is not None:
        try:
            out["ask_prob"] = float(out["ask_cents"]) / 100.0
        except (TypeError, ValueError):
            pass
    out["source"] = "approved_entry"
    return out


def score_overlay(rows: list[dict[str, Any]], name: str) -> dict[str, Any]:
    fn = OVERLAYS[name]
    scored = []
    for raw in rows:
        if raw.get("side_won") is None:
            continue
        row = normalize_row(raw)
        try:
            p = clamp_prob(float(fn(row)))
        except (KeyError, TypeError, ValueError):
            continue
        outcome = 1.0 if row.get("side_won") is True else 0.0
        scored.append({
            "market": row.get("market"),
            "side": row.get("side"),
            "p": p,
            "outcome": outcome,
            "won": row.get("side_won"),
            "brier": (p - outcome) ** 2,
            "logloss": logloss(p, outcome),
            "actual_gross_cents": row.get("actual_gross_cents"),
        })
    briers = [float(row["brier"]) for row in scored]
    loglosses = [float(row["logloss"]) for row in scored]
    outcomes = [float(row["outcome"]) for row in scored]
    probs = [float(row["p"]) for row in scored]
    return {
        "overlay": name,
        "entries": len(rows),
        "settled": len(scored),
        "wins": sum(1 for row in scored if row.get("won") is True),
        "losses": sum(1 for row in scored if row.get("won") is False),
        "avg_p": avg(probs),
        "win_rate": avg(outcomes),
        "calibration_error": None if avg(probs) is None or avg(outcomes) is None else avg(outcomes) - avg(probs),
        "avg_brier": avg(briers),
        "avg_logloss": avg(loglosses),
        "gross_cents": sum(float(row.get("actual_gross_cents") or 0.0) for row in scored),
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


def build_report() -> dict[str, Any]:
    rows = approved_entry_rows()
    scores = [score_overlay(rows, name) for name in OVERLAY_NAMES if name in OVERLAYS]
    ranked = enrich(scores)
    return {
        "entry_surface": "approved_v28_entries_only",
        "rows": len(rows),
        "settled": sum(1 for row in rows if row.get("side_won") is not None),
        "ranked": ranked,
        "best_overlay": ranked[0].get("overlay") if ranked else None,
        "interpretation": current_read(ranked),
    }


def current_read(ranked: list[dict[str, Any]]) -> list[str]:
    notes = []
    if ranked:
        best = ranked[0]
        notes.append(
            f"Best approved-entry overlay by Brier is {best['overlay']} with Brier delta {best.get('brier_delta_vs_raw')}."
        )
    if ranked and int(ranked[0].get("settled") or 0) < MIN_SETTLED:
        notes.append("Approved-entry sample is still below 30 settled rows, so this is diagnostic only.")
    raw = next((row for row in ranked if row.get("overlay") == "raw_probability"), {})
    if raw:
        notes.append(
            f"Raw approved-entry calibration error is {raw.get('calibration_error')} with win rate {raw.get('win_rate')} and avg p {raw.get('avg_p')}."
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
        "# v28 Approved-Entry FV Overlay Validator",
        "",
        "FV overlay calibration using only v28-approved entry rows.",
        "",
        f"- Rows/settled: `{report.get('rows')}/{report.get('settled')}`",
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
        "| rank | overlay | settled | W/L | avg p | win rate | cal err | brier | d brier | logloss | d logloss | gross c | blockers |",
        "|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|",
    ])
    for idx, row in enumerate(report.get("ranked") or [], start=1):
        lines.append(
            f"| {idx} | `{row.get('overlay')}` | {row.get('settled')} | {row.get('wins')}/{row.get('losses')} | "
            f"{fmt(row.get('avg_p'))} | {fmt(row.get('win_rate'))} | {fmt(row.get('calibration_error'))} | "
            f"{fmt(row.get('avg_brier'))} | {fmt(row.get('brier_delta_vs_raw'))} | "
            f"{fmt(row.get('avg_logloss'))} | {fmt(row.get('logloss_delta_vs_raw'))} | "
            f"{fmt(row.get('gross_cents'))} | {', '.join(row.get('blockers') or []) or 'none'} |"
        )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    report = build_report()
    write_md(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
