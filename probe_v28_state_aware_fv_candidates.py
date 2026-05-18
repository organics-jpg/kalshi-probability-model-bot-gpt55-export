"""State-aware v28 FV candidates for forward shadow telemetry.

Hypothesis under test:
- First observations in a market/side can keep raw v28 geometry.
- Later observations and repeated entries should forget stale v28 confidence
  faster and anchor toward the executable book.

This script is research-only. It does not change live bot behavior.
"""
from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any, Callable

from probe_v28_rmt_regime_diagnostic import attach_regime_rows
from probe_v28_shadow_entry_policy_bakeoff import observation_pool


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
OUT_JSON = OUT_DIR / "v28_state_aware_fv_candidates_latest.json"
OUT_CSV = OUT_DIR / "v28_state_aware_fv_candidates_latest.csv"
OUT_MD = OUT_DIR / "v28_state_aware_fv_candidates_latest.md"


def clamp01(value: float) -> float:
    return max(0.000001, min(0.999999, value))


def as_float(value: Any) -> float | None:
    if value is None or value == "":
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def blend(p_v28: float, p_book: float, alpha_v28: float) -> float:
    return clamp01(alpha_v28 * p_v28 + (1.0 - alpha_v28) * p_book)


def enrich_state(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    seen_market_side: dict[tuple[str, str], int] = {}
    seen_market: dict[str, int] = {}
    enriched: list[dict[str, Any]] = []
    for row in sorted(rows, key=lambda item: str(item.get("ts_wall") or "")):
        market = str(row.get("market") or "")
        side = str(row.get("side") or "")
        key = (market, side)
        enriched_row = dict(row)
        enriched_row["market_observation_index"] = seen_market.get(market, 0)
        enriched_row["market_side_observation_index"] = seen_market_side.get(key, 0)
        enriched_row["is_first_market_observation"] = seen_market.get(market, 0) == 0
        enriched_row["is_first_market_side_observation"] = seen_market_side.get(key, 0) == 0
        enriched.append(enriched_row)
        if market:
            seen_market[market] = seen_market.get(market, 0) + 1
        if market and side:
            seen_market_side[key] = seen_market_side.get(key, 0) + 1
    return enriched


def p_raw(row: dict[str, Any]) -> float:
    return clamp01(float(row["p_side"]))


def p_book(row: dict[str, Any]) -> float:
    return clamp01(float(row["ask_prob"]))


def p_first_side_raw_later_book(row: dict[str, Any]) -> float:
    if row.get("is_first_market_side_observation") is True:
        return p_raw(row)
    return p_book(row)


def p_first_market_raw_later_book(row: dict[str, Any]) -> float:
    if row.get("is_first_market_observation") is True:
        return p_raw(row)
    return p_book(row)


def p_repeated_side_book_anchor(row: dict[str, Any]) -> float:
    p_v28 = p_raw(row)
    p_exec = p_book(row)
    side_idx = int(row.get("market_side_observation_index") or 0)
    if side_idx == 0:
        return p_v28
    if side_idx == 1:
        return blend(p_v28, p_exec, 0.50)
    return blend(p_v28, p_exec, 0.25)


def p_repeated_market_book_anchor(row: dict[str, Any]) -> float:
    p_v28 = p_raw(row)
    p_exec = p_book(row)
    market_idx = int(row.get("market_observation_index") or 0)
    if market_idx == 0:
        return p_v28
    if market_idx <= 3:
        return blend(p_v28, p_exec, 0.50)
    return blend(p_v28, p_exec, 0.25)


def p_rmt_aggressive_forget(row: dict[str, Any]) -> float:
    tag = str(row.get("spectral_tag") or "")
    if tag in {"spectral_dominant_factor", "spectral_noise", "insufficient_history"}:
        return p_book(row)
    return p_raw(row)


def p_rmt_repetition_forget(row: dict[str, Any]) -> float:
    tag = str(row.get("spectral_tag") or "")
    side_idx = int(row.get("market_side_observation_index") or 0)
    if tag == "spectral_factor" and side_idx == 0:
        return p_raw(row)
    if side_idx == 0:
        return blend(p_raw(row), p_book(row), 0.50)
    if tag == "spectral_dominant_factor":
        return p_book(row)
    return blend(p_raw(row), p_book(row), 0.35)


def p_rmt_memory_gate(row: dict[str, Any]) -> float:
    tag = str(row.get("spectral_tag") or "")
    top_over_edge = as_float(row.get("top_over_mp_edge"))
    side_idx = int(row.get("market_side_observation_index") or 0)
    if tag == "spectral_factor" and side_idx == 0:
        return p_raw(row)
    if top_over_edge is not None and top_over_edge >= 3.0:
        return p_book(row)
    if side_idx >= 2:
        return p_book(row)
    if side_idx == 1:
        return blend(p_raw(row), p_book(row), 0.35)
    return blend(p_raw(row), p_book(row), 0.65)


CANDIDATES: dict[str, Callable[[dict[str, Any]], float]] = {
    "v28_raw": p_raw,
    "book_ask_prior": p_book,
    "first_side_raw_later_book": p_first_side_raw_later_book,
    "first_market_raw_later_book": p_first_market_raw_later_book,
    "repeated_side_book_anchor": p_repeated_side_book_anchor,
    "repeated_market_book_anchor": p_repeated_market_book_anchor,
    "rmt_aggressive_forget": p_rmt_aggressive_forget,
    "rmt_repetition_forget": p_rmt_repetition_forget,
    "rmt_memory_gate": p_rmt_memory_gate,
}


def score_candidate(row: dict[str, Any], name: str, fn: Callable[[dict[str, Any]], float]) -> dict[str, Any] | None:
    if row.get("side_won") is None:
        return None
    if row.get("p_side") is None or row.get("ask_prob") is None:
        return None
    try:
        p = fn(row)
    except (KeyError, TypeError, ValueError):
        return None
    outcome = 1.0 if row.get("side_won") is True else 0.0
    return {
        "candidate": name,
        "market": row.get("market"),
        "source": row.get("source"),
        "side": row.get("side"),
        "p": p,
        "outcome": outcome,
        "brier": (p - outcome) ** 2,
        "gross_cents": row.get("gross_cents"),
        "market_observation_index": row.get("market_observation_index"),
        "market_side_observation_index": row.get("market_side_observation_index"),
        "is_first_market_observation": row.get("is_first_market_observation"),
        "is_first_market_side_observation": row.get("is_first_market_side_observation"),
        "spectral_tag": row.get("spectral_tag"),
        "top_over_mp_edge": row.get("top_over_mp_edge"),
        "outlier_share": row.get("outlier_share"),
        "raw_v28_p": row.get("p_side"),
        "book_p": row.get("ask_prob"),
        "v28_minus_book_p": row.get("v28_minus_ask_prob"),
    }


def collapse_rows(rows: list[dict[str, Any]], mode: str) -> list[dict[str, Any]]:
    picked: dict[tuple[str, str, str], dict[str, Any]] = {}
    for row in sorted(rows, key=lambda item: str(item.get("market") or "")):
        key = (
            str(row.get("candidate") or ""),
            str(row.get("market") or ""),
            str(row.get("side") or ""),
            str(row.get("source") or ""),
        )
        if mode == "first":
            picked.setdefault(key, row)
        elif mode == "last":
            picked[key] = row
        else:
            raise ValueError(f"unknown collapse mode: {mode}")
    return list(picked.values())


def summarize_group(rows: list[dict[str, Any]]) -> dict[str, Any]:
    if not rows:
        return {"count": 0, "avg_brier": None, "avg_p": None, "win_rate": None, "gross_cents": 0.0}
    return {
        "count": len(rows),
        "avg_brier": sum(float(row["brier"]) for row in rows) / len(rows),
        "avg_p": sum(float(row["p"]) for row in rows) / len(rows),
        "win_rate": sum(float(row["outcome"]) for row in rows) / len(rows),
        "gross_cents": sum(float(row.get("gross_cents") or 0.0) for row in rows),
    }


def summarize(rows: list[dict[str, Any]]) -> dict[str, Any]:
    by_candidate = {
        name: summarize_group([row for row in rows if row.get("candidate") == name])
        for name in CANDIDATES
    }
    raw_brier = by_candidate.get("v28_raw", {}).get("avg_brier")
    ranked: list[dict[str, Any]] = []
    for name, bucket in by_candidate.items():
        avg_brier = bucket.get("avg_brier")
        ranked.append(
            {
                "candidate": name,
                **bucket,
                "brier_minus_v28_raw": None if avg_brier is None or raw_brier is None else avg_brier - raw_brier,
            }
        )
    ranked.sort(key=lambda row: (float("inf") if row["avg_brier"] is None else float(row["avg_brier"]), row["candidate"]))
    return {"by_candidate": by_candidate, "ranked": ranked}


def build_report() -> dict[str, Any]:
    observations = enrich_state(attach_regime_rows(observation_pool()))
    scored: list[dict[str, Any]] = []
    for row in observations:
        for name, fn in CANDIDATES.items():
            scored_row = score_candidate(row, name, fn)
            if scored_row:
                scored.append(scored_row)
    views = {
        "all_observations": summarize(scored),
        "approved_entries": summarize([row for row in scored if row.get("source") == "approved_entry"]),
        "rejected_actionable": summarize([row for row in scored if row.get("source") == "rejected_actionable"]),
        "first_per_market_side_source": summarize(collapse_rows(scored, "first")),
        "last_per_market_side_source": summarize(collapse_rows(scored, "last")),
    }
    return {
        "observation_count": len(observations),
        "scored_rows": len(scored),
        "summary": summarize(scored),
        "views": views,
        "rows": scored,
    }


def write_csv(rows: list[dict[str, Any]]) -> None:
    if not rows:
        OUT_CSV.write_text("", encoding="utf-8")
        return
    keys = list(rows[0].keys())
    with OUT_CSV.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=keys)
        writer.writeheader()
        writer.writerows(rows)


