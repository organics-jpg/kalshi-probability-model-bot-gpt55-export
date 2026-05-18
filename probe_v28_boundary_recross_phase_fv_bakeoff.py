"""Phase-aware boundary/recross FV bakeoff for target-coverage rows.

Research-only; no live bot changes or orders.

The current boundary/recross shrink improves calibration by reducing
overconfidence on losing rows, but it also pulls down several winning rows.
This report tests fixed physics variants that separate boundary turbulence
from valid directional acceleration. It is diagnostic only; any useful rule
must be frozen separately and earn future rows before promotion.
"""
from __future__ import annotations

import json
import math
import random
from pathlib import Path
from typing import Any, Callable

from probe_v28_target_coverage_fv_overlay_validator import (
    boundary_recross_shrink_probability,
    clamp_prob,
)


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
TARGET_JSON = OUT_DIR / "v28_target_coverage_fv_overlay_validator_latest.json"
OUT_JSON = OUT_DIR / "v28_boundary_recross_phase_fv_bakeoff_latest.json"
OUT_MD = OUT_DIR / "v28_boundary_recross_phase_fv_bakeoff_latest.md"

BOOTSTRAP_RUNS = 5000


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


def normalized(row: dict[str, Any]) -> dict[str, Any]:
    out = dict(row)
    if out.get("p_side") is None and out.get("p_raw") is not None:
        out["p_side"] = out.get("p_raw")
    return out


def raw_probability(row: dict[str, Any]) -> float:
    raw = as_float(row.get("p_side") if row.get("p_side") is not None else row.get("p_raw"))
    if raw is None:
        raise ValueError("missing raw probability")
    return clamp_prob(raw)


def shrink_half(raw: float) -> float:
    return clamp_prob(0.5 + 0.5 * (raw - 0.5))


def near_recross_shrink_only(row: dict[str, Any]) -> float:
    raw = raw_probability(row)
    recross = as_float(row.get("recross_hazard_score"))
    abs_d = as_float(row.get("abs_d_sigma"))
    if recross is not None and abs_d is not None and recross >= 0.55 and abs_d < 0.45:
        return shrink_half(raw)
    return raw


def edge_phase_shrink(row: dict[str, Any]) -> float:
    raw = raw_probability(row)
    edge = as_float(row.get("raw_edge_prob"))
    recross = as_float(row.get("recross_hazard_score"))
    abs_d = as_float(row.get("abs_d_sigma"))
    if edge is None or recross is None or abs_d is None:
        return raw
    shallow_turbulence = abs_d < 0.45 and recross >= 0.55 and edge < 0.08
    thin_deep_pressure = abs_d >= 0.45 and recross >= 0.40 and edge < 0.02
    if shallow_turbulence or thin_deep_pressure:
        return shrink_half(raw)
    return raw


def confidence_leak_shrink(row: dict[str, Any]) -> float:
    raw = raw_probability(row)
    edge = as_float(row.get("raw_edge_prob"))
    recross = as_float(row.get("recross_hazard_score"))
    abs_d = as_float(row.get("abs_d_sigma"))
    ask = as_float(row.get("ask_prob"))
    if edge is None or recross is None or abs_d is None:
        return raw
    near_boundary = abs_d < 0.45 and recross >= 0.55
    expensive_thin_touch = ask is not None and ask >= 0.70 and edge < 0.03 and recross >= 0.35
    if near_boundary or expensive_thin_touch:
        leak = 0.35 if raw >= 0.75 else 0.50
        return clamp_prob(0.5 + leak * (raw - 0.5))
    return raw


VARIANTS: dict[str, Callable[[dict[str, Any]], float]] = {
    "raw_probability": raw_probability,
    "boundary_recross_shrink_probability": boundary_recross_shrink_probability,
    "near_recross_shrink_only": near_recross_shrink_only,
    "edge_phase_shrink": edge_phase_shrink,
    "confidence_leak_shrink": confidence_leak_shrink,
}

