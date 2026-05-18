"""Outcome-linkage overlay for post-freeze v28 feature-gate variants.

Research-only; no live bot changes or orders.

The feature-gate research surface can lag finalized Kalshi outcomes for rows
whose markets are already resolved in the refreshed live scorer artifacts.
This probe reports how post-feature-freeze variant summaries would look if
those finalized market results were linked back for still-pending rows. It is
an audit overlay, not an official scorer replacement.
"""
from __future__ import annotations

import csv
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from probe_v28_boundary_clock_feature_gate_candidate import (
    MAX_RECONSTRUCTED_SHARE,
    MIN_FULL_LOSS_CUSHION,
    MIN_SETTLED,
    blockers,
)
from probe_v28_coverage_repair_pool_diagnostic import COVERAGE_FLOOR
from probe_v28_danger_tag_replacement_diagnostic import row_net_after_fee


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
FEATURE_JSON = OUT_DIR / "v28_boundary_clock_feature_gate_candidate_latest.json"
MARKET_RESULTS_CSV = ROOT / "stats" / "live_mushroom_v28_size2" / "market_results.csv"
OUT_JSON = OUT_DIR / "v28_feature_gate_outcome_linkage_overlay_latest.json"
OUT_MD = OUT_DIR / "v28_feature_gate_outcome_linkage_overlay_latest.md"

TARGET_LANES = {"post_feature_freeze_entry", "post_feature_freeze_bridge"}


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


def load_market_results(path: Path) -> dict[str, dict[str, str]]:
    out: dict[str, dict[str, str]] = {}
    if not path.exists():
        return out
    with path.open("r", encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle):
            market = str(row.get("market") or "")
            if market:
                out[market] = row
    return out


def side_won(side: str, result: str) -> bool | None:
    if side not in {"yes", "no"} or result not in {"yes", "no"}:
        return None
    return side == result


def row_net_cents(row: dict[str, Any]) -> float:
    stored = as_float(row.get("net_cents"))
    if stored is not None:
        return stored
    return float(row_net_after_fee(row) or 0.0)


def linked_row(row: dict[str, Any], market_results: dict[str, dict[str, str]]) -> tuple[dict[str, Any], bool]:
    if row.get("side_won") is not None:
        return dict(row), False
    market = str(row.get("market") or "")
    result_row = market_results.get(market) or {}
    result = str(result_row.get("result") or "")
    won = side_won(str(row.get("side") or ""), result)
    if won is None:
        return dict(row), False
    out = dict(row)
    out["side_won"] = won
    out["linked_market_result"] = result
    out["linked_market_status"] = result_row.get("status")
    out["linked_settlement_ts"] = result_row.get("settlement_ts")
    out["net_cents"] = row_net_after_fee(out)
    return out, True


def summarize(rows: list[dict[str, Any]], denominator: int) -> dict[str, Any]:
    settled = [row for row in rows if row.get("side_won") is not None]
    net_cents = sum(row_net_cents(row) for row in settled)
    return {
        "entries": len(rows),
        "settled": len(settled),
        "wins": sum(1 for row in settled if row.get("side_won") is True),
        "losses": sum(1 for row in settled if row.get("side_won") is False),
        "coverage_pct": 100.0 * len(rows) / denominator if denominator else None,
        "net_cents": net_cents,
        "avg_net_cents": net_cents / len(settled) if settled else None,
    }


def source_share(source_counts: dict[str, int]) -> float | None:
    total = sum(source_counts.values())
    if total <= 0:
        return None
    return (total - int(source_counts.get("approved_entry") or 0)) / total


