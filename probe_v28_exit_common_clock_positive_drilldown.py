"""Drilldown for positive strict common-clock exit watches.

Research-only; no live bot changes or orders.

The exit maturity runway shows common-clock v2 and v3 are positive but still
blocked by sample size, suppression density, and full-loss cushion. This probe
keeps those strict windows and explains what the positive rows are doing:
which exits were suppressed, whether suppressions were helpful, and what loss
classes remain.
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
COMMON_CLOCK_JSON = OUT_DIR / "v28_exit_policy_common_clock_watch_latest.json"
OUT_JSON = OUT_DIR / "v28_exit_common_clock_positive_drilldown_latest.json"
OUT_MD = OUT_DIR / "v28_exit_common_clock_positive_drilldown_latest.md"

TARGET_WINDOWS = [
    "new_exit_mix_common_forward_v2",
    "new_exit_mix_common_forward_v3",
]


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


def best_summary(common: dict[str, Any], window: str) -> dict[str, Any]:
    for item in common.get("windows") or []:
        if item.get("window") == window:
            return (item.get("summaries") or [{}])[0]
    return {}


def policy_pair(policy: str) -> tuple[Callable[[dict[str, Any]], float | None], Callable[[dict[str, Any]], bool]]:
    loss_state = cc.loss_guard_load_json(cc.LOSS_GUARD_STATE_JSON)
    loss_v2_state = cc.loss_guard_load_json(cc.LOSS_GUARD_V2_STATE_JSON)
    loss_v3_state = cc.loss_guard_load_json(cc.LOSS_GUARD_V3_STATE_JSON)
    if policy == "loss_guard_value_p85_reduce_p79_gap0":
        return cc.loss_guard_policy(loss_state), lambda row: cc.should_loss_guard_suppress(row, loss_state)
    if policy == "loss_guard_v2_value_gap0_or_p85_shallowdd_reduce_p79_gap0":
        return cc.loss_guard_v2_policy(loss_v2_state), lambda row: cc.should_loss_guard_v2_suppress(row, loss_v2_state)
    if policy == "loss_guard_v3_value_gap0_or_p85_shallow_or_p95_extreme_reduce_p79_gap0":
        return cc.loss_guard_v3_policy(loss_v3_state), lambda row: cc.should_loss_guard_v3_suppress(row, loss_v3_state)
    if policy == "book_gap_soft_gap15_or_p_hold75":
        return cc.book_gap_policy, cc.should_book_gap_suppress
    if policy == "dual_book_gap_else_reduce":
        return cc.dual_policy, cc.should_dual_suppress
    if policy == "reduce_p_hold_ge_075":
        return cc.reduce_policy, cc.should_reduce_suppress
    return cc.current_policy, lambda row: False


def result_tags(row: dict[str, Any], current: float, candidate: float, suppressed: bool) -> list[str]:
    tags: list[str] = []
    hold = fnum(cc.hold_to_settlement(row))
    hold_delta = hold - current
    won = cc.side_won(row)
    if suppressed:
        tags.append("suppressed")
        if hold_delta > 0:
            tags.append("suppression_helpful")
        elif hold_delta < 0:
            tags.append("suppression_harmful")
    elif hold_delta > 0:
        tags.append("unsuppressed_winner_clip")
    elif hold_delta < 0:
        tags.append("exit_helped_vs_hold")
    if candidate < 0:
        tags.append("candidate_loss")
    if current < 0:
        tags.append("current_loss")
    if won is True:
        tags.append("settlement_winner")
    elif won is False:
        tags.append("settlement_loser")
    tags.extend(cc.suppression_tags(row))
    return tags


def compact_row(row: dict[str, Any], current: float, candidate: float, suppressed: bool) -> dict[str, Any]:
    hold = fnum(cc.hold_to_settlement(row))
    return {
        "market": row.get("market"),
        "side": row.get("side"),
        "result": row.get("result"),
        "side_won": cc.side_won(row),
        "entry_ts": row.get("entry_ts"),
        "exit_ts": row.get("exit_ts"),
        "exit_reason": cc.exit_reason(row),
        "p_hold": cc.exit_p_hold(row),
        "hold_book_gap": cc.hold_book_gap(row),
        "fair_drawdown_cents": cc.exit_fair_drawdown(row),
        "exit_price_cents": cc.exit_price_cents(row),
        "current_cents": current,
        "hold_cents": hold,
        "candidate_cents": candidate,
        "hold_minus_current_cents": hold - current,
        "candidate_delta_cents": candidate - current,
        "suppressed": suppressed,
        "tags": result_tags(row, current, candidate, suppressed),
    }


def has_tag(row: dict[str, Any], tag: str) -> bool:
    return tag in set(row.get("tags") or [])


def candidate_residual_predicates() -> dict[str, Callable[[dict[str, Any]], bool]]:
    return {
        "p_hold_lt_75": lambda row: fnum(row.get("p_hold")) < 0.75,
        "p_hold_lt_75_and_book_gap_negative": (
            lambda row: fnum(row.get("p_hold")) < 0.75 and fnum(row.get("hold_book_gap")) < 0.0
        ),
        "p_hold_lt_75_and_value_over_hold": (
            lambda row: fnum(row.get("p_hold")) < 0.75 and has_tag(row, "value_over_hold")
        ),
        "p_hold_lt_75_and_exit_price_below_70": (
            lambda row: fnum(row.get("p_hold")) < 0.75 and has_tag(row, "exit_price_below_70")
        ),
        "p_hold_75_79": lambda row: has_tag(row, "p_hold_75_79"),
        "fair_drawdown_positive": lambda row: has_tag(row, "fair_drawdown_positive"),
        "book_gap_negative": lambda row: fnum(row.get("hold_book_gap")) < 0.0,
        "value_over_hold": lambda row: has_tag(row, "value_over_hold"),
        "probability_reduce": lambda row: has_tag(row, "probability_reduce"),
        "exit_price_below_70": lambda row: has_tag(row, "exit_price_below_70"),
        "exitable_70_79": lambda row: has_tag(row, "exitable_at_70_79"),
        "mushroom_probability_collapse_full": (
            lambda row: has_tag(row, "mushroom_v28_probability_collapse_full")
        ),
    }


def residual_separator(unscored_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Test simple observables on rows the current best policy did not suppress."""
    unsuppressed = [row for row in unscored_rows if not row.get("suppressed")]
    out: list[dict[str, Any]] = []
    for name, pred in candidate_residual_predicates().items():
        selected = [row for row in unsuppressed if pred(row)]
        helpful = [row for row in selected if fnum(row.get("hold_minus_current_cents")) > 0.0]
        harmful = [row for row in selected if fnum(row.get("hold_minus_current_cents")) < 0.0]
        flats = len(selected) - len(helpful) - len(harmful)
        helpful_delta = sum(fnum(row.get("hold_minus_current_cents")) for row in helpful)
        harmful_delta = sum(fnum(row.get("hold_minus_current_cents")) for row in harmful)
        out.append(
            {
                "selector": name,
                "selected": len(selected),
                "helpful_rows": len(helpful),
                "harmful_rows": len(harmful),
                "flat_rows": flats,
                "net_delta_cents_if_suppressed": helpful_delta + harmful_delta,
                "helpful_delta_cents": helpful_delta,
                "harmful_delta_cents": harmful_delta,
                "examples": sorted(
                    selected,
                    key=lambda row: fnum(row.get("hold_minus_current_cents")),
                    reverse=True,
                )[:5],
            }
        )
    return sorted(
        out,
        key=lambda row: (
            fnum(row.get("net_delta_cents_if_suppressed")),
            -fnum(row.get("harmful_rows")),
            fnum(row.get("selected")),
        ),
        reverse=True,
    )


