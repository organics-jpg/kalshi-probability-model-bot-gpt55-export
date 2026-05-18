"""Conservative FV sharpening variants on the target-coverage surface.

Research-only; no live bot changes or orders.

The current target-coverage FV overlay sharpens all raw probabilities >= 0.60.
Forward rows show one p60-75 loss now weakens the Brier interval and worsens
bucket ECE. This probe tests a physical alternative: only sharpen when the raw
probability is already high enough that boundary churn is less likely to be the
dominant force.
"""
from __future__ import annotations

import json
import math
import random
from pathlib import Path
from typing import Any, Callable


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
TARGET_JSON = OUT_DIR / "v28_target_coverage_fv_overlay_validator_latest.json"
OUT_JSON = OUT_DIR / "v28_target_coverage_conservative_fv_variants_latest.json"
OUT_MD = OUT_DIR / "v28_target_coverage_conservative_fv_variants_latest.md"

BOOTSTRAP_RUNS = 5000
BOOTSTRAP_SEED = 28655
MIN_SETTLED = 30


def load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
    return payload if isinstance(payload, dict) else {}


def as_float(value: Any) -> float | None:
    if value is None or value == "":
        return None
    try:
        out = float(value)
    except (TypeError, ValueError):
        return None
    return out if math.isfinite(out) else None


def clamp_prob(value: float) -> float:
    return max(0.000001, min(0.999999, value))


def logit(p: float) -> float:
    p = clamp_prob(p)
    return math.log(p / (1.0 - p))


def inv_logit(x: float) -> float:
    return 1.0 / (1.0 + math.exp(-x))


def logloss(p: float, outcome: float) -> float:
    p = clamp_prob(p)
    return -(outcome * math.log(p) + (1.0 - outcome) * math.log(1.0 - p))


def sharpen(p: float) -> float:
    return clamp_prob(inv_logit(1.25 * logit(p)))


def raw_p(row: dict[str, Any]) -> float:
    value = as_float(row.get("p_raw") if row.get("p_raw") is not None else row.get("p_side"))
    if value is None:
        raise ValueError("missing raw probability")
    return clamp_prob(value)


def raw_probability(row: dict[str, Any]) -> float:
    return raw_p(row)


def logit125_p60(row: dict[str, Any]) -> float:
    p = raw_p(row)
    return sharpen(p) if p >= 0.60 else p


def logit125_p70(row: dict[str, Any]) -> float:
    p = raw_p(row)
    return sharpen(p) if p >= 0.70 else p


def logit125_p75(row: dict[str, Any]) -> float:
    p = raw_p(row)
    return sharpen(p) if p >= 0.75 else p


def logit125_p80(row: dict[str, Any]) -> float:
    p = raw_p(row)
    return sharpen(p) if p >= 0.80 else p


def logit125_p60_skip_mid_loss_zone(row: dict[str, Any]) -> float:
    p = raw_p(row)
    recross = as_float(row.get("recross_hazard_score")) or 0.0
    ask = as_float(row.get("ask_prob")) or 0.0
    # Physics hypothesis: middle-confidence rows near the touch are still
    # vulnerable to recross/churn; sharpen them only when either conviction is
    # high or the recross score is calm.
    if p >= 0.75 or (p >= 0.60 and recross <= 0.60 and ask <= 0.70):
        return sharpen(p)
    return p


