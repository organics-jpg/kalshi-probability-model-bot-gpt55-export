"""Live status snapshot for the v28 common-clock exit-guard trial.

This probe is observational only. It reads local lock/log/score artifacts and,
when credentials are available, reconciles current Kalshi balance, positions,
resting orders, and recent fills.
"""
from __future__ import annotations

import ctypes
import json
import os
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"

STRATEGY_TAG = os.getenv(
    "V28_COMMON_CLOCK_STRATEGY_TAG",
    "mushroom_v28_common_clock_exit_guard_v1_size1_live",
)
LOG_SOURCE_TAG = os.getenv(
    "V28_COMMON_CLOCK_LOG_SOURCE_TAG",
    "live_mushroom_v28_common_clock_exit_guard_size1",
)

LOCK_PATH = ROOT / "state" / "live_trading.lock"
LOG_DIR = ROOT / "logs" / LOG_SOURCE_TAG
BOT_LOG = LOG_DIR / "bot.log"
EXECUTION_EVENTS = LOG_DIR / "execution_events.ndjson"
GUARD_LEDGER = LOG_DIR / "mushroom_v28_exit_guard_shadow.ndjson"
RECONCILIATION_LEDGER = LOG_DIR / "exchange_reconciliation.ndjson"
LIFECYCLE_LEDGER = LOG_DIR / "v28_trade_lifecycle.ndjson"
SCORE_SUMMARY = ROOT / "stats" / STRATEGY_TAG / "summary.json"

def env_path(name: str, default: Path) -> Path:
    value = os.getenv(name)
    if not value:
        return default
    return Path(value).expanduser().resolve()


OUT_JSON = env_path(
    "V28_COMMON_CLOCK_STATUS_JSON",
    OUT_DIR / "v28_common_clock_live_trial_status_latest.json",
)
OUT_MD = env_path(
    "V28_COMMON_CLOCK_STATUS_MD",
    OUT_DIR / "v28_common_clock_live_trial_status_latest.md",
)


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def parse_ts(value: Any) -> datetime | None:
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return datetime.fromtimestamp(float(value), tz=timezone.utc)
    text = str(value).strip()
    if not text:
        return None
    if text.isdigit():
        return datetime.fromtimestamp(float(text), tz=timezone.utc)
    try:
        parsed = datetime.fromisoformat(text.replace("Z", "+00:00"))
    except ValueError:
        return None
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
    return payload if isinstance(payload, dict) else {}


def process_running(pid: Any) -> bool:
    try:
        pid_int = int(pid)
    except (TypeError, ValueError):
        return False
    if pid_int <= 0:
        return False
    handle = ctypes.windll.kernel32.OpenProcess(0x1000, False, pid_int)
    if not handle:
        return False
    ctypes.windll.kernel32.CloseHandle(handle)
    return True


def tail_lines(path: Path, limit: int) -> list[str]:
    if not path.exists():
        return []
    lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    return lines[-limit:]


def parse_event_lines(path: Path, limit: int = 200) -> dict[str, Any]:
    events: list[dict[str, Any]] = []
    for line in tail_lines(path, limit):
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(event, dict):
            events.append(event)
    event_types = Counter(str(event.get("event_type", "")) for event in events)
    reject_reasons = Counter(
        str(event.get("decision_reason") or event.get("mushroom_v28_reject_reason") or "<blank>")
        for event in events
    )
    approved = [event for event in events if event.get("mushroom_v28_approved") is True]
    order_like = [
        event
        for event in events
        if event.get("order_id")
        or event.get("client_order_id")
        or str(event.get("event_type", "")).lower().find("order") >= 0
        or str(event.get("event_type", "")).lower().find("fill") >= 0
    ]
    latest = events[-1] if events else {}
    return {
        "events_scanned": len(events),
        "event_types": dict(event_types),
        "reject_reasons": dict(reject_reasons),
        "approved_seen": len(approved),
        "order_like_seen": len(order_like),
        "latest_event_type": latest.get("event_type"),
        "latest_decision_reason": latest.get("decision_reason")
        or latest.get("mushroom_v28_reject_reason"),
        "latest_market": latest.get("market"),
        "latest_wall_ts": latest.get("ts_wall"),
        "latest_btc_ok": latest.get("mushroom_v28_btc_ok"),
        "latest_balance_ok": latest.get("mushroom_v28_balance_ok"),
        "latest_position_size": latest.get("position_size"),
    }


