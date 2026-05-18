"""Forward calibration report for v28 FV observations.

Combines actual v28 entries with actionable rejected observations, then scores
probability calibration after settlement. This keeps model-quality evidence
separate from historical P&L row shopping.
"""
from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

from probe_v28_forward_physics_registry import build_rows as build_entry_rows
from probe_v28_rejected_opportunity_score import build_rows as build_reject_rows


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
OUT_CSV = OUT_DIR / "v28_forward_calibration_latest.csv"
OUT_JSON = OUT_DIR / "v28_forward_calibration_latest.json"
OUT_MD = OUT_DIR / "v28_forward_calibration_latest.md"


BUCKETS = [
    (0.00, 0.50, "00_50"),
    (0.50, 0.60, "50_60"),
    (0.60, 0.70, "60_70"),
    (0.70, 0.80, "70_80"),
    (0.80, 0.85, "80_85"),
    (0.85, 0.90, "85_90"),
    (0.90, 0.95, "90_95"),
    (0.95, 1.01, "95_100"),
]


def bucket_label(p: float | None) -> str:
    if p is None:
        return "missing"
    for low, high, label in BUCKETS:
        if low <= p < high:
            return label
    return "out_of_range"


def as_float(value: Any) -> float | None:
    if value is None or value == "":
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def entry_observations() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for row in build_entry_rows():
        p_side = as_float(row.get("p_side"))
        side_won = row.get("side_won")
        if p_side is None or side_won is None:
            continue
        rows.append(
            {
                "source": "entry",
                "market": row.get("market"),
                "side": row.get("side"),
                "reason": "approved_entry",
                "p_side": p_side,
                "outcome": 1.0 if side_won is True else 0.0,
                "brier": (p_side - (1.0 if side_won is True else 0.0)) ** 2,
                "bucket": bucket_label(p_side),
                "actionable": True,
                "edge_cents": row.get("edge_cents"),
                "ask_cents": row.get("ask_cents"),
                "seconds_to_close": row.get("seconds_to_close"),
                "sigma_t_dollars": row.get("sigma_t_dollars"),
                "recross_hazard_score": row.get("recross_hazard_score"),
                "h6_recross_hazard_high": row.get("h6_recross_hazard_high"),
                "gross_cents": row.get("actual_gross_cents"),
            }
        )
    return rows


def reject_observations() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for row in build_reject_rows():
        if row.get("actionable_shadow") is not True:
            continue
        p_side = as_float(row.get("p_side"))
        side_won = row.get("side_won")
        if p_side is None or side_won is None:
            continue
        rows.append(
            {
                "source": "rejected_actionable",
                "market": row.get("market"),
                "side": row.get("side"),
                "reason": row.get("reason"),
                "p_side": p_side,
                "outcome": 1.0 if side_won is True else 0.0,
                "brier": (p_side - (1.0 if side_won is True else 0.0)) ** 2,
                "bucket": bucket_label(p_side),
                "actionable": True,
                "edge_cents": row.get("edge_cents"),
                "ask_cents": row.get("ask_cents"),
                "seconds_to_close": row.get("seconds_to_close"),
                "sigma_t_dollars": row.get("sigma_t_dollars"),
                "recross_hazard_score": row.get("recross_hazard_score"),
                "h6_recross_hazard_high": row.get("h6_recross_hazard_high"),
                "gross_cents": row.get("hypothetical_hold_gross_cents"),
            }
        )
    return rows


def summarize_group(rows: list[dict[str, Any]]) -> dict[str, Any]:
    if not rows:
        return {
            "count": 0,
            "avg_p": None,
            "win_rate": None,
            "calibration_error": None,
            "avg_brier": None,
            "gross_cents": 0.0,
        }
    avg_p = sum(float(row["p_side"]) for row in rows) / len(rows)
    win_rate = sum(float(row["outcome"]) for row in rows) / len(rows)
    return {
        "count": len(rows),
        "avg_p": avg_p,
        "win_rate": win_rate,
        "calibration_error": win_rate - avg_p,
        "avg_brier": sum(float(row["brier"]) for row in rows) / len(rows),
        "gross_cents": sum(float(row["gross_cents"] or 0.0) for row in rows),
    }


