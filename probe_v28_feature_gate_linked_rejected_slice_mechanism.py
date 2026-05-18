"""Linked rejected-slice mechanism audit for the broad feature-gate row.

Research-only; no live bot changes or orders.

The linked source-runway shows the broad raw03 feature-gate row is still
source-quality blocked. This probe classifies the rejected-actionable slice
after linking finalized market outcomes, so the source-quality failure mode is
described by observable features rather than by PnL rows that are still marked
pending in the research surface.
"""
from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from probe_v28_boundary_clock_feature_gate_candidate import RULES, best_per_market, market, passes, raw_edge, source
from probe_v28_danger_tag_replacement_diagnostic import row_net_after_fee
from probe_v28_frozen_boundary_clock_repair_entry import future_surfaces as entry_surfaces


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
FEATURE_STATE_JSON = OUT_DIR / "v28_boundary_clock_feature_gate_candidate_state.json"
MARKET_RESULTS_CSV = ROOT / "stats" / "live_mushroom_v28_size2" / "market_results.csv"
OUT_JSON = OUT_DIR / "v28_feature_gate_linked_rejected_slice_mechanism_latest.json"
OUT_MD = OUT_DIR / "v28_feature_gate_linked_rejected_slice_mechanism_latest.md"

RULE_NAME = "raw03_recross70_abs075"
LANE = "post_feature_freeze_entry"


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


def load_market_results(path: Path) -> dict[str, dict[str, str]]:
    out: dict[str, dict[str, str]] = {}
    if not path.exists():
        return out
    with path.open("r", encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle):
            ticker = str(row.get("market") or "")
            if ticker:
                out[ticker] = row
    return out


def fnum(value: Any, default: float = 0.0) -> float:
    if value is None or value == "":
        return default
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def side_won(side: str, result: str) -> bool | None:
    if side not in {"yes", "no"} or result not in {"yes", "no"}:
        return None
    return side == result


def linked_row(row: dict[str, Any], market_results: dict[str, dict[str, str]]) -> dict[str, Any]:
    out = dict(row)
    if out.get("side_won") is None:
        result = str((market_results.get(market(out)) or {}).get("result") or "")
        won = side_won(str(out.get("side") or ""), result)
        if won is not None:
            out["side_won"] = won
            out["linked_market_result"] = result
    out["net_cents"] = row_net_after_fee(out)
    return out


def p_side(row: dict[str, Any]) -> float:
    value = fnum(row.get("p_side"), -1.0)
    if value >= 0:
        return value
    p_yes = fnum(row.get("p_yes"), -1.0)
    if p_yes < 0:
        return 0.0
    return p_yes if str(row.get("side") or "") == "yes" else 1.0 - p_yes


def ask(row: dict[str, Any]) -> float:
    value = fnum(row.get("ask_prob"), -1.0)
    if value >= 0:
        return value
    cents = fnum(row.get("ask_cents"), -1.0)
    return cents / 100.0 if cents >= 0 else 0.0


def abs_d(row: dict[str, Any]) -> float:
    return abs(fnum(row.get("abs_d_sigma")))


def recross(row: dict[str, Any]) -> float:
    return fnum(row.get("recross_hazard_score"))


def seconds_to_close(row: dict[str, Any]) -> float:
    return fnum(row.get("seconds_to_close"))


def depth(row: dict[str, Any]) -> float:
    return fnum(row.get("eligible_depth"))


def feature_tags(row: dict[str, Any]) -> list[str]:
    tags = ["source_quality_error"]
    if ask(row) < 0.50:
        tags.append("cheap_tail_ask_lt50")
    elif ask(row) < 0.65:
        tags.append("mid_ask_50_65")
    if abs_d(row) < 0.65:
        tags.append("weak_boundary_distance_lt65")
    elif abs_d(row) < 0.85:
        tags.append("moderate_boundary_distance_65_85")
    if recross(row) > 0.60:
        tags.append("high_recross_gt60")
    elif recross(row) > 0.30:
        tags.append("moderate_recross_30_60")
    if p_side(row) < 0.75:
        tags.append("low_p_side_lt75")
    elif p_side(row) < 0.85:
        tags.append("moderate_p_side_75_85")
    if seconds_to_close(row) < 240.0:
        tags.append("early_observation_stc_lt240")
    if depth(row) < 100.0:
        tags.append("thin_depth_lt100")
    edge = raw_edge(row)
    if edge is not None and edge < 0.05:
        tags.append("thin_raw_edge_lt05")
    return tags


def summarize(rows: list[dict[str, Any]]) -> dict[str, Any]:
    settled = [row for row in rows if row.get("side_won") is not None]
    net_cents = sum(fnum(row.get("net_cents")) for row in settled)
    return {
        "rows": len(rows),
        "settled": len(settled),
        "wins": sum(1 for row in settled if row.get("side_won") is True),
        "losses": sum(1 for row in settled if row.get("side_won") is False),
        "net_cents": net_cents,
        "avg_net_cents": net_cents / len(settled) if settled else None,
    }


