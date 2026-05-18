"""Hybrid-veto repair probe for the v28 target coverage surface.

Research-only; no live bot changes or orders.

The target surface has a bad cluster where raw v28 says the ask is favorable,
but the hybrid confidence-shrink FV pulls fair value below the ask. Skipping
that cluster alone cuts too much coverage, so this probe asks whether we can
replace those rows with cleaner missed-market opportunities while preserving a
75% participation floor.
"""
from __future__ import annotations

import json
import math
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

from probe_v28_coverage_repair_pool_diagnostic import (
    COVERAGE_FLOOR,
    as_float,
    is_clean_repair,
    raw_edge,
    row_net_after_fee,
    summarize,
)
from probe_v28_frozen_forward_candidates import market_timing, parse_ts
from probe_v28_hybrid_confidence_shrink_fv import hybrid_reason, p_hybrid
from probe_v28_raw_entry_coverage_valve import selected_base_rows
from probe_v28_rmt_regime_diagnostic import attach_regime_rows
from probe_v28_shadow_entry_policy_bakeoff import observation_pool
from probe_v28_state_aware_fv_candidates import enrich_state
from probe_v28_target_coverage_fv_overlay_validator import (
    STATE_JSON as TARGET_STATE_JSON,
    apply_policy,
    load_json,
)


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
STATE_JSON = OUT_DIR / "v28_target_hybrid_veto_repair_state.json"
OUT_JSON = OUT_DIR / "v28_target_hybrid_veto_repair_latest.json"
OUT_MD = OUT_DIR / "v28_target_hybrid_veto_repair_latest.md"

POLICY = "raw_p50_turbulence_valve_edge4_p60_recross75_near25"
MIN_SETTLED = 30


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def load_or_create_state() -> dict[str, Any]:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    if STATE_JSON.exists():
        payload = load_json(STATE_JSON)
        if payload.get("freeze_ts_utc") and payload.get("policy") == POLICY:
            return payload
    payload = {
        "freeze_ts_utc": utc_now_iso(),
        "policy": POLICY,
        "candidate_family": "target_hybrid_veto_repair",
        "coverage_floor": COVERAGE_FLOOR,
        "danger_rule": "raw edge >= 0 but hybrid confidence-shrink edge < 0",
        "repair_rule": "replace skipped target markets with first clean missed-market rows ranked by hybrid-adjusted stability",
        "physics": (
            "When raw FV barely clears the ask but shrink-to-50 pulls fair value below the ask, "
            "the market is usually near a noisy boundary where the apparent edge is path-fragile. "
            "The repair pool tries to keep broad participation by shifting that risk budget to "
            "cleaner rows with positive hybrid edge, calmer recross geometry, or stronger distance."
        ),
    }
    STATE_JSON.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return payload


def clamp_prob(value: float) -> float:
    return max(0.000001, min(0.999999, value))


def p_raw(row: dict[str, Any]) -> float:
    value = as_float(row.get("p_side") if row.get("p_side") is not None else row.get("p_raw"))
    if value is None:
        raise ValueError("missing raw probability")
    return clamp_prob(value)


def ask_prob(row: dict[str, Any]) -> float | None:
    value = as_float(row.get("ask_prob"))
    if value is not None:
        return value
    cents = as_float(row.get("ask_cents"))
    return None if cents is None else cents / 100.0


def raw_edge_value(row: dict[str, Any]) -> float | None:
    edge = raw_edge(row)
    if edge is not None:
        return edge
    ask = ask_prob(row)
    return None if ask is None else p_raw(row) - ask


def hybrid_edge_value(row: dict[str, Any]) -> float | None:
    ask = ask_prob(row)
    return None if ask is None else p_hybrid(row) - ask


def recross_score(row: dict[str, Any]) -> float:
    value = as_float(row.get("recross_hazard_score"))
    return value if value is not None else 1.0


def abs_distance(row: dict[str, Any]) -> float:
    value = as_float(row.get("abs_d_sigma"))
    return value if value is not None else 0.0


def is_hybrid_veto(row: dict[str, Any]) -> bool:
    raw = raw_edge_value(row)
    hybrid = hybrid_edge_value(row)
    return raw is not None and hybrid is not None and raw >= 0.0 and hybrid < 0.0


def danger_all_veto(row: dict[str, Any]) -> bool:
    return is_hybrid_veto(row)


def danger_veto_negative_2pp(row: dict[str, Any]) -> bool:
    hybrid = hybrid_edge_value(row)
    return is_hybrid_veto(row) and hybrid is not None and hybrid <= -0.02


