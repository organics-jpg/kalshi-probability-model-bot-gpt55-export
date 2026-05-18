"""Jackknife robustness for early-NO boundary FV deconfidence.

Research-only; no live bot changes or orders.

This is not promotion evidence. It stress-tests the diagnostic calibration
lift behind the frozen early-NO boundary FV entry validator by leaving one
market out at a time.
"""
from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any

from probe_v28_frozen_early_no_boundary_fv_entry import (
    POLICY,
    adjusted_row,
    diagnostic_market_set,
    raw_probability,
)
from probe_v28_raw_entry_coverage_valve import selected_base_rows
from probe_v28_target_coverage_fv_overlay_validator import apply_policy


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
FROZEN_JSON = OUT_DIR / "v28_frozen_early_no_boundary_fv_entry_latest.json"
OUT_JSON = OUT_DIR / "v28_early_no_boundary_fv_jackknife_latest.json"
OUT_MD = OUT_DIR / "v28_early_no_boundary_fv_jackknife_latest.md"


def load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
    return payload if isinstance(payload, dict) else {}


def clamp_prob(value: float) -> float:
    return max(0.000001, min(0.999999, value))


def logloss(p: float, outcome: float) -> float:
    p = clamp_prob(p)
    return -(outcome * math.log(p) + (1.0 - outcome) * math.log(1.0 - p))


def diagnostic_rows() -> list[dict[str, Any]]:
    markets, _ = diagnostic_market_set()
    rows = [row for row in selected_base_rows() if str(row.get("market") or "") in markets]
    adjusted = apply_policy([adjusted_row(row) for row in rows], POLICY)
    return [row for row in adjusted if row.get("side_won") is not None]


def score(rows: list[dict[str, Any]]) -> dict[str, Any]:
    scored = []
    for row in rows:
        won = row.get("side_won")
        if won is None:
            continue
        p_raw = row.get("p_raw_before_early_no_boundary")
        if p_raw is None:
            p_raw = raw_probability(row)
        p_adj = raw_probability(row)
        if p_raw is None or p_adj is None:
            continue
        outcome = 1.0 if won is True else 0.0
        scored.append({
            "market": row.get("market"),
            "won": won,
            "adjusted": bool(row.get("early_no_boundary_adjusted")),
            "net_cents": row.get("net_gross_cents_after_entry_fee"),
            "brier_delta": (clamp_prob(float(p_adj)) - outcome) ** 2 - (clamp_prob(float(p_raw)) - outcome) ** 2,
            "logloss_delta": logloss(float(p_adj), outcome) - logloss(float(p_raw), outcome),
        })
    briers = [float(row["brier_delta"]) for row in scored]
    losses = [float(row["logloss_delta"]) for row in scored]
    return {
        "rows": len(scored),
        "adjusted_rows": sum(1 for row in scored if row["adjusted"]),
        "wins": sum(1 for row in scored if row["won"] is True),
        "losses": sum(1 for row in scored if row["won"] is False),
        "net_cents": sum(float(row.get("net_cents") or 0.0) for row in scored),
        "brier_mean_delta": sum(briers) / len(briers) if briers else None,
        "logloss_mean_delta": sum(losses) / len(losses) if losses else None,
        "brier_positive_count": sum(1 for value in briers if value > 0.0),
        "brier_negative_count": sum(1 for value in briers if value < 0.0),
        "logloss_positive_count": sum(1 for value in losses if value > 0.0),
        "logloss_negative_count": sum(1 for value in losses if value < 0.0),
    }


