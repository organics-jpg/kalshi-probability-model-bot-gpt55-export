from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pandas as pd
import requests

from probe_truffle_historical_replay import build_ordered_market_records
from truffle_regime_lease import load_prompt_text, resolve_truffle_chat_completion_endpoint, resolve_truffle_model_id

ROOT = Path(__file__).resolve().parent
DEFAULT_OUTPUT_PATH = ROOT / "logs" / "truffle_day_supervisor_latest.json"
DEFAULT_PROMPT_PATH = ROOT / "truffle_day_supervisor_prompt.txt"

ALLOW_NEXT_DAY = "ALLOW_NEXT_DAY"
BLOCK_NEXT_DAY = "BLOCK_NEXT_DAY"


@dataclass(frozen=True)
class DayCase:
    profile_name: str
    next_day_date_local: str
    next_day_net_pnl_dollars: float
    payload: dict[str, Any]
    expected_decision: str
    previous_day_net_pnl_dollars: float
    recent_2_days_net_pnl_dollars: float
    recent_3_day_sign_pattern: str


def session_summary(frame: pd.DataFrame) -> dict[str, Any]:
    if frame.empty:
        return {
            "session_count": 0,
            "trade_count": 0,
            "net_pnl_dollars": 0.0,
            "avg_session_net_dollars": 0.0,
            "positive_session_fraction": 0.0,
        }
    nets = frame["net_pnl_dollars"].astype(float)
    trades = frame["trade_count"].astype(float)
    return {
        "session_count": int(len(frame)),
        "trade_count": int(trades.sum()),
        "net_pnl_dollars": round(float(nets.sum()), 4),
        "avg_session_net_dollars": round(float(nets.mean()), 4),
        "positive_session_fraction": round(float((nets > 0).mean()), 4),
    }


def market_summary(records: list[Any]) -> dict[str, Any]:
    traded = [row for row in records if row.traded]
    signal_count = sum(int(row.signal_count or 0) for row in records)
    return {
        "market_count": int(len(traded)),
        "net_pnl_dollars": round(sum(float(row.pnl_dollars or 0.0) for row in traded), 4),
        "positive_trade_fraction": round(
            sum(1 for row in traded if float(row.pnl_dollars or 0.0) > 0) / max(1, len(traded)),
            4,
        ),
        "exit_count": int(sum(1 for row in traded if str(row.outcome_type or "").strip().lower() == "exit")),
        "stale_per_signal": round(
            sum(int(row.stale_book_deferral_count or 0) for row in records) / max(1, signal_count),
            4,
        ),
    }


def sign_pattern(values: list[float]) -> str:
    tokens: list[str] = []
    for value in values:
        if value > 0:
            tokens.append("+")
        elif value < 0:
            tokens.append("-")
        else:
            tokens.append("0")
    return "".join(tokens)


