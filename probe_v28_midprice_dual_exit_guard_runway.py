"""Runway monitor for the current top midprice-boundary dual-exit guard.

Research-only; no live bot changes or orders.

The guard-refinement probe owns the row-level replay. This compact report turns
that replay into a promotion-gate runway so the top diagnostic branch can be
watched without reading the full joined-row ledger every cycle.
"""
from __future__ import annotations

import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
GUARD_JSON = OUT_DIR / "v28_soft_frontier_midprice_boundary_dual_exit_guard_refinement_latest.json"
LIVE_SUMMARY_JSON = ROOT / "stats" / "live_mushroom_v28_size2" / "summary.json"
OUT_JSON = OUT_DIR / "v28_midprice_dual_exit_guard_runway_latest.json"
OUT_MD = OUT_DIR / "v28_midprice_dual_exit_guard_runway_latest.md"

MIN_JOINED_ROWS = 30
MIN_SUPPRESSED_ROWS = 30
MAX_RECONSTRUCTED_SHARE = 0.35
MIN_FULL_LOSS_CUSHION_CENTS = 300.0
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


def as_float(value: Any) -> float | None:
    if value is None or value == "":
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


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


def at_or_after(value: Any, freeze_ts: str | None) -> bool:
    ts = parse_ts(value)
    freeze = parse_ts(freeze_ts)
    return bool(ts and freeze and ts >= freeze)


