"""Common-clock watch for v28 exit-policy candidates.

Research-only; no live bot changes or orders.

The leading candidates are exit repairs, but their individual reports use
different birth/freeze clocks. This report scores reduce, book-gap, loss-guard,
and dual-exit policies on identical row windows so future evidence cannot be
inflated by comparing unlike samples.
"""
from __future__ import annotations

import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

from probe_v28_exit_book_gap_candidates import (
    hold_book_gap,
    is_soft_exit,
    p_hold as book_p_hold,
)
from probe_v28_exit_policy_candidates import (
    build_rows,
    current_exit,
    exit_fair_drawdown,
    exit_p_hold,
    exit_reason,
    hold_to_settlement,
    is_value_over_hold,
    is_probability_reduce,
    side_won,
)
from probe_v28_frozen_dual_exit_book_gap_else_reduce import STATE_JSON as DUAL_STATE_JSON
from probe_v28_frozen_exit_book_gap_loss_guard import (
    STATE_JSON as LOSS_GUARD_STATE_JSON,
    candidate_gross as loss_guard_candidate_gross,
    load_json as loss_guard_load_json,
    should_suppress as loss_guard_should_suppress,
)
from probe_v28_frozen_exit_book_gap_loss_guard_v2 import (
    STATE_JSON as LOSS_GUARD_V2_STATE_JSON,
    candidate_gross as loss_guard_v2_candidate_gross,
    should_suppress as loss_guard_v2_should_suppress,
)
from probe_v28_frozen_exit_book_gap_loss_guard_v3 import (
    STATE_JSON as LOSS_GUARD_V3_STATE_JSON,
    candidate_gross as loss_guard_v3_candidate_gross,
    should_suppress as loss_guard_v3_should_suppress,
)
from probe_v28_frozen_exit_book_gap_suppression import (
    STATE_JSON as BOOK_GAP_STATE_JSON,
    GAP_FLOOR,
    P_HOLD_FLOOR as BOOK_P_HOLD_FLOOR,
    candidate_gross as book_gap_candidate_gross,
)
from probe_v28_frozen_exit_reduce_suppression import (
    STATE_JSON as REDUCE_STATE_JSON,
    P_HOLD_FLOOR as REDUCE_P_HOLD_FLOOR,
    candidate_gross as reduce_candidate_gross,
)


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
OUT_JSON = OUT_DIR / "v28_exit_policy_common_clock_watch_latest.json"
OUT_MD = OUT_DIR / "v28_exit_policy_common_clock_watch_latest.md"

MIN_SETTLED = 30
MIN_SUPPRESSED_DECISIONS = 30
MIN_FULL_LOSS_CUSHION = 3


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def parse_ts(value: Any) -> datetime | None:
    if not value:
        return None
    try:
        dt = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except ValueError:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def row_ts(row: dict[str, Any]) -> datetime | None:
    return parse_ts(row.get("exit_ts") or row.get("entry_ts"))


def as_float(value: Any) -> float | None:
    if value is None or value == "":
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def row_key(row: dict[str, Any]) -> tuple[Any, Any, Any]:
    return (row.get("market"), row.get("side"), row.get("entry_ts"))


def build_scored_rows() -> list[dict[str, Any]]:
    rows = []
    for row in build_rows():
        if current_exit(row) is None or hold_to_settlement(row) is None:
            continue
        rows.append(row)
    return rows


def filter_snapshot(rows: list[dict[str, Any]], freeze_ts: str | None) -> list[dict[str, Any]]:
    freeze_dt = parse_ts(freeze_ts)
    filtered = []
    for row in rows:
        ts = row_ts(row)
        if freeze_dt is not None and ts is not None and ts < freeze_dt:
            continue
        filtered.append(row)
    return filtered


def current_policy(row: dict[str, Any]) -> float | None:
    return current_exit(row)


def reduce_policy(row: dict[str, Any]) -> float | None:
    return reduce_candidate_gross(row, REDUCE_P_HOLD_FLOOR)


def book_gap_policy(row: dict[str, Any]) -> float | None:
    return book_gap_candidate_gross(row, GAP_FLOOR, BOOK_P_HOLD_FLOOR)


def loss_guard_policy(state: dict[str, Any]) -> Callable[[dict[str, Any]], float | None]:
    return lambda row: loss_guard_candidate_gross(row, state)


def loss_guard_v2_policy(state: dict[str, Any]) -> Callable[[dict[str, Any]], float | None]:
    return lambda row: loss_guard_v2_candidate_gross(row, state)


