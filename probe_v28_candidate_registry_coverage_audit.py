"""Audit whether the consolidated v28 candidate table covers active lanes.

Research-only; no live bot changes or orders.

This deliberately separates active promotion-tracked candidates from older
diagnostic/frontier artifacts. The all-candidates table should cover the
active frozen registry plus the manually tracked special families; it should
not pretend every historical diagnostic scan row is an active candidate.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
TRACKER_JSON = OUT_DIR / "v28_candidate_pnl_tracker_latest.json"
LEADERBOARD_JSON = OUT_DIR / "v28_frozen_candidate_leaderboard_latest.json"
OUT_JSON = OUT_DIR / "v28_candidate_registry_coverage_audit_latest.json"
OUT_MD = OUT_DIR / "v28_candidate_registry_coverage_audit_latest.md"

SPECIAL_SOURCES = {
    "rmt_forgetting_entry_bakeoff": OUT_DIR / "v28_rmt_forgetting_entry_bakeoff_latest.json",
    "path_rmt_forward_gate": OUT_DIR / "v28_path_rmt_forward_gate_latest.json",
    "boundary_memory_fv": OUT_DIR / "v28_boundary_memory_fv_candidates_latest.json",
    "phi_forgetting_fv": OUT_DIR / "v28_phi_forgetting_fv_candidates_latest.json",
    "reward_memory_fv": OUT_DIR / "v28_reward_memory_fv_candidates_latest.json",
    "false_conviction_family_scorecard": OUT_DIR / "v28_false_conviction_family_scorecard_latest.json",
    "collapse_reentry_registry": OUT_DIR / "v28_live_collapse_reentry_registry_latest.json",
    "soft_frontier_size_shrink_portfolio": OUT_DIR / "v28_soft_frontier_size_shrink_portfolio_latest.json",
    "soft_frontier_midprice_boundary_shrink": OUT_DIR / "v28_soft_frontier_midprice_boundary_shrink_latest.json",
    "soft_frontier_midprice_boundary_exit_stack": OUT_DIR / "v28_soft_frontier_midprice_boundary_exit_stack_latest.json",
    "exit_reduce_drift_guard": OUT_DIR / "v28_frozen_exit_reduce_drift_guard_watch_latest.json",
    "exit_shallow_drawdown": OUT_DIR / "v28_frozen_exit_shallow_drawdown_watch_latest.json",
    "exit_shallow_duration_lte52": OUT_DIR / "v28_frozen_exit_shallow_duration_watch_latest.json",
    "exit_clip_separator_watch": OUT_DIR / "v28_frozen_exit_clip_separator_watch_latest.json",
    "matched_unchanged_loss_guard_watch": OUT_DIR / "v28_frozen_matched_unchanged_loss_guard_watch_latest.json",
    "feature_gate_exit_bid_suppression_watch": OUT_DIR / "v28_feature_gate_exit_bid_suppression_watch_latest.json",
    "frozen_value_exit_feature_side_guard": OUT_DIR / "v28_frozen_value_exit_feature_side_guard_latest.json",
    "exit_common_clock_residual_child_watch": OUT_DIR / "v28_frozen_exit_common_clock_residual_child_watch_latest.json",
    "soft_frontier_midprice_delayed_recheck_exit": OUT_DIR / "v28_frozen_soft_frontier_midprice_delayed_recheck_exit_latest.json",
    "soft_frontier_midprice_delayed_recheck_rescue": OUT_DIR / "v28_frozen_soft_frontier_midprice_delayed_recheck_rescue_latest.json",
}

IGNORE_DIAGNOSTIC_FILES = {
    TRACKER_JSON.name,
    LEADERBOARD_JSON.name,
    "v28_all_candidates_sorted_by_pnl_latest.json",
    "v28_candidate_vs_live_full_table_latest.json",
    "v28_candidate_readiness_distance_latest.json",
    "v28_goal_completion_audit_latest.json",
    "v28_current_direction_decision_latest.json",
    "v28_candidate_watchlist_latest.json",
    OUT_JSON.name,
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


def active_expected_rows() -> list[dict[str, Any]]:
    expected: list[dict[str, Any]] = []

    leaderboard = load_json(LEADERBOARD_JSON)
    for row in leaderboard.get("ranked") or []:
        if not isinstance(row, dict):
            continue
        gate = str(row.get("gate") or "")
        policy = str(row.get("policy") or "")
        if gate and policy:
            expected.append({
                "source": LEADERBOARD_JSON.name,
                "gate": gate,
                "policy": policy,
            })

    for gate, path in SPECIAL_SOURCES.items():
        payload = load_json(path)
        if not payload:
            continue
        if gate == "rmt_forgetting_entry_bakeoff":
            for row in payload.get("ranked_by_pnl") or []:
                policy = str((row or {}).get("policy") or "")
                if policy and ("rmt_" in policy or "book_ask_prior" in policy):
                    expected.append({"source": path.name, "gate": gate, "policy": policy})
        elif gate == "path_rmt_forward_gate":
            for row in payload.get("summaries") or []:
                policy = str((row or {}).get("policy") or "")
                if policy and "rmt" in policy:
                    expected.append({"source": path.name, "gate": gate, "policy": policy})
        elif gate in {"boundary_memory_fv", "phi_forgetting_fv", "reward_memory_fv"}:
            for row in payload.get("forward") or []:
                policy = str((row or {}).get("overlay") or "")
                if policy and policy != "raw_probability":
                    expected.append({"source": path.name, "gate": gate, "policy": policy})
        elif gate == "false_conviction_family_scorecard":
            for row in payload.get("rows") or []:
                policy = str((row or {}).get("candidate") or (row or {}).get("name") or "")
                if policy:
                    expected.append({"source": path.name, "gate": gate, "policy": policy})
        elif gate == "collapse_reentry_registry":
            summary = payload.get("future_summary")
            if isinstance(summary, dict):
                expected.append({
                    "source": path.name,
                    "gate": gate,
                    "policy": "all_post_collapse_reentries_actual",
                })
                expected.append({
                    "source": path.name,
                    "gate": gate,
                    "policy": "skip_all_post_collapse_reentries",
                })
            for row in payload.get("future_tag_rollups") or []:
                tag = str((row or {}).get("tag") or "")
                if tag:
                    expected.append({
                        "source": path.name,
                        "gate": gate,
                        "policy": f"skip_reentry_tag_{tag}",
                    })
        elif gate in {"soft_frontier_size_shrink_portfolio", "soft_frontier_midprice_boundary_shrink"}:
            for lane in payload.get("lanes") or []:
                if not isinstance(lane, dict):
                    continue
                lane_name = str(lane.get("lane") or "")
                for variant in lane.get("variants") or []:
                    if not isinstance(variant, dict):
                        continue
                    policy = str(variant.get("candidate") or f"{lane_name}_{variant.get('weight_policy')}")
                    if policy:
                        expected.append({"source": path.name, "gate": gate, "policy": policy})
        elif gate == "soft_frontier_midprice_boundary_exit_stack":
            for variant in payload.get("variants") or []:
                if not isinstance(variant, dict):
                    continue
                policy = str(variant.get("candidate") or variant.get("policy") or "")
                if policy:
                    expected.append({"source": path.name, "gate": gate, "policy": policy})
        elif gate == "exit_reduce_drift_guard":
            for collection_key, prefix in [
                ("diagnostic_since_base_freeze", "diagnostic"),
                ("post_drift_guard_birth", "post_birth"),
            ]:
                for item in payload.get(collection_key) or []:
                    if not isinstance(item, dict):
                        continue
                    policy = str(item.get("policy") or "")
                    if policy:
                        label = policy if policy.startswith(f"{prefix}_") else f"{prefix}_{policy}"
                        expected.append({"source": path.name, "gate": gate, "policy": label})
        elif gate in {"exit_shallow_drawdown", "exit_shallow_duration_lte52"}:
            state = payload.get("state") if isinstance(payload.get("state"), dict) else {}
            for key, prefix in [("best_diagnostic", "diagnostic"), ("best_strict_forward", "post_birth")]:
                item = payload.get(key)
                if not isinstance(item, dict):
                    continue
                policy = str(item.get("policy") or state.get("candidate") or key)
                if policy:
                    label = policy if policy.startswith(f"{prefix}_") else f"{prefix}_{policy}"
                    expected.append({"source": path.name, "gate": gate, "policy": label})
        elif gate == "exit_clip_separator_watch":
            state = payload.get("state") if isinstance(payload.get("state"), dict) else {}
            summary = payload.get("candidate_summary")
            policy = str(state.get("candidate") or "")
            if policy and isinstance(summary, dict):
                expected.append({"source": path.name, "gate": gate, "policy": policy})
        elif gate == "matched_unchanged_loss_guard_watch":
            state = payload.get("state") if isinstance(payload.get("state"), dict) else {}
            summary = payload.get("post_freeze_summary")
            if state.get("freeze_ts_utc") and isinstance(summary, dict):
                expected.append({
                    "source": path.name,
                    "gate": gate,
                    "policy": "guarded_matched_unchanged_loss_hold_watch",
                })
        elif gate == "feature_gate_exit_bid_suppression_watch":
            state = payload.get("state")
            policy = str((state or {}).get("candidate") or "")
            lanes = payload.get("lanes") or []
            has_post_birth_lane = any(
                isinstance(lane, dict) and lane.get("lane") == "post_exit_bid_birth"
                for lane in lanes
            )
            if policy and has_post_birth_lane:
                expected.append({"source": path.name, "gate": gate, "policy": policy})
        elif gate == "frozen_value_exit_feature_side_guard":
            for lane in payload.get("lanes") or []:
                if not isinstance(lane, dict):
                    continue
                label = str(lane.get("label") or lane.get("lane") or "")
                if label:
                    expected.append({
                        "source": path.name,
                        "gate": gate,
                        "policy": f"{label}_value_only_gap15_or_p75_feature_gate_same_side",
                    })
        elif gate == "exit_common_clock_residual_child_watch":
            state = payload.get("state")
            policy = str((state or {}).get("candidate") or "")
            lanes = payload.get("lanes") or []
            has_post_birth_lane = any(
                isinstance(lane, dict) and lane.get("label") == "post_child_birth"
                for lane in lanes
            )
            if policy and has_post_birth_lane:
                expected.append({"source": path.name, "gate": gate, "policy": policy})
        elif gate in {"soft_frontier_midprice_delayed_recheck_exit", "soft_frontier_midprice_delayed_recheck_rescue"}:
            state = payload.get("state") if isinstance(payload.get("state"), dict) else {}
            entry_policy = str(state.get("entry_policy") or "")
            exit_source = str(state.get("exit_source") or "")
            recheck_policy = str(state.get("recheck_policy") or "")
            policy_base = "_".join(part for part in [entry_policy, exit_source, recheck_policy] if part)
            post_lane_name = (
                "post_clean_rescue_birth"
                if gate == "soft_frontier_midprice_delayed_recheck_rescue"
                else "post_delayed_recheck_birth"
            )
            lanes = payload.get("lanes") or []
            has_post_birth_lane = any(
                isinstance(lane, dict) and lane.get("lane") == post_lane_name
                for lane in lanes
            )
            if policy_base and has_post_birth_lane:
                expected.append({
                    "source": path.name,
                    "gate": gate,
                    "policy": f"{post_lane_name}_{policy_base}",
                })

    deduped: dict[tuple[str, str], dict[str, Any]] = {}
    for row in expected:
        deduped[(row["gate"], row["policy"])] = row
    return list(deduped.values())


def tracker_keys() -> set[tuple[str, str]]:
    payload = load_json(TRACKER_JSON)
    return {
        (str(row.get("gate") or ""), str(row.get("policy") or ""))
        for row in payload.get("rows") or []
        if isinstance(row, dict)
    }


def walk_candidate_like(obj: Any, path: tuple[str, ...] = ()) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    if isinstance(obj, dict):
        name = obj.get("policy") or obj.get("candidate") or obj.get("overlay") or obj.get("variant") or obj.get("name")
        has_metrics = any(
            key in obj
            for key in (
                "entries",
                "settled",
                "net_cents",
                "net_cents_after_entry_fee",
                "coverage_pct",
                "wins",
                "losses",
            )
        )
        if name and has_metrics:
            rows.append({
                "path": "/".join(path),
                "name": str(name),
                "entries": obj.get("entries"),
                "settled": obj.get("settled"),
                "net_cents": obj.get("net_cents", obj.get("net_cents_after_entry_fee")),
            })
        for key, value in obj.items():
            rows.extend(walk_candidate_like(value, path + (str(key),)))
    elif isinstance(obj, list):
        for idx, value in enumerate(obj):
            rows.extend(walk_candidate_like(value, path + (str(idx),)))
    return rows


def diagnostic_untracked_examples(active_keys: set[tuple[str, str]], limit: int = 30) -> tuple[int, list[dict[str, Any]]]:
    tracked_policies = {policy for _, policy in active_keys}
    count = 0
    examples: list[dict[str, Any]] = []
    for path in sorted(OUT_DIR.glob("v28*_latest.json")):
        if path.name in IGNORE_DIAGNOSTIC_FILES:
            continue
        payload = load_json(path)
        if not payload:
            continue
        for row in walk_candidate_like(payload):
            if row["name"] in tracked_policies or row["name"] == "raw_probability":
                continue
            count += 1
            if len(examples) < limit:
                examples.append({
                    "file": path.name,
                    **row,
                })
    return count, examples


def build_report() -> dict[str, Any]:
    expected = active_expected_rows()
    keys = tracker_keys()
    missing = [
        row for row in expected
        if (row["gate"], row["policy"]) not in keys
    ]
    extra_active = [
        {"gate": gate, "policy": policy}
        for gate, policy in sorted(keys)
        if gate and policy and all((gate, policy) != (row["gate"], row["policy"]) for row in expected)
    ]
    diagnostic_count, diagnostic_examples = diagnostic_untracked_examples(keys)
    return {
        "generated_at_utc": utc_now_iso(),
        "active_registry_complete": not missing,
        "tracker_rows": len(keys),
        "active_expected_rows": len(expected),
        "active_missing_rows": missing,
        "active_extra_tracker_rows": extra_active,
        "diagnostic_candidate_like_untracked_count": diagnostic_count,
        "diagnostic_candidate_like_untracked_examples": diagnostic_examples,
        "interpretation": [
            "active_registry_complete=true means the consolidated table covers the frozen leaderboard and special tracked families.",
            "diagnostic_candidate_like_untracked rows are old scans/frontiers/diagnostics; they are not automatically promotion-tracked candidates.",
        ],
        "sources": {
            "tracker": str(TRACKER_JSON),
            "frozen_leaderboard": str(LEADERBOARD_JSON),
            "special_sources": {gate: str(path) for gate, path in SPECIAL_SOURCES.items()},
        },
    }


def write_md(report: dict[str, Any]) -> None:
    lines = [
        "# v28 Candidate Registry Coverage Audit",
        "",
        "Research-only audit of the consolidated all-candidates table.",
        "",
        f"- Generated UTC: `{report['generated_at_utc']}`",
        f"- Active registry complete: `{report['active_registry_complete']}`",
        f"- Consolidated tracker rows: `{report['tracker_rows']}`",
        f"- Active expected rows checked: `{report['active_expected_rows']}`",
        f"- Active missing rows: `{len(report['active_missing_rows'])}`",
        f"- Diagnostic candidate-like rows outside tracker: `{report['diagnostic_candidate_like_untracked_count']}`",
        "",
        "## Active Missing Rows",
        "",
    ]
    if report["active_missing_rows"]:
        lines.extend([
            "| source | gate | policy |",
            "|---|---|---|",
        ])
        for row in report["active_missing_rows"]:
            lines.append(f"| `{row['source']}` | `{row['gate']}` | `{row['policy']}` |")
    else:
        lines.append("- None.")

    lines.extend([
        "",
        "## Diagnostic Untracked Examples",
        "",
        "These are candidate-like diagnostic rows in old scan/frontier artifacts. They are not automatically active promotion candidates.",
        "",
    ])
    if report["diagnostic_candidate_like_untracked_examples"]:
        lines.extend([
            "| file | path | name | entries | settled | net c |",
            "|---|---|---|---:|---:|---:|",
        ])
        for row in report["diagnostic_candidate_like_untracked_examples"]:
            lines.append(
                f"| `{row['file']}` | `{row['path']}` | `{row['name']}` | "
                f"{row.get('entries')} | {row.get('settled')} | {row.get('net_cents')} |"
            )
    else:
        lines.append("- None found.")

    lines.extend([
        "",
        "## Interpretation",
        "",
        "- The consolidated table is complete for active tracked candidates when `active_registry_complete` is true.",
        "- Old diagnostic scans can still contain candidate-like rows; they need explicit freezing/registration before becoming active table lanes.",
    ])
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    report = build_report()
    write_md(report)
    print(OUT_MD)


if __name__ == "__main__":
    main()
