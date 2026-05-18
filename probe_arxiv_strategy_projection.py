"""Paper-inspired strategy projections for the live v28 BTC 15m bot.

Research-only. This script reads refreshed scorer outputs and execution event
telemetry, then projects simple strategy gates inspired by the Truffle/arXiv
ideas against already-recorded live v28 entries. It never places orders and
does not modify live bot logic.
"""
from __future__ import annotations

import csv
import json
import math
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable
from zoneinfo import ZoneInfo


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
TRADES_CSV = ROOT / "stats" / "live_mushroom_v28_size2" / "trades.csv"
LIVE_SUMMARY_JSON = ROOT / "stats" / "live_mushroom_v28_size2" / "summary.json"
EXECUTION_EVENTS = ROOT / "logs" / "live_mushroom_v28_size2" / "execution_events.ndjson"
CANDIDATE_TABLE_JSON = OUT_DIR / "v28_candidate_vs_live_full_table_latest.json"
OUT_JSON = OUT_DIR / "arxiv_strategy_projection_latest.json"
OUT_MD = OUT_DIR / "arxiv_strategy_projection_latest.md"

NY_TZ = ZoneInfo("America/New_York")


def load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
    return payload if isinstance(payload, dict) else {}


def as_float(value: Any) -> float | None:
    if value is None or value == "":
        return None
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    return number if math.isfinite(number) else None


def as_int_price(value: Any) -> str:
    number = as_float(value)
    if number is None:
        return ""
    return str(int(number))


def parse_wall_to_local(value: Any) -> datetime | None:
    if not value:
        return None
    text = str(value)
    try:
        if text.endswith("Z"):
            return datetime.fromisoformat(text.replace("Z", "+00:00")).astimezone(NY_TZ).replace(tzinfo=None)
        parsed = datetime.fromisoformat(text)
    except ValueError:
        return None
    if parsed.tzinfo is not None:
        return parsed.astimezone(NY_TZ).replace(tzinfo=None)
    return parsed


def feature_quality(event: dict[str, Any]) -> int:
    event_type = str(event.get("event_type") or "")
    score = {
        "plan_built": 30,
        "signal_seen": 20,
        "mushroom_v28_approved": 10,
        "order_submit_start": 5,
        "order_submit_success": 5,
    }.get(event_type, 0)
    for key in (
        "mushroom_p_side",
        "mushroom_v28_p_side",
        "depth_required",
        "eligible_depth",
        "mushroom_v28_edge_cents",
        "book_age_ms",
        "mushroom_v28_abs_d_sigma",
    ):
        if event.get(key) not in (None, ""):
            score += 5
    return score


def load_feature_events() -> dict[tuple[str, str, str], list[dict[str, Any]]]:
    wanted = {
        "signal_seen",
        "mushroom_v28_approved",
        "plan_built",
        "order_submit_start",
        "order_submit_success",
    }
    by_key: dict[tuple[str, str, str], list[dict[str, Any]]] = {}
    if not EXECUTION_EVENTS.exists():
        return by_key
    with EXECUTION_EVENTS.open("r", encoding="utf-8") as handle:
        for line in handle:
            try:
                event = json.loads(line)
            except json.JSONDecodeError:
                continue
            if event.get("event_type") not in wanted:
                continue
            if event.get("mushroom_v28_p_side") is None and event.get("event_type") not in {
                "order_submit_start",
                "order_submit_success",
            }:
                continue
            local_dt = parse_wall_to_local(event.get("ts_wall"))
            if local_dt is None:
                continue
            trigger = (
                event.get("trigger_price_cents")
                or event.get("mushroom_v28_ask_cents")
                or event.get("cap_price_cents")
            )
            side = event.get("side") or event.get("mushroom_v28_side")
            key = (str(event.get("market") or ""), str(side or ""), as_int_price(trigger))
            event = dict(event)
            event["_local_dt"] = local_dt
            by_key.setdefault(key, []).append(event)
    for rows in by_key.values():
        rows.sort(key=lambda item: item["_local_dt"])
    return by_key


