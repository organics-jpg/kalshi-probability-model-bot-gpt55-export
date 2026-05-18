from __future__ import annotations

import argparse
import bisect
import json
import math
from dataclasses import asdict, dataclass, replace
from pathlib import Path
from typing import Sequence

from .meta_probability_loro import _find_label_path
from .replay_runner import ReplayConfig, ReplayInput, ReplayReport, evaluate_replay, load_replay_inputs_from_jsonl
from .spot_context_merge import SpotTickRow, load_spot_ticks
from .spot_realized_vol_terminal_diagnostic import realized_annualized_vol_at_decision
from .spot_rv_anchor_switch_loro import _market_ev_metrics
from .terminal_projection import brownian_terminal_probability


@dataclass(frozen=True)
class SpotDriftTerminalSpec:
    name: str
    drift_window_seconds: int
    drift_weight: float
    total_drift_cap_bps: float
    vol_window_seconds: int
    fallback_annualized_vol: float
    floor_annualized_vol: float
    cap_annualized_vol: float
    brownian_blend_weight: float


@dataclass(frozen=True)
class SpotDriftRunInput:
    name: str
    root: str
    candidate_path: str
    label_path: str
    spot_tick_path: str
    row_count: int
    market_count: int
    spot_tick_count: int


@dataclass(frozen=True)
class SpotDriftRunRow:
    run: str
    spec: str
    candidate_count: int
    market_count: int
    selected_count: int
    fallback_drift_count: int
    fallback_vol_count: int
    avg_total_drift_bps: float
    avg_annualized_vol: float
    total_counterfactual_pnl_cents: float
    brier: float
    log_loss: float
    beats_brownian: bool
    beats_market: bool
    beats_current_calibrated: bool
    ev_rank_correlation_sign: float
    top_ev_bucket_pnl_cents: float
    market_ev_rank_correlation_sign: float
    top_market_ev_bucket_avg_pnl_cents: float
    strict_gate_pass: bool


@dataclass(frozen=True)
class SpotDriftSummaryRow:
    spec: str
    run_count: int
    total_counterfactual_pnl_cents: float
    mean_brier: float
    mean_log_loss: float
    positive_pnl_count: int
    beats_brownian_count: int
    beats_market_count: int
    beats_current_count: int
    positive_ev_rank_count: int
    positive_top_bucket_count: int
    positive_market_ev_rank_count: int
    positive_market_top_bucket_count: int
    strict_gate_count: int
    strict_all_runs: bool


@dataclass(frozen=True)
class SpotDriftSideRunRow:
    run: str
    spec: str
    side: str
    selected_count: int
    win_count: int
    win_rate: float
    total_counterfactual_pnl_cents: float
    avg_counterfactual_pnl_cents_per_selected: float


@dataclass(frozen=True)
class SpotDriftSideSummaryRow:
    spec: str
    side: str
    run_count: int
    selected_count: int
    win_count: int
    win_rate: float
    total_counterfactual_pnl_cents: float
    avg_counterfactual_pnl_cents_per_selected: float
    positive_pnl_run_count: int


@dataclass(frozen=True)
class SpotDriftTerminalDiagnosticReport:
    run_inputs: tuple[SpotDriftRunInput, ...]
    skipped_run_roots: tuple[str, ...]
    specs: tuple[SpotDriftTerminalSpec, ...]
    run_rows: tuple[SpotDriftRunRow, ...]
    summary_rows: tuple[SpotDriftSummaryRow, ...]
    side_run_rows: tuple[SpotDriftSideRunRow, ...]
    side_summary_rows: tuple[SpotDriftSideSummaryRow, ...]
    candidate_ready_for_predeclared_shadow: bool
    promotion_safe: bool
    conclusion: str


