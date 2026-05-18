from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import pandas as pd
import requests

from probe_truffle_ambiguity_router import (
    VALID_DECISIONS,
    build_profile_case_stream,
    get_case_metric,
    is_hard_green,
    is_hard_red,
    summarize_hybrid,
)
from probe_truffle_session_supervisor import ALLOW_NEXT_SESSION, BLOCK_NEXT_SESSION, SessionCase
from truffle_regime_lease import load_prompt_text, resolve_truffle_chat_completion_endpoint, resolve_truffle_model_id

ROOT = Path(__file__).resolve().parent
DEFAULT_OUTPUT_PATH = ROOT / "logs" / "truffle_prototype_router_latest.json"
DEFAULT_PROMPT_PATH = ROOT / "truffle_prototype_router_prompt.txt"


def extract_json_object(text: str) -> dict[str, Any] | None:
    body = str(text or "").strip()
    if not body:
        return None
    start = body.find("{")
    end = body.rfind("}")
    if start < 0 or end < start:
        return None
    try:
        value = json.loads(body[start : end + 1])
    except Exception:
        return None
    return value if isinstance(value, dict) else None


def issue_router_decision(
    payload: dict[str, Any],
    *,
    endpoint: str,
    model: str,
    timeout_ms: int,
    prompt_text: str,
) -> dict[str, Any]:
    resolved_endpoint = resolve_truffle_chat_completion_endpoint(endpoint)
    resolved_model = resolve_truffle_model_id(model, endpoint=resolved_endpoint, timeout_ms=timeout_ms) or model
    request_timeout = max(1.0, float(timeout_ms) / 1000.0)
    body = {
        "model": resolved_model,
        "temperature": 0,
        "max_tokens": 180,
        "messages": [
            {"role": "system", "content": prompt_text},
            {"role": "user", "content": json.dumps(payload, sort_keys=True)},
        ],
    }
    response = requests.post(
        resolved_endpoint,
        headers={"Content-Type": "application/json"},
        json=body,
        timeout=request_timeout,
    )
    response.raise_for_status()
    response_payload = response.json()
    content = ""
    if isinstance(response_payload, dict):
        choices = response_payload.get("choices")
        if isinstance(choices, list) and choices:
            message = choices[0].get("message") if isinstance(choices[0], dict) else None
            if isinstance(message, dict):
                content = str(message.get("content") or "")
    parsed = extract_json_object(content)
    return {
        "raw_response": response_payload,
        "content": content,
        "parsed": parsed,
    }


def case_vector(case: SessionCase) -> dict[str, float]:
    return {
        "previous_day_net_pnl_dollars": get_case_metric(case, "previous_day_summary", "net_pnl_dollars"),
        "same_session_trailing_net_pnl_dollars": get_case_metric(case, "same_session_trailing_summary", "net_pnl_dollars"),
        "previous_session_net_pnl_dollars": get_case_metric(case, "previous_session", "net_pnl_dollars"),
        "recent_2_sessions_net_pnl_dollars": get_case_metric(case, "recent_2_sessions", "net_pnl_dollars"),
        "recent_4_candidate_markets_net_pnl_dollars": get_case_metric(case, "recent_4_candidate_markets", "net_pnl_dollars"),
        "recent_8_candidate_markets_net_pnl_dollars": get_case_metric(case, "recent_8_candidate_markets", "net_pnl_dollars"),
    }


def build_prototype(cases: list[SessionCase]) -> dict[str, Any]:
    if not cases:
        return {
            "count": 0,
            "avg_next_session_net_pnl_dollars": 0.0,
            "previous_day_net_pnl_dollars": 0.0,
            "same_session_trailing_net_pnl_dollars": 0.0,
            "previous_session_net_pnl_dollars": 0.0,
            "recent_2_sessions_net_pnl_dollars": 0.0,
            "recent_4_candidate_markets_net_pnl_dollars": 0.0,
            "recent_8_candidate_markets_net_pnl_dollars": 0.0,
        }
    vectors = [case_vector(case) for case in cases]
    return {
        "count": int(len(cases)),
        "avg_next_session_net_pnl_dollars": round(sum(case.next_session_net_pnl_dollars for case in cases) / len(cases), 4),
        **{
            key: round(sum(vector[key] for vector in vectors) / len(vectors), 4)
            for key in vectors[0]
        },
    }


