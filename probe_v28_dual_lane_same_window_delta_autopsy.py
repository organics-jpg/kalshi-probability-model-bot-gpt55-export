"""Autopsy candidate-vs-live delta on the same post-freeze markets.

Research-only; no live bot changes or orders.

The same-window comparator says whether a strict precheck candidate is beating
actual live v28 on the same markets. This probe explains the delta so a green
candidate row is not mistaken for a live-baseline improvement.
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
COMPARE_JSON = OUT_DIR / "v28_dual_lane_same_window_live_compare_latest.json"
LIVE_TRADES_CSV = ROOT / "stats" / "live_mushroom_v28_size2" / "trades.csv"
OUT_JSON = OUT_DIR / "v28_dual_lane_same_window_delta_autopsy_latest.json"
OUT_MD = OUT_DIR / "v28_dual_lane_same_window_delta_autopsy_latest.md"

LOCAL_TZ = datetime.now().astimezone().tzinfo


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


def parse_ts(value: str | None) -> datetime | None:
    if not value:
        return None
    text = str(value).strip()
    if not text:
        return None
    try:
        if "T" in text:
            return datetime.fromisoformat(text.replace("Z", "+00:00")).astimezone(timezone.utc)
        return datetime.strptime(text, "%Y-%m-%d %H:%M:%S").replace(tzinfo=LOCAL_TZ).astimezone(timezone.utc)
    except ValueError:
        return None


def money(value: Any) -> str:
    cents = fnum(value)
    return f"{cents:.0f}c (${cents / 100.0:.2f})"


def load_live_trades_after(freeze_ts: str) -> list[dict[str, Any]]:
    freeze = parse_ts(freeze_ts)
    if freeze is None or not LIVE_TRADES_CSV.exists():
        return []
    rows: list[dict[str, Any]] = []
    with LIVE_TRADES_CSV.open("r", encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle):
            entry_ts = parse_ts(row.get("entry_ts"))
            if entry_ts is None or entry_ts < freeze:
                continue
            item = dict(row)
            item["entry_ts_utc"] = entry_ts.isoformat()
            item["net_cents"] = round(100.0 * fnum(row.get("net_pnl_dollars")), 4)
            item["entry_fill_cents"] = fnum(row.get("entry_fill_cents_used") or row.get("entry_fill_cents_assumed"))
            item["exit_fill_cents"] = fnum(row.get("exit_fill_cents_used") or row.get("exit_fill_cents_assumed"))
            rows.append(item)
    return rows


def classify(row: dict[str, Any]) -> str:
    candidate = fnum(row.get("candidate_net_cents"))
    live = fnum(row.get("live_net_cents"))
    delta = fnum(row.get("candidate_minus_live_cents"))
    if delta < 0:
        if candidate >= 0 and live > candidate:
            return "candidate_positive_live_captured_more"
        if candidate < 0 <= live:
            return "candidate_loss_live_escape"
        if candidate < live < 0:
            return "candidate_larger_loss_than_live"
        return "candidate_trails_live_other"
    if delta > 0:
        if candidate >= 0 > live:
            return "candidate_avoids_live_loss"
        if candidate > live >= 0:
            return "candidate_captures_more_than_live"
        if live == 0:
            return "candidate_selected_live_absent_market"
        return "candidate_ahead_other"
    return "tied"


def live_side_breakdown(trades: list[dict[str, Any]], candidate_side: str) -> dict[str, Any]:
    side_counts: Counter[str] = Counter()
    side_net: dict[str, float] = defaultdict(float)
    outcomes: Counter[str] = Counter()
    for trade in trades:
        side = str(trade.get("side") or "")
        side_counts[side] += 1
        side_net[side] += fnum(trade.get("net_cents"))
        outcomes[str(trade.get("outcome") or "unknown")] += 1
    same_side = side_net.get(candidate_side, 0.0)
    opposite = sum(value for side, value in side_net.items() if side != candidate_side)
    return {
        "live_side_counts": dict(side_counts),
        "live_side_net_cents": dict(side_net),
        "live_same_side_net_cents": same_side,
        "live_opposite_side_net_cents": opposite,
        "live_outcome_counts": dict(outcomes),
        "live_avg_entry_fill_cents": (
            sum(fnum(trade.get("entry_fill_cents")) for trade in trades) / len(trades) if trades else None
        ),
        "live_avg_exit_fill_cents": (
            sum(fnum(trade.get("exit_fill_cents")) for trade in trades) / len(trades) if trades else None
        ),
    }


def summarize(rows: list[dict[str, Any]], key: str) -> list[dict[str, Any]]:
    grouped: dict[str, dict[str, Any]] = {}
    for row in rows:
        label = str(row.get(key) or "unknown")
        item = grouped.setdefault(
            label,
            {
                key: label,
                "rows": 0,
                "candidate_net_cents": 0.0,
                "live_net_cents": 0.0,
                "candidate_minus_live_cents": 0.0,
                "candidate_wins": 0,
                "candidate_losses": 0,
                "live_wins": 0,
                "live_losses": 0,
            },
        )
        candidate = fnum(row.get("candidate_net_cents"))
        live = fnum(row.get("live_net_cents"))
        item["rows"] += 1
        item["candidate_net_cents"] += candidate
        item["live_net_cents"] += live
        item["candidate_minus_live_cents"] += fnum(row.get("candidate_minus_live_cents"))
        item["candidate_wins"] += int(candidate > 0)
        item["candidate_losses"] += int(candidate < 0)
        item["live_wins"] += int(live > 0)
        item["live_losses"] += int(live < 0)
    return sorted(grouped.values(), key=lambda item: fnum(item.get("candidate_minus_live_cents")))


def build_report() -> dict[str, Any]:
    compare = load_json(COMPARE_JSON)
    freeze_ts = str(compare.get("freeze_ts_utc") or "")
    live_rows = load_live_trades_after(freeze_ts)
    live_by_market: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in live_rows:
        market = str(row.get("market") or "")
        if market:
            live_by_market[market].append(row)

    rows: list[dict[str, Any]] = []
    for base in compare.get("comparison_rows") or []:
        if not isinstance(base, dict):
            continue
        market = str(base.get("market") or "")
        trades = live_by_market.get(market, [])
        item = dict(base)
        item["classification"] = classify(item)
        item["live_trade_bucket"] = (
            "no_live_trade"
            if not trades
            else "single_live_trade"
            if len(trades) == 1
            else "multi_live_trade"
        )
        item.update(live_side_breakdown(trades, str(item.get("candidate_side") or "")))
        rows.append(item)

    trailing = [row for row in rows if fnum(row.get("candidate_minus_live_cents")) < 0]
    ahead = [row for row in rows if fnum(row.get("candidate_minus_live_cents")) > 0]
    deficit_cents = sum(fnum(row.get("candidate_minus_live_cents")) for row in trailing)
    surplus_cents = sum(fnum(row.get("candidate_minus_live_cents")) for row in ahead)
    top_deficits = sorted(trailing, key=lambda row: fnum(row.get("candidate_minus_live_cents")))[:8]
    top_surpluses = sorted(ahead, key=lambda row: fnum(row.get("candidate_minus_live_cents")), reverse=True)[:8]
    class_rows = summarize(rows, "classification")

    interpretation = [
        "Same-window evidence is research-only and cannot promote the dual lane before own-freeze rows mature.",
        "The current strict precheck is behind actual live v28 on the same markets; this is a live-baseline blocker, not just a sample-size blocker.",
    ]
    if class_rows:
        worst_class = class_rows[0]
        interpretation.append(
            "Largest negative bucket is "
            f"{worst_class.get('classification')} with {worst_class.get('rows')} rows and "
            f"{money(worst_class.get('candidate_minus_live_cents'))} candidate-minus-live."
        )
    if top_deficits:
        interpretation.append(
            "Top deficits should be treated as failure-mode examples for entry/exposure/exit-clock repair, "
            "not as rows to hand-pick away."
        )

    return {
        "generated_at_utc": utc_now_iso(),
        "freeze_ts_utc": freeze_ts,
        "same_window_compare_generated_at_utc": compare.get("generated_at_utc"),
        "promotion_use": "same_window_research_only",
        "candidate_policy": compare.get("candidate_policy"),
        "future_denominator": compare.get("future_denominator"),
        "candidate_summary": compare.get("candidate_summary"),
        "live_same_candidate_markets_summary": compare.get("live_same_candidate_markets_summary"),
        "candidate_minus_live_same_markets_cents": compare.get("candidate_minus_live_same_markets_cents"),
        "deficit_rows": len(trailing),
        "deficit_cents": deficit_cents,
        "surplus_rows": len(ahead),
        "surplus_cents": surplus_cents,
        "classification_summary": class_rows,
        "component_summary": summarize(rows, "candidate_component"),
        "source_summary": summarize(rows, "candidate_source"),
        "live_trade_bucket_summary": summarize(rows, "live_trade_bucket"),
        "top_deficits": top_deficits,
        "top_surpluses": top_surpluses,
        "rows": rows,
        "interpretation": interpretation,
    }


def write_outputs(report: dict[str, Any]) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8")
    cand = report.get("candidate_summary") or {}
    live = report.get("live_same_candidate_markets_summary") or {}
    lines = [
        "# v28 Dual-Lane Same-Window Delta Autopsy",
        "",
        "Research-only. No live bot logic changes, no orders.",
        "",
        f"- Generated UTC: `{report.get('generated_at_utc')}`",
        f"- Compare UTC: `{report.get('same_window_compare_generated_at_utc')}`",
        f"- Freeze UTC: `{report.get('freeze_ts_utc')}`",
        f"- Candidate policy: `{report.get('candidate_policy')}`",
        f"- Promotion use: `{report.get('promotion_use')}`",
        "",
        "## Read",
        "",
    ]
    lines.extend(f"- {item}" for item in report.get("interpretation") or [])
    lines.extend(
        [
            "",
            "## Same-Window Summary",
            "",
            f"- Candidate: `{cand.get('entries')}` entries, W/L `{cand.get('wins')}/{cand.get('losses')}`, net `{money(cand.get('net_cents'))}`, cushion `{cand.get('full_loss_cushion')}`.",
            f"- Live on candidate markets: `{live.get('entries')}` markets, W/L `{live.get('wins')}/{live.get('losses')}`, net `{money(live.get('net_cents'))}`, cushion `{live.get('full_loss_cushion')}`.",
            f"- Candidate minus live: `{money(report.get('candidate_minus_live_same_markets_cents'))}`.",
            f"- Deficit/surplus split: `{report.get('deficit_rows')}` deficit rows for `{money(report.get('deficit_cents'))}`, `{report.get('surplus_rows')}` surplus rows for `{money(report.get('surplus_cents'))}`.",
            "",
            "## Classification Summary",
            "",
            "| class | rows | candidate net | live net | candidate-live | candidate W/L | live W/L |",
            "|---|---:|---:|---:|---:|---:|---:|",
        ]
    )
    for row in report.get("classification_summary") or []:
        lines.append(
            f"| `{row.get('classification')}` | {row.get('rows')} | {money(row.get('candidate_net_cents'))} | "
            f"{money(row.get('live_net_cents'))} | {money(row.get('candidate_minus_live_cents'))} | "
            f"{row.get('candidate_wins')}/{row.get('candidate_losses')} | {row.get('live_wins')}/{row.get('live_losses')} |"
        )
    lines.extend(
        [
            "",
            "## Top Deficits",
            "",
            "| market | class | side | component | source | candidate | live | delta | live trades | live side net |",
            "|---|---|---|---|---|---:|---:|---:|---:|---|",
        ]
    )
    for row in report.get("top_deficits") or []:
        lines.append(
            f"| `{row.get('market')}` | `{row.get('classification')}` | {row.get('candidate_side')} | "
            f"{row.get('candidate_component')} | {row.get('candidate_source')} | "
            f"{money(row.get('candidate_net_cents'))} | {money(row.get('live_net_cents'))} | "
            f"{money(row.get('candidate_minus_live_cents'))} | {row.get('live_trade_count')} | "
            f"`{row.get('live_side_net_cents')}` |"
        )
    lines.extend(
        [
            "",
            "## Top Surpluses",
            "",
            "| market | class | side | component | source | candidate | live | delta | live trades |",
            "|---|---|---|---|---|---:|---:|---:|---:|",
        ]
    )
    for row in report.get("top_surpluses") or []:
        lines.append(
            f"| `{row.get('market')}` | `{row.get('classification')}` | {row.get('candidate_side')} | "
            f"{row.get('candidate_component')} | {row.get('candidate_source')} | "
            f"{money(row.get('candidate_net_cents'))} | {money(row.get('live_net_cents'))} | "
            f"{money(row.get('candidate_minus_live_cents'))} | {row.get('live_trade_count')} |"
        )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    report = build_report()
    write_outputs(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
