from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass, replace
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable, Literal, Sequence

from .calibrators import OnlineLogitCalibrator
from .meta_probability_loro import _find_label_path
from .replay_runner import ReplayConfig, ReplayInput, evaluate_replay, load_replay_inputs_from_jsonl


SourceName = Literal[
    "brownian",
    "particle",
    "market",
    "current",
    "market_particle_75_25",
    "brownian_particle_75_25",
    "brownian_market_75_25",
    "brownian_current_75_25",
]
UpdateMode = Literal["row", "market_last"]


@dataclass(frozen=True)
class OnlineAnchorSpec:
    name: str
    source: SourceName
    learning_rate: float
    l2: float
    update_mode: UpdateMode


@dataclass(frozen=True)
class OnlineAnchorRunInput:
    name: str
    root: str
    candidate_path: str
    label_path: str
    row_count: int
    market_count: int


@dataclass(frozen=True)
class OnlineAnchorRunRow:
    run: str
    spec: str
    source: str
    update_mode: str
    candidate_count: int
    market_count: int
    selected_count: int
    raw_brier: float
    raw_log_loss: float
    calibrated_brier: float
    calibrated_log_loss: float
    total_counterfactual_pnl_cents: float
    beats_raw: bool
    beats_brownian: bool
    beats_market: bool
    beats_current_calibrated: bool
    ev_rank_correlation_sign: float
    top_ev_bucket_pnl_cents: float
    strict_gate_pass: bool


@dataclass(frozen=True)
class OnlineAnchorSummaryRow:
    spec: str
    source: str
    update_mode: str
    run_count: int
    total_counterfactual_pnl_cents: float
    mean_raw_brier: float
    mean_calibrated_brier: float
    mean_raw_log_loss: float
    mean_calibrated_log_loss: float
    positive_pnl_count: int
    beats_raw_count: int
    beats_brownian_count: int
    beats_market_count: int
    beats_current_count: int
    positive_ev_rank_count: int
    positive_top_bucket_count: int
    strict_gate_count: int
    strict_all_runs: bool


@dataclass(frozen=True)
class OnlineAnchorCalibrationDiagnosticReport:
    run_inputs: tuple[OnlineAnchorRunInput, ...]
    spec_count: int
    run_rows: tuple[OnlineAnchorRunRow, ...]
    summary_rows: tuple[OnlineAnchorSummaryRow, ...]
    best_by_brier: OnlineAnchorSummaryRow | None
    best_by_pnl: OnlineAnchorSummaryRow | None
    promotion_safe: bool
    conclusion: str


def build_online_anchor_calibration_diagnostic(
    run_roots: Sequence[Path],
    *,
    replay_config: ReplayConfig | None = None,
) -> OnlineAnchorCalibrationDiagnosticReport:
    if not run_roots:
        raise ValueError("at least one run root is required")
    cfg = replay_config or ReplayConfig(min_fill_prob=0.5, counterfactual_fill_threshold=0.5)
    loaded_runs = [_load_run(root) for root in run_roots]
    run_rows: list[OnlineAnchorRunRow] = []
    for run_meta, rows in loaded_runs:
        for spec in _spec_registry():
            raw_rows = [replace(row, particle_p_yes=_source_probability(row, spec.source)) for row in rows]
            calibrated_rows = _online_calibrated_rows(rows, spec)
            raw_replay = evaluate_replay(raw_rows, cfg)
            calibrated_replay = evaluate_replay(calibrated_rows, cfg)
            beats_raw = (
                calibrated_replay.particle.brier < raw_replay.particle.brier
                and calibrated_replay.particle.log_loss < raw_replay.particle.log_loss
            )
            strict = (
                calibrated_replay.total_counterfactual_pnl_cents > 0.0
                and beats_raw
                and calibrated_replay.particle_beats_brownian
                and calibrated_replay.particle_beats_market
                and calibrated_replay.particle_beats_current_calibrated
                and calibrated_replay.ev_rank_correlation_sign > 0.0
                and calibrated_replay.top_ev_bucket_pnl_cents > 0.0
            )
            run_rows.append(
                OnlineAnchorRunRow(
                    run=run_meta.name,
                    spec=spec.name,
                    source=spec.source,
                    update_mode=spec.update_mode,
                    candidate_count=calibrated_replay.candidate_count,
                    market_count=run_meta.market_count,
                    selected_count=calibrated_replay.selected_count,
                    raw_brier=raw_replay.particle.brier,
                    raw_log_loss=raw_replay.particle.log_loss,
                    calibrated_brier=calibrated_replay.particle.brier,
                    calibrated_log_loss=calibrated_replay.particle.log_loss,
                    total_counterfactual_pnl_cents=calibrated_replay.total_counterfactual_pnl_cents,
                    beats_raw=beats_raw,
                    beats_brownian=calibrated_replay.particle_beats_brownian,
                    beats_market=calibrated_replay.particle_beats_market,
                    beats_current_calibrated=calibrated_replay.particle_beats_current_calibrated,
                    ev_rank_correlation_sign=calibrated_replay.ev_rank_correlation_sign,
                    top_ev_bucket_pnl_cents=calibrated_replay.top_ev_bucket_pnl_cents,
                    strict_gate_pass=strict,
                )
            )
    summaries = tuple(_summarize(run_rows))
    best_by_brier = min(summaries, key=lambda row: (row.mean_calibrated_brier, row.mean_calibrated_log_loss), default=None)
    best_by_pnl = max(summaries, key=lambda row: row.total_counterfactual_pnl_cents, default=None)
    strict_candidates = [row for row in summaries if row.strict_all_runs]
    conclusion = (
        "At least one label-gated online anchor calibration cleared every locked run, "
        "but this diagnostic was not predeclared before capture and remains research-only."
        if strict_candidates
        else "No label-gated online anchor calibration clears strict locked-run probability and EV gates."
    )
    return OnlineAnchorCalibrationDiagnosticReport(
        run_inputs=tuple(meta for meta, _ in loaded_runs),
        spec_count=len(_spec_registry()),
        run_rows=tuple(run_rows),
        summary_rows=summaries,
        best_by_brier=best_by_brier,
        best_by_pnl=best_by_pnl,
        promotion_safe=False,
        conclusion=conclusion,
    )