def build_day_cases(dataset_tag: str) -> list[DayCase]:
    records = build_ordered_market_records(dataset_tag)
    rows: list[dict[str, Any]] = []
    for row in records:
        if not row.traded or not row.market_close_time:
            continue
        close_dt = pd.Timestamp(row.market_close_time).tz_convert("America/New_York")
        rows.append(
            {
                "profile_name": dataset_tag,
                "record": row,
                "date": close_dt.strftime("%Y-%m-%d"),
                "session": row.session or "unknown",
                "market_close_time": close_dt,
                "pnl_dollars": float(row.pnl_dollars or 0.0),
            }
        )
    trade_df = pd.DataFrame(rows).sort_values("market_close_time").reset_index(drop=True)
    if trade_df.empty:
        return []

    day_groups: list[dict[str, Any]] = []
    for date, frame in trade_df.groupby("date", sort=False):
        session_rows: list[dict[str, Any]] = []
        for session, session_frame in frame.groupby("session", sort=False):
            session_rows.append(
                {
                    "session_label": str(session),
                    "trade_count": int(len(session_frame)),
                    "net_pnl_dollars": round(float(session_frame["pnl_dollars"].sum()), 4),
                    "positive_trade_fraction": round(float((session_frame["pnl_dollars"] > 0).mean()), 4),
                }
            )
        day_groups.append(
            {
                "date": str(date),
                "trade_count": int(len(frame)),
                "session_count": int(frame["session"].nunique()),
                "net_pnl_dollars": round(float(frame["pnl_dollars"].sum()), 4),
                "positive_trade_fraction": round(float((frame["pnl_dollars"] > 0).mean()), 4),
                "records": frame["record"].tolist(),
                "sessions": session_rows,
            }
        )

    cases: list[DayCase] = []
    prior_cases: list[DayCase] = []
    for index, current_day in enumerate(day_groups):
        if index < 3:
            continue
        previous_day = day_groups[index - 1]
        recent_2_days = day_groups[max(0, index - 2) : index]
        recent_3_days = day_groups[max(0, index - 3) : index]
        recent_market_records: list[Any] = []
        for row in day_groups[:index]:
            recent_market_records.extend(row["records"])

        day_sequence = [
            {
                "day_label": str(row["date"]),
                "net_pnl_dollars": round(float(row["net_pnl_dollars"]), 4),
                "trade_count": int(row["trade_count"]),
                "positive_trade_fraction": round(float(row["positive_trade_fraction"]), 4),
                "session_count": int(row["session_count"]),
            }
            for row in recent_3_days
        ]
        payload = {
            "schema_version": "day_lease_input_v1",
            "profile_name": dataset_tag,
            "lease_scope": "next_day_only",
            "next_day_date_local": current_day["date"],
            "previous_day_summary": {
                "day_label": str(previous_day["date"]),
                "trade_count": int(previous_day["trade_count"]),
                "session_count": int(previous_day["session_count"]),
                "net_pnl_dollars": round(float(previous_day["net_pnl_dollars"]), 4),
                "positive_trade_fraction": round(float(previous_day["positive_trade_fraction"]), 4),
            },
            "recent_2_days": {
                "day_count": int(len(recent_2_days)),
                "trade_count": int(sum(int(row["trade_count"]) for row in recent_2_days)),
                "net_pnl_dollars": round(sum(float(row["net_pnl_dollars"]) for row in recent_2_days), 4),
                "avg_day_net_dollars": round(
                    sum(float(row["net_pnl_dollars"]) for row in recent_2_days) / max(1, len(recent_2_days)),
                    4,
                ),
                "positive_day_fraction": round(
                    sum(1 for row in recent_2_days if float(row["net_pnl_dollars"]) > 0) / max(1, len(recent_2_days)),
                    4,
                ),
            },
            "recent_3_days_sequence": day_sequence,
            "previous_day_sessions_sequence": previous_day["sessions"],
            "recent_8_candidate_markets": market_summary(recent_market_records[-8:]),
            "recent_16_candidate_markets": market_summary(recent_market_records[-16:]),
            "retrieved_analogues": retrieve_analogues(
                target_previous_day_net=float(previous_day["net_pnl_dollars"]),
                target_recent_2_day_net=sum(float(row["net_pnl_dollars"]) for row in recent_2_days),
                target_recent_sign_pattern=sign_pattern([float(row["net_pnl_dollars"]) for row in recent_3_days]),
                prior_cases=prior_cases,
                max_examples=2,
            ),
        }
        case = DayCase(
            profile_name=dataset_tag,
            next_day_date_local=str(current_day["date"]),
            next_day_net_pnl_dollars=float(current_day["net_pnl_dollars"]),
            payload=payload,
            expected_decision=ALLOW_NEXT_DAY if float(current_day["net_pnl_dollars"]) > 0 else BLOCK_NEXT_DAY,
            previous_day_net_pnl_dollars=float(previous_day["net_pnl_dollars"]),
            recent_2_days_net_pnl_dollars=sum(float(row["net_pnl_dollars"]) for row in recent_2_days),
            recent_3_day_sign_pattern=sign_pattern([float(row["net_pnl_dollars"]) for row in recent_3_days]),
        )
        cases.append(case)
        prior_cases.append(case)
    return cases


