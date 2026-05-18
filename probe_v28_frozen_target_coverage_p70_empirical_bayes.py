"""Frozen validator for empirical-Bayes p70 FV.

Research-only; no live bot changes or orders.

Freezes the p70 selective-memory idea with evidence-weighted scale. This keeps
the same target-coverage entry surface and only changes the FV probability:
raw p < 0.70 stays raw, raw p >= 0.70 is logit-sharpened with a scale earned
from the observed adjusted p70 bucket count.
"""
from __future__ import annotations

import json
import math
import random
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

from probe_v28_frozen_forward_candidates import market_timing, parse_ts
from probe_v28_exchange_result_enrichment import attach_exchange_results
from probe_v28_raw_entry_coverage_valve import selected_base_rows
from probe_v28_target_coverage_fv_overlay_validator import DEFAULT_POLICY, apply_policy
from probe_v28_target_coverage_p70_empirical_bayes import FULL_SCALE, raw_probability


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
STATE_JSON = OUT_DIR / "v28_frozen_target_coverage_p70_empirical_bayes_state.json"
OUT_JSON = OUT_DIR / "v28_frozen_target_coverage_p70_empirical_bayes_latest.json"
OUT_MD = OUT_DIR / "v28_frozen_target_coverage_p70_empirical_bayes_latest.md"

MIN_SETTLED = 30
BOOTSTRAP_RUNS = 5000
BOOTSTRAP_SEED = 28791
PRIOR_COUNT = 6


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
    return payload if isinstance(payload, dict) else {}


