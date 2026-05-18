"""Future-only live v28 high-confidence quality registry.

Research-only. This freezes physical tags, then scores future live v28
approvals with p_side >= 0.70 by settlement outcome. It is intentionally not a
promotion gate by itself; it is a guardrail against tuning p70 sharpening on a
tiny or cherry-picked sample.
"""
from __future__ import annotations

import json
import math
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
EVENTS = ROOT / "logs" / "live_mushroom_v28_size2" / "execution_events.ndjson"
OUTCOMES = ROOT / "state" / "live_mushroom_v28_size2" / "recent_market_outcomes.json"
OUT_DIR = ROOT / "logs" / "edge_research"
STATE_JSON = OUT_DIR / "v28_live_p70_quality_registry_state.json"
OUT_JSON = OUT_DIR / "v28_live_p70_quality_registry_latest.json"
OUT_MD = OUT_DIR / "v28_live_p70_quality_registry_latest.md"


TAG_DEFINITIONS = {
    "p85_live_threshold": "p_side >= 0.85",
    "p90_extreme_confidence": "p_side >= 0.90",
    "edge_ge_4c": "edge_cents >= 4",
    "thin_edge_lt_4c": "edge_cents < 4",
    "deep_geometry": "abs_d_sigma >= 0.90",
    "boundary_geometry": "abs_d_sigma < 0.60",
    "early_gt_12m": "seconds_to_close > 720",
    "middle_time_120_720s": "120 <= seconds_to_close <= 720",
    "crowded_or_deep_touch": "depth_count >= 500",
    "older_book_500ms": "book_age_ms >= 500",
}


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def parse_ts(value: Any) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except ValueError:
        return None


def as_float(value: Any) -> float | None:
    if value is None or value == "":
        return None
    try:
        out = float(value)
    except (TypeError, ValueError):
        return None
    return out if math.isfinite(out) else None


def load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
    return payload if isinstance(payload, dict) else {}


