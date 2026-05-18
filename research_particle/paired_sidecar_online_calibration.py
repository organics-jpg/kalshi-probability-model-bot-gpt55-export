from __future__ import annotations

import argparse
import json
import math
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Literal, Mapping, Sequence

from .calibrators import OnlineLogitCalibrator


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INPUT_ROOT = ROOT / "logs" / "particle_research" / "real_shadow" / "sidecar_spot_pairs"
DEFAULT_AGGREGATE_JSON = ROOT / "logs" / "particle_research" / "reports" / "paired_sidecar_spot_aggregate_latest.json"
DEFAULT_OUTPUT_JSON = ROOT / "logs" / "particle_research" / "reports" / "paired_sidecar_online_calibration_latest.json"
DEFAULT_OUTPUT_MD = ROOT / "logs" / "particle_research" / "reports" / "paired_sidecar_online_calibration_latest.md"

UpdateMode = Literal["row", "market_mean"]

BASELINE_MODELS = (
    "candidate_raw",
    "v28",
    "candle_brownian",
    "tick_brownian",
    "market_side_ask",
)

BLEND_WEIGHTS = (0.05, 0.10, 0.15, 0.20, 0.25)


@dataclass(frozen=True)
class OnlineCalibrationSpec:
    name: str
    source_model: str
    learning_rate: float
    l2: float
    update_mode: UpdateMode


@dataclass(frozen=True)
class PreparedRow:
    row: Mapping[str, Any]
    decision_ts_utc: datetime
    label_available_ts_utc: datetime
    market_ticker: str
    source_capture_id: str


@dataclass(frozen=True)
class PairedSidecarOnlineCalibrationSummary:
    schema_version: str
    generated_utc: str
    promotion_allowed: bool
    promotion_status: Mapping[str, Any]
    input_root: str
    input_aggregate_json: str
    output_json: str
    output_md: str
    input_rows: int
    input_markets: int
    prepared_rows: int
    issue_count: int
    spec_count: int
    best_model_by_brier: str
    best_model_by_logloss: str
    best_model_by_pnl: str
    market_equal_best_model_by_brier: str
    market_equal_best_model_by_logloss: str
    raw_candidate_brier: float | None
    best_calibrated_brier: float | None
    raw_candidate_logloss: float | None
    best_calibrated_logloss: float | None
    raw_candidate_top_ev_bucket_pnl_cents: float | None
    best_calibrated_top_ev_bucket_pnl_cents: float | None
    best_calibrated_model: str
    market_count_for_stability: int
    raw_candidate_positive_market_top_ev_count: int
    best_calibrated_positive_market_top_ev_count: int
    best_calibrated_positive_market_selected_pnl_count: int
    best_blend_model_by_market_equal_brier: str
    best_blend_market_equal_brier: float | None
    best_blend_positive_market_top_ev_count: int
    best_blend_positive_market_selected_pnl_count: int
    candidate_ready_for_research: bool
    conclusion: str


