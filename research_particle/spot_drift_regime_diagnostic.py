from __future__ import annotations

import argparse
import json
import math
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Callable, Mapping, Sequence

from .replay_runner import ReplayConfig, ReplayDecision, ReplayInput, evaluate_replay
from .spot_drift_terminal_diagnostic import (
    SpotDriftTerminalSpec,
    _load_eligible_run,
    _specs,
    materialize_spot_drift_terminal_rows,
    recent_spot_drift_per_second,
)
from .spot_context_merge import SpotTickRow


@dataclass(frozen=True)
class SpotDriftRegimeRunInput:
    name: str
    root: str
    row_count: int
    market_count: int
    spot_tick_count: int


@dataclass(frozen=True)
class SpotDriftDecisionFeature:
    run: str
    spec: str
    market_ticker: str
    selected: bool
    side: str
    won: bool | None
    counterfactual_pnl_cents: float
    seconds_to_close: float
    total_drift_bps: float
    drift_fallback: bool
    drift_sign_bucket: str
    drift_abs_bucket: str
    drift_side_alignment_bucket: str
    time_to_close_bucket: str
    moneyness_bps: float
    moneyness_sign_bucket: str
    moneyness_abs_bucket: str
    market_current_consensus_bucket: str


@dataclass(frozen=True)
class SpotDriftRegimeBucketRow:
    spec: str
    bucket_type: str
    bucket: str
    selected_count: int
    win_count: int
    win_rate: float
    total_counterfactual_pnl_cents: float
    avg_counterfactual_pnl_cents: float
    positive_run_count: int
    run_count: int


@dataclass(frozen=True)
class SpotDriftRegimeRuleRunRow:
    run: str
    spec: str
    rule: str
    selected_count: int
    win_count: int
    win_rate: float
    total_counterfactual_pnl_cents: float


@dataclass(frozen=True)
class SpotDriftRegimeRuleSummaryRow:
    spec: str
    rule: str
    run_count: int
    selected_count: int
    positive_run_count: int
    nonzero_run_count: int
    total_counterfactual_pnl_cents: float
    min_run_pnl_cents: float
    stable_positive: bool


@dataclass(frozen=True)
class SpotDriftRegimeDiagnosticReport:
    run_inputs: tuple[SpotDriftRegimeRunInput, ...]
    skipped_run_roots: tuple[str, ...]
    specs: tuple[str, ...]
    feature_count: int
    selected_count: int
    bucket_rows: tuple[SpotDriftRegimeBucketRow, ...]
    rule_run_rows: tuple[SpotDriftRegimeRuleRunRow, ...]
    rule_summary_rows: tuple[SpotDriftRegimeRuleSummaryRow, ...]
    stable_positive_rules: tuple[str, ...]
    candidate_ready_for_predeclared_shadow: bool
    promotion_safe: bool
    conclusion: str


