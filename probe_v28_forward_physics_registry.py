"""Forward physics registry for the reactivated v28 shadow.

This is intentionally descriptive, not an optimizer. It records fresh v28
shadow entries/exits with predeclared physics tags so later decisions can be
made from forward evidence instead of historical row shopping.
"""
from __future__ import annotations

import csv
import json
import math
from collections import defaultdict
from pathlib import Path
from typing import Any

from probe_v28_reactivated_shadow_status import (
    EVENTS_PATH,
    JSON_PATH as STATUS_JSON_PATH,
    STORAGE_TAG,
    as_float,
    market_result,
    read_events,
    reconstruct_trades,
    score_trade,
)


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
REGISTRY_CSV = OUT_DIR / "v28_forward_physics_registry_latest.csv"
REGISTRY_JSON = OUT_DIR / "v28_forward_physics_registry_latest.json"
REGISTRY_MD = OUT_DIR / "v28_forward_physics_registry_latest.md"


def recross_hazard_score(abs_d_sigma: float | None, seconds_to_close: float | None, sigma: float | None) -> float | None:
    if abs_d_sigma is None or seconds_to_close is None or sigma is None:
        return None
    time_factor = min(1.0, max(0.0, seconds_to_close / 900.0)) ** 0.5
    sigma_factor = min(1.5, max(0.0, sigma / 100.0))
    return math.exp(-abs_d_sigma) * time_factor * sigma_factor


def side_probability(event: dict[str, Any], prefix: str, side: str) -> float | None:
    if side == "yes":
        return as_float(event.get(f"{prefix}_p_yes"))
    p_yes = as_float(event.get(f"{prefix}_p_yes"))
    return None if p_yes is None else 1.0 - p_yes


def approval_events(events: list[dict[str, Any]]) -> list[dict[str, Any]]:
    approvals: list[dict[str, Any]] = []
    for event in events:
        event_type = str(event.get("event_type") or "")
        if event_type != "mushroom_v28_approved":
            continue
        market = str(event.get("market") or "")
        side = str(event.get("side") or event.get("mushroom_v28_side") or "").lower()
        if not market or side not in {"yes", "no"}:
            continue
        row = dict(event)
        row["side"] = side
        approvals.append(row)
    return sorted(approvals, key=lambda row: str(row.get("ts_wall") or ""))


def approval_for_trade(approvals: list[dict[str, Any]], trade_score: dict[str, Any]) -> dict[str, Any] | None:
    market = str(trade_score.get("market") or "")
    side = str(trade_score.get("side") or "").lower()
    entry_ts = str(trade_score.get("entry_ts") or "")
    candidates = [
        event
        for event in approvals
        if str(event.get("market") or "") == market
        and str(event.get("side") or event.get("mushroom_v28_side") or "").lower() == side
        and str(event.get("ts_wall") or "") <= entry_ts
    ]
    return candidates[-1] if candidates else None


