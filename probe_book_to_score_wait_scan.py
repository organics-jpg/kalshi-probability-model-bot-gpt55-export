"""Causal book-to-score wait scan for BTC 15m profit candidates.

The temporal side-flip diagnostic shows that early book rows are often cheaper
when the later score model agrees, but can be wrong when the later score model
flips side. This probe tests causal wait rules that decide from the first book
row only:

- no trigger: enter the book-style row immediately;
- trigger: wait for the first later score-style row in the same market, then
  either enter that score row or only enter it if the side flipped.

Research-only: no orders are submitted and no bot files or live processes are
modified. Passing rows are diagnostic forward-test candidates only.
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Dict, Iterable, List

import pandas as pd

from probe_cross_dataset_interval_frontier import load_v21_side_rows
from probe_cross_dataset_profit_frontier import enrich_selected, fmt_cents, fmt_roi, metrics_for
from probe_frontier_candidate_v2_diagnostic import select_policy
from probe_market_interval_80coverage import (
    MARKET_COVERAGE_FLOOR,
    MIN_HOLDOUT_SELECTED_MARKETS,
    MIN_SELECTED_MARKETS,
    OUT_DIR,
    clean_json,
    load_side_rows,
    market_base,
    pct,
)


REPORT_MD = OUT_DIR / "book_to_score_wait_scan_latest.md"
REPORT_JSON = OUT_DIR / "book_to_score_wait_scan_latest.json"
REPORT_CSV = OUT_DIR / "book_to_score_wait_scan_latest.csv"

ANCHORS = ["book_margin", "book_margin_early", "book_margin_gap015"]
REFERENCES = ["score_min60", "score_min60_gap020"]
MODES = ["enter_ref", "switch_only"]


@dataclass(frozen=True)
class Condition:
    feature: str
    op: str
    threshold: float

    @property
    def label(self) -> str:
        if self.feature == "none":
            return "none"
        return f"{self.feature}{self.op}{self.threshold:g}"


@dataclass(frozen=True)
class WaitRule:
    anchor: str
    reference: str
    mode: str
    condition: Condition

    @property
    def label(self) -> str:
        if self.condition.feature == "none":
            return f"{self.anchor}_baseline"
        return f"{self.anchor}_wait_for_{self.reference}_{self.mode}_if_{self.condition.label}"


def clean_json_local(value: Any) -> Any:
    if isinstance(value, pd.Timestamp):
        return value.isoformat()
    if isinstance(value, dict):
        return {str(k): clean_json_local(v) for k, v in value.items()}
    if isinstance(value, list):
        return [clean_json_local(v) for v in value]
    return clean_json(value)


def prepare_selected(side_rows: pd.DataFrame) -> tuple[pd.DataFrame, Dict[str, pd.DataFrame]]:
    base = market_base(side_rows)
    selected = {
        name: select_policy(side_rows, base, name)
        for name in sorted(set(ANCHORS + REFERENCES))
    }
    for name, frame in selected.items():
        selected[name] = frame.copy()
        selected[name]["entry_dt"] = pd.to_datetime(selected[name]["entry_dt"], utc=True, errors="coerce")
    return base, selected


def available_conditions(anchor_rows: pd.DataFrame) -> Iterable[Condition]:
    specs = [
        ("seconds_to_close", ">=", [360, 480, 600, 720, 840]),
        ("book_p_side", "<=", [0.60, 0.65, 0.70]),
        ("brownian_p_rv_15m", "<=", [0.55, 0.60, 0.65, 0.70]),
        ("score_min_book_rv15", "<=", [0.55, 0.60, 0.65, 0.70]),
        ("abs_book_rv15_gap", ">=", [0.05, 0.10, 0.15, 0.20, 0.25]),
        ("adverse_move_15m", ">=", [25, 50, 75, 100, 125]),
        ("touch_loss_rv_15m", ">=", [0.50, 0.75, 1.00]),
        ("ask_cents", ">=", [65, 70, 75]),
        ("spread_cents", ">=", [2, 3, 4]),
    ]
    yield Condition("none", ">=", 0.0)
    for feature, op, thresholds in specs:
        if feature not in anchor_rows.columns:
            continue
        for threshold in thresholds:
            yield Condition(feature, op, float(threshold))


def condition_mask(rows: pd.DataFrame, condition: Condition) -> pd.Series:
    if condition.feature == "none":
        return pd.Series([False] * len(rows), index=rows.index)
    values = pd.to_numeric(rows[condition.feature], errors="coerce")
    if condition.op == "<=":
        return values.le(condition.threshold).fillna(False)
    if condition.op == ">=":
        return values.ge(condition.threshold).fillna(False)
    raise ValueError(condition.op)


def reference_after_map(anchor_rows: pd.DataFrame, reference_rows: pd.DataFrame) -> Dict[Any, pd.Series]:
    anchor = anchor_rows.copy()
    reference = reference_rows.copy()
    if anchor.empty:
        return {}
    reference_groups = {
        str(market): part.sort_values(["entry_dt", "market"]).copy()
        for market, part in reference.groupby("market", sort=False)
    }
    out: Dict[Any, pd.Series] = {}
    for idx, row in anchor.iterrows():
        ref = reference_groups.get(str(row["market"]))
        if ref is None or ref.empty:
            continue
        row_dt = row["entry_dt"]
        if not pd.isna(row_dt):
            ref = ref[ref["entry_dt"].ge(row_dt)]
        if not ref.empty:
            out[idx] = ref.iloc[0]
    return out


def apply_rule(anchor_rows: pd.DataFrame, reference_after: Dict[Any, pd.Series], rule: WaitRule) -> pd.DataFrame:
    anchor = anchor_rows.copy()
    if anchor.empty:
        return anchor
    trigger = condition_mask(anchor, rule.condition)
    rows: List[pd.Series] = []
    for idx, row in anchor.sort_values(["entry_dt", "market"]).iterrows():
        if not bool(trigger.loc[idx]):
            rows.append(row)
            continue
        ref_row = reference_after.get(idx)
        if ref_row is None:
            continue
        if rule.mode == "switch_only" and str(ref_row.get("side")) == str(row.get("side")):
            continue
        rows.append(ref_row)
    if not rows:
        return anchor.iloc[0:0].copy()
    out = pd.DataFrame(rows).drop_duplicates(subset=["market"], keep="first")
    out = out.sort_values(["entry_dt", "market"]).reset_index(drop=True)
    out["wait_rule"] = rule.label
    return enrich_selected(out)


def coverage_pass(metrics: Dict[str, Dict[str, Any]]) -> bool:
    return (
        all((metrics[split]["coverage"] or 0.0) >= MARKET_COVERAGE_FLOOR for split in ["all", "train", "validation", "holdout"])
        and metrics["all"]["markets"] >= MIN_SELECTED_MARKETS
        and metrics["holdout"]["markets"] >= MIN_HOLDOUT_SELECTED_MARKETS
    )


def oos_positive(metrics: Dict[str, Dict[str, Any]]) -> bool:
    return all((metrics[split]["net_pnl_cents"] or 0.0) > 0.0 for split in ["validation", "holdout"])


def flatten(
    rule: WaitRule,
    current_metrics: Dict[str, Dict[str, Any]],
    v21_metrics: Dict[str, Dict[str, Any]],
    current_base_net: float,
    v21_base_net: float,
) -> Dict[str, Any]:
    row: Dict[str, Any] = {
        "label": rule.label,
        "anchor": rule.anchor,
        "reference": rule.reference,
        "mode": rule.mode,
        "condition": rule.condition.label,
        "current_coverage_pass": coverage_pass(current_metrics),
        "v21_coverage_pass": coverage_pass(v21_metrics),
        "both_coverage_pass": coverage_pass(current_metrics) and coverage_pass(v21_metrics),
        "current_oos_positive": oos_positive(current_metrics),
        "v21_oos_positive": oos_positive(v21_metrics),
        "both_oos_positive": oos_positive(current_metrics) and oos_positive(v21_metrics),
    }
    row["current_delta_vs_anchor_cents"] = (current_metrics["all"]["net_pnl_cents"] or 0.0) - current_base_net
    row["v21_delta_vs_anchor_cents"] = (v21_metrics["all"]["net_pnl_cents"] or 0.0) - v21_base_net
    row["combined_delta_vs_anchor_cents"] = row["current_delta_vs_anchor_cents"] + row["v21_delta_vs_anchor_cents"]
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


def write_report(generated: str, rows: pd.DataFrame) -> None:
    eligible = rows[rows["both_coverage_pass"]].copy()
    top = eligible.sort_values(
        ["both_oos_positive", "combined_delta_vs_anchor_cents", "min_oos_roi"],
        ascending=[False, False, False],
    ).head(25)
    lines = [
        "# Book To Score Wait Scan",
        "",
        f"Generated UTC: `{generated}`",
        "",
        "## Scope",
        "",
        "- Research-only scan; no orders are submitted and no bot files or live processes are touched.",
        "- Tests causal rules that decide from the first book-style row whether to wait for a later score-style row.",
        "- Passing rows are diagnostic only; promotion still requires strict pre-registered live evidence.",
        "",
        "## Summary",
        "",
        f"- Rules scanned: {len(rows)}",
        f"- Both-dataset 80% coverage rules: {int(rows['both_coverage_pass'].sum())}",
        f"- Both-dataset OOS-positive rules: {int((rows['both_coverage_pass'] & rows['both_oos_positive']).sum())}",
        "",
        "## Top Rows",
        "",
        "| rank | rule | delta current/v21 | current net/acc/cov | v21 net/acc/cov | OOS ROI floor |",
        "|---:|---|---:|---:|---:|---:|",
    ]
    for rank, (_, row) in enumerate(top.iterrows(), start=1):
        lines.append(
            f"| {rank} | `{row['label']}` | "
            f"{fmt_cents(row['current_delta_vs_anchor_cents'])}/{fmt_cents(row['v21_delta_vs_anchor_cents'])} | "
            f"{fmt_cents(row['current_all_net_pnl_cents'])}/{pct(row['current_all_accuracy'])}/{pct(row['current_all_coverage'])} | "
            f"{fmt_cents(row['v21_all_net_pnl_cents'])}/{pct(row['v21_all_accuracy'])}/{pct(row['v21_all_coverage'])} | "
            f"{fmt_roi(row['min_oos_roi'])} |"
        )
    lines += ["", "## Read", ""]
    if top.empty:
        lines.append("- No causal book-to-score wait rule preserved 80% coverage on both datasets.")
    else:
        best = top.iloc[0]
        lines.append(
            f"- Best coverage-valid row: `{best['label']}` with current/v21 delta "
            f"{fmt_cents(best['current_delta_vs_anchor_cents'])}/{fmt_cents(best['v21_delta_vs_anchor_cents'])}."
        )
        if bool(best["both_oos_positive"]) and float(best["combined_delta_vs_anchor_cents"]) > 0.0:
            lines.append("- Worth forward-lock consideration only if the trigger is physically interpretable and not just a timing artifact.")
        else:
            lines.append("- No wait rule improves the book anchors robustly enough to forward-lock.")
    REPORT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    generated = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%SZ")
    current_base, current_selected = prepare_selected(load_side_rows())
    v21_base, v21_selected = prepare_selected(load_v21_side_rows())
    rows: List[Dict[str, Any]] = []
    for anchor_name in ANCHORS:
        current_anchor = current_selected[anchor_name]
        v21_anchor = v21_selected[anchor_name]
        current_base_net = float(enrich_selected(current_anchor)["net_pnl_cents"].sum())
        v21_base_net = float(enrich_selected(v21_anchor)["net_pnl_cents"].sum())
        conditions = list(available_conditions(current_anchor))
        for reference_name in REFERENCES:
            current_reference_after = reference_after_map(current_anchor, current_selected[reference_name])
            v21_reference_after = reference_after_map(v21_anchor, v21_selected[reference_name])
            for condition in conditions:
                modes = ["enter_ref"] if condition.feature == "none" else MODES
                for mode in modes:
                    rule = WaitRule(anchor_name, reference_name, mode, condition)
                    current_rule = apply_rule(current_anchor, current_reference_after, rule)
                    v21_rule = apply_rule(v21_anchor, v21_reference_after, rule)
                    rows.append(
                        flatten(
                            rule,
                            metrics_for(current_base, current_rule),
                            metrics_for(v21_base, v21_rule),
                            current_base_net,
                            v21_base_net,
                        )
                    )
    df = pd.DataFrame(rows)
    df.to_csv(REPORT_CSV, index=False)
    REPORT_JSON.write_text(
        json.dumps({"generated_utc": generated, "rows": clean_json_local(df.to_dict(orient="records"))}, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    write_report(generated, df)
    print("Book-to-score wait scan complete")
    print(f"rules={len(df)} coverage_pass={int(df['both_coverage_pass'].sum())}")
    print(f"report={REPORT_MD}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