def build_spot_drift_regime_diagnostic(
    run_roots: Sequence[Path],
    *,
    spec_names: Sequence[str] | None = None,
    replay_config: ReplayConfig | None = None,
    max_spot_age_ms: float = 5_000.0,
) -> SpotDriftRegimeDiagnosticReport:
    cfg = replay_config or ReplayConfig(min_fill_prob=0.5, counterfactual_fill_threshold=0.5)
    loaded_runs: list[tuple[SpotDriftRegimeRunInput, tuple[ReplayInput, ...], tuple[SpotTickRow, ...]]] = []
    skipped: list[str] = []
    for root in run_roots:
        loaded = _load_eligible_run(root)
        if loaded is None:
            skipped.append(str(root))
            continue
        meta, rows, ticks = loaded
        loaded_runs.append(
            (
                SpotDriftRegimeRunInput(
                    name=meta.name,
                    root=meta.root,
                    row_count=meta.row_count,
                    market_count=meta.market_count,
                    spot_tick_count=meta.spot_tick_count,
                ),
                rows,
                ticks,
            )
        )

    selected_specs = _select_specs(spec_names)
    features: list[SpotDriftDecisionFeature] = []
    for meta, rows, ticks in loaded_runs:
        for spec in selected_specs:
            materialized, _ = materialize_spot_drift_terminal_rows(
                rows,
                ticks,
                spec,
                max_spot_age_ms=max_spot_age_ms,
            )
            replay = evaluate_replay(materialized, cfg)
            features.extend(
                _decision_features(
                    meta.name,
                    spec,
                    rows,
                    ticks,
                    replay.decisions,
                    max_spot_age_ms=max_spot_age_ms,
                )
            )

    bucket_rows = tuple(_build_bucket_rows(features, run_count=len(loaded_runs)))
    rule_run_rows = tuple(_build_rule_run_rows(features))
    rule_summary_rows = tuple(_summarize_rules(rule_run_rows, run_count=len(loaded_runs)))
    stable_rules = tuple(
        f"{row.spec}:{row.rule}" for row in rule_summary_rows if row.stable_positive
    )
    conclusion = (
        "At least one post-hoc drift/regime rule was positive in every eligible run. "
        "This only nominates a fresh predeclared shadow test; it is not promotion evidence."
        if stable_rules
        else "No simple post-hoc drift/regime rule was positive in every eligible run."
    )
    return SpotDriftRegimeDiagnosticReport(
        run_inputs=tuple(meta for meta, _, _ in loaded_runs),
        skipped_run_roots=tuple(skipped),
        specs=tuple(spec.name for spec in selected_specs),
        feature_count=len(features),
        selected_count=sum(1 for row in features if row.selected),
        bucket_rows=bucket_rows,
        rule_run_rows=rule_run_rows,
        rule_summary_rows=rule_summary_rows,
        stable_positive_rules=stable_rules,
        candidate_ready_for_predeclared_shadow=bool(stable_rules),
        promotion_safe=False,
        conclusion=conclusion,
    )


def write_spot_drift_regime_diagnostic(
    report: SpotDriftRegimeDiagnosticReport,
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
        description="Diagnose whether next-second spot drift only works in simple timestamp-safe regimes."
    )
    parser.add_argument("--run-root", action="append", required=True, type=Path)
    parser.add_argument("--spec", action="append", default=None, help="optional spot drift spec name to inspect")
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--stem", default="spot_drift_regime_diagnostic")
    parser.add_argument("--max-spot-age-ms", default=5_000.0, type=float)
    parser.add_argument("--min-fill-prob", default=0.5, type=float)
    parser.add_argument("--counterfactual-fill-threshold", default=0.5, type=float)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    report = build_spot_drift_regime_diagnostic(
        args.run_root,
        spec_names=args.spec,
        replay_config=ReplayConfig(
            min_fill_prob=args.min_fill_prob,
            counterfactual_fill_threshold=args.counterfactual_fill_threshold,
        ),
        max_spot_age_ms=args.max_spot_age_ms,
    )
    json_path, md_path = write_spot_drift_regime_diagnostic(report, args.output_dir, args.stem)
    print(f"eligible_run_count={len(report.run_inputs)}")
    print(f"skipped_run_count={len(report.skipped_run_roots)}")
    print(f"spec_count={len(report.specs)}")
    print(f"feature_count={report.feature_count}")
    print(f"selected_count={report.selected_count}")
    print(f"stable_positive_rules={len(report.stable_positive_rules)}")
    if report.stable_positive_rules:
        print("stable_rule_names=" + ",".join(report.stable_positive_rules[:10]))
    print(f"candidate_ready_for_predeclared_shadow={report.candidate_ready_for_predeclared_shadow}")
    print(f"promotion_safe={report.promotion_safe}")
    print(f"json_report={json_path}")
    print(f"md_report={md_path}")
    return 0


