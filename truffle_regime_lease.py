from __future__ import annotations

import json
import math
import os
import re
import time
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import requests

LEASE_INPUT_SCHEMA_VERSION = "lease_input_v1"
LEASE_DECISION_SCHEMA_VERSION = "lease_decision_v1"
LEASE_SCOPE = "next_market_only"
ALLOW_90_78_NEXT_MARKET = "ALLOW_90_78_NEXT_MARKET"
BLOCK_NEXT_MARKET = "BLOCK_NEXT_MARKET"
VALID_LEASE_DECISIONS = {ALLOW_90_78_NEXT_MARKET, BLOCK_NEXT_MARKET}
VALID_LEASE_MODES = {"disabled", "shadow_only", "enforce_entries_only"}
VALID_LEASE_ISSUERS = {"stub", "truffle_http"}
DEFAULT_TRUFFLE_CHAT_COMPLETIONS_PATH = "/if2/v1/chat/completions"
DEFAULT_TRUFFLE_MODELS_PATH = "/if2/v1/models"
DEFAULT_TRUFFLE_MODEL_PREFERENCE = ("Qwen3.5-2B", "Qwen3.6-35B-A3B")
PLAIN_JSON_FALLBACK_SUFFIX = (
    "Return a single JSON object only. Do not include markdown, reasoning, "
    "code fences, or any prose before or after the JSON object."
)
DEFAULT_LEASE_MAX_TOKENS = 220
DEFAULT_REASONING_LEASE_MAX_TOKENS = 2400
LEASE_DECISION_TOOL_NAME = "emit_lease_decision"
_MODEL_CACHE_BY_ENDPOINT: dict[str, str] = {}

DEFAULT_TRUFFLE_LEASE_PROMPT = """You are the regime lease issuer for a Kalshi BTC 15 minute trading bot.
Return JSON only.

You must choose exactly one decision:
- ALLOW_90_78_NEXT_MARKET
- BLOCK_NEXT_MARKET

Be conservative. The goal is loss mitigation, not maximum trade count.
Use the recent market summaries to decide whether the next market should be traded.
Do not explain with prose outside the JSON object.

Required output schema:
{
  "schema_version": "lease_decision_v1",
  "decision": "ALLOW_90_78_NEXT_MARKET or BLOCK_NEXT_MARKET",
  "candidate_profile_if_allowed": "90_78",
  "lease_scope": "next_market_only",
  "next_market_ticker": "<same ticker from input>",
  "next_market_session": "<same session from input>",
  "valid_for_market_ticker": "<same ticker from input>",
  "issued_at": "<ISO8601 UTC timestamp>",
  "confidence": 0.0,
  "rationale_code": "<short machine-friendly code>",
  "summary_reason": "<one short sentence>"
}
"""

DEFAULT_TRUFFLE_REASONING_TOOL_PROMPT = """You are the regime lease issuer for a Kalshi BTC 15 minute trading bot.
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

Reference manual:
- Prefer recent_4_markets over recent_8_markets when they disagree, unless the short window is obviously too sparse.
- Treat positive_trade_fraction, net_pnl_dollars, and last_4_market_sequence as the main edge clues.
- Treat exit_loss_dollars, settlement_loss_count, stale_book_deferral_count, ioc_zero_fill_count, and submit_latency_p95_ms as the main fragility clues.
- A clean allow usually needs: PASS precheck, non-sparse evidence, positive recent PnL, acceptable recent win quality, and no material friction warnings.
- A clean block usually comes from: sparse evidence, clustered losses, deteriorating sequence, weak recent profitability, or elevated friction.
- Keep the decision aligned with loss mitigation, not upside imagination.
- Never allow because of a single positive metric if the rest of the picture is weak.
- Never block because of a single weak warning if the broader picture is clearly strong, unless the warning is a hard readiness problem.

Structured output reminders:
- next_market_ticker must match the input exactly character-for-character
- next_market_session must match the input exactly
- valid_for_market_ticker must equal next_market_ticker
- candidate_profile_if_allowed must stay 90_78 even when blocking
- confidence should reflect decisiveness, not optimism
- rationale_code should be concise, uppercase or machine-friendly, and specific
- summary_reason should stay under roughly one short sentence and should not become a paragraph

Anti-failure reminders:
- do not paraphrase the whole payload before acting
- do not write your analysis into normal content
- do not emit a malformed partial tool call
- do not drift the schema_version, lease_scope, or decision names
- if any part of the evidence feels underdetermined, choose BLOCK_NEXT_MARKET
"""


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def utc_now_iso() -> str:
    return utc_now().isoformat()


def default_truffile_state_path() -> Path | None:
    local_app_data = os.environ.get("LOCALAPPDATA", "").strip()
    candidates: list[Path] = []
    if local_app_data:
        candidates.append(Path(local_app_data) / "truffile" / "truffile" / "state.json")
    candidates.append(Path.home() / ".truffile" / "state.json")
    candidates.append(Path.home() / ".local" / "share" / "truffile" / "truffile" / "state.json")
    for candidate in candidates:
        if candidate.exists():
            return candidate
    return candidates[0] if candidates else None


def load_truffile_state() -> dict[str, Any]:
    path = default_truffile_state_path()
    if path is None:
        return {}
    try:
        parsed = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}
    return parsed if isinstance(parsed, dict) else {}


def discover_truffle_device_name() -> str:
    state = load_truffile_state()
    last_used = str(state.get("last_used_device") or "").strip()
    if last_used:
        return last_used
    tokens = state.get("tokens")
    if isinstance(tokens, dict):
        for key in tokens:
            device = str(key or "").strip()
            if device:
                return device
    return ""


def resolve_truffle_chat_completion_endpoint(endpoint: str) -> str:
    text = str(endpoint or "").strip()
    if text:
        normalized = text.rstrip("/")
        lower = normalized.lower()
        if lower.endswith("/chat/completions"):
            return normalized
        if lower.endswith("/models"):
            return normalized[: -len("/models")] + "/chat/completions"
        if lower.endswith("/if2/v1"):
            return normalized + "/chat/completions"
        if "/if2/v1/" not in lower:
            return normalized + DEFAULT_TRUFFLE_CHAT_COMPLETIONS_PATH
        return normalized
    device = discover_truffle_device_name()
    if not device:
        return ""
    return f"http://{device}.local{DEFAULT_TRUFFLE_CHAT_COMPLETIONS_PATH}"


