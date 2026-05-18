"""Continuous scorecard for the v28 long-term operating goal."""
from __future__ import annotations

import json
import os
import re
from pathlib import Path
from typing import Any

from probe_v28_forward_physics_registry import build_rows, summarize
from probe_v28_reactivated_shadow_status import LOG_PATH
from probe_v28_reactivated_shadow_status import read_events


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
SCORECARD_JSON = OUT_DIR / "v28_continuous_scorecard_latest.json"
SCORECARD_MD = OUT_DIR / "v28_continuous_scorecard_latest.md"

DEFAULT_START_BALANCE_CENTS = 1276.0
DEFAULT_CURRENT_ACCOUNT_BALANCE_CENTS = 2640.0
DEFAULT_LOSS_STOP_COUNT = 5
DEFAULT_DRAWDOWN_STOP_PCT = 0.40
WATCH_RE = re.compile(r"Watching market (?P<market>\S+)")


def env_float(name: str, default: float) -> float:
    value = os.environ.get(name)
    if value is None or value == "":
        return default
    try:
        return float(value)
    except ValueError:
        return default


def env_int(name: str, default: int) -> int:
    value = os.environ.get(name)
    if value is None or value == "":
        return default
    try:
        return int(value)
    except ValueError:
        return default


def as_float(value: Any) -> float | None:
    if value is None or value == "":
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def classify_failure(row: dict[str, Any]) -> str:
    gross = as_float(row.get("actual_gross_cents"))
    hold = as_float(row.get("hold_gross_cents"))
    exit_value = as_float(row.get("exit_value_cents"))
    side_won = row.get("side_won")

    if gross is None:
        return "open_or_unscored"
    if side_won is None:
        return "exited_unsettled"
    if gross >= 0 and not (exit_value is not None and exit_value < -20):
        return "none"
    if side_won is False:
        return "fv_or_entry_timing_error"
    if side_won is True and exit_value is not None and exit_value < 0:
        return "exit_policy_cost"
    if hold is not None and hold < 0 <= gross:
        return "exit_saved_hold_loss"
    return "execution_or_state_error"


def drawdown(cumulative: list[float]) -> tuple[float, float]:
    peak = 0.0
    max_dd = 0.0
    current = 0.0
    for value in cumulative:
        current = value
        if current > peak:
            peak = current
        max_dd = min(max_dd, current - peak)
    return current, max_dd


def watched_markets() -> list[str]:
    if not LOG_PATH.exists():
        return []
    markets: list[str] = []
    seen: set[str] = set()
    with LOG_PATH.open("r", encoding="utf-8", errors="replace") as handle:
        for line in handle:
            match = WATCH_RE.search(line)
            if not match:
                continue
            market = match.group("market")
            if market not in seen:
                seen.add(market)
                markets.append(market)
    return markets


def summarize_rejections() -> dict[str, Any]:
    events = [event for event in read_events() if event.get("event_type") == "mushroom_v28_rejected"]
    by_reason: dict[str, int] = {}
    by_side: dict[str, int] = {}
    by_market: dict[str, int] = {}
    near_miss_count = 0
    physics_block_counts: dict[str, int] = {}
    for event in events:
        reason = str(event.get("mushroom_v28_reject_reason") or event.get("decision_reason") or "unknown")
        side = str(event.get("side") or event.get("mushroom_v28_side") or "unknown")
        market = str(event.get("market") or "unknown")
        by_reason[reason] = by_reason.get(reason, 0) + 1
        by_side[side] = by_side.get(side, 0) + 1
        by_market[market] = by_market.get(market, 0) + 1
        if (
            event.get("mushroom_v28_status") == "ok"
            and event.get("mushroom_v28_p_ok") is True
            and event.get("mushroom_v28_edge_ok") is True
            and event.get("mushroom_v28_ask_ok") is True
        ):
            near_miss_count += 1
        for key in [
            "time_window",
            "book_stale",
            "btc_stale",
            "ask_too_high",
            "p_below_floor",
            "edge_below_floor",
            "model_price_cap",
            "risk_or_depth",
            "balance",
        ]:
            if reason == key:
                physics_block_counts[key] = physics_block_counts.get(key, 0) + 1
    return {
        "events": len(events),
        "markets": len({str(event.get("market") or "") for event in events if event.get("market")}),
        "near_miss_count": near_miss_count,
        "by_reason": dict(sorted(by_reason.items())),
        "by_side": dict(sorted(by_side.items())),
        "top_markets": dict(sorted(by_market.items(), key=lambda item: item[1], reverse=True)[:12]),
        "physics_block_counts": dict(sorted(physics_block_counts.items())),
    }


