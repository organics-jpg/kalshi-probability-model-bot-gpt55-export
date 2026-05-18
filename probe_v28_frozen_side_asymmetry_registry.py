"""Frozen registry for v28 side-asymmetry residual FV risk.

Research-only; no live bot changes or orders.

This is not a candidate. It freezes a physics bucket surfaced by the
side-asymmetry diagnostic so future rows can decide whether the effect is real:
NO-side, p60-70, mid-boundary, mid-recross rows may represent unresolved
"has not crossed yet" path risk rather than a durable NO edge.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from probe_v28_boundary_clock_hazard_repair import clock_composite
from probe_v28_frozen_forward_candidates import market_timing, parse_ts
from probe_v28_target_coverage_pnl_attribution import forward_rows, net_cents


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
STATE_JSON = OUT_DIR / "v28_frozen_side_asymmetry_registry_state.json"
OUT_JSON = OUT_DIR / "v28_frozen_side_asymmetry_registry_latest.json"
OUT_MD = OUT_DIR / "v28_frozen_side_asymmetry_registry_latest.md"


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
        state = load_json(STATE_JSON)
        if state.get("freeze_ts_utc"):
            return state
    state = {
        "freeze_ts_utc": utc_now_iso(),
        "registry": "side_asymmetry_no_p60_70_midboundary_midrecross",
        "rule": "side=no, 0.60<=p_side<0.70, 0.30<=abs_d_sigma<0.55, 0.45<=recross_hazard_score<0.75",
        "hypothesis": "Mid-confidence NO at moderate distance can be unresolved boundary hesitation, not a mirror image of YES escape.",
        "promotion_note": "Registry only; do not add an FV penalty until future rows show enough settled negative expectancy or overconfidence.",
    }
    STATE_JSON.write_text(json.dumps(state, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return state


def as_float(value: Any) -> float | None:
    if value is None or value == "":
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def is_bucket(row: dict[str, Any]) -> bool:
    p = as_float(row.get("p_side"))
    abs_d = as_float(row.get("abs_d_sigma"))
    recross = as_float(row.get("recross_hazard_score"))
    return (
        str(row.get("side") or "").lower() == "no"
        and p is not None and 0.60 <= p < 0.70
        and abs_d is not None and 0.30 <= abs_d < 0.55
        and recross is not None and 0.45 <= recross < 0.75
    )


def future_target_rows(freeze_ts: str) -> tuple[list[dict[str, Any]], int]:
    freeze_dt = parse_ts(freeze_ts)
    timing = market_timing(freeze_dt)
    markets = set(timing["clean_forward_markets"])
    rows, _old_denominator = forward_rows()
    rows = [row for row in rows if str(row.get("market") or "") in markets]
    return rows, len(markets)


def summarize(rows: list[dict[str, Any]], denominator: int) -> dict[str, Any]:
    settled = [row for row in rows if row.get("side_won") is not None]
    net = sum(float(net_cents(row) or 0.0) for row in settled)
    wins = sum(1 for row in settled if row.get("side_won") is True)
    avg_p = (
        sum(float(as_float(row.get("p_side")) or 0.0) for row in settled) / len(settled)
        if settled
        else None
    )
    win_rate = wins / len(settled) if settled else None
    return {
        "entries": len(rows),
        "settled": len(settled),
        "wins": wins,
        "losses": sum(1 for row in settled if row.get("side_won") is False),
        "coverage_pct": 100.0 * len(rows) / denominator if denominator else None,
        "net_cents": net,
        "avg_net_cents": net / len(settled) if settled else None,
        "avg_p_side": avg_p,
        "win_rate": win_rate,
        "calibration_gap": None if avg_p is None or win_rate is None else avg_p - win_rate,
    }


def compact(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "market": row.get("market"),
        "ts_wall": row.get("ts_wall"),
        "source": row.get("source"),
        "side": row.get("side"),
        "side_won": row.get("side_won"),
        "net_cents": net_cents(row),
        "p_side": row.get("p_side"),
        "ask_prob": row.get("ask_prob"),
        "raw_edge_prob": row.get("raw_edge_prob"),
        "seconds_to_close": row.get("seconds_to_close"),
        "abs_d_sigma": row.get("abs_d_sigma"),
        "recross_hazard_score": row.get("recross_hazard_score"),
        "clock_hazard": clock_composite(row),
    }


def build_report() -> dict[str, Any]:
    state = load_or_create_state()
    rows, denominator = future_target_rows(str(state["freeze_ts_utc"]))
    bucket = [row for row in rows if is_bucket(row)]
    non_clock_bucket = [row for row in bucket if not clock_composite(row)]
    return {
        "freeze": state,
        "future_denominator": denominator,
        "target_summary": summarize(rows, denominator),
        "bucket_summary": summarize(bucket, denominator),
        "non_clock_bucket_summary": summarize(non_clock_bucket, denominator),
        "rows": [compact(row) for row in bucket],
        "interpretation": interpretation(bucket, non_clock_bucket, denominator),
    }


def interpretation(bucket: list[dict[str, Any]], non_clock_bucket: list[dict[str, Any]], denominator: int) -> list[str]:
    settled = [row for row in bucket if row.get("side_won") is not None]
    non_clock_settled = [row for row in non_clock_bucket if row.get("side_won") is not None]
    return [
        f"Future denominator is {denominator}; side-asymmetry bucket has {len(bucket)} entries and {len(settled)} settled rows.",
        f"Non-clock subset has {len(non_clock_bucket)} entries and {len(non_clock_settled)} settled rows.",
        "This is a registry only; it becomes a candidate only after enough future evidence accumulates.",
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
    freeze = report.get("freeze") or {}
    target = report.get("target_summary") or {}
    bucket = report.get("bucket_summary") or {}
    non_clock = report.get("non_clock_bucket_summary") or {}
    lines = [
        "# v28 Frozen Side-Asymmetry Registry",
        "",
        f"- Freeze timestamp UTC: `{freeze.get('freeze_ts_utc')}`",
        f"- Registry: `{freeze.get('registry')}`",
        f"- Rule: `{freeze.get('rule')}`",
        f"- Future denominator: `{report.get('future_denominator')}`",
        f"- Target entries/settled: `{target.get('entries')}/{target.get('settled')}`",
        f"- Bucket entries/settled/WL/net/cal gap: `{bucket.get('entries')}/{bucket.get('settled')}/{bucket.get('wins')}/{bucket.get('losses')}/{fmt(bucket.get('net_cents'))}c/{fmt(bucket.get('calibration_gap'))}`",
        f"- Non-clock entries/settled/WL/net/cal gap: `{non_clock.get('entries')}/{non_clock.get('settled')}/{non_clock.get('wins')}/{non_clock.get('losses')}/{fmt(non_clock.get('net_cents'))}c/{fmt(non_clock.get('calibration_gap'))}`",
        "",
        "## Interpretation",
        "",
    ]
    for note in report.get("interpretation") or []:
        lines.append(f"- {note}")
    lines.extend([
        "",
        "## Rows",
        "",
        "| market | source | side | won | net c | p | ask | edge | stc | abs d | recross | clock |",
        "|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|---|",
    ])
    for row in report.get("rows") or []:
        lines.append(
            f"| {row.get('market')} | {row.get('source')} | {row.get('side')} | {row.get('side_won')} | "
            f"{fmt(row.get('net_cents'))} | {fmt(row.get('p_side'))} | {fmt(row.get('ask_prob'))} | "
            f"{fmt(row.get('raw_edge_prob'))} | {fmt(row.get('seconds_to_close'))} | "
            f"{fmt(row.get('abs_d_sigma'))} | {fmt(row.get('recross_hazard_score'))} | {row.get('clock_hazard')} |"
        )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    report = build_report()
    write_md(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
