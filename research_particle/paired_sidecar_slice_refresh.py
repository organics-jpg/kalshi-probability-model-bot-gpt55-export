from __future__ import annotations

import argparse
import asyncio
import json
import uuid
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping, Sequence

from probe_particle_goal_completion_audit import audit as particle_goal_audit
from probe_particle_goal_completion_audit import write_report as write_particle_goal_audit

from .paired_sidecar_blend_failure_analysis import (
    DEFAULT_OUTPUT_JSON as DEFAULT_FAILURE_JSON,
    DEFAULT_OUTPUT_MD as DEFAULT_FAILURE_MD,
    _slice_buckets,
    build_paired_sidecar_blend_failure_analysis,
    write_paired_sidecar_blend_failure_analysis,
)
from .paired_sidecar_online_calibration import (
    DEFAULT_OUTPUT_JSON as DEFAULT_ONLINE_JSON,
    DEFAULT_OUTPUT_MD as DEFAULT_ONLINE_MD,
    build_paired_sidecar_online_calibration,
    write_paired_sidecar_online_calibration,
)
from .paired_sidecar_slice_oos import (
    DEFAULT_OUTPUT_DIR as DEFAULT_REPORT_DIR,
    evaluate_paired_sidecar_slice_oos,
    write_paired_sidecar_slice_oos_report,
)
from .paired_sidecar_spot_aggregate import (
    DEFAULT_INPUT_ROOT,
    DEFAULT_OUTPUT_JSON as DEFAULT_AGGREGATE_JSON,
)
from .paired_sidecar_spot_capture import run_paired_sidecar_spot_capture
from .paired_sidecar_spot_diagnostic import DEFAULT_LABELED_CSV
from .paired_sidecar_spot_enrichment import DEFAULT_PACKET_CSV
from .paired_sidecar_spot_refresh import (
    DEFAULT_REFRESH_JSON,
    DEFAULT_REFRESH_MD,
    refresh_paired_sidecar_spot_evidence,
    write_refresh_outputs,
)


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PLAN_JSON = (
    ROOT
    / "logs"
    / "particle_research"
    / "locked_oos_plans"
    / "paired_sidecar_slice_PSLICELOCK001_locked_plan.json"
)
DEFAULT_OUTPUT_JSON = ROOT / "logs" / "particle_research" / "reports" / "paired_sidecar_slice_refresh_latest.json"
DEFAULT_OUTPUT_MD = ROOT / "logs" / "particle_research" / "reports" / "paired_sidecar_slice_refresh_latest.md"


@dataclass(frozen=True)
class PairedSidecarSliceRefreshSummary:
    schema_version: str
    generated_utc: str
    promotion_allowed: bool
    promotion_status: Mapping[str, Any]
    plan_json: str
    hypothesis_id: str
    model: str
    slice_type: str
    bucket: str
    locked_after_utc: str
    output_json: str
    output_md: str
    collect_requested: bool
    collect_run_id: str
    collect_status: str
    collect_paired_capture_ready: bool
    collect_manifest_json: str
    label_refresh_requested: bool
    label_refresh_status: str
    paired_manifest_count: int
    paired_diagnostic_ready_count: int
    aggregate_joined_rows: int
    aggregate_joined_markets: int
    aggregate_candidate_ready: bool
    pending_manifest_count: int
    pending_enriched_rows: int
    pending_slice_previews: tuple[Mapping[str, Any], ...]
    next_pending_market_close_utc: str
    seconds_until_next_pending_close: float | None
    online_prepared_rows: int
    online_input_markets: int
    online_best_model_by_brier: str
    online_market_equal_best_model_by_brier: str
    failure_posthoc_slice_candidates: int
    slice_report_count: int
    slice_reports: tuple[Mapping[str, Any], ...]
    slice_fresh_candidate_rows: int
    slice_fresh_markets: int
    slice_rows: int
    slice_markets: int
    slice_selected_count: int
    slice_selected_pnl_cents: float
    slice_promotion_safe: bool
    goal_audit_refreshed: bool
    goal_complete: bool


