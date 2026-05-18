"""Feature-gate core/expansion mix watch for v28.

Research-only; no live bot changes or orders.

This probe tests whether the clean high-win ask65 bridge can serve as a core
lane while the broader raw03 bridge is treated as a reduced-size expansion
layer. The intent is to test a physical mix/match idea:

- expensive/high-confirmation entries are cleaner and can carry normal size;
- cheap-tail or reconstructed expansion rows add coverage but should be
  exposure-shrunk until approved-source forward evidence improves.

The probe uses already-frozen post-feature-freeze rows only.
"""
from __future__ import annotations

import json
import math
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
SOURCE_JSON = OUT_DIR / "v28_boundary_clock_feature_gate_candidate_latest.json"
OUT_JSON = OUT_DIR / "v28_feature_gate_core_expansion_mix_latest.json"
OUT_MD = OUT_DIR / "v28_feature_gate_core_expansion_mix_latest.md"

BROAD_LANE = "post_feature_freeze_bridge"
BROAD_CANDIDATE = "post_feature_freeze_bridge_raw03_recross70_abs075"
CORE_CANDIDATE = "post_feature_freeze_bridge_raw05_recross60_abs085_ask65"
TARGET_COVERAGE_MIN = 75.0
TARGET_COVERAGE_MAX = 90.0
SOURCE_SHARE_MAX = 0.35
MIN_SETTLED = 30
MIN_CUSHION = 3


def load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
    return payload if isinstance(payload, dict) else {}


def is_reconstructed(row: dict[str, Any]) -> bool:
    source = str(row.get("source") or "").lower()
    return source != "approved_entry"


def row_key(row: dict[str, Any]) -> tuple[str, str]:
    return str(row.get("market") or ""), str(row.get("side") or "")


def get_variant(payload: dict[str, Any], lane_name: str, candidate: str) -> dict[str, Any]:
    for lane in payload.get("lanes") or []:
        if not isinstance(lane, dict) or lane.get("lane") != lane_name:
            continue
        for variant in lane.get("variants") or []:
            if isinstance(variant, dict) and variant.get("candidate") == candidate:
                return variant
    return {}


def ask_prob(row: dict[str, Any]) -> float:
    try:
        return float(row.get("ask_prob"))
    except (TypeError, ValueError):
        return 0.0


def raw_edge(row: dict[str, Any]) -> float:
    try:
        return float(row.get("raw_edge"))
    except (TypeError, ValueError):
        return 0.0


def recross(row: dict[str, Any]) -> float:
    try:
        return float(row.get("recross_hazard_score"))
    except (TypeError, ValueError):
        return 1.0


def net_cents(row: dict[str, Any]) -> float:
    try:
        return float(row.get("net_cents"))
    except (TypeError, ValueError):
        return 0.0


def expansion_class(row: dict[str, Any], core_keys: set[tuple[str, str]]) -> str:
    if row_key(row) in core_keys:
        return "core"
    tags: list[str] = []
    if is_reconstructed(row):
        tags.append("source_fragile")
    if ask_prob(row) < 0.15:
        tags.append("cheap_tail")
    if raw_edge(row) < 0.05:
        tags.append("thin_raw_edge")
    if recross(row) > 0.30:
        tags.append("recross_risk")
    return "+".join(tags) if tags else "approved_expansion"


def policy_weight(policy: str, row: dict[str, Any], core_keys: set[tuple[str, str]]) -> float:
    in_core = row_key(row) in core_keys
    if policy == "core_only":
        return 1.0 if in_core else 0.0
    if in_core:
        return 1.0
    source_fragile = is_reconstructed(row)
    cheap_tail = ask_prob(row) < 0.15
    thin_edge = raw_edge(row) < 0.05
    recross_risk = recross(row) > 0.30

    if policy == "broad_full_control":
        return 1.0
    if policy == "expansion_half":
        return 0.5
    if policy == "expansion_quarter":
        return 0.25
    if policy == "approved_expansion_full_reconstructed_quarter":
        return 0.25 if source_fragile else 1.0
    if policy == "cheap_tail_quarter_else_half":
        return 0.25 if cheap_tail else 0.5
    if policy == "source_or_cheap_quarter_else_half":
        return 0.25 if (source_fragile or cheap_tail) else 0.5
    if policy == "skip_thin_cheap_else_half":
        return 0.0 if (cheap_tail and thin_edge) else 0.5
    if policy == "skip_source_thin_cheap_else_half":
        return 0.0 if (source_fragile and cheap_tail and thin_edge) else 0.5
    if policy == "continuous_ask_scaled_expansion":
        # Cheap options are lottery-like; scale expansion notional smoothly up
        # to normal half-size as ask approaches the clean ask65 core floor.
        return max(0.10, min(0.50, ask_prob(row) / 1.30))
    if policy == "continuous_quality_scaled_expansion":
        weight = 0.50
        if source_fragile:
            weight *= 0.50
        if cheap_tail:
            weight *= 0.50
        if thin_edge:
            weight *= 0.50
        if recross_risk:
            weight *= 0.50
        return max(0.0625, weight)
    return 0.0


