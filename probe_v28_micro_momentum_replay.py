from __future__ import annotations

import csv
import json
import math
from bisect import bisect_right
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from statistics import mean
from typing import Any
from zoneinfo import ZoneInfo


ROOT = Path(__file__).resolve().parent
LIVE_TAG = "live_mushroom_v28_common_clock_exit_guard_sourcefix_hybridfpt_robustrank1_btcrest_size2_multi_exactgate_depthratio"
STRATEGY_TAG = "mushroom_v28_common_clock_exit_guard_v1_sourcefix_hybridfpt_robustrank1_btcrest_size2_multi_exactgate_depthratio_live"
EVENTS_PATH = ROOT / "logs" / LIVE_TAG / "execution_events.ndjson"
TRADES_PATH = ROOT / "stats" / STRATEGY_TAG / "trades.csv"
MARKET_RESULTS_PATH = ROOT / "stats" / STRATEGY_TAG / "market_results.csv"
OUT_JSON = ROOT / "logs" / "edge_research" / "v28_micro_momentum_replay_latest.json"
OUT_MD = ROOT / "logs" / "edge_research" / "v28_micro_momentum_replay_latest.md"

LOCAL_TZ = ZoneInfo("America/New_York")
UTC = ZoneInfo("UTC")
WINDOWS_SECONDS = (15, 30, 60)
CAPS_CENTS = (0.5, 1.0, 2.0, 3.0)
MOMENTUM_FILTER_THRESHOLDS = (-0.9, -0.75, -0.5, -0.25, 0.0)
LOW_EDGE_MARGINS_CENTS = (3.0, 5.0, 8.0)


def parse_ts(value: str | None) -> datetime | None:
    if not value:
        return None
    value = value.strip()
    if not value:
        return None
    if "T" in value:
        return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(UTC)
    return datetime.strptime(value, "%Y-%m-%d %H:%M:%S").replace(tzinfo=LOCAL_TZ).astimezone(UTC)


def fnum(value: Any, default: float = math.nan) -> float:
    try:
        if value is None or value == "":
            return default
        return float(value)
    except (TypeError, ValueError):
        return default


