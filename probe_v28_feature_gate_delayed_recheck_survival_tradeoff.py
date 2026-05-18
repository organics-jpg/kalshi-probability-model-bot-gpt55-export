"""Survival tradeoff for feature-gate high-bid vs delayed-recheck exit watches.

Research-only. This consolidates existing diagnostic/frozen artifacts and does
not change live bot logic or candidate rules.
"""
from __future__ import annotations

import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
OUT_JSON = OUT_DIR / "v28_feature_gate_delayed_recheck_survival_tradeoff_latest.json"
OUT_MD = OUT_DIR / "v28_feature_gate_delayed_recheck_survival_tradeoff_latest.md"

PATH_RISK = OUT_DIR / "v28_feature_gate_exit_bid_path_risk_latest.json"
DELAYED_WATCH = OUT_DIR / "v28_frozen_feature_gate_exit_bid_delayed_recheck_latest.json"


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


def fnum(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def cents(value: Any) -> str:
    try:
        c = float(value)
    except (TypeError, ValueError):
        return ""
    return f"{c:.0f}c"


def lane_rows(payload: dict[str, Any], lane_name: str) -> list[dict[str, Any]]:
    for lane in payload.get("lanes") or []:
        if lane.get("lane") == lane_name:
            return lane.get("rows") or []
    return []


def reason_group(row: dict[str, Any]) -> str:
    keys = " ".join((row.get("exit_reason_counts") or {}).keys())
    if "exit_value_over_hold" in keys:
        return "value_over_hold"
    if "probability_reduce" in keys:
        return "probability_reduce"
    if "probability_collapse" in keys:
        return "probability_collapse"
    return "other"


def summarize(rows: list[dict[str, Any]], delta_key: str) -> dict[str, Any]:
    reason_counts = Counter(row["reason_group"] for row in rows)
    return {
        "rows": len(rows),
        "delta_vs_live_cents": sum(fnum(row.get(delta_key)) for row in rows),
        "adverse_10c_rows": sum(1 for row in rows if row.get("adverse_10c")),
        "adverse_25c_rows": sum(1 for row in rows if row.get("adverse_25c")),
        "adverse_50c_rows": sum(1 for row in rows if row.get("adverse_50c")),
        "worst_min_after_exit_bid_cents": min([fnum(row.get("min_after_exit_bid_cents")) for row in rows], default=None),
        "reason_group_counts": dict(reason_counts),
    }


def build_report() -> dict[str, Any]:
    path_risk = load_json(PATH_RISK)
    delayed = load_json(DELAYED_WATCH)
    high_rows = lane_rows(path_risk, "diagnostic_feature_gate_exit_bid")
    delayed_rows = lane_rows(delayed, "diagnostic_prefreeze_context")
    delayed_by_market = {row.get("market"): row for row in delayed_rows}

    joined = []
    for row in high_rows:
        market = row.get("market")
        delayed_row = delayed_by_market.get(market, {})
        delayed_suppressed = bool(delayed_row.get("delayed_recheck_suppressed"))
        joined.append(
            {
                "market": market,
                "source": row.get("source"),
                "side": row.get("side"),
                "reason_group": reason_group(row),
                "high_bid_delta_vs_live_cents": fnum(row.get("delta_vs_live_cents")),
                "delayed_delta_vs_live_cents": fnum(delayed_row.get("delayed_recheck_delta_cents")) if delayed_suppressed else 0.0,
                "delta_given_up_cents": fnum(row.get("delta_vs_live_cents")) - (fnum(delayed_row.get("delayed_recheck_delta_cents")) if delayed_suppressed else 0.0),
                "delayed_suppressed": delayed_suppressed,
                "exit_bid_min": row.get("exit_bid_min"),
                "recheck_bid": delayed_row.get("recheck_bid"),
                "window_drop_cents": delayed_row.get("window_drop_cents"),
                "min_window_bid": delayed_row.get("min_window_bid"),
                "min_after_exit_bid_cents": row.get("min_after_exit_bid_cents"),
                "adverse_10c": bool(row.get("adverse_10c")),
                "adverse_25c": bool(row.get("adverse_25c")),
                "adverse_50c": bool(row.get("adverse_50c")),
            }
        )

    suppressed = [row for row in joined if row["delayed_suppressed"]]
    rejected = [row for row in joined if not row["delayed_suppressed"]]
    rejected.sort(key=lambda row: fnum(row.get("min_after_exit_bid_cents")))
    suppressed.sort(key=lambda row: fnum(row.get("min_after_exit_bid_cents")))

    return {
        "generated_at_utc": utc_now_iso(),
        "sources": {
            "path_risk": str(PATH_RISK),
            "delayed_watch": str(DELAYED_WATCH),
        },
        "high_bid_summary": summarize(joined, "high_bid_delta_vs_live_cents"),
        "delayed_suppressed_summary": summarize(suppressed, "delayed_delta_vs_live_cents"),
        "delayed_rejected_summary": summarize(rejected, "high_bid_delta_vs_live_cents"),
        "joined_rows": joined,
        "rejected_rows": rejected,
        "suppressed_worst_path_rows": suppressed[:8],
        "interpretation": [
            "High-bid suppression catches every diagnostic winner clip but includes large adverse post-exit excursions.",
            "The frozen delayed-recheck rule gives up some diagnostic recovery to avoid the weakest air-pocket holds, but it does not eliminate all large adverse excursions.",
            "Rejected rows are not automatically bad exclusions; they are the survival guard doing its job and need strict post-freeze validation.",
        ],
    }


def write_report(payload: dict[str, Any]) -> None:
    high = payload["high_bid_summary"]
    supp = payload["delayed_suppressed_summary"]
    rej = payload["delayed_rejected_summary"]
    lines = [
        "# v28 Feature-Gate Delayed-Recheck Survival Tradeoff",
        "",
        "Research-only consolidation. No live bot changes, no orders, no new candidate rule.",
        "",
        f"- Generated UTC: `{payload['generated_at_utc']}`",
        "",
        "## Summary",
        "",
        "| set | rows | delta vs live | adverse 10/25/50 | worst min-after-exit | reason groups |",
        "|---|---:|---:|---:|---:|---|",
        f"| high-bid caught | {high['rows']} | {cents(high['delta_vs_live_cents'])} | {high['adverse_10c_rows']}/{high['adverse_25c_rows']}/{high['adverse_50c_rows']} | {cents(high['worst_min_after_exit_bid_cents'])} | {high['reason_group_counts']} |",
        f"| delayed-recheck kept | {supp['rows']} | {cents(supp['delta_vs_live_cents'])} | {supp['adverse_10c_rows']}/{supp['adverse_25c_rows']}/{supp['adverse_50c_rows']} | {cents(supp['worst_min_after_exit_bid_cents'])} | {supp['reason_group_counts']} |",
        f"| delayed-recheck rejected | {rej['rows']} | {cents(rej['delta_vs_live_cents'])} | {rej['adverse_10c_rows']}/{rej['adverse_25c_rows']}/{rej['adverse_50c_rows']} | {cents(rej['worst_min_after_exit_bid_cents'])} | {rej['reason_group_counts']} |",
        "",
        "## Rejected By Delayed Recheck",
        "",
        "| market | reason | high-bid delta | given up | exit bid | recheck bid | drop | min window | min-after-exit | adverse |",
        "|---|---|---:|---:|---:|---:|---:|---:|---:|---|",
    ]
    for row in payload["rejected_rows"]:
        adverse = "/".join(
            flag for flag, present in [("10", row.get("adverse_10c")), ("25", row.get("adverse_25c")), ("50", row.get("adverse_50c"))] if present
        )
        lines.append(
            "| {market} | {reason} | {delta} | {given} | {exit_bid} | {recheck} | {drop} | {min_window} | {min_after} | {adverse} |".format(
                market=row.get("market"),
                reason=row.get("reason_group"),
                delta=cents(row.get("high_bid_delta_vs_live_cents")),
                given=cents(row.get("delta_given_up_cents")),
                exit_bid=row.get("exit_bid_min"),
                recheck=row.get("recheck_bid"),
                drop=row.get("window_drop_cents"),
                min_window=row.get("min_window_bid"),
                min_after=cents(row.get("min_after_exit_bid_cents")),
                adverse=adverse,
            )
        )

    lines.extend(
        [
            "",
            "## Worst Kept Paths",
            "",
            "| market | reason | delayed delta | exit bid | recheck bid | drop | min-after-exit | adverse |",
            "|---|---|---:|---:|---:|---:|---:|---|",
        ]
    )
    for row in payload["suppressed_worst_path_rows"]:
        adverse = "/".join(
            flag for flag, present in [("10", row.get("adverse_10c")), ("25", row.get("adverse_25c")), ("50", row.get("adverse_50c"))] if present
        )
        lines.append(
            "| {market} | {reason} | {delta} | {exit_bid} | {recheck} | {drop} | {min_after} | {adverse} |".format(
                market=row.get("market"),
                reason=row.get("reason_group"),
                delta=cents(row.get("delayed_delta_vs_live_cents")),
                exit_bid=row.get("exit_bid_min"),
                recheck=row.get("recheck_bid"),
                drop=row.get("window_drop_cents"),
                min_after=cents(row.get("min_after_exit_bid_cents")),
                adverse=adverse,
            )
        )

    lines.extend(["", "## Interpretation", ""])
    for item in payload["interpretation"]:
        lines.append(f"- {item}")

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    payload = build_report()
    write_report(payload)
    print(OUT_MD)


if __name__ == "__main__":
    main()
