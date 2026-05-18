"""Parent-fill repair child for the v28 top-component stack.

Research-only; no live bot changes or orders.

The false-negative exit-rescue child repairs the approved-entry clipped-winner
losses, leaving a smaller rejected-actionable parent-fill loss pocket. This
probe layers source-risk sizing on only those parent-fill rows to test whether
the broad 75% stack can keep coverage while reducing entry/FV/source damage.
Diagnostic rows are mechanism discovery only; this probe owns a fresh freeze
clock for strict evidence.
"""
from __future__ import annotations

import json
import math
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

from probe_v28_top_component_false_negative_rescue_child import (
    PARENT_LABEL,
    RULES as EXIT_CHILD_RULES,
    base_selected_cents,
    choose_parent,
    fnum,
    has_exit_marks,
    live_cents,
    row_weight,
    source,
)
from probe_v28_top_component_mix_portfolio import compose, strict_parent_hold_rows, strict_rescue_rows


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
TOP_COMPONENT_JSON = OUT_DIR / "v28_top_component_mix_portfolio_latest.json"
STATE_JSON = OUT_DIR / "v28_top_component_parent_fill_repair_child_state.json"
OUT_JSON = OUT_DIR / "v28_top_component_parent_fill_repair_child_latest.json"
OUT_MD = OUT_DIR / "v28_top_component_parent_fill_repair_child_latest.md"

EXIT_CHILD_RULE = "diagnostic_approved_union_rebound"
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


