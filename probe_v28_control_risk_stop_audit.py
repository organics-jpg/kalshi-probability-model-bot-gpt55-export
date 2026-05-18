"""Audit the control risk-stop blocker used by v28 live-readiness reports.

Research-only; no live bot changes or orders.

The live-readiness gate correctly treats a control risk stop as a hard blocker,
but the stop can be triggered by very different mechanisms. This report
separates account-survival drawdown from raw loss-count churn so sidecar
research knows what must be repaired before any live trial.
"""
from __future__ import annotations

import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
SCORECARD_JSON = OUT_DIR / "v28_continuous_scorecard_latest.json"
OUT_JSON = OUT_DIR / "v28_control_risk_stop_audit_latest.json"
OUT_MD = OUT_DIR / "v28_control_risk_stop_audit_latest.md"

DEFAULT_LOSS_STOP_COUNT = 5
DEFAULT_DRAWDOWN_STOP_PCT = 40.0
FULL_LOSS_CENTS = 100.0


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


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


def pct(numerator: float, denominator: float) -> float | None:
    if denominator <= 0:
        return None
    return numerator / denominator * 100.0


def loss_bucket(value: float) -> str:
    loss = abs(value)
    if loss < 10.0:
        return "micro_lt_10c"
    if loss < 25.0:
        return "small_10_24c"
    if loss < 50.0:
        return "medium_25_49c"
    if loss < FULL_LOSS_CENTS:
        return "large_50_99c"
    return "full_loss_ge_100c"


def sorted_scored_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    scored = [row for row in rows if as_float(row.get("actual_gross_cents")) is not None]
    return sorted(scored, key=lambda row: str(row.get("entry_ts") or row.get("exit_ts") or ""))


