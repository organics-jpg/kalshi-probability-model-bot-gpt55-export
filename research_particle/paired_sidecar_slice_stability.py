from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping, Sequence


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MARKET_BREAKDOWN_JSON = (
    ROOT / "logs" / "particle_research" / "reports" / "paired_sidecar_slice_market_breakdown_latest.json"
)
DEFAULT_OUTPUT_JSON = (
    ROOT / "logs" / "particle_research" / "reports" / "paired_sidecar_slice_stability_latest.json"
)
DEFAULT_OUTPUT_MD = (
    ROOT / "logs" / "particle_research" / "reports" / "paired_sidecar_slice_stability_latest.md"
)


@dataclass(frozen=True)
class SliceStabilityRow:
    hypothesis_id: str
    model: str
    bucket: str
    particle_like_model: bool
    market_count: int
    positive_market_count: int
    negative_market_count: int
    positive_market_fraction: float
    selected_pnl_cents: float
    top_ev_bucket_pnl_cents: float
    mean_market_selected_pnl_cents: float
    stdev_market_selected_pnl_cents: float
    worst_market_ticker: str
    worst_market_selected_pnl_cents: float
    best_market_ticker: str
    best_market_selected_pnl_cents: float
    max_abs_market_pnl_share: float
    selected_pnl_delta_vs_v28_cents: float | None
    top_ev_pnl_delta_vs_v28_cents: float | None
    mean_brier_delta_vs_v28: float | None
    mean_logloss_delta_vs_v28: float | None
    stability_warnings: tuple[str, ...]
    stability_screen_pass: bool


@dataclass(frozen=True)
class SliceStabilityReport:
    schema_version: str
    generated_utc: str
    promotion_allowed: bool
    promotion_status: Mapping[str, Any]
    input_market_breakdown_json: str
    output_json: str
    output_md: str
    min_markets: int
    min_positive_market_fraction: float
    max_abs_market_pnl_share: float
    row_count: int
    particle_like_count: int
    stability_screen_pass_count: int
    particle_like_stability_screen_pass_count: int
    most_concentrated_hypothesis_id: str
    most_concentrated_abs_market_pnl_share: float
    rows: tuple[SliceStabilityRow, ...]
    conclusion: str


def build_slice_stability_report(
    *,
    market_breakdown_json: Path = DEFAULT_MARKET_BREAKDOWN_JSON,
    output_json: Path = DEFAULT_OUTPUT_JSON,
    output_md: Path = DEFAULT_OUTPUT_MD,
    min_markets: int = 20,
    min_positive_market_fraction: float = 0.60,
    max_abs_market_pnl_share: float = 0.40,
) -> SliceStabilityReport:
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
        _stability_row(
            hypothesis_id=hypothesis_id,
            model=model,
            bucket=bucket,
            rows=items,
            min_markets=min_markets,
            min_positive_market_fraction=min_positive_market_fraction,
            max_abs_market_pnl_share=max_abs_market_pnl_share,
        )
        for (hypothesis_id, model, bucket), items in sorted(grouped.items())
    )
    particle_rows = [row for row in rows if row.particle_like_model]
    most_concentrated = max(rows, key=lambda row: row.max_abs_market_pnl_share, default=None)
    conclusion = _conclusion(rows, particle_rows)
    return SliceStabilityReport(
        schema_version="paired-sidecar-slice-stability-v1",
        generated_utc=datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        promotion_allowed=False,
        promotion_status={
            "allowed": False,
            "reason": "slice stability is diagnostic only and cannot approve live trading",
        },
        input_market_breakdown_json=str(market_breakdown_json),
        output_json=str(output_json),
        output_md=str(output_md),
        min_markets=min_markets,
        min_positive_market_fraction=min_positive_market_fraction,
        max_abs_market_pnl_share=max_abs_market_pnl_share,
        row_count=len(rows),
        particle_like_count=len(particle_rows),
        stability_screen_pass_count=sum(1 for row in rows if row.stability_screen_pass),
        particle_like_stability_screen_pass_count=sum(
            1 for row in particle_rows if row.stability_screen_pass
        ),
        most_concentrated_hypothesis_id="" if most_concentrated is None else most_concentrated.hypothesis_id,
        most_concentrated_abs_market_pnl_share=(
            0.0 if most_concentrated is None else most_concentrated.max_abs_market_pnl_share
        ),
        rows=rows,
        conclusion=conclusion,
    )


