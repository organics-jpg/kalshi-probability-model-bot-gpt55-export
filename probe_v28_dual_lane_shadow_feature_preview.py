"""Lightweight post-freeze feature preview for the v28 dual-lane watch.

Research-only; no live bot changes and no orders.

This does not replace the heavy own-freeze scorer. It reads the current shadow
event stream and checks whether post-freeze approved/rejected observations have
the observable ingredients used by the dual-lane sidecar and primary pocket.
"""
from __future__ import annotations

import json
import math
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from probe_v28_dual_lane_freeze_collection_monitor import freeze_ts, live_baseline_cents
from probe_v28_exit_policy_common_clock_watch import parse_ts
from probe_v28_forward_physics_registry import recross_hazard_score
from probe_v28_reactivated_shadow_status import market_result, read_events, reconstruct_trades, score_trade
from probe_v28_rejected_opportunity_score import as_int, outcome_for_side


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
OUT_JSON = OUT_DIR / "v28_dual_lane_shadow_feature_preview_latest.json"
OUT_MD = OUT_DIR / "v28_dual_lane_shadow_feature_preview_latest.md"

RAW_EDGE_MIN = 0.05
RECROSS_MAX = 0.60
ABS_D_MIN = 0.85
CHEAP_SIDE_FLOOR = 0.65
CHEAP_PENALTY_LAMBDA = 0.25
PRIMARY_MID_ABS_D_MIN = 0.60
PRIMARY_MID_ABS_D_MAX = 0.75
PRIMARY_MAX_ASK = 0.65
PRIMARY_PROXY_NOTE = (
    "This is only the observable sizing-pocket proxy. The actual primary lane "
    "is selected by the parent-fill composer before this pocket can shrink size."
)


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def as_float(value: Any) -> float | None:
    if value is None or value == "":
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def local_time_iso(value: str | None) -> str | None:
    parsed = parse_ts(value)
    if parsed is None:
        return None
    return parsed.astimezone().isoformat()


def event_ts(event: dict[str, Any]) -> datetime | None:
    return parse_ts(event.get("ts_wall") or event.get("timestamp") or event.get("ts"))


def raw_edge_from(row: dict[str, Any]) -> float | None:
    raw = as_float(row.get("raw_edge_cents"))
    if raw is not None:
        return raw / 100.0
    p_side = as_float(row.get("p_side"))
    ask = as_float(row.get("ask_prob"))
    if p_side is None or ask is None:
        return None
    return p_side - ask


def cheap_gap(row: dict[str, Any]) -> float | None:
    ask = as_float(row.get("ask_prob"))
    if ask is None:
        return None
    return max(0.0, CHEAP_SIDE_FLOOR - ask)


def adjusted_edge(row: dict[str, Any]) -> float | None:
    edge = raw_edge_from(row)
    gap = cheap_gap(row)
    if edge is None or gap is None:
        return None
    return edge - CHEAP_PENALTY_LAMBDA * gap


def sidecar_missing(row: dict[str, Any]) -> list[str]:
    missing: list[str] = []
    edge = raw_edge_from(row)
    recross = as_float(row.get("recross_hazard_score"))
    abs_d = as_float(row.get("abs_d_sigma"))
    if edge is None:
        missing.append("raw_edge_missing")
    elif edge < RAW_EDGE_MIN:
        missing.append("raw_edge_lt_05")
    if recross is None:
        missing.append("recross_missing")
    elif recross > RECROSS_MAX:
        missing.append("recross_gt_60")
    if abs_d is None:
        missing.append("abs_d_missing")
    elif abs_d < ABS_D_MIN:
        missing.append("abs_d_lt_085")
    return missing


def sidecar_eligible(row: dict[str, Any]) -> bool:
    return not sidecar_missing(row)


def primary_pocket(row: dict[str, Any]) -> bool:
    abs_d = as_float(row.get("abs_d_sigma"))
    ask = as_float(row.get("ask_prob"))
    return (
        abs_d is not None
        and ask is not None
        and PRIMARY_MID_ABS_D_MIN <= abs_d <= PRIMARY_MID_ABS_D_MAX
        and ask <= PRIMARY_MAX_ASK
    )