def tag_table(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        for tag in feature_tags(row):
            grouped[tag].append(row)
    out = []
    for tag, items in grouped.items():
        summary = summarize(items)
        summary["tag"] = tag
        out.append(summary)
    out.sort(key=lambda row: (float(row.get("net_cents") or 0.0), -int(row.get("rows") or 0)))
    return out


def compact(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "market": market(row),
        "source": source(row),
        "side": row.get("side"),
        "side_won": row.get("side_won"),
        "net_cents": row.get("net_cents"),
        "ask_prob": ask(row),
        "p_side": p_side(row),
        "raw_edge": raw_edge(row),
        "recross_hazard_score": recross(row),
        "abs_d_sigma": abs_d(row),
        "seconds_to_close": seconds_to_close(row),
        "eligible_depth": depth(row),
        "tags": feature_tags(row),
    }


def build_report() -> dict[str, Any]:
    state = load_json(FEATURE_STATE_JSON)
    freeze_ts = str(state.get("freeze_ts_utc") or "")
    all_rows, _, denominator = entry_surfaces(freeze_ts)
    selected = best_per_market([row for row in all_rows if passes(row, RULES[RULE_NAME])])
    market_results = load_market_results(MARKET_RESULTS_CSV)
    linked = [linked_row(row, market_results) for row in selected]
    approved = [row for row in linked if source(row) == "approved_entry"]
    rejected = [row for row in linked if source(row) != "approved_entry"]
    rejected_losses = [row for row in rejected if row.get("side_won") is False]
    rejected_wins = [row for row in rejected if row.get("side_won") is True]
    report = {
        "generated_at_utc": utc_now_iso(),
        "lane": LANE,
        "candidate": f"{LANE}_{RULE_NAME}",
        "freeze_ts_utc": freeze_ts,
        "future_denominator": denominator,
        "selected_summary": summarize(linked),
        "approved_summary": summarize(approved),
        "rejected_summary": summarize(rejected),
        "rejected_loss_summary": summarize(rejected_losses),
        "rejected_win_summary": summarize(rejected_wins),
        "tag_table": tag_table(rejected),
        "worst_rejected_rows": [compact(row) for row in sorted(rejected, key=lambda item: fnum(item.get("net_cents")))[:10]],
        "best_rejected_rows": [compact(row) for row in sorted(rejected, key=lambda item: fnum(item.get("net_cents")), reverse=True)[:5]],
    }
    report["interpretation"] = interpretation(report)
    return report


def interpretation(report: dict[str, Any]) -> list[str]:
    rejected = report.get("rejected_summary") or {}
    losses = report.get("rejected_loss_summary") or {}
    worst_tags = (report.get("tag_table") or [])[:4]
    return [
        "Source labels are audit-only here; the tags are observable failure descriptors for the rejected-actionable slice.",
        (
            f"Rejected-actionable slice is {rejected.get('wins')}/{rejected.get('losses')} for "
            f"{rejected.get('net_cents')}c, but losses are frequent: {losses.get('rows')} rejected rows lose."
        ),
        f"Worst linked rejected-slice tags: {[row.get('tag') for row in worst_tags]}.",
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
        "# v28 Feature-Gate Linked Rejected-Slice Mechanism",
        "",
        "Research-only mechanism audit. No live bot changes or orders.",
        "",
        f"- Generated UTC: `{report.get('generated_at_utc')}`",
        f"- Candidate: `{report.get('candidate')}`",
        f"- Freeze UTC: `{report.get('freeze_ts_utc')}`",
        f"- Future denominator: `{report.get('future_denominator')}`",
        "",
        "## Interpretation",
        "",
    ]
    for note in report.get("interpretation") or []:
        lines.append(f"- {note}")
    lines.extend(
        [
            "",
            "## Summaries",
            "",
            "| slice | rows | settled | W/L | net c | avg c |",
            "|---|---:|---:|---:|---:|---:|",
        ]
    )
    for label, key in [
        ("selected", "selected_summary"),
        ("approved", "approved_summary"),
        ("rejected", "rejected_summary"),
        ("rejected_losses", "rejected_loss_summary"),
        ("rejected_wins", "rejected_win_summary"),
    ]:
        row = report.get(key) or {}
        lines.append(
            f"| {label} | {row.get('rows')} | {row.get('settled')} | {row.get('wins')}/{row.get('losses')} | "
            f"{fmt(row.get('net_cents'))} | {fmt(row.get('avg_net_cents'))} |"
        )
    lines.extend(
        [
            "",
            "## Rejected Slice Tags",
            "",
            "| tag | rows | settled | W/L | net c | avg c |",
            "|---|---:|---:|---:|---:|---:|",
        ]
    )
    for row in report.get("tag_table") or []:
        lines.append(
            f"| {row.get('tag')} | {row.get('rows')} | {row.get('settled')} | {row.get('wins')}/{row.get('losses')} | "
            f"{fmt(row.get('net_cents'))} | {fmt(row.get('avg_net_cents'))} |"
        )
    lines.extend(
        [
            "",
            "## Worst Rejected Rows",
            "",
            "| market | side | won | net c | ask | p side | edge | recross | abs d | stc | depth | tags |",
            "|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---|",
        ]
    )
    for row in report.get("worst_rejected_rows") or []:
        lines.append(
            f"| {row.get('market')} | {row.get('side')} | {row.get('side_won')} | {fmt(row.get('net_cents'))} | "
            f"{fmt(row.get('ask_prob'))} | {fmt(row.get('p_side'))} | {fmt(row.get('raw_edge'))} | "
            f"{fmt(row.get('recross_hazard_score'))} | {fmt(row.get('abs_d_sigma'))} | "
            f"{fmt(row.get('seconds_to_close'))} | {fmt(row.get('eligible_depth'))} | "
            f"{', '.join(row.get('tags') or [])} |"
        )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    report = build_report()
    write_md(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
