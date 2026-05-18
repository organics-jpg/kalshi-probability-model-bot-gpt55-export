from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pandas as pd
import requests

from probe_truffle_session_supervisor import (
    ALLOW_NEXT_SESSION,
    BLOCK_NEXT_SESSION,
    SessionCase,
    build_session_cases,
)
from truffle_regime_lease import load_prompt_text, resolve_truffle_chat_completion_endpoint, resolve_truffle_model_id

ROOT = Path(__file__).resolve().parent
DEFAULT_OUTPUT_PATH = ROOT / "logs" / "truffle_ambiguity_router_latest.json"
DEFAULT_PROMPT_PATH = ROOT / "truffle_ambiguity_router_prompt.txt"
VALID_DECISIONS = {ALLOW_NEXT_SESSION, BLOCK_NEXT_SESSION}
MACRO_EVENT_CALENDAR_2026: dict[str, dict[str, str]] = {
    "2026-03-06": {"event_family": "jobs", "event_name": "employment_situation", "release_time_et": "08:30"},
    "2026-03-11": {"event_family": "cpi", "event_name": "consumer_price_index", "release_time_et": "08:30"},
    "2026-03-18": {"event_family": "fomc", "event_name": "fomc_rate_decision", "release_time_et": "14:00"},
    "2026-04-03": {"event_family": "jobs", "event_name": "employment_situation", "release_time_et": "08:30"},
    "2026-04-10": {"event_family": "cpi", "event_name": "consumer_price_index", "release_time_et": "08:30"},
}


@dataclass(frozen=True)
class RoutedCase:
    route: str
    case: SessionCase


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
    max_tokens: int = 180,
    response_format: str = "none",
) -> dict[str, Any]:
    resolved_endpoint = resolve_truffle_chat_completion_endpoint(endpoint)
    resolved_model = resolve_truffle_model_id(model, endpoint=resolved_endpoint, timeout_ms=timeout_ms) or model
    request_timeout = max(1.0, float(timeout_ms) / 1000.0)
    body = {
        "model": resolved_model,
        "temperature": 0,
        "max_tokens": int(max_tokens),
        "messages": [
            {"role": "system", "content": prompt_text},
            {"role": "user", "content": json.dumps(payload, sort_keys=True)},
        ],
    }
    if str(response_format).strip().lower() == "json_object":
        body["response_format"] = {"type": "json_object"}
    response = requests.post(
        resolved_endpoint,
        headers={"Content-Type": "application/json"},
        json=body,
        timeout=request_timeout,
    )
    response.raise_for_status()
    response_payload = response.json()
    content = ""
    finish_reason = ""
    usage = {}
    if isinstance(response_payload, dict):
        choices = response_payload.get("choices")
        if isinstance(choices, list) and choices:
            choice = choices[0] if isinstance(choices[0], dict) else {}
            finish_reason = str(choice.get("finish_reason") or "")
            message = choice.get("message") if isinstance(choice, dict) else None
            if isinstance(message, dict):
                content = str(message.get("content") or "")
        usage = response_payload.get("usage") if isinstance(response_payload.get("usage"), dict) else {}
    parsed = extract_json_object(content)
    return {
        "raw_response": response_payload,
        "content": content,
        "parsed": parsed,
        "finish_reason": finish_reason,
        "usage": usage,
    }


def get_case_metric(case: SessionCase, *keys: str) -> float:
    current: Any = case.payload
    for key in keys:
        if not isinstance(current, dict):
            return 0.0
        current = current.get(key)
    try:
        return float(current)
    except Exception:
        return 0.0


def is_hard_red(case: SessionCase, *, hot_day_threshold: float) -> bool:
    return get_case_metric(case, "previous_day_summary", "net_pnl_dollars") >= hot_day_threshold


def is_hard_green(case: SessionCase, *, hot_day_threshold: float) -> bool:
    if is_hard_red(case, hot_day_threshold=hot_day_threshold):
        return False
    session_label = str(case.session_label or "")
    same_session_net = get_case_metric(case, "same_session_trailing_summary", "net_pnl_dollars")
    return session_label == "overnight" and same_session_net > 0.0


