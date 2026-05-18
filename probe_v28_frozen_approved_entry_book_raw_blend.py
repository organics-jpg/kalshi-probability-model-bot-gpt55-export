"""Frozen approved-entry book/raw FV blend watch.

Research-only; no live bot changes or orders.

Diagnostic approved-entry evidence says the executable book is useful as a
humility anchor, but strict future conditional-book rows also show that raw v28
can be correct during high-confidence runs. This freezes smooth convex blends
instead of another brittle regime cutoff.
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
STATE_JSON = OUT_DIR / "v28_frozen_approved_entry_book_raw_blend_state.json"
OUT_JSON = OUT_DIR / "v28_frozen_approved_entry_book_raw_blend_latest.json"
OUT_MD = OUT_DIR / "v28_frozen_approved_entry_book_raw_blend_latest.md"

ALPHAS = [0.35, 0.50, 0.75]
PRIMARY_ALPHA = 0.50
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
        "primary_candidate": "book_raw_blend_alpha_0p50",
        "alpha_grid": ALPHAS,
        "rule": "p = book_probability + alpha * (raw_probability - book_probability)",
        "physics": (
            "Use the executable book as a humility anchor while retaining a "
            "continuous memory term from raw v28 when the model's conviction is "
            "physically supported. This avoids a hard book-vs-raw cutoff."
        ),
        "strict_forward_note": "Rows before this timestamp are diagnostic context only.",
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


def rows_by_time(freeze_ts: str, future: bool) -> list[dict[str, Any]]:
    freeze_dt = parse_ts(freeze_ts)
    rows: list[dict[str, Any]] = []
    for row in approved_entry_rows():
        entry_dt = parse_ts(row.get("entry_ts"))
        if freeze_dt is not None and entry_dt is not None:
            is_future = entry_dt >= freeze_dt
            if future != is_future:
                continue
        if row.get("side_won") is None:
            continue
        out = dict(row)
        if out.get("ask_prob") is None and out.get("ask_cents") is not None:
            ask_cents = as_float(out.get("ask_cents"))
            if ask_cents is not None:
                out["ask_prob"] = ask_cents / 100.0
        rows.append(out)
    return rows


def raw_probability(row: dict[str, Any]) -> float:
    return clamp_prob(float(OVERLAYS["raw_probability"](row)))


def book_probability(row: dict[str, Any]) -> float:
    return clamp_prob(float(OVERLAYS["book_probability"](row)))


def blend_probability(row: dict[str, Any], alpha: float) -> float:
    book_p = book_probability(row)
    raw_p = raw_probability(row)
    return clamp_prob(book_p + alpha * (raw_p - book_p))


def mean(values: list[float]) -> float | None:
    return sum(values) / len(values) if values else None


def score_overlay(rows: list[dict[str, Any]], name: str, alpha: float | None) -> dict[str, Any]:
    scored: list[dict[str, Any]] = []
    for row in rows:
        try:
            p = raw_probability(row) if alpha is None else blend_probability(row, alpha)
        except (KeyError, TypeError, ValueError):
            continue
        outcome = 1.0 if row.get("side_won") is True else 0.0
        scored.append({
            "p": p,
            "outcome": outcome,
            "won": row.get("side_won"),
            "brier": (p - outcome) ** 2,
            "logloss": logloss(p, outcome),
            "gross_cents": as_float(row.get("actual_gross_cents")) or 0.0,
        })
    wins = sum(1 for row in scored if row["won"] is True)
    losses = sum(1 for row in scored if row["won"] is False)
    return {
        "overlay": name,
        "alpha": alpha,
        "entries": len(rows),
        "settled": len(scored),
        "wins": wins,
        "losses": losses,
        "win_rate": None if not scored else wins / len(scored),
        "avg_p": mean([float(row["p"]) for row in scored]),
        "avg_brier": mean([float(row["brier"]) for row in scored]),
        "avg_logloss": mean([float(row["logloss"]) for row in scored]),
        "gross_cents": sum(float(row["gross_cents"]) for row in scored),
        "full_loss_cushion_estimate": int(sum(float(row["gross_cents"]) for row in scored) // 100)
        if sum(float(row["gross_cents"]) for row in scored) > 0
        else 0,
    }


def score_set(rows: list[dict[str, Any]]) -> dict[str, Any]:
    raw = score_overlay(rows, "raw_probability", None)
    raw_brier = as_float(raw.get("avg_brier"))
    raw_logloss = as_float(raw.get("avg_logloss"))
    ranked: list[dict[str, Any]] = [raw]
    for alpha in ALPHAS:
        row = score_overlay(rows, f"book_raw_blend_alpha_{str(alpha).replace('.', 'p')}", alpha)
        brier = as_float(row.get("avg_brier"))
        loss = as_float(row.get("avg_logloss"))
        row["brier_delta_vs_raw"] = None if brier is None or raw_brier is None else brier - raw_brier
        row["logloss_delta_vs_raw"] = None if loss is None or raw_logloss is None else loss - raw_logloss
        blockers = []
        if int(row.get("settled") or 0) < MIN_SETTLED:
            blockers.append("settled_lt_30")
        if row["brier_delta_vs_raw"] is None or row["brier_delta_vs_raw"] >= 0.0:
            blockers.append("brier_not_better_than_raw")
        if row["logloss_delta_vs_raw"] is None or row["logloss_delta_vs_raw"] >= 0.0:
            blockers.append("logloss_not_better_than_raw")
        row["blockers"] = blockers
        ranked.append(row)
    ranked = sorted(
        ranked,
        key=lambda row: (
            as_float(row.get("avg_brier")) if as_float(row.get("avg_brier")) is not None else 999.0,
            as_float(row.get("avg_logloss")) if as_float(row.get("avg_logloss")) is not None else 999.0,
        ),
    )
    primary = next((row for row in ranked if row.get("alpha") == PRIMARY_ALPHA), {})
    return {
        "entries": len(rows),
        "settled": sum(1 for row in rows if row.get("side_won") is not None),
        "ranked": ranked,
        "primary": primary,
    }


def build_report() -> dict[str, Any]:
    state = load_or_create_state()
    freeze_ts = str(state["freeze_ts_utc"])
    future = score_set(rows_by_time(freeze_ts, future=True))
    prefreeze = score_set(rows_by_time(freeze_ts, future=False))
    primary = future.get("primary") or {}
    return {
        "freeze": state,
        "future": future,
        "prefreeze_context": prefreeze,
        "candidate_summary": {
            "entries": primary.get("entries"),
            "settled": primary.get("settled"),
            "wins": primary.get("wins"),
            "losses": primary.get("losses"),
            "net_cents": primary.get("gross_cents"),
            "full_loss_cushion_estimate": primary.get("full_loss_cushion_estimate"),
            "brier_delta_vs_raw": primary.get("brier_delta_vs_raw"),
            "logloss_delta_vs_raw": primary.get("logloss_delta_vs_raw"),
        },
        "candidate_live_ready": not (primary.get("blockers") or []),
        "blockers": primary.get("blockers") or [],
        "interpretation": interpretation(state, future, prefreeze),
    }


def interpretation(
    state: dict[str, Any],
    future: dict[str, Any],
    prefreeze: dict[str, Any],
) -> list[str]:
    primary = future.get("primary") or {}
    pre = prefreeze.get("primary") or {}
    return [
        f"Frozen primary `{state.get('primary_candidate')}` has future entries/settled {future.get('entries')}/{future.get('settled')}.",
        f"Future primary Brier/logloss deltas versus raw are {primary.get('brier_delta_vs_raw')}/{primary.get('logloss_delta_vs_raw')}.",
        f"Pre-freeze primary deltas were {pre.get('brier_delta_vs_raw')}/{pre.get('logloss_delta_vs_raw')} over {prefreeze.get('settled')} settled rows.",
        f"Promotion blockers: {primary.get('blockers') or []}.",
        "Pre-freeze context motivates the blend only; future rows are the validation evidence.",
    ]


def fmt(value: Any) -> str:
    if value is None:
        return "None"
    if isinstance(value, float):
        return f"{value:.6f}"
    return str(value)


def write_md(report: dict[str, Any]) -> None:
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8")
    freeze = report["freeze"]
    lines = [
        "# v28 Frozen Approved-Entry Book/Raw Blend FV",
        "",
        "Research-only frozen FV calibration watch for actual v28-approved entries.",
        "",
        f"- Freeze timestamp UTC: `{freeze.get('freeze_ts_utc')}`",
        f"- Primary candidate: `{freeze.get('primary_candidate')}`",
        f"- Rule: `{freeze.get('rule')}`",
        f"- Physics: {freeze.get('physics')}",
        f"- Candidate live ready: `{report.get('candidate_live_ready')}`",
        f"- Blockers: `{', '.join(report.get('blockers') or []) or 'none'}`",
        "",
        "## Interpretation",
        "",
    ]
    for note in report.get("interpretation") or []:
        lines.append(f"- {note}")
    for section, key in (("Future Validation", "future"), ("Pre-Freeze Context", "prefreeze_context")):
        lines.extend([
            "",
            f"## {section}",
            "",
            "| rank | overlay | settled | W/L | avg p | brier | d brier | logloss | d logloss | gross c | blockers |",
            "|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---|",
        ])
        for idx, row in enumerate(report[key].get("ranked") or [], start=1):
            lines.append(
                f"| {idx} | `{row.get('overlay')}` | {row.get('settled')} | "
                f"{row.get('wins')}/{row.get('losses')} | {fmt(row.get('avg_p'))} | "
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
