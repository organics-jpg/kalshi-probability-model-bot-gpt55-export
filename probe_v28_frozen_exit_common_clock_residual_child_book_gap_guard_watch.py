"""Frozen book-gap guard watch for the common-clock residual exit child.

Research-only; no live bot changes or orders.

The base residual 70-79c child found both clipped winners and false holds.
The diagnostic guardrail scan showed that requiring a clearly negative
hold-book gap removes the observed strict false holds while keeping the
winner-clipping rows. This file freezes that observable child repair so only
future rows after its own birth can count.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import probe_v28_exit_policy_common_clock_watch as cc
import probe_v28_exit_common_clock_residual_child_guardrail_variants as guards
import probe_v28_frozen_exit_common_clock_residual_child_watch as residual


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
STATE_JSON = OUT_DIR / "v28_frozen_exit_common_clock_residual_child_book_gap_guard_watch_state.json"
OUT_JSON = OUT_DIR / "v28_frozen_exit_common_clock_residual_child_book_gap_guard_watch_latest.json"
OUT_MD = OUT_DIR / "v28_frozen_exit_common_clock_residual_child_book_gap_guard_watch_latest.md"

POLICY = "residual_exit70_79_book_gap_le_neg_0_5pp"
VARIANT = "book_gap_le_neg_0_5pp"
PHYSICS = (
    "A 70-79c exit may be a transient winner clip only when the order book still "
    "leans toward holding. Flat or positive hold-book gap in p_hold 75-79 "
    "probability-reduce exits is a false-hold risk."
)
MIN_SETTLED = 30
MIN_SUPPRESSED = 30
MIN_FULL_LOSS_CUSHION = 3


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
        "parent_child": "parent_loss_guard_plus_residual_exit70_79",
        "child_condition": "parent_not_suppressed_and_exit_price_70_79_and_hold_book_gap_le_neg_0_5pp",
        "diagnostic_source": str(OUT_DIR / "v28_exit_common_clock_residual_child_guardrail_variants_latest.json"),
        "physics": PHYSICS,
    }
    STATE_JSON.write_text(json.dumps(state, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return state


def fmt(value: Any) -> str:
    if value is None:
        return "n/a"
    if isinstance(value, float):
        return f"{value:.2f}"
    return str(value)


def build_report() -> dict[str, Any]:
    state = ensure_state()
    rows = cc.build_scored_rows()
    windows = residual.strict_windows()
    lanes = [
        guards.score_variant(
            cc.filter_snapshot(rows, windows.get("new_exit_mix_common_forward_v2")),
            "diagnostic_v2_common_clock_context",
            windows.get("new_exit_mix_common_forward_v2"),
            VARIANT,
            PHYSICS,
            lambda row, parent: guards.base_child(row, parent) and guards.gap_le(row, -0.005),
        ),
        guards.score_variant(
            cc.filter_snapshot(rows, windows.get("new_exit_mix_common_forward_v3")),
            "diagnostic_v3_common_clock_context",
            windows.get("new_exit_mix_common_forward_v3"),
            VARIANT,
            PHYSICS,
            lambda row, parent: guards.base_child(row, parent) and guards.gap_le(row, -0.005),
        ),
        guards.score_variant(
            cc.filter_snapshot(rows, state.get("freeze_ts_utc")),
            "post_book_gap_guard_birth",
            state.get("freeze_ts_utc"),
            VARIANT,
            PHYSICS,
            lambda row, parent: guards.base_child(row, parent) and guards.gap_le(row, -0.005),
        ),
    ]
    # score_variant only marks "post_child_birth" as strict; this watch has its own strict lane.
    for lane in lanes:
        lane["strict_forward"] = lane.get("lane") == "post_book_gap_guard_birth"
        blockers = list(lane.get("blockers") or [])
        if lane.get("strict_forward"):
            if int(lane.get("settled") or 0) < MIN_SETTLED and "settled_lt_30" not in blockers:
                blockers.append("settled_lt_30")
            if int(lane.get("child_suppressed") or 0) < MIN_SUPPRESSED and "child_suppressed_decisions_lt_30" not in blockers:
                blockers.append("child_suppressed_decisions_lt_30")
            if int(lane.get("full_loss_cushion_estimate") or 0) < MIN_FULL_LOSS_CUSHION and "full_loss_cushion_lt_3" not in blockers:
                blockers.append("full_loss_cushion_lt_3")
            lane["blockers"] = blockers
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
    lanes = {lane.get("lane"): lane for lane in report.get("lanes") or []}
    strict = lanes.get("post_book_gap_guard_birth") or {}
    notes = [
        "Research-only frozen child-repair watch; no live bot changes or orders.",
        f"Book-gap guard freeze UTC is {state.get('freeze_ts_utc')}; only post_book_gap_guard_birth is strict evidence for this child.",
        "Diagnostic common-clock lanes explain the mechanism but cannot promote the guard.",
        (
            f"post_book_gap_guard_birth: settled {strict.get('settled')}, child suppressed "
            f"{strict.get('child_suppressed')}, helpful/harmful {strict.get('child_helpful')}/"
            f"{strict.get('child_harmful')}, child delta {strict.get('child_delta_vs_parent_cents')}c, "
            f"candidate net {strict.get('candidate_net_cents')}c, blockers {strict.get('blockers')}."
        ),
    ]
    if int(strict.get("settled") or 0) == 0:
        notes.append("No post-birth rows yet; this is an empty strict watch.")
    return notes


def short_row(row: dict[str, Any]) -> str:
    return (
        f"{row.get('market')} {row.get('side')}/{row.get('result')} "
        f"parent={fmt(row.get('parent_cents'))} hold={fmt(row.get('hold_cents'))} "
        f"cand={fmt(row.get('candidate_cents'))} child_delta={fmt(row.get('child_delta_vs_parent_cents'))} "
        f"p_hold={fmt(row.get('p_hold'))} gap={fmt(row.get('hold_book_gap'))} tags={row.get('tags')}"
    )


def write_md(report: dict[str, Any]) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8")
    lines = [
        "# v28 Frozen Exit Common-Clock Residual Child Book-Gap Guard Watch",
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
    lines.extend([
        "",
        "## Lanes",
        "",
        "| lane | strict | settled | child suppressed | helpful/harmful | child delta | candidate net | delta vs current | cushion | blockers |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---|",
    ])
    for lane in report.get("lanes") or []:
        lines.append(
            f"| `{lane.get('lane')}` | {lane.get('strict_forward')} | {lane.get('settled')} | "
            f"{lane.get('child_suppressed')} | {lane.get('child_helpful')}/{lane.get('child_harmful')} | "
            f"{fmt(lane.get('child_delta_vs_parent_cents'))} | {fmt(lane.get('candidate_net_cents'))} | "
            f"{fmt(lane.get('delta_vs_current_cents'))} | {lane.get('full_loss_cushion_estimate')} | "
            f"{', '.join(lane.get('blockers') or []) or 'none'} |"
        )
    for lane in report.get("lanes") or []:
        lines.extend(["", f"## {lane.get('lane')}", "", "### Child Rows"])
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
