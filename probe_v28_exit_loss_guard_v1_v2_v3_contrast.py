"""Contrast v28 book-gap loss-guard v1/v2/v3 row by row.

Research-only; no live bot changes or orders.

V3 is a narrow relaxation of V2 intended to keep extreme p_hold value-exit
winner recovery while still rejecting lower-confidence rich-exit/negative-gap
holds. This report compares all three frozen rules on identical windows.
"""
from __future__ import annotations

import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from probe_v28_exit_book_gap_candidates import hold_book_gap
from probe_v28_exit_policy_candidates import (
    build_rows,
    current_exit,
    exit_fair_drawdown,
    exit_p_hold,
    exit_reason,
    hold_to_settlement,
    side_won,
)
from probe_v28_exit_policy_common_clock_watch import exit_price_cents, parse_ts, suppression_tags
from probe_v28_frozen_exit_book_gap_loss_guard import (
    STATE_JSON as V1_STATE_JSON,
    load_json,
    should_suppress as v1_should_suppress,
)
from probe_v28_frozen_exit_book_gap_loss_guard_v2 import (
    STATE_JSON as V2_STATE_JSON,
    should_suppress as v2_should_suppress,
)
from probe_v28_frozen_exit_book_gap_loss_guard_v3 import (
    STATE_JSON as V3_STATE_JSON,
    should_suppress as v3_should_suppress,
)


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
OUT_JSON = OUT_DIR / "v28_exit_loss_guard_v1_v2_v3_contrast_latest.json"
OUT_MD = OUT_DIR / "v28_exit_loss_guard_v1_v2_v3_contrast_latest.md"

BOOK_GAP_FREEZE = "2026-05-06T08:46:39.207330+00:00"


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def row_ts(row: dict[str, Any]) -> datetime | None:
    return parse_ts(row.get("exit_ts") or row.get("entry_ts"))


def build_scored_rows() -> list[dict[str, Any]]:
    rows = []
    for row in build_rows():
        if current_exit(row) is None or hold_to_settlement(row) is None:
            continue
        rows.append(row)
    return rows


def filter_snapshot(rows: list[dict[str, Any]], freeze_ts: str | None) -> list[dict[str, Any]]:
    freeze_dt = parse_ts(freeze_ts)
    out = []
    for row in rows:
        ts = row_ts(row)
        if freeze_dt is not None and ts is not None and ts < freeze_dt:
            continue
        out.append(row)
    return out


def cents(value: Any) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def policy_bits(row: dict[str, Any], v1_state: dict[str, Any], v2_state: dict[str, Any], v3_state: dict[str, Any]) -> tuple[bool, bool, bool]:
    return (
        v1_should_suppress(row, v1_state),
        v2_should_suppress(row, v2_state),
        v3_should_suppress(row, v3_state),
    )


def label_for(bits: tuple[bool, bool, bool]) -> str:
    v1, v2, v3 = bits
    if v1 and v2 and v3:
        return "all_three"
    if v1 and v3 and not v2:
        return "v1_v3_only"
    if v1 and not v2 and not v3:
        return "v1_only"
    if v2 and v3 and not v1:
        return "v2_v3_only"
    if v2 and not v1 and not v3:
        return "v2_only"
    if v3 and not v1 and not v2:
        return "v3_only"
    return "none"


def compact(row: dict[str, Any], label: str, bits: tuple[bool, bool, bool]) -> dict[str, Any]:
    delta = cents(hold_to_settlement(row)) - cents(current_exit(row))
    return {
        "market": row.get("market"),
        "side": row.get("side"),
        "result": row.get("result"),
        "classification": label,
        "v1_v2_v3": bits,
        "entry_ts": row.get("entry_ts"),
        "exit_ts": row.get("exit_ts"),
        "exit_reason": exit_reason(row),
        "p_hold": exit_p_hold(row),
        "hold_book_gap": hold_book_gap(row),
        "fair_drawdown_cents": exit_fair_drawdown(row),
        "exit_price_cents": exit_price_cents(row),
        "current_cents": current_exit(row),
        "hold_cents": hold_to_settlement(row),
        "delta_if_suppressed_cents": delta,
        "side_won": side_won(row),
        "tags": suppression_tags(row),
    }


def summarize(rows: list[dict[str, Any]], v1_state: dict[str, Any], v2_state: dict[str, Any], v3_state: dict[str, Any]) -> dict[str, Any]:
    buckets: dict[str, list[dict[str, Any]]] = {
        "all_three": [],
        "v1_v3_only": [],
        "v1_only": [],
        "v2_v3_only": [],
        "v2_only": [],
        "v3_only": [],
        "none": [],
    }
    tag_counts: dict[str, Counter[str]] = {key: Counter() for key in buckets}
    reason_counts: dict[str, Counter[str]] = {key: Counter() for key in buckets}
    examples: dict[str, list[dict[str, Any]]] = {key: [] for key in buckets}
    for row in rows:
        bits = policy_bits(row, v1_state, v2_state, v3_state)
        label = label_for(bits)
        buckets[label].append(row)
        for tag in suppression_tags(row):
            tag_counts[label][tag] += 1
        reason_counts[label][exit_reason(row)] += 1
        if label != "none":
            examples[label].append(compact(row, label, bits))

    def bucket_summary(label: str) -> dict[str, Any]:
        selected = buckets[label]
        deltas = [cents(hold_to_settlement(row)) - cents(current_exit(row)) for row in selected]
        helpful = [delta for row, delta in zip(selected, deltas) if side_won(row) is True]
        harmful = [delta for row, delta in zip(selected, deltas) if side_won(row) is False]
        return {
            "rows": len(selected),
            "net_delta_cents": sum(deltas),
            "helpful_rows": len(helpful),
            "harmful_rows": len(harmful),
            "helpful_delta_cents": sum(helpful),
            "harmful_delta_cents": sum(harmful),
            "top_tags": dict(tag_counts[label].most_common(10)),
            "exit_reasons": dict(reason_counts[label].most_common()),
            "examples": sorted(
                examples[label],
                key=lambda item: cents(item.get("delta_if_suppressed_cents")),
            )[:12],
        }

    return {
        "rows": len(rows),
        "current_gross_cents": sum(cents(current_exit(row)) for row in rows),
        "buckets": {label: bucket_summary(label) for label in buckets},
    }