def case_distance(left: SessionCase, right: SessionCase) -> float:
    score = 0.0
    if str(left.session_label or "") != str(right.session_label or ""):
        score += 4.0
    score += abs(
        get_case_metric(left, "previous_day_summary", "net_pnl_dollars")
        - get_case_metric(right, "previous_day_summary", "net_pnl_dollars")
    )
    score += 0.75 * abs(
        get_case_metric(left, "same_session_trailing_summary", "net_pnl_dollars")
        - get_case_metric(right, "same_session_trailing_summary", "net_pnl_dollars")
    )
    score += 0.5 * abs(
        get_case_metric(left, "previous_session", "net_pnl_dollars")
        - get_case_metric(right, "previous_session", "net_pnl_dollars")
    )
    score += 0.35 * abs(
        get_case_metric(left, "recent_2_sessions", "net_pnl_dollars")
        - get_case_metric(right, "recent_2_sessions", "net_pnl_dollars")
    )
    score += 0.25 * abs(
        get_case_metric(left, "recent_4_candidate_markets", "net_pnl_dollars")
        - get_case_metric(right, "recent_4_candidate_markets", "net_pnl_dollars")
    )
    return score


def analogue_record(case: SessionCase) -> dict[str, Any]:
    return {
        "session_key": case.session_key,
        "next_session_label": case.session_label,
        "decision": case.expected_decision,
        "actual_next_session_net_pnl_dollars": round(case.next_session_net_pnl_dollars, 4),
        "previous_day_net_pnl_dollars": round(get_case_metric(case, "previous_day_summary", "net_pnl_dollars"), 4),
        "same_session_trailing_net_pnl_dollars": round(
            get_case_metric(case, "same_session_trailing_summary", "net_pnl_dollars"), 4
        ),
        "previous_session_net_pnl_dollars": round(get_case_metric(case, "previous_session", "net_pnl_dollars"), 4),
        "recent_2_sessions_net_pnl_dollars": round(get_case_metric(case, "recent_2_sessions", "net_pnl_dollars"), 4),
        "recent_4_candidate_markets_net_pnl_dollars": round(
            get_case_metric(case, "recent_4_candidate_markets", "net_pnl_dollars"), 4
        ),
    }


def select_closest_case(
    target: SessionCase,
    history: list[SessionCase],
    *,
    decision: str | None = None,
    same_label_only: bool = False,
) -> SessionCase | None:
    if not history:
        return None
    eligible = history
    if same_label_only:
        target_label = str(target.session_label or "")
        eligible = [case for case in eligible if str(case.session_label or "") == target_label]
    if decision:
        eligible = [case for case in eligible if case.expected_decision == decision]
    if not eligible:
        return None
    return min(eligible, key=lambda case: case_distance(target, case))


def retrieve_analogues(
    target: SessionCase,
    history: list[SessionCase],
    *,
    max_examples: int,
    same_label_only: bool = False,
) -> list[dict[str, Any]]:
    if max_examples <= 0 or not history:
        return []
    eligible_history = history
    if same_label_only:
        target_label = str(target.session_label or "")
        eligible_history = [case for case in history if str(case.session_label or "") == target_label]
        if not eligible_history:
            return []
    positives = [case for case in eligible_history if case.expected_decision == ALLOW_NEXT_SESSION]
    negatives = [case for case in eligible_history if case.expected_decision == BLOCK_NEXT_SESSION]
    selected: list[SessionCase] = []
    if positives:
        selected.append(min(positives, key=lambda case: case_distance(target, case)))
    if negatives:
        selected.append(min(negatives, key=lambda case: case_distance(target, case)))
    if len(selected) < max_examples:
        for case in sorted(eligible_history, key=lambda item: case_distance(target, item)):
            if case not in selected:
                selected.append(case)
            if len(selected) >= max_examples:
                break
    return [analogue_record(case) for case in selected[:max_examples]]


def sign_bucket(value: float) -> int:
    if value > 0:
        return 1
    if value < 0:
        return -1
    return 0


