"""Frozen probability calibration for the p52 recross-escape challenger.

Research-only. Scores only post-freeze selected rows from the frozen recross
gate and compares probability overlays against raw p_eff on the same rows.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from probe_v28_recross_escape_probability_calibration import TRANSFORMS, expected_calibration_error, logloss


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
FROZEN_RECROSS_JSON = OUT_DIR / "v28_frozen_raw_p52_recross_escape_challenger_latest.json"
OUT_JSON = OUT_DIR / "v28_frozen_recross_escape_probability_calibration_latest.json"
OUT_MD = OUT_DIR / "v28_frozen_recross_escape_probability_calibration_latest.md"
POLICY = "p52_recross_escape_opp240_oppedge5_keep"


def load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
    return payload if isinstance(payload, dict) else {}


def selected_rows() -> list[dict[str, Any]]:
    payload = load_json(FROZEN_RECROSS_JSON)
    for row in payload.get("summary") or []:
        if row.get("policy") == POLICY:
            selected = row.get("selected_forward_rows")
            return selected if isinstance(selected, list) else []
    return []


def summarize(name: str, rows: list[dict[str, Any]]) -> dict[str, Any]:
    fn = TRANSFORMS[name]
    settled = [row for row in rows if row.get("side_won") is not None]
    probs = [fn(row) for row in settled]
    outcomes = [1.0 if row.get("side_won") is True else 0.0 for row in settled]
    briers = [(p - y) ** 2 for p, y in zip(probs, outcomes)]
    losses = [logloss(p, y) for p, y in zip(probs, outcomes)]
    return {
        "probability": name,
        "entries": len(rows),
        "settled": len(settled),
        "wins": sum(1 for row in settled if row.get("side_won") is True),
        "losses": sum(1 for row in settled if row.get("side_won") is False),
        "avg_p": sum(probs) / len(probs) if probs else None,
        "avg_brier": sum(briers) / len(briers) if briers else None,
        "avg_logloss": sum(losses) / len(losses) if losses else None,
        "ece": expected_calibration_error(probs, outcomes),
    }


def delta(value: Any, base: Any) -> float | None:
    if value is None or base is None:
        return None
    return float(value) - float(base)


def build_report() -> dict[str, Any]:
    payload = load_json(FROZEN_RECROSS_JSON)
    rows = selected_rows()
    summaries = [summarize(name, rows) for name in TRANSFORMS]
    raw = next((row for row in summaries if row.get("probability") == "raw_probability"), {})
    for row in summaries:
        row["brier_delta_vs_raw"] = delta(row.get("avg_brier"), raw.get("avg_brier"))
        row["logloss_delta_vs_raw"] = delta(row.get("avg_logloss"), raw.get("avg_logloss"))
        row["ece_delta_vs_raw"] = delta(row.get("ece"), raw.get("ece"))
    summaries.sort(key=lambda row: (
        float(row.get("avg_brier") if row.get("avg_brier") is not None else 999.0),
        float(row.get("avg_logloss") if row.get("avg_logloss") is not None else 999.0),
    ))
    return {
        "source_freeze_ts": payload.get("freeze_ts"),
        "source_forward_market_denominator": payload.get("forward_market_denominator"),
        "policy": POLICY,
        "entries": len(rows),
        "settled": sum(1 for row in rows if row.get("side_won") is not None),
        "summaries": summaries,
    }


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
        "# v28 Frozen Recross-Escape Probability Calibration",
        "",
        "Forward-only fixed-row FV calibration for the recross-escape challenger.",
        "",
        f"- Source freeze timestamp UTC: `{report.get('source_freeze_ts')}`",
        f"- Source forward denominator: `{report.get('source_forward_market_denominator')}`",
        f"- Policy: `{report.get('policy')}`",
        f"- Entries/settled: `{report.get('entries')}/{report.get('settled')}`",
        "",
        "| probability | entries | settled | W/L | avg p | brier | brier d | logloss | logloss d | ece | ece d |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for row in report.get("summaries") or []:
        lines.append(
            f"| {row.get('probability')} | {row.get('entries')} | {row.get('settled')} | "
            f"{row.get('wins')}/{row.get('losses')} | {fmt(row.get('avg_p'))} | "
            f"{fmt(row.get('avg_brier'))} | {fmt(row.get('brier_delta_vs_raw'))} | "
            f"{fmt(row.get('avg_logloss'))} | {fmt(row.get('logloss_delta_vs_raw'))} | "
            f"{fmt(row.get('ece'))} | {fmt(row.get('ece_delta_vs_raw'))} |"
        )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    report = build_report()
    write_report(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
