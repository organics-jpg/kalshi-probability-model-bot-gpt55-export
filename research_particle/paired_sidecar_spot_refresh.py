from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass, replace
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

from probe_particle_goal_completion_audit import audit as particle_goal_audit
from probe_particle_goal_completion_audit import write_report as write_particle_goal_audit
from run_v28_successor_sidecar_collection_cycle import run_cycle as run_sidecar_cycle
from run_v28_successor_sidecar_collection_cycle import write_outputs as write_sidecar_cycle_outputs

from .paired_sidecar_spot_aggregate import (
    DEFAULT_INPUT_ROOT,
    DEFAULT_OUTPUT_JSON as DEFAULT_AGGREGATE_JSON,
    DEFAULT_OUTPUT_MD as DEFAULT_AGGREGATE_MD,
    build_paired_sidecar_spot_aggregate,
    write_paired_sidecar_spot_aggregate,
)
from .paired_sidecar_spot_diagnostic import (
    DEFAULT_LABELED_CSV,
    build_sidecar_spot_diagnostic,
    write_sidecar_spot_diagnostic,
)
from .paired_sidecar_spot_enrichment import (
    DEFAULT_PACKET_CSV,
    build_enriched_sidecar_spot_packets,
    write_enrichment_outputs,
)


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_REFRESH_JSON = ROOT / "logs" / "particle_research" / "reports" / "paired_sidecar_spot_refresh_latest.json"
DEFAULT_REFRESH_MD = ROOT / "logs" / "particle_research" / "reports" / "paired_sidecar_spot_refresh_latest.md"


@dataclass(frozen=True)
class PairedSidecarSpotRefreshSummary:
    schema_version: str
    generated_utc: str
    promotion_allowed: bool
    promotion_status: Mapping[str, Any]
    label_refresh_requested: bool
    label_refresh_status: str
    label_refresh_written: bool
    input_root: str
    packet_csv: str
    labeled_csv: str
    output_json: str
    output_md: str
    manifest_count: int
    skipped_manifest_count: int
    enrichment_ready_count: int
    diagnostic_ready_count: int
    pending_diagnostic_count: int
    aggregate_ready: bool
    aggregate_fresh: bool
    aggregate_joined_rows: int
    aggregate_joined_markets: int
    aggregate_candidate_ready: bool
    aggregate_rows_remaining_for_shadow: int
    aggregate_markets_remaining_for_shadow: int
    aggregate_best_model_by_brier: str
    aggregate_best_model_by_logloss: str
    goal_audit_refreshed: bool
    goal_complete: bool


