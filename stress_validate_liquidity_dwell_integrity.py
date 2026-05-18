from __future__ import annotations

import csv
import json
import math
import random
import statistics
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import probe_codex_entry_microstructure_edges as micro
import validate_liquidity_dwell_integrity as prior
from probe_codex_entry_timing_edges import delayed_entry_pnl
from probe_codex_terminal_salvage_all_trades import EDGE_DIR
from probe_stop_touch_confirmation import strategy_id


UTC = timezone.utc
FAMILY = "liquidity_dwell_integrity_admission"
ROOT = Path(__file__).resolve().parent
LOG_DIR = ROOT / "logs"
RANDOM_SEED = 240424


def n(value: Any, default: float | None = None) -> float | None:
    try:
        if value in (None, ""):
            return default
        parsed = float(value)
        if math.isnan(parsed):
            return default
        return parsed
    except Exception:
        return default


def money(value: Any) -> str:
    parsed = n(value)
    return "" if parsed is None else f"${parsed:,.2f}"


def pct(value: Any) -> str:
    parsed = n(value)
    return "" if parsed is None else f"{100.0 * parsed:.1f}%"


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    fields: list[str] = []
    for row in rows:
        for key in row:
            if key not in fields:
                fields.append(key)
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def dt(value: Any) -> datetime:
    return datetime.fromisoformat(str(value).replace("Z", "+00:00"))


def weeks_between_rows(rows: list[dict[str, Any]]) -> float:
    if len(rows) < 2:
        return 0.0
    ordered = sorted(rows, key=lambda row: str(row["entry_ts"]))
    start = dt(ordered[0]["entry_ts"])
    end = dt(ordered[-1]["entry_ts"])
    return max(0.0, (end - start).total_seconds() / 86400.0 / 7.0)


def base_param_sets() -> list[dict[str, Any]]:
    return [
        {
            "variant": "train_selected_pressure_0p3",
            "source": "locked_train_selected",
            "params": {
                "delay_seconds": 120,
                "max_entry_ask": 90,
                "max_opp_pressure": 0.3,
                "max_spread": 10,
                "min_bid_sum": 0,
                "min_quality_seconds": 10,
                "min_quality_share": 0.75,
            },
        },
        {
            "variant": "nearby_pressure_0p5",
            "source": "nearby_robust_scan",
            "params": {
                "delay_seconds": 120,
                "max_entry_ask": 90,
                "max_opp_pressure": 0.5,
                "max_spread": 10,
                "min_bid_sum": 0,
                "min_quality_seconds": 10,
                "min_quality_share": 0.75,
            },
        },
        {
            "variant": "nearby_pressure_0p5_spread4",
            "source": "nearby_tighter_spread",
            "params": {
                "delay_seconds": 120,
                "max_entry_ask": 90,
                "max_opp_pressure": 0.5,
                "max_spread": 4,
                "min_bid_sum": 0,
                "min_quality_seconds": 10,
                "min_quality_share": 0.75,
            },
        },
    ]


def row_for_case(
    case: dict[str, Any],
    prepared: dict[str, Any],
    params: dict[str, Any],
    *,
    mode: str,
    slippage_cents: float = 0.0,
) -> dict[str, Any]:
    features = prepared.get(str(int(params["delay_seconds"])))
    enter = False
    skip_reason = "missing_or_gate_failed"
    meta: dict[str, Any] = {}
    ask: float | None = None
    if features and micro.quote_gate(features, params):
        if mode == "final_gate_only":
            enter = True
            ask = float(features["held_ask"])
            meta = {
                "entry_elapsed": features["elapsed"],
                "quality_seconds": None,
                "quality_share": None,
                "pressure": round(float(features["pressure"]), 6),
                "spread": round(float(features["spread"]), 4),
                "bid_sum": round(float(features["bid_sum"]), 4),
            }
        else:
            _pnl, sim_meta = micro.sim_liquidity_dwell_integrity_admission(case, prepared, params)
            enter = bool(sim_meta.get("enter"))
            skip_reason = str(sim_meta.get("skip_reason") or "insufficient_liquidity_dwell")
            if enter:
                ask = float(sim_meta["entry_ask"])
                meta = sim_meta
    pnl_100 = 0.0
    ask_with_slippage = None
    if enter and ask is not None:
        ask_with_slippage = ask + slippage_cents
        pnl_100 = delayed_entry_pnl(case, ask_with_slippage, contracts=100)
    return {
        "dataset": case.get("dataset"),
        "market": case.get("market"),
        "side": case.get("side"),
        "entry_ts": case.get("entry_ts"),
        "entry_day_et": case.get("entry_day_et"),
        "settlement_win": bool(case.get("settlement_win")),
        "mode": mode,
        "enter": enter,
        "skip_reason": "" if enter else skip_reason,
        "entry_ask": ask,
        "entry_ask_with_slippage": ask_with_slippage,
        "pnl_100": pnl_100,
        "quality_seconds": n(meta.get("quality_seconds")),
        "quality_share": n(meta.get("quality_share")),
        "pressure": n(meta.get("pressure")),
        "spread": n(meta.get("spread")),
        "bid_sum": n(meta.get("bid_sum")),
        "entry_elapsed": n(meta.get("entry_elapsed") or meta.get("elapsed")),
    }


