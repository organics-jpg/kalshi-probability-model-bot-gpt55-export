"""Pending sensitivity for frozen p70 FV validators.

Research-only; no live bot changes or orders.

The frozen p70 reports can show losses that were not actually adjusted by p70.
This probe separates settled raw-only rows from pending p70-adjustable rows so
the evidence stream is easier to interpret while markets are unresolved.
"""
from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any, Callable

from probe_v28_frozen_forward_candidates import market_timing, parse_ts
from probe_v28_frozen_target_coverage_p70_fv import STATE_JSON as HARD_STATE_JSON
from probe_v28_frozen_target_coverage_p70_empirical_bayes import (
    FULL_SCALE,
    PRIOR_COUNT,
    STATE_JSON as EB_STATE_JSON,
    evidence_scale,
    p70_empirical_bayes_probability,
)
from probe_v28_raw_entry_coverage_valve import selected_base_rows
from probe_v28_target_coverage_conservative_fv_variants import raw_probability, sharpen
from probe_v28_target_coverage_fv_overlay_validator import DEFAULT_POLICY, apply_policy


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
OUT_JSON = OUT_DIR / "v28_frozen_target_coverage_p70_pending_sensitivity_latest.json"
OUT_MD = OUT_DIR / "v28_frozen_target_coverage_p70_pending_sensitivity_latest.md"


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


def hard_p70_probability(row: dict[str, Any]) -> float:
    p = clamp_prob(float(raw_probability(row)))
    return sharpen(p) if p >= 0.70 else p


def logloss(p: float, outcome: float) -> float:
    p = clamp_prob(p)
    return -(outcome * math.log(p) + (1.0 - outcome) * math.log(1.0 - p))


def score_row(row: dict[str, Any], probability_fn: Callable[[dict[str, Any]], float]) -> dict[str, Any]:
    p_raw = clamp_prob(float(raw_probability(row)))
    p_variant = clamp_prob(float(probability_fn(row)))
    out = {
        "market": row.get("market"),
        "side": row.get("side"),
        "source": row.get("source"),
        "p_raw": p_raw,
        "p_variant": p_variant,
        "adjusted": abs(p_variant - p_raw) > 1e-9,
        "ask_prob": row.get("ask_prob"),
        "raw_edge_prob": row.get("raw_edge_prob"),
        "abs_d_sigma": row.get("abs_d_sigma"),
        "recross_hazard_score": row.get("recross_hazard_score"),
        "seconds_to_close": row.get("seconds_to_close"),
        "side_won": row.get("side_won"),
        "net_cents": row.get("net_gross_cents_after_entry_fee"),
    }
    if row.get("side_won") is not None:
        outcome = 1.0 if row.get("side_won") is True else 0.0
        out.update({
            "brier_delta": (p_variant - outcome) ** 2 - (p_raw - outcome) ** 2,
            "logloss_delta": logloss(p_variant, outcome) - logloss(p_raw, outcome),
        })
    else:
        out.update({"brier_delta": None, "logloss_delta": None})
    return out


def selected_forward_rows(state: dict[str, Any]) -> tuple[list[dict[str, Any]], int]:
    freeze_ts = state.get("freeze_ts_utc")
    if not freeze_ts:
        return [], 0
    timing = market_timing(parse_ts(freeze_ts))
    forward_markets = timing["clean_forward_markets"]
    rows = apply_policy(selected_base_rows(), str(state.get("entry_policy") or DEFAULT_POLICY))
    return [row for row in rows if str(row.get("market") or "") in forward_markets], len(forward_markets)


def summarize_rows(rows: list[dict[str, Any]]) -> dict[str, Any]:
    pending = [row for row in rows if row.get("side_won") is None]
    settled = [row for row in rows if row.get("side_won") is not None]
    adjusted = [row for row in rows if row.get("adjusted")]
    pending_adjusted = [row for row in pending if row.get("adjusted")]
    settled_adjusted = [row for row in settled if row.get("adjusted")]
    return {
        "rows": len(rows),
        "pending": len(pending),
        "settled": len(settled),
        "adjusted": len(adjusted),
        "pending_adjusted": len(pending_adjusted),
        "settled_adjusted": len(settled_adjusted),
        "settled_adjusted_wins": sum(1 for row in settled_adjusted if row.get("side_won") is True),
        "settled_adjusted_losses": sum(1 for row in settled_adjusted if row.get("side_won") is False),
        "settled_raw_only_losses": sum(1 for row in settled if not row.get("adjusted") and row.get("side_won") is False),
        "pending_adjusted_rows": pending_adjusted,
        "settled_rows": settled,
    }


