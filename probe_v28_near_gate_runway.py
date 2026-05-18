"""Near-gate runway audit for v28 candidate families.

Research-only; no live bot changes or orders.

This report takes the consolidated candidate tracker and ranks rows by how close
they are to promotion gates. It is deliberately gate-first rather than PnL-first
so diagnostic green rows do not masquerade as live candidates.
"""
from __future__ import annotations

import json
import math
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
TRACKER_JSON = OUT_DIR / "v28_candidate_pnl_tracker_latest.json"
LIVE_SUMMARY_JSON = ROOT / "stats" / "live_mushroom_v28_size2" / "summary.json"
OUT_JSON = OUT_DIR / "v28_near_gate_runway_latest.json"
OUT_MD = OUT_DIR / "v28_near_gate_runway_latest.md"

MIN_SETTLED = 30
MIN_COVERAGE = 75.0
MAX_COVERAGE = 90.0
MAX_SOURCE_SHARE = 0.35
MIN_CUSHION = 3


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


def live_cents() -> float:
    live = load_json(LIVE_SUMMARY_JSON)
    return 100.0 * fnum(live.get("net_pnl_total_dollars"))


def infer_denominator(row: dict[str, Any]) -> int | None:
    explicit = row.get("forward_denominator") or row.get("future_denominator")
    if explicit:
        return int(fnum(explicit))
    entries = int(fnum(row.get("entries")))
    coverage = fnum(row.get("coverage_pct"), math.nan)
    if entries > 0 and math.isfinite(coverage) and coverage > 0:
        return int(round(entries / (coverage / 100.0)))
    return None


def source_share(row: dict[str, Any]) -> float | None:
    share = row.get("simulated_share")
    if share is not None:
        return fnum(share)
    entries = int(fnum(row.get("entries")))
    approved = row.get("approved_entry_count")
    if entries > 0 and approved is not None:
        return max(0.0, (entries - int(fnum(approved))) / entries)
    return None


def source_clean_rows_needed(row: dict[str, Any]) -> int | None:
    entries = int(fnum(row.get("entries")))
    if entries <= 0:
        return None
    approved = row.get("approved_entry_count")
    if approved is not None:
        rejected = max(0, entries - int(fnum(approved)))
    else:
        share = source_share(row)
        if share is None:
            return None
        rejected = int(round(share * entries))
    return max(0, int(math.ceil(rejected / MAX_SOURCE_SHARE - entries)))


def coverage_entries_needed(row: dict[str, Any]) -> int | None:
    entries = int(fnum(row.get("entries")))
    denominator = infer_denominator(row)
    if not denominator:
        return None
    target = int(math.ceil(MIN_COVERAGE / 100.0 * denominator))
    return max(0, target - entries)


def normalized_blockers(row: dict[str, Any], live_net: float) -> list[str]:
    blockers = list(row.get("blockers") or [])
    settled = int(fnum(row.get("settled")))
    net = fnum(row.get("net_cents_after_entry_fee"))
    coverage = row.get("coverage_pct")
    coverage_num = fnum(coverage, math.nan) if coverage is not None else math.nan
    share = source_share(row)
    cushion = int(fnum(row.get("full_loss_cushion_estimate"), math.floor(max(0.0, net) / 100.0)))
    if not row.get("strict_forward"):
        blockers.append("not_strict_forward")
    if settled < MIN_SETTLED:
        blockers.append("settled_lt_30")
    if coverage is None or not math.isfinite(coverage_num) or coverage_num < MIN_COVERAGE:
        blockers.append("coverage_too_low")
    elif coverage_num > MAX_COVERAGE:
        blockers.append("coverage_too_high")
    if share is None or share > MAX_SOURCE_SHARE:
        blockers.append("source_share_gt_35pct")
    if net <= 0:
        blockers.append("net_not_positive")
    if cushion < MIN_CUSHION:
        blockers.append("full_loss_cushion_lt_3")
    if net <= live_net:
        blockers.append("does_not_beat_refreshed_live_baseline")
    if not row.get("live_ready"):
        blockers.append("live_ready_false")
    out: list[str] = []
    seen = set()
    for blocker in blockers:
        if blocker not in seen:
            seen.add(blocker)
            out.append(str(blocker))
    return out