def _decision_features(
    run: str,
    spec: SpotDriftTerminalSpec,
    rows: Sequence[ReplayInput],
    ticks: Sequence[SpotTickRow],
    decisions: Sequence[ReplayDecision],
    *,
    max_spot_age_ms: float,
) -> list[SpotDriftDecisionFeature]:
    sorted_rows = sorted(rows, key=lambda item: (item.snapshot.decision_ts_utc, item.snapshot.market_ticker))
    if len(sorted_rows) != len(decisions):
        raise ValueError("decision count does not match materialized row count")
    times = [tick.available_ts_utc for tick in ticks]
    prices = [float(tick.price) for tick in ticks]
    features: list[SpotDriftDecisionFeature] = []
    for row, decision in zip(sorted_rows, decisions):
        seconds_to_close = max(0.0, (row.label.settlement_ts_utc - row.snapshot.decision_ts_utc).total_seconds())
        drift_per_second, drift_fallback = recent_spot_drift_per_second(
            row,
            times,
            prices,
            spec.drift_window_seconds,
            spec.drift_weight,
            spec.total_drift_cap_bps,
            max_spot_age_ms=max_spot_age_ms,
        )
        total_drift_bps = 10_000.0 * drift_per_second * seconds_to_close
        moneyness_bps = _moneyness_bps(row)
        features.append(
            SpotDriftDecisionFeature(
                run=run,
                spec=spec.name,
                market_ticker=row.snapshot.market_ticker,
                selected=decision.selected,
                side=str(decision.side or "none"),
                won=decision.won,
                counterfactual_pnl_cents=decision.counterfactual_pnl_cents,
                seconds_to_close=seconds_to_close,
                total_drift_bps=total_drift_bps,
                drift_fallback=drift_fallback,
                drift_sign_bucket=_drift_sign_bucket(total_drift_bps, drift_fallback),
                drift_abs_bucket=_drift_abs_bucket(total_drift_bps, drift_fallback),
                drift_side_alignment_bucket=_drift_side_alignment_bucket(decision, total_drift_bps, drift_fallback),
                time_to_close_bucket=_time_bucket(seconds_to_close),
                moneyness_bps=moneyness_bps,
                moneyness_sign_bucket=_moneyness_sign_bucket(moneyness_bps),
                moneyness_abs_bucket=_moneyness_abs_bucket(moneyness_bps),
                market_current_consensus_bucket=_market_current_consensus_bucket(decision),
            )
        )
    return features


def _build_bucket_rows(
    features: Sequence[SpotDriftDecisionFeature],
    *,
    run_count: int,
) -> list[SpotDriftRegimeBucketRow]:
    selected = [row for row in features if row.selected]
    rows: list[SpotDriftRegimeBucketRow] = []
    labelers: tuple[tuple[str, Callable[[SpotDriftDecisionFeature], str]], ...] = (
        ("side", lambda row: row.side),
        ("drift_sign", lambda row: row.drift_sign_bucket),
        ("drift_abs", lambda row: row.drift_abs_bucket),
        ("drift_alignment", lambda row: row.drift_side_alignment_bucket),
        ("time_to_close", lambda row: row.time_to_close_bucket),
        ("moneyness_sign", lambda row: row.moneyness_sign_bucket),
        ("moneyness_abs", lambda row: row.moneyness_abs_bucket),
        ("market_current_consensus", lambda row: row.market_current_consensus_bucket),
    )
    for spec in sorted({row.spec for row in selected}):
        spec_rows = [row for row in selected if row.spec == spec]
        for bucket_type, labeler in labelers:
            grouped: dict[str, list[SpotDriftDecisionFeature]] = {}
            for row in spec_rows:
                grouped.setdefault(labeler(row), []).append(row)
            for bucket in sorted(grouped):
                bucket_features = grouped[bucket]
                rows.append(_bucket_row(spec, bucket_type, bucket, bucket_features, run_count=run_count))
    return sorted(
        rows,
        key=lambda row: (
            row.spec,
            row.bucket_type,
            row.bucket,
        ),
    )


