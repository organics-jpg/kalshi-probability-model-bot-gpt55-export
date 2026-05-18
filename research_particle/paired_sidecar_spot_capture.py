from __future__ import annotations

import argparse
import asyncio
import json
import uuid
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Iterable, Mapping

from run_v28_successor_sidecar_collection_cycle import RESEARCH_ONLY_GUARDRAILS
from run_v28_successor_sidecar_collection_cycle import run_cycle as run_sidecar_cycle
from run_v28_successor_sidecar_collection_cycle import write_outputs as write_sidecar_cycle_outputs

from .spot_context_merge import load_spot_ticks
from .spot_ticker_recorder import SpotTickerRecorderStatus, record_spot_ticks


ROOT = Path(__file__).resolve().parents[1]
EDGE_DIR = ROOT / "logs" / "edge_research"
DEFAULT_ARTIFACT_BASE = ROOT / "logs" / "particle_research" / "real_shadow" / "sidecar_spot_pairs"
LATEST_SIDECAR_BATCH_JSON = EDGE_DIR / "v28_successor_public_rest_sidecar_batch_latest.json"

PAIRED_GUARDRAILS = [
    "research-only paired capture",
    "does not start or stop live bot processes",
    "does not read or write secrets",
    "does not place orders",
    "does not mutate live thresholds or order logic",
    "promotion_allowed is always false",
]


@dataclass(frozen=True)
class SidecarSpotAlignmentRow:
    schema_version: str
    market_ticker: str
    bundle_path: str
    decision_ts_utc: str
    latest_spot_before_ts_utc: str
    latest_spot_before_exchange_ts_utc: str
    latest_spot_before_age_ms: float | None
    first_spot_after_ts_utc: str
    first_spot_after_age_ms: float | None
    independent_spot_source: str
    spot_ready_no_future: bool
    issue: str


@dataclass(frozen=True)
class PairedSidecarSpotCaptureResult:
    schema_version: str
    generated_utc: str
    run_id: str
    artifact_root: str
    collect_mode: str
    promotion_allowed: bool
    promotion_status: Mapping[str, Any]
    sidecar_cycle_status: str
    sidecar_markets_selected: int
    sidecar_packet_rows: int
    sidecar_frozen_rows: int
    sidecar_frozen_markets: int
    sidecar_latest_batch_json: str
    spot_feed: str
    spot_output: str
    spot_issues: str
    spot_status_path: str
    spot_status: str
    spot_ticks_written: int
    spot_issue_count: int
    spot_return_error: str
    spot_max_age_ms: float
    alignment_row_count: int
    alignment_ready_count: int
    alignment_issue_count: int
    paired_capture_ready: bool
    research_only_guardrails: tuple[str, ...]
    manifest_json: str
    manifest_md: str


def build_sidecar_spot_alignment(
    *,
    batch_report: Mapping[str, Any],
    spot_path: Path,
    workspace: Path = ROOT,
    max_age_ms: float = 2_000.0,
) -> list[SidecarSpotAlignmentRow]:
    ticks = load_spot_ticks(spot_path) if spot_path.exists() else []
    rows: list[SidecarSpotAlignmentRow] = []
    for market in batch_report.get("markets") or []:
        if not isinstance(market, Mapping):
            continue
        bundle_path = _resolve_bundle_path(market.get("output_bundle_json"), workspace=workspace)
        decision_ts = _bundle_decision_ts(bundle_path) or _parse_dt(
            (batch_report.get("summary") or {}).get("generated_utc")
        )
        ticker = str(market.get("market_ticker") or "")
        if decision_ts is None:
            rows.append(
                SidecarSpotAlignmentRow(
                    schema_version="sidecar-spot-alignment-v1",
                    market_ticker=ticker,
                    bundle_path=str(bundle_path) if bundle_path is not None else "",
                    decision_ts_utc="",
                    latest_spot_before_ts_utc="",
                    latest_spot_before_exchange_ts_utc="",
                    latest_spot_before_age_ms=None,
                    first_spot_after_ts_utc="",
                    first_spot_after_age_ms=None,
                    independent_spot_source="",
                    spot_ready_no_future=False,
                    issue="missing_sidecar_decision_timestamp",
                )
            )
            continue
        before = None
        after = None
        for tick in ticks:
            if tick.available_ts_utc <= decision_ts:
                before = tick
            elif after is None:
                after = tick
                break
        age_before_ms = (
            1000.0 * (decision_ts - before.available_ts_utc).total_seconds()
            if before is not None
            else None
        )
        age_after_ms = (
            1000.0 * (after.available_ts_utc - decision_ts).total_seconds()
            if after is not None
            else None
        )
        issue = ""
        if before is None:
            issue = "no_independent_spot_tick_at_or_before_sidecar_capture"
        elif age_before_ms is None or age_before_ms > max_age_ms:
            issue = f"latest_independent_spot_tick_too_old_ms={age_before_ms:.3f}"
        rows.append(
            SidecarSpotAlignmentRow(
                schema_version="sidecar-spot-alignment-v1",
                market_ticker=ticker,
                bundle_path=str(bundle_path) if bundle_path is not None else "",
                decision_ts_utc=decision_ts.isoformat(),
                latest_spot_before_ts_utc=before.available_ts_utc.isoformat() if before else "",
                latest_spot_before_exchange_ts_utc=before.exchange_ts_utc.isoformat() if before else "",
                latest_spot_before_age_ms=age_before_ms,
                first_spot_after_ts_utc=after.available_ts_utc.isoformat() if after else "",
                first_spot_after_age_ms=age_after_ms,
                independent_spot_source=before.source if before else "",
                spot_ready_no_future=before is not None and age_before_ms is not None and age_before_ms <= max_age_ms,
                issue=issue,
            )
        )
    return rows


