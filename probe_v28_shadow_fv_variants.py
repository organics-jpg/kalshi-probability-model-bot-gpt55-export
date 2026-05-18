"""Forward shadow bakeoff for v28 FV probability variants.

These variants are predeclared physics arguments, not fitted parameters:
- raw v28: current model probability.
- book ask prior: executable ask as a crowd/noise prior.
- fixed shrink: conservative blend toward the book prior.
- recross shrink: shrink more when price geometry says recross risk is high.
- edge confidence: shrink less only when v28 has meaningful edge over book.
- large disagreement anchor: trust book more when v28 and executable book
  strongly disagree, because that often means live market state is moving faster
  than the model geometry.

The script only scores settled forward observations. It does not alter the bot.
"""
from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any, Callable

from probe_v28_book_disagreement_calibration import build_rows as build_observations


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
OUT_CSV = OUT_DIR / "v28_shadow_fv_variants_latest.csv"
OUT_JSON = OUT_DIR / "v28_shadow_fv_variants_latest.json"
OUT_MD = OUT_DIR / "v28_shadow_fv_variants_latest.md"


def clamp01(value: float) -> float:
    return max(0.000001, min(0.999999, value))


def as_float(value: Any) -> float | None:
    if value is None or value == "":
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def variant_raw(row: dict[str, Any]) -> float:
    return clamp01(float(row["p_side"]))


def variant_book(row: dict[str, Any]) -> float:
    return clamp01(float(row["ask_prob"]))


def blend(row: dict[str, Any], alpha_v28: float) -> float:
    p_v28 = float(row["p_side"])
    p_book = float(row["ask_prob"])
    return clamp01(alpha_v28 * p_v28 + (1.0 - alpha_v28) * p_book)


def variant_fixed_shrink_75(row: dict[str, Any]) -> float:
    return blend(row, 0.75)


def variant_fixed_shrink_50(row: dict[str, Any]) -> float:
    return blend(row, 0.50)


def variant_recross_shrink(row: dict[str, Any]) -> float:
    hazard = as_float(row.get("recross_hazard_score"))
    if hazard is None:
        alpha = 0.70
    elif hazard >= 0.35:
        alpha = 0.45
    elif hazard >= 0.25:
        alpha = 0.60
    else:
        alpha = 0.80
    return blend(row, alpha)


def variant_edge_confidence(row: dict[str, Any]) -> float:
    edge = as_float(row.get("edge_cents"))
    disagreement = abs(float(row["v28_minus_ask_prob"]))
    if edge is not None and edge >= 2.0 and 0.03 <= disagreement <= 0.10:
        alpha = 0.90
    elif edge is not None and edge >= 0.0:
        alpha = 0.70
    else:
        alpha = 0.45
    return blend(row, alpha)


def variant_book_when_v28_coinflip(row: dict[str, Any]) -> float:
    p_v28 = float(row["p_side"])
    p_book = float(row["ask_prob"])
    if abs(p_v28 - 0.50) <= 0.08 and abs(p_book - 0.50) >= 0.05:
        return clamp01(p_book)
    return clamp01(p_v28)


def variant_book_when_v28_coinflip_else_edge(row: dict[str, Any]) -> float:
    p_v28 = float(row["p_side"])
    p_book = float(row["ask_prob"])
    edge = as_float(row.get("edge_cents"))
    if abs(p_v28 - 0.50) <= 0.08 and abs(p_book - 0.50) >= 0.05:
        return clamp01(p_book)
    if edge is not None and edge < 0.0 and abs(p_v28 - p_book) <= 0.04:
        return blend(row, 0.50)
    return clamp01(p_v28)


def variant_large_disagreement_book_anchor(row: dict[str, Any]) -> float:
    delta = float(row["v28_minus_ask_prob"])
    if abs(delta) >= 0.15:
        return blend(row, 0.35)
    if abs(delta) >= 0.08:
        return blend(row, 0.55)
    return clamp01(float(row["p_side"]))


def variant_v28_premium_book_anchor(row: dict[str, Any]) -> float:
    delta = float(row["v28_minus_ask_prob"])
    if delta >= 0.15:
        return blend(row, 0.30)
    if delta >= 0.08:
        return blend(row, 0.50)
    return clamp01(float(row["p_side"]))


VARIANTS: dict[str, Callable[[dict[str, Any]], float]] = {
    "v28_raw": variant_raw,
    "book_ask_prior": variant_book,
    "fixed_shrink_75_v28_25_book": variant_fixed_shrink_75,
    "fixed_shrink_50_v28_50_book": variant_fixed_shrink_50,
    "recross_shrink": variant_recross_shrink,
    "edge_confidence_shrink": variant_edge_confidence,
    "book_when_v28_coinflip": variant_book_when_v28_coinflip,
    "book_when_v28_coinflip_else_edge": variant_book_when_v28_coinflip_else_edge,
    "large_disagreement_book_anchor": variant_large_disagreement_book_anchor,
    "v28_premium_book_anchor": variant_v28_premium_book_anchor,
}


def score_variant(row: dict[str, Any], name: str, fn: Callable[[dict[str, Any]], float]) -> dict[str, Any]:
    p = fn(row)
    outcome = float(row["outcome"])
    brier = (p - outcome) ** 2
    return {
        "variant": name,
        "source": row.get("source"),
        "market": row.get("market"),
        "side": row.get("side"),
        "reason": row.get("reason"),
        "p": p,
        "outcome": outcome,
        "brier": brier,
        "raw_v28_p": row.get("p_side"),
        "book_p": row.get("ask_prob"),
        "v28_minus_book_p": row.get("v28_minus_ask_prob"),
        "edge_cents": row.get("edge_cents"),
        "recross_hazard_score": row.get("recross_hazard_score"),
        "gross_cents": row.get("gross_cents"),
    }


