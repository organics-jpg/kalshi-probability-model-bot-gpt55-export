"""Hazard primary maturity scan for BTC 15m fair value.

The first live loss for hazard_mean_touch80 occurred on an extremely early row,
with roughly 14.4 minutes left. This probe tests whether the primary
first-passage signal needs a causal maturation window before it can be trusted,
and whether delayed fallbacks can preserve the >=80% recurring-market target.

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
from probe_physics_probability_blend_audit import add_blend_scores
from probe_profit_touch_hazard_frontier import HazardPolicy, gate_mask as touch_gate_mask


REPORT_MD = OUT_DIR / "hazard_primary_maturity_frontier_latest.md"
REPORT_JSON = OUT_DIR / "hazard_primary_maturity_frontier_latest.json"
CSV_LATEST = OUT_DIR / "hazard_primary_maturity_frontier_latest.csv"

BASE_HAZARD = HazardPolicy("hazard_discounted_mean_15", 0.45, 0.0, 80.0, 60.0, "touch_loss15<=0.80")


@dataclass(frozen=True)
class PrimarySpec:
    name: str
    max_seconds_to_close: Optional[float]

    @property
    def label(self) -> str:
        if self.max_seconds_to_close is None:
            return "primary=no_cap"
        elapsed = 900.0 - self.max_seconds_to_close
        return f"primary=wait{elapsed:g}s; sec<={self.max_seconds_to_close:g}"


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
        return f"fallback={self.name}:{self.chooser}>={self.min_score:g}{edge}; ask<={self.ask_max:g}; sec>={self.min_seconds_to_close:g}{max_sec}"


PRIMARY_SPECS = [
    PrimarySpec("no_cap", None),
    PrimarySpec("wait30s", 870.0),
    PrimarySpec("wait60s", 840.0),
    PrimarySpec("wait90s", 810.0),
    PrimarySpec("wait120s", 780.0),
    PrimarySpec("wait180s", 720.0),
    PrimarySpec("wait300s", 600.0),
]

FALLBACK_SPECS: List[Optional[FallbackSpec]] = [
    None,
    FallbackSpec("score60", "score_min_book_rv15", 0.60, 95.0, 60.0),
    FallbackSpec("score60_wait8m", "score_min_book_rv15", 0.60, 95.0, 60.0, None, 480.0),
    FallbackSpec("logit55_edge15_wait8m", "blend_logit_book_rv_hazard_mean", 0.55, 95.0, 60.0, -15.0, 480.0),
    FallbackSpec("logit55_edge15_wait6m", "blend_logit_book_rv_hazard_mean", 0.55, 95.0, 60.0, -15.0, 360.0),
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
    return (
        rows.sort_values(["market", "entry_dt", "selector_priority"])
        .groupby("market", as_index=False, sort=False)
        .first()
        .sort_values(["entry_dt", "market"])
        .reset_index(drop=True)
        .drop(columns=["selector_priority"], errors="ignore")
    )


def primary_selected(base: pd.DataFrame, side_rows: pd.DataFrame, spec: PrimarySpec) -> pd.DataFrame:
    rows = side_rows.merge(base[["market", "split"]], on="market", how="inner")
    chosen = choose_decision_sides(rows, BASE_HAZARD.chooser)
    if chosen.empty:
        return chosen.copy()
    selected = chosen[touch_gate_mask(chosen, BASE_HAZARD)].copy()
    if spec.max_seconds_to_close is not None and not selected.empty:
        selected = selected[
            pd.to_numeric(selected["seconds_to_close"], errors="coerce").le(spec.max_seconds_to_close)
        ].copy()
    if selected.empty:
        return selected
    selected = first_market_rows(enrich_selected(selected))
    selected["selector"] = f"hazard_{spec.name}"
    return selected


def fallback_selected(base: pd.DataFrame, side_rows: pd.DataFrame, spec: Optional[FallbackSpec]) -> pd.DataFrame:
    if spec is None:
        return side_rows.iloc[0:0].copy()
    rows = side_rows.merge(base[["market", "split"]], on="market", how="inner")
    chosen = choose_decision_sides(rows, spec.chooser)
    if chosen.empty:
        return chosen.copy()
    chosen = enrich_selected(chosen)
    scores = pd.to_numeric(chosen[spec.chooser], errors="coerce")
    chosen["fair_edge_cents"] = 100.0 * scores - pd.to_numeric(chosen["entry_cost_cents"], errors="coerce")
    mask = (
        scores.ge(spec.min_score)
        & pd.to_numeric(chosen["ask_cents"], errors="coerce").le(spec.ask_max)
        & pd.to_numeric(chosen["seconds_to_close"], errors="coerce").ge(spec.min_seconds_to_close)
    )
    if spec.max_seconds_to_close is not None:
        mask &= pd.to_numeric(chosen["seconds_to_close"], errors="coerce").le(spec.max_seconds_to_close)
    if spec.edge_floor_cents is not None:
        mask &= chosen["fair_edge_cents"].ge(spec.edge_floor_cents)
    selected = chosen[mask].copy()
    if selected.empty:
        return selected
    selected = first_market_rows(selected)
    selected["selector"] = f"fallback_{spec.name}"
    return selected


def selected_for(base: pd.DataFrame, side_rows: pd.DataFrame, primary: PrimarySpec, fallback: Optional[FallbackSpec]) -> pd.DataFrame:
    return first_causal_rows(
        primary_selected(base, side_rows, primary),
        fallback_selected(base, side_rows, fallback),
    )


def metrics_for(base: pd.DataFrame, selected: pd.DataFrame) -> Dict[str, Dict[str, Any]]:
    return {split: split_metric(base, selected, split) for split in ["all", "train", "validation", "holdout"]}


def flatten(primary: PrimarySpec, fallback: Optional[FallbackSpec], current: Dict[str, Dict[str, Any]], v21: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
    fallback_name = fallback.name if fallback is not None else "none"
    row: Dict[str, Any] = {
        "primary": primary.name,
        "fallback": fallback_name,
        "label": f"{primary.label}; {fallback.label if fallback is not None else 'fallback=none'}",
    }
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
    current_side = add_blend_scores(load_side_rows())
    v21_side = add_blend_scores(load_v21_side_rows())
    current_base = market_base(current_side)
    v21_base = market_base(v21_side)
    rows: List[Dict[str, Any]] = []
    for primary in PRIMARY_SPECS:
        for fallback in FALLBACK_SPECS:
            current_selected = selected_for(current_base, current_side, primary, fallback)
            v21_selected = selected_for(v21_base, v21_side, primary, fallback)
            rows.append(flatten(primary, fallback, metrics_for(current_base, current_selected), metrics_for(v21_base, v21_selected)))
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
        "# Hazard Primary Maturity Frontier",
        "",
        f"Generated UTC: `{generated}`",
        "",
        "## Scope",
        "",
        "- Research-only scan; no orders are submitted and no bot files or live processes are touched.",
        "- Tests whether the hazard primary should wait for elapsed path information before acting.",
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
        lines.append("- No maturity row is positive on validation/holdout for both datasets at strict 80% OOS coverage.")
    else:
        best = strict.iloc[0]
        lines.append(
            f"- Best strict diagnostic row is `{best['label']}` with combined all-ledger net "
            f"{fmt_cents(best['combined_all_net_pnl_cents'])}."
        )
    for path in [REPORT_MD, OUT_DIR / f"hazard_primary_maturity_frontier_{generated}.md"]:
        path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    generated = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%SZ")
    frame, diagnostics = scan()
    frame.to_csv(CSV_LATEST, index=False)
    (OUT_DIR / f"hazard_primary_maturity_frontier_{generated}.csv").write_text(
        CSV_LATEST.read_text(encoding="utf-8"),
        encoding="utf-8",
    )
    write_report(generated, frame, diagnostics)
    payload = {"generated_utc": generated, "diagnostics": diagnostics, "rows": frame.to_dict("records")}
    for path in [REPORT_JSON, OUT_DIR / f"hazard_primary_maturity_frontier_{generated}.json"]:
        path.write_text(json.dumps(clean_json_local(payload), indent=2, sort_keys=True), encoding="utf-8")
    print("Hazard primary maturity frontier complete")
    print(f"rows={len(frame)}")
    print(f"report={REPORT_MD}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
