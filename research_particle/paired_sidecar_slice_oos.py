from __future__ import annotations

import argparse
import json
import math
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Literal, Mapping, Sequence

from .paired_sidecar_blend_failure_analysis import (
    DEFAULT_AGGREGATE_JSON,
    DEFAULT_ONLINE_CALIBRATION_JSON,
    _enriched_rows,
    _load_json,
    _mapping,
    _slice_buckets,
)


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT_DIR = ROOT / "logs" / "particle_research" / "reports"
EvaluationScope = Literal["same_sample_diagnostic", "locked_forward_shadow"]


@dataclass(frozen=True)
class PairedSidecarSliceGateConfig:
    min_fresh_candidate_rows: int = 200
    min_fresh_markets: int = 20
    min_slice_rows: int = 100
    min_slice_markets: int = 15
    min_selected_count: int = 50
    min_selected_pnl_cents: float = 1.0
    min_avg_pnl_per_selected_cents: float = 0.01
    min_positive_selected_market_share: float = 0.60
    min_positive_top_ev_market_share: float = 0.60
    top_ev_fraction: float = 0.20
    require_positive_ev_rank: bool = True
    require_positive_top_ev_bucket: bool = True
    require_beats_baseline_brier: bool = True
    require_beats_baseline_logloss: bool = True
    require_beats_baseline_selected_pnl: bool = False


@dataclass(frozen=True)
class SliceModelMetrics:
    model: str
    rows: int
    markets: int
    brier: float
    logloss: float
    mean_ev_cents: float
    selected_count: int
    selected_pnl_cents: float
    avg_pnl_per_selected_cents: float
    top_ev_bucket_count: int
    top_ev_bucket_pnl_cents: float
    ev_rank_correlation: float
    positive_selected_market_count: int
    positive_top_ev_market_count: int


@dataclass(frozen=True)
class PairedSidecarSliceGateResults:
    enough_fresh_candidate_rows: bool
    enough_fresh_markets: bool
    enough_slice_rows: bool
    enough_slice_markets: bool
    enough_selected: bool
    positive_selected_pnl: bool
    positive_avg_pnl: bool
    positive_ev_rank: bool
    positive_top_ev_bucket: bool
    positive_selected_market_share: bool
    positive_top_ev_market_share: bool
    beats_baseline_brier: bool
    beats_baseline_logloss: bool
    beats_baseline_selected_pnl: bool
    locked_forward_scope: bool
    all_passed: bool


@dataclass(frozen=True)
class PairedSidecarSliceOOSReport:
    schema_version: str
    generated_utc: str
    promotion_allowed: bool
    promotion_status: Mapping[str, Any]
    hypothesis_id: str
    model: str
    slice_type: str
    bucket: str
    locked_after_utc: str
    evaluation_scope: EvaluationScope
    online_calibration_json: str
    aggregate_json: str
    output_json: str
    output_md: str
    fee_cents: float
    assumed_fill_probability: float
    no_fill_penalty_cents: float
    baseline_models: tuple[str, ...]
    total_input_rows: int
    total_input_markets: int
    fresh_candidate_rows: int
    fresh_markets: int
    slice_rows: int
    slice_markets: int
    selected_metrics: SliceModelMetrics
    baseline_metrics: tuple[SliceModelMetrics, ...]
    gate_config: PairedSidecarSliceGateConfig
    gate_results: PairedSidecarSliceGateResults
    promotion_safe: bool
    note: str