def build_validator(name: str, state_path: Path, probability_fn_factory: Callable[[list[dict[str, Any]], dict[str, Any]], Callable[[dict[str, Any]], float]]) -> dict[str, Any]:
    state = load_json(state_path)
    raw_rows, denominator = selected_forward_rows(state)
    probability_fn = probability_fn_factory(raw_rows, state)
    rows = [score_row(row, probability_fn) for row in raw_rows]
    return {
        "validator": name,
        "freeze": state,
        "future_denominator": denominator,
        "entries": len(rows),
        "coverage_pct": 100.0 * len(rows) / denominator if denominator else None,
        "summary": summarize_rows(rows),
        "rows": rows,
    }


def hard_factory(_rows: list[dict[str, Any]], _state: dict[str, Any]) -> Callable[[dict[str, Any]], float]:
    return hard_p70_probability


def eb_factory(rows: list[dict[str, Any]], state: dict[str, Any]) -> Callable[[dict[str, Any]], float]:
    adjusted_count = sum(1 for row in rows if clamp_prob(float(raw_probability(row))) >= 0.70)
    scale = evidence_scale(adjusted_count, int(state.get("prior_count") or PRIOR_COUNT), float(state.get("full_scale") or FULL_SCALE))
    return lambda row: p70_empirical_bayes_probability(row, scale)


def build_report() -> dict[str, Any]:
    validators = [
        build_validator("hard_p70", HARD_STATE_JSON, hard_factory),
        build_validator("empirical_bayes_p70", EB_STATE_JSON, eb_factory),
    ]
    return {
        "validators": validators,
        "interpretation": interpretation(validators),
    }


def interpretation(validators: list[dict[str, Any]]) -> list[str]:
    notes = []
    for validator in validators:
        summary = validator.get("summary") or {}
        notes.append(
            f"{validator.get('validator')}: entries {validator.get('entries')}/{validator.get('future_denominator')}, pending adjusted {summary.get('pending_adjusted')}, settled adjusted {summary.get('settled_adjusted')}."
        )
        if summary.get("settled_raw_only_losses"):
            notes.append(
                f"{validator.get('validator')}: {summary.get('settled_raw_only_losses')} settled losses were raw-only, so they are entry-surface evidence, not p70 FV evidence."
            )
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
        "# v28 Frozen Target-Coverage p70 Pending Sensitivity",
        "",
        "## Current Read",
        "",
    ]
    for note in report.get("interpretation") or []:
        lines.append(f"- {note}")
    for validator in report.get("validators") or []:
        summary = validator.get("summary") or {}
        lines.extend([
            "",
            f"## {validator.get('validator')}",
            "",
            f"- Freeze timestamp UTC: `{(validator.get('freeze') or {}).get('freeze_ts_utc')}`",
            f"- Entries/denominator/coverage: `{validator.get('entries')}/{validator.get('future_denominator')}/{fmt(validator.get('coverage_pct'))}`",
            f"- Rows/pending/settled/adjusted: `{summary.get('rows')}/{summary.get('pending')}/{summary.get('settled')}/{summary.get('adjusted')}`",
            f"- Pending adjusted / settled adjusted: `{summary.get('pending_adjusted')}/{summary.get('settled_adjusted')}`",
            "",
            "| market | side | p raw | p variant | adjusted | ask | edge | abs d | recross | stc | won | net c | brier d | logloss d |",
            "|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---|---:|---:|---:|",
        ])
        for row in validator.get("rows") or []:
            lines.append(
                f"| {row.get('market')} | {row.get('side')} | {fmt(row.get('p_raw'))} | {fmt(row.get('p_variant'))} | "
                f"{row.get('adjusted')} | {fmt(row.get('ask_prob'))} | {fmt(row.get('raw_edge_prob'))} | "
                f"{fmt(row.get('abs_d_sigma'))} | {fmt(row.get('recross_hazard_score'))} | {fmt(row.get('seconds_to_close'))} | "
                f"{row.get('side_won')} | {fmt(row.get('net_cents'))} | {fmt(row.get('brier_delta'))} | {fmt(row.get('logloss_delta'))} |"
            )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    report = build_report()
    write_md(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
