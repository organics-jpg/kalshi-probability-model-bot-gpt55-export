"""Observable coverage/source frontier for boundary-clock feature gates.

Research-only; no live bot changes or orders.

This is an audit, not a new promotable candidate. It scans observable gate
features around the frozen boundary-clock feature-gate family and then reports
the PnL/coverage/source-quality tradeoff. Source labels are only used after
selection to audit evidence quality.
"""
from __future__ import annotations

import json
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
    recross,
    reconstructed_share,
    source,
)
from probe_v28_coverage_repair_pool_diagnostic import COVERAGE_FLOOR, raw_edge, summarize
from probe_v28_frozen_boundary_clock_fv_entry_bridge import future_surfaces as bridge_surfaces
from probe_v28_frozen_boundary_clock_repair_entry import future_surfaces as entry_surfaces


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
OUT_JSON = OUT_DIR / "v28_boundary_clock_feature_gate_coverage_source_frontier_latest.json"
OUT_MD = OUT_DIR / "v28_boundary_clock_feature_gate_coverage_source_frontier_latest.md"

RAW_EDGE_MINS = [0.03, 0.05, 0.07]
RECROSS_MAXES = [0.50, 0.60, 0.70]
ABS_D_MINS = [0.50, 0.65, 0.75, 0.85]
ASK_MINS = [None, 0.35, 0.50, 0.65]
MAX_RECON_SHARE = 0.35


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def source_counts(rows: list[dict[str, Any]]) -> dict[str, int]:
    return dict(Counter(source(row) for row in rows))


def passes_rule(row: dict[str, Any], rule: dict[str, Any]) -> bool:
    edge = raw_edge(row)
    row_recross = recross(row)
    abs_d = as_float(row.get("abs_d_sigma"))
    ask = as_float(row.get("ask_prob"))
    if edge is None or row_recross is None or abs_d is None:
        return False
    if edge < float(rule["raw_edge_min"]):
        return False
    if row_recross > float(rule["recross_max"]):
        return False
    if abs_d < float(rule["abs_d_min"]):
        return False
    ask_min = rule.get("ask_min")
    if ask_min is not None and (ask is None or ask < float(ask_min)):
        return False
    return True


def rule_name(rule: dict[str, Any]) -> str:
    ask = rule.get("ask_min")
    ask_part = "asknone" if ask is None else f"ask{int(round(float(ask) * 100)):02d}"
    return (
        f"raw{int(round(float(rule['raw_edge_min']) * 100)):02d}_"
        f"recross{int(round(float(rule['recross_max']) * 100)):02d}_"
        f"abs{int(round(float(rule['abs_d_min']) * 100)):02d}_"
        f"{ask_part}"
    )


def selected_rows(rows: list[dict[str, Any]], rule: dict[str, Any]) -> list[dict[str, Any]]:
    return best_per_market([row for row in rows if passes_rule(row, rule)])


def classify_frontier(row: dict[str, Any]) -> list[str]:
    summary = row.get("summary") or {}
    out = []
    coverage = as_float(summary.get("coverage_pct"))
    net_cents = as_float(summary.get("net_cents"))
    share = row.get("reconstructed_share")
    if coverage is not None and coverage >= COVERAGE_FLOOR:
        out.append("target_coverage")
    if net_cents is not None and net_cents > 0:
        out.append("positive_net")
    if share is not None and share <= MAX_RECON_SHARE:
        out.append("source_clean")
    if "target_coverage" in out and "positive_net" in out and "source_clean" in out:
        out.append("frontier_watch")
    return out