def resolve_truffle_models_endpoint(endpoint: str) -> str:
    chat_endpoint = resolve_truffle_chat_completion_endpoint(endpoint)
    if not chat_endpoint:
        return ""
    normalized = chat_endpoint.rstrip("/")
    lower = normalized.lower()
    if lower.endswith("/chat/completions"):
        return normalized[: -len("/chat/completions")] + "/models"
    if lower.endswith("/if2/v1"):
        return normalized + "/models"
    if lower.endswith("/models"):
        return normalized
    return normalized + DEFAULT_TRUFFLE_MODELS_PATH


def resolve_truffle_model_id(model: str, *, endpoint: str, timeout_ms: int) -> str:
    explicit = str(model or "").strip()
    if explicit:
        return explicit
    models_endpoint = resolve_truffle_models_endpoint(endpoint)
    if not models_endpoint:
        return ""
    cached = _MODEL_CACHE_BY_ENDPOINT.get(models_endpoint)
    if cached:
        return cached
    try:
        response = requests.get(
            models_endpoint,
            timeout=max(0.25, min(float(timeout_ms) / 1000.0, 5.0)),
        )
        response.raise_for_status()
        payload = response.json()
    except Exception:
        return ""
    entries = payload.get("data") if isinstance(payload, dict) else None
    if not isinstance(entries, list):
        return ""
    available_ids = [str(item.get("id") or "").strip() for item in entries if isinstance(item, dict)]
    available_ids = [item for item in available_ids if item]
    if not available_ids:
        return ""
    for preferred in DEFAULT_TRUFFLE_MODEL_PREFERENCE:
        if preferred in available_ids:
            _MODEL_CACHE_BY_ENDPOINT[models_endpoint] = preferred
            return preferred
    chosen = available_ids[0]
    _MODEL_CACHE_BY_ENDPOINT[models_endpoint] = chosen
    return chosen


def model_looks_like_reasoning(model: str) -> bool:
    text = str(model or "").strip().lower()
    return any(token in text for token in ("35b", "reason", "r1", "thinking"))


def normalize_reasoning_enabled(reasoning_enabled: str | bool | None, *, model: str) -> bool:
    if isinstance(reasoning_enabled, bool):
        return reasoning_enabled
    text = str(reasoning_enabled or "").strip().lower()
    if text in {"1", "true", "yes", "on"}:
        return True
    if text in {"0", "false", "no", "off"}:
        return False
    return model_looks_like_reasoning(model)


def resolve_lease_max_tokens(max_tokens: int | None, *, model: str, reasoning_enabled: bool) -> int:
    requested = int(max_tokens or 0)
    if requested > 0:
        return requested
    if reasoning_enabled and model_looks_like_reasoning(model):
        return DEFAULT_REASONING_LEASE_MAX_TOKENS
    return DEFAULT_LEASE_MAX_TOKENS


def build_lease_decision_tool_schema() -> list[dict[str, Any]]:
    return [
        {
            "type": "function",
            "function": {
                "name": LEASE_DECISION_TOOL_NAME,
                "description": "Emit the final lease decision as structured arguments.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "schema_version": {"type": "string"},
                        "decision": {
                            "type": "string",
                            "enum": [ALLOW_90_78_NEXT_MARKET, BLOCK_NEXT_MARKET],
                        },
                        "candidate_profile_if_allowed": {"type": "string"},
                        "lease_scope": {"type": "string"},
                        "next_market_ticker": {"type": "string"},
                        "next_market_session": {"type": "string"},
                        "valid_for_market_ticker": {"type": "string"},
                        "issued_at": {"type": "string"},
                        "confidence": {"type": "number"},
                        "rationale_code": {"type": "string"},
                        "summary_reason": {"type": "string"},
                    },
                    "required": [
                        "schema_version",
                        "decision",
                        "candidate_profile_if_allowed",
                        "lease_scope",
                        "next_market_ticker",
                        "next_market_session",
                        "valid_for_market_ticker",
                        "issued_at",
                        "confidence",
                        "rationale_code",
                        "summary_reason",
                    ],
                    "additionalProperties": False,
                },
            },
        }
    ]


def compact_reasoning_payload(payload: dict[str, Any]) -> dict[str, Any]:
    def compact_summary(summary: Any) -> dict[str, Any]:
        if not isinstance(summary, dict):
            return {}
        keys = (
            "traded_markets",
            "signal_markets",
            "signal_count_total",
            "positive_trade_fraction",
            "net_pnl_dollars",
            "exit_loss_dollars",
            "settlement_loss_count",
            "stale_book_deferral_count",
            "stale_deferrals_per_signal",
            "ioc_zero_fill_count",
            "ioc_zero_fills_per_trade",
            "submit_latency_p95_ms",
            "avg_entry_trigger_cents",
            "exit_count",
            "count",
            "trade_count",
            "win_count",
            "traded_win_count",
            "loss_count",
            "traded_loss_count",
            "traded_exit_count",
            "skip_count",
            "avg_pnl_dollars",
            "win_rate",
        )
        compacted: dict[str, Any] = {}
        for key in keys:
            if key in summary:
                compacted[key] = summary[key]
        return compacted

    compact_sequence: list[dict[str, Any]] = []
    if isinstance(payload.get("last_4_market_sequence"), list):
        for row in payload.get("last_4_market_sequence", [])[:4]:
            if not isinstance(row, dict):
                continue
            compact_sequence.append(
                {
                    "market": row.get("market"),
                    "session": row.get("session"),
                    "traded": row.get("traded"),
                    "outcome_type": row.get("outcome_type"),
                    "pnl_dollars": row.get("pnl_dollars"),
                    "signal_count": row.get("signal_count"),
                    "stale_book_deferral_count": row.get("stale_book_deferral_count"),
                    "ioc_zero_fill_count": row.get("ioc_zero_fill_count"),
                }
            )

    return {
        "schema_version": str(payload.get("schema_version") or LEASE_INPUT_SCHEMA_VERSION),
        "strategy_family": str(payload.get("strategy_family") or "btc15m_supervisor"),
        "candidate_profile_if_allowed": "90_78",
        "configured_profile": str(payload.get("configured_profile") or "90_78"),
        "lease_scope": LEASE_SCOPE,
        "next_market_ticker": str(payload.get("next_market_ticker") or ""),
        "next_market_session": str(payload.get("next_market_session") or "unknown"),
        "deterministic_precheck": str(payload.get("deterministic_precheck") or "UNKNOWN"),
        "generated_at": str(payload.get("generated_at") or utc_now_iso()),
        "recent_4_markets": compact_summary(payload.get("recent_4_markets")),
        "recent_8_markets": compact_summary(payload.get("recent_8_markets")),
        "last_4_market_sequence": compact_sequence,
    }


