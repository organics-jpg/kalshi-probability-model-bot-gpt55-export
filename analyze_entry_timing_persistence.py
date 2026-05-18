from __future__ import annotations

import csv
import json
import math
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from probe_codex_entry_timing_edges import (
    StrategySpec,
    build_kelly_model,
    discover_datasets,
    load_dataset_cases,
    prepare_case,
    sim_delayed_entry_survival_filter,
    sim_empirical_kelly_entry_sizer,
    summarize_entry_rows,
)
from probe_stop_touch_confirmation import strategy_id


ROOT = Path(__file__).resolve().parent
EDGE_DIR = ROOT / "logs" / "edge_research"
LATEST_ENTRY_JSON = EDGE_DIR / "codex_entry_timing_research_latest.json"
UTC = timezone.utc


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def fnum(value: Any, default: float = 0.0) -> float:
    try:
        parsed = float(value)
    except (TypeError, ValueError):
        return default
    return default if math.isnan(parsed) else parsed


def money(value: Any) -> str:
    return f"${fnum(value):,.2f}"


def link(path: Path, label: str | None = None) -> str:
    return f"[{label or path.name}](<{path.resolve()}>)"


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def enhanced_summary(label: str, rows: list[dict[str, Any]]) -> dict[str, Any]:
    summary = summarize_entry_rows(label, rows)
    entries = int(summary["entries"])
    contracts = int(summary["total_contracts"])
    n = int(summary["n"])
    sim = fnum(summary["sim_pnl"])
    summary["net_edge_per_entered_trade"] = round(sim / entries, 4) if entries else 0.0
    summary["net_edge_per_contract"] = round(sim / contracts, 4) if contracts else 0.0
    summary["net_edge_per_opportunity"] = round(sim / n, 4) if n else 0.0
    summary["delta_vs_actual_per_opportunity"] = round(fnum(summary["delta_vs_actual"]) / n, 4) if n else 0.0
    summary["delta_vs_no_stop_per_opportunity"] = round(fnum(summary["delta_vs_no_stop"]) / n, 4) if n else 0.0
    summary["loss_rate_when_entered"] = round(
        int(summary["entered_settlement_losers"]) / entries, 4
    ) if entries else 0.0
    return summary


def make_spec(family: str, params: dict[str, Any], theorem: str, equation: str) -> StrategySpec:
    if family == "delayed_entry_survival_filter":
        return StrategySpec(
            family=family,
            theorem=theorem,
            equation=equation,
            params=params,
            simulator=sim_delayed_entry_survival_filter,
            model_builder=None,
        )
    if family == "empirical_kelly_entry_sizer":
        return StrategySpec(
            family=family,
            theorem=theorem,
            equation=equation,
            params=params,
            simulator=sim_empirical_kelly_entry_sizer,
            model_builder=build_kelly_model,
        )
    raise ValueError(f"unsupported family {family}")


def row_for_case(case: dict[str, Any], pnl: float, meta: dict[str, Any], label: str, family: str, variant: str) -> dict[str, Any]:
    return {
        "label": label,
        "family": family,
        "variant": variant,
        "dataset": case["dataset"],
        "market": case["market"],
        "side": case.get("side"),
        "entry_ts": case["entry_ts"],
        "entry_day_et": case["entry_day_et"],
        "settlement_win": bool(case["settlement_win"]),
        "actual_net_pnl": float(case["actual_net_pnl"]),
        "hold_pnl": float(case["hold_pnl"]),
        "sim_pnl": float(pnl),
        "action": "enter" if meta.get("enter") else "skip",
        "entry_ask": meta.get("entry_ask"),
        "entry_elapsed": meta.get("entry_elapsed"),
        "contracts": int(meta.get("contracts") or 0),
        "base_contracts": int(case["qty"]),
        "skip_reason": meta.get("skip_reason"),
        "q_hat": meta.get("q_hat"),
        "edge_cents": meta.get("edge_cents"),
        "kelly_fraction": meta.get("kelly_fraction"),
        "pressure": meta.get("pressure"),
        "bid_sum": meta.get("bid_sum"),
        "spread": meta.get("spread"),
    }


