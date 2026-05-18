from __future__ import annotations

import argparse
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent
DEFAULT_OUTPUT_PATH = ROOT / "logs" / "truffle_committee_eval_latest.json"

ALLOW_NEXT_SESSION = "ALLOW_NEXT_SESSION"
BLOCK_NEXT_SESSION = "BLOCK_NEXT_SESSION"
VALID_DECISIONS = {ALLOW_NEXT_SESSION, BLOCK_NEXT_SESSION}


def load_rows(paths: list[Path]) -> dict[tuple[str, str], list[dict[str, Any]]]:
    rows_by_key: dict[tuple[str, str], list[dict[str, Any]]] = {}
    for path in paths:
        payload = json.loads(path.read_text(encoding="utf-8"))
        for row in payload.get("rows", []):
            if not isinstance(row, dict):
                continue
            key = (str(row.get("profile_name") or ""), str(row.get("session_key") or ""))
            if not all(key):
                continue
            rows_by_key.setdefault(key, []).append(row)
    return rows_by_key


def valid_decisions(rows: list[dict[str, Any]]) -> list[str]:
    return [str(row.get("decision") or "").strip() for row in rows if str(row.get("decision") or "").strip() in VALID_DECISIONS]


def majority_allow(rows: list[dict[str, Any]]) -> bool:
    decisions = valid_decisions(rows)
    if not decisions:
        return False
    return Counter(decisions).most_common(1)[0][0] == ALLOW_NEXT_SESSION


def consensus_allow(rows: list[dict[str, Any]], *, expected_count: int) -> bool:
    decisions = valid_decisions(rows)
    return len(decisions) == expected_count and all(decision == ALLOW_NEXT_SESSION for decision in decisions)


def get_feature(row: dict[str, Any], *keys: str, default: float = 0.0) -> float:
    payload = row.get("payload") if isinstance(row, dict) else None
    current: Any = payload
    for key in keys:
        if not isinstance(current, dict):
            return default
        current = current.get(key)
    try:
        return float(current)
    except Exception:
        return default


def evaluate_strategies(rows_by_key: dict[tuple[str, str], list[dict[str, Any]]], *, profile_name: str) -> list[dict[str, Any]]:
    filtered_keys = sorted(key for key in rows_by_key if key[0] == profile_name)
    run_count = max((len(rows_by_key[key]) for key in filtered_keys), default=0)

    def score(strategy_name: str, allow_fn: Any) -> dict[str, Any]:
        baseline_net = 0.0
        allowed_net = 0.0
        allowed_sessions: list[dict[str, Any]] = []
        for key in filtered_keys:
            rows = rows_by_key[key]
            row0 = rows[0]
            next_pnl = float(row0.get("next_session_net_pnl_dollars") or 0.0)
            baseline_net += next_pnl
            if allow_fn(rows):
                allowed_net += next_pnl
                allowed_sessions.append(
                    {
                        "session_key": key[1],
                        "session_label": str(row0.get("session_label") or ""),
                        "next_session_net_pnl_dollars": round(next_pnl, 4),
                        "prev_day_net_pnl_dollars": round(
                            get_feature(row0, "previous_day_summary", "net_pnl_dollars"), 4
                        ),
                        "same_session_trailing_net_pnl_dollars": round(
                            get_feature(row0, "same_session_trailing_summary", "net_pnl_dollars"), 4
                        ),
                        "run_decisions": valid_decisions(rows),
                    }
                )
        return {
            "name": strategy_name,
            "profile_name": profile_name,
            "case_count": int(len(filtered_keys)),
            "allowed_count": int(len(allowed_sessions)),
            "allowed_net_pnl_dollars": round(allowed_net, 4),
            "baseline_net_pnl_dollars": round(baseline_net, 4),
            "net_delta_dollars": round(allowed_net - baseline_net, 4),
            "allowed_sessions": allowed_sessions,
        }

    return [
        score("truffle_majority", lambda rows: majority_allow(rows)),
        score("truffle_consensus", lambda rows: consensus_allow(rows, expected_count=run_count)),
        score(
            "hard_red_prev_day_ge_5_plus_majority",
            lambda rows: (
                get_feature(rows[0], "previous_day_summary", "net_pnl_dollars") < 5.0
                and majority_allow(rows)
            ),
        ),
        score(
            "hard_red_prev_day_ge_5_plus_consensus",
            lambda rows: (
                get_feature(rows[0], "previous_day_summary", "net_pnl_dollars") < 5.0
                and consensus_allow(rows, expected_count=run_count)
            ),
        ),
        score(
            "hard_red_plus_overnight_rebound_only",
            lambda rows: (
                get_feature(rows[0], "previous_day_summary", "net_pnl_dollars") < 5.0
                and str(rows[0].get("session_label") or "") == "overnight"
                and get_feature(rows[0], "same_session_trailing_summary", "net_pnl_dollars") > 0.0
            ),
        ),
        score(
            "hard_red_plus_overnight_rebound_plus_majority",
            lambda rows: (
                (
                    get_feature(rows[0], "previous_day_summary", "net_pnl_dollars") < 5.0
                    and str(rows[0].get("session_label") or "") == "overnight"
                    and get_feature(rows[0], "same_session_trailing_summary", "net_pnl_dollars") > 0.0
                )
                or (
                    get_feature(rows[0], "previous_day_summary", "net_pnl_dollars") < 5.0
                    and majority_allow(rows)
                )
            ),
        ),
    ]


def main() -> None:
    parser = argparse.ArgumentParser(description="Evaluate committee and hybrid lease strategies over Truffle session outputs.")
    parser.add_argument("--inputs", nargs="+", required=True)
    parser.add_argument("--profile", default="live_90_70")
    parser.add_argument("--output-path", default=str(DEFAULT_OUTPUT_PATH))
    args = parser.parse_args()

    input_paths = [Path(value).resolve() if not Path(value).is_absolute() else Path(value) for value in args.inputs]
    rows_by_key = load_rows(input_paths)
    strategies = evaluate_strategies(rows_by_key, profile_name=str(args.profile))
    payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "profile_name": str(args.profile),
        "input_paths": [str(path) for path in input_paths],
        "strategies": strategies,
    }

    output_path = Path(args.output_path)
    if not output_path.is_absolute():
        output_path = ROOT / output_path
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")

    print(f"Saved committee evaluation to {output_path}")
    for row in strategies:
        print(row["name"], row["allowed_count"], row["allowed_net_pnl_dollars"], row["net_delta_dollars"])


if __name__ == "__main__":
    main()
