"""Observable separator audit for feature-gate live exit suppression.

Research-only; no live bot changes or orders.

The hold counterfactual says live exits both save losing markets and clip
winning markets. This probe searches simple observable market-level separators
on the feature-gate selected-side live trades to identify which exit contexts
look suppressible versus true loss-control exits. Any candidate found here is
diagnostic only and must be frozen before it counts as evidence.
"""
from __future__ import annotations

import json
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from statistics import mean
from typing import Any


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
COUNTERFACTUAL_JSON = OUT_DIR / "v28_feature_gate_live_exit_hold_counterfactual_latest.json"
EXECUTION_EVENTS = ROOT / "logs" / "live_mushroom_v28_size2" / "execution_events.ndjson"
OUT_JSON = OUT_DIR / "v28_feature_gate_exit_suppression_separator_latest.json"
OUT_MD = OUT_DIR / "v28_feature_gate_exit_suppression_separator_latest.md"

FEATURES = [
    "theory_net_cents",
    "entry_fill_avg_cents",
    "exit_fill_avg_cents",
    "entry_to_exit_price_delta",
    "selected_side_qty",
    "selected_side_trade_count",
    "exit_event_count",
    "exit_signal_count",
    "exit_p_hold_min",
    "exit_p_hold_avg",
    "exit_p_hold_max",
    "exit_fair_drawdown_min",
    "exit_fair_drawdown_avg",
    "exit_fair_drawdown_max",
    "exit_hold_net_min",
    "exit_hold_net_avg",
    "exit_hold_net_max",
    "exit_bid_min",
    "exit_bid_avg",
    "exit_bid_max",
    "exit_depth_min",
    "exit_depth_avg",
    "exit_book_age_max",
    "reason_probability_reduce_share",
    "reason_value_over_hold_share",
    "reason_probability_collapse_share",
]

OBSERVABLE_SEPARATOR_FEATURES = [
    "entry_fill_avg_cents",
    "selected_side_qty",
    "selected_side_trade_count",
    "exit_signal_count",
    "exit_p_hold_min",
    "exit_p_hold_avg",
    "exit_p_hold_max",
    "exit_fair_drawdown_min",
    "exit_fair_drawdown_avg",
    "exit_fair_drawdown_max",
    "exit_hold_net_min",
    "exit_hold_net_avg",
    "exit_hold_net_max",
    "exit_bid_min",
    "exit_bid_avg",
    "exit_bid_max",
    "exit_depth_min",
    "exit_depth_avg",
    "exit_book_age_max",
    "reason_probability_reduce_share",
    "reason_value_over_hold_share",
    "reason_probability_collapse_share",
]


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


def maybe_float(value: Any) -> float | None:
    if value is None or value == "":
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


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


def event_exit_reason(row: dict[str, Any]) -> str:
    return str(
        row.get("mushroom_v28_exit_reason")
        or row.get("decision_reason")
        or row.get("stop_tier")
        or ""
    )


def selected_exit_events(events: list[dict[str, Any]], side: str) -> list[dict[str, Any]]:
    out = []
    for row in events:
        event_type = str(row.get("event_type") or "")
        if "exit" not in event_type and not str(row.get("client_order_id") or "").startswith("btc15m-exit"):
            continue
        if str(row.get("side") or "") != side:
            continue
        out.append(row)
    return out


def signal_events(events: list[dict[str, Any]], side: str) -> list[dict[str, Any]]:
    return [
        row for row in selected_exit_events(events, side)
        if str(row.get("event_type") or "") in {"exit_signal_seen", "exit_snapshot_built", "exit_plan_built"}
    ]


def stat(values: list[float], mode: str) -> float | None:
    if not values:
        return None
    if mode == "min":
        return min(values)
    if mode == "max":
        return max(values)
    return mean(values)


def values(rows: list[dict[str, Any]], key: str) -> list[float]:
    return [value for value in (maybe_float(row.get(key)) for row in rows) if value is not None]


def reason_share(reason_counts: dict[str, Any], token: str) -> float:
    total = sum(int(count or 0) for count in reason_counts.values())
    if not total:
        return 0.0
    matched = sum(int(count or 0) for reason, count in reason_counts.items() if token in str(reason))
    return matched / total


