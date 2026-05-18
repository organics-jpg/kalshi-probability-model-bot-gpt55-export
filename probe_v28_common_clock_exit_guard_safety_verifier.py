"""Safety verifier for the dormant common-clock v28 exit guard.

Research-only; no live bot changes, process control, API calls, or orders.

This verifier checks source-level invariants that must hold before the paper
shadow path is trusted:
- default guard mode is disabled
- reconciliation is opt-in
- enforcement is only possible in explicit enforce mode
- disabled mode emits no guard shadow ledger
"""
from __future__ import annotations

import ast
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
LIVE_BOT = ROOT / "kalshi_btc15m_bot_ws.py"
IMPLEMENTATION_GAP_JSON = OUT_DIR / "v28_common_clock_exit_guard_implementation_gap_latest.json"
OUT_JSON = OUT_DIR / "v28_common_clock_exit_guard_safety_verifier_latest.json"
OUT_MD = OUT_DIR / "v28_common_clock_exit_guard_safety_verifier_latest.md"


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


def source() -> str:
    return LIVE_BOT.read_text(encoding="utf-8", errors="ignore") if LIVE_BOT.exists() else ""


def dataclass_defaults(src: str, class_name: str) -> dict[str, Any]:
    tree = ast.parse(src)
    defaults: dict[str, Any] = {}
    for node in tree.body:
        if not isinstance(node, ast.ClassDef) or node.name != class_name:
            continue
        for item in node.body:
            if not isinstance(item, ast.AnnAssign) or not isinstance(item.target, ast.Name):
                continue
            if item.value is None:
                continue
            try:
                defaults[item.target.id] = ast.literal_eval(item.value)
            except (ValueError, SyntaxError):
                defaults[item.target.id] = ast.unparse(item.value)
    return defaults


def check(name: str, passed: bool, evidence: Any, required: str) -> dict[str, Any]:
    return {
        "name": name,
        "passed": bool(passed),
        "status": "pass" if passed else "fail",
        "evidence": evidence,
        "required": required,
    }


def build_report() -> dict[str, Any]:
    src = source()
    defaults = dataclass_defaults(src, "Config")
    implementation = load_json(IMPLEMENTATION_GAP_JSON)
    checks = [
        check(
            "default_guard_mode_disabled",
            defaults.get("mushroom_v28_exit_guard_mode") == "disabled",
            defaults.get("mushroom_v28_exit_guard_mode"),
            "Config default must be disabled.",
        ),
        check(
            "default_reconciliation_disabled",
            defaults.get("mushroom_v28_exit_guard_reconciliation_enabled") is False,
            defaults.get("mushroom_v28_exit_guard_reconciliation_enabled"),
            "Exchange reconciliation must be opt-in to avoid surprise API calls.",
        ),
        check(
            "default_kill_switch_not_active",
            defaults.get("mushroom_v28_exit_guard_kill_switch") is False,
            defaults.get("mushroom_v28_exit_guard_kill_switch"),
            "Default kill switch should not alter disabled behavior.",
        ),
        check(
            "env_mode_default_disabled",
            'os.getenv("MUSHROOM_V28_EXIT_GUARD_MODE", "disabled")' in src,
            "MUSHROOM_V28_EXIT_GUARD_MODE default disabled",
            "load_config must default guard mode to disabled.",
        ),
        check(
            "mode_validation",
            'MUSHROOM_V28_EXIT_GUARD_MODE must be disabled, paper, or enforce' in src,
            "disabled|paper|enforce validation present",
            "Invalid guard modes must fail config validation.",
        ),
        check(
            "disabled_mode_short_circuits_shadow_emit",
            'if self.config.mushroom_v28_exit_guard_mode == "disabled":' in src
            and "return\n        payload = {" in src,
            "emit_mushroom_v28_exit_guard_shadow returns in disabled mode",
            "Disabled mode must not write the paper ledger.",
        ),
        check(
            "enforcement_requires_enforce_mode",
            'self.config.mushroom_v28_exit_guard_mode == "enforce"' in src
            and 'guard.get("suppress_exit")' in src,
            "enforce mode plus suppress_exit gate",
            "The guard must not suppress exits in disabled or paper mode.",
        ),
        check(
            "reconciliation_requires_opt_in_flag",
            "if self.config.mushroom_v28_exit_guard_reconciliation_enabled:" in src,
            "MUSHROOM_V28_EXIT_GUARD_RECONCILIATION_ENABLED gate",
            "Kalshi reconciliation API calls must be behind an explicit flag.",
        ),
        check(
            "implementation_gap_has_no_source_blockers",
            implementation.get("decision") == "implementation_ready_for_paper_shadow_review",
            {
                "decision": implementation.get("decision"),
                "blockers": implementation.get("blockers"),
            },
            "Implementation-gap probe must report source scaffolding ready for paper-shadow review.",
        ),
    ]
    failed = [row for row in checks if not row["passed"]]
    return {
        "generated_at_utc": utc_now_iso(),
        "purpose": "Verify dormant common-clock exit guard safety invariants.",
        "decision": "pass_paper_shadow_source_safety" if not failed else "fail_fix_guard_safety",
        "checks": checks,
        "summary": {
            "checks_total": len(checks),
            "checks_passed": sum(1 for row in checks if row["passed"]),
            "checks_failed": len(failed),
        },
        "sources": {
            "live_bot": str(LIVE_BOT),
            "implementation_gap": str(IMPLEMENTATION_GAP_JSON),
        },
    }


def fmt(value: Any) -> str:
    if isinstance(value, (dict, list)):
        return json.dumps(value, sort_keys=True, default=str).replace("|", "\\|")
    return str(value).replace("|", "\\|")


def write_outputs(report: dict[str, Any]) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8")
    summary = report.get("summary") or {}
    lines = [
        "# v28 Common-Clock Exit Guard Safety Verifier",
        "",
        "Research-only. No API calls, no live bot process control, no orders.",
        "",
        f"- Generated UTC: `{report.get('generated_at_utc')}`",
        f"- Decision: `{report.get('decision')}`",
        f"- Checks passed/failed: `{summary.get('checks_passed')}/{summary.get('checks_failed')}`",
        "",
        "| status | check | evidence | required |",
        "|---|---|---|---|",
    ]
    for row in report.get("checks") or []:
        lines.append(
            f"| `{row.get('status')}` | `{row.get('name')}` | {fmt(row.get('evidence'))} | {fmt(row.get('required'))} |"
        )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    report = build_report()
    write_outputs(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