def bval(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if value is None:
        return False
    return str(value).lower() == "true"


def side_sign(side: str) -> int:
    return 1 if str(side).lower() == "yes" else -1


@dataclass
class PricePoint:
    ts: datetime
    price: float


def load_events() -> list[dict[str, Any]]:
    events: list[dict[str, Any]] = []
    with EVENTS_PATH.open("r", encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            row = json.loads(line)
            ts = parse_ts(row.get("ts_wall"))
            if ts is None:
                continue
            row["_ts"] = ts
            events.append(row)
    events.sort(key=lambda r: r["_ts"])
    return events


def load_trades() -> list[dict[str, Any]]:
    with TRADES_PATH.open("r", encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))
    for row in rows:
        row["_entry_ts"] = parse_ts(row.get("entry_ts"))
        row["_net_pnl"] = fnum(row.get("net_pnl_dollars"), 0.0)
    return rows


def load_market_results() -> dict[str, str]:
    if not MARKET_RESULTS_PATH.exists():
        return {}
    with MARKET_RESULTS_PATH.open("r", encoding="utf-8", newline="") as f:
        return {r["market"]: str(r.get("result", "")).lower() for r in csv.DictReader(f)}


def build_price_series(events: list[dict[str, Any]]) -> tuple[list[datetime], list[PricePoint]]:
    points: list[PricePoint] = []
    for row in events:
        price = fnum(row.get("mushroom_v28_btc_price"))
        if math.isfinite(price) and price > 0:
            points.append(PricePoint(row["_ts"], price))
    points.sort(key=lambda p: p.ts)
    return [p.ts for p in points], points


def price_at_or_before(times: list[datetime], points: list[PricePoint], ts: datetime) -> PricePoint | None:
    idx = bisect_right(times, ts) - 1
    if idx < 0:
        return None
    return points[idx]


def micro_momentum_score(
    *,
    side: str,
    ts: datetime,
    price_now: float,
    sigma_t_dollars: float,
    horizon_seconds: float,
    times: list[datetime],
    points: list[PricePoint],
) -> dict[str, Any]:
    details = []
    signed = side_sign(side)
    horizon = max(float(horizon_seconds), 1.0)
    sigma = max(float(sigma_t_dollars), 1e-9)
    for window in WINDOWS_SECONDS:
        lag_ts = datetime.fromtimestamp(ts.timestamp() - window, tz=UTC)
        lag = price_at_or_before(times, points, lag_ts)
        if lag is None:
            continue
        age_error = abs((lag.ts - lag_ts).total_seconds())
        if age_error > max(10.0, window):
            continue
        toward_dollars = signed * (float(price_now) - lag.price)
        local_sigma = sigma * math.sqrt(window / horizon)
        normalized = max(-1.0, min(1.0, toward_dollars / max(local_sigma, 1e-9)))
        details.append(
            {
                "window_seconds": window,
                "lag_price": round(lag.price, 2),
                "toward_dollars": round(toward_dollars, 4),
                "local_sigma_dollars": round(local_sigma, 4),
                "normalized": round(normalized, 6),
            }
        )
    score = mean(d["normalized"] for d in details) if details else 0.0
    return {"score": round(score, 6), "details": details}


def event_edge(row: dict[str, Any]) -> float:
    return fnum(row.get("mushroom_v28_edge_cents"), fnum(row.get("mushroom_edge_cents")))


def event_min_edge(row: dict[str, Any]) -> float:
    return max(3.0, fnum(row.get("mushroom_v28_min_edge_cents"), fnum(row.get("mushroom_min_edge_cents"), 3.0)))


def event_sigma(row: dict[str, Any]) -> float:
    return fnum(row.get("mushroom_v28_sigma_t_dollars"), fnum(row.get("mushroom_sigma_t_dollars")))


def event_d_sigma(row: dict[str, Any]) -> float:
    return fnum(row.get("mushroom_v28_d_sigma"), fnum(row.get("mushroom_d_sigma")))


def event_seconds_to_close(row: dict[str, Any]) -> float:
    return fnum(row.get("mushroom_v28_seconds_to_close"), fnum(row.get("mushroom_seconds_to_close"), 900.0))


def event_btc_price(row: dict[str, Any]) -> float:
    return fnum(row.get("mushroom_v28_btc_price"), fnum(row.get("mushroom_btc_price")))


def has_decision_context(row: dict[str, Any]) -> bool:
    return math.isfinite(event_edge(row)) and math.isfinite(event_sigma(row))


def match_entry_event(trade: dict[str, Any], fill_events: list[dict[str, Any]]) -> dict[str, Any] | None:
    ts = trade.get("_entry_ts")
    if ts is None:
        return None
    market = trade.get("market")
    side = trade.get("side")
    candidates = [
        e
        for e in fill_events
        if e.get("market") == market
        and str(e.get("side", "")).lower() == str(side).lower()
        and abs((e["_ts"] - ts).total_seconds()) <= 5.0
    ]
    if not candidates:
        candidates = [
            e
            for e in fill_events
            if e.get("market") == market
            and str(e.get("side", "")).lower() == str(side).lower()
            and abs((e["_ts"] - ts).total_seconds()) <= 90.0
        ]
    if not candidates:
        return None
    return min(candidates, key=lambda e: abs((e["_ts"] - ts).total_seconds()))


def match_decision_context(fill: dict[str, Any], events: list[dict[str, Any]]) -> dict[str, Any]:
    if has_decision_context(fill):
        return fill
    market = fill.get("market")
    side = str(fill.get("side", "")).lower()
    ts = fill["_ts"]
    context_types = {"mushroom_v28_approved", "signal_seen", "plan_built", "execution_deferred", "fill_full"}
    candidates = [
        e
        for e in events
        if e.get("event_type") in context_types
        and e.get("market") == market
        and str(e.get("side", "")).lower() == side
        and e["_ts"] <= ts
        and 0 <= (ts - e["_ts"]).total_seconds() <= 5.0
        and has_decision_context(e)
    ]
    if not candidates:
        candidates = [
            e
            for e in events
            if e.get("market") == market
            and str(e.get("side", "")).lower() == side
            and abs((e["_ts"] - ts).total_seconds()) <= 20.0
            and has_decision_context(e)
        ]
    if not candidates:
        return fill
    return max(candidates, key=lambda e: e["_ts"])


def exact_gate_like(row: dict[str, Any]) -> bool:
    # The live exact-gate run should only use the frozen rank1 entry gates plus
    # execution/risk safety. This helper is for rough "could have added" counts.
    if not bval(row.get("mushroom_v28_book_ok")):
        return False
    if not bval(row.get("mushroom_v28_time_ok")):
        return False
    if not bval(row.get("mushroom_v28_ask_ok")):
        return False
    if not bval(row.get("mushroom_v28_btc_ok")):
        return False
    if not bval(row.get("mushroom_v28_risk_ok")):
        return False
    if not bval(row.get("mushroom_v28_balance_ok")):
        return False
    abs_d = abs(fnum(row.get("mushroom_v28_d_sigma")))
    if not (0.80 <= abs_d <= 1.10):
        return False
    if fnum(row.get("mushroom_v28_ask_cents")) > 85:
        return False
    if fnum(row.get("mushroom_v28_seconds_to_close")) < 120:
        return False
    return True


def main() -> None:
    events = load_events()
    trades = load_trades()
    market_results = load_market_results()
    times, points = build_price_series(events)
    fill_events = [e for e in events if e.get("event_type") == "fill_full"]

    trade_rows = []
    for trade in trades:
        entry = match_entry_event(trade, fill_events)
        if entry is None:
            trade_rows.append({"trade": trade, "matched": False})
            continue
        context = match_decision_context(entry, events)
        price_now = event_btc_price(context)
        if not math.isfinite(price_now):
            point = price_at_or_before(times, points, entry["_ts"])
            price_now = point.price if point is not None else math.nan
        mm = micro_momentum_score(
            side=str(trade.get("side")),
            ts=entry["_ts"],
            price_now=price_now,
            sigma_t_dollars=event_sigma(context),
            horizon_seconds=event_seconds_to_close(context),
            times=times,
            points=points,
        )
        edge = event_edge(context)
        min_edge = event_min_edge(context)
        trade_rows.append(
            {
                "matched": True,
                "market": trade.get("market"),
                "side": trade.get("side"),
                "entry_ts": trade.get("entry_ts"),
                "net_pnl_dollars": trade["_net_pnl"],
                "entry_event_ts_utc": entry["_ts"].isoformat(),
                "context_event_type": context.get("event_type"),
                "context_event_ts_utc": context["_ts"].isoformat(),
                "entry_edge_cents": round(edge, 6),
                "min_edge_cents": round(min_edge, 6),
                "btc_price": round(price_now, 2),
                "sigma_t_dollars": round(event_sigma(context), 6),
                "d_sigma": round(event_d_sigma(context), 6),
                "micro_momentum_score": mm["score"],
                "micro_momentum_details": mm["details"],
            }
        )

    base_net = round(sum(fnum(t.get("net_pnl_dollars"), 0.0) for t in trade_rows if t.get("matched")), 4)
    base_count = sum(1 for t in trade_rows if t.get("matched"))

    cap_summaries = []
    for cap in CAPS_CENTS:
        kept = []
        skipped = []
        for row in trade_rows:
            if not row.get("matched"):
                continue
            adjusted_edge = float(row["entry_edge_cents"]) + cap * float(row["micro_momentum_score"])
            row_result = {
                "market": row["market"],
                "side": row["side"],
                "entry_ts": row["entry_ts"],
                "net_pnl_dollars": row["net_pnl_dollars"],
                "entry_edge_cents": row["entry_edge_cents"],
                "momentum_score": row["micro_momentum_score"],
                "adjusted_edge_cents": round(adjusted_edge, 6),
                "min_edge_cents": row["min_edge_cents"],
            }
            if adjusted_edge >= float(row["min_edge_cents"]):
                kept.append(row_result)
            else:
                skipped.append(row_result)
        net = round(sum(float(r["net_pnl_dollars"]) for r in kept), 4)
        cap_summaries.append(
            {
                "cap_cents": cap,
                "kept_trades": len(kept),
                "skipped_trades": len(skipped),
                "net_pnl_dollars": net,
                "delta_vs_base_dollars": round(net - base_net, 4),
                "skipped_net_pnl_dollars": round(sum(float(r["net_pnl_dollars"]) for r in skipped), 4),
                "skipped": skipped,
            }
        )

    filter_summaries = []
    for threshold in MOMENTUM_FILTER_THRESHOLDS:
        kept = [r for r in trade_rows if r.get("matched") and float(r["micro_momentum_score"]) >= threshold]
        skipped = [r for r in trade_rows if r.get("matched") and float(r["micro_momentum_score"]) < threshold]
        net = round(sum(float(r["net_pnl_dollars"]) for r in kept), 4)
        filter_summaries.append(
            {
                "kind": "hard_momentum_floor",
                "threshold": threshold,
                "kept_trades": len(kept),
                "skipped_trades": len(skipped),
                "net_pnl_dollars": net,
                "delta_vs_base_dollars": round(net - base_net, 4),
                "skipped_net_pnl_dollars": round(sum(float(r["net_pnl_dollars"]) for r in skipped), 4),
            }
        )
    for margin in LOW_EDGE_MARGINS_CENTS:
        for threshold in (-0.75, -0.5, -0.25):
            skipped = [
                r
                for r in trade_rows
                if r.get("matched")
                and (float(r["entry_edge_cents"]) - float(r["min_edge_cents"])) <= margin
                and float(r["micro_momentum_score"]) < threshold
            ]
            kept = [r for r in trade_rows if r.get("matched") and r not in skipped]
            net = round(sum(float(r["net_pnl_dollars"]) for r in kept), 4)
            filter_summaries.append(
                {
                    "kind": "low_edge_adverse_momentum_filter",
                    "edge_margin_cents": margin,
                    "threshold": threshold,
                    "kept_trades": len(kept),
                    "skipped_trades": len(skipped),
                    "net_pnl_dollars": net,
                    "delta_vs_base_dollars": round(net - base_net, 4),
                    "skipped_net_pnl_dollars": round(sum(float(r["net_pnl_dollars"]) for r in skipped), 4),
                    "skipped": [
                        {
                            "market": r["market"],
                            "side": r["side"],
                            "entry_ts": r["entry_ts"],
                            "net_pnl_dollars": r["net_pnl_dollars"],
                            "entry_edge_cents": r["entry_edge_cents"],
                            "momentum_score": r["micro_momentum_score"],
                        }
                        for r in skipped
                    ],
                }
            )

    potential_adds = []
    for row in events:
        if row.get("event_type") not in {"mushroom_v28_rejected"}:
            continue
        if not exact_gate_like(row):
            continue
        edge = fnum(row.get("mushroom_v28_edge_cents"))
        min_edge = fnum(row.get("mushroom_v28_min_edge_cents"), 3.0)
        if edge >= min_edge:
            continue
        price_now = fnum(row.get("mushroom_v28_btc_price"))
        mm = micro_momentum_score(
            side=str(row.get("side") or row.get("mushroom_v28_side")),
            ts=row["_ts"],
            price_now=price_now,
            sigma_t_dollars=fnum(row.get("mushroom_v28_sigma_t_dollars")),
            horizon_seconds=fnum(row.get("mushroom_v28_seconds_to_close"), 900.0),
            times=times,
            points=points,
        )
        best_cap = max(CAPS_CENTS)
        adjusted = edge + best_cap * float(mm["score"])
        if adjusted >= min_edge:
            side = str(row.get("side") or row.get("mushroom_v28_side")).lower()
            result = market_results.get(str(row.get("market")), "")
            qty = int(fnum(row.get("mushroom_v28_target_count"), 2))
            ask = fnum(row.get("mushroom_v28_ask_cents"))
            fee = fnum(row.get("mushroom_v28_fee_cents"), 0.0)
            settlement_net = None
            if result in {"yes", "no"} and side in {"yes", "no"} and math.isfinite(ask):
                payout = 100.0 if result == side else 0.0
                settlement_net = round(((payout - ask - fee) * qty) / 100.0, 4)
            potential_adds.append(
                {
                    "ts_utc": row["_ts"].isoformat(),
                    "market": row.get("market"),
                    "side": side,
                    "ask_cents": ask,
                    "edge_cents": round(edge, 6),
                    "min_edge_cents": min_edge,
                    "momentum_score": mm["score"],
                    "adjusted_edge_at_cap3_cents": round(adjusted, 6),
                    "result": result,
                    "rough_settlement_net_dollars": settlement_net,
                    "reject_reason": row.get("mushroom_v28_reject_reason") or row.get("decision_reason"),
                }
            )

    payload = {
        "strategy_tag": STRATEGY_TAG,
        "log_source_tag": LIVE_TAG,
        "method": "Micro-momentum is a capped edge nudge. Positive means BTC moved toward the candidate side over 15/30/60s; negative means against it. Replay keeps actual realized PnL for filled trades that would still pass adjusted_edge >= min_edge.",
        "base_matched_trades": base_count,
        "base_net_pnl_dollars": base_net,
        "windows_seconds": WINDOWS_SECONDS,
        "cap_summaries": cap_summaries,
        "filter_summaries": filter_summaries,
        "trade_rows": trade_rows,
        "potential_adds_note": "Potential adds are rough settlement-only diagnostics for rejected rows that would cross edge after a 3c cap; they are not full-policy PnL because no live fills/exits existed.",
        "potential_adds_count": len(potential_adds),
        "potential_adds_rough_settlement_net_dollars": round(sum(fnum(r.get("rough_settlement_net_dollars"), 0.0) for r in potential_adds), 4),
        "potential_adds": potential_adds[:50],
    }
    OUT_JSON.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")

    lines = [
        "# v28 Micro Momentum Replay",
        "",
        f"- strategy_tag: `{STRATEGY_TAG}`",
        f"- log_source_tag: `{LIVE_TAG}`",
        f"- base matched trades: {base_count}",
        f"- base net after fees: ${base_net:.4f}",
        f"- windows: {', '.join(str(w) + 's' for w in WINDOWS_SECONDS)}",
        "",
        "## Filled-trade replay",
        "",
        "| cap | kept | skipped | net after fees | delta | skipped pnl |",
        "|---:|---:|---:|---:|---:|---:|",
    ]
    for s in cap_summaries:
        lines.append(
            f"| {s['cap_cents']:.1f}c | {s['kept_trades']} | {s['skipped_trades']} | "
            f"${s['net_pnl_dollars']:.4f} | ${s['delta_vs_base_dollars']:.4f} | ${s['skipped_net_pnl_dollars']:.4f} |"
        )
    lines += [
        "",
        "## Skipped Trades At 3c Cap",
        "",
    ]
    cap3 = next(s for s in cap_summaries if s["cap_cents"] == 3.0)
    if cap3["skipped"]:
        lines += ["| entry | market | side | pnl | edge | momentum | adjusted edge |", "|---|---|---:|---:|---:|---:|---:|"]
        for r in cap3["skipped"]:
            lines.append(
                f"| {r['entry_ts']} | `{r['market']}` | {r['side']} | ${float(r['net_pnl_dollars']):.4f} | "
                f"{float(r['entry_edge_cents']):.3f}c | {float(r['momentum_score']):.3f} | {float(r['adjusted_edge_cents']):.3f}c |"
            )
    else:
        lines.append("- none")
    lines += [
        "",
        "## Nearby Filter Diagnostics",
        "",
        "| filter | setting | kept | skipped | net after fees | delta |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    best_filters = sorted(filter_summaries, key=lambda s: float(s["net_pnl_dollars"]), reverse=True)[:8]
    for s in best_filters:
        if s["kind"] == "hard_momentum_floor":
            setting = f"score >= {s['threshold']}"
            label = "hard floor"
        else:
            setting = f"margin <= {s['edge_margin_cents']}c, score < {s['threshold']}"
            label = "low-edge adverse"
        lines.append(
            f"| {label} | {setting} | {s['kept_trades']} | {s['skipped_trades']} | "
            f"${s['net_pnl_dollars']:.4f} | ${s['delta_vs_base_dollars']:.4f} |"
        )
    lines += [
        "",
        "## Potential Adds",
        "",
        f"- rough add count at 3c cap: {len(potential_adds)}",
        f"- rough settlement-only net: ${payload['potential_adds_rough_settlement_net_dollars']:.4f}",
        "- note: this is not full-policy PnL; it ignores real fill probability and exit behavior.",
        "",
    ]
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")
    print(json.dumps(payload, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
