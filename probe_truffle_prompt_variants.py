from __future__ import annotations

import json
import time
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

import requests

from truffle_regime_lease import (
    DEFAULT_TRUFFLE_REASONING_TOOL_PROMPT,
    build_lease_decision_tool_schema,
    compact_reasoning_payload,
    parse_lease_decision,
    resolve_truffle_chat_completion_endpoint,
    resolve_truffle_model_id,
)

OUTPUT_PATH = Path("logs") / "truffle_prompt_variants_latest.json"
MODEL_NAME = "Qwen3.6-35B-A3B"
MAX_TOKENS = 1600
TIMEOUT_SECONDS = 120

SAMPLE_PAYLOAD = {
    "schema_version": "lease_input_v1",
    "strategy_family": "btc15m_supervisor",
    "candidate_profile_if_allowed": "90_78",
    "configured_profile": "90_78",
    "lease_scope": "next_market_only",
    "next_market_ticker": "KXBTC15M-PROMPTSCAN",
    "next_market_session": "afternoon",
    "deterministic_precheck": "PASS",
    "generated_at": "2026-04-20T16:05:00+00:00",
    "recent_4_markets": {
        "traded_markets": 3,
        "positive_trade_fraction": 0.6667,
        "net_pnl_dollars": 12.0,
        "exit_loss_dollars": 6.0,
        "settlement_loss_count": 0,
        "stale_book_deferral_count": 0,
        "ioc_zero_fill_count": 0,
        "submit_latency_p95_ms": 330.0,
    },
    "recent_8_markets": {
        "traded_markets": 6,
        "positive_trade_fraction": 0.6667,
        "net_pnl_dollars": 20.0,
        "exit_loss_dollars": 6.0,
        "settlement_loss_count": 0,
        "stale_book_deferral_count": 1,
        "ioc_zero_fill_count": 1,
        "submit_latency_p95_ms": 380.0,
    },
    "last_4_market_sequence": [
        {
            "market": "m1",
            "outcome_type": "win",
            "pnl_dollars": 10.0,
            "signal_count": 1,
            "stale_book_deferral_count": 0,
            "ioc_zero_fill_count": 0,
        },
        {
            "market": "m2",
            "outcome_type": "loss",
            "pnl_dollars": -6.0,
            "signal_count": 1,
            "stale_book_deferral_count": 0,
            "ioc_zero_fill_count": 0,
        },
        {
            "market": "m3",
            "outcome_type": "win",
            "pnl_dollars": 8.0,
            "signal_count": 1,
            "stale_book_deferral_count": 0,
            "ioc_zero_fill_count": 0,
        },
        {
            "market": "m4",
            "outcome_type": "skipped",
            "pnl_dollars": 0.0,
            "signal_count": 0,
            "stale_book_deferral_count": 0,
            "ioc_zero_fill_count": 0,
        },
    ],
}


@dataclass
class PromptVariant:
    name: str
    technique: str
    prompt: str
    reasoning_enabled: bool = False
    max_tokens: int = MAX_TOKENS


