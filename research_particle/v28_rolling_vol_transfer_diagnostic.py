from __future__ import annotations

import argparse
import json
from collections import defaultdict
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Sequence

from .dynamic_particle_replay import DynamicParticleSpec, RollingVolEstimator
from .replay_runner import ReplayConfig, ReplayInput, evaluate_replay, load_replay_inputs_from_jsonl
from .terminal_projection import brownian_terminal_probability
from .validation import brier_score, log_loss


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_REAL_SHADOW_DIR = ROOT / "logs" / "particle_research" / "real_shadow"
DEFAULT_OUTPUT_JSON = (
    ROOT / "logs" / "particle_research" / "reports" / "v28_rolling_vol_transfer_diagnostic_latest.json"
)
DEFAULT_OUTPUT_MD = (
    ROOT / "logs" / "particle_research" / "reports" / "v28_rolling_vol_transfer_diagnostic_latest.md"
)


@dataclass(frozen=True)
class TransferRunRow:
    root_name: str
    strategy: str
    strategy_family: str
    candidate_count: int
    market_count: int
    selected_count: int
    total_pnl_cents: float
    delta_vs_current_cents: float
    avg_selected_pnl_cents: float
    brier: float
    log_loss: float
    beats_current_brier: bool
    beats_current_log_loss: bool
    notes: str


@dataclass(frozen=True)
class TransferSummaryRow:
    strategy: str
    strategy_family: str
    run_count: int
    candidate_count: int
    market_count: int
    selected_count: int
    total_pnl_cents: float
    delta_vs_current_cents: float
    avg_selected_pnl_cents: float
    weighted_brier: float
    weighted_log_loss: float
    positive_delta_run_count: int
    beats_current_brier_run_count: int
    beats_current_log_loss_run_count: int
    strict_transfer_candidate: bool
    notes: str


@dataclass(frozen=True)
class V28RollingVolTransferReport:
    schema_version: str
    generated_utc: str
    promotion_allowed: bool
    output_json: str
    output_md: str
    root_count: int
    roots: tuple[str, ...]
    best_by_total_delta: str
    best_probability_transfer: str
    summary_rows: tuple[TransferSummaryRow, ...]
    run_rows: tuple[TransferRunRow, ...]
    conclusion: str


def discover_shadow_roots(base_dir: Path = DEFAULT_REAL_SHADOW_DIR) -> tuple[Path, ...]:
    if not base_dir.exists():
        return ()
    roots: list[Path] = []
    for path in sorted(base_dir.iterdir(), key=lambda item: item.name):
        if not path.is_dir():
            continue
        if _candidate_path(path).exists() and _label_path(path).exists():
            roots.append(path)
    return tuple(roots)


def build_v28_rolling_vol_transfer_diagnostic(
    roots: Sequence[Path] | None = None,
    *,
    output_json: Path = DEFAULT_OUTPUT_JSON,
    output_md: Path = DEFAULT_OUTPUT_MD,
) -> V28RollingVolTransferReport:
    selected_roots = tuple(roots) if roots is not None else discover_shadow_roots()
    run_rows: list[TransferRunRow] = []
    for root in selected_roots:
        rows = load_replay_inputs_from_jsonl(_candidate_path(root), _label_path(root))
        run_rows.extend(evaluate_transfer_rows(rows, root_name=root.name))
    summary_rows = _summarize(run_rows)
    best_by_total_delta = max(summary_rows, key=lambda row: row.delta_vs_current_cents).strategy if summary_rows else ""
    probability_rows = [row for row in summary_rows if row.strategy_family == "blend"]
    best_probability_transfer = (
        max(probability_rows, key=lambda row: row.delta_vs_current_cents).strategy if probability_rows else ""
    )
    conclusion = _conclusion(summary_rows)
    return V28RollingVolTransferReport(
        schema_version="v28-rolling-vol-transfer-diagnostic-v1",
        generated_utc=_utc_now(),
        promotion_allowed=False,
        output_json=str(output_json),
        output_md=str(output_md),
        root_count=len(selected_roots),
        roots=tuple(root.name for root in selected_roots),
        best_by_total_delta=best_by_total_delta,
        best_probability_transfer=best_probability_transfer,
        summary_rows=tuple(summary_rows),
        run_rows=tuple(run_rows),
        conclusion=conclusion,
    )


