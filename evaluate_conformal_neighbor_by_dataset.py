from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from probe_stop_touch_confirmation import append_ledger, idea_key, strategy_id, update_strategy_memory
from stress_validate_conformal_neighbor_edges import (
    enrich_settlement_times,
    load_selected_strategies,
    simulate_strategy,
)
from validate_btc_spot_synthetic_ev_broad import EDGE_DIR, baseline_payload, load_or_fetch_candles, prepare_case
from probe_codex_entry_conformal_neighbor_edges import load_cases


UTC = timezone.utc


def compact_summary(row: dict[str, Any]) -> dict[str, Any]:
    keep = [
        "label",
        "n",
        "actual_recorded_pnl",
        "no_stop_hold_pnl",
        "sim_pnl",
        "delta_vs_actual",
        "delta_vs_no_stop",
        "entries",
        "entry_win_rate",
        "entered_settlement_losers",
        "entered_settlement_winners",
        "skipped_settlement_losers",
        "skipped_settlement_winners",
        "total_contracts",
        "contract_fraction",
        "worst_trade",
    ]
    return {key: row.get(key) for key in keep}


def summarize_rows(label: str, rows: list[dict[str, Any]]) -> dict[str, Any]:
    from validate_btc_spot_synthetic_ev_broad import summarize_entry_rows
    from probe_codex_entry_conformal_neighbor_edges import risk_summary

    summary = summarize_entry_rows(label, rows)
    risk = risk_summary(rows)
    return {**summary, "max_drawdown": risk["max_drawdown"], "loss_count": risk["loss_count"]}


