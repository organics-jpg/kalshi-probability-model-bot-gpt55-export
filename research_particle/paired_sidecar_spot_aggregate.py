from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

from .paired_sidecar_spot_diagnostic import MODEL_FIELDS, _model_summaries


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INPUT_ROOT = ROOT / "logs" / "particle_research" / "real_shadow" / "sidecar_spot_pairs"
DEFAULT_OUTPUT_JSON = ROOT / "logs" / "particle_research" / "reports" / "paired_sidecar_spot_aggregate_latest.json"
DEFAULT_OUTPUT_MD = ROOT / "logs" / "particle_research" / "reports" / "paired_sidecar_spot_aggregate_latest.md"


@dataclass(frozen=True)
class PairedSidecarSpotAggregateSummary:
    schema_version: str
    generated_utc: str
    promotion_allowed: bool
    promotion_status: Mapping[str, Any]
    input_root: str
    output_json: str
    output_md: str
    diagnostic_file_count: int
    skipped_diagnostic_count: int
    ready_diagnostic_count: int
    joined_rows: int
    joined_markets: int
    issue_count: int
    diagnostic_ready: bool
    candidate_ready_for_predeclared_shadow: bool
    min_rows_for_shadow: int
    min_markets_for_shadow: int
    rows_remaining_for_shadow: int
    markets_remaining_for_shadow: int
    best_model_by_brier: str
    best_model_by_logloss: str
    best_model_by_pnl: str
    market_equal_best_model_by_brier: str
    market_equal_best_model_by_logloss: str
    tick_brownian_delta_brier_vs_candle: float | None
    tick_brownian_delta_logloss_vs_candle: float | None
    market_equal_tick_brownian_delta_brier_vs_candle: float | None
    market_equal_tick_brownian_delta_logloss_vs_candle: float | None
    tick_brownian_better_brier_capture_count: int
    tick_brownian_better_logloss_capture_count: int


