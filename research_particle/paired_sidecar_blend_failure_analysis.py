from __future__ import annotations

import argparse
import json
import math
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping, Sequence


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_ONLINE_CALIBRATION_JSON = (
    ROOT / "logs" / "particle_research" / "reports" / "paired_sidecar_online_calibration_latest.json"
)
DEFAULT_AGGREGATE_JSON = (
    ROOT / "logs" / "particle_research" / "reports" / "paired_sidecar_spot_aggregate_latest.json"
)
DEFAULT_OUTPUT_JSON = (
    ROOT / "logs" / "particle_research" / "reports" / "paired_sidecar_blend_failure_analysis_latest.json"
)
DEFAULT_OUTPUT_MD = (
    ROOT / "logs" / "particle_research" / "reports" / "paired_sidecar_blend_failure_analysis_latest.md"
)

DEFAULT_BASELINES = ("v28", "market_side_ask", "candle_brownian")
DEFAULT_FOCUS_MODELS = (
    "candidate_raw",
    "v28",
    "market_side_ask",
    "candle_brownian",
    "tick_brownian",
    "online_logit_candidate_lr010_row",
    "blend_v28_online_lr010_w10",
    "blend_v28_online_lr010_w25",
    "blend_market_online_lr010_w15",
)


@dataclass(frozen=True)
class ModelFailureSummary:
    model: str
    rows: int
    markets: int
    brier: float
    logloss: float
    market_equal_brier: float
    market_equal_logloss: float
    selected_count: int
    selected_pnl_cents: float
    top_ev_bucket_count: int
    top_ev_bucket_pnl_cents: float
    positive_selected_market_count: int
    positive_top_ev_market_count: int
    negative_selected_market_count: int
    negative_top_ev_market_count: int


@dataclass(frozen=True)
class ModelComparisonRow:
    model: str
    baseline: str
    rows: int
    markets: int
    row_brier_delta: float
    row_logloss_delta: float
    row_selected_pnl_delta_cents: float
    row_top_ev_bucket_pnl_delta_cents: float
    market_equal_brier_delta: float
    market_equal_logloss_delta: float
    market_equal_selected_pnl_delta_cents: float
    market_equal_top_ev_bucket_pnl_delta_cents: float


@dataclass(frozen=True)
class SliceRow:
    model: str
    slice_type: str
    bucket: str
    rows: int
    markets: int
    brier: float
    logloss: float
    selected_count: int
    selected_pnl_cents: float
    top_ev_bucket_count: int
    top_ev_bucket_pnl_cents: float
    positive_selected_market_count: int
    positive_top_ev_market_count: int


@dataclass(frozen=True)
class MarketDriverRow:
    model: str
    market_ticker: str
    rows: int
    y_yes_win: int
    label_available_ts_utc: str
    brier: float
    logloss: float
    selected_count: int
    selected_pnl_cents: float
    top_ev_bucket_count: int
    top_ev_bucket_pnl_cents: float
    selected_pnl_delta_vs_v28_cents: float | None
    top_ev_bucket_pnl_delta_vs_v28_cents: float | None


@dataclass(frozen=True)
class PosthocSliceCandidate:
    model: str
    slice_type: str
    bucket: str
    rows: int
    markets: int
    selected_count: int
    selected_pnl_cents: float
    top_ev_bucket_pnl_cents: float
    positive_selected_market_count: int
    positive_market_share: float
    note: str


@dataclass(frozen=True)
class PairedSidecarBlendFailureAnalysisReport:
    schema_version: str
    generated_utc: str
    promotion_allowed: bool
    promotion_status: Mapping[str, Any]
    input_online_calibration_json: str
    input_aggregate_json: str
    output_json: str
    output_md: str
    rows: int
    markets: int
    focus_models: tuple[str, ...]
    baselines: tuple[str, ...]
    best_model_by_brier: str
    best_model_by_logloss: str
    market_equal_best_model_by_brier: str
    market_equal_best_model_by_logloss: str
    best_blend_model_by_market_equal_brier: str
    best_blend_positive_market_top_ev_count: int
    best_blend_positive_market_selected_pnl_count: int
    model_summaries: tuple[ModelFailureSummary, ...]
    comparisons: tuple[ModelComparisonRow, ...]
    slice_rows: tuple[SliceRow, ...]
    worst_market_drivers: tuple[MarketDriverRow, ...]
    posthoc_slice_candidates: tuple[PosthocSliceCandidate, ...]
    promotion_safe: bool
    conclusion: str