def retrieve_analogues(
    *,
    target_previous_day_net: float,
    target_recent_2_day_net: float,
    target_recent_sign_pattern: str,
    prior_cases: list[DayCase],
    max_examples: int,
) -> list[dict[str, Any]]:
    if max_examples <= 0 or not prior_cases:
        return []

    def distance(case: DayCase) -> tuple[float, float]:
        pattern_penalty = 0.0 if case.recent_3_day_sign_pattern == target_recent_sign_pattern else 1.0
        score = (
            abs(case.previous_day_net_pnl_dollars - target_previous_day_net)
            + 0.5 * abs(case.recent_2_days_net_pnl_dollars - target_recent_2_day_net)
            + 5.0 * pattern_penalty
        )
        return (score, abs(case.next_day_net_pnl_dollars))

    positives = [case for case in prior_cases if case.expected_decision == ALLOW_NEXT_DAY]
    negatives = [case for case in prior_cases if case.expected_decision == BLOCK_NEXT_DAY]
    selected: list[DayCase] = []
    if positives:
        selected.append(min(positives, key=distance))
    if negatives:
        selected.append(min(negatives, key=distance))
    if len(selected) < max_examples:
        for case in sorted(prior_cases, key=distance):
            if case not in selected:
                selected.append(case)
            if len(selected) >= max_examples:
                break
    return [
        {
            "analogue_next_day_date_local": case.next_day_date_local,
            "decision": case.expected_decision,
            "actual_next_day_net_pnl_dollars": round(case.next_day_net_pnl_dollars, 4),
            "previous_day_net_pnl_dollars": round(case.previous_day_net_pnl_dollars, 4),
            "recent_2_days_net_pnl_dollars": round(case.recent_2_days_net_pnl_dollars, 4),
            "recent_3_day_sign_pattern": case.recent_3_day_sign_pattern,
        }
        for case in selected[:max_examples]
    ]


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


