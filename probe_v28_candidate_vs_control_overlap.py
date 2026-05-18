"""Same-market candidate versus v28 control overlap audit.

Research-only; no live bot changes or orders.

The usual bakeoff ranks candidates on the markets they select. That is useful,
but it can hide whether a candidate is truly better than the live/control
strategy or just selecting a different set of mostly simulated rejected rows.
This audit splits each entry candidate into:
- overlap markets where both candidate and baseline_v28_approved settled;
- candidate-only settled markets;
- baseline-only settled markets.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
BAKEOFF_JSON = OUT_DIR / "v28_shadow_entry_policy_bakeoff_latest.json"
OUT_JSON = OUT_DIR / "v28_candidate_vs_control_overlap_latest.json"
OUT_MD = OUT_DIR / "v28_candidate_vs_control_overlap_latest.md"

BASELINE_POLICY = "baseline_v28_approved"
MIN_PROMOTION_SETTLED = 30
MAX_SIMULATED_SHARE = 0.35
TARGET_COVERAGE_MIN = 75.0
TARGET_COVERAGE_MAX = 90.0


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


def settled(row: dict[str, Any]) -> bool:
    return row.get("side_won") is not None and as_float(row.get("gross_cents")) is not None


def market_key(row: dict[str, Any]) -> str:
    return str(row.get("market") or "")


def summarize_rows(rows: list[dict[str, Any]]) -> dict[str, Any]:
    settled_rows = [row for row in rows if settled(row)]
    gross_values = [float(row.get("gross_cents") or 0.0) for row in settled_rows]
    return {
        "rows": len(rows),
        "settled": len(settled_rows),
        "wins": sum(1 for row in settled_rows if row.get("side_won") is True),
        "losses": sum(1 for row in settled_rows if row.get("side_won") is False),
        "gross_cents": sum(gross_values),
        "avg_gross_cents": sum(gross_values) / len(gross_values) if gross_values else None,
        "approved_entry_count": sum(1 for row in rows if row.get("source") == "approved_entry"),
        "added_reject_count": sum(1 for row in rows if row.get("source") == "rejected_actionable"),
    }


def blockers(summary: dict[str, Any]) -> list[str]:
    out: list[str] = []
    settled_count = int(as_float(summary.get("candidate_settled")) or 0)
    coverage = as_float(summary.get("candidate_coverage_pct"))
    sim_share = as_float(summary.get("candidate_simulated_share"))
    if settled_count < MIN_PROMOTION_SETTLED:
        out.append("candidate_settled_lt_30")
    if sim_share is None or sim_share > MAX_SIMULATED_SHARE:
        out.append("candidate_simulated_share_gt_35pct")
    if coverage is None or coverage < TARGET_COVERAGE_MIN:
        out.append("coverage_below_75pct")
    if coverage is not None and coverage > TARGET_COVERAGE_MAX:
        out.append("coverage_above_90pct")
    if as_float(summary.get("overlap_delta_cents")) is None:
        out.append("no_settled_overlap_with_control")
    return out


def build_report() -> dict[str, Any]:
    payload = load_json(BAKEOFF_JSON)
    all_rows = payload.get("rows") if isinstance(payload.get("rows"), list) else []
    ranked = payload.get("ranked") if isinstance(payload.get("ranked"), list) else []
    coverage_by_policy = {str(row.get("policy") or ""): row.get("coverage_pct") for row in ranked}
    rows_by_policy: dict[str, list[dict[str, Any]]] = {}
    for row in all_rows:
        policy = str(row.get("policy") or "")
        if policy:
            rows_by_policy.setdefault(policy, []).append(row)

    baseline_rows = rows_by_policy.get(BASELINE_POLICY, [])
    baseline_by_market = {market_key(row): row for row in baseline_rows if market_key(row) and settled(row)}
    candidate_rows: list[dict[str, Any]] = []
    for policy, rows in rows_by_policy.items():
        if policy == BASELINE_POLICY:
            continue
        cand_settled_by_market = {market_key(row): row for row in rows if market_key(row) and settled(row)}
        overlap_markets = sorted(set(cand_settled_by_market).intersection(baseline_by_market))
        cand_overlap = [cand_settled_by_market[market] for market in overlap_markets]
        base_overlap = [baseline_by_market[market] for market in overlap_markets]
        candidate_only_markets = sorted(set(cand_settled_by_market).difference(baseline_by_market))
        baseline_only_markets = sorted(set(baseline_by_market).difference(cand_settled_by_market))
        candidate_only = [cand_settled_by_market[market] for market in candidate_only_markets]
        baseline_only = [baseline_by_market[market] for market in baseline_only_markets]
        cand_summary = summarize_rows(rows)
        overlap_candidate_gross = sum(float(row.get("gross_cents") or 0.0) for row in cand_overlap)
        overlap_baseline_gross = sum(float(row.get("gross_cents") or 0.0) for row in base_overlap)
        candidate_only_gross = sum(float(row.get("gross_cents") or 0.0) for row in candidate_only)
        baseline_only_gross = sum(float(row.get("gross_cents") or 0.0) for row in baseline_only)
        simulated_share = (
            cand_summary["added_reject_count"] / cand_summary["rows"]
            if cand_summary["rows"]
            else None
        )
        row = {
            "policy": policy,
            "candidate_entries": cand_summary["rows"],
            "candidate_settled": cand_summary["settled"],
            "candidate_wins": cand_summary["wins"],
            "candidate_losses": cand_summary["losses"],
            "candidate_gross_cents": cand_summary["gross_cents"],
            "candidate_avg_gross_cents": cand_summary["avg_gross_cents"],
            "candidate_coverage_pct": coverage_by_policy.get(policy),
            "candidate_approved_entry_count": cand_summary["approved_entry_count"],
            "candidate_added_reject_count": cand_summary["added_reject_count"],
            "candidate_simulated_share": simulated_share,
            "overlap_markets": len(overlap_markets),
            "overlap_candidate_gross_cents": overlap_candidate_gross,
            "overlap_baseline_gross_cents": overlap_baseline_gross,
            "overlap_delta_cents": overlap_candidate_gross - overlap_baseline_gross if overlap_markets else None,
            "candidate_only_markets": len(candidate_only_markets),
            "candidate_only_gross_cents": candidate_only_gross,
            "baseline_only_markets": len(baseline_only_markets),
            "baseline_only_gross_cents": baseline_only_gross,
            "net_selection_delta_cents": candidate_only_gross - baseline_only_gross,
            "sample_overlap_markets": overlap_markets[:8],
            "sample_candidate_only_markets": candidate_only_markets[:8],
        }
        row["blockers"] = blockers(row)
        candidate_rows.append(row)

    ranked_rows = sorted(
        candidate_rows,
        key=lambda row: (
            float(row.get("candidate_gross_cents") or -999999.0),
            float(row.get("overlap_delta_cents") if row.get("overlap_delta_cents") is not None else -999999.0),
            -float(row.get("candidate_simulated_share") or 1.0),
        ),
        reverse=True,
    )
    target_coverage_rows = [
        row for row in ranked_rows
        if (as_float(row.get("candidate_coverage_pct")) is not None and TARGET_COVERAGE_MIN <= float(row["candidate_coverage_pct"]) <= TARGET_COVERAGE_MAX)
    ]
    return {
        "baseline_policy": BASELINE_POLICY,
        "baseline": summarize_rows(baseline_rows),
        "watched_markets": payload.get("watched_markets"),
        "observation_rows": payload.get("observation_rows"),
        "rows": candidate_rows,
        "ranked": ranked_rows,
        "target_coverage_ranked": target_coverage_rows,
        "interpretation": current_read(ranked_rows, target_coverage_rows),
    }


def current_read(rows: list[dict[str, Any]], target_rows: list[dict[str, Any]]) -> list[str]:
    notes: list[str] = []
    if rows:
        top = rows[0]
        notes.append(
            f"Top gross candidate is {top['policy']} with {top['candidate_gross_cents']}c on its selected settled markets."
        )
    positive_overlap = [row for row in rows if as_float(row.get("overlap_delta_cents")) is not None and float(row["overlap_delta_cents"]) > 0]
    if positive_overlap:
        best = max(positive_overlap, key=lambda row: float(row.get("overlap_delta_cents") or 0.0))
        notes.append(
            f"Best same-market overlap delta is {best['policy']} at {best['overlap_delta_cents']}c across {best['overlap_markets']} overlapping markets."
        )
    if target_rows:
        best_target = target_rows[0]
        notes.append(
            f"Best 75-90% coverage candidate by gross is {best_target['policy']} with coverage {best_target['candidate_coverage_pct']} and gross {best_target['candidate_gross_cents']}c."
        )
    blockers = sorted({blocker for row in rows for blocker in (row.get("blockers") or [])})
    if blockers:
        notes.append(f"Common blockers remain: {', '.join(blockers)}.")
    return notes


def fmt(value: Any) -> str:
    if value is None:
        return "None"
    if isinstance(value, float):
        return f"{value:.6f}"
    return str(value)


def write_md(report: dict[str, Any]) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8")
    base = report.get("baseline") or {}
    lines = [
        "# v28 Candidate vs Control Overlap",
        "",
        "Same-market control comparison for shadow entry candidates. No candidate is promoted here.",
        "",
        f"- Baseline policy: `{report.get('baseline_policy')}`",
        f"- Baseline entries/settled/W-L/gross: `{base.get('rows')}/{base.get('settled')}/{base.get('wins')}-{base.get('losses')}/{fmt(base.get('gross_cents'))}c`",
        f"- Watched markets / observation rows: `{report.get('watched_markets')}/{report.get('observation_rows')}`",
        "",
        "## Current Read",
        "",
    ]
    for note in report.get("interpretation") or []:
        lines.append(f"- {note}")
    lines.extend([
        "",
        "## Ranked Candidates",
        "",
        "| rank | policy | entries | settled | W/L | coverage | gross c | sim share | overlap delta | candidate-only c | baseline-only c | blockers |",
        "|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|",
    ])
    for idx, row in enumerate(report.get("ranked") or [], start=1):
        lines.append(
            f"| {idx} | `{row.get('policy')}` | {row.get('candidate_entries')} | {row.get('candidate_settled')} | "
            f"{row.get('candidate_wins')}/{row.get('candidate_losses')} | {fmt(row.get('candidate_coverage_pct'))} | "
            f"{fmt(row.get('candidate_gross_cents'))} | {fmt(row.get('candidate_simulated_share'))} | "
            f"{fmt(row.get('overlap_delta_cents'))} | {fmt(row.get('candidate_only_gross_cents'))} | "
            f"{fmt(row.get('baseline_only_gross_cents'))} | {', '.join(row.get('blockers') or []) or 'none'} |"
        )
    lines.extend([
        "",
        "## Target-Coverage Rows",
        "",
        "| policy | coverage | gross c | overlap markets | overlap delta | simulated share | blockers |",
        "|---|---:|---:|---:|---:|---:|---|",
    ])
    for row in report.get("target_coverage_ranked") or []:
        lines.append(
            f"| `{row.get('policy')}` | {fmt(row.get('candidate_coverage_pct'))} | "
            f"{fmt(row.get('candidate_gross_cents'))} | {row.get('overlap_markets')} | "
            f"{fmt(row.get('overlap_delta_cents'))} | {fmt(row.get('candidate_simulated_share'))} | "
            f"{', '.join(row.get('blockers') or []) or 'none'} |"
        )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    report = build_report()
    write_md(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
