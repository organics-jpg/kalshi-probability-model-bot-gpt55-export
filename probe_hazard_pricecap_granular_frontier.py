"""Granular ask-cap frontier for the hazard BTC 15m model.

The live hazard branch is directionally promising but vulnerable to expensive
late certainty. This probe scans the narrow 73c-80c price-cap band to find
whether a physics-motivated overreaction cap can improve EV while preserving
the recurring-market coverage floor.

Historical rows are diagnostic only; the live registry-cap rows are also
diagnostic because the cap is being selected after some outcomes are known.
Any passing cap must be forward-locked before use.
"""
from __future__ import annotations

import json
import math
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

import pandas as pd

from probe_cross_dataset_interval_frontier import load_v21_side_rows
from probe_cross_dataset_profit_frontier import fmt_cents, fmt_roi
from probe_hazard_overreaction_frontier import OverreactionSpec, flatten, metrics_for, selected_rows
from probe_interval_policy_degeneracy_audit import wilson_lower
from probe_market_interval_80coverage import (
    MARKET_COVERAGE_FLOOR,
    OUT_DIR,
    clean_json,
    load_side_rows,
    market_base,
    pct,
)
from probe_profit_lock_bayesian_ev_monitor import posterior_stats
from probe_profit_touch_hazard_frontier import add_touch_hazard_scores


MAIN_REGISTRY = OUT_DIR / "profit_lock_pending_signal_registry_latest.csv"
DENOMINATOR_AUDIT = OUT_DIR / "profit_lock_market_denominator_audit_latest.json"
REPORT_LATEST = OUT_DIR / "hazard_pricecap_granular_frontier_latest.md"
JSON_LATEST = OUT_DIR / "hazard_pricecap_granular_frontier_latest.json"
CSV_LATEST = OUT_DIR / "hazard_pricecap_granular_frontier_latest.csv"


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
    return str(value).strip().lower() in {"true", "1", "yes"}


def fmt_num(value: Optional[float], digits: int = 3) -> str:
    if value is None or not math.isfinite(float(value)):
        return "NA"
    return f"{float(value):.{digits}f}"


def make_specs() -> List[OverreactionSpec]:
    specs: List[OverreactionSpec] = []
    for ask_max in [73.0, 74.0, 75.0, 76.0, 77.0, 78.0, 79.0, 80.0]:
        specs.append(OverreactionSpec(f"ask{ask_max:g}", ask_max))
        specs.append(OverreactionSpec(f"ask{ask_max:g}_score65", ask_max, max_score=0.65))
        specs.append(OverreactionSpec(f"ask{ask_max:g}_margin75", ask_max, max_margin_sigma=0.75))
        specs.append(
            OverreactionSpec(
                f"ask{ask_max:g}_score65_margin75",
                ask_max,
                max_score=0.65,
                max_margin_sigma=0.75,
            )
        )
    return specs


