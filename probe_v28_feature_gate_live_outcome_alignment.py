"""Live-outcome alignment audit for v28 feature-gate rows.

Research-only; no live bot changes or orders.

The feature-gate reports score a frozen entry surface by settlement outcome.
The live bot may trade the same market differently, exit before settlement, or
trade the opposite side. This probe joins selected post-freeze feature-gate
markets to the refreshed live trade CSV so theoretical entry signal quality is
kept separate from exit/execution/state behavior.
"""
from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
FEATURE_JSON = OUT_DIR / "v28_boundary_clock_feature_gate_candidate_latest.json"
TRADES_CSV = ROOT / "stats" / "live_mushroom_v28_size2" / "trades.csv"
OUT_JSON = OUT_DIR / "v28_feature_gate_live_outcome_alignment_latest.json"
OUT_MD = OUT_DIR / "v28_feature_gate_live_outcome_alignment_latest.md"

TARGET_LANES = {"post_feature_freeze_entry", "post_feature_freeze_bridge"}
TARGET_CANDIDATES = {
    "post_feature_freeze_entry_raw03_recross70_abs075",
    "post_feature_freeze_bridge_raw03_recross70_abs075",
    "post_feature_freeze_entry_raw05_recross60_abs085",
    "post_feature_freeze_bridge_raw05_recross60_abs085",
    "post_feature_freeze_entry_raw05_recross60_abs085_ask65",
    "post_feature_freeze_bridge_raw05_recross60_abs085_ask65",
}


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


def load_trades(path: Path) -> dict[str, list[dict[str, Any]]]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    if not path.exists():
        return grouped
    with path.open("r", encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle):
            market = str(row.get("market") or "")
            if market:
                grouped[market].append(row)
    return grouped


def side_summary(trades: list[dict[str, Any]], selected_side: str) -> dict[str, Any]:
    selected = [row for row in trades if str(row.get("side") or "") == selected_side]
    opposite = [row for row in trades if str(row.get("side") or "") and str(row.get("side") or "") != selected_side]
    selected_net = sum(100.0 * fnum(row.get("net_pnl_dollars")) for row in selected)
    opposite_net = sum(100.0 * fnum(row.get("net_pnl_dollars")) for row in opposite)
    selected_qty = sum(fnum(row.get("qty")) for row in selected)
    opposite_qty = sum(fnum(row.get("qty")) for row in opposite)
    return {
        "selected_side_trades": len(selected),
        "opposite_side_trades": len(opposite),
        "selected_side_live_net_cents": selected_net,
        "opposite_side_live_net_cents": opposite_net,
        "selected_side_qty": selected_qty,
        "opposite_side_qty": opposite_qty,
        "selected_side_live_net_cents_per_contract": selected_net / selected_qty if selected_qty else None,
        "opposite_side_live_net_cents_per_contract": opposite_net / opposite_qty if opposite_qty else None,
    }


def live_summary(trades: list[dict[str, Any]], selected_side: str) -> dict[str, Any]:
    total_net = sum(100.0 * fnum(row.get("net_pnl_dollars")) for row in trades)
    qty = sum(fnum(row.get("qty")) for row in trades)
    sides = Counter(str(row.get("side") or "unknown") for row in trades)
    outcomes = Counter(str(row.get("outcome") or "unknown") for row in trades)
    exits = Counter(str(row.get("resolution_source") or "unknown") for row in trades)
    side_part = side_summary(trades, selected_side)
    return {
        "live_trade_count": len(trades),
        "live_qty": qty,
        "live_net_cents_total": total_net,
        "live_net_cents_per_contract": total_net / qty if qty else None,
        "sides": dict(sides),
        "outcomes": dict(outcomes),
        "resolution_sources": dict(exits),
        **side_part,
    }


def sign(value: float | None) -> str:
    if value is None:
        return "missing"
    if value > 0:
        return "positive"
    if value < 0:
        return "negative"
    return "flat"


