from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping, Sequence

from .paired_sidecar_blend_failure_analysis import (
    DEFAULT_AGGREGATE_JSON,
    DEFAULT_ONLINE_CALIBRATION_JSON,
    _enriched_rows,
    _load_json,
    _mapping,
    _slice_buckets,
)
from .paired_sidecar_slice_oos import (
    PairedSidecarSliceGateConfig,
    _gate_config_from_plan,
    _model_available,
    _parse_dt,
    _row_after_lock,
    _scored_row,
)


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PLAN_DIR = ROOT / "logs" / "particle_research" / "locked_oos_plans"
DEFAULT_OUTPUT_JSON = ROOT / "logs" / "particle_research" / "reports" / "paired_sidecar_slice_market_breakdown_latest.json"
DEFAULT_OUTPUT_MD = ROOT / "logs" / "particle_research" / "reports" / "paired_sidecar_slice_market_breakdown_latest.md"


@dataclass(frozen=True)
class SliceMarketBreakdownRow:
    hypothesis_id: str
    model: str
    market_ticker: str
    bucket: str
    locked_after_utc: str
    rows: int
    selected_count: int
    selected_pnl_cents: float
    top_ev_bucket_count: int
    top_ev_bucket_pnl_cents: float
    brier: float
    logloss: float
    v28_selected_count: int
    v28_selected_pnl_cents: float
    v28_top_ev_bucket_pnl_cents: float
    v28_brier: float
    v28_logloss: float
    selected_pnl_delta_vs_v28_cents: float | None
    top_ev_pnl_delta_vs_v28_cents: float | None
    brier_delta_vs_v28: float | None
    logloss_delta_vs_v28: float | None


@dataclass(frozen=True)
class SliceMarketBreakdownReport:
    schema_version: str
    generated_utc: str
    promotion_allowed: bool
    promotion_status: Mapping[str, Any]
    input_plan_dir: str
    input_online_calibration_json: str
    input_aggregate_json: str
    output_json: str
    output_md: str
    plan_count: int
    row_count: int
    particle_like_row_count: int
    particle_like_negative_market_count: int
    worst_particle_hypothesis_id: str
    worst_particle_market_ticker: str
    worst_particle_selected_pnl_cents: float
    worst_particle_delta_vs_v28_cents: float | None
    rows: tuple[SliceMarketBreakdownRow, ...]
    conclusion: str


def build_slice_market_breakdown(
    *,
    plan_dir: Path = DEFAULT_PLAN_DIR,
    plan_pattern: str = "paired_sidecar_slice_PSLICELOCK*_locked_plan.json",
    online_calibration_json: Path = DEFAULT_ONLINE_CALIBRATION_JSON,
    aggregate_json: Path = DEFAULT_AGGREGATE_JSON,
    output_json: Path = DEFAULT_OUTPUT_JSON,
    output_md: Path = DEFAULT_OUTPUT_MD,
) -> SliceMarketBreakdownReport:
    online_payload = _load_json(online_calibration_json)
    aggregate_payload = _load_json(aggregate_json)
    all_rows = _enriched_rows(
        [_mapping(row) for row in online_payload.get("calibrated_rows") or []],
        [_mapping(row) for row in aggregate_payload.get("diagnostic_rows") or []],
    )
    plans = [_load_json(path) for path in sorted(plan_dir.glob(plan_pattern))]
    rows: list[SliceMarketBreakdownRow] = []
    for plan in plans:
        rows.extend(_plan_market_rows(plan, all_rows))
    particle_rows = [
        row
        for row in rows
        if row.model not in {"", "v28", "market_side_ask", "candle_brownian"}
    ]
    negative_particle_rows = [row for row in particle_rows if row.selected_pnl_cents < 0.0]
    worst = min(particle_rows, key=lambda row: row.selected_pnl_cents, default=None)
    conclusion = _conclusion(rows, particle_rows, negative_particle_rows)
    return SliceMarketBreakdownReport(
        schema_version="paired-sidecar-slice-market-breakdown-v1",
        generated_utc=datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        promotion_allowed=False,
        promotion_status={
            "allowed": False,
            "reason": "market breakdown is diagnostic only and cannot approve live trading",
        },
        input_plan_dir=str(plan_dir),
        input_online_calibration_json=str(online_calibration_json),
        input_aggregate_json=str(aggregate_json),
        output_json=str(output_json),
        output_md=str(output_md),
        plan_count=len(plans),
        row_count=len(rows),
        particle_like_row_count=len(particle_rows),
        particle_like_negative_market_count=len(negative_particle_rows),
        worst_particle_hypothesis_id="" if worst is None else worst.hypothesis_id,
        worst_particle_market_ticker="" if worst is None else worst.market_ticker,
        worst_particle_selected_pnl_cents=0.0 if worst is None else worst.selected_pnl_cents,
        worst_particle_delta_vs_v28_cents=None if worst is None else worst.selected_pnl_delta_vs_v28_cents,
        rows=tuple(rows),
        conclusion=conclusion,
    )


