"""Bayesian/sequential EV monitor for locked BTC 15m profit candidates.

Fresh samples are too small for Wilson-over-break-even proof, but the locks
need an explicit sequential read as new markets settle. This monitor uses only
fresh post-lock outcomes from the existing validation JSON files and asks:

- what is the posterior probability that the true win rate is above the
  observed average fee-aware break-even probability?
- what is the posterior expected net edge per selected contract?
- how many additional perfect fresh wins would be needed to clear a 95%
  posterior probability gate?

The posterior uses a neutral Beta(1, 1) prior by default. This is not a live
promotion gate by itself; it is a research monitor next to the Wilson gate.

Research-only: no orders are submitted and no bot files or live processes are
modified.
"""
from __future__ import annotations

import json
import math
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional

import numpy as np
import pandas as pd

from probe_cross_dataset_profit_frontier import fmt_cents, fmt_roi
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

POSTERIOR_SAMPLES = 200_000
POSTERIOR_PROB_GATE = 0.95
MIN_FRESH_MARKETS_GATE = 30
RNG_SEED = 20260502


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


def posterior_stats(
    wins: int,
    losses: int,
    break_even: Optional[float],
    avg_entry_cost: Optional[float],
    *,
    seed_offset: int = 0,
) -> Dict[str, Any]:
    if break_even is None or avg_entry_cost is None:
        return {
            "posterior_alpha": 1.0 + wins,
            "posterior_beta": 1.0 + losses,
            "prob_win_rate_gt_break_even": None,
            "posterior_mean_win_rate": None,
            "posterior_p05_win_rate": None,
            "posterior_p95_win_rate": None,
            "posterior_mean_edge_cents": None,
            "posterior_p05_edge_cents": None,
        }
    alpha = 1.0 + int(wins)
    beta = 1.0 + int(losses)
    rng = np.random.default_rng(RNG_SEED + seed_offset + wins * 17 + losses * 31)
    draws = rng.beta(alpha, beta, size=POSTERIOR_SAMPLES)
    edge = 100.0 * draws - float(avg_entry_cost)
    return {
        "posterior_alpha": alpha,
        "posterior_beta": beta,
        "prob_win_rate_gt_break_even": float((draws > float(break_even)).mean()),
        "posterior_mean_win_rate": float(draws.mean()),
        "posterior_p05_win_rate": float(np.quantile(draws, 0.05)),
        "posterior_p95_win_rate": float(np.quantile(draws, 0.95)),
        "posterior_mean_edge_cents": float(edge.mean()),
        "posterior_p05_edge_cents": float(np.quantile(edge, 0.05)),
        "posterior_p95_edge_cents": float(np.quantile(edge, 0.95)),
    }


def extra_perfect_wins_for_posterior(
    wins: int,
    losses: int,
    break_even: Optional[float],
    avg_entry_cost: Optional[float],
    max_extra: int = 5_000,
) -> Optional[int]:
    if break_even is None or avg_entry_cost is None:
        return None
    for extra in range(max_extra + 1):
        stats = posterior_stats(wins + extra, losses, break_even, avg_entry_cost, seed_offset=10_000 + extra)
        prob = stats["prob_win_rate_gt_break_even"]
        if prob is not None and prob >= POSTERIOR_PROB_GATE:
            return extra
    return None


def summarize(name: str, path: Path, readiness_rows: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
    ready = readiness_rows.get(name)
    if path.exists():
        payload = json.loads(path.read_text(encoding="utf-8"))
        lock = payload["lock"]
        all_metric = payload["all_metric"]
    elif ready:
        payload = {}
        lock = {"policy": {"label": ""}, "overlay": {"label": ready.get("overlay", "")}, "lock_close_dt": None}
        all_metric = {
            "accuracy": ready.get("accuracy"),
            "fee_aware_break_even_accuracy": ready.get("break_even"),
            "net_pnl_cents": ready.get("net_pnl_cents"),
            "net_roi_on_cost": ready.get("net_roi_on_cost"),
        }
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
            "coverage": ready.get("resolved_coverage"),
            "net_pnl_cents": ready.get("net_pnl_cents"),
            "net_roi_on_cost": ready.get("net_roi_on_cost"),
        }
        fresh_source = "registered_signal_readiness"
    else:
        fresh = payload["fresh_metric"]
        fresh_source = "fresh_metric"
    wins = int(fresh.get("wins") or 0)
    losses = int(fresh.get("losses") or 0)
    markets = int(fresh.get("markets") or 0)
    entry_cost = fresh.get("entry_cost_cents")
    avg_entry_cost = (float(entry_cost) / markets) if entry_cost is not None and markets else None
    break_even = fresh.get("fee_aware_break_even_accuracy")
    if break_even is None:
        break_even = all_metric.get("fee_aware_break_even_accuracy")
    if avg_entry_cost is None and break_even is not None:
        avg_entry_cost = 100.0 * float(break_even)
    if avg_entry_cost is None and all_metric.get("entry_cost_cents") is not None and all_metric.get("markets"):
        avg_entry_cost = float(all_metric["entry_cost_cents"]) / float(all_metric["markets"])
    stats = posterior_stats(wins, losses, break_even, avg_entry_cost, seed_offset=0 if name == "original" else 1000)
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
        "fresh_markets": markets,
        "fresh_wins": wins,
        "fresh_losses": losses,
        "fresh_accuracy": fresh.get("accuracy"),
        "fresh_break_even": break_even,
        "fresh_coverage": fresh.get("coverage"),
        "fresh_net_pnl_cents": fresh.get("net_pnl_cents"),
        "fresh_net_roi": fresh.get("net_roi_on_cost"),
        "fresh_avg_entry_cost_cents": avg_entry_cost,
        "all_accuracy": all_metric.get("accuracy"),
        "all_break_even": all_metric.get("fee_aware_break_even_accuracy"),
        "all_net_pnl_cents": all_metric.get("net_pnl_cents"),
        "all_net_roi": all_metric.get("net_roi_on_cost"),
        **stats,
    }
    row["posterior_extra_perfect_wins_to_gate"] = extra_perfect_wins_for_posterior(
        wins,
        losses,
        break_even,
        avg_entry_cost,
    )
    row["posterior_ready"] = (
        markets >= MIN_FRESH_MARKETS_GATE
        and (row["fresh_coverage"] or 0.0) >= MARKET_COVERAGE_FLOOR
        and (row["fresh_net_pnl_cents"] or 0.0) > 0.0
        and (row["prob_win_rate_gt_break_even"] or 0.0) >= POSTERIOR_PROB_GATE
        and (row["posterior_p05_edge_cents"] or -1.0) > 0.0
    )
    return row


