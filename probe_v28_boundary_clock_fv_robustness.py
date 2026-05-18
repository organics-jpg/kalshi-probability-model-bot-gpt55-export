"""Robustness audit for the boundary-clock FV overlay diagnostic.

Research-only; no live bot changes or orders.

The boundary-clock FV overlay improves calibration by collapsing hazard rows to
50. This audit checks whether that improvement survives leave-one adjusted-row
stress, and whether the adjusted rows have a coherent physical error profile.
"""
from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any

from probe_v28_target_coverage_fv_overlay_validator import clamp_prob, logloss


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
SOURCE_JSON = OUT_DIR / "v28_boundary_clock_fv_overlay_latest.json"
OUT_JSON = OUT_DIR / "v28_boundary_clock_fv_robustness_latest.json"
OUT_MD = OUT_DIR / "v28_boundary_clock_fv_robustness_latest.md"


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
        out = float(value)
    except (TypeError, ValueError):
        return None
    return out if math.isfinite(out) else None


def contribution(row: dict[str, Any]) -> dict[str, Any]:
    raw = clamp_prob(float(row.get("raw_p")))
    adjusted = clamp_prob(float(row.get("adjusted_p")))
    outcome = 1.0 if row.get("side_won") is True else 0.0
    raw_brier = (raw - outcome) ** 2
    adj_brier = (adjusted - outcome) ** 2
    raw_loss = logloss(raw, outcome)
    adj_loss = logloss(adjusted, outcome)
    return {
        **row,
        "outcome": outcome,
        "brier_delta": adj_brier - raw_brier,
        "logloss_delta": adj_loss - raw_loss,
        "helped_brier": adj_brier < raw_brier,
        "helped_logloss": adj_loss < raw_loss,
    }


def avg(values: list[float]) -> float | None:
    return sum(values) / len(values) if values else None


def rollup(rows: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "rows": len(rows),
        "wins": sum(1 for row in rows if row.get("side_won") is True),
        "losses": sum(1 for row in rows if row.get("side_won") is False),
        "net_cents": sum(float(as_float(row.get("net_cents")) or 0.0) for row in rows),
        "brier_delta_sum": sum(float(row.get("brier_delta") or 0.0) for row in rows),
        "logloss_delta_sum": sum(float(row.get("logloss_delta") or 0.0) for row in rows),
        "brier_helped_rows": sum(1 for row in rows if row.get("helped_brier") is True),
        "logloss_helped_rows": sum(1 for row in rows if row.get("helped_logloss") is True),
        "avg_raw_p": avg([float(row["raw_p"]) for row in rows if row.get("raw_p") is not None]),
        "avg_abs_delta_p": avg([abs(float(row["delta_p"])) for row in rows if row.get("delta_p") is not None]),
    }


def build_report() -> dict[str, Any]:
    source = load_json(SOURCE_JSON)
    best = next(
        (row for row in (source.get("ranked") or []) if row.get("overlay") == source.get("best_overlay")),
        (source.get("ranked") or [{}])[0],
    )
    settled = int(best.get("settled") or 0)
    rows = [contribution(row) for row in source.get("hazard_rows") or [] if row.get("side_won") is not None]
    brier_sum = sum(float(row["brier_delta"]) for row in rows)
    logloss_sum = sum(float(row["logloss_delta"]) for row in rows)
    leave_one = []
    for row in rows:
        denom = max(1, settled - 1)
        leave_one.append({
            "market": row.get("market"),
            "side_won": row.get("side_won"),
            "net_cents": row.get("net_cents"),
            "brier_contribution": row.get("brier_delta"),
            "logloss_contribution": row.get("logloss_delta"),
            "brier_mean_without_row": (brier_sum - float(row["brier_delta"])) / denom,
            "logloss_mean_without_row": (logloss_sum - float(row["logloss_delta"])) / denom,
        })
    leave_one.sort(key=lambda row: float(row.get("brier_mean_without_row") or 999.0), reverse=True)
    wins = [row for row in rows if row.get("side_won") is True]
    losses = [row for row in rows if row.get("side_won") is False]
    worst_brier = leave_one[0] if leave_one else {}
    worst_logloss = sorted(
        leave_one,
        key=lambda row: float(row.get("logloss_mean_without_row") or 999.0),
        reverse=True,
    )[0] if leave_one else {}
    return {
        "diagnostic": "boundary_clock_fv_robustness",
        "source": str(SOURCE_JSON),
        "overlay": source.get("best_overlay"),
        "settled": settled,
        "adjusted_rows": len(rows),
        "base_brier_delta": best.get("brier_delta_vs_raw"),
        "base_logloss_delta": best.get("logloss_delta_vs_raw"),
        "adjusted_rollup": rollup(rows),
        "adjusted_win_rollup": rollup(wins),
        "adjusted_loss_rollup": rollup(losses),
        "leave_one": leave_one,
        "worst_leave_one_brier": worst_brier,
        "worst_leave_one_logloss": worst_logloss,
        "passes_basic_robustness": (
            bool(rows)
            and as_float(best.get("brier_delta_vs_raw")) is not None
            and float(best.get("brier_delta_vs_raw")) < 0.0
            and as_float(best.get("logloss_delta_vs_raw")) is not None
            and float(best.get("logloss_delta_vs_raw")) < 0.0
            and float(worst_brier.get("brier_mean_without_row") or 999.0) < 0.0
            and float(worst_logloss.get("logloss_mean_without_row") or 999.0) < 0.0
        ),
        "rows": rows,
        "interpretation": interpretation(best, rows, worst_brier, worst_logloss),
    }


