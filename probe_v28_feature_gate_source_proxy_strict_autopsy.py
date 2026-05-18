"""Strict-row autopsy for the feature-gate source-proxy watch.

Research-only; no live bot changes, process control, or orders.

This reads the existing source-proxy coverage-repair artifact and classifies
the strict post-birth rows into the project's failure buckets. Source labels
are audit-only; they are not used to define a deployable rule.
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
SOURCE_PROXY_REPAIR_JSON = OUT_DIR / "v28_feature_gate_source_proxy_coverage_repair_latest.json"
OUT_JSON = OUT_DIR / "v28_feature_gate_source_proxy_strict_autopsy_latest.json"
OUT_MD = OUT_DIR / "v28_feature_gate_source_proxy_strict_autopsy_latest.md"

MAX_RECON_SHARE = 0.35
MIN_SETTLED = 30
MIN_CUSHION = 3
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


def fnum(value: Any, default: float = 0.0) -> float:
    if value is None or value == "":
        return default
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def is_approved(row: dict[str, Any]) -> bool:
    return str(row.get("source") or "") == "approved_entry"


def weighted_net(row: dict[str, Any]) -> float:
    return fnum(row.get("net_cents")) * fnum(row.get("weight"), 1.0)


def side_won(row: dict[str, Any]) -> bool | None:
    value = row.get("side_won")
    if isinstance(value, bool):
        return value
    return None


def row_tags(row: dict[str, Any]) -> list[str]:
    tags: list[str] = []
    if not is_approved(row):
        tags.append("source_quality_error")
    if weighted_net(row) < 0:
        tags.append("selected_loss")
    won = side_won(row)
    if won is False:
        tags.append("fv_or_entry_timing_error")
    if fnum(row.get("raw_edge")) < 0.05:
        tags.append("thin_raw_edge")
    if fnum(row.get("eligible_depth")) < 100:
        tags.append("thin_depth")
    if fnum(row.get("abs_d_sigma")) < 0.65:
        tags.append("weak_boundary_distance")
    if fnum(row.get("recross_hazard_score")) > 0.30:
        tags.append("recross_or_boundary_churn")
    ask = fnum(row.get("ask_prob"))
    if ask < 0.50:
        tags.append("cheap_tail_or_contrarian")
    elif ask < 0.65:
        tags.append("mid_cheap_touch")
    if fnum(row.get("seconds_to_close")) < 240:
        tags.append("early_observation")
    if fnum(row.get("weight"), 1.0) < 1.0:
        tags.append("notional_shrunk")
    if not tags:
        tags.append("clean_or_unclassified")
    return tags


def source_share(rows: list[dict[str, Any]]) -> float:
    if not rows:
        return 0.0
    return sum(1 for row in rows if not is_approved(row)) / len(rows)


def summarize_rows(rows: list[dict[str, Any]]) -> dict[str, Any]:
    wins = sum(1 for row in rows if weighted_net(row) > 0)
    losses = sum(1 for row in rows if weighted_net(row) < 0)
    net = sum(weighted_net(row) for row in rows)
    source_counts = Counter(str(row.get("source") or "unknown") for row in rows)
    role_counts = Counter(str(row.get("role") or "unknown") for row in rows)
    tag_counts: Counter[str] = Counter()
    tag_net: defaultdict[str, float] = defaultdict(float)
    tag_rows: defaultdict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        for tag in row_tags(row):
            tag_counts[tag] += 1
            tag_net[tag] += weighted_net(row)
            tag_rows[tag].append(row)
    return {
        "entries": len(rows),
        "settled": len(rows),
        "wins": wins,
        "losses": losses,
        "weighted_net_cents": net,
        "full_loss_cushion": int(max(0.0, net) // FULL_LOSS_CENTS),
        "row_reconstructed_share": source_share(rows),
        "source_counts": dict(source_counts),
        "role_counts": dict(role_counts),
        "tag_counts": dict(tag_counts),
        "tag_weighted_net_cents": {key: round(value, 6) for key, value in sorted(tag_net.items())},
        "worst_rows": [
            row_view(row)
            for row in sorted(rows, key=weighted_net)[:10]
        ],
    }


def gate_math(rows: list[dict[str, Any]]) -> dict[str, Any]:
    entries = len(rows)
    non_approved = sum(1 for row in rows if not is_approved(row))
    approved = entries - non_approved
    max_non_approved_now = math.floor(MAX_RECON_SHARE * entries)
    replacements_needed_same_entries = max(0, non_approved - max_non_approved_now)
    settled_rows_needed = max(0, MIN_SETTLED - entries)
    entries_at_current_non_approved = math.ceil(non_approved / MAX_RECON_SHARE) if non_approved else entries
    clean_additions_needed_if_no_replacements = max(settled_rows_needed, entries_at_current_non_approved - entries)
    net = sum(weighted_net(row) for row in rows)
    cushion_needed_cents = max(0.0, MIN_CUSHION * FULL_LOSS_CENTS - net)
    return {
        "entries": entries,
        "approved_rows": approved,
        "non_approved_rows": non_approved,
        "max_non_approved_at_current_entries": max_non_approved_now,
        "source_replacements_needed_same_entries": replacements_needed_same_entries,
        "settled_rows_needed": settled_rows_needed,
        "clean_additions_needed_if_no_replacements": clean_additions_needed_if_no_replacements,
        "net_cents_needed_for_cushion3": round(cushion_needed_cents, 6),
    }


def row_view(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "market": row.get("market"),
        "side": row.get("side"),
        "source": row.get("source"),
        "role": row.get("role"),
        "side_won": row.get("side_won"),
        "weight": row.get("weight"),
        "net_cents": row.get("net_cents"),
        "weighted_net_cents": round(weighted_net(row), 6),
        "raw_edge": row.get("raw_edge"),
        "p_side": row.get("p_side"),
        "ask_prob": row.get("ask_prob"),
        "abs_d_sigma": row.get("abs_d_sigma"),
        "recross_hazard_score": row.get("recross_hazard_score"),
        "seconds_to_close": row.get("seconds_to_close"),
        "eligible_depth": row.get("eligible_depth"),
        "tags": row_tags(row),
    }


def best_variant(lane: dict[str, Any]) -> dict[str, Any]:
    variants = lane.get("top_variants") or []
    return variants[0] if variants else {}


def autopsy_lane(lane: dict[str, Any]) -> dict[str, Any]:
    variant = best_variant(lane)
    rows = list(variant.get("selected_rows") or [])
    summary = summarize_rows(rows)
    approved_rows = [row for row in rows if is_approved(row)]
    source_rows = [row for row in rows if not is_approved(row)]
    losing_rows = [row for row in rows if weighted_net(row) < 0]
    return {
        "lane": lane.get("lane"),
        "freeze_ts_utc": lane.get("freeze_ts_utc"),
        "future_denominator": lane.get("future_denominator"),
        "candidate_id": variant.get("candidate_id"),
        "reported_blockers": variant.get("blockers") or [],
        "reported_weighted_net_cents": variant.get("weighted_net_cents"),
        "reported_coverage_pct": variant.get("coverage_pct"),
        "summary": summary,
        "gate_math": gate_math(rows),
        "approved_slice": summarize_rows(approved_rows),
        "non_approved_slice": summarize_rows(source_rows),
        "losing_slice": summarize_rows(losing_rows),
        "strict_read": strict_read(summary, gate_math(rows), source_rows, losing_rows),
    }


def strict_read(summary: dict[str, Any], math_row: dict[str, Any], source_rows: list[dict[str, Any]], losing_rows: list[dict[str, Any]]) -> list[str]:
    notes = []
    if summary.get("settled", 0) < MIN_SETTLED:
        notes.append("sample_is_still_below_30_settled")
    if summary.get("row_reconstructed_share", 0.0) > MAX_RECON_SHARE:
        notes.append(
            f"source_gate_needs_{math_row.get('source_replacements_needed_same_entries')}_same-size replacements_or_{math_row.get('clean_additions_needed_if_no_replacements')}_clean_additions"
        )
    if summary.get("full_loss_cushion", 0) < MIN_CUSHION:
        notes.append(f"cushion_needs_{math_row.get('net_cents_needed_for_cushion3')}c_more_net")
    source_net = sum(weighted_net(row) for row in source_rows)
    if source_rows and source_net < 0:
        notes.append("non_approved_slice_is_net_negative")
    if losing_rows:
        top_tags = Counter(tag for row in losing_rows for tag in row_tags(row)).most_common(5)
        notes.append(f"loss_tags={dict(top_tags)}")
    return notes


def build_report() -> dict[str, Any]:
    source = load_json(SOURCE_PROXY_REPAIR_JSON)
    lanes = [
        lane for lane in source.get("lanes") or []
        if str(lane.get("lane") or "").startswith("post_source_proxy_birth_")
    ]
    lane_reports = [autopsy_lane(lane) for lane in lanes]
    return {
        "generated_at_utc": utc_now_iso(),
        "source_artifact": str(SOURCE_PROXY_REPAIR_JSON),
        "source_generated_at_utc": source.get("generated_at_utc"),
        "purpose": "Classify strict post-birth feature-gate source-proxy rows into failure buckets.",
        "lanes": lane_reports,
        "interpretation": interpretation(lane_reports),
    }


def interpretation(lanes: list[dict[str, Any]]) -> list[str]:
    notes = ["This is audit-only; source labels are not deployable selection features."]
    for lane in lanes:
        summary = lane.get("summary") or {}
        math_row = lane.get("gate_math") or {}
        notes.append(
            f"{lane.get('lane')}: best {lane.get('candidate_id')} has {summary.get('settled')} settled, "
            f"net {summary.get('weighted_net_cents')}c, row-source share {summary.get('row_reconstructed_share')}, "
            f"cushion {summary.get('full_loss_cushion')}; needs {math_row.get('source_replacements_needed_same_entries')} "
            f"same-size source replacements or {math_row.get('clean_additions_needed_if_no_replacements')} clean additions, "
            f"plus {math_row.get('net_cents_needed_for_cushion3')}c for cushion."
        )
    return notes


def fmt(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, float):
        return f"{value:.6f}"
    return str(value)


def write_report(report: dict[str, Any]) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    lines = [
        "# v28 Feature-Gate Source-Proxy Strict Autopsy",
        "",
        "Research-only. No live bot logic changes, no process control, no orders.",
        "",
        f"- Generated UTC: `{report.get('generated_at_utc')}`",
        f"- Source artifact UTC: `{report.get('source_generated_at_utc')}`",
        "",
        "## Interpretation",
        "",
    ]
    for note in report.get("interpretation") or []:
        lines.append(f"- {note}")
    for lane in report.get("lanes") or []:
        summary = lane.get("summary") or {}
        math_row = lane.get("gate_math") or {}
        approved = lane.get("approved_slice") or {}
        non_approved = lane.get("non_approved_slice") or {}
        losing = lane.get("losing_slice") or {}
        lines += [
            "",
            f"## {lane.get('lane')}",
            "",
            f"- Candidate: `{lane.get('candidate_id')}`",
            f"- Reported blockers: `{', '.join(lane.get('reported_blockers') or []) or 'none'}`",
            f"- Settled/net/source/cushion: `{summary.get('settled')}` / `{fmt(summary.get('weighted_net_cents'))}c` / `{fmt(summary.get('row_reconstructed_share'))}` / `{summary.get('full_loss_cushion')}`",
            f"- Gate arithmetic: source replacements `{math_row.get('source_replacements_needed_same_entries')}`, clean additions if no replacements `{math_row.get('clean_additions_needed_if_no_replacements')}`, net needed for cushion `{fmt(math_row.get('net_cents_needed_for_cushion3'))}c`",
            f"- Approved slice: `{approved.get('settled')}` rows, `{fmt(approved.get('weighted_net_cents'))}c`, W/L `{approved.get('wins')}/{approved.get('losses')}`",
            f"- Non-approved slice: `{non_approved.get('settled')}` rows, `{fmt(non_approved.get('weighted_net_cents'))}c`, W/L `{non_approved.get('wins')}/{non_approved.get('losses')}`",
            f"- Losing slice: `{losing.get('settled')}` rows, `{fmt(losing.get('weighted_net_cents'))}c`",
            f"- Strict read: `{', '.join(lane.get('strict_read') or [])}`",
            "",
            "### Tag Counts",
            "",
            "| tag | rows | weighted net c |",
            "|---|---:|---:|",
        ]
        tag_counts = summary.get("tag_counts") or {}
        tag_net = summary.get("tag_weighted_net_cents") or {}
        for tag, count in sorted(tag_counts.items(), key=lambda item: (-item[1], item[0])):
            lines.append(f"| `{tag}` | {count} | {fmt(tag_net.get(tag))} |")
        lines += [
            "",
            "### Worst Rows",
            "",
            "| market | side | source | role | weighted c | raw edge | p_side | ask | abs_d | recross | tags |",
            "|---|---|---|---|---:|---:|---:|---:|---:|---:|---|",
        ]
        for row in summary.get("worst_rows") or []:
            lines.append(
                "| {market} | {side} | {source} | {role} | {weighted} | {raw_edge} | {p_side} | {ask} | {abs_d} | {recross} | {tags} |".format(
                    market=row.get("market"),
                    side=row.get("side"),
                    source=row.get("source"),
                    role=row.get("role"),
                    weighted=fmt(row.get("weighted_net_cents")),
                    raw_edge=fmt(row.get("raw_edge")),
                    p_side=fmt(row.get("p_side")),
                    ask=fmt(row.get("ask_prob")),
                    abs_d=fmt(row.get("abs_d_sigma")),
                    recross=fmt(row.get("recross_hazard_score")),
                    tags=", ".join(row.get("tags") or []),
                )
            )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    report = build_report()
    write_report(report)
    print(f"Wrote {OUT_MD}")


if __name__ == "__main__":
    main()
