from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass, replace
from pathlib import Path
from typing import Iterable, Literal, Sequence

from .meta_probability_loro import _find_label_path
from .replay_runner import ReplayConfig, ReplayInput, evaluate_replay, load_replay_inputs_from_jsonl
from .validation import brier_score, log_loss


AnchorName = Literal["particle", "brownian", "market", "current_calibrated"]


@dataclass(frozen=True)
class AnchorRunInput:
    name: str
    root: str
    candidate_path: str
    label_path: str
    row_count: int
    market_count: int


@dataclass(frozen=True)
class AnchorMetricRow:
    scope: str
    bucket: str
    anchor: str
    run_count: int
    market_count: int
    candidate_count: int
    selected_count: int
    yes_rate: float
    avg_abs_moneyness_bps: float
    avg_seconds_to_close: float
    avg_spread_cents: float
    brier: float
    log_loss: float
    total_counterfactual_pnl_cents: float
    ev_rank_correlation_sign: float
    top_ev_bucket_pnl_cents: float


@dataclass(frozen=True)
class AnchorWinnerRow:
    scope: str
    bucket: str
    run_count: int
    market_count: int
    candidate_count: int
    best_by_brier: str
    best_by_log_loss: str
    best_by_pnl: str
    brier_gap_second_minus_best: float
    best_brier_value: float
    best_pnl_cents: float


@dataclass(frozen=True)
class AnchorRegimeProfileReport:
    run_inputs: tuple[AnchorRunInput, ...]
    metric_rows: tuple[AnchorMetricRow, ...]
    winner_rows: tuple[AnchorWinnerRow, ...]
    run_best_counts_by_brier: dict[str, int]
    market_best_counts_by_brier: dict[str, int]
    state_bucket_best_counts_by_brier: dict[str, int]
    promotion_safe: bool
    conclusion: str


def build_anchor_regime_profile(
    run_roots: Sequence[Path],
    *,
    replay_config: ReplayConfig | None = None,
) -> AnchorRegimeProfileReport:
    if not run_roots:
        raise ValueError("at least one run root is required")
    cfg = replay_config or ReplayConfig(min_fill_prob=0.5, counterfactual_fill_threshold=0.5)
    loaded_runs = [_load_run(root) for root in run_roots]

    metric_rows: list[AnchorMetricRow] = []
    winner_rows: list[AnchorWinnerRow] = []

    all_rows = [row for _, rows in loaded_runs for row in rows]
    _append_scope(metric_rows, winner_rows, "all", "all_locked_rows", all_rows, cfg)

    for meta, rows in loaded_runs:
        _append_scope(metric_rows, winner_rows, "run", meta.name, rows, cfg)
        by_market: dict[str, list[ReplayInput]] = {}
        for row in rows:
            by_market.setdefault(row.snapshot.market_ticker, []).append(row)
        for market, market_rows in sorted(by_market.items()):
            _append_scope(metric_rows, winner_rows, "market", f"{meta.name}:{market}", market_rows, cfg)

    for bucket_name, bucket_rows in _bucket_rows(all_rows):
        _append_scope(metric_rows, winner_rows, "state_bucket", bucket_name, bucket_rows, cfg)

    run_counts = _winner_counts(winner_rows, scope="run")
    market_counts = _winner_counts(winner_rows, scope="market")
    bucket_counts = _winner_counts(winner_rows, scope="state_bucket")
    dominant = max(run_counts.values(), default=0)
    conclusion = (
        "One probability anchor dominates every locked run by Brier; it is a candidate "
        "for a predeclared fresh OOS hypothesis, not promotion evidence."
        if dominant == len(loaded_runs)
        else "No single timestamp-available anchor dominates all locked runs by Brier; "
        "anchor switching needs a stronger state signal before it is promotable."
    )
    return AnchorRegimeProfileReport(
        run_inputs=tuple(meta for meta, _ in loaded_runs),
        metric_rows=tuple(metric_rows),
        winner_rows=tuple(winner_rows),
        run_best_counts_by_brier=run_counts,
        market_best_counts_by_brier=market_counts,
        state_bucket_best_counts_by_brier=bucket_counts,
        promotion_safe=False,
        conclusion=conclusion,
    )