def analogue_match_distance(target: SessionCase, reference: SessionCase) -> float:
    return round(
        abs(get_case_metric(target, "previous_day_summary", "net_pnl_dollars") - get_case_metric(reference, "previous_day_summary", "net_pnl_dollars"))
        + abs(get_case_metric(target, "recent_2_sessions", "net_pnl_dollars") - get_case_metric(reference, "recent_2_sessions", "net_pnl_dollars"))
        + 0.35
        * abs(
            get_case_metric(target, "same_session_trailing_summary", "net_pnl_dollars")
            - get_case_metric(reference, "same_session_trailing_summary", "net_pnl_dollars")
        ),
        4,
    )


def analogue_sign_match_count(target: SessionCase, reference: SessionCase) -> int:
    keys = [
        ("previous_day_summary", "net_pnl_dollars"),
        ("recent_2_sessions", "net_pnl_dollars"),
        ("same_session_trailing_summary", "net_pnl_dollars"),
    ]
    return int(
        sum(
            sign_bucket(get_case_metric(target, *keyspec)) == sign_bucket(get_case_metric(reference, *keyspec))
            for keyspec in keys
        )
    )


def build_same_label_match_signal(case: SessionCase, history: list[SessionCase]) -> dict[str, Any]:
    same_label_history = [entry for entry in history if str(entry.session_label or "") == str(case.session_label or "")]
    positive_pool = [entry for entry in same_label_history if entry.expected_decision == ALLOW_NEXT_SESSION]
    negative_pool = [entry for entry in same_label_history if entry.expected_decision == BLOCK_NEXT_SESSION]
    positive_case = min(positive_pool, key=lambda entry: analogue_match_distance(case, entry)) if positive_pool else None
    negative_case = min(negative_pool, key=lambda entry: analogue_match_distance(case, entry)) if negative_pool else None
    if positive_case is None and negative_case is None:
        return {
            "available": False,
            "preferred_label": "none",
            "preference_strength": "none",
        }
    positive_distance = analogue_match_distance(case, positive_case) if positive_case is not None else None
    negative_distance = analogue_match_distance(case, negative_case) if negative_case is not None else None
    positive_sign_matches = analogue_sign_match_count(case, positive_case) if positive_case is not None else None
    negative_sign_matches = analogue_sign_match_count(case, negative_case) if negative_case is not None else None
    preferred_label = "none"
    strength = "weak"
    if positive_case is not None and negative_case is None:
        preferred_label = "positive"
        sign_matches = int(positive_sign_matches or 0)
        distance = float(positive_distance or 0.0)
        if sign_matches >= 3 and distance <= 5.0:
            strength = "strong"
        elif sign_matches >= 2 and distance <= 8.0:
            strength = "moderate"
    elif negative_case is not None and positive_case is None:
        preferred_label = "negative"
        sign_matches = int(negative_sign_matches or 0)
        distance = float(negative_distance or 0.0)
        if sign_matches >= 3 and distance <= 5.0:
            strength = "strong"
        elif sign_matches >= 2 and distance <= 8.0:
            strength = "moderate"
    elif positive_case is not None and negative_case is not None:
        distance_gap = float(negative_distance or 0.0) - float(positive_distance or 0.0)
        sign_gap = int(positive_sign_matches or 0) - int(negative_sign_matches or 0)
        if distance_gap > 1.0 or (distance_gap > 0.25 and sign_gap >= 0):
            preferred_label = "positive"
        elif distance_gap < -1.0 or (distance_gap < -0.25 and sign_gap <= 0):
            preferred_label = "negative"
        else:
            preferred_label = "mixed"
        if abs(distance_gap) >= 5.0 or abs(sign_gap) >= 2:
            strength = "strong"
        elif abs(distance_gap) >= 1.0 or abs(sign_gap) >= 1:
            strength = "moderate"
    return {
        "available": True,
        "preferred_label": preferred_label,
        "preference_strength": strength,
        "positive_analogue_session_key": positive_case.session_key if positive_case is not None else "",
        "positive_distance": positive_distance,
        "positive_sign_match_count": positive_sign_matches,
        "negative_analogue_session_key": negative_case.session_key if negative_case is not None else "",
        "negative_distance": negative_distance,
        "negative_sign_match_count": negative_sign_matches,
    }