def extract_tool_call_dict(payload: Any) -> dict[str, Any] | None:
    if isinstance(payload, dict):
        tool_calls = payload.get("tool_calls")
        if isinstance(tool_calls, list):
            for tool_call in tool_calls:
                if not isinstance(tool_call, dict):
                    continue
                function = tool_call.get("function")
                if not isinstance(function, dict):
                    continue
                if str(function.get("name") or "").strip() != LEASE_DECISION_TOOL_NAME:
                    continue
                arguments = function.get("arguments")
                extracted = extract_tool_call_dict(arguments)
                if extracted is not None:
                    return extracted
        if isinstance(payload.get("choices"), list) and payload.get("choices"):
            for choice in payload["choices"]:
                extracted = extract_tool_call_dict(choice)
                if extracted is not None:
                    return extracted
        message = payload.get("message")
        if isinstance(message, dict):
            extracted = extract_tool_call_dict(message)
            if extracted is not None:
                return extracted
        if "arguments" in payload:
            extracted = extract_tool_call_dict(payload.get("arguments"))
            if extracted is not None:
                return extracted
        return None
    if isinstance(payload, list):
        for item in payload:
            extracted = extract_tool_call_dict(item)
            if extracted is not None:
                return extracted
        return None
    if payload in (None, ""):
        return None
    text = str(payload)
    stripped = text.strip()
    if not stripped:
        return None
    try:
        parsed = json.loads(stripped)
    except Exception:
        parsed = None
    if isinstance(parsed, dict):
        return parsed
    if "<tool_call>" not in text or f"<function={LEASE_DECISION_TOOL_NAME}>" not in text:
        return None
    matches = re.findall(r"<parameter=([^>]+)>\s*(.*?)\s*</parameter>", text, flags=re.DOTALL)
    if not matches:
        return None
    extracted: dict[str, Any] = {}
    for key, value in matches:
        cleaned_key = str(key or "").strip()
        cleaned_value = str(value or "").strip()
        if not cleaned_key:
            continue
        extracted[cleaned_key] = cleaned_value
    return extracted or None


def parse_iso(value: Any) -> datetime | None:
    if value in (None, ""):
        return None
    text = str(value).strip()
    if not text:
        return None
    try:
        return datetime.fromisoformat(text.replace("Z", "+00:00"))
    except Exception:
        return None


def coerce_float(value: Any, default: float = 0.0) -> float:
    if value in (None, ""):
        return default
    try:
        return float(value)
    except Exception:
        return default


def coerce_int(value: Any, default: int = 0) -> int:
    if value in (None, ""):
        return default
    try:
        return int(float(value))
    except Exception:
        return default


def percentile_95(values: list[float]) -> float:
    if not values:
        return 0.0
    ordered = sorted(float(v) for v in values)
    if len(ordered) == 1:
        return round(ordered[0], 4)
    rank = 0.95 * (len(ordered) - 1)
    lower = int(math.floor(rank))
    upper = int(math.ceil(rank))
    if lower == upper:
        return round(ordered[lower], 4)
    blend = rank - lower
    return round((ordered[lower] * (1.0 - blend)) + (ordered[upper] * blend), 4)


def infer_session_label(dt: datetime | None) -> str:
    if dt is None:
        return "unknown"
    hour = dt.hour
    if hour < 6:
        return "overnight"
    if hour < 12:
        return "morning"
    if hour < 17:
        return "afternoon"
    if hour < 22:
        return "evening"
    return "late_evening"


def extract_json_dict(payload: Any) -> dict[str, Any] | None:
    if isinstance(payload, dict):
        tool_dict = extract_tool_call_dict(payload)
        if tool_dict is not None:
            return tool_dict
        if isinstance(payload.get("choices"), list) and payload.get("choices"):
            choice = payload["choices"][0]
            if isinstance(choice, dict):
                message = choice.get("message")
                if isinstance(message, dict):
                    content = message.get("content")
                    extracted = extract_json_dict(content)
                    if extracted is not None:
                        return extracted
                if "text" in choice:
                    extracted = extract_json_dict(choice.get("text"))
                    if extracted is not None:
                        return extracted
        if isinstance(payload.get("output"), list):
            for item in payload["output"]:
                extracted = extract_json_dict(item)
                if extracted is not None:
                    return extracted
        if any(key in payload for key in ("schema_version", "decision", "next_market_ticker", "valid_for_market_ticker")):
            return payload
        return None
    if isinstance(payload, list):
        for item in payload:
            extracted = extract_json_dict(item)
            if extracted is not None:
                return extracted
        return None
    if payload in (None, ""):
        return None
    text = str(payload).strip()
    if not text:
        return None
    try:
        parsed = json.loads(text)
    except Exception:
        start = text.find("{")
        end = text.rfind("}")
        if start < 0 or end <= start:
            return None
        try:
            parsed = json.loads(text[start : end + 1])
        except Exception:
            return None
    return parsed if isinstance(parsed, dict) else None


