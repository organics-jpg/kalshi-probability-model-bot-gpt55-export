"""Source-slice audit for the feature-gate size-shrink candidate.

Research-only; no live bot changes or orders.

The size-shrink candidate is the closest strict, target-coverage branch, but it
still fails the row-count source gate. This probe asks whether the source-fragile
repair rows are contributing real edge or merely buying coverage.
"""
from __future__ import annotations

import json
import math
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
SOURCE_JSON = OUT_DIR / "v28_feature_gate_coverage_size_shrink_latest.json"
LIVE_SUMMARY_JSON = ROOT / "stats" / "live_mushroom_v28_size2" / "summary.json"
OUT_JSON = OUT_DIR / "v28_feature_gate_size_shrink_source_slice_latest.json"
OUT_MD = OUT_DIR / "v28_feature_gate_size_shrink_source_slice_latest.md"

TARGET_COVERAGE_MIN = 75.0
MAX_RECON_SHARE = 0.35
MIN_SETTLED = 30
MIN_CUSHION = 3


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def fnum(value: Any, default: float = 0.0) -> float:
    try:
        if value is None:
            return default
        return float(value)
    except (TypeError, ValueError):
        return default


def b(value: Any) -> bool:
    return bool(value)


def live_net_cents() -> float:
    if not LIVE_SUMMARY_JSON.exists():
        return 0.0
    return 100.0 * fnum(load_json(LIVE_SUMMARY_JSON).get("net_pnl_total_dollars"))


def row_id(row: dict[str, Any]) -> tuple[Any, Any]:
    return row.get("market"), row.get("side")


def is_recon(row: dict[str, Any]) -> bool:
    return not b(row.get("approved"))


def is_settled(row: dict[str, Any]) -> bool:
    return b(row.get("settled"))


def role(row: dict[str, Any]) -> str:
    return "anchor_overlap" if b(row.get("is_anchor")) else "repair_added"


def weighted_net(row: dict[str, Any]) -> float:
    return fnum(row.get("weighted_net_cents"))


def raw_net(row: dict[str, Any]) -> float:
    return fnum(row.get("raw_net_cents"))


def source_name(row: dict[str, Any]) -> str:
    return str(row.get("source") or "unknown")


def scenario_metrics(
    label: str,
    rows: list[dict[str, Any]],
    denominator: int,
    live_net: float,
) -> dict[str, Any]:
    settled_rows = [row for row in rows if is_settled(row)]
    wins = sum(1 for row in settled_rows if raw_net(row) > 0)
    losses = sum(1 for row in settled_rows if raw_net(row) < 0)
    net = sum(weighted_net(row) for row in settled_rows)
    recon_count = sum(1 for row in rows if is_recon(row))
    entries = len(rows)
    coverage = 100.0 * entries / denominator if denominator else 0.0
    recon_share = recon_count / entries if entries else 0.0
    weight_sum = sum(fnum(row.get("weight")) for row in rows)
    recon_weight = sum(fnum(row.get("weight")) for row in rows if is_recon(row))
    exposure_recon_share = recon_weight / weight_sum if weight_sum else 0.0
    blockers: list[str] = []
    if len(settled_rows) < MIN_SETTLED:
        blockers.append("settled_lt_30")
    if coverage < TARGET_COVERAGE_MIN:
        blockers.append("coverage_too_low")
    if recon_share > MAX_RECON_SHARE:
        blockers.append("row_reconstructed_share_gt_35pct")
    if math.floor(max(0.0, net) / 100.0) < MIN_CUSHION:
        blockers.append("full_loss_cushion_lt_3")
    if net <= live_net:
        blockers.append("does_not_beat_refreshed_live_baseline")
    return {
        "scenario": label,
        "entries": entries,
        "settled": len(settled_rows),
        "wins": wins,
        "losses": losses,
        "coverage_pct": coverage,
        "weighted_net_cents": net,
        "delta_vs_live_cents": net - live_net,
        "row_reconstructed_share": recon_share,
        "exposure_reconstructed_share": exposure_recon_share,
        "full_loss_cushion": math.floor(max(0.0, net) / 100.0),
        "blockers": blockers,
    }


