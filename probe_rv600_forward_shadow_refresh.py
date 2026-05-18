from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from research_particle.kalshi_market_results import fetch_market_results
from research_particle.market_result_labels import build_label_contexts_from_market_results


DEFAULT_REAL_SHADOW_DIR = Path("logs/particle_research/real_shadow")
DEFAULT_NAME_PREFIX = "rv600_forward_shadow_"


@dataclass(frozen=True)
class ForwardRootRefresh:
    root: str
    candidate_snapshots: str
    market_count: int
    result_count: int
    issue_count: int
    labels_written: int
    labels_skipped: int
    market_results: str
    market_result_issues: str
    label_contexts: str


@dataclass(frozen=True)
class ForwardShadowRefreshReport:
    generated_utc: str
    base_dir: str
    roots_scanned: int
    roots_refreshed: int
    total_markets: int
    total_results: int
    total_issues: int
    total_labels_written: int
    rows: tuple[ForwardRootRefresh, ...]


def build_forward_shadow_refresh_report(
    base_dir: Path = DEFAULT_REAL_SHADOW_DIR,
    *,
    name_prefix: str = DEFAULT_NAME_PREFIX,
    base_url: str | None = None,
) -> ForwardShadowRefreshReport:
    roots = tuple(discover_candidate_roots(base_dir, name_prefix=name_prefix))
    rows: list[ForwardRootRefresh] = []
    for root in roots:
        rows.append(refresh_forward_root(root, base_url=base_url))
    return ForwardShadowRefreshReport(
        generated_utc=datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        base_dir=str(base_dir),
        roots_scanned=len(roots),
        roots_refreshed=len(rows),
        total_markets=sum(row.market_count for row in rows),
        total_results=sum(row.result_count for row in rows),
        total_issues=sum(row.issue_count for row in rows),
        total_labels_written=sum(row.labels_written for row in rows),
        rows=tuple(rows),
    )


def discover_candidate_roots(base_dir: Path, *, name_prefix: str = DEFAULT_NAME_PREFIX) -> list[Path]:
    if not base_dir.exists():
        return []
    roots: list[Path] = []
    for path in sorted(base_dir.iterdir(), key=lambda item: item.name):
        if not path.is_dir():
            continue
        if name_prefix and not path.name.startswith(name_prefix):
            continue
        if _candidate_path(path).exists():
            roots.append(path)
    return roots


def refresh_forward_root(root: Path, *, base_url: str | None = None) -> ForwardRootRefresh:
    candidate_path = _candidate_path(root)
    market_results_path = root / "market_results_full_refresh.json"
    market_issues_path = root / "market_result_issues_full_refresh.json"
    label_context_path = _label_path(root)
    tickers = load_candidate_markets(candidate_path)
    if base_url:
        result_count, issue_count = fetch_market_results(
            tickers,
            market_results_path,
            market_issues_path,
            base_url=base_url,
        )
    else:
        result_count, issue_count = fetch_market_results(
            tickers,
            market_results_path,
            market_issues_path,
        )
    labels_written, labels_skipped = build_label_contexts_from_market_results(
        candidate_path,
        market_results_path,
        label_context_path,
    )
    _merge_pipeline_manifest(
        root,
        {
            "market_result_path": str(market_results_path),
            "market_result_issue_path": str(market_issues_path),
            "label_context_path": str(label_context_path),
            "labels_written": labels_written,
            "label_refresh_generated_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        },
    )
    return ForwardRootRefresh(
        root=str(root),
        candidate_snapshots=str(candidate_path),
        market_count=len(tickers),
        result_count=result_count,
        issue_count=issue_count,
        labels_written=labels_written,
        labels_skipped=labels_skipped,
        market_results=str(market_results_path),
        market_result_issues=str(market_issues_path),
        label_contexts=str(label_context_path),
    )


def load_candidate_markets(candidate_path: Path) -> list[str]:
    seen: set[str] = set()
    tickers: list[str] = []
    with candidate_path.open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            payload = json.loads(line)
            snapshot = payload.get("snapshot", payload)
            ticker = str(snapshot.get("market_ticker") or "")
            if ticker and ticker not in seen:
                seen.add(ticker)
                tickers.append(ticker)
    return tickers


def write_report(report: ForwardShadowRefreshReport, output_json: Path, output_md: Path) -> None:
    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_md.parent.mkdir(parents=True, exist_ok=True)
    output_json.write_text(
        json.dumps(_to_jsonable(report), indent=2, sort_keys=True),
        encoding="utf-8",
    )
    output_md.write_text(_markdown(report), encoding="utf-8")


def _merge_pipeline_manifest(root: Path, values: dict[str, Any]) -> None:
    manifest_path = root / "pipeline_work" / "pipeline_manifest.json"
    if not manifest_path.exists():
        return
    try:
        payload = json.loads(manifest_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return
    payload.update(values)
    manifest_path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def _candidate_path(root: Path) -> Path:
    return root / "candidate_snapshots" / "candidate_snapshots.ndjson"


def _label_path(root: Path) -> Path:
    return root / "pipeline_work" / "label_contexts_full_refresh.ndjson"


def _to_jsonable(report: ForwardShadowRefreshReport) -> dict[str, Any]:
    payload = asdict(report)
    payload["rows"] = [asdict(row) for row in report.rows]
    return payload


def _markdown(report: ForwardShadowRefreshReport) -> str:
    lines = [
        "# RV600 Forward Shadow Refresh",
        "",
        f"- generated_utc: {report.generated_utc}",
        f"- base_dir: `{report.base_dir}`",
        f"- roots_scanned: {report.roots_scanned}",
        f"- roots_refreshed: {report.roots_refreshed}",
        f"- total_markets: {report.total_markets}",
        f"- total_results: {report.total_results}",
        f"- total_issues: {report.total_issues}",
        f"- total_labels_written: {report.total_labels_written}",
        "",
        "## Roots",
        "",
        "| root | markets | resolved | issues | labels |",
        "|---|---:|---:|---:|---:|",
    ]
    for row in report.rows:
        lines.append(
            f"| `{row.root}` | {row.market_count} | {row.result_count} | "
            f"{row.issue_count} | {row.labels_written} |"
        )
    lines.append("")
    return "\n".join(lines)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Refresh resolved Kalshi labels for RV600 forward-shadow research roots."
    )
    parser.add_argument("--base-dir", type=Path, default=DEFAULT_REAL_SHADOW_DIR)
    parser.add_argument("--name-prefix", default=DEFAULT_NAME_PREFIX)
    parser.add_argument("--base-url", default=None)
    parser.add_argument(
        "--output-json",
        type=Path,
        default=Path("logs/particle_research/reports/rv600_forward_shadow_refresh_latest.json"),
    )
    parser.add_argument(
        "--output-md",
        type=Path,
        default=Path("logs/particle_research/reports/rv600_forward_shadow_refresh_latest.md"),
    )
    parser.add_argument("--write", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    report = build_forward_shadow_refresh_report(
        args.base_dir,
        name_prefix=args.name_prefix,
        base_url=args.base_url,
    )
    if args.write:
        write_report(report, args.output_json, args.output_md)
    print(f"roots_refreshed={report.roots_refreshed}")
    print(f"total_markets={report.total_markets}")
    print(f"total_results={report.total_results}")
    print(f"total_issues={report.total_issues}")
    print(f"total_labels_written={report.total_labels_written}")
    if args.write:
        print(f"output_json={args.output_json}")
        print(f"output_md={args.output_md}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
