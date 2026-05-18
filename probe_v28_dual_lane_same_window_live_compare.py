"""Same-window live comparator for the v28 dual-lane candidate.

Research-only; no live bot changes or orders.

The readiness gate intentionally keeps a conservative wall against the full
live baseline, but research needs an apples-to-apples read too: how the
candidate is doing on the same post-freeze markets the live v28 bot is seeing.
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
STRICT_PRECHECK_JSON = OUT_DIR / "v28_dual_lane_strict_replay_precheck_latest.json"
LIVE_TRADES_CSV = ROOT / "stats" / "live_mushroom_v28_size2" / "trades.csv"
OUT_JSON = OUT_DIR / "v28_dual_lane_same_window_live_compare_latest.json"
OUT_MD = OUT_DIR / "v28_dual_lane_same_window_live_compare_latest.md"


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
            item = dict(row)
            item["entry_ts_utc"] = entry_ts.isoformat()
            item["net_cents"] = round(100.0 * fnum(row.get("net_pnl_dollars")), 4)
            rows.append(item)
    return rows


def candidate_rows(best: dict[str, Any]) -> list[dict[str, Any]]:
    rows = best.get("worst_rows") if isinstance(best.get("worst_rows"), list) else []
    out = [row for row in rows if isinstance(row, dict) and row.get("market")]
    # The strict-precheck compact artifact stores all rows while settled <= 30.
    return out


def row_net(row: dict[str, Any]) -> float:
    for field in ("final_weighted_cents", "weighted_net_cents", "selected_weighted_cents", "net_cents"):
        if row.get(field) is not None:
            return fnum(row.get(field))
    return 0.0


def summarize_values(values: list[float], denominator: int | None = None) -> dict[str, Any]:
    total = sum(values)
    return {
        "entries": len(values),
        "wins": sum(1 for value in values if value > 0),
        "losses": sum(1 for value in values if value < 0),
        "net_cents": total,
        "full_loss_cushion": int(max(0.0, total) // 100.0),
        "coverage_pct": 100.0 * len(values) / denominator if denominator else None,
    }


def aggregate_live_by_market(rows: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    grouped: dict[str, dict[str, Any]] = defaultdict(
        lambda: {
            "trades": 0,
            "net_cents": 0.0,
            "qty": 0.0,
            "side_counts": defaultdict(int),
            "side_net_cents": defaultdict(float),
        }
    )
    for row in rows:
        market = str(row.get("market") or "")
        if not market:
            continue
        side = str(row.get("side") or "")
        grouped[market]["market"] = market
        grouped[market]["trades"] += 1
        grouped[market]["net_cents"] += fnum(row.get("net_cents"))
        grouped[market]["qty"] += fnum(row.get("qty"))
        if side:
            grouped[market]["side_counts"][side] += 1
            grouped[market]["side_net_cents"][side] += fnum(row.get("net_cents"))
    for item in grouped.values():
        item["pnl_sign"] = 1 if item["net_cents"] > 0 else -1 if item["net_cents"] < 0 else 0
        item["side_counts"] = dict(item["side_counts"])
        item["side_net_cents"] = dict(item["side_net_cents"])
        item["dominant_side"] = max(item["side_counts"], key=item["side_counts"].get) if item["side_counts"] else None
    return dict(grouped)


def comparison_bucket(candidate_net: float, live_net: float, candidate_minus_live: float) -> str:
    if live_net == 0.0:
        return "candidate_vs_no_live_pnl"
    if candidate_net < 0 and live_net > 0:
        return "candidate_wrong_or_exit_bad_live_won"
    if candidate_net > 0 and live_net > candidate_net:
        return "candidate_right_but_live_captured_more"
    if candidate_net > 0 and live_net < 0:
        return "candidate_improves_live_loss"
    if candidate_minus_live > 0:
        return "candidate_better_than_live"
    return "candidate_not_better_than_live"


def build_report() -> dict[str, Any]:
    strict = load_json(STRICT_PRECHECK_JSON)
    best = strict.get("best_union") if isinstance(strict.get("best_union"), dict) else {}
    freeze_ts = str(strict.get("freeze_ts_utc") or "")
    live_rows = load_live_trades_after(freeze_ts)
    live_by_market = aggregate_live_by_market(live_rows)
    cand_rows = candidate_rows(best)
    cand_markets = sorted({str(row.get("market")) for row in cand_rows if row.get("market")})
    same_live = [live_by_market[market] for market in cand_markets if market in live_by_market]
    candidate_values = [row_net(row) for row in cand_rows]
    live_same_values = [fnum(row.get("net_cents")) for row in same_live]
    live_all_market_values = [fnum(row.get("net_cents")) for row in live_by_market.values()]
    denominator = int(((best.get("primary_diagnostics") or {}).get("future_denominator") or 0) or 0)
    candidate_summary = summarize_values(candidate_values, denominator)
    live_same_summary = summarize_values(live_same_values, denominator)
    live_all_summary = summarize_values(live_all_market_values, denominator)
    comparison_rows = []
    for row in cand_rows:
        market = str(row.get("market") or "")
        live = live_by_market.get(market, {})
        candidate_side = str(row.get("side") or "")
        candidate_net = row_net(row)
        live_net = fnum(live.get("net_cents"))
        same_side_net = fnum((live.get("side_net_cents") or {}).get(candidate_side))
        opposite_side_net = live_net - same_side_net
        delta = candidate_net - live_net
        comparison_rows.append(
            {
                "market": market,
                "candidate_side": candidate_side,
                "candidate_component": row.get("component"),
                "candidate_source": row.get("source"),
                "candidate_side_won": row.get("side_won"),
                "candidate_net_cents": candidate_net,
                "live_trade_count": live.get("trades", 0),
                "live_qty": live.get("qty", 0.0),
                "live_sides": ",".join(sorted((live.get("side_counts") or {}).keys())),
                "live_dominant_side": live.get("dominant_side"),
                "live_same_side_net_cents": same_side_net,
                "live_opposite_side_net_cents": opposite_side_net,
                "live_net_cents": live_net,
                "candidate_minus_live_cents": delta,
                "comparison_bucket": comparison_bucket(candidate_net, live_net, delta),
                "raw_edge": row.get("raw_edge"),
                "recross_hazard_score": row.get("recross_hazard_score"),
                "abs_d_sigma": row.get("abs_d_sigma"),
                "ask_prob": row.get("ask_prob"),
            }
        )
    comparison_rows.sort(key=lambda row: fnum(row.get("candidate_minus_live_cents")))
    bucket_summary: dict[str, dict[str, Any]] = {}
    for row in comparison_rows:
        bucket = str(row.get("comparison_bucket") or "unknown")
        item = bucket_summary.setdefault(
            bucket,
            {
                "rows": 0,
                "candidate_net_cents": 0.0,
                "live_net_cents": 0.0,
                "candidate_minus_live_cents": 0.0,
            },
        )
        item["rows"] += 1
        item["candidate_net_cents"] += fnum(row.get("candidate_net_cents"))
        item["live_net_cents"] += fnum(row.get("live_net_cents"))
        item["candidate_minus_live_cents"] += fnum(row.get("candidate_minus_live_cents"))
    return {
        "generated_at_utc": utc_now_iso(),
        "freeze_ts_utc": freeze_ts,
        "strict_precheck_generated_at_utc": strict.get("generated_at_utc"),
        "promotion_use": "same_window_research_only",
        "candidate_policy": best.get("sidecar_policy"),
        "future_denominator": denominator,
        "candidate_summary": candidate_summary,
        "live_same_candidate_markets_summary": live_same_summary,
        "live_all_post_freeze_market_summary": live_all_summary,
        "candidate_minus_live_same_markets_cents": candidate_summary["net_cents"] - live_same_summary["net_cents"],
        "candidate_markets": len(cand_markets),
        "live_post_freeze_trades": len(live_rows),
        "live_post_freeze_markets": len(live_by_market),
        "comparison_bucket_summary": bucket_summary,
        "comparison_rows": comparison_rows,
        "read": [
            "This is an apples-to-apples research comparator, not a promotion gate by itself.",
            "Candidate rows come from the latest forced strict precheck artifact; this is complete only while the compact artifact contains all candidate rows.",
            "Live rows are actual scored v28 trades after the candidate freeze, aggregated by market.",
            "Large candidate-minus-live gaps can be exit/position-management gaps even when the candidate chose the correct settlement side.",
        ],
    }


def pct(value: Any) -> str:
    if value is None:
        return "n/a"
    return f"{fnum(value):.2f}%"


def write_md(report: dict[str, Any]) -> None:
    write_json(OUT_JSON, report)
    cand = report.get("candidate_summary") or {}
    same = report.get("live_same_candidate_markets_summary") or {}
    live_all = report.get("live_all_post_freeze_market_summary") or {}
    lines = [
        "# v28 Dual-Lane Same-Window Live Compare",
        "",
        "Research-only. No live bot logic changes, no orders.",
        "",
        f"- Generated UTC: `{report.get('generated_at_utc')}`",
        f"- Freeze UTC: `{report.get('freeze_ts_utc')}`",
        f"- Strict precheck UTC: `{report.get('strict_precheck_generated_at_utc')}`",
        f"- Promotion use: `{report.get('promotion_use')}`",
        f"- Candidate policy: `{report.get('candidate_policy')}`",
        f"- Future denominator: `{report.get('future_denominator')}`",
        f"- Live post-freeze trades/markets: `{report.get('live_post_freeze_trades')}` / `{report.get('live_post_freeze_markets')}`",
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
                f"| candidate forced precheck | {cand.get('entries')} | {cand.get('wins')}/{cand.get('losses')} | "
                f"{pct(cand.get('coverage_pct'))} | {money(cand.get('net_cents'))} | {cand.get('full_loss_cushion')} |"
            ),
            (
                f"| live v28 on candidate markets | {same.get('entries')} | {same.get('wins')}/{same.get('losses')} | "
                f"{pct(same.get('coverage_pct'))} | {money(same.get('net_cents'))} | {same.get('full_loss_cushion')} |"
            ),
            (
                f"| live v28 all post-freeze markets | {live_all.get('entries')} | {live_all.get('wins')}/{live_all.get('losses')} | "
                f"{pct(live_all.get('coverage_pct'))} | {money(live_all.get('net_cents'))} | {live_all.get('full_loss_cushion')} |"
            ),
            "",
            f"- Candidate minus live on same candidate markets: `{money(report.get('candidate_minus_live_same_markets_cents'))}`",
            "",
            "## Delta Buckets",
            "",
            "| bucket | rows | candidate net | live net | candidate-live |",
            "|---|---:|---:|---:|---:|",
        ]
    )
    bucket_summary = report.get("comparison_bucket_summary") if isinstance(report.get("comparison_bucket_summary"), dict) else {}
    for bucket, item in sorted(
        bucket_summary.items(),
        key=lambda pair: fnum((pair[1] or {}).get("candidate_minus_live_cents")),
    ):
        if not isinstance(item, dict):
            continue
        lines.append(
            f"| `{bucket}` | {item.get('rows')} | {money(item.get('candidate_net_cents'))} | "
            f"{money(item.get('live_net_cents'))} | {money(item.get('candidate_minus_live_cents'))} |"
        )
    lines.extend(
        [
            "",
            "## Market-Level Comparison",
            "",
            "| market | side | component | source | bucket | candidate net | live trades | live sides | live same-side | live opposite | live net | candidate-live |",
            "|---|---|---|---|---|---:|---:|---|---:|---:|---:|---:|",
        ]
    )
    for row in report.get("comparison_rows") or []:
        if not isinstance(row, dict):
            continue
        lines.append(
            f"| `{row.get('market')}` | {row.get('candidate_side')} | {row.get('candidate_component')} | "
            f"{row.get('candidate_source')} | `{row.get('comparison_bucket')}` | {money(row.get('candidate_net_cents'))} | "
            f"{row.get('live_trade_count')} | {row.get('live_sides')} | "
            f"{money(row.get('live_same_side_net_cents'))} | {money(row.get('live_opposite_side_net_cents'))} | "
            f"{money(row.get('live_net_cents'))} | "
            f"{money(row.get('candidate_minus_live_cents'))} |"
        )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    report = build_report()
    write_md(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
