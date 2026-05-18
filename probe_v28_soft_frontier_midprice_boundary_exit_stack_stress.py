"""Stress drilldown for the mid-price boundary + guarded exit stack.

Research-only; no live bot changes or orders.

The stack can look strong because a broad diagnostic entry family overlaps a
book-gap exit sample. This audit asks whether the apparent gain is physically
distributed or just source-heavy/outlier-heavy overlap.
"""
from __future__ import annotations

import json
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
STACK_JSON = OUT_DIR / "v28_soft_frontier_midprice_boundary_exit_stack_latest.json"
OUT_JSON = OUT_DIR / "v28_soft_frontier_midprice_boundary_exit_stack_stress_latest.json"
OUT_MD = OUT_DIR / "v28_soft_frontier_midprice_boundary_exit_stack_stress_latest.md"

MAX_RECONSTRUCTED_SHARE = 0.35
MIN_JOINED_EXIT_ROWS = 30
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


def as_float(value: Any) -> float | None:
    if value is None or value == "":
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def full_loss_cushion(net_cents: float) -> int:
    return int(max(0.0, net_cents) // 100.0)


def stress_variant(variant: dict[str, Any]) -> dict[str, Any]:
    joined = variant.get("joined_rows") if isinstance(variant.get("joined_rows"), list) else []
    post_stack_joined = variant.get("post_stack_joined_rows") if isinstance(variant.get("post_stack_joined_rows"), list) else []
    weighted_values = [as_float(row.get("weighted_exit_candidate_cents")) or 0.0 for row in joined if isinstance(row, dict)]
    weighted_delta_values = [as_float(row.get("weighted_exit_delta_cents")) or 0.0 for row in joined if isinstance(row, dict)]
    net = sum(weighted_values)
    delta = sum(weighted_delta_values)
    top_win = max(weighted_values, default=0.0)
    worst_loss = min(weighted_values, default=0.0)
    source_counts: Counter[str] = Counter()
    source_net: defaultdict[str, float] = defaultdict(float)
    exit_reason_counts: Counter[str] = Counter()
    exit_reason_net: defaultdict[str, float] = defaultdict(float)
    suppressed_counts: Counter[str] = Counter()
    boundary_net = 0.0
    boundary_rows = 0
    for row in joined:
        if not isinstance(row, dict):
            continue
        source = str(row.get("source") or "unknown")
        value = as_float(row.get("weighted_exit_candidate_cents")) or 0.0
        reason = str(row.get("exit_reason") or "held_to_settlement_no_exit")
        suppressed = "suppressed" if bool(row.get("suppressed")) else "not_suppressed"
        source_counts[source] += 1
        source_net[source] += value
        exit_reason_counts[reason] += 1
        exit_reason_net[reason] += value
        suppressed_counts[suppressed] += 1
        if bool(row.get("midprice_boundary_band")):
            boundary_rows += 1
            boundary_net += value

    reconstructed_rows = len(joined) - int(source_counts.get("approved_entry") or 0)
    reconstructed_share = reconstructed_rows / len(joined) if joined else None
    blockers = list(variant.get("blockers") or [])
    stress_blockers: list[str] = []
    if len(joined) < MIN_JOINED_EXIT_ROWS:
        stress_blockers.append("joined_exit_rows_lt_30")
    if reconstructed_share is not None and reconstructed_share > MAX_RECONSTRUCTED_SHARE:
        stress_blockers.append("joined_reconstructed_share_gt_35pct")
    if full_loss_cushion(net) < MIN_FULL_LOSS_CUSHION:
        stress_blockers.append("joined_full_loss_cushion_lt_3")
    if top_win > 0 and net - top_win <= 0:
        stress_blockers.append("top_win_dependency")
    return {
        "candidate": variant.get("candidate"),
        "lane": variant.get("lane"),
        "policy": variant.get("policy"),
        "exit_source": variant.get("exit_source"),
        "strict_forward": variant.get("strict_forward"),
        "entry_summary": variant.get("entry_summary") or {},
        "joined_exit_rows": len(joined),
        "post_stack_joined_exit_rows": len(post_stack_joined),
        "weighted_joined_exit_net_cents": net,
        "weighted_joined_exit_delta_cents": delta,
        "post_stack_weighted_exit_net_cents": variant.get("post_stack_weighted_exit_candidate_cents"),
        "post_stack_weighted_exit_delta_cents": variant.get("post_stack_weighted_exit_delta_cents"),
        "weighted_exit_wins": sum(1 for value in weighted_values if value >= 0.0),
        "weighted_exit_losses": sum(1 for value in weighted_values if value < 0.0),
        "top_weighted_win_cents": top_win,
        "worst_weighted_loss_cents": worst_loss,
        "net_without_top_win_cents": net - top_win,
        "full_loss_cushion_estimate": full_loss_cushion(net),
        "joined_reconstructed_share": reconstructed_share,
        "joined_source_counts": dict(source_counts),
        "joined_source_net_cents": dict(source_net),
        "exit_reason_counts": dict(exit_reason_counts),
        "exit_reason_net_cents": dict(exit_reason_net),
        "suppressed_counts": dict(suppressed_counts),
        "midprice_boundary_joined_rows": boundary_rows,
        "midprice_boundary_weighted_exit_net_cents": boundary_net,
        "candidate_blockers": blockers,
        "stress_blockers": stress_blockers,
    }


def build_report() -> dict[str, Any]:
    stack = load_json(STACK_JSON)
    rows = [stress_variant(row) for row in stack.get("variants") or [] if isinstance(row, dict)]
    rows.sort(
        key=lambda row: (
            len(row.get("stress_blockers") or []),
            len(row.get("candidate_blockers") or []),
            -float(row.get("weighted_joined_exit_net_cents") or -999999.0),
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
        "Stress audit only; this does not make the stack promotable.",
        "A strong overlap row still needs strict combo-forward rows, clean source share, and outlier robustness.",
    ]
    if rows:
        best = rows[0]
        notes.append(
            f"Best stress row {best.get('candidate')} has {best.get('joined_exit_rows')} joined exits, "
            f"W/L {best.get('weighted_exit_wins')}/{best.get('weighted_exit_losses')}, net "
            f"{best.get('weighted_joined_exit_net_cents')}c, delta "
            f"{best.get('weighted_joined_exit_delta_cents')}c, net without top win "
            f"{best.get('net_without_top_win_cents')}c, post-stack joined exits "
            f"{best.get('post_stack_joined_exit_rows')}, joined reconstructed share "
            f"{best.get('joined_reconstructed_share')}, stress blockers {best.get('stress_blockers')}, "
            f"candidate blockers {best.get('candidate_blockers')}."
        )
    strict = [row for row in rows if row.get("strict_forward")]
    if strict:
        top_strict = strict[0]
        notes.append(
            f"Best strict row {top_strict.get('candidate')} has {top_strict.get('joined_exit_rows')} diagnostic joined exits, "
            f"{top_strict.get('post_stack_joined_exit_rows')} post-stack joined exits, and "
            f"{top_strict.get('weighted_joined_exit_net_cents')}c diagnostic net; blockers "
            f"{top_strict.get('candidate_blockers') + top_strict.get('stress_blockers')}."
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
        "# v28 Soft-Frontier Mid-Price Boundary Exit-Stack Stress",
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
        "## Rows",
        "",
        "| rank | candidate | strict | joined | post-stack joined | W/L | net c | post-stack net | delta c | post-stack delta | net ex top | recon | cushion | source net | exit reason net | stress blockers | candidate blockers |",
        "|---:|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|---|---|---|",
    ])
    for idx, row in enumerate((report.get("rows") or [])[:30], start=1):
        lines.append(
            f"| {idx} | `{row.get('candidate')}` | {row.get('strict_forward')} | "
            f"{row.get('joined_exit_rows')} | {row.get('post_stack_joined_exit_rows')} | "
            f"{row.get('weighted_exit_wins')}/{row.get('weighted_exit_losses')} | "
            f"{fmt(row.get('weighted_joined_exit_net_cents'))} | {fmt(row.get('post_stack_weighted_exit_net_cents'))} | "
            f"{fmt(row.get('weighted_joined_exit_delta_cents'))} | {fmt(row.get('post_stack_weighted_exit_delta_cents'))} | "
            f"{fmt(row.get('net_without_top_win_cents'))} | {fmt(row.get('joined_reconstructed_share'))} | "
            f"{row.get('full_loss_cushion_estimate')} | {row.get('joined_source_net_cents')} | "
            f"{row.get('exit_reason_net_cents')} | {', '.join(row.get('stress_blockers') or []) or 'none'} | "
            f"{', '.join(row.get('candidate_blockers') or []) or 'none'} |"
        )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    report = build_report()
    write_md(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
