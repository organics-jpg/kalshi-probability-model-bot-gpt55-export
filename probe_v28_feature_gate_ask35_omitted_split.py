"""Diagnostic split of ask35 frontier omitted rows.

Research-only; no live bot changes or orders. The ask35 frontier is clean but
under-covered. This probe studies the omitted rows to see whether coverage can
be repaired by an observable physical mechanism instead of blind threshold
relaxation.
"""
from __future__ import annotations

import itertools
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from statistics import mean, median
from typing import Any


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
MECH_JSON = OUT_DIR / "v28_boundary_clock_feature_gate_frontier_mechanism_latest.json"
OUT_JSON = OUT_DIR / "v28_feature_gate_ask35_omitted_split_latest.json"
OUT_MD = OUT_DIR / "v28_feature_gate_ask35_omitted_split_latest.md"


def load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
    return payload if isinstance(payload, dict) else {}


def as_float(value: Any) -> float | None:
    try:
        if value is None or value == "":
            return None
        return float(value)
    except (TypeError, ValueError):
        return None


def net(row: dict[str, Any]) -> float:
    return float(as_float(row.get("net_cents")) or 0.0)


def feature(row: dict[str, Any], name: str) -> float | None:
    return as_float(row.get(name))


def side_won(row: dict[str, Any]) -> bool:
    return bool(row.get("side_won") or row.get("outcome") == "win")


def summarize_rows(rows: list[dict[str, Any]]) -> dict[str, Any]:
    if not rows:
        return {
            "rows": 0,
            "net_cents": 0.0,
            "wins": 0,
            "losses": 0,
            "source_counts": {},
            "tag_counts": {},
            "fail_reason_counts": {},
            "feature_ranges": {},
        }
    wins = sum(1 for row in rows if side_won(row))
    losses = len(rows) - wins
    ranges: dict[str, list[float] | None] = {}
    for name in ("raw_edge", "recross_hazard_score", "abs_d_sigma", "ask_prob"):
        values = [value for row in rows if (value := feature(row, name)) is not None]
        ranges[name] = [min(values), median(values), max(values)] if values else None
    tag_counts: Counter[str] = Counter()
    fail_counts: Counter[str] = Counter()
    for row in rows:
        tag_counts.update(str(tag) for tag in row.get("mechanism_tags") or [])
        fail_counts.update(str(reason) for reason in row.get("fail_reasons") or [])
    return {
        "rows": len(rows),
        "net_cents": sum(net(row) for row in rows),
        "avg_net_cents": mean(net(row) for row in rows),
        "wins": wins,
        "losses": losses,
        "source_counts": dict(Counter(str(row.get("source") or "") for row in rows)),
        "side_counts": dict(Counter(str(row.get("side") or "") for row in rows)),
        "tag_counts": dict(tag_counts.most_common()),
        "fail_reason_counts": dict(fail_counts.most_common()),
        "feature_ranges": ranges,
    }


def passes_rule(row: dict[str, Any], rule: dict[str, Any]) -> bool:
    for name, op, threshold in rule["clauses"]:
        value = feature(row, name)
        if value is None:
            return False
        if op == ">=" and value < threshold:
            return False
        if op == "<=" and value > threshold:
            return False
    side = rule.get("side")
    if side and str(row.get("side") or "") != side:
        return False
    return True