def build_paired_sidecar_blend_failure_analysis(
    *,
    online_calibration_json: Path = DEFAULT_ONLINE_CALIBRATION_JSON,
    aggregate_json: Path = DEFAULT_AGGREGATE_JSON,
    output_json: Path = DEFAULT_OUTPUT_JSON,
    output_md: Path = DEFAULT_OUTPUT_MD,
    focus_models: Sequence[str] | None = None,
    baselines: Sequence[str] = DEFAULT_BASELINES,
) -> PairedSidecarBlendFailureAnalysisReport:
    online_payload = _load_json(online_calibration_json)
    aggregate_payload = _load_json(aggregate_json)
    summary = _mapping(online_payload.get("summary"))
    rows = _enriched_rows(
        [_mapping(row) for row in online_payload.get("calibrated_rows") or []],
        [_mapping(row) for row in aggregate_payload.get("diagnostic_rows") or []],
    )
    available_models = _available_models(rows)
    selected_models = _select_focus_models(summary, available_models, focus_models)
    selected_baselines = tuple(model for model in baselines if model in available_models)
    model_rows = _by_model(online_payload.get("model_rows"))
    market_equal_rows = _by_model(online_payload.get("market_equal_model_rows"))
    market_model_rows = _market_model_index(online_payload.get("market_model_rows"))
    top_keys_by_model = _top_ev_keys_by_model(rows, selected_models)

    model_summaries = tuple(
        _model_failure_summary(model, model_rows, market_equal_rows, market_model_rows)
        for model in selected_models
    )
    comparisons = tuple(
        _comparison(model, baseline, model_rows, market_equal_rows)
        for model in selected_models
        for baseline in selected_baselines
        if model != baseline
    )
    slice_rows = tuple(_slice_rows(rows, selected_models, top_keys_by_model))
    best_blend = str(summary.get("best_blend_model_by_market_equal_brier") or "")
    driver_model = best_blend if best_blend in available_models else _first_existing(
        selected_models, ("blend_v28_online_lr010_w25", "blend_market_online_lr010_w15")
    )
    worst_market_drivers = tuple(
        _worst_market_drivers(driver_model, rows, market_model_rows, limit=12)
        if driver_model
        else []
    )
    posthoc_slice_candidates = tuple(_posthoc_slice_candidates(slice_rows))
    conclusion = _conclusion(summary, comparisons, worst_market_drivers, posthoc_slice_candidates)

    return PairedSidecarBlendFailureAnalysisReport(
        schema_version="paired-sidecar-blend-failure-analysis-v1",
        generated_utc=datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        promotion_allowed=False,
        promotion_status={
            "allowed": False,
            "reason": (
                "post-hoc failure analysis is diagnostic only; any sub-regime must be "
                "predeclared and validated on new forward-shadow markets before live impact"
            ),
        },
        input_online_calibration_json=str(online_calibration_json),
        input_aggregate_json=str(aggregate_json),
        output_json=str(output_json),
        output_md=str(output_md),
        rows=len(rows),
        markets=len({str(row.get("market_ticker") or "") for row in rows if row.get("market_ticker")}),
        focus_models=tuple(selected_models),
        baselines=selected_baselines,
        best_model_by_brier=str(summary.get("best_model_by_brier") or ""),
        best_model_by_logloss=str(summary.get("best_model_by_logloss") or ""),
        market_equal_best_model_by_brier=str(summary.get("market_equal_best_model_by_brier") or ""),
        market_equal_best_model_by_logloss=str(summary.get("market_equal_best_model_by_logloss") or ""),
        best_blend_model_by_market_equal_brier=best_blend,
        best_blend_positive_market_top_ev_count=int(
            summary.get("best_blend_positive_market_top_ev_count") or 0
        ),
        best_blend_positive_market_selected_pnl_count=int(
            summary.get("best_blend_positive_market_selected_pnl_count") or 0
        ),
        model_summaries=model_summaries,
        comparisons=comparisons,
        slice_rows=slice_rows,
        worst_market_drivers=worst_market_drivers,
        posthoc_slice_candidates=posthoc_slice_candidates,
        promotion_safe=False,
        conclusion=conclusion,
    )


