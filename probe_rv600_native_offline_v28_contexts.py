from __future__ import annotations

import argparse
import glob
import json
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable, Mapping, Protocol

from btc_mushroom_forecaster_v28_fast import FastMushroomFVEngineV28
from build_v28_successor_public_rest_sidecar_bundle import (
    DEFAULT_COINBASE_BASE_URL,
    btc_rows_from_candles,
    fetch_coinbase_candles,
    market_close_ts,
    parse_btc_strike,
    parse_ts,
)
from research_particle.kalshi_market_results import PROD_BASE_URL, fetch_market_payload
from research_particle.spot_context_merge import SpotTickRow, load_spot_ticks


ROOT = Path(__file__).resolve().parent
DEFAULT_DATASET = "rv600_forward_native_shadow"
DEFAULT_CHECKPOINTS = (
    ROOT / "research_data" / DEFAULT_DATASET / "book_checkpoints" / "**" / "*.ndjson"
)
DEFAULT_ARTIFACT_ROOT = (
    ROOT
    / "logs"
    / "particle_research"
    / "real_shadow"
    / "rv600_forward_native_shadow_offline_v28_20260513T115640Z"
)
DEFAULT_SOURCE_ARTIFACT_ROOT = (
    ROOT / "logs" / "particle_research" / "real_shadow" / DEFAULT_DATASET
)
DEFAULT_SPOT_TICKS = DEFAULT_SOURCE_ARTIFACT_ROOT / "independent_spot_ticks.ndjson"
DEFAULT_OUTPUT = DEFAULT_ARTIFACT_ROOT / "offline_v28_contexts.ndjson"
DEFAULT_ISSUES = DEFAULT_ARTIFACT_ROOT / "offline_v28_context_issues.ndjson"
DEFAULT_SUMMARY_JSON = DEFAULT_ARTIFACT_ROOT / "offline_v28_context_summary.json"
DEFAULT_SUMMARY_MD = DEFAULT_ARTIFACT_ROOT / "offline_v28_context_summary.md"


SOURCE_NAME = "offline_v28_context_from_public_btc_replay"


@dataclass(frozen=True)
class MarketMeta:
    market_ticker: str
    strike: float
    settlement_ts_utc: datetime
    source: str


@dataclass(frozen=True)
class ContextBuildSummary:
    generated_utc: str
    schema_version: str
    checkpoint_path: str
    checkpoint_files: int
    checkpoint_rows_read: int
    spot_tick_path: str
    spot_ticks_read: int
    warmup_candle_rows: int
    warmup_end_utc: str
    contexts_written: int
    issue_count: int
    distinct_markets: int
    first_context_ts_utc: str
    last_context_ts_utc: str
    min_current_calibrated_p_yes: float | None
    max_current_calibrated_p_yes: float | None
    output: str
    issues: str
    modeling_choice: str
    research_only: bool = True


class ProbabilityReplayer(Protocol):
    warmup_rows: int
    warmup_end_utc: datetime

    def update_through(self, decision_ts: datetime) -> SpotTickRow | None:
        ...

    def predict_p_yes(self, *, strike: float, horizon_seconds: float) -> float:
        ...


class CausalV28Replayer:
    def __init__(
        self,
        *,
        btc_rows: Iterable[Mapping[str, Any]],
        spot_ticks: list[SpotTickRow],
        warmup_end_utc: datetime,
    ) -> None:
        self.engine = FastMushroomFVEngineV28()
        self.spot_ticks = spot_ticks
        self.tick_index = 0
        self.last_tick: SpotTickRow | None = None
        self.warmup_end_utc = warmup_end_utc
        self.warmup_rows = 0
        for row in btc_rows:
            self.engine.update_bar(
                open=float(row.get("open") or row.get("price")),
                high=float(row.get("high") or row.get("price")),
                low=float(row.get("low") or row.get("price")),
                close=float(row.get("close") or row.get("price")),
                volume=float(row.get("volume") or 0.0),
                ts=_parse_dt(row["ts_utc"]),
            )
            self.warmup_rows += 1
        if not self.engine.ready():
            raise RuntimeError(
                "v28 engine not ready after warmup: "
                f"warmup_rows={self.warmup_rows}; required={self.engine.config.min_bars}"
            )

    def update_through(self, decision_ts: datetime) -> SpotTickRow | None:
        while self.tick_index < len(self.spot_ticks):
            tick = self.spot_ticks[self.tick_index]
            if tick.available_ts_utc > decision_ts:
                break
            self.engine.update_tick(tick.price, tick.available_ts_utc, volume=0.0)
            self.last_tick = tick
            self.tick_index += 1
        return self.last_tick

    def predict_p_yes(self, *, strike: float, horizon_seconds: float) -> float:
        batch = self.engine.predict_many(
            strikes=[float(strike)],
            horizon_seconds=max(1.0, float(horizon_seconds)),
        )
        return float(batch.p_yes[0])


