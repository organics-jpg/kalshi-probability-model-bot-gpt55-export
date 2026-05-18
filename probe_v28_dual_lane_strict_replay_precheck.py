"""Manual strict-replay precheck for the v28 dual-lane own-freeze scorer.

Research-only; no live bot changes and no orders.

This deliberately forces the heavy own-freeze replay before the 30-window sample
gate, then writes a separate precheck artifact. It must not be used as promotion
evidence while the sample is immature.
"""
from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import probe_v28_dual_lane_own_freeze_watch as own_freeze


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
OUT_JSON = OUT_DIR / "v28_dual_lane_strict_replay_precheck_latest.json"
OUT_MD = OUT_DIR / "v28_dual_lane_strict_replay_precheck_latest.md"


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def money(value: Any) -> str:
    try:
        cents = float(value)
    except (TypeError, ValueError):
        return "n/a"
    return f"{cents:.0f}c (${cents / 100.0:.2f})"


def pct(value: Any, already_pct: bool = True) -> str:
    if value is None:
        return "n/a"
    try:
        number = float(value)
    except (TypeError, ValueError):
        return "n/a"
    if not already_pct:
        number *= 100.0
    return f"{number:.2f}%"


def compact_union(row: dict[str, Any]) -> dict[str, Any]:
    summary = row.get("summary") if isinstance(row.get("summary"), dict) else {}
    primary = row.get("primary") if isinstance(row.get("primary"), dict) else {}
    sidecar = row.get("sidecar") if isinstance(row.get("sidecar"), dict) else {}
    return {
        "sidecar_policy": sidecar.get("policy"),
        "primary_policy": primary.get("policy"),
        "settled": summary.get("settled"),
        "wins": summary.get("wins"),
        "losses": summary.get("losses"),
        "net_cents": summary.get("net_cents"),
        "coverage_pct": summary.get("coverage_pct"),
        "reconstructed_share": summary.get("reconstructed_share"),
        "full_loss_cushion": summary.get("full_loss_cushion"),
        "source_counts": summary.get("source_counts"),
        "shared_markets": row.get("shared_markets"),
        "sidecar_add_entries": row.get("sidecar_add_entries"),
        "sidecar_add_net_cents": row.get("sidecar_add_net_cents"),
        "live_ready": row.get("live_ready"),
        "blockers": row.get("blockers") or [],
        "worst_rows": row.get("rows") or [],
        "primary_diagnostics": primary.get("diagnostics"),
    }


def build_report() -> dict[str, Any]:
    old_force = os.environ.get("V28_DUAL_FORCE_REPLAY")
    os.environ["V28_DUAL_FORCE_REPLAY"] = "1"
    try:
        report = own_freeze.build_report()
    finally:
        if old_force is None:
            os.environ.pop("V28_DUAL_FORCE_REPLAY", None)
        else:
            os.environ["V28_DUAL_FORCE_REPLAY"] = old_force

    unions = [compact_union(row) for row in report.get("unions") or [] if isinstance(row, dict)]
    best = unions[0] if unions else {}
    return {
        "generated_at_utc": utc_now_iso(),
        "source_probe": "probe_v28_dual_lane_own_freeze_watch.build_report(force_replay=1)",
        "promotion_use": "not_promotion_evidence_before_min_sample",
        "freeze_ts_utc": (report.get("state") or {}).get("freeze_ts_utc"),
        "freeze_local_time": report.get("freeze_local_time"),
        "live_baseline_cents": report.get("live_baseline_cents"),
        "possible_market_windows_since_freeze": report.get("possible_market_windows_since_freeze"),
        "market_windows_remaining_to_min_sample": report.get("market_windows_remaining_to_min_sample"),
        "earliest_min_sample_utc": report.get("earliest_min_sample_utc"),
        "earliest_min_sample_local_time": report.get("earliest_min_sample_local_time"),
        "force_replay": report.get("force_replay"),
        "pre_sample_short_circuit": report.get("pre_sample_short_circuit"),
        "unions": unions,
        "best_union": best,
        "read": [
            "Heavy strict replay path executed successfully.",
            "Rows are diagnostic precheck only until the 30-settled-row own-freeze gate is available.",
            "Use this to detect scorer/join failures early, not to approve live testing.",
        ],
    }


