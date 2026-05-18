"""Feature-gate exit/state repair frontier.

Research-only; no live bot changes or orders.

This probe takes the frozen feature-gate selected-side live entries and tests
market-level exit suppression counterfactuals. The goal is not to declare a
deployable exit rule, but to identify which physical exit failure modes deserve
the next frozen shadow implementation.
"""
from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
ALIGNMENT_JSON = OUT_DIR / "v28_feature_gate_live_outcome_alignment_latest.json"
TRADES_CSV = ROOT / "stats" / "live_mushroom_v28_size2" / "trades.csv"
EXECUTION_EVENTS = ROOT / "logs" / "live_mushroom_v28_size2" / "execution_events.ndjson"
OUT_JSON = OUT_DIR / "v28_feature_gate_exit_state_repair_frontier_latest.json"
OUT_MD = OUT_DIR / "v28_feature_gate_exit_state_repair_frontier_latest.md"

TARGET_CANDIDATE = "post_feature_freeze_entry_raw03_recross70_abs075"


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
    if value is None or value == "":
        return default
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def maybe_fnum(value: Any) -> float | None:
    if value is None or value == "":
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def load_trades(path: Path, markets: set[str]) -> dict[str, list[dict[str, Any]]]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    if not path.exists():
        return grouped
    with path.open("r", encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle):
            market = str(row.get("market") or "")
            if market in markets:
                grouped[market].append(row)
    return grouped


def load_events(path: Path, markets: set[str]) -> dict[str, list[dict[str, Any]]]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    if not path.exists():
        return grouped
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            if not line.strip():
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError:
                continue
            market = str(row.get("market") or "")
            if market in markets:
                grouped[market].append(row)
    for market in grouped:
        grouped[market].sort(key=lambda row: str(row.get("ts_wall") or ""))
    return grouped


def target_rows(payload: dict[str, Any]) -> list[dict[str, Any]]:
    for variant in payload.get("variants") or []:
        if variant.get("candidate") == TARGET_CANDIDATE:
            return [row for row in variant.get("rows") or [] if isinstance(row, dict)]
    return []


def selected_side_trades(trades: list[dict[str, Any]], side: str) -> list[dict[str, Any]]:
    return [row for row in trades if str(row.get("side") or "") == side]


def qty(trades: list[dict[str, Any]]) -> float:
    return sum(fnum(row.get("qty")) for row in trades)


def live_net_cents(trades: list[dict[str, Any]]) -> float:
    return sum(100.0 * fnum(row.get("net_pnl_dollars")) for row in trades)


def hold_net_for_trade(row: dict[str, Any], side_won: bool) -> float:
    quantity = fnum(row.get("qty"))
    entry = fnum(row.get("entry_fill_cents_used"))
    entry_fee = fnum(row.get("entry_fee_cents"))
    exit_fee = fnum(row.get("exit_fee_cents"))
    settlement_value = 100.0 if side_won else 0.0
    return quantity * (settlement_value - entry) - entry_fee - exit_fee


def hold_net_cents(trades: list[dict[str, Any]], side_won: bool) -> float:
    return sum(hold_net_for_trade(row, side_won) for row in trades)


def first_text(rows: list[dict[str, Any]], field: str) -> str | None:
    values = sorted(str(row.get(field) or "") for row in rows if row.get(field))
    return values[0] if values else None


def last_text(rows: list[dict[str, Any]], field: str) -> str | None:
    values = sorted(str(row.get(field) or "") for row in rows if row.get(field))
    return values[-1] if values else None


def exit_reason(row: dict[str, Any]) -> str:
    return str(
        row.get("mushroom_v28_exit_reason")
        or row.get("decision_reason")
        or row.get("stop_tier")
        or ""
    )


def reason_family(reason: str) -> str | None:
    if "value_over_hold" in reason:
        return "value_over_hold"
    if "probability_reduce" in reason:
        return "probability_reduce"
    if "probability_collapse" in reason:
        return "probability_collapse"
    return None


def exit_events(events: list[dict[str, Any]], side: str) -> list[dict[str, Any]]:
    out = []
    for row in events:
        event_type = str(row.get("event_type") or "")
        client_order_id = str(row.get("client_order_id") or "")
        if "exit" not in event_type and not client_order_id.startswith("btc15m-exit"):
            continue
        if str(row.get("side") or "") != side:
            continue
        if not exit_reason(row):
            continue
        out.append(row)
    return out