def classify(theory_net: float, selected_side: str, trades: list[dict[str, Any]], live: dict[str, Any]) -> list[str]:
    tags: list[str] = []
    if not trades:
        return ["no_live_trade_on_market"]
    theory_sign = sign(theory_net)
    live_sign = sign(fnum(live.get("live_net_cents_total")))
    selected_side_sign = sign(fnum(live.get("selected_side_live_net_cents")))
    if int(live.get("selected_side_trades") or 0) == 0:
        tags.append("live_did_not_trade_selected_side")
    if int(live.get("opposite_side_trades") or 0) > 0:
        tags.append("live_traded_opposite_side")
    if theory_sign == "positive" and live_sign == "negative":
        tags.append("theory_win_live_market_loss")
    if theory_sign == "positive" and selected_side_sign == "negative":
        tags.append("theory_win_selected_side_live_loss")
    if theory_sign == "negative" and live_sign == "positive":
        tags.append("theory_loss_live_market_win")
    if any(str(row.get("outcome") or "") == "exited_before_settlement" for row in trades):
        tags.append("live_exited_before_settlement")
    if theory_sign == live_sign == "positive":
        tags.append("same_sign_positive")
    if theory_sign == live_sign == "negative":
        tags.append("same_sign_negative")
    return tags or ["live_alignment_unclear"]


def compact_row(row: dict[str, Any], trades_by_market: dict[str, list[dict[str, Any]]]) -> dict[str, Any]:
    market = str(row.get("market") or "")
    side = str(row.get("side") or "")
    theory_net = fnum(row.get("net_cents"))
    trades = trades_by_market.get(market) or []
    live = live_summary(trades, side)
    tags = classify(theory_net, side, trades, live)
    return {
        "market": market,
        "source": row.get("source"),
        "side": side,
        "side_won": row.get("side_won"),
        "theory_net_cents": theory_net,
        "ask_prob": row.get("ask_prob"),
        "raw_edge": row.get("raw_edge"),
        "recross_hazard_score": row.get("recross_hazard_score"),
        "abs_d_sigma": row.get("abs_d_sigma"),
        **live,
        "alignment_tags": tags,
    }


def summarize(rows: list[dict[str, Any]]) -> dict[str, Any]:
    live_traded = [row for row in rows if int(row.get("live_trade_count") or 0) > 0]
    theory_net = sum(fnum(row.get("theory_net_cents")) for row in rows)
    live_net = sum(fnum(row.get("live_net_cents_total")) for row in rows)
    selected_live_net = sum(fnum(row.get("selected_side_live_net_cents")) for row in rows)
    live_per_contract_market_sum = sum(
        fnum(row.get("live_net_cents_per_contract"))
        for row in rows
        if row.get("live_net_cents_per_contract") is not None
    )
    selected_side_per_contract_market_sum = sum(
        fnum(row.get("selected_side_live_net_cents_per_contract"))
        for row in rows
        if row.get("selected_side_live_net_cents_per_contract") is not None
    )
    tags = Counter(tag for row in rows for tag in row.get("alignment_tags") or [])
    source_tags = Counter(
        f"{row.get('source')}::{tag}"
        for row in rows
        for tag in row.get("alignment_tags") or []
    )
    return {
        "rows": len(rows),
        "live_traded_markets": len(live_traded),
        "no_live_trade_markets": len(rows) - len(live_traded),
        "theory_net_cents": theory_net,
        "live_net_cents_total": live_net,
        "selected_side_live_net_cents": selected_live_net,
        "live_net_cents_per_contract_market_sum": live_per_contract_market_sum,
        "selected_side_live_net_cents_per_contract_market_sum": selected_side_per_contract_market_sum,
        "theory_minus_live_total_cents": theory_net - live_net,
        "theory_minus_selected_side_live_cents": theory_net - selected_live_net,
        "theory_minus_live_per_contract_market_sum_cents": theory_net - live_per_contract_market_sum,
        "theory_minus_selected_side_per_contract_market_sum_cents": (
            theory_net - selected_side_per_contract_market_sum
        ),
        "tag_counts": dict(tags.most_common()),
        "source_tag_counts": dict(source_tags.most_common()),
    }


