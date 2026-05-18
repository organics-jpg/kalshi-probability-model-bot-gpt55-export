"""Unified leaderboard for frozen v28 forward candidates.

This consolidates the separate frozen candidate families into one forward-only
view. It is intentionally conservative: tiny samples and live blockers remain
visible, and no row is considered promoted by ranking well here.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
SOURCES = [
    ("primary_p60", OUT_DIR / "v28_frozen_forward_candidates_latest.json"),
    ("threshold_p58", OUT_DIR / "v28_frozen_threshold_challengers_latest.json"),
    ("side_agreement", OUT_DIR / "v28_frozen_side_agreement_challengers_latest.json"),
    ("convex_escape", OUT_DIR / "v28_frozen_convex_escape_challengers_latest.json"),
    ("raw_physics", OUT_DIR / "v28_frozen_raw_physics_challengers_latest.json"),
    ("raw_p52_sideflip", OUT_DIR / "v28_frozen_raw_p52_sideflip_challenger_latest.json"),
    ("raw_p52_recross_escape", OUT_DIR / "v28_frozen_raw_p52_recross_escape_challenger_latest.json"),
    ("noise_shrinkage", OUT_DIR / "v28_frozen_noise_floor_shrinkage_challengers_latest.json"),
    ("path_confirmed", OUT_DIR / "v28_path_confirmed_entry_candidates_latest.json"),
    ("raw_entry_coverage_valve", OUT_DIR / "v28_raw_entry_coverage_valve_latest.json"),
    ("target_coverage_p70_fv", OUT_DIR / "v28_frozen_target_coverage_p70_fv_latest.json"),
    ("target_coverage_p70_empirical_bayes", OUT_DIR / "v28_frozen_target_coverage_p70_empirical_bayes_latest.json"),
    ("mid_edge_false_conviction_fv", OUT_DIR / "v28_frozen_mid_edge_false_conviction_fv_latest.json"),
    ("composite_false_conviction_fv", OUT_DIR / "v28_frozen_composite_false_conviction_fv_latest.json"),
    ("thin_recross_midp_entry_gate", OUT_DIR / "v28_frozen_thin_recross_midp_entry_gate_latest.json"),
    ("target_loss_tag_repair_entry", OUT_DIR / "v28_frozen_target_loss_tag_repair_entry_latest.json"),
    ("early_no_boundary_decay_repair_entry", OUT_DIR / "v28_frozen_early_no_boundary_decay_repair_entry_latest.json"),
    ("mid_edge_boundary_deception_repair_entry", OUT_DIR / "v28_frozen_mid_edge_boundary_deception_repair_entry_latest.json"),
    ("composite_false_conviction_repair_entry", OUT_DIR / "v28_frozen_composite_false_conviction_repair_entry_latest.json"),
    ("goldilocks_edge_repair_entry", OUT_DIR / "v28_frozen_goldilocks_edge_repair_entry_latest.json"),
    ("false_conviction_approved_repair", OUT_DIR / "v28_frozen_false_conviction_approved_repair_latest.json"),
    ("low_recross_repair_entry", OUT_DIR / "v28_frozen_low_recross_repair_entry_latest.json"),
    ("high_raw_p_repair_entry", OUT_DIR / "v28_frozen_high_raw_p_repair_entry_latest.json"),
    ("p50_book_edge_entry", OUT_DIR / "v28_frozen_p50_book_edge_entry_latest.json"),
    ("book_plus05_entry", OUT_DIR / "v28_frozen_book_plus05_entry_latest.json"),
    ("book_plus05_no_cheap_yes_entry", OUT_DIR / "v28_frozen_book_plus05_no_cheap_yes_entry_latest.json"),
    ("raw_p52_favorite_valley_skip", OUT_DIR / "v28_frozen_raw_p52_favorite_valley_skip_latest.json"),
    ("raw_p52_mid_edge_skip", OUT_DIR / "v28_frozen_raw_p52_mid_edge_skip_latest.json"),
    ("raw_p52_shadow_mid_edge_skip", OUT_DIR / "v28_frozen_raw_p52_shadow_mid_edge_skip_latest.json"),
    ("raw_p52_book_disagreement_skip", OUT_DIR / "v28_frozen_raw_p52_book_disagreement_skip_latest.json"),
    ("raw_p52_book_shrink_entry", OUT_DIR / "v28_frozen_raw_p52_book_shrink_entry_latest.json"),
    ("raw_p52_early_no_boundary_skip", OUT_DIR / "v28_frozen_raw_p52_early_no_boundary_skip_latest.json"),
    ("raw_p52_early_no_boundary_band_skip", OUT_DIR / "v28_frozen_raw_p52_early_no_boundary_band_skip_latest.json"),
]
READINESS_JSON = OUT_DIR / "v28_live_trade_readiness_latest.json"
OUT_JSON = OUT_DIR / "v28_frozen_candidate_leaderboard_latest.json"
OUT_MD = OUT_DIR / "v28_frozen_candidate_leaderboard_latest.md"


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


def readiness_map() -> dict[tuple[str, str], dict[str, Any]]:
    payload = load_json(READINESS_JSON)
    return {
        (str(row.get("gate") or ""), str(row.get("policy") or "")): row
        for row in payload.get("candidates") or []
    }


def choose_blockers(row: dict[str, Any], ready: dict[str, Any]) -> list[str]:
    """Prefer the owning frozen scorecard's blockers over stale readiness joins."""
    source = row.get("source_blockers")
    if source is None:
        source = row.get("blockers")
    source_blockers = [str(item) for item in (source or []) if item]
    ready_blockers = [str(item) for item in (ready.get("blockers") or []) if item]
    if not source_blockers:
        return ready_blockers
    blockers = list(source_blockers)
    for blocker in ready_blockers:
        if blocker.startswith("control_") and blocker not in blockers:
            blockers.append(blocker)
    return blockers


