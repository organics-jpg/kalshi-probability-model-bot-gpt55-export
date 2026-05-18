from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass, replace
from pathlib import Path
from typing import Callable, Mapping, Sequence

from .meta_probability_loro import _find_label_path
from .replay_runner import ReplayConfig, ReplayInput, ReplayReport, evaluate_replay, load_replay_inputs_from_jsonl
from .spot_context_merge import SpotTickRow, load_spot_ticks
from .spot_realized_vol_terminal_oos import HypothesisId, materialize_spot_realized_vol_terminal_rows
from .validation import brier_score, log_loss, pairwise_rank_correlation_sign, top_bucket_mean_pnl


BASE_ANCHORS = ("brownian", "market", "current_calibrated", "particle")
RV_ANCHOR = "rv_terminal"
AnchorName = str
BucketFn = Callable[["_AnchorRow"], str]


@dataclass(frozen=True)
class SpotRVAnchorRunInput:
    name: str
    root: str
    candidate_path: str
    label_path: str
    spot_tick_path: str
    row_count: int
    market_count: int
    spot_tick_count: int
    rv_fallback_row_count: int


@dataclass(frozen=True)
class SpotRVAnchorSwitchSpec:
    name: str
    bucket_fn: BucketFn


@dataclass(frozen=True)
class TrainedSpotRVAnchorSwitch:
    spec: str
    train_run_count: int
    train_cluster_count: int
    min_bucket_clusters: int
    global_anchor: str
    bucket_anchors: dict[str, str]


@dataclass(frozen=True)
class SpotRVAnchorSwitchHoldoutRow:
    holdout_run: str
    spec: str
    train_run_count: int
    train_cluster_count: int
    min_bucket_clusters: int
    global_anchor: str
    bucket_count: int
    holdout_candidate_count: int
    holdout_market_count: int
    selected_count: int
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
class SpotRVAnchorSwitchSummaryRow:
    spec: str
    holdout_count: int
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
    strict_all_holdouts: bool


@dataclass(frozen=True)
class SpotRVAnchorSwitchLOROReport:
    run_inputs: tuple[SpotRVAnchorRunInput, ...]
    skipped_run_roots: tuple[str, ...]
    anchors: tuple[str, ...]
    hypothesis_id: HypothesisId
    specs: tuple[str, ...]
    min_bucket_clusters: int
    holdout_rows: tuple[SpotRVAnchorSwitchHoldoutRow, ...]
    summary_rows: tuple[SpotRVAnchorSwitchSummaryRow, ...]
    candidate_ready_for_predeclared_shadow: bool
    promotion_safe: bool
    conclusion: str


@dataclass(frozen=True)
class _AnchorRow:
    row: ReplayInput
    rv_terminal_p_yes: float


