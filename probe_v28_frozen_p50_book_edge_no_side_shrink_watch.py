"""Frozen watch for p50 book-edge with NO-side size shrink.

Research-only; no live bot changes or orders.

Child born from the p50 book-edge source/failure drilldown. The physical
argument is side asymmetry: the frozen parent was broad and positive, but NO
rows were net negative while YES rows carried the PnL. This watch keeps broad
participation by taking the same entry rule while quarter-sizing NO-side rows.
"""
from __future__ import annotations

import json
import math
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from probe_v28_frozen_p50_book_edge_entry import policy_match, settled
from probe_v28_shadow_entry_policy_bakeoff import observation_pool


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
STATE_JSON = OUT_DIR / "v28_frozen_p50_book_edge_no_side_shrink_watch_state.json"
OUT_JSON = OUT_DIR / "v28_frozen_p50_book_edge_no_side_shrink_watch_latest.json"
OUT_MD = OUT_DIR / "v28_frozen_p50_book_edge_no_side_shrink_watch_latest.md"

POLICY = "p50_book_plus_05_edge_nonnegative_quarter_no_side"
MIN_SETTLED = 30
TARGET_COVERAGE_MIN = 75.0
TARGET_COVERAGE_MAX = 90.0
MAX_WEIGHTED_REJECTED_SHARE = 0.35
MIN_FULL_LOSS_CUSHION = 3


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


