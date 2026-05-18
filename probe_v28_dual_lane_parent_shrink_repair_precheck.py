"""Forced strict-replay precheck for the dual-lane parent-shrink repair.

Research-only; no live bot changes and no orders.

This writes a separate diagnostic artifact so forced replay does not overwrite
the normal own-freeze watch file. It is not promotion evidence before the
30-settled-row gate.
"""
from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import probe_v28_dual_lane_parent_shrink_watch as repair_watch


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
OUT_JSON = OUT_DIR / "v28_dual_lane_parent_shrink_repair_precheck_latest.json"
OUT_MD = OUT_DIR / "v28_dual_lane_parent_shrink_repair_precheck_latest.md"


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
    sidecar = row.get("sidecar") if isinstance(row.get("sidecar"), dict) else {}
    primary = row.get("primary") if isinstance(row.get("primary"), dict) else {}
    return {
        "policy": sidecar.get("policy"),
        "primary_policy": primary.get("policy"),
        "settled": summary.get("settled"),
        "wins": summary.get("wins"),
        "losses": summary.get("losses"),
        "coverage_pct": summary.get("coverage_pct"),
        "net_cents": summary.get("net_cents"),
        "reconstructed_share": summary.get("reconstructed_share"),
        "full_loss_cushion": summary.get("full_loss_cushion"),
        "source_counts": summary.get("source_counts"),
        "sidecar_add_net_cents": row.get("sidecar_add_net_cents"),
        "shared_markets": row.get("shared_markets"),
        "live_ready": row.get("live_ready"),
        "blockers": row.get("blockers") or [],
    }


def build_report() -> dict[str, Any]:
    old_force = os.environ.get("V28_DUAL_PARENT_SHRINK_FORCE_REPLAY")
    os.environ["V28_DUAL_PARENT_SHRINK_FORCE_REPLAY"] = "1"
    try:
        report = repair_watch.build_report()
    finally:
        if old_force is None:
            os.environ.pop("V28_DUAL_PARENT_SHRINK_FORCE_REPLAY", None)
        else:
            os.environ["V28_DUAL_PARENT_SHRINK_FORCE_REPLAY"] = old_force

    unions = [compact_union(row) for row in report.get("unions") or [] if isinstance(row, dict)]
    return {
        "generated_at_utc": utc_now_iso(),
        "source_probe": "probe_v28_dual_lane_parent_shrink_watch.build_report(force_replay=1)",
        "promotion_use": "not_promotion_evidence_before_min_sample",
        "freeze_ts_utc": (report.get("state") or {}).get("freeze_ts_utc"),
        "freeze_local_time": report.get("freeze_local_time"),
        "live_baseline_cents": report.get("live_baseline_cents"),
        "possible_market_windows_since_freeze": report.get("possible_market_windows_since_freeze"),
        "market_windows_remaining_to_min_sample": report.get("market_windows_remaining_to_min_sample"),
        "earliest_min_sample_local_time": report.get("earliest_min_sample_local_time"),
        "force_replay": report.get("force_replay"),
        "pre_sample_short_circuit": report.get("pre_sample_short_circuit"),
        "repair_rule": (report.get("state") or {}).get("shrink_rule"),
        "unions": unions,
        "best_union": unions[0] if unions else {},
        "read": [
            "Forced repair replay executed into a separate diagnostic artifact.",
            "Rows are not promotion evidence before the repair branch reaches its own 30-settled-row gate.",
            "Use this only to catch scorer/join/accounting failures before the real checkpoint.",
        ],
    }


def write_report(report: dict[str, Any]) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8")
    best = report.get("best_union") if isinstance(report.get("best_union"), dict) else {}
    lines = [
        "# v28 Dual-Lane Parent-Shrink Repair Precheck",
        "",
        "Research-only. No live bot logic changes, no orders.",
        "",
        f"- Generated UTC: `{report.get('generated_at_utc')}`",
        f"- Promotion use: `{report.get('promotion_use')}`",
        f"- Freeze UTC/local: `{report.get('freeze_ts_utc')}` / `{report.get('freeze_local_time')}`",
        f"- Live baseline: `{money(report.get('live_baseline_cents'))}`",
        f"- Windows since freeze / remaining: `{report.get('possible_market_windows_since_freeze')}` / `{report.get('market_windows_remaining_to_min_sample')}`",
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
            "## Best Forced Repair Union",
            "",
            "| policy | settled | W/L | coverage | net | recon | cushion | blockers |",
            "|---|---:|---:|---:|---:|---:|---:|---|",
            (
                f"| `{best.get('policy')}` | {best.get('settled')} | {best.get('wins')}/{best.get('losses')} | "
                f"{pct(best.get('coverage_pct'))} | {money(best.get('net_cents'))} | "
                f"{pct(best.get('reconstructed_share'), False)} | {best.get('full_loss_cushion')} | "
                f"{', '.join(str(item) for item in best.get('blockers') or [])} |"
            ),
            "",
            "## All Forced Repair Unions",
            "",
            "| policy | settled | W/L | coverage | net | recon | sidecar add | shared | blockers |",
            "|---|---:|---:|---:|---:|---:|---:|---:|---|",
        ]
    )
    for row in report.get("unions") or []:
        if not isinstance(row, dict):
            continue
        lines.append(
            f"| `{row.get('policy')}` | {row.get('settled')} | {row.get('wins')}/{row.get('losses')} | "
            f"{pct(row.get('coverage_pct'))} | {money(row.get('net_cents'))} | "
            f"{pct(row.get('reconstructed_share'), False)} | {money(row.get('sidecar_add_net_cents'))} | "
            f"{row.get('shared_markets')} | {', '.join(str(item) for item in row.get('blockers') or [])} |"
        )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    report = build_report()
    write_report(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
