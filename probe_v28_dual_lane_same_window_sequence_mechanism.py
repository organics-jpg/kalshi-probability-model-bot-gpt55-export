"""Sequence-level mechanism audit for dual-lane same-window deficits.

Research-only; no live bot changes or orders.

This explains how actual live v28 beat the current dual-lane forced precheck on
the same markets: larger same-side exposure, better exit capture, side flips, or
other sequence effects.
"""
from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
DELTA_JSON = OUT_DIR / "v28_dual_lane_same_window_delta_autopsy_latest.json"
LIVE_TRADES_CSV = ROOT / "stats" / "live_mushroom_v28_size2" / "trades.csv"
OUT_JSON = OUT_DIR / "v28_dual_lane_same_window_sequence_mechanism_latest.json"
OUT_MD = OUT_DIR / "v28_dual_lane_same_window_sequence_mechanism_latest.md"

LOCAL_TZ = datetime.now().astimezone().tzinfo


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


def fnum(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def money(value: Any) -> str:
    cents = fnum(value)
    return f"{cents:.0f}c (${cents / 100.0:.2f})"


def parse_ts(value: str | None) -> datetime | None:
    if not value:
        return None
    text = str(value).strip()
    if not text:
        return None
    try:
        if "T" in text:
            return datetime.fromisoformat(text.replace("Z", "+00:00")).astimezone(timezone.utc)
        return datetime.strptime(text, "%Y-%m-%d %H:%M:%S").replace(tzinfo=LOCAL_TZ).astimezone(timezone.utc)
    except ValueError:
        return None


def load_live_trades_after(freeze_ts: str) -> list[dict[str, Any]]:
    freeze = parse_ts(freeze_ts)
    if freeze is None or not LIVE_TRADES_CSV.exists():
        return []
    rows: list[dict[str, Any]] = []
    with LIVE_TRADES_CSV.open("r", encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle):
            entry_ts = parse_ts(row.get("entry_ts"))
            if entry_ts is None or entry_ts < freeze:
                continue
            exit_ts = parse_ts(row.get("exit_ts"))
            item = dict(row)
            item["entry_ts_utc"] = entry_ts.isoformat()
            item["exit_ts_utc"] = exit_ts.isoformat() if exit_ts else None
            item["qty_num"] = fnum(row.get("qty"))
            item["entry_fill_cents"] = fnum(row.get("entry_fill_cents_used") or row.get("entry_fill_cents_assumed"))
            item["exit_fill_cents"] = fnum(row.get("exit_fill_cents_used") or row.get("exit_fill_cents_assumed"))
            item["net_cents"] = round(100.0 * fnum(row.get("net_pnl_dollars")), 4)
            rows.append(item)
    return rows


def sequence_mechanism(candidate: dict[str, Any], trades: list[dict[str, Any]]) -> str:
    side = str(candidate.get("candidate_side") or "")
    candidate_net = fnum(candidate.get("candidate_net_cents"))
    live_net = fnum(candidate.get("live_net_cents"))
    same_side_net = sum(fnum(row.get("net_cents")) for row in trades if row.get("side") == side)
    opposite_net = live_net - same_side_net
    sides = {str(row.get("side") or "") for row in trades}
    terminal_wins = [row for row in trades if str(row.get("outcome") or "") == "win"]
    exited = [row for row in trades if str(row.get("outcome") or "") == "exited_before_settlement"]

    if candidate_net >= 0 and live_net > candidate_net:
        if len(sides) == 1 and terminal_wins and not exited:
            return "live_larger_terminal_exposure_same_side"
        if len(sides) == 1 and exited:
            return "live_same_side_exit_capture_scaled_better"
        if opposite_net > 0:
            return "live_added_opposite_side_profit"
        return "live_same_side_captured_more"
    if candidate_net < 0 <= live_net:
        if opposite_net > 0 and same_side_net <= 0:
            return "live_side_flip_escaped_candidate_loss"
        if same_side_net > 0:
            return "live_same_side_timing_escaped_candidate_loss"
        return "live_sequence_escaped_candidate_loss"
    if live_net < candidate_net:
        return "candidate_sequence_better_than_live"
    return "sequence_tied"


def compact_trade(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "entry_ts": row.get("entry_ts"),
        "side": row.get("side"),
        "qty": row.get("qty_num"),
        "entry_fill_cents": row.get("entry_fill_cents"),
        "exit_ts": row.get("exit_ts"),
        "exit_fill_cents": row.get("exit_fill_cents"),
        "outcome": row.get("outcome"),
        "net_cents": row.get("net_cents"),
    }


def summarize(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[str, dict[str, Any]] = {}
    for row in rows:
        label = str(row.get("mechanism") or "unknown")
        item = grouped.setdefault(
            label,
            {
                "mechanism": label,
                "rows": 0,
                "candidate_net_cents": 0.0,
                "live_net_cents": 0.0,
                "candidate_minus_live_cents": 0.0,
                "live_trade_count": 0,
                "live_qty": 0.0,
            },
        )
        item["rows"] += 1
        item["candidate_net_cents"] += fnum(row.get("candidate_net_cents"))
        item["live_net_cents"] += fnum(row.get("live_net_cents"))
        item["candidate_minus_live_cents"] += fnum(row.get("candidate_minus_live_cents"))
        item["live_trade_count"] += int(fnum(row.get("live_trade_count")))
        item["live_qty"] += fnum(row.get("live_qty"))
    return sorted(grouped.values(), key=lambda item: fnum(item.get("candidate_minus_live_cents")))


def build_report() -> dict[str, Any]:
    delta = load_json(DELTA_JSON)
    freeze_ts = str(delta.get("freeze_ts_utc") or "")
    trades = load_live_trades_after(freeze_ts)
    by_market: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for trade in trades:
        market = str(trade.get("market") or "")
        if market:
            by_market[market].append(trade)

    deficit_rows = [row for row in delta.get("top_deficits") or [] if isinstance(row, dict)]
    rows: list[dict[str, Any]] = []
    for row in deficit_rows:
        market = str(row.get("market") or "")
        market_trades = sorted(by_market.get(market, []), key=lambda item: str(item.get("entry_ts") or ""))
        side = str(row.get("candidate_side") or "")
        same_side_net = sum(fnum(trade.get("net_cents")) for trade in market_trades if trade.get("side") == side)
        opposite_net = sum(fnum(trade.get("net_cents")) for trade in market_trades if trade.get("side") != side)
        live_qty = sum(fnum(trade.get("qty_num")) for trade in market_trades)
        live_side_counts = Counter(str(trade.get("side") or "") for trade in market_trades)
        item = dict(row)
        item.update(
            {
                "mechanism": sequence_mechanism(row, market_trades),
                "live_same_side_net_cents": same_side_net,
                "live_opposite_side_net_cents": opposite_net,
                "live_trade_count": len(market_trades),
                "live_qty": live_qty,
                "live_side_counts": dict(live_side_counts),
                "live_sequence": [compact_trade(trade) for trade in market_trades],
            }
        )
        rows.append(item)

    summary = summarize(rows)
    largest = summary[0] if summary else {}
    interpretation = [
        "This is a mechanism audit for same-window deficits only; it is not a promotion gate.",
        "Deficit markets should be used to repair exposure/exit sequencing, not to hand-pick exclusions.",
    ]
    if largest:
        interpretation.append(
            f"Largest mechanism bucket is {largest.get('mechanism')} with {largest.get('rows')} row(s) "
            f"and {money(largest.get('candidate_minus_live_cents'))} candidate-minus-live."
        )
    if any(row.get("mechanism") == "live_side_flip_escaped_candidate_loss" for row in rows):
        interpretation.append(
            "Candidate-loss rows include live side-flip escapes, so a one-shot hold-fill parent row is missing state transition behavior."
        )

    return {
        "generated_at_utc": utc_now_iso(),
        "freeze_ts_utc": freeze_ts,
        "delta_autopsy_generated_at_utc": delta.get("generated_at_utc"),
        "promotion_use": "same_window_research_only",
        "candidate_policy": delta.get("candidate_policy"),
        "candidate_minus_live_same_markets_cents": delta.get("candidate_minus_live_same_markets_cents"),
        "deficit_rows": len(rows),
        "mechanism_summary": summary,
        "rows": rows,
        "interpretation": interpretation,
    }


def write_outputs(report: dict[str, Any]) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8")
    lines = [
        "# v28 Dual-Lane Same-Window Sequence Mechanism",
        "",
        "Research-only. No live bot logic changes, no orders.",
        "",
        f"- Generated UTC: `{report.get('generated_at_utc')}`",
        f"- Delta autopsy UTC: `{report.get('delta_autopsy_generated_at_utc')}`",
        f"- Freeze UTC: `{report.get('freeze_ts_utc')}`",
        f"- Candidate policy: `{report.get('candidate_policy')}`",
        f"- Candidate minus live on same markets: `{money(report.get('candidate_minus_live_same_markets_cents'))}`",
        "",
        "## Read",
        "",
    ]
    lines.extend(f"- {item}" for item in report.get("interpretation") or [])
    lines.extend(
        [
            "",
            "## Mechanism Summary",
            "",
            "| mechanism | rows | candidate net | live net | candidate-live | live trades | live qty |",
            "|---|---:|---:|---:|---:|---:|---:|",
        ]
    )
    for row in report.get("mechanism_summary") or []:
        lines.append(
            f"| `{row.get('mechanism')}` | {row.get('rows')} | {money(row.get('candidate_net_cents'))} | "
            f"{money(row.get('live_net_cents'))} | {money(row.get('candidate_minus_live_cents'))} | "
            f"{row.get('live_trade_count')} | {row.get('live_qty'):.0f} |"
        )
    lines.extend(
        [
            "",
            "## Deficit Rows",
            "",
            "| market | mechanism | class | side | candidate | live | delta | same-side live | opposite live | trades | sequence |",
            "|---|---|---|---|---:|---:|---:|---:|---:|---:|---|",
        ]
    )
    for row in report.get("rows") or []:
        sequence = "; ".join(
            (
                f"{trade.get('entry_ts')} {trade.get('side')}x{trade.get('qty'):.0f} "
                f"{trade.get('entry_fill_cents'):.0f}->{trade.get('exit_fill_cents'):.0f} "
                f"{trade.get('outcome')} {money(trade.get('net_cents'))}"
            )
            for trade in row.get("live_sequence") or []
        )
        lines.append(
            f"| `{row.get('market')}` | `{row.get('mechanism')}` | `{row.get('classification')}` | "
            f"{row.get('candidate_side')} | {money(row.get('candidate_net_cents'))} | "
            f"{money(row.get('live_net_cents'))} | {money(row.get('candidate_minus_live_cents'))} | "
            f"{money(row.get('live_same_side_net_cents'))} | {money(row.get('live_opposite_side_net_cents'))} | "
            f"{row.get('live_trade_count')} | {sequence} |"
        )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    report = build_report()
    write_outputs(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