@dataclass
class LeaseDecision:
    schema_version: str = LEASE_DECISION_SCHEMA_VERSION
    decision: str = BLOCK_NEXT_MARKET
    candidate_profile_if_allowed: str = "90_78"
    lease_scope: str = LEASE_SCOPE
    next_market_ticker: str = ""
    next_market_session: str = "unknown"
    valid_for_market_ticker: str = ""
    issued_at: str = ""
    confidence: float = 0.0
    rationale_code: str = ""
    summary_reason: str = ""
    issuer: str = ""
    raw_response: str = ""
    parse_error: str = ""
    input_payload: dict[str, Any] = field(default_factory=dict)

    @property
    def is_valid(self) -> bool:
        return not self.parse_error

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class MarketOutcomeRecord:
    market: str
    side: str = ""
    session: str = "unknown"
    watched_at: str = ""
    market_close_time: str = ""
    resolved_at: str = ""
    signal_count: int = 0
    traded: bool = False
    outcome_type: str = "open_or_unresolved"
    pnl_dollars: float = 0.0
    entry_trigger_cents: int | None = None
    entry_qty: int = 0
    entry_fill_cents: int | None = None
    entry_notional_cents: int = 0
    entry_fee_cents: int = 0
    exit_qty: int = 0
    exit_fill_cents: int | None = None
    exit_notional_cents: int = 0
    exit_fee_cents: int = 0
    exit_count: int = 0
    exit_loss_dollars: float = 0.0
    stale_book_deferral_count: int = 0
    dead_market_deferral_count: int = 0
    ioc_zero_fill_count: int = 0
    submit_latency_samples_ms: list[float] = field(default_factory=list)
    side_cashflows: dict[str, dict[str, float]] = field(default_factory=dict)
    settlement_result: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    def sort_key(self) -> tuple[str, str]:
        primary = str(self.market_close_time or self.resolved_at or self.watched_at or "")
        return (primary, self.market)

    def add_submit_latency(self, latency_ms: float) -> None:
        if latency_ms < 0:
            return
        self.submit_latency_samples_ms.append(round(float(latency_ms), 4))
        self.submit_latency_samples_ms = self.submit_latency_samples_ms[-32:]

    def record_signal(self) -> None:
        self.signal_count += 1

    def _numeric(self, value: Any) -> float:
        try:
            return float(value or 0.0)
        except (TypeError, ValueError):
            return 0.0

    def _side_cashflow(self, side: str) -> dict[str, float]:
        normalized = str(side or "").strip().lower()
        if normalized not in {"yes", "no"}:
            normalized = str(self.side or "").strip().lower()
        if normalized not in {"yes", "no"}:
            normalized = "unknown"
        bucket = self.side_cashflows.setdefault(
            normalized,
            {
                "entry_qty": 0,
                "entry_notional_cents": 0,
                "entry_fee_cents": 0,
                "exit_qty": 0,
                "exit_notional_cents": 0,
                "exit_fee_cents": 0,
            },
        )
        for key in (
            "entry_qty",
            "entry_notional_cents",
            "entry_fee_cents",
            "exit_qty",
            "exit_notional_cents",
            "exit_fee_cents",
        ):
            bucket[key] = self._numeric(bucket.get(key))
        return bucket

    def _side_remaining_contracts(self, side: str) -> float:
        bucket = self.side_cashflows.get(side) or {}
        return max(0.0, self._numeric(bucket.get("entry_qty")) - self._numeric(bucket.get("exit_qty")))

    def _side_remaining_entry_notional_cents(self, side: str) -> float:
        bucket = self.side_cashflows.get(side) or {}
        remaining = self._side_remaining_contracts(side)
        entry_qty = self._numeric(bucket.get("entry_qty"))
        if remaining <= 0 or entry_qty <= 0:
            return 0.0
        avg_entry_cents = self._numeric(bucket.get("entry_notional_cents")) / max(1.0, entry_qty)
        return max(0.0, avg_entry_cents * remaining)

    def _side_settlement_payout_cents(self, result: str) -> float:
        normalized = str(result or "").strip().lower()
        if not self.side_cashflows:
            return 0
        if normalized == "void":
            return sum(self._side_remaining_entry_notional_cents(side) for side in self.side_cashflows)
        if normalized not in {"yes", "no"}:
            return 0.0
        return 100 * self._side_remaining_contracts(normalized)

    def record_entry(
        self,
        *,
        side: str,
        qty: float,
        fill_price_cents: float,
        fee_cents: float,
        trigger_price_cents: int | None,
    ) -> None:
        if qty <= 0 or fill_price_cents <= 0:
            return
        qty_value = float(qty)
        fill_value = float(fill_price_cents)
        fee_value = max(0.0, float(fee_cents or 0.0))
        self.side = side
        self.traded = True
        self.outcome_type = "open_or_unresolved"
        self.entry_qty += qty_value
        self.entry_notional_cents += fill_value * qty_value
        self.entry_fee_cents += fee_value
        self.entry_fill_cents = int(round(self.entry_notional_cents / max(1, self.entry_qty)))
        bucket = self._side_cashflow(side)
        bucket["entry_qty"] += qty_value
        bucket["entry_notional_cents"] += fill_value * qty_value
        bucket["entry_fee_cents"] += fee_value
        if trigger_price_cents is not None and self.entry_trigger_cents is None:
            self.entry_trigger_cents = int(trigger_price_cents)

    def record_exit_fill(
        self,
        *,
        side: str = "",
        qty: float,
        fill_price_cents: float,
        fee_cents: float,
        remaining_position: float,
        resolved_at: str,
    ) -> None:
        if qty <= 0 or fill_price_cents <= 0:
            return
        qty_value = float(qty)
        fill_value = float(fill_price_cents)
        fee_value = max(0.0, float(fee_cents or 0.0))
        self.exit_qty += qty_value
        self.exit_notional_cents += fill_value * qty_value
        self.exit_fee_cents += fee_value
        self.exit_count += 1
        self.exit_fill_cents = int(round(self.exit_notional_cents / max(1, self.exit_qty)))
        bucket = self._side_cashflow(side)
        bucket["exit_qty"] += qty_value
        bucket["exit_notional_cents"] += fill_value * qty_value
        bucket["exit_fee_cents"] += fee_value
        if self.entry_fill_cents is not None and fill_price_cents < self.entry_fill_cents:
            loss_dollars = ((self.entry_fill_cents - fill_value) * qty_value) / 100.0
            self.exit_loss_dollars = round(self.exit_loss_dollars + loss_dollars, 4)
        if remaining_position <= 0:
            gross = (self.exit_notional_cents - self.entry_notional_cents) / 100.0
            fees = (self.entry_fee_cents + self.exit_fee_cents) / 100.0
            self.pnl_dollars = round(gross - fees, 4)
            self.outcome_type = "exit"
            self.resolved_at = resolved_at

    def remaining_contracts(self) -> float:
        return max(0.0, float(self.entry_qty or 0.0) - float(self.exit_qty or 0.0))

    def remaining_entry_notional_cents(self) -> float:
        remaining = self.remaining_contracts()
        if remaining <= 0 or self.entry_qty <= 0:
            return 0.0
        avg_entry_cents = self.entry_notional_cents / max(1, self.entry_qty)
        return max(0.0, avg_entry_cents * remaining)

    def net_pnl_cents_with_settlement(self, *, settlement_payout_cents: float) -> float:
        return (
            float(self.exit_notional_cents)
            + float(settlement_payout_cents)
            - float(self.entry_notional_cents)
            - float(self.entry_fee_cents)
            - float(self.exit_fee_cents)
        )

    def recompute_terminal_pnl_from_cashflows(self) -> None:
        if not self.traded or self.entry_qty <= 0:
            return
        if self.outcome_type not in {"exit", "win", "settlement_loss", "void"}:
            return
        settlement_payout_cents = 0.0
        if self.side_cashflows and self.settlement_result:
            settlement_payout_cents = self._side_settlement_payout_cents(self.settlement_result)
        elif self.outcome_type == "win":
            settlement_payout_cents = 100 * self.remaining_contracts()
        elif self.outcome_type == "void":
            settlement_payout_cents = self.remaining_entry_notional_cents()
        pnl_cents = self.net_pnl_cents_with_settlement(
            settlement_payout_cents=settlement_payout_cents
        )
        self.pnl_dollars = round(pnl_cents / 100.0, 4)

    def finalize_no_trade(self, *, resolved_at: str) -> None:
        if self.traded:
            return
        self.outcome_type = "no_trade"
        self.pnl_dollars = 0.0
        self.resolved_at = resolved_at

    def finalize_settlement(self, *, result: str, resolved_at: str) -> None:
        normalized = str(result or "").strip().lower()
        if not self.traded or self.entry_qty <= 0 or self.entry_fill_cents is None:
            if normalized == "void":
                self.outcome_type = "void"
                self.pnl_dollars = 0.0
                self.settlement_result = normalized
                self.resolved_at = resolved_at
            return
        if self.outcome_type == "exit":
            return
        remaining_qty = self.remaining_contracts()
        settlement_payout_cents = 0
        if normalized == "void":
            self.outcome_type = "void"
            settlement_payout_cents = (
                self._side_settlement_payout_cents(normalized)
                if self.side_cashflows
                else self.remaining_entry_notional_cents()
            )
        elif normalized in {"yes", "no"}:
            settlement_payout_cents = (
                self._side_settlement_payout_cents(normalized)
                if self.side_cashflows
                else (100 * remaining_qty if self.side and self.side == normalized else 0)
            )
            if settlement_payout_cents > 0:
                self.outcome_type = "win"
            else:
                self.outcome_type = "settlement_loss"
        else:
            return
        self.settlement_result = normalized
        pnl_cents = self.net_pnl_cents_with_settlement(
            settlement_payout_cents=settlement_payout_cents
        )
        self.pnl_dollars = round(pnl_cents / 100.0, 4)
        self.resolved_at = resolved_at