def classify_window(window: str, freeze_ts: str | None, summary: dict[str, Any]) -> dict[str, Any]:
    rows = cc.filter_snapshot(cc.build_scored_rows(), freeze_ts)
    policy = str(summary.get("policy") or "current_v28_exit")
    policy_fn, suppress_fn = policy_pair(policy)
    scored: list[dict[str, Any]] = []
    for row in rows:
        current = cc.current_exit(row)
        candidate = policy_fn(row)
        if current is None or candidate is None:
            continue
        cur_f = float(current)
        cand_f = float(candidate)
        scored.append(compact_row(row, cur_f, cand_f, suppress_fn(row)))
    suppressed = [row for row in scored if row.get("suppressed")]
    helpful = [row for row in suppressed if fnum(row.get("hold_minus_current_cents")) > 0.0]
    harmful = [row for row in suppressed if fnum(row.get("hold_minus_current_cents")) < 0.0]
    candidate_losses = [row for row in scored if fnum(row.get("candidate_cents")) < 0.0]
    unsuppressed_winner_clips = [
        row for row in scored
        if not row.get("suppressed") and fnum(row.get("hold_minus_current_cents")) > 0.0
    ]
    exit_helped_losers = [
        row for row in scored
        if not row.get("suppressed") and fnum(row.get("hold_minus_current_cents")) < 0.0
    ]
    tag_counts = Counter(tag for row in scored for tag in row.get("tags") or [])
    loss_tag_counts = Counter(tag for row in candidate_losses for tag in row.get("tags") or [])
    return {
        "window": window,
        "freeze_ts_utc": freeze_ts,
        "policy": policy,
        "summary": summary,
        "row_count": len(scored),
        "suppressed_count": len(suppressed),
        "helpful_suppressed_count": len(helpful),
        "harmful_suppressed_count": len(harmful),
        "candidate_loss_count": len(candidate_losses),
        "unsuppressed_winner_clip_count": len(unsuppressed_winner_clips),
        "exit_helped_loser_count": len(exit_helped_losers),
        "tag_counts": dict(tag_counts.most_common()),
        "candidate_loss_tag_counts": dict(loss_tag_counts.most_common()),
        "residual_separator": residual_separator(scored),
        "suppressed_rows": sorted(suppressed, key=lambda row: fnum(row.get("candidate_delta_cents")), reverse=True),
        "worst_candidate_losses": sorted(candidate_losses, key=lambda row: fnum(row.get("candidate_cents")))[:10],
        "largest_unsuppressed_winner_clips": sorted(
            unsuppressed_winner_clips,
            key=lambda row: fnum(row.get("hold_minus_current_cents")),
            reverse=True,
        )[:10],
        "exit_helped_loser_examples": sorted(
            exit_helped_losers,
            key=lambda row: fnum(row.get("hold_minus_current_cents")),
        )[:10],
    }


