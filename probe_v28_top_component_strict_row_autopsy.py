"""Autopsy of strict post-birth rows for the v28 top-component branch.

Research-only. This classifies the actual strict forward rows behind the
top-component portfolio so the branch is not judged from diagnostic PnL alone.
"""
from __future__ import annotations

import json
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
OUT_JSON = OUT_DIR / "v28_top_component_strict_row_autopsy_latest.json"
OUT_MD = OUT_DIR / "v28_top_component_strict_row_autopsy_latest.md"

MIX = OUT_DIR / "v28_top_component_mix_portfolio_latest.json"
CHILD = OUT_DIR / "v28_top_component_parent_fill_repair_child_latest.json"
GATE = OUT_DIR / "v28_top_component_strict_gate_audit_latest.json"


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


def cents(value: Any) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def fmt_cents(value: Any) -> str:
    return f"{cents(value):.0f}c"


def fmt_num(value: Any, digits: int = 3) -> str:
    try:
        return f"{float(value):.{digits}f}"
    except (TypeError, ValueError):
        return "n/a"


def row_key(row: dict[str, Any]) -> tuple[str, str, str, str]:
    return (
        str(row.get("market") or ""),
        str(row.get("side") or ""),
        str(row.get("source") or ""),
        str(row.get("component") or ""),
    )


def row_pnl(row: dict[str, Any]) -> float:
    for key in ("selected_weighted_cents", "final_weighted_cents", "weighted_net_cents", "net_cents"):
        if row.get(key) is not None:
            return cents(row.get(key))
    return 0.0


def classify(row: dict[str, Any]) -> list[str]:
    tags: list[str] = []
    if row.get("component") == "strict_parent_midprice_hold_fill":
        tags.append("parent_fill_no_exit_clock")
    if row.get("source") != "approved_entry":
        tags.append("source_quality_error")

    pnl = row_pnl(row)
    won = bool(row.get("side_won"))
    if pnl < 0 or not won:
        tags.append("fv_or_entry_error")
        ask = row.get("ask_prob")
        abs_d = row.get("abs_d_sigma")
        recross = row.get("recross_hazard_score")
        raw = row.get("raw_edge")
        if ask is not None and float(ask) < 0.65:
            tags.append("low_or_mid_ask_touch")
        if abs_d is not None and float(abs_d) < 0.85:
            tags.append("weak_boundary_distance")
        if recross is not None and float(recross) > 0.30:
            tags.append("moderate_recross")
        if raw is not None and float(raw) > 0.20:
            tags.append("large_raw_edge_false_positive")
    else:
        tags.append("strict_forward_winner")

    return tags


def collect_rows(mix: dict[str, Any], child: dict[str, Any]) -> list[dict[str, Any]]:
    rows_by_key: dict[tuple[str, str, str, str], dict[str, Any]] = {}

    for variant in mix.get("strict_variants", []):
        if not isinstance(variant, dict):
            continue
        for row in variant.get("rows", []) or []:
            if not isinstance(row, dict):
                continue
            key = row_key(row)
            record = rows_by_key.setdefault(
                key,
                {
                    "market": row.get("market"),
                    "side": row.get("side"),
                    "source": row.get("source"),
                    "component": row.get("component"),
                    "pnl_cents": row_pnl(row),
                    "side_won": row.get("side_won"),
                    "raw_edge": row.get("raw_edge"),
                    "recross_hazard_score": row.get("recross_hazard_score"),
                    "abs_d_sigma": row.get("abs_d_sigma"),
                    "ask_prob": row.get("ask_prob"),
                    "variant_labels": [],
                },
            )
            record["variant_labels"].append(variant.get("label"))

    for variant in child.get("strict_variants", []):
        if not isinstance(variant, dict):
            continue
        for row in variant.get("worst_rows", []) or []:
            if not isinstance(row, dict):
                continue
            key = row_key(row)
            record = rows_by_key.setdefault(
                key,
                {
                    "market": row.get("market"),
                    "side": row.get("side"),
                    "source": row.get("source"),
                    "component": row.get("component"),
                    "pnl_cents": row_pnl(row),
                    "side_won": row.get("side_won"),
                    "raw_edge": row.get("raw_edge"),
                    "recross_hazard_score": row.get("recross_hazard_score"),
                    "abs_d_sigma": row.get("abs_d_sigma"),
                    "ask_prob": row.get("ask_prob"),
                    "variant_labels": [],
                },
            )
            record["variant_labels"].append(variant.get("label"))

    autopsy_rows = []
    for record in rows_by_key.values():
        labels = sorted(set(str(label) for label in record.get("variant_labels", []) if label))
        record["variant_labels"] = labels
        record["failure_tags"] = classify(record)
        autopsy_rows.append(record)

    autopsy_rows.sort(key=lambda row: (cents(row.get("pnl_cents")), str(row.get("market"))))
    return autopsy_rows