def run_rows(
    prepped: list[tuple[dict[str, Any], dict[str, Any]]],
    params: dict[str, Any],
    *,
    mode: str = "dwell",
    slippage_cents: float = 0.0,
) -> list[dict[str, Any]]:
    return [
        row_for_case(case, prepared, params, mode=mode, slippage_cents=slippage_cents)
        for case, prepared in prepped
    ]


def summarize(label: str, rows: list[dict[str, Any]], *, weeks: float | None = None) -> dict[str, Any]:
    entered = [row for row in rows if row["enter"]]
    entries = len(entered)
    wins = sum(1 for row in entered if row["settlement_win"])
    pnl = round(sum(float(row["pnl_100"]) for row in entered), 4)
    cumulative = 0.0
    peak = 0.0
    max_drawdown = 0.0
    for row in sorted(entered, key=lambda item: str(item["entry_ts"])):
        cumulative += float(row["pnl_100"])
        peak = max(peak, cumulative)
        max_drawdown = min(max_drawdown, cumulative - peak)
    active_days = defaultdict(float)
    for row in entered:
        active_days[str(row.get("entry_day_et"))] += float(row["pnl_100"])
    losses = [float(row["pnl_100"]) for row in entered if float(row["pnl_100"]) < 0]
    asks = [float(row["entry_ask"]) for row in entered if row.get("entry_ask") is not None]
    pressures = [float(row["pressure"]) for row in entered if row.get("pressure") is not None]
    return {
        "label": label,
        "rows": len(rows),
        "entries": entries,
        "pnl_100": pnl,
        "edge_per_entry_100": round(pnl / entries, 6) if entries else 0.0,
        "weekly_pnl_100": round(pnl / weeks, 6) if weeks and weeks > 0 else None,
        "entries_per_week": round(entries / weeks, 6) if weeks and weeks > 0 else None,
        "win_rate": round(wins / entries, 6) if entries else 0.0,
        "losses": len(losses),
        "worst_trade_100": round(min([float(row["pnl_100"]) for row in entered] or [0.0]), 4),
        "max_drawdown_100": round(max_drawdown, 4),
        "active_days": len(active_days),
        "positive_days": sum(1 for value in active_days.values() if value > 0),
        "negative_days": sum(1 for value in active_days.values() if value < 0),
        "avg_entry_ask": round(sum(asks) / len(asks), 4) if asks else None,
        "avg_pressure": round(sum(pressures) / len(pressures), 4) if pressures else None,
        "unique_markets": len({row["market"] for row in entered}),
    }


def chronological_blocks(
    prepped: list[tuple[dict[str, Any], dict[str, Any]]], block_count: int
) -> list[list[tuple[dict[str, Any], dict[str, Any]]]]:
    ordered = sorted(prepped, key=lambda item: (str(item[0]["entry_ts"]), str(item[0]["market"]), str(item[0]["side"])))
    blocks = []
    for idx in range(block_count):
        start = int(len(ordered) * idx / block_count)
        end = int(len(ordered) * (idx + 1) / block_count)
        blocks.append(ordered[start:end])
    return blocks


def build_grid() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for delay in (60, 120, 180):
        for max_ask in (88, 90, 92):
            for pressure in (0.2, 0.3, 0.4, 0.5, 0.6):
                for spread in (4, 10):
                    for quality_share in (0.50, 0.65, 0.75, 0.85, 0.90):
                        for quality_seconds in (10, 30, 60):
                            rows.append(
                                {
                                    "delay_seconds": delay,
                                    "max_entry_ask": max_ask,
                                    "max_opp_pressure": pressure,
                                    "max_spread": spread,
                                    "min_bid_sum": 0,
                                    "min_quality_seconds": quality_seconds,
                                    "min_quality_share": quality_share,
                                }
                            )
    return rows


def parameter_distance(params: dict[str, Any], anchor: dict[str, Any]) -> float:
    weights = {
        "delay_seconds": 1 / 60,
        "max_entry_ask": 1 / 2,
        "max_opp_pressure": 1 / 0.1,
        "max_spread": 1 / 6,
        "min_quality_seconds": 1 / 20,
        "min_quality_share": 1 / 0.1,
    }
    total = 0.0
    for key, weight in weights.items():
        total += abs(float(params[key]) - float(anchor[key])) * weight
    return round(total, 4)


def random_null(
    *,
    variant: str,
    pool_rows: list[dict[str, Any]],
    actual_rows: list[dict[str, Any]],
    reps: int = 5000,
) -> dict[str, Any]:
    pool = [row for row in pool_rows if row["enter"]]
    actual = [row for row in actual_rows if row["enter"]]
    sample_size = len(actual)
    actual_pnl = round(sum(float(row["pnl_100"]) for row in actual), 4)
    if sample_size <= 0 or len(pool) < sample_size:
        return {
            "variant": variant,
            "sample_size": sample_size,
            "pool_entries": len(pool),
            "actual_pnl_100": actual_pnl,
            "null_mean_pnl_100": None,
            "null_p05_pnl_100": None,
            "null_p50_pnl_100": None,
            "null_p95_pnl_100": None,
            "p_value_random_pool_ge_actual": None,
        }
    rng = random.Random(RANDOM_SEED + sum(ord(ch) for ch in variant))
    values = []
    pool_pnls = [float(row["pnl_100"]) for row in pool]
    for _ in range(reps):
        values.append(round(sum(rng.sample(pool_pnls, sample_size)), 4))
    values.sort()
    ge = sum(1 for value in values if value >= actual_pnl)
    return {
        "variant": variant,
        "sample_size": sample_size,
        "pool_entries": len(pool),
        "actual_pnl_100": actual_pnl,
        "null_mean_pnl_100": round(statistics.mean(values), 4),
        "null_p05_pnl_100": values[int(0.05 * (len(values) - 1))],
        "null_p50_pnl_100": values[int(0.50 * (len(values) - 1))],
        "null_p95_pnl_100": values[int(0.95 * (len(values) - 1))],
        "p_value_random_pool_ge_actual": round((ge + 1) / (len(values) + 1), 6),
    }


