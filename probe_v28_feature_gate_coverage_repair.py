"""Near-promotion coverage repair audit for v28 feature gates.

Research-only; no live bot changes or orders.

The near-promotion feature-gate lane is profitable and source-clean enough, but
too narrow. This probe tests observable relaxations around that lane and
separates the added rows from the existing anchor rows so we can see whether a
coverage repair adds real signal or just imports source-fragile exposure.
"""
from __future__ import annotations

import json
import math
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from probe_v28_boundary_clock_feature_gate_candidate import (
    as_float,
    best_per_market,
    blockers,
    load_or_create_state,
    market,
    net,
    reconstructed_share,
    source,
)
from probe_v28_boundary_clock_feature_gate_coverage_source_frontier import passes_rule, rule_name
from probe_v28_frozen_boundary_clock_fv_entry_bridge import future_surfaces as bridge_surfaces
from probe_v28_frozen_boundary_clock_repair_entry import future_surfaces as entry_surfaces


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
OUT_JSON = OUT_DIR / "v28_feature_gate_coverage_repair_latest.json"
OUT_MD = OUT_DIR / "v28_feature_gate_coverage_repair_latest.md"

TARGET_COVERAGE_MIN = 75.0
TARGET_COVERAGE_MAX = 90.0
MAX_RECON_SHARE = 0.35
MIN_SETTLED = 30
MIN_CUSHION = 3

ANCHOR_RULE = {
    "raw_edge_min": 0.05,
    "recross_max": 0.60,
    "abs_d_min": 0.85,
    "ask_min": None,
}

RAW_EDGE_MINS = [0.03, 0.05, 0.07]
RECROSS_MAXES = [0.50, 0.60, 0.70]
ABS_D_MINS = [0.50, 0.75, 0.85]
ASK_MINS = [None, 0.35, 0.65]


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def row_key(row: dict[str, Any]) -> tuple[str, str]:
    return str(row.get("market") or ""), str(row.get("side") or "")


def is_settled(row: dict[str, Any]) -> bool:
    return isinstance(row.get("side_won"), bool)


def is_reconstructed(row: dict[str, Any]) -> bool:
    return source(row) != "approved_entry"


def fnum(value: Any, default: float = 0.0) -> float:
    parsed = as_float(value)
    return default if parsed is None else parsed


def classify_row(row: dict[str, Any]) -> list[str]:
    tags: list[str] = []
    if is_reconstructed(row):
        tags.append("source_fragile")
    if fnum(row.get("ask_prob")) < 0.15:
        tags.append("cheap_tail")
    if fnum(row.get("raw_edge")) < 0.05:
        tags.append("thin_raw_edge")
    if fnum(row.get("recross_hazard_score"), 1.0) > 0.30:
        tags.append("recross_risk")
    if fnum(row.get("abs_d_sigma")) < 0.85:
        tags.append("lower_abs_d")
    return tags or ["clean_like"]


def source_counts(rows: list[dict[str, Any]]) -> dict[str, int]:
    return dict(Counter(source(row) for row in rows))


