"""Path-flip override scan for the high-coverage v2 frontier.

V2 keeps coverage high by taking the first Brownian RV15 side with enough edge.
The 14:30 UTC failure showed a later opposite-side path signal that was right.
This diagnostic keeps the v2 entry as the default but permits a later
opposite-side override only when the flip has sufficient score and the price is
still tolerable.

Research-only: no orders are submitted and no bot files or live processes are
modified.
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

import pandas as pd

from probe_cross_dataset_interval_frontier import load_v21_side_rows
from probe_cross_dataset_profit_frontier import enrich_selected, fmt_cents, fmt_roi, metrics_for
from probe_market_interval_80coverage import (
    MARKET_COVERAGE_FLOOR,
    MIN_HOLDOUT_SELECTED_MARKETS,
    MIN_SELECTED_MARKETS,
    OUT_DIR,
    choose_decision_sides,
    clean_json,
    load_side_rows,
    market_base,
    pct,
)


REPORT_MD = OUT_DIR / "path_flip_override_frontier_latest.md"
REPORT_JSON = OUT_DIR / "path_flip_override_frontier_latest.json"
REPORT_CSV = OUT_DIR / "path_flip_override_frontier_latest.csv"

BASE_CHOOSER = "brownian_p_rv_15m"
BASE_MIN_SCORE = 0.55
BASE_ASK_MAX = 95.0
BASE_MIN_SECONDS = 120.0


@dataclass(frozen=True)
class FlipPolicy:
    override_chooser: str
    min_override_score: float
    override_ask_max: float
    min_delay_sec: float
    max_seconds_to_close: float
    max_ask_worse: Optional[float]

    @property
    def label(self) -> str:
        worse = "none" if self.max_ask_worse is None else f"{self.max_ask_worse:g}c"
        return (
            f"base=v2; override={self.override_chooser}>={self.min_override_score:.2f}; "
            f"ask<={self.override_ask_max:g}; delay>={self.min_delay_sec:g}s; "
            f"sec_to_close<={self.max_seconds_to_close:g}; ask_worse<={worse}"
        )


def clean_json_local(value: Any) -> Any:
    if isinstance(value, pd.Timestamp):
        return value.isoformat()
    if isinstance(value, dict):
        return {str(k): clean_json_local(v) for k, v in value.items()}
    if isinstance(value, list):
        return [clean_json_local(v) for v in value]
    return clean_json(value)


def make_policies() -> List[FlipPolicy]:
    policies: List[FlipPolicy] = []
    for chooser in ["brownian_p_rv_15m"]:
        for min_score in [0.65, 0.70]:
            for ask_max in [80.0, 90.0]:
                for delay in [60.0]:
                    for max_sec in [660.0, 600.0]:
                        for max_worse in [None, 30.0]:
                            policies.append(FlipPolicy(chooser, min_score, ask_max, delay, max_sec, max_worse))
    return policies


def base_selected(base_chosen: pd.DataFrame) -> pd.DataFrame:
    score = pd.to_numeric(base_chosen[BASE_CHOOSER], errors="coerce")
    ask = pd.to_numeric(base_chosen["ask_cents"], errors="coerce")
    seconds = pd.to_numeric(base_chosen["seconds_to_close"], errors="coerce")
    rows = base_chosen[
        score.ge(BASE_MIN_SCORE)
        & ask.le(BASE_ASK_MAX)
        & seconds.ge(BASE_MIN_SECONDS)
    ].copy()
    if rows.empty:
        return rows
    return (
        rows.sort_values(["market", "entry_dt"])
        .groupby("market", as_index=False, sort=False)
        .first()
        .sort_values(["entry_dt", "market"])
        .reset_index(drop=True)
    )


def apply_flip_override(base_rows: pd.DataFrame, override_chosen: pd.DataFrame, policy: FlipPolicy) -> pd.DataFrame:
    if base_rows.empty:
        return enrich_selected(base_rows)
    override = override_chosen.copy()
    override["entry_dt"] = pd.to_datetime(override["entry_dt"], utc=True, errors="coerce")
    override["seconds_to_close"] = pd.to_numeric(override["seconds_to_close"], errors="coerce")
    override["ask_cents"] = pd.to_numeric(override["ask_cents"], errors="coerce")
    override[policy.override_chooser] = pd.to_numeric(override[policy.override_chooser], errors="coerce")
    selected: List[pd.Series] = []
    for _, base in base_rows.sort_values(["market", "entry_dt"]).iterrows():
        base_dt = pd.to_datetime(base["entry_dt"], utc=True, errors="coerce")
        base_ask = float(base["ask_cents"])
        pool = override[
            override["market"].eq(base["market"])
            & override["side"].ne(base["side"])
            & override["entry_dt"].ge(base_dt + pd.Timedelta(seconds=policy.min_delay_sec))
            & override[policy.override_chooser].ge(policy.min_override_score)
            & override["ask_cents"].le(policy.override_ask_max)
            & override["seconds_to_close"].ge(BASE_MIN_SECONDS)
            & override["seconds_to_close"].le(policy.max_seconds_to_close)
        ].copy()
        if policy.max_ask_worse is not None:
            pool = pool[pool["ask_cents"].le(base_ask + policy.max_ask_worse)].copy()
        if pool.empty:
            chosen = base.copy()
            chosen["override_used"] = False
            selected.append(chosen)
            continue
        chosen = pool.sort_values("entry_dt").iloc[0].copy()
        chosen["override_used"] = True
        chosen["base_side"] = base["side"]
        chosen["base_ask_cents"] = base_ask
        chosen["base_entry_dt"] = base_dt
        selected.append(chosen)
    out = pd.DataFrame(selected).sort_values(["entry_dt", "market"]).reset_index(drop=True)
    return enrich_selected(out)


def coverage_pass(metrics: Dict[str, Dict[str, Any]]) -> bool:
    return (
        all((metrics[split]["coverage"] or 0.0) >= MARKET_COVERAGE_FLOOR for split in ["all", "train", "validation", "holdout"])
        and metrics["all"]["markets"] >= MIN_SELECTED_MARKETS
        and metrics["holdout"]["markets"] >= MIN_HOLDOUT_SELECTED_MARKETS
    )


def profitable_oos(metrics: Dict[str, Dict[str, Any]]) -> bool:
    return all((metrics[split]["net_pnl_cents"] or 0.0) > 0.0 for split in ["validation", "holdout"])


def override_count(selected: pd.DataFrame) -> int:
    if selected.empty or "override_used" not in selected.columns:
        return 0
    return int(selected["override_used"].fillna(False).astype(bool).sum())


def flatten(
    policy: FlipPolicy,
    current: Dict[str, Dict[str, Any]],
    v21: Dict[str, Dict[str, Any]],
    current_overrides: int,
    v21_overrides: int,
    current_base_net: float,
    v21_base_net: float,
) -> Dict[str, Any]:
    row: Dict[str, Any] = {
        "label": policy.label,
        "override_chooser": policy.override_chooser,
        "min_override_score": policy.min_override_score,
        "override_ask_max": policy.override_ask_max,
        "min_delay_sec": policy.min_delay_sec,
        "max_seconds_to_close": policy.max_seconds_to_close,
        "max_ask_worse": policy.max_ask_worse,
        "current_overrides": current_overrides,
        "v21_overrides": v21_overrides,
        "current_coverage_pass": coverage_pass(current),
        "v21_coverage_pass": coverage_pass(v21),
        "both_coverage_pass": coverage_pass(current) and coverage_pass(v21),
        "current_profitable_oos": profitable_oos(current),
        "v21_profitable_oos": profitable_oos(v21),
        "both_profitable_oos": profitable_oos(current) and profitable_oos(v21),
    }
    row["current_delta_vs_base_cents"] = (current["all"]["net_pnl_cents"] or 0.0) - current_base_net
    row["v21_delta_vs_base_cents"] = (v21["all"]["net_pnl_cents"] or 0.0) - v21_base_net
    row["combined_delta_vs_base_cents"] = row["current_delta_vs_base_cents"] + row["v21_delta_vs_base_cents"]
    row["combined_all_net_pnl_cents"] = (current["all"]["net_pnl_cents"] or 0.0) + (v21["all"]["net_pnl_cents"] or 0.0)
    row["min_all_coverage"] = min(current["all"]["coverage"] or 0.0, v21["all"]["coverage"] or 0.0)
    row["min_oos_net_roi"] = min(
        current["validation"]["net_roi_on_cost"] or -1.0,
        current["holdout"]["net_roi_on_cost"] or -1.0,
        v21["validation"]["net_roi_on_cost"] or -1.0,
        v21["holdout"]["net_roi_on_cost"] or -1.0,
    )
    row["min_accuracy_minus_break_even"] = min(
        current[split]["accuracy_minus_break_even"] or -1.0
        for split in ["all", "train", "validation", "holdout"]
    )
    row["min_accuracy_minus_break_even"] = min(
        row["min_accuracy_minus_break_even"],
        min(v21[split]["accuracy_minus_break_even"] or -1.0 for split in ["all", "train", "validation", "holdout"]),
    )
    for prefix, metrics in [("current", current), ("v21", v21)]:
        for split, values in metrics.items():
            for key, value in values.items():
                row[f"{prefix}_{split}_{key}"] = value
    return row


def write_report(
    generated: str,
    rows: pd.DataFrame,
    current_base_metrics: Dict[str, Dict[str, Any]],
    v21_base_metrics: Dict[str, Dict[str, Any]],
    selected_by_label: Dict[str, pd.DataFrame],
) -> None:
    viable = rows[rows["both_coverage_pass"]].copy()
    viable = viable.sort_values(
        ["both_profitable_oos", "combined_delta_vs_base_cents", "min_oos_net_roi", "min_accuracy_minus_break_even"],
        ascending=[False, False, False, False],
    )
    top = viable.head(20)
    lines: List[str] = [
        "# Path-Flip Override Frontier",
        "",
        f"Generated UTC: `{generated}`",
        "",
        "## Scope",
        "",
        "- Research-only scan; no orders are submitted and no bot files or live processes are touched.",
        "- Keeps v2 as the default high-coverage entry and tests later opposite-side overrides.",
        "- Diagnostic only; a winner still needs a forward lock and strict pre-resolution validation.",
        "",
        "## Baseline",
        "",
        f"- Current v2 baseline: {fmt_cents(current_base_metrics['all']['net_pnl_cents'])}, "
        f"{pct(current_base_metrics['all']['accuracy'])} accuracy, {pct(current_base_metrics['all']['coverage'])} coverage.",
        f"- V21 v2 baseline: {fmt_cents(v21_base_metrics['all']['net_pnl_cents'])}, "
        f"{pct(v21_base_metrics['all']['accuracy'])} accuracy, {pct(v21_base_metrics['all']['coverage'])} coverage.",
        "",
        "## Summary",
        "",
        f"- Policies scanned: {len(rows)}",
        f"- Both-dataset 80% coverage policies: {int(rows['both_coverage_pass'].sum())}",
        f"- Both-dataset OOS-positive policies: {int((rows['both_coverage_pass'] & rows['both_profitable_oos']).sum())}",
        "",
        "## Top Rows",
        "",
        "| rank | policy | delta current/v21 | overrides current/v21 | current net/acc/cov | v21 net/acc/cov | OOS ROI floor |",
        "|---:|---|---:|---:|---:|---:|---:|",
    ]
    for rank, (_, row) in enumerate(top.iterrows(), start=1):
        lines.append(
            f"| {rank} | `{row['label']}` | "
            f"{fmt_cents(row['current_delta_vs_base_cents'])}/{fmt_cents(row['v21_delta_vs_base_cents'])} | "
            f"{int(row['current_overrides'])}/{int(row['v21_overrides'])} | "
            f"{fmt_cents(row['current_all_net_pnl_cents'])}/{pct(row['current_all_accuracy'])}/{pct(row['current_all_coverage'])} | "
            f"{fmt_cents(row['v21_all_net_pnl_cents'])}/{pct(row['v21_all_accuracy'])}/{pct(row['v21_all_coverage'])} | "
            f"{fmt_roi(row['min_oos_net_roi'])} |"
        )

    lines += [
        "",
        "## 14:30 UTC Split Case",
        "",
        "| policy | selected side | entry | ask | outcome | win | net | override |",
        "|---|---|---|---:|---|---|---:|---|",
    ]
    split_market = "KXBTC15M-26MAY031030-30"
    for _, row in top.head(8).iterrows():
        selected = selected_by_label.get(row["label"], pd.DataFrame())
        hit = selected[selected["market"].eq(split_market)] if not selected.empty else selected
        if hit.empty:
            lines.append(f"| `{row['label']}` | skipped |  |  |  |  |  |  |")
            continue
        item = hit.iloc[0]
        lines.append(
            f"| `{row['label']}` | {item.get('side')} | `{item.get('entry_dt')}` | "
            f"{fmt_cents(item.get('ask_cents'))} | {item.get('outcome')} | {bool(item.get('win'))} | "
            f"{fmt_cents(item.get('net_pnl_cents'))} | {bool(item.get('override_used'))} |"
        )

    lines += ["", "## Read", ""]
    if top.empty:
        lines.append("- No path-flip override row preserved the 80% coverage floor on both datasets.")
    else:
        best = top.iloc[0]
        lines.append(
            f"- Best diagnostic row: `{best['label']}` with current/v21 delta "
            f"{fmt_cents(best['current_delta_vs_base_cents'])}/{fmt_cents(best['v21_delta_vs_base_cents'])}."
        )
        lines.append(
            "- Important: this scan is an upper-bound diagnostic, not yet a tradable lock. "
            "It keeps the early v2 selection when no flip appears, but replaces it with a later opposite-side row when a flip appears. "
            "A tradable version must model either waiting cost or exit-and-reverse cost before any forward lock."
        )
    REPORT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def dataset_setup(side_rows: pd.DataFrame, base: pd.DataFrame) -> tuple[pd.DataFrame, Dict[str, pd.DataFrame]]:
    rows = side_rows.merge(base[["market", "split"]], on="market", how="inner")
    choosers = sorted({"brownian_p_rv_15m", "score_min_book_rv15", "book_p_side"})
    return rows, {chooser: choose_decision_sides(rows, chooser) for chooser in choosers}


def main() -> int:
    generated = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%SZ")
    current_side = load_side_rows()
    v21_side = load_v21_side_rows()
    current_base = market_base(current_side)
    v21_base = market_base(v21_side)
    _, current_chosen = dataset_setup(current_side, current_base)
    _, v21_chosen = dataset_setup(v21_side, v21_base)
    current_base_selected = enrich_selected(base_selected(current_chosen[BASE_CHOOSER]))
    v21_base_selected = enrich_selected(base_selected(v21_chosen[BASE_CHOOSER]))
    current_base_metrics = metrics_for(current_base, current_base_selected)
    v21_base_metrics = metrics_for(v21_base, v21_base_selected)
    current_base_net = float(current_base_metrics["all"]["net_pnl_cents"] or 0.0)
    v21_base_net = float(v21_base_metrics["all"]["net_pnl_cents"] or 0.0)

    rows: List[Dict[str, Any]] = []
    selected_by_label: Dict[str, pd.DataFrame] = {}
    for policy in make_policies():
        current_selected = apply_flip_override(current_base_selected, current_chosen[policy.override_chooser], policy)
        v21_selected = apply_flip_override(v21_base_selected, v21_chosen[policy.override_chooser], policy)
        current_metrics = metrics_for(current_base, current_selected)
        v21_metrics = metrics_for(v21_base, v21_selected)
        row = flatten(
            policy,
            current_metrics,
            v21_metrics,
            override_count(current_selected),
            override_count(v21_selected),
            current_base_net,
            v21_base_net,
        )
        rows.append(row)
        if row["both_coverage_pass"]:
            selected_by_label[row["label"]] = current_selected
    df = pd.DataFrame(rows)
    df.to_csv(REPORT_CSV, index=False)
    REPORT_JSON.write_text(
        json.dumps({"generated_utc": generated, "rows": clean_json_local(df.to_dict(orient="records"))}, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    write_report(generated, df, current_base_metrics, v21_base_metrics, selected_by_label)
    print("Path-flip override frontier scan complete")
    print(f"policies={len(df)} coverage_pass={int(df['both_coverage_pass'].sum())}")
    print(f"report={REPORT_MD}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
