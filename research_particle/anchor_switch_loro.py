from __future__ import annotations

import argparse
import json
import math
from dataclasses import asdict, dataclass, replace
from pathlib import Path
from typing import Callable, Mapping, Sequence

from .meta_probability_loro import RunInputSet, _load_run
from .replay_runner import ReplayConfig, ReplayInput, ReplayReport, evaluate_replay
from .validation import brier_score, log_loss


ANCHORS = ("brownian", "market", "current_calibrated", "particle")
BucketFn = Callable[[ReplayInput], str]


@dataclass(frozen=True)
class AnchorSwitchSpec:
    name: str
    bucket_fn: BucketFn


@dataclass(frozen=True)
class TrainedAnchorSwitch:
    spec: str
    train_run_count: int
    train_cluster_count: int
    min_bucket_clusters: int
    global_anchor: str
    bucket_anchors: dict[str, str]


@dataclass(frozen=True)
class AnchorSwitchHoldoutRow:
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
    strict_gate_pass: bool


@dataclass(frozen=True)
class AnchorSwitchSummaryRow:
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
    strict_gate_count: int
    strict_all_holdouts: bool


@dataclass(frozen=True)
class AnchorSwitchLOROReport:
    run_inputs: tuple[RunInputSet, ...]
    specs: tuple[str, ...]
    min_bucket_clusters: int
    holdout_rows: tuple[AnchorSwitchHoldoutRow, ...]
    summary_rows: tuple[AnchorSwitchSummaryRow, ...]
    promotion_safe: bool
    conclusion: str


def build_anchor_switch_loro_report(
    run_roots: Sequence[Path],
    *,
    min_bucket_clusters: int = 3,
    replay_config: ReplayConfig | None = None,
) -> AnchorSwitchLOROReport:
    if len(run_roots) < 2:
        raise ValueError("at least two run roots are required")
    if min_bucket_clusters < 1:
        raise ValueError("min_bucket_clusters must be positive")
    cfg = replay_config or ReplayConfig(min_fill_prob=0.5, counterfactual_fill_threshold=0.5)
    specs = _specs()
    loaded_runs = [_load_run(root) for root in run_roots]
    holdout_rows: list[AnchorSwitchHoldoutRow] = []
    for holdout_name, holdout_meta, holdout_raw_rows in loaded_runs:
        train_rows = [
            row
            for run_name, _, rows in loaded_runs
            if run_name != holdout_name
            for row in rows
        ]
        for spec in specs:
            model = _train_anchor_switch(
                spec,
                train_rows,
                train_run_count=len(run_roots) - 1,
                min_bucket_clusters=min_bucket_clusters,
            )
            switched_rows = _apply_anchor_switch(model, spec, holdout_raw_rows)
            replay = evaluate_replay(switched_rows, cfg)
            strict = _strict_gate(replay)
            holdout_rows.append(
                AnchorSwitchHoldoutRow(
                    holdout_run=holdout_name,
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
                    strict_gate_pass=strict,
                )
            )
    summaries = tuple(_summarize(holdout_rows))
    promotion_safe = any(row.strict_all_holdouts for row in summaries)
    conclusion = (
        "At least one state-bucket anchor switch passed all strict locked holdouts; "
        "still require a fresh predeclared shadow run before promotion."
        if promotion_safe
        else "No state-bucket anchor switch passed strict locked holdout gates."
    )
    return AnchorSwitchLOROReport(
        run_inputs=tuple(meta for _, meta, _ in loaded_runs),
        specs=tuple(spec.name for spec in specs),
        min_bucket_clusters=min_bucket_clusters,
        holdout_rows=tuple(holdout_rows),
        summary_rows=summaries,
        promotion_safe=promotion_safe,
        conclusion=conclusion,
    )


