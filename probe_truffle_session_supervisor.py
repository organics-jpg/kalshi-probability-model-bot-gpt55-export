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
DEFAULT_OUTPUT_PATH = ROOT / "logs" / "truffle_session_supervisor_latest.json"
DEFAULT_PROMPT_PATH = ROOT / "truffle_session_supervisor_prompt.txt"

ALLOW_NEXT_SESSION = "ALLOW_NEXT_SESSION"
BLOCK_NEXT_SESSION = "BLOCK_NEXT_SESSION"


@dataclass(frozen=True)
class SessionCase:
    profile_name: str
    session_key: str
    session_date_local: str
    session_label: str
    next_session_net_pnl_dollars: float
    payload: dict[str, Any]
    expected_decision: str


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


def build_session_cases(dataset_tag: str) -> tuple[list[SessionCase], list[SessionCase]]:
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
    session_groups: list[dict[str, Any]] = []
    for (date, session), frame in trade_df.groupby(["date", "session"], sort=False):
        session_groups.append(
            {
                "profile_name": dataset_tag,
                "session_key": f"{date}|{session}",
                "date": date,
                "session": session,
                "trade_count": int(len(frame)),
                "net_pnl_dollars": round(float(frame["pnl_dollars"].sum()), 4),
                "positive_trade_fraction": round(float((frame["pnl_dollars"] > 0).mean()), 4),
                "records": frame["record"].tolist(),
            }
        )

    unique_days = sorted({row["date"] for row in session_groups})
    held_out_days = set(unique_days[3:])
    train_cases: list[SessionCase] = []
    held_out_cases: list[SessionCase] = []
    prior_sessions = pd.DataFrame(columns=["date", "session", "trade_count", "net_pnl_dollars", "positive_trade_fraction"])
    prior_market_records: list[Any] = []

    for index, session_row in enumerate(session_groups):
        if index < 3:
            prior_sessions = pd.concat(
                [
                    prior_sessions,
                    pd.DataFrame(
                        [
                            {
                                "date": session_row["date"],
                                "session": session_row["session"],
                                "trade_count": session_row["trade_count"],
                                "net_pnl_dollars": session_row["net_pnl_dollars"],
                                "positive_trade_fraction": session_row["positive_trade_fraction"],
                            }
                        ]
                    ),
                ],
                ignore_index=True,
            )
            prior_market_records.extend(session_row["records"])
            continue

        recent_3_sessions = prior_sessions.tail(3).copy()
        recent_2_sessions = prior_sessions.tail(2).copy()
        previous_session = recent_3_sessions.tail(1).copy()
        prior_same_session = prior_sessions[prior_sessions["session"] == str(session_row["session"])].tail(3).copy()
        same_session_summary = session_summary(prior_same_session)
        prior_days = sorted(str(value) for value in prior_sessions["date"].dropna().unique())
        previous_day = prior_days[-1] if prior_days else ""
        previous_day_summary = session_summary(prior_sessions[prior_sessions["date"] == previous_day].copy()) if previous_day else session_summary(pd.DataFrame())
        payload = {
            "schema_version": "session_lease_input_v1",
            "profile_name": dataset_tag,
            "lease_scope": "next_session_only",
            "next_session_key": session_row["session_key"],
            "next_session_date_local": session_row["date"],
            "next_session_label": session_row["session"],
            "previous_session": session_summary(previous_session),
            "recent_2_sessions": session_summary(recent_2_sessions),
            "recent_3_sessions_sequence": [
                {
                    "session_label": str(item["session"]),
                    "trade_count": int(item["trade_count"]),
                    "net_pnl_dollars": round(float(item["net_pnl_dollars"]), 4),
                    "positive_trade_fraction": round(float(item["positive_trade_fraction"]), 4),
                }
                for item in recent_3_sessions.to_dict("records")
            ],
            "previous_day_label": previous_day,
            "previous_day_summary": previous_day_summary,
            "same_session_trailing_summary": same_session_summary,
            "recent_4_candidate_markets": market_summary(prior_market_records[-4:]),
            "recent_8_candidate_markets": market_summary(prior_market_records[-8:]),
        }
        case = SessionCase(
            profile_name=dataset_tag,
            session_key=session_row["session_key"],
            session_date_local=session_row["date"],
            session_label=session_row["session"],
            next_session_net_pnl_dollars=float(session_row["net_pnl_dollars"]),
            payload=payload,
            expected_decision=ALLOW_NEXT_SESSION if float(session_row["net_pnl_dollars"]) > 0 else BLOCK_NEXT_SESSION,
        )
        if session_row["date"] in held_out_days:
            held_out_cases.append(case)
        else:
            train_cases.append(case)

        prior_sessions = pd.concat(
            [
                prior_sessions,
                pd.DataFrame(
                    [
                        {
                            "date": session_row["date"],
                            "session": session_row["session"],
                            "trade_count": session_row["trade_count"],
                            "net_pnl_dollars": session_row["net_pnl_dollars"],
                            "positive_trade_fraction": session_row["positive_trade_fraction"],
                        }
                    ]
                ),
            ],
            ignore_index=True,
        )
        prior_market_records.extend(session_row["records"])
    return train_cases, held_out_cases


