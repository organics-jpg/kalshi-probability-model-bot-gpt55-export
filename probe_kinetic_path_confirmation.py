"""Kinetic path-confirmation scan.

The fresh kinetic loss showed a fast side flip after the first eligible
snapshot. This diagnostic asks whether requiring the same side to remain the
chosen side for a short delay improves EV while preserving the user's
recurring-market coverage requirement.

Research-only: no orders are submitted and no bot files or live processes are
modified.
"""
from __future__ import annotations

import json
import math
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

import numpy as np
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
from probe_profit_kinetic_touch_fresh_validation import KINETIC_TOUCH_LOCK_PATH
from probe_profit_lock_time_boundary import effective_lock_dt
from probe_profit_touch_hazard_fresh_validation import policy_from_record
from probe_profit_touch_hazard_frontier import HazardPolicy, add_touch_hazard_scores, gate_mask as touch_gate_mask


REPORT_MD = OUT_DIR / "kinetic_path_confirmation_latest.md"
REPORT_JSON = OUT_DIR / "kinetic_path_confirmation_latest.json"
REPORT_CSV = OUT_DIR / "kinetic_path_confirmation_latest.csv"


@dataclass(frozen=True)
class ConfirmSpec:
    delay_sec: float
    max_ask_worse: Optional[float] = None
    min_confirm_score: Optional[float] = None
    min_confirm_book: Optional[float] = None

    @property
    def label(self) -> str:
        if self.delay_sec <= 0:
            return "no_confirmation"
        parts = [f"same_side_for>={int(self.delay_sec)}s"]
        if self.max_ask_worse is not None:
            parts.append(f"ask_worse<={self.max_ask_worse:g}c")
        if self.min_confirm_score is not None:
            parts.append(f"confirm_score>={self.min_confirm_score:g}")
        if self.min_confirm_book is not None:
            parts.append(f"confirm_book>={self.min_confirm_book:g}")
        return " AND ".join(parts)


def clean_json_local(value: Any) -> Any:
    if isinstance(value, pd.Timestamp):
        return value.isoformat()
    if isinstance(value, dict):
        return {str(k): clean_json_local(v) for k, v in value.items()}
    if isinstance(value, list):
        return [clean_json_local(v) for v in value]
    return clean_json(value)


def finite(value: Any, default: float = -999999.0) -> float:
    try:
        val = float(value)
    except (TypeError, ValueError):
        return default
    if not np.isfinite(val):
        return default
    return val


def make_specs() -> List[ConfirmSpec]:
    specs = [ConfirmSpec(0)]
    for delay in [30.0, 60.0, 90.0, 120.0, 180.0]:
        for ask_worse in [None, 0.0, 5.0, 10.0]:
            for min_score in [0.55, 0.57, 0.60]:
                specs.append(ConfirmSpec(delay, max_ask_worse=ask_worse, min_confirm_score=min_score))
            for min_book in [0.55, 0.60]:
                specs.append(ConfirmSpec(delay, max_ask_worse=ask_worse, min_confirm_score=0.55, min_confirm_book=min_book))
    seen: set[str] = set()
    out: List[ConfirmSpec] = []
    for spec in specs:
        if spec.label in seen:
            continue
        seen.add(spec.label)
        out.append(spec)
    return out


def eligible_chosen(side_rows: pd.DataFrame, base: pd.DataFrame, policy: HazardPolicy) -> pd.DataFrame:
    rows = side_rows.merge(base[["market", "split"]], on="market", how="inner")
    chosen = choose_decision_sides(rows, policy.chooser)
    if chosen.empty:
        return chosen
    eligible = chosen[touch_gate_mask(chosen, policy)].copy()
    if eligible.empty:
        return eligible
    eligible["entry_dt"] = pd.to_datetime(eligible["entry_dt"], utc=True, errors="coerce")
    return eligible.sort_values(["market", "entry_dt"]).reset_index(drop=True)


def passes_confirm(candidate: pd.Series, confirm: pd.Series, policy: HazardPolicy, spec: ConfirmSpec) -> bool:
    if spec.max_ask_worse is not None:
        if finite(confirm.get("ask_cents")) > finite(candidate.get("ask_cents")) + spec.max_ask_worse:
            return False
    if spec.min_confirm_score is not None:
        if finite(confirm.get(policy.chooser)) < spec.min_confirm_score:
            return False
    if spec.min_confirm_book is not None:
        if finite(confirm.get("book_p_side")) < spec.min_confirm_book:
            return False
    return True