def evaluate_paired_sidecar_slice_oos(
    *,
    online_calibration_json: Path = DEFAULT_ONLINE_CALIBRATION_JSON,
    aggregate_json: Path = DEFAULT_AGGREGATE_JSON,
    output_dir: Path = DEFAULT_OUTPUT_DIR,
    stem: str = "paired_sidecar_slice_oos",
    plan_json: Path | None = None,
    hypothesis_id: str = "manual",
    model: str = "blend_v28_online_lr010_w20",
    slice_type: str = "time_to_close_band",
    bucket: str = "600s_plus",
    locked_after_utc: str = "",
    evaluation_scope: EvaluationScope = "same_sample_diagnostic",
    baseline_models: Sequence[str] = ("v28", "market_side_ask", "candle_brownian"),
    fee_cents: float = 1.5,
    assumed_fill_probability: float = 1.0,
    no_fill_penalty_cents: float = 0.0,
    gate_config: PairedSidecarSliceGateConfig | None = None,
) -> PairedSidecarSliceOOSReport:
    plan = _load_json(plan_json) if plan_json else {}
    plan_summary = _mapping(plan.get("summary")) if "summary" in plan else _mapping(plan)
    hypothesis_id = str(plan_summary.get("hypothesis_id") or hypothesis_id)
    model = str(plan_summary.get("model") or model)
    slice_type = str(plan_summary.get("slice_type") or slice_type)
    bucket = str(plan_summary.get("bucket") or bucket)
    locked_after_utc = str(plan_summary.get("locked_after_utc") or locked_after_utc)
    evaluation_scope = str(plan_summary.get("evaluation_scope") or evaluation_scope)  # type: ignore[assignment]
    fee_cents = float(plan_summary.get("fee_cents", fee_cents))
    assumed_fill_probability = float(plan_summary.get("assumed_fill_probability", assumed_fill_probability))
    no_fill_penalty_cents = float(plan_summary.get("no_fill_penalty_cents", no_fill_penalty_cents))
    baseline_models = tuple(plan_summary.get("baseline_models") or baseline_models)
    gates = _gate_config_from_plan(plan_summary) or gate_config or PairedSidecarSliceGateConfig()

    online_payload = _load_json(online_calibration_json)
    aggregate_payload = _load_json(aggregate_json)
    all_rows = _enriched_rows(
        [_mapping(row) for row in online_payload.get("calibrated_rows") or []],
        [_mapping(row) for row in aggregate_payload.get("diagnostic_rows") or []],
    )
    lock_ts = _parse_dt(locked_after_utc)
    fresh_rows = [
        row
        for row in all_rows
        if _row_after_lock(row, lock_ts)
    ]
    slice_rows = [
        row
        for row in fresh_rows
        if (slice_type, bucket) in _slice_buckets(row)
    ]
    baseline_models = tuple(model_name for model_name in baseline_models if _model_available(slice_rows, model_name))
    selected_metrics = _model_metrics(
        slice_rows,
        model,
        fee_cents=fee_cents,
        assumed_fill_probability=assumed_fill_probability,
        no_fill_penalty_cents=no_fill_penalty_cents,
        top_ev_fraction=gates.top_ev_fraction,
    )
    baseline_metrics = tuple(
        _model_metrics(
            slice_rows,
            baseline,
            fee_cents=fee_cents,
            assumed_fill_probability=assumed_fill_probability,
            no_fill_penalty_cents=no_fill_penalty_cents,
            top_ev_fraction=gates.top_ev_fraction,
        )
        for baseline in baseline_models
    )
    gate_results = _gate_results(
        selected=selected_metrics,
        baselines=baseline_metrics,
        fresh_rows=fresh_rows,
        evaluation_scope=evaluation_scope,
        gates=gates,
    )
    output_json = output_dir / f"{stem}.json"
    output_md = output_dir / f"{stem}.md"
    return PairedSidecarSliceOOSReport(
        schema_version="paired-sidecar-slice-oos-v1",
        generated_utc=datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        promotion_allowed=False,
        promotion_status={
            "allowed": False,
            "reason": (
                "slice OOS reports are research-only; live trading remains untouched "
                "even if promotion_safe becomes true"
            ),
        },
        hypothesis_id=hypothesis_id,
        model=model,
        slice_type=slice_type,
        bucket=bucket,
        locked_after_utc=locked_after_utc,
        evaluation_scope=evaluation_scope,
        online_calibration_json=str(online_calibration_json),
        aggregate_json=str(aggregate_json),
        output_json=str(output_json),
        output_md=str(output_md),
        fee_cents=float(fee_cents),
        assumed_fill_probability=float(assumed_fill_probability),
        no_fill_penalty_cents=float(no_fill_penalty_cents),
        baseline_models=baseline_models,
        total_input_rows=len(all_rows),
        total_input_markets=len({str(row.get("market_ticker") or "") for row in all_rows if row.get("market_ticker")}),
        fresh_candidate_rows=len(fresh_rows),
        fresh_markets=len({str(row.get("market_ticker") or "") for row in fresh_rows if row.get("market_ticker")}),
        slice_rows=len(slice_rows),
        slice_markets=len({str(row.get("market_ticker") or "") for row in slice_rows if row.get("market_ticker")}),
        selected_metrics=selected_metrics,
        baseline_metrics=baseline_metrics,
        gate_config=gates,
        gate_results=gate_results,
        promotion_safe=bool(gate_results.all_passed),
        note=(
            "Rows at or before locked_after_utc are excluded from every gate. "
            "The slice can only clear on fresh paired sidecar live-shadow rows."
        ),
    )