def write_anchor_regime_profile(
    report: AnchorRegimeProfileReport,
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
        description="Profile which probability anchor wins by run, market, and timestamp-available state bucket."
    )
    parser.add_argument("--run-root", action="append", required=True, type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--stem", default="anchor_regime_profile")
    parser.add_argument("--min-fill-prob", default=0.5, type=float)
    parser.add_argument("--counterfactual-fill-threshold", default=0.5, type=float)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    report = build_anchor_regime_profile(
        args.run_root,
        replay_config=ReplayConfig(
            min_fill_prob=args.min_fill_prob,
            counterfactual_fill_threshold=args.counterfactual_fill_threshold,
        ),
    )
    json_path, md_path = write_anchor_regime_profile(report, args.output_dir, args.stem)
    print(f"run_count={len(report.run_inputs)}")
    print(f"metric_row_count={len(report.metric_rows)}")
    print(f"winner_row_count={len(report.winner_rows)}")
    print(f"run_best_counts_by_brier={json.dumps(report.run_best_counts_by_brier, sort_keys=True)}")
    print(f"market_best_counts_by_brier={json.dumps(report.market_best_counts_by_brier, sort_keys=True)}")
    print(f"state_bucket_best_counts_by_brier={json.dumps(report.state_bucket_best_counts_by_brier, sort_keys=True)}")
    print(f"promotion_safe={report.promotion_safe}")
    print(f"json_report={json_path}")
    print(f"md_report={md_path}")
    return 0


def _append_scope(
    metric_rows: list[AnchorMetricRow],
    winner_rows: list[AnchorWinnerRow],
    scope: str,
    bucket: str,
    rows: Sequence[ReplayInput],
    cfg: ReplayConfig,
) -> None:
    if not rows:
        return
    scoped_metrics = [_metric_row(scope, bucket, anchor, rows, cfg) for anchor in _anchors()]
    metric_rows.extend(scoped_metrics)
    winner_rows.append(_winner_row(scope, bucket, scoped_metrics))


def _metric_row(
    scope: str,
    bucket: str,
    anchor: AnchorName,
    rows: Sequence[ReplayInput],
    cfg: ReplayConfig,
) -> AnchorMetricRow:
    variant_rows = [replace(row, particle_p_yes=_anchor_probability(row, anchor)) for row in rows]
    replay = evaluate_replay(variant_rows, cfg)
    labels = [1 if row.label.result_yes else 0 for row in rows]
    probs = [_anchor_probability(row, anchor) for row in rows]
    return AnchorMetricRow(
        scope=scope,
        bucket=bucket,
        anchor=anchor,
        run_count=len({bucket.split(":", 1)[0]}) if scope == "market" else 1,
        market_count=len({row.snapshot.market_ticker for row in rows}),
        candidate_count=len(rows),
        selected_count=replay.selected_count,
        yes_rate=sum(labels) / len(labels),
        avg_abs_moneyness_bps=_mean(abs(_moneyness_bps(row)) for row in rows),
        avg_seconds_to_close=_mean(_seconds_to_close(row) for row in rows),
        avg_spread_cents=_mean(
            row.snapshot.yes_ask_cents + row.snapshot.no_ask_cents - 100.0
            for row in rows
        ),
        brier=brier_score(probs, labels),
        log_loss=log_loss(probs, labels),
        total_counterfactual_pnl_cents=replay.total_counterfactual_pnl_cents,
        ev_rank_correlation_sign=replay.ev_rank_correlation_sign,
        top_ev_bucket_pnl_cents=replay.top_ev_bucket_pnl_cents,
    )


def _winner_row(scope: str, bucket: str, metrics: Sequence[AnchorMetricRow]) -> AnchorWinnerRow:
    best_brier = min(metrics, key=lambda row: (row.brier, row.log_loss))
    best_log_loss = min(metrics, key=lambda row: (row.log_loss, row.brier))
    best_pnl = max(metrics, key=lambda row: row.total_counterfactual_pnl_cents)
    sorted_brier = sorted(metrics, key=lambda row: (row.brier, row.log_loss))
    gap = (
        sorted_brier[1].brier - sorted_brier[0].brier
        if len(sorted_brier) > 1
        else 0.0
    )
    return AnchorWinnerRow(
        scope=scope,
        bucket=bucket,
        run_count=max(row.run_count for row in metrics),
        market_count=max(row.market_count for row in metrics),
        candidate_count=max(row.candidate_count for row in metrics),
        best_by_brier=best_brier.anchor,
        best_by_log_loss=best_log_loss.anchor,
        best_by_pnl=best_pnl.anchor,
        brier_gap_second_minus_best=gap,
        best_brier_value=best_brier.brier,
        best_pnl_cents=best_pnl.total_counterfactual_pnl_cents,
    )


def _bucket_rows(rows: Sequence[ReplayInput]) -> list[tuple[str, list[ReplayInput]]]:
    buckets: dict[str, list[ReplayInput]] = {}
    for row in rows:
        for name in (
            _time_bucket(row),
            _moneyness_bucket(row),
            _spread_bucket(row),
            _market_brownian_disagreement_bucket(row),
        ):
            buckets.setdefault(name, []).append(row)
    return sorted(buckets.items())


def _time_bucket(row: ReplayInput) -> str:
    seconds = _seconds_to_close(row)
    if seconds <= 60:
        return "ttc_000_060s"
    if seconds <= 180:
        return "ttc_061_180s"
    if seconds <= 300:
        return "ttc_181_300s"
    if seconds <= 600:
        return "ttc_301_600s"
    return "ttc_gt600s"


def _moneyness_bucket(row: ReplayInput) -> str:
    abs_bps = abs(_moneyness_bps(row))
    if abs_bps <= 10:
        return "abs_mny_000_010bps"
    if abs_bps <= 25:
        return "abs_mny_011_025bps"
    if abs_bps <= 50:
        return "abs_mny_026_050bps"
    if abs_bps <= 100:
        return "abs_mny_051_100bps"
    return "abs_mny_gt100bps"


def _spread_bucket(row: ReplayInput) -> str:
    spread = row.snapshot.yes_ask_cents + row.snapshot.no_ask_cents - 100.0
    if spread <= 1:
        return "spread_000_001c"
    if spread <= 3:
        return "spread_002_003c"
    if spread <= 6:
        return "spread_004_006c"
    return "spread_gt006c"


def _market_brownian_disagreement_bucket(row: ReplayInput) -> str:
    diff = row.market_p_yes - row.brownian_p_yes
    if diff >= 0.10:
        return "market_minus_brownian_ge10pp"
    if diff <= -0.10:
        return "market_minus_brownian_le_neg10pp"
    return "market_minus_brownian_mid"


def _anchor_probability(row: ReplayInput, anchor: AnchorName) -> float:
    if anchor == "particle":
        return _clamp01(row.particle_p_yes)
    if anchor == "brownian":
        return _clamp01(row.brownian_p_yes)
    if anchor == "market":
        return _clamp01(row.market_p_yes)
    if anchor == "current_calibrated":
        return _clamp01(row.current_calibrated_p_yes)
    raise ValueError(f"unknown anchor: {anchor}")


def _anchors() -> tuple[AnchorName, ...]:
    return ("particle", "brownian", "market", "current_calibrated")


def _winner_counts(rows: Sequence[AnchorWinnerRow], *, scope: str) -> dict[str, int]:
    counts = {anchor: 0 for anchor in _anchors()}
    for row in rows:
        if row.scope == scope:
            counts[row.best_by_brier] += 1
    return counts


def _load_run(root: Path) -> tuple[AnchorRunInput, list[ReplayInput]]:
    candidate_path = root / "candidate_snapshots" / "candidate_snapshots.ndjson"
    label_path = _find_label_path(root)
    rows = load_replay_inputs_from_jsonl(candidate_path, label_path)
    meta = AnchorRunInput(
        name=root.name,
        root=str(root),
        candidate_path=str(candidate_path),
        label_path=str(label_path),
        row_count=len(rows),
        market_count=len({row.snapshot.market_ticker for row in rows}),
    )
    return meta, rows


def _moneyness_bps(row: ReplayInput) -> float:
    return ((row.snapshot.spot - row.snapshot.strike) / row.snapshot.strike) * 10_000.0


def _seconds_to_close(row: ReplayInput) -> float:
    return (row.label.settlement_ts_utc - row.snapshot.decision_ts_utc).total_seconds()


def _mean(values: Iterable[float]) -> float:
    materialized = list(values)
    return sum(materialized) / len(materialized) if materialized else 0.0


def _clamp01(value: float) -> float:
    return max(0.0, min(1.0, float(value)))


def _markdown(report: AnchorRegimeProfileReport) -> str:
    lines = [
        "# Anchor Regime Profile",
        "",
        f"- run_count: {len(report.run_inputs)}",
        f"- metric_row_count: {len(report.metric_rows)}",
        f"- winner_row_count: {len(report.winner_rows)}",
        f"- promotion_safe: {report.promotion_safe}",
        f"- conclusion: {report.conclusion}",
        f"- run_best_counts_by_brier: `{json.dumps(report.run_best_counts_by_brier, sort_keys=True)}`",
        f"- market_best_counts_by_brier: `{json.dumps(report.market_best_counts_by_brier, sort_keys=True)}`",
        f"- state_bucket_best_counts_by_brier: `{json.dumps(report.state_bucket_best_counts_by_brier, sort_keys=True)}`",
        "",
        "## Winner Rows",
        "",
        "| scope | bucket | markets | candidates | best_brier | best_log_loss | best_pnl | brier_gap | best_brier_value | best_pnl_cents |",
        "|---|---|---:|---:|---|---|---|---:|---:|---:|",
    ]
    for row in sorted(report.winner_rows, key=lambda item: (item.scope, item.bucket)):
        lines.append(
            "| {scope} | {bucket} | {market_count} | {candidate_count} | "
            "{best_by_brier} | {best_by_log_loss} | {best_by_pnl} | "
            "{brier_gap_second_minus_best:.6f} | {best_brier_value:.6f} | "
            "{best_pnl_cents:.4f} |".format(**asdict(row))
        )
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    raise SystemExit(main())
