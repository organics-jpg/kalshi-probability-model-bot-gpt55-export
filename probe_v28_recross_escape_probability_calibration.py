"""Probability calibration overlays for the p52 recross-escape candidate.

Research-only. This does not change live bot logic or place orders.

The recross-escape candidate improves discovery P&L, but its raw p_eff Brier is
slightly worse than raw p52. This probe keeps the selected trades fixed and
tests whether the FV probability attached to those trades should be calibrated
differently.
"""
from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
RECROSS_JSON = OUT_DIR / "v28_raw_p52_recross_escape_candidate_latest.json"
OUT_JSON = OUT_DIR / "v28_recross_escape_probability_calibration_latest.json"
OUT_MD = OUT_DIR / "v28_recross_escape_probability_calibration_latest.md"

POLICY = "p52_recross_escape_opp240_oppedge5_keep"


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
        return float(value)
    except (TypeError, ValueError):
        return None


def clamp(value: float) -> float:
    return max(0.000001, min(0.999999, value))


def logit(p: float) -> float:
    p = clamp(p)
    return math.log(p / (1.0 - p))


def inv_logit(x: float) -> float:
    return clamp(1.0 / (1.0 + math.exp(-x)))


def p_raw(row: dict[str, Any]) -> float:
    return clamp(as_float(row.get("p_eff")) or as_float(row.get("raw_p_eff")) or 0.5)


def p_plus(row: dict[str, Any], amount: float) -> float:
    return clamp(p_raw(row) + amount)


def p_logit_scale(row: dict[str, Any], scale: float) -> float:
    return inv_logit(logit(p_raw(row)) * scale)


def p_mode_calibrated(row: dict[str, Any]) -> float:
    p = p_raw(row)
    mode = str(row.get("mode") or "")
    if mode == "danger_follow_opposite":
        return clamp(p + 0.06)
    if mode == "danger_keep_high_edge":
        return clamp(p + 0.04)
    if mode == "danger_no_opposite_keep":
        return clamp(p + 0.02)
    return clamp(p + 0.04)


def p_conservative_mode(row: dict[str, Any]) -> float:
    p = p_raw(row)
    mode = str(row.get("mode") or "")
    if mode == "danger_no_opposite_keep":
        return clamp(p)
    if mode == "danger_follow_opposite":
        return clamp(p + 0.04)
    return clamp(p + 0.03)


TRANSFORMS = {
    "raw_probability": p_raw,
    "plus03_probability": lambda row: p_plus(row, 0.03),
    "plus05_probability": lambda row: p_plus(row, 0.05),
    "logit110_probability": lambda row: p_logit_scale(row, 1.10),
    "logit125_probability": lambda row: p_logit_scale(row, 1.25),
    "mode_calibrated_probability": p_mode_calibrated,
    "conservative_mode_probability": p_conservative_mode,
}


def logloss(p: float, y: float) -> float:
    p = clamp(p)
    return -(y * math.log(p) + (1.0 - y) * math.log(1.0 - p))


def selected_rows() -> list[dict[str, Any]]:
    payload = load_json(RECROSS_JSON)
    rows = payload.get("rows") if isinstance(payload.get("rows"), list) else []
    return [row for row in rows if row.get("policy") == POLICY]


def summarize(name: str, rows: list[dict[str, Any]]) -> dict[str, Any]:
    fn = TRANSFORMS[name]
    settled = [row for row in rows if row.get("side_won") is not None]
    probs = [fn(row) for row in settled]
    outcomes = [1.0 if row.get("side_won") is True else 0.0 for row in settled]
    briers = [(p - y) ** 2 for p, y in zip(probs, outcomes)]
    losses = [logloss(p, y) for p, y in zip(probs, outcomes)]
    ece = expected_calibration_error(probs, outcomes)
    return {
        "probability": name,
        "count": len(settled),
        "wins": sum(1 for row in settled if row.get("side_won") is True),
        "losses": sum(1 for row in settled if row.get("side_won") is False),
        "avg_p": sum(probs) / len(probs) if probs else None,
        "avg_brier": sum(briers) / len(briers) if briers else None,
        "avg_logloss": sum(losses) / len(losses) if losses else None,
        "ece": ece,
        "by_mode": summarize_by_mode(name, settled),
    }


def expected_calibration_error(probs: list[float], outcomes: list[float]) -> float | None:
    if not probs:
        return None
    bins = [(0.0, 0.6), (0.6, 0.7), (0.7, 0.8), (0.8, 0.9), (0.9, 1.01)]
    total = 0.0
    for lo, hi in bins:
        idx = [i for i, p in enumerate(probs) if lo <= p < hi]
        if not idx:
            continue
        conf = sum(probs[i] for i in idx) / len(idx)
        acc = sum(outcomes[i] for i in idx) / len(idx)
        total += len(idx) / len(probs) * abs(conf - acc)
    return total


