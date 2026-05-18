"""Audit partial-size treatment of the loss-guard v3 residual bucket.

Research-only; no live bot changes or orders.

The v3 book-gap loss guard rejects the v1-only bucket because older evidence
showed rare false-hold risk there. Recent strict v3 rows show a small positive
v1-only residual bucket, so this probe tests whether a continuous/partial-size
overlay is a real improvement or just a tempting sparse-sample relaxation.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from probe_v28_exit_loss_guard_v1_v2_v3_contrast import (
    BOOK_GAP_FREEZE,
    V1_STATE_JSON,
    V2_STATE_JSON,
    V3_STATE_JSON,
    build_scored_rows,
    cents,
    compact,
    filter_snapshot,
    label_for,
    load_json,
    policy_bits,
    row_ts,
)
from probe_v28_exit_policy_candidates import current_exit, hold_to_settlement, side_won


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
OUT_JSON = OUT_DIR / "v28_exit_loss_guard_v3_residual_bucket_size_shrink_latest.json"
OUT_MD = OUT_DIR / "v28_exit_loss_guard_v3_residual_bucket_size_shrink_latest.md"

POLICIES = [
    ("v3_control", 0.0),
    ("v3_plus_residual_quarter", 0.25),
    ("v3_plus_residual_half", 0.5),
    ("v3_plus_residual_full_v1_like", 1.0),
]


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def money(value: Any) -> str:
    number = cents(value)
    return f"{number:.1f}c (${number / 100.0:.2f})"


def full_loss_cushion(value: float) -> int:
    return max(0, int(value // 100.0))


def row_delta(row: dict[str, Any]) -> float:
    return cents(hold_to_settlement(row)) - cents(current_exit(row))


def summarize_bucket(rows: list[dict[str, Any]]) -> dict[str, Any]:
    deltas = [row_delta(row) for row in rows]
    helpful = [delta for row, delta in zip(rows, deltas) if side_won(row) is True]
    harmful = [delta for row, delta in zip(rows, deltas) if side_won(row) is False]
    return {
        "rows": len(rows),
        "net_delta_cents": sum(deltas),
        "helpful_rows": len(helpful),
        "harmful_rows": len(harmful),
        "helpful_delta_cents": sum(helpful),
        "harmful_delta_cents": sum(harmful),
        "avg_delta_cents": (sum(deltas) / len(deltas)) if deltas else 0.0,
        "worst_delta_cents": min(deltas) if deltas else 0.0,
        "best_delta_cents": max(deltas) if deltas else 0.0,
        "examples": sorted(
            rows,
            key=row_delta,
        )[:10],
    }


def summarize_window(
    name: str,
    freeze_ts: str | None,
    rows: list[dict[str, Any]],
    v1_state: dict[str, Any],
    v2_state: dict[str, Any],
    v3_state: dict[str, Any],
) -> dict[str, Any]:
    selected = filter_snapshot(rows, freeze_ts)
    current_net = sum(cents(current_exit(row)) for row in selected)
    v3_rows: list[dict[str, Any]] = []
    residual_rows: list[dict[str, Any]] = []
    other_rows: list[dict[str, Any]] = []

    for row in selected:
        bits = policy_bits(row, v1_state, v2_state, v3_state)
        label = label_for(bits)
        if bits[2]:
            v3_rows.append(row)
        elif label == "v1_only":
            residual_rows.append(row)
        else:
            other_rows.append(row)

    v3_delta = sum(row_delta(row) for row in v3_rows)
    residual_delta = sum(row_delta(row) for row in residual_rows)
    residual_harm = sum(row_delta(row) for row in residual_rows if side_won(row) is False)

    policies = []
    for policy, residual_weight in POLICIES:
        weighted_residual_delta = residual_delta * residual_weight
        weighted_residual_harm = residual_harm * residual_weight
        candidate_net = current_net + v3_delta + weighted_residual_delta
        delta_vs_current = v3_delta + weighted_residual_delta
        decision_count = len(v3_rows) + (len(residual_rows) if residual_weight > 0 else 0)
        effective_decision_weight = len(v3_rows) + residual_weight * len(residual_rows)
        blockers = []
        if len(selected) < 30:
            blockers.append("settled_lt_30")
        if decision_count < 30:
            blockers.append("suppressed_decisions_lt_30")
        if full_loss_cushion(candidate_net) < 3:
            blockers.append("candidate_full_loss_cushion_lt_3")
        if full_loss_cushion(delta_vs_current) < 3:
            blockers.append("delta_full_loss_cushion_lt_3")
        if residual_weight > 0 and residual_harm < 0:
            blockers.append("residual_false_hold_harm_present")
        if residual_weight > 0:
            blockers.append("residual_policy_not_independently_frozen")
        policies.append(
            {
                "policy": policy,
                "residual_weight": residual_weight,
                "rows": len(selected),
                "current_net_cents": current_net,
                "candidate_net_cents": candidate_net,
                "delta_vs_current_cents": delta_vs_current,
                "v3_selected_rows": len(v3_rows),
                "residual_rows": len(residual_rows),
                "decision_count": decision_count,
                "effective_decision_weight": effective_decision_weight,
                "v3_delta_cents": v3_delta,
                "weighted_residual_delta_cents": weighted_residual_delta,
                "weighted_residual_harm_cents": weighted_residual_harm,
                "candidate_full_loss_cushion": full_loss_cushion(candidate_net),
                "delta_full_loss_cushion": full_loss_cushion(delta_vs_current),
                "blockers": blockers,
            }
        )

    return {
        "window": name,
        "freeze_ts_utc": freeze_ts,
        "rows": len(selected),
        "current_net_cents": current_net,
        "v3_bucket": summarize_bucket(v3_rows),
        "residual_v1_only_bucket": summarize_bucket(residual_rows),
        "other_rows": len(other_rows),
        "policies": policies,
    }


def compact_examples(window: dict[str, Any]) -> None:
    for key in ["v3_bucket", "residual_v1_only_bucket"]:
        examples = []
        for row in (window.get(key) or {}).get("examples") or []:
            bits = row.get("_policy_bits")
            if bits is None:
                bits = (False, False, False)
            examples.append(compact(row, key, bits))
        (window.get(key) or {})["examples"] = examples


def build_report() -> dict[str, Any]:
    v1_state = load_json(V1_STATE_JSON)
    v2_state = load_json(V2_STATE_JSON)
    v3_state = load_json(V3_STATE_JSON)
    rows = build_scored_rows()

    for row in rows:
        row["_policy_bits"] = policy_bits(row, v1_state, v2_state, v3_state)

    windows = {
        "all_exit_rows_diagnostic": None,
        "book_gap_freeze_comparable": BOOK_GAP_FREEZE,
        "v1_strict_forward": v1_state.get("freeze_ts_utc"),
        "v2_strict_forward": v2_state.get("freeze_ts_utc"),
        "v3_strict_forward": v3_state.get("freeze_ts_utc"),
    }
    scored_windows = [
        summarize_window(name, freeze_ts, rows, v1_state, v2_state, v3_state)
        for name, freeze_ts in windows.items()
    ]
    for window in scored_windows:
        compact_examples(window)

    v3_window = next((window for window in scored_windows if window.get("window") == "v3_strict_forward"), {})
    residual = v3_window.get("residual_v1_only_bucket") or {}
    residual_rows = residual.get("rows") or 0
    residual_net = cents(residual.get("net_delta_cents"))
    residual_harm = cents(residual.get("harmful_delta_cents"))
    diagnostic = scored_windows[0] if scored_windows else {}
    diagnostic_residual = diagnostic.get("residual_v1_only_bucket") or {}

    interpretation = [
        "This is a research-only residual-bucket audit; it does not freeze a candidate or change live exits.",
        "The v1-only residual bucket is the extra exposure v3 currently rejects.",
        (
            f"Strict v3-forward residual currently has {residual_rows} row(s), "
            f"{residual_net:.1f}c net delta, and {residual_harm:.1f}c harmful delta."
        ),
        (
            "Diagnostic all-exit residual has "
            f"{diagnostic_residual.get('rows')} row(s), "
            f"{cents(diagnostic_residual.get('net_delta_cents')):.1f}c net, "
            f"and {cents(diagnostic_residual.get('harmful_delta_cents')):.1f}c harmful delta."
        ),
    ]
    if residual_rows and residual_net > 0 and cents(diagnostic_residual.get("net_delta_cents")) <= 0:
        interpretation.append(
            "The strict-forward residual is positive, but older diagnostic evidence is not; this is not enough to justify a new residual relaxation."
        )
    if residual_harm < 0 or cents(diagnostic_residual.get("harmful_delta_cents")) < 0:
        interpretation.append(
            "Residual false-hold risk remains the binding physical risk, so any future residual overlay needs its own freeze and should probably be partial-size rather than a full hold."
        )

    return {
        "generated_at_utc": utc_now_iso(),
        "v1_freeze_ts_utc": v1_state.get("freeze_ts_utc"),
        "v2_freeze_ts_utc": v2_state.get("freeze_ts_utc"),
        "v3_freeze_ts_utc": v3_state.get("freeze_ts_utc"),
        "base_scored_row_count": len(rows),
        "windows": scored_windows,
        "interpretation": interpretation,
    }


def write_md(report: dict[str, Any]) -> None:
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8")
    lines = [
        "# v28 Exit Loss-Guard V3 Residual Bucket Size-Shrink Audit",
        "",
        "Research-only; no live bot changes or orders.",
        "",
        f"- Generated UTC: `{report.get('generated_at_utc')}`",
        f"- V1 freeze UTC: `{report.get('v1_freeze_ts_utc')}`",
        f"- V2 freeze UTC: `{report.get('v2_freeze_ts_utc')}`",
        f"- V3 freeze UTC: `{report.get('v3_freeze_ts_utc')}`",
        "",
        "## Interpretation",
        "",
    ]
    lines.extend(f"- {note}" for note in report.get("interpretation") or [])

    for window in report.get("windows") or []:
        v3_bucket = window.get("v3_bucket") or {}
        residual = window.get("residual_v1_only_bucket") or {}
        lines.extend(
            [
                "",
                f"## {window.get('window')}",
                "",
                f"- Freeze UTC: `{window.get('freeze_ts_utc')}`",
                f"- Rows: `{window.get('rows')}`",
                f"- Current net: `{money(window.get('current_net_cents'))}`",
                f"- V3 selected rows/delta: `{v3_bucket.get('rows')}` / `{money(v3_bucket.get('net_delta_cents'))}`",
                f"- Residual v1-only rows/delta: `{residual.get('rows')}` / `{money(residual.get('net_delta_cents'))}`",
                f"- Residual helpful/harmful: `{residual.get('helpful_rows')}/{residual.get('harmful_rows')}`",
                f"- Residual harmful delta: `{money(residual.get('harmful_delta_cents'))}`",
                "",
                "| policy | residual weight | candidate c | delta c | selected rows | effective weight | residual weighted c | cushion cand/delta | blockers |",
                "|---|---:|---:|---:|---:|---:|---:|---:|---|",
            ]
        )
        for policy in window.get("policies") or []:
            lines.append(
                f"| `{policy.get('policy')}` | {policy.get('residual_weight')} | "
                f"{money(policy.get('candidate_net_cents'))} | {money(policy.get('delta_vs_current_cents'))} | "
                f"{policy.get('decision_count')} | {policy.get('effective_decision_weight'):.2f} | "
                f"{money(policy.get('weighted_residual_delta_cents'))} | "
                f"{policy.get('candidate_full_loss_cushion')}/{policy.get('delta_full_loss_cushion')} | "
                f"{', '.join(policy.get('blockers') or []) or 'none'} |"
            )
        examples = residual.get("examples") or []
        if examples:
            lines.extend(
                [
                    "",
                    "### Worst Residual Examples",
                    "",
                    "| market | side/result | reason | p_hold | gap | drawdown | exit | delta | tags |",
                    "|---|---|---|---:|---:|---:|---:|---:|---|",
                ]
            )
            for row in examples[:8]:
                lines.append(
                    f"| {row.get('market')} | {row.get('side')}/{row.get('result')} | "
                    f"{row.get('exit_reason')} | {row.get('p_hold')} | {row.get('hold_book_gap')} | "
                    f"{row.get('fair_drawdown_cents')} | {row.get('exit_price_cents')} | "
                    f"{money(row.get('delta_if_suppressed_cents'))} | {', '.join(row.get('tags') or [])} |"
                )

    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    report = build_report()
    write_md(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
