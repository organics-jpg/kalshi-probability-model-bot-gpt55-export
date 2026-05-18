"""Information-decay diagnostic for v28 shadow telemetry.

This tests a simple version of "useful forgetting": for each actionable v28
observation, compare the current probability signal with exponentially retained
same-market evidence from prior observations. It is descriptive only and does
not change bot logic.
"""
from __future__ import annotations

import csv
import json
import math
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any

from probe_v28_shadow_entry_policy_bakeoff import observation_pool


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
OUT_CSV = OUT_DIR / "v28_information_decay_diagnostic_latest.csv"
OUT_JSON = OUT_DIR / "v28_information_decay_diagnostic_latest.json"
OUT_MD = OUT_DIR / "v28_information_decay_diagnostic_latest.md"

HALF_LIFE_SECONDS = [15, 45, 120, 300]


def as_float(value: Any) -> float | None:
    if value is None or value == "":
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def parse_ts(value: Any) -> datetime | None:
    if not value:
        return None
    text = str(value)
    if text.endswith("Z"):
        text = text[:-1] + "+00:00"
    try:
        return datetime.fromisoformat(text)
    except ValueError:
        return None


def outcome(row: dict[str, Any]) -> float | None:
    side_won = row.get("side_won")
    if side_won is True:
        return 1.0
    if side_won is False:
        return 0.0
    return None


def clamp_prob(value: float) -> float:
    return min(0.995, max(0.005, value))


def score_prob(prob: float | None, actual: float | None) -> float | None:
    if prob is None or actual is None:
        return None
    return (clamp_prob(prob) - actual) ** 2


def blend_prob(a: float | None, b: float | None, weight_a: float) -> float | None:
    if a is None:
        return b
    if b is None:
        return a
    return clamp_prob(weight_a * a + (1.0 - weight_a) * b)


def gross_from_prob_source(row: dict[str, Any]) -> float | None:
    gross = as_float(row.get("gross_cents"))
    return gross


