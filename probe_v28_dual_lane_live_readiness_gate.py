"""Dual-lane-only live-readiness gate for v28 research.

Research-only; no live bot changes and no orders.

This is deliberately narrower than the global controlled live-test gate. It
only evaluates the dual_lane_overlap_union own-freeze watch and its collection
monitor so the candidate's status is easy to audit without diagnostic rows or
other candidates crowding the table.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
OWN_FREEZE_JSON = OUT_DIR / "v28_dual_lane_own_freeze_watch_latest.json"
COLLECTION_JSON = OUT_DIR / "v28_dual_lane_freeze_collection_monitor_latest.json"
PREVIEW_JSON = OUT_DIR / "v28_dual_lane_shadow_feature_preview_latest.json"
DIAGNOSTIC_JSON = OUT_DIR / "v28_dual_lane_overlap_portfolio_latest.json"
LIVE_SUMMARY_JSON = ROOT / "stats" / "live_mushroom_v28_size2" / "summary.json"
OUT_JSON = OUT_DIR / "v28_dual_lane_live_readiness_gate_latest.json"
OUT_MD = OUT_DIR / "v28_dual_lane_live_readiness_gate_latest.md"

MIN_SETTLED = 30
MIN_CUSHION = 3
MAX_RECON_SHARE = 0.35
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


def fnum(value: Any, default: float = 0.0) -> float:
    try:
        if value is None or value == "":
            return default
        return float(value)
    except (TypeError, ValueError):
        return default


def live_baseline_cents() -> float:
    live = load_json(LIVE_SUMMARY_JSON)
    return 100.0 * fnum(live.get("net_pnl_total_dollars"))


def missing_gates(row: dict[str, Any], live_cents: float) -> list[str]:
    summary = row.get("summary") if isinstance(row.get("summary"), dict) else {}
    missing: list[str] = []
    settled = int(fnum(summary.get("settled")))
    net = fnum(summary.get("net_cents"))
    coverage = summary.get("coverage_pct")
    coverage_f = fnum(coverage) if coverage is not None else None
    recon = summary.get("reconstructed_share")
    recon_f = fnum(recon) if recon is not None else None
    cushion = int(fnum(summary.get("full_loss_cushion")))

    if not bool(row.get("strict_forward")):
        missing.append("not_strict_forward")
    if settled < MIN_SETTLED:
        missing.append(f"settled_lt_{MIN_SETTLED}")
    if net <= 0:
        missing.append("net_not_positive")
    if coverage_f is None:
        missing.append("coverage_unknown")
    elif coverage_f < TARGET_COVERAGE_MIN:
        missing.append("coverage_lt_75pct")
    elif coverage_f > TARGET_COVERAGE_MAX:
        missing.append("coverage_gt_90pct")
    if recon_f is None:
        missing.append("source_share_unknown")
    elif recon_f > MAX_RECON_SHARE:
        missing.append("reconstructed_share_gt_35pct")
    if cushion < MIN_CUSHION:
        missing.append("full_loss_cushion_lt_3")
    if net <= live_cents:
        missing.append("does_not_beat_refreshed_live_baseline")
    for blocker in row.get("blockers") or []:
        if blocker and blocker not in missing:
            missing.append(str(blocker))
    return missing


def compact_union(row: dict[str, Any], live_cents: float) -> dict[str, Any]:
    summary = row.get("summary") if isinstance(row.get("summary"), dict) else {}
    sidecar = row.get("sidecar") if isinstance(row.get("sidecar"), dict) else {}
    net = fnum(summary.get("net_cents"))
    gates = missing_gates(row, live_cents)
    return {
        "policy": sidecar.get("policy"),
        "settled": int(fnum(summary.get("settled"))),
        "wins": int(fnum(summary.get("wins"))),
        "losses": int(fnum(summary.get("losses"))),
        "coverage_pct": summary.get("coverage_pct"),
        "net_cents": net,
        "delta_vs_live_cents": net - live_cents,
        "reconstructed_share": summary.get("reconstructed_share"),
        "full_loss_cushion": summary.get("full_loss_cushion"),
        "sidecar_add_entries": row.get("sidecar_add_entries"),
        "sidecar_add_net_cents": row.get("sidecar_add_net_cents"),
        "shared_markets": row.get("shared_markets"),
        "strict_forward": bool(row.get("strict_forward")),
        "live_ready": not gates,
        "missing_gates": gates,
    }


def compact_summary(summary: dict[str, Any] | None) -> dict[str, Any]:
    src = summary if isinstance(summary, dict) else {}
    return {
        "entries": int(fnum(src.get("entries"))),
        "settled": int(fnum(src.get("settled"))),
        "wins": int(fnum(src.get("wins"))),
        "losses": int(fnum(src.get("losses"))),
        "coverage_pct": src.get("coverage_pct"),
        "net_cents": fnum(src.get("net_cents")),
        "reconstructed_share": src.get("reconstructed_share"),
        "full_loss_cushion": src.get("full_loss_cushion"),
        "source_counts": src.get("source_counts"),
    }


def compact_portfolio(portfolio: dict[str, Any] | None) -> dict[str, Any]:
    src = portfolio if isinstance(portfolio, dict) else {}
    primary = src.get("primary") if isinstance(src.get("primary"), dict) else {}
    sidecar = src.get("sidecar") if isinstance(src.get("sidecar"), dict) else {}
    union = src.get("union") if isinstance(src.get("union"), dict) else {}
    return {
        "primary": f"{primary.get('source')}:{primary.get('policy')}" if primary else None,
        "sidecar": sidecar.get("policy"),
        "summary": compact_summary(union),
        "sidecar_add_entries": src.get("sidecar_add_entries"),
        "sidecar_add_net_cents": src.get("sidecar_add_net_cents"),
        "shared_markets": src.get("shared_markets"),
        "blockers": src.get("blockers") or [],
    }


def build_report() -> dict[str, Any]:
    own = load_json(OWN_FREEZE_JSON)
    collection = load_json(COLLECTION_JSON)
    preview = load_json(PREVIEW_JSON)
    diagnostic = load_json(DIAGNOSTIC_JSON)
    live_cents = live_baseline_cents()
    unions = [
        compact_union(row, live_cents)
        for row in own.get("unions") or []
        if isinstance(row, dict)
    ]
    unions.sort(key=lambda row: (len(row.get("missing_gates") or []), -fnum(row.get("net_cents"))))
    eligible = [row for row in unions if row.get("live_ready")]
    clock = collection.get("sample_clock") if isinstance(collection.get("sample_clock"), dict) else {}
    stream = collection.get("shadow_collection") if isinstance(collection.get("shadow_collection"), dict) else {}
    collection_blocker = collection.get("blocker")
    decision = "dual_lane_live_test_review" if eligible and not collection_blocker else "no_live_test"

    if collection_blocker == "waiting_for_min_30_market_windows":
        next_action = (
            "Keep collecting. The candidate is born and shadow data is arriving, "
            "but it cannot pass the 30-settled-row gate yet."
        )
    elif collection_blocker:
        next_action = f"Investigate collection blocker: {collection_blocker}."
    elif not eligible:
        next_action = "Review missing score gates on the own-freeze union rows."
    else:
        next_action = "Manual review can start; score gates and collection monitor are clear."

    return {
        "generated_at_utc": utc_now_iso(),
        "decision": decision,
        "freeze_ts_utc": own.get("state", {}).get("freeze_ts_utc") if isinstance(own.get("state"), dict) else None,
        "freeze_local_time": own.get("freeze_local_time"),
        "live_baseline_cents": live_cents,
        "requirements": {
            "min_settled": MIN_SETTLED,
            "coverage_min_pct": TARGET_COVERAGE_MIN,
            "coverage_max_pct": TARGET_COVERAGE_MAX,
            "max_reconstructed_share": MAX_RECON_SHARE,
            "min_full_loss_cushion": MIN_CUSHION,
            "must_beat_live_baseline_cents": live_cents,
        },
        "sample_clock": clock,
        "collection": {
            "blocker": collection_blocker,
            "post_freeze_events": stream.get("post_freeze_events"),
            "post_freeze_entry_rows": stream.get("post_freeze_entry_rows"),
            "post_freeze_distinct_markets": stream.get("post_freeze_distinct_markets"),
            "settled_post_exit_clock_rows": stream.get("settled_post_exit_clock_rows"),
            "pending_post_exit_clock_rows": stream.get("pending_post_exit_clock_rows"),
        },
        "evidence_layers": {
            "diagnostic_pre_own_freeze": compact_portfolio((diagnostic.get("top_portfolios") or [None])[0]),
            "strict_pre_own_freeze_context": compact_portfolio((diagnostic.get("top_strict_post_portfolios") or [None])[0]),
            "shadow_feature_preview": {
                "scope": preview.get("preview_scope"),
                "generated_at_utc": preview.get("generated_at_utc"),
                "post_freeze_observation_count": preview.get("post_freeze_observation_count"),
                "post_freeze_distinct_markets": preview.get("post_freeze_distinct_markets"),
                "feature_availability": preview.get("feature_availability"),
                "sidecar_preview_summary": compact_summary(preview.get("sidecar_preview_summary")),
                "primary_pocket_preview_summary": compact_summary(preview.get("primary_pocket_preview_summary")),
                "primary_pocket_rule_note": (preview.get("primary_pocket_rule") or {}).get("note")
                if isinstance(preview.get("primary_pocket_rule"), dict)
                else None,
            },
            "own_freeze_promotion_score": {
                "strict_forward_only": True,
                "source": str(OWN_FREEZE_JSON),
                "note": "Only this layer can make the dual lane live-ready.",
            },
        },
        "eligible": eligible,
        "unions": unions,
        "next_action": next_action,
        "interpretation": [
            "This is the dual-lane-only readiness gate.",
            "Pre-own-freeze rows explain why the dual lane was created but cannot prove live readiness.",
            "The shadow feature preview checks collection health only; it is not promotion evidence.",
            "Diagnostic dual-lane PnL is not promotion evidence; only own-freeze rows count.",
            "The global controlled live-test gate remains the final arbiter before any live trade test.",
        ],
    }


def cents(value: Any) -> str:
    amount = fnum(value)
    return f"{amount:.0f}c (${amount / 100.0:.2f})"


def pct(value: Any) -> str:
    if value is None:
        return "n/a"
    return f"{fnum(value):.2f}%"


def share(value: Any) -> str:
    if value is None:
        return "n/a"
    return f"{100.0 * fnum(value):.2f}%"


def write_report(report: dict[str, Any]) -> None:
    clock = report.get("sample_clock") or {}
    collection = report.get("collection") or {}
    layers = report.get("evidence_layers") or {}
    diagnostic = layers.get("diagnostic_pre_own_freeze") or {}
    strict_context = layers.get("strict_pre_own_freeze_context") or {}
    preview = layers.get("shadow_feature_preview") or {}
    preview_sidecar = preview.get("sidecar_preview_summary") or {}
    preview_primary = preview.get("primary_pocket_preview_summary") or {}
    lines = [
        "# v28 Dual-Lane Live-Readiness Gate",
        "",
        "Research-only. No live bot logic changes, no orders.",
        "",
        f"- Generated UTC: `{report.get('generated_at_utc')}`",
        f"- Decision: `{report.get('decision')}`",
        f"- Freeze UTC: `{report.get('freeze_ts_utc')}`",
        f"- Freeze local time: `{report.get('freeze_local_time')}`",
        f"- Live baseline: `{cents(report.get('live_baseline_cents'))}`",
        f"- Next action: {report.get('next_action')}",
        "",
        "## Sample And Collection",
        "",
        f"- Possible 15m windows since freeze: `{clock.get('possible_market_windows_since_freeze')}`",
        f"- Windows remaining to 30-row gate: `{clock.get('windows_remaining_to_min_sample')}`",
        f"- Earliest possible 30-window local time: `{clock.get('earliest_min_sample_local_time')}`",
        f"- Collection blocker: `{collection.get('blocker') or 'none'}`",
        f"- Post-freeze events/entries/settled/pending: `{collection.get('post_freeze_events')}` / "
        f"`{collection.get('post_freeze_entry_rows')}` / `{collection.get('settled_post_exit_clock_rows')}` / "
        f"`{collection.get('pending_post_exit_clock_rows')}`",
        "",
        "## Evidence Layers",
        "",
        "| layer | status | entries | W/L | coverage | net | recon | cushion | note |",
        "|---|---|---:|---:|---:|---:|---:|---:|---|",
        (
            f"| diagnostic pre-own-freeze | discovery only | {(diagnostic.get('summary') or {}).get('entries')} | "
            f"{(diagnostic.get('summary') or {}).get('wins')}/{(diagnostic.get('summary') or {}).get('losses')} | "
            f"{pct((diagnostic.get('summary') or {}).get('coverage_pct'))} | "
            f"{cents((diagnostic.get('summary') or {}).get('net_cents'))} | "
            f"{share((diagnostic.get('summary') or {}).get('reconstructed_share'))} | "
            f"{(diagnostic.get('summary') or {}).get('full_loss_cushion')} | prior rows found the union; not live-readiness proof |"
        ),
        (
            f"| strict/post context before own-freeze | context only | {(strict_context.get('summary') or {}).get('entries')} | "
            f"{(strict_context.get('summary') or {}).get('wins')}/{(strict_context.get('summary') or {}).get('losses')} | "
            f"{pct((strict_context.get('summary') or {}).get('coverage_pct'))} | "
            f"{cents((strict_context.get('summary') or {}).get('net_cents'))} | "
            f"{share((strict_context.get('summary') or {}).get('reconstructed_share'))} | "
            f"{(strict_context.get('summary') or {}).get('full_loss_cushion')} | useful but still born before exact union freeze |"
        ),
        (
            f"| post-freeze sidecar feature preview | collection health only | {preview_sidecar.get('entries')} | "
            f"{preview_sidecar.get('wins')}/{preview_sidecar.get('losses')} | {pct(preview_sidecar.get('coverage_pct'))} | "
            f"{cents(preview_sidecar.get('net_cents'))} | {share(preview_sidecar.get('reconstructed_share'))} | "
            f"{preview_sidecar.get('full_loss_cushion')} | feature availability and early row-shape check only |"
        ),
        (
            f"| post-freeze primary sizing-pocket proxy | risk proxy only | {preview_primary.get('entries')} | "
            f"{preview_primary.get('wins')}/{preview_primary.get('losses')} | {pct(preview_primary.get('coverage_pct'))} | "
            f"{cents(preview_primary.get('net_cents'))} | {share(preview_primary.get('reconstructed_share'))} | "
            f"{preview_primary.get('full_loss_cushion')} | sizing-pocket proxy, not actual primary selection |"
        ),
        "",
        f"- Preview observations/features: `{preview.get('post_freeze_observation_count')}` observations across "
        f"`{preview.get('post_freeze_distinct_markets')}` markets; availability `{preview.get('feature_availability')}`.",
        f"- Primary proxy note: {preview.get('primary_pocket_rule_note') or 'n/a'}",
        "",
        "## Own-Freeze Gate Rows",
        "",
        "| policy | settled | W/L | coverage | net | delta live | recon | cushion | live ready | missing gates |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---|---|",
    ]
    for row in report.get("unions") or []:
        lines.append(
            f"| `{row.get('policy')}` | {row.get('settled')} | {row.get('wins')}/{row.get('losses')} | "
            f"{pct(row.get('coverage_pct'))} | {cents(row.get('net_cents'))} | {cents(row.get('delta_vs_live_cents'))} | "
            f"{share(row.get('reconstructed_share'))} | {row.get('full_loss_cushion')} | `{row.get('live_ready')}` | "
            f"{', '.join(row.get('missing_gates') or []) or 'none'} |"
        )
    lines.extend(["", "## Interpretation", ""])
    lines.extend(f"- {item}" for item in report.get("interpretation") or [])

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8")
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    report = build_report()
    write_report(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