def build_prompt_variants() -> list[PromptVariant]:
    variants: list[PromptVariant] = []
    ultra_verbose_prompt = """
You are the regime lease issuer for a Kalshi BTC 15 minute trading bot.
Use the input to decide whether the next market should be leased for profile 90_78.
Your only final action is to call emit_lease_decision exactly once. Never answer in normal text.

Objective:
- loss mitigation first
- avoid trading ambiguous or degraded regimes
- do not chase trade count

Interpret the evidence this way:
- deterministic_precheck is the bot's hard readiness state and should dominate if it is not PASS
- recent_4_markets is the highest-priority short-horizon regime summary
- recent_8_markets is a secondary broader context summary
- positive_trade_fraction approximates whether recent trades are mostly favorable
- net_pnl_dollars summarizes realized edge over the window
- exit_loss_dollars warns that the current strategy may be giving back value on exits
- settlement_loss_count warns about recent full-loss outcomes
- stale_book_deferral_count and ioc_zero_fill_count warn about execution quality degradation
- submit_latency_p95_ms warns about rising system reaction lag
- last_4_market_sequence shows clustering, streaks, and whether recent outcomes are improving or degrading

Decision guidance:
- block if evidence is sparse, contradictory, or weak
- block if recent losses or friction metrics suggest a bad regime
- allow only when recent evidence is supportive enough to justify new risk
- if uncertain, choose BLOCK_NEXT_MARKET

Output contract:
- decision must be ALLOW_90_78_NEXT_MARKET or BLOCK_NEXT_MARKET
- candidate_profile_if_allowed must be 90_78
- lease_scope must be next_market_only
- next_market_ticker must exactly copy the input ticker
- next_market_session must exactly copy the input session
- valid_for_market_ticker must exactly copy the input ticker
- issued_at must be an ISO8601 UTC timestamp
- confidence must be numeric and between 0.0 and 1.0
- rationale_code must be short, machine-friendly, and specific
- summary_reason must be one short sentence

Failure guardrails:
- do not restate the entire input
- do not narrate your reasoning in content
- do not produce markdown
- do not emit partial or malformed tool calls
- do not invent unsupported decisions or profiles
""".strip()
    variants.append(
        PromptVariant(
            name="baseline_minimal",
            technique="baseline",
            prompt=DEFAULT_TRUFFLE_REASONING_TOOL_PROMPT.strip(),
        )
    )
    variants.append(
        PromptVariant(
            name="schema_lock_medium",
            technique="schema_lock",
            prompt="""
You are the regime lease issuer for a Kalshi BTC 15 minute trading bot.
Call emit_lease_decision exactly once. Do not answer in plain text.

Output contract:
- decision must be ALLOW_90_78_NEXT_MARKET or BLOCK_NEXT_MARKET
- candidate_profile_if_allowed must be 90_78
- lease_scope must be next_market_only
- next_market_ticker must exactly equal the input ticker
- next_market_session must exactly equal the input session
- valid_for_market_ticker must exactly equal the input ticker
- confidence must be between 0.0 and 1.0
- rationale_code must be short and machine-friendly
- summary_reason must be one short sentence

If uncertain, block.
""".strip(),
        )
    )
    variants.append(
        PromptVariant(
            name="priority_rubric_rich",
            technique="priority_rubric",
            prompt="""
You issue regime leases for a BTC 15m trading bot.
Think privately and then call emit_lease_decision exactly once.
Never answer in normal text.

Decision priority:
1. Respect deterministic_precheck first. If it is not PASS, block.
2. Prefer loss mitigation over trade count.
3. Block when recent outcomes indicate a bad or ambiguous regime.
4. Allow only when recent evidence is clearly supportive.

Interpretation hints:
- positive_trade_fraction is a rough win-rate style summary
- net_pnl_dollars is the recent realized edge summary
- exit_loss_dollars, settlement_loss_count, stale_book_deferral_count, and ioc_zero_fill_count are regime friction or failure warnings
- last_4_market_sequence shows clustering and streak behavior

Required field rules:
- candidate_profile_if_allowed = 90_78
- lease_scope = next_market_only
- next_market_ticker/session/valid_for_market_ticker must copy the input
- rationale_code short
- summary_reason one short sentence
- if uncertain, choose BLOCK_NEXT_MARKET
""".strip(),
        )
    )
    variants.append(
        PromptVariant(
            name="guardrails_rich",
            technique="guardrails",
            prompt="""
You are a structured lease classifier for a Kalshi BTC 15 minute bot.
Return your final answer only by calling emit_lease_decision exactly once.

Do not:
- restate the input
- explain your reasoning in normal text
- include markdown
- invent extra fields
- change the ticker or session
- output a partial tool call

Do:
- be conservative
- prefer blocking over weak confidence allows
- use short machine-friendly rationale_code values
- keep summary_reason to one sentence
- keep confidence between 0 and 1

Map the evidence to one of two decisions only:
- ALLOW_90_78_NEXT_MARKET
- BLOCK_NEXT_MARKET
""".strip(),
        )
    )
    variants.append(
        PromptVariant(
            name="field_semantics_richer",
            technique="field_semantics",
            prompt="""
You are the regime lease issuer for a Kalshi BTC 15 minute trading bot.
Your only final action is to call emit_lease_decision exactly once.

Field semantics:
- deterministic_precheck: hard readiness signal from the bot
- recent_4_markets: short-term regime snapshot
- recent_8_markets: broader recent regime snapshot
- positive_trade_fraction: fraction of recent traded markets that were positive
- net_pnl_dollars: realized profit or loss over the summary window
- exit_loss_dollars: realized damage from exits over the summary window
- settlement_loss_count: recent full-loss outcomes
- stale_book_deferral_count and ioc_zero_fill_count: execution-friction warnings
- last_4_market_sequence: streaks, clustering, and recency context

Decision intent:
- allow only when recent evidence is supportive enough for loss mitigation goals
- block when evidence is weak, contradictory, sparse, or fragile
- if uncertain, block

Field constraints:
- candidate_profile_if_allowed = 90_78
- lease_scope = next_market_only
- copy next_market_ticker, next_market_session, and valid_for_market_ticker from the input
- use one short sentence for summary_reason
""".strip(),
        )
    )
    variants.append(
        PromptVariant(
            name="delimited_contract_rich",
            technique="delimited_contract",
            prompt="""
<role>
You issue regime leases for a Kalshi BTC 15 minute trading bot.
</role>
<action>
Call emit_lease_decision exactly once.
Do not answer in plain text.
</action>
<constraints>
decision: ALLOW_90_78_NEXT_MARKET or BLOCK_NEXT_MARKET
candidate_profile_if_allowed: 90_78
lease_scope: next_market_only
next_market_ticker: copy input exactly
next_market_session: copy input exactly
valid_for_market_ticker: copy input ticker exactly
confidence: 0.0 to 1.0
rationale_code: short machine-friendly token
summary_reason: one short sentence
</constraints>
<policy>
Prefer blocking over weak or ambiguous allows.
Loss mitigation matters more than trade count.
If uncertain, block.
</policy>
""".strip(),
        )
    )
    variants.append(
        PromptVariant(
            name="fewshot_micro_rich",
            technique="fewshot_micro",
            prompt="""
You are the regime lease issuer for a Kalshi BTC 15 minute trading bot.
Call emit_lease_decision exactly once and do not answer in plain text.

Mini examples:
- weak or sparse evidence -> BLOCK_NEXT_MARKET
- clear positive recent regime with passing precheck -> ALLOW_90_78_NEXT_MARKET

Required field rules:
- candidate_profile_if_allowed = 90_78
- lease_scope = next_market_only
- ticker/session/valid_for_market_ticker copied from input
- confidence between 0 and 1
- rationale_code short
- summary_reason one short sentence

If evidence is mixed or unclear, block.
""".strip(),
        )
    )
    variants.append(
        PromptVariant(
            name="ultra_verbose_max",
            technique="max_detail",
            prompt=ultra_verbose_prompt,
            max_tokens=2200,
        )
    )
    variants.append(
        PromptVariant(
            name="max_plus_examples_xl",
            technique="examples_plus_detail",
            prompt=(
                ultra_verbose_prompt
                + "\n\nMini decision examples:\n"
                + "- Example A: deterministic_precheck is PASS, recent_4_markets net_pnl_dollars is positive, positive_trade_fraction is high, and friction metrics are quiet -> ALLOW_90_78_NEXT_MARKET.\n"
                + "- Example B: deterministic_precheck is PASS but recent_4_markets is weak, losses are clustering, or friction is elevated -> BLOCK_NEXT_MARKET.\n"
                + "- Example C: evidence is sparse or contradictory -> BLOCK_NEXT_MARKET.\n"
                + "\nDo not copy these examples into the final output. Use them only as policy guidance."
            ),
            max_tokens=2400,
        )
    )
    variants.append(
        PromptVariant(
            name="max_plus_decision_ladder_xxl",
            technique="decision_ladder",
            prompt=(
                ultra_verbose_prompt
                + "\n\nDecision ladder:\n"
                + "1. Hard-readiness gate: if deterministic_precheck is not PASS, block.\n"
                + "2. Evidence sufficiency gate: if recent history is too sparse to judge, block.\n"
                + "3. Regime quality gate: if recent_4_markets or last_4_market_sequence suggests a degrading regime, block.\n"
                + "4. Execution-friction gate: if stale-book, IOC-zero-fill, settlement-loss, or latency warnings are elevated, lean block unless evidence is unusually strong.\n"
                + "5. Allow gate: only allow when recent evidence is clearly positive after the earlier gates.\n"
                + "\nTie-break rule: in any close case or mixed case, block."
            ),
            max_tokens=2400,
        )
    )
    variants.append(
        PromptVariant(
            name="max_plus_failure_taxonomy_xxxl",
            technique="failure_taxonomy",
            prompt=(
                ultra_verbose_prompt
                + "\n\nFailure taxonomy to watch for:\n"
                + "- bad_regime: recent outcomes indicate the strategy has lost local edge\n"
                + "- execution_friction: stale_book_deferral_count, ioc_zero_fill_count, or latency suggest the strategy may fail even if the underlying idea is okay\n"
                + "- weak_signal_quality: positive_trade_fraction or net_pnl_dollars are too weak to justify new risk\n"
                + "- loss_cluster: last_4_market_sequence shows clustered adverse outcomes\n"
                + "- sparse_evidence: not enough recent traded markets or sequence evidence to judge\n"
                + "\nUse rationale_code values that reflect the dominant failure mode or dominant positive case.\n"
                + "Do not mention this taxonomy directly in the summary_reason unless it helps keep the sentence short and specific."
            ),
            max_tokens=2600,
        )
    )
    variants.append(
        PromptVariant(
            name="overstuffed_reference_manual",
            technique="ceiling_search",
            prompt=(
                ultra_verbose_prompt
                + "\n\nReference manual:\n"
                + "- Prefer recent_4_markets over recent_8_markets when they disagree, unless the short window is obviously too sparse.\n"
                + "- Treat positive_trade_fraction, net_pnl_dollars, and last_4_market_sequence as the main edge clues.\n"
                + "- Treat exit_loss_dollars, settlement_loss_count, stale_book_deferral_count, ioc_zero_fill_count, and submit_latency_p95_ms as the main fragility clues.\n"
                + "- A clean allow usually needs: PASS precheck, non-sparse evidence, positive recent PnL, acceptable recent win quality, and no material friction warnings.\n"
                + "- A clean block usually comes from: sparse evidence, clustered losses, deteriorating sequence, weak recent profitability, or elevated friction.\n"
                + "- Keep the decision aligned with loss mitigation, not upside imagination.\n"
                + "- Never allow because of a single positive metric if the rest of the picture is weak.\n"
                + "- Never block because of a single weak warning if the broader picture is clearly strong, unless the warning is a hard readiness problem.\n"
                + "\nStructured output reminders:\n"
                + "- next_market_ticker must match the input exactly character-for-character\n"
                + "- next_market_session must match the input exactly\n"
                + "- valid_for_market_ticker must equal next_market_ticker\n"
                + "- candidate_profile_if_allowed must stay 90_78 even when blocking\n"
                + "- confidence should reflect decisiveness, not optimism\n"
                + "- rationale_code should be concise, uppercase or machine-friendly, and specific\n"
                + "- summary_reason should stay under roughly one short sentence and should not become a paragraph\n"
                + "\nAnti-failure reminders:\n"
                + "- do not paraphrase the whole payload before acting\n"
                + "- do not write your analysis into normal content\n"
                + "- do not emit a malformed partial tool call\n"
                + "- do not drift the schema_version, lease_scope, or decision names\n"
                + "- if any part of the evidence feels underdetermined, choose BLOCK_NEXT_MARKET"
            ),
            max_tokens=2800,
        )
    )
    variants.append(
        PromptVariant(
            name="reasoning_enabled_probe",
            technique="reasoning_probe",
            prompt="""
You are the regime lease issuer for a Kalshi BTC 15 minute trading bot.
Think privately in the reasoning channel only.
When ready, call emit_lease_decision exactly once.
Do not answer in plain text.

Use recent_4_markets first, recent_8_markets second, and block if uncertain.
All output fields must satisfy the strict lease contract.
""".strip(),
            reasoning_enabled=True,
            max_tokens=2200,
        )
    )
    return variants


