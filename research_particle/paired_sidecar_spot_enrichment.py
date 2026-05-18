from __future__ import annotations

import argparse
import csv
import json
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable, Mapping

from .spot_context_merge import SpotTickRow, load_spot_ticks


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PACKET_CSV = ROOT / "research_particle" / "v28_successor" / "sidecar_bundle_batch_packets_latest.csv"

ENRICHED_FIELDS = [
    "sidecar_spot_pair_run_id",
    "sidecar_spot_pair_manifest",
    "sidecar_spot_pair_bundle_matched",
    "independent_spot_ready",
    "independent_spot_price",
    "independent_spot_source",
    "independent_spot_available_ts_utc",
    "independent_spot_exchange_ts_utc",
    "independent_spot_age_ms",
    "independent_spot_vs_candle_bps",
    "independent_spot_issue",
]


@dataclass(frozen=True)
class PairedSidecarSpotEnrichmentSummary:
    schema_version: str
    generated_utc: str
    promotion_allowed: bool
    promotion_status: Mapping[str, Any]
    manifest_path: str
    packet_csv: str
    spot_path: str
    output_csv: str
    output_json: str
    output_md: str
    run_id: str
    spot_max_age_ms: float
    packet_rows_read: int
    matching_packet_rows: int
    enriched_packet_rows: int
    issue_count: int
    matched_bundle_count: int
    spot_tick_count: int
    enrichment_ready: bool


def build_enriched_sidecar_spot_packets(
    *,
    manifest_path: Path,
    packet_csv: Path = DEFAULT_PACKET_CSV,
    output_csv: Path | None = None,
    output_json: Path | None = None,
    output_md: Path | None = None,
    spot_max_age_ms: float | None = None,
    workspace: Path = ROOT,
) -> tuple[PairedSidecarSpotEnrichmentSummary, list[dict[str, Any]]]:
    manifest = _load_json(manifest_path)
    manifest_summary = _summary(manifest)
    artifact_root = Path(str(manifest_summary.get("artifact_root") or manifest_path.parent))
    output_csv = output_csv or artifact_root / "sidecar_packets_independent_spot_enriched.csv"
    output_json = output_json or artifact_root / "sidecar_packets_independent_spot_enriched.json"
    output_md = output_md or artifact_root / "sidecar_packets_independent_spot_enriched.md"
    spot_path = Path(str(manifest_summary.get("spot_output") or artifact_root / "spot_ticks.ndjson"))
    max_age = float(spot_max_age_ms if spot_max_age_ms is not None else manifest_summary.get("spot_max_age_ms", 2_000.0) or 2_000.0)
    bundle_keys = _manifest_bundle_keys(manifest, workspace=workspace)
    ticks = load_spot_ticks(spot_path) if spot_path.exists() else []
    packet_rows = _read_csv_rows(packet_csv)
    out_rows: list[dict[str, Any]] = []
    issue_count = 0
    enriched_count = 0

    for row in packet_rows:
        if not _row_matches_bundle(row, bundle_keys, workspace=workspace):
            continue
        enriched = dict(row)
        decision_ts = _parse_dt(row.get("decision_ts_utc"))
        tick = _latest_spot_tick(ticks, decision_ts) if decision_ts is not None else None
        issue = ""
        age_ms = None
        if decision_ts is None:
            issue = "missing_packet_decision_ts"
        elif tick is None:
            issue = "no_independent_spot_tick_at_or_before_packet_decision"
        else:
            age_ms = 1000.0 * (decision_ts - tick.available_ts_utc).total_seconds()
            if age_ms > max_age:
                issue = f"latest_independent_spot_tick_too_old_ms={age_ms:.3f}"
        ready = tick is not None and age_ms is not None and age_ms <= max_age and not issue
        if ready:
            enriched_count += 1
        else:
            issue_count += 1
        candle_spot = _as_float(row.get("btc_spot"))
        delta_bps = (
            10_000.0 * (tick.price - candle_spot) / candle_spot
            if tick is not None and candle_spot not in (None, 0.0)
            else None
        )
        enriched.update(
            {
                "sidecar_spot_pair_run_id": manifest_summary.get("run_id", ""),
                "sidecar_spot_pair_manifest": _rel_path(manifest_path, workspace),
                "sidecar_spot_pair_bundle_matched": "True",
                "independent_spot_ready": "True" if ready else "False",
                "independent_spot_price": "" if tick is None else f"{tick.price:.8f}",
                "independent_spot_source": "" if tick is None else tick.source,
                "independent_spot_available_ts_utc": "" if tick is None else tick.available_ts_utc.isoformat(),
                "independent_spot_exchange_ts_utc": "" if tick is None else tick.exchange_ts_utc.isoformat(),
                "independent_spot_age_ms": "" if age_ms is None else f"{age_ms:.3f}",
                "independent_spot_vs_candle_bps": "" if delta_bps is None else f"{delta_bps:.6f}",
                "independent_spot_issue": issue,
            }
        )
        out_rows.append(enriched)

    summary = PairedSidecarSpotEnrichmentSummary(
        schema_version="paired-sidecar-spot-enrichment-v1",
        generated_utc=datetime.now(timezone.utc).isoformat(),
        promotion_allowed=False,
        promotion_status={
            "allowed": False,
            "reason": "sidecar spot enrichment is timestamp-available instrumentation only; promotion still requires locked OOS probability, EV-rank, and PnL gates",
        },
        manifest_path=str(manifest_path),
        packet_csv=str(packet_csv),
        spot_path=str(spot_path),
        output_csv=str(output_csv),
        output_json=str(output_json),
        output_md=str(output_md),
        run_id=str(manifest_summary.get("run_id") or ""),
        spot_max_age_ms=max_age,
        packet_rows_read=len(packet_rows),
        matching_packet_rows=len(out_rows),
        enriched_packet_rows=enriched_count,
        issue_count=issue_count,
        matched_bundle_count=len(bundle_keys),
        spot_tick_count=len(ticks),
        enrichment_ready=bool(out_rows) and enriched_count == len(out_rows),
    )
    return summary, out_rows


