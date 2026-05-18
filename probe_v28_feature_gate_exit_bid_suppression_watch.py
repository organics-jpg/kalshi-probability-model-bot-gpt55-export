"""Frozen watch for feature-gate high-exit-bid suppression.

Research-only; no live bot changes or orders.

The feature-gate exit separator audit found a retrospective observable shape:
high exit bid on selected-side live exits separated winner clips from true
loss-control exits in the current sample. This probe freezes that shape from a
new timestamp and scores only future/post-birth rows as forward evidence.
"""
from __future__ import annotations

import json
from collections import Counter, defaultdict
from datetime import datetime, timezone
from math import floor
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
COUNTERFACTUAL_JSON = OUT_DIR / "v28_feature_gate_live_exit_hold_counterfactual_latest.json"
SEPARATOR_JSON = OUT_DIR / "v28_feature_gate_exit_suppression_separator_latest.json"
EXECUTION_EVENTS = ROOT / "logs" / "live_mushroom_v28_size2" / "execution_events.ndjson"
STATE_JSON = OUT_DIR / "v28_feature_gate_exit_bid_suppression_watch_state.json"
OUT_JSON = OUT_DIR / "v28_feature_gate_exit_bid_suppression_watch_latest.json"
OUT_MD = OUT_DIR / "v28_feature_gate_exit_bid_suppression_watch_latest.md"

MIN_SETTLED = 30
MIN_SUPPRESSED = 30
MIN_FULL_LOSS_CUSHION = 3


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


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def load_or_create_state() -> dict[str, Any]:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    if STATE_JSON.exists():
        payload = load_json(STATE_JSON)
        if payload.get("freeze_ts_utc"):
            return payload
    separator = load_json(SEPARATOR_JSON)
    best = (separator.get("observable_candidate_separators") or [{}])[0]
    state = {
        "freeze_ts_utc": utc_now_iso(),
        "candidate": "feature_gate_exit_bid_min_ge_60_suppress",
        "origin": "Frozen from v28_feature_gate_exit_suppression_separator_latest observable separator.",
        "diagnostic_best_separator": best,
        "exit_bid_min_cents": 60.0,
        "target_candidate": "post_feature_freeze_entry_raw03_recross70_abs075",
        "physics": "A selected-side exit while the bid remains at least 60c can be a transient clip of a still-valuable thesis; low exit bids are more likely true loss-control exits.",
        "research_only": True,
        "strict_forward_note": "Only post_exit_bid_birth rows count as forward evidence.",
    }
    write_json(STATE_JSON, state)
    return state


def fnum(value: Any, default: float = 0.0) -> float:
    if value is None or value == "":
        return default
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def maybe_float(value: Any) -> float | None:
    if value is None or value == "":
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def parse_ts(value: Any) -> datetime | None:
    if not value:
        return None
    try:
        dt = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except ValueError:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def load_events(path: Path, markets: set[str]) -> dict[str, list[dict[str, Any]]]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    if not path.exists():
        return grouped
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            if not line.strip():
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError:
                continue
            market = str(row.get("market") or "")
            if market in markets:
                grouped[market].append(row)
    for market in grouped:
        grouped[market].sort(key=lambda row: str(row.get("ts_wall") or ""))
    return grouped


def event_exit_reason(row: dict[str, Any]) -> str:
    return str(
        row.get("mushroom_v28_exit_reason")
        or row.get("decision_reason")
        or row.get("stop_tier")
        or ""
    )


def selected_exit_events(events: list[dict[str, Any]], side: str) -> list[dict[str, Any]]:
    out = []
    for row in events:
        event_type = str(row.get("event_type") or "")
        if "exit" not in event_type and not str(row.get("client_order_id") or "").startswith("btc15m-exit"):
            continue
        if str(row.get("side") or "") != side:
            continue
        out.append(row)
    return out


def signal_events(events: list[dict[str, Any]], side: str) -> list[dict[str, Any]]:
    return [
        row for row in selected_exit_events(events, side)
        if str(row.get("event_type") or "") in {"exit_signal_seen", "exit_snapshot_built", "exit_plan_built"}
    ]


def values(rows: list[dict[str, Any]], key: str) -> list[float]:
    return [value for value in (maybe_float(row.get(key)) for row in rows) if value is not None]


def stat(values_in: list[float], mode: str) -> float | None:
    if not values_in:
        return None
    if mode == "min":
        return min(values_in)
    if mode == "max":
        return max(values_in)
    return sum(values_in) / len(values_in)


def reason_counts(events: list[dict[str, Any]]) -> dict[str, int]:
    return dict(Counter(event_exit_reason(row) for row in events if event_exit_reason(row)))


