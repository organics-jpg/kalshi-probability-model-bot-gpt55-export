"""Side-asymmetry FV diagnostic for the v28 target-coverage surface.

Research-only; no live bot changes or orders.

Physics hypothesis:
    In BTC 15m boundary markets, YES and NO are not always symmetric after
    conditioning on path state. NO entries can represent "price has not crossed
    yet" in an early unresolved path, while YES entries often represent "price
    has already escaped." This probe checks predeclared side/path buckets and
    asks where the raw FV is directionally miscalibrated or economically toxic.

This is diagnostic only. It does not optimize thresholds or promote a rule.
"""
from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any

from probe_v28_boundary_clock_hazard_repair import clock_composite
from probe_v28_target_coverage_pnl_attribution import forward_rows, net_cents


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
OUT_JSON = OUT_DIR / "v28_side_asymmetry_fv_diagnostic_latest.json"
OUT_MD = OUT_DIR / "v28_side_asymmetry_fv_diagnostic_latest.md"

MIN_BUCKET_SETTLED = 3


def as_float(value: Any) -> float | None:
    if value is None or value == "":
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def p_bucket(p: float | None) -> str:
    if p is None:
        return "p_unknown"
    if p < 0.60:
        return "p50_60"
    if p < 0.70:
        return "p60_70"
    if p < 0.80:
        return "p70_80"
    return "p80_100"


def distance_bucket(abs_d: float | None) -> str:
    if abs_d is None:
        return "d_unknown"
    if abs_d < 0.30:
        return "near_boundary"
    if abs_d < 0.55:
        return "mid_boundary"
    if abs_d < 0.85:
        return "outer_boundary"
    return "far_boundary"


def recross_bucket(rec: float | None) -> str:
    if rec is None:
        return "rec_unknown"
    if rec < 0.45:
        return "low_recross"
    if rec < 0.75:
        return "mid_recross"
    return "high_recross"


def time_bucket(stc: float | None) -> str:
    if stc is None:
        return "stc_unknown"
    if stc >= 780.0:
        return "early"
    if stc <= 480.0:
        return "late"
    return "middle"


def clipped_probability(value: float) -> float:
    return min(0.999, max(0.001, value))


def brier(p: float, won: bool) -> float:
    y = 1.0 if won else 0.0
    return (p - y) ** 2


def logloss(p: float, won: bool) -> float:
    p = clipped_probability(p)
    return -math.log(p if won else 1.0 - p)


def row_view(row: dict[str, Any]) -> dict[str, Any]:
    p = as_float(row.get("p_side"))
    abs_d = as_float(row.get("abs_d_sigma"))
    rec = as_float(row.get("recross_hazard_score"))
    stc = as_float(row.get("seconds_to_close"))
    return {
        "market": row.get("market"),
        "source": row.get("source"),
        "side": str(row.get("side") or "").lower(),
        "side_won": row.get("side_won"),
        "net_cents": net_cents(row),
        "p_side": p,
        "ask_prob": as_float(row.get("ask_prob")),
        "edge_prob": as_float(row.get("raw_edge_prob")),
        "seconds_to_close": stc,
        "abs_d_sigma": abs_d,
        "recross_hazard_score": rec,
        "clock_hazard": clock_composite(row),
        "p_bucket": p_bucket(p),
        "distance_bucket": distance_bucket(abs_d),
        "recross_bucket": recross_bucket(rec),
        "time_bucket": time_bucket(stc),
    }


def bucket_keys(row: dict[str, Any]) -> list[str]:
    view = row_view(row)
    side = view["side"] or "side_unknown"
    keys = [
        f"side:{side}",
        f"side:{side}|{view['p_bucket']}",
        f"side:{side}|{view['p_bucket']}|{view['distance_bucket']}",
        f"side:{side}|{view['p_bucket']}|{view['distance_bucket']}|{view['recross_bucket']}",
        f"side:{side}|{view['p_bucket']}|{view['distance_bucket']}|{view['time_bucket']}",
        f"side:{side}|{view['p_bucket']}|{view['distance_bucket']}|clock:{view['clock_hazard']}",
    ]
    if view["source"]:
        keys.append(f"side:{side}|source:{view['source']}")
    return keys


def summarize_bucket(name: str, rows: list[dict[str, Any]]) -> dict[str, Any]:
    settled = [row_view(row) for row in rows if row.get("side_won") is not None]
    raw_brier = 0.0
    shrink_brier = 0.0
    raw_logloss = 0.0
    shrink_logloss = 0.0
    wins = 0
    losses = 0
    for row in settled:
        p = row["p_side"]
        if p is None:
            continue
        won = row["side_won"] is True
        wins += 1 if won else 0
        losses += 0 if won else 1
        raw_brier += brier(p, won)
        shrink_brier += brier(0.50, won)
        raw_logloss += logloss(p, won)
        shrink_logloss += logloss(0.50, won)
    scored = wins + losses
    net = sum(float(row.get("net_cents") or 0.0) for row in settled)
    avg_p = sum(float(row["p_side"] or 0.0) for row in settled) / scored if scored else None
    empirical = wins / scored if scored else None
    return {
        "bucket": name,
        "rows": len(rows),
        "settled": scored,
        "wins": wins,
        "losses": losses,
        "win_rate": empirical,
        "avg_p_side": avg_p,
        "calibration_gap": None if avg_p is None or empirical is None else avg_p - empirical,
        "net_cents": net,
        "avg_net_cents": net / scored if scored else None,
        "brier_delta_shrink_to_50": shrink_brier - raw_brier if scored else None,
        "logloss_delta_shrink_to_50": shrink_logloss - raw_logloss if scored else None,
        "rows_view": settled,
    }