def full_loss_cushion(net_cents: float | None) -> int:
    if net_cents is None:
        return 0
    return int(max(0.0, net_cents) // 100.0)


def source_share(rows: list[dict[str, Any]]) -> float | None:
    if not rows:
        return None
    counts = Counter(str(row.get("source") or "unknown") for row in rows)
    total = sum(counts.values())
    approved = counts.get("approved_entry", 0)
    if total <= 0:
        return None
    return (total - approved) / total


def clean_rows_needed(reconstructed: int, selected: int) -> int | None:
    if selected <= 0:
        return None
    for rows in range(0, 500):
        if reconstructed / (selected + rows) <= MAX_RECONSTRUCTED_SHARE:
            return rows
    return 500


def wl(rows: list[dict[str, Any]], key: str = "weighted_candidate_cents") -> dict[str, int]:
    wins = losses = flats = 0
    for row in rows:
        value = as_float(row.get(key)) or 0.0
        if value > 0:
            wins += 1
        elif value < 0:
            losses += 1
        else:
            flats += 1
    return {"wins": wins, "losses": losses, "flats": flats}


def row_net(rows: list[dict[str, Any]], key: str = "weighted_candidate_cents") -> float:
    return sum(as_float(row.get(key)) or 0.0 for row in rows)


def summarize_variant(row: dict[str, Any], freeze_ts: str | None, live_net_cents: float | None) -> dict[str, Any]:
    joined_rows = [item for item in row.get("joined_rows") or [] if isinstance(item, dict)]
    post_rows = [
        item for item in joined_rows
        if at_or_after(item.get("entry_ts") or item.get("exit_ts"), freeze_ts)
    ]
    suppressed = [item for item in joined_rows if item.get("suppressed")]
    post_suppressed = [item for item in post_rows if item.get("suppressed")]
    post_source_counts = Counter(str(item.get("source") or "unknown") for item in post_rows)
    post_reconstructed = sum(post_source_counts.values()) - post_source_counts.get("approved_entry", 0)
    post_net = row_net(post_rows)
    diagnostic_net = as_float(row.get("weighted_candidate_cents"))
    entry = row.get("entry_summary") if isinstance(row.get("entry_summary"), dict) else {}
    coverage = as_float(entry.get("coverage_pct"))
    diagnostic_share = source_share(joined_rows)
    post_share = source_share(post_rows)
    post_cushion = full_loss_cushion(post_net)
    blockers = list(row.get("blockers") or [])
    missing: list[str] = []
    if len(post_rows) < MIN_JOINED_ROWS:
        missing.append(f"post_joined_rows+{MIN_JOINED_ROWS - len(post_rows)}")
    if len(post_suppressed) < MIN_SUPPRESSED_ROWS:
        missing.append(f"post_suppressed_rows+{MIN_SUPPRESSED_ROWS - len(post_suppressed)}")
    if post_net <= 0:
        missing.append("post_positive_pnl")
    if post_net < MIN_FULL_LOSS_CUSHION_CENTS:
        missing.append(f"post_cushion_cents+{MIN_FULL_LOSS_CUSHION_CENTS - post_net:.0f}")
    if coverage is None or coverage < TARGET_COVERAGE_MIN or coverage > TARGET_COVERAGE_MAX:
        missing.append("target_coverage")
    if post_share is None:
        missing.append("post_source_sample_empty")
    elif post_share > MAX_RECONSTRUCTED_SHARE:
        missing.append(f"post_clean_rows+{clean_rows_needed(post_reconstructed, len(post_rows))}")
    if blockers:
        missing.append("guard_probe_blockers_present")
    if not row.get("live_ready"):
        missing.append("live_ready_false")
    return {
        "policy": row.get("policy"),
        "guard": row.get("guard"),
        "lane": row.get("lane"),
        "strict_forward": bool(row.get("strict_forward")),
        "coverage_pct": coverage,
        "diagnostic_joined_rows": len(joined_rows),
        "diagnostic_suppressed_rows": len(suppressed),
        "diagnostic_net_cents": diagnostic_net,
        "diagnostic_wl": wl(joined_rows),
        "diagnostic_reconstructed_share": diagnostic_share,
        "post_joined_rows": len(post_rows),
        "post_suppressed_rows": len(post_suppressed),
        "post_net_cents": post_net,
        "post_wl": wl(post_rows),
        "post_source_counts": dict(post_source_counts),
        "post_reconstructed_share": post_share,
        "post_full_loss_cushion": post_cushion,
        "post_delta_vs_live_cents": None if live_net_cents is None else post_net - live_net_cents,
        "missing_gates": missing,
        "blockers": blockers,
        "live_ready": False if missing else bool(row.get("live_ready")),
    }


def build_report() -> dict[str, Any]:
    guard = load_json(GUARD_JSON)
    live = load_json(LIVE_SUMMARY_JSON)
    freeze = guard.get("freeze") if isinstance(guard.get("freeze"), dict) else {}
    freeze_ts = freeze.get("freeze_ts_utc")
    live_net = as_float(live.get("net_pnl_total_dollars"))
    live_net_cents = None if live_net is None else live_net * 100.0
    variants = [row for row in guard.get("variants") or [] if isinstance(row, dict)]
    summaries = [summarize_variant(row, freeze_ts, live_net_cents) for row in variants]
    summaries.sort(
        key=lambda row: (
            row.get("live_ready") is True,
            as_float(row.get("diagnostic_net_cents")) or -1e9,
            as_float(row.get("post_net_cents")) or -1e9,
        ),
        reverse=True,
    )
    best = summaries[0] if summaries else {}
    return {
        "generated_at_utc": utc_now_iso(),
        "source": str(GUARD_JSON),
        "freeze_ts_utc": freeze_ts,
        "live_baseline_net_cents": live_net_cents,
        "candidate_live_ready": any(bool(row.get("live_ready")) for row in summaries),
        "best_policy": best.get("policy"),
        "best_missing_gates": best.get("missing_gates"),
        "variants": summaries,
        "interpretation": [
            "This report is a runway monitor for the current top diagnostic branch, not a promotion override.",
            "Pre-freeze diagnostic rows show mechanism strength; only post-freeze joined/suppressed rows count for live readiness.",
            f"Best current policy {best.get('policy')} has diagnostic net {best.get('diagnostic_net_cents')}c, post net {best.get('post_net_cents')}c, and missing gates {best.get('missing_gates')}.",
        ],
    }


def fmt_cents(value: Any) -> str:
    number = as_float(value)
    if number is None:
        return "n/a"
    return f"{number:.0f}c (${number / 100.0:.2f})"


def fmt_pct(value: Any) -> str:
    number = as_float(value)
    if number is None:
        return "n/a"
    return f"{number * 100.0:.1f}%" if number <= 1.0 else f"{number:.1f}%"


def write_outputs(report: dict[str, Any]) -> None:
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8")
    lines = [
        "# v28 Midprice Dual-Exit Guard Runway",
        "",
        "Research-only runway monitor. No live bot changes or orders.",
        "",
        f"- Generated UTC: `{report.get('generated_at_utc')}`",
        f"- Guard freeze UTC: `{report.get('freeze_ts_utc')}`",
        f"- Live baseline net: `{fmt_cents(report.get('live_baseline_net_cents'))}`",
        f"- Any live-ready guard candidate: `{report.get('candidate_live_ready')}`",
        f"- Best policy: `{report.get('best_policy')}`",
        f"- Best missing gates: `{report.get('best_missing_gates')}`",
        "",
        "## Guard Variants",
        "",
        "| rank | policy | coverage | diag rows | diag W/L | diag net | diag recon | post rows | post suppress | post W/L | post net | post recon | post cushion | live ready |",
        "|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|",
    ]
    for idx, row in enumerate(report.get("variants") or [], start=1):
        diag_wl = row.get("diagnostic_wl") or {}
        post_wl = row.get("post_wl") or {}
        lines.append(
            "| {rank} | `{policy}` | {coverage} | {diag_rows} | {diag_wins}/{diag_losses} | {diag_net} | {diag_share} | {post_rows} | {post_supp} | {post_wins}/{post_losses} | {post_net} | {post_share} | {post_cushion} | {ready} |".format(
                rank=idx,
                policy=row.get("policy"),
                coverage=fmt_pct(row.get("coverage_pct")),
                diag_rows=row.get("diagnostic_joined_rows"),
                diag_wins=diag_wl.get("wins"),
                diag_losses=diag_wl.get("losses"),
                diag_net=fmt_cents(row.get("diagnostic_net_cents")),
                diag_share=fmt_pct(row.get("diagnostic_reconstructed_share")),
                post_rows=row.get("post_joined_rows"),
                post_supp=row.get("post_suppressed_rows"),
                post_wins=post_wl.get("wins"),
                post_losses=post_wl.get("losses"),
                post_net=fmt_cents(row.get("post_net_cents")),
                post_share=fmt_pct(row.get("post_reconstructed_share")),
                post_cushion=row.get("post_full_loss_cushion"),
                ready=row.get("live_ready"),
            )
        )
    lines.extend([
        "",
        "## Interpretation",
        "",
    ])
    for note in report.get("interpretation") or []:
        lines.append(f"- {note}")
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    report = build_report()
    write_outputs(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