def load_or_create_state() -> dict[str, Any]:
    state = load_json(STATE_JSON)
    if state.get("freeze_ts_utc"):
        return state
    state = {
        "freeze_ts_utc": utc_now_iso(),
        "candidate_family": "top_component_parent_fill_repair_child",
        "parent_candidate": PARENT_LABEL,
        "exit_child_rule": EXIT_CHILD_RULE,
        "note": "Freeze created after false-negative child left rejected-actionable parent-fill losses. Pre-freeze rows are diagnostic only.",
    }
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    STATE_JSON.write_text(json.dumps(state, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return state


def is_parent_fill(row: dict[str, Any]) -> bool:
    return str(row.get("component") or "").startswith("parent_midprice")


def apply_exit_child(row: dict[str, Any]) -> dict[str, Any]:
    rule = EXIT_CHILD_RULES[EXIT_CHILD_RULE]
    item = dict(row)
    original = base_selected_cents(row)
    candidate = original
    rescue = False
    if has_exit_marks(row) and rule(row):
        candidate = fnum(row.get("hold_cents"))
        rescue = True
    weight = row_weight(row)
    weighted = weight * candidate
    item.update(
        {
            "exit_child_rescue": rescue,
            "exit_child_selected_cents": candidate,
            "exit_child_weighted_cents": weighted,
            "exit_child_delta_cents": weighted - fnum(row.get("selected_weighted_cents")),
        }
    )
    return item


def in_mid_confidence_pocket(row: dict[str, Any]) -> bool:
    if not is_parent_fill(row) or source(row) == "approved_entry":
        return False
    return in_observable_mid_confidence_pocket(row)


def in_observable_mid_confidence_pocket(row: dict[str, Any]) -> bool:
    if not is_parent_fill(row):
        return False
    abs_d = fnum(row.get("abs_d_sigma"), math.nan)
    ask = fnum(row.get("ask_prob"), math.nan)
    return math.isfinite(abs_d) and math.isfinite(ask) and 0.60 <= abs_d <= 0.75 and ask <= 0.65


def smooth_source_risk_scale(row: dict[str, Any]) -> float:
    if not is_parent_fill(row) or source(row) == "approved_entry":
        return 1.0
    abs_d = fnum(row.get("abs_d_sigma"), math.nan)
    ask = fnum(row.get("ask_prob"), math.nan)
    if not math.isfinite(abs_d) or not math.isfinite(ask):
        return 0.50
    abs_conf = max(0.0, min(1.0, (abs_d - 0.55) / 0.70))
    ask_conf = max(0.0, min(1.0, (ask - 0.40) / 0.55))
    confidence = 0.5 * abs_conf + 0.5 * ask_conf
    return max(0.25, min(1.0, 0.25 + 0.75 * confidence))


def triangular_notch(value: float, center: float, width: float) -> float:
    if not math.isfinite(value):
        return 0.0
    return max(0.0, min(1.0, 1.0 - abs(value - center) / width))


def parent_fill_mid_absd_ask_notch_scale(row: dict[str, Any]) -> float:
    if not is_parent_fill(row):
        return 1.0
    abs_d = fnum(row.get("abs_d_sigma"), math.nan)
    ask = fnum(row.get("ask_prob"), math.nan)
    if not math.isfinite(abs_d) or not math.isfinite(ask):
        return 0.50
    abs_risk = triangular_notch(abs_d, 0.73, 0.16)
    ask_risk = max(0.0, min(1.0, (0.75 - ask) / 0.40))
    return max(0.25, min(1.0, 1.0 - 0.75 * abs_risk * ask_risk))


def parent_fill_wide_mid_absd_ask_notch_scale(row: dict[str, Any]) -> float:
    if not is_parent_fill(row):
        return 1.0
    abs_d = fnum(row.get("abs_d_sigma"), math.nan)
    ask = fnum(row.get("ask_prob"), math.nan)
    if not math.isfinite(abs_d) or not math.isfinite(ask):
        return 0.50
    abs_risk = triangular_notch(abs_d, 0.73, 0.22)
    ask_risk = max(0.0, min(1.0, (0.85 - ask) / 0.50))
    return max(0.25, min(1.0, 1.0 - 0.75 * abs_risk * ask_risk))


SIZING_RULES: dict[str, Callable[[dict[str, Any]], float]] = {
    "diagnostic_exit_child_only_control": lambda row: 1.0,
    "diagnostic_parent_fill_all_rejected_half": lambda row: 0.50
    if is_parent_fill(row) and source(row) != "approved_entry"
    else 1.0,
    "diagnostic_parent_fill_all_rejected_quarter": lambda row: 0.25
    if is_parent_fill(row) and source(row) != "approved_entry"
    else 1.0,
    "diagnostic_mid_confidence_parent_fill_half": lambda row: 0.50 if in_mid_confidence_pocket(row) else 1.0,
    "diagnostic_mid_confidence_parent_fill_quarter": lambda row: 0.25 if in_mid_confidence_pocket(row) else 1.0,
    "diagnostic_observable_mid_confidence_parent_fill_half": lambda row: 0.50
    if in_observable_mid_confidence_pocket(row)
    else 1.0,
    "diagnostic_observable_mid_confidence_parent_fill_quarter": lambda row: 0.25
    if in_observable_mid_confidence_pocket(row)
    else 1.0,
    "diagnostic_smooth_parent_fill_source_risk": smooth_source_risk_scale,
    "diagnostic_parent_fill_mid_absd_ask_notch": parent_fill_mid_absd_ask_notch_scale,
    "diagnostic_parent_fill_wide_mid_absd_ask_notch": parent_fill_wide_mid_absd_ask_notch_scale,
}


def strict_rows_for_child(freeze_ts: str) -> tuple[list[dict[str, Any]], int, dict[str, Any]]:
    parent_rows, denominator, diagnostics = strict_parent_hold_rows(freeze_ts)
    all_rows, exit_rows = strict_rescue_rows(parent_rows)
    rows = compose(exit_rows, parent_rows, "observable_absd_ranked_fill", 75.0, denominator)
    diagnostics = dict(diagnostics)
    diagnostics.update(
        {
            "settled_parent_rows_with_exit_clock": len(exit_rows),
            "settled_parent_rows_without_exit_clock": max(0, len(parent_rows) - len(exit_rows)),
            "strict_absd_fill_rows": len(rows),
        }
    )
    return rows, denominator, diagnostics


def score_variant(label: str, rows: list[dict[str, Any]], denominator: int, strict_forward: bool) -> dict[str, Any]:
    scale_rule = SIZING_RULES[label]
    scored = []
    shrunk = []
    exit_rescued = []
    for row in rows:
        item = apply_exit_child(row)
        scale = scale_rule(item)
        base_weighted = fnum(item.get("exit_child_weighted_cents"))
        final_weighted = base_weighted * scale
        item.update(
            {
                "parent_fill_scale": scale,
                "final_weighted_cents": final_weighted,
                "parent_fill_shrink_delta_cents": final_weighted - base_weighted,
            }
        )
        if scale < 0.999:
            shrunk.append(item)
        if item.get("exit_child_rescue"):
            exit_rescued.append(item)
        scored.append(item)

    net = sum(fnum(row.get("final_weighted_cents")) for row in scored)
    wins = sum(1 for row in scored if fnum(row.get("final_weighted_cents")) > 0)
    losses = sum(1 for row in scored if fnum(row.get("final_weighted_cents")) < 0)
    counts = Counter(source(row) for row in scored)
    reconstructed = len(scored) - int(counts.get("approved_entry") or 0)
    recon_share = reconstructed / len(scored) if scored else None
    source_gate_row_margin = int(math.floor(MAX_RECONSTRUCTED_SHARE * len(scored))) - reconstructed if scored else None
    coverage = 100.0 * len(scored) / denominator if denominator else None
    live = live_cents()
    blockers: list[str] = []
    if not strict_forward:
        blockers.append("diagnostic_prefreeze")
    if (
        "all_rejected" in label
        or label in {"diagnostic_mid_confidence_parent_fill_half", "diagnostic_mid_confidence_parent_fill_quarter"}
        or "source_risk" in label
    ):
        blockers.append("source_label_diagnostic")
    if len(scored) < MIN_SETTLED:
        blockers.append("settled_lt_30")
    if coverage is None or coverage < TARGET_COVERAGE_MIN:
        blockers.append("coverage_too_low")
    if coverage is not None and coverage > TARGET_COVERAGE_MAX:
        blockers.append("coverage_too_high")
    if recon_share is not None and recon_share > MAX_RECONSTRUCTED_SHARE:
        blockers.append("row_reconstructed_share_gt_35pct")
    elif source_gate_row_margin is not None and source_gate_row_margin <= 0:
        blockers.append("source_gate_zero_row_margin")
    if net <= 0:
        blockers.append("net_not_positive")
    if int(max(0.0, net) // 100.0) < MIN_FULL_LOSS_CUSHION:
        blockers.append("full_loss_cushion_lt_3")
    if net <= live:
        blockers.append("does_not_beat_refreshed_live_baseline")

    parent_rows = [row for row in scored if is_parent_fill(row)]
    shrunk_net_delta = sum(fnum(row.get("parent_fill_shrink_delta_cents")) for row in shrunk)
    return {
        "label": label.replace("diagnostic_", "post_parent_fill_child_birth_" if strict_forward else "diagnostic_"),
        "rule": label,
        "strict_forward": strict_forward,
        "entries": len(scored),
        "settled": len(scored),
        "wins": wins,
        "losses": losses,
        "coverage_pct": coverage,
        "net_cents": net,
        "delta_vs_live_cents": net - live,
        "reconstructed_share": recon_share,
        "source_gate_row_margin": source_gate_row_margin,
        "source_counts": dict(counts),
        "full_loss_cushion": int(max(0.0, net) // 100.0),
        "exit_child_rescues": len(exit_rescued),
        "exit_child_delta_cents": sum(fnum(row.get("exit_child_delta_cents")) for row in scored),
        "parent_fill_rows": len(parent_rows),
        "parent_fill_net_cents": sum(fnum(row.get("final_weighted_cents")) for row in parent_rows),
        "shrunk_parent_fill_rows": len(shrunk),
        "parent_fill_shrink_delta_cents": shrunk_net_delta,
        "blockers": blockers,
        "rows": scored,
        "worst_rows": sorted(scored, key=lambda row: fnum(row.get("final_weighted_cents")))[:14],
        "shrunk_examples": sorted(shrunk, key=lambda row: fnum(row.get("parent_fill_shrink_delta_cents")), reverse=True)[:14],
    }


def runway_for_variant(row: dict[str, Any], denominator: int, diagnostics: dict[str, Any]) -> dict[str, Any]:
    entries = int(row.get("entries") or 0)
    settled = int(row.get("settled") or 0)
    net = fnum(row.get("net_cents"))
    source_counts = row.get("source_counts") if isinstance(row.get("source_counts"), dict) else {}
    approved = int(source_counts.get("approved_entry") or 0)
    reconstructed = max(0, entries - approved)
    target_entries = int(math.ceil(TARGET_COVERAGE_MIN / 100.0 * denominator)) if denominator else 0
    pending = [item for item in diagnostics.get("pending_parent_examples") or [] if isinstance(item, dict)]
    pending_source_counts = Counter(source(item) for item in pending)
    clean_rows_needed_for_source = 0
    if entries:
        clean_rows_needed_for_source = max(0, int(math.ceil(reconstructed / MAX_RECONSTRUCTED_SHARE - entries)))
    live = live_cents()
    return {
        "candidate": row.get("label"),
        "target_entries_for_75pct": target_entries,
        "coverage_entries_needed": max(0, target_entries - entries),
        "settled_rows_needed_for_sample": max(0, MIN_SETTLED - settled),
        "approved_rows_needed_for_source_gate_if_no_more_rejected": clean_rows_needed_for_source,
        "net_cents_needed_to_beat_live": max(0.0, live - net + 1.0),
        "net_cents_needed_for_cushion3": max(0.0, MIN_FULL_LOSS_CUSHION * 100.0 - net),
        "exit_clock_joined_rows": int(diagnostics.get("settled_parent_rows_with_exit_clock") or 0),
        "exit_clock_joined_rows_needed_for_mechanism_sample": max(
            0,
            MIN_SETTLED - int(diagnostics.get("settled_parent_rows_with_exit_clock") or 0),
        ),
        "pending_rows": len(pending),
        "pending_source_counts": dict(pending_source_counts),
    }


def build_report() -> dict[str, Any]:
    state = load_or_create_state()
    payload = load_json(TOP_COMPONENT_JSON)
    denominator = int(payload.get("denominator") or 0)
    parent = choose_parent(payload, PARENT_LABEL)
    parent_rows = [row for row in parent.get("rows") or [] if isinstance(row, dict)]
    freeze_ts = str(state.get("freeze_ts_utc"))
    strict_rows, strict_denominator, strict_diagnostics = strict_rows_for_child(freeze_ts)
    diagnostic = [score_variant(label, parent_rows, denominator, False) for label in SIZING_RULES]
    strict = [score_variant(label, strict_rows, strict_denominator, True) for label in SIZING_RULES]
    variants = diagnostic + strict
    variants.sort(
        key=lambda row: (
            len([b for b in row.get("blockers") or [] if b != "diagnostic_prefreeze"]),
            -fnum(row.get("net_cents"), -999999.0),
        )
    )
    best_diag = next((row for row in variants if not row.get("strict_forward")), {})
    strict_ranked = sorted(
        strict,
        key=lambda row: (
            len(row.get("blockers") or []),
            -fnum(row.get("net_cents"), -999999.0),
        ),
    )
    best_strict = strict_ranked[0] if strict_ranked else {}
    strict_runway = runway_for_variant(best_strict, strict_denominator, strict_diagnostics) if best_strict else {}
    return {
        "generated_at_utc": utc_now_iso(),
        "state": state,
        "source_report": str(TOP_COMPONENT_JSON),
        "parent_report_utc": payload.get("generated_at_utc"),
        "parent_label": parent.get("label"),
        "parent_net_cents": parent.get("net_cents"),
        "parent_wins": parent.get("wins"),
        "parent_losses": parent.get("losses"),
        "exit_child_rule": EXIT_CHILD_RULE,
        "denominator": denominator,
        "strict_denominator": strict_denominator,
        "strict_scoreable_rows_from_child_freeze": len(strict_rows),
        "strict_forward_diagnostics": strict_diagnostics,
        "strict_runway": strict_runway,
        "diagnostic_variants": diagnostic,
        "strict_variants": strict,
        "variants": variants,
        "interpretation": [
            "Research-only parent-fill repair child; no live bot changes or orders.",
            (
                f"Best diagnostic child {best_diag.get('label')} scores "
                f"{best_diag.get('net_cents')}c with W/L {best_diag.get('wins')}/{best_diag.get('losses')} "
                f"and {best_diag.get('shrunk_parent_fill_rows')} shrunk parent-fill rows."
            ) if best_diag else "No diagnostic child scored.",
            "This tests whether rejected-actionable parent-fill exposure should be confidence-sized after the approved-entry exit rescue.",
            f"Child freeze UTC is {state.get('freeze_ts_utc')}; strict rows from this child freeze are the only promotion evidence.",
        ],
    }


def fmt(value: Any) -> str:
    if value is None:
        return "n/a"
    if isinstance(value, float):
        return f"{value:.3f}"
    return str(value)


def write_md(report: dict[str, Any]) -> None:
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8")
    lines = [
        "# v28 Top-Component Parent-Fill Repair Child",
        "",
        "Research-only; no live bot changes or orders.",
        "",
        f"- Generated UTC: `{report.get('generated_at_utc')}`",
        f"- Child freeze UTC: `{(report.get('state') or {}).get('freeze_ts_utc')}`",
        f"- Parent: `{report.get('parent_label')}` `{fmt(report.get('parent_net_cents'))}c` `{report.get('parent_wins')}/{report.get('parent_losses')}`",
        f"- Exit child rule layered first: `{report.get('exit_child_rule')}`",
        f"- Strict scoreable rows from child freeze: `{report.get('strict_scoreable_rows_from_child_freeze')}`",
        "",
        "## Interpretation",
        "",
    ]
    lines.extend(f"- {note}" for note in report.get("interpretation") or [])
    strict_diag = report.get("strict_forward_diagnostics") if isinstance(report.get("strict_forward_diagnostics"), dict) else {}
    lines.extend(
        [
            "",
            "## Strict Runway",
            "",
            f"- Future denominator: `{strict_diag.get('future_denominator')}`",
            f"- Future observation rows: `{strict_diag.get('future_observation_rows')}`",
            f"- Broad pass rows: `{strict_diag.get('broad_pass_rows')}`",
            f"- Selected parent rows: `{strict_diag.get('selected_parent_rows')}`",
            f"- Settled selected rows: `{strict_diag.get('selected_settled_rows')}`",
            f"- Pending selected rows: `{strict_diag.get('selected_pending_rows')}`",
            f"- Settled selected rows with exit-clock join: `{strict_diag.get('settled_parent_rows_with_exit_clock')}`",
            f"- Strict absd-fill rows: `{strict_diag.get('strict_absd_fill_rows')}`",
        ]
    )
    runway = report.get("strict_runway") if isinstance(report.get("strict_runway"), dict) else {}
    if runway:
        lines.extend(
            [
                "",
                "### Gate Runway",
                "",
                f"- Closest strict candidate: `{runway.get('candidate')}`",
                f"- Entries needed for 75% coverage at current denominator: `{runway.get('coverage_entries_needed')}`",
                f"- Settled rows needed for 30-row sample: `{runway.get('settled_rows_needed_for_sample')}`",
                f"- Approved rows needed for source gate if no more rejected rows are added: `{runway.get('approved_rows_needed_for_source_gate_if_no_more_rejected')}`",
                f"- Net cents needed to beat refreshed live baseline: `{fmt(runway.get('net_cents_needed_to_beat_live'))}`",
                f"- Net cents needed for 3 full-loss cushion: `{fmt(runway.get('net_cents_needed_for_cushion3'))}`",
                f"- Exit-clock joined rows needed for mechanism sample: `{runway.get('exit_clock_joined_rows_needed_for_mechanism_sample')}`",
                f"- Pending source counts: `{runway.get('pending_source_counts')}`",
            ]
        )
    pending = strict_diag.get("pending_parent_examples") or []
    if pending:
        lines.extend(
            [
                "",
                "### Pending Parent Rows",
                "",
                "| market | side | source | raw edge | recross | abs d | ask | weight |",
                "|---|---|---|---:|---:|---:|---:|---:|",
            ]
        )
        for row in pending:
            if not isinstance(row, dict):
                continue
            lines.append(
                f"| {row.get('market')} | {row.get('side')} | {row.get('source')} | "
                f"{fmt(row.get('raw_edge'))} | {fmt(row.get('recross_hazard_score'))} | "
                f"{fmt(row.get('abs_d_sigma'))} | {fmt(row.get('ask_prob'))} | {fmt(row.get('weight'))} |"
            )
    near_misses = strict_diag.get("near_miss_examples") or []
    if near_misses:
        lines.extend(
            [
                "",
                "### Strict Near Misses",
                "",
                "| market | side | source | pass count | missing | raw edge | recross | abs d | ask |",
                "|---|---|---|---:|---|---:|---:|---:|---:|",
            ]
        )
        for row in near_misses[:8]:
            if not isinstance(row, dict):
                continue
            missing = ",".join(str(part) for part in row.get("broad_missing") or [])
            lines.append(
                f"| {row.get('market')} | {row.get('side')} | {row.get('source')} | "
                f"{row.get('broad_pass_count')} | {missing} | {fmt(row.get('raw_edge'))} | "
                f"{fmt(row.get('recross_hazard_score'))} | {fmt(row.get('abs_d_sigma'))} | {fmt(row.get('ask_prob'))} |"
            )
    lines.extend(
        [
            "",
            "## Variants",
            "",
            "| label | settled | W/L | coverage | net | delta live | recon | src margin | cushion | exit rescues/delta | parent fill rows/net | shrunk rows/delta | blockers |",
            "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|",
        ]
    )
    for row in report.get("variants") or []:
        lines.append(
            f"| `{row.get('label')}` | {row.get('settled')} | {row.get('wins')}/{row.get('losses')} | "
            f"{fmt(row.get('coverage_pct'))}% | {fmt(row.get('net_cents'))} | {fmt(row.get('delta_vs_live_cents'))} | "
            f"{fmt(row.get('reconstructed_share'))} | {row.get('source_gate_row_margin')} | {row.get('full_loss_cushion')} | "
            f"{row.get('exit_child_rescues')}/{fmt(row.get('exit_child_delta_cents'))} | "
            f"{row.get('parent_fill_rows')}/{fmt(row.get('parent_fill_net_cents'))} | "
            f"{row.get('shrunk_parent_fill_rows')}/{fmt(row.get('parent_fill_shrink_delta_cents'))} | "
            f"{', '.join(row.get('blockers') or [])} |"
        )
    best = (report.get("variants") or [{}])[0]
    lines.extend(
        [
            "",
            "## Best Variant Worst Rows",
            "",
            "| market | side | source | component | final | scale | raw edge | abs d | ask | recross |",
            "|---|---|---|---|---:|---:|---:|---:|---:|---:|",
        ]
    )
    for row in best.get("worst_rows") or []:
        lines.append(
            f"| {row.get('market')} | {row.get('side')} | {source(row)} | {row.get('component')} | "
            f"{fmt(row.get('final_weighted_cents'))} | {fmt(row.get('parent_fill_scale'))} | "
            f"{fmt(row.get('raw_edge'))} | {fmt(row.get('abs_d_sigma'))} | {fmt(row.get('ask_prob'))} | "
            f"{fmt(row.get('recross_hazard_score'))} |"
        )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    report = build_report()
    write_md(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
