"""Fresh validation for locked frontier-derived profit policies.

This fills the validation sidecars for forward-locked policies that are tracked
by the strict pre-resolution registry. It reads existing lock files only; it
does not create locks, submit orders, or modify live bot code.
"""
from __future__ import annotations

import argparse
import json
import math
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

import pandas as pd

from probe_cross_dataset_profit_frontier import enrich_selected, fmt_cents, fmt_roi, split_metric
from probe_market_interval_80coverage import (
    MARKET_COVERAGE_FLOOR,
    OUT_DIR,
    Policy,
    choose_decision_sides,
    clean_json,
    gate_mask,
    load_side_rows,
    market_base,
    pct,
    select_markets_from_chosen,
)
from probe_profit_frontier_fresh_validation import policy_from_record
from probe_profit_lock_time_boundary import effective_lock_dt
from probe_v2_conditional_wait_forward_validation import (
    metric_for_strict_registry,
    metric_row,
    registry_recompute_divergence,
    strict_registry_rows,
)


@dataclass(frozen=True)
class LockSpec:
    name: str
    title: str
    lock_path: Path
    report_stem: str


LOCK_SPECS = [
    LockSpec(
        name="frontier_v2_continuous",
        title="Frontier V2 Continuous",
        lock_path=OUT_DIR / "profit_frontier_v2_continuous_lock.json",
        report_stem="profit_frontier_v2_continuous_validation",
    ),
    LockSpec(
        name="book_margin",
        title="Book Margin",
        lock_path=OUT_DIR / "profit_frontier_book_margin_lock.json",
        report_stem="profit_frontier_book_margin_validation",
    ),
    LockSpec(
        name="book_margin_early",
        title="Book Margin Early",
        lock_path=OUT_DIR / "profit_frontier_book_margin_early_lock.json",
        report_stem="profit_frontier_book_margin_early_validation",
    ),
    LockSpec(
        name="book_margin_gap015",
        title="Book Margin Gap015",
        lock_path=OUT_DIR / "profit_frontier_book_margin_gap015_lock.json",
        report_stem="profit_frontier_book_margin_gap015_validation",
    ),
    LockSpec(
        name="book_margin_adverse100",
        title="Book Margin Adverse100",
        lock_path=OUT_DIR / "profit_frontier_book_margin_adverse100_lock.json",
        report_stem="profit_frontier_book_margin_adverse100_validation",
    ),
    LockSpec(
        name="book_margin_delayed_adv100_brownian55",
        title="Book Margin Delayed Adverse100 Brownian55",
        lock_path=OUT_DIR / "profit_book_margin_delayed_adv100_brownian55_lock.json",
        report_stem="profit_book_margin_delayed_adv100_brownian55_validation",
    ),
    LockSpec(
        name="score_min60",
        title="Score Min60",
        lock_path=OUT_DIR / "profit_frontier_score_min60_lock.json",
        report_stem="profit_frontier_score_min60_validation",
    ),
    LockSpec(
        name="score_min60_gap020",
        title="Score Min60 Gap020",
        lock_path=OUT_DIR / "profit_frontier_score_min60_gap020_lock.json",
        report_stem="profit_frontier_score_min60_gap020_validation",
    ),
]


def clean_json_local(value: Any) -> Any:
    if isinstance(value, pd.Timestamp):
        return value.isoformat()
    if isinstance(value, dict):
        return {str(k): clean_json_local(v) for k, v in value.items()}
    if isinstance(value, list):
        return [clean_json_local(v) for v in value]
    return clean_json(value)


def fmt_num(value: Optional[float]) -> str:
    if value is None or not math.isfinite(float(value)):
        return "NA"
    return f"{float(value):.3f}"


def load_lock(spec: LockSpec) -> Dict[str, Any]:
    if not spec.lock_path.exists():
        raise FileNotFoundError(f"Missing lock for {spec.name}: {spec.lock_path}")
    return json.loads(spec.lock_path.read_text(encoding="utf-8"))


def select_for_policy(side_rows: pd.DataFrame, base: pd.DataFrame, policy: Policy) -> pd.DataFrame:
    rows = side_rows.merge(base[["market", "split"]], on="market", how="inner")
    chosen = choose_decision_sides(rows, policy.chooser)
    return enrich_selected(select_markets_from_chosen(chosen, policy))


