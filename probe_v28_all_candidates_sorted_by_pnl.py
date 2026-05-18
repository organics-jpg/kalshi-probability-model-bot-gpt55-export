"""All v28 candidate lanes sorted by PnL.

Research-only; no live bot changes or orders.

This is the wide scoreboard counterpart to the readiness-distance digest. It
keeps every tracked lane visible and sorted by current forward/shadow PnL.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
TRACKER_JSON = OUT_DIR / "v28_candidate_pnl_tracker_latest.json"
OUT_JSON = OUT_DIR / "v28_all_candidates_sorted_by_pnl_latest.json"
OUT_MD = OUT_DIR / "v28_all_candidates_sorted_by_pnl_latest.md"


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


def fmt_cents(value: Any) -> str:
    number = as_float(value)
    if number is None:
        return "n/a"
    return f"{number:.0f}c"


def fmt_pct(value: Any) -> str:
    number = as_float(value)
    if number is None:
        return "n/a"
    return f"{number:.2f}%"


def fmt_share(value: Any) -> str:
    number = as_float(value)
    if number is None:
        return "n/a"
    return f"{number * 100.0:.1f}%"


def wl(row: dict[str, Any]) -> str:
    wins = row.get("wins")
    losses = row.get("losses")
    if wins is None or losses is None:
        return "n/a"
    return f"{wins}/{losses}"


def row_sort_key(row: dict[str, Any]) -> tuple[float, float]:
    pnl = as_float(row.get("net_cents_after_entry_fee"))
    settled = as_float(row.get("settled")) or 0.0
    return (pnl if pnl is not None else -999999.0, settled)


def compact_row(row: dict[str, Any], rank: int) -> dict[str, Any]:
    return {
        "rank": rank,
        "gate": row.get("gate"),
        "policy": row.get("policy"),
        "entries": row.get("entries"),
        "settled": row.get("settled"),
        "wins": row.get("wins"),
        "losses": row.get("losses"),
        "coverage_pct": row.get("coverage_pct"),
        "net_cents": row.get("net_cents_after_entry_fee"),
        "simulated_share": row.get("simulated_share"),
        "live_ready": row.get("live_ready"),
        "target_coverage": row.get("target_coverage"),
        "blockers": row.get("blockers") or [],
    }


def build_report() -> dict[str, Any]:
    tracker = load_json(TRACKER_JSON)
    rows = [row for row in tracker.get("rows") or [] if isinstance(row, dict)]
    sorted_rows = sorted(rows, key=row_sort_key, reverse=True)
    ranked = [compact_row(row, rank) for rank, row in enumerate(sorted_rows, start=1)]
    positive = [
        row for row in ranked
        if (as_float(row.get("net_cents")) or 0.0) > 0.0
    ]
    target_positive = [
        row for row in positive
        if bool(row.get("target_coverage"))
    ]
    return {
        "generated_at_utc": utc_now_iso(),
        "source": str(TRACKER_JSON),
        "summary": {
            "candidates": len(ranked),
            "positive_candidates": len(positive),
            "positive_target_coverage_candidates": len(target_positive),
            "live_ready_candidates": sum(1 for row in ranked if row.get("live_ready")),
        },
        "rows": ranked,
    }


def write_md(report: dict[str, Any]) -> None:
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    summary = report["summary"]
    lines = [
        "# v28 All Candidates Sorted By PnL",
        "",
        "Research-only table generated from `v28_candidate_pnl_tracker_latest.json`.",
        "",
        f"- Generated UTC: `{report.get('generated_at_utc')}`",
        f"- Candidates: `{summary['candidates']}`",
        f"- Positive candidates: `{summary['positive_candidates']}`",
        f"- Positive target-coverage candidates: `{summary['positive_target_coverage_candidates']}`",
        f"- Live-ready candidates: `{summary['live_ready_candidates']}`",
        "",
        "| rank | gate | policy | entries | settled | W/L | coverage | pnl | sim share | target cov | live ready | blockers |",
        "|---:|---|---|---:|---:|---:|---:|---:|---:|---|---|---|",
    ]
    for row in report.get("rows") or []:
        blockers = ", ".join(str(item) for item in (row.get("blockers") or []))
        lines.append(
            f"| {row.get('rank')} | `{row.get('gate')}` | `{row.get('policy')}` | "
            f"{row.get('entries')} | {row.get('settled')} | {wl(row)} | "
            f"{fmt_pct(row.get('coverage_pct'))} | {fmt_cents(row.get('net_cents'))} | "
            f"{fmt_share(row.get('simulated_share'))} | {row.get('target_coverage')} | "
            f"{row.get('live_ready')} | {blockers} |"
        )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    report = build_report()
    write_md(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