def classify_shape(response_payload: dict[str, Any]) -> str:
    if not isinstance(response_payload, dict):
        return "unknown"
    choices = response_payload.get("choices")
    if not isinstance(choices, list) or not choices:
        return "unknown"
    choice = choices[0]
    if not isinstance(choice, dict):
        return "unknown"
    message = choice.get("message")
    if not isinstance(message, dict):
        return "unknown"
    if isinstance(message.get("tool_calls"), list) and message.get("tool_calls"):
        return "tool_calls"
    content = str(message.get("content") or "")
    if "<tool_call>" in content:
        return "pseudo_tool_text"
    if "thinking process" in content.lower():
        return "reasoning_in_content"
    if content:
        return "plain_content"
    return "empty_content"


def run_variant(variant: PromptVariant, *, endpoint: str, model: str) -> dict[str, Any]:
    compact_payload = compact_reasoning_payload(SAMPLE_PAYLOAD)
    body = {
        "model": model,
        "temperature": 0,
        "max_tokens": int(variant.max_tokens),
        "tools": build_lease_decision_tool_schema(),
        "tool_choice": "auto",
        "messages": [
            {"role": "system", "content": variant.prompt},
            {"role": "user", "content": json.dumps(compact_payload, sort_keys=True, separators=(",", ":"))},
        ],
        "reasoning": {"enabled": bool(variant.reasoning_enabled)},
    }
    started = time.perf_counter()
    try:
        response = requests.post(
            endpoint,
            json=body,
            timeout=TIMEOUT_SECONDS,
        )
        response.raise_for_status()
        response_payload = response.json()
        http_error = ""
    except Exception as exc:
        elapsed = round(time.perf_counter() - started, 3)
        return {
            "variant": asdict(variant),
            "elapsed_seconds": elapsed,
            "http_error": str(exc),
            "valid": False,
            "decision": "",
            "parse_error": f"http_error:{exc}",
            "shape": "http_error",
            "finish_reason": "",
            "prompt_chars": len(variant.prompt),
            "content_preview": "",
            "raw_response_preview": "",
        }
    elapsed = round(time.perf_counter() - started, 3)
    parsed = parse_lease_decision(
        response_payload,
        issuer="truffle_http",
        next_market_ticker=str(SAMPLE_PAYLOAD["next_market_ticker"]),
        next_market_session=str(SAMPLE_PAYLOAD["next_market_session"]),
        input_payload=SAMPLE_PAYLOAD,
    )
    choices = response_payload.get("choices") if isinstance(response_payload, dict) else None
    first_choice = choices[0] if isinstance(choices, list) and choices else {}
    message = first_choice.get("message") if isinstance(first_choice, dict) else {}
    content_preview = ""
    if isinstance(message, dict):
        content_preview = str(message.get("content") or "")[:600]
    usage = response_payload.get("usage", {}) if isinstance(response_payload, dict) else {}
    return {
        "variant": asdict(variant),
        "elapsed_seconds": elapsed,
        "http_error": http_error,
        "valid": bool(parsed.is_valid),
        "decision": parsed.decision,
        "parse_error": parsed.parse_error,
        "summary_reason": parsed.summary_reason,
        "rationale_code": parsed.rationale_code,
        "confidence": parsed.confidence,
        "shape": classify_shape(response_payload),
        "finish_reason": first_choice.get("finish_reason") if isinstance(first_choice, dict) else "",
        "usage": usage,
        "prompt_chars": len(variant.prompt),
        "content_preview": content_preview,
        "raw_response_preview": parsed.raw_response[:1000],
    }