def runway(row: dict[str, Any], live_net: float) -> dict[str, Any]:
    net = fnum(row.get("net_cents_after_entry_fee"))
    settled = int(fnum(row.get("settled")))
    entries = int(fnum(row.get("entries")))
    coverage = row.get("coverage_pct")
    share = source_share(row)
    blockers = normalized_blockers(row, live_net)
    return {
        "gate": row.get("gate"),
        "policy": row.get("policy"),
        "entries": entries,
        "settled": settled,
        "wins": row.get("wins"),
        "losses": row.get("losses"),
        "coverage_pct": coverage,
        "net_cents": net,
        "delta_vs_live_cents": net - live_net,
        "source_share": share,
        "cushion": int(fnum(row.get("full_loss_cushion_estimate"), math.floor(max(0.0, net) / 100.0))),
        "strict_forward": bool(row.get("strict_forward")),
        "live_ready": bool(row.get("live_ready")),
        "target_coverage": bool(row.get("target_coverage")),
        "settled_rows_needed": max(0, MIN_SETTLED - settled),
        "coverage_entries_needed": coverage_entries_needed(row),
        "approved_rows_needed_for_source_gate": source_clean_rows_needed(row),
        "net_cents_needed_to_beat_live": max(0.0, live_net - net + 1.0),
        "net_cents_needed_for_cushion3": max(0.0, MIN_CUSHION * 100.0 - net),
        "blockers": blockers,
        "blocker_count": len(blockers),
    }


def sort_key(row: dict[str, Any]) -> tuple[Any, ...]:
    blockers = set(row.get("blockers") or [])
    hard = len([item for item in blockers if item not in {"live_ready_false"}])
    return (
        hard,
        int(row.get("settled_rows_needed") or 0),
        fnum(row.get("net_cents_needed_to_beat_live")),
        -fnum(row.get("net_cents")),
        str(row.get("gate")),
        str(row.get("policy")),
    )


def build_report() -> dict[str, Any]:
    tracker = load_json(TRACKER_JSON)
    live_net = live_cents()
    rows = [runway(row, live_net) for row in tracker.get("rows") or [] if isinstance(row, dict)]
    positive = [row for row in rows if fnum(row.get("net_cents")) > 0]
    target_positive = [row for row in positive if row.get("target_coverage")]
    strict_positive = [row for row in positive if row.get("strict_forward")]
    strict_target_positive = [row for row in target_positive if row.get("strict_forward")]
    live_ready = [row for row in rows if row.get("live_ready")]
    blocker_counts = Counter(blocker for row in target_positive for blocker in (row.get("blockers") or []))
    return {
        "generated_at_utc": utc_now_iso(),
        "live_baseline_cents": live_net,
        "counts": {
            "rows": len(rows),
            "positive": len(positive),
            "target_positive": len(target_positive),
            "strict_positive": len(strict_positive),
            "strict_target_positive": len(strict_target_positive),
            "live_ready": len(live_ready),
        },
        "top_strict_target_positive": sorted(strict_target_positive, key=sort_key)[:20],
        "top_target_positive": sorted(target_positive, key=sort_key)[:20],
        "top_strict_positive": sorted(strict_positive, key=sort_key)[:20],
        "blocker_counts_target_positive": dict(blocker_counts.most_common(20)),
        "interpretation": interpretation(live_net, live_ready, strict_target_positive, target_positive, blocker_counts),
    }