def ensure_state() -> dict[str, Any]:
    state = load_json(STATE_JSON)
    if state:
        return state
    state = {
        "candidate": POLICY,
        "freeze_ts_utc": datetime.now(UTC).isoformat(),
        "parent": "p50_book_plus_05_edge_nonnegative",
        "entry_rule": "ask 1-90c, p_side >= 0.50, v28_minus_ask_prob >= 0.05, edge_cents >= 0",
        "size_rule": "YES rows weight 1.0; NO rows weight 0.25",
        "physics": "Parent p50 book-edge was broad and positive, but NO-side rows were net negative. Quarter-sizing NO tests whether side-aware risk shrink preserves coverage while improving drawdown cushion.",
        "source": "probe_v28_p50_book_edge_source_failure_drilldown.py",
    }
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    STATE_JSON.write_text(json.dumps(state, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return state


def row_weight(row: dict[str, Any]) -> float:
    return 0.25 if row.get("side") == "no" else 1.0


def first_per_market(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    picked: dict[str, dict[str, Any]] = {}
    for row in sorted(rows, key=lambda item: str(item.get("ts_wall") or "")):
        if not policy_match(row):
            continue
        market = str(row.get("market") or "")
        if market and market not in picked:
            picked[market] = row
    return [picked[market] for market in sorted(picked)]


def summarize(rows: list[dict[str, Any]], denominator_markets: int) -> dict[str, Any]:
    settled_rows = [row for row in rows if settled(row)]
    weighted_gross = sum((as_float(row.get("gross_cents")) or 0.0) * row_weight(row) for row in settled_rows)
    approved_weight = sum(row_weight(row) for row in rows if row.get("source") == "approved_entry")
    rejected_weight = sum(row_weight(row) for row in rows if row.get("source") == "rejected_actionable")
    total_weight = approved_weight + rejected_weight
    markets = {row.get("market") for row in rows if row.get("market")}
    yes_rows = [row for row in rows if row.get("side") == "yes"]
    no_rows = [row for row in rows if row.get("side") == "no"]
    return {
        "entries": len(rows),
        "effective_entries": sum(row_weight(row) for row in rows),
        "settled": len(settled_rows),
        "wins": sum(1 for row in settled_rows if row.get("side_won") is True),
        "losses": sum(1 for row in settled_rows if row.get("side_won") is False),
        "weighted_gross_cents": weighted_gross,
        "avg_weighted_gross_cents": weighted_gross / sum(row_weight(row) for row in settled_rows) if settled_rows else None,
        "coverage_pct": (len(markets) / denominator_markets * 100.0) if denominator_markets else 0.0,
        "approved_entry_count": sum(1 for row in rows if row.get("source") == "approved_entry"),
        "rejected_actionable_count": sum(1 for row in rows if row.get("source") == "rejected_actionable"),
        "weighted_rejected_actionable_share": rejected_weight / total_weight if total_weight else None,
        "yes_entries": len(yes_rows),
        "no_entries": len(no_rows),
        "yes_weighted_gross_cents": sum((as_float(row.get("gross_cents")) or 0.0) for row in yes_rows if settled(row)),
        "no_weighted_gross_cents": sum((as_float(row.get("gross_cents")) or 0.0) * row_weight(row) for row in no_rows if settled(row)),
        "full_loss_cushion": math.floor(weighted_gross / 100.0) if weighted_gross > 0 else 0,
    }


def blocker_list(summary: dict[str, Any]) -> list[str]:
    blockers = []
    if int(summary.get("settled") or 0) < MIN_SETTLED:
        blockers.append("settled_lt_30")
    coverage = as_float(summary.get("coverage_pct"))
    if coverage is None or coverage < TARGET_COVERAGE_MIN:
        blockers.append("coverage_too_low")
    elif coverage > TARGET_COVERAGE_MAX:
        blockers.append("coverage_too_high")
    if (as_float(summary.get("weighted_gross_cents")) or 0.0) <= 0:
        blockers.append("weighted_gross_not_positive")
    share = as_float(summary.get("weighted_rejected_actionable_share"))
    if share is None or share > MAX_WEIGHTED_REJECTED_SHARE:
        blockers.append("weighted_rejected_actionable_share_gt_35pct")
    if int(summary.get("full_loss_cushion") or 0) < MIN_FULL_LOSS_CUSHION:
        blockers.append("full_loss_cushion_lt_3")
    return blockers


def build_report() -> dict[str, Any]:
    state = ensure_state()
    freeze_ts = parse_ts(state.get("freeze_ts_utc"))
    all_rows = observation_pool()
    future_rows = [
        row for row in all_rows
        if parse_ts(row.get("ts_wall")) is not None
        and freeze_ts is not None
        and parse_ts(row.get("ts_wall")) > freeze_ts
    ]
    denominator_markets = len({row.get("market") for row in future_rows if row.get("market")})
    candidate_rows = first_per_market(future_rows)
    summary = summarize(candidate_rows, denominator_markets)
    blockers = blocker_list(summary)
    return {
        "generated_at_utc": datetime.now(UTC).isoformat(),
        "freeze": state,
        "future_denominator_markets": denominator_markets,
        "summary": summary,
        "blockers": blockers,
        "candidate_live_ready": not blockers,
        "sample_markets": [row.get("market") for row in candidate_rows[:10]],
        "rows": candidate_rows,
        "interpretation": [
            f"Frozen {POLICY} has {summary.get('entries')} post-birth entries across {denominator_markets} future markets.",
            f"Weighted gross/coverage/source share are {summary.get('weighted_gross_cents')}c/{summary.get('coverage_pct')}%/{summary.get('weighted_rejected_actionable_share')}.",
            f"Blockers: {', '.join(blockers) if blockers else 'none'}.",
            "This is a size-shrink watch only; live testing still requires the controlled live-test gate.",
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
    summary = report.get("summary") or {}
    freeze = report.get("freeze") or {}
    lines = [
        "# v28 Frozen p50 Book-Edge NO-Side Shrink Watch",
        "",
        "Research-only frozen child candidate. No live orders.",
        "",
        f"- Candidate live-ready: `{report.get('candidate_live_ready')}`",
        f"- Freeze timestamp: `{freeze.get('freeze_ts_utc')}`",
        f"- Entry rule: `{freeze.get('entry_rule')}`",
        f"- Size rule: `{freeze.get('size_rule')}`",
        f"- Future denominator markets: `{report.get('future_denominator_markets')}`",
        f"- Entries/effective/settled/W-L: `{summary.get('entries')}/{fmt(summary.get('effective_entries'))}/{summary.get('settled')}/{summary.get('wins')}-{summary.get('losses')}`",
        f"- Weighted gross / avg weighted gross: `{fmt(summary.get('weighted_gross_cents'))}/{fmt(summary.get('avg_weighted_gross_cents'))}`",
        f"- Coverage: `{fmt(summary.get('coverage_pct'))}%`",
        f"- Approved/rejected/weighted rejected share: `{summary.get('approved_entry_count')}/{summary.get('rejected_actionable_count')}/{fmt(summary.get('weighted_rejected_actionable_share'))}`",
        f"- YES/NO entries and weighted gross: `{summary.get('yes_entries')}/{summary.get('no_entries')}/{fmt(summary.get('yes_weighted_gross_cents'))}/{fmt(summary.get('no_weighted_gross_cents'))}`",
        f"- Full-loss cushion: `{summary.get('full_loss_cushion')}`",
        f"- Blockers: `{', '.join(report.get('blockers') or []) or 'none'}`",
        "",
        "## Interpretation",
        "",
    ]
    for note in report.get("interpretation") or []:
        lines.append(f"- {note}")
    lines.extend(["", "## Sample Markets", ""])
    for market in report.get("sample_markets") or []:
        lines.append(f"- `{market}`")
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    report = build_report()
    write_md(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
