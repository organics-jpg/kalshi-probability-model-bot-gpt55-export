from __future__ import annotations

import argparse
import csv
import json
import math
import os
import time
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Iterable

import numpy as np


ROOT = Path(__file__).resolve().parent
REPORT_DIR = ROOT / "logs" / "particle_research" / "reports"
DOCS_DIR = ROOT / "docs" / "research"
SHADOW_DIR = ROOT / "logs" / "particle_research" / "ou_mispricing_forward_shadow"

DEFAULT_LOG_TAG = "live_mushroom_v28_common_clock_phi_reward_memory_lifecycle_exit_toll_size2_live"
DEFAULT_EVENTS = ROOT / "logs" / DEFAULT_LOG_TAG / "execution_events.ndjson"
DEFAULT_MARKET_RESULTS = (
    ROOT
    / "stats"
    / "mushroom_v28_common_clock_phi_reward_memory_lifecycle_exit_toll_size2_live_analysis_api"
    / "market_results.csv"
)


@dataclass(frozen=True)
class MarketResult:
    result: str
    close_ts: datetime | None = None
    settlement_ts: datetime | None = None


@dataclass
class Snapshot:
    ts: datetime
    market: str
    strike: float
    btc_price: float
    close_ts: datetime
    seconds_to_close: float
    yes_ask: float
    yes_bid: float
    no_ask: float
    no_bid: float
    fair_yes: float = float("nan")
    sigma_t: float = float("nan")
    z: float = float("nan")

    @property
    def mid_yes(self) -> float:
        return (self.yes_ask + self.yes_bid) / 2.0

    @property
    def spread_yes(self) -> float:
        return max(0.0, self.yes_ask - self.yes_bid)

    @property
    def spread_no(self) -> float:
        return max(0.0, self.no_ask - self.no_bid)

    def side_ask(self, side: str) -> float:
        return self.yes_ask if side == "yes" else self.no_ask

    def side_bid(self, side: str) -> float:
        return self.yes_bid if side == "yes" else self.no_bid

    def side_mid(self, side: str) -> float:
        return self.mid_yes if side == "yes" else (100.0 - self.mid_yes)

    def side_spread(self, side: str) -> float:
        return self.spread_yes if side == "yes" else self.spread_no

    def fair_side(self, side: str) -> float:
        return self.fair_yes if side == "yes" else (100.0 - self.fair_yes)


@dataclass(frozen=True)
class OUFitted:
    ok: bool
    n: int
    phi: float = float("nan")
    intercept: float = float("nan")
    mu: float = float("nan")
    sigma: float = float("nan")
    half_life_steps: float | None = None
    reason: str = ""


@dataclass(frozen=True)
class SimChoice:
    ok: bool
    pt_cents: float = 0.0
    sl_cents: float = 0.0
    max_hold_seconds: float = 0.0
    expected_net_cents: float = 0.0
    std_net_cents: float = 0.0
    sharpe_like: float = 0.0
    loss_prob: float = 1.0
    reason: str = ""


@dataclass
class Position:
    entry_ts: datetime
    entry_market: str
    side: str
    entry_price: float
    entry_fee_cents: float
    pt_cents: float
    sl_cents: float
    max_hold_seconds: float
    sim_expected_net_cents: float
    sim_sharpe_like: float
    entry_fair_side: float
    entry_z: float
    entry_seconds_to_close: float


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def parse_ts(value: Any) -> datetime | None:
    if value in (None, ""):
        return None
    text = str(value).strip()
    if not text:
        return None
    text = text.replace("Z", "+00:00")
    try:
        out = datetime.fromisoformat(text)
    except ValueError:
        return None
    if out.tzinfo is None:
        out = out.replace(tzinfo=timezone.utc)
    return out.astimezone(timezone.utc)


def as_float(value: Any) -> float | None:
    if value in (None, ""):
        return None
    try:
        out = float(value)
    except (TypeError, ValueError):
        return None
    return out if math.isfinite(out) else None


def bounded_cents(value: float | None) -> float | None:
    if value is None:
        return None
    if 0.0 <= value <= 100.0:
        return float(value)
    return None


def normal_cdf(x: float) -> float:
    return 0.5 * (1.0 + math.erf(x / math.sqrt(2.0)))