def write_enrichment_outputs(summary: PairedSidecarSpotEnrichmentSummary, rows: list[dict[str, Any]]) -> None:
    output_csv = Path(summary.output_csv)
    output_json = Path(summary.output_json)
    output_md = Path(summary.output_md)
    output_csv.parent.mkdir(parents=True, exist_ok=True)
    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_md.parent.mkdir(parents=True, exist_ok=True)
    _write_csv_rows(rows, _fieldnames(rows), output_csv)
    output_json.write_text(
        json.dumps({"summary": asdict(summary), "rows": rows}, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    output_md.write_text(_markdown(summary, rows), encoding="utf-8")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Enrich paired sidecar packet rows with latest no-future independent spot ticks."
    )
    parser.add_argument("--manifest", required=True, type=Path)
    parser.add_argument("--packet-csv", type=Path, default=DEFAULT_PACKET_CSV)
    parser.add_argument("--output-csv", type=Path, default=None)
    parser.add_argument("--output-json", type=Path, default=None)
    parser.add_argument("--output-md", type=Path, default=None)
    parser.add_argument("--spot-max-age-ms", type=float, default=None)
    parser.add_argument("--write", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    summary, rows = build_enriched_sidecar_spot_packets(
        manifest_path=args.manifest,
        packet_csv=args.packet_csv,
        output_csv=args.output_csv,
        output_json=args.output_json,
        output_md=args.output_md,
        spot_max_age_ms=args.spot_max_age_ms,
    )
    if args.write:
        write_enrichment_outputs(summary, rows)
    print(f"enrichment_ready={summary.enrichment_ready}")
    print(f"matching_packet_rows={summary.matching_packet_rows}")
    print(f"enriched_packet_rows={summary.enriched_packet_rows}")
    print(f"issue_count={summary.issue_count}")
    print(f"promotion_allowed={summary.promotion_allowed}")
    print(f"output_csv={summary.output_csv}")
    return 0


def _summary(manifest: Mapping[str, Any]) -> Mapping[str, Any]:
    summary = manifest.get("summary")
    return summary if isinstance(summary, Mapping) else manifest


def _manifest_bundle_keys(manifest: Mapping[str, Any], *, workspace: Path) -> set[str]:
    keys: set[str] = set()
    for row in manifest.get("alignment_rows") or []:
        if not isinstance(row, Mapping):
            continue
        keys.update(_path_keys(row.get("bundle_path"), workspace=workspace))
    for row in manifest.get("sidecar_batch_markets") or []:
        if not isinstance(row, Mapping):
            continue
        keys.update(_path_keys(row.get("output_bundle_json"), workspace=workspace))
    return {key for key in keys if key}


def _row_matches_bundle(row: Mapping[str, Any], bundle_keys: set[str], *, workspace: Path) -> bool:
    return bool(_path_keys(row.get("source_file"), workspace=workspace) & bundle_keys)


def _path_keys(value: Any, *, workspace: Path) -> set[str]:
    text = str(value or "").strip().replace("\\", "/")
    if not text:
        return set()
    path = Path(text)
    keys = {text, text.lower()}
    try:
        resolved = path if path.is_absolute() else workspace / path
        keys.add(str(resolved.resolve()).replace("\\", "/"))
        keys.add(str(resolved.resolve()).replace("\\", "/").lower())
        try:
            rel = str(resolved.resolve().relative_to(workspace.resolve())).replace("\\", "/")
            keys.add(rel)
            keys.add(rel.lower())
        except ValueError:
            pass
    except Exception:  # noqa: BLE001
        pass
    return keys


def _latest_spot_tick(ticks: list[SpotTickRow], decision_ts: datetime) -> SpotTickRow | None:
    selected = None
    for tick in ticks:
        if tick.available_ts_utc <= decision_ts:
            selected = tick
        else:
            break
    return selected


def _read_csv_rows(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8", newline="") as handle:
        return [dict(row) for row in csv.DictReader(handle)]


def _write_csv_rows(rows: list[dict[str, Any]], fieldnames: list[str], path: Path) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def _fieldnames(rows: list[dict[str, Any]]) -> list[str]:
    return list(dict.fromkeys([key for row in rows for key in row.keys()] + ENRICHED_FIELDS))


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


def _as_float(value: Any) -> float | None:
    try:
        parsed = float(str(value).strip())
    except (TypeError, ValueError):
        return None
    return parsed


def _rel_path(path: Path, workspace: Path) -> str:
    try:
        return str(path.resolve().relative_to(workspace.resolve())).replace("\\", "/")
    except ValueError:
        return str(path)


def _markdown(summary: PairedSidecarSpotEnrichmentSummary, rows: list[dict[str, Any]]) -> str:
    lines = [
        "# Paired Sidecar Spot Packet Enrichment",
        "",
        "Research-only enrichment of sidecar packet rows with independent public BTC spot ticks available at or before each packet decision timestamp.",
        "",
        "## Summary",
        "",
        f"- Generated UTC: `{summary.generated_utc}`",
        f"- Run id: `{summary.run_id}`",
        f"- Promotion allowed: `{summary.promotion_allowed}`",
        f"- Enrichment ready: `{summary.enrichment_ready}`",
        f"- Packet rows read: `{summary.packet_rows_read}`",
        f"- Matching packet rows: `{summary.matching_packet_rows}`",
        f"- Enriched packet rows: `{summary.enriched_packet_rows}`",
        f"- Issue count: `{summary.issue_count}`",
        f"- Spot ticks: `{summary.spot_tick_count}`",
        "",
        "## Rows",
        "",
        "| market | side | candidate | decision ts | independent spot | age ms | delta vs candle bps | ready | issue |",
        "|---|---|---|---|---:|---:|---:|---|---|",
    ]
    for row in rows[:50]:
        lines.append(
            f"| `{row.get('market_ticker', '')}` | `{row.get('side', '')}` | `{row.get('candidate_id', '')}` | "
            f"`{row.get('decision_ts_utc', '')}` | {row.get('independent_spot_price', '')} | "
            f"{row.get('independent_spot_age_ms', '')} | {row.get('independent_spot_vs_candle_bps', '')} | "
            f"`{row.get('independent_spot_ready', '')}` | `{row.get('independent_spot_issue', '')}` |"
        )
    if len(rows) > 50:
        lines.append(f"| ... | ... | ... | ... | ... | ... | ... | ... | `{len(rows) - 50} more rows omitted` |")
    if not rows:
        lines.append("|  |  |  |  |  |  |  | `False` | `no matching packet rows` |")
    lines.extend(
        [
            "",
            "## Read",
            "",
            "- This artifact does not modify frozen sidecar rows or any live bot state.",
            "- It is input-quality evidence only; probability, EV ranking, PnL, and promotion gates remain separate.",
        ]
    )
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    raise SystemExit(main())