def build_router_payload(case: SessionCase, *, prior_ambiguous_cases: list[SessionCase], max_analogues: int) -> dict[str, Any]:
    macro_context = build_macro_event_context(case)
    return {
        "schema_version": "ambiguity_router_input_v1",
        "profile_name": case.profile_name,
        "lease_scope": "next_session_only",
        "router_state": "AMBIGUOUS_ONLY",
        "next_session_key": case.session_key,
        "next_session_date_local": case.session_date_local,
        "next_session_label": case.session_label,
        "previous_session": case.payload["previous_session"],
        "recent_2_sessions": case.payload["recent_2_sessions"],
        "recent_3_sessions_sequence": case.payload["recent_3_sessions_sequence"],
        "previous_day_label": case.payload["previous_day_label"],
        "previous_day_summary": case.payload["previous_day_summary"],
        "same_session_trailing_summary": case.payload["same_session_trailing_summary"],
        "recent_4_candidate_markets": case.payload["recent_4_candidate_markets"],
        "recent_8_candidate_markets": case.payload["recent_8_candidate_markets"],
        "macro_event_context": macro_context,
        "same_label_match_signal": build_same_label_match_signal(case, prior_ambiguous_cases),
        "retrieved_analogues": retrieve_analogues(case, prior_ambiguous_cases, max_examples=max_analogues),
        "retrieved_same_label_analogues": retrieve_analogues(
            case,
            prior_ambiguous_cases,
            max_examples=max_analogues,
            same_label_only=True,
        ),
    }


def compact_router_payload(payload: dict[str, Any], *, payload_mode: str) -> dict[str, Any]:
    mode = str(payload_mode or "full").strip().lower()
    if mode == "match_signal_minimal":
        return {
            "next_session_key": payload.get("next_session_key"),
            "next_session_label": payload.get("next_session_label"),
            "macro_event_context": payload.get("macro_event_context"),
            "same_label_match_signal": payload.get("same_label_match_signal"),
        }
    if mode == "signal_guard_minimal":
        signal = payload.get("same_label_match_signal") if isinstance(payload.get("same_label_match_signal"), dict) else {}
        macro = payload.get("macro_event_context") if isinstance(payload.get("macro_event_context"), dict) else {}
        late_window_guard = "n_a"
        if (
            str(signal.get("preferred_label") or "") == "positive"
            and str(macro.get("event_family") or "") in {"jobs", "cpi"}
            and str(macro.get("session_relation") or "") == "same_day_late_window"
        ):
            late_window_guard = "pass" if float(signal.get("positive_distance") or 999.0) <= 10.0 else "fail"
        return {
            "next_session_key": payload.get("next_session_key"),
            "signal_direction": signal.get("preferred_label"),
            "signal_strength": signal.get("preference_strength"),
            "late_window_positive_guard": late_window_guard,
            "macro_tiebreak_allowed": bool(
                macro.get("event_day")
                and str(macro.get("session_relation") or "")
                in {"direct_reaction_window", "same_day_post_release_window", "post_release_window"}
            ),
            "macro_event_context": macro,
        }
    return payload


def build_macro_event_context(case: SessionCase) -> dict[str, Any]:
    event = MACRO_EVENT_CALENDAR_2026.get(str(case.session_date_local or ""))
    session_label = str(case.session_label or "")
    if not event:
        return {
            "event_day": False,
            "event_family": "none",
            "event_name": "",
            "release_time_et": "",
            "session_relation": "no_scheduled_macro_event",
        }
    event_family = str(event["event_family"])
    relation = "same_day_non_core_window"
    if event_family in {"jobs", "cpi"}:
        if session_label == "morning":
            relation = "direct_reaction_window"
        elif session_label == "afternoon":
            relation = "same_day_post_release_window"
        else:
            relation = "same_day_late_window"
    elif event_family == "fomc":
        if session_label == "afternoon":
            relation = "pre_release_window"
        elif session_label in {"evening", "late_evening"}:
            relation = "post_release_window"
        else:
            relation = "same_day_early_window"
    return {
        "event_day": True,
        "event_family": event_family,
        "event_name": str(event["event_name"]),
        "release_time_et": str(event["release_time_et"]),
        "session_relation": relation,
    }


