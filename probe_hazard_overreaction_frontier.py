"""Hazard overreaction frontier for BTC 15m fair value.

Two live hazard losses exposed different failure modes:

1. An early medium-confidence signal.
2. A late, expensive, high-confidence signal after a large normalized move.

This probe tests a physics-motivated cap: path hazard can become an
overreaction signal when the state is too extended or too expensive. It scans a
small family of upper caps on hazard score, ask, and normalized margin, while
requiring >=80% market coverage in current and v21 ledgers.

Research-only: no orders are submitted and no bot files or live processes are
modified. Passing rows are diagnostic and must be forward-locked before use.
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
from probe_profit_touch_hazard_frontier import HazardPolicy, add_touch_hazard_scores, gate_mask as touch_gate_mask


REPORT_MD = OUT_DIR / "hazard_overreaction_frontier_latest.md"
REPORT_JSON = OUT_DIR / "hazard_overreaction_frontier_latest.json"
CSV_LATEST = OUT_DIR / "hazard_overreaction_frontier_latest.csv"

BASE = HazardPolicy("hazard_discounted_mean_15", 0.45, 0.0, 80.0, 60.0, "touch_loss15<=0.80")


@dataclass(frozen=True)
class OverreactionSpec:
    name: str
    ask_max: float
    max_score: Optional[float] = None
    max_margin_sigma: Optional[float] = None
    max_seconds_to_close: Optional[float] = None

    @property
    def label(self) -> str:
        parts = [
            f"hazard>=0.45",
            f"ask<={self.ask_max:g}",
            "sec>=60",
            "touch_loss<=0.80",
        ]
        if self.max_score is not None:
            parts.append(f"hazard<={self.max_score:g}")
        if self.max_margin_sigma is not None:
            parts.append(f"margin_sigma<={self.max_margin_sigma:g}")
        if self.max_seconds_to_close is not None:
            parts.append(f"sec<={self.max_seconds_to_close:g}")
        return "; ".join(parts)


SPECS = [
    OverreactionSpec("base", 80.0),
    OverreactionSpec("ask75", 75.0),
    OverreactionSpec("score65", 80.0, max_score=0.65),
    OverreactionSpec("score60", 80.0, max_score=0.60),
    OverreactionSpec("score55", 80.0, max_score=0.55),
    OverreactionSpec("margin75", 80.0, max_margin_sigma=0.75),
    OverreactionSpec("margin65", 80.0, max_margin_sigma=0.65),
    OverreactionSpec("ask75_score65", 75.0, max_score=0.65),
    OverreactionSpec("ask75_margin75", 75.0, max_margin_sigma=0.75),
    OverreactionSpec("score65_margin75", 80.0, max_score=0.65, max_margin_sigma=0.75),
    OverreactionSpec("ask75_score65_margin75", 75.0, max_score=0.65, max_margin_sigma=0.75),
    OverreactionSpec("sec840_score65", 80.0, max_score=0.65, max_seconds_to_close=840.0),
    OverreactionSpec("sec840_margin75", 80.0, max_margin_sigma=0.75, max_seconds_to_close=840.0),
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


def selected_rows(base: pd.DataFrame, side_rows: pd.DataFrame, spec: OverreactionSpec) -> pd.DataFrame:
    rows = side_rows.merge(base[["market", "split"]], on="market", how="inner")
    chosen = choose_decision_sides(rows, BASE.chooser)
    if chosen.empty:
        return chosen.copy()
    selected = chosen[touch_gate_mask(chosen, BASE)].copy()
    if selected.empty:
        return selected
    selected = selected[pd.to_numeric(selected["ask_cents"], errors="coerce").le(spec.ask_max)].copy()
    if spec.max_score is not None and not selected.empty:
        selected = selected[
            pd.to_numeric(selected[BASE.chooser], errors="coerce").le(spec.max_score)
        ].copy()
    if spec.max_margin_sigma is not None and not selected.empty:
        selected = selected[
            pd.to_numeric(selected["margin_per_rv_sigma_15m"], errors="coerce").le(spec.max_margin_sigma)
        ].copy()
    if spec.max_seconds_to_close is not None and not selected.empty:
        selected = selected[
            pd.to_numeric(selected["seconds_to_close"], errors="coerce").le(spec.max_seconds_to_close)
        ].copy()
    if selected.empty:
        return selected
    selected = first_market_rows(enrich_selected(selected))
    selected["policy"] = spec.name
    return selected


def metrics_for(base: pd.DataFrame, selected: pd.DataFrame) -> Dict[str, Dict[str, Any]]:
    return {split: split_metric(base, selected, split) for split in ["all", "train", "validation", "holdout"]}


def flatten(spec: OverreactionSpec, current: Dict[str, Dict[str, Any]], v21: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
    row: Dict[str, Any] = {"policy": spec.name, "label": spec.label}
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
    return row


def scan() -> tuple[pd.DataFrame, Dict[str, Any]]:
    current_side = add_touch_hazard_scores(load_side_rows())
    v21_side = add_touch_hazard_scores(load_v21_side_rows())
    current_base = market_base(current_side)
    v21_base = market_base(v21_side)
    rows: List[Dict[str, Any]] = []
    for spec in SPECS:
        current_selected = selected_rows(current_base, current_side, spec)
        v21_selected = selected_rows(v21_base, v21_side, spec)
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
        "# Hazard Overreaction Frontier",
        "",
        f"Generated UTC: `{generated}`",
        "",
        "## Scope",
        "",
        "- Research-only scan; no orders are submitted and no bot files or live processes are touched.",
        "- Tests whether high-score / high-price / high-extension hazard states are overreaction rather than confirmation.",
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
        lines.append("- No overreaction cap is positive on validation/holdout for both datasets at strict 80% OOS coverage.")
    else:
        best = strict.iloc[0]
        lines.append(
            f"- Best strict diagnostic row is `{best['label']}` with combined all-ledger net "
            f"{fmt_cents(best['combined_all_net_pnl_cents'])}."
        )
    for path in [REPORT_MD, OUT_DIR / f"hazard_overreaction_frontier_{generated}.md"]:
        path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    generated = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%SZ")
    frame, diagnostics = scan()
    frame.to_csv(CSV_LATEST, index=False)
    (OUT_DIR / f"hazard_overreaction_frontier_{generated}.csv").write_text(
        CSV_LATEST.read_text(encoding="utf-8"),
        encoding="utf-8",
    )
    write_report(generated, frame, diagnostics)
    payload = {"generated_utc": generated, "diagnostics": diagnostics, "rows": frame.to_dict("records")}
    for path in [REPORT_JSON, OUT_DIR / f"hazard_overreaction_frontier_{generated}.json"]:
        path.write_text(json.dumps(clean_json_local(payload), indent=2, sort_keys=True), encoding="utf-8")
    print("Hazard overreaction frontier complete")
    print(f"rows={len(frame)}")
    print(f"report={REPORT_MD}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