def compact_market(row: dict[str, Any], events: list[dict[str, Any]], state: dict[str, Any]) -> dict[str, Any] | None:
    if fnum(row.get("selected_side_qty")) <= 0:
        return None
    side = str(row.get("side") or "")
    signals = signal_events(events, side)
    selected_exits = selected_exit_events(events, side)
    bid_values = values(signals, "mushroom_v28_exit_bid_cents")
    exit_bid_min = stat(bid_values, "min")
    first_exit_ts = parse_ts((signals[0] if signals else selected_exits[0] if selected_exits else {}).get("ts_wall"))
    live = fnum(row.get("selected_live_net_cents"))
    hold = fnum(row.get("selected_hold_to_settlement_net_cents"))
    candidate = hold if exit_bid_min is not None and exit_bid_min >= float(state["exit_bid_min_cents"]) else live
    return {
        "market": row.get("market"),
        "source": row.get("source"),
        "side": side,
        "side_won": bool(row.get("side_won")),
        "first_exit_ts_utc": first_exit_ts.isoformat() if first_exit_ts else None,
        "selected_side_qty": fnum(row.get("selected_side_qty")),
        "selected_side_trade_count": fnum(row.get("selected_side_trade_count")),
        "theory_net_cents": fnum(row.get("theory_net_cents")),
        "live_selected_net_cents": live,
        "hold_to_settlement_net_cents": hold,
        "candidate_net_cents": candidate,
        "delta_vs_live_cents": candidate - live,
        "suppressed": candidate != live,
        "suppression_helpful": candidate > live,
        "entry_fill_avg_cents": maybe_float(row.get("entry_fill_avg_cents")),
        "exit_fill_avg_cents": maybe_float(row.get("exit_fill_avg_cents")),
        "exit_bid_min": exit_bid_min,
        "exit_bid_avg": stat(bid_values, "avg"),
        "exit_p_hold_avg": stat(values(signals, "mushroom_v28_p_hold"), "avg"),
        "exit_fair_drawdown_avg": stat(values(signals, "mushroom_v28_fair_drawdown_cents"), "avg"),
        "exit_hold_net_avg": stat(values(signals, "mushroom_v28_hold_net_cents"), "avg"),
        "exit_reason_counts": reason_counts(selected_exits),
    }


def rows_after(rows: list[dict[str, Any]], freeze_ts: str) -> list[dict[str, Any]]:
    freeze = parse_ts(freeze_ts)
    if freeze is None:
        return []
    out = []
    for row in rows:
        ts = parse_ts(row.get("first_exit_ts_utc"))
        if ts is not None and ts >= freeze:
            out.append(row)
    return out


def summarize(rows: list[dict[str, Any]], strict_forward: bool) -> dict[str, Any]:
    scored = [row for row in rows if fnum(row.get("selected_side_qty")) > 0]
    suppressed = [row for row in scored if row.get("suppressed")]
    helpful = [row for row in suppressed if fnum(row.get("delta_vs_live_cents")) > 0]
    harmful = [row for row in suppressed if fnum(row.get("delta_vs_live_cents")) < 0]
    live_net = sum(fnum(row.get("live_selected_net_cents")) for row in scored)
    candidate_net = sum(fnum(row.get("candidate_net_cents")) for row in scored)
    delta = candidate_net - live_net
    cushion = floor(candidate_net / 100.0) if candidate_net > 0 else 0
    blockers = []
    if len(scored) < MIN_SETTLED:
        blockers.append("settled_lt_30")
    if len(suppressed) < MIN_SUPPRESSED:
        blockers.append("suppressed_decisions_lt_30")
    if candidate_net <= 0:
        blockers.append("net_not_positive")
    if delta <= 0:
        blockers.append("delta_not_positive")
    if harmful:
        blockers.append("suppressed_losers_present")
    if sum(fnum(row.get("delta_vs_live_cents")) for row in harmful) < 0:
        blockers.append("suppressed_loss_control_cost_negative")
    if cushion < MIN_FULL_LOSS_CUSHION:
        blockers.append("full_loss_cushion_lt_3")
    if not strict_forward:
        blockers.append("diagnostic_prefreeze")
    return {
        "settled": len(scored),
        "strict_forward": strict_forward,
        "live_selected_net_cents": live_net,
        "candidate_net_cents": candidate_net,
        "delta_vs_live_cents": delta,
        "live_wins": sum(1 for row in scored if fnum(row.get("live_selected_net_cents")) >= 0),
        "live_losses": sum(1 for row in scored if fnum(row.get("live_selected_net_cents")) < 0),
        "candidate_wins": sum(1 for row in scored if fnum(row.get("candidate_net_cents")) >= 0),
        "candidate_losses": sum(1 for row in scored if fnum(row.get("candidate_net_cents")) < 0),
        "suppressed_exits": len(suppressed),
        "suppressed_helpful": len(helpful),
        "suppressed_harmful": len(harmful),
        "winner_clip_recovered_cents": sum(fnum(row.get("delta_vs_live_cents")) for row in helpful),
        "loss_control_cost_cents": sum(fnum(row.get("delta_vs_live_cents")) for row in harmful),
        "full_loss_cushion_estimate": cushion,
        "source_counts": dict(Counter(str(row.get("source") or "unknown") for row in scored)),
        "suppressed_source_counts": dict(Counter(str(row.get("source") or "unknown") for row in suppressed)),
        "exit_reason_counts": dict(Counter(
            reason for row in suppressed for reason, count in (row.get("exit_reason_counts") or {}).items() for _ in range(int(count or 0))
        )),
        "blockers": blockers,
        "selected_examples": suppressed[:12],
    }