def group_metrics(
    label: str,
    rows: list[dict[str, Any]],
    key_func: Callable[[dict[str, Any]], str],
) -> list[dict[str, Any]]:
    buckets: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        buckets[key_func(row)].append(row)
    out = []
    for key, items in sorted(buckets.items()):
        settled = [row for row in items if is_settled(row)]
        out.append(
            {
                "group": label,
                "bucket": key,
                "entries": len(items),
                "settled": len(settled),
                "wins": sum(1 for row in settled if raw_net(row) > 0),
                "losses": sum(1 for row in settled if raw_net(row) < 0),
                "weighted_net_cents": sum(weighted_net(row) for row in settled),
                "avg_weighted_net_cents": (
                    sum(weighted_net(row) for row in settled) / len(settled) if settled else 0.0
                ),
                "row_reconstructed_share": (
                    sum(1 for row in items if is_recon(row)) / len(items) if items else 0.0
                ),
                "weight_sum": sum(fnum(row.get("weight")) for row in items),
            }
        )
    return out


def best_policy(lane: dict[str, Any]) -> dict[str, Any]:
    rows = lane.get("rows") or []
    if not rows:
        return {}
    return rows[0]


def source_gate_best_case_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    approved = [row for row in rows if not is_recon(row)]
    recon = [row for row in rows if is_recon(row)]
    max_recon = math.floor((MAX_RECON_SHARE * len(approved)) / (1.0 - MAX_RECON_SHARE))
    recon_keep = sorted(recon, key=lambda row: weighted_net(row), reverse=True)[:max_recon]
    return approved + recon_keep


def source_add_rows_needed(rows: list[dict[str, Any]]) -> int:
    entries = len(rows)
    recon = sum(1 for row in rows if is_recon(row))
    add = 0
    while entries + add > 0 and recon / (entries + add) > MAX_RECON_SHARE:
        add += 1
    return add


def analyze_lane(lane: dict[str, Any], live_net: float) -> dict[str, Any]:
    policy = best_policy(lane)
    rows = list(policy.get("selected_rows") or [])
    denominator = int(fnum(lane.get("future_denominator")))
    approved_rows = [row for row in rows if not is_recon(row)]
    recon_rows = [row for row in rows if is_recon(row)]
    anchor_rows = [row for row in rows if role(row) == "anchor_overlap"]
    repair_rows = [row for row in rows if role(row) == "repair_added"]
    zero_recon_rows = [
        {**row, "weighted_net_cents": 0.0 if is_recon(row) and is_settled(row) else row.get("weighted_net_cents")}
        for row in rows
    ]
    quarter_recon_rows = [
        {
            **row,
            "weighted_net_cents": weighted_net(row) * 0.25 if is_recon(row) and is_settled(row) else row.get("weighted_net_cents"),
        }
        for row in rows
    ]

    scenarios = [
        scenario_metrics("current_weighted_policy", rows, denominator, live_net),
        scenario_metrics("approved_only_drop_reconstructed", approved_rows, denominator, live_net),
        scenario_metrics("anchor_overlap_only", anchor_rows, denominator, live_net),
        scenario_metrics("repair_added_only", repair_rows, denominator, live_net),
        scenario_metrics("source_gate_best_case_drop_recon", source_gate_best_case_rows(rows), denominator, live_net),
        scenario_metrics("zero_recontribution_keep_rows", zero_recon_rows, denominator, live_net),
        scenario_metrics("quarter_recontribution_keep_rows", quarter_recon_rows, denominator, live_net),
    ]

    groups = []
    groups.extend(group_metrics("role", rows, role))
    groups.extend(group_metrics("source", rows, source_name))
    groups.extend(group_metrics("role_x_source", rows, lambda row: f"{role(row)}::{source_name(row)}"))
    groups.extend(
        group_metrics(
            "abs_d_sigma_bucket",
            rows,
            lambda row: (
                "abs_lt_075"
                if fnum(row.get("abs_d_sigma")) < 0.75
                else "abs_075_125"
                if fnum(row.get("abs_d_sigma")) < 1.25
                else "abs_ge_125"
            ),
        )
    )
    groups.extend(
        group_metrics(
            "recross_bucket",
            rows,
            lambda row: (
                "recross_lt_015"
                if fnum(row.get("recross_hazard_score")) < 0.15
                else "recross_015_035"
                if fnum(row.get("recross_hazard_score")) < 0.35
                else "recross_ge_035"
            ),
        )
    )

    repair_recon = [row for row in repair_rows if is_recon(row)]
    repair_approved = [row for row in repair_rows if not is_recon(row)]
    worst_rows = sorted(
        [row for row in rows if is_settled(row)],
        key=lambda row: weighted_net(row),
    )[:10]
    best_recon = sorted(
        [row for row in recon_rows if is_settled(row)],
        key=lambda row: weighted_net(row),
        reverse=True,
    )[:10]

    return {
        "lane": lane.get("lane"),
        "policy": policy.get("policy"),
        "anchor_rule": lane.get("anchor_rule"),
        "repair_rule": lane.get("repair_rule"),
        "future_denominator": denominator,
        "reported_summary": {
            key: policy.get(key)
            for key in (
                "entries",
                "settled",
                "wins",
                "losses",
                "coverage_pct",
                "weighted_net_cents",
                "row_reconstructed_share",
                "exposure_reconstructed_share",
                "full_loss_cushion",
                "blockers",
            )
        },
        "source_counts": dict(Counter(source_name(row) for row in rows)),
        "role_counts": dict(Counter(role(row) for row in rows)),
        "repair_source_counts": dict(Counter(source_name(row) for row in repair_rows)),
        "source_gate_clean_rows_needed_if_keep_current": source_add_rows_needed(rows),
        "approved_repair_rows": len(repair_approved),
        "reconstructed_repair_rows": len(repair_recon),
        "scenarios": scenarios,
        "groups": groups,
        "worst_rows": [
            {
                "market": row.get("market"),
                "side": row.get("side"),
                "role": role(row),
                "source": source_name(row),
                "raw_net_cents": row.get("raw_net_cents"),
                "weight": row.get("weight"),
                "weighted_net_cents": row.get("weighted_net_cents"),
                "abs_d_sigma": row.get("abs_d_sigma"),
                "recross_hazard_score": row.get("recross_hazard_score"),
                "ask_prob": row.get("ask_prob"),
            }
            for row in worst_rows
        ],
        "best_reconstructed_rows": [
            {
                "market": row.get("market"),
                "side": row.get("side"),
                "role": role(row),
                "source": source_name(row),
                "raw_net_cents": row.get("raw_net_cents"),
                "weight": row.get("weight"),
                "weighted_net_cents": row.get("weighted_net_cents"),
                "abs_d_sigma": row.get("abs_d_sigma"),
                "recross_hazard_score": row.get("recross_hazard_score"),
                "ask_prob": row.get("ask_prob"),
            }
            for row in best_recon
        ],
    }


