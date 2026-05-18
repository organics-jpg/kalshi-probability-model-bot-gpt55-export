"""Book-disagreement calibration for v28 forward observations.

Kalshi touch prices are a noisy crowd prior. This report measures when v28's
probability diverges from executable ask probability and whether that
divergence is calibrated on fresh settled observations.
"""
from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

from probe_v28_forward_calibration import entry_observations, reject_observations, summarize_group


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
OUT_CSV = OUT_DIR / "v28_book_disagreement_calibration_latest.csv"
OUT_JSON = OUT_DIR / "v28_book_disagreement_calibration_latest.json"
OUT_MD = OUT_DIR / "v28_book_disagreement_calibration_latest.md"


def as_float(value: Any) -> float | None:
    if value is None or value == "":
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def disagreement_label(delta: float | None) -> str:
    if delta is None:
        return "missing"
    if delta < -0.05:
        return "v28_below_book"
    if delta < 0.00:
        return "slightly_below_book"
    if delta < 0.03:
        return "near_book"
    if delta < 0.08:
        return "v28_plus_03_08"
    if delta < 0.15:
        return "v28_plus_08_15"
    return "v28_plus_15"


def build_rows() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for row in entry_observations() + reject_observations():
        ask = as_float(row.get("ask_cents"))
        p_side = as_float(row.get("p_side"))
        if ask is None or p_side is None:
            continue
        ask_prob = ask / 100.0
        delta = p_side - ask_prob
        outcome = as_float(row.get("outcome"))
        if outcome is None:
            continue
        book_brier = (ask_prob - outcome) ** 2
        v28_brier = (p_side - outcome) ** 2
        gross = as_float(row.get("gross_cents")) or 0.0
        rows.append(
            {
                **row,
                "ask_prob": ask_prob,
                "v28_minus_ask_prob": delta,
                "disagreement_bucket": disagreement_label(delta),
                "book_brier": book_brier,
                "v28_brier": v28_brier,
                "v28_brier_minus_book_brier": v28_brier - book_brier,
                "gross_cents": gross,
            }
        )
    return rows


def summarize_book_group(rows: list[dict[str, Any]]) -> dict[str, Any]:
    base = summarize_group(rows)
    if not rows:
        base.update(
            {
                "avg_ask_prob": None,
                "avg_v28_minus_ask_prob": None,
                "avg_book_brier": None,
                "avg_v28_brier_minus_book_brier": None,
            }
        )
        return base
    base.update(
        {
            "avg_ask_prob": sum(float(row["ask_prob"]) for row in rows) / len(rows),
            "avg_v28_minus_ask_prob": sum(float(row["v28_minus_ask_prob"]) for row in rows) / len(rows),
            "avg_book_brier": sum(float(row["book_brier"]) for row in rows) / len(rows),
            "avg_v28_brier_minus_book_brier": sum(float(row["v28_brier_minus_book_brier"]) for row in rows) / len(rows),
        }
    )
    return base


def summarize(rows: list[dict[str, Any]]) -> dict[str, Any]:
    buckets = [
        "v28_below_book",
        "slightly_below_book",
        "near_book",
        "v28_plus_03_08",
        "v28_plus_08_15",
        "v28_plus_15",
    ]
    return {
        "overall": summarize_book_group(rows),
        "by_disagreement": {
            bucket: summarize_book_group([row for row in rows if row.get("disagreement_bucket") == bucket])
            for bucket in buckets
        },
        "by_source": {
            source: summarize_book_group([row for row in rows if row.get("source") == source])
            for source in sorted({str(row.get("source") or "") for row in rows})
        },
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
        "# v28 Book Disagreement Calibration",
        "",
        "- Physics prior: executable book price is a noisy market-implied probability.",
        "- Question: when v28 disagrees with that prior, is v28 better calibrated after settlement?",
        "",
        "## Overall",
        "",
        f"- Observations: `{overall['count']}`",
        f"- Avg v28 p: `{overall['avg_p']}`",
        f"- Avg ask probability: `{overall['avg_ask_prob']}`",
        f"- Avg v28 minus ask probability: `{overall['avg_v28_minus_ask_prob']}`",
        f"- Win rate: `{overall['win_rate']}`",
        f"- Avg v28 Brier: `{overall['avg_brier']}`",
        f"- Avg book Brier: `{overall['avg_book_brier']}`",
        f"- Avg v28 minus book Brier: `{overall['avg_v28_brier_minus_book_brier']}`",
        "",
        "## By Disagreement Bucket",
        "",
        "| bucket | count | avg v28 p | avg ask p | win rate | v28-book p | v28 brier | book brier | v28-book brier | gross c |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for bucket, item in summary["by_disagreement"].items():
        lines.append(
            f"| {bucket} | {item['count']} | {item['avg_p']} | {item['avg_ask_prob']} | {item['win_rate']} | "
            f"{item['avg_v28_minus_ask_prob']} | {item['avg_brier']} | {item['avg_book_brier']} | "
            f"{item['avg_v28_brier_minus_book_brier']} | {item['gross_cents']} |"
        )
    lines.extend(["", "## Observations", ""])
    if rows:
        lines.append("| source | market | side | bucket | p_side | ask p | outcome | v28-book brier | gross c |")
        lines.append("|---|---|---|---|---:|---:|---:|---:|---:|")
        for row in rows[-20:]:
            lines.append(
                "| {source} | {market} | {side} | {disagreement_bucket} | {p_side} | {ask_prob} | {outcome} | {v28_brier_minus_book_brier} | {gross_cents} |".format(
                    **row
                )
            )
    else:
        lines.append("No settled book-disagreement observations yet.")
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    rows = build_rows()
    rows.sort(key=lambda row: (str(row.get("market") or ""), str(row.get("source") or ""), str(row.get("side") or "")))
    summary = summarize(rows)
    OUT_JSON.write_text(json.dumps({"summary": summary, "rows": rows}, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_csv(rows)
    write_md(rows, summary)
    print(str(OUT_MD))


if __name__ == "__main__":
    main()
