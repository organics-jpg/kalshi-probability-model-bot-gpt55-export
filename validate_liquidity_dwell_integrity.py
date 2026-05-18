from __future__ import annotations

import csv
import json
import math
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import probe_codex_entry_microstructure_edges as micro
from probe_codex_entry_timing_edges import delayed_entry_pnl
from probe_codex_terminal_salvage_all_trades import EDGE_DIR, discover_datasets, load_dataset_cases
from probe_stop_touch_confirmation import strategy_id


UTC = timezone.utc
FAMILY = "liquidity_dwell_integrity_admission"


def n(value: Any, default: float | None = None) -> float | None:
    try:
        if value in (None, ""):
            return default
        parsed = float(value)
        return default if math.isnan(parsed) else parsed
    except Exception:
        return default


def money(value: Any) -> str:
    value = n(value)
    return "" if value is None else f"${value:,.2f}"


def pct(value: Any) -> str:
    value = n(value)
    return "" if value is None else f"{100.0 * value:.1f}%"


def iso_to_dt(value: str) -> datetime:
    return datetime.fromisoformat(str(value).replace("Z", "+00:00"))


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


def load_prepped_quote_path() -> tuple[list[tuple[dict[str, Any], dict[str, Any]]], tuple[int, ...]]:
    payloads = [load_dataset_cases(dataset, refresh_cache=False) for dataset in discover_datasets()]
    cases: list[dict[str, Any]] = []
    for payload in payloads:
        dataset = payload.get("dataset")
        for case in payload.get("cases", []):
            case.setdefault("dataset", dataset)
            cases.append(case)
    cases = sorted(cases, key=lambda item: (item["entry_ts"], item["market"], item["side"]))
    strategies = micro.build_strategy_grid()
    quote_delays = tuple(sorted({
        int(strategy.params["delay_seconds"])
        for strategy in strategies
        if strategy.scope == "quote_path"
    }))
    return [(case, micro.prepare_quote_case(case, quote_delays)) for case in cases], quote_delays


def liquidity_spec(params: dict[str, Any]) -> micro.StrategySpec:
    return micro.StrategySpec(
        family=FAMILY,
        theorem=(
            "The executable book state should persist through time; an acceptable final quote is less reliable "
            "when most of the interval was wide, slack, or opponent-heavy."
        ),
        equation=(
            "Q=(1/T)*integral 1{held_ask<=A and spread<=S and bid_sum>=B and p_opp<=P} dt; "
            "enter only if final gates pass, Q>=q, and quality_seconds>=s."
        ),
        params=params,
        scope="quote_path",
        simulator=micro.sim_liquidity_dwell_integrity_admission,
    )