def with_decay_features(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    ordered = []
    for row in rows:
        ts = parse_ts(row.get("ts_wall"))
        p_side = as_float(row.get("p_side"))
        ask_prob = as_float(row.get("ask_prob"))
        if ts is None or p_side is None or ask_prob is None:
            continue
        enriched = dict(row)
        enriched["_ts"] = ts
        ordered.append(enriched)
    ordered.sort(key=lambda row: (str(row.get("market") or ""), row["_ts"], str(row.get("side") or "")))

    states: dict[tuple[str, str, int], dict[str, Any]] = {}
    out: list[dict[str, Any]] = []
    for row in ordered:
        market = str(row.get("market") or "")
        side = str(row.get("side") or "")
        ts = row["_ts"]
        p_side = float(row["p_side"])
        ask_prob = float(row["ask_prob"])
        actual = outcome(row)
        row_out = {key: value for key, value in row.items() if key != "_ts"}
        row_out["outcome"] = actual
        row_out["current_p_brier"] = score_prob(p_side, actual)
        row_out["book_brier"] = score_prob(ask_prob, actual)
        row_out["gross_cents"] = gross_from_prob_source(row)

        for half_life in HALF_LIFE_SECONDS:
            state_key = (market, side, half_life)
            state = states.get(state_key)
            prefix = f"hl{half_life}"
            if state is None:
                row_out[f"{prefix}_prior_p"] = None
                row_out[f"{prefix}_prior_book"] = None
                row_out[f"{prefix}_prior_age_seconds"] = None
                row_out[f"{prefix}_p_surprise"] = None
                row_out[f"{prefix}_book_surprise"] = None
                row_out[f"{prefix}_prior_p_brier"] = None
                row_out[f"{prefix}_prior_book_brier"] = None
            else:
                dt = max(0.0, (ts - state["ts"]).total_seconds())
                alpha = 1.0 - math.exp(-math.log(2.0) * dt / float(half_life))
                prior_p = float(state["p"])
                prior_book = float(state["book"])
                row_out[f"{prefix}_prior_p"] = prior_p
                row_out[f"{prefix}_prior_book"] = prior_book
                row_out[f"{prefix}_prior_age_seconds"] = dt
                row_out[f"{prefix}_p_surprise"] = p_side - prior_p
                row_out[f"{prefix}_book_surprise"] = ask_prob - prior_book
                row_out[f"{prefix}_prior_p_brier"] = score_prob(prior_p, actual)
                row_out[f"{prefix}_prior_book_brier"] = score_prob(prior_book, actual)
                state["p"] = prior_p + alpha * (p_side - prior_p)
                state["book"] = prior_book + alpha * (ask_prob - prior_book)
                state["ts"] = ts
                continue
            states[state_key] = {"p": p_side, "book": ask_prob, "ts": ts}
        out.append(row_out)
    return out


def avg(values: list[float]) -> float | None:
    return sum(values) / len(values) if values else None


def summarize_rows(rows: list[dict[str, Any]]) -> dict[str, Any]:
    settled = [row for row in rows if row.get("outcome") is not None]
    resolved = [row for row in rows if row.get("gross_cents") is not None]
    summary: dict[str, Any] = {
        "rows": len(rows),
        "settled": len(settled),
        "resolved": len(resolved),
        "current_p_brier": avg([float(row["current_p_brier"]) for row in settled if row.get("current_p_brier") is not None]),
        "book_brier": avg([float(row["book_brier"]) for row in settled if row.get("book_brier") is not None]),
        "gross_cents": sum(float(row["gross_cents"]) for row in resolved),
        "by_half_life": {},
    }
    for half_life in HALF_LIFE_SECONDS:
        prefix = f"hl{half_life}"
        comparable = [
            row
            for row in settled
            if row.get(f"{prefix}_prior_p_brier") is not None and row.get("current_p_brier") is not None
        ]
        p_surprises = [abs(float(row[f"{prefix}_p_surprise"])) for row in comparable if row.get(f"{prefix}_p_surprise") is not None]
        retained_briers = [float(row[f"{prefix}_prior_p_brier"]) for row in comparable]
        current_briers = [float(row["current_p_brier"]) for row in comparable]
        book_retained_briers = [float(row[f"{prefix}_prior_book_brier"]) for row in comparable if row.get(f"{prefix}_prior_book_brier") is not None]
        book_current_briers = [float(row["book_brier"]) for row in comparable if row.get("book_brier") is not None]
        stale_worse = sum(
            1
            for row in comparable
            if row.get(f"{prefix}_prior_p_brier") is not None
            and row.get("current_p_brier") is not None
            and float(row[f"{prefix}_prior_p_brier"]) > float(row["current_p_brier"])
        )
        summary["by_half_life"][str(half_life)] = {
            "comparable": len(comparable),
            "current_p_brier": avg(current_briers),
            "retained_p_brier": avg(retained_briers),
            "retained_minus_current_p_brier": None if not retained_briers or not current_briers else avg(retained_briers) - avg(current_briers),
            "current_book_brier": avg(book_current_briers),
            "retained_book_brier": avg(book_retained_briers),
            "retained_minus_current_book_brier": (
                None if not book_retained_briers or not book_current_briers else avg(book_retained_briers) - avg(book_current_briers)
            ),
            "avg_abs_p_surprise": avg(p_surprises),
            "stale_worse_count": stale_worse,
        }
    return summary


def summarize_by_source(rows: list[dict[str, Any]]) -> dict[str, Any]:
    buckets: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        buckets[str(row.get("source") or "unknown")].append(row)
    return {name: summarize_rows(bucket) for name, bucket in sorted(buckets.items())}


def collapse_rows(rows: list[dict[str, Any]], mode: str) -> list[dict[str, Any]]:
    picked: dict[tuple[str, str, str], dict[str, Any]] = {}
    sorted_rows = sorted(rows, key=lambda row: str(row.get("ts_wall") or ""))
    for row in sorted_rows:
        key = (str(row.get("market") or ""), str(row.get("side") or ""), str(row.get("source") or ""))
        if mode == "first":
            picked.setdefault(key, row)
        elif mode == "last":
            picked[key] = row
        else:
            raise ValueError(f"unknown collapse mode: {mode}")
    return list(picked.values())


def summarize_views(rows: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "all_observations": summarize_rows(rows),
        "first_per_market_side_source": summarize_rows(collapse_rows(rows, "first")),
        "last_per_market_side_source": summarize_rows(collapse_rows(rows, "last")),
    }


def state_variant_prob(row: dict[str, Any], name: str) -> float | None:
    current = as_float(row.get("p_side"))
    book = as_float(row.get("ask_prob"))
    prior_15 = as_float(row.get("hl15_prior_p"))
    prior_120 = as_float(row.get("hl120_prior_p"))
    surprise_15 = as_float(row.get("hl15_p_surprise"))
    seconds_to_close = as_float(row.get("seconds_to_close"))
    if name == "current_v28":
        return current
    if name == "book_prior":
        return book
    if name == "retain_15s_prior":
        return prior_15 if prior_15 is not None else current
    if name == "opening_context_then_current":
        if seconds_to_close is not None and seconds_to_close >= 720.0 and prior_120 is not None:
            return blend_prob(current, prior_120, 0.50)
        return current
    if name == "shock_forget_else_light_15s_blend":
        if prior_15 is None or surprise_15 is None:
            return current
        if abs(surprise_15) >= 0.08:
            return current
        return blend_prob(current, prior_15, 0.85)
    if name == "book_anchor_on_large_surprise":
        if surprise_15 is not None and abs(surprise_15) >= 0.12 and book is not None:
            return blend_prob(current, book, 0.65)
        return current
    raise ValueError(f"unknown state variant: {name}")


STATE_VARIANTS = [
    "current_v28",
    "book_prior",
    "retain_15s_prior",
    "opening_context_then_current",
    "shock_forget_else_light_15s_blend",
    "book_anchor_on_large_surprise",
]


def summarize_state_variants(rows: list[dict[str, Any]]) -> dict[str, Any]:
    settled = [row for row in rows if row.get("outcome") is not None]
    by_variant: dict[str, dict[str, Any]] = {}
    for variant in STATE_VARIANTS:
        scored = []
        for row in settled:
            p = state_variant_prob(row, variant)
            brier = score_prob(p, as_float(row.get("outcome")))
            if p is None or brier is None:
                continue
            scored.append((p, brier, row))
        by_variant[variant] = {
            "count": len(scored),
            "avg_p": avg([item[0] for item in scored]),
            "win_rate": avg([float(item[2]["outcome"]) for item in scored]),
            "avg_brier": avg([item[1] for item in scored]),
            "gross_cents": sum(float(item[2].get("gross_cents") or 0.0) for item in scored),
        }
    raw_brier = by_variant["current_v28"]["avg_brier"]
    ranked = []
    for variant, bucket in by_variant.items():
        avg_brier = bucket.get("avg_brier")
        ranked.append(
            {
                "variant": variant,
                **bucket,
                "brier_minus_current_v28": None if avg_brier is None or raw_brier is None else avg_brier - raw_brier,
            }
        )
    ranked.sort(key=lambda row: (float("inf") if row["avg_brier"] is None else float(row["avg_brier"]), row["variant"]))
    return {"by_variant": by_variant, "ranked": ranked}


def write_csv(rows: list[dict[str, Any]]) -> None:
    if not rows:
        OUT_CSV.write_text("", encoding="utf-8")
        return
    keys: list[str] = []
    for row in rows:
        for key in row:
            if key not in keys:
                keys.append(key)
    with OUT_CSV.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=keys)
        writer.writeheader()
        writer.writerows(rows)