def build_paired_sidecar_spot_aggregate(
    *,
    input_root: Path = DEFAULT_INPUT_ROOT,
    output_json: Path = DEFAULT_OUTPUT_JSON,
    output_md: Path = DEFAULT_OUTPUT_MD,
    min_rows_for_shadow: int = 200,
    min_markets_for_shadow: int = 40,
) -> tuple[PairedSidecarSpotAggregateSummary, list[dict[str, Any]], list[dict[str, Any]]]:
    diagnostic_files = sorted(input_root.glob("*/sidecar_spot_tick_vs_candle_diagnostic.json"))
    ready_count = 0
    skipped_count = 0
    issue_count = 0
    diagnostic_rows: list[dict[str, Any]] = []
    better_brier_count = 0
    better_logloss_count = 0
    for path in diagnostic_files:
        manifest_issue = _diagnostic_manifest_issue(path)
        if manifest_issue:
            skipped_count += 1
            issue_count += 1
            continue
        payload = _load_json(path)
        summary = _summary_from_payload(payload)
        if bool(summary.get("diagnostic_ready")):
            ready_count += 1
        issue_count += int(summary.get("issue_count", 0) or 0)
        if _is_negative(summary.get("tick_brownian_delta_brier_vs_candle")):
            better_brier_count += 1
        if _is_negative(summary.get("tick_brownian_delta_logloss_vs_candle")):
            better_logloss_count += 1
        for row in payload.get("diagnostic_rows") or []:
            if isinstance(row, dict):
                enriched = dict(row)
                enriched["source_diagnostic_json"] = str(path)
                enriched["source_capture_id"] = path.parent.name
                diagnostic_rows.append(enriched)

    model_rows = _model_summaries(diagnostic_rows)
    market_equal_model_rows = _market_equal_model_summaries(diagnostic_rows)
    by_model = {row["model"]: row for row in model_rows}
    by_market_equal_model = {row["model"]: row for row in market_equal_model_rows}
    best_brier = min(model_rows, key=lambda row: float(row["brier"]), default={})
    best_logloss = min(model_rows, key=lambda row: float(row["logloss"]), default={})
    best_pnl = max(model_rows, key=lambda row: float(row["top_ev_bucket_pnl_cents"]), default={})
    market_equal_best_brier = min(market_equal_model_rows, key=lambda row: float(row["brier"]), default={})
    market_equal_best_logloss = min(market_equal_model_rows, key=lambda row: float(row["logloss"]), default={})
    candle = by_model.get("candle_brownian")
    tick = by_model.get("tick_brownian")
    market_equal_candle = by_market_equal_model.get("candle_brownian")
    market_equal_tick = by_market_equal_model.get("tick_brownian")
    joined_markets = len({str(row.get("market_ticker") or "") for row in diagnostic_rows if row.get("market_ticker")})
    rows_remaining = max(0, int(min_rows_for_shadow) - len(diagnostic_rows))
    markets_remaining = max(0, int(min_markets_for_shadow) - joined_markets)
    summary = PairedSidecarSpotAggregateSummary(
        schema_version="paired-sidecar-spot-aggregate-v1",
        generated_utc=datetime.now(timezone.utc).isoformat(),
        promotion_allowed=False,
        promotion_status={
            "allowed": False,
            "reason": "aggregate paired sidecar spot diagnostic is research-only evidence; promotion requires predeclared locked OOS probability, EV-rank, and PnL gates",
        },
        input_root=str(input_root),
        output_json=str(output_json),
        output_md=str(output_md),
        diagnostic_file_count=len(diagnostic_files),
        skipped_diagnostic_count=skipped_count,
        ready_diagnostic_count=ready_count,
        joined_rows=len(diagnostic_rows),
        joined_markets=joined_markets,
        issue_count=issue_count,
        diagnostic_ready=bool(diagnostic_rows),
        candidate_ready_for_predeclared_shadow=(
            len(diagnostic_rows) >= min_rows_for_shadow and joined_markets >= min_markets_for_shadow
        ),
        min_rows_for_shadow=min_rows_for_shadow,
        min_markets_for_shadow=min_markets_for_shadow,
        rows_remaining_for_shadow=rows_remaining,
        markets_remaining_for_shadow=markets_remaining,
        best_model_by_brier=str(best_brier.get("model", "")),
        best_model_by_logloss=str(best_logloss.get("model", "")),
        best_model_by_pnl=str(best_pnl.get("model", "")),
        market_equal_best_model_by_brier=str(market_equal_best_brier.get("model", "")),
        market_equal_best_model_by_logloss=str(market_equal_best_logloss.get("model", "")),
        tick_brownian_delta_brier_vs_candle=(
            float(tick["brier"]) - float(candle["brier"])
            if tick and candle
            else None
        ),
        tick_brownian_delta_logloss_vs_candle=(
            float(tick["logloss"]) - float(candle["logloss"])
            if tick and candle
            else None
        ),
        market_equal_tick_brownian_delta_brier_vs_candle=(
            float(market_equal_tick["brier"]) - float(market_equal_candle["brier"])
            if market_equal_tick and market_equal_candle
            else None
        ),
        market_equal_tick_brownian_delta_logloss_vs_candle=(
            float(market_equal_tick["logloss"]) - float(market_equal_candle["logloss"])
            if market_equal_tick and market_equal_candle
            else None
        ),
        tick_brownian_better_brier_capture_count=better_brier_count,
        tick_brownian_better_logloss_capture_count=better_logloss_count,
    )
    return summary, model_rows, diagnostic_rows


