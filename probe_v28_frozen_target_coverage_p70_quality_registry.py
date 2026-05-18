"""Frozen quality registry for p70-adjustable target-coverage rows.

Research-only; no live bot changes or orders.

Hard p70 is promising but fragile. This registry does not promote a new model;
it predeclares physical quality tags for future raw p>=0.70 rows so we can
learn which high-confidence situations actually deserve sharpening.
"""
from __future__ import annotations

import json
import math
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from probe_v28_frozen_forward_candidates import market_timing, parse_ts
from probe_v28_raw_entry_coverage_valve import selected_base_rows
from probe_v28_target_coverage_fv_overlay_validator import DEFAULT_POLICY, apply_policy


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
STATE_JSON = OUT_DIR / "v28_frozen_target_coverage_p70_quality_registry_state.json"
OUT_JSON = OUT_DIR / "v28_frozen_target_coverage_p70_quality_registry_latest.json"
OUT_MD = OUT_DIR / "v28_frozen_target_coverage_p70_quality_registry_latest.md"


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


def load_or_create_state() -> dict[str, Any]:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    if STATE_JSON.exists():
        payload = load_json(STATE_JSON)
        if payload.get("freeze_ts_utc"):
            return payload
    state = {
        "freeze_ts_utc": utc_now_iso(),
        "entry_policy": DEFAULT_POLICY,
        "registry": "p70_quality_tags",
        "rule": "Track future target-coverage rows with raw p>=0.70 and fixed physical quality tags before considering tag-conditioned sharpening.",
        "tag_definitions": {
            "calm_recross": "recross_hazard_score <= 0.45",
            "turbulent_recross": "recross_hazard_score >= 0.65",
            "deep_geometry": "abs_d_sigma >= 0.90",
            "boundary_geometry": "abs_d_sigma < 0.60",
            "book_discount_ge_4pp": "raw_edge_prob >= 0.04",
            "thin_edge_lt_3pp": "raw_edge_prob < 0.03",
            "expensive_ask_ge_85c": "ask_prob >= 0.85",
            "middle_time_120_720s": "120 <= seconds_to_close <= 720",
            "late_or_extreme_time": "seconds_to_close < 120 or seconds_to_close > 720",
        },
    }
    STATE_JSON.write_text(json.dumps(state, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return state


def as_float(value: Any) -> float | None:
    if value is None or value == "":
        return None
    try:
        out = float(value)
    except (TypeError, ValueError):
        return None
    return out if math.isfinite(out) else None


def raw_p(row: dict[str, Any]) -> float | None:
    return as_float(row.get("p_side") if row.get("p_side") is not None else row.get("p_raw"))


def quality_tags(row: dict[str, Any]) -> list[str]:
    recross = as_float(row.get("recross_hazard_score"))
    abs_d = as_float(row.get("abs_d_sigma"))
    edge = as_float(row.get("raw_edge_prob"))
    ask = as_float(row.get("ask_prob"))
    stc = as_float(row.get("seconds_to_close"))
    tags: list[str] = []
    if recross is not None and recross <= 0.45:
        tags.append("calm_recross")
    if recross is not None and recross >= 0.65:
        tags.append("turbulent_recross")
    if abs_d is not None and abs_d >= 0.90:
        tags.append("deep_geometry")
    if abs_d is not None and abs_d < 0.60:
        tags.append("boundary_geometry")
    if edge is not None and edge >= 0.04:
        tags.append("book_discount_ge_4pp")
    if edge is not None and edge < 0.03:
        tags.append("thin_edge_lt_3pp")
    if ask is not None and ask >= 0.85:
        tags.append("expensive_ask_ge_85c")
    if stc is not None and 120.0 <= stc <= 720.0:
        tags.append("middle_time_120_720s")
    if stc is not None and (stc < 120.0 or stc > 720.0):
        tags.append("late_or_extreme_time")
    if not tags:
        tags.append("untagged")
    return tags


def row_summary(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "market": row.get("market"),
        "side": row.get("side"),
        "source": row.get("source"),
        "p_raw": raw_p(row),
        "ask_prob": row.get("ask_prob"),
        "raw_edge_prob": row.get("raw_edge_prob"),
        "abs_d_sigma": row.get("abs_d_sigma"),
        "recross_hazard_score": row.get("recross_hazard_score"),
        "seconds_to_close": row.get("seconds_to_close"),
        "side_won": row.get("side_won"),
        "net_cents": row.get("net_gross_cents_after_entry_fee"),
        "tags": quality_tags(row),
    }


def tag_rollups(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    tags = sorted({tag for row in rows for tag in row.get("tags", [])})
    out = []
    for tag in tags:
        tag_rows = [row for row in rows if tag in (row.get("tags") or [])]
        settled = [row for row in tag_rows if row.get("side_won") is not None]
        out.append({
            "tag": tag,
            "rows": len(tag_rows),
            "settled": len(settled),
            "wins": sum(1 for row in settled if row.get("side_won") is True),
            "losses": sum(1 for row in settled if row.get("side_won") is False),
            "net_cents": sum(float(row.get("net_cents") or 0.0) for row in settled),
            "avg_raw_p": sum(float(row.get("p_raw") or 0.0) for row in tag_rows) / len(tag_rows) if tag_rows else None,
        })
    out.sort(key=lambda row: (-int(row.get("settled") or 0), str(row.get("tag"))))
    return out


def build_report() -> dict[str, Any]:
    state = load_or_create_state()
    timing = market_timing(parse_ts(state["freeze_ts_utc"]))
    forward_markets = timing["clean_forward_markets"]
    all_rows = apply_policy(selected_base_rows(), str(state.get("entry_policy") or DEFAULT_POLICY))
    forward_rows = [row for row in all_rows if str(row.get("market") or "") in forward_markets]
    p70_rows = [row_summary(row) for row in forward_rows if (raw_p(row) or 0.0) >= 0.70]
    return {
        "freeze": state,
        "future_denominator": len(forward_markets),
        "target_entries": len(forward_rows),
        "p70_rows": len(p70_rows),
        "settled_p70_rows": sum(1 for row in p70_rows if row.get("side_won") is not None),
        "tag_rollups": tag_rollups(p70_rows),
        "rows": p70_rows,
        "interpretation": interpretation(p70_rows, forward_rows, forward_markets),
    }


def interpretation(p70_rows: list[dict[str, Any]], forward_rows: list[dict[str, Any]], forward_markets: set[str]) -> list[str]:
    if not forward_markets:
        return ["No clean post-freeze markets exist yet for the p70 quality registry."]
    if not p70_rows:
        return [
            f"The target surface has {len(forward_rows)} entries over {len(forward_markets)} future markets, but no raw p>=0.70 rows yet.",
            "No p70 quality inference is possible until high-confidence rows appear post-freeze.",
        ]
    settled = [row for row in p70_rows if row.get("side_won") is not None]
    return [
        f"The registry has {len(p70_rows)} p70-adjustable rows over {len(forward_markets)} future markets; settled {len(settled)}.",
        "Use tag rollups only as forward evidence; do not tune tag definitions from these rows.",
    ]


def fmt(value: Any) -> str:
    if value is None:
        return "None"
    if isinstance(value, float):
        return f"{value:.6f}"
    return str(value)


def write_md(report: dict[str, Any]) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8")
    lines = [
        "# v28 Frozen Target-Coverage p70 Quality Registry",
        "",
        f"- Freeze timestamp UTC: `{(report.get('freeze') or {}).get('freeze_ts_utc')}`",
        f"- Future denominator/target entries/p70 rows/settled p70: `{report.get('future_denominator')}/{report.get('target_entries')}/{report.get('p70_rows')}/{report.get('settled_p70_rows')}`",
        "",
        "## Current Read",
        "",
    ]
    for note in report.get("interpretation") or []:
        lines.append(f"- {note}")
    lines.extend([
        "",
        "## Tag Rollups",
        "",
        "| tag | rows | settled | W/L | net c | avg raw p |",
        "|---|---:|---:|---:|---:|---:|",
    ])
    for row in report.get("tag_rollups") or []:
        lines.append(
            f"| {row.get('tag')} | {row.get('rows')} | {row.get('settled')} | "
            f"{row.get('wins')}/{row.get('losses')} | {fmt(row.get('net_cents'))} | {fmt(row.get('avg_raw_p'))} |"
        )
    lines.extend([
        "",
        "## Rows",
        "",
        "| market | side | p raw | ask | edge | abs d | recross | stc | won | net c | tags |",
        "|---|---|---:|---:|---:|---:|---:|---:|---|---:|---|",
    ])
    for row in report.get("rows") or []:
        lines.append(
            f"| {row.get('market')} | {row.get('side')} | {fmt(row.get('p_raw'))} | "
            f"{fmt(row.get('ask_prob'))} | {fmt(row.get('raw_edge_prob'))} | {fmt(row.get('abs_d_sigma'))} | "
            f"{fmt(row.get('recross_hazard_score'))} | {fmt(row.get('seconds_to_close'))} | {row.get('side_won')} | "
            f"{fmt(row.get('net_cents'))} | {', '.join(row.get('tags') or [])} |"
        )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    report = build_report()
    write_md(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
