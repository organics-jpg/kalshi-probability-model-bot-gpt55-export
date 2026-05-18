"""Suppressed-loser audit for the value/reduce-depth exit composite.

Research-only; no live bot changes or orders.

The value/reduce-depth composite is a strong diagnostic loss-count reducer, but
promotion is blocked whenever suppressed losers are present. This audit keeps
the exact loser rows and their physical features in a small report so future
children can target the real failure mode instead of broadening exit holds.
"""
from __future__ import annotations

import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
SOURCE_JSON = OUT_DIR / "v28_frozen_exit_value_reduce_depth_composite_latest.json"
OUT_JSON = OUT_DIR / "v28_exit_value_reduce_depth_suppressed_loser_audit_latest.json"
OUT_MD = OUT_DIR / "v28_exit_value_reduce_depth_suppressed_loser_audit_latest.md"


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


def physical_tags(row: dict[str, Any]) -> list[str]:
    tags = []
    reason = str(row.get("exit_reason") or "")
    p_hold = fnum(row.get("p_hold"))
    gap = fnum(row.get("hold_book_gap"))
    drawdown = fnum(row.get("fair_drawdown_cents"))
    depth = fnum(row.get("entry_depth"))
    current = fnum(row.get("current_cents"))
    if "probability_reduce" in reason:
        tags.append("probability_reduce")
    if "value_over_hold" in reason:
        tags.append("value_over_hold")
    if p_hold < 0.79:
        tags.append("p_hold_below_079")
    if 0.75 <= p_hold < 0.79:
        tags.append("p_hold_075_079")
    if gap > 0.0:
        tags.append("positive_book_gap")
    if drawdown > 0.0:
        tags.append("positive_fair_drawdown")
    if depth <= 50.0:
        tags.append("very_shallow_entry_depth")
    if current < 0.0:
        tags.append("already_negative_exit")
    if current >= 0.0:
        tags.append("not_yet_negative_exit")
    return tags


def loser_rows(payload: dict[str, Any]) -> list[dict[str, Any]]:
    out = []
    for lane in payload.get("lanes") or []:
        if not isinstance(lane, dict):
            continue
        lane_name = lane.get("lane")
        for variant in lane.get("variants") or []:
            if not isinstance(variant, dict):
                continue
            summary = variant.get("summary") or {}
            for row in variant.get("suppressed_rows") or []:
                if not isinstance(row, dict) or row.get("side_won") is not False:
                    continue
                enriched = {
                    "lane": lane_name,
                    "rule": variant.get("rule"),
                    "market": row.get("market"),
                    "side": row.get("side"),
                    "result": row.get("result"),
                    "exit_reason": row.get("exit_reason"),
                    "entry_depth": row.get("entry_depth"),
                    "p_hold": row.get("p_hold"),
                    "hold_book_gap": row.get("hold_book_gap"),
                    "fair_drawdown_cents": row.get("fair_drawdown_cents"),
                    "current_cents": row.get("current_cents"),
                    "hold_cents": row.get("hold_cents"),
                    "delta_cents": row.get("delta_cents"),
                    "worst_post_exit_hold_mark_cents": row.get("worst_post_exit_hold_mark_cents"),
                    "variant_candidate_gross_cents": summary.get("candidate_gross_cents"),
                    "variant_delta_vs_current_cents": summary.get("delta_vs_current_cents"),
                    "variant_suppressed_exits": summary.get("suppressed_exits"),
                    "variant_suppressed_winners": summary.get("suppressed_winners"),
                    "variant_suppressed_losers": summary.get("suppressed_losers"),
                }
                enriched["tags"] = physical_tags(enriched)
                out.append(enriched)
    out.sort(key=lambda row: (str(row.get("lane")), str(row.get("rule")), str(row.get("market"))))
    return out


