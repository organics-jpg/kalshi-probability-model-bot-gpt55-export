"""Same-window live comparator for the dual-lane overlay filter.

Research-only; no live bot changes or orders.

This compares the overlay filter's strict own-freeze selected rows to live v28
on the same selected markets. It is intentionally separate from the broad
dual-lane same-window comparator because the overlay is a narrow risk-control
branch, not a replacement strategy.
"""
from __future__ import annotations

import csv
import json
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
FILTER_WATCH_JSON = OUT_DIR / "v28_dual_lane_overlay_filter_watch_latest.json"
LIVE_TRADES_CSV = ROOT / "stats" / "live_mushroom_v28_size2" / "trades.csv"
OUT_JSON = OUT_DIR / "v28_dual_lane_overlay_same_window_compare_latest.json"
OUT_MD = OUT_DIR / "v28_dual_lane_overlay_same_window_compare_latest.md"

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


def write_json(path: Path, payload: dict[str, Any]) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8")


def fnum(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def money(value: Any) -> str:
    cents = fnum(value)
    return f"{cents:.0f}c (${cents / 100.0:.2f})"


def pct(value: Any) -> str:
    if value is None:
        return "n/a"
    return f"{fnum(value):.2f}%"


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


def row_net(row: dict[str, Any]) -> float:
    for field in ("final_weighted_cents", "weighted_net_cents", "selected_weighted_cents", "net_cents"):
        if row.get(field) is not None:
            return fnum(row.get(field))
    return 0.0


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
            rows.append(item)
    return rows


def aggregate_live_by_market(rows: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    grouped: dict[str, dict[str, Any]] = defaultdict(
        lambda: {"market": "", "trades": 0, "qty": 0.0, "net_cents": 0.0, "side_counts": defaultdict(int)}
    )
    for row in rows:
        market = str(row.get("market") or "")
        if not market:
            continue
        side = str(row.get("side") or "")
        grouped[market]["market"] = market
        grouped[market]["trades"] += 1
        grouped[market]["qty"] += fnum(row.get("qty"))
        grouped[market]["net_cents"] += fnum(row.get("net_cents"))
        if side:
            grouped[market]["side_counts"][side] += 1
    out: dict[str, dict[str, Any]] = {}
    for market, item in grouped.items():
        counts = dict(item["side_counts"])
        out[market] = {
            "market": market,
            "trades": item["trades"],
            "qty": item["qty"],
            "net_cents": item["net_cents"],
            "sides": ",".join(sorted(counts)),
            "dominant_side": max(counts, key=counts.get) if counts else None,
        }
    return out


def summarize(values: list[float], denominator: int | None = None) -> dict[str, Any]:
    total = sum(values)
    return {
        "entries": len(values),
        "wins": sum(1 for value in values if value > 0),
        "losses": sum(1 for value in values if value < 0),
        "net_cents": total,
        "full_loss_cushion": int(max(0.0, total) // 100.0),
        "coverage_pct": 100.0 * len(values) / denominator if denominator else None,
    }


def build_report() -> dict[str, Any]:
    watch = load_json(FILTER_WATCH_JSON)
    state = watch.get("state") if isinstance(watch.get("state"), dict) else {}
    freeze_ts = str(state.get("freeze_ts_utc") or "")
    best = watch.get("best_lane") if isinstance(watch.get("best_lane"), dict) else {}
    summary = best.get("summary") if isinstance(best.get("summary"), dict) else {}
    denominator = int(summary.get("entries") or 0)
    rows = [row for row in best.get("rows") or [] if isinstance(row, dict) and row.get("market")]
    if not denominator:
        denominator = int(summary.get("settled") or len(rows) or 0)
    live_rows = load_live_trades_after(freeze_ts)
    live_by_market = aggregate_live_by_market(live_rows)
    selected_markets = sorted({str(row.get("market")) for row in rows if row.get("market")})
    candidate_values = [row_net(row) for row in rows]
    live_same_values = [fnum(live_by_market.get(market, {}).get("net_cents")) for market in selected_markets if market in live_by_market]
    candidate_summary = summarize(candidate_values, denominator)
    live_same_summary = summarize(live_same_values, denominator)
    comparison_rows = []
    for row in rows:
        market = str(row.get("market") or "")
        live = live_by_market.get(market, {})
        candidate_net = row_net(row)
        live_net = fnum(live.get("net_cents"))
        comparison_rows.append(
            {
                "market": market,
                "candidate_side": row.get("side"),
                "candidate_component": row.get("component"),
                "candidate_source": row.get("source"),
                "candidate_net_cents": candidate_net,
                "live_trade_count": live.get("trades", 0),
                "live_qty": live.get("qty", 0.0),
                "live_sides": live.get("sides", ""),
                "live_net_cents": live_net,
                "candidate_minus_live_cents": candidate_net - live_net,
            }
        )
    comparison_rows.sort(key=lambda row: fnum(row.get("candidate_minus_live_cents")))
    delta = candidate_summary["net_cents"] - live_same_summary["net_cents"]
    return {
        "generated_at_utc": utc_now_iso(),
        "filter_watch_generated_at_utc": watch.get("generated_at_utc"),
        "freeze_ts_utc": freeze_ts,
        "freeze_local_time": watch.get("freeze_local_time"),
        "promotion_use": "overlay_same_window_research_only",
        "overlay_policy": best.get("sidecar_policy"),
        "overlay_rule": (state.get("overlay_rule") or {}).get("name"),
        "selected_markets": selected_markets,
        "candidate_summary": candidate_summary,
        "live_same_selected_markets_summary": live_same_summary,
        "candidate_minus_live_same_markets_cents": delta,
        "live_post_freeze_trades": len(live_rows),
        "live_post_freeze_markets": len(live_by_market),
        "comparison_rows": comparison_rows,
        "read": [
            "This is a strict selected-market comparator for the overlay filter.",
            "It remains empty until the overlay watch has selected own-freeze rows.",
            "A positive standalone overlay PnL is insufficient; selected rows should also improve live v28 on the same markets.",
        ],
    }


def write_md(report: dict[str, Any]) -> None:
    write_json(OUT_JSON, report)
    cand = report.get("candidate_summary") or {}
    live = report.get("live_same_selected_markets_summary") or {}
    lines = [
        "# v28 Dual-Lane Overlay Same-Window Compare",
        "",
        "Research-only. No live bot logic changes, no orders.",
        "",
        f"- Generated UTC: `{report.get('generated_at_utc')}`",
        f"- Filter watch UTC: `{report.get('filter_watch_generated_at_utc')}`",
        f"- Freeze UTC/local: `{report.get('freeze_ts_utc')}` / `{report.get('freeze_local_time')}`",
        f"- Promotion use: `{report.get('promotion_use')}`",
        f"- Overlay policy/rule: `{report.get('overlay_policy')}` / `{report.get('overlay_rule')}`",
        f"- Selected markets: `{len(report.get('selected_markets') or [])}`",
        f"- Candidate minus live on selected markets: `{money(report.get('candidate_minus_live_same_markets_cents'))}`",
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
            "| scope | entries/markets | W/L | coverage | net | cushion |",
            "|---|---:|---:|---:|---:|---:|",
            (
                f"| overlay selected rows | {cand.get('entries')} | {cand.get('wins')}/{cand.get('losses')} | "
                f"{pct(cand.get('coverage_pct'))} | {money(cand.get('net_cents'))} | {cand.get('full_loss_cushion')} |"
            ),
            (
                f"| live v28 same selected markets | {live.get('entries')} | {live.get('wins')}/{live.get('losses')} | "
                f"{pct(live.get('coverage_pct'))} | {money(live.get('net_cents'))} | {live.get('full_loss_cushion')} |"
            ),
            "",
            "## Market-Level Comparison",
            "",
            "| market | side | component | source | candidate net | live trades | live sides | live net | candidate-live |",
            "|---|---|---|---|---:|---:|---|---:|---:|",
        ]
    )
    for row in report.get("comparison_rows") or []:
        if not isinstance(row, dict):
            continue
        lines.append(
            f"| `{row.get('market')}` | {row.get('candidate_side')} | {row.get('candidate_component')} | "
            f"{row.get('candidate_source')} | {money(row.get('candidate_net_cents'))} | "
            f"{row.get('live_trade_count')} | {row.get('live_sides')} | {money(row.get('live_net_cents'))} | "
            f"{money(row.get('candidate_minus_live_cents'))} |"
        )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    report = build_report()
    write_md(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
