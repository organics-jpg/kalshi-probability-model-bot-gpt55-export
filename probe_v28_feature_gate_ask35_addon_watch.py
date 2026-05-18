"""Frozen watch for ask35 plus a mid-price/high-edge omitted-row add-on.

Research-only; no live bot changes or orders. The add-on was discovered from
the ask35 omitted-row split, so it must start a new forward clock before it can
matter.
"""
from __future__ import annotations

import json
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from probe_v28_coverage_repair_pool_diagnostic import COVERAGE_FLOOR, raw_edge, row_net_after_fee, summarize
from probe_v28_frozen_boundary_clock_fv_entry_bridge import future_surfaces as bridge_surfaces
from probe_v28_frozen_boundary_clock_repair_entry import future_surfaces as entry_surfaces


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
STATE_JSON = OUT_DIR / "v28_feature_gate_ask35_addon_watch_state.json"
OUT_JSON = OUT_DIR / "v28_feature_gate_ask35_addon_watch_latest.json"
OUT_MD = OUT_DIR / "v28_feature_gate_ask35_addon_watch_latest.md"

MIN_SETTLED = 30
MAX_RECONSTRUCTED_SHARE = 0.35
MIN_FULL_LOSS_CUSHION = 3


BASE_ASK35 = {
    "raw_edge_min": 0.03,
    "recross_max": 0.60,
    "abs_d_min": 0.85,
    "ask_min": 0.35,
}

