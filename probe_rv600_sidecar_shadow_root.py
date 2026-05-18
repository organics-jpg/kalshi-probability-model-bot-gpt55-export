from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

from research_particle.kalshi_market_results import fetch_market_payload, market_result_row_from_market


DEFAULT_INPUT_ROOT = Path("logs/particle_research/real_shadow/sidecar_spot_pairs")
DEFAULT_OUTPUT_ROOT = Path("logs/particle_research/real_shadow/rv600_sidecar_spot_pairs_forward")
DEFAULT_MIN_DECISION_TS_UTC = "2026-05-13T05:37:07+00:00"


@dataclass(frozen=True)
class SidecarShadowBuildSummary:
    generated_utc: str
    input_root: str
    output_root: str
    min_decision_ts_utc: str
    diagnostic_files: int
    enriched_files: int
    candidate_rows_written: int
    label_rows_written: int
    distinct_markets: int
    duplicate_snapshot_rows_skipped: int
    pre_min_decision_rows_skipped: int
    missing_label_rows_skipped: int
    independent_spot_rows_skipped: int
    malformed_rows_skipped: int
    fetched_label_rows: int
    candidate_snapshot_path: str
    label_context_path: str
    output_json: str
    output_md: str


def build_sidecar_shadow_root(
    *,
    input_root: Path = DEFAULT_INPUT_ROOT,
    output_root: Path = DEFAULT_OUTPUT_ROOT,
    min_decision_ts_utc: datetime | None,
    require_independent_spot: bool = True,
    fetch_missing_labels: bool = False,
    fee_cents: float = 2.0,
) -> tuple[SidecarShadowBuildSummary, list[dict[str, Any]], list[dict[str, Any]]]:
    label_by_key = _load_sidecar_labels(input_root)
    fetched_labels_by_market: dict[str, dict[str, Any] | None] = {}
    candidate_rows: list[dict[str, Any]] = []
    labels_by_market: dict[str, dict[str, Any]] = {}
    seen_snapshots: set[tuple[str, str]] = set()
    diagnostic_files = len(list(input_root.glob("*/sidecar_spot_tick_vs_candle_diagnostic.json")))
    enriched_files = 0
    duplicate_snapshot_rows_skipped = 0
    pre_min_decision_rows_skipped = 0
    missing_label_rows_skipped = 0
    independent_spot_rows_skipped = 0
    malformed_rows_skipped = 0
    fetched_label_rows = 0

    for enriched_path in sorted(input_root.glob("*/sidecar_packets_independent_spot_enriched.json")):
        enriched_files += 1
        try:
            rows = _load_enriched_rows(enriched_path)
        except Exception:
            malformed_rows_skipped += 1
            continue
        for row in rows:
            try:
                market = str(row.get("market_ticker") or "")
                decision_ts = _parse_dt_required(row.get("decision_ts_utc"), "decision_ts_utc")
                decision_key = _dt_key(decision_ts)
                if not market:
                    raise ValueError("missing market_ticker")
                if min_decision_ts_utc is not None and decision_ts < min_decision_ts_utc:
                    pre_min_decision_rows_skipped += 1
                    continue
                snapshot_key = (market, decision_key)
                if snapshot_key in seen_snapshots:
                    duplicate_snapshot_rows_skipped += 1
                    continue
                if require_independent_spot and not _truthy(row.get("independent_spot_ready")):
                    independent_spot_rows_skipped += 1
                    continue
                label = label_by_key.get(snapshot_key)
                if label is None and fetch_missing_labels:
                    label = _fetch_public_label_for_row(
                        row,
                        fetched_labels_by_market=fetched_labels_by_market,
                    )
                    if label is not None:
                        fetched_label_rows += 1
                if label is None:
                    missing_label_rows_skipped += 1
                    continue
                candidate = _candidate_payload(row, decision_ts=decision_ts, fee_cents=fee_cents)
                label_payload = _label_payload(row, label)
                candidate_rows.append(candidate)
                labels_by_market[market] = label_payload
                seen_snapshots.add(snapshot_key)
            except Exception:
                malformed_rows_skipped += 1

    candidate_path = output_root / "candidate_snapshots" / "candidate_snapshots.ndjson"
    label_path = output_root / "pipeline_work" / "label_contexts_full_refresh.ndjson"
    output_json = output_root / "rv600_sidecar_shadow_root_summary.json"
    output_md = output_root / "rv600_sidecar_shadow_root_summary.md"
    summary = SidecarShadowBuildSummary(
        generated_utc=_utc_now(),
        input_root=str(input_root),
        output_root=str(output_root),
        min_decision_ts_utc="" if min_decision_ts_utc is None else min_decision_ts_utc.isoformat(),
        diagnostic_files=diagnostic_files,
        enriched_files=enriched_files,
        candidate_rows_written=len(candidate_rows),
        label_rows_written=len(labels_by_market),
        distinct_markets=len(labels_by_market),
        duplicate_snapshot_rows_skipped=duplicate_snapshot_rows_skipped,
        pre_min_decision_rows_skipped=pre_min_decision_rows_skipped,
        missing_label_rows_skipped=missing_label_rows_skipped,
        independent_spot_rows_skipped=independent_spot_rows_skipped,
        malformed_rows_skipped=malformed_rows_skipped,
        fetched_label_rows=fetched_label_rows,
        candidate_snapshot_path=str(candidate_path),
        label_context_path=str(label_path),
        output_json=str(output_json),
        output_md=str(output_md),
    )
    return summary, candidate_rows, list(labels_by_market.values())