def build_report() -> dict[str, Any]:
    v1_state = load_json(V1_STATE_JSON)
    v2_state = load_json(V2_STATE_JSON)
    v3_state = load_json(V3_STATE_JSON)
    scored_rows = build_scored_rows()
    windows = {
        "all_exit_rows_diagnostic": None,
        "book_gap_freeze_comparable": BOOK_GAP_FREEZE,
        "v1_strict_forward": v1_state.get("freeze_ts_utc"),
        "v2_strict_forward": v2_state.get("freeze_ts_utc"),
        "v3_strict_forward": v3_state.get("freeze_ts_utc"),
    }
    report = {
        "generated_at_utc": utc_now_iso(),
        "v1_freeze_ts_utc": v1_state.get("freeze_ts_utc"),
        "v2_freeze_ts_utc": v2_state.get("freeze_ts_utc"),
        "v3_freeze_ts_utc": v3_state.get("freeze_ts_utc"),
        "base_scored_row_count": len(scored_rows),
        "windows": [
            {
                "window": name,
                "freeze_ts_utc": freeze_ts,
                **summarize(filter_snapshot(scored_rows, freeze_ts), v1_state, v2_state, v3_state),
            }
            for name, freeze_ts in windows.items()
        ],
        "interpretation": [
            "v1_v3_only is the intended V3 recovery bucket: V3 keeps rows that v2 rejects, but only when the extreme-p rule passes.",
            "v1_only is the lower-confidence risk bucket that V3 continues to reject.",
            "Only v3_strict_forward is strict evidence for V3; older windows are diagnostic/comparable only.",
        ],
    }
    return report


def money(value: Any) -> str:
    number = cents(value)
    return f"{number:.0f}c (${number / 100.0:.2f})"


def write_md(report: dict[str, Any]) -> None:
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8")
    lines = [
        "# v28 Exit Loss-Guard V1/V2/V3 Contrast",
        "",
        "Research-only; no live bot changes or orders.",
        "",
        f"- Generated UTC: `{report.get('generated_at_utc')}`",
        f"- V1 freeze UTC: `{report.get('v1_freeze_ts_utc')}`",
        f"- V2 freeze UTC: `{report.get('v2_freeze_ts_utc')}`",
        f"- V3 freeze UTC: `{report.get('v3_freeze_ts_utc')}`",
        "",
        "## Interpretation",
        "",
    ]
    lines.extend(f"- {note}" for note in report.get("interpretation") or [])
    for window in report.get("windows") or []:
        lines.extend([
            "",
            f"## {window.get('window')}",
            "",
            f"- Freeze UTC: `{window.get('freeze_ts_utc')}`",
            f"- Rows: `{window.get('rows')}`",
            f"- Current gross: `{money(window.get('current_gross_cents'))}`",
            "",
            "| bucket | rows | net delta | helpful | harmful | helpful delta | harmful delta | top tags |",
            "|---|---:|---:|---:|---:|---:|---:|---|",
        ])
        for label, bucket in (window.get("buckets") or {}).items():
            if label == "none" and not bucket.get("rows"):
                continue
            top_tags = ", ".join(f"{tag}:{count}" for tag, count in list((bucket.get("top_tags") or {}).items())[:5])
            lines.append(
                f"| `{label}` | {bucket.get('rows')} | {money(bucket.get('net_delta_cents'))} | "
                f"{bucket.get('helpful_rows')} | {bucket.get('harmful_rows')} | "
                f"{money(bucket.get('helpful_delta_cents'))} | {money(bucket.get('harmful_delta_cents'))} | {top_tags or 'none'} |"
            )
        for section, title in [("v1_v3_only", "V1/V3-Only Examples"), ("v1_only", "V1-Only Rejected By V3 Examples")]:
            examples = ((window.get("buckets") or {}).get(section) or {}).get("examples") or []
            if not examples:
                continue
            lines.extend([
                "",
                f"### {title}",
                "",
                "| market | side/result | reason | p_hold | gap | drawdown | exit | delta | tags |",
                "|---|---|---|---:|---:|---:|---:|---:|---|",
            ])
            for row in examples[:8]:
                lines.append(
                    f"| {row.get('market')} | {row.get('side')}/{row.get('result')} | {row.get('exit_reason')} | "
                    f"{row.get('p_hold')} | {row.get('hold_book_gap')} | {row.get('fair_drawdown_cents')} | "
                    f"{row.get('exit_price_cents')} | {money(row.get('delta_if_suppressed_cents'))} | "
                    f"{', '.join(row.get('tags') or [])} |"
                )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    report = build_report()
    write_md(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
