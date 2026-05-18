"""Frozen common-clock residual child watch for v28 exits.

Research-only; no live bot changes or orders.

The positive common-clock parent suppresses high-p-hold/value-over-hold exits,
but the drilldown found unsuppressed winner clips remain. This watch freezes a
narrow observable child shape: after the parent has not suppressed an exit,
hold instead of exiting when the exit is still priced in the 70-79c band.
Historical rows are diagnostic only; the post-birth lane is the only strict
evidence for this child.
"""
from __future__ import annotations

import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import probe_v28_exit_policy_common_clock_watch as cc


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
STATE_JSON = OUT_DIR / "v28_frozen_exit_common_clock_residual_child_watch_state.json"
OUT_JSON = OUT_DIR / "v28_frozen_exit_common_clock_residual_child_watch_latest.json"
OUT_MD = OUT_DIR / "v28_frozen_exit_common_clock_residual_child_watch_latest.md"
COMMON_CLOCK_JSON = OUT_DIR / "v28_exit_policy_common_clock_watch_latest.json"

MIN_SETTLED = 30
MIN_SUPPRESSED = 30
MIN_FULL_LOSS_CUSHION = 3
POLICY = "parent_loss_guard_plus_residual_exit70_79"


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


def ensure_state() -> dict[str, Any]:
    state = load_json(STATE_JSON)
    if state.get("freeze_ts_utc"):
        return state
    state = {
        "freeze_ts_utc": utc_now_iso(),
        "candidate": POLICY,
        "parent_policy": "loss_guard_value_p85_reduce_p79_gap0",
        "child_condition": "parent_not_suppressed_and_exit_price_cents_70_to_79",
        "physics": (
            "A still-high exit price with low parent confidence may be transient "
            "winner clipping; strict forward rows must prove it does not reopen "
            "loss-control damage."
        ),
    }
    STATE_JSON.write_text(json.dumps(state, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return state


def fnum(value: Any, default: float = 0.0) -> float:
    if value is None or value == "":
        return default
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def current_policy_pair() -> tuple[Any, Any]:
    loss_state = cc.loss_guard_load_json(cc.LOSS_GUARD_STATE_JSON)
    return cc.loss_guard_policy(loss_state), lambda row: cc.should_loss_guard_suppress(row, loss_state)


def child_suppresses(row: dict[str, Any], parent_suppressed: bool) -> bool:
    if parent_suppressed:
        return False
    exit_price = cc.exit_price_cents(row)
    return exit_price is not None and 70.0 <= float(exit_price) < 80.0


def tags_for(row: dict[str, Any], parent_suppressed: bool, child_suppressed: bool) -> list[str]:
    tags = []
    if parent_suppressed:
        tags.append("parent_suppressed")
    if child_suppressed:
        tags.append("child_residual_suppressed")
    if cc.side_won(row) is True:
        tags.append("settlement_winner")
    elif cc.side_won(row) is False:
        tags.append("settlement_loser")
    tags.extend(cc.suppression_tags(row))
    return tags


def score_rows(rows: list[dict[str, Any]], label: str, freeze_ts: str | None) -> dict[str, Any]:
    parent_policy, parent_suppress_fn = current_policy_pair()
    scored = []
    for row in rows:
        cur = cc.current_exit(row)
        parent = parent_policy(row)
        hold = cc.hold_to_settlement(row)
        if cur is None or parent is None or hold is None:
            continue
        cur_f = float(cur)
        parent_f = float(parent)
        hold_f = float(hold)
        parent_suppressed = bool(parent_suppress_fn(row))
        child_suppressed = child_suppresses(row, parent_suppressed)
        candidate_f = hold_f if child_suppressed else parent_f
        scored.append(
            {
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
                "current_cents": cur_f,
                "parent_cents": parent_f,
                "hold_cents": hold_f,
                "candidate_cents": candidate_f,
                "parent_delta_cents": parent_f - cur_f,
                "child_delta_vs_parent_cents": candidate_f - parent_f,
                "candidate_delta_vs_current_cents": candidate_f - cur_f,
                "parent_suppressed": parent_suppressed,
                "child_suppressed": child_suppressed,
                "side_won": cc.side_won(row),
                "tags": tags_for(row, parent_suppressed, child_suppressed),
            }
        )
    current_net = sum(fnum(row.get("current_cents")) for row in scored)
    parent_net = sum(fnum(row.get("parent_cents")) for row in scored)
    candidate_net = sum(fnum(row.get("candidate_cents")) for row in scored)
    child_rows = [row for row in scored if row.get("child_suppressed")]
    helpful = [row for row in child_rows if fnum(row.get("child_delta_vs_parent_cents")) > 0.0]
    harmful = [row for row in child_rows if fnum(row.get("child_delta_vs_parent_cents")) < 0.0]
    child_delta = sum(fnum(row.get("child_delta_vs_parent_cents")) for row in child_rows)
    cushion = int(candidate_net // 100.0) if candidate_net > 0.0 else 0
    blockers = []
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
    if sum(fnum(row.get("child_delta_vs_parent_cents")) for row in harmful) < 0.0:
        blockers.append("child_loss_control_cost_negative")
    if cushion < MIN_FULL_LOSS_CUSHION:
        blockers.append("full_loss_cushion_lt_3")
    tag_counts = Counter(tag for row in scored for tag in row.get("tags") or [])
    child_tag_counts = Counter(tag for row in child_rows for tag in row.get("tags") or [])
    return {
        "label": label,
        "freeze_ts_utc": freeze_ts,
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
        "child_loss_control_cost_cents": sum(fnum(row.get("child_delta_vs_parent_cents")) for row in harmful),
        "full_loss_cushion_estimate": cushion,
        "blockers": blockers,
        "live_ready": False,
        "strict_forward": label == "post_child_birth",
        "tag_counts": dict(tag_counts.most_common()),
        "child_tag_counts": dict(child_tag_counts.most_common()),
        "child_rows": sorted(child_rows, key=lambda row: fnum(row.get("child_delta_vs_parent_cents")), reverse=True)[:20],
        "worst_candidate_rows": sorted(scored, key=lambda row: fnum(row.get("candidate_cents")))[:10],
    }


def strict_windows() -> dict[str, str | None]:
    common = load_json(COMMON_CLOCK_JSON)
    windows = common.get("strict_forward_windows")
    return windows if isinstance(windows, dict) else {}


def build_report() -> dict[str, Any]:
    state = ensure_state()
    rows = cc.build_scored_rows()
    windows = strict_windows()
    lanes = [
        score_rows(
            cc.filter_snapshot(rows, windows.get("new_exit_mix_common_forward_v2")),
            "diagnostic_v2_common_clock_context",
            windows.get("new_exit_mix_common_forward_v2"),
        ),
        score_rows(
            cc.filter_snapshot(rows, windows.get("new_exit_mix_common_forward_v3")),
            "diagnostic_v3_common_clock_context",
            windows.get("new_exit_mix_common_forward_v3"),
        ),
        score_rows(
            cc.filter_snapshot(rows, state.get("freeze_ts_utc")),
            "post_child_birth",
            state.get("freeze_ts_utc"),
        ),
    ]
    report = {
        "generated_at_utc": utc_now_iso(),
        "state": state,
        "requirements": {
            "min_settled": MIN_SETTLED,
            "min_child_suppressed": MIN_SUPPRESSED,
            "min_full_loss_cushion": MIN_FULL_LOSS_CUSHION,
        },
        "lanes": lanes,
    }
    report["interpretation"] = interpretation(report)
    return report


def interpretation(report: dict[str, Any]) -> list[str]:
    state = report.get("state") or {}
    lanes = {lane.get("label"): lane for lane in report.get("lanes") or []}
    post = lanes.get("post_child_birth") or {}
    notes = [
        "Research-only child watch; no live bot changes or orders.",
        f"Child freeze UTC is {state.get('freeze_ts_utc')}; only post_child_birth is strict evidence.",
        "Diagnostic context is allowed to shape hypotheses, not promotion.",
    ]
    for label in ["diagnostic_v2_common_clock_context", "diagnostic_v3_common_clock_context", "post_child_birth"]:
        lane = lanes.get(label) or {}
        notes.append(
            f"{label}: settled {lane.get('settled')}, child suppressed {lane.get('child_suppressed')}, "
            f"helpful/harmful {lane.get('child_helpful')}/{lane.get('child_harmful')}, "
            f"child delta {lane.get('child_delta_vs_parent_cents')}c, candidate net {lane.get('candidate_net_cents')}c, "
            f"blockers {lane.get('blockers')}."
        )
    if post.get("settled", 0) == 0:
        notes.append("Post-birth evidence has not started, so this branch is watch-only.")
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
        f"parent={fmt(row.get('parent_cents'))} hold={fmt(row.get('hold_cents'))} "
        f"cand={fmt(row.get('candidate_cents'))} child_delta={fmt(row.get('child_delta_vs_parent_cents'))} "
        f"tags={row.get('tags')}"
    )


def write_md(report: dict[str, Any]) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8")
    lines = [
        "# v28 Frozen Exit Common-Clock Residual Child Watch",
        "",
        "Research-only. No live bot changes or orders.",
        "",
        f"- Generated UTC: `{report.get('generated_at_utc')}`",
        f"- State: `{report.get('state')}`",
        "",
        "## Interpretation",
        "",
    ]
    lines.extend(f"- {note}" for note in report.get("interpretation") or [])
    lines.extend(
        [
            "",
            "## Lanes",
            "",
            "| lane | strict | settled | parent suppressed | child suppressed | child helpful/harmful | current | parent | candidate | child delta | cushion | blockers |",
            "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|",
        ]
    )
    for lane in report.get("lanes") or []:
        lines.append(
            f"| `{lane.get('label')}` | `{lane.get('strict_forward')}` | {lane.get('settled')} | "
            f"{lane.get('parent_suppressed')} | {lane.get('child_suppressed')} | "
            f"{lane.get('child_helpful')}/{lane.get('child_harmful')} | "
            f"{fmt(lane.get('current_net_cents'))}c | {fmt(lane.get('parent_net_cents'))}c | "
            f"{fmt(lane.get('candidate_net_cents'))}c | {fmt(lane.get('child_delta_vs_parent_cents'))}c | "
            f"{lane.get('full_loss_cushion_estimate')} | {', '.join(lane.get('blockers') or []) or 'none'} |"
        )
    for lane in report.get("lanes") or []:
        lines.extend(["", f"## {lane.get('label')}", "", "### Child Rows"])
        for row in lane.get("child_rows") or []:
            lines.append(f"- {short_row(row)}")
        lines.extend(["", "### Worst Candidate Rows"])
        for row in lane.get("worst_candidate_rows") or []:
            lines.append(f"- {short_row(row)}")
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    report = build_report()
    write_md(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
