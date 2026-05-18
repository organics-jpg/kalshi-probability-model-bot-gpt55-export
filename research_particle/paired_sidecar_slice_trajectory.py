from __future__ import annotations

import argparse
import json
import re
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping, Sequence


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MARKET_BREAKDOWN_JSON = (
    ROOT / "logs" / "particle_research" / "reports" / "paired_sidecar_slice_market_breakdown_latest.json"
)
DEFAULT_OUTPUT_JSON = (
    ROOT / "logs" / "particle_research" / "reports" / "paired_sidecar_slice_trajectory_latest.json"
)
DEFAULT_OUTPUT_MD = (
    ROOT / "logs" / "particle_research" / "reports" / "paired_sidecar_slice_trajectory_latest.md"
)

MONTHS = {
    "JAN": 1,
    "FEB": 2,
    "MAR": 3,
    "APR": 4,
    "MAY": 5,
    "JUN": 6,
    "JUL": 7,
    "AUG": 8,
    "SEP": 9,
    "OCT": 10,
    "NOV": 11,
    "DEC": 12,
}


@dataclass(frozen=True)
class SliceTrajectoryPoint:
    market_ticker: str
    market_close_utc: str
    selected_pnl_cents: float
    selected_pnl_delta_vs_v28_cents: float | None
    running_selected_pnl_cents: float
    running_selected_pnl_delta_vs_v28_cents: float | None


@dataclass(frozen=True)
class SliceTrajectoryRow:
    hypothesis_id: str
    model: str
    bucket: str
    particle_like_model: bool
    market_count: int
    selected_pnl_cents: float
    selected_pnl_delta_vs_v28_cents: float | None
    last_n_market_count: int
    last_n_selected_pnl_cents: float
    last_n_selected_pnl_delta_vs_v28_cents: float | None
    positive_market_count: int
    positive_last_n_market_count: int
    max_drawdown_cents: float
    final_running_peak_cents: float
    final_running_trough_cents: float
    first_market_ticker: str
    last_market_ticker: str
    trajectory_warnings: tuple[str, ...]
    trajectory_screen_pass: bool
    points: tuple[SliceTrajectoryPoint, ...]


@dataclass(frozen=True)
class SliceTrajectoryReport:
    schema_version: str
    generated_utc: str
    promotion_allowed: bool
    promotion_status: Mapping[str, Any]
    input_market_breakdown_json: str
    output_json: str
    output_md: str
    min_markets: int
    recent_market_count: int
    max_drawdown_multiple: float
    row_count: int
    particle_like_count: int
    trajectory_screen_pass_count: int
    particle_like_trajectory_screen_pass_count: int
    worst_recent_hypothesis_id: str
    worst_recent_selected_pnl_cents: float
    rows: tuple[SliceTrajectoryRow, ...]
    conclusion: str


