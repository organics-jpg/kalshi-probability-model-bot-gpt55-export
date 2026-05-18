"""Registry-first fresh validation for locked profit candidates.

The recompute validators read the two-sided resolved ledger, which can lag the
live pre-resolution registry. This report treats the immutable registered
signals as the forward source of truth, joins denominator-audit coverage, and
flags stale recompute evidence explicitly.

Research-only: no orders are submitted and no bot files or live processes are
modified.
"""
from __future__ import annotations

import json
import math
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, Optional

import pandas as pd

from probe_cross_dataset_profit_frontier import fmt_cents, fmt_roi
from probe_interval_policy_degeneracy_audit import wilson_lower
from probe_market_interval_80coverage import (
    LEDGER,
    MARKET_COVERAGE_FLOOR,
    OUT_DIR,
    clean_json,
    load_side_rows,
    pct,
)
from probe_profit_lock_bayesian_ev_monitor import (
    MIN_FRESH_MARKETS_GATE,
    POSTERIOR_PROB_GATE,
    extra_perfect_wins_for_posterior,
    posterior_stats,
)


MAIN_REGISTRY = OUT_DIR / "profit_lock_pending_signal_registry_latest.csv"
PATH_REGISTRY = OUT_DIR / "kinetic_path_confirmation_pending_registry_latest.csv"
DENOMINATOR_AUDIT = OUT_DIR / "profit_lock_market_denominator_audit_latest.json"

REPORT_LATEST = OUT_DIR / "profit_lock_registry_fresh_validation_latest.md"
JSON_LATEST = OUT_DIR / "profit_lock_registry_fresh_validation_latest.json"
CSV_LATEST = OUT_DIR / "profit_lock_registry_fresh_validation_latest.csv"
BRANCH_CSV_LATEST = OUT_DIR / "profit_lock_registry_fresh_validation_branches_latest.csv"

KEY_LOCKS = {
    "book_margin",
    "book_margin_early",
    "book_p80_profit_frontier",
    "book_p80_ask90_frontier",
    "hazard_mean_touch80",
    "hazard_mean_touch80_ask76",
    "hazard_fallback_logit55",
    "hazard_fallback_logit55_wait8",
    "hazard_fallback_score60",
    "impulse_reversal_book_margin_fade",
    "logit_blend_edge10",
    "logit_blend_thresh55_edge15",
    "kinetic_path_confirm",
}


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


def load_registry(path: Path) -> pd.DataFrame:
    if not path.exists():
        return pd.DataFrame()
    rows = pd.read_csv(path)
    if rows.empty:
        return rows
    for col in ["registered_utc", "entry_dt", "close_dt"]:
        rows[col] = pd.to_datetime(rows.get(col), utc=True, errors="coerce")
    rows = rows.dropna(subset=["lock_name", "market", "registered_utc", "entry_dt", "close_dt"]).copy()
    rows = rows[rows["registered_utc"].lt(rows["close_dt"])].copy()
    if rows.empty:
        return rows
    rows["lock_name"] = rows["lock_name"].astype(str)
    rows["outcome_available_bool"] = rows["outcome_available"].map(bool_value)
    rows["win_bool"] = rows["win"].map(bool_value)
    for col in [
        "ask_cents",
        "entry_fee_cents",
        "net_pnl_cents",
        "seconds_to_close",
        "score_value",
        "touch_loss_rv_15m",
        "hazard_discounted_mean_15",
        "blend_logit_book_rv_hazard_mean",
        "book_p_side",
    ]:
        if col in rows.columns:
            rows[col] = pd.to_numeric(rows[col], errors="coerce")
    return rows


def load_all_registries() -> pd.DataFrame:
    frames = [load_registry(path) for path in [MAIN_REGISTRY, PATH_REGISTRY]]
    frames = [frame for frame in frames if not frame.empty]
    if not frames:
        return pd.DataFrame()
    return pd.concat(frames, ignore_index=True, sort=False)


def denominator_rows() -> Dict[str, Dict[str, Any]]:
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


def max_timestamp(rows: pd.DataFrame, column: str) -> Optional[pd.Timestamp]:
    if rows.empty or column not in rows.columns:
        return None
    series = pd.to_datetime(rows[column], utc=True, errors="coerce").dropna()
    if series.empty:
        return None
    return series.max()


