"""False-conviction FV-to-entry bridge for v28 target coverage.

Research-only; no live bot changes or orders.

Question:
    The leading entry repair says early boundary/high-recross rows can be
    false conviction. This probe tests whether that same physical idea can live
    inside the FV engine itself: shrink the side probability before selecting
    the first eligible row, then score the resulting entry surface.

Anti-overfit posture:
    Variants are fixed by geometry, not chosen from a wide parameter search.
    The report shows both an existing frozen-window diagnostic and a separate
    post-freeze window that must earn its own future rows.
"""
from __future__ import annotations

import json
import math
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

from probe_v28_exchange_result_enrichment import attach_exchange_results
from probe_v28_frozen_forward_candidates import market_timing, parse_ts
from probe_v28_noise_floor_shrinkage_candidates import ask_prob, estimate_entry_fee_cents
from probe_v28_raw_entry_coverage_valve import MIN_P_KEEP
from probe_v28_rmt_regime_diagnostic import attach_regime_rows
from probe_v28_shadow_entry_policy_bakeoff import base_tradeable, observation_pool
from probe_v28_state_aware_fv_candidates import enrich_state, p_raw


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
STATE_JSON = OUT_DIR / "v28_false_conviction_fv_entry_bridge_state.json"
OUT_JSON = OUT_DIR / "v28_false_conviction_fv_entry_bridge_latest.json"
OUT_MD = OUT_DIR / "v28_false_conviction_fv_entry_bridge_latest.md"

REFERENCE_FREEZE_JSON = OUT_DIR / "v28_frozen_early_no_boundary_decay_repair_entry_state.json"