def build_slice_trajectory_report(
    *,
    market_breakdown_json: Path = DEFAULT_MARKET_BREAKDOWN_JSON,
    output_json: Path = DEFAULT_OUTPUT_JSON,
    output_md: Path = DEFAULT_OUTPUT_MD,
    min_markets: int = 20,
    recent_market_count: int = 5,
    max_drawdown_multiple: float = 1.50,
) -> SliceTrajectoryReport:
    payload = _load_json(market_breakdown_json)
    market_rows = [_mapping(row) for row in payload.get("rows") or []]
    grouped: dict[tuple[str, str, str], list[Mapping[str, Any]]] = {}
    for row in market_rows:
        key = (
            str(row.get("hypothesis_id") or ""),
            str(row.get("model") or ""),
            str(row.get("bucket") or ""),
        )
        grouped.setdefault(key, []).append(row)
    rows = tuple(
        _trajectory_row(
            hypothesis_id=hypothesis_id,
            model=model,
            bucket=bucket,
            rows=items,
            min_markets=min_markets,
            recent_market_count=recent_market_count,
            max_drawdown_multiple=max_drawdown_multiple,
        )
        for (hypothesis_id, model, bucket), items in sorted(grouped.items())
    )
    particle_rows = [row for row in rows if row.particle_like_model]
    worst_recent = min(particle_rows, key=lambda row: row.last_n_selected_pnl_cents, default=None)
    return SliceTrajectoryReport(
        schema_version="paired-sidecar-slice-trajectory-v1",
        generated_utc=datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        promotion_allowed=False,
        promotion_status={
            "allowed": False,
            "reason": "slice trajectory is diagnostic only and cannot approve live trading",
        },
        input_market_breakdown_json=str(market_breakdown_json),
        output_json=str(output_json),
        output_md=str(output_md),
        min_markets=min_markets,
        recent_market_count=recent_market_count,
        max_drawdown_multiple=max_drawdown_multiple,
        row_count=len(rows),
        particle_like_count=len(particle_rows),
        trajectory_screen_pass_count=sum(1 for row in rows if row.trajectory_screen_pass),
        particle_like_trajectory_screen_pass_count=sum(
            1 for row in particle_rows if row.trajectory_screen_pass
        ),
        worst_recent_hypothesis_id="" if worst_recent is None else worst_recent.hypothesis_id,
        worst_recent_selected_pnl_cents=0.0 if worst_recent is None else worst_recent.last_n_selected_pnl_cents,
        rows=rows,
        conclusion=_conclusion(rows, particle_rows),
    )


