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
import research_liquidity_dwell_improvements as improve
import validate_liquidity_dwell_integrity as prior
from probe_codex_entry_timing_edges import delayed_entry_pnl
from probe_codex_terminal_salvage_all_trades import EDGE_DIR


UTC = timezone.utc
RANDOM_SEED = 24042477


def n(value: Any, default: float | None = None) -> float | None:
    try:
        if value in (None, ""):
            return default
        parsed = float(value)
        return default if math.isnan(parsed) else parsed
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


def percentile(values: list[float], q: float) -> float | None:
    if not values:
        return None
    ordered = sorted(values)
    idx = min(len(ordered) - 1, max(0, int(round(q * (len(ordered) - 1)))))
    return round(ordered[idx], 4)


def wilson(k: int, total: int, z: float = 1.96) -> tuple[float, float]:
    if total <= 0:
        return 0.0, 0.0
    phat = k / total
    denom = 1.0 + z * z / total
    center = (phat + z * z / (2.0 * total)) / denom
    spread = z * math.sqrt((phat * (1.0 - phat) + z * z / (4.0 * total)) / total) / denom
    return max(0.0, center - spread), min(1.0, center + spread)


def variant_specs() -> list[dict[str, Any]]:
    return [
        {
            "variant": "locked_conservative_p03_q075",
            "hypothesis": "Cleanest train-selected dwell baseline.",
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
            "variant": "pnl_max_p05_q065",
            "hypothesis": "Best simple holdout PnL from improvement grid.",
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
            "hypothesis": "Prior pressure-0.5 reference before qshare relaxation.",
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
            "variant": "robust_pressure_persistence_ask88",
            "hypothesis": "Lower-PnL, higher-edge robustness candidate from pressure-persistence family.",
            "params": {
                "delay_seconds": 120,
                "max_entry_ask": 88,
                "max_opp_pressure": 0.5,
                "max_spread": 10,
                "min_bid_sum": 0,
                "min_quality_seconds": 10,
                "min_quality_share": 0.65,
                "max_pressure_mean": 0.3,
                "max_pressure_max": 0.6,
            },
        },
        {
            "variant": "path_stability_ask88",
            "hypothesis": "Walk-forward-positive path-stability challenger.",
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


def case_row(
    case: dict[str, Any],
    outcome: dict[str, Any],
    *,
    idx: int,
    variant: str,
    mode: str,
) -> dict[str, Any]:
    entry_dt = prior.iso_to_dt(str(case["entry_ts"]))
    return {
        "variant": variant,
        "mode": mode,
        "case_index": idx,
        "dataset": case.get("dataset"),
        "market": case.get("market"),
        "side": case.get("side"),
        "entry_ts": case.get("entry_ts"),
        "entry_day_et": case.get("entry_day_et"),
        "entry_hour_utc": entry_dt.hour,
        "settlement_win": bool(case.get("settlement_win")),
        "enter": bool(outcome.get("enter")),
        "pnl_100": float(outcome.get("pnl_100") or 0.0),
        "entry_ask": n(outcome.get("entry_ask")),
        "quality_share": n(outcome.get("quality_share")),
        "quality_seconds": n(outcome.get("quality_seconds")),
        "pressure": n(outcome.get("pressure")),
        "spread": n(outcome.get("spread")),
        "bid_sum": n(outcome.get("bid_sum")),
        "own_bid_net": n(outcome.get("own_bid_net")),
        "own_bid_omega": n(outcome.get("own_bid_omega")),
        "ask_range": n(outcome.get("ask_range")),
        "pressure_mean": n(outcome.get("pressure_mean")),
        "skip_reason": outcome.get("skip_reason", ""),
    }


def final_gate_outcome(case: dict[str, Any], prepared: dict[str, Any], params: dict[str, Any]) -> dict[str, Any]:
    snapshot = prepared.get(str(int(params["delay_seconds"])))
    if not snapshot or not micro.quote_gate(snapshot, params):
        return {"enter": False, "pnl_100": 0.0, "skip_reason": "missing_or_gate_failed"}
    ask = float(snapshot["held_ask"])
    return {
        "enter": True,
        "pnl_100": delayed_entry_pnl(case, ask, contracts=100),
        "settlement_win": bool(case.get("settlement_win")),
        "entry_ask": ask,
        "pressure": round(float(snapshot["pressure"]), 6),
        "spread": round(float(snapshot["spread"]), 4),
        "bid_sum": round(float(snapshot["bid_sum"]), 4),
    }


def summarize_rows(label: str, rows: list[dict[str, Any]]) -> dict[str, Any]:
    entered = [row for row in rows if row["enter"]]
    entries = len(entered)
    pnl = round(sum(float(row["pnl_100"]) for row in entered), 4)
    wins = sum(1 for row in entered if row["settlement_win"])
    losses = entries - wins
    low, high = wilson(wins, entries)
    cumulative = 0.0
    peak = 0.0
    max_drawdown = 0.0
    longest_loss_run = 0
    current_loss_run = 0
    for row in sorted(entered, key=lambda item: (str(item["entry_ts"]), str(item["market"]), str(item["side"]))):
        cumulative += float(row["pnl_100"])
        peak = max(peak, cumulative)
        max_drawdown = min(max_drawdown, cumulative - peak)
        if row["settlement_win"]:
            current_loss_run = 0
        else:
            current_loss_run += 1
            longest_loss_run = max(longest_loss_run, current_loss_run)
    days = defaultdict(float)
    for row in entered:
        days[str(row["entry_day_et"])] += float(row["pnl_100"])
    asks = [float(row["entry_ask"]) for row in entered if row.get("entry_ask") is not None]
    return {
        "label": label,
        "entries": entries,
        "wins": wins,
        "losses": losses,
        "win_rate": round(wins / entries, 6) if entries else 0.0,
        "win_rate_ci_low": round(low, 6),
        "win_rate_ci_high": round(high, 6),
        "pnl_100": pnl,
        "edge_per_entry_100": round(pnl / entries, 6) if entries else 0.0,
        "max_drawdown_100": round(max_drawdown, 4),
        "worst_trade_100": round(min([float(row["pnl_100"]) for row in entered] or [0.0]), 4),
        "longest_loss_run": longest_loss_run,
        "active_days": len(days),
        "positive_days": sum(1 for value in days.values() if value > 0),
        "negative_days": sum(1 for value in days.values() if value < 0),
        "avg_entry_ask": round(sum(asks) / len(asks), 4) if asks else None,
        "unique_markets": len({row["market"] for row in entered}),
    }


def grouped_summaries(rows: list[dict[str, Any]], keys: list[str]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for key in keys:
        groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
        for row in rows:
            groups[str(row.get(key))].append(row)
        for value, items in sorted(groups.items()):
            summary = summarize_rows(f"{key}={value}", items)
            summary["group_key"] = key
            summary["group_value"] = value
            out.append(summary)
    return out


def chronological_block_rows(rows: list[dict[str, Any]], blocks: int) -> list[dict[str, Any]]:
    ordered = sorted(rows, key=lambda item: (str(item["entry_ts"]), str(item["market"]), str(item["side"])))
    out: list[dict[str, Any]] = []
    for block in range(blocks):
        start = int(len(ordered) * block / blocks)
        end = int(len(ordered) * (block + 1) / blocks)
        items = ordered[start:end]
        summary = summarize_rows(f"block_{block + 1}", items)
        summary["block"] = block + 1
        summary["start"] = items[0]["entry_ts"] if items else ""
        summary["end"] = items[-1]["entry_ts"] if items else ""
        out.append(summary)
    return out


def bootstrap_pnl(rows: list[dict[str, Any]], reps: int = 10000, *, cluster_key: str | None = None) -> dict[str, Any]:
    entered = [row for row in rows if row["enter"]]
    actual = round(sum(float(row["pnl_100"]) for row in entered), 4)
    if not entered:
        return {
            "entries": 0,
            "actual_pnl_100": actual,
            "mean_pnl_100": None,
            "p05_pnl_100": None,
            "p50_pnl_100": None,
            "p95_pnl_100": None,
            "prob_positive": None,
        }
    rng = random.Random(RANDOM_SEED + len(entered) + (17 if cluster_key else 0))
    values: list[float] = []
    if cluster_key is None:
        pnls = [float(row["pnl_100"]) for row in entered]
        for _ in range(reps):
            values.append(sum(rng.choice(pnls) for _ in range(len(pnls))))
    else:
        clusters: dict[str, float] = defaultdict(float)
        for row in entered:
            clusters[str(row.get(cluster_key))] += float(row["pnl_100"])
        cluster_values = list(clusters.values())
        for _ in range(reps):
            values.append(sum(rng.choice(cluster_values) for _ in range(len(cluster_values))))
    return {
        "entries": len(entered),
        "actual_pnl_100": actual,
        "mean_pnl_100": round(statistics.mean(values), 4),
        "p05_pnl_100": percentile(values, 0.05),
        "p50_pnl_100": percentile(values, 0.50),
        "p95_pnl_100": percentile(values, 0.95),
        "prob_positive": round(sum(1 for value in values if value > 0) / len(values), 6),
    }


def final_gate_rejection(rows: list[dict[str, Any]], final_rows: list[dict[str, Any]]) -> dict[str, Any]:
    dwell_keys = {(row["case_index"], row["variant"]) for row in rows if row["enter"]}
    rejected = [
        row
        for row in final_rows
        if row["enter"] and (row["case_index"], row["variant"]) not in dwell_keys
    ]
    winners = sum(1 for row in rejected if row["settlement_win"])
    losers = sum(1 for row in rejected if not row["settlement_win"])
    pnl = round(sum(float(row["pnl_100"]) for row in rejected), 4)
    return {
        "final_gate_rejected_entries": len(rejected),
        "rejected_winners": winners,
        "rejected_losers": losers,
        "rejected_if_entered_pnl_100": pnl,
        "rejected_edge_per_entry_100": round(pnl / len(rejected), 6) if rejected else 0.0,
    }


def slippage_curve(
    items: list[tuple[dict[str, Any], dict[str, Any]]],
    params: dict[str, Any],
    indices: list[int],
    variant: str,
) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for slip in range(0, 11):
        total = 0.0
        entries = 0
        for idx in indices:
            case, prepared = items[idx]
            outcome = improve.simulate_case(case, prepared, params)
            if not outcome.get("enter"):
                continue
            entries += 1
            ask = float(outcome["entry_ask"]) + slip
            total += delayed_entry_pnl(case, ask, contracts=100)
        out.append(
            {
                "variant": variant,
                "slippage_cents": slip,
                "entries": entries,
                "pnl_100": round(total, 4),
                "edge_per_entry_100": round(total / entries, 6) if entries else 0.0,
            }
        )
    return out


def size_curve(
    items: list[tuple[dict[str, Any], dict[str, Any]]],
    params: dict[str, Any],
    indices: list[int],
    variant: str,
) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for contracts in (2, 10, 25, 50, 75, 100, 150, 200):
        total = 0.0
        entries = 0
        for idx in indices:
            case, prepared = items[idx]
            outcome = improve.simulate_case(case, prepared, params)
            if not outcome.get("enter"):
                continue
            entries += 1
            total += delayed_entry_pnl(case, float(outcome["entry_ask"]), contracts=contracts)
        out.append(
            {
                "variant": variant,
                "contracts": contracts,
                "entries": entries,
                "pnl": round(total, 4),
                "weekly_projection": None,
                "edge_per_entry": round(total / entries, 6) if entries else 0.0,
            }
        )
    return out


def overlap_matrix(rows_by_variant: dict[str, list[dict[str, Any]]]) -> list[dict[str, Any]]:
    entered_sets = {
        variant: {row["case_index"] for row in rows if row["enter"]}
        for variant, rows in rows_by_variant.items()
    }
    out: list[dict[str, Any]] = []
    for left, left_set in entered_sets.items():
        for right, right_set in entered_sets.items():
            union = left_set | right_set
            intersection = left_set & right_set
            out.append(
                {
                    "left": left,
                    "right": right,
                    "left_entries": len(left_set),
                    "right_entries": len(right_set),
                    "overlap": len(intersection),
                    "jaccard": round(len(intersection) / len(union), 6) if union else 0.0,
                    "left_unique": len(left_set - right_set),
                    "right_unique": len(right_set - left_set),
                }
            )
    return out


def make_block_chart(path: Path, rows: list[dict[str, Any]]) -> None:
    variants = list(dict.fromkeys(row["variant"] for row in rows))
    blocks = sorted({int(row["block"]) for row in rows})
    width = 1120
    height = 470
    pad_l = 70
    pad_t = 45
    pad_b = 65
    pad_r = 30
    values = [float(row["pnl_100"]) for row in rows]
    min_y = min([0.0] + values)
    max_y = max([0.0] + values)
    span = max(1.0, max_y - min_y)
    colors = ["#2166ac", "#1b9e77", "#d95f02", "#7570b3", "#666666"]

    def sx(block: int) -> float:
        return pad_l + (block - 1) / max(1, len(blocks) - 1) * (width - pad_l - pad_r)

    def sy(value: float) -> float:
        return pad_t + (max_y - value) / span * (height - pad_t - pad_b)

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="#fbfbf8"/>',
        '<text x="24" y="28" font-family="Segoe UI, Arial" font-size="18" font-weight="700" fill="#222">Liquidity dwell due diligence: chronological block PnL</text>',
        f'<line x1="{pad_l}" y1="{sy(0):.1f}" x2="{width-pad_r}" y2="{sy(0):.1f}" stroke="#999" stroke-width="1"/>',
        f'<line x1="{pad_l}" y1="{pad_t}" x2="{pad_l}" y2="{height-pad_b}" stroke="#555" stroke-width="1"/>',
        f'<line x1="{pad_l}" y1="{height-pad_b}" x2="{width-pad_r}" y2="{height-pad_b}" stroke="#555" stroke-width="1"/>',
    ]
    for idx, variant in enumerate(variants):
        points = sorted([row for row in rows if row["variant"] == variant], key=lambda row: int(row["block"]))
        d = " ".join(
            ("M" if i == 0 else "L") + f"{sx(int(row['block'])):.1f},{sy(float(row['pnl_100'])):.1f}"
            for i, row in enumerate(points)
        )
        color = colors[idx % len(colors)]
        parts.append(f'<path d="{d}" fill="none" stroke="{color}" stroke-width="2.2"/>')
        lx = 85 + (idx % 2) * 470
        ly = height - 42 + (idx // 2) * 16
        parts.append(f'<rect x="{lx}" y="{ly-9}" width="18" height="3" fill="{color}"/>')
        parts.append(f'<text x="{lx+24}" y="{ly-5}" font-family="Segoe UI, Arial" font-size="12" fill="#222">{variant}</text>')
    parts.append("</svg>")
    path.write_text("\n".join(parts), encoding="utf-8")


def main() -> None:
    prepped, _quote_delays = prior.load_prepped_quote_path()
    count = len(prepped)
    split = int(count * 0.7)
    holdout_indices = list(range(split, count))
    train_indices = list(range(split))
    specs = variant_specs()
    all_rows: list[dict[str, Any]] = []
    final_rows: list[dict[str, Any]] = []
    summary_rows: list[dict[str, Any]] = []
    group_rows: list[dict[str, Any]] = []
    block_rows: list[dict[str, Any]] = []
    bootstrap_rows: list[dict[str, Any]] = []
    rejection_rows: list[dict[str, Any]] = []
    slippage_rows: list[dict[str, Any]] = []
    size_rows: list[dict[str, Any]] = []
    holdout_by_variant: dict[str, list[dict[str, Any]]] = {}

    for spec in specs:
        params = spec["params"]
        variant = spec["variant"]
        rows: list[dict[str, Any]] = []
        finals: list[dict[str, Any]] = []
        for idx, (case, prepared) in enumerate(prepped):
            outcome = improve.simulate_case(case, prepared, params)
            rows.append(case_row(case, outcome, idx=idx, variant=variant, mode="dwell"))
            final = final_gate_outcome(case, prepared, params)
            finals.append(case_row(case, final, idx=idx, variant=variant, mode="final_gate_only"))
        all_rows.extend(rows)
        final_rows.extend(finals)
        holdout_rows = [row for row in rows if row["case_index"] in holdout_indices]
        train_rows = [row for row in rows if row["case_index"] in train_indices]
        holdout_by_variant[variant] = holdout_rows
        for sample, sample_rows in (("train", train_rows), ("holdout", holdout_rows), ("full", rows)):
            summary = summarize_rows(sample, sample_rows)
            summary_rows.append({"variant": variant, "sample": sample, "hypothesis": spec["hypothesis"], **summary})
        for row in grouped_summaries(holdout_rows, ["dataset", "side", "entry_day_et", "entry_hour_utc"]):
            group_rows.append({"variant": variant, **row})
        for row in chronological_block_rows(rows, 16):
            block_rows.append({"variant": variant, **row})
        bootstrap_rows.append({"variant": variant, "sample": "holdout_trade_bootstrap", **bootstrap_pnl(holdout_rows)})
        bootstrap_rows.append({"variant": variant, "sample": "holdout_day_bootstrap", **bootstrap_pnl(holdout_rows, cluster_key="entry_day_et")})
        holdout_finals = [row for row in finals if row["case_index"] in holdout_indices]
        rejection_rows.append({"variant": variant, **final_gate_rejection(holdout_rows, holdout_finals)})
        slippage_rows.extend(slippage_curve(prepped, params, holdout_indices, variant))
        size_rows.extend(size_curve(prepped, params, holdout_indices, variant))

    overlap_rows = overlap_matrix(holdout_by_variant)

    timestamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
    report_md = EDGE_DIR / f"liquidity_dwell_due_diligence_{timestamp}.md"
    json_path = EDGE_DIR / f"liquidity_dwell_due_diligence_{timestamp}.json"
    summary_csv = EDGE_DIR / f"liquidity_dwell_due_diligence_summary_{timestamp}.csv"
    groups_csv = EDGE_DIR / f"liquidity_dwell_due_diligence_groups_{timestamp}.csv"
    blocks_csv = EDGE_DIR / f"liquidity_dwell_due_diligence_blocks_{timestamp}.csv"
    bootstrap_csv = EDGE_DIR / f"liquidity_dwell_due_diligence_bootstrap_{timestamp}.csv"
    rejection_csv = EDGE_DIR / f"liquidity_dwell_due_diligence_rejections_{timestamp}.csv"
    slippage_csv = EDGE_DIR / f"liquidity_dwell_due_diligence_slippage_{timestamp}.csv"
    size_csv = EDGE_DIR / f"liquidity_dwell_due_diligence_size_curve_{timestamp}.csv"
    overlap_csv = EDGE_DIR / f"liquidity_dwell_due_diligence_overlap_{timestamp}.csv"
    rows_csv = EDGE_DIR / f"liquidity_dwell_due_diligence_rows_{timestamp}.csv"
    chart_svg = EDGE_DIR / f"liquidity_dwell_due_diligence_blocks_{timestamp}.svg"

    write_csv(summary_csv, summary_rows)
    write_csv(groups_csv, group_rows)
    write_csv(blocks_csv, block_rows)
    write_csv(bootstrap_csv, bootstrap_rows)
    write_csv(rejection_csv, rejection_rows)
    write_csv(slippage_csv, slippage_rows)
    write_csv(size_csv, size_rows)
    write_csv(overlap_csv, overlap_rows)
    write_csv(rows_csv, all_rows)
    make_block_chart(chart_svg, block_rows)

    holdout_summary = sorted(
        [row for row in summary_rows if row["sample"] == "holdout"],
        key=lambda row: float(row["pnl_100"]),
        reverse=True,
    )
    top_bootstrap = {row["variant"]: row for row in bootstrap_rows if row["sample"] == "holdout_day_bootstrap"}
    top_rejections = {row["variant"]: row for row in rejection_rows}

    lines = [
        "# Liquidity Dwell Due Diligence",
        "",
        f"- Generated: `{datetime.now(UTC).isoformat(timespec='seconds')}`",
        "- Scope: research-only. No live entry logic, exit logic, production configs, run scripts, or bot processes were changed.",
        f"- Fixed candidates tested: `{len(specs)}`.",
        "- Purpose: extensive validation/invalidation around concentration, bootstrap confidence, slippage, size, overlap, and final-gate rejection quality.",
        "",
        "## Candidate Scorecard",
        "",
        "| Variant | Holdout PnL at 100 | Entries | Edge/trade | Win rate | Max DD | Day-bootstrap p05/p50/p95 | P(positive) | Rejected final-gate PnL |",
        "|---|---:|---:|---:|---:|---:|---|---:|---:|",
    ]
    for row in holdout_summary:
        boot = top_bootstrap[row["variant"]]
        reject = top_rejections[row["variant"]]
        lines.append(
            f"| `{row['variant']}` | {money(row['pnl_100'])} | {row['entries']} | {money(row['edge_per_entry_100'])} | "
            f"{pct(row['win_rate'])} | {money(row['max_drawdown_100'])} | "
            f"{money(boot['p05_pnl_100'])}/{money(boot['p50_pnl_100'])}/{money(boot['p95_pnl_100'])} | "
            f"{pct(boot['prob_positive'])} | {money(reject['rejected_if_entered_pnl_100'])} |"
        )
    lines.extend(
        [
            "",
            "## Slippage Breakeven",
            "",
            "| Variant | +0c | +3c | +5c | +10c |",
            "|---|---:|---:|---:|---:|",
        ]
    )
    for variant in [spec["variant"] for spec in specs]:
        values = {int(row["slippage_cents"]): row["pnl_100"] for row in slippage_rows if row["variant"] == variant}
        lines.append(
            f"| `{variant}` | {money(values.get(0))} | {money(values.get(3))} | {money(values.get(5))} | {money(values.get(10))} |"
        )
    lines.extend(
        [
            "",
            "## Biggest Slice Risks",
            "",
            "| Variant | Worst dataset | PnL | Worst side | PnL | Worst day/hour group | PnL |",
            "|---|---|---:|---|---:|---|---:|",
        ]
    )
    for variant in [spec["variant"] for spec in specs]:
        dataset_groups = [row for row in group_rows if row["variant"] == variant and row["group_key"] == "dataset"]
        side_groups = [row for row in group_rows if row["variant"] == variant and row["group_key"] == "side"]
        day_hour_groups = [
            row for row in group_rows
            if row["variant"] == variant and row["group_key"] in {"entry_day_et", "entry_hour_utc"} and int(row["entries"]) > 0
        ]
        worst_dataset = min(dataset_groups, key=lambda row: float(row["pnl_100"])) if dataset_groups else {}
        worst_side = min(side_groups, key=lambda row: float(row["pnl_100"])) if side_groups else {}
        worst_group = min(day_hour_groups, key=lambda row: float(row["pnl_100"])) if day_hour_groups else {}
        lines.append(
            f"| `{variant}` | `{worst_dataset.get('group_value', '')}` | {money(worst_dataset.get('pnl_100'))} | "
            f"`{worst_side.get('group_value', '')}` | {money(worst_side.get('pnl_100'))} | "
            f"`{worst_group.get('group_key', '')}={worst_group.get('group_value', '')}` | {money(worst_group.get('pnl_100'))} |"
        )
    lines.extend(
        [
            "",
            "## Read",
            "",
            "- The PnL-max variant still wins on raw holdout dollars, but it relies on the relaxed quality-share setting and remains a shadow candidate.",
            "- The ask<=88 pressure-persistence/path-stability variants give up PnL but are more selective and often have cleaner slice behavior; these are better robustness probes.",
            "- The rejected-final-gate column is important: negative rejected PnL means the dwell layer is filtering bad final-gate trades, not just reducing volume.",
            "- This still does not replace fresh forward settlement. The next go/no-go gate should be locked shadow collection on markets after this research timestamp.",
            "",
            "## Artifacts",
            "",
            f"- [summary CSV](<{summary_csv.resolve()}>)",
            f"- [group/slice CSV](<{groups_csv.resolve()}>)",
            f"- [block CSV](<{blocks_csv.resolve()}>)",
            f"- [bootstrap CSV](<{bootstrap_csv.resolve()}>)",
            f"- [final-gate rejection CSV](<{rejection_csv.resolve()}>)",
            f"- [slippage CSV](<{slippage_csv.resolve()}>)",
            f"- [size curve CSV](<{size_csv.resolve()}>)",
            f"- [overlap CSV](<{overlap_csv.resolve()}>)",
            f"- [per-case rows](<{rows_csv.resolve()}>)",
            f"- [block chart](<{chart_svg.resolve()}>)",
        ]
    )
    report_md.write_text("\n".join(lines) + "\n", encoding="utf-8")
    json_path.write_text(
        json.dumps(
            {
                "generated": datetime.now(UTC).isoformat(),
                "summary_rows": summary_rows,
                "bootstrap_rows": bootstrap_rows,
                "rejection_rows": rejection_rows,
                "slippage_rows": slippage_rows,
                "size_rows": size_rows,
                "overlap_rows": overlap_rows,
            },
            indent=2,
            sort_keys=True,
        ),
        encoding="utf-8",
    )

    latest_pairs = {
        report_md: EDGE_DIR / "liquidity_dwell_due_diligence_latest.md",
        json_path: EDGE_DIR / "liquidity_dwell_due_diligence_latest.json",
        summary_csv: EDGE_DIR / "liquidity_dwell_due_diligence_summary_latest.csv",
        groups_csv: EDGE_DIR / "liquidity_dwell_due_diligence_groups_latest.csv",
        blocks_csv: EDGE_DIR / "liquidity_dwell_due_diligence_blocks_latest.csv",
        bootstrap_csv: EDGE_DIR / "liquidity_dwell_due_diligence_bootstrap_latest.csv",
        rejection_csv: EDGE_DIR / "liquidity_dwell_due_diligence_rejections_latest.csv",
        slippage_csv: EDGE_DIR / "liquidity_dwell_due_diligence_slippage_latest.csv",
        size_csv: EDGE_DIR / "liquidity_dwell_due_diligence_size_curve_latest.csv",
        overlap_csv: EDGE_DIR / "liquidity_dwell_due_diligence_overlap_latest.csv",
        rows_csv: EDGE_DIR / "liquidity_dwell_due_diligence_rows_latest.csv",
        chart_svg: EDGE_DIR / "liquidity_dwell_due_diligence_blocks_latest.svg",
    }
    for src, dst in latest_pairs.items():
        dst.write_text(src.read_text(encoding="utf-8"), encoding="utf-8")

    print(
        json.dumps(
            {
                "report": str(report_md.resolve()),
                "json": str(json_path.resolve()),
                "summary_csv": str(summary_csv.resolve()),
                "bootstrap_csv": str(bootstrap_csv.resolve()),
                "rejection_csv": str(rejection_csv.resolve()),
                "slippage_csv": str(slippage_csv.resolve()),
                "rows_csv": str(rows_csv.resolve()),
                "chart_svg": str(chart_svg.resolve()),
                "variants": len(specs),
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
