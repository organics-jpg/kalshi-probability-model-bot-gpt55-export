"""Readiness monitor based on pre-registered locked-profit signals.

The fresh validators recompute selected rows from the latest log snapshot. That
is useful for diagnostics, but live promotion evidence should prefer signals
that were registered before the outcome was known. This monitor reads the
pre-resolution registries and computes resolved EV state from those immutable
first signals.

Research-only: no orders are submitted and no bot files or live processes are
modified.
"""
from __future__ import annotations

import json
import math
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional

import pandas as pd

from probe_cross_dataset_profit_frontier import fmt_cents, fmt_roi
from probe_interval_policy_degeneracy_audit import wilson_lower
from probe_profit_lock_bayesian_ev_monitor import (
    MIN_FRESH_MARKETS_GATE,
    POSTERIOR_PROB_GATE,
    extra_perfect_wins_for_posterior,
    posterior_stats,
)
from probe_market_interval_80coverage import MARKET_COVERAGE_FLOOR, OUT_DIR, clean_json, pct


MAIN_REGISTRY = OUT_DIR / "profit_lock_pending_signal_registry_latest.csv"
PATH_REGISTRY = OUT_DIR / "kinetic_path_confirmation_pending_registry_latest.csv"
DENOMINATOR_AUDIT = OUT_DIR / "profit_lock_market_denominator_audit_latest.json"

VALIDATION_FILES = [
    ("original", OUT_DIR / "profit_frontier_fresh_validation_latest.json"),
    ("frontier_v2", OUT_DIR / "profit_frontier_v2_fresh_validation_latest.json"),
    ("frontier_v2_continuous", OUT_DIR / "profit_frontier_v2_continuous_validation_latest.json"),
    ("book_margin", OUT_DIR / "profit_frontier_book_margin_validation_latest.json"),
    ("book_margin_early", OUT_DIR / "profit_frontier_book_margin_early_validation_latest.json"),
    ("book_margin_gap015", OUT_DIR / "profit_frontier_book_margin_gap015_validation_latest.json"),
    ("book_margin_adverse100", OUT_DIR / "profit_frontier_book_margin_adverse100_validation_latest.json"),
    ("book_margin_delayed_adv100_brownian55", OUT_DIR / "profit_book_margin_delayed_adv100_brownian55_validation_latest.json"),
    ("book_hour04_v2_switch", OUT_DIR / "profit_book_hour04_v2_switch_validation_latest.json"),
    ("book_refmargin_score_switch", OUT_DIR / "profit_book_refmargin_score_switch_validation_latest.json"),
    ("score_min60", OUT_DIR / "profit_frontier_score_min60_validation_latest.json"),
    ("score_min60_gap020", OUT_DIR / "profit_frontier_score_min60_gap020_validation_latest.json"),
    ("book_early_score_gap020_wait", OUT_DIR / "profit_book_early_score_gap020_wait_validation_latest.json"),
    ("book_score_gap020_wait", OUT_DIR / "profit_book_score_gap020_wait_validation_latest.json"),
    ("v2_wait_score_min60_early", OUT_DIR / "profit_v2_wait_score_min60_early_validation_latest.json"),
    ("v2_wait_score_min60_brownian70_early", OUT_DIR / "profit_v2_wait_score_min60_brownian70_early_validation_latest.json"),
    ("challenger", OUT_DIR / "profit_challenger_fresh_validation_latest.json"),
    ("touch_hazard", OUT_DIR / "profit_touch_hazard_fresh_validation_latest.json"),
    ("touch_overlay", OUT_DIR / "profit_touch_hazard_overlay_fresh_validation_latest.json"),
    ("kinetic_touch", OUT_DIR / "profit_kinetic_touch_fresh_validation_latest.json"),
    ("hazard_mean_touch80", OUT_DIR / "profit_hazard_mean_touch80_fresh_validation_latest.json"),
    ("logit_blend_edge10", OUT_DIR / "profit_logit_blend_edge10_fresh_validation_latest.json"),
    ("logit_blend_thresh55_edge15", OUT_DIR / "profit_logit_blend_thresh55_edge15_fresh_validation_latest.json"),
    ("hazard_fallback_logit55", OUT_DIR / "profit_hazard_fallback_logit55_fresh_validation_latest.json"),
    ("hazard_fallback_logit55_wait8", OUT_DIR / "profit_hazard_fallback_logit55_wait8_fresh_validation_latest.json"),
    ("hazard_fallback_score60", OUT_DIR / "profit_hazard_fallback_score60_fresh_validation_latest.json"),
    ("impulse_reversal_book_margin_fade", OUT_DIR / "profit_impulse_reversal_book_margin_fade_fresh_validation_latest.json"),
    ("kinetic_guard", OUT_DIR / "profit_kinetic_guard_fresh_validation_latest.json"),
    ("kinetic_price_guard", OUT_DIR / "profit_kinetic_price_guard_fresh_validation_latest.json"),
    ("kinetic_combo_price_guard", OUT_DIR / "profit_kinetic_combo_price_guard_fresh_validation_latest.json"),
    ("kinetic_path_confirm", OUT_DIR / "profit_kinetic_path_confirm_fresh_validation_latest.json"),
]