def loss_guard_v3_policy(state: dict[str, Any]) -> Callable[[dict[str, Any]], float | None]:
    return lambda row: loss_guard_v3_candidate_gross(row, state)


def dual_policy(row: dict[str, Any]) -> float | None:
    book = book_gap_policy(row)
    reduce = reduce_policy(row)
    if should_book_gap_suppress(row):
        return book
    if is_probability_reduce(row):
        return reduce
    return current_exit(row)


def should_reduce_suppress(row: dict[str, Any]) -> bool:
    p_hold = exit_p_hold(row)
    return is_probability_reduce(row) and p_hold is not None and p_hold >= REDUCE_P_HOLD_FLOOR


def should_book_gap_suppress(row: dict[str, Any]) -> bool:
    if not is_soft_exit(row):
        return False
    gap = hold_book_gap(row)
    p_hold = book_p_hold(row)
    return (gap is not None and gap >= GAP_FLOOR) or (p_hold is not None and p_hold >= BOOK_P_HOLD_FLOOR)


def should_loss_guard_suppress(row: dict[str, Any], state: dict[str, Any]) -> bool:
    return loss_guard_should_suppress(row, state)


def should_loss_guard_v2_suppress(row: dict[str, Any], state: dict[str, Any]) -> bool:
    return loss_guard_v2_should_suppress(row, state)


def should_loss_guard_v3_suppress(row: dict[str, Any], state: dict[str, Any]) -> bool:
    return loss_guard_v3_should_suppress(row, state)


def should_dual_suppress(row: dict[str, Any]) -> bool:
    return should_book_gap_suppress(row) or should_reduce_suppress(row)


def exit_price_cents(row: dict[str, Any]) -> float | None:
    features = row.get("exit_features") if isinstance(row.get("exit_features"), dict) else {}
    return as_float(features.get("mushroom_v28_exit_bid_cents")) or as_float(row.get("exit_cents"))


def suppression_tags(row: dict[str, Any]) -> list[str]:
    tags = []
    reason = exit_reason(row)
    if is_probability_reduce(row):
        tags.append("probability_reduce")
    elif is_value_over_hold(row):
        tags.append("value_over_hold")
    else:
        tags.append(reason or "other_exit_reason")
    p_hold = exit_p_hold(row)
    gap = hold_book_gap(row)
    drawdown = exit_fair_drawdown(row)
    exit_price = exit_price_cents(row)
    if p_hold is not None:
        if p_hold >= 0.85:
            tags.append("p_hold_ge_85")
        elif p_hold >= 0.79:
            tags.append("p_hold_79_85")
        elif p_hold >= 0.75:
            tags.append("p_hold_75_79")
        else:
            tags.append("p_hold_lt_75")
    if gap is not None:
        if gap < 0.0:
            tags.append("book_gap_negative")
        elif gap < 0.05:
            tags.append("book_gap_0_5pp")
        elif gap < 0.15:
            tags.append("book_gap_5_15pp")
        else:
            tags.append("book_gap_ge_15pp")
    if drawdown is not None:
        if drawdown > 0.0:
            tags.append("fair_drawdown_positive")
        elif drawdown > -2.5:
            tags.append("fair_drawdown_shallow")
        elif drawdown <= -5.0:
            tags.append("fair_drawdown_deep")
    if exit_price is not None:
        if exit_price >= 80.0:
            tags.append("exitable_at_80_plus")
        elif exit_price >= 70.0:
            tags.append("exitable_at_70_79")
        else:
            tags.append("exit_price_below_70")
    return tags


def compact_suppressed_row(row: dict[str, Any], candidate_cents: float, current_cents: float) -> dict[str, Any]:
    return {
        "market": row.get("market"),
        "side": row.get("side"),
        "result": row.get("result"),
        "exit_reason": exit_reason(row),
        "p_hold": exit_p_hold(row),
        "hold_book_gap": hold_book_gap(row),
        "fair_drawdown_cents": exit_fair_drawdown(row),
        "exit_price_cents": exit_price_cents(row),
        "current_cents": current_cents,
        "candidate_cents": candidate_cents,
        "delta_cents": candidate_cents - current_cents,
        "tags": suppression_tags(row),
    }