def build_scorecard() -> dict[str, Any]:
    rows = build_rows()
    registry_summary = summarize(rows)
    watched = watched_markets()
    rejection_summary = summarize_rejections()
    entered_markets = {str(row.get("market")) for row in rows if row.get("market")}
    scored = [row for row in rows if row.get("actual_gross_cents") is not None]
    settled = [row for row in rows if row.get("side_won") is not None]

    cumulative: list[float] = []
    total = 0.0
    loss_streak = 0
    max_loss_streak = 0
    for row in scored:
        gross = float(row["actual_gross_cents"])
        total += gross
        cumulative.append(total)
        if gross < 0:
            loss_streak += 1
            max_loss_streak = max(max_loss_streak, loss_streak)
        elif gross > 0:
            loss_streak = 0

    current_cents, max_dd_cents = drawdown(cumulative)
    start_balance_cents = env_float("V28_TRIAL_START_BALANCE_CENTS", DEFAULT_START_BALANCE_CENTS)
    current_account_balance_cents = env_float(
        "V28_CURRENT_ACCOUNT_BALANCE_CENTS",
        DEFAULT_CURRENT_ACCOUNT_BALANCE_CENTS,
    )
    loss_stop_count = env_int("V28_MEDIUM_RISK_LOSS_STOP_COUNT", DEFAULT_LOSS_STOP_COUNT)
    drawdown_stop_pct = env_float("V28_MEDIUM_RISK_DRAWDOWN_STOP_PCT", DEFAULT_DRAWDOWN_STOP_PCT)
    net_losses = sum(1 for row in scored if float(row["actual_gross_cents"]) < 0)
    drawdown_pct = abs(max_dd_cents) / start_balance_cents if start_balance_cents > 0 else 0.0
    risk_stop = net_losses >= loss_stop_count or drawdown_pct >= drawdown_stop_pct

    failure_counts: dict[str, int] = {}
    for row in rows:
        label = classify_failure(row)
        row["failure_class"] = label
        failure_counts[label] = failure_counts.get(label, 0) + 1

    return {
        "rows": rows,
        "summary": {
            "entries": len(rows),
            "watched_markets": len(watched),
            "entered_markets": len(entered_markets),
            "coverage_pct": (len(entered_markets) / len(watched) * 100.0) if watched else None,
            "scored_trades": len(scored),
            "settled_trades": len(settled),
            "wins": sum(1 for row in settled if row.get("side_won") is True),
            "gross_cents": total,
            "hold_gross_cents": registry_summary["hold_gross_cents"],
            "exit_value_cents": total - float(registry_summary["hold_gross_cents"]),
            "trial_start_balance_cents": start_balance_cents,
            "current_account_balance_cents": current_account_balance_cents,
            "roi_pct": (total / start_balance_cents * 100.0) if start_balance_cents > 0 else None,
            "pnl_pct_of_current_account": (
                total / current_account_balance_cents * 100.0
                if current_account_balance_cents > 0
                else None
            ),
            "max_drawdown_cents": max_dd_cents,
            "max_drawdown_pct": drawdown_pct * 100.0,
            "net_losses": net_losses,
            "max_loss_streak": max_loss_streak,
            "risk_stop": risk_stop,
            "risk_stop_reason": (
                "loss_count" if net_losses >= loss_stop_count else "drawdown" if drawdown_pct >= drawdown_stop_pct else ""
            ),
            "avg_brier": registry_summary["avg_brier"],
            "failure_counts": failure_counts,
            "physics_flags": registry_summary["by_flag"],
            "reject_telemetry": rejection_summary,
            "watched_market_list": watched,
        },
    }