async def run_paired_sidecar_spot_capture(
    *,
    artifact_root: Path,
    run_id: str,
    collect_mode: str = "fixture",
    spot_feed: str = "coinbase",
    spot_run_seconds: float = 15.0,
    spot_warmup_seconds: float = 1.0,
    spot_max_rows: int | None = None,
    spot_max_age_ms: float = 2_000.0,
    timeout_seconds: float = 10.0,
    max_markets: int = 80,
    nearest_close_only: bool = True,
    skip_label_fetch: bool = True,
    refresh_downstream_audits: bool = False,
    write_sidecar_cycle: bool = True,
) -> tuple[PairedSidecarSpotCaptureResult, list[SidecarSpotAlignmentRow], Mapping[str, Any]]:
    artifact_root.mkdir(parents=True, exist_ok=True)
    spot_path = artifact_root / "spot_ticks.ndjson"
    spot_issue_path = artifact_root / "spot_issues.ndjson"
    spot_status_path = artifact_root / "spot_status.json"
    manifest_json = artifact_root / "paired_sidecar_spot_manifest.json"
    manifest_md = artifact_root / "paired_sidecar_spot_manifest.md"

    capture_started_utc = datetime.now(timezone.utc)
    spot_task = asyncio.create_task(
        record_spot_ticks(
            output_path=spot_path,
            issue_path=spot_issue_path,
            status_path=spot_status_path,
            feed=spot_feed,
            run_seconds=max(0.1, float(spot_run_seconds)),
            max_rows=spot_max_rows,
        )
    )
    await asyncio.sleep(max(0.0, min(float(spot_warmup_seconds), float(spot_run_seconds))))
    sidecar_report = await asyncio.to_thread(
        run_sidecar_cycle,
        collect_mode=collect_mode.replace("-", "_"),
        timeout_seconds=timeout_seconds,
        max_markets=max_markets,
        nearest_close_only=nearest_close_only,
        write=write_sidecar_cycle,
        skip_label_fetch=skip_label_fetch,
        refresh_downstream_audits=refresh_downstream_audits,
    )
    if write_sidecar_cycle:
        write_sidecar_cycle_outputs(sidecar_report)
    spot_status = await spot_task
    capture_finished_utc = datetime.now(timezone.utc)

    loaded_batch_report = _load_json(LATEST_SIDECAR_BATCH_JSON) if LATEST_SIDECAR_BATCH_JSON.exists() else {}
    batch_report = batch_report_for_alignment(
        sidecar_report=sidecar_report,
        loaded_batch_report=loaded_batch_report,
        capture_started_utc=capture_started_utc,
        capture_finished_utc=capture_finished_utc,
    )
    alignment_rows = build_sidecar_spot_alignment(
        batch_report=batch_report,
        spot_path=spot_path,
        workspace=ROOT,
        max_age_ms=spot_max_age_ms,
    )
    result = build_manifest(
        run_id=run_id,
        artifact_root=artifact_root,
        collect_mode=collect_mode,
        sidecar_report=sidecar_report,
        batch_report=batch_report,
        spot_status=spot_status,
        spot_path=spot_path,
        spot_issue_path=spot_issue_path,
        spot_status_path=spot_status_path,
        spot_max_age_ms=spot_max_age_ms,
        alignment_rows=alignment_rows,
        manifest_json=manifest_json,
        manifest_md=manifest_md,
    )
    _write_outputs(result, alignment_rows, sidecar_report, batch_report)
    return result, alignment_rows, sidecar_report


