"""Observable rescue frontier for delayed-recheck false negatives.

Research-only; no live bot changes or orders.

The broad delayed-recheck candidate leaves several unsuppressed exits where
holding would have recovered the loss. This diagnostic scans observable relaxes
of the recheck rule to see whether those false negatives can be recovered
without also suppressing true loss-control exits.
"""
from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Any

from probe_v28_soft_frontier_midprice_delayed_recheck_path_risk import OUT_DIR, fnum, load_json, utc_now_iso


WATCH_JSON = OUT_DIR / "v28_frozen_soft_frontier_midprice_delayed_recheck_exit_latest.json"
OUT_JSON = OUT_DIR / "v28_soft_frontier_delayed_recheck_rescue_frontier_latest.json"
OUT_MD = OUT_DIR / "v28_soft_frontier_delayed_recheck_rescue_frontier_latest.md"


VARIANTS = [
    {"name": "base_delay60_bid60_drop10", "bid_floor": 60, "max_drop": 10, "p_hold_floor": None, "fair_drawdown_max": None, "exit_bid_floor": None},
    {"name": "drop11_bid60", "bid_floor": 60, "max_drop": 11, "p_hold_floor": None, "fair_drawdown_max": None, "exit_bid_floor": None},
    {"name": "drop15_bid60", "bid_floor": 60, "max_drop": 15, "p_hold_floor": None, "fair_drawdown_max": None, "exit_bid_floor": None},
    {"name": "drop20_bid60", "bid_floor": 60, "max_drop": 20, "p_hold_floor": None, "fair_drawdown_max": None, "exit_bid_floor": None},
    {"name": "bid45_drop15_phold60", "bid_floor": 45, "max_drop": 15, "p_hold_floor": 0.60, "fair_drawdown_max": 12, "exit_bid_floor": 55},
    {"name": "bid40_drop20_phold60", "bid_floor": 40, "max_drop": 20, "p_hold_floor": 0.60, "fair_drawdown_max": 12, "exit_bid_floor": 55},
    {"name": "bid40_drop20_phold55", "bid_floor": 40, "max_drop": 20, "p_hold_floor": 0.55, "fair_drawdown_max": 12, "exit_bid_floor": 55},
    {"name": "bid40_drop20_phold50", "bid_floor": 40, "max_drop": 20, "p_hold_floor": 0.50, "fair_drawdown_max": 16, "exit_bid_floor": 55},
    {"name": "low_bid_value_exit_phold50", "bid_floor": 40, "max_drop": 45, "p_hold_floor": 0.50, "fair_drawdown_max": 30, "exit_bid_floor": 50, "exit_reason": "mushroom_v28_exit_value_over_hold"},
    {"name": "collapse_rescue_phold60_drop12", "bid_floor": 55, "max_drop": 12, "p_hold_floor": 0.60, "fair_drawdown_max": 8, "exit_bid_floor": 60, "exit_reason": "mushroom_v28_probability_collapse_full"},
]


def diagnostic_rows() -> list[dict[str, Any]]:
    payload = load_json(WATCH_JSON)
    for lane in payload.get("lanes") or []:
        if lane.get("lane") == "diagnostic_prefreeze_context":
            return [row for row in lane.get("rows") or [] if isinstance(row, dict)]
    return []


def passes(row: dict[str, Any], variant: dict[str, Any]) -> bool:
    recheck_bid = fnum(row.get("recheck_bid"), None)
    drop = fnum(row.get("window_drop_cents"), None)
    exit_bid = fnum(row.get("exit_bid"), None)
    p_hold = fnum(row.get("p_hold"), None)
    fair_drawdown = fnum(row.get("fair_drawdown_cents"), None)
    if variant.get("exit_reason") and str(row.get("exit_reason") or "") != str(variant["exit_reason"]):
        return False
    if recheck_bid is None or recheck_bid < float(variant["bid_floor"]):
        return False
    if drop is None or drop > float(variant["max_drop"]):
        return False
    if variant.get("exit_bid_floor") is not None and (exit_bid is None or exit_bid < float(variant["exit_bid_floor"])):
        return False
    if variant.get("p_hold_floor") is not None and (p_hold is None or p_hold < float(variant["p_hold_floor"])):
        return False
    if variant.get("fair_drawdown_max") is not None and (fair_drawdown is None or fair_drawdown > float(variant["fair_drawdown_max"])):
        return False
    return True


