from __future__ import annotations

import argparse
import csv
import json
import math
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

import numpy as np


ROOT = Path(__file__).resolve().parent
NY = ZoneInfo("America/New_York")

DEFAULT_TAG = "mushroom_v28_common_clock_phi_reward_memory_lifecycle_exit_toll_size2_live"
DEFAULT_LOG_TAG = f"live_{DEFAULT_TAG}"
DEFAULT_TRADES_CSV = ROOT / "stats" / f"{DEFAULT_TAG}_analysis_api" / "trades.csv"
DEFAULT_MARKET_RESULTS_CSV = ROOT / "stats" / f"{DEFAULT_TAG}_analysis_api" / "market_results.csv"
DEFAULT_EVENTS_NDJSON = ROOT / "logs" / DEFAULT_LOG_TAG / "execution_events.ndjson"
DEFAULT_REPORT_PATH = ROOT / "docs" / "research" / "OU_EXIT_MESH_PROBE_LATEST.md"
DEFAULT_JSON_PATH = ROOT / "logs" / "particle_research" / "reports" / "ou_exit_mesh_probe_latest.json"
DEFAULT_GRID_CSV = ROOT / "logs" / "particle_research" / "reports" / "ou_exit_mesh_grid_latest.csv"


@dataclass(frozen=True)
class Trade:
    trade_id: int
    market: str
    side: str
    qty: float
    entry_dt: datetime
    entry_price_cents: float
    entry_fee_cents: float
    actual_net_pnl_dollars: float | None
    result: str
    settlement_dt: datetime | None


@dataclass(frozen=True)
class Observation:
    ts: datetime
    yes_bid: float
    no_bid: float
    yes_ask: float
    no_ask: float
    btc_price: float | None = None
    strike: float | None = None


@dataclass(frozen=True)
class PreparedTrade:
    trade: Trade
    path: tuple[tuple[datetime, float], ...]
    settlement_cents: float


def as_float(value: Any) -> float | None:
    if value in (None, ""):
        return None
    try:
        out = float(value)
    except (TypeError, ValueError):
        return None
    if not math.isfinite(out):
        return None
    return out


def bounded_cents(value: float | None) -> float | None:
    if value is None:
        return None
    if value < 0 or value > 100:
        return None
    return float(value)


def first_float(payload: dict[str, Any], names: tuple[str, ...]) -> float | None:
    for name in names:
        value = bounded_cents(as_float(payload.get(name)))
        if value is not None:
            return value
    return None


def parse_utc_ts(value: Any) -> datetime | None:
    if value in (None, ""):
        return None
    text = str(value).strip()
    if not text:
        return None
    text = text.replace("Z", "+00:00")
    try:
        dt = datetime.fromisoformat(text)
    except ValueError:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=NY)
    return dt.astimezone(timezone.utc)


def parse_local_trade_ts(value: Any) -> datetime | None:
    if value in (None, ""):
        return None
    text = str(value).strip()
    if not text:
        return None
    for fmt in ("%Y-%m-%d %H:%M:%S.%f", "%Y-%m-%d %H:%M:%S"):
        try:
            return datetime.strptime(text, fmt).replace(tzinfo=NY).astimezone(timezone.utc)
        except ValueError:
            pass
    return parse_utc_ts(text)