def streaks(scored: list[dict[str, Any]]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    current: list[dict[str, Any]] = []
    for row in scored:
        gross = as_float(row.get("actual_gross_cents")) or 0.0
        if gross < 0:
            current.append(row)
            continue
        if current:
            out.append(summarize_streak(current))
            current = []
    if current:
        out.append(summarize_streak(current))
    out.sort(key=lambda row: (row["rows"], abs(row["net_cents"])), reverse=True)
    return out


def summarize_streak(rows: list[dict[str, Any]]) -> dict[str, Any]:
    gross = [as_float(row.get("actual_gross_cents")) or 0.0 for row in rows]
    return {
        "rows": len(rows),
        "net_cents": sum(gross),
        "first_market": rows[0].get("market"),
        "last_market": rows[-1].get("market"),
        "first_ts": rows[0].get("entry_ts") or rows[0].get("exit_ts"),
        "last_ts": rows[-1].get("entry_ts") or rows[-1].get("exit_ts"),
        "failure_classes": dict(Counter(str(row.get("failure_class") or "unknown") for row in rows)),
    }


def build_report() -> dict[str, Any]:
    scorecard = load_json(SCORECARD_JSON)
    summary = scorecard.get("summary") or {}
    rows = scorecard.get("rows") or []
    scored = sorted_scored_rows(rows if isinstance(rows, list) else [])
    losing = [row for row in scored if (as_float(row.get("actual_gross_cents")) or 0.0) < 0.0]
    winning = [row for row in scored if (as_float(row.get("actual_gross_cents")) or 0.0) > 0.0]
    flat = [row for row in scored if (as_float(row.get("actual_gross_cents")) or 0.0) == 0.0]

    loss_values = [as_float(row.get("actual_gross_cents")) or 0.0 for row in losing]
    win_values = [as_float(row.get("actual_gross_cents")) or 0.0 for row in winning]
    gross = as_float(summary.get("gross_cents")) or 0.0
    max_drawdown = as_float(summary.get("max_drawdown_cents")) or 0.0
    max_drawdown_pct = as_float(summary.get("max_drawdown_pct")) or 0.0
    net_losses = int(as_float(summary.get("net_losses")) or len(losing))
    loss_stop_count = DEFAULT_LOSS_STOP_COUNT
    drawdown_stop_pct = DEFAULT_DRAWDOWN_STOP_PCT
    risk_stop_by_loss_count = net_losses >= loss_stop_count
    risk_stop_by_drawdown = max_drawdown_pct >= drawdown_stop_pct
    full_loss_events = [row for row in losing if abs(as_float(row.get("actual_gross_cents")) or 0.0) >= FULL_LOSS_CENTS]
    near_full_loss_events = [
        row for row in losing
        if FULL_LOSS_CENTS * 0.5 <= abs(as_float(row.get("actual_gross_cents")) or 0.0) < FULL_LOSS_CENTS
    ]
    bucket_counts = Counter(loss_bucket(value) for value in loss_values)
    bucket_net = Counter()
    for value in loss_values:
        bucket_net[loss_bucket(value)] += value

    by_failure: dict[str, dict[str, Any]] = {}
    for row in losing:
        label = str(row.get("failure_class") or "unknown")
        item = by_failure.setdefault(label, {"rows": 0, "net_cents": 0.0})
        item["rows"] += 1
        item["net_cents"] += as_float(row.get("actual_gross_cents")) or 0.0

    by_flag: dict[str, dict[str, Any]] = {}
    for row in losing:
        for key, value in row.items():
            if not key.startswith("h") or value is not True:
                continue
            item = by_flag.setdefault(key, {"rows": 0, "net_cents": 0.0})
            item["rows"] += 1
            item["net_cents"] += as_float(row.get("actual_gross_cents")) or 0.0

    top_loss_rows = sorted(
        losing,
        key=lambda row: as_float(row.get("actual_gross_cents")) or 0.0,
    )[:12]
    top_loss_streaks = streaks(scored)[:8]

    report = {
        "generated_at_utc": utc_now_iso(),
        "scorecard_path": str(SCORECARD_JSON),
        "summary": {
            "risk_stop": bool(summary.get("risk_stop")),
            "risk_stop_reason": summary.get("risk_stop_reason"),
            "risk_stop_by_loss_count": risk_stop_by_loss_count,
            "risk_stop_by_drawdown": risk_stop_by_drawdown,
            "loss_stop_count": loss_stop_count,
            "drawdown_stop_pct": drawdown_stop_pct,
            "scored_trades": len(scored),
            "losing_trades": len(losing),
            "winning_trades": len(winning),
            "flat_trades": len(flat),
            "gross_cents": gross,
            "max_drawdown_cents": max_drawdown,
            "max_drawdown_pct": max_drawdown_pct,
            "gross_full_loss_cushion": int(gross // FULL_LOSS_CENTS) if gross > 0 else 0,
            "drawdown_full_loss_equivalent": abs(max_drawdown) / FULL_LOSS_CENTS,
            "full_loss_events": len(full_loss_events),
            "near_full_loss_events_50_99c": len(near_full_loss_events),
            "avg_losing_trade_cents": sum(loss_values) / len(loss_values) if loss_values else None,
            "avg_winning_trade_cents": sum(win_values) / len(win_values) if win_values else None,
            "loss_trade_share_pct": pct(len(losing), len(scored)),
            "profit_factor_trade_gross": (
                sum(win_values) / abs(sum(loss_values)) if loss_values and sum(loss_values) < 0 else None
            ),
        },
        "loss_buckets": {
            key: {"rows": bucket_counts[key], "net_cents": bucket_net[key]}
            for key in sorted(bucket_counts)
        },
        "losing_failure_classes": dict(sorted(by_failure.items(), key=lambda item: item[1]["net_cents"])),
        "losing_physics_flags": dict(sorted(by_flag.items(), key=lambda item: item[1]["net_cents"])),
        "top_loss_streaks": top_loss_streaks,
        "largest_losing_trades": [
            {
                "market": row.get("market"),
                "side": row.get("side"),
                "result": row.get("result"),
                "entry_ts": row.get("entry_ts"),
                "gross_cents": row.get("actual_gross_cents"),
                "hold_gross_cents": row.get("hold_gross_cents"),
                "exit_value_cents": row.get("exit_value_cents"),
                "failure_class": row.get("failure_class"),
                "flags": [key for key, value in row.items() if key.startswith("h") and value is True],
            }
            for row in top_loss_rows
        ],
        "interpretation": [],
    }
    report["interpretation"] = interpretation(report)
    return report


def interpretation(report: dict[str, Any]) -> list[str]:
    summary = report["summary"]
    notes = [
        "This audit is explanatory only; it does not clear live-readiness or weaken the risk stop.",
        (
            f"Risk stop is {summary['risk_stop']} by loss-count={summary['risk_stop_by_loss_count']} "
            f"and drawdown={summary['risk_stop_by_drawdown']}."
        ),
        (
            f"Control window is net positive {summary['gross_cents']}c with max drawdown "
            f"{summary['max_drawdown_cents']}c ({summary['max_drawdown_pct']}%)."
        ),
        (
            f"Losses are {summary['losing_trades']} of {summary['scored_trades']} scored trades; "
            f"full-loss events are {summary['full_loss_events']} and 50-99c near-full losses are "
            f"{summary['near_full_loss_events_50_99c']}."
        ),
    ]
    if summary["risk_stop_by_loss_count"] and not summary["risk_stop_by_drawdown"]:
        notes.append(
            "The active blocker is churn/loss-count, not current drawdown-account-survival failure. Candidate exits still need to reduce loss clusters before any sidecar trial."
        )
    return notes


def money(value: Any) -> str:
    numeric = as_float(value)
    if numeric is None:
        return "n/a"
    return f"{numeric:.0f}c (${numeric / 100.0:.2f})"


def fmt(value: Any) -> str:
    if value is None:
        return "n/a"
    if isinstance(value, float):
        return f"{value:.6f}"
    return str(value)


def write_md(report: dict[str, Any]) -> None:
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8")
    summary = report["summary"]
    lines = [
        "# v28 Control Risk-Stop Audit",
        "",
        "Research-only; no live bot changes or orders.",
        "",
        f"- Generated UTC: `{report['generated_at_utc']}`",
        f"- Source scorecard: `{report['scorecard_path']}`",
        "",
        "## Interpretation",
        "",
    ]
    lines.extend(f"- {note}" for note in report.get("interpretation") or [])
    lines.extend([
        "",
        "## Summary",
        "",
        f"- Risk stop: `{summary['risk_stop']}` `{summary['risk_stop_reason']}`",
        f"- Loss-count trigger: `{summary['risk_stop_by_loss_count']}` ({summary['losing_trades']} losses vs stop {summary['loss_stop_count']})",
        f"- Drawdown trigger: `{summary['risk_stop_by_drawdown']}` ({summary['max_drawdown_pct']:.2f}% vs stop {summary['drawdown_stop_pct']:.2f}%)",
        f"- Gross PnL: `{money(summary['gross_cents'])}`",
        f"- Max drawdown: `{money(summary['max_drawdown_cents'])}`",
        f"- Full-loss events: `{summary['full_loss_events']}`",
        f"- Near-full losses 50-99c: `{summary['near_full_loss_events_50_99c']}`",
        f"- Profit factor: `{fmt(summary['profit_factor_trade_gross'])}`",
        "",
        "## Loss Buckets",
        "",
        "| bucket | rows | net |",
        "|---|---:|---:|",
    ])
    for bucket, item in report.get("loss_buckets", {}).items():
        lines.append(f"| `{bucket}` | {item.get('rows')} | {money(item.get('net_cents'))} |")
    lines.extend([
        "",
        "## Losing Failure Classes",
        "",
        "| class | rows | net |",
        "|---|---:|---:|",
    ])
    for label, item in report.get("losing_failure_classes", {}).items():
        lines.append(f"| `{label}` | {item.get('rows')} | {money(item.get('net_cents'))} |")
    lines.extend([
        "",
        "## Largest Loss Streaks",
        "",
        "| rows | net | first market | last market | failure classes |",
        "|---:|---:|---|---|---|",
    ])
    for row in report.get("top_loss_streaks") or []:
        lines.append(
            f"| {row.get('rows')} | {money(row.get('net_cents'))} | `{row.get('first_market')}` | "
            f"`{row.get('last_market')}` | `{row.get('failure_classes')}` |"
        )
    lines.extend([
        "",
        "## Largest Losing Trades",
        "",
        "| market | side | result | gross | hold | exit value | failure | flags |",
        "|---|---|---|---:|---:|---:|---|---|",
    ])
    for row in report.get("largest_losing_trades") or []:
        lines.append(
            f"| `{row.get('market')}` | {row.get('side')} | {row.get('result')} | "
            f"{money(row.get('gross_cents'))} | {money(row.get('hold_gross_cents'))} | "
            f"{money(row.get('exit_value_cents'))} | `{row.get('failure_class')}` | "
            f"`{','.join(row.get('flags') or [])}` |"
        )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    report = build_report()
    write_md(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