VARIANT_NOTES = {
    "raw_probability": "Control: no adjustment to v28 FV.",
    "boundary_recross_shrink_probability": "Current candidate: shrink shallow high-recross rows and thin turbulent touches.",
    "near_recross_shrink_only": "Only boundary turbulence forgets; thin away-from-boundary touches keep raw confidence.",
    "edge_phase_shrink": "Shrink shallow turbulence only when edge is not wide, plus very thin deep-pressure touches.",
    "confidence_leak_shrink": "Shrink boundary turbulence, with stronger leak on expensive thin high-confidence touches.",
}


def logloss(p: float, outcome: float) -> float:
    p = clamp_prob(p)
    return -(outcome * math.log(p) + (1.0 - outcome) * math.log(1.0 - p))


def score_rows(rows: list[dict[str, Any]], name: str, fn: Callable[[dict[str, Any]], float]) -> dict[str, Any]:
    scored: list[dict[str, Any]] = []
    for row0 in rows:
        if row0.get("side_won") is None:
            continue
        row = normalized(row0)
        try:
            p = clamp_prob(float(fn(row)))
            raw_p = raw_probability(row)
        except (KeyError, TypeError, ValueError):
            continue
        outcome = 1.0 if row.get("side_won") is True else 0.0
        scored.append({
            **row0,
            "p": p,
            "raw_p": raw_p,
            "outcome": outcome,
            "adjusted": abs(p - raw_p) > 1e-12,
            "brier": (p - outcome) ** 2,
            "raw_brier": (raw_p - outcome) ** 2,
            "logloss": logloss(p, outcome),
            "raw_logloss": logloss(raw_p, outcome),
            "net_cents": row.get("net_gross_cents_after_entry_fee"),
        })
    return summarize(name, scored)


def summarize(name: str, scored: list[dict[str, Any]]) -> dict[str, Any]:
    brier_deltas = [float(row["brier"]) - float(row["raw_brier"]) for row in scored]
    logloss_deltas = [float(row["logloss"]) - float(row["raw_logloss"]) for row in scored]
    net = sum(float(row.get("net_cents") or 0.0) for row in scored)
    wins = sum(1 for row in scored if row.get("side_won") is True)
    return {
        "variant": name,
        "note": VARIANT_NOTES.get(name),
        "rows": len(scored),
        "wins": wins,
        "losses": len(scored) - wins,
        "adjusted_rows": sum(1 for row in scored if row.get("adjusted")),
        "net_cents": net,
        "avg_p": avg([float(row["p"]) for row in scored]),
        "win_rate": wins / len(scored) if scored else None,
        "brier_mean": avg([float(row["brier"]) for row in scored]),
        "logloss_mean": avg([float(row["logloss"]) for row in scored]),
        "brier_mean_delta": avg(brier_deltas),
        "logloss_mean_delta": avg(logloss_deltas),
        "brier_bootstrap": bootstrap_mean_delta(brier_deltas),
        "logloss_bootstrap": bootstrap_mean_delta(logloss_deltas),
        "rows_detail": detail(scored),
    }


def avg(values: list[float]) -> float | None:
    return sum(values) / len(values) if values else None


def bootstrap_mean_delta(values: list[float]) -> dict[str, Any]:
    if not values:
        return {"runs": 0, "p05": None, "p50": None, "p95": None, "prob_negative": None}
    rng = random.Random(20260506)
    means = []
    for _ in range(BOOTSTRAP_RUNS):
        sample = [values[rng.randrange(len(values))] for _ in values]
        means.append(sum(sample) / len(sample))
    means.sort()
    return {
        "runs": BOOTSTRAP_RUNS,
        "p05": percentile(means, 0.05),
        "p50": percentile(means, 0.50),
        "p95": percentile(means, 0.95),
        "prob_negative": sum(1 for value in means if value < 0.0) / len(means),
    }


def percentile(values: list[float], q: float) -> float:
    idx = min(len(values) - 1, max(0, int(round(q * (len(values) - 1)))))
    return values[idx]


