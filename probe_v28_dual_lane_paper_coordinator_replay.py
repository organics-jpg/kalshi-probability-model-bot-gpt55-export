"""Paper coordinator replay for v28 vs dual-lane same-window rows.

Research-only. This does not place orders, stop the live bot, or change live
bot behavior. It turns the current same-window comparison into the ledger shape
needed by a future single-process live-test coordinator.
"""
from __future__ import annotations

import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
COMPARE_JSON = OUT_DIR / "v28_dual_lane_same_window_live_compare_latest.json"
OUT_JSON = OUT_DIR / "v28_dual_lane_paper_coordinator_replay_latest.json"
OUT_MD = OUT_DIR / "v28_dual_lane_paper_coordinator_replay_latest.md"


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
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def money(value: Any) -> str:
    cents = fnum(value)
    return f"{cents:.0f}c (${cents / 100.0:.2f})"


def classify(row: dict[str, Any]) -> str:
    live_trades = int(fnum(row.get("live_trade_count")))
    candidate_side = str(row.get("candidate_side") or "")
    live_sides = {item for item in str(row.get("live_sides") or "").split(",") if item}
    if live_trades <= 0:
        return "dual_lane_only"
    if candidate_side and candidate_side in live_sides and len(live_sides) == 1:
        return "same_market_same_side"
    if candidate_side and candidate_side not in live_sides:
        return "same_market_opposite_side"
    if len(live_sides) > 1:
        return "same_market_live_side_flip"
    return "same_market_other"


def build_report() -> dict[str, Any]:
    compare = load_json(COMPARE_JSON)
    rows = [row for row in compare.get("comparison_rows") or [] if isinstance(row, dict)]
    ledger_rows = []
    for row in rows:
        market = str(row.get("market") or "")
        conflict = classify(row)
        ledger_rows.append(
            {
                "market": market,
                "lane": "dual_lane",
                "policy": compare.get("candidate_policy"),
                "side": row.get("candidate_side"),
                "component": row.get("candidate_component"),
                "source": row.get("candidate_source"),
                "virtual_action": "entry_exit_replay",
                "net_cents": row.get("candidate_net_cents"),
                "conflict_class": conflict,
                "paired_live_net_cents": row.get("live_net_cents"),
                "candidate_minus_live_cents": row.get("candidate_minus_live_cents"),
            }
        )
        if int(fnum(row.get("live_trade_count"))) > 0:
            ledger_rows.append(
                {
                    "market": market,
                    "lane": "live_v28",
                    "policy": "mushroom_v28_live_gate_ev_exit_size2",
                    "side": row.get("live_sides"),
                    "component": "actual_live_trades",
                    "source": "live_execution_events",
                    "virtual_action": "actual_live_aggregate",
                    "net_cents": row.get("live_net_cents"),
                    "conflict_class": conflict,
                    "paired_dual_lane_net_cents": row.get("candidate_net_cents"),
                    "dual_lane_minus_live_cents": row.get("candidate_minus_live_cents"),
                }
            )
    by_conflict: dict[str, dict[str, Any]] = {}
    for row in rows:
        conflict = classify(row)
        item = by_conflict.setdefault(
            conflict,
            {
                "markets": 0,
                "dual_lane_net_cents": 0.0,
                "live_net_cents": 0.0,
                "dual_minus_live_cents": 0.0,
            },
        )
        item["markets"] += 1
        item["dual_lane_net_cents"] += fnum(row.get("candidate_net_cents"))
        item["live_net_cents"] += fnum(row.get("live_net_cents"))
        item["dual_minus_live_cents"] += fnum(row.get("candidate_minus_live_cents"))
    conflict_counts = Counter(classify(row) for row in rows)
    hazards = []
    if conflict_counts.get("same_market_opposite_side") or conflict_counts.get("same_market_live_side_flip"):
        hazards.append("same_market_position_attribution_conflict")
    if fnum(compare.get("candidate_minus_live_same_markets_cents")) <= 0:
        hazards.append("dual_lane_underperforms_live_same_window")
    if any(row.get("candidate_source") == "rejected_actionable" for row in rows):
        hazards.append("candidate_contains_reconstructed_or_rejected_rows")
    return {
        "generated_at_utc": utc_now_iso(),
        "promotion_use": "paper_coordinator_replay_only",
        "compare_generated_at_utc": compare.get("generated_at_utc"),
        "candidate_policy": compare.get("candidate_policy"),
        "future_denominator": compare.get("future_denominator"),
        "candidate_summary": compare.get("candidate_summary"),
        "live_same_candidate_markets_summary": compare.get("live_same_candidate_markets_summary"),
        "candidate_minus_live_same_markets_cents": compare.get("candidate_minus_live_same_markets_cents"),
        "conflict_summary": by_conflict,
        "hazards": hazards,
        "ledger_rows": ledger_rows,
        "read": [
            "This is the ledger shape needed before live dual-lane can trade alongside v28.",
            "Rows are replay/paper rows, not live orders.",
            "Same-market same-side rows could be coordinated as shared exposure; side-flip/opposite-side rows require explicit arbitration.",
        ],
    }


