"""Near-promotion watch for boundary-clock feature-gate post-freeze rows.

Research-only; no live bot changes or orders.

This is not a new threshold search. It tracks the already-frozen observable
feature-gate rows that are closest to broad-entry promotion, with explicit
pending-row and clean-row runway counts.
"""
from __future__ import annotations

import json
import math
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
FEATURE_JSON = OUT_DIR / "v28_boundary_clock_feature_gate_candidate_latest.json"
OUT_JSON = OUT_DIR / "v28_feature_gate_near_promotion_watch_latest.json"
OUT_MD = OUT_DIR / "v28_feature_gate_near_promotion_watch_latest.md"

TARGET_LANES = {"post_feature_freeze_entry", "post_feature_freeze_bridge"}
TARGET_RULES = {
    "raw03_recross70_abs075",
    "raw05_recross60_abs085",
    "raw05_recross60_abs085_ask65",
}

MIN_SETTLED = 30
MIN_COVERAGE = 75.0
MAX_RECONSTRUCTED_SHARE = 0.35
MIN_CUSHION_CENTS = 300.0


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


def rule_name(candidate: str) -> str:
    for prefix in ("post_feature_freeze_entry_", "post_feature_freeze_bridge_"):
        if candidate.startswith(prefix):
            return candidate[len(prefix):]
    return candidate


def source(row: dict[str, Any]) -> str:
    return str(row.get("source") or "unknown")


def is_approved(row: dict[str, Any]) -> bool:
    return source(row) == "approved_entry"


def is_settled(row: dict[str, Any]) -> bool:
    return row.get("side_won") is not None


def net(row: dict[str, Any]) -> float:
    return float(as_float(row.get("net_cents")) or 0.0)


def clean_rows_needed(reconstructed: int, selected: int) -> int:
    for rows in range(0, 500):
        if selected + rows > 0 and reconstructed / (selected + rows) <= MAX_RECONSTRUCTED_SHARE:
            return rows
    return 500


def classify_loss(row: dict[str, Any]) -> list[str]:
    tags: list[str] = []
    ask = as_float(row.get("ask_prob"))
    abs_d = as_float(row.get("abs_d_sigma"))
    recross = as_float(row.get("recross_hazard_score"))
    edge = as_float(row.get("raw_edge"))
    if not is_approved(row):
        tags.append("source_quality")
    if ask is not None and ask < 0.35:
        tags.append("cheap_tail")
    elif ask is not None and ask < 0.50:
        tags.append("mid_cheap")
    if abs_d is not None and abs_d < 0.75:
        tags.append("near_boundary")
    if recross is not None and recross > 0.50:
        tags.append("recross_churn")
    if edge is not None and edge < 0.05:
        tags.append("thin_raw_edge")
    return tags or ["unclassified"]