ADDON_MIDPRICE_HIGH_EDGE = {
    "raw_edge_min": 0.10,
    "ask_min": 0.40,
    "abs_d_max": 0.85,
}


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
        "candidate_family": "feature_gate_ask35_addon_watch",
        "origin": "Ask35 frontier omitted-row split; diagnostic add-on requires own post-birth evidence.",
        "base_rule": BASE_ASK35,
        "addon_rule": ADDON_MIDPRICE_HIGH_EDGE,
    }
    STATE_JSON.write_text(json.dumps(state, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return state


def as_float(value: Any) -> float | None:
    try:
        if value is None or value == "":
            return None
        return float(value)
    except (TypeError, ValueError):
        return None


def market(row: dict[str, Any]) -> str:
    return str(row.get("market") or "")


def source(row: dict[str, Any]) -> str:
    return str(row.get("source") or "unknown")


def net(row: dict[str, Any]) -> float:
    return float(row_net_after_fee(row) or 0.0)


def recross(row: dict[str, Any]) -> float | None:
    return as_float(row.get("recross_hazard_score"))


def ask(row: dict[str, Any]) -> float | None:
    return as_float(row.get("ask_prob"))


def abs_d(row: dict[str, Any]) -> float | None:
    return as_float(row.get("abs_d_sigma"))


def passes_base(row: dict[str, Any]) -> bool:
    edge = raw_edge(row)
    row_recross = recross(row)
    row_abs_d = abs_d(row)
    row_ask = ask(row)
    if edge is None or row_recross is None or row_abs_d is None or row_ask is None:
        return False
    return (
        edge >= BASE_ASK35["raw_edge_min"]
        and row_recross <= BASE_ASK35["recross_max"]
        and row_abs_d >= BASE_ASK35["abs_d_min"]
        and row_ask >= BASE_ASK35["ask_min"]
    )


def passes_addon(row: dict[str, Any]) -> bool:
    edge = raw_edge(row)
    row_abs_d = abs_d(row)
    row_ask = ask(row)
    if edge is None or row_abs_d is None or row_ask is None:
        return False
    return (
        edge >= ADDON_MIDPRICE_HIGH_EDGE["raw_edge_min"]
        and row_ask >= ADDON_MIDPRICE_HIGH_EDGE["ask_min"]
        and row_abs_d < ADDON_MIDPRICE_HIGH_EDGE["abs_d_max"]
    )


def best_per_market(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        if market(row):
            grouped[market(row)].append(row)
    return [max(items, key=lambda row: raw_edge(row) or -999.0) for items in grouped.values()]


def source_counts(rows: list[dict[str, Any]]) -> dict[str, int]:
    return dict(Counter(source(row) for row in rows))


def reconstructed_share(counts: dict[str, int]) -> float | None:
    total = sum(counts.values())
    if total <= 0:
        return None
    return (total - int(counts.get("approved_entry") or 0)) / total


def blockers(summary: dict[str, Any], share: float | None) -> list[str]:
    out: list[str] = []
    settled = int(as_float(summary.get("settled")) or 0)
    coverage = as_float(summary.get("coverage_pct"))
    net_cents = as_float(summary.get("net_cents"))
    cushion = int(max(0.0, float(net_cents or 0.0)) // 100.0)
    if settled < MIN_SETTLED:
        out.append("settled_lt_30")
    if coverage is None or coverage < COVERAGE_FLOOR:
        out.append("coverage_too_low")
    if net_cents is None or net_cents <= 0:
        out.append("net_not_positive")
    if share is not None and share > MAX_RECONSTRUCTED_SHARE:
        out.append("reconstructed_share_gt_35pct")
    if cushion < MIN_FULL_LOSS_CUSHION:
        out.append("full_loss_cushion_lt_3")
    return out


def evaluate(label: str, freeze_ts: str, surfaces_fn: Any) -> dict[str, Any]:
    rows, _, denominator = surfaces_fn(freeze_ts)
    selected_base = best_per_market([row for row in rows if passes_base(row)])
    selected_combo = best_per_market([row for row in rows if passes_base(row) or passes_addon(row)])
    selected_addon_only = [
        row
        for row in selected_combo
        if passes_addon(row) and not passes_base(row)
    ]
    variants = []
    for name, selected in [
        ("base_ask35", selected_base),
        ("ask35_plus_midprice_high_edge_addon", selected_combo),
        ("addon_only_component", selected_addon_only),
    ]:
        summary = summarize(selected, denominator)
        counts = source_counts(selected)
        share = reconstructed_share(counts)
        variants.append(
            {
                "candidate": f"{label}_{name}",
                "summary": summary,
                "source_counts": counts,
                "reconstructed_share": share,
                "full_loss_cushion_estimate": int(max(0.0, float(summary.get("net_cents") or 0.0)) // 100.0),
                "blockers": blockers(summary, share),
                "rows": [
                    {
                        "market": market(row),
                        "side": row.get("side"),
                        "source": source(row),
                        "side_won": row.get("side_won"),
                        "net_cents": net(row),
                        "raw_edge": raw_edge(row),
                        "recross_hazard_score": row.get("recross_hazard_score"),
                        "abs_d_sigma": row.get("abs_d_sigma"),
                        "ask_prob": row.get("ask_prob"),
                        "component": "addon" if passes_addon(row) and not passes_base(row) else "base",
                    }
                    for row in selected
                ],
            }
        )
    return {
        "lane": label,
        "freeze_ts": freeze_ts,
        "future_denominator": denominator,
        "variants": variants,
    }


def build_report() -> dict[str, Any]:
    state = load_or_create_state()
    freeze_ts = str(state["freeze_ts_utc"])
    lanes = [
        evaluate("post_addon_watch_entry", freeze_ts, entry_surfaces),
        evaluate("post_addon_watch_bridge", freeze_ts, bridge_surfaces),
    ]
    notes = [
        "This watch starts from its own freeze timestamp; pre-freeze omitted-split strength is diagnostic only.",
    ]
    for lane in lanes:
        best = lane["variants"][1]
        addon = lane["variants"][2]
        summary = best["summary"]
        addon_summary = addon["summary"]
        notes.append(
            f"{lane.get('lane')}: combo settled {summary.get('settled')}, coverage {summary.get('coverage_pct')}%, "
            f"net {summary.get('net_cents')}c, recon {best.get('reconstructed_share')}, blockers {best.get('blockers')}; "
            f"addon-only settled {addon_summary.get('settled')}, net {addon_summary.get('net_cents')}c."
        )
    return {
        "generated_at_utc": utc_now_iso(),
        "state": state,
        "lanes": lanes,
        "interpretation": notes,
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
    state = report.get("state") or {}
    lines = [
        "# v28 Feature-Gate Ask35 Add-On Watch",
        "",
        "Research-only; frozen watch, no live bot logic changes or orders.",
        "",
        f"- Generated UTC: `{report.get('generated_at_utc')}`",
        f"- Freeze UTC: `{state.get('freeze_ts_utc')}`",
        f"- Base rule: `{state.get('base_rule')}`",
        f"- Add-on rule: `{state.get('addon_rule')}`",
        "",
        "## Interpretation",
        "",
    ]
    for note in report.get("interpretation") or []:
        lines.append(f"- {note}")
    for lane in report.get("lanes") or []:
        lines.extend(
            [
                "",
                f"## {lane.get('lane')}",
                "",
                f"- Future denominator: `{lane.get('future_denominator')}`",
                "",
                "| candidate | settled | W/L | coverage | net c | recon | source counts | cushion | blockers |",
                "|---|---:|---:|---:|---:|---:|---|---:|---|",
            ]
        )
        for row in lane.get("variants") or []:
            summary = row.get("summary") or {}
            lines.append(
                f"| `{row.get('candidate')}` | {summary.get('settled')} | {summary.get('wins')}/{summary.get('losses')} | "
                f"{fmt(summary.get('coverage_pct'))} | {fmt(summary.get('net_cents'))} | "
                f"{fmt(row.get('reconstructed_share'))} | `{row.get('source_counts')}` | "
                f"{row.get('full_loss_cushion_estimate')} | {', '.join(row.get('blockers') or []) or 'none'} |"
            )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    report = build_report()
    write_md(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
