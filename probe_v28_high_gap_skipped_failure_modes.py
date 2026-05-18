"""Failure-mode readout for high raw/book-gap rows skipped by state valves.

Research-only; no live bot changes or orders.

This probe intentionally works from the saved full-surface adapter report. It
does not rebuild surfaces or invent a new candidate. Its purpose is to turn the
approved-entry valve adapter's skipped rows into explicit failure-mode evidence
for the v28 research ledger.
"""
from __future__ import annotations

import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
FULL_SURFACE_JSON = OUT_DIR / "v28_approved_entry_state_valve_full_surface_latest.json"
OUT_JSON = OUT_DIR / "v28_high_gap_skipped_failure_modes_latest.json"
OUT_MD = OUT_DIR / "v28_high_gap_skipped_failure_modes_latest.md"


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


def fmt(value: Any) -> str:
    if value is None:
        return "None"
    if isinstance(value, float):
        return f"{value:.6f}"
    return str(value)


def row_key(row: dict[str, Any]) -> tuple[str, str, str, str]:
    return (
        str(row.get("market") or ""),
        str(row.get("side") or ""),
        str(row.get("source") or ""),
        str(row.get("ts_wall") or ""),
    )


def unique_skipped_rows(payload: dict[str, Any]) -> list[dict[str, Any]]:
    seen: set[tuple[str, str, str, str]] = set()
    rows: list[dict[str, Any]] = []
    for surface_row in payload.get("rows") or []:
        for skipped in surface_row.get("skipped_rows") or []:
            key = row_key(skipped)
            if key in seen:
                continue
            seen.add(key)
            enriched = dict(skipped)
            enriched["from_valve"] = surface_row.get("valve")
            enriched["from_surface"] = surface_row.get("surface")
            enriched["from_policy"] = surface_row.get("policy")
            rows.append(enriched)
    rows.sort(key=lambda row: str(row.get("ts_wall") or ""))
    return rows


def gap_bucket(value: float | None) -> str:
    if value is None:
        return "gap_unknown"
    if value < 0.30:
        return "gap_lt_30pp"
    if value < 0.35:
        return "gap_30_35pp"
    if value < 0.40:
        return "gap_35_40pp"
    return "gap_ge_40pp"


def ask_bucket(value: float | None) -> str:
    if value is None:
        return "ask_unknown"
    if value < 0.20:
        return "ask_lt_20c"
    if value < 0.30:
        return "ask_20_30c"
    if value < 0.40:
        return "ask_30_40c"
    return "ask_ge_40c"


def classify_row(row: dict[str, Any]) -> list[str]:
    modes: list[str] = []
    source = str(row.get("source") or "unknown")
    if source != "approved_entry":
        modes.append("source_quality_error")
    gap = as_float(row.get("raw_book_gap"))
    if gap is not None and gap >= 0.30:
        modes.append("fv_overconfidence_or_book_dislocation")
    if bool(row.get("side_won")):
        modes.append("fragility_error_hard_cutoff_misses_right_tail")
    else:
        modes.append("fv_error_side_lost_despite_large_edge")
    entry_index = as_float(row.get("market_side_entry_index"))
    if entry_index is not None and entry_index > 0:
        modes.append("entry_timing_same_side_reentry")
    else:
        modes.append("entry_timing_first_touch_not_reentry")
    return modes


def summarize_rows(rows: list[dict[str, Any]]) -> dict[str, Any]:
    nets = [as_float(row.get("net_cents")) or 0.0 for row in rows]
    wins = [row for row in rows if bool(row.get("side_won"))]
    losses = [row for row in rows if not bool(row.get("side_won"))]
    win_net = sum(as_float(row.get("net_cents")) or 0.0 for row in wins)
    loss_net = sum(as_float(row.get("net_cents")) or 0.0 for row in losses)
    modes: Counter[str] = Counter()
    gap_buckets: Counter[str] = Counter()
    ask_buckets: Counter[str] = Counter()
    by_side: Counter[str] = Counter()
    by_source: Counter[str] = Counter()
    by_surface: Counter[str] = Counter()
    for row in rows:
        modes.update(classify_row(row))
        gap_buckets.update([gap_bucket(as_float(row.get("raw_book_gap")))])
        ask_buckets.update([ask_bucket(as_float(row.get("ask_prob")))])
        by_side.update([str(row.get("side") or "unknown")])
        by_source.update([str(row.get("source") or "unknown")])
        by_surface.update([str(row.get("from_surface") or "unknown")])
    return {
        "rows": len(rows),
        "wins": len(wins),
        "losses": len(losses),
        "net_cents": sum(nets),
        "win_net_cents": win_net,
        "loss_net_cents": loss_net,
        "avg_net_cents": None if not rows else sum(nets) / len(rows),
        "loss_avg_net_cents": None if not losses else loss_net / len(losses),
        "mode_counts": dict(modes),
        "gap_buckets": dict(gap_buckets),
        "ask_buckets": dict(ask_buckets),
        "side_counts": dict(by_side),
        "source_counts": dict(by_source),
        "surface_counts": dict(by_surface),
    }