def summarize_by_mode(name: str, rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    fn = TRANSFORMS[name]
    by_mode: dict[str, list[dict[str, Any]]] = {}
    for row in rows:
        by_mode.setdefault(str(row.get("mode") or "unknown"), []).append(row)
    summaries: list[dict[str, Any]] = []
    for mode, mode_rows in sorted(by_mode.items()):
        probs = [fn(row) for row in mode_rows]
        outcomes = [1.0 if row.get("side_won") is True else 0.0 for row in mode_rows]
        briers = [(p - y) ** 2 for p, y in zip(probs, outcomes)]
        summaries.append({
            "mode": mode,
            "count": len(mode_rows),
            "wins": sum(1 for row in mode_rows if row.get("side_won") is True),
            "losses": sum(1 for row in mode_rows if row.get("side_won") is False),
            "avg_p": sum(probs) / len(probs) if probs else None,
            "avg_brier": sum(briers) / len(briers) if briers else None,
        })
    return summaries


def build_report() -> dict[str, Any]:
    rows = selected_rows()
    summaries = [summarize(name, rows) for name in TRANSFORMS]
    raw = next((row for row in summaries if row["probability"] == "raw_probability"), {})
    for row in summaries:
        row["brier_delta_vs_raw"] = delta(row.get("avg_brier"), raw.get("avg_brier"))
        row["logloss_delta_vs_raw"] = delta(row.get("avg_logloss"), raw.get("avg_logloss"))
        row["ece_delta_vs_raw"] = delta(row.get("ece"), raw.get("ece"))
    summaries.sort(key=lambda row: (
        float(row.get("avg_brier") if row.get("avg_brier") is not None else 999.0),
        float(row.get("avg_logloss") if row.get("avg_logloss") is not None else 999.0),
    ))
    lift_plateau = build_lift_plateau(rows)
    plus05_jackknife = build_jackknife(rows, 0.05)
    return {
        "policy": POLICY,
        "entries": len(rows),
        "settled": sum(1 for row in rows if row.get("side_won") is not None),
        "summaries": summaries,
        "lift_plateau": lift_plateau,
        "plus05_jackknife": plus05_jackknife,
    }


def score_lift(rows: list[dict[str, Any]], lift: float) -> dict[str, Any]:
    settled = [row for row in rows if row.get("side_won") is not None]
    probs = [clamp(p_raw(row) + lift) for row in settled]
    outcomes = [1.0 if row.get("side_won") is True else 0.0 for row in settled]
    briers = [(p - y) ** 2 for p, y in zip(probs, outcomes)]
    losses = [logloss(p, y) for p, y in zip(probs, outcomes)]
    return {
        "lift": lift,
        "count": len(settled),
        "avg_p": sum(probs) / len(probs) if probs else None,
        "avg_brier": sum(briers) / len(briers) if briers else None,
        "avg_logloss": sum(losses) / len(losses) if losses else None,
    }


def build_lift_plateau(rows: list[dict[str, Any]]) -> dict[str, Any]:
    lifts = [i / 100.0 for i in range(-5, 16)]
    scored = [score_lift(rows, lift) for lift in lifts]
    raw = next((row for row in scored if abs(float(row["lift"])) < 0.000001), {})
    for row in scored:
        row["brier_delta_vs_raw"] = delta(row.get("avg_brier"), raw.get("avg_brier"))
        row["logloss_delta_vs_raw"] = delta(row.get("avg_logloss"), raw.get("avg_logloss"))
    best = min(
        scored,
        key=lambda row: float(row.get("avg_brier") if row.get("avg_brier") is not None else 999.0),
        default={},
    )
    improving = [
        row["lift"]
        for row in scored
        if row.get("brier_delta_vs_raw") is not None and float(row["brier_delta_vs_raw"]) < 0.0
    ]
    return {
        "best_lift": best.get("lift"),
        "best_brier": best.get("avg_brier"),
        "improving_lifts": improving,
        "rows": scored,
    }


def build_jackknife(rows: list[dict[str, Any]], lift: float) -> dict[str, Any]:
    settled = [row for row in rows if row.get("side_won") is not None]
    markets = sorted({str(row.get("market") or "") for row in settled})
    slices: list[dict[str, Any]] = []
    for market in markets:
        kept = [row for row in settled if str(row.get("market") or "") != market]
        raw = score_lift(kept, 0.0)
        lifted = score_lift(kept, lift)
        slices.append({
            "left_out_market": market,
            "kept_count": len(kept),
            "brier_delta_vs_raw": delta(lifted.get("avg_brier"), raw.get("avg_brier")),
            "logloss_delta_vs_raw": delta(lifted.get("avg_logloss"), raw.get("avg_logloss")),
        })
    brier_deltas = [float(row["brier_delta_vs_raw"]) for row in slices if row.get("brier_delta_vs_raw") is not None]
    logloss_deltas = [float(row["logloss_delta_vs_raw"]) for row in slices if row.get("logloss_delta_vs_raw") is not None]
    return {
        "lift": lift,
        "slices": slices,
        "slice_count": len(slices),
        "brier_improved_slices": sum(1 for value in brier_deltas if value < 0.0),
        "logloss_improved_slices": sum(1 for value in logloss_deltas if value < 0.0),
        "worst_brier_delta": max(brier_deltas) if brier_deltas else None,
        "worst_logloss_delta": max(logloss_deltas) if logloss_deltas else None,
    }


def delta(value: Any, base: Any) -> float | None:
    if value is None or base is None:
        return None
    return float(value) - float(base)


def fmt(value: Any) -> str:
    if value is None:
        return "None"
    if isinstance(value, float):
        return f"{value:.6f}"
    return str(value)


def write_report(report: dict[str, Any]) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    lines = [
        "# v28 Recross-Escape Probability Calibration",
        "",
        "Fixed-row probability calibration for the p52 recross-escape candidate. This scores FV accuracy only; P&L is unchanged.",
        "",
        f"- Policy: `{report.get('policy')}`",
        f"- Entries/settled: `{report.get('entries')}/{report.get('settled')}`",
        "",
        "## Scorecard",
        "",
        "| probability | count | W/L | avg p | brier | brier d | logloss | logloss d | ece | ece d |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for row in report.get("summaries") or []:
        lines.append(
            f"| {row.get('probability')} | {row.get('count')} | {row.get('wins')}/{row.get('losses')} | "
            f"{fmt(row.get('avg_p'))} | {fmt(row.get('avg_brier'))} | {fmt(row.get('brier_delta_vs_raw'))} | "
            f"{fmt(row.get('avg_logloss'))} | {fmt(row.get('logloss_delta_vs_raw'))} | "
            f"{fmt(row.get('ece'))} | {fmt(row.get('ece_delta_vs_raw'))} |"
        )
    lines.extend(["", "## Best By Mode", ""])
    best = (report.get("summaries") or [{}])[0]
    for row in best.get("by_mode") or []:
        lines.append(
            f"- `{row.get('mode')}`: count `{row.get('count')}`, W/L `{row.get('wins')}/{row.get('losses')}`, "
            f"avg p `{fmt(row.get('avg_p'))}`, brier `{fmt(row.get('avg_brier'))}`"
        )
    plateau = report.get("lift_plateau") or {}
    lines.extend([
        "",
        "## Lift Plateau",
        "",
        f"- Best lift: `{fmt(plateau.get('best_lift'))}` with Brier `{fmt(plateau.get('best_brier'))}`",
        f"- Improving lifts vs raw: `{plateau.get('improving_lifts')}`",
        "",
        "| lift | avg p | brier | brier d | logloss | logloss d |",
        "|---:|---:|---:|---:|---:|---:|",
    ])
    for row in plateau.get("rows") or []:
        if row.get("lift") in {-0.05, -0.03, 0.0, 0.03, 0.05, 0.07, 0.10, 0.15}:
            lines.append(
                f"| {fmt(row.get('lift'))} | {fmt(row.get('avg_p'))} | {fmt(row.get('avg_brier'))} | "
                f"{fmt(row.get('brier_delta_vs_raw'))} | {fmt(row.get('avg_logloss'))} | "
                f"{fmt(row.get('logloss_delta_vs_raw'))} |"
            )
    jackknife = report.get("plus05_jackknife") or {}
    lines.extend([
        "",
        "## Plus05 Jackknife",
        "",
        f"- Slices: `{jackknife.get('slice_count')}`",
        f"- Brier improved slices: `{jackknife.get('brier_improved_slices')}`",
        f"- Logloss improved slices: `{jackknife.get('logloss_improved_slices')}`",
        f"- Worst Brier delta: `{fmt(jackknife.get('worst_brier_delta'))}`",
        f"- Worst logloss delta: `{fmt(jackknife.get('worst_logloss_delta'))}`",
    ])
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    report = build_report()
    write_report(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