def summarize_policy(
    policy: str,
    rows: list[dict[str, Any]],
    denominator: float,
    core_keys: set[tuple[str, str]],
) -> dict[str, Any]:
    selected: list[dict[str, Any]] = []
    settled_rows: list[dict[str, Any]] = []
    weighted_net = 0.0
    weight_sum = 0.0
    source_weight = 0.0
    wins = 0
    losses = 0
    class_counts: Counter[str] = Counter()
    class_weight: Counter[str] = Counter()
    class_net: Counter[str] = Counter()

    for row in rows:
        weight = policy_weight(policy, row, core_keys)
        if weight <= 0:
            continue
        row_net = net_cents(row)
        selected.append(row)
        weight_sum += weight
        if is_reconstructed(row):
            source_weight += weight
        if isinstance(row.get("side_won"), bool):
            settled_rows.append(row)
            weighted_net += weight * row_net
            if row_net > 0:
                wins += 1
            elif row_net < 0:
                losses += 1
        cls = expansion_class(row, core_keys)
        class_counts[cls] += 1
        class_weight[cls] += weight
        if isinstance(row.get("side_won"), bool):
            class_net[cls] += weight * row_net

    entries = len(selected)
    settled = len(settled_rows)
    row_source = sum(1 for row in selected if is_reconstructed(row))
    coverage = 100.0 * entries / denominator if denominator else 0.0
    row_source_share = row_source / entries if entries else 0.0
    exposure_source_share = source_weight / weight_sum if weight_sum else 0.0
    cushion = math.floor(weighted_net / 100.0) if weighted_net > 0 else 0
    blockers: list[str] = []
    coverage_entries_needed = max(0, math.ceil(TARGET_COVERAGE_MIN * denominator / 100.0 - entries))
    settled_rows_needed = max(0, MIN_SETTLED - settled)
    clean_rows_needed_for_source = 0
    while entries + clean_rows_needed_for_source > 0 and (
        row_source / (entries + clean_rows_needed_for_source)
    ) > SOURCE_SHARE_MAX:
        clean_rows_needed_for_source += 1
    net_cents_needed_for_cushion3 = max(0.0, 300.0 - weighted_net)
    if settled < MIN_SETTLED:
        blockers.append("settled_lt_30")
    if not (TARGET_COVERAGE_MIN <= coverage <= TARGET_COVERAGE_MAX):
        blockers.append("coverage_outside_target")
    if row_source_share > SOURCE_SHARE_MAX:
        blockers.append("row_source_share_gt_35pct")
    if exposure_source_share > SOURCE_SHARE_MAX:
        blockers.append("exposure_source_share_gt_35pct")
    if weighted_net <= 0:
        blockers.append("weighted_net_not_positive")
    if cushion < MIN_CUSHION:
        blockers.append("weighted_full_loss_cushion_lt_3")

    return {
        "policy": policy,
        "entries": entries,
        "settled": settled,
        "wins": wins,
        "losses": losses,
        "coverage_pct": coverage,
        "weighted_net_cents": weighted_net,
        "avg_weighted_net_cents": weighted_net / settled if settled else 0.0,
        "weight_sum": weight_sum,
        "row_source_share": row_source_share,
        "exposure_source_share": exposure_source_share,
        "full_loss_cushion": cushion,
        "coverage_entries_needed": coverage_entries_needed,
        "settled_rows_needed": settled_rows_needed,
        "clean_rows_needed_for_source": clean_rows_needed_for_source,
        "net_cents_needed_for_cushion3": net_cents_needed_for_cushion3,
        "blockers": blockers,
        "live_ready": not blockers,
        "class_counts": dict(class_counts),
        "class_weight": dict(class_weight),
        "class_weighted_net_cents": dict(class_net),
    }


def fmt_cents(value: Any) -> str:
    try:
        cents = float(value)
    except (TypeError, ValueError):
        return "n/a"
    return f"{cents:.1f}c (${cents / 100.0:.2f})"