class MarketOutcomeStore:
    def __init__(self, path: Path, *, max_records: int = 256) -> None:
        self.path = path
        self.max_records = max(16, int(max_records))
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.records: dict[str, MarketOutcomeRecord] = {}
        self._load()

    def _load(self) -> None:
        if not self.path.exists():
            self.records = {}
            return
        try:
            raw = json.loads(self.path.read_text(encoding="utf-8"))
        except Exception:
            self.records = {}
            return
        items = raw.get("records") if isinstance(raw, dict) else raw
        if not isinstance(items, list):
            self.records = {}
            return
        loaded: dict[str, MarketOutcomeRecord] = {}
        for item in items:
            if not isinstance(item, dict):
                continue
            market = str(item.get("market") or "").strip()
            if not market:
                continue
            try:
                record = MarketOutcomeRecord(**item)
                record.recompute_terminal_pnl_from_cashflows()
                loaded[market] = record
            except Exception:
                continue
        self.records = loaded

    def save(self) -> None:
        ordered = sorted(self.records.values(), key=lambda row: row.sort_key())
        payload = {
            "updated_at": utc_now_iso(),
            "records": [row.to_dict() for row in ordered[-self.max_records :]],
        }
        self.path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")

    def ensure_market(
        self,
        market: str,
        *,
        session: str = "unknown",
        watched_at: str = "",
        market_close_time: str = "",
    ) -> MarketOutcomeRecord:
        record = self.records.get(market)
        if record is None:
            record = MarketOutcomeRecord(
                market=market,
                session=session or "unknown",
                watched_at=watched_at or utc_now_iso(),
                market_close_time=market_close_time or "",
            )
            self.records[market] = record
        else:
            if session and record.session == "unknown":
                record.session = session
            if watched_at and not record.watched_at:
                record.watched_at = watched_at
            if market_close_time and not record.market_close_time:
                record.market_close_time = market_close_time
        return record

    def mark_signal_seen(self, market: str) -> None:
        record = self.ensure_market(market)
        record.record_signal()
        self.save()

    def mark_stale_deferral(self, market: str) -> None:
        record = self.ensure_market(market)
        record.stale_book_deferral_count += 1
        self.save()

    def mark_dead_market_deferral(self, market: str) -> None:
        record = self.ensure_market(market)
        record.dead_market_deferral_count += 1
        self.save()

    def mark_ioc_zero_fill(self, market: str) -> None:
        record = self.ensure_market(market)
        record.ioc_zero_fill_count += 1
        self.save()

    def mark_submit_latency(self, market: str, latency_ms: float) -> None:
        record = self.ensure_market(market)
        record.add_submit_latency(latency_ms)
        self.save()

    def record_entry(
        self,
        market: str,
        *,
        side: str,
        qty: int,
        fill_price_cents: int,
        fee_cents: int,
        trigger_price_cents: int | None,
    ) -> None:
        record = self.ensure_market(market)
        record.record_entry(
            side=side,
            qty=qty,
            fill_price_cents=fill_price_cents,
            fee_cents=fee_cents,
            trigger_price_cents=trigger_price_cents,
        )
        self.save()

    def record_exit_fill(
        self,
        market: str,
        *,
        side: str = "",
        qty: int,
        fill_price_cents: int,
        fee_cents: int,
        remaining_position: int,
        resolved_at: str,
    ) -> None:
        record = self.ensure_market(market)
        record.record_exit_fill(
            side=side,
            qty=qty,
            fill_price_cents=fill_price_cents,
            fee_cents=fee_cents,
            remaining_position=remaining_position,
            resolved_at=resolved_at,
        )
        self.save()

    def finalize_no_trade(self, market: str, *, resolved_at: str) -> None:
        record = self.ensure_market(market)
        record.finalize_no_trade(resolved_at=resolved_at)
        self.save()

    def finalize_settlement(self, market: str, *, result: str, resolved_at: str) -> None:
        record = self.ensure_market(market)
        record.finalize_settlement(result=result, resolved_at=resolved_at)
        self.save()

    def get(self, market: str) -> MarketOutcomeRecord | None:
        return self.records.get(market)

    def recent_records(self, *, limit: int, exclude_market: str | None = None) -> list[MarketOutcomeRecord]:
        ordered = sorted(self.records.values(), key=lambda row: row.sort_key())
        if exclude_market:
            ordered = [row for row in ordered if row.market != exclude_market]
        return ordered[-max(0, int(limit)) :]

    def unresolved_closed_markets(self, *, as_of: datetime | None = None, limit: int = 8) -> list[MarketOutcomeRecord]:
        now = as_of or utc_now()
        pending: list[MarketOutcomeRecord] = []
        for record in self.records.values():
            close_dt = parse_iso(record.market_close_time)
            if close_dt is None or close_dt > now:
                continue
            if record.outcome_type == "open_or_unresolved":
                pending.append(record)
        pending.sort(key=lambda row: row.sort_key())
        return pending[-max(1, int(limit)) :]