def build_report() -> dict[str, Any]:
    ready_by_key = readiness_map()
    rows: list[dict[str, Any]] = []
    for gate, path in SOURCES:
        payload = load_json(path)
        if gate == "raw_entry_coverage_valve":
            source_rows = []
            for policy_row in payload.get("ranked") or []:
                fwd = (policy_row.get("forward") or {}).get("coverage_valve") or {}
                source_rows.append({
                    **fwd,
                    "policy": policy_row.get("policy"),
                    "forward_market_denominator": payload.get("forward_denominator"),
                })
        elif gate == "thin_recross_midp_entry_gate":
            candidate = payload.get("candidate") or {}
            source_rows = [{
                **candidate,
                "policy": (payload.get("freeze") or {}).get("candidate"),
                "forward_market_denominator": payload.get("future_denominator"),
                "wins": candidate.get("wins"),
                "losses": candidate.get("losses"),
            }]
        elif gate in {
            "target_loss_tag_repair_entry",
            "early_no_boundary_decay_repair_entry",
            "mid_edge_boundary_deception_repair_entry",
            "composite_false_conviction_repair_entry",
            "goldilocks_edge_repair_entry",
            "false_conviction_approved_repair",
            "low_recross_repair_entry",
            "high_raw_p_repair_entry",
            "raw_p52_favorite_valley_skip",
            "raw_p52_mid_edge_skip",
            "raw_p52_shadow_mid_edge_skip",
            "raw_p52_book_disagreement_skip",
            "raw_p52_book_shrink_entry",
            "raw_p52_early_no_boundary_skip",
            "raw_p52_early_no_boundary_band_skip",
        }:
            candidate = (
                ((payload.get("frozen_future") or {}).get("candidate_summary") or {})
                if gate == "goldilocks_edge_repair_entry"
                else payload.get("candidate_summary") or {}
            )
            source_rows = [{
                **candidate,
                "policy": (payload.get("freeze") or {}).get("candidate"),
                "forward_market_denominator": (payload.get("frozen_future") or {}).get("future_denominator") if gate == "goldilocks_edge_repair_entry" else payload.get("future_denominator"),
                "net_cents_after_entry_fee": candidate.get("net_cents"),
                "wins": candidate.get("wins"),
                "losses": candidate.get("losses"),
                "source_blockers": (payload.get("frozen_future") or {}).get("blockers") if gate == "goldilocks_edge_repair_entry" else payload.get("blockers"),
            }]
        elif gate in {
            "p50_book_edge_entry",
            "book_plus05_entry",
            "book_plus05_no_cheap_yes_entry",
        }:
            summary = payload.get("summary") or {}
            source_rows = [{
                **summary,
                "policy": (payload.get("freeze") or {}).get("candidate"),
                "forward_market_denominator": payload.get("future_denominator_markets"),
                "net_cents_after_entry_fee": summary.get("gross_cents"),
                "wins": summary.get("wins"),
                "losses": summary.get("losses"),
                "approved_entry_count": summary.get("approved_entry_count"),
                "added_reject_count": summary.get("simulated_or_rejected_count"),
                "source_blockers": payload.get("blockers"),
            }]
        elif gate in {
            "target_coverage_p70_fv",
            "target_coverage_p70_empirical_bayes",
            "mid_edge_false_conviction_fv",
            "composite_false_conviction_fv",
        }:
            best = (payload.get("ranked") or [{}])[0]
            source_rows = [{
                "policy": f"{(payload.get('freeze') or {}).get('entry_policy')} + {best.get('variant')}",
                "entries": payload.get("entries"),
                "settled": payload.get("settled"),
                "wins": best.get("wins"),
                "losses": best.get("losses"),
                "coverage_pct": payload.get("coverage_pct"),
                "net_cents_after_entry_fee": best.get("net_cents"),
                "avg_brier": best.get("brier_mean_delta"),
                "forward_market_denominator": payload.get("future_denominator"),
            }]
        else:
            source_rows = payload.get("summary") or payload.get("summaries") or []
        for row in source_rows:
            policy = str(row.get("policy") or "")
            ready = ready_by_key.get((gate, policy), {})
            entries = as_float(row.get("entries")) or 0.0
            settled = as_float(row.get("settled")) or 0.0
            net = as_float(row.get("net_cents_after_entry_fee")) or 0.0
            coverage = as_float(row.get("coverage_pct"))
            avg_brier = as_float(row.get("avg_brier"))
            rows.append({
                "gate": gate,
                "policy": policy,
                "freeze_ts": payload.get("freeze_ts"),
                "forward_denominator": payload.get("forward_market_denominator") or payload.get("future_denominator"),
                "entries": row.get("entries"),
                "settled": row.get("settled"),
                "wins": row.get("wins"),
                "losses": row.get("losses"),
                "coverage_pct": coverage,
                "net_cents_after_entry_fee": net,
                "avg_net_cents_after_entry_fee": net / settled if settled else None,
                "avg_brier": avg_brier,
                "approved_entry_count": row.get("approved_entry_count"),
                "added_reject_count": row.get("added_reject_count"),
                "missed_forward_market_count": row.get("missed_forward_market_count"),
                "live_ready": ready.get("live_ready", False),
                "blockers": choose_blockers(row, ready),
                "coverage_in_target": coverage is not None and 70.0 <= coverage <= 90.0,
                "settled_sample_tiny": settled < 10,
                "settled_sample_promotion_blocked": settled < 30,
            })
    ranked = sorted(
        rows,
        key=lambda row: (
            float(row.get("net_cents_after_entry_fee") or -999999.0),
            bool(row["coverage_in_target"]),
            -float(row.get("avg_brier") if row.get("avg_brier") is not None else 999.0),
            -float(row.get("settled") or 0.0),
        ),
        reverse=True,
    )
    return {
        "sources": [{"gate": gate, "path": str(path)} for gate, path in SOURCES],
        "rows": rows,
        "ranked": ranked,
    }