def build_manifest(
    *,
    run_id: str,
    artifact_root: Path,
    collect_mode: str,
    sidecar_report: Mapping[str, Any],
    batch_report: Mapping[str, Any],
    spot_status: SpotTickerRecorderStatus,
    spot_path: Path,
    spot_issue_path: Path,
    spot_status_path: Path,
    spot_max_age_ms: float,
    alignment_rows: list[SidecarSpotAlignmentRow],
    manifest_json: Path,
    manifest_md: Path,
) -> PairedSidecarSpotCaptureResult:
    sidecar_summary = sidecar_report.get("summary") or {}
    batch_summary = batch_report.get("summary") or {}
    ready_count = sum(1 for row in alignment_rows if row.spot_ready_no_future)
    issue_count = sum(1 for row in alignment_rows if row.issue)
    paired_ready = bool(alignment_rows) and ready_count == len(alignment_rows) and spot_status.ticks_written > 0
    return PairedSidecarSpotCaptureResult(
        schema_version="paired-sidecar-spot-capture-v1",
        generated_utc=datetime.now(timezone.utc).isoformat(),
        run_id=run_id,
        artifact_root=str(artifact_root),
        collect_mode=collect_mode,
        promotion_allowed=False,
        promotion_status={
            "allowed": False,
            "reason": "paired sidecar spot capture is instrumentation evidence only; it cannot promote trading without locked OOS probability, EV-rank, and PnL gates",
        },
        sidecar_cycle_status=str(sidecar_summary.get("cycle_status") or ""),
        sidecar_markets_selected=int(batch_summary.get("markets_selected") or 0),
        sidecar_packet_rows=int(batch_summary.get("packet_rows") or 0),
        sidecar_frozen_rows=int(sidecar_summary.get("sidecar_frozen_rows") or 0),
        sidecar_frozen_markets=int(sidecar_summary.get("sidecar_frozen_markets") or 0),
        sidecar_latest_batch_json=_rel_path(LATEST_SIDECAR_BATCH_JSON),
        spot_feed=spot_status.source,
        spot_output=str(spot_path),
        spot_issues=str(spot_issue_path),
        spot_status_path=str(spot_status_path),
        spot_status=spot_status.status,
        spot_ticks_written=int(spot_status.ticks_written),
        spot_issue_count=int(spot_status.issue_count),
        spot_return_error=spot_status.error,
        spot_max_age_ms=float(spot_max_age_ms),
        alignment_row_count=len(alignment_rows),
        alignment_ready_count=ready_count,
        alignment_issue_count=issue_count,
        paired_capture_ready=paired_ready,
        research_only_guardrails=tuple(dict.fromkeys(PAIRED_GUARDRAILS + RESEARCH_ONLY_GUARDRAILS)),
        manifest_json=str(manifest_json),
        manifest_md=str(manifest_md),
    )


def batch_report_for_alignment(
    *,
    sidecar_report: Mapping[str, Any],
    loaded_batch_report: Mapping[str, Any],
    capture_started_utc: datetime | None = None,
    capture_finished_utc: datetime | None = None,
    tolerance_seconds: float = 2.0,
) -> Mapping[str, Any]:
    """Avoid pairing independent spot ticks to stale sidecar batch evidence."""
    summary = sidecar_report.get("summary") if isinstance(sidecar_report.get("summary"), Mapping) else {}
    blockers = {str(blocker) for blocker in (summary.get("blockers") or [])}
    if "blocked_collection_error" in blockers:
        return _empty_batch_report_for_alignment(
            batch_status="sidecar_collection_blocked_latest_batch_ignored",
            reason="sidecar collection reported blocked_collection_error; latest public REST batch may be stale and is not eligible for paired alignment",
        )

    collect_mode = str(summary.get("collect_mode") or "").replace("-", "_")
    if collect_mode == "none" or capture_started_utc is None or capture_finished_utc is None:
        return loaded_batch_report

    batch_summary = loaded_batch_report.get("summary") if isinstance(loaded_batch_report.get("summary"), Mapping) else {}
    batch_mode = str(batch_summary.get("mode") or "").replace("-", "_")
    if batch_mode and batch_mode != collect_mode:
        return _empty_batch_report_for_alignment(
            batch_status="sidecar_batch_mode_mismatch_ignored",
            reason=(
                "latest sidecar batch mode does not match the paired sidecar collection mode; "
                "batch is treated as stale or unrelated and is not eligible for paired alignment"
            ),
        )

    batch_generated_utc = _parse_dt(batch_summary.get("generated_utc"))
    if batch_generated_utc is None:
        return _empty_batch_report_for_alignment(
            batch_status="sidecar_batch_missing_generated_utc_ignored",
            reason="fresh paired sidecar capture could not verify latest batch generated_utc; batch is not eligible for paired alignment",
        )

    tolerance = timedelta(seconds=max(0.0, float(tolerance_seconds)))
    window_start = capture_started_utc.astimezone(timezone.utc) - tolerance
    window_end = capture_finished_utc.astimezone(timezone.utc) + tolerance
    if batch_generated_utc < window_start or batch_generated_utc > window_end:
        return _empty_batch_report_for_alignment(
            batch_status="sidecar_batch_outside_paired_capture_window_ignored",
            reason=(
                "latest sidecar batch generated_utc is outside this paired capture window; "
                "batch is treated as stale and is not eligible for paired alignment"
            ),
        )

    return loaded_batch_report


