"""Forward runway for the mid-price boundary + guarded exit stack.

Research-only; no live bot changes or orders.

This report turns the stack's blockers into concrete forward requirements:
how many post-stack joined exits, clean source rows, and weighted cents are
needed before the stack can graduate from diagnostic overlap to promotion
discussion.
"""
from __future__ import annotations

import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
STACK_JSON = OUT_DIR / "v28_soft_frontier_midprice_boundary_exit_stack_latest.json"
OUT_JSON = OUT_DIR / "v28_soft_frontier_midprice_boundary_exit_stack_runway_latest.json"
OUT_MD = OUT_DIR / "v28_soft_frontier_midprice_boundary_exit_stack_runway_latest.md"

MIN_POST_STACK_JOINED = 30
MIN_FULL_LOSS_CUSHION = 3
MAX_RECONSTRUCTED_SHARE = 0.35
TARGET_CUSHION_CENTS = MIN_FULL_LOSS_CUSHION * 100.0


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


def full_loss_cushion(net_cents: float) -> int:
    return int(max(0.0, net_cents) // 100.0)


def source_counts(rows: list[dict[str, Any]]) -> dict[str, int]:
    return dict(Counter(str(row.get("source") or "unknown") for row in rows if isinstance(row, dict)))


def reconstructed_share_from_counts(counts: dict[str, int]) -> float | None:
    total = sum(counts.values())
    if total <= 0:
        return None
    return (total - int(counts.get("approved_entry") or 0)) / total


def clean_rows_needed_for_share(counts: dict[str, int]) -> int:
    total = sum(counts.values())
    approved = int(counts.get("approved_entry") or 0)
    if total <= 0:
        return 0
    needed = 0
    while total > 0 and (total - approved) / total > MAX_RECONSTRUCTED_SHARE:
        needed += 1
        total += 1
        approved += 1
    return needed


def evaluate_variant(variant: dict[str, Any]) -> dict[str, Any]:
    post_rows = variant.get("post_stack_joined_rows") if isinstance(variant.get("post_stack_joined_rows"), list) else []
    post_counts = source_counts(post_rows)
    post_share = reconstructed_share_from_counts(post_counts)
    post_net = as_float(variant.get("post_stack_weighted_exit_candidate_cents")) or 0.0
    post_delta = as_float(variant.get("post_stack_weighted_exit_delta_cents")) or 0.0
    post_joined = int(variant.get("post_stack_joined_exit_rows") or 0)
    rows_needed = max(0, MIN_POST_STACK_JOINED - post_joined)
    cents_needed = max(0.0, TARGET_CUSHION_CENTS - post_net)
    blockers = list(variant.get("blockers") or [])
    runway_blockers = []
    if rows_needed:
        runway_blockers.append("needs_post_stack_joined_rows")
    if cents_needed:
        runway_blockers.append("needs_weighted_cushion_cents")
    if post_share is not None and post_share > MAX_RECONSTRUCTED_SHARE:
        runway_blockers.append("needs_clean_source_dilution")
    if not bool(variant.get("strict_forward")):
        runway_blockers.append("entry_lane_not_strict_combo_forward")
    return {
        "candidate": variant.get("candidate"),
        "lane": variant.get("lane"),
        "policy": variant.get("policy"),
        "exit_source": variant.get("exit_source"),
        "strict_forward": bool(variant.get("strict_forward")),
        "entry_summary": variant.get("entry_summary") or {},
        "diagnostic_joined_exit_rows": variant.get("joined_exit_rows"),
        "diagnostic_weighted_exit_net_cents": variant.get("weighted_joined_exit_candidate_cents"),
        "diagnostic_weighted_exit_delta_cents": variant.get("weighted_joined_exit_delta_cents"),
        "post_stack_joined_exit_rows": post_joined,
        "post_stack_weighted_exit_net_cents": post_net,
        "post_stack_weighted_exit_delta_cents": post_delta,
        "post_stack_source_counts": post_counts,
        "post_stack_reconstructed_share": post_share,
        "post_stack_clean_rows_needed_for_source_gate": clean_rows_needed_for_share(post_counts),
        "post_stack_joined_rows_needed_for_sample_gate": rows_needed,
        "post_stack_weighted_cents_needed_for_cushion3": cents_needed,
        "post_stack_full_loss_cushion_estimate": full_loss_cushion(post_net),
        "candidate_blockers": blockers,
        "runway_blockers": runway_blockers,
    }


def build_report() -> dict[str, Any]:
    stack = load_json(STACK_JSON)
    rows = [evaluate_variant(row) for row in stack.get("variants") or [] if isinstance(row, dict)]
    rows.sort(
        key=lambda row: (
            len(row.get("runway_blockers") or []),
            row.get("post_stack_joined_rows_needed_for_sample_gate") or 999,
            row.get("post_stack_weighted_cents_needed_for_cushion3") or 999999.0,
            -float(row.get("diagnostic_weighted_exit_net_cents") or -999999.0),
        )
    )
    return {
        "generated_at_utc": utc_now_iso(),
        "stack_generated_at_utc": stack.get("generated_at_utc"),
        "stack_freeze": stack.get("freeze") or {},
        "rows": rows,
        "interpretation": interpretation(rows),
    }


def interpretation(rows: list[dict[str, Any]]) -> list[str]:
    notes = [
        "Runway only; no live logic changes and no promotion by itself.",
        "Post-stack joined rows are the promotion-relevant sample for this combined entry+exit branch.",
    ]
    if rows:
        best = rows[0]
        notes.append(
            f"Closest runway row {best.get('candidate')} has "
            f"{best.get('post_stack_joined_exit_rows')} post-stack joined exits, "
            f"{best.get('post_stack_weighted_exit_net_cents')}c post-stack net, "
            f"{best.get('post_stack_weighted_exit_delta_cents')}c post-stack delta, needs "
            f"{best.get('post_stack_joined_rows_needed_for_sample_gate')} joined rows and "
            f"{best.get('post_stack_weighted_cents_needed_for_cushion3')}c for cushion; blockers "
            f"{best.get('runway_blockers')}."
        )
    strict = [row for row in rows if row.get("strict_forward")]
    if strict:
        top_strict = strict[0]
        notes.append(
            f"Best strict entry-lane runway {top_strict.get('candidate')} has "
            f"{top_strict.get('post_stack_joined_exit_rows')} post-stack joined exits and needs "
            f"{top_strict.get('post_stack_joined_rows_needed_for_sample_gate')} more joined rows."
        )
    return notes


def fmt(value: Any) -> str:
    if value is None:
        return "None"
    if isinstance(value, float):
        return f"{value:.6f}"
    return str(value)


def write_md(report: dict[str, Any]) -> None:
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8")
    lines = [
        "# v28 Soft-Frontier Mid-Price Boundary Exit-Stack Runway",
        "",
        "Research-only; no live bot changes or orders.",
        "",
        f"- Generated UTC: `{report.get('generated_at_utc')}`",
        f"- Stack freeze UTC: `{(report.get('stack_freeze') or {}).get('freeze_ts_utc')}`",
        "",
        "## Interpretation",
        "",
    ]
    lines.extend(f"- {note}" for note in report.get("interpretation") or [])
    lines.extend([
        "",
        "## Runway",
        "",
        "| rank | candidate | strict | diagnostic joined | post-stack joined | post-stack net | post-stack delta | rows needed | cents needed | post recon | clean rows needed | runway blockers | candidate blockers |",
        "|---:|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---|---|",
    ])
    for idx, row in enumerate((report.get("rows") or [])[:30], start=1):
        lines.append(
            f"| {idx} | `{row.get('candidate')}` | {row.get('strict_forward')} | "
            f"{row.get('diagnostic_joined_exit_rows')} | {row.get('post_stack_joined_exit_rows')} | "
            f"{fmt(row.get('post_stack_weighted_exit_net_cents'))} | "
            f"{fmt(row.get('post_stack_weighted_exit_delta_cents'))} | "
            f"{row.get('post_stack_joined_rows_needed_for_sample_gate')} | "
            f"{fmt(row.get('post_stack_weighted_cents_needed_for_cushion3'))} | "
            f"{fmt(row.get('post_stack_reconstructed_share'))} | "
            f"{row.get('post_stack_clean_rows_needed_for_source_gate')} | "
            f"{', '.join(row.get('runway_blockers') or []) or 'none'} | "
            f"{', '.join(row.get('candidate_blockers') or []) or 'none'} |"
        )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    report = build_report()
    write_md(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
