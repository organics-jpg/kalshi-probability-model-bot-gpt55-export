"""Hazard-primary fallback scan for BTC 15m fair value.

The hazard-mean touch80 trial has started profitable but temporarily fell below
the 80% observed trade-rate target after skipping an open market. This probe
tests a simple architecture: take the hazard signal when it fires, otherwise
fall back to a high-coverage fair-value prior.

Research-only: no orders are submitted and no bot files or live processes are
modified. Any passing row must be forward-locked before use.
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

import pandas as pd

from probe_cross_dataset_interval_frontier import load_v21_side_rows
from probe_cross_dataset_profit_frontier import enrich_selected, fmt_cents, fmt_roi, split_metric
from probe_market_interval_80coverage import (
    MARKET_COVERAGE_FLOOR,
    OUT_DIR,
    choose_decision_sides,
    clean_json,
    load_side_rows,
    market_base,
    pct,
)
from probe_physics_probability_blend_audit import add_blend_scores
from probe_profit_touch_hazard_frontier import HazardPolicy, gate_mask as touch_gate_mask


REPORT_MD = OUT_DIR / "hazard_fallback_frontier_latest.md"
REPORT_JSON = OUT_DIR / "hazard_fallback_frontier_latest.json"
CSV_LATEST = OUT_DIR / "hazard_fallback_frontier_latest.csv"

HAZARD = HazardPolicy("hazard_discounted_mean_15", 0.45, 0.0, 80.0, 60.0, "touch_loss15<=0.80")


@dataclass(frozen=True)
class FallbackSpec:
    name: str
    chooser: str
    min_score: float
    ask_max: float
    min_seconds_to_close: float
    edge_floor_cents: Optional[float] = None
    max_seconds_to_close: Optional[float] = None

    @property
    def label(self) -> str:
        edge = f"; fair_edge>={self.edge_floor_cents:g}c" if self.edge_floor_cents is not None else ""
        max_sec = f"; sec<={self.max_seconds_to_close:g}" if self.max_seconds_to_close is not None else ""
        return f"hazard_primary_else_{self.name}: {self.chooser}>={self.min_score:g}{edge}; ask<={self.ask_max:g}; sec>={self.min_seconds_to_close:g}{max_sec}"


FALLBACKS = [
    FallbackSpec("logit_edge10", "blend_logit_book_rv_hazard_mean", 0.0, 95.0, 60.0, -10.0),
    FallbackSpec("logit_thresh55_edge15", "blend_logit_book_rv_hazard_mean", 0.55, 95.0, 60.0, -15.0),
    FallbackSpec("logit_thresh55_edge15_wait10m", "blend_logit_book_rv_hazard_mean", 0.55, 95.0, 60.0, -15.0, 600.0),
    FallbackSpec("logit_thresh55_edge15_wait8m", "blend_logit_book_rv_hazard_mean", 0.55, 95.0, 60.0, -15.0, 480.0),
    FallbackSpec("logit_thresh55_edge15_wait6m", "blend_logit_book_rv_hazard_mean", 0.55, 95.0, 60.0, -15.0, 360.0),
    FallbackSpec("book60", "book_p_side", 0.60, 95.0, 60.0, None),
    FallbackSpec("score_min60", "score_min_book_rv15", 0.60, 95.0, 60.0, None),
]


def clean_json_local(value: Any) -> Any:
    if isinstance(value, pd.Timestamp):
        return value.isoformat()
    if isinstance(value, dict):
        return {str(k): clean_json_local(v) for k, v in value.items()}
    if isinstance(value, list):
        return [clean_json_local(v) for v in value]
    return clean_json(value)


def first_market_rows(rows: pd.DataFrame) -> pd.DataFrame:
    if rows.empty:
        return rows.copy()
    return (
        rows.sort_values(["market", "entry_dt"])
        .groupby("market", as_index=False, sort=False)
        .first()
        .sort_values(["entry_dt", "market"])
        .reset_index(drop=True)
    )


def hazard_selected(base: pd.DataFrame, side_rows: pd.DataFrame) -> pd.DataFrame:
    rows = side_rows.merge(base[["market", "split"]], on="market", how="inner")
    chosen = choose_decision_sides(rows, HAZARD.chooser)
    if chosen.empty:
        return chosen
    selected = chosen[touch_gate_mask(chosen, HAZARD)].copy()
    selected["selector"] = "hazard_primary"
    return first_market_rows(enrich_selected(selected))


def fallback_selected(base: pd.DataFrame, side_rows: pd.DataFrame, spec: FallbackSpec) -> pd.DataFrame:
    rows = side_rows.merge(base[["market", "split"]], on="market", how="inner")
    chosen = choose_decision_sides(rows, spec.chooser)
    if chosen.empty:
        return chosen
    chosen = enrich_selected(chosen)
    scores = pd.to_numeric(chosen[spec.chooser], errors="coerce")
    mask = (
        scores.ge(spec.min_score)
        & pd.to_numeric(chosen["ask_cents"], errors="coerce").le(spec.ask_max)
        & pd.to_numeric(chosen["seconds_to_close"], errors="coerce").ge(spec.min_seconds_to_close)
    )
    if spec.max_seconds_to_close is not None:
        mask &= pd.to_numeric(chosen["seconds_to_close"], errors="coerce").le(spec.max_seconds_to_close)
    if spec.edge_floor_cents is not None:
        chosen["fair_edge_cents"] = 100.0 * scores - pd.to_numeric(chosen["entry_cost_cents"], errors="coerce")
        mask &= chosen["fair_edge_cents"].ge(spec.edge_floor_cents)
    selected = chosen[mask].copy()
    selected["selector"] = f"fallback_{spec.name}"
    return first_market_rows(selected)


def combined_selected(base: pd.DataFrame, side_rows: pd.DataFrame, spec: FallbackSpec) -> pd.DataFrame:
    primary = hazard_selected(base, side_rows)
    fallback = fallback_selected(base, side_rows, spec)
    if primary.empty:
        return fallback
    primary_markets = set(primary["market"].astype(str))
    fallback = fallback[~fallback["market"].astype(str).isin(primary_markets)].copy()
    return pd.concat([primary, fallback], ignore_index=True, sort=False).sort_values(["entry_dt", "market"]).reset_index(drop=True)


def metrics_for(base: pd.DataFrame, selected: pd.DataFrame) -> Dict[str, Dict[str, Any]]:
    return {split: split_metric(base, selected, split) for split in ["all", "train", "validation", "holdout"]}


def flatten(spec: FallbackSpec, current: Dict[str, Dict[str, Any]], v21: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
    row: Dict[str, Any] = {"fallback": spec.name, "label": spec.label}
    for prefix, metrics in [("current", current), ("v21", v21)]:
        for split, metric in metrics.items():
            for key, value in metric.items():
                row[f"{prefix}_{split}_{key}"] = value
    row["combined_all_net_pnl_cents"] = (row["current_all_net_pnl_cents"] or 0.0) + (row["v21_all_net_pnl_cents"] or 0.0)
    row["min_all_coverage"] = min(row["current_all_coverage"] or 0.0, row["v21_all_coverage"] or 0.0)
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
    row["both_all_positive"] = (row["current_all_net_pnl_cents"] or 0.0) > 0.0 and (row["v21_all_net_pnl_cents"] or 0.0) > 0.0
    return row


def scan() -> tuple[pd.DataFrame, Dict[str, Any]]:
    current_side = add_blend_scores(load_side_rows())
    v21_side = add_blend_scores(load_v21_side_rows())
    current_base = market_base(current_side)
    v21_base = market_base(v21_side)
    rows: List[Dict[str, Any]] = []
    for spec in FALLBACKS:
        current_selected = combined_selected(current_base, current_side, spec)
        v21_selected = combined_selected(v21_base, v21_side, spec)
        rows.append(flatten(spec, metrics_for(current_base, current_selected), metrics_for(v21_base, v21_selected)))
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
    return (
        f"| `{row['label']}` | {fmt_cents(row['combined_all_net_pnl_cents'])} | "
        f"{fmt_cents(row['current_all_net_pnl_cents'])}/{fmt_roi(row['current_all_net_roi_on_cost'])} | "
        f"{pct(row['current_all_accuracy'])}/{pct(row['current_all_coverage'])} | "
        f"{fmt_cents(row['v21_all_net_pnl_cents'])}/{fmt_roi(row['v21_all_net_roi_on_cost'])} | "
        f"{pct(row['v21_all_accuracy'])}/{pct(row['v21_all_coverage'])} | "
        f"{pct(row['min_oos_coverage'])} | {row['both_oos_positive']} | {row['strict_80_oos_coverage_pass']} |"
    )


def write_report(generated: str, frame: pd.DataFrame, diagnostics: Dict[str, Any]) -> None:
    strict = frame[frame["both_oos_positive"] & frame["strict_80_oos_coverage_pass"] & frame["both_all_positive"]]
    lines = [
        "# Hazard Fallback Frontier",
        "",
        f"Generated UTC: `{generated}`",
        "",
        "## Scope",
        "",
        "- Research-only scan; no orders are submitted and no bot files or live processes are touched.",
        "- Uses hazard-mean touch80 as primary; if it skips a market, tries a high-coverage fallback.",
        "- Any passing row must be forward-locked before use.",
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
        "| policy | combined net | current net/ROI | current acc/cov | v21 net/ROI | v21 acc/cov | min OOS cov | OOS positive | strict cov |",
        "|---|---:|---:|---:|---:|---:|---:|---|---|",
    ]
    for _, row in frame.iterrows():
        lines.append(table_row(row.to_dict()))
    lines += ["", "## Read", ""]
    if strict.empty:
        lines.append("- No hazard-primary fallback row is positive on validation/holdout for both datasets at strict 80% OOS coverage.")
    else:
        best = strict.iloc[0]
        lines.append(
            f"- Best strict diagnostic row is `{best['label']}` with combined all-ledger net "
            f"{fmt_cents(best['combined_all_net_pnl_cents'])}."
        )
    for path in [REPORT_MD, OUT_DIR / f"hazard_fallback_frontier_{generated}.md"]:
        path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    generated = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%SZ")
    frame, diagnostics = scan()
    frame.to_csv(CSV_LATEST, index=False)
    (OUT_DIR / f"hazard_fallback_frontier_{generated}.csv").write_text(CSV_LATEST.read_text(encoding="utf-8"), encoding="utf-8")
    write_report(generated, frame, diagnostics)
    payload = {"generated_utc": generated, "diagnostics": diagnostics, "rows": frame.to_dict("records")}
    for path in [REPORT_JSON, OUT_DIR / f"hazard_fallback_frontier_{generated}.json"]:
        path.write_text(json.dumps(clean_json_local(payload), indent=2, sort_keys=True), encoding="utf-8")
    print("Hazard fallback frontier complete")
    print(f"rows={len(frame)}")
    print(f"report={REPORT_MD}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
