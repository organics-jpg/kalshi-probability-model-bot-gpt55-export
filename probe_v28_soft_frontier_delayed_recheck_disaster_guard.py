"""Disaster-guard scan for the delayed-recheck drop15 rescue.

Research-only; no live bot changes or orders.

The drop15 rescue improves diagnostic PnL versus the base delayed-recheck rule,
but its path-risk audit shows one large post-recheck adverse mark. This probe
simulates observable stop guards after the delayed recheck to see whether the
extra recovered PnL can survive a realistic account-survival constraint.
"""
from __future__ import annotations

import json
from collections import Counter
from datetime import timedelta
from typing import Any

from probe_v28_feature_gate_exit_bid_path_risk import OUT_DIR, fnum, load_json, parse_utc, to_eastern_naive, utc_now_iso
from probe_v28_post_exit_path import btc15m_close_time_from_ticker, held_bid, read_heartbeats


FRONTIER_JSON = OUT_DIR / "v28_soft_frontier_delayed_recheck_rescue_frontier_latest.json"
BOOK_GAP_JSON = OUT_DIR / "v28_frozen_exit_book_gap_suppression_latest.json"
REDUCE_JSON = OUT_DIR / "v28_frozen_exit_reduce_suppression_latest.json"
OUT_JSON = OUT_DIR / "v28_soft_frontier_delayed_recheck_disaster_guard_latest.json"
OUT_MD = OUT_DIR / "v28_soft_frontier_delayed_recheck_disaster_guard_latest.md"

PRIMARY_VARIANT = "drop15_bid60"
BASE_VARIANT = "base_delay60_bid60_drop10"

GUARDS = [
    {"name": "no_guard", "drop_from_recheck": None, "absolute_floor": None},
    {"name": "drop15_only", "drop_from_recheck": 15, "absolute_floor": None},
    {"name": "drop20_only", "drop_from_recheck": 20, "absolute_floor": None},
    {"name": "drop25_only", "drop_from_recheck": 25, "absolute_floor": None},
    {"name": "drop30_only", "drop_from_recheck": 30, "absolute_floor": None},
    {"name": "floor55_only", "drop_from_recheck": None, "absolute_floor": 55},
    {"name": "floor50_only", "drop_from_recheck": None, "absolute_floor": 50},
    {"name": "floor45_only", "drop_from_recheck": None, "absolute_floor": 45},
    {"name": "drop15_or_floor55", "drop_from_recheck": 15, "absolute_floor": 55},
    {"name": "drop20_or_floor50", "drop_from_recheck": 20, "absolute_floor": 50},
    {"name": "drop25_or_floor50", "drop_from_recheck": 25, "absolute_floor": 50},
    {"name": "drop25_or_floor45", "drop_from_recheck": 25, "absolute_floor": 45},
    {"name": "drop30_or_floor45", "drop_from_recheck": 30, "absolute_floor": 45},
    {"name": "drop30_or_floor40", "drop_from_recheck": 30, "absolute_floor": 40},
]


def variant_rows(name: str) -> list[dict[str, Any]]:
    payload = load_json(FRONTIER_JSON)
    for item in payload.get("variants") or []:
        if (item.get("variant") or {}).get("name") == name:
            return [row for row in item.get("scored_rows") or [] if isinstance(row, dict)]
    return []


def exit_ledger_rows() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for ledger_name, path in [("book_gap", BOOK_GAP_JSON), ("reduce", REDUCE_JSON)]:
        for row in load_json(path).get("rows") or []:
            if isinstance(row, dict):
                rows.append({**row, "ledger": ledger_name})
    return rows


def row_key(row: dict[str, Any]) -> tuple[str, str, str]:
    return (str(row.get("market") or ""), str(row.get("side") or ""), str(row.get("exit_ts") or ""))


def entry_cents_by_key() -> dict[tuple[str, str, str], float]:
    out: dict[tuple[str, str, str], float] = {}
    for row in exit_ledger_rows():
        entry = row.get("entry_cents")
        if entry is not None and row.get("exit_ts"):
            out[row_key(row)] = fnum(entry)
    return out


