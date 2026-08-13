#!/usr/bin/env python3
"""KXBTC15M single-cycle price-priority volatility-harvest research.

Mechanism-distinct family: take at most one 100-contract position in a market,
prove the passive entry from a later execution strictly through our limit, then
rest a reduce-only take-profit order and prove that exit from a later execution
strictly through the exit limit.  Completed cycles have settlement-independent
PnL.  If the exit never certifies, the live rule holds the one position to
settlement; future exit success is never used to decide whether to enter.

The search uses only the first chronological half of the Vela Apr-Jun corpus.
One rule is frozen from train, evaluated once on the next quarter, and the final
quarter is opened only if train+validation independently clear every declared
gate.  Missing trade-tape markets are zeros in the full-calendar denominator.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from dataclasses import asdict, dataclass
from pathlib import Path

import numpy as np
import pandas as pd

QTY = 100.0
TARGET = 100_000.0
SEED = 20260813


@dataclass(frozen=True)
class Rule:
    tau: int
    side_rule: str
    offset: float
    take_profit: float
    latency: float
    entry_min_tte: int
    entry_cap: float


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def fee(qty: float, p: float) -> float:
    if qty <= 0 or not math.isfinite(p):
        return 0.0
    # Deliberately reserve the full 7% taker coefficient on passive certified fills.
    raw = 0.07 * qty * p * (1.0 - p)
    return math.ceil(raw * 100.0 - 1e-12) / 100.0


def load(root: Path):
    mp = root / "backtest/data/markets.parquet"
    tp = root / "backtest/data/trades.parquet"
    m = pd.read_parquet(mp).copy()
    t = pd.read_parquet(tp).copy()
    m["close_dt"] = pd.to_datetime(m["close_dt"], utc=True)
    if "yes" not in m.columns:
        if "margin" in m.columns:
            m["yes"] = (pd.to_numeric(m["margin"], errors="coerce") >= 0).astype(int)
        else:
            m["yes"] = m["result"].astype(str).str.lower().eq("yes").astype(int)
    m["day"] = m.close_dt.dt.floor("D")
    t["created_time"] = pd.to_datetime(t["created_time"], utc=True, errors="coerce")
    for c in ("sec_to_close", "yes_price", "no_price", "size"):
        t[c] = pd.to_numeric(t[c], errors="coerce")
    t["taker_side"] = t["taker_side"].astype(str).str.lower().str.strip()
    t = t[
        t.created_time.notna()
        & t.ticker.isin(set(m.ticker))
        & t.yes_price.between(0.001, 0.999)
        & t.no_price.between(0.001, 0.999)
        & (t["size"] > 0)
        & t.taker_side.isin(["yes", "no"])
    ].copy()
    t = t.sort_values(["ticker", "created_time"]).drop_duplicates(
        ["ticker", "created_time", "yes_price", "size", "taker_side"], keep="last"
    )
    manifest = {
        "markets": {"path": str(mp), "bytes": mp.stat().st_size, "sha256": sha256(mp)},
        "trades": {"path": str(tp), "bytes": tp.stat().st_size, "sha256": sha256(tp)},
    }
    return m.sort_values("close_dt").reset_index(drop=True), t.reset_index(drop=True), manifest


def partition(m: pd.DataFrame):
    days = pd.date_range(m.day.min(), m.day.max(), freq="D", tz="UTC")
    n = len(days)
    a = n // 2
    b = a + n // 4
    return days, set(days[:a]), set(days[a:b]), set(days[b:])


def trade_arrays(t: pd.DataFrame) -> dict[str, dict[str, np.ndarray]]:
    out = {}
    for ticker, g in t.groupby("ticker", sort=False):
        g = g.sort_values("created_time")
        out[str(ticker)] = {
            "ns": g.created_time.astype("int64").to_numpy(np.int64),
            "tte": g.sec_to_close.to_numpy(float),
            "yp": g.yes_price.to_numpy(float),
            "np": g.no_price.to_numpy(float),
            "side": g.taker_side.to_numpy(str),
        }
    return out


def prior_price(a: dict[str, np.ndarray], tau: int, seconds_back: float = 0.0):
    # sec_to_close decreases with time.  Choose the latest execution causally
    # available at tau (+ seconds_back for an older comparison point).
    target = tau + seconds_back
    idx = np.flatnonzero(a["tte"] >= target - 1e-12)
    if not len(idx):
        return None
    i = int(idx[-1])
    return i, float(a["yp"][i]), float(a["np"][i]), int(a["ns"][i])


def choose_side(a: dict[str, np.ndarray], tau: int, side_rule: str):
    now = prior_price(a, tau)
    if now is None:
        return None
    i, yp, np_, decision_ns = now
    if side_rule == "favorite":
        side = "yes" if yp >= np_ else "no"
    elif side_rule == "cheaper":
        side = "yes" if yp < np_ else "no"
    elif side_rule in {"contrarian5", "contrarian15"}:
        lag = 5 if side_rule.endswith("5") else 15
        old = prior_price(a, tau, lag)
        if old is None:
            return None
        move = yp - float(old[1])
        if abs(move) < 1e-12:
            return None
        side = "no" if move > 0 else "yes"
    else:
        raise ValueError(side_rule)
    p = yp if side == "yes" else np_
    return side, p, decision_ns


def first_entry_certificate(a, side: str, limit: float, arrival_ns: int, min_tte: int):
    start = int(np.searchsorted(a["ns"], arrival_ns, side="left"))
    if start >= len(a["ns"]):
        return None
    live = a["tte"][start:] >= min_tte - 1e-12
    if side == "yes":
        hit = live & (a["side"][start:] == "no") & (a["yp"][start:] < limit - 1e-12)
    else:
        hit = live & (a["side"][start:] == "yes") & (a["np"][start:] < limit - 1e-12)
    k = np.flatnonzero(hit)
    return None if not len(k) else start + int(k[0])


def first_exit_certificate(a, side: str, ask: float, arrival_ns: int):
    start = int(np.searchsorted(a["ns"], arrival_ns, side="left"))
    if start >= len(a["ns"]):
        return None
    if side == "yes":
        # Aggressive YES buys strictly above our live YES ask.
        hit = (a["side"][start:] == "yes") & (a["yp"][start:] > ask + 1e-12)
    else:
        # Aggressive NO buys strictly above our live NO ask.
        hit = (a["side"][start:] == "no") & (a["np"][start:] > ask + 1e-12)
    k = np.flatnonzero(hit)
    return None if not len(k) else start + int(k[0])


def simulate(rule: Rule, markets: pd.DataFrame, arrays: dict[str, dict[str, np.ndarray]],
             split_days: set[pd.Timestamp], latency_extra: float = 0.0,
             adverse_ct: float = 0.0) -> pd.DataFrame:
    rows = []
    lat = rule.latency + latency_extra
    sub = markets[markets.day.isin(split_days)]
    for r in sub.itertuples(index=False):
        a = arrays.get(str(r.ticker))
        if a is None:
            continue
        chosen = choose_side(a, rule.tau, rule.side_rule)
        if chosen is None:
            continue
        side, current_side_price, decision_ns = chosen
        entry = math.floor((current_side_price - rule.offset) * 1000 + 1e-9) / 1000.0
        if not (0.05 <= entry <= rule.entry_cap):
            continue
        arrival_ns = decision_ns + int(lat * 1e9)
        ei = first_entry_certificate(a, side, entry, arrival_ns, rule.entry_min_tte)
        if ei is None:
            rows.append({"ticker": r.ticker, "close_dt": r.close_dt, "day": r.day,
                         "attempt": True, "entered": False, "completed": False, "side": side,
                         "entry": entry, "exit": math.nan, "pnl": 0.0, "position_max": 0.0})
            continue
        cert_ns = int(a["ns"][ei])
        ask = math.ceil((entry + rule.take_profit) * 1000 - 1e-9) / 1000.0
        if ask >= 0.995:
            continue
        exit_arrival = cert_ns + int(lat * 1e9)
        xi = first_exit_certificate(a, side, ask, exit_arrival)
        entry_debit = QTY * (entry + adverse_ct) + fee(QTY, entry)
        if xi is not None:
            exit_credit = QTY * (ask - adverse_ct) - fee(QTY, ask)
            pnl = exit_credit - entry_debit
            completed = True
            exit_ns = int(a["ns"][xi])
        else:
            won = bool(r.yes) if side == "yes" else not bool(r.yes)
            pnl = QTY * float(won) - entry_debit
            completed = False
            exit_ns = None
        rows.append({
            "ticker": r.ticker, "close_dt": r.close_dt, "day": r.day,
            "attempt": True, "entered": True, "completed": completed, "side": side,
            "decision_ns": decision_ns, "entry_cert_ns": cert_ns, "exit_cert_ns": exit_ns,
            "entry": entry, "exit": ask if completed else math.nan,
            "pnl": float(pnl), "position_max": QTY,
        })
    return pd.DataFrame(rows)


def block_lcb(x: np.ndarray, block: int, reps: int = 6000) -> float:
    n = len(x)
    if n < 10:
        return -math.inf
    block = max(2, min(block, n))
    rng = np.random.default_rng(SEED + n + block)
    k = math.ceil(n / block)
    starts = rng.integers(0, n, size=(reps, k))
    offs = np.arange(block)
    idx = (starts[:, :, None] + offs[None, None, :]) % n
    idx = idx.reshape(reps, -1)[:, :n]
    ann = x[idx].sum(axis=1) / n * 365.0
    return float(np.quantile(ann, 0.05))


def metrics(ledger: pd.DataFrame, markets: pd.DataFrame, split_days: set[pd.Timestamp], bootstrap=False):
    idx = pd.DatetimeIndex(sorted(split_days))
    n_days = len(idx)
    subm = markets[markets.day.isin(split_days)].copy()
    pnl_map = ledger.groupby("ticker").pnl.sum() if len(ledger) else pd.Series(dtype=float)
    subm["pnl"] = subm.ticker.map(pnl_map).fillna(0.0)
    daily = subm.groupby("day").pnl.sum().reindex(idx, fill_value=0.0)
    total = float(daily.sum())
    annual = total / n_days * 365.0 if n_days else -math.inf
    subm["block2h"] = subm.close_dt.dt.floor("2h")
    blocks = subm.groupby("block2h").pnl.sum()
    best_day = max(0.0, float(daily.max())) if len(daily) else 0.0
    best_block = max(0.0, float(blocks.max())) if len(blocks) else 0.0
    entered = ledger[ledger.entered.astype(bool)] if len(ledger) and "entered" in ledger else pd.DataFrame()
    winners = entered.loc[entered.pnl > 0, "pnl"].sort_values(ascending=False) if len(entered) else pd.Series(dtype=float)
    k = int(math.ceil(0.10 * len(entered))) if len(entered) else 0
    half = max(1, n_days // 2)
    half_annual = []
    for ds in (set(idx[:half]), set(idx[half:])):
        if not ds:
            continue
        d = daily.reindex(pd.DatetimeIndex(sorted(ds)), fill_value=0.0)
        half_annual.append(float(d.sum() / len(d) * 365.0))
    result = {
        "calendar_days": n_days,
        "source_markets": int(len(subm)),
        "attempted_markets": int(ledger.ticker.nunique()) if len(ledger) else 0,
        "entered_markets": int(entered.ticker.nunique()) if len(entered) else 0,
        "completed_cycles": int(entered.completed.sum()) if len(entered) else 0,
        "completion_rate": float(entered.completed.mean()) if len(entered) else 0.0,
        "net_pnl": total,
        "annual_net": annual,
        "annual_after_best_day_removed": (total - best_day) / n_days * 365.0 if n_days else -math.inf,
        "annual_after_best_2h_removed": (total - best_block) / n_days * 365.0 if n_days else -math.inf,
        "annual_after_top10pct_winners_removed": (total - float(winners.head(k).sum())) / n_days * 365.0 if n_days else -math.inf,
        "chronological_half_annual": half_annual,
        "mean_per_entered_market": float(entered.pnl.mean()) if len(entered) else 0.0,
        "median_per_entered_market": float(entered.pnl.median()) if len(entered) else 0.0,
        "positive_entered_fraction": float((entered.pnl > 0).mean()) if len(entered) else 0.0,
        "max_position_contracts": float(entered.position_max.max()) if len(entered) else 0.0,
        "aggregate_gross_face_notional_max": QTY if len(entered) else 0.0,
    }
    if bootstrap:
        x = daily.to_numpy(float)
        result["lcb_3day"] = block_lcb(x, 3)
        result["lcb_7day"] = block_lcb(x, 7)
        result["capacity_limited_95_lcb_annual"] = min(result["lcb_3day"], result["lcb_7day"])
    return result


def quick_score(m: dict) -> float:
    halves = m.get("chronological_half_annual", [])
    return min([
        m.get("annual_net", -math.inf),
        m.get("annual_after_best_day_removed", -math.inf),
        m.get("annual_after_best_2h_removed", -math.inf),
        m.get("annual_after_top10pct_winners_removed", -math.inf),
    ] + halves)


def passes(m: dict) -> bool:
    return (
        m.get("annual_net", -math.inf) > TARGET
        and m.get("capacity_limited_95_lcb_annual", -math.inf) > TARGET
        and m.get("annual_after_best_day_removed", -math.inf) > TARGET
        and m.get("annual_after_best_2h_removed", -math.inf) > TARGET
        and m.get("annual_after_top10pct_winners_removed", -math.inf) > TARGET
        and m.get("entered_markets", 0) >= 100
        and all(v > 0 for v in m.get("chronological_half_annual", []))
        and m.get("aggregate_gross_face_notional_max", math.inf) <= 100.0 + 1e-9
    )


def grid():
    out = []
    for tau in (90, 120, 150, 170):
        for side_rule in ("favorite", "cheaper", "contrarian5", "contrarian15"):
            for offset in (0.01, 0.02, 0.04, 0.06):
                for tp in (0.07, 0.10, 0.15, 0.20):
                    for latency in (1.0, 2.0):
                        for min_tte in (30, 60):
                            for cap in (0.75, 0.90):
                                if min_tte >= tau:
                                    continue
                                out.append(Rule(tau, side_rule, offset, tp, latency, min_tte, cap))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--vela", type=Path, required=True)
    ap.add_argument("--output", type=Path, required=True)
    args = ap.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)

    markets, trades, manifest = load(args.vela)
    arrays = trade_arrays(trades)
    days, train_days, val_days, hold_days = partition(markets)
    candidates = grid()
    screens = []
    for i, rule in enumerate(candidates, 1):
        led = simulate(rule, markets, arrays, train_days)
        met = metrics(led, markets, train_days, bootstrap=False)
        screens.append({"rule": asdict(rule), "train": met, "score": quick_score(met)})
        if i % 100 == 0:
            print(json.dumps({"screened": i, "total": len(candidates), "best": max(x["score"] for x in screens)}), flush=True)
    screens.sort(key=lambda x: x["score"], reverse=True)

    # Train-only refinement of uncertainty for top 20; no validation has been read yet.
    top = []
    for row in screens[:20]:
        rule = Rule(**row["rule"])
        led = simulate(rule, markets, arrays, train_days)
        met = metrics(led, markets, train_days, bootstrap=True)
        stress_led = simulate(rule, markets, arrays, train_days, latency_extra=1.0, adverse_ct=0.01)
        stress_met = metrics(stress_led, markets, train_days, bootstrap=False)
        row = {"rule": asdict(rule), "train": met, "train_stress_1s_1c_each_leg": stress_met,
               "score": min(quick_score(met), stress_met.get("annual_net", -math.inf))}
        top.append(row)
    top.sort(key=lambda x: x["score"], reverse=True)
    frozen = Rule(**top[0]["rule"])

    train_ledger = simulate(frozen, markets, arrays, train_days)
    train = metrics(train_ledger, markets, train_days, bootstrap=True)
    val_ledger = simulate(frozen, markets, arrays, val_days)
    validation = metrics(val_ledger, markets, val_days, bootstrap=True)
    validation_stress = metrics(
        simulate(frozen, markets, arrays, val_days, latency_extra=1.0, adverse_ct=0.01),
        markets, val_days, bootstrap=True,
    )

    holdout_opened = passes(train) and passes(validation)
    holdout = None
    holdout_stresses = None
    hold_ledger = pd.DataFrame()
    if holdout_opened:
        hold_ledger = simulate(frozen, markets, arrays, hold_days)
        holdout = metrics(hold_ledger, markets, hold_days, bootstrap=True)
        holdout_stresses = {}
        for extra, adverse in ((1.0, 0.0), (2.0, 0.0), (0.0, 0.01), (1.0, 0.01)):
            key = f"latency_plus_{extra:g}s_adverse_{adverse*100:g}c_each_leg"
            holdout_stresses[key] = metrics(
                simulate(frozen, markets, arrays, hold_days, latency_extra=extra, adverse_ct=adverse),
                markets, hold_days, bootstrap=True,
            )

    all_pass = bool(
        holdout_opened
        and holdout is not None
        and passes(holdout)
        and holdout_stresses is not None
        and all(v.get("annual_net", -math.inf) > TARGET for v in holdout_stresses.values())
    )

    spec = {
        "mechanism": "one-position single-cycle intramarket volatility harvest with strict-through price-priority entry and reduce-only exit certificates",
        "entry_quantity_contracts": QTY,
        "max_position_contracts": QTY,
        "gross_face_notional_interpretation": "one 100-contract entry creates $100 face exposure; the sell exit is reduce-only and cannot increase gross exposure",
        "unfilled_entry_pnl": 0.0,
        "uncertified_exit_policy": "hold the one entered position to binary settlement",
        "fill_evidence": "strictly-through execution after declared communication latency; certificate timestamp is conservatively treated as fill-notification time",
        "fee_reserve": "full 7% taker coefficient on every certified passive entry/exit, whole-order cent rounding",
        "train_selection": "prespecified grid on first 50% calendar days only; bootstrap top 20 train rules; freeze one before validation",
        "validation": "next 25% calendar days, one touch",
        "holdout": "final 25% calendar days, opened only if frozen train and validation each clear every gate",
        "missing_trade_tape": "source markets without sampled trade tape are retained as zero PnL in calendar annualization",
    }
    frozen_hash = hashlib.sha256(json.dumps({"rule": asdict(frozen), "spec": spec}, sort_keys=True).encode()).hexdigest()
    result = {
        "source": manifest,
        "source_market_rows": int(len(markets)),
        "trade_rows": int(len(trades)),
        "trade_tape_markets": int(trades.ticker.nunique()),
        "calendar_start": str(days.min()),
        "calendar_end": str(days.max()),
        "calendar_days": int(len(days)),
        "candidate_count": len(candidates),
        "frozen_rule": asdict(frozen),
        "frozen_spec_sha256": frozen_hash,
        "spec": spec,
        "train": train,
        "validation": validation,
        "validation_stress_1s_1c_each_leg": validation_stress,
        "holdout_opened": holdout_opened,
        "holdout": holdout,
        "holdout_stresses": holdout_stresses,
        "passes_vela_original_profit_gates": all_pass,
        "top_20_train_only": top,
        "lockbox_policy": "no external July/August replication labels are accessed by this script",
    }
    (args.output / "single_cycle_price_priority.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    train_ledger.to_csv(args.output / "train_ledger.csv.gz", index=False, compression="gzip")
    val_ledger.to_csv(args.output / "validation_ledger.csv.gz", index=False, compression="gzip")
    if holdout_opened:
        hold_ledger.to_csv(args.output / "holdout_ledger.csv.gz", index=False, compression="gzip")
    print(json.dumps({
        "candidate_count": len(candidates),
        "frozen_rule": asdict(frozen),
        "train": train,
        "validation": validation,
        "holdout_opened": holdout_opened,
        "holdout": holdout,
        "passes": all_pass,
    }, indent=2), flush=True)


if __name__ == "__main__":
    main()