def evaluate_transfer_rows(rows: Sequence[ReplayInput], *, root_name: str = "in_memory") -> tuple[TransferRunRow, ...]:
    if not rows:
        raise ValueError("at least one row is required")
    cfg = ReplayConfig()
    current_rows = [_replace_probability(row, row.current_calibrated_p_yes) for row in rows]
    current_report = evaluate_replay(current_rows, cfg)
    current_brier = current_report.particle.brier
    current_log_loss = current_report.particle.log_loss
    current_pnl = current_report.total_counterfactual_pnl_cents
    market_count = len({row.snapshot.market_ticker for row in rows})
    labels = [1 if row.label.result_yes else 0 for row in rows]

    strategy_rows: list[TransferRunRow] = [
        TransferRunRow(
            root_name=root_name,
            strategy="current_calibrated_v28",
            strategy_family="baseline",
            candidate_count=len(rows),
            market_count=market_count,
            selected_count=current_report.selected_count,
            total_pnl_cents=current_pnl,
            delta_vs_current_cents=0.0,
            avg_selected_pnl_cents=current_report.avg_counterfactual_pnl_cents_per_selected,
            brier=current_brier,
            log_loss=current_log_loss,
            beats_current_brier=False,
            beats_current_log_loss=False,
            notes="baseline control",
        )
    ]

    rv_probability_sets = {
        "rv300": _rolling_vol_probabilities(rows, lookback_seconds=300.0),
        "rv600": _rolling_vol_probabilities(rows, lookback_seconds=600.0),
    }
    for rv_name, rv_probs in rv_probability_sets.items():
        strategy_rows.append(
            _probability_strategy_row(
                rows,
                labels,
                root_name=root_name,
                strategy=rv_name,
                strategy_family="rolling_vol",
                probs=rv_probs,
                current_pnl=current_pnl,
                current_brier=current_brier,
                current_log_loss=current_log_loss,
                notes="rolling-vol replacement; diagnostic only",
            )
        )
        for weight in (0.05, 0.10, 0.20):
            blended = [
                _clamp01((1.0 - weight) * row.current_calibrated_p_yes + weight * rv_p)
                for row, rv_p in zip(rows, rv_probs)
            ]
            strategy_rows.append(
                _probability_strategy_row(
                    rows,
                    labels,
                    root_name=root_name,
                    strategy=f"v28_{int((1.0 - weight) * 100):02d}_{rv_name}_{int(weight * 100):02d}",
                    strategy_family="blend",
                    probs=blended,
                    current_pnl=current_pnl,
                    current_brier=current_brier,
                    current_log_loss=current_log_loss,
                    notes="tiny probability blend into v28/current",
                )
            )
        strategy_rows.append(
            _agreement_veto_row(
                rows,
                root_name=root_name,
                strategy=f"v28_with_{rv_name}_side_agreement_veto",
                rv_probs=rv_probs,
                current_report=current_report,
                current_brier=current_brier,
                current_log_loss=current_log_loss,
                current_pnl=current_pnl,
            )
        )
    return tuple(strategy_rows)


