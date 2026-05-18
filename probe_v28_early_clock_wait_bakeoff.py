"""Early-clock wait/repair bakeoff for the v28 target-coverage surface.

Research-only; no live bot changes or orders.

Physics hypothesis:
    In the first minutes of a BTC 15m market, near-boundary prices are often
    path-resolution guesses rather than stable FV. Instead of buying the first
    broad-coverage signal, wait for clock decay and accept the first later
    same-market row whose executable edge is still nonnegative. If no coherent
    later row appears, repair coverage from clean calmer rows.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from probe_v28_boundary_reversal_opportunity import row_net_after_fee, seconds_between
from probe_v28_composite_false_conviction_repair_bakeoff import first_clean_by_market_scored, score_farthest_boundary
from probe_v28_coverage_repair_pool_diagnostic import COVERAGE_FLOOR, build_surfaces, raw_edge, summarize
from probe_v28_shadow_entry_policy_bakeoff import base_tradeable


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
OUT_JSON = OUT_DIR / "v28_early_clock_wait_bakeoff_latest.json"
OUT_MD = OUT_DIR / "v28_early_clock_wait_bakeoff_latest.md"

EARLY_STC = 780.0
WAIT_STCS = [720.0, 660.0, 600.0, 480.0]
MAX_DELAY_SECONDS = 360.0
MAX_DELAYS = [240.0, 360.0, 480.0, 600.0]
P_FLOORS = [0.50, 0.55, 0.60]
DANGER_MODES = ["all_early", "early_boundary", "early_no_decay", "cheap_boundary"]
SIDE_MODES = ["any_side", "same_side", "opposite_side"]


def as_float(value: Any) -> float | None:
    if value is None or value == "":
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def seconds_to_close(row: dict[str, Any]) -> float | None:
    for key in ("seconds_to_close", "stc", "seconds_to_expiry"):
        value = as_float(row.get(key))
        if value is not None:
            return value
    return None


def probability(row: dict[str, Any]) -> float | None:
    return as_float(row.get("p_side") if row.get("p_side") is not None else row.get("p_raw"))


def abs_distance(row: dict[str, Any]) -> float | None:
    return as_float(row.get("abs_d_sigma"))


def recross(row: dict[str, Any]) -> float | None:
    return as_float(row.get("recross_hazard_score"))


def net_ready(row: dict[str, Any]) -> dict[str, Any]:
    net = row.get("net_gross_cents_after_entry_fee")
    if net is None:
        net = row_net_after_fee(row)
    edge = row.get("raw_edge_prob")
    if edge is None:
        edge = raw_edge(row)
    return {**row, "net_gross_cents_after_entry_fee": net, "raw_edge_prob": edge}


def is_danger(row: dict[str, Any], mode: str) -> bool:
    stc = seconds_to_close(row)
    p = probability(row)
    ask = as_float(row.get("ask_prob"))
    abs_d = abs_distance(row)
    r = recross(row)
    side = str(row.get("side") or "").lower()
    if stc is None or stc < EARLY_STC:
        return False
    if mode == "all_early":
        return True
    if mode == "early_boundary":
        return abs_d is not None and r is not None and abs_d <= 0.45 and r >= 0.55
    if mode == "early_no_decay":
        return side == "no" and p is not None and abs_d is not None and r is not None and p < 0.70 and abs_d <= 0.45 and r >= 0.55
    if mode == "cheap_boundary":
        return p is not None and ask is not None and abs_d is not None and r is not None and ask < 0.55 and p < 0.62 and abs_d <= 0.25 and r >= 0.75
    return False


def choose_wait_replacement(
    all_rows: list[dict[str, Any]],
    target: dict[str, Any],
    wait_stc: float,
    p_floor: float,
    side_mode: str,
    max_delay_seconds: float = MAX_DELAY_SECONDS,
) -> dict[str, Any] | None:
    market = str(target.get("market") or "")
    target_side = str(target.get("side") or "")
    candidates = []
    for row in all_rows:
        if str(row.get("market") or "") != market:
            continue
        if side_mode == "same_side" and str(row.get("side") or "") != target_side:
            continue
        if side_mode == "opposite_side" and str(row.get("side") or "") == target_side:
            continue
        delay = seconds_between(target.get("ts_wall"), row.get("ts_wall"))
        if delay is None or delay <= 0.0 or delay > max_delay_seconds:
            continue
        stc = seconds_to_close(row)
        if stc is None or stc > wait_stc:
            continue
        if not base_tradeable(row):
            continue
        p = probability(row)
        edge = raw_edge(row)
        if p is None or edge is None or p < p_floor or edge < 0.0:
            continue
        candidates.append({**net_ready(row), "replacement_delay_seconds": delay})
    candidates.sort(key=lambda row: (float(row.get("replacement_delay_seconds") or 999999.0), -float(row.get("raw_edge_prob") or -999.0)))
    return candidates[0] if candidates else None


def ceil_entries_for_floor(denominator: int) -> int:
    return int((COVERAGE_FLOOR * denominator + 99.999999) // 100)


def clean_repairs(all_rows: list[dict[str, Any]], markets: set[str]) -> list[dict[str, Any]]:
    return [net_ready(row) for row in first_clean_by_market_scored(all_rows, markets, score_farthest_boundary, chronological=False)]


def score_policy(
    all_rows: list[dict[str, Any]],
    target: list[dict[str, Any]],
    denominator: int,
    wait_stc: float,
    p_floor: float,
    danger_mode: str,
    side_mode: str,
    max_delay_seconds: float = MAX_DELAY_SECONDS,
) -> dict[str, Any]:
    all_markets = {str(row.get("market") or "") for row in all_rows if row.get("market")}
    target_markets = {str(row.get("market") or "") for row in target}
    danger = [net_ready(row) for row in target if is_danger(row, danger_mode)]
    danger_markets = {str(row.get("market") or "") for row in danger}
    kept = [net_ready(row) for row in target if str(row.get("market") or "") not in danger_markets]
    replacements = []
    cases = []
    for row in danger:
        repl = choose_wait_replacement(all_rows, row, wait_stc, p_floor, side_mode, max_delay_seconds)
        if repl is not None:
            replacements.append(repl)
        cases.append({"target": row_view(row), "replacement": row_view(repl) if repl else None})
    current = kept + replacements
    needed = max(0, ceil_entries_for_floor(denominator) - len(current))
    used_markets = {str(row.get("market") or "") for row in current if row.get("market")}
    repairs = clean_repairs(all_rows, all_markets - target_markets)[:needed]
    repair_markets = {str(row.get("market") or "") for row in repairs}
    if len(repairs) < needed:
        for row in clean_repairs(all_rows, all_markets - used_markets - repair_markets):
            if len(repairs) >= needed:
                break
            market = str(row.get("market") or "")
            if market in repair_markets:
                continue
            repairs.append(row)
            repair_markets.add(market)
    candidate = current + repairs
    summary = summarize(candidate, denominator)
    target_summary = summarize([net_ready(row) for row in target], denominator)
    return {
        "policy": f"{danger_mode}_wait{int(wait_stc)}_p{int(p_floor * 100)}_{side_mode}_delay{int(max_delay_seconds)}",
        "danger_mode": danger_mode,
        "wait_stc": wait_stc,
        "p_floor": p_floor,
        "side_mode": side_mode,
        "max_delay_seconds": max_delay_seconds,
        "target_summary": target_summary,
        "danger_summary": summarize(danger, denominator),
        "replacement_summary": summarize(replacements, denominator),
        "repair_summary": summarize(repairs, denominator),
        "candidate_summary": summary,
        "delta_vs_target_cents": float(summary.get("net_cents") or 0.0) - float(target_summary.get("net_cents") or 0.0),
        "needed_repairs": needed,
        "chosen_repairs": len(repairs),
        "cases": cases,
    }


def leave_one_out(policy: dict[str, Any]) -> dict[str, Any]:
    cases = []
    markets = sorted({str((case.get("target") or {}).get("market") or "") for case in policy.get("cases") or []})
    target_net = float((policy.get("target_summary") or {}).get("net_cents") or 0.0)
    candidate_net = float((policy.get("candidate_summary") or {}).get("net_cents") or 0.0)
    for market in markets:
        removed_target = sum(float(((case.get("target") or {}).get("net_cents")) or 0.0) for case in policy.get("cases") or [] if (case.get("target") or {}).get("market") == market)
        removed_repl = sum(float(((case.get("replacement") or {}).get("net_cents")) or 0.0) for case in policy.get("cases") or [] if (case.get("target") or {}).get("market") == market and case.get("replacement"))
        cases.append({"excluded_market": market, "loo_delta_cents": (candidate_net - removed_repl) - (target_net - removed_target)})
    deltas = [float(row["loo_delta_cents"]) for row in cases]
    return {
        "markets": len(markets),
        "worst_delta_cents": min(deltas) if deltas else None,
        "negative_exclusions": sum(1 for value in deltas if value < 0.0),
        "cases": cases,
    }


def row_view(row: dict[str, Any] | None) -> dict[str, Any] | None:
    if row is None:
        return None
    return {
        "market": row.get("market"),
        "source": row.get("source"),
        "side": row.get("side"),
        "side_won": row.get("side_won"),
        "net_cents": row.get("net_gross_cents_after_entry_fee"),
        "p_side": row.get("p_side"),
        "ask_prob": row.get("ask_prob"),
        "raw_edge_prob": row.get("raw_edge_prob"),
        "seconds_to_close": row.get("seconds_to_close"),
        "abs_d_sigma": row.get("abs_d_sigma"),
        "recross_hazard_score": row.get("recross_hazard_score"),
        "replacement_delay_seconds": row.get("replacement_delay_seconds"),
    }


def build_report() -> dict[str, Any]:
    all_rows, target, denominator, _forward_markets = build_surfaces()
    policies = []
    for danger_mode in DANGER_MODES:
        for wait_stc in WAIT_STCS:
            for max_delay_seconds in MAX_DELAYS:
                for p_floor in P_FLOORS:
                    for side_mode in SIDE_MODES:
                        policy = score_policy(
                            all_rows,
                            target,
                            denominator,
                            wait_stc,
                            p_floor,
                            danger_mode,
                            side_mode,
                            max_delay_seconds,
                        )
                        policy["loo"] = leave_one_out(policy)
                        policies.append(policy)
    policies.sort(
        key=lambda row: (
            -float((row.get("candidate_summary") or {}).get("net_cents") or -999999.0),
            abs(float((row.get("candidate_summary") or {}).get("coverage_pct") or 0.0) - 78.0),
            -float(row.get("delta_vs_target_cents") or -999999.0),
        )
    )
    best = policies[0] if policies else {}
    return {
        "diagnostic": "early_clock_wait_bakeoff",
        "physics": "Wait for early noisy boundary states to age before buying; repair coverage from calmer geometry.",
        "requirements": {
            "early_stc": EARLY_STC,
            "wait_stcs": WAIT_STCS,
            "max_delays": MAX_DELAYS,
            "p_floors": P_FLOORS,
            "danger_modes": DANGER_MODES,
            "side_modes": SIDE_MODES,
            "coverage_floor": COVERAGE_FLOOR,
        },
        "forward_denominator": denominator,
        "policy_count": len(policies),
        "best_policy": best.get("policy"),
        "best": best,
        "top": policies[:12],
        "interpretation": [
            f"Best early-clock wait policy is {best.get('policy')} with net {(best.get('candidate_summary') or {}).get('net_cents')}c.",
            f"Target net was {(best.get('target_summary') or {}).get('net_cents')}c; delta {best.get('delta_vs_target_cents')}c.",
            "This is discovery-only. Any viable row needs a frozen forward validator before promotion.",
        ],
    }


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
        "# v28 Early-Clock Wait Bakeoff",
        "",
        "Research-only; no live bot changes and no orders.",
        "",
        f"- Best policy: `{report.get('best_policy')}`",
        f"- Policy count: `{report.get('policy_count')}`",
        f"- Forward denominator: `{report.get('forward_denominator')}`",
        "",
        "## Interpretation",
        "",
    ]
    for note in report.get("interpretation") or []:
        lines.append(f"- {note}")
    lines.extend([
        "",
        "## Top Policies",
        "",
        "| policy | entries | settled | W/L | coverage | net c | delta c | danger net | repl net | repair net | LOO worst | LOO neg |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ])
    for row in report.get("top") or []:
        cand = row.get("candidate_summary") or {}
        danger = row.get("danger_summary") or {}
        repl = row.get("replacement_summary") or {}
        repair = row.get("repair_summary") or {}
        loo = row.get("loo") or {}
        lines.append(
            f"| `{row.get('policy')}` | {cand.get('entries')} | {cand.get('settled')} | {cand.get('wins')}/{cand.get('losses')} | "
            f"{fmt(cand.get('coverage_pct'))} | {fmt(cand.get('net_cents'))} | {fmt(row.get('delta_vs_target_cents'))} | "
            f"{fmt(danger.get('net_cents'))} | {fmt(repl.get('net_cents'))} | {fmt(repair.get('net_cents'))} | "
            f"{fmt(loo.get('worst_delta_cents'))} | {loo.get('negative_exclusions')} |"
        )
    best = report.get("best") or {}
    lines.extend([
        "",
        "## Best Cases",
        "",
        "| market | target side | target won | target net | stc | abs d | recross | repl side | repl won | repl net | delay |",
        "|---|---|---|---:|---:|---:|---:|---|---|---:|---:|",
    ])
    for case in (best.get("cases") or [])[:20]:
        target = case.get("target") or {}
        repl = case.get("replacement") or {}
        lines.append(
            f"| {target.get('market')} | {target.get('side')} | {target.get('side_won')} | {fmt(target.get('net_cents'))} | "
            f"{fmt(target.get('seconds_to_close'))} | {fmt(target.get('abs_d_sigma'))} | {fmt(target.get('recross_hazard_score'))} | "
            f"{repl.get('side')} | {repl.get('side_won')} | {fmt(repl.get('net_cents'))} | {fmt(repl.get('replacement_delay_seconds'))} |"
        )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    report = build_report()
    write_md(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