def issue_day_decision(
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


def summarize_results(*, cases: list[DayCase], rows: list[dict[str, Any]]) -> dict[str, Any]:
    baseline_net = round(sum(case.next_day_net_pnl_dollars for case in cases), 4)
    allowed = [row for row in rows if row.get("decision") == ALLOW_NEXT_DAY]
    return {
        "case_count": int(len(cases)),
        "valid_count": int(sum(1 for row in rows if row.get("is_valid"))),
        "accuracy": round(sum(1 for row in rows if row.get("is_correct")) / max(1, len(cases)), 4),
        "allowed_count": int(len(allowed)),
        "allowed_net_pnl_dollars": round(sum(float(row.get("next_day_net_pnl_dollars") or 0.0) for row in allowed), 4),
        "baseline_net_pnl_dollars": baseline_net,
        "net_delta_dollars": round(
            sum(float(row.get("next_day_net_pnl_dollars") or 0.0) for row in allowed) - baseline_net,
            4,
        ),
    }


def deterministic_day_baselines(cases: list[DayCase]) -> list[dict[str, Any]]:
    if not cases:
        return []
    frame = pd.DataFrame(
        [
            {
                "profile_name": case.profile_name,
                "next_day_net_pnl_dollars": case.next_day_net_pnl_dollars,
                "prev_day_net_pnl_dollars": case.previous_day_net_pnl_dollars,
            }
            for case in cases
        ]
    )
    rules = {
        "always_allow": pd.Series(True, index=frame.index),
        "block_if_prev_day_net_ge_5": ~(frame["prev_day_net_pnl_dollars"] >= 5.0),
        "block_if_prev_day_net_ge_2": ~(frame["prev_day_net_pnl_dollars"] >= 2.0),
        "profile_specific_hot_day": ~(
            ((frame["profile_name"] == "live_90_70") & (frame["prev_day_net_pnl_dollars"] >= 5.0))
            | ((frame["profile_name"] == "live_90_78") & (frame["prev_day_net_pnl_dollars"] >= 12.0))
        ),
    }
    baseline_net = round(float(frame["next_day_net_pnl_dollars"].sum()), 4)
    rows: list[dict[str, Any]] = []
    for name, keep_mask in rules.items():
        kept = frame.loc[keep_mask].copy()
        net = round(float(kept["next_day_net_pnl_dollars"].sum()), 4)
        rows.append(
            {
                "name": name,
                "kept_days": int(len(kept)),
                "allowed_net_pnl_dollars": net,
                "baseline_net_pnl_dollars": baseline_net,
                "net_delta_dollars": round(net - baseline_net, 4),
            }
        )
    return rows


def main() -> None:
    parser = argparse.ArgumentParser(description="Probe Truffle as a profile-aware next-day supervisor.")
    parser.add_argument("--datasets", nargs="+", default=["live_90_70", "live_90_78"])
    parser.add_argument("--endpoint", default="http://192.168.1.234/if2/v1/chat/completions")
    parser.add_argument("--model", default="Qwen3.5-2B")
    parser.add_argument("--prompt-path", default=str(DEFAULT_PROMPT_PATH))
    parser.add_argument("--timeout-ms", type=int, default=15000)
    parser.add_argument("--output-path", default=str(DEFAULT_OUTPUT_PATH))
    args = parser.parse_args()

    prompt_text = load_prompt_text(Path(args.prompt_path))
    all_cases: list[DayCase] = []
    for dataset_tag in args.datasets:
        all_cases.extend(build_day_cases(dataset_tag))

    rows: list[dict[str, Any]] = []
    for case in all_cases:
        response = issue_day_decision(
            case.payload,
            endpoint=args.endpoint,
            model=args.model,
            timeout_ms=args.timeout_ms,
            prompt_text=prompt_text,
        )
        parsed = response.get("parsed") if isinstance(response, dict) else None
        decision = str(parsed.get("decision") or "").strip() if isinstance(parsed, dict) else ""
        is_valid = decision in {ALLOW_NEXT_DAY, BLOCK_NEXT_DAY}
        rows.append(
            {
                "profile_name": case.profile_name,
                "next_day_date_local": case.next_day_date_local,
                "next_day_net_pnl_dollars": round(case.next_day_net_pnl_dollars, 4),
                "expected_decision": case.expected_decision,
                "decision": decision,
                "is_valid": bool(is_valid),
                "is_correct": bool(is_valid and decision == case.expected_decision),
                "confidence": parsed.get("confidence") if isinstance(parsed, dict) else None,
                "rationale_code": parsed.get("rationale_code") if isinstance(parsed, dict) else "",
                "summary_reason": parsed.get("summary_reason") if isinstance(parsed, dict) else "",
                "payload": case.payload,
            }
        )

    by_profile: list[dict[str, Any]] = []
    rows_df = pd.DataFrame(rows)
    for profile_name, _ in rows_df.groupby("profile_name", dropna=False):
        cases = [case for case in all_cases if case.profile_name == str(profile_name)]
        profile_rows = [row for row in rows if row["profile_name"] == profile_name]
        by_profile.append(
            {
                "profile_name": profile_name,
                **summarize_results(cases=cases, rows=profile_rows),
            }
        )

    payload = {
        "generated_at": pd.Timestamp.utcnow().isoformat(),
        "endpoint": args.endpoint,
        "model": args.model,
        "prompt_path": str(Path(args.prompt_path).resolve()),
        "summary": summarize_results(cases=all_cases, rows=rows),
        "by_profile": by_profile,
        "deterministic_baselines": deterministic_day_baselines(all_cases),
        "rows": rows,
    }

    output_path = Path(args.output_path)
    if not output_path.is_absolute():
        output_path = ROOT / output_path
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")

    print(f"Saved Truffle day supervisor probe to {output_path}")
    print(payload["summary"])
    for row in payload["by_profile"]:
        print(row)
    for row in payload["deterministic_baselines"]:
        print(row)


if __name__ == "__main__":
    main()
