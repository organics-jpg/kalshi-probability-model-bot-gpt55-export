"""Frozen forward watch for soft-frontier feature-gate entries plus guarded exits.

Research-only; no live bot changes or orders.

This is the broad-entry mix/match branch: take the observable clean-broad
feature-gate rule that reached target coverage diagnostically, then apply the
frozen book-gap/loss-guard exit candidates only when the selected entry can be
matched to an unambiguous real live v28 exit row.
"""
from __future__ import annotations

import json
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from probe_v28_boundary_clock_feature_gate_candidate import as_float, best_per_market, passes, source
from probe_v28_coverage_repair_pool_diagnostic import COVERAGE_FLOOR, summarize
from probe_v28_frozen_boundary_clock_fv_entry_bridge import future_surfaces as bridge_surfaces
from probe_v28_frozen_boundary_clock_repair_entry import future_surfaces as entry_surfaces


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
STATE_JSON = OUT_DIR / "v28_frozen_feature_gate_soft_frontier_exit_stack_state.json"
OUT_JSON = OUT_DIR / "v28_frozen_feature_gate_soft_frontier_exit_stack_latest.json"
OUT_MD = OUT_DIR / "v28_frozen_feature_gate_soft_frontier_exit_stack_latest.md"

EXIT_SOURCES = {
    "book_gap": OUT_DIR / "v28_frozen_exit_book_gap_suppression_latest.json",
    "loss_guard_v1": OUT_DIR / "v28_frozen_exit_book_gap_loss_guard_latest.json",
    "loss_guard_v2": OUT_DIR / "v28_frozen_exit_book_gap_loss_guard_v2_latest.json",
    "loss_guard_v3": OUT_DIR / "v28_frozen_exit_book_gap_loss_guard_v3_latest.json",
}

SOFT_RULES = {
    "soft_raw03_recross50_abs50_ask35": {
        "raw_edge_min": 0.03,
        "recross_max": 0.50,
        "abs_d_min": 0.50,
        "ask_min": 0.35,
    },
    "soft_raw03_recross50_abs50_ask50": {
        "raw_edge_min": 0.03,
        "recross_max": 0.50,
        "abs_d_min": 0.50,
        "ask_min": 0.50,
    },
    "soft_raw03_recross50_abs65_ask35": {
        "raw_edge_min": 0.03,
        "recross_max": 0.50,
        "abs_d_min": 0.65,
        "ask_min": 0.35,
    },
}

MIN_SETTLED = 30
MAX_RECONSTRUCTED_SHARE = 0.35
MIN_FULL_LOSS_CUSHION = 3
MIN_JOINED_EXIT_ROWS = 30


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


