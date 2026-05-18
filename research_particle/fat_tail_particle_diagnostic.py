from __future__ import annotations

import argparse
import json
import math
from dataclasses import asdict, dataclass, replace
from pathlib import Path
from typing import Sequence

from .meta_probability_loro import _find_label_path
from .replay_runner import ReplayConfig, ReplayInput, evaluate_replay, load_replay_inputs_from_jsonl
from .terminal_projection import brownian_terminal_probability


SECONDS_PER_YEAR = 365.0 * 24.0 * 60.0 * 60.0


@dataclass(frozen=True)
class FatTailSpec:
    name: str
    annualized_vol: float
    jump_weight: float = 0.0
    jump_vol_scale: float = 1.0
    jump_mean_bps: float = 0.0


@dataclass(frozen=True)
class FatTailRunInput:
    name: str
    root: str
    candidate_path: str
    label_path: str
    row_count: int
    market_count: int


@dataclass(frozen=True)
class FatTailRunRow:
    run: str
    spec: str
    candidate_count: int
    market_count: int
    selected_count: int
    total_counterfactual_pnl_cents: float
    brier: float
    log_loss: float
    beats_brownian: bool
    beats_market: bool
    beats_current_calibrated: bool
    ev_rank_correlation_sign: float
    top_ev_bucket_pnl_cents: float
    strict_gate_pass: bool


@dataclass(frozen=True)
class FatTailSummaryRow:
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
    strict_gate_count: int
    strict_all_runs: bool


@dataclass(frozen=True)
class FatTailParticleDiagnosticReport:
    run_inputs: tuple[FatTailRunInput, ...]
    spec_count: int
    run_rows: tuple[FatTailRunRow, ...]
    summary_rows: tuple[FatTailSummaryRow, ...]
    best_by_brier: FatTailSummaryRow | None
    best_by_pnl: FatTailSummaryRow | None
    promotion_safe: bool
    conclusion: str


def terminal_jump_mixture_probability(
    *,
    spot: float,
    strike: float,
    seconds_to_close: float,
    annualized_vol: float,
    jump_weight: float,
    jump_vol_scale: float,
    jump_mean_bps: float,
) -> float:
    if not 0.0 <= jump_weight <= 1.0:
        raise ValueError("jump_weight must be in [0, 1]")
    if jump_vol_scale <= 0.0:
        raise ValueError("jump_vol_scale must be positive")
    base = brownian_terminal_probability(
        spot=spot,
        strike=strike,
        seconds_to_close=seconds_to_close,
        annualized_vol=annualized_vol,
    )
    if jump_weight == 0.0:
        return base
    jump = _normal_terminal_probability_with_jump_mean(
        spot=spot,
        strike=strike,
        seconds_to_close=seconds_to_close,
        annualized_vol=annualized_vol * jump_vol_scale,
        jump_mean_bps=jump_mean_bps,
    )
    return _clamp01((1.0 - jump_weight) * base + jump_weight * jump)


def build_fat_tail_particle_diagnostic(
    run_roots: Sequence[Path],
    *,
    replay_config: ReplayConfig | None = None,
) -> FatTailParticleDiagnosticReport:
    if not run_roots:
        raise ValueError("at least one run root is required")
    cfg = replay_config or ReplayConfig(min_fill_prob=0.5, counterfactual_fill_threshold=0.5)
    loaded_runs = [_load_run(root) for root in run_roots]
    run_rows: list[FatTailRunRow] = []
    for run_meta, rows in loaded_runs:
        for spec in _spec_registry():
            variant_rows = [replace(row, particle_p_yes=_probability_for(row, spec)) for row in rows]
            replay = evaluate_replay(variant_rows, cfg)
            strict = (
                replay.total_counterfactual_pnl_cents > 0.0
                and replay.particle_beats_brownian
                and replay.particle_beats_market
                and replay.particle_beats_current_calibrated
                and replay.ev_rank_correlation_sign > 0.0
                and replay.top_ev_bucket_pnl_cents > 0.0
            )
            run_rows.append(
                FatTailRunRow(
                    run=run_meta.name,
                    spec=spec.name,
                    candidate_count=replay.candidate_count,
                    market_count=run_meta.market_count,
                    selected_count=replay.selected_count,
                    total_counterfactual_pnl_cents=replay.total_counterfactual_pnl_cents,
                    brier=replay.particle.brier,
                    log_loss=replay.particle.log_loss,
                    beats_brownian=replay.particle_beats_brownian,
                    beats_market=replay.particle_beats_market,
                    beats_current_calibrated=replay.particle_beats_current_calibrated,
                    ev_rank_correlation_sign=replay.ev_rank_correlation_sign,
                    top_ev_bucket_pnl_cents=replay.top_ev_bucket_pnl_cents,
                    strict_gate_pass=strict,
                )
            )
    summaries = tuple(_summarize(run_rows))
    best_by_brier = min(summaries, key=lambda row: (row.mean_brier, row.mean_log_loss), default=None)
    best_by_pnl = max(summaries, key=lambda row: row.total_counterfactual_pnl_cents, default=None)
    promotion_safe = False
    strict_candidates = [row for row in summaries if row.strict_all_runs]
    conclusion = (
        "At least one fixed fat-tail terminal distribution cleared every locked run, "
        "but this diagnostic was not predeclared before capture and remains research-only."
        if strict_candidates
        else "No fixed fat-tail/jump-mixture terminal distribution clears strict locked-run gates."
    )
    return FatTailParticleDiagnosticReport(
        run_inputs=tuple(meta for meta, _ in loaded_runs),
        spec_count=len(_spec_registry()),
        run_rows=tuple(run_rows),
        summary_rows=summaries,
        best_by_brier=best_by_brier,
        best_by_pnl=best_by_pnl,
        promotion_safe=promotion_safe,
        conclusion=conclusion,
    )