def refresh_paired_sidecar_spot_evidence(
    *,
    input_root: Path = DEFAULT_INPUT_ROOT,
    packet_csv: Path = DEFAULT_PACKET_CSV,
    labeled_csv: Path = DEFAULT_LABELED_CSV,
    output_json: Path = DEFAULT_REFRESH_JSON,
    output_md: Path = DEFAULT_REFRESH_MD,
    write: bool = False,
    refresh_goal_audit: bool = True,
    fetch_labels: bool = False,
    label_timeout_seconds: float = 10.0,
) -> tuple[PairedSidecarSpotRefreshSummary, list[dict[str, Any]]]:
    aggregate_output_json = DEFAULT_AGGREGATE_JSON
    aggregate_output_md = DEFAULT_AGGREGATE_MD
    if Path(output_json) != DEFAULT_REFRESH_JSON:
        aggregate_output_json = Path(output_json).parent / DEFAULT_AGGREGATE_JSON.name
    if Path(output_md) != DEFAULT_REFRESH_MD:
        aggregate_output_md = Path(output_md).parent / DEFAULT_AGGREGATE_MD.name

    label_refresh_status = "not_requested"
    if fetch_labels:
        label_cycle_report = run_sidecar_cycle(
            collect_mode="none",
            timeout_seconds=label_timeout_seconds,
            max_markets=80,
            nearest_close_only=True,
            write=write,
            skip_label_fetch=False,
            refresh_downstream_audits=False,
        )
        if write:
            write_sidecar_cycle_outputs(label_cycle_report)
        label_refresh_status = str((label_cycle_report.get("summary") or {}).get("cycle_status") or "unknown")

    manifests = sorted(input_root.glob("*/paired_sidecar_spot_manifest.json"))
    rows: list[dict[str, Any]] = []
    skipped_manifest_count = 0
    enrichment_ready_count = 0
    diagnostic_ready_count = 0
    for manifest in manifests:
        manifest_payload = _load_json(manifest)
        manifest_summary = _summary_from_payload(manifest_payload)
        if not bool(manifest_summary.get("paired_capture_ready")):
            skipped_manifest_count += 1
            rows.append(
                {
                    "manifest": str(manifest),
                    "run_id": str(manifest_summary.get("run_id") or manifest.parent.name),
                    "enrichment_ready": False,
                    "enriched_packet_rows": 0,
                    "enrichment_issue_count": int(manifest_summary.get("alignment_issue_count", 0) or 0),
                    "diagnostic_ready": False,
                    "diagnostic_joined_rows": 0,
                    "diagnostic_joined_markets": 0,
                    "skipped_reason": "paired_capture_not_ready",
                }
            )
            continue
        consistency_issue = _paired_manifest_consistency_issue(manifest_payload)
        if consistency_issue:
            skipped_manifest_count += 1
            rows.append(
                {
                    "manifest": str(manifest),
                    "run_id": str(manifest_summary.get("run_id") or manifest.parent.name),
                    "enrichment_ready": False,
                    "enriched_packet_rows": 0,
                    "enrichment_issue_count": 1,
                    "diagnostic_ready": False,
                    "diagnostic_joined_rows": 0,
                    "diagnostic_joined_markets": 0,
                    "skipped_reason": consistency_issue,
                }
            )
            continue
        enrichment_summary, enrichment_rows = build_enriched_sidecar_spot_packets(
            manifest_path=manifest,
            packet_csv=packet_csv,
        )
        if write:
            write_enrichment_outputs(enrichment_summary, enrichment_rows)
        if enrichment_summary.enrichment_ready:
            enrichment_ready_count += 1

        diagnostic_summary = None
        if write:
            diagnostic_summary, model_rows, diagnostic_rows = build_sidecar_spot_diagnostic(
                enriched_csv=Path(enrichment_summary.output_csv),
                labeled_csv=labeled_csv,
            )
            write_sidecar_spot_diagnostic(diagnostic_summary, model_rows, diagnostic_rows)
            if diagnostic_summary.diagnostic_ready:
                diagnostic_ready_count += 1
        rows.append(
            {
                "manifest": str(manifest),
                "run_id": enrichment_summary.run_id,
                "enrichment_ready": enrichment_summary.enrichment_ready,
                "enriched_packet_rows": enrichment_summary.enriched_packet_rows,
                "enrichment_issue_count": enrichment_summary.issue_count,
                "diagnostic_ready": bool(diagnostic_summary and diagnostic_summary.diagnostic_ready),
                "diagnostic_joined_rows": 0 if diagnostic_summary is None else diagnostic_summary.joined_rows,
                "diagnostic_joined_markets": 0 if diagnostic_summary is None else diagnostic_summary.joined_markets,
                "skipped_reason": "",
            }
        )

    aggregate_summary, aggregate_model_rows, aggregate_diagnostic_rows = build_paired_sidecar_spot_aggregate(
        input_root=input_root,
        output_json=aggregate_output_json,
        output_md=aggregate_output_md,
    )
    if write:
        write_paired_sidecar_spot_aggregate(
            aggregate_summary,
            aggregate_model_rows,
            aggregate_diagnostic_rows,
        )
    actual_diagnostic_count = len(list(input_root.glob("*/sidecar_spot_tick_vs_candle_diagnostic.json")))
    aggregate_fresh = aggregate_summary.diagnostic_file_count == actual_diagnostic_count

    summary = PairedSidecarSpotRefreshSummary(
        schema_version="paired-sidecar-spot-refresh-v1",
        generated_utc=datetime.now(timezone.utc).isoformat(),
        promotion_allowed=False,
        promotion_status={
            "allowed": False,
            "reason": "paired sidecar spot refresh only rewrites research diagnostics and cannot promote trading",
        },
        label_refresh_requested=bool(fetch_labels),
        label_refresh_status=label_refresh_status,
        label_refresh_written=bool(fetch_labels and write),
        input_root=str(input_root),
        packet_csv=str(packet_csv),
        labeled_csv=str(labeled_csv),
        output_json=str(output_json),
        output_md=str(output_md),
        manifest_count=len(manifests),
        skipped_manifest_count=skipped_manifest_count,
        enrichment_ready_count=enrichment_ready_count,
        diagnostic_ready_count=diagnostic_ready_count,
        pending_diagnostic_count=max(0, len(manifests) - skipped_manifest_count - diagnostic_ready_count),
        aggregate_ready=aggregate_summary.diagnostic_ready,
        aggregate_fresh=aggregate_fresh,
        aggregate_joined_rows=aggregate_summary.joined_rows,
        aggregate_joined_markets=aggregate_summary.joined_markets,
        aggregate_candidate_ready=aggregate_summary.candidate_ready_for_predeclared_shadow,
        aggregate_rows_remaining_for_shadow=aggregate_summary.rows_remaining_for_shadow,
        aggregate_markets_remaining_for_shadow=aggregate_summary.markets_remaining_for_shadow,
        aggregate_best_model_by_brier=aggregate_summary.best_model_by_brier,
        aggregate_best_model_by_logloss=aggregate_summary.best_model_by_logloss,
        goal_audit_refreshed=False,
        goal_complete=False,
    )
    if write and refresh_goal_audit:
        write_refresh_outputs(summary, rows)
        goal_payload = particle_goal_audit(ROOT)
        write_particle_goal_audit(goal_payload)
        summary = replace(
            summary,
            goal_audit_refreshed=True,
            goal_complete=bool(goal_payload.get("complete")),
        )
        write_refresh_outputs(summary, rows)
    return summary, rows