def build_profile_case_stream(profile_name: str) -> tuple[list[SessionCase], list[SessionCase], list[SessionCase]]:
    train_cases, held_out_cases = build_session_cases(profile_name)
    return train_cases, held_out_cases, train_cases + held_out_cases


def summarize_hybrid(rows: list[dict[str, Any]]) -> dict[str, Any]:
    baseline = round(sum(float(row.get("next_session_net_pnl_dollars") or 0.0) for row in rows), 4)
    allowed = [row for row in rows if bool(row.get("final_allow"))]
    return {
        "case_count": int(len(rows)),
        "allowed_count": int(len(allowed)),
        "allowed_net_pnl_dollars": round(sum(float(row.get("next_session_net_pnl_dollars") or 0.0) for row in allowed), 4),
        "baseline_net_pnl_dollars": baseline,
        "net_delta_dollars": round(
            sum(float(row.get("next_session_net_pnl_dollars") or 0.0) for row in allowed) - baseline,
            4,
        ),
        "route_counts": {
            "hard_red": int(sum(1 for row in rows if row.get("route") == "hard_red")),
            "hard_green": int(sum(1 for row in rows if row.get("route") == "hard_green")),
            "ambiguous": int(sum(1 for row in rows if row.get("route") == "ambiguous")),
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Probe Truffle as an ambiguity router on top of deterministic session routing.")
    parser.add_argument("--profile", default="live_90_70")
    parser.add_argument("--endpoint", default="http://192.168.1.234/if2/v1/chat/completions")
    parser.add_argument("--model", default="Qwen3.5-2B")
    parser.add_argument("--prompt-path", default=str(DEFAULT_PROMPT_PATH))
    parser.add_argument("--timeout-ms", type=int, default=20000)
    parser.add_argument("--max-tokens", type=int, default=180)
    parser.add_argument("--response-format", choices=["none", "json_object"], default="none")
    parser.add_argument(
        "--payload-mode",
        choices=["full", "match_signal_minimal", "signal_guard_minimal"],
        default="full",
    )
    parser.add_argument("--hot-day-threshold", type=float, default=5.0)
    parser.add_argument("--max-analogues", type=int, default=2)
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
        elif case in train_cases:
            route = "ambiguous"

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
                payload = build_router_payload(
                    case,
                    prior_ambiguous_cases=prior_ambiguous_cases,
                    max_analogues=max(0, int(args.max_analogues)),
                )
                model_payload = compact_router_payload(payload, payload_mode=str(args.payload_mode))
                run_outputs: list[dict[str, Any]] = []
                decisions: list[str] = []
                for _ in range(max(1, int(args.router_repeats))):
                    response = issue_router_decision(
                        model_payload,
                        endpoint=args.endpoint,
                        model=args.model,
                        timeout_ms=args.timeout_ms,
                        prompt_text=prompt_text,
                        max_tokens=int(args.max_tokens),
                        response_format=str(args.response_format),
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
                            "parsed_ok": bool(isinstance(parsed, dict)),
                            "finish_reason": str(response.get("finish_reason") or ""),
                            "content_preview": str(response.get("content") or "")[:240],
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
                row["router_payload"] = model_payload
                row["router_payload_full"] = payload
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
        "max_tokens": int(args.max_tokens),
        "response_format": str(args.response_format),
        "payload_mode": str(args.payload_mode),
        "hot_day_threshold": float(args.hot_day_threshold),
        "max_analogues": int(args.max_analogues),
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

    print(f"Saved Truffle ambiguity router probe to {output_path}")
    print(payload["summary"])
    print(payload["ambiguous_router_summary"])


if __name__ == "__main__":
    main()
