"""Dual-lane overlap portfolio probe for v28 candidates.

Research-only; no live bot changes or orders.

This asks whether the highest-PnL broad-ish post-freeze lanes and the highest
win-rate sidecar lanes are complementary enough to justify tracking as a dual
strategy. It uses only row-level shadow/research ledgers and treats results as
diagnostic until a combined lane is frozen from its own timestamp.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
CONTINUOUS_PENALTY_JSON = OUT_DIR / "v28_boundary_clock_feature_gate_continuous_penalty_latest.json"
MIDPRICE_SHRINK_JSON = OUT_DIR / "v28_soft_frontier_midprice_boundary_shrink_latest.json"
FEATURE_LEDGER_JSON = OUT_DIR / "v28_boundary_clock_feature_gate_row_ledger_latest.json"
SOURCE_BLOCKER_JSON = OUT_DIR / "v28_feature_gate_source_blocker_mechanism_latest.json"
FALSE_CONVICTION_BRIDGE_JSON = OUT_DIR / "v28_false_conviction_fv_entry_bridge_latest.json"
TOP_COMPONENT_MIX_JSON = OUT_DIR / "v28_top_component_mix_portfolio_latest.json"
TOP_COMPONENT_PARENT_CHILD_JSON = OUT_DIR / "v28_top_component_parent_fill_repair_child_latest.json"
TRACKER_JSON = OUT_DIR / "v28_candidate_pnl_tracker_latest.json"
OUT_JSON = OUT_DIR / "v28_dual_lane_overlap_portfolio_latest.json"
OUT_MD = OUT_DIR / "v28_dual_lane_overlap_portfolio_latest.md"


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


def as_float(value: Any) -> float | None:
    if value is None or value == "":
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def net(row: dict[str, Any]) -> float:
    for field in (
        "weighted_net_cents",
        "final_weighted_cents",
        "selected_weighted_cents",
        "net_cents",
        "raw_net_cents",
        "candidate_cents",
    ):
        value = as_float(row.get(field))
        if value is not None:
            return value
    return 0.0


def row_key(row: dict[str, Any]) -> tuple[str, str]:
    return (str(row.get("market") or ""), str(row.get("side") or ""))


def market_key(row: dict[str, Any]) -> str:
    return str(row.get("market") or "")


def source_is_clean(row: dict[str, Any]) -> bool:
    return str(row.get("source") or "") == "approved_entry"


def summarize_rows(rows: list[dict[str, Any]], denominator: int | None = None) -> dict[str, Any]:
    total = sum(net(row) for row in rows)
    entries = len(rows)
    settled_rows = [row for row in rows if as_float(row.get("net_cents")) is not None or as_float(row.get("weighted_net_cents")) is not None]
    denom = denominator or entries
    losses = sum(1 for row in settled_rows if net(row) < 0)
    wins = sum(1 for row in settled_rows if net(row) > 0)
    clean = sum(1 for row in rows if source_is_clean(row))
    return {
        "entries": entries,
        "settled": len(settled_rows),
        "wins": wins,
        "losses": losses,
        "net_cents": total,
        "avg_net_cents": total / entries if entries else 0.0,
        "coverage_pct": (entries / denom * 100.0) if denom else None,
        "reconstructed_share": (1.0 - clean / entries) if entries else None,
        "full_loss_cushion": int(max(0.0, total) // 100.0),
        "worst_loss_cents": min((net(row) for row in settled_rows), default=0.0),
    }


def normalize_rows(rows: list[dict[str, Any]], lane: str, policy: str, weight_field: str | None = None) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for row in rows:
        if not isinstance(row, dict) or not row.get("market"):
            continue
        clone = dict(row)
        clone["lane"] = lane
        clone["policy"] = policy
        if weight_field and as_float(clone.get(weight_field)) is not None:
            clone["weighted_net_cents"] = as_float(clone.get(weight_field))
        elif as_float(clone.get("weighted_net_cents")) is None:
            clone["weighted_net_cents"] = net(clone)
        out.append(clone)
    return out


def continuous_penalty_lanes(payload: dict[str, Any]) -> list[dict[str, Any]]:
    lanes: list[dict[str, Any]] = []
    for lane in payload.get("lanes") or []:
        lane_name = lane.get("lane")
        if lane_name not in {"post_penalty_birth_entry", "post_penalty_birth_bridge"}:
            continue
        denominator = int(as_float(lane.get("future_denominator")) or 0)
        for variant in lane.get("variants") or []:
            candidate = str(variant.get("candidate") or "")
            if not candidate or not candidate.endswith("rank_only"):
                continue
            rows = normalize_rows(variant.get("rows") or [], str(lane_name), candidate)
            lanes.append({
                "lane": str(lane_name),
                "policy": candidate,
                "denominator": denominator,
                "rows": rows,
                "summary": summarize_rows(rows, denominator),
                "source": "continuous_penalty",
            })
    return lanes


def midprice_lanes(payload: dict[str, Any]) -> list[dict[str, Any]]:
    lanes: list[dict[str, Any]] = []
    for lane in payload.get("lanes") or []:
        lane_name = lane.get("lane")
        if lane_name not in {"post_feature_freeze_entry", "post_feature_freeze_bridge", "diagnostic_entry", "diagnostic_bridge"}:
            continue
        denominator = int(as_float(lane.get("future_denominator")) or 0)
        for variant in lane.get("variants") or []:
            candidate = str(variant.get("candidate") or "")
            summary = variant.get("summary") or {}
            rows = normalize_rows(summary.get("rows") or [], str(lane_name), candidate, weight_field="weighted_net_cents")
            if rows:
                lanes.append({
                    "lane": str(lane_name),
                    "policy": candidate,
                    "denominator": denominator,
                    "rows": rows,
                    "summary": summarize_rows(rows, denominator),
                    "source": "midprice_boundary_shrink",
                })
    return lanes


def feature_ledger_lanes(payload: dict[str, Any]) -> list[dict[str, Any]]:
    lanes: list[dict[str, Any]] = []
    wanted = {"raw05_recross60_abs085_ask65", "raw03_recross70_abs075", "raw05_recross60_abs085"}
    for lane in payload.get("lanes") or []:
        lane_name = lane.get("lane")
        if lane_name not in {"post_feature_freeze_entry", "post_feature_freeze_bridge"}:
            continue
        denominator = int(as_float(lane.get("future_denominator")) or 0)
        for rule in lane.get("rules") or []:
            name = str(rule.get("rule") or "")
            if name not in wanted:
                continue
            rows = normalize_rows(rule.get("selected_rows") or [], str(lane_name), name)
            lanes.append({
                "lane": str(lane_name),
                "policy": name,
                "denominator": denominator,
                "rows": rows,
                "summary": summarize_rows(rows, denominator),
                "source": "feature_gate_ledger",
            })
    return lanes


def source_blocker_lanes(payload: dict[str, Any]) -> list[dict[str, Any]]:
    lanes: list[dict[str, Any]] = []
    for lane in payload.get("lanes") or []:
        lane_name = lane.get("lane")
        if lane_name not in {"post_feature_freeze_entry", "post_feature_freeze_bridge"}:
            continue
        denominator = int(as_float(lane.get("future_denominator")) or 0)
        rows = normalize_rows((lane.get("approved_rows") or []) + (lane.get("source_rows") or []), str(lane_name), "repair_low_absd_quarter_else_half")
        if rows:
            lanes.append({
                "lane": str(lane_name),
                "policy": "repair_low_absd_quarter_else_half",
                "denominator": denominator,
                "rows": rows,
                "summary": summarize_rows(rows, denominator),
                "source": "source_blocker_mechanism",
            })
    return lanes


def false_conviction_lanes(payload: dict[str, Any]) -> list[dict[str, Any]]:
    lanes: list[dict[str, Any]] = []
    for window in payload.get("windows") or []:
        if window.get("window") != "post_freeze_candidate":
            continue
        denominator = int(as_float(window.get("future_denominator")) or 0)
        samples = window.get("selected_rows_sample") or {}
        ranked = sorted(
            [
                row for row in window.get("ranked") or []
                if isinstance(row, dict)
                and as_float(row.get("net_cents")) is not None
                and str(row.get("score_name") or "")
                in {
                    "first_eligible+strict_edge4_or_p60+continuous_recross_forget",
                    "first_eligible+escape_edge8_or_p70_or_far_edge4+false_zone_to_book",
                    "first_eligible+target_weak_turbulence_skip+raw_probability",
                }
            ],
            key=lambda row: float(row.get("net_cents") or -999999.0),
            reverse=True,
        )
        for rank in ranked:
            score_name = str(rank.get("score_name") or "")
            rows = normalize_rows(samples.get(score_name) or [], "post_freeze_candidate", score_name)
            if rows:
                lanes.append({
                    "lane": "post_freeze_candidate",
                    "policy": score_name,
                    "denominator": denominator,
                    "rows": rows,
                    "summary": summarize_rows(rows, denominator),
                    "source": "false_conviction_bridge",
                    "tracker_summary": rank,
                })
    return lanes


def top_component_lanes(payload: dict[str, Any], source_name: str) -> list[dict[str, Any]]:
    lanes: list[dict[str, Any]] = []
    if not payload:
        return lanes
    diagnostic_denominator = int(as_float(payload.get("denominator")) or 0)
    strict_denominator = int(as_float(payload.get("strict_denominator")) or diagnostic_denominator)
    for variant in payload.get("variants") or []:
        if not isinstance(variant, dict):
            continue
        label = str(variant.get("label") or "")
        rows = variant.get("rows") or []
        if not label or not isinstance(rows, list) or not rows:
            continue
        is_strict = bool(variant.get("strict_forward")) or label.startswith("post_")
        lane_name = "post_top_component_child" if is_strict else "diagnostic_top_component"
        denominator = strict_denominator if is_strict else diagnostic_denominator
        if any(as_float(row.get("final_weighted_cents")) is not None for row in rows if isinstance(row, dict)):
            weight_field = "final_weighted_cents"
        elif any(as_float(row.get("selected_weighted_cents")) is not None for row in rows if isinstance(row, dict)):
            weight_field = "selected_weighted_cents"
        else:
            weight_field = None
        normalized = normalize_rows(rows, lane_name, label, weight_field=weight_field)
        if normalized:
            lanes.append(
                {
                    "lane": lane_name,
                    "policy": label,
                    "denominator": denominator,
                    "rows": normalized,
                    "summary": summarize_rows(normalized, denominator),
                    "source": source_name,
                    "blockers": variant.get("blockers") or [],
                }
            )
    return lanes


def compact_lane(lane: dict[str, Any]) -> dict[str, Any]:
    summary = lane.get("summary") or {}
    return {
        "source": lane.get("source"),
        "lane": lane.get("lane"),
        "policy": lane.get("policy"),
        "entries": summary.get("entries"),
        "settled": summary.get("settled"),
        "wins": summary.get("wins"),
        "losses": summary.get("losses"),
        "net_cents": summary.get("net_cents"),
        "coverage_pct": summary.get("coverage_pct"),
        "reconstructed_share": summary.get("reconstructed_share"),
        "full_loss_cushion": summary.get("full_loss_cushion"),
    }


def union_portfolio(primary: dict[str, Any], sidecar: dict[str, Any]) -> dict[str, Any]:
    primary_rows = primary.get("rows") or []
    sidecar_rows = sidecar.get("rows") or []
    primary_by_market = {market_key(row): row for row in primary_rows}
    sidecar_by_market = {market_key(row): row for row in sidecar_rows}
    shared_markets = sorted(set(primary_by_market) & set(sidecar_by_market))
    sidecar_add_rows = [row for row in sidecar_rows if market_key(row) not in primary_by_market]
    primary_add_rows = [row for row in primary_rows if market_key(row) not in sidecar_by_market]
    union_rows = primary_rows + sidecar_add_rows
    denominator = max(int(primary.get("denominator") or 0), int(sidecar.get("denominator") or 0), len({market_key(row) for row in union_rows}))
    shared_same_side = 0
    shared_opposite_side = 0
    shared_net_primary = 0.0
    shared_net_sidecar = 0.0
    shared_both_loss = 0
    shared_sidecar_rescues_primary_loss = 0
    for market in shared_markets:
        left = primary_by_market[market]
        right = sidecar_by_market[market]
        if row_key(left) == row_key(right):
            shared_same_side += 1
        else:
            shared_opposite_side += 1
        left_net = net(left)
        right_net = net(right)
        shared_net_primary += left_net
        shared_net_sidecar += right_net
        if left_net < 0 and right_net < 0:
            shared_both_loss += 1
        if left_net < 0 < right_net:
            shared_sidecar_rescues_primary_loss += 1
    sidecar_add_net = sum(net(row) for row in sidecar_add_rows)
    primary_summary = primary.get("summary") or {}
    sidecar_summary = sidecar.get("summary") or {}
    union_summary = summarize_rows(union_rows, denominator)
    blockers = []
    if union_summary["settled"] < 30:
        blockers.append("settled_lt_30")
    if union_summary["net_cents"] <= 0:
        blockers.append("net_not_positive")
    if union_summary["coverage_pct"] is not None and not (75.0 <= union_summary["coverage_pct"] <= 90.0):
        blockers.append("coverage_outside_target")
    if union_summary["reconstructed_share"] is None or union_summary["reconstructed_share"] > 0.35:
        blockers.append("reconstructed_share_gt_35pct")
    if union_summary["full_loss_cushion"] < 3:
        blockers.append("full_loss_cushion_lt_3")
    blockers.append("needs_own_frozen_forward_birth")
    blockers.append("live_ready_false")
    return {
        "primary": compact_lane(primary),
        "sidecar": compact_lane(sidecar),
        "shared_markets": len(shared_markets),
        "shared_same_side": shared_same_side,
        "shared_opposite_side": shared_opposite_side,
        "shared_primary_net_cents": shared_net_primary,
        "shared_sidecar_net_cents": shared_net_sidecar,
        "shared_both_loss_count": shared_both_loss,
        "shared_sidecar_rescues_primary_loss_count": shared_sidecar_rescues_primary_loss,
        "sidecar_add_entries": len(sidecar_add_rows),
        "sidecar_add_net_cents": sidecar_add_net,
        "sidecar_add_losses": sum(1 for row in sidecar_add_rows if net(row) < 0),
        "primary_unique_entries": len(primary_add_rows),
        "primary_net_cents": primary_summary.get("net_cents"),
        "sidecar_net_cents": sidecar_summary.get("net_cents"),
        "union": union_summary,
        "blockers": blockers,
        "portfolio_score": (
            float(union_summary.get("net_cents") or 0.0)
            + 50.0 * float(union_summary.get("full_loss_cushion") or 0.0)
            - 200.0 * max(0.0, float(union_summary.get("reconstructed_share") or 1.0) - 0.35)
            - 25.0 * len(blockers)
        ),
    }


def confirmation_portfolio(primary: dict[str, Any], sidecar: dict[str, Any]) -> dict[str, Any]:
    primary_rows = primary.get("rows") or []
    sidecar_rows = sidecar.get("rows") or []
    sidecar_by_market = {market_key(row): row for row in sidecar_rows}
    confirmed_rows = [row for row in primary_rows if market_key(row) in sidecar_by_market]
    same_side_rows = [
        row for row in confirmed_rows
        if row_key(row) == row_key(sidecar_by_market[market_key(row)])
    ]
    opposite_side_rows = [
        row for row in confirmed_rows
        if row_key(row) != row_key(sidecar_by_market[market_key(row)])
    ]
    omitted_rows = [row for row in primary_rows if market_key(row) not in sidecar_by_market]
    denominator = int(primary.get("denominator") or sidecar.get("denominator") or len(primary_rows))
    confirmed_summary = summarize_rows(confirmed_rows, denominator)
    same_side_summary = summarize_rows(same_side_rows, denominator)
    omitted_summary = summarize_rows(omitted_rows, denominator)
    blockers = []
    if confirmed_summary["settled"] < 30:
        blockers.append("settled_lt_30")
    if confirmed_summary["net_cents"] <= 0:
        blockers.append("net_not_positive")
    if confirmed_summary["coverage_pct"] is not None and not (75.0 <= confirmed_summary["coverage_pct"] <= 90.0):
        blockers.append("coverage_outside_target")
    if confirmed_summary["reconstructed_share"] is None or confirmed_summary["reconstructed_share"] > 0.35:
        blockers.append("reconstructed_share_gt_35pct")
    if confirmed_summary["full_loss_cushion"] < 3:
        blockers.append("full_loss_cushion_lt_3")
    blockers.extend(["confirmation_filter_diagnostic", "needs_own_frozen_forward_birth", "live_ready_false"])
    return {
        "primary": compact_lane(primary),
        "sidecar": compact_lane(sidecar),
        "confirmed": confirmed_summary,
        "same_side": same_side_summary,
        "opposite_side_entries": len(opposite_side_rows),
        "omitted_primary": omitted_summary,
        "primary_net_cents": (primary.get("summary") or {}).get("net_cents"),
        "primary_entries": (primary.get("summary") or {}).get("entries"),
        "primary_coverage_pct": (primary.get("summary") or {}).get("coverage_pct"),
        "blockers": blockers,
        "confirmation_score": (
            float(confirmed_summary.get("net_cents") or 0.0)
            + 75.0 * float(confirmed_summary.get("full_loss_cushion") or 0.0)
            - 300.0 * max(0.0, float(confirmed_summary.get("reconstructed_share") or 1.0) - 0.35)
            - 40.0 * len(blockers)
        ),
    }


def tracker_note() -> dict[str, Any]:
    tracker = load_json(TRACKER_JSON)
    rows = tracker.get("rows") or []
    live_ready = sum(1 for row in rows if row.get("live_ready") is True)
    return {
        "tracker_rows": len(rows),
        "live_ready_rows": live_ready,
        "positive_rows": sum(1 for row in rows if (as_float(row.get("net_cents_after_entry_fee")) or 0.0) > 0.0),
    }


def build_report() -> dict[str, Any]:
    continuous = continuous_penalty_lanes(load_json(CONTINUOUS_PENALTY_JSON))
    false_conviction = false_conviction_lanes(load_json(FALSE_CONVICTION_BRIDGE_JSON))
    midprice = midprice_lanes(load_json(MIDPRICE_SHRINK_JSON))
    feature = feature_ledger_lanes(load_json(FEATURE_LEDGER_JSON))
    source_blocker = source_blocker_lanes(load_json(SOURCE_BLOCKER_JSON))
    top_component_mix = top_component_lanes(load_json(TOP_COMPONENT_MIX_JSON), "top_component_mix_portfolio")
    top_component_parent_child = top_component_lanes(
        load_json(TOP_COMPONENT_PARENT_CHILD_JSON),
        "top_component_parent_fill_repair_child",
    )

    primaries = [
        lane for lane in (top_component_parent_child + top_component_mix + midprice + feature + source_blocker)
        if (lane.get("summary") or {}).get("entries", 0) >= 25
        and (lane.get("summary") or {}).get("net_cents", 0.0) > 0
    ]
    sidecars = [
        lane for lane in (continuous + false_conviction)
        if (lane.get("summary") or {}).get("net_cents", 0.0) > 0
    ]
    portfolios = [union_portfolio(primary, sidecar) for primary in primaries for sidecar in sidecars]
    confirmations = [confirmation_portfolio(primary, sidecar) for primary in primaries for sidecar in sidecars]
    portfolios.sort(
        key=lambda row: (
            len(row.get("blockers") or []),
            -float(row.get("portfolio_score") or -999999.0),
            -float((row.get("union") or {}).get("net_cents") or -999999.0),
        )
    )
    top = portfolios[:20]
    strict_post = [
        row for row in portfolios
        if str((row.get("primary") or {}).get("lane") or "").startswith("post_")
        and str((row.get("sidecar") or {}).get("lane") or "").startswith("post_")
    ]
    strict_post.sort(
        key=lambda row: (
            len(row.get("blockers") or []),
            -float((row.get("union") or {}).get("net_cents") or -999999.0),
            -float((row.get("union") or {}).get("coverage_pct") or 0.0),
        )
    )
    confirmations.sort(
        key=lambda row: (
            len([b for b in row.get("blockers") or [] if b != "coverage_outside_target"]),
            -float(row.get("confirmation_score") or -999999.0),
            -float((row.get("confirmed") or {}).get("net_cents") or -999999.0),
        )
    )
    strict_confirmations = [
        row for row in confirmations
        if str((row.get("primary") or {}).get("lane") or "").startswith("post_")
        and str((row.get("sidecar") or {}).get("lane") or "").startswith("post_")
    ]
    return {
        "generated_at_utc": utc_now_iso(),
        "tracker_context": tracker_note(),
        "lane_counts": {
            "primaries": len(primaries),
            "sidecars": len(sidecars),
            "portfolios": len(portfolios),
        },
        "top_portfolios": top,
        "top_strict_post_portfolios": strict_post[:20],
        "top_confirmations": confirmations[:20],
        "top_strict_confirmations": strict_confirmations[:20],
        "top_primary_lanes": sorted([compact_lane(lane) for lane in primaries], key=lambda row: float(row.get("net_cents") or 0.0), reverse=True)[:15],
        "top_sidecar_lanes": sorted([compact_lane(lane) for lane in sidecars], key=lambda row: float(row.get("net_cents") or 0.0), reverse=True)[:15],
        "interpretation": interpretation(top, strict_post[:20], confirmations[:20], strict_confirmations[:20]),
    }


def interpretation(
    portfolios: list[dict[str, Any]],
    strict_post: list[dict[str, Any]] | None = None,
    confirmations: list[dict[str, Any]] | None = None,
    strict_confirmations: list[dict[str, Any]] | None = None,
) -> list[str]:
    notes = [
        "This is a diagnostic portfolio-overlap scorecard, not a promotion artifact.",
        "A dual lane must be frozen from its own timestamp before any live-readiness claim.",
    ]
    if not portfolios:
        notes.append("No row-level primary/sidecar combinations were available.")
        return notes
    best = portfolios[0]
    union = best.get("union") or {}
    notes.append(
        f"Best diagnostic union is {best['primary']['source']} / {best['primary']['policy']} plus "
        f"{best['sidecar']['policy']}: {union.get('entries')} entries, "
        f"W/L {union.get('wins')}/{union.get('losses')}, net {union.get('net_cents')}c, "
        f"coverage {union.get('coverage_pct')}%, recon {union.get('reconstructed_share')}, "
        f"blockers {best.get('blockers')}."
    )
    notes.append(
        f"The sidecar adds {best.get('sidecar_add_entries')} non-overlap rows for "
        f"{best.get('sidecar_add_net_cents')}c with {best.get('sidecar_add_losses')} losses; "
        f"shared markets {best.get('shared_markets')}."
    )
    if strict_post:
        strict = strict_post[0]
        strict_union = strict.get("union") or {}
        notes.append(
            f"Best strict/post-only union is {strict['primary']['source']} / {strict['primary']['policy']} plus "
            f"{strict['sidecar']['policy']}: {strict_union.get('entries')} entries, "
            f"W/L {strict_union.get('wins')}/{strict_union.get('losses')}, net {strict_union.get('net_cents')}c, "
            f"coverage {strict_union.get('coverage_pct')}%, recon {strict_union.get('reconstructed_share')}, "
            f"blockers {strict.get('blockers')}."
        )
    if confirmations:
        confirmed = confirmations[0]
        summary = confirmed.get("confirmed") or {}
        omitted = confirmed.get("omitted_primary") or {}
        notes.append(
            f"Best confirmation/veto test keeps {summary.get('entries')} primary rows for "
            f"{summary.get('net_cents')}c, W/L {summary.get('wins')}/{summary.get('losses')}, "
            f"coverage {summary.get('coverage_pct')}%, and omits {omitted.get('entries')} primary rows "
            f"for {omitted.get('net_cents')}c. Blockers {confirmed.get('blockers')}."
        )
    if strict_confirmations:
        strict_confirmed = strict_confirmations[0]
        summary = strict_confirmed.get("confirmed") or {}
        notes.append(
            f"Best strict/post confirmation keeps {summary.get('entries')} primary rows for "
            f"{summary.get('net_cents')}c, W/L {summary.get('wins')}/{summary.get('losses')}, "
            f"coverage {summary.get('coverage_pct')}%, blockers {strict_confirmed.get('blockers')}."
        )
    return notes


def money(value: Any) -> str:
    number = as_float(value) or 0.0
    return f"{number:.0f}c (${number / 100.0:.2f})"


def pct(value: Any) -> str:
    number = as_float(value)
    return "n/a" if number is None else f"{number * 100.0:.1f}%" if number <= 1.0 else f"{number:.1f}%"


def wl(summary: dict[str, Any]) -> str:
    return f"{summary.get('wins')}/{summary.get('losses')}"


def write_report(report: dict[str, Any]) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8")
    lines = [
        "# v28 Dual-Lane Overlap Portfolio",
        "",
        "Research-only. No live bot changes or orders.",
        "",
        f"- Generated UTC: `{report.get('generated_at_utc')}`",
        f"- Tracker context: `{report.get('tracker_context')}`",
        f"- Lane counts: `{report.get('lane_counts')}`",
        "",
        "## Interpretation",
        "",
    ]
    lines.extend(f"- {note}" for note in report.get("interpretation") or [])
    lines.extend([
        "",
        "## Top Diagnostic Dual Portfolios",
        "",
        "| rank | primary | sidecar | union entries | W/L | coverage | net | recon | cushion | sidecar add net | shared | blockers |",
        "|---:|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---|",
    ])
    for idx, row in enumerate(report.get("top_portfolios") or [], start=1):
        union = row.get("union") or {}
        primary = row.get("primary") or {}
        sidecar = row.get("sidecar") or {}
        lines.append(
            f"| {idx} | `{primary.get('source')}:{primary.get('policy')}` | `{sidecar.get('policy')}` | "
            f"{union.get('entries')} | {wl(union)} | {pct(union.get('coverage_pct'))} | {money(union.get('net_cents'))} | "
            f"{pct(union.get('reconstructed_share'))} | {union.get('full_loss_cushion')} | "
            f"{money(row.get('sidecar_add_net_cents'))} | {row.get('shared_markets')} | "
            f"{', '.join(row.get('blockers') or [])} |"
        )
    lines.extend([
        "",
        "## Top Strict/Post-Birth Dual Portfolios",
        "",
        "| rank | primary | sidecar | union entries | W/L | coverage | net | recon | cushion | sidecar add net | shared | blockers |",
        "|---:|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---|",
    ])
    for idx, row in enumerate(report.get("top_strict_post_portfolios") or [], start=1):
        union = row.get("union") or {}
        primary = row.get("primary") or {}
        sidecar = row.get("sidecar") or {}
        lines.append(
            f"| {idx} | `{primary.get('source')}:{primary.get('policy')}` | `{sidecar.get('policy')}` | "
            f"{union.get('entries')} | {wl(union)} | {pct(union.get('coverage_pct'))} | {money(union.get('net_cents'))} | "
            f"{pct(union.get('reconstructed_share'))} | {union.get('full_loss_cushion')} | "
            f"{money(row.get('sidecar_add_net_cents'))} | {row.get('shared_markets')} | "
            f"{', '.join(row.get('blockers') or [])} |"
        )
    lines.extend([
        "",
        "## Top Confirmation/Veto Tests",
        "",
        "| rank | primary | confirmer | kept entries | W/L | coverage | kept net | same-side net | omitted net | recon | blockers |",
        "|---:|---|---|---:|---:|---:|---:|---:|---:|---:|---|",
    ])
    for idx, row in enumerate(report.get("top_confirmations") or [], start=1):
        confirmed = row.get("confirmed") or {}
        same_side = row.get("same_side") or {}
        omitted = row.get("omitted_primary") or {}
        primary = row.get("primary") or {}
        sidecar = row.get("sidecar") or {}
        lines.append(
            f"| {idx} | `{primary.get('source')}:{primary.get('policy')}` | `{sidecar.get('policy')}` | "
            f"{confirmed.get('entries')} | {wl(confirmed)} | {pct(confirmed.get('coverage_pct'))} | "
            f"{money(confirmed.get('net_cents'))} | {money(same_side.get('net_cents'))} | "
            f"{money(omitted.get('net_cents'))} | {pct(confirmed.get('reconstructed_share'))} | "
            f"{', '.join(row.get('blockers') or [])} |"
        )
    lines.extend([
        "",
        "## Top Strict/Post Confirmation Tests",
        "",
        "| rank | primary | confirmer | kept entries | W/L | coverage | kept net | same-side net | omitted net | recon | blockers |",
        "|---:|---|---|---:|---:|---:|---:|---:|---:|---:|---|",
    ])
    for idx, row in enumerate(report.get("top_strict_confirmations") or [], start=1):
        confirmed = row.get("confirmed") or {}
        same_side = row.get("same_side") or {}
        omitted = row.get("omitted_primary") or {}
        primary = row.get("primary") or {}
        sidecar = row.get("sidecar") or {}
        lines.append(
            f"| {idx} | `{primary.get('source')}:{primary.get('policy')}` | `{sidecar.get('policy')}` | "
            f"{confirmed.get('entries')} | {wl(confirmed)} | {pct(confirmed.get('coverage_pct'))} | "
            f"{money(confirmed.get('net_cents'))} | {money(same_side.get('net_cents'))} | "
            f"{money(omitted.get('net_cents'))} | {pct(confirmed.get('reconstructed_share'))} | "
            f"{', '.join(row.get('blockers') or [])} |"
        )
    lines.extend([
        "",
        "## Top Primary Lanes",
        "",
        "| rank | source | lane | policy | entries | W/L | coverage | net | recon | cushion |",
        "|---:|---|---|---|---:|---:|---:|---:|---:|---:|",
    ])
    for idx, row in enumerate(report.get("top_primary_lanes") or [], start=1):
        lines.append(
            f"| {idx} | `{row.get('source')}` | `{row.get('lane')}` | `{row.get('policy')}` | {row.get('entries')} | "
            f"{row.get('wins')}/{row.get('losses')} | {pct(row.get('coverage_pct'))} | {money(row.get('net_cents'))} | "
            f"{pct(row.get('reconstructed_share'))} | {row.get('full_loss_cushion')} |"
        )
    lines.extend([
        "",
        "## Top Sidecar Lanes",
        "",
        "| rank | lane | policy | entries | W/L | coverage | net | recon | cushion |",
        "|---:|---|---|---:|---:|---:|---:|---:|---:|",
    ])
    for idx, row in enumerate(report.get("top_sidecar_lanes") or [], start=1):
        lines.append(
            f"| {idx} | `{row.get('lane')}` | `{row.get('policy')}` | {row.get('entries')} | "
            f"{row.get('wins')}/{row.get('losses')} | {pct(row.get('coverage_pct'))} | {money(row.get('net_cents'))} | "
            f"{pct(row.get('reconstructed_share'))} | {row.get('full_loss_cushion')} |"
        )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    report = build_report()
    write_report(report)
    print(OUT_MD)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