def _empty_batch_report_for_alignment(*, batch_status: str, reason: str) -> Mapping[str, Any]:
    return {
        "summary": {
            "batch_status": batch_status,
            "markets_selected": 0,
            "packet_rows": 0,
            "packet_markets": 0,
            "promotion_allowed": False,
            "reason": reason,
        },
        "markets": [],
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Research-only paired live sidecar snapshot plus independent BTC spot tick capture."
    )
    parser.add_argument("--collect-mode", choices=("fixture", "public-rest", "none"), default="fixture")
    parser.add_argument("--run-id", default="")
    parser.add_argument("--artifact-root", type=Path, default=None)
    parser.add_argument("--spot-feed", choices=("coinbase", "binance"), default="coinbase")
    parser.add_argument("--spot-run-seconds", type=float, default=15.0)
    parser.add_argument("--spot-warmup-seconds", type=float, default=1.0)
    parser.add_argument("--spot-max-rows", type=int, default=None)
    parser.add_argument("--spot-max-age-ms", type=float, default=2_000.0)
    parser.add_argument("--timeout-seconds", type=float, default=10.0)
    parser.add_argument("--max-markets", type=int, default=80)
    parser.add_argument("--all-open-closes", action="store_true")
    parser.add_argument("--fetch-labels", action="store_true")
    parser.add_argument("--refresh-downstream-audits", action="store_true")
    parser.add_argument(
        "--skip-sidecar-cycle-write",
        action="store_true",
        help="Do not write the normal sidecar cycle artifacts; useful only for narrow debugging because alignment needs the latest sidecar batch report.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    run_id = args.run_id or datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ") + "-" + uuid.uuid4().hex[:8]
    artifact_root = args.artifact_root or DEFAULT_ARTIFACT_BASE / run_id
    result, _alignment, _sidecar = asyncio.run(
        run_paired_sidecar_spot_capture(
            artifact_root=artifact_root,
            run_id=run_id,
            collect_mode=args.collect_mode,
            spot_feed=args.spot_feed,
            spot_run_seconds=args.spot_run_seconds,
            spot_warmup_seconds=args.spot_warmup_seconds,
            spot_max_rows=args.spot_max_rows,
            spot_max_age_ms=args.spot_max_age_ms,
            timeout_seconds=args.timeout_seconds,
            max_markets=args.max_markets,
            nearest_close_only=not bool(args.all_open_closes),
            skip_label_fetch=not bool(args.fetch_labels),
            refresh_downstream_audits=bool(args.refresh_downstream_audits),
            write_sidecar_cycle=not bool(args.skip_sidecar_cycle_write),
        )
    )
    print(f"paired_capture_ready={result.paired_capture_ready}")
    print(f"sidecar_cycle_status={result.sidecar_cycle_status}")
    print(f"spot_ticks_written={result.spot_ticks_written}")
    print(f"alignment_ready_count={result.alignment_ready_count}")
    print(f"alignment_row_count={result.alignment_row_count}")
    print(f"promotion_allowed={result.promotion_allowed}")
    print(f"manifest_json={result.manifest_json}")
    return 0 if result.spot_status != "error" else 1