def best_feature_match(
    index: dict[tuple[str, str, str], list[dict[str, Any]]],
    trade: dict[str, Any],
) -> tuple[dict[str, Any] | None, float | None]:
    key = (
        str(trade.get("market") or ""),
        str(trade.get("side") or ""),
        as_int_price(trade.get("entry_trigger_cents")),
    )
    entry_dt = trade.get("_entry_dt")
    if not isinstance(entry_dt, datetime):
        return None, None
    candidates: list[tuple[float, int, dict[str, Any]]] = []
    for event in index.get(key, []):
        delta = abs((event["_local_dt"] - entry_dt).total_seconds())
        if delta <= 3.0:
            candidates.append((delta, feature_quality(event), event))
    if not candidates:
        return None, None
    candidates.sort(key=lambda item: (-item[1], item[0]))
    delta, _, event = candidates[0]
    return event, delta


def load_matched_live_trades() -> tuple[list[dict[str, Any]], dict[str, Any]]:
    features = load_feature_events()
    matched: list[dict[str, Any]] = []
    raw_trade_count = 0
    if not TRADES_CSV.exists():
        return matched, {"raw_trade_count": 0, "matched_trade_count": 0}
    with TRADES_CSV.open("r", newline="", encoding="utf-8") as handle:
        for trade in csv.DictReader(handle):
            pnl_dollars = as_float(trade.get("net_pnl_dollars"))
            entry_dt = parse_wall_to_local(trade.get("entry_ts"))
            if pnl_dollars is None or entry_dt is None:
                continue
            raw_trade_count += 1
            trade = dict(trade)
            trade["_entry_dt"] = entry_dt
            trade["pnl_cents"] = pnl_dollars * 100.0
            feature, match_seconds = best_feature_match(features, trade)
            if feature is None:
                continue
            trade["feature_event_type"] = feature.get("event_type")
            trade["feature_match_seconds"] = match_seconds
            enrich_trade_features(trade, feature)
            matched.append(trade)
    matched.sort(key=lambda row: row["_entry_dt"])
    diagnostics = {
        "raw_trade_count": raw_trade_count,
        "matched_trade_count": len(matched),
        "feature_index_keys": len(features),
        "feature_event_type_counts": {
            event_type: sum(1 for row in matched if row.get("feature_event_type") == event_type)
            for event_type in sorted({str(row.get("feature_event_type")) for row in matched})
        },
    }
    return matched, diagnostics


def enrich_trade_features(trade: dict[str, Any], feature: dict[str, Any]) -> None:
    p28 = as_float(feature.get("mushroom_v28_p_side"))
    p22 = as_float(feature.get("mushroom_p_side"))
    edge28 = as_float(feature.get("mushroom_v28_edge_cents"))
    edge22 = as_float(feature.get("mushroom_edge_cents"))
    depth = as_float(feature.get("eligible_depth") or feature.get("mushroom_v28_eligible_depth"))
    required = as_float(feature.get("depth_required"))
    ask = as_float(feature.get("mushroom_v28_ask_cents") or trade.get("entry_trigger_cents"))
    trade.update(
        {
            "p28": p28,
            "p22": p22,
            "probability_gap": abs(p28 - p22) if p28 is not None and p22 is not None else None,
            "edge28_cents": edge28,
            "edge22_cents": edge22,
            "edge_gap_cents": abs(edge28 - edge22) if edge28 is not None and edge22 is not None else None,
            "eligible_depth": depth,
            "depth_required": required,
            "depth_ratio": depth / required if depth is not None and required and required > 0 else None,
            "book_age_ms": as_float(feature.get("book_age_ms") or feature.get("mushroom_v28_book_age_ms")),
            "btc_age_ms": as_float(feature.get("mushroom_v28_btc_age_ms")),
            "seconds_to_close": as_float(feature.get("seconds_to_close") or feature.get("mushroom_v28_seconds_to_close")),
            "ask_cents": ask,
            "abs_d_sigma": as_float(feature.get("mushroom_v28_abs_d_sigma")),
            "volshock": as_float(feature.get("mushroom_v28_volshock")),
            "arrow": as_float(feature.get("mushroom_v28_arrow")),
        }
    )


