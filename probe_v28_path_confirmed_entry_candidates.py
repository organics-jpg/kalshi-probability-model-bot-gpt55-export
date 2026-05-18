"""Path-confirmed challengers for broad raw-v28 entries.

The failure mode under test is path dependence: an early raw-p50 broad entry can
pick one side, then the stricter v28 path later approves the opposite side. A
live-realistic response is not to peek at settlement, but to wait briefly and
require the same side to remain eligible without opposite v28 approval.

Research-only; no live bot changes or orders.
"""
from __future__ import annotations

import json
from datetime import timedelta
from pathlib import Path
from typing import Any

from probe_v28_frozen_forward_candidates import market_timing, parse_ts
from probe_v28_noise_floor_shrinkage_candidates import selected_rows
from probe_v28_raw_entry_calibrated_probability import clamp_prob, logloss
from probe_v28_reactivated_shadow_status import read_events
from probe_v28_rmt_forgetting_entry_bakeoff import estimate_entry_fee_cents
from probe_v28_rmt_regime_diagnostic import attach_regime_rows
from probe_v28_shadow_entry_policy_bakeoff import base_tradeable, observation_pool
from probe_v28_state_aware_fv_candidates import enrich_state, p_raw, p_rmt_memory_gate, p_rmt_repetition_forget


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
STATE_JSON = OUT_DIR / "v28_frozen_raw_entry_calibrated_probability_state.json"
OUT_JSON = OUT_DIR / "v28_path_confirmed_entry_candidates_latest.json"
OUT_MD = OUT_DIR / "v28_path_confirmed_entry_candidates_latest.md"
WAIT_SECONDS = [120, 180, 240]
SELECTIVE_POLICIES = [
    ("selective_fragile_wait180", 180, "fragile_low_p_high_recross"),
    ("selective_fragile_wait240", 240, "fragile_low_p_high_recross"),
    ("selective_nearstrike_wait180", 180, "nearstrike_low_p"),
    ("selective_rmt_memory_gap_wait180", 180, "rmt_memory_gap"),
    ("selective_rmt_repetition_gap_wait180", 180, "rmt_repetition_gap"),
    ("selective_rmt_memory_gap_wait180_rmtedge02", 180, "rmt_memory_gap_confirm_edge02"),
    ("selective_rmt_repetition_gap_wait180_rmtedge02", 180, "rmt_repetition_gap_confirm_edge02"),
    ("selective_rmt_memory_gap_wait180_rmtedge02_or_opp", 180, "rmt_memory_gap_confirm_edge02_or_opp"),
    ("selective_rmt_repetition_gap_wait180_rmtedge02_or_opp", 180, "rmt_repetition_gap_confirm_edge02_or_opp"),
    ("selective_rmt_memory_gap_wait240_rmtedge02_or_opp", 240, "rmt_memory_gap_confirm_edge02_or_opp"),
    ("selective_rmt_repetition_gap_wait240_rmtedge02_or_opp", 240, "rmt_repetition_gap_confirm_edge02_or_opp"),
    ("weakraw_rmt_memory_margin02_wait240_or_opp", 240, "weakraw_rmt_memory_margin02_or_opp"),
    ("weakraw_rmt_repetition_margin02_wait240_or_opp", 240, "weakraw_rmt_repetition_margin02_or_opp"),
]


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
        return float(value)
    except (TypeError, ValueError):
        return None


def approval_events() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for event in read_events():
        if event.get("event_type") != "mushroom_v28_approved":
            continue
        market = str(event.get("market") or "")
        side = str(event.get("side") or event.get("mushroom_v28_side") or "").lower()
        ts = parse_ts(event.get("ts_wall"))
        if market and side in {"yes", "no"} and ts is not None:
            rows.append({"market": market, "side": side, "ts": ts, "event": event})
    return sorted(rows, key=lambda row: row["ts"])


def raw_edge(row: dict[str, Any]) -> float | None:
    ask = as_float(row.get("ask_prob"))
    if ask is None:
        return None
    return p_raw(row) - ask


def qualifies_same_side(row: dict[str, Any], side: str) -> bool:
    edge = raw_edge(row)
    return (
        str(row.get("side") or "").lower() == side
        and base_tradeable(row)
        and p_raw(row) >= 0.50
        and edge is not None
        and edge >= 0.0
    )