def build_offline_context_rows(
    *,
    checkpoints: Iterable[Mapping[str, Any]],
    market_meta: Mapping[str, MarketMeta],
    replayer: ProbabilityReplayer,
    max_spot_age_ms: float,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    contexts: list[dict[str, Any]] = []
    issues: list[dict[str, Any]] = []
    for row_number, checkpoint in enumerate(
        sorted(checkpoints, key=lambda row: _checkpoint_ts(row)),
        start=1,
    ):
        ticker = str(checkpoint.get("market_ticker") or "")
        try:
            if not ticker:
                raise ValueError("checkpoint missing market_ticker")
            if ticker not in market_meta:
                raise ValueError("missing market metadata")
            meta = market_meta[ticker]
            decision_ts = _checkpoint_ts(checkpoint)
            tick = replayer.update_through(decision_ts)
            if tick is None:
                raise ValueError("no independent spot tick at or before checkpoint")
            spot_age_ms = 1000.0 * (decision_ts - tick.available_ts_utc).total_seconds()
            if spot_age_ms < 0:
                raise ValueError("spot tick is after checkpoint")
            if spot_age_ms > max_spot_age_ms:
                raise ValueError(f"latest independent spot is too old: age_ms={spot_age_ms:.3f}")
            horizon_seconds = (meta.settlement_ts_utc - decision_ts).total_seconds()
            if horizon_seconds <= 0:
                raise ValueError("checkpoint is not before settlement")
            p_yes = replayer.predict_p_yes(
                strike=meta.strike,
                horizon_seconds=horizon_seconds,
            )
            contexts.append(
                {
                    "schema_version": "rv600-offline-v28-context-v1",
                    "market_ticker": ticker,
                    "context_ts_utc": decision_ts.isoformat(),
                    "strike": meta.strike,
                    "settlement_ts_utc": meta.settlement_ts_utc.isoformat(),
                    "spot": tick.price,
                    "spot_ts_utc": tick.available_ts_utc.isoformat(),
                    "current_calibrated_p_yes": max(0.0, min(1.0, p_yes)),
                    "position_size": 1,
                    "source": SOURCE_NAME,
                    "market_metadata_source": meta.source,
                    "source_quality_tier": "native_continuous_offline_v28_control",
                    "causal_replay": True,
                    "spot_age_ms": spot_age_ms,
                    "warmup_candle_rows": int(replayer.warmup_rows),
                    "warmup_end_utc": replayer.warmup_end_utc.isoformat(),
                    "checkpoint_source": checkpoint.get("source"),
                    "checkpoint_run_id": checkpoint.get("run_id"),
                    "checkpoint_sequence_number": checkpoint.get("sequence_number"),
                }
            )
        except Exception as exc:
            issues.append(
                {
                    "row_number": row_number,
                    "market_ticker": ticker,
                    "reason": str(exc),
                }
            )
    return contexts, issues


def run(args: argparse.Namespace) -> ContextBuildSummary:
    checkpoints = load_checkpoints(args.checkpoints)
    requested_markets = {str(ticker).strip() for ticker in (args.market_ticker or []) if str(ticker).strip()}
    if requested_markets:
        checkpoints = [
            row
            for row in checkpoints
            if str(row.get("market_ticker") or "") in requested_markets
        ]
    if not checkpoints:
        raise RuntimeError(f"no checkpoint rows found: {args.checkpoints}")
    spot_ticks = load_spot_ticks(args.spot_ticks)
    if not spot_ticks:
        raise RuntimeError(f"no spot ticks found: {args.spot_ticks}")
    first_checkpoint_ts = min(_checkpoint_ts(row) for row in checkpoints)
    warmup_end_utc = _floor_minute(first_checkpoint_ts)
    candles = fetch_coinbase_candles(
        coinbase_base_url=args.coinbase_base_url,
        now_utc=warmup_end_utc,
        minutes=args.warmup_minutes,
        timeout_seconds=args.timeout_seconds,
    )
    btc_rows = [
        row
        for row in btc_rows_from_candles(candles)
        if _parse_dt(row["ts_utc"]) < warmup_end_utc
    ]
    market_meta = fetch_market_meta(
        sorted({str(row.get("market_ticker") or "") for row in checkpoints if row.get("market_ticker")}),
        base_url=args.kalshi_base_url,
    )
    replayer = CausalV28Replayer(
        btc_rows=btc_rows,
        spot_ticks=spot_ticks,
        warmup_end_utc=warmup_end_utc,
    )
    contexts, issues = build_offline_context_rows(
        checkpoints=checkpoints,
        market_meta=market_meta,
        replayer=replayer,
        max_spot_age_ms=args.max_spot_age_ms,
    )
    write_jsonl(args.output, contexts)
    write_jsonl(args.issues, issues)
    p_values = [float(row["current_calibrated_p_yes"]) for row in contexts]
    timestamps = [_parse_dt(row["context_ts_utc"]) for row in contexts]
    summary = ContextBuildSummary(
        generated_utc=datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        schema_version="rv600-offline-v28-context-summary-v1",
        checkpoint_path=str(args.checkpoints),
        checkpoint_files=len(checkpoint_files(args.checkpoints)),
        checkpoint_rows_read=len(checkpoints),
        spot_tick_path=str(args.spot_ticks),
        spot_ticks_read=len(spot_ticks),
        warmup_candle_rows=len(btc_rows),
        warmup_end_utc=warmup_end_utc.isoformat(),
        contexts_written=len(contexts),
        issue_count=len(issues),
        distinct_markets=len({row["market_ticker"] for row in contexts}),
        first_context_ts_utc=min(timestamps).isoformat() if timestamps else "",
        last_context_ts_utc=max(timestamps).isoformat() if timestamps else "",
        min_current_calibrated_p_yes=min(p_values) if p_values else None,
        max_current_calibrated_p_yes=max(p_values) if p_values else None,
        output=str(args.output),
        issues=str(args.issues),
        modeling_choice=(
            "Causal offline v28 event replay from public Coinbase candles and "
            "native independent spot ticks; no live bot state, orders, or restarts."
        ),
    )
    write_summary(summary, args.summary_json, args.summary_md)
    return summary


def load_checkpoints(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for file_path in checkpoint_files(path):
        with file_path.open("r", encoding="utf-8", errors="replace") as handle:
            for line in handle:
                line = line.strip()
                if not line:
                    continue
                payload = json.loads(line)
                if isinstance(payload, dict):
                    rows.append(payload)
    return rows


def checkpoint_files(path: Path) -> list[Path]:
    path_text = str(path)
    if any(marker in path_text for marker in ("*", "?", "[")):
        matches = [Path(match) for match in glob.glob(path_text, recursive=True)]
        return sorted(match for match in matches if match.is_file())
    return [path] if path.is_file() else []


def fetch_market_meta(tickers: list[str], *, base_url: str) -> dict[str, MarketMeta]:
    metas: dict[str, MarketMeta] = {}
    for ticker in tickers:
        payload = dict(fetch_market_payload(ticker, base_url=base_url))
        strike = parse_btc_strike(payload)
        close_ts = parse_ts(market_close_ts(payload))
        if strike is None or close_ts is None:
            raise RuntimeError(f"missing strike or close time for {ticker}")
        metas[ticker] = MarketMeta(
            market_ticker=ticker,
            strike=float(strike),
            settlement_ts_utc=close_ts,
            source=str(payload.get("_result_source") or "kalshi_public_market"),
        )
    return metas


def write_jsonl(path: Path, rows: Iterable[Mapping[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        for row in rows:
            handle.write(json.dumps(row, sort_keys=True) + "\n")


def write_summary(summary: ContextBuildSummary, output_json: Path, output_md: Path) -> None:
    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_json.write_text(
        json.dumps(asdict(summary), indent=2, sort_keys=True),
        encoding="utf-8",
    )
    output_md.write_text(_summary_markdown(summary), encoding="utf-8")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Build research-only native RV600 passive-checkpoint contexts by replaying "
            "the v28 fair-value engine from public BTC data without touching the live bot."
        )
    )
    parser.add_argument("--checkpoints", type=Path, default=DEFAULT_CHECKPOINTS)
    parser.add_argument("--spot-ticks", type=Path, default=DEFAULT_SPOT_TICKS)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--issues", type=Path, default=DEFAULT_ISSUES)
    parser.add_argument("--summary-json", type=Path, default=DEFAULT_SUMMARY_JSON)
    parser.add_argument("--summary-md", type=Path, default=DEFAULT_SUMMARY_MD)
    parser.add_argument("--coinbase-base-url", default=DEFAULT_COINBASE_BASE_URL)
    parser.add_argument("--kalshi-base-url", default=PROD_BASE_URL)
    parser.add_argument("--warmup-minutes", default=240, type=int)
    parser.add_argument("--max-spot-age-ms", default=5000.0, type=float)
    parser.add_argument("--timeout-seconds", default=20.0, type=float)
    parser.add_argument(
        "--market-ticker",
        action="append",
        default=[],
        help="Optional market ticker filter; repeat to include multiple resolved markets.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    summary = run(args)
    print(f"contexts_written={summary.contexts_written}")
    print(f"issue_count={summary.issue_count}")
    print(f"distinct_markets={summary.distinct_markets}")
    print(f"output={summary.output}")
    print(f"issues={summary.issues}")
    print(f"summary_json={args.summary_json}")
    print(f"summary_md={args.summary_md}")
    return 0


def _checkpoint_ts(row: Mapping[str, Any]) -> datetime:
    for key in ("checkpoint_ts", "ts_wall", "local_recv_ts"):
        if row.get(key) not in (None, ""):
            return _parse_dt(row[key])
    raise ValueError("checkpoint missing checkpoint_ts")


def _parse_dt(value: Any) -> datetime:
    if isinstance(value, datetime):
        parsed = value
    else:
        parsed = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def _floor_minute(value: datetime) -> datetime:
    return _parse_dt(value).replace(second=0, microsecond=0)


def _summary_markdown(summary: ContextBuildSummary) -> str:
    lines = [
        "# RV600 Native Offline V28 Context Replay",
        "",
        f"- generated_utc: {summary.generated_utc}",
        f"- research_only: {summary.research_only}",
        f"- contexts_written: {summary.contexts_written}",
        f"- issue_count: {summary.issue_count}",
        f"- distinct_markets: {summary.distinct_markets}",
        f"- checkpoint_rows_read: {summary.checkpoint_rows_read}",
        f"- spot_ticks_read: {summary.spot_ticks_read}",
        f"- warmup_candle_rows: {summary.warmup_candle_rows}",
        f"- warmup_end_utc: {summary.warmup_end_utc}",
        f"- first_context_ts_utc: {summary.first_context_ts_utc}",
        f"- last_context_ts_utc: {summary.last_context_ts_utc}",
        f"- min_current_calibrated_p_yes: {summary.min_current_calibrated_p_yes}",
        f"- max_current_calibrated_p_yes: {summary.max_current_calibrated_p_yes}",
        f"- output: `{summary.output}`",
        f"- issues: `{summary.issues}`",
        "",
        "## Modeling Choice",
        "",
        summary.modeling_choice,
        "",
    ]
    return "\n".join(lines)


if __name__ == "__main__":
    raise SystemExit(main())