def interpretation(
    live_net: float,
    live_ready: list[dict[str, Any]],
    strict_target_positive: list[dict[str, Any]],
    target_positive: list[dict[str, Any]],
    blocker_counts: Counter[str],
) -> list[str]:
    notes = [
        "Research-only near-gate audit; no live bot changes or orders.",
        f"Live baseline for runway math is {live_net:.0f}c.",
        f"Live-ready rows found: {len(live_ready)}.",
    ]
    if strict_target_positive:
        best = sorted(strict_target_positive, key=sort_key)[0]
        notes.append(
            "Closest strict target-positive row is "
            f"{best.get('gate')} / {best.get('policy')} with net {best.get('net_cents')}c, "
            f"settled {best.get('settled')}, coverage {best.get('coverage_pct')}%, "
            f"source share {best.get('source_share')}, blockers {best.get('blockers')}."
        )
    if target_positive:
        best_any = sorted(target_positive, key=sort_key)[0]
        notes.append(
            "Closest target-positive row overall is "
            f"{best_any.get('gate')} / {best_any.get('policy')}; "
            "diagnostic/prefreeze rows still need their own strict birth if not strict_forward."
        )
    if blocker_counts:
        common = ", ".join(f"{key}={value}" for key, value in blocker_counts.most_common(5))
        notes.append(f"Most common blockers among positive target-coverage rows: {common}.")
    return notes


def fmt(value: Any) -> str:
    if value is None:
        return "n/a"
    if isinstance(value, float):
        return f"{value:.2f}"
    return str(value)


def write_md(report: dict[str, Any]) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8")
    counts = report.get("counts") or {}
    lines = [
        "# v28 Near-Gate Runway",
        "",
        "Research-only. No live bot logic changes, no orders, no process control.",
        "",
        f"- Generated UTC: `{report.get('generated_at_utc')}`",
        f"- Live baseline: `{fmt(report.get('live_baseline_cents'))}c`",
        f"- Rows / positive / target-positive / strict-target-positive / live-ready: `{counts.get('rows')}/{counts.get('positive')}/{counts.get('target_positive')}/{counts.get('strict_target_positive')}/{counts.get('live_ready')}`",
        "",
        "## Interpretation",
        "",
    ]
    lines.extend(f"- {note}" for note in report.get("interpretation") or [])
    lines.extend(
        [
            "",
            "## Closest Strict Target-Positive",
            "",
            "| rank | gate | policy | settled | W/L | coverage | net | delta live | source | cushion | sample need | cov need | clean source need | net to live | blockers |",
            "|---:|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|",
        ]
    )
    for idx, row in enumerate(report.get("top_strict_target_positive") or [], start=1):
        lines.append(table_row(idx, row))
    lines.extend(
        [
            "",
            "## Closest Target-Positive Overall",
            "",
            "| rank | gate | policy | settled | W/L | coverage | net | delta live | source | cushion | sample need | cov need | clean source need | net to live | blockers |",
            "|---:|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|",
        ]
    )
    for idx, row in enumerate(report.get("top_target_positive") or [], start=1):
        lines.append(table_row(idx, row))
    lines.extend(["", "## Blocker Counts", ""])
    for blocker, count in (report.get("blocker_counts_target_positive") or {}).items():
        lines.append(f"- `{blocker}`: `{count}`")
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def table_row(idx: int, row: dict[str, Any]) -> str:
    blockers = ", ".join(row.get("blockers") or []) or "none"
    wl = f"{row.get('wins')}/{row.get('losses')}" if row.get("wins") is not None else ""
    return (
        f"| {idx} | `{row.get('gate')}` | `{row.get('policy')}` | {row.get('settled')} | {wl} | "
        f"{fmt(row.get('coverage_pct'))}% | {fmt(row.get('net_cents'))} | {fmt(row.get('delta_vs_live_cents'))} | "
        f"{fmt(row.get('source_share'))} | {row.get('cushion')} | {row.get('settled_rows_needed')} | "
        f"{row.get('coverage_entries_needed')} | {row.get('approved_rows_needed_for_source_gate')} | "
        f"{fmt(row.get('net_cents_needed_to_beat_live'))} | {blockers} |"
    )


def main() -> None:
    report = build_report()
    write_md(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