def build_paired_sidecar_online_calibration(
    *,
    input_root: Path = DEFAULT_INPUT_ROOT,
    input_aggregate_json: Path = DEFAULT_AGGREGATE_JSON,
    output_json: Path = DEFAULT_OUTPUT_JSON,
    output_md: Path = DEFAULT_OUTPUT_MD,
) -> tuple[PairedSidecarOnlineCalibrationSummary, list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    aggregate = _load_json(input_aggregate_json)
    raw_rows = [row for row in aggregate.get("diagnostic_rows") or [] if isinstance(row, Mapping)]
    close_by_capture = _label_available_by_capture(input_root)
    prepared_rows: list[PreparedRow] = []
    issue_count = 0
    for row in raw_rows:
        prepared = _prepare_row(row, close_by_capture)
        if prepared is None:
            issue_count += 1
            continue
        prepared_rows.append(prepared)

    model_names = list(BASELINE_MODELS) + [spec.name for spec in _spec_registry()] + [spec[0] for spec in _blend_registry()]
    calibrated_rows = _build_calibrated_rows(prepared_rows)
    model_rows = _model_summaries(calibrated_rows, model_names)
    market_equal_model_rows = _market_equal_model_summaries(calibrated_rows, model_names)
    market_model_rows = _market_model_summaries(calibrated_rows, model_names)

    best_brier = min(model_rows, key=lambda row: float(row["brier"]), default={})
    best_logloss = min(model_rows, key=lambda row: float(row["logloss"]), default={})
    best_pnl = max(model_rows, key=lambda row: float(row["top_ev_bucket_pnl_cents"]), default={})
    market_equal_best_brier = min(market_equal_model_rows, key=lambda row: float(row["brier"]), default={})
    market_equal_best_logloss = min(market_equal_model_rows, key=lambda row: float(row["logloss"]), default={})
    by_model = {row["model"]: row for row in model_rows}
    raw = by_model.get("candidate_raw")
    calibrated_only = [row for row in model_rows if str(row.get("model") or "").startswith("online_logit_")]
    best_calibrated = min(calibrated_only, key=lambda row: (float(row["brier"]), float(row["logloss"])), default=None)
    best_calibrated_top = max(calibrated_only, key=lambda row: float(row["top_ev_bucket_pnl_cents"]), default=None)
    best_calibrated_name = str(best_calibrated.get("model", "")) if best_calibrated else ""
    market_equal_blends = [
        row for row in market_equal_model_rows if str(row.get("model") or "").startswith("blend_")
    ]
    best_blend_market_equal = min(
        market_equal_blends,
        key=lambda row: (float(row["brier"]), float(row["logloss"])),
        default=None,
    )
    best_blend_market_equal_name = (
        str(best_blend_market_equal.get("model", "")) if best_blend_market_equal else ""
    )

    conclusion = _conclusion(raw, best_calibrated, best_calibrated_top)
    summary = PairedSidecarOnlineCalibrationSummary(
        schema_version="paired-sidecar-online-calibration-v1",
        generated_utc=datetime.now(timezone.utc).isoformat(),
        promotion_allowed=False,
        promotion_status={
            "allowed": False,
            "reason": "online calibration diagnostic is research-only and label-gated; promotion requires predeclared forward shadow gates",
        },
        input_root=str(input_root),
        input_aggregate_json=str(input_aggregate_json),
        output_json=str(output_json),
        output_md=str(output_md),
        input_rows=len(raw_rows),
        input_markets=len({str(row.get("market_ticker") or "") for row in raw_rows if row.get("market_ticker")}),
        prepared_rows=len(prepared_rows),
        issue_count=issue_count,
        spec_count=len(_spec_registry()),
        best_model_by_brier=str(best_brier.get("model", "")),
        best_model_by_logloss=str(best_logloss.get("model", "")),
        best_model_by_pnl=str(best_pnl.get("model", "")),
        market_equal_best_model_by_brier=str(market_equal_best_brier.get("model", "")),
        market_equal_best_model_by_logloss=str(market_equal_best_logloss.get("model", "")),
        raw_candidate_brier=float(raw["brier"]) if raw else None,
        best_calibrated_brier=float(best_calibrated["brier"]) if best_calibrated else None,
        raw_candidate_logloss=float(raw["logloss"]) if raw else None,
        best_calibrated_logloss=float(best_calibrated["logloss"]) if best_calibrated else None,
        raw_candidate_top_ev_bucket_pnl_cents=(
            float(raw["top_ev_bucket_pnl_cents"]) if raw else None
        ),
        best_calibrated_top_ev_bucket_pnl_cents=(
            float(best_calibrated_top["top_ev_bucket_pnl_cents"]) if best_calibrated_top else None
        ),
        best_calibrated_model=best_calibrated_name,
        market_count_for_stability=len({str(row.get("market_ticker") or "") for row in calibrated_rows if row.get("market_ticker")}),
        raw_candidate_positive_market_top_ev_count=_positive_market_count(
            market_model_rows,
            "candidate_raw",
            "top_ev_bucket_pnl_cents",
        ),
        best_calibrated_positive_market_top_ev_count=_positive_market_count(
            market_model_rows,
            best_calibrated_name,
            "top_ev_bucket_pnl_cents",
        ),
        best_calibrated_positive_market_selected_pnl_count=_positive_market_count(
            market_model_rows,
            best_calibrated_name,
            "selected_pnl_cents",
        ),
        best_blend_model_by_market_equal_brier=best_blend_market_equal_name,
        best_blend_market_equal_brier=(
            float(best_blend_market_equal["brier"]) if best_blend_market_equal else None
        ),
        best_blend_positive_market_top_ev_count=_positive_market_count(
            market_model_rows,
            best_blend_market_equal_name,
            "top_ev_bucket_pnl_cents",
        ),
        best_blend_positive_market_selected_pnl_count=_positive_market_count(
            market_model_rows,
            best_blend_market_equal_name,
            "selected_pnl_cents",
        ),
        candidate_ready_for_research=bool(prepared_rows),
        conclusion=conclusion,
    )
    return summary, model_rows, market_equal_model_rows, calibrated_rows, market_model_rows


def write_paired_sidecar_online_calibration(
    summary: PairedSidecarOnlineCalibrationSummary,
    model_rows: list[dict[str, Any]],
    market_equal_model_rows: list[dict[str, Any]],
    calibrated_rows: list[dict[str, Any]],
    market_model_rows: list[dict[str, Any]],
) -> None:
    output_json = Path(summary.output_json)
    output_md = Path(summary.output_md)
    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_md.parent.mkdir(parents=True, exist_ok=True)
    output_json.write_text(
        json.dumps(
            {
                "summary": asdict(summary),
                "model_rows": model_rows,
                "market_equal_model_rows": market_equal_model_rows,
                "calibrated_rows": calibrated_rows,
                "market_model_rows": market_model_rows,
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    output_md.write_text(_markdown(summary, model_rows, market_equal_model_rows), encoding="utf-8")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Research-only label-gated online calibration diagnostic for paired sidecar live-shadow rows."
    )
    parser.add_argument("--input-root", type=Path, default=DEFAULT_INPUT_ROOT)
    parser.add_argument("--input-aggregate-json", type=Path, default=DEFAULT_AGGREGATE_JSON)
    parser.add_argument("--output-json", type=Path, default=DEFAULT_OUTPUT_JSON)
    parser.add_argument("--output-md", type=Path, default=DEFAULT_OUTPUT_MD)
    parser.add_argument("--write", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    summary, model_rows, market_equal_model_rows, calibrated_rows, market_model_rows = build_paired_sidecar_online_calibration(
        input_root=args.input_root,
        input_aggregate_json=args.input_aggregate_json,
        output_json=args.output_json,
        output_md=args.output_md,
    )
    if args.write:
        write_paired_sidecar_online_calibration(
            summary,
            model_rows,
            market_equal_model_rows,
            calibrated_rows,
            market_model_rows,
        )
    print(f"candidate_ready_for_research={summary.candidate_ready_for_research}")
    print(f"prepared_rows={summary.prepared_rows}")
    print(f"input_markets={summary.input_markets}")
    print(f"best_model_by_brier={summary.best_model_by_brier}")
    print(f"best_model_by_logloss={summary.best_model_by_logloss}")
    print(f"raw_candidate_brier={summary.raw_candidate_brier}")
    print(f"best_calibrated_brier={summary.best_calibrated_brier}")
    print(f"raw_candidate_logloss={summary.raw_candidate_logloss}")
    print(f"best_calibrated_logloss={summary.best_calibrated_logloss}")
    print(f"raw_candidate_top_ev_bucket_pnl_cents={summary.raw_candidate_top_ev_bucket_pnl_cents}")
    print(f"best_calibrated_top_ev_bucket_pnl_cents={summary.best_calibrated_top_ev_bucket_pnl_cents}")
    print(f"best_calibrated_model={summary.best_calibrated_model}")
    print(f"market_count_for_stability={summary.market_count_for_stability}")
    print(f"best_calibrated_positive_market_top_ev_count={summary.best_calibrated_positive_market_top_ev_count}")
    print(f"best_calibrated_positive_market_selected_pnl_count={summary.best_calibrated_positive_market_selected_pnl_count}")
    print(f"best_blend_model_by_market_equal_brier={summary.best_blend_model_by_market_equal_brier}")
    print(f"best_blend_market_equal_brier={summary.best_blend_market_equal_brier}")
    print(f"best_blend_positive_market_top_ev_count={summary.best_blend_positive_market_top_ev_count}")
    print(f"best_blend_positive_market_selected_pnl_count={summary.best_blend_positive_market_selected_pnl_count}")
    print(f"promotion_allowed={summary.promotion_allowed}")
    print(f"output_json={summary.output_json}")
    return 0


def _spec_registry() -> tuple[OnlineCalibrationSpec, ...]:
    return (
        OnlineCalibrationSpec("online_logit_candidate_lr003_row", "candidate", 0.003, 0.001, "row"),
        OnlineCalibrationSpec("online_logit_candidate_lr010_row", "candidate", 0.010, 0.001, "row"),
        OnlineCalibrationSpec("online_logit_candidate_lr030_row", "candidate", 0.030, 0.001, "row"),
        OnlineCalibrationSpec("online_logit_candidate_lr003_market_mean", "candidate", 0.003, 0.001, "market_mean"),
        OnlineCalibrationSpec("online_logit_candidate_lr010_market_mean", "candidate", 0.010, 0.001, "market_mean"),
        OnlineCalibrationSpec("online_logit_candidate_lr030_market_mean", "candidate", 0.030, 0.001, "market_mean"),
    )


def _blend_registry() -> tuple[tuple[str, str, str, float], ...]:
    blends: list[tuple[str, str, str, float]] = []
    for weight in BLEND_WEIGHTS:
        tag = int(round(weight * 100))
        blends.append(
            (
                f"blend_v28_online_lr010_w{tag:02d}",
                "v28",
                "online_logit_candidate_lr010_row",
                weight,
            )
        )
        blends.append(
            (
                f"blend_market_online_lr010_w{tag:02d}",
                "market_side_ask",
                "online_logit_candidate_lr010_row",
                weight,
            )
        )
    return tuple(blends)


def _build_calibrated_rows(prepared_rows: Sequence[PreparedRow]) -> list[dict[str, Any]]:
    sorted_rows = sorted(prepared_rows, key=lambda item: item.decision_ts_utc)
    spec_predictions = {
        spec.name: _predict_with_spec(sorted_rows, spec)
        for spec in _spec_registry()
    }
    output: list[dict[str, Any]] = []
    for idx, prepared in enumerate(sorted_rows):
        base = prepared.row
        out = {
            "row_id": str(base.get("row_id") or ""),
            "market_ticker": prepared.market_ticker,
            "source_capture_id": prepared.source_capture_id,
            "decision_ts_utc": prepared.decision_ts_utc.isoformat(),
            "label_available_ts_utc": prepared.label_available_ts_utc.isoformat(),
            "side": str(base.get("side") or "").lower(),
            "ask_cents": _required_float(base.get("ask_cents"), "ask_cents"),
            "y_yes_win": _label(base),
        }
        probabilities = {
            "candidate_raw": _probability(base, "candidate"),
            "v28": _probability(base, "v28"),
            "candle_brownian": _probability(base, "candle_brownian"),
            "tick_brownian": _probability(base, "tick_brownian"),
            "market_side_ask": _probability(base, "market_side_ask"),
        }
        for name, predictions in spec_predictions.items():
            probabilities[name] = predictions[idx]
        for name, anchor_model, online_model, weight in _blend_registry():
            probabilities[name] = _clamp01(
                (1.0 - weight) * probabilities[anchor_model]
                + weight * probabilities[online_model]
            )
        for model, p_yes in probabilities.items():
            _add_model_metrics(out, model, p_yes)
        output.append(out)
    return output


def _predict_with_spec(rows: Sequence[PreparedRow], spec: OnlineCalibrationSpec) -> list[float]:
    calibrator = OnlineLogitCalibrator(learning_rate=spec.learning_rate, l2=spec.l2)
    predictions: list[float] = []
    pending_rows: list[tuple[datetime, float, int]] = []
    pending_market_values: dict[str, tuple[datetime, list[float], int]] = {}
    for prepared in rows:
        if spec.update_mode == "row":
            _apply_ready_row_updates(calibrator, pending_rows, prepared.decision_ts_utc)
            pending_rows[:] = [item for item in pending_rows if item[0] > prepared.decision_ts_utc]
        else:
            _apply_ready_market_updates(calibrator, pending_market_values, prepared.decision_ts_utc)

        raw_p = _probability(prepared.row, spec.source_model)
        predictions.append(_clamp01(calibrator.predict(raw_p)))
        label = _label(prepared.row)
        if spec.update_mode == "row":
            pending_rows.append((prepared.label_available_ts_utc, raw_p, label))
        else:
            existing = pending_market_values.get(prepared.market_ticker)
            if existing is None:
                pending_market_values[prepared.market_ticker] = (
                    prepared.label_available_ts_utc,
                    [raw_p],
                    label,
                )
            else:
                available_ts, values, existing_label = existing
                values.append(raw_p)
                pending_market_values[prepared.market_ticker] = (
                    max(available_ts, prepared.label_available_ts_utc),
                    values,
                    existing_label if existing_label == label else label,
                )
    return predictions


def _apply_ready_row_updates(
    calibrator: OnlineLogitCalibrator,
    pending_rows: Sequence[tuple[datetime, float, int]],
    decision_ts: datetime,
) -> None:
    for available_ts, raw_p, label in pending_rows:
        if available_ts <= decision_ts:
            calibrator.update_with_label(raw_p, label)


def _apply_ready_market_updates(
    calibrator: OnlineLogitCalibrator,
    pending_market_values: dict[str, tuple[datetime, list[float], int]],
    decision_ts: datetime,
) -> None:
    ready = [
        market
        for market, (available_ts, _values, _label) in pending_market_values.items()
        if available_ts <= decision_ts
    ]
    for market in sorted(ready):
        _available_ts, values, label = pending_market_values.pop(market)
        if values:
            calibrator.update_with_label(sum(values) / len(values), label)


def _add_model_metrics(out: dict[str, Any], model: str, p_yes: float) -> None:
    side = str(out["side"]).lower()
    ask = float(out["ask_cents"])
    y = int(out["y_yes_win"])
    p_side = p_yes if side == "yes" else 1.0 - p_yes
    side_won = bool(y) if side == "yes" else not bool(y)
    ev = p_side * 100.0 - ask
    pnl = (100.0 - ask) if side_won else -ask
    out[f"{model}_p_yes"] = p_yes
    out[f"{model}_brier"] = (p_yes - y) ** 2
    out[f"{model}_logloss"] = _logloss(p_yes, y)
    out[f"{model}_side_ev_cents"] = ev
    out[f"{model}_side_pnl_if_selected_cents"] = pnl if ev > 0.0 else 0.0


def _model_summaries(rows: Sequence[Mapping[str, Any]], model_names: Sequence[str]) -> list[dict[str, Any]]:
    summaries: list[dict[str, Any]] = []
    for model in model_names:
        if not rows:
            summaries.append(_empty_summary(model))
            continue
        evs = [float(row[f"{model}_side_ev_cents"]) for row in rows]
        pnls = [float(row[f"{model}_side_pnl_if_selected_cents"]) for row in rows]
        selected = [pnl for ev, pnl in zip(evs, pnls) if ev > 0.0]
        top_count = max(1, math.ceil(len(rows) * 0.2))
        ranked = sorted(zip(evs, pnls), key=lambda item: item[0], reverse=True)[:top_count]
        summaries.append(
            {
                "model": model,
                "rows": len(rows),
                "markets": len({str(row.get("market_ticker") or "") for row in rows if row.get("market_ticker")}),
                "brier": _mean(float(row[f"{model}_brier"]) for row in rows),
                "logloss": _mean(float(row[f"{model}_logloss"]) for row in rows),
                "mean_side_ev_cents": _mean(evs),
                "selected_count": len(selected),
                "selected_pnl_cents": sum(selected),
                "top_ev_bucket_count": len(ranked),
                "top_ev_bucket_pnl_cents": sum(pnl for _ev, pnl in ranked),
                "promotion_safe": False,
            }
        )
    return summaries


def _market_equal_model_summaries(rows: Sequence[Mapping[str, Any]], model_names: Sequence[str]) -> list[dict[str, Any]]:
    by_market: dict[str, list[Mapping[str, Any]]] = {}
    for row in rows:
        market = str(row.get("market_ticker") or "")
        if market:
            by_market.setdefault(market, []).append(row)
    if not by_market:
        return _model_summaries([], model_names)

    per_market = [_model_summaries(market_rows, model_names) for market_rows in by_market.values()]
    summaries: list[dict[str, Any]] = []
    for model in model_names:
        model_rows = [next((row for row in market_rows if row["model"] == model), None) for market_rows in per_market]
        model_rows = [row for row in model_rows if row is not None]
        summaries.append(
            {
                "model": model,
                "rows": sum(int(row.get("rows", 0) or 0) for row in model_rows),
                "markets": len(model_rows),
                "brier": _mean(float(row.get("brier", 0.0) or 0.0) for row in model_rows),
                "logloss": _mean(float(row.get("logloss", 0.0) or 0.0) for row in model_rows),
                "mean_side_ev_cents": _mean(float(row.get("mean_side_ev_cents", 0.0) or 0.0) for row in model_rows),
                "selected_count": sum(int(row.get("selected_count", 0) or 0) for row in model_rows),
                "selected_pnl_cents": _mean(float(row.get("selected_pnl_cents", 0.0) or 0.0) for row in model_rows),
                "top_ev_bucket_count": sum(int(row.get("top_ev_bucket_count", 0) or 0) for row in model_rows),
                "top_ev_bucket_pnl_cents": _mean(
                    float(row.get("top_ev_bucket_pnl_cents", 0.0) or 0.0) for row in model_rows
                ),
                "promotion_safe": False,
            }
        )
    return summaries


def _market_model_summaries(rows: Sequence[Mapping[str, Any]], model_names: Sequence[str]) -> list[dict[str, Any]]:
    by_market: dict[str, list[Mapping[str, Any]]] = {}
    for row in rows:
        market = str(row.get("market_ticker") or "")
        if market:
            by_market.setdefault(market, []).append(row)
    market_rows: list[dict[str, Any]] = []
    for market, rows_for_market in sorted(by_market.items()):
        close_ts = max(str(row.get("label_available_ts_utc") or "") for row in rows_for_market)
        for summary in _model_summaries(rows_for_market, model_names):
            item = dict(summary)
            item["market_ticker"] = market
            item["label_available_ts_utc"] = close_ts
            market_rows.append(item)
    return market_rows


def _positive_market_count(
    market_model_rows: Sequence[Mapping[str, Any]],
    model: str,
    field: str,
) -> int:
    if not model:
        return 0
    return sum(
        1
        for row in market_model_rows
        if str(row.get("model") or "") == model and float(row.get(field, 0.0) or 0.0) > 0.0
    )


def _empty_summary(model: str) -> dict[str, Any]:
    return {
        "model": model,
        "rows": 0,
        "markets": 0,
        "brier": 0.0,
        "logloss": 0.0,
        "mean_side_ev_cents": 0.0,
        "selected_count": 0,
        "selected_pnl_cents": 0.0,
        "top_ev_bucket_count": 0,
        "top_ev_bucket_pnl_cents": 0.0,
        "promotion_safe": False,
    }


def _prepare_row(row: Mapping[str, Any], close_by_capture: Mapping[str, datetime]) -> PreparedRow | None:
    capture_id = str(row.get("source_capture_id") or "")
    close_ts = close_by_capture.get(capture_id)
    decision_ts = _parse_dt(row.get("decision_ts_utc"))
    market = str(row.get("market_ticker") or "")
    if not capture_id or close_ts is None or decision_ts is None or not market:
        return None
    return PreparedRow(
        row=row,
        decision_ts_utc=decision_ts,
        label_available_ts_utc=close_ts,
        market_ticker=market,
        source_capture_id=capture_id,
    )


def _label_available_by_capture(input_root: Path) -> dict[str, datetime]:
    out: dict[str, datetime] = {}
    for manifest_path in input_root.glob("*/paired_sidecar_spot_manifest.json"):
        payload = _load_json(manifest_path)
        batch_markets = payload.get("sidecar_batch_markets")
        if not isinstance(batch_markets, list):
            continue
        close_times = [
            _parse_dt(market.get("market_close_ts_utc"))
            for market in batch_markets
            if isinstance(market, Mapping)
        ]
        close_times = [item for item in close_times if item is not None]
        if close_times:
            out[manifest_path.parent.name] = max(close_times)
    return out


def _probability(row: Mapping[str, Any], model: str) -> float:
    field = "candidate_p_yes" if model == "candidate" else f"{model}_p_yes"
    return _clamp01(_required_float(row.get(field), field))


def _label(row: Mapping[str, Any]) -> int:
    value = row.get("y_yes_win")
    if isinstance(value, bool):
        return 1 if value else 0
    parsed = str(value).strip().lower()
    if parsed in {"1", "true", "yes", "y"}:
        return 1
    if parsed in {"0", "false", "no", "n"}:
        return 0
    return int(float(parsed))


def _conclusion(
    raw: Mapping[str, Any] | None,
    best_calibrated: Mapping[str, Any] | None,
    best_calibrated_top: Mapping[str, Any] | None,
) -> str:
    if not raw or not best_calibrated:
        return "No prepared rows were available for label-gated online calibration."
    improved_probability = (
        float(best_calibrated["brier"]) < float(raw["brier"])
        and float(best_calibrated["logloss"]) < float(raw["logloss"])
    )
    top_positive = bool(best_calibrated_top) and float(best_calibrated_top["top_ev_bucket_pnl_cents"]) > 0.0
    if improved_probability and top_positive:
        return (
            "Label-gated online calibration improves raw candidate Brier/log-loss and has a positive top-EV bucket, "
            "but this remains retrospective research-only evidence until predeclared forward shadow passes."
        )
    if improved_probability:
        return (
            "Label-gated online calibration improves raw candidate probability quality, but EV ranking/top-bucket evidence is still insufficient."
        )
    return "Label-gated online calibration does not repair raw candidate probability quality on the current paired aggregate."


def _required_float(value: Any, name: str) -> float:
    try:
        parsed = float(str(value).strip())
    except (TypeError, ValueError):
        raise ValueError(f"missing numeric {name}") from None
    if not math.isfinite(parsed):
        raise ValueError(f"non-finite numeric {name}")
    return parsed


def _clamp01(value: float) -> float:
    return min(1.0 - 1e-12, max(1e-12, float(value)))


def _logloss(p: float, y: int) -> float:
    p = _clamp01(p)
    return -(y * math.log(p) + (1 - y) * math.log(1.0 - p))


def _mean(values: Any) -> float:
    seq = list(values)
    return sum(seq) / len(seq) if seq else 0.0


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


def _load_json(path: Path) -> dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def _markdown(
    summary: PairedSidecarOnlineCalibrationSummary,
    model_rows: Sequence[Mapping[str, Any]],
    market_equal_model_rows: Sequence[Mapping[str, Any]],
) -> str:
    lines = [
        "# Paired Sidecar Online Calibration Diagnostic",
        "",
        "Research-only diagnostic for label-gated online logit calibration of paired live-shadow sidecar rows.",
        "",
        "## Summary",
        "",
        f"- Generated UTC: `{summary.generated_utc}`",
        f"- Promotion allowed: `{summary.promotion_allowed}`",
        f"- Prepared rows / input rows: `{summary.prepared_rows}` / `{summary.input_rows}`",
        f"- Input markets: `{summary.input_markets}`",
        f"- Issue count: `{summary.issue_count}`",
        f"- Best model by Brier: `{summary.best_model_by_brier}`",
        f"- Best model by log loss: `{summary.best_model_by_logloss}`",
        f"- Market-equal best model by Brier: `{summary.market_equal_best_model_by_brier}`",
        f"- Market-equal best model by log loss: `{summary.market_equal_best_model_by_logloss}`",
        f"- Raw candidate Brier / log loss: `{summary.raw_candidate_brier}` / `{summary.raw_candidate_logloss}`",
        f"- Best calibrated Brier / log loss: `{summary.best_calibrated_brier}` / `{summary.best_calibrated_logloss}`",
        f"- Raw / best calibrated top-EV bucket PnL: `{summary.raw_candidate_top_ev_bucket_pnl_cents}` / `{summary.best_calibrated_top_ev_bucket_pnl_cents}`",
        f"- Best calibrated model: `{summary.best_calibrated_model}`",
        f"- Market stability count: `{summary.market_count_for_stability}`",
        f"- Raw / best calibrated positive market top-EV counts: `{summary.raw_candidate_positive_market_top_ev_count}` / `{summary.best_calibrated_positive_market_top_ev_count}`",
        f"- Best calibrated positive market selected-PnL count: `{summary.best_calibrated_positive_market_selected_pnl_count}`",
        f"- Best blend by market-equal Brier: `{summary.best_blend_model_by_market_equal_brier}` / `{summary.best_blend_market_equal_brier}`",
        f"- Best blend positive market top-EV / selected-PnL counts: `{summary.best_blend_positive_market_top_ev_count}` / `{summary.best_blend_positive_market_selected_pnl_count}`",
        f"- Conclusion: {summary.conclusion}",
        "",
        "## Row-Weighted Model Rows",
        "",
        "| model | rows | markets | brier | logloss | selected | selected pnl | top bucket pnl |",
        "|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for row in model_rows:
        lines.append(_model_row_markdown(row))
    lines.extend(
        [
            "",
            "## Market-Equal Model Rows",
            "",
            "| model | rows | markets | brier | logloss | selected | selected pnl | top bucket pnl |",
            "|---|---:|---:|---:|---:|---:|---:|---:|",
        ]
    )
    for row in market_equal_model_rows:
        lines.append(_model_row_markdown(row))
    lines.extend(
        [
            "",
            "## Read",
            "",
            "- Calibrator updates are delayed until each source capture's market close timestamp.",
            "- `market_mean` specs update once per settled market, avoiding repeated same-market row overweighting.",
            "- This file is not a promotion artifact; it is a research diagnostic for the probability-calibration layer.",
        ]
    )
    return "\n".join(lines) + "\n"


def _model_row_markdown(row: Mapping[str, Any]) -> str:
    return (
        f"| `{row['model']}` | {row['rows']} | {row['markets']} | {row['brier']} | "
        f"{row['logloss']} | {row['selected_count']} | {row['selected_pnl_cents']} | "
        f"{row['top_ev_bucket_pnl_cents']} |"
    )


if __name__ == "__main__":
    raise SystemExit(main())