def is_rejected_actionable(event: dict[str, Any]) -> bool:
    ask = as_float(event.get("mushroom_v28_ask_cents") or event.get("trigger_price_cents"))
    return bool(
        ask is not None
        and 1.0 <= ask <= 99.0
        and event.get("mushroom_v28_book_ok") is True
        and event.get("mushroom_v28_btc_ok") is True
        and event.get("mushroom_v28_time_ok") is True
        and event.get("mushroom_v28_risk_ok") is True
    )


def row_from_rejected(event: dict[str, Any]) -> dict[str, Any] | None:
    if event.get("event_type") != "mushroom_v28_rejected" or not is_rejected_actionable(event):
        return None
    market = str(event.get("market") or "")
    side = str(event.get("side") or event.get("mushroom_v28_side") or "").lower()
    ask = as_float(event.get("mushroom_v28_ask_cents") or event.get("trigger_price_cents"))
    p_side = as_float(event.get("mushroom_v28_p_side"))
    if not market or side not in {"yes", "no"} or ask is None or p_side is None:
        return None
    status, result = market_result(market)
    side_won = outcome_for_side(result, side)
    qty = max(1, as_int(event.get("mushroom_v28_target_count")) or 1)
    net_cents = None
    if side_won is not None:
        net_cents = ((100 if side_won else 0) - int(ask)) * qty
    abs_d = as_float(event.get("mushroom_v28_abs_d_sigma"))
    seconds_to_close = as_float(event.get("mushroom_v28_seconds_to_close"))
    sigma = as_float(event.get("mushroom_v28_sigma_t_dollars"))
    return {
        "source": "rejected_actionable",
        "market": market,
        "side": side,
        "ts_wall": event.get("ts_wall"),
        "status": status,
        "result": result,
        "side_won": side_won,
        "net_cents": net_cents,
        "p_side": p_side,
        "ask_prob": ask / 100.0,
        "ask_cents": ask,
        "raw_edge_cents": as_float(event.get("mushroom_v28_raw_edge_cents")),
        "edge_cents": as_float(event.get("mushroom_v28_edge_cents")),
        "seconds_to_close": seconds_to_close,
        "sigma_t_dollars": sigma,
        "abs_d_sigma": abs_d,
        "recross_hazard_score": recross_hazard_score(abs_d, seconds_to_close, sigma),
        "eligible_depth": as_float(event.get("mushroom_v28_eligible_depth")),
        "reason": event.get("mushroom_v28_reject_reason") or event.get("decision_reason"),
    }


def row_from_trade(trade_row: dict[str, Any]) -> dict[str, Any] | None:
    features = trade_row.get("entry_features") if isinstance(trade_row.get("entry_features"), dict) else {}
    market = str(trade_row.get("market") or "")
    side = str(trade_row.get("side") or "").lower()
    ask = as_float(features.get("mushroom_v28_ask_cents") or trade_row.get("entry_cents"))
    p_side = as_float(features.get("mushroom_v28_p_side"))
    if not market or side not in {"yes", "no"} or ask is None or p_side is None:
        return None
    abs_d = as_float(features.get("mushroom_v28_abs_d_sigma"))
    seconds_to_close = as_float(features.get("mushroom_v28_seconds_to_close"))
    sigma = as_float(features.get("mushroom_v28_sigma_t_dollars"))
    return {
        "source": "approved_entry",
        "market": market,
        "side": side,
        "ts_wall": trade_row.get("entry_ts"),
        "status": trade_row.get("status"),
        "result": trade_row.get("result"),
        "side_won": outcome_for_side(trade_row.get("result"), side),
        "net_cents": trade_row.get("actual_gross_cents"),
        "hold_gross_cents": trade_row.get("hold_gross_cents"),
        "p_side": p_side,
        "ask_prob": ask / 100.0,
        "ask_cents": ask,
        "raw_edge_cents": as_float(features.get("mushroom_v28_raw_edge_cents")),
        "edge_cents": as_float(features.get("mushroom_v28_edge_cents")),
        "seconds_to_close": seconds_to_close,
        "sigma_t_dollars": sigma,
        "abs_d_sigma": abs_d,
        "recross_hazard_score": recross_hazard_score(abs_d, seconds_to_close, sigma),
        "eligible_depth": as_float(features.get("mushroom_v28_eligible_depth")),
        "reason": trade_row.get("entry_reason"),
    }