def detail(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    out = []
    for row in rows:
        out.append({
            "market": row.get("market"),
            "side": row.get("side"),
            "side_won": row.get("side_won"),
            "net_cents": row.get("net_cents"),
            "raw_p": row.get("raw_p"),
            "p": row.get("p"),
            "adjusted": row.get("adjusted"),
            "ask_prob": row.get("ask_prob"),
            "raw_edge_prob": row.get("raw_edge_prob"),
            "abs_d_sigma": row.get("abs_d_sigma"),
            "recross_hazard_score": row.get("recross_hazard_score"),
            "coverage_valve_reason": row.get("coverage_valve_reason"),
        })
    return out


def build_report() -> dict[str, Any]:
    target = load_json(TARGET_JSON)
    rows = target.get("forward_rows") if isinstance(target.get("forward_rows"), list) else []
    ranked = [score_rows(rows, name, fn) for name, fn in VARIANTS.items()]
    ranked.sort(key=lambda row: (
        float(row.get("brier_mean_delta") if row.get("brier_mean_delta") is not None else 999.0),
        float(row.get("logloss_mean_delta") if row.get("logloss_mean_delta") is not None else 999.0),
    ))
    return {
        "source_artifact": str(TARGET_JSON),
        "policy": target.get("policy"),
        "target_freeze_ts": target.get("freeze_ts"),
        "forward_denominator": target.get("forward_denominator"),
        "forward_entries": len(rows),
        "settled_rows": sum(1 for row in rows if row.get("side_won") is not None),
        "ranked": ranked,
        "requirements": [
            "diagnostic only; not promotion evidence",
            "same target-coverage rows for every variant",
            "raw control included",
            "future freeze required before any live consideration",
        ],
        "interpretation": interpretation(ranked),
    }


def interpretation(ranked: list[dict[str, Any]]) -> list[str]:
    best = ranked[0] if ranked else {}
    current = next((row for row in ranked if row.get("variant") == "boundary_recross_shrink_probability"), {})
    notes = []
    if best:
        notes.append(
            f"Best diagnostic variant by Brier delta is {best.get('variant')} with {best.get('rows')} rows and Brier/logloss deltas {best.get('brier_mean_delta')}/{best.get('logloss_mean_delta')}."
        )
    if current and best and current.get("variant") != best.get("variant"):
        notes.append(
            f"The current shrink is not the diagnostic winner on this refreshed slice; treat this only as a hypothesis until frozen forward rows exist."
        )
    if best and ((best.get("brier_bootstrap") or {}).get("p95") or 1.0) >= 0.0:
        notes.append("The best diagnostic variant still does not have a strictly negative bootstrap p95; sample risk remains unresolved.")
    return notes


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
        "# v28 Boundary/Recross Phase FV Bakeoff",
        "",
        "Diagnostic-only bakeoff on the fixed target-coverage forward rows.",
        "",
        f"- Policy: `{report.get('policy')}`",
        f"- Target freeze timestamp UTC: `{report.get('target_freeze_ts')}`",
        f"- Forward entries/settled/denominator: `{report.get('forward_entries')}/{report.get('settled_rows')}/{report.get('forward_denominator')}`",
        "",
        "## Interpretation",
        "",
    ]
    for note in report.get("interpretation") or []:
        lines.append(f"- {note}")
    lines.extend([
        "",
        "## Ranking",
        "",
        "| rank | variant | rows | adjusted | W/L | net c | brier d | brier p95 | logloss d | logloss p95 | avg p | win rate | note |",
        "|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|",
    ])
    for idx, row in enumerate(report.get("ranked") or [], start=1):
        b_boot = row.get("brier_bootstrap") or {}
        l_boot = row.get("logloss_bootstrap") or {}
        lines.append(
            f"| {idx} | {row.get('variant')} | {row.get('rows')} | {row.get('adjusted_rows')} | "
            f"{row.get('wins')}/{row.get('losses')} | {fmt(row.get('net_cents'))} | "
            f"{fmt(row.get('brier_mean_delta'))} | {fmt(b_boot.get('p95'))} | "
            f"{fmt(row.get('logloss_mean_delta'))} | {fmt(l_boot.get('p95'))} | "
            f"{fmt(row.get('avg_p'))} | {fmt(row.get('win_rate'))} | {row.get('note')} |"
        )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    report = build_report()
    write_md(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