def write_refresh_outputs(summary: PairedSidecarSpotRefreshSummary, rows: list[dict[str, Any]]) -> None:
    output_json = Path(summary.output_json)
    output_md = Path(summary.output_md)
    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_md.parent.mkdir(parents=True, exist_ok=True)
    output_json.write_text(
        json.dumps({"summary": asdict(summary), "rows": rows}, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    output_md.write_text(_markdown(summary, rows), encoding="utf-8")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Refresh research-only paired sidecar/spot enrichment, diagnostics, aggregate, and goal audit."
    )
    parser.add_argument("--input-root", type=Path, default=DEFAULT_INPUT_ROOT)
    parser.add_argument("--packet-csv", type=Path, default=DEFAULT_PACKET_CSV)
    parser.add_argument("--labeled-csv", type=Path, default=DEFAULT_LABELED_CSV)
    parser.add_argument("--output-json", type=Path, default=DEFAULT_REFRESH_JSON)
    parser.add_argument("--output-md", type=Path, default=DEFAULT_REFRESH_MD)
    parser.add_argument(
        "--fetch-labels",
        action="store_true",
        help="Before paired diagnostics, refresh sidecar settlement labels using collect_mode=none. This is research-only and does not collect new pre-close snapshots.",
    )
    parser.add_argument("--label-timeout-seconds", type=float, default=10.0)
    parser.add_argument("--skip-goal-audit", action="store_true")
    parser.add_argument("--write", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    summary, rows = refresh_paired_sidecar_spot_evidence(
        input_root=args.input_root,
        packet_csv=args.packet_csv,
        labeled_csv=args.labeled_csv,
        output_json=args.output_json,
        output_md=args.output_md,
        write=bool(args.write),
        refresh_goal_audit=not bool(args.skip_goal_audit),
        fetch_labels=bool(args.fetch_labels),
        label_timeout_seconds=float(args.label_timeout_seconds),
    )
    if args.write:
        write_refresh_outputs(summary, rows)
    print(f"manifest_count={summary.manifest_count}")
    print(f"label_refresh_requested={summary.label_refresh_requested}")
    print(f"label_refresh_status={summary.label_refresh_status}")
    print(f"label_refresh_written={summary.label_refresh_written}")
    print(f"skipped_manifest_count={summary.skipped_manifest_count}")
    print(f"enrichment_ready_count={summary.enrichment_ready_count}")
    print(f"diagnostic_ready_count={summary.diagnostic_ready_count}")
    print(f"pending_diagnostic_count={summary.pending_diagnostic_count}")
    print(f"aggregate_ready={summary.aggregate_ready}")
    print(f"aggregate_fresh={summary.aggregate_fresh}")
    print(f"aggregate_joined_rows={summary.aggregate_joined_rows}")
    print(f"aggregate_joined_markets={summary.aggregate_joined_markets}")
    print(f"aggregate_candidate_ready={summary.aggregate_candidate_ready}")
    print(f"aggregate_rows_remaining_for_shadow={summary.aggregate_rows_remaining_for_shadow}")
    print(f"aggregate_markets_remaining_for_shadow={summary.aggregate_markets_remaining_for_shadow}")
    print(f"promotion_allowed={summary.promotion_allowed}")
    print(f"goal_complete={summary.goal_complete}")
    print(f"output_json={summary.output_json}")
    return 0


def _markdown(summary: PairedSidecarSpotRefreshSummary, rows: list[dict[str, Any]]) -> str:
    lines = [
        "# Paired Sidecar Spot Refresh",
        "",
        "Research-only refresh of existing paired sidecar/independent-spot artifacts. It does not collect new pre-close market snapshots, place orders, or touch live bot state.",
        "",
        "## Summary",
        "",
        f"- Generated UTC: `{summary.generated_utc}`",
        f"- Promotion allowed: `{summary.promotion_allowed}`",
        f"- Label refresh requested/status/written: `{summary.label_refresh_requested}` / `{summary.label_refresh_status}` / `{summary.label_refresh_written}`",
        f"- Manifests: `{summary.manifest_count}`",
        f"- Skipped manifests: `{summary.skipped_manifest_count}`",
        f"- Enrichment ready: `{summary.enrichment_ready_count}`",
        f"- Diagnostics ready: `{summary.diagnostic_ready_count}`",
        f"- Pending diagnostics: `{summary.pending_diagnostic_count}`",
        f"- Aggregate ready/fresh: `{summary.aggregate_ready}` / `{summary.aggregate_fresh}`",
        f"- Aggregate joined rows / markets: `{summary.aggregate_joined_rows}` / `{summary.aggregate_joined_markets}`",
        f"- Aggregate candidate ready: `{summary.aggregate_candidate_ready}`",
        f"- Aggregate rows / markets remaining: `{summary.aggregate_rows_remaining_for_shadow}` / `{summary.aggregate_markets_remaining_for_shadow}`",
        f"- Aggregate best Brier/log loss: `{summary.aggregate_best_model_by_brier}` / `{summary.aggregate_best_model_by_logloss}`",
        f"- Goal audit refreshed/complete: `{summary.goal_audit_refreshed}` / `{summary.goal_complete}`",
        "",
        "## Manifests",
        "",
        "| run | enrichment ready | enriched rows | enrichment issues | diagnostic ready | joined rows | joined markets | skipped reason |",
        "|---|---:|---:|---:|---:|---:|---:|---|",
    ]
    for row in rows:
        lines.append(
            f"| `{row.get('run_id', '')}` | `{row.get('enrichment_ready')}` | "
            f"{row.get('enriched_packet_rows', 0)} | {row.get('enrichment_issue_count', 0)} | "
            f"`{row.get('diagnostic_ready')}` | {row.get('diagnostic_joined_rows', 0)} | "
            f"{row.get('diagnostic_joined_markets', 0)} | `{row.get('skipped_reason', '')}` |"
        )
    lines.extend(
        [
            "",
            "## Read",
            "",
            "- This is a maintenance/reporting command for existing research artifacts only.",
            "- `aggregate_candidate_ready=True` is only a coverage floor for later predeclared shadow tests, never a live-trading approval.",
        ]
    )
    return "\n".join(lines) + "\n"


def _load_json(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return payload if isinstance(payload, dict) else {}


def _summary_from_payload(payload: Mapping[str, Any]) -> Mapping[str, Any]:
    summary = payload.get("summary")
    return summary if isinstance(summary, Mapping) else payload


def _paired_manifest_consistency_issue(payload: Mapping[str, Any]) -> str:
    summary = _summary_from_payload(payload)
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


if __name__ == "__main__":
    raise SystemExit(main())