def summarize_variant(lane: str, row: dict[str, Any], denominator: int | None) -> dict[str, Any]:
    candidate = str(row.get("candidate") or "")
    summary = row.get("candidate_summary") if isinstance(row.get("candidate_summary"), dict) else {}
    rows = [item for item in row.get("rows") or [] if isinstance(item, dict)]
    settled = [item for item in rows if is_settled(item)]
    pending = [item for item in rows if not is_settled(item)]
    source_counts = Counter(source(item) for item in rows)
    pending_source_counts = Counter(source(item) for item in pending)
    settled_source_counts = Counter(source(item) for item in settled)
    reconstructed = len(rows) - source_counts.get("approved_entry", 0)
    share = None if not rows else reconstructed / len(rows)
    net_cents = as_float(summary.get("net_cents")) or sum(net(item) for item in settled)
    coverage = as_float(summary.get("coverage_pct"))
    losses = [item for item in settled if net(item) < 0]
    loss_tags = Counter(tag for item in losses for tag in classify_loss(item))
    missing: list[str] = []
    if len(settled) < MIN_SETTLED:
        missing.append(f"settled+{MIN_SETTLED - len(settled)}")
    entries = int(as_float(summary.get("entries")) or len(rows))
    required_entries = None
    coverage_entries_needed = None
    if denominator:
        required_entries = math.ceil(MIN_COVERAGE * denominator / 100.0)
        coverage_entries_needed = max(0, required_entries - entries)
    if coverage is None or coverage < MIN_COVERAGE:
        gap = MIN_COVERAGE - (coverage or 0.0)
        missing.append(f"coverage+{gap:.1f}pp")
    if share is None:
        missing.append("source_unknown")
    elif share > MAX_RECONSTRUCTED_SHARE:
        missing.append(f"clean_rows+{clean_rows_needed(reconstructed, len(rows))}")
    if net_cents < MIN_CUSHION_CENTS:
        missing.append(f"cushion_cents+{MIN_CUSHION_CENTS - net_cents:.0f}")
    if net_cents <= 0:
        missing.append("positive_pnl")
    pending_approved = pending_source_counts.get("approved_entry", 0)
    clean_needed = None if share is None or share <= MAX_RECONSTRUCTED_SHARE else clean_rows_needed(reconstructed, len(rows))
    settled_needed = max(0, MIN_SETTLED - len(settled))
    cushion_needed = max(0.0, MIN_CUSHION_CENTS - net_cents)
    future_clean_rows_needed_for_all_gates = max(
        settled_needed,
        coverage_entries_needed or 0,
        clean_needed or 0,
        1 if cushion_needed > 0 else 0,
    )
    avg_future_net_needed_for_cushion3 = (
        cushion_needed / future_clean_rows_needed_for_all_gates
        if future_clean_rows_needed_for_all_gates > 0
        else 0.0
    )
    return {
        "lane": lane,
        "candidate": candidate,
        "rule": rule_name(candidate),
        "entries": entries,
        "future_denominator": denominator,
        "required_entries_for_75pct": required_entries,
        "coverage_entries_needed": coverage_entries_needed,
        "selected_rows": len(rows),
        "settled": len(settled),
        "pending": len(pending),
        "pending_approved": pending_approved,
        "pending_reconstructed_or_unknown": len(pending) - pending_approved,
        "wins": int(as_float(summary.get("wins")) or sum(1 for item in settled if net(item) > 0)),
        "losses": int(as_float(summary.get("losses")) or len(losses)),
        "coverage_pct": coverage,
        "net_cents": net_cents,
        "source_counts": dict(source_counts),
        "settled_source_counts": dict(settled_source_counts),
        "pending_source_counts": dict(pending_source_counts),
        "reconstructed_share": share,
        "full_loss_cushion": int(max(0.0, net_cents) // 100.0),
        "clean_rows_needed_for_source": clean_needed,
        "settled_rows_needed": settled_needed,
        "net_cents_needed_for_cushion3": cushion_needed,
        "future_clean_rows_needed_for_all_gates": future_clean_rows_needed_for_all_gates,
        "avg_future_net_needed_for_cushion3": avg_future_net_needed_for_cushion3,
        "loss_tag_counts": dict(loss_tags),
        "largest_losses": sorted(
            [
                {
                    "market": item.get("market"),
                    "source": source(item),
                    "side": item.get("side"),
                    "net_cents": net(item),
                    "ask_prob": item.get("ask_prob"),
                    "abs_d_sigma": item.get("abs_d_sigma"),
                    "recross_hazard_score": item.get("recross_hazard_score"),
                    "raw_edge": item.get("raw_edge"),
                    "tags": classify_loss(item),
                }
                for item in losses
            ],
            key=lambda item: item["net_cents"],
        )[:8],
        "missing_gates": missing,
        "live_ready": not missing,
    }


def build_report() -> dict[str, Any]:
    payload = load_json(FEATURE_JSON)
    rows: list[dict[str, Any]] = []
    for lane in payload.get("lanes") or []:
        if not isinstance(lane, dict) or lane.get("lane") not in TARGET_LANES:
            continue
        lane_name = str(lane.get("lane"))
        denominator = as_float(lane.get("future_denominator"))
        denominator_int = int(denominator) if denominator is not None else None
        for variant in lane.get("variants") or []:
            if not isinstance(variant, dict):
                continue
            if rule_name(str(variant.get("candidate") or "")) in TARGET_RULES:
                rows.append(summarize_variant(lane_name, variant, denominator_int))
    rows.sort(
        key=lambda row: (
            row.get("live_ready") is True,
            -(len(row.get("missing_gates") or [])),
            as_float(row.get("net_cents")) or -1e9,
        ),
        reverse=True,
    )
    best = rows[0] if rows else {}
    return {
        "generated_at_utc": utc_now_iso(),
        "source": str(FEATURE_JSON),
        "feature_gate_freeze_ts_utc": (payload.get("state") or {}).get("freeze_ts_utc"),
        "candidate_live_ready": any(bool(row.get("live_ready")) for row in rows),
        "best_candidate": best.get("candidate"),
        "best_missing_gates": best.get("missing_gates"),
        "rows": rows,
        "interpretation": [
            "This watch tracks already-frozen feature-gate rules only; it is not a new threshold search.",
            "Pending approved rows can close sample/source gaps, but promotion still requires settled PnL and full-loss cushion.",
            f"Best watched row {best.get('candidate')} has net {best.get('net_cents')}c, coverage {best.get('coverage_pct')}%, reconstructed share {best.get('reconstructed_share')}, and missing gates {best.get('missing_gates')}.",
        ],
    }


def fmt_pct(value: Any) -> str:
    number = as_float(value)
    if number is None:
        return "n/a"
    return f"{number * 100.0:.1f}%" if number <= 1.0 else f"{number:.1f}%"


def fmt_cents(value: Any) -> str:
    number = as_float(value)
    if number is None:
        return "n/a"
    return f"{number:.0f}c (${number / 100.0:.2f})"


def write_outputs(report: dict[str, Any]) -> None:
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8")
    lines = [
        "# v28 Feature-Gate Near-Promotion Watch",
        "",
        "Research-only watch. No live bot changes or orders.",
        "",
        f"- Generated UTC: `{report.get('generated_at_utc')}`",
        f"- Feature-gate freeze UTC: `{report.get('feature_gate_freeze_ts_utc')}`",
        f"- Any live-ready watched row: `{report.get('candidate_live_ready')}`",
        f"- Best candidate: `{report.get('best_candidate')}`",
        f"- Best missing gates: `{report.get('best_missing_gates')}`",
        "",
        "## Watched Rows",
        "",
        "| lane | candidate | settled | W/L | coverage | net | recon | cushion | rows needed | avg c/row | missing gates |",
        "|---|---|---:|---:|---:|---:|---:|---:|---|---:|---|",
    ]
    for row in report.get("rows") or []:
        lines.append(
            f"| `{row.get('lane')}` | `{row.get('candidate')}` | {row.get('settled')} | "
            f"{row.get('wins')}/{row.get('losses')} | {fmt_pct(row.get('coverage_pct'))} | "
            f"{fmt_cents(row.get('net_cents'))} | {fmt_pct(row.get('reconstructed_share'))} | {row.get('full_loss_cushion')} | "
            f"cov {row.get('coverage_entries_needed')}/settle {row.get('settled_rows_needed')}/clean {row.get('clean_rows_needed_for_source') or 0}/cushion {fmt_cents(row.get('net_cents_needed_for_cushion3'))} | "
            f"{fmt_cents(row.get('avg_future_net_needed_for_cushion3'))} | "
            f"{', '.join(row.get('missing_gates') or []) or 'none'} |"
        )
    lines.extend(["", "## Loss Tags", ""])
    for row in report.get("rows") or []:
        lines.append(f"### {row.get('candidate')}")
        lines.append(f"- Source counts: `{row.get('source_counts')}`")
        lines.append(f"- Pending source counts: `{row.get('pending_source_counts')}`")
        lines.append(f"- Loss tag counts: `{row.get('loss_tag_counts')}`")
        largest = row.get("largest_losses") or []
        if largest:
            lines.append("")
            lines.append("| market | source | side | net | ask | abs d | recross | raw edge | tags |")
            lines.append("|---|---|---|---:|---:|---:|---:|---:|---|")
            for loss in largest:
                lines.append(
                    f"| {loss.get('market')} | {loss.get('source')} | {loss.get('side')} | {fmt_cents(loss.get('net_cents'))} | "
                    f"{loss.get('ask_prob')} | {loss.get('abs_d_sigma')} | {loss.get('recross_hazard_score')} | "
                    f"{loss.get('raw_edge')} | {', '.join(loss.get('tags') or [])} |"
                )
        lines.append("")
    lines.extend(["## Interpretation", ""])
    for note in report.get("interpretation") or []:
        lines.append(f"- {note}")
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    report = build_report()
    write_outputs(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