def write_md(report: dict[str, Any]) -> None:
    lines: list[str] = [
        "# v28 Feature-Gate Core/Expansion Mix",
        "",
        "Research-only mix/match probe. No live bot changes or orders.",
        "",
        f"- Generated UTC: `{report.get('generated_at_utc')}`",
        f"- Source generated UTC: `{report.get('source_generated_at_utc')}`",
        f"- Lane: `{BROAD_LANE}`",
        f"- Core: `{CORE_CANDIDATE}`",
        f"- Broad expansion parent: `{BROAD_CANDIDATE}`",
        f"- Any live-ready mix row: `{report.get('any_live_ready')}`",
        f"- Best policy: `{(report.get('rows') or [{}])[0].get('policy')}`",
        "",
        "## Mix Rows",
        "",
        "| rank | policy | entries | settled | W/L | coverage | weighted net | row source | exposure source | cushion | rows needed | live ready | blockers |",
        "|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|---|",
    ]
    for idx, row in enumerate(report.get("rows") or [], start=1):
        lines.append(
            f"| {idx} | `{row.get('policy')}` | {row.get('entries')} | {row.get('settled')} | {row.get('wins')}/{row.get('losses')} | "
            f"{row.get('coverage_pct'):.1f}% | {fmt_cents(row.get('weighted_net_cents'))} | "
            f"{row.get('row_source_share'):.1%} | {row.get('exposure_source_share'):.1%} | "
            f"{row.get('full_loss_cushion')} | "
            f"cov {row.get('coverage_entries_needed')}/settle {row.get('settled_rows_needed')}/clean {row.get('clean_rows_needed_for_source')}/cushion {row.get('net_cents_needed_for_cushion3'):.1f}c | "
            f"{row.get('live_ready')} | "
            f"{', '.join(row.get('blockers') or []) or 'none'} |"
        )
    best = (report.get("rows") or [{}])[0]
    lines.extend([
        "",
        "## Best Policy Class Attribution",
        "",
        f"- Policy: `{best.get('policy')}`",
        f"- Class counts: `{best.get('class_counts')}`",
        f"- Class weights: `{best.get('class_weight')}`",
        f"- Class weighted net: `{best.get('class_weighted_net_cents')}`",
        "",
        "## Interpretation",
        "",
        "- Full-size broad coverage now has enough settled rows, but source share and full-loss cushion still block promotion.",
        "- Fractional expansion can reduce notional/source exposure, but official promotion still needs row-source quality unless the gate is explicitly changed.",
        "- Treat any live_ready=False row as watch-only, even if weighted net improves.",
    ])
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    payload = load_json(SOURCE_JSON)
    broad = get_variant(payload, BROAD_LANE, BROAD_CANDIDATE)
    core = get_variant(payload, BROAD_LANE, CORE_CANDIDATE)
    broad_rows = [row for row in broad.get("rows") or [] if isinstance(row, dict)]
    core_rows = [row for row in core.get("rows") or [] if isinstance(row, dict)]
    core_keys = {row_key(row) for row in core_rows}
    broad_summary = broad.get("candidate_summary") or {}
    denominator = float(broad_summary.get("entries") or 0)
    coverage = float((broad.get("candidate_summary") or {}).get("coverage_pct") or 0.0)
    if denominator and coverage:
        denominator = denominator * 100.0 / coverage

    policies = [
        "broad_full_control",
        "core_only",
        "expansion_half",
        "expansion_quarter",
        "approved_expansion_full_reconstructed_quarter",
        "cheap_tail_quarter_else_half",
        "source_or_cheap_quarter_else_half",
        "skip_thin_cheap_else_half",
        "skip_source_thin_cheap_else_half",
        "continuous_ask_scaled_expansion",
        "continuous_quality_scaled_expansion",
    ]
    rows = [summarize_policy(policy, broad_rows, denominator, core_keys) for policy in policies]
    rows.sort(
        key=lambda row: (
            bool(row.get("live_ready")),
            float(row.get("weighted_net_cents") or 0.0),
            -len(row.get("blockers") or []),
        ),
        reverse=True,
    )

    report = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "source": str(SOURCE_JSON),
        "source_generated_at_utc": payload.get("generated_at_utc"),
        "lane": BROAD_LANE,
        "core_candidate": CORE_CANDIDATE,
        "broad_candidate": BROAD_CANDIDATE,
        "denominator": denominator,
        "broad_summary": broad.get("candidate_summary"),
        "core_summary": core.get("candidate_summary"),
        "any_live_ready": any(row.get("live_ready") for row in rows),
        "rows": rows,
    }
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_md(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