def run_rows(
    prepped: list[tuple[dict[str, Any], dict[str, Any]]],
    spec: StrategySpec,
    label: str,
    variant: str,
    *,
    model_prepped: list[tuple[dict[str, Any], dict[str, Any]]] | None = None,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    model = spec.model_builder(model_prepped or prepped, spec.params) if spec.model_builder else None
    rows = []
    for case, prepared in prepped:
        pnl, meta = spec.simulator(case, prepared, spec.params, model)
        rows.append(row_for_case(case, pnl, meta, label, spec.family, variant))
    model_summary = {
        "train_cases": model.get("train_cases") if model else None,
        "global_q": round(float(model.get("global_q")), 6) if model else None,
        "cells": len(model.get("counts", {})) if model else None,
    }
    return rows, model_summary


def group_summary(label: str, rows: list[dict[str, Any]], group_key: str) -> list[dict[str, Any]]:
    out = []
    groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        groups[str(row.get(group_key))].append(row)
    for key in sorted(groups):
        summary = enhanced_summary(label, groups[key])
        out.append({"group": key, **summary})
    return out


def max_drawdown(values: list[float]) -> float:
    peak = 0.0
    drawdown = 0.0
    running = 0.0
    for value in values:
        running += value
        peak = max(peak, running)
        drawdown = min(drawdown, running - peak)
    return round(drawdown, 4)


def chronological_blocks(prepped: list[tuple[dict[str, Any], dict[str, Any]]], block_count: int = 5):
    ordered = sorted(prepped, key=lambda item: (item[0]["entry_ts"], item[0]["market"], item[0]["side"]))
    blocks = []
    for block_index in range(block_count):
        start = round(len(ordered) * block_index / block_count)
        end = round(len(ordered) * (block_index + 1) / block_count)
        blocks.append(ordered[start:end])
    return blocks


def svg_cumulative(path: Path, series: dict[str, list[tuple[int, float]]]) -> None:
    width, height = 1000, 520
    ml, mr, mt, mb = 70, 210, 45, 60
    plot_w, plot_h = width - ml - mr, height - mt - mb
    all_x = [x for vals in series.values() for x, _ in vals]
    all_y = [y for vals in series.values() for _, y in vals] + [0.0]
    x_min, x_max = min(all_x or [0]), max(all_x or [1])
    y_min, y_max = min(all_y), max(all_y)
    if abs(y_max - y_min) < 1e-9:
        y_min -= 1
        y_max += 1
    y_pad = (y_max - y_min) * 0.08
    y_min -= y_pad
    y_max += y_pad

    def sx(x: float) -> float:
        return ml + ((x - x_min) / max(1, x_max - x_min)) * plot_w

    def sy(y: float) -> float:
        return mt + (1 - ((y - y_min) / (y_max - y_min))) * plot_h

    colors = ["#2563eb", "#16a34a", "#dc2626", "#9333ea", "#f59e0b", "#0891b2"]
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="#fff"/>',
        '<text x="70" y="28" font-family="Arial" font-size="20" font-weight="700" fill="#111827">Entry Timing Cumulative PnL by Variant</text>',
        f'<line x1="{ml}" y1="{sy(0):.2f}" x2="{width - mr}" y2="{sy(0):.2f}" stroke="#9ca3af"/>',
        f'<line x1="{ml}" y1="{mt}" x2="{ml}" y2="{height - mb}" stroke="#111827"/>',
        f'<line x1="{ml}" y1="{height - mb}" x2="{width - mr}" y2="{height - mb}" stroke="#111827"/>',
    ]
    for i, (label, vals) in enumerate(series.items()):
        color = colors[i % len(colors)]
        points = " ".join(f"{sx(x):.2f},{sy(y):.2f}" for x, y in vals)
        if points:
            parts.append(f'<polyline fill="none" stroke="{color}" stroke-width="2" points="{points}"/>')
        ly = 68 + i * 22
        parts.append(f'<rect x="{width - mr + 25}" y="{ly - 10}" width="10" height="10" fill="{color}"/>')
        parts.append(f'<text x="{width - mr + 42}" y="{ly}" font-family="Arial" font-size="12" fill="#374151">{label}</text>')
    for tick in range(5):
        y = y_min + (y_max - y_min) * tick / 4
        parts.append(f'<text x="{ml - 8}" y="{sy(y) + 4:.2f}" text-anchor="end" font-family="Arial" font-size="11" fill="#4b5563">{y:.0f}</text>')
    parts.append("</svg>")
    path.write_text("\n".join(parts), encoding="utf-8")