def build_spot_rv_anchor_switch_loro_report(
    run_roots: Sequence[Path],
    *,
    hypothesis_id: HypothesisId = "rv233_blend50_fixed65_terminal_v1",
    min_bucket_clusters: int = 3,
    replay_config: ReplayConfig | None = None,
) -> SpotRVAnchorSwitchLOROReport:
    if len(run_roots) < 2:
        raise ValueError("at least two run roots are required")
    if min_bucket_clusters < 1:
        raise ValueError("min_bucket_clusters must be positive")
    cfg = replay_config or ReplayConfig(min_fill_prob=0.5, counterfactual_fill_threshold=0.5)
    loaded_runs: list[tuple[SpotRVAnchorRunInput, tuple[_AnchorRow, ...]]] = []
    skipped: list[str] = []
    for root in run_roots:
        loaded = _load_eligible_run(root, hypothesis_id=hypothesis_id)
        if loaded is None:
            skipped.append(str(root))
        else:
            loaded_runs.append(loaded)
    if len(loaded_runs) < 2:
        raise ValueError("at least two run roots with candidate snapshots and independent spot ticks are required")
    specs = _specs()
    holdout_rows: list[SpotRVAnchorSwitchHoldoutRow] = []
    for holdout_meta, holdout_rows_raw in loaded_runs:
        train_rows = [
            item
            for train_meta, rows in loaded_runs
            if train_meta.name != holdout_meta.name
            for item in rows
        ]
        for spec in specs:
            model = _train_anchor_switch(
                spec,
                train_rows,
                train_run_count=len(loaded_runs) - 1,
                min_bucket_clusters=min_bucket_clusters,
            )
            switched_rows = _apply_anchor_switch(model, spec, holdout_rows_raw)
            replay = evaluate_replay(switched_rows, cfg)
            market_ev_rank, top_market_bucket = _market_ev_metrics(replay)
            strict = _strict_gate(replay)
            holdout_rows.append(
                SpotRVAnchorSwitchHoldoutRow(
                    holdout_run=holdout_meta.name,
                    spec=spec.name,
                    train_run_count=model.train_run_count,
                    train_cluster_count=model.train_cluster_count,
                    min_bucket_clusters=model.min_bucket_clusters,
                    global_anchor=model.global_anchor,
                    bucket_count=len(model.bucket_anchors),
                    holdout_candidate_count=replay.candidate_count,
                    holdout_market_count=holdout_meta.market_count,
                    selected_count=replay.selected_count,
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
                    strict_gate_pass=strict,
                )
            )
    summaries = tuple(_summarize(holdout_rows))
    candidate_ready = any(row.strict_all_holdouts for row in summaries)
    conclusion = (
        "At least one realized-vol-aware anchor switch cleared every eligible locked holdout. "
        "Because this switch was selected after capture, treat it only as a candidate for a fresh "
        "predeclared live-shadow run."
        if candidate_ready
        else "No realized-vol-aware anchor switch cleared strict eligible locked holdout gates."
    )
    return SpotRVAnchorSwitchLOROReport(
        run_inputs=tuple(meta for meta, _ in loaded_runs),
        skipped_run_roots=tuple(skipped),
        anchors=tuple(BASE_ANCHORS + (RV_ANCHOR,)),
        hypothesis_id=hypothesis_id,
        specs=tuple(spec.name for spec in specs),
        min_bucket_clusters=min_bucket_clusters,
        holdout_rows=tuple(holdout_rows),
        summary_rows=summaries,
        candidate_ready_for_predeclared_shadow=candidate_ready,
        promotion_safe=False,
        conclusion=conclusion,
    )