class LeaseCacheStore:
    def __init__(self, path: Path) -> None:
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def load(self) -> LeaseDecision | None:
        if not self.path.exists():
            return None
        try:
            raw = json.loads(self.path.read_text(encoding="utf-8"))
        except Exception:
            return None
        if not isinstance(raw, dict):
            return None
        try:
            return LeaseDecision(**raw)
        except Exception:
            return None

    def save(self, decision: LeaseDecision) -> None:
        self.path.write_text(json.dumps(decision.to_dict(), indent=2, sort_keys=True), encoding="utf-8")


class LeaseEventWriter:
    def __init__(self, path: Path) -> None:
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def emit(self, event_type: str, **payload: Any) -> None:
        event = {
            "event_type": event_type,
            "ts_wall": utc_now_iso(),
            "ts_mono": round(time.monotonic(), 6),
        }
        event.update(payload)
        with self.path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(event, sort_keys=True) + "\n")


def build_recent_market_summary(records: list[MarketOutcomeRecord]) -> dict[str, Any]:
    traded_records = [row for row in records if row.traded]
    latency_samples: list[float] = []
    trigger_values: list[int] = []
    positive_trades = 0
    exit_loss_dollars = 0.0
    settlement_loss_count = 0
    for row in records:
        latency_samples.extend(float(value) for value in row.submit_latency_samples_ms if value is not None)
        if row.entry_trigger_cents is not None and row.traded:
            trigger_values.append(int(row.entry_trigger_cents))
        if row.traded and float(row.pnl_dollars) > 0:
            positive_trades += 1
        if row.outcome_type == "settlement_loss":
            settlement_loss_count += 1
        exit_loss_dollars += float(row.exit_loss_dollars or 0.0)
    avg_entry_trigger = round(sum(trigger_values) / len(trigger_values), 4) if trigger_values else 0.0
    positive_fraction = round(positive_trades / len(traded_records), 4) if traded_records else 0.0
    return {
        "traded_markets": len(traded_records),
        "signal_markets": sum(1 for row in records if row.signal_count > 0),
        "net_pnl_dollars": round(sum(float(row.pnl_dollars or 0.0) for row in records if row.traded), 4),
        "exit_count": sum(int(row.exit_count or 0) for row in records),
        "exit_loss_dollars": round(exit_loss_dollars, 4),
        "settlement_loss_count": settlement_loss_count,
        "avg_entry_trigger_cents": avg_entry_trigger,
        "stale_book_deferral_count": sum(int(row.stale_book_deferral_count or 0) for row in records),
        "ioc_zero_fill_count": sum(int(row.ioc_zero_fill_count or 0) for row in records),
        "submit_latency_p95_ms": percentile_95(latency_samples),
        "positive_trade_fraction": positive_fraction,
    }


def build_last_market_sequence(records: list[MarketOutcomeRecord]) -> list[dict[str, Any]]:
    sequence: list[dict[str, Any]] = []
    for row in records:
        sequence.append(
            {
                "market": row.market,
                "session": row.session,
                "traded": row.traded,
                "signal_count": row.signal_count,
                "outcome_type": row.outcome_type,
                "pnl_dollars": round(float(row.pnl_dollars or 0.0), 4),
                "entry_trigger_cents": row.entry_trigger_cents if row.entry_trigger_cents is not None else 0,
                "stale_book_deferral_count": int(row.stale_book_deferral_count or 0),
                "ioc_zero_fill_count": int(row.ioc_zero_fill_count or 0),
            }
        )
    return sequence


def parse_lease_decision(
    payload: Any,
    *,
    issuer: str,
    next_market_ticker: str,
    next_market_session: str,
    input_payload: dict[str, Any],
) -> LeaseDecision:
    extracted = extract_json_dict(payload)
    raw_response = payload if isinstance(payload, str) else json.dumps(payload, sort_keys=True)
    if extracted is None:
        return LeaseDecision(
            issuer=issuer,
            next_market_ticker=next_market_ticker,
            next_market_session=next_market_session,
            valid_for_market_ticker=next_market_ticker,
            issued_at=utc_now_iso(),
            raw_response=str(raw_response),
            parse_error="missing_json_object",
            input_payload=input_payload,
        )
    decision = str(extracted.get("decision") or "").strip().upper()
    if decision == "ALLOW_NEXT_MARKET":
        decision = ALLOW_90_78_NEXT_MARKET
    if decision not in VALID_LEASE_DECISIONS:
        return LeaseDecision(
            issuer=issuer,
            next_market_ticker=next_market_ticker,
            next_market_session=next_market_session,
            valid_for_market_ticker=next_market_ticker,
            issued_at=utc_now_iso(),
            raw_response=str(raw_response),
            parse_error=f"invalid_decision:{decision or 'missing'}",
            input_payload=input_payload,
        )
    candidate_profile = "90_78"
    extracted_next_market = str(extracted.get("next_market_ticker") or next_market_ticker).strip() or next_market_ticker
    valid_for_market = str(extracted.get("valid_for_market_ticker") or extracted_next_market or next_market_ticker).strip()
    parsed = LeaseDecision(
        schema_version=LEASE_DECISION_SCHEMA_VERSION,
        decision=decision,
        candidate_profile_if_allowed=candidate_profile,
        lease_scope=LEASE_SCOPE,
        next_market_ticker=extracted_next_market,
        next_market_session=str(extracted.get("next_market_session") or next_market_session).strip() or next_market_session,
        valid_for_market_ticker=valid_for_market or next_market_ticker,
        issued_at=str(extracted.get("issued_at") or utc_now_iso()),
        confidence=max(0.0, min(1.0, coerce_float(extracted.get("confidence"), 0.0))),
        rationale_code=str(extracted.get("rationale_code") or "").strip(),
        summary_reason=str(extracted.get("summary_reason") or "").strip(),
        issuer=issuer,
        raw_response=str(raw_response),
        parse_error="",
        input_payload=input_payload,
    )
    if parsed.next_market_ticker != next_market_ticker:
        parsed.parse_error = f"next_market_mismatch:{parsed.next_market_ticker}"
    elif parsed.valid_for_market_ticker != next_market_ticker:
        parsed.parse_error = f"market_mismatch:{parsed.valid_for_market_ticker}"
    return parsed


