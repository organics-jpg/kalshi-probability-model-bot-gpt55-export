"""Mechanism drilldown for the midprice source-dilution watch.

Research-only; no live bot changes or orders.

This explains whether the remaining source-risk in the diluted midprice lane is
replaceable by observable same-market alternatives, or whether the branch is
still dependent on reconstructed/rejected rows that cannot be safely repaired
without fresh approved-entry evidence.
"""
from __future__ import annotations

import json
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from probe_v28_boundary_clock_feature_gate_candidate import as_float, best_per_market, load_json, market, net, source
from probe_v28_frozen_boundary_clock_repair_entry import future_surfaces as entry_surfaces
from probe_v28_midprice_source_dilution_watch import FILTERS, STATE_JSON, passes_broad, passes_filter, quarter_weight
from probe_v28_midprice_source_dilution_watch import rows_from_artifact as dilution_rows_from_artifact
from probe_v28_coverage_repair_pool_diagnostic import raw_edge


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
MIDPRICE_JSON = OUT_DIR / "v28_soft_frontier_midprice_boundary_shrink_latest.json"
OUT_JSON = OUT_DIR / "v28_midprice_source_dilution_mechanism_latest.json"
OUT_MD = OUT_DIR / "v28_midprice_source_dilution_mechanism_latest.md"

PARENT_FEATURE_FREEZE = "2026-05-06T16:47:25.847566+00:00"
TARGET_FILTER = "absd_gte_055_or_ask_gte_065"


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def fnum(value: Any, default: float = 0.0) -> float:
    parsed = as_float(value)
    return default if parsed is None else parsed


def recross(row: dict[str, Any]) -> float:
    return fnum(row.get("recross_hazard_score"), 1.0)


def abs_d(row: dict[str, Any]) -> float:
    return fnum(row.get("abs_d_sigma"))


def ask(row: dict[str, Any]) -> float:
    return fnum(row.get("ask_prob"))


def raw_score(row: dict[str, Any]) -> float:
    if row.get("raw_edge") is not None:
        return fnum(row.get("raw_edge"), -999.0)
    return fnum(raw_edge(row), -999.0)


def weighted_net(row: dict[str, Any]) -> float:
    raw_net = as_float(row.get("raw_net_cents"))
    if raw_net is None:
        raw_net = net(row)
    return raw_net * quarter_weight(row)


def rank_raw(row: dict[str, Any]) -> tuple[float, float, float, str]:
    return (raw_score(row), abs_d(row), -recross(row), str(row.get("ts_wall") or ""))


def compact(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "market": market(row),
        "side": row.get("side"),
        "source": source(row),
        "net_cents": net(row),
        "weighted_net_cents": weighted_net(row),
        "weight": quarter_weight(row),
        "raw_edge": raw_score(row),
        "abs_d_sigma": row.get("abs_d_sigma"),
        "ask_prob": row.get("ask_prob"),
        "recross_hazard_score": row.get("recross_hazard_score"),
        "seconds_to_close": row.get("seconds_to_close"),
        "eligible_depth": row.get("eligible_depth"),
        "book_age_ms": row.get("book_age_ms"),
        "btc_age_ms": row.get("btc_age_ms"),
        "side_won": row.get("side_won"),
        "tags": tags(row),
    }


def tags(row: dict[str, Any]) -> list[str]:
    out: list[str] = []
    if source(row) != "approved_entry":
        out.append("source_quality_risk")
    if abs_d(row) < 0.55:
        out.append("very_weak_boundary_absd_lt055")
    elif abs_d(row) < 0.65:
        out.append("weak_boundary_absd_lt065")
    elif abs_d(row) < 0.85:
        out.append("moderate_boundary_absd_lt085")
    if ask(row) < 0.50:
        out.append("cheap_or_midcheap_ask_lt050")
    elif ask(row) < 0.65:
        out.append("midprice_ask_lt065")
    if recross(row) > 0.30:
        out.append("recross_gt030")
    if raw_score(row) < 0.05:
        out.append("thin_raw_edge_lt005")
    if row.get("seconds_to_close") is not None and fnum(row.get("seconds_to_close")) < 240:
        out.append("early_stc_lt240")
    if row.get("eligible_depth") is not None and fnum(row.get("eligible_depth")) < 100:
        out.append("thin_depth_lt100")
    return out or ["clean_or_unclassified"]