def simple_condition_mask(rows: pd.DataFrame, condition: Dict[str, Any]) -> pd.Series:
    values = pd.to_numeric(rows.get(condition["feature"]), errors="coerce")
    threshold = float(condition["threshold"])
    if condition["op"] == "<=":
        return values.le(threshold).fillna(False)
    if condition["op"] == ">=":
        return values.ge(threshold).fillna(False)
    raise ValueError(f"unknown condition op: {condition['op']}")


def all_conditions_mask(rows: pd.DataFrame, conditions: List[Dict[str, Any]]) -> pd.Series:
    mask = pd.Series(True, index=rows.index)
    for condition in conditions:
        mask &= simple_condition_mask(rows, condition)
    return mask.fillna(False)


def apply_lock_veto(selected: pd.DataFrame, lock: Dict[str, Any]) -> pd.DataFrame:
    veto = lock.get("veto")
    if not veto or selected.empty:
        return selected
    return selected[simple_condition_mask(selected, veto)].copy()


def select_for_delayed_policy(
    side_rows: pd.DataFrame,
    base: pd.DataFrame,
    policy: Policy,
    conditions: List[Dict[str, Any]],
) -> pd.DataFrame:
    rows = side_rows.merge(base[["market", "split"]], on="market", how="inner")
    chosen = choose_decision_sides(rows, policy.chooser)
    if chosen.empty:
        return chosen
    eligible = chosen[gate_mask(chosen, policy) & all_conditions_mask(chosen, conditions)].copy()
    if eligible.empty:
        return eligible
    selected = (
        eligible.sort_values(["market", "entry_dt"])
        .groupby("market", as_index=False, sort=False)
        .first()
        .sort_values(["entry_dt", "market"])
        .reset_index(drop=True)
    )
    return enrich_selected(selected)


def select_for_lock(side_rows: pd.DataFrame, base: pd.DataFrame, policy: Policy, lock: Dict[str, Any]) -> pd.DataFrame:
    conditions = list(lock.get("delay_conditions") or [])
    if conditions:
        return select_for_delayed_policy(side_rows, base, policy, conditions)
    return apply_lock_veto(select_for_policy(side_rows, base, policy), lock)


def metric_for_scope(base: pd.DataFrame, selected: pd.DataFrame) -> Dict[str, Any]:
    metric = split_metric(base, selected, "all")
    metric["coverage_pass"] = (metric["coverage"] or 0.0) >= MARKET_COVERAGE_FLOOR
    metric["wilson_minus_break_even"] = (
        (metric["wilson95_lower"] or 0.0) - (metric["fee_aware_break_even_accuracy"] or 1.0)
    )
    metric["positive_net"] = (metric["net_pnl_cents"] or 0.0) > 0.0
    return metric


def fresh_scope(
    side_rows: pd.DataFrame,
    base: pd.DataFrame,
    policy: Policy,
    lock: Dict[str, Any],
) -> tuple[pd.DataFrame, pd.DataFrame]:
    boundary = effective_lock_dt(lock)
    if pd.isna(boundary):
        return base.iloc[0:0].copy(), side_rows.iloc[0:0].copy()

    close_dt = pd.to_datetime(base["close_dt"], utc=True, errors="coerce")
    fresh_base = base[close_dt.gt(boundary)].copy()
    if fresh_base.empty:
        return fresh_base, side_rows.iloc[0:0].copy()

    entry_dt = pd.to_datetime(side_rows["entry_dt"], utc=True, errors="coerce")
    fresh_side_rows = side_rows[
        entry_dt.gt(boundary) & side_rows["market"].isin(set(fresh_base["market"]))
    ].copy()
    fresh_selected = select_for_lock(fresh_side_rows, fresh_base, policy, lock)
    return fresh_base, fresh_selected


