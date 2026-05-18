"""Forward validation for a locked book/score reference-margin switch.

The regime-switch scan's best causal-class row switches from the book-margin
anchor to the score_min60_gap020 reference when the reference row's margin per
RV sigma is weak. This keeps the rule causal: the switch can only happen after
the reference row exists, and strict pre-resolution registry rows remain the
promotion authority.

Research-only: no orders are submitted and no bot files or live processes are
modified.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any, Dict

import pandas as pd

from probe_cross_dataset_profit_frontier import enrich_selected
from probe_market_interval_80coverage import MARKET_COVERAGE_FLOOR, OUT_DIR, clean_json, load_side_rows, market_base
from probe_profit_lock_pending_signal_monitor import BOOK_REFMARGIN_SCORE_SWITCH_LOCK_PATH, select_session_switch_rows
from probe_profit_lock_time_boundary import effective_lock_dt
from probe_v2_conditional_wait_forward_validation import (
    metric_for_strict_registry,
    metric_row,
    registry_recompute_divergence,
    strict_registry_rows,
)


LOCK_NAME = "book_refmargin_score_switch"
REPORT_MD = OUT_DIR / "profit_book_refmargin_score_switch_validation_latest.md"
REPORT_JSON = OUT_DIR / "profit_book_refmargin_score_switch_validation_latest.json"
SELECTED_CSV = OUT_DIR / "profit_book_refmargin_score_switch_selected_latest.csv"


def clean_json_local(value: Any) -> Any:
    if isinstance(value, pd.Timestamp):
        return value.isoformat()
    if isinstance(value, dict):
        return {str(k): clean_json_local(v) for k, v in value.items()}
    if isinstance(value, list):
        return [clean_json_local(v) for v in value]
    return clean_json(value)


def metric_for_scope(base: pd.DataFrame, selected: pd.DataFrame) -> Dict[str, Any]:
    from probe_cross_dataset_profit_frontier import split_metric

    metric = split_metric(base, selected, "all")
    metric["coverage_pass"] = (metric["coverage"] or 0.0) >= MARKET_COVERAGE_FLOOR
    metric["wilson_minus_break_even"] = (
        metric["wilson95_lower"] - metric["fee_aware_break_even_accuracy"]
        if metric["wilson95_lower"] is not None and metric["fee_aware_break_even_accuracy"] is not None
        else None
    )
    metric["positive_net"] = (metric["net_pnl_cents"] or 0.0) > 0.0
    return metric


def select_for_lock(side_rows: pd.DataFrame, base: pd.DataFrame, lock: Dict[str, Any]) -> pd.DataFrame:
    rows = side_rows.merge(base[["market", "split"]], on="market", how="inner")
    return enrich_selected(select_session_switch_rows(rows, lock))


def fresh_scope(side_rows: pd.DataFrame, base: pd.DataFrame, lock: Dict[str, Any]) -> tuple[pd.DataFrame, pd.DataFrame]:
    boundary = effective_lock_dt(lock)
    if pd.isna(boundary):
        return base.iloc[0:0].copy(), side_rows.iloc[0:0].copy()
    first_entry = pd.to_datetime(base["first_entry_dt"], utc=True, errors="coerce")
    close_dt = pd.to_datetime(base["close_dt"], utc=True, errors="coerce")
    fresh_base = base[first_entry.gt(boundary) & close_dt.gt(boundary)].copy()
    if fresh_base.empty:
        return fresh_base, side_rows.iloc[0:0].copy()
    side_work = side_rows.copy()
    side_work["entry_dt"] = pd.to_datetime(side_work["entry_dt"], utc=True, errors="coerce")
    side_work["close_dt"] = pd.to_datetime(side_work["close_dt"], utc=True, errors="coerce")
    fresh_side_rows = side_work[
        side_work["entry_dt"].gt(boundary)
        & side_work["close_dt"].gt(boundary)
        & side_work["market"].isin(set(fresh_base["market"]))
    ].copy()
    return fresh_base, select_for_lock(fresh_side_rows, fresh_base, lock)


def write_report(
    path,
    generated: str,
    lock: Dict[str, Any],
    all_metric: Dict[str, Any],
    fresh_metric: Dict[str, Any],
    strict_metric: Dict[str, Any],
    divergence: Dict[str, Any],
) -> None:
    effective_dt = effective_lock_dt(lock)
    switch = lock.get("switch_rule", {})
    lines = [
        "# Book Reference-Margin Score Switch Forward Validation",
        "",
        f"Generated UTC: `{generated}`",
        "",
        "## Scope",
        "",
        "- Research-only validation; no orders are submitted and no bot files or live processes are touched.",
        "- Locked rule: use book_margin, but switch to score_min60_gap020 when the reference margin per RV sigma is <=0.5.",
        "- This is forward-test evidence only; the regime-switch scan is not promotion evidence.",
        "",
        "## Lock",
        "",
        f"- Label: `{switch.get('label')}`",
        f"- Effective entry boundary: `{effective_dt.isoformat() if not pd.isna(effective_dt) else None}`",
        f"- Lock file: `{BOOK_REFMARGIN_SCORE_SWITCH_LOCK_PATH}`",
        "",
        "## Metrics",
        "",
        "| scope | markets | wins/losses | acc | break-even | Wilson low | Wilson edge | coverage | net P&L | net ROI | median ask |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for name, metric in [
        ("all current ledger", all_metric),
        ("recomputed fresh after lock", fresh_metric),
        ("strict registered fresh", strict_metric),
    ]:
        lines.append(metric_row(name, metric))
    lines += [
        "",
        "## Recompute Drift Check",
        "",
        f"- Compared strict and recomputed rows: {divergence['compared']}.",
        f"- Mismatched rows: {divergence['mismatches']}; missing recomputed rows: {divergence['missing_recompute']}.",
    ]
    for example in divergence["examples"]:
        lines.append(f"- `{example['market']}` strict `{example['strict']}` vs recomputed `{example['recomputed']}`.")
    lines += ["", "## Read", ""]
    if strict_metric["base_markets"] == 0:
        lines.append("- Reference-margin switch lock is waiting for post-boundary resolved markets.")
    elif strict_metric["positive_net"] and strict_metric["coverage_pass"]:
        lines.append("- Strict registered fresh sample is positive and coverage-valid so far, but strict registered sample size is still required.")
    else:
        lines.append("- Strict registered fresh sample is not promotion-quality proof.")
    lines.append("- The physical hypothesis is book-pressure fragility when the later score reference has weak RV-scaled margin.")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    generated = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%SZ")
    lock = json.loads(BOOK_REFMARGIN_SCORE_SWITCH_LOCK_PATH.read_text(encoding="utf-8"))
    side_rows = load_side_rows()
    base = market_base(side_rows)
    selected = select_for_lock(side_rows, base, lock)
    all_metric = metric_for_scope(base, selected)
    fresh_base, fresh_selected = fresh_scope(side_rows, base, lock)
    fresh_metric = metric_for_scope(fresh_base, fresh_selected)
    boundary = effective_lock_dt(lock)
    strict_rows = strict_registry_rows(LOCK_NAME, fresh_base, boundary)
    strict_metric = metric_for_strict_registry(fresh_base, strict_rows)
    divergence = registry_recompute_divergence(fresh_selected, strict_rows)

    selected.to_csv(SELECTED_CSV, index=False)
    selected.to_csv(OUT_DIR / f"profit_book_refmargin_score_switch_selected_{generated}.csv", index=False)

    md_stamp = OUT_DIR / f"profit_book_refmargin_score_switch_validation_{generated}.md"
    json_stamp = OUT_DIR / f"profit_book_refmargin_score_switch_validation_{generated}.json"
    write_report(REPORT_MD, generated, lock, all_metric, fresh_metric, strict_metric, divergence)
    write_report(md_stamp, generated, lock, all_metric, fresh_metric, strict_metric, divergence)
    payload = {
        "generated_utc": generated,
        "name": LOCK_NAME,
        "lock": lock,
        "all_metric": all_metric,
        "fresh_metric": fresh_metric,
        "strict_registered_metric": strict_metric,
        "registry_recompute_divergence": divergence,
    }
    for path in [REPORT_JSON, json_stamp]:
        path.write_text(json.dumps(clean_json_local(payload), indent=2, sort_keys=True), encoding="utf-8")
    print("Book reference-margin score switch forward validation complete")
    print(
        "strict_fresh_markets={markets} fresh_base={base_markets} fresh_net={net}c".format(
            markets=int(strict_metric["markets"]),
            base_markets=int(strict_metric["base_markets"]),
            net=float(strict_metric["net_pnl_cents"] or 0.0),
        )
    )
    print(f"report={REPORT_MD}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