def estimated_order_fee_cents(price_cents: float, count: int = 1) -> int:
    bounded_price = max(1, min(99, int(round(float(price_cents)))))
    numerator = 7 * int(count) * bounded_price * (100 - bounded_price)
    return max(1, (numerator + 9999) // 10000)


def read_json_lines(path: Path, *, start_offset: int = 0) -> Iterable[tuple[int, dict[str, Any]]]:
    with path.open("r", encoding="utf-8", errors="replace") as fh:
        if start_offset:
            fh.seek(start_offset)
        while True:
            pos = fh.tell()
            line = fh.readline()
            if not line:
                break
            if not line.strip():
                continue
            try:
                yield fh.tell(), json.loads(line)
            except json.JSONDecodeError:
                continue


def load_market_results(path: Path | None) -> dict[str, MarketResult]:
    if path is None or not path.exists():
        return {}
    out: dict[str, MarketResult] = {}
    with path.open("r", encoding="utf-8", newline="") as fh:
        reader = csv.DictReader(fh)
        for row in reader:
            market = str(row.get("market") or "").strip()
            if not market:
                continue
            result = str(row.get("result") or row.get("market_result") or "").strip().lower()
            out[market] = MarketResult(
                result=result,
                close_ts=parse_ts(row.get("close_time") or row.get("watch_close_time")),
                settlement_ts=parse_ts(row.get("settlement_ts")),
            )
    return out


def first_cents(payload: dict[str, Any], names: tuple[str, ...]) -> float | None:
    for name in names:
        value = bounded_cents(as_float(payload.get(name)))
        if value is not None:
            return value
    return None


def extract_payload(raw: dict[str, Any]) -> dict[str, Any]:
    nested = raw.get("payload_json")
    if isinstance(nested, dict):
        payload = dict(raw)
        payload.update(nested)
        return payload
    return raw


def update_book_state(state: dict[str, Any], payload: dict[str, Any]) -> None:
    yes_ask = first_cents(payload, ("derived_yes_ask", "yes_ask", "yes_ask_cents", "mushroom_yes_ask_cents"))
    no_ask = first_cents(payload, ("derived_no_ask", "no_ask", "no_ask_cents", "mushroom_no_ask_cents"))
    yes_bid = first_cents(payload, ("yes_bid", "yes_bid_cents", "mushroom_yes_bid_cents"))
    no_bid = first_cents(payload, ("no_bid", "no_bid_cents", "mushroom_no_bid_cents"))

    side = str(payload.get("mushroom_v28_side") or payload.get("mushroom_side") or payload.get("side") or "").lower()
    side_ask = first_cents(
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
    if side == "no" and side_ask is not None:
        no_ask = side_ask

    if yes_ask is not None:
        state["yes_ask"] = yes_ask
    if no_ask is not None:
        state["no_ask"] = no_ask
    if yes_bid is not None:
        state["yes_bid"] = yes_bid
    if no_bid is not None:
        state["no_bid"] = no_bid

    if state.get("yes_bid") is None and state.get("no_ask") is not None:
        state["yes_bid"] = max(0.0, min(99.0, 100.0 - float(state["no_ask"])))
    if state.get("no_bid") is None and state.get("yes_ask") is not None:
        state["no_bid"] = max(0.0, min(99.0, 100.0 - float(state["yes_ask"])))


def extract_snapshot(
    raw: dict[str, Any],
    states: dict[str, dict[str, Any]],
    market_results: dict[str, MarketResult],
) -> Snapshot | None:
    payload = extract_payload(raw)
    market = str(payload.get("market") or payload.get("market_ticker") or "").strip()
    if not market:
        return None
    ts = parse_ts(payload.get("ts_wall") or payload.get("local_recv_ts") or payload.get("time"))
    if ts is None:
        return None
    state = states.setdefault(market, {"yes_ask": None, "yes_bid": None, "no_ask": None, "no_bid": None})
    update_book_state(state, payload)

    strike = as_float(payload.get("mushroom_v28_strike")) or as_float(payload.get("mushroom_strike")) or as_float(payload.get("strike"))
    if strike is not None:
        state["strike"] = strike
    btc = (
        as_float(payload.get("mushroom_v28_btc_price"))
        or as_float(payload.get("mushroom_btc_price"))
        or as_float(payload.get("btc_price"))
        or as_float(payload.get("underlying_price"))
    )
    if btc is not None:
        state["btc_price"] = btc

    close_ts = parse_ts(payload.get("close_time") or payload.get("watch_close_time"))
    seconds_to_close = as_float(payload.get("mushroom_v28_seconds_to_close")) or as_float(payload.get("seconds_to_close"))
    if close_ts is not None:
        state["close_ts"] = close_ts
    elif seconds_to_close is not None:
        state["close_ts"] = ts + timedelta(seconds=max(0.0, seconds_to_close))
    elif market in market_results and market_results[market].close_ts is not None:
        state["close_ts"] = market_results[market].close_ts

    required = ("yes_ask", "yes_bid", "no_ask", "no_bid", "strike", "btc_price", "close_ts")
    if any(state.get(name) is None for name in required):
        return None
    close = state["close_ts"]
    sec = max(0.0, (close - ts).total_seconds())
    if sec <= 0:
        return None
    return Snapshot(
        ts=ts,
        market=market,
        strike=float(state["strike"]),
        btc_price=float(state["btc_price"]),
        close_ts=close,
        seconds_to_close=sec,
        yes_ask=float(state["yes_ask"]),
        yes_bid=float(state["yes_bid"]),
        no_ask=float(state["no_ask"]),
        no_bid=float(state["no_bid"]),
    )


def load_snapshots(
    event_paths: list[Path],
    market_results: dict[str, MarketResult],
    *,
    max_lines: int | None = None,
) -> list[Snapshot]:
    states: dict[str, dict[str, Any]] = {}
    rows: list[Snapshot] = []
    seen = 0
    for path in event_paths:
        for _, raw in read_json_lines(path):
            seen += 1
            snap = extract_snapshot(raw, states, market_results)
            if snap is not None:
                rows.append(snap)
            if max_lines and seen >= max_lines:
                break
        if max_lines and seen >= max_lines:
            break
    rows.sort(key=lambda row: (row.ts, row.market))
    return rows


def event_paths_from_args(paths: list[str], roots: list[str]) -> list[Path]:
    out = [Path(path) for path in paths]
    for root in roots:
        root_path = Path(root)
        if root_path.is_file():
            out.append(root_path)
        elif root_path.exists():
            out.extend(sorted(root_path.rglob("*.ndjson")))
    return [path for path in out if path.exists() and path.is_file()]


def add_fair_values(
    snapshots: list[Snapshot],
    *,
    vol_lookback_seconds: float,
    min_vol_points: int,
    fallback_sigma_per_sqrt_s: float,
) -> list[Snapshot]:
    spot_rows: list[tuple[float, float]] = []
    last_ts_price: tuple[float, float] | None = None
    for row in snapshots:
        ts_float = row.ts.timestamp()
        if last_ts_price is None or ts_float > last_ts_price[0]:
            spot_rows.append((ts_float, row.btc_price))
            last_ts_price = (ts_float, row.btc_price)
    sigmas: list[tuple[float, float]] = []
    left = 0
    for idx in range(1, len(spot_rows)):
        ts = spot_rows[idx][0]
        while left < idx and spot_rows[left][0] < ts - vol_lookback_seconds:
            left += 1
        values: list[float] = []
        for j in range(max(left + 1, 1), idx + 1):
            dt = spot_rows[j][0] - spot_rows[j - 1][0]
            if 0 < dt <= 30:
                values.append((spot_rows[j][1] - spot_rows[j - 1][1]) ** 2 / dt)
        if len(values) >= min_vol_points:
            sigma = math.sqrt(float(np.mean(values)))
        else:
            sigma = fallback_sigma_per_sqrt_s
        sigmas.append((ts, max(0.01, sigma)))

    sigma_idx = 0
    enriched: list[Snapshot] = []
    for row in snapshots:
        ts_float = row.ts.timestamp()
        while sigma_idx + 1 < len(sigmas) and sigmas[sigma_idx + 1][0] <= ts_float:
            sigma_idx += 1
        sigma_per_s = sigmas[sigma_idx][1] if sigmas else fallback_sigma_per_sqrt_s
        sigma_t = max(1.0, sigma_per_s * math.sqrt(max(1.0, row.seconds_to_close)))
        fair_yes = 100.0 * normal_cdf((row.btc_price - row.strike) / sigma_t)
        fair_yes = max(0.5, min(99.5, fair_yes))
        row.fair_yes = fair_yes
        row.sigma_t = sigma_t
        row.z = row.mid_yes - fair_yes
        if math.isfinite(row.z):
            enriched.append(row)
    return enriched


def downsample_snapshots(rows: list[Snapshot], *, sample_seconds: float) -> list[Snapshot]:
    if sample_seconds <= 0:
        return rows
    last_by_market: dict[str, float] = {}
    out: list[Snapshot] = []
    for row in rows:
        last = last_by_market.get(row.market)
        now = row.ts.timestamp()
        if last is None or now - last >= sample_seconds:
            out.append(row)
            last_by_market[row.market] = now
    return out


def fit_ou(values: list[float], *, min_points: int) -> OUFitted:
    clean = np.array([v for v in values if math.isfinite(v)], dtype=float)
    if len(clean) < min_points:
        return OUFitted(ok=False, n=len(clean), reason="too_few_points")
    x = clean[:-1]
    y = clean[1:]
    if len(x) < max(4, min_points - 1):
        return OUFitted(ok=False, n=len(clean), reason="too_few_pairs")
    design = np.column_stack([np.ones_like(x), x])
    intercept, phi = np.linalg.lstsq(design, y, rcond=None)[0]
    resid = y - (intercept + phi * x)
    sigma = float(resid.std(ddof=2)) if len(resid) > 2 else 0.0
    if sigma <= 1e-9:
        return OUFitted(ok=False, n=len(clean), reason="zero_sigma")
    mu = float(intercept / (1.0 - phi)) if abs(1.0 - phi) > 1e-8 else float(clean.mean())
    half_life = None
    if 0.0 < phi < 1.0:
        half_life = float(-math.log(2.0) / math.log(phi))
    return OUFitted(
        ok=True,
        n=len(clean),
        phi=float(phi),
        intercept=float(intercept),
        mu=mu,
        sigma=sigma,
        half_life_steps=half_life,
    )


def simulate_choice(
    *,
    z0: float,
    side: str,
    fit: OUFitted,
    entry_ask: float,
    entry_mid: float,
    exit_spread_cost: float,
    sample_seconds: float,
    pt_values: list[float],
    sl_values: list[float],
    hold_values: list[float],
    n_paths: int,
    rng: np.random.Generator,
) -> SimChoice:
    if not fit.ok:
        return SimChoice(ok=False, reason=fit.reason)
    if not (-0.25 <= fit.phi <= 1.02):
        return SimChoice(ok=False, reason="unstable_phi")
    max_steps = max(1, int(math.ceil(max(hold_values) / max(1.0, sample_seconds))))
    shocks = rng.standard_normal(size=(max_steps, int(n_paths)))
    paths = np.empty((max_steps + 1, int(n_paths)), dtype=float)
    paths[0] = float(z0)
    phi = max(-0.25, min(1.02, fit.phi))
    for step in range(1, max_steps + 1):
        paths[step] = fit.mu + phi * (paths[step - 1] - fit.mu) + fit.sigma * shocks[step - 1]

    direction = 1.0 if side == "yes" else -1.0
    entry_cost = max(0.0, entry_ask - entry_mid)
    fee_cents = estimated_order_fee_cents(entry_ask, 1) + estimated_order_fee_cents(entry_ask, 1)
    fixed_cost = entry_cost + max(0.0, exit_spread_cost) + fee_cents

    best: SimChoice | None = None
    for hold_seconds in hold_values:
        steps = max(1, min(max_steps, int(math.ceil(hold_seconds / max(1.0, sample_seconds)))))
        deltas = direction * (paths[: steps + 1] - float(z0))
        for pt in pt_values:
            hit_pt = deltas >= float(pt)
            for sl in sl_values:
                hit_sl = deltas <= -float(sl)
                pnl = deltas[steps].copy()
                done = np.zeros(int(n_paths), dtype=bool)
                for step in range(1, steps + 1):
                    active = ~done
                    if not active.any():
                        break
                    sl_now = active & hit_sl[step]
                    pt_now = active & hit_pt[step] & ~sl_now
                    if pt_now.any():
                        pnl[pt_now] = float(pt)
                        done[pt_now] = True
                    if sl_now.any():
                        pnl[sl_now] = -float(sl)
                        done[sl_now] = True
                net = pnl - fixed_cost
                mean = float(net.mean())
                std = float(net.std(ddof=1))
                sharpe = mean / std if std > 1e-9 else (999.0 if mean > 0 else 0.0)
                loss_prob = float((net < 0).mean())
                choice = SimChoice(
                    ok=True,
                    pt_cents=float(pt),
                    sl_cents=float(sl),
                    max_hold_seconds=float(hold_seconds),
                    expected_net_cents=mean,
                    std_net_cents=std,
                    sharpe_like=sharpe,
                    loss_prob=loss_prob,
                )
                if best is None or (
                    choice.expected_net_cents,
                    choice.sharpe_like,
                    -choice.loss_prob,
                ) > (
                    best.expected_net_cents,
                    best.sharpe_like,
                    -best.loss_prob,
                ):
                    best = choice
    return best or SimChoice(ok=False, reason="no_candidates")


def result_settlement_cents(result: MarketResult | None, side: str) -> float | None:
    if result is None or result.result not in {"yes", "no"}:
        return None
    return 100.0 if result.result == side else 0.0


def close_position(
    pos: Position,
    row: Snapshot,
    *,
    exit_price: float,
    exit_reason: str,
    settlement: bool,
) -> dict[str, Any]:
    exit_fee = 0 if settlement else estimated_order_fee_cents(exit_price, 1)
    net_cents = exit_price - pos.entry_price - pos.entry_fee_cents - exit_fee
    return {
        "entry_ts": pos.entry_ts.isoformat(),
        "exit_ts": row.ts.isoformat(),
        "market": pos.entry_market,
        "side": pos.side,
        "entry_price_cents": round(pos.entry_price, 4),
        "exit_price_cents": round(exit_price, 4),
        "entry_fee_cents": round(pos.entry_fee_cents, 4),
        "exit_fee_cents": round(float(exit_fee), 4),
        "net_pnl_cents": round(net_cents, 4),
        "net_pnl_dollars": round(net_cents / 100.0, 4),
        "exit_reason": exit_reason,
        "settlement_exit": bool(settlement),
        "hold_seconds": round(max(0.0, (row.ts - pos.entry_ts).total_seconds()), 3),
        "pt_cents": pos.pt_cents,
        "sl_cents": pos.sl_cents,
        "max_hold_seconds": pos.max_hold_seconds,
        "sim_expected_net_cents": round(pos.sim_expected_net_cents, 4),
        "sim_sharpe_like": round(pos.sim_sharpe_like, 6),
        "entry_fair_side_cents": round(pos.entry_fair_side, 4),
        "entry_z_cents": round(pos.entry_z, 4),
        "entry_seconds_to_close": round(pos.entry_seconds_to_close, 3),
    }


def run_backtest(
    snapshots: list[Snapshot],
    market_results: dict[str, MarketResult],
    *,
    z_lookback: int,
    min_ou_points: int,
    entry_z_min: float,
    min_raw_edge_cents: float,
    min_sim_ev_cents: float,
    max_loss_prob: float,
    max_spread_cents: float,
    min_seconds_to_close: float,
    max_seconds_to_close: float,
    sample_seconds: float,
    pt_values: list[float],
    sl_values: list[float],
    hold_values: list[float],
    sim_paths: int,
    one_entry_per_market: bool,
    seed: int,
) -> dict[str, Any]:
    rng = np.random.default_rng(int(seed))
    z_history: list[float] = []
    open_pos: dict[str, Position] = {}
    traded_markets: set[str] = set()
    trades: list[dict[str, Any]] = []
    rejects = defaultdict(int)
    decisions = 0

    for row in snapshots:
        pos = open_pos.get(row.market)
        if pos is not None:
            side_bid = row.side_bid(pos.side)
            pnl_cents = side_bid - pos.entry_price
            age = max(0.0, (row.ts - pos.entry_ts).total_seconds())
            close_reason = ""
            exit_price = side_bid
            settlement = False
            if pnl_cents >= pos.pt_cents:
                close_reason = "take_profit"
            elif pnl_cents <= -pos.sl_cents:
                close_reason = "stop_loss"
            elif age >= pos.max_hold_seconds:
                close_reason = "max_hold"
            elif row.seconds_to_close <= 1:
                settle = result_settlement_cents(market_results.get(row.market), pos.side)
                if settle is not None:
                    close_reason = "settlement"
                    exit_price = settle
                    settlement = True
            if close_reason:
                trades.append(close_position(pos, row, exit_price=exit_price, exit_reason=close_reason, settlement=settlement))
                open_pos.pop(row.market, None)

        z_history.append(row.z)
        if len(z_history) < min_ou_points:
            rejects["warming"] += 1
            continue
        if len(z_history) > max(z_lookback * 2, z_lookback + 10):
            z_history = z_history[-z_lookback:]
        if one_entry_per_market and row.market in traded_markets:
            rejects["one_entry_per_market"] += 1
            continue
        if row.market in open_pos:
            rejects["already_open"] += 1
            continue
        if not (min_seconds_to_close <= row.seconds_to_close <= max_seconds_to_close):
            rejects["time_window"] += 1
            continue

        yes_edge = row.fair_yes - row.yes_ask - estimated_order_fee_cents(row.yes_ask, 1)
        no_edge = (100.0 - row.fair_yes) - row.no_ask - estimated_order_fee_cents(row.no_ask, 1)
        side = "yes" if yes_edge >= no_edge else "no"
        raw_edge = yes_edge if side == "yes" else no_edge
        aligned_z = row.z <= -entry_z_min if side == "yes" else row.z >= entry_z_min
        if raw_edge < min_raw_edge_cents or not aligned_z:
            rejects["edge_or_z"] += 1
            continue
        if row.side_spread(side) > max_spread_cents:
            rejects["spread"] += 1
            continue

        fit = fit_ou(z_history[-z_lookback:], min_points=min_ou_points)
        if not fit.ok:
            rejects[f"ou_{fit.reason}"] += 1
            continue
        choice = simulate_choice(
            z0=row.z,
            side=side,
            fit=fit,
            entry_ask=row.side_ask(side),
            entry_mid=row.side_mid(side),
            exit_spread_cost=row.side_spread(side) / 2.0,
            sample_seconds=sample_seconds,
            pt_values=pt_values,
            sl_values=sl_values,
            hold_values=hold_values,
            n_paths=sim_paths,
            rng=rng,
        )
        decisions += 1
        if not choice.ok:
            rejects[f"sim_{choice.reason}"] += 1
            continue
        if choice.expected_net_cents < min_sim_ev_cents or choice.loss_prob > max_loss_prob:
            rejects["sim_gate"] += 1
            continue

        open_pos[row.market] = Position(
            entry_ts=row.ts,
            entry_market=row.market,
            side=side,
            entry_price=row.side_ask(side),
            entry_fee_cents=float(estimated_order_fee_cents(row.side_ask(side), 1)),
            pt_cents=choice.pt_cents,
            sl_cents=choice.sl_cents,
            max_hold_seconds=choice.max_hold_seconds,
            sim_expected_net_cents=choice.expected_net_cents,
            sim_sharpe_like=choice.sharpe_like,
            entry_fair_side=row.fair_side(side),
            entry_z=row.z,
            entry_seconds_to_close=row.seconds_to_close,
        )
        traded_markets.add(row.market)

    for market, pos in list(open_pos.items()):
        market_rows = [row for row in snapshots if row.market == market]
        if not market_rows:
            continue
        last = market_rows[-1]
        settle = result_settlement_cents(market_results.get(market), pos.side)
        if settle is not None:
            trades.append(close_position(pos, last, exit_price=settle, exit_reason="settlement_after_tape", settlement=True))
        else:
            trades.append(close_position(pos, last, exit_price=last.side_bid(pos.side), exit_reason="last_bid_after_tape", settlement=False))

    pnls = np.array([float(row["net_pnl_dollars"]) for row in trades], dtype=float)
    realized_trades = [row for row in trades if row.get("exit_reason") != "last_bid_after_tape"]
    realized_pnls = np.array([float(row["net_pnl_dollars"]) for row in realized_trades], dtype=float)
    marked_open_trades = [row for row in trades if row.get("exit_reason") == "last_bid_after_tape"]
    marked_open_pnls = np.array([float(row["net_pnl_dollars"]) for row in marked_open_trades], dtype=float)
    by_reason = defaultdict(int)
    for trade in trades:
        by_reason[str(trade["exit_reason"])] += 1
    return {
        "summary": {
            "snapshot_count": len(snapshots),
            "markets": len({row.market for row in snapshots}),
            "trade_count": len(trades),
            "net_pnl_dollars": round(float(pnls.sum()), 4) if len(pnls) else 0.0,
            "realized_trade_count_ex_open_marks": len(realized_trades),
            "realized_net_pnl_dollars_ex_open_marks": round(float(realized_pnls.sum()), 4) if len(realized_pnls) else 0.0,
            "open_mark_trade_count": len(marked_open_trades),
            "open_mark_net_pnl_dollars": round(float(marked_open_pnls.sum()), 4) if len(marked_open_pnls) else 0.0,
            "mean_trade_pnl_dollars": round(float(pnls.mean()), 6) if len(pnls) else 0.0,
            "std_trade_pnl_dollars": round(float(pnls.std(ddof=1)), 6) if len(pnls) > 1 else 0.0,
            "win_rate": round(float((pnls > 0).mean()), 4) if len(pnls) else None,
            "wins": int((pnls > 0).sum()) if len(pnls) else 0,
            "losses": int((pnls < 0).sum()) if len(pnls) else 0,
            "sim_decisions_scored": int(decisions),
            "rejects": dict(sorted(rejects.items())),
            "exit_reasons": dict(sorted(by_reason.items())),
        },
        "trades": trades,
    }


def parse_float_list(text: str) -> list[float]:
    return [float(part.strip()) for part in str(text).split(",") if part.strip()]


def write_backtest_outputs(report: dict[str, Any], *, json_path: Path, md_path: Path, trades_csv_path: Path) -> None:
    json_path.parent.mkdir(parents=True, exist_ok=True)
    md_path.parent.mkdir(parents=True, exist_ok=True)
    trades_csv_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
    trades = report.get("trades") or []
    if trades:
        with trades_csv_path.open("w", encoding="utf-8", newline="") as fh:
            writer = csv.DictWriter(fh, fieldnames=list(trades[0].keys()))
            writer.writeheader()
            writer.writerows(trades)
    summary = report["summary"]
    lines = [
        "# OU Mispricing Optimal-Stopping Backtest",
        "",
        "Brand-new research lane: Brownian fair value from BTC spot/strike plus Carr-inspired OU simulation on Kalshi probability mispricing.",
        "",
        "Audit note: this is not a paper-exact Carr/Lopez de Prado implementation. The paper optimizes exit corridors for an already-open position; this harness adds a new fair-value entry rule, Kalshi fees/spreads, and historical-tape PnL scoring.",
        "",
        f"- Generated UTC: `{report['generated_utc']}`",
        f"- Event files: `{report['inputs']['event_file_count']}`",
        f"- Market-results source: `{report['inputs'].get('market_results_csv') or ''}`",
        f"- Snapshots after filters: `{summary['snapshot_count']}`",
        f"- Markets: `{summary['markets']}`",
        f"- Trades: `{summary['trade_count']}`",
        f"- Net PnL: `{summary['net_pnl_dollars']}` dollars",
        f"- Realized/settled PnL excluding open mark-to-last rows: `{summary['realized_net_pnl_dollars_ex_open_marks']}` dollars on `{summary['realized_trade_count_ex_open_marks']}` trades",
        f"- Open mark-to-last PnL: `{summary['open_mark_net_pnl_dollars']}` dollars on `{summary['open_mark_trade_count']}` trades",
        f"- Win rate: `{summary['win_rate']}`",
        f"- Sim decisions scored: `{summary['sim_decisions_scored']}`",
        "",
        "## Exit Reasons",
        "",
    ]
    for key, value in summary.get("exit_reasons", {}).items():
        lines.append(f"- `{key}`: {value}")
    lines.extend(["", "## Rejection Counts", ""])
    for key, value in summary.get("rejects", {}).items():
        lines.append(f"- `{key}`: {value}")
    lines.extend(["", "## First Trades", "", "| Entry | Market | Side | Entry | Exit | PnL $ | Reason |", "|---|---|---:|---:|---:|---:|---|"])
    for trade in trades[:25]:
        lines.append(
            f"| {trade['entry_ts']} | {trade['market']} | {trade['side']} | {trade['entry_price_cents']} | {trade['exit_price_cents']} | {trade['net_pnl_dollars']} | {trade['exit_reason']} |"
        )
    lines.append("")
    md_path.write_text("\n".join(lines), encoding="utf-8")


def run_backtest_mode(args: argparse.Namespace) -> dict[str, Any]:
    event_paths = event_paths_from_args(args.events, args.roots)
    if not event_paths:
        raise RuntimeError("No event paths found.")
    market_results = load_market_results(Path(args.market_results) if args.market_results else None)
    raw = load_snapshots(event_paths, market_results, max_lines=args.max_lines)
    enriched = add_fair_values(
        raw,
        vol_lookback_seconds=float(args.vol_lookback_seconds),
        min_vol_points=int(args.min_vol_points),
        fallback_sigma_per_sqrt_s=float(args.fallback_sigma_per_sqrt_s),
    )
    sampled = downsample_snapshots(enriched, sample_seconds=float(args.sample_seconds))
    report = run_backtest(
        sampled,
        market_results,
        z_lookback=int(args.z_lookback),
        min_ou_points=int(args.min_ou_points),
        entry_z_min=float(args.entry_z_min),
        min_raw_edge_cents=float(args.min_raw_edge_cents),
        min_sim_ev_cents=float(args.min_sim_ev_cents),
        max_loss_prob=float(args.max_loss_prob),
        max_spread_cents=float(args.max_spread_cents),
        min_seconds_to_close=float(args.min_seconds_to_close),
        max_seconds_to_close=float(args.max_seconds_to_close),
        sample_seconds=float(args.sample_seconds),
        pt_values=parse_float_list(args.pt_values),
        sl_values=parse_float_list(args.sl_values),
        hold_values=parse_float_list(args.hold_values),
        sim_paths=int(args.sim_paths),
        one_entry_per_market=not bool(args.allow_reentry),
        seed=int(args.seed),
    )
    payload = {
        "generated_utc": utc_now_iso(),
        "inputs": {
            "event_paths": [str(path) for path in event_paths],
            "event_file_count": len(event_paths),
            "market_results_csv": str(args.market_results) if args.market_results else "",
            "raw_snapshot_count": len(raw),
            "fair_snapshot_count": len(enriched),
        },
        "settings": vars(args),
        **report,
    }
    write_backtest_outputs(
        payload,
        json_path=Path(args.output_json),
        md_path=Path(args.output_md),
        trades_csv_path=Path(args.output_trades_csv),
    )
    return payload


def append_shadow_event(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(payload, sort_keys=True, default=str) + "\n")


def run_shadow_mode(args: argparse.Namespace) -> dict[str, Any]:
    events_path = Path(args.events[0] if args.events else DEFAULT_EVENTS)
    if not events_path.exists():
        raise RuntimeError(f"Shadow source does not exist: {events_path}")
    out_path = Path(args.shadow_log)
    status_path = Path(args.shadow_status)
    market_results: dict[str, MarketResult] = {}
    states: dict[str, dict[str, Any]] = {}
    z_history: list[float] = []
    open_pos: dict[str, Position] = {}
    initial_size = events_path.stat().st_size
    offset = max(0, initial_size - int(args.tail_bytes))
    rng = np.random.default_rng(int(args.seed))
    started = utc_now_iso()
    events_written = 0
    loops = 0
    warmup_snapshots = 0

    warmup_raw: list[Snapshot] = []
    for next_offset, raw in read_json_lines(events_path, start_offset=offset):
        offset = next_offset
        snap = extract_snapshot(raw, states, market_results)
        if snap is not None:
            warmup_raw.append(snap)
    warmup_enriched = add_fair_values(
        warmup_raw,
        vol_lookback_seconds=float(args.vol_lookback_seconds),
        min_vol_points=int(args.min_vol_points),
        fallback_sigma_per_sqrt_s=float(args.fallback_sigma_per_sqrt_s),
    )
    warmup_sampled = downsample_snapshots(warmup_enriched, sample_seconds=float(args.sample_seconds))
    z_history = [row.z for row in warmup_sampled[-int(args.z_lookback) :] if math.isfinite(row.z)]
    warmup_snapshots = len(warmup_sampled)
    offset = initial_size

    append_shadow_event(
        out_path,
        {
            "event_type": "shadow_start",
            "ts_wall": started,
            "source": str(events_path),
            "research_only": True,
            "places_orders": False,
            "strategy": "ou_mispricing_optimal_stopping",
            "warmup_snapshots": warmup_snapshots,
        },
    )
    while loops < int(args.iterations):
        loops += 1
        new_rows = 0
        raw_snaps: list[Snapshot] = []
        for next_offset, raw in read_json_lines(events_path, start_offset=offset):
            offset = next_offset
            snap = extract_snapshot(raw, states, market_results)
            if snap is not None:
                raw_snaps.append(snap)
                new_rows += 1
        enriched = add_fair_values(
            raw_snaps,
            vol_lookback_seconds=float(args.vol_lookback_seconds),
            min_vol_points=int(args.min_vol_points),
            fallback_sigma_per_sqrt_s=float(args.fallback_sigma_per_sqrt_s),
        )
        sampled = downsample_snapshots(enriched, sample_seconds=float(args.sample_seconds))
        for row in sampled:
            pos = open_pos.get(row.market)
            if pos is not None:
                side_bid = row.side_bid(pos.side)
                pnl = side_bid - pos.entry_price
                age = max(0.0, (row.ts - pos.entry_ts).total_seconds())
                reason = ""
                if pnl >= pos.pt_cents:
                    reason = "take_profit"
                elif pnl <= -pos.sl_cents:
                    reason = "stop_loss"
                elif age >= pos.max_hold_seconds:
                    reason = "max_hold"
                if reason:
                    event = {
                        "event_type": "shadow_exit",
                        "ts_wall": row.ts.isoformat(),
                        **close_position(pos, row, exit_price=side_bid, exit_reason=reason, settlement=False),
                    }
                    append_shadow_event(out_path, event)
                    open_pos.pop(row.market, None)
                    events_written += 1

            z_history.append(row.z)
            if len(z_history) > int(args.z_lookback) * 2:
                z_history = z_history[-int(args.z_lookback) :]
            if len(z_history) < int(args.min_ou_points) or row.market in open_pos:
                continue
            if not (float(args.min_seconds_to_close) <= row.seconds_to_close <= float(args.max_seconds_to_close)):
                continue
            yes_edge = row.fair_yes - row.yes_ask - estimated_order_fee_cents(row.yes_ask, 1)
            no_edge = (100.0 - row.fair_yes) - row.no_ask - estimated_order_fee_cents(row.no_ask, 1)
            side = "yes" if yes_edge >= no_edge else "no"
            raw_edge = yes_edge if side == "yes" else no_edge
            aligned_z = row.z <= -float(args.entry_z_min) if side == "yes" else row.z >= float(args.entry_z_min)
            if raw_edge < float(args.min_raw_edge_cents) or not aligned_z or row.side_spread(side) > float(args.max_spread_cents):
                continue
            fit = fit_ou(z_history[-int(args.z_lookback) :], min_points=int(args.min_ou_points))
            choice = simulate_choice(
                z0=row.z,
                side=side,
                fit=fit,
                entry_ask=row.side_ask(side),
                entry_mid=row.side_mid(side),
                exit_spread_cost=row.side_spread(side) / 2.0,
                sample_seconds=float(args.sample_seconds),
                pt_values=parse_float_list(args.pt_values),
                sl_values=parse_float_list(args.sl_values),
                hold_values=parse_float_list(args.hold_values),
                n_paths=int(args.sim_paths),
                rng=rng,
            )
            if not choice.ok or choice.expected_net_cents < float(args.min_sim_ev_cents) or choice.loss_prob > float(args.max_loss_prob):
                continue
            pos = Position(
                entry_ts=row.ts,
                entry_market=row.market,
                side=side,
                entry_price=row.side_ask(side),
                entry_fee_cents=float(estimated_order_fee_cents(row.side_ask(side), 1)),
                pt_cents=choice.pt_cents,
                sl_cents=choice.sl_cents,
                max_hold_seconds=choice.max_hold_seconds,
                sim_expected_net_cents=choice.expected_net_cents,
                sim_sharpe_like=choice.sharpe_like,
                entry_fair_side=row.fair_side(side),
                entry_z=row.z,
                entry_seconds_to_close=row.seconds_to_close,
            )
            open_pos[row.market] = pos
            append_shadow_event(
                out_path,
                {
                    "event_type": "shadow_entry",
                    "ts_wall": row.ts.isoformat(),
                    "market": row.market,
                    "side": side,
                    "entry_price_cents": round(pos.entry_price, 4),
                    "entry_fee_cents": round(pos.entry_fee_cents, 4),
                    "fair_side_cents": round(pos.entry_fair_side, 4),
                    "z_cents": round(row.z, 4),
                    "raw_edge_cents": round(raw_edge, 4),
                    "pt_cents": choice.pt_cents,
                    "sl_cents": choice.sl_cents,
                    "max_hold_seconds": choice.max_hold_seconds,
                    "sim_expected_net_cents": round(choice.expected_net_cents, 4),
                    "sim_sharpe_like": round(choice.sharpe_like, 6),
                    "loss_prob": round(choice.loss_prob, 4),
                    "research_only": True,
                    "places_orders": False,
                },
            )
            events_written += 1

        status = {
            "generated_utc": utc_now_iso(),
            "started_utc": started,
            "source": str(events_path),
            "offset": offset,
            "loop": loops,
            "new_snapshots_last_loop": new_rows,
            "open_positions": len(open_pos),
            "events_written": events_written,
            "warmup_snapshots": warmup_snapshots,
            "shadow_log": str(out_path),
            "research_only": True,
            "places_orders": False,
        }
        status_path.parent.mkdir(parents=True, exist_ok=True)
        status_path.write_text(json.dumps(status, indent=2, sort_keys=True), encoding="utf-8")
        if loops < int(args.iterations):
            time.sleep(float(args.poll_seconds))
    return status


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Research-only OU mispricing strategy backtest and forward shadow.")
    parser.add_argument("--mode", choices=("backtest", "shadow"), default="backtest")
    parser.add_argument("--events", action="append", default=[], help="Event NDJSON path. Can be passed multiple times.")
    parser.add_argument("--roots", action="append", default=[], help="Root directory to scan for NDJSON files.")
    parser.add_argument("--market-results", default=str(DEFAULT_MARKET_RESULTS))
    parser.add_argument("--output-json", default=str(REPORT_DIR / "ou_mispricing_backtest_latest.json"))
    parser.add_argument("--output-md", default=str(DOCS_DIR / "OU_MISPRICING_BACKTEST_LATEST.md"))
    parser.add_argument("--output-trades-csv", default=str(REPORT_DIR / "ou_mispricing_backtest_trades_latest.csv"))
    parser.add_argument("--sample-seconds", type=float, default=5.0)
    parser.add_argument("--vol-lookback-seconds", type=float, default=1800.0)
    parser.add_argument("--min-vol-points", type=int, default=20)
    parser.add_argument("--fallback-sigma-per-sqrt-s", type=float, default=5.0)
    parser.add_argument("--z-lookback", type=int, default=400)
    parser.add_argument("--min-ou-points", type=int, default=120)
    parser.add_argument("--entry-z-min", type=float, default=4.0)
    parser.add_argument("--min-raw-edge-cents", type=float, default=1.5)
    parser.add_argument("--min-sim-ev-cents", type=float, default=1.0)
    parser.add_argument("--max-loss-prob", type=float, default=0.58)
    parser.add_argument("--max-spread-cents", type=float, default=6.0)
    parser.add_argument("--min-seconds-to-close", type=float, default=45.0)
    parser.add_argument("--max-seconds-to-close", type=float, default=600.0)
    parser.add_argument("--pt-values", default="3,5,8,12,18,25")
    parser.add_argument("--sl-values", default="4,8,12,20,35,55")
    parser.add_argument("--hold-values", default="30,60,120,240,480")
    parser.add_argument("--sim-paths", type=int, default=2000)
    parser.add_argument("--seed", type=int, default=14081159)
    parser.add_argument("--allow-reentry", action="store_true")
    parser.add_argument("--max-lines", type=int, default=0)
    parser.add_argument("--shadow-log", default=str(SHADOW_DIR / "decisions.ndjson"))
    parser.add_argument("--shadow-status", default=str(SHADOW_DIR / "status.json"))
    parser.add_argument("--tail-bytes", type=int, default=40_000_000)
    parser.add_argument("--iterations", type=int, default=1)
    parser.add_argument("--poll-seconds", type=float, default=10.0)
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    if not args.events and args.mode == "backtest":
        args.events = [str(DEFAULT_EVENTS)]
    args.max_lines = int(args.max_lines or 0) or None
    if args.mode == "backtest":
        report = run_backtest_mode(args)
        print(json.dumps({"summary": report["summary"], "outputs": {
            "json": args.output_json,
            "markdown": args.output_md,
            "trades_csv": args.output_trades_csv,
        }}, indent=2, sort_keys=True))
    else:
        status = run_shadow_mode(args)
        print(json.dumps(status, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