def selected_event_features(events: list[dict[str, Any]]) -> dict[str, Any]:
    by_family: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in events:
        family = reason_family(exit_reason(row))
        if family:
            by_family[family].append(row)

    max_p_hold = None
    min_drawdown = None
    families = sorted(by_family)
    family_stats = {}
    for family, rows in by_family.items():
        p_holds = [maybe_fnum(row.get("mushroom_v28_p_hold")) for row in rows]
        p_holds = [value for value in p_holds if value is not None]
        drawdowns = [maybe_fnum(row.get("mushroom_v28_fair_drawdown_cents")) for row in rows]
        drawdowns = [value for value in drawdowns if value is not None]
        family_stats[family] = {
            "events": len(rows),
            "max_p_hold": max(p_holds) if p_holds else None,
            "min_fair_drawdown_cents": min(drawdowns) if drawdowns else None,
        }
        if p_holds:
            max_p_hold = max(max_p_hold or 0.0, max(p_holds))
        if drawdowns:
            min_drawdown = min(drawdowns) if min_drawdown is None else min(min_drawdown, min(drawdowns))

    return {
        "families": families,
        "family_stats": family_stats,
        "max_p_hold": max_p_hold,
        "min_fair_drawdown_cents": min_drawdown,
        "exit_event_count": len(events),
        "reason_counts": dict(Counter(exit_reason(row) for row in events if exit_reason(row))),
    }


def market_row(align: dict[str, Any], trades: list[dict[str, Any]], events: list[dict[str, Any]]) -> dict[str, Any]:
    side = str(align.get("side") or "")
    selected = selected_side_trades(trades, side)
    selected_events = exit_events(events, side)
    side_won = bool(align.get("side_won"))
    selected_live = live_net_cents(selected)
    selected_hold = hold_net_cents(selected, side_won)
    features = selected_event_features(selected_events)
    return {
        "market": align.get("market"),
        "source": align.get("source"),
        "side": side,
        "side_won": side_won,
        "theory_net_cents": fnum(align.get("theory_net_cents")),
        "selected_side_qty": qty(selected),
        "selected_side_trade_count": len(selected),
        "selected_entry_ts_min": first_text(selected, "entry_ts"),
        "selected_exit_ts_max": last_text(selected, "exit_ts"),
        "live_net_cents": selected_live,
        "hold_net_cents": selected_hold,
        "hold_delta_cents": selected_hold - selected_live,
        "families": features["families"],
        "family_stats": features["family_stats"],
        "max_p_hold": features["max_p_hold"],
        "min_fair_drawdown_cents": features["min_fair_drawdown_cents"],
        "exit_event_count": features["exit_event_count"],
        "reason_counts": features["reason_counts"],
    }


def has_family(row: dict[str, Any], family: str) -> bool:
    return family in set(row.get("families") or [])


def has_any_family(row: dict[str, Any], families: set[str]) -> bool:
    return bool(set(row.get("families") or []) & families)


def phold_at_least(row: dict[str, Any], threshold: float) -> bool:
    value = row.get("max_p_hold")
    return value is not None and fnum(value) >= threshold


def drawdown_at_most(row: dict[str, Any], threshold: float) -> bool:
    value = row.get("min_fair_drawdown_cents")
    return value is not None and fnum(value) <= threshold


def source_is(row: dict[str, Any], source: str) -> bool:
    return str(row.get("source") or "") == source


def selected(row: dict[str, Any]) -> bool:
    return fnum(row.get("selected_side_qty")) > 0


Predicate = Callable[[dict[str, Any]], bool]


