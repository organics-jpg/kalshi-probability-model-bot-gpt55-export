"""Observable quarantine child for the v28 top-component parent-fill pocket.

Research-only; no live bot changes or orders.

The latest strict-row autopsy shows the weakest top-component failures as
parent-fill/no-exit-clock rows with low ask and weak boundary distance. This
probe tests source-free observable shrink/quarantine rules around that pocket.
Rows before this probe's own freeze are diagnostic context only.
"""
from __future__ import annotations

import json
import math
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

from probe_v28_top_component_parent_fill_repair_child import (
    PARENT_LABEL,
    apply_exit_child,
    fnum,
    is_parent_fill,
    live_cents,
    source,
    strict_rows_for_child,
)


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
PARENT_CHILD_JSON = OUT_DIR / "v28_top_component_parent_fill_repair_child_latest.json"
AUTOPSY_JSON = OUT_DIR / "v28_top_component_strict_row_autopsy_latest.json"
STATE_JSON = OUT_DIR / "v28_top_component_observable_quarantine_child_state.json"
OUT_JSON = OUT_DIR / "v28_top_component_observable_quarantine_child_latest.json"
OUT_MD = OUT_DIR / "v28_top_component_observable_quarantine_child_latest.md"

MAX_RECONSTRUCTED_SHARE = 0.35
MIN_SETTLED = 30
MIN_FULL_LOSS_CUSHION = 3
TARGET_COVERAGE_MIN = 75.0
TARGET_COVERAGE_MAX = 90.0


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


def write_json(path: Path, payload: dict[str, Any]) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def load_or_create_state() -> dict[str, Any]:
    state = load_json(STATE_JSON)
    if state.get("freeze_ts_utc"):
        return state
    state = {
        "freeze_ts_utc": utc_now_iso(),
        "candidate_family": "top_component_observable_quarantine_child",
        "parent_candidate": PARENT_LABEL,
        "note": (
            "Freeze created after strict-row autopsy found low-ask/weak-boundary "
            "parent-fill losses. Pre-freeze/autopsy rows are diagnostic only."
        ),
    }
    write_json(STATE_JSON, state)
    return state


def feature(row: dict[str, Any], key: str) -> float:
    return fnum(row.get(key), math.nan)


def weak_touch(row: dict[str, Any]) -> bool:
    abs_d = feature(row, "abs_d_sigma")
    ask = feature(row, "ask_prob")
    return math.isfinite(abs_d) and math.isfinite(ask) and abs_d <= 0.75 and ask <= 0.65


def very_weak_touch(row: dict[str, Any]) -> bool:
    abs_d = feature(row, "abs_d_sigma")
    ask = feature(row, "ask_prob")
    return math.isfinite(abs_d) and math.isfinite(ask) and abs_d <= 0.70 and ask <= 0.60


def low_ask(row: dict[str, Any]) -> bool:
    ask = feature(row, "ask_prob")
    return math.isfinite(ask) and ask <= 0.65


def weak_boundary(row: dict[str, Any]) -> bool:
    abs_d = feature(row, "abs_d_sigma")
    return math.isfinite(abs_d) and abs_d <= 0.75


def smooth_weak_touch_scale(row: dict[str, Any]) -> float:
    if not observable_parent_fill(row):
        return 1.0
    abs_d = feature(row, "abs_d_sigma")
    ask = feature(row, "ask_prob")
    if not math.isfinite(abs_d) or not math.isfinite(ask):
        return 0.50
    abs_conf = max(0.0, min(1.0, (abs_d - 0.55) / 0.35))
    ask_conf = max(0.0, min(1.0, (ask - 0.40) / 0.35))
    confidence = 0.5 * abs_conf + 0.5 * ask_conf
    return max(0.25, min(1.0, 0.25 + 0.75 * confidence))


def observable_parent_fill(row: dict[str, Any]) -> bool:
    component = str(row.get("component") or "")
    return is_parent_fill(row) or component.startswith("strict_parent_midprice")


Rule = Callable[[dict[str, Any]], float]


