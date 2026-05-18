"""Accounting audit for the v28 dual-lane strict replay scorer.

Research-only; no live bot changes and no orders.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
OWN_FREEZE_PY = ROOT / "probe_v28_dual_lane_own_freeze_watch.py"
PRECHECK_JSON = OUT_DIR / "v28_dual_lane_strict_replay_precheck_latest.json"
OUT_JSON = OUT_DIR / "v28_dual_lane_strict_replay_accounting_audit_latest.json"
OUT_MD = OUT_DIR / "v28_dual_lane_strict_replay_accounting_audit_latest.md"


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


def build_report() -> dict[str, Any]:
    source_text = OWN_FREEZE_PY.read_text(encoding="utf-8") if OWN_FREEZE_PY.exists() else ""
    precheck = load_json(PRECHECK_JSON)
    best = precheck.get("best_union") if isinstance(precheck.get("best_union"), dict) else {}
    source_uses_feature_gate_net = "feature_gate_net(row)" in source_text
    imports_feature_gate_net = "net as feature_gate_net" in source_text
    sidecar_add_net = best.get("sidecar_add_net_cents")
    best_net = best.get("net_cents")
    settled = int(best.get("settled") or 0)
    return {
        "generated_at_utc": utc_now_iso(),
        "audited_file": str(OWN_FREEZE_PY),
        "precheck_file": str(PRECHECK_JSON),
        "imports_feature_gate_net": imports_feature_gate_net,
        "sidecar_compaction_uses_feature_gate_net": source_uses_feature_gate_net,
        "accounting_patch_verified": imports_feature_gate_net and source_uses_feature_gate_net,
        "precheck_generated_at_utc": precheck.get("generated_at_utc"),
        "promotion_use": precheck.get("promotion_use"),
        "possible_market_windows_since_freeze": precheck.get("possible_market_windows_since_freeze"),
        "best_union": best,
        "score_path_read": (
            "strict_replay_sidecar_net_uses_boundary_clock_feature_gate_net"
            if imports_feature_gate_net and source_uses_feature_gate_net
            else "strict_replay_sidecar_net_path_unverified"
        ),
        "precheck_read": {
            "settled": settled,
            "net_cents": best_net,
            "sidecar_add_net_cents": sidecar_add_net,
            "nonzero_sidecar_add": sidecar_add_net is not None and float(sidecar_add_net) != 0.0,
            "blockers": best.get("blockers") or [],
        },
    }


def write_md(report: dict[str, Any]) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8")
    best = report.get("best_union") if isinstance(report.get("best_union"), dict) else {}
    lines = [
        "# v28 Dual-Lane Strict Replay Accounting Audit",
        "",
        "Research-only. No live bot logic changes, no orders.",
        "",
        f"- Generated UTC: `{report.get('generated_at_utc')}`",
        f"- Audited file: `{report.get('audited_file')}`",
        f"- Precheck artifact: `{report.get('precheck_file')}`",
        f"- Accounting patch verified: `{report.get('accounting_patch_verified')}`",
        f"- Score path read: `{report.get('score_path_read')}`",
        f"- Precheck promotion use: `{report.get('promotion_use')}`",
        f"- Precheck windows: `{report.get('possible_market_windows_since_freeze')}`",
        "",
        "## Checks",
        "",
        "| check | status |",
        "|---|---|",
        f"| imports `feature_gate_net` | `{report.get('imports_feature_gate_net')}` |",
        f"| sidecar compaction uses `feature_gate_net(row)` | `{report.get('sidecar_compaction_uses_feature_gate_net')}` |",
        f"| latest precheck has nonzero sidecar add | `{(report.get('precheck_read') or {}).get('nonzero_sidecar_add')}` |",
        "",
        "## Latest Strict Precheck",
        "",
        "| policy | settled | W/L | coverage | net | sidecar add | recon | cushion | blockers |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---|",
        (
            f"| `{best.get('sidecar_policy')}` | {best.get('settled')} | {best.get('wins')}/{best.get('losses')} | "
            f"{pct(best.get('coverage_pct'))} | {money(best.get('net_cents'))} | "
            f"{money(best.get('sidecar_add_net_cents'))} | {pct(best.get('reconstructed_share'), False)} | "
            f"{best.get('full_loss_cushion')} | {', '.join(str(item) for item in best.get('blockers') or [])} |"
        ),
        "",
        "## Interpretation",
        "",
        "- This audit verifies the research scorer wiring, not live readiness.",
        "- The strict precheck remains diagnostic until the 30-settled-row own-freeze sample gate is available.",
        "- The main remaining blocker is evidence maturity, not the sidecar PnL accounting path.",
    ]
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    report = build_report()
    write_md(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