def find_rules(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    clauses = []
    for threshold in (0.10, 0.20, 0.30, 0.40, 0.50):
        clauses.append(("ask_prob", ">=", threshold))
    for threshold in (0.10, 0.20, 0.30, 0.40, 0.50, 0.60, 0.70):
        clauses.append(("abs_d_sigma", ">=", threshold))
    for threshold in (0.20, 0.30, 0.40, 0.50, 0.60, 0.70):
        clauses.append(("recross_hazard_score", "<=", threshold))
    for threshold in (0.05, 0.10, 0.15, 0.20, 0.30):
        clauses.append(("raw_edge", ">=", threshold))

    rules: list[dict[str, Any]] = []
    for size in (1, 2, 3):
        for combo in itertools.combinations(clauses, size):
            for side in (None, "yes", "no"):
                rule = {"clauses": list(combo), "side": side}
                selected = [row for row in rows if passes_rule(row, rule)]
                if len(selected) < 5:
                    continue
                summary = summarize_rows(selected)
                if summary["net_cents"] <= 0:
                    continue
                rules.append(
                    {
                        "rule": rule,
                        "summary": summary,
                        "rows": [
                            {
                                "market": row.get("market"),
                                "side": row.get("side"),
                                "source": row.get("source"),
                                "net_cents": row.get("net_cents"),
                                "raw_edge": row.get("raw_edge"),
                                "recross_hazard_score": row.get("recross_hazard_score"),
                                "abs_d_sigma": row.get("abs_d_sigma"),
                                "ask_prob": row.get("ask_prob"),
                                "outcome": row.get("outcome"),
                                "mechanism_tags": row.get("mechanism_tags"),
                            }
                            for row in selected
                        ],
                    }
                )
    rules.sort(
        key=lambda row: (
            row["summary"]["losses"],
            -row["summary"]["rows"],
            -row["summary"]["net_cents"],
        )
    )
    return rules[:20]


def lane_report(lane: dict[str, Any]) -> dict[str, Any]:
    omitted = list(lane.get("omitted_rows") or [])
    winners = [row for row in omitted if side_won(row)]
    losers = [row for row in omitted if not side_won(row)]
    return {
        "lane": lane.get("lane"),
        "frontier_rule": (lane.get("frontier_rule") or {}).get("rule_name"),
        "frontier_summary": lane.get("frontier_selected_summary"),
        "omitted_summary": summarize_rows(omitted),
        "omitted_winner_summary": summarize_rows(winners),
        "omitted_loser_summary": summarize_rows(losers),
        "best_omitted_addon_rules": find_rules(omitted),
        "top_omitted_winners": sorted(
            [
                {
                    "market": row.get("market"),
                    "side": row.get("side"),
                    "source": row.get("source"),
                    "net_cents": row.get("net_cents"),
                    "raw_edge": row.get("raw_edge"),
                    "recross_hazard_score": row.get("recross_hazard_score"),
                    "abs_d_sigma": row.get("abs_d_sigma"),
                    "ask_prob": row.get("ask_prob"),
                    "mechanism_tags": row.get("mechanism_tags"),
                    "fail_reasons": row.get("fail_reasons"),
                }
                for row in winners
            ],
            key=lambda row: float(row.get("net_cents") or 0.0),
            reverse=True,
        )[:10],
        "worst_omitted_losers": sorted(
            [
                {
                    "market": row.get("market"),
                    "side": row.get("side"),
                    "source": row.get("source"),
                    "net_cents": row.get("net_cents"),
                    "raw_edge": row.get("raw_edge"),
                    "recross_hazard_score": row.get("recross_hazard_score"),
                    "abs_d_sigma": row.get("abs_d_sigma"),
                    "ask_prob": row.get("ask_prob"),
                    "mechanism_tags": row.get("mechanism_tags"),
                    "fail_reasons": row.get("fail_reasons"),
                }
                for row in losers
            ],
            key=lambda row: float(row.get("net_cents") or 0.0),
        )[:10],
    }


def build_report() -> dict[str, Any]:
    payload = load_json(MECH_JSON)
    lanes = [
        lane_report(lane)
        for lane in payload.get("lanes") or []
        if lane.get("lane") in {"post_feature_freeze_entry", "post_feature_freeze_bridge"}
    ]
    notes = [
        "This is diagnostic only; rules are searched on omitted rows and need their own freeze before use.",
    ]
    for lane in lanes:
        omitted = lane["omitted_summary"]
        winners = lane["omitted_winner_summary"]
        losers = lane["omitted_loser_summary"]
        best = (lane.get("best_omitted_addon_rules") or [{}])[0]
        notes.append(
            f"{lane.get('lane')}: omitted {omitted.get('rows')} rows net {omitted.get('net_cents')}c "
            f"with W/L {winners.get('rows')}/{losers.get('rows')}; best diagnostic add-on "
            f"{best.get('rule')} summary {(best.get('summary') or {})}."
        )
    return {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "source": str(MECH_JSON),
        "lanes": lanes,
        "interpretation": notes,
    }


def rule_str(rule: dict[str, Any]) -> str:
    clauses = [f"{name}{op}{threshold}" for name, op, threshold in rule.get("clauses") or []]
    if rule.get("side"):
        clauses.append(f"side={rule['side']}")
    return " & ".join(clauses) or "none"


def write_md(report: dict[str, Any]) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8")
    lines = [
        "# v28 Feature-Gate Ask35 Omitted Split",
        "",
        "Research-only. No live bot logic changes, no process control, no orders.",
        "",
        f"- Generated UTC: `{report.get('generated_at_utc')}`",
        f"- Source: `{report.get('source')}`",
        "",
        "## Interpretation",
        "",
    ]
    for note in report.get("interpretation") or []:
        lines.append(f"- {note}")
    for lane in report.get("lanes") or []:
        lines.extend(["", f"## {lane.get('lane')}", ""])
        for label, summary in [
            ("omitted", lane.get("omitted_summary") or {}),
            ("omitted winners", lane.get("omitted_winner_summary") or {}),
            ("omitted losers", lane.get("omitted_loser_summary") or {}),
        ]:
            lines.append(
                f"- {label}: rows `{summary.get('rows')}`, W/L `{summary.get('wins')}/{summary.get('losses')}`, "
                f"net `{summary.get('net_cents')}c`, side counts `{summary.get('side_counts')}`, fail reasons `{summary.get('fail_reason_counts')}`"
            )
        lines.extend(["", "### Best Diagnostic Add-On Rules", ""])
        lines.append("| rule | rows | W/L | net c | avg c | side counts | feature ranges |")
        lines.append("|---|---:|---:|---:|---:|---|---|")
        for row in lane.get("best_omitted_addon_rules") or []:
            summary = row.get("summary") or {}
            lines.append(
                f"| `{rule_str(row.get('rule') or {})}` | {summary.get('rows')} | "
                f"{summary.get('wins')}/{summary.get('losses')} | {summary.get('net_cents')} | "
                f"{summary.get('avg_net_cents')} | `{summary.get('side_counts')}` | `{summary.get('feature_ranges')}` |"
            )
        lines.extend(["", "### Top Omitted Winners", ""])
        lines.append("| market | side | net c | edge | recross | abs d | ask | tags |")
        lines.append("|---|---|---:|---:|---:|---:|---:|---|")
        for row in lane.get("top_omitted_winners") or []:
            lines.append(
                f"| `{row.get('market')}` | `{row.get('side')}` | {row.get('net_cents')} | "
                f"{row.get('raw_edge')} | {row.get('recross_hazard_score')} | {row.get('abs_d_sigma')} | "
                f"{row.get('ask_prob')} | `{row.get('mechanism_tags')}` |"
            )
        lines.extend(["", "### Worst Omitted Losers", ""])
        lines.append("| market | side | net c | edge | recross | abs d | ask | tags |")
        lines.append("|---|---|---:|---:|---:|---:|---:|---|")
        for row in lane.get("worst_omitted_losers") or []:
            lines.append(
                f"| `{row.get('market')}` | `{row.get('side')}` | {row.get('net_cents')} | "
                f"{row.get('raw_edge')} | {row.get('recross_hazard_score')} | {row.get('abs_d_sigma')} | "
                f"{row.get('ask_prob')} | `{row.get('mechanism_tags')}` |"
            )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    report = build_report()
    write_md(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