def choose_best(results: list[dict[str, Any]]) -> dict[str, Any] | None:
    valid_results = [row for row in results if row.get("valid")]
    if not valid_results:
        return None
    valid_results.sort(
        key=lambda row: (
            int(row.get("prompt_chars") or 0),
            -float(row.get("elapsed_seconds") or 0.0),
        ),
        reverse=True,
    )
    return valid_results[0]


def main() -> None:
    endpoint = resolve_truffle_chat_completion_endpoint("")
    model = resolve_truffle_model_id(MODEL_NAME, endpoint=endpoint, timeout_ms=8000) or MODEL_NAME
    variants = build_prompt_variants()
    results: list[dict[str, Any]] = []
    for index, variant in enumerate(variants, start=1):
        print(f"[{index}/{len(variants)}] {variant.name}")
        results.append(run_variant(variant, endpoint=endpoint, model=model))
    best = choose_best(results)
    payload = {
        "endpoint": endpoint,
        "model": model,
        "sample_payload": SAMPLE_PAYLOAD,
        "compact_payload": compact_reasoning_payload(SAMPLE_PAYLOAD),
        "results": results,
        "best_variant": best,
    }
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    print()
    print("Summary")
    for row in results:
        name = row["variant"]["name"]
        valid = "valid" if row.get("valid") else "invalid"
        elapsed = row.get("elapsed_seconds")
        prompt_chars = row.get("prompt_chars")
        shape = row.get("shape")
        parse_error = row.get("parse_error") or ""
        print(f"- {name}: {valid}, {elapsed}s, {prompt_chars} chars, {shape}, {parse_error}")
    print()
    if best:
        print("Best variant")
        print(json.dumps(best, indent=2, sort_keys=True))
    else:
        print("No valid variant found.")


if __name__ == "__main__":
    main()