def write_sidecar_shadow_root(
    summary: SidecarShadowBuildSummary,
    candidate_rows: list[dict[str, Any]],
    label_rows: list[dict[str, Any]],
) -> None:
    candidate_path = Path(summary.candidate_snapshot_path)
    label_path = Path(summary.label_context_path)
    output_json = Path(summary.output_json)
    output_md = Path(summary.output_md)
    for path in (candidate_path, label_path, output_json, output_md):
        path.parent.mkdir(parents=True, exist_ok=True)
    _write_jsonl(candidate_path, candidate_rows)
    _write_jsonl(label_path, label_rows)
    output_json.write_text(
        json.dumps(
            {
                "summary": asdict(summary),
                "candidate_rows": candidate_rows,
                "label_rows": label_rows,
            },
            indent=2,
            sort_keys=True,
        ),
        encoding="utf-8",
    )
    output_md.write_text(_markdown(summary), encoding="utf-8")


def _load_sidecar_labels(input_root: Path) -> dict[tuple[str, str], dict[str, Any]]:
    labels: dict[tuple[str, str], dict[str, Any]] = {}
    for diagnostic_path in sorted(input_root.glob("*/sidecar_spot_tick_vs_candle_diagnostic.json")):
        try:
            payload = json.loads(diagnostic_path.read_text(encoding="utf-8"))
        except Exception:
            continue
        for row in payload.get("diagnostic_rows") or []:
            if not isinstance(row, Mapping):
                continue
            market = str(row.get("market_ticker") or "")
            decision_raw = row.get("decision_ts_utc")
            if not market or not decision_raw:
                continue
            try:
                decision_key = _dt_key(_parse_dt_required(decision_raw, "decision_ts_utc"))
            except Exception:
                continue
            labels.setdefault(
                (market, decision_key),
                {
                    "market_ticker": market,
                    "decision_ts_utc": decision_key,
                    "y_yes_win": _truthy(row.get("y_yes_win")),
                    "source_diagnostic": str(diagnostic_path),
                },
            )
    return labels


def _load_enriched_rows(path: Path) -> list[Mapping[str, Any]]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    rows = payload.get("rows") if isinstance(payload, Mapping) else payload
    if not isinstance(rows, list):
        raise ValueError(f"rows list expected in {path}")
    return [row for row in rows if isinstance(row, Mapping)]


def _fetch_public_label_for_row(
    row: Mapping[str, Any],
    *,
    fetched_labels_by_market: dict[str, dict[str, Any] | None],
) -> dict[str, Any] | None:
    market = str(row.get("market_ticker") or "")
    if not market:
        return None
    if market not in fetched_labels_by_market:
        try:
            market_payload = fetch_market_payload(market)
            result_row = market_result_row_from_market(market_payload)
        except Exception:
            result_row = None
        fetched_labels_by_market[market] = (
            None
            if result_row is None
            else {
                "market_ticker": market,
                "y_yes_win": str(result_row.get("result") or "").lower() == "yes",
                "source_diagnostic": "kalshi_public_market_result",
            }
        )
    return fetched_labels_by_market[market]