def build_rows() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for obs in build_observations():
        if obs.get("outcome") is None or obs.get("p_side") is None or obs.get("ask_prob") is None:
            continue
        for name, fn in VARIANTS.items():
            rows.append(score_variant(obs, name, fn))
    return rows


def summarize_group(rows: list[dict[str, Any]]) -> dict[str, Any]:
    if not rows:
        return {
            "count": 0,
            "avg_p": None,
            "win_rate": None,
            "avg_brier": None,
            "gross_cents": 0.0,
        }
    avg_p = sum(float(row["p"]) for row in rows) / len(rows)
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
    by_variant = {
        variant: summarize_group([row for row in rows if row.get("variant") == variant])
        for variant in VARIANTS
    }
    raw_brier = by_variant.get("v28_raw", {}).get("avg_brier")
    book_brier = by_variant.get("book_ask_prior", {}).get("avg_brier")
    ranked: list[dict[str, Any]] = []
    for variant, bucket in by_variant.items():
        avg_brier = bucket.get("avg_brier")
        ranked.append(
            {
                "variant": variant,
                **bucket,
                "brier_minus_v28_raw": None if avg_brier is None or raw_brier is None else float(avg_brier) - float(raw_brier),
                "brier_minus_book_prior": None if avg_brier is None or book_brier is None else float(avg_brier) - float(book_brier),
            }
        )
    ranked.sort(key=lambda item: (float("inf") if item["avg_brier"] is None else float(item["avg_brier"]), item["variant"]))
    return {
        "rows": len(rows),
        "observation_count": len(rows) // max(1, len(VARIANTS)),
        "by_variant": by_variant,
        "ranked": ranked,
    }


def collapse_rows(rows: list[dict[str, Any]], mode: str) -> list[dict[str, Any]]:
    picked: dict[tuple[str, str, str, str], dict[str, Any]] = {}
    sorted_rows = sorted(rows, key=lambda row: str(row.get("market") or ""))
    for row in sorted_rows:
        key = (
            str(row.get("variant") or ""),
            str(row.get("market") or ""),
            str(row.get("side") or ""),
            str(row.get("source") or ""),
        )
        if mode == "first":
            picked.setdefault(key, row)
        elif mode == "last":
            picked[key] = row
        else:
            raise ValueError(f"unknown collapse mode: {mode}")
    return list(picked.values())


def summarize_views(rows: list[dict[str, Any]]) -> dict[str, Any]:
    sources = sorted({str(row.get("source") or "unknown") for row in rows})
    views: dict[str, Any] = {
        "all_observations": summarize(rows),
        "first_per_market_side_source": summarize(collapse_rows(rows, "first")),
        "last_per_market_side_source": summarize(collapse_rows(rows, "last")),
    }
    for source in sources:
        views[f"source_{source}"] = summarize([row for row in rows if str(row.get("source") or "unknown") == source])
    return views


def write_csv(rows: list[dict[str, Any]]) -> None:
    if not rows:
        OUT_CSV.write_text("", encoding="utf-8")
        return
    keys = list(rows[0].keys())
    with OUT_CSV.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=keys)
        writer.writeheader()
        writer.writerows(rows)


def write_md(summary: dict[str, Any]) -> None:
    lines = [
        "# v28 Shadow FV Variants",
        "",
        "- Scope: settled forward observations only.",
        "- Promotion rule: no variant is useful without a physical reason plus fresh sample size; this report is evidence plumbing, not a live rule.",
        "",
        f"- Observations: `{summary['observation_count']}`",
        "",
        "## Ranked By Brier",
        "",
        "| rank | variant | count | avg p | win rate | error | avg brier | vs raw | vs book | gross c |",
        "|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for idx, row in enumerate(summary["ranked"], start=1):
        lines.append(
            f"| {idx} | {row['variant']} | {row['count']} | {row['avg_p']} | {row['win_rate']} | "
            f"{row.get('calibration_error')} | {row['avg_brier']} | {row['brier_minus_v28_raw']} | "
            f"{row['brier_minus_book_prior']} | {row['gross_cents']} |"
        )
    lines.extend([
        "",
        "## Robustness Views",
        "",
        "| view | best variant | obs | best brier | raw brier | book brier | best vs raw |",
        "|---|---|---:|---:|---:|---:|---:|",
    ])
    for view_name, view_summary in summary.get("views", {}).items():
        ranked = view_summary.get("ranked") or []
        if not ranked:
            continue
        best = ranked[0]
        raw = view_summary.get("by_variant", {}).get("v28_raw", {})
        book = view_summary.get("by_variant", {}).get("book_ask_prior", {})
        lines.append(
            f"| {view_name} | {best['variant']} | {view_summary['observation_count']} | "
            f"{best['avg_brier']} | {raw.get('avg_brier')} | {book.get('avg_brier')} | "
            f"{best.get('brier_minus_v28_raw')} |"
        )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    rows = build_rows()
    summary = summarize(rows)
    summary["views"] = summarize_views(rows)
    OUT_JSON.write_text(json.dumps({"summary": summary, "rows": rows}, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_csv(rows)
    write_md(summary)
    print(str(OUT_MD))


if __name__ == "__main__":
    main()
