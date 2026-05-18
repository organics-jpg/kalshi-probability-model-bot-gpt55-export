"""Frozen recross-aware book-shrink FV validator.

Research-only; no live bot changes or orders.

Physics hypothesis:
When raw v28 strongly disagrees with the executable book while recross hazard is
high, the book may be pricing path instability that static fair value misses.
This validator freezes that idea and scores only future rows after its own
timestamp.
"""
from __future__ import annotations

import json
import math
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from probe_v28_frozen_book_plus05_no_cheap_yes_entry import policy_match
from probe_v28_shadow_entry_policy_bakeoff import observation_pool


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
STATE_JSON = OUT_DIR / "v28_frozen_recross_book_shrink_fv_state.json"
OUT_JSON = OUT_DIR / "v28_frozen_recross_book_shrink_fv_latest.json"
OUT_MD = OUT_DIR / "v28_frozen_recross_book_shrink_fv_latest.md"

ENTRY_POLICY = "book_plus_05_no_cheap_yes_boundary"
VARIANT = "recross_book_shrink_065_delta08"
MIN_SETTLED = 30


def load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
    return payload if isinstance(payload, dict) else {}


def as_float(value: Any) -> float | None:
    if value is None or value == "":
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def parse_ts(value: Any) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except ValueError:
        return None


def clipped(p: float) -> float:
    return min(0.999, max(0.001, p))


def brier(p: float, y: float) -> float:
    return (clipped(p) - y) ** 2


def logloss(p: float, y: float) -> float:
    p = clipped(p)
    return -(y * math.log(p) + (1.0 - y) * math.log(1.0 - p))