def write_outputs(report: dict[str, Any]) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8")
    candidate = report.get("candidate_summary") if isinstance(report.get("candidate_summary"), dict) else {}
    live = (
        report.get("live_same_candidate_markets_summary")
        if isinstance(report.get("live_same_candidate_markets_summary"), dict)
        else {}
    )
    lines = [
        "# v28 Dual-Lane Paper Coordinator Replay",
        "",
        "Research-only. No orders placed, no live bot stopped, no live bot logic changed.",
        "",
        f"- Generated UTC: `{report.get('generated_at_utc')}`",
        f"- Promotion use: `{report.get('promotion_use')}`",
        f"- Same-window compare UTC: `{report.get('compare_generated_at_utc')}`",
        f"- Candidate policy: `{report.get('candidate_policy')}`",
        "",
        "## Read",
        "",
    ]
    lines.extend(f"- {item}" for item in report.get("read") or [])
    lines.extend(
        [
            "",
            "## Summary",
            "",
            f"- Dual-lane W/L/net: `{candidate.get('wins')}/{candidate.get('losses')}` / `{money(candidate.get('net_cents'))}`",
            f"- Live v28 same-market W/L/net: `{live.get('wins')}/{live.get('losses')}` / `{money(live.get('net_cents'))}`",
            f"- Dual-lane minus live: `{money(report.get('candidate_minus_live_same_markets_cents'))}`",
            f"- Hazards: `{', '.join(report.get('hazards') or []) or 'none'}`",
            "",
            "## Conflict Summary",
            "",
            "| conflict | markets | dual-lane net | live net | dual-live |",
            "|---|---:|---:|---:|---:|",
        ]
    )
    for conflict, item in sorted((report.get("conflict_summary") or {}).items()):
        lines.append(
            f"| `{conflict}` | {item.get('markets')} | {money(item.get('dual_lane_net_cents'))} | "
            f"{money(item.get('live_net_cents'))} | {money(item.get('dual_minus_live_cents'))} |"
        )
    lines.extend(
        [
            "",
            "## Ledger Preview",
            "",
            "| lane | market | side | source | conflict | net | paired delta |",
            "|---|---|---|---|---|---:|---:|",
        ]
    )
    for row in (report.get("ledger_rows") or [])[:30]:
        paired = row.get("candidate_minus_live_cents")
        if paired is None:
            paired = row.get("dual_lane_minus_live_cents")
        lines.append(
            f"| `{row.get('lane')}` | `{row.get('market')}` | {row.get('side')} | "
            f"{row.get('source')} | `{row.get('conflict_class')}` | {money(row.get('net_cents'))} | {money(paired)} |"
        )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    report = build_report()
    write_outputs(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