def summarize(rows: list[dict[str, Any]], denominator: int) -> dict[str, Any]:
    total = sum(weighted_net(row) for row in rows)
    approved = sum(1 for row in rows if source(row) == "approved_entry")
    return {
        "entries": len(rows),
        "settled": sum(1 for row in rows if isinstance(row.get("side_won"), bool)),
        "wins": sum(1 for row in rows if weighted_net(row) > 0),
        "losses": sum(1 for row in rows if weighted_net(row) < 0),
        "net_cents": total,
        "coverage_pct": 100.0 * len(rows) / denominator if denominator else None,
        "reconstructed_share": 1.0 - approved / len(rows) if rows else None,
        "full_loss_cushion": int(max(0.0, total) // 100.0),
        "source_counts": dict(Counter(source(row) for row in rows)),
        "tag_counts": dict(Counter(tag for row in rows for tag in tags(row))),
    }


def selected_rows(all_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rule = FILTERS[TARGET_FILTER]
    return best_per_market([row for row in all_rows if passes_broad(row) and passes_filter(row, rule)])


def same_market_alternates(all_rows: list[dict[str, Any]], selected: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    rule = FILTERS[TARGET_FILTER]
    for row in all_rows:
        if passes_broad(row) and passes_filter(row, rule):
            grouped[market(row)].append(row)
    out = []
    for row in selected:
        if source(row) == "approved_entry":
            continue
        alts = sorted(
            [alt for alt in grouped.get(market(row), []) if source(alt) == "approved_entry"],
            key=rank_raw,
            reverse=True,
        )
        out.append({
            "selected": compact(row),
            "approved_alternates": [compact(alt) for alt in alts[:5]],
            "same_market_approved_exists": bool(alts),
        })
    return out


def source_oracle_replacement(all_rows: list[dict[str, Any]], selected: list[dict[str, Any]], denominator: int) -> dict[str, Any]:
    selected_markets = {market(row) for row in selected}
    selected_source_rows = sorted([row for row in selected if source(row) != "approved_entry"], key=weighted_net)
    omitted_approved = best_per_market(
        [
            row for row in all_rows
            if passes_broad(row)
            and passes_filter(row, FILTERS[TARGET_FILTER])
            and source(row) == "approved_entry"
            and market(row) not in selected_markets
        ]
    )
    omitted_approved = sorted(omitted_approved, key=weighted_net, reverse=True)
    variants = []
    for n in range(1, min(len(selected_source_rows), len(omitted_approved)) + 1):
        drop = selected_source_rows[:n]
        drop_markets = {market(row) for row in drop}
        candidate = [row for row in selected if market(row) not in drop_markets] + omitted_approved[:n]
        summary = summarize(candidate, denominator)
        variants.append({
            "replacements": n,
            "dropped": [compact(row) for row in drop],
            "added": [compact(row) for row in omitted_approved[:n]],
            "summary": summary,
            "clears_core_gates": clears_core_gates(summary),
        })
    return {
        "selected_source_rows": len(selected_source_rows),
        "omitted_approved_available": len(omitted_approved),
        "first_clear": next((row for row in variants if row.get("clears_core_gates")), None),
        "variants": variants[:8],
        "note": "Non-deployable source-label oracle bound; source labels are audit-only.",
    }


def clears_core_gates(summary: dict[str, Any]) -> bool:
    coverage = as_float(summary.get("coverage_pct"))
    recon = as_float(summary.get("reconstructed_share"))
    return (
        int(summary.get("settled") or 0) >= 30
        and coverage is not None and coverage >= 75.0
        and recon is not None and recon <= 0.35
        and fnum(summary.get("net_cents")) > 0
        and int(summary.get("full_loss_cushion") or 0) >= 3
    )


def omitted_near_misses(all_rows: list[dict[str, Any]], selected: list[dict[str, Any]], denominator: int) -> dict[str, Any]:
    selected_markets = {market(row) for row in selected}
    near = []
    for row in all_rows:
        if market(row) in selected_markets or source(row) != "approved_entry":
            continue
        if not passes_broad(row):
            continue
        fail_reasons = []
        if not passes_filter(row, FILTERS[TARGET_FILTER]):
            fail_reasons.append("dilution_filter_fail")
        if fail_reasons:
            near.append({**compact(row), "fail_reasons": fail_reasons})
    near.sort(key=lambda row: fnum(row.get("weighted_net_cents")), reverse=True)
    return {
        "count": len(near),
        "summary": {
            "entries": len(near),
            "net_cents": sum(fnum(row.get("weighted_net_cents")) for row in near),
            "wins": sum(1 for row in near if fnum(row.get("weighted_net_cents")) > 0),
            "losses": sum(1 for row in near if fnum(row.get("weighted_net_cents")) < 0),
            "coverage_if_added_pct": 100.0 * (len(selected) + len(near)) / denominator if denominator else None,
        },
        "top": near[:12],
        "worst": sorted(near, key=lambda row: fnum(row.get("weighted_net_cents")))[:12],
    }


def build_report() -> dict[str, Any]:
    state = load_json(STATE_JSON)
    all_rows, _, surface_denominator = entry_surfaces(PARENT_FEATURE_FREEZE)
    artifact_rows, artifact_denominator = dilution_rows_from_artifact("post_feature_freeze_entry")
    denominator = int(artifact_denominator or surface_denominator or 0)
    selected = [row for row in artifact_rows if passes_filter(row, FILTERS[TARGET_FILTER])]
    selected_source = [row for row in selected if source(row) != "approved_entry"]
    selected_approved = [row for row in selected if source(row) == "approved_entry"]
    return {
        "generated_at_utc": utc_now_iso(),
        "candidate_freeze_ts_utc": state.get("freeze_ts_utc"),
        "parent_feature_freeze_ts_utc": PARENT_FEATURE_FREEZE,
        "target_filter": TARGET_FILTER,
        "future_denominator": denominator,
        "surface_denominator_for_alternates": int(surface_denominator or 0),
        "selected_summary": summarize(selected, denominator),
        "approved_selected_summary": summarize(selected_approved, denominator),
        "source_selected_summary": summarize(selected_source, denominator),
        "same_market_alternates": same_market_alternates(all_rows, selected),
        "source_oracle_replacement": source_oracle_replacement(all_rows, selected, denominator),
        "omitted_near_misses": omitted_near_misses(all_rows, selected, denominator),
        "source_rows": sorted([compact(row) for row in selected_source], key=lambda row: fnum(row.get("weighted_net_cents"))),
        "approved_rows": sorted([compact(row) for row in selected_approved], key=lambda row: fnum(row.get("weighted_net_cents"))),
    }


def money(value: Any) -> str:
    number = as_float(value)
    return "n/a" if number is None else f"{number:.1f}c"


def pct(value: Any) -> str:
    number = as_float(value)
    if number is None:
        return "n/a"
    if number <= 1.0:
        number *= 100.0
    return f"{number:.2f}%"


def write_report(report: dict[str, Any]) -> None:
    selected = report.get("selected_summary") or {}
    source_summary = report.get("source_selected_summary") or {}
    oracle = report.get("source_oracle_replacement") or {}
    notes = [
        "Source labels are audit/oracle-only; the deployable candidate still uses observable abs_d/ask filtering.",
        f"Selected lane has {selected.get('entries')} entries, net {selected.get('net_cents')}c, recon {selected.get('reconstructed_share')}, cushion {selected.get('full_loss_cushion')}.",
        f"Remaining source-risk slice has {source_summary.get('entries')} rows for {source_summary.get('net_cents')}c; omitted approved available for oracle replacement: {oracle.get('omitted_approved_available')}.",
    ]
    report["interpretation"] = notes
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8")
    lines = [
        "# v28 Midprice Source-Dilution Mechanism",
        "",
        "Research-only. No live bot changes or orders.",
        "",
        f"- Generated UTC: `{report.get('generated_at_utc')}`",
        f"- Candidate freeze UTC: `{report.get('candidate_freeze_ts_utc')}`",
        f"- Parent feature freeze UTC: `{report.get('parent_feature_freeze_ts_utc')}`",
        "",
        "## Interpretation",
        "",
    ]
    lines.extend(f"- {note}" for note in notes)
    lines.extend([
        "",
        "## Summaries",
        "",
        f"- Selected: `{report.get('selected_summary')}`",
        f"- Approved selected: `{report.get('approved_selected_summary')}`",
        f"- Source selected: `{report.get('source_selected_summary')}`",
        f"- Oracle replacement: `{report.get('source_oracle_replacement')}`",
        f"- Omitted near misses: `{report.get('omitted_near_misses')}`",
        "",
        "## Source Rows",
        "",
        "| market | side | net | source | abs_d | ask | recross | tags |",
        "|---|---|---:|---|---:|---:|---:|---|",
    ])
    for row in report.get("source_rows") or []:
        lines.append(
            f"| `{row.get('market')}` | `{row.get('side')}` | {money(row.get('weighted_net_cents'))} | "
            f"`{row.get('source')}` | {row.get('abs_d_sigma')} | {row.get('ask_prob')} | "
            f"{row.get('recross_hazard_score')} | {', '.join(row.get('tags') or [])} |"
        )
    lines.extend([
        "",
        "## Same-Market Alternates",
        "",
        "| selected market | selected net | approved alternates |",
        "|---|---:|---|",
    ])
    for row in report.get("same_market_alternates") or []:
        selected_row = row.get("selected") or {}
        alts = row.get("approved_alternates") or []
        alt_text = "; ".join(
            f"{alt.get('side')} {money(alt.get('weighted_net_cents'))} absd={alt.get('abs_d_sigma')} ask={alt.get('ask_prob')}"
            for alt in alts
        ) or "none"
        lines.append(f"| `{selected_row.get('market')}` | {money(selected_row.get('weighted_net_cents'))} | {alt_text} |")
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    report = build_report()
    write_report(report)
    print(OUT_MD)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
