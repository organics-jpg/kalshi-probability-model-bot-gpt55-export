from __future__ import annotations

import csv
import json
import os
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo


SCRIPT_DIR = Path(__file__).resolve().parent
LOCAL_TZ = ZoneInfo(os.getenv("PHI_SEGMENT_LOCAL_TZ", "America/New_York"))


def parse_event_ts(value: str | None) -> datetime | None:
    if not value:
        return None
    text = str(value).strip().replace("Z", "+00:00")
    try:
        dt = datetime.fromisoformat(text)
    except ValueError:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def parse_trade_ts(value: str | None) -> datetime | None:
    if not value:
        return None
    text = str(value).strip()
    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M:%S"):
        try:
            naive = datetime.strptime(text, fmt)
            return naive.replace(tzinfo=LOCAL_TZ).astimezone(timezone.utc)
        except ValueError:
            pass
    return parse_event_ts(text)


def fnum(value: Any, default: float = 0.0) -> float:
    try:
        if value is None or value == "":
            return default
        return float(value)
    except (TypeError, ValueError):
        return default


def load_ndjson(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    if not path.exists():
        return rows
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        try:
            row = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(row, dict):
            rows.append(row)
    return rows


def load_csv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open(newline="", encoding="utf-8", errors="replace") as handle:
        return list(csv.DictReader(handle))


def stats_bucket() -> dict[str, Any]:
    return {
        "trades": 0,
        "wins": 0,
        "losses": 0,
        "flats": 0,
        "gross_pnl_dollars": 0.0,
        "fees_dollars": 0.0,
        "net_pnl_dollars": 0.0,
        "qty": 0.0,
    }


def add_trade(bucket: dict[str, Any], trade: dict[str, Any]) -> None:
    net = fnum(trade.get("net_pnl_dollars"))
    gross = fnum(trade.get("gross_pnl_dollars"))
    fees = fnum(trade.get("total_fees_dollars"))
    bucket["trades"] += 1
    bucket["qty"] += fnum(trade.get("qty"))
    bucket["gross_pnl_dollars"] += gross
    bucket["fees_dollars"] += fees
    bucket["net_pnl_dollars"] += net
    if net > 0:
        bucket["wins"] += 1
    elif net < 0:
        bucket["losses"] += 1
    else:
        bucket["flats"] += 1


def finalize_bucket(bucket: dict[str, Any]) -> dict[str, Any]:
    trades = max(1, int(bucket["trades"]))
    out = dict(bucket)
    for key in ("gross_pnl_dollars", "fees_dollars", "net_pnl_dollars", "qty"):
        out[key] = round(float(out[key]), 4)
    out["avg_net_pnl_dollars"] = round(float(bucket["net_pnl_dollars"]) / trades, 4)
    out["win_rate"] = round(float(bucket["wins"]) / trades, 4)
    return out


def nearest_event(
    events: list[dict[str, Any]],
    *,
    market: str,
    side: str,
    ts: datetime | None,
    max_seconds: float,
) -> dict[str, Any] | None:
    if ts is None:
        return None
    best: tuple[float, dict[str, Any]] | None = None
    for row in events:
        if str(row.get("market") or "") != market:
            continue
        row_side = str(row.get("side") or row.get("mushroom_v28_side") or "").lower()
        if row_side and side and row_side != side:
            continue
        row_ts = parse_event_ts(row.get("ts_wall"))
        if row_ts is None:
            continue
        delta = abs((row_ts - ts).total_seconds())
        if delta <= max_seconds and (best is None or delta < best[0]):
            best = (delta, row)
    return best[1] if best else None


def score_segments(strategy_tag: str, log_source_tag: str) -> dict[str, Any]:
    stats_dir = SCRIPT_DIR / "stats" / strategy_tag
    log_dir = SCRIPT_DIR / "logs" / log_source_tag
    trades = load_csv(stats_dir / "trades.csv")
    events = load_ndjson(log_dir / "execution_events.ndjson")

    approvals = [row for row in events if row.get("event_type") == "mushroom_v28_approved"]
    exits = [row for row in events if row.get("event_type") == "exit_signal_seen"]

    by_raw_phi: dict[str, dict[str, Any]] = defaultdict(stats_bucket)
    by_near_miss: dict[str, dict[str, Any]] = defaultdict(stats_bucket)
    by_exit_family: dict[str, dict[str, Any]] = defaultdict(stats_bucket)
    by_add_on: dict[str, dict[str, Any]] = defaultdict(stats_bucket)
    by_market: dict[str, dict[str, Any]] = defaultdict(stats_bucket)

    market_trade_index: dict[str, int] = defaultdict(int)
    market_first_side: dict[str, str] = {}
    annotated: list[dict[str, Any]] = []

    for trade in trades:
        market = str(trade.get("market") or "")
        side = str(trade.get("side") or "").lower()
        entry_ts = parse_trade_ts(trade.get("entry_ts"))
        exit_ts = parse_trade_ts(trade.get("exit_ts"))
        approval = nearest_event(approvals, market=market, side=side, ts=entry_ts, max_seconds=8.0)
        exit_event = nearest_event(exits, market=market, side=side, ts=exit_ts, max_seconds=12.0)

        raw_approved = bool(approval and approval.get("mushroom_v28_phi_memory_raw_approved"))
        adjusted_approved = bool(approval and approval.get("mushroom_v28_phi_memory_adjusted_approved"))
        action = str((approval or {}).get("mushroom_v28_phi_memory_entry_action") or "")
        if raw_approved:
            raw_phi_segment = "raw_keep"
        elif adjusted_approved or action == "explore":
            raw_phi_segment = "phi_explore"
        else:
            raw_phi_segment = "unknown"

        misses = list((approval or {}).get("mushroom_v28_phi_memory_near_pass_misses") or [])
        near_segment = "strict_pass" if not misses else "+".join(str(item) for item in misses)

        exit_reason = str(
            (exit_event or {}).get("mushroom_v28_phi_memory_adjusted_exit_reason")
            or (exit_event or {}).get("mushroom_v28_exit_reason")
            or ("settlement_or_open" if not trade.get("exit_ts") else "unknown")
        )

        market_trade_index[market] += 1
        if market not in market_first_side:
            market_first_side[market] = side
        add_on_segment = "first_entry" if market_trade_index[market] == 1 else "same_market_add_on"
        if market_trade_index[market] > 1 and side != market_first_side[market]:
            add_on_segment = "same_market_side_switch"

        for segment, table in (
            (raw_phi_segment, by_raw_phi),
            (near_segment, by_near_miss),
            (exit_reason, by_exit_family),
            (add_on_segment, by_add_on),
            (market, by_market),
        ):
            add_trade(table[segment], trade)

        annotated.append(
            {
                "entry_ts": trade.get("entry_ts"),
                "market": market,
                "side": side,
                "qty": fnum(trade.get("qty")),
                "net_pnl_dollars": fnum(trade.get("net_pnl_dollars")),
                "raw_phi_segment": raw_phi_segment,
                "near_segment": near_segment,
                "exit_family": exit_reason,
                "add_on_segment": add_on_segment,
                "entry_edge_cents": fnum((approval or {}).get("mushroom_v28_edge_cents"), None),
                "entry_abs_d_sigma": fnum((approval or {}).get("mushroom_v28_abs_d_sigma"), None),
                "entry_ask_cents": fnum((approval or {}).get("mushroom_v28_ask_cents"), None),
                "exit_p_hold": fnum((exit_event or {}).get("mushroom_v28_p_hold"), None),
            }
        )

    def finish_table(table: dict[str, dict[str, Any]]) -> dict[str, Any]:
        return {key: finalize_bucket(value) for key, value in sorted(table.items())}

    report = {
        "strategy_tag": strategy_tag,
        "log_source_tag": log_source_tag,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "trade_count": len(trades),
        "raw_vs_phi": finish_table(by_raw_phi),
        "near_miss": finish_table(by_near_miss),
        "exit_family": finish_table(by_exit_family),
        "same_market_add_ons": finish_table(by_add_on),
        "by_market": finish_table(by_market),
        "annotated_trades": annotated,
        "inputs": {
            "trades_csv": str(stats_dir / "trades.csv"),
            "execution_events": str(log_dir / "execution_events.ndjson"),
        },
    }
    out_path = stats_dir / "phi_memory_segment_score_latest.json"
    out_path.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
    return report


def main() -> None:
    strategy_tag = os.getenv("PHI_SEGMENT_STRATEGY_TAG") or os.getenv(
        "OUTPUT_STRATEGY_TAG",
        "mushroom_v28_common_clock_phi_reward_memory_size2_live",
    )
    log_source_tag = os.getenv("PHI_SEGMENT_LOG_SOURCE_TAG") or os.getenv(
        "LOG_SOURCE_TAG",
        "live_mushroom_v28_common_clock_phi_reward_memory_size2_live",
    )
    report = score_segments(strategy_tag=strategy_tag, log_source_tag=log_source_tag)
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
