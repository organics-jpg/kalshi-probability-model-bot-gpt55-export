"""p70 versus smooth confidence-temperature FV bakeoff.

Research-only; no live bot changes or orders.

The current best FV idea is hard selective memory: leave raw probabilities
below 70% alone, sharpen raw probabilities at or above 70%. This probe asks
whether that discontinuity is physically justified or whether a smoother
confidence-temperature function better matches the target-coverage rows.
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
OUT_JSON = OUT_DIR / "v28_target_coverage_confidence_temperature_bakeoff_latest.json"
OUT_MD = OUT_DIR / "v28_target_coverage_confidence_temperature_bakeoff_latest.md"

BOOTSTRAP_RUNS = 5000
BOOTSTRAP_SEED = 28731
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


def raw_probability(row: dict[str, Any]) -> float:
    value = as_float(row.get("p_raw") if row.get("p_raw") is not None else row.get("p_side"))
    if value is None:
        raise ValueError("missing raw probability")
    return clamp_prob(value)


def sharpen(p: float, scale: float) -> float:
    return clamp_prob(inv_logit(scale * logit(p)))


def ramp(value: float, lo: float, hi: float) -> float:
    if hi <= lo:
        return 0.0
    return max(0.0, min(1.0, (value - lo) / (hi - lo)))


def recross_heat(row: dict[str, Any]) -> float:
    recross = as_float(row.get("recross_hazard_score")) or 0.0
    edge = abs(as_float(row.get("raw_edge_prob")) or 0.0)
    abs_d = as_float(row.get("abs_d_sigma"))
    near_boundary = 1.0 if abs_d is None else max(0.0, min(1.0, (0.70 - abs_d) / 0.70))
    thin_edge = max(0.0, min(1.0, (0.06 - edge) / 0.06))
    return max(0.0, min(1.0, recross * near_boundary * thin_edge))


def raw(row: dict[str, Any]) -> float:
    return raw_probability(row)


def hard_p70(row: dict[str, Any]) -> float:
    p = raw_probability(row)
    return sharpen(p, 1.25) if p >= 0.70 else p


def hard_p68(row: dict[str, Any]) -> float:
    p = raw_probability(row)
    return sharpen(p, 1.25) if p >= 0.68 else p


def hard_p72(row: dict[str, Any]) -> float:
    p = raw_probability(row)
    return sharpen(p, 1.25) if p >= 0.72 else p


def smooth_60_80(row: dict[str, Any]) -> float:
    p = raw_probability(row)
    scale = 1.0 + 0.25 * ramp(p, 0.60, 0.80)
    return sharpen(p, scale)


def smooth_65_85(row: dict[str, Any]) -> float:
    p = raw_probability(row)
    scale = 1.0 + 0.25 * ramp(p, 0.65, 0.85)
    return sharpen(p, scale)


def smooth_70_90(row: dict[str, Any]) -> float:
    p = raw_probability(row)
    scale = 1.0 + 0.25 * ramp(p, 0.70, 0.90)
    return sharpen(p, scale)


def heat_gated_smooth_60_80(row: dict[str, Any]) -> float:
    p = raw_probability(row)
    heat = recross_heat(row)
    scale = 1.0 + 0.25 * ramp(p, 0.60, 0.80) * (1.0 - 0.70 * heat)
    return sharpen(p, scale)


def heat_gated_hard_p70(row: dict[str, Any]) -> float:
    p = raw_probability(row)
    if p < 0.70:
        return p
    scale = 1.0 + 0.25 * (1.0 - 0.70 * recross_heat(row))
    return sharpen(p, scale)


VARIANTS: dict[str, Callable[[dict[str, Any]], float]] = {
    "raw_probability": raw,
    "hard_logit125_p68": hard_p68,
    "hard_logit125_p70": hard_p70,
    "hard_logit125_p72": hard_p72,
    "smooth_logit_ramp_60_80": smooth_60_80,
    "smooth_logit_ramp_65_85": smooth_65_85,
    "smooth_logit_ramp_70_90": smooth_70_90,
    "heat_gated_smooth_60_80": heat_gated_smooth_60_80,
    "heat_gated_hard_p70": heat_gated_hard_p70,
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
        p_raw = raw_probability(row)
        p_variant = clamp_prob(float(fn(row)))
        outcome = 1.0 if row.get("side_won") is True else 0.0
        scored.append({
            "market": row.get("market"),
            "side": row.get("side"),
            "won": row.get("side_won"),
            "p_raw": p_raw,
            "p_variant": p_variant,
            "adjusted": abs(p_variant - p_raw) > 1e-9,
            "heat": recross_heat(row),
            "ask_prob": row.get("ask_prob"),
            "raw_edge_prob": row.get("raw_edge_prob"),
            "recross_hazard_score": row.get("recross_hazard_score"),
            "net_cents": row.get("net_gross_cents_after_entry_fee"),
            "brier_delta": (p_variant - outcome) ** 2 - (p_raw - outcome) ** 2,
            "logloss_delta": logloss(p_variant, outcome) - logloss(p_raw, outcome),
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
        "avg_p": sum(float(row["p_variant"]) for row in scored) / len(scored) if scored else None,
        "brier_mean_delta": sum(briers) / len(briers) if briers else None,
        "logloss_mean_delta": sum(losses) / len(losses) if losses else None,
        "brier_negative_count": sum(1 for value in briers if value < 0.0),
        "brier_positive_count": sum(1 for value in briers if value > 0.0),
        "brier_zero_count": sum(1 for value in briers if value == 0.0),
        "logloss_negative_count": sum(1 for value in losses if value < 0.0),
        "logloss_positive_count": sum(1 for value in losses if value > 0.0),
        "logloss_zero_count": sum(1 for value in losses if value == 0.0),
        "brier_bootstrap": bboot,
        "logloss_bootstrap": lboot,
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
        int(row.get("adjusted_rows") or 0),
    ))
    return {
        "policy": target.get("policy"),
        "forward_denominator": target.get("forward_denominator"),
        "entries": len(rows),
        "settled": sum(1 for row in rows if row.get("side_won") is not None),
        "best_variant": ranked[0].get("variant") if ranked else None,
        "ranked": ranked,
        "interpretation": interpretation(ranked),
    }


def interpretation(ranked: list[dict[str, Any]]) -> list[str]:
    best = next((row for row in ranked if row.get("variant") != "raw_probability"), {})
    hard = next((row for row in ranked if row.get("variant") == "hard_logit125_p70"), {})
    return [
        f"Best confidence-temperature diagnostic is {best.get('variant')} with Brier/logloss mean deltas {best.get('brier_mean_delta')}/{best.get('logloss_mean_delta')}.",
        f"Hard p70 has Brier/logloss mean deltas {hard.get('brier_mean_delta')}/{hard.get('logloss_mean_delta')} and p95s {(hard.get('brier_bootstrap') or {}).get('p95')}/{(hard.get('logloss_bootstrap') or {}).get('p95')}.",
        "If a smooth variant only wins by adjusting more boundary rows, it needs a stronger physics argument and a frozen validator before promotion.",
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
        "# v28 Target-Coverage Confidence Temperature Bakeoff",
        "",
        f"- Policy: `{report.get('policy')}`",
        f"- Entries/settled/denominator: `{report.get('entries')}/{report.get('settled')}/{report.get('forward_denominator')}`",
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
        "| rank | variant | rows | adjusted | W/L | avg p | brier mean | brier p95 | brier -/+ /0 | logloss mean | logloss p95 | logloss -/+ /0 | blockers |",
        "|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|",
    ])
    for idx, row in enumerate(report.get("ranked") or [], start=1):
        bboot = row.get("brier_bootstrap") or {}
        lboot = row.get("logloss_bootstrap") or {}
        lines.append(
            f"| {idx} | `{row.get('variant')}` | {row.get('rows')} | {row.get('adjusted_rows')} | "
            f"{row.get('wins')}/{row.get('losses')} | {fmt(row.get('avg_p'))} | "
            f"{fmt(row.get('brier_mean_delta'))} | {fmt(bboot.get('p95'))} | "
            f"{row.get('brier_negative_count')}/{row.get('brier_positive_count')}/{row.get('brier_zero_count')} | "
            f"{fmt(row.get('logloss_mean_delta'))} | {fmt(lboot.get('p95'))} | "
            f"{row.get('logloss_negative_count')}/{row.get('logloss_positive_count')}/{row.get('logloss_zero_count')} | "
            f"{', '.join(row.get('blockers') or []) or 'none'} |"
        )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    report = build_report()
    write_md(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