def post_freeze_rows(freeze: str | None) -> list[dict[str, Any]]:
    freeze_dt = parse_ts(freeze)
    if freeze_dt is None:
        return []
    rows: list[dict[str, Any]] = []
    events = read_events()
    trade_rows = [score_trade(trade) for trade in reconstruct_trades(events)]
    for trade_row in trade_rows:
        ts = parse_ts(trade_row.get("entry_ts"))
        if ts is not None and ts >= freeze_dt:
            row = row_from_trade(trade_row)
            if row is not None:
                rows.append(row)
    for event in events:
        ts = event_ts(event)
        if ts is not None and ts >= freeze_dt:
            row = row_from_rejected(event)
            if row is not None:
                rows.append(row)
    rows.sort(key=lambda row: str(row.get("ts_wall") or ""))
    return rows


def best_sidecar_by_market(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        if sidecar_eligible(row):
            enriched = dict(row)
            enriched["raw_edge"] = raw_edge_from(row)
            enriched["cheap_gap"] = cheap_gap(row)
            enriched["adjusted_edge"] = adjusted_edge(row)
            grouped[str(row.get("market") or "")].append(enriched)
    return [
        max(items, key=lambda row: (float(row.get("adjusted_edge") or -999.0), str(row.get("ts_wall") or "")))
        for items in grouped.values()
        if items
    ]


def best_primary_by_market(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        if primary_pocket(row):
            enriched = dict(row)
            enriched["raw_edge"] = raw_edge_from(row)
            grouped[str(row.get("market") or "")].append(enriched)
    return [
        max(items, key=lambda row: (float(row.get("raw_edge") or -999.0), str(row.get("ts_wall") or "")))
        for items in grouped.values()
        if items
    ]


def summarize(rows: list[dict[str, Any]], denominator: int) -> dict[str, Any]:
    settled = [row for row in rows if row.get("side_won") is not None and row.get("net_cents") is not None]
    net = sum(float(row.get("net_cents") or 0.0) for row in settled)
    entries = len(rows)
    approved = sum(1 for row in rows if row.get("source") == "approved_entry")
    reconstructed = entries - approved
    negative_raw_edge = sum(1 for row in rows if (raw_edge_from(row) is not None and float(raw_edge_from(row) or 0.0) < 0.0))
    sidecar_ineligible = sum(1 for row in rows if not sidecar_eligible(row))
    return {
        "entries": entries,
        "settled": len(settled),
        "wins": sum(1 for row in settled if row.get("side_won") is True),
        "losses": sum(1 for row in settled if row.get("side_won") is False),
        "pnl_wins": sum(1 for row in settled if float(row.get("net_cents") or 0.0) > 0.0),
        "pnl_losses": sum(1 for row in settled if float(row.get("net_cents") or 0.0) < 0.0),
        "pnl_flats": sum(1 for row in settled if float(row.get("net_cents") or 0.0) == 0.0),
        "net_cents": net,
        "coverage_pct": 100.0 * entries / denominator if denominator else None,
        "source_counts": dict(Counter(str(row.get("source") or "unknown") for row in rows)),
        "reconstructed_share": reconstructed / entries if entries else None,
        "full_loss_cushion": int(max(0.0, net) // 100.0),
        "negative_raw_edge_rows": negative_raw_edge,
        "sidecar_ineligible_rows": sidecar_ineligible,
    }


def compact(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "market": row.get("market"),
        "source": row.get("source"),
        "side": row.get("side"),
        "ts_wall": row.get("ts_wall"),
        "status": row.get("status"),
        "result": row.get("result"),
        "side_won": row.get("side_won"),
        "net_cents": row.get("net_cents"),
        "raw_edge": raw_edge_from(row),
        "cheap_gap": cheap_gap(row),
        "adjusted_edge": adjusted_edge(row),
        "recross_hazard_score": row.get("recross_hazard_score"),
        "abs_d_sigma": row.get("abs_d_sigma"),
        "ask_prob": row.get("ask_prob"),
        "primary_mid_confidence_pocket": primary_pocket(row),
        "sidecar_missing": sidecar_missing(row),
    }


def build_report() -> dict[str, Any]:
    freeze = freeze_ts()
    rows = post_freeze_rows(freeze)
    denominator = len({str(row.get("market") or "") for row in rows if row.get("market")})
    sidecar_rows = best_sidecar_by_market(rows)
    primary_rows = best_primary_by_market(rows)
    missing_counts = Counter(reason for row in rows for reason in sidecar_missing(row))
    availability = {
        "raw_edge": sum(1 for row in rows if raw_edge_from(row) is not None),
        "recross_hazard_score": sum(1 for row in rows if row.get("recross_hazard_score") is not None),
        "abs_d_sigma": sum(1 for row in rows if row.get("abs_d_sigma") is not None),
        "ask_prob": sum(1 for row in rows if row.get("ask_prob") is not None),
    }
    return {
        "generated_at_utc": utc_now_iso(),
        "freeze_ts_utc": freeze,
        "freeze_local_time": local_time_iso(freeze),
        "live_baseline_cents": live_baseline_cents(),
        "preview_scope": (
            "Non-promotional preview over post-freeze shadow approved and rejected-actionable observations. "
            "Own-freeze strict scorer remains authoritative for live readiness."
        ),
        "post_freeze_observation_count": len(rows),
        "post_freeze_distinct_markets": denominator,
        "feature_availability": availability,
        "sidecar_rule": {
            "raw_edge_min": RAW_EDGE_MIN,
            "recross_max": RECROSS_MAX,
            "abs_d_min": ABS_D_MIN,
            "cheap_penalty_lambda": CHEAP_PENALTY_LAMBDA,
            "cheap_side_floor": CHEAP_SIDE_FLOOR,
        },
        "primary_pocket_rule": {
            "abs_d_min": PRIMARY_MID_ABS_D_MIN,
            "abs_d_max": PRIMARY_MID_ABS_D_MAX,
            "ask_max": PRIMARY_MAX_ASK,
            "note": PRIMARY_PROXY_NOTE,
        },
        "sidecar_preview_summary": summarize(sidecar_rows, denominator),
        "primary_pocket_preview_summary": summarize(primary_rows, denominator),
        "sidecar_missing_counts": dict(sorted(missing_counts.items())),
        "sidecar_preview_rows": [compact(row) for row in sidecar_rows[-20:]],
        "primary_pocket_rows": [compact(row) for row in primary_rows[-20:]],
        "interpretation": [
            "This preview is useful for collection and feature-availability debugging only.",
            "A good preview row does not count as a live-readiness row until the heavy own-freeze scorer confirms it.",
            "If feature availability is high but own-freeze rows remain zero after the 30-window mark, the bottleneck is the scorer/surface replay path rather than shadow collection.",
            "The primary pocket preview is a risk proxy only; it does not reproduce the parent-fill composer.",
        ],
    }


def fmt(value: Any, digits: int = 3) -> str:
    if value is None:
        return ""
    try:
        val = float(value)
    except (TypeError, ValueError):
        return str(value)
    if not math.isfinite(val):
        return ""
    return f"{val:.{digits}f}"


def cents(value: Any) -> str:
    if value is None:
        return ""
    try:
        amount = float(value)
    except (TypeError, ValueError):
        return str(value)
    return f"{amount:.0f}c (${amount / 100.0:.2f})"


def write_report(report: dict[str, Any]) -> None:
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8")
    sidecar = report.get("sidecar_preview_summary") or {}
    primary = report.get("primary_pocket_preview_summary") or {}
    lines = [
        "# v28 Dual-Lane Shadow Feature Preview",
        "",
        "Research-only. No live bot logic changes, no orders.",
        "",
        f"- Generated UTC: `{report.get('generated_at_utc')}`",
        f"- Freeze UTC: `{report.get('freeze_ts_utc')}`",
        f"- Freeze local time: `{report.get('freeze_local_time')}`",
        f"- Live baseline: `{cents(report.get('live_baseline_cents'))}`",
        f"- Post-freeze observations: `{report.get('post_freeze_observation_count')}`",
        f"- Post-freeze distinct markets: `{report.get('post_freeze_distinct_markets')}`",
        f"- Scope: {report.get('preview_scope')}",
        "",
        "## Interpretation",
        "",
    ]
    lines.extend(f"- {item}" for item in report.get("interpretation") or [])
    availability = report.get("feature_availability") or {}
    lines.extend(
        [
            "",
            "## Feature Availability",
            "",
            "| feature | rows present |",
            "|---|---:|",
        ]
    )
    for key in ["raw_edge", "recross_hazard_score", "abs_d_sigma", "ask_prob"]:
        lines.append(f"| `{key}` | {availability.get(key)} |")
    lines.extend(
        [
            "",
            "## Preview Summaries",
            "",
            "| preview | entries | settled | W/L | coverage | net | recon | cushion | source counts |",
            "|---|---:|---:|---:|---:|---:|---:|---:|---|",
        ]
    )
    for name, summary in [
        ("sidecar exact observable rule", sidecar),
        ("primary sizing-pocket risk proxy", primary),
    ]:
        recon = summary.get("reconstructed_share")
        recon_text = "n/a" if recon is None else f"{100.0 * float(recon):.2f}%"
        lines.append(
            f"| {name} | {summary.get('entries')} | {summary.get('settled')} | "
            f"{summary.get('wins')}/{summary.get('losses')} | {fmt(summary.get('coverage_pct'), 2)}% | "
            f"{cents(summary.get('net_cents'))} | {recon_text} | {summary.get('full_loss_cushion')} | "
            f"`{summary.get('source_counts')}` |"
        )
    lines.extend(
        [
            "",
            "## Realized PnL Sign",
            "",
            "| preview | PnL wins | PnL losses | flats | note |",
            "|---|---:|---:|---:|---|",
            (
                f"| sidecar exact observable rule | {sidecar.get('pnl_wins')} | {sidecar.get('pnl_losses')} | "
                f"{sidecar.get('pnl_flats')} | settlement W/L can differ from realized exit PnL |"
            ),
            (
                f"| primary sizing-pocket risk proxy | {primary.get('pnl_wins')} | {primary.get('pnl_losses')} | "
                f"{primary.get('pnl_flats')} | risk proxy only, not actual parent-fill selection |"
            ),
            "",
            "## Primary Proxy Caution",
            "",
            f"- {PRIMARY_PROXY_NOTE}",
            f"- Current proxy negative-raw-edge rows: `{primary.get('negative_raw_edge_rows')}`",
            f"- Current proxy sidecar-ineligible rows: `{primary.get('sidecar_ineligible_rows')}`",
        ]
    )
    lines.extend(
        [
            "",
            "## Sidecar Missing Counts",
            "",
            "| reason | count |",
            "|---|---:|",
        ]
    )
    for reason, count in (report.get("sidecar_missing_counts") or {}).items():
        lines.append(f"| `{reason}` | {count} |")
    rows = report.get("sidecar_preview_rows") or []
    if rows:
        lines.extend(
            [
                "",
                "## Recent Sidecar Preview Rows",
                "",
                "| market | source | side | won | net | raw edge | adjusted | recross | abs d | ask | missing |",
                "|---|---|---|---|---:|---:|---:|---:|---:|---:|---|",
            ]
        )
        for row in rows:
            lines.append(
                f"| `{row.get('market')}` | {row.get('source')} | {row.get('side')} | {row.get('side_won')} | "
                f"{cents(row.get('net_cents'))} | {fmt(row.get('raw_edge'))} | {fmt(row.get('adjusted_edge'))} | "
                f"{fmt(row.get('recross_hazard_score'))} | {fmt(row.get('abs_d_sigma'))} | "
                f"{fmt(row.get('ask_prob'))} | {', '.join(row.get('sidecar_missing') or []) or 'none'} |"
            )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    report = build_report()
    write_report(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