def parse_lifecycle_lines(path: Path, limit: int = 300) -> dict[str, Any]:
    events: list[dict[str, Any]] = []
    for line in tail_lines(path, limit):
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(event, dict):
            events.append(event)
    event_counts = Counter(str(event.get("event", "")) for event in events)
    actions = Counter(str(event.get("action", "")) for event in events if event.get("action"))
    buckets = Counter(str(event.get("bucket", "")) for event in events if event.get("bucket"))
    latest = events[-1] if events else {}
    rewards = [event for event in events if event.get("event") == "lifecycle_settlement_reward"]
    reward_delta = sum(number_or_zero(event.get("reward_delta_cents")) for event in rewards)
    return {
        "events_scanned": len(events),
        "event_counts": dict(event_counts),
        "actions": dict(actions),
        "buckets": dict(buckets),
        "reward_delta_cents_tail": round(reward_delta, 4),
        "latest_event": latest.get("event"),
        "latest_action": latest.get("action"),
        "latest_bucket": latest.get("bucket"),
        "latest_market": latest.get("market_ticker"),
        "latest_ts": latest.get("ts"),
    }


def kalshi_snapshot() -> dict[str, Any]:
    try:
        from kalshi_btc15m_bot_ws import KalshiClient, load_config

        client = KalshiClient(load_config())
        fills = client.get_fills(limit=100)
        return {
            "available": True,
            "balance": client.get_balance(),
            "positions": client.get_positions(),
            "resting_orders": client.get_resting_orders(),
            "recent_fills_count": len(fills) if isinstance(fills, list) else None,
            "recent_fills": fills if isinstance(fills, list) else [],
        }
    except Exception as exc:  # noqa: BLE001 - status probe should report, not fail.
        return {"available": False, "error": repr(exc)}


def number_or_zero(value: Any) -> float:
    try:
        if value is None or value == "":
            return 0.0
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def fill_count(fill: dict[str, Any]) -> float:
    return abs(number_or_zero(fill.get("count_fp") or fill.get("count") or fill.get("contracts")))


def fill_fee_dollars(fill: dict[str, Any]) -> float:
    return abs(number_or_zero(fill.get("fee_cost") or fill.get("fee_cost_dollars") or fill.get("fees_dollars")))


def fill_contract_price_dollars(fill: dict[str, Any]) -> float:
    side = str(fill.get("side") or "").strip().lower()
    action = str(fill.get("action") or "").strip().lower()
    yes_price = number_or_zero(fill.get("yes_price_dollars") or fill.get("yes_price"))
    no_price = number_or_zero(fill.get("no_price_dollars") or fill.get("no_price"))
    if action == "sell":
        # Kalshi sell fills can report the complementary side while both side
        # prices are present. The contract sold is therefore the opposite price.
        if side == "yes":
            return no_price
        if side == "no":
            return yes_price
    if side == "yes":
        return yes_price
    if side == "no":
        return no_price
    return yes_price or no_price


def position_ticker(row: dict[str, Any]) -> str:
    return str(row.get("ticker") or row.get("market_ticker") or "").strip()


def active_position_rows(positions: Any) -> list[dict[str, Any]]:
    if not isinstance(positions, list):
        return []
    active: list[dict[str, Any]] = []
    for row in positions:
        if not isinstance(row, dict):
            continue
        position = abs(number_or_zero(row.get("position") or row.get("position_fp")))
        exposure = abs(number_or_zero(row.get("market_exposure_dollars")))
        resting = abs(number_or_zero(row.get("resting_orders_count")))
        if position > 0 or exposure > 0 or resting > 0:
            active.append(row)
    return active


def fill_timestamp(fill: dict[str, Any]) -> datetime | None:
    for key in ("created_time", "created_at", "ts", "timestamp"):
        parsed = parse_ts(fill.get(key))
        if parsed is not None:
            return parsed
    return None


def fills_since(fills: Any, start_ts: Any) -> list[dict[str, Any]]:
    if not isinstance(fills, list):
        return []
    start = parse_ts(start_ts)
    if start is None:
        return []
    out: list[dict[str, Any]] = []
    for fill in fills:
        if not isinstance(fill, dict):
            continue
        fill_ts = fill_timestamp(fill)
        if fill_ts is not None and fill_ts >= start:
            out.append(fill)
    return out