def danger_veto_high_recross(row: dict[str, Any]) -> bool:
    return is_hybrid_veto(row) and recross_score(row) >= 0.75


def danger_veto_high_recross_near(row: dict[str, Any]) -> bool:
    return is_hybrid_veto(row) and recross_score(row) >= 0.75 and abs_distance(row) <= 0.45


def danger_veto_phi_half(row: dict[str, Any]) -> bool:
    return is_hybrid_veto(row) and hybrid_reason(row) == "phi_half_high_recross"


DANGER_RULES: dict[str, Callable[[dict[str, Any]], bool]] = {
    "skip_all_hybrid_vetoes": danger_all_veto,
    "skip_hybrid_veto_edge_lte_minus2pp": danger_veto_negative_2pp,
    "skip_hybrid_veto_high_recross": danger_veto_high_recross,
    "skip_hybrid_veto_high_recross_near": danger_veto_high_recross_near,
    "skip_hybrid_veto_phi_half_reason": danger_veto_phi_half,
}


def ceil_entries_for_floor(denominator: int) -> int:
    return int((COVERAGE_FLOOR * denominator + 99.999999) // 100)


def source_counts(rows: list[dict[str, Any]]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for row in rows:
        key = str(row.get("source") or "unknown")
        counts[key] = counts.get(key, 0) + 1
    return dict(sorted(counts.items()))


def hybrid_repair_score(row: dict[str, Any]) -> float:
    p = p_hybrid(row)
    edge = hybrid_edge_value(row)
    raw = raw_edge_value(row)
    return (
        p
        + 1.75 * (edge if edge is not None else -1.0)
        + 0.25 * (raw if raw is not None else 0.0)
        + 0.05 * abs_distance(row)
        - 0.08 * recross_score(row)
    )


def is_hybrid_clean_repair(row: dict[str, Any], require_hybrid_edge: bool) -> bool:
    if not is_clean_repair(row):
        return False
    edge = hybrid_edge_value(row)
    if edge is None:
        return False
    if require_hybrid_edge and edge < 0.0:
        return False
    return ask_prob(row) is not None and p_hybrid(row) >= 0.55


def repair_rows_by_market(
    rows: list[dict[str, Any]],
    markets: set[str],
    require_hybrid_edge: bool,
) -> list[dict[str, Any]]:
    candidates: list[dict[str, Any]] = []
    for row in rows:
        market = str(row.get("market") or "")
        if market not in markets or not is_hybrid_clean_repair(row, require_hybrid_edge):
            continue
        candidates.append(
            {
                **row,
                "raw_edge_prob": raw_edge_value(row),
                "hybrid_edge_prob": hybrid_edge_value(row),
                "p_hybrid": p_hybrid(row),
                "hybrid_reason": hybrid_reason(row),
                "repair_score": hybrid_repair_score(row),
                "net_gross_cents_after_entry_fee": row_net_after_fee(row),
            }
        )
    candidates.sort(key=lambda row: (-float(row.get("repair_score") or -999.0), str(row.get("ts_wall") or "")))
    out: list[dict[str, Any]] = []
    seen: set[str] = set()
    for row in candidates:
        market = str(row.get("market") or "")
        if market in seen:
            continue
        out.append(row)
        seen.add(market)
    return out


def surface_for_freeze(freeze_ts: str) -> tuple[list[dict[str, Any]], list[dict[str, Any]], int, set[str]]:
    timing = market_timing(parse_ts(freeze_ts))
    forward_markets = set(timing["clean_forward_markets"])
    all_rows = enrich_state(attach_regime_rows(observation_pool()))
    all_rows = [row for row in all_rows if str(row.get("market") or "") in forward_markets]
    target = apply_policy(selected_base_rows(), POLICY)
    target = [row for row in target if str(row.get("market") or "") in forward_markets]
    return all_rows, target, len(forward_markets), forward_markets


def build_candidate(
    all_rows: list[dict[str, Any]],
    target: list[dict[str, Any]],
    denominator: int,
    forward_markets: set[str],
    name: str,
    danger_fn: Callable[[dict[str, Any]], bool],
    require_hybrid_edge: bool,
) -> dict[str, Any]:
    target_markets = {str(row.get("market") or "") for row in target}
    danger = [row for row in target if danger_fn(row)]
    danger_markets = {str(row.get("market") or "") for row in danger}
    kept = [row for row in target if str(row.get("market") or "") not in danger_markets]
    needed = max(0, ceil_entries_for_floor(denominator) - len(kept))

    missed = repair_rows_by_market(all_rows, forward_markets - target_markets, require_hybrid_edge)
    chosen = missed[:needed]
    chosen_markets = {str(row.get("market") or "") for row in chosen}
    if len(chosen) < needed:
        kept_markets = {str(row.get("market") or "") for row in kept}
        extras = repair_rows_by_market(
            all_rows,
            forward_markets - kept_markets - chosen_markets,
            require_hybrid_edge,
        )
        for row in extras:
            if len(chosen) >= needed:
                break
            market = str(row.get("market") or "")
            if market in chosen_markets:
                continue
            chosen.append(row)
            chosen_markets.add(market)

    candidate = kept + chosen
    target_summary = summarize(target, denominator)
    candidate_summary = summarize(candidate, denominator)
    danger_summary = summarize(danger, denominator)
    repair_summary = summarize(chosen, denominator)
    return {
        "candidate": name,
        "require_hybrid_edge_repair": require_hybrid_edge,
        "target_summary": target_summary,
        "danger_summary": danger_summary,
        "kept_summary": summarize(kept, denominator),
        "repair_summary": repair_summary,
        "candidate_summary": candidate_summary,
        "needed_repairs": needed,
        "available_missed_repairs": len(missed),
        "chosen_repairs": len(chosen),
        "delta_vs_target_cents": float(candidate_summary.get("net_cents") or 0.0)
        - float(target_summary.get("net_cents") or 0.0),
        "source_counts": source_counts(candidate),
        "blockers": blockers(candidate_summary),
        "danger_rows": [compact(row) for row in danger],
        "repair_rows": [compact(row) for row in chosen],
    }


def blockers(summary: dict[str, Any]) -> list[str]:
    out: list[str] = []
    settled = int(as_float(summary.get("settled")) or 0)
    coverage = as_float(summary.get("coverage_pct"))
    net = as_float(summary.get("net_cents"))
    if settled < MIN_SETTLED:
        out.append("settled_lt_30")
    if coverage is None or coverage < COVERAGE_FLOOR:
        out.append("coverage_too_low")
    if net is None or net <= 0.0:
        out.append("net_not_positive")
    return out


def compact(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "market": row.get("market"),
        "ts_wall": row.get("ts_wall"),
        "source": row.get("source"),
        "side": row.get("side"),
        "side_won": row.get("side_won"),
        "net_cents": row.get("net_gross_cents_after_entry_fee") or row_net_after_fee(row),
        "p_raw": safe_prob(p_raw, row),
        "p_hybrid": safe_prob(p_hybrid, row),
        "ask_prob": ask_prob(row),
        "raw_edge": raw_edge_value(row),
        "hybrid_edge": hybrid_edge_value(row),
        "hybrid_reason": safe_reason(row),
        "recross_hazard_score": row.get("recross_hazard_score"),
        "abs_d_sigma": row.get("abs_d_sigma"),
        "repair_score": row.get("repair_score"),
    }


def safe_prob(fn: Callable[[dict[str, Any]], float], row: dict[str, Any]) -> float | None:
    try:
        return fn(row)
    except (KeyError, TypeError, ValueError, ZeroDivisionError):
        return None


def safe_reason(row: dict[str, Any]) -> str | None:
    try:
        return hybrid_reason(row)
    except (KeyError, TypeError, ValueError, ZeroDivisionError):
        return None


def evaluate_window(label: str, freeze_ts: str) -> dict[str, Any]:
    all_rows, target, denominator, forward_markets = surface_for_freeze(freeze_ts)
    variants: list[dict[str, Any]] = []
    for danger_name, danger_fn in DANGER_RULES.items():
        for require_hybrid_edge in (True, False):
            suffix = "hybrid_edge_repair" if require_hybrid_edge else "raw_clean_repair"
            variants.append(
                build_candidate(
                    all_rows,
                    target,
                    denominator,
                    forward_markets,
                    f"{danger_name}_{suffix}",
                    danger_fn,
                    require_hybrid_edge,
                )
            )
    variants.sort(
        key=lambda row: (
            len(row.get("blockers") or []),
            -float(row.get("delta_vs_target_cents") or -999999.0),
            -float((row.get("candidate_summary") or {}).get("net_cents") or -999999.0),
        )
    )
    return {
        "window": label,
        "freeze_ts": freeze_ts,
        "forward_denominator": denominator,
        "target_summary": summarize(target, denominator),
        "hybrid_veto_summary": summarize([row for row in target if is_hybrid_veto(row)], denominator),
        "variants": variants,
    }


def build_report() -> dict[str, Any]:
    state = load_or_create_state()
    target_state = load_json(TARGET_STATE_JSON)
    diagnostic_freeze = target_state.get("source_coverage_freeze_ts") or target_state.get("freeze_ts")
    windows = []
    if diagnostic_freeze:
        windows.append(evaluate_window("diagnostic_existing_target_window", str(diagnostic_freeze)))
    windows.append(evaluate_window("post_repair_freeze_window", str(state["freeze_ts_utc"])))
    return {
        "generated_at_utc": utc_now_iso(),
        "state": state,
        "policy": POLICY,
        "interpretation": interpretation(windows),
        "windows": windows,
    }


def interpretation(windows: list[dict[str, Any]]) -> list[str]:
    notes = [
        "This probe is research-only and does not change live entries.",
        "The diagnostic window is for idea triage; the post-repair-freeze window is the promotion evidence stream.",
    ]
    for window in windows:
        best = (window.get("variants") or [{}])[0]
        cand = best.get("candidate_summary") or {}
        target = window.get("target_summary") or {}
        veto = window.get("hybrid_veto_summary") or {}
        notes.append(
            f"{window.get('window')}: target net {target.get('net_cents')}c, hybrid-veto cluster "
            f"{veto.get('settled')} settled for {veto.get('net_cents')}c, best candidate "
            f"{best.get('candidate')} coverage {cand.get('coverage_pct')}% net {cand.get('net_cents')}c "
            f"delta {best.get('delta_vs_target_cents')}c blockers {best.get('blockers')}."
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
    state = report.get("state") or {}
    lines = [
        "# v28 Target Hybrid-Veto Repair",
        "",
        "Research-only: use hybrid FV as a warning light, then repair coverage from cleaner missed-market rows.",
        "",
        f"- Generated UTC: `{report.get('generated_at_utc')}`",
        f"- Repair freeze UTC: `{state.get('freeze_ts_utc')}`",
        f"- Policy: `{report.get('policy')}`",
        f"- Coverage floor: `{state.get('coverage_floor')}`",
        "",
        "## Interpretation",
        "",
    ]
    for note in report.get("interpretation") or []:
        lines.append(f"- {note}")
    for window in report.get("windows") or []:
        lines.extend(
            [
                "",
                f"## {window.get('window')}",
                "",
                f"- Freeze UTC: `{window.get('freeze_ts')}`",
                f"- Forward denominator: `{window.get('forward_denominator')}`",
                "",
                "| rank | candidate | repairs | coverage | net c | delta c | W/L | veto net c | repair net c | blockers |",
                "|---:|---|---:|---:|---:|---:|---:|---:|---:|---|",
            ]
        )
        for idx, row in enumerate(window.get("variants") or [], start=1):
            cand = row.get("candidate_summary") or {}
            veto = row.get("danger_summary") or {}
            repairs = row.get("repair_summary") or {}
            lines.append(
                f"| {idx} | {row.get('candidate')} | {row.get('chosen_repairs')} | "
                f"{fmt(cand.get('coverage_pct'))} | {fmt(cand.get('net_cents'))} | "
                f"{fmt(row.get('delta_vs_target_cents'))} | {cand.get('wins')}/{cand.get('losses')} | "
                f"{fmt(veto.get('net_cents'))} | {fmt(repairs.get('net_cents'))} | "
                f"{', '.join(row.get('blockers') or [])} |"
            )
        best = (window.get("variants") or [{}])[0]
        lines.extend(
            [
                "",
                "### Best Candidate Repairs",
                "",
                "| market | source | side | won | net c | raw p | hybrid p | ask | raw edge | hybrid edge | recross | abs d | score |",
                "|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
            ]
        )
        for row in best.get("repair_rows") or []:
            lines.append(
                f"| {row.get('market')} | {row.get('source')} | {row.get('side')} | {row.get('side_won')} | "
                f"{fmt(row.get('net_cents'))} | {fmt(row.get('p_raw'))} | {fmt(row.get('p_hybrid'))} | "
                f"{fmt(row.get('ask_prob'))} | {fmt(row.get('raw_edge'))} | {fmt(row.get('hybrid_edge'))} | "
                f"{fmt(row.get('recross_hazard_score'))} | {fmt(row.get('abs_d_sigma'))} | {fmt(row.get('repair_score'))} |"
            )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    report = build_report()
    write_md(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
