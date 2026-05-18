"""Stack the lead FV bridge with geometry-aware reduce-exit suppression.

Research-only; no live bot changes or orders.

This answers a practical question: if the FV bridge chooses good sides but v28
probability_reduce clips winners, how much of the bridge's apparent weakness is
exit monetization rather than side-probability error?
"""
from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
BRIDGE_SOURCE_JSON = OUT_DIR / "v28_fv_bridge_source_quality_latest.json"
EXIT_ROWS_JSON = OUT_DIR / "v28_frozen_exit_reduce_suppression_latest.json"
OUT_JSON = OUT_DIR / "v28_fv_bridge_exit_geometry_stack_latest.json"
OUT_MD = OUT_DIR / "v28_fv_bridge_exit_geometry_stack_latest.md"

P_HOLD_FLOOR = 0.75
MAX_MATCH_SECONDS = 240.0


def as_float(value: Any) -> float | None:
    if value is None or value == "":
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def parse_ts(value: Any) -> datetime | None:
    if not isinstance(value, str) or not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None


def load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
    return payload if isinstance(payload, dict) else {}


def side_won(row: dict[str, Any]) -> bool | None:
    side = str(row.get("side") or "").lower()
    result = str(row.get("result") or "").lower()
    if side not in {"yes", "no"} or result not in {"yes", "no"}:
        return None
    return side == result


def hold_net_cents(row: dict[str, Any]) -> float | None:
    ask_prob = as_float(row.get("ask_prob"))
    if ask_prob is None:
        return None
    if row.get("side_won") is True:
        return (1.0 - ask_prob) * 100.0
    if row.get("side_won") is False:
        return -ask_prob * 100.0
    return None


def suppress_geometry(exit_row: dict[str, Any]) -> bool:
    if str(exit_row.get("exit_reason") or "") != "mushroom_v28_probability_reduce":
        return False
    if (as_float(exit_row.get("p_hold")) or 0.0) < P_HOLD_FLOOR:
        return False
    side = str(exit_row.get("side") or "").lower()
    drawdown = as_float(exit_row.get("fair_drawdown_cents"))
    if drawdown is None:
        return False
    if side == "yes":
        return drawdown >= 0.0
    if side == "no":
        return drawdown <= 0.0
    return False


def indexed_exit_rows(payload: dict[str, Any]) -> dict[tuple[str, str], list[dict[str, Any]]]:
    out: dict[tuple[str, str], list[dict[str, Any]]] = {}
    for row in payload.get("rows") or []:
        if not isinstance(row, dict):
            continue
        market = str(row.get("market") or "")
        side = str(row.get("side") or "").lower()
        entry_ts = parse_ts(row.get("entry_ts"))
        if not market or side not in {"yes", "no"} or entry_ts is None:
            continue
        enriched = dict(row)
        enriched["_entry_dt"] = entry_ts
        out.setdefault((market, side), []).append(enriched)
    for rows in out.values():
        rows.sort(key=lambda row: row["_entry_dt"])
    return out


def match_exit_row(
    bridge_row: dict[str, Any],
    exit_index: dict[tuple[str, str], list[dict[str, Any]]],
    used: set[int],
) -> dict[str, Any] | None:
    market = str(bridge_row.get("market") or "")
    side = str(bridge_row.get("side") or "").lower()
    ts = parse_ts(bridge_row.get("ts_wall"))
    if not market or side not in {"yes", "no"} or ts is None:
        return None
    candidates = exit_index.get((market, side)) or []
    best: tuple[float, int, dict[str, Any]] | None = None
    for idx, row in enumerate(candidates):
        row_id = id(row)
        if row_id in used:
            continue
        delta = abs((row["_entry_dt"] - ts).total_seconds())
        if delta > MAX_MATCH_SECONDS:
            continue
        if best is None or delta < best[0]:
            best = (delta, idx, row)
    if best is None:
        return None
    used.add(id(best[2]))
    matched = dict(best[2])
    matched["_match_seconds"] = best[0]
    return matched


def bridge_windows(payload: dict[str, Any]) -> list[dict[str, Any]]:
    return [window for window in payload.get("windows") or [] if isinstance(window, dict)]