def variant_overlay(lane: dict[str, Any], variant: dict[str, Any], market_results: dict[str, dict[str, str]]) -> dict[str, Any]:
    rows = [row for row in variant.get("rows") or [] if isinstance(row, dict)]
    denominator = int(as_float(lane.get("future_denominator")) or 0)
    linked_rows = []
    linked_count = 0
    linked_net_delta = 0.0
    linked_details = []
    for row in rows:
        before_net = row_net_cents(row) if row.get("side_won") is not None else 0.0
        out, did_link = linked_row(row, market_results)
        linked_rows.append(out)
        if did_link:
            linked_count += 1
            linked_net = row_net_cents(out)
            linked_net_delta += linked_net - before_net
            linked_details.append(
                {
                    "market": out.get("market"),
                    "source": out.get("source"),
                    "side": out.get("side"),
                    "market_result": out.get("linked_market_result"),
                    "side_won": out.get("side_won"),
                    "net_cents": linked_net,
                    "ask_prob": out.get("ask_prob"),
                    "raw_edge": out.get("raw_edge"),
                    "recross_hazard_score": out.get("recross_hazard_score"),
                    "abs_d_sigma": out.get("abs_d_sigma"),
                }
            )
    linked_summary = summarize(linked_rows, denominator)
    counts = dict(Counter(str(row.get("source") or "unknown") for row in rows))
    share = source_share(counts)
    official_summary = variant.get("candidate_summary") or {}
    linked_blockers = blockers(linked_summary, share)
    return {
        "lane": lane.get("lane"),
        "candidate": variant.get("candidate"),
        "official_summary": official_summary,
        "linked_summary": linked_summary,
        "linked_rows_count": linked_count,
        "linked_net_delta_cents": linked_net_delta,
        "source_counts": counts,
        "reconstructed_share": share,
        "official_blockers": variant.get("blockers"),
        "linked_blockers": linked_blockers,
        "linked_full_loss_cushion_estimate": int(max(0.0, float(linked_summary.get("net_cents") or 0.0)) // 100.0),
        "coverage_gate": (linked_summary.get("coverage_pct") or 0.0) >= COVERAGE_FLOOR,
        "sample_gate": int(linked_summary.get("settled") or 0) >= MIN_SETTLED,
        "net_gate": float(linked_summary.get("net_cents") or 0.0) > 0.0,
        "source_gate": share is not None and share <= MAX_RECONSTRUCTED_SHARE,
        "cushion_gate": int(max(0.0, float(linked_summary.get("net_cents") or 0.0)) // 100.0) >= MIN_FULL_LOSS_CUSHION,
        "linked_rows": linked_details,
    }


def build_report() -> dict[str, Any]:
    feature = load_json(FEATURE_JSON)
    market_results = load_market_results(MARKET_RESULTS_CSV)
    overlays = []
    for lane in feature.get("lanes") or []:
        if lane.get("lane") not in TARGET_LANES:
            continue
        for variant in lane.get("variants") or []:
            if isinstance(variant, dict):
                overlays.append(variant_overlay(lane, variant, market_results))
    overlays.sort(
        key=lambda row: (
            len(row.get("linked_blockers") or []),
            -float((row.get("linked_summary") or {}).get("net_cents") or -999999.0),
        )
    )
    return {
        "generated_at_utc": utc_now_iso(),
        "feature_source": str(FEATURE_JSON),
        "market_results_source": str(MARKET_RESULTS_CSV),
        "purpose": "Outcome-linkage overlay for post-freeze feature-gate variants; official scorer unchanged.",
        "rows": overlays,
        "interpretation": interpretation(overlays),
    }


def interpretation(overlays: list[dict[str, Any]]) -> list[str]:
    notes = [
        "Rows are ranked by linked blockers and linked net, but this remains an audit overlay.",
    ]
    if overlays:
        best = overlays[0]
        linked = best.get("linked_summary") or {}
        notes.append(
            f"Best linked row is {best.get('candidate')} with settled {linked.get('settled')}, "
            f"coverage {linked.get('coverage_pct')}%, net {linked.get('net_cents')}c, "
            f"reconstructed share {best.get('reconstructed_share')}, blockers {best.get('linked_blockers')}."
        )
    live_ready = [row for row in overlays if not row.get("linked_blockers")]
    notes.append(f"Linked-overlay live-ready rows: {len(live_ready)}.")
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
    lines = [
        "# v28 Feature-Gate Outcome Linkage Overlay",
        "",
        "Research-only audit overlay. No live bot changes or orders.",
        "",
        f"- Generated UTC: `{report.get('generated_at_utc')}`",
        "",
        "## Interpretation",
        "",
    ]
    for note in report.get("interpretation") or []:
        lines.append(f"- {note}")
    lines.extend(
        [
            "",
            "## Variants",
            "",
            "| rank | lane | candidate | official settled/net | linked settled/net | coverage | recon | linked rows | cushion | linked blockers |",
            "|---:|---|---|---:|---:|---:|---:|---:|---:|---|",
        ]
    )
    for idx, row in enumerate(report.get("rows") or [], start=1):
        official = row.get("official_summary") or {}
        linked = row.get("linked_summary") or {}
        lines.append(
            f"| {idx} | {row.get('lane')} | {row.get('candidate')} | "
            f"{official.get('settled')}/{fmt(official.get('net_cents'))}c | "
            f"{linked.get('settled')}/{fmt(linked.get('net_cents'))}c | "
            f"{fmt(linked.get('coverage_pct'))} | {fmt(row.get('reconstructed_share'))} | "
            f"{row.get('linked_rows_count')} | {row.get('linked_full_loss_cushion_estimate')} | "
            f"{', '.join(row.get('linked_blockers') or []) or 'none'} |"
        )
    lines.extend(
        [
            "",
            "## Linked Rows",
            "",
            "| candidate | market | source | side | result | won | net c | ask | edge | recross | abs d |",
            "|---|---|---|---|---|---|---:|---:|---:|---:|---:|",
        ]
    )
    for row in report.get("rows") or []:
        for linked in row.get("linked_rows") or []:
            lines.append(
                f"| {row.get('candidate')} | {linked.get('market')} | {linked.get('source')} | "
                f"{linked.get('side')} | {linked.get('market_result')} | {linked.get('side_won')} | "
                f"{fmt(linked.get('net_cents'))} | {fmt(linked.get('ask_prob'))} | "
                f"{fmt(linked.get('raw_edge'))} | {fmt(linked.get('recross_hazard_score'))} | "
                f"{fmt(linked.get('abs_d_sigma'))} |"
            )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    report = build_report()
    write_md(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