def trade_stats(rows: list[dict[str, Any]], denominator: int) -> dict[str, Any]:
    pnl_values = [as_float(row.get("pnl_cents")) or 0.0 for row in rows]
    wins = sum(1 for value in pnl_values if value > 0)
    losses = sum(1 for value in pnl_values if value < 0)
    flats = sum(1 for value in pnl_values if abs(value) < 1e-9)
    cost_basis = sum(as_float(row.get("entry_notional_dollars")) or 0.0 for row in rows)
    net_cents = sum(pnl_values)
    return {
        "entries": len(rows),
        "coverage_of_live_entries": len(rows) / denominator if denominator else None,
        "wins": wins,
        "losses": losses,
        "flats": flats,
        "win_rate_ex_flats": wins / (wins + losses) if wins + losses else None,
        "net_cents": net_cents,
        "net_dollars": net_cents / 100.0,
        "avg_cents_per_entry": net_cents / len(rows) if rows else None,
        "cost_basis_dollars": cost_basis,
        "roi_on_entry_notional": (net_cents / 100.0) / cost_basis if cost_basis else None,
    }


@dataclass(frozen=True)
class Strategy:
    name: str
    ideas: str
    rule: str
    interpretation: str
    predicate: Callable[[dict[str, Any]], bool]


def ge(value: Any, threshold: float) -> bool:
    number = as_float(value)
    return number is not None and number >= threshold


def le(value: Any, threshold: float) -> bool:
    number = as_float(value)
    return number is not None and number <= threshold


def between(value: Any, low: float, high: float) -> bool:
    number = as_float(value)
    return number is not None and low <= number <= high


STRATEGIES = [
    Strategy(
        name="current_live_v28_replay",
        ideas="baseline",
        rule="All matched live v28 entries from the refreshed scorer window.",
        interpretation="Control row for same-window comparison.",
        predicate=lambda row: True,
    ),
    Strategy(
        name="conformal_consensus_winrate_gate",
        ideas="conformal interval / ensemble agreement",
        rule="Keep current v28 entries only when v28-v22 probability gap <= 0.12 and v28 edge >= 4c.",
        interpretation=(
            "A cheap proxy for calibrated uncertainty: use v22-v28 agreement as an interval width. "
            "It tilts toward hit rate, but may sacrifice too much coverage and total PnL."
        ),
        predicate=lambda row: le(row.get("probability_gap"), 0.12) and ge(row.get("edge28_cents"), 4.0),
    ),
    Strategy(
        name="depth_decay_fillability_gate",
        ideas="Dubach depth decay / Lokin state-dependent fill probability",
        rule=(
            "Keep current v28 entries only when depth/required >= 3, book age <= 750ms, "
            "ask <= 80c, and seconds_to_close >= 600."
        ),
        interpretation=(
            "A conservative execution-quality gate: enough displayed depth, fresh enough book, "
            "not too late in the round, and not paying the expensive tail."
        ),
        predicate=lambda row: (
            ge(row.get("depth_ratio"), 3.0)
            and le(row.get("book_age_ms"), 750.0)
            and le(row.get("ask_cents"), 80.0)
            and ge(row.get("seconds_to_close"), 600.0)
        ),
    ),
    Strategy(
        name="brownian_fpt_sanity_gate",
        ideas="Brownian first-passage / jump-diffusion baseline",
        rule="Keep current v28 entries only when v28 edge >= 3c, seconds_to_close >= 120, and 0.70 <= abs_d_sigma <= 1.10.",
        interpretation=(
            "Use the terminal-distribution idea as a sanity band: avoid extremely thin/remote or late states "
            "where the v28 fair value has historically been less reliable."
        ),
        predicate=lambda row: (
            ge(row.get("edge28_cents"), 3.0)
            and ge(row.get("seconds_to_close"), 120.0)
            and between(row.get("abs_d_sigma"), 0.70, 1.10)
        ),
    ),
    Strategy(
        name="hybrid_fpt_depth_gate",
        ideas="Brownian FPT + LOB fillability",
        rule=(
            "Keep current v28 entries only when edge >= 3c, depth/required >= 8, book age <= 750ms, "
            "ask <= 83c, seconds_to_close >= 120, and 0.85 <= abs_d_sigma <= 1.10."
        ),
        interpretation=(
            "A stricter combined gate. It is cleaner mechanically, but the projection shows that stacking "
            "filters can over-reduce the opportunity set."
        ),
        predicate=lambda row: (
            ge(row.get("edge28_cents"), 3.0)
            and ge(row.get("depth_ratio"), 8.0)
            and le(row.get("book_age_ms"), 750.0)
            and le(row.get("ask_cents"), 83.0)
            and ge(row.get("seconds_to_close"), 120.0)
            and between(row.get("abs_d_sigma"), 0.85, 1.10)
        ),
    ),
]


