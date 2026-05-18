"""Empirical-Bayes shrinkage for p70 selective-memory FV.

Research-only; no live bot changes or orders.

Hard p70 says which rows may be sharpened, but the current evidence is only
six adjusted winners. This probe treats the sharpening scale itself as
evidence-weighted: start near raw FV and earn the full logit scale only as the
p70 bucket accumulates adjusted rows.
"""
from __future__ import annotations

import json
import math
import random
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
TARGET_JSON = OUT_DIR / "v28_target_coverage_fv_overlay_validator_latest.json"
OUT_JSON = OUT_DIR / "v28_target_coverage_p70_empirical_bayes_latest.json"
OUT_MD = OUT_DIR / "v28_target_coverage_p70_empirical_bayes_latest.md"

BOOTSTRAP_RUNS = 5000
BOOTSTRAP_SEED = 28783
FULL_SCALE = 1.25
PRIOR_COUNTS = [6, 12, 24, 48]
ADVERSE_RAW_P = 0.80


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


def sharpen(p: float, scale: float) -> float:
    return clamp_prob(inv_logit(scale * logit(p)))


def logloss(p: float, outcome: float) -> float:
    p = clamp_prob(p)
    return -(outcome * math.log(p) + (1.0 - outcome) * math.log(1.0 - p))


def raw_probability(row: dict[str, Any]) -> float:
    value = as_float(row.get("p_raw") if row.get("p_raw") is not None else row.get("p_side"))
    if value is None:
        raise ValueError("missing raw probability")
    return clamp_prob(value)


def percentile(sorted_values: list[float], q: float) -> float | None:
    if not sorted_values:
        return None
    idx = min(len(sorted_values) - 1, max(0, int(round((len(sorted_values) - 1) * q))))
    return sorted_values[idx]


def bootstrap(values: list[float], seed_offset: int) -> dict[str, Any]:
    if len(values) < 5:
        return {"runs": 0, "p05": None, "p50": None, "p95": None, "prob_negative": None}
    rng = random.Random(BOOTSTRAP_SEED + seed_offset + len(values))
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


def selected_rows() -> list[dict[str, Any]]:
    target = load_json(TARGET_JSON)
    rows = target.get("forward_rows") if isinstance(target.get("forward_rows"), list) else []
    return [row for row in rows if row.get("side_won") is not None]


def evidence_scale(adjusted_count: int, prior_count: int) -> float:
    weight = adjusted_count / (adjusted_count + prior_count) if adjusted_count + prior_count > 0 else 0.0
    return 1.0 + (FULL_SCALE - 1.0) * weight


def p70_scaled(row: dict[str, Any], scale: float) -> float:
    p = raw_probability(row)
    return sharpen(p, scale) if p >= 0.70 else p


def score(rows: list[dict[str, Any]], prior_count: int) -> dict[str, Any]:
    adjusted_count = sum(1 for row in rows if raw_probability(row) >= 0.70)
    scale = evidence_scale(adjusted_count, prior_count)
    scored = []
    for row in rows:
        p_raw = raw_probability(row)
        p_var = p70_scaled(row, scale)
        outcome = 1.0 if row.get("side_won") is True else 0.0
        scored.append({
            "market": row.get("market"),
            "p_raw": p_raw,
            "p_variant": p_var,
            "adjusted": abs(p_var - p_raw) > 1e-9,
            "outcome": outcome,
            "side_won": row.get("side_won"),
            "brier_delta": (p_var - outcome) ** 2 - (p_raw - outcome) ** 2,
            "logloss_delta": logloss(p_var, outcome) - logloss(p_raw, outcome),
        })
    briers = [float(row["brier_delta"]) for row in scored]
    losses = [float(row["logloss_delta"]) for row in scored]
    bboot = bootstrap(briers, prior_count)
    lboot = bootstrap(losses, prior_count * 2)
    adverse = adverse_delta(scale)
    brier_break = first_break(briers, float(adverse["brier_delta"]), prior_count * 3)
    logloss_break = first_break(losses, float(adverse["logloss_delta"]), prior_count * 4)
    return {
        "variant": f"p70_empirical_bayes_prior{prior_count}",
        "prior_count": prior_count,
        "adjusted_evidence_count": adjusted_count,
        "scale": scale,
        "rows": len(scored),
        "adjusted_rows": sum(1 for row in scored if row.get("adjusted")),
        "brier_mean_delta": sum(briers) / len(briers) if briers else None,
        "brier_p95": bboot.get("p95"),
        "brier_prob_negative": bboot.get("prob_negative"),
        "logloss_mean_delta": sum(losses) / len(losses) if losses else None,
        "logloss_p95": lboot.get("p95"),
        "logloss_prob_negative": lboot.get("prob_negative"),
        "adverse_raw_p": ADVERSE_RAW_P,
        "adverse_variant_p": adverse["p_variant"],
        "first_brier_break_count": brier_break,
        "first_logloss_break_count": logloss_break,
        "first_any_break_count": min([value for value in [brier_break, logloss_break] if value is not None], default=None),
        "blockers": ["settled_lt_30"] if len(scored) < 30 else [],
        "rows_detail": scored,
    }