def source_freshness(registry: pd.DataFrame) -> Dict[str, Any]:
    raw_max_close = None
    raw_rows = 0
    raw_error = ""
    try:
        side_rows = load_side_rows()
        raw_rows = int(len(side_rows))
        raw_max_close = max_timestamp(side_rows, "close_dt")
    except Exception as exc:  # pragma: no cover - diagnostic fallback
        raw_error = f"{type(exc).__name__}: {exc}"

    resolved = registry[registry["outcome_available_bool"]] if not registry.empty else registry
    pending = registry[~registry["outcome_available_bool"]] if not registry.empty else registry
    registry_resolved_max = max_timestamp(resolved, "close_dt")
    registry_pending_max = max_timestamp(pending, "close_dt")
    stale = (
        raw_max_close is not None
        and registry_resolved_max is not None
        and raw_max_close < registry_resolved_max
    )
    return {
        "raw_ledger": str(LEDGER),
        "raw_resolved_rows": raw_rows,
        "raw_resolved_max_close_dt": raw_max_close,
        "registry_rows": int(len(registry)) if not registry.empty else 0,
        "registry_resolved_rows": int(len(resolved)) if not registry.empty else 0,
        "registry_pending_rows": int(len(pending)) if not registry.empty else 0,
        "registry_resolved_max_close_dt": registry_resolved_max,
        "registry_pending_max_close_dt": registry_pending_max,
        "raw_recompute_source_stale": stale,
        "raw_load_error": raw_error,
    }


def summarize_lock(name: str, rows: pd.DataFrame, denom: Dict[str, Any]) -> Dict[str, Any]:
    resolved = rows[rows["outcome_available_bool"]].copy()
    pending = rows[~rows["outcome_available_bool"]].copy()
    n = int(len(resolved))
    wins = int(resolved["win_bool"].sum()) if n else 0
    losses = n - wins
    net = float(resolved["net_pnl_cents"].sum()) if n else 0.0
    entry_cost = None
    avg_entry_cost = None
    break_even = None
    if n:
        costs = pd.to_numeric(resolved["ask_cents"], errors="coerce") + pd.to_numeric(
            resolved["entry_fee_cents"], errors="coerce"
        ).fillna(0.0)
        entry_cost = float(costs.sum())
        avg_entry_cost = entry_cost / n if n else None
        break_even = avg_entry_cost / 100.0 if avg_entry_cost is not None else None
    accuracy = wins / n if n else None
    wilson = wilson_lower(wins, n) if n else None
    posterior = posterior_stats(wins, losses, break_even, avg_entry_cost)

    registered = int(len(rows))
    observed_markets = int(denom.get("observed_post_lock_markets") or 0)
    resolved_markets = int(denom.get("resolved_post_lock_markets") or 0)
    coverage_denominator = max(observed_markets, registered) if observed_markets else registered
    resolved_coverage_denominator = max(resolved_markets, n) if resolved_markets else max(registered, n)
    registered_coverage = registered / coverage_denominator if coverage_denominator else None
    resolved_coverage = n / resolved_coverage_denominator if resolved_coverage_denominator else None

    row = {
        "name": name,
        "registered": registered,
        "resolved": n,
        "pending": int(len(pending)),
        "wins": wins,
        "losses": losses,
        "accuracy": accuracy,
        "break_even": break_even,
        "wilson95_lower": wilson,
        "wilson_minus_break_even": (wilson - break_even) if wilson is not None and break_even is not None else None,
        "registered_coverage": registered_coverage,
        "resolved_coverage": resolved_coverage,
        "coverage_denominator": coverage_denominator,
        "resolved_coverage_denominator": resolved_coverage_denominator,
        "observed_post_lock_markets": observed_markets,
        "resolved_post_lock_markets": resolved_markets,
        "net_pnl_cents": net,
        "entry_cost_cents": entry_cost,
        "net_roi_on_cost": (net / entry_cost) if entry_cost else None,
        "median_ask": float(resolved["ask_cents"].median()) if n else None,
        "median_score": float(resolved["score_value"].median()) if n and "score_value" in resolved else None,
        "last_resolved_market": str(resolved.sort_values("close_dt").iloc[-1]["market"]) if n else "",
        "first_pending_market": str(pending.sort_values("close_dt").iloc[0]["market"]) if not pending.empty else "",
        **posterior,
    }
    row["posterior_extra_perfect_wins_to_gate"] = extra_perfect_wins_for_posterior(
        wins,
        losses,
        break_even,
        avg_entry_cost,
    )
    row["promotion_ready"] = (
        n >= MIN_FRESH_MARKETS_GATE
        and (resolved_coverage or 0.0) >= MARKET_COVERAGE_FLOOR
        and net > 0.0
        and (row["prob_win_rate_gt_break_even"] or 0.0) >= POSTERIOR_PROB_GATE
        and (row["posterior_p05_edge_cents"] or -1.0) > 0.0
    )
    row["wilson_ready"] = (
        n >= 75
        and (resolved_coverage or 0.0) >= MARKET_COVERAGE_FLOOR
        and net > 0.0
        and row["wilson_minus_break_even"] is not None
        and row["wilson_minus_break_even"] >= 0.0
    )
    return row