def evaluate(variant: dict[str, Any], rows: list[dict[str, Any]]) -> dict[str, Any]:
    scored = []
    for row in rows:
        suppress = passes(row, variant)
        current = fnum(row.get("current_cents"))
        hold = fnum(row.get("hold_cents"))
        weight = fnum(row.get("entry_weight"), 1.0)
        candidate = hold if suppress else current
        out = dict(row)
        out.update(
            {
                "frontier_suppressed": suppress,
                "frontier_candidate_cents": candidate,
                "frontier_weighted_candidate_cents": weight * candidate,
                "frontier_weighted_delta_cents": weight * (candidate - current),
            }
        )
        scored.append(out)
    suppressed = [row for row in scored if row.get("frontier_suppressed")]
    helpful = [row for row in suppressed if fnum(row.get("frontier_weighted_delta_cents")) > 0]
    harmful = [row for row in suppressed if fnum(row.get("frontier_weighted_delta_cents")) < 0]
    net = sum(fnum(row.get("frontier_weighted_candidate_cents")) for row in scored)
    current_net = sum(fnum(row.get("weighted_current_cents")) for row in scored)
    base_net = sum(fnum(row.get("weighted_candidate_cents")) for row in scored)
    losses = [row for row in scored if fnum(row.get("frontier_weighted_candidate_cents")) < 0]
    blockers: list[str] = ["diagnostic_prefreeze"]
    if len(harmful) > 0:
        blockers.append("suppressed_losers_present")
    if net <= base_net:
        blockers.append("does_not_improve_base_delayed_recheck")
    if len(suppressed) < 30:
        blockers.append("suppressed_decisions_lt_30")
    if net <= 0:
        blockers.append("net_not_positive")
    return {
        "variant": variant,
        "rows": len(scored),
        "suppressed": len(suppressed),
        "helpful_suppressed": len(helpful),
        "harmful_suppressed": len(harmful),
        "current_net_cents": current_net,
        "base_delayed_net_cents": base_net,
        "candidate_net_cents": net,
        "delta_vs_current_cents": net - current_net,
        "delta_vs_base_delayed_cents": net - base_net,
        "losses": len(losses),
        "loss_cents": sum(fnum(row.get("frontier_weighted_candidate_cents")) for row in losses),
        "source_counts": dict(Counter(str(row.get("source") or "unknown") for row in suppressed)),
        "exit_reason_counts": dict(Counter(str(row.get("exit_reason") or "unknown") for row in suppressed)),
        "blockers": blockers,
        "scored_rows": scored,
    }


def build_report() -> dict[str, Any]:
    rows = diagnostic_rows()
    variants = [evaluate(variant, rows) for variant in VARIANTS]
    variants.sort(
        key=lambda row: (
            len([b for b in row.get("blockers") or [] if b != "diagnostic_prefreeze"]),
            int(row.get("harmful_suppressed") or 0),
            -float(row.get("candidate_net_cents") or -999999),
        )
    )
    best = variants[0] if variants else {}
    return {
        "generated_at_utc": utc_now_iso(),
        "watch_source": str(WATCH_JSON),
        "variants": variants,
        "interpretation": [
            "Research-only false-negative rescue frontier; no live bot changes or orders.",
            (
                f"Best diagnostic relax {((best.get('variant') or {}).get('name'))} has "
                f"net {best.get('candidate_net_cents')}c, delta vs base {best.get('delta_vs_base_delayed_cents')}c, "
                f"helpful/harmful {best.get('helpful_suppressed')}/{best.get('harmful_suppressed')}, "
                f"blockers {best.get('blockers')}."
            ) if best else "No rows scored.",
            "Any green relax is only a hypothesis until frozen and proven post-birth.",
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
        "# v28 Soft-Frontier Delayed-Recheck Rescue Frontier",
        "",
        "Research-only diagnostic frontier. No live bot changes or orders.",
        "",
        f"- Generated UTC: `{report.get('generated_at_utc')}`",
        "",
        "## Interpretation",
        "",
    ]
    lines.extend(f"- {note}" for note in report.get("interpretation") or [])
    lines.extend(
        [
            "",
            "## Variants",
            "",
            "| rank | variant | suppressed | H/H | base net | candidate net | delta base | losses | loss c | source counts | exit reasons | blockers |",
            "|---:|---|---:|---:|---:|---:|---:|---:|---:|---|---|---|",
        ]
    )
    for idx, item in enumerate(report.get("variants") or [], start=1):
        variant = item.get("variant") or {}
        lines.append(
            f"| {idx} | `{variant.get('name')}` | {item.get('suppressed')} | "
            f"{item.get('helpful_suppressed')}/{item.get('harmful_suppressed')} | "
            f"{fmt(item.get('base_delayed_net_cents'))} | {fmt(item.get('candidate_net_cents'))} | "
            f"{fmt(item.get('delta_vs_base_delayed_cents'))} | {item.get('losses')} | "
            f"{fmt(item.get('loss_cents'))} | {item.get('source_counts')} | {item.get('exit_reason_counts')} | "
            f"{', '.join(item.get('blockers') or [])} |"
        )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    report = build_report()
    write_md(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