def write_md(scorecard: dict[str, Any]) -> None:
    summary = scorecard["summary"]
    rows = scorecard["rows"]
    lines = [
        "# v28 Continuous Scorecard",
        "",
        "- Goal: durable risk-adjusted ROI from the v28 BTC 15m strategy.",
        "- Mode: quiet continuous monitoring; old logs are diagnostic only.",
        "",
        "## Risk-Adjusted Score",
        "",
        f"- Entries: `{summary['entries']}`",
        f"- Watched markets: `{summary['watched_markets']}`",
        f"- Entered markets: `{summary['entered_markets']}`",
        f"- Shadow coverage: `{summary['coverage_pct']:.2f}%`" if summary["coverage_pct"] is not None else "- Shadow coverage: `None`",
        f"- Scored trades: `{summary['scored_trades']}`",
        f"- Settled trades: `{summary['settled_trades']}`",
        f"- Wins: `{summary['wins']}`",
        f"- Gross P&L: `${summary['gross_cents'] / 100.0:.2f}`",
        f"- Current account balance reference: `${summary['current_account_balance_cents'] / 100.0:.2f}`",
        f"- Hold-to-settlement P&L: `${summary['hold_gross_cents'] / 100.0:.2f}`",
        f"- Exit value vs hold: `${summary['exit_value_cents'] / 100.0:.2f}`",
        f"- Trial ROI on start balance: `{summary['roi_pct']:.2f}%`",
        f"- Shadow P&L as % of current account: `{summary['pnl_pct_of_current_account']:.2f}%`",
        f"- Max drawdown: `${summary['max_drawdown_cents'] / 100.0:.2f}` / `{summary['max_drawdown_pct']:.2f}%`",
        f"- Net losing trades: `{summary['net_losses']}`",
        f"- Max loss streak: `{summary['max_loss_streak']}`",
        f"- Risk stop active: `{summary['risk_stop']}` `{summary['risk_stop_reason']}`",
        f"- Avg Brier: `{summary['avg_brier']}`",
        "",
        "## Reject / Opportunity Telemetry",
        "",
        f"- Reject events: `{summary['reject_telemetry']['events']}`",
        f"- Reject markets: `{summary['reject_telemetry']['markets']}`",
        f"- Near misses: `{summary['reject_telemetry']['near_miss_count']}`",
        "",
        "### Reject Reasons",
        "",
    ]
    for key, value in sorted(summary["reject_telemetry"]["by_reason"].items()):
        lines.append(f"- `{key}`: {value}")

    lines.extend([
        "",
        "## Failure Attribution",
        "",
    ])
    for key, value in sorted(summary["failure_counts"].items()):
        lines.append(f"- `{key}`: {value}")

    lines.extend(["", "## Latest Rows", ""])
    if rows:
        lines.append("| market | side | result | gross c | hold c | exit value c | failure | flags |")
        lines.append("|---|---|---|---:|---:|---:|---|---|")
        for row in rows[-12:]:
            flags = ",".join(
                key
                for key in [
                    "h1_feed_fresh",
                    "h2_thin_touch_depth",
                    "h2_crowded_depth",
                    "h4_large_model_disagreement",
                    "h4_old_model_opposes_side",
                    "h5_late_high_sigma",
                    "h6_recross_hazard_high",
                ]
                if row.get(key) is True
            )
            lines.append(
                "| {market} | {side} | {result} | {actual_gross_cents} | {hold_gross_cents} | {exit_value_cents} | {failure_class} | {flags} |".format(
                    flags=flags,
                    **row,
                )
            )
    else:
        lines.append("No v28 forward rows yet.")
    SCORECARD_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    scorecard = build_scorecard()
    SCORECARD_JSON.write_text(json.dumps(scorecard, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_md(scorecard)
    print(str(SCORECARD_MD))


if __name__ == "__main__":
    main()