def write_v28_rolling_vol_transfer_diagnostic(report: V28RollingVolTransferReport) -> None:
    output_json = Path(report.output_json)
    output_md = Path(report.output_md)
    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_md.parent.mkdir(parents=True, exist_ok=True)
    output_json.write_text(json.dumps(asdict(report), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    output_md.write_text(_markdown(report), encoding="utf-8")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Test whether rolling-vol particle probabilities can improve v28/current-calibrated decisions."
    )
    parser.add_argument("--root", action="append", type=Path, default=[])
    parser.add_argument("--output-json", type=Path, default=DEFAULT_OUTPUT_JSON)
    parser.add_argument("--output-md", type=Path, default=DEFAULT_OUTPUT_MD)
    parser.add_argument("--write", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    roots = tuple(args.root) if args.root else None
    report = build_v28_rolling_vol_transfer_diagnostic(
        roots,
        output_json=args.output_json,
        output_md=args.output_md,
    )
    if args.write:
        write_v28_rolling_vol_transfer_diagnostic(report)
    print(f"root_count={report.root_count}")
    print(f"best_by_total_delta={report.best_by_total_delta}")
    print(f"best_probability_transfer={report.best_probability_transfer}")
    print(f"promotion_allowed={report.promotion_allowed}")
    print(f"conclusion={report.conclusion}")
    print(f"output_json={report.output_json}")
    return 0


def _probability_strategy_row(
    rows: Sequence[ReplayInput],
    labels: Sequence[int],
    *,
    root_name: str,
    strategy: str,
    strategy_family: str,
    probs: Sequence[float],
    current_pnl: float,
    current_brier: float,
    current_log_loss: float,
    notes: str,
) -> TransferRunRow:
    variant_rows = [_replace_probability(row, prob) for row, prob in zip(rows, probs)]
    report = evaluate_replay(variant_rows, ReplayConfig())
    brier = brier_score(probs, labels)
    ll = log_loss(probs, labels)
    return TransferRunRow(
        root_name=root_name,
        strategy=strategy,
        strategy_family=strategy_family,
        candidate_count=len(rows),
        market_count=len({row.snapshot.market_ticker for row in rows}),
        selected_count=report.selected_count,
        total_pnl_cents=report.total_counterfactual_pnl_cents,
        delta_vs_current_cents=report.total_counterfactual_pnl_cents - current_pnl,
        avg_selected_pnl_cents=report.avg_counterfactual_pnl_cents_per_selected,
        brier=brier,
        log_loss=ll,
        beats_current_brier=brier < current_brier,
        beats_current_log_loss=ll < current_log_loss,
        notes=notes,
    )


def _agreement_veto_row(
    rows: Sequence[ReplayInput],
    *,
    root_name: str,
    strategy: str,
    rv_probs: Sequence[float],
    current_report,
    current_brier: float,
    current_log_loss: float,
    current_pnl: float,
) -> TransferRunRow:
    rv_report = evaluate_replay(
        [_replace_probability(row, rv_prob) for row, rv_prob in zip(rows, rv_probs)],
        ReplayConfig(),
    )
    selected_count = 0
    total_pnl = 0.0
    selected_pnls: list[float] = []
    for current_decision, rv_decision in zip(current_report.decisions, rv_report.decisions):
        if not current_decision.selected:
            continue
        if not rv_decision.selected or current_decision.side != rv_decision.side:
            continue
        selected_count += 1
        total_pnl += current_decision.counterfactual_pnl_cents
        selected_pnls.append(current_decision.counterfactual_pnl_cents)
    return TransferRunRow(
        root_name=root_name,
        strategy=strategy,
        strategy_family="agreement_veto",
        candidate_count=len(rows),
        market_count=len({row.snapshot.market_ticker for row in rows}),
        selected_count=selected_count,
        total_pnl_cents=total_pnl,
        delta_vs_current_cents=total_pnl - current_pnl,
        avg_selected_pnl_cents=(sum(selected_pnls) / selected_count if selected_count else 0.0),
        brier=current_brier,
        log_loss=current_log_loss,
        beats_current_brier=False,
        beats_current_log_loss=False,
        notes="v28/current decision kept only when rolling-vol chooses the same side",
    )


def _rolling_vol_probabilities(rows: Sequence[ReplayInput], *, lookback_seconds: float) -> list[float]:
    spec = DynamicParticleSpec(
        name=f"rolling_vol_{int(lookback_seconds)}s",
        lookback_seconds=lookback_seconds,
        fallback_annualized_vol=0.65,
        min_annualized_vol=0.20,
        max_annualized_vol=2.50,
        min_distinct_observations=3,
    )
    estimator = RollingVolEstimator(spec)
    probs_by_key: dict[tuple[str, str], float] = {}
    for row in sorted(rows, key=lambda item: (item.snapshot.decision_ts_utc, item.snapshot.market_ticker)):
        vol = estimator.observe_and_estimate(row.snapshot.decision_ts_utc, row.snapshot.spot)
        seconds_to_close = max(0.0, (row.label.settlement_ts_utc - row.snapshot.decision_ts_utc).total_seconds())
        probs_by_key[_row_key(row)] = _clamp01(
            brownian_terminal_probability(row.snapshot.spot, row.snapshot.strike, seconds_to_close, vol)
        )
    return [probs_by_key[_row_key(row)] for row in rows]


def _summarize(run_rows: Sequence[TransferRunRow]) -> list[TransferSummaryRow]:
    grouped: dict[str, list[TransferRunRow]] = defaultdict(list)
    for row in run_rows:
        grouped[row.strategy].append(row)
    summary_rows: list[TransferSummaryRow] = []
    for strategy, rows in grouped.items():
        candidate_count = sum(row.candidate_count for row in rows)
        selected_count = sum(row.selected_count for row in rows)
        total_pnl = sum(row.total_pnl_cents for row in rows)
        total_delta = sum(row.delta_vs_current_cents for row in rows)
        weighted_brier = sum(row.brier * row.candidate_count for row in rows) / candidate_count
        weighted_log_loss = sum(row.log_loss * row.candidate_count for row in rows) / candidate_count
        positive_delta = sum(1 for row in rows if row.delta_vs_current_cents > 0.0)
        beats_brier = sum(1 for row in rows if row.beats_current_brier)
        beats_log_loss = sum(1 for row in rows if row.beats_current_log_loss)
        family = rows[0].strategy_family
        strict_transfer = (
            family == "blend"
            and total_delta > 0.0
            and positive_delta >= max(1, int(0.6 * len(rows)))
            and beats_brier >= max(1, int(0.6 * len(rows)))
            and beats_log_loss >= max(1, int(0.6 * len(rows)))
        )
        summary_rows.append(
            TransferSummaryRow(
                strategy=strategy,
                strategy_family=family,
                run_count=len(rows),
                candidate_count=candidate_count,
                market_count=sum(row.market_count for row in rows),
                selected_count=selected_count,
                total_pnl_cents=total_pnl,
                delta_vs_current_cents=total_delta,
                avg_selected_pnl_cents=(total_pnl / selected_count if selected_count else 0.0),
                weighted_brier=weighted_brier,
                weighted_log_loss=weighted_log_loss,
                positive_delta_run_count=positive_delta,
                beats_current_brier_run_count=beats_brier,
                beats_current_log_loss_run_count=beats_log_loss,
                strict_transfer_candidate=strict_transfer,
                notes=_summary_notes(family, total_delta, positive_delta, beats_brier, beats_log_loss, len(rows)),
            )
        )
    return sorted(summary_rows, key=lambda row: (row.strict_transfer_candidate, row.delta_vs_current_cents), reverse=True)


def _summary_notes(
    family: str,
    total_delta: float,
    positive_delta: int,
    beats_brier: int,
    beats_log_loss: int,
    run_count: int,
) -> str:
    if family == "baseline":
        return "v28/current-calibrated control"
    if total_delta <= 0.0:
        return "does not improve total PnL versus v28/current"
    if family == "agreement_veto":
        return "PnL-positive veto if positive, but it reduces coverage and keeps v28 probability score"
    return (
        f"positive total delta; positive PnL delta in {positive_delta}/{run_count}, "
        f"Brier beat in {beats_brier}/{run_count}, log-loss beat in {beats_log_loss}/{run_count}"
    )


def _conclusion(summary_rows: Sequence[TransferSummaryRow]) -> str:
    if not summary_rows:
        return "No eligible roots were found."
    strict = [row for row in summary_rows if row.strict_transfer_candidate]
    if strict:
        names = ", ".join(row.strategy for row in strict)
        return (
            "Research-only transfer clue found: these tiny v28/rolling-vol blends cleared the strict diagnostic "
            f"screen across the available roots: {names}. They still require a predeclared fresh shadow lock."
        )
    best = max(summary_rows, key=lambda row: row.delta_vs_current_cents)
    return (
        "No rolling-vol transfer cleared the strict diagnostic screen versus v28/current. "
        f"Best total delta was {best.strategy} at {best.delta_vs_current_cents:.1f}c, "
        "so keep rolling-vol as a research feature, not a live v28 change."
    )


def _replace_probability(row: ReplayInput, probability: float) -> ReplayInput:
    from dataclasses import replace

    return replace(row, particle_p_yes=_clamp01(probability))


def _row_key(row: ReplayInput) -> tuple[str, str]:
    return (row.snapshot.market_ticker, row.snapshot.decision_ts_utc.isoformat())


def _candidate_path(root: Path) -> Path:
    return root / "candidate_snapshots" / "candidate_snapshots.ndjson"


def _label_path(root: Path) -> Path:
    return root / "pipeline_work" / "label_contexts_full_refresh.ndjson"


def _clamp01(value: float) -> float:
    return max(0.0, min(1.0, float(value)))


def _utc_now() -> str:
    from datetime import datetime, timezone

    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _markdown(report: V28RollingVolTransferReport) -> str:
    lines = [
        "# V28 Rolling-Vol Transfer Diagnostic",
        "",
        f"- generated_utc: {report.generated_utc}",
        f"- promotion_allowed: {report.promotion_allowed}",
        f"- root_count: {report.root_count}",
        f"- best_by_total_delta: {report.best_by_total_delta}",
        f"- best_probability_transfer: {report.best_probability_transfer}",
        f"- conclusion: {report.conclusion}",
        "",
        "## Summary",
        "",
        "| strategy | family | runs | selected | pnl_cents | delta_vs_current | avg_selected_pnl | brier | log_loss | +delta runs | brier beats | logloss beats | strict? |",
        "|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|",
    ]
    for row in report.summary_rows:
        lines.append(
            "| {strategy} | {strategy_family} | {run_count} | {selected_count} | "
            "{total_pnl_cents:.1f} | {delta_vs_current_cents:.1f} | "
            "{avg_selected_pnl_cents:.4f} | {weighted_brier:.6f} | "
            "{weighted_log_loss:.6f} | {positive_delta_run_count} | "
            "{beats_current_brier_run_count} | {beats_current_log_loss_run_count} | "
            "{strict_transfer_candidate} |".format(**asdict(row))
        )
    lines.extend(["", "## Roots", ""])
    for root in report.roots:
        lines.append(f"- {root}")
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    raise SystemExit(main())