def is_fragile(base: dict[str, Any], mode: str) -> bool:
    p = p_raw(base)
    recross = as_float(base.get("recross_hazard_score")) or 0.0
    abs_d = as_float(base.get("abs_d_sigma")) or 999.0
    edge = raw_edge(base) or 0.0
    if mode == "fragile_low_p_high_recross":
        return p < 0.60 and recross >= 0.75 and abs_d <= 0.35
    if mode == "nearstrike_low_p":
        return p < 0.60 and abs_d <= 0.25 and edge < 0.12
    if mode in {"rmt_memory_gap", "rmt_memory_gap_confirm_edge02", "rmt_memory_gap_confirm_edge02_or_opp"}:
        return (
            str(base.get("spectral_tag") or "") == "spectral_dominant_factor"
            and int(base.get("market_side_observation_index") or 0) == 0
            and p < 0.60
            and abs_d <= 0.25
            and recross >= 0.75
            and p - p_rmt_memory_gate(base) >= 0.025
        )
    if mode in {"rmt_repetition_gap", "rmt_repetition_gap_confirm_edge02", "rmt_repetition_gap_confirm_edge02_or_opp"}:
        return (
            str(base.get("spectral_tag") or "") == "spectral_dominant_factor"
            and int(base.get("market_side_observation_index") or 0) == 0
            and p < 0.60
            and abs_d <= 0.25
            and recross >= 0.75
            and p - p_rmt_repetition_forget(base) >= 0.025
        )
    if mode in {"weakraw_rmt_memory_margin02_or_opp", "weakraw_rmt_repetition_margin02_or_opp"}:
        return p < 0.60
    raise ValueError(f"unknown selective mode: {mode}")


def qualifies_confirmed(row: dict[str, Any], side: str, mode: str) -> bool:
    if not qualifies_same_side(row, side):
        return False
    ask = as_float(row.get("ask_prob"))
    if ask is None:
        return False
    if mode in {"rmt_memory_gap_confirm_edge02", "rmt_memory_gap_confirm_edge02_or_opp"}:
        return p_rmt_memory_gate(row) - ask >= 0.02
    if mode in {"rmt_repetition_gap_confirm_edge02", "rmt_repetition_gap_confirm_edge02_or_opp"}:
        return p_rmt_repetition_forget(row) - ask >= 0.02
    if mode == "weakraw_rmt_memory_margin02_or_opp":
        return p_rmt_memory_gate(row) - ask >= 0.02
    if mode == "weakraw_rmt_repetition_margin02_or_opp":
        return p_rmt_repetition_forget(row) - ask >= 0.02
    return True


def allow_opposite_follow(mode: str) -> bool:
    return mode in {
        "rmt_memory_gap_confirm_edge02_or_opp",
        "rmt_repetition_gap_confirm_edge02_or_opp",
        "weakraw_rmt_memory_margin02_or_opp",
        "weakraw_rmt_repetition_margin02_or_opp",
    }


def row_at_or_after_opposite(
    rows: list[dict[str, Any]],
    opposite: dict[str, Any],
    market: str,
) -> dict[str, Any] | None:
    side = str(opposite.get("side") or "").lower()
    opposite_ts = parse_ts(opposite.get("ts_wall"))
    if opposite_ts is None:
        return None
    for row in rows:
        row_ts = parse_ts(row.get("ts_wall"))
        if (
            str(row.get("market") or "") == market
            and str(row.get("side") or "").lower() == side
            and row_ts is not None
            and row_ts >= opposite_ts
            and base_tradeable(row)
        ):
            return row
    return None


def opposite_approval_between(
    approvals: list[dict[str, Any]],
    market: str,
    side: str,
    start: Any,
    end: Any,
) -> dict[str, Any] | None:
    opposite = "no" if side == "yes" else "yes"
    for row in approvals:
        if row["market"] == market and row["side"] == opposite and start <= row["ts"] <= end:
            event = row["event"]
            return {
                "ts_wall": event.get("ts_wall"),
                "side": row["side"],
                "p_side": as_float(event.get("mushroom_v28_p_side")),
                "ask_cents": as_float(event.get("mushroom_v28_ask_cents")),
                "edge_cents": as_float(event.get("mushroom_v28_edge_cents")),
            }
    return None