def selected_variants(feature: dict[str, Any]) -> list[dict[str, Any]]:
    out = []
    for lane in feature.get("lanes") or []:
        if lane.get("lane") not in TARGET_LANES:
            continue
        for variant in lane.get("variants") or []:
            if not isinstance(variant, dict):
                continue
            if variant.get("candidate") in TARGET_CANDIDATES:
                out.append(
                    {
                        "lane": lane.get("lane"),
                        "candidate": variant.get("candidate"),
                        "future_denominator": lane.get("future_denominator"),
                        "official_summary": variant.get("candidate_summary") or {},
                        "official_blockers": variant.get("blockers") or [],
                        "rows": [row for row in variant.get("rows") or [] if isinstance(row, dict)],
                    }
                )
    return out


def build_report() -> dict[str, Any]:
    feature = load_json(FEATURE_JSON)
    trades = load_trades(TRADES_CSV)
    variants = []
    for variant in selected_variants(feature):
        rows = [compact_row(row, trades) for row in variant.get("rows") or []]
        rows.sort(
            key=lambda row: (
                "theory_win_live_market_loss" not in (row.get("alignment_tags") or []),
                fnum(row.get("live_net_cents_total")),
            )
        )
        variant_out = dict(variant)
        variant_out["alignment_summary"] = summarize(rows)
        variant_out["rows"] = rows
        variants.append(variant_out)
    variants.sort(
        key=lambda row: (
            str(row.get("lane")),
            str(row.get("candidate")),
        )
    )
    report = {
        "generated_at_utc": utc_now_iso(),
        "feature_source": str(FEATURE_JSON),
        "trades_source": str(TRADES_CSV),
        "purpose": "Compare feature-gate theoretical settlement rows to actual live trade outcomes on the same markets.",
        "variants": variants,
    }
    report["interpretation"] = interpretation(report)
    return report


def interpretation(report: dict[str, Any]) -> list[str]:
    notes = [
        "This is an attribution audit only; it does not change official candidate scoring or live behavior.",
    ]
    for variant in report.get("variants") or []:
        summary = variant.get("alignment_summary") or {}
        notes.append(
            f"{variant.get('candidate')}: theory {summary.get('theory_net_cents')}c vs live total "
            f"{summary.get('live_net_cents_total')}c and live per-contract market-sum "
            f"{summary.get('live_net_cents_per_contract_market_sum')}c on "
            f"{summary.get('live_traded_markets')}/{summary.get('rows')} selected markets; "
            f"tags {summary.get('tag_counts')}."
        )
    return notes


def fmt(value: Any) -> str:
    if value is None:
        return "None"
    if isinstance(value, float):
        return f"{value:.6f}"
    return str(value)


def write_md(report: dict[str, Any]) -> None:
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8")
    lines = [
        "# v28 Feature-Gate Live Outcome Alignment",
        "",
        "Research-only attribution audit. No live bot changes or orders.",
        "",
        f"- Generated UTC: `{report.get('generated_at_utc')}`",
        f"- Feature source: `{report.get('feature_source')}`",
        f"- Trades source: `{report.get('trades_source')}`",
        "",
        "## Interpretation",
        "",
    ]
    lines.extend(f"- {note}" for note in report.get("interpretation") or [])
    for variant in report.get("variants") or []:
        summary = variant.get("alignment_summary") or {}
        lines.extend(
            [
                "",
                f"## {variant.get('candidate')}",
                "",
                f"- Lane: `{variant.get('lane')}`",
                f"- Official summary: `{variant.get('official_summary')}`",
                f"- Official blockers: `{variant.get('official_blockers')}`",
                f"- Alignment summary: `{summary}`",
                "",
                "| market | source | side | won | theory c | live trades | live sides | live c | live c/ct | selected-side c/ct | tags |",
                "|---|---|---|---|---:|---:|---|---:|---:|---:|---|",
            ]
        )
        for row in variant.get("rows") or []:
            lines.append(
                f"| {row.get('market')} | {row.get('source')} | {row.get('side')} | {row.get('side_won')} | "
                f"{fmt(row.get('theory_net_cents'))} | {row.get('live_trade_count')} | {row.get('sides')} | "
                f"{fmt(row.get('live_net_cents_total'))} | {fmt(row.get('live_net_cents_per_contract'))} | "
                f"{fmt(row.get('selected_side_live_net_cents_per_contract'))} | "
                f"{', '.join(row.get('alignment_tags') or [])} |"
            )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    report = build_report()
    write_md(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