def write_paired_sidecar_blend_failure_analysis(
    report: PairedSidecarBlendFailureAnalysisReport,
) -> None:
    output_json = Path(report.output_json)
    output_md = Path(report.output_md)
    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_md.parent.mkdir(parents=True, exist_ok=True)
    output_json.write_text(json.dumps(asdict(report), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    output_md.write_text(_markdown(report), encoding="utf-8")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Post-hoc failure analysis for paired sidecar online calibration/blend candidates."
    )
    parser.add_argument("--online-calibration-json", type=Path, default=DEFAULT_ONLINE_CALIBRATION_JSON)
    parser.add_argument("--aggregate-json", type=Path, default=DEFAULT_AGGREGATE_JSON)
    parser.add_argument("--output-json", type=Path, default=DEFAULT_OUTPUT_JSON)
    parser.add_argument("--output-md", type=Path, default=DEFAULT_OUTPUT_MD)
    parser.add_argument("--focus-model", action="append", default=None)
    parser.add_argument("--baseline", action="append", default=None)
    parser.add_argument("--write", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    report = build_paired_sidecar_blend_failure_analysis(
        online_calibration_json=args.online_calibration_json,
        aggregate_json=args.aggregate_json,
        output_json=args.output_json,
        output_md=args.output_md,
        focus_models=args.focus_model,
        baselines=tuple(args.baseline) if args.baseline else DEFAULT_BASELINES,
    )
    if args.write:
        write_paired_sidecar_blend_failure_analysis(report)
    print(f"rows={report.rows}")
    print(f"markets={report.markets}")
    print(f"best_blend_model_by_market_equal_brier={report.best_blend_model_by_market_equal_brier}")
    print(f"best_blend_positive_market_top_ev_count={report.best_blend_positive_market_top_ev_count}")
    print(f"best_blend_positive_market_selected_pnl_count={report.best_blend_positive_market_selected_pnl_count}")
    print(f"posthoc_slice_candidate_count={len(report.posthoc_slice_candidates)}")
    print(f"promotion_allowed={report.promotion_allowed}")
    print(f"promotion_safe={report.promotion_safe}")
    print(f"output_json={report.output_json}")
    return 0


def _load_json(path: Path) -> dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def _mapping(value: Any) -> dict[str, Any]:
    return dict(value) if isinstance(value, Mapping) else {}


def _by_model(rows: Any) -> dict[str, dict[str, Any]]:
    out: dict[str, dict[str, Any]] = {}
    for row in rows or []:
        item = _mapping(row)
        model = str(item.get("model") or "")
        if model:
            out[model] = item
    return out


def _market_model_index(rows: Any) -> dict[tuple[str, str], dict[str, Any]]:
    out: dict[tuple[str, str], dict[str, Any]] = {}
    for row in rows or []:
        item = _mapping(row)
        model = str(item.get("model") or "")
        market = str(item.get("market_ticker") or "")
        if model and market:
            out[(model, market)] = item
    return out


def _enriched_rows(
    calibrated_rows: Sequence[Mapping[str, Any]],
    diagnostic_rows: Sequence[Mapping[str, Any]],
) -> list[dict[str, Any]]:
    extra_by_key = {
        _row_key(row): row
        for row in diagnostic_rows
        if _row_key(row)
    }
    out: list[dict[str, Any]] = []
    for row in calibrated_rows:
        item = dict(row)
        extra = extra_by_key.get(_row_key(item), {})
        for field in (
            "independent_spot_age_ms",
            "spot_delta_bps",
            "tick_spot",
            "candle_spot",
            "candidate_id",
            "source_diagnostic_json",
        ):
            if field in extra and field not in item:
                item[field] = extra[field]
        item["seconds_to_close"] = _seconds_between(
            str(item.get("decision_ts_utc") or ""),
            str(item.get("label_available_ts_utc") or ""),
        )
        out.append(item)
    return out


def _row_key(row: Mapping[str, Any]) -> tuple[str, str]:
    return str(row.get("source_capture_id") or ""), str(row.get("row_id") or "")


def _seconds_between(start: str, end: str) -> float | None:
    start_dt = _parse_dt(start)
    end_dt = _parse_dt(end)
    if start_dt is None or end_dt is None:
        return None
    return (end_dt - start_dt).total_seconds()


def _parse_dt(value: str) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None


def _available_models(rows: Sequence[Mapping[str, Any]]) -> tuple[str, ...]:
    models: set[str] = set()
    for row in rows:
        for key in row:
            if key.endswith("_p_yes"):
                models.add(key[: -len("_p_yes")])
    return tuple(sorted(models))


def _select_focus_models(
    summary: Mapping[str, Any],
    available_models: Sequence[str],
    focus_models: Sequence[str] | None,
) -> tuple[str, ...]:
    if focus_models:
        candidates = list(focus_models)
    else:
        candidates = list(DEFAULT_FOCUS_MODELS)
        for key in (
            "best_model_by_brier",
            "best_model_by_logloss",
            "best_model_by_pnl",
            "market_equal_best_model_by_brier",
            "market_equal_best_model_by_logloss",
            "best_calibrated_model",
            "best_blend_model_by_market_equal_brier",
        ):
            value = str(summary.get(key) or "")
            if value:
                candidates.append(value)
    available = set(available_models)
    return tuple(_dedupe(model for model in candidates if model in available))


def _dedupe(values: Sequence[str] | Any) -> list[str]:
    seen: set[str] = set()
    out: list[str] = []
    for value in values:
        if value not in seen:
            seen.add(value)
            out.append(value)
    return out


def _first_existing(values: Sequence[str], candidates: Sequence[str]) -> str:
    existing = set(values)
    for candidate in candidates:
        if candidate in existing:
            return candidate
    return ""


def _model_failure_summary(
    model: str,
    model_rows: Mapping[str, Mapping[str, Any]],
    market_equal_rows: Mapping[str, Mapping[str, Any]],
    market_model_rows: Mapping[tuple[str, str], Mapping[str, Any]],
) -> ModelFailureSummary:
    row = model_rows.get(model, {})
    market_equal = market_equal_rows.get(model, {})
    model_market_rows = [item for (name, _market), item in market_model_rows.items() if name == model]
    return ModelFailureSummary(
        model=model,
        rows=int(row.get("rows", 0) or 0),
        markets=int(row.get("markets", 0) or 0),
        brier=_float(row.get("brier")),
        logloss=_float(row.get("logloss")),
        market_equal_brier=_float(market_equal.get("brier")),
        market_equal_logloss=_float(market_equal.get("logloss")),
        selected_count=int(row.get("selected_count", 0) or 0),
        selected_pnl_cents=_float(row.get("selected_pnl_cents")),
        top_ev_bucket_count=int(row.get("top_ev_bucket_count", 0) or 0),
        top_ev_bucket_pnl_cents=_float(row.get("top_ev_bucket_pnl_cents")),
        positive_selected_market_count=sum(
            1 for item in model_market_rows if _float(item.get("selected_pnl_cents")) > 0.0
        ),
        positive_top_ev_market_count=sum(
            1 for item in model_market_rows if _float(item.get("top_ev_bucket_pnl_cents")) > 0.0
        ),
        negative_selected_market_count=sum(
            1 for item in model_market_rows if _float(item.get("selected_pnl_cents")) < 0.0
        ),
        negative_top_ev_market_count=sum(
            1 for item in model_market_rows if _float(item.get("top_ev_bucket_pnl_cents")) < 0.0
        ),
    )


def _comparison(
    model: str,
    baseline: str,
    model_rows: Mapping[str, Mapping[str, Any]],
    market_equal_rows: Mapping[str, Mapping[str, Any]],
) -> ModelComparisonRow:
    row = model_rows.get(model, {})
    base = model_rows.get(baseline, {})
    market_equal = market_equal_rows.get(model, {})
    market_equal_base = market_equal_rows.get(baseline, {})
    return ModelComparisonRow(
        model=model,
        baseline=baseline,
        rows=int(row.get("rows", 0) or 0),
        markets=int(row.get("markets", 0) or 0),
        row_brier_delta=_float(row.get("brier")) - _float(base.get("brier")),
        row_logloss_delta=_float(row.get("logloss")) - _float(base.get("logloss")),
        row_selected_pnl_delta_cents=_float(row.get("selected_pnl_cents"))
        - _float(base.get("selected_pnl_cents")),
        row_top_ev_bucket_pnl_delta_cents=_float(row.get("top_ev_bucket_pnl_cents"))
        - _float(base.get("top_ev_bucket_pnl_cents")),
        market_equal_brier_delta=_float(market_equal.get("brier"))
        - _float(market_equal_base.get("brier")),
        market_equal_logloss_delta=_float(market_equal.get("logloss"))
        - _float(market_equal_base.get("logloss")),
        market_equal_selected_pnl_delta_cents=_float(market_equal.get("selected_pnl_cents"))
        - _float(market_equal_base.get("selected_pnl_cents")),
        market_equal_top_ev_bucket_pnl_delta_cents=_float(market_equal.get("top_ev_bucket_pnl_cents"))
        - _float(market_equal_base.get("top_ev_bucket_pnl_cents")),
    )


def _top_ev_keys_by_model(
    rows: Sequence[Mapping[str, Any]],
    models: Sequence[str],
) -> dict[str, set[tuple[str, str]]]:
    out: dict[str, set[tuple[str, str]]] = {}
    top_count = max(1, math.ceil(len(rows) * 0.2)) if rows else 0
    for model in models:
        ranked = sorted(
            rows,
            key=lambda row: _float(row.get(f"{model}_side_ev_cents")),
            reverse=True,
        )[:top_count]
        out[model] = {_row_key(row) for row in ranked}
    return out


def _slice_rows(
    rows: Sequence[Mapping[str, Any]],
    models: Sequence[str],
    top_keys_by_model: Mapping[str, set[tuple[str, str]]],
) -> list[SliceRow]:
    slice_groups: dict[tuple[str, str], list[Mapping[str, Any]]] = {}
    for row in rows:
        for slice_type, bucket in _slice_buckets(row):
            slice_groups.setdefault((slice_type, bucket), []).append(row)

    out: list[SliceRow] = []
    for model in models:
        top_keys = top_keys_by_model.get(model, set())
        for (slice_type, bucket), bucket_rows in sorted(slice_groups.items()):
            out.append(_slice_summary(model, slice_type, bucket, bucket_rows, top_keys))
    return out


def _slice_summary(
    model: str,
    slice_type: str,
    bucket: str,
    rows: Sequence[Mapping[str, Any]],
    top_keys: set[tuple[str, str]],
) -> SliceRow:
    selected_rows = [
        row
        for row in rows
        if _float(row.get(f"{model}_side_ev_cents")) > 0.0
    ]
    top_rows = [row for row in rows if _row_key(row) in top_keys]
    return SliceRow(
        model=model,
        slice_type=slice_type,
        bucket=bucket,
        rows=len(rows),
        markets=len({str(row.get("market_ticker") or "") for row in rows if row.get("market_ticker")}),
        brier=_mean(_float(row.get(f"{model}_brier")) for row in rows),
        logloss=_mean(_float(row.get(f"{model}_logloss")) for row in rows),
        selected_count=len(selected_rows),
        selected_pnl_cents=sum(_float(row.get(f"{model}_side_pnl_if_selected_cents")) for row in selected_rows),
        top_ev_bucket_count=len(top_rows),
        top_ev_bucket_pnl_cents=sum(
            _selected_or_forced_pnl(row, model) for row in top_rows
        ),
        positive_selected_market_count=_positive_market_count(selected_rows, model, "selected"),
        positive_top_ev_market_count=_positive_top_market_count(top_rows, model),
    )


def _slice_buckets(row: Mapping[str, Any]) -> tuple[tuple[str, str], ...]:
    candidate = _float_or_none(row.get("candidate_raw_p_yes"))
    v28 = _float_or_none(row.get("v28_p_yes"))
    market = _float_or_none(row.get("market_side_ask_p_yes"))
    return (
        ("side", str(row.get("side") or "missing")),
        ("ask_band", _ask_band(_float_or_none(row.get("ask_cents")))),
        ("time_to_close_band", _time_to_close_band(_float_or_none(row.get("seconds_to_close")))),
        ("spot_age_band", _spot_age_band(_float_or_none(row.get("independent_spot_age_ms")))),
        ("spot_delta_abs_bps_band", _spot_delta_abs_band(_float_or_none(row.get("spot_delta_bps")))),
        ("candidate_v28_disagreement_band", _prob_gap_band(_abs_gap(candidate, v28))),
        ("market_v28_disagreement_band", _prob_gap_band(_abs_gap(market, v28))),
    )


def _ask_band(value: float | None) -> str:
    if value is None:
        return "missing"
    if value < 20:
        return "00_20"
    if value < 40:
        return "20_40"
    if value < 60:
        return "40_60"
    if value < 80:
        return "60_80"
    return "80_100"


def _time_to_close_band(value: float | None) -> str:
    if value is None:
        return "missing"
    if value <= 60:
        return "000_060s"
    if value <= 180:
        return "061_180s"
    if value <= 300:
        return "181_300s"
    if value <= 600:
        return "301_600s"
    return "600s_plus"


def _spot_age_band(value: float | None) -> str:
    if value is None:
        return "missing"
    if value <= 500:
        return "0000_0500ms"
    if value <= 2_000:
        return "0501_2000ms"
    if value <= 5_000:
        return "2001_5000ms"
    return "5000ms_plus"


def _spot_delta_abs_band(value: float | None) -> str:
    if value is None:
        return "missing"
    value = abs(value)
    if value <= 1:
        return "00_01bps"
    if value <= 5:
        return "01_05bps"
    if value <= 15:
        return "05_15bps"
    return "15bps_plus"


def _prob_gap_band(value: float | None) -> str:
    if value is None:
        return "missing"
    if value <= 0.05:
        return "00_05pp"
    if value <= 0.15:
        return "05_15pp"
    if value <= 0.30:
        return "15_30pp"
    return "30pp_plus"


def _abs_gap(left: float | None, right: float | None) -> float | None:
    if left is None or right is None:
        return None
    return abs(left - right)


def _worst_market_drivers(
    model: str,
    calibrated_rows: Sequence[Mapping[str, Any]],
    market_model_rows: Mapping[tuple[str, str], Mapping[str, Any]],
    *,
    limit: int,
) -> list[MarketDriverRow]:
    driver_rows: list[MarketDriverRow] = []
    y_by_market = _label_by_market(calibrated_rows)
    markets = sorted({market for name, market in market_model_rows if name == model})
    for market in markets:
        item = market_model_rows.get((model, market), {})
        base = market_model_rows.get(("v28", market), {})
        driver_rows.append(
            MarketDriverRow(
                model=model,
                market_ticker=market,
                rows=int(item.get("rows", 0) or 0),
                y_yes_win=y_by_market.get(market, 0),
                label_available_ts_utc=str(item.get("label_available_ts_utc") or ""),
                brier=_float(item.get("brier")),
                logloss=_float(item.get("logloss")),
                selected_count=int(item.get("selected_count", 0) or 0),
                selected_pnl_cents=_float(item.get("selected_pnl_cents")),
                top_ev_bucket_count=int(item.get("top_ev_bucket_count", 0) or 0),
                top_ev_bucket_pnl_cents=_float(item.get("top_ev_bucket_pnl_cents")),
                selected_pnl_delta_vs_v28_cents=(
                    _float(item.get("selected_pnl_cents")) - _float(base.get("selected_pnl_cents"))
                    if base
                    else None
                ),
                top_ev_bucket_pnl_delta_vs_v28_cents=(
                    _float(item.get("top_ev_bucket_pnl_cents"))
                    - _float(base.get("top_ev_bucket_pnl_cents"))
                    if base
                    else None
                ),
            )
        )
    return sorted(driver_rows, key=lambda row: (row.selected_pnl_cents, row.top_ev_bucket_pnl_cents))[:limit]


def _label_by_market(rows: Sequence[Mapping[str, Any]]) -> dict[str, int]:
    out: dict[str, int] = {}
    for row in rows:
        market = str(row.get("market_ticker") or "")
        if market and market not in out:
            out[market] = int(_float(row.get("y_yes_win")))
    return out


def _posthoc_slice_candidates(slice_rows: Sequence[SliceRow]) -> list[PosthocSliceCandidate]:
    candidates: list[PosthocSliceCandidate] = []
    for row in slice_rows:
        if row.rows < 50 or row.markets < 5:
            continue
        if row.selected_count <= 0 or row.selected_pnl_cents <= 0.0 or row.top_ev_bucket_pnl_cents <= 0.0:
            continue
        share = row.positive_selected_market_count / row.markets if row.markets else 0.0
        if share < 0.60:
            continue
        candidates.append(
            PosthocSliceCandidate(
                model=row.model,
                slice_type=row.slice_type,
                bucket=row.bucket,
                rows=row.rows,
                markets=row.markets,
                selected_count=row.selected_count,
                selected_pnl_cents=row.selected_pnl_cents,
                top_ev_bucket_pnl_cents=row.top_ev_bucket_pnl_cents,
                positive_selected_market_count=row.positive_selected_market_count,
                positive_market_share=share,
                note="post-hoc only; predeclare this slice before any fresh shadow validation",
            )
        )
    return sorted(
        candidates,
        key=lambda row: (row.positive_market_share, row.selected_pnl_cents, row.top_ev_bucket_pnl_cents),
        reverse=True,
    )[:20]


def _positive_market_count(
    rows: Sequence[Mapping[str, Any]],
    model: str,
    mode: str,
) -> int:
    by_market: dict[str, float] = {}
    for row in rows:
        market = str(row.get("market_ticker") or "")
        if not market:
            continue
        if mode == "selected":
            pnl = _float(row.get(f"{model}_side_pnl_if_selected_cents"))
        else:
            pnl = _selected_or_forced_pnl(row, model)
        by_market[market] = by_market.get(market, 0.0) + pnl
    return sum(1 for pnl in by_market.values() if pnl > 0.0)


def _positive_top_market_count(rows: Sequence[Mapping[str, Any]], model: str) -> int:
    by_market: dict[str, float] = {}
    for row in rows:
        market = str(row.get("market_ticker") or "")
        if market:
            by_market[market] = by_market.get(market, 0.0) + _selected_or_forced_pnl(row, model)
    return sum(1 for pnl in by_market.values() if pnl > 0.0)


def _selected_or_forced_pnl(row: Mapping[str, Any], model: str) -> float:
    # Top-EV buckets include the model's highest-ranked rows even when EV is
    # negative in pathological cases. Use the actual side payoff for those rows.
    selected_pnl = _float(row.get(f"{model}_side_pnl_if_selected_cents"))
    if selected_pnl != 0.0:
        return selected_pnl
    side = str(row.get("side") or "").lower()
    y = int(_float(row.get("y_yes_win")))
    ask = _float(row.get("ask_cents"))
    side_won = bool(y) if side == "yes" else not bool(y)
    return (100.0 - ask) if side_won else -ask


def _float(value: Any) -> float:
    parsed = _float_or_none(value)
    return 0.0 if parsed is None else parsed


def _float_or_none(value: Any) -> float | None:
    try:
        parsed = float(value)
    except (TypeError, ValueError):
        return None
    if not math.isfinite(parsed):
        return None
    return parsed


def _mean(values: Any) -> float:
    items = [float(value) for value in values]
    return sum(items) / len(items) if items else 0.0


def _conclusion(
    summary: Mapping[str, Any],
    comparisons: Sequence[ModelComparisonRow],
    worst_market_drivers: Sequence[MarketDriverRow],
    posthoc_slice_candidates: Sequence[PosthocSliceCandidate],
) -> str:
    best_blend = str(summary.get("best_blend_model_by_market_equal_brier") or "")
    best_blend_vs_candle = next(
        (
            row
            for row in comparisons
            if row.model == best_blend and row.baseline == "candle_brownian"
        ),
        None,
    )
    fragments = [
        "Post-hoc diagnostic only: promotion remains blocked.",
    ]
    if best_blend and best_blend_vs_candle:
        fragments.append(
            f"{best_blend} market-equal Brier delta vs candle_brownian is "
            f"{best_blend_vs_candle.market_equal_brier_delta:.6f} and logloss delta is "
            f"{best_blend_vs_candle.market_equal_logloss_delta:.6f} "
            "(negative is better; mixed signs block promotion)."
        )
    if worst_market_drivers:
        worst = worst_market_drivers[0]
        fragments.append(
            f"Worst selected-PnL market for the focus blend is {worst.market_ticker} "
            f"at {worst.selected_pnl_cents:.1f}c."
        )
    if posthoc_slice_candidates:
        top = posthoc_slice_candidates[0]
        fragments.append(
            f"Best post-hoc slice candidate is {top.model}/{top.slice_type}={top.bucket} "
            f"with {top.positive_selected_market_count}/{top.markets} positive markets; "
            "it must be predeclared before fresh shadow validation."
        )
    else:
        fragments.append("No slice met the conservative post-hoc nomination filter.")
    return " ".join(fragments)


def _markdown(report: PairedSidecarBlendFailureAnalysisReport) -> str:
    lines = [
        "# Paired Sidecar Blend Failure Analysis",
        "",
        f"- generated_utc: `{report.generated_utc}`",
        f"- rows: `{report.rows}`",
        f"- markets: `{report.markets}`",
        f"- promotion_allowed: `{report.promotion_allowed}`",
        f"- promotion_safe: `{report.promotion_safe}`",
        f"- conclusion: {report.conclusion}",
        "",
        "## Model summaries",
        "",
        "| model | brier | logloss | market_eq_brier | selected_pnl_c | top_ev_pnl_c | pos_selected_mkts | pos_top_mkts |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for row in report.model_summaries:
        lines.append(
            f"| {row.model} | {row.brier:.6f} | {row.logloss:.6f} | "
            f"{row.market_equal_brier:.6f} | {row.selected_pnl_cents:.1f} | "
            f"{row.top_ev_bucket_pnl_cents:.1f} | {row.positive_selected_market_count}/{row.markets} | "
            f"{row.positive_top_ev_market_count}/{row.markets} |"
        )
    lines.extend(
        [
            "",
            "## Baseline deltas",
            "",
            "Negative Brier/logloss deltas are better. Positive PnL deltas are better.",
            "",
            "| model | baseline | row_brier_d | row_logloss_d | row_top_ev_pnl_d_c | mkt_eq_brier_d | mkt_eq_logloss_d | mkt_eq_top_ev_pnl_d_c |",
            "| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |",
        ]
    )
    for row in report.comparisons:
        if row.model not in report.focus_models[:]:
            continue
        lines.append(
            f"| {row.model} | {row.baseline} | {row.row_brier_delta:.6f} | "
            f"{row.row_logloss_delta:.6f} | {row.row_top_ev_bucket_pnl_delta_cents:.1f} | "
            f"{row.market_equal_brier_delta:.6f} | {row.market_equal_logloss_delta:.6f} | "
            f"{row.market_equal_top_ev_bucket_pnl_delta_cents:.1f} |"
        )
    lines.extend(
        [
            "",
            "## Worst focus-blend markets",
            "",
            "| model | market | rows | selected_count | selected_pnl_c | top_ev_pnl_c | selected_delta_vs_v28_c |",
            "| --- | --- | ---: | ---: | ---: | ---: | ---: |",
        ]
    )
    for row in report.worst_market_drivers:
        delta = "" if row.selected_pnl_delta_vs_v28_cents is None else f"{row.selected_pnl_delta_vs_v28_cents:.1f}"
        lines.append(
            f"| {row.model} | {row.market_ticker} | {row.rows} | {row.selected_count} | "
            f"{row.selected_pnl_cents:.1f} | {row.top_ev_bucket_pnl_cents:.1f} | {delta} |"
        )
    lines.extend(
        [
            "",
            "## Post-hoc slice candidates",
            "",
            "These are not promotion evidence. They are only candidates for fresh predeclared shadow tests.",
            "",
            "| model | slice | bucket | rows | markets | selected_count | selected_pnl_c | top_ev_pnl_c | positive_markets |",
            "| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |",
        ]
    )
    for row in report.posthoc_slice_candidates[:12]:
        lines.append(
            f"| {row.model} | {row.slice_type} | {row.bucket} | {row.rows} | {row.markets} | "
            f"{row.selected_count} | {row.selected_pnl_cents:.1f} | {row.top_ev_bucket_pnl_cents:.1f} | "
            f"{row.positive_selected_market_count}/{row.markets} |"
        )
    lines.extend(
        [
            "",
            "## Slice rows",
            "",
            "The JSON report contains all slice rows. This markdown shows the 20 strongest positive selected-PnL rows with at least 50 denominator rows.",
            "",
            "| model | slice | bucket | rows | markets | brier | selected_pnl_c | top_ev_pnl_c | positive_selected_mkts |",
            "| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |",
        ]
    )
    displayed = sorted(
        [row for row in report.slice_rows if row.rows >= 50],
        key=lambda row: row.selected_pnl_cents,
        reverse=True,
    )[:20]
    for row in displayed:
        lines.append(
            f"| {row.model} | {row.slice_type} | {row.bucket} | {row.rows} | {row.markets} | "
            f"{row.brier:.6f} | {row.selected_pnl_cents:.1f} | {row.top_ev_bucket_pnl_cents:.1f} | "
            f"{row.positive_selected_market_count}/{row.markets} |"
        )
    lines.append("")
    return "\n".join(lines)


if __name__ == "__main__":
    raise SystemExit(main())
