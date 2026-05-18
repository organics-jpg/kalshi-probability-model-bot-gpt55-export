"""Chronological block audit for locked BTC 15m profit candidates.

This diagnostic asks a simple anti-overfitting question: when markets are
grouped into sequential chronological blocks, does a candidate make money in
most blocks while keeping high recurring-market coverage?

Research-only: no orders are submitted and no bot files or live processes are
modified. This is not promotion evidence.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any, Dict, List

import pandas as pd

from probe_cross_dataset_interval_frontier import load_v21_side_rows
from probe_cross_dataset_profit_frontier import fmt_cents, fmt_roi
from probe_market_interval_80coverage import OUT_DIR, clean_json, load_side_rows, market_base, pct
from probe_profit_lock_candidate_stability_audit import prepare_selected


REPORT_MD = OUT_DIR / "profit_lock_walkforward_block_audit_latest.md"
REPORT_JSON = OUT_DIR / "profit_lock_walkforward_block_audit_latest.json"
BLOCK_CSV = OUT_DIR / "profit_lock_walkforward_block_audit_latest.csv"
SUMMARY_CSV = OUT_DIR / "profit_lock_walkforward_block_summary_latest.csv"

BLOCK_MARKETS = 20
COVERAGE_FLOOR = 0.75


def clean_json_local(value: Any) -> Any:
    if isinstance(value, pd.Timestamp):
        return value.isoformat()
    if isinstance(value, dict):
        return {str(k): clean_json_local(v) for k, v in value.items()}
    if isinstance(value, list):
        return [clean_json_local(v) for v in value]
    return clean_json(value)


def block_base(base: pd.DataFrame) -> pd.DataFrame:
    out = base.copy()
    out["close_dt"] = pd.to_datetime(out["close_dt"], utc=True, errors="coerce")
    out = out.sort_values(["close_dt", "market"]).reset_index(drop=True)
    out["block_index"] = out.index // BLOCK_MARKETS
    block_info = (
        out.groupby("block_index", as_index=False, sort=True)
        .agg(
            block_start_close_dt=("close_dt", "min"),
            block_end_close_dt=("close_dt", "max"),
            block_base_markets=("market", "count"),
        )
    )
    return out.merge(block_info, on="block_index", how="left")


def selected_with_blocks(selected: pd.DataFrame, base_blocks: pd.DataFrame) -> pd.DataFrame:
    if selected.empty:
        return selected.copy()
    cols = [
        "market",
        "block_index",
        "block_start_close_dt",
        "block_end_close_dt",
        "block_base_markets",
        "split",
    ]
    return selected.drop(columns=[col for col in cols if col in selected.columns and col != "market"], errors="ignore").merge(
        base_blocks[cols],
        on="market",
        how="inner",
    )


def summarize_block(dataset: str, policy: str, block: pd.Series, selected: pd.DataFrame) -> Dict[str, Any]:
    part = selected[selected["block_index"].eq(block["block_index"])].copy()
    n = int(len(part))
    wins = int(part["win"].astype(bool).sum()) if n else 0
    net = float(pd.to_numeric(part.get("net_pnl_cents"), errors="coerce").sum()) if n else 0.0
    cost = float(pd.to_numeric(part.get("entry_cost_cents"), errors="coerce").sum()) if n else 0.0
    base_n = int(block["block_base_markets"])
    return {
        "dataset": dataset,
        "policy": policy,
        "block_index": int(block["block_index"]),
        "block_start_close_dt": block["block_start_close_dt"],
        "block_end_close_dt": block["block_end_close_dt"],
        "base_markets": base_n,
        "selected_markets": n,
        "coverage": n / base_n if base_n else None,
        "wins": wins,
        "losses": n - wins,
        "accuracy": wins / n if n else None,
        "net_pnl_cents": net,
        "net_roi_on_cost": net / cost if cost else None,
        "median_ask": float(pd.to_numeric(part["ask_cents"], errors="coerce").median()) if n else None,
        "coverage_pass": (n / base_n if base_n else 0.0) >= COVERAGE_FLOOR,
        "positive_net": net > 0.0,
    }


def build_rows(dataset: str, side_rows: pd.DataFrame) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    base, selected_by_policy = prepare_selected(dataset, side_rows)
    base_blocks = block_base(base)
    block_rows: List[Dict[str, Any]] = []
    summary_rows: List[Dict[str, Any]] = []
    block_index = (
        base_blocks.groupby("block_index", as_index=False, sort=True)
        .agg(
            block_start_close_dt=("block_start_close_dt", "first"),
            block_end_close_dt=("block_end_close_dt", "first"),
            block_base_markets=("block_base_markets", "first"),
        )
    )
    for policy, selected in selected_by_policy.items():
        selected_blocks = selected_with_blocks(selected, base_blocks)
        rows = [
            summarize_block(dataset, policy, block, selected_blocks)
            for _, block in block_index.iterrows()
        ]
        block_rows.extend(rows)
        supported = [row for row in rows if int(row["base_markets"]) >= max(5, BLOCK_MARKETS // 2)]
        positive = [row for row in supported if row["positive_net"]]
        coverage_pass = [row for row in supported if row["coverage_pass"]]
        both_pass = [row for row in supported if row["positive_net"] and row["coverage_pass"]]
        net_sum = sum(float(row["net_pnl_cents"] or 0.0) for row in supported)
        selected_sum = sum(int(row["selected_markets"]) for row in supported)
        cost_sum = float(pd.to_numeric(selected_blocks.get("entry_cost_cents"), errors="coerce").sum()) if not selected_blocks.empty else 0.0
        worst = min(supported, key=lambda row: float(row["net_pnl_cents"] or 0.0)) if supported else {}
        summary_rows.append(
            {
                "dataset": dataset,
                "policy": policy,
                "blocks": len(supported),
                "positive_blocks": len(positive),
                "coverage_pass_blocks": len(coverage_pass),
                "positive_coverage_pass_blocks": len(both_pass),
                "positive_block_rate": len(positive) / len(supported) if supported else None,
                "positive_coverage_pass_rate": len(both_pass) / len(supported) if supported else None,
                "net_pnl_cents": net_sum,
                "net_roi_on_cost": net_sum / cost_sum if cost_sum else None,
                "selected_markets": selected_sum,
                "base_markets": sum(int(row["base_markets"]) for row in supported),
                "coverage": selected_sum / sum(int(row["base_markets"]) for row in supported) if supported else None,
                "worst_block_index": worst.get("block_index"),
                "worst_block_net_pnl_cents": worst.get("net_pnl_cents"),
                "worst_block_coverage": worst.get("coverage"),
            }
        )
    return block_rows, summary_rows


def write_report(generated: str, block_df: pd.DataFrame, summary_df: pd.DataFrame) -> None:
    worst = block_df[
        block_df["base_markets"].ge(max(5, BLOCK_MARKETS // 2))
    ].sort_values("net_pnl_cents", ascending=True).head(20)
    lines = [
        "# Profit Lock Walk-Forward Block Audit",
        "",
        f"Generated UTC: `{generated}`",
        "",
        "## Scope",
        "",
        "- Research-only chronological block diagnostic; no orders are submitted and no bot files or live processes are touched.",
        f"- Blocks are sequential groups of `{BLOCK_MARKETS}` recurring BTC 15m markets.",
        "- A robust high-coverage candidate should not depend on one favorable time slice.",
        "",
        "## Summary",
        "",
        "| dataset | policy | blocks | positive blocks | positive+coverage blocks | total net/ROI | coverage | worst block |",
        "|---|---|---:|---:|---:|---:|---:|---:|",
    ]
    for _, row in summary_df.sort_values(["dataset", "policy"]).iterrows():
        lines.append(
            f"| {row['dataset']} | `{row['policy']}` | {int(row['blocks'])} | "
            f"{int(row['positive_blocks'])}/{pct(row['positive_block_rate'])} | "
            f"{int(row['positive_coverage_pass_blocks'])}/{pct(row['positive_coverage_pass_rate'])} | "
            f"{fmt_cents(row['net_pnl_cents'])}/{fmt_roi(row['net_roi_on_cost'])} | "
            f"{pct(row['coverage'])} | {fmt_cents(row['worst_block_net_pnl_cents'])} |"
        )

    lines += [
        "",
        "## Worst Blocks",
        "",
        "| dataset | policy | block | closes UTC | selected/base | wins/losses | net | ROI |",
        "|---|---|---:|---|---:|---:|---:|---:|",
    ]
    for _, row in worst.iterrows():
        start = pd.to_datetime(row["block_start_close_dt"], utc=True, errors="coerce")
        end = pd.to_datetime(row["block_end_close_dt"], utc=True, errors="coerce")
        lines.append(
            f"| {row['dataset']} | `{row['policy']}` | {int(row['block_index'])} | "
            f"{start.isoformat() if not pd.isna(start) else 'NA'} to {end.isoformat() if not pd.isna(end) else 'NA'} | "
            f"{int(row['selected_markets'])}/{int(row['base_markets'])} | "
            f"{int(row['wins'])}/{int(row['losses'])} | {fmt_cents(row['net_pnl_cents'])} | "
            f"{fmt_roi(row['net_roi_on_cost'])} |"
        )

    lines += ["", "## Read", ""]
    for policy in sorted(summary_df["policy"].unique()):
        part = summary_df[summary_df["policy"].eq(policy)]
        min_positive_rate = float(part["positive_block_rate"].min()) if not part.empty else 0.0
        min_coverage = float(part["coverage"].min()) if not part.empty else 0.0
        worst_block = float(part["worst_block_net_pnl_cents"].min()) if not part.empty else 0.0
        lines.append(
            f"- `{policy}` min positive-block rate/min coverage/worst block: "
            f"{pct(min_positive_rate)}/{pct(min_coverage)}/{fmt_cents(worst_block)}."
        )
    lines.append("- Block stability is diagnostic only; strict pre-registered live evidence remains the promotion gate.")
    REPORT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    generated = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%SZ")
    block_rows: List[Dict[str, Any]] = []
    summary_rows: List[Dict[str, Any]] = []
    for dataset, loader in [("current", load_side_rows), ("v21", load_v21_side_rows)]:
        rows, summary = build_rows(dataset, loader())
        block_rows.extend(rows)
        summary_rows.extend(summary)
    block_df = pd.DataFrame(block_rows)
    summary_df = pd.DataFrame(summary_rows)
    block_df.to_csv(BLOCK_CSV, index=False)
    summary_df.to_csv(SUMMARY_CSV, index=False)
    block_stamp = OUT_DIR / f"profit_lock_walkforward_block_audit_{generated}.csv"
    summary_stamp = OUT_DIR / f"profit_lock_walkforward_block_summary_{generated}.csv"
    block_df.to_csv(block_stamp, index=False)
    summary_df.to_csv(summary_stamp, index=False)
    payload = {
        "generated_utc": generated,
        "block_markets": BLOCK_MARKETS,
        "coverage_floor": COVERAGE_FLOOR,
        "blocks": clean_json_local(block_df.to_dict(orient="records")),
        "summary": clean_json_local(summary_df.to_dict(orient="records")),
    }
    json_stamp = OUT_DIR / f"profit_lock_walkforward_block_audit_{generated}.json"
    for path in [REPORT_JSON, json_stamp]:
        path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    write_report(generated, block_df, summary_df)
    md_stamp = OUT_DIR / f"profit_lock_walkforward_block_audit_{generated}.md"
    md_stamp.write_text(REPORT_MD.read_text(encoding="utf-8"), encoding="utf-8")
    print("Profit lock walk-forward block audit complete")
    print(f"blocks={len(block_df)} summary_rows={len(summary_df)}")
    print(f"report={REPORT_MD}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