def clean_json_local(value: Any) -> Any:
    if isinstance(value, pd.Timestamp):
        return value.isoformat()
    if isinstance(value, dict):
        return {str(k): clean_json_local(v) for k, v in value.items()}
    if isinstance(value, list):
        return [clean_json_local(v) for v in value]
    return clean_json(value)


def bool_value(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    return str(value).lower() in {"true", "1", "yes"}


def fmt_num(value: Optional[float], digits: int = 3) -> str:
    if value is None or not math.isfinite(float(value)):
        return "NA"
    return f"{float(value):.{digits}f}"


def load_registry(path: Path) -> pd.DataFrame:
    if not path.exists():
        return pd.DataFrame()
    rows = pd.read_csv(path)
    if rows.empty:
        return rows
    rows["lock_name"] = rows["lock_name"].astype(str)
    registered_dt = pd.to_datetime(rows.get("registered_utc"), utc=True, errors="coerce")
    close_dt = pd.to_datetime(rows.get("close_dt"), utc=True, errors="coerce")
    rows = rows[registered_dt.notna() & close_dt.notna() & registered_dt.lt(close_dt)].copy()
    if rows.empty:
        return rows
    rows["outcome_available_bool"] = rows["outcome_available"].map(bool_value)
    rows["win_bool"] = rows["win"].map(bool_value)
    for col in ["ask_cents", "entry_fee_cents", "net_pnl_cents"]:
        rows[col] = pd.to_numeric(rows.get(col), errors="coerce")
    return rows


def validation_context(name: str, path: Path) -> Dict[str, Any]:
    if not path.exists():
        return {"fresh_base_markets": 0, "fallback_break_even": None, "overlay": ""}
    payload = json.loads(path.read_text(encoding="utf-8"))
    fresh = payload.get("fresh_metric", {})
    all_metric = payload.get("all_metric", {})
    lock = payload.get("lock", {})
    overlay = (
        lock.get("overlay", {}).get("label", "")
        or lock.get("confirmation", {}).get("label", "")
    )
    return {
        "fresh_base_markets": int(fresh.get("base_markets") or 0),
        "fallback_break_even": all_metric.get("fee_aware_break_even_accuracy"),
        "overlay": overlay,
    }


def denominator_context() -> Dict[str, Dict[str, Any]]:
    if not DENOMINATOR_AUDIT.exists():
        return {}
    try:
        payload = json.loads(DENOMINATOR_AUDIT.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
    rows = payload.get("rows", [])
    if not isinstance(rows, list):
        return {}
    return {str(row.get("name")): row for row in rows if isinstance(row, dict)}


def summarize_lock(name: str, path: Path, registry: pd.DataFrame, denominators: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
    ctx = validation_context(name, path)
    denom = denominators.get(name, {})
    rows = registry[registry["lock_name"].eq(name)].copy() if not registry.empty else pd.DataFrame()
    resolved = rows[rows["outcome_available_bool"]] if not rows.empty else rows
    pending = rows[~rows["outcome_available_bool"]] if not rows.empty else rows
    n = int(len(resolved))
    wins = int(resolved["win_bool"].sum()) if n else 0
    losses = n - wins
    net = float(resolved["net_pnl_cents"].sum()) if n else 0.0
    entry_cost = float((resolved["ask_cents"] + resolved["entry_fee_cents"].fillna(0.0)).sum()) if n else None
    avg_entry_cost = (entry_cost / n) if n and entry_cost is not None else None
    break_even = (entry_cost / n / 100.0) if n and entry_cost is not None else ctx["fallback_break_even"]
    accuracy = (wins / n) if n else None
    wilson = wilson_lower(wins, n) if n else None
    posterior = posterior_stats(wins, losses, break_even, avg_entry_cost)
    registered = int(len(rows))
    fresh_base = int(ctx["fresh_base_markets"])
    observed_markets = int(denom.get("observed_post_lock_markets") or 0)
    resolved_markets = int(denom.get("resolved_post_lock_markets") or 0)
    if observed_markets or resolved_markets:
        coverage_denominator = max(observed_markets, registered)
        resolved_coverage_denominator = max(resolved_markets, n)
        coverage_source = "market_denominator_audit"
    else:
        coverage_denominator = max(fresh_base, registered)
        resolved_coverage_denominator = coverage_denominator
        coverage_source = "fresh_validator_fallback"
    registered_coverage = (registered / coverage_denominator) if coverage_denominator else None
    resolved_coverage = (n / resolved_coverage_denominator) if resolved_coverage_denominator else None
    row = {
        "name": name,
        "path": str(path),
        "overlay": ctx["overlay"],
        "registered": registered,
        "resolved": n,
        "pending": int(len(pending)),
        "fresh_base_markets": fresh_base,
        "coverage_denominator": coverage_denominator,
        "resolved_coverage_denominator": resolved_coverage_denominator,
        "coverage_source": coverage_source,
        "observed_post_lock_markets": observed_markets,
        "resolved_post_lock_markets": resolved_markets,
        "wins": wins,
        "losses": losses,
        "accuracy": accuracy,
        "break_even": break_even,
        "wilson95_lower": wilson,
        "wilson_minus_break_even": (wilson - break_even) if wilson is not None and break_even is not None else None,
        "registered_coverage": registered_coverage,
        "resolved_coverage": resolved_coverage,
        "net_pnl_cents": net,
        "net_roi_on_cost": (net / entry_cost) if entry_cost else None,
        **posterior,
    }
    row["posterior_extra_perfect_wins_to_gate"] = extra_perfect_wins_for_posterior(
        wins,
        losses,
        break_even,
        avg_entry_cost,
    )
    row["registered_ready"] = (
        n >= 75
        and (row["resolved_coverage"] or 0.0) >= MARKET_COVERAGE_FLOOR
        and net > 0.0
        and row["wilson_minus_break_even"] is not None
        and row["wilson_minus_break_even"] >= 0.0
    )
    row["registered_bayesian_ready"] = (
        n >= MIN_FRESH_MARKETS_GATE
        and (row["resolved_coverage"] or 0.0) >= MARKET_COVERAGE_FLOOR
        and net > 0.0
        and (row["prob_win_rate_gt_break_even"] or 0.0) >= POSTERIOR_PROB_GATE
        and (row["posterior_p05_edge_cents"] or -1.0) > 0.0
    )
    return row


def write_report(path: Path, generated: str, rows: list[Dict[str, Any]]) -> None:
    lines = [
        "# Profit Lock Registered-Signal Readiness",
        "",
        f"Generated UTC: `{generated}`",
        "",
        "## Scope",
        "",
        "- Research-only monitor; no orders are submitted and no bot files or live processes are touched.",
        "- Uses pre-registered first signals captured before outcomes were known.",
        "- This is stricter promotion evidence than recomputing first eligible rows from a later log snapshot.",
        "",
        "## Registered Signal State",
        "",
        "| lock | overlay | registered/resolved/pending | wins/losses | acc | break-even | Wilson low | P(p>BE) | p05 edge | resolved coverage | registered coverage | net P&L | ROI | Bayes extra wins | Wilson ready | Bayes ready |",
        "|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|---|",
    ]
    for row in rows:
        lines.append(
            f"| {row['name']} | `{row['overlay'] or 'none'}` | "
            f"{row['registered']}/{row['resolved']}/{row['pending']} | {row['wins']}/{row['losses']} | "
            f"{pct(row['accuracy'])} | {pct(row['break_even'])} | {pct(row['wilson95_lower'])} | "
            f"{fmt_num(row['prob_win_rate_gt_break_even'])} | {fmt_cents(row['posterior_p05_edge_cents'])} | "
            f"{pct(row['resolved_coverage'])} | {pct(row['registered_coverage'])} | "
            f"{fmt_cents(row['net_pnl_cents'])} | {fmt_roi(row['net_roi_on_cost'])} | "
            f"{row['posterior_extra_perfect_wins_to_gate'] if row['posterior_extra_perfect_wins_to_gate'] is not None else 'NA'} | "
            f"{row['registered_ready']} | {row['registered_bayesian_ready']} |"
        )
    lines += ["", "## Read", ""]
    if any(row["registered_ready"] for row in rows):
        lines.append("- At least one lock clears the registered-signal Wilson gate.")
    else:
        lines.append("- No lock clears the registered-signal Wilson gate yet.")
    if any(row["registered_bayesian_ready"] for row in rows):
        lines.append("- At least one lock clears the registered-signal Bayesian gate.")
    else:
        lines.append("- No lock clears the registered-signal Bayesian gate yet.")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    generated = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%SZ")
    main_registry = load_registry(MAIN_REGISTRY)
    path_registry = load_registry(PATH_REGISTRY)
    registry = pd.concat(
        [frame for frame in [main_registry, path_registry] if not frame.empty],
        ignore_index=True,
    ) if not main_registry.empty or not path_registry.empty else pd.DataFrame()
    denominators = denominator_context()
    validation_by_name = {name: path for name, path in VALIDATION_FILES}
    ordered_names = [name for name, _ in VALIDATION_FILES]
    if not registry.empty and "lock_name" in registry.columns:
        for name in sorted(str(value) for value in registry["lock_name"].dropna().unique()):
            if name not in validation_by_name:
                validation_by_name[name] = OUT_DIR / f"{name}_validation_latest.json"
                ordered_names.append(name)
    rows = [summarize_lock(name, validation_by_name[name], registry, denominators) for name in ordered_names]
    md_latest = OUT_DIR / "profit_lock_registered_signal_readiness_latest.md"
    md_stamp = OUT_DIR / f"profit_lock_registered_signal_readiness_{generated}.md"
    json_latest = OUT_DIR / "profit_lock_registered_signal_readiness_latest.json"
    json_stamp = OUT_DIR / f"profit_lock_registered_signal_readiness_{generated}.json"
    csv_latest = OUT_DIR / "profit_lock_registered_signal_readiness_latest.csv"
    csv_stamp = OUT_DIR / f"profit_lock_registered_signal_readiness_{generated}.csv"
    write_report(md_latest, generated, rows)
    write_report(md_stamp, generated, rows)
    pd.DataFrame(rows).to_csv(csv_latest, index=False)
    pd.DataFrame(rows).to_csv(csv_stamp, index=False)
    payload = {
        "generated_utc": generated,
        "rows": rows,
        "ready_count": int(sum(bool(row["registered_ready"]) for row in rows)),
        "bayesian_ready_count": int(sum(bool(row["registered_bayesian_ready"]) for row in rows)),
    }
    for out_path in [json_latest, json_stamp]:
        out_path.write_text(json.dumps(clean_json_local(payload), indent=2, sort_keys=True), encoding="utf-8")
    print("Profit lock registered-signal readiness complete")
    print(f"ready_count={payload['ready_count']}")
    print(f"report={md_latest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