def build_report() -> dict[str, Any]:
    mix = load_json(MIX)
    child = load_json(CHILD)
    gate = load_json(GATE)
    rows = collect_rows(mix, child)

    tag_counts: Counter[str] = Counter()
    source_counts: Counter[str] = Counter()
    component_counts: Counter[str] = Counter()
    source_net: defaultdict[str, float] = defaultdict(float)
    for row in rows:
        for tag in row.get("failure_tags") or []:
            tag_counts[str(tag)] += 1
        source = str(row.get("source") or "")
        component = str(row.get("component") or "")
        source_counts[source] += 1
        component_counts[component] += 1
        source_net[source] += cents(row.get("pnl_cents"))

    loss_rows = [row for row in rows if cents(row.get("pnl_cents")) < 0]
    win_rows = [row for row in rows if cents(row.get("pnl_cents")) > 0]

    interpretation = [
        "Research-only strict-row autopsy; no live bot changes or orders.",
        f"Strict sample is only {len(rows)} unique rows, so this is failure classification, not promotion evidence.",
        "All observed strict rows are parent-fill rows without exit-clock joins; the exit-rescue component has not been forward-proven here.",
        f"Losses are {len(loss_rows)} rows for {fmt_cents(sum(cents(row.get('pnl_cents')) for row in loss_rows))}; wins are {len(win_rows)} rows for {fmt_cents(sum(cents(row.get('pnl_cents')) for row in win_rows))}.",
        "The current strict failures point to source-quality plus FV/entry false positives, not a reason to broaden parent-fill exposure.",
    ]

    return {
        "generated_at_utc": utc_now_iso(),
        "sources": {
            "mix_portfolio": str(MIX),
            "parent_fill_child": str(CHILD),
            "strict_gate": str(GATE),
        },
        "gate_live_net_cents": gate.get("live_net_cents"),
        "promotion_gate_pass_count": gate.get("promotion_gate_pass_count"),
        "strict_unique_rows": len(rows),
        "strict_loss_rows": len(loss_rows),
        "strict_win_rows": len(win_rows),
        "strict_net_cents": sum(cents(row.get("pnl_cents")) for row in rows),
        "tag_counts": dict(tag_counts),
        "source_counts": dict(source_counts),
        "component_counts": dict(component_counts),
        "source_net_cents": dict(source_net),
        "rows": rows,
        "interpretation": interpretation,
    }


def write_markdown(report: dict[str, Any]) -> None:
    lines = [
        "# v28 Top-Component Strict Row Autopsy",
        "",
        "Research-only. No live bot logic changes, no orders, no process control.",
        "",
        f"- Generated UTC: `{report.get('generated_at_utc')}`",
        f"- Strict unique rows: `{report.get('strict_unique_rows')}`",
        f"- Strict net: `{fmt_cents(report.get('strict_net_cents'))}`",
        f"- Promotion gate passes: `{report.get('promotion_gate_pass_count')}`",
        "",
        "## Interpretation",
        "",
    ]
    lines.extend(f"- {note}" for note in report.get("interpretation") or [])

    lines.extend(
        [
            "",
            "## Failure Tags",
            "",
            "| tag | rows |",
            "|---|---:|",
        ]
    )
    for tag, count in sorted((report.get("tag_counts") or {}).items(), key=lambda item: (-item[1], item[0])):
        lines.append(f"| `{tag}` | {count} |")

    lines.extend(
        [
            "",
            "## Source Net",
            "",
            "| source | rows | net |",
            "|---|---:|---:|",
        ]
    )
    source_counts = report.get("source_counts") or {}
    source_net = report.get("source_net_cents") or {}
    for source, count in sorted(source_counts.items()):
        lines.append(f"| `{source}` | {count} | {fmt_cents(source_net.get(source))} |")

    lines.extend(
        [
            "",
            "## Strict Rows",
            "",
            "| market | side | source | pnl | won | raw edge | recross | abs d | ask | tags |",
            "|---|---|---|---:|---|---:|---:|---:|---:|---|",
        ]
    )
    for row in report.get("rows") or []:
        tags = ", ".join(str(tag) for tag in row.get("failure_tags") or [])
        lines.append(
            "| "
            f"`{row.get('market')}` | "
            f"`{row.get('side')}` | "
            f"`{row.get('source')}` | "
            f"{fmt_cents(row.get('pnl_cents'))} | "
            f"{row.get('side_won')} | "
            f"{fmt_num(row.get('raw_edge'))} | "
            f"{fmt_num(row.get('recross_hazard_score'))} | "
            f"{fmt_num(row.get('abs_d_sigma'))} | "
            f"{fmt_num(row.get('ask_prob'))} | "
            f"{tags} |"
        )

    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    report = build_report()
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
    write_markdown(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