def select_confirmed(side_rows: pd.DataFrame, base: pd.DataFrame, policy: HazardPolicy, spec: ConfirmSpec) -> pd.DataFrame:
    eligible = eligible_chosen(side_rows, base, policy)
    if eligible.empty:
        return enrich_selected(eligible)
    if spec.delay_sec <= 0:
        selected = (
            eligible.sort_values(["market", "entry_dt"])
            .groupby("market", as_index=False, sort=False)
            .first()
            .sort_values(["entry_dt", "market"])
            .reset_index(drop=True)
        )
        return enrich_selected(selected)

    selected_rows: List[pd.Series] = []
    for _, part in eligible.groupby("market", sort=False):
        part = part.sort_values("entry_dt").reset_index(drop=True)
        chosen_row: Optional[pd.Series] = None
        for idx, candidate in part.iterrows():
            target_dt = candidate["entry_dt"] + pd.Timedelta(seconds=spec.delay_sec)
            confirm_pool = part[
                part["entry_dt"].ge(target_dt)
                & part["side"].eq(candidate["side"])
            ]
            if confirm_pool.empty:
                continue
            confirm = confirm_pool.iloc[0].copy()
            if not passes_confirm(candidate, confirm, policy, spec):
                continue
            confirm["initial_entry_dt"] = candidate["entry_dt"]
            confirm["initial_ask_cents"] = candidate["ask_cents"]
            confirm["confirm_delay_sec"] = (confirm["entry_dt"] - candidate["entry_dt"]).total_seconds()
            chosen_row = confirm
            break
        if chosen_row is not None:
            selected_rows.append(chosen_row)
    if not selected_rows:
        return enrich_selected(eligible.iloc[0:0].copy())
    selected = pd.DataFrame(selected_rows).sort_values(["entry_dt", "market"]).reset_index(drop=True)
    return enrich_selected(selected)


def metric(base: pd.DataFrame, selected: pd.DataFrame, split: str = "all") -> Dict[str, Any]:
    out = split_metric(base, selected, split)
    out["coverage_pass"] = finite(out.get("coverage"), 0.0) >= MARKET_COVERAGE_FLOOR
    out["positive_net"] = finite(out.get("net_pnl_cents"), 0.0) > 0.0
    return out


def metrics_for(base: pd.DataFrame, selected: pd.DataFrame) -> Dict[str, Dict[str, Any]]:
    return {split: metric(base, selected, split) for split in ["all", "train", "validation", "holdout"]}


def all_split_positive(metrics: Dict[str, Dict[str, Any]]) -> bool:
    return all(finite(metrics[split].get("net_pnl_cents"), 0.0) > 0.0 for split in ["all", "train", "validation", "holdout"])


def all_split_coverage(metrics: Dict[str, Dict[str, Any]]) -> bool:
    return all(finite(metrics[split].get("coverage"), 0.0) >= MARKET_COVERAGE_FLOOR for split in ["all", "train", "validation", "holdout"])


def min_oos_roi(*metric_sets: Dict[str, Dict[str, Any]]) -> float:
    values: List[float] = []
    for metrics in metric_sets:
        values.extend(
            [
                finite(metrics["validation"].get("net_roi_on_cost")),
                finite(metrics["holdout"].get("net_roi_on_cost")),
            ]
        )
    return min(values) if values else -999999.0


def fresh_metric(base: pd.DataFrame, selected: pd.DataFrame, lock: Dict[str, Any]) -> Dict[str, Any]:
    boundary = effective_lock_dt(lock)
    if pd.isna(boundary):
        fresh_base = base.iloc[0:0].copy()
    else:
        fresh_base = base[pd.to_datetime(base["close_dt"], utc=True, errors="coerce").gt(boundary)].copy()
    fresh_selected = selected[selected["market"].isin(set(fresh_base["market"]))].copy()
    return metric(fresh_base, fresh_selected, "all")