def refresh_paired_sidecar_slice_status(
    *,
    plan_json: Path = DEFAULT_PLAN_JSON,
    plan_jsons: Sequence[Path] | None = None,
    input_root: Path = DEFAULT_INPUT_ROOT,
    packet_csv: Path = DEFAULT_PACKET_CSV,
    labeled_csv: Path = DEFAULT_LABELED_CSV,
    refresh_json: Path = DEFAULT_REFRESH_JSON,
    refresh_md: Path = DEFAULT_REFRESH_MD,
    aggregate_json: Path = DEFAULT_AGGREGATE_JSON,
    online_json: Path = DEFAULT_ONLINE_JSON,
    online_md: Path = DEFAULT_ONLINE_MD,
    failure_json: Path = DEFAULT_FAILURE_JSON,
    failure_md: Path = DEFAULT_FAILURE_MD,
    slice_report_dir: Path = DEFAULT_REPORT_DIR,
    slice_stem: str = "paired_sidecar_slice_oos_PSLICELOCK001_latest",
    output_json: Path = DEFAULT_OUTPUT_JSON,
    output_md: Path = DEFAULT_OUTPUT_MD,
    write: bool = False,
    fetch_labels: bool = False,
    refresh_goal_audit: bool = True,
    collect_once: bool = False,
    collect_run_id: str = "",
    collect_mode: str = "public-rest",
    spot_feed: str = "coinbase",
    spot_run_seconds: float = 15.0,
    spot_warmup_seconds: float = 1.0,
    spot_max_age_ms: float = 2_000.0,
    timeout_seconds: float = 10.0,
    max_markets: int = 80,
) -> PairedSidecarSliceRefreshSummary:
    plan_paths = _slice_plan_paths(primary=plan_json, explicit=plan_jsons)
    plan_json = plan_paths[0]
    plan = _load_json(plan_json)
    hypothesis_id = str(plan.get("hypothesis_id") or "")
    model = str(plan.get("model") or "")
    slice_type = str(plan.get("slice_type") or "")
    bucket = str(plan.get("bucket") or "")
    locked_after_utc = str(plan.get("locked_after_utc") or "")

    collect_status = "not_requested"
    capture_ready = False
    collect_manifest_json = ""
    run_id = collect_run_id
    if collect_once:
        run_id = run_id or datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ") + "-" + uuid.uuid4().hex[:8]
        artifact_root = input_root / run_id
        capture, _alignment, _sidecar = asyncio.run(
            run_paired_sidecar_spot_capture(
                artifact_root=artifact_root,
                run_id=run_id,
                collect_mode=collect_mode,
                spot_feed=spot_feed,
                spot_run_seconds=spot_run_seconds,
                spot_warmup_seconds=spot_warmup_seconds,
                spot_max_age_ms=spot_max_age_ms,
                timeout_seconds=timeout_seconds,
                max_markets=max_markets,
                nearest_close_only=True,
                skip_label_fetch=True,
                refresh_downstream_audits=False,
                write_sidecar_cycle=True,
            )
        )
        collect_status = str(capture.sidecar_cycle_status)
        capture_ready = bool(capture.paired_capture_ready)
        collect_manifest_json = str(capture.manifest_json)

    refresh_summary, refresh_rows = refresh_paired_sidecar_spot_evidence(
        input_root=input_root,
        packet_csv=packet_csv,
        labeled_csv=labeled_csv,
        output_json=refresh_json,
        output_md=refresh_md,
        write=write,
        refresh_goal_audit=False,
        fetch_labels=fetch_labels,
    )
    if write:
        write_refresh_outputs(refresh_summary, refresh_rows)

    online_summary, model_rows, market_equal_rows, calibrated_rows, market_model_rows = (
        build_paired_sidecar_online_calibration(
            input_root=input_root,
            input_aggregate_json=aggregate_json,
            output_json=online_json,
            output_md=online_md,
        )
    )
    if write:
        write_paired_sidecar_online_calibration(
            online_summary,
            model_rows,
            market_equal_rows,
            calibrated_rows,
            market_model_rows,
        )

    failure_report = build_paired_sidecar_blend_failure_analysis(
        online_calibration_json=online_json,
        aggregate_json=aggregate_json,
        output_json=failure_json,
        output_md=failure_md,
    )
    if write:
        write_paired_sidecar_blend_failure_analysis(failure_report)

    slice_reports = []
    plan_payloads = []
    for idx, current_plan_json in enumerate(plan_paths):
        current_plan = _load_json(current_plan_json)
        plan_payloads.append(current_plan)
        current_stem = (
            slice_stem
            if idx == 0 and len(plan_paths) == 1
            else _slice_report_stem(current_plan_json, current_plan, default_stem=slice_stem)
        )
        report = evaluate_paired_sidecar_slice_oos(
            online_calibration_json=online_json,
            aggregate_json=aggregate_json,
            output_dir=slice_report_dir,
            stem=current_stem,
            plan_json=current_plan_json,
        )
        slice_reports.append(report)
        if write:
            write_paired_sidecar_slice_oos_report(report)
    slice_report = slice_reports[0]

    pending = _pending_manifest_status(input_root=input_root, plan_payloads=plan_payloads)
    goal_complete = False
    goal_audit_refreshed = False
    if write and refresh_goal_audit:
        goal_payload = particle_goal_audit(ROOT)
        write_particle_goal_audit(goal_payload)
        goal_audit_refreshed = True
        goal_complete = bool(goal_payload.get("complete"))

    return PairedSidecarSliceRefreshSummary(
        schema_version="paired-sidecar-slice-refresh-v1",
        generated_utc=datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        promotion_allowed=False,
        promotion_status={
            "allowed": False,
            "reason": "locked slice refresh is research-only and cannot approve live trading",
        },
        plan_json=str(plan_json),
        hypothesis_id=hypothesis_id,
        model=model,
        slice_type=slice_type,
        bucket=bucket,
        locked_after_utc=locked_after_utc,
        output_json=str(output_json),
        output_md=str(output_md),
        collect_requested=bool(collect_once),
        collect_run_id=run_id,
        collect_status=collect_status,
        collect_paired_capture_ready=capture_ready,
        collect_manifest_json=collect_manifest_json,
        label_refresh_requested=bool(fetch_labels),
        label_refresh_status=refresh_summary.label_refresh_status,
        paired_manifest_count=refresh_summary.manifest_count,
        paired_diagnostic_ready_count=refresh_summary.diagnostic_ready_count,
        aggregate_joined_rows=refresh_summary.aggregate_joined_rows,
        aggregate_joined_markets=refresh_summary.aggregate_joined_markets,
        aggregate_candidate_ready=refresh_summary.aggregate_candidate_ready,
        pending_manifest_count=int(pending["pending_manifest_count"]),
        pending_enriched_rows=int(pending["pending_enriched_rows"]),
        pending_slice_previews=tuple(pending["pending_slice_previews"]),
        next_pending_market_close_utc=str(pending["next_pending_market_close_utc"]),
        seconds_until_next_pending_close=pending["seconds_until_next_pending_close"],
        online_prepared_rows=online_summary.prepared_rows,
        online_input_markets=online_summary.input_markets,
        online_best_model_by_brier=online_summary.best_model_by_brier,
        online_market_equal_best_model_by_brier=online_summary.market_equal_best_model_by_brier,
        failure_posthoc_slice_candidates=len(failure_report.posthoc_slice_candidates),
        slice_report_count=len(slice_reports),
        slice_reports=tuple(_slice_report_summary(report) for report in slice_reports),
        slice_fresh_candidate_rows=slice_report.fresh_candidate_rows,
        slice_fresh_markets=slice_report.fresh_markets,
        slice_rows=slice_report.slice_rows,
        slice_markets=slice_report.slice_markets,
        slice_selected_count=slice_report.selected_metrics.selected_count,
        slice_selected_pnl_cents=slice_report.selected_metrics.selected_pnl_cents,
        slice_promotion_safe=slice_report.promotion_safe,
        goal_audit_refreshed=goal_audit_refreshed,
        goal_complete=goal_complete,
    )


