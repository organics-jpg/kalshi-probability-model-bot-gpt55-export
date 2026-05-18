"""Score v28 rejected opportunities after settlement.

This is a forward-evidence diagnostic, not an optimizer. It estimates whether
v28's entry rejections protected the strategy or missed a profitable entry,
grouped by the physical rejection reason observed live.
"""
from __future__ import annotations

import csv
import json
import math
from pathlib import Path
from typing import Any

from probe_v28_forward_physics_registry import recross_hazard_score
from probe_v28_reactivated_shadow_status import STORAGE_TAG, as_float, market_result, read_events


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
OUT_CSV = OUT_DIR / "v28_rejected_opportunity_score_latest.csv"
OUT_JSON = OUT_DIR / "v28_rejected_opportunity_score_latest.json"
OUT_MD = OUT_DIR / "v28_rejected_opportunity_score_latest.md"


def as_int(value: Any) -> int | None:
    if value is None or value == "":
        return None
    try:
        if isinstance(value, float) and math.isnan(value):
            return None
        return int(float(value))
    except (TypeError, ValueError):
        return None


def outcome_for_side(result: str, side: str) -> bool | None:
    if result not in {"yes", "no"} or side not in {"yes", "no"}:
        return None
    return result == side


def build_rows() -> list[dict[str, Any]]:
    events = [event for event in read_events() if event.get("event_type") == "mushroom_v28_rejected"]
    first_by_key: dict[tuple[str, str, str], dict[str, Any]] = {}
    for event in events:
        market = str(event.get("market") or "")
        side = str(event.get("side") or event.get("mushroom_v28_side") or "").lower()
        reason = str(event.get("mushroom_v28_reject_reason") or event.get("decision_reason") or "unknown")
        if not market or side not in {"yes", "no"}:
            continue
        key = (market, side, reason)
        if key not in first_by_key:
            first_by_key[key] = event

    rows: list[dict[str, Any]] = []
    for (market, side, reason), event in sorted(first_by_key.items(), key=lambda item: str(item[1].get("ts_wall") or "")):
        status, result = market_result(market)
        side_won = outcome_for_side(result, side)
        ask_cents = as_int(event.get("mushroom_v28_ask_cents") or event.get("trigger_price_cents"))
        qty = max(1, as_int(event.get("mushroom_v28_target_count")) or 1)
        hypothetical_hold_gross = None
        if side_won is not None and ask_cents is not None:
            hypothetical_hold_gross = ((100 if side_won else 0) - ask_cents) * qty
        actionable_shadow = bool(
            ask_cents is not None
            and 1 <= ask_cents <= 99
            and event.get("mushroom_v28_book_ok") is True
            and event.get("mushroom_v28_btc_ok") is True
            and event.get("mushroom_v28_time_ok") is True
            and event.get("mushroom_v28_risk_ok") is True
        )
        if hypothetical_hold_gross is None:
            verdict = "unresolved"
        elif hypothetical_hold_gross > 0:
            verdict = "missed_profit"
        elif hypothetical_hold_gross < 0:
            verdict = "protected_loss"
        else:
            verdict = "neutral"

        p_side = as_float(event.get("mushroom_v28_p_side"))
        brier = None
        if side_won is not None and p_side is not None:
            brier = (p_side - (1.0 if side_won else 0.0)) ** 2

        abs_d_sigma = as_float(event.get("mushroom_v28_abs_d_sigma"))
        seconds_to_close = as_float(event.get("mushroom_v28_seconds_to_close"))
        sigma = as_float(event.get("mushroom_v28_sigma_t_dollars"))
        recross_hazard = recross_hazard_score(abs_d_sigma, seconds_to_close, sigma)

        row = {
            "market": market,
            "ts_wall": event.get("ts_wall"),
            "side": side,
            "reason": reason,
            "status": status,
            "result": result,
            "side_won": side_won,
            "ask_cents": ask_cents,
            "qty": qty,
            "hypothetical_hold_gross_cents": hypothetical_hold_gross,
            "verdict": verdict,
            "actionable_shadow": actionable_shadow,
            "p_side": p_side,
            "brier": brier,
            "edge_cents": as_float(event.get("mushroom_v28_edge_cents")),
            "raw_edge_cents": as_float(event.get("mushroom_v28_raw_edge_cents")),
            "fair_side_cents": as_float(event.get("mushroom_v28_fair_side_cents")),
            "seconds_to_close": seconds_to_close,
            "sigma_t_dollars": sigma,
            "abs_d_sigma": abs_d_sigma,
            "recross_hazard_score": recross_hazard,
            "btc_age_ms": as_float(event.get("mushroom_v28_btc_age_ms")),
            "book_age_ms": as_float(event.get("mushroom_v28_book_age_ms")),
            "eligible_depth": as_float(event.get("mushroom_v28_eligible_depth")),
            "p_ok": event.get("mushroom_v28_p_ok"),
            "edge_ok": event.get("mushroom_v28_edge_ok"),
            "model_price_ok": event.get("mushroom_v28_model_price_ok"),
            "ask_ok": event.get("mushroom_v28_ask_ok"),
            "book_ok": event.get("mushroom_v28_book_ok"),
            "btc_ok": event.get("mushroom_v28_btc_ok"),
            "risk_ok": event.get("mushroom_v28_risk_ok"),
            "h6_recross_hazard_high": recross_hazard is not None and recross_hazard >= 0.25,
        }
        rows.append(row)
    return rows