def fmt(value: Any) -> str:
    if value is None:
        return "None"
    if isinstance(value, float):
        return f"{value:.6f}"
    return str(value)


def write_md(report: dict[str, Any]) -> None:
    lines = [
        "# v28 State-Aware FV Candidates",
        "",
        "Shadow-only probability candidates that explicitly forget stale same-market evidence.",
        "",
        f"- Observation rows: `{report['observation_count']}`",
        f"- Scored rows: `{report['scored_rows']}`",
        "",
        "## Ranked Overall",
        "",
        "| rank | candidate | count | avg p | win rate | avg brier | vs raw | gross c |",
        "|---:|---|---:|---:|---:|---:|---:|---:|",
    ]
    for idx, row in enumerate(report["summary"]["ranked"], start=1):
        lines.append(
            f"| {idx} | {row['candidate']} | {row['count']} | {fmt(row['avg_p'])} | {fmt(row['win_rate'])} | "
            f"{fmt(row['avg_brier'])} | {fmt(row['brier_minus_v28_raw'])} | {row['gross_cents']} |"
        )
    lines.extend(["", "## Robustness Views", ""])
    lines.append("| view | best candidate | count | best brier | best vs raw |")
    lines.append("|---|---|---:|---:|---:|")
    for view_name, view in report["views"].items():
        best = (view.get("ranked") or [{}])[0]
        lines.append(
            f"| {view_name} | {best.get('candidate')} | {best.get('count')} | "
            f"{fmt(best.get('avg_brier'))} | {fmt(best.get('brier_minus_v28_raw'))} |"
        )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    report = build_report()
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_csv(report["rows"])
    write_md(report)
    print(str(OUT_MD))


if __name__ == "__main__":
    main()