def build_spot_drift_terminal_diagnostic(
    run_roots: Sequence[Path],
    *,
    replay_config: ReplayConfig | None = None,
    max_spot_age_ms: float = 5_000.0,
) -> SpotDriftTerminalDiagnosticReport:
    cfg = replay_config or ReplayConfig(min_fill_prob=0.5, counterfactual_fill_threshold=0.5)
    loaded_runs: list[tuple[SpotDriftRunInput, tuple[ReplayInput, ...], tuple[SpotTickRow, ...]]] = []
    skipped: list[str] = []
    for root in run_roots:
        loaded = _load_eligible_run(root)
        if loaded is None:
            skipped.append(str(root))
        else:
            loaded_runs.append(loaded)
    specs = _specs()
    run_rows: list[SpotDriftRunRow] = []
    side_run_rows: list[SpotDriftSideRunRow] = []
    for meta, rows, ticks in loaded_runs:
        for spec in specs:
            materialized, diagnostics = materialize_spot_drift_terminal_rows(
                rows,
                ticks,
                spec,
                max_spot_age_ms=max_spot_age_ms,
            )
            replay = evaluate_replay(materialized, cfg)
            market_ev_rank, top_market_bucket = _market_ev_metrics(replay)
            side_run_rows.extend(_side_run_rows(meta.name, spec.name, replay))
            run_rows.append(
                SpotDriftRunRow(
                    run=meta.name,
                    spec=spec.name,
                    candidate_count=replay.candidate_count,
                    market_count=meta.market_count,
                    selected_count=replay.selected_count,
                    fallback_drift_count=diagnostics["fallback_drift_count"],
                    fallback_vol_count=diagnostics["fallback_vol_count"],
                    avg_total_drift_bps=diagnostics["avg_total_drift_bps"],
                    avg_annualized_vol=diagnostics["avg_annualized_vol"],
                    total_counterfactual_pnl_cents=replay.total_counterfactual_pnl_cents,
                    brier=replay.particle.brier,
                    log_loss=replay.particle.log_loss,
                    beats_brownian=replay.particle_beats_brownian,
                    beats_market=replay.particle_beats_market,
                    beats_current_calibrated=replay.particle_beats_current_calibrated,
                    ev_rank_correlation_sign=replay.ev_rank_correlation_sign,
                    top_ev_bucket_pnl_cents=replay.top_ev_bucket_pnl_cents,
                    market_ev_rank_correlation_sign=market_ev_rank,
                    top_market_ev_bucket_avg_pnl_cents=top_market_bucket,
                    strict_gate_pass=_strict_gate(replay),
                )
            )
    summaries = tuple(_summarize(run_rows))
    side_summaries = tuple(_summarize_sides(side_run_rows))
    candidate_ready = any(row.strict_all_runs for row in summaries)
    conclusion = (
        "At least one next-second spot-drift terminal diagnostic cleared every eligible locked run. "
        "Because this is same-evidence research, it only nominates a fresh predeclared shadow run."
        if candidate_ready
        else "No next-second spot-drift terminal diagnostic cleared strict eligible locked-run gates."
    )
    return SpotDriftTerminalDiagnosticReport(
        run_inputs=tuple(meta for meta, _, _ in loaded_runs),
        skipped_run_roots=tuple(skipped),
        specs=specs,
        run_rows=tuple(run_rows),
        summary_rows=summaries,
        side_run_rows=tuple(side_run_rows),
        side_summary_rows=side_summaries,
        candidate_ready_for_predeclared_shadow=candidate_ready,
        promotion_safe=False,
        conclusion=conclusion,
    )


