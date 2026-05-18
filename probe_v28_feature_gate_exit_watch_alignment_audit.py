"""Align feature-gate live exit mismatches with frozen exit-watch shapes.

Research-only. This report joins existing diagnostic/frozen watch artifacts and
does not change live bot logic or candidate rules.
"""
from __future__ import annotations

import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
OUT_JSON = OUT_DIR / "v28_feature_gate_exit_watch_alignment_audit_latest.json"
OUT_MD = OUT_DIR / "v28_feature_gate_exit_watch_alignment_audit_latest.md"

MISMATCH = OUT_DIR / "v28_feature_gate_live_exit_mismatch_drilldown_latest.json"
EXIT_BID = OUT_DIR / "v28_feature_gate_exit_bid_suppression_watch_latest.json"
DELAYED = OUT_DIR / "v28_frozen_feature_gate_exit_bid_delayed_recheck_latest.json"
VALUE = OUT_DIR / "v28_frozen_feature_gate_value_exit_watch_latest.json"


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


def cents(value: Any) -> str:
    try:
        c = float(value)
    except (TypeError, ValueError):
        return ""
    return f"{c:.0f}c"


def first_lane_rows(payload: dict[str, Any], lane_name: str) -> dict[str, dict[str, Any]]:
    lanes = payload.get("lanes") if isinstance(payload.get("lanes"), list) else []
    for lane in lanes:
        if lane.get("lane") == lane_name or lane.get("label") == lane_name:
            rows = lane.get("rows") if isinstance(lane.get("rows"), list) else []
            return {str(row.get("market")): row for row in rows if row.get("market")}
    return {}


def state_freeze(payload: dict[str, Any]) -> str | None:
    state = payload.get("state") if isinstance(payload.get("state"), dict) else {}
    return state.get("freeze_ts_utc") or payload.get("freeze_ts_utc")


def reason_group(reason_counts: dict[str, Any]) -> str:
    keys = " ".join(reason_counts.keys())
    if "exit_value_over_hold" in keys:
        return "value_over_hold"
    if "probability_reduce" in keys:
        return "probability_reduce"
    if "probability_collapse" in keys:
        return "probability_collapse"
    return "other"


def live_selected_net(market: dict[str, Any]) -> float:
    return float(market.get("live_selected_side_net_cents") or 0.0)


