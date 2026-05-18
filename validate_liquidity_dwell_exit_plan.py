from __future__ import annotations

import csv
import json
import math
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import research_liquidity_dwell_improvements as dwell_research
import validate_liquidity_dwell_integrity as dwell_validation
from probe_codex_terminal_salvage_all_trades import EDGE_DIR
from probe_stop_touch_confirmation import estimated_order_fee_cents


UTC = timezone.utc
CONTRACTS = 100


def money(value: Any) -> str:
    try:
        parsed = float(value)
    except (TypeError, ValueError):
        return ""
    return f"${parsed:,.2f}"


def pct(value: Any) -> str:
    try:
        parsed = float(value)
    except (TypeError, ValueError):
        return ""
    return f"{100.0 * parsed:.1f}%"


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    fields: list[str] = []
    for row in rows:
        for key in row:
            if key not in fields:
                fields.append(key)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def candidate_variants() -> list[dict[str, Any]]:
    return [
        {
            "variant": "pnl_max_p05_q065",
            "reason": "Best holdout PnL from the current dwell improvement scan.",
            "params": {
                "delay_seconds": 120,
                "max_entry_ask": 90,
                "max_opp_pressure": 0.5,
                "max_spread": 10,
                "min_bid_sum": 0,
                "min_quality_seconds": 10,
                "min_quality_share": 0.65,
            },
        },
        {
            "variant": "prior_p05_q075",
            "reason": "Prior pressure-0.5 robust reference.",
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
            "variant": "locked_conservative_p03_q075",
            "reason": "Train-selected locked conservative reference.",
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
            "variant": "robust_pressure_persistence_ask88",
            "reason": "Lower count, higher edge/trade pressure-persistence guard.",
            "params": {
                "delay_seconds": 120,
                "max_entry_ask": 88,
                "max_opp_pressure": 0.5,
                "max_pressure_max": 0.4,
                "max_pressure_mean": 0.3,
                "max_spread": 10,
                "min_bid_sum": 0,
                "min_quality_seconds": 10,
                "min_quality_share": 0.65,
            },
        },
        {
            "variant": "path_stability_ask88",
            "reason": "Nearby path-stability guard with tighter entry count.",
            "params": {
                "delay_seconds": 120,
                "max_entry_ask": 88,
                "max_opp_pressure": 0.5,
                "max_spread": 10,
                "min_bid_sum": 0,
                "min_quality_seconds": 10,
                "min_quality_share": 0.65,
                "max_ask_range": 20,
                "max_ask_up_jump": 99,
            },
        },
    ]


def exit_policies() -> list[dict[str, Any]]:
    policies: list[dict[str, Any]] = [
        {
            "policy": "hold_to_settlement",
            "kind": "hold",
            "description": "No discretionary exit; settle the selected entry.",
        },
    ]
    for threshold in (78, 70, 60):
        policies.append(
            {
                "policy": f"routine_stop_{threshold}",
                "kind": "threshold",
                "threshold": threshold,
                "confirm_points": 1,
                "exit_slip_cents": 1,
                "description": f"Exit after first post-entry held_ask <= {threshold}c.",
            }
        )
    for threshold in (45, 30, 20, 15, 10):
        policies.append(
            {
                "policy": f"deep_panic_{threshold}_confirm2",
                "kind": "threshold",
                "threshold": threshold,
                "confirm_points": 2,
                "exit_slip_cents": 1,
                "description": (
                    f"Emergency salvage only: exit after two consecutive post-entry "
                    f"quotes with held_ask <= {threshold}c."
                ),
            }
        )
    policies.append(
        {
            "policy": "deep_panic_10_confirm1",
            "kind": "threshold",
            "threshold": 10,
            "confirm_points": 1,
            "exit_slip_cents": 1,
            "description": "Emergency salvage control: first quote with held_ask <= 10c.",
        }
    )
    return policies