def summarize(rows: list[dict[str, Any]]) -> dict[str, Any]:
    by_bucket = {
        label: summarize_group([row for row in rows if row.get("bucket") == label])
        for _, _, label in BUCKETS
    }
    by_source = {
        source: summarize_group([row for row in rows if row.get("source") == source])
        for source in sorted({str(row.get("source") or "") for row in rows})
    }
    by_reason = {
        reason: summarize_group([row for row in rows if row.get("reason") == reason])
        for reason in sorted({str(row.get("reason") or "") for row in rows})
    }
    by_flag = {
        "recross_hazard_high": summarize_group([row for row in rows if row.get("h6_recross_hazard_high") is True]),
        "recross_hazard_not_high": summarize_group([row for row in rows if row.get("h6_recross_hazard_high") is not True]),
    }
    return {
        "overall": summarize_group(rows),
        "by_bucket": by_bucket,
        "by_source": by_source,
        "by_reason": by_reason,
        "by_flag": by_flag,
    }


def write_csv(rows: list[dict[str, Any]]) -> None:
    if not rows:
        OUT_CSV.write_text("", encoding="utf-8")
        return
    keys = list(rows[0].keys())
    with OUT_CSV.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=keys)
        writer.writeheader()
        writer.writerows(rows)


def write_md(rows: list[dict[str, Any]], summary: dict[str, Any]) -> None:
    overall = summary["overall"]
    lines = [
        "# v28 Forward Calibration",
        "",
        "- Scope: settled v28 approved entries plus actionable settled rejects.",
        "- Purpose: judge FV probability calibration before using P&L as a model selector.",
        "",
        "## Overall",
        "",
        f"- Observations: `{overall['count']}`",
        f"- Avg p_side: `{overall['avg_p']}`",
        f"- Win rate: `{overall['win_rate']}`",
        f"- Calibration error win_rate_minus_avg_p: `{overall['calibration_error']}`",
        f"- Avg Brier: `{overall['avg_brier']}`",
        f"- Gross cents proxy: `{overall['gross_cents']}`",
        "",
        "## By Probability Bucket",
        "",
        "| bucket | count | avg p | win rate | error | brier | gross c |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for label, bucket in summary["by_bucket"].items():
        lines.append(
            f"| {label} | {bucket['count']} | {bucket['avg_p']} | {bucket['win_rate']} | "
            f"{bucket['calibration_error']} | {bucket['avg_brier']} | {bucket['gross_cents']} |"
        )
    lines.extend(["", "## By Source", "", "| source | count | avg p | win rate | error | brier | gross c |", "|---|---:|---:|---:|---:|---:|---:|"])
    for label, bucket in summary["by_source"].items():
        lines.append(
            f"| {label} | {bucket['count']} | {bucket['avg_p']} | {bucket['win_rate']} | "
            f"{bucket['calibration_error']} | {bucket['avg_brier']} | {bucket['gross_cents']} |"
        )
    lines.extend(["", "## Latest Observations", ""])
    if rows:
        lines.append("| source | market | side | reason | bucket | p_side | outcome | brier | gross c |")
        lines.append("|---|---|---|---|---|---:|---:|---:|---:|")
        for row in rows[-20:]:
            lines.append(
                "| {source} | {market} | {side} | {reason} | {bucket} | {p_side} | {outcome} | {brier} | {gross_cents} |".format(
                    **row
                )
            )
    else:
        lines.append("No settled calibration observations yet.")
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    rows = entry_observations() + reject_observations()
    rows.sort(key=lambda row: (str(row.get("market") or ""), str(row.get("source") or ""), str(row.get("side") or "")))
    summary = summarize(rows)
    OUT_JSON.write_text(json.dumps({"summary": summary, "rows": rows}, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_csv(rows)
    write_md(rows, summary)
    print(str(OUT_MD))


if __name__ == "__main__":
    main()