def build_rows() -> list[dict[str, Any]]:
    events = read_events()
    approvals = approval_events(events)
    trades = reconstruct_trades(events)

    rows: list[dict[str, Any]] = []
    for trade in trades:
        score = score_trade(trade)
        event = approval_for_trade(approvals, score)
        if event is None:
            continue
        market = str(score.get("market") or "")
        side = str(score.get("side") or "").lower()
        status, result = market_result(market)
        if score:
            status = str(score.get("status") or status)
            result = str(score.get("result") or result)

        p_side = as_float(event.get("mushroom_v28_p_side"))
        p_yes = as_float(event.get("mushroom_v28_p_yes"))
        old_p_yes = as_float(event.get("mushroom_p_yes"))
        old_best_side = str(event.get("mushroom_best_side") or "").lower()
        old_side_p = side_probability(event, "mushroom", side)
        p_disagreement = None if p_side is None or old_side_p is None else p_side - old_side_p

        outcome = None
        side_won = None
        probability_error = None
        brier = None
        if result in {"yes", "no"} and p_side is not None:
            side_won = result == side
            outcome = 1.0 if side_won else 0.0
            probability_error = outcome - p_side
            brier = (p_side - outcome) ** 2

        btc_age = as_float(event.get("mushroom_v28_btc_age_ms"))
        book_age = as_float(event.get("mushroom_v28_book_age_ms"))
        depth = as_float(event.get("mushroom_v28_eligible_depth"))
        edge = as_float(event.get("mushroom_v28_edge_cents"))
        sigma = as_float(event.get("mushroom_v28_sigma_t_dollars"))
        d_sigma = as_float(event.get("mushroom_v28_d_sigma"))
        abs_d_sigma = as_float(event.get("mushroom_v28_abs_d_sigma"))
        seconds_to_close = as_float(event.get("mushroom_v28_seconds_to_close"))
        recross_hazard = recross_hazard_score(abs_d_sigma, seconds_to_close, sigma)

        rows.append(
            {
                "market": market,
                "entry_ts": event.get("ts_wall"),
                "side": side,
                "status": status,
                "result": result,
                "entry_cents": score.get("entry_cents"),
                "exit_cents": score.get("exit_cents"),
                "actual_gross_cents": score.get("actual_gross_cents"),
                "hold_gross_cents": score.get("hold_gross_cents"),
                "exit_value_cents": score.get("exit_value_cents"),
                "exit_reason": score.get("exit_reason"),
                "side_won": side_won,
                "p_side": p_side,
                "p_yes": p_yes,
                "probability_error": probability_error,
                "brier": brier,
                "ask_cents": event.get("mushroom_v28_ask_cents"),
                "fair_side_cents": event.get("mushroom_v28_fair_side_cents"),
                "edge_cents": edge,
                "raw_edge_cents": event.get("mushroom_v28_raw_edge_cents"),
                "net_edge_cents": event.get("mushroom_v28_net_edge_cents"),
                "seconds_to_close": seconds_to_close,
                "d_sigma": d_sigma,
                "abs_d_sigma": abs_d_sigma,
                "sigma_t_dollars": sigma,
                "recross_hazard_score": recross_hazard,
                "btc_age_ms": btc_age,
                "book_age_ms": book_age,
                "eligible_depth": depth,
                "btc_price": event.get("mushroom_v28_btc_price"),
                "strike": event.get("mushroom_v28_strike"),
                "volshock": event.get("mushroom_v28_volshock"),
                "old_v22_best_side": old_best_side,
                "old_v22_p_yes": old_p_yes,
                "old_v22_side_p": old_side_p,
                "v28_minus_v22_side_p": p_disagreement,
                "h1_feed_fresh": btc_age is not None and btc_age <= 600.0 and book_age is not None and book_age <= 1000.0,
                "h2_thin_touch_depth": depth is not None and depth < 25.0,
                "h2_crowded_depth": depth is not None and depth > 1300.0,
                "h4_large_model_disagreement": p_disagreement is not None and abs(p_disagreement) >= 0.08,
                "h4_old_model_opposes_side": bool(old_best_side and old_best_side != side),
                "h5_late_high_sigma": (
                    seconds_to_close is not None
                    and seconds_to_close <= 180.0
                    and sigma is not None
                    and sigma >= 50.0
                ),
                "h6_recross_hazard_high": recross_hazard is not None and recross_hazard >= 0.25,
            }
        )
    return rows


