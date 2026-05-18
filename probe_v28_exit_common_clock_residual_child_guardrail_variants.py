"""Guardrail variants for the common-clock residual exit child.

Research-only; no live bot changes or orders.

The frozen residual child exposed a false-hold failure: 70-79c probability-
reduce exits around p_hold 75-79 can be true losers. This probe tests small
observable guard variants against the same frozen windows so the failure mode
is classified before any new child watch is considered.
"""
from __future__ import annotations

import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

import probe_v28_exit_policy_common_clock_watch as cc
import probe_v28_frozen_exit_common_clock_residual_child_watch as residual


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
OUT_JSON = OUT_DIR / "v28_exit_common_clock_residual_child_guardrail_variants_latest.json"
OUT_MD = OUT_DIR / "v28_exit_common_clock_residual_child_guardrail_variants_latest.md"

MIN_SETTLED = 30
MIN_SUPPRESSED = 30
MIN_FULL_LOSS_CUSHION = 3


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def fnum(value: Any, default: float = 0.0) -> float:
    if value is None or value == "":
        return default
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def fmt(value: Any) -> str:
    if value is None:
        return "n/a"
    if isinstance(value, float):
        return f"{value:.2f}"
    return str(value)


def exit_price_70_79(row: dict[str, Any]) -> bool:
    price = cc.exit_price_cents(row)
    return price is not None and 70.0 <= float(price) < 80.0


def is_prob_reduce(row: dict[str, Any]) -> bool:
    return cc.exit_reason(row) == "mushroom_v28_probability_reduce"


def is_value_over_hold(row: dict[str, Any]) -> bool:
    return cc.exit_reason(row) == "mushroom_v28_exit_value_over_hold"


def p_hold_75_79(row: dict[str, Any]) -> bool:
    p_hold = cc.exit_p_hold(row)
    return p_hold is not None and 0.75 <= float(p_hold) < 0.80


def gap_le(row: dict[str, Any], threshold: float) -> bool:
    gap = cc.hold_book_gap(row)
    return gap is not None and float(gap) <= threshold


def base_child(row: dict[str, Any], parent_suppressed: bool) -> bool:
    return (not parent_suppressed) and exit_price_70_79(row)


def variant_specs() -> list[tuple[str, str, Callable[[dict[str, Any], bool], bool]]]:
    return [
        (
            "base_exit70_79",
            "Frozen residual child: parent not suppressed and exit price 70-79c.",
            base_child,
        ),
        (
            "exclude_probability_reduce_p75_79",
            "Remove the observed strict false-hold pocket: probability-reduce exits with p_hold 75-79.",
            lambda row, parent: base_child(row, parent) and not (is_prob_reduce(row) and p_hold_75_79(row)),
        ),
        (
            "value_over_hold_only",
            "Hold only value-over-hold exits in the residual 70-79c band.",
            lambda row, parent: base_child(row, parent) and is_value_over_hold(row),
        ),
        (
            "book_gap_le_neg_0_5pp",
            "Require the book to agree with holding by at least -0.5pp gap.",
            lambda row, parent: base_child(row, parent) and gap_le(row, -0.005),
        ),
        (
            "p_hold_lt75_or_book_gap_le_neg_0_5pp",
            "Allow low-p_hold clips or book-confirmed holds, excluding flat/positive-gap p75-79 false holds.",
            lambda row, parent: base_child(row, parent)
            and ((cc.exit_p_hold(row) is not None and float(cc.exit_p_hold(row)) < 0.75) or gap_le(row, -0.005)),
        ),
        (
            "prob_reduce_requires_book_gap_le_neg_0_5pp",
            "Permit probability-reduce residual holds only when the book gap is clearly negative.",
            lambda row, parent: base_child(row, parent)
            and ((not is_prob_reduce(row)) or gap_le(row, -0.005)),
        ),
    ]


def row_tags(row: dict[str, Any], parent_suppressed: bool, child_suppressed: bool) -> list[str]:
    tags = residual.tags_for(row, parent_suppressed, child_suppressed)
    if is_prob_reduce(row):
        tags.append("probability_reduce_exit")
    if is_value_over_hold(row):
        tags.append("value_over_hold_exit")
    if p_hold_75_79(row):
        tags.append("p_hold_75_79_guard_zone")
    if gap_le(row, -0.005):
        tags.append("book_gap_le_neg_0_5pp")
    return tags