def build_report() -> dict[str, Any]:
    state = load_or_create_state()
    counterfactual = load_json(COUNTERFACTUAL_JSON)
    markets = {str(row.get("market") or "") for row in counterfactual.get("markets") or [] if row.get("market")}
    events = load_events(EXECUTION_EVENTS, markets)
    all_rows = []
    for row in counterfactual.get("markets") or []:
        compact = compact_market(row, events.get(str(row.get("market") or ""), []), state)
        if compact is not None:
            all_rows.append(compact)
    post_rows = rows_after(all_rows, str(state.get("freeze_ts_utc") or ""))
    diagnostic_summary = summarize(all_rows, strict_forward=False)
    post_summary = summarize(post_rows, strict_forward=True)
    report = {
        "generated_at_utc": utc_now_iso(),
        "state": state,
        "counterfactual_source": str(COUNTERFACTUAL_JSON),
        "execution_events_source": str(EXECUTION_EVENTS),
        "lanes": [
            {
                "lane": "diagnostic_feature_gate_exit_bid",
                "summary": diagnostic_summary,
                "rows": all_rows,
            },
            {
                "lane": "post_exit_bid_birth",
                "summary": post_summary,
                "rows": post_rows,
            },
        ],
        "candidate_live_ready": False,
    }
    report["interpretation"] = interpretation(report)
    return report


def interpretation(report: dict[str, Any]) -> list[str]:
    diagnostic = (report.get("lanes") or [{}, {}])[0].get("summary") or {}
    post = (report.get("lanes") or [{}, {}])[1].get("summary") or {}
    return [
        "Research-only frozen watch; it does not change live exits or entries.",
        (
            f"Diagnostic lane: {diagnostic.get('settled')} rows, {diagnostic.get('suppressed_exits')} suppressions, "
            f"delta {diagnostic.get('delta_vs_live_cents')}c, helpful/harmful "
            f"{diagnostic.get('suppressed_helpful')}/{diagnostic.get('suppressed_harmful')}."
        ),
        (
            f"Post-birth lane: {post.get('settled')} rows, {post.get('suppressed_exits')} suppressions, "
            f"delta {post.get('delta_vs_live_cents')}c, blockers {post.get('blockers')}."
        ),
        "Only the post-birth lane can become forward evidence.",
    ]


def fmt(value: Any) -> str:
    if value is None:
        return "None"
    if isinstance(value, float):
        return f"{value:.6f}"
    return str(value)


def write_md(report: dict[str, Any]) -> None:
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8")
    state = report.get("state") or {}
    lines = [
        "# v28 Feature-Gate Exit Bid Suppression Watch",
        "",
        "Research-only frozen watch. No live bot changes or orders.",
        "",
        f"- Generated UTC: `{report.get('generated_at_utc')}`",
        f"- Freeze UTC: `{state.get('freeze_ts_utc')}`",
        f"- Candidate: `{state.get('candidate')}`",
        f"- Rule: suppress selected-side feature-gate exits when `exit_bid_min >= {state.get('exit_bid_min_cents')}`.",
        "",
        "## Interpretation",
        "",
    ]
    lines.extend(f"- {note}" for note in report.get("interpretation") or [])
    for lane in report.get("lanes") or []:
        summary = lane.get("summary") or {}
        lines.extend(
            [
                "",
                f"## {lane.get('lane')}",
                "",
                f"- Settled/scored: `{summary.get('settled')}`",
                f"- Suppressed exits: `{summary.get('suppressed_exits')}`",
                f"- Helpful/harmful suppressions: `{summary.get('suppressed_helpful')} / {summary.get('suppressed_harmful')}`",
                f"- Live selected net: `{fmt(summary.get('live_selected_net_cents'))}c`",
                f"- Candidate net: `{fmt(summary.get('candidate_net_cents'))}c`",
                f"- Delta vs live: `{fmt(summary.get('delta_vs_live_cents'))}c`",
                f"- Full-loss cushion: `{summary.get('full_loss_cushion_estimate')}`",
                f"- Blockers: `{summary.get('blockers')}`",
                "",
                "| market | source | side | won | first exit | live c | hold c | candidate c | delta c | bid min | p_hold avg | reason counts |",
                "|---|---|---|---:|---|---:|---:|---:|---:|---:|---:|---|",
            ]
        )
        for row in summary.get("selected_examples") or []:
            lines.append(
                f"| {row.get('market')} | {row.get('source')} | {row.get('side')} | {row.get('side_won')} | "
                f"{row.get('first_exit_ts_utc')} | {fmt(row.get('live_selected_net_cents'))} | "
                f"{fmt(row.get('hold_to_settlement_net_cents'))} | {fmt(row.get('candidate_net_cents'))} | "
                f"{fmt(row.get('delta_vs_live_cents'))} | {fmt(row.get('exit_bid_min'))} | "
                f"{fmt(row.get('exit_p_hold_avg'))} | {row.get('exit_reason_counts')} |"
            )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    report = build_report()
    write_md(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