def exchange_accounting_summary(
    *,
    exchange: dict[str, Any],
    candidate_fills: list[dict[str, Any]],
) -> dict[str, Any]:
    balance = exchange.get("balance") if exchange.get("available") else {}
    positions = exchange.get("positions") if exchange.get("available") else []
    positions_by_market = {
        position_ticker(row): row
        for row in positions
        if isinstance(row, dict) and position_ticker(row)
    } if isinstance(positions, list) else {}
    markets = sorted(
        {
            str(fill.get("market_ticker") or fill.get("ticker") or "").strip()
            for fill in candidate_fills
            if str(fill.get("market_ticker") or fill.get("ticker") or "").strip()
        }
    )
    by_market: dict[str, Any] = {}
    totals = {
        "fills": 0,
        "buy_contracts": 0.0,
        "sell_contracts": 0.0,
        "buy_notional_dollars": 0.0,
        "sell_notional_dollars": 0.0,
        "fill_fees_dollars": 0.0,
        "exchange_gross_realized_pnl_dollars": 0.0,
        "exchange_fees_paid_dollars": 0.0,
        "exchange_net_realized_pnl_after_fees_dollars": 0.0,
    }
    for market in markets:
        fills = [
            fill for fill in candidate_fills
            if str(fill.get("market_ticker") or fill.get("ticker") or "").strip() == market
        ]
        buy_contracts = 0.0
        sell_contracts = 0.0
        buy_notional = 0.0
        sell_notional = 0.0
        fill_fees = 0.0
        for fill in fills:
            count = fill_count(fill)
            notional = count * fill_contract_price_dollars(fill)
            fee = fill_fee_dollars(fill)
            fill_fees += fee
            if str(fill.get("action") or "").strip().lower() == "buy":
                buy_contracts += count
                buy_notional += notional
            elif str(fill.get("action") or "").strip().lower() == "sell":
                sell_contracts += count
                sell_notional += notional
        position = positions_by_market.get(market, {})
        position_has_realized = (
            isinstance(position, dict)
            and position.get("realized_pnl_dollars") not in {None, ""}
        )
        if position_has_realized:
            gross_realized = number_or_zero(position.get("realized_pnl_dollars"))
            gross_realized_source = "kalshi_position"
        else:
            matched_contracts = min(buy_contracts, sell_contracts)
            if matched_contracts > 0 and buy_contracts > 0 and sell_contracts > 0:
                avg_buy = buy_notional / buy_contracts
                avg_sell = sell_notional / sell_contracts
                gross_realized = (avg_sell - avg_buy) * matched_contracts
                gross_realized_source = "fills_matched_notional"
            else:
                gross_realized = 0.0
                gross_realized_source = "unrealized_or_no_round_trip"
        fees_paid = number_or_zero(position.get("fees_paid_dollars")) or fill_fees
        net_after_fees = gross_realized - fees_paid
        row = {
            "fills": len(fills),
            "buy_contracts": round(buy_contracts, 4),
            "sell_contracts": round(sell_contracts, 4),
            "buy_notional_dollars": round(buy_notional, 4),
            "sell_notional_dollars": round(sell_notional, 4),
            "fill_fees_dollars": round(fill_fees, 4),
            "exchange_gross_realized_pnl_dollars": round(gross_realized, 4),
            "exchange_gross_realized_source": gross_realized_source,
            "exchange_fees_paid_dollars": round(fees_paid, 4),
            "exchange_net_realized_pnl_after_fees_dollars": round(net_after_fees, 4),
            "exchange_position_fp": position.get("position_fp") if isinstance(position, dict) else None,
            "exchange_market_exposure_dollars": position.get("market_exposure_dollars") if isinstance(position, dict) else None,
        }
        by_market[market] = row
        totals["fills"] += len(fills)
        totals["buy_contracts"] += buy_contracts
        totals["sell_contracts"] += sell_contracts
        totals["buy_notional_dollars"] += buy_notional
        totals["sell_notional_dollars"] += sell_notional
        totals["fill_fees_dollars"] += fill_fees
        totals["exchange_gross_realized_pnl_dollars"] += gross_realized
        totals["exchange_fees_paid_dollars"] += fees_paid
        totals["exchange_net_realized_pnl_after_fees_dollars"] += net_after_fees
    rounded_totals = {
        key: (round(value, 4) if isinstance(value, float) else value)
        for key, value in totals.items()
    }
    return {
        "balance": balance,
        "balance_cents": balance.get("balance") if isinstance(balance, dict) else None,
        "portfolio_value_cents": balance.get("portfolio_value") if isinstance(balance, dict) else None,
        "markets": markets,
        "by_market": by_market,
        "totals": rounded_totals,
        "source": "kalshi_api_positions_and_fills_since_live_lock",
    }