def path_after_exit(row: dict[str, Any], heartbeats: list[dict[str, Any]]) -> list[dict[str, Any]]:
    market = str(row.get("market") or "")
    side = str(row.get("side") or "")
    exit_ts = to_eastern_naive(parse_utc(row.get("exit_ts")))
    close_ts = to_eastern_naive(btc15m_close_time_from_ticker(market))
    points = [
        {**hb, "held_bid": held_bid(hb, side)}
        for hb in heartbeats
        if hb["market"] == market
        and exit_ts is not None
        and hb["ts"] >= exit_ts
        and (close_ts is None or hb["ts"] < close_ts)
    ]
    points.sort(key=lambda point: point["ts"])
    return points


def after_recheck_points(row: dict[str, Any], heartbeats: list[dict[str, Any]]) -> list[dict[str, Any]]:
    exit_ts = to_eastern_naive(parse_utc(row.get("exit_ts")))
    if exit_ts is None:
        return []
    recheck_ts = exit_ts + timedelta(seconds=60)
    return [point for point in path_after_exit(row, heartbeats) if point["ts"] >= recheck_ts]


def guard_trigger(
    row: dict[str, Any],
    guard: dict[str, Any],
    heartbeats: list[dict[str, Any]],
) -> dict[str, Any]:
    points = after_recheck_points(row, heartbeats)
    recheck_bid = fnum(row.get("recheck_bid"), None)
    if not points or recheck_bid is None:
        return {
            "guard_triggered": False,
            "guard_bid": None,
            "guard_ts": None,
            "min_bid_until_guard": None,
            "min_after_recheck_bid": None,
            "points_after_recheck": len(points),
        }
    bids = [fnum(point.get("held_bid")) for point in points]
    drop = guard.get("drop_from_recheck")
    floor = guard.get("absolute_floor")
    for point in points:
        bid = fnum(point.get("held_bid"), None)
        if bid is None:
            continue
        drop_hit = drop is not None and bid <= recheck_bid - float(drop)
        floor_hit = floor is not None and bid <= float(floor)
        if drop_hit or floor_hit:
            prefix = [fnum(p.get("held_bid")) for p in points if p["ts"] <= point["ts"]]
            return {
                "guard_triggered": True,
                "guard_bid": bid,
                "guard_ts": point["ts"].isoformat(),
                "guard_reason": "drop" if drop_hit else "floor",
                "min_bid_until_guard": min(prefix) if prefix else bid,
                "min_after_recheck_bid": min(bids),
                "points_after_recheck": len(points),
            }
    return {
        "guard_triggered": False,
        "guard_bid": None,
        "guard_ts": None,
        "guard_reason": None,
        "min_bid_until_guard": min(bids) if bids else None,
        "min_after_recheck_bid": min(bids) if bids else None,
        "points_after_recheck": len(points),
    }