def split_rows(rows: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    n = len(rows)
    train_end = int(0.60 * n)
    validation_end = int(0.80 * n)
    return {
        "train_first_60pct": rows[:train_end],
        "validation_next_20pct": rows[train_end:validation_end],
        "holdout_last_20pct": rows[validation_end:],
    }


def evaluate_strategies(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    denominator = len(rows)
    splits = split_rows(rows)
    results: list[dict[str, Any]] = []
    for strategy in STRATEGIES:
        selected = [row for row in rows if strategy.predicate(row)]
        split_stats = {}
        for split_name, split in splits.items():
            split_selected = [row for row in split if strategy.predicate(row)]
            split_stats[split_name] = trade_stats(split_selected, len(split))
        results.append(
            {
                "name": strategy.name,
                "ideas": strategy.ideas,
                "rule": strategy.rule,
                "interpretation": strategy.interpretation,
                "all": trade_stats(selected, denominator),
                "splits": split_stats,
            }
        )
    return results


def candidate_artifact_crosswalk() -> list[dict[str, Any]]:
    payload = load_json(CANDIDATE_TABLE_JSON)
    rows = [row for row in payload.get("rows") or [] if isinstance(row, dict) and row.get("type") == "candidate"]
    motifs = [
        (
            "best_existing_fillability_candidate",
            "Dubach/Lokin execution model",
            ("fill", "book", "depth", "ask", "liquid"),
        ),
        (
            "best_existing_fpt_physics_candidate",
            "Brownian/FPT or path physics",
            ("brownian", "diffusion", "bridge", "physics", "recross", "hazard", "clock"),
        ),
        (
            "best_existing_consensus_candidate",
            "conformal/agreement/interval uncertainty",
            ("conformal", "agreement", "interval", "bayes", "neighbor", "disagreement"),
        ),
    ]
    output: list[dict[str, Any]] = []
    for name, ideas, words in motifs:
        matches = []
        for row in rows:
            haystack = f"{row.get('gate')} {row.get('policy')}".lower()
            if not any(word in haystack for word in words):
                continue
            matches.append(row)
        matches.sort(key=lambda row: as_float(row.get("net_cents")) or -10**9, reverse=True)
        if not matches:
            continue
        row = matches[0]
        wins = as_float(row.get("wins"))
        losses = as_float(row.get("losses"))
        output.append(
            {
                "name": name,
                "ideas": ideas,
                "gate": row.get("gate"),
                "policy": row.get("policy"),
                "entries": row.get("entries"),
                "settled": row.get("settled"),
                "wins": row.get("wins"),
                "losses": row.get("losses"),
                "win_rate_ex_flats": wins / (wins + losses) if wins is not None and losses is not None and wins + losses else None,
                "coverage_pct": row.get("coverage_pct"),
                "net_cents": row.get("net_cents"),
                "net_dollars": (as_float(row.get("net_cents")) or 0.0) / 100.0,
                "delta_vs_live_cents": row.get("delta_vs_live_cents"),
                "live_ready": row.get("live_ready"),
                "simulated_share": row.get("simulated_share"),
                "blockers": row.get("blockers") or [],
            }
        )
    return output


def fmt_money(value: Any) -> str:
    number = as_float(value)
    if number is None:
        return "n/a"
    return f"${number:,.2f}"


def fmt_cents(value: Any) -> str:
    number = as_float(value)
    if number is None:
        return "n/a"
    return f"{number:,.1f}c"


def fmt_pct(value: Any) -> str:
    number = as_float(value)
    if number is None:
        return "n/a"
    return f"{100.0 * number:.1f}%"


def fmt_wl(stats: dict[str, Any]) -> str:
    flats = int(stats.get("flats") or 0)
    suffix = f" (+{flats} flat)" if flats else ""
    return f"{int(stats.get('wins') or 0)}/{int(stats.get('losses') or 0)}{suffix}"


def write_md(report: dict[str, Any]) -> None:
    lines = [
        "# arXiv Strategy Projection",
        "",
        "Research-only same-window replay over refreshed live v28 trades. These are projected gates over recorded entries, not live-trading instructions.",
        "",
        f"- Generated UTC: `{report.get('generated_at_utc')}`",
        f"- Matched trades: `{report.get('diagnostics', {}).get('matched_trade_count')}` / `{report.get('diagnostics', {}).get('raw_trade_count')}`",
        f"- Live scorer net: `{fmt_money(report.get('live_summary', {}).get('net_pnl_total_dollars'))}`",
        "",
        "## Live-entry replay strategies",
        "",
        "| strategy | ideas | entries | W/L | win rate | net PnL | avg/entry | coverage | train PnL | validation PnL | holdout PnL | rule |",
        "|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|",
    ]
    for row in report.get("strategies") or []:
        stats = row.get("all") or {}
        splits = row.get("splits") or {}
        lines.append(
            f"| {row.get('name')} | {row.get('ideas')} | {stats.get('entries')} | {fmt_wl(stats)} | "
            f"{fmt_pct(stats.get('win_rate_ex_flats'))} | {fmt_money(stats.get('net_dollars'))} | "
            f"{fmt_cents(stats.get('avg_cents_per_entry'))} | {fmt_pct(stats.get('coverage_of_live_entries'))} | "
            f"{fmt_money((splits.get('train_first_60pct') or {}).get('net_dollars'))} | "
            f"{fmt_money((splits.get('validation_next_20pct') or {}).get('net_dollars'))} | "
            f"{fmt_money((splits.get('holdout_last_20pct') or {}).get('net_dollars'))} | "
            f"{row.get('rule')} |"
        )
    lines.extend(
        [
            "",
            "## Existing candidate crosswalk",
            "",
            "These are the strongest current candidate-table rows whose names already match the paper themes. They use existing candidate artifacts rather than the raw live-entry replay above.",
            "",
            "| candidate | ideas | entries | W/L | win rate | coverage | net PnL | delta vs live | live ready | source share | blockers |",
            "|---|---|---:|---:|---:|---:|---:|---:|---|---:|---|",
        ]
    )
    for row in report.get("candidate_artifact_crosswalk") or []:
        blockers = ", ".join(str(item) for item in row.get("blockers") or [])
        lines.append(
            f"| {row.get('gate')} / {row.get('policy')} | {row.get('ideas')} | {row.get('entries')} | "
            f"{row.get('wins')}/{row.get('losses')} | {fmt_pct(row.get('win_rate_ex_flats'))} | "
            f"{fmt_pct((as_float(row.get('coverage_pct')) or 0.0) / 100.0 if row.get('coverage_pct') is not None else None)} | "
            f"{fmt_money(row.get('net_dollars'))} | {fmt_cents(row.get('delta_vs_live_cents'))} | "
            f"{row.get('live_ready')} | {row.get('simulated_share') if row.get('simulated_share') is not None else 'n/a'} | {blockers} |"
        )
    lines.extend(
        [
            "",
            "## Notes",
            "",
            "- The consensus/conformal row is a proxy using v22-v28 disagreement as interval width; it is not a real Venn-Abers/conformal calibrator yet.",
            "- The Brownian/FPT row is the strongest same-window replay, but it is still retrospective. It needs frozen forward collection before promotion.",
            "- Win rate and PnL diverge here: the best PnL row does not have the best hit rate because payoff size matters.",
        ]
    )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    rows, diagnostics = load_matched_live_trades()
    report = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "purpose": "Research-only projection of Truffle/arXiv-inspired strategy gates over recorded live v28 entries.",
        "inputs": {
            "trades_csv": str(TRADES_CSV),
            "execution_events": str(EXECUTION_EVENTS),
            "live_summary_json": str(LIVE_SUMMARY_JSON),
            "candidate_table_json": str(CANDIDATE_TABLE_JSON),
        },
        "diagnostics": diagnostics,
        "live_summary": load_json(LIVE_SUMMARY_JSON),
        "strategies": evaluate_strategies(rows),
        "candidate_artifact_crosswalk": candidate_artifact_crosswalk(),
    }
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8")
    write_md(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