def evaluate_rule(lane: str, rows: list[dict[str, Any]], denominator: int, rule: dict[str, Any]) -> dict[str, Any]:
    selected = selected_rows(rows, rule)
    summary = summarize(selected, denominator)
    counts = source_counts(selected)
    share = reconstructed_share(counts)
    result = {
        "lane": lane,
        "rule": rule_name(rule),
        "rule_params": rule,
        "future_denominator": denominator,
        "summary": summary,
        "source_counts": counts,
        "reconstructed_share": share,
        "full_loss_cushion_estimate": int(max(0.0, float(summary.get("net_cents") or 0.0)) // 100.0),
        "blockers": blockers(summary, share),
        "markets": [market(row) for row in selected],
        "selected_net_cents": [net(row) for row in selected],
    }
    result["frontier_tags"] = classify_frontier(result)
    return result


def pareto_frontier(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    front = []
    for row in rows:
        summary = row.get("summary") or {}
        coverage = float(summary.get("coverage_pct") or 0.0)
        net_cents = float(summary.get("net_cents") or -999999.0)
        share = float(row.get("reconstructed_share") if row.get("reconstructed_share") is not None else 1.0)
        dominated = False
        for other in rows:
            if other is row:
                continue
            other_summary = other.get("summary") or {}
            other_coverage = float(other_summary.get("coverage_pct") or 0.0)
            other_net = float(other_summary.get("net_cents") or -999999.0)
            other_share = float(other.get("reconstructed_share") if other.get("reconstructed_share") is not None else 1.0)
            if (
                other_coverage >= coverage
                and other_net >= net_cents
                and other_share <= share
                and (other_coverage > coverage or other_net > net_cents or other_share < share)
            ):
                dominated = True
                break
        if not dominated:
            front.append(row)
    front.sort(
        key=lambda row: (
            "frontier_watch" not in row.get("frontier_tags", []),
            -float((row.get("summary") or {}).get("net_cents") or -999999.0),
            -float((row.get("summary") or {}).get("coverage_pct") or 0.0),
            float(row.get("reconstructed_share") if row.get("reconstructed_share") is not None else 1.0),
        )
    )
    return front


def evaluate_lane(label: str, freeze_ts: str, surfaces_fn: Any) -> dict[str, Any]:
    rows, _, denominator = surfaces_fn(freeze_ts)
    variants = []
    for raw_min in RAW_EDGE_MINS:
        for recross_max in RECROSS_MAXES:
            for abs_min in ABS_D_MINS:
                for ask_min in ASK_MINS:
                    rule = {
                        "raw_edge_min": raw_min,
                        "recross_max": recross_max,
                        "abs_d_min": abs_min,
                        "ask_min": ask_min,
                    }
                    variants.append(evaluate_rule(label, rows, int(denominator or 0), rule))
    variants.sort(
        key=lambda row: (
            len(row.get("blockers") or []),
            -float((row.get("summary") or {}).get("net_cents") or -999999.0),
            -float((row.get("summary") or {}).get("coverage_pct") or 0.0),
            float(row.get("reconstructed_share") if row.get("reconstructed_share") is not None else 1.0),
        )
    )
    frontier = pareto_frontier(variants)
    clean_broad = [
        row
        for row in variants
        if "frontier_watch" in row.get("frontier_tags", [])
    ]
    clean_broad.sort(
        key=lambda row: (
            -float((row.get("summary") or {}).get("net_cents") or -999999.0),
            -float((row.get("summary") or {}).get("coverage_pct") or 0.0),
        )
    )
    return {
        "lane": label,
        "freeze_ts_utc": freeze_ts,
        "future_denominator": int(denominator or 0),
        "top_variants": variants[:20],
        "pareto_frontier": frontier[:20],
        "clean_broad_positive": clean_broad[:20],
        "variant_count": len(variants),
    }


def build_report() -> dict[str, Any]:
    state = load_or_create_state()
    freeze_ts = str(state["freeze_ts_utc"])
    lanes = [
        evaluate_lane("post_feature_freeze_entry", freeze_ts, entry_surfaces),
        evaluate_lane("post_feature_freeze_bridge", freeze_ts, bridge_surfaces),
    ]
    report = {
        "generated_at_utc": utc_now_iso(),
        "freeze_ts_utc": freeze_ts,
        "purpose": "Observable-only coverage/source frontier audit for the frozen feature-gate family.",
        "lanes": lanes,
    }
    report["interpretation"] = interpretation(report)
    return report


def interpretation(report: dict[str, Any]) -> list[str]:
    notes = [
        "This is an audit surface only; source labels are not used for selection and no row is promotable from this scan.",
    ]
    for lane in report.get("lanes") or []:
        clean = lane.get("clean_broad_positive") or []
        front = lane.get("pareto_frontier") or []
        if clean:
            best = clean[0]
            summary = best.get("summary") or {}
            notes.append(
                f"{lane.get('lane')}: {len(clean)} observable rule(s) are positive, target-coverage, and <=35% reconstructed in the current tiny post-freeze sample; best {best.get('rule')} has {summary.get('entries')}/{lane.get('future_denominator')} entries, net {summary.get('net_cents')}c, recon {best.get('reconstructed_share')}."
            )
        elif front:
            best = front[0]
            summary = best.get("summary") or {}
            notes.append(
                f"{lane.get('lane')}: no observable rule clears net/coverage/source gates together; best Pareto row {best.get('rule')} has {summary.get('entries')}/{lane.get('future_denominator')} entries, coverage {summary.get('coverage_pct')}%, net {summary.get('net_cents')}c, recon {best.get('reconstructed_share')}."
            )
    return notes


def fmt(value: Any) -> str:
    if value is None:
        return "None"
    if isinstance(value, float):
        return f"{value:.6f}"
    return str(value)


def append_table(lines: list[str], rows: list[dict[str, Any]]) -> None:
    lines.extend(
        [
            "| rule | selected/den | W/L | coverage | net c | recon | cushion | tags | blockers |",
            "|---|---:|---:|---:|---:|---:|---:|---|---|",
        ]
    )
    for row in rows:
        summary = row.get("summary") or {}
        lines.append(
            f"| {row.get('rule')} | {summary.get('entries')}/{summary.get('denominator', row.get('future_denominator', ''))} | "
            f"{summary.get('wins')}/{summary.get('losses')} | {fmt(summary.get('coverage_pct'))} | "
            f"{fmt(summary.get('net_cents'))} | {fmt(row.get('reconstructed_share'))} | "
            f"{row.get('full_loss_cushion_estimate')} | {', '.join(row.get('frontier_tags') or []) or 'none'} | "
            f"{', '.join(row.get('blockers') or []) or 'none'} |"
        )


def write_report(report: dict[str, Any]) -> None:
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8")
    lines = [
        "# v28 Boundary-Clock Feature-Gate Coverage/Source Frontier",
        "",
        "Research-only audit; no live bot changes or orders.",
        "",
        f"- Generated UTC: `{report.get('generated_at_utc')}`",
        f"- Feature-gate freeze UTC: `{report.get('freeze_ts_utc')}`",
        "",
        "## Interpretation",
        "",
    ]
    for note in report.get("interpretation") or []:
        lines.append(f"- {note}")
    for lane in report.get("lanes") or []:
        lines.extend(["", f"## {lane.get('lane')}", ""])
        lines.append(f"- Future denominator: `{lane.get('future_denominator')}`")
        lines.append(f"- Scanned observable variants: `{lane.get('variant_count')}`")
        lines.extend(["", "### Clean Broad Positive Rules", ""])
        clean = lane.get("clean_broad_positive") or []
        if clean:
            append_table(lines, clean[:12])
        else:
            lines.append("- None.")
        lines.extend(["", "### Pareto Frontier", ""])
        append_table(lines, (lane.get("pareto_frontier") or [])[:12])
        lines.extend(["", "### Top By Gate Sort", ""])
        append_table(lines, (lane.get("top_variants") or [])[:12])
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    report = build_report()
    write_report(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