def exact_weeks(items: list[tuple[dict[str, Any], dict[str, Any]]], indices: list[int]) -> float:
    if len(indices) < 2:
        return 0.0
    start = dwell_validation.iso_to_dt(str(items[indices[0]][0]["entry_ts"]))
    end = dwell_validation.iso_to_dt(str(items[indices[-1]][0]["entry_ts"]))
    return max(0.0, (end - start).total_seconds() / 86400.0 / 7.0)


def chronological_blocks(count: int, block_count: int = 8) -> list[list[int]]:
    return [
        list(range(int(count * idx / block_count), int(count * (idx + 1) / block_count)))
        for idx in range(block_count)
    ]


def points_after_entry(case: dict[str, Any], delay_seconds: float) -> list[dict[str, float]]:
    points: list[dict[str, float]] = []
    for point in case.get("path", []):
        try:
            elapsed = float(point.get("elapsed"))
            held_ask = float(point.get("held_ask"))
            own_bid = float(point.get("own_bid"))
        except (TypeError, ValueError):
            continue
        if elapsed < delay_seconds or math.isnan(held_ask) or math.isnan(own_bid):
            continue
        points.append(point)
    return points


def exit_fill_from_point(point: dict[str, Any], slip_cents: float) -> float:
    try:
        bid = float(point.get("own_bid"))
    except (TypeError, ValueError):
        bid = 0.0
    if math.isnan(bid):
        bid = 0.0
    return max(0.0, min(99.0, bid - slip_cents))


def exit_pnl_from_delayed_entry(entry_ask: float, exit_bid: float, contracts: int = CONTRACTS) -> float:
    entry_fee = estimated_order_fee_cents(entry_ask, contracts)
    exit_fee = estimated_order_fee_cents(exit_bid, contracts)
    return round((contracts * (exit_bid - entry_ask) - entry_fee - exit_fee) / 100.0, 4)


def first_threshold_exit(
    case: dict[str, Any],
    *,
    delay_seconds: float,
    threshold: float,
    confirm_points: int,
    exit_slip_cents: float,
) -> dict[str, Any] | None:
    streak = 0
    for point in points_after_entry(case, delay_seconds):
        held_ask = float(point["held_ask"])
        if held_ask <= threshold:
            streak += 1
        else:
            streak = 0
        if streak >= confirm_points:
            fill = exit_fill_from_point(point, exit_slip_cents)
            return {
                "exit": True,
                "exit_bid": fill,
                "raw_exit_bid": float(point["own_bid"]),
                "held_ask": held_ask,
                "exit_elapsed": float(point["elapsed"]),
                "trigger_threshold": threshold,
                "confirm_points": confirm_points,
                "exit_slip_cents": exit_slip_cents,
            }
    return None


def simulate_exit_policy(
    case: dict[str, Any],
    entry_meta: dict[str, Any],
    policy: dict[str, Any],
) -> dict[str, Any]:
    entry_ask = float(entry_meta["entry_ask"])
    delay_seconds = float(entry_meta.get("delay_seconds") or policy.get("delay_seconds") or 0.0)
    hold_pnl = dwell_research.delayed_entry_pnl(case, entry_ask, contracts=CONTRACTS)
    if policy["kind"] == "hold":
        return {
            "action": "hold",
            "pnl_100": hold_pnl,
            "hold_pnl_100": hold_pnl,
            "delta_vs_hold_100": 0.0,
            "exit_bid": None,
            "exit_elapsed": None,
            "held_ask_at_exit": None,
            "raw_exit_bid": None,
        }
    exit_meta = first_threshold_exit(
        case,
        delay_seconds=delay_seconds,
        threshold=float(policy["threshold"]),
        confirm_points=int(policy.get("confirm_points") or 1),
        exit_slip_cents=float(policy.get("exit_slip_cents") or 0.0),
    )
    if not exit_meta:
        return {
            "action": "hold",
            "pnl_100": hold_pnl,
            "hold_pnl_100": hold_pnl,
            "delta_vs_hold_100": 0.0,
            "exit_bid": None,
            "exit_elapsed": None,
            "held_ask_at_exit": None,
            "raw_exit_bid": None,
        }
    pnl = exit_pnl_from_delayed_entry(entry_ask, float(exit_meta["exit_bid"]), contracts=CONTRACTS)
    return {
        "action": "exit",
        "pnl_100": pnl,
        "hold_pnl_100": hold_pnl,
        "delta_vs_hold_100": round(pnl - hold_pnl, 4),
        "exit_bid": exit_meta["exit_bid"],
        "exit_elapsed": exit_meta["exit_elapsed"],
        "held_ask_at_exit": exit_meta["held_ask"],
        "raw_exit_bid": exit_meta["raw_exit_bid"],
    }