def write_paired_sidecar_spot_aggregate(
    summary: PairedSidecarSpotAggregateSummary,
    model_rows: list[dict[str, Any]],
    diagnostic_rows: list[dict[str, Any]],
) -> None:
    output_json = Path(summary.output_json)
    output_md = Path(summary.output_md)
    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_md.parent.mkdir(parents=True, exist_ok=True)
    market_equal_model_rows = _market_equal_model_summaries(diagnostic_rows)
    output_json.write_text(
        json.dumps(
            {
                "summary": asdict(summary),
                "model_rows": model_rows,
                "market_equal_model_rows": market_equal_model_rows,
                "diagnostic_rows": diagnostic_rows,
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    output_md.write_text(_markdown(summary, model_rows), encoding="utf-8")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Aggregate paired sidecar no-future spot tick diagnostics across live-shadow captures."
    )
    parser.add_argument("--input-root", type=Path, default=DEFAULT_INPUT_ROOT)
    parser.add_argument("--output-json", type=Path, default=DEFAULT_OUTPUT_JSON)
    parser.add_argument("--output-md", type=Path, default=DEFAULT_OUTPUT_MD)
    parser.add_argument("--min-rows-for-shadow", type=int, default=200)
    parser.add_argument("--min-markets-for-shadow", type=int, default=40)
    parser.add_argument("--write", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    summary, model_rows, diagnostic_rows = build_paired_sidecar_spot_aggregate(
        input_root=args.input_root,
        output_json=args.output_json,
        output_md=args.output_md,
        min_rows_for_shadow=args.min_rows_for_shadow,
        min_markets_for_shadow=args.min_markets_for_shadow,
    )
    if args.write:
        write_paired_sidecar_spot_aggregate(summary, model_rows, diagnostic_rows)
    print(f"diagnostic_ready={summary.diagnostic_ready}")
    print(f"candidate_ready_for_predeclared_shadow={summary.candidate_ready_for_predeclared_shadow}")
    print(f"diagnostic_file_count={summary.diagnostic_file_count}")
    print(f"skipped_diagnostic_count={summary.skipped_diagnostic_count}")
    print(f"ready_diagnostic_count={summary.ready_diagnostic_count}")
    print(f"joined_rows={summary.joined_rows}")
    print(f"joined_markets={summary.joined_markets}")
    print(f"best_model_by_brier={summary.best_model_by_brier}")
    print(f"best_model_by_logloss={summary.best_model_by_logloss}")
    print(f"market_equal_best_model_by_brier={summary.market_equal_best_model_by_brier}")
    print(f"market_equal_best_model_by_logloss={summary.market_equal_best_model_by_logloss}")
    print(f"promotion_allowed={summary.promotion_allowed}")
    print(f"output_json={summary.output_json}")
    return 0


def _load_json(path: Path) -> dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def _summary_from_payload(payload: dict[str, Any]) -> dict[str, Any]:
    summary = payload.get("summary")
    return summary if isinstance(summary, dict) else payload


def _diagnostic_manifest_issue(diagnostic_path: Path) -> str:
    manifest_path = diagnostic_path.parent / "paired_sidecar_spot_manifest.json"
    manifest_payload = _load_json(manifest_path)
    if not manifest_payload:
        return "missing_paired_manifest"
    summary = _summary_from_payload(manifest_payload)
    if not bool(summary.get("paired_capture_ready")):
        return "paired_capture_not_ready"
    consistency_issue = _paired_manifest_consistency_issue(manifest_payload)
    if consistency_issue:
        return consistency_issue
    return ""


def _paired_manifest_consistency_issue(payload: Mapping[str, Any]) -> str:
    summary = _summary_from_payload(dict(payload))
    collect_mode = str(summary.get("collect_mode") or "").replace("-", "_")
    batch_summary = payload.get("sidecar_batch_summary")
    batch_summary = batch_summary if isinstance(batch_summary, Mapping) else {}
    batch_mode = str(batch_summary.get("mode") or "").replace("-", "_")
    if collect_mode and collect_mode != "none" and batch_mode and batch_mode != collect_mode:
        return "sidecar_batch_mode_mismatch"

    market_close_by_ticker: dict[str, datetime] = {}
    batch_markets = payload.get("sidecar_batch_markets")
    if isinstance(batch_markets, list):
        for market in batch_markets:
            if not isinstance(market, Mapping):
                continue
            ticker = str(market.get("market_ticker") or "")
            close_ts = _parse_dt(market.get("market_close_ts_utc"))
            if ticker and close_ts is not None:
                market_close_by_ticker[ticker] = close_ts

    alignment_rows = payload.get("alignment_rows")
    if isinstance(alignment_rows, list):
        for row in alignment_rows:
            if not isinstance(row, Mapping):
                continue
            ticker = str(row.get("market_ticker") or "")
            decision_ts = _parse_dt(row.get("decision_ts_utc"))
            close_ts = market_close_by_ticker.get(ticker)
            if decision_ts is not None and close_ts is not None and close_ts <= decision_ts:
                return "sidecar_market_not_preclose_at_decision"
    return ""


def _parse_dt(value: Any) -> datetime | None:
    text = str(value or "").strip()
    if not text:
        return None
    try:
        parsed = datetime.fromisoformat(text.replace("Z", "+00:00"))
    except ValueError:
        return None
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def _market_equal_model_summaries(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    by_market: dict[str, list[dict[str, Any]]] = {}
    for row in rows:
        market = str(row.get("market_ticker") or "")
        if market:
            by_market.setdefault(market, []).append(row)
    if not by_market:
        return _model_summaries([])

    per_market_by_model: list[dict[str, dict[str, Any]]] = []
    for market_rows in by_market.values():
        per_market_by_model.append({row["model"]: row for row in _model_summaries(market_rows)})

    summaries: list[dict[str, Any]] = []
    for model in MODEL_FIELDS:
        model_summaries = [item[model] for item in per_market_by_model if model in item]
        summaries.append(
            {
                "model": model,
                "rows": sum(int(item.get("rows", 0) or 0) for item in model_summaries),
                "markets": len(model_summaries),
                "brier": _mean(float(item.get("brier", 0.0) or 0.0) for item in model_summaries),
                "logloss": _mean(float(item.get("logloss", 0.0) or 0.0) for item in model_summaries),
                "mean_side_ev_cents": _mean(
                    float(item.get("mean_side_ev_cents", 0.0) or 0.0) for item in model_summaries
                ),
                "selected_count": sum(int(item.get("selected_count", 0) or 0) for item in model_summaries),
                "selected_pnl_cents": _mean(
                    float(item.get("selected_pnl_cents", 0.0) or 0.0) for item in model_summaries
                ),
                "top_ev_bucket_count": sum(int(item.get("top_ev_bucket_count", 0) or 0) for item in model_summaries),
                "top_ev_bucket_pnl_cents": _mean(
                    float(item.get("top_ev_bucket_pnl_cents", 0.0) or 0.0) for item in model_summaries
                ),
                "promotion_safe": False,
            }
        )
    return summaries


def _mean(values: Any) -> float:
    seq = list(values)
    return sum(seq) / len(seq) if seq else 0.0


def _is_negative(value: Any) -> bool:
    try:
        return float(value) < 0.0
    except (TypeError, ValueError):
        return False


def _markdown(summary: PairedSidecarSpotAggregateSummary, model_rows: list[dict[str, Any]]) -> str:
    lines = [
        "# Paired Sidecar Spot Aggregate Diagnostic",
        "",
        "Research-only aggregate across paired live sidecar/independent-spot diagnostics.",
        "",
        "## Summary",
        "",
        f"- Generated UTC: `{summary.generated_utc}`",
        f"- Promotion allowed: `{summary.promotion_allowed}`",
        f"- Diagnostic ready: `{summary.diagnostic_ready}`",
        f"- Candidate ready for predeclared shadow: `{summary.candidate_ready_for_predeclared_shadow}`",
        f"- Diagnostic files ready / skipped / total: `{summary.ready_diagnostic_count}` / `{summary.skipped_diagnostic_count}` / `{summary.diagnostic_file_count}`",
        f"- Joined rows / markets: `{summary.joined_rows}` / `{summary.joined_markets}`",
        f"- Rows / markets remaining for predeclared shadow floor: `{summary.rows_remaining_for_shadow}` / `{summary.markets_remaining_for_shadow}`",
        f"- Issue count: `{summary.issue_count}`",
        f"- Best model by Brier: `{summary.best_model_by_brier}`",
        f"- Best model by log loss: `{summary.best_model_by_logloss}`",
        f"- Market-equal best model by Brier: `{summary.market_equal_best_model_by_brier}`",
        f"- Market-equal best model by log loss: `{summary.market_equal_best_model_by_logloss}`",
        f"- Tick Brownian delta Brier vs candle: `{summary.tick_brownian_delta_brier_vs_candle}`",
        f"- Tick Brownian delta log loss vs candle: `{summary.tick_brownian_delta_logloss_vs_candle}`",
        f"- Market-equal tick Brownian delta Brier vs candle: `{summary.market_equal_tick_brownian_delta_brier_vs_candle}`",
        f"- Market-equal tick Brownian delta log loss vs candle: `{summary.market_equal_tick_brownian_delta_logloss_vs_candle}`",
        f"- Tick Brownian better capture counts: Brier `{summary.tick_brownian_better_brier_capture_count}`, log loss `{summary.tick_brownian_better_logloss_capture_count}`",
        "",
        "## Model Rows",
        "",
        "| model | rows | markets | brier | logloss | selected | selected pnl | top bucket pnl |",
        "|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for row in model_rows:
        lines.append(
            f"| `{row['model']}` | {row['rows']} | {row['markets']} | {row['brier']} | "
            f"{row['logloss']} | {row['selected_count']} | {row['selected_pnl_cents']} | "
            f"{row['top_ev_bucket_pnl_cents']} |"
        )
    lines.extend(
        [
            "",
            "## Read",
            "",
            "- This aggregates instrumentation diagnostics only; it is not a promotion artifact.",
            "- The candidate-ready flag is a coverage floor for future predeclared shadow tests, not live-trading approval.",
        ]
    )
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    raise SystemExit(main())
