"""Coverage-gap audit for the current top observable v28 stack.

Research-only; no live bot changes or orders.

The top observable stack now has some strict evidence, but its early strict
coverage is below target. This report explains whether the missing coverage is
settled evidence, pending market coverage, or an observable predicate failure.
"""
from __future__ import annotations

import json
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
PARENT_FILL_JSON = OUT_DIR / "v28_top_component_parent_fill_repair_child_latest.json"
OUT_JSON = OUT_DIR / "v28_top_observable_stack_coverage_gap_latest.json"
OUT_MD = OUT_DIR / "v28_top_observable_stack_coverage_gap_latest.md"


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
    if value is None or value == "":
        return default
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def build_report() -> dict[str, Any]:
    payload = load_json(PARENT_FILL_JSON)
    diag = payload.get("strict_forward_diagnostics") if isinstance(payload.get("strict_forward_diagnostics"), dict) else {}
    near = [row for row in diag.get("near_miss_examples") or [] if isinstance(row, dict)]
    by_market: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in near:
        by_market[str(row.get("market") or "")].append(row)

    selected = set()
    pending = set()
    settled = set()
    for row in diag.get("pending_parent_examples") or []:
        if isinstance(row, dict):
            pending.add(str(row.get("market") or ""))
    for row in diag.get("settled_parent_examples") or []:
        if isinstance(row, dict):
            settled.add(str(row.get("market") or ""))
            selected.add(str(row.get("market") or ""))
    for row in near:
        if row.get("broad_pass_count") == 4:
            selected.add(str(row.get("market") or ""))

    rows_by_market = []
    for market, rows in sorted(by_market.items()):
        best = sorted(
            rows,
            key=lambda row: (
                int(row.get("broad_pass_count") or 0),
                fnum(row.get("raw_edge"), -999.0),
                fnum(row.get("abs_d_sigma"), -999.0),
                fnum(row.get("ask_prob"), -999.0),
                -fnum(row.get("recross_hazard_score"), 999.0),
            ),
            reverse=True,
        )[0]
        rows_by_market.append(
            {
                "market": market,
                "selected_or_pass": market in selected,
                "pending_selected": market in pending,
                "settled_selected": market in settled,
                "best_side": best.get("side"),
                "best_source": best.get("source"),
                "best_side_won": best.get("side_won"),
                "best_pass_count": best.get("broad_pass_count"),
                "best_missing": best.get("broad_missing") or [],
                "raw_edge": best.get("raw_edge"),
                "recross_hazard_score": best.get("recross_hazard_score"),
                "abs_d_sigma": best.get("abs_d_sigma"),
                "ask_prob": best.get("ask_prob"),
            }
        )

    missing_predicates = Counter(
        pred
        for row in rows_by_market
        if not row["selected_or_pass"]
        for pred in row.get("best_missing") or []
    )
    return {
        "generated_at_utc": utc_now_iso(),
        "freeze_ts_utc": (payload.get("state") or {}).get("freeze_ts_utc") if isinstance(payload.get("state"), dict) else None,
        "future_denominator": diag.get("future_denominator"),
        "future_observation_rows": diag.get("future_observation_rows"),
        "selected_parent_rows": diag.get("selected_parent_rows"),
        "selected_settled_rows": diag.get("selected_settled_rows"),
        "selected_pending_rows": diag.get("selected_pending_rows"),
        "strict_absd_fill_rows": diag.get("strict_absd_fill_rows"),
        "markets_seen": len(rows_by_market),
        "coverage_gap_markets": [row for row in rows_by_market if not row["selected_or_pass"]],
        "selected_markets": [row for row in rows_by_market if row["selected_or_pass"]],
        "missing_predicate_counts": dict(sorted(missing_predicates.items())),
        "interpretation": [
            "Research-only coverage-gap audit; no live bot changes or orders.",
            "Early strict coverage is thin because only one of the first two forward markets passed the broad observable parent rule.",
            "The current missing market is not settled yet, so it is not evidence to relax predicates.",
            "If this pattern repeats after settlement, recross and abs-d are the first predicate failures to inspect.",
        ],
    }


def fmt(value: Any) -> str:
    if value is None:
        return "n/a"
    if isinstance(value, float):
        return f"{value:.3f}"
    return str(value)


def write_md(report: dict[str, Any]) -> None:
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    lines = [
        "# v28 Top Observable Stack Coverage Gap",
        "",
        "Research-only; no live bot changes or orders.",
        "",
        f"- Generated UTC: `{report.get('generated_at_utc')}`",
        f"- Freeze UTC: `{report.get('freeze_ts_utc')}`",
        f"- Future denominator: `{report.get('future_denominator')}`",
        f"- Future observation rows: `{report.get('future_observation_rows')}`",
        f"- Selected settled/pending rows: `{report.get('selected_settled_rows')}/{report.get('selected_pending_rows')}`",
        f"- Missing predicate counts on gap markets: `{report.get('missing_predicate_counts')}`",
        "",
        "## Coverage Gap Markets",
        "",
        "| market | best side | source | won | pass count | missing | raw edge | recross | abs d | ask |",
        "|---|---|---|---|---:|---|---:|---:|---:|---:|",
    ]
    for row in report.get("coverage_gap_markets") or []:
        missing = ",".join(str(part) for part in row.get("best_missing") or [])
        lines.append(
            f"| {row.get('market')} | {row.get('best_side')} | {row.get('best_source')} | {row.get('best_side_won')} | "
            f"{row.get('best_pass_count')} | {missing} | {fmt(row.get('raw_edge'))} | "
            f"{fmt(row.get('recross_hazard_score'))} | {fmt(row.get('abs_d_sigma'))} | {fmt(row.get('ask_prob'))} |"
        )
    lines.extend(
        [
            "",
            "## Selected Markets",
            "",
            "| market | best side | source | won | pass count | raw edge | recross | abs d | ask |",
            "|---|---|---|---|---:|---:|---:|---:|---:|",
        ]
    )
    for row in report.get("selected_markets") or []:
        lines.append(
            f"| {row.get('market')} | {row.get('best_side')} | {row.get('best_source')} | {row.get('best_side_won')} | "
            f"{row.get('best_pass_count')} | {fmt(row.get('raw_edge'))} | {fmt(row.get('recross_hazard_score'))} | "
            f"{fmt(row.get('abs_d_sigma'))} | {fmt(row.get('ask_prob'))} |"
        )
    lines.extend(["", "## Interpretation", ""])
    lines.extend(f"- {item}" for item in report.get("interpretation") or [])
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    report = build_report()
    write_md(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