def issue_stub_lease(payload: dict[str, Any]) -> LeaseDecision:
    recent_4 = payload.get("recent_4_markets", {})
    recent_8 = payload.get("recent_8_markets", {})
    recent_4_net = coerce_float(recent_4.get("net_pnl_dollars"))
    recent_8_net = coerce_float(recent_8.get("net_pnl_dollars"))
    recent_4_positive = coerce_float(recent_4.get("positive_trade_fraction"))
    recent_4_exit_loss = coerce_float(recent_4.get("exit_loss_dollars"))
    recent_4_settlement_losses = coerce_int(recent_4.get("settlement_loss_count"))
    decision = ALLOW_90_78_NEXT_MARKET
    rationale_code = "recent_regime_ok"
    summary_reason = "Recent market outcomes do not show a strong loss cluster."
    if recent_4_net <= -6.0:
        decision = BLOCK_NEXT_MARKET
        rationale_code = "recent4_net_loss_cluster"
        summary_reason = "Recent four-market net PnL is materially negative."
    elif recent_8_net <= -10.0:
        decision = BLOCK_NEXT_MARKET
        rationale_code = "recent8_net_loss_cluster"
        summary_reason = "Recent eight-market net PnL is materially negative."
    elif recent_4_settlement_losses >= 2:
        decision = BLOCK_NEXT_MARKET
        rationale_code = "settlement_loss_cluster"
        summary_reason = "Multiple recent settlement losses suggest a bad regime."
    elif recent_4_exit_loss >= 4.0 and recent_4_positive <= 0.25:
        decision = BLOCK_NEXT_MARKET
        rationale_code = "exit_loss_cluster"
        summary_reason = "Recent exit losses are elevated and win rate is weak."
    raw = {
        "schema_version": LEASE_DECISION_SCHEMA_VERSION,
        "decision": decision,
        "candidate_profile_if_allowed": "90_78",
        "lease_scope": LEASE_SCOPE,
        "next_market_ticker": str(payload.get("next_market_ticker") or ""),
        "next_market_session": str(payload.get("next_market_session") or "unknown"),
        "valid_for_market_ticker": str(payload.get("next_market_ticker") or ""),
        "issued_at": utc_now_iso(),
        "confidence": 0.55,
        "rationale_code": rationale_code,
        "summary_reason": summary_reason,
    }
    return parse_lease_decision(
        raw,
        issuer="stub",
        next_market_ticker=str(payload.get("next_market_ticker") or ""),
        next_market_session=str(payload.get("next_market_session") or "unknown"),
        input_payload=payload,
    )


def load_prompt_text(path: Path | None, *, default_text: str = DEFAULT_TRUFFLE_LEASE_PROMPT) -> str:
    if path is None:
        return default_text
    try:
        text = path.read_text(encoding="utf-8").strip()
    except Exception:
        return default_text
    return text or default_text


def maybe_build_deterministic_lease_decision(payload: dict[str, Any], *, issuer: str) -> LeaseDecision | None:
    next_market_ticker = str(payload.get("next_market_ticker") or "")
    next_market_session = str(payload.get("next_market_session") or "unknown")
    deterministic_precheck = str(payload.get("deterministic_precheck") or "").strip().upper()
    if deterministic_precheck and deterministic_precheck != "PASS":
        return parse_lease_decision(
            {
                "schema_version": LEASE_DECISION_SCHEMA_VERSION,
                "decision": BLOCK_NEXT_MARKET,
                "candidate_profile_if_allowed": "90_78",
                "lease_scope": LEASE_SCOPE,
                "next_market_ticker": next_market_ticker,
                "next_market_session": next_market_session,
                "valid_for_market_ticker": next_market_ticker,
                "issued_at": utc_now_iso(),
                "confidence": 1.0,
                "rationale_code": "DETERMINISTIC_PRECHECK_BLOCK",
                "summary_reason": "Deterministic precheck is not passing, so the next market is blocked.",
            },
            issuer=issuer,
            next_market_ticker=next_market_ticker,
            next_market_session=next_market_session,
            input_payload=payload,
        )
    recent_4 = payload.get("recent_4_markets", {})
    recent_8 = payload.get("recent_8_markets", {})
    total_recent_observations = max(
        coerce_int(recent_4.get("traded_markets"), 0),
        coerce_int(recent_4.get("trade_count"), 0),
        coerce_int(recent_4.get("signal_markets"), 0),
        coerce_int(recent_4.get("count"), 0),
        coerce_int(recent_8.get("traded_markets"), 0),
        coerce_int(recent_8.get("trade_count"), 0),
        coerce_int(recent_8.get("signal_markets"), 0),
        coerce_int(recent_8.get("count"), 0),
    )
    if total_recent_observations <= 0:
        return parse_lease_decision(
            {
                "schema_version": LEASE_DECISION_SCHEMA_VERSION,
                "decision": BLOCK_NEXT_MARKET,
                "candidate_profile_if_allowed": "90_78",
                "lease_scope": LEASE_SCOPE,
                "next_market_ticker": next_market_ticker,
                "next_market_session": next_market_session,
                "valid_for_market_ticker": next_market_ticker,
                "issued_at": utc_now_iso(),
                "confidence": 1.0,
                "rationale_code": "NO_RECENT_REGIME_DATA",
                "summary_reason": "No recent regime data is available, so the next market is blocked.",
            },
            issuer=issuer,
            next_market_ticker=next_market_ticker,
            next_market_session=next_market_session,
            input_payload=payload,
        )
    return None


