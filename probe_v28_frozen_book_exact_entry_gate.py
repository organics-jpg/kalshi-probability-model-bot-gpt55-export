"""Frozen book-exact entry gate for broad v28/RMT candidates.

Research-only; no live bot changes or orders.

The broad RMT/forgetting candidates often lose money even when calibration
improves. One physically distinct subset is when the effective FV has fully
forgotten v28 and equals the executable book probability. This freezes that
subset as an entry gate and requires future rows to prove whether it is useful
or just historical book-favorite luck.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from probe_v28_book_favorite_edge_diagnostic import p_eff_mode
from probe_v28_rmt_forgetting_entry_bakeoff import build_report as build_entry_bakeoff_report
from probe_v28_shadow_entry_policy_bakeoff import observation_pool


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
STATE_JSON = OUT_DIR / "v28_frozen_book_exact_entry_gate_state.json"
OUT_JSON = OUT_DIR / "v28_frozen_book_exact_entry_gate_latest.json"
OUT_MD = OUT_DIR / "v28_frozen_book_exact_entry_gate_latest.md"

POLICIES = [
    {
        "policy": "first_side_raw_later_book_p58_edge0",
        "role": "lower-threshold book-collapse gate",
        "physics": "When stale v28 geometry is fully forgotten and the effective probability equals the book, require book-favorite state to carry the trade.",
    },
    {
        "policy": "first_side_raw_later_book_p60_edge0",
        "role": "primary book-collapse gate",
        "physics": "Same as p58, but only when the executable book favorite is at least 60%.",
    },
    {
        "policy": "rmt_repetition_forget_p58_edge0",
        "role": "RMT repetition book-collapse gate",
        "physics": "Only accept repeated-side/RMT states after the model has fully collapsed to book probability.",
    },
    {
        "policy": "rmt_repetition_forget_p60_edge0",
        "role": "stricter RMT repetition book-collapse gate",
        "physics": "Same as p58 RMT repetition gate, with at least 60% book probability.",
    },
]


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


def as_float(value: Any) -> float | None:
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def load_or_create_state() -> dict[str, Any]:
    if STATE_JSON.exists():
        try:
            payload = json.loads(STATE_JSON.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            payload = {}
        if isinstance(payload, dict) and payload.get("freeze_ts_utc"):
            return payload
    payload = {
        "freeze_ts_utc": utc_now_iso(),
        "candidate": "book_exact_entry_gate",
        "policies": POLICIES,
        "rule": {
            "mode": "book_exact",
            "one_entry_per_market": True,
            "source": "v28_rmt_forgetting_entry_bakeoff selected rows",
        },
        "promotion_floor": {
            "min_settled": 30,
            "min_coverage_pct": 75.0,
            "max_coverage_pct": 90.0,
            "must_be_net_positive": True,
            "max_simulated_share": 0.35,
        },
        "physics": (
            "If the FV estimate has fully collapsed to executable book probability, "
            "the trade is not raw model alpha. It is a book/state regime bet and "
            "must show forward edge after fees without relying on rejected-row simulation."
        ),
    }
    STATE_JSON.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return payload


def clean_forward_markets(freeze_dt: datetime | None) -> set[str]:
    if freeze_dt is None:
        return set()
    first_seen: dict[str, datetime] = {}
    post_freeze: set[str] = set()
    for row in observation_pool():
        market = str(row.get("market") or "")
        ts = parse_ts(row.get("ts_wall"))
        if not market or ts is None:
            continue
        if market not in first_seen or ts < first_seen[market]:
            first_seen[market] = ts
        if ts >= freeze_dt:
            post_freeze.add(market)
    return {market for market, first_ts in first_seen.items() if first_ts >= freeze_dt}


def selected_book_exact_rows(policy: str, rows: list[dict[str, Any]], markets: set[str] | None = None) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for row in rows:
        if row.get("policy") != policy:
            continue
        if p_eff_mode(row) != "book_exact":
            continue
        market = str(row.get("market") or "")
        if markets is not None and market not in markets:
            continue
        out.append(row)
    return sorted(out, key=lambda item: str(item.get("ts_wall") or ""))


def summarize(policy: str, rows: list[dict[str, Any]], denominator: int, floor: dict[str, Any]) -> dict[str, Any]:
    settled = [row for row in rows if row.get("side_won") is not None]
    resolved = [row for row in rows if row.get("gross_cents") is not None]
    net = sum(float(row.get("net_gross_cents_after_entry_fee") or row.get("gross_cents") or 0.0) for row in resolved)
    gross = sum(float(row.get("gross_cents") or 0.0) for row in resolved)
    entries = len(rows)
    added = sum(1 for row in rows if row.get("source") == "rejected_actionable")
    sim_share = added / entries if entries else None
    coverage = (entries / denominator * 100.0) if denominator else None
    blockers: list[str] = []
    if len(settled) < int(floor.get("min_settled") or 30):
        blockers.append("settled_lt_30")
    if coverage is None or coverage < float(floor.get("min_coverage_pct") or 75.0):
        blockers.append("coverage_too_low")
    if coverage is not None and coverage > float(floor.get("max_coverage_pct") or 90.0):
        blockers.append("coverage_too_high")
    if net <= 0.0:
        blockers.append("net_not_positive")
    if sim_share is None or sim_share > float(floor.get("max_simulated_share") or 0.35):
        blockers.append("simulated_share_gt_35pct")
    return {
        "policy": policy,
        "entries": entries,
        "resolved": len(resolved),
        "settled": len(settled),
        "wins": sum(1 for row in settled if row.get("side_won") is True),
        "losses": sum(1 for row in settled if row.get("side_won") is False),
        "coverage_pct": coverage,
        "gross_cents": gross,
        "net_cents_after_entry_fee": net,
        "avg_net_cents_after_entry_fee": net / len(resolved) if resolved else None,
        "approved_entry_count": sum(1 for row in rows if row.get("source") == "approved_entry"),
        "added_reject_count": added,
        "simulated_share": sim_share,
        "blockers": blockers,
        "promotion_ready": not blockers,
    }


def row_preview(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    preview = []
    for row in rows[-12:]:
        preview.append({
            "market": row.get("market"),
            "ts_wall": row.get("ts_wall"),
            "side": row.get("side"),
            "source": row.get("source"),
            "p_eff": row.get("p_eff"),
            "ask_prob": row.get("ask_prob"),
            "p_side": row.get("p_side"),
            "gross_cents": row.get("gross_cents"),
            "net_cents_after_entry_fee": row.get("net_gross_cents_after_entry_fee"),
            "side_won": row.get("side_won"),
        })
    return preview


def build_report() -> dict[str, Any]:
    state = load_or_create_state()
    freeze_dt = parse_ts(state.get("freeze_ts_utc"))
    payload = build_entry_bakeoff_report()
    rows = payload.get("rows") if isinstance(payload.get("rows"), list) else []
    forward_markets = clean_forward_markets(freeze_dt)
    floor = state.get("promotion_floor") or {}
    diagnostic_denominator = int(payload.get("watched_markets") or 0)
    forward_denominator = len(forward_markets)
    summaries = []
    for item in state.get("policies") or POLICIES:
        policy = item["policy"]
        diagnostic_rows = selected_book_exact_rows(policy, rows)
        future_rows = selected_book_exact_rows(policy, rows, forward_markets)
        summaries.append({
            "policy": policy,
            "role": item.get("role"),
            "physics": item.get("physics"),
            "diagnostic": summarize(policy, diagnostic_rows, diagnostic_denominator, floor),
            "future": summarize(policy, future_rows, forward_denominator, floor),
            "future_rows": row_preview(future_rows),
        })
    return {
        "freeze": state,
        "forward_denominator_markets": forward_denominator,
        "forward_markets": sorted(forward_markets),
        "diagnostic_denominator_markets": diagnostic_denominator,
        "summaries": summaries,
        "any_promotion_ready": any((row.get("future") or {}).get("promotion_ready") for row in summaries),
    }


def fmt(value: Any) -> str:
    if value is None:
        return "None"
    if isinstance(value, float):
        return f"{value:.6f}"
    return str(value)


def write_md(report: dict[str, Any]) -> None:
    lines = [
        "# v28 Frozen Book-Exact Entry Gate",
        "",
        "Shadow-only validator. A candidate row counts only when the effective FV equals executable book probability.",
        "",
        f"- Freeze timestamp UTC: `{(report.get('freeze') or {}).get('freeze_ts_utc')}`",
        f"- Forward denominator markets: `{report.get('forward_denominator_markets')}`",
        f"- Diagnostic denominator markets: `{report.get('diagnostic_denominator_markets')}`",
        f"- Any promotion ready: `{report.get('any_promotion_ready')}`",
        "",
        "## Scorecard",
        "",
        "| policy | window | entries | settled | W/L | coverage | net c | avg net c | actual/sim | sim share | blockers |",
        "|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---|",
    ]
    for row in report.get("summaries") or []:
        for window in ["diagnostic", "future"]:
            bucket = row.get(window) or {}
            lines.append(
                f"| {row.get('policy')} | {window} | {bucket.get('entries')} | {bucket.get('settled')} | "
                f"{bucket.get('wins')}/{bucket.get('losses')} | {fmt(bucket.get('coverage_pct'))} | "
                f"{fmt(bucket.get('net_cents_after_entry_fee'))} | {fmt(bucket.get('avg_net_cents_after_entry_fee'))} | "
                f"{bucket.get('approved_entry_count')}/{bucket.get('added_reject_count')} | "
                f"{fmt(bucket.get('simulated_share'))} | {', '.join(bucket.get('blockers') or []) or 'none'} |"
            )
    lines.extend(["", "## Physics", ""])
    for row in report.get("summaries") or []:
        lines.append(f"- `{row.get('policy')}`: {row.get('physics')}")
    lines.extend(["", "## Future Row Preview", ""])
    for row in report.get("summaries") or []:
        lines.append(f"### {row.get('policy')}")
        preview = row.get("future_rows") or []
        if not preview:
            lines.append("No future rows yet.")
            continue
        lines.append("| market | ts | side | source | p_eff | raw p | ask | won | net c |")
        lines.append("|---|---|---|---|---:|---:|---:|---|---:|")
        for item in preview:
            lines.append(
                f"| {item.get('market')} | {item.get('ts_wall')} | {item.get('side')} | "
                f"{item.get('source')} | {fmt(item.get('p_eff'))} | {fmt(item.get('p_side'))} | "
                f"{fmt(item.get('ask_prob'))} | {item.get('side_won')} | {fmt(item.get('net_cents_after_entry_fee'))} |"
            )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    report = build_report()
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8")
    write_md(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
