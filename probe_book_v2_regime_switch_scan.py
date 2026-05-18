"""Book/Brownian regime-switch scan for BTC 15m profit locks.

Recent strict rows show a regime flip: later book/score pressure lost to
earlier Brownian-side entries. This probe asks whether a physically
interpretable switch rule can preserve recurring-market coverage while choosing
between the high-coverage book anchor and Brownian/score references.

Research-only: no orders are submitted and no bot files or live processes are
modified. Pair-dependent rows are diagnostic only; forward locks must be causal.
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Dict, Iterable, List, Optional

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


REPORT_MD = OUT_DIR / "book_v2_regime_switch_scan_latest.md"
REPORT_JSON = OUT_DIR / "book_v2_regime_switch_scan_latest.json"
REPORT_CSV = OUT_DIR / "book_v2_regime_switch_scan_latest.csv"

ANCHORS = ["book_margin", "book_margin_early"]
REFERENCES = ["frontier_v2", "score_min60", "score_min60_gap020"]


@dataclass(frozen=True)
class Condition:
    scope: str
    feature: str
    op: str
    threshold: Optional[float] = None

    @property
    def label(self) -> str:
        if self.feature in {"none", "side_disagree", "ref_earlier", "ref_earlier_side_disagree", "anchor_earlier_side_disagree"}:
            return self.feature
        if self.op == "hour==":
            return f"{self.scope}_{self.feature}=={int(self.threshold or 0):02d}"
        return f"{self.scope}_{self.feature}{self.op}{self.threshold:g}"


@dataclass(frozen=True)
class SwitchRule:
    anchor: str
    reference: str
    condition: Condition

    @property
    def label(self) -> str:
        if self.condition.feature == "none":
            return f"{self.anchor}_baseline"
        return f"{self.anchor}_switch_to_{self.reference}_if_{self.condition.label}"

    @property
    def causal_class(self) -> str:
        if self.condition.scope in {"anchor", "reference"}:
            return f"{self.condition.scope}_only"
        if self.condition.feature == "none":
            return "baseline"
        return "pair_diagnostic"


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
        name: select_policy(side_rows, base, name).copy()
        for name in sorted(set(ANCHORS + REFERENCES))
    }
    for frame in selected.values():
        if not frame.empty:
            frame["entry_dt"] = pd.to_datetime(frame["entry_dt"], utc=True, errors="coerce")
            frame["entry_hour_utc"] = frame["entry_dt"].dt.hour
    return base, selected


def numeric_conditions(scope: str, frame: pd.DataFrame) -> Iterable[Condition]:
    specs = [
        ("entry_hour_utc", "hour==", list(range(24))),
        ("ask_cents", "<=", [40, 50, 60, 65, 70, 75, 80]),
        ("ask_cents", ">=", [60, 65, 70, 75, 80]),
        ("seconds_to_close", ">=", [360, 480, 600, 720, 840]),
        ("book_p_side", "<=", [0.45, 0.50, 0.55, 0.60, 0.65]),
        ("book_p_side", ">=", [0.60, 0.65, 0.70, 0.75, 0.80]),
        ("brownian_p_rv_15m", ">=", [0.55, 0.60, 0.65, 0.70, 0.75]),
        ("brownian_p_rv_15m", "<=", [0.45, 0.50, 0.55, 0.60, 0.65]),
        ("abs_book_rv15_gap", ">=", [0.05, 0.10, 0.15, 0.20, 0.25]),
        ("abs_book_rv15_gap", "<=", [0.05, 0.10, 0.15, 0.20]),
        ("adverse_move_15m", ">=", [25, 50, 75, 100, 150, 200, 250]),
        ("adverse_move_15m", "<=", [10, 25, 50, 75, 100]),
        ("margin_per_rv_sigma_15m", "<=", [0.0, 0.25, 0.50, 0.75]),
        ("margin_per_rv_sigma_15m", ">=", [0.0, 0.25, 0.50, 0.75, 1.0]),
        ("touch_loss_rv_15m", ">=", [0.50, 0.75, 0.90, 1.00]),
        ("touch_loss_rv_15m", "<=", [0.50, 0.75, 0.90]),
    ]
    for feature, op, thresholds in specs:
        if feature not in frame.columns:
            continue
        for threshold in thresholds:
            yield Condition(scope, feature, op, float(threshold))


def all_conditions(anchor_rows: pd.DataFrame, reference_rows: pd.DataFrame) -> List[Condition]:
    out = [Condition("pair", "none", "")]
    out.extend(numeric_conditions("anchor", anchor_rows))
    out.extend(numeric_conditions("reference", reference_rows))
    out.extend(
        [
            Condition("pair", "side_disagree", ""),
            Condition("pair", "ref_earlier", ""),
            Condition("pair", "ref_earlier_side_disagree", ""),
            Condition("pair", "anchor_earlier_side_disagree", ""),
        ]
    )
    return out


def condition_mask(pair: pd.DataFrame, condition: Condition) -> pd.Series:
    if pair.empty:
        return pd.Series(dtype=bool)
    if condition.feature == "none":
        return pd.Series([False] * len(pair), index=pair.index)
    if condition.feature == "side_disagree":
        return pair["side_anchor"].astype(str).ne(pair["side_reference"].astype(str)).fillna(False)
    if condition.feature == "ref_earlier":
        return pair["reference_minus_anchor_seconds"].lt(-1e-6).fillna(False)
    if condition.feature == "ref_earlier_side_disagree":
        return (
            pair["reference_minus_anchor_seconds"].lt(-1e-6)
            & pair["side_anchor"].astype(str).ne(pair["side_reference"].astype(str))
        ).fillna(False)
    if condition.feature == "anchor_earlier_side_disagree":
        return (
            pair["reference_minus_anchor_seconds"].gt(1e-6)
            & pair["side_anchor"].astype(str).ne(pair["side_reference"].astype(str))
        ).fillna(False)

    col = f"{condition.feature}_{condition.scope}"
    if col not in pair.columns:
        return pd.Series([False] * len(pair), index=pair.index)
    values = pd.to_numeric(pair[col], errors="coerce")
    threshold = float(condition.threshold or 0.0)
    if condition.op == "hour==":
        return values.eq(threshold).fillna(False)
    if condition.op == "<=":
        return values.le(threshold).fillna(False)
    if condition.op == ">=":
        return values.ge(threshold).fillna(False)
    raise ValueError(condition.op)


def paired(anchor: pd.DataFrame, reference: pd.DataFrame) -> pd.DataFrame:
    cols = [
        "market",
        "split",
        "side",
        "ask_cents",
        "entry_dt",
        "seconds_to_close",
        "book_p_side",
        "brownian_p_rv_15m",
        "abs_book_rv15_gap",
        "adverse_move_15m",
        "margin_per_rv_sigma_15m",
        "touch_loss_rv_15m",
        "entry_hour_utc",
    ]
    left = anchor[[col for col in cols if col in anchor.columns]].copy()
    right = reference[[col for col in cols if col in reference.columns]].copy()
    pair = left.merge(right, on=["market", "split"], suffixes=("_anchor", "_reference"))
    if pair.empty:
        return pair
    pair["entry_dt_anchor"] = pd.to_datetime(pair["entry_dt_anchor"], utc=True, errors="coerce")
    pair["entry_dt_reference"] = pd.to_datetime(pair["entry_dt_reference"], utc=True, errors="coerce")
    pair["reference_minus_anchor_seconds"] = (
        pair["entry_dt_reference"] - pair["entry_dt_anchor"]
    ).dt.total_seconds()
    return pair


def apply_rule(anchor: pd.DataFrame, reference: pd.DataFrame, rule: SwitchRule) -> pd.DataFrame:
    if anchor.empty and reference.empty:
        return anchor
    anchor_by_market = {str(row["market"]): row for _, row in anchor.iterrows()}
    reference_by_market = {str(row["market"]): row for _, row in reference.iterrows()}
    pair = paired(anchor, reference)
    trigger_by_market = {}
    if not pair.empty:
        triggers = condition_mask(pair, rule.condition)
        trigger_by_market = {
            str(row["market"]): bool(triggers.loc[idx])
            for idx, row in pair.iterrows()
        }

    rows: List[pd.Series] = []
    for market in sorted(set(anchor_by_market) | set(reference_by_market)):
        anchor_row = anchor_by_market.get(market)
        reference_row = reference_by_market.get(market)
        trigger = trigger_by_market.get(market, False)
        if rule.condition.feature == "none":
            if anchor_row is not None:
                rows.append(anchor_row)
            elif reference_row is not None:
                rows.append(reference_row)
        elif rule.condition.scope == "anchor":
            if anchor_row is None:
                if reference_row is not None:
                    rows.append(reference_row)
            elif trigger:
                if reference_row is not None:
                    rows.append(reference_row)
            else:
                rows.append(anchor_row)
        elif rule.condition.scope == "reference":
            if reference_row is None:
                continue
            if trigger:
                rows.append(reference_row)
            elif anchor_row is not None:
                anchor_dt = pd.to_datetime(anchor_row.get("entry_dt"), utc=True, errors="coerce")
                reference_dt = pd.to_datetime(reference_row.get("entry_dt"), utc=True, errors="coerce")
                if not pd.isna(anchor_dt) and not pd.isna(reference_dt) and reference_dt <= anchor_dt:
                    rows.append(anchor_row)
        else:
            if trigger and reference_row is not None:
                rows.append(reference_row)
            elif anchor_row is not None:
                rows.append(anchor_row)
            elif reference_row is not None:
                rows.append(reference_row)
    if not rows:
        return anchor.iloc[0:0].copy()
    out = pd.DataFrame(rows).drop_duplicates(subset=["market"], keep="first")
    out = out.sort_values(["entry_dt", "market"]).reset_index(drop=True)
    out["switch_rule"] = rule.label
    out["causal_class"] = rule.causal_class
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
    rule: SwitchRule,
    current_metrics: Dict[str, Dict[str, Any]],
    v21_metrics: Dict[str, Dict[str, Any]],
    current_anchor_net: float,
    v21_anchor_net: float,
) -> Dict[str, Any]:
    row: Dict[str, Any] = {
        "label": rule.label,
        "anchor": rule.anchor,
        "reference": rule.reference,
        "condition": rule.condition.label,
        "condition_scope": rule.condition.scope,
        "causal_class": rule.causal_class,
        "current_coverage_pass": coverage_pass(current_metrics),
        "v21_coverage_pass": coverage_pass(v21_metrics),
        "both_coverage_pass": coverage_pass(current_metrics) and coverage_pass(v21_metrics),
        "current_oos_positive": oos_positive(current_metrics),
        "v21_oos_positive": oos_positive(v21_metrics),
        "both_oos_positive": oos_positive(current_metrics) and oos_positive(v21_metrics),
    }
    row["current_delta_vs_anchor_cents"] = (current_metrics["all"]["net_pnl_cents"] or 0.0) - current_anchor_net
    row["v21_delta_vs_anchor_cents"] = (v21_metrics["all"]["net_pnl_cents"] or 0.0) - v21_anchor_net
    row["combined_delta_vs_anchor_cents"] = row["current_delta_vs_anchor_cents"] + row["v21_delta_vs_anchor_cents"]
    row["both_delta_positive"] = row["current_delta_vs_anchor_cents"] > 0 and row["v21_delta_vs_anchor_cents"] > 0
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


def run_scan() -> pd.DataFrame:
    current_base, current_selected = prepare_selected(load_side_rows())
    v21_base, v21_selected = prepare_selected(load_v21_side_rows())
    rows: List[Dict[str, Any]] = []
    for anchor_name in ANCHORS:
        current_anchor = current_selected[anchor_name]
        v21_anchor = v21_selected[anchor_name]
        current_anchor_net = float(enrich_selected(current_anchor)["net_pnl_cents"].sum())
        v21_anchor_net = float(enrich_selected(v21_anchor)["net_pnl_cents"].sum())
        for reference_name in REFERENCES:
            current_reference = current_selected[reference_name]
            v21_reference = v21_selected[reference_name]
            conditions = all_conditions(current_anchor, current_reference)
            for condition in conditions:
                rule = SwitchRule(anchor_name, reference_name, condition)
                current_rule = apply_rule(current_anchor, current_reference, rule)
                v21_rule = apply_rule(v21_anchor, v21_reference, rule)
                rows.append(
                    flatten(
                        rule,
                        metrics_for(current_base, current_rule),
                        metrics_for(v21_base, v21_rule),
                        current_anchor_net,
                        v21_anchor_net,
                    )
                )
    return pd.DataFrame(rows)


def write_report(generated: str, rows: pd.DataFrame) -> None:
    eligible = rows[rows["both_coverage_pass"]].copy()
    top = eligible.sort_values(
        ["both_oos_positive", "combined_delta_vs_anchor_cents", "min_oos_roi"],
        ascending=[False, False, False],
    ).head(25)
    causal = eligible[
        eligible["causal_class"].isin(["anchor_only", "reference_only"])
        & eligible["both_oos_positive"]
        & eligible["both_delta_positive"]
    ].sort_values(["combined_delta_vs_anchor_cents", "min_oos_roi"], ascending=[False, False]).head(10)

    lines = [
        "# Book V2 Regime Switch Scan",
        "",
        f"Generated UTC: `{generated}`",
        "",
        "## Scope",
        "",
        "- Research-only scan; no orders are submitted and no bot files or live processes are touched.",
        "- Tests high-coverage switches between book-margin anchors and Brownian/score references on current and v21 ledgers.",
        "- Pair-dependent rules are diagnostic only. Forward candidates must be physically interpretable and causal.",
        "- Anchor-only and reference-only switch rows use executable within-market semantics; reference-conditioned false fallbacks cannot claim earlier anchor prices.",
        "- Best causal rows must improve both datasets individually; combined positive delta is not enough.",
        "",
        "## Summary",
        "",
        f"- Rules scanned: {len(rows)}",
        f"- Both-dataset 80% coverage rules: {int(rows['both_coverage_pass'].sum())}",
        f"- Both-dataset OOS-positive coverage rules: {int((rows['both_coverage_pass'] & rows['both_oos_positive']).sum())}",
        f"- Causal-class positive coverage rules: {len(causal)}",
        "",
        "## Top Rows",
        "",
        "| rank | rule | class | delta current/v21 | current net/acc/cov | v21 net/acc/cov | OOS ROI floor |",
        "|---:|---|---|---:|---:|---:|---:|",
    ]
    for rank, (_, row) in enumerate(top.iterrows(), start=1):
        lines.append(
            f"| {rank} | `{row['label']}` | {row['causal_class']} | "
            f"{fmt_cents(row['current_delta_vs_anchor_cents'])}/{fmt_cents(row['v21_delta_vs_anchor_cents'])} | "
            f"{fmt_cents(row['current_all_net_pnl_cents'])}/{pct(row['current_all_accuracy'])}/{pct(row['current_all_coverage'])} | "
            f"{fmt_cents(row['v21_all_net_pnl_cents'])}/{pct(row['v21_all_accuracy'])}/{pct(row['v21_all_coverage'])} | "
            f"{fmt_roi(row['min_oos_roi'])} |"
        )

    lines += [
        "",
        "## Best Causal-Class Rows",
        "",
        "| rank | rule | class | delta current/v21 | current net/acc/cov | v21 net/acc/cov | OOS ROI floor |",
        "|---:|---|---|---:|---:|---:|---:|",
    ]
    for rank, (_, row) in enumerate(causal.iterrows(), start=1):
        lines.append(
            f"| {rank} | `{row['label']}` | {row['causal_class']} | "
            f"{fmt_cents(row['current_delta_vs_anchor_cents'])}/{fmt_cents(row['v21_delta_vs_anchor_cents'])} | "
            f"{fmt_cents(row['current_all_net_pnl_cents'])}/{pct(row['current_all_accuracy'])}/{pct(row['current_all_coverage'])} | "
            f"{fmt_cents(row['v21_all_net_pnl_cents'])}/{pct(row['v21_all_accuracy'])}/{pct(row['v21_all_coverage'])} | "
            f"{fmt_roi(row['min_oos_roi'])} |"
        )
    if causal.empty:
        lines.append("|  | No causal-class switch improved both datasets while preserving coverage. |  |  |  |  |  |")

    lines += ["", "## Read", ""]
    if top.empty:
        lines.append("- No switch rule preserved 80% market coverage on both datasets.")
    else:
        best = top.iloc[0]
        lines.append(
            f"- Best coverage-valid rule: `{best['label']}` with current/v21 delta "
            f"{fmt_cents(best['current_delta_vs_anchor_cents'])}/{fmt_cents(best['v21_delta_vs_anchor_cents'])}."
        )
        if str(best["causal_class"]) == "pair_diagnostic":
            lines.append("- The top rule is pair-dependent, so it explains the failure mode but is not directly forward-lockable.")
    if causal.empty:
        lines.append("- No single observable causal trigger is strong enough to forward-lock from this scan.")
    else:
        best_causal = causal.iloc[0]
        lines.append(
            f"- Best causal-class candidate is `{best_causal['label']}`, but it still needs strict forward registration before use."
        )
    lines.append("- Goal remains strict live sample size plus >=75-80% recurring-market coverage, not retrospective scan rank.")
    REPORT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    generated = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%SZ")
    df = run_scan()
    df.to_csv(REPORT_CSV, index=False)
    REPORT_JSON.write_text(
        json.dumps({"generated_utc": generated, "rows": clean_json_local(df.to_dict(orient="records"))}, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    write_report(generated, df)
    print("Book/V2 regime-switch scan complete")
    print(f"rules={len(df)} coverage_pass={int(df['both_coverage_pass'].sum())}")
    print(f"report={REPORT_MD}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
