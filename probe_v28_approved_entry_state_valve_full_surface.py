"""Full-surface replay for approved-entry state valves.

Research-only; no live bot changes or orders.

The approved-entry valve validators proved a useful mechanism on actual
v28-approved entries. This adapter applies those observable valve rules to the
normal broad target surfaces so the result can be judged against the same
coverage/source/cushion/live-baseline gates used by other entry lanes.
"""
from __future__ import annotations

import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Callable

from probe_v28_coverage_repair_pool_diagnostic import COVERAGE_FLOOR, as_float, row_net_after_fee, summarize
from probe_v28_frozen_boundary_clock_fv_entry_bridge import future_surfaces as bridge_surfaces
from probe_v28_frozen_boundary_clock_repair_entry import future_surfaces as entry_surfaces


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"

DANGER_VALVE_JSON = OUT_DIR / "v28_frozen_danger_zone_entry_valve_latest.json"
STATE_VALVE_JSON = OUT_DIR / "v28_frozen_approved_entry_state_valve_latest.json"
LIVE_SUMMARY_JSON = ROOT / "stats" / "live_mushroom_v28_size2" / "summary.json"

OUT_JSON = OUT_DIR / "v28_approved_entry_state_valve_full_surface_latest.json"
OUT_MD = OUT_DIR / "v28_approved_entry_state_valve_full_surface_latest.md"

MIN_SETTLED = 30
MAX_RECONSTRUCTED_SHARE = 0.35
MIN_FULL_LOSS_CUSHION = 3
TARGET_COVERAGE_MAX = 90.0


def load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
    return payload if isinstance(payload, dict) else {}


def live_net_cents() -> float | None:
    payload = load_json(LIVE_SUMMARY_JSON)
    dollars = as_float(payload.get("net_pnl_total_dollars"))
    return None if dollars is None else round(dollars * 100.0, 6)


def raw_book_gap(row: dict[str, Any]) -> float | None:
    gap = as_float(row.get("raw_book_gap"))
    if gap is not None:
        return gap
    p_side = as_float(row.get("p_side"))
    ask = as_float(row.get("ask_prob"))
    if ask is None:
        ask_cents = as_float(row.get("ask_cents"))
        ask = None if ask_cents is None else ask_cents / 100.0
    return None if p_side is None or ask is None else p_side - ask


def row_time(row: dict[str, Any]) -> str:
    return str(row.get("ts_wall") or row.get("entry_ts") or "")