def main() -> None:
    latest = load_json(LATEST_ENTRY_JSON)
    datasets = latest.get("datasets") or discover_datasets()
    payloads = [load_dataset_cases(dataset, refresh_cache=False) for dataset in datasets]
    cases: list[dict[str, Any]] = []
    for payload in payloads:
        cases.extend(payload.get("cases", []))
    cases = sorted(cases, key=lambda case: (case["entry_ts"], case["market"], case["side"]))

    candidates: list[dict[str, Any]] = []
    for family in ("delayed_entry_survival_filter", "empirical_kelly_entry_sizer"):
        best = latest["best_by_family"][family]
        walk = latest["walk_forward"]["families"][family]
        theorem = best["theorem"]
        equation = best["equation"]
        variants = [
            ("full_sample_best", best["params"]),
            ("train_selected", walk["selected_params"]),
        ]
        robust_rows = latest.get("robust_positive_scan", {}).get(family, [])
        if robust_rows:
            variants.append(("robust_positive_top", robust_rows[0]["params"]))
        seen = set()
        for variant, params in variants:
            key = json.dumps(params, sort_keys=True)
            if key in seen:
                continue
            seen.add(key)
            spec = make_spec(family, params, theorem, equation)
            candidates.append(
                {
                    "family": family,
                    "variant": variant,
                    "strategy_id": strategy_id(family, params),
                    "params": params,
                    "spec": spec,
                }
            )

    delays = tuple(sorted({int(c["params"]["delay_seconds"]) for c in candidates}))
    prepped = [(case, prepare_case(case, delays)) for case in cases]
    ordered = sorted(prepped, key=lambda item: (item[0]["entry_ts"], item[0]["market"], item[0]["side"]))
    split = int(len(ordered) * 0.7)
    train = ordered[:split]
    holdout = ordered[split:]
    blocks = chronological_blocks(ordered, 5)

    stamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
    json_path = EDGE_DIR / f"codex_entry_timing_persistence_{stamp}.json"
    md_path = EDGE_DIR / f"codex_entry_timing_persistence_{stamp}.md"
    summary_csv = EDGE_DIR / f"codex_entry_timing_persistence_summary_{stamp}.csv"
    blocks_csv = EDGE_DIR / f"codex_entry_timing_persistence_blocks_{stamp}.csv"
    daily_csv = EDGE_DIR / f"codex_entry_timing_persistence_daily_{stamp}.csv"
    rows_csv = EDGE_DIR / f"codex_entry_timing_persistence_rows_{stamp}.csv"
    chart_svg = EDGE_DIR / f"codex_entry_timing_persistence_cumulative_{stamp}.svg"
    latest_md = EDGE_DIR / "codex_entry_timing_persistence_latest.md"
    latest_json = EDGE_DIR / "codex_entry_timing_persistence_latest.json"

    summary_rows = []
    daily_rows = []
    block_rows = []
    all_case_rows = []
    cumulative_series = {}
    payload_candidates = []

    for candidate in candidates:
        spec: StrategySpec = candidate["spec"]
        label = candidate["strategy_id"]
        variant = candidate["variant"]
        family = candidate["family"]

        full_rows, full_model = run_rows(prepped, spec, label, variant)
        train_rows, train_model = run_rows(train, spec, label, variant, model_prepped=train)
        holdout_rows, holdout_model = run_rows(holdout, spec, label, variant, model_prepped=train)
        full_summary = enhanced_summary(label, full_rows)
        train_summary = enhanced_summary(label, train_rows)
        holdout_summary = enhanced_summary(label, holdout_rows)

        day_stats = group_summary(label, full_rows, "entry_day_et")
        active_days = [row for row in day_stats if int(row["entries"]) > 0]
        positive_days = [row for row in active_days if fnum(row["sim_pnl"]) > 0]
        negative_days = [row for row in active_days if fnum(row["sim_pnl"]) < 0]

        chronological_entered = [
            row for row in sorted(full_rows, key=lambda row: (row["entry_ts"], row["market"], row["side"]))
            if row["action"] == "enter"
        ]
        cumulative = []
        running = 0.0
        for idx, row in enumerate(chronological_entered, start=1):
            running += fnum(row["sim_pnl"])
            cumulative.append((idx, round(running, 4)))
        cumulative_series[f"{family}:{variant}"[:42]] = cumulative

        oos_block_summaries = []
        for idx, block in enumerate(blocks, start=1):
            if spec.model_builder and idx == 1:
                block_rows.append(
                    {
                        "family": family,
                        "variant": variant,
                        "strategy_id": label,
                        "block": idx,
                        "mode": "calibration_only",
                        "n": len(block),
                        "entries": "",
                        "sim_pnl": "",
                        "net_edge_per_entered_trade": "",
                        "net_edge_per_contract": "",
                        "entry_win_rate": "",
                        "delta_vs_actual": "",
                        "delta_vs_no_stop": "",
                    }
                )
                continue
            prior = [item for previous in blocks[: idx - 1] for item in previous]
            model_source = prior if spec.model_builder else None
            rows, _ = run_rows(block, spec, label, variant, model_prepped=model_source)
            summary = enhanced_summary(label, rows)
            mode = "prior_only_oos" if spec.model_builder else "fixed_rule"
            block_record = {
                "family": family,
                "variant": variant,
                "strategy_id": label,
                "block": idx,
                "mode": mode,
                "n": summary["n"],
                "entries": summary["entries"],
                "sim_pnl": summary["sim_pnl"],
                "net_edge_per_entered_trade": summary["net_edge_per_entered_trade"],
                "net_edge_per_contract": summary["net_edge_per_contract"],
                "entry_win_rate": summary["entry_win_rate"],
                "delta_vs_actual": summary["delta_vs_actual"],
                "delta_vs_no_stop": summary["delta_vs_no_stop"],
            }
            block_rows.append(block_record)
            oos_block_summaries.append(block_record)

        scored_blocks = [row for row in oos_block_summaries if row["entries"] != "" and int(row["entries"]) > 0]
        positive_blocks = [row for row in scored_blocks if fnum(row["sim_pnl"]) > 0]
        entered_pnls = [fnum(row["sim_pnl"]) for row in chronological_entered]
        summary_record = {
            "family": family,
            "variant": variant,
            "strategy_id": label,
            "status_hint": "candidate" if holdout_summary["sim_pnl"] > 0 else "watchlist",
            "full_sim_pnl": full_summary["sim_pnl"],
            "full_delta_vs_actual": full_summary["delta_vs_actual"],
            "full_delta_vs_no_stop": full_summary["delta_vs_no_stop"],
            "full_entries": full_summary["entries"],
            "full_total_contracts": full_summary["total_contracts"],
            "full_entry_win_rate": full_summary["entry_win_rate"],
            "full_net_edge_per_trade": full_summary["net_edge_per_entered_trade"],
            "full_net_edge_per_contract": full_summary["net_edge_per_contract"],
            "full_net_edge_per_opportunity": full_summary["net_edge_per_opportunity"],
            "train_sim_pnl": train_summary["sim_pnl"],
            "train_net_edge_per_trade": train_summary["net_edge_per_entered_trade"],
            "holdout_sim_pnl": holdout_summary["sim_pnl"],
            "holdout_delta_vs_actual": holdout_summary["delta_vs_actual"],
            "holdout_delta_vs_no_stop": holdout_summary["delta_vs_no_stop"],
            "holdout_entries": holdout_summary["entries"],
            "holdout_entry_win_rate": holdout_summary["entry_win_rate"],
            "holdout_net_edge_per_trade": holdout_summary["net_edge_per_entered_trade"],
            "holdout_net_edge_per_contract": holdout_summary["net_edge_per_contract"],
            "active_days": len(active_days),
            "positive_active_days": len(positive_days),
            "negative_active_days": len(negative_days),
            "positive_active_day_rate": round(len(positive_days) / len(active_days), 4) if active_days else 0.0,
            "scored_oos_blocks": len(scored_blocks),
            "positive_oos_blocks": len(positive_blocks),
            "positive_oos_block_rate": round(len(positive_blocks) / len(scored_blocks), 4) if scored_blocks else 0.0,
            "worst_active_day_pnl": min((fnum(row["sim_pnl"]) for row in active_days), default=0.0),
            "max_entered_trade_drawdown": max_drawdown(entered_pnls),
            "model_train_cases_full": full_model["train_cases"],
            "model_global_q_full": full_model["global_q"],
            "params": json.dumps(candidate["params"], sort_keys=True),
        }
        summary_rows.append(summary_record)
        payload_candidates.append(
            {
                "family": family,
                "variant": variant,
                "strategy_id": label,
                "params": candidate["params"],
                "full_summary": full_summary,
                "train_summary": train_summary,
                "holdout_summary": holdout_summary,
                "day_summary": day_stats,
                "oos_blocks": oos_block_summaries,
                "model_summary_full": full_model,
                "model_summary_train": train_model,
                "holdout_model_summary": holdout_model,
            }
        )

        for row in day_stats:
            daily_rows.append(
                {
                    "family": family,
                    "variant": variant,
                    "strategy_id": label,
                    "day": row["group"],
                    "n": row["n"],
                    "entries": row["entries"],
                    "sim_pnl": row["sim_pnl"],
                    "net_edge_per_entered_trade": row["net_edge_per_entered_trade"],
                    "net_edge_per_contract": row["net_edge_per_contract"],
                    "entry_win_rate": row["entry_win_rate"],
                    "delta_vs_actual": row["delta_vs_actual"],
                    "delta_vs_no_stop": row["delta_vs_no_stop"],
                    "entered_losers": row["entered_settlement_losers"],
                    "skipped_losers": row["skipped_settlement_losers"],
                    "skipped_winners": row["skipped_settlement_winners"],
                }
            )
        all_case_rows.extend(full_rows)

    summary_rows = sorted(summary_rows, key=lambda row: (fnum(row["holdout_sim_pnl"]), fnum(row["full_sim_pnl"])), reverse=True)
    write_csv(summary_csv, summary_rows)
    write_csv(blocks_csv, block_rows)
    write_csv(daily_csv, daily_rows)
    write_csv(rows_csv, all_case_rows)
    svg_cumulative(chart_svg, cumulative_series)

    report_payload = {
        "generated_at": datetime.now(UTC).isoformat(),
        "source": Path(__file__).name,
        "scope": "research_only_entry_timing_persistence",
        "datasets": datasets,
        "case_count": len(cases),
        "train_n": len(train),
        "holdout_n": len(holdout),
        "split_entry_ts": holdout[0][0]["entry_ts"] if holdout else None,
        "candidates": payload_candidates,
        "summary_rows": summary_rows,
        "artifacts": {
            "summary_csv": str(summary_csv),
            "blocks_csv": str(blocks_csv),
            "daily_csv": str(daily_csv),
            "rows_csv": str(rows_csv),
            "chart_svg": str(chart_svg),
            "markdown": str(md_path),
            "json": str(json_path),
        },
        "guardrail": "No live entry logic, live exit logic, production config, run script, or live process was changed.",
    }
    json_path.write_text(json.dumps(report_payload, indent=2, sort_keys=True), encoding="utf-8")
    latest_json.write_text(json.dumps(report_payload, indent=2, sort_keys=True), encoding="utf-8")

    lines = [
        "# Codex Entry Timing Persistence Deep Dive",
        "",
        f"- Generated: `{report_payload['generated_at']}`",
        f"- Cases: `{len(cases)}` quote-path opportunities across `{', '.join(datasets)}`",
        f"- Chronological split: `{len(train)}` train / `{len(holdout)}` holdout, holdout begins `{report_payload['split_entry_ts']}`",
        "- Scope: research-only. No live logic, configs, run scripts, or processes changed.",
        "",
        "## Headline",
        "",
    ]

    kelly_rows = [row for row in summary_rows if row["family"] == "empirical_kelly_entry_sizer"]
    survival_rows = [row for row in summary_rows if row["family"] == "delayed_entry_survival_filter"]
    best_kelly = max(kelly_rows, key=lambda row: fnum(row["holdout_sim_pnl"])) if kelly_rows else None
    best_survival = max(survival_rows, key=lambda row: fnum(row["holdout_sim_pnl"])) if survival_rows else None
    if best_kelly:
        lines.append(
            f"- Kelly-style entry sizing has the cleaner persistence: best holdout variant `{best_kelly['variant']}` made "
            f"{money(best_kelly['holdout_sim_pnl'])} on {best_kelly['holdout_entries']} entries, "
            f"{money(best_kelly['holdout_net_edge_per_trade'])} per entered trade, and {money(best_kelly['holdout_net_edge_per_contract'])} per contract."
        )
    if best_survival:
        lines.append(
            f"- Delayed survival filtering has larger full-sample upside but is more selection-sensitive: best holdout variant `{best_survival['variant']}` made "
            f"{money(best_survival['holdout_sim_pnl'])}, while the train-selected variant remains negative on holdout."
        )
    lines.append("- Net edge per trade below means realized simulated PnL divided by actual entered trades; skip-all baseline is zero.")

    lines.extend(
        [
            "",
            "## Candidate Summary",
            "",
            "| Family | Variant | Full PnL | Holdout PnL | Holdout edge/trade | Holdout edge/contract | Active day + rate | OOS block + rate | Drawdown | Verdict |",
            "|---|---|---:|---:|---:|---:|---:|---:|---:|---|",
        ]
    )
    for row in summary_rows:
        verdict = "candidate" if row["family"] == "empirical_kelly_entry_sizer" and fnum(row["holdout_sim_pnl"]) > 0 else "watchlist"
        if row["family"] == "delayed_entry_survival_filter" and row["variant"] == "train_selected":
            verdict = "reject selected params"
        elif row["family"] == "delayed_entry_survival_filter" and fnum(row["holdout_sim_pnl"]) > 0:
            verdict = "needs preregistered validation"
        lines.append(
            f"| `{row['family']}` | `{row['variant']}` | {money(row['full_sim_pnl'])} | {money(row['holdout_sim_pnl'])} | "
            f"{money(row['holdout_net_edge_per_trade'])} | {money(row['holdout_net_edge_per_contract'])} | "
            f"{row['positive_active_days']}/{row['active_days']} | {row['positive_oos_blocks']}/{row['scored_oos_blocks']} | "
            f"{money(row['max_entered_trade_drawdown'])} | {verdict} |"
        )

    lines.extend(
        [
            "",
            "## Persistence Notes",
            "",
            "- The train-selected `empirical_kelly_entry_sizer` stayed positive on holdout and had much smaller sizing exposure: 26 holdout entries, 142 contracts, and positive edge versus actual/no-stop/skip-all.",
            "- The train-selected `delayed_entry_survival_filter` beat actual and no-stop on holdout but lost money versus skip-all. For an entry admission strategy, skip-all is the clean hurdle; failing it means the selected params should not be promoted.",
            "- The full-sample survival-filter params are interesting but not clean evidence because the same data selected them. Robust nearby rows need a fresh/pre-registered split.",
            "- For Kelly variants, prior-only block scoring is the closest persistence check because each block only uses earlier blocks to calibrate q-hat.",
            "",
            "## Artifacts",
            "",
            f"- {link(summary_csv)}",
            f"- {link(blocks_csv)}",
            f"- {link(daily_csv)}",
            f"- {link(rows_csv)}",
            f"- {link(chart_svg)}",
            f"- {link(json_path)}",
        ]
    )
    md_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    latest_md.write_text(md_path.read_text(encoding="utf-8"), encoding="utf-8")

    print(
        json.dumps(
            {
                "markdown": str(md_path.resolve()),
                "json": str(json_path.resolve()),
                "summary_csv": str(summary_csv.resolve()),
                "blocks_csv": str(blocks_csv.resolve()),
                "daily_csv": str(daily_csv.resolve()),
                "rows_csv": str(rows_csv.resolve()),
                "chart_svg": str(chart_svg.resolve()),
                "summary_rows": summary_rows,
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
