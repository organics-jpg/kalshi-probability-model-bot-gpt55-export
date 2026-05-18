"""Boundary-temperature FV diagnostics on the target-coverage surface.

Research-only; no live bot changes or orders.

The target-coverage surface has two different physical forces:
- high-conviction rows where sharpening helps;
- boundary/churn rows where raw probability may be too certain.

This probe tests probability-only deconfidence variants. It does not promote
or freeze them; it asks whether a continuous "temperature" penalty has enough
signal to deserve a separate frozen validator later.
"""
from __future__ import annotations

import json
import math
import random
from pathlib import Path
from typing import Any, Callable

from probe_v28_target_coverage_conservative_fv_variants import (
    logit125_p60_skip_mid_loss_zone,
    raw_probability,
)


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
TARGET_JSON = OUT_DIR / "v28_target_coverage_fv_overlay_validator_latest.json"
OUT_JSON = OUT_DIR / "v28_target_coverage_boundary_temperature_fv_latest.json"
OUT_MD = OUT_DIR / "v28_target_coverage_boundary_temperature_fv_latest.md"

BOOTSTRAP_RUNS = 5000
BOOTSTRAP_SEED = 28691
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


def logloss(p: float, outcome: float) -> float:
    p = clamp_prob(p)
    return -(outcome * math.log(p) + (1.0 - outcome) * math.log(1.0 - p))


def shrink_to_half(p: float, amount: float) -> float:
    return clamp_prob(0.5 + (p - 0.5) * (1.0 - max(0.0, min(1.0, amount))))


def recross_heat(row: dict[str, Any]) -> float:
    recross = as_float(row.get("recross_hazard_score")) or 0.0
    abs_d = as_float(row.get("abs_d_sigma")) or 999.0
    edge = abs(as_float(row.get("raw_edge_prob")) or 0.0)
    near = max(0.0, min(1.0, (0.60 - abs_d) / 0.60))
    thin = max(0.0, min(1.0, (0.08 - edge) / 0.08))
    return max(0.0, min(1.0, recross * near * thin))


def conservative_probability(row: dict[str, Any]) -> float:
    return clamp_prob(float(logit125_p60_skip_mid_loss_zone(row)))


def boundary_temp_light(row: dict[str, Any]) -> float:
    p = conservative_probability(row)
    raw = clamp_prob(float(raw_probability(row)))
    if 0.60 <= raw < 0.75:
        return shrink_to_half(p, 0.20 * recross_heat(row))
    return p


def boundary_temp_medium(row: dict[str, Any]) -> float:
    p = conservative_probability(row)
    raw = clamp_prob(float(raw_probability(row)))
    if 0.60 <= raw < 0.75:
        return shrink_to_half(p, 0.35 * recross_heat(row))
    return p


def boundary_temp_strong(row: dict[str, Any]) -> float:
    p = conservative_probability(row)
    raw = clamp_prob(float(raw_probability(row)))
    if 0.60 <= raw < 0.75:
        return shrink_to_half(p, 0.50 * recross_heat(row))
    return p


def thin_recross_book_blend(row: dict[str, Any]) -> float:
    p = conservative_probability(row)
    raw = clamp_prob(float(raw_probability(row)))
    edge = as_float(row.get("raw_edge_prob"))
    recross = as_float(row.get("recross_hazard_score")) or 0.0
    ask = as_float(row.get("ask_prob"))
    if ask is not None and edge is not None and 0.60 <= raw < 0.75 and edge < 0.02 and recross >= 0.85:
        return clamp_prob(0.5 * p + 0.5 * ask)
    return p


VARIANTS: dict[str, Callable[[dict[str, Any]], float]] = {
    "raw_probability": raw_probability,
    "conservative_logit125_calm_mid_or_p75": conservative_probability,
    "boundary_temp_light": boundary_temp_light,
    "boundary_temp_medium": boundary_temp_medium,
    "boundary_temp_strong": boundary_temp_strong,
    "thin_recross_book_blend": thin_recross_book_blend,
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
        p_raw = clamp_prob(float(raw_probability(row)))
        p_variant = clamp_prob(float(fn(row)))
        outcome = 1.0 if row.get("side_won") is True else 0.0
        scored.append({
            "market": row.get("market"),
            "side": row.get("side"),
            "won": row.get("side_won"),
            "p_raw": p_raw,
            "p_variant": p_variant,
            "ask_prob": row.get("ask_prob"),
            "raw_edge_prob": row.get("raw_edge_prob"),
            "abs_d_sigma": row.get("abs_d_sigma"),
            "recross_hazard_score": row.get("recross_hazard_score"),
            "heat": recross_heat(row),
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
        "wins": sum(1 for row in scored if row.get("won") is True),
        "losses": sum(1 for row in scored if row.get("won") is False),
        "avg_p": sum(float(row["p_variant"]) for row in scored) / len(scored) if scored else None,
        "brier_mean_delta": sum(briers) / len(briers) if briers else None,
        "logloss_mean_delta": sum(losses) / len(losses) if losses else None,
        "brier_bootstrap": bboot,
        "logloss_bootstrap": lboot,
        "adjusted_rows": sum(1 for row in scored if abs(float(row["p_variant"]) - float(row["p_raw"])) > 1e-9),
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
        "entries": len(rows),
        "settled": sum(1 for row in rows if row.get("side_won") is not None),
        "forward_denominator": target.get("forward_denominator"),
        "best_variant": ranked[0].get("variant") if ranked else None,
        "ranked": ranked,
        "interpretation": interpretation(ranked),
    }


def interpretation(ranked: list[dict[str, Any]]) -> list[str]:
    best = next((row for row in ranked if row.get("variant") != "raw_probability"), {})
    return [
        f"Best boundary-temperature diagnostic is {best.get('variant')} with Brier/logloss mean deltas {best.get('brier_mean_delta')}/{best.get('logloss_mean_delta')}.",
        f"Its Brier/logloss p95 deltas are {(best.get('brier_bootstrap') or {}).get('p95')}/{(best.get('logloss_bootstrap') or {}).get('p95')}.",
        "Diagnostic only; freeze separately before using future rows as promotion evidence.",
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
        "# v28 Target-Coverage Boundary Temperature FV",
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
        "| rank | variant | rows | adjusted | W/L | avg p | brier mean | brier p95 | logloss mean | logloss p95 | blockers |",
        "|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---|",
    ])
    for idx, row in enumerate(report.get("ranked") or [], start=1):
        bboot = row.get("brier_bootstrap") or {}
        lboot = row.get("logloss_bootstrap") or {}
        lines.append(
            f"| {idx} | `{row.get('variant')}` | {row.get('rows')} | {row.get('adjusted_rows')} | "
            f"{row.get('wins')}/{row.get('losses')} | {fmt(row.get('avg_p'))} | "
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
