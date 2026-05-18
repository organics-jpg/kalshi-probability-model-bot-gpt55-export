"""Frozen forward validator for danger-zone FV calibration.

Research-only; no live bot changes or orders.

Validates fixed probability overlays on future actual v28-approved entries:
- raw_probability;
- book_probability;
- danger_to_book, which uses raw FV except in fixed danger zones where it
  falls back to executable book probability.
"""
from __future__ import annotations

import json
import math
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

from probe_v28_approved_entry_state_valves import book_prob, raw_book_gap, raw_prob, sorted_rows, with_state


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
STATE_JSON = OUT_DIR / "v28_frozen_danger_zone_fv_calibration_state.json"
OUT_JSON = OUT_DIR / "v28_frozen_danger_zone_fv_calibration_latest.json"
OUT_MD = OUT_DIR / "v28_frozen_danger_zone_fv_calibration_latest.md"

ENTRY_SURFACE = "actual_v28_approved_entries_only"
MIN_SETTLED = 30


def parse_ts(value: Any) -> datetime:
    if not value:
        return datetime.min.replace(tzinfo=timezone.utc)
    try:
        dt = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except ValueError:
        return datetime.min.replace(tzinfo=timezone.utc)
    return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)


def load_or_create_state() -> dict[str, Any]:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    if STATE_JSON.exists():
        try:
            payload = json.loads(STATE_JSON.read_text(encoding="utf-8"))
            if isinstance(payload, dict) and payload.get("freeze_ts_utc"):
                return payload
        except json.JSONDecodeError:
            pass
    state = {
        "freeze_ts_utc": datetime.now(timezone.utc).isoformat(),
        "entry_surface": ENTRY_SURFACE,
        "overlays": ["raw_probability", "book_probability", "danger_to_book"],
        "danger_rule": "raw-book gap > 0.30, or same-side reentry raw-book gap > 0.15",
    }
    STATE_JSON.write_text(json.dumps(state, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return state


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


def raw_probability(row: dict[str, Any]) -> float | None:
    return raw_prob(row)


def book_probability(row: dict[str, Any]) -> float | None:
    return book_prob(row)


def danger_to_book(row: dict[str, Any]) -> float | None:
    raw = raw_prob(row)
    book = book_prob(row)
    if raw is None:
        return None
    if danger_zone(row) and book is not None:
        return book
    return raw


OVERLAYS: dict[str, Callable[[dict[str, Any]], float | None]] = {
    "raw_probability": raw_probability,
    "book_probability": book_probability,
    "danger_to_book": danger_to_book,
}


def score_overlay(rows: list[dict[str, Any]], name: str, fn: Callable[[dict[str, Any]], float | None]) -> dict[str, Any]:
    scored = []
    for row in rows:
        p = fn(row)
        if p is None:
            continue
        outcome = 1.0 if row.get("side_won") is True else 0.0
        p = clamp_prob(float(p))
        scored.append({
            "p": p,
            "outcome": outcome,
            "won": row.get("side_won"),
            "brier": (p - outcome) ** 2,
            "logloss": logloss(p, outcome),
            "danger_zone": danger_zone(row),
        })
    briers = [float(row["brier"]) for row in scored]
    loglosses = [float(row["logloss"]) for row in scored]
    outcomes = [float(row["outcome"]) for row in scored]
    probs = [float(row["p"]) for row in scored]
    return {
        "overlay": name,
        "rows": len(scored),
        "wins": sum(1 for row in scored if row.get("won") is True),
        "losses": sum(1 for row in scored if row.get("won") is False),
        "avg_p": avg(probs),
        "win_rate": avg(outcomes),
        "avg_brier": avg(briers),
        "avg_logloss": avg(loglosses),
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
        if int(enriched.get("rows") or 0) < MIN_SETTLED:
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
    state = load_or_create_state()
    freeze_ts = parse_ts(state["freeze_ts_utc"])
    rows = [
        row for row in with_state(sorted_rows())
        if parse_ts(row.get("entry_ts")) >= freeze_ts
    ]
    ranked = enrich([score_overlay(rows, name, OVERLAYS[name]) for name in state["overlays"] if name in OVERLAYS])
    return {
        "freeze": state,
        "future_rows": len(rows),
        "future_markets": len({row.get("market") for row in rows}),
        "danger_rows": sum(1 for row in rows if danger_zone(row)),
        "ranked": ranked,
        "best_overlay": ranked[0].get("overlay") if ranked else None,
        "interpretation": current_read(ranked, rows),
    }


def current_read(ranked: list[dict[str, Any]], rows: list[dict[str, Any]]) -> list[str]:
    if not ranked:
        return ["No future rows yet."]
    best = ranked[0]
    return [
        f"Frozen danger-zone FV best overlay is {best.get('overlay')} with Brier/logloss deltas {best.get('brier_delta_vs_raw')}/{best.get('logloss_delta_vs_raw')}.",
        f"Future rows/danger rows: {len(rows)}/{sum(1 for row in rows if danger_zone(row))}.",
    ]


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
        "# v28 Frozen Danger-Zone FV Calibration",
        "",
        f"- Freeze timestamp UTC: `{(report.get('freeze') or {}).get('freeze_ts_utc')}`",
        f"- Future rows/markets/danger rows: `{report.get('future_rows')}/{report.get('future_markets')}/{report.get('danger_rows')}`",
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
        "| rank | overlay | rows | W/L | avg p | win rate | brier | d brier | logloss | d logloss | blockers |",
        "|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---|",
    ])
    for idx, row in enumerate(report.get("ranked") or [], start=1):
        lines.append(
            f"| {idx} | `{row.get('overlay')}` | {row.get('rows')} | {row.get('wins')}/{row.get('losses')} | "
            f"{fmt(row.get('avg_p'))} | {fmt(row.get('win_rate'))} | {fmt(row.get('avg_brier'))} | "
            f"{fmt(row.get('brier_delta_vs_raw'))} | {fmt(row.get('avg_logloss'))} | "
            f"{fmt(row.get('logloss_delta_vs_raw'))} | {', '.join(row.get('blockers') or []) or 'none'} |"
        )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    report = build_report()
    write_md(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