def summarize_policy(
    rows: list[dict[str, Any]],
    name: str,
    policy_fn: Callable[[dict[str, Any]], float | None],
    suppress_fn: Callable[[dict[str, Any]], bool],
) -> dict[str, Any]:
    current_vals = []
    candidate_vals = []
    suppressed = []
    helpful_suppressed_rows = []
    harmful_suppressed_rows = []
    details = []
    for row in rows:
        cur = current_exit(row)
        cand = policy_fn(row)
        if cur is None or cand is None:
            continue
        cur_f = float(cur)
        cand_f = float(cand)
        current_vals.append(cur_f)
        candidate_vals.append(cand_f)
        suppress = suppress_fn(row)
        if suppress:
            suppressed.append(row)
            compact = compact_suppressed_row(row, cand_f, cur_f)
            if side_won(row) is True:
                helpful_suppressed_rows.append(compact)
            elif side_won(row) is False:
                harmful_suppressed_rows.append(compact)
        details.append(
            {
                "market": row.get("market"),
                "side": row.get("side"),
                "result": row.get("result"),
                "entry_ts": row.get("entry_ts"),
                "exit_ts": row.get("exit_ts"),
                "exit_reason": exit_reason(row),
                "current_cents": cur_f,
                "candidate_cents": cand_f,
                "delta_cents": cand_f - cur_f,
                "suppressed": suppress,
            }
        )
    current_sum = sum(current_vals)
    candidate_sum = sum(candidate_vals)
    winner_recovery = sum(
        float(hold_to_settlement(row) or 0.0) - float(current_exit(row) or 0.0)
        for row in suppressed
        if side_won(row) is True
    )
    loss_cost = sum(
        float(hold_to_settlement(row) or 0.0) - float(current_exit(row) or 0.0)
        for row in suppressed
        if side_won(row) is False
    )
    cushion = int(candidate_sum // 100.0) if candidate_sum > 0.0 else 0
    helpful_tag_counts = Counter(tag for row in helpful_suppressed_rows for tag in row.get("tags") or [])
    harmful_tag_counts = Counter(tag for row in harmful_suppressed_rows for tag in row.get("tags") or [])
    blockers = []
    if len(candidate_vals) < MIN_SETTLED:
        blockers.append("settled_lt_30")
    if len(suppressed) < MIN_SUPPRESSED_DECISIONS:
        blockers.append("suppressed_decisions_lt_30")
    if candidate_sum <= 0.0:
        blockers.append("net_not_positive")
    if candidate_sum - current_sum <= 0.0:
        blockers.append("delta_vs_current_not_positive")
    if loss_cost < 0.0:
        blockers.append("loss_control_cost_negative")
    if cushion < MIN_FULL_LOSS_CUSHION:
        blockers.append("full_loss_cushion_lt_3")
    return {
        "policy": name,
        "rows": len(rows),
        "settled": len(candidate_vals),
        "current_gross_cents": current_sum,
        "candidate_gross_cents": candidate_sum,
        "delta_vs_current_cents": candidate_sum - current_sum,
        "current_wins": sum(1 for value in current_vals if value >= 0.0),
        "current_losses": sum(1 for value in current_vals if value < 0.0),
        "candidate_wins": sum(1 for value in candidate_vals if value >= 0.0),
        "candidate_losses": sum(1 for value in candidate_vals if value < 0.0),
        "loss_count_reduction": (
            sum(1 for value in current_vals if value < 0.0)
            - sum(1 for value in candidate_vals if value < 0.0)
        ),
        "suppressed_exits": len(suppressed),
        "winner_clip_recovered_cents": winner_recovery,
        "loss_control_cost_cents": loss_cost,
        "helpful_suppressed_rows": len(helpful_suppressed_rows),
        "harmful_suppressed_rows": len(harmful_suppressed_rows),
        "helpful_tag_counts": dict(helpful_tag_counts.most_common()),
        "harmful_tag_counts": dict(harmful_tag_counts.most_common()),
        "harmful_suppressed_examples": sorted(
            harmful_suppressed_rows,
            key=lambda item: float(item.get("delta_cents") or 0.0),
        )[:8],
        "full_loss_cushion_estimate": cushion,
        "integrity_pass": not blockers,
        "blockers": blockers,
        "worst_rows": sorted(details, key=lambda item: float(item.get("candidate_cents") or 0.0))[:8],
    }


def state_freeze(path: Path) -> str | None:
    return loss_guard_load_json(path).get("freeze_ts_utc")


def max_freeze(*values: str | None) -> str | None:
    parsed = [(parse_ts(value), value) for value in values if value]
    parsed = [(dt, value) for dt, value in parsed if dt is not None]
    if not parsed:
        return None
    return max(parsed, key=lambda item: item[0])[1]


def build_report() -> dict[str, Any]:
    loss_state = loss_guard_load_json(LOSS_GUARD_STATE_JSON)
    loss_v2_state = loss_guard_load_json(LOSS_GUARD_V2_STATE_JSON)
    loss_v3_state = loss_guard_load_json(LOSS_GUARD_V3_STATE_JSON)
    scored_rows = build_scored_rows()
    freezes = {
        "reduce": state_freeze(REDUCE_STATE_JSON),
        "book_gap": state_freeze(BOOK_GAP_STATE_JSON),
        "loss_guard": loss_state.get("freeze_ts_utc"),
        "loss_guard_v2": loss_v2_state.get("freeze_ts_utc"),
        "loss_guard_v3": loss_v3_state.get("freeze_ts_utc"),
        "dual": state_freeze(DUAL_STATE_JSON),
    }
    v1_common_forward = max_freeze(freezes.get("loss_guard"), freezes.get("dual"))
    v2_common_forward = max_freeze(freezes.get("loss_guard_v2"), freezes.get("dual"))
    v3_common_forward = max_freeze(freezes.get("loss_guard_v3"), freezes.get("dual"))
    windows = {
        "all_exit_rows_diagnostic": None,
        "book_gap_freeze_comparable": freezes.get("book_gap"),
        "new_exit_mix_common_forward_v1": v1_common_forward,
        "new_exit_mix_common_forward_v2": v2_common_forward,
        "new_exit_mix_common_forward_v3": v3_common_forward,
    }
    base_policies = [
        ("current_v28_exit", current_policy, lambda row: False),
        ("reduce_p_hold_ge_075", reduce_policy, should_reduce_suppress),
        ("book_gap_soft_gap15_or_p_hold75", book_gap_policy, should_book_gap_suppress),
        (
            "loss_guard_value_p85_reduce_p79_gap0",
            loss_guard_policy(loss_state),
            lambda row: should_loss_guard_suppress(row, loss_state),
        ),
        (
            "loss_guard_v2_value_gap0_or_p85_shallowdd_reduce_p79_gap0",
            loss_guard_v2_policy(loss_v2_state),
            lambda row: should_loss_guard_v2_suppress(row, loss_v2_state),
        ),
        ("dual_book_gap_else_reduce", dual_policy, should_dual_suppress),
    ]
    v3_policy = (
        "loss_guard_v3_value_gap0_or_p85_shallow_or_p95_extreme_reduce_p79_gap0",
        loss_guard_v3_policy(loss_v3_state),
        lambda row: should_loss_guard_v3_suppress(row, loss_v3_state),
    )
    diagnostic_policies = [
        *base_policies[:-1],
        (
            v3_policy[0],
            v3_policy[1],
            v3_policy[2],
        ),
        base_policies[-1],
    ]
    window_reports = []
    for name, freeze_ts in windows.items():
        rows = filter_snapshot(scored_rows, freeze_ts)
        if name in {"all_exit_rows_diagnostic", "book_gap_freeze_comparable", "new_exit_mix_common_forward_v3"}:
            policies = diagnostic_policies
        else:
            policies = base_policies
        summaries = [summarize_policy(rows, policy, fn, suppress_fn) for policy, fn, suppress_fn in policies]
        summaries.sort(
            key=lambda row: (
                bool(row.get("integrity_pass")),
                float(row.get("candidate_gross_cents") or -999999.0),
                float(row.get("delta_vs_current_cents") or -999999.0),
            ),
            reverse=True,
        )
        window_reports.append({
            "window": name,
            "freeze_ts_utc": freeze_ts,
            "row_count": len(rows),
            "summaries": summaries,
        })
    return {
        "generated_at_utc": utc_now_iso(),
        "base_scored_row_count": len(scored_rows),
        "freeze_timestamps": freezes,
        "strict_forward_windows": {
            "new_exit_mix_common_forward_v1": v1_common_forward,
            "new_exit_mix_common_forward_v2": v2_common_forward,
            "new_exit_mix_common_forward_v3": v3_common_forward,
        },
        "requirements": {
            "min_settled": MIN_SETTLED,
            "min_suppressed_decisions": MIN_SUPPRESSED_DECISIONS,
            "min_full_loss_cushion": MIN_FULL_LOSS_CUSHION,
        },
        "windows": window_reports,
        "interpretation": interpretation(window_reports),
    }


def interpretation(windows: list[dict[str, Any]]) -> list[str]:
    notes = [
        "Only the new_exit_mix_common_forward_* windows are strict forward evidence for newly frozen exit-mix branches.",
        "The v1/v2/v3 common windows each start from that branch's own shared/freeze clock; later branches are not credited inside older strict windows.",
        "All older windows are diagnostic/comparable only.",
    ]
    for strict in [row for row in windows if str(row.get("window") or "").startswith("new_exit_mix_common_forward")]:
        best = (strict.get("summaries") or [{}])[0]
        best_churn = max(
            strict.get("summaries") or [{}],
            key=lambda item: (
                float(item.get("loss_count_reduction") or -999999.0),
                float(item.get("delta_vs_current_cents") or -999999.0),
            ),
        )
        notes.append(
            f"{strict.get('window')} has {strict.get('row_count')} rows; best policy {best.get('policy')} has net {best.get('candidate_gross_cents')}c and blockers {best.get('blockers')}."
        )
        notes.append(
            f"{strict.get('window')} best loss-count reducer is {best_churn.get('policy')} with loss-count reduction {best_churn.get('loss_count_reduction')} and delta {best_churn.get('delta_vs_current_cents')}c."
        )
    comparable = next((row for row in windows if row.get("window") == "book_gap_freeze_comparable"), None)
    if comparable:
        best = (comparable.get("summaries") or [{}])[0]
        notes.append(
            f"Comparable book-gap-freeze window best policy is {best.get('policy')} with net {best.get('candidate_gross_cents')}c and loss cost {best.get('loss_control_cost_cents')}c."
        )
    return notes


def money(value: Any) -> str:
    number = as_float(value)
    if number is None:
        return "n/a"
    return f"{number:.0f}c (${number / 100.0:.2f})"


def write_report(report: dict[str, Any]) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8")
    lines = [
        "# v28 Exit Policy Common-Clock Watch",
        "",
        "Research-only. No live bot changes or orders.",
        "",
        f"- Generated UTC: `{report.get('generated_at_utc')}`",
        f"- Strict common-forward windows: `{report.get('strict_forward_windows')}`",
        f"- Freeze timestamps: `{report.get('freeze_timestamps')}`",
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
            f"- Rows: `{window.get('row_count')}`",
            "",
            "| rank | policy | settled | current W/L | candidate W/L | loss count delta | current | candidate | delta | suppressed | winner recovery | loss cost | cushion | pass | blockers |",
            "|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|---|",
        ])
        for idx, row in enumerate(window.get("summaries") or [], start=1):
            lines.append(
                f"| {idx} | `{row.get('policy')}` | {row.get('settled')} | "
                f"{row.get('current_wins')}/{row.get('current_losses')} | {row.get('candidate_wins')}/{row.get('candidate_losses')} | "
                f"{row.get('loss_count_reduction')} | "
                f"{money(row.get('current_gross_cents'))} | {money(row.get('candidate_gross_cents'))} | {money(row.get('delta_vs_current_cents'))} | "
                f"{row.get('suppressed_exits')} | {money(row.get('winner_clip_recovered_cents'))} | {money(row.get('loss_control_cost_cents'))} | "
                f"{row.get('full_loss_cushion_estimate')} | {row.get('integrity_pass')} | {', '.join(row.get('blockers') or []) or 'none'} |"
            )
        lines.extend([
            "",
            "### Suppressed Loss Tags",
            "",
            "| policy | helpful/harmful suppressed | loss cost | top harmful tags |",
            "|---|---:|---:|---|",
        ])
        for row in window.get("summaries") or []:
            harmful_tags = ", ".join(
                f"{tag}:{count}"
                for tag, count in list((row.get("harmful_tag_counts") or {}).items())[:6]
            )
            lines.append(
                f"| `{row.get('policy')}` | {row.get('helpful_suppressed_rows')}/{row.get('harmful_suppressed_rows')} | "
                f"{money(row.get('loss_control_cost_cents'))} | {harmful_tags or 'none'} |"
            )
        examples = []
        for row in window.get("summaries") or []:
            for example in row.get("harmful_suppressed_examples") or []:
                item = dict(example)
                item["policy"] = row.get("policy")
                examples.append(item)
        if examples:
            lines.extend([
                "",
                "### Worst Suppressed-Loss Examples",
                "",
                "| policy | market | side/result | reason | p_hold | gap | drawdown | exit | delta | tags |",
                "|---|---|---|---|---:|---:|---:|---:|---:|---|",
            ])
            for row in sorted(examples, key=lambda item: float(item.get("delta_cents") or 0.0))[:10]:
                lines.append(
                    f"| `{row.get('policy')}` | {row.get('market')} | {row.get('side')}/{row.get('result')} | "
                    f"{row.get('exit_reason')} | {row.get('p_hold')} | {row.get('hold_book_gap')} | "
                    f"{row.get('fair_drawdown_cents')} | {row.get('exit_price_cents')} | {money(row.get('delta_cents'))} | "
                    f"{', '.join(row.get('tags') or [])} |"
                )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    report = build_report()
    write_report(report)
    print(OUT_MD)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