VARIANTS: dict[str, Callable[[dict[str, Any]], float]] = {
    "raw_probability": raw_probability,
    "logit125_p60": logit125_p60,
    "logit125_p70": logit125_p70,
    "logit125_p75": logit125_p75,
    "logit125_p80": logit125_p80,
    "logit125_p60_calm_mid_or_p75": logit125_p60_skip_mid_loss_zone,
}


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
        p_raw = raw_p(row)
        p_var = clamp_prob(float(fn(row)))
        outcome = 1.0 if row.get("side_won") is True else 0.0
        scored.append({
            "market": row.get("market"),
            "side": row.get("side"),
            "won": row.get("side_won"),
            "p_raw": p_raw,
            "p_variant": p_var,
            "raw_edge_prob": row.get("raw_edge_prob"),
            "ask_prob": row.get("ask_prob"),
            "recross_hazard_score": row.get("recross_hazard_score"),
            "reason": row.get("coverage_valve_reason"),
            "net_cents": row.get("net_gross_cents_after_entry_fee"),
            "brier_delta": (p_var - outcome) ** 2 - (p_raw - outcome) ** 2,
            "logloss_delta": logloss(p_var, outcome) - logloss(p_raw, outcome),
        })
    brier_deltas = [float(row["brier_delta"]) for row in scored]
    logloss_deltas = [float(row["logloss_delta"]) for row in scored]
    brier_boot = bootstrap(brier_deltas)
    logloss_boot = bootstrap(logloss_deltas)
    blockers = []
    if len(scored) < MIN_SETTLED:
        blockers.append("settled_lt_30")
    if name != "raw_probability":
        if not brier_deltas or sum(brier_deltas) / len(brier_deltas) >= 0.0:
            blockers.append("mean_brier_not_better")
        if brier_boot.get("p95") is None or float(brier_boot["p95"]) >= 0.0:
            blockers.append("brier_interval_not_strictly_negative")
        if not logloss_deltas or sum(logloss_deltas) / len(logloss_deltas) >= 0.0:
            blockers.append("mean_logloss_not_better")
        if logloss_boot.get("p95") is None or float(logloss_boot["p95"]) >= 0.0:
            blockers.append("logloss_interval_not_strictly_negative")
    return {
        "variant": name,
        "rows": len(scored),
        "wins": sum(1 for row in scored if row.get("won") is True),
        "losses": sum(1 for row in scored if row.get("won") is False),
        "avg_p": sum(float(row["p_variant"]) for row in scored) / len(scored) if scored else None,
        "brier_mean_delta": sum(brier_deltas) / len(brier_deltas) if brier_deltas else None,
        "logloss_mean_delta": sum(logloss_deltas) / len(logloss_deltas) if logloss_deltas else None,
        "brier_positive_count": sum(1 for value in brier_deltas if value > 0.0),
        "brier_negative_count": sum(1 for value in brier_deltas if value < 0.0),
        "logloss_positive_count": sum(1 for value in logloss_deltas if value > 0.0),
        "logloss_negative_count": sum(1 for value in logloss_deltas if value < 0.0),
        "brier_bootstrap": brier_boot,
        "logloss_bootstrap": logloss_boot,
        "blockers": blockers,
        "rows_detail": scored,
    }


def build_report() -> dict[str, Any]:
    target = load_json(TARGET_JSON)
    rows = target.get("forward_rows") if isinstance(target.get("forward_rows"), list) else []
    ranked = [score_variant(rows, name, fn) for name, fn in VARIANTS.items()]
    ranked.sort(key=lambda row: (
        0 if row.get("variant") != "raw_probability" and row.get("brier_mean_delta") is not None else 1,
        float(row.get("brier_mean_delta") if row.get("brier_mean_delta") is not None else 999.0),
        float((row.get("brier_bootstrap") or {}).get("p95") if (row.get("brier_bootstrap") or {}).get("p95") is not None else 999.0),
    ))
    return {
        "policy": target.get("policy"),
        "freeze_ts": target.get("freeze_ts"),
        "forward_denominator": target.get("forward_denominator"),
        "entries": len(rows),
        "settled": sum(1 for row in rows if row.get("side_won") is not None),
        "best_variant": ranked[0].get("variant") if ranked else None,
        "ranked": ranked,
        "interpretation": current_read(ranked),
    }


def current_read(ranked: list[dict[str, Any]]) -> list[str]:
    best_nonraw = next((row for row in ranked if row.get("variant") != "raw_probability"), {})
    return [
        f"Best conservative target-coverage FV variant is {best_nonraw.get('variant')} with Brier/logloss mean deltas {best_nonraw.get('brier_mean_delta')}/{best_nonraw.get('logloss_mean_delta')}.",
        f"Its Brier/logloss p95 deltas are {(best_nonraw.get('brier_bootstrap') or {}).get('p95')}/{(best_nonraw.get('logloss_bootstrap') or {}).get('p95')}.",
        "Discovery/diagnostic only unless frozen forward from this timestamp.",
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
        "# v28 Target-Coverage Conservative FV Variants",
        "",
        f"- Policy: `{report.get('policy')}`",
        f"- Forward entries/settled/denominator: `{report.get('entries')}/{report.get('settled')}/{report.get('forward_denominator')}`",
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
        "| rank | variant | rows | W/L | avg p | brier mean | brier p95 | brier -/+ | logloss mean | logloss p95 | logloss -/+ | blockers |",
        "|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|",
    ])
    for idx, row in enumerate(report.get("ranked") or [], start=1):
        bboot = row.get("brier_bootstrap") or {}
        lboot = row.get("logloss_bootstrap") or {}
        lines.append(
            f"| {idx} | `{row.get('variant')}` | {row.get('rows')} | {row.get('wins')}/{row.get('losses')} | "
            f"{fmt(row.get('avg_p'))} | {fmt(row.get('brier_mean_delta'))} | {fmt(bboot.get('p95'))} | "
            f"{row.get('brier_negative_count')}/{row.get('brier_positive_count')} | "
            f"{fmt(row.get('logloss_mean_delta'))} | {fmt(lboot.get('p95'))} | "
            f"{row.get('logloss_negative_count')}/{row.get('logloss_positive_count')} | "
            f"{', '.join(row.get('blockers') or []) or 'none'} |"
        )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    report = build_report()
    write_md(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