VARIANTS: list[tuple[str, str, Predicate]] = [
    ("baseline_live", "Actual live selected-side exits/state on feature-gate rows.", lambda row: False),
    ("hold_all_selected_oracle", "Oracle bound: hold every selected-side live entry to settlement.", lambda row: selected(row)),
    (
        "hold_approved_entry_source_oracle",
        "Source-quality diagnostic: hold only rows labelled approved_entry.",
        lambda row: selected(row) and source_is(row, "approved_entry"),
    ),
    (
        "hold_rejected_actionable_source_oracle",
        "Source-quality diagnostic: hold only rows labelled rejected_actionable.",
        lambda row: selected(row) and source_is(row, "rejected_actionable"),
    ),
    (
        "suppress_value_over_hold",
        "Suppress value_over_hold exits on selected feature-gate rows.",
        lambda row: selected(row) and has_family(row, "value_over_hold"),
    ),
    (
        "suppress_probability_reduce",
        "Suppress probability_reduce exits on selected feature-gate rows.",
        lambda row: selected(row) and has_family(row, "probability_reduce"),
    ),
    (
        "suppress_probability_collapse",
        "Suppress probability_collapse exits on selected feature-gate rows.",
        lambda row: selected(row) and has_family(row, "probability_collapse"),
    ),
    (
        "suppress_value_or_reduce",
        "Suppress value_over_hold or probability_reduce exits on selected feature-gate rows.",
        lambda row: selected(row) and has_any_family(row, {"value_over_hold", "probability_reduce"}),
    ),
    (
        "suppress_any_exit_family",
        "Suppress any recognized v28 exit family on selected feature-gate rows.",
        lambda row: selected(row) and has_any_family(
            row, {"value_over_hold", "probability_reduce", "probability_collapse"}
        ),
    ),
    (
        "suppress_value_or_reduce_p_hold80",
        "Suppress value/reduce exits only when observed p_hold reached 0.80+.",
        lambda row: selected(row)
        and has_any_family(row, {"value_over_hold", "probability_reduce"})
        and phold_at_least(row, 0.80),
    ),
    (
        "suppress_value_or_reduce_p_hold85",
        "Suppress value/reduce exits only when observed p_hold reached 0.85+.",
        lambda row: selected(row)
        and has_any_family(row, {"value_over_hold", "probability_reduce"})
        and phold_at_least(row, 0.85),
    ),
    (
        "suppress_value_or_reduce_shallow_dd5",
        "Suppress value/reduce exits only when fair drawdown was <=5c.",
        lambda row: selected(row)
        and has_any_family(row, {"value_over_hold", "probability_reduce"})
        and drawdown_at_most(row, 5.0),
    ),
    (
        "approved_suppress_value_or_reduce",
        "Source diagnostic: suppress value/reduce only on approved_entry rows.",
        lambda row: selected(row)
        and source_is(row, "approved_entry")
        and has_any_family(row, {"value_over_hold", "probability_reduce"}),
    ),
    (
        "approved_suppress_any_exit_family",
        "Source diagnostic: suppress any recognized exit only on approved_entry rows.",
        lambda row: selected(row)
        and source_is(row, "approved_entry")
        and has_any_family(row, {"value_over_hold", "probability_reduce", "probability_collapse"}),
    ),
]


def variant_summary(rows: list[dict[str, Any]], name: str, description: str, predicate: Predicate) -> dict[str, Any]:
    selected_rows = [row for row in rows if selected(row)]
    suppressed = [row for row in selected_rows if predicate(row)]
    simulated_net = sum(
        fnum(row.get("hold_net_cents")) if predicate(row) else fnum(row.get("live_net_cents"))
        for row in selected_rows
    )
    baseline_net = sum(fnum(row.get("live_net_cents")) for row in selected_rows)
    hold_all_net = sum(fnum(row.get("hold_net_cents")) for row in selected_rows)
    losers_suppressed = [row for row in suppressed if not row.get("side_won")]
    winners_suppressed = [row for row in suppressed if row.get("side_won")]
    return {
        "variant": name,
        "description": description,
        "selected_side_live_traded_markets": len(selected_rows),
        "suppressed_markets": len(suppressed),
        "suppressed_winners": len(winners_suppressed),
        "suppressed_losers": len(losers_suppressed),
        "simulated_net_cents": simulated_net,
        "baseline_live_net_cents": baseline_net,
        "hold_all_oracle_net_cents": hold_all_net,
        "delta_vs_baseline_cents": simulated_net - baseline_net,
        "delta_vs_hold_all_oracle_cents": simulated_net - hold_all_net,
        "worst_market_cents": min([fnum(row.get("hold_net_cents")) if predicate(row) else fnum(row.get("live_net_cents")) for row in selected_rows] or [0.0]),
        "source_counts": dict(Counter(str(row.get("source") or "unknown") for row in suppressed)),
        "family_counts": dict(Counter(family for row in suppressed for family in row.get("families") or [])),
        "blockers": [
            "diagnostic_counterfactual_uses_settlement_outcomes",
            "selected_side_live_subset_only",
            "not_frozen_forward_shadow_policy",
            *([] if len(selected_rows) >= 30 else ["selected_side_rows_lt_30"]),
        ],
    }