def write_spot_rv_anchor_switch_loro_report(
    report: SpotRVAnchorSwitchLOROReport,
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
        description=(
            "Leave-one-run-out anchor switching diagnostic that includes a timestamp-available "
            "independent-spot realized-vol terminal anchor."
        )
    )
    parser.add_argument("--run-root", action="append", required=True, type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--stem", default="spot_rv_anchor_switch_loro")
    parser.add_argument("--hypothesis-id", default="rv233_blend50_fixed65_terminal_v1")
    parser.add_argument("--min-bucket-clusters", default=3, type=int)
    parser.add_argument("--min-fill-prob", default=0.5, type=float)
    parser.add_argument("--counterfactual-fill-threshold", default=0.5, type=float)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    report = build_spot_rv_anchor_switch_loro_report(
        args.run_root,
        hypothesis_id=args.hypothesis_id,
        min_bucket_clusters=args.min_bucket_clusters,
        replay_config=ReplayConfig(
            min_fill_prob=args.min_fill_prob,
            counterfactual_fill_threshold=args.counterfactual_fill_threshold,
        ),
    )
    json_path, md_path = write_spot_rv_anchor_switch_loro_report(report, args.output_dir, args.stem)
    print(f"eligible_run_count={len(report.run_inputs)}")
    print(f"skipped_run_count={len(report.skipped_run_roots)}")
    print(f"anchor_count={len(report.anchors)}")
    print(f"spec_count={len(report.specs)}")
    print(f"holdout_row_count={len(report.holdout_rows)}")
    print(f"summary_row_count={len(report.summary_rows)}")
    print(f"candidate_ready_for_predeclared_shadow={report.candidate_ready_for_predeclared_shadow}")
    print(f"promotion_safe={report.promotion_safe}")
    print(f"json_report={json_path}")
    print(f"md_report={md_path}")
    return 0


def _load_eligible_run(
    root: Path,
    *,
    hypothesis_id: HypothesisId,
) -> tuple[SpotRVAnchorRunInput, tuple[_AnchorRow, ...]] | None:
    candidate_path = root / "candidate_snapshots" / "candidate_snapshots.ndjson"
    spot_path = root / "independent_spot_ticks.ndjson"
    if not candidate_path.exists() or not spot_path.exists():
        return None
    label_path = _find_label_path(root)
    rows = sorted(
        load_replay_inputs_from_jsonl(candidate_path, label_path),
        key=lambda item: (item.snapshot.decision_ts_utc, item.snapshot.market_ticker),
    )
    ticks = load_spot_ticks(spot_path)
    if not rows or not ticks:
        return None
    rv_rows, _, fallback_count = materialize_spot_realized_vol_terminal_rows(
        rows,
        ticks,
        hypothesis_id=hypothesis_id,
    )
    anchor_rows: list[_AnchorRow] = []
    for row, rv_row in zip(rows, rv_rows, strict=True):
        if (
            row.snapshot.market_ticker != rv_row.snapshot.market_ticker
            or row.snapshot.decision_ts_utc != rv_row.snapshot.decision_ts_utc
        ):
            raise ValueError(f"realized-vol rows are not aligned for {root}")
        anchor_rows.append(_AnchorRow(row=row, rv_terminal_p_yes=rv_row.particle_p_yes))
    meta = SpotRVAnchorRunInput(
        name=root.name,
        root=str(root),
        candidate_path=str(candidate_path),
        label_path=str(label_path),
        spot_tick_path=str(spot_path),
        row_count=len(rows),
        market_count=len({row.snapshot.market_ticker for row in rows}),
        spot_tick_count=len(ticks),
        rv_fallback_row_count=fallback_count,
    )
    return meta, tuple(anchor_rows)


def _train_anchor_switch(
    spec: SpotRVAnchorSwitchSpec,
    rows: Sequence[_AnchorRow],
    *,
    train_run_count: int,
    min_bucket_clusters: int,
) -> TrainedSpotRVAnchorSwitch:
    clusters = _cluster_samples(spec, rows)
    if not clusters:
        raise ValueError("no training clusters")
    global_anchor = _best_anchor(clusters)
    by_bucket: dict[str, list[dict[str, float | int | str]]] = {}
    for cluster in clusters:
        by_bucket.setdefault(str(cluster["bucket"]), []).append(cluster)
    bucket_anchors: dict[str, str] = {}
    for bucket, bucket_clusters in by_bucket.items():
        if len(bucket_clusters) >= min_bucket_clusters:
            bucket_anchors[bucket] = _best_anchor(bucket_clusters)
    return TrainedSpotRVAnchorSwitch(
        spec=spec.name,
        train_run_count=train_run_count,
        train_cluster_count=len(clusters),
        min_bucket_clusters=min_bucket_clusters,
        global_anchor=global_anchor,
        bucket_anchors=bucket_anchors,
    )


def _cluster_samples(
    spec: SpotRVAnchorSwitchSpec,
    rows: Sequence[_AnchorRow],
) -> list[dict[str, float | int | str]]:
    grouped: dict[tuple[str, str], list[_AnchorRow]] = {}
    for item in rows:
        grouped.setdefault((item.row.snapshot.market_ticker, spec.bucket_fn(item)), []).append(item)
    samples: list[dict[str, float | int | str]] = []
    for (_, bucket), bucket_rows in grouped.items():
        label = 1 if bucket_rows[0].row.label.result_yes else 0
        sample: dict[str, float | int | str] = {"bucket": bucket, "label": label}
        for anchor in BASE_ANCHORS + (RV_ANCHOR,):
            sample[anchor] = sum(_anchor_prob(item, anchor) for item in bucket_rows) / len(bucket_rows)
        samples.append(sample)
    return samples


def _best_anchor(samples: Sequence[Mapping[str, float | int | str]]) -> str:
    labels = [int(sample["label"]) for sample in samples]
    return min(
        BASE_ANCHORS + (RV_ANCHOR,),
        key=lambda anchor: (
            brier_score([float(sample[anchor]) for sample in samples], labels),
            log_loss([float(sample[anchor]) for sample in samples], labels),
        ),
    )


def _apply_anchor_switch(
    model: TrainedSpotRVAnchorSwitch,
    spec: SpotRVAnchorSwitchSpec,
    rows: Sequence[_AnchorRow],
) -> list[ReplayInput]:
    switched: list[ReplayInput] = []
    for item in rows:
        bucket = spec.bucket_fn(item)
        anchor = model.bucket_anchors.get(bucket, model.global_anchor)
        switched.append(replace(item.row, particle_p_yes=_anchor_prob(item, anchor)))
    return switched


def _anchor_prob(item: _AnchorRow, anchor: AnchorName) -> float:
    row = item.row
    if anchor == "brownian":
        return row.brownian_p_yes
    if anchor == "market":
        return row.market_p_yes
    if anchor == "current_calibrated":
        return row.current_calibrated_p_yes
    if anchor == "particle":
        return row.particle_p_yes
    if anchor == RV_ANCHOR:
        return item.rv_terminal_p_yes
    raise ValueError(f"unknown anchor: {anchor}")


def _strict_gate(report: ReplayReport) -> bool:
    return (
        report.total_counterfactual_pnl_cents > 0.0
        and report.particle_beats_brownian
        and report.particle_beats_market
        and report.particle_beats_current_calibrated
        and report.ev_rank_correlation_sign > 0.0
        and report.top_ev_bucket_pnl_cents > 0.0
    )


def _summarize(rows: Sequence[SpotRVAnchorSwitchHoldoutRow]) -> list[SpotRVAnchorSwitchSummaryRow]:
    grouped: dict[str, list[SpotRVAnchorSwitchHoldoutRow]] = {}
    for row in rows:
        grouped.setdefault(row.spec, []).append(row)
    summaries: list[SpotRVAnchorSwitchSummaryRow] = []
    for spec in sorted(grouped):
        spec_rows = grouped[spec]
        strict_count = sum(1 for row in spec_rows if row.strict_gate_pass)
        summaries.append(
            SpotRVAnchorSwitchSummaryRow(
                spec=spec,
                holdout_count=len(spec_rows),
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
                strict_all_holdouts=(strict_count == len(spec_rows) and bool(spec_rows)),
            )
        )
    return sorted(
        summaries,
        key=lambda row: (
            row.strict_all_holdouts,
            row.strict_gate_count,
            row.beats_current_count,
            row.total_counterfactual_pnl_cents,
        ),
        reverse=True,
    )


def _specs() -> tuple[SpotRVAnchorSwitchSpec, ...]:
    return (
        SpotRVAnchorSwitchSpec("global", lambda item: "all"),
        SpotRVAnchorSwitchSpec("time", lambda item: _time_bucket(item.row)),
        SpotRVAnchorSwitchSpec("moneyness", lambda item: _moneyness_bucket(item.row)),
        SpotRVAnchorSwitchSpec(
            "time_moneyness",
            lambda item: f"{_time_bucket(item.row)}|{_moneyness_bucket(item.row)}",
        ),
        SpotRVAnchorSwitchSpec(
            "time_rv_disagreement",
            lambda item: f"{_time_bucket(item.row)}|{_rv_disagreement_bucket(item)}",
        ),
        SpotRVAnchorSwitchSpec(
            "time_moneyness_rv_disagreement",
            lambda item: f"{_time_bucket(item.row)}|{_moneyness_bucket(item.row)}|{_rv_disagreement_bucket(item)}",
        ),
    )


def _time_bucket(row: ReplayInput) -> str:
    seconds = max(0.0, (row.label.settlement_ts_utc - row.snapshot.decision_ts_utc).total_seconds())
    if seconds <= 180.0:
        return "t_le_180"
    if seconds <= 300.0:
        return "t_181_300"
    if seconds <= 600.0:
        return "t_301_600"
    return "t_gt_600"


def _moneyness_bucket(row: ReplayInput) -> str:
    bps = abs((row.snapshot.spot - row.snapshot.strike) / row.snapshot.strike) * 10000.0
    if bps <= 5.0:
        return "m_le_5bps"
    if bps <= 15.0:
        return "m_5_15bps"
    if bps <= 30.0:
        return "m_15_30bps"
    return "m_gt_30bps"


def _rv_disagreement_bucket(item: _AnchorRow) -> str:
    anchors = (
        item.row.market_p_yes,
        item.row.current_calibrated_p_yes,
        item.row.brownian_p_yes,
        item.row.particle_p_yes,
    )
    diff = max(abs(item.rv_terminal_p_yes - anchor) for anchor in anchors)
    if diff <= 0.05:
        return "rv_agree_le_5pp"
    if diff <= 0.15:
        return "rv_disagree_5_15pp"
    return "rv_disagree_gt_15pp"


def _market_ev_metrics(report: ReplayReport) -> tuple[float, float]:
    grouped: dict[str, list[float]] = {}
    ev_grouped: dict[str, list[float]] = {}
    for decision in report.decisions:
        grouped.setdefault(decision.market_ticker, []).append(decision.counterfactual_pnl_cents)
        ev_grouped.setdefault(decision.market_ticker, []).append(
            max(decision.ev_yes_cents, decision.ev_no_cents)
        )
    predicted: list[float] = []
    realized: list[float] = []
    for market_ticker in sorted(grouped):
        pnl_values = grouped[market_ticker]
        ev_values = ev_grouped[market_ticker]
        if not pnl_values or not ev_values:
            continue
        predicted.append(_mean(ev_values))
        realized.append(_mean(pnl_values))
    if not predicted:
        return 0.0, 0.0
    return pairwise_rank_correlation_sign(predicted, realized), top_bucket_mean_pnl(
        predicted,
        realized,
        top_fraction=0.20,
    )


def _mean(values: Sequence[float] | object) -> float:
    vals = [float(value) for value in values]
    return sum(vals) / len(vals) if vals else 0.0


def _markdown(report: SpotRVAnchorSwitchLOROReport) -> str:
    lines = [
        "# Spot RV Anchor Switch LORO Report",
        "",
        f"- eligible_run_count: {len(report.run_inputs)}",
        f"- skipped_run_count: {len(report.skipped_run_roots)}",
        f"- anchors: {', '.join(report.anchors)}",
        f"- hypothesis_id: {report.hypothesis_id}",
        f"- spec_count: {len(report.specs)}",
        f"- min_bucket_clusters: {report.min_bucket_clusters}",
        f"- holdout_row_count: {len(report.holdout_rows)}",
        f"- candidate_ready_for_predeclared_shadow: {report.candidate_ready_for_predeclared_shadow}",
        f"- promotion_safe: {report.promotion_safe}",
        f"- conclusion: {report.conclusion}",
        "",
        "## Summary",
        "",
        "| spec | holdouts | total_pnl_cents | mean_brier | mean_log_loss | positive_pnl | beats_brownian | beats_market | beats_current | positive_ev_rank | positive_top_bucket | positive_market_ev_rank | positive_market_top_bucket | strict_gates | strict_all |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|",
    ]
    for row in report.summary_rows:
        lines.append(
            "| "
            f"{row.spec} | "
            f"{row.holdout_count} | "
            f"{row.total_counterfactual_pnl_cents:.4f} | "
            f"{row.mean_brier:.6f} | "
            f"{row.mean_log_loss:.6f} | "
            f"{row.positive_pnl_count}/{row.holdout_count} | "
            f"{row.beats_brownian_count}/{row.holdout_count} | "
            f"{row.beats_market_count}/{row.holdout_count} | "
            f"{row.beats_current_count}/{row.holdout_count} | "
            f"{row.positive_ev_rank_count}/{row.holdout_count} | "
            f"{row.positive_top_bucket_count}/{row.holdout_count} | "
            f"{row.positive_market_ev_rank_count}/{row.holdout_count} | "
            f"{row.positive_market_top_bucket_count}/{row.holdout_count} | "
            f"{row.strict_gate_count}/{row.holdout_count} | "
            f"{row.strict_all_holdouts} |"
        )
    lines.extend(
        [
            "",
            "## Holdouts",
            "",
            "| holdout | spec | global_anchor | buckets | selected | pnl_cents | brier | beats_brownian | beats_market | beats_current | ev_rank | top_bucket | market_ev_rank | top_market_bucket | strict |",
            "|---|---|---|---:|---:|---:|---:|---|---|---|---:|---:|---:|---:|---|",
        ]
    )
    for row in report.holdout_rows:
        lines.append(
            "| "
            f"{row.holdout_run} | "
            f"{row.spec} | "
            f"{row.global_anchor} | "
            f"{row.bucket_count} | "
            f"{row.selected_count} | "
            f"{row.total_counterfactual_pnl_cents:.4f} | "
            f"{row.brier:.6f} | "
            f"{row.beats_brownian} | "
            f"{row.beats_market} | "
            f"{row.beats_current_calibrated} | "
            f"{row.ev_rank_correlation_sign:.6f} | "
            f"{row.top_ev_bucket_pnl_cents:.4f} | "
            f"{row.market_ev_rank_correlation_sign:.6f} | "
            f"{row.top_market_ev_bucket_avg_pnl_cents:.4f} | "
            f"{row.strict_gate_pass} |"
        )
    lines.extend(
        [
            "",
            "## Run Inputs",
            "",
            "| run | rows | markets | spot_ticks | rv_fallback_rows | candidate_path | label_path | spot_tick_path |",
            "|---|---:|---:|---:|---:|---|---|---|",
        ]
    )
    for row in report.run_inputs:
        lines.append(
            "| "
            f"{row.name} | "
            f"{row.row_count} | "
            f"{row.market_count} | "
            f"{row.spot_tick_count} | "
            f"{row.rv_fallback_row_count} | "
            f"`{row.candidate_path}` | "
            f"`{row.label_path}` | "
            f"`{row.spot_tick_path}` |"
        )
    if report.skipped_run_roots:
        lines.extend(["", "## Skipped Runs", ""])
        for root in report.skipped_run_roots:
            lines.append(f"- `{root}`")
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    raise SystemExit(main())
