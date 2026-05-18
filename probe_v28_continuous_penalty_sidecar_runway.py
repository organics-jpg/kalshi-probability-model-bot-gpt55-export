"""Runway audit for the continuous-penalty sidecar watch.

Research-only; no live bot changes or orders.

The sidecar watch says the post-penalty rank-only lane is one settled row away
from sample size. This probe adds the missing risk context: how far it is from
the refreshed live baseline, how many perfect wins are needed, and how much
loss/source capacity remains before the live-test gates break again.
"""
from __future__ import annotations

import json
import math
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
SOURCE_JSON = OUT_DIR / "v28_boundary_clock_feature_gate_continuous_penalty_latest.json"
LIVE_SUMMARY_JSON = ROOT / "stats" / "live_mushroom_v28_size2" / "summary.json"
OUT_JSON = OUT_DIR / "v28_continuous_penalty_sidecar_runway_latest.json"
OUT_MD = OUT_DIR / "v28_continuous_penalty_sidecar_runway_latest.md"

MIN_SETTLED = 30
MAX_RECON_SHARE = 0.35
MIN_CUSHION = 3
MAX_SINGLE_WIN_CENTS = 100.0


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


def live_cents() -> float:
    live = load_json(LIVE_SUMMARY_JSON)
    return 100.0 * (as_float(live.get("net_pnl_total_dollars")) or 0.0)


def net(row: dict[str, Any]) -> float:
    return as_float(row.get("net_cents")) or 0.0


def summarize_variant(lane: dict[str, Any], variant: dict[str, Any], live_net: float) -> dict[str, Any]:
    rows = [row for row in variant.get("rows") or [] if isinstance(row, dict)]
    entries = len(rows)
    settled = sum(1 for row in rows if row.get("side_won") is not None)
    wins = sum(1 for row in rows if net(row) > 0)
    losses = sum(1 for row in rows if net(row) < 0)
    total = sum(net(row) for row in rows)
    approved = sum(1 for row in rows if row.get("source") == "approved_entry")
    rejected = sum(1 for row in rows if row.get("source") != "approved_entry")
    deficit = max(0.0, live_net + 1.0 - total)
    rows_to_sample = max(0, MIN_SETTLED - settled)
    perfect_wins_to_live = math.ceil(deficit / MAX_SINGLE_WIN_CENTS) if deficit > 0 else 0
    max_rejected_at_current_entries = math.floor(MAX_RECON_SHARE * entries)
    rejected_capacity_now = max(0, max_rejected_at_current_entries - rejected)
    max_full_losses_before_cushion_break = max(0, math.floor((total - MIN_CUSHION * 100.0) / 100.0))
    return {
        "lane": lane.get("lane"),
        "candidate": variant.get("candidate"),
        "future_denominator": lane.get("future_denominator"),
        "entries": entries,
        "settled": settled,
        "wins": wins,
        "losses": losses,
        "net_cents": total,
        "coverage_pct": (entries / (as_float(lane.get("future_denominator")) or entries) * 100.0) if entries else 0.0,
        "approved_rows": approved,
        "rejected_or_reconstructed_rows": rejected,
        "reconstructed_share": rejected / entries if entries else None,
        "full_loss_cushion": math.floor(total / 100.0) if total > 0 else 0,
        "delta_vs_live_cents": total - live_net,
        "rows_to_sample": rows_to_sample,
        "additional_net_to_beat_live_cents": deficit,
        "perfect_full_wins_to_beat_live": perfect_wins_to_live,
        "rejected_capacity_at_current_entry_count": rejected_capacity_now,
        "max_full_losses_before_cushion_break": max_full_losses_before_cushion_break,
        "blockers": blockers(settled, total, rejected / entries if entries else None, live_net),
    }


def blockers(settled: int, total: float, recon: float | None, live_net: float) -> list[str]:
    out = []
    if settled < MIN_SETTLED:
        out.append("settled_lt_30")
    if total <= 0.0:
        out.append("net_not_positive")
    if recon is None or recon > MAX_RECON_SHARE:
        out.append("reconstructed_share_gt_35pct")
    if math.floor(total / 100.0) < MIN_CUSHION:
        out.append("full_loss_cushion_lt_3")
    if total <= live_net:
        out.append("does_not_beat_refreshed_live_baseline")
    out.append("live_ready_false")
    return out


