from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import math
import os
import re
import statistics
import sys
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable
from urllib import request
from zoneinfo import ZoneInfo

import pandas as pd

ROOT = Path(__file__).resolve().parent
DATASET = "live_90_70"
EDGE_DIR = ROOT / "logs" / "edge_research"
CASE_CACHE_PATH = EDGE_DIR / "live_90_70_heartbeat_cases.json.gz"
MEMORY_PATH = EDGE_DIR / "strategy_memory.json"
IDEA_LEDGER_PATH = EDGE_DIR / "edge_idea_ledger.jsonl"
IDEA_INDEX_PATH = EDGE_DIR / "edge_idea_index.json"
TRADES_PATH = ROOT / "stats" / DATASET / "trades.csv"
ORIGINAL_LOG_DIR = Path(r"C:\Users\organ\Desktop\kalshi btc bot SCALED\logs\live_90_70")
LOCAL_LOG_DIR = ROOT / "logs" / DATASET
ET = ZoneInfo("America/New_York")
UTC = timezone.utc

HEARTBEAT_RE = re.compile(
    r"^(?P<ts>\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d{3}).*"
    r"Heartbeat \| watch=(?P<market>\S+) yes_bid=(?P<yes>\S+) yes_ask=\S+ "
    r"no_bid=(?P<no>\S+) no_ask=\S+"
)


@dataclass(frozen=True)
class CandidateStrategy:
    strategy_id: str
    family: str
    theorem: str
    equation: str
    params: dict[str, Any]
    simulator: Callable[[dict[str, Any]], tuple[float, dict[str, Any]]]


def parse_log_ts(value: str) -> datetime:
    return datetime.strptime(value, "%Y-%m-%d %H:%M:%S,%f").replace(tzinfo=ET).astimezone(UTC)


def parse_float(value: str) -> float | None:
    if value in {"None", "null", ""}:
        return None
    try:
        return float(value)
    except ValueError:
        return None