def with_reentry_state(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    counts_by_market_side: dict[tuple[str, str], int] = defaultdict(int)
    out = []
    for row in sorted(rows, key=lambda item: (str(item.get("market") or ""), row_time(item))):
        market = str(row.get("market") or "")
        side = str(row.get("side") or "")
        key = (market, side)
        enriched = dict(row)
        enriched["market_side_entry_index"] = counts_by_market_side[key]
        enriched["raw_book_gap"] = raw_book_gap(row)
        counts_by_market_side[key] += 1
        out.append(enriched)
    return out


def keep_state_valve(row: dict[str, Any]) -> bool:
    if int(row.get("market_side_entry_index") or 0) == 0:
        return True
    gap = raw_book_gap(row)
    return gap is None or gap <= 0.15


def keep_danger_valve(row: dict[str, Any]) -> bool:
    gap = raw_book_gap(row)
    if gap is None:
        return True
    if gap > 0.30:
        return False
    if int(row.get("market_side_entry_index") or 0) > 0 and gap > 0.15:
        return False
    return True


POLICIES: dict[str, Callable[[dict[str, Any]], bool]] = {
    "same_side_reentry_gap_lte_15pp": keep_state_valve,
    "skip_reentry_gap15_or_gap30": keep_danger_valve,
}


def source(row: dict[str, Any]) -> str:
    return str(row.get("source") or "unknown")


def source_counts(rows: list[dict[str, Any]]) -> dict[str, int]:
    return dict(Counter(source(row) for row in rows))


def reconstructed_share(counts: dict[str, int]) -> float | None:
    total = sum(counts.values())
    if total <= 0:
        return None
    return (total - int(counts.get("approved_entry") or 0)) / total


def net_cents(row: dict[str, Any]) -> float:
    return float(row.get("net_gross_cents_after_entry_fee") or row_net_after_fee(row) or 0.0)


def full_loss_cushion(cents: float | None) -> int | None:
    if cents is None:
        return None
    if cents <= 0:
        return 0
    return int(cents // 100)


def compact(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "market": row.get("market"),
        "source": source(row),
        "side": row.get("side"),
        "side_won": row.get("side_won"),
        "net_cents": net_cents(row),
        "p_side": row.get("p_side"),
        "ask_prob": row.get("ask_prob"),
        "raw_book_gap": raw_book_gap(row),
        "market_side_entry_index": row.get("market_side_entry_index"),
        "ts_wall": row.get("ts_wall") or row.get("entry_ts"),
    }


def evaluate_surface(
    valve_label: str,
    policy: str,
    freeze_ts: str,
    surface_label: str,
    surface_fn: Callable[[str], tuple[list[dict[str, Any]], list[dict[str, Any]], int]],
    live_cents: float | None,
) -> dict[str, Any]:
    _, target, denominator = surface_fn(freeze_ts)
    target_state = with_reentry_state(target)
    keep = POLICIES[policy]
    selected = [row for row in target_state if keep(row)]
    skipped = [row for row in target_state if not keep(row)]

    base = summarize(target_state, denominator)
    candidate = summarize(selected, denominator)
    skipped_summary = summarize(skipped, denominator)
    counts = source_counts(selected)
    share = reconstructed_share(counts)
    base_net = as_float(base.get("net_cents")) or 0.0
    candidate_net = as_float(candidate.get("net_cents")) or 0.0
    delta_vs_base = candidate_net - base_net
    delta_vs_live = None if live_cents is None else candidate_net - live_cents
    cushion = full_loss_cushion(candidate_net)
    delta_cushion = full_loss_cushion(delta_vs_base)

    blockers: list[str] = []
    settled = int(as_float(candidate.get("settled")) or 0)
    coverage = as_float(candidate.get("coverage_pct"))
    if settled < MIN_SETTLED:
        blockers.append("settled_lt_30")
    if coverage is None or coverage < COVERAGE_FLOOR:
        blockers.append("coverage_too_low")
    if coverage is not None and coverage > TARGET_COVERAGE_MAX:
        blockers.append("coverage_above_90pct")
    if candidate_net <= 0:
        blockers.append("net_not_positive")
    if share is not None and share > MAX_RECONSTRUCTED_SHARE:
        blockers.append("reconstructed_share_gt_35pct")
    if cushion is None or cushion < MIN_FULL_LOSS_CUSHION:
        blockers.append("full_loss_cushion_lt_3")
    if delta_cushion is None or delta_cushion < MIN_FULL_LOSS_CUSHION:
        blockers.append("delta_full_loss_cushion_lt_3")
    if delta_vs_base <= 0:
        blockers.append("delta_vs_base_not_positive")
    if delta_vs_live is None or delta_vs_live <= 0:
        blockers.append("does_not_beat_refreshed_live_baseline")
    blockers.append("adapter_replay_not_independently_frozen_candidate")
    blockers.append("live_readiness_not_evaluated")

    return {
        "valve": valve_label,
        "policy": policy,
        "surface": surface_label,
        "freeze_ts_utc": freeze_ts,
        "future_denominator": denominator,
        "base_summary": base,
        "candidate_summary": candidate,
        "skipped_summary": skipped_summary,
        "delta_vs_base_cents": delta_vs_base,
        "delta_vs_live_cents": delta_vs_live,
        "source_counts": counts,
        "reconstructed_share": share,
        "full_loss_cushion": cushion,
        "delta_full_loss_cushion": delta_cushion,
        "skipped_rows": [compact(row) for row in skipped],
        "blockers": blockers,
        "promotion_ready": False,
    }


def valve_sources() -> list[dict[str, Any]]:
    out = []
    for label, path in [
        ("danger_zone_entry_valve", DANGER_VALVE_JSON),
        ("approved_entry_state_valve", STATE_VALVE_JSON),
    ]:
        payload = load_json(path)
        candidate = payload.get("candidate") or {}
        freeze = payload.get("freeze") or {}
        policy = str(candidate.get("policy") or freeze.get("policy") or "")
        freeze_ts = str(freeze.get("freeze_ts_utc") or "")
        if policy in POLICIES and freeze_ts:
            out.append({
                "label": label,
                "policy": policy,
                "freeze_ts_utc": freeze_ts,
                "approved_only_report": payload,
            })
    return out


def build_report() -> dict[str, Any]:
    live_cents = live_net_cents()
    rows = []
    for valve in valve_sources():
        for surface_label, surface_fn in [
            ("entry_surface", entry_surfaces),
            ("fv_bridge_surface", bridge_surfaces),
        ]:
            rows.append(
                evaluate_surface(
                    valve["label"],
                    valve["policy"],
                    valve["freeze_ts_utc"],
                    surface_label,
                    surface_fn,
                    live_cents,
                )
            )
    rows.sort(
        key=lambda row: (
            len(row.get("blockers") or []),
            -float(row.get("delta_vs_base_cents") or -999999.0),
            -float((row.get("candidate_summary") or {}).get("net_cents") or -999999.0),
        )
    )
    return {
        "live_net_cents": live_cents,
        "rows": rows,
        "promotion_ready_rows": [row for row in rows if row.get("promotion_ready")],
        "interpretation": interpretation(rows, live_cents),
    }


def interpretation(rows: list[dict[str, Any]], live_cents: float | None) -> list[str]:
    if not rows:
        return ["No frozen valve sources were available for full-surface replay."]
    best = rows[0]
    best_summary = best.get("candidate_summary") or {}
    return [
        f"Best full-surface valve replay is {best.get('valve')} / {best.get('surface')} with net {best_summary.get('net_cents')}c, delta vs base {best.get('delta_vs_base_cents')}c, and blockers {best.get('blockers')}.",
        f"Live baseline used for naive comparison is {live_cents}c.",
        "This is an adapter replay, not a new independently frozen candidate; promote nothing from this report.",
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
        "# v28 Approved-Entry State Valve Full-Surface Replay",
        "",
        "Research-only adapter replay; no live bot changes or orders.",
        "",
        f"- Live baseline net: `{fmt(report.get('live_net_cents'))}c`",
        f"- Replayed rows: `{len(report.get('rows') or [])}`",
        f"- Promotion-ready rows: `{len(report.get('promotion_ready_rows') or [])}`",
        "",
        "## Interpretation",
        "",
    ]
    for note in report.get("interpretation") or []:
        lines.append(f"- {note}")
    lines.extend([
        "",
        "## Full-Surface Rows",
        "",
        "| valve | surface | policy | settled | W/L | coverage | net c | delta vs base | delta vs live | recon share | cushion/delta cushion | skipped | blockers |",
        "|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|",
    ])
    for row in report.get("rows") or []:
        summary = row.get("candidate_summary") or {}
        skipped = row.get("skipped_summary") or {}
        lines.append(
            f"| `{row.get('valve')}` | `{row.get('surface')}` | `{row.get('policy')}` | "
            f"{summary.get('settled')} | {summary.get('wins')}/{summary.get('losses')} | "
            f"{fmt(summary.get('coverage_pct'))} | {fmt(summary.get('net_cents'))} | "
            f"{fmt(row.get('delta_vs_base_cents'))} | {fmt(row.get('delta_vs_live_cents'))} | "
            f"{fmt(row.get('reconstructed_share'))} | {fmt(row.get('full_loss_cushion'))}/{fmt(row.get('delta_full_loss_cushion'))} | "
            f"{skipped.get('entries')} | {', '.join(row.get('blockers') or []) or 'none'} |"
        )
    lines.extend(["", "## Skipped Rows", ""])
    for row in report.get("rows") or []:
        skipped_rows = row.get("skipped_rows") or []
        if not skipped_rows:
            continue
        lines.append(f"### {row.get('valve')} / {row.get('surface')}")
        for skipped in skipped_rows[:12]:
            lines.append(
                f"- `{skipped.get('market')}` `{skipped.get('source')}` `{skipped.get('side')}` won `{skipped.get('side_won')}`, "
                f"net `{fmt(skipped.get('net_cents'))}c`, gap `{fmt(skipped.get('raw_book_gap'))}`, "
                f"same-side idx `{skipped.get('market_side_entry_index')}`"
            )
        lines.append("")
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    report = build_report()
    write_md(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