def compact_row(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "market": row.get("market"),
        "side": row.get("side"),
        "side_won": row.get("side_won"),
        "source": row.get("source"),
        "net_cents": as_float(row.get("net_cents")),
        "p_side": as_float(row.get("p_side")),
        "ask_prob": as_float(row.get("ask_prob")),
        "raw_book_gap": as_float(row.get("raw_book_gap")),
        "market_side_entry_index": row.get("market_side_entry_index"),
        "ts_wall": row.get("ts_wall"),
        "failure_modes": classify_row(row),
    }


def build_report() -> dict[str, Any]:
    payload = load_json(FULL_SURFACE_JSON)
    rows = unique_skipped_rows(payload)
    summary = summarize_rows(rows)
    observations = []
    if rows:
        observations.extend([
            (
                "The saved full-surface valve adapter has only "
                f"{len(rows)} unique skipped high-gap rows, so this is mechanism evidence, not a candidate score."
            ),
            (
                f"Skipping them would have improved the broad adapter by {-summary['net_cents']}c because "
                f"{summary['losses']} losers summed to {summary['loss_net_cents']}c while "
                f"{summary['wins']} winner summed to {summary['win_net_cents']}c."
            ),
            (
                "All skipped rows are rejected-actionable, so the dominant failure family remains source-quality plus "
                "FV/book dislocation, not approved-entry live behavior."
            ),
            (
                "The single +141c skipped winner is the important fragility warning: a hard high-gap cutoff can remove "
                "large right-tail wins even when the small sample is net helpful."
            ),
        ])
    else:
        observations.append("No skipped rows were present in the full-surface adapter report.")
    return {
        "input_report": str(FULL_SURFACE_JSON),
        "summary": summary,
        "rows": [compact_row(row) for row in rows],
        "observability_limits": [
            "Uses saved adapter skipped rows only; it does not rebuild selected/base rows.",
            "No exit-path fields are present here, so exit-policy error cannot be directly scored.",
            "No live-readiness or promotion gate is evaluated by this forensic probe.",
        ],
        "interpretation": observations,
        "next_research_implication": (
            "Treat high raw/book gap on rejected-actionable rows as a continuous confidence/shrinkage input, "
            "not as a promotable hard veto. A useful next candidate would need to test a soft penalty across the "
            "full surface with strict forward freeze, source-share control, and explicit tail-winner cost accounting."
        ),
    }


def write_md(report: dict[str, Any]) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8")
    summary = report.get("summary") or {}
    lines = [
        "# v28 High-Gap Skipped Failure Modes",
        "",
        "Research-only forensic readout; no live bot changes or orders.",
        "",
        f"- Input report: `{report.get('input_report')}`",
        f"- Unique skipped rows: `{summary.get('rows')}`",
        f"- W/L: `{summary.get('wins')}/{summary.get('losses')}`",
        f"- Net of skipped rows: `{fmt(summary.get('net_cents'))}c`",
        f"- Loss net / winner net: `{fmt(summary.get('loss_net_cents'))}c` / `{fmt(summary.get('win_net_cents'))}c`",
        "",
        "## Interpretation",
        "",
    ]
    for note in report.get("interpretation") or []:
        lines.append(f"- {note}")
    lines.extend([
        "",
        "## Failure Buckets",
        "",
        f"- Mode counts: `{summary.get('mode_counts')}`",
        f"- Gap buckets: `{summary.get('gap_buckets')}`",
        f"- Ask buckets: `{summary.get('ask_buckets')}`",
        f"- Source counts: `{summary.get('source_counts')}`",
        f"- Side counts: `{summary.get('side_counts')}`",
        "",
        "## Rows",
        "",
        "| market | side | source | won | net c | p_side | ask | gap | failure modes |",
        "|---|---|---|---:|---:|---:|---:|---:|---|",
    ])
    for row in report.get("rows") or []:
        lines.append(
            f"| `{row.get('market')}` | `{row.get('side')}` | `{row.get('source')}` | "
            f"{row.get('side_won')} | {fmt(row.get('net_cents'))} | {fmt(row.get('p_side'))} | "
            f"{fmt(row.get('ask_prob'))} | {fmt(row.get('raw_book_gap'))} | "
            f"{', '.join(row.get('failure_modes') or [])} |"
        )
    lines.extend([
        "",
        "## Limits",
        "",
    ])
    for note in report.get("observability_limits") or []:
        lines.append(f"- {note}")
    lines.extend([
        "",
        "## Next Research Implication",
        "",
        report.get("next_research_implication") or "",
    ])
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    report = build_report()
    write_md(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
