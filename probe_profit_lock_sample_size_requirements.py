"""Sample-size gates for locked BTC 15m profit candidates.

The locked EV candidates are profitable on tiny fresh samples, but the goal
requires live verification with sample size. This monitor converts the fresh
state into explicit gates:

- current fresh coverage,
- whether fresh net P&L is positive,
- whether the Wilson lower bound for fresh accuracy clears the average
  fee-aware break-even probability,
- extra perfect fresh wins needed to clear that Wilson/break-even gate,
- approximate selected sample size needed if the all-ledger observed edge
  persisted.

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
from probe_market_interval_80coverage import MARKET_COVERAGE_FLOOR, OUT_DIR, clean_json, pct


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
REGISTERED_READINESS_JSON = OUT_DIR / "profit_lock_registered_signal_readiness_latest.json"


def clean_json_local(value: Any) -> Any:
    if isinstance(value, pd.Timestamp):
        return value.isoformat()
    if isinstance(value, dict):
        return {str(k): clean_json_local(v) for k, v in value.items()}
    if isinstance(value, list):
        return [clean_json_local(v) for v in value]
    return clean_json(value)


def fmt_num(value: Optional[float], digits: int = 3) -> str:
    if value is None or not math.isfinite(float(value)):
        return "NA"
    return f"{float(value):.{digits}f}"


def extra_perfect_wins_needed(wins: int, n: int, break_even: Optional[float], max_extra: int = 10_000) -> Optional[int]:
    if break_even is None or not math.isfinite(float(break_even)):
        return None
    for extra in range(max_extra + 1):
        new_n = n + extra
        if new_n <= 0:
            continue
        new_wins = wins + extra
        lower = wilson_lower(new_wins, new_n)
        if lower is not None and lower >= break_even:
            return extra
    return None


def min_n_at_accuracy(accuracy: Optional[float], break_even: Optional[float], max_n: int = 20_000) -> Optional[int]:
    if accuracy is None or break_even is None:
        return None
    if not math.isfinite(float(accuracy)) or not math.isfinite(float(break_even)):
        return None
    if accuracy <= break_even:
        return None
    for n in range(1, max_n + 1):
        wins = int(math.ceil(float(accuracy) * n))
        lower = wilson_lower(wins, n)
        if lower is not None and lower >= break_even:
            return n
    return None


def readiness_context() -> Dict[str, Dict[str, Any]]:
    if not REGISTERED_READINESS_JSON.exists():
        return {}
    try:
        payload = json.loads(REGISTERED_READINESS_JSON.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
    rows = payload.get("rows", [])
    if not isinstance(rows, list):
        return {}
    return {str(row.get("name")): row for row in rows if isinstance(row, dict)}


def summarize(name: str, path: Path, readiness_rows: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
    ready = readiness_rows.get(name)
    if path.exists():
        payload = json.loads(path.read_text(encoding="utf-8"))
        all_metric = payload["all_metric"]
        lock = payload["lock"]
    elif ready:
        payload = {}
        all_metric = {
            "accuracy": ready.get("accuracy"),
            "fee_aware_break_even_accuracy": ready.get("break_even"),
            "wilson95_lower": ready.get("wilson95_lower"),
            "net_pnl_cents": ready.get("net_pnl_cents"),
            "net_roi_on_cost": ready.get("net_roi_on_cost"),
            "coverage": ready.get("resolved_coverage"),
        }
        lock = {"policy": {"label": ""}, "overlay": {"label": ready.get("overlay", "")}, "lock_close_dt": None}
    else:
        raise SystemExit(f"Missing validation JSON for {name}: {path}")
    if ready:
        fresh = {
            "base_markets": ready.get("resolved_coverage_denominator"),
            "markets": ready.get("resolved"),
            "wins": ready.get("wins"),
            "losses": ready.get("losses"),
            "accuracy": ready.get("accuracy"),
            "fee_aware_break_even_accuracy": ready.get("break_even"),
            "wilson95_lower": ready.get("wilson95_lower"),
            "wilson_minus_break_even": ready.get("wilson_minus_break_even"),
            "coverage": ready.get("resolved_coverage"),
            "net_pnl_cents": ready.get("net_pnl_cents"),
            "net_roi_on_cost": ready.get("net_roi_on_cost"),
            "median_ask": None,
        }
        fresh_source = "registered_signal_readiness"
    else:
        fresh = payload.get("strict_registered_metric") or payload["fresh_metric"]
        fresh_source = "strict_registered_metric" if payload.get("strict_registered_metric") else "fresh_metric"
    wins = int(fresh.get("wins") or 0)
    n = int(fresh.get("markets") or 0)
    break_even = fresh.get("fee_aware_break_even_accuracy")
    if break_even is None and n <= 0:
        break_even = all_metric.get("fee_aware_break_even_accuracy")
    coverage = fresh.get("coverage")
    overlay_label = (
        lock.get("overlay", {}).get("label", "")
        or lock.get("confirmation", {}).get("label", "")
    )
    row = {
        "name": name,
        "path": str(path),
        "fresh_metric_source": fresh_source,
        "label": lock.get("policy", {}).get("label", ""),
        "overlay": overlay_label,
        "lock_close_dt": lock.get("lock_close_dt"),
        "fresh_base_markets": int(fresh.get("base_markets") or 0),
        "fresh_markets": n,
        "fresh_wins": wins,
        "fresh_losses": int(fresh.get("losses") or 0),
        "fresh_accuracy": fresh.get("accuracy"),
        "fresh_break_even": fresh.get("fee_aware_break_even_accuracy"),
        "fallback_break_even_for_empty_fresh": all_metric.get("fee_aware_break_even_accuracy"),
        "fresh_wilson_lower": fresh.get("wilson95_lower"),
        "fresh_wilson_minus_break_even": fresh.get("wilson_minus_break_even"),
        "fresh_coverage": coverage,
        "fresh_coverage_pass": (coverage or 0.0) >= MARKET_COVERAGE_FLOOR if coverage is not None else False,
        "fresh_positive_net": (fresh.get("net_pnl_cents") or 0.0) > 0.0,
        "fresh_net_pnl_cents": fresh.get("net_pnl_cents"),
        "fresh_net_roi": fresh.get("net_roi_on_cost"),
        "fresh_median_ask": fresh.get("median_ask"),
        "all_accuracy": all_metric.get("accuracy"),
        "all_break_even": all_metric.get("fee_aware_break_even_accuracy"),
        "all_wilson_lower": all_metric.get("wilson95_lower"),
        "all_net_pnl_cents": all_metric.get("net_pnl_cents"),
        "all_net_roi": all_metric.get("net_roi_on_cost"),
        "all_coverage": all_metric.get("coverage"),
    }
    row["fresh_ev_wilson_pass"] = (
        row["fresh_wilson_lower"] is not None
        and row["fresh_break_even"] is not None
        and row["fresh_wilson_lower"] >= row["fresh_break_even"]
    )
    row["extra_perfect_wins_for_fresh_ev_wilson"] = extra_perfect_wins_needed(wins, n, break_even)
    row["selected_n_needed_at_all_accuracy"] = min_n_at_accuracy(row["all_accuracy"], row["all_break_even"])
    row["additional_selected_n_needed_at_all_accuracy"] = (
        max(0, int(row["selected_n_needed_at_all_accuracy"]) - n)
        if row["selected_n_needed_at_all_accuracy"] is not None
        else None
    )
    row["completion_ready"] = (
        row["fresh_coverage_pass"]
        and row["fresh_positive_net"]
        and row["fresh_ev_wilson_pass"]
        and n >= 75
    )
    return row


def write_report(path: Path, generated: str, rows: list[Dict[str, Any]]) -> None:
    lines = [
        "# Profit Lock Sample-Size Requirements",
        "",
        f"Generated UTC: `{generated}`",
        "",
        "## Scope",
        "",
        "- Research-only monitor; no orders are submitted and no bot files or live processes are touched.",
        "- Fresh EV proof requires positive net P&L, >=80% recurring-market coverage, and a Wilson lower bound above average fee-aware break-even.",
        "- Includes separate combo price-guard and path-confirmation locks as fresh forward evidence; neither is a promotion into live trading.",
        "- Uses registered-signal readiness rows when available; otherwise falls back to strict validator metrics, then recomputed fresh metrics.",
        "- `extra perfect wins` assumes all future selected fresh markets win at approximately the current/fallback break-even level.",
        "- `n at all accuracy` estimates selected fresh sample size needed if the all-ledger observed accuracy and break-even persist.",
        "",
        "## Locks",
        "",
        "| lock | source | overlay | fresh markets | wins/losses | acc | break-even | Wilson low | coverage | net P&L | ROI | extra perfect wins | n at all accuracy | ready |",
        "|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|",
    ]
    for row in rows:
        lines.append(
            f"| {row['name']} | `{row['fresh_metric_source']}` | `{row['overlay'] or 'none'}` | "
            f"{row['fresh_markets']}/{row['fresh_base_markets']} | {row['fresh_wins']}/{row['fresh_losses']} | "
            f"{pct(row['fresh_accuracy'])} | {pct(row['fresh_break_even'])} | {pct(row['fresh_wilson_lower'])} | "
            f"{pct(row['fresh_coverage'])} | {fmt_cents(row['fresh_net_pnl_cents'])} | {fmt_roi(row['fresh_net_roi'])} | "
            f"{row['extra_perfect_wins_for_fresh_ev_wilson'] if row['extra_perfect_wins_for_fresh_ev_wilson'] is not None else 'NA'} | "
            f"{row['selected_n_needed_at_all_accuracy'] if row['selected_n_needed_at_all_accuracy'] is not None else 'NA'} | "
            f"{row['completion_ready']} |"
        )
    lines += ["", "## Read", ""]
    ready = [row for row in rows if row["completion_ready"]]
    if ready:
        lines.append("- At least one lock meets the current EV sample-size gate.")
    else:
        lines.append("- No lock meets the fresh EV sample-size gate yet.")
    for row in rows:
        extra = row["extra_perfect_wins_for_fresh_ev_wilson"]
        lines.append(
            f"- {row['name']}: needs {extra if extra is not None else 'NA'} additional perfect selected fresh wins "
            f"to clear Wilson over break-even from the current fresh state."
        )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    generated = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%SZ")
    readiness_rows = readiness_context()
    validation_by_name = {name: path for name, path in VALIDATION_FILES}
    ordered_names = [name for name, _ in VALIDATION_FILES]
    for name in sorted(readiness_rows):
        if name not in validation_by_name:
            validation_by_name[name] = OUT_DIR / f"{name}_validation_latest.json"
            ordered_names.append(name)
    rows = [summarize(name, validation_by_name[name], readiness_rows) for name in ordered_names]
    md_latest = OUT_DIR / "profit_lock_sample_size_requirements_latest.md"
    md_stamp = OUT_DIR / f"profit_lock_sample_size_requirements_{generated}.md"
    json_latest = OUT_DIR / "profit_lock_sample_size_requirements_latest.json"
    json_stamp = OUT_DIR / f"profit_lock_sample_size_requirements_{generated}.json"
    csv_latest = OUT_DIR / "profit_lock_sample_size_requirements_latest.csv"
    csv_stamp = OUT_DIR / f"profit_lock_sample_size_requirements_{generated}.csv"
    write_report(md_latest, generated, rows)
    write_report(md_stamp, generated, rows)
    pd.DataFrame(rows).to_csv(csv_latest, index=False)
    pd.DataFrame(rows).to_csv(csv_stamp, index=False)
    payload = {
        "generated_utc": generated,
        "rows": rows,
        "ready_count": int(sum(bool(row["completion_ready"]) for row in rows)),
    }
    for path in [json_latest, json_stamp]:
        path.write_text(json.dumps(clean_json_local(payload), indent=2, sort_keys=True), encoding="utf-8")
    print("Profit lock sample-size requirements complete")
    print(f"ready_count={payload['ready_count']}")
    print(f"report={md_latest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
