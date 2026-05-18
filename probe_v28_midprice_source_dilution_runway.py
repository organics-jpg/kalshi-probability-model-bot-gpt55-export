"""Promotion runway for the midprice source-dilution watch.

Research-only; no live bot changes or orders.

This keeps the newly frozen source-dilution branch honest by measuring only
post-dilution-birth rows against the broad-entry promotion gates.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
WATCH_JSON = OUT_DIR / "v28_midprice_source_dilution_watch_latest.json"
STABILITY_JSON = OUT_DIR / "v28_midprice_source_dilution_stability_latest.json"
MECHANISM_JSON = OUT_DIR / "v28_midprice_source_dilution_mechanism_latest.json"
OUT_JSON = OUT_DIR / "v28_midprice_source_dilution_runway_latest.json"
OUT_MD = OUT_DIR / "v28_midprice_source_dilution_runway_latest.md"

MIN_SETTLED = 30
TARGET_COVERAGE_MIN = 75.0
TARGET_COVERAGE_MAX = 90.0
MAX_RECON_SHARE = 0.35
MIN_CUSHION = 3


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


def as_int(value: Any) -> int:
    return int(as_float(value) or 0)


def coverage_entries_needed(entries: int, denominator: int) -> int:
    target = int(TARGET_COVERAGE_MIN * denominator / 100.0)
    while denominator and 100.0 * target / denominator < TARGET_COVERAGE_MIN:
        target += 1
    return max(0, target - entries)


def clean_rows_needed(entries: int, approved: int) -> int:
    clean = approved
    total = entries
    needed = 0
    while total > 0 and 1.0 - clean / total > MAX_RECON_SHARE:
        clean += 1
        total += 1
        needed += 1
    return needed


def blockers_for(variant: dict[str, Any], denominator: int) -> list[str]:
    entries = as_int(variant.get("entries"))
    settled = as_int(variant.get("settled"))
    net = as_float(variant.get("net_cents")) or 0.0
    coverage = as_float(variant.get("coverage_pct"))
    recon = as_float(variant.get("reconstructed_share"))
    cushion = as_int(variant.get("full_loss_cushion"))
    blockers: list[str] = []
    if settled < MIN_SETTLED:
        blockers.append("settled_lt_30")
    if coverage is None or coverage < TARGET_COVERAGE_MIN:
        blockers.append("coverage_too_low")
    if coverage is not None and coverage > TARGET_COVERAGE_MAX:
        blockers.append("coverage_too_high")
    if net <= 0:
        blockers.append("net_not_positive")
    if recon is None or recon > MAX_RECON_SHARE:
        blockers.append("reconstructed_share_gt_35pct")
    if cushion < MIN_CUSHION:
        blockers.append("full_loss_cushion_lt_3")
    if denominator <= 0:
        blockers.append("no_post_birth_denominator_yet")
    return blockers


def summarize_variant(lane: dict[str, Any], variant: dict[str, Any]) -> dict[str, Any]:
    denominator = as_int(lane.get("future_denominator"))
    entries = as_int(variant.get("entries"))
    source_counts = variant.get("source_counts") if isinstance(variant.get("source_counts"), dict) else {}
    approved = as_int(source_counts.get("approved_entry"))
    net = as_float(variant.get("net_cents")) or 0.0
    cushion = int(max(0.0, net) // 100.0)
    blockers = blockers_for({**variant, "full_loss_cushion": cushion}, denominator)
    return {
        "lane": lane.get("lane"),
        "filter": variant.get("filter"),
        "strict_forward": bool(lane.get("strict_forward")),
        "denominator": denominator,
        "entries": entries,
        "settled": variant.get("settled"),
        "wins": variant.get("wins"),
        "losses": variant.get("losses"),
        "coverage_pct": variant.get("coverage_pct"),
        "net_cents": net,
        "reconstructed_share": variant.get("reconstructed_share"),
        "full_loss_cushion": cushion,
        "source_counts": source_counts,
        "blockers": blockers,
        "settled_needed": max(0, MIN_SETTLED - as_int(variant.get("settled"))),
        "coverage_entries_needed": coverage_entries_needed(entries, denominator),
        "clean_rows_needed_for_source": clean_rows_needed(entries, approved),
        "net_cents_needed_for_cushion3": max(0.0, MIN_CUSHION * 100.0 - net),
        "live_ready": bool(lane.get("strict_forward")) and not blockers,
    }


def best_for_lane(payload: dict[str, Any], lane_name: str) -> dict[str, Any]:
    lane = next((row for row in payload.get("lanes") or [] if row.get("lane") == lane_name), {})
    variants = lane.get("variants") or []
    if not variants:
        return {
            "lane": lane_name,
            "strict_forward": lane.get("strict_forward"),
            "denominator": as_int(lane.get("future_denominator")),
            "entries": 0,
            "settled": 0,
            "wins": 0,
            "losses": 0,
            "coverage_pct": None,
            "net_cents": 0.0,
            "reconstructed_share": None,
            "full_loss_cushion": 0,
            "source_counts": {},
            "blockers": ["no_variants"],
            "settled_needed": MIN_SETTLED,
            "coverage_entries_needed": 0,
            "clean_rows_needed_for_source": 0,
            "net_cents_needed_for_cushion3": 300.0,
            "live_ready": False,
        }
    summarized = [summarize_variant(lane, variant) for variant in variants]
    summarized.sort(
        key=lambda row: (
            len(row.get("blockers") or []),
            -float(row.get("net_cents") or -999999.0),
            -float(row.get("coverage_pct") or 0.0),
        )
    )
    return summarized[0]


def build_report() -> dict[str, Any]:
    watch = load_json(WATCH_JSON)
    stability = load_json(STABILITY_JSON)
    mechanism = load_json(MECHANISM_JSON)
    entry = best_for_lane(watch, "post_dilution_birth_entry")
    bridge = best_for_lane(watch, "post_dilution_birth_bridge")
    report = {
        "generated_at_utc": utc_now_iso(),
        "freeze_ts_utc": (watch.get("state") or {}).get("freeze_ts_utc"),
        "candidate": (watch.get("state") or {}).get("candidate"),
        "entry_runway": entry,
        "bridge_runway": bridge,
        "any_live_ready": bool(entry.get("live_ready") or bridge.get("live_ready")),
        "parent_diagnostic_best": next(
            (
                (lane.get("variants") or [{}])[0]
                for lane in watch.get("lanes") or []
                if lane.get("lane") == "diagnostic_parent_entry"
            ),
            {},
        ),
        "parent_stability_flags": ((stability.get("lanes") or [{}])[0]).get("stability_flags"),
        "mechanism_interpretation": mechanism.get("interpretation"),
    }
    report["interpretation"] = interpretation(report)
    return report


def interpretation(report: dict[str, Any]) -> list[str]:
    notes = [
        "Only post_dilution_birth lanes count as forward evidence for this branch.",
    ]
    for label in ("entry_runway", "bridge_runway"):
        row = report.get(label) or {}
        notes.append(
            f"{label}: settled {row.get('settled')}, coverage {row.get('coverage_pct')}, "
            f"net {row.get('net_cents')}c, recon {row.get('reconstructed_share')}, "
            f"cushion {row.get('full_loss_cushion')}, blockers {row.get('blockers')}."
        )
    if not report.get("any_live_ready"):
        notes.append("No source-dilution lane is live-ready.")
    return notes


def money(value: Any) -> str:
    number = as_float(value)
    return "n/a" if number is None else f"{number:.1f}c"


def pct(value: Any) -> str:
    number = as_float(value)
    return "n/a" if number is None else f"{number:.2f}%"


def write_report(report: dict[str, Any]) -> None:
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8")
    lines = [
        "# v28 Midprice Source-Dilution Runway",
        "",
        "Research-only. No live bot changes or orders.",
        "",
        f"- Generated UTC: `{report.get('generated_at_utc')}`",
        f"- Freeze UTC: `{report.get('freeze_ts_utc')}`",
        f"- Candidate: `{report.get('candidate')}`",
        f"- Any live-ready: `{report.get('any_live_ready')}`",
        "",
        "## Interpretation",
        "",
    ]
    lines.extend(f"- {note}" for note in report.get("interpretation") or [])
    lines.extend([
        "",
        "## Runway",
        "",
        "| lane | filter | denom | entries | settled | W/L | coverage | net | recon | cushion | settled need | cov need | clean need | cushion need | blockers |",
        "|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|",
    ])
    for lane_name in ("entry_runway", "bridge_runway"):
        row = report.get(lane_name) or {}
        lines.append(
            f"| `{lane_name}` | `{row.get('filter')}` | {row.get('denominator')} | {row.get('entries')} | "
            f"{row.get('settled')} | {row.get('wins')}/{row.get('losses')} | {pct(row.get('coverage_pct'))} | "
            f"{money(row.get('net_cents'))} | {pct((as_float(row.get('reconstructed_share')) or 0.0) * 100.0) if row.get('reconstructed_share') is not None else 'n/a'} | "
            f"{row.get('full_loss_cushion')} | {row.get('settled_needed')} | {row.get('coverage_entries_needed')} | "
            f"{row.get('clean_rows_needed_for_source')} | {money(row.get('net_cents_needed_for_cushion3'))} | "
            f"{', '.join(row.get('blockers') or []) or 'none'} |"
        )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    report = build_report()
    write_report(report)
    print(OUT_MD)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