def summarize(rows: list[dict[str, Any]]) -> dict[str, Any]:
    settled = [row for row in rows if row.get("side_won") is not None]
    exited_or_settled = [row for row in rows if row.get("actual_gross_cents") is not None]
    by_flag: dict[str, dict[str, Any]] = {}
    flag_keys = [
        "h1_feed_fresh",
        "h2_thin_touch_depth",
        "h2_crowded_depth",
        "h4_large_model_disagreement",
        "h4_old_model_opposes_side",
        "h5_late_high_sigma",
        "h6_recross_hazard_high",
    ]
    for key in flag_keys:
        bucket = [row for row in rows if row.get(key) is True]
        settled_bucket = [row for row in bucket if row.get("side_won") is not None]
        pnl_bucket = [row for row in bucket if row.get("actual_gross_cents") is not None]
        by_flag[key] = {
            "count": len(bucket),
            "settled": len(settled_bucket),
            "wins": sum(1 for row in settled_bucket if row.get("side_won") is True),
            "gross_cents": sum(float(row["actual_gross_cents"]) for row in pnl_bucket),
            "avg_brier": (
                sum(float(row["brier"]) for row in settled_bucket if row.get("brier") is not None)
                / max(1, sum(1 for row in settled_bucket if row.get("brier") is not None))
                if settled_bucket
                else None
            ),
        }
    return {
        "storage_tag": STORAGE_TAG,
        "events_path": str(EVENTS_PATH),
        "status_json_path": str(STATUS_JSON_PATH),
        "entries": len(rows),
        "settled": len(settled),
        "wins": sum(1 for row in settled if row.get("side_won") is True),
        "exited_or_settled": len(exited_or_settled),
        "gross_cents": sum(float(row["actual_gross_cents"]) for row in exited_or_settled),
        "hold_gross_cents": sum(float(row["hold_gross_cents"]) for row in exited_or_settled if row.get("hold_gross_cents") is not None),
        "avg_brier": (
            sum(float(row["brier"]) for row in settled if row.get("brier") is not None)
            / max(1, sum(1 for row in settled if row.get("brier") is not None))
            if settled
            else None
        ),
        "by_flag": by_flag,
    }


def write_csv(rows: list[dict[str, Any]]) -> None:
    if not rows:
        REGISTRY_CSV.write_text("", encoding="utf-8")
        return
    with REGISTRY_CSV.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def write_md(rows: list[dict[str, Any]], summary: dict[str, Any]) -> None:
    lines = [
        "# v28 Forward Physics Registry",
        "",
        "Descriptive forward registry only. These tags are predeclared diagnostics, not tuned rules.",
        "",
        f"- Entries: `{summary['entries']}`",
        f"- Settled entries: `{summary['settled']}`",
        f"- Settled wins: `{summary['wins']}`",
        f"- Exited/settled P&L: `${summary['gross_cents'] / 100.0:.2f}`",
        f"- Hold-to-settlement P&L on comparable rows: `${summary['hold_gross_cents'] / 100.0:.2f}`",
        f"- Avg Brier on settled rows: `{summary['avg_brier']}`",
        "",
        "## Physics Tags",
        "",
    ]
    for key, value in summary["by_flag"].items():
        lines.append(
            f"- `{key}`: count={value['count']}, settled={value['settled']}, wins={value['wins']}, "
            f"gross=${value['gross_cents'] / 100.0:.2f}, avg_brier={value['avg_brier']}"
        )
    lines.extend(["", "## Entries", ""])
    if rows:
        lines.append("| market | side | p_side | ask | edge | depth | recross | v28-v22 p | old best | flags | result | gross c |")
        lines.append("|---|---|---:|---:|---:|---:|---:|---:|---|---|---|---:|")
        for row in rows:
            flags = ",".join(
                key
                for key in [
                    "h1_feed_fresh",
                    "h2_thin_touch_depth",
                    "h2_crowded_depth",
                    "h4_large_model_disagreement",
                    "h4_old_model_opposes_side",
                    "h5_late_high_sigma",
                    "h6_recross_hazard_high",
                ]
                if row.get(key) is True
            )
            lines.append(
                "| {market} | {side} | {p_side} | {ask_cents} | {edge_cents} | {eligible_depth} | {recross_hazard_score} | {v28_minus_v22_side_p} | {old_v22_best_side} | {flags} | {result} | {actual_gross_cents} |".format(
                    flags=flags,
                    **row,
                )
            )
    else:
        lines.append("No v28 approvals recorded yet.")
    REGISTRY_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    rows = build_rows()
    summary = summarize(rows)
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    write_csv(rows)
    REGISTRY_JSON.write_text(json.dumps({"summary": summary, "rows": rows}, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_md(rows, summary)
    print(str(REGISTRY_MD))


if __name__ == "__main__":
    main()