def branch_rows(name: str, rows: pd.DataFrame) -> Iterable[Dict[str, Any]]:
    resolved = rows[rows["outcome_available_bool"]].copy()
    if resolved.empty:
        return []
    out = []
    for chooser, part in resolved.groupby("chooser", dropna=False):
        n = int(len(part))
        wins = int(part["win_bool"].sum())
        out.append(
            {
                "lock": name,
                "chooser": str(chooser),
                "resolved": n,
                "wins": wins,
                "losses": n - wins,
                "accuracy": wins / n if n else None,
                "net_pnl_cents": float(part["net_pnl_cents"].sum()),
                "median_ask": float(part["ask_cents"].median()),
                "median_score": float(part["score_value"].median()) if "score_value" in part else None,
            }
        )
    return out


def table_rows(rows: Iterable[Dict[str, Any]]) -> list[str]:
    lines = [
        "| lock | reg/res/pend | wins/losses | acc | break-even | P(p>BE) | p05 edge | resolved cov | net P&L | ROI | median ask | extra wins | ready |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|",
    ]
    for row in rows:
        lines.append(
            f"| {row['name']} | {row['registered']}/{row['resolved']}/{row['pending']} | "
            f"{row['wins']}/{row['losses']} | {pct(row['accuracy'])} | {pct(row['break_even'])} | "
            f"{fmt_num(row['prob_win_rate_gt_break_even'])} | {fmt_cents(row['posterior_p05_edge_cents'])} | "
            f"{pct(row['resolved_coverage'])} | {fmt_cents(row['net_pnl_cents'])} | "
            f"{fmt_roi(row['net_roi_on_cost'])} | {fmt_cents(row['median_ask'])} | "
            f"{row['posterior_extra_perfect_wins_to_gate'] if row['posterior_extra_perfect_wins_to_gate'] is not None else 'NA'} | "
            f"{row['promotion_ready']} |"
        )
    return lines


