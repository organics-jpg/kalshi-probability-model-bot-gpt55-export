"""Physics sanity audit for the kinetic guard overlay.

The guarded kinetic overlay was chosen after the first kinetic forward loss, so
it cannot be trusted as fresh evidence by itself. This probe asks whether the
guard family behaves like a stable physical prior or like a current-ledger scar:
does adverse-path blocking improve both datasets, or does it merely transfer
profit between captures while preserving coverage?

Research-only: no orders are submitted and no bot files or live processes are
modified.
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Dict, Iterable, List, Optional

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
from probe_profit_touch_hazard_fresh_validation import policy_from_record
from probe_profit_touch_hazard_frontier import HazardPolicy, add_touch_hazard_scores, gate_mask as touch_gate_mask


@dataclass(frozen=True)
class GuardSpec:
    family: str
    min_kinetic: Optional[float] = None
    max_adverse15: Optional[float] = None
    max_ask: Optional[float] = None
    max_touch_loss15: Optional[float] = None
    min_book: Optional[float] = None
    min_margin15: Optional[float] = None

    @property
    def label(self) -> str:
        clauses: List[str] = []
        if self.min_kinetic is not None:
            clauses.append(f"kinetic>={self.min_kinetic:g}")
        if self.max_adverse15 is not None:
            clauses.append(f"adverse15<={self.max_adverse15:g}")
        if self.max_ask is not None:
            clauses.append(f"ask<={self.max_ask:g}")
        if self.max_touch_loss15 is not None:
            clauses.append(f"touch_loss15<={self.max_touch_loss15:g}")
        if self.min_book is not None:
            clauses.append(f"book>={self.min_book:g}")
        if self.min_margin15 is not None:
            clauses.append(f"margin15>={self.min_margin15:g}")
        return "none" if not clauses else " AND ".join(clauses)


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


def guard_mask(rows: pd.DataFrame, spec: GuardSpec) -> pd.Series:
    mask = pd.Series(True, index=rows.index)
    if spec.min_kinetic is not None:
        mask &= pd.to_numeric(rows["kinetic_touch_score_15"], errors="coerce").ge(spec.min_kinetic)
    if spec.max_adverse15 is not None:
        mask &= pd.to_numeric(rows["adverse_move_15m"], errors="coerce").le(spec.max_adverse15)
    if spec.max_ask is not None:
        mask &= pd.to_numeric(rows["ask_cents"], errors="coerce").le(spec.max_ask)
    if spec.max_touch_loss15 is not None:
        mask &= pd.to_numeric(rows["touch_loss_rv_15m"], errors="coerce").le(spec.max_touch_loss15)
    if spec.min_book is not None:
        mask &= pd.to_numeric(rows["book_p_side"], errors="coerce").ge(spec.min_book)
    if spec.min_margin15 is not None:
        mask &= pd.to_numeric(rows["margin_per_rv_sigma_15m"], errors="coerce").ge(spec.min_margin15)
    return mask.fillna(False)


def make_specs() -> List[GuardSpec]:
    specs = [GuardSpec("base")]
    for min_kinetic in [0.55, 0.56, 0.57, 0.58, 0.60]:
        for max_adverse in [20.0, 50.0, 75.0, 100.0, None]:
            specs.append(GuardSpec("kinetic_adverse", min_kinetic=min_kinetic, max_adverse15=max_adverse))
    for max_adverse in [20.0, 50.0, 75.0, 100.0]:
        for max_ask in [70.0, 75.0, 80.0, 85.0, 90.0]:
            specs.append(GuardSpec("adverse_ask", max_adverse15=max_adverse, max_ask=max_ask))
    for min_kinetic in [0.56, 0.57, 0.58]:
        for max_adverse in [50.0, 75.0]:
            for max_ask in [75.0, 80.0, 90.0]:
                specs.append(
                    GuardSpec(
                        "kinetic_adverse_ask",
                        min_kinetic=min_kinetic,
                        max_adverse15=max_adverse,
                        max_ask=max_ask,
                    )
                )
    for min_kinetic in [0.56, 0.57, 0.58]:
        for max_touch in [0.80, 0.85, 0.90]:
            specs.append(GuardSpec("kinetic_touchloss", min_kinetic=min_kinetic, max_touch_loss15=max_touch))
    for min_kinetic in [0.56, 0.57]:
        for min_book in [0.55, 0.60]:
            specs.append(GuardSpec("kinetic_book", min_kinetic=min_kinetic, min_book=min_book))
    for min_kinetic in [0.56, 0.57]:
        for min_margin in [0.0, 0.25, 0.50]:
            specs.append(GuardSpec("kinetic_margin", min_kinetic=min_kinetic, min_margin15=min_margin))

    seen: set[str] = set()
    out: List[GuardSpec] = []
    for spec in specs:
        if spec.label in seen:
            continue
        seen.add(spec.label)
        out.append(spec)
    return out


def select_with_guard(side_rows: pd.DataFrame, base: pd.DataFrame, policy: HazardPolicy, spec: GuardSpec) -> pd.DataFrame:
    rows = side_rows.merge(base[["market", "split"]], on="market", how="inner")
    chosen = choose_decision_sides(rows, policy.chooser)
    if chosen.empty:
        return enrich_selected(chosen)
    eligible = chosen[touch_gate_mask(chosen, policy) & guard_mask(chosen, spec)].copy()
    if eligible.empty:
        return enrich_selected(eligible)
    selected = (
        eligible.sort_values(["market", "entry_dt"])
        .groupby("market", as_index=False, sort=False)
        .first()
        .sort_values(["entry_dt", "market"])
        .reset_index(drop=True)
    )
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
        values.extend([finite(metrics["validation"].get("net_roi_on_cost")), finite(metrics["holdout"].get("net_roi_on_cost"))])
    return min(values) if values else -999999.0


def flatten(
    spec: GuardSpec,
    current_metrics: Dict[str, Dict[str, Any]],
    v21_metrics: Dict[str, Dict[str, Any]],
    base_current: Dict[str, Any],
    base_v21: Dict[str, Any],
) -> Dict[str, Any]:
    current_all = current_metrics["all"]
    v21_all = v21_metrics["all"]
    row: Dict[str, Any] = {
        "family": spec.family,
        "guard": spec.label,
        "current_coverage_pass": all_split_coverage(current_metrics),
        "v21_coverage_pass": all_split_coverage(v21_metrics),
        "current_all_split_positive": all_split_positive(current_metrics),
        "v21_all_split_positive": all_split_positive(v21_metrics),
        "min_oos_roi": min_oos_roi(current_metrics, v21_metrics),
        "current_delta_vs_base_cents": finite(current_all.get("net_pnl_cents")) - finite(base_current.get("net_pnl_cents")),
        "v21_delta_vs_base_cents": finite(v21_all.get("net_pnl_cents")) - finite(base_v21.get("net_pnl_cents")),
        "combined_delta_vs_base_cents": (
            finite(current_all.get("net_pnl_cents"))
            + finite(v21_all.get("net_pnl_cents"))
            - finite(base_current.get("net_pnl_cents"))
            - finite(base_v21.get("net_pnl_cents"))
        ),
    }
    row["both_coverage_pass"] = row["current_coverage_pass"] and row["v21_coverage_pass"]
    row["both_all_split_positive"] = row["current_all_split_positive"] and row["v21_all_split_positive"]
    for prefix, metrics in [("current", current_metrics), ("v21", v21_metrics)]:
        for split, values in metrics.items():
            for key, value in values.items():
                row[f"{prefix}_{split}_{key}"] = value
    return row


def rank_key(row: Dict[str, Any]) -> tuple:
    return (
        int(row["both_coverage_pass"]),
        int(row["both_all_split_positive"]),
        row["combined_delta_vs_base_cents"],
        row["min_oos_roi"],
        finite(row.get("current_all_net_pnl_cents")),
        finite(row.get("v21_all_net_pnl_cents")),
    )


def family_summary(results: pd.DataFrame) -> pd.DataFrame:
    rows: List[Dict[str, Any]] = []
    for family, group in results.groupby("family", sort=False):
        coverage = group[group["both_coverage_pass"]]
        positive = coverage[coverage["both_all_split_positive"]]
        rows.append(
            {
                "family": family,
                "rows": int(len(group)),
                "coverage_rows": int(len(coverage)),
                "positive_coverage_rows": int(len(positive)),
                "best_combined_delta": float(group["combined_delta_vs_base_cents"].max()) if not group.empty else 0.0,
                "median_combined_delta": float(group["combined_delta_vs_base_cents"].median()) if not group.empty else 0.0,
                "best_min_oos_roi": float(coverage["min_oos_roi"].max()) if not coverage.empty else None,
            }
        )
    return pd.DataFrame(rows).sort_values(["positive_coverage_rows", "best_combined_delta"], ascending=[False, False])


def market_set_delta(base_selected: pd.DataFrame, guard_selected: pd.DataFrame) -> Dict[str, Any]:
    base_markets = set(base_selected["market"])
    guard_markets = set(guard_selected["market"])
    removed = base_selected[base_selected["market"].isin(base_markets - guard_markets)].copy()
    added = guard_selected[guard_selected["market"].isin(guard_markets - base_markets)].copy()
    common = base_selected[base_selected["market"].isin(base_markets & guard_markets)][["market", "net_pnl_cents"]].merge(
        guard_selected[guard_selected["market"].isin(base_markets & guard_markets)][["market", "net_pnl_cents"]],
        on="market",
        how="inner",
        suffixes=("_base", "_guard"),
    )
    common_delta = (
        common["net_pnl_cents_guard"].astype(float) - common["net_pnl_cents_base"].astype(float)
        if not common.empty
        else pd.Series(dtype=float)
    )
    return {
        "removed_markets": int(len(removed)),
        "removed_net_pnl_cents": float(removed["net_pnl_cents"].sum()) if not removed.empty else 0.0,
        "removed_wins": int(removed["win"].sum()) if not removed.empty and "win" in removed else 0,
        "removed_losses": int((~removed["win"].astype(bool)).sum()) if not removed.empty and "win" in removed else 0,
        "added_markets": int(len(added)),
        "added_net_pnl_cents": float(added["net_pnl_cents"].sum()) if not added.empty else 0.0,
        "added_wins": int(added["win"].sum()) if not added.empty and "win" in added else 0,
        "added_losses": int((~added["win"].astype(bool)).sum()) if not added.empty and "win" in added else 0,
        "common_markets": int(len(common)),
        "common_entry_delta_cents": float(common_delta.sum()) if not common_delta.empty else 0.0,
    }


def scan() -> tuple[pd.DataFrame, pd.DataFrame, Dict[str, Any]]:
    if not KINETIC_TOUCH_LOCK_PATH.exists():
        raise SystemExit(f"Missing kinetic touch lock: {KINETIC_TOUCH_LOCK_PATH}")
    lock = json.loads(KINETIC_TOUCH_LOCK_PATH.read_text(encoding="utf-8"))
    policy = policy_from_record(lock["policy"])
    specs = make_specs()

    current_side = add_touch_hazard_scores(load_side_rows())
    current_base = market_base(current_side)
    v21_side = add_touch_hazard_scores(load_v21_side_rows())
    v21_base = market_base(v21_side)

    base_spec = GuardSpec("base")
    guard_spec = GuardSpec("kinetic_adverse", min_kinetic=0.57, max_adverse15=50.0)
    base_current_selected = select_with_guard(current_side, current_base, policy, base_spec)
    base_v21_selected = select_with_guard(v21_side, v21_base, policy, base_spec)
    guard_current_selected = select_with_guard(current_side, current_base, policy, guard_spec)
    guard_v21_selected = select_with_guard(v21_side, v21_base, policy, guard_spec)
    base_current_metrics = metrics_for(current_base, base_current_selected)
    base_v21_metrics = metrics_for(v21_base, base_v21_selected)

    rows: List[Dict[str, Any]] = []
    for spec in specs:
        current_selected = select_with_guard(current_side, current_base, policy, spec)
        v21_selected = select_with_guard(v21_side, v21_base, policy, spec)
        rows.append(
            flatten(
                spec,
                metrics_for(current_base, current_selected),
                metrics_for(v21_base, v21_selected),
                base_current_metrics["all"],
                base_v21_metrics["all"],
            )
        )
    rows.sort(key=rank_key, reverse=True)
    results = pd.DataFrame(rows)
    diagnostics = {
        "policy": lock["policy"],
        "lock_close_dt": lock.get("lock_close_dt"),
        "current_intervals": int(len(current_base)),
        "v21_intervals": int(len(v21_base)),
        "specs_scanned": int(len(specs)),
        "base_current": base_current_metrics["all"],
        "base_v21": base_v21_metrics["all"],
        "guard_current": metrics_for(current_base, guard_current_selected)["all"],
        "guard_v21": metrics_for(v21_base, guard_v21_selected)["all"],
        "current_market_set_delta": market_set_delta(base_current_selected, guard_current_selected),
        "v21_market_set_delta": market_set_delta(base_v21_selected, guard_v21_selected),
    }
    return results, family_summary(results), diagnostics


def write_report(path, generated: str, results: pd.DataFrame, families: pd.DataFrame, diagnostics: Dict[str, Any]) -> None:
    coverage = results[results["both_coverage_pass"]]
    positive = coverage[coverage["both_all_split_positive"]]
    selected_guard = results[results["guard"].eq("kinetic>=0.57 AND adverse15<=50")]
    selected = selected_guard.iloc[0].to_dict() if not selected_guard.empty else None
    base_current = diagnostics["base_current"]
    base_v21 = diagnostics["base_v21"]
    guard_current = diagnostics["guard_current"]
    guard_v21 = diagnostics["guard_v21"]
    current_delta = finite(guard_current.get("net_pnl_cents")) - finite(base_current.get("net_pnl_cents"))
    v21_delta = finite(guard_v21.get("net_pnl_cents")) - finite(base_v21.get("net_pnl_cents"))

    lines: List[str] = [
        "# Kinetic-Guard Physics Sanity Audit",
        "",
        f"Generated UTC: `{generated}`",
        "",
        "## Scope",
        "",
        "- Research-only audit; no orders are submitted and no bot files or live processes are touched.",
        "- Tests whether the guarded kinetic family looks physically stable rather than merely explaining a recent loss.",
        "- Does not update any lock and does not count post-outcome diagnostics as fresh evidence.",
        "",
        "## Baseline Versus Guard",
        "",
        f"- Policy: `{diagnostics['policy']['label']}`",
        f"- Kinetic lock close time: `{diagnostics['lock_close_dt']}`",
        f"- Current intervals: {diagnostics['current_intervals']}; v21 intervals: {diagnostics['v21_intervals']}; guard specs scanned: {diagnostics['specs_scanned']}",
        "",
        "| dataset | model | markets | wins/losses | acc | break-even | coverage | net P&L | ROI | delta vs unguarded |",
        "|---|---|---:|---:|---:|---:|---:|---:|---:|---:|",
        (
            f"| current | unguarded kinetic | {int(base_current['markets'])}/{int(base_current['base_markets'])} | "
            f"{int(base_current['wins'])}/{int(base_current['losses'])} | {pct(base_current['accuracy'])} | "
            f"{pct(base_current['fee_aware_break_even_accuracy'])} | {pct(base_current['coverage'])} | "
            f"{fmt_cents(base_current['net_pnl_cents'])} | {fmt_roi(base_current['net_roi_on_cost'])} | {fmt_cents(0)} |"
        ),
        (
            f"| current | `kinetic>=0.57 AND adverse15<=50` | {int(guard_current['markets'])}/{int(guard_current['base_markets'])} | "
            f"{int(guard_current['wins'])}/{int(guard_current['losses'])} | {pct(guard_current['accuracy'])} | "
            f"{pct(guard_current['fee_aware_break_even_accuracy'])} | {pct(guard_current['coverage'])} | "
            f"{fmt_cents(guard_current['net_pnl_cents'])} | {fmt_roi(guard_current['net_roi_on_cost'])} | {fmt_cents(current_delta)} |"
        ),
        (
            f"| v21 | unguarded kinetic | {int(base_v21['markets'])}/{int(base_v21['base_markets'])} | "
            f"{int(base_v21['wins'])}/{int(base_v21['losses'])} | {pct(base_v21['accuracy'])} | "
            f"{pct(base_v21['fee_aware_break_even_accuracy'])} | {pct(base_v21['coverage'])} | "
            f"{fmt_cents(base_v21['net_pnl_cents'])} | {fmt_roi(base_v21['net_roi_on_cost'])} | {fmt_cents(0)} |"
        ),
        (
            f"| v21 | `kinetic>=0.57 AND adverse15<=50` | {int(guard_v21['markets'])}/{int(guard_v21['base_markets'])} | "
            f"{int(guard_v21['wins'])}/{int(guard_v21['losses'])} | {pct(guard_v21['accuracy'])} | "
            f"{pct(guard_v21['fee_aware_break_even_accuracy'])} | {pct(guard_v21['coverage'])} | "
            f"{fmt_cents(guard_v21['net_pnl_cents'])} | {fmt_roi(guard_v21['net_roi_on_cost'])} | {fmt_cents(v21_delta)} |"
        ),
        "",
        "## Guard Family Summary",
        "",
        "| family | rows | 80%-coverage rows | positive coverage rows | best delta | median delta | best min OOS ROI |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for row in families.to_dict("records"):
        lines.append(
            f"| `{row['family']}` | {row['rows']} | {row['coverage_rows']} | {row['positive_coverage_rows']} | "
            f"{fmt_cents(row['best_combined_delta'])} | {fmt_cents(row['median_combined_delta'])} | {fmt_roi(row['best_min_oos_roi'])} |"
        )

    lines += [
        "",
        "## Top Coverage-Preserving Guards",
        "",
        "| rank | guard | family | current net/delta | current acc/cov | v21 net/delta | v21 acc/cov | min OOS ROI |",
        "|---:|---|---|---:|---:|---:|---:|---:|",
    ]
    for idx, row in enumerate(coverage.head(15).to_dict("records"), start=1):
        lines.append(
            f"| {idx} | `{row['guard']}` | `{row['family']}` | "
            f"{fmt_cents(row['current_all_net_pnl_cents'])}/{fmt_cents(row['current_delta_vs_base_cents'])} | "
            f"{pct(row['current_all_accuracy'])}/{pct(row['current_all_coverage'])} | "
            f"{fmt_cents(row['v21_all_net_pnl_cents'])}/{fmt_cents(row['v21_delta_vs_base_cents'])} | "
            f"{pct(row['v21_all_accuracy'])}/{pct(row['v21_all_coverage'])} | {fmt_roi(row['min_oos_roi'])} |"
        )

    lines += ["", "## Read", ""]
    lines.append(f"- Both-dataset 80%-coverage guards: {len(coverage)}; all-split-positive coverage guards: {len(positive)}.")
    if selected is not None:
        lines.append(
            f"- The locked guard improves current by {fmt_cents(selected['current_delta_vs_base_cents'])} "
            f"but changes v21 by {fmt_cents(selected['v21_delta_vs_base_cents'])}; combined delta is "
            f"{fmt_cents(selected['combined_delta_vs_base_cents'])}."
        )
    cur_set = diagnostics["current_market_set_delta"]
    v21_set = diagnostics["v21_market_set_delta"]
    lines.append(
        f"- Market-set delta for the locked guard: current removed {cur_set['removed_markets']} base markets "
        f"({fmt_cents(cur_set['removed_net_pnl_cents'])}) and added {cur_set['added_markets']} alternate markets "
        f"({fmt_cents(cur_set['added_net_pnl_cents'])}); current common-market entry/timing delta is "
        f"{fmt_cents(cur_set['common_entry_delta_cents'])}. V21 removed {v21_set['removed_markets']} "
        f"({fmt_cents(v21_set['removed_net_pnl_cents'])}) and added {v21_set['added_markets']} "
        f"({fmt_cents(v21_set['added_net_pnl_cents'])}); v21 common-market entry/timing delta is "
        f"{fmt_cents(v21_set['common_entry_delta_cents'])}."
    )
    if selected is not None and finite(selected["v21_delta_vs_base_cents"]) < 0.0:
        lines.append(
            "- This is a caution flag: the guard repairs the current weak slice but does not dominate the unguarded kinetic rule on v21."
        )
    lines.append(
        "- Treat the guard as a live forward hypothesis only. The next pending outcome is high leverage because one loss would wipe out the current +21c fresh guard net."
    )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    generated = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%SZ")
    results, families, diagnostics = scan()
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    csv_latest = OUT_DIR / "kinetic_guard_physics_sanity_latest.csv"
    csv_stamp = OUT_DIR / f"kinetic_guard_physics_sanity_{generated}.csv"
    family_latest = OUT_DIR / "kinetic_guard_physics_sanity_families_latest.csv"
    family_stamp = OUT_DIR / f"kinetic_guard_physics_sanity_families_{generated}.csv"
    md_latest = OUT_DIR / "kinetic_guard_physics_sanity_latest.md"
    md_stamp = OUT_DIR / f"kinetic_guard_physics_sanity_{generated}.md"
    json_latest = OUT_DIR / "kinetic_guard_physics_sanity_latest.json"
    json_stamp = OUT_DIR / f"kinetic_guard_physics_sanity_{generated}.json"

    results.to_csv(csv_latest, index=False)
    results.to_csv(csv_stamp, index=False)
    families.to_csv(family_latest, index=False)
    families.to_csv(family_stamp, index=False)
    write_report(md_latest, generated, results, families, diagnostics)
    write_report(md_stamp, generated, results, families, diagnostics)

    payload = {
        "generated_utc": generated,
        "diagnostics": diagnostics,
        "both_coverage_count": int(results["both_coverage_pass"].sum()),
        "both_positive_all_splits_count": int((results["both_coverage_pass"] & results["both_all_split_positive"]).sum()),
        "selected_guard": results[results["guard"].eq("kinetic>=0.57 AND adverse15<=50")].head(1).to_dict("records"),
        "top_rows": results.head(25).to_dict("records"),
        "families": families.to_dict("records"),
    }
    for out_path in [json_latest, json_stamp]:
        out_path.write_text(json.dumps(clean_json_local(payload), indent=2, sort_keys=True), encoding="utf-8")

    print("Kinetic-guard physics sanity audit complete")
    print(f"guards={len(results)} both_coverage={int(results['both_coverage_pass'].sum())}")
    print(f"both_positive_all_splits={int((results['both_coverage_pass'] & results['both_all_split_positive']).sum())}")
    print(f"report={md_latest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