def write_report(path: Path, generated: str, rows: list[Dict[str, Any]]) -> None:
    lines = [
        "# Profit Lock Bayesian EV Monitor",
        "",
        f"Generated UTC: `{generated}`",
        "",
        "## Scope",
        "",
        "- Research-only monitor; no orders are submitted and no bot files or live processes are touched.",
        "- Uses strict registered-signal readiness rows when available; otherwise falls back to validator fresh metrics.",
        "- Posterior uses neutral Beta(1, 1), Monte Carlo sampled for EV probability and edge intervals.",
        f"- Ready gate: at least {MIN_FRESH_MARKETS_GATE} fresh selected markets, >=80% fresh coverage, positive fresh net, posterior P(win rate > break-even) >= {POSTERIOR_PROB_GATE:.2f}, and positive p05 posterior edge.",
        "",
        "## Posterior EV State",
        "",
        "| lock | source | overlay | fresh | acc | break-even | net P&L | posterior mean p | P(p>BE) | p05 edge | mean edge | extra perfect wins | ready |",
        "|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|",
    ]
    for row in rows:
        lines.append(
            f"| {row['name']} | `{row['fresh_metric_source']}` | `{row['overlay'] or 'none'}` | "
            f"{row['fresh_wins']}/{row['fresh_losses']} of {row['fresh_markets']} | "
            f"{pct(row['fresh_accuracy'])} | {pct(row['fresh_break_even'])} | "
            f"{fmt_cents(row['fresh_net_pnl_cents'])} | {pct(row['posterior_mean_win_rate'])} | "
            f"{fmt_num(row['prob_win_rate_gt_break_even'])} | {fmt_cents(row['posterior_p05_edge_cents'])} | "
            f"{fmt_cents(row['posterior_mean_edge_cents'])} | "
            f"{row['posterior_extra_perfect_wins_to_gate'] if row['posterior_extra_perfect_wins_to_gate'] is not None else 'NA'} | "
            f"{row['posterior_ready']} |"
        )
    lines += ["", "## Read", ""]
    ready = [row for row in rows if row["posterior_ready"]]
    if ready:
        lines.append("- At least one lock clears the Bayesian EV gate.")
    else:
        lines.append("- No lock clears the Bayesian EV gate yet.")
    for row in rows:
        extra = row["posterior_extra_perfect_wins_to_gate"]
        lines.append(
            f"- {row['name']}: posterior P(p>break-even) is {fmt_num(row['prob_win_rate_gt_break_even'])}; "
            f"needs {extra if extra is not None else 'NA'} additional perfect fresh wins to reach the posterior probability gate from the current state."
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
    md_latest = OUT_DIR / "profit_lock_bayesian_ev_monitor_latest.md"
    md_stamp = OUT_DIR / f"profit_lock_bayesian_ev_monitor_{generated}.md"
    json_latest = OUT_DIR / "profit_lock_bayesian_ev_monitor_latest.json"
    json_stamp = OUT_DIR / f"profit_lock_bayesian_ev_monitor_{generated}.json"
    csv_latest = OUT_DIR / "profit_lock_bayesian_ev_monitor_latest.csv"
    csv_stamp = OUT_DIR / f"profit_lock_bayesian_ev_monitor_{generated}.csv"
    write_report(md_latest, generated, rows)
    write_report(md_stamp, generated, rows)
    pd.DataFrame(rows).to_csv(csv_latest, index=False)
    pd.DataFrame(rows).to_csv(csv_stamp, index=False)
    payload = {
        "generated_utc": generated,
        "posterior_samples": POSTERIOR_SAMPLES,
        "posterior_prob_gate": POSTERIOR_PROB_GATE,
        "min_fresh_markets_gate": MIN_FRESH_MARKETS_GATE,
        "rows": rows,
        "ready_count": int(sum(bool(row["posterior_ready"]) for row in rows)),
    }
    for path in [json_latest, json_stamp]:
        path.write_text(json.dumps(clean_json_local(payload), indent=2, sort_keys=True), encoding="utf-8")
    print("Profit lock Bayesian EV monitor complete")
    print(f"ready_count={payload['ready_count']}")
    print(f"report={md_latest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
