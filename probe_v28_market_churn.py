"""Market-level churn diagnostic for v28 shadow trades.

This report groups multiple entries in the same BTC 15m market to expose
side-flips, repeated entries, and market-level P&L that per-trade rows can hide.
"""
from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path
from typing import Any

from probe_v28_reactivated_shadow_status import read_events, reconstruct_trades, score_trade


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
OUT_JSON = OUT_DIR / "v28_market_churn_latest.json"
OUT_MD = OUT_DIR / "v28_market_churn_latest.md"


def build_rows() -> list[dict[str, Any]]:
    scored = [score_trade(trade) for trade in reconstruct_trades(read_events())]
    by_market: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in scored:
        by_market[str(row.get("market") or "")].append(row)

    rows: list[dict[str, Any]] = []
    for market, trades in sorted(by_market.items()):
        trades = sorted(trades, key=lambda row: str(row.get("entry_ts") or ""))
        sides = [str(row.get("side") or "") for row in trades]
        gross_values = [row.get("actual_gross_cents") for row in trades if row.get("actual_gross_cents") is not None]
        hold_values = [row.get("hold_gross_cents") for row in trades if row.get("hold_gross_cents") is not None]
        rows.append(
            {
                "market": market,
                "trades": len(trades),
                "unique_sides": sorted(set(sides)),
                "side_sequence": ">".join(sides),
                "side_flipped": len(set(sides)) > 1,
                "status": trades[-1].get("status"),
                "result": trades[-1].get("result"),
                "gross_cents": sum(float(value) for value in gross_values),
                "hold_gross_cents": sum(float(value) for value in hold_values),
                "exit_value_cents": sum(
                    float(row["exit_value_cents"])
                    for row in trades
                    if row.get("exit_value_cents") is not None
                ),
                "trade_rows": [
                    {
                        "side": row.get("side"),
                        "entry_cents": row.get("entry_cents"),
                        "exit_cents": row.get("exit_cents"),
                        "actual_gross_cents": row.get("actual_gross_cents"),
                        "hold_gross_cents": row.get("hold_gross_cents"),
                        "exit_value_cents": row.get("exit_value_cents"),
                        "exit_reason": (
                            row.get("exit_features", {}).get("mushroom_v28_exit_reason")
                            if isinstance(row.get("exit_features"), dict)
                            else None
                        )
                        or row.get("exit_reason"),
                    }
                    for row in trades
                ],
            }
        )
    return rows


def summarize(rows: list[dict[str, Any]]) -> dict[str, Any]:
    churned = [row for row in rows if row["trades"] > 1]
    flipped = [row for row in rows if row["side_flipped"]]
    return {
        "markets": len(rows),
        "churned_markets": len(churned),
        "flipped_markets": len(flipped),
        "gross_cents": sum(float(row["gross_cents"]) for row in rows),
        "hold_gross_cents": sum(float(row["hold_gross_cents"]) for row in rows),
        "exit_value_cents": sum(float(row["exit_value_cents"]) for row in rows),
        "churn_gross_cents": sum(float(row["gross_cents"]) for row in churned),
        "churn_hold_gross_cents": sum(float(row["hold_gross_cents"]) for row in churned),
        "churn_exit_value_cents": sum(float(row["exit_value_cents"]) for row in churned),
    }


def write_md(rows: list[dict[str, Any]], summary: dict[str, Any]) -> None:
    lines = [
        "# v28 Market Churn",
        "",
        "Groups v28 shadow trades by market to expose repeated entries and side flips.",
        "",
        f"- Markets entered: `{summary['markets']}`",
        f"- Markets with multiple entries: `{summary['churned_markets']}`",
        f"- Markets with side flips: `{summary['flipped_markets']}`",
        f"- Gross P&L: `${summary['gross_cents'] / 100.0:.2f}`",
        f"- Hold P&L: `${summary['hold_gross_cents'] / 100.0:.2f}`",
        f"- Exit value: `${summary['exit_value_cents'] / 100.0:.2f}`",
        f"- Churn-market gross P&L: `${summary['churn_gross_cents'] / 100.0:.2f}`",
        f"- Churn-market hold P&L: `${summary['churn_hold_gross_cents'] / 100.0:.2f}`",
        f"- Churn-market exit value: `${summary['churn_exit_value_cents'] / 100.0:.2f}`",
        "",
        "## Markets",
        "",
        "| market | trades | sides | flipped | result | gross c | hold c | exit value c |",
        "|---|---:|---|---|---|---:|---:|---:|",
    ]
    for row in rows:
        lines.append(
            "| {market} | {trades} | {side_sequence} | {side_flipped} | {result} | {gross_cents} | {hold_gross_cents} | {exit_value_cents} |".format(
                **row
            )
        )
    lines.extend(["", "## Trade Detail", ""])
    for row in rows:
        if row["trades"] <= 1:
            continue
        lines.append(f"### {row['market']}")
        lines.append("")
        lines.append("| side | entry | exit | gross c | hold c | exit value c | exit reason |")
        lines.append("|---|---:|---:|---:|---:|---:|---|")
        for trade in row["trade_rows"]:
            lines.append(
                "| {side} | {entry_cents} | {exit_cents} | {actual_gross_cents} | {hold_gross_cents} | {exit_value_cents} | {exit_reason} |".format(
                    **trade
                )
            )
        lines.append("")
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