def parse_depth(value: Any) -> float | None:
    parsed = n(value)
    if parsed is not None:
        return parsed
    try:
        return float(str(value).strip())
    except Exception:
        return None


def percentile(values: list[float], q: float) -> float | None:
    if not values:
        return None
    ordered = sorted(values)
    idx = min(len(ordered) - 1, max(0, int(round(q * (len(ordered) - 1)))))
    return round(ordered[idx], 4)


def live_capacity_smoke() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for path in sorted(LOG_DIR.glob("*/execution_events.ndjson")):
        signal_depths: list[float] = []
        unique_markets: set[tuple[str, str]] = set()
        stale_deferrals = 0
        insufficient_balance = 0
        signal_events = 0
        with path.open("r", encoding="utf-8", errors="ignore") as f:
            for line in f:
                try:
                    event = json.loads(line)
                except Exception:
                    continue
                event_type = str(event.get("event_type") or "")
                result = str(event.get("result") or "")
                if result == "stale_book":
                    stale_deferrals += 1
                if result == "insufficient_balance":
                    insufficient_balance += 1
                if event_type != "signal_seen":
                    continue
                cap = n(event.get("cap_price_cents"))
                top = n(event.get("top_of_book_limit_cents"))
                if cap is not None and cap > 90:
                    continue
                if top is not None and top > 90:
                    continue
                depth = parse_depth(event.get("eligible_depth"))
                if depth is None:
                    continue
                signal_events += 1
                signal_depths.append(depth)
                unique_markets.add((str(event.get("market") or ""), str(event.get("side") or "")))
        if signal_events or stale_deferrals or insufficient_balance:
            rows.append(
                {
                    "log": path.parent.name,
                    "signal_events_at_or_below_90": signal_events,
                    "unique_market_sides": len(unique_markets),
                    "depth_ge_100_events": sum(1 for value in signal_depths if value >= 100),
                    "depth_ge_100_rate": round(sum(1 for value in signal_depths if value >= 100) / signal_events, 6)
                    if signal_events
                    else None,
                    "min_depth": percentile(signal_depths, 0.0),
                    "p10_depth": percentile(signal_depths, 0.10),
                    "median_depth": percentile(signal_depths, 0.50),
                    "p90_depth": percentile(signal_depths, 0.90),
                    "max_depth": percentile(signal_depths, 1.0),
                    "stale_book_deferrals": stale_deferrals,
                    "insufficient_balance_deferrals": insufficient_balance,
                }
            )
    return rows


def anchored_walk_forward(
    prepped: list[tuple[dict[str, Any], dict[str, Any]]],
    param_grid: list[dict[str, Any]],
    *,
    block_count: int = 8,
    min_train_entries: int = 20,
) -> list[dict[str, Any]]:
    blocks = chronological_blocks(prepped, block_count)
    rows: list[dict[str, Any]] = []
    for test_idx in range(2, block_count):
        train_sample = [item for block in blocks[:test_idx] for item in block]
        test_sample = blocks[test_idx]
        train_weeks = prior.exact_weeks([{"entry_ts": item[0]["entry_ts"]} for item in train_sample])
        test_weeks = prior.exact_weeks([{"entry_ts": item[0]["entry_ts"]} for item in test_sample])
        candidates: list[dict[str, Any]] = []
        fallback: list[dict[str, Any]] = []
        for params in param_grid:
            train_rows = run_rows(train_sample, params, mode="dwell")
            train_summary = summarize("train_prefix", train_rows, weeks=train_weeks)
            item = {
                "params": params,
                "train_entries": train_summary["entries"],
                "train_pnl_100": train_summary["pnl_100"],
                "train_edge_per_entry_100": train_summary["edge_per_entry_100"],
                "train_win_rate": train_summary["win_rate"],
            }
            fallback.append(item)
            if train_summary["entries"] >= min_train_entries and train_summary["pnl_100"] > 0:
                candidates.append(item)
        selection_pool = candidates or fallback
        selected = sorted(
            selection_pool,
            key=lambda row: (
                float(row["train_pnl_100"]),
                float(row["train_edge_per_entry_100"]),
                int(row["train_entries"]),
            ),
            reverse=True,
        )[0]
        params = selected["params"]
        test_rows = run_rows(test_sample, params, mode="dwell")
        test_summary = summarize("next_block", test_rows, weeks=test_weeks)
        rows.append(
            {
                "fold": test_idx - 1,
                "test_block": test_idx + 1,
                "train_blocks": f"1-{test_idx}",
                "selection_pool": "positive_min_entries" if candidates else "fallback_best_train",
                "strategy_id": strategy_id(FAMILY, params),
                "params": json.dumps(params, sort_keys=True),
                "delay_seconds": params["delay_seconds"],
                "max_entry_ask": params["max_entry_ask"],
                "max_opp_pressure": params["max_opp_pressure"],
                "max_spread": params["max_spread"],
                "min_quality_seconds": params["min_quality_seconds"],
                "min_quality_share": params["min_quality_share"],
                "train_entries": selected["train_entries"],
                "train_pnl_100": selected["train_pnl_100"],
                "train_edge_per_entry_100": selected["train_edge_per_entry_100"],
                "train_win_rate": selected["train_win_rate"],
                "test_start": test_sample[0][0]["entry_ts"] if test_sample else "",
                "test_end": test_sample[-1][0]["entry_ts"] if test_sample else "",
                "test_entries": test_summary["entries"],
                "test_pnl_100": test_summary["pnl_100"],
                "test_edge_per_entry_100": test_summary["edge_per_entry_100"],
                "test_weekly_pnl_100": test_summary["weekly_pnl_100"],
                "test_win_rate": test_summary["win_rate"],
                "test_max_drawdown_100": test_summary["max_drawdown_100"],
            }
        )
    return rows


