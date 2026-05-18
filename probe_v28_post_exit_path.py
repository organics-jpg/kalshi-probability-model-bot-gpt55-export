"""Post-exit path diagnostic for v28 shadow trades.

This report asks what the visible book did after each v28 exit. It is meant to
separate useful defensive exits from exits that sell a temporary shakeout before
the held side recovers into settlement.
"""
from __future__ import annotations

import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

from probe_v28_reactivated_shadow_status import (
    LOG_PATH,
    btc15m_close_time_from_ticker,
    read_events,
    reconstruct_trades,
    score_trade,
)


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
OUT_JSON = OUT_DIR / "v28_post_exit_path_latest.json"
OUT_MD = OUT_DIR / "v28_post_exit_path_latest.md"

HEARTBEAT_RE = re.compile(
    r"^(?P<ts>\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}),\d+\s+\|\s+INFO\s+\|\s+Heartbeat\s+\|\s+"
    r"watch=(?P<market>\S+)\s+yes_bid=(?P<yes_bid>\d+)\s+yes_ask=(?P<yes_ask>\d+)\s+"
    r"no_bid=(?P<no_bid>\d+)\s+no_ask=(?P<no_ask>\d+)"
)
EASTERN = ZoneInfo("America/New_York")


def parse_wall(value: str) -> datetime | None:
    if not value:
        return None
    text = value.replace("T", " ").replace("Z", "")
    try:
        parsed = datetime.fromisoformat(text)
    except ValueError:
        if "." in text:
            text = text.split(".", 1)[0]
        try:
            return datetime.strptime(text[:19], "%Y-%m-%d %H:%M:%S")
        except ValueError:
            return None
    if parsed.tzinfo is not None:
        return parsed.astimezone(EASTERN).replace(tzinfo=None)
    return parsed


def read_heartbeats() -> list[dict[str, Any]]:
    if not LOG_PATH.exists():
        return []
    rows: list[dict[str, Any]] = []
    with LOG_PATH.open("r", encoding="utf-8", errors="replace") as handle:
        for line in handle:
            match = HEARTBEAT_RE.search(line)
            if not match:
                continue
            ts = parse_wall(match.group("ts"))
            if ts is None:
                continue
            rows.append(
                {
                    "ts": ts,
                    "market": match.group("market"),
                    "yes_bid": int(match.group("yes_bid")),
                    "yes_ask": int(match.group("yes_ask")),
                    "no_bid": int(match.group("no_bid")),
                    "no_ask": int(match.group("no_ask")),
                }
            )
    return rows


def held_bid(row: dict[str, Any], side: str) -> int:
    return int(row["yes_bid"] if side == "yes" else row["no_bid"])


def build_rows() -> list[dict[str, Any]]:
    heartbeats = read_heartbeats()
    scored = [score_trade(trade) for trade in reconstruct_trades(read_events())]
    rows: list[dict[str, Any]] = []
    for trade in scored:
        exit_ts = parse_wall(str(trade.get("exit_ts") or ""))
        if exit_ts is None or trade.get("exit_cents") is None:
            continue
        market = str(trade.get("market") or "")
        side = str(trade.get("side") or "").lower()
        close_time_utc = btc15m_close_time_from_ticker(market)
        close_time = (
            close_time_utc.astimezone(EASTERN).replace(tzinfo=None)
            if close_time_utc is not None
            else None
        )
        future = [
            row
            for row in heartbeats
            if row["market"] == market and row["ts"] >= exit_ts
            and (close_time is None or row["ts"] < close_time)
        ]
        bids = [held_bid(row, side) for row in future]
        exit_cents = int(trade["exit_cents"])
        max_bid = max(bids) if bids else None
        min_bid = min(bids) if bids else None
        last_bid = bids[-1] if bids else None
        first_bid = bids[0] if bids else None
        max_after_cents = None if max_bid is None else max_bid - exit_cents
        min_after_cents = None if min_bid is None else min_bid - exit_cents
        min_unrealized_hold_gross = None if min_bid is None else (min_bid - int(trade["entry_cents"])) * int(trade["qty"])
        max_unrealized_hold_gross = None if max_bid is None else (max_bid - int(trade["entry_cents"])) * int(trade["qty"])
        rows.append(
            {
                "market": market,
                "side": side,
                "result": trade.get("result"),
                "entry_cents": trade.get("entry_cents"),
                "exit_cents": exit_cents,
                "actual_gross_cents": trade.get("actual_gross_cents"),
                "hold_gross_cents": trade.get("hold_gross_cents"),
                "exit_value_cents": trade.get("exit_value_cents"),
                "post_exit_points": len(future),
                "first_post_exit_bid": first_bid,
                "max_post_exit_bid": max_bid,
                "min_post_exit_bid": min_bid,
                "last_post_exit_bid": last_bid,
                "max_after_exit_cents": max_after_cents,
                "min_after_exit_cents": min_after_cents,
                "min_unrealized_hold_gross_cents": min_unrealized_hold_gross,
                "max_unrealized_hold_gross_cents": max_unrealized_hold_gross,
                "recovered_above_exit": max_after_cents is not None and max_after_cents > 0,
                "deteriorated_below_exit": min_after_cents is not None and min_after_cents < 0,
            }
        )
    return rows