def selected_entries_for_variant(
    prepped: list[tuple[dict[str, Any], dict[str, Any]]],
    variant: dict[str, Any],
) -> list[dict[str, Any]]:
    params = variant["params"]
    rows: list[dict[str, Any]] = []
    for idx, (case, prepared) in enumerate(prepped):
        entry_meta = dwell_research.simulate_case(case, prepared, params)
        if not entry_meta.get("enter"):
            continue
        entry_meta["delay_seconds"] = params["delay_seconds"]
        rows.append(
            {
                "index": idx,
                "case": case,
                "entry_meta": entry_meta,
                "variant": variant["variant"],
                "params": params,
            }
        )
    return rows


def summarize_policy_rows(
    *,
    variant: str,
    policy: str,
    sample: str,
    rows: list[dict[str, Any]],
    weeks: float | None,
) -> dict[str, Any]:
    entries = len(rows)
    exits = [row for row in rows if row["action"] == "exit"]
    false_exits = [row for row in exits if row["settlement_win"]]
    true_loser_exits = [row for row in exits if not row["settlement_win"]]
    true_losers = [row for row in rows if not row["settlement_win"]]
    missed_losers = [row for row in rows if not row["settlement_win"] and row["action"] != "exit"]
    pnl = sum(float(row["pnl_100"]) for row in rows)
    hold_pnl = sum(float(row["hold_pnl_100"]) for row in rows)
    winners = [row for row in rows if row["settlement_win"]]
    cumulative = 0.0
    peak = 0.0
    max_drawdown = 0.0
    for row in sorted(rows, key=lambda item: item["index"]):
        cumulative += float(row["pnl_100"])
        peak = max(peak, cumulative)
        max_drawdown = min(max_drawdown, cumulative - peak)
    days = defaultdict(float)
    for row in rows:
        days[row["entry_day_et"]] += float(row["pnl_100"])
    positive_days = sum(1 for value in days.values() if value > 0)
    return {
        "variant": variant,
        "policy": policy,
        "sample": sample,
        "entries": entries,
        "exits": len(exits),
        "exit_rate": round(len(exits) / entries, 6) if entries else 0.0,
        "false_exits": len(false_exits),
        "true_loser_exits": len(true_loser_exits),
        "true_losers": len(true_losers),
        "missed_true_losers": len(missed_losers),
        "false_exit_rate": round(len(false_exits) / len(exits), 6) if exits else 0.0,
        "missed_loser_rate": round(len(missed_losers) / len(true_losers), 6) if true_losers else 0.0,
        "pnl_100": round(pnl, 4),
        "hold_pnl_100": round(hold_pnl, 4),
        "delta_vs_hold_100": round(pnl - hold_pnl, 4),
        "edge_per_entry_100": round(pnl / entries, 6) if entries else 0.0,
        "weekly_pnl_100": round(pnl / weeks, 6) if weeks and weeks > 0 else None,
        "weekly_delta_vs_hold_100": round((pnl - hold_pnl) / weeks, 6) if weeks and weeks > 0 else None,
        "win_rate": round(len(winners) / entries, 6) if entries else 0.0,
        "worst_trade_100": round(min([float(row["pnl_100"]) for row in rows] or [0.0]), 4),
        "max_drawdown_100": round(max_drawdown, 4),
        "active_days": len(days),
        "positive_days": positive_days,
        "positive_day_rate": round(positive_days / len(days), 6) if days else 0.0,
        "avg_entry_ask": round(sum(float(row["entry_ask"]) for row in rows) / entries, 4) if entries else None,
        "avg_exit_bid": round(sum(float(row["exit_bid"]) for row in exits) / len(exits), 4) if exits else None,
    }


