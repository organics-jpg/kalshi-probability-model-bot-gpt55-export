"""Source and physics audit for the broad book-edge entry lane.

Research-only; no live bot changes or orders.

This report is diagnostic, not promotion evidence. It explains whether the
current broad book-edge discovery row is supported by actual approved entries
or mostly by rejected-actionable shadow rows.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Callable


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
BAKEOFF_JSON = OUT_DIR / "v28_shadow_entry_policy_bakeoff_latest.json"
FROZEN_JSON = OUT_DIR / "v28_frozen_book_plus05_no_cheap_yes_entry_latest.json"
OUT_JSON = OUT_DIR / "v28_broad_book_edge_source_audit_latest.json"
OUT_MD = OUT_DIR / "v28_broad_book_edge_source_audit_latest.md"

POLICY = "book_plus_05_no_cheap_yes_boundary"
MAX_SIM_SHARE = 0.35
MIN_APPROVED_SETTLED = 30


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


def selected_rows() -> list[dict[str, Any]]:
    payload = load_json(BAKEOFF_JSON)
    rows = payload.get("rows") if isinstance(payload.get("rows"), list) else []
    return [row for row in rows if row.get("policy") == POLICY]


def summarize(rows: list[dict[str, Any]]) -> dict[str, Any]:
    settled = [row for row in rows if row.get("side_won") is not None]
    gross = sum(float(row.get("gross_cents") or 0.0) for row in settled)
    return {
        "entries": len(rows),
        "settled": len(settled),
        "wins": sum(1 for row in settled if row.get("side_won") is True),
        "losses": sum(1 for row in settled if row.get("side_won") is False),
        "gross_cents": gross,
        "avg_gross_cents": gross / len(settled) if settled else None,
    }


def bucket(name: str, rows: list[dict[str, Any]], predicate: Callable[[dict[str, Any]], bool]) -> dict[str, Any]:
    picked = [row for row in rows if predicate(row)]
    return {"bucket": name, **summarize(picked)}


def build_report() -> dict[str, Any]:
    rows = selected_rows()
    approved = [row for row in rows if row.get("source") == "approved_entry"]
    rejected = [row for row in rows if row.get("source") == "rejected_actionable"]
    sim_share = len(rejected) / len(rows) if rows else None
    source_rows = [
        {"source": "approved_entry", **summarize(approved)},
        {"source": "rejected_actionable", **summarize(rejected)},
    ]
    physics_rows = [
        bucket("high_conf_p65_plus", rows, lambda row: (as_float(row.get("p_side")) or 0.0) >= 0.65),
        bucket("mid_conf_45_65", rows, lambda row: 0.45 <= (as_float(row.get("p_side")) or -1.0) < 0.65),
        bucket("yes_side", rows, lambda row: str(row.get("side") or "").lower() == "yes"),
        bucket("no_side", rows, lambda row: str(row.get("side") or "").lower() == "no"),
        bucket("high_recross_075_plus", rows, lambda row: (as_float(row.get("recross_hazard_score")) or 0.0) >= 0.75),
        bucket("near_strike_sigma_lt025", rows, lambda row: (as_float(row.get("abs_d_sigma")) or 999.0) < 0.25),
    ]
    blockers = []
    if sim_share is None or sim_share > MAX_SIM_SHARE:
        blockers.append("simulated_share_gt_35pct")
    if len([row for row in approved if row.get("side_won") is not None]) < MIN_APPROVED_SETTLED:
        blockers.append("approved_settled_lt_30")
    frozen = load_json(FROZEN_JSON)
    frozen_summary = frozen.get("summary") or {}
    if int(as_float(frozen_summary.get("settled")) or 0) < MIN_APPROVED_SETTLED:
        blockers.append("frozen_forward_settled_lt_30")
    return {
        "policy": POLICY,
        "summary": summarize(rows),
        "source_rows": source_rows,
        "physics_rows": physics_rows,
        "simulated_share": sim_share,
        "blockers": blockers,
        "diagnostic_supported": not blockers,
        "frozen_summary": frozen_summary,
        "interpretation": [
            f"{POLICY} is the current best broad discovery lane, but promotion depends on future rows and source balance.",
            f"Actual-approved rows are {source_rows[0]['settled']} settled for {source_rows[0]['gross_cents']}c; rejected-actionable rows are {source_rows[1]['settled']} settled for {source_rows[1]['gross_cents']}c.",
            f"Simulated/rejected share is {sim_share}; blocker threshold is {MAX_SIM_SHARE}.",
            f"Frozen future settled rows are {frozen_summary.get('settled')}; discovery evidence is not enough.",
        ],
    }


def fmt(value: Any) -> str:
    if value is None:
        return "None"
    if isinstance(value, float):
        return f"{value:.6f}"
    return str(value)


def write_md(report: dict[str, Any]) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8")
    summary = report.get("summary") or {}
    lines = [
        "# v28 Broad Book-Edge Source Audit",
        "",
        "Diagnostic-only audit for the current broad book-edge lane. No live orders.",
        "",
        f"- Policy: `{report.get('policy')}`",
        f"- Diagnostic supported: `{report.get('diagnostic_supported')}`",
        f"- Entries/settled/W-L: `{summary.get('entries')}/{summary.get('settled')}/{summary.get('wins')}-{summary.get('losses')}`",
        f"- Gross / avg gross: `{fmt(summary.get('gross_cents'))}/{fmt(summary.get('avg_gross_cents'))}`",
        f"- Simulated share: `{fmt(report.get('simulated_share'))}`",
        f"- Blockers: `{', '.join(report.get('blockers') or []) or 'none'}`",
        "",
        "## Interpretation",
        "",
    ]
    for note in report.get("interpretation") or []:
        lines.append(f"- {note}")
    lines.extend([
        "",
        "## Source Rows",
        "",
        "| source | entries | settled | W-L | gross c | avg c |",
        "|---|---:|---:|---:|---:|---:|",
    ])
    for row in report.get("source_rows") or []:
        lines.append(
            f"| {row.get('source')} | {row.get('entries')} | {row.get('settled')} | "
            f"{row.get('wins')}-{row.get('losses')} | {fmt(row.get('gross_cents'))} | {fmt(row.get('avg_gross_cents'))} |"
        )
    lines.extend([
        "",
        "## Physics Rows",
        "",
        "| bucket | entries | settled | W-L | gross c | avg c |",
        "|---|---:|---:|---:|---:|---:|",
    ])
    for row in report.get("physics_rows") or []:
        lines.append(
            f"| {row.get('bucket')} | {row.get('entries')} | {row.get('settled')} | "
            f"{row.get('wins')}-{row.get('losses')} | {fmt(row.get('gross_cents'))} | {fmt(row.get('avg_gross_cents'))} |"
        )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    report = build_report()
    write_md(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