def materialize_spot_drift_terminal_rows(
    rows: Sequence[ReplayInput],
    ticks: Sequence[SpotTickRow],
    spec: SpotDriftTerminalSpec,
    *,
    max_spot_age_ms: float = 5_000.0,
) -> tuple[tuple[ReplayInput, ...], dict[str, float | int]]:
    if not rows:
        raise ValueError("at least one replay row is required")
    times = [tick.available_ts_utc for tick in ticks]
    prices = [float(tick.price) for tick in ticks]
    materialized: list[ReplayInput] = []
    fallback_drift_count = 0
    fallback_vol_count = 0
    total_drift_values: list[float] = []
    vol_values: list[float] = []
    for row in sorted(rows, key=lambda item: (item.snapshot.decision_ts_utc, item.snapshot.market_ticker)):
        seconds_to_close = max(0.0, (row.label.settlement_ts_utc - row.snapshot.decision_ts_utc).total_seconds())
        drift_per_second, used_drift_fallback = recent_spot_drift_per_second(
            row,
            times,
            prices,
            spec.drift_window_seconds,
            spec.drift_weight,
            spec.total_drift_cap_bps,
            max_spot_age_ms=max_spot_age_ms,
        )
        ann_vol, used_vol_fallback = realized_annualized_vol_at_decision(
            row.snapshot.decision_ts_utc,
            times,
            prices,
            spec.vol_window_seconds,
            fallback_annualized_vol=spec.fallback_annualized_vol,
            floor_annualized_vol=spec.floor_annualized_vol,
            cap_annualized_vol=spec.cap_annualized_vol,
        )
        fallback_drift_count += int(used_drift_fallback)
        fallback_vol_count += int(used_vol_fallback)
        total_drift_values.append(10_000.0 * drift_per_second * seconds_to_close)
        vol_values.append(ann_vol)
        drift_prob = brownian_terminal_probability(
            row.snapshot.spot,
            row.snapshot.strike,
            seconds_to_close,
            ann_vol,
            drift_per_second=drift_per_second,
        )
        p_yes = spec.brownian_blend_weight * row.brownian_p_yes + (1.0 - spec.brownian_blend_weight) * drift_prob
        materialized.append(replace(row, particle_p_yes=_clamp01(p_yes)))
    diagnostics = {
        "fallback_drift_count": fallback_drift_count,
        "fallback_vol_count": fallback_vol_count,
        "avg_total_drift_bps": _mean(total_drift_values),
        "avg_annualized_vol": _mean(vol_values),
    }
    return tuple(materialized), diagnostics


def recent_spot_drift_per_second(
    row: ReplayInput,
    times: Sequence,
    prices: Sequence[float],
    window_seconds: int,
    drift_weight: float,
    total_drift_cap_bps: float,
    *,
    max_spot_age_ms: float = 5_000.0,
) -> tuple[float, bool]:
    if window_seconds <= 0:
        raise ValueError("window_seconds must be positive")
    if not times or not prices:
        return 0.0, True
    decision_ts = row.snapshot.decision_ts_utc
    end_idx = bisect.bisect_right(times, decision_ts) - 1
    if end_idx < 0:
        return 0.0, True
    age_ms = 1000.0 * (decision_ts - times[end_idx]).total_seconds()
    if age_ms > max_spot_age_ms:
        return 0.0, True
    start_ts = decision_ts - _seconds_delta(window_seconds)
    start_idx = bisect.bisect_left(times, start_ts)
    if start_idx >= end_idx:
        return 0.0, True
    start_price = float(prices[start_idx])
    end_price = float(prices[end_idx])
    if start_price <= 0.0 or end_price <= 0.0:
        return 0.0, True
    raw_drift = drift_weight * math.log(end_price / start_price) / float(window_seconds)
    seconds_to_close = max(0.0, (row.label.settlement_ts_utc - row.snapshot.decision_ts_utc).total_seconds())
    if seconds_to_close <= 0.0:
        return 0.0, False
    cap_log_return = abs(total_drift_cap_bps) / 10_000.0
    capped_total = min(cap_log_return, max(-cap_log_return, raw_drift * seconds_to_close))
    return capped_total / seconds_to_close, False