def _bucket_row(
    spec: str,
    bucket_type: str,
    bucket: str,
    rows: Sequence[SpotDriftDecisionFeature],
    *,
    run_count: int,
) -> SpotDriftRegimeBucketRow:
    wins = sum(1 for row in rows if row.won)
    pnl = sum(row.counterfactual_pnl_cents for row in rows)
    runs_positive = {
        run
        for run in {row.run for row in rows}
        if sum(row.counterfactual_pnl_cents for row in rows if row.run == run) > 0.0
    }
    return SpotDriftRegimeBucketRow(
        spec=spec,
        bucket_type=bucket_type,
        bucket=bucket,
        selected_count=len(rows),
        win_count=wins,
        win_rate=(wins / len(rows) if rows else 0.0),
        total_counterfactual_pnl_cents=pnl,
        avg_counterfactual_pnl_cents=(pnl / len(rows) if rows else 0.0),
        positive_run_count=len(runs_positive),
        run_count=run_count,
    )


def _build_rule_run_rows(features: Sequence[SpotDriftDecisionFeature]) -> list[SpotDriftRegimeRuleRunRow]:
    rules: Mapping[str, Callable[[SpotDriftDecisionFeature], bool]] = {
        "base": lambda row: True,
        "require_drift_aligned": lambda row: row.drift_side_alignment_bucket == "aligned_with_drift",
        "skip_drift_against": lambda row: row.drift_side_alignment_bucket != "against_drift",
        "require_abs_drift_ge_1bps": lambda row: abs(row.total_drift_bps) >= 1.0 and not row.drift_fallback,
        "require_abs_drift_ge_3bps": lambda row: abs(row.total_drift_bps) >= 3.0 and not row.drift_fallback,
        "require_abs_drift_ge_6bps": lambda row: abs(row.total_drift_bps) >= 6.0 and not row.drift_fallback,
        "require_drift_aligned_abs_ge_1bps": (
            lambda row: row.drift_side_alignment_bucket == "aligned_with_drift"
            and abs(row.total_drift_bps) >= 1.0
        ),
        "require_drift_aligned_abs_ge_3bps": (
            lambda row: row.drift_side_alignment_bucket == "aligned_with_drift"
            and abs(row.total_drift_bps) >= 3.0
        ),
        "require_late_le_300s": lambda row: row.seconds_to_close <= 300.0,
        "require_mid_181_600s": lambda row: 180.0 < row.seconds_to_close <= 600.0,
        "require_near_strike_abs_le_10bps": lambda row: abs(row.moneyness_bps) <= 10.0,
        "require_drift_aligned_near_strike_abs_le_10bps": (
            lambda row: row.drift_side_alignment_bucket == "aligned_with_drift"
            and abs(row.moneyness_bps) <= 10.0
        ),
        "require_market_current_consensus_alignment": (
            lambda row: row.market_current_consensus_bucket == "aligned_with_market_current"
        ),
        "skip_against_market_current_consensus": (
            lambda row: row.market_current_consensus_bucket != "against_market_current"
        ),
    }
    selected = [row for row in features if row.selected]
    rows: list[SpotDriftRegimeRuleRunRow] = []
    for (run, spec), group in _group_by_run_spec(selected).items():
        for rule, keep in rules.items():
            kept = [row for row in group if keep(row)]
            wins = sum(1 for row in kept if row.won)
            pnl = sum(row.counterfactual_pnl_cents for row in kept)
            rows.append(
                SpotDriftRegimeRuleRunRow(
                    run=run,
                    spec=spec,
                    rule=rule,
                    selected_count=len(kept),
                    win_count=wins,
                    win_rate=(wins / len(kept) if kept else 0.0),
                    total_counterfactual_pnl_cents=pnl,
                )
            )
    return rows


