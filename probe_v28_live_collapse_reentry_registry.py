"""Future-only live v28 probability-collapse reentry registry.

Research-only; no live bot changes or orders.

The market-physics question is whether a v28 probability-collapse exit marks a
temporary turbulence pocket or a genuine thesis reset. If the bot re-enters the
same market shortly after a collapse, this registry scores those reentries as a
predeclared state feature instead of hand-tuning from the latest noisy example.
"""
from __future__ import annotations

import json
import math
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
EVENTS = ROOT / "logs" / "live_mushroom_v28_size2" / "execution_events.ndjson"
OUT_DIR = ROOT / "logs" / "edge_research"
STATE_JSON = OUT_DIR / "v28_live_collapse_reentry_registry_state.json"
OUT_JSON = OUT_DIR / "v28_live_collapse_reentry_registry_latest.json"
OUT_MD = OUT_DIR / "v28_live_collapse_reentry_registry_latest.md"


RULE = {
    "registry": "live_v28_probability_collapse_reentry",
    "hypothesis": (
        "A probability-collapse exit is a high-turbulence state transition. "
        "Same-market reentries after collapse should be separately calibrated "
        "before being trusted as ordinary high-confidence FV entries."
    ),
    "candidate_action": "diagnostic_only_skip_or_penalize_post_collapse_reentries",
    "tag_definitions": {
        "opposite_side_reentry": "entry side differs from the collapsed exit side",
        "same_side_reentry": "entry side equals the collapsed exit side",
        "fast_reentry_lte_180s": "seconds since collapse exit <= 180",
        "mid_reentry_180_360s": "180 < seconds since collapse exit <= 360",
        "late_reentry_gt_360s": "seconds since collapse exit > 360",
        "high_conf_p90": "p_side >= 0.90",
        "thin_edge_lt_4c": "edge_cents < 4",
        "strong_edge_ge_8c": "edge_cents >= 8",
        "older_book_500ms": "book_age_ms >= 500",
    },
}


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def parse_ts(value: Any) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except ValueError:
        return None


def as_float(value: Any) -> float | None:
    if value is None or value == "":
        return None
    try:
        out = float(value)
    except (TypeError, ValueError):
        return None
    return out if math.isfinite(out) else None


