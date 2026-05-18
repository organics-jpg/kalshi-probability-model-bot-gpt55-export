"""Residual attribution after boundary-clock FV correction.

Research-only; no live bot changes or orders.

The boundary-clock overlay explains a large chunk of target-surface
miscalibration. This probe isolates what remains wrong after that correction so
future iterations do not keep rediscovering the same hazard bucket.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from probe_v28_boundary_clock_fv_overlay import raw_prob, shrink_prob
from probe_v28_boundary_clock_hazard_repair import clock_composite
from probe_v28_target_coverage_pnl_attribution import forward_rows, net_cents, tags
from probe_v28_target_coverage_fv_overlay_validator import logloss


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
OUT_JSON = OUT_DIR / "v28_boundary_clock_residual_attribution_latest.json"
OUT_MD = OUT_DIR / "v28_boundary_clock_residual_attribution_latest.md"


def brier(p: float, outcome: float) -> float:
    return (p - outcome) ** 2


def adjusted_prob(row: dict[str, Any]) -> float:
    return shrink_prob(row, 0.0)


def row_view(row: dict[str, Any]) -> dict[str, Any]:
    raw = raw_prob(row)
    adj = adjusted_prob(row)
    outcome = 1.0 if row.get("side_won") is True else 0.0
    return {
        "market": row.get("market"),
        "ts_wall": row.get("ts_wall"),
        "source": row.get("source"),
        "side": row.get("side"),
        "side_won": row.get("side_won"),
        "net_cents": net_cents(row),
        "raw_p": raw,
        "adjusted_p": adj,
        "delta_p": adj - raw,
        "brier_delta": brier(adj, outcome) - brier(raw, outcome),
        "logloss_delta": logloss(adj, outcome) - logloss(raw, outcome),
        "ask_prob": row.get("ask_prob"),
        "raw_edge_prob": row.get("raw_edge_prob"),
        "seconds_to_close": row.get("seconds_to_close"),
        "abs_d_sigma": row.get("abs_d_sigma"),
        "recross_hazard_score": row.get("recross_hazard_score"),
        "clock_composite": clock_composite(row),
        "tags": tags(row),
    }


def summarize(rows: list[dict[str, Any]]) -> dict[str, Any]:
    settled = [row for row in rows if row.get("side_won") is not None]
    return {
        "rows": len(rows),
        "settled": len(settled),
        "wins": sum(1 for row in settled if row.get("side_won") is True),
        "losses": sum(1 for row in settled if row.get("side_won") is False),
        "net_cents": sum(float(net_cents(row) or 0.0) for row in settled),
    }


def tag_rollups(rows: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    groups: dict[str, list[dict[str, Any]]] = {}
    for row in rows:
        for tag in tags(row):
            groups.setdefault(tag, []).append(row)
    out = {}
    for tag, group in groups.items():
        out[tag] = summarize(group)
    return dict(sorted(out.items(), key=lambda item: (float(item[1]["net_cents"]), -int(item[1]["settled"]))))


def build_report() -> dict[str, Any]:
    rows, denominator = forward_rows()
    settled = [row for row in rows if row.get("side_won") is not None]
    clock_rows = [row for row in settled if clock_composite(row)]
    non_clock = [row for row in settled if not clock_composite(row)]
    direction_wrong = [row for row in settled if row.get("side_won") is False]
    clock_wrong = [row for row in direction_wrong if clock_composite(row)]
    residual_wrong = [row for row in direction_wrong if not clock_composite(row)]
    return {
        "diagnostic": "boundary_clock_residual_attribution",
        "forward_denominator": denominator,
        "summary": summarize(rows),
        "clock_summary": summarize(clock_rows),
        "non_clock_summary": summarize(non_clock),
        "direction_wrong_summary": summarize(direction_wrong),
        "clock_wrong_summary": summarize(clock_wrong),
        "residual_wrong_summary": summarize(residual_wrong),
        "residual_wrong_rows": [row_view(row) for row in sorted(residual_wrong, key=lambda row: float(net_cents(row) or 0.0))],
        "residual_wrong_tag_rollups": tag_rollups(residual_wrong),
        "interpretation": interpretation(rows, clock_wrong, residual_wrong),
    }


def interpretation(rows: list[dict[str, Any]], clock_wrong: list[dict[str, Any]], residual_wrong: list[dict[str, Any]]) -> list[str]:
    settled = [row for row in rows if row.get("side_won") is not None]
    return [
        f"Target surface has {len(rows)} entries and {len(settled)} settled rows.",
        f"Boundary-clock hazard explains {len(clock_wrong)} direction-wrong rows.",
        f"Residual non-clock direction errors: {len(residual_wrong)} rows.",
        "Next FV work should focus only on residual non-clock errors if frozen boundary-clock validation holds up.",
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
        "# v28 Boundary-Clock Residual Attribution",
        "",
        "Diagnostic-only: no live bot changes and no orders.",
        "",
        f"- Forward denominator: `{report.get('forward_denominator')}`",
        "",
        "## Interpretation",
        "",
    ]
    for note in report.get("interpretation") or []:
        lines.append(f"- {note}")
    lines.extend([
        "",
        "## Summaries",
        "",
        "| slice | rows | settled | W/L | net c |",
        "|---|---:|---:|---:|---:|",
    ])
    for label, key in [
        ("target", "summary"),
        ("clock", "clock_summary"),
        ("non_clock", "non_clock_summary"),
        ("direction_wrong", "direction_wrong_summary"),
        ("clock_wrong", "clock_wrong_summary"),
        ("residual_wrong", "residual_wrong_summary"),
    ]:
        row = report.get(key) or {}
        lines.append(
            f"| {label} | {row.get('rows')} | {row.get('settled')} | {row.get('wins')}/{row.get('losses')} | {fmt(row.get('net_cents'))} |"
        )
    lines.extend([
        "",
        "## Residual Wrong Rows",
        "",
        "| market | source | side | net c | raw p | adj p | ask | edge | stc | abs d | recross | tags |",
        "|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---|",
    ])
    for row in report.get("residual_wrong_rows") or []:
        lines.append(
            f"| {row.get('market')} | {row.get('source')} | {row.get('side')} | {fmt(row.get('net_cents'))} | "
            f"{fmt(row.get('raw_p'))} | {fmt(row.get('adjusted_p'))} | {fmt(row.get('ask_prob'))} | "
            f"{fmt(row.get('raw_edge_prob'))} | {fmt(row.get('seconds_to_close'))} | "
            f"{fmt(row.get('abs_d_sigma'))} | {fmt(row.get('recross_hazard_score'))} | {', '.join(row.get('tags') or [])} |"
        )
    lines.extend([
        "",
        "## Residual Wrong Tag Rollups",
        "",
        "| tag | rows | settled | W/L | net c |",
        "|---|---:|---:|---:|---:|",
    ])
    for tag, row in (report.get("residual_wrong_tag_rollups") or {}).items():
        lines.append(
            f"| {tag} | {row.get('rows')} | {row.get('settled')} | {row.get('wins')}/{row.get('losses')} | {fmt(row.get('net_cents'))} |"
        )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    report = build_report()
    write_md(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