def compact_market(row: dict[str, Any], events: list[dict[str, Any]]) -> dict[str, Any] | None:
    if fnum(row.get("selected_side_qty")) <= 0:
        return None
    delta = fnum(row.get("exit_delta_vs_hold_cents"))
    if delta == 0:
        return None
    side = str(row.get("side") or "")
    signals = signal_events(events, side)
    reason_counts = row.get("exit_reason_counts") if isinstance(row.get("exit_reason_counts"), dict) else {}
    out = {
        "market": row.get("market"),
        "source": row.get("source"),
        "side": side,
        "side_won": row.get("side_won"),
        "exit_delta_vs_hold_cents": delta,
        "suppression_delta_cents": -delta,
        "suppress_would_help": delta < 0,
        "theory_net_cents": fnum(row.get("theory_net_cents")),
        "entry_fill_avg_cents": maybe_float(row.get("entry_fill_avg_cents")),
        "exit_fill_avg_cents": maybe_float(row.get("exit_fill_avg_cents")),
        "selected_side_qty": fnum(row.get("selected_side_qty")),
        "selected_side_trade_count": fnum(row.get("selected_side_trade_count")),
        "exit_event_count": fnum(row.get("exit_event_count")),
        "exit_signal_count": len(signals),
        "reason_probability_reduce_share": reason_share(reason_counts, "probability_reduce"),
        "reason_value_over_hold_share": reason_share(reason_counts, "value_over_hold"),
        "reason_probability_collapse_share": reason_share(reason_counts, "probability_collapse"),
        "exit_reason_counts": reason_counts,
    }
    entry = maybe_float(out.get("entry_fill_avg_cents"))
    exit_fill = maybe_float(out.get("exit_fill_avg_cents"))
    out["entry_to_exit_price_delta"] = None if entry is None or exit_fill is None else exit_fill - entry
    p_hold = values(signals, "mushroom_v28_p_hold")
    drawdown = values(signals, "mushroom_v28_fair_drawdown_cents")
    hold_net = values(signals, "mushroom_v28_hold_net_cents")
    bid = values(signals, "mushroom_v28_exit_bid_cents")
    depth = values(signals, "eligible_depth")
    book_age = values(signals, "book_age_ms")
    for prefix, vals in [
        ("exit_p_hold", p_hold),
        ("exit_fair_drawdown", drawdown),
        ("exit_hold_net", hold_net),
        ("exit_bid", bid),
        ("exit_depth", depth),
    ]:
        out[f"{prefix}_min"] = stat(vals, "min")
        out[f"{prefix}_avg"] = stat(vals, "avg")
        out[f"{prefix}_max"] = stat(vals, "max")
    out["exit_book_age_max"] = stat(book_age, "max")
    return out


def split_score(rows: list[dict[str, Any]], feature: str, threshold: float, direction: str) -> dict[str, Any]:
    selected = []
    omitted = []
    for row in rows:
        value = maybe_float(row.get(feature))
        if value is None:
            omitted.append(row)
            continue
        keep = value >= threshold if direction == "ge" else value <= threshold
        (selected if keep else omitted).append(row)
    selected_delta = sum(fnum(row.get("suppression_delta_cents")) for row in selected)
    omitted_delta = sum(fnum(row.get("suppression_delta_cents")) for row in omitted)
    helpful_selected = sum(1 for row in selected if row.get("suppress_would_help"))
    harmful_selected = sum(1 for row in selected if not row.get("suppress_would_help"))
    return {
        "feature": feature,
        "direction": direction,
        "threshold": threshold,
        "selected_rows": len(selected),
        "selected_helpful": helpful_selected,
        "selected_harmful": harmful_selected,
        "selected_suppression_delta_cents": selected_delta,
        "omitted_suppression_delta_cents": omitted_delta,
        "helpful_excluded": sum(1 for row in omitted if row.get("suppress_would_help")),
        "harmful_excluded": sum(1 for row in omitted if not row.get("suppress_would_help")),
        "selected_markets": [row.get("market") for row in selected],
    }


