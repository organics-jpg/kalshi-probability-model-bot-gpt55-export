"""Source dilution runway for the v28 hybrid/boundary entry stack.

Research-only; no live bot changes or orders.

The combined stack is broad and profitable in diagnostic windows, but the
candidate rows are still too reconstructed-heavy. This report estimates how
much future clean approved-entry evidence is needed to dilute reconstructed
share below the promotion gate while preserving positive PnL.
"""
from __future__ import annotations

import json
import math
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
STACK_JSON = OUT_DIR / "v28_hybrid_boundary_entry_stack_latest.json"
FRONTIER_JSON = OUT_DIR / "v28_hybrid_boundary_source_frontier_latest.json"
OUT_JSON = OUT_DIR / "v28_hybrid_boundary_source_dilution_runway_latest.json"
OUT_MD = OUT_DIR / "v28_hybrid_boundary_source_dilution_runway_latest.md"

MIN_SETTLED = 30
COVERAGE_FLOOR = 75.0
MAX_RECONSTRUCTED_SHARE = 0.35
MIN_FULL_LOSS_CUSHION_CENTS = 300.0


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


def find_window(payload: dict[str, Any], name: str) -> dict[str, Any]:
    for window in payload.get("windows") or []:
        if isinstance(window, dict) and window.get("window") == name:
            return window
    return {}


def summary(row: dict[str, Any]) -> dict[str, Any]:
    value = row.get("candidate_summary")
    return value if isinstance(value, dict) else {}


def source_counts(row: dict[str, Any]) -> dict[str, int]:
    counts = row.get("source_counts")
    if not isinstance(counts, dict):
        counts = (row.get("integrity_preview") or {}).get("candidate_source_counts")
    if not isinstance(counts, dict):
        return {}
    return {str(key): int(value or 0) for key, value in counts.items()}


def selected_count(row: dict[str, Any]) -> int:
    s = summary(row)
    return int(as_float(s.get("settled")) or as_float(s.get("entries")) or 0)


def entry_count(row: dict[str, Any]) -> int:
    s = summary(row)
    return int(as_float(s.get("entries")) or selected_count(row))


def denominator_for_window(window: dict[str, Any], row: dict[str, Any]) -> int:
    denom = int(as_float(window.get("forward_denominator")) or 0)
    if denom > 0:
        return denom
    coverage = as_float(summary(row).get("coverage_pct"))
    selected = selected_count(row)
    if coverage and coverage > 0:
        return int(round(selected / (coverage / 100.0)))
    return selected


def recon_parts(row: dict[str, Any]) -> tuple[int, int, int]:
    counts = source_counts(row)
    approved = int(counts.get("approved_entry") or 0)
    total = sum(counts.values()) or selected_count(row)
    reconstructed = max(0, total - approved)
    return total, approved, reconstructed


def approved_needed_for_recon(total: int, reconstructed: int) -> int:
    if total <= 0:
        return 0
    current = reconstructed / total
    if current <= MAX_RECONSTRUCTED_SHARE:
        return 0
    return int(math.ceil((reconstructed / MAX_RECONSTRUCTED_SHARE) - total))


