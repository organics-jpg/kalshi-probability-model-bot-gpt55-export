"""Forward monitor for the v28 calibrated FV candidate.

Tracks the frozen raw-entry + calibrated-probability candidate through clean
forward markets, including pending rows and missed markets. This is a monitor,
not a promotion rule.

Research-only; no live bot changes or orders.
"""
from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any

from probe_v28_entry_conditioned_data_quality import market_close_guess
from probe_v28_frozen_forward_candidates import market_timing, parse_ts
from probe_v28_noise_floor_shrinkage_candidates import selected_rows
from probe_v28_raw_entry_calibrated_probability import OVERLAYS
from probe_v28_rmt_regime_diagnostic import attach_regime_rows
from probe_v28_shadow_entry_policy_bakeoff import observation_pool
from probe_v28_state_aware_fv_candidates import enrich_state, p_raw


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
STATE_JSON = OUT_DIR / "v28_frozen_raw_entry_calibrated_probability_state.json"
OUT_JSON = OUT_DIR / "v28_calibrated_fv_forward_monitor_latest.json"
OUT_MD = OUT_DIR / "v28_calibrated_fv_forward_monitor_latest.md"


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


def first_market_rows(rows: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    picked: dict[str, dict[str, Any]] = {}
    for row in sorted(rows, key=lambda item: str(item.get("ts_wall") or "")):
        market = str(row.get("market") or "")
        if market and market not in picked:
            picked[market] = row
    return picked


def row_detail(row: dict[str, Any] | None) -> dict[str, Any] | None:
    if row is None:
        return None
    market = str(row.get("market") or "")
    raw_p = as_float(row.get("p_side"))
    plus05 = None if raw_p is None else OVERLAYS["entry_conditioned_plus05_probability"](row)
    ask = as_float(row.get("ask_prob"))
    close_time = market_close_guess(market)
    side_won = row.get("side_won")
    outcome = None if side_won is None else (1.0 if side_won is True else 0.0)
    raw_brier = None if raw_p is None or outcome is None else (raw_p - outcome) ** 2
    plus05_brier = None if plus05 is None or outcome is None else (plus05 - outcome) ** 2
    raw_logloss = None if raw_p is None or outcome is None else logloss(raw_p, outcome)
    plus05_logloss = None if plus05 is None or outcome is None else logloss(plus05, outcome)
    return {
        "market": row.get("market"),
        "close_time_utc": close_time.isoformat() if close_time is not None else None,
        "ts_wall": row.get("ts_wall"),
        "source": row.get("source"),
        "side": row.get("side"),
        "reason": row.get("reason"),
        "p_raw": raw_p,
        "p_plus05": plus05,
        "ask_prob": ask,
        "raw_edge_prob": None if raw_p is None or ask is None else raw_p - ask,
        "seconds_to_close": row.get("seconds_to_close"),
        "abs_d_sigma": row.get("abs_d_sigma"),
        "recross_hazard_score": row.get("recross_hazard_score"),
        "spectral_tag": row.get("spectral_tag"),
        "side_won": side_won,
        "net_gross_cents_after_entry_fee": row.get("net_gross_cents_after_entry_fee"),
        "raw_brier": raw_brier,
        "plus05_brier": plus05_brier,
        "brier_delta_plus05_minus_raw": None if raw_brier is None or plus05_brier is None else plus05_brier - raw_brier,
        "raw_logloss": raw_logloss,
        "plus05_logloss": plus05_logloss,
        "logloss_delta_plus05_minus_raw": None if raw_logloss is None or plus05_logloss is None else plus05_logloss - raw_logloss,
    }


def clamp_prob(value: float) -> float:
    return max(0.000001, min(0.999999, value))


def logloss(p: float, outcome: float) -> float:
    p = clamp_prob(p)
    return -(outcome * math.log(p) + (1.0 - outcome) * math.log(1.0 - p))


def build_report() -> dict[str, Any]:
    state = load_json(STATE_JSON)
    freeze_dt = parse_ts(state.get("freeze_ts"))
    rows = enrich_state(attach_regime_rows(observation_pool()))
    timing = market_timing(freeze_dt)
    clean_markets = set(timing["clean_forward_markets"])
    selected = selected_rows(rows, "v28_raw", p_raw, 0.50, 0.00)
    selected_by_market = {str(row.get("market") or ""): row for row in selected}
    first_by_market = first_market_rows(rows)
    clean_details = []
    now_utc = latest_observation_time(rows)
    for market in sorted(clean_markets):
        selected_row = selected_by_market.get(market)
        selected_detail = row_detail(selected_row)
        if selected_detail is not None:
            selected_detail["close_state"] = close_state(selected_detail.get("close_time_utc"), selected_detail.get("side_won"), now_utc)
            selected_detail["seconds_to_or_since_close_at_last_observation"] = seconds_to_or_since_close(selected_detail.get("close_time_utc"), now_utc)
        clean_details.append({
            "market": market,
            "selected": selected_row is not None,
            "selected_row": selected_detail,
            "first_observed_row": row_detail(first_by_market.get(market)),
        })
    selected_clean = [item for item in clean_details if item["selected"]]
    settled = [item for item in selected_clean if item.get("selected_row", {}).get("side_won") is not None]
    pending = [item for item in selected_clean if item.get("selected_row", {}).get("side_won") is None]
    misses = [item for item in clean_details if not item["selected"]]
    return {
        "freeze_ts": state.get("freeze_ts"),
        "clean_forward_market_count": len(clean_markets),
        "excluded_in_progress_markets": sorted(timing["excluded_in_progress_markets"]),
        "post_freeze_observed_markets": sorted(timing["post_freeze_observed_markets"]),
        "selected_clean_count": len(selected_clean),
        "settled_selected_count": len(settled),
        "pending_selected_count": len(pending),
        "missed_clean_count": len(misses),
        "coverage_pct": len(selected_clean) / len(clean_markets) * 100.0 if clean_markets else None,
        "selected_net_cents": sum(float((item.get("selected_row") or {}).get("net_gross_cents_after_entry_fee") or 0.0) for item in settled),
        "calibration_delta": calibration_delta(settled),
        "selected_win_loss": {
            "wins": sum(1 for item in settled if (item.get("selected_row") or {}).get("side_won") is True),
            "losses": sum(1 for item in settled if (item.get("selected_row") or {}).get("side_won") is False),
        },
        "clean_details": clean_details,
        "pending_details": pending,
        "miss_details": misses,
        "latest_observation_time": now_utc.isoformat() if now_utc is not None else None,
    }


def latest_observation_time(rows: list[dict[str, Any]]) -> Any:
    times = [parse_ts(row.get("ts_wall")) for row in rows]
    times = [ts for ts in times if ts is not None]
    return max(times) if times else None


def seconds_to_or_since_close(close_iso: Any, now_utc: Any) -> float | None:
    if close_iso is None or now_utc is None:
        return None
    close_dt = parse_ts(close_iso)
    if close_dt is None:
        return None
    return (close_dt - now_utc).total_seconds()


def close_state(close_iso: Any, side_won: Any, now_utc: Any) -> str:
    if side_won is not None:
        return "settled"
    seconds = seconds_to_or_since_close(close_iso, now_utc)
    if seconds is None:
        return "unknown_close"
    if seconds > 0:
        return "pre_close_pending"
    return "post_close_unsettled"


def calibration_delta(settled_items: list[dict[str, Any]]) -> dict[str, Any]:
    rows = [item.get("selected_row") or {} for item in settled_items]
    return {
        "settled": len(rows),
        "raw_brier_sum": sum(float(row.get("raw_brier") or 0.0) for row in rows),
        "plus05_brier_sum": sum(float(row.get("plus05_brier") or 0.0) for row in rows),
        "brier_delta_sum": sum(float(row.get("brier_delta_plus05_minus_raw") or 0.0) for row in rows),
        "raw_logloss_sum": sum(float(row.get("raw_logloss") or 0.0) for row in rows),
        "plus05_logloss_sum": sum(float(row.get("plus05_logloss") or 0.0) for row in rows),
        "logloss_delta_sum": sum(float(row.get("logloss_delta_plus05_minus_raw") or 0.0) for row in rows),
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
    wl = report["selected_win_loss"]
    cal = report["calibration_delta"]
    lines = [
        "# v28 Calibrated FV Forward Monitor",
        "",
        "Monitor for clean forward markets after the calibrated-FV freeze. Not a promotion rule.",
        "",
        f"- Freeze timestamp UTC: `{report['freeze_ts']}`",
        f"- Clean forward markets: `{report['clean_forward_market_count']}`",
        f"- Selected/settled/pending/missed: `{report['selected_clean_count']}/{report['settled_selected_count']}/{report['pending_selected_count']}/{report['missed_clean_count']}`",
        f"- Coverage: `{fmt(report['coverage_pct'])}`",
        f"- Settled W/L and net: `{wl['wins']}/{wl['losses']}` / `{fmt(report['selected_net_cents'])}c`",
        f"- Calibration deltas, +5 minus raw Brier/logloss: `{fmt(cal['brier_delta_sum'])}` / `{fmt(cal['logloss_delta_sum'])}`",
        f"- Excluded partial markets: `{report['excluded_in_progress_markets']}`",
        f"- Latest observation time: `{report.get('latest_observation_time')}`",
        "",
        "## Clean Forward Markets",
        "",
        "| market | selected | close state | sec to/since close | side | source | p raw | p +5 | ask | edge | won | net c | brier d | logloss d | first reason |",
        "|---|---|---|---:|---|---|---:|---:|---:|---:|---|---:|---:|---:|---|",
    ]
    for item in report["clean_details"]:
        selected = item.get("selected_row") or {}
        first = item.get("first_observed_row") or {}
        lines.append(
            f"| {item['market']} | {item['selected']} | {selected.get('close_state')} | "
            f"{fmt(selected.get('seconds_to_or_since_close_at_last_observation'))} | "
            f"{selected.get('side')} | {selected.get('source')} | "
            f"{fmt(selected.get('p_raw'))} | {fmt(selected.get('p_plus05'))} | {fmt(selected.get('ask_prob'))} | "
            f"{fmt(selected.get('raw_edge_prob'))} | {selected.get('side_won')} | "
            f"{fmt(selected.get('net_gross_cents_after_entry_fee'))} | "
            f"{fmt(selected.get('brier_delta_plus05_minus_raw'))} | "
            f"{fmt(selected.get('logloss_delta_plus05_minus_raw'))} | {first.get('reason')} |"
        )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    report = build_report()
    write_report(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