def write_anchor_switch_loro_report(
    report: AnchorSwitchLOROReport,
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
        description="Leave-one-run-out state-bucket anchor switching diagnostic for locked particle replays."
    )
    parser.add_argument("--run-root", action="append", required=True, type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--stem", default="anchor_switch_loro")
    parser.add_argument("--min-bucket-clusters", default=3, type=int)
    parser.add_argument("--min-fill-prob", default=0.5, type=float)
    parser.add_argument("--counterfactual-fill-threshold", default=0.5, type=float)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    report = build_anchor_switch_loro_report(
        args.run_root,
        min_bucket_clusters=args.min_bucket_clusters,
        replay_config=ReplayConfig(
            min_fill_prob=args.min_fill_prob,
            counterfactual_fill_threshold=args.counterfactual_fill_threshold,
        ),
    )
    json_path, md_path = write_anchor_switch_loro_report(report, args.output_dir, args.stem)
    print(f"run_count={len(report.run_inputs)}")
    print(f"spec_count={len(report.specs)}")
    print(f"holdout_row_count={len(report.holdout_rows)}")
    print(f"summary_row_count={len(report.summary_rows)}")
    print(f"promotion_safe={report.promotion_safe}")
    print(f"json_report={json_path}")
    print(f"md_report={md_path}")
    return 0


def _train_anchor_switch(
    spec: AnchorSwitchSpec,
    rows: Sequence[ReplayInput],
    *,
    train_run_count: int,
    min_bucket_clusters: int,
) -> TrainedAnchorSwitch:
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
    return TrainedAnchorSwitch(
        spec=spec.name,
        train_run_count=train_run_count,
        train_cluster_count=len(clusters),
        min_bucket_clusters=min_bucket_clusters,
        global_anchor=global_anchor,
        bucket_anchors=bucket_anchors,
    )


def _cluster_samples(spec: AnchorSwitchSpec, rows: Sequence[ReplayInput]) -> list[dict[str, float | int | str]]:
    grouped: dict[tuple[str, str], list[ReplayInput]] = {}
    for row in rows:
        grouped.setdefault((row.snapshot.market_ticker, spec.bucket_fn(row)), []).append(row)
    samples: list[dict[str, float | int | str]] = []
    for (_, bucket), bucket_rows in grouped.items():
        label = 1 if bucket_rows[0].label.result_yes else 0
        sample: dict[str, float | int | str] = {"bucket": bucket, "label": label}
        for anchor in ANCHORS:
            sample[anchor] = sum(_anchor_prob(row, anchor) for row in bucket_rows) / len(bucket_rows)
        samples.append(sample)
    return samples


def _best_anchor(samples: Sequence[Mapping[str, float | int | str]]) -> str:
    labels = [int(sample["label"]) for sample in samples]
    return min(
        ANCHORS,
        key=lambda anchor: (
            brier_score([float(sample[anchor]) for sample in samples], labels),
            log_loss([float(sample[anchor]) for sample in samples], labels),
        ),
    )


def _apply_anchor_switch(
    model: TrainedAnchorSwitch,
    spec: AnchorSwitchSpec,
    rows: Sequence[ReplayInput],
) -> list[ReplayInput]:
    switched: list[ReplayInput] = []
    for row in rows:
        bucket = spec.bucket_fn(row)
        anchor = model.bucket_anchors.get(bucket, model.global_anchor)
        switched.append(replace(row, particle_p_yes=_anchor_prob(row, anchor)))
    return switched


def _anchor_prob(row: ReplayInput, anchor: str) -> float:
    if anchor == "brownian":
        return row.brownian_p_yes
    if anchor == "market":
        return row.market_p_yes
    if anchor == "current_calibrated":
        return row.current_calibrated_p_yes
    if anchor == "particle":
        return row.particle_p_yes
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


def _summarize(rows: Sequence[AnchorSwitchHoldoutRow]) -> list[AnchorSwitchSummaryRow]:
    grouped: dict[str, list[AnchorSwitchHoldoutRow]] = {}
    for row in rows:
        grouped.setdefault(row.spec, []).append(row)
    summaries: list[AnchorSwitchSummaryRow] = []
    for spec in sorted(grouped):
        spec_rows = grouped[spec]
        strict_count = sum(1 for row in spec_rows if row.strict_gate_pass)
        summaries.append(
            AnchorSwitchSummaryRow(
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


def _specs() -> tuple[AnchorSwitchSpec, ...]:
    return (
        AnchorSwitchSpec("global", lambda row: "all"),
        AnchorSwitchSpec("time", lambda row: _time_bucket(row)),
        AnchorSwitchSpec("moneyness", lambda row: _moneyness_bucket(row)),
        AnchorSwitchSpec("time_moneyness", lambda row: f"{_time_bucket(row)}|{_moneyness_bucket(row)}"),
        AnchorSwitchSpec(
            "time_moneyness_disagreement",
            lambda row: f"{_time_bucket(row)}|{_moneyness_bucket(row)}|{_anchor_disagreement_bucket(row)}",
        ),
        AnchorSwitchSpec(
            "time_spread_disagreement",
            lambda row: f"{_time_bucket(row)}|{_spread_bucket(row)}|{_anchor_disagreement_bucket(row)}",
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


def _spread_bucket(row: ReplayInput) -> str:
    spread = max(0.0, row.snapshot.yes_ask_cents + row.snapshot.no_ask_cents - 100.0)
    if spread <= 2.0:
        return "spread_le_2c"
    if spread <= 5.0:
        return "spread_2_5c"
    return "spread_gt_5c"


def _anchor_disagreement_bucket(row: ReplayInput) -> str:
    diff = max(
        abs(row.market_p_yes - row.current_calibrated_p_yes),
        abs(row.market_p_yes - row.brownian_p_yes),
        abs(row.current_calibrated_p_yes - row.brownian_p_yes),
    )
    if diff <= 0.05:
        return "agree_le_5pp"
    if diff <= 0.15:
        return "disagree_5_15pp"
    return "disagree_gt_15pp"


def _mean(values: Sequence[float] | object) -> float:
    vals = [float(value) for value in values]
    return sum(vals) / len(vals) if vals else 0.0


def _markdown(report: AnchorSwitchLOROReport) -> str:
    lines = [
        "# Anchor Switch LORO Report",
        "",
        f"- run_count: {len(report.run_inputs)}",
        f"- spec_count: {len(report.specs)}",
        f"- min_bucket_clusters: {report.min_bucket_clusters}",
        f"- holdout_row_count: {len(report.holdout_rows)}",
        f"- promotion_safe: {report.promotion_safe}",
        f"- conclusion: {report.conclusion}",
        "",
        "## Summary",
        "",
        "| spec | holdouts | total_pnl_cents | mean_brier | mean_log_loss | positive_pnl | beats_brownian | beats_market | beats_current | positive_ev_rank | positive_top_bucket | strict_gates | strict_all |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|",
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
            f"{row.strict_gate_count}/{row.holdout_count} | "
            f"{row.strict_all_holdouts} |"
        )
    lines.extend(
        [
            "",
            "## Holdouts",
            "",
            "| holdout | spec | global_anchor | buckets | selected | pnl_cents | brier | beats_brownian | beats_market | beats_current | ev_rank | top_bucket | strict |",
            "|---|---|---|---:|---:|---:|---:|---|---|---|---:|---:|---|",
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