def build_report() -> dict[str, Any]:
    common = load_json(COMMON_CLOCK_JSON)
    strict_windows = common.get("strict_forward_windows") or {}
    windows = [
        classify_window(window, strict_windows.get(window), best_summary(common, window))
        for window in TARGET_WINDOWS
    ]
    report = {
        "generated_at_utc": utc_now_iso(),
        "common_clock_source": str(COMMON_CLOCK_JSON),
        "windows": windows,
    }
    report["interpretation"] = interpretation(report)
    return report


def interpretation(report: dict[str, Any]) -> list[str]:
    notes = [
        "Research-only drilldown; it does not create or change an exit rule.",
        "Both positive strict common-clock windows are still promotion-blocked by sample size, suppression density, and full-loss cushion.",
    ]
    for window in report.get("windows") or []:
        summary = window.get("summary") or {}
        notes.append(
            f"{window.get('window')} best policy {window.get('policy')} has net "
            f"{summary.get('candidate_gross_cents')}c, delta {summary.get('delta_vs_current_cents')}c, "
            f"suppressed helpful/harmful {window.get('helpful_suppressed_count')}/{window.get('harmful_suppressed_count')}, "
            f"candidate losses {window.get('candidate_loss_count')}, and unsuppressed winner clips {window.get('unsuppressed_winner_clip_count')}."
        )
    return notes


def fmt(value: Any) -> str:
    if value is None:
        return "n/a"
    if isinstance(value, float):
        return f"{value:.2f}"
    return str(value)


def short_row(row: dict[str, Any]) -> str:
    return (
        f"{row.get('market')} {row.get('side')}/{row.get('result')} "
        f"cur={fmt(row.get('current_cents'))} hold={fmt(row.get('hold_cents'))} "
        f"cand={fmt(row.get('candidate_cents'))} delta={fmt(row.get('candidate_delta_cents'))} "
        f"tags={row.get('tags')}"
    )


def write_md(report: dict[str, Any]) -> None:
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8")
    lines = [
        "# v28 Exit Common-Clock Positive Drilldown",
        "",
        "Research-only strict-window drilldown. No live bot changes or orders.",
        "",
        f"- Generated UTC: `{report.get('generated_at_utc')}`",
        "",
        "## Interpretation",
        "",
    ]
    lines.extend(f"- {note}" for note in report.get("interpretation") or [])
    for window in report.get("windows") or []:
        summary = window.get("summary") or {}
        lines.extend(
            [
                "",
                f"## {window.get('window')}",
                "",
                f"- Freeze UTC: `{window.get('freeze_ts_utc')}`",
                f"- Best policy: `{window.get('policy')}`",
                f"- Settled/suppressed: `{summary.get('settled')}` / `{window.get('suppressed_count')}`",
                f"- Net/delta: `{summary.get('candidate_gross_cents')}c` / `{summary.get('delta_vs_current_cents')}c`",
                f"- Helpful/harmful suppressions: `{window.get('helpful_suppressed_count')}` / `{window.get('harmful_suppressed_count')}`",
                f"- Candidate losses: `{window.get('candidate_loss_count')}`",
                f"- Unsuppressed winner clips: `{window.get('unsuppressed_winner_clip_count')}`",
                f"- Candidate-loss tags: `{window.get('candidate_loss_tag_counts')}`",
                f"- Best residual selector: `{(window.get('residual_separator') or [{}])[0].get('selector')}` "
                f"for `{(window.get('residual_separator') or [{}])[0].get('net_delta_cents_if_suppressed')}c`, "
                f"helpful/harmful `{(window.get('residual_separator') or [{}])[0].get('helpful_rows')}`/"
                f"`{(window.get('residual_separator') or [{}])[0].get('harmful_rows')}`",
                "",
                "### Suppressed Rows",
            ]
        )
        for row in window.get("suppressed_rows") or []:
            lines.append(f"- {short_row(row)}")
        lines.extend(["", "### Worst Candidate Losses"])
        for row in window.get("worst_candidate_losses") or []:
            lines.append(f"- {short_row(row)}")
        lines.extend(["", "### Largest Unsuppressed Winner Clips"])
        for row in window.get("largest_unsuppressed_winner_clips") or []:
            lines.append(f"- {short_row(row)}")
        lines.extend(["", "### Residual Separator Scan"])
        for row in (window.get("residual_separator") or [])[:8]:
            lines.append(
                f"- {row.get('selector')}: selected={row.get('selected')} "
                f"helpful/harmful={row.get('helpful_rows')}/{row.get('harmful_rows')} "
                f"net_delta={fmt(row.get('net_delta_cents_if_suppressed'))}c"
            )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    report = build_report()
    write_md(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
