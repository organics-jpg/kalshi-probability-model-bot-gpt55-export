from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
OUT_JSON = ROOT / "logs" / "project_os" / "live_testing_status_latest.json"
OUT_MD = ROOT / "logs" / "project_os" / "live_testing_status_latest.md"
READINESS_JSON = ROOT / "logs" / "project_os" / "candidate_readiness_reevaluation_latest.json"

LIVE_NODE_ID = "candidate:v28_successor:v28s_boundary_monotonic_time_safe_v001_logged_events_diagnostic"
LIVE_CANDIDATE_ID = "v28s_boundary_monotonic_time_safe_v001"
LIVE_LABEL = "v28s_boundary_monotonic_time_safe_v001 / logged_events_diagnostic"


def iso_z() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def read_json(path: Path) -> Any:
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8", errors="ignore") or "{}")


def shadow_rows_from_readiness() -> list[dict[str, Any]]:
    payload = read_json(READINESS_JSON)
    if not isinstance(payload, dict):
        return []
    rows: list[dict[str, Any]] = []
    for row in payload.get("candidates") or []:
        if not isinstance(row, dict):
            continue
        if row.get("node_id") == LIVE_NODE_ID:
            continue
        if not row.get("live_shadow_ready"):
            continue
        rows.append(
            {
                "node_id": row.get("node_id"),
                "candidate_id": str(row.get("label") or "").split(" / ", 1)[0],
                "label": row.get("label"),
                "family": row.get("family") or "v28_successor",
                "mode": "live_shadow",
                "launch_status": "running",
                "pid": None,
                "strategy_tag": "v28_successor_market_coverage_shadow_loop",
                "bot_storage_tag": "v28_successor_shadow_candidates",
                "position_size": 0,
                "no_max_drawdown": True,
                "next_action": "Live-shadow collection is running; refresh the atlas after the next sidecar cycle for updated evidence.",
                "summary": "No-order v28 successor market coverage shadow collection.",
            }
        )
    return rows


def build_payload(args: argparse.Namespace) -> dict[str, Any]:
    generated = iso_z()
    live_row = {
        "node_id": LIVE_NODE_ID,
        "candidate_id": LIVE_CANDIDATE_ID,
        "label": LIVE_LABEL,
        "family": "v28_successor",
        "mode": "live_order",
        "launch_status": args.live_status,
        "pid": args.live_pid,
        "strategy_tag": "v28_successor_time_safe_live_size2",
        "bot_storage_tag": "live_v28_successor_time_safe_size2",
        "position_size": 2,
        "no_max_drawdown": True,
        "started_at_utc": generated,
        "implementation": {
            "candidate_id": LIVE_CANDIDATE_ID,
            "model_hash": "9b461a310d06c06b55af2e2d",
            "entry_mode": "tested_shadow_rule",
            "shadow_min_edge_cents": 1.0,
            "source_row_gate": "raw v28 mushroom_v28_approved gate",
            "successor_gate": "candidate_edge_cents >= 1.0, matching frozen shadow_enter",
            "position_size": 2,
            "exit_stop_loss_enabled": False,
            "mushroom_v28_live_exit_enabled": False,
            "exit_guard_mode": "disabled",
        },
        "next_action": "Monitor fills, settlement, and successor telemetry; keep live testing bounded to this explicit candidate.",
        "summary": "Controlled live test for the frozen time-safe v28 successor surface at position size 2.",
    }
    shadow_rows = shadow_rows_from_readiness()
    for row in shadow_rows:
        row["pid"] = args.shadow_pid
        row["launch_status"] = args.shadow_status
        row["started_at_utc"] = generated
    return {
        "schema": "project_os_live_testing_status_v1",
        "generated_at_utc": generated,
        "live_tests": [live_row],
        "shadow_tests": shadow_rows,
        "outputs": {
            "json": "logs/project_os/live_testing_status_latest.json",
            "markdown": "logs/project_os/live_testing_status_latest.md",
        },
    }


def write_markdown(payload: dict[str, Any]) -> None:
    lines = [
        "# Live Testing Status",
        "",
        f"- Generated UTC: `{payload['generated_at_utc']}`",
        "",
        "## Live Orders",
        "",
    ]
    for row in payload.get("live_tests") or []:
        lines.append(
            f"- `{row['label']}` status=`{row['launch_status']}` pid=`{row.get('pid')}` "
            f"strategy=`{row.get('strategy_tag')}` size=`{row.get('position_size')}` no_max_drawdown=`{row.get('no_max_drawdown')}`"
        )
    lines.extend(["", "## Live Shadow", ""])
    for row in payload.get("shadow_tests") or []:
        lines.append(
            f"- `{row['label']}` status=`{row['launch_status']}` pid=`{row.get('pid')}` strategy=`{row.get('strategy_tag')}`"
        )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--live-pid", type=int, default=0)
    parser.add_argument("--shadow-pid", type=int, default=0)
    parser.add_argument("--live-status", default="running")
    parser.add_argument("--shadow-status", default="running")
    args = parser.parse_args()

    payload = build_payload(args)
    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_markdown(payload)
    print(json.dumps({"written": str(OUT_JSON), "live_tests": len(payload["live_tests"]), "shadow_tests": len(payload["shadow_tests"])}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