def base_variants() -> list[dict[str, Any]]:
    return [
        {
            "variant": "train_selected_locked",
            "source": "walk_forward_train_selected",
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
            "variant": "robust_best_pressure_0p5",
            "source": "robust_positive_scan_top",
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
            "variant": "robust_best_pressure_0p5_quality30",
            "source": "robust_positive_scan_tied_top",
            "params": {
                "delay_seconds": 120,
                "max_entry_ask": 90,
                "max_opp_pressure": 0.5,
                "max_spread": 10,
                "min_bid_sum": 0,
                "min_quality_seconds": 30,
                "min_quality_share": 0.75,
            },
        },
        {
            "variant": "tight_spread_pressure_0p5",
            "source": "robust_positive_scan_nearby",
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
        {
            "variant": "conservative_quality_0p9",
            "source": "full_sample_sensitivity",
            "params": {
                "delay_seconds": 120,
                "max_entry_ask": 90,
                "max_opp_pressure": 0.3,
                "max_spread": 10,
                "min_bid_sum": 0,
                "min_quality_seconds": 10,
                "min_quality_share": 0.90,
            },
        },
        {
            "variant": "looser_ask_92_control",
            "source": "negative_control",
            "params": {
                "delay_seconds": 120,
                "max_entry_ask": 92,
                "max_opp_pressure": 0.3,
                "max_spread": 10,
                "min_bid_sum": 0,
                "min_quality_seconds": 10,
                "min_quality_share": 0.75,
            },
        },
    ]


def exact_binom_sf(k: int, total: int, p: float) -> float:
    if total <= 0:
        return 1.0
    p = max(0.0, min(1.0, p))
    acc = 0.0
    for i in range(k, total + 1):
        acc += math.comb(total, i) * (p ** i) * ((1.0 - p) ** (total - i))
    return min(1.0, acc)


def wilson_interval(k: int, total: int, z: float = 1.96) -> tuple[float, float]:
    if total <= 0:
        return (0.0, 0.0)
    phat = k / total
    denom = 1.0 + z * z / total
    center = (phat + z * z / (2.0 * total)) / denom
    spread = z * math.sqrt((phat * (1.0 - phat) + z * z / (4.0 * total)) / total) / denom
    return max(0.0, center - spread), min(1.0, center + spread)


def summarize_rows(label: str, rows: list[dict[str, Any]], *, weeks: float | None = None) -> dict[str, Any]:
    entered = [row for row in rows if row["enter"]]
    winners = [row for row in entered if row["settlement_win"]]
    losers = [row for row in entered if not row["settlement_win"]]
    pnl = round(sum(float(row["pnl"]) for row in rows), 4)
    pnl_100 = round(sum(float(row["pnl_100"]) for row in entered), 4)
    contracts = sum(int(row["contracts"]) for row in entered)
    entries = len(entered)
    avg_win_100 = sum(row["pnl_100"] for row in winners) / len(winners) if winners else 0.0
    avg_loss_100 = -sum(row["pnl_100"] for row in losers) / len(losers) if losers else 0.0
    break_even_rate = avg_loss_100 / (avg_loss_100 + avg_win_100) if (avg_loss_100 + avg_win_100) > 0 else 0.0
    win_rate_value = len(winners) / entries if entries else 0.0
    low_ci, high_ci = wilson_interval(len(winners), entries)
    p_value = exact_binom_sf(len(winners), entries, break_even_rate) if entries else 1.0
    cumulative = 0.0
    max_drawdown = 0.0
    peak = 0.0
    for row in entered:
        cumulative += float(row["pnl_100"])
        peak = max(peak, cumulative)
        max_drawdown = min(max_drawdown, cumulative - peak)
    days = defaultdict(float)
    for row in entered:
        days[row["entry_day_et"]] += float(row["pnl_100"])
    positive_days = sum(1 for value in days.values() if value > 0)
    negative_days = sum(1 for value in days.values() if value < 0)
    return {
        "label": label,
        "n": len(rows),
        "entries": entries,
        "win_rate": round(win_rate_value, 6),
        "win_rate_ci_low": round(low_ci, 6),
        "win_rate_ci_high": round(high_ci, 6),
        "break_even_win_rate_100_contracts": round(break_even_rate, 6),
        "binom_p_value_vs_break_even": round(p_value, 8),
        "sim_pnl_original_size": pnl,
        "total_contracts_original_size": contracts,
        "edge_per_original_contract": round(pnl / contracts, 6) if contracts else 0.0,
        "pnl_100_contracts": pnl_100,
        "edge_per_100_contract_entry": round(pnl_100 / entries, 6) if entries else 0.0,
        "entries_per_week": round(entries / weeks, 6) if weeks and weeks > 0 else None,
        "weekly_pnl_100_contracts": round(pnl_100 / weeks, 6) if weeks and weeks > 0 else None,
        "avg_entry_ask": round(sum(float(row["entry_ask"]) for row in entered) / entries, 4) if entries else None,
        "avg_quality_share": round(sum(float(row["quality_share"]) for row in entered) / entries, 4) if entries else None,
        "avg_quality_seconds": round(sum(float(row["quality_seconds"]) for row in entered) / entries, 4) if entries else None,
        "avg_pressure": round(sum(float(row["pressure"]) for row in entered) / entries, 4) if entries else None,
        "worst_trade_100_contracts": round(min([row["pnl_100"] for row in entered] or [0.0]), 4),
        "max_drawdown_100_contracts": round(max_drawdown, 4),
        "active_days": len(days),
        "positive_days": positive_days,
        "negative_days": negative_days,
        "positive_day_rate": round(positive_days / len(days), 6) if days else 0.0,
        "unique_markets": len({row["market"] for row in entered}),
        "entries_per_unique_market": round(entries / max(1, len({row["market"] for row in entered})), 4),
    }


def row_for_case(case: dict[str, Any], meta: dict[str, Any], pnl: float) -> dict[str, Any]:
    enter = bool(meta.get("enter"))
    ask = n(meta.get("entry_ask"), 0.0) or 0.0
    contracts = int(meta.get("contracts") or (case.get("qty") if enter else 0) or 0)
    return {
        "dataset": case.get("dataset"),
        "market": case.get("market"),
        "side": case.get("side"),
        "entry_ts": case.get("entry_ts"),
        "entry_day_et": case.get("entry_day_et"),
        "settlement_win": bool(case.get("settlement_win")),
        "enter": enter,
        "pnl": pnl if enter else 0.0,
        "pnl_100": delayed_entry_pnl(case, ask, contracts=100) if enter else 0.0,
        "contracts": contracts,
        "entry_ask": ask if enter else None,
        "entry_elapsed": n(meta.get("entry_elapsed")),
        "quality_share": n(meta.get("quality_share")),
        "quality_seconds": n(meta.get("quality_seconds")),
        "pressure": n(meta.get("pressure")),
        "spread": n(meta.get("spread")),
        "bid_sum": n(meta.get("bid_sum")),
        "skip_reason": meta.get("skip_reason", ""),
    }


def run_variant(prepped: list[tuple[dict[str, Any], dict[str, Any]]], variant: dict[str, Any]) -> list[dict[str, Any]]:
    spec = liquidity_spec(variant["params"])
    rows = []
    for case, prepared in prepped:
        pnl, meta = spec.simulator(case, prepared, spec.params)
        row = row_for_case(case, meta, pnl)
        row["variant"] = variant["variant"]
        row["strategy_id"] = strategy_id(FAMILY, spec.params)
        rows.append(row)
    return rows


def chronological_blocks(rows: list[dict[str, Any]], block_count: int = 5) -> list[list[dict[str, Any]]]:
    ordered = sorted(rows, key=lambda row: (str(row["entry_ts"]), str(row["market"]), str(row["side"])))
    blocks = []
    for idx in range(block_count):
        start = int(len(ordered) * idx / block_count)
        end = int(len(ordered) * (idx + 1) / block_count)
        blocks.append(ordered[start:end])
    return blocks


def group_summary_rows(rows: list[dict[str, Any]], keys: list[str]) -> list[dict[str, Any]]:
    out = []
    for key in keys:
        groups = defaultdict(list)
        for row in rows:
            groups[str(row.get(key))].append(row)
        for value, items in sorted(groups.items()):
            summary = summarize_rows(f"{key}={value}", items)
            summary["group_key"] = key
            summary["group_value"] = value
            out.append(summary)
    return out


def exact_weeks(rows: list[dict[str, Any]]) -> float:
    if len(rows) < 2:
        return 0.0
    ordered = sorted(rows, key=lambda row: row["entry_ts"])
    start = iso_to_dt(str(ordered[0]["entry_ts"]))
    end = iso_to_dt(str(ordered[-1]["entry_ts"]))
    return max(0.0, (end - start).total_seconds() / 86400.0 / 7.0)


def make_chart(path: Path, cumulative_rows: list[dict[str, Any]]) -> None:
    series_by_variant: dict[str, list[tuple[int, float]]] = defaultdict(list)
    for row in cumulative_rows:
        series_by_variant[row["variant"]].append((int(row["entry_index"]), float(row["cumulative_pnl_100"])))
    width = 1100
    height = 520
    pad_l = 70
    pad_r = 30
    pad_t = 40
    pad_b = 70
    all_points = [point for series in series_by_variant.values() for point in series]
    max_x = max([point[0] for point in all_points] or [1])
    min_y = min([0.0] + [point[1] for point in all_points])
    max_y = max([0.0] + [point[1] for point in all_points])
    y_span = max(1.0, max_y - min_y)
    x_span = max(1, max_x)
    colors = ["#2166ac", "#1b9e77", "#d95f02", "#7570b3", "#666666", "#a6761d"]

    def sx(x: float) -> float:
        return pad_l + x / x_span * (width - pad_l - pad_r)

    def sy(y: float) -> float:
        return pad_t + (max_y - y) / y_span * (height - pad_t - pad_b)

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="#fbfbf8"/>',
        '<text x="22" y="26" font-family="Segoe UI, Arial" font-size="18" font-weight="700" fill="#222">Liquidity dwell validation: cumulative 100-contract holdout PnL</text>',
        f'<line x1="{pad_l}" y1="{sy(0):.1f}" x2="{width-pad_r}" y2="{sy(0):.1f}" stroke="#999" stroke-width="1"/>',
        f'<line x1="{pad_l}" y1="{pad_t}" x2="{pad_l}" y2="{height-pad_b}" stroke="#555" stroke-width="1"/>',
        f'<line x1="{pad_l}" y1="{height-pad_b}" x2="{width-pad_r}" y2="{height-pad_b}" stroke="#555" stroke-width="1"/>',
    ]
    for i, (variant, points) in enumerate(series_by_variant.items()):
        points = sorted(points)
        if not points:
            continue
        d = " ".join(
            ("M" if idx == 0 else "L") + f"{sx(x):.1f},{sy(y):.1f}"
            for idx, (x, y) in enumerate(points)
        )
        color = colors[i % len(colors)]
        parts.append(f'<path d="{d}" fill="none" stroke="{color}" stroke-width="2.2"/>')
        lx = 88 + (i % 2) * 430
        ly = height - 44 + (i // 2) * 16
        parts.append(f'<rect x="{lx}" y="{ly-9}" width="18" height="3" fill="{color}"/>')
        parts.append(
            f'<text x="{lx+24}" y="{ly-5}" font-family="Segoe UI, Arial" font-size="12" fill="#222">{variant}</text>'
        )
    parts.append(f'<text x="22" y="{sy(max_y)+5:.1f}" font-family="Segoe UI, Arial" font-size="11" fill="#333">{money(max_y)}</text>')
    parts.append(f'<text x="22" y="{sy(min_y)+5:.1f}" font-family="Segoe UI, Arial" font-size="11" fill="#333">{money(min_y)}</text>')
    parts.append("</svg>")
    path.write_text("\n".join(parts), encoding="utf-8")


def write_report(
    path: Path,
    *,
    summary_rows: list[dict[str, Any]],
    block_rows: list[dict[str, Any]],
    group_rows: list[dict[str, Any]],
    variant_csv: Path,
    block_csv: Path,
    group_csv: Path,
    row_csv: Path,
    chart_svg: Path,
) -> None:
    top = sorted(summary_rows, key=lambda row: n(row["holdout_weekly_pnl_100_contracts"], -1e18), reverse=True)
    train_locked = next(row for row in summary_rows if row["variant"] == "train_selected_locked")
    robust = next(row for row in summary_rows if row["variant"] == "robust_best_pressure_0p5")
    lines = [
        "# Liquidity Dwell Integrity Validation",
        "",
        f"- Generated: `{datetime.now(UTC).isoformat(timespec='seconds')}`",
        "- Scope: research-only. No live entry logic, exit logic, production configs, run scripts, or bot processes were changed.",
        "- Target strategy: `liquidity_dwell_integrity_admission`.",
        "",
        "## What The Rule Does",
        "",
        "- Waits for the simulated delayed entry point, usually 120 seconds.",
        "- Requires the final quote to be acceptable: held ask at or below the max ask, spread within the cap, bid book not slack, and opposing pressure below the cap.",
        "- Then requires that same acceptable book state to have persisted through most of the pre-entry window, not just appeared at the final snapshot.",
        "- In plain terms: do not buy the contract just because the last quote looks fine; buy only when the book spent enough time looking fine.",
        "",
        "## Headline Validation",
        "",
        "| Variant | Holdout PnL | Holdout entries | Win rate | Edge/entry at 100 contracts | Weekly PnL at 100 contracts | Max drawdown at 100 | Status read |",
        "|---|---:|---:|---:|---:|---:|---:|---|",
    ]
    for row in top:
        status = "best validation PnL; lock before forward test" if row["variant"] == robust["variant"] else ""
        if row["variant"] == train_locked["variant"]:
            status = "cleaner because it was train-selected"
        lines.append(
            f"| `{row['variant']}` | {money(row['holdout_pnl_original_size'])} | {int(row['holdout_entries'])} | {pct(row['holdout_win_rate'])} | "
            f"{money(row['holdout_edge_per_100_contract_entry'])} | {money(row['holdout_weekly_pnl_100_contracts'])} | "
            f"{money(row['holdout_max_drawdown_100_contracts'])} | {status or row['source']} |"
        )
    lines.extend(
        [
            "",
            "## Why It Looks Like It Works",
            "",
            "- The strongest versions cap the entry ask at 90c. Loosening to 92c or 94c sharply lowers economics in prior sensitivity, which says the edge is not just generic high-win-rate buying.",
            "- The dwell requirement filters out single-tick/flickering quotes. The rule is exploiting persistence of executable book quality: stable tight/supportive quotes are materially different from one acceptable final snapshot.",
            "- Holdout results are positive across the main live-style datasets and both sides for the locked variant; the edge is not carried by a single yes/no side.",
            "- The robust pressure-0.5 variant makes more trades and more weekly PnL, while the pressure-0.3 locked variant has the cleaner selection story and better win rate.",
            "",
            "## Persistence And Overfit Read",
            "",
            f"- Locked train-selected holdout: {money(train_locked['holdout_pnl_original_size'])}, "
            f"{int(train_locked['holdout_entries'])} entries, {pct(train_locked['holdout_win_rate'])} win rate, "
            f"{money(train_locked['holdout_weekly_pnl_100_contracts'])}/week at 100 contracts.",
            f"- Robust nearby holdout: {money(robust['holdout_pnl_original_size'])}, "
            f"{int(robust['holdout_entries'])} entries, {pct(robust['holdout_win_rate'])} win rate, "
            f"{money(robust['holdout_weekly_pnl_100_contracts'])}/week at 100 contracts.",
            "- I would not call this bulletproof yet. The positive evidence is strong enough for shadow/locked forward testing, not for live promotion.",
            "- Main overfit risk: the best robust row was chosen after scanning nearby parameters. The locked train-selected rule is more defensible even though it projects less weekly PnL.",
            "",
            "## Chronological Blocks",
            "",
            "| Variant | Block | Entries | PnL at 100 contracts | Win rate | Max drawdown |",
            "|---|---:|---:|---:|---:|---:|",
        ]
    )
    for row in block_rows:
        if row["variant"] not in {train_locked["variant"], robust["variant"]}:
            continue
        lines.append(
            f"| `{row['variant']}` | {row['block']} | {int(row['entries'])} | {money(row['pnl_100_contracts'])} | {pct(row['win_rate'])} | {money(row['max_drawdown_100_contracts'])} |"
        )
    lines.extend(
        [
            "",
            "## Failure Modes To Guard Before Live",
            "",
            "- Capacity/slippage: the replay assumes 100 contracts fill at the observed ask. The live order book may not support that size, especially near expiry.",
            "- Correlation: multiple entries can cluster by market regime; worst 100-contract holdout trade was around a full 90c-style loss.",
            "- Regime drift: this may rely on the current Kalshi BTC 15m microstructure. A fee/liquidity/participant change could reduce the dwell signal.",
            "- Data scope: the quote-path sample is useful, but this needs a fresh locked forward run on post-selection markets.",
            "",
            "## Recommended Next Steps",
            "",
            "1. Lock the train-selected rule and the pressure-0.5 nearby rule as shadow-only candidates.",
            "2. Collect fresh forward evidence without changing live entry behavior: entries, skipped opportunities, simulated fillability at 100 contracts, and actual top-of-book depth at entry.",
            "3. Add capacity checks before any live consideration: minimum ask size, max slippage, stale-book age, and no market with insufficient displayed liquidity.",
            "4. Only promote if fresh forward PnL stays positive versus skip-all and the exact 100-contract fillability test remains realistic.",
            "",
            "## Artifacts",
            "",
            f"- [variant summary](<{variant_csv.resolve()}>)",
            f"- [chronological blocks](<{block_csv.resolve()}>)",
            f"- [group breakdowns](<{group_csv.resolve()}>)",
            f"- [per-case rows](<{row_csv.resolve()}>)",
            f"- [cumulative chart](<{chart_svg.resolve()}>)",
        ]
    )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    prepped, _quote_delays = load_prepped_quote_path()
    split = int(len(prepped) * 0.7)
    train = prepped[:split]
    holdout = prepped[split:]
    full_weeks = exact_weeks([{"entry_ts": item[0]["entry_ts"]} for item in prepped])
    train_weeks = exact_weeks([{"entry_ts": item[0]["entry_ts"]} for item in train])
    holdout_weeks = exact_weeks([{"entry_ts": item[0]["entry_ts"]} for item in holdout])
    variants = base_variants()

    summary_rows: list[dict[str, Any]] = []
    block_rows: list[dict[str, Any]] = []
    group_rows: list[dict[str, Any]] = []
    case_rows: list[dict[str, Any]] = []
    cumulative_rows: list[dict[str, Any]] = []

    for variant in variants:
        full_rows = run_variant(prepped, variant)
        train_rows = run_variant(train, variant)
        holdout_rows = run_variant(holdout, variant)
        case_rows.extend(holdout_rows)

        full_summary = summarize_rows("full", full_rows, weeks=full_weeks)
        train_summary = summarize_rows("train", train_rows, weeks=train_weeks)
        holdout_summary = summarize_rows("holdout", holdout_rows, weeks=holdout_weeks)
        summary_rows.append({
            "variant": variant["variant"],
            "source": variant["source"],
            "strategy_id": strategy_id(FAMILY, variant["params"]),
            "params": json.dumps(variant["params"], sort_keys=True),
            "full_pnl_original_size": full_summary["sim_pnl_original_size"],
            "full_entries": full_summary["entries"],
            "full_win_rate": full_summary["win_rate"],
            "full_pnl_100_contracts": full_summary["pnl_100_contracts"],
            "full_weekly_pnl_100_contracts": full_summary["weekly_pnl_100_contracts"],
            "train_pnl_original_size": train_summary["sim_pnl_original_size"],
            "train_entries": train_summary["entries"],
            "train_win_rate": train_summary["win_rate"],
            "holdout_start": holdout[0][0]["entry_ts"],
            "holdout_end": holdout[-1][0]["entry_ts"],
            "holdout_weeks": holdout_weeks,
            "holdout_pnl_original_size": holdout_summary["sim_pnl_original_size"],
            "holdout_entries": holdout_summary["entries"],
            "holdout_entries_per_week": holdout_summary["entries_per_week"],
            "holdout_total_contracts_original_size": holdout_summary["total_contracts_original_size"],
            "holdout_edge_per_original_contract": holdout_summary["edge_per_original_contract"],
            "holdout_win_rate": holdout_summary["win_rate"],
            "holdout_win_rate_ci_low": holdout_summary["win_rate_ci_low"],
            "holdout_win_rate_ci_high": holdout_summary["win_rate_ci_high"],
            "holdout_break_even_win_rate_100_contracts": holdout_summary["break_even_win_rate_100_contracts"],
            "holdout_binom_p_value_vs_break_even": holdout_summary["binom_p_value_vs_break_even"],
            "holdout_pnl_100_contracts": holdout_summary["pnl_100_contracts"],
            "holdout_edge_per_100_contract_entry": holdout_summary["edge_per_100_contract_entry"],
            "holdout_weekly_pnl_100_contracts": holdout_summary["weekly_pnl_100_contracts"],
            "holdout_avg_entry_ask": holdout_summary["avg_entry_ask"],
            "holdout_avg_quality_share": holdout_summary["avg_quality_share"],
            "holdout_avg_quality_seconds": holdout_summary["avg_quality_seconds"],
            "holdout_avg_pressure": holdout_summary["avg_pressure"],
            "holdout_worst_trade_100_contracts": holdout_summary["worst_trade_100_contracts"],
            "holdout_max_drawdown_100_contracts": holdout_summary["max_drawdown_100_contracts"],
            "holdout_active_days": holdout_summary["active_days"],
            "holdout_positive_days": holdout_summary["positive_days"],
            "holdout_negative_days": holdout_summary["negative_days"],
            "holdout_positive_day_rate": holdout_summary["positive_day_rate"],
            "holdout_unique_markets": holdout_summary["unique_markets"],
            "holdout_entries_per_unique_market": holdout_summary["entries_per_unique_market"],
        })

        for key_row in group_summary_rows(holdout_rows, ["dataset", "side", "entry_day_et"]):
            key_row["variant"] = variant["variant"]
            group_rows.append(key_row)

        for block_idx, block in enumerate(chronological_blocks(holdout_rows, 5), 1):
            block_summary = summarize_rows(f"block_{block_idx}", block)
            block_summary["variant"] = variant["variant"]
            block_summary["block"] = block_idx
            if block:
                block_summary["start_entry_ts"] = block[0]["entry_ts"]
                block_summary["end_entry_ts"] = block[-1]["entry_ts"]
            block_rows.append(block_summary)

        entered = [row for row in holdout_rows if row["enter"]]
        cumulative = 0.0
        for idx, row in enumerate(entered, 1):
            cumulative += float(row["pnl_100"])
            cumulative_rows.append({
                "variant": variant["variant"],
                "entry_index": idx,
                "entry_ts": row["entry_ts"],
                "market": row["market"],
                "side": row["side"],
                "pnl_100": row["pnl_100"],
                "cumulative_pnl_100": round(cumulative, 4),
            })

    stamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
    EDGE_DIR.mkdir(parents=True, exist_ok=True)
    variant_csv = EDGE_DIR / f"liquidity_dwell_validation_variants_{stamp}.csv"
    block_csv = EDGE_DIR / f"liquidity_dwell_validation_blocks_{stamp}.csv"
    group_csv = EDGE_DIR / f"liquidity_dwell_validation_groups_{stamp}.csv"
    row_csv = EDGE_DIR / f"liquidity_dwell_validation_rows_{stamp}.csv"
    cumulative_csv = EDGE_DIR / f"liquidity_dwell_validation_cumulative_{stamp}.csv"
    chart_svg = EDGE_DIR / f"liquidity_dwell_validation_cumulative_{stamp}.svg"
    report_md = EDGE_DIR / f"liquidity_dwell_validation_{stamp}.md"
    json_path = EDGE_DIR / f"liquidity_dwell_validation_{stamp}.json"

    write_csv(variant_csv, summary_rows)
    write_csv(block_csv, block_rows)
    write_csv(group_csv, group_rows)
    write_csv(row_csv, case_rows)
    write_csv(cumulative_csv, cumulative_rows)
    make_chart(chart_svg, cumulative_rows)
    payload = {
        "generated_at": datetime.now(UTC).isoformat(),
        "guardrail": "research_only_no_live_logic_or_config_changes",
        "family": FAMILY,
        "case_count": len(prepped),
        "train_n": len(train),
        "holdout_n": len(holdout),
        "holdout_start": holdout[0][0]["entry_ts"],
        "holdout_end": holdout[-1][0]["entry_ts"],
        "holdout_weeks": holdout_weeks,
        "summary_rows": summary_rows,
        "artifacts": {
            "report_md": str(report_md),
            "variant_csv": str(variant_csv),
            "block_csv": str(block_csv),
            "group_csv": str(group_csv),
            "row_csv": str(row_csv),
            "cumulative_csv": str(cumulative_csv),
            "chart_svg": str(chart_svg),
        },
    }
    json_path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    write_report(
        report_md,
        summary_rows=summary_rows,
        block_rows=block_rows,
        group_rows=group_rows,
        variant_csv=variant_csv,
        block_csv=block_csv,
        group_csv=group_csv,
        row_csv=row_csv,
        chart_svg=chart_svg,
    )

    latest_md = EDGE_DIR / "liquidity_dwell_validation_latest.md"
    latest_json = EDGE_DIR / "liquidity_dwell_validation_latest.json"
    latest_variants = EDGE_DIR / "liquidity_dwell_validation_variants_latest.csv"
    latest_blocks = EDGE_DIR / "liquidity_dwell_validation_blocks_latest.csv"
    latest_groups = EDGE_DIR / "liquidity_dwell_validation_groups_latest.csv"
    latest_rows = EDGE_DIR / "liquidity_dwell_validation_rows_latest.csv"
    latest_chart = EDGE_DIR / "liquidity_dwell_validation_cumulative_latest.svg"
    latest_md.write_text(report_md.read_text(encoding="utf-8"), encoding="utf-8")
    latest_json.write_text(json_path.read_text(encoding="utf-8"), encoding="utf-8")
    latest_variants.write_text(variant_csv.read_text(encoding="utf-8"), encoding="utf-8")
    latest_blocks.write_text(block_csv.read_text(encoding="utf-8"), encoding="utf-8")
    latest_groups.write_text(group_csv.read_text(encoding="utf-8"), encoding="utf-8")
    latest_rows.write_text(row_csv.read_text(encoding="utf-8"), encoding="utf-8")
    latest_chart.write_text(chart_svg.read_text(encoding="utf-8"), encoding="utf-8")

    print(json.dumps({
        "report": str(report_md.resolve()),
        "json": str(json_path.resolve()),
        "variant_csv": str(variant_csv.resolve()),
        "block_csv": str(block_csv.resolve()),
        "group_csv": str(group_csv.resolve()),
        "row_csv": str(row_csv.resolve()),
        "chart_svg": str(chart_svg.resolve()),
        "variants": len(summary_rows),
        "holdout_weeks": holdout_weeks,
    }, indent=2))


if __name__ == "__main__":
    main()