def write_slice_market_breakdown(report: SliceMarketBreakdownReport) -> None:
    output_json = Path(report.output_json)
    output_md = Path(report.output_md)
    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_md.parent.mkdir(parents=True, exist_ok=True)
    output_json.write_text(json.dumps(asdict(report), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    output_md.write_text(_markdown(report), encoding="utf-8")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Break down frozen paired sidecar slice locks by market."
    )
    parser.add_argument("--plan-dir", type=Path, default=DEFAULT_PLAN_DIR)
    parser.add_argument("--plan-pattern", default="paired_sidecar_slice_PSLICELOCK*_locked_plan.json")
    parser.add_argument("--online-calibration-json", type=Path, default=DEFAULT_ONLINE_CALIBRATION_JSON)
    parser.add_argument("--aggregate-json", type=Path, default=DEFAULT_AGGREGATE_JSON)
    parser.add_argument("--output-json", type=Path, default=DEFAULT_OUTPUT_JSON)
    parser.add_argument("--output-md", type=Path, default=DEFAULT_OUTPUT_MD)
    parser.add_argument("--write", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    report = build_slice_market_breakdown(
        plan_dir=args.plan_dir,
        plan_pattern=args.plan_pattern,
        online_calibration_json=args.online_calibration_json,
        aggregate_json=args.aggregate_json,
        output_json=args.output_json,
        output_md=args.output_md,
    )
    if args.write:
        write_slice_market_breakdown(report)
    print(f"promotion_allowed={report.promotion_allowed}")
    print(f"plan_count={report.plan_count}")
    print(f"row_count={report.row_count}")
    print(f"particle_like_row_count={report.particle_like_row_count}")
    print(f"particle_like_negative_market_count={report.particle_like_negative_market_count}")
    print(f"worst_particle_hypothesis_id={report.worst_particle_hypothesis_id}")
    print(f"worst_particle_market_ticker={report.worst_particle_market_ticker}")
    print(f"worst_particle_selected_pnl_cents={report.worst_particle_selected_pnl_cents:.4f}")
    print(f"worst_particle_delta_vs_v28_cents={report.worst_particle_delta_vs_v28_cents}")
    print(f"conclusion={report.conclusion}")
    print(f"output_json={report.output_json}")
    return 0


def _plan_market_rows(
    plan_payload: Mapping[str, Any],
    all_rows: Sequence[Mapping[str, Any]],
) -> list[SliceMarketBreakdownRow]:
    hypothesis_id = str(plan_payload.get("hypothesis_id") or "")
    model = str(plan_payload.get("model") or "")
    bucket = str(plan_payload.get("bucket") or "")
    slice_type = str(plan_payload.get("slice_type") or "")
    locked_after_utc = str(plan_payload.get("locked_after_utc") or "")
    fee_cents = _float(plan_payload.get("fee_cents"), 1.5)
    assumed_fill_probability = _float(plan_payload.get("assumed_fill_probability"), 1.0)
    no_fill_penalty_cents = _float(plan_payload.get("no_fill_penalty_cents"), 0.0)
    gates = _gate_config_from_plan(plan_payload) or PairedSidecarSliceGateConfig()
    lock_ts = _parse_dt(locked_after_utc)
    slice_rows = [
        row
        for row in all_rows
        if _row_after_lock(row, lock_ts) and (slice_type, bucket) in _slice_buckets(row)
    ]
    if not _model_available(slice_rows, model):
        return []
    markets = sorted({str(row.get("market_ticker") or "") for row in slice_rows if row.get("market_ticker")})
    return [
        _market_row(
            hypothesis_id=hypothesis_id,
            model=model,
            bucket=bucket,
            locked_after_utc=locked_after_utc,
            market_ticker=market,
            rows=[row for row in slice_rows if str(row.get("market_ticker") or "") == market],
            fee_cents=fee_cents,
            assumed_fill_probability=assumed_fill_probability,
            no_fill_penalty_cents=no_fill_penalty_cents,
            top_ev_fraction=gates.top_ev_fraction,
        )
        for market in markets
    ]


def _market_row(
    *,
    hypothesis_id: str,
    model: str,
    bucket: str,
    locked_after_utc: str,
    market_ticker: str,
    rows: Sequence[Mapping[str, Any]],
    fee_cents: float,
    assumed_fill_probability: float,
    no_fill_penalty_cents: float,
    top_ev_fraction: float,
) -> SliceMarketBreakdownRow:
    scored = _scored(rows, model, fee_cents, assumed_fill_probability, no_fill_penalty_cents)
    v28_scored = _scored(rows, "v28", fee_cents, assumed_fill_probability, no_fill_penalty_cents)
    selected = [row for row in scored if row["ev_cents"] > 0.0]
    v28_selected = [row for row in v28_scored if row["ev_cents"] > 0.0]
    top = _top_ev(scored, top_ev_fraction)
    v28_top = _top_ev(v28_scored, top_ev_fraction)
    selected_pnl = sum(row["pnl_cents"] for row in selected)
    v28_selected_pnl = sum(row["pnl_cents"] for row in v28_selected)
    top_pnl = sum(row["pnl_cents"] for row in top)
    v28_top_pnl = sum(row["pnl_cents"] for row in v28_top)
    brier = _mean(row["brier"] for row in scored)
    logloss = _mean(row["logloss"] for row in scored)
    v28_brier = _mean(row["brier"] for row in v28_scored)
    v28_logloss = _mean(row["logloss"] for row in v28_scored)
    has_v28 = bool(v28_scored)
    return SliceMarketBreakdownRow(
        hypothesis_id=hypothesis_id,
        model=model,
        market_ticker=market_ticker,
        bucket=bucket,
        locked_after_utc=locked_after_utc,
        rows=len(scored),
        selected_count=len(selected),
        selected_pnl_cents=selected_pnl,
        top_ev_bucket_count=len(top),
        top_ev_bucket_pnl_cents=top_pnl,
        brier=brier,
        logloss=logloss,
        v28_selected_count=len(v28_selected),
        v28_selected_pnl_cents=v28_selected_pnl,
        v28_top_ev_bucket_pnl_cents=v28_top_pnl,
        v28_brier=v28_brier,
        v28_logloss=v28_logloss,
        selected_pnl_delta_vs_v28_cents=None if not has_v28 else selected_pnl - v28_selected_pnl,
        top_ev_pnl_delta_vs_v28_cents=None if not has_v28 else top_pnl - v28_top_pnl,
        brier_delta_vs_v28=None if not has_v28 else brier - v28_brier,
        logloss_delta_vs_v28=None if not has_v28 else logloss - v28_logloss,
    )


def _scored(
    rows: Sequence[Mapping[str, Any]],
    model: str,
    fee_cents: float,
    assumed_fill_probability: float,
    no_fill_penalty_cents: float,
) -> list[dict[str, Any]]:
    return [
        _scored_row(
            row,
            model,
            fee_cents=fee_cents,
            assumed_fill_probability=assumed_fill_probability,
            no_fill_penalty_cents=no_fill_penalty_cents,
        )
        for row in rows
        if f"{model}_p_yes" in row
    ]


def _top_ev(rows: Sequence[Mapping[str, Any]], top_ev_fraction: float) -> list[Mapping[str, Any]]:
    if not rows:
        return []
    fraction = max(0.0, min(1.0, top_ev_fraction))
    top_count = max(1, int((len(rows) * fraction) + 0.999999))
    return sorted(rows, key=lambda row: float(row.get("ev_cents", 0.0) or 0.0), reverse=True)[:top_count]


def _conclusion(
    rows: Sequence[SliceMarketBreakdownRow],
    particle_rows: Sequence[SliceMarketBreakdownRow],
    negative_particle_rows: Sequence[SliceMarketBreakdownRow],
) -> str:
    if not rows:
        return "No market rows are available for the frozen slice locks."
    if negative_particle_rows:
        worst = min(negative_particle_rows, key=lambda row: row.selected_pnl_cents)
        return (
            "Particle-like slice locks have negative market-level outcomes. "
            f"Worst row: {worst.hypothesis_id} on {worst.market_ticker} at "
            f"{worst.selected_pnl_cents:.1f}c selected PnL."
        )
    if particle_rows:
        return "Particle-like slice locks have no negative market rows yet, but this is still diagnostic only."
    return "Only non-particle controls are present in the frozen slice locks."


def _float(value: Any, default: float = 0.0) -> float:
    try:
        parsed = float(value)
    except (TypeError, ValueError):
        return default
    return parsed if parsed == parsed else default


def _mean(values: Any) -> float:
    items = [float(value) for value in values]
    return sum(items) / len(items) if items else 0.0


def _fmt_optional(value: float | None) -> str:
    return "" if value is None else f"{value:.6f}"


def _markdown(report: SliceMarketBreakdownReport) -> str:
    lines = [
        "# Paired Sidecar Slice Market Breakdown",
        "",
        f"- generated_utc: `{report.generated_utc}`",
        f"- promotion_allowed: `{report.promotion_allowed}`",
        f"- plan_count: `{report.plan_count}`",
        f"- row_count: `{report.row_count}`",
        f"- particle_like_row_count: `{report.particle_like_row_count}`",
        f"- particle_like_negative_market_count: `{report.particle_like_negative_market_count}`",
        f"- worst_particle_hypothesis_id: `{report.worst_particle_hypothesis_id}`",
        f"- worst_particle_market_ticker: `{report.worst_particle_market_ticker}`",
        f"- worst_particle_selected_pnl_cents: `{report.worst_particle_selected_pnl_cents:.1f}`",
        f"- worst_particle_delta_vs_v28_cents: `{_fmt_optional(report.worst_particle_delta_vs_v28_cents)}`",
        "",
        "## Rows",
        "",
        "| hypothesis | model | market | rows | selected | pnl c | v28 pnl c | dPnL vs v28 | top EV c | dTopEV vs v28 | Brier | dBrier vs v28 | logloss | dLogloss vs v28 |",
        "| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for row in sorted(report.rows, key=lambda item: (item.hypothesis_id, item.selected_pnl_cents)):
        lines.append(
            "| "
            f"`{row.hypothesis_id}` | "
            f"`{row.model}` | "
            f"`{row.market_ticker}` | "
            f"`{row.rows}` | "
            f"`{row.selected_count}` | "
            f"`{row.selected_pnl_cents:.1f}` | "
            f"`{row.v28_selected_pnl_cents:.1f}` | "
            f"`{_fmt_optional(row.selected_pnl_delta_vs_v28_cents)}` | "
            f"`{row.top_ev_bucket_pnl_cents:.1f}` | "
            f"`{_fmt_optional(row.top_ev_pnl_delta_vs_v28_cents)}` | "
            f"`{row.brier:.6f}` | "
            f"`{_fmt_optional(row.brier_delta_vs_v28)}` | "
            f"`{row.logloss:.6f}` | "
            f"`{_fmt_optional(row.logloss_delta_vs_v28)}` |"
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
