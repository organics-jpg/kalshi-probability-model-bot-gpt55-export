"""Book-disagreement trajectory FV diagnostics for v28.

Research-only; no live bot changes or orders.

Physics idea: raw FV can be stale relative to the tradeable venue when the
same side's executable book probability deteriorates while raw FV stays high.
This tests fixed, simple shrinkage rules on every v28 observation with a known
settlement result, then reports de-correlated views so repeated ticks do not
masquerade as independent evidence.
"""
from __future__ import annotations

import json
import math
from datetime import datetime
from pathlib import Path
from typing import Any, Callable

from probe_v28_reactivated_shadow_status import market_result, read_events


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
OUT_JSON = OUT_DIR / "v28_book_disagreement_trajectory_fv_latest.json"
OUT_MD = OUT_DIR / "v28_book_disagreement_trajectory_fv_latest.md"


def as_float(value: Any) -> float | None:
    if value is None or value == "":
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def parse_ts(value: Any) -> datetime:
    if not value:
        return datetime.min
    try:
        return datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except ValueError:
        return datetime.min


def clamp(p: float) -> float:
    return max(0.000001, min(0.999999, p))


def logloss(p: float, outcome: float) -> float:
    p = clamp(p)
    return -(outcome * math.log(p) + (1.0 - outcome) * math.log(1.0 - p))


def raw_p(row: dict[str, Any]) -> float:
    return clamp(float(row["p_side"]))


def book_p(row: dict[str, Any]) -> float:
    return clamp(float(row["ask_prob"]))


def gap(row: dict[str, Any]) -> float:
    return raw_p(row) - book_p(row)


def blend(raw: float, book: float, book_weight: float) -> float:
    return clamp((1.0 - book_weight) * raw + book_weight * book)


def p_gap15_half_book(row: dict[str, Any]) -> float:
    raw = raw_p(row)
    book = book_p(row)
    return blend(raw, book, 0.50) if raw - book > 0.15 else raw


def p_gap20_half_book(row: dict[str, Any]) -> float:
    raw = raw_p(row)
    book = book_p(row)
    return blend(raw, book, 0.50) if raw - book > 0.20 else raw


def p_book_drawdown10_heavy_book(row: dict[str, Any]) -> float:
    raw = raw_p(row)
    book = book_p(row)
    drawdown = as_float(row.get("book_delta_vs_prior_same_side"))
    if drawdown is not None and drawdown <= -0.10:
        return blend(raw, book, 0.70)
    return raw


def p_gap15_or_drawdown10(row: dict[str, Any]) -> float:
    raw = raw_p(row)
    book = book_p(row)
    drawdown = as_float(row.get("book_delta_vs_prior_same_side"))
    if raw - book > 0.15 or (drawdown is not None and drawdown <= -0.10):
        return blend(raw, book, 0.60)
    return raw


def p_gap15_drawdown10_only(row: dict[str, Any]) -> float:
    raw = raw_p(row)
    book = book_p(row)
    drawdown = as_float(row.get("book_delta_vs_prior_same_side"))
    if raw - book > 0.15 and drawdown is not None and drawdown <= -0.10:
        return blend(raw, book, 0.75)
    return raw


VARIANTS: dict[str, Callable[[dict[str, Any]], float]] = {
    "raw_probability": raw_p,
    "book_probability": book_p,
    "gap15_half_book": p_gap15_half_book,
    "gap20_half_book": p_gap20_half_book,
    "book_drawdown10_heavy_book": p_book_drawdown10_heavy_book,
    "gap15_or_drawdown10": p_gap15_or_drawdown10,
    "gap15_and_drawdown10_only": p_gap15_drawdown10_only,
}