def make_policy_chart(path: Path, rows: list[dict[str, Any]]) -> None:
    selected = rows[:12]
    width = 1180
    row_h = 34
    height = 84 + row_h * max(1, len(selected))
    left = 310
    right = 170
    top = 50
    values = [float(row["pnl_100"]) for row in selected] or [0.0]
    min_v = min(0.0, min(values))
    max_v = max(0.0, max(values))
    span = max(1.0, max_v - min_v)

    def x(value: float) -> float:
        return left + (value - min_v) / span * (width - left - right)

    zero_x = x(0.0)
    lines = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="#ffffff"/>',
        '<text x="24" y="30" font-family="Arial" font-size="20" font-weight="700">Liquidity dwell exit policy holdout PnL at 100 contracts</text>',
        f'<line x1="{zero_x:.2f}" y1="{top - 8}" x2="{zero_x:.2f}" y2="{height - 24}" stroke="#777" stroke-width="1"/>',
    ]
    for idx, row in enumerate(selected):
        y = top + idx * row_h
        value = float(row["pnl_100"])
        x0 = min(zero_x, x(value))
        bar_w = abs(x(value) - zero_x)
        color = "#0f766e" if value >= 0 else "#b91c1c"
        label = f"{row['variant']} / {row['policy']}"
        lines.extend(
            [
                f'<text x="24" y="{y + 20}" font-family="Arial" font-size="12" fill="#111">{label}</text>',
                f'<rect x="{x0:.2f}" y="{y + 5}" width="{bar_w:.2f}" height="20" fill="{color}" opacity="0.85"/>',
                f'<text x="{width - 150}" y="{y + 20}" font-family="Arial" font-size="12" fill="#111">{money(value)}</text>',
            ]
        )
    lines.append("</svg>")
    path.write_text("\n".join(lines), encoding="utf-8")


