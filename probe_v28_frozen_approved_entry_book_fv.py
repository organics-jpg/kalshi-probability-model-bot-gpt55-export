"""Frozen approved-entry book-anchor FV calibration challenger.

Research-only; no live bot changes or orders.

Physics hypothesis:
    The v28 decision engine may be good at selecting direction, while its raw
    probability is too confident once the market has already priced the touch.
    On actual approved entries, executable book probability may be a better
    terminal FV calibration anchor than raw v28 probability.

This freezes that hypothesis and scores only future v28-approved rows.
"""
from __future__ import annotations

import json
import math
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from probe_v28_forward_physics_registry import build_rows as approved_entry_rows
from probe_v28_raw_entry_calibrated_probability import OVERLAYS


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
STATE_JSON = OUT_DIR / "v28_frozen_approved_entry_book_fv_state.json"
OUT_JSON = OUT_DIR / "v28_frozen_approved_entry_book_fv_latest.json"
OUT_MD = OUT_DIR / "v28_frozen_approved_entry_book_fv_latest.md"

MIN_SETTLED = 30
OVERLAY_NAMES = [
    "raw_probability",
    "book_probability",
    "noise_shrink_light_probability",
]


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
    return payload if isinstance(payload, dict) else {}


def load_or_create_state() -> dict[str, Any]:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    if STATE_JSON.exists():
        state = load_json(STATE_JSON)
        if state.get("freeze_ts_utc"):
            return state
    state = {
        "freeze_ts_utc": utc_now_iso(),
        "entry_surface": "actual_v28_approved_entries_only",
        "candidate": "book_probability",
        "overlays": OVERLAY_NAMES,
        "rule": "Compare book_probability against raw_probability only on future actual v28-approved entries.",
        "physics": "Raw v28 may select direction, while the executable book is a stronger calibration anchor after selection and fees.",
    }
    STATE_JSON.write_text(json.dumps(state, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return state


def parse_ts(value: Any) -> datetime | None:
    if not value:
        return None
    try:
        text = str(value).replace("Z", "+00:00")
        dt = datetime.fromisoformat(text)
    except ValueError:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def clamp_prob(value: float) -> float:
    return max(0.000001, min(0.999999, value))


def logloss(p: float, outcome: float) -> float:
    p = clamp_prob(p)
    return -(outcome * math.log(p) + (1.0 - outcome) * math.log(1.0 - p))


def avg(values: list[float]) -> float | None:
    return sum(values) / len(values) if values else None


def normalize_row(row: dict[str, Any]) -> dict[str, Any]:
    out = dict(row)
    if out.get("ask_prob") is None and out.get("ask_cents") is not None:
        try:
            out["ask_prob"] = float(out["ask_cents"]) / 100.0
        except (TypeError, ValueError):
            pass
    out["source"] = "approved_entry"
    return out


def future_rows(freeze_ts: str) -> list[dict[str, Any]]:
    freeze_dt = parse_ts(freeze_ts)
    rows = []
    for row in approved_entry_rows():
        entry_dt = parse_ts(row.get("entry_ts"))
        if freeze_dt is not None and entry_dt is not None and entry_dt < freeze_dt:
            continue
        rows.append(row)
    return rows


def score_overlay(rows: list[dict[str, Any]], overlay: str) -> dict[str, Any]:
    fn = OVERLAYS[overlay]
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
            "ask_cents": row.get("ask_cents"),
            "p_raw": row.get("p_side"),
        })
    briers = [float(row["brier"]) for row in scored]
    loglosses = [float(row["logloss"]) for row in scored]
    probs = [float(row["p"]) for row in scored]
    outcomes = [float(row["outcome"]) for row in scored]
    return {
        "overlay": overlay,
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
        "scored_rows": scored,
    }


def enrich(scores: list[dict[str, Any]], candidate: str) -> list[dict[str, Any]]:
    raw = next((row for row in scores if row.get("overlay") == "raw_probability"), {})
    raw_brier = raw.get("avg_brier")
    raw_logloss = raw.get("avg_logloss")
    out = []
    for row in scores:
        brier = row.get("avg_brier")
        loss = row.get("avg_logloss")
        enriched = {
            **{key: value for key, value in row.items() if key != "scored_rows"},
            "brier_delta_vs_raw": None if brier is None or raw_brier is None else float(brier) - float(raw_brier),
            "logloss_delta_vs_raw": None if loss is None or raw_logloss is None else float(loss) - float(raw_logloss),
        }
        blockers = []
        if int(enriched.get("settled") or 0) < MIN_SETTLED:
            blockers.append("settled_lt_30")
        if enriched.get("overlay") == candidate:
            if enriched["brier_delta_vs_raw"] is None or enriched["brier_delta_vs_raw"] >= 0.0:
                blockers.append("brier_not_better_than_raw")
            if enriched["logloss_delta_vs_raw"] is None or enriched["logloss_delta_vs_raw"] >= 0.0:
                blockers.append("logloss_not_better_than_raw")
        enriched["blockers"] = blockers
        out.append(enriched)
    out.sort(key=lambda row: (float(row.get("avg_brier") or 999.0), float(row.get("avg_logloss") or 999.0)))
    return out


def build_report() -> dict[str, Any]:
    state = load_or_create_state()
    rows = future_rows(str(state["freeze_ts_utc"]))
    scores = [score_overlay(rows, name) for name in state.get("overlays", OVERLAY_NAMES) if name in OVERLAYS]
    ranked = enrich(scores, str(state.get("candidate") or "book_probability"))
    candidate = next((row for row in ranked if row.get("overlay") == state.get("candidate")), {})
    return {
        "freeze": state,
        "future_entries": len(rows),
        "future_settled": sum(1 for row in rows if row.get("side_won") is not None),
        "ranked": ranked,
        "candidate": candidate,
        "candidate_live_ready": not candidate.get("blockers"),
        "interpretation": interpretation(state, candidate),
    }


def interpretation(state: dict[str, Any], candidate: dict[str, Any]) -> list[str]:
    return [
        f"Frozen approved-entry FV candidate {state.get('candidate')} has {candidate.get('settled')} future settled rows.",
        f"Brier/logloss deltas versus raw are {candidate.get('brier_delta_vs_raw')}/{candidate.get('logloss_delta_vs_raw')}.",
        "This is actual approved-entry calibration evidence only; it does not use rejected-actionable rows.",
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
    freeze = report.get("freeze") or {}
    lines = [
        "# v28 Frozen Approved-Entry Book FV",
        "",
        f"- Freeze timestamp UTC: `{freeze.get('freeze_ts_utc')}`",
        f"- Entry surface: `{freeze.get('entry_surface')}`",
        f"- Candidate: `{freeze.get('candidate')}`",
        f"- Future entries/settled: `{report.get('future_entries')}/{report.get('future_settled')}`",
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