def evidence_path(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def append_reconciliation_snapshot(report: dict[str, Any]) -> bool:
    """Persist an exchange snapshot for live-test auditability."""
    exchange = report.get("exchange") or {}
    if not exchange.get("available"):
        return False
    RECONCILIATION_LEDGER.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "event_type": "common_clock_live_status_exchange_reconciliation",
        "stage": "status_snapshot",
        "ts_wall": report.get("generated_at_utc"),
        "strategy_tag": report.get("strategy_tag"),
        "log_source_tag": report.get("log_source_tag"),
        "status": report.get("status"),
        "lock_matches": report.get("lock_matches"),
        "process_running": report.get("process_running"),
        "score": report.get("score"),
        "exchange_active_positions_count": report.get("exchange_active_positions_count"),
        "exchange_resting_orders_count": report.get("exchange_resting_orders_count"),
        "balance": exchange.get("balance"),
        "positions": exchange.get("positions"),
        "resting_orders": exchange.get("resting_orders"),
        "recent_fills_count": exchange.get("recent_fills_count"),
        "recent_fills": exchange.get("recent_fills"),
        "run_start_utc": (report.get("lock") or {}).get("acquired_at"),
        "candidate_recent_fills_since_run_count": report.get("candidate_recent_fills_since_run_count"),
        "candidate_recent_fills_since_run": report.get("candidate_recent_fills_since_run"),
        "exchange_accounting": report.get("exchange_accounting"),
    }
    with RECONCILIATION_LEDGER.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(payload, sort_keys=True, default=str) + "\n")
    return True


def build_report() -> dict[str, Any]:
    lock = load_json(LOCK_PATH)
    score = load_json(SCORE_SUMMARY)
    lock_matches = lock.get("strategy_tag") == STRATEGY_TAG
    running = process_running(lock.get("pid")) if lock_matches else False
    execution_summary = parse_event_lines(EXECUTION_EVENTS)
    lifecycle_summary = parse_lifecycle_lines(LIFECYCLE_LEDGER)
    exchange = kalshi_snapshot()
    open_positions = exchange.get("positions") if exchange.get("available") else None
    resting_orders = exchange.get("resting_orders") if exchange.get("available") else None
    active_positions = active_position_rows(open_positions)
    candidate_recent_fills = fills_since(exchange.get("recent_fills"), lock.get("acquired_at"))
    exchange_accounting = exchange_accounting_summary(
        exchange=exchange,
        candidate_fills=candidate_recent_fills,
    )
    active_exposure = bool(active_positions) or bool(resting_orders)
    entries_total = int(score.get("entries_total", 0) or 0)
    completed_round_trips = int(score.get("completed_round_trips", 0) or 0)
    net_pnl_dollars = float(score.get("net_pnl_total_dollars", 0) or 0)
    status = "running_waiting_for_first_entry"
    if not lock_matches:
        status = "not_running_lock_missing_or_other_strategy"
    elif not running:
        status = "not_running_stale_lock"
    elif active_exposure:
        status = "running_with_exchange_exposure"
    elif completed_round_trips > 0:
        status = "running_scored_round_trips"
    elif entries_total > 0:
        status = "running_with_local_entries"

    return {
        "generated_at_utc": utc_now_iso(),
        "strategy_tag": STRATEGY_TAG,
        "log_source_tag": LOG_SOURCE_TAG,
        "status": status,
        "lock": lock,
        "lock_matches": lock_matches,
        "process_running": running,
        "score": {
            "entries_total": entries_total,
            "completed_round_trips": completed_round_trips,
            "open_positions": int(score.get("open_positions", 0) or 0),
            "net_pnl_total_dollars": net_pnl_dollars,
            "diagnosis": score.get("diagnosis"),
            "score_mode": score.get("score_mode"),
        },
        "execution_events": execution_summary,
        "lifecycle": lifecycle_summary,
        "exchange": exchange,
        "exchange_accounting": exchange_accounting,
        "candidate_recent_fills_since_run": candidate_recent_fills,
        "candidate_recent_fills_since_run_count": len(candidate_recent_fills),
        "exchange_active_positions": active_positions,
        "exchange_active_positions_count": len(active_positions),
        "exchange_resting_orders_count": len(resting_orders) if isinstance(resting_orders, list) else None,
        "artifacts": {
            "bot_log": evidence_path(BOT_LOG),
            "execution_events": evidence_path(EXECUTION_EVENTS),
            "guard_ledger": evidence_path(GUARD_LEDGER),
            "reconciliation_ledger": evidence_path(RECONCILIATION_LEDGER),
            "lifecycle_ledger": evidence_path(LIFECYCLE_LEDGER),
            "score_summary": evidence_path(SCORE_SUMMARY),
        },
        "artifact_exists": {
            "bot_log": BOT_LOG.exists(),
            "execution_events": EXECUTION_EVENTS.exists(),
            "guard_ledger": GUARD_LEDGER.exists(),
            "reconciliation_ledger": RECONCILIATION_LEDGER.exists(),
            "lifecycle_ledger": LIFECYCLE_LEDGER.exists(),
            "score_summary": SCORE_SUMMARY.exists(),
        },
    }


