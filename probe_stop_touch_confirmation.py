from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import math
import re
import statistics
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable
from zoneinfo import ZoneInfo

import pandas as pd


ROOT = Path(__file__).resolve().parent
DATASET = "live_90_70"
EDGE_DIR = ROOT / "logs" / "edge_research"
CROSS_BOOK_CACHE = EDGE_DIR / "live_90_70_cross_book_cases.json.gz"
TRADES_PATH = ROOT / "stats" / DATASET / "trades.csv"
MARKET_RESULTS_PATH = ROOT / "stats" / DATASET / "market_results.csv"
LOCAL_LOG_DIR = ROOT / "logs" / DATASET
LEDGER_PATH = EDGE_DIR / "edge_idea_ledger.jsonl"
INDEX_PATH = EDGE_DIR / "edge_idea_index.json"
STRATEGY_MEMORY_PATH = EDGE_DIR / "strategy_memory.json"
ET = ZoneInfo("America/New_York")
UTC = timezone.utc

HEARTBEAT_RE = re.compile(
    r"^(?P<ts>\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d{3}).*"
    r"Heartbeat \| watch=(?P<market>\S+) yes_bid=(?P<yes_bid>\S+) yes_ask=(?P<yes_ask>\S+) "
    r"no_bid=(?P<no_bid>\S+) no_ask=(?P<no_ask>\S+)"
)


@dataclass(frozen=True)
class StrategySpec:
    family: str
    theorem: str
    equation: str
    params: dict[str, Any]
    simulator: Callable[[dict[str, Any], dict[str, Any]], tuple[float, dict[str, Any]]]


def parse_log_ts(value: str) -> datetime:
    return datetime.strptime(value, "%Y-%m-%d %H:%M:%S,%f").replace(tzinfo=ET).astimezone(UTC)


def parse_float(value: Any) -> float | None:
    if value is None:
        return None
    text = str(value)
    if text in {"None", "nan", "NaN", "null", ""}:
        return None
    try:
        return float(text)
    except ValueError:
        return None


def first_present(*values: Any) -> str | None:
    for value in values:
        if value is None:
            continue
        if pd.isna(value):
            continue
        text = str(value).strip()
        if text and text.lower() not in {"nan", "none"}:
            return text
    return None


