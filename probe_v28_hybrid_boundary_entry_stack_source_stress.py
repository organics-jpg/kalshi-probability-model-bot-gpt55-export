"""Source stress audit for the v28 hybrid/boundary entry stack.

Research-only; no live bot changes or orders.

The combined stack can be broad and positive, but its selected rows are often
reconstructed/rejected-actionable. This report measures selected-row source
composition, source-split PnL, and dilution/cushion runway for the stack's
current best lanes. It does not create a new candidate.
"""
from __future__ import annotations

import json
import math
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
STACK_JSON = OUT_DIR / "v28_hybrid_boundary_entry_stack_latest.json"
OUT_JSON = OUT_DIR / "v28_hybrid_boundary_entry_stack_source_stress_latest.json"
OUT_MD = OUT_DIR / "v28_hybrid_boundary_entry_stack_source_stress_latest.md"

MIN_SETTLED = 30
MAX_RECONSTRUCTED_SHARE = 0.35
MIN_FULL_LOSS_CUSHION_CENTS = 300.0
FULL_LOSS_CENTS = 100.0


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


def row_source(row: dict[str, Any]) -> str:
    return str(row.get("source") or "unknown")


def group_summary(rows: list[dict[str, Any]]) -> dict[str, Any]:
    by_source: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        by_source[row_source(row)].append(row)
    source_summary = {}
    for source, group in sorted(by_source.items()):
        net_values = [as_float(row.get("net_cents")) or 0.0 for row in group]
        source_summary[source] = {
            "rows": len(group),
            "wins": sum(1 for row in group if row.get("side_won") is True),
            "losses": sum(1 for row in group if row.get("side_won") is False),
            "net_cents": sum(net_values),
            "avg_net_cents": None if not group else sum(net_values) / len(group),
        }
    return source_summary


def approved_needed_for_recon(total: int, reconstructed: int) -> int:
    if total <= 0:
        return 0
    if reconstructed / total <= MAX_RECONSTRUCTED_SHARE:
        return 0
    return int(math.ceil((reconstructed / MAX_RECONSTRUCTED_SHARE) - total))


