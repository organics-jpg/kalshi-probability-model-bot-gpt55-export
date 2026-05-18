"""Hazard trigger-persistence frontier for BTC 15m markets.

Price caps address overpaying for certainty, but recent live losses also point
to reversal risk after a hazard trigger. This probe asks a more physical
question: after the first hazard trigger, does the same side need to persist for
a short causal window before the signal is tradable?

Research-only: no orders are submitted and no bot files or live processes are
modified. Passing rows are diagnostic and must be forward-locked before use.
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Dict, List

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


REPORT_LATEST = OUT_DIR / "hazard_trigger_persistence_frontier_latest.md"
JSON_LATEST = OUT_DIR / "hazard_trigger_persistence_frontier_latest.json"
CSV_LATEST = OUT_DIR / "hazard_trigger_persistence_frontier_latest.csv"

BASE = HazardPolicy("hazard_discounted_mean_15", 0.45, 0.0, 80.0, 60.0, "touch_loss15<=0.80")


@dataclass(frozen=True)
class PersistenceSpec:
    name: str
    ask_max: float
    delay_sec: float
    continuous_side: bool = True

    @property
    def label(self) -> str:
        parts = [
            "hazard>=0.45",
            f"ask<={self.ask_max:g}",
            "sec>=60",
            "touch_loss<=0.80",
            f"persist>={self.delay_sec:g}s",
        ]
        if self.continuous_side:
            parts.append("continuous_side")
        return "; ".join(parts)


def clean_json_local(value: Any) -> Any:
    if isinstance(value, pd.Timestamp):
        return value.isoformat()
    if isinstance(value, dict):
        return {str(k): clean_json_local(v) for k, v in value.items()}
    if isinstance(value, list):
        return [clean_json_local(v) for v in value]
    return clean_json(value)


def make_specs() -> List[PersistenceSpec]:
    specs: List[PersistenceSpec] = []
    for ask_max in [76.0, 80.0]:
        for delay in [0.0, 15.0, 30.0, 60.0, 120.0]:
            specs.append(PersistenceSpec(f"ask{ask_max:g}_persist{delay:g}", ask_max, delay))
    return specs


def base_gate(chosen: pd.DataFrame, ask_max: float) -> pd.Series:
    return touch_gate_mask(chosen, BASE) & pd.to_numeric(chosen["ask_cents"], errors="coerce").le(float(ask_max))


def first_persistent_rows(base: pd.DataFrame, side_rows: pd.DataFrame, spec: PersistenceSpec) -> pd.DataFrame:
    rows = side_rows.merge(base[["market", "split"]], on="market", how="inner")
    chosen = choose_decision_sides(rows, BASE.chooser)
    if chosen.empty:
        return chosen.copy()
    chosen = chosen.copy()
    chosen["entry_dt"] = pd.to_datetime(chosen["entry_dt"], utc=True, errors="coerce")
    chosen = chosen.dropna(subset=["entry_dt"]).sort_values(["market", "entry_dt"]).reset_index(drop=True)
    eligible = chosen[base_gate(chosen, spec.ask_max)].copy()
    if eligible.empty:
        return eligible

    selected_rows: list[pd.Series] = []
    chosen_by_market = {market: part.copy() for market, part in chosen.groupby("market", sort=False)}
    eligible_by_market = {market: part.copy() for market, part in eligible.groupby("market", sort=False)}
    for market, triggers in eligible_by_market.items():
        all_rows = chosen_by_market.get(market)
        if all_rows is None or all_rows.empty:
            continue
        accepted = None
        for _, trigger in triggers.iterrows():
            target_dt = trigger["entry_dt"] + pd.Timedelta(seconds=float(spec.delay_sec))
            same_side_later = triggers[
                triggers["side"].astype(str).eq(str(trigger["side"]))
                & pd.to_datetime(triggers["entry_dt"], utc=True, errors="coerce").ge(target_dt)
            ].copy()
            if same_side_later.empty:
                continue
            candidate = same_side_later.iloc[0]
            if spec.continuous_side and spec.delay_sec > 0:
                between = all_rows[
                    pd.to_datetime(all_rows["entry_dt"], utc=True, errors="coerce").between(
                        trigger["entry_dt"],
                        candidate["entry_dt"],
                        inclusive="both",
                    )
                ]
                if not between["side"].astype(str).eq(str(trigger["side"])).all():
                    continue
            accepted = candidate
            break
        if accepted is not None:
            selected_rows.append(accepted)

    if not selected_rows:
        return eligible.iloc[0:0].copy()
    selected = pd.DataFrame(selected_rows).sort_values(["entry_dt", "market"]).reset_index(drop=True)
    selected = enrich_selected(selected)
    selected["policy"] = spec.name
    return selected


def metrics_for(base: pd.DataFrame, selected: pd.DataFrame) -> Dict[str, Dict[str, Any]]:
    return {split: split_metric(base, selected, split) for split in ["all", "train", "validation", "holdout"]}


def flatten(spec: PersistenceSpec, current: Dict[str, Dict[str, Any]], v21: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
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
    for spec in make_specs():
        current_selected = first_persistent_rows(current_base, current_side, spec)
        v21_selected = first_persistent_rows(v21_base, v21_side, spec)
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
        "# Hazard Trigger Persistence Frontier",
        "",
        f"Generated UTC: `{generated}`",
        "",
        "## Scope",
        "",
        "- Research-only scan; no orders are submitted and no bot files or live processes are touched.",
        "- Tests whether hazard signals need same-side persistence after first trigger.",
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
        lines.append("- No persistence rule is positive on validation/holdout for both datasets at strict 80% OOS coverage.")
    else:
        best = strict.iloc[0]
        lines.append(
            f"- Best strict diagnostic row is `{best['label']}` with combined all-ledger net "
            f"{fmt_cents(best['combined_all_net_pnl_cents'])}."
        )
    for path in [REPORT_LATEST, OUT_DIR / f"hazard_trigger_persistence_frontier_{generated}.md"]:
        path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    generated = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%SZ")
    frame, diagnostics = scan()
    frame.to_csv(CSV_LATEST, index=False)
    frame.to_csv(OUT_DIR / f"hazard_trigger_persistence_frontier_{generated}.csv", index=False)
    write_report(generated, frame, diagnostics)
    payload = {"generated_utc": generated, "diagnostics": diagnostics, "rows": frame.to_dict("records")}
    for path in [JSON_LATEST, OUT_DIR / f"hazard_trigger_persistence_frontier_{generated}.json"]:
        path.write_text(json.dumps(clean_json_local(payload), indent=2, sort_keys=True), encoding="utf-8")
    print("Hazard trigger persistence frontier complete")
    print(f"rows={len(frame)}")
    print(f"report={REPORT_LATEST}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