def estimated_order_fee_cents(price_cents: float, count: int) -> int:
    bounded_price = max(1, min(99, int(round(float(price_cents)))))
    numerator = 7 * int(count) * bounded_price * (100 - bounded_price)
    return max(1, (numerator + 9999) // 10000)


def exit_pnl(case: dict[str, Any], bid: float) -> float:
    qty = int(case["qty"])
    entry = float(case["entry"])
    entry_fee = float(case["entry_fee_cents"])
    exit_fee = estimated_order_fee_cents(bid, qty)
    return round((qty * (bid - entry) - entry_fee - exit_fee) / 100.0, 4)


def hold_pnl(row: pd.Series, settlement_win: bool) -> float:
    qty = int(row["qty"])
    entry = float(row["entry_fill_cents_used"])
    fee = float(row.get("entry_fee_cents", 0.0) or 0.0)
    if settlement_win:
        return round((qty * (100 - entry) - fee) / 100.0, 4)
    return round(-(qty * entry + fee) / 100.0, 4)


def candidate_log_files() -> list[Path]:
    preferred = [LOCAL_LOG_DIR / "bot.log.1", LOCAL_LOG_DIR / "bot.log"]
    return [path for path in preferred if path.exists()]


def load_trades_with_final_results() -> pd.DataFrame:
    trades = pd.read_csv(TRADES_PATH)
    market_results = pd.read_csv(MARKET_RESULTS_PATH)
    final = market_results[["market", "result", "settlement_ts"]].rename(
        columns={"result": "final_result", "settlement_ts": "final_settlement_ts"}
    )
    trades = trades.merge(final, on="market", how="left")
    trades = trades[pd.notna(trades["entry_fill_cents_used"])].copy()
    trades["side_l"] = trades["side"].astype(str).str.lower()
    trades["final_result_l"] = trades.apply(
        lambda row: str(
            first_present(row.get("result"), row.get("market_result"), row.get("final_result")) or ""
        ).lower(),
        axis=1,
    )
    trades["settlement_win_final"] = trades["side_l"] == trades["final_result_l"]
    trades["entry_local"] = pd.to_datetime(trades["entry_ts"], errors="coerce").dt.tz_localize(
        ET, ambiguous="NaT", nonexistent="NaT"
    )
    trades["entry_utc"] = trades["entry_local"].dt.tz_convert("UTC")
    settlement_text = trades.apply(
        lambda row: first_present(row.get("settlement_ts"), row.get("final_settlement_ts")),
        axis=1,
    )
    trades["settlement_utc"] = pd.to_datetime(settlement_text, errors="coerce", utc=True)
    return trades


def build_cross_book_cases() -> list[dict[str, Any]]:
    trades = load_trades_with_final_results()
    markets = set(trades["market"].astype(str))
    heartbeat_series: dict[str, list[tuple[datetime, float | None, float | None, float | None, float | None]]] = {
        market: [] for market in markets
    }

    scanned_lines = 0
    matched_lines = 0
    started = time.time()
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
                yes_bid = parse_float(match.group("yes_bid"))
                yes_ask = parse_float(match.group("yes_ask"))
                no_bid = parse_float(match.group("no_bid"))
                no_ask = parse_float(match.group("no_ask"))
                if yes_bid is None and no_bid is None:
                    continue
                heartbeat_series[market].append((parse_log_ts(match.group("ts")), yes_bid, yes_ask, no_bid, no_ask))
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
        path: list[dict[str, float]] = []
        for ts, yes_bid, yes_ask, no_bid, no_ask in heartbeat_series.get(market, []):
            if ts < entry_utc or ts > end_utc:
                continue
            own_bid = yes_bid if side == "yes" else no_bid
            opp_bid = no_bid if side == "yes" else yes_bid
            own_ask = yes_ask if side == "yes" else no_ask
            opp_ask = no_ask if side == "yes" else yes_ask
            if own_bid is None:
                continue
            elapsed = round((ts - entry_utc.to_pydatetime()).total_seconds(), 3)
            if elapsed < 0:
                continue
            point = {
                "elapsed": float(elapsed),
                "own_bid": float(own_bid),
                "opp_bid": float(opp_bid) if opp_bid is not None else math.nan,
                "own_ask": float(own_ask) if own_ask is not None else math.nan,
                "opp_ask": float(opp_ask) if opp_ask is not None else math.nan,
                "yes_bid": float(yes_bid) if yes_bid is not None else math.nan,
                "no_bid": float(no_bid) if no_bid is not None else math.nan,
            }
            if not math.isnan(point["opp_bid"]):
                point["bid_sum"] = point["own_bid"] + point["opp_bid"]
            else:
                point["bid_sum"] = math.nan
            if math.isnan(point["own_ask"]) and not math.isnan(point["opp_bid"]):
                point["held_ask"] = 100.0 - point["opp_bid"]
            else:
                point["held_ask"] = point["own_ask"]
            path.append(point)
        if not path:
            continue
        settlement_win = bool(row["settlement_win_final"])
        hold = hold_pnl(row, settlement_win)
        entry_utc_dt = entry_utc.to_pydatetime()
        cases.append(
            {
                "market": market,
                "side": side,
                "entry_ts": entry_utc_dt.isoformat(),
                "entry_day_et": entry_utc_dt.astimezone(ET).strftime("%Y-%m-%d"),
                "entry": float(row["entry_fill_cents_used"]),
                "entry_trigger_cents": float(row["entry_trigger_cents"]),
                "qty": int(row["qty"]),
                "entry_fee_cents": float(row.get("entry_fee_cents", 0.0) or 0.0),
                "actual_net_pnl": float(row["net_pnl_dollars"]),
                "actual_outcome": str(row["outcome"]),
                "actual_exit": bool(pd.notna(row.get("exit_ts"))),
                "actual_exit_bid": parse_float(row.get("exit_fill_cents_used")),
                "final_result": str(row["final_result_l"]),
                "settlement_win": settlement_win,
                "hold_pnl": hold,
                "path": path,
                "min_bid": min(float(point["own_bid"]) for point in path),
                "max_drawdown": max(0.0, float(row["entry_fill_cents_used"]) - min(float(point["own_bid"]) for point in path)),
            }
        )

    EDGE_DIR.mkdir(parents=True, exist_ok=True)
    payload = {
        "generated_at": datetime.now(UTC).isoformat(),
        "source_logs": [str(path) for path in candidate_log_files()],
        "trades_total": int(len(trades)),
        "cases": cases,
        "scan_stats": {
            "scanned_lines": scanned_lines,
            "matched_heartbeat_lines": matched_lines,
            "elapsed_seconds": round(time.time() - started, 3),
        },
        "label_note": "Settlement labels merge stats/live_90_70/market_results.csv, including stopped trades with blank trade-level market_result.",
    }
    with gzip.open(CROSS_BOOK_CACHE, "wt", encoding="utf-8") as handle:
        json.dump(payload, handle)
    return cases


def load_cases(refresh_cache: bool = False) -> list[dict[str, Any]]:
    if refresh_cache or not CROSS_BOOK_CACHE.exists():
        return build_cross_book_cases()
    with gzip.open(CROSS_BOOK_CACHE, "rt", encoding="utf-8") as handle:
        payload = json.load(handle)
    return list(payload["cases"])


def window_points(case: dict[str, Any], idx: int, width_seconds: float) -> list[dict[str, float]]:
    current_t = float(case["path"][idx]["elapsed"])
    lower = current_t - width_seconds
    return [point for point in case["path"][: idx + 1] if float(point["elapsed"]) >= lower]


def confirmed_stop_indices(
    case: dict[str, Any],
    *,
    stop: float,
    panic: float = 68.0,
    post_fill_delay: float = 30.0,
    confirm_checks: int = 2,
    confirm_seconds: float = 15.0,
) -> list[int]:
    indices: list[int] = []
    first_trigger_elapsed: float | None = None
    trigger_count = 0
    for idx, point in enumerate(case["path"]):
        elapsed = float(point["elapsed"])
        if elapsed < post_fill_delay:
            continue
        held_ask = float(point.get("held_ask", math.nan))
        if math.isnan(held_ask) or held_ask > stop:
            first_trigger_elapsed = None
            trigger_count = 0
            continue
        if held_ask <= panic:
            indices.append(idx)
            continue
        if first_trigger_elapsed is None:
            first_trigger_elapsed = elapsed
            trigger_count = 1
        else:
            trigger_count += 1
        if trigger_count >= confirm_checks or elapsed - first_trigger_elapsed >= confirm_seconds:
            indices.append(idx)
    return indices


def sim_cross_book_confirmed_stop(case: dict[str, Any], params: dict[str, Any]) -> tuple[float, dict[str, Any]]:
    stop = float(params["stop"])
    opp_confirm = float(params["opp_confirm"])
    min_bid_sum = float(params["min_bid_sum"])
    for idx in confirmed_stop_indices(case, stop=stop):
        point = case["path"][idx]
        bid = float(point["own_bid"])
        opp_bid = float(point["opp_bid"])
        bid_sum = float(point["bid_sum"])
        held_ask = float(point.get("held_ask", math.nan))
        if math.isnan(held_ask) or math.isnan(opp_bid) or math.isnan(bid_sum):
            continue
        if opp_bid >= opp_confirm and bid_sum >= min_bid_sum:
            return exit_pnl(case, bid), {
                "exit": True,
                "exit_bid": bid,
                "exit_elapsed": float(point["elapsed"]),
                "held_ask": held_ask,
                "opp_bid": opp_bid,
                "bid_sum": bid_sum,
            }
    return float(case["hold_pnl"]), {"exit": False}


def sim_stop_path_efficiency(case: dict[str, Any], params: dict[str, Any]) -> tuple[float, dict[str, Any]]:
    stop = float(params["stop"])
    window = float(params["window"])
    min_efficiency = float(params["min_efficiency"])
    min_window_drop = float(params["min_window_drop"])
    for idx in confirmed_stop_indices(case, stop=stop):
        point = case["path"][idx]
        bid = float(point["own_bid"])
        held_ask = float(point.get("held_ask", math.nan))
        points = window_points(case, idx, window)
        if len(points) < 2:
            continue
        held_asks = [float(item.get("held_ask", math.nan)) for item in points]
        if any(math.isnan(value) for value in held_asks):
            continue
        moves = [abs(held_asks[i] - held_asks[i - 1]) for i in range(1, len(held_asks))]
        path_length = sum(moves)
        net_drop = held_asks[0] - held_ask
        efficiency = max(0.0, net_drop) / (path_length + 1e-6)
        if net_drop >= min_window_drop and efficiency >= min_efficiency:
            return exit_pnl(case, bid), {
                "exit": True,
                "exit_bid": bid,
                "exit_elapsed": float(point["elapsed"]),
                "held_ask": held_ask,
                "net_drop": round(net_drop, 4),
                "efficiency": round(efficiency, 4),
            }
    return float(case["hold_pnl"]), {"exit": False}


def sim_stop_overshoot_acceleration(case: dict[str, Any], params: dict[str, Any]) -> tuple[float, dict[str, Any]]:
    stop = float(params["stop"])
    window = float(params["window"])
    min_score = float(params["min_score"])
    for idx in confirmed_stop_indices(case, stop=stop):
        point = case["path"][idx]
        bid = float(point["own_bid"])
        held_ask = float(point.get("held_ask", math.nan))
        points = window_points(case, idx, window)
        if len(points) < 2:
            continue
        start_held_ask = float(points[0].get("held_ask", math.nan))
        if math.isnan(start_held_ask) or math.isnan(held_ask):
            continue
        elapsed_span = max(1.0, float(points[-1]["elapsed"]) - float(points[0]["elapsed"]))
        drop_per_min = max(0.0, start_held_ask - held_ask) * 60.0 / elapsed_span
        overshoot = max(0.0, stop - held_ask)
        score = overshoot + drop_per_min
        if score >= min_score:
            return exit_pnl(case, bid), {
                "exit": True,
                "exit_bid": bid,
                "exit_elapsed": float(point["elapsed"]),
                "held_ask": held_ask,
                "overshoot": round(overshoot, 4),
                "drop_per_min": round(drop_per_min, 4),
                "score": round(score, 4),
            }
    return float(case["hold_pnl"]), {"exit": False}


def sim_deep_panic_salvage(case: dict[str, Any], params: dict[str, Any]) -> tuple[float, dict[str, Any]]:
    panic_trigger = float(params["panic_trigger"])
    for idx in confirmed_stop_indices(case, stop=panic_trigger, panic=panic_trigger):
        point = case["path"][idx]
        bid = float(point["own_bid"])
        return exit_pnl(case, bid), {
            "exit": True,
            "exit_bid": bid,
            "exit_elapsed": float(point["elapsed"]),
            "held_ask": float(point.get("held_ask", math.nan)),
        }
    return float(case["hold_pnl"]), {"exit": False}


def sim_deterministic_stop(case: dict[str, Any], stop: float) -> tuple[float, dict[str, Any]]:
    for idx in confirmed_stop_indices(case, stop=stop):
        point = case["path"][idx]
        bid = float(point["own_bid"])
        return exit_pnl(case, bid), {
            "exit": True,
            "exit_bid": bid,
            "exit_elapsed": float(point["elapsed"]),
            "held_ask": float(point.get("held_ask", math.nan)),
        }
    return float(case["hold_pnl"]), {"exit": False}


def strategy_id(family: str, params: dict[str, Any]) -> str:
    encoded = json.dumps({"family": family, "params": params}, sort_keys=True)
    return f"{family}_{hashlib.sha1(encoded.encode('utf-8')).hexdigest()[:8]}"


def idea_key(family: str, equation: str, params: dict[str, Any]) -> str:
    encoded = json.dumps({"family": family, "equation": equation, "params": params}, sort_keys=True)
    return hashlib.sha1(encoded.encode("utf-8")).hexdigest()


def build_strategy_grid() -> list[StrategySpec]:
    strategies: list[StrategySpec] = []

    def add(
        family: str,
        theorem: str,
        equation: str,
        params: dict[str, Any],
        simulator: Callable[[dict[str, Any], dict[str, Any]], tuple[float, dict[str, Any]]],
    ) -> None:
        strategies.append(StrategySpec(family, theorem, equation, params, simulator))

    for stop in (68, 70, 72):
        for opp_confirm in (28, 32, 36, 40, 44):
            for min_bid_sum in (94, 96, 98):
                add(
                    "held_ask_cross_book_confirmed_stop",
                    "A stop touch is more trustworthy when the opposite contract is bid aggressively and the two-sided bid book is not slack.",
                    "At a confirmed held_ask <= S stop, exit when opposite_bid >= C and own_bid + opposite_bid >= B; otherwise keep holding to settlement.",
                    {"stop": stop, "opp_confirm": opp_confirm, "min_bid_sum": min_bid_sum},
                    sim_cross_book_confirmed_stop,
                )

    for stop in (68, 70, 72):
        for window in (45, 60, 90):
            for min_efficiency in (0.45, 0.60, 0.75, 0.90):
                for min_window_drop in (8, 12, 16):
                    add(
                        "held_ask_stop_path_efficiency",
                        "True terminal stops should arrive through directional price discovery; false stops should look choppier.",
                        "ER=(held_ask_start-held_ask_t)/(sum(|delta held_ask|)+epsilon) over W seconds; exit at confirmed held_ask <= S when ER >= E and window_drop >= D.",
                        {
                            "stop": stop,
                            "window": window,
                            "min_efficiency": min_efficiency,
                            "min_window_drop": min_window_drop,
                        },
                        sim_stop_path_efficiency,
                    )

    for stop in (68, 70, 72):
        for window in (30, 45, 60, 90):
            for min_score in (10, 14, 18, 22, 26):
                add(
                    "held_ask_stop_overshoot_acceleration",
                    "A shallow stop graze should be treated differently from a fast overshoot through the stop.",
                    "A=max(0,S-held_ask_t)+max(0,held_ask_start-held_ask_t)*60/elapsed_window; exit at confirmed held_ask <= S when A >= L.",
                    {"stop": stop, "window": window, "min_score": min_score},
                    sim_stop_overshoot_acceleration,
                )

    for panic_trigger in (5, 10, 15, 20, 25, 30):
        add(
            "held_ask_deep_panic_salvage",
            "If corrected settlement labels show most ordinary stop exits are false positives, only a near-zero held-side ask may be worth salvaging.",
            "Exit only when confirmed held_ask <= P, with P far below the 70c stop; otherwise hold to settlement.",
            {"panic_trigger": panic_trigger},
            sim_deep_panic_salvage,
        )

    return strategies


def summarize_rows(label: str, rows: list[dict[str, Any]]) -> dict[str, Any]:
    exits = [row for row in rows if row["action"] == "exit"]
    false_exits = [row for row in exits if row["settlement_win"]]
    true_loser_exits = [row for row in exits if not row["settlement_win"]]
    true_losers = [row for row in rows if not row["settlement_win"]]
    missed_true_losers = [row for row in rows if not row["settlement_win"] and row["action"] != "exit"]
    actual = sum(float(row["actual_net_pnl"]) for row in rows)
    no_stop = sum(float(row["hold_pnl"]) for row in rows)
    sim = sum(float(row["sim_pnl"]) for row in rows)
    return {
        "label": label,
        "n": len(rows),
        "actual_recorded_pnl": round(actual, 2),
        "no_stop_hold_pnl": round(no_stop, 2),
        "sim_pnl": round(sim, 2),
        "delta_vs_actual": round(sim - actual, 2),
        "delta_vs_no_stop": round(sim - no_stop, 2),
        "exits": len(exits),
        "false_exit_settlement_winners": len(false_exits),
        "true_loser_exits": len(true_loser_exits),
        "true_losers": len(true_losers),
        "missed_true_losers": len(missed_true_losers),
        "false_exit_rate": round(len(false_exits) / len(exits), 4) if exits else 0.0,
        "missed_true_loser_rate": round(len(missed_true_losers) / len(true_losers), 4) if true_losers else 0.0,
        "avg_exit_bid": round(statistics.mean([row["exit_bid"] for row in exits]), 2) if exits else None,
        "worst_trade": round(min(float(row["sim_pnl"]) for row in rows), 2) if rows else None,
    }


def run_strategy(cases: list[dict[str, Any]], strategy: StrategySpec) -> dict[str, Any]:
    sid = strategy_id(strategy.family, strategy.params)
    rows: list[dict[str, Any]] = []
    for case in cases:
        pnl, meta = strategy.simulator(case, strategy.params)
        exit_bid = meta.get("exit_bid")
        rows.append(
            {
                "market": case["market"],
                "entry_day_et": case["entry_day_et"],
                "settlement_win": bool(case["settlement_win"]),
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
    by_day: dict[str, dict[str, Any]] = {}
    for day in sorted({row["entry_day_et"] for row in rows}):
        by_day[day] = summarize_rows(day, [row for row in rows if row["entry_day_et"] == day])
    return {
        "strategy_id": sid,
        "family": strategy.family,
        "theorem": strategy.theorem,
        "equation": strategy.equation,
        "params": strategy.params,
        "summary": summarize_rows(sid, rows),
        "by_day": by_day,
        "interesting_examples": sorted(
            rows,
            key=lambda row: (
                float(row["sim_pnl"]) - float(row["hold_pnl"]),
                -float(row["max_drawdown"]),
            ),
        )[:8],
    }


def baseline_rows(cases: list[dict[str, Any]], mode: str) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for case in cases:
        if mode == "actual":
            pnl = float(case["actual_net_pnl"])
            action = "actual_exit" if case["actual_exit"] else "actual_hold"
            exit_bid = case.get("actual_exit_bid")
        elif mode == "no_stop":
            pnl = float(case["hold_pnl"])
            action = "hold"
            exit_bid = None
        elif mode.startswith("stop_"):
            stop = float(mode.split("_", 1)[1])
            pnl, meta = sim_deterministic_stop(case, stop)
            action = "exit" if meta.get("exit") else "hold"
            exit_bid = meta.get("exit_bid")
        else:
            raise ValueError(mode)
        rows.append(
            {
                "market": case["market"],
                "entry_day_et": case["entry_day_et"],
                "settlement_win": bool(case["settlement_win"]),
                "actual_net_pnl": float(case["actual_net_pnl"]),
                "hold_pnl": float(case["hold_pnl"]),
                "sim_pnl": float(pnl),
                "action": "exit" if "exit" in action else "hold",
                "exit_bid": float(exit_bid) if exit_bid is not None and not pd.isna(exit_bid) else None,
            }
        )
    return rows


def select_family_best(results: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    best: dict[str, dict[str, Any]] = {}
    for result in results:
        family = result["family"]
        if family not in best or result["summary"]["sim_pnl"] > best[family]["summary"]["sim_pnl"]:
            best[family] = result
    return best


def walk_forward_summary(cases: list[dict[str, Any]], strategies: list[StrategySpec]) -> dict[str, Any]:
    ordered = sorted(cases, key=lambda case: case["entry_ts"])
    split = int(len(ordered) * 0.7)
    train = ordered[:split]
    holdout = ordered[split:]
    by_family: dict[str, list[StrategySpec]] = {}
    for strategy in strategies:
        by_family.setdefault(strategy.family, []).append(strategy)
    output: dict[str, Any] = {
        "train_n": len(train),
        "holdout_n": len(holdout),
        "split_entry_ts": ordered[split]["entry_ts"] if holdout else None,
        "families": {},
    }
    for family, items in by_family.items():
        train_results = [run_strategy(train, strategy) for strategy in items]
        selected = max(train_results, key=lambda result: result["summary"]["sim_pnl"])
        selected_spec = next(strategy for strategy in items if strategy_id(strategy.family, strategy.params) == selected["strategy_id"])
        holdout_result = run_strategy(holdout, selected_spec)
        output["families"][family] = {
            "selected_strategy_id": selected["strategy_id"],
            "selected_params": selected["params"],
            "train_summary": selected["summary"],
            "holdout_summary": holdout_result["summary"],
        }
    return output


def result_distance(params: dict[str, Any], best_params: dict[str, Any]) -> float:
    distance = 0.0
    for key, best in best_params.items():
        value = params.get(key)
        if isinstance(best, (int, float)) and isinstance(value, (int, float)):
            scale = max(1.0, abs(float(best)))
            distance += abs(float(value) - float(best)) / scale
        elif value != best:
            distance += 1.0
    return distance


def sensitivity(results: list[dict[str, Any]], best_by_family: dict[str, dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    output: dict[str, list[dict[str, Any]]] = {}
    for family, best in best_by_family.items():
        family_results = [result for result in results if result["family"] == family]
        ranked = sorted(
            family_results,
            key=lambda result: (result_distance(result["params"], best["params"]), -result["summary"]["sim_pnl"]),
        )
        output[family] = [
            {
                "strategy_id": result["strategy_id"],
                "params": result["params"],
                "sim_pnl": result["summary"]["sim_pnl"],
                "delta_vs_actual": result["summary"]["delta_vs_actual"],
                "delta_vs_no_stop": result["summary"]["delta_vs_no_stop"],
                "exits": result["summary"]["exits"],
                "false_exits": result["summary"]["false_exit_settlement_winners"],
                "missed_true_losers": result["summary"]["missed_true_losers"],
            }
            for result in ranked[:12]
        ]
    return output


def load_index() -> dict[str, list[str]]:
    if not INDEX_PATH.exists():
        return {"idea_keys": [], "tested_strategy_ids": []}
    try:
        loaded = json.loads(INDEX_PATH.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {"idea_keys": [], "tested_strategy_ids": []}
    return {
        "idea_keys": list(loaded.get("idea_keys", [])),
        "tested_strategy_ids": list(loaded.get("tested_strategy_ids", [])),
    }


def save_index(index: dict[str, list[str]]) -> None:
    index["idea_keys"] = list(dict.fromkeys(index.get("idea_keys", [])))
    index["tested_strategy_ids"] = list(dict.fromkeys(index.get("tested_strategy_ids", [])))
    INDEX_PATH.write_text(json.dumps(index, indent=2, sort_keys=True), encoding="utf-8")


def append_ledger(records: list[dict[str, Any]]) -> None:
    index = load_index()
    known_keys = set(index.get("idea_keys", []))
    known_ids = set(index.get("tested_strategy_ids", []))
    new_records: list[dict[str, Any]] = []
    for record in records:
        if record["idea_key"] in known_keys or record["strategy_id"] in known_ids:
            continue
        new_records.append(record)
        known_keys.add(record["idea_key"])
        known_ids.add(record["strategy_id"])
    if new_records:
        with LEDGER_PATH.open("a", encoding="utf-8") as handle:
            for record in new_records:
                handle.write(json.dumps(record, sort_keys=True) + "\n")
    index["idea_keys"] = list(known_keys)
    index["tested_strategy_ids"] = list(known_ids)
    save_index(index)


def update_strategy_memory(payload: dict[str, Any], best_results: dict[str, dict[str, Any]]) -> None:
    if STRATEGY_MEMORY_PATH.exists():
        try:
            memory = json.loads(STRATEGY_MEMORY_PATH.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            memory = {"runs": [], "tested_strategy_ids": []}
    else:
        memory = {"runs": [], "tested_strategy_ids": []}
    strategy_ids = [result["strategy_id"] for result in best_results.values()]
    memory["tested_strategy_ids"] = list(dict.fromkeys([*memory.get("tested_strategy_ids", []), *strategy_ids]))
    best = max(best_results.values(), key=lambda result: result["summary"]["sim_pnl"]) if best_results else None
    memory.setdefault("runs", []).append(
        {
            "generated_at": payload["generated_at"],
            "json_path": payload["json_path"],
            "strategy_ids": strategy_ids,
            "best_sim_pnl": best["summary"]["sim_pnl"] if best else None,
            "best_delta_vs_actual": best["summary"]["delta_vs_actual"] if best else None,
            "best_delta_vs_no_stop": best["summary"]["delta_vs_no_stop"] if best else None,
        }
    )
    STRATEGY_MEMORY_PATH.write_text(json.dumps(memory, indent=2, sort_keys=True), encoding="utf-8")


def write_markdown_report(path: Path, payload: dict[str, Any]) -> None:
    lines = [
        "# Codex Stop-Touch Confirmation Research",
        "",
        f"- Generated: `{payload['generated_at']}`",
        f"- Dataset: `{payload['dataset']}`",
        f"- Cases: `{payload['case_count']}`",
        "- Settlement labels: corrected by merging `stats/live_90_70/market_results.csv` for stopped trades.",
        f"- Actual recorded PnL: `${payload['baselines']['actual']['sim_pnl']}`",
        f"- Corrected no-stop hold-to-settlement PnL: `${payload['baselines']['no_stop']['sim_pnl']}`",
        f"- Deterministic confirmed held-ask stop 70 PnL: `${payload['baselines']['stop_70']['sim_pnl']}`",
        "",
        "## New Hypotheses Tested",
    ]
    for family, result in payload["best_by_family"].items():
        summary = result["summary"]
        holdout = payload["walk_forward"]["families"][family]["holdout_summary"]
        status = "candidate for review" if summary["delta_vs_no_stop"] > 0 and holdout["delta_vs_no_stop"] > 0 else "not robust enough"
        lines.extend(
            [
                "",
                f"### {family} `{result['strategy_id']}`",
                "",
                f"- Status: {status}",
                f"- Theorem: {result['theorem']}",
                f"- Equation: `{result['equation']}`",
                f"- Best params: `{json.dumps(result['params'], sort_keys=True)}`",
                f"- Full sample sim PnL: `${summary['sim_pnl']}`",
                f"- Delta vs actual: `${summary['delta_vs_actual']}`",
                f"- Delta vs no-stop hold: `${summary['delta_vs_no_stop']}`",
                f"- Exits / false exits / missed true losers: `{summary['exits']} / {summary['false_exit_settlement_winners']} / {summary['missed_true_losers']}`",
                f"- 70/30 holdout sim PnL: `${holdout['sim_pnl']}`",
                f"- 70/30 holdout delta vs no-stop: `${holdout['delta_vs_no_stop']}`",
            ]
        )
    lines.extend(
        [
            "",
            "## Truffle / Prior Policy Reference",
            "",
            f"- Online supervisor eval reference: `{json.dumps(payload['truffle_reference'], sort_keys=True)}`",
            "",
            "## Guardrail",
            "",
            "This run is research-only. It does not modify live entry logic, live exit logic, run scripts, or production config.",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")


def load_truffle_reference() -> dict[str, Any]:
    path = ROOT / "logs" / "online_exit_supervisor_policy_eval_latest.json"
    if not path.exists():
        return {"available": False}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return {"available": False, "error": repr(exc)}
    best: list[dict[str, Any]] = []
    for delay in data.get("delays", []):
        for policy in delay.get("top_policies", [])[:1]:
            best.append(
                {
                    "delay_seconds": delay.get("delay_seconds"),
                    "policy": policy.get("policy"),
                    "rule": policy.get("rule"),
                    "delta_dollars": policy.get("delta_dollars"),
                    "exit_count": policy.get("exit_count"),
                }
            )
    best_sorted = sorted(best, key=lambda item: float(item.get("delta_dollars") or -999), reverse=True)
    return {
        "available": True,
        "note": "Reference only; prior output is a delayed stop-slice policy eval, not the same full replay.",
        "best_top_policy_by_delay": best_sorted[:5],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Research-only stop-touch confirmation probes for live_90_70.")
    parser.add_argument("--refresh-cache", action="store_true")
    args = parser.parse_args()

    EDGE_DIR.mkdir(parents=True, exist_ok=True)
    cases = load_cases(refresh_cache=args.refresh_cache)
    strategies = build_strategy_grid()
    results = [run_strategy(cases, strategy) for strategy in strategies]
    best_by_family = select_family_best(results)
    walk = walk_forward_summary(cases, strategies)
    sens = sensitivity(results, best_by_family)

    baselines = {
        "actual": summarize_rows("actual", baseline_rows(cases, "actual")),
        "no_stop": summarize_rows("no_stop_hold_to_settlement", baseline_rows(cases, "no_stop")),
        "stop_68": summarize_rows("first_touch_stop_68", baseline_rows(cases, "stop_68")),
        "stop_70": summarize_rows("first_touch_stop_70", baseline_rows(cases, "stop_70")),
        "stop_72": summarize_rows("first_touch_stop_72", baseline_rows(cases, "stop_72")),
    }

    generated_at = datetime.now(UTC).isoformat()
    stamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
    json_path = EDGE_DIR / f"codex_stop_touch_research_{stamp}.json"
    md_path = EDGE_DIR / f"codex_stop_touch_research_{stamp}.md"
    latest_json = EDGE_DIR / "codex_stop_touch_research_latest.json"
    latest_md = EDGE_DIR / "codex_stop_touch_research_latest.md"

    payload = {
        "generated_at": generated_at,
        "dataset": DATASET,
        "case_count": len(cases),
        "label_correction": {
            "trade_csv_issue": "Stopped trades have blank trade-level final results.",
            "source_of_truth": str(MARKET_RESULTS_PATH),
            "actual_recorded_pnl": baselines["actual"]["sim_pnl"],
            "corrected_no_stop_hold_pnl": baselines["no_stop"]["sim_pnl"],
        },
        "baselines": baselines,
        "best_by_family": best_by_family,
        "sensitivity": sens,
        "walk_forward": walk,
        "truffle_reference": load_truffle_reference(),
        "json_path": str(json_path),
        "markdown_path": str(md_path),
        "live_logic_changed": False,
    }
    json_text = json.dumps(payload, indent=2, sort_keys=True)
    json_path.write_text(json_text, encoding="utf-8")
    latest_json.write_text(json_text, encoding="utf-8")
    write_markdown_report(md_path, payload)
    write_markdown_report(latest_md, payload)

    ledger_records = []
    for family, result in best_by_family.items():
        holdout = walk["families"][family]["holdout_summary"]
        summary = result["summary"]
        status = "candidate_for_human_review" if summary["delta_vs_no_stop"] > 0 and holdout["delta_vs_no_stop"] > 0 else "tested_not_robust"
        ledger_records.append(
            {
                "recorded_at": datetime.now(UTC).isoformat(),
                "status": status,
                "source": "probe_stop_touch_confirmation.py",
                "dataset": DATASET,
                "strategy_id": result["strategy_id"],
                "idea_key": idea_key(result["family"], result["equation"], result["params"]),
                "family": result["family"],
                "theorem": result["theorem"],
                "equation": result["equation"],
                "params": result["params"],
                "param_grid_size": len([item for item in results if item["family"] == family]),
                "generated_at": generated_at,
                "json_path": str(json_path),
                "markdown_path": str(md_path),
                "summary": summary,
                "holdout_summary": holdout,
                "sensitivity_excerpt": sens.get(family, [])[:5],
            }
        )
    append_ledger(ledger_records)
    update_strategy_memory(payload, best_by_family)

    print(f"Saved JSON: {json_path}")
    print(f"Saved Markdown: {md_path}")
    print(f"Cases={len(cases)} actual={baselines['actual']['sim_pnl']} no_stop={baselines['no_stop']['sim_pnl']} stop70={baselines['stop_70']['sim_pnl']}")
    for family, result in best_by_family.items():
        summary = result["summary"]
        holdout = walk["families"][family]["holdout_summary"]
        print(
            f"{family} {result['strategy_id']} sim={summary['sim_pnl']} "
            f"delta_actual={summary['delta_vs_actual']} delta_no_stop={summary['delta_vs_no_stop']} "
            f"exits={summary['exits']} false={summary['false_exit_settlement_winners']} "
            f"missed_losers={summary['missed_true_losers']} holdout_delta_no_stop={holdout['delta_vs_no_stop']}"
        )


if __name__ == "__main__":
    main()
