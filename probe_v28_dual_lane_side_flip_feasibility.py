"""Feasibility audit for side-flip state repair in the v28 dual-lane branch.

Research-only; no live bot changes or orders.

The sequence audit found two candidate-loss markets where live v28 escaped by
taking early same-side damage and then winning on the opposite side. This probe
checks whether that side-flip behavior is a broad, actionable repair signal or
only a sparse hindsight pattern.
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
DELTA_JSON = OUT_DIR / "v28_dual_lane_same_window_delta_autopsy_latest.json"
SEQUENCE_JSON = OUT_DIR / "v28_dual_lane_same_window_sequence_mechanism_latest.json"
LIVE_TRADES_CSV = ROOT / "stats" / "live_mushroom_v28_size2" / "trades.csv"
OUT_JSON = OUT_DIR / "v28_dual_lane_side_flip_feasibility_latest.json"
OUT_MD = OUT_DIR / "v28_dual_lane_side_flip_feasibility_latest.md"

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
        if value is None or value == "":
            return default
        return float(value)
    except (TypeError, ValueError):
        return default


def money(value: Any) -> str:
    cents = fnum(value)
    return f"{cents:.0f}c (${cents / 100.0:.2f})"


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
            exit_ts = parse_ts(row.get("exit_ts"))
            item = dict(row)
            item["entry_ts_utc"] = entry_ts.isoformat()
            item["exit_ts_utc"] = exit_ts.isoformat() if exit_ts else None
            item["net_cents"] = round(100.0 * fnum(row.get("net_pnl_dollars")), 4)
            item["qty_num"] = fnum(row.get("qty"))
            rows.append(item)
    return rows


def summarize_market(market: str, trades: list[dict[str, Any]], candidate: dict[str, Any] | None = None) -> dict[str, Any]:
    trades = sorted(trades, key=lambda row: str(row.get("entry_ts_utc") or ""))
    side_counts: Counter[str] = Counter(str(row.get("side") or "") for row in trades)
    side_net: dict[str, float] = defaultdict(float)
    for row in trades:
        side_net[str(row.get("side") or "")] += fnum(row.get("net_cents"))
    candidate_side = str((candidate or {}).get("candidate_side") or "")
    same_side_net = side_net.get(candidate_side, 0.0) if candidate_side else None
    opposite_side_net = (
        sum(value for side, value in side_net.items() if side != candidate_side)
        if candidate_side
        else None
    )
    sides = [side for side, count in side_counts.items() if side and count]
    first_side = str(trades[0].get("side") or "") if trades else ""
    side_changes = sum(
        1
        for prev, curr in zip(trades, trades[1:])
        if str(prev.get("side") or "") != str(curr.get("side") or "")
    )
    return {
        "market": market,
        "trade_count": len(trades),
        "sides": sides,
        "side_counts": dict(side_counts),
        "side_net_cents": dict(side_net),
        "net_cents": sum(fnum(row.get("net_cents")) for row in trades),
        "has_side_flip": len(sides) > 1,
        "side_changes": side_changes,
        "first_side": first_side,
        "candidate_side": candidate_side or None,
        "candidate_net_cents": (candidate or {}).get("candidate_net_cents"),
        "candidate_minus_live_cents": (candidate or {}).get("candidate_minus_live_cents"),
        "same_side_net_cents": same_side_net,
        "opposite_side_net_cents": opposite_side_net,
        "opposite_rescue": (
            bool(candidate_side)
            and fnum(same_side_net) <= 0
            and fnum(opposite_side_net) > 0
            and fnum((candidate or {}).get("candidate_net_cents")) < 0
        ),
        "sequence": [
            {
                "entry_ts": row.get("entry_ts"),
                "side": row.get("side"),
                "qty": row.get("qty_num"),
                "outcome": row.get("outcome"),
                "net_cents": row.get("net_cents"),
            }
            for row in trades
        ],
    }


def summarize_group(rows: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "markets": len(rows),
        "net_cents": sum(fnum(row.get("net_cents")) for row in rows),
        "positive_markets": sum(1 for row in rows if fnum(row.get("net_cents")) > 0),
        "negative_markets": sum(1 for row in rows if fnum(row.get("net_cents")) < 0),
        "trade_count": sum(int(fnum(row.get("trade_count"))) for row in rows),
        "side_flip_markets": sum(1 for row in rows if row.get("has_side_flip")),
        "opposite_rescue_markets": sum(1 for row in rows if row.get("opposite_rescue")),
    }


def build_report() -> dict[str, Any]:
    delta = load_json(DELTA_JSON)
    sequence = load_json(SEQUENCE_JSON)
    freeze_ts = str(delta.get("freeze_ts_utc") or "")
    live_trades = load_live_trades_after(freeze_ts)
    by_market: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in live_trades:
        market = str(row.get("market") or "")
        if market:
            by_market[market].append(row)
    candidate_by_market = {
        str(row.get("market")): row for row in delta.get("rows") or [] if isinstance(row, dict) and row.get("market")
    }
    all_live_market_rows = [
        summarize_market(market, trades)
        for market, trades in sorted(by_market.items())
    ]
    candidate_market_rows = [
        summarize_market(market, by_market.get(market, []), candidate)
        for market, candidate in sorted(candidate_by_market.items())
    ]
    side_flip_candidate_rows = [row for row in candidate_market_rows if row.get("has_side_flip")]
    opposite_rescue_rows = [row for row in candidate_market_rows if row.get("opposite_rescue")]
    all_side_flip_rows = [row for row in all_live_market_rows if row.get("has_side_flip")]

    blocker_tags = ["research_only", "not_frozen_forward", "side_flip_trigger_not_observable_from_static_candidate_row"]
    if len(opposite_rescue_rows) < 5:
        blocker_tags.append("opposite_rescue_sample_too_sparse")
    if len(side_flip_candidate_rows) < 5:
        blocker_tags.append("candidate_side_flip_sample_too_sparse")

    interpretation = [
        "Side-flip rescue is real in the current deficit rows, but it is sparse and derived from live sequence behavior.",
        "The current candidate row is static; a deployable repair would need an explicit pre-registered state-transition trigger and its own forward rows.",
    ]
    if opposite_rescue_rows:
        interpretation.append(
            f"Candidate-market opposite-side rescues: {len(opposite_rescue_rows)} market(s), "
            f"{money(sum(fnum(row.get('opposite_side_net_cents')) for row in opposite_rescue_rows))} opposite-side net."
        )
    if all_side_flip_rows:
        interpretation.append(
            f"All post-freeze live side-flip markets: {len(all_side_flip_rows)} of {len(all_live_market_rows)} markets, "
            f"net {money(sum(fnum(row.get('net_cents')) for row in all_side_flip_rows))}."
        )

    return {
        "generated_at_utc": utc_now_iso(),
        "promotion_use": "feasibility_only_not_candidate",
        "freeze_ts_utc": freeze_ts,
        "delta_autopsy_generated_at_utc": delta.get("generated_at_utc"),
        "sequence_mechanism_generated_at_utc": sequence.get("generated_at_utc"),
        "candidate_policy": delta.get("candidate_policy"),
        "all_live_summary": summarize_group(all_live_market_rows),
        "all_live_side_flip_summary": summarize_group(all_side_flip_rows),
        "candidate_market_summary": summarize_group(candidate_market_rows),
        "candidate_side_flip_summary": summarize_group(side_flip_candidate_rows),
        "candidate_opposite_rescue_summary": summarize_group(opposite_rescue_rows),
        "candidate_side_flip_rows": side_flip_candidate_rows,
        "candidate_opposite_rescue_rows": opposite_rescue_rows,
        "blockers": blocker_tags,
        "interpretation": interpretation,
    }


def write_outputs(report: dict[str, Any]) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8")
    all_live = report.get("all_live_summary") or {}
    all_flip = report.get("all_live_side_flip_summary") or {}
    cand = report.get("candidate_market_summary") or {}
    cand_flip = report.get("candidate_side_flip_summary") or {}
    rescue = report.get("candidate_opposite_rescue_summary") or {}
    lines = [
        "# v28 Dual-Lane Side-Flip Feasibility",
        "",
        "Research-only. No live bot logic changes, no orders.",
        "",
        f"- Generated UTC: `{report.get('generated_at_utc')}`",
        f"- Promotion use: `{report.get('promotion_use')}`",
        f"- Freeze UTC: `{report.get('freeze_ts_utc')}`",
        f"- Candidate policy: `{report.get('candidate_policy')}`",
        f"- Blockers: `{', '.join(report.get('blockers') or [])}`",
        "",
        "## Read",
        "",
    ]
    lines.extend(f"- {item}" for item in report.get("interpretation") or [])
    lines.extend(
        [
            "",
            "## Summary",
            "",
            "| scope | markets | net | positive/negative | trades | side-flip markets | opposite rescues |",
            "|---|---:|---:|---:|---:|---:|---:|",
            f"| all post-freeze live markets | {all_live.get('markets')} | {money(all_live.get('net_cents'))} | {all_live.get('positive_markets')}/{all_live.get('negative_markets')} | {all_live.get('trade_count')} | {all_live.get('side_flip_markets')} | {all_live.get('opposite_rescue_markets')} |",
            f"| all post-freeze side-flip markets | {all_flip.get('markets')} | {money(all_flip.get('net_cents'))} | {all_flip.get('positive_markets')}/{all_flip.get('negative_markets')} | {all_flip.get('trade_count')} | {all_flip.get('side_flip_markets')} | {all_flip.get('opposite_rescue_markets')} |",
            f"| candidate markets | {cand.get('markets')} | {money(cand.get('net_cents'))} | {cand.get('positive_markets')}/{cand.get('negative_markets')} | {cand.get('trade_count')} | {cand.get('side_flip_markets')} | {cand.get('opposite_rescue_markets')} |",
            f"| candidate side-flip markets | {cand_flip.get('markets')} | {money(cand_flip.get('net_cents'))} | {cand_flip.get('positive_markets')}/{cand_flip.get('negative_markets')} | {cand_flip.get('trade_count')} | {cand_flip.get('side_flip_markets')} | {cand_flip.get('opposite_rescue_markets')} |",
            f"| candidate opposite-rescue markets | {rescue.get('markets')} | {money(rescue.get('net_cents'))} | {rescue.get('positive_markets')}/{rescue.get('negative_markets')} | {rescue.get('trade_count')} | {rescue.get('side_flip_markets')} | {rescue.get('opposite_rescue_markets')} |",
            "",
            "## Candidate Opposite-Rescue Rows",
            "",
            "| market | candidate side | candidate net | same-side live | opposite live | live net | sequence |",
            "|---|---|---:|---:|---:|---:|---|",
        ]
    )
    for row in report.get("candidate_opposite_rescue_rows") or []:
        sequence = "; ".join(
            f"{item.get('entry_ts')} {item.get('side')}x{item.get('qty'):.0f} {item.get('outcome')} {money(item.get('net_cents'))}"
            for item in row.get("sequence") or []
        )
        lines.append(
            f"| `{row.get('market')}` | {row.get('candidate_side')} | {money(row.get('candidate_net_cents'))} | "
            f"{money(row.get('same_side_net_cents'))} | {money(row.get('opposite_side_net_cents'))} | "
            f"{money(row.get('net_cents'))} | {sequence} |"
        )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    report = build_report()
    write_outputs(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
