"""Causal block-stability scan for hazard-primary fallback thresholds.

This is the timestamp-causal version of the hazard threshold scan: primary
hazard and fallback rows compete by first eligible entry time per market, with
hazard winning only exact timestamp ties. It exists to test whether raising the
hazard confidence floor fixes low-score loss modes without using noncausal
"hazard appeared later" arbitration.

Research-only: no orders are submitted and no bot files or live processes are
modified. Any passing row is only a forward-test candidate because this scan
sees validation/holdout.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any, Dict, List

import pandas as pd

import probe_hazard_primary_threshold_stability_scan as base_scan
from probe_cross_dataset_interval_frontier import load_v21_side_rows
from probe_cross_dataset_profit_frontier import fmt_cents, fmt_roi
from probe_hazard_fallback_causal_frontier import first_causal_rows
from probe_hazard_fallback_frontier import fallback_selected
from probe_market_interval_80coverage import MARKET_COVERAGE_FLOOR, OUT_DIR, clean_json, load_side_rows, market_base, pct
from probe_physics_probability_blend_audit import add_blend_scores


REPORT_MD = OUT_DIR / "hazard_causal_threshold_stability_scan_latest.md"
REPORT_JSON = OUT_DIR / "hazard_causal_threshold_stability_scan_latest.json"
SUMMARY_CSV = OUT_DIR / "hazard_causal_threshold_stability_summary_latest.csv"
BLOCK_CSV = OUT_DIR / "hazard_causal_threshold_stability_blocks_latest.csv"
SLICE_CSV = OUT_DIR / "hazard_causal_threshold_stability_slices_latest.csv"


def clean_json_local(value: Any) -> Any:
    if isinstance(value, pd.Timestamp):
        return value.isoformat()
    if isinstance(value, dict):
        return {str(k): clean_json_local(v) for k, v in value.items()}
    if isinstance(value, list):
        return [clean_json_local(v) for v in value]
    return clean_json(value)


def causal_combined_selected(base: pd.DataFrame, side_rows: pd.DataFrame, candidate: base_scan.Candidate) -> pd.DataFrame:
    primary = base_scan.hazard_selected(base, side_rows, candidate.hazard_policy)
    fallback = fallback_selected(base, side_rows, candidate.fallback_policy)
    return first_causal_rows(primary, fallback)


def combined_table(summary: pd.DataFrame, blocks: pd.DataFrame) -> pd.DataFrame:
    block_summ = base_scan.block_summary(blocks)
    rows: List[Dict[str, Any]] = []
    for candidate in sorted(summary["candidate"].unique()):
        part = summary[summary["candidate"].eq(candidate)]
        block_part = block_summ[block_summ["candidate"].eq(candidate)] if not block_summ.empty else block_summ
        coverage_ok = bool(part["coverage_pass"].all()) if not part.empty else False
        all_splits_ok = bool(part["all_splits_positive"].all()) if not part.empty else False
        oos_ok = bool(part["oos_positive"].all()) if not part.empty else False
        min_block_rate = float(block_part["positive_coverage_block_rate"].min()) if not block_part.empty else 0.0
        combined_net = float(part["all_net_pnl_cents"].astype(float).sum()) if not part.empty else 0.0
        rows.append(
            {
                "candidate": candidate,
                "combined_net_pnl_cents": combined_net,
                "coverage_ok": coverage_ok,
                "all_splits_ok": all_splits_ok,
                "oos_ok": oos_ok,
                "min_positive_coverage_block_rate": min_block_rate,
                "robust": coverage_ok
                and all_splits_ok
                and oos_ok
                and min_block_rate >= base_scan.POSITIVE_BLOCK_RATE_FLOOR,
            }
        )
    return pd.DataFrame(rows).sort_values(
        ["robust", "min_positive_coverage_block_rate", "combined_net_pnl_cents"],
        ascending=[False, False, False],
    )


def write_report(generated: str, summary: pd.DataFrame, blocks: pd.DataFrame, slices: pd.DataFrame) -> None:
    combined = combined_table(summary, blocks)
    supported = slices[slices["markets"].ge(base_scan.MIN_SLICE_MARKETS)].copy() if not slices.empty else slices
    worst_slices = supported.sort_values("net_pnl_cents", ascending=True).head(18) if not supported.empty else supported

    lines = [
        "# Causal Hazard Threshold Stability Scan",
        "",
        f"Generated UTC: `{generated}`",
        "",
        "## Scope",
        "",
        "- Research-only scan; no orders are submitted and no bot files or live processes are touched.",
        "- Chooses the first eligible hazard-primary or fallback signal by timestamp per market.",
        "- Tests whether raising the hazard floor improves low-score loss modes while preserving high market coverage.",
        "- Any passing row is still only a forward-test candidate because this scan sees validation/holdout.",
        "",
        "## Combined Read",
        "",
        "| candidate | combined net | coverage | all splits | OOS | min positive+coverage blocks | robust |",
        "|---|---:|---|---|---|---:|---|",
    ]
    for _, row in combined.iterrows():
        lines.append(
            f"| `{row['candidate']}` | {fmt_cents(row['combined_net_pnl_cents'])} | "
            f"{bool(row['coverage_ok'])} | {bool(row['all_splits_ok'])} | {bool(row['oos_ok'])} | "
            f"{pct(row['min_positive_coverage_block_rate'])} | {bool(row['robust'])} |"
        )

    lines += [
        "",
        "## Split Summary",
        "",
        "| dataset | candidate | all net/ROI | all acc/cov | train net | validation net | holdout net | coverage pass | all splits positive |",
        "|---|---|---:|---:|---:|---:|---:|---|---|",
    ]
    for _, row in summary.sort_values(["candidate", "dataset"]).iterrows():
        lines.append(
            f"| {row['dataset']} | `{row['candidate']}` | "
            f"{fmt_cents(row['all_net_pnl_cents'])}/{fmt_roi(row['all_net_roi_on_cost'])} | "
            f"{pct(row['all_accuracy'])}/{pct(row['all_coverage'])} | "
            f"{fmt_cents(row['train_net_pnl_cents'])} | {fmt_cents(row['validation_net_pnl_cents'])} | "
            f"{fmt_cents(row['holdout_net_pnl_cents'])} | {bool(row['coverage_pass'])} | "
            f"{bool(row['all_splits_positive'])} |"
        )

    lines += [
        "",
        "## Worst Supported Slices",
        "",
        f"Only slices with at least `{base_scan.MIN_SLICE_MARKETS}` selected markets are shown.",
        "",
        "| dataset | candidate | slice | markets | wins/losses | net | net/market | median ask |",
        "|---|---|---|---:|---:|---:|---:|---:|",
    ]
    if worst_slices.empty:
        lines.append("| none | none | none | 0 | 0/0 | 0.0c | 0.0c | NA |")
    else:
        for _, row in worst_slices.iterrows():
            lines.append(
                f"| {row['dataset']} | `{row['candidate']}` | {row['group_type']}=`{row['group']}` | "
                f"{int(row['markets'])} | {int(row['wins'])}/{int(row['losses'])} | "
                f"{fmt_cents(row['net_pnl_cents'])} | {fmt_cents(row['net_per_market_cents'])} | "
                f"{fmt_cents(row['median_ask'])} |"
            )

    lines += ["", "## Read", ""]
    if combined["robust"].any():
        best = combined[combined["robust"]].iloc[0]
        lines.append(f"- Best robust diagnostic row: `{best['candidate']}`.")
    else:
        lines.append("- No causal hazard-threshold row clears the combined coverage, split, OOS, and block-stability gate.")
    lines.append("- Do not promote or lock a scanned row without fresh strict live registration.")
    REPORT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    generated = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%SZ")
    summary_rows: List[Dict[str, Any]] = []
    block_rows: List[Dict[str, Any]] = []
    slice_rows: List[Dict[str, Any]] = []
    for dataset, loader in [("current", load_side_rows), ("v21", load_v21_side_rows)]:
        side_rows = add_blend_scores(loader())
        base = market_base(side_rows)
        for candidate in base_scan.CANDIDATES:
            selected = causal_combined_selected(base, side_rows, candidate)
            summary_rows.append(base_scan.flatten_summary(dataset, candidate, base, selected))
            block_rows.extend(base_scan.block_rows(dataset, candidate, base, selected))
            slice_rows.extend(base_scan.slice_rows(dataset, candidate, selected))

    summary = pd.DataFrame(summary_rows)
    blocks = pd.DataFrame(block_rows)
    slices = pd.DataFrame(slice_rows)
    summary.to_csv(SUMMARY_CSV, index=False)
    blocks.to_csv(BLOCK_CSV, index=False)
    slices.to_csv(SLICE_CSV, index=False)
    combined = combined_table(summary, blocks)
    payload = {
        "generated_utc": generated,
        "market_coverage_floor": MARKET_COVERAGE_FLOOR,
        "positive_block_rate_floor": base_scan.POSITIVE_BLOCK_RATE_FLOOR,
        "combined": clean_json_local(combined.to_dict(orient="records")),
        "summary": clean_json_local(summary.to_dict(orient="records")),
        "blocks": clean_json_local(blocks.to_dict(orient="records")),
        "slices": clean_json_local(slices.to_dict(orient="records")),
    }
    REPORT_JSON.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    (OUT_DIR / f"hazard_causal_threshold_stability_scan_{generated}.json").write_text(
        REPORT_JSON.read_text(encoding="utf-8"),
        encoding="utf-8",
    )
    write_report(generated, summary, blocks, slices)
    (OUT_DIR / f"hazard_causal_threshold_stability_scan_{generated}.md").write_text(
        REPORT_MD.read_text(encoding="utf-8"),
        encoding="utf-8",
    )
    print("Causal hazard threshold stability scan complete")
    print(f"candidates={len(base_scan.CANDIDATES)} summary_rows={len(summary)}")
    print(f"report={REPORT_MD}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
