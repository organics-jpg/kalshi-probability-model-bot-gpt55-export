from __future__ import annotations

import argparse
import collections
import json
import statistics
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent
DEFAULT_LOG_PATH = ROOT / "logs" / "live_90_78_shadow_size2" / "truffle_post_entry_shadow.ndjson"
DEFAULT_OUTPUT_PATH = ROOT / "logs" / "live_post_entry_shadow_reliability_latest.json"


def iter_ndjson(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    if not path.exists():
        return rows
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        try:
            parsed = json.loads(line)
        except Exception:
            continue
        if isinstance(parsed, dict):
            rows.append(parsed)
    return rows


def parse_usage(raw_response: str) -> dict[str, Any]:
    try:
        parsed = json.loads(raw_response)
    except Exception:
        return {}
    if not isinstance(parsed, dict):
        return {}
    usage = parsed.get("usage")
    return usage if isinstance(usage, dict) else {}


def summarize_numeric(values: list[float]) -> dict[str, Any]:
    clean = [float(value) for value in values if isinstance(value, (int, float))]
    if not clean:
        return {"count": 0}
    return {
        "count": int(len(clean)),
        "avg": round(float(statistics.mean(clean)), 4),
        "min": round(float(min(clean)), 4),
        "max": round(float(max(clean)), 4),
    }


def summarize_exit_eval_rows(rows: list[dict[str, Any]]) -> dict[str, Any]:
    deltas = [float(row.get("delta_vs_actual_dollars") or 0.0) for row in rows]
    if not rows:
        return {
            "count": 0,
            "delta_if_exit_dollars": 0.0,
            "false_exit_cost_dollars": 0.0,
            "oracle_exit_value_dollars": 0.0,
            "truth_label_counts": {},
        }
    return {
        "count": int(len(rows)),
        "delta_if_exit_dollars": round(float(sum(deltas)), 4),
        "false_exit_cost_dollars": round(float(-sum(delta for delta in deltas if delta < 0)), 4),
        "oracle_exit_value_dollars": round(float(sum(delta for delta in deltas if delta > 0)), 4),
        "truth_label_counts": dict(collections.Counter(str(row.get("truth_label") or "") for row in rows)),
    }


def decision_label(row: dict[str, Any]) -> str:
    decision = row.get("decision") if isinstance(row.get("decision"), dict) else {}
    schema = str(decision.get("decision_schema") or row.get("decision_schema") or "").strip()
    exit_decision = str(decision.get("decision") or row.get("exit_supervisor_decision") or "").strip().upper()
    if schema == "exit_supervisor" or exit_decision in {"HOLD", "EXIT_NOW"}:
        return exit_decision or "INVALID"
    reversal_risk = str(decision.get("reversal_risk") or "").strip().upper()
    settlement_bias = str(decision.get("settlement_bias") or "").strip().upper()
    if reversal_risk == "HIGH":
        return "RED_LIGHT"
    if settlement_bias == "FAVORABLE" and reversal_risk != "HIGH":
        return "GREEN_LIGHT"
    if reversal_risk in {"LOW", "MEDIUM"} or settlement_bias in {"UNCLEAR", "UNFAVORABLE"}:
        return "NEUTRAL"
    if row.get("red_light"):
        return "RED_LIGHT"
    if row.get("green_light"):
        return "GREEN_LIGHT"
    if row.get("valid"):
        return "NEUTRAL"
    return "INVALID"


def post_entry_context(decision: dict[str, Any]) -> dict[str, Any]:
    payload = decision.get("input_payload") if isinstance(decision.get("input_payload"), dict) else {}
    post = payload.get("post_entry") if isinstance(payload.get("post_entry"), dict) else {}
    return post


def strong_above_entry_guard_applies(decision: dict[str, Any], label: str) -> bool:
    if label not in {"RED_LIGHT", "EXIT_NOW"}:
        return False
    post = post_entry_context(decision)
    return (
        str(post.get("current_strength") or "").strip().lower() == "strong"
        and str(post.get("current_vs_entry_state") or "").strip().lower() == "above_entry"
        and str(post.get("damage_state") or "").strip().lower() in {"light", "medium"}
    )


def guarded_decision_label(decision: dict[str, Any], label: str) -> str:
    if strong_above_entry_guard_applies(decision, label):
        return "HOLD_GUARDED_STRONG_ABOVE_ENTRY"
    return label


def red_guard_variants(decision: dict[str, Any], label: str) -> list[str]:
    if label not in {"RED_LIGHT", "EXIT_NOW"}:
        return []
    post = post_entry_context(decision)
    strength = str(post.get("current_strength") or "").strip().lower()
    vs_entry = str(post.get("current_vs_entry_state") or "").strip().lower()
    damage = str(post.get("damage_state") or "").strip().lower()
    variants: list[str] = []
    if strength == "strong" and vs_entry == "above_entry" and damage in {"light", "medium"}:
        variants.append("strong_above_light_medium")
    if strength == "strong" and vs_entry == "above_entry":
        variants.append("strong_above_any_damage")
    if strength == "strong" and vs_entry in {"above_entry", "near_entry"} and damage in {"light", "medium"}:
        variants.append("strong_near_or_above_light_medium")
    if strength == "strong" and vs_entry in {"above_entry", "near_entry"}:
        variants.append("strong_above_or_near_any")
    if strength == "strong" and damage in {"light", "medium"}:
        variants.append("strong_light_medium")
    return variants


def analyze(path: Path) -> dict[str, Any]:
    rows = iter_ndjson(path)
    event_counts = collections.Counter(str(row.get("event_type") or "unknown") for row in rows)
    decisions = [row for row in rows if row.get("event_type") == "post_entry_shadow_decision"]
    outcomes = [row for row in rows if row.get("event_type") == "post_entry_shadow_outcome"]
    valid_decisions = [row for row in decisions if bool(row.get("valid"))]
    invalid_decisions = [row for row in decisions if not bool(row.get("valid"))]

    usage_rows = [parse_usage(str((row.get("decision") or {}).get("raw_response") or "")) for row in valid_decisions]
    usage_summary = {
        "prompt_tokens": summarize_numeric([row.get("prompt_tokens") for row in usage_rows]),
        "completion_tokens": summarize_numeric([row.get("completion_tokens") for row in usage_rows]),
        "total_tokens": summarize_numeric([row.get("total_tokens") for row in usage_rows]),
        "ttft_ms": summarize_numeric([row.get("ttft_ms") for row in usage_rows]),
        "decode_tokens_per_second": summarize_numeric([row.get("decode_tokens_per_second") for row in usage_rows]),
    }

    outcome_pairs: list[dict[str, Any]] = []
    shadow_exit_evals: list[dict[str, Any]] = []
    decision_eval_rows: list[dict[str, Any]] = []
    for row in outcomes:
        decision = row.get("decision") if isinstance(row.get("decision"), dict) else {}
        shadow_eval = row.get("shadow_exit_eval") if isinstance(row.get("shadow_exit_eval"), dict) else {}
        label = decision_label({"decision": decision, **row})
        guarded_label = guarded_decision_label(decision, label)
        guard_variants = red_guard_variants(decision, label)
        if shadow_eval.get("available"):
            shadow_exit_evals.append(shadow_eval)
            decision_eval_rows.append(
                {
                    **shadow_eval,
                "decision_label": label,
                "guarded_decision_label": guarded_label,
                "guard_variants": guard_variants,
                "market": row.get("market"),
                "side": row.get("side"),
            }
            )
        outcome_pairs.append(
            {
                "market": row.get("market"),
                "side": row.get("side"),
                "decision_label": label,
                "guarded_decision_label": guarded_label,
                "guard_applied": bool(guarded_label != label),
                "guard_variants": guard_variants,
                "reversal_risk": decision.get("reversal_risk"),
                "settlement_bias": decision.get("settlement_bias"),
                "exit_supervisor_decision": decision.get("decision"),
                "confidence": decision.get("confidence"),
                "outcome_type": row.get("outcome_type"),
                "pnl_dollars": row.get("pnl_dollars"),
            }
        )

    pair_counts = collections.Counter(
        (row["decision_label"], row["outcome_type"])
        for row in outcome_pairs
    )
    red_or_exit = [
        row
        for row in outcome_pairs
        if row["decision_label"] in {"RED_LIGHT", "EXIT_NOW"}
    ]
    false_red_or_exit = [
        row
        for row in red_or_exit
        if row["outcome_type"] == "win"
    ]
    true_red_or_exit = [
        row
        for row in red_or_exit
        if row["outcome_type"] in {"exit", "settlement_loss"}
    ]
    guarded_red_or_exit = [
        row
        for row in outcome_pairs
        if row["guarded_decision_label"] in {"RED_LIGHT", "EXIT_NOW"}
    ]
    guarded_false_red_or_exit = [
        row
        for row in guarded_red_or_exit
        if row["outcome_type"] == "win"
    ]
    guarded_true_red_or_exit = [
        row
        for row in guarded_red_or_exit
        if row["outcome_type"] in {"exit", "settlement_loss"}
    ]
    guarded_away = [row for row in outcome_pairs if row.get("guard_applied")]
    guarded_away_false_wins = [row for row in guarded_away if row["outcome_type"] == "win"]
    guarded_away_true_adverse = [row for row in guarded_away if row["outcome_type"] in {"exit", "settlement_loss"}]
    guard_variant_scan: dict[str, Any] = {}
    for variant in sorted({variant for row in outcome_pairs for variant in list(row.get("guard_variants") or [])}):
        guarded_rows = [row for row in outcome_pairs if variant in list(row.get("guard_variants") or [])]
        remaining_rows = [
            row
            for row in outcome_pairs
            if row["decision_label"] in {"RED_LIGHT", "EXIT_NOW"} and variant not in list(row.get("guard_variants") or [])
        ]
        remaining_false = [row for row in remaining_rows if row["outcome_type"] == "win"]
        remaining_true = [row for row in remaining_rows if row["outcome_type"] in {"exit", "settlement_loss"}]
        guarded_false = [row for row in guarded_rows if row["outcome_type"] == "win"]
        guarded_true = [row for row in guarded_rows if row["outcome_type"] in {"exit", "settlement_loss"}]
        guard_variant_scan[variant] = {
            "guarded_count": int(len(guarded_rows)),
            "guarded_false_win_count": int(len(guarded_false)),
            "guarded_true_adverse_count": int(len(guarded_true)),
            "remaining_red_count": int(len(remaining_rows)),
            "remaining_false_win_count": int(len(remaining_false)),
            "remaining_true_adverse_count": int(len(remaining_true)),
            "remaining_false_win_rate": round(len(remaining_false) / len(remaining_rows), 4) if remaining_rows else None,
        }
    model_exit_eval_rows = [
        row
        for row in decision_eval_rows
        if str(row.get("decision_label") or "") in {"EXIT_NOW", "RED_LIGHT"}
    ]
    model_hold_eval_rows = [
        row
        for row in decision_eval_rows
        if str(row.get("decision_label") or "") in {"HOLD", "GREEN_LIGHT", "NEUTRAL"}
    ]
    by_decision_eval: dict[str, Any] = {}
    for label in sorted({str(row.get("decision_label") or "") for row in decision_eval_rows}):
        by_decision_eval[label] = summarize_exit_eval_rows(
            [row for row in decision_eval_rows if str(row.get("decision_label") or "") == label]
        )
    by_tag_model_exit: dict[str, dict[str, Any]] = {}
    for tag in sorted({tag for row in model_exit_eval_rows for tag in list(row.get("candidate_slice_tags") or [])}):
        tagged = [row for row in model_exit_eval_rows if tag in list(row.get("candidate_slice_tags") or [])]
        by_tag_model_exit[tag] = summarize_exit_eval_rows(tagged)
    eval_by_tag: dict[str, dict[str, Any]] = {}
    for tag in sorted({tag for row in shadow_exit_evals for tag in list(row.get("candidate_slice_tags") or [])}):
        tagged = [row for row in shadow_exit_evals if tag in list(row.get("candidate_slice_tags") or [])]
        deltas = [float(row.get("delta_vs_actual_dollars") or 0.0) for row in tagged]
        eval_by_tag[tag] = {
            "count": int(len(tagged)),
            "exit_now_truth_count": int(sum(1 for row in tagged if row.get("truth_label") == "EXIT_NOW")),
            "hold_truth_count": int(sum(1 for row in tagged if row.get("truth_label") == "HOLD")),
            "neutral_truth_count": int(sum(1 for row in tagged if row.get("truth_label") == "NEUTRAL")),
            "delta_if_exit_all_dollars": round(float(sum(deltas)), 4),
            "false_exit_cost_dollars": round(float(-sum(delta for delta in deltas if delta < 0)), 4),
            "oracle_exit_now_only_delta_dollars": round(float(sum(delta for delta in deltas if delta > 0)), 4),
        }

    return {
        "log_path": str(path),
        "event_count": int(len(rows)),
        "event_counts": dict(event_counts),
        "decision_count": int(len(decisions)),
        "valid_decision_count": int(len(valid_decisions)),
        "invalid_decision_count": int(len(invalid_decisions)),
        "parse_error_counts": dict(collections.Counter(str(row.get("parse_error") or "") for row in invalid_decisions)),
        "decision_label_counts": dict(collections.Counter(decision_label(row) for row in decisions)),
        "outcome_count": int(len(outcomes)),
        "outcome_type_counts": dict(collections.Counter(str(row.get("outcome_type") or "") for row in outcomes)),
        "decision_outcome_counts": {
            f"{decision}|{outcome}": int(count)
            for (decision, outcome), count in pair_counts.items()
        },
        "red_or_exit_outcome_summary": {
            "count": int(len(red_or_exit)),
            "true_adverse_count": int(len(true_red_or_exit)),
            "false_win_count": int(len(false_red_or_exit)),
            "false_win_rate": round(len(false_red_or_exit) / len(red_or_exit), 4) if red_or_exit else None,
        },
        "guarded_red_or_exit_outcome_summary": {
            "guard": "convert RED_LIGHT/EXIT_NOW to HOLD when post_entry is strong + above_entry + light_or_medium_damage",
            "count": int(len(guarded_red_or_exit)),
            "true_adverse_count": int(len(guarded_true_red_or_exit)),
            "false_win_count": int(len(guarded_false_red_or_exit)),
            "false_win_rate": round(len(guarded_false_red_or_exit) / len(guarded_red_or_exit), 4) if guarded_red_or_exit else None,
            "guarded_away_count": int(len(guarded_away)),
            "guarded_away_false_win_count": int(len(guarded_away_false_wins)),
            "guarded_away_true_adverse_count": int(len(guarded_away_true_adverse)),
            "guarded_away_markets": [str(row.get("market") or "") for row in guarded_away],
        },
        "guard_variant_scan": guard_variant_scan,
        "shadow_exit_eval_summary": {
            "available_count": int(len(shadow_exit_evals)),
            "truth_label_counts": dict(collections.Counter(str(row.get("truth_label") or "") for row in shadow_exit_evals)),
            "by_tag": eval_by_tag,
        },
        "model_exit_policy_eval_summary": {
            "available_count": int(len(decision_eval_rows)),
            "model_exit_count": int(len(model_exit_eval_rows)),
            "model_hold_or_non_exit_count": int(len(model_hold_eval_rows)),
            "model_exit": summarize_exit_eval_rows(model_exit_eval_rows),
            "model_hold_or_non_exit": summarize_exit_eval_rows(model_hold_eval_rows),
            "by_decision": by_decision_eval,
            "by_tag_when_model_exited": by_tag_model_exit,
        },
        "usage_summary": usage_summary,
        "recent_decisions": [
            {
                "ts_wall": row.get("ts_wall"),
                "market": row.get("market"),
                "side": row.get("side"),
                "decision_label": decision_label(row),
                "valid": bool(row.get("valid")),
                "parse_error": row.get("parse_error") or "",
                "candidate_slice_tags": row.get("candidate_slice_tags") or [],
            }
            for row in decisions[-10:]
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Summarize live post-entry Truffle shadow reliability and outcome alignment.")
    parser.add_argument("--log-path", default=str(DEFAULT_LOG_PATH))
    parser.add_argument("--output-path", default=str(DEFAULT_OUTPUT_PATH))
    args = parser.parse_args()

    log_path = Path(args.log_path)
    if not log_path.is_absolute():
        log_path = ROOT / log_path
    output_path = Path(args.output_path)
    if not output_path.is_absolute():
        output_path = ROOT / output_path

    payload = analyze(log_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    print(f"Saved live post-entry shadow reliability to {output_path}")
    print(json.dumps({
        "decision_count": payload["decision_count"],
        "valid_decision_count": payload["valid_decision_count"],
        "invalid_decision_count": payload["invalid_decision_count"],
        "decision_label_counts": payload["decision_label_counts"],
        "outcome_type_counts": payload["outcome_type_counts"],
        "red_or_exit_outcome_summary": payload["red_or_exit_outcome_summary"],
        "guarded_red_or_exit_outcome_summary": payload["guarded_red_or_exit_outcome_summary"],
        "guard_variant_scan": payload["guard_variant_scan"],
        "model_exit_policy_eval_summary": payload["model_exit_policy_eval_summary"],
    }, indent=2))


if __name__ == "__main__":
    main()
