"""Frozen boundary/recross shrink FV challenger.

Research-only; no live bot changes or orders.

Physics hypothesis:
    A shallow-distance 15m BTC boundary state with high recross hazard is not a
    durable probability statement. In those rows, raw v28 confidence is treated
    as noisy and shrunk toward 50 instead of sharpened. This is a calibration
    candidate, not a live rule, until it earns forward rows.
"""
from __future__ import annotations

import json
import math
import random
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

from probe_v28_exchange_result_enrichment import attach_exchange_results
from probe_v28_frozen_forward_candidates import market_timing, parse_ts
from probe_v28_raw_entry_coverage_valve import selected_base_rows
from probe_v28_target_coverage_conservative_fv_variants import raw_probability
from probe_v28_target_coverage_fv_overlay_validator import (
    DEFAULT_POLICY,
    apply_policy,
    boundary_recross_shrink_probability,
)


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
STATE_JSON = OUT_DIR / "v28_frozen_boundary_recross_shrink_fv_state.json"
OUT_JSON = OUT_DIR / "v28_frozen_boundary_recross_shrink_fv_latest.json"
OUT_MD = OUT_DIR / "v28_frozen_boundary_recross_shrink_fv_latest.md"

MIN_SETTLED = 30
BOOTSTRAP_RUNS = 5000
BOOTSTRAP_SEED = 286117


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
        state = load_json(STATE_JSON)
        if state.get("freeze_ts_utc"):
            return state
    state = {
        "freeze_ts_utc": utc_now_iso(),
        "entry_policy": DEFAULT_POLICY,
        "variant": "boundary_recross_shrink_probability",
        "rule": "shrink raw probability halfway toward 50 when recross>=0.55 and abs_d<0.45, or raw_edge<3pp and recross>=0.40",
        "physics": "Near-boundary high-recross states are turbulent repeated-crossing regimes; confidence should lose memory rather than sharpen.",
    }
    STATE_JSON.write_text(json.dumps(state, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return state


def clamp_prob(value: float) -> float:
    return max(0.000001, min(0.999999, value))


def logloss(p: float, outcome: float) -> float:
    p = clamp_prob(p)
    return -(outcome * math.log(p) + (1.0 - outcome) * math.log(1.0 - p))


def percentile(sorted_values: list[float], q: float) -> float | None:
    if not sorted_values:
        return None
    idx = min(len(sorted_values) - 1, max(0, int(round((len(sorted_values) - 1) * q))))
    return sorted_values[idx]


def bootstrap(values: list[float], seed_offset: int = 0) -> dict[str, Any]:
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
            "ask_prob": row.get("ask_prob"),
            "raw_edge_prob": row.get("raw_edge_prob"),
            "abs_d_sigma": row.get("abs_d_sigma"),
            "recross_hazard_score": row.get("recross_hazard_score"),
            "net_cents": row.get("net_gross_cents_after_entry_fee"),
            "brier_delta": (p_var - outcome) ** 2 - (p_raw - outcome) ** 2,
            "logloss_delta": logloss(p_var, outcome) - logloss(p_raw, outcome),
        })
    briers = [float(row["brier_delta"]) for row in scored]
    losses = [float(row["logloss_delta"]) for row in scored]
    bboot = bootstrap(briers, 11)
    lboot = bootstrap(losses, 23)
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
    future_markets = timing["clean_forward_markets"]
    all_rows = apply_policy(selected_base_rows(), str(state.get("entry_policy") or DEFAULT_POLICY))
    future_rows = attach_exchange_results([row for row in all_rows if str(row.get("market") or "") in future_markets])
    ranked = [
        score_variant(future_rows, "raw_probability", raw_probability),
        score_variant(future_rows, str(state.get("variant")), boundary_recross_shrink_probability),
    ]
    ranked.sort(key=lambda row: (
        row.get("variant") == "raw_probability",
        float(row.get("brier_mean_delta") if row.get("brier_mean_delta") is not None else 999.0),
    ))
    return {
        "freeze": state,
        "future_denominator": len(future_markets),
        "entries": len(future_rows),
        "settled": sum(1 for row in future_rows if row.get("side_won") is not None),
        "coverage_pct": 100.0 * len(future_rows) / len(future_markets) if future_markets else None,
        "ranked": ranked,
        "best_variant": ranked[0].get("variant") if ranked else None,
        "interpretation": [
            f"Frozen boundary/recross shrink has {len(future_rows)} entries over {len(future_markets)} future markets.",
            "This starts from its own freeze timestamp and is not promotion evidence until it reaches forward sample size.",
        ],
    }


def fmt(value: Any) -> str:
    if value is None:
        return "None"
    if isinstance(value, float):
        return f"{value:.6f}"
    return str(value)


def write_md(report: dict[str, Any]) -> None:
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8")
    lines = [
        "# v28 Frozen Boundary/Recross Shrink FV",
        "",
        f"- Freeze timestamp UTC: `{(report.get('freeze') or {}).get('freeze_ts_utc')}`",
        f"- Entry policy: `{(report.get('freeze') or {}).get('entry_policy')}`",
        f"- Variant: `{(report.get('freeze') or {}).get('variant')}`",
        f"- Future entries/settled/denominator: `{report.get('entries')}/{report.get('settled')}/{report.get('future_denominator')}`",
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
    print(str(OUT_MD))


if __name__ == "__main__":
    main()