def build_report() -> dict[str, Any]:
    alignment = load_json(ALIGNMENT_JSON)
    rows = target_rows(alignment)
    markets = {str(row.get("market") or "") for row in rows if row.get("market")}
    trades = load_trades(TRADES_CSV, markets)
    events = load_events(EXECUTION_EVENTS, markets)
    market_rows = [
        market_row(row, trades.get(str(row.get("market") or ""), []), events.get(str(row.get("market") or ""), []))
        for row in rows
    ]
    market_rows.sort(key=lambda row: fnum(row.get("hold_delta_cents")), reverse=True)
    variants = [
        variant_summary(market_rows, name, description, predicate)
        for name, description, predicate in VARIANTS
    ]
    variants.sort(key=lambda row: fnum(row.get("simulated_net_cents")), reverse=True)
    baseline = next(row for row in variants if row["variant"] == "baseline_live")
    best = variants[0] if variants else {}
    interpretation = [
        "Research-only frontier; it does not change live exits or place orders.",
        (
            f"Baseline selected-side live PnL is {baseline.get('simulated_net_cents')}c across "
            f"{baseline.get('selected_side_live_traded_markets')} traded feature-gate markets."
        ),
        (
            f"Best diagnostic variant is {best.get('variant')} at {best.get('simulated_net_cents')}c, "
            f"delta {best.get('delta_vs_baseline_cents')}c versus actual live selected-side exits."
        ),
        (
            "Rows remain non-deployable from this report alone because the simulation uses settlement "
            "outcomes and only covers live selected-side overlap."
        ),
    ]
    return {
        "generated_at_utc": utc_now_iso(),
        "target_candidate": TARGET_CANDIDATE,
        "alignment_source": str(ALIGNMENT_JSON),
        "trades_source": str(TRADES_CSV),
        "execution_events_source": str(EXECUTION_EVENTS),
        "interpretation": interpretation,
        "variants": variants,
        "markets": market_rows,
    }


def fmt(value: Any) -> str:
    if value is None:
        return "n/a"
    if isinstance(value, float):
        return f"{value:.2f}"
    return str(value)


def write_md(report: dict[str, Any]) -> None:
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8")
    lines = [
        "# v28 Feature-Gate Exit/State Repair Frontier",
        "",
        "Research-only diagnostic. No live bot changes or orders.",
        "",
        f"- Generated UTC: `{report.get('generated_at_utc')}`",
        f"- Candidate: `{report.get('target_candidate')}`",
        "",
        "## Interpretation",
        "",
    ]
    lines.extend(f"- {note}" for note in report.get("interpretation") or [])
    lines.extend(
        [
            "",
            "## Exit Suppression Frontier",
            "",
            "| variant | sim net c | delta live c | delta hold-all c | suppressed | W/L suppressed | worst market c | source counts | family counts | blockers |",
            "|---|---:|---:|---:|---:|---:|---:|---|---|---|",
        ]
    )
    for row in report.get("variants") or []:
        lines.append(
            f"| `{row.get('variant')}` | {fmt(row.get('simulated_net_cents'))} | "
            f"{fmt(row.get('delta_vs_baseline_cents'))} | {fmt(row.get('delta_vs_hold_all_oracle_cents'))} | "
            f"{row.get('suppressed_markets')} | {row.get('suppressed_winners')}/{row.get('suppressed_losers')} | "
            f"{fmt(row.get('worst_market_cents'))} | `{row.get('source_counts')}` | "
            f"`{row.get('family_counts')}` | {', '.join(row.get('blockers') or [])} |"
        )
    lines.extend(
        [
            "",
            "## Largest Hold Deltas",
            "",
            "| market | source | side | won | live c | hold c | hold delta c | p_hold max | drawdown min | families |",
            "|---|---|---|---:|---:|---:|---:|---:|---:|---|",
        ]
    )
    for row in (report.get("markets") or [])[:20]:
        if not selected(row):
            continue
        lines.append(
            f"| {row.get('market')} | {row.get('source')} | {row.get('side')} | {row.get('side_won')} | "
            f"{fmt(row.get('live_net_cents'))} | {fmt(row.get('hold_net_cents'))} | "
            f"{fmt(row.get('hold_delta_cents'))} | {fmt(row.get('max_p_hold'))} | "
            f"{fmt(row.get('min_fair_drawdown_cents'))} | {', '.join(row.get('families') or [])} |"
        )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    report = build_report()
    write_md(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