def as_int(value: Any) -> int | None:
    value_float = as_float(value)
    return int(round(value_float)) if value_float is not None else None


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
    state = {"freeze_ts_utc": utc_now_iso(), **RULE}
    STATE_JSON.write_text(json.dumps(state, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return state


def load_events() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    if not EVENTS.exists():
        return rows
    with EVENTS.open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError:
                continue
            if isinstance(row, dict):
                rows.append(row)
    rows.sort(key=lambda row: parse_ts(row.get("ts_wall")) or datetime.min.replace(tzinfo=timezone.utc))
    return rows


def fill_rank(event_type: str) -> int:
    return {
        "fill_full": 4,
        "exit_reconciled": 3,
        "exit_submit_success": 2,
        "order_submit_success": 2,
    }.get(event_type, 1)


def dedupe_fills(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    by_order: dict[str, dict[str, Any]] = {}
    anonymous: list[dict[str, Any]] = []
    for row in rows:
        key = str(row.get("client_order_id") or row.get("order_id") or "")
        if not key:
            anonymous.append(row)
            continue
        current = by_order.get(key)
        if current is None:
            by_order[key] = row
            continue
        cur_rank = fill_rank(str(current.get("event_type") or ""))
        row_rank = fill_rank(str(row.get("event_type") or ""))
        cur_ts = parse_ts(current.get("ts_wall")) or datetime.min.replace(tzinfo=timezone.utc)
        row_ts = parse_ts(row.get("ts_wall")) or datetime.min.replace(tzinfo=timezone.utc)
        if row_rank > cur_rank or (row_rank == cur_rank and row_ts >= cur_ts):
            by_order[key] = row
    out = list(by_order.values()) + anonymous
    out.sort(key=lambda row: parse_ts(row.get("ts_wall")) or datetime.min.replace(tzinfo=timezone.utc))
    return out


def row_price(row: dict[str, Any]) -> int | None:
    return as_int(
        row.get("actual_fill_price_cents")
        or row.get("trigger_price_cents")
        or row.get("top_of_book_limit_cents")
        or row.get("cap_price_cents")
    )


def row_qty(row: dict[str, Any]) -> int:
    return as_int(row.get("fill_count") or row.get("position_size") or row.get("slice_target_size")) or 0


def build_legs(events: list[dict[str, Any]]) -> list[dict[str, Any]]:
    entry_fills = dedupe_fills([
        row for row in events
        if row.get("event_type") == "fill_full"
        and str(row.get("client_order_id") or "").startswith("btc15m-entry")
    ])
    exit_fills = dedupe_fills([
        row for row in events
        if row.get("event_type") in {"fill_full", "exit_reconciled"}
        and str(row.get("client_order_id") or "").startswith("btc15m-exit")
    ])
    legs: list[dict[str, Any]] = []
    markets = sorted({str(row.get("market") or "") for row in [*entry_fills, *exit_fills] if row.get("market")})
    for market in markets:
        combined = [
            (parse_ts(row.get("ts_wall")), "entry", row)
            for row in entry_fills
            if str(row.get("market") or "") == market
        ]
        combined.extend(
            (parse_ts(row.get("ts_wall")), "exit", row)
            for row in exit_fills
            if str(row.get("market") or "") == market
        )
        combined = [item for item in combined if item[0] is not None]
        combined.sort(key=lambda item: item[0])

        open_lots: list[dict[str, Any]] = []
        for ts, kind, row in combined:
            if kind == "entry":
                qty = row_qty(row)
                price = row_price(row)
                if qty <= 0 or price is None:
                    continue
                open_lots.append({"entry": row, "remaining": qty, "entry_price": price})
                continue

            qty = row_qty(row)
            exit_price = row_price(row)
            if qty <= 0 or exit_price is None:
                continue
            remaining = qty
            while remaining > 0 and open_lots:
                lot = open_lots[0]
                take = min(remaining, int(lot["remaining"]))
                entry = lot["entry"]
                entry_price = int(lot["entry_price"])
                legs.append(make_leg(entry, row, take, entry_price, exit_price))
                lot["remaining"] = int(lot["remaining"]) - take
                remaining -= take
                if lot["remaining"] <= 0:
                    open_lots.pop(0)

        for lot in open_lots:
            entry = lot["entry"]
            legs.append(make_leg(entry, None, int(lot["remaining"]), int(lot["entry_price"]), None))
    legs.sort(key=lambda row: parse_ts(row.get("entry_ts")) or datetime.min.replace(tzinfo=timezone.utc))
    return legs


def make_leg(entry: dict[str, Any], exit_row: dict[str, Any] | None, qty: int, entry_price: int, exit_price: int | None) -> dict[str, Any]:
    gross = None if exit_price is None else qty * (exit_price - entry_price)
    return {
        "market": entry.get("market"),
        "side": entry.get("side") or entry.get("mushroom_v28_side"),
        "qty": qty,
        "entry_ts": entry.get("ts_wall"),
        "entry_price_cents": entry_price,
        "entry_p_side": as_float(entry.get("mushroom_v28_p_side")),
        "entry_edge_cents": as_float(entry.get("mushroom_v28_edge_cents")),
        "entry_abs_d_sigma": as_float(entry.get("mushroom_v28_abs_d_sigma")),
        "entry_seconds_to_close": as_float(entry.get("mushroom_v28_seconds_to_close") or entry.get("seconds_to_close")),
        "entry_depth_count": as_float(entry.get("mushroom_v28_depth_count")),
        "entry_book_age_ms": as_float(entry.get("mushroom_v28_book_age_ms")),
        "exit_ts": exit_row.get("ts_wall") if exit_row else None,
        "exit_price_cents": exit_price,
        "exit_reason": exit_row.get("decision_reason") if exit_row else None,
        "gross_cents": gross,
        "status": "closed" if exit_row else "open",
    }


def tags(row: dict[str, Any]) -> list[str]:
    seconds = as_float(row.get("seconds_since_collapse"))
    p_side = as_float(row.get("entry_p_side"))
    edge = as_float(row.get("entry_edge_cents"))
    book_age = as_float(row.get("entry_book_age_ms"))
    out: list[str] = []
    out.append("same_side_reentry" if row.get("same_side_as_collapse") else "opposite_side_reentry")
    if seconds is not None and seconds <= 180:
        out.append("fast_reentry_lte_180s")
    if seconds is not None and 180 < seconds <= 360:
        out.append("mid_reentry_180_360s")
    if seconds is not None and seconds > 360:
        out.append("late_reentry_gt_360s")
    if p_side is not None and p_side >= 0.90:
        out.append("high_conf_p90")
    if edge is not None and edge < 4.0:
        out.append("thin_edge_lt_4c")
    if edge is not None and edge >= 8.0:
        out.append("strong_edge_ge_8c")
    if book_age is not None and book_age >= 500:
        out.append("older_book_500ms")
    return out


def reentry_rows(legs: list[dict[str, Any]], freeze_ts: datetime) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    by_market: dict[str, list[dict[str, Any]]] = {}
    for leg in legs:
        by_market.setdefault(str(leg.get("market") or ""), []).append(leg)

    all_rows: list[dict[str, Any]] = []
    for market, market_legs in by_market.items():
        previous_collapse: dict[str, Any] | None = None
        for leg in sorted(market_legs, key=lambda row: parse_ts(row.get("entry_ts")) or datetime.min.replace(tzinfo=timezone.utc)):
            entry_ts = parse_ts(leg.get("entry_ts"))
            if previous_collapse and entry_ts:
                collapse_ts = parse_ts(previous_collapse.get("exit_ts"))
                if collapse_ts and entry_ts > collapse_ts:
                    row = {
                        **leg,
                        "collapse_exit_ts": previous_collapse.get("exit_ts"),
                        "collapse_exit_side": previous_collapse.get("side"),
                        "collapse_exit_price_cents": previous_collapse.get("exit_price_cents"),
                        "collapse_entry_price_cents": previous_collapse.get("entry_price_cents"),
                        "seconds_since_collapse": (entry_ts - collapse_ts).total_seconds(),
                        "same_side_as_collapse": leg.get("side") == previous_collapse.get("side"),
                    }
                    row["tags"] = tags(row)
                    all_rows.append(row)
            reason = str(leg.get("exit_reason") or "")
            if "probability_collapse_full" in reason:
                previous_collapse = leg
    future = [row for row in all_rows if (parse_ts(row.get("entry_ts")) or datetime.min.replace(tzinfo=timezone.utc)) > freeze_ts]
    return all_rows, future


def rollups(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    out = []
    for tag in sorted({tag for row in rows for tag in row.get("tags", [])}):
        tagged = [row for row in rows if tag in (row.get("tags") or [])]
        closed = [row for row in tagged if row.get("gross_cents") is not None]
        gross = sum(float(row.get("gross_cents") or 0.0) for row in closed)
        out.append({
            "tag": tag,
            "rows": len(tagged),
            "closed": len(closed),
            "wins": sum(1 for row in closed if float(row.get("gross_cents") or 0.0) > 0),
            "losses": sum(1 for row in closed if float(row.get("gross_cents") or 0.0) < 0),
            "gross_cents": gross,
            "skip_delta_cents": -gross,
        })
    out.sort(key=lambda row: (-int(row.get("closed") or 0), str(row.get("tag"))))
    return out


def summarize(rows: list[dict[str, Any]]) -> dict[str, Any]:
    closed = [row for row in rows if row.get("gross_cents") is not None]
    gross = sum(float(row.get("gross_cents") or 0.0) for row in closed)
    return {
        "rows": len(rows),
        "closed": len(closed),
        "open": len(rows) - len(closed),
        "wins": sum(1 for row in closed if float(row.get("gross_cents") or 0.0) > 0),
        "losses": sum(1 for row in closed if float(row.get("gross_cents") or 0.0) < 0),
        "gross_cents": gross,
        "skip_delta_cents": -gross,
    }


def build_report() -> dict[str, Any]:
    state = load_or_create_state()
    freeze_ts = parse_ts(state["freeze_ts_utc"]) or datetime.now(timezone.utc)
    legs = build_legs(load_events())
    all_rows, future_rows = reentry_rows(legs, freeze_ts)
    return {
        "freeze": state,
        "diagnostic_all_summary": summarize(all_rows),
        "future_summary": summarize(future_rows),
        "future_tag_rollups": rollups(future_rows),
        "diagnostic_recent_rows": all_rows[-12:],
        "future_rows": future_rows,
        "interpretation": interpretation(future_rows),
    }


def interpretation(future_rows: list[dict[str, Any]]) -> list[str]:
    if not future_rows:
        return [
            "No post-freeze collapse-reentry rows yet. Current/pre-freeze rows are diagnostic only.",
            "Once rows arrive, a positive skip_delta_cents means skipping post-collapse reentries would have helped; negative means it would have hurt.",
        ]
    summary = summarize(future_rows)
    return [
        f"Post-freeze collapse-reentry rows: {summary['rows']} total, {summary['closed']} closed, {summary['open']} open.",
        f"Closed gross is {summary['gross_cents']}c; hypothetical skip delta is {summary['skip_delta_cents']}c.",
        "This is a state/FV confidence feature, not a promotion rule until sample size and tag stability are adequate.",
    ]


def fmt(value: Any) -> str:
    if value is None:
        return "None"
    if isinstance(value, float):
        return f"{value:.6f}"
    return str(value)


def write_report(report: dict[str, Any]) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8")
    future = report.get("future_summary") or {}
    diag = report.get("diagnostic_all_summary") or {}
    lines = [
        "# v28 Live Collapse Reentry Registry",
        "",
        f"- Freeze timestamp UTC: `{(report.get('freeze') or {}).get('freeze_ts_utc')}`",
        f"- Future rows/closed/open: `{future.get('rows')}/{future.get('closed')}/{future.get('open')}`",
        f"- Future gross / skip delta: `{fmt(future.get('gross_cents'))}c / {fmt(future.get('skip_delta_cents'))}c`",
        f"- Diagnostic all rows/closed/open: `{diag.get('rows')}/{diag.get('closed')}/{diag.get('open')}`",
        "",
        "## Current Read",
        "",
    ]
    for note in report.get("interpretation") or []:
        lines.append(f"- {note}")
    lines.extend([
        "",
        "## Future Tag Rollups",
        "",
        "| tag | rows | closed | W/L | gross c | skip delta c |",
        "|---|---:|---:|---:|---:|---:|",
    ])
    for row in report.get("future_tag_rollups") or []:
        lines.append(
            f"| {row.get('tag')} | {row.get('rows')} | {row.get('closed')} | "
            f"{row.get('wins')}/{row.get('losses')} | {fmt(row.get('gross_cents'))} | {fmt(row.get('skip_delta_cents'))} |"
        )
    lines.extend([
        "",
        "## Future Rows",
        "",
        "| market | side | entry | exit | p | edge | sec since collapse | same side | gross c | tags |",
        "|---|---|---:|---:|---:|---:|---:|---|---:|---|",
    ])
    for row in report.get("future_rows") or []:
        lines.append(row_line(row))
    lines.extend([
        "",
        "## Diagnostic Recent Rows",
        "",
        "These rows are not promotion evidence if they predate the freeze.",
        "",
        "| market | side | entry | exit | p | edge | sec since collapse | same side | gross c | tags |",
        "|---|---|---:|---:|---:|---:|---:|---|---:|---|",
    ])
    for row in report.get("diagnostic_recent_rows") or []:
        lines.append(row_line(row))
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def row_line(row: dict[str, Any]) -> str:
    return (
        f"| {row.get('market')} | {row.get('side')} | {fmt(row.get('entry_price_cents'))} | "
        f"{fmt(row.get('exit_price_cents'))} | {fmt(row.get('entry_p_side'))} | "
        f"{fmt(row.get('entry_edge_cents'))} | {fmt(row.get('seconds_since_collapse'))} | "
        f"{row.get('same_side_as_collapse')} | {fmt(row.get('gross_cents'))} | "
        f"{', '.join(row.get('tags') or [])} |"
    )


def main() -> None:
    report = build_report()
    write_report(report)
    print(str(OUT_MD))


if __name__ == "__main__":
    main()