def score_scenario(scenario: dict[str, Any], exit_index: dict[tuple[str, str], list[dict[str, Any]]]) -> dict[str, Any]:
    rows = scenario.get("rows")
    used: set[int] = set()
    scored_rows = []
    for row in rows if isinstance(rows, list) else []:
        if not isinstance(row, dict):
            continue
        current = as_float(row.get("net_cents"))
        hold = hold_net_cents(row)
        if current is None or hold is None:
            continue
        match = match_exit_row(row, exit_index, used)
        stack = current
        stack_delta = 0.0
        suppressed = False
        match_reason = None
        if match is not None:
            match_reason = match.get("exit_reason")
            match_current = as_float(match.get("current_cents"))
            match_hold = as_float(match.get("hold_cents"))
            if match_current is not None and match_hold is not None and suppress_geometry(match):
                suppressed = True
                stack_delta = match_hold - match_current
                stack = current + stack_delta
        scored_rows.append({
            "market": row.get("market"),
            "source": row.get("source"),
            "side": row.get("side"),
            "side_won": row.get("side_won"),
            "ask_prob": row.get("ask_prob"),
            "realized_net_cents": current,
            "hold_net_cents": hold,
            "stack_net_cents": stack,
            "stack_delta_cents": stack_delta,
            "matched_exit": match is not None,
            "matched_exit_reason": match_reason,
            "matched_seconds": None if match is None else match.get("_match_seconds"),
            "geometry_suppressed_reduce": suppressed,
        })
    directional_wins = sum(1 for row in scored_rows if row.get("side_won") is True)
    directional_losses = sum(1 for row in scored_rows if row.get("side_won") is False)
    realized = sum(row["realized_net_cents"] for row in scored_rows)
    hold = sum(row["hold_net_cents"] for row in scored_rows)
    stack = sum(row["stack_net_cents"] for row in scored_rows)
    return {
        "scenario": scenario.get("scenario"),
        "entries": scenario.get("entries"),
        "settled": len(scored_rows),
        "coverage_pct": scenario.get("coverage_pct"),
        "directional_wins": directional_wins,
        "directional_losses": directional_losses,
        "directional_win_rate": None if not scored_rows else directional_wins / len(scored_rows),
        "realized_net_cents": realized,
        "hold_to_settlement_net_cents": hold,
        "stack_net_cents": stack,
        "stack_delta_vs_realized_cents": stack - realized,
        "exit_vs_hold_cents": realized - hold,
        "stack_vs_hold_cents": stack - hold,
        "matched_rows": sum(1 for row in scored_rows if row.get("matched_exit")),
        "geometry_suppressed_rows": sum(1 for row in scored_rows if row.get("geometry_suppressed_reduce")),
        "negative_realized_winners": sum(
            1 for row in scored_rows
            if row.get("side_won") is True and (as_float(row.get("realized_net_cents")) or 0.0) < 0
        ),
        "negative_stack_winners": sum(
            1 for row in scored_rows
            if row.get("side_won") is True and (as_float(row.get("stack_net_cents")) or 0.0) < 0
        ),
        "rows": scored_rows,
        "blockers": scenario.get("blockers") or [],
    }


def build_report() -> dict[str, Any]:
    bridge_payload = load_json(BRIDGE_SOURCE_JSON)
    exit_payload = load_json(EXIT_ROWS_JSON)
    exit_index = indexed_exit_rows(exit_payload)
    windows = []
    for window in bridge_windows(bridge_payload):
        scored_scenarios = []
        for scenario in window.get("scenarios") or []:
            if isinstance(scenario, dict):
                scored_scenarios.append(score_scenario(scenario, exit_index))
        windows.append({
            "window": window.get("window"),
            "freeze_ts_utc": window.get("freeze_ts_utc"),
            "future_denominator": window.get("future_denominator"),
            "scenarios": scored_scenarios,
        })
    interpretation = []
    for window in windows:
        approved = next((s for s in window["scenarios"] if s.get("scenario") == "lead_approved_only"), None)
        if approved:
            interpretation.append(
                f"{window.get('window')}: approved-only realized {approved.get('realized_net_cents')}c, "
                f"stack {approved.get('stack_net_cents')}c, hold {approved.get('hold_to_settlement_net_cents')}c, "
                f"matched {approved.get('matched_rows')}/{approved.get('settled')}, suppressed {approved.get('geometry_suppressed_rows')}."
            )
    return {
        "purpose": "Measure the lead FV bridge with geometry-aware reduce-exit suppression applied to matched actual trades.",
        "requirements": [
            "research-only, no live bot changes, no orders",
            "approved-only source rows must remain visible",
            "matched exit rows only; unmatched rows keep original realized PnL",
            "diagnostic stack result is not promotion evidence without frozen forward rows",
        ],
        "bridge_source": str(BRIDGE_SOURCE_JSON),
        "exit_source": str(EXIT_ROWS_JSON),
        "p_hold_floor": P_HOLD_FLOOR,
        "max_match_seconds": MAX_MATCH_SECONDS,
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
        "# v28 FV Bridge + Exit Geometry Stack",
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
        lines.append("| scenario | settled | coverage | dir W/L | realized c | stack c | hold c | stack-realized c | stack-hold c | matched | suppressed | neg winners current/stack |")
        lines.append("|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|")
        for scenario in window.get("scenarios") or []:
            lines.append(
                f"| `{scenario.get('scenario')}` | {scenario.get('settled')} | "
                f"{fmt(scenario.get('coverage_pct'))} | "
                f"{scenario.get('directional_wins')}/{scenario.get('directional_losses')} | "
                f"{fmt(scenario.get('realized_net_cents'))} | {fmt(scenario.get('stack_net_cents'))} | "
                f"{fmt(scenario.get('hold_to_settlement_net_cents'))} | "
                f"{fmt(scenario.get('stack_delta_vs_realized_cents'))} | "
                f"{fmt(scenario.get('stack_vs_hold_cents'))} | "
                f"{scenario.get('matched_rows')} | {scenario.get('geometry_suppressed_rows')} | "
                f"{scenario.get('negative_realized_winners')}/{scenario.get('negative_stack_winners')} |"
            )
        lines.extend(["", "### Suppressed Matched Rows", ""])
        lines.append("| scenario | market | source | side | side won | realized c | stack c | delta c | exit reason | match sec |")
        lines.append("|---|---|---|---|---:|---:|---:|---:|---|---:|")
        for scenario in window.get("scenarios") or []:
            for row in scenario.get("rows") or []:
                if not row.get("geometry_suppressed_reduce"):
                    continue
                lines.append(
                    f"| `{scenario.get('scenario')}` | `{row.get('market')}` | `{row.get('source')}` | "
                    f"`{row.get('side')}` | {row.get('side_won')} | "
                    f"{fmt(row.get('realized_net_cents'))} | {fmt(row.get('stack_net_cents'))} | "
                    f"{fmt(row.get('stack_delta_cents'))} | `{row.get('matched_exit_reason')}` | "
                    f"{fmt(row.get('matched_seconds'))} |"
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