def interpretation(lanes: list[dict[str, Any]], live_net: float) -> list[str]:
    notes = [
        "Research-only source-slice audit; no live bot changes or orders.",
        f"Live baseline for delta math is {live_net:.0f}c.",
    ]
    for lane in lanes:
        scenarios = {row.get("scenario"): row for row in lane.get("scenarios") or []}
        current = scenarios.get("current_weighted_policy") or {}
        approved = scenarios.get("approved_only_drop_reconstructed") or {}
        repair = scenarios.get("repair_added_only") or {}
        source_clean = scenarios.get("source_gate_best_case_drop_recon") or {}
        notes.append(
            f"{lane.get('lane')}: current policy is {current.get('weighted_net_cents')}c "
            f"with W/L {current.get('wins')}/{current.get('losses')} and "
            f"{current.get('coverage_pct'):.2f}% coverage, but row source share stays "
            f"{current.get('row_reconstructed_share'):.3f}."
        )
        notes.append(
            f"{lane.get('lane')}: approved-only rows are {approved.get('weighted_net_cents')}c "
            f"with W/L {approved.get('wins')}/{approved.get('losses')} but only "
            f"{approved.get('coverage_pct'):.2f}% coverage; repair-added rows alone are "
            f"{repair.get('weighted_net_cents')}c with W/L {repair.get('wins')}/{repair.get('losses')}."
        )
        notes.append(
            f"{lane.get('lane')}: even a post-hoc best-case source-gate trim leaves "
            f"{source_clean.get('coverage_pct'):.2f}% coverage, so this branch needs fresh "
            "approved rows rather than more reconstructed repair rows."
        )
    return notes


def build_report() -> dict[str, Any]:
    source = load_json(SOURCE_JSON)
    live_net = live_net_cents()
    lanes = [analyze_lane(lane, live_net) for lane in source.get("lanes") or []]
    return {
        "generated_at_utc": utc_now_iso(),
        "source_path": str(SOURCE_JSON),
        "live_summary_path": str(LIVE_SUMMARY_JSON),
        "live_baseline_cents": live_net,
        "freeze_ts_utc": source.get("freeze_ts_utc"),
        "lanes": lanes,
        "interpretation": interpretation(lanes, live_net),
    }