def score_guard(
    guard: dict[str, Any],
    rows: list[dict[str, Any]],
    base_rows: list[dict[str, Any]],
    entry_lookup: dict[tuple[str, str, str], float],
    heartbeats: list[dict[str, Any]],
) -> dict[str, Any]:
    base_by_key = {row_key(row): row for row in base_rows}
    scored: list[dict[str, Any]] = []
    for row in rows:
        key = row_key(row)
        weight = fnum(row.get("entry_weight"), 1.0)
        current = fnum(row.get("current_cents"))
        hold = fnum(row.get("hold_cents"))
        base_candidate = fnum((base_by_key.get(key) or {}).get("frontier_candidate_cents"), fnum(row.get("weighted_candidate_cents")))
        suppress = bool(row.get("frontier_suppressed"))
        trigger = guard_trigger(row, guard, heartbeats) if suppress else {}
        entry_cents = entry_lookup.get(key)
        if suppress and trigger.get("guard_triggered") and entry_cents is not None:
            candidate = 2.0 * (fnum(trigger.get("guard_bid")) - entry_cents)
            disposition = "guard_exit"
        elif suppress:
            candidate = hold
            disposition = "hold_to_settlement"
        else:
            candidate = current
            disposition = "original_exit"
        out = {
            **row,
            "guard": guard.get("name"),
            "entry_cents": entry_cents,
            "guard_candidate_cents": candidate,
            "guard_weighted_candidate_cents": weight * candidate,
            "guard_weighted_delta_vs_current_cents": weight * (candidate - current),
            "guard_weighted_delta_vs_base_cents": weight * (candidate - base_candidate),
            "guard_disposition": disposition,
            **trigger,
        }
        scored.append(out)
    suppressed = [row for row in scored if row.get("frontier_suppressed")]
    guarded = [row for row in scored if row.get("guard_disposition") == "guard_exit"]
    helpful = [row for row in suppressed if fnum(row.get("guard_weighted_delta_vs_current_cents")) > 0]
    harmful = [row for row in suppressed if fnum(row.get("guard_weighted_delta_vs_current_cents")) < 0]
    missing_entry = [row for row in suppressed if row.get("entry_cents") is None]
    base_net = sum(fnum((base_by_key.get(row_key(row)) or {}).get("frontier_weighted_candidate_cents"), fnum(row.get("weighted_candidate_cents"))) for row in rows)
    no_guard_net = sum(fnum(row.get("frontier_weighted_candidate_cents")) for row in rows)
    net = sum(fnum(row.get("guard_weighted_candidate_cents")) for row in scored)
    losses = [row for row in scored if fnum(row.get("guard_weighted_candidate_cents")) < 0]
    path_rows = [row for row in suppressed if row.get("min_bid_until_guard") is not None]
    min_until_guard = [fnum(row.get("min_bid_until_guard")) - fnum(row.get("recheck_bid")) for row in path_rows]
    min_after_recheck = [fnum(row.get("min_after_recheck_bid")) - fnum(row.get("recheck_bid")) for row in path_rows if row.get("min_after_recheck_bid") is not None]
    blockers: list[str] = ["diagnostic_prefreeze"]
    if missing_entry:
        blockers.append("missing_entry_cents")
    if len(harmful) > 0:
        blockers.append("guarded_harmful_vs_original_exit")
    if net <= base_net:
        blockers.append("does_not_improve_base_delayed_recheck")
    if net <= 0:
        blockers.append("net_not_positive")
    if min_until_guard and min(min_until_guard) <= -25.0:
        blockers.append("large_adverse_before_guard")
    if min_until_guard and min(min_until_guard) <= -50.0:
        blockers.append("extreme_adverse_before_guard")
    return {
        "guard": guard,
        "rows": len(scored),
        "suppressed": len(suppressed),
        "guarded_exits": len(guarded),
        "helpful_suppressed": len(helpful),
        "harmful_suppressed": len(harmful),
        "base_delayed_net_cents": base_net,
        "drop15_no_guard_net_cents": no_guard_net,
        "candidate_net_cents": net,
        "delta_vs_base_delayed_cents": net - base_net,
        "delta_vs_drop15_no_guard_cents": net - no_guard_net,
        "losses": len(losses),
        "loss_cents": sum(fnum(row.get("guard_weighted_candidate_cents")) for row in losses),
        "worst_min_until_guard_from_recheck_cents": min(min_until_guard) if min_until_guard else None,
        "worst_min_after_recheck_from_recheck_cents": min(min_after_recheck) if min_after_recheck else None,
        "source_counts": dict(Counter(str(row.get("source") or "unknown") for row in suppressed)),
        "disposition_counts": dict(Counter(str(row.get("guard_disposition") or "unknown") for row in scored)),
        "blockers": blockers,
        "scored_rows": scored,
    }


def build_report() -> dict[str, Any]:
    rows = variant_rows(PRIMARY_VARIANT)
    base_rows = variant_rows(BASE_VARIANT)
    entry_lookup = entry_cents_by_key()
    heartbeats = read_heartbeats()
    guards = [score_guard(guard, rows, base_rows, entry_lookup, heartbeats) for guard in GUARDS]
    guards.sort(
        key=lambda item: (
            len([b for b in item.get("blockers") or [] if b != "diagnostic_prefreeze"]),
            int(item.get("harmful_suppressed") or 0),
            -float(item.get("candidate_net_cents") or -999999),
        )
    )
    best = guards[0] if guards else {}
    return {
        "generated_at_utc": utc_now_iso(),
        "frontier_source": str(FRONTIER_JSON),
        "primary_variant": PRIMARY_VARIANT,
        "base_variant": BASE_VARIANT,
        "guards": guards,
        "interpretation": [
            "Research-only disaster-guard scan; no live bot changes or orders.",
            (
                f"Best guard {((best.get('guard') or {}).get('name'))} has net "
                f"{best.get('candidate_net_cents')}c, delta vs base "
                f"{best.get('delta_vs_base_delayed_cents')}c, guarded exits "
                f"{best.get('guarded_exits')}, helpful/harmful "
                f"{best.get('helpful_suppressed')}/{best.get('harmful_suppressed')}, "
                f"worst pre-guard excursion {best.get('worst_min_until_guard_from_recheck_cents')}c, "
                f"blockers {best.get('blockers')}."
            ) if best else "No rows scored.",
            "A guard is only interesting if it preserves improvement over base while removing large adverse path risk.",
        ],
    }