def score_variant(
    rows: list[dict[str, Any]],
    label: str,
    freeze_ts: str | None,
    variant: str,
    physics: str,
    child_fn: Callable[[dict[str, Any], bool], bool],
) -> dict[str, Any]:
    parent_policy, parent_suppress_fn = residual.current_policy_pair()
    scored: list[dict[str, Any]] = []
    for row in rows:
        current = cc.current_exit(row)
        parent = parent_policy(row)
        hold = cc.hold_to_settlement(row)
        if current is None or parent is None or hold is None:
            continue
        current_f = float(current)
        parent_f = float(parent)
        hold_f = float(hold)
        parent_suppressed = bool(parent_suppress_fn(row))
        child_suppressed = bool(child_fn(row, parent_suppressed))
        candidate_f = hold_f if child_suppressed else parent_f
        scored.append({
            "market": row.get("market"),
            "side": row.get("side"),
            "result": row.get("result"),
            "entry_ts": row.get("entry_ts"),
            "exit_ts": row.get("exit_ts"),
            "exit_reason": cc.exit_reason(row),
            "p_hold": cc.exit_p_hold(row),
            "hold_book_gap": cc.hold_book_gap(row),
            "fair_drawdown_cents": cc.exit_fair_drawdown(row),
            "exit_price_cents": cc.exit_price_cents(row),
            "current_cents": current_f,
            "parent_cents": parent_f,
            "hold_cents": hold_f,
            "candidate_cents": candidate_f,
            "parent_delta_cents": parent_f - current_f,
            "child_delta_vs_parent_cents": candidate_f - parent_f,
            "candidate_delta_vs_current_cents": candidate_f - current_f,
            "parent_suppressed": parent_suppressed,
            "child_suppressed": child_suppressed,
            "side_won": cc.side_won(row),
            "tags": row_tags(row, parent_suppressed, child_suppressed),
        })
    current_net = sum(fnum(row.get("current_cents")) for row in scored)
    parent_net = sum(fnum(row.get("parent_cents")) for row in scored)
    candidate_net = sum(fnum(row.get("candidate_cents")) for row in scored)
    child_rows = [row for row in scored if row.get("child_suppressed")]
    helpful = [row for row in child_rows if fnum(row.get("child_delta_vs_parent_cents")) > 0.0]
    harmful = [row for row in child_rows if fnum(row.get("child_delta_vs_parent_cents")) < 0.0]
    child_delta = sum(fnum(row.get("child_delta_vs_parent_cents")) for row in child_rows)
    cushion = int(candidate_net // 100.0) if candidate_net > 0.0 else 0
    loss_cost = sum(fnum(row.get("child_delta_vs_parent_cents")) for row in harmful)
    blockers: list[str] = []
    if len(scored) < MIN_SETTLED:
        blockers.append("settled_lt_30")
    if len(child_rows) < MIN_SUPPRESSED:
        blockers.append("child_suppressed_decisions_lt_30")
    if candidate_net <= 0.0:
        blockers.append("net_not_positive")
    if candidate_net - current_net <= 0.0:
        blockers.append("delta_vs_current_not_positive")
    if child_delta <= 0.0:
        blockers.append("child_delta_vs_parent_not_positive")
    if loss_cost < 0.0:
        blockers.append("child_loss_control_cost_negative")
    if cushion < MIN_FULL_LOSS_CUSHION:
        blockers.append("full_loss_cushion_lt_3")
    if harmful:
        blockers.append("strict_or_window_false_holds_present")
    return {
        "lane": label,
        "freeze_ts_utc": freeze_ts,
        "variant": variant,
        "physics": physics,
        "strict_forward": label == "post_child_birth",
        "settled": len(scored),
        "current_net_cents": current_net,
        "parent_net_cents": parent_net,
        "candidate_net_cents": candidate_net,
        "delta_vs_current_cents": candidate_net - current_net,
        "child_delta_vs_parent_cents": child_delta,
        "candidate_wins": sum(1 for row in scored if fnum(row.get("candidate_cents")) >= 0.0),
        "candidate_losses": sum(1 for row in scored if fnum(row.get("candidate_cents")) < 0.0),
        "parent_suppressed": sum(1 for row in scored if row.get("parent_suppressed")),
        "child_suppressed": len(child_rows),
        "child_helpful": len(helpful),
        "child_harmful": len(harmful),
        "child_loss_control_cost_cents": loss_cost,
        "full_loss_cushion_estimate": cushion,
        "blockers": blockers,
        "tag_counts": dict(Counter(tag for row in scored for tag in row.get("tags") or []).most_common()),
        "child_tag_counts": dict(Counter(tag for row in child_rows for tag in row.get("tags") or []).most_common()),
        "child_rows": sorted(child_rows, key=lambda row: fnum(row.get("child_delta_vs_parent_cents")))[:20],
        "worst_candidate_rows": sorted(scored, key=lambda row: fnum(row.get("candidate_cents")))[:10],
    }


def build_report() -> dict[str, Any]:
    state = residual.ensure_state()
    rows = cc.build_scored_rows()
    windows = residual.strict_windows()
    lanes = [
        ("diagnostic_v2_common_clock_context", windows.get("new_exit_mix_common_forward_v2")),
        ("diagnostic_v3_common_clock_context", windows.get("new_exit_mix_common_forward_v3")),
        ("post_child_birth", state.get("freeze_ts_utc")),
    ]
    scored_lanes: list[dict[str, Any]] = []
    for lane_label, freeze_ts in lanes:
        lane_rows = cc.filter_snapshot(rows, freeze_ts)
        for variant, physics, child_fn in variant_specs():
            scored_lanes.append(score_variant(lane_rows, lane_label, freeze_ts, variant, physics, child_fn))
    strict = [row for row in scored_lanes if row.get("strict_forward")]
    clean_strict = [
        row for row in strict
        if row.get("child_harmful") == 0
        and fnum(row.get("child_delta_vs_parent_cents")) > 0.0
        and fnum(row.get("candidate_net_cents")) > 0.0
    ]
    clean_strict = sorted(
        clean_strict,
        key=lambda row: (
            fnum(row.get("child_delta_vs_parent_cents")),
            fnum(row.get("candidate_net_cents")),
            fnum(row.get("child_suppressed")),
        ),
        reverse=True,
    )
    return {
        "generated_at_utc": utc_now_iso(),
        "state": state,
        "requirements": {
            "min_settled": MIN_SETTLED,
            "min_child_suppressed": MIN_SUPPRESSED,
            "min_full_loss_cushion": MIN_FULL_LOSS_CUSHION,
        },
        "lanes": scored_lanes,
        "clean_strict_variants": clean_strict,
        "interpretation": interpretation(scored_lanes, clean_strict),
    }


def interpretation(lanes: list[dict[str, Any]], clean_strict: list[dict[str, Any]]) -> list[str]:
    post_base = next((row for row in lanes if row.get("lane") == "post_child_birth" and row.get("variant") == "base_exit70_79"), {})
    best = clean_strict[0] if clean_strict else {}
    notes = [
        "Research-only guardrail scan; no live bot changes or orders.",
        "All variants use observable exit fields only; source labels and settlement are audit outcomes, not rule inputs.",
        (
            f"Base strict residual child: {post_base.get('settled')} settled, "
            f"{post_base.get('child_suppressed')} child suppressions, helpful/harmful "
            f"{post_base.get('child_helpful')}/{post_base.get('child_harmful')}, "
            f"child delta {post_base.get('child_delta_vs_parent_cents')}c, blockers {post_base.get('blockers')}."
        ),
    ]
    if best:
        notes.append(
            f"Best clean strict guard by child delta is {best.get('variant')}: "
            f"{best.get('child_suppressed')} child suppressions, helpful/harmful "
            f"{best.get('child_helpful')}/{best.get('child_harmful')}, "
            f"child delta {best.get('child_delta_vs_parent_cents')}c, candidate net "
            f"{best.get('candidate_net_cents')}c, blockers {best.get('blockers')}."
        )
    notes.append("These are guardrail diagnostics only; any new child would need its own freeze and future rows.")
    return notes


def write_md(report: dict[str, Any]) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8")
    lines = [
        "# v28 Exit Common-Clock Residual Child Guardrail Variants",
        "",
        "Research-only guardrail scan. No live bot changes or orders.",
        "",
        f"- Generated UTC: `{report.get('generated_at_utc')}`",
        f"- Child freeze UTC: `{(report.get('state') or {}).get('freeze_ts_utc')}`",
        "",
        "## Interpretation",
        "",
    ]
    lines.extend(f"- {note}" for note in report.get("interpretation") or [])
    lines.extend([
        "",
        "## Lane Summary",
        "",
        "| lane | variant | strict | settled | child supp | help/harm | child delta | candidate net | delta vs current | cushion | blockers |",
        "|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---|",
    ])
    for row in report.get("lanes") or []:
        lines.append(
            f"| `{row.get('lane')}` | `{row.get('variant')}` | {row.get('strict_forward')} | "
            f"{row.get('settled')} | {row.get('child_suppressed')} | "
            f"{row.get('child_helpful')}/{row.get('child_harmful')} | "
            f"{fmt(row.get('child_delta_vs_parent_cents'))} | {fmt(row.get('candidate_net_cents'))} | "
            f"{fmt(row.get('delta_vs_current_cents'))} | {row.get('full_loss_cushion_estimate')} | "
            f"{', '.join(row.get('blockers') or []) or 'none'} |"
        )
    lines.extend(["", "## Strict Child Rows", ""])
    for row in report.get("lanes") or []:
        if row.get("lane") != "post_child_birth":
            continue
        child_rows = row.get("child_rows") or []
        if not child_rows:
            continue
        lines.extend([
            f"### {row.get('variant')}",
            "",
            "| market | side | won | reason | exit | p_hold | gap | current | hold | child delta | tags |",
            "|---|---|---:|---|---:|---:|---:|---:|---:|---:|---|",
        ])
        for child in child_rows[:12]:
            lines.append(
                f"| `{child.get('market')}` | `{child.get('side')}` | {child.get('side_won')} | "
                f"`{child.get('exit_reason')}` | {fmt(child.get('exit_price_cents'))} | "
                f"{fmt(child.get('p_hold'))} | {fmt(child.get('hold_book_gap'))} | "
                f"{fmt(child.get('current_cents'))} | {fmt(child.get('hold_cents'))} | "
                f"{fmt(child.get('child_delta_vs_parent_cents'))} | {', '.join(child.get('tags') or [])} |"
            )
        lines.append("")
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    report = build_report()
    write_md(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