def load_or_create_state() -> dict[str, Any]:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    if STATE_JSON.exists():
        payload = load_json(STATE_JSON)
        if payload.get("freeze_ts_utc"):
            return payload
    state = {
        "freeze_ts_utc": utc_now_iso(),
        "entry_policy": DEFAULT_POLICY,
        "variant": "p70_empirical_bayes_prior6",
        "prior_count": PRIOR_COUNT,
        "full_scale": FULL_SCALE,
        "rule": "raw p < 0.70 stays raw; raw p >= 0.70 uses scale 1 + (full_scale - 1) * adjusted_count / (adjusted_count + prior_count)",
        "source_artifact": "v28_target_coverage_p70_empirical_bayes_latest.json",
    }
    STATE_JSON.write_text(json.dumps(state, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return state


def clamp_prob(value: float) -> float:
    return max(0.000001, min(0.999999, value))


def logit(p: float) -> float:
    p = clamp_prob(p)
    return math.log(p / (1.0 - p))


def inv_logit(x: float) -> float:
    return 1.0 / (1.0 + math.exp(-x))


def sharpen(p: float, scale: float) -> float:
    return clamp_prob(inv_logit(scale * logit(p)))


def evidence_scale(adjusted_count: int, prior_count: int, full_scale: float) -> float:
    weight = adjusted_count / (adjusted_count + prior_count) if adjusted_count + prior_count > 0 else 0.0
    return 1.0 + (full_scale - 1.0) * weight


def p70_empirical_bayes_probability(row: dict[str, Any], scale: float) -> float:
    p = clamp_prob(float(raw_probability(row)))
    return sharpen(p, scale) if p >= 0.70 else p


def logloss(p: float, outcome: float) -> float:
    p = clamp_prob(p)
    return -(outcome * math.log(p) + (1.0 - outcome) * math.log(1.0 - p))


def percentile(sorted_values: list[float], q: float) -> float | None:
    if not sorted_values:
        return None
    idx = min(len(sorted_values) - 1, max(0, int(round((len(sorted_values) - 1) * q))))
    return sorted_values[idx]


def bootstrap(values: list[float]) -> dict[str, Any]:
    if len(values) < 5:
        return {"runs": 0, "p05": None, "p50": None, "p95": None, "prob_negative": None}
    rng = random.Random(BOOTSTRAP_SEED + len(values))
    samples = []
    for _ in range(BOOTSTRAP_RUNS):
        samples.append(sum(rng.choice(values) for _ in values) / len(values))
    samples.sort()
    return {
        "runs": BOOTSTRAP_RUNS,
        "p05": percentile(samples, 0.05),
        "p50": percentile(samples, 0.50),
        "p95": percentile(samples, 0.95),
        "prob_negative": sum(1 for value in samples if value < 0.0) / len(samples),
    }


def score_variant(rows: list[dict[str, Any]], name: str, fn: Callable[[dict[str, Any]], float]) -> dict[str, Any]:
    scored = []
    for row in rows:
        if row.get("side_won") is None:
            continue
        p_raw = clamp_prob(float(raw_probability(row)))
        p_var = clamp_prob(float(fn(row)))
        outcome = 1.0 if row.get("side_won") is True else 0.0
        scored.append({
            "market": row.get("market"),
            "side": row.get("side"),
            "won": row.get("side_won"),
            "p_raw": p_raw,
            "p_variant": p_var,
            "adjusted": abs(p_var - p_raw) > 1e-9,
            "net_cents": row.get("net_gross_cents_after_entry_fee"),
            "brier_delta": (p_var - outcome) ** 2 - (p_raw - outcome) ** 2,
            "logloss_delta": logloss(p_var, outcome) - logloss(p_raw, outcome),
        })
    briers = [float(row["brier_delta"]) for row in scored]
    losses = [float(row["logloss_delta"]) for row in scored]
    bboot = bootstrap(briers)
    lboot = bootstrap(losses)
    blockers = []
    if len(scored) < MIN_SETTLED:
        blockers.append("settled_lt_30")
    if name != "raw_probability":
        if not briers or sum(briers) / len(briers) >= 0.0:
            blockers.append("mean_brier_not_better")
        if bboot.get("p95") is None or float(bboot["p95"]) >= 0.0:
            blockers.append("brier_interval_not_strictly_negative")
        if not losses or sum(losses) / len(losses) >= 0.0:
            blockers.append("mean_logloss_not_better")
        if lboot.get("p95") is None or float(lboot["p95"]) >= 0.0:
            blockers.append("logloss_interval_not_strictly_negative")
    return {
        "variant": name,
        "rows": len(scored),
        "adjusted_rows": sum(1 for row in scored if row.get("adjusted")),
        "wins": sum(1 for row in scored if row.get("won") is True),
        "losses": sum(1 for row in scored if row.get("won") is False),
        "net_cents": sum(float(row.get("net_cents") or 0.0) for row in scored),
        "brier_mean_delta": sum(briers) / len(briers) if briers else None,
        "logloss_mean_delta": sum(losses) / len(losses) if losses else None,
        "brier_bootstrap": bboot,
        "logloss_bootstrap": lboot,
        "blockers": blockers,
        "rows_detail": scored,
    }


def build_report() -> dict[str, Any]:
    state = load_or_create_state()
    timing = market_timing(parse_ts(state["freeze_ts_utc"]))
    forward_markets = timing["clean_forward_markets"]
    all_rows = apply_policy(selected_base_rows(), str(state.get("entry_policy") or DEFAULT_POLICY))
    rows = attach_exchange_results([row for row in all_rows if str(row.get("market") or "") in forward_markets])
    adjusted_count = sum(1 for row in rows if clamp_prob(float(raw_probability(row))) >= 0.70)
    scale = evidence_scale(adjusted_count, int(state.get("prior_count") or PRIOR_COUNT), float(state.get("full_scale") or FULL_SCALE))
    ranked = [
        score_variant(rows, "raw_probability", raw_probability),
        score_variant(rows, str(state.get("variant")), lambda row: p70_empirical_bayes_probability(row, scale)),
    ]
    ranked.sort(key=lambda row: (
        row.get("variant") == "raw_probability",
        float(row.get("brier_mean_delta") if row.get("brier_mean_delta") is not None else 999.0),
    ))
    return {
        "freeze": state,
        "future_denominator": len(forward_markets),
        "entries": len(rows),
        "settled": sum(1 for row in rows if row.get("side_won") is not None),
        "adjusted_evidence_count": adjusted_count,
        "scale": scale,
        "coverage_pct": 100.0 * len(rows) / len(forward_markets) if forward_markets else None,
        "ranked": ranked,
        "best_variant": ranked[0].get("variant") if ranked else None,
        "interpretation": current_read(ranked, rows, forward_markets, scale),
    }


def current_read(ranked: list[dict[str, Any]], rows: list[dict[str, Any]], forward_markets: set[str], scale: float) -> list[str]:
    best = ranked[0] if ranked else {}
    return [
        f"Frozen empirical-Bayes p70 FV has {len(rows)} entries over {len(forward_markets)} future markets.",
        f"Current earned scale is {scale}.",
        f"Best variant is {best.get('variant')} with Brier/logloss deltas {best.get('brier_mean_delta')}/{best.get('logloss_mean_delta')}.",
    ]


def fmt(value: Any) -> str:
    if value is None:
        return "None"
    if isinstance(value, float):
        return f"{value:.6f}"
    return str(value)


def write_md(report: dict[str, Any]) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8")
    lines = [
        "# v28 Frozen Target-Coverage p70 Empirical Bayes",
        "",
        f"- Freeze timestamp UTC: `{(report.get('freeze') or {}).get('freeze_ts_utc')}`",
        f"- Entry policy: `{(report.get('freeze') or {}).get('entry_policy')}`",
        f"- Variant: `{(report.get('freeze') or {}).get('variant')}`",
        f"- Future entries/settled/denominator: `{report.get('entries')}/{report.get('settled')}/{report.get('future_denominator')}`",
        f"- Adjusted evidence count/current scale: `{report.get('adjusted_evidence_count')}/{fmt(report.get('scale'))}`",
        f"- Coverage: `{fmt(report.get('coverage_pct'))}`",
        f"- Best variant: `{report.get('best_variant')}`",
        "",
        "## Current Read",
        "",
    ]
    for note in report.get("interpretation") or []:
        lines.append(f"- {note}")
    lines.extend([
        "",
        "## Ranking",
        "",
        "| rank | variant | rows | adjusted | W/L | net c | brier mean | brier p95 | logloss mean | logloss p95 | blockers |",
        "|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---|",
    ])
    for idx, row in enumerate(report.get("ranked") or [], start=1):
        bboot = row.get("brier_bootstrap") or {}
        lboot = row.get("logloss_bootstrap") or {}
        lines.append(
            f"| {idx} | `{row.get('variant')}` | {row.get('rows')} | {row.get('adjusted_rows')} | "
            f"{row.get('wins')}/{row.get('losses')} | {fmt(row.get('net_cents'))} | "
            f"{fmt(row.get('brier_mean_delta'))} | {fmt(bboot.get('p95'))} | "
            f"{fmt(row.get('logloss_mean_delta'))} | {fmt(lboot.get('p95'))} | "
            f"{', '.join(row.get('blockers') or []) or 'none'} |"
        )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    report = build_report()
    write_md(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