def _summarize_rules(
    rows: Sequence[SpotDriftRegimeRuleRunRow],
    *,
    run_count: int,
) -> list[SpotDriftRegimeRuleSummaryRow]:
    grouped: dict[tuple[str, str], list[SpotDriftRegimeRuleRunRow]] = {}
    for row in rows:
        grouped.setdefault((row.spec, row.rule), []).append(row)
    summaries: list[SpotDriftRegimeRuleSummaryRow] = []
    for (spec, rule), rule_rows in grouped.items():
        positive = sum(1 for row in rule_rows if row.total_counterfactual_pnl_cents > 0.0)
        nonzero = sum(1 for row in rule_rows if row.selected_count > 0)
        min_pnl = min((row.total_counterfactual_pnl_cents for row in rule_rows), default=0.0)
        summaries.append(
            SpotDriftRegimeRuleSummaryRow(
                spec=spec,
                rule=rule,
                run_count=len(rule_rows),
                selected_count=sum(row.selected_count for row in rule_rows),
                positive_run_count=positive,
                nonzero_run_count=nonzero,
                total_counterfactual_pnl_cents=sum(row.total_counterfactual_pnl_cents for row in rule_rows),
                min_run_pnl_cents=min_pnl,
                stable_positive=(
                    len(rule_rows) == run_count
                    and nonzero == run_count
                    and positive == run_count
                ),
            )
        )
    return sorted(
        summaries,
        key=lambda row: (
            row.stable_positive,
            row.positive_run_count,
            row.total_counterfactual_pnl_cents,
            row.selected_count,
        ),
        reverse=True,
    )


def _select_specs(spec_names: Sequence[str] | None) -> tuple[SpotDriftTerminalSpec, ...]:
    specs = {spec.name: spec for spec in _specs()}
    if not spec_names:
        return tuple(specs.values())
    missing = sorted(set(spec_names) - set(specs))
    if missing:
        raise ValueError(f"unknown spot drift spec(s): {', '.join(missing)}")
    return tuple(specs[name] for name in spec_names)


def _group_by_run_spec(
    rows: Sequence[SpotDriftDecisionFeature],
) -> dict[tuple[str, str], list[SpotDriftDecisionFeature]]:
    grouped: dict[tuple[str, str], list[SpotDriftDecisionFeature]] = {}
    for row in rows:
        grouped.setdefault((row.run, row.spec), []).append(row)
    return grouped


def _drift_sign_bucket(total_drift_bps: float, fallback: bool) -> str:
    if fallback:
        return "fallback"
    if total_drift_bps >= 0.50:
        return "positive"
    if total_drift_bps <= -0.50:
        return "negative"
    return "flat"


def _drift_abs_bucket(total_drift_bps: float, fallback: bool) -> str:
    if fallback:
        return "fallback"
    value = abs(total_drift_bps)
    if value < 0.50:
        return "000_lt_0_5bps"
    if value < 1.0:
        return "001_0_5_1bps"
    if value < 3.0:
        return "002_1_3bps"
    if value < 6.0:
        return "003_3_6bps"
    return "004_ge_6bps"


def _drift_side_alignment_bucket(
    decision: ReplayDecision,
    total_drift_bps: float,
    fallback: bool,
) -> str:
    if not decision.selected or decision.side is None:
        return "not_selected"
    if fallback or abs(total_drift_bps) < 0.50:
        return "flat_or_fallback"
    drift_side = "yes" if total_drift_bps > 0.0 else "no"
    return "aligned_with_drift" if decision.side == drift_side else "against_drift"


def _time_bucket(seconds_to_close: float) -> str:
    if seconds_to_close <= 60.0:
        return "000_060s"
    if seconds_to_close <= 180.0:
        return "061_180s"
    if seconds_to_close <= 300.0:
        return "181_300s"
    if seconds_to_close <= 600.0:
        return "301_600s"
    return "gt_600s"


def _moneyness_bps(row: ReplayInput) -> float:
    if row.snapshot.spot <= 0.0 or row.snapshot.strike <= 0.0:
        return 0.0
    return 10_000.0 * math.log(row.snapshot.spot / row.snapshot.strike)


def _moneyness_sign_bucket(moneyness_bps: float) -> str:
    if moneyness_bps >= 2.0:
        return "spot_above_strike"
    if moneyness_bps <= -2.0:
        return "spot_below_strike"
    return "spot_near_strike"