def selected_detail(row: dict[str, Any], policy: str, base: dict[str, Any]) -> dict[str, Any]:
    ask = as_float(row.get("ask_prob")) or 0.0
    p = clamp_prob(p_raw(row) + 0.05)
    outcome = None if row.get("side_won") is None else (1.0 if row.get("side_won") is True else 0.0)
    brier = None if outcome is None else (p - outcome) ** 2
    raw_brier = None if outcome is None else (p_raw(row) - outcome) ** 2
    net = None
    if row.get("gross_cents") is not None:
        net = float(row.get("gross_cents") or 0.0) - estimate_entry_fee_cents(row)
    base_ts = parse_ts(base.get("ts_wall"))
    row_ts = parse_ts(row.get("ts_wall"))
    return {
        "policy": policy,
        "market": row.get("market"),
        "ts_wall": row.get("ts_wall"),
        "source": row.get("source"),
        "delay_seconds": None if base_ts is None or row_ts is None else (row_ts - base_ts).total_seconds(),
        "side": row.get("side"),
        "p_raw": p_raw(row),
        "p_rmt_memory_gate": p_rmt_memory_gate(row),
        "p_rmt_repetition_forget": p_rmt_repetition_forget(row),
        "p_plus05": p,
        "ask_prob": ask,
        "raw_edge_prob": p_raw(row) - ask,
        "seconds_to_close": row.get("seconds_to_close"),
        "side_won": row.get("side_won"),
        "net_gross_cents_after_entry_fee": net,
        "brier_plus05": brier,
        "logloss_plus05": None if outcome is None else logloss(p, outcome),
        "brier_delta_plus05_minus_raw": None if brier is None or raw_brier is None else brier - raw_brier,
        "logloss_delta_plus05_minus_raw": None if outcome is None else logloss(p, outcome) - logloss(p_raw(row), outcome),
    }


