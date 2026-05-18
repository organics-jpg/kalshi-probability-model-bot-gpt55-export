"""Same-heartbeat consensus override scan for Brownian v2.

Direct book/Brownian consensus candidates fixed many recent v2 failures, but
they also gave back historical v21 edge by entering the same side later or at
worse prices. This probe tests a stricter, tradable hybrid:

- choose the v2 Brownian side at each heartbeat by default;
- at the same decision_key only, flip to a consensus side if the consensus
  chooser disagrees and clears a simple threshold;
- select the first eligible heartbeat per market.

That avoids late optionality and keeps the recurring-market coverage unit.

Research-only: no orders are submitted and no bot files or live processes are
modified.
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Dict, List

import numpy as np
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
    select_markets_from_chosen,
)
from probe_profit_frontier_fresh_validation import policy_from_record
from probe_profit_frontier_v2_fresh_validation import FRONTIER_V2_LOCK_PATH


REPORT_MD = OUT_DIR / "v2_consensus_override_scan_latest.md"
REPORT_JSON = OUT_DIR / "v2_consensus_override_scan_latest.json"
REPORT_CSV = OUT_DIR / "v2_consensus_override_scan_latest.csv"


@dataclass(frozen=True)
class OverridePolicy:
    chooser: str
    min_score: float
    ask_max: float
    min_seconds: float
    require_disagree: bool
    fallback_when_v2_fails: bool
    gate: str = "none"

    @property
    def label(self) -> str:
        parts = [
            f"v2_default_then_{self.chooser}",
            f"{self.chooser}>={self.min_score:g}",
            f"ask<={self.ask_max:g}",
            f"sec>={self.min_seconds:g}",
        ]
        if self.gate != "none":
            parts.append(self.gate)
        if self.require_disagree:
            parts.append("disagree_only")
        if self.fallback_when_v2_fails:
            parts.append("fallback")
        return "; ".join(parts)


def clean_json_local(value: Any) -> Any:
    if isinstance(value, pd.Timestamp):
        return value.isoformat()
    if isinstance(value, dict):
        return {str(k): clean_json_local(v) for k, v in value.items()}
    if isinstance(value, list):
        return [clean_json_local(v) for v in value]
    return clean_json(value)


def v2_policy() -> Any:
    lock = json.loads(FRONTIER_V2_LOCK_PATH.read_text(encoding="utf-8"))
    return policy_from_record(lock["policy"])


def make_policies() -> List[OverridePolicy]:
    out: List[OverridePolicy] = []
    for chooser, thresholds, gates in [
        ("score_min_book_rv15", [0.55, 0.60, 0.65, 0.70], ["none"]),
        ("book_p_side", [0.55, 0.60, 0.65, 0.70], ["none", "margin_rv15>=0", "brownian15>=0.55_and_brownian30>=0.55"]),
    ]:
        for threshold in thresholds:
            for ask_max in [90.0, 95.0]:
                for gate in gates:
                    for fallback in [False, True]:
                        out.append(
                            OverridePolicy(
                                chooser=chooser,
                                min_score=threshold,
                                ask_max=ask_max,
                                min_seconds=120.0,
                                require_disagree=True,
                                fallback_when_v2_fails=fallback,
                                gate=gate,
                            )
                        )
    return out


def gate_mask(rows: pd.DataFrame, policy: OverridePolicy) -> pd.Series:
    mask = (
        pd.to_numeric(rows[policy.chooser], errors="coerce").ge(policy.min_score)
        & pd.to_numeric(rows["ask_cents"], errors="coerce").le(policy.ask_max)
        & pd.to_numeric(rows["seconds_to_close"], errors="coerce").ge(policy.min_seconds)
    )
    if policy.gate == "none":
        return mask.fillna(False)
    if policy.gate == "margin_rv15>=0":
        return (mask & pd.to_numeric(rows["margin_per_rv_sigma_15m"], errors="coerce").ge(0.0)).fillna(False)
    if policy.gate == "brownian15>=0.55_and_brownian30>=0.55":
        return (
            mask
            & pd.to_numeric(rows["brownian_p_rv_15m"], errors="coerce").ge(0.55)
            & pd.to_numeric(rows["brownian_p_rv_30m"], errors="coerce").ge(0.55)
        ).fillna(False)
    raise ValueError(policy.gate)


def select_v2(side_rows: pd.DataFrame, base: pd.DataFrame) -> pd.DataFrame:
    policy = v2_policy()
    rows = side_rows.merge(base[["market", "split"]], on="market", how="inner")
    chosen = choose_decision_sides(rows, policy.chooser)
    return enrich_selected(select_markets_from_chosen(chosen, policy))


def selected_hybrid(side_rows: pd.DataFrame, base: pd.DataFrame, policy: OverridePolicy) -> pd.DataFrame:
    rows = side_rows.merge(base[["market", "split"]], on="market", how="inner")
    base_policy = v2_policy()
    v2_chosen = choose_decision_sides(rows, base_policy.chooser)
    alt_chosen = choose_decision_sides(rows, policy.chooser)
    if v2_chosen.empty and alt_chosen.empty:
        return enrich_selected(rows.iloc[0:0].copy())

    v2_cols = [
        "decision_key",
        "side",
        "ask_cents",
        "seconds_to_close",
        base_policy.chooser,
    ]
    alt_cols = [
        "decision_key",
        "side",
        "ask_cents",
        "seconds_to_close",
        policy.chooser,
        "margin_per_rv_sigma_15m",
        "brownian_p_rv_15m",
        "brownian_p_rv_30m",
    ]
    for col in alt_cols:
        if col not in alt_chosen.columns:
            alt_chosen[col] = np.nan
    paired = rows.merge(
        v2_chosen[v2_cols].rename(
            columns={
                "side": "v2_side",
                "ask_cents": "v2_ask_cents",
                "seconds_to_close": "v2_seconds_to_close",
                base_policy.chooser: "v2_score",
            }
        ),
        on="decision_key",
        how="left",
    ).merge(
        alt_chosen[alt_cols].rename(
            columns={
                "side": "alt_side",
                "ask_cents": "alt_ask_cents",
                "seconds_to_close": "alt_seconds_to_close",
                policy.chooser: "alt_score",
                "margin_per_rv_sigma_15m": "alt_margin_per_rv_sigma_15m",
                "brownian_p_rv_15m": "alt_brownian_p_rv_15m",
                "brownian_p_rv_30m": "alt_brownian_p_rv_30m",
            }
        ),
        on="decision_key",
        how="left",
    )

    v2_pass = (
        pd.to_numeric(paired["v2_score"], errors="coerce").ge(base_policy.min_score)
        & pd.to_numeric(paired["v2_ask_cents"], errors="coerce").le(base_policy.ask_max)
        & pd.to_numeric(paired["v2_seconds_to_close"], errors="coerce").ge(base_policy.min_seconds_to_close)
    ).fillna(False)
    alt_pass = (
        pd.to_numeric(paired["alt_score"], errors="coerce").ge(policy.min_score)
        & pd.to_numeric(paired["alt_ask_cents"], errors="coerce").le(policy.ask_max)
        & pd.to_numeric(paired["alt_seconds_to_close"], errors="coerce").ge(policy.min_seconds)
    ).fillna(False)
    if policy.gate == "margin_rv15>=0":
        alt_pass &= pd.to_numeric(paired["alt_margin_per_rv_sigma_15m"], errors="coerce").ge(0.0).fillna(False)
    elif policy.gate == "brownian15>=0.55_and_brownian30>=0.55":
        alt_pass &= (
            pd.to_numeric(paired["alt_brownian_p_rv_15m"], errors="coerce").ge(0.55)
            & pd.to_numeric(paired["alt_brownian_p_rv_30m"], errors="coerce").ge(0.55)
        ).fillna(False)
    elif policy.gate != "none":
        raise ValueError(policy.gate)
    is_v2_row = paired["side"].astype(str).eq(paired["v2_side"].astype(str))
    is_alt_row = paired["side"].astype(str).eq(paired["alt_side"].astype(str))
    disagrees = paired["v2_side"].astype(str).ne(paired["alt_side"].astype(str))
    override = alt_pass & is_alt_row
    if policy.require_disagree:
        override &= disagrees
    base = v2_pass & is_v2_row
    if not policy.fallback_when_v2_fails:
        override &= v2_pass
    selected_rows = paired[override | (base & ~override.groupby(paired["decision_key"]).transform("any"))].copy()
    if selected_rows.empty:
        return enrich_selected(selected_rows)
    selected_rows["override_used"] = override.loc[selected_rows.index].astype(bool).values
    selected = (
        selected_rows.sort_values(["market", "entry_dt"])
        .groupby("market", as_index=False, sort=False)
        .first()
        .sort_values(["entry_dt", "market"])
        .reset_index(drop=True)
    )
    selected["override_policy"] = policy.label
    return enrich_selected(selected)


def coverage_pass(metrics: Dict[str, Dict[str, Any]]) -> bool:
    return (
        all((metrics[split]["coverage"] or 0.0) >= MARKET_COVERAGE_FLOOR for split in ["all", "train", "validation", "holdout"])
        and metrics["all"]["markets"] >= MIN_SELECTED_MARKETS
        and metrics["holdout"]["markets"] >= MIN_HOLDOUT_SELECTED_MARKETS
    )


def oos_positive(metrics: Dict[str, Dict[str, Any]]) -> bool:
    return all((metrics[split]["net_pnl_cents"] or 0.0) > 0.0 for split in ["validation", "holdout"])


def flatten(
    policy: OverridePolicy,
    current_metrics: Dict[str, Dict[str, Any]],
    v21_metrics: Dict[str, Dict[str, Any]],
    base_current: float,
    base_v21: float,
) -> Dict[str, Any]:
    row: Dict[str, Any] = {
        "label": policy.label,
        "chooser": policy.chooser,
        "min_score": policy.min_score,
        "ask_max": policy.ask_max,
        "min_seconds": policy.min_seconds,
        "gate": policy.gate,
        "require_disagree": policy.require_disagree,
        "fallback_when_v2_fails": policy.fallback_when_v2_fails,
        "current_coverage_pass": coverage_pass(current_metrics),
        "v21_coverage_pass": coverage_pass(v21_metrics),
        "both_coverage_pass": coverage_pass(current_metrics) and coverage_pass(v21_metrics),
        "current_oos_positive": oos_positive(current_metrics),
        "v21_oos_positive": oos_positive(v21_metrics),
        "both_oos_positive": oos_positive(current_metrics) and oos_positive(v21_metrics),
    }
    row["current_delta_vs_v2_cents"] = (current_metrics["all"]["net_pnl_cents"] or 0.0) - base_current
    row["v21_delta_vs_v2_cents"] = (v21_metrics["all"]["net_pnl_cents"] or 0.0) - base_v21
    row["combined_delta_vs_v2_cents"] = row["current_delta_vs_v2_cents"] + row["v21_delta_vs_v2_cents"]
    row["min_oos_roi"] = min(
        current_metrics["validation"]["net_roi_on_cost"] or -1.0,
        current_metrics["holdout"]["net_roi_on_cost"] or -1.0,
        v21_metrics["validation"]["net_roi_on_cost"] or -1.0,
        v21_metrics["holdout"]["net_roi_on_cost"] or -1.0,
    )
    for prefix, metrics in [("current", current_metrics), ("v21", v21_metrics)]:
        for split, values in metrics.items():
            for key, value in values.items():
                row[f"{prefix}_{split}_{key}"] = value
    return row


def write_report(generated: str, rows: pd.DataFrame, base_current: float, base_v21: float) -> None:
    top = rows[rows["both_coverage_pass"]].copy()
    top = top.sort_values(
        ["both_oos_positive", "combined_delta_vs_v2_cents", "min_oos_roi"],
        ascending=[False, False, False],
    ).head(20)
    lines = [
        "# V2 Consensus Override Scan",
        "",
        f"Generated UTC: `{generated}`",
        "",
        "## Scope",
        "",
        "- Research-only scan; no orders are submitted and no bot files or live processes are touched.",
        "- Keeps Brownian v2 as default and flips only at the same heartbeat when a consensus chooser disagrees.",
        "- This avoids late-switch optionality and preserves the recurring-market coverage unit.",
        "",
        "## Baseline",
        "",
        f"- Current v2 baseline: {fmt_cents(base_current)}",
        f"- V21 v2 baseline: {fmt_cents(base_v21)}",
        "",
        "## Summary",
        "",
        f"- Hybrid policies scanned: {len(rows)}",
        f"- Both-dataset 80% coverage policies: {int(rows['both_coverage_pass'].sum())}",
        f"- Both-dataset OOS-positive policies: {int((rows['both_coverage_pass'] & rows['both_oos_positive']).sum())}",
        "",
        "## Top Rows",
        "",
        "| rank | policy | delta current/v21 | current net/acc/cov | v21 net/acc/cov | OOS ROI floor |",
        "|---:|---|---:|---:|---:|---:|",
    ]
    for rank, (_, row) in enumerate(top.iterrows(), start=1):
        lines.append(
            f"| {rank} | `{row['label']}` | "
            f"{fmt_cents(row['current_delta_vs_v2_cents'])}/{fmt_cents(row['v21_delta_vs_v2_cents'])} | "
            f"{fmt_cents(row['current_all_net_pnl_cents'])}/{pct(row['current_all_accuracy'])}/{pct(row['current_all_coverage'])} | "
            f"{fmt_cents(row['v21_all_net_pnl_cents'])}/{pct(row['v21_all_accuracy'])}/{pct(row['v21_all_coverage'])} | "
            f"{fmt_roi(row['min_oos_roi'])} |"
        )
    lines += ["", "## Read", ""]
    if top.empty:
        lines.append("- No hybrid policy preserved 80% coverage on both datasets.")
    else:
        best = top.iloc[0]
        lines.append(
            f"- Best hybrid row: `{best['label']}` with current/v21 delta "
            f"{fmt_cents(best['current_delta_vs_v2_cents'])}/{fmt_cents(best['v21_delta_vs_v2_cents'])}."
        )
        if bool(best["both_oos_positive"]) and best["combined_delta_vs_v2_cents"] > 0:
            lines.append("- This is worth forward-lock consideration, not promotion.")
        else:
            lines.append("- No hybrid beats v2 robustly enough to lock.")
    REPORT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    generated = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%SZ")
    current_side = load_side_rows()
    v21_side = load_v21_side_rows()
    current_base = market_base(current_side)
    v21_base = market_base(v21_side)
    current_v2 = select_v2(current_side, current_base)
    v21_v2 = select_v2(v21_side, v21_base)
    base_current = float(current_v2["net_pnl_cents"].sum())
    base_v21 = float(v21_v2["net_pnl_cents"].sum())
    rows: List[Dict[str, Any]] = []
    for policy in make_policies():
        current_selected = selected_hybrid(current_side, current_base, policy)
        v21_selected = selected_hybrid(v21_side, v21_base, policy)
        rows.append(
            flatten(
                policy,
                metrics_for(current_base, current_selected),
                metrics_for(v21_base, v21_selected),
                base_current,
                base_v21,
            )
        )
    df = pd.DataFrame(rows)
    df.to_csv(REPORT_CSV, index=False)
    REPORT_JSON.write_text(
        json.dumps({"generated_utc": generated, "rows": clean_json_local(df.to_dict(orient="records"))}, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    write_report(generated, df, base_current, base_v21)
    print("V2 consensus override scan complete")
    print(f"policies={len(df)} coverage_pass={int(df['both_coverage_pass'].sum())}")
    print(f"report={REPORT_MD}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
