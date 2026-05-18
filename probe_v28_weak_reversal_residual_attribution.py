"""Residual attribution for the weak-boundary reversal bakeoff.

Research-only; no live bot changes or orders.

The reversal family removes one obvious false-conviction cluster but remains
negative. This script asks what the remaining losses have in common, using
coarse predeclared physics tags instead of tuning another rule.
"""
from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
INPUT_JSON = OUT_DIR / "v28_weak_boundary_reversal_bakeoff_latest.json"
OUT_JSON = OUT_DIR / "v28_weak_reversal_residual_attribution_latest.json"
OUT_MD = OUT_DIR / "v28_weak_reversal_residual_attribution_latest.md"


def as_float(value: Any) -> float | None:
    if value is None or value == "":
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def bucket(value: Any, cuts: list[float], labels: list[str]) -> str:
    v = as_float(value)
    if v is None:
        return "missing"
    for cut, label in zip(cuts, labels):
        if v < cut:
            return label
    return labels[-1]


def row_tags(row: dict[str, Any]) -> list[str]:
    side = str(row.get("side") or "missing")
    source = str(row.get("source") or "missing")
    return [
        f"side_{side}",
        f"source_{source}",
        f"ask_{bucket(row.get('ask_prob'), [0.45, 0.55, 0.65, 0.75], ['lt45', '45_55', '55_65', '65_75', 'gte75'])}",
        f"edge_{bucket(row.get('raw_edge_prob'), [0.02, 0.05, 0.08, 0.12], ['lt2pp', '2_5pp', '5_8pp', '8_12pp', 'gte12pp'])}",
        f"p_{bucket(row.get('p_side'), [0.58, 0.65, 0.72, 0.80], ['lt58', '58_65', '65_72', '72_80', 'gte80'])}",
        f"recross_{bucket(row.get('recross_hazard_score'), [0.50, 0.65, 0.80, 0.95], ['lt50', '50_65', '65_80', '80_95', 'gte95'])}",
        f"absd_{bucket(row.get('abs_d_sigma'), [0.20, 0.35, 0.55, 0.80], ['lt20', '20_35', '35_55', '55_80', 'gte80'])}",
        f"stc_{bucket(row.get('seconds_to_close'), [600, 750, 850], ['lt600', '600_750', '750_850', 'gte850'])}",
        f"delay_{bucket(row.get('replacement_delay_seconds'), [1, 120, 240], ['none', 'lt120', '120_240', 'gte240'])}",
    ]


def summarize(rows: list[dict[str, Any]]) -> dict[str, Any]:
    settled = [row for row in rows if row.get("side_won") is not None]
    wins = [row for row in settled if row.get("side_won") is True]
    losses = [row for row in settled if row.get("side_won") is False]
    net = sum(float(row.get("net_cents") or 0.0) for row in settled)
    return {
        "entries": len(rows),
        "settled": len(settled),
        "wins": len(wins),
        "losses": len(losses),
        "net_cents": net,
        "avg_net_cents": net / len(settled) if settled else None,
    }


def build_report() -> dict[str, Any]:
    payload = json.loads(INPUT_JSON.read_text(encoding="utf-8"))
    best = payload.get("best") or {}
    rows = best.get("candidate_rows") or []
    by_tag: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        for tag in row_tags(row):
            by_tag[tag].append(row)
    tag_rows = []
    for tag, tagged_rows in by_tag.items():
        summary = summarize(tagged_rows)
        if summary["settled"] < 2:
            continue
        tag_rows.append({"tag": tag, **summary})
    tag_rows.sort(key=lambda row: (float(row["net_cents"]), -int(row["settled"])))
    return {
        "diagnostic": "weak_reversal_residual_attribution",
        "best_policy": best.get("policy"),
        "candidate_summary": best.get("candidate_summary"),
        "worst_tags": tag_rows[:20],
        "loss_rows": best.get("loss_rows") or [],
        "interpretation": interpretation(best, tag_rows),
    }


def interpretation(best: dict[str, Any], tag_rows: list[dict[str, Any]]) -> list[str]:
    candidate = best.get("candidate_summary") or {}
    notes = [
        f"Best weak-reversal candidate remains negative: {candidate.get('net_cents')}c on {candidate.get('settled')} settled rows.",
    ]
    worst = tag_rows[0] if tag_rows else {}
    if worst:
        notes.append(
            f"Worst residual tag is {worst.get('tag')} with {worst.get('settled')} settled rows and {worst.get('net_cents')}c."
        )
    notes.append("This is attribution only; do not convert a tag into a rule without frozen forward evidence.")
    return notes


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
        "# v28 Weak-Reversal Residual Attribution",
        "",
        "Research-only; no live bot changes and no orders.",
        "",
        f"- Best policy: `{report.get('best_policy')}`",
        "",
        "## Interpretation",
        "",
    ]
    for note in report.get("interpretation") or []:
        lines.append(f"- {note}")
    lines.extend(
        [
            "",
            "## Worst Tags",
            "",
            "| tag | settled | W/L | net c | avg c |",
            "|---|---:|---:|---:|---:|",
        ]
    )
    for row in report.get("worst_tags") or []:
        lines.append(
            f"| {row.get('tag')} | {row.get('settled')} | {row.get('wins')}/{row.get('losses')} | "
            f"{fmt(row.get('net_cents'))} | {fmt(row.get('avg_net_cents'))} |"
        )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    report = build_report()
    write_md(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