def summarize_variant(window: dict[str, Any], variant: dict[str, Any]) -> dict[str, Any]:
    summary = variant.get("candidate_summary") if isinstance(variant.get("candidate_summary"), dict) else {}
    rows = variant.get("candidate_rows") if isinstance(variant.get("candidate_rows"), list) else []
    rows = [row for row in rows if isinstance(row, dict)]
    source_counts = Counter(row_source(row) for row in rows)
    total = len(rows)
    approved = int(source_counts.get("approved_entry") or 0)
    reconstructed = max(0, total - approved)
    net_cents = as_float(summary.get("net_cents")) or 0.0
    settled = int(as_float(summary.get("settled")) or 0)
    needed_source = approved_needed_for_recon(total, reconstructed)
    needed_sample = max(0, MIN_SETTLED - settled)
    needed_cushion_cents = max(0.0, MIN_FULL_LOSS_CUSHION_CENTS - net_cents)
    avg_net = as_float(summary.get("avg_net_cents"))
    rows_for_cushion = None
    if needed_cushion_cents <= 0:
        rows_for_cushion = 0
    elif avg_net is not None and avg_net > 0.0:
        rows_for_cushion = int(math.ceil(needed_cushion_cents / avg_net))
    return {
        "window": window.get("window"),
        "candidate": variant.get("candidate"),
        "summary": summary,
        "source_counts": dict(source_counts),
        "source_summary": group_summary(rows),
        "reconstructed_share": None if total <= 0 else reconstructed / total,
        "approved_rows": approved,
        "reconstructed_rows": reconstructed,
        "clean_rows_needed_for_source_gate": needed_source,
        "settled_rows_needed_for_sample_gate": needed_sample,
        "net_cents_needed_for_cushion3": needed_cushion_cents,
        "rows_needed_for_cushion3_at_current_avg": rows_for_cushion,
        "max_full_losses_positive": int(max(0.0, net_cents) // FULL_LOSS_CENTS),
        "max_full_losses_with_cushion3": int(max(0.0, net_cents - MIN_FULL_LOSS_CUSHION_CENTS) // FULL_LOSS_CENTS),
        "stress_blockers": stress_blockers(total, reconstructed, settled, net_cents),
    }


def stress_blockers(total: int, reconstructed: int, settled: int, net_cents: float) -> list[str]:
    blockers: list[str] = []
    if settled < MIN_SETTLED:
        blockers.append("settled_lt_30")
    if total <= 0 or reconstructed / total > MAX_RECONSTRUCTED_SHARE:
        blockers.append("reconstructed_share_gt_35pct")
    if net_cents <= 0.0:
        blockers.append("net_not_positive")
    if net_cents < MIN_FULL_LOSS_CUSHION_CENTS:
        blockers.append("full_loss_cushion_lt_3")
    return blockers


def best_variant(window: dict[str, Any]) -> dict[str, Any]:
    variants = window.get("variants") if isinstance(window.get("variants"), list) else []
    return variants[0] if variants and isinstance(variants[0], dict) else {}


def build_report() -> dict[str, Any]:
    stack = load_json(STACK_JSON)
    lanes = []
    for window in stack.get("windows") or []:
        if not isinstance(window, dict):
            continue
        best = best_variant(window)
        if best:
            lanes.append(summarize_variant(window, best))
    report = {
        "generated_at_utc": utc_now_iso(),
        "stack_generated_at_utc": stack.get("generated_at_utc"),
        "stack_freeze_ts_utc": (stack.get("state") or {}).get("freeze_ts_utc"),
        "requirements": {
            "min_settled": MIN_SETTLED,
            "max_reconstructed_share": MAX_RECONSTRUCTED_SHARE,
            "min_full_loss_cushion_cents": MIN_FULL_LOSS_CUSHION_CENTS,
        },
        "lanes": lanes,
    }
    report["interpretation"] = interpretation(report)
    return report


def interpretation(report: dict[str, Any]) -> list[str]:
    notes = [
        "This is the formal source-stress audit for the combined stack; it is not promotion evidence by itself.",
    ]
    for lane in report.get("lanes") or []:
        summary = lane.get("summary") or {}
        notes.append(
            f"{lane.get('window')}: {lane.get('candidate')} has {summary.get('settled')} settled, "
            f"coverage {summary.get('coverage_pct')}%, net {summary.get('net_cents')}c, reconstructed share "
            f"{lane.get('reconstructed_share')}; needs {lane.get('clean_rows_needed_for_source_gate')} clean rows for source, "
            f"{lane.get('settled_rows_needed_for_sample_gate')} rows for sample, and "
            f"{lane.get('net_cents_needed_for_cushion3')}c for cushion; blockers {lane.get('stress_blockers')}."
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
        "# v28 Hybrid/Boundary Entry Stack Source Stress",
        "",
        "Research-only; no live bot changes or orders.",
        "",
        f"- Generated UTC: `{report.get('generated_at_utc')}`",
        f"- Stack generated UTC: `{report.get('stack_generated_at_utc')}`",
        f"- Stack freeze UTC: `{report.get('stack_freeze_ts_utc')}`",
        "",
        "## Interpretation",
        "",
    ]
    for note in report.get("interpretation") or []:
        lines.append(f"- {note}")
    lines.extend(
        [
            "",
            "## Lanes",
            "",
            "| window | candidate | settled | coverage | net c | W/L | recon share | approved/recon | source rows needed | sample rows needed | cushion c needed | max full losses positive | blockers |",
            "|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|",
        ]
    )
    for lane in report.get("lanes") or []:
        summary = lane.get("summary") or {}
        lines.append(
            f"| {lane.get('window')} | {lane.get('candidate')} | {summary.get('settled')} | "
            f"{fmt(summary.get('coverage_pct'))} | {fmt(summary.get('net_cents'))} | "
            f"{summary.get('wins')}/{summary.get('losses')} | {fmt(lane.get('reconstructed_share'))} | "
            f"{lane.get('approved_rows')}/{lane.get('reconstructed_rows')} | "
            f"{lane.get('clean_rows_needed_for_source_gate')} | {lane.get('settled_rows_needed_for_sample_gate')} | "
            f"{fmt(lane.get('net_cents_needed_for_cushion3'))} | {lane.get('max_full_losses_positive')} | "
            f"{', '.join(lane.get('stress_blockers') or []) or 'none'} |"
        )
    for lane in report.get("lanes") or []:
        lines.extend(["", f"## Source Split: {lane.get('window')}", ""])
        lines.extend(
            [
                "| source | rows | W/L | net c | avg c |",
                "|---|---:|---:|---:|---:|",
            ]
        )
        for source, source_summary in (lane.get("source_summary") or {}).items():
            lines.append(
                f"| {source} | {source_summary.get('rows')} | {source_summary.get('wins')}/{source_summary.get('losses')} | "
                f"{fmt(source_summary.get('net_cents'))} | {fmt(source_summary.get('avg_net_cents'))} |"
            )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    report = build_report()
    write_md(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