def observation_events() -> list[dict[str, Any]]:
    rows = []
    for event in read_events():
        event_type = str(event.get("event_type") or "")
        if event_type not in {"mushroom_v28_approved", "mushroom_v28_rejected"}:
            continue
        market = str(event.get("market") or "")
        side = str(event.get("side") or event.get("mushroom_v28_side") or "").lower()
        if not market or side not in {"yes", "no"}:
            continue
        p_side = as_float(event.get("mushroom_v28_p_side"))
        ask = as_float(event.get("mushroom_v28_ask_cents"))
        if p_side is None or ask is None:
            continue
        status, result = market_result(market)
        if result not in {"yes", "no"}:
            continue
        rows.append({
            "ts_wall": event.get("ts_wall"),
            "market": market,
            "side": side,
            "event_type": event_type,
            "approved": event_type == "mushroom_v28_approved",
            "result": result,
            "side_won": result == side,
            "outcome": 1.0 if result == side else 0.0,
            "p_side": p_side,
            "ask_prob": ask / 100.0,
            "ask_cents": ask,
            "seconds_to_close": as_float(event.get("mushroom_v28_seconds_to_close")),
            "book_age_ms": as_float(event.get("mushroom_v28_book_age_ms")),
            "btc_age_ms": as_float(event.get("mushroom_v28_btc_age_ms")),
            "raw_edge_cents": as_float(event.get("mushroom_v28_raw_edge_cents")),
            "net_edge_cents": as_float(event.get("mushroom_v28_net_edge_cents")),
            "reject_reason": event.get("mushroom_v28_reject_reason") or event.get("decision_reason"),
        })
    rows.sort(key=lambda row: (str(row["market"]), str(row["side"]), parse_ts(row.get("ts_wall"))))
    return add_trajectory(rows)


