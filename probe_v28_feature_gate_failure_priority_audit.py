"""Compact failure-priority audit for the v28 feature-gate branch.

Research-only. This consolidates existing failure classifiers into the explicit
project failure buckets and does not change live bot logic or candidate rules.
"""
from __future__ import annotations

import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
OUT_JSON = OUT_DIR / "v28_feature_gate_failure_priority_audit_latest.json"
OUT_MD = OUT_DIR / "v28_feature_gate_failure_priority_audit_latest.md"

FAILURE_MODES = OUT_DIR / "v28_boundary_clock_feature_gate_failure_modes_latest.json"
LOSS_ANALOG = OUT_DIR / "v28_boundary_clock_feature_gate_loss_analog_monitor_latest.json"
RESIDUAL = OUT_DIR / "v28_boundary_clock_feature_gate_residual_loss_mechanism_latest.json"
LIVE_MISMATCH = OUT_DIR / "v28_feature_gate_live_exit_mismatch_drilldown_latest.json"
PROMOTION_GAP = OUT_DIR / "v28_feature_gate_promotion_gap_audit_latest.json"


BUCKET_LABELS = {
    "fv_error": "FV error",
    "entry_timing_error": "Entry timing error",
    "exit_policy_error": "Exit-policy error",
    "execution_friction_error": "Execution/friction error",
    "market_regime_error": "Market-regime error",
    "source_quality_error": "Source-quality error",
    "fragility_error": "Fragility error",
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


def cents(value: Any) -> str:
    try:
        c = float(value)
    except (TypeError, ValueError):
        return ""
    return f"{c:.0f}c"


def pct(value: Any) -> str:
    try:
        return f"{float(value):.2f}%"
    except (TypeError, ValueError):
        return ""


def post_entry_row(payload: dict[str, Any], candidate: str) -> dict[str, Any]:
    lanes = payload.get("lanes") if isinstance(payload.get("lanes"), dict) else {}
    rows = lanes.get("post_feature_freeze_entry") if isinstance(lanes.get("post_feature_freeze_entry"), list) else []
    for row in rows:
        if row.get("candidate") == candidate:
            return row
    return rows[0] if rows else {}


def loss_stats(loss_rows: list[dict[str, Any]]) -> dict[str, Any]:
    tag_counts: Counter[str] = Counter()
    source_counts: Counter[str] = Counter()
    source_net: Counter[str] = Counter()
    tag_net: Counter[str] = Counter()
    worst_rows = []
    for row in loss_rows:
        net = float(row.get("net_cents") or 0.0)
        source = str(row.get("source") or "unknown")
        source_counts[source] += 1
        source_net[source] += net
        for tag in row.get("failure_tags") or []:
            tag_counts[str(tag)] += 1
            tag_net[str(tag)] += net
        worst_rows.append(
            {
                "market": row.get("market"),
                "source": source,
                "side": row.get("side"),
                "net_cents": net,
                "raw_edge": row.get("raw_edge"),
                "recross_hazard_score": row.get("recross_hazard_score"),
                "abs_d_sigma": row.get("abs_d_sigma"),
                "ask_prob": row.get("ask_prob"),
                "failure_tags": row.get("failure_tags") or [],
            }
        )
    worst_rows.sort(key=lambda item: float(item.get("net_cents") or 0.0))
    return {
        "loss_count": len(loss_rows),
        "loss_net_cents": sum(float(row.get("net_cents") or 0.0) for row in loss_rows),
        "tag_counts": dict(tag_counts),
        "tag_net_cents": dict(tag_net),
        "source_counts": dict(source_counts),
        "source_net_cents": dict(source_net),
        "worst_rows": worst_rows[:8],
    }


def analog_components(payload: dict[str, Any]) -> dict[str, Any]:
    lanes = payload.get("lanes") if isinstance(payload.get("lanes"), dict) else {}
    lane = lanes.get("post_feature_freeze_entry") if isinstance(lanes.get("post_feature_freeze_entry"), dict) else {}
    scores = lane.get("summary_scores") if isinstance(lane.get("summary_scores"), dict) else {}
    return {
        "rows": scores.get("rows"),
        "avg_loss_analog_score": scores.get("avg_loss_analog_score"),
        "max_loss_analog_score": scores.get("max_loss_analog_score"),
        "risk_component_counts": scores.get("risk_component_counts") or {},
    }


def residual_summary(payload: dict[str, Any]) -> dict[str, Any]:
    lanes = payload.get("lanes") if isinstance(payload.get("lanes"), dict) else {}
    lane = lanes.get("post_penalty_birth_entry") if isinstance(lanes.get("post_penalty_birth_entry"), dict) else {}
    residual = lane.get("residual_summary") if isinstance(lane.get("residual_summary"), dict) else {}
    loss = lane.get("loss_summary") if isinstance(lane.get("loss_summary"), dict) else {}
    return {
        "post_penalty_rows": (lane.get("summary") or {}).get("settled"),
        "post_penalty_net_cents": (lane.get("summary") or {}).get("net_cents"),
        "residual_tag_counts": residual.get("tag_counts") or {},
        "loss_tag_counts": loss.get("tag_counts") or {},
    }


def live_exit_mismatch(payload: dict[str, Any]) -> dict[str, Any]:
    markets = payload.get("markets") if isinstance(payload.get("markets"), list) else []
    class_counts: Counter[str] = Counter()
    reason_counts: Counter[str] = Counter()
    theory = 0.0
    live = 0.0
    for market in markets:
        theory += float(market.get("theory_net_cents") or 0.0)
        live += float(market.get("live_selected_side_net_cents") or 0.0)
        for cls in market.get("classifications") or []:
            class_counts[str(cls)] += 1
        for reason, count in (market.get("exit_reason_counts") or {}).items():
            reason_counts[str(reason)] += int(count or 0)
    return {
        "markets": len(markets),
        "theory_net_cents": theory,
        "live_selected_net_cents": live,
        "swing_cents": theory - live,
        "class_counts": dict(class_counts),
        "reason_counts": dict(reason_counts),
    }


def summary_value(row: dict[str, Any], key: str) -> Any:
    summary = row.get("summary") if isinstance(row.get("summary"), dict) else {}
    return row.get(key, summary.get(key))


def bucket_priority(
    selected: dict[str, Any],
    stats: dict[str, Any],
    mismatch: dict[str, Any],
    promotion: dict[str, Any],
) -> list[dict[str, Any]]:
    tag_counts = Counter(stats.get("tag_counts") or {})
    broad = {}
    for row in promotion.get("official_feature_gate_rows") or []:
        if row.get("candidate") == "post_feature_freeze_entry_raw03_recross70_abs075":
            broad = row
            break

    priorities = [
        {
            "bucket": "exit_policy_error",
            "evidence": (
                f"{mismatch.get('markets')} selected-side theory winners became live selected-side losses; "
                f"settlement theory {cents(mismatch.get('theory_net_cents'))}, live selected {cents(mismatch.get('live_selected_net_cents'))}, "
                f"swing {cents(mismatch.get('swing_cents'))}."
            ),
            "repair_read": "Exit/state validation remains first priority, but active exit watches still need strict post-freeze denominators.",
            "rank": 1,
        },
        {
            "bucket": "source_quality_error",
            "evidence": (
                f"{tag_counts.get('source_quality_error', 0)} selected losses carry source-quality tags; "
                f"official broad lane reconstructed share is {float(broad.get('reconstructed_share') or 0.0):.2%}."
            ),
            "repair_read": "Needs new clean approved rows or an observable source-risk shrink that clears row source, coverage, live delta, and cushion together.",
            "rank": 2,
        },
        {
            "bucket": "fragility_error",
            "evidence": f"Broad post-freeze lane cushion is {broad.get('full_loss_cushion')}; loss rows total {cents(stats.get('loss_net_cents'))}.",
            "repair_read": "Current positive net cannot absorb three full losses; any repair must add cushion without reintroducing source risk.",
            "rank": 3,
        },
        {
            "bucket": "execution_friction_error",
            "evidence": f"{tag_counts.get('execution_friction_error', 0)} selected losses are tagged execution/friction or thin-edge failure.",
            "repair_read": "This overlaps source/cheap-touch risk and argues for sizing/entry-quality shrink rather than wider thresholds.",
            "rank": 4,
        },
        {
            "bucket": "fv_error",
            "evidence": f"{tag_counts.get('fv_error', 0)} selected losses show FV/overconfidence tags, including large approved losses.",
            "repair_read": "FV calibration is a later overlay here; entry/exit state currently has clearer forward blockers.",
            "rank": 5,
        },
        {
            "bucket": "market_regime_error",
            "evidence": f"{tag_counts.get('market_regime_error', 0)} selected losses carry regime/path tags.",
            "repair_read": "Use as warning context for shrink/regime overlays; do not make a brittle cutoff from this small sample.",
            "rank": 6,
        },
        {
            "bucket": "entry_timing_error",
            "evidence": f"{tag_counts.get('entry_timing_error', 0)} selected loss is explicitly tagged entry timing.",
            "repair_read": "Not the dominant post-freeze repair path versus exit/source/cushion blockers.",
            "rank": 7,
        },
    ]
    return priorities


def build_report() -> dict[str, Any]:
    failure = load_json(FAILURE_MODES)
    analog = load_json(LOSS_ANALOG)
    residual = load_json(RESIDUAL)
    mismatch_payload = load_json(LIVE_MISMATCH)
    promotion = load_json(PROMOTION_GAP)

    selected = post_entry_row(failure, "post_feature_freeze_entry_raw03_recross70_abs075")
    stats = loss_stats(selected.get("loss_rows") or [])
    mismatch = live_exit_mismatch(mismatch_payload)
    priorities = bucket_priority(selected, stats, mismatch, promotion)

    return {
        "generated_at_utc": utc_now_iso(),
        "freeze_ts_utc": failure.get("freeze_ts_utc"),
        "candidate": selected.get("candidate"),
        "selected_summary": {
            "settled": summary_value(selected, "settled"),
            "denominator": selected.get("denominator"),
            "wins": summary_value(selected, "wins"),
            "losses": summary_value(selected, "losses"),
            "coverage_pct": summary_value(selected, "coverage_pct"),
            "net_cents": summary_value(selected, "net_cents"),
            "reconstructed_share": selected.get("reconstructed_share"),
            "full_loss_cushion": selected.get("full_loss_cushion"),
            "blockers": selected.get("blockers") or [],
            "structural_failure_modes": selected.get("structural_failure_modes") or [],
            "selected_row_failure_counts": selected.get("selected_row_failure_counts") or {},
        },
        "loss_stats": stats,
        "loss_analog": analog_components(analog),
        "residual_after_penalty": residual_summary(residual),
        "live_exit_mismatch": mismatch,
        "bucket_priorities": priorities,
        "conclusion": "exit_state_first_but_watch_only",
    }


def write_report(payload: dict[str, Any]) -> None:
    summary = payload["selected_summary"]
    lines = [
        "# v28 Feature-Gate Failure Priority Audit",
        "",
        "Research-only consolidation. No live bot changes, no orders, no new candidate rule.",
        "",
        f"- Generated UTC: `{payload['generated_at_utc']}`",
        f"- Feature-gate freeze UTC: `{payload.get('freeze_ts_utc')}`",
        f"- Candidate: `{payload.get('candidate')}`",
        f"- Conclusion: `{payload['conclusion']}`",
        "",
        "## Current Strict Lane",
        "",
        f"- Settled / denominator: `{summary.get('settled')}` / `{summary.get('denominator')}`",
        f"- W/L: `{summary.get('wins')}/{summary.get('losses')}`",
        f"- Coverage: `{pct(summary.get('coverage_pct'))}`",
        f"- Net: `{cents(summary.get('net_cents'))}`",
        f"- Reconstructed share: `{float(summary.get('reconstructed_share') or 0.0):.2%}`",
        f"- Full-loss cushion: `{summary.get('full_loss_cushion')}`",
        f"- Blockers: `{', '.join(summary.get('blockers') or [])}`",
        f"- Structural modes: `{', '.join(summary.get('structural_failure_modes') or [])}`",
        "",
        "## Failure Bucket Priority",
        "",
        "| rank | bucket | evidence | repair read |",
        "|---:|---|---|---|",
    ]
    for item in payload["bucket_priorities"]:
        lines.append(
            f"| {item.get('rank')} | {BUCKET_LABELS.get(item.get('bucket'), item.get('bucket'))} | {item.get('evidence')} | {item.get('repair_read')} |"
        )

    analog = payload["loss_analog"]
    residual = payload["residual_after_penalty"]
    mismatch = payload["live_exit_mismatch"]
    lines.extend(
        [
            "",
            "## Supporting Signals",
            "",
            f"- Loss analog risk components: `{analog.get('risk_component_counts')}`",
            f"- Post-penalty residual tag counts: `{residual.get('loss_tag_counts')}`",
            f"- Live exit mismatch class counts: `{mismatch.get('class_counts')}`",
            f"- Live exit mismatch reason counts: `{mismatch.get('reason_counts')}`",
            "",
            "## Worst Strict Loss Rows",
            "",
            "| market | source | side | net | raw edge | recross | abs d | ask | tags |",
            "|---|---|---|---:|---:|---:|---:|---:|---|",
        ]
    )
    for row in payload["loss_stats"].get("worst_rows") or []:
        lines.append(
            "| {market} | {source} | {side} | {net} | {edge} | {recross} | {absd} | {ask} | {tags} |".format(
                market=row.get("market"),
                source=row.get("source"),
                side=row.get("side"),
                net=cents(row.get("net_cents")),
                edge=row.get("raw_edge"),
                recross=row.get("recross_hazard_score"),
                absd=row.get("abs_d_sigma"),
                ask=row.get("ask_prob"),
                tags=", ".join(row.get("failure_tags") or []),
            )
        )

    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "- The feature-gate branch is not blocked by a single threshold defect.",
            "- Exit/state repair has the clearest live-market failure evidence, but the frozen exit watches still need strict forward rows.",
            "- Source quality and cushion remain hard promotion blockers even if entry-side diagnostic PnL is positive.",
        ]
    )

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    payload = build_report()
    write_report(payload)
    print(OUT_MD)


if __name__ == "__main__":
    main()