def write_fat_tail_particle_diagnostic(
    report: FatTailParticleDiagnosticReport,
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
        description="Evaluate fixed fat-tail/jump-mixture terminal probability variants on locked run roots."
    )
    parser.add_argument("--run-root", action="append", required=True, type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--stem", default="fat_tail_particle_diagnostic")
    parser.add_argument("--min-fill-prob", default=0.5, type=float)
    parser.add_argument("--counterfactual-fill-threshold", default=0.5, type=float)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    report = build_fat_tail_particle_diagnostic(
        args.run_root,
        replay_config=ReplayConfig(
            min_fill_prob=args.min_fill_prob,
            counterfactual_fill_threshold=args.counterfactual_fill_threshold,
        ),
    )
    json_path, md_path = write_fat_tail_particle_diagnostic(report, args.output_dir, args.stem)
    print(f"run_count={len(report.run_inputs)}")
    print(f"spec_count={report.spec_count}")
    print(f"summary_row_count={len(report.summary_rows)}")
    print(f"promotion_safe={report.promotion_safe}")
    if report.best_by_brier:
        print(f"best_by_brier={report.best_by_brier.spec}")
        print(f"best_by_brier_brier={report.best_by_brier.mean_brier:.6f}")
    if report.best_by_pnl:
        print(f"best_by_pnl={report.best_by_pnl.spec}")
        print(f"best_by_pnl_total_counterfactual_pnl_cents={report.best_by_pnl.total_counterfactual_pnl_cents:.4f}")
    print(f"json_report={json_path}")
    print(f"md_report={md_path}")
    return 0


def _spec_registry() -> tuple[FatTailSpec, ...]:
    return (
        FatTailSpec("gaussian_vol45", annualized_vol=0.45),
        FatTailSpec("gaussian_vol65", annualized_vol=0.65),
        FatTailSpec("gaussian_vol85", annualized_vol=0.85),
        FatTailSpec("gaussian_vol110", annualized_vol=1.10),
        FatTailSpec("tail05_scale3_vol65", annualized_vol=0.65, jump_weight=0.05, jump_vol_scale=3.0),
        FatTailSpec("tail10_scale3_vol65", annualized_vol=0.65, jump_weight=0.10, jump_vol_scale=3.0),
        FatTailSpec("tail20_scale3_vol65", annualized_vol=0.65, jump_weight=0.20, jump_vol_scale=3.0),
        FatTailSpec("tail10_scale5_vol65", annualized_vol=0.65, jump_weight=0.10, jump_vol_scale=5.0),
        FatTailSpec("tail20_scale5_vol65", annualized_vol=0.65, jump_weight=0.20, jump_vol_scale=5.0),
        FatTailSpec(
            "tail10_scale3_up10bps_vol65",
            annualized_vol=0.65,
            jump_weight=0.10,
            jump_vol_scale=3.0,
            jump_mean_bps=10.0,
        ),
        FatTailSpec(
            "tail10_scale3_down10bps_vol65",
            annualized_vol=0.65,
            jump_weight=0.10,
            jump_vol_scale=3.0,
            jump_mean_bps=-10.0,
        ),
        FatTailSpec(
            "tail20_scale4_up5bps_vol85",
            annualized_vol=0.85,
            jump_weight=0.20,
            jump_vol_scale=4.0,
            jump_mean_bps=5.0,
        ),
        FatTailSpec(
            "tail20_scale4_down5bps_vol85",
            annualized_vol=0.85,
            jump_weight=0.20,
            jump_vol_scale=4.0,
            jump_mean_bps=-5.0,
        ),
    )


def _load_run(root: Path) -> tuple[FatTailRunInput, list[ReplayInput]]:
    candidate_path = root / "candidate_snapshots" / "candidate_snapshots.ndjson"
    label_path = _find_label_path(root)
    rows = load_replay_inputs_from_jsonl(candidate_path, label_path)
    return (
        FatTailRunInput(
            name=root.name,
            root=str(root),
            candidate_path=str(candidate_path),
            label_path=str(label_path),
            row_count=len(rows),
            market_count=len({row.snapshot.market_ticker for row in rows}),
        ),
        rows,
    )


def _probability_for(row: ReplayInput, spec: FatTailSpec) -> float:
    seconds_to_close = max(
        0.0,
        (row.label.settlement_ts_utc - row.snapshot.decision_ts_utc).total_seconds(),
    )
    return terminal_jump_mixture_probability(
        spot=row.snapshot.spot,
        strike=row.snapshot.strike,
        seconds_to_close=seconds_to_close,
        annualized_vol=spec.annualized_vol,
        jump_weight=spec.jump_weight,
        jump_vol_scale=spec.jump_vol_scale,
        jump_mean_bps=spec.jump_mean_bps,
    )


def _normal_terminal_probability_with_jump_mean(
    *,
    spot: float,
    strike: float,
    seconds_to_close: float,
    annualized_vol: float,
    jump_mean_bps: float,
) -> float:
    if seconds_to_close <= 0.0:
        return 1.0 if spot > strike else 0.0
    if spot <= 0.0 or strike <= 0.0:
        raise ValueError("spot and strike must be positive")
    sigma_per_sqrt_second = annualized_vol / math.sqrt(SECONDS_PER_YEAR)
    stdev = sigma_per_sqrt_second * math.sqrt(seconds_to_close)
    mean = math.log(spot / strike) + jump_mean_bps / 10_000.0
    if stdev <= 0.0:
        return 1.0 if mean > 0.0 else 0.0
    return 0.5 * (1.0 + math.erf((mean / stdev) / math.sqrt(2.0)))


def _summarize(rows: Sequence[FatTailRunRow]) -> list[FatTailSummaryRow]:
    grouped: dict[str, list[FatTailRunRow]] = {}
    for row in rows:
        grouped.setdefault(row.spec, []).append(row)
    summaries: list[FatTailSummaryRow] = []
    for spec in sorted(grouped):
        spec_rows = grouped[spec]
        strict_count = sum(1 for row in spec_rows if row.strict_gate_pass)
        summaries.append(
            FatTailSummaryRow(
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


def _mean(values) -> float:
    seq = [float(value) for value in values]
    if not seq:
        return 0.0
    return sum(seq) / len(seq)


def _clamp01(value: float) -> float:
    return max(0.0, min(1.0, float(value)))


def _markdown(report: FatTailParticleDiagnosticReport) -> str:
    lines = [
        "# Fat-Tail Particle Diagnostic",
        "",
        f"- run_count: {len(report.run_inputs)}",
        f"- spec_count: {report.spec_count}",
        f"- promotion_safe: {report.promotion_safe}",
        f"- conclusion: {report.conclusion}",
        f"- best_by_brier: {report.best_by_brier.spec if report.best_by_brier else 'none'}",
        f"- best_by_pnl: {report.best_by_pnl.spec if report.best_by_pnl else 'none'}",
        "",
        "## Summary",
        "",
        "| spec | runs | total_pnl_cents | mean_brier | mean_log_loss | positive_pnl | beats_brownian | beats_market | beats_current | positive_ev_rank | positive_top_bucket | strict_gates | strict_all |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|",
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
            f"{row.strict_gate_count}/{row.run_count} | "
            f"{row.strict_all_runs} |"
        )
    lines.extend(
        [
            "",
            "## Runs",
            "",
            "| run | spec | candidates | markets | selected | pnl_cents | brier | log_loss | beats_brownian | beats_market | beats_current | ev_rank | top_bucket_pnl | strict |",
            "|---|---|---:|---:|---:|---:|---:|---:|---|---|---|---:|---:|---|",
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
            f"{row.total_counterfactual_pnl_cents:.4f} | "
            f"{row.brier:.6f} | "
            f"{row.log_loss:.6f} | "
            f"{row.beats_brownian} | "
            f"{row.beats_market} | "
            f"{row.beats_current_calibrated} | "
            f"{row.ev_rank_correlation_sign:.6f} | "
            f"{row.top_ev_bucket_pnl_cents:.4f} | "
            f"{row.strict_gate_pass} |"
        )
    lines.extend(
        [
            "",
            "## Run Inputs",
            "",
            "| run | rows | markets | candidate_path | label_path |",
            "|---|---:|---:|---|---|",
        ]
    )
    for row in report.run_inputs:
        lines.append(
            "| "
            f"{row.name} | "
            f"{row.row_count} | "
            f"{row.market_count} | "
            f"`{row.candidate_path}` | "
            f"`{row.label_path}` |"
        )
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    raise SystemExit(main())
