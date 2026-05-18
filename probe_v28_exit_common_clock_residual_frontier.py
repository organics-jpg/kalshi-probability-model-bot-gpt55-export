"""Residual rescue frontier for strict common-clock exit watches.

Research-only; no live bot changes, no process control, no orders.

The current best strict common-clock exit guard is positive but sparse. This
probe tests small observable residual suppressions on rows that the base guard
does not suppress, so we can separate clean clipped-winner rescue from
false-hold risk before freezing any child watch.
"""
from __future__ import annotations

import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

import probe_v28_exit_policy_common_clock_watch as cc


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
OUT_JSON = OUT_DIR / "v28_exit_common_clock_residual_frontier_latest.json"
OUT_MD = OUT_DIR / "v28_exit_common_clock_residual_frontier_latest.md"

TARGET_WINDOWS = [
    "new_exit_mix_common_forward_v2",
    "new_exit_mix_common_forward_v3",
]
BASE_POLICY = "loss_guard_value_p85_reduce_p79_gap0"
MIN_SETTLED = 30
MIN_TOTAL_SUPPRESSED = 30
MIN_RESIDUAL_SUPPRESSED = 10
MIN_CUSHION_CENTS = 300.0


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


def fnum(value: Any, default: float = 0.0) -> float:
    if value is None or value == "":
        return default
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def tags(row: dict[str, Any]) -> set[str]:
    return set(cc.suppression_tags(row))


def exit_reason_text(row: dict[str, Any]) -> str:
    return str(cc.exit_reason(row) or "")


def p_hold(row: dict[str, Any]) -> float | None:
    return cc.exit_p_hold(row)


def gap(row: dict[str, Any]) -> float | None:
    return cc.hold_book_gap(row)


def drawdown(row: dict[str, Any]) -> float | None:
    return cc.exit_fair_drawdown(row)


def exit_price(row: dict[str, Any]) -> float | None:
    return cc.exit_price_cents(row)


def is_low_p(row: dict[str, Any]) -> bool:
    value = p_hold(row)
    return value is not None and value < 0.75


def is_collapse(row: dict[str, Any]) -> bool:
    return "collapse_full" in exit_reason_text(row)


def predicates() -> dict[str, Callable[[dict[str, Any]], bool]]:
    return {
        "collapse_full_any": is_collapse,
        "collapse_full_low_p": lambda row: is_collapse(row) and is_low_p(row),
        "collapse_full_low_p_exit_below70": (
            lambda row: is_collapse(row) and is_low_p(row) and fnum(exit_price(row), 999.0) < 70.0
        ),
        "collapse_full_low_p_gap_0_to_15pp": (
            lambda row: (
                is_collapse(row)
                and is_low_p(row)
                and gap(row) is not None
                and 0.0 <= fnum(gap(row)) < 0.15
            )
        ),
        "low_p_book_gap_5_to_15pp": (
            lambda row: is_low_p(row) and gap(row) is not None and 0.05 <= fnum(gap(row)) < 0.15
        ),
        "low_p_exit_below70_gap_nonnegative": (
            lambda row: is_low_p(row) and fnum(exit_price(row), 999.0) < 70.0 and fnum(gap(row), -999.0) >= 0.0
        ),
        "prob_reduce_p75_79_gap_0_to_5pp": (
            lambda row: (
                "probability_reduce" in tags(row)
                and 0.75 <= fnum(p_hold(row), -999.0) < 0.79
                and 0.0 <= fnum(gap(row), -999.0) < 0.05
            )
        ),
        "prob_reduce_p75_79_exit70_79": (
            lambda row: (
                "probability_reduce" in tags(row)
                and 0.75 <= fnum(p_hold(row), -999.0) < 0.79
                and 70.0 <= fnum(exit_price(row), -999.0) < 80.0
            )
        ),
        "value_low_p_book_negative": (
            lambda row: "value_over_hold" in tags(row) and is_low_p(row) and fnum(gap(row), 999.0) < 0.0
        ),
        "value_low_p_book_negative_exit_below70": (
            lambda row: (
                "value_over_hold" in tags(row)
                and is_low_p(row)
                and fnum(gap(row), 999.0) < 0.0
                and fnum(exit_price(row), 999.0) < 70.0
            )
        ),
        "fair_drawdown_positive_low_p": (
            lambda row: is_low_p(row) and fnum(drawdown(row), -999.0) > 0.0
        ),
    }