def _candidate_payload(row: Mapping[str, Any], *, decision_ts: datetime, fee_cents: float) -> dict[str, Any]:
    market = str(row["market_ticker"])
    yes_ask = _required_float(row.get("yes_ask_cents"), "yes_ask_cents")
    no_ask = _required_float(row.get("no_ask_cents"), "no_ask_cents")
    spot = _optional_float(row.get("independent_spot_price"))
    if spot is None:
        spot = _required_float(row.get("btc_spot"), "btc_spot")
    book_mid = _optional_float(row.get("book_mid_yes_cents"))
    if book_mid is None:
        book_mid = (yes_ask + (100.0 - no_ask)) / 2.0
    current_p_yes = _required_probability(row.get("v28_p_yes"), "v28_p_yes")
    particle_p_yes = _optional_probability(row.get("candidate_p_yes"))
    if particle_p_yes is None:
        particle_p_yes = current_p_yes
    tick_brownian = _optional_probability(row.get("tick_brownian_p_yes"))
    if tick_brownian is None:
        tick_brownian = _optional_probability(row.get("candle_brownian_p_yes"))
    if tick_brownian is None:
        tick_brownian = current_p_yes
    return {
        "schema_version": 1,
        "record_type": "candidate_snapshot",
        "recorded_ts_utc": _utc_now(),
        "decision_shadow": "rv600_sidecar_spot_pair",
        "reason": "rv600_sidecar_shadow_root",
        "snapshot": {
            "market_ticker": market,
            "decision_ts_utc": decision_ts.isoformat(),
            "recv_ts_utc": decision_ts.isoformat(),
            "strike": _required_float(row.get("strike"), "strike"),
            "spot": spot,
            "yes_ask_cents": yes_ask,
            "no_ask_cents": no_ask,
            "fee_cents": float(fee_cents),
            "fill_prob": 1.0,
            "yes_fill_prob": 1.0,
            "no_fill_prob": 1.0,
        },
        "extra": {
            "particle_p_yes": particle_p_yes,
            "brownian_p_yes": tick_brownian,
            "market_p_yes": max(0.0, min(1.0, book_mid / 100.0)),
            "current_calibrated_p_yes": current_p_yes,
            "current_calibrated_p_yes_source": "sidecar_v28_p_yes",
            "seconds_to_close": _optional_float(row.get("seconds_to_close")),
            "independent_spot_age_ms": _optional_float(row.get("independent_spot_age_ms")),
            "source_quality_tier": row.get("source_quality_tier"),
            "sidecar_spot_pair_run_id": row.get("sidecar_spot_pair_run_id"),
            "source_file": row.get("source_file"),
            "dedupe_key": f"{market}|{decision_ts.isoformat()}",
        },
    }


def _label_payload(row: Mapping[str, Any], label: Mapping[str, Any]) -> dict[str, Any]:
    market = str(row["market_ticker"])
    strike = _required_float(row.get("strike"), "strike")
    close_ts = _parse_dt_required(row.get("market_close_ts_utc"), "market_close_ts_utc")
    yes_win = bool(label["y_yes_win"])
    return {
        "market_ticker": market,
        "settlement_ts_utc": close_ts.isoformat(),
        "label_available_ts_utc": close_ts.isoformat(),
        "settlement_price": strike + 1.0 if yes_win else strike - 1.0,
        "strike": strike,
        "binary_result": "yes" if yes_win else "no",
        "settlement_price_is_binary_proxy": True,
        "source": label.get("source_diagnostic", "sidecar_spot_diagnostic"),
    }


def _write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        for row in rows:
            handle.write(json.dumps(row, sort_keys=True) + "\n")


