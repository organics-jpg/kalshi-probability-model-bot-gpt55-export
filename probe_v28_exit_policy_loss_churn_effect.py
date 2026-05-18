"""Loss-count churn effect for frozen v28 exit-policy candidates.

Research-only; no live bot changes or orders.

Live-readiness is currently blocked by loss-count churn rather than full-loss
drawdown. This report scores exit repairs by their effect on losing-row counts
inside each policy's own frozen/research window, separate from raw PnL.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
OUT_JSON = OUT_DIR / "v28_exit_policy_loss_churn_effect_latest.json"
OUT_MD = OUT_DIR / "v28_exit_policy_loss_churn_effect_latest.md"

ROW_ARTIFACTS = {
    "exit_reduce_suppression": OUT_DIR / "v28_frozen_exit_reduce_suppression_latest.json",
    "exit_reduce_yes_suppression": OUT_DIR / "v28_frozen_exit_reduce_yes_suppression_latest.json",
    "exit_book_gap_suppression": OUT_DIR / "v28_frozen_exit_book_gap_suppression_latest.json",
    "exit_book_gap_loss_guard": OUT_DIR / "v28_frozen_exit_book_gap_loss_guard_latest.json",
    "exit_book_gap_loss_guard_v2": OUT_DIR / "v28_frozen_exit_book_gap_loss_guard_v2_latest.json",
    "exit_book_gap_loss_guard_v3": OUT_DIR / "v28_frozen_exit_book_gap_loss_guard_v3_latest.json",
    "exit_book_gap_value_only": OUT_DIR / "v28_frozen_exit_book_gap_value_only_latest.json",
    "dual_exit_book_gap_else_reduce": OUT_DIR / "v28_frozen_dual_exit_book_gap_else_reduce_latest.json",
}

LANE_SUMMARY_ARTIFACTS = {
    "exit_reduce_depth_gate": OUT_DIR / "v28_frozen_exit_reduce_depth_gate_latest.json",
    "exit_reduce_observable_loss_control": OUT_DIR / "v28_frozen_exit_reduce_observable_loss_control_watch_latest.json",
    "exit_value_reduce_depth_composite": OUT_DIR / "v28_frozen_exit_value_reduce_depth_composite_latest.json",
}

LEGACY_LANE_LABELS = {
    ("exit_reduce_observable_loss_control", "post_observable_birth"): "observable_reduce_loss_control_post_birth",
    ("exit_reduce_observable_loss_control", "diagnostic_from_reduce_freeze"): "observable_reduce_loss_control_diagnostic",
}

SUMMARY_ARTIFACTS = {
    # Kept as a fallback for older artifacts without lane/variant detail.
    "_fallback_observable_reduce_loss_control_post_birth": (
        OUT_DIR / "v28_frozen_exit_reduce_observable_loss_control_watch_latest.json",
        "post_observable_birth",
    ),
    "_fallback_observable_reduce_loss_control_diagnostic": (
        OUT_DIR / "v28_frozen_exit_reduce_observable_loss_control_watch_latest.json",
        "diagnostic_from_reduce_freeze",
    ),
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


def as_float(value: Any) -> float | None:
    if value is None or value == "":
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def money(value: Any) -> str:
    number = as_float(value)
    if number is None:
        return "n/a"
    return f"{number:.0f}c (${number / 100.0:.2f})"


def sign(value: float) -> str:
    if value > 0:
        return "win"
    if value < 0:
        return "loss"
    return "flat"


def summarize_rows(label: str, payload: dict[str, Any]) -> dict[str, Any]:
    rows = payload.get("rows")
    if not isinstance(rows, list):
        rows = []
    usable = [
        row for row in rows
        if as_float(row.get("current_cents")) is not None
        and as_float(row.get("candidate_cents")) is not None
    ]
    current_values = [as_float(row.get("current_cents")) or 0.0 for row in usable]
    candidate_values = [as_float(row.get("candidate_cents")) or 0.0 for row in usable]
    suppressed_rows = [row for row in usable if row.get("suppressed") is True]
    loss_to_non_loss = [
        row for row in usable
        if (as_float(row.get("current_cents")) or 0.0) < 0.0
        and (as_float(row.get("candidate_cents")) or 0.0) >= 0.0
    ]
    non_loss_to_loss = [
        row for row in usable
        if (as_float(row.get("current_cents")) or 0.0) >= 0.0
        and (as_float(row.get("candidate_cents")) or 0.0) < 0.0
    ]
    loss_to_smaller_loss = [
        row for row in usable
        if (as_float(row.get("current_cents")) or 0.0) < 0.0
        and (as_float(row.get("candidate_cents")) or 0.0) < 0.0
        and (as_float(row.get("candidate_cents")) or 0.0) > (as_float(row.get("current_cents")) or 0.0)
    ]
    worsened_losses = [
        row for row in usable
        if (as_float(row.get("candidate_cents")) or 0.0) < (as_float(row.get("current_cents")) or 0.0)
    ]
    current_losses = sum(1 for value in current_values if value < 0.0)
    candidate_losses = sum(1 for value in candidate_values if value < 0.0)
    current_wins = sum(1 for value in current_values if value > 0.0)
    candidate_wins = sum(1 for value in candidate_values if value > 0.0)
    current_near_full = sum(1 for value in current_values if -100.0 < value <= -50.0)
    candidate_near_full = sum(1 for value in candidate_values if -100.0 < value <= -50.0)
    current_full = sum(1 for value in current_values if value <= -100.0)
    candidate_full = sum(1 for value in candidate_values if value <= -100.0)
    summary = payload.get("summary") if isinstance(payload.get("summary"), dict) else {}
    loss_control_cost = summary.get("loss_control_cost_cents")
    full_loss_cushion = summary.get("full_loss_cushion_estimate")
    return {
        "label": label,
        "candidate": (payload.get("freeze") or {}).get("candidate") or payload.get("candidate"),
        "evidence": "strict_forward",
        "source_kind": "row_replay",
        "rows": len(usable),
        "current_net_cents": sum(current_values),
        "candidate_net_cents": sum(candidate_values),
        "delta_cents": sum(candidate_values) - sum(current_values),
        "current_wins": current_wins,
        "current_losses": current_losses,
        "candidate_wins": candidate_wins,
        "candidate_losses": candidate_losses,
        "loss_count_reduction": current_losses - candidate_losses,
        "loss_to_non_loss": len(loss_to_non_loss),
        "loss_to_smaller_loss": len(loss_to_smaller_loss),
        "non_loss_to_loss": len(non_loss_to_loss),
        "worsened_rows": len(worsened_losses),
        "current_near_full": current_near_full,
        "candidate_near_full": candidate_near_full,
        "current_full": current_full,
        "candidate_full": candidate_full,
        "suppressed_rows": len(suppressed_rows),
        "suppressed_loss_to_non_loss": sum(1 for row in suppressed_rows if row in loss_to_non_loss),
        "suppressed_non_loss_to_loss": sum(1 for row in suppressed_rows if row in non_loss_to_loss),
        "suppressed_losers": summary.get("suppressed_losers"),
        "loss_control_cost_cents": loss_control_cost,
        "full_loss_cushion_estimate": full_loss_cushion,
        "loss_reduction_pct": (
            None if current_losses == 0 else (current_losses - candidate_losses) / current_losses * 100.0
        ),
        "blockers": payload.get("blockers") or [],
        "top_loss_to_non_loss": [
            compact_row(row) for row in sorted(
                loss_to_non_loss,
                key=lambda item: as_float(item.get("delta_cents")) or 0.0,
                reverse=True,
            )[:8]
        ],
        "top_new_losses": [
            compact_row(row) for row in sorted(
                non_loss_to_loss,
                key=lambda item: as_float(item.get("delta_cents")) or 0.0,
            )[:8]
        ],
    }


def compact_row(row: dict[str, Any]) -> dict[str, Any]:
    current = as_float(row.get("current_cents")) or 0.0
    candidate = as_float(row.get("candidate_cents")) or 0.0
    return {
        "market": row.get("market"),
        "side": row.get("side"),
        "result": row.get("result"),
        "entry_ts": row.get("entry_ts"),
        "exit_reason": row.get("exit_reason"),
        "current_cents": current,
        "candidate_cents": candidate,
        "delta_cents": candidate - current,
        "current_sign": sign(current),
        "candidate_sign": sign(candidate),
        "p_hold": row.get("p_hold"),
        "exit_cents": row.get("exit_cents"),
    }


def summary_variant(label: str, payload: dict[str, Any], lane_name: str) -> dict[str, Any]:
    lanes = payload.get("lanes") or []
    lane = next((item for item in lanes if item.get("lane") == lane_name), {})
    variant = (lane.get("variants") or [{}])[0]
    summary = variant.get("summary") or {}
    current_losses = int(as_float(summary.get("current_losses")) or 0)
    candidate_losses = int(as_float(summary.get("candidate_losses")) or 0)
    current_wins = int(as_float(summary.get("current_wins")) or 0)
    candidate_wins = int(as_float(summary.get("candidate_wins")) or 0)
    return {
        "label": label,
        "candidate": variant.get("candidate"),
        "evidence": "strict_forward" if lane_name.startswith("post_") else "diagnostic_only",
        "source_kind": "lane_summary",
        "rows": summary.get("settled") or summary.get("rows"),
        "current_net_cents": summary.get("current_gross_cents"),
        "candidate_net_cents": summary.get("candidate_gross_cents"),
        "delta_cents": summary.get("delta_vs_current_cents"),
        "current_wins": current_wins,
        "current_losses": current_losses,
        "candidate_wins": candidate_wins,
        "candidate_losses": candidate_losses,
        "loss_count_reduction": current_losses - candidate_losses,
        "loss_to_non_loss": None,
        "loss_to_smaller_loss": None,
        "non_loss_to_loss": None,
        "worsened_rows": None,
        "current_near_full": None,
        "candidate_near_full": None,
        "current_full": None,
        "candidate_full": None,
        "suppressed_rows": summary.get("suppressed_exits"),
        "suppressed_losers": summary.get("suppressed_losers"),
        "suppressed_loss_to_non_loss": None,
        "suppressed_non_loss_to_loss": summary.get("suppressed_losers"),
        "loss_control_cost_cents": summary.get("loss_control_cost_cents"),
        "full_loss_cushion_estimate": summary.get("full_loss_cushion_estimate"),
        "loss_reduction_pct": (
            None if current_losses == 0 else (current_losses - candidate_losses) / current_losses * 100.0
        ),
        "blockers": variant.get("blockers") or [],
        "top_loss_to_non_loss": [],
        "top_new_losses": [],
    }


def lane_summary_rows(label_prefix: str, payload: dict[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for lane in payload.get("lanes") or []:
        if not isinstance(lane, dict):
            continue
        lane_name = str(lane.get("lane") or "")
        label = LEGACY_LANE_LABELS.get((label_prefix, lane_name), f"{label_prefix}_{lane_name}")
        for variant in lane.get("variants") or []:
            if not isinstance(variant, dict):
                continue
            summary = variant.get("summary") or {}
            if not isinstance(summary, dict):
                continue
            current_losses = int(as_float(summary.get("current_losses")) or 0)
            candidate_losses = int(as_float(summary.get("candidate_losses")) or 0)
            current_wins = int(as_float(summary.get("current_wins")) or 0)
            candidate_wins = int(as_float(summary.get("candidate_wins")) or 0)
            rows.append({
                "label": label,
                "candidate": variant.get("candidate"),
                "evidence": "strict_forward" if lane_name.startswith("post_") else "diagnostic_only",
                "source_kind": "lane_summary",
                "rows": summary.get("settled") or summary.get("rows"),
                "current_net_cents": summary.get("current_gross_cents"),
                "candidate_net_cents": summary.get("candidate_gross_cents") or summary.get("net_cents"),
                "delta_cents": summary.get("delta_vs_current_cents"),
                "current_wins": current_wins,
                "current_losses": current_losses,
                "candidate_wins": candidate_wins,
                "candidate_losses": candidate_losses,
                "loss_count_reduction": current_losses - candidate_losses,
                "loss_to_non_loss": None,
                "loss_to_smaller_loss": None,
                "non_loss_to_loss": None,
                "worsened_rows": None,
                "current_near_full": None,
                "candidate_near_full": None,
                "current_full": None,
                "candidate_full": None,
                "suppressed_rows": summary.get("suppressed_exits"),
                "suppressed_losers": summary.get("suppressed_losers"),
                "suppressed_loss_to_non_loss": None,
                "suppressed_non_loss_to_loss": summary.get("suppressed_losers"),
                "loss_control_cost_cents": summary.get("loss_control_cost_cents"),
                "full_loss_cushion_estimate": summary.get("full_loss_cushion_estimate"),
                "loss_reduction_pct": (
                    None if current_losses == 0 else (current_losses - candidate_losses) / current_losses * 100.0
                ),
                "blockers": variant.get("blockers") or [],
                "top_loss_to_non_loss": [],
                "top_new_losses": [],
            })
    return rows


def build_report() -> dict[str, Any]:
    rows = [summarize_rows(label, load_json(path)) for label, path in ROW_ARTIFACTS.items()]
    for label_prefix, path in LANE_SUMMARY_ARTIFACTS.items():
        lane_rows = lane_summary_rows(label_prefix, load_json(path))
        if lane_rows:
            rows.extend(lane_rows)
    seen_lane_labels = {
        (row.get("label"), row.get("evidence"))
        for row in rows
        if row.get("source_kind") == "lane_summary"
    }
    for label, (path, lane_name) in SUMMARY_ARTIFACTS.items():
        fallback_label = label.removeprefix("_fallback_")
        evidence = "strict_forward" if lane_name.startswith("post_") else "diagnostic_only"
        if (fallback_label, evidence) not in seen_lane_labels:
            rows.append(summary_variant(fallback_label, load_json(path), lane_name))
    rows.sort(
        key=lambda item: (
            as_float(item.get("loss_count_reduction")) or -999999.0,
            as_float(item.get("delta_cents")) or -999999.0,
        ),
        reverse=True,
    )
    return {
        "generated_at_utc": utc_now_iso(),
        "interpretation": [
            "This is a churn-readiness lens, not a promotion decision.",
            "Positive loss-count reduction means fewer losing rows inside that candidate's own frozen/research window.",
            "Rows are not all on a common clock; use this to pick mechanisms for common-clock validation, not to promote live logic.",
        ],
        "rows": rows,
    }


def write_md(report: dict[str, Any]) -> None:
    lines = [
        "# v28 Exit Policy Loss-Count Churn Effect",
        "",
        "Research-only. No live bot changes or orders.",
        "",
        f"- Generated UTC: `{report['generated_at_utc']}`",
        "",
        "## Interpretation",
        "",
    ]
    lines.extend(f"- {note}" for note in report["interpretation"])
    lines.extend([
        "",
        "## Churn Ranking",
        "",
        "| rank | lane | candidate | rows | current W/L | candidate W/L | loss count delta | net delta | suppressed | new losses | near-full delta | blockers |",
        "|---:|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---|",
    ])
    for idx, row in enumerate(report["rows"], start=1):
        near_full_delta = ""
        if row.get("current_near_full") is not None and row.get("candidate_near_full") is not None:
            near_full_delta = str(int(row["current_near_full"]) - int(row["candidate_near_full"]))
        lines.append(
            f"| {idx} | `{row['label']}` | `{row.get('candidate')}` | {row.get('rows')} | "
            f"{row.get('current_wins')}/{row.get('current_losses')} | "
            f"{row.get('candidate_wins')}/{row.get('candidate_losses')} | "
            f"{row.get('loss_count_reduction')} | {money(row.get('delta_cents'))} | "
            f"{row.get('suppressed_rows')} | {row.get('non_loss_to_loss')} | {near_full_delta} | "
            f"{', '.join(str(item) for item in row.get('blockers') or [])} |"
        )
    lines.extend([
        "",
        "## Best Loss-To-Non-Loss Examples",
        "",
    ])
    for row in report["rows"][:5]:
        examples = row.get("top_loss_to_non_loss") or []
        if not examples:
            continue
        lines.append(f"### {row['label']}")
        lines.append("")
        lines.append("| market | side | result | reason | current | candidate | delta | p_hold |")
        lines.append("|---|---|---|---|---:|---:|---:|---:|")
        for example in examples[:5]:
            lines.append(
                f"| `{example.get('market')}` | {example.get('side')} | {example.get('result')} | "
                f"{example.get('exit_reason')} | {money(example.get('current_cents'))} | "
                f"{money(example.get('candidate_cents'))} | {money(example.get('delta_cents'))} | "
                f"{example.get('p_hold')} |"
            )
        lines.append("")
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    report = build_report()
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_md(report)
    print(str(OUT_MD))


if __name__ == "__main__":
    main()