def load_or_create_state() -> dict[str, Any]:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    if STATE_JSON.exists():
        state = load_json(STATE_JSON)
        if state.get("freeze_ts_utc"):
            return state
    state = {
        "freeze_ts_utc": utc_now_iso(),
        "candidate_family": "feature_gate_soft_frontier_exit_stack",
        "entry_rules": SOFT_RULES,
        "exit_rule": "Use frozen book-gap/loss-guard exit candidates only for unambiguous matched live v28 exit rows.",
        "physics": (
            "The soft frontier preserves target coverage by admitting moderate boundary distance "
            "when raw edge, recross risk, and ask quality are all acceptable. Guarded exits then "
            "test whether the main remaining failure is exit clipping rather than entry selection."
        ),
        "strict_forward_note": "Rows before this timestamp are diagnostic only; only post-freeze rows count for promotion.",
    }
    STATE_JSON.write_text(json.dumps(state, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return state


def parse_ts(value: Any) -> datetime | None:
    if not value:
        return None
    try:
        dt = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except ValueError:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def market(row: dict[str, Any]) -> str:
    return str(row.get("market") or "")


def side(row: dict[str, Any]) -> str:
    return str(row.get("side") or "")


def net(row: dict[str, Any]) -> float:
    return float(row.get("net_gross_cents_after_entry_fee") or row.get("net_cents") or 0.0)


def source_counts(rows: list[dict[str, Any]]) -> dict[str, int]:
    return dict(Counter(source(row) for row in rows))


def reconstructed_share(rows: list[dict[str, Any]]) -> float | None:
    counts = source_counts(rows)
    total = sum(counts.values())
    if total <= 0:
        return None
    return (total - int(counts.get("approved_entry") or 0)) / total


def exit_rows_after(source_path: Path, freeze_ts: str) -> dict[tuple[str, str], list[dict[str, Any]]]:
    freeze_dt = parse_ts(freeze_ts)
    grouped: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    payload = load_json(source_path)
    for row in payload.get("rows") or []:
        row_dt = parse_ts(row.get("exit_ts") or row.get("entry_ts"))
        if freeze_dt is not None and row_dt is not None and row_dt < freeze_dt:
            continue
        grouped[(market(row), side(row))].append(row)
    return grouped


def candidate_cents(row: dict[str, Any]) -> float:
    return float(row.get("candidate_cents") or row.get("candidate_net_cents") or 0.0)


def current_cents(row: dict[str, Any]) -> float:
    return float(row.get("current_cents") or row.get("current_net_cents") or 0.0)


def evaluate_rule(
    lane: str,
    exit_source: str,
    all_rows: list[dict[str, Any]],
    denominator: int,
    rule_name: str,
    rule: dict[str, Any],
    exits: dict[tuple[str, str], list[dict[str, Any]]],
) -> dict[str, Any]:
    selected = best_per_market([row for row in all_rows if passes(row, rule)])
    entry_summary = summarize(selected, denominator)
    joined: list[dict[str, Any]] = []
    ambiguous = 0
    unmatched = 0
    for row in selected:
        matches = exits.get((market(row), side(row))) or []
        entry_ts_set = {item.get("entry_ts") for item in matches if item.get("entry_ts")}
        if len(entry_ts_set) > 1:
            ambiguous += 1
            continue
        if not matches:
            unmatched += 1
            continue
        exit_row = matches[0]
        joined.append({
            "market": market(row),
            "side": side(row),
            "source": source(row),
            "entry_net_cents": net(row),
            "exit_current_cents": current_cents(exit_row),
            "exit_candidate_cents": candidate_cents(exit_row),
            "exit_delta_cents": candidate_cents(exit_row) - current_cents(exit_row),
            "entry_ts": exit_row.get("entry_ts"),
            "exit_reason": exit_row.get("exit_reason"),
            "suppressed": exit_row.get("suppressed"),
        })
    joined_exit_net = sum(row["exit_candidate_cents"] for row in joined)
    joined_current_net = sum(row["exit_current_cents"] for row in joined)
    share = reconstructed_share(selected)
    blockers = []
    settled = int(as_float(entry_summary.get("settled")) or 0)
    coverage = as_float(entry_summary.get("coverage_pct"))
    entry_net = as_float(entry_summary.get("net_cents")) or 0.0
    if settled < MIN_SETTLED:
        blockers.append("entry_settled_lt_30")
    if coverage is None or coverage < COVERAGE_FLOOR:
        blockers.append("entry_coverage_too_low")
    if entry_net <= 0:
        blockers.append("entry_net_not_positive")
    if share is not None and share > MAX_RECONSTRUCTED_SHARE:
        blockers.append("entry_reconstructed_share_gt_35pct")
    if int(max(0.0, entry_net) // 100.0) < MIN_FULL_LOSS_CUSHION:
        blockers.append("entry_full_loss_cushion_lt_3")
    if len(joined) < MIN_JOINED_EXIT_ROWS:
        blockers.append("joined_exit_rows_lt_30")
    if joined_exit_net <= 0:
        blockers.append("joined_exit_net_not_positive")
    if int(max(0.0, joined_exit_net) // 100.0) < MIN_FULL_LOSS_CUSHION:
        blockers.append("joined_exit_full_loss_cushion_lt_3")
    return {
        "lane": lane,
        "exit_source": exit_source,
        "rule": rule_name,
        "candidate": f"{lane}_{rule_name}_{exit_source}_exit",
        "entry_summary": entry_summary,
        "source_counts": source_counts(selected),
        "reconstructed_share": share,
        "joined_exit_rows": len(joined),
        "joined_exit_current_cents": joined_current_net,
        "joined_exit_candidate_cents": joined_exit_net,
        "joined_exit_delta_cents": joined_exit_net - joined_current_net,
        "ambiguous_join_rows": ambiguous,
        "unmatched_selected_rows": unmatched,
        "joined_rows": joined,
        "blockers": blockers,
        "live_ready": not blockers,
    }


def evaluate_lane(
    label: str,
    exit_source: str,
    freeze_ts: str,
    surface: tuple[list[dict[str, Any]], Any, Any],
    exits: dict[tuple[str, str], list[dict[str, Any]]],
) -> dict[str, Any]:
    all_rows, _, denominator = surface
    variants = [
        evaluate_rule(label, exit_source, all_rows, int(denominator or 0), name, rule, exits)
        for name, rule in SOFT_RULES.items()
    ]
    variants.sort(
        key=lambda row: (
            len(row.get("blockers") or []),
            -float(row.get("joined_exit_candidate_cents") or -999999.0),
            -float((row.get("entry_summary") or {}).get("net_cents") or -999999.0),
        )
    )
    return {
        "lane": label,
        "exit_source": exit_source,
        "freeze_ts_utc": freeze_ts,
        "future_denominator": int(denominator or 0),
        "variants": variants,
    }


def interpretation(lanes: list[dict[str, Any]]) -> list[str]:
    notes = []
    for lane in lanes:
        best = (lane.get("variants") or [{}])[0]
        summary = best.get("entry_summary") or {}
        notes.append(
            f"{lane.get('lane')} {lane.get('exit_source')} best {best.get('rule')} has entry settled {summary.get('settled')}, "
            f"coverage {summary.get('coverage_pct')}%, entry net {summary.get('net_cents')}c, "
            f"joined exit rows {best.get('joined_exit_rows')}, joined exit net {best.get('joined_exit_candidate_cents')}c, "
            f"blockers {best.get('blockers')}."
        )
    return notes


def build_report() -> dict[str, Any]:
    state = load_or_create_state()
    freeze_ts = str(state["freeze_ts_utc"])
    surfaces = {
        "post_soft_stack_entry": entry_surfaces(freeze_ts),
        "post_soft_stack_bridge": bridge_surfaces(freeze_ts),
    }
    lanes = []
    exit_rows_available: dict[str, int] = {}
    for exit_source, path in EXIT_SOURCES.items():
        exits = exit_rows_after(path, freeze_ts)
        exit_rows_available[exit_source] = sum(len(rows) for rows in exits.values())
        lanes.extend([
            evaluate_lane("post_soft_stack_entry", exit_source, freeze_ts, surfaces["post_soft_stack_entry"], exits),
            evaluate_lane("post_soft_stack_bridge", exit_source, freeze_ts, surfaces["post_soft_stack_bridge"], exits),
        ])
    return {
        "generated_at_utc": utc_now_iso(),
        "freeze": state,
        "exit_sources": {name: str(path) for name, path in EXIT_SOURCES.items()},
        "exit_rows_available": exit_rows_available,
        "lanes": lanes,
        "candidate_live_ready": any(
            bool(variant.get("live_ready"))
            for lane in lanes
            for variant in lane.get("variants") or []
        ),
        "interpretation": interpretation(lanes),
    }


def fmt(value: Any) -> str:
    if value is None:
        return "None"
    if isinstance(value, float):
        return f"{value:.6f}"
    return str(value)


def write_md(report: dict[str, Any]) -> None:
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8")
    freeze = report.get("freeze") or {}
    lines = [
        "# v28 Frozen Feature-Gate Soft-Frontier + Guarded Exit Stack",
        "",
        "Research-only frozen forward watch. No live bot changes.",
        "",
        f"- Generated UTC: `{report.get('generated_at_utc')}`",
        f"- Freeze timestamp UTC: `{freeze.get('freeze_ts_utc')}`",
        f"- Candidate family: `{freeze.get('candidate_family')}`",
        f"- Exit rows available after freeze: `{report.get('exit_rows_available')}`",
        f"- Any live-ready variant: `{report.get('candidate_live_ready')}`",
        "",
        "## Interpretation",
        "",
    ]
    for note in report.get("interpretation") or []:
        lines.append(f"- {note}")
    for lane in report.get("lanes") or []:
        lines.extend(["", f"## {lane.get('lane')} / {lane.get('exit_source')}", ""])
        lines.extend([
            "| rank | rule | entry settled | W/L | coverage | entry net | recon share | joined exit rows | joined exit net | joined delta | unmatched | ambiguous | blockers |",
            "|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|",
        ])
        for idx, row in enumerate(lane.get("variants") or [], start=1):
            summary = row.get("entry_summary") or {}
            lines.append(
                f"| {idx} | `{row.get('rule')}` | {summary.get('settled')} | "
                f"{summary.get('wins')}/{summary.get('losses')} | {fmt(summary.get('coverage_pct'))} | "
                f"{fmt(summary.get('net_cents'))} | {fmt(row.get('reconstructed_share'))} | "
                f"{row.get('joined_exit_rows')} | {fmt(row.get('joined_exit_candidate_cents'))} | "
                f"{fmt(row.get('joined_exit_delta_cents'))} | {row.get('unmatched_selected_rows')} | "
                f"{row.get('ambiguous_join_rows')} | {', '.join(row.get('blockers') or []) or 'none'} |"
            )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    report = build_report()
    write_md(report)
    print(str(OUT_MD))


if __name__ == "__main__":
    main()