def write_md(report: dict[str, Any]) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8")
    best = report.get("best_union") if isinstance(report.get("best_union"), dict) else {}
    lines = [
        "# v28 Dual-Lane Strict Replay Precheck",
        "",
        "Research-only. No live bot logic changes, no orders.",
        "",
        f"- Generated UTC: `{report.get('generated_at_utc')}`",
        f"- Promotion use: `{report.get('promotion_use')}`",
        f"- Freeze UTC/local: `{report.get('freeze_ts_utc')}` / `{report.get('freeze_local_time')}`",
        f"- Live baseline: `{money(report.get('live_baseline_cents'))}`",
        f"- Possible windows / remaining: `{report.get('possible_market_windows_since_freeze')}` / `{report.get('market_windows_remaining_to_min_sample')}`",
        f"- Earliest 30-window local time: `{report.get('earliest_min_sample_local_time')}`",
        f"- Force replay: `{report.get('force_replay')}`",
        f"- Pre-sample short-circuit: `{report.get('pre_sample_short_circuit')}`",
        "",
        "## Read",
        "",
    ]
    lines.extend(f"- {item}" for item in report.get("read") or [])
    lines.extend(
        [
            "",
            "## Best Forced-Replay Union",
            "",
            "| policy | settled | W/L | coverage | net | recon | cushion | source counts | blockers |",
            "|---|---:|---:|---:|---:|---:|---:|---|---|",
            (
                f"| `{best.get('sidecar_policy')}` | {best.get('settled')} | "
                f"{best.get('wins')}/{best.get('losses')} | {pct(best.get('coverage_pct'))} | "
                f"{money(best.get('net_cents'))} | {pct(best.get('reconstructed_share'), False)} | "
                f"{best.get('full_loss_cushion')} | `{best.get('source_counts')}` | "
                f"{', '.join(str(item) for item in best.get('blockers') or [])} |"
            ),
            "",
            "## All Forced-Replay Unions",
            "",
            "| sidecar | settled | W/L | coverage | net | recon | shared | add net | blockers |",
            "|---|---:|---:|---:|---:|---:|---:|---:|---|",
        ]
    )
    for row in report.get("unions") or []:
        if not isinstance(row, dict):
            continue
        lines.append(
            f"| `{row.get('sidecar_policy')}` | {row.get('settled')} | "
            f"{row.get('wins')}/{row.get('losses')} | {pct(row.get('coverage_pct'))} | "
            f"{money(row.get('net_cents'))} | {pct(row.get('reconstructed_share'), False)} | "
            f"{row.get('shared_markets')} | {money(row.get('sidecar_add_net_cents'))} | "
            f"{', '.join(str(item) for item in row.get('blockers') or [])} |"
        )
    worst_rows = best.get("worst_rows") if isinstance(best.get("worst_rows"), list) else []
    if worst_rows:
        lines.extend(
            [
                "",
                "## Worst Rows",
                "",
                "| market | side | source | component | net | raw edge | recross | abs d | ask |",
                "|---|---|---|---|---:|---:|---:|---:|---:|",
            ]
        )
        for row in worst_rows[:10]:
            if not isinstance(row, dict):
                continue
            lines.append(
                f"| `{row.get('market')}` | {row.get('side')} | {row.get('source')} | {row.get('component')} | "
                f"{money(row.get('final_weighted_cents') if row.get('final_weighted_cents') is not None else row.get('weighted_net_cents'))} | "
                f"{row.get('raw_edge')} | {row.get('recross_hazard_score')} | {row.get('abs_d_sigma')} | {row.get('ask_prob')} |"
            )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    report = build_report()
    write_md(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
