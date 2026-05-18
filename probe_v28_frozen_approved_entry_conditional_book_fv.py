"""Frozen conditional book-anchor FV for actual v28-approved entries.

Research-only; no live bot changes or orders.

Frozen hypothesis:
    The executable book is a useful humility anchor when raw v28 is most likely
    to be overconfident: NO side, late entries, or rows where the book discounts
    raw by at least 10 percentage points. For high-confidence expensive YES
    entries, raw v28 may preserve useful conviction better than a blanket book
    anchor.

This file freezes that rule and scores only future actual v28-approved entries
for promotion evidence. It also reports pre-freeze context separately so the
physical motivation is visible without counting it as validation.
"""
from __future__ import annotations

import json
import math
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

from probe_v28_forward_physics_registry import build_rows as approved_entry_rows
from probe_v28_raw_entry_calibrated_probability import OVERLAYS


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
STATE_JSON = OUT_DIR / "v28_frozen_approved_entry_conditional_book_fv_state.json"
OUT_JSON = OUT_DIR / "v28_frozen_approved_entry_conditional_book_fv_latest.json"
OUT_MD = OUT_DIR / "v28_frozen_approved_entry_conditional_book_fv_latest.md"

MIN_SETTLED = 30


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
        "candidate": "conditional_book_no_late_discount",
        "rule": "Use book_probability if side=no OR seconds_to_close<240 OR raw_probability-book_probability>=0.10; otherwise use raw_probability.",
        "physics": "Book anchoring should act as humility under late/NO/market-discounted overconfidence while preserving raw conviction on expensive high-confidence YES rows.",
        "min_settled": MIN_SETTLED,
        "source_attribution": "v28_approved_entry_book_fv_regime_attribution_latest",
    }
    STATE_JSON.write_text(json.dumps(state, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return state


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


def as_float(value: Any) -> float | None:
    if value is None or value == "":
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def clamp_prob(value: float) -> float:
    return max(0.000001, min(0.999999, value))


def logloss(p: float, outcome: float) -> float:
    p = clamp_prob(p)
    return -(outcome * math.log(p) + (1.0 - outcome) * math.log(1.0 - p))


def normalize_row(row: dict[str, Any]) -> dict[str, Any]:
    out = dict(row)
    if out.get("ask_prob") is None and out.get("ask_cents") is not None:
        ask_cents = as_float(out.get("ask_cents"))
        if ask_cents is not None:
            out["ask_prob"] = ask_cents / 100.0
    out["source"] = "approved_entry"
    return out


def rows_by_time(freeze_ts: str, future: bool) -> list[dict[str, Any]]:
    freeze_dt = parse_ts(freeze_ts)
    rows = []
    for row in approved_entry_rows():
        entry_dt = parse_ts(row.get("entry_ts"))
        if freeze_dt is not None and entry_dt is not None:
            is_future = entry_dt >= freeze_dt
            if future != is_future:
                continue
        if row.get("side_won") is None:
            continue
        rows.append(normalize_row(row))
    return rows


def raw_probability(row: dict[str, Any]) -> float:
    return clamp_prob(float(OVERLAYS["raw_probability"](row)))


def book_probability(row: dict[str, Any]) -> float:
    return clamp_prob(float(OVERLAYS["book_probability"](row)))


def conditional_book_probability(row: dict[str, Any]) -> float:
    raw_p = raw_probability(row)
    book_p = book_probability(row)
    stc = as_float(row.get("seconds_to_close"))
    use_book = (
        row.get("side") == "no"
        or (stc is not None and stc < 240.0)
        or raw_p - book_p >= 0.10
    )
    return book_p if use_book else raw_p


OVERLAY_FNS: dict[str, Callable[[dict[str, Any]], float]] = {
    "raw_probability": raw_probability,
    "book_probability": book_probability,
    "conditional_book_no_late_discount": conditional_book_probability,
}


def mean(values: list[float]) -> float | None:
    return sum(values) / len(values) if values else None


def score(rows: list[dict[str, Any]], overlay: str) -> dict[str, Any]:
    fn = OVERLAY_FNS[overlay]
    scored = []
    for row in rows:
        try:
            p = fn(row)
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
            "gross_cents": row.get("actual_gross_cents"),
        })
    wins = sum(1 for row in scored if row.get("won") is True)
    losses = sum(1 for row in scored if row.get("won") is False)
    return {
        "overlay": overlay,
        "entries": len(rows),
        "settled": len(scored),
        "wins": wins,
        "losses": losses,
        "win_rate": None if not scored else wins / len(scored),
        "avg_p": mean([float(row["p"]) for row in scored]),
        "avg_brier": mean([float(row["brier"]) for row in scored]),
        "avg_logloss": mean([float(row["logloss"]) for row in scored]),
        "gross_cents": sum(float(row.get("gross_cents") or 0.0) for row in scored),
    }