def write_report(
    path: Path,
    generated: str,
    spec: LockSpec,
    lock: Dict[str, Any],
    all_metric: Dict[str, Any],
    fresh_metric: Dict[str, Any],
    strict_metric: Dict[str, Any],
    divergence: Dict[str, Any],
) -> None:
    policy = lock["policy"]
    effective_dt = effective_lock_dt(lock)
    lines = [
        f"# {spec.title} Locked Policy Validation",
        "",
        f"Generated UTC: `{generated}`",
        "",
        "## Scope",
        "",
        "- Research-only validation; no orders are submitted and no bot files or live processes are touched.",
        "- Reads an existing forward lock and evaluates the current resolved heartbeat ledger.",
        "- Recomputed fresh metrics can drift when Brownian/RV features are refreshed; strict registered rows are the promotion authority.",
        "",
        "## Locked Policy",
        "",
        f"- Name: `{spec.name}`",
        f"- Label: `{policy.get('label') or Policy(**{k: policy[k] for k in ['chooser', 'min_score', 'ask_max', 'min_seconds_to_close', 'gate']}).label}`",
        f"- Lock close time: `{lock.get('lock_close_dt')}`",
        f"- Effective entry boundary: `{effective_dt.isoformat() if not pd.isna(effective_dt) else None}`",
        f"- Lock file: `{spec.lock_path}`",
        "",
        "## Metrics",
        "",
        "| scope | markets | wins/losses | acc | break-even | Wilson low | Wilson edge | coverage | net P&L | net ROI | median ask |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for label, metric in [
        ("all current ledger", all_metric),
        ("recomputed fresh after lock", fresh_metric),
        ("strict registered fresh", strict_metric),
    ]:
        lines.append(metric_row(label, metric))
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
        lines.append("- The lock is waiting for post-boundary resolved markets.")
    elif strict_metric["positive_net"] and strict_metric["coverage_pass"]:
        lines.append("- Strict registered fresh sample is positive and coverage-valid so far, but strict registered sample size is still required.")
    else:
        lines.append("- Strict registered fresh sample is not promotion-quality proof.")
    if divergence["mismatches"] or divergence["missing_recompute"]:
        lines.append("- Recomputed fresh rows diverge from pre-registered rows; strict registered rows are the promotion authority.")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def validate_spec(generated: str, spec: LockSpec, side_rows: pd.DataFrame, base: pd.DataFrame) -> Dict[str, Any]:
    lock = load_lock(spec)
    policy = policy_from_record(lock["policy"])
    selected = select_for_lock(side_rows, base, policy, lock)
    all_metric = metric_for_scope(base, selected)
    fresh_base, fresh_selected = fresh_scope(side_rows, base, policy, lock)
    fresh_metric = metric_for_scope(fresh_base, fresh_selected)
    boundary = effective_lock_dt(lock)
    strict_rows = strict_registry_rows(spec.name, fresh_base, boundary)
    strict_metric = metric_for_strict_registry(fresh_base, strict_rows)
    divergence = registry_recompute_divergence(fresh_selected, strict_rows)

    md_latest = OUT_DIR / f"{spec.report_stem}_latest.md"
    md_stamp = OUT_DIR / f"{spec.report_stem}_{generated}.md"
    json_latest = OUT_DIR / f"{spec.report_stem}_latest.json"
    json_stamp = OUT_DIR / f"{spec.report_stem}_{generated}.json"
    write_report(md_latest, generated, spec, lock, all_metric, fresh_metric, strict_metric, divergence)
    write_report(md_stamp, generated, spec, lock, all_metric, fresh_metric, strict_metric, divergence)

    payload = {
        "generated_utc": generated,
        "name": spec.name,
        "lock": lock,
        "all_metric": all_metric,
        "fresh_metric": fresh_metric,
        "strict_registered_metric": strict_metric,
        "registry_recompute_divergence": divergence,
    }
    for path in [json_latest, json_stamp]:
        path.write_text(json.dumps(clean_json_local(payload), indent=2, sort_keys=True), encoding="utf-8")
    return payload


def selected_specs(names: Iterable[str]) -> List[LockSpec]:
    requested = {name for name in names}
    if not requested:
        return list(LOCK_SPECS)
    known = {spec.name for spec in LOCK_SPECS}
    unknown = sorted(requested - known)
    if unknown:
        raise SystemExit(f"Unknown lock name(s): {', '.join(unknown)}")
    return [spec for spec in LOCK_SPECS if spec.name in requested]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--name",
        action="append",
        default=[],
        help="Optional lock name to validate. May be supplied more than once; default validates all tracked locks.",
    )
    args = parser.parse_args()

    generated = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%SZ")
    side_rows = load_side_rows()
    base = market_base(side_rows)
    specs = selected_specs(args.name)
    payloads = [validate_spec(generated, spec, side_rows, base) for spec in specs]
    for payload in payloads:
        fresh = payload.get("strict_registered_metric") or payload["fresh_metric"]
        source = "strict" if payload.get("strict_registered_metric") else "recomputed"
        print(
            "{name}: {source}_fresh_markets={markets} fresh_base={base_markets} fresh_net={net}c".format(
                name=payload["name"],
                source=source,
                markets=int(fresh["markets"]),
                base_markets=int(fresh["base_markets"]),
                net=float(fresh["net_pnl_cents"] or 0.0),
            )
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
