"""Audit false-hold guardrail overlap with active v28 exit-watch rows.

Research-only; no live bot changes or orders.

The promotion gate correctly treats false-hold harm as a safety blocker, but
that can mix two different reads: observed harmful suppressions in a watch's
own strict rows versus historical/adjacent false-hold mechanism risk. This
probe separates those reads without weakening the promotion gates.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
GATE_JSON = OUT_DIR / "v28_exit_watch_promotion_gate_audit_latest.json"
GUARDRAIL_JSON = OUT_DIR / "v28_exit_false_hold_guardrail_bridge_latest.json"
OUT_JSON = OUT_DIR / "v28_exit_false_hold_rule_overlap_audit_latest.json"
OUT_MD = OUT_DIR / "v28_exit_false_hold_rule_overlap_audit_latest.md"

SOURCES = {
    "book_gap_suppression": OUT_DIR / "v28_frozen_exit_book_gap_suppression_latest.json",
    "book_gap_loss_guard": OUT_DIR / "v28_frozen_exit_book_gap_loss_guard_latest.json",
    "book_gap_loss_guard_v2": OUT_DIR / "v28_frozen_exit_book_gap_loss_guard_v2_latest.json",
    "book_gap_loss_guard_v3": OUT_DIR / "v28_frozen_exit_book_gap_loss_guard_v3_latest.json",
    "book_gap_value_only": OUT_DIR / "v28_frozen_exit_book_gap_value_only_latest.json",
    "dual_exit_book_gap_else_reduce": OUT_DIR / "v28_frozen_dual_exit_book_gap_else_reduce_latest.json",
    "reduce_geometry_relaxed": OUT_DIR / "v28_frozen_exit_reduce_geometry_relaxed_watch_latest.json",
    "exit_shallow_drawdown": OUT_DIR / "v28_frozen_exit_shallow_drawdown_watch_latest.json",
    "value_exit_feature_side_guard": OUT_DIR / "v28_frozen_value_exit_feature_side_guard_latest.json",
}


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


def row_key(row: dict[str, Any]) -> tuple[str, str, str, str]:
    return (
        str(row.get("market") or ""),
        str(row.get("side") or ""),
        str(row.get("exit_reason") or ""),
        str(row.get("exit_ts") or ""),
    )


def guardrail_harm_keys(payload: dict[str, Any]) -> set[tuple[str, str, str, str]]:
    keys: set[tuple[str, str, str, str]] = set()
    for row in payload.get("examples") or []:
        if isinstance(row, dict) and fnum(row.get("delta_cents")) < 0:
            keys.add(row_key(row))
    return keys


def strict_row_groups(payload: dict[str, Any]) -> list[tuple[str, list[dict[str, Any]]]]:
    groups: list[tuple[str, list[dict[str, Any]]]] = []
    rows = payload.get("rows")
    if isinstance(rows, list):
        groups.append(("top_level_rows", [row for row in rows if isinstance(row, dict)]))
    for lane in payload.get("lanes") or []:
        if not isinstance(lane, dict):
            continue
        lane_name = str(lane.get("lane") or "")
        lane_rows = lane.get("rows")
        if not isinstance(lane_rows, list):
            continue
        if "diagnostic" in lane_name or "prefreeze" in lane_name:
            continue
        groups.append((lane_name or "lane_rows", [row for row in lane_rows if isinstance(row, dict)]))
    return groups


def row_delta(row: dict[str, Any]) -> float:
    if row.get("delta_cents") is not None:
        return fnum(row.get("delta_cents"))
    current = row.get("current_cents")
    candidate = row.get("candidate_cents")
    if current is not None and candidate is not None:
        return fnum(candidate) - fnum(current)
    current = row.get("weighted_current_cents")
    candidate = row.get("weighted_candidate_cents")
    if current is not None and candidate is not None:
        return fnum(candidate) - fnum(current)
    return 0.0


def summarize_source(lane: str, path: Path, guard_keys: set[tuple[str, str, str, str]]) -> dict[str, Any]:
    payload = load_json(path)
    groups = strict_row_groups(payload)
    rows: list[dict[str, Any]] = []
    group_counts: dict[str, int] = {}
    for group, group_rows in groups:
        group_counts[group] = len(group_rows)
        rows.extend(group_rows)

    settled_rows = [row for row in rows if row.get("result") not in (None, "", "unknown")]
    scored_rows = settled_rows or rows
    suppressed = [row for row in scored_rows if row.get("suppressed") is True]
    harmful = [row for row in suppressed if row_delta(row) < 0]
    helpful = [row for row in suppressed if row_delta(row) > 0]
    overlap = [row for row in suppressed if row_key(row) in guard_keys]
    harmful_overlap = [row for row in harmful if row_key(row) in guard_keys]
    return {
        "lane": lane,
        "source": str(path),
        "row_groups": group_counts,
        "rows": len(rows),
        "settled_rows": len(settled_rows),
        "suppressed": len(suppressed),
        "helpful_suppressed": len(helpful),
        "harmful_suppressed": len(harmful),
        "suppressed_delta_cents": sum(row_delta(row) for row in suppressed),
        "harmful_delta_cents": sum(row_delta(row) for row in harmful),
        "guardrail_example_overlap": len(overlap),
        "harmful_guardrail_example_overlap": len(harmful_overlap),
        "top_harmful": sorted(
            (
                {
                    "market": row.get("market"),
                    "side": row.get("side"),
                    "exit_reason": row.get("exit_reason"),
                    "exit_cents": row.get("exit_cents") or row.get("exit_price_cents"),
                    "p_hold": row.get("p_hold"),
                    "hold_book_gap": row.get("hold_book_gap"),
                    "fair_drawdown_cents": row.get("fair_drawdown_cents"),
                    "delta_cents": row_delta(row),
                }
                for row in harmful
            ),
            key=lambda item: fnum(item.get("delta_cents")),
        )[:5],
    }


def build_report() -> dict[str, Any]:
    gate = load_json(GATE_JSON)
    guardrail = load_json(GUARDRAIL_JSON)
    guard_keys = guardrail_harm_keys(guardrail)
    gate_rows = {str(row.get("lane")): row for row in gate.get("rows") or [] if isinstance(row, dict)}
    rows = []
    for lane, path in SOURCES.items():
        row = summarize_source(lane, path, guard_keys)
        gate_row = gate_rows.get(lane) or {}
        row["gate_read"] = gate_row.get("primary_read") or gate_row.get("read")
        row["gate_status"] = gate_row.get("status")
        row["gate_false_hold_guard"] = bool(gate_row.get("false_hold_guardrail_required") or gate_row.get("false_hold_guard"))
        row["gate_blockers"] = gate_row.get("hard_blockers") or gate_row.get("blockers") or []
        if row["gate_false_hold_guard"] and row["harmful_suppressed"] == 0:
            row["read"] = "guardrail_prior_risk_no_current_strict_harm"
        elif row["harmful_suppressed"] > 0:
            row["read"] = "observed_current_strict_harm"
        elif row["suppressed"] == 0:
            row["read"] = "rule_not_firing_or_no_strict_suppression"
        else:
            row["read"] = "current_strict_suppression_clean_but_immature"
        rows.append(row)

    return {
        "generated_at_utc": utc_now_iso(),
        "inputs": {
            "promotion_gate": str(GATE_JSON),
            "false_hold_guardrail": str(GUARDRAIL_JSON),
        },
        "guardrail_harm_example_count": len(guard_keys),
        "rows": rows,
        "interpretation": [
            "Research-only audit; this does not relax the false-hold guardrail or approve any exit watch.",
            "A lane with zero current harmful suppressed rows can still be blocked by prior false-hold mechanism risk until it has enough strict suppressions.",
            "Observed current strict harm is stronger evidence than broad tag overlap; prior-risk-only lanes should keep collecting rather than be promoted.",
        ],
    }


def fmt_cents(value: Any) -> str:
    return f"{fnum(value):.2f}"


def write_markdown(report: dict[str, Any]) -> None:
    lines = [
        "# v28 Exit False-Hold Rule Overlap Audit",
        "",
        "Research-only. No live bot logic changes, no orders, no process control.",
        "",
        f"- Generated UTC: `{report.get('generated_at_utc')}`",
        f"- Guardrail harmful example keys: `{report.get('guardrail_harm_example_count')}`",
        "",
        "## Interpretation",
        "",
    ]
    lines.extend(f"- {note}" for note in report.get("interpretation") or [])
    lines.extend(
        [
            "",
            "## Lane Table",
            "",
            "| lane | read | gate read | rows | settled | suppressed | helpful | harmful | delta c | harm c | guard overlap | harmful overlap | gate false-hold | blockers |",
            "|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|---|",
        ]
    )
    for row in report.get("rows") or []:
        lines.append(
            "| "
            + " | ".join(
                [
                    f"`{row.get('lane')}`",
                    f"`{row.get('read')}`",
                    f"`{row.get('gate_read')}`",
                    str(row.get("rows")),
                    str(row.get("settled_rows")),
                    str(row.get("suppressed")),
                    str(row.get("helpful_suppressed")),
                    str(row.get("harmful_suppressed")),
                    fmt_cents(row.get("suppressed_delta_cents")),
                    fmt_cents(row.get("harmful_delta_cents")),
                    str(row.get("guardrail_example_overlap")),
                    str(row.get("harmful_guardrail_example_overlap")),
                    f"`{row.get('gate_false_hold_guard')}`",
                    ", ".join(row.get("gate_blockers") or []) or "none",
                ]
            )
            + " |"
        )
    lines.extend(["", "## Current Harm Examples", ""])
    for row in report.get("rows") or []:
        harmful = row.get("top_harmful") or []
        if not harmful:
            continue
        lines.append(f"### {row.get('lane')}")
        for item in harmful:
            lines.append(
                f"- `{item.get('market')}` `{item.get('side')}` {fmt_cents(item.get('delta_cents'))}c "
                f"exit `{item.get('exit_reason')}`, exit `{item.get('exit_cents')}`, "
                f"p_hold `{item.get('p_hold')}`, book_gap `{item.get('hold_book_gap')}`, "
                f"fair_drawdown `{item.get('fair_drawdown_cents')}`"
            )
        lines.append("")
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    report = build_report()
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
    write_markdown(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