def enrich(scores: list[dict[str, Any]], candidate: str) -> list[dict[str, Any]]:
    raw = next((row for row in scores if row["overlay"] == "raw_probability"), {})
    raw_brier = raw.get("avg_brier")
    raw_logloss = raw.get("avg_logloss")
    enriched = []
    for row in scores:
        brier = row.get("avg_brier")
        loss = row.get("avg_logloss")
        out = {
            **row,
            "brier_delta_vs_raw": None if brier is None or raw_brier is None else float(brier) - float(raw_brier),
            "logloss_delta_vs_raw": None if loss is None or raw_logloss is None else float(loss) - float(raw_logloss),
        }
        blockers = []
        if out["overlay"] == candidate:
            if int(out.get("settled") or 0) < MIN_SETTLED:
                blockers.append("settled_lt_30")
            if out["brier_delta_vs_raw"] is None or out["brier_delta_vs_raw"] >= 0.0:
                blockers.append("brier_not_better_than_raw")
            if out["logloss_delta_vs_raw"] is None or out["logloss_delta_vs_raw"] >= 0.0:
                blockers.append("logloss_not_better_than_raw")
        out["blockers"] = blockers
        enriched.append(out)
    return sorted(
        enriched,
        key=lambda row: (
            float(row.get("avg_brier") if row.get("avg_brier") is not None else 999.0),
            float(row.get("avg_logloss") if row.get("avg_logloss") is not None else 999.0),
        ),
    )


def score_set(rows: list[dict[str, Any]], candidate: str) -> dict[str, Any]:
    scores = [score(rows, name) for name in OVERLAY_FNS]
    ranked = enrich(scores, candidate)
    candidate_row = next((row for row in ranked if row["overlay"] == candidate), {})
    return {
        "entries": len(rows),
        "settled": sum(1 for row in rows if row.get("side_won") is not None),
        "ranked": ranked,
        "candidate": candidate_row,
    }


def build_report() -> dict[str, Any]:
    state = load_or_create_state()
    candidate = str(state["candidate"])
    future = score_set(rows_by_time(str(state["freeze_ts_utc"]), future=True), candidate)
    prefreeze_context = score_set(rows_by_time(str(state["freeze_ts_utc"]), future=False), candidate)
    candidate_future = future["candidate"]
    return {
        "freeze": state,
        "future": future,
        "prefreeze_context": prefreeze_context,
        "candidate_live_ready": not candidate_future.get("blockers"),
        "interpretation": interpretation(state, future, prefreeze_context),
    }


def interpretation(
    state: dict[str, Any],
    future: dict[str, Any],
    prefreeze_context: dict[str, Any],
) -> list[str]:
    candidate = future.get("candidate") or {}
    pre = prefreeze_context.get("candidate") or {}
    blockers = candidate.get("blockers") or []
    return [
        f"Frozen candidate `{state.get('candidate')}` has future entries/settled {future.get('entries')}/{future.get('settled')}.",
        f"Future Brier/logloss deltas versus raw are {candidate.get('brier_delta_vs_raw')}/{candidate.get('logloss_delta_vs_raw')}.",
        f"Pre-freeze context deltas were {pre.get('brier_delta_vs_raw')}/{pre.get('logloss_delta_vs_raw')} over {prefreeze_context.get('settled')} settled rows.",
        f"Promotion blockers: {', '.join(blockers) if blockers else 'none'}.",
        "Pre-freeze context is only motivation; future rows are the validation evidence.",
    ]


def fmt(value: Any) -> str:
    if value is None:
        return "None"
    if isinstance(value, float):
        return f"{value:.6f}"
    return str(value)


def write_ranking(lines: list[str], rows: list[dict[str, Any]]) -> None:
    lines.extend([
        "| rank | overlay | settled | W/L | avg p | brier | d brier | logloss | d logloss | gross c | blockers |",
        "|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---|",
    ])
    for idx, row in enumerate(rows, start=1):
        lines.append(
            f"| {idx} | `{row.get('overlay')}` | {row.get('settled')} | {row.get('wins')}/{row.get('losses')} | "
            f"{fmt(row.get('avg_p'))} | {fmt(row.get('avg_brier'))} | {fmt(row.get('brier_delta_vs_raw'))} | "
            f"{fmt(row.get('avg_logloss'))} | {fmt(row.get('logloss_delta_vs_raw'))} | "
            f"{fmt(row.get('gross_cents'))} | {', '.join(row.get('blockers') or []) or 'none'} |"
        )


def write_md(report: dict[str, Any]) -> None:
    freeze = report["freeze"]
    lines = [
        "# v28 Frozen Approved-Entry Conditional Book FV",
        "",
        f"- Freeze timestamp UTC: `{freeze.get('freeze_ts_utc')}`",
        f"- Candidate: `{freeze.get('candidate')}`",
        f"- Rule: `{freeze.get('rule')}`",
        f"- Physics: {freeze.get('physics')}",
        "",
        "## Interpretation",
        "",
    ]
    for note in report.get("interpretation") or []:
        lines.append(f"- {note}")
    lines.extend(["", "## Future Validation", ""])
    write_ranking(lines, report["future"]["ranked"])
    lines.extend(["", "## Pre-Freeze Context", ""])
    write_ranking(lines, report["prefreeze_context"]["ranked"])
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    report = build_report()
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_md(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