def _moneyness_abs_bucket(moneyness_bps: float) -> str:
    value = abs(moneyness_bps)
    if value <= 5.0:
        return "000_le_5bps"
    if value <= 10.0:
        return "001_5_10bps"
    if value <= 20.0:
        return "002_10_20bps"
    if value <= 40.0:
        return "003_20_40bps"
    return "004_gt_40bps"


def _market_current_consensus_bucket(decision: ReplayDecision) -> str:
    if not decision.selected or decision.side is None:
        return "not_selected"
    market_side = "yes" if decision.market_p_yes >= 0.5 else "no"
    current_side = "yes" if decision.current_calibrated_p_yes >= 0.5 else "no"
    if market_side != current_side:
        return "market_current_disagree"
    if decision.side == market_side:
        return "aligned_with_market_current"
    return "against_market_current"


def _markdown(report: SpotDriftRegimeDiagnosticReport) -> str:
    lines = [
        "# Spot Drift Regime Diagnostic",
        "",
        f"- eligible_run_count: {len(report.run_inputs)}",
        f"- skipped_run_count: {len(report.skipped_run_roots)}",
        f"- spec_count: {len(report.specs)}",
        f"- feature_count: {report.feature_count}",
        f"- selected_count: {report.selected_count}",
        f"- stable_positive_rules: {len(report.stable_positive_rules)}",
        f"- candidate_ready_for_predeclared_shadow: {report.candidate_ready_for_predeclared_shadow}",
        f"- promotion_safe: {report.promotion_safe}",
        f"- conclusion: {report.conclusion}",
        "",
        "## Rule Summary",
        "",
        "| spec | rule | positive_runs | nonzero_runs | selected | pnl_cents | min_run_pnl_cents | stable_positive |",
        "|---|---|---:|---:|---:|---:|---:|---|",
    ]
    for row in report.rule_summary_rows:
        lines.append(
            "| "
            f"{row.spec} | "
            f"{row.rule} | "
            f"{row.positive_run_count}/{row.run_count} | "
            f"{row.nonzero_run_count}/{row.run_count} | "
            f"{row.selected_count} | "
            f"{row.total_counterfactual_pnl_cents:.4f} | "
            f"{row.min_run_pnl_cents:.4f} | "
            f"{row.stable_positive} |"
        )
    lines.extend(
        [
            "",
            "## Buckets",
            "",
            "| spec | type | bucket | selected | win_rate | pnl_cents | avg_pnl_cents | positive_runs |",
            "|---|---|---|---:|---:|---:|---:|---:|",
        ]
    )
    for row in report.bucket_rows:
        lines.append(
            "| "
            f"{row.spec} | "
            f"{row.bucket_type} | "
            f"{row.bucket} | "
            f"{row.selected_count} | "
            f"{row.win_rate:.4f} | "
            f"{row.total_counterfactual_pnl_cents:.4f} | "
            f"{row.avg_counterfactual_pnl_cents:.4f} | "
            f"{row.positive_run_count}/{row.run_count} |"
        )
    lines.extend(
        [
            "",
            "## Rule By Run",
            "",
            "| run | spec | rule | selected | win_rate | pnl_cents |",
            "|---|---|---|---:|---:|---:|",
        ]
    )
    for row in report.rule_run_rows:
        lines.append(
            "| "
            f"{row.run} | "
            f"{row.spec} | "
            f"{row.rule} | "
            f"{row.selected_count} | "
            f"{row.win_rate:.4f} | "
            f"{row.total_counterfactual_pnl_cents:.4f} |"
        )
    lines.extend(["", "## Run Inputs", "", "| run | rows | markets | spot_ticks |", "|---|---:|---:|---:|"])
    for row in report.run_inputs:
        lines.append(f"| {row.name} | {row.row_count} | {row.market_count} | {row.spot_tick_count} |")
    if report.skipped_run_roots:
        lines.extend(["", "## Skipped Runs", ""])
        lines.extend(f"- `{root}`" for root in report.skipped_run_roots)
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    raise SystemExit(main())