def build_report() -> dict[str, Any]:
    frozen = load_json(FROZEN_JSON)
    rows = diagnostic_rows()
    markets = sorted({str(row.get("market") or "") for row in rows})
    full = score(rows)
    jackknife = []
    for market in markets:
        removed = [row for row in rows if str(row.get("market") or "") == market]
        kept = [row for row in rows if str(row.get("market") or "") != market]
        item = {
            "left_out_market": market,
            "removed_rows": len(removed),
            "removed_adjusted_rows": sum(1 for row in removed if row.get("early_no_boundary_adjusted")),
            "removed_wins": sum(1 for row in removed if row.get("side_won") is True),
            "removed_losses": sum(1 for row in removed if row.get("side_won") is False),
            "removed_net_cents": sum(float(row.get("net_gross_cents_after_entry_fee") or 0.0) for row in removed),
            **score(kept),
        }
        jackknife.append(item)
    failures = [
        row for row in jackknife
        if row.get("brier_mean_delta") is None
        or float(row["brier_mean_delta"]) >= 0.0
        or row.get("logloss_mean_delta") is None
        or float(row["logloss_mean_delta"]) >= 0.0
    ]
    worst_brier = max(jackknife, key=lambda row: float(row.get("brier_mean_delta") or -999.0), default={})
    worst_logloss = max(jackknife, key=lambda row: float(row.get("logloss_mean_delta") or -999.0), default={})
    return {
        "source_frozen_report": str(FROZEN_JSON),
        "freeze_ts": (frozen.get("freeze") or {}).get("freeze_ts_utc"),
        "policy": POLICY,
        "candidate": "early_no_boundary_fv_entry",
        "diagnostic_rows": len(rows),
        "markets": len(markets),
        "full": full,
        "jackknife": jackknife,
        "pass": bool(jackknife) and not failures,
        "failure_count": len(failures),
        "failure_markets": [row.get("left_out_market") for row in failures],
        "worst_brier": worst_brier,
        "worst_logloss": worst_logloss,
        "interpretation": [
            f"Full diagnostic Brier/logloss deltas are {full.get('brier_mean_delta')}/{full.get('logloss_mean_delta')} over {full.get('rows')} rows.",
            f"Leave-one-market-out failures: {len(failures)}.",
            f"Worst Brier leave-out is {worst_brier.get('left_out_market')} at {worst_brier.get('brier_mean_delta')}.",
            f"Worst logloss leave-out is {worst_logloss.get('left_out_market')} at {worst_logloss.get('logloss_mean_delta')}.",
            "This remains diagnostic only; frozen future rows are required before promotion.",
        ],
    }


def fmt(value: Any) -> str:
    if value is None:
        return "None"
    if isinstance(value, float):
        return f"{value:.6f}"
    return str(value)


def write_md(report: dict[str, Any]) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8")
    full = report.get("full") or {}
    lines = [
        "# v28 Early-NO Boundary FV Jackknife",
        "",
        "Leave-one-market-out anti-overfit check for the diagnostic early-NO boundary FV calibration lift.",
        "",
        f"- Freeze timestamp UTC: `{report.get('freeze_ts')}`",
        f"- Policy: `{report.get('policy')}`",
        f"- Candidate: `{report.get('candidate')}`",
        f"- Diagnostic rows/markets: `{report.get('diagnostic_rows')}/{report.get('markets')}`",
        f"- Pass: `{report.get('pass')}`",
        f"- Failure count: `{report.get('failure_count')}`",
        f"- Full rows/adjusted: `{full.get('rows')}/{full.get('adjusted_rows')}`",
        f"- Full Brier/logloss delta: `{fmt(full.get('brier_mean_delta'))}/{fmt(full.get('logloss_mean_delta'))}`",
        "",
        "## Current Read",
        "",
    ]
    for note in report.get("interpretation") or []:
        lines.append(f"- {note}")
    lines.extend([
        "",
        "## Leave-One-Market-Out",
        "",
        "| left out | removed adj | removed W/L | removed net c | rows | adjusted | brier mean | brier -/+ | logloss mean | logloss -/+ |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ])
    for row in report.get("jackknife") or []:
        lines.append(
            f"| {row.get('left_out_market')} | {row.get('removed_adjusted_rows')} | "
            f"{row.get('removed_wins')}/{row.get('removed_losses')} | {fmt(row.get('removed_net_cents'))} | "
            f"{row.get('rows')} | {row.get('adjusted_rows')} | {fmt(row.get('brier_mean_delta'))} | "
            f"{row.get('brier_negative_count')}/{row.get('brier_positive_count')} | {fmt(row.get('logloss_mean_delta'))} | "
            f"{row.get('logloss_negative_count')}/{row.get('logloss_positive_count')} |"
        )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    report = build_report()
    write_md(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