def compact(row: dict[str, Any], current: float, hold: float, reason: str) -> dict[str, Any]:
    return {
        "market": row.get("market"),
        "side": row.get("side"),
        "result": row.get("result"),
        "side_won": cc.side_won(row),
        "entry_ts": row.get("entry_ts"),
        "exit_ts": row.get("exit_ts"),
        "exit_reason": cc.exit_reason(row),
        "p_hold": p_hold(row),
        "hold_book_gap": gap(row),
        "fair_drawdown_cents": drawdown(row),
        "exit_price_cents": exit_price(row),
        "current_cents": current,
        "hold_cents": hold,
        "delta_cents": hold - current,
        "residual_reason": reason,
        "tags": cc.suppression_tags(row),
    }


def base_pair() -> tuple[Callable[[dict[str, Any]], float | None], Callable[[dict[str, Any]], bool]]:
    state = cc.loss_guard_load_json(cc.LOSS_GUARD_STATE_JSON)
    return cc.loss_guard_policy(state), lambda row: cc.should_loss_guard_suppress(row, state)


def summarize_window(window: str, freeze_ts: str | None) -> dict[str, Any]:
    rows = cc.filter_snapshot(cc.build_scored_rows(), freeze_ts)
    base_policy, base_suppress = base_pair()
    base_suppressed = []
    candidates = []
    pred_map = predicates()
    for name, pred in pred_map.items():
        current_vals: list[float] = []
        base_vals: list[float] = []
        candidate_vals: list[float] = []
        residual_rows: list[dict[str, Any]] = []
        base_rows = 0
        for row in rows:
            current = cc.current_exit(row)
            hold = cc.hold_to_settlement(row)
            base = base_policy(row)
            if current is None or hold is None or base is None:
                continue
            cur_f = float(current)
            hold_f = float(hold)
            base_f = float(base)
            suppress_base = base_suppress(row)
            suppress_residual = (not suppress_base) and pred(row)
            current_vals.append(cur_f)
            base_vals.append(base_f)
            candidate_vals.append(hold_f if suppress_residual else base_f)
            if suppress_base:
                base_rows += 1
                base_suppressed.append(row)
            if suppress_residual:
                residual_rows.append(compact(row, cur_f, hold_f, name))
        helpful = [row for row in residual_rows if row.get("side_won") is True]
        harmful = [row for row in residual_rows if row.get("side_won") is False]
        unknown = len(residual_rows) - len(helpful) - len(harmful)
        current_net = sum(current_vals)
        base_net = sum(base_vals)
        candidate_net = sum(candidate_vals)
        residual_delta = candidate_net - base_net
        total_delta = candidate_net - current_net
        tag_counts = Counter(tag for row in residual_rows for tag in row.get("tags") or [])
        blockers = []
        if len(candidate_vals) < MIN_SETTLED:
            blockers.append("settled_lt_30")
        if base_rows + len(residual_rows) < MIN_TOTAL_SUPPRESSED:
            blockers.append("total_suppressed_lt_30")
        if len(residual_rows) < MIN_RESIDUAL_SUPPRESSED:
            blockers.append("residual_suppressed_lt_10")
        if candidate_net <= 0:
            blockers.append("net_not_positive")
        if total_delta <= 0:
            blockers.append("delta_vs_current_not_positive")
        if residual_delta <= 0:
            blockers.append("residual_delta_not_positive")
        if harmful:
            blockers.append("residual_harmful_false_holds_present")
        if candidate_net < MIN_CUSHION_CENTS:
            blockers.append("full_loss_cushion_lt_3")
        candidates.append(
            {
                "window": window,
                "freeze_ts_utc": freeze_ts,
                "base_policy": BASE_POLICY,
                "residual_policy": name,
                "settled": len(candidate_vals),
                "base_suppressed": base_rows,
                "residual_suppressed": len(residual_rows),
                "total_suppressed": base_rows + len(residual_rows),
                "residual_helpful": len(helpful),
                "residual_harmful": len(harmful),
                "residual_unknown": unknown,
                "current_net_cents": current_net,
                "base_net_cents": base_net,
                "candidate_net_cents": candidate_net,
                "base_delta_vs_current_cents": base_net - current_net,
                "candidate_delta_vs_current_cents": total_delta,
                "residual_delta_vs_base_cents": residual_delta,
                "full_loss_cushion_estimate": int(candidate_net // 100.0) if candidate_net > 0 else 0,
                "top_residual_tags": dict(tag_counts.most_common(8)),
                "blockers": blockers,
                "residual_examples": sorted(
                    residual_rows,
                    key=lambda row: fnum(row.get("delta_cents")),
                    reverse=True,
                )[:8],
                "harmful_examples": sorted(
                    harmful,
                    key=lambda row: fnum(row.get("delta_cents")),
                )[:5],
            }
        )
    candidates.sort(
        key=lambda row: (
            len(row.get("blockers") or []),
            fnum(row.get("residual_harmful")),
            -fnum(row.get("residual_delta_vs_base_cents")),
            -fnum(row.get("total_suppressed")),
        )
    )
    return {
        "window": window,
        "freeze_ts_utc": freeze_ts,
        "row_count": len(rows),
        "base_policy": BASE_POLICY,
        "base_suppressed_unique": len({(row.get("market"), row.get("side"), row.get("entry_ts")) for row in base_suppressed}),
        "candidates": candidates,
    }


def build_report() -> dict[str, Any]:
    strict_windows = load_json(cc.OUT_JSON).get("strict_forward_windows") or {}
    windows = [summarize_window(name, strict_windows.get(name)) for name in TARGET_WINDOWS]
    report = {
        "generated_at_utc": utc_now_iso(),
        "source": str(cc.OUT_JSON),
        "requirements": {
            "min_settled": MIN_SETTLED,
            "min_total_suppressed": MIN_TOTAL_SUPPRESSED,
            "min_residual_suppressed_for_child": MIN_RESIDUAL_SUPPRESSED,
            "min_cushion_cents": MIN_CUSHION_CENTS,
        },
        "windows": windows,
    }
    report["interpretation"] = interpretation(report)
    return report


def interpretation(report: dict[str, Any]) -> list[str]:
    notes = [
        "This is a strict-row residual frontier only; it does not freeze or promote a live exit rule.",
    ]
    for window in report.get("windows") or []:
        candidates = window.get("candidates") or []
        best = candidates[0] if candidates else {}
        clean = [row for row in candidates if "residual_harmful_false_holds_present" not in (row.get("blockers") or [])]
        best_clean = clean[0] if clean else {}
        if best:
            notes.append(
                f"{window.get('window')} best overall residual is {best.get('residual_policy')} with "
                f"{best.get('residual_suppressed')} residual rows, {best.get('residual_helpful')}/"
                f"{best.get('residual_harmful')} helpful/harmful, and "
                f"{best.get('residual_delta_vs_base_cents')}c versus base."
            )
        if best_clean:
            notes.append(
                f"{window.get('window')} best clean residual is {best_clean.get('residual_policy')} with "
                f"{best_clean.get('residual_suppressed')} rows and "
                f"{best_clean.get('residual_delta_vs_base_cents')}c; blockers remain "
                f"{best_clean.get('blockers')}."
            )
    notes.append(
        "If the clean residual remains sparse, the correct action is continued strict collection or a separately frozen child watch, not promotion."
    )
    return notes


def money(value: Any) -> str:
    return f"{fnum(value):.0f}c"


def write_md(report: dict[str, Any]) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8")
    lines = [
        "# v28 Exit Common-Clock Residual Frontier",
        "",
        "Research-only. No live bot logic changes, no process control, no orders.",
        "",
        f"- Generated UTC: `{report.get('generated_at_utc')}`",
        f"- Source: `{report.get('source')}`",
        "",
        "## Interpretation",
        "",
    ]
    lines.extend(f"- {note}" for note in report.get("interpretation") or [])
    for window in report.get("windows") or []:
        lines.extend([
            "",
            f"## {window.get('window')}",
            "",
            f"- Freeze UTC: `{window.get('freeze_ts_utc')}`",
            f"- Row count/base suppressed: `{window.get('row_count')}` / `{window.get('base_suppressed_unique')}`",
            "",
            "| rank | residual policy | residual rows | helpful/harmful | base c | candidate c | residual delta | total suppressed | cushion | blockers |",
            "|---:|---|---:|---:|---:|---:|---:|---:|---:|---|",
        ])
        for idx, row in enumerate(window.get("candidates") or [], start=1):
            lines.append(
                f"| {idx} | `{row.get('residual_policy')}` | {row.get('residual_suppressed')} | "
                f"{row.get('residual_helpful')}/{row.get('residual_harmful')} | "
                f"{money(row.get('base_net_cents'))} | {money(row.get('candidate_net_cents'))} | "
                f"{money(row.get('residual_delta_vs_base_cents'))} | {row.get('total_suppressed')} | "
                f"{row.get('full_loss_cushion_estimate')} | `{', '.join(row.get('blockers') or [])}` |"
            )
        best = (window.get("candidates") or [{}])[0]
        if best.get("harmful_examples"):
            lines.extend(["", "### Harmful Examples For Top Residual", ""])
            for row in best.get("harmful_examples") or []:
                lines.append(
                    f"- `{row.get('market')}` `{row.get('side')}/{row.get('result')}` "
                    f"reason=`{row.get('exit_reason')}` p_hold=`{row.get('p_hold')}` "
                    f"gap=`{row.get('hold_book_gap')}` drawdown=`{row.get('fair_drawdown_cents')}` "
                    f"delta=`{row.get('delta_cents')}`"
                )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    report = build_report()
    write_md(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
