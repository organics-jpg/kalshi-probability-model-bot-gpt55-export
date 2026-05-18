"""Leave-one-market-out robustness for target-coverage p70 FV.

Research-only; no live bot changes or orders.

This checks whether the current p70 diagnostic edge depends on one market. It
is not promotion evidence by itself because the p70 validator has a later
freeze timestamp, but it helps reject fragile ideas before waiting for more
forward rows.
"""
from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any

from probe_v28_target_coverage_conservative_fv_variants import logit125_p70, raw_probability


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
TARGET_JSON = OUT_DIR / "v28_target_coverage_fv_overlay_validator_latest.json"
OUT_JSON = OUT_DIR / "v28_target_coverage_p70_jackknife_latest.json"
OUT_MD = OUT_DIR / "v28_target_coverage_p70_jackknife_latest.md"


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


def score_rows(rows: list[dict[str, Any]]) -> dict[str, Any]:
    scored = []
    for row in rows:
        if row.get("side_won") is None:
            continue
        p_raw = clamp_prob(float(raw_probability(row)))
        p_p70 = clamp_prob(float(logit125_p70(row)))
        outcome = 1.0 if row.get("side_won") is True else 0.0
        scored.append({
            "market": row.get("market"),
            "brier_delta": (p_p70 - outcome) ** 2 - (p_raw - outcome) ** 2,
            "logloss_delta": logloss(p_p70, outcome) - logloss(p_raw, outcome),
            "adjusted": abs(p_p70 - p_raw) > 1e-9,
        })
    briers = [float(row["brier_delta"]) for row in scored]
    losses = [float(row["logloss_delta"]) for row in scored]
    return {
        "rows": len(scored),
        "adjusted": sum(1 for row in scored if row["adjusted"]),
        "brier_mean_delta": sum(briers) / len(briers) if briers else None,
        "logloss_mean_delta": sum(losses) / len(losses) if losses else None,
        "brier_positive_count": sum(1 for value in briers if value > 0.0),
        "brier_negative_count": sum(1 for value in briers if value < 0.0),
        "logloss_positive_count": sum(1 for value in losses if value > 0.0),
        "logloss_negative_count": sum(1 for value in losses if value < 0.0),
    }


def build_report() -> dict[str, Any]:
    target = load_json(TARGET_JSON)
    rows = [
        row for row in (target.get("forward_rows") if isinstance(target.get("forward_rows"), list) else [])
        if row.get("side_won") is not None
    ]
    markets = sorted({str(row.get("market") or "") for row in rows})
    full = score_rows(rows)
    jackknife = []
    for market in markets:
        subset = [row for row in rows if str(row.get("market") or "") != market]
        scored = score_rows(subset)
        jackknife.append({
            "left_out_market": market,
            **scored,
        })
    failures = [
        row for row in jackknife
        if row.get("brier_mean_delta") is None
        or float(row.get("brier_mean_delta")) >= 0.0
        or row.get("logloss_mean_delta") is None
        or float(row.get("logloss_mean_delta")) >= 0.0
    ]
    worst_brier = max(jackknife, key=lambda row: float(row.get("brier_mean_delta") or -999.0), default={})
    worst_logloss = max(jackknife, key=lambda row: float(row.get("logloss_mean_delta") or -999.0), default={})
    return {
        "policy": target.get("policy"),
        "entries": target.get("forward", [{}])[0].get("entries") if target.get("forward") else len(rows),
        "settled": len(rows),
        "forward_denominator": target.get("forward_denominator"),
        "full": full,
        "jackknife": jackknife,
        "pass": not failures and bool(jackknife),
        "failure_count": len(failures),
        "worst_brier": worst_brier,
        "worst_logloss": worst_logloss,
        "interpretation": [
            f"Full p70 Brier/logloss deltas are {full.get('brier_mean_delta')}/{full.get('logloss_mean_delta')} over {full.get('rows')} rows.",
            f"Leave-one-market-out failures: {len(failures)}.",
            f"Worst Brier leave-out is {worst_brier.get('left_out_market')} at {worst_brier.get('brier_mean_delta')}.",
            f"Worst logloss leave-out is {worst_logloss.get('left_out_market')} at {worst_logloss.get('logloss_mean_delta')}.",
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
        "# v28 Target-Coverage P70 Jackknife",
        "",
        f"- Policy: `{report.get('policy')}`",
        f"- Entries/settled/denominator: `{report.get('entries')}/{report.get('settled')}/{report.get('forward_denominator')}`",
        f"- Pass: `{report.get('pass')}`",
        f"- Failure count: `{report.get('failure_count')}`",
        f"- Full rows/adjusted: `{full.get('rows')}/{full.get('adjusted')}`",
        f"- Full Brier/logloss: `{fmt(full.get('brier_mean_delta'))}/{fmt(full.get('logloss_mean_delta'))}`",
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
        "| left out | rows | adjusted | brier mean | brier -/+ | logloss mean | logloss -/+ |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ])
    for row in report.get("jackknife") or []:
        lines.append(
            f"| {row.get('left_out_market')} | {row.get('rows')} | {row.get('adjusted')} | "
            f"{fmt(row.get('brier_mean_delta'))} | {row.get('brier_negative_count')}/{row.get('brier_positive_count')} | "
            f"{fmt(row.get('logloss_mean_delta'))} | {row.get('logloss_negative_count')}/{row.get('logloss_positive_count')} |"
        )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    report = build_report()
    write_md(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