def adverse_delta(scale: float) -> dict[str, float]:
    row = {"p_raw": ADVERSE_RAW_P}
    p_raw = raw_probability(row)
    p_variant = p70_scaled(row, scale)
    outcome = 0.0
    return {
        "p_raw": p_raw,
        "p_variant": p_variant,
        "brier_delta": (p_variant - outcome) ** 2 - (p_raw - outcome) ** 2,
        "logloss_delta": logloss(p_variant, outcome) - logloss(p_raw, outcome),
    }


def first_break(base_values: list[float], adverse_value: float, seed_offset: int) -> int | None:
    for count in range(1, 9):
        values = base_values + [adverse_value] * count
        boot = bootstrap(values, seed_offset + count)
        mean = sum(values) / len(values) if values else None
        p95 = boot.get("p95")
        if mean is None or mean >= 0.0 or p95 is None or float(p95) >= 0.0:
            return count
    return None


def build_report() -> dict[str, Any]:
    rows = selected_rows()
    ranked = [score(rows, prior_count) for prior_count in PRIOR_COUNTS]
    ranked.sort(key=lambda row: (
        float(row.get("brier_p95") if row.get("brier_p95") is not None else 999.0),
        float(row.get("brier_mean_delta") if row.get("brier_mean_delta") is not None else 999.0),
        -int(row.get("prior_count") or 0),
    ))
    return {
        "source": str(TARGET_JSON),
        "rows": len(rows),
        "full_scale": FULL_SCALE,
        "best_variant": ranked[0].get("variant") if ranked else None,
        "ranked": ranked,
        "interpretation": interpretation(ranked),
    }


def interpretation(ranked: list[dict[str, Any]]) -> list[str]:
    if not ranked:
        return ["No settled target-coverage rows available."]
    best = ranked[0]
    fullish = next((row for row in ranked if row.get("prior_count") == 6), best)
    conservative = next((row for row in ranked if row.get("prior_count") == 48), best)
    return [
        f"Best empirical-Bayes p70 variant is {best.get('variant')} with scale {best.get('scale')} and Brier/logloss p95 {best.get('brier_p95')}/{best.get('logloss_p95')}.",
        f"Light prior count 6 uses scale {fullish.get('scale')}; heavy prior count 48 uses scale {conservative.get('scale')}.",
        f"Best variant first adverse p80 break count is {best.get('first_any_break_count')}.",
        "This is an anti-overfit throttle on certainty, not a new entry selector; it preserves target coverage.",
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
        "# v28 Target-Coverage p70 Empirical Bayes",
        "",
        f"- Rows: `{report.get('rows')}`",
        f"- Full target scale: `{report.get('full_scale')}`",
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
        "| variant | prior count | evidence count | scale | rows | adjusted | brier mean | brier p95 | logloss mean | logloss p95 | adverse p80 p | first break | blockers |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|",
    ])
    for row in report.get("ranked") or []:
        lines.append(
            f"| {row.get('variant')} | {row.get('prior_count')} | {row.get('adjusted_evidence_count')} | "
            f"{fmt(row.get('scale'))} | {row.get('rows')} | {row.get('adjusted_rows')} | "
            f"{fmt(row.get('brier_mean_delta'))} | {fmt(row.get('brier_p95'))} | "
            f"{fmt(row.get('logloss_mean_delta'))} | {fmt(row.get('logloss_p95'))} | "
            f"{fmt(row.get('adverse_variant_p'))} | {row.get('first_any_break_count')} | "
            f"{', '.join(row.get('blockers') or []) or 'none'} |"
        )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    report = build_report()
    write_md(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
