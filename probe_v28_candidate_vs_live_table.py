"""Full candidate-vs-live PnL table for v28 research.

Research-only; no live bot changes or orders.

This materializes the user's requested all-candidate scoreboard from current
local artifacts so it stays in sync with the live-only scorer and candidate
tracking refreshes.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
TRACKER_JSON = OUT_DIR / "v28_candidate_pnl_tracker_latest.json"
INTEGRITY_JSON = OUT_DIR / "v28_candidate_integrity_scorecard_latest.json"
LEADERBOARD_JSON = OUT_DIR / "v28_frozen_candidate_leaderboard_latest.json"
LIVE_SUMMARY_JSON = ROOT / "stats" / "live_mushroom_v28_size2" / "summary.json"
OUT_JSON = OUT_DIR / "v28_candidate_vs_live_full_table_latest.json"
OUT_MD = OUT_DIR / "v28_candidate_vs_live_full_table_latest.md"


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


def key(gate: Any, policy: Any) -> str:
    return f"{gate}::{policy}"


def fmt_num(value: Any, digits: int = 2) -> str:
    number = as_float(value)
    if number is None:
        return ""
    return f"{number:.{digits}f}"


def fmt_pct(value: Any) -> str:
    number = as_float(value)
    if number is None:
        return ""
    return f"{number:.2f}%"


def fmt_money_cents(value: Any) -> str:
    number = as_float(value)
    if number is None:
        return ""
    return f"{number / 100.0:.2f}"


def wl(row: dict[str, Any]) -> str:
    wins = row.get("wins")
    losses = row.get("losses")
    if wins is None or losses is None:
        return ""
    return f"{wins}/{losses}"


def build_wl_lookup(*payloads: dict[str, Any]) -> dict[str, dict[str, Any]]:
    out: dict[str, dict[str, Any]] = {}
    for payload in payloads:
        rows = []
        for field in ("rows", "ranked", "candidates", "leaderboard", "scorecard"):
            value = payload.get(field)
            if isinstance(value, list):
                rows.extend(item for item in value if isinstance(item, dict))
        for row in rows:
            if row.get("wins") is None and row.get("losses") is None:
                continue
            out[key(row.get("gate"), row.get("policy"))] = {
                "wins": row.get("wins"),
                "losses": row.get("losses"),
            }
    return out


def build_integrity_lookup(payload: dict[str, Any]) -> dict[str, dict[str, Any]]:
    out: dict[str, dict[str, Any]] = {}
    for field in ("candidates", "exit_candidates"):
        value = payload.get(field)
        if not isinstance(value, list):
            continue
        for row in value:
            if not isinstance(row, dict):
                continue
            out[key(row.get("gate"), row.get("policy"))] = row
    return out


def build_report() -> dict[str, Any]:
    tracker = load_json(TRACKER_JSON)
    integrity = load_json(INTEGRITY_JSON)
    leaderboard = load_json(LEADERBOARD_JSON)
    live = load_json(LIVE_SUMMARY_JSON)
    lookup = build_wl_lookup(leaderboard, integrity)
    integrity_lookup = build_integrity_lookup(integrity)
    live_pnl_cents = round(float(live.get("net_pnl_total_dollars") or 0.0) * 100.0)
    rows = [
        {
            "type": "live",
            "gate": live.get("strategy_tag") or "live_mushroom_v28_size2",
            "policy": "current live strategy",
            "entries": live.get("entries_total"),
            "settled": live.get("completed_round_trips"),
            "wins": live.get("confirmed_wins_by_sign"),
            "losses": live.get("confirmed_losses_by_sign"),
            "coverage_pct": None,
            "net_cents": live_pnl_cents,
            "delta_vs_live_cents": 0,
            "live_ready": None,
            "target_coverage": None,
            "simulated_share": None,
            "blockers": [],
        }
    ]
    for row in tracker.get("rows") or []:
        if not isinstance(row, dict):
            continue
        net = as_float(row.get("net_cents_after_entry_fee"))
        row_key = key(row.get("gate"), row.get("policy"))
        wins_losses = lookup.get(row_key, {})
        integrity_row = integrity_lookup.get(row_key, {})
        blockers = list(dict.fromkeys([*(row.get("blockers") or []), *(integrity_row.get("blockers") or [])]))
        simulated_share = integrity_row.get("stress_reconstructed_share")
        if simulated_share is None:
            simulated_share = row.get("simulated_share")
        rows.append(
            {
                "type": "candidate",
                "gate": row.get("gate"),
                "policy": row.get("policy"),
                "entries": row.get("entries"),
                "settled": row.get("settled"),
                "wins": row.get("wins") if row.get("wins") is not None else wins_losses.get("wins"),
                "losses": row.get("losses") if row.get("losses") is not None else wins_losses.get("losses"),
                "coverage_pct": row.get("coverage_pct"),
                "net_cents": net,
                "delta_vs_live_cents": None if net is None else net - live_pnl_cents,
                "live_ready": row.get("live_ready"),
                "target_coverage": row.get("target_coverage"),
                "simulated_share": simulated_share,
                "blockers": blockers,
            }
        )
    candidate_rows = rows[1:]
    candidate_rows.sort(key=lambda row: as_float(row.get("net_cents")) or -999999.0, reverse=True)
    rows = rows[:1] + candidate_rows
    return {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "live_summary_path": str(LIVE_SUMMARY_JSON),
        "tracker_path": str(TRACKER_JSON),
        "candidate_count": len(candidate_rows),
        "live_net_cents": live_pnl_cents,
        "positive_candidate_count": sum(1 for row in candidate_rows if (as_float(row.get("net_cents")) or 0.0) > 0),
        "target_coverage_positive_count": sum(
            1
            for row in candidate_rows
            if row.get("target_coverage") is True and (as_float(row.get("net_cents")) or 0.0) > 0
        ),
        "live_ready_count": sum(1 for row in candidate_rows if row.get("live_ready") is True),
        "rows": rows,
    }


def write_md(report: dict[str, Any]) -> None:
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8")
    lines = [
        "# v28 Candidate Vs Live PnL Comparison",
        "",
        "Generated from refreshed local artifacts. Candidate rows are shadow/forward research windows; live row is current live-only `score_bot_log.py` output.",
        "",
        f"- Generated UTC: `{report.get('generated_at_utc')}`",
        f"- Candidates: `{report.get('candidate_count')}`",
        f"- Positive candidates: `{report.get('positive_candidate_count')}`",
        f"- Positive target-coverage candidates: `{report.get('target_coverage_positive_count')}`",
        f"- Live-ready candidates: `{report.get('live_ready_count')}`",
        "",
        "| type | gate | policy | entries | settled/rt | W/L | coverage | pnl c | pnl $ | delta vs live c | live ready | target cov | sim share | blockers |",
        "|---|---|---|---:|---:|---:|---:|---:|---:|---:|---|---|---:|---|",
    ]
    for row in report.get("rows") or []:
        blockers = ", ".join(str(item) for item in row.get("blockers") or [])
        lines.append(
            f"| {row.get('type')} | {row.get('gate')} | {row.get('policy')} | "
            f"{row.get('entries') if row.get('entries') is not None else ''} | "
            f"{row.get('settled') if row.get('settled') is not None else ''} | "
            f"{wl(row)} | {fmt_pct(row.get('coverage_pct'))} | {fmt_num(row.get('net_cents'), 0)} | "
            f"{fmt_money_cents(row.get('net_cents'))} | {fmt_num(row.get('delta_vs_live_cents'), 0)} | "
            f"{row.get('live_ready') if row.get('live_ready') is not None else ''} | "
            f"{row.get('target_coverage') if row.get('target_coverage') is not None else ''} | "
            f"{fmt_num(row.get('simulated_share'), 2)} | {blockers} |"
        )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    report = build_report()
    write_md(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