def summarize_rows(rows: list[dict[str, Any]], denominator: int) -> dict[str, Any]:
    settled = [row for row in rows if is_settled(row)]
    wins = sum(1 for row in settled if net(row) > 0)
    losses = sum(1 for row in settled if net(row) < 0)
    net_cents = sum(net(row) for row in settled)
    counts = source_counts(rows)
    recon_share = reconstructed_share(counts)
    coverage = 100.0 * len(rows) / denominator if denominator else 0.0
    return {
        "entries": len(rows),
        "settled": len(settled),
        "pending": len(rows) - len(settled),
        "wins": wins,
        "losses": losses,
        "net_cents": net_cents,
        "avg_net_cents": net_cents / len(settled) if settled else 0.0,
        "coverage_pct": coverage,
        "source_counts": counts,
        "reconstructed_share": recon_share,
        "full_loss_cushion": int(max(0.0, net_cents) // 100.0),
    }


def row_blockers(summary: dict[str, Any]) -> list[str]:
    out = blockers(summary, summary.get("reconstructed_share"))
    if summary.get("full_loss_cushion", 0) < MIN_CUSHION and "full_loss_cushion_lt_3" not in out:
        out.append("full_loss_cushion_lt_3")
    coverage = fnum(summary.get("coverage_pct"))
    if coverage > TARGET_COVERAGE_MAX and "coverage_too_high" not in out:
        out.append("coverage_too_high")
    return out


def make_rule(raw_min: float, recross_max: float, abs_min: float, ask_min: float | None) -> dict[str, Any]:
    return {
        "raw_edge_min": raw_min,
        "recross_max": recross_max,
        "abs_d_min": abs_min,
        "ask_min": ask_min,
    }


def selected_for_rule(rows: list[dict[str, Any]], rule: dict[str, Any]) -> list[dict[str, Any]]:
    return best_per_market([row for row in rows if passes_rule(row, rule)])


def evaluate_rule(
    lane: str,
    all_rows: list[dict[str, Any]],
    denominator: int,
    anchor_rows: list[dict[str, Any]],
    rule: dict[str, Any],
) -> dict[str, Any]:
    selected = selected_for_rule(all_rows, rule)
    anchor_keys = {row_key(row) for row in anchor_rows}
    selected_keys = {row_key(row) for row in selected}
    added = [row for row in selected if row_key(row) not in anchor_keys]
    removed = [row for row in anchor_rows if row_key(row) not in selected_keys]
    selected_summary = summarize_rows(selected, denominator)
    added_summary = summarize_rows(added, denominator)
    removed_summary = summarize_rows(removed, denominator)
    tag_counts: Counter[str] = Counter()
    tag_net: Counter[str] = Counter()
    for row in added:
        for tag in classify_row(row):
            tag_counts[tag] += 1
            if is_settled(row):
                tag_net[tag] += net(row)
    required_entries = math.ceil(TARGET_COVERAGE_MIN * denominator / 100.0)
    clean_rows_needed = 0
    recon_count = sum(1 for row in selected if is_reconstructed(row))
    while len(selected) + clean_rows_needed > 0 and (
        recon_count / (len(selected) + clean_rows_needed)
    ) > MAX_RECON_SHARE:
        clean_rows_needed += 1
    needed_for_cushion = max(0.0, 300.0 - float(selected_summary["net_cents"]))
    return {
        "lane": lane,
        "rule": rule_name(rule),
        "rule_params": rule,
        "summary": selected_summary,
        "added_summary": added_summary,
        "removed_summary": removed_summary,
        "added_tag_counts": dict(tag_counts),
        "added_tag_net_cents": dict(tag_net),
        "coverage_entries_needed": max(0, required_entries - len(selected)),
        "clean_rows_needed_for_source": clean_rows_needed,
        "net_cents_needed_for_cushion3": needed_for_cushion,
        "blockers": row_blockers(selected_summary),
        "live_ready": False,
        "added_largest_losses": sorted(
            [
                {
                    "market": market(row),
                    "side": row.get("side"),
                    "source": source(row),
                    "net_cents": net(row),
                    "ask_prob": row.get("ask_prob"),
                    "raw_edge": row.get("raw_edge"),
                    "recross_hazard_score": row.get("recross_hazard_score"),
                    "abs_d_sigma": row.get("abs_d_sigma"),
                    "tags": classify_row(row),
                }
                for row in added
                if is_settled(row) and net(row) < 0
            ],
            key=lambda row: row["net_cents"],
        )[:8],
        "added_best_wins": sorted(
            [
                {
                    "market": market(row),
                    "side": row.get("side"),
                    "source": source(row),
                    "net_cents": net(row),
                    "ask_prob": row.get("ask_prob"),
                    "raw_edge": row.get("raw_edge"),
                    "recross_hazard_score": row.get("recross_hazard_score"),
                    "abs_d_sigma": row.get("abs_d_sigma"),
                    "tags": classify_row(row),
                }
                for row in added
                if is_settled(row) and net(row) > 0
            ],
            key=lambda row: -row["net_cents"],
        )[:8],
    }


def evaluate_lane(label: str, freeze_ts: str, surfaces_fn: Any) -> dict[str, Any]:
    rows, _, denominator = surfaces_fn(freeze_ts)
    denominator = int(denominator or 0)
    anchor = selected_for_rule(rows, ANCHOR_RULE)
    variants: list[dict[str, Any]] = []
    for raw_min in RAW_EDGE_MINS:
        for recross_max in RECROSS_MAXES:
            for abs_min in ABS_D_MINS:
                for ask_min in ASK_MINS:
                    variants.append(
                        evaluate_rule(label, rows, denominator, anchor, make_rule(raw_min, recross_max, abs_min, ask_min))
                    )
    variants.sort(
        key=lambda row: (
            len(row["blockers"]),
            row["coverage_entries_needed"],
            row["clean_rows_needed_for_source"],
            row["net_cents_needed_for_cushion3"],
            -float((row.get("summary") or {}).get("net_cents") or -999999.0),
        )
    )
    clean_broad = [
        row
        for row in variants
        if not row["blockers"]
    ]
    near_misses = variants[:20]
    target_coverage = [
        row
        for row in variants
        if fnum((row.get("summary") or {}).get("coverage_pct")) >= TARGET_COVERAGE_MIN
        and fnum((row.get("summary") or {}).get("net_cents")) > 0
    ]
    target_coverage.sort(
        key=lambda row: (
            row["clean_rows_needed_for_source"],
            row["net_cents_needed_for_cushion3"],
            -float((row.get("summary") or {}).get("net_cents") or -999999.0),
        )
    )
    anchor_summary = summarize_rows(anchor, denominator)
    return {
        "lane": label,
        "future_denominator": denominator,
        "anchor_rule": rule_name(ANCHOR_RULE),
        "anchor_summary": anchor_summary,
        "anchor_blockers": row_blockers(anchor_summary),
        "clean_broad_live_ready_now": clean_broad[:20],
        "near_misses": near_misses,
        "target_coverage_positive": target_coverage[:20],
        "variant_count": len(variants),
    }


def build_report() -> dict[str, Any]:
    state = load_or_create_state()
    freeze_ts = str(state["freeze_ts_utc"])
    report = {
        "generated_at_utc": utc_now_iso(),
        "freeze_ts_utc": freeze_ts,
        "purpose": (
            "Audit whether observable relaxations can repair coverage for the current "
            "near-promotion feature-gate lane without breaking source quality or cushion."
        ),
        "lanes": [
            evaluate_lane("post_feature_freeze_entry", freeze_ts, entry_surfaces),
            evaluate_lane("post_feature_freeze_bridge", freeze_ts, bridge_surfaces),
        ],
    }
    report["interpretation"] = interpretation(report)
    return report


def interpretation(report: dict[str, Any]) -> list[str]:
    notes = [
        "This is a research-only repair audit; no row is promoted by this scan.",
    ]
    for lane in report.get("lanes") or []:
        clean = lane.get("clean_broad_live_ready_now") or []
        anchor = lane.get("anchor_summary") or {}
        near = (lane.get("near_misses") or [{}])[0]
        near_summary = near.get("summary") or {}
        if clean:
            best = clean[0]
            summary = best.get("summary") or {}
            notes.append(
                f"{lane.get('lane')}: found {len(clean)} observable repair(s) clearing gates in this tiny window; "
                f"best {best.get('rule')} selected {summary.get('entries')}/{lane.get('future_denominator')} "
                f"with net {summary.get('net_cents')}c and recon {summary.get('reconstructed_share')}."
            )
        else:
            notes.append(
                f"{lane.get('lane')}: no observable relaxation clears all gates now. Anchor {lane.get('anchor_rule')} "
                f"has {anchor.get('entries')}/{lane.get('future_denominator')} entries, net {anchor.get('net_cents')}c, "
                f"recon {anchor.get('reconstructed_share')}; nearest {near.get('rule')} has "
                f"{near_summary.get('entries')}/{lane.get('future_denominator')} entries, net {near_summary.get('net_cents')}c, "
                f"recon {near_summary.get('reconstructed_share')}, blockers {near.get('blockers')}."
            )
    return notes


def fmt(value: Any) -> str:
    if value is None:
        return "n/a"
    if isinstance(value, float):
        return f"{value:.3f}"
    return str(value)


def append_table(lines: list[str], rows: list[dict[str, Any]]) -> None:
    lines.extend(
        [
            "| rule | selected W/L | selected cov | selected net | recon | added W/L | added net | added source | needs | blockers |",
            "|---|---:|---:|---:|---:|---:|---:|---|---|---|",
        ]
    )
    for row in rows:
        summary = row.get("summary") or {}
        added = row.get("added_summary") or {}
        needs = (
            f"cov {row.get('coverage_entries_needed')}, "
            f"clean {row.get('clean_rows_needed_for_source')}, "
            f"cushion {fmt(row.get('net_cents_needed_for_cushion3'))}c"
        )
        lines.append(
            f"| {row.get('rule')} | {summary.get('wins')}/{summary.get('losses')} | "
            f"{fmt(summary.get('coverage_pct'))}% | {fmt(summary.get('net_cents'))} | "
            f"{fmt(summary.get('reconstructed_share'))} | {added.get('wins')}/{added.get('losses')} | "
            f"{fmt(added.get('net_cents'))} | {added.get('source_counts')} | {needs} | "
            f"{', '.join(row.get('blockers') or []) or 'none'} |"
        )


def write_report(report: dict[str, Any]) -> None:
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8")
    lines = [
        "# v28 Feature-Gate Coverage Repair Audit",
        "",
        "Research-only; no live bot changes or orders.",
        "",
        f"- Generated UTC: `{report.get('generated_at_utc')}`",
        f"- Freeze UTC: `{report.get('freeze_ts_utc')}`",
        "",
        "## Interpretation",
    ]
    lines.extend(f"- {note}" for note in report.get("interpretation") or [])
    for lane in report.get("lanes") or []:
        anchor = lane.get("anchor_summary") or {}
        lines.extend(
            [
                "",
                f"## {lane.get('lane')}",
                "",
                f"- Anchor: `{lane.get('anchor_rule')}`",
                f"- Anchor selected: `{anchor.get('entries')}/{lane.get('future_denominator')}`",
                f"- Anchor W/L: `{anchor.get('wins')}/{anchor.get('losses')}`",
                f"- Anchor net: `{fmt(anchor.get('net_cents'))}c`",
                f"- Anchor reconstructed share: `{fmt(anchor.get('reconstructed_share'))}`",
                f"- Anchor blockers: `{', '.join(lane.get('anchor_blockers') or []) or 'none'}`",
                "",
                "### Nearest Observable Repairs",
                "",
            ]
        )
        append_table(lines, lane.get("near_misses") or [])
        target = lane.get("target_coverage_positive") or []
        if target:
            lines.extend(["", "### Positive Target-Coverage Relaxations", ""])
            append_table(lines, target[:10])
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    write_report(build_report())


if __name__ == "__main__":
    main()
