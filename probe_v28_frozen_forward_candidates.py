"""Frozen forward-only scorecard for selected v28 FV candidates.

Discovery reports can overstate edge because the rule was chosen after seeing
some of the rows. This script creates a freeze timestamp on first run and only
scores future rows after that timestamp. It is shadow-only and does not affect
live trading.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from probe_v28_rmt_forgetting_entry_bakeoff import build_report as build_entry_bakeoff_report
from probe_v28_rmt_forgetting_entry_bakeoff import FV, THRESHOLDS, effective_edge, selected_rows
from probe_v28_rmt_regime_diagnostic import attach_regime_rows
from probe_v28_shadow_entry_policy_bakeoff import observation_pool
from probe_v28_state_aware_fv_candidates import enrich_state


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
STATE_JSON = OUT_DIR / "v28_frozen_forward_candidates_state.json"
OUT_JSON = OUT_DIR / "v28_frozen_forward_candidates_latest.json"
OUT_MD = OUT_DIR / "v28_frozen_forward_candidates_latest.md"

FROZEN_POLICIES = [
    {
        "policy": "first_side_raw_later_book_p60_edge0",
        "role": "primary_calibrated_broad_candidate",
        "physics": "Retain raw v28 only on first market-side observation, then forget stale geometry and anchor to book. Requires effective p >= 0.60 and nonnegative effective edge.",
    },
    {
        "policy": "rmt_repetition_forget_p60_edge0",
        "role": "primary_rmt_forgetting_candidate",
        "physics": "Use RMT regime plus repeated-side state to decide how aggressively to forget v28 and anchor to book. Requires effective p >= 0.60 and nonnegative effective edge.",
    },
    {
        "policy": "book_ask_prior_p60_edge0",
        "role": "book_favorite_control",
        "physics": "Pure executable book favorite control. Tests whether the edge is just book favorites above 60c.",
    },
    {
        "policy": "v28_raw_p50_edge0",
        "role": "raw_broad_control",
        "physics": "Raw v28 broad control. Kept to test whether better P&L is unstable over time despite weaker calibration.",
    },
]

POLICY_PARAMS = {
    f"{fv_name}_{threshold_name}": (fv_name, min_p, min_edge)
    for fv_name in FV
    for threshold_name, min_p, min_edge in THRESHOLDS
}


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def parse_ts(value: Any) -> datetime | None:
    if value is None:
        return None
    text = str(value)
    try:
        if text.endswith("Z"):
            text = text[:-1] + "+00:00"
        dt = datetime.fromisoformat(text)
    except ValueError:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def load_or_create_state() -> dict[str, Any]:
    if STATE_JSON.exists():
        try:
            payload = json.loads(STATE_JSON.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            payload = {}
        if isinstance(payload, dict) and payload.get("freeze_ts"):
            return payload
    payload = {
        "freeze_ts": utc_now_iso(),
        "policies": FROZEN_POLICIES,
        "promotion_floor": {
            "min_settled": 30,
            "max_simulated_share": 0.35,
            "required_coverage_pct_min": 70.0,
            "required_coverage_pct_max": 90.0,
            "must_be_net_positive": True,
            "must_have_nonnegative_temporal_halves": True,
            "fv_validation_allows_shadow_rows": True,
        },
    }
    STATE_JSON.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return payload


def load_entry_rows() -> tuple[int, list[dict[str, Any]]]:
    payload = build_entry_bakeoff_report()
    rows = payload.get("rows")
    watched = int(payload.get("watched_markets") or 0)
    return watched, rows if isinstance(rows, list) else []


def market_timing(freeze_dt: datetime | None) -> dict[str, Any]:
    if freeze_dt is None:
        return {
            "clean_forward_markets": set(),
            "excluded_in_progress_markets": set(),
            "post_freeze_observed_markets": set(),
        }
    first_seen: dict[str, datetime] = {}
    post_freeze_seen: set[str] = set()
    for row in observation_pool():
        ts = parse_ts(row.get("ts_wall"))
        market = str(row.get("market") or "")
        if ts is not None and market:
            if market not in first_seen or ts < first_seen[market]:
                first_seen[market] = ts
            if ts >= freeze_dt:
                post_freeze_seen.add(market)
    clean = {market for market, first_ts in first_seen.items() if first_ts >= freeze_dt}
    return {
        "clean_forward_markets": clean,
        "excluded_in_progress_markets": post_freeze_seen - clean,
        "post_freeze_observed_markets": post_freeze_seen,
    }


def as_float(value: Any) -> float | None:
    if value is None or value == "":
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def summarize(policy: str, rows: list[dict[str, Any]], forward_denominator: int) -> dict[str, Any]:
    resolved = [row for row in rows if row.get("gross_cents") is not None]
    settled = [row for row in rows if row.get("side_won") is not None]
    gross = sum(float(row.get("gross_cents") or 0.0) for row in resolved)
    net = sum(float(row.get("net_gross_cents_after_entry_fee") or row.get("gross_cents") or 0.0) for row in resolved)
    briers = [
        (float(row["p_eff"]) - (1.0 if row.get("side_won") is True else 0.0)) ** 2
        for row in settled
        if row.get("p_eff") is not None
    ]
    entries = len(rows)
    return {
        "policy": policy,
        "entries": entries,
        "resolved": len(resolved),
        "settled": len(settled),
        "wins": sum(1 for row in settled if row.get("side_won") is True),
        "losses": sum(1 for row in settled if row.get("side_won") is False),
        "coverage_pct": (entries / forward_denominator * 100.0) if forward_denominator else None,
        "gross_cents": gross,
        "net_cents_after_entry_fee": net,
        "avg_net_cents_after_entry_fee": net / len(resolved) if resolved else None,
        "avg_brier": sum(briers) / len(briers) if briers else None,
        "approved_entry_count": sum(1 for row in rows if row.get("source") == "approved_entry"),
        "added_reject_count": sum(1 for row in rows if row.get("source") == "rejected_actionable"),
    }


def promotion_checks(row: dict[str, Any], floor: dict[str, Any]) -> dict[str, Any]:
    blockers: list[str] = []
    settled = as_float(row.get("settled")) or 0.0
    entries = as_float(row.get("entries")) or 0.0
    added = as_float(row.get("added_reject_count")) or 0.0
    sim_share = added / entries if entries else None
    coverage = as_float(row.get("coverage_pct"))
    if settled < float(floor.get("min_settled") or 30):
        blockers.append(f"settled_lt_{floor.get('min_settled')}")
    if sim_share is None or sim_share > float(floor.get("max_simulated_share") or 0.35):
        blockers.append(f"simulated_share_gt_{floor.get('max_simulated_share')}")
    if coverage is None or coverage < float(floor.get("required_coverage_pct_min") or 70.0):
        blockers.append("coverage_too_low")
    if coverage is not None and coverage > float(floor.get("required_coverage_pct_max") or 90.0):
        blockers.append("coverage_too_high")
    if floor.get("must_be_net_positive") and float(row.get("net_cents_after_entry_fee") or 0.0) <= 0.0:
        blockers.append("net_not_positive")
    return {
        "simulated_share": sim_share,
        "blockers": blockers,
        "promotable": not blockers,
    }


def fv_validation_checks(row: dict[str, Any], floor: dict[str, Any]) -> dict[str, Any]:
    blockers: list[str] = []
    settled = as_float(row.get("settled")) or 0.0
    coverage = as_float(row.get("coverage_pct"))
    if settled < float(floor.get("min_settled") or 30):
        blockers.append(f"settled_lt_{floor.get('min_settled')}")
    if coverage is None or coverage < float(floor.get("required_coverage_pct_min") or 70.0):
        blockers.append("coverage_too_low")
    if coverage is not None and coverage > float(floor.get("required_coverage_pct_max") or 90.0):
        blockers.append("coverage_too_high")
    if floor.get("must_be_net_positive") and float(row.get("net_cents_after_entry_fee") or 0.0) <= 0.0:
        blockers.append("net_not_positive")
    return {
        "blockers": blockers,
        "validated": not blockers,
    }


def build_report() -> dict[str, Any]:
    state = load_or_create_state()
    freeze_dt = parse_ts(state["freeze_ts"])
    watched_count, rows = load_entry_rows()
    enriched_observations = enrich_state(attach_regime_rows(observation_pool()))
    timing = market_timing(freeze_dt)
    forward_markets = timing["clean_forward_markets"]
    future_rows = [
        row for row in rows
        if str(row.get("market") or "") in forward_markets
    ]
    forward_denominator = len(forward_markets)
    floor = state.get("promotion_floor") or {}
    summary: list[dict[str, Any]] = []
    for item in state.get("policies") or FROZEN_POLICIES:
        policy = item["policy"]
        policy_rows = [row for row in future_rows if row.get("policy") == policy]
        s = summarize(policy, policy_rows, forward_denominator)
        selected_markets = {str(row.get("market") or "") for row in policy_rows if row.get("market")}
        missed_markets = sorted(forward_markets - selected_markets)
        miss_details = [
            missed_market_detail(policy, market, enriched_observations)
            for market in missed_markets
        ]
        summary.append({
            **s,
            "role": item.get("role"),
            "missed_forward_markets": missed_markets,
            "missed_forward_market_count": len(missed_markets),
            "missed_forward_market_details": miss_details,
            "selected_forward_rows": selected_row_details(policy_rows),
            "fv_validation_checks": fv_validation_checks(s, floor),
            "execution_promotion_checks": promotion_checks(s, floor),
        })
    return {
        "freeze_ts": state["freeze_ts"],
        "watched_markets_current_denominator": watched_count,
        "forward_market_denominator": forward_denominator,
        "forward_markets": sorted(forward_markets),
        "excluded_in_progress_markets": sorted(timing["excluded_in_progress_markets"]),
        "post_freeze_observed_markets": sorted(timing["post_freeze_observed_markets"]),
        "future_candidate_rows": len(future_rows),
        "policies": state.get("policies") or FROZEN_POLICIES,
        "promotion_floor": floor,
        "summary": summary,
    }


def missed_market_detail(policy: str, market: str, observations: list[dict[str, Any]]) -> dict[str, Any]:
    params = POLICY_PARAMS.get(policy)
    market_rows = [row for row in observations if row.get("market") == market]
    if not params or not market_rows:
        return {"market": market, "reason": "no_policy_params_or_rows"}
    fv_name, min_p, min_edge = params
    fn = FV[fv_name]
    candidates: list[dict[str, Any]] = []
    for row in sorted(market_rows, key=lambda item: str(item.get("ts_wall") or "")):
        try:
            p_eff = fn(row)
        except (KeyError, TypeError, ValueError):
            continue
        edge = effective_edge(row, p_eff)
        candidates.append({
            "ts_wall": row.get("ts_wall"),
            "side": row.get("side"),
            "source": row.get("source"),
            "reason": row.get("reason"),
            "p_side": row.get("p_side"),
            "ask_prob": row.get("ask_prob"),
            "p_eff": p_eff,
            "eff_edge_prob": edge,
            "spectral_tag": row.get("spectral_tag"),
            "market_side_observation_index": row.get("market_side_observation_index"),
            "failed_min_p": p_eff < min_p,
            "failed_min_edge": edge is None or edge < min_edge,
        })
    best = sorted(
        candidates,
        key=lambda item: (float(item.get("p_eff") or -1.0), float(item.get("eff_edge_prob") or -999.0)),
        reverse=True,
    )
    return {
        "market": market,
        "policy": policy,
        "min_p": min_p,
        "min_edge": min_edge,
        "best_candidate": best[0] if best else None,
        "candidate_count": len(candidates),
        "reason": classify_miss(best[0] if best else None),
    }


def classify_miss(best: dict[str, Any] | None) -> str:
    if not best:
        return "no_candidate_rows"
    if best.get("failed_min_p") and best.get("failed_min_edge"):
        return "p_and_edge_below_threshold"
    if best.get("failed_min_p"):
        return "p_below_threshold"
    if best.get("failed_min_edge"):
        return "edge_below_threshold"
    return "unknown_selection_miss"


def selected_row_details(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    details: list[dict[str, Any]] = []
    for row in sorted(rows, key=lambda item: str(item.get("ts_wall") or "")):
        details.append({
            "market": row.get("market"),
            "ts_wall": row.get("ts_wall"),
            "source": row.get("source"),
            "side": row.get("side"),
            "reason": row.get("reason"),
            "seconds_to_close": row.get("seconds_to_close"),
            "market_observation_index": row.get("market_observation_index"),
            "market_side_observation_index": row.get("market_side_observation_index"),
            "p_eff": row.get("p_eff"),
            "p_side": row.get("p_side"),
            "ask_prob": row.get("ask_prob"),
            "eff_edge_prob": row.get("eff_edge_prob"),
            "spectral_tag": row.get("spectral_tag"),
            "gross_cents": row.get("gross_cents"),
            "net_gross_cents_after_entry_fee": row.get("net_gross_cents_after_entry_fee"),
            "side_won": row.get("side_won"),
        })
    return details


def fmt(value: Any) -> str:
    if value is None:
        return "None"
    if isinstance(value, float):
        return f"{value:.6f}"
    return str(value)


def write_md(report: dict[str, Any]) -> None:
    lines = [
        "# v28 Frozen Forward Candidates",
        "",
        "Forward-only scorecard. Rows before freeze timestamp do not count.",
        "",
        f"- Freeze timestamp UTC: `{report['freeze_ts']}`",
        f"- Current watched-market denominator: `{report['watched_markets_current_denominator']}`",
        f"- Forward market denominator: `{report['forward_market_denominator']}`",
        f"- Excluded in-progress post-freeze markets: `{len(report['excluded_in_progress_markets'])}`",
        f"- Future candidate rows: `{report['future_candidate_rows']}`",
        "",
        "## Frozen Policies",
        "",
    ]
    for item in report["policies"]:
        lines.append(f"- `{item['policy']}` ({item.get('role')}): {item.get('physics')}")
    lines.extend([
        "",
        "## Forward Scorecard",
        "",
        "| policy | entries | settled | wins/losses | coverage | net c | avg brier | actual/shadow | FV blockers | execution blockers |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---|---|",
    ])
    for row in report["summary"]:
        fv_checks = row.get("fv_validation_checks") or {}
        exec_checks = row.get("execution_promotion_checks") or {}
        lines.append(
            f"| {row['policy']} | {row['entries']} | {row['settled']} | {row['wins']}/{row['losses']} | "
            f"{fmt(row['coverage_pct'])} | {fmt(row['net_cents_after_entry_fee'])} | {fmt(row['avg_brier'])} | "
            f"{row['approved_entry_count']}/{row['added_reject_count']} | "
            f"{', '.join(fv_checks.get('blockers') or []) or 'none'} | "
            f"{', '.join(exec_checks.get('blockers') or []) or 'none'} |"
        )
    lines.extend(["", "## Missed Forward Markets", ""])
    for row in report["summary"]:
        missed = row.get("missed_forward_markets") or []
        preview = ", ".join(missed[:8])
        if len(missed) > 8:
            preview += ", ..."
        lines.append(f"- `{row['policy']}` missed `{len(missed)}`: {preview or 'none'}")
        for detail in row.get("missed_forward_market_details") or []:
            best = detail.get("best_candidate") or {}
            lines.append(
                f"  - `{detail.get('market')}` reason `{detail.get('reason')}`, best side `{best.get('side')}`, "
                f"p_eff `{fmt(best.get('p_eff'))}`, ask `{fmt(best.get('ask_prob'))}`, "
                f"edge `{fmt(best.get('eff_edge_prob'))}`, raw_p `{fmt(best.get('p_side'))}`"
            )
    lines.extend(["", "## Excluded In-Progress Markets", ""])
    excluded = report.get("excluded_in_progress_markets") or []
    lines.append(", ".join(excluded) if excluded else "none")
    lines.extend(["", "## Selected Forward Rows", ""])
    for row in report["summary"]:
        lines.append(f"### {row['policy']}")
        selected = row.get("selected_forward_rows") or []
        if not selected:
            lines.append("none")
            continue
        lines.append("| market | ts | side | source | obs idx | stc | p_eff | raw p | ask | edge | won | net c |")
        lines.append("|---|---|---|---|---:|---:|---:|---:|---:|---:|---|---:|")
        for item in selected[-10:]:
            lines.append(
                f"| {item.get('market')} | {item.get('ts_wall')} | {item.get('side')} | {item.get('source')} | "
                f"{fmt(item.get('market_observation_index'))} | {fmt(item.get('seconds_to_close'))} | "
                f"{fmt(item.get('p_eff'))} | {fmt(item.get('p_side'))} | {fmt(item.get('ask_prob'))} | "
                f"{fmt(item.get('eff_edge_prob'))} | {item.get('side_won')} | {fmt(item.get('net_gross_cents_after_entry_fee'))} |"
            )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    report = build_report()
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_md(report)
    print(str(OUT_MD))


if __name__ == "__main__":
    main()