def candidate_separators(rows: list[dict[str, Any]], features: list[str]) -> list[dict[str, Any]]:
    candidates = []
    for feature in features:
        unique_values = sorted({maybe_float(row.get(feature)) for row in rows if maybe_float(row.get(feature)) is not None})
        if len(unique_values) < 2:
            continue
        for threshold in unique_values:
            candidates.append(split_score(rows, feature, threshold, "ge"))
            candidates.append(split_score(rows, feature, threshold, "le"))
    candidates.sort(
        key=lambda row: (
            -float(row.get("selected_suppression_delta_cents") or -999999.0),
            int(row.get("selected_harmful") or 0),
            -int(row.get("selected_helpful") or 0),
            -int(row.get("selected_rows") or 0),
        )
    )
    return candidates[:40]


def summarize(rows: list[dict[str, Any]]) -> dict[str, Any]:
    helpful = [row for row in rows if row.get("suppress_would_help")]
    harmful = [row for row in rows if not row.get("suppress_would_help")]
    return {
        "rows": len(rows),
        "helpful_to_suppress_rows": len(helpful),
        "harmful_to_suppress_rows": len(harmful),
        "all_suppress_delta_cents": sum(fnum(row.get("suppression_delta_cents")) for row in rows),
        "helpful_suppress_delta_cents": sum(fnum(row.get("suppression_delta_cents")) for row in helpful),
        "harmful_suppress_delta_cents": sum(fnum(row.get("suppression_delta_cents")) for row in harmful),
        "source_counts": dict(Counter(str(row.get("source") or "unknown") for row in rows)),
        "source_helpful_harmful": {
            source: {
                "helpful": sum(1 for row in rows if row.get("source") == source and row.get("suppress_would_help")),
                "harmful": sum(1 for row in rows if row.get("source") == source and not row.get("suppress_would_help")),
                "delta_cents": sum(fnum(row.get("suppression_delta_cents")) for row in rows if row.get("source") == source),
            }
            for source in sorted({str(row.get("source") or "unknown") for row in rows})
        },
    }


def interpretation(report: dict[str, Any]) -> list[str]:
    summary = report.get("summary") or {}
    best = (report.get("observable_candidate_separators") or [{}])[0]
    oracle_best = (report.get("diagnostic_oracle_separators") or [{}])[0]
    return [
        "Diagnostic separator audit only; any rule must be frozen before it can count as forward evidence.",
        (
            f"All-exit suppression on these rows would be {summary.get('all_suppress_delta_cents')}c, with "
            f"{summary.get('helpful_to_suppress_rows')} helpful-to-suppress and "
            f"{summary.get('harmful_to_suppress_rows')} harmful-to-suppress markets."
        ),
        (
            f"Best deployable-like observable separator: {best.get('feature')} {best.get('direction')} "
            f"{best.get('threshold')} selects {best.get('selected_rows')} markets for "
            f"{best.get('selected_suppression_delta_cents')}c, with helpful/harmful "
            f"{best.get('selected_helpful')}/{best.get('selected_harmful')}."
        ) if best else "No separator candidates found.",
        (
            f"Best oracle/diagnostic separator is {oracle_best.get('feature')} {oracle_best.get('direction')} "
            f"{oracle_best.get('threshold')}; treat it as an upper-bound contrast, not an actionable rule."
        ) if oracle_best else "No oracle separator candidates found.",
        "Use the separator shape to design a frozen watch, not to justify live changes.",
    ]