MIN_SETTLED = 30
COVERAGE_MIN = 75.0
COVERAGE_MAX = 90.0
EDGE_KEEP = 0.04
RECROSS_FLOOR = 0.75
NEAR_ABS_D = 0.25
PHI = (1.0 + math.sqrt(5.0)) / 2.0
PHI_INV = 1.0 / PHI
PHI_INV2 = PHI_INV * PHI_INV


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
        "candidate": "false_conviction_fv_entry_bridge",
        "entry_surface": "first adjusted-p50 edge0 row, then target turbulence valve on adjusted FV",
        "target_policy": f"p>=0.50 edge>=0; keep if p>=0.60 or edge>={EDGE_KEEP:.2f}; skip weak near recross {RECROSS_FLOOR}/{NEAR_ABS_D}",
        "physics": (
            "Early unresolved boundary states should reduce conviction before entry selection. "
            "The FV should forget stale/local certainty when recross geometry says the path has not escaped."
        ),
    }
    STATE_JSON.write_text(json.dumps(state, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return state


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


def seconds_to_close(row: dict[str, Any]) -> float | None:
    for key in ("seconds_to_close", "stc", "seconds_to_expiry"):
        value = as_float(row.get(key))
        if value is not None:
            return value
    return None


def recross(row: dict[str, Any]) -> float | None:
    return as_float(row.get("recross_hazard_score"))


def abs_d(row: dict[str, Any]) -> float | None:
    return as_float(row.get("abs_d_sigma"))


def raw_edge(row: dict[str, Any]) -> float | None:
    ask = ask_prob(row)
    if ask is None:
        return None
    return p_raw(row) - ask


def adjusted_edge(row: dict[str, Any], p_eff: float) -> float | None:
    ask = ask_prob(row)
    return None if ask is None else p_eff - ask


def early_no_boundary_decay(row: dict[str, Any]) -> bool:
    stc = seconds_to_close(row)
    hazard = recross(row)
    distance = abs_d(row)
    p = p_raw(row)
    return (
        str(row.get("side") or "").lower() == "no"
        and stc is not None
        and hazard is not None
        and distance is not None
        and stc >= 720.0
        and p < 0.70
        and distance <= 0.45
        and hazard >= 0.55
    )


def cheap_boundary_turbulence(row: dict[str, Any]) -> bool:
    ask = ask_prob(row)
    hazard = recross(row)
    distance = abs_d(row)
    p = p_raw(row)
    return (
        ask is not None
        and hazard is not None
        and distance is not None
        and ask < 0.55
        and p < 0.62
        and distance <= 0.25
        and hazard >= 0.75
    )


def false_conviction_zone(row: dict[str, Any]) -> bool:
    return early_no_boundary_decay(row) or cheap_boundary_turbulence(row)


def p_raw_probability(row: dict[str, Any]) -> float:
    return clamp_prob(p_raw(row))


def p_false_to_book(row: dict[str, Any]) -> float:
    raw = p_raw_probability(row)
    ask = ask_prob(row)
    if ask is None or not false_conviction_zone(row):
        return raw
    # Treat the book as a hard humility anchor only in the predeclared danger zone.
    return clamp_prob(min(raw, ask))


def p_false_half_to_50(row: dict[str, Any]) -> float:
    raw = p_raw_probability(row)
    if not false_conviction_zone(row):
        return raw
    return clamp_prob(0.5 + 0.5 * (raw - 0.5))


def p_continuous_recross_forget(row: dict[str, Any]) -> float:
    raw = p_raw_probability(row)
    hazard = recross(row)
    distance = abs_d(row)
    stc = seconds_to_close(row)
    if hazard is None or distance is None or stc is None:
        return raw
    near = max(0.0, min(1.0, (0.75 - distance) / 0.75))
    clock = max(0.0, min(1.0, stc / 900.0))
    side_mult = 1.15 if str(row.get("side") or "").lower() == "no" else 0.85
    forget = max(0.0, min(0.70, hazard * near * clock * side_mult))
    reliability = 1.0 - forget
    return clamp_prob(0.5 + reliability * (raw - 0.5))


def p_phi_activity_memory_forget(row: dict[str, Any]) -> float:
    raw = p_raw_probability(row)
    hazard = recross(row) or 0.0
    distance = abs_d(row)
    stc = seconds_to_close(row) or 0.0
    sigma = as_float(row.get("sigma_t_dollars")) or 0.0
    top_over = as_float(row.get("top_over_mp_edge"))
    outlier_share = as_float(row.get("outlier_share"))
    market_idx = int(as_float(row.get("market_observation_index")) or 0)
    side_idx = int(as_float(row.get("market_side_observation_index")) or 0)

    near = 1.0 if distance is None else max(0.0, min(1.0, (0.85 - distance) / 0.85))
    clock = max(0.0, min(1.0, stc / 900.0))
    sigma_pressure = max(0.0, min(1.0, sigma / 220.0))
    spectral_pressure = 0.0
    if top_over is not None:
        spectral_pressure = max(spectral_pressure, max(0.0, min(1.0, (top_over - 1.0) / 2.0)))
    if outlier_share is not None:
        spectral_pressure = max(spectral_pressure, max(0.0, min(1.0, outlier_share)))
    repetition_pressure = max(0.0, min(1.0, (market_idx + side_idx) / 6.0))
    side_mult = 1.10 if str(row.get("side") or "").lower() == "no" else 0.90

    # Fixed phi-compressible weights: strongest memory is path recross, then
    # volatility, spectral noise, and stale repeated observation. No fitted decimals.
    raw_forget = (
        PHI_INV * hazard * near * clock * side_mult
        + PHI_INV2 * sigma_pressure * near
        + PHI_INV2 * spectral_pressure
        + (PHI_INV2 * PHI_INV) * repetition_pressure
    )
    forget = max(0.0, min(0.72, raw_forget))
    return clamp_prob(0.5 + (1.0 - forget) * (raw - 0.5))


def p_phi_boundary_only_forget(row: dict[str, Any]) -> float:
    raw = p_raw_probability(row)
    hazard = recross(row) or 0.0
    distance = abs_d(row)
    stc = seconds_to_close(row) or 0.0
    near = 1.0 if distance is None else max(0.0, min(1.0, (0.85 - distance) / 0.85))
    clock = max(0.0, min(1.0, stc / 900.0))
    side_mult = 1.10 if str(row.get("side") or "").lower() == "no" else 0.90
    forget = max(0.0, min(0.72, PHI_INV * hazard * near * clock * side_mult))
    return clamp_prob(0.5 + (1.0 - forget) * (raw - 0.5))


VARIANTS: dict[str, Callable[[dict[str, Any]], float]] = {
    "raw_probability": p_raw_probability,
    "false_zone_to_book": p_false_to_book,
    "false_zone_half_to_50": p_false_half_to_50,
    "continuous_recross_forget": p_continuous_recross_forget,
    "phi_boundary_forget": p_phi_boundary_only_forget,
    "phi_activity_memory_forget": p_phi_activity_memory_forget,
}


def passes_adjusted_target_policy(row: dict[str, Any], p_eff: float, selector: str) -> tuple[bool, str]:
    edge = adjusted_edge(row, p_eff)
    if edge is None:
        return False, "missing_ask"
    if p_eff < 0.50 or edge < 0.0:
        return False, "below_p50_or_negative_edge"
    distance = abs_d(row) if abs_d(row) is not None else 999.0
    if selector == "escape_edge8_or_p70_or_far_edge4":
        if p_eff >= 0.70:
            return True, "keep_p_ge_70"
        if edge >= 0.08:
            return True, "keep_edge_ge_8pp"
        if distance >= 0.75 and edge >= EDGE_KEEP:
            return True, "keep_far_edge_ge_4pp"
        return False, "skip_unescaped_weak_edge"
    if selector == "escape_edge6_or_p65_or_far_edge4":
        if p_eff >= 0.65:
            return True, "keep_p_ge_65"
        if edge >= 0.06:
            return True, "keep_edge_ge_6pp"
        if distance >= 0.75 and edge >= EDGE_KEEP:
            return True, "keep_far_edge_ge_4pp"
        return False, "skip_unescaped_weak_edge"
    if p_eff >= MIN_P_KEEP:
        return True, "keep_p_ge_60"
    if edge >= EDGE_KEEP:
        return True, "keep_edge_ge_4pp"
    if selector == "strict_edge4_or_p60":
        return False, "skip_below_edge4_and_p60"
    hazard = recross(row) or 0.0
    if hazard >= RECROSS_FLOOR and distance <= NEAR_ABS_D:
        return False, "skip_weak_thin_recross_boundary"
    return True, "keep_not_turbulent"


def select_entries(
    rows: list[dict[str, Any]],
    selector: str,
    variant: str,
    fn: Callable[[dict[str, Any]], float],
    scope: str,
) -> list[dict[str, Any]]:
    picked: dict[str, dict[str, Any]] = {}
    decided: set[str] = set()
    for row in sorted(rows, key=lambda item: str(item.get("ts_wall") or "")):
        if not base_tradeable(row):
            continue
        market = str(row.get("market") or "")
        if not market or market in picked or market in decided:
            continue
        if scope == "first_tradeable_decision":
            decided.add(market)
        try:
            p_eff = fn(row)
        except (TypeError, ValueError, KeyError):
            continue
        ok, reason = passes_adjusted_target_policy(row, p_eff, selector)
        if not ok:
            continue
        edge = adjusted_edge(row, p_eff)
        picked[market] = {
            **row,
            "scope": scope,
            "selector": selector,
            "fv_variant": variant,
            "p_eff": p_eff,
            "raw_p_eff": p_raw_probability(row),
            "eff_edge_prob": edge,
            "raw_edge_prob": raw_edge(row),
            "false_conviction_zone": false_conviction_zone(row),
            "early_no_boundary_decay": early_no_boundary_decay(row),
            "cheap_boundary_turbulence": cheap_boundary_turbulence(row),
            "adjusted_target_reason": reason,
            "net_gross_cents_after_entry_fee": None if row.get("gross_cents") is None else float(row.get("gross_cents") or 0.0) - estimate_entry_fee_cents(row),
        }
    return [picked[key] for key in sorted(picked)]


def escape_energy(row: dict[str, Any]) -> float:
    p_eff = as_float(row.get("p_eff")) or 0.5
    edge = as_float(row.get("eff_edge_prob")) or 0.0
    distance = as_float(row.get("abs_d_sigma")) or 0.0
    hazard = as_float(row.get("recross_hazard_score")) or 0.0
    stc = seconds_to_close(row) or 0.0
    clock_risk = max(0.0, min(1.0, stc / 900.0))
    return (p_eff - 0.5) + edge + 0.08 * min(distance, 1.25) - 0.08 * hazard * clock_risk


def thin_by_escape_energy(rows: list[dict[str, Any]], denominator: int, target_coverage: float) -> list[dict[str, Any]]:
    if not rows or denominator <= 0:
        return rows
    keep_count = max(0, min(len(rows), int(math.ceil(denominator * target_coverage))))
    ranked = sorted(
        rows,
        key=lambda row: (
            -escape_energy(row),
            str(row.get("ts_wall") or ""),
            str(row.get("market") or ""),
        ),
    )
    kept_markets = {str(row.get("market") or "") for row in ranked[:keep_count]}
    return [{**row, "escape_energy": escape_energy(row)} for row in rows if str(row.get("market") or "") in kept_markets]


def summarize(rows: list[dict[str, Any]], denominator: int) -> dict[str, Any]:
    settled = [row for row in rows if row.get("side_won") is not None]
    outcomes = [1.0 if row.get("side_won") is True else 0.0 for row in settled]
    probs = [float(row.get("p_eff")) for row in settled if row.get("p_eff") is not None]
    briers = [(p - y) ** 2 for p, y in zip(probs, outcomes)]
    losses = [logloss(p, y) for p, y in zip(probs, outcomes)]
    net = sum(float(row.get("net_gross_cents_after_entry_fee") or 0.0) for row in settled)
    return {
        "entries": len(rows),
        "settled": len(settled),
        "wins": sum(1 for row in settled if row.get("side_won") is True),
        "losses": sum(1 for row in settled if row.get("side_won") is False),
        "coverage_pct": 100.0 * len(rows) / denominator if denominator else None,
        "net_cents": net,
        "avg_net_cents": net / len(settled) if settled else None,
        "avg_brier": sum(briers) / len(briers) if briers else None,
        "avg_logloss": sum(losses) / len(losses) if losses else None,
        "avg_p": sum(probs) / len(probs) if probs else None,
        "win_rate": sum(outcomes) / len(outcomes) if outcomes else None,
        "false_conviction_entries": sum(1 for row in rows if row.get("false_conviction_zone")),
        "approved_entry_count": sum(1 for row in rows if row.get("source") == "approved_entry"),
        "reconstructed_count": sum(1 for row in rows if row.get("source") != "approved_entry"),
    }


def blockers(summary: dict[str, Any], raw_summary: dict[str, Any]) -> list[str]:
    out: list[str] = []
    coverage = as_float(summary.get("coverage_pct"))
    settled = int(as_float(summary.get("settled")) or 0)
    net = as_float(summary.get("net_cents")) or 0.0
    brier = as_float(summary.get("avg_brier"))
    raw_brier = as_float(raw_summary.get("avg_brier"))
    loss = as_float(summary.get("avg_logloss"))
    raw_loss = as_float(raw_summary.get("avg_logloss"))
    if settled < MIN_SETTLED:
        out.append("settled_lt_30")
    if coverage is None or coverage < COVERAGE_MIN:
        out.append("coverage_too_low")
    if coverage is not None and coverage > COVERAGE_MAX:
        out.append("coverage_too_high")
    if net <= 0.0:
        out.append("net_not_positive")
    if brier is None or raw_brier is None or brier >= raw_brier:
        out.append("brier_not_better_than_raw")
    if loss is None or raw_loss is None or loss >= raw_loss:
        out.append("logloss_not_better_than_raw")
    return out


def row_view(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "market": row.get("market"),
        "ts_wall": row.get("ts_wall"),
        "source": row.get("source"),
        "side": row.get("side"),
        "side_won": row.get("side_won"),
        "p_eff": row.get("p_eff"),
        "raw_p_eff": row.get("raw_p_eff"),
        "ask_prob": row.get("ask_prob"),
        "eff_edge_prob": row.get("eff_edge_prob"),
        "raw_edge_prob": row.get("raw_edge_prob"),
        "seconds_to_close": seconds_to_close(row),
        "abs_d_sigma": row.get("abs_d_sigma"),
        "recross_hazard_score": row.get("recross_hazard_score"),
        "false_conviction_zone": row.get("false_conviction_zone"),
        "reason": row.get("adjusted_target_reason"),
        "net_cents": row.get("net_gross_cents_after_entry_fee"),
    }


def score_window(name: str, freeze_ts: str) -> dict[str, Any]:
    timing = market_timing(parse_ts(freeze_ts))
    future_markets = set(timing["clean_forward_markets"])
    rows = enrich_state(attach_regime_rows(observation_pool()))
    rows = attach_exchange_results([row for row in rows if str(row.get("market") or "") in future_markets])
    denominator = len(future_markets)
    scored = []
    raw_summary: dict[str, Any] = {}
    details: dict[str, list[dict[str, Any]]] = {}
    selector_names = [
        "strict_edge4_or_p60",
        "escape_edge6_or_p65_or_far_edge4",
        "escape_edge8_or_p70_or_far_edge4",
        "target_weak_turbulence_skip",
    ]
    scope_names = [
        "first_eligible",
        "first_eligible_top80_escape_energy",
        "first_eligible_top75_escape_energy",
        "first_tradeable_decision",
    ]
    for scope in scope_names:
      for selector in selector_names:
       for variant, fn in VARIANTS.items():
        base_scope = "first_eligible" if scope.startswith("first_eligible_top") else scope
        selected = select_entries(rows, selector, variant, fn, base_scope)
        if scope == "first_eligible_top80_escape_energy":
            selected = thin_by_escape_energy(selected, denominator, 0.80)
        elif scope == "first_eligible_top75_escape_energy":
            selected = thin_by_escape_energy(selected, denominator, 0.75)
        summary = {"scope": scope, "selector": selector, **summarize(selected, denominator)}
        score_name = f"{scope}+{selector}+{variant}"
        if scope == "first_eligible" and selector == "strict_edge4_or_p60" and variant == "raw_probability":
            raw_summary = summary
        details[score_name] = [row_view(row) for row in selected[:80]]
        scored.append({"variant": variant, "score_name": score_name, **summary})
    enriched = []
    for row in scored:
        brier = as_float(row.get("avg_brier"))
        raw_brier = as_float(raw_summary.get("avg_brier"))
        loss = as_float(row.get("avg_logloss"))
        raw_loss = as_float(raw_summary.get("avg_logloss"))
        net = as_float(row.get("net_cents"))
        raw_net = as_float(raw_summary.get("net_cents"))
        enriched_row = {
            **row,
            "delta_net_vs_raw": None if net is None or raw_net is None else net - raw_net,
            "brier_delta_vs_raw": None if brier is None or raw_brier is None else brier - raw_brier,
            "logloss_delta_vs_raw": None if loss is None or raw_loss is None else loss - raw_loss,
        }
        enriched_row["blockers"] = [] if row.get("score_name") == "first_eligible+strict_edge4_or_p60+raw_probability" else blockers(enriched_row, raw_summary)
        enriched.append(enriched_row)
    enriched.sort(key=lambda row: (
        bool(row.get("blockers")),
        -(as_float(row.get("net_cents")) or -999999.0),
        as_float(row.get("avg_brier")) or 999.0,
    ))
    return {
        "window": name,
        "freeze_ts_utc": freeze_ts,
        "future_denominator": denominator,
        "ranked": enriched,
        "selected_rows_sample": details,
    }


def build_report() -> dict[str, Any]:
    state = load_or_create_state()
    reference_state = load_json(REFERENCE_FREEZE_JSON)
    reference_freeze = reference_state.get("freeze_ts_utc") or state["freeze_ts_utc"]
    windows = [
        score_window("diagnostic_existing_false_conviction_freeze", str(reference_freeze)),
        score_window("post_freeze_candidate", str(state["freeze_ts_utc"])),
    ]
    return {
        "state": state,
        "requirements": [
            "research-only, no live bot changes, no orders",
            "fixed physics variants, no parameter grid",
            "must preserve 75-90% coverage",
            "must reach >=30 settled post-freeze rows before live readiness",
            "must improve PnL and FV calibration versus raw adjusted-entry baseline",
        ],
        "interpretation": interpretation(windows),
        "windows": windows,
    }


def interpretation(windows: list[dict[str, Any]]) -> list[str]:
    notes = []
    for window in windows:
        ranked = window.get("ranked") or []
        best = ranked[0] if ranked else {}
        notes.append(
            f"{window.get('window')}: best {best.get('variant')} entries/settled/coverage/net "
            f"{best.get('entries')}/{best.get('settled')}/{best.get('coverage_pct')}/{best.get('net_cents')}c; "
            f"blockers {best.get('blockers') or []}."
        )
    notes.append("Use the diagnostic window only for direction; promotion depends on the post-freeze window.")
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
        "# v28 False-Conviction FV Entry Bridge",
        "",
        "Research-only; no live bot changes and no orders.",
        "",
        f"- Freeze UTC: `{(report.get('state') or {}).get('freeze_ts_utc')}`",
        f"- Candidate: `{(report.get('state') or {}).get('candidate')}`",
        "",
        "## Current Read",
        "",
    ]
    for note in report.get("interpretation") or []:
        lines.append(f"- {note}")
    for window in report.get("windows") or []:
        lines.extend([
            "",
            f"## {window.get('window')}",
            "",
            f"- Freeze UTC: `{window.get('freeze_ts_utc')}`",
            f"- Future denominator: `{window.get('future_denominator')}`",
            "",
        "| rank | scope + selector + variant | entries | settled | W/L | coverage | net c | d net | brier | d brier | logloss | d logloss | false-zone | approved/recon | blockers |",
        "|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|",
        ])
        for idx, row in enumerate(window.get("ranked") or [], start=1):
            lines.append(
                f"| {idx} | `{row.get('score_name')}` | {row.get('entries')} | {row.get('settled')} | "
                f"{row.get('wins')}/{row.get('losses')} | {fmt(row.get('coverage_pct'))} | "
                f"{fmt(row.get('net_cents'))} | {fmt(row.get('delta_net_vs_raw'))} | "
                f"{fmt(row.get('avg_brier'))} | {fmt(row.get('brier_delta_vs_raw'))} | "
                f"{fmt(row.get('avg_logloss'))} | {fmt(row.get('logloss_delta_vs_raw'))} | "
                f"{row.get('false_conviction_entries')} | {row.get('approved_entry_count')}/{row.get('reconstructed_count')} | "
                f"{', '.join(row.get('blockers') or []) or 'none'} |"
            )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    report = build_report()
    write_md(report)
    print(str(OUT_MD))


if __name__ == "__main__":
    main()