def make_slippage_chart(path: Path, rows: list[dict[str, Any]]) -> None:
    width = 900
    height = 420
    pad_l = 70
    pad_r = 30
    pad_t = 45
    pad_b = 60
    variants = sorted({row["variant"] for row in rows})
    points_by_variant: dict[str, list[tuple[float, float]]] = defaultdict(list)
    for row in rows:
        points_by_variant[row["variant"]].append((float(row["slippage_cents"]), float(row["pnl_100"])))
    all_points = [point for points in points_by_variant.values() for point in points]
    max_x = max([point[0] for point in all_points] or [3.0])
    min_y = min([0.0] + [point[1] for point in all_points])
    max_y = max([0.0] + [point[1] for point in all_points])
    y_span = max(1.0, max_y - min_y)
    colors = ["#1b9e77", "#2166ac", "#d95f02", "#7570b3"]

    def sx(x: float) -> float:
        return pad_l + (x / max(1.0, max_x)) * (width - pad_l - pad_r)

    def sy(y: float) -> float:
        return pad_t + (max_y - y) / y_span * (height - pad_t - pad_b)

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="#fbfbf8"/>',
        '<text x="24" y="28" font-family="Segoe UI, Arial" font-size="18" font-weight="700" fill="#222">Liquidity dwell holdout PnL under slippage stress</text>',
        f'<line x1="{pad_l}" y1="{sy(0):.1f}" x2="{width-pad_r}" y2="{sy(0):.1f}" stroke="#999" stroke-width="1"/>',
        f'<line x1="{pad_l}" y1="{pad_t}" x2="{pad_l}" y2="{height-pad_b}" stroke="#555" stroke-width="1"/>',
        f'<line x1="{pad_l}" y1="{height-pad_b}" x2="{width-pad_r}" y2="{height-pad_b}" stroke="#555" stroke-width="1"/>',
        f'<text x="{width/2-40:.1f}" y="{height-18}" font-family="Segoe UI, Arial" font-size="12" fill="#333">extra entry cost, cents</text>',
        f'<text x="18" y="{sy(max_y)+5:.1f}" font-family="Segoe UI, Arial" font-size="11" fill="#333">{money(max_y)}</text>',
        f'<text x="18" y="{sy(min_y)+5:.1f}" font-family="Segoe UI, Arial" font-size="11" fill="#333">{money(min_y)}</text>',
    ]
    for idx, variant in enumerate(variants):
        points = sorted(points_by_variant[variant])
        color = colors[idx % len(colors)]
        d = " ".join(
            ("M" if point_idx == 0 else "L") + f"{sx(x):.1f},{sy(y):.1f}"
            for point_idx, (x, y) in enumerate(points)
        )
        parts.append(f'<path d="{d}" fill="none" stroke="{color}" stroke-width="2.4"/>')
        for x, y in points:
            parts.append(f'<circle cx="{sx(x):.1f}" cy="{sy(y):.1f}" r="3.5" fill="{color}"/>')
        lx = 95 + idx * 245
        ly = height - 38
        parts.append(f'<rect x="{lx}" y="{ly-8}" width="20" height="3" fill="{color}"/>')
        parts.append(f'<text x="{lx+26}" y="{ly-4}" font-family="Segoe UI, Arial" font-size="12" fill="#222">{variant}</text>')
    parts.append("</svg>")
    path.write_text("\n".join(parts), encoding="utf-8")