def fmt(value: Any) -> str:
    if value is None:
        return "None"
    if isinstance(value, float):
        return f"{value:.6f}"
    return str(value)


def write_md(report: dict[str, Any]) -> None:
    lines = [
        "# v28 Frozen Candidate Leaderboard",
        "",
        "Forward-only consolidated view. Ranking is not promotion; live readiness blockers still apply.",
        "",
        "| rank | gate | policy | entries | settled | W/L | coverage | net c | avg c | brier | live ready | key blockers |",
        "|---:|---|---|---:|---:|---:|---:|---:|---:|---:|---|---|",
    ]
    for idx, row in enumerate(report["ranked"], start=1):
        blockers = row.get("blockers") or []
        short_blockers = ", ".join(blockers[:4])
        if len(blockers) > 4:
            short_blockers += ", ..."
        lines.append(
            f"| {idx} | {row['gate']} | {row['policy']} | {row['entries']} | {row['settled']} | "
            f"{row['wins']}/{row['losses']} | {fmt(row['coverage_pct'])} | {fmt(row['net_cents_after_entry_fee'])} | "
            f"{fmt(row['avg_net_cents_after_entry_fee'])} | {fmt(row['avg_brier'])} | {row['live_ready']} | "
            f"{short_blockers or 'none'} |"
        )
    lines.extend([
        "",
        "## Current Interpretation",
        "",
    ])
    top = report["ranked"][0] if report["ranked"] else None
    if top:
        lines.append(
            f"- Current net leader: `{top['gate']}` `{top['policy']}` "
            f"with net `{fmt(top['net_cents_after_entry_fee'])}c`, coverage `{fmt(top['coverage_pct'])}`, "
            f"settled `{top['settled']}`."
        )
    target_rows = [row for row in report["ranked"] if row.get("coverage_in_target")]
    if target_rows:
        target = target_rows[0]
        lines.append(
            f"- Best target-coverage row: `{target['gate']}` `{target['policy']}` "
            f"with net `{fmt(target['net_cents_after_entry_fee'])}c`, coverage `{fmt(target['coverage_pct'])}`, "
            f"settled `{target['settled']}`."
        )
    lines.append("- Anything with fewer than 30 settled forward rows remains evidence-gathering only.")
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    report = build_report()
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_md(report)
    print(str(OUT_MD))


if __name__ == "__main__":
    main()