def summarize_bucket(rows: list[dict[str, Any]]) -> dict[str, Any]:
    resolved = [row for row in rows if row.get("hypothetical_hold_gross_cents") is not None]
    actionable = [row for row in rows if row.get("actionable_shadow") is True]
    actionable_resolved = [row for row in actionable if row.get("hypothetical_hold_gross_cents") is not None]
    return {
        "count": len(rows),
        "resolved": len(resolved),
        "actionable": len(actionable),
        "actionable_resolved": len(actionable_resolved),
        "would_win": sum(1 for row in resolved if row.get("side_won") is True),
        "would_lose": sum(1 for row in resolved if row.get("side_won") is False),
        "hypothetical_hold_gross_cents": sum(float(row["hypothetical_hold_gross_cents"]) for row in resolved),
        "actionable_hold_gross_cents": sum(float(row["hypothetical_hold_gross_cents"]) for row in actionable_resolved),
        "missed_profit_count": sum(1 for row in actionable_resolved if row.get("verdict") == "missed_profit"),
        "protected_loss_count": sum(1 for row in actionable_resolved if row.get("verdict") == "protected_loss"),
        "avg_brier": (
            sum(float(row["brier"]) for row in resolved if row.get("brier") is not None)
            / max(1, sum(1 for row in resolved if row.get("brier") is not None))
            if resolved
            else None
        ),
    }


def summarize(rows: list[dict[str, Any]]) -> dict[str, Any]:
    by_reason: dict[str, dict[str, Any]] = {}
    by_flag: dict[str, dict[str, Any]] = {}
    reasons = sorted({str(row.get("reason") or "unknown") for row in rows})
    for reason in reasons:
        by_reason[reason] = summarize_bucket([row for row in rows if row.get("reason") == reason])
    for flag in ["actionable_shadow", "h6_recross_hazard_high", "book_ok", "btc_ok", "p_ok", "edge_ok", "model_price_ok"]:
        by_flag[flag] = summarize_bucket([row for row in rows if row.get(flag) is True])
    return {
        "storage_tag": STORAGE_TAG,
        "rows": len(rows),
        "overall": summarize_bucket(rows),
        "by_reason": by_reason,
        "by_flag": by_flag,
    }


def write_csv(rows: list[dict[str, Any]]) -> None:
    if not rows:
        OUT_CSV.write_text("", encoding="utf-8")
        return
    keys = list(rows[0].keys())
    with OUT_CSV.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=keys)
        writer.writeheader()
        writer.writerows(rows)


def write_md(rows: list[dict[str, Any]], summary: dict[str, Any]) -> None:
    overall = summary["overall"]
    lines = [
        "# v28 Rejected Opportunity Score",
        "",
        "- Purpose: score rejected v28 opportunities after settlement without changing strategy logic.",
        "- Unit: first rejected observation per market/side/reason, so repeated throttle events do not dominate.",
        "",
        "## Overall",
        "",
        f"- Opportunities: `{overall['count']}`",
        f"- Resolved: `{overall['resolved']}`",
        f"- Actionable resolved: `{overall['actionable_resolved']}`",
        f"- Would win: `{overall['would_win']}`",
        f"- Would lose: `{overall['would_lose']}`",
        f"- Hypothetical hold gross: `${overall['hypothetical_hold_gross_cents'] / 100.0:.2f}`",
        f"- Actionable hold gross: `${overall['actionable_hold_gross_cents'] / 100.0:.2f}`",
        f"- Actionable missed-profit/protected-loss: `{overall['missed_profit_count']}` / `{overall['protected_loss_count']}`",
        f"- Avg Brier: `{overall['avg_brier']}`",
        "",
        "## By Reject Reason",
        "",
        "| reason | count | resolved | actionable resolved | missed | protected | hold gross | actionable gross | avg brier |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for reason, bucket in summary["by_reason"].items():
        lines.append(
            f"| {reason} | {bucket['count']} | {bucket['resolved']} | {bucket['actionable_resolved']} | "
            f"{bucket['missed_profit_count']} | {bucket['protected_loss_count']} | "
            f"${bucket['hypothetical_hold_gross_cents'] / 100.0:.2f} | "
            f"${bucket['actionable_hold_gross_cents'] / 100.0:.2f} | {bucket['avg_brier']} |"
        )
    lines.extend(["", "## Latest Rows", ""])
    if rows:
        lines.append("| market | side | reason | action | status | result | ask | side won | hold gross | verdict | p_side | edge |")
        lines.append("|---|---|---|---|---|---|---:|---|---:|---|---:|---:|")
        for row in rows[-20:]:
            gross = row.get("hypothetical_hold_gross_cents")
            lines.append(
                "| {market} | {side} | {reason} | {actionable_shadow} | {status} | {result} | {ask_cents} | {side_won} | {gross} | {verdict} | {p_side} | {edge_cents} |".format(
                    gross="" if gross is None else gross,
                    **row,
                )
            )
    else:
        lines.append("No rejected opportunities yet.")
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    rows = build_rows()
    summary = summarize(rows)
    payload = {"summary": summary, "rows": rows}
    OUT_JSON.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_csv(rows)
    write_md(rows, summary)
    print(str(OUT_MD))


if __name__ == "__main__":
    main()