def write_report(report: dict[str, Any]) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    appended_reconciliation = append_reconciliation_snapshot(report)
    report["artifact_exists"]["reconciliation_ledger"] = RECONCILIATION_LEDGER.exists()
    report["reconciliation_snapshot_appended"] = appended_reconciliation
    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_MD.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8")
    score = report["score"]
    events = report["execution_events"]
    lifecycle = report.get("lifecycle") or {}
    exchange = report["exchange"]
    accounting = report.get("exchange_accounting") or {}
    accounting_totals = accounting.get("totals") or {}
    positions = exchange.get("positions") if exchange.get("available") else "unavailable"
    resting_orders = exchange.get("resting_orders") if exchange.get("available") else "unavailable"
    lines = [
        "# v28 Common-Clock Live Trial Status",
        "",
        f"- Generated UTC: `{report['generated_at_utc']}`",
        f"- Status: `{report['status']}`",
        f"- Strategy: `{report['strategy_tag']}`",
        f"- Lock/process: `{report['lock_matches']}` / `{report['process_running']}`",
        f"- Score entries/round trips/net: `{score['entries_total']}` / `{score['completed_round_trips']}` / `${score['net_pnl_total_dollars']:.2f}`",
        f"- Latest event: `{events.get('latest_event_type')}` / `{events.get('latest_decision_reason')}` at `{events.get('latest_wall_ts')}`",
        f"- Event counts: `{events.get('event_types')}`",
        f"- Reject reasons: `{events.get('reject_reasons')}`",
        f"- Lifecycle actions/buckets: `{lifecycle.get('actions')}` / `{lifecycle.get('buckets')}`",
        f"- Lifecycle latest/reward tail: `{lifecycle.get('latest_event')}` / `{lifecycle.get('latest_action')}` / `{lifecycle.get('latest_bucket')}` / `{lifecycle.get('reward_delta_cents_tail')}`c",
        f"- Exchange positions: `{positions}`",
        f"- Exchange active positions count: `{report.get('exchange_active_positions_count')}`",
        f"- Exchange resting orders: `{resting_orders}`",
        f"- Exchange resting orders count: `{report.get('exchange_resting_orders_count')}`",
        f"- Recent fills returned: `{exchange.get('recent_fills_count')}`",
        f"- Candidate recent fills since run start: `{report.get('candidate_recent_fills_since_run_count')}`",
        f"- Kalshi balance cents / portfolio cents: `{accounting.get('balance_cents')}` / `{accounting.get('portfolio_value_cents')}`",
        f"- Kalshi fills/fees since run: `{accounting_totals.get('fills')}` / `${float(accounting_totals.get('exchange_fees_paid_dollars') or 0.0):.2f}`",
        f"- Kalshi gross/net realized since run: `${float(accounting_totals.get('exchange_gross_realized_pnl_dollars') or 0.0):.2f}` / `${float(accounting_totals.get('exchange_net_realized_pnl_after_fees_dollars') or 0.0):.2f}`",
        f"- Reconciliation snapshot appended: `{report.get('reconciliation_snapshot_appended')}`",
        "",
        "## Artifacts",
    ]
    for name, path in report["artifacts"].items():
        lines.append(f"- {name}: `{path}` exists=`{report['artifact_exists'].get(name)}`")
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    write_report(build_report())


if __name__ == "__main__":
    main()