def run() -> None:
    cases, _ = load_cases(None)
    settlement_info = enrich_settlement_times(cases)
    selected = load_selected_strategies()
    candles = load_or_fetch_candles(cases, refresh_cache=False)
    delays = tuple(sorted({int(strategy.params["delay_seconds"]) for strategy in selected.values()}))
    prepped = [(case, prepare_case(case, candles, delays)) for case in cases]
    datasets = sorted({str(case["dataset"]) for case in cases})

    scenarios = [
        ("all_settled_history", "settlement_available", "all"),
        ("same_dataset_history", "settlement_available", "same_dataset"),
        ("other_dataset_history", "settlement_available", "cross_dataset"),
        ("entry_proxy_all_history", "entry_proxy", "all"),
    ]

    rows: list[dict[str, Any]] = []
    for family, strategy in selected.items():
        for dataset in datasets:
            for scenario_name, history_mode, history_scope in scenarios:
                sim_rows = simulate_strategy(
                    prepped,
                    strategy,
                    history_mode=history_mode,
                    history_scope=history_scope,
                    current_datasets={dataset},
                )
                summary = summarize_rows(f"{family}:{dataset}:{scenario_name}", sim_rows)
                rows.append(
                    {
                        "family": family,
                        "strategy_id": strategy_id(strategy.family, strategy.params),
                        "dataset": dataset,
                        "scenario": scenario_name,
                        **summary,
                    }
                )

    baselines = baseline_payload(cases)
    generated_at = datetime.now(UTC).isoformat()
    stamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
    json_path = EDGE_DIR / f"conformal_neighbor_by_dataset_{stamp}.json"
    md_path = EDGE_DIR / f"conformal_neighbor_by_dataset_{stamp}.md"
    latest_json = EDGE_DIR / "conformal_neighbor_by_dataset_latest.json"
    latest_md = EDGE_DIR / "conformal_neighbor_by_dataset_latest.md"
    csv_path = EDGE_DIR / f"conformal_neighbor_by_dataset_{stamp}.csv"
    latest_csv = EDGE_DIR / "conformal_neighbor_by_dataset_latest.csv"

    import pandas as pd

    frame = pd.DataFrame(rows)
    frame.to_csv(csv_path, index=False)
    frame.to_csv(latest_csv, index=False)

    payload = {
        "generated_at": generated_at,
        "json_path": str(json_path),
        "markdown_path": str(md_path),
        "csv_path": str(csv_path),
        "datasets": datasets,
        "settlement_info": settlement_info,
        "baselines": baselines,
        "rows": rows,
    }
    text = json.dumps(payload, indent=2, sort_keys=True)
    json_path.write_text(text, encoding="utf-8")
    latest_json.write_text(text, encoding="utf-8")

    lines = [
        "# Conformal Neighbor By-Dataset Validation",
        "",
        f"- Generated: `{generated_at}`",
        f"- Datasets: `{', '.join(datasets)}`",
        f"- Settlement timestamp fallback count: `{settlement_info['settlement_missing_fallback_count']}`",
        "- Scope: research-only; live entry/exit logic, configs, run scripts, and bot processes were not changed.",
        "",
        "## Selected Sizer Across Datasets",
        "",
        "| Dataset | Scenario | PnL | Delta Actual | Entries | Win Rate | Losses | Max DD | Worst |",
        "|---|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for row in rows:
        if row["family"] != "online_neighbor_lcb_sizer":
            continue
        lines.append(
            f"| `{row['dataset']}` | `{row['scenario']}` | {row['sim_pnl']} | {row['delta_vs_actual']} | {row['entries']} | {row['entry_win_rate']} | {row['loss_count']} | {row['max_drawdown']} | {row['worst_trade']} |"
        )
    lines.extend(
        [
            "",
            "## Readout",
            "",
            "- `live_90_70` remains the only dataset with meaningful entry count under the selected candidate.",
            "- `live_87_77_67` fires twice and wins, but it has only 9 cases, so this is anecdotal.",
            "- `entry_90_stop_78` and `live_90_78` produce zero selected entries with the chosen parameters.",
            "- Same-dataset-only history is weaker than all-history, which suggests the candidate is borrowing useful context from the full settled pool, but not enough to generalize outside `live_90_70` yet.",
        ]
    )
    md_path.write_text("\n".join(lines), encoding="utf-8")
    latest_md.write_text("\n".join(lines), encoding="utf-8")

    # Ledger this as validation of an existing candidate, not a new production proposal.
    sizer_rows = [row for row in rows if row["family"] == "online_neighbor_lcb_sizer"]
    all_history_rows = [row for row in sizer_rows if row["scenario"] == "all_settled_history"]
    actual = round(sum(float(row["actual_recorded_pnl"]) for row in all_history_rows), 2)
    no_stop = round(sum(float(row["no_stop_hold_pnl"]) for row in all_history_rows), 2)
    sim = round(sum(float(row["sim_pnl"]) for row in all_history_rows), 2)
    total = {
        "actual_recorded_pnl": actual,
        "no_stop_hold_pnl": no_stop,
        "sim_pnl": sim,
        "delta_vs_actual": round(sim - actual, 2),
        "delta_vs_no_stop": round(sim - no_stop, 2),
        "entries": sum(int(row["entries"]) for row in all_history_rows),
        "datasets_with_entries": [row["dataset"] for row in all_history_rows if int(row["entries"]) > 0],
    }
    strategy = selected["online_neighbor_lcb_sizer"]
    family = "online_neighbor_lcb_sizer_by_dataset_validation"
    equation = strategy.equation + " Validation split: score selected candidate separately by current dataset using all, same-dataset, cross-dataset, and entry-proxy histories."
    ledger_record = {
        "recorded_at": generated_at,
        "generated_at": generated_at,
        "source": Path(__file__).name,
        "status": "validated_dataset_concentrated",
        "dataset": "all_quote_path_trades_with_closed_1m_btc_by_dataset",
        "datasets": datasets,
        "family": family,
        "strategy_id": strategy_id(family, strategy.params),
        "idea_key": idea_key(family, equation, strategy.params),
        "theorem": strategy.theorem,
        "equation": equation,
        "params": strategy.params,
        "summary": total,
        "json_path": str(json_path),
        "markdown_path": str(md_path),
    }
    append_ledger([ledger_record])
    update_strategy_memory(payload, {family: {"strategy_id": ledger_record["strategy_id"], "summary": total}})
    print(f"Wrote {md_path} | all-history datasets with entries: {total['datasets_with_entries']}")


if __name__ == "__main__":
    run()