def load_or_create_state() -> dict[str, Any]:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    if STATE_JSON.exists():
        state = load_json(STATE_JSON)
        if state.get("freeze_ts_utc"):
            return state
    state = {
        "freeze_ts_utc": utc_now_iso(),
        "registry": "live_v28_p70_quality_tags",
        "rule": "Track future live v28 approvals with p_side >= 0.70 by fixed physical tags.",
        "tag_definitions": TAG_DEFINITIONS,
    }
    STATE_JSON.write_text(json.dumps(state, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return state


def load_events() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    if not EVENTS.exists():
        return rows
    with EVENTS.open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError:
                continue
            if isinstance(row, dict):
                rows.append(row)
    return rows


def outcome_map() -> dict[str, dict[str, Any]]:
    payload = load_json(OUTCOMES)
    records = payload.get("records") if isinstance(payload.get("records"), list) else []
    out: dict[str, dict[str, Any]] = {}
    for row in records:
        if isinstance(row, dict) and row.get("market"):
            out[str(row["market"])] = row
    return out


def tags(row: dict[str, Any]) -> list[str]:
    p = as_float(row.get("mushroom_v28_p_side"))
    edge = as_float(row.get("mushroom_v28_edge_cents"))
    abs_d = as_float(row.get("mushroom_v28_abs_d_sigma"))
    stc = as_float(row.get("mushroom_v28_seconds_to_close"))
    depth = as_float(row.get("mushroom_v28_depth_count"))
    book_age = as_float(row.get("mushroom_v28_book_age_ms"))
    out: list[str] = []
    if p is not None and p >= 0.85:
        out.append("p85_live_threshold")
    if p is not None and p >= 0.90:
        out.append("p90_extreme_confidence")
    if edge is not None and edge >= 4.0:
        out.append("edge_ge_4c")
    if edge is not None and edge < 4.0:
        out.append("thin_edge_lt_4c")
    if abs_d is not None and abs_d >= 0.90:
        out.append("deep_geometry")
    if abs_d is not None and abs_d < 0.60:
        out.append("boundary_geometry")
    if stc is not None and stc > 720.0:
        out.append("early_gt_12m")
    if stc is not None and 120.0 <= stc <= 720.0:
        out.append("middle_time_120_720s")
    if depth is not None and depth >= 500.0:
        out.append("crowded_or_deep_touch")
    if book_age is not None and book_age >= 500.0:
        out.append("older_book_500ms")
    return out or ["untagged"]


def side_won(row: dict[str, Any], outcome: dict[str, Any] | None) -> bool | None:
    if not outcome:
        return None
    market_result = str(outcome.get("market_result") or "").strip().lower()
    if market_result in {"yes", "no"}:
        return str(row.get("mushroom_v28_side") or row.get("side") or "").strip().lower() == market_result
    result = str(outcome.get("outcome_type") or "").lower()
    if result == "win":
        return True
    if result in {"loss", "settled_loss"}:
        return False
    return None


def row_summary(row: dict[str, Any], outcome: dict[str, Any] | None) -> dict[str, Any]:
    p = as_float(row.get("mushroom_v28_p_side"))
    won = side_won(row, outcome)
    brier = None
    logloss = None
    if p is not None and won is not None:
        y = 1.0 if won else 0.0
        brier = (p - y) ** 2
        clipped = min(max(p, 1e-9), 1 - 1e-9)
        logloss = -(math.log(clipped) if won else math.log(1 - clipped))
    return {
        "market": row.get("market"),
        "ts_wall": row.get("ts_wall"),
        "side": row.get("mushroom_v28_side") or row.get("side"),
        "p_side": p,
        "ask_cents": as_float(row.get("mushroom_v28_ask_cents")),
        "edge_cents": as_float(row.get("mushroom_v28_edge_cents")),
        "abs_d_sigma": as_float(row.get("mushroom_v28_abs_d_sigma")),
        "seconds_to_close": as_float(row.get("mushroom_v28_seconds_to_close")),
        "depth_count": as_float(row.get("mushroom_v28_depth_count")),
        "book_age_ms": as_float(row.get("mushroom_v28_book_age_ms")),
        "outcome_type": outcome.get("outcome_type") if outcome else None,
        "pnl_dollars": outcome.get("pnl_dollars") if outcome else None,
        "side_won": won,
        "brier": brier,
        "logloss": logloss,
        "tags": tags(row),
    }


def rollups(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    out = []
    for tag in sorted({tag for row in rows for tag in row.get("tags", [])}):
        tagged = [row for row in rows if tag in (row.get("tags") or [])]
        settled = [row for row in tagged if row.get("side_won") is not None]
        out.append({
            "tag": tag,
            "rows": len(tagged),
            "settled": len(settled),
            "wins": sum(1 for row in settled if row.get("side_won") is True),
            "losses": sum(1 for row in settled if row.get("side_won") is False),
            "avg_p": sum(float(row.get("p_side") or 0.0) for row in tagged) / len(tagged) if tagged else None,
            "avg_brier": sum(float(row.get("brier") or 0.0) for row in settled) / len(settled) if settled else None,
        })
    out.sort(key=lambda row: (-int(row.get("settled") or 0), str(row.get("tag"))))
    return out


def build_report() -> dict[str, Any]:
    state = load_or_create_state()
    freeze_ts = parse_ts(state["freeze_ts_utc"]) or datetime.now(timezone.utc)
    outcomes = outcome_map()
    future_source_rows = []
    for row in load_events():
        if row.get("event_type") != "mushroom_v28_approved" or row.get("mushroom_v28_approved") is not True:
            continue
        ts = parse_ts(row.get("ts_wall"))
        if ts is None or ts <= freeze_ts:
            continue
        p = as_float(row.get("mushroom_v28_p_side"))
        if p is None or p < 0.70:
            continue
        future_source_rows.append(row)
    exchange_results = fetch_exchange_results(sorted({str(row.get("market") or "") for row in future_source_rows if row.get("market")}))
    future = []
    for row in future_source_rows:
        market = str(row.get("market") or "")
        outcome = dict(outcomes.get(market) or {})
        if market in exchange_results:
            outcome["market_result"] = exchange_results[market]
        future.append(row_summary(row, outcome or None))
    settled = [row for row in future if row.get("side_won") is not None]
    return {
        "freeze": state,
        "rows": future,
        "row_count": len(future),
        "settled_count": len(settled),
        "wins": sum(1 for row in settled if row.get("side_won") is True),
        "losses": sum(1 for row in settled if row.get("side_won") is False),
        "avg_brier": sum(float(row.get("brier") or 0.0) for row in settled) / len(settled) if settled else None,
        "tag_rollups": rollups(future),
    }


def fetch_exchange_results(markets: list[str]) -> dict[str, str]:
    unresolved = [market for market in markets if market]
    if not unresolved:
        return {}
    try:
        from kalshi_btc15m_bot_ws import KalshiClient, load_config

        client = KalshiClient(load_config())
        out: dict[str, str] = {}
        for market in unresolved:
            payload = client.get_market(market)
            result = str((payload or {}).get("result") or "").strip().lower()
            if result in {"yes", "no"}:
                out[market] = result
        return out
    except Exception:
        return {}


def fmt(value: Any) -> str:
    if value is None:
        return "None"
    if isinstance(value, float):
        return f"{value:.6f}"
    return str(value)


def write_report(report: dict[str, Any]) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8")
    lines = [
        "# v28 Live p70 Quality Registry",
        "",
        f"- Freeze timestamp UTC: `{(report.get('freeze') or {}).get('freeze_ts_utc')}`",
        f"- Rows/settled/W-L: `{report.get('row_count')}/{report.get('settled_count')}/{report.get('wins')}-{report.get('losses')}`",
        f"- Avg Brier: `{fmt(report.get('avg_brier'))}`",
        "",
        "## Tag Rollups",
        "",
        "| tag | rows | settled | W/L | avg p | avg brier |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for row in report.get("tag_rollups") or []:
        lines.append(
            f"| {row.get('tag')} | {row.get('rows')} | {row.get('settled')} | {row.get('wins')}/{row.get('losses')} | "
            f"{fmt(row.get('avg_p'))} | {fmt(row.get('avg_brier'))} |"
        )
    lines.extend([
        "",
        "## Rows",
        "",
        "| market | ts | side | p | ask | edge | abs d | stc | depth | outcome | brier | tags |",
        "|---|---|---|---:|---:|---:|---:|---:|---:|---|---:|---|",
    ])
    for row in report.get("rows") or []:
        lines.append(
            f"| {row.get('market')} | {row.get('ts_wall')} | {row.get('side')} | {fmt(row.get('p_side'))} | "
            f"{fmt(row.get('ask_cents'))} | {fmt(row.get('edge_cents'))} | {fmt(row.get('abs_d_sigma'))} | "
            f"{fmt(row.get('seconds_to_close'))} | {fmt(row.get('depth_count'))} | {row.get('outcome_type')} | "
            f"{fmt(row.get('brier'))} | {', '.join(row.get('tags') or [])} |"
        )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    report = build_report()
    write_report(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