def write_report(generated: str, rows: list[Dict[str, Any]], branches: list[Dict[str, Any]], freshness: Dict[str, Any]) -> None:
    ranked = sorted(rows, key=lambda row: ((row["promotion_ready"], row["net_pnl_cents"]), row["name"]), reverse=True)
    key_rows = [row for row in ranked if row["name"] in KEY_LOCKS]
    top_rows = ranked[:12]
    key_branches = [
        row
        for row in branches
        if row["lock"] in {"hazard_fallback_score60", "hazard_fallback_logit55", "hazard_fallback_logit55_wait8"}
    ]

    raw_max = freshness["raw_resolved_max_close_dt"]
    reg_max = freshness["registry_resolved_max_close_dt"]
    pending_max = freshness["registry_pending_max_close_dt"]
    lines = [
        "# Profit Lock Registry Fresh Validation",
        "",
        f"Generated UTC: `{generated}`",
        "",
        "## Scope",
        "",
        "- Research-only validation; no orders are submitted and no bot files or live processes are touched.",
        "- Uses pre-resolution registry rows as the forward source of truth.",
        "- Joins the market-denominator audit for recurring-market coverage.",
        "- Flags when recompute validators are stale relative to the live registry.",
        "",
        "## Source Freshness",
        "",
        "| source | rows | max resolved close | max pending close | stale vs registry |",
        "|---|---:|---:|---:|---|",
        f"| raw recompute ledger `{freshness['raw_ledger']}` | {freshness['raw_resolved_rows']} | "
        f"{raw_max.isoformat() if raw_max is not None else 'NA'} | NA | {freshness['raw_recompute_source_stale']} |",
        f"| registered signal registry | {freshness['registry_rows']} | "
        f"{reg_max.isoformat() if reg_max is not None else 'NA'} | "
        f"{pending_max.isoformat() if pending_max is not None else 'NA'} | False |",
    ]
    if freshness["raw_load_error"]:
        lines.append(f"- Raw recompute ledger load error: `{freshness['raw_load_error']}`")
    if freshness["raw_recompute_source_stale"]:
        lines.append(
            "- Recompute-based fresh validators are behind the registry; use registered-signal readiness for live promotion evidence."
        )

    lines += ["", "## Key Candidates", ""]
    lines.extend(table_rows(key_rows))
    lines += ["", "## Top Registered Locks", ""]
    lines.extend(table_rows(top_rows))
    lines += ["", "## Hazard Fallback Branches", ""]
    lines += [
        "| lock | chooser | resolved | wins/losses | acc | net P&L | median ask | median score |",
        "|---|---|---:|---:|---:|---:|---:|---:|",
    ]
    for row in sorted(key_branches, key=lambda item: (item["lock"], item["chooser"])):
        lines.append(
            f"| {row['lock']} | `{row['chooser']}` | {row['resolved']} | {row['wins']}/{row['losses']} | "
            f"{pct(row['accuracy'])} | {fmt_cents(row['net_pnl_cents'])} | "
            f"{fmt_cents(row['median_ask'])} | {fmt_num(row['median_score'])} |"
        )
    if not key_branches:
        lines.append("| none |  | 0 | 0/0 | NA | 0.0c | NA | NA |")

    lines += ["", "## Read", ""]
    if any(row["promotion_ready"] for row in rows):
        lines.append("- At least one registered lock clears the Bayesian promotion gate.")
    else:
        lines.append("- No registered lock clears the Bayesian promotion gate yet.")
    if any(row["wilson_ready"] for row in rows):
        lines.append("- At least one registered lock clears the stricter Wilson promotion gate.")
    else:
        lines.append("- No registered lock clears the stricter Wilson promotion gate yet.")
    path_stamp = OUT_DIR / f"profit_lock_registry_fresh_validation_{generated}.md"
    for path in [REPORT_LATEST, path_stamp]:
        path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    generated = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%SZ")
    registry = load_all_registries()
    denominators = denominator_rows()
    freshness = source_freshness(registry)

    rows: list[Dict[str, Any]] = []
    branches: list[Dict[str, Any]] = []
    if not registry.empty:
        for name, part in registry.groupby("lock_name", sort=True):
            denom = denominators.get(str(name), {})
            rows.append(summarize_lock(str(name), part.copy(), denom))
            branches.extend(branch_rows(str(name), part.copy()))

    rows_frame = pd.DataFrame(rows)
    branches_frame = pd.DataFrame(branches)
    rows_frame.to_csv(CSV_LATEST, index=False)
    rows_frame.to_csv(OUT_DIR / f"profit_lock_registry_fresh_validation_{generated}.csv", index=False)
    branches_frame.to_csv(BRANCH_CSV_LATEST, index=False)
    branches_frame.to_csv(OUT_DIR / f"profit_lock_registry_fresh_validation_branches_{generated}.csv", index=False)

    write_report(generated, rows, branches, freshness)
    payload = {
        "generated_utc": generated,
        "source_freshness": freshness,
        "rows": rows,
        "branches": branches,
        "ready_count": int(sum(bool(row["promotion_ready"]) for row in rows)),
        "wilson_ready_count": int(sum(bool(row["wilson_ready"]) for row in rows)),
    }
    for path in [JSON_LATEST, OUT_DIR / f"profit_lock_registry_fresh_validation_{generated}.json"]:
        path.write_text(json.dumps(clean_json_local(payload), indent=2, sort_keys=True), encoding="utf-8")

    print("Profit lock registry fresh validation complete")
    print(f"locks={len(rows)} ready_count={payload['ready_count']} wilson_ready_count={payload['wilson_ready_count']}")
    print(f"raw_recompute_source_stale={freshness['raw_recompute_source_stale']}")
    print(f"report={REPORT_LATEST}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
