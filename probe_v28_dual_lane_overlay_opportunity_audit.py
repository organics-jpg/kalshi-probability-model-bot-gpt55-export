"""Overlay-opportunity audit for v28 dual-lane versus live v28.

Research-only; no live bot changes or orders.

This probe treats dual-lane as a possible overlay/risk-control component rather
than a replacement strategy. It classifies same-window market deltas into
whether dual-lane avoids live losses, misses live winner capture, or is
directionally wrong.
"""
from __future__ import annotations

import json
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
COMPARE_JSON = OUT_DIR / "v28_dual_lane_same_window_live_compare_latest.json"
OUT_JSON = OUT_DIR / "v28_dual_lane_overlay_opportunity_audit_latest.json"
OUT_MD = OUT_DIR / "v28_dual_lane_overlay_opportunity_audit_latest.md"


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


def write_json(path: Path, payload: dict[str, Any]) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8")


def fnum(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def money(value: Any) -> str:
    cents = fnum(value)
    return f"{cents:.0f}c (${cents / 100.0:.2f})"


def avg(rows: list[dict[str, Any]], field: str) -> float | None:
    values = [fnum(row.get(field), float("nan")) for row in rows if row.get(field) is not None]
    values = [value for value in values if value == value]
    return sum(values) / len(values) if values else None


def summarize(rows: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "rows": len(rows),
        "candidate_net_cents": sum(fnum(row.get("candidate_net_cents")) for row in rows),
        "live_net_cents": sum(fnum(row.get("live_net_cents")) for row in rows),
        "candidate_minus_live_cents": sum(fnum(row.get("candidate_minus_live_cents")) for row in rows),
        "avg_raw_edge": avg(rows, "raw_edge"),
        "avg_ask_prob": avg(rows, "ask_prob"),
        "avg_abs_d_sigma": avg(rows, "abs_d_sigma"),
        "avg_recross_hazard": avg(rows, "recross_hazard_score"),
        "components": dict(
            sorted(
                {
                    str(component): sum(1 for row in rows if str(row.get("candidate_component")) == str(component))
                    for component in {row.get("candidate_component") for row in rows}
                }.items()
            )
        ),
        "sources": dict(
            sorted(
                {
                    str(source): sum(1 for row in rows if str(row.get("candidate_source")) == str(source))
                    for source in {row.get("candidate_source") for row in rows}
                }.items()
            )
        ),
        "sides": dict(
            sorted(
                {
                    str(side): sum(1 for row in rows if str(row.get("candidate_side")) == str(side))
                    for side in {row.get("candidate_side") for row in rows}
                }.items()
            )
        ),
    }


def build_report() -> dict[str, Any]:
    compare = load_json(COMPARE_JSON)
    rows = [row for row in compare.get("comparison_rows") or [] if isinstance(row, dict)]
    by_bucket: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        by_bucket[str(row.get("comparison_bucket") or "unknown")].append(row)

    summaries = {bucket: summarize(items) for bucket, items in sorted(by_bucket.items())}
    helpful_buckets = {"candidate_improves_live_loss", "candidate_vs_no_live_pnl"}
    harmful_buckets = {"candidate_right_but_live_captured_more", "candidate_wrong_or_exit_bad_live_won"}
    helpful_rows = [row for row in rows if row.get("comparison_bucket") in helpful_buckets]
    harmful_rows = [row for row in rows if row.get("comparison_bucket") in harmful_buckets]
    helpful = summarize(helpful_rows)
    harmful = summarize(harmful_rows)
    net_overlay_opportunity = helpful["candidate_minus_live_cents"] + harmful["candidate_minus_live_cents"]

    failure_modes = {
        "exit_policy_error": {
            "status": "active",
            "evidence": (
                "Three same-side winning markets show live v28 captured far more than dual-lane; "
                "dual-lane's current exit/weighting caps winners too aggressively."
            ),
        },
        "entry_timing_error": {
            "status": "active",
            "evidence": "Two candidate loss rows were live-positive after live v28 flipped or managed the market better.",
        },
        "execution_friction_error": {
            "status": "possible",
            "evidence": "Candidate rows are single-row simulated/weighted fills while live v28 can scale or re-enter.",
        },
        "source_quality_error": {
            "status": "not_main_same_window_driver",
            "evidence": "Most harmful candidate-minus-live rows are approved-entry rows, not rejected-actionable rows.",
        },
        "fragility_error": {
            "status": "active",
            "evidence": "Candidate net remains below one full-loss cushion and same-window delta is negative.",
        },
    }

    return {
        "generated_at_utc": utc_now_iso(),
        "compare_generated_at_utc": compare.get("generated_at_utc"),
        "promotion_use": "diagnostic_only_overlay_design",
        "candidate_policy": compare.get("candidate_policy"),
        "same_window_delta_cents": compare.get("candidate_minus_live_same_markets_cents"),
        "bucket_summaries": summaries,
        "helpful_overlay_summary": helpful,
        "harmful_overlay_summary": harmful,
        "net_overlay_opportunity_cents": net_overlay_opportunity,
        "failure_modes": failure_modes,
        "candidate_read": [
            "Dual-lane is not currently a live-v28 replacement.",
            "Its useful shape is as a possible risk-control overlay on markets where live v28 churns or loses.",
            "The blocker is winner capture: live v28 made large same-side gains on several markets that dual-lane clipped to small wins.",
            "A live-ready repair must preserve live v28's winner capture while using dual-lane only where it has forward evidence of reducing live loss clusters.",
        ],
    }


def fmt(value: Any) -> str:
    if value is None:
        return "n/a"
    return f"{fnum(value):.3f}"


def write_md(report: dict[str, Any]) -> None:
    write_json(OUT_JSON, report)
    helpful = report.get("helpful_overlay_summary") or {}
    harmful = report.get("harmful_overlay_summary") or {}
    lines = [
        "# v28 Dual-Lane Overlay Opportunity Audit",
        "",
        "Research-only. No live bot logic changes, no orders.",
        "",
        f"- Generated UTC: `{report.get('generated_at_utc')}`",
        f"- Same-window compare UTC: `{report.get('compare_generated_at_utc')}`",
        f"- Promotion use: `{report.get('promotion_use')}`",
        f"- Candidate policy: `{report.get('candidate_policy')}`",
        f"- Current same-window delta: `{money(report.get('same_window_delta_cents'))}`",
        "",
        "## Read",
        "",
    ]
    lines.extend(f"- {item}" for item in report.get("candidate_read") or [])
    lines.extend(
        [
            "",
            "## Overlay Split",
            "",
            "| split | rows | candidate net | live net | candidate-live | avg raw | avg ask | avg abs d | avg recross |",
            "|---|---:|---:|---:|---:|---:|---:|---:|---:|",
            (
                f"| helpful or no-live-pnl buckets | {helpful.get('rows')} | {money(helpful.get('candidate_net_cents'))} | "
                f"{money(helpful.get('live_net_cents'))} | {money(helpful.get('candidate_minus_live_cents'))} | "
                f"{fmt(helpful.get('avg_raw_edge'))} | {fmt(helpful.get('avg_ask_prob'))} | "
                f"{fmt(helpful.get('avg_abs_d_sigma'))} | {fmt(helpful.get('avg_recross_hazard'))} |"
            ),
            (
                f"| harmful buckets | {harmful.get('rows')} | {money(harmful.get('candidate_net_cents'))} | "
                f"{money(harmful.get('live_net_cents'))} | {money(harmful.get('candidate_minus_live_cents'))} | "
                f"{fmt(harmful.get('avg_raw_edge'))} | {fmt(harmful.get('avg_ask_prob'))} | "
                f"{fmt(harmful.get('avg_abs_d_sigma'))} | {fmt(harmful.get('avg_recross_hazard'))} |"
            ),
        ]
    )
    lines.extend(
        [
            "",
            "## Bucket Summaries",
            "",
            "| bucket | rows | candidate net | live net | candidate-live | components | sides |",
            "|---|---:|---:|---:|---:|---|---|",
        ]
    )
    summaries = report.get("bucket_summaries") if isinstance(report.get("bucket_summaries"), dict) else {}
    for bucket, summary in sorted(summaries.items(), key=lambda item: fnum((item[1] or {}).get("candidate_minus_live_cents"))):
        if not isinstance(summary, dict):
            continue
        lines.append(
            f"| `{bucket}` | {summary.get('rows')} | {money(summary.get('candidate_net_cents'))} | "
            f"{money(summary.get('live_net_cents'))} | {money(summary.get('candidate_minus_live_cents'))} | "
            f"`{summary.get('components')}` | `{summary.get('sides')}` |"
        )
    lines.extend(
        [
            "",
            "## Failure Modes",
            "",
            "| mode | status | evidence |",
            "|---|---|---|",
        ]
    )
    modes = report.get("failure_modes") if isinstance(report.get("failure_modes"), dict) else {}
    for mode, item in modes.items():
        if not isinstance(item, dict):
            continue
        lines.append(f"| `{mode}` | `{item.get('status')}` | {item.get('evidence')} |")
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    report = build_report()
    write_md(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
