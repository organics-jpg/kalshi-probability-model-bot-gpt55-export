"""Attribution for FV bridge side accuracy versus realized PnL.

Research-only; no live bot changes or orders.

The FV bridge can be directionally right while realized PnL is damaged by
exit/state handling. This probe compares realized net cents to a simple
hold-to-settlement payoff using the observed executable ask in the source
quality audit.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
SOURCE_JSON = OUT_DIR / "v28_fv_bridge_source_quality_latest.json"
OUT_JSON = OUT_DIR / "v28_fv_bridge_direction_vs_realized_latest.json"
OUT_MD = OUT_DIR / "v28_fv_bridge_direction_vs_realized_latest.md"


def as_float(value: Any) -> float | None:
    if value is None or value == "":
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def load_source() -> dict[str, Any]:
    if not SOURCE_JSON.exists():
        return {}
    try:
        payload = json.loads(SOURCE_JSON.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
    return payload if isinstance(payload, dict) else {}


def hold_net_cents(row: dict[str, Any]) -> float | None:
    ask_prob = as_float(row.get("ask_prob"))
    if ask_prob is None:
        return None
    if row.get("side_won") is True:
        return (1.0 - ask_prob) * 100.0
    if row.get("side_won") is False:
        return -ask_prob * 100.0
    return None


def summarize_rows(rows: list[dict[str, Any]]) -> dict[str, Any]:
    settled_rows = []
    for row in rows:
        if not isinstance(row, dict):
            continue
        realized = as_float(row.get("net_cents"))
        hold = hold_net_cents(row)
        if realized is None or hold is None:
            continue
        enriched = dict(row)
        enriched["hold_net_cents"] = hold
        enriched["exit_vs_hold_cents"] = realized - hold
        settled_rows.append(enriched)

    wins = sum(1 for row in settled_rows if row.get("side_won") is True)
    losses = sum(1 for row in settled_rows if row.get("side_won") is False)
    realized_net = sum(as_float(row.get("net_cents")) or 0.0 for row in settled_rows)
    hold_net = sum(as_float(row.get("hold_net_cents")) or 0.0 for row in settled_rows)
    exit_vs_hold = realized_net - hold_net
    negative_realized_winners = [
        row for row in settled_rows
        if row.get("side_won") is True and (as_float(row.get("net_cents")) or 0.0) < 0.0
    ]
    worst_exit_drag = sorted(
        settled_rows,
        key=lambda row: as_float(row.get("exit_vs_hold_cents")) or 0.0,
    )[:8]
    directional_rate = None
    if settled_rows:
        directional_rate = wins / len(settled_rows)
    return {
        "settled": len(settled_rows),
        "directional_wins": wins,
        "directional_losses": losses,
        "directional_win_rate": directional_rate,
        "realized_net_cents": realized_net,
        "hold_to_settlement_net_cents": hold_net,
        "exit_vs_hold_cents": exit_vs_hold,
        "negative_realized_winners": len(negative_realized_winners),
        "worst_exit_drag": [
            {
                "market": row.get("market"),
                "source": row.get("source"),
                "side": row.get("side"),
                "side_won": row.get("side_won"),
                "ask_prob": row.get("ask_prob"),
                "realized_net_cents": row.get("net_cents"),
                "hold_net_cents": row.get("hold_net_cents"),
                "exit_vs_hold_cents": row.get("exit_vs_hold_cents"),
                "ts_wall": row.get("ts_wall"),
            }
            for row in worst_exit_drag
        ],
    }


def build_report() -> dict[str, Any]:
    payload = load_source()
    windows = []
    for window in payload.get("windows") or []:
        if not isinstance(window, dict):
            continue
        scenarios = []
        for scenario in window.get("scenarios") or []:
            if not isinstance(scenario, dict):
                continue
            rows = scenario.get("rows")
            scenarios.append({
                "scenario": scenario.get("scenario"),
                "summary": summarize_rows(rows if isinstance(rows, list) else []),
            })
        windows.append({
            "window": window.get("window"),
            "freeze_ts_utc": window.get("freeze_ts_utc"),
            "future_denominator": window.get("future_denominator"),
            "scenarios": scenarios,
        })
    interpretation = []
    for window in windows:
        approved = next(
            (row["summary"] for row in window["scenarios"] if row.get("scenario") == "lead_approved_only"),
            {},
        )
        if approved:
            interpretation.append(
                f"{window.get('window')}: approved-only directional {approved.get('directional_wins')}/"
                f"{approved.get('settled')}, realized {approved.get('realized_net_cents')}c, "
                f"hold {approved.get('hold_to_settlement_net_cents')}c, exit-vs-hold {approved.get('exit_vs_hold_cents')}c."
            )
    return {
        "purpose": "Separate FV bridge side accuracy from realized exit/state PnL.",
        "source": str(SOURCE_JSON),
        "requirements": [
            "research-only, no live bot changes, no orders",
            "use existing source-quality rows",
            "compare approved-only and reconstructed/all-source scenarios",
        ],
        "interpretation": interpretation,
        "windows": windows,
    }


def fmt(value: Any) -> str:
    if value is None:
        return "None"
    if isinstance(value, float):
        return f"{value:.3f}"
    return str(value)


def write_md(report: dict[str, Any]) -> None:
    lines = [
        "# v28 FV Bridge Direction vs Realized PnL",
        "",
        "Research-only; no live bot changes and no orders.",
        "",
        "## Current Read",
        "",
    ]
    for note in report.get("interpretation") or []:
        lines.append(f"- {note}")
    for window in report.get("windows") or []:
        lines.extend(["", f"## {window.get('window')}", ""])
        lines.append(
            "| scenario | settled | directional W/L | dir win rate | realized c | hold c | exit-vs-hold c | negative realized winners |"
        )
        lines.append("|---|---:|---:|---:|---:|---:|---:|---:|")
        for scenario in window.get("scenarios") or []:
            summary = scenario.get("summary") or {}
            lines.append(
                f"| `{scenario.get('scenario')}` | {summary.get('settled')} | "
                f"{summary.get('directional_wins')}/{summary.get('directional_losses')} | "
                f"{fmt(summary.get('directional_win_rate'))} | "
                f"{fmt(summary.get('realized_net_cents'))} | "
                f"{fmt(summary.get('hold_to_settlement_net_cents'))} | "
                f"{fmt(summary.get('exit_vs_hold_cents'))} | "
                f"{summary.get('negative_realized_winners')} |"
            )
        lines.extend(["", "### Worst Exit Drag Rows", ""])
        lines.append("| scenario | market | source | side | side won | ask | realized c | hold c | exit-vs-hold c |")
        lines.append("|---|---|---|---|---:|---:|---:|---:|---:|")
        for scenario in window.get("scenarios") or []:
            for row in (scenario.get("summary") or {}).get("worst_exit_drag") or []:
                lines.append(
                    f"| `{scenario.get('scenario')}` | `{row.get('market')}` | `{row.get('source')}` | "
                    f"`{row.get('side')}` | {row.get('side_won')} | {fmt(row.get('ask_prob'))} | "
                    f"{fmt(row.get('realized_net_cents'))} | {fmt(row.get('hold_net_cents'))} | "
                    f"{fmt(row.get('exit_vs_hold_cents'))} |"
                )
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8")
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    report = build_report()
    write_md(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
