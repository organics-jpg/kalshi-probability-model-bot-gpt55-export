"""Counterfactual v28 exit-policy diagnostics on forward shadow trades.

This does not change bot behavior. It evaluates predeclared exit variants
against settled forward trades so exit changes are judged before promotion.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Callable

from probe_v28_reactivated_shadow_status import read_events, reconstruct_trades, score_trade
from probe_v28_post_exit_path import build_rows as build_post_exit_rows


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
OUT_JSON = OUT_DIR / "v28_exit_policy_candidates_latest.json"
OUT_MD = OUT_DIR / "v28_exit_policy_candidates_latest.md"


def as_float(value: Any) -> float | None:
    if value is None or value == "":
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def exit_reason(row: dict[str, Any]) -> str:
    features = row.get("exit_features") if isinstance(row.get("exit_features"), dict) else {}
    return str(features.get("mushroom_v28_exit_reason") or row.get("exit_reason") or "")


def exit_p_hold(row: dict[str, Any]) -> float | None:
    features = row.get("exit_features") if isinstance(row.get("exit_features"), dict) else {}
    return as_float(features.get("mushroom_v28_p_hold"))


def exit_fair_drawdown(row: dict[str, Any]) -> float | None:
    features = row.get("exit_features") if isinstance(row.get("exit_features"), dict) else {}
    return as_float(features.get("mushroom_v28_fair_drawdown_cents"))


def is_value_over_hold(row: dict[str, Any]) -> bool:
    return exit_reason(row) == "mushroom_v28_exit_value_over_hold"


def is_probability_reduce(row: dict[str, Any]) -> bool:
    return exit_reason(row) == "mushroom_v28_probability_reduce"


def current_exit(row: dict[str, Any]) -> float | None:
    return as_float(row.get("actual_gross_cents"))


def hold_to_settlement(row: dict[str, Any]) -> float | None:
    return as_float(row.get("hold_gross_cents"))


def suppress_voh_when_p_hold_at_least(threshold: float) -> Callable[[dict[str, Any]], float | None]:
    def policy(row: dict[str, Any]) -> float | None:
        p_hold = exit_p_hold(row)
        if is_value_over_hold(row) and p_hold is not None and p_hold >= threshold:
            return hold_to_settlement(row)
        return current_exit(row)

    return policy


def suppress_probability_reduce_when_p_hold_at_least(threshold: float) -> Callable[[dict[str, Any]], float | None]:
    def policy(row: dict[str, Any]) -> float | None:
        p_hold = exit_p_hold(row)
        if is_probability_reduce(row) and p_hold is not None and p_hold >= threshold:
            return hold_to_settlement(row)
        return current_exit(row)

    return policy


def suppress_soft_exits_when_p_hold_ge_075(row: dict[str, Any]) -> float | None:
    p_hold = exit_p_hold(row)
    if p_hold is not None and p_hold >= 0.75 and (is_value_over_hold(row) or is_probability_reduce(row)):
        return hold_to_settlement(row)
    return current_exit(row)


def suppress_voh_when_thesis_not_broken(row: dict[str, Any]) -> float | None:
    p_hold = exit_p_hold(row)
    drawdown = exit_fair_drawdown(row)
    if is_value_over_hold(row) and p_hold is not None and drawdown is not None:
        if p_hold >= 0.75 and drawdown <= 5.0:
            return hold_to_settlement(row)
    return current_exit(row)


POLICIES: dict[str, Callable[[dict[str, Any]], float | None]] = {
    "current_v28_exit": current_exit,
    "hold_to_settlement_control": hold_to_settlement,
    "suppress_voh_p_hold_ge_075": suppress_voh_when_p_hold_at_least(0.75),
    "suppress_voh_p_hold_ge_080": suppress_voh_when_p_hold_at_least(0.80),
    "suppress_reduce_p_hold_ge_075": suppress_probability_reduce_when_p_hold_at_least(0.75),
    "suppress_reduce_p_hold_ge_080": suppress_probability_reduce_when_p_hold_at_least(0.80),
    "suppress_voh_or_reduce_p_hold_ge_075": suppress_soft_exits_when_p_hold_ge_075,
    "suppress_voh_p75_fair_drawdown_lte_5c": suppress_voh_when_thesis_not_broken,
}


def side_won(row: dict[str, Any]) -> bool | None:
    result = str(row.get("result") or "").lower()
    side = str(row.get("side") or "").lower()
    if result not in {"yes", "no"} or side not in {"yes", "no"}:
        return None
    return result == side


def build_rows() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for trade in reconstruct_trades(read_events()):
        score = score_trade(trade)
        if score.get("hold_gross_cents") is None:
            continue
        rows.append(score)
    return rows


def summarize_policy(name: str, fn: Callable[[dict[str, Any]], float | None], rows: list[dict[str, Any]]) -> dict[str, Any]:
    scored = []
    for row in rows:
        gross = fn(row)
        if gross is not None:
            scored.append((row, float(gross)))
    return {
        "policy": name,
        "trades": len(scored),
        "wins": sum(1 for _, gross in scored if gross >= 0),
        "losses": sum(1 for _, gross in scored if gross < 0),
        "gross_cents": sum(gross for _, gross in scored),
        "avg_gross_cents": (sum(gross for _, gross in scored) / len(scored)) if scored else None,
        "winner_clip_cents": sum(
            min(0.0, float(row.get("actual_gross_cents") or 0.0) - float(row.get("hold_gross_cents") or 0.0))
            for row, _ in scored
            if side_won(row) is True
        ),
    }


def build_report() -> dict[str, Any]:
    rows = build_rows()
    path_by_market = {str(row.get("market")): row for row in build_post_exit_rows()}
    summaries = [summarize_policy(name, fn, rows) for name, fn in POLICIES.items()]
    current = next((row for row in summaries if row["policy"] == "current_v28_exit"), None)
    if current:
        for row in summaries:
            row["delta_vs_current_cents"] = row["gross_cents"] - current["gross_cents"]
            policy_marks = []
            for trade_row in rows:
                gross = POLICIES[row["policy"]](trade_row)
                if gross is None:
                    continue
                path = path_by_market.get(str(trade_row.get("market")))
                if row["policy"] == "current_v28_exit" or path is None:
                    policy_marks.append(float(trade_row.get("actual_gross_cents") or gross))
                elif gross == trade_row.get("hold_gross_cents"):
                    mark = path.get("min_unrealized_hold_gross_cents")
                    policy_marks.append(float(mark if mark is not None else gross))
                else:
                    policy_marks.append(float(gross))
            row["worst_intratrade_mark_cents"] = min(policy_marks) if policy_marks else None
    detail_rows: list[dict[str, Any]] = []
    for row in rows:
        path = path_by_market.get(str(row.get("market"))) or {}
        detail = {
            "market": row.get("market"),
            "side": row.get("side"),
            "result": row.get("result"),
            "entry_cents": row.get("entry_cents"),
            "exit_cents": row.get("exit_cents"),
            "current_cents": row.get("actual_gross_cents"),
            "hold_cents": row.get("hold_gross_cents"),
            "exit_value_cents": row.get("exit_value_cents"),
            "exit_reason": exit_reason(row),
            "p_hold": exit_p_hold(row),
            "fair_drawdown_cents": exit_fair_drawdown(row),
            "worst_post_exit_hold_mark_cents": path.get("min_unrealized_hold_gross_cents"),
        }
        for name, fn in POLICIES.items():
            detail[name] = fn(row)
        detail_rows.append(detail)
    return {"summary": summaries, "rows": detail_rows}


def write_md(report: dict[str, Any]) -> None:
    lines = [
        "# v28 Exit Policy Candidates",
        "",
        "Counterfactual report on settled forward shadow trades only. These are candidates for shadowing, not promoted live rules.",
        "",
        "## Summary",
        "",
        "| policy | trades | wins | losses | gross c | avg c | delta vs current c | worst mark c | winner clip c |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for row in sorted(report["summary"], key=lambda item: item["gross_cents"], reverse=True):
        lines.append(
            "| {policy} | {trades} | {wins} | {losses} | {gross_cents} | {avg_gross_cents} | {delta_vs_current_cents} | {worst_intratrade_mark_cents} | {winner_clip_cents} |".format(
                **row
            )
        )
    lines.extend(
        [
            "",
            "## Rows",
            "",
            "| market | side | result | entry | exit | current c | hold c | exit value c | p_hold | drawdown c | worst hold mark c |",
            "|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|",
        ]
    )
    for row in report["rows"]:
        lines.append(
            "| {market} | {side} | {result} | {entry_cents} | {exit_cents} | {current_cents} | {hold_cents} | {exit_value_cents} | {p_hold} | {fair_drawdown_cents} | {worst_post_exit_hold_mark_cents} |".format(
                **row
            )
        )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    report = build_report()
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_md(report)
    print(str(OUT_MD))


if __name__ == "__main__":
    main()
