"""Book-favorite edge diagnostic for broad v28 candidate rows.

Several broad-coverage candidates can degenerate into "buy the executable book
favorite" because their effective FV equals the ask probability after forgetting.
This diagnostic asks whether those rows have realized edge over ask after an
estimated Kalshi entry fee, or whether the apparent P&L is just small-sample
favorite luck.
"""
from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

from probe_v28_rmt_forgetting_entry_bakeoff import estimate_entry_fee_cents


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
ENTRY_JSON = OUT_DIR / "v28_rmt_forgetting_entry_bakeoff_latest.json"
OUT_JSON = OUT_DIR / "v28_book_favorite_edge_diagnostic_latest.json"
OUT_CSV = OUT_DIR / "v28_book_favorite_edge_diagnostic_latest.csv"
OUT_MD = OUT_DIR / "v28_book_favorite_edge_diagnostic_latest.md"

WATCH_POLICIES = [
    "v28_raw_p50_edge0",
    "first_side_raw_later_book_p58_edge0",
    "first_side_raw_later_book_p60_edge0",
    "rmt_repetition_forget_p58_edge0",
    "rmt_repetition_forget_p60_edge0",
    "book_ask_prior_p60_edge0",
]


def as_float(value: Any) -> float | None:
    if value is None or value == "":
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def load_rows() -> list[dict[str, Any]]:
    if not ENTRY_JSON.exists():
        return []
    payload = json.loads(ENTRY_JSON.read_text(encoding="utf-8"))
    rows = payload.get("rows")
    return rows if isinstance(rows, list) else []


def ask_bucket(ask_cents: float | None) -> str:
    if ask_cents is None:
        return "unknown"
    if ask_cents < 50:
        return "ask_lt_50"
    if ask_cents < 60:
        return "ask_50_59"
    if ask_cents < 70:
        return "ask_60_69"
    if ask_cents < 80:
        return "ask_70_79"
    return "ask_80_plus"


def p_eff_mode(row: dict[str, Any]) -> str:
    p_eff = as_float(row.get("p_eff"))
    ask_prob = as_float(row.get("ask_prob"))
    raw = as_float(row.get("p_side"))
    if p_eff is None or ask_prob is None or raw is None:
        return "unknown"
    if abs(p_eff - ask_prob) <= 0.000001:
        return "book_exact"
    if abs(p_eff - raw) <= 0.000001:
        return "raw_exact"
    return "blend"


def summarize_group(rows: list[dict[str, Any]]) -> dict[str, Any]:
    settled = [row for row in rows if row.get("side_won") is not None and as_float(row.get("ask_cents")) is not None]
    if not settled:
        return {
            "count": 0,
            "win_rate": None,
            "avg_ask_prob": None,
            "realized_edge_vs_ask_prob": None,
            "fee_cents": 0.0,
            "gross_cents": 0.0,
            "net_cents_after_entry_fee": 0.0,
        }
    wins = sum(1 for row in settled if row.get("side_won") is True)
    ask_probs = [float(row["ask_cents"]) / 100.0 for row in settled]
    fees = [estimate_entry_fee_cents(row) for row in settled]
    gross = sum(float(row.get("gross_cents") or 0.0) for row in settled)
    fee_total = sum(fees)
    win_rate = wins / len(settled)
    avg_ask = sum(ask_probs) / len(ask_probs)
    return {
        "count": len(settled),
        "wins": wins,
        "losses": len(settled) - wins,
        "win_rate": win_rate,
        "avg_ask_prob": avg_ask,
        "realized_edge_vs_ask_prob": win_rate - avg_ask,
        "fee_cents": fee_total,
        "gross_cents": gross,
        "net_cents_after_entry_fee": gross - fee_total,
        "avg_net_cents_after_entry_fee": (gross - fee_total) / len(settled),
    }


def build_report() -> dict[str, Any]:
    rows = [row for row in load_rows() if row.get("policy") in WATCH_POLICIES]
    summaries: list[dict[str, Any]] = []
    detail_rows: list[dict[str, Any]] = []
    for policy in WATCH_POLICIES:
        policy_rows = [row for row in rows if row.get("policy") == policy]
        summaries.append({"policy": policy, "group": "all", **summarize_group(policy_rows)})
        for mode in ["raw_exact", "book_exact", "blend"]:
            summaries.append({"policy": policy, "group": f"mode_{mode}", **summarize_group([row for row in policy_rows if p_eff_mode(row) == mode])})
        for bucket in ["ask_lt_50", "ask_50_59", "ask_60_69", "ask_70_79", "ask_80_plus"]:
            summaries.append({"policy": policy, "group": bucket, **summarize_group([row for row in policy_rows if ask_bucket(as_float(row.get("ask_cents"))) == bucket])})
        for row in policy_rows:
            ask = as_float(row.get("ask_cents"))
            detail_rows.append(
                {
                    "policy": policy,
                    "market": row.get("market"),
                    "side": row.get("side"),
                    "source": row.get("source"),
                    "reason": row.get("reason"),
                    "mode": p_eff_mode(row),
                    "ask_bucket": ask_bucket(ask),
                    "ask_cents": ask,
                    "p_eff": row.get("p_eff"),
                    "p_side": row.get("p_side"),
                    "side_won": row.get("side_won"),
                    "gross_cents": row.get("gross_cents"),
                    "estimated_entry_fee_cents": estimate_entry_fee_cents(row),
                }
            )
    return {
        "watch_policies": WATCH_POLICIES,
        "summary": summaries,
        "rows": detail_rows,
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


def fmt(value: Any) -> str:
    if value is None:
        return "None"
    if isinstance(value, float):
        return f"{value:.6f}"
    return str(value)


def write_md(report: dict[str, Any]) -> None:
    lines = [
        "# v28 Book-Favorite Edge Diagnostic",
        "",
        "Checks whether broad candidates have realized edge over executable ask after estimated entry fees.",
        "",
        "## Policy Summary",
        "",
        "| policy | group | count | wins/losses | win rate | avg ask | realized edge vs ask | net c | avg net c |",
        "|---|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for row in report["summary"]:
        if row["group"] == "all" or row["group"].startswith("mode_"):
            lines.append(
                f"| {row['policy']} | {row['group']} | {row['count']} | {row.get('wins')}/{row.get('losses')} | "
                f"{fmt(row.get('win_rate'))} | {fmt(row.get('avg_ask_prob'))} | {fmt(row.get('realized_edge_vs_ask_prob'))} | "
                f"{fmt(row.get('net_cents_after_entry_fee'))} | {fmt(row.get('avg_net_cents_after_entry_fee'))} |"
            )
    lines.extend(["", "## Ask Buckets", ""])
    lines.append("| policy | bucket | count | wins/losses | win rate | avg ask | realized edge vs ask | net c |")
    lines.append("|---|---|---:|---:|---:|---:|---:|---:|")
    for row in report["summary"]:
        if row["group"].startswith("ask_"):
            lines.append(
                f"| {row['policy']} | {row['group']} | {row['count']} | {row.get('wins')}/{row.get('losses')} | "
                f"{fmt(row.get('win_rate'))} | {fmt(row.get('avg_ask_prob'))} | {fmt(row.get('realized_edge_vs_ask_prob'))} | "
                f"{fmt(row.get('net_cents_after_entry_fee'))} |"
            )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    report = build_report()
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_csv(report["rows"])
    write_md(report)
    print(str(OUT_MD))


if __name__ == "__main__":
    main()