def write_online_anchor_calibration_diagnostic(
    report: OnlineAnchorCalibrationDiagnosticReport,
    output_dir: Path,
    stem: str,
) -> tuple[Path, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    json_path = output_dir / f"{stem}.json"
    md_path = output_dir / f"{stem}.md"
    json_path.write_text(json.dumps(asdict(report), indent=2, sort_keys=True), encoding="utf-8")
    md_path.write_text(_markdown(report), encoding="utf-8")
    return json_path, md_path


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Evaluate label-gated online calibration of Brownian/particle/market probability anchors."
    )
    parser.add_argument("--run-root", action="append", required=True, type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--stem", default="online_anchor_calibration_diagnostic")
    parser.add_argument("--min-fill-prob", default=0.5, type=float)
    parser.add_argument("--counterfactual-fill-threshold", default=0.5, type=float)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    report = build_online_anchor_calibration_diagnostic(
        args.run_root,
        replay_config=ReplayConfig(
            min_fill_prob=args.min_fill_prob,
            counterfactual_fill_threshold=args.counterfactual_fill_threshold,
        ),
    )
    json_path, md_path = write_online_anchor_calibration_diagnostic(report, args.output_dir, args.stem)
    print(f"run_count={len(report.run_inputs)}")
    print(f"spec_count={report.spec_count}")
    print(f"summary_row_count={len(report.summary_rows)}")
    print(f"promotion_safe={report.promotion_safe}")
    if report.best_by_brier:
        print(f"best_by_brier={report.best_by_brier.spec}")
        print(f"best_by_brier_brier={report.best_by_brier.mean_calibrated_brier:.6f}")
    if report.best_by_pnl:
        print(f"best_by_pnl={report.best_by_pnl.spec}")
        print(f"best_by_pnl_total_counterfactual_pnl_cents={report.best_by_pnl.total_counterfactual_pnl_cents:.4f}")
    print(f"json_report={json_path}")
    print(f"md_report={md_path}")
    return 0


def _spec_registry() -> tuple[OnlineAnchorSpec, ...]:
    return (
        OnlineAnchorSpec("online_logit_brownian_lr003_row", "brownian", 0.003, 0.001, "row"),
        OnlineAnchorSpec("online_logit_brownian_lr010_row", "brownian", 0.010, 0.001, "row"),
        OnlineAnchorSpec("online_logit_particle_lr003_row", "particle", 0.003, 0.001, "row"),
        OnlineAnchorSpec("online_logit_market_lr003_row", "market", 0.003, 0.001, "row"),
        OnlineAnchorSpec("online_logit_current_lr003_row", "current", 0.003, 0.001, "row"),
        OnlineAnchorSpec("online_logit_market_particle75_lr003_row", "market_particle_75_25", 0.003, 0.001, "row"),
        OnlineAnchorSpec("online_logit_brownian_particle75_lr003_row", "brownian_particle_75_25", 0.003, 0.001, "row"),
        OnlineAnchorSpec("online_logit_brownian_market75_lr003_row", "brownian_market_75_25", 0.003, 0.001, "row"),
        OnlineAnchorSpec("online_logit_brownian_current75_lr003_row", "brownian_current_75_25", 0.003, 0.001, "row"),
        OnlineAnchorSpec("online_logit_brownian_lr003_marketlast", "brownian", 0.003, 0.001, "market_last"),
        OnlineAnchorSpec("online_logit_particle_lr003_marketlast", "particle", 0.003, 0.001, "market_last"),
        OnlineAnchorSpec("online_logit_market_particle75_lr003_marketlast", "market_particle_75_25", 0.003, 0.001, "market_last"),
    )


def _online_calibrated_rows(rows: Sequence[ReplayInput], spec: OnlineAnchorSpec) -> list[ReplayInput]:
    calibrator = OnlineLogitCalibrator(learning_rate=spec.learning_rate, l2=spec.l2)
    output: list[ReplayInput] = []
    pending_rows: list[tuple[datetime, float, int]] = []
    pending_market_last: dict[str, tuple[datetime, float, int]] = {}
    for row in sorted(rows, key=lambda item: item.snapshot.decision_ts_utc):
        if spec.update_mode == "row":
            _apply_ready_row_updates(calibrator, pending_rows, row.snapshot.decision_ts_utc)
            pending_rows[:] = [item for item in pending_rows if item[0] > row.snapshot.decision_ts_utc]
        else:
            _apply_ready_market_updates(calibrator, pending_market_last, row.snapshot.decision_ts_utc)
        raw_p = _source_probability(row, spec.source)
        calibrated_p = calibrator.predict(raw_p)
        output.append(replace(row, particle_p_yes=_clamp01(calibrated_p)))
        label_int = 1 if row.label.result_yes else 0
        if spec.update_mode == "row":
            pending_rows.append((row.label.label_available_ts_utc, raw_p, label_int))
        else:
            pending_market_last[row.snapshot.market_ticker] = (
                row.label.label_available_ts_utc,
                raw_p,
                label_int,
            )
    if spec.update_mode == "row":
        _apply_ready_row_updates(calibrator, pending_rows, datetime.max.replace(tzinfo=timezone.utc))
    else:
        _apply_ready_market_updates(calibrator, pending_market_last, datetime.max.replace(tzinfo=timezone.utc))
    return output


def _apply_ready_row_updates(
    calibrator: OnlineLogitCalibrator,
    pending: Sequence[tuple[datetime, float, int]],
    now: datetime,
) -> None:
    for _, raw_p, label_int in sorted((item for item in pending if item[0] <= now), key=lambda item: item[0]):
        calibrator.update_with_label(raw_p, label_int)


def _apply_ready_market_updates(
    calibrator: OnlineLogitCalibrator,
    pending_by_market: dict[str, tuple[datetime, float, int]],
    now: datetime,
) -> None:
    ready = [
        (market, item)
        for market, item in pending_by_market.items()
        if item[0] <= now
    ]
    for market, (_, raw_p, label_int) in sorted(ready, key=lambda item: item[1][0]):
        calibrator.update_with_label(raw_p, label_int)
        pending_by_market.pop(market, None)


def _source_probability(row: ReplayInput, source: SourceName) -> float:
    if source == "brownian":
        return _clamp01(row.brownian_p_yes)
    if source == "particle":
        return _clamp01(row.particle_p_yes)
    if source == "market":
        return _clamp01(row.market_p_yes)
    if source == "current":
        return _clamp01(row.current_calibrated_p_yes)
    if source == "market_particle_75_25":
        return _clamp01(0.75 * row.market_p_yes + 0.25 * row.particle_p_yes)
    if source == "brownian_particle_75_25":
        return _clamp01(0.75 * row.brownian_p_yes + 0.25 * row.particle_p_yes)
    if source == "brownian_market_75_25":
        return _clamp01(0.75 * row.brownian_p_yes + 0.25 * row.market_p_yes)
    if source == "brownian_current_75_25":
        return _clamp01(0.75 * row.brownian_p_yes + 0.25 * row.current_calibrated_p_yes)
    raise ValueError(f"unknown source: {source}")


def _load_run(root: Path) -> tuple[OnlineAnchorRunInput, list[ReplayInput]]:
    candidate_path = root / "candidate_snapshots" / "candidate_snapshots.ndjson"
    label_path = _find_label_path(root)
    rows = load_replay_inputs_from_jsonl(candidate_path, label_path)
    meta = OnlineAnchorRunInput(
        name=root.name,
        root=str(root),
        candidate_path=str(candidate_path),
        label_path=str(label_path),
        row_count=len(rows),
        market_count=len({row.snapshot.market_ticker for row in rows}),
    )
    return meta, rows


def _summarize(rows: Sequence[OnlineAnchorRunRow]) -> list[OnlineAnchorSummaryRow]:
    grouped: dict[str, list[OnlineAnchorRunRow]] = {}
    for row in rows:
        grouped.setdefault(row.spec, []).append(row)
    summaries: list[OnlineAnchorSummaryRow] = []
    for spec, group in sorted(grouped.items()):
        run_count = len(group)
        strict_count = sum(1 for row in group if row.strict_gate_pass)
        summaries.append(
            OnlineAnchorSummaryRow(
                spec=spec,
                source=group[0].source,
                update_mode=group[0].update_mode,
                run_count=run_count,
                total_counterfactual_pnl_cents=sum(row.total_counterfactual_pnl_cents for row in group),
                mean_raw_brier=sum(row.raw_brier for row in group) / max(1, run_count),
                mean_calibrated_brier=sum(row.calibrated_brier for row in group) / max(1, run_count),
                mean_raw_log_loss=sum(row.raw_log_loss for row in group) / max(1, run_count),
                mean_calibrated_log_loss=sum(row.calibrated_log_loss for row in group) / max(1, run_count),
                positive_pnl_count=sum(1 for row in group if row.total_counterfactual_pnl_cents > 0.0),
                beats_raw_count=sum(1 for row in group if row.beats_raw),
                beats_brownian_count=sum(1 for row in group if row.beats_brownian),
                beats_market_count=sum(1 for row in group if row.beats_market),
                beats_current_count=sum(1 for row in group if row.beats_current_calibrated),
                positive_ev_rank_count=sum(1 for row in group if row.ev_rank_correlation_sign > 0.0),
                positive_top_bucket_count=sum(1 for row in group if row.top_ev_bucket_pnl_cents > 0.0),
                strict_gate_count=strict_count,
                strict_all_runs=strict_count == run_count,
            )
        )
    return summaries


def _markdown(report: OnlineAnchorCalibrationDiagnosticReport) -> str:
    lines = [
        "# Online Anchor Calibration Diagnostic",
        "",
        f"- run_count: {len(report.run_inputs)}",
        f"- spec_count: {report.spec_count}",
        f"- promotion_safe: {report.promotion_safe}",
        f"- conclusion: {report.conclusion}",
        "",
        "## Summary Rows",
        "",
        "| spec | source | mode | runs | total_pnl_cents | raw_brier | cal_brier | raw_log_loss | cal_log_loss | positive_pnl | beats_raw | beats_brownian | beats_market | beats_current | positive_ev_rank | positive_top_bucket | strict_gates | strict_all_runs |",
        "|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|",
    ]
    for row in sorted(
        report.summary_rows,
        key=lambda item: (not item.strict_all_runs, item.mean_calibrated_brier, -item.total_counterfactual_pnl_cents),
    ):
        lines.append(
            "| {spec} | {source} | {update_mode} | {run_count} | "
            "{total_counterfactual_pnl_cents:.4f} | {mean_raw_brier:.6f} | "
            "{mean_calibrated_brier:.6f} | {mean_raw_log_loss:.6f} | "
            "{mean_calibrated_log_loss:.6f} | {positive_pnl_count} | "
            "{beats_raw_count} | {beats_brownian_count} | {beats_market_count} | "
            "{beats_current_count} | {positive_ev_rank_count} | "
            "{positive_top_bucket_count} | {strict_gate_count} | {strict_all_runs} |".format(
                **asdict(row)
            )
        )
    return "\n".join(lines) + "\n"


def _clamp01(value: float) -> float:
    return max(0.0, min(1.0, float(value)))


if __name__ == "__main__":
    raise SystemExit(main())