def write_spot_drift_terminal_diagnostic(
    report: SpotDriftTerminalDiagnosticReport,
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
        description="Evaluate next-second spot-drift terminal probabilities on eligible locked shadow roots."
    )
    parser.add_argument("--run-root", action="append", required=True, type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--stem", default="spot_drift_terminal_diagnostic")
    parser.add_argument("--max-spot-age-ms", default=5_000.0, type=float)
    parser.add_argument("--min-fill-prob", default=0.5, type=float)
    parser.add_argument("--counterfactual-fill-threshold", default=0.5, type=float)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    report = build_spot_drift_terminal_diagnostic(
        args.run_root,
        replay_config=ReplayConfig(
            min_fill_prob=args.min_fill_prob,
            counterfactual_fill_threshold=args.counterfactual_fill_threshold,
        ),
        max_spot_age_ms=args.max_spot_age_ms,
    )
    json_path, md_path = write_spot_drift_terminal_diagnostic(report, args.output_dir, args.stem)
    print(f"eligible_run_count={len(report.run_inputs)}")
    print(f"skipped_run_count={len(report.skipped_run_roots)}")
    print(f"spec_count={len(report.specs)}")
    print(f"run_row_count={len(report.run_rows)}")
    print(f"summary_row_count={len(report.summary_rows)}")
    print(f"candidate_ready_for_predeclared_shadow={report.candidate_ready_for_predeclared_shadow}")
    print(f"promotion_safe={report.promotion_safe}")
    print(f"json_report={json_path}")
    print(f"md_report={md_path}")
    return 0


def _load_eligible_run(root: Path) -> tuple[SpotDriftRunInput, tuple[ReplayInput, ...], tuple[SpotTickRow, ...]] | None:
    candidate_path = root / "candidate_snapshots" / "candidate_snapshots.ndjson"
    spot_path = root / "independent_spot_ticks.ndjson"
    if not candidate_path.exists() or not spot_path.exists():
        return None
    label_path = _find_label_path(root)
    rows = tuple(
        sorted(
            load_replay_inputs_from_jsonl(candidate_path, label_path),
            key=lambda item: (item.snapshot.decision_ts_utc, item.snapshot.market_ticker),
        )
    )
    ticks = tuple(load_spot_ticks(spot_path))
    if not rows or not ticks:
        return None
    meta = SpotDriftRunInput(
        name=root.name,
        root=str(root),
        candidate_path=str(candidate_path),
        label_path=str(label_path),
        spot_tick_path=str(spot_path),
        row_count=len(rows),
        market_count=len({row.snapshot.market_ticker for row in rows}),
        spot_tick_count=len(ticks),
    )
    return meta, rows, ticks


def _specs() -> tuple[SpotDriftTerminalSpec, ...]:
    return (
        SpotDriftTerminalSpec("drift5_cap10_rv89_blend50", 5, 0.50, 10.0, 89, 0.65, 0.20, 1.50, 0.50),
        SpotDriftTerminalSpec("drift13_cap15_rv233_blend50", 13, 0.50, 15.0, 233, 0.65, 0.20, 1.50, 0.50),
        SpotDriftTerminalSpec("drift21_cap20_rv377_blend50", 21, 0.50, 20.0, 377, 0.65, 0.20, 1.50, 0.50),
        SpotDriftTerminalSpec("drift34_cap20_rv610_blend50", 34, 0.50, 20.0, 610, 0.65, 0.20, 1.50, 0.50),
        SpotDriftTerminalSpec("drift13_cap10_fixed65_blend25", 13, 0.50, 10.0, 233, 0.65, 0.65, 0.65, 0.25),
    )


def _strict_gate(report: ReplayReport) -> bool:
    return (
        report.total_counterfactual_pnl_cents > 0.0
        and report.particle_beats_brownian
        and report.particle_beats_market
        and report.particle_beats_current_calibrated
        and report.ev_rank_correlation_sign > 0.0
        and report.top_ev_bucket_pnl_cents > 0.0
    )


def _summarize(rows: Sequence[SpotDriftRunRow]) -> list[SpotDriftSummaryRow]:
    grouped: dict[str, list[SpotDriftRunRow]] = {}
    for row in rows:
        grouped.setdefault(row.spec, []).append(row)
    summaries: list[SpotDriftSummaryRow] = []
    for spec in sorted(grouped):
        spec_rows = grouped[spec]
        strict_count = sum(1 for row in spec_rows if row.strict_gate_pass)
        summaries.append(
            SpotDriftSummaryRow(
                spec=spec,
                run_count=len(spec_rows),
                total_counterfactual_pnl_cents=sum(row.total_counterfactual_pnl_cents for row in spec_rows),
                mean_brier=_mean(row.brier for row in spec_rows),
                mean_log_loss=_mean(row.log_loss for row in spec_rows),
                positive_pnl_count=sum(1 for row in spec_rows if row.total_counterfactual_pnl_cents > 0.0),
                beats_brownian_count=sum(1 for row in spec_rows if row.beats_brownian),
                beats_market_count=sum(1 for row in spec_rows if row.beats_market),
                beats_current_count=sum(1 for row in spec_rows if row.beats_current_calibrated),
                positive_ev_rank_count=sum(1 for row in spec_rows if row.ev_rank_correlation_sign > 0.0),
                positive_top_bucket_count=sum(1 for row in spec_rows if row.top_ev_bucket_pnl_cents > 0.0),
                positive_market_ev_rank_count=sum(
                    1 for row in spec_rows if row.market_ev_rank_correlation_sign > 0.0
                ),
                positive_market_top_bucket_count=sum(
                    1 for row in spec_rows if row.top_market_ev_bucket_avg_pnl_cents > 0.0
                ),
                strict_gate_count=strict_count,
                strict_all_runs=(strict_count == len(spec_rows) and bool(spec_rows)),
            )
        )
    return sorted(
        summaries,
        key=lambda row: (
            row.strict_all_runs,
            row.strict_gate_count,
            row.beats_current_count,
            row.total_counterfactual_pnl_cents,
        ),
        reverse=True,
    )


def _side_run_rows(run: str, spec: str, report: ReplayReport) -> list[SpotDriftSideRunRow]:
    rows: list[SpotDriftSideRunRow] = []
    for side in ("yes", "no"):
        decisions = [decision for decision in report.decisions if decision.selected and decision.side == side]
        pnl = sum(decision.counterfactual_pnl_cents for decision in decisions)
        wins = sum(1 for decision in decisions if decision.won)
        rows.append(
            SpotDriftSideRunRow(
                run=run,
                spec=spec,
                side=side,
                selected_count=len(decisions),
                win_count=wins,
                win_rate=(wins / len(decisions) if decisions else 0.0),
                total_counterfactual_pnl_cents=pnl,
                avg_counterfactual_pnl_cents_per_selected=(pnl / len(decisions) if decisions else 0.0),
            )
        )
    return rows


def _summarize_sides(rows: Sequence[SpotDriftSideRunRow]) -> list[SpotDriftSideSummaryRow]:
    grouped: dict[tuple[str, str], list[SpotDriftSideRunRow]] = {}
    for row in rows:
        grouped.setdefault((row.spec, row.side), []).append(row)
    summaries: list[SpotDriftSideSummaryRow] = []
    for (spec, side), side_rows in sorted(grouped.items()):
        selected = sum(row.selected_count for row in side_rows)
        wins = sum(row.win_count for row in side_rows)
        pnl = sum(row.total_counterfactual_pnl_cents for row in side_rows)
        summaries.append(
            SpotDriftSideSummaryRow(
                spec=spec,
                side=side,
                run_count=len(side_rows),
                selected_count=selected,
                win_count=wins,
                win_rate=(wins / selected if selected else 0.0),
                total_counterfactual_pnl_cents=pnl,
                avg_counterfactual_pnl_cents_per_selected=(pnl / selected if selected else 0.0),
                positive_pnl_run_count=sum(1 for row in side_rows if row.total_counterfactual_pnl_cents > 0.0),
            )
        )
    return sorted(
        summaries,
        key=lambda row: (
            row.spec,
            row.side,
        ),
    )


def _markdown(report: SpotDriftTerminalDiagnosticReport) -> str:
    lines = [
        "# Spot Drift Terminal Diagnostic",
        "",
        f"- eligible_run_count: {len(report.run_inputs)}",
        f"- skipped_run_count: {len(report.skipped_run_roots)}",
        f"- spec_count: {len(report.specs)}",
        f"- candidate_ready_for_predeclared_shadow: {report.candidate_ready_for_predeclared_shadow}",
        f"- promotion_safe: {report.promotion_safe}",
        f"- conclusion: {report.conclusion}",
        "",
        "## Summary",
        "",
        "| spec | runs | pnl_cents | mean_brier | mean_log_loss | positive_pnl | beats_brownian | beats_market | beats_current | ev_rank | top_bucket | market_ev_rank | market_top_bucket | strict | strict_all |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|",
    ]
    for row in report.summary_rows:
        lines.append(
            "| "
            f"{row.spec} | "
            f"{row.run_count} | "
            f"{row.total_counterfactual_pnl_cents:.4f} | "
            f"{row.mean_brier:.6f} | "
            f"{row.mean_log_loss:.6f} | "
            f"{row.positive_pnl_count}/{row.run_count} | "
            f"{row.beats_brownian_count}/{row.run_count} | "
            f"{row.beats_market_count}/{row.run_count} | "
            f"{row.beats_current_count}/{row.run_count} | "
            f"{row.positive_ev_rank_count}/{row.run_count} | "
            f"{row.positive_top_bucket_count}/{row.run_count} | "
            f"{row.positive_market_ev_rank_count}/{row.run_count} | "
            f"{row.positive_market_top_bucket_count}/{row.run_count} | "
            f"{row.strict_gate_count}/{row.run_count} | "
            f"{row.strict_all_runs} |"
        )
    lines.extend(
        [
            "",
            "## Side Summary",
            "",
            "| spec | side | runs | selected | win_rate | pnl_cents | avg_pnl_selected | positive_pnl_runs |",
            "|---|---|---:|---:|---:|---:|---:|---:|",
        ]
    )
    for row in report.side_summary_rows:
        lines.append(
            "| "
            f"{row.spec} | "
            f"{row.side} | "
            f"{row.run_count} | "
            f"{row.selected_count} | "
            f"{row.win_rate:.6f} | "
            f"{row.total_counterfactual_pnl_cents:.4f} | "
            f"{row.avg_counterfactual_pnl_cents_per_selected:.4f} | "
            f"{row.positive_pnl_run_count}/{row.run_count} |"
        )
    lines.extend(
        [
            "",
            "## Runs",
            "",
            "| run | spec | candidates | markets | selected | drift_fallback | vol_fallback | avg_drift_bps | avg_vol | pnl_cents | brier | beats_current | ev_rank | top_bucket | market_ev_rank | market_top_bucket | strict |",
            "|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|---:|---:|---:|---:|---|",
        ]
    )
    for row in report.run_rows:
        lines.append(
            "| "
            f"{row.run} | "
            f"{row.spec} | "
            f"{row.candidate_count} | "
            f"{row.market_count} | "
            f"{row.selected_count} | "
            f"{row.fallback_drift_count} | "
            f"{row.fallback_vol_count} | "
            f"{row.avg_total_drift_bps:.4f} | "
            f"{row.avg_annualized_vol:.6f} | "
            f"{row.total_counterfactual_pnl_cents:.4f} | "
            f"{row.brier:.6f} | "
            f"{row.beats_current_calibrated} | "
            f"{row.ev_rank_correlation_sign:.6f} | "
            f"{row.top_ev_bucket_pnl_cents:.4f} | "
            f"{row.market_ev_rank_correlation_sign:.6f} | "
            f"{row.top_market_ev_bucket_avg_pnl_cents:.4f} | "
            f"{row.strict_gate_pass} |"
        )
    lines.extend(["", "## Run Inputs", "", "| run | rows | markets | spot_ticks |", "|---|---:|---:|---:|"])
    for row in report.run_inputs:
        lines.append(f"| {row.name} | {row.row_count} | {row.market_count} | {row.spot_tick_count} |")
    if report.skipped_run_roots:
        lines.extend(["", "## Skipped Runs", ""])
        lines.extend(f"- `{root}`" for root in report.skipped_run_roots)
    return "\n".join(lines) + "\n"


def _seconds_delta(seconds: int):
    from datetime import timedelta

    return timedelta(seconds=seconds)


def _mean(values) -> float:
    seq = [float(value) for value in values]
    return sum(seq) / len(seq) if seq else 0.0


def _clamp01(value: float) -> float:
    return min(1.0, max(0.0, float(value)))


if __name__ == "__main__":
    raise SystemExit(main())