def build_candidate_rows(
    base_rows: list[dict[str, Any]],
    observations: list[dict[str, Any]],
    approvals: list[dict[str, Any]],
    wait_seconds: int,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    selected: list[dict[str, Any]] = []
    blocked: list[dict[str, Any]] = []
    by_market = {}
    for row in observations:
        by_market.setdefault(str(row.get("market") or ""), []).append(row)
    for base in base_rows:
        market = str(base.get("market") or "")
        side = str(base.get("side") or "").lower()
        base_ts = parse_ts(base.get("ts_wall"))
        if base_ts is None:
            continue
        confirm_after = base_ts + timedelta(seconds=wait_seconds)
        rows = sorted(by_market.get(market, []), key=lambda item: str(item.get("ts_wall") or ""))
        candidates = [row for row in rows if (parse_ts(row.get("ts_wall")) or base_ts) >= confirm_after]
        opposite = opposite_approval_between(approvals, market, side, base_ts, confirm_after)
        if opposite is not None:
            blocked.append({"market": market, "base_side": side, "reason": "opposite_approval_before_confirm", "opposite": opposite, "base": base})
            continue
        kept = next((row for row in candidates if qualifies_same_side(row, side)), None)
        if kept is None:
            blocked.append({"market": market, "base_side": side, "reason": "same_side_not_confirmed", "base": base})
            continue
        selected.append(selected_detail(kept, f"path_confirm_wait{wait_seconds}", base))
    return selected, blocked


def build_selective_candidate_rows(
    base_rows: list[dict[str, Any]],
    observations: list[dict[str, Any]],
    approvals: list[dict[str, Any]],
    policy: str,
    wait_seconds: int,
    mode: str,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    selected: list[dict[str, Any]] = []
    blocked: list[dict[str, Any]] = []
    by_market = {}
    for row in observations:
        by_market.setdefault(str(row.get("market") or ""), []).append(row)
    for base in base_rows:
        market = str(base.get("market") or "")
        side = str(base.get("side") or "").lower()
        base_ts = parse_ts(base.get("ts_wall"))
        if base_ts is None:
            continue
        if not is_fragile(base, mode):
            selected.append(selected_detail(base, policy, base))
            continue
        confirm_after = base_ts + timedelta(seconds=wait_seconds)
        rows = sorted(by_market.get(market, []), key=lambda item: str(item.get("ts_wall") or ""))
        candidates = [row for row in rows if (parse_ts(row.get("ts_wall")) or base_ts) >= confirm_after]
        opposite = opposite_approval_between(approvals, market, side, base_ts, confirm_after)
        if opposite is not None:
            if allow_opposite_follow(mode):
                flipped = row_at_or_after_opposite(rows, opposite, market)
                if flipped is not None:
                    selected.append(selected_detail(flipped, policy, base))
                    continue
            blocked.append({
                "market": market,
                "base_side": side,
                "reason": "fragile_opposite_approval_before_confirm",
                "opposite": opposite,
                "base": base,
                "mode": mode,
            })
            continue
        kept = next((row for row in candidates if qualifies_confirmed(row, side, mode)), None)
        if kept is None:
            blocked.append({
                "market": market,
                "base_side": side,
                "reason": "fragile_same_side_not_confirmed",
                "base": base,
                "mode": mode,
            })
            continue
        selected.append(selected_detail(kept, policy, base))
    return selected, blocked


def summarize(policy: str, rows: list[dict[str, Any]], blocked: list[dict[str, Any]], denominator: int) -> dict[str, Any]:
    settled = [row for row in rows if row.get("side_won") is not None]
    brier_deltas = [float(row["brier_delta_plus05_minus_raw"]) for row in settled if row.get("brier_delta_plus05_minus_raw") is not None]
    logloss_deltas = [float(row["logloss_delta_plus05_minus_raw"]) for row in settled if row.get("logloss_delta_plus05_minus_raw") is not None]
    briers = [float(row["brier_plus05"]) for row in settled if row.get("brier_plus05") is not None]
    loglosses = [float(row["logloss_plus05"]) for row in settled if row.get("logloss_plus05") is not None]
    net = sum(float(row.get("net_gross_cents_after_entry_fee") or 0.0) for row in settled)
    return {
        "policy": policy,
        "entries": len(rows),
        "settled": len(settled),
        "wins": sum(1 for row in settled if row.get("side_won") is True),
        "losses": sum(1 for row in settled if row.get("side_won") is False),
        "approved_entry_count": sum(1 for row in rows if row.get("source") == "approved_entry"),
        "added_reject_count": sum(1 for row in rows if row.get("source") == "rejected_actionable"),
        "simulated_share": (
            sum(1 for row in rows if row.get("source") == "rejected_actionable") / len(rows)
            if rows
            else None
        ),
        "coverage_pct": len(rows) / denominator * 100.0 if denominator else None,
        "net_cents_after_entry_fee": net,
        "avg_brier": sum(briers) / len(briers) if briers else None,
        "avg_logloss": sum(loglosses) / len(loglosses) if loglosses else None,
        "brier_delta_mean_plus05_minus_raw": sum(brier_deltas) / len(brier_deltas) if brier_deltas else None,
        "logloss_delta_mean_plus05_minus_raw": sum(logloss_deltas) / len(logloss_deltas) if logloss_deltas else None,
        "blocked_count": len(blocked),
        "blocked_reasons": reason_counts(blocked),
        "actual_only": summarize_slice([row for row in rows if row.get("source") == "approved_entry"]),
        "simulated_only": summarize_slice([row for row in rows if row.get("source") == "rejected_actionable"]),
        "rows": rows,
        "blocked": blocked,
    }


def summarize_slice(rows: list[dict[str, Any]]) -> dict[str, Any]:
    settled = [row for row in rows if row.get("side_won") is not None]
    net = sum(float(row.get("net_gross_cents_after_entry_fee") or 0.0) for row in settled)
    brier_deltas = [float(row["brier_delta_plus05_minus_raw"]) for row in settled if row.get("brier_delta_plus05_minus_raw") is not None]
    return {
        "entries": len(rows),
        "settled": len(settled),
        "wins": sum(1 for row in settled if row.get("side_won") is True),
        "losses": sum(1 for row in settled if row.get("side_won") is False),
        "net_cents_after_entry_fee": net,
        "brier_delta_mean_plus05_minus_raw": sum(brier_deltas) / len(brier_deltas) if brier_deltas else None,
    }


def reason_counts(rows: list[dict[str, Any]]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for row in rows:
        reason = str(row.get("reason") or "unknown")
        counts[reason] = counts.get(reason, 0) + 1
    return counts


def build_report() -> dict[str, Any]:
    state = load_json(STATE_JSON)
    freeze_dt = parse_ts(state.get("freeze_ts"))
    observations = enrich_state(attach_regime_rows(observation_pool()))
    timing = market_timing(freeze_dt)
    forward_markets = set(timing["clean_forward_markets"])
    base_rows = [
        row for row in selected_rows(observations, "v28_raw", p_raw, 0.50, 0.00)
        if str(row.get("market") or "") in forward_markets
    ]
    forward_denominator = len(forward_markets)
    approvals = approval_events()
    summaries = []
    for wait in WAIT_SECONDS:
        rows, blocked = build_candidate_rows(base_rows, observations, approvals, wait)
        summaries.append(summarize(f"path_confirm_wait{wait}", rows, blocked, forward_denominator))
    for policy, wait, mode in SELECTIVE_POLICIES:
        rows, blocked = build_selective_candidate_rows(base_rows, observations, approvals, policy, wait, mode)
        summaries.append(summarize(policy, rows, blocked, forward_denominator))
    return {
        "freeze_ts": state.get("freeze_ts"),
        "forward_market_denominator": forward_denominator,
        "base_entries": len(base_rows),
        "base_markets": [str(row.get("market") or "") for row in base_rows],
        "summaries": summaries,
    }


def fmt(value: Any) -> str:
    if value is None:
        return "None"
    if isinstance(value, float):
        return f"{value:.6f}"
    return str(value)


def write_report(report: dict[str, Any]) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8")
    lines = [
        "# v28 Path-Confirmed Entry Candidates",
        "",
        "Live-realistic confirmation challengers for broad raw-p50 entries. These wait briefly and require the same side to remain eligible without opposite v28 approval.",
        "",
        f"- Freeze timestamp UTC: `{report.get('freeze_ts')}`",
        f"- Forward denominator/base entries: `{report.get('forward_market_denominator')}/{report.get('base_entries')}`",
        "",
        "| policy | entries | settled | W/L | actual/sim | sim share | coverage | net c | brier | brier d | logloss d | blocked | reasons |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|",
    ]
    for row in report.get("summaries") or []:
        lines.append(
            f"| {row.get('policy')} | {row.get('entries')} | {row.get('settled')} | {row.get('wins')}/{row.get('losses')} | "
            f"{row.get('approved_entry_count')}/{row.get('added_reject_count')} | {fmt(row.get('simulated_share'))} | "
            f"{fmt(row.get('coverage_pct'))} | {fmt(row.get('net_cents_after_entry_fee'))} | {fmt(row.get('avg_brier'))} | "
            f"{fmt(row.get('brier_delta_mean_plus05_minus_raw'))} | {fmt(row.get('logloss_delta_mean_plus05_minus_raw'))} | "
            f"{row.get('blocked_count')} | {row.get('blocked_reasons')} |"
        )
    lines.extend(["", "## Selected Rows", ""])
    for summary in report.get("summaries") or []:
        lines.extend(["", f"### {summary.get('policy')}", ""])
        lines.append("| market | source | delay s | side | p raw | p rmt gate | p rmt rep | ask | won | net c |")
        lines.append("|---|---|---:|---|---:|---:|---:|---:|---|---:|")
        for row in summary.get("rows") or []:
            lines.append(
                f"| {row.get('market')} | {row.get('source')} | {fmt(row.get('delay_seconds'))} | {row.get('side')} | "
                f"{fmt(row.get('p_raw'))} | {fmt(row.get('p_rmt_memory_gate'))} | "
                f"{fmt(row.get('p_rmt_repetition_forget'))} | {fmt(row.get('ask_prob'))} | {row.get('side_won')} | "
                f"{fmt(row.get('net_gross_cents_after_entry_fee'))} |"
            )
    lines.extend(["", "## Actual-vs-Simulated Slices", ""])
    lines.append("| policy | actual entries | actual settled | actual W/L | actual net c | sim entries | sim settled | sim W/L | sim net c |")
    lines.append("|---|---:|---:|---:|---:|---:|---:|---:|---:|")
    for summary in report.get("summaries") or []:
        actual = summary.get("actual_only") or {}
        sim = summary.get("simulated_only") or {}
        lines.append(
            f"| {summary.get('policy')} | {actual.get('entries')} | {actual.get('settled')} | "
            f"{actual.get('wins')}/{actual.get('losses')} | {fmt(actual.get('net_cents_after_entry_fee'))} | "
            f"{sim.get('entries')} | {sim.get('settled')} | {sim.get('wins')}/{sim.get('losses')} | "
            f"{fmt(sim.get('net_cents_after_entry_fee'))} |"
        )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    report = build_report()
    write_report(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