def ensure_state() -> dict[str, Any]:
    state = load_json(STATE_JSON)
    if state:
        return state
    state = {
        "freeze_ts_utc": datetime.now(UTC).isoformat(),
        "entry_policy": ENTRY_POLICY,
        "variant": VARIANT,
        "rule": "On book_plus_05_no_cheap_yes_boundary rows, shrink raw v28 75% toward book when recross_hazard >= 0.65 and abs(raw-book) >= 0.08; otherwise keep raw.",
        "physics": "High recross plus large raw/book disagreement means the executable book can encode path instability not captured by static boundary FV.",
    }
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    STATE_JSON.write_text(json.dumps(state, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return state


def first_per_market(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    picked: dict[str, dict[str, Any]] = {}
    for row in sorted(rows, key=lambda item: str(item.get("ts_wall") or "")):
        if not policy_match(row):
            continue
        market = str(row.get("market") or "")
        if market and market not in picked:
            picked[market] = row
    return [picked[market] for market in sorted(picked)]


def recross_book_shrink(row: dict[str, Any]) -> float | None:
    raw = as_float(row.get("p_side"))
    book = as_float(row.get("ask_prob"))
    recross = as_float(row.get("recross_hazard_score"))
    if raw is None or book is None:
        return None
    if recross is not None and recross >= 0.65 and abs(raw - book) >= 0.08:
        return clipped(0.25 * raw + 0.75 * book)
    return clipped(raw)


def score_variant(rows: list[dict[str, Any]]) -> dict[str, Any]:
    settled = [row for row in rows if row.get("side_won") is not None]
    raw_pairs = []
    variant_pairs = []
    adjusted = 0
    for row in settled:
        raw = as_float(row.get("p_side"))
        variant = recross_book_shrink(row)
        if raw is None or variant is None:
            continue
        y = 1.0 if row.get("side_won") is True else 0.0
        raw_pairs.append((raw, y))
        variant_pairs.append((variant, y))
        if abs(raw - variant) > 1e-12:
            adjusted += 1
    if not raw_pairs or not variant_pairs:
        return {"rows": len(settled), "adjusted_rows": adjusted}
    raw_brier = sum(brier(p, y) for p, y in raw_pairs) / len(raw_pairs)
    variant_brier = sum(brier(p, y) for p, y in variant_pairs) / len(variant_pairs)
    raw_logloss = sum(logloss(p, y) for p, y in raw_pairs) / len(raw_pairs)
    variant_logloss = sum(logloss(p, y) for p, y in variant_pairs) / len(variant_pairs)
    return {
        "rows": len(variant_pairs),
        "adjusted_rows": adjusted,
        "raw_brier": raw_brier,
        "variant_brier": variant_brier,
        "brier_delta_vs_raw": variant_brier - raw_brier,
        "raw_logloss": raw_logloss,
        "variant_logloss": variant_logloss,
        "logloss_delta_vs_raw": variant_logloss - raw_logloss,
    }


def summarize_entries(rows: list[dict[str, Any]], denominator: int) -> dict[str, Any]:
    settled = [row for row in rows if row.get("side_won") is not None]
    gross = sum(float(row.get("gross_cents") or 0.0) for row in settled)
    return {
        "entries": len(rows),
        "settled": len(settled),
        "wins": sum(1 for row in settled if row.get("side_won") is True),
        "losses": sum(1 for row in settled if row.get("side_won") is False),
        "gross_cents": gross,
        "coverage_pct": (len({row.get("market") for row in rows if row.get("market")}) / denominator * 100.0) if denominator else 0.0,
        "approved_entry_count": sum(1 for row in rows if row.get("source") == "approved_entry"),
        "simulated_or_rejected_count": sum(1 for row in rows if row.get("source") == "rejected_actionable"),
    }


def build_report() -> dict[str, Any]:
    state = ensure_state()
    freeze_ts = parse_ts(state.get("freeze_ts_utc"))
    future_rows = [
        row for row in observation_pool()
        if parse_ts(row.get("ts_wall")) is not None and freeze_ts is not None and parse_ts(row.get("ts_wall")) > freeze_ts
    ]
    denominator = len({row.get("market") for row in future_rows if row.get("market")})
    selected = first_per_market(future_rows)
    summary = summarize_entries(selected, denominator)
    score = score_variant(selected)
    blockers = []
    if int(score.get("rows") or 0) < MIN_SETTLED:
        blockers.append("settled_lt_30")
    if score.get("brier_delta_vs_raw") is None or float(score.get("brier_delta_vs_raw") or 0.0) >= 0.0:
        blockers.append("brier_not_better_than_raw")
    if score.get("logloss_delta_vs_raw") is None or float(score.get("logloss_delta_vs_raw") or 0.0) >= 0.0:
        blockers.append("logloss_not_better_than_raw")
    return {
        "freeze": state,
        "future_denominator_markets": denominator,
        "summary": summary,
        "score": score,
        "blockers": blockers,
        "fv_ready": not blockers,
        "rows": selected,
        "interpretation": [
            f"{VARIANT} has {summary.get('entries')} future entries and {score.get('rows')} settled rows.",
            f"Adjusted settled rows: {score.get('adjusted_rows')}; Brier/logloss deltas: {score.get('brier_delta_vs_raw')}/{score.get('logloss_delta_vs_raw')}.",
            f"Blockers: {', '.join(blockers) if blockers else 'none'}.",
        ],
    }


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
    summary = report.get("summary") or {}
    score = report.get("score") or {}
    lines = [
        "# v28 Frozen Recross Book-Shrink FV",
        "",
        "Future-only FV challenger. No live orders.",
        "",
        f"- FV ready: `{report.get('fv_ready')}`",
        f"- Freeze timestamp: `{freeze.get('freeze_ts_utc')}`",
        f"- Entry policy: `{freeze.get('entry_policy')}`",
        f"- Variant: `{freeze.get('variant')}`",
        f"- Future denominator markets: `{report.get('future_denominator_markets')}`",
        f"- Entries/settled/W-L/gross: `{summary.get('entries')}/{summary.get('settled')}/{summary.get('wins')}-{summary.get('losses')}/{fmt(summary.get('gross_cents'))}`",
        f"- Coverage: `{fmt(summary.get('coverage_pct'))}%`",
        f"- Approved/simulated: `{summary.get('approved_entry_count')}/{summary.get('simulated_or_rejected_count')}`",
        f"- Adjusted settled rows: `{score.get('adjusted_rows')}`",
        f"- Brier/logloss delta vs raw: `{fmt(score.get('brier_delta_vs_raw'))}/{fmt(score.get('logloss_delta_vs_raw'))}`",
        f"- Blockers: `{', '.join(report.get('blockers') or []) or 'none'}`",
        "",
        "## Interpretation",
        "",
    ]
    for note in report.get("interpretation") or []:
        lines.append(f"- {note}")
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    report = build_report()
    write_md(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