def summarize(rows: list[dict[str, Any]]) -> dict[str, Any]:
    resolved = [row for row in rows if row.get("exit_value_cents") is not None]
    return {
        "exits": len(rows),
        "resolved": len(resolved),
        "recovered_above_exit": sum(1 for row in rows if row.get("recovered_above_exit") is True),
        "deteriorated_below_exit": sum(1 for row in rows if row.get("deteriorated_below_exit") is True),
        "avg_max_after_exit_cents": (
            sum(float(row["max_after_exit_cents"]) for row in rows if row.get("max_after_exit_cents") is not None)
            / max(1, sum(1 for row in rows if row.get("max_after_exit_cents") is not None))
            if rows
            else None
        ),
        "avg_min_after_exit_cents": (
            sum(float(row["min_after_exit_cents"]) for row in rows if row.get("min_after_exit_cents") is not None)
            / max(1, sum(1 for row in rows if row.get("min_after_exit_cents") is not None))
            if rows
            else None
        ),
        "exit_value_cents": sum(float(row["exit_value_cents"]) for row in resolved),
        "avg_min_unrealized_hold_gross_cents": (
            sum(float(row["min_unrealized_hold_gross_cents"]) for row in rows if row.get("min_unrealized_hold_gross_cents") is not None)
            / max(1, sum(1 for row in rows if row.get("min_unrealized_hold_gross_cents") is not None))
            if rows
            else None
        ),
    }


def write_md(rows: list[dict[str, Any]], summary: dict[str, Any]) -> None:
    lines = [
        "# v28 Post-Exit Path",
        "",
        "Forward-only diagnostic from observed heartbeat books after each v28 exit.",
        "",
        f"- Exits: `{summary['exits']}`",
        f"- Resolved exits: `{summary['resolved']}`",
        f"- Recovered above exit: `{summary['recovered_above_exit']}`",
        f"- Deteriorated below exit: `{summary['deteriorated_below_exit']}`",
        f"- Avg max after exit: `{summary['avg_max_after_exit_cents']}` cents",
        f"- Avg min after exit: `{summary['avg_min_after_exit_cents']}` cents",
        f"- Avg worst post-exit hold mark: `{summary['avg_min_unrealized_hold_gross_cents']}` cents",
        f"- Settled exit value vs hold: `{summary['exit_value_cents']}` cents",
        "",
        "## Rows",
        "",
        "| market | side | result | entry | exit | hold c | exit value c | points | max bid | min bid | last bid | max-after c | min-after c | worst hold mark c | best hold mark c |",
        "|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for row in rows:
        lines.append(
            "| {market} | {side} | {result} | {entry_cents} | {exit_cents} | {hold_gross_cents} | {exit_value_cents} | {post_exit_points} | {max_post_exit_bid} | {min_post_exit_bid} | {last_post_exit_bid} | {max_after_exit_cents} | {min_after_exit_cents} | {min_unrealized_hold_gross_cents} | {max_unrealized_hold_gross_cents} |".format(
                **row
            )
        )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    rows = build_rows()
    summary = summarize(rows)
    OUT_JSON.write_text(json.dumps({"summary": summary, "rows": rows}, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_md(rows, summary)
    print(str(OUT_MD))


if __name__ == "__main__":
    main()