def _write_outputs(
    result: PairedSidecarSpotCaptureResult,
    alignment_rows: list[SidecarSpotAlignmentRow],
    sidecar_report: Mapping[str, Any],
    batch_report: Mapping[str, Any],
) -> None:
    manifest_json = Path(result.manifest_json)
    manifest_md = Path(result.manifest_md)
    manifest_json.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "summary": asdict(result),
        "alignment_rows": [asdict(row) for row in alignment_rows],
        "sidecar_cycle_summary": sidecar_report.get("summary") or {},
        "sidecar_batch_summary": batch_report.get("summary") or {},
        "sidecar_batch_markets": batch_report.get("markets") or [],
    }
    manifest_json.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    manifest_md.write_text(_manifest_markdown(result, alignment_rows), encoding="utf-8")


def _manifest_markdown(
    result: PairedSidecarSpotCaptureResult,
    alignment_rows: list[SidecarSpotAlignmentRow],
) -> str:
    lines = [
        "# Paired Sidecar Spot Capture",
        "",
        "Research-only paired capture of one sidecar collection cycle and independent public BTC spot ticks. It does not touch live bot state, orders, thresholds, secrets, or processes.",
        "",
        "## Summary",
        "",
        f"- Generated UTC: `{result.generated_utc}`",
        f"- Run id: `{result.run_id}`",
        f"- Collect mode: `{result.collect_mode}`",
        f"- Promotion allowed: `{result.promotion_allowed}`",
        f"- Paired capture ready: `{result.paired_capture_ready}`",
        f"- Sidecar cycle status: `{result.sidecar_cycle_status}`",
        f"- Sidecar markets selected / packet rows: `{result.sidecar_markets_selected}` / `{result.sidecar_packet_rows}`",
        f"- Sidecar frozen rows / markets: `{result.sidecar_frozen_rows}` / `{result.sidecar_frozen_markets}`",
        f"- Spot feed/status/ticks: `{result.spot_feed}` / `{result.spot_status}` / `{result.spot_ticks_written}`",
        f"- Alignment ready rows: `{result.alignment_ready_count}` / `{result.alignment_row_count}`",
        "",
        "## Alignment",
        "",
        "| market | decision ts | latest spot before | age ms | ready | issue |",
        "|---|---|---|---:|---|---|",
    ]
    for row in alignment_rows:
        age = "" if row.latest_spot_before_age_ms is None else f"{row.latest_spot_before_age_ms:.3f}"
        lines.append(
            f"| `{row.market_ticker}` | `{row.decision_ts_utc}` | `{row.latest_spot_before_ts_utc}` | "
            f"{age} | `{row.spot_ready_no_future}` | `{row.issue}` |"
        )
    if not alignment_rows:
        lines.append("|  |  |  |  | `False` | `no sidecar batch markets found` |")
    lines.extend(
        [
            "",
            "## Read",
            "",
            "- `spot_ready_no_future=True` means a locally received independent spot tick existed at or before the sidecar bundle capture timestamp within the configured freshness limit.",
            "- This artifact proves instrumentation coverage only. It is not a probability, EV, PnL, or promotion result.",
        ]
    )
    return "\n".join(lines) + "\n"


def _resolve_bundle_path(value: Any, *, workspace: Path) -> Path | None:
    text = str(value or "").strip()
    if not text:
        return None
    path = Path(text)
    if path.is_absolute():
        return path
    return workspace / path


def _bundle_decision_ts(path: Path | None) -> datetime | None:
    if path is None or not path.exists():
        return None
    try:
        payload = _load_json(path)
    except Exception:  # noqa: BLE001
        return None
    for key in ("registered_utc", "decision_ts_utc", "generated_utc"):
        parsed = _parse_dt(payload.get(key))
        if parsed is not None:
            return parsed
    checkpoint = payload.get("checkpoint")
    if isinstance(checkpoint, Mapping):
        parsed = _parse_dt(checkpoint.get("checkpoint_ts"))
        if parsed is not None:
            return parsed
    return None


def _load_json(path: Path) -> Mapping[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, Mapping):
        raise ValueError(f"JSON object expected: {path}")
    return payload


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


def _rel_path(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(ROOT)).replace("\\", "/")
    except ValueError:
        return str(path)


def _read_jsonl(path: Path) -> Iterable[Mapping[str, Any]]:
    with path.open("r", encoding="utf-8", errors="replace") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            payload = json.loads(line)
            if isinstance(payload, Mapping):
                yield payload


if __name__ == "__main__":
    raise SystemExit(main())