RULES: dict[str, Rule] = {
    "observable_quarantine_control": lambda row: 1.0,
    "weak_touch_quarter": lambda row: 0.25 if observable_parent_fill(row) and weak_touch(row) else 1.0,
    "weak_touch_half": lambda row: 0.50 if observable_parent_fill(row) and weak_touch(row) else 1.0,
    "weak_touch_zero": lambda row: 0.0 if observable_parent_fill(row) and weak_touch(row) else 1.0,
    "very_weak_touch_zero": lambda row: 0.0 if observable_parent_fill(row) and very_weak_touch(row) else 1.0,
    "low_ask_quarter": lambda row: 0.25 if observable_parent_fill(row) and low_ask(row) else 1.0,
    "weak_boundary_quarter": lambda row: 0.25 if observable_parent_fill(row) and weak_boundary(row) else 1.0,
    "smooth_weak_touch": smooth_weak_touch_scale,
}


def base_row_cents(row: dict[str, Any]) -> float:
    if "pnl_cents" in row:
        return fnum(row.get("pnl_cents"))
    return fnum(row.get("final_weighted_cents"), fnum(row.get("selected_weighted_cents"), fnum(row.get("weighted_net_cents"))))


def prepare_parent_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    prepared = []
    for row in rows:
        if not isinstance(row, dict):
            continue
        item = apply_exit_child(row)
        item["base_weighted_cents"] = fnum(item.get("final_weighted_cents"), fnum(item.get("exit_child_weighted_cents")))
        prepared.append(item)
    return prepared


def prepare_autopsy_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    prepared = []
    for row in rows:
        if not isinstance(row, dict):
            continue
        item = dict(row)
        item["base_weighted_cents"] = base_row_cents(item)
        prepared.append(item)
    return prepared