def load_denominator(name: str) -> Dict[str, Any]:
    if not DENOMINATOR_AUDIT.exists():
        return {}
    try:
        payload = json.loads(DENOMINATOR_AUDIT.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
    for row in payload.get("rows", []):
        if isinstance(row, dict) and row.get("name") == name:
            return row
    return {}


def load_hazard_registry() -> pd.DataFrame:
    if not MAIN_REGISTRY.exists():
        return pd.DataFrame()
    rows = pd.read_csv(MAIN_REGISTRY)
    if rows.empty:
        return rows
    rows = rows[rows["lock_name"].astype(str).eq("hazard_mean_touch80")].copy()
    if rows.empty:
        return rows
    rows["outcome_available_bool"] = rows["outcome_available"].map(bool_value)
    rows["win_bool"] = rows["win"].map(bool_value)
    for col in ["ask_cents", "entry_fee_cents", "net_pnl_cents", "score_value", "seconds_to_close"]:
        rows[col] = pd.to_numeric(rows.get(col), errors="coerce")
    rows["entry_dt"] = pd.to_datetime(rows.get("entry_dt"), utc=True, errors="coerce")
    rows["close_dt"] = pd.to_datetime(rows.get("close_dt"), utc=True, errors="coerce")
    return rows.dropna(subset=["entry_dt", "close_dt", "ask_cents"]).copy()


def live_cap_metric(registry: pd.DataFrame, ask_max: float, denom: Dict[str, Any]) -> Dict[str, Any]:
    selected = registry[pd.to_numeric(registry["ask_cents"], errors="coerce").le(float(ask_max))].copy()
    resolved = selected[selected["outcome_available_bool"]].copy()
    n = int(len(resolved))
    wins = int(resolved["win_bool"].sum()) if n else 0
    losses = n - wins
    net = float(resolved["net_pnl_cents"].sum()) if n else 0.0
    costs = (
        pd.to_numeric(resolved["ask_cents"], errors="coerce")
        + pd.to_numeric(resolved["entry_fee_cents"], errors="coerce").fillna(0.0)
    )
    entry_cost = float(costs.sum()) if n else None
    avg_entry_cost = entry_cost / n if entry_cost else None
    break_even = avg_entry_cost / 100.0 if avg_entry_cost is not None else None
    observed = int(denom.get("observed_post_lock_markets") or len(registry))
    resolved_base = int(denom.get("resolved_post_lock_markets") or int(registry["outcome_available_bool"].sum()))
    posterior = posterior_stats(wins, losses, break_even, avg_entry_cost)
    return {
        "live_registered": int(len(selected)),
        "live_resolved": n,
        "live_pending": int(len(selected) - n),
        "live_wins": wins,
        "live_losses": losses,
        "live_accuracy": wins / n if n else None,
        "live_break_even": break_even,
        "live_wilson95_lower": wilson_lower(wins, n) if n else None,
        "live_registered_coverage": len(selected) / observed if observed else None,
        "live_resolved_coverage": n / resolved_base if resolved_base else None,
        "live_net_pnl_cents": net,
        "live_net_roi_on_cost": net / entry_cost if entry_cost else None,
        "live_median_ask": float(resolved["ask_cents"].median()) if n else None,
        "live_prob_win_rate_gt_break_even": posterior["prob_win_rate_gt_break_even"],
        "live_p05_edge_cents": posterior["posterior_p05_edge_cents"],
    }


def scan() -> tuple[pd.DataFrame, Dict[str, Any]]:
    current_side = add_touch_hazard_scores(load_side_rows())
    v21_side = add_touch_hazard_scores(load_v21_side_rows())
    current_base = market_base(current_side)
    v21_base = market_base(v21_side)
    registry = load_hazard_registry()
    denom = load_denominator("hazard_mean_touch80")

    rows: List[Dict[str, Any]] = []
    for spec in make_specs():
        current_selected = selected_rows(current_base, current_side, spec)
        v21_selected = selected_rows(v21_base, v21_side, spec)
        row = flatten(spec, metrics_for(current_base, current_selected), metrics_for(v21_base, v21_selected))
        row.update(live_cap_metric(registry, spec.ask_max, denom))
        row["live_resolved_coverage_pass"] = (row["live_resolved_coverage"] or 0.0) >= MARKET_COVERAGE_FLOOR
        row["live_registered_coverage_pass"] = (row["live_registered_coverage"] or 0.0) >= MARKET_COVERAGE_FLOOR
        row["strict_all"] = (
            bool(row["both_all_positive"])
            and bool(row["both_oos_positive"])
            and bool(row["strict_80_oos_coverage_pass"])
            and bool(row["live_resolved_coverage_pass"])
        )
        rows.append(row)

    frame = pd.DataFrame(rows).sort_values(
        ["strict_all", "both_oos_positive", "strict_80_oos_coverage_pass", "combined_all_net_pnl_cents"],
        ascending=[False, False, False, False],
    )
    diagnostics = {
        "current_markets": int(len(current_base)),
        "v21_markets": int(len(v21_base)),
        "live_hazard_registered_rows": int(len(registry)),
        "live_hazard_resolved_rows": int(registry["outcome_available_bool"].sum()) if not registry.empty else 0,
        "rows": int(len(frame)),
    }
    return frame.reset_index(drop=True), diagnostics


def table_row(row: Dict[str, Any]) -> str:
    return (
        f"| `{row['label']}` | {fmt_cents(row['combined_all_net_pnl_cents'])} | "
        f"{pct(row['min_oos_coverage'])} | {row['strict_80_oos_coverage_pass']} | "
        f"{fmt_cents(row['current_all_net_pnl_cents'])}/{pct(row['current_all_coverage'])} | "
        f"{fmt_cents(row['v21_all_net_pnl_cents'])}/{pct(row['v21_all_coverage'])} | "
        f"{row['live_wins']}/{row['live_losses']} | {fmt_cents(row['live_net_pnl_cents'])} | "
        f"{pct(row['live_resolved_coverage'])} | {pct(row['live_registered_coverage'])} | "
        f"{fmt_num(row['live_prob_win_rate_gt_break_even'])} | {fmt_cents(row['live_p05_edge_cents'])} |"
    )


def write_report(generated: str, frame: pd.DataFrame, diagnostics: Dict[str, Any]) -> None:
    strict = frame[frame["strict_all"]]
    lines = [
        "# Hazard Price-Cap Granular Frontier",
        "",
        f"Generated UTC: `{generated}`",
        "",
        "## Scope",
        "",
        "- Research-only scan; no orders are submitted and no bot files or live processes are touched.",
        "- Scans ask caps from 73c to 80c with small score/extension variants.",
        "- Historical current/v21 rows are diagnostic; live registry cap rows are post-hoc diagnostics and must be forward-locked before use.",
        "",
        "## Diagnostics",
        "",
        f"- Current historical markets: {diagnostics['current_markets']}",
        f"- V21 historical markets: {diagnostics['v21_markets']}",
        f"- Live hazard registered/resolved rows: {diagnostics['live_hazard_registered_rows']}/{diagnostics['live_hazard_resolved_rows']}",
        f"- Rows scanned: {diagnostics['rows']}",
        f"- Strict historical + live coverage rows: {len(strict)}",
        "",
        "## Rows",
        "",
        "| policy | combined net | min OOS cov | hist strict cov | current net/cov | v21 net/cov | live wins/losses | live net | live resolved cov | live registered cov | live P(p>BE) | live p05 edge |",
        "|---|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for _, row in frame.iterrows():
        lines.append(table_row(row.to_dict()))
    lines += ["", "## Read", ""]
    if strict.empty:
        lines.append("- No granular cap clears strict historical OOS coverage and live resolved coverage simultaneously.")
    else:
        best = strict.iloc[0]
        lines.append(
            f"- Best strict granular cap is `{best['label']}` with combined historical net "
            f"{fmt_cents(best['combined_all_net_pnl_cents'])} and live post-hoc net "
            f"{fmt_cents(best['live_net_pnl_cents'])}."
        )
    if not frame.empty:
        best_live = frame.sort_values(["live_net_pnl_cents", "live_resolved_coverage"], ascending=[False, False]).iloc[0]
        lines.append(
            f"- Best live post-hoc cap is `{best_live['label']}` with "
            f"{fmt_cents(best_live['live_net_pnl_cents'])}, but this is not promotion evidence."
        )
    for path in [REPORT_LATEST, OUT_DIR / f"hazard_pricecap_granular_frontier_{generated}.md"]:
        path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    generated = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%SZ")
    frame, diagnostics = scan()
    frame.to_csv(CSV_LATEST, index=False)
    frame.to_csv(OUT_DIR / f"hazard_pricecap_granular_frontier_{generated}.csv", index=False)
    write_report(generated, frame, diagnostics)
    payload = {"generated_utc": generated, "diagnostics": diagnostics, "rows": frame.to_dict("records")}
    for path in [JSON_LATEST, OUT_DIR / f"hazard_pricecap_granular_frontier_{generated}.json"]:
        path.write_text(json.dumps(clean_json_local(payload), indent=2, sort_keys=True), encoding="utf-8")
    print("Hazard price-cap granular frontier complete")
    print(f"rows={len(frame)}")
    print(f"report={REPORT_LATEST}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
