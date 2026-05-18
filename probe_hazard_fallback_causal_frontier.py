"""Causal hazard-primary fallback scan for BTC 15m fair value.

The first hazard-fallback scan was useful for model design, but its arbitration
was optimistic: if hazard appeared anywhere in a market, it removed the fallback
row even when fallback would have appeared first in live time. This probe scores
the physically tradable version: choose the earliest eligible primary/fallback
row per market, with hazard only winning ties.

Research-only: no orders are submitted and no bot files or live processes are
modified. Any passing row must be forward-locked and validated live.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any, Dict, List

import pandas as pd

from probe_cross_dataset_interval_frontier import load_v21_side_rows
from probe_cross_dataset_profit_frontier import fmt_cents, fmt_roi
from probe_hazard_fallback_frontier import (
    FALLBACKS,
    FallbackSpec,
    clean_json_local,
    combined_selected as noncausal_combined_selected,
    fallback_selected,
    hazard_selected,
    metrics_for,
)
from probe_market_interval_80coverage import (
    MARKET_COVERAGE_FLOOR,
    OUT_DIR,
    clean_json,
    load_side_rows,
    market_base,
    pct,
)
from probe_physics_probability_blend_audit import add_blend_scores


REPORT_MD = OUT_DIR / "hazard_fallback_causal_frontier_latest.md"
REPORT_JSON = OUT_DIR / "hazard_fallback_causal_frontier_latest.json"
CSV_LATEST = OUT_DIR / "hazard_fallback_causal_frontier_latest.csv"


def first_causal_rows(primary: pd.DataFrame, fallback: pd.DataFrame) -> pd.DataFrame:
    frames: List[pd.DataFrame] = []
    if not primary.empty:
        p = primary.copy()
        p["selector_priority"] = 0
        frames.append(p)
    if not fallback.empty:
        f = fallback.copy()
        f["selector_priority"] = 1
        frames.append(f)
    if not frames:
        return primary.iloc[0:0].copy()
    rows = pd.concat(frames, ignore_index=True, sort=False)
    rows["entry_dt"] = pd.to_datetime(rows["entry_dt"], utc=True, errors="coerce")
    selected = (
        rows.sort_values(["market", "entry_dt", "selector_priority"])
        .groupby("market", as_index=False, sort=False)
        .first()
        .sort_values(["entry_dt", "market"])
        .reset_index(drop=True)
    )
    return selected.drop(columns=["selector_priority"], errors="ignore")


def causal_combined_selected(base: pd.DataFrame, side_rows: pd.DataFrame, spec: FallbackSpec) -> pd.DataFrame:
    primary = hazard_selected(base, side_rows)
    fallback = fallback_selected(base, side_rows, spec)
    return first_causal_rows(primary, fallback)


def conflict_stats(primary: pd.DataFrame, fallback: pd.DataFrame, selected: pd.DataFrame) -> Dict[str, Any]:
    if primary.empty or fallback.empty:
        both = pd.DataFrame()
    else:
        both = primary[["market", "entry_dt"]].merge(
            fallback[["market", "entry_dt"]],
            on="market",
            how="inner",
            suffixes=("_primary", "_fallback"),
        )
    if both.empty:
        fallback_before_primary = 0
        primary_before_fallback = 0
        both_count = 0
    else:
        primary_dt = pd.to_datetime(both["entry_dt_primary"], utc=True, errors="coerce")
        fallback_dt = pd.to_datetime(both["entry_dt_fallback"], utc=True, errors="coerce")
        fallback_before_primary = int(fallback_dt.lt(primary_dt).sum())
        primary_before_fallback = int(primary_dt.lt(fallback_dt).sum())
        both_count = int(len(both))
    selector_counts = selected.get("selector", pd.Series(dtype=str)).astype(str).value_counts().to_dict()
    return {
        "both_primary_and_fallback": both_count,
        "fallback_before_primary": fallback_before_primary,
        "primary_before_fallback": primary_before_fallback,
        "selected_hazard_primary": int(selector_counts.get("hazard_primary", 0)),
        "selected_fallback": int(sum(count for selector, count in selector_counts.items() if selector.startswith("fallback_"))),
    }


def flatten(
    spec: FallbackSpec,
    current: Dict[str, Dict[str, Any]],
    v21: Dict[str, Dict[str, Any]],
    current_noncausal: Dict[str, Dict[str, Any]],
    v21_noncausal: Dict[str, Dict[str, Any]],
    current_conflicts: Dict[str, Any],
    v21_conflicts: Dict[str, Any],
) -> Dict[str, Any]:
    row: Dict[str, Any] = {"fallback": spec.name, "label": spec.label}
    for prefix, metrics in [("current", current), ("v21", v21)]:
        for split, metric in metrics.items():
            for key, value in metric.items():
                row[f"{prefix}_{split}_{key}"] = value
    row["combined_all_net_pnl_cents"] = (row["current_all_net_pnl_cents"] or 0.0) + (
        row["v21_all_net_pnl_cents"] or 0.0
    )
    row["min_oos_coverage"] = min(
        row["current_validation_coverage"] or 0.0,
        row["current_holdout_coverage"] or 0.0,
        row["v21_validation_coverage"] or 0.0,
        row["v21_holdout_coverage"] or 0.0,
    )
    row["strict_80_oos_coverage_pass"] = row["min_oos_coverage"] >= MARKET_COVERAGE_FLOOR
    row["both_oos_positive"] = all(
        (row[f"{dataset}_{split}_net_pnl_cents"] or 0.0) > 0.0
        for dataset in ["current", "v21"]
        for split in ["validation", "holdout"]
    )
    row["both_all_positive"] = (row["current_all_net_pnl_cents"] or 0.0) > 0.0 and (
        row["v21_all_net_pnl_cents"] or 0.0
    ) > 0.0
    row["current_all_noncausal_gap_cents"] = (current_noncausal["all"]["net_pnl_cents"] or 0.0) - (
        current["all"]["net_pnl_cents"] or 0.0
    )
    row["v21_all_noncausal_gap_cents"] = (v21_noncausal["all"]["net_pnl_cents"] or 0.0) - (
        v21["all"]["net_pnl_cents"] or 0.0
    )
    for prefix, stats in [("current", current_conflicts), ("v21", v21_conflicts)]:
        for key, value in stats.items():
            row[f"{prefix}_{key}"] = value
    return row


def scan() -> tuple[pd.DataFrame, Dict[str, Any]]:
    current_side = add_blend_scores(load_side_rows())
    v21_side = add_blend_scores(load_v21_side_rows())
    current_base = market_base(current_side)
    v21_base = market_base(v21_side)
    rows: List[Dict[str, Any]] = []
    for spec in FALLBACKS:
        current_primary = hazard_selected(current_base, current_side)
        current_fallback = fallback_selected(current_base, current_side, spec)
        current_selected = first_causal_rows(current_primary, current_fallback)
        current_noncausal = noncausal_combined_selected(current_base, current_side, spec)

        v21_primary = hazard_selected(v21_base, v21_side)
        v21_fallback = fallback_selected(v21_base, v21_side, spec)
        v21_selected = first_causal_rows(v21_primary, v21_fallback)
        v21_noncausal = noncausal_combined_selected(v21_base, v21_side, spec)

        rows.append(
            flatten(
                spec,
                metrics_for(current_base, current_selected),
                metrics_for(v21_base, v21_selected),
                metrics_for(current_base, current_noncausal),
                metrics_for(v21_base, v21_noncausal),
                conflict_stats(current_primary, current_fallback, current_selected),
                conflict_stats(v21_primary, v21_fallback, v21_selected),
            )
        )
    frame = pd.DataFrame(rows).sort_values(
        ["both_oos_positive", "strict_80_oos_coverage_pass", "combined_all_net_pnl_cents"],
        ascending=[False, False, False],
    )
    diagnostics = {
        "current_markets": int(len(current_base)),
        "v21_markets": int(len(v21_base)),
        "rows": int(len(frame)),
    }
    return frame.reset_index(drop=True), diagnostics


def table_row(row: Dict[str, Any]) -> str:
    total_gap = (row["current_all_noncausal_gap_cents"] or 0.0) + (row["v21_all_noncausal_gap_cents"] or 0.0)
    conflict = f"{row['current_fallback_before_primary']}/{row['v21_fallback_before_primary']}"
    return (
        f"| `{row['label']}` | {fmt_cents(row['combined_all_net_pnl_cents'])} | "
        f"{fmt_cents(total_gap)} | "
        f"{fmt_cents(row['current_all_net_pnl_cents'])}/{fmt_roi(row['current_all_net_roi_on_cost'])} | "
        f"{pct(row['current_all_accuracy'])}/{pct(row['current_all_coverage'])} | "
        f"{fmt_cents(row['v21_all_net_pnl_cents'])}/{fmt_roi(row['v21_all_net_roi_on_cost'])} | "
        f"{pct(row['v21_all_accuracy'])}/{pct(row['v21_all_coverage'])} | "
        f"{pct(row['min_oos_coverage'])} | {conflict} | {row['both_oos_positive']} | {row['strict_80_oos_coverage_pass']} |"
    )


def write_report(generated: str, frame: pd.DataFrame, diagnostics: Dict[str, Any]) -> None:
    strict = frame[frame["both_oos_positive"] & frame["strict_80_oos_coverage_pass"] & frame["both_all_positive"]]
    lines = [
        "# Causal Hazard Fallback Frontier",
        "",
        f"Generated UTC: `{generated}`",
        "",
        "## Scope",
        "",
        "- Research-only scan; no orders are submitted and no bot files or live processes are touched.",
        "- Scores the first eligible primary/fallback signal by timestamp per market.",
        "- Noncausal gap is the extra P&L shown by the earlier optimistic scan that let later hazard suppress earlier fallback.",
        "",
        "## Diagnostics",
        "",
        f"- Current markets: {diagnostics['current_markets']}",
        f"- V21 markets: {diagnostics['v21_markets']}",
        f"- Rows scanned: {diagnostics['rows']}",
        f"- Strict positive OOS rows: {len(strict)}",
        "",
        "## Rows",
        "",
        "| policy | causal combined net | noncausal gap | current net/ROI | current acc/cov | v21 net/ROI | v21 acc/cov | min OOS cov | fallback-before-primary current/v21 | OOS positive | strict cov |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---|---|",
    ]
    for _, row in frame.iterrows():
        lines.append(table_row(row.to_dict()))
    lines += ["", "## Read", ""]
    if strict.empty:
        lines.append("- No causal hazard-primary fallback row is positive on validation/holdout for both datasets at strict 80% OOS coverage.")
    else:
        best = strict.iloc[0]
        lines.append(
            f"- Best strict causal row is `{best['label']}` with combined all-ledger net "
            f"{fmt_cents(best['combined_all_net_pnl_cents'])}."
        )
    worst_gap = frame.sort_values(
        ["current_all_noncausal_gap_cents", "v21_all_noncausal_gap_cents"],
        ascending=[False, False],
    ).iloc[0]
    lines.append(
        f"- Largest current noncausal optimism gap is `{worst_gap['label']}` at "
        f"{fmt_cents(worst_gap['current_all_noncausal_gap_cents'])} current / "
        f"{fmt_cents(worst_gap['v21_all_noncausal_gap_cents'])} v21."
    )
    for path in [REPORT_MD, OUT_DIR / f"hazard_fallback_causal_frontier_{generated}.md"]:
        path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def clean_payload(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(k): clean_payload(v) for k, v in value.items()}
    if isinstance(value, list):
        return [clean_payload(v) for v in value]
    return clean_json_local(clean_json(value))


def main() -> int:
    generated = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%SZ")
    frame, diagnostics = scan()
    frame.to_csv(CSV_LATEST, index=False)
    (OUT_DIR / f"hazard_fallback_causal_frontier_{generated}.csv").write_text(
        CSV_LATEST.read_text(encoding="utf-8"),
        encoding="utf-8",
    )
    write_report(generated, frame, diagnostics)
    payload = {"generated_utc": generated, "diagnostics": diagnostics, "rows": frame.to_dict("records")}
    for path in [REPORT_JSON, OUT_DIR / f"hazard_fallback_causal_frontier_{generated}.json"]:
        path.write_text(json.dumps(clean_payload(payload), indent=2, sort_keys=True), encoding="utf-8")
    print("Causal hazard fallback frontier complete")
    print(f"rows={len(frame)}")
    print(f"report={REPORT_MD}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