def flatten(
    spec: ConfirmSpec,
    current_metrics: Dict[str, Dict[str, Any]],
    v21_metrics: Dict[str, Dict[str, Any]],
    fresh: Dict[str, Any],
    base_current_all: Dict[str, Any],
    base_v21_all: Dict[str, Any],
) -> Dict[str, Any]:
    current_all = current_metrics["all"]
    v21_all = v21_metrics["all"]
    row: Dict[str, Any] = {
        "confirmation": spec.label,
        "delay_sec": spec.delay_sec,
        "max_ask_worse": spec.max_ask_worse,
        "min_confirm_score": spec.min_confirm_score,
        "min_confirm_book": spec.min_confirm_book,
        "current_coverage_pass": all_split_coverage(current_metrics),
        "v21_coverage_pass": all_split_coverage(v21_metrics),
        "current_all_split_positive": all_split_positive(current_metrics),
        "v21_all_split_positive": all_split_positive(v21_metrics),
        "both_coverage_pass": all_split_coverage(current_metrics) and all_split_coverage(v21_metrics),
        "both_all_split_positive": all_split_positive(current_metrics) and all_split_positive(v21_metrics),
        "min_oos_roi": min_oos_roi(current_metrics, v21_metrics),
        "fresh_markets": fresh.get("markets"),
        "fresh_base_markets": fresh.get("base_markets"),
        "fresh_wins": fresh.get("wins"),
        "fresh_losses": fresh.get("losses"),
        "fresh_net_pnl_cents": fresh.get("net_pnl_cents"),
        "fresh_coverage": fresh.get("coverage"),
        "current_delta_vs_base_cents": finite(current_all.get("net_pnl_cents")) - finite(base_current_all.get("net_pnl_cents")),
        "v21_delta_vs_base_cents": finite(v21_all.get("net_pnl_cents")) - finite(base_v21_all.get("net_pnl_cents")),
    }
    row["combined_delta_vs_base_cents"] = row["current_delta_vs_base_cents"] + row["v21_delta_vs_base_cents"]
    for prefix, metrics in [("current", current_metrics), ("v21", v21_metrics)]:
        for split, values in metrics.items():
            for key, value in values.items():
                row[f"{prefix}_{split}_{key}"] = value
    return row