def build_few_shot_examples(cases: list[SessionCase], *, max_examples: int) -> str:
    if max_examples <= 0 or not cases:
        return ""
    blocks: list[str] = []
    positives = [case for case in cases if case.expected_decision == ALLOW_NEXT_SESSION]
    negatives = [case for case in cases if case.expected_decision == BLOCK_NEXT_SESSION]
    selected: list[SessionCase] = []
    if positives:
        selected.append(max(positives, key=lambda case: case.next_session_net_pnl_dollars))
    if negatives:
        selected.append(min(negatives, key=lambda case: case.next_session_net_pnl_dollars))
    for case in cases:
        if len(selected) >= max_examples:
            break
        if case not in selected:
            selected.append(case)
    for idx, case in enumerate(selected[:max_examples], start=1):
        blocks.append(
            f"Example {idx} input:\n{json.dumps(case.payload, sort_keys=True)}\n"
            f"Example {idx} output:\n"
            + json.dumps(
                {
                    "schema_version": "session_lease_decision_v1",
                    "decision": case.expected_decision,
                    "confidence": 0.75,
                    "rationale_code": "example_reference",
                    "summary_reason": "Example reference label.",
                },
                sort_keys=True,
            )
        )
    return "\n\n".join(blocks)


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


def issue_session_decision(
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
        "max_tokens": 160,
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


def summarize_results(
    *,
    cases: list[SessionCase],
    rows: list[dict[str, Any]],
) -> dict[str, Any]:
    baseline_net = round(sum(case.next_session_net_pnl_dollars for case in cases), 4)
    allowed = [row for row in rows if row.get("decision") == ALLOW_NEXT_SESSION]
    return {
        "case_count": int(len(cases)),
        "valid_count": int(sum(1 for row in rows if row.get("is_valid"))),
        "accuracy": round(sum(1 for row in rows if row.get("is_correct")) / max(1, len(cases)), 4),
        "allowed_count": int(len(allowed)),
        "allowed_net_pnl_dollars": round(sum(float(row.get("next_session_net_pnl_dollars") or 0.0) for row in allowed), 4),
        "baseline_net_pnl_dollars": baseline_net,
        "net_delta_dollars": round(
            sum(float(row.get("next_session_net_pnl_dollars") or 0.0) for row in allowed) - baseline_net,
            4,
        ),
    }


def deterministic_session_baselines(cases: list[SessionCase]) -> list[dict[str, Any]]:
    if not cases:
        return []
    frame = pd.DataFrame(
        [
            {
                "profile_name": case.profile_name,
                "next_session_net_pnl_dollars": case.next_session_net_pnl_dollars,
                "prev_session_net_pnl_dollars": float(case.payload["previous_session"]["net_pnl_dollars"]),
            }
            for case in cases
        ]
    )
    rules = {
        "always_allow": pd.Series(True, index=frame.index),
        "block_if_prev_session_net_ge_1": ~(frame["prev_session_net_pnl_dollars"] >= 1.0),
        "profile_specific_hot": ~(
            ((frame["profile_name"] == "live_90_70") & (frame["prev_session_net_pnl_dollars"] >= 1.0))
            | ((frame["profile_name"] == "live_90_78") & (frame["prev_session_net_pnl_dollars"] <= -1.0))
        ),
    }
    baseline_net = round(float(frame["next_session_net_pnl_dollars"].sum()), 4)
    rows: list[dict[str, Any]] = []
    for name, keep_mask in rules.items():
        kept = frame.loc[keep_mask].copy()
        net = round(float(kept["next_session_net_pnl_dollars"].sum()), 4)
        rows.append(
            {
                "name": name,
                "kept_sessions": int(len(kept)),
                "allowed_net_pnl_dollars": net,
                "baseline_net_pnl_dollars": baseline_net,
                "net_delta_dollars": round(net - baseline_net, 4),
            }
        )
    return rows


def main() -> None:
    parser = argparse.ArgumentParser(description="Probe Truffle as a profile-aware next-session supervisor.")
    parser.add_argument("--datasets", nargs="+", default=["live_90_78", "live_90_70"])
    parser.add_argument("--endpoint", default="http://192.168.1.234/if2/v1/chat/completions")
    parser.add_argument("--model", default="Qwen3.5-2B")
    parser.add_argument("--prompt-path", default=str(DEFAULT_PROMPT_PATH))
    parser.add_argument("--few-shot-examples", type=int, default=0)
    parser.add_argument("--timeout-ms", type=int, default=15000)
    parser.add_argument("--output-path", default=str(DEFAULT_OUTPUT_PATH))
    args = parser.parse_args()

    prompt_text = load_prompt_text(Path(args.prompt_path))
    all_train_cases: list[SessionCase] = []
    all_held_out_cases: list[SessionCase] = []
    for dataset_tag in args.datasets:
        train_cases, held_out_cases = build_session_cases(dataset_tag)
        all_train_cases.extend(train_cases)
        all_held_out_cases.extend(held_out_cases)

    few_shot_text = build_few_shot_examples(all_train_cases, max_examples=max(0, int(args.few_shot_examples)))
    effective_prompt = prompt_text if not few_shot_text else f"{prompt_text}\n\nFew-shot references:\n{few_shot_text}"

    rows: list[dict[str, Any]] = []
    for case in all_held_out_cases:
        response = issue_session_decision(
            case.payload,
            endpoint=args.endpoint,
            model=args.model,
            timeout_ms=args.timeout_ms,
            prompt_text=effective_prompt,
        )
        parsed = response.get("parsed") if isinstance(response, dict) else None
        decision = str(parsed.get("decision") or "").strip() if isinstance(parsed, dict) else ""
        is_valid = decision in {ALLOW_NEXT_SESSION, BLOCK_NEXT_SESSION}
        rows.append(
            {
                "profile_name": case.profile_name,
                "session_key": case.session_key,
                "session_date_local": case.session_date_local,
                "session_label": case.session_label,
                "next_session_net_pnl_dollars": round(case.next_session_net_pnl_dollars, 4),
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
    for profile_name, frame in pd.DataFrame(rows).groupby("profile_name", dropna=False):
        cases = [case for case in all_held_out_cases if case.profile_name == str(profile_name)]
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
        "few_shot_examples": int(args.few_shot_examples),
        "summary": summarize_results(cases=all_held_out_cases, rows=rows),
        "by_profile": by_profile,
        "deterministic_baselines": deterministic_session_baselines(all_held_out_cases),
        "rows": rows,
    }

    output_path = Path(args.output_path)
    if not output_path.is_absolute():
        output_path = ROOT / output_path
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")

    print(f"Saved Truffle session supervisor probe to {output_path}")
    print(payload["summary"])
    for row in payload["by_profile"]:
        print(row)
    for row in payload["deterministic_baselines"]:
        print(row)


if __name__ == "__main__":
    main()