def estimated_order_fee_cents(price_cents: float, count: int) -> int:
    bounded_price = max(1, min(99, int(round(float(price_cents)))))
    numerator = 7 * int(count) * bounded_price * (100 - bounded_price)
    return max(1, (numerator + 9999) // 10000)


def load_market_results(path: Path) -> dict[str, dict[str, Any]]:
    out: dict[str, dict[str, Any]] = {}
    if not path.exists():
        return out
    with path.open("r", encoding="utf-8", newline="") as fh:
        reader = csv.DictReader(fh)
        for row in reader:
            market = str(row.get("market") or "").strip()
            if not market:
                continue
            out[market] = {
                "result": str(row.get("result") or "").strip().lower(),
                "settlement_dt": parse_utc_ts(row.get("settlement_ts")) or parse_utc_ts(row.get("close_time")),
            }
    return out


def load_trades(path: Path, market_results: dict[str, dict[str, Any]]) -> list[Trade]:
    trades: list[Trade] = []
    with path.open("r", encoding="utf-8", newline="") as fh:
        reader = csv.DictReader(fh)
        for idx, row in enumerate(reader):
            market = str(row.get("market") or "").strip()
            side = str(row.get("side") or "").strip().lower()
            entry_dt = parse_local_trade_ts(row.get("entry_ts"))
            entry_price = as_float(row.get("entry_fill_cents_used")) or as_float(row.get("entry_fill_cents_actual"))
            qty = as_float(row.get("qty"))
            if not market or side not in {"yes", "no"} or entry_dt is None or entry_price is None or qty is None or qty <= 0:
                continue
            result = str(row.get("market_result") or "").strip().lower()
            settlement_dt = parse_utc_ts(row.get("settlement_ts"))
            if not result:
                result = str(market_results.get(market, {}).get("result") or "").strip().lower()
            if settlement_dt is None:
                settlement_dt = market_results.get(market, {}).get("settlement_dt")
            trades.append(
                Trade(
                    trade_id=idx,
                    market=market,
                    side=side,
                    qty=float(qty),
                    entry_dt=entry_dt,
                    entry_price_cents=float(entry_price),
                    entry_fee_cents=float(as_float(row.get("entry_fee_cents")) or 0.0),
                    actual_net_pnl_dollars=as_float(row.get("net_pnl_dollars")),
                    result=result,
                    settlement_dt=settlement_dt,
                )
            )
    trades.sort(key=lambda trade: (trade.entry_dt, trade.trade_id))
    return trades


def extract_asks(payload: dict[str, Any]) -> tuple[float | None, float | None]:
    yes_ask = first_float(payload, ("derived_yes_ask", "yes_ask_cents", "mushroom_yes_ask_cents"))
    no_ask = first_float(payload, ("derived_no_ask", "no_ask_cents", "mushroom_no_ask_cents"))

    side = str(payload.get("mushroom_v28_side") or payload.get("mushroom_side") or payload.get("side") or "").lower()
    side_ask = first_float(
        payload,
        (
            "mushroom_v28_ask_cents",
            "mushroom_ask_cents",
            "cap_price_cents",
            "top_of_book_limit_cents",
        ),
    )
    if side == "yes" and side_ask is not None:
        yes_ask = side_ask
    elif side == "no" and side_ask is not None:
        no_ask = side_ask
    return yes_ask, no_ask


def load_observations(path: Path, markets: set[str]) -> dict[str, list[Observation]]:
    states: dict[str, dict[str, float | None]] = {}
    out: dict[str, list[Observation]] = {market: [] for market in markets}
    bad_json = 0
    with path.open("r", encoding="utf-8", errors="replace") as fh:
        for line in fh:
            if not line.strip():
                continue
            try:
                payload = json.loads(line)
            except json.JSONDecodeError:
                bad_json += 1
                continue
            market = str(payload.get("market") or "").strip()
            if market not in markets:
                continue
            ts = parse_utc_ts(payload.get("ts_wall"))
            if ts is None:
                continue
            state = states.setdefault(market, {"yes_ask": None, "no_ask": None})
            yes_ask, no_ask = extract_asks(payload)
            if yes_ask is not None:
                state["yes_ask"] = yes_ask
            if no_ask is not None:
                state["no_ask"] = no_ask
            if state["yes_ask"] is None or state["no_ask"] is None:
                continue
            yes_bid = max(0.0, min(99.0, 100.0 - float(state["no_ask"])))
            no_bid = max(0.0, min(99.0, 100.0 - float(state["yes_ask"])))
            obs = Observation(
                ts=ts,
                yes_bid=yes_bid,
                no_bid=no_bid,
                yes_ask=float(state["yes_ask"]),
                no_ask=float(state["no_ask"]),
                btc_price=as_float(payload.get("mushroom_v28_btc_price")) or as_float(payload.get("mushroom_btc_price")),
                strike=as_float(payload.get("mushroom_v28_strike")) or as_float(payload.get("mushroom_strike")) or as_float(payload.get("strike")),
            )
            previous = out[market][-1] if out[market] else None
            if previous and previous.ts == obs.ts and previous.yes_bid == obs.yes_bid and previous.no_bid == obs.no_bid:
                continue
            out[market].append(obs)
    for rows in out.values():
        rows.sort(key=lambda obs: obs.ts)
    if bad_json:
        print(f"Skipped {bad_json} malformed event lines")
    return out


def trade_path(
    trade: Trade,
    observations: dict[str, list[Observation]],
    *,
    min_hold_seconds: float,
    exit_slippage_cents: float,
) -> list[tuple[datetime, float]]:
    start = trade.entry_dt.timestamp() + float(min_hold_seconds)
    end = trade.settlement_dt.timestamp() if trade.settlement_dt is not None else float("inf")
    rows: list[tuple[datetime, float]] = []
    for obs in observations.get(trade.market, []):
        ts_seconds = obs.ts.timestamp()
        if ts_seconds < start or ts_seconds > end:
            continue
        raw_bid = obs.yes_bid if trade.side == "yes" else obs.no_bid
        bid = max(0.0, min(99.0, float(raw_bid) - float(exit_slippage_cents)))
        rows.append((obs.ts, bid))
    return rows


def settle_value_cents(trade: Trade) -> float | None:
    if trade.result not in {"yes", "no"}:
        return None
    return 100.0 if trade.result == trade.side else 0.0


def score_rule(
    prepared: list[PreparedTrade],
    *,
    pt_cents: int,
    sl_cents: int,
) -> dict[str, Any]:
    pnls: list[float] = []
    actuals: list[float] = []
    exits = 0
    settlements = 0
    hold_seconds: list[float] = []
    for prepared_trade in prepared:
        trade = prepared_trade.trade
        if trade.actual_net_pnl_dollars is not None:
            actuals.append(float(trade.actual_net_pnl_dollars))
        exit_price: float | None = None
        exit_ts: datetime | None = None
        for ts, bid in prepared_trade.path:
            if bid >= trade.entry_price_cents + pt_cents or bid <= trade.entry_price_cents - sl_cents:
                exit_price = bid
                exit_ts = ts
                break
        qty_int = max(1, int(math.ceil(trade.qty)))
        if exit_price is None:
            settle = prepared_trade.settlement_cents
            gross = trade.qty * (settle - trade.entry_price_cents) / 100.0
            net = gross - (trade.entry_fee_cents / 100.0)
            settlements += 1
            if trade.settlement_dt is not None:
                hold_seconds.append(max(0.0, trade.settlement_dt.timestamp() - trade.entry_dt.timestamp()))
        else:
            exit_fee = estimated_order_fee_cents(exit_price, qty_int)
            gross = trade.qty * (exit_price - trade.entry_price_cents) / 100.0
            net = gross - ((trade.entry_fee_cents + exit_fee) / 100.0)
            exits += 1
            if exit_ts is not None:
                hold_seconds.append(max(0.0, exit_ts.timestamp() - trade.entry_dt.timestamp()))
        pnls.append(float(net))
    arr = np.array(pnls, dtype=float)
    actual_arr = np.array(actuals, dtype=float)
    mean = float(arr.mean()) if len(arr) else 0.0
    std = float(arr.std(ddof=1)) if len(arr) > 1 else 0.0
    sharpe = mean / std if std > 1e-12 else (float("inf") if mean > 0 else 0.0)
    return {
        "pt_cents": int(pt_cents),
        "sl_cents": int(sl_cents),
        "trades": int(len(arr)),
        "skipped": 0,
        "total_net_pnl_dollars": round(float(arr.sum()), 4) if len(arr) else 0.0,
        "actual_net_pnl_dollars": round(float(actual_arr.sum()), 4) if len(actual_arr) else None,
        "delta_vs_actual_dollars": round(float(arr.sum() - actual_arr.sum()), 4) if len(arr) and len(actual_arr) else None,
        "mean_net_pnl_dollars": round(mean, 6),
        "std_net_pnl_dollars": round(std, 6),
        "sharpe_like": round(float(sharpe), 6) if math.isfinite(sharpe) else 999.0,
        "wins": int((arr > 0).sum()) if len(arr) else 0,
        "losses": int((arr < 0).sum()) if len(arr) else 0,
        "win_rate": round(float((arr > 0).mean()), 4) if len(arr) else None,
        "exit_count": int(exits),
        "settlement_count": int(settlements),
        "exit_rate": round(exits / len(arr), 4) if len(arr) else None,
        "avg_hold_seconds": round(float(np.mean(hold_seconds)), 2) if hold_seconds else None,
    }


def grid_scores(
    prepared: list[PreparedTrade],
    *,
    pt_values: list[int],
    sl_values: list[int],
) -> list[dict[str, Any]]:
    rows = [
        score_rule(
            prepared,
            pt_cents=pt,
            sl_cents=sl,
        )
        for pt in pt_values
        for sl in sl_values
    ]
    rows.sort(
        key=lambda row: (
            float(row["total_net_pnl_dollars"]),
            float(row["sharpe_like"]),
            int(row["trades"]),
        ),
        reverse=True,
    )
    return rows


def fit_ar1_from_paths(
    prepared: list[PreparedTrade],
) -> dict[str, Any]:
    x_values: list[float] = []
    y_values: list[float] = []
    initials: list[float] = []
    for prepared_trade in prepared:
        trade = prepared_trade.trade
        pnl_path = [bid - trade.entry_price_cents for _, bid in prepared_trade.path]
        if pnl_path:
            initials.append(float(pnl_path[0]))
        if len(pnl_path) < 2:
            continue
        x_values.extend(float(value) for value in pnl_path[:-1])
        y_values.extend(float(value) for value in pnl_path[1:])
    if len(x_values) < 10:
        return {"ok": False, "reason": "too_few_path_pairs", "pairs": len(x_values)}
    x = np.array(x_values, dtype=float)
    y = np.array(y_values, dtype=float)
    design = np.column_stack([np.ones_like(x), x])
    intercept, phi = np.linalg.lstsq(design, y, rcond=None)[0]
    resid = y - (intercept + phi * x)
    sigma = float(resid.std(ddof=2)) if len(resid) > 2 else 0.0
    mu = float(intercept / (1.0 - phi)) if abs(1.0 - phi) > 1e-8 else float(x.mean())
    if 0.0 < phi < 1.0:
        half_life_steps = float(-math.log(2.0) / math.log(phi))
    else:
        half_life_steps = None
    return {
        "ok": True,
        "pairs": int(len(x_values)),
        "initial_count": int(len(initials)),
        "phi": round(float(phi), 8),
        "intercept": round(float(intercept), 8),
        "mu_cents": round(mu, 6),
        "sigma_cents": round(sigma, 6),
        "half_life_steps": round(half_life_steps, 4) if half_life_steps is not None else None,
        "initial_mean_cents": round(float(np.mean(initials)), 6) if initials else None,
        "initial_median_cents": round(float(np.median(initials)), 6) if initials else None,
        "initials": initials,
    }


def simulate_ou_select_rule(
    fit: dict[str, Any],
    *,
    pt_values: list[int],
    sl_values: list[int],
    avg_round_trip_fee_cents_per_contract: float,
    max_steps: int,
    n_paths: int,
    seed: int,
) -> dict[str, Any]:
    if not fit.get("ok"):
        return {"ok": False, "reason": fit.get("reason", "fit_failed")}
    phi = float(fit["phi"])
    sigma = float(fit["sigma_cents"])
    mu = float(fit["mu_cents"])
    initials = [float(value) for value in fit.get("initials") or []]
    if not initials:
        initials = [0.0]
    rng = np.random.default_rng(int(seed))
    x = rng.choice(np.array(initials, dtype=float), size=int(n_paths), replace=True)
    shocks = rng.standard_normal(size=(int(max_steps), int(n_paths)))
    paths = np.empty((int(max_steps) + 1, int(n_paths)), dtype=float)
    paths[0] = x
    for step in range(1, int(max_steps) + 1):
        paths[step] = mu + phi * (paths[step - 1] - mu) + sigma * shocks[step - 1]
    candidates: list[dict[str, Any]] = []
    for pt in pt_values:
        for sl in sl_values:
            hit_pt = paths >= float(pt)
            hit_sl = paths <= -float(sl)
            pnl = paths[-1].copy()
            exit_steps = np.full(int(n_paths), int(max_steps) + 1, dtype=int)
            for step in range(1, int(max_steps) + 1):
                unresolved = exit_steps == int(max_steps) + 1
                if not unresolved.any():
                    break
                pt_now = unresolved & hit_pt[step]
                sl_now = unresolved & hit_sl[step]
                both = pt_now & sl_now
                if both.any():
                    sl_now = sl_now | both
                    pt_now = pt_now & ~both
                if pt_now.any():
                    pnl[pt_now] = float(pt)
                    exit_steps[pt_now] = step
                if sl_now.any():
                    pnl[sl_now] = -float(sl)
                    exit_steps[sl_now] = step
            pnl = (pnl - float(avg_round_trip_fee_cents_per_contract)) / 100.0
            mean = float(pnl.mean())
            std = float(pnl.std(ddof=1))
            sharpe = mean / std if std > 1e-12 else (999.0 if mean > 0 else 0.0)
            candidates.append(
                {
                    "pt_cents": int(pt),
                    "sl_cents": int(sl),
                    "sim_mean_dollars": round(mean, 6),
                    "sim_std_dollars": round(std, 6),
                    "sim_sharpe_like": round(float(sharpe), 6),
                    "sim_exit_rate": round(float((exit_steps <= int(max_steps)).mean()), 4),
                }
            )
    candidates.sort(
        key=lambda row: (
            float(row["sim_sharpe_like"]),
            float(row["sim_mean_dollars"]),
        ),
        reverse=True,
    )
    return {"ok": True, "best": candidates[0], "top": candidates[:10]}


def walk_forward_ou(
    prepared: list[PreparedTrade],
    *,
    pt_values: list[int],
    sl_values: list[int],
    sim_pt_values: list[int],
    sim_sl_values: list[int],
    train_size: int,
    test_size: int,
    max_steps: int,
    n_paths: int,
    seed: int,
) -> dict[str, Any]:
    parts: list[dict[str, Any]] = []
    idx = int(train_size)
    while idx < len(prepared):
        train = prepared[:idx]
        test = prepared[idx : min(len(prepared), idx + int(test_size))]
        if not test:
            break
        fit = fit_ar1_from_paths(train)
        avg_fee = average_round_trip_fee_cents_per_contract([row.trade for row in train])
        selected = simulate_ou_select_rule(
            fit,
            pt_values=sim_pt_values,
            sl_values=sim_sl_values,
            avg_round_trip_fee_cents_per_contract=avg_fee,
            max_steps=max_steps,
            n_paths=n_paths,
            seed=seed + idx,
        )
        if selected.get("ok"):
            best = selected["best"]
            test_score = score_rule(
                test,
                pt_cents=int(best["pt_cents"]),
                sl_cents=int(best["sl_cents"]),
            )
            parts.append(
                {
                    "train_rows": len(train),
                    "test_rows": len(test),
                    "test_start": test[0].trade.entry_dt.isoformat(),
                    "test_end": test[-1].trade.entry_dt.isoformat(),
                    "phi": fit.get("phi"),
                    "half_life_steps": fit.get("half_life_steps"),
                    "selected_pt_cents": int(best["pt_cents"]),
                    "selected_sl_cents": int(best["sl_cents"]),
                    "sim_sharpe_like": best["sim_sharpe_like"],
                    "test_total_net_pnl_dollars": test_score["total_net_pnl_dollars"],
                    "test_actual_net_pnl_dollars": test_score["actual_net_pnl_dollars"],
                    "test_delta_vs_actual_dollars": test_score["delta_vs_actual_dollars"],
                    "test_win_rate": test_score["win_rate"],
                    "test_exit_rate": test_score["exit_rate"],
                }
            )
        idx += int(test_size)
    total_model = sum(float(part["test_total_net_pnl_dollars"]) for part in parts)
    total_actual = sum(float(part["test_actual_net_pnl_dollars"] or 0.0) for part in parts)
    return {
        "parts": parts,
        "aggregate_test_net_pnl_dollars": round(total_model, 4),
        "aggregate_actual_net_pnl_dollars": round(total_actual, 4),
        "aggregate_delta_vs_actual_dollars": round(total_model - total_actual, 4),
    }


def walk_forward_grid_select(
    prepared: list[PreparedTrade],
    *,
    pt_values: list[int],
    sl_values: list[int],
    train_size: int,
    test_size: int,
) -> dict[str, Any]:
    parts: list[dict[str, Any]] = []
    idx = int(train_size)
    while idx < len(prepared):
        train = prepared[:idx]
        test = prepared[idx : min(len(prepared), idx + int(test_size))]
        if not test:
            break
        train_grid = grid_scores(train, pt_values=pt_values, sl_values=sl_values)
        if not train_grid:
            break
        selected = train_grid[0]
        test_score = score_rule(
            test,
            pt_cents=int(selected["pt_cents"]),
            sl_cents=int(selected["sl_cents"]),
        )
        parts.append(
            {
                "train_rows": len(train),
                "test_rows": len(test),
                "test_start": test[0].trade.entry_dt.isoformat(),
                "test_end": test[-1].trade.entry_dt.isoformat(),
                "selected_pt_cents": int(selected["pt_cents"]),
                "selected_sl_cents": int(selected["sl_cents"]),
                "train_total_net_pnl_dollars": selected["total_net_pnl_dollars"],
                "train_delta_vs_actual_dollars": selected["delta_vs_actual_dollars"],
                "test_total_net_pnl_dollars": test_score["total_net_pnl_dollars"],
                "test_actual_net_pnl_dollars": test_score["actual_net_pnl_dollars"],
                "test_delta_vs_actual_dollars": test_score["delta_vs_actual_dollars"],
                "test_win_rate": test_score["win_rate"],
                "test_exit_rate": test_score["exit_rate"],
            }
        )
        idx += int(test_size)
    total_model = sum(float(part["test_total_net_pnl_dollars"]) for part in parts)
    total_actual = sum(float(part["test_actual_net_pnl_dollars"] or 0.0) for part in parts)
    return {
        "parts": parts,
        "aggregate_test_net_pnl_dollars": round(total_model, 4),
        "aggregate_actual_net_pnl_dollars": round(total_actual, 4),
        "aggregate_delta_vs_actual_dollars": round(total_model - total_actual, 4),
    }


def average_round_trip_fee_cents_per_contract(trades: list[Trade]) -> float:
    values: list[float] = []
    for trade in trades:
        qty_int = max(1, int(math.ceil(trade.qty)))
        entry_fee_per_contract = trade.entry_fee_cents / max(1.0, trade.qty)
        exit_fee_per_contract = estimated_order_fee_cents(trade.entry_price_cents, qty_int) / max(1.0, trade.qty)
        values.append(entry_fee_per_contract + exit_fee_per_contract)
    return float(np.mean(values)) if values else 0.0


def fit_btc_gap_ar1(observations: dict[str, list[Observation]]) -> dict[str, Any]:
    x_values: list[float] = []
    y_values: list[float] = []
    for rows in observations.values():
        series = [obs.btc_price - obs.strike for obs in rows if obs.btc_price is not None and obs.strike is not None]
        if len(series) < 2:
            continue
        x_values.extend(series[:-1])
        y_values.extend(series[1:])
    if len(x_values) < 10:
        return {"ok": False, "reason": "too_few_pairs", "pairs": len(x_values)}
    x = np.array(x_values, dtype=float)
    y = np.array(y_values, dtype=float)
    design = np.column_stack([np.ones_like(x), x])
    intercept, phi = np.linalg.lstsq(design, y, rcond=None)[0]
    resid = y - (intercept + phi * x)
    if 0.0 < phi < 1.0:
        half_life = float(-math.log(2.0) / math.log(phi))
    else:
        half_life = None
    return {
        "ok": True,
        "pairs": int(len(x_values)),
        "phi": round(float(phi), 8),
        "intercept": round(float(intercept), 8),
        "sigma_dollars": round(float(resid.std(ddof=2)), 6) if len(resid) > 2 else 0.0,
        "half_life_steps": round(half_life, 4) if half_life is not None else None,
    }


def resolved_with_paths(trades: list[Trade], observations: dict[str, list[Observation]], min_hold_seconds: float, exit_slippage_cents: float) -> list[Trade]:
    out: list[Trade] = []
    for trade in trades:
        if settle_value_cents(trade) is None:
            continue
        if trade_path(trade, observations, min_hold_seconds=min_hold_seconds, exit_slippage_cents=exit_slippage_cents):
            out.append(trade)
    return out


def prepare_trades(
    trades: list[Trade],
    observations: dict[str, list[Observation]],
    *,
    min_hold_seconds: float,
    exit_slippage_cents: float,
) -> list[PreparedTrade]:
    prepared: list[PreparedTrade] = []
    for trade in trades:
        settle = settle_value_cents(trade)
        if settle is None:
            continue
        path = trade_path(
            trade,
            observations,
            min_hold_seconds=min_hold_seconds,
            exit_slippage_cents=exit_slippage_cents,
        )
        if not path:
            continue
        prepared.append(PreparedTrade(trade=trade, path=tuple(path), settlement_cents=float(settle)))
    prepared.sort(key=lambda row: (row.trade.entry_dt, row.trade.trade_id))
    return prepared


def write_grid_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fields = list(rows[0].keys()) if rows else []
    with path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def render_report(payload: dict[str, Any]) -> str:
    best = payload["in_sample_grid_top"][0] if payload["in_sample_grid_top"] else {}
    ou = payload["full_sample_ou"]
    selected = payload["full_sample_simulated_selection"]
    walk = payload["walk_forward_ou"]
    grid_walk = payload["walk_forward_grid_select"]
    btc = payload["btc_gap_ar1"]
    verdict = payload["verdict"]
    lines = [
        "# OU exit mesh probe",
        "",
        f"Generated: {payload['generated_at']}",
        "",
        "## Verdict",
        "",
        verdict,
        "",
        "## Inputs",
        "",
        f"- Trades: `{payload['inputs']['trades_csv']}`",
        f"- Market results: `{payload['inputs']['market_results_csv']}`",
        f"- Execution events: `{payload['inputs']['events_ndjson']}`",
        f"- Trade rows usable after resolved/path filters: {payload['counts']['usable_trades']} of {payload['counts']['raw_trades']}",
        f"- Exit model: same-side sell bid reconstructed as `100 - opposite ask`, with {payload['settings']['exit_slippage_cents']}c slippage and {payload['settings']['min_hold_seconds']}s minimum hold.",
        "",
        "## Baseline",
        "",
        f"- Actual API-reconciled net PnL on usable trades: {payload['baseline']['actual_net_pnl_dollars']:.4f} dollars",
        f"- Actual wins/losses by row sign: {payload['baseline']['actual_wins']} / {payload['baseline']['actual_losses']}",
        "",
        "## OU Diagnostics",
        "",
        f"- BTC strike-gap AR(1): phi={btc.get('phi')}, half_life_steps={btc.get('half_life_steps')}, pairs={btc.get('pairs')}",
        f"- Held-position MtM PnL AR(1): phi={ou.get('phi')}, half_life_steps={ou.get('half_life_steps')}, mu_cents={ou.get('mu_cents')}, sigma_cents={ou.get('sigma_cents')}, pairs={ou.get('pairs')}",
        "",
        "## Best Retrospective Real-Path Grid",
        "",
        f"- Best full-sample rule by real observed paths: PT=+{best.get('pt_cents')}c, SL=-{best.get('sl_cents')}c",
        f"- Counterfactual net PnL: {best.get('total_net_pnl_dollars')} dollars; delta vs actual: {best.get('delta_vs_actual_dollars')} dollars; win rate: {best.get('win_rate')}; exit rate: {best.get('exit_rate')}",
        "",
        "## Carr-Inspired Simulated Selection",
        "",
    ]
    if selected.get("ok"):
        sel = selected["best"]
        lines.extend(
            [
                f"- Full-sample simulation-selected rule: PT=+{sel['pt_cents']}c, SL=-{sel['sl_cents']}c, simulated Sharpe-like={sel['sim_sharpe_like']}",
            ]
        )
    else:
        lines.append(f"- Simulation selection failed: {selected.get('reason')}")
    lines.extend(
        [
            f"- Walk-forward aggregate net PnL: {walk['aggregate_test_net_pnl_dollars']:.4f} dollars",
            f"- Same slices actual net PnL: {walk['aggregate_actual_net_pnl_dollars']:.4f} dollars",
            f"- Walk-forward delta vs actual: {walk['aggregate_delta_vs_actual_dollars']:.4f} dollars",
            f"- Historical-grid walk-forward net PnL: {grid_walk['aggregate_test_net_pnl_dollars']:.4f} dollars; delta vs actual: {grid_walk['aggregate_delta_vs_actual_dollars']:.4f} dollars",
            "",
            "## Walk-Forward Parts",
            "",
            "| Test start | Rows | Selected PT | Selected SL | Test net | Actual net | Delta |",
            "|---|---:|---:|---:|---:|---:|---:|",
        ]
    )
    for part in walk["parts"]:
        lines.append(
            f"| {part['test_start']} | {part['test_rows']} | {part['selected_pt_cents']} | {part['selected_sl_cents']} | {part['test_total_net_pnl_dollars']} | {part['test_actual_net_pnl_dollars']} | {part['test_delta_vs_actual_dollars']} |"
        )
    lines.extend(
        [
            "",
            "## Top Retrospective Nodes",
            "",
            "| PT | SL | Net | Delta vs actual | Win rate | Exit rate | Avg hold sec |",
            "|---:|---:|---:|---:|---:|---:|---:|",
        ]
    )
    for row in payload["in_sample_grid_top"][:10]:
        lines.append(
            f"| {row['pt_cents']} | {row['sl_cents']} | {row['total_net_pnl_dollars']} | {row['delta_vs_actual_dollars']} | {row['win_rate']} | {row['exit_rate']} | {row['avg_hold_seconds']} |"
        )
    lines.append("")
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="Research-only Carr-inspired OU exit mesh probe for v28 Kalshi BTC logs.")
    parser.add_argument("--trades-csv", default=str(DEFAULT_TRADES_CSV))
    parser.add_argument("--market-results-csv", default=str(DEFAULT_MARKET_RESULTS_CSV))
    parser.add_argument("--events-ndjson", default=str(DEFAULT_EVENTS_NDJSON))
    parser.add_argument("--report-path", default=str(DEFAULT_REPORT_PATH))
    parser.add_argument("--json-path", default=str(DEFAULT_JSON_PATH))
    parser.add_argument("--grid-csv", default=str(DEFAULT_GRID_CSV))
    parser.add_argument("--min-hold-seconds", type=float, default=30.0)
    parser.add_argument("--exit-slippage-cents", type=float, default=1.0)
    parser.add_argument("--pt-min", type=int, default=1)
    parser.add_argument("--pt-max", type=int, default=40)
    parser.add_argument("--sl-min", type=int, default=1)
    parser.add_argument("--sl-max", type=int, default=80)
    parser.add_argument("--sim-pt-step", type=int, default=2)
    parser.add_argument("--sim-sl-step", type=int, default=4)
    parser.add_argument("--train-size", type=int, default=30)
    parser.add_argument("--test-size", type=int, default=15)
    parser.add_argument("--sim-paths", type=int, default=8000)
    parser.add_argument("--sim-steps", type=int, default=50)
    parser.add_argument("--seed", type=int, default=14081159)
    args = parser.parse_args()

    trades_csv = Path(args.trades_csv)
    market_results_csv = Path(args.market_results_csv)
    events_ndjson = Path(args.events_ndjson)
    market_results = load_market_results(market_results_csv)
    raw_trades = load_trades(trades_csv, market_results)
    observations = load_observations(events_ndjson, {trade.market for trade in raw_trades})
    prepared = prepare_trades(
        raw_trades,
        observations,
        min_hold_seconds=float(args.min_hold_seconds),
        exit_slippage_cents=float(args.exit_slippage_cents),
    )
    trades = [row.trade for row in prepared]

    pt_values = list(range(int(args.pt_min), int(args.pt_max) + 1))
    sl_values = list(range(int(args.sl_min), int(args.sl_max) + 1))
    sim_pt_values = list(range(int(args.pt_min), int(args.pt_max) + 1, max(1, int(args.sim_pt_step))))
    sim_sl_values = list(range(int(args.sl_min), int(args.sl_max) + 1, max(1, int(args.sim_sl_step))))
    grid = grid_scores(
        prepared,
        pt_values=pt_values,
        sl_values=sl_values,
    )
    full_fit = fit_ar1_from_paths(prepared)
    full_selection = simulate_ou_select_rule(
        full_fit,
        pt_values=sim_pt_values,
        sl_values=sim_sl_values,
        avg_round_trip_fee_cents_per_contract=average_round_trip_fee_cents_per_contract(trades),
        max_steps=int(args.sim_steps),
        n_paths=int(args.sim_paths),
        seed=int(args.seed),
    )
    walk = walk_forward_ou(
        prepared,
        pt_values=pt_values,
        sl_values=sl_values,
        sim_pt_values=sim_pt_values,
        sim_sl_values=sim_sl_values,
        train_size=int(args.train_size),
        test_size=int(args.test_size),
        max_steps=int(args.sim_steps),
        n_paths=int(args.sim_paths),
        seed=int(args.seed),
    )
    grid_walk = walk_forward_grid_select(
        prepared,
        pt_values=pt_values,
        sl_values=sl_values,
        train_size=int(args.train_size),
        test_size=int(args.test_size),
    )
    btc_gap = fit_btc_gap_ar1(observations)

    actuals = np.array([trade.actual_net_pnl_dollars for trade in trades if trade.actual_net_pnl_dollars is not None], dtype=float)
    best = grid[0] if grid else {}
    if walk["aggregate_test_net_pnl_dollars"] > 0 and walk["aggregate_delta_vs_actual_dollars"] > 0:
        verdict = (
            "The OU mesh is worth promoting to a stricter shadow experiment: the walk-forward simulation-selected exits "
            "were profitable and improved on actual exits after the fee/slippage controls used here."
        )
    elif best and float(best.get("total_net_pnl_dollars", 0.0)) > 0:
        verdict = (
            "There is a real exit-shape worth studying, but not yet a profitable Carr-inspired strategy. "
            "A retrospective grid can find positive nodes on this small sample, while the simulation-selected "
            "walk-forward result does not clear the profitability gate."
        )
    else:
        verdict = (
            "No profitable strategy is supported yet. Under the current fee/slippage/path reconstruction, neither "
            "the retrospective real-path mesh nor the Carr-inspired OU walk-forward selection clears a positive-PnL gate."
        )

    payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "inputs": {
            "trades_csv": str(trades_csv),
            "market_results_csv": str(market_results_csv),
            "events_ndjson": str(events_ndjson),
        },
        "settings": {
            "min_hold_seconds": float(args.min_hold_seconds),
            "exit_slippage_cents": float(args.exit_slippage_cents),
            "pt_min": int(args.pt_min),
            "pt_max": int(args.pt_max),
            "sl_min": int(args.sl_min),
            "sl_max": int(args.sl_max),
            "sim_pt_step": int(args.sim_pt_step),
            "sim_sl_step": int(args.sim_sl_step),
            "train_size": int(args.train_size),
            "test_size": int(args.test_size),
            "sim_paths": int(args.sim_paths),
            "sim_steps": int(args.sim_steps),
        },
        "counts": {
            "raw_trades": len(raw_trades),
            "usable_trades": len(trades),
            "markets": len({trade.market for trade in raw_trades}),
            "markets_with_observations": sum(1 for rows in observations.values() if rows),
            "observations": sum(len(rows) for rows in observations.values()),
        },
        "baseline": {
            "actual_net_pnl_dollars": round(float(actuals.sum()), 4) if len(actuals) else 0.0,
            "actual_wins": int((actuals > 0).sum()) if len(actuals) else 0,
            "actual_losses": int((actuals < 0).sum()) if len(actuals) else 0,
        },
        "btc_gap_ar1": btc_gap,
        "full_sample_ou": {key: value for key, value in full_fit.items() if key != "initials"},
        "full_sample_simulated_selection": full_selection,
        "walk_forward_ou": walk,
        "walk_forward_grid_select": grid_walk,
        "in_sample_grid_top": grid[:25],
        "verdict": verdict,
    }

    json_path = Path(args.json_path)
    report_path = Path(args.report_path)
    grid_csv = Path(args.grid_csv)
    json_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    report_path.write_text(render_report(payload), encoding="utf-8")
    write_grid_csv(grid_csv, grid)

    print(json.dumps({
        "report": str(report_path),
        "json": str(json_path),
        "grid_csv": str(grid_csv),
        "verdict": verdict,
        "counts": payload["counts"],
        "baseline": payload["baseline"],
        "btc_gap_ar1": btc_gap,
        "full_sample_ou": payload["full_sample_ou"],
        "best_grid": grid[0] if grid else None,
        "walk_forward_ou": walk,
        "walk_forward_grid_select": grid_walk,
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