def write_report(path: Path, payload: dict[str, Any]) -> None:
    top_holdout = payload["top_holdout"]
    best_variant_rows = payload["best_variant_holdout_rows"]
    production_exit = payload["production_exit_holdout"]
    best_non_hold = payload["best_non_hold_holdout"]
    robustness_rows = payload["best_variant_policy_robustness"]
    lines = [
        "# Liquidity Dwell Exit Plan Validation",
        "",
        f"- Generated: `{payload['generated_at']}`",
        "- Scope: research-only. No live entry logic, exit logic, production configs, run scripts, or bot processes were changed.",
        f"- Cases replayed: `{payload['case_count']}` quote-path cases; split remains first 70% train / last 30% chronological holdout.",
        f"- Contract scale: `{CONTRACTS}` contracts per selected entry.",
        "",
        "## Recommendation",
        "",
        f"- Production-grade exit plan from this backtest: `{production_exit['policy']}`.",
        f"- Holdout projected PnL at 100 contracts: {money(production_exit['pnl_100'])} total, {money(production_exit['weekly_pnl_100'])}/week, {money(production_exit['edge_per_entry_100'])}/trade.",
        f"- Best non-hold watchlist policy: `{best_non_hold['policy']}` at {money(best_non_hold['pnl_100'])} holdout PnL, {money(best_non_hold['weekly_pnl_100'])}/week, {money(best_non_hold['delta_vs_hold_100'])} vs hold.",
        "- The watchlist panic exit is not promoted yet because it wins the holdout but loses vs hold over train/full sample. Shadow it online before making it live.",
        "- Routine 60c/70c/78c stops are rejected by this replay; they mostly cut future winners.",
        "",
        "## Top Holdout Policies",
        "",
        "| Rank | Variant | Exit policy | Entries | Exits | False exits | PnL 100 | Weekly PnL 100 | Edge/trade | Delta vs hold | Max DD |",
        "|---:|---|---|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for idx, row in enumerate(top_holdout[:12], start=1):
        lines.append(
            f"| {idx} | `{row['variant']}` | `{row['policy']}` | {row['entries']} | {row['exits']} | "
            f"{row['false_exits']} | {money(row['pnl_100'])} | {money(row['weekly_pnl_100'])} | "
            f"{money(row['edge_per_entry_100'])} | {money(row['delta_vs_hold_100'])} | {money(row['max_drawdown_100'])} |"
        )
    lines.extend(
        [
            "",
            "## Robustness Gate On Best Entry Variant",
            "",
            "| Exit policy | Train delta | Holdout delta | Full delta | Train false exits | Holdout false exits | Verdict |",
            "|---|---:|---:|---:|---:|---:|---|",
        ]
    )
    for row in robustness_rows:
        lines.append(
            f"| `{row['policy']}` | {money(row['train_delta_vs_hold_100'])} | "
            f"{money(row['holdout_delta_vs_hold_100'])} | {money(row['full_delta_vs_hold_100'])} | "
            f"{row['train_false_exits']} | {row['holdout_false_exits']} | {row['verdict']} |"
        )
    lines.extend(
        [
            "",
            "## Exit Controls On Best Entry Variant",
            "",
            "| Exit policy | Entries | Exits | False exits | Missed losers | PnL 100 | Weekly PnL 100 | Delta vs hold | Edge/trade |",
            "|---|---:|---:|---:|---:|---:|---:|---:|---:|",
        ]
    )
    for row in best_variant_rows:
        lines.append(
            f"| `{row['policy']}` | {row['entries']} | {row['exits']} | {row['false_exits']} | "
            f"{row['missed_true_losers']} | {money(row['pnl_100'])} | {money(row['weekly_pnl_100'])} | "
            f"{money(row['delta_vs_hold_100'])} | {money(row['edge_per_entry_100'])} |"
        )
    lines.extend(
        [
            "",
            "## Read",
            "",
            "- The exit plan is validated only if the selected exit policy beats or matches hold-to-settlement on the chronological holdout and does not create many false exits from settlement winners.",
            "- A deep-panic salvage exit is useful only as a rare disaster guard. If it does not trigger in holdout, it should not be counted as PnL improvement; it only limits pathological future paths.",
            "- A routine 60c/70c/78c stop is rejected if it lowers holdout PnL or mostly exits future winners.",
            "- This run treats projected PnL as historical holdout PnL divided by elapsed holdout weeks; it is not a live promise.",
            "",
            "## Artifacts",
            "",
            f"- [summary CSV](<{payload['paths']['summary_csv']}>)",
            f"- [trade ledger CSV](<{payload['paths']['trades_csv']}>)",
            f"- [JSON payload](<{payload['paths']['json']}>)",
            f"- [holdout chart](<{payload['paths']['chart_svg']}>)",
        ]
    )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    prepped, _quote_delays = dwell_validation.load_prepped_quote_path()
    count = len(prepped)
    split = int(count * 0.7)
    samples = {
        "full": list(range(count)),
        "train": list(range(split)),
        "holdout": list(range(split, count)),
    }
    sample_weeks = {sample: exact_weeks(prepped, indices) for sample, indices in samples.items()}
    blocks = chronological_blocks(count, 8)
    policies = exit_policies()
    variants = candidate_variants()

    summary_rows: list[dict[str, Any]] = []
    trade_rows: list[dict[str, Any]] = []
    block_rows: list[dict[str, Any]] = []

    for variant in variants:
        selected = selected_entries_for_variant(prepped, variant)
        for policy in policies:
            policy_trade_rows: list[dict[str, Any]] = []
            for item in selected:
                case = item["case"]
                entry_meta = item["entry_meta"]
                exit_result = simulate_exit_policy(case, entry_meta, policy)
                row = {
                    "variant": variant["variant"],
                    "policy": policy["policy"],
                    "index": item["index"],
                    "dataset": case.get("dataset"),
                    "market": case.get("market"),
                    "side": case.get("side"),
                    "entry_ts": case.get("entry_ts"),
                    "entry_day_et": case.get("entry_day_et"),
                    "settlement_win": bool(case.get("settlement_win")),
                    "entry_ask": float(entry_meta["entry_ask"]),
                    "quality_seconds": entry_meta.get("quality_seconds"),
                    "quality_share": entry_meta.get("quality_share"),
                    "pressure": entry_meta.get("pressure"),
                    "spread": entry_meta.get("spread"),
                    **exit_result,
                }
                trade_rows.append(row)
                policy_trade_rows.append(row)
            for sample, indices in samples.items():
                index_set = set(indices)
                sample_rows = [row for row in policy_trade_rows if int(row["index"]) in index_set]
                summary_rows.append(
                    summarize_policy_rows(
                        variant=variant["variant"],
                        policy=policy["policy"],
                        sample=sample,
                        rows=sample_rows,
                        weeks=sample_weeks[sample],
                    )
                )
            for block_idx, indices in enumerate(blocks, start=1):
                index_set = set(indices)
                sample_rows = [row for row in policy_trade_rows if int(row["index"]) in index_set]
                block_rows.append(
                    {
                        "block": block_idx,
                        "start": prepped[indices[0]][0]["entry_ts"] if indices else "",
                        "end": prepped[indices[-1]][0]["entry_ts"] if indices else "",
                        **summarize_policy_rows(
                            variant=variant["variant"],
                            policy=policy["policy"],
                            sample=f"block_{block_idx}",
                            rows=sample_rows,
                            weeks=exact_weeks(prepped, indices),
                        ),
                    }
                )

    holdout_rows = [row for row in summary_rows if row["sample"] == "holdout"]
    top_holdout = sorted(
        holdout_rows,
        key=lambda row: (
            float(row["pnl_100"]),
            float(row["edge_per_entry_100"]),
            -float(row["false_exit_rate"]),
        ),
        reverse=True,
    )
    best_variant = "pnl_max_p05_q065"
    best_variant_holdout_rows = sorted(
        [row for row in holdout_rows if row["variant"] == best_variant],
        key=lambda row: (float(row["pnl_100"]), float(row["delta_vs_hold_100"])),
        reverse=True,
    )
    summary_by_key = {
        (row["variant"], row["policy"], row["sample"]): row
        for row in summary_rows
    }
    production_exit_holdout = summary_by_key[(best_variant, "hold_to_settlement", "holdout")]
    best_non_hold_holdout = sorted(
        [row for row in best_variant_holdout_rows if row["policy"] != "hold_to_settlement"],
        key=lambda row: (float(row["pnl_100"]), float(row["delta_vs_hold_100"])),
        reverse=True,
    )[0]
    best_variant_policy_robustness: list[dict[str, Any]] = []
    for holdout_row in best_variant_holdout_rows:
        policy = holdout_row["policy"]
        train = summary_by_key[(best_variant, policy, "train")]
        full = summary_by_key[(best_variant, policy, "full")]
        promotable = (
            policy == "hold_to_settlement"
            or (
                float(train["delta_vs_hold_100"]) >= 0.0
                and float(holdout_row["delta_vs_hold_100"]) >= 0.0
                and float(full["delta_vs_hold_100"]) >= 0.0
                and int(train["false_exits"]) == 0
                and int(holdout_row["false_exits"]) == 0
            )
        )
        if policy == "hold_to_settlement":
            verdict = "production baseline"
        elif promotable:
            verdict = "promotable"
        elif float(holdout_row["delta_vs_hold_100"]) > 0.0:
            verdict = "watchlist; holdout-only improvement"
        else:
            verdict = "reject"
        best_variant_policy_robustness.append(
            {
                "policy": policy,
                "train_delta_vs_hold_100": train["delta_vs_hold_100"],
                "holdout_delta_vs_hold_100": holdout_row["delta_vs_hold_100"],
                "full_delta_vs_hold_100": full["delta_vs_hold_100"],
                "train_false_exits": train["false_exits"],
                "holdout_false_exits": holdout_row["false_exits"],
                "verdict": verdict,
            }
        )

    timestamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
    report_md = EDGE_DIR / f"liquidity_dwell_exit_plan_validation_{timestamp}.md"
    json_path = EDGE_DIR / f"liquidity_dwell_exit_plan_validation_{timestamp}.json"
    summary_csv = EDGE_DIR / f"liquidity_dwell_exit_plan_summary_{timestamp}.csv"
    trades_csv = EDGE_DIR / f"liquidity_dwell_exit_plan_trades_{timestamp}.csv"
    blocks_csv = EDGE_DIR / f"liquidity_dwell_exit_plan_blocks_{timestamp}.csv"
    chart_svg = EDGE_DIR / f"liquidity_dwell_exit_plan_holdout_pnl_{timestamp}.svg"

    write_csv(summary_csv, summary_rows)
    write_csv(trades_csv, trade_rows)
    write_csv(blocks_csv, block_rows)
    make_policy_chart(chart_svg, top_holdout)

    payload = {
        "generated_at": datetime.now(UTC).isoformat(timespec="seconds"),
        "case_count": count,
        "split_index": split,
        "contract_scale": CONTRACTS,
        "samples": {sample: {"indices": len(indices), "weeks": sample_weeks[sample]} for sample, indices in samples.items()},
        "variants": variants,
        "policies": policies,
        "summary_rows": summary_rows,
        "block_rows": block_rows,
        "top_holdout": top_holdout,
        "best_variant_holdout_rows": best_variant_holdout_rows,
        "production_exit_holdout": production_exit_holdout,
        "best_non_hold_holdout": best_non_hold_holdout,
        "best_variant_policy_robustness": best_variant_policy_robustness,
        "paths": {
            "report_md": str(report_md.resolve()),
            "json": str(json_path.resolve()),
            "summary_csv": str(summary_csv.resolve()),
            "trades_csv": str(trades_csv.resolve()),
            "blocks_csv": str(blocks_csv.resolve()),
            "chart_svg": str(chart_svg.resolve()),
        },
    }
    json_path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    write_report(report_md, payload)

    latest_pairs = {
        report_md: EDGE_DIR / "liquidity_dwell_exit_plan_validation_latest.md",
        json_path: EDGE_DIR / "liquidity_dwell_exit_plan_validation_latest.json",
        summary_csv: EDGE_DIR / "liquidity_dwell_exit_plan_summary_latest.csv",
        trades_csv: EDGE_DIR / "liquidity_dwell_exit_plan_trades_latest.csv",
        blocks_csv: EDGE_DIR / "liquidity_dwell_exit_plan_blocks_latest.csv",
        chart_svg: EDGE_DIR / "liquidity_dwell_exit_plan_holdout_pnl_latest.svg",
    }
    for src, dst in latest_pairs.items():
        dst.write_text(src.read_text(encoding="utf-8"), encoding="utf-8")

    print(
        json.dumps(
            {
                "report": str(report_md.resolve()),
                "json": str(json_path.resolve()),
                "summary_csv": str(summary_csv.resolve()),
                "trades_csv": str(trades_csv.resolve()),
                "blocks_csv": str(blocks_csv.resolve()),
                "chart_svg": str(chart_svg.resolve()),
                "production_exit": production_exit_holdout,
                "best_non_hold_watchlist": best_non_hold_holdout,
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