def write_slice_trajectory_report(report: SliceTrajectoryReport) -> None:
    output_json = Path(report.output_json)
    output_md = Path(report.output_md)
    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_md.parent.mkdir(parents=True, exist_ok=True)
    output_json.write_text(json.dumps(asdict(report), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    output_md.write_text(_markdown(report), encoding="utf-8")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Summarize market-by-market trajectories for frozen paired sidecar slice locks."
    )
    parser.add_argument("--market-breakdown-json", type=Path, default=DEFAULT_MARKET_BREAKDOWN_JSON)
    parser.add_argument("--output-json", type=Path, default=DEFAULT_OUTPUT_JSON)
    parser.add_argument("--output-md", type=Path, default=DEFAULT_OUTPUT_MD)
    parser.add_argument("--min-markets", type=int, default=20)
    parser.add_argument("--recent-market-count", type=int, default=5)
    parser.add_argument("--max-drawdown-multiple", type=float, default=1.50)
    parser.add_argument("--write", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    report = build_slice_trajectory_report(
        market_breakdown_json=args.market_breakdown_json,
        output_json=args.output_json,
        output_md=args.output_md,
        min_markets=args.min_markets,
        recent_market_count=args.recent_market_count,
        max_drawdown_multiple=args.max_drawdown_multiple,
    )
    if args.write:
        write_slice_trajectory_report(report)
    print(f"promotion_allowed={report.promotion_allowed}")
    print(f"row_count={report.row_count}")
    print(f"particle_like_count={report.particle_like_count}")
    print(f"trajectory_screen_pass_count={report.trajectory_screen_pass_count}")
    print(f"particle_like_trajectory_screen_pass_count={report.particle_like_trajectory_screen_pass_count}")
    print(f"worst_recent_hypothesis_id={report.worst_recent_hypothesis_id}")
    print(f"worst_recent_selected_pnl_cents={report.worst_recent_selected_pnl_cents:.4f}")
    print(f"conclusion={report.conclusion}")
    print(f"output_json={report.output_json}")
    return 0


def _trajectory_row(
    *,
    hypothesis_id: str,
    model: str,
    bucket: str,
    rows: Sequence[Mapping[str, Any]],
    min_markets: int,
    recent_market_count: int,
    max_drawdown_multiple: float,
) -> SliceTrajectoryRow:
    ordered = sorted(rows, key=lambda row: (_market_close_utc(str(row.get("market_ticker") or "")), str(row.get("market_ticker") or "")))
    points: list[SliceTrajectoryPoint] = []
    running = 0.0
    running_delta = 0.0
    has_delta = any(row.get("selected_pnl_delta_vs_v28_cents") is not None for row in ordered)
    peak = 0.0
    trough = 0.0
    max_drawdown = 0.0
    for row in ordered:
        pnl = _float(row.get("selected_pnl_cents"))
        delta = row.get("selected_pnl_delta_vs_v28_cents")
        parsed_delta = None if delta is None else _float(delta)
        running += pnl
        if parsed_delta is not None:
            running_delta += parsed_delta
        peak = max(peak, running)
        trough = min(trough, running)
        max_drawdown = max(max_drawdown, peak - running)
        points.append(
            SliceTrajectoryPoint(
                market_ticker=str(row.get("market_ticker") or ""),
                market_close_utc=_market_close_utc(str(row.get("market_ticker") or "")),
                selected_pnl_cents=pnl,
                selected_pnl_delta_vs_v28_cents=parsed_delta,
                running_selected_pnl_cents=running,
                running_selected_pnl_delta_vs_v28_cents=running_delta if has_delta else None,
            )
        )
    recent_n = max(1, recent_market_count)
    recent_points = points[-recent_n:]
    recent_delta_values = [
        point.selected_pnl_delta_vs_v28_cents
        for point in recent_points
        if point.selected_pnl_delta_vs_v28_cents is not None
    ]
    recent_delta = sum(recent_delta_values) if recent_delta_values else None
    particle_like = model not in {"", "v28", "market_side_ask", "candle_brownian"}
    total_delta = running_delta if has_delta else None
    selected_total = sum(point.selected_pnl_cents for point in points)
    recent_total = sum(point.selected_pnl_cents for point in recent_points)
    positive_count = sum(1 for point in points if point.selected_pnl_cents > 0.0)
    recent_positive_count = sum(1 for point in recent_points if point.selected_pnl_cents > 0.0)
    warnings = _warnings(
        particle_like=particle_like,
        market_count=len(points),
        min_markets=min_markets,
        selected_total=selected_total,
        total_delta=total_delta,
        recent_total=recent_total,
        recent_delta=recent_delta,
        max_drawdown=max_drawdown,
        max_drawdown_multiple=max_drawdown_multiple,
    )
    return SliceTrajectoryRow(
        hypothesis_id=hypothesis_id,
        model=model,
        bucket=bucket,
        particle_like_model=particle_like,
        market_count=len(points),
        selected_pnl_cents=selected_total,
        selected_pnl_delta_vs_v28_cents=total_delta,
        last_n_market_count=len(recent_points),
        last_n_selected_pnl_cents=recent_total,
        last_n_selected_pnl_delta_vs_v28_cents=recent_delta,
        positive_market_count=positive_count,
        positive_last_n_market_count=recent_positive_count,
        max_drawdown_cents=max_drawdown,
        final_running_peak_cents=peak,
        final_running_trough_cents=trough,
        first_market_ticker="" if not points else points[0].market_ticker,
        last_market_ticker="" if not points else points[-1].market_ticker,
        trajectory_warnings=warnings,
        trajectory_screen_pass=particle_like and not warnings,
        points=tuple(points),
    )


def _warnings(
    *,
    particle_like: bool,
    market_count: int,
    min_markets: int,
    selected_total: float,
    total_delta: float | None,
    recent_total: float,
    recent_delta: float | None,
    max_drawdown: float,
    max_drawdown_multiple: float,
) -> tuple[str, ...]:
    warnings: list[str] = []
    if market_count < min_markets:
        warnings.append("underpowered_markets")
    if selected_total <= 0.0:
        warnings.append("nonpositive_total_pnl")
    if recent_total <= 0.0:
        warnings.append("nonpositive_recent_pnl")
    if particle_like and total_delta is not None and total_delta <= 0.0:
        warnings.append("nonpositive_total_delta_vs_v28")
    if particle_like and recent_delta is not None and recent_delta <= 0.0:
        warnings.append("nonpositive_recent_delta_vs_v28")
    if selected_total > 0.0 and max_drawdown > selected_total * max_drawdown_multiple:
        warnings.append("drawdown_large_vs_total_pnl")
    return tuple(warnings)


def _market_close_utc(ticker: str) -> str:
    match = re.search(r"-(\d{2})([A-Z]{3})(\d{2})(\d{2})(\d{2})-", ticker.upper())
    if not match:
        return ""
    year, month, day, hour, minute = match.groups()
    month_number = MONTHS.get(month)
    if month_number is None:
        return ""
    try:
        close = datetime(
            year=2000 + int(year),
            month=month_number,
            day=int(day),
            hour=int(hour),
            minute=int(minute),
            tzinfo=timezone.utc,
        )
    except ValueError:
        return ""
    return close.replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _conclusion(
    rows: Sequence[SliceTrajectoryRow],
    particle_rows: Sequence[SliceTrajectoryRow],
) -> str:
    if not rows:
        return "No market breakdown rows are available for trajectory analysis."
    passing = [row for row in particle_rows if row.trajectory_screen_pass]
    if passing:
        names = ", ".join(row.hypothesis_id for row in passing)
        return f"Diagnostic only: {names} pass the trajectory screen, but this does not authorize live trading."
    if particle_rows:
        return "No particle-like lock passes the trajectory screen; keep all locks shadow-only."
    return "Only non-particle controls are present in the trajectory screen."


def _load_json(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return payload if isinstance(payload, dict) else {}


def _mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _float(value: Any, default: float = 0.0) -> float:
    try:
        parsed = float(value)
    except (TypeError, ValueError):
        return default
    return parsed if parsed == parsed else default


def _fmt_optional(value: float | None) -> str:
    return "" if value is None else f"{value:.6f}"


def _markdown(report: SliceTrajectoryReport) -> str:
    lines = [
        "# Paired Sidecar Slice Trajectory",
        "",
        f"- generated_utc: `{report.generated_utc}`",
        f"- promotion_allowed: `{report.promotion_allowed}`",
        f"- row_count: `{report.row_count}`",
        f"- particle_like_count: `{report.particle_like_count}`",
        f"- trajectory_screen_pass_count: `{report.trajectory_screen_pass_count}`",
        f"- particle_like_trajectory_screen_pass_count: `{report.particle_like_trajectory_screen_pass_count}`",
        f"- worst_recent_hypothesis_id: `{report.worst_recent_hypothesis_id}`",
        f"- worst_recent_selected_pnl_cents: `{report.worst_recent_selected_pnl_cents:.1f}`",
        "",
        "## Rows",
        "",
        "| hypothesis | model | markets | total c | dTotal vs v28 | recent n | recent c | dRecent vs v28 | pos all/recent | max DD c | first | last | warnings | pass |",
        "| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- |",
    ]
    for row in report.rows:
        warnings = ", ".join(row.trajectory_warnings)
        lines.append(
            "| "
            f"`{row.hypothesis_id}` | "
            f"`{row.model}` | "
            f"`{row.market_count}` | "
            f"`{row.selected_pnl_cents:.1f}` | "
            f"`{_fmt_optional(row.selected_pnl_delta_vs_v28_cents)}` | "
            f"`{row.last_n_market_count}` | "
            f"`{row.last_n_selected_pnl_cents:.1f}` | "
            f"`{_fmt_optional(row.last_n_selected_pnl_delta_vs_v28_cents)}` | "
            f"`{row.positive_market_count}` / `{row.positive_last_n_market_count}` | "
            f"`{row.max_drawdown_cents:.1f}` | "
            f"`{row.first_market_ticker}` | "
            f"`{row.last_market_ticker}` | "
            f"`{warnings}` | "
            f"`{row.trajectory_screen_pass}` |"
        )
    lines.extend(
        [
            "",
            "## Conclusion",
            "",
            report.conclusion,
            "",
            "This report is diagnostic only and never authorizes live trading.",
            "",
        ]
    )
    return "\n".join(lines)


if __name__ == "__main__":
    raise SystemExit(main())