def write_slice_stability_report(report: SliceStabilityReport) -> None:
    output_json = Path(report.output_json)
    output_md = Path(report.output_md)
    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_md.parent.mkdir(parents=True, exist_ok=True)
    output_json.write_text(json.dumps(asdict(report), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    output_md.write_text(_markdown(report), encoding="utf-8")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Summarize market-by-market stability for frozen paired sidecar slice locks."
    )
    parser.add_argument("--market-breakdown-json", type=Path, default=DEFAULT_MARKET_BREAKDOWN_JSON)
    parser.add_argument("--output-json", type=Path, default=DEFAULT_OUTPUT_JSON)
    parser.add_argument("--output-md", type=Path, default=DEFAULT_OUTPUT_MD)
    parser.add_argument("--min-markets", type=int, default=20)
    parser.add_argument("--min-positive-market-fraction", type=float, default=0.60)
    parser.add_argument("--max-abs-market-pnl-share", type=float, default=0.40)
    parser.add_argument("--write", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    report = build_slice_stability_report(
        market_breakdown_json=args.market_breakdown_json,
        output_json=args.output_json,
        output_md=args.output_md,
        min_markets=args.min_markets,
        min_positive_market_fraction=args.min_positive_market_fraction,
        max_abs_market_pnl_share=args.max_abs_market_pnl_share,
    )
    if args.write:
        write_slice_stability_report(report)
    print(f"promotion_allowed={report.promotion_allowed}")
    print(f"row_count={report.row_count}")
    print(f"particle_like_count={report.particle_like_count}")
    print(f"stability_screen_pass_count={report.stability_screen_pass_count}")
    print(f"particle_like_stability_screen_pass_count={report.particle_like_stability_screen_pass_count}")
    print(f"most_concentrated_hypothesis_id={report.most_concentrated_hypothesis_id}")
    print(f"most_concentrated_abs_market_pnl_share={report.most_concentrated_abs_market_pnl_share:.6f}")
    print(f"conclusion={report.conclusion}")
    print(f"output_json={report.output_json}")
    return 0


def _stability_row(
    *,
    hypothesis_id: str,
    model: str,
    bucket: str,
    rows: Sequence[Mapping[str, Any]],
    min_markets: int,
    min_positive_market_fraction: float,
    max_abs_market_pnl_share: float,
) -> SliceStabilityRow:
    selected = [_float(row.get("selected_pnl_cents")) for row in rows]
    top_ev = [_float(row.get("top_ev_bucket_pnl_cents")) for row in rows]
    market_count = len(rows)
    positive_count = sum(1 for value in selected if value > 0.0)
    negative_count = sum(1 for value in selected if value < 0.0)
    selected_total = sum(selected)
    top_ev_total = sum(top_ev)
    abs_total = sum(abs(value) for value in selected)
    max_abs_share = 0.0 if abs_total <= 0.0 else max(abs(value) for value in selected) / abs_total
    worst = min(rows, key=lambda row: _float(row.get("selected_pnl_cents")), default={})
    best = max(rows, key=lambda row: _float(row.get("selected_pnl_cents")), default={})
    particle_like = model not in {"", "v28", "market_side_ask", "candle_brownian"}
    selected_deltas = [
        _float(row.get("selected_pnl_delta_vs_v28_cents"))
        for row in rows
        if row.get("selected_pnl_delta_vs_v28_cents") is not None
    ]
    top_deltas = [
        _float(row.get("top_ev_pnl_delta_vs_v28_cents"))
        for row in rows
        if row.get("top_ev_pnl_delta_vs_v28_cents") is not None
    ]
    brier_deltas = [
        _float(row.get("brier_delta_vs_v28"))
        for row in rows
        if row.get("brier_delta_vs_v28") is not None
    ]
    logloss_deltas = [
        _float(row.get("logloss_delta_vs_v28"))
        for row in rows
        if row.get("logloss_delta_vs_v28") is not None
    ]
    selected_delta = sum(selected_deltas) if selected_deltas else None
    top_delta = sum(top_deltas) if top_deltas else None
    mean_brier_delta = _mean(brier_deltas) if brier_deltas else None
    mean_logloss_delta = _mean(logloss_deltas) if logloss_deltas else None
    positive_fraction = 0.0 if market_count == 0 else positive_count / market_count
    warnings = _warnings(
        particle_like=particle_like,
        market_count=market_count,
        min_markets=min_markets,
        selected_total=selected_total,
        top_ev_total=top_ev_total,
        positive_fraction=positive_fraction,
        min_positive_market_fraction=min_positive_market_fraction,
        max_abs_share=max_abs_share,
        max_abs_market_pnl_share=max_abs_market_pnl_share,
        selected_delta=selected_delta,
        top_delta=top_delta,
        mean_brier_delta=mean_brier_delta,
        mean_logloss_delta=mean_logloss_delta,
    )
    return SliceStabilityRow(
        hypothesis_id=hypothesis_id,
        model=model,
        bucket=bucket,
        particle_like_model=particle_like,
        market_count=market_count,
        positive_market_count=positive_count,
        negative_market_count=negative_count,
        positive_market_fraction=positive_fraction,
        selected_pnl_cents=selected_total,
        top_ev_bucket_pnl_cents=top_ev_total,
        mean_market_selected_pnl_cents=_mean(selected),
        stdev_market_selected_pnl_cents=_stdev(selected),
        worst_market_ticker=str(worst.get("market_ticker") or ""),
        worst_market_selected_pnl_cents=_float(worst.get("selected_pnl_cents")),
        best_market_ticker=str(best.get("market_ticker") or ""),
        best_market_selected_pnl_cents=_float(best.get("selected_pnl_cents")),
        max_abs_market_pnl_share=max_abs_share,
        selected_pnl_delta_vs_v28_cents=selected_delta,
        top_ev_pnl_delta_vs_v28_cents=top_delta,
        mean_brier_delta_vs_v28=mean_brier_delta,
        mean_logloss_delta_vs_v28=mean_logloss_delta,
        stability_warnings=warnings,
        stability_screen_pass=particle_like and not warnings,
    )


def _warnings(
    *,
    particle_like: bool,
    market_count: int,
    min_markets: int,
    selected_total: float,
    top_ev_total: float,
    positive_fraction: float,
    min_positive_market_fraction: float,
    max_abs_share: float,
    max_abs_market_pnl_share: float,
    selected_delta: float | None,
    top_delta: float | None,
    mean_brier_delta: float | None,
    mean_logloss_delta: float | None,
) -> tuple[str, ...]:
    warnings: list[str] = []
    if market_count < min_markets:
        warnings.append("underpowered_markets")
    if selected_total <= 0.0:
        warnings.append("nonpositive_selected_pnl")
    if top_ev_total <= 0.0:
        warnings.append("nonpositive_top_ev_pnl")
    if positive_fraction < min_positive_market_fraction:
        warnings.append("low_positive_market_fraction")
    if max_abs_share > max_abs_market_pnl_share:
        warnings.append("concentrated_market_pnl")
    if particle_like and selected_delta is not None and selected_delta <= 0.0:
        warnings.append("worse_or_equal_selected_vs_v28")
    if particle_like and top_delta is not None and top_delta <= 0.0:
        warnings.append("worse_or_equal_top_ev_vs_v28")
    if particle_like and mean_brier_delta is not None and mean_brier_delta >= 0.0:
        warnings.append("worse_or_equal_brier_vs_v28")
    if particle_like and mean_logloss_delta is not None and mean_logloss_delta >= 0.0:
        warnings.append("worse_or_equal_logloss_vs_v28")
    return tuple(warnings)


def _conclusion(
    rows: Sequence[SliceStabilityRow],
    particle_rows: Sequence[SliceStabilityRow],
) -> str:
    if not rows:
        return "No market breakdown rows are available for stability analysis."
    passing = [row for row in particle_rows if row.stability_screen_pass]
    if passing:
        names = ", ".join(row.hypothesis_id for row in passing)
        return f"Diagnostic only: {names} pass the market-stability screen, but this does not authorize live trading."
    if particle_rows:
        return "No particle-like lock passes the market-stability screen; keep all locks shadow-only."
    return "Only non-particle controls are present in the market-stability screen."


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


def _mean(values: Sequence[float]) -> float:
    return sum(values) / len(values) if values else 0.0


def _stdev(values: Sequence[float]) -> float:
    if not values:
        return 0.0
    mean = _mean(values)
    return (sum((value - mean) ** 2 for value in values) / len(values)) ** 0.5


def _fmt_optional(value: float | None) -> str:
    return "" if value is None else f"{value:.6f}"


def _markdown(report: SliceStabilityReport) -> str:
    lines = [
        "# Paired Sidecar Slice Stability",
        "",
        f"- generated_utc: `{report.generated_utc}`",
        f"- promotion_allowed: `{report.promotion_allowed}`",
        f"- row_count: `{report.row_count}`",
        f"- particle_like_count: `{report.particle_like_count}`",
        f"- stability_screen_pass_count: `{report.stability_screen_pass_count}`",
        f"- particle_like_stability_screen_pass_count: `{report.particle_like_stability_screen_pass_count}`",
        f"- most_concentrated_hypothesis_id: `{report.most_concentrated_hypothesis_id}`",
        f"- most_concentrated_abs_market_pnl_share: `{report.most_concentrated_abs_market_pnl_share:.6f}`",
        "",
        "## Rows",
        "",
        "| hypothesis | model | markets | pos/neg | pnl c | top EV c | pos frac | mean c | stdev c | worst market | worst c | best c | max abs share | dPnL vs v28 | dTopEV vs v28 | dBrier | dLogloss | warnings | pass |",
        "| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- |",
    ]
    for row in report.rows:
        warnings = ", ".join(row.stability_warnings)
        lines.append(
            "| "
            f"`{row.hypothesis_id}` | "
            f"`{row.model}` | "
            f"`{row.market_count}` | "
            f"`{row.positive_market_count}` / `{row.negative_market_count}` | "
            f"`{row.selected_pnl_cents:.1f}` | "
            f"`{row.top_ev_bucket_pnl_cents:.1f}` | "
            f"`{row.positive_market_fraction:.3f}` | "
            f"`{row.mean_market_selected_pnl_cents:.1f}` | "
            f"`{row.stdev_market_selected_pnl_cents:.1f}` | "
            f"`{row.worst_market_ticker}` | "
            f"`{row.worst_market_selected_pnl_cents:.1f}` | "
            f"`{row.best_market_selected_pnl_cents:.1f}` | "
            f"`{row.max_abs_market_pnl_share:.3f}` | "
            f"`{_fmt_optional(row.selected_pnl_delta_vs_v28_cents)}` | "
            f"`{_fmt_optional(row.top_ev_pnl_delta_vs_v28_cents)}` | "
            f"`{_fmt_optional(row.mean_brier_delta_vs_v28)}` | "
            f"`{_fmt_optional(row.mean_logloss_delta_vs_v28)}` | "
            f"`{warnings}` | "
            f"`{row.stability_screen_pass}` |"
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