def build_market_row(
    market: dict[str, Any],
    exit_bid_rows: dict[str, dict[str, Any]],
    delayed_rows: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    ticker = str(market.get("market"))
    exit_bid = exit_bid_rows.get(ticker, {})
    delayed = delayed_rows.get(ticker, {})
    reasons = market.get("exit_reason_counts") if isinstance(market.get("exit_reason_counts"), dict) else {}
    group = reason_group(reasons)

    value_watch_catches = group == "value_over_hold"
    high_bid_catches = bool(exit_bid.get("suppressed"))
    delayed_catches = bool(delayed.get("delayed_recheck_suppressed"))
    broad_loss_control_risk = group in {"probability_reduce", "probability_collapse"}

    return {
        "market": ticker,
        "source": market.get("source"),
        "side": market.get("side"),
        "theory_net_cents": market.get("theory_net_cents"),
        "live_selected_side_net_cents": live_selected_net(market),
        "swing_cents": float(market.get("theory_net_cents") or 0.0) - live_selected_net(market),
        "reason_group": group,
        "exit_reason_counts": reasons,
        "value_watch_catches": value_watch_catches,
        "high_bid_watch_catches": high_bid_catches,
        "delayed_recheck_watch_catches": delayed_catches,
        "broad_loss_control_risk": broad_loss_control_risk,
        "exit_bid_min": exit_bid.get("exit_bid_min") or delayed.get("exit_bid_min"),
        "exit_bid_avg": exit_bid.get("exit_bid_avg") or delayed.get("exit_bid_avg"),
        "exit_p_hold_avg": exit_bid.get("exit_p_hold_avg") or delayed.get("exit_p_hold_avg"),
        "recheck_bid": delayed.get("recheck_bid"),
        "window_drop_cents": delayed.get("window_drop_cents"),
        "min_window_bid": delayed.get("min_window_bid"),
        "delayed_delta_vs_live_cents": delayed.get("delayed_recheck_delta_cents"),
        "high_bid_delta_vs_live_cents": exit_bid.get("delta_vs_live_cents"),
    }


def summarize(rows: list[dict[str, Any]]) -> dict[str, Any]:
    reason_counts = Counter(row["reason_group"] for row in rows)
    return {
        "markets": len(rows),
        "theory_net_cents": sum(float(row.get("theory_net_cents") or 0.0) for row in rows),
        "live_selected_side_net_cents": sum(float(row.get("live_selected_side_net_cents") or 0.0) for row in rows),
        "swing_cents": sum(float(row.get("swing_cents") or 0.0) for row in rows),
        "value_watch_catches": sum(1 for row in rows if row.get("value_watch_catches")),
        "high_bid_watch_catches": sum(1 for row in rows if row.get("high_bid_watch_catches")),
        "delayed_recheck_watch_catches": sum(1 for row in rows if row.get("delayed_recheck_watch_catches")),
        "broad_loss_control_risk_rows": sum(1 for row in rows if row.get("broad_loss_control_risk")),
        "reason_group_counts": dict(reason_counts),
    }


def strict_status(payload: dict[str, Any], post_lane_name: str) -> dict[str, Any]:
    lanes = payload.get("lanes") if isinstance(payload.get("lanes"), list) else []
    for lane in lanes:
        if lane.get("lane") == post_lane_name or lane.get("label") == post_lane_name:
            summary = lane.get("summary") if isinstance(lane.get("summary"), dict) else {}
            rows = lane.get("rows")
            variants = lane.get("variants")
            if isinstance(rows, list):
                return {
                    "rows": summary.get("settled", summary.get("rows", len(rows))),
                    "suppressed": summary.get("suppressed_exits", summary.get("suppressed", 0)),
                    "net_cents": summary.get("candidate_net_cents", 0),
                    "blockers": summary.get("blockers", []),
                    "kind": "rows",
                }
            if isinstance(variants, list):
                best = variants[0] if variants else {}
                return {
                    "rows": best.get("settled", 0),
                    "suppressed": best.get("suppressed", 0),
                    "net_cents": best.get("candidate_net_cents", 0),
                    "blockers": best.get("blockers", []),
                    "kind": "variants",
                }
    return {"rows": 0, "kind": "missing"}


def build_report() -> dict[str, Any]:
    mismatch = load_json(MISMATCH)
    exit_bid = load_json(EXIT_BID)
    delayed = load_json(DELAYED)
    value = load_json(VALUE)

    exit_bid_rows = first_lane_rows(exit_bid, "diagnostic_feature_gate_exit_bid")
    delayed_rows = first_lane_rows(delayed, "diagnostic_prefreeze_context")
    rows = [
        build_market_row(market, exit_bid_rows, delayed_rows)
        for market in (mismatch.get("markets") or [])
    ]

    return {
        "generated_at_utc": utc_now_iso(),
        "sources": {
            "mismatch": str(MISMATCH),
            "exit_bid_watch": str(EXIT_BID),
            "delayed_recheck_watch": str(DELAYED),
            "value_exit_watch": str(VALUE),
        },
        "freeze_timestamps": {
            "exit_bid_watch": state_freeze(exit_bid),
            "delayed_recheck_watch": state_freeze(delayed),
            "value_exit_watch": state_freeze(value),
        },
        "strict_status": {
            "exit_bid_watch": strict_status(exit_bid, "post_exit_bid_birth"),
            "delayed_recheck_watch": strict_status(delayed, "post_delayed_recheck_birth"),
            "value_exit_watch": strict_status(value, "post_value_exit_birth"),
        },
        "summary": summarize(rows),
        "rows": rows,
        "interpretation": [
            "All joined rows are diagnostic/prefreeze for these exit watches; strict post-freeze watch rows remain the promotion denominator.",
            "Value-only catches fewer observed selected-side winner clips but is narrower and closer to preserving reduce/collapse loss-control behavior.",
            "High-bid and delayed-recheck watch shapes cover more observed clips, including reduce/collapse exits, so they need strict forward proof that they do not suppress true loss-control exits.",
        ],
    }


def write_report(payload: dict[str, Any]) -> None:
    summary = payload["summary"]
    strict = payload["strict_status"]
    lines = [
        "# v28 Feature-Gate Exit Watch Alignment Audit",
        "",
        "Research-only alignment report. No live bot changes, no orders, no new candidate rule.",
        "",
        f"- Generated UTC: `{payload['generated_at_utc']}`",
        f"- Mismatch markets: `{summary['markets']}`",
        f"- Settlement theory / live selected-side / swing: `{cents(summary['theory_net_cents'])}` / `{cents(summary['live_selected_side_net_cents'])}` / `{cents(summary['swing_cents'])}`",
        f"- Value-watch catches: `{summary['value_watch_catches']}`",
        f"- High-bid watch catches: `{summary['high_bid_watch_catches']}`",
        f"- Delayed-recheck watch catches: `{summary['delayed_recheck_watch_catches']}`",
        f"- Broad loss-control risk rows among catches: `{summary['broad_loss_control_risk_rows']}`",
        f"- Reason groups: `{summary['reason_group_counts']}`",
        "",
        "## Strict Watch Status",
        "",
        "| watch | freeze UTC | strict rows | suppressed | net | blockers |",
        "|---|---|---:|---:|---:|---|",
    ]
    for name, status in strict.items():
        lines.append(
            "| {name} | `{freeze}` | {rows} | {suppressed} | {net} | {blockers} |".format(
                name=name,
                freeze=payload["freeze_timestamps"].get(name),
                rows=status.get("rows", 0),
                suppressed=status.get("suppressed", 0),
                net=cents(status.get("net_cents", 0)),
                blockers=", ".join(status.get("blockers") or []),
            )
        )

    lines.extend(
        [
            "",
            "## Mismatch Alignment",
            "",
            "| market | reason group | theory | live selected | swing | value | high bid | delayed | bid min | p_hold avg | recheck bid | drop | risk |",
            "|---|---|---:|---:|---:|---|---|---|---:|---:|---:|---:|---|",
        ]
    )
    for row in payload["rows"]:
        lines.append(
            "| {market} | {reason} | {theory} | {live} | {swing} | {value} | {high} | {delayed} | {bid} | {p_hold} | {recheck} | {drop} | {risk} |".format(
                market=row.get("market"),
                reason=row.get("reason_group"),
                theory=cents(row.get("theory_net_cents")),
                live=cents(row.get("live_selected_side_net_cents")),
                swing=cents(row.get("swing_cents")),
                value="yes" if row.get("value_watch_catches") else "",
                high="yes" if row.get("high_bid_watch_catches") else "",
                delayed="yes" if row.get("delayed_recheck_watch_catches") else "",
                bid=row.get("exit_bid_min"),
                p_hold=row.get("exit_p_hold_avg"),
                recheck=row.get("recheck_bid"),
                drop=row.get("window_drop_cents"),
                risk="reduce/collapse" if row.get("broad_loss_control_risk") else "",
            )
        )

    lines.extend(["", "## Interpretation", ""])
    for item in payload["interpretation"]:
        lines.append(f"- {item}")

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    payload = build_report()
    write_report(payload)
    print(OUT_MD)


if __name__ == "__main__":
    main()