def compact(row: dict[str, Any], window: dict[str, Any]) -> dict[str, Any]:
    s = summary(row)
    net = as_float(s.get("net_cents")) or 0.0
    settled = selected_count(row)
    entries = entry_count(row)
    denominator = denominator_for_window(window, row)
    total, approved, reconstructed = recon_parts(row)
    needed_recon = approved_needed_for_recon(total, reconstructed)
    needed_sample = max(0, MIN_SETTLED - settled)
    needed_gate = max(needed_recon, needed_sample)
    coverage_after_gate = None
    if denominator + needed_gate > 0:
        coverage_after_gate = 100.0 * (entries + needed_gate) / (denominator + needed_gate)
    max_full_losses_positive = int(max(0.0, net) // 100.0)
    max_full_losses_cushion3 = int(max(0.0, net - MIN_FULL_LOSS_CUSHION_CENTS) // 100.0)
    avg_needed_positive = None
    avg_needed_cushion3 = None
    if needed_gate > 0:
        avg_needed_positive = ((0.01 - net) / needed_gate)
        avg_needed_cushion3 = ((MIN_FULL_LOSS_CUSHION_CENTS - net) / needed_gate)
    return {
        "candidate": row.get("candidate"),
        "settled": settled,
        "entries": entries,
        "denominator": denominator,
        "coverage_pct": s.get("coverage_pct"),
        "net_cents": s.get("net_cents"),
        "wins": s.get("wins"),
        "losses": s.get("losses"),
        "approved_entry": approved,
        "reconstructed": reconstructed,
        "reconstructed_share": None if total <= 0 else reconstructed / total,
        "approved_needed_for_recon35": needed_recon,
        "future_selected_needed_for_30": needed_sample,
        "future_approved_selected_needed_for_gate": needed_gate,
        "coverage_after_gate_if_all_selected": coverage_after_gate,
        "max_full_losses_while_positive": max_full_losses_positive,
        "max_full_losses_while_cushion3": max_full_losses_cushion3,
        "avg_future_net_needed_positive_cents": avg_needed_positive,
        "avg_future_net_needed_cushion3_cents": avg_needed_cushion3,
        "blockers": row.get("promotion_blockers") or row.get("blockers") or [],
    }


def broad_positive(row: dict[str, Any]) -> bool:
    s = summary(row)
    settled = int(as_float(s.get("settled")) or 0)
    coverage = as_float(s.get("coverage_pct"))
    net = as_float(s.get("net_cents"))
    return settled >= MIN_SETTLED and coverage is not None and coverage >= COVERAGE_FLOOR and net is not None and net > 0


def top_rows(window: dict[str, Any], limit: int = 8) -> list[dict[str, Any]]:
    variants = window.get("variants") if isinstance(window.get("variants"), list) else []
    broad = [row for row in variants if broad_positive(row)]
    rows = broad or variants
    return sorted(
        rows,
        key=lambda row: (
            -(as_float(summary(row).get("net_cents")) or -999999.0),
            as_float((row.get("integrity_preview") or {}).get("reconstructed_share")) or 1.0,
        ),
    )[:limit]


def build_report() -> dict[str, Any]:
    stack = load_json(STACK_JSON)
    frontier = load_json(FRONTIER_JSON)
    diagnostic = find_window(stack, "diagnostic_existing_target_window")
    post = find_window(stack, "post_stack_freeze_window")
    frontier_diag = find_window(frontier, "diagnostic_existing_target_window")
    frontier_post = find_window(frontier, "post_stack_freeze_window")
    report = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "purpose": "Estimate clean approved-entry evidence needed to dilute reconstructed share for the hybrid/boundary stack.",
        "stack_generated_at_utc": stack.get("generated_at_utc"),
        "stack_freeze_utc": (stack.get("state") or {}).get("freeze_ts_utc"),
        "requirements": {
            "min_settled": MIN_SETTLED,
            "coverage_floor": COVERAGE_FLOOR,
            "max_reconstructed_share": MAX_RECONSTRUCTED_SHARE,
            "min_full_loss_cushion_cents": MIN_FULL_LOSS_CUSHION_CENTS,
        },
        "diagnostic_top": [compact(row, diagnostic) for row in top_rows(diagnostic)],
        "post_freeze_top": [compact(row, post) for row in top_rows(post)],
        "frontier_diagnostic_top": [compact(row, frontier_diag) for row in top_rows(frontier_diag, 5)],
        "frontier_post_freeze_top": [compact(row, frontier_post) for row in top_rows(frontier_post, 5)],
    }
    report["interpretation"] = interpretation(report)
    return report


def interpretation(report: dict[str, Any]) -> list[str]:
    notes: list[str] = []
    diag = (report.get("diagnostic_top") or [{}])[0]
    post = (report.get("post_freeze_top") or [{}])[0]
    frontier = (report.get("frontier_diagnostic_top") or [{}])[0]
    if diag:
        notes.append(
            f"Best diagnostic stack needs {diag.get('approved_needed_for_recon35')} additional clean approved selected rows to dilute reconstructed share to <=35%; it can absorb {diag.get('max_full_losses_while_positive')} full-loss rows before net turns non-positive."
        )
    if frontier:
        notes.append(
            f"Even the diagnostic source frontier needs {frontier.get('approved_needed_for_recon35')} clean approved selected rows unless coverage is allowed to fall below target."
        )
    if post:
        notes.append(
            f"Post-freeze stack evidence is still tiny: settled {post.get('settled')} with {post.get('entries')} entries of denominator {post.get('denominator')}, reconstructed share {post.get('reconstructed_share')}; it needs {post.get('future_approved_selected_needed_for_gate')} future clean approved settled rows to satisfy the sample/source gate together."
        )
    notes.append("This is a runway estimate, not promotion evidence; future rows must actually settle and stay profitable.")
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
        "# v28 Hybrid/Boundary Source Dilution Runway",
        "",
        "Research-only; no live bot changes or orders.",
        "",
        f"- Generated UTC: `{report.get('generated_at_utc')}`",
        f"- Stack freeze UTC: `{report.get('stack_freeze_utc')}`",
        "",
        "## Interpretation",
        "",
    ]
    for note in report.get("interpretation") or []:
        lines.append(f"- {note}")
    for title, key in [
        ("Diagnostic Stack Runway", "diagnostic_top"),
        ("Post-Freeze Stack Runway", "post_freeze_top"),
        ("Diagnostic Frontier Runway", "frontier_diagnostic_top"),
        ("Post-Freeze Frontier Runway", "frontier_post_freeze_top"),
    ]:
        lines.extend(
            [
                "",
                f"## {title}",
                "",
                "| rank | candidate | settled/entries/den | cov | net c | W/L | recon share | approved | recon | clean rows to <=35% | future rows to gate | max full losses positive | avg c needed for cushion3 | blockers |",
                "|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|",
            ]
        )
        for idx, row in enumerate(report.get(key) or [], start=1):
            lines.append(
                f"| {idx} | {row.get('settled')}/{row.get('entries')}/{row.get('denominator')} | "
                f"{fmt(row.get('coverage_pct'))} | {fmt(row.get('net_cents'))} | {row.get('wins')}/{row.get('losses')} | "
                f"{fmt(row.get('reconstructed_share'))} | {row.get('approved_entry')} | {row.get('reconstructed')} | "
                f"{row.get('approved_needed_for_recon35')} | {row.get('future_approved_selected_needed_for_gate')} | "
                f"{row.get('max_full_losses_while_positive')} | {fmt(row.get('avg_future_net_needed_cushion3_cents'))} | "
                f"{', '.join(row.get('blockers') or []) or 'none'} |"
            )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    report = build_report()
    write_md(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
