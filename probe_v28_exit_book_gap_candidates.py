"""Book-gap exit diagnostics for v28.

Research-only; no live bot changes or orders.

Tests whether soft exits should be suppressed when v28's held-side fair value
is materially above the executable exit bid. This is the exit-side analogue of
the raw/book disagreement trajectory diagnostics.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Callable

from probe_v28_exit_policy_candidates import build_rows, current_exit, hold_to_settlement
from probe_v28_post_exit_path import build_rows as build_post_exit_rows


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
OUT_JSON = OUT_DIR / "v28_exit_book_gap_candidates_latest.json"
OUT_MD = OUT_DIR / "v28_exit_book_gap_candidates_latest.md"


def as_float(value: Any) -> float | None:
    if value is None or value == "":
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def exit_features(row: dict[str, Any]) -> dict[str, Any]:
    return row.get("exit_features") if isinstance(row.get("exit_features"), dict) else {}


def exit_reason(row: dict[str, Any]) -> str:
    return str(exit_features(row).get("mushroom_v28_exit_reason") or row.get("exit_reason") or "")


def is_soft_exit(row: dict[str, Any]) -> bool:
    return exit_reason(row) in {"mushroom_v28_exit_value_over_hold", "mushroom_v28_probability_reduce"}


def is_collapse(row: dict[str, Any]) -> bool:
    return exit_reason(row) == "mushroom_v28_probability_collapse_full"


def p_hold(row: dict[str, Any]) -> float | None:
    return as_float(exit_features(row).get("mushroom_v28_p_hold"))


def exit_bid_prob(row: dict[str, Any]) -> float | None:
    bid = as_float(exit_features(row).get("mushroom_v28_exit_bid_cents"))
    return None if bid is None else bid / 100.0


def fair_drawdown(row: dict[str, Any]) -> float | None:
    return as_float(exit_features(row).get("mushroom_v28_fair_drawdown_cents"))


def hold_book_gap(row: dict[str, Any]) -> float | None:
    p = p_hold(row)
    bid = exit_bid_prob(row)
    return None if p is None or bid is None else p - bid


def suppress_soft_gap(threshold: float) -> Callable[[dict[str, Any]], float | None]:
    def policy(row: dict[str, Any]) -> float | None:
        gap = hold_book_gap(row)
        if is_soft_exit(row) and gap is not None and gap >= threshold:
            return hold_to_settlement(row)
        return current_exit(row)

    return policy


def suppress_soft_gap15_or_p75(row: dict[str, Any]) -> float | None:
    gap = hold_book_gap(row)
    p = p_hold(row)
    if is_soft_exit(row) and ((gap is not None and gap >= 0.15) or (p is not None and p >= 0.75)):
        return hold_to_settlement(row)
    return current_exit(row)


def suppress_soft_gap15_drawdown_lte5(row: dict[str, Any]) -> float | None:
    gap = hold_book_gap(row)
    drawdown = fair_drawdown(row)
    if is_soft_exit(row) and gap is not None and gap >= 0.15 and drawdown is not None and drawdown <= 5.0:
        return hold_to_settlement(row)
    return current_exit(row)


def suppress_reduce_gap15_keep_collapse(row: dict[str, Any]) -> float | None:
    gap = hold_book_gap(row)
    if exit_reason(row) == "mushroom_v28_probability_reduce" and gap is not None and gap >= 0.15:
        return hold_to_settlement(row)
    return current_exit(row)


POLICIES: dict[str, Callable[[dict[str, Any]], float | None]] = {
    "current_v28_exit": current_exit,
    "hold_to_settlement_control": hold_to_settlement,
    "suppress_soft_exit_hold_book_gap_ge_10pp": suppress_soft_gap(0.10),
    "suppress_soft_exit_hold_book_gap_ge_15pp": suppress_soft_gap(0.15),
    "suppress_soft_exit_hold_book_gap_ge_20pp": suppress_soft_gap(0.20),
    "suppress_soft_gap15_or_p_hold75": suppress_soft_gap15_or_p75,
    "suppress_soft_gap15_drawdown_lte5": suppress_soft_gap15_drawdown_lte5,
    "suppress_reduce_gap15_keep_collapse": suppress_reduce_gap15_keep_collapse,
}


def side_won(row: dict[str, Any]) -> bool | None:
    result = str(row.get("result") or "").lower()
    side = str(row.get("side") or "").lower()
    if result not in {"yes", "no"} or side not in {"yes", "no"}:
        return None
    return result == side


def summarize_policy(name: str, fn: Callable[[dict[str, Any]], float | None], rows: list[dict[str, Any]]) -> dict[str, Any]:
    scored = []
    for row in rows:
        gross = fn(row)
        if gross is not None:
            scored.append((row, float(gross)))
    return {
        "policy": name,
        "trades": len(scored),
        "wins": sum(1 for _, gross in scored if gross >= 0.0),
        "losses": sum(1 for _, gross in scored if gross < 0.0),
        "gross_cents": sum(gross for _, gross in scored),
        "avg_gross_cents": (sum(gross for _, gross in scored) / len(scored)) if scored else None,
        "suppressed_exits": sum(1 for row, gross in scored if gross == hold_to_settlement(row) and current_exit(row) != hold_to_settlement(row)),
        "suppressed_collapse_exits": sum(1 for row, gross in scored if is_collapse(row) and gross == hold_to_settlement(row) and current_exit(row) != hold_to_settlement(row)),
        "winner_clip_cents": sum(
            min(0.0, float(row.get("actual_gross_cents") or 0.0) - float(row.get("hold_gross_cents") or 0.0))
            for row, _ in scored
            if side_won(row) is True
        ),
    }


def worst_mark_for_policy(name: str, rows: list[dict[str, Any]]) -> float | None:
    path_by_market = {str(row.get("market")): row for row in build_post_exit_rows()}
    marks = []
    for row in rows:
        gross = POLICIES[name](row)
        if gross is None:
            continue
        if gross == hold_to_settlement(row) and current_exit(row) != hold_to_settlement(row):
            path = path_by_market.get(str(row.get("market"))) or {}
            mark = path.get("min_unrealized_hold_gross_cents")
            marks.append(float(mark if mark is not None else gross))
        else:
            marks.append(float(gross))
    return min(marks) if marks else None


def build_report() -> dict[str, Any]:
    rows = [row for row in build_rows() if row.get("hold_gross_cents") is not None]
    summaries = [summarize_policy(name, fn, rows) for name, fn in POLICIES.items()]
    current = next((row for row in summaries if row["policy"] == "current_v28_exit"), {})
    for summary in summaries:
        summary["delta_vs_current_cents"] = float(summary["gross_cents"]) - float(current.get("gross_cents") or 0.0)
        summary["worst_intratrade_mark_cents"] = worst_mark_for_policy(str(summary["policy"]), rows)
    details = []
    for row in rows:
        detail = {
            "market": row.get("market"),
            "side": row.get("side"),
            "result": row.get("result"),
            "exit_reason": exit_reason(row),
            "current_cents": current_exit(row),
            "hold_cents": hold_to_settlement(row),
            "exit_value_cents": row.get("exit_value_cents"),
            "p_hold": p_hold(row),
            "exit_bid_prob": exit_bid_prob(row),
            "hold_book_gap": hold_book_gap(row),
            "fair_drawdown_cents": fair_drawdown(row),
        }
        for name, fn in POLICIES.items():
            detail[name] = fn(row)
        details.append(detail)
    summaries.sort(key=lambda item: float(item.get("gross_cents") or -999999.0), reverse=True)
    return {
        "summary": summaries,
        "rows": details,
        "interpretation": current_read(summaries),
    }


def current_read(summaries: list[dict[str, Any]]) -> list[str]:
    best = summaries[0] if summaries else {}
    current = next((row for row in summaries if row.get("policy") == "current_v28_exit"), {})
    return [
        f"Best book-gap exit policy is {best.get('policy')} with gross {best.get('gross_cents')}c and delta {best.get('delta_vs_current_cents')}c vs current.",
        f"Current v28 exit gross is {current.get('gross_cents')}c over {current.get('trades')} trades.",
        "This is diagnostic only; forward promotion needs a frozen validator with future rows.",
    ]


def fmt(value: Any) -> str:
    if value is None:
        return "None"
    if isinstance(value, float):
        return f"{value:.6f}"
    return str(value)


def write_md(report: dict[str, Any]) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8")
    lines = [
        "# v28 Exit Book-Gap Candidates",
        "",
        "Research-only exit diagnostics using p_hold minus executable exit bid.",
        "",
        "## Current Read",
        "",
    ]
    for note in report.get("interpretation") or []:
        lines.append(f"- {note}")
    lines.extend([
        "",
        "## Summary",
        "",
        "| policy | trades | W/L | gross c | delta c | suppressed | suppressed collapse | worst mark c | winner clip c |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|",
    ])
    for row in report.get("summary") or []:
        lines.append(
            f"| `{row.get('policy')}` | {row.get('trades')} | {row.get('wins')}/{row.get('losses')} | "
            f"{fmt(row.get('gross_cents'))} | {fmt(row.get('delta_vs_current_cents'))} | "
            f"{row.get('suppressed_exits')} | {row.get('suppressed_collapse_exits')} | "
            f"{fmt(row.get('worst_intratrade_mark_cents'))} | {fmt(row.get('winner_clip_cents'))} |"
        )
    lines.extend([
        "",
        "## Rows",
        "",
        "| market | side | result | reason | current | hold | p_hold | bid | gap | drawdown |",
        "|---|---|---|---|---:|---:|---:|---:|---:|---:|",
    ])
    for row in report.get("rows") or []:
        lines.append(
            f"| `{row.get('market')}` | {row.get('side')} | {row.get('result')} | `{row.get('exit_reason')}` | "
            f"{fmt(row.get('current_cents'))} | {fmt(row.get('hold_cents'))} | {fmt(row.get('p_hold'))} | "
            f"{fmt(row.get('exit_bid_prob'))} | {fmt(row.get('hold_book_gap'))} | {fmt(row.get('fair_drawdown_cents'))} |"
        )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    report = build_report()
    write_md(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
