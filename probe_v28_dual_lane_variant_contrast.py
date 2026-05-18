"""Variant contrast for v28 dual-lane entry vs bridge unions.

Research-only; no live bot changes and no orders.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
PRECHECK_JSON = OUT_DIR / "v28_dual_lane_strict_replay_precheck_latest.json"
UPDATE_JSON = OUT_DIR / "v28_dual_lane_live_market_update_latest.json"
OUT_JSON = OUT_DIR / "v28_dual_lane_variant_contrast_latest.json"
OUT_MD = OUT_DIR / "v28_dual_lane_variant_contrast_latest.md"


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
        return float(value)
    except (TypeError, ValueError):
        return default


def money(value: Any) -> str:
    return f"{fnum(value):.0f}c (${fnum(value) / 100.0:.2f})"


def pct(value: Any, already_pct: bool = True) -> str:
    if value is None:
        return "n/a"
    number = fnum(value)
    if not already_pct:
        number *= 100.0
    return f"{number:.2f}%"


def variant_name(row: dict[str, Any]) -> str:
    policy = str(row.get("sidecar_policy") or "")
    if "_bridge_" in policy:
        return "bridge"
    if "_entry_" in policy:
        return "entry"
    return policy or "unknown"


def rank_variants(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return sorted(
        rows,
        key=lambda row: (
            len(row.get("blockers") or []),
            -fnum(row.get("net_cents")),
            -fnum(row.get("coverage_pct")),
        ),
    )


def build_report() -> dict[str, Any]:
    precheck = load_json(PRECHECK_JSON)
    update = load_json(UPDATE_JSON)
    rows = [row for row in precheck.get("unions") or [] if isinstance(row, dict)]
    ranked = rank_variants(rows)
    by_name = {variant_name(row): row for row in rows}
    entry = by_name.get("entry", {})
    bridge = by_name.get("bridge", {})
    net_delta_bridge_minus_entry = fnum(bridge.get("net_cents")) - fnum(entry.get("net_cents"))
    coverage_delta_bridge_minus_entry = fnum(bridge.get("coverage_pct")) - fnum(entry.get("coverage_pct"))
    bridge_is_current_preferred = bool(ranked and variant_name(ranked[0]) == "bridge")
    return {
        "generated_at_utc": utc_now_iso(),
        "promotion_use": precheck.get("promotion_use"),
        "precheck_generated_at_utc": precheck.get("generated_at_utc"),
        "precheck_windows": precheck.get("possible_market_windows_since_freeze"),
        "current_windows": update.get("possible_windows_since_freeze"),
        "live_baseline_cents": update.get("live_baseline_cents") or precheck.get("live_baseline_cents"),
        "ranked_variants": ranked,
        "entry_variant": entry,
        "bridge_variant": bridge,
        "bridge_minus_entry_net_cents": net_delta_bridge_minus_entry,
        "bridge_minus_entry_coverage_pct": coverage_delta_bridge_minus_entry,
        "bridge_is_current_preferred": bridge_is_current_preferred,
        "read": [
            "Forced replay precheck is diagnostic until 30 strict-forward settled rows exist.",
            (
                "Bridge union is currently the better forced-replay lane."
                if bridge_is_current_preferred
                else "Entry union is currently the better forced-replay lane."
            ),
            "At the 30-window gate, prefer the lane that clears all gates, not the one with the best immature precheck PnL.",
        ],
    }


def write_md(report: dict[str, Any]) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8")
    lines = [
        "# v28 Dual-Lane Variant Contrast",
        "",
        "Research-only. No live bot logic changes, no orders.",
        "",
        f"- Generated UTC: `{report.get('generated_at_utc')}`",
        f"- Precheck UTC: `{report.get('precheck_generated_at_utc')}`",
        f"- Promotion use: `{report.get('promotion_use')}`",
        f"- Precheck/current windows: `{report.get('precheck_windows')}` / `{report.get('current_windows')}`",
        f"- Live baseline: `{money(report.get('live_baseline_cents'))}`",
        f"- Bridge minus entry net: `{money(report.get('bridge_minus_entry_net_cents'))}`",
        f"- Bridge minus entry coverage: `{pct(report.get('bridge_minus_entry_coverage_pct'))}`",
        f"- Current preferred precheck lane: `{'bridge' if report.get('bridge_is_current_preferred') else 'entry'}`",
        "",
        "## Read",
        "",
    ]
    lines.extend(f"- {item}" for item in report.get("read") or [])
    lines.extend(
        [
            "",
            "## Forced-Replay Variants",
            "",
            "| rank | lane | settled | W/L | coverage | net | recon | cushion | sidecar add | shared | blockers |",
            "|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---|",
        ]
    )
    for idx, row in enumerate(report.get("ranked_variants") or [], 1):
        lines.append(
            f"| {idx} | `{variant_name(row)}` | {row.get('settled')} | {row.get('wins')}/{row.get('losses')} | "
            f"{pct(row.get('coverage_pct'))} | {money(row.get('net_cents'))} | "
            f"{pct(row.get('reconstructed_share'), False)} | {row.get('full_loss_cushion')} | "
            f"{money(row.get('sidecar_add_net_cents'))} | {row.get('shared_markets')} | "
            f"{', '.join(str(item) for item in row.get('blockers') or [])} |"
        )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    report = build_report()
    write_md(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