def build_report() -> dict[str, Any]:
    rows, denominator = forward_rows()
    groups: dict[str, list[dict[str, Any]]] = {}
    for row in rows:
        for key in bucket_keys(row):
            groups.setdefault(key, []).append(row)
    bucket_rows = [
        summarize_bucket(name, group)
        for name, group in groups.items()
    ]
    suspicious = [
        row for row in bucket_rows
        if int(row.get("settled") or 0) >= MIN_BUCKET_SETTLED
        and float(row.get("net_cents") or 0.0) < 0.0
        and (as_float(row.get("calibration_gap")) or 0.0) > 0.05
    ]
    suspicious.sort(
        key=lambda row: (
            float(row.get("net_cents") or 0.0),
            -float(row.get("calibration_gap") or 0.0),
        )
    )
    return {
        "diagnostic": "side_asymmetry_fv",
        "policy": "raw_p50_turbulence_valve_edge4_p60_recross75_near25",
        "forward_denominator": denominator,
        "entries": len(rows),
        "settled": sum(1 for row in rows if row.get("side_won") is not None),
        "min_bucket_settled": MIN_BUCKET_SETTLED,
        "suspicious_buckets": suspicious[:20],
        "all_buckets": sorted(
            bucket_rows,
            key=lambda row: (
                0 if int(row.get("settled") or 0) >= MIN_BUCKET_SETTLED else 1,
                float(row.get("net_cents") or 0.0),
            ),
        ),
        "interpretation": interpretation(suspicious, rows, denominator),
    }


def interpretation(suspicious: list[dict[str, Any]], rows: list[dict[str, Any]], denominator: int) -> list[str]:
    out = [
        f"Target surface has {len(rows)} entries over {denominator} forward markets.",
        "Buckets are predeclared by side, p-range, distance, recross, time, source, and boundary-clock state.",
    ]
    if suspicious:
        top = suspicious[0]
        out.append(
            f"Top suspicious bucket is {top.get('bucket')} with settled={top.get('settled')}, net={top.get('net_cents')}c, avg_p={top.get('avg_p_side')}, win_rate={top.get('win_rate')}."
        )
        out.append("This is diagnostic only; promote nothing until a frozen future registry validates the bucket.")
    else:
        out.append("No predeclared side-asymmetry bucket has enough settled rows plus negative PnL plus overconfidence.")
    return out


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
        "# v28 Side-Asymmetry FV Diagnostic",
        "",
        "Research-only: no live bot changes and no orders.",
        "",
        f"- Policy: `{report.get('policy')}`",
        f"- Forward denominator: `{report.get('forward_denominator')}`",
        f"- Entries/settled: `{report.get('entries')}/{report.get('settled')}`",
        f"- Min bucket settled: `{report.get('min_bucket_settled')}`",
        "",
        "## Interpretation",
        "",
    ]
    for note in report.get("interpretation") or []:
        lines.append(f"- {note}")
    lines.extend([
        "",
        "## Suspicious Buckets",
        "",
        "| bucket | rows | settled | W/L | avg p | win rate | cal gap | net c | shrink50 brier delta |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|",
    ])
    for row in report.get("suspicious_buckets") or []:
        lines.append(
            f"| {row.get('bucket')} | {row.get('rows')} | {row.get('settled')} | "
            f"{row.get('wins')}/{row.get('losses')} | {fmt(row.get('avg_p_side'))} | "
            f"{fmt(row.get('win_rate'))} | {fmt(row.get('calibration_gap'))} | "
            f"{fmt(row.get('net_cents'))} | {fmt(row.get('brier_delta_shrink_to_50'))} |"
        )
    lines.extend([
        "",
        "## Worst Rows From Top Bucket",
        "",
        "| market | source | side | won | net c | p | ask | edge | stc | abs d | recross | clock |",
        "|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|---|",
    ])
    top = (report.get("suspicious_buckets") or [{}])[0]
    rows_view = sorted(top.get("rows_view") or [], key=lambda row: float(row.get("net_cents") or 0.0))[:12]
    for row in rows_view:
        lines.append(
            f"| {row.get('market')} | {row.get('source')} | {row.get('side')} | {row.get('side_won')} | "
            f"{fmt(row.get('net_cents'))} | {fmt(row.get('p_side'))} | {fmt(row.get('ask_prob'))} | "
            f"{fmt(row.get('edge_prob'))} | {fmt(row.get('seconds_to_close'))} | "
            f"{fmt(row.get('abs_d_sigma'))} | {fmt(row.get('recross_hazard_score'))} | {row.get('clock_hazard')} |"
        )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    report = build_report()
    write_md(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