def fmt(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, float):
        return f"{value:.6f}"
    return str(value)


def write_md(report: dict[str, Any]) -> None:
    summary = report["summary"]
    views = report["views"]
    lines = [
        "# v28 Information Decay Diagnostic",
        "",
        "Shadow-only test of whether older same-market evidence should be retained or forgotten.",
        "",
        "Interpretation: positive `retained-current` Brier means stale retained evidence was worse than the current signal, so faster forgetting helped on this sample.",
        "",
        f"- Rows: `{summary['rows']}`",
        f"- Settled rows: `{summary['settled']}`",
        f"- Current p Brier: `{summary['current_p_brier']}`",
        f"- Current book Brier: `{summary['book_brier']}`",
        f"- Hypothetical gross on resolved rows: `${summary['gross_cents'] / 100.0:.2f}`",
        "",
        "## Half-Life Comparison",
        "",
        "| half-life sec | comparable | current p brier | retained p brier | retained-current p | current book brier | retained book brier | retained-current book | avg abs p surprise | stale worse |",
        "|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for half_life, row in summary["by_half_life"].items():
        lines.append(
            f"| {half_life} | {row['comparable']} | {fmt(row['current_p_brier'])} | {fmt(row['retained_p_brier'])} | "
            f"{fmt(row['retained_minus_current_p_brier'])} | {fmt(row['current_book_brier'])} | "
            f"{fmt(row['retained_book_brier'])} | {fmt(row['retained_minus_current_book_brier'])} | "
            f"{fmt(row['avg_abs_p_surprise'])} | {row['stale_worse_count']} |"
        )
    lines.extend([
        "",
        "## State FV Variants",
        "",
        "| rank | variant | count | avg p | win rate | avg brier | vs current | gross c |",
        "|---:|---|---:|---:|---:|---:|---:|---:|",
    ])
    for idx, row in enumerate(report["state_variants"]["ranked"], start=1):
        lines.append(
            f"| {idx} | {row['variant']} | {row['count']} | {fmt(row['avg_p'])} | {fmt(row['win_rate'])} | "
            f"{fmt(row['avg_brier'])} | {fmt(row['brier_minus_current_v28'])} | {fmt(row['gross_cents'])} |"
        )
    lines.extend([
        "",
        "## De-Duplicated Views",
        "",
        "| view | rows | settled | current p brier | retained-current p 15s | retained-current p 45s | retained-current p 120s | retained-current p 300s | gross c |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|",
    ])
    for name, bucket in views.items():
        by_half_life = bucket["by_half_life"]
        lines.append(
            f"| {name} | {bucket['rows']} | {bucket['settled']} | {fmt(bucket['current_p_brier'])} | "
            f"{fmt(by_half_life['15']['retained_minus_current_p_brier'])} | "
            f"{fmt(by_half_life['45']['retained_minus_current_p_brier'])} | "
            f"{fmt(by_half_life['120']['retained_minus_current_p_brier'])} | "
            f"{fmt(by_half_life['300']['retained_minus_current_p_brier'])} | "
            f"{fmt(bucket['gross_cents'])} |"
        )
    lines.extend(["", "## By Source", ""])
    for source, bucket in report["by_source"].items():
        lines.append(
            f"- `{source}`: rows={bucket['rows']}, settled={bucket['settled']}, "
            f"current_p_brier={bucket['current_p_brier']}, gross=${bucket['gross_cents'] / 100.0:.2f}"
        )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    rows = with_decay_features(observation_pool())
    report = {
        "half_life_seconds": HALF_LIFE_SECONDS,
        "summary": summarize_rows(rows),
        "views": summarize_views(rows),
        "state_variants": summarize_state_variants(rows),
        "by_source": summarize_by_source(rows),
        "rows": rows,
    }
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8")
    write_csv(rows)
    write_md(report)
    print(str(OUT_MD))


if __name__ == "__main__":
    main()
