from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import pandas as pd

from probe_truffle_ambiguity_router import build_router_payload, is_hard_green, is_hard_red
from probe_truffle_session_supervisor import SessionCase, build_session_cases

ROOT = Path(__file__).resolve().parent
DEFAULT_OUTPUT_PATH = ROOT / "logs" / "signal_match_rule_eval.json"


def allow_by_signal_rule(case: SessionCase, *, prior_ambiguous_cases: list[SessionCase]) -> tuple[bool, dict[str, Any]]:
    payload = build_router_payload(case, prior_ambiguous_cases=prior_ambiguous_cases, max_analogues=2)
    signal = payload["same_label_match_signal"]
    macro = payload["macro_event_context"]
    margin = float(signal.get("negative_distance") or 0.0) - float(signal.get("positive_distance") or 0.0)
    late_fail = bool(
        signal.get("preferred_label") == "positive"
        and macro.get("event_family") in {"jobs", "cpi"}
        and macro.get("session_relation") == "same_day_late_window"
        and float(signal.get("positive_distance") or 999.0) > 10.0
    )
    allow = bool(
        signal.get("preferred_label") == "positive"
        and not late_fail
        and (
            signal.get("preference_strength") == "strong"
            or (signal.get("preference_strength") == "moderate" and margin >= 1.0)
        )
    )
    return allow, {
        "same_label_match_signal": signal,
        "macro_event_context": macro,
        "distance_margin": round(margin, 4),
        "late_window_positive_guard_failed": late_fail,
    }


def evaluate_profile(profile_name: str) -> dict[str, Any]:
    train_cases, held_out_cases = build_session_cases(profile_name)
    all_cases = train_cases + held_out_cases
    held_out_keys = {case.session_key for case in held_out_cases}
    prior_ambiguous_cases: list[SessionCase] = []
    rows: list[dict[str, Any]] = []

    for case in all_cases:
        route = "ambiguous"
        if is_hard_red(case, hot_day_threshold=5.0):
            route = "hard_red"
        elif is_hard_green(case, hot_day_threshold=5.0):
            route = "hard_green"

        if case.session_key in held_out_keys and case not in train_cases:
            final_allow = False
            rule_detail: dict[str, Any] = {}
            final_decision = "BLOCK_NEXT_SESSION"
            if route == "hard_green":
                final_allow = True
                final_decision = "ALLOW_NEXT_SESSION"
            elif route == "ambiguous":
                final_allow, rule_detail = allow_by_signal_rule(case, prior_ambiguous_cases=prior_ambiguous_cases)
                final_decision = "ALLOW_NEXT_SESSION" if final_allow else "BLOCK_NEXT_SESSION"

            rows.append(
                {
                    "profile_name": profile_name,
                    "session_key": case.session_key,
                    "session_date_local": case.session_date_local,
                    "session_label": case.session_label,
                    "route": route,
                    "expected_decision": case.expected_decision,
                    "next_session_net_pnl_dollars": round(case.next_session_net_pnl_dollars, 4),
                    "final_decision": final_decision,
                    "final_allow": final_allow,
                    "rule_detail": rule_detail,
                }
            )

        if route == "ambiguous":
            prior_ambiguous_cases.append(case)

    allowed = [row for row in rows if row["final_allow"]]
    ambiguous_allowed = [row for row in rows if row["route"] == "ambiguous" and row["final_allow"]]
    baseline = round(sum(float(row["next_session_net_pnl_dollars"]) for row in rows), 4)
    return {
        "generated_at": pd.Timestamp.utcnow().isoformat(),
        "profile_name": profile_name,
        "summary": {
            "case_count": len(rows),
            "allowed_count": len(allowed),
            "allowed_net_pnl_dollars": round(sum(float(row["next_session_net_pnl_dollars"]) for row in allowed), 4),
            "baseline_net_pnl_dollars": baseline,
            "net_delta_dollars": round(
                sum(float(row["next_session_net_pnl_dollars"]) for row in allowed) - baseline,
                4,
            ),
        },
        "ambiguous_summary": {
            "ambiguous_case_count": sum(1 for row in rows if row["route"] == "ambiguous"),
            "ambiguous_allowed_count": len(ambiguous_allowed),
            "ambiguous_allowed_net_pnl_dollars": round(
                sum(float(row["next_session_net_pnl_dollars"]) for row in ambiguous_allowed),
                4,
            ),
            "ambiguous_total_net_pnl_dollars": round(
                sum(float(row["next_session_net_pnl_dollars"]) for row in rows if row["route"] == "ambiguous"),
                4,
            ),
        },
        "rows": rows,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Evaluate the deterministic signal-match ambiguity rule.")
    parser.add_argument("--profiles", nargs="+", default=["live_90_70", "live_90_78"])
    parser.add_argument("--output-path", default=str(DEFAULT_OUTPUT_PATH))
    args = parser.parse_args()

    results = [evaluate_profile(profile_name) for profile_name in args.profiles]
    payload = {"profiles": results}

    output_path = Path(args.output_path)
    if not output_path.is_absolute():
        output_path = ROOT / output_path
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")

    print(f"Saved deterministic signal-match rule probe to {output_path}")
    for result in results:
        print(result["profile_name"], result["summary"], result["ambiguous_summary"])


if __name__ == "__main__":
    main()