def fmt(value: Any) -> str:
    if value is None:
        return "n/a"
    if isinstance(value, float):
        return f"{value:.2f}"
    return str(value)


def write_md(report: dict[str, Any]) -> None:
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8")
    lines = [
        "# v28 Soft-Frontier Delayed-Recheck Disaster Guard",
        "",
        "Research-only diagnostic scan. No live bot changes or orders.",
        "",
        f"- Generated UTC: `{report.get('generated_at_utc')}`",
        f"- Primary rescue variant: `{report.get('primary_variant')}`",
        f"- Base comparison variant: `{report.get('base_variant')}`",
        "",
        "## Interpretation",
        "",
    ]
    lines.extend(f"- {note}" for note in report.get("interpretation") or [])
    lines.extend(
        [
            "",
            "## Guards",
            "",
            "| rank | guard | guarded exits | H/H | base net | no-guard net | guarded net | delta base | delta no guard | losses | worst pre-guard | blockers |",
            "|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|",
        ]
    )
    for idx, item in enumerate(report.get("guards") or [], start=1):
        guard = item.get("guard") or {}
        lines.append(
            f"| {idx} | `{guard.get('name')}` | {item.get('guarded_exits')} | "
            f"{item.get('helpful_suppressed')}/{item.get('harmful_suppressed')} | "
            f"{fmt(item.get('base_delayed_net_cents'))} | {fmt(item.get('drop15_no_guard_net_cents'))} | "
            f"{fmt(item.get('candidate_net_cents'))} | {fmt(item.get('delta_vs_base_delayed_cents'))} | "
            f"{fmt(item.get('delta_vs_drop15_no_guard_cents'))} | {item.get('losses')} | "
            f"{fmt(item.get('worst_min_until_guard_from_recheck_cents'))} | "
            f"{', '.join(item.get('blockers') or [])} |"
        )
    lines.extend(
        [
            "",
            "## Worst Rows By Best Guard",
            "",
            "| market | side | source | reason | entry | recheck | min until guard | min after recheck | disposition | guard bid | weighted candidate | delta vs current |",
            "|---|---|---|---|---:|---:|---:|---:|---|---:|---:|---:|",
        ]
    )
    best_rows = ((report.get("guards") or [{}])[0].get("scored_rows") or []) if report.get("guards") else []
    best_rows = sorted(
        best_rows,
        key=lambda row: fnum(row.get("min_bid_until_guard"), 999.0) - fnum(row.get("recheck_bid"), 0.0),
    )
    for row in best_rows[:30]:
        min_until = None
        if row.get("min_bid_until_guard") is not None and row.get("recheck_bid") is not None:
            min_until = fnum(row.get("min_bid_until_guard")) - fnum(row.get("recheck_bid"))
        min_after = None
        if row.get("min_after_recheck_bid") is not None and row.get("recheck_bid") is not None:
            min_after = fnum(row.get("min_after_recheck_bid")) - fnum(row.get("recheck_bid"))
        lines.append(
            f"| {row.get('market')} | {row.get('side')} | {row.get('source')} | {row.get('exit_reason')} | "
            f"{fmt(row.get('entry_cents'))} | {fmt(row.get('recheck_bid'))} | {fmt(min_until)} | {fmt(min_after)} | "
            f"{row.get('guard_disposition')} | {fmt(row.get('guard_bid'))} | "
            f"{fmt(row.get('guard_weighted_candidate_cents'))} | {fmt(row.get('guard_weighted_delta_vs_current_cents'))} |"
        )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    report = build_report()
    write_md(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