def build_report() -> dict[str, Any]:
    payload = load_json(SOURCE_JSON)
    live_net = live_cents()
    rows = []
    for lane in payload.get("lanes") or []:
        if not isinstance(lane, dict) or not str(lane.get("lane") or "").startswith("post_penalty_birth_"):
            continue
        for variant in lane.get("variants") or []:
            if not isinstance(variant, dict):
                continue
            candidate = str(variant.get("candidate") or "")
            if not candidate.endswith("rank_only"):
                continue
            rows.append(summarize_variant(lane, variant, live_net))
    rows.sort(key=lambda row: (len(row.get("blockers") or []), -(as_float(row.get("net_cents")) or 0.0), str(row.get("candidate"))))
    return {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "source_artifact": str(SOURCE_JSON),
        "live_baseline_cents": live_net,
        "rows": rows,
        "best": rows[0] if rows else {},
        "candidate_live_ready": False,
        "interpretation": interpretation(rows, live_net),
    }


def interpretation(rows: list[dict[str, Any]], live_net: float) -> list[str]:
    if not rows:
        return ["No post-penalty birth rank-only rows are available."]
    best = rows[0]
    return [
        f"Best continuous-penalty sidecar has {best.get('settled')} settled, W/L {best.get('wins')}/{best.get('losses')}, net {best.get('net_cents')}c, and source share {best.get('reconstructed_share')}.",
        f"It needs {best.get('rows_to_sample')} more settled row for sample, but {best.get('additional_net_to_beat_live_cents')}c more PnL to beat the refreshed live baseline of {live_net}c.",
        f"At a 100c maximum single-row win assumption, it needs at least {best.get('perfect_full_wins_to_beat_live')} additional perfect wins, not just one sample row.",
        f"Current cushion can absorb {best.get('max_full_losses_before_cushion_break')} full-loss rows before falling below the three-full-loss gate.",
    ]


def fmt(value: Any) -> str:
    if value is None:
        return "None"
    if isinstance(value, float):
        return f"{value:.6f}"
    return str(value)


def write_md(report: dict[str, Any]) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8")
    best = report.get("best") or {}
    lines = [
        "# v28 Continuous-Penalty Sidecar Runway",
        "",
        "Research-only runway audit. No live orders.",
        "",
        f"- Generated UTC: `{report.get('generated_at_utc')}`",
        f"- Live baseline: `{fmt(report.get('live_baseline_cents'))}c`",
        f"- Candidate live-ready: `{report.get('candidate_live_ready')}`",
        f"- Best candidate: `{best.get('lane')} / {best.get('candidate')}`",
        f"- Best settled/W-L/net/source/cushion: `{best.get('settled')}/{best.get('wins')}-{best.get('losses')}/{fmt(best.get('net_cents'))}c/{fmt(best.get('reconstructed_share'))}/{best.get('full_loss_cushion')}`",
        f"- Rows to sample / net to live / perfect wins to live: `{best.get('rows_to_sample')}/{fmt(best.get('additional_net_to_beat_live_cents'))}c/{best.get('perfect_full_wins_to_beat_live')}`",
        f"- Full losses before cushion breaks: `{best.get('max_full_losses_before_cushion_break')}`",
        f"- Blockers: `{', '.join(best.get('blockers') or []) or 'none'}`",
        "",
        "## Interpretation",
        "",
    ]
    for note in report.get("interpretation") or []:
        lines.append(f"- {note}")
    lines.extend([
        "",
        "## Rank-Only Rows",
        "",
        "| lane | candidate | settled | W-L | net c | delta live | source | cushion | sample need | perfect wins to live | full-loss capacity | blockers |",
        "|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|",
    ])
    for row in report.get("rows") or []:
        lines.append(
            f"| `{row.get('lane')}` | `{row.get('candidate')}` | {row.get('settled')} | {row.get('wins')}-{row.get('losses')} | "
            f"{fmt(row.get('net_cents'))} | {fmt(row.get('delta_vs_live_cents'))} | {fmt(row.get('reconstructed_share'))} | "
            f"{row.get('full_loss_cushion')} | {row.get('rows_to_sample')} | {row.get('perfect_full_wins_to_beat_live')} | "
            f"{row.get('max_full_losses_before_cushion_break')} | `{', '.join(row.get('blockers') or []) or 'none'}` |"
        )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    report = build_report()
    write_md(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