def issue_truffle_http_lease(
    payload: dict[str, Any],
    *,
    endpoint: str,
    model: str,
    timeout_ms: int,
    prompt_text: str,
    tool_prompt_text: str = "",
    api_key: str = "",
    max_tokens: int = 0,
    reasoning_enabled: str | bool = "auto",
) -> LeaseDecision:
    deterministic_decision = maybe_build_deterministic_lease_decision(payload, issuer="truffle_http")
    if deterministic_decision is not None:
        return deterministic_decision
    resolved_endpoint = resolve_truffle_chat_completion_endpoint(endpoint)
    if not resolved_endpoint:
        return LeaseDecision(
            issuer="truffle_http",
            next_market_ticker=str(payload.get("next_market_ticker") or ""),
            next_market_session=str(payload.get("next_market_session") or "unknown"),
            valid_for_market_ticker=str(payload.get("next_market_ticker") or ""),
            issued_at=utc_now_iso(),
            raw_response="",
            parse_error="missing_endpoint",
            input_payload=payload,
        )
    resolved_model = resolve_truffle_model_id(model, endpoint=resolved_endpoint, timeout_ms=timeout_ms)
    if not resolved_model:
        return LeaseDecision(
            issuer="truffle_http",
            next_market_ticker=str(payload.get("next_market_ticker") or ""),
            next_market_session=str(payload.get("next_market_session") or "unknown"),
            valid_for_market_ticker=str(payload.get("next_market_ticker") or ""),
            issued_at=utc_now_iso(),
            raw_response="",
            parse_error="missing_model",
            input_payload=payload,
        )
    headers = {"Content-Type": "application/json"}
    if api_key.strip():
        headers["Authorization"] = f"Bearer {api_key.strip()}"
    use_reasoning = normalize_reasoning_enabled(reasoning_enabled, model=resolved_model)
    effective_max_tokens = resolve_lease_max_tokens(max_tokens, model=resolved_model, reasoning_enabled=use_reasoning)
    compact_payload_json = json.dumps(compact_reasoning_payload(payload), sort_keys=True, separators=(",", ":"))
    effective_tool_prompt = (tool_prompt_text or DEFAULT_TRUFFLE_REASONING_TOOL_PROMPT).strip()
    attempts: list[tuple[str, dict[str, Any]]] = []
    if use_reasoning and model_looks_like_reasoning(resolved_model):
        attempts.append(
            (
                "tool_call_no_reasoning",
                {
                    "model": resolved_model,
                    "temperature": 0,
                    "max_tokens": max(800, min(effective_max_tokens, 1600)),
                    "reasoning": {"enabled": False},
                    "tools": build_lease_decision_tool_schema(),
                    "tool_choice": "auto",
                    "messages": [
                        {"role": "system", "content": effective_tool_prompt},
                        {"role": "user", "content": compact_payload_json},
                    ],
                },
            )
        )
        attempts.append(
            (
                "reasoning_tool_call",
                {
                    "model": resolved_model,
                    "temperature": 0,
                    "max_tokens": effective_max_tokens,
                    "reasoning": {"enabled": True},
                    "tools": build_lease_decision_tool_schema(),
                    "tool_choice": "auto",
                    "messages": [
                        {"role": "system", "content": effective_tool_prompt},
                        {"role": "user", "content": compact_payload_json},
                    ],
                },
            )
        )
    attempts.extend(
        [
            (
                "json_mode",
                {
                    "model": resolved_model,
                    "temperature": 0,
                    "max_tokens": effective_max_tokens,
                    "messages": [
                        {"role": "system", "content": prompt_text or DEFAULT_TRUFFLE_LEASE_PROMPT},
                        {"role": "user", "content": json.dumps(payload, sort_keys=True)},
                    ],
                    "response_format": {"type": "json_object"},
                    **({"reasoning": {"enabled": True}} if use_reasoning else {}),
                },
            ),
            (
                "plain_json",
                {
                    "model": resolved_model,
                    "temperature": 0,
                    "max_tokens": effective_max_tokens,
                    "messages": [
                        {
                            "role": "system",
                            "content": ((prompt_text or DEFAULT_TRUFFLE_LEASE_PROMPT).strip() + "\n\n" + PLAIN_JSON_FALLBACK_SUFFIX).strip(),
                        },
                        {"role": "user", "content": json.dumps(payload, sort_keys=True)},
                    ],
                    **({"reasoning": {"enabled": True}} if use_reasoning else {}),
                },
            ),
        ]
    )
    attempt_errors: list[str] = []
    last_invalid_decision: LeaseDecision | None = None
    request_timeout = max(0.25, float(timeout_ms) / 1000.0)

    for attempt_name, body in attempts:
        try:
            response = requests.post(
                resolved_endpoint,
                headers=headers,
                json=body,
                timeout=request_timeout,
            )
            response.raise_for_status()
            response_payload = response.json()
        except Exception as exc:
            attempt_errors.append(f"{attempt_name}:http_error:{exc}")
            continue
        parsed = parse_lease_decision(
            response_payload,
            issuer="truffle_http",
            next_market_ticker=str(payload.get("next_market_ticker") or ""),
            next_market_session=str(payload.get("next_market_session") or "unknown"),
            input_payload=payload,
        )
        if parsed.is_valid:
            return parsed
        parsed.parse_error = f"{attempt_name}:{parsed.parse_error}"
        last_invalid_decision = parsed
        attempt_errors.append(parsed.parse_error)

    if last_invalid_decision is not None:
        last_invalid_decision.parse_error = "|".join(attempt_errors) or last_invalid_decision.parse_error
        return last_invalid_decision
    return LeaseDecision(
        issuer="truffle_http",
        next_market_ticker=str(payload.get("next_market_ticker") or ""),
        next_market_session=str(payload.get("next_market_session") or "unknown"),
        valid_for_market_ticker=str(payload.get("next_market_ticker") or ""),
        issued_at=utc_now_iso(),
        raw_response="",
        parse_error="|".join(attempt_errors) or "http_error:unknown",
        input_payload=payload,
    )


def lease_is_stale(decision: LeaseDecision | None, *, max_staleness_seconds: float, now: datetime | None = None) -> bool:
    if decision is None or not decision.is_valid:
        return True
    issued_at = parse_iso(decision.issued_at)
    if issued_at is None:
        return True
    age_seconds = ((now or utc_now()) - issued_at).total_seconds()
    return age_seconds > max(0.0, float(max_staleness_seconds))