def fmt(value: Any, digits: int = 3) -> str:
    if value is None:
        return ""
    if isinstance(value, float):
        return f"{value:.{digits}f}"
    return str(value)


def wl(row: dict[str, Any]) -> str:
    return f"{row.get('wins')}/{row.get('losses')}"


def write_report(report: dict[str, Any]) -> None:
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    lines = [
        "# v28 Feature-Gate Size-Shrink Source Slice",
        "",
        "Research-only. No live bot logic changes, no orders, no process control.",
        "",
        f"- Generated UTC: `{report.get('generated_at_utc')}`",
        f"- Feature-gate freeze UTC: `{report.get('freeze_ts_utc')}`",
        f"- Live baseline: `{fmt(report.get('live_baseline_cents'))}c`",
        "",
        "## Interpretation",
        "",
    ]
    lines.extend(f"- {note}" for note in report.get("interpretation") or [])
    for lane in report.get("lanes") or []:
        lines.extend(
            [
                "",
                f"## {lane.get('lane')}",
                "",
                f"- Policy: `{lane.get('policy')}`",
                f"- Anchor rule: `{lane.get('anchor_rule')}`",
                f"- Repair rule: `{lane.get('repair_rule')}`",
                f"- Future denominator: `{lane.get('future_denominator')}`",
                f"- Source counts: `{lane.get('source_counts')}`",
                f"- Role counts: `{lane.get('role_counts')}`",
                f"- Repair source counts: `{lane.get('repair_source_counts')}`",
                f"- Clean approved rows needed if current rows are kept: `{lane.get('source_gate_clean_rows_needed_if_keep_current')}`",
                "",
                "### Scenarios",
                "",
                "| scenario | entries | settled | W/L | coverage | net c | delta live c | row recon | exposure recon | cushion | blockers |",
                "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|",
            ]
        )
        for row in lane.get("scenarios") or []:
            blockers = ", ".join(row.get("blockers") or []) or "none"
            lines.append(
                f"| `{row.get('scenario')}` | {row.get('entries')} | {row.get('settled')} | "
                f"{wl(row)} | {fmt(row.get('coverage_pct'))}% | {fmt(row.get('weighted_net_cents'))} | "
                f"{fmt(row.get('delta_vs_live_cents'))} | {fmt(row.get('row_reconstructed_share'))} | "
                f"{fmt(row.get('exposure_reconstructed_share'))} | {row.get('full_loss_cushion')} | {blockers} |"
            )
        lines.extend(
            [
                "",
                "### Group Attribution",
                "",
                "| group | bucket | entries | settled | W/L | weighted net c | avg weighted net c | row recon | weight sum |",
                "|---|---|---:|---:|---:|---:|---:|---:|---:|",
            ]
        )
        for row in lane.get("groups") or []:
            lines.append(
                f"| {row.get('group')} | `{row.get('bucket')}` | {row.get('entries')} | {row.get('settled')} | "
                f"{wl(row)} | {fmt(row.get('weighted_net_cents'))} | {fmt(row.get('avg_weighted_net_cents'))} | "
                f"{fmt(row.get('row_reconstructed_share'))} | {fmt(row.get('weight_sum'))} |"
            )
        lines.extend(
            [
                "",
                "### Worst Settled Rows",
                "",
                "| market | side | role | source | raw net | weight | weighted net | abs d | recross | ask |",
                "|---|---|---|---|---:|---:|---:|---:|---:|---:|",
            ]
        )
        for row in lane.get("worst_rows") or []:
            lines.append(
                f"| `{row.get('market')}` | {row.get('side')} | {row.get('role')} | {row.get('source')} | "
                f"{fmt(row.get('raw_net_cents'))} | {fmt(row.get('weight'))} | {fmt(row.get('weighted_net_cents'))} | "
                f"{fmt(row.get('abs_d_sigma'))} | {fmt(row.get('recross_hazard_score'))} | {fmt(row.get('ask_prob'))} |"
            )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    write_report(build_report())
    print(f"Wrote {OUT_MD}")
    print(f"Wrote {OUT_JSON}")


if __name__ == "__main__":
    main()