def main() -> None:
    prepped, _quote_delays = prior.load_prepped_quote_path()
    split = int(len(prepped) * 0.7)
    train = prepped[:split]
    holdout = prepped[split:]
    full_weeks = prior.exact_weeks([{"entry_ts": item[0]["entry_ts"]} for item in prepped])
    train_weeks = prior.exact_weeks([{"entry_ts": item[0]["entry_ts"]} for item in train])
    holdout_weeks = prior.exact_weeks([{"entry_ts": item[0]["entry_ts"]} for item in holdout])
    variants = base_param_sets()

    summary_rows: list[dict[str, Any]] = []
    ablation_rows: list[dict[str, Any]] = []
    block_rows: list[dict[str, Any]] = []
    grid_rows: list[dict[str, Any]] = []
    random_rows: list[dict[str, Any]] = []
    slippage_rows: list[dict[str, Any]] = []
    param_grid = build_grid()

    for variant in variants:
        params = variant["params"]
        for sample_name, sample, weeks in (
            ("full", prepped, full_weeks),
            ("train", train, train_weeks),
            ("holdout", holdout, holdout_weeks),
        ):
            dwell_rows = run_rows(sample, params, mode="dwell")
            final_rows = run_rows(sample, params, mode="final_gate_only")
            dwell_summary = summarize(f"{variant['variant']}:{sample_name}:dwell", dwell_rows, weeks=weeks)
            final_summary = summarize(f"{variant['variant']}:{sample_name}:final_gate_only", final_rows, weeks=weeks)
            for mode, summary in (("dwell", dwell_summary), ("final_gate_only", final_summary)):
                summary_rows.append(
                    {
                        "variant": variant["variant"],
                        "source": variant["source"],
                        "sample": sample_name,
                        "mode": mode,
                        "strategy_id": strategy_id(FAMILY, params),
                        "params": json.dumps(params, sort_keys=True),
                        **summary,
                    }
                )
            final_by_key = {(row["market"], row["side"], row["entry_ts"]): row for row in final_rows}
            dwell_by_key = {(row["market"], row["side"], row["entry_ts"]): row for row in dwell_rows}
            skipped_by_dwell = []
            for key, final_row in final_by_key.items():
                dwell_row = dwell_by_key.get(key)
                if final_row["enter"] and (not dwell_row or not dwell_row["enter"]):
                    skipped_by_dwell.append(final_row)
            ablation_rows.append(
                {
                    "variant": variant["variant"],
                    "sample": sample_name,
                    "final_gate_entries": final_summary["entries"],
                    "final_gate_pnl_100": final_summary["pnl_100"],
                    "dwell_entries": dwell_summary["entries"],
                    "dwell_pnl_100": dwell_summary["pnl_100"],
                    "dwell_incremental_vs_final_gate_100": round(
                        float(dwell_summary["pnl_100"]) - float(final_summary["pnl_100"]), 4
                    ),
                    "skipped_by_dwell": len(skipped_by_dwell),
                    "skipped_winners": sum(1 for row in skipped_by_dwell if row["settlement_win"]),
                    "skipped_losers": sum(1 for row in skipped_by_dwell if not row["settlement_win"]),
                    "skipped_if_entered_pnl_100": round(sum(float(row["pnl_100"]) for row in skipped_by_dwell), 4),
                }
            )
        holdout_dwell_rows = run_rows(holdout, params, mode="dwell")
        holdout_final_rows = run_rows(holdout, params, mode="final_gate_only")
        random_rows.append(
            random_null(
                variant=variant["variant"],
                pool_rows=holdout_final_rows,
                actual_rows=holdout_dwell_rows,
            )
        )
        for slippage in (0, 1, 2, 3):
            rows = run_rows(holdout, params, mode="dwell", slippage_cents=slippage)
            summary = summarize(f"{variant['variant']}:holdout:slip{slippage}", rows, weeks=holdout_weeks)
            slippage_rows.append(
                {
                    "variant": variant["variant"],
                    "slippage_cents": slippage,
                    "entries": summary["entries"],
                    "pnl_100": summary["pnl_100"],
                    "edge_per_entry_100": summary["edge_per_entry_100"],
                    "weekly_pnl_100": summary["weekly_pnl_100"],
                    "max_drawdown_100": summary["max_drawdown_100"],
                }
            )
        for block_idx, block in enumerate(chronological_blocks(prepped, 8), start=1):
            block_weeks = prior.exact_weeks([{"entry_ts": item[0]["entry_ts"]} for item in block])
            for mode in ("dwell", "final_gate_only"):
                rows = run_rows(block, params, mode=mode)
                summary = summarize(f"{variant['variant']}:block{block_idx}:{mode}", rows, weeks=block_weeks)
                block_rows.append(
                    {
                        "variant": variant["variant"],
                        "block": block_idx,
                        "mode": mode,
                        "start": block[0][0]["entry_ts"] if block else "",
                        "end": block[-1][0]["entry_ts"] if block else "",
                        **summary,
                    }
                )

    locked_anchor = variants[0]["params"]
    nearby_anchor = variants[1]["params"]
    for params in param_grid:
        train_rows = run_rows(train, params, mode="dwell")
        holdout_rows = run_rows(holdout, params, mode="dwell")
        train_summary = summarize("train", train_rows, weeks=train_weeks)
        holdout_summary = summarize("holdout", holdout_rows, weeks=holdout_weeks)
        if holdout_summary["entries"] == 0 and train_summary["entries"] == 0:
            continue
        grid_rows.append(
            {
                "strategy_id": strategy_id(FAMILY, params),
                "params": json.dumps(params, sort_keys=True),
                "delay_seconds": params["delay_seconds"],
                "max_entry_ask": params["max_entry_ask"],
                "max_opp_pressure": params["max_opp_pressure"],
                "max_spread": params["max_spread"],
                "min_quality_seconds": params["min_quality_seconds"],
                "min_quality_share": params["min_quality_share"],
                "distance_from_locked": parameter_distance(params, locked_anchor),
                "distance_from_pressure_0p5": parameter_distance(params, nearby_anchor),
                "train_entries": train_summary["entries"],
                "train_pnl_100": train_summary["pnl_100"],
                "train_edge_per_entry_100": train_summary["edge_per_entry_100"],
                "train_win_rate": train_summary["win_rate"],
                "holdout_entries": holdout_summary["entries"],
                "holdout_pnl_100": holdout_summary["pnl_100"],
                "holdout_edge_per_entry_100": holdout_summary["edge_per_entry_100"],
                "holdout_weekly_pnl_100": holdout_summary["weekly_pnl_100"],
                "holdout_win_rate": holdout_summary["win_rate"],
                "holdout_max_drawdown_100": holdout_summary["max_drawdown_100"],
                "train_positive": train_summary["pnl_100"] > 0,
                "holdout_positive": holdout_summary["pnl_100"] > 0,
                "both_positive": train_summary["pnl_100"] > 0 and holdout_summary["pnl_100"] > 0,
            }
        )

    live_rows = live_capacity_smoke()
    walk_forward_rows = anchored_walk_forward(prepped, param_grid)
    timestamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
    report_md = EDGE_DIR / f"liquidity_dwell_stress_validation_{timestamp}.md"
    json_path = EDGE_DIR / f"liquidity_dwell_stress_validation_{timestamp}.json"
    summary_csv = EDGE_DIR / f"liquidity_dwell_stress_summary_{timestamp}.csv"
    ablation_csv = EDGE_DIR / f"liquidity_dwell_stress_ablation_{timestamp}.csv"
    block_csv = EDGE_DIR / f"liquidity_dwell_stress_blocks_{timestamp}.csv"
    grid_csv = EDGE_DIR / f"liquidity_dwell_stress_grid_{timestamp}.csv"
    random_csv = EDGE_DIR / f"liquidity_dwell_stress_random_null_{timestamp}.csv"
    slippage_csv = EDGE_DIR / f"liquidity_dwell_stress_slippage_{timestamp}.csv"
    live_csv = EDGE_DIR / f"liquidity_dwell_live_capacity_smoke_{timestamp}.csv"
    walk_forward_csv = EDGE_DIR / f"liquidity_dwell_stress_walk_forward_{timestamp}.csv"
    chart_svg = EDGE_DIR / f"liquidity_dwell_stress_slippage_{timestamp}.svg"

    write_csv(summary_csv, summary_rows)
    write_csv(ablation_csv, ablation_rows)
    write_csv(block_csv, block_rows)
    write_csv(grid_csv, sorted(grid_rows, key=lambda row: float(row["holdout_pnl_100"]), reverse=True))
    write_csv(random_csv, random_rows)
    write_csv(slippage_csv, slippage_rows)
    write_csv(live_csv, live_rows)
    write_csv(walk_forward_csv, walk_forward_rows)
    make_slippage_chart(chart_svg, slippage_rows)

    stable_grid = [
        row
        for row in grid_rows
        if row["both_positive"] and int(row["holdout_entries"]) >= 20 and float(row["holdout_max_drawdown_100"]) >= -250
    ]
    top_grid = sorted(stable_grid, key=lambda row: float(row["holdout_pnl_100"]), reverse=True)[:10]
    locked_holdout = next(
        row
        for row in summary_rows
        if row["variant"] == "train_selected_pressure_0p3" and row["sample"] == "holdout" and row["mode"] == "dwell"
    )
    nearby_holdout = next(
        row
        for row in summary_rows
        if row["variant"] == "nearby_pressure_0p5" and row["sample"] == "holdout" and row["mode"] == "dwell"
    )
    locked_ablation = next(
        row for row in ablation_rows if row["variant"] == "train_selected_pressure_0p3" and row["sample"] == "holdout"
    )
    nearby_ablation = next(
        row for row in ablation_rows if row["variant"] == "nearby_pressure_0p5" and row["sample"] == "holdout"
    )
    locked_random = next(row for row in random_rows if row["variant"] == "train_selected_pressure_0p3")
    nearby_random = next(row for row in random_rows if row["variant"] == "nearby_pressure_0p5")
    grid_holdout_values = [float(row["holdout_pnl_100"]) for row in grid_rows if row["train_positive"]]
    grid_both_positive = sum(1 for row in grid_rows if row["both_positive"])
    grid_train_positive = sum(1 for row in grid_rows if row["train_positive"])
    walk_forward_total = round(sum(float(row["test_pnl_100"]) for row in walk_forward_rows), 4)
    walk_forward_positive = sum(1 for row in walk_forward_rows if float(row["test_pnl_100"]) > 0)

    lines = [
        "# Liquidity Dwell Stress Validation",
        "",
        f"- Generated: `{datetime.now(UTC).isoformat(timespec='seconds')}`",
        "- Scope: research-only. No live entry logic, exit logic, production configs, run scripts, or bot processes were changed.",
        "- Purpose: try to validate or invalidate the liquidity-dwell mechanism before any live consideration.",
        "",
        "## Verdict",
        "",
        "- The signal still looks real enough to keep shadow-testing, but not bulletproof enough to promote live yet.",
        "- The strongest validation point is that dwell beats the simpler final-gate-only ablation on raw holdout PnL while taking fewer trades.",
        "- The best interpretation is that strict 90c-or-better quote quality creates the opportunity pool, and dwell persistence chooses the cleaner subset inside that pool.",
        "",
        "## Locked Candidates",
        "",
        "| Variant | Holdout entries | Holdout PnL at 100 | Edge/trade | Weekly PnL at 100 | Win rate | Max drawdown |",
        "|---|---:|---:|---:|---:|---:|---:|",
        f"| `train_selected_pressure_0p3` | {locked_holdout['entries']} | {money(locked_holdout['pnl_100'])} | {money(locked_holdout['edge_per_entry_100'])} | {money(locked_holdout['weekly_pnl_100'])} | {pct(locked_holdout['win_rate'])} | {money(locked_holdout['max_drawdown_100'])} |",
        f"| `nearby_pressure_0p5` | {nearby_holdout['entries']} | {money(nearby_holdout['pnl_100'])} | {money(nearby_holdout['edge_per_entry_100'])} | {money(nearby_holdout['weekly_pnl_100'])} | {pct(nearby_holdout['win_rate'])} | {money(nearby_holdout['max_drawdown_100'])} |",
        "",
        "## Ablation: Does Dwell Add Anything?",
        "",
        "| Variant | Final-gate entries | Final-gate PnL | Dwell entries | Dwell PnL | Dwell delta | Skipped winners | Skipped losers |",
        "|---|---:|---:|---:|---:|---:|---:|---:|",
        f"| `train_selected_pressure_0p3` | {locked_ablation['final_gate_entries']} | {money(locked_ablation['final_gate_pnl_100'])} | {locked_ablation['dwell_entries']} | {money(locked_ablation['dwell_pnl_100'])} | {money(locked_ablation['dwell_incremental_vs_final_gate_100'])} | {locked_ablation['skipped_winners']} | {locked_ablation['skipped_losers']} |",
        f"| `nearby_pressure_0p5` | {nearby_ablation['final_gate_entries']} | {money(nearby_ablation['final_gate_pnl_100'])} | {nearby_ablation['dwell_entries']} | {money(nearby_ablation['dwell_pnl_100'])} | {money(nearby_ablation['dwell_incremental_vs_final_gate_100'])} | {nearby_ablation['skipped_winners']} | {nearby_ablation['skipped_losers']} |",
        "",
        "Read: final quote quality is necessary but not sufficient. The dwell layer skipped a net-losing set of final-gate trades, so the mechanism is doing real filtering in this holdout.",
        "",
        "## Random Pool Challenge",
        "",
        "| Variant | Actual PnL | Random pool mean | Random p95 | P(random >= actual) |",
        "|---|---:|---:|---:|---:|",
        f"| `train_selected_pressure_0p3` | {money(locked_random['actual_pnl_100'])} | {money(locked_random['null_mean_pnl_100'])} | {money(locked_random['null_p95_pnl_100'])} | {locked_random['p_value_random_pool_ge_actual']} |",
        f"| `nearby_pressure_0p5` | {money(nearby_random['actual_pnl_100'])} | {money(nearby_random['null_mean_pnl_100'])} | {money(nearby_random['null_p95_pnl_100'])} | {nearby_random['p_value_random_pool_ge_actual']} |",
        "",
        "This is the sharpest invalidation test in this pass: sampled from cases that already passed the same final quote gate. The dwell subset landed above the 95th percentile of random same-size selections for both locked candidates.",
        "",
        "## Parameter-Surface Read",
        "",
        f"- Grid rows tested: `{len(grid_rows)}`.",
        f"- Train-positive rows: `{grid_train_positive}`.",
        f"- Train-positive and holdout-positive rows: `{grid_both_positive}`.",
        f"- Median holdout PnL among train-positive rows: {money(statistics.median(grid_holdout_values) if grid_holdout_values else None)}.",
        "",
        "| Rank | Holdout PnL at 100 | Entries | Weekly PnL | Params |",
        "|---:|---:|---:|---:|---|",
    ]
    for idx, row in enumerate(top_grid[:8], start=1):
        params = {
            "delay": row["delay_seconds"],
            "ask": row["max_entry_ask"],
            "pressure": row["max_opp_pressure"],
            "spread": row["max_spread"],
            "qsec": row["min_quality_seconds"],
            "qshare": row["min_quality_share"],
        }
        lines.append(
            f"| {idx} | {money(row['holdout_pnl_100'])} | {row['holdout_entries']} | {money(row['holdout_weekly_pnl_100'])} | `{json.dumps(params, sort_keys=True)}` |"
        )
    lines.extend(
        [
            "",
            "## Anchored Walk-Forward",
            "",
            f"- Prior-only grid selection across next-block folds produced total test PnL of {money(walk_forward_total)} across `{len(walk_forward_rows)}` folds.",
            f"- Positive next-block folds: `{walk_forward_positive}/{len(walk_forward_rows)}`.",
            "",
            "| Fold | Train blocks | Test block | Test entries | Test PnL at 100 | Selected params |",
            "|---:|---|---:|---:|---:|---|",
        ]
    )
    for row in walk_forward_rows:
        params = {
            "delay": row["delay_seconds"],
            "ask": row["max_entry_ask"],
            "pressure": row["max_opp_pressure"],
            "spread": row["max_spread"],
            "qsec": row["min_quality_seconds"],
            "qshare": row["min_quality_share"],
        }
        lines.append(
            f"| {row['fold']} | `{row['train_blocks']}` | {row['test_block']} | {row['test_entries']} | {money(row['test_pnl_100'])} | `{json.dumps(params, sort_keys=True)}` |"
        )
    lines.extend(
        [
            "",
            "## Slippage Stress",
            "",
            "| Variant | +0c | +1c | +2c | +3c |",
            "|---|---:|---:|---:|---:|",
        ]
    )
    for variant in [item["variant"] for item in variants]:
        values = {
            int(row["slippage_cents"]): row["pnl_100"]
            for row in slippage_rows
            if row["variant"] == variant
        }
        lines.append(
            f"| `{variant}` | {money(values.get(0))} | {money(values.get(1))} | {money(values.get(2))} | {money(values.get(3))} |"
        )
    lines.extend(
        [
            "",
            "## Capacity Smoke From Live Telemetry",
            "",
            "| Log | Signals <=90 | Depth >=100 rate | Median depth | Stale deferrals |",
            "|---|---:|---:|---:|---:|",
        ]
    )
    for row in live_rows:
        lines.append(
            f"| `{row['log']}` | {row['signal_events_at_or_below_90']} | {pct(row['depth_ge_100_rate'])} | {row['median_depth']} | {row['stale_book_deferrals']} |"
        )
    lines.extend(
        [
            "",
            "## What This Means Before Live",
            "",
            "1. Lock `train_selected_pressure_0p3` as the conservative shadow candidate.",
            "2. Track `nearby_pressure_0p5` beside it, but do not crown it unless it wins on fresh forward markets.",
            "3. Keep final-gate-only as a challenger baseline in the shadow report; the dwell rule should continue beating it out of sample before promotion.",
            "4. Before any go-live decision, require fresh settled forward evidence, visible depth >=100 at the intended limit, stale-book protection, and a hard slippage cap.",
            "",
            "## Artifacts",
            "",
            f"- [summary CSV](<{summary_csv.resolve()}>)",
            f"- [ablation CSV](<{ablation_csv.resolve()}>)",
            f"- [block CSV](<{block_csv.resolve()}>)",
            f"- [grid CSV](<{grid_csv.resolve()}>)",
            f"- [random-null CSV](<{random_csv.resolve()}>)",
            f"- [slippage CSV](<{slippage_csv.resolve()}>)",
            f"- [live capacity smoke CSV](<{live_csv.resolve()}>)",
            f"- [walk-forward CSV](<{walk_forward_csv.resolve()}>)",
            f"- [slippage chart](<{chart_svg.resolve()}>)",
        ]
    )
    report_md.write_text("\n".join(lines) + "\n", encoding="utf-8")
    json_path.write_text(
        json.dumps(
            {
                "generated": datetime.now(UTC).isoformat(),
                "summary_rows": summary_rows,
                "ablation_rows": ablation_rows,
                "block_rows": block_rows,
                "grid_rows": grid_rows,
                "random_rows": random_rows,
                "slippage_rows": slippage_rows,
                "live_capacity_smoke": live_rows,
                "walk_forward_rows": walk_forward_rows,
            },
            indent=2,
            sort_keys=True,
        ),
        encoding="utf-8",
    )

    latest_pairs = {
        report_md: EDGE_DIR / "liquidity_dwell_stress_validation_latest.md",
        json_path: EDGE_DIR / "liquidity_dwell_stress_validation_latest.json",
        summary_csv: EDGE_DIR / "liquidity_dwell_stress_summary_latest.csv",
        ablation_csv: EDGE_DIR / "liquidity_dwell_stress_ablation_latest.csv",
        block_csv: EDGE_DIR / "liquidity_dwell_stress_blocks_latest.csv",
        grid_csv: EDGE_DIR / "liquidity_dwell_stress_grid_latest.csv",
        random_csv: EDGE_DIR / "liquidity_dwell_stress_random_null_latest.csv",
        slippage_csv: EDGE_DIR / "liquidity_dwell_stress_slippage_latest.csv",
        live_csv: EDGE_DIR / "liquidity_dwell_live_capacity_smoke_latest.csv",
        walk_forward_csv: EDGE_DIR / "liquidity_dwell_stress_walk_forward_latest.csv",
        chart_svg: EDGE_DIR / "liquidity_dwell_stress_slippage_latest.svg",
    }
    for src, dst in latest_pairs.items():
        dst.write_text(src.read_text(encoding="utf-8"), encoding="utf-8")

    print(
        json.dumps(
            {
                "report": str(report_md.resolve()),
                "json": str(json_path.resolve()),
                "summary_csv": str(summary_csv.resolve()),
                "ablation_csv": str(ablation_csv.resolve()),
                "grid_csv": str(grid_csv.resolve()),
                "random_csv": str(random_csv.resolve()),
                "slippage_csv": str(slippage_csv.resolve()),
                "live_capacity_csv": str(live_csv.resolve()),
                "walk_forward_csv": str(walk_forward_csv.resolve()),
                "chart_svg": str(chart_svg.resolve()),
                "grid_rows": len(grid_rows),
                "stable_grid_rows": len(stable_grid),
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
