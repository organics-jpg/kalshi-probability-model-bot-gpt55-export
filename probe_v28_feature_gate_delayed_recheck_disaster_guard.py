"""Diagnostic disaster-guard scan for feature-gate delayed recheck.

Research-only. This scans observable guards that would reject a delayed-recheck
suppression when path-survival evidence is weak. It does not change live bot
logic or freeze a new rule.
"""
from __future__ import annotations

import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
OUT_JSON = OUT_DIR / "v28_feature_gate_delayed_recheck_disaster_guard_latest.json"
OUT_MD = OUT_DIR / "v28_feature_gate_delayed_recheck_disaster_guard_latest.md"

TRADEOFF = OUT_DIR / "v28_feature_gate_delayed_recheck_survival_tradeoff_latest.json"


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


def guard_specs() -> list[tuple[str, str, Callable[[dict[str, Any]], bool]]]:
    specs: list[tuple[str, str, Callable[[dict[str, Any]], bool]]] = []
    for floor in [60, 65, 70, 75, 80, 85]:
        specs.append(
            (
                f"reject_recheck_bid_lte_{floor}",
                f"Reject delayed suppression if recheck bid <= {floor}c.",
                lambda row, floor=floor: fnum(row.get("recheck_bid"), 999.0) <= floor,
            )
        )
    for floor in [60, 65, 70, 75, 80]:
        specs.append(
            (
                f"reject_min_window_bid_lte_{floor}",
                f"Reject delayed suppression if minimum bid during recheck window <= {floor}c.",
                lambda row, floor=floor: fnum(row.get("min_window_bid"), 999.0) <= floor,
            )
        )
    for drop in [0, 3, 5, 8, 10]:
        specs.append(
            (
                f"reject_window_drop_gte_{drop}",
                f"Reject delayed suppression if window drop >= {drop}c.",
                lambda row, drop=drop: fnum(row.get("window_drop_cents"), -999.0) >= drop,
            )
        )
    specs.extend(
        [
            (
                "reject_value_over_hold_recheck_bid_lte_82",
                "Reject value-over-hold delayed suppressions with recheck bid <=82c.",
                lambda row: row.get("reason_group") == "value_over_hold" and fnum(row.get("recheck_bid"), 999.0) <= 82,
            ),
            (
                "reject_value_over_hold_window_drop_gte_8",
                "Reject value-over-hold delayed suppressions with window drop >=8c.",
                lambda row: row.get("reason_group") == "value_over_hold" and fnum(row.get("window_drop_cents"), -999.0) >= 8,
            ),
            (
                "reject_value_over_hold_min_window_lte_61",
                "Reject value-over-hold delayed suppressions with min-window bid <=61c.",
                lambda row: row.get("reason_group") == "value_over_hold" and fnum(row.get("min_window_bid"), 999.0) <= 61,
            ),
            (
                "reject_reduce_recheck_bid_lte_76",
                "Reject probability-reduce delayed suppressions with recheck bid <=76c.",
                lambda row: row.get("reason_group") == "probability_reduce" and fnum(row.get("recheck_bid"), 999.0) <= 76,
            ),
            (
                "reject_reduce_window_drop_gte_0",
                "Reject probability-reduce delayed suppressions with nonpositive/immediate weak recheck window.",
                lambda row: row.get("reason_group") == "probability_reduce" and fnum(row.get("window_drop_cents"), -999.0) >= 0,
            ),
        ]
    )
    return specs


def reason_counts(rows: list[dict[str, Any]]) -> dict[str, int]:
    return dict(Counter(str(row.get("reason_group") or "unknown") for row in rows))


def summarize_variant(name: str, description: str, rows: list[dict[str, Any]], guard: Callable[[dict[str, Any]], bool]) -> dict[str, Any]:
    base = [row for row in rows if row.get("delayed_suppressed")]
    rejected = [row for row in base if guard(row)]
    kept = [row for row in base if not guard(row)]
    base_delta = sum(fnum(row.get("delayed_delta_vs_live_cents")) for row in base)
    kept_delta = sum(fnum(row.get("delayed_delta_vs_live_cents")) for row in kept)
    rejected_delta = sum(fnum(row.get("delayed_delta_vs_live_cents")) for row in rejected)
    adverse_25_removed = sum(1 for row in rejected if row.get("adverse_25c"))
    adverse_50_removed = sum(1 for row in rejected if row.get("adverse_50c"))
    adverse_25_kept = sum(1 for row in kept if row.get("adverse_25c"))
    adverse_50_kept = sum(1 for row in kept if row.get("adverse_50c"))
    return {
        "name": name,
        "description": description,
        "base_suppressed": len(base),
        "guarded_rejections": len(rejected),
        "kept_suppressions": len(kept),
        "base_delta_cents": base_delta,
        "kept_delta_cents": kept_delta,
        "rejected_delta_cents": rejected_delta,
        "delta_given_up_pct": None if base_delta == 0 else rejected_delta / base_delta,
        "adverse_25_removed": adverse_25_removed,
        "adverse_50_removed": adverse_50_removed,
        "adverse_25_kept": adverse_25_kept,
        "adverse_50_kept": adverse_50_kept,
        "rejected_reason_counts": reason_counts(rejected),
        "kept_reason_counts": reason_counts(kept),
        "rejected_markets": [row.get("market") for row in rejected],
        "blockers": blockers_for(kept_delta, rejected_delta, adverse_25_removed, adverse_25_kept, len(rejected)),
    }