def build_router_payload(case: SessionCase, *, history: list[SessionCase]) -> dict[str, Any]:
    same_session = [item for item in history if item.session_label == case.session_label]
    positives = [item for item in history if item.expected_decision == ALLOW_NEXT_SESSION]
    negatives = [item for item in history if item.expected_decision == BLOCK_NEXT_SESSION]
    same_session_positives = [item for item in same_session if item.expected_decision == ALLOW_NEXT_SESSION]
    same_session_negatives = [item for item in same_session if item.expected_decision == BLOCK_NEXT_SESSION]
    return {
        "schema_version": "prototype_router_input_v1",
        "profile_name": case.profile_name,
        "lease_scope": "next_session_only",
        "router_state": "AMBIGUOUS_ONLY",
        "next_session_key": case.session_key,
        "next_session_date_local": case.session_date_local,
        "next_session_label": case.session_label,
        "current_case": {
            **case_vector(case),
            "next_session_label": case.session_label,
        },
        "same_session_positive_prototype": build_prototype(same_session_positives),
        "same_session_negative_prototype": build_prototype(same_session_negatives),
        "global_positive_prototype": build_prototype(positives),
        "global_negative_prototype": build_prototype(negatives),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Probe Truffle prototype routing on ambiguous sessions.")
    parser.add_argument("--profile", default="live_90_70")
    parser.add_argument("--endpoint", default="http://192.168.1.234/if2/v1/chat/completions")
    parser.add_argument("--model", default="Qwen3.5-2B")
    parser.add_argument("--prompt-path", default=str(DEFAULT_PROMPT_PATH))
    parser.add_argument("--timeout-ms", type=int, default=20000)
    parser.add_argument("--hot-day-threshold", type=float, default=5.0)
    parser.add_argument("--router-repeats", type=int, default=1)
    parser.add_argument("--router-vote", choices=["majority", "consensus"], default="majority")
    parser.add_argument("--output-path", default=str(DEFAULT_OUTPUT_PATH))
    args = parser.parse_args()

    prompt_text = load_prompt_text(Path(args.prompt_path))
    train_cases, held_out_cases, all_cases = build_profile_case_stream(str(args.profile))
    held_out_keys = {case.session_key for case in held_out_cases}
    prior_ambiguous_cases: list[SessionCase] = []
    rows: list[dict[str, Any]] = []

    for case in all_cases:
        route = "ambiguous"
        if is_hard_red(case, hot_day_threshold=float(args.hot_day_threshold)):
            route = "hard_red"
        elif is_hard_green(case, hot_day_threshold=float(args.hot_day_threshold)):
            route = "hard_green"

        if case not in train_cases and case.session_key in held_out_keys:
            row: dict[str, Any] = {
                "profile_name": case.profile_name,
                "session_key": case.session_key,
                "session_date_local": case.session_date_local,
                "session_label": case.session_label,
                "next_session_net_pnl_dollars": round(case.next_session_net_pnl_dollars, 4),
                "expected_decision": case.expected_decision,
                "route": route,
                "final_allow": False,
            }
            if route == "hard_red":
                row["final_decision"] = BLOCK_NEXT_SESSION
                row["final_allow"] = False
            elif route == "hard_green":
                row["final_decision"] = ALLOW_NEXT_SESSION
                row["final_allow"] = True
            else:
                payload = build_router_payload(case, history=prior_ambiguous_cases)
                run_outputs: list[dict[str, Any]] = []
                decisions: list[str] = []
                for _ in range(max(1, int(args.router_repeats))):
                    response = issue_router_decision(
                        payload,
                        endpoint=args.endpoint,
                        model=args.model,
                        timeout_ms=args.timeout_ms,
                        prompt_text=prompt_text,
                    )
                    parsed = response.get("parsed") if isinstance(response, dict) else None
                    decision = str(parsed.get("decision") or "").strip() if isinstance(parsed, dict) else ""
                    if decision in VALID_DECISIONS:
                        decisions.append(decision)
                    run_outputs.append(
                        {
                            "decision": decision,
                            "confidence": parsed.get("confidence") if isinstance(parsed, dict) else None,
                            "rationale_code": parsed.get("rationale_code") if isinstance(parsed, dict) else "",
                            "summary_reason": parsed.get("summary_reason") if isinstance(parsed, dict) else "",
                        }
                    )
                allow_votes = sum(decision == ALLOW_NEXT_SESSION for decision in decisions)
                block_votes = sum(decision == BLOCK_NEXT_SESSION for decision in decisions)
                if str(args.router_vote) == "consensus":
                    final_decision = (
                        ALLOW_NEXT_SESSION
                        if decisions
                        and len(decisions) == int(args.router_repeats)
                        and allow_votes == int(args.router_repeats)
                        else BLOCK_NEXT_SESSION
                    )
                else:
                    final_decision = ALLOW_NEXT_SESSION if allow_votes > block_votes else BLOCK_NEXT_SESSION
                row["router_payload"] = payload
                row["router_runs"] = run_outputs
                row["final_decision"] = final_decision
                row["final_allow"] = final_decision == ALLOW_NEXT_SESSION
            rows.append(row)

        if route == "ambiguous":
            prior_ambiguous_cases.append(case)

    allowed = [row for row in rows if bool(row.get("final_allow"))]
    ambiguous_allowed = [row for row in rows if row.get("route") == "ambiguous" and bool(row.get("final_allow"))]
    payload = {
        "generated_at": pd.Timestamp.utcnow().isoformat(),
        "profile_name": args.profile,
        "endpoint": args.endpoint,
        "model": args.model,
        "prompt_path": str(Path(args.prompt_path).resolve()),
        "hot_day_threshold": float(args.hot_day_threshold),
        "router_repeats": int(args.router_repeats),
        "router_vote": str(args.router_vote),
        "summary": summarize_hybrid(rows),
        "ambiguous_router_summary": {
            "ambiguous_case_count": int(sum(1 for row in rows if row.get("route") == "ambiguous")),
            "ambiguous_allowed_count": int(len(ambiguous_allowed)),
            "ambiguous_allowed_net_pnl_dollars": round(
                sum(float(row.get("next_session_net_pnl_dollars") or 0.0) for row in ambiguous_allowed), 4
            ),
            "ambiguous_total_net_pnl_dollars": round(
                sum(float(row.get("next_session_net_pnl_dollars") or 0.0) for row in rows if row.get("route") == "ambiguous"),
                4,
            ),
        },
        "rows": rows,
        "allowed_sessions": allowed,
    }

    output_path = Path(args.output_path)
    if not output_path.is_absolute():
        output_path = ROOT / output_path
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")

    print(f"Saved Truffle prototype router probe to {output_path}")
    print(payload["summary"])
    print(payload["ambiguous_router_summary"])


if __name__ == "__main__":
    main()