def build_report() -> dict[str, Any]:
    counterfactual = load_json(COUNTERFACTUAL_JSON)
    markets = {str(row.get("market") or "") for row in counterfactual.get("markets") or [] if row.get("market")}
    events = load_events(EXECUTION_EVENTS, markets)
    rows = []
    for row in counterfactual.get("markets") or []:
        compact = compact_market(row, events.get(str(row.get("market") or ""), []))
        if compact is not None:
            rows.append(compact)
    rows.sort(key=lambda row: fnum(row.get("suppression_delta_cents")), reverse=True)
    observable_separators = candidate_separators(rows, OBSERVABLE_SEPARATOR_FEATURES)
    oracle_separators = candidate_separators(rows, FEATURES)
    report = {
        "generated_at_utc": utc_now_iso(),
        "counterfactual_source": str(COUNTERFACTUAL_JSON),
        "execution_events_source": str(EXECUTION_EVENTS),
        "summary": summarize(rows),
        "observable_candidate_separators": observable_separators,
        "diagnostic_oracle_separators": oracle_separators,
        "rows": rows,
    }
    report["interpretation"] = interpretation(report)
    return report


def fmt(value: Any) -> str:
    if value is None:
        return "None"
    if isinstance(value, float):
        return f"{value:.6f}"
    return str(value)


def write_md(report: dict[str, Any]) -> None:
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8")
    lines = [
        "# v28 Feature-Gate Exit Suppression Separator",
        "",
        "Research-only diagnostic. No live bot changes or orders.",
        "",
        f"- Generated UTC: `{report.get('generated_at_utc')}`",
        "",
        "## Interpretation",
        "",
    ]
    lines.extend(f"- {note}" for note in report.get("interpretation") or [])
    lines.extend(
        [
            "",
            "## Observable Candidate Separators",
            "",
            "| feature | dir | threshold | selected | helpful/harmful | suppress delta c | omitted delta c | excluded helpful | excluded harmful |",
            "|---|---|---:|---:|---:|---:|---:|---:|---:|",
        ]
    )
    for row in report.get("observable_candidate_separators") or []:
        lines.append(
            f"| {row.get('feature')} | {row.get('direction')} | {fmt(row.get('threshold'))} | "
            f"{row.get('selected_rows')} | {row.get('selected_helpful')}/{row.get('selected_harmful')} | "
            f"{fmt(row.get('selected_suppression_delta_cents'))} | {fmt(row.get('omitted_suppression_delta_cents'))} | "
            f"{row.get('helpful_excluded')} | {row.get('harmful_excluded')} |"
        )
    lines.extend(
        [
            "",
            "## Oracle/Diagnostic Separators",
            "",
            "| feature | dir | threshold | selected | helpful/harmful | suppress delta c | omitted delta c | excluded helpful | excluded harmful |",
            "|---|---|---:|---:|---:|---:|---:|---:|---:|",
        ]
    )
    for row in (report.get("diagnostic_oracle_separators") or [])[:12]:
        lines.append(
            f"| {row.get('feature')} | {row.get('direction')} | {fmt(row.get('threshold'))} | "
            f"{row.get('selected_rows')} | {row.get('selected_helpful')}/{row.get('selected_harmful')} | "
            f"{fmt(row.get('selected_suppression_delta_cents'))} | {fmt(row.get('omitted_suppression_delta_cents'))} | "
            f"{row.get('helpful_excluded')} | {row.get('harmful_excluded')} |"
        )
    lines.extend(
        [
            "",
            "## Rows",
            "",
            "| market | source | side | won | suppress helps | suppress delta c | theory c | entry | exit | p_hold avg | drawdown avg | hold net avg | reason shares |",
            "|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|",
        ]
    )
    for row in report.get("rows") or []:
        reason_shares = {
            "reduce": row.get("reason_probability_reduce_share"),
            "value": row.get("reason_value_over_hold_share"),
            "collapse": row.get("reason_probability_collapse_share"),
        }
        lines.append(
            f"| {row.get('market')} | {row.get('source')} | {row.get('side')} | {row.get('side_won')} | "
            f"{row.get('suppress_would_help')} | {fmt(row.get('suppression_delta_cents'))} | "
            f"{fmt(row.get('theory_net_cents'))} | {fmt(row.get('entry_fill_avg_cents'))} | "
            f"{fmt(row.get('exit_fill_avg_cents'))} | {fmt(row.get('exit_p_hold_avg'))} | "
            f"{fmt(row.get('exit_fair_drawdown_avg'))} | {fmt(row.get('exit_hold_net_avg'))} | "
            f"{reason_shares} |"
        )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    report = build_report()
    write_md(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