def estimated_order_fee_cents(price_cents: float, count: int) -> int:
    bounded_price = max(1, min(99, int(round(float(price_cents)))))
    numerator = 7 * int(count) * bounded_price * (100 - bounded_price)
    return max(1, (numerator + 9999) // 10000)


def stats(values: list[float | None]) -> dict[str, Any] | None:
    clean = sorted(float(value) for value in values if value is not None and not pd.isna(value))
    if not clean:
        return None

    def pct(q: float) -> float:
        if len(clean) == 1:
            return clean[0]
        k = (len(clean) - 1) * q
        f = int(k)
        c = min(f + 1, len(clean) - 1)
        return clean[f] + (clean[c] - clean[f]) * (k - f)

    return {
        "n": len(clean),
        "avg": round(statistics.mean(clean), 4),
        "median": round(statistics.median(clean), 4),
        "p25": round(pct(0.25), 4),
        "p75": round(pct(0.75), 4),
        "p90": round(pct(0.90), 4),
        "p95": round(pct(0.95), 4),
        "min": round(min(clean), 4),
        "max": round(max(clean), 4),
    }


def exit_pnl(case: dict[str, Any], bid: float) -> float:
    qty = int(case["qty"])
    entry = float(case["entry"])
    entry_fee = float(case["entry_fee_cents"])
    exit_fee = estimated_order_fee_cents(bid, qty)
    return round((qty * (bid - entry) - entry_fee - exit_fee) / 100.0, 4)


def hold_pnl(row: pd.Series) -> float:
    entry = float(row["entry_fill_cents_used"])
    qty = int(row["qty"])
    fee = float(row.get("entry_fee_cents", 0.0) or 0.0)
    if bool(row["settlement_win"]):
        return round((qty * (100 - entry) - fee) / 100.0, 4)
    return round(-(qty * entry + fee) / 100.0, 4)


def candidate_log_files() -> list[Path]:
    log_dir = ORIGINAL_LOG_DIR if ORIGINAL_LOG_DIR.exists() else LOCAL_LOG_DIR
    preferred = [log_dir / "bot.log.1", log_dir / "bot.log"]
    return [path for path in preferred if path.exists()]


def build_case_cache() -> list[dict[str, Any]]:
    if not TRADES_PATH.exists():
        raise FileNotFoundError(f"Missing trades file: {TRADES_PATH}")

    trades = pd.read_csv(TRADES_PATH)
    trades = trades[pd.notna(trades["entry_fill_cents_used"])].copy()
    trades["entry_local"] = pd.to_datetime(trades["entry_ts"], errors="coerce").dt.tz_localize(
        ET, ambiguous="NaT", nonexistent="NaT"
    )
    trades["entry_utc"] = trades["entry_local"].dt.tz_convert("UTC")
    trades["settlement_utc"] = pd.to_datetime(trades["settlement_ts"], errors="coerce", utc=True)
    trades["side_l"] = trades["side"].astype(str).str.lower()
    trades["result_l"] = trades["result"].fillna(trades["market_result"]).astype(str).str.lower()
    trades["settlement_win"] = trades["side_l"] == trades["result_l"]

    markets = set(trades["market"].astype(str))
    heartbeat_series: dict[str, list[tuple[datetime, float | None, float | None]]] = {market: [] for market in markets}

    scanned_lines = 0
    matched_lines = 0
    start = time.time()
    for log_path in candidate_log_files():
        with log_path.open("r", encoding="utf-8", errors="ignore") as handle:
            for line in handle:
                scanned_lines += 1
                if "Heartbeat | watch=" not in line:
                    continue
                match = HEARTBEAT_RE.search(line)
                if not match:
                    continue
                market = match.group("market")
                if market not in heartbeat_series:
                    continue
                yes = parse_float(match.group("yes"))
                no = parse_float(match.group("no"))
                if yes is None and no is None:
                    continue
                heartbeat_series[market].append((parse_log_ts(match.group("ts")), yes, no))
                matched_lines += 1

    cases: list[dict[str, Any]] = []
    for _, row in trades.iterrows():
        market = str(row["market"])
        entry_utc = row["entry_utc"]
        if pd.isna(entry_utc):
            continue
        settlement_utc = row["settlement_utc"]
        end_utc = (
            settlement_utc + pd.Timedelta(seconds=60)
            if not pd.isna(settlement_utc)
            else entry_utc + pd.Timedelta(minutes=15)
        )
        side = str(row["side_l"])
        path: list[list[float]] = []
        for ts, yes_bid, no_bid in heartbeat_series.get(market, []):
            if ts < entry_utc or ts > end_utc:
                continue
            bid = yes_bid if side == "yes" else no_bid
            if bid is None:
                continue
            elapsed = round((ts - entry_utc.to_pydatetime()).total_seconds(), 3)
            if elapsed >= 0:
                path.append([elapsed, float(bid)])
        if not path:
            continue
        entry = float(row["entry_fill_cents_used"])
        bids = [point[1] for point in path]
        case = {
            "market": market,
            "side": side,
            "entry": entry,
            "entry_trigger_cents": float(row["entry_trigger_cents"]),
            "qty": int(row["qty"]),
            "entry_fee_cents": float(row.get("entry_fee_cents", 0.0) or 0.0),
            "actual_net_pnl": float(row["net_pnl_dollars"]),
            "actual_outcome": str(row["outcome"]),
            "settlement_win": bool(row["settlement_win"]),
            "hold_pnl": hold_pnl(row),
            "min_bid": min(bids),
            "max_drawdown": max(0.0, entry - min(bids)),
            "path": path,
        }
        cases.append(case)

    EDGE_DIR.mkdir(parents=True, exist_ok=True)
    payload = {
        "generated_at": datetime.now(UTC).isoformat(),
        "source_logs": [str(path) for path in candidate_log_files()],
        "trades_total": int(len(trades)),
        "cases": cases,
        "scan_stats": {
            "scanned_lines": scanned_lines,
            "matched_heartbeat_lines": matched_lines,
            "elapsed_seconds": round(time.time() - start, 3),
        },
    }
    with gzip.open(CASE_CACHE_PATH, "wt", encoding="utf-8") as handle:
        json.dump(payload, handle)
    return cases


def load_cases(refresh_cache: bool = False) -> list[dict[str, Any]]:
    if refresh_cache or not CASE_CACHE_PATH.exists():
        return build_case_cache()
    with gzip.open(CASE_CACHE_PATH, "rt", encoding="utf-8") as handle:
        payload = json.load(handle)
    return list(payload["cases"])


def path_after(case: dict[str, Any], activate_seconds: float = 0.0) -> list[tuple[float, float]]:
    return [(float(t), float(bid)) for t, bid in case["path"] if float(t) >= activate_seconds]


def nearest_bid(case: dict[str, Any], seconds: float, window: float = 15.0) -> float | None:
    candidates = [
        (abs(float(t) - seconds), float(bid))
        for t, bid in case["path"]
        if seconds - window <= float(t) <= seconds + window
    ]
    if not candidates:
        return None
    return min(candidates, key=lambda item: item[0])[1]


def first_bid_at_or_below(
    case: dict[str, Any], *, threshold: float, activate_seconds: float, confirm_seconds: float = 0.0
) -> tuple[float, dict[str, Any]]:
    armed_at: float | None = None
    for elapsed, bid in path_after(case, activate_seconds):
        if bid <= threshold:
            if confirm_seconds <= 0:
                return exit_pnl(case, bid), {"exit": True, "exit_bid": bid, "exit_elapsed": elapsed}
            if armed_at is None:
                armed_at = elapsed
            elif elapsed - armed_at >= confirm_seconds:
                return exit_pnl(case, bid), {"exit": True, "exit_bid": bid, "exit_elapsed": elapsed}
        else:
            armed_at = None
    return float(case["hold_pnl"]), {"exit": False}


def sim_area_deficit(case: dict[str, Any], params: dict[str, Any]) -> tuple[float, dict[str, Any]]:
    activate = float(params["activate"])
    threshold = float(params["threshold"])
    area_limit = float(params["area_limit"])
    reclaim_bonus = float(params["reclaim_bonus"])
    prev_t: float | None = None
    deficit_area = 0.0
    surplus_area = 0.0
    armed = False
    for elapsed, bid in path_after(case, activate):
        if prev_t is None:
            prev_t = elapsed
            continue
        dt = min(30.0, max(0.0, elapsed - prev_t))
        deficit_area += max(0.0, threshold - bid) * dt
        surplus_area += max(0.0, bid - (threshold + reclaim_bonus)) * dt
        score = deficit_area - 0.45 * surplus_area
        if bid <= threshold:
            armed = True
        if armed and score >= area_limit:
            return exit_pnl(case, bid), {
                "exit": True,
                "exit_bid": bid,
                "exit_elapsed": elapsed,
                "score": round(score, 4),
            }
        prev_t = elapsed
    return float(case["hold_pnl"]), {"exit": False}


def sim_rebound_half_life(case: dict[str, Any], params: dict[str, Any]) -> tuple[float, dict[str, Any]]:
    activate = float(params["activate"])
    danger = float(params["danger"])
    wait = float(params["wait"])
    min_rebound = float(params["min_rebound"])
    points = path_after(case, activate)
    for idx, (elapsed, bid) in enumerate(points):
        if bid > danger:
            continue
        low = bid
        end_t = elapsed + wait
        window = [(t, b) for t, b in points[idx:] if t <= end_t]
        if not window:
            continue
        max_rebound = max(b for _, b in window) - low
        last_t, last_bid = window[-1]
        if max_rebound < min_rebound and last_bid <= danger + min_rebound:
            return exit_pnl(case, last_bid), {
                "exit": True,
                "exit_bid": last_bid,
                "exit_elapsed": last_t,
                "max_rebound": round(max_rebound, 4),
            }
    return float(case["hold_pnl"]), {"exit": False}


def sim_entropy_cliff(case: dict[str, Any], params: dict[str, Any]) -> tuple[float, dict[str, Any]]:
    activate = float(params["activate"])
    threshold = float(params["threshold"])
    entropy_min = float(params["entropy_min"])
    slope_window = float(params["slope_window"])
    points = path_after(case, activate)
    for idx, (elapsed, bid) in enumerate(points):
        if bid > threshold:
            continue
        p = max(0.01, min(0.99, bid / 100.0))
        entropy = -(p * math.log(p) + (1.0 - p) * math.log(1.0 - p))
        previous = [(t, b) for t, b in points[: idx + 1] if elapsed - slope_window <= t <= elapsed]
        if len(previous) < 2:
            continue
        slope = bid - previous[0][1]
        if entropy >= entropy_min and slope <= -float(params["max_slope"]):
            return exit_pnl(case, bid), {
                "exit": True,
                "exit_bid": bid,
                "exit_elapsed": elapsed,
                "entropy": round(entropy, 4),
                "slope": round(slope, 4),
            }
    return float(case["hold_pnl"]), {"exit": False}


def sim_late_cliff(case: dict[str, Any], params: dict[str, Any]) -> tuple[float, dict[str, Any]]:
    activate = float(params["activate"])
    cliff_drop = float(params["cliff_drop"])
    floor = float(params["floor"])
    running_high = -1.0
    for elapsed, bid in path_after(case, 0.0):
        running_high = max(running_high, bid)
        if elapsed < activate:
            continue
        if running_high - bid >= cliff_drop and bid <= floor:
            return exit_pnl(case, bid), {
                "exit": True,
                "exit_bid": bid,
                "exit_elapsed": elapsed,
                "running_high": running_high,
            }
    return float(case["hold_pnl"]), {"exit": False}


def sim_hazard_curvature(case: dict[str, Any], params: dict[str, Any]) -> tuple[float, dict[str, Any]]:
    activate = float(params["activate"])
    cut = float(params["cut"])
    min_drawdown = float(params["min_drawdown"])
    running_low = 101.0
    for elapsed, bid in path_after(case, activate):
        running_low = min(running_low, bid)
        drawdown = max(0.0, float(case["entry"]) - bid)
        rebound = max(0.0, bid - running_low)
        time_factor = 1.0 + min(1.0, elapsed / 900.0)
        hazard = ((drawdown**2) / (rebound + 1.0)) * time_factor
        if drawdown >= min_drawdown and hazard >= cut:
            return exit_pnl(case, bid), {
                "exit": True,
                "exit_bid": bid,
                "exit_elapsed": elapsed,
                "hazard": round(hazard, 4),
            }
    return float(case["hold_pnl"]), {"exit": False}


def make_strategy_id(family: str, params: dict[str, Any]) -> str:
    encoded = json.dumps({"family": family, "params": params}, sort_keys=True)
    digest = hashlib.sha1(encoded.encode("utf-8")).hexdigest()[:8]
    return f"{family}_{digest}"


def candidate_catalog() -> list[CandidateStrategy]:
    strategies: list[CandidateStrategy] = []

    def add(
        family: str,
        theorem: str,
        equation: str,
        params: dict[str, Any],
        simulator: Callable[[dict[str, Any]], tuple[float, dict[str, Any]]],
    ) -> None:
        strategies.append(
            CandidateStrategy(
                strategy_id=make_strategy_id(family, params),
                family=family,
                theorem=theorem,
                equation=equation,
                params=params,
                simulator=simulator,
            )
        )

    for threshold in (82, 83, 85):
        for area_limit in (900, 1500, 2400, 3600):
            add(
                "drawdown_area_balance",
                "A loss is more likely terminal when time-integrated damage below a danger price exceeds recovery area.",
                "A = integral(max(0,K-P_t)dt) - 0.45*integral(max(0,P_t-(K+r))dt); exit if A > L.",
                {"activate": 60, "threshold": threshold, "area_limit": area_limit, "reclaim_bonus": 5},
                lambda case, p={"activate": 60, "threshold": threshold, "area_limit": area_limit, "reclaim_bonus": 5}: sim_area_deficit(case, p),
            )

    for danger in (80, 82, 85):
        for wait in (30, 45, 60):
            for min_rebound in (5, 8, 12):
                add(
                    "rebound_half_life",
                    "A recoverable U-shape should show rebound energy quickly after first danger breach.",
                    "R = max(P_t in [tau,tau+w]) - min(P_tau); exit if R < r before the half-life expires.",
                    {"activate": 60, "danger": danger, "wait": wait, "min_rebound": min_rebound},
                    lambda case, p={"activate": 60, "danger": danger, "wait": wait, "min_rebound": min_rebound}: sim_rebound_half_life(case, p),
                )

    for threshold in (80, 82, 85):
        for entropy_min in (0.45, 0.50, 0.55):
            add(
                "entropy_cliff",
                "A 90c position repricing toward maximum uncertainty while sloping down is a tail-risk event.",
                "H(p)=-p*ln(p)-(1-p)*ln(1-p); exit if H(P_t)>h and dP/dt is adverse.",
                {"activate": 60, "threshold": threshold, "entropy_min": entropy_min, "slope_window": 45, "max_slope": 8},
                lambda case, p={"activate": 60, "threshold": threshold, "entropy_min": entropy_min, "slope_window": 45, "max_slope": 8}: sim_entropy_cliff(case, p),
            )

    for activate in (120, 180, 240):
        for cliff_drop in (18, 24, 30):
            add(
                "late_cliff_guard",
                "A position that looked safe then suffers a late cliff should be treated differently from early noise.",
                "C = max(P_since_entry) - P_t; after tau, exit if C > c and P_t < floor.",
                {"activate": activate, "cliff_drop": cliff_drop, "floor": 82},
                lambda case, p={"activate": activate, "cliff_drop": cliff_drop, "floor": 82}: sim_late_cliff(case, p),
            )

    for min_drawdown in (10, 12, 15, 18):
        for cut in (90, 140, 220, 320):
            add(
                "hazard_curvature",
                "Convex damage matters more than linear damage when rebound is weak.",
                "Q = ((entry-P_t)^2/(rebound_from_low+1))*(1+t/900); exit if Q > q.",
                {"activate": 60, "min_drawdown": min_drawdown, "cut": cut},
                lambda case, p={"activate": 60, "min_drawdown": min_drawdown, "cut": cut}: sim_hazard_curvature(case, p),
            )

    return strategies


def load_memory() -> dict[str, Any]:
    if not MEMORY_PATH.exists():
        return {"tested_strategy_ids": [], "runs": []}
    try:
        return json.loads(MEMORY_PATH.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {"tested_strategy_ids": [], "runs": []}


def save_memory(memory: dict[str, Any]) -> None:
    EDGE_DIR.mkdir(parents=True, exist_ok=True)
    MEMORY_PATH.write_text(json.dumps(memory, indent=2, sort_keys=True), encoding="utf-8")


def load_idea_index() -> dict[str, Any]:
    if not IDEA_INDEX_PATH.exists():
        return {"idea_keys": [], "tested_strategy_ids": []}
    try:
        loaded = json.loads(IDEA_INDEX_PATH.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {"idea_keys": [], "tested_strategy_ids": []}
    return {
        "idea_keys": list(loaded.get("idea_keys", [])),
        "tested_strategy_ids": list(loaded.get("tested_strategy_ids", [])),
    }


def save_idea_index(index: dict[str, Any]) -> None:
    EDGE_DIR.mkdir(parents=True, exist_ok=True)
    index["idea_keys"] = list(dict.fromkeys(index.get("idea_keys", [])))
    index["tested_strategy_ids"] = list(dict.fromkeys(index.get("tested_strategy_ids", [])))
    IDEA_INDEX_PATH.write_text(json.dumps(index, indent=2, sort_keys=True), encoding="utf-8")


def strategy_idea_key(strategy: CandidateStrategy) -> str:
    canonical = json.dumps(
        {
            "family": strategy.family,
            "equation": strategy.equation,
            "params": strategy.params,
        },
        sort_keys=True,
    )
    return hashlib.sha1(canonical.encode("utf-8")).hexdigest()


def append_idea_ledger(records: list[dict[str, Any]]) -> None:
    if not records:
        return
    EDGE_DIR.mkdir(parents=True, exist_ok=True)
    index = load_idea_index()
    known_keys = set(index.get("idea_keys", []))
    known_strategy_ids = set(index.get("tested_strategy_ids", []))
    new_records: list[dict[str, Any]] = []
    for record in records:
        idea_key = str(record.get("idea_key") or "")
        strategy_id = str(record.get("strategy_id") or "")
        if idea_key and idea_key in known_keys:
            continue
        if strategy_id and strategy_id in known_strategy_ids:
            continue
        new_records.append(record)
        if idea_key:
            known_keys.add(idea_key)
        if strategy_id:
            known_strategy_ids.add(strategy_id)
    if not new_records:
        return
    with IDEA_LEDGER_PATH.open("a", encoding="utf-8") as handle:
        for record in new_records:
            handle.write(json.dumps(record, sort_keys=True) + "\n")
    index["idea_keys"] = sorted(known_keys)
    index["tested_strategy_ids"] = sorted(known_strategy_ids)
    save_idea_index(index)


def backfill_idea_ledger_from_memory(memory: dict[str, Any]) -> None:
    catalog_by_id = {strategy.strategy_id: strategy for strategy in candidate_catalog()}
    records: list[dict[str, Any]] = []
    for run in memory.get("runs", []):
        for strategy_id in run.get("strategy_ids", []):
            strategy = catalog_by_id.get(strategy_id)
            if strategy is None:
                records.append(
                    {
                        "recorded_at": datetime.now(UTC).isoformat(),
                        "status": "tested_backfilled",
                        "source": "strategy_memory",
                        "dataset": DATASET,
                        "strategy_id": strategy_id,
                        "idea_key": f"legacy:{strategy_id}",
                        "generated_at": run.get("generated_at"),
                        "json_path": run.get("json_path"),
                    }
                )
                continue
            records.append(
                {
                    "recorded_at": datetime.now(UTC).isoformat(),
                    "status": "tested_backfilled",
                    "source": "strategy_memory",
                    "dataset": DATASET,
                    "strategy_id": strategy.strategy_id,
                    "idea_key": strategy_idea_key(strategy),
                    "family": strategy.family,
                    "theorem": strategy.theorem,
                    "equation": strategy.equation,
                    "params": strategy.params,
                    "generated_at": run.get("generated_at"),
                    "json_path": run.get("json_path"),
                }
            )
    append_idea_ledger(records)


def select_strategies(max_strategies: int) -> list[CandidateStrategy]:
    memory = load_memory()
    index = load_idea_index()
    tested = set(memory.get("tested_strategy_ids", [])) | set(index.get("tested_strategy_ids", []))
    tested_idea_keys = set(index.get("idea_keys", []))
    catalog = candidate_catalog()
    untested = [
        item for item in catalog if item.strategy_id not in tested and strategy_idea_key(item) not in tested_idea_keys
    ]
    hour_seed = datetime.now(UTC).strftime("%Y%m%d%H")
    ranked = sorted(
        untested,
        key=lambda item: hashlib.sha1(f"{hour_seed}:{item.strategy_id}".encode("utf-8")).hexdigest(),
    )
    return ranked[: max(0, min(3, max_strategies))]


def summarize_rows(label: str, rows: list[dict[str, Any]]) -> dict[str, Any]:
    exits = [row for row in rows if row["action"] == "exit"]
    exited_winners = [row for row in exits if row["settlement_win"]]
    exited_losers = [row for row in exits if not row["settlement_win"]]
    actual = sum(float(row["actual_net_pnl"]) for row in rows)
    hold = sum(float(row["hold_pnl"]) for row in rows)
    sim = sum(float(row["sim_pnl"]) for row in rows)
    return {
        "label": label,
        "n": len(rows),
        "actual_recorded_pnl": round(actual, 2),
        "hold_to_settlement_pnl": round(hold, 2),
        "sim_pnl": round(sim, 2),
        "delta_vs_hold": round(sim - hold, 2),
        "delta_vs_actual": round(sim - actual, 2),
        "exits": len(exits),
        "exited_settlement_winners": len(exited_winners),
        "exited_settlement_losers": len(exited_losers),
        "avg_exit_bid": round(statistics.mean([row["exit_bid"] for row in exits]), 2) if exits else None,
        "worst_trade": round(min(float(row["sim_pnl"]) for row in rows), 2) if rows else None,
    }


def run_strategy(cases: list[dict[str, Any]], strategy: CandidateStrategy) -> dict[str, Any]:
    rows: list[dict[str, Any]] = []
    for case in cases:
        pnl, meta = strategy.simulator(case)
        exit_bid = meta.get("exit_bid")
        rows.append(
            {
                "market": case["market"],
                "settlement_win": bool(case["settlement_win"]),
                "actual_outcome": case["actual_outcome"],
                "actual_net_pnl": float(case["actual_net_pnl"]),
                "hold_pnl": float(case["hold_pnl"]),
                "sim_pnl": float(pnl),
                "action": "exit" if meta.get("exit") else "hold",
                "exit_bid": float(exit_bid) if exit_bid is not None else None,
                "entry": float(case["entry"]),
                "min_bid": float(case["min_bid"]),
                "max_drawdown": float(case["max_drawdown"]),
            }
        )
    summary = summarize_rows(strategy.strategy_id, rows)
    return {
        "strategy_id": strategy.strategy_id,
        "family": strategy.family,
        "theorem": strategy.theorem,
        "equation": strategy.equation,
        "params": strategy.params,
        "summary": summary,
        "interesting_examples": sorted(
            rows,
            key=lambda row: (
                float(row["sim_pnl"]) - float(row["hold_pnl"]),
                -float(row["max_drawdown"]),
            ),
        )[:8],
    }


def baseline_summary(cases: list[dict[str, Any]]) -> dict[str, Any]:
    rows = [
        {
            "actual_net_pnl": float(case["actual_net_pnl"]),
            "hold_pnl": float(case["hold_pnl"]),
            "sim_pnl": float(case["hold_pnl"]),
            "action": "hold",
            "exit_bid": None,
            "settlement_win": bool(case["settlement_win"]),
        }
        for case in cases
    ]
    return summarize_rows("hold_to_settlement", rows)


def drawdown_summary(cases: list[dict[str, Any]]) -> dict[str, Any]:
    winners = [case for case in cases if case["settlement_win"]]
    losers = [case for case in cases if not case["settlement_win"]]
    return {
        "winners": {
            "entry": stats([case["entry"] for case in winners]),
            "min_bid": stats([case["min_bid"] for case in winners]),
            "max_drawdown": stats([case["max_drawdown"] for case in winners]),
            "bid_60s": stats([nearest_bid(case, 60) for case in winners]),
            "bid_90s": stats([nearest_bid(case, 90) for case in winners]),
        },
        "losers": {
            "entry": stats([case["entry"] for case in losers]),
            "min_bid": stats([case["min_bid"] for case in losers]),
            "max_drawdown": stats([case["max_drawdown"] for case in losers]),
            "bid_60s": stats([nearest_bid(case, 60) for case in losers]),
            "bid_90s": stats([nearest_bid(case, 90) for case in losers]),
        },
    }


def parse_qwen_tool_text(content: str) -> dict[str, Any] | None:
    if "<tool_call>" not in content or "<function=emit_edge_hypotheses>" not in content:
        return None
    parsed: dict[str, Any] = {}
    for match in re.finditer(r"<parameter=([a-zA-Z0-9_]+)>\s*(.*?)(?=\n<parameter=|</function>|</tool_call>|$)", content, re.S):
        key = match.group(1)
        value = match.group(2).replace("</parameter>", "").strip()
        if key == "hypotheses":
            parsed[key] = json.loads(value)
        else:
            parsed[key] = value.strip().strip('"')
    return parsed if parsed.get("hypotheses") else None


def normalize_edge_hypotheses(parsed: dict[str, Any] | None) -> dict[str, Any] | None:
    if parsed is None:
        return None
    normalized = dict(parsed)
    hypotheses = normalized.get("hypotheses")
    if isinstance(hypotheses, str):
        try:
            normalized["hypotheses"] = json.loads(hypotheses)
        except json.JSONDecodeError:
            normalized["hypotheses_raw"] = hypotheses
    return normalized


def maybe_call_truffle(cases: list[dict[str, Any]], top_prior: dict[str, Any] | None) -> dict[str, Any]:
    endpoint = os.environ.get(
        "TRUFFLE_POST_ENTRY_SHADOW_ENDPOINT",
        "http://192.168.1.234/if2/v1/chat/completions",
    )
    model = os.environ.get("TRUFFLE_POST_ENTRY_SHADOW_MODEL", "Qwen3.6-35B-A3B")
    if os.environ.get("EDGE_RESEARCH_USE_TRUFFLE", "0").lower() in {"0", "false", "no"}:
        return {"enabled": False, "reason": "EDGE_RESEARCH_USE_TRUFFLE disabled"}

    winners = [case for case in cases if case["settlement_win"]]
    losers = [case for case in cases if not case["settlement_win"]]
    prompt_payload = {
        "dataset": DATASET,
        "case_count": len(cases),
        "actual_pnl": round(sum(float(case["actual_net_pnl"]) for case in cases), 2),
        "hold_to_settlement_pnl": round(sum(float(case["hold_pnl"]) for case in cases), 2),
        "winner_drawdown": stats([case["max_drawdown"] for case in winners]),
        "loser_drawdown": stats([case["max_drawdown"] for case in losers]),
        "top_prior_strategy": top_prior,
        "task": "Invent 1-3 compact, testable Truffle supervisory hypotheses for Kalshi BTC 15m edge research. Do not suggest live trading changes.",
    }
    tool_name = "emit_edge_hypotheses"
    tool_schema = [
        {
            "type": "function",
            "function": {
                "name": tool_name,
                "description": (
                    "Emit compact research-only hypotheses that can be turned into deterministic "
                    "backtests on historical Kalshi BTC 15 minute trade paths."
                ),
                "parameters": {
                    "type": "object",
                    "additionalProperties": False,
                    "properties": {
                        "hypotheses": {
                            "type": "array",
                            "minItems": 1,
                            "maxItems": 3,
                            "items": {
                                "type": "object",
                                "additionalProperties": False,
                                "properties": {
                                    "name": {"type": "string"},
                                    "equation": {"type": "string"},
                                    "why_it_might_work": {"type": "string"},
                                    "failure_mode": {"type": "string"},
                                    "backtest_spec": {"type": "string"},
                                },
                                "required": [
                                    "name",
                                    "equation",
                                    "why_it_might_work",
                                    "failure_mode",
                                    "backtest_spec",
                                ],
                            },
                        },
                        "most_promising_next_backtest": {"type": "string"},
                        "skeptical_note": {"type": "string"},
                    },
                    "required": ["hypotheses", "most_promising_next_backtest", "skeptical_note"],
                },
            },
        }
    ]
    body = {
        "model": model,
        "messages": [
            {
                "role": "system",
                "content": (
                    "You are an aggressive but skeptical quant research assistant. "
                    "Use the tool call only. Do not write prose. Do not reveal hidden reasoning. "
                    "Invent compact equations only when they map to backtestable price-path features. "
                    "Be terse: each string field must be one short sentence."
                ),
            },
            {"role": "user", "content": json.dumps(prompt_payload, sort_keys=True)},
        ],
        "max_tokens": 1200,
        "temperature": 0.4,
        "tools": tool_schema,
        "tool_choice": {"type": "function", "function": {"name": tool_name}},
        "reasoning": {"enabled": False},
        "extra_body": {"chat_template_kwargs": {"enable_thinking": False}},
    }
    started = time.time()
    try:
        req = request.Request(
            endpoint,
            data=json.dumps(body).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with request.urlopen(req, timeout=45) as resp:
            raw = resp.read().decode("utf-8", errors="replace")
        elapsed = round(time.time() - started, 3)
        parsed_raw = json.loads(raw)
        message = parsed_raw.get("choices", [{}])[0].get("message", {})
        content = message.get("content", "") or ""
        tool_calls = message.get("tool_calls") or []
        tool_arguments = ""
        if tool_calls:
            tool_arguments = tool_calls[0].get("function", {}).get("arguments", "") or ""
        try:
            parsed_content = json.loads(tool_arguments or content)
            parse_error = None
        except json.JSONDecodeError as exc:
            try:
                parsed_content = parse_qwen_tool_text(content)
                parse_error = None if parsed_content is not None else repr(exc)
            except Exception as inner_exc:
                parsed_content = None
                parse_error = f"{repr(exc)}; qwen_tool_parse={repr(inner_exc)}"
        parsed_content = normalize_edge_hypotheses(parsed_content)
        return {
            "enabled": True,
            "ok": parsed_content is not None,
            "endpoint": endpoint,
            "model": model,
            "elapsed_seconds": elapsed,
            "content_excerpt": content[:500],
            "tool_arguments_excerpt": tool_arguments[:1000],
            "parsed_content": parsed_content,
            "parse_error": parse_error,
            "usage": parsed_raw.get("usage", {}),
        }
    except Exception as exc:
        return {
            "enabled": True,
            "ok": False,
            "endpoint": endpoint,
            "model": model,
            "error": repr(exc),
            "elapsed_seconds": round(time.time() - started, 3),
        }


def write_markdown_report(path: Path, payload: dict[str, Any]) -> None:
    baseline = payload["baseline"]
    truffle_ideation = payload.get("truffle_ideation", {})
    truffle_report = {
        "enabled": truffle_ideation.get("enabled"),
        "ok": truffle_ideation.get("ok"),
        "endpoint": truffle_ideation.get("endpoint"),
        "model": truffle_ideation.get("model"),
        "elapsed_seconds": truffle_ideation.get("elapsed_seconds"),
        "parsed_content": truffle_ideation.get("parsed_content"),
        "parse_error": truffle_ideation.get("parse_error") or truffle_ideation.get("error"),
        "content_excerpt": truffle_ideation.get("content_excerpt"),
        "tool_arguments_excerpt": truffle_ideation.get("tool_arguments_excerpt"),
        "usage": truffle_ideation.get("usage"),
    }
    lines = [
        "# Hourly Truffle Edge Research",
        "",
        f"- Generated: `{payload['generated_at']}`",
        f"- Dataset: `{payload['dataset']}`",
        f"- Cases: `{payload['case_count']}`",
        f"- Actual recorded PnL: `${baseline['actual_recorded_pnl']}`",
        f"- Hypothetical hold-to-settlement PnL: `${baseline['hold_to_settlement_pnl']}`",
        f"- Idea ledger: `{payload.get('idea_ledger_path')}`",
        "",
        "## Tested Strategies",
    ]
    for result in payload["strategy_results"]:
        summary = result["summary"]
        lines.extend(
            [
                "",
                f"### {result['family']} `{result['strategy_id']}`",
                "",
                f"- Theorem: {result['theorem']}",
                f"- Equation: `{result['equation']}`",
                f"- Params: `{json.dumps(result['params'], sort_keys=True)}`",
                f"- Sim PnL: `${summary['sim_pnl']}`",
                f"- Delta vs actual: `${summary['delta_vs_actual']}`",
                f"- Delta vs no-stop hold: `${summary['delta_vs_hold']}`",
                f"- Exits: `{summary['exits']}`",
                f"- Exited settlement winners: `{summary['exited_settlement_winners']}`",
                f"- Exited settlement losers: `{summary['exited_settlement_losers']}`",
            ]
        )
    lines.extend(
        [
            "",
            "## Truffle Ideation",
            "",
            "```json",
            json.dumps(truffle_report, indent=2, sort_keys=True),
            "```",
            "",
            "## Guardrail",
            "",
            "This run is research-only. It does not modify live entry or exit logic.",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Hourly research-only edge hunter for the Kalshi BTC bot.")
    parser.add_argument("--max-strategies", type=int, default=3)
    parser.add_argument("--refresh-cache", action="store_true")
    parser.add_argument("--no-truffle", action="store_true")
    parser.add_argument("--use-truffle", action="store_true")
    args = parser.parse_args()

    if args.use_truffle:
        os.environ["EDGE_RESEARCH_USE_TRUFFLE"] = "1"
    if args.no_truffle:
        os.environ["EDGE_RESEARCH_USE_TRUFFLE"] = "0"

    EDGE_DIR.mkdir(parents=True, exist_ok=True)
    backfill_idea_ledger_from_memory(load_memory())
    cases = load_cases(refresh_cache=args.refresh_cache)
    strategies = select_strategies(args.max_strategies)
    baseline = baseline_summary(cases)
    results = [run_strategy(cases, strategy) for strategy in strategies]
    best_result = max(results, key=lambda result: result["summary"]["sim_pnl"]) if results else None
    truffle = maybe_call_truffle(cases, best_result["summary"] if best_result else None)

    payload = {
        "generated_at": datetime.now(UTC).isoformat(),
        "dataset": DATASET,
        "case_count": len(cases),
        "baseline": baseline,
        "drawdown_summary": drawdown_summary(cases),
        "strategy_results": results,
        "truffle_ideation": truffle,
        "idea_ledger_path": str(IDEA_LEDGER_PATH),
        "idea_index_path": str(IDEA_INDEX_PATH),
        "live_logic_changed": False,
    }

    stamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
    json_path = EDGE_DIR / f"hourly_edge_research_{stamp}.json"
    latest_json = EDGE_DIR / "hourly_edge_research_latest.json"
    md_path = EDGE_DIR / f"hourly_edge_research_{stamp}.md"
    latest_md = EDGE_DIR / "hourly_edge_research_latest.md"
    json_text = json.dumps(payload, indent=2, sort_keys=True)
    json_path.write_text(json_text, encoding="utf-8")
    latest_json.write_text(json_text, encoding="utf-8")
    write_markdown_report(md_path, payload)
    write_markdown_report(latest_md, payload)

    results_by_id = {result["strategy_id"]: result for result in results}
    append_idea_ledger(
        [
            {
                "recorded_at": datetime.now(UTC).isoformat(),
                "status": "tested",
                "source": "hourly_truffle_edge_research.py",
                "dataset": DATASET,
                "strategy_id": strategy.strategy_id,
                "idea_key": strategy_idea_key(strategy),
                "family": strategy.family,
                "theorem": strategy.theorem,
                "equation": strategy.equation,
                "params": strategy.params,
                "generated_at": payload["generated_at"],
                "json_path": str(json_path),
                "markdown_path": str(md_path),
                "summary": results_by_id.get(strategy.strategy_id, {}).get("summary"),
            }
            for strategy in strategies
        ]
    )

    memory = load_memory()
    tested = list(dict.fromkeys([*memory.get("tested_strategy_ids", []), *[s.strategy_id for s in strategies]]))
    memory["tested_strategy_ids"] = tested
    memory.setdefault("runs", []).append(
        {
            "generated_at": payload["generated_at"],
            "json_path": str(json_path),
            "strategy_ids": [s.strategy_id for s in strategies],
            "best_sim_pnl": best_result["summary"]["sim_pnl"] if best_result else None,
            "best_delta_vs_actual": best_result["summary"]["delta_vs_actual"] if best_result else None,
        }
    )
    save_memory(memory)

    print(f"Saved hourly edge research JSON: {json_path}")
    print(f"Saved hourly edge research Markdown: {md_path}")
    print(
        f"Baseline actual={baseline['actual_recorded_pnl']} "
        f"hold={baseline['hold_to_settlement_pnl']} cases={len(cases)}"
    )
    for result in results:
        summary = result["summary"]
        print(
            f"{result['strategy_id']}: sim={summary['sim_pnl']} "
            f"delta_actual={summary['delta_vs_actual']} exits={summary['exits']}"
        )
    if not results:
        print("No untested built-in strategies remain. Extend the research catalog before the next run.")
    if truffle.get("ok"):
        print(f"Truffle ideation ok in {truffle.get('elapsed_seconds')}s")
    else:
        print(f"Truffle ideation unavailable: {truffle.get('error') or truffle.get('reason')}")


if __name__ == "__main__":
    main()