def _markdown(summary: SidecarShadowBuildSummary) -> str:
    return "\n".join(
        [
            "# RV600 Sidecar Shadow Root",
            "",
            "Research-only derived RV600 input root built from paired sidecar/independent-spot diagnostics.",
            "",
            "## Summary",
            "",
            f"- generated_utc: `{summary.generated_utc}`",
            f"- input_root: `{summary.input_root}`",
            f"- output_root: `{summary.output_root}`",
            f"- min_decision_ts_utc: `{summary.min_decision_ts_utc}`",
            f"- diagnostic_files: `{summary.diagnostic_files}`",
            f"- enriched_files: `{summary.enriched_files}`",
            f"- candidate_rows_written: `{summary.candidate_rows_written}`",
            f"- label_rows_written: `{summary.label_rows_written}`",
            f"- distinct_markets: `{summary.distinct_markets}`",
            "",
            "## Guardrails",
            "",
            "- one RV600 snapshot is written per market and decision timestamp",
            "- duplicate sidecar model-candidate rows are skipped to avoid replay inflation",
            "- by default only post-lock decisions are written",
            "- this converter writes research artifacts only; it does not touch live bot state or orders",
            "",
            "## Skips",
            "",
            f"- duplicate_snapshot_rows_skipped: `{summary.duplicate_snapshot_rows_skipped}`",
            f"- pre_min_decision_rows_skipped: `{summary.pre_min_decision_rows_skipped}`",
            f"- missing_label_rows_skipped: `{summary.missing_label_rows_skipped}`",
            f"- independent_spot_rows_skipped: `{summary.independent_spot_rows_skipped}`",
            f"- malformed_rows_skipped: `{summary.malformed_rows_skipped}`",
            f"- fetched_label_rows: `{summary.fetched_label_rows}`",
            "",
        ]
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Build an RV600-compatible shadow root from settled paired sidecar/spot diagnostics."
    )
    parser.add_argument("--input-root", type=Path, default=DEFAULT_INPUT_ROOT)
    parser.add_argument("--output-root", type=Path, default=DEFAULT_OUTPUT_ROOT)
    parser.add_argument("--min-decision-ts-utc", default=DEFAULT_MIN_DECISION_TS_UTC)
    parser.add_argument("--include-all-decisions", action="store_true")
    parser.add_argument("--allow-missing-independent-spot", action="store_true")
    parser.add_argument("--fetch-missing-labels", action="store_true")
    parser.add_argument("--fee-cents", type=float, default=2.0)
    parser.add_argument("--write", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    min_decision = None if args.include_all_decisions else _parse_dt_required(
        args.min_decision_ts_utc,
        "min_decision_ts_utc",
    )
    summary, candidate_rows, label_rows = build_sidecar_shadow_root(
        input_root=args.input_root,
        output_root=args.output_root,
        min_decision_ts_utc=min_decision,
        require_independent_spot=not bool(args.allow_missing_independent_spot),
        fetch_missing_labels=bool(args.fetch_missing_labels),
        fee_cents=float(args.fee_cents),
    )
    if args.write:
        write_sidecar_shadow_root(summary, candidate_rows, label_rows)
    print(f"candidate_rows_written={summary.candidate_rows_written}")
    print(f"label_rows_written={summary.label_rows_written}")
    print(f"distinct_markets={summary.distinct_markets}")
    print(f"duplicate_snapshot_rows_skipped={summary.duplicate_snapshot_rows_skipped}")
    print(f"pre_min_decision_rows_skipped={summary.pre_min_decision_rows_skipped}")
    print(f"missing_label_rows_skipped={summary.missing_label_rows_skipped}")
    print(f"fetched_label_rows={summary.fetched_label_rows}")
    if args.write:
        print(f"candidate_snapshot_path={summary.candidate_snapshot_path}")
        print(f"label_context_path={summary.label_context_path}")
        print(f"output_json={summary.output_json}")
    return 0


def _parse_dt_required(value: Any, name: str) -> datetime:
    text = str(value or "").strip()
    if not text:
        raise ValueError(f"missing {name}")
    parsed = datetime.fromisoformat(text.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def _dt_key(value: datetime) -> str:
    return value.astimezone(timezone.utc).isoformat()


def _required_float(value: Any, name: str) -> float:
    parsed = _optional_float(value)
    if parsed is None:
        raise ValueError(f"missing {name}")
    return parsed


def _optional_float(value: Any) -> float | None:
    if value in (None, ""):
        return None
    return float(value)


def _required_probability(value: Any, name: str) -> float:
    parsed = _optional_probability(value)
    if parsed is None:
        raise ValueError(f"missing {name}")
    return parsed


def _optional_probability(value: Any) -> float | None:
    parsed = _optional_float(value)
    if parsed is None:
        return None
    return max(0.0, min(1.0, parsed))


def _truthy(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() in {"1", "true", "yes", "y"}


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


if __name__ == "__main__":
    raise SystemExit(main())