def write_paired_sidecar_slice_refresh(summary: PairedSidecarSliceRefreshSummary) -> None:
    output_json = Path(summary.output_json)
    output_md = Path(summary.output_md)
    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_md.parent.mkdir(parents=True, exist_ok=True)
    output_json.write_text(json.dumps({"summary": asdict(summary)}, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    output_md.write_text(_markdown(summary), encoding="utf-8")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Research-only refresh of locked paired sidecar slice status."
    )
    parser.add_argument("--plan-json", type=Path, default=DEFAULT_PLAN_JSON)
    parser.add_argument(
        "--extra-plan-json",
        action="append",
        type=Path,
        default=None,
        help="Additional locked slice plans to refresh after the primary plan.",
    )
    parser.add_argument("--input-root", type=Path, default=DEFAULT_INPUT_ROOT)
    parser.add_argument("--packet-csv", type=Path, default=DEFAULT_PACKET_CSV)
    parser.add_argument("--labeled-csv", type=Path, default=DEFAULT_LABELED_CSV)
    parser.add_argument("--refresh-json", type=Path, default=DEFAULT_REFRESH_JSON)
    parser.add_argument("--refresh-md", type=Path, default=DEFAULT_REFRESH_MD)
    parser.add_argument("--aggregate-json", type=Path, default=DEFAULT_AGGREGATE_JSON)
    parser.add_argument("--online-json", type=Path, default=DEFAULT_ONLINE_JSON)
    parser.add_argument("--online-md", type=Path, default=DEFAULT_ONLINE_MD)
    parser.add_argument("--failure-json", type=Path, default=DEFAULT_FAILURE_JSON)
    parser.add_argument("--failure-md", type=Path, default=DEFAULT_FAILURE_MD)
    parser.add_argument("--slice-report-dir", type=Path, default=DEFAULT_REPORT_DIR)
    parser.add_argument("--slice-stem", default="paired_sidecar_slice_oos_PSLICELOCK001_latest")
    parser.add_argument("--output-json", type=Path, default=DEFAULT_OUTPUT_JSON)
    parser.add_argument("--output-md", type=Path, default=DEFAULT_OUTPUT_MD)
    parser.add_argument("--fetch-labels", action="store_true")
    parser.add_argument("--collect-once", action="store_true")
    parser.add_argument("--collect-run-id", default="")
    parser.add_argument("--spot-run-seconds", type=float, default=15.0)
    parser.add_argument("--spot-warmup-seconds", type=float, default=1.0)
    parser.add_argument("--spot-max-age-ms", type=float, default=2_000.0)
    parser.add_argument("--timeout-seconds", type=float, default=10.0)
    parser.add_argument("--max-markets", type=int, default=80)
    parser.add_argument("--skip-goal-audit", action="store_true")
    parser.add_argument("--write", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    summary = refresh_paired_sidecar_slice_status(
        plan_json=args.plan_json,
        plan_jsons=args.extra_plan_json,
        input_root=args.input_root,
        packet_csv=args.packet_csv,
        labeled_csv=args.labeled_csv,
        refresh_json=args.refresh_json,
        refresh_md=args.refresh_md,
        aggregate_json=args.aggregate_json,
        online_json=args.online_json,
        online_md=args.online_md,
        failure_json=args.failure_json,
        failure_md=args.failure_md,
        slice_report_dir=args.slice_report_dir,
        slice_stem=args.slice_stem,
        output_json=args.output_json,
        output_md=args.output_md,
        write=bool(args.write),
        fetch_labels=bool(args.fetch_labels),
        refresh_goal_audit=not bool(args.skip_goal_audit),
        collect_once=bool(args.collect_once),
        collect_run_id=args.collect_run_id,
        spot_run_seconds=float(args.spot_run_seconds),
        spot_warmup_seconds=float(args.spot_warmup_seconds),
        spot_max_age_ms=float(args.spot_max_age_ms),
        timeout_seconds=float(args.timeout_seconds),
        max_markets=int(args.max_markets),
    )
    if args.write:
        write_paired_sidecar_slice_refresh(summary)
    print(f"hypothesis_id={summary.hypothesis_id}")
    print(f"collect_requested={summary.collect_requested}")
    print(f"collect_status={summary.collect_status}")
    print(f"label_refresh_requested={summary.label_refresh_requested}")
    print(f"label_refresh_status={summary.label_refresh_status}")
    print(f"aggregate_joined_rows={summary.aggregate_joined_rows}")
    print(f"aggregate_joined_markets={summary.aggregate_joined_markets}")
    print(f"pending_manifest_count={summary.pending_manifest_count}")
    print(f"pending_enriched_rows={summary.pending_enriched_rows}")
    for item in summary.pending_slice_previews:
        print(
            "pending_slice_preview="
            f"{item.get('hypothesis_id')} "
            f"fresh={item.get('pending_fresh_rows')}/{item.get('pending_fresh_markets')} "
            f"slice={item.get('pending_slice_rows')}/{item.get('pending_slice_markets')}"
        )
    print(f"next_pending_market_close_utc={summary.next_pending_market_close_utc}")
    print(f"seconds_until_next_pending_close={summary.seconds_until_next_pending_close}")
    print(f"online_prepared_rows={summary.online_prepared_rows}")
    print(f"slice_report_count={summary.slice_report_count}")
    for item in summary.slice_reports:
        print(
            "slice_report="
            f"{item.get('hypothesis_id')} "
            f"rows={item.get('slice_rows')} "
            f"markets={item.get('slice_markets')} "
            f"selected={item.get('selected_count')} "
            f"pnl={item.get('selected_pnl_cents')} "
            f"safe={item.get('promotion_safe')}"
        )
    print(f"slice_fresh_candidate_rows={summary.slice_fresh_candidate_rows}")
    print(f"slice_fresh_markets={summary.slice_fresh_markets}")
    print(f"slice_rows={summary.slice_rows}")
    print(f"slice_markets={summary.slice_markets}")
    print(f"slice_selected_count={summary.slice_selected_count}")
    print(f"slice_selected_pnl_cents={summary.slice_selected_pnl_cents:.4f}")
    print(f"slice_promotion_safe={summary.slice_promotion_safe}")
    print(f"promotion_allowed={summary.promotion_allowed}")
    print(f"goal_complete={summary.goal_complete}")
    print(f"output_json={summary.output_json}")
    return 0


def _load_json(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return payload if isinstance(payload, dict) else {}


def _slice_plan_paths(*, primary: Path, explicit: Sequence[Path] | None) -> tuple[Path, ...]:
    candidates = [primary]
    if explicit is not None:
        candidates.extend(explicit)
    else:
        candidates.extend(sorted(primary.parent.glob("paired_sidecar_slice_PSLICELOCK*_locked_plan.json")))
    unique: list[Path] = []
    seen: set[str] = set()
    for path in candidates:
        key = str(path.resolve())
        if key in seen:
            continue
        seen.add(key)
        unique.append(path)
    return tuple(unique)


def _slice_report_stem(plan_path: Path, plan_payload: Mapping[str, Any], *, default_stem: str) -> str:
    run_id = str(plan_payload.get("run_id") or "")
    if run_id:
        return f"paired_sidecar_slice_oos_{run_id}_latest"
    if plan_path.stem:
        return plan_path.stem.replace("_locked_plan", "_oos_latest")
    return default_stem


def _slice_report_summary(report: Any) -> Mapping[str, Any]:
    return {
        "hypothesis_id": report.hypothesis_id,
        "model": report.model,
        "bucket": report.bucket,
        "locked_after_utc": report.locked_after_utc,
        "promotion_allowed": report.promotion_allowed,
        "promotion_safe": report.promotion_safe,
        "fresh_candidate_rows": report.fresh_candidate_rows,
        "fresh_markets": report.fresh_markets,
        "slice_rows": report.slice_rows,
        "slice_markets": report.slice_markets,
        "selected_count": report.selected_metrics.selected_count,
        "selected_pnl_cents": report.selected_metrics.selected_pnl_cents,
        "top_ev_bucket_pnl_cents": report.selected_metrics.top_ev_bucket_pnl_cents,
    }


def _pending_manifest_status(
    *,
    input_root: Path,
    plan_payloads: Sequence[Mapping[str, Any]] = (),
) -> dict[str, Any]:
    pending_count = 0
    pending_enriched_rows = 0
    close_times: list[datetime] = []
    pending_rows: list[Mapping[str, Any]] = []
    for manifest_path in sorted(input_root.glob("*/paired_sidecar_spot_manifest.json")):
        manifest = _load_json(manifest_path)
        summary = _summary_from_payload(manifest)
        if not bool(summary.get("paired_capture_ready")):
            continue
        diagnostic = _load_json(manifest_path.parent / "sidecar_spot_tick_vs_candle_diagnostic.json")
        diagnostic_summary = _summary_from_payload(diagnostic)
        if bool(diagnostic_summary.get("diagnostic_ready")):
            continue
        enrichment = _load_json(manifest_path.parent / "sidecar_packets_independent_spot_enriched.json")
        enrichment_summary = _summary_from_payload(enrichment)
        if not bool(enrichment_summary.get("enrichment_ready")):
            continue
        rows = enrichment.get("rows") or enrichment.get("enriched_rows") or []
        rows = [row for row in rows if isinstance(row, Mapping)]
        pending_count += 1
        pending_enriched_rows += int(enrichment_summary.get("enriched_packet_rows", 0) or 0)
        pending_rows.extend(rows)
        for market in manifest.get("sidecar_batch_markets") or []:
            if not isinstance(market, Mapping):
                continue
            close_ts = _parse_dt(str(market.get("market_close_ts_utc") or ""))
            if close_ts is not None:
                close_times.append(close_ts)
    now = datetime.now(timezone.utc)
    future_or_recent = sorted(close_times)
    next_close = future_or_recent[0] if future_or_recent else None
    return {
        "pending_manifest_count": pending_count,
        "pending_enriched_rows": pending_enriched_rows,
        "pending_slice_previews": tuple(_pending_slice_previews(pending_rows, plan_payloads)),
        "next_pending_market_close_utc": "" if next_close is None else next_close.isoformat(),
        "seconds_until_next_pending_close": (
            None if next_close is None else (next_close - now).total_seconds()
        ),
    }


def _pending_slice_previews(
    pending_rows: Sequence[Mapping[str, Any]],
    plan_payloads: Sequence[Mapping[str, Any]],
) -> list[Mapping[str, Any]]:
    normalized_rows = [_pending_preview_row(row) for row in pending_rows]
    previews: list[Mapping[str, Any]] = []
    for plan in plan_payloads:
        hypothesis_id = str(plan.get("hypothesis_id") or "")
        slice_type = str(plan.get("slice_type") or "")
        bucket = str(plan.get("bucket") or "")
        locked_after_utc = str(plan.get("locked_after_utc") or "")
        lock_ts = _parse_dt(locked_after_utc)
        fresh_rows = [row for row in normalized_rows if _row_after_lock(row, lock_ts)]
        slice_rows = [
            row
            for row in fresh_rows
            if (slice_type, bucket) in _slice_buckets(row)
        ]
        previews.append(
            {
                "hypothesis_id": hypothesis_id,
                "model": str(plan.get("model") or ""),
                "slice_type": slice_type,
                "bucket": bucket,
                "locked_after_utc": locked_after_utc,
                "pending_fresh_rows": len(fresh_rows),
                "pending_fresh_markets": _market_count(fresh_rows),
                "pending_slice_rows": len(slice_rows),
                "pending_slice_markets": _market_count(slice_rows),
                "outcome_free": True,
            }
        )
    return previews


def _pending_preview_row(row: Mapping[str, Any]) -> Mapping[str, Any]:
    item = dict(row)
    if "candidate_raw_p_yes" not in item and "candidate_p_yes" in item:
        item["candidate_raw_p_yes"] = item["candidate_p_yes"]
    if "market_side_ask_p_yes" not in item and "book_implied_yes_from_side_ask" in item:
        item["market_side_ask_p_yes"] = item["book_implied_yes_from_side_ask"]
    return item


def _row_after_lock(row: Mapping[str, Any], lock_ts: datetime | None) -> bool:
    if lock_ts is None:
        return True
    decision_ts = _parse_dt(str(row.get("decision_ts_utc") or ""))
    return decision_ts is not None and decision_ts > lock_ts


def _market_count(rows: Sequence[Mapping[str, Any]]) -> int:
    return len({str(row.get("market_ticker") or "") for row in rows if row.get("market_ticker")})


def _summary_from_payload(payload: Mapping[str, Any]) -> Mapping[str, Any]:
    summary = payload.get("summary")
    return summary if isinstance(summary, Mapping) else payload


def _parse_dt(value: str) -> datetime | None:
    if not value:
        return None
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def _markdown(summary: PairedSidecarSliceRefreshSummary) -> str:
    lines = [
        "# Paired Sidecar Slice Refresh",
        "",
        "Research-only maintenance refresh for the predeclared paired sidecar slice. By default it does not collect new snapshots, place orders, or touch live bot state.",
        "",
        "## Summary",
        "",
        f"- generated_utc: `{summary.generated_utc}`",
        f"- promotion_allowed: `{summary.promotion_allowed}`",
        f"- hypothesis_id: `{summary.hypothesis_id}`",
        f"- model: `{summary.model}`",
        f"- slice: `{summary.slice_type}={summary.bucket}`",
        f"- locked_after_utc: `{summary.locked_after_utc}`",
        f"- collect_requested/status: `{summary.collect_requested}` / `{summary.collect_status}`",
        f"- label_refresh_requested/status: `{summary.label_refresh_requested}` / `{summary.label_refresh_status}`",
        f"- aggregate rows / markets: `{summary.aggregate_joined_rows}` / `{summary.aggregate_joined_markets}`",
        f"- pending manifests / enriched rows: `{summary.pending_manifest_count}` / `{summary.pending_enriched_rows}`",
        f"- next pending market close UTC: `{summary.next_pending_market_close_utc}`",
        f"- seconds until next pending close: `{summary.seconds_until_next_pending_close}`",
        f"- online prepared rows / markets: `{summary.online_prepared_rows}` / `{summary.online_input_markets}`",
        f"- slice report count: `{summary.slice_report_count}`",
        f"- slice fresh rows / markets: `{summary.slice_fresh_candidate_rows}` / `{summary.slice_fresh_markets}`",
        f"- slice rows / markets: `{summary.slice_rows}` / `{summary.slice_markets}`",
        f"- slice selected count: `{summary.slice_selected_count}`",
        f"- slice selected PnL cents: `{summary.slice_selected_pnl_cents:.1f}`",
        f"- slice promotion_safe: `{summary.slice_promotion_safe}`",
        f"- goal audit refreshed/complete: `{summary.goal_audit_refreshed}` / `{summary.goal_complete}`",
        "",
        "## Slice Reports",
        "",
        "| hypothesis | model | fresh rows/markets | slice rows/markets | selected | selected pnl c | top EV pnl c | safe |",
        "| --- | --- | ---: | ---: | ---: | ---: | ---: | --- |",
    ]
    for item in summary.slice_reports:
        lines.append(
            "| "
            f"`{item.get('hypothesis_id')}` | "
            f"`{item.get('model')}` | "
            f"`{item.get('fresh_candidate_rows')}` / `{item.get('fresh_markets')}` | "
            f"`{item.get('slice_rows')}` / `{item.get('slice_markets')}` | "
            f"`{item.get('selected_count')}` | "
            f"`{float(item.get('selected_pnl_cents') or 0):.1f}` | "
            f"`{float(item.get('top_ev_bucket_pnl_cents') or 0):.1f}` | "
            f"`{item.get('promotion_safe')}` |"
        )
    lines.extend(
        [
            "",
            "## Pending Slice Preview",
            "",
            "| hypothesis | model | pending fresh rows/markets | pending slice rows/markets | outcome-free |",
            "| --- | --- | ---: | ---: | --- |",
        ]
    )
    for item in summary.pending_slice_previews:
        lines.append(
            "| "
            f"`{item.get('hypothesis_id')}` | "
            f"`{item.get('model')}` | "
            f"`{item.get('pending_fresh_rows')}` / `{item.get('pending_fresh_markets')}` | "
            f"`{item.get('pending_slice_rows')}` / `{item.get('pending_slice_markets')}` | "
            f"`{item.get('outcome_free')}` |"
        )
    lines.extend(
        [
            "",
        "## Read",
        "",
        "- `slice_promotion_safe=True` would still be research evidence only; the live bot remains untouched until the broader goal audit clears.",
        "- Post-lock rows are the only rows counted by the locked slice evaluator.",
        "",
        ]
    )
    return "\n".join(lines)


if __name__ == "__main__":
    raise SystemExit(main())