def interpretation(
    best: dict[str, Any],
    rows: list[dict[str, Any]],
    worst_brier: dict[str, Any],
    worst_logloss: dict[str, Any],
) -> list[str]:
    return [
        f"Base Brier/logloss deltas are {best.get('brier_delta_vs_raw')}/{best.get('logloss_delta_vs_raw')} over {best.get('settled')} settled rows.",
        f"Adjusted hazard rows: {len(rows)}.",
        f"Worst leave-one Brier mean remains {worst_brier.get('brier_mean_without_row')}.",
        f"Worst leave-one logloss mean remains {worst_logloss.get('logloss_mean_without_row')}.",
        "This is still diagnostic; frozen future validation controls promotion.",
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
    roll = report.get("adjusted_rollup") or {}
    lines = [
        "# v28 Boundary-Clock FV Robustness",
        "",
        "Diagnostic-only: no live bot changes and no orders.",
        "",
        f"- Overlay: `{report.get('overlay')}`",
        f"- Passes basic robustness: `{report.get('passes_basic_robustness')}`",
        f"- Settled/adjusted rows: `{report.get('settled')}/{report.get('adjusted_rows')}`",
        f"- Base Brier/logloss delta: `{fmt(report.get('base_brier_delta'))}/{fmt(report.get('base_logloss_delta'))}`",
        f"- Adjusted W/L/net: `{roll.get('wins')}/{roll.get('losses')}/{fmt(roll.get('net_cents'))}c`",
        "",
        "## Interpretation",
        "",
    ]
    for note in report.get("interpretation") or []:
        lines.append(f"- {note}")
    lines.extend([
        "",
        "## Leave-One Stress",
        "",
        "| market | won | net c | brier contrib | logloss contrib | brier without | logloss without |",
        "|---|---|---:|---:|---:|---:|---:|",
    ])
    for row in report.get("leave_one") or []:
        lines.append(
            f"| {row.get('market')} | {row.get('side_won')} | {fmt(row.get('net_cents'))} | "
            f"{fmt(row.get('brier_contribution'))} | {fmt(row.get('logloss_contribution'))} | "
            f"{fmt(row.get('brier_mean_without_row'))} | {fmt(row.get('logloss_mean_without_row'))} |"
        )
    lines.extend([
        "",
        "## Adjusted Rows",
        "",
        "| market | side | won | raw p | adj p | d p | brier d | logloss d | stc | abs d | recross |",
        "|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|",
    ])
    for row in report.get("rows") or []:
        lines.append(
            f"| {row.get('market')} | {row.get('side')} | {row.get('side_won')} | "
            f"{fmt(row.get('raw_p'))} | {fmt(row.get('adjusted_p'))} | {fmt(row.get('delta_p'))} | "
            f"{fmt(row.get('brier_delta'))} | {fmt(row.get('logloss_delta'))} | "
            f"{fmt(row.get('seconds_to_close'))} | {fmt(row.get('abs_d_sigma'))} | {fmt(row.get('recross_hazard_score'))} |"
        )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    report = build_report()
    write_md(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