def blockers_for(
    kept_delta: float,
    rejected_delta: float,
    adverse_25_removed: int,
    adverse_25_kept: int,
    rejected_count: int,
) -> list[str]:
    blockers = ["diagnostic_prefreeze", "suppressed_decisions_lt_30"]
    if rejected_count == 0:
        blockers.append("no_guarded_rows")
    if adverse_25_removed == 0:
        blockers.append("does_not_remove_large_adverse_rows")
    if adverse_25_kept > 0:
        blockers.append("large_adverse_rows_remain")
    if rejected_delta >= 350:
        blockers.append("gives_up_large_recovery")
    if kept_delta <= 0:
        blockers.append("kept_delta_not_positive")
    return blockers


def build_report() -> dict[str, Any]:
    tradeoff = load_json(TRADEOFF)
    rows = tradeoff.get("joined_rows") if isinstance(tradeoff.get("joined_rows"), list) else []
    variants = [summarize_variant(name, desc, rows, fn) for name, desc, fn in guard_specs()]
    variants.sort(
        key=lambda row: (
            int("large_adverse_rows_remain" in row["blockers"]),
            int("gives_up_large_recovery" in row["blockers"]),
            -int(row["adverse_25_removed"]),
            -float(row["kept_delta_cents"]),
        )
    )
    return {
        "generated_at_utc": utc_now_iso(),
        "tradeoff_source": str(TRADEOFF),
        "base_delayed_summary": tradeoff.get("delayed_suppressed_summary", {}),
        "variants": variants,
        "best": variants[0] if variants else {},
        "interpretation": [
            "All rows are diagnostic/prefreeze; this is not promotion evidence.",
            "A usable disaster guard should remove large adverse paths without giving back most delayed-recheck recovery.",
            "If every clean-looking guard either leaves large adverse rows or sacrifices too much recovery, keep the frozen delayed-recheck watch unchanged until strict rows arrive.",
        ],
    }


def write_report(payload: dict[str, Any]) -> None:
    base = payload["base_delayed_summary"]
    best = payload["best"]
    lines = [
        "# v28 Feature-Gate Delayed-Recheck Disaster Guard",
        "",
        "Research-only diagnostic guard scan. No live bot changes, no orders, no new frozen rule.",
        "",
        f"- Generated UTC: `{payload['generated_at_utc']}`",
        f"- Base delayed rows / delta: `{base.get('rows')}` / `{cents(base.get('delta_vs_live_cents'))}`",
        f"- Base adverse 25/50 rows: `{base.get('adverse_25c_rows')}` / `{base.get('adverse_50c_rows')}`",
        f"- Best diagnostic guard by conservative sort: `{best.get('name')}`",
        f"- Best kept delta / given up: `{cents(best.get('kept_delta_cents'))}` / `{cents(best.get('rejected_delta_cents'))}`",
        f"- Best adverse 25/50 kept: `{best.get('adverse_25_kept')}` / `{best.get('adverse_50_kept')}`",
        f"- Best blockers: `{', '.join(best.get('blockers') or [])}`",
        "",
        "## Guard Scan",
        "",
        "| guard | rejects | kept | kept delta | given up | adverse 25 removed/kept | adverse 50 removed/kept | rejected reasons | blockers |",
        "|---|---:|---:|---:|---:|---:|---:|---|---|",
    ]
    for row in payload["variants"]:
        lines.append(
            "| {name} | {rejects} | {kept} | {kept_delta} | {given_up} | {a25r}/{a25k} | {a50r}/{a50k} | {reasons} | {blockers} |".format(
                name=row.get("name"),
                rejects=row.get("guarded_rejections"),
                kept=row.get("kept_suppressions"),
                kept_delta=cents(row.get("kept_delta_cents")),
                given_up=cents(row.get("rejected_delta_cents")),
                a25r=row.get("adverse_25_removed"),
                a25k=row.get("adverse_25_kept"),
                a50r=row.get("adverse_50_removed"),
                a50k=row.get("adverse_50_kept"),
                reasons=row.get("rejected_reason_counts"),
                blockers=", ".join(row.get("blockers") or []),
            )
        )

    lines.extend(
        [
            "",
            "## Interpretation",
            "",
        ]
    )
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