def write_paired_sidecar_slice_oos_report(report: PairedSidecarSliceOOSReport) -> None:
    output_json = Path(report.output_json)
    output_md = Path(report.output_md)
    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_md.parent.mkdir(parents=True, exist_ok=True)
    output_json.write_text(json.dumps(asdict(report), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    output_md.write_text(_markdown(report), encoding="utf-8")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Evaluate a predeclared paired sidecar calibration/blend slice on fresh rows only."
    )
    parser.add_argument("--plan-json", type=Path, default=None)
    parser.add_argument("--online-calibration-json", type=Path, default=DEFAULT_ONLINE_CALIBRATION_JSON)
    parser.add_argument("--aggregate-json", type=Path, default=DEFAULT_AGGREGATE_JSON)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--stem", default="paired_sidecar_slice_oos")
    parser.add_argument("--hypothesis-id", default="manual")
    parser.add_argument("--model", default="blend_v28_online_lr010_w20")
    parser.add_argument("--slice-type", default="time_to_close_band")
    parser.add_argument("--bucket", default="600s_plus")
    parser.add_argument("--locked-after-utc", default="")
    parser.add_argument(
        "--evaluation-scope",
        choices=["same_sample_diagnostic", "locked_forward_shadow"],
        default="same_sample_diagnostic",
    )
    parser.add_argument("--baseline-model", action="append", default=None)
    parser.add_argument("--fee-cents", type=float, default=1.5)
    parser.add_argument("--assumed-fill-probability", type=float, default=1.0)
    parser.add_argument("--no-fill-penalty-cents", type=float, default=0.0)
    parser.add_argument("--gate-min-fresh-candidate-rows", type=int, default=200)
    parser.add_argument("--gate-min-fresh-markets", type=int, default=20)
    parser.add_argument("--gate-min-slice-rows", type=int, default=100)
    parser.add_argument("--gate-min-slice-markets", type=int, default=15)
    parser.add_argument("--gate-min-selected", type=int, default=50)
    parser.add_argument("--write", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    report = evaluate_paired_sidecar_slice_oos(
        online_calibration_json=args.online_calibration_json,
        aggregate_json=args.aggregate_json,
        output_dir=args.output_dir,
        stem=args.stem,
        plan_json=args.plan_json,
        hypothesis_id=args.hypothesis_id,
        model=args.model,
        slice_type=args.slice_type,
        bucket=args.bucket,
        locked_after_utc=args.locked_after_utc,
        evaluation_scope=args.evaluation_scope,
        baseline_models=tuple(args.baseline_model) if args.baseline_model else ("v28", "market_side_ask", "candle_brownian"),
        fee_cents=args.fee_cents,
        assumed_fill_probability=args.assumed_fill_probability,
        no_fill_penalty_cents=args.no_fill_penalty_cents,
        gate_config=PairedSidecarSliceGateConfig(
            min_fresh_candidate_rows=args.gate_min_fresh_candidate_rows,
            min_fresh_markets=args.gate_min_fresh_markets,
            min_slice_rows=args.gate_min_slice_rows,
            min_slice_markets=args.gate_min_slice_markets,
            min_selected_count=args.gate_min_selected,
        ),
    )
    if args.write:
        write_paired_sidecar_slice_oos_report(report)
    print(f"hypothesis_id={report.hypothesis_id}")
    print(f"evaluation_scope={report.evaluation_scope}")
    print(f"model={report.model}")
    print(f"slice={report.slice_type}={report.bucket}")
    print(f"locked_after_utc={report.locked_after_utc}")
    print(f"fresh_candidate_rows={report.fresh_candidate_rows}")
    print(f"fresh_markets={report.fresh_markets}")
    print(f"slice_rows={report.slice_rows}")
    print(f"slice_markets={report.slice_markets}")
    print(f"selected_count={report.selected_metrics.selected_count}")
    print(f"selected_pnl_cents={report.selected_metrics.selected_pnl_cents:.4f}")
    print(f"promotion_allowed={report.promotion_allowed}")
    print(f"promotion_safe={report.promotion_safe}")
    print(f"output_json={report.output_json}")
    return 0


def _gate_config_from_plan(plan: Mapping[str, Any]) -> PairedSidecarSliceGateConfig | None:
    raw = plan.get("gate_config")
    if not isinstance(raw, Mapping):
        return None
    defaults = asdict(PairedSidecarSliceGateConfig())
    defaults.update({key: raw[key] for key in defaults if key in raw})
    return PairedSidecarSliceGateConfig(**defaults)


def _row_after_lock(row: Mapping[str, Any], lock_ts: datetime | None) -> bool:
    if lock_ts is None:
        return True
    decision_ts = _parse_dt(str(row.get("decision_ts_utc") or ""))
    return decision_ts is not None and decision_ts > lock_ts


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


def _model_available(rows: Sequence[Mapping[str, Any]], model: str) -> bool:
    return any(f"{model}_p_yes" in row for row in rows)


def _model_metrics(
    rows: Sequence[Mapping[str, Any]],
    model: str,
    *,
    fee_cents: float,
    assumed_fill_probability: float,
    no_fill_penalty_cents: float,
    top_ev_fraction: float,
) -> SliceModelMetrics:
    scored = [
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
    selected = [row for row in scored if row["ev_cents"] > 0.0]
    top_count = max(1, math.ceil(len(scored) * max(0.0, min(1.0, top_ev_fraction)))) if scored else 0
    top = sorted(scored, key=lambda row: row["ev_cents"], reverse=True)[:top_count]
    selected_market_pnl = _market_pnl(selected, "pnl_cents")
    top_market_pnl = _market_pnl(top, "pnl_cents")
    return SliceModelMetrics(
        model=model,
        rows=len(scored),
        markets=len({row["market_ticker"] for row in scored if row["market_ticker"]}),
        brier=_mean(row["brier"] for row in scored),
        logloss=_mean(row["logloss"] for row in scored),
        mean_ev_cents=_mean(row["ev_cents"] for row in scored),
        selected_count=len(selected),
        selected_pnl_cents=sum(row["pnl_cents"] for row in selected),
        avg_pnl_per_selected_cents=_mean(row["pnl_cents"] for row in selected),
        top_ev_bucket_count=len(top),
        top_ev_bucket_pnl_cents=sum(row["pnl_cents"] for row in top),
        ev_rank_correlation=_correlation(
            [row["ev_cents"] for row in scored],
            [row["pnl_cents"] for row in scored],
        ),
        positive_selected_market_count=sum(1 for pnl in selected_market_pnl.values() if pnl > 0.0),
        positive_top_ev_market_count=sum(1 for pnl in top_market_pnl.values() if pnl > 0.0),
    )


def _scored_row(
    row: Mapping[str, Any],
    model: str,
    *,
    fee_cents: float,
    assumed_fill_probability: float,
    no_fill_penalty_cents: float,
) -> dict[str, Any]:
    p_yes = _clamp01(_float(row.get(f"{model}_p_yes"), 0.5))
    y_yes = int(_float(row.get("y_yes_win"), 0.0))
    side = str(row.get("side") or "yes").lower()
    ask = _float(row.get("ask_cents"), 50.0)
    p_side = p_yes if side == "yes" else 1.0 - p_yes
    side_won = bool(y_yes) if side == "yes" else not bool(y_yes)
    win_pnl = 100.0 - ask - fee_cents
    lose_pnl = -(ask + fee_cents)
    pnl = win_pnl if side_won else lose_pnl
    fill_prob = _clamp01(assumed_fill_probability)
    ev = fill_prob * (p_side * win_pnl + (1.0 - p_side) * lose_pnl) - (1.0 - fill_prob) * no_fill_penalty_cents
    return {
        "market_ticker": str(row.get("market_ticker") or ""),
        "brier": (p_yes - y_yes) ** 2,
        "logloss": _logloss(p_yes, y_yes),
        "ev_cents": ev,
        "pnl_cents": pnl,
    }


def _gate_results(
    *,
    selected: SliceModelMetrics,
    baselines: Sequence[SliceModelMetrics],
    fresh_rows: Sequence[Mapping[str, Any]],
    evaluation_scope: EvaluationScope,
    gates: PairedSidecarSliceGateConfig,
) -> PairedSidecarSliceGateResults:
    fresh_markets = len({str(row.get("market_ticker") or "") for row in fresh_rows if row.get("market_ticker")})
    enough_fresh_candidate_rows = len(fresh_rows) >= gates.min_fresh_candidate_rows
    enough_fresh_markets = fresh_markets >= gates.min_fresh_markets
    enough_slice_rows = selected.rows >= gates.min_slice_rows
    enough_slice_markets = selected.markets >= gates.min_slice_markets
    enough_selected = selected.selected_count >= gates.min_selected_count
    positive_selected_pnl = selected.selected_pnl_cents >= gates.min_selected_pnl_cents
    positive_avg_pnl = selected.avg_pnl_per_selected_cents >= gates.min_avg_pnl_per_selected_cents
    positive_ev_rank = selected.ev_rank_correlation > 0.0 if gates.require_positive_ev_rank else True
    positive_top_ev_bucket = selected.top_ev_bucket_pnl_cents > 0.0 if gates.require_positive_top_ev_bucket else True
    positive_selected_market_share = (
        selected.markets > 0
        and (selected.positive_selected_market_count / selected.markets) >= gates.min_positive_selected_market_share
    )
    positive_top_ev_market_share = (
        selected.markets > 0
        and (selected.positive_top_ev_market_count / selected.markets) >= gates.min_positive_top_ev_market_share
    )
    comparable_baselines = bool(baselines) and selected.rows > 0 and all(
        baseline.rows == selected.rows and baseline.rows > 0 for baseline in baselines
    )
    beats_baseline_brier = (
        comparable_baselines and all(selected.brier < baseline.brier for baseline in baselines)
        if gates.require_beats_baseline_brier
        else True
    )
    beats_baseline_logloss = (
        comparable_baselines and all(selected.logloss < baseline.logloss for baseline in baselines)
        if gates.require_beats_baseline_logloss
        else True
    )
    beats_baseline_selected_pnl = (
        comparable_baselines and all(selected.selected_pnl_cents > baseline.selected_pnl_cents for baseline in baselines)
        if gates.require_beats_baseline_selected_pnl
        else True
    )
    locked_forward_scope = evaluation_scope == "locked_forward_shadow"
    checks = (
        enough_fresh_candidate_rows,
        enough_fresh_markets,
        enough_slice_rows,
        enough_slice_markets,
        enough_selected,
        positive_selected_pnl,
        positive_avg_pnl,
        positive_ev_rank,
        positive_top_ev_bucket,
        positive_selected_market_share,
        positive_top_ev_market_share,
        beats_baseline_brier,
        beats_baseline_logloss,
        beats_baseline_selected_pnl,
        locked_forward_scope,
    )
    return PairedSidecarSliceGateResults(
        enough_fresh_candidate_rows=enough_fresh_candidate_rows,
        enough_fresh_markets=enough_fresh_markets,
        enough_slice_rows=enough_slice_rows,
        enough_slice_markets=enough_slice_markets,
        enough_selected=enough_selected,
        positive_selected_pnl=positive_selected_pnl,
        positive_avg_pnl=positive_avg_pnl,
        positive_ev_rank=positive_ev_rank,
        positive_top_ev_bucket=positive_top_ev_bucket,
        positive_selected_market_share=positive_selected_market_share,
        positive_top_ev_market_share=positive_top_ev_market_share,
        beats_baseline_brier=beats_baseline_brier,
        beats_baseline_logloss=beats_baseline_logloss,
        beats_baseline_selected_pnl=beats_baseline_selected_pnl,
        locked_forward_scope=locked_forward_scope,
        all_passed=all(checks),
    )


def _market_pnl(rows: Sequence[Mapping[str, Any]], field: str) -> dict[str, float]:
    out: dict[str, float] = {}
    for row in rows:
        market = str(row.get("market_ticker") or "")
        if market:
            out[market] = out.get(market, 0.0) + float(row.get(field, 0.0) or 0.0)
    return out


def _correlation(left: Sequence[float], right: Sequence[float]) -> float:
    if len(left) < 2 or len(left) != len(right):
        return 0.0
    left_mean = sum(left) / len(left)
    right_mean = sum(right) / len(right)
    numerator = sum((x - left_mean) * (y - right_mean) for x, y in zip(left, right))
    left_var = sum((x - left_mean) ** 2 for x in left)
    right_var = sum((y - right_mean) ** 2 for y in right)
    if left_var <= 0.0 or right_var <= 0.0:
        return 0.0
    return numerator / math.sqrt(left_var * right_var)


def _logloss(p: float, y: int) -> float:
    p = min(1.0 - 1e-12, max(1e-12, p))
    return -(y * math.log(p) + (1 - y) * math.log(1.0 - p))


def _clamp01(value: float) -> float:
    return min(1.0, max(0.0, value))


def _float(value: Any, default: float) -> float:
    try:
        parsed = float(value)
    except (TypeError, ValueError):
        return default
    return parsed if math.isfinite(parsed) else default


def _mean(values: Sequence[float] | Any) -> float:
    items = [float(value) for value in values]
    return sum(items) / len(items) if items else 0.0


def _markdown(report: PairedSidecarSliceOOSReport) -> str:
    lines = [
        "# Paired Sidecar Slice OOS Report",
        "",
        f"- generated_utc: `{report.generated_utc}`",
        f"- hypothesis_id: `{report.hypothesis_id}`",
        f"- evaluation_scope: `{report.evaluation_scope}`",
        f"- locked_after_utc: `{report.locked_after_utc}`",
        f"- model: `{report.model}`",
        f"- slice: `{report.slice_type}={report.bucket}`",
        f"- promotion_allowed: `{report.promotion_allowed}`",
        f"- promotion_safe: `{report.promotion_safe}`",
        f"- fresh_candidate_rows / markets: `{report.fresh_candidate_rows}` / `{report.fresh_markets}`",
        f"- slice_rows / markets: `{report.slice_rows}` / `{report.slice_markets}`",
        f"- selected_count: `{report.selected_metrics.selected_count}`",
        f"- selected_pnl_cents: `{report.selected_metrics.selected_pnl_cents:.1f}`",
        f"- top_ev_bucket_pnl_cents: `{report.selected_metrics.top_ev_bucket_pnl_cents:.1f}`",
        "",
        "## Gate Results",
        "",
        "| gate | passed |",
        "| --- | ---: |",
    ]
    for key, value in asdict(report.gate_results).items():
        lines.append(f"| {key} | `{value}` |")
    lines.extend(
        [
            "",
            "## Metrics",
            "",
            "| model | rows | markets | brier | logloss | selected_count | selected_pnl_c | top_ev_pnl_c | ev_rank_corr | pos_selected_mkts | pos_top_mkts |",
            "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
        ]
    )
    for row in (report.selected_metrics, *report.baseline_metrics):
        lines.append(
            f"| {row.model} | {row.rows} | {row.markets} | {row.brier:.6f} | {row.logloss:.6f} | "
            f"{row.selected_count} | {row.selected_pnl_cents:.1f} | {row.top_ev_bucket_pnl_cents:.1f} | "
            f"{row.ev_rank_correlation:.6f} | {row.positive_selected_market_count}/{row.markets} | "
            f"{row.positive_top_ev_market_count}/{row.markets} |"
        )
    lines.extend(
        [
            "",
            "## Notes",
            "",
            f"- {report.note}",
            "- This report is research-only and cannot place orders or mutate live strategy state.",
            "",
        ]
    )
    return "\n".join(lines)


if __name__ == "__main__":
    raise SystemExit(main())