def score_rows(label: str, rows: list[dict[str, Any]], denominator: int, strict_forward: bool, diagnostic_context: bool) -> dict[str, Any]:
    rule = RULES[label]
    scored = []
    affected = []
    zeroed = []
    for row in rows:
        item = dict(row)
        base = fnum(item.get("base_weighted_cents"), base_row_cents(item))
        scale = rule(item)
        final = base * scale
        item.update(
            {
                "observable_quarantine_scale": scale,
                "base_weighted_cents": base,
                "final_weighted_cents": final,
                "observable_quarantine_delta_cents": final - base,
                "weak_touch": weak_touch(item),
                "very_weak_touch": very_weak_touch(item),
                "low_ask": low_ask(item),
                "weak_boundary": weak_boundary(item),
            }
        )
        if scale < 0.999:
            affected.append(item)
        if scale <= 0.0:
            zeroed.append(item)
        scored.append(item)

    active = [row for row in scored if fnum(row.get("observable_quarantine_scale")) > 0.0]
    entries = len(active)
    net = sum(fnum(row.get("final_weighted_cents")) for row in active)
    wins = sum(1 for row in active if fnum(row.get("final_weighted_cents")) > 0)
    losses = sum(1 for row in active if fnum(row.get("final_weighted_cents")) < 0)
    counts = Counter(source(row) for row in active)
    reconstructed = entries - int(counts.get("approved_entry") or 0)
    recon_share = reconstructed / entries if entries else None
    coverage = 100.0 * entries / denominator if denominator else None
    source_margin = int(math.floor(MAX_RECONSTRUCTED_SHARE * entries)) - reconstructed if entries else None
    live = live_cents()
    worst_loss = min([fnum(row.get("final_weighted_cents")) for row in active], default=0.0)
    full_loss_cushion = int(max(0.0, net) // max(1.0, abs(worst_loss))) if worst_loss < 0 else int(max(0.0, net) // 100.0)
    blockers: list[str] = []
    if diagnostic_context:
        blockers.append("diagnostic_or_prefreeze_context")
    if not strict_forward:
        blockers.append("not_strict_forward")
    if entries < MIN_SETTLED:
        blockers.append("settled_lt_30")
    if coverage is None or coverage < TARGET_COVERAGE_MIN:
        blockers.append("coverage_too_low")
    if coverage is not None and coverage > TARGET_COVERAGE_MAX:
        blockers.append("coverage_too_high")
    if recon_share is not None and recon_share > MAX_RECONSTRUCTED_SHARE:
        blockers.append("row_reconstructed_share_gt_35pct")
    elif source_margin is not None and source_margin <= 0:
        blockers.append("source_gate_zero_row_margin")
    if net <= 0:
        blockers.append("net_not_positive")
    if full_loss_cushion < MIN_FULL_LOSS_CUSHION:
        blockers.append("full_loss_cushion_lt_3")
    if net <= live:
        blockers.append("does_not_beat_refreshed_live_baseline")
    if zeroed:
        blockers.append("zero_size_changes_coverage")

    affected_net_before = sum(fnum(row.get("base_weighted_cents")) for row in affected)
    affected_net_after = sum(fnum(row.get("final_weighted_cents")) for row in affected if fnum(row.get("observable_quarantine_scale")) > 0.0)
    return {
        "label": label,
        "strict_forward": strict_forward,
        "diagnostic_context": diagnostic_context,
        "entries": entries,
        "settled": entries,
        "wins": wins,
        "losses": losses,
        "coverage_pct": coverage,
        "net_cents": net,
        "delta_vs_live_cents": net - live,
        "reconstructed_share": recon_share,
        "source_gate_row_margin": source_margin,
        "source_counts": dict(counts),
        "full_loss_cushion": full_loss_cushion,
        "affected_rows": len(affected),
        "zeroed_rows": len(zeroed),
        "affected_net_before_cents": affected_net_before,
        "affected_net_after_cents": affected_net_after,
        "affected_delta_cents": affected_net_after - affected_net_before,
        "blockers": blockers,
        "worst_rows": sorted(active, key=lambda row: fnum(row.get("final_weighted_cents")))[:10],
        "affected_examples": sorted(affected, key=lambda row: fnum(row.get("observable_quarantine_delta_cents")), reverse=True)[:10],
    }


def best_parent_variant(payload: dict[str, Any]) -> dict[str, Any]:
    variants = [row for row in payload.get("diagnostic_variants") or [] if isinstance(row, dict)]
    variants.sort(key=lambda row: fnum(row.get("net_cents"), -999999.0), reverse=True)
    return variants[0] if variants else {}


def build_report() -> dict[str, Any]:
    state = load_or_create_state()
    parent_payload = load_json(PARENT_CHILD_JSON)
    autopsy_payload = load_json(AUTOPSY_JSON)
    parent_best = best_parent_variant(parent_payload)
    parent_rows = prepare_parent_rows([row for row in parent_best.get("rows") or [] if isinstance(row, dict)])
    parent_denominator = int(parent_payload.get("denominator") or len(parent_rows) or 0)
    autopsy_rows = prepare_autopsy_rows([row for row in autopsy_payload.get("rows") or [] if isinstance(row, dict)])
    autopsy_denominator = int(autopsy_payload.get("strict_unique_rows") or len(autopsy_rows) or 0)

    own_strict_rows, own_strict_denominator, own_strict_diagnostics = strict_rows_for_child(str(state.get("freeze_ts_utc")))
    own_strict_rows = prepare_parent_rows(own_strict_rows)

    diagnostic = [score_rows(label, parent_rows, parent_denominator, False, True) for label in RULES]
    autopsy_context = [score_rows(label, autopsy_rows, autopsy_denominator, False, True) for label in RULES]
    strict = [score_rows(label, own_strict_rows, own_strict_denominator, True, False) for label in RULES]
    return {
        "generated_at_utc": utc_now_iso(),
        "state": state,
        "parent_source": str(PARENT_CHILD_JSON),
        "autopsy_source": str(AUTOPSY_JSON),
        "parent_base_label": parent_best.get("label"),
        "parent_base_net_cents": parent_best.get("net_cents"),
        "parent_base_entries": parent_best.get("entries"),
        "parent_base_coverage_pct": parent_best.get("coverage_pct"),
        "parent_base_reconstructed_share": parent_best.get("reconstructed_share"),
        "diagnostic_denominator": parent_denominator,
        "autopsy_context_denominator": autopsy_denominator,
        "own_strict_denominator": own_strict_denominator,
        "own_strict_diagnostics": own_strict_diagnostics,
        "diagnostic": sorted(diagnostic, key=lambda row: fnum(row.get("net_cents"), -999999.0), reverse=True),
        "autopsy_context": sorted(autopsy_context, key=lambda row: fnum(row.get("net_cents"), -999999.0), reverse=True),
        "strict": sorted(strict, key=lambda row: fnum(row.get("net_cents"), -999999.0), reverse=True),
        "interpretation": [
            "Research-only observable quarantine child; no live bot changes or orders.",
            "The rule family uses only observable ask/abs-distance geometry; source labels are audit-only.",
            "Diagnostic/autopsy rows are pre-birth context because the child was created after seeing the strict failures.",
            "Own strict rows from this child freeze are the only future promotion evidence.",
        ],
    }


def fmt(value: Any, digits: int = 1) -> str:
    if value is None:
        return ""
    try:
        return f"{float(value):.{digits}f}"
    except (TypeError, ValueError):
        return str(value)


def money(value: Any) -> str:
    cents = fnum(value)
    return f"{cents:.0f}c (${cents / 100.0:.2f})"


def table(rows: list[dict[str, Any]], limit: int = 8) -> list[str]:
    lines = [
        "| rank | rule | entries | W/L | coverage | net | recon | cushion | affected | affected delta | blockers |",
        "|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---|",
    ]
    for idx, row in enumerate(rows[:limit], 1):
        blockers = ", ".join(str(part) for part in row.get("blockers") or []) or "none"
        lines.append(
            f"| {idx} | `{row.get('label')}` | {row.get('entries')} | {row.get('wins')}/{row.get('losses')} | "
            f"{fmt(row.get('coverage_pct'))}% | {money(row.get('net_cents'))} | "
            f"{fmt(100.0 * fnum(row.get('reconstructed_share')), 1)}% | {row.get('full_loss_cushion')} | "
            f"{row.get('affected_rows')} | {money(row.get('affected_delta_cents'))} | {blockers} |"
        )
    return lines


def render_markdown(report: dict[str, Any]) -> str:
    strict = report.get("strict") or []
    diag = report.get("diagnostic") or []
    autopsy = report.get("autopsy_context") or []
    lines = [
        "# v28 Top-Component Observable Quarantine Child",
        "",
        "Research-only. No live bot logic changes, no orders, no process control.",
        "",
        f"- Generated UTC: `{report.get('generated_at_utc')}`",
        f"- Child freeze UTC: `{(report.get('state') or {}).get('freeze_ts_utc')}`",
        f"- Parent diagnostic base: `{report.get('parent_base_label')}` {money(report.get('parent_base_net_cents'))}, entries `{report.get('parent_base_entries')}`, coverage `{fmt(report.get('parent_base_coverage_pct'))}%`",
        f"- Own strict denominator: `{report.get('own_strict_denominator')}`",
        "",
        "## Interpretation",
        "",
    ]
    lines.extend(f"- {note}" for note in report.get("interpretation") or [])
    best_auto = autopsy[0] if autopsy else {}
    best_diag = diag[0] if diag else {}
    best_strict = strict[0] if strict else {}
    lines.extend(
        [
            f"- Best autopsy-context rule: `{best_auto.get('label')}` {money(best_auto.get('net_cents'))}, W/L `{best_auto.get('wins')}/{best_auto.get('losses')}`, blockers `{best_auto.get('blockers')}`.",
            f"- Best diagnostic rule: `{best_diag.get('label')}` {money(best_diag.get('net_cents'))}, W/L `{best_diag.get('wins')}/{best_diag.get('losses')}`, coverage `{fmt(best_diag.get('coverage_pct'))}%`.",
            f"- Best own-strict rule: `{best_strict.get('label')}` {money(best_strict.get('net_cents'))}, W/L `{best_strict.get('wins')}/{best_strict.get('losses')}`, blockers `{best_strict.get('blockers')}`.",
            "",
            "## Diagnostic Parent Rows",
            "",
        ]
    )
    lines.extend(table(diag))
    lines.extend(["", "## Strict Autopsy Context", ""])
    lines.extend(table(autopsy))
    lines.extend(["", "## Own Strict Post-Birth Watch", ""])
    lines.extend(table(strict))
    lines.extend(["", "## Own Strict Diagnostics", ""])
    strict_diag = report.get("own_strict_diagnostics") if isinstance(report.get("own_strict_diagnostics"), dict) else {}
    for key in [
        "future_denominator",
        "future_observation_rows",
        "broad_pass_rows",
        "selected_parent_rows",
        "selected_settled_rows",
        "selected_pending_rows",
        "settled_parent_rows_with_exit_clock",
        "strict_absd_fill_rows",
    ]:
        lines.append(f"- `{key}`: `{strict_diag.get(key)}`")
    lines.append("")
    return "\n".join(lines)


def main() -> None:
    report = build_report()
    write_json(OUT_JSON, report)
    OUT_MD.write_text(render_markdown(report), encoding="utf-8")
    print(OUT_MD)


if __name__ == "__main__":
    main()