def build_report() -> dict[str, Any]:
    source = load_json(SOURCE_JSON)
    rows = loser_rows(source)
    post_rows = [row for row in rows if row.get("lane") == "post_composite_birth"]
    diagnostic_rows = [row for row in rows if row.get("lane") == "diagnostic_from_exit_freezes"]
    tag_counts = Counter(tag for row in rows for tag in row.get("tags") or [])
    market_counts = Counter(str(row.get("market")) for row in rows)
    interpretation = [
        "Research-only audit; no live bot changes or orders.",
        "Suppressed losers are the active blocker for the looser value/reduce-depth composite variants.",
    ]
    if post_rows:
        interpretation.append(
            "Post-birth suppressed loser row(s) exist; do not promote p75 reduce-depth variants until a child avoids them."
        )
    else:
        interpretation.append("No post-birth suppressed loser rows are present in the current artifact.")
    if market_counts:
        top_market, top_count = market_counts.most_common(1)[0]
        interpretation.append(f"Most repeated suppressed-loser market is {top_market} across {top_count} variant/lane hits.")
    return {
        "generated_at_utc": utc_now_iso(),
        "source": str(SOURCE_JSON),
        "composite_generated_at_utc": source.get("generated_at_utc"),
        "composite_freeze_ts_utc": (source.get("freeze") or {}).get("freeze_ts_utc"),
        "total_suppressed_loser_hits": len(rows),
        "diagnostic_suppressed_loser_hits": len(diagnostic_rows),
        "post_birth_suppressed_loser_hits": len(post_rows),
        "unique_suppressed_loser_markets": len(market_counts),
        "tag_counts": dict(tag_counts),
        "market_counts": dict(market_counts),
        "rows": rows,
        "interpretation": interpretation,
    }


def fmt(value: Any) -> str:
    if value is None:
        return "n/a"
    if isinstance(value, float):
        return f"{value:.6f}"
    return str(value)


def write_md(report: dict[str, Any]) -> None:
    lines = [
        "# v28 Exit Value/Reduce-Depth Suppressed-Loser Audit",
        "",
        "Research-only. No live bot logic changes, no orders, no process control.",
        "",
        f"- Generated UTC: `{report.get('generated_at_utc')}`",
        f"- Composite generated UTC: `{report.get('composite_generated_at_utc')}`",
        f"- Composite freeze UTC: `{report.get('composite_freeze_ts_utc')}`",
        f"- Total suppressed-loser hits: `{report.get('total_suppressed_loser_hits')}`",
        f"- Post-birth suppressed-loser hits: `{report.get('post_birth_suppressed_loser_hits')}`",
        f"- Unique suppressed-loser markets: `{report.get('unique_suppressed_loser_markets')}`",
        "",
        "## Interpretation",
        "",
    ]
    lines.extend(f"- {note}" for note in report.get("interpretation") or [])
    lines.extend(
        [
            "",
            "## Tag Counts",
            "",
            "| tag | hits |",
            "|---|---:|",
        ]
    )
    for tag, count in sorted((report.get("tag_counts") or {}).items(), key=lambda item: (-int(item[1]), item[0])):
        lines.append(f"| `{tag}` | {count} |")
    lines.extend(
        [
            "",
            "## Suppressed Loser Rows",
            "",
            "| lane | rule | market | side | reason | current | hold | delta | p_hold | gap | drawdown | depth | worst mark | tags |",
            "|---|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---|",
        ]
    )
    for row in report.get("rows") or []:
        lines.append(
            f"| `{row.get('lane')}` | `{row.get('rule')}` | `{row.get('market')}` | `{row.get('side')}` | "
            f"`{row.get('exit_reason')}` | {fmt(row.get('current_cents'))} | {fmt(row.get('hold_cents'))} | "
            f"{fmt(row.get('delta_cents'))} | {fmt(row.get('p_hold'))} | {fmt(row.get('hold_book_gap'))} | "
            f"{fmt(row.get('fair_drawdown_cents'))} | {fmt(row.get('entry_depth'))} | "
            f"{fmt(row.get('worst_post_exit_hold_mark_cents'))} | {', '.join(row.get('tags') or [])} |"
        )
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    report = build_report()
    write_md(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