def write_report(generated: str, lock: Dict[str, Any], rows: pd.DataFrame, selected_by_label: Dict[str, pd.DataFrame]) -> None:
    filtered = rows[rows["both_coverage_pass"]].copy()
    stable = filtered[filtered["both_all_split_positive"]].copy()
    stable = stable.sort_values(
        ["combined_delta_vs_base_cents", "min_oos_roi", "fresh_net_pnl_cents"],
        ascending=[False, False, False],
    )
    top = stable.head(15)
    base = rows[rows["confirmation"].eq("no_confirmation")].iloc[0]

    lines: List[str] = [
        "# Kinetic Path-Confirmation Scan",
        "",
        f"Generated UTC: `{generated}`",
        "",
        "## Scope",
        "",
        "- Research-only diagnostic; no orders are submitted and no bot files or live processes are touched.",
        "- Tests delayed same-side confirmation after the frozen kinetic-touch row first becomes eligible.",
        "- Any confirmation rule must receive a separate future lock before it counts as fresh validation.",
        "",
        "## Data",
        "",
        f"- Policy: `{lock['policy']['label']}`",
        f"- Kinetic lock close time: `{lock.get('lock_close_dt')}`",
        f"- Rules scanned: {len(rows)}",
        f"- Both-dataset 80%-coverage rules: {int(rows['both_coverage_pass'].sum())}",
        f"- Both-dataset all-split-positive coverage rules: {int(stable.shape[0])}",
        f"- Baseline current/v21 net: {fmt_cents(base['current_all_net_pnl_cents'])} / {fmt_cents(base['v21_all_net_pnl_cents'])}",
        "",
        "## Top Confirmation Rows",
        "",
        "| rank | confirmation | current net/delta | current acc/cov | v21 net/delta | v21 acc/cov | fresh | min OOS ROI |",
        "|---:|---|---:|---:|---:|---:|---:|---:|",
    ]
    for rank, (_, row) in enumerate(top.iterrows(), start=1):
        lines.append(
            f"| {rank} | `{row['confirmation']}` | "
            f"{fmt_cents(row['current_all_net_pnl_cents'])}/{fmt_cents(row['current_delta_vs_base_cents'])} | "
            f"{pct(row['current_all_accuracy'])}/{pct(row['current_all_coverage'])} | "
            f"{fmt_cents(row['v21_all_net_pnl_cents'])}/{fmt_cents(row['v21_delta_vs_base_cents'])} | "
            f"{pct(row['v21_all_accuracy'])}/{pct(row['v21_all_coverage'])} | "
            f"{int(row['fresh_wins'])}/{int(row['fresh_losses'])} {fmt_cents(row['fresh_net_pnl_cents'])} | "
            f"{fmt_roi(row['min_oos_roi'])} |"
        )

    lines += [
        "",
        "## 03:45 Loss Market Behavior",
        "",
        "| confirmation | selected side | entry | ask | outcome | win |",
        "|---|---|---|---:|---|---|",
    ]
    loss_market = "KXBTC15M-26MAY022345-45"
    for _, row in top.head(8).iterrows():
        label = row["confirmation"]
        selected = selected_by_label.get(label, pd.DataFrame())
        match = selected[selected["market"].eq(loss_market)] if not selected.empty else selected
        if match.empty:
            lines.append(f"| `{label}` | skipped |  |  |  |  |")
            continue
        item = match.iloc[0]
        lines.append(
            f"| `{label}` | {item.get('side')} | `{item.get('entry_dt')}` | "
            f"{fmt_cents(item.get('ask_cents'))} | {item.get('outcome')} | {bool(item.get('win'))} |"
        )

    lines += [
        "",
        "## Read",
        "",
    ]
    if top.empty:
        lines.append("- No delayed confirmation rule preserved coverage and all-split-positive EV across both datasets.")
    else:
        best = top.iloc[0]
        lines.append(
            f"- Best diagnostic confirmation row is `{best['confirmation']}` with current/v21 deltas "
            f"{fmt_cents(best['current_delta_vs_base_cents'])}/{fmt_cents(best['v21_delta_vs_base_cents'])}."
        )
        if finite(best["combined_delta_vs_base_cents"]) > 0:
            lines.append("- Same-side confirmation may be a real path-physics prior, but it is post-loss research and needs its own forward lock.")
        else:
            lines.append("- Same-side confirmation does not clearly dominate the frozen kinetic baseline.")

    REPORT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")
    REPORT_JSON.write_text(
        json.dumps(
            {
                "generated_utc": generated,
                "lock": clean_json_local(lock),
                "rows": clean_json_local(rows.to_dict(orient="records")),
            },
            indent=2,
            sort_keys=True,
        ),
        encoding="utf-8",
    )
    rows.to_csv(REPORT_CSV, index=False)


def main() -> int:
    generated = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%SZ")
    lock = json.loads(KINETIC_TOUCH_LOCK_PATH.read_text(encoding="utf-8"))
    policy = policy_from_record(lock["policy"])

    current_side = add_touch_hazard_scores(load_side_rows())
    v21_side = add_touch_hazard_scores(load_v21_side_rows())
    current_base = market_base(current_side)
    v21_base = market_base(v21_side)

    records: List[Dict[str, Any]] = []
    selected_by_label: Dict[str, pd.DataFrame] = {}
    base_current_all: Optional[Dict[str, Any]] = None
    base_v21_all: Optional[Dict[str, Any]] = None
    for spec in make_specs():
        current_sel = select_confirmed(current_side, current_base, policy, spec)
        v21_sel = select_confirmed(v21_side, v21_base, policy, spec)
        current_metrics = metrics_for(current_base, current_sel)
        v21_metrics = metrics_for(v21_base, v21_sel)
        if spec.delay_sec <= 0:
            base_current_all = current_metrics["all"]
            base_v21_all = v21_metrics["all"]
        if base_current_all is None or base_v21_all is None:
            raise RuntimeError("baseline metrics not initialized")
        fresh = fresh_metric(current_base, current_sel, lock)
        row = flatten(spec, current_metrics, v21_metrics, fresh, base_current_all, base_v21_all)
        records.append(row)
        selected_by_label[spec.label] = current_sel

    rows = pd.DataFrame(records)
    write_report(generated, lock, rows, selected_by_label)
    print("Kinetic path-confirmation scan complete")
    print(f"rules={len(rows)} both_coverage={int(rows['both_coverage_pass'].sum())}")
    print(f"report={REPORT_MD}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