def add_trajectory(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    counts: dict[tuple[str, str], int] = {}
    prior_book: dict[tuple[str, str], float] = {}
    prior_gap: dict[tuple[str, str], float] = {}
    out = []
    for row in rows:
        key = (str(row["market"]), str(row["side"]))
        enriched = dict(row)
        current_book = float(row["ask_prob"])
        current_gap = gap(row)
        enriched["market_side_obs_index"] = counts.get(key, 0)
        enriched["book_delta_vs_prior_same_side"] = None if key not in prior_book else current_book - prior_book[key]
        enriched["gap_delta_vs_prior_same_side"] = None if key not in prior_gap else current_gap - prior_gap[key]
        enriched["raw_book_gap"] = current_gap
        out.append(enriched)
        counts[key] = counts.get(key, 0) + 1
        prior_book[key] = current_book
        prior_gap[key] = current_gap
    return out


def view_rows(rows: list[dict[str, Any]], view: str) -> list[dict[str, Any]]:
    if view == "all_observations":
        return rows
    if view == "approved_only":
        return [row for row in rows if row.get("approved") is True]
    grouped: dict[tuple[str, str], list[dict[str, Any]]] = {}
    for row in rows:
        grouped.setdefault((str(row["market"]), str(row["side"])), []).append(row)
    if view == "first_per_market_side":
        return [items[0] for items in grouped.values() if items]
    if view == "last_per_market_side":
        return [items[-1] for items in grouped.values() if items]
    raise ValueError(view)


def score(rows: list[dict[str, Any]], variant: str, fn: Callable[[dict[str, Any]], float]) -> dict[str, Any]:
    scored = []
    for row in rows:
        p = fn(row)
        outcome = float(row["outcome"])
        scored.append({
            "p": p,
            "outcome": outcome,
            "brier": (p - outcome) ** 2,
            "logloss": logloss(p, outcome),
            "won": row["side_won"],
        })
    probs = [row["p"] for row in scored]
    outcomes = [row["outcome"] for row in scored]
    return {
        "variant": variant,
        "rows": len(scored),
        "wins": sum(1 for row in scored if row["won"] is True),
        "losses": sum(1 for row in scored if row["won"] is False),
        "avg_p": avg(probs),
        "win_rate": avg(outcomes),
        "calibration_error": None if avg(probs) is None or avg(outcomes) is None else avg(outcomes) - avg(probs),
        "avg_brier": avg([row["brier"] for row in scored]),
        "avg_logloss": avg([row["logloss"] for row in scored]),
    }


def avg(values: list[float]) -> float | None:
    return sum(values) / len(values) if values else None


def rank_view(rows: list[dict[str, Any]], view: str) -> dict[str, Any]:
    selected = view_rows(rows, view)
    scores = [score(selected, name, fn) for name, fn in VARIANTS.items()]
    raw = next((row for row in scores if row["variant"] == "raw_probability"), {})
    raw_brier = raw.get("avg_brier")
    raw_logloss = raw.get("avg_logloss")
    ranked = []
    for row in scores:
        enriched = {
            **row,
            "brier_delta_vs_raw": None if row.get("avg_brier") is None or raw_brier is None else float(row["avg_brier"]) - float(raw_brier),
            "logloss_delta_vs_raw": None if row.get("avg_logloss") is None or raw_logloss is None else float(row["avg_logloss"]) - float(raw_logloss),
        }
        ranked.append(enriched)
    ranked.sort(key=lambda row: (float(row.get("avg_brier") or 999.0), float(row.get("avg_logloss") or 999.0)))
    return {"view": view, "rows": len(selected), "ranked": ranked}


def trigger_buckets(rows: list[dict[str, Any]]) -> dict[str, Any]:
    buckets = {
        "gap_gt_15pp": [row for row in rows if float(row["raw_book_gap"]) > 0.15],
        "same_side_book_down_gt_10pp": [
            row for row in rows
            if row.get("book_delta_vs_prior_same_side") is not None
            and float(row["book_delta_vs_prior_same_side"]) <= -0.10
        ],
        "gap_gt15_and_book_down_gt10": [
            row for row in rows
            if float(row["raw_book_gap"]) > 0.15
            and row.get("book_delta_vs_prior_same_side") is not None
            and float(row["book_delta_vs_prior_same_side"]) <= -0.10
        ],
    }
    out = {}
    for name, bucket in buckets.items():
        ranked = rank_view(bucket, "all_observations")["ranked"] if bucket else []
        out[name] = {
            "rows": len(bucket),
            "wins": sum(1 for row in bucket if row["side_won"] is True),
            "losses": sum(1 for row in bucket if row["side_won"] is False),
            "best_variant": ranked[0]["variant"] if ranked else None,
            "best_brier_delta_vs_raw": ranked[0].get("brier_delta_vs_raw") if ranked else None,
        }
    return out


def build_report() -> dict[str, Any]:
    rows = observation_events()
    views = [rank_view(rows, view) for view in ["approved_only", "first_per_market_side", "last_per_market_side", "all_observations"]]
    return {
        "surface": "all_settled_v28_approved_and_rejected_observations",
        "rows": len(rows),
        "markets": len({row["market"] for row in rows}),
        "market_sides": len({(row["market"], row["side"]) for row in rows}),
        "views": views,
        "trigger_buckets": trigger_buckets(rows),
        "interpretation": current_read(views),
    }


def current_read(views: list[dict[str, Any]]) -> list[str]:
    notes = []
    for view in views:
        ranked = view.get("ranked") or []
        if not ranked:
            continue
        best = ranked[0]
        notes.append(
            f"View {view['view']} best variant is {best['variant']} with Brier/logloss deltas {best.get('brier_delta_vs_raw')}/{best.get('logloss_delta_vs_raw')}."
        )
    notes.append("Repeated observation views are diagnostic only; first/last per market-side are less autocorrelated.")
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
        "# v28 Book-Disagreement Trajectory FV",
        "",
        "Research-only FV diagnostics using raw/book gap and same-side book trajectory.",
        "",
        f"- Surface: `{report.get('surface')}`",
        f"- Rows/markets/market-sides: `{report.get('rows')}/{report.get('markets')}/{report.get('market_sides')}`",
        "",
        "## Current Read",
        "",
    ]
    for note in report.get("interpretation") or []:
        lines.append(f"- {note}")
    for view in report.get("views") or []:
        lines.extend([
            "",
            f"## View: {view.get('view')}",
            "",
            f"- Rows: `{view.get('rows')}`",
            "",
            "| rank | variant | rows | W/L | avg p | win rate | cal err | brier d | logloss d |",
            "|---:|---|---:|---:|---:|---:|---:|---:|---:|",
        ])
        for idx, row in enumerate((view.get("ranked") or [])[:7], start=1):
            lines.append(
                f"| {idx} | `{row.get('variant')}` | {row.get('rows')} | {row.get('wins')}/{row.get('losses')} | "
                f"{fmt(row.get('avg_p'))} | {fmt(row.get('win_rate'))} | {fmt(row.get('calibration_error'))} | "
                f"{fmt(row.get('brier_delta_vs_raw'))} | {fmt(row.get('logloss_delta_vs_raw'))} |"
            )
    lines.extend([
        "",
        "## Trigger Buckets",
        "",
        "| bucket | rows | W/L | best variant | best brier d |",
        "|---|---:|---:|---|---:|",
    ])
    for name, row in (report.get("trigger_buckets") or {}).items():
        lines.append(
            f"| `{name}` | {row.get('rows')} | {row.get('wins')}/{row.get('losses')} | "
            f"`{row.get('best_variant')}` | {fmt(row.get('best_brier_delta_vs_raw'))} |"
        )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    report = build_report()
    write_md(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
