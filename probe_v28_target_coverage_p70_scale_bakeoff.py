"""Scale bakeoff for p70 selective-memory FV.

Research-only; no live bot changes or orders.

The hard p70 idea decides which rows are eligible for sharpening. This probe
separates that decision from sharpening strength. A less aggressive logit
scale may give up a little calibration gain while becoming less brittle to the
next high-confidence loss.
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
OUT_JSON = OUT_DIR / "v28_target_coverage_p70_scale_bakeoff_latest.json"
OUT_MD = OUT_DIR / "v28_target_coverage_p70_scale_bakeoff_latest.md"

BOOTSTRAP_RUNS = 5000
BOOTSTRAP_SEED = 28759
SCALES = [1.05, 1.10, 1.15, 1.20, 1.25, 1.30]
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


def p70_scaled(row: dict[str, Any], scale: float) -> float:
    p = raw_probability(row)
    return sharpen(p, scale) if p >= 0.70 else p


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


def paired_deltas(rows: list[dict[str, Any]], scale: float) -> list[dict[str, Any]]:
    out = []
    for row in rows:
        p_raw = raw_probability(row)
        p_scaled = p70_scaled(row, scale)
        outcome = 1.0 if row.get("side_won") is True else 0.0
        out.append({
            "market": row.get("market"),
            "p_raw": p_raw,
            "p_scaled": p_scaled,
            "outcome": outcome,
            "adjusted": abs(p_scaled - p_raw) > 1e-9,
            "brier_delta": (p_scaled - outcome) ** 2 - (p_raw - outcome) ** 2,
            "logloss_delta": logloss(p_scaled, outcome) - logloss(p_raw, outcome),
        })
    return out


def adverse_delta(scale: float, raw_p: float = ADVERSE_RAW_P) -> dict[str, float]:
    row = {"p_raw": raw_p}
    p_raw = raw_probability(row)
    p_scaled = p70_scaled(row, scale)
    outcome = 0.0
    return {
        "raw_p": raw_p,
        "p_scaled": p_scaled,
        "brier_delta": (p_scaled - outcome) ** 2 - (p_raw - outcome) ** 2,
        "logloss_delta": logloss(p_scaled, outcome) - logloss(p_raw, outcome),
    }


def summarize(values: list[float], seed_offset: int) -> dict[str, Any]:
    boot = bootstrap(values, seed_offset)
    return {
        "mean": sum(values) / len(values) if values else None,
        "p95": boot.get("p95"),
        "prob_negative": boot.get("prob_negative"),
    }


def first_break(base_values: list[float], adverse_value: float, seed_offset: int) -> int | None:
    for count in range(1, 9):
        values = base_values + [adverse_value] * count
        summary = summarize(values, seed_offset + count)
        if summary["mean"] is None or summary["mean"] >= 0.0 or summary["p95"] is None or summary["p95"] >= 0.0:
            return count
    return None


def score_scale(rows: list[dict[str, Any]], scale: float) -> dict[str, Any]:
    paired = paired_deltas(rows, scale)
    briers = [float(row["brier_delta"]) for row in paired]
    losses = [float(row["logloss_delta"]) for row in paired]
    b_summary = summarize(briers, int(scale * 1000))
    l_summary = summarize(losses, int(scale * 2000))
    adverse = adverse_delta(scale)
    b_break = first_break(briers, float(adverse["brier_delta"]), int(scale * 3000))
    l_break = first_break(losses, float(adverse["logloss_delta"]), int(scale * 4000))
    return {
        "scale": scale,
        "rows": len(paired),
        "adjusted_rows": sum(1 for row in paired if row.get("adjusted")),
        "avg_p_adjusted": (
            sum(float(row["p_scaled"]) for row in paired if row.get("adjusted")) / sum(1 for row in paired if row.get("adjusted"))
            if any(row.get("adjusted") for row in paired)
            else None
        ),
        "brier_mean_delta": b_summary["mean"],
        "brier_p95": b_summary["p95"],
        "brier_prob_negative": b_summary["prob_negative"],
        "logloss_mean_delta": l_summary["mean"],
        "logloss_p95": l_summary["p95"],
        "logloss_prob_negative": l_summary["prob_negative"],
        "adverse_raw_p": ADVERSE_RAW_P,
        "adverse_scaled_p": adverse["p_scaled"],
        "first_brier_break_count": b_break,
        "first_logloss_break_count": l_break,
        "first_any_break_count": min([value for value in [b_break, l_break] if value is not None], default=None),
        "paired_rows": paired,
    }


def rank_key(row: dict[str, Any]) -> tuple[int, float, float, float]:
    first_break = row.get("first_any_break_count")
    # Prefer interval survival first, then calibration, with smaller scale as
    # tie-breaker because it makes fewer unsupported claims about certainty.
    fragility_penalty = 99 if first_break is None else -int(first_break)
    return (
        fragility_penalty,
        float(row.get("brier_p95") if row.get("brier_p95") is not None else 999.0),
        float(row.get("brier_mean_delta") if row.get("brier_mean_delta") is not None else 999.0),
        float(row.get("scale") or 999.0),
    )


def build_report() -> dict[str, Any]:
    rows = selected_rows()
    scored = [score_scale(rows, scale) for scale in SCALES]
    ranked = sorted(scored, key=rank_key)
    return {
        "policy_source": str(TARGET_JSON),
        "rows": len(rows),
        "best_scale": ranked[0].get("scale") if ranked else None,
        "ranked": ranked,
        "interpretation": interpretation(ranked),
    }


def interpretation(ranked: list[dict[str, Any]]) -> list[str]:
    if not ranked:
        return ["No settled target-coverage rows available."]
    best_cal = min(ranked, key=lambda row: float(row.get("brier_mean_delta") if row.get("brier_mean_delta") is not None else 999.0))
    best_robust = ranked[0]
    return [
        f"Best calibration scale is {best_cal.get('scale')} with Brier/logloss mean deltas {best_cal.get('brier_mean_delta')}/{best_cal.get('logloss_mean_delta')}.",
        f"Robustness-ranked scale is {best_robust.get('scale')} with first adverse p80 break count {best_robust.get('first_any_break_count')}.",
        "If all scales break on the first adverse p80 row, the problem is sample fragility, not scale tuning.",
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
        "# v28 Target-Coverage p70 Scale Bakeoff",
        "",
        f"- Rows: `{report.get('rows')}`",
        f"- Best robustness-ranked scale: `{report.get('best_scale')}`",
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
        "| scale | rows | adjusted | avg adjusted p | brier mean | brier p95 | logloss mean | logloss p95 | adverse p80 scaled | first brier break | first logloss break | first any break |",
        "|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ])
    for row in report.get("ranked") or []:
        lines.append(
            f"| {fmt(row.get('scale'))} | {row.get('rows')} | {row.get('adjusted_rows')} | {fmt(row.get('avg_p_adjusted'))} | "
            f"{fmt(row.get('brier_mean_delta'))} | {fmt(row.get('brier_p95'))} | "
            f"{fmt(row.get('logloss_mean_delta'))} | {fmt(row.get('logloss_p95'))} | "
            f"{fmt(row.get('adverse_scaled_p'))} | {row.get('first_brier_break_count')} | "
            f"{row.get('first_logloss_break_count')} | {row.get('first_any_break_count')} |"
        )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    report = build_report()
    write_md(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
