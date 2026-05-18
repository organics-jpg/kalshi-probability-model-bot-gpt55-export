from __future__ import annotations

import argparse
from dataclasses import replace
from datetime import datetime, timezone
from pathlib import Path
from statistics import median
from typing import Sequence

from .calibrators import OnlineLogitCalibrator
from .dynamic_particle_replay import DynamicParticleSpec, RollingVolEstimator
from .online_logit_particle_replay import (
    _add_market_update,
    _apply_available_market_updates,
    _apply_available_updates,
)
from .replay_runner import (
    ReplayConfig,
    ReplayInput,
    evaluate_replay,
    load_replay_inputs_from_jsonl,
    write_replay_report,
)
from .terminal_projection import brownian_terminal_probability


def materialize_variant_rows(
    rows: Sequence[ReplayInput],
    variant: str,
) -> list[ReplayInput]:
    if not rows:
        raise ValueError("at least one replay row is required")
    sorted_rows = sorted(rows, key=lambda row: (row.snapshot.decision_ts_utc, row.snapshot.market_ticker))
    contexts = _variant_contexts(sorted_rows)
    labels = [1 if row.label.result_yes else 0 for row in sorted_rows]
    if variant in {
        "late300_mc50_online_logit_rv600",
        "late300_mc75_online_logit_rv600",
        "late300_consensus_mc75_online_logit_rv600",
        "late180_mc75_online_logit_rv600",
    }:
        return _materialize_late_market_current_blend(sorted_rows, contexts, labels, variant)
    if variant.startswith("online_logit_market_mean_"):
        raw_name = variant.removeprefix("online_logit_market_mean_")
        raw_probs = [_raw_probability(context, raw_name) for context in contexts]
        return _apply_online_logit(sorted_rows, raw_probs, labels, update_mode="market_mean")
    if variant.startswith("online_logit_"):
        raw_name = variant.removeprefix("online_logit_")
        raw_probs = [_raw_probability(context, raw_name) for context in contexts]
        return _apply_online_logit(sorted_rows, raw_probs, labels, update_mode="candidate")
    return [
        replace(row, particle_p_yes=_clamp01(_raw_probability(context, variant)))
        for row, context in zip(sorted_rows, contexts)
    ]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Materialize a named diagnostic probability variant into a full strict replay report with decisions."
    )
    parser.add_argument("--candidates", required=True, type=Path)
    parser.add_argument("--labels", required=True, type=Path)
    parser.add_argument("--variant", required=True)
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--stem", default=None)
    parser.add_argument("--min-ev-cents", default=0.0, type=float)
    parser.add_argument("--min-fill-prob", default=0.0, type=float)
    parser.add_argument("--no-fill-penalty-cents", default=0.0, type=float)
    parser.add_argument(
        "--counterfactual-fill-policy",
        choices=["threshold", "always_fill", "never_fill"],
        default="threshold",
    )
    parser.add_argument("--counterfactual-fill-threshold", default=0.5, type=float)
    parser.add_argument("--default-annualized-vol", default=None, type=float)
    parser.add_argument("--allow-missing-labels", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    rows = load_replay_inputs_from_jsonl(
        args.candidates,
        args.labels,
        default_annualized_vol=args.default_annualized_vol,
        allow_missing_labels=bool(args.allow_missing_labels),
    )
    source_candidate_count = _line_count(args.candidates)
    skipped_unlabeled_count = max(0, source_candidate_count - len(rows))
    denominator_scope = "resolved_labeled_subset" if args.allow_missing_labels else "all_labeled_candidates"
    variant_rows = materialize_variant_rows(rows, args.variant)
    report = replace(
        evaluate_replay(
            variant_rows,
            ReplayConfig(
                min_ev_cents=args.min_ev_cents,
                min_fill_prob=args.min_fill_prob,
                no_fill_penalty_cents=args.no_fill_penalty_cents,
                counterfactual_fill_policy=args.counterfactual_fill_policy,
                counterfactual_fill_threshold=args.counterfactual_fill_threshold,
            ),
        ),
        source_candidate_count=source_candidate_count,
        skipped_unlabeled_count=skipped_unlabeled_count,
        denominator_scope=denominator_scope,
    )
    stem = args.stem or f"materialized_{_safe_stem(args.variant)}"
    json_path, md_path = write_replay_report(report, args.output_dir, stem)
    print(f"variant={args.variant}")
    print(f"candidate_count={report.candidate_count}")
    print(f"source_candidate_count={report.source_candidate_count}")
    print(f"skipped_unlabeled_count={report.skipped_unlabeled_count}")
    print(f"denominator_scope={report.denominator_scope}")
    print(f"selected_count={report.selected_count}")
    print(f"total_counterfactual_pnl_cents={report.total_counterfactual_pnl_cents:.4f}")
    print(f"particle_beats_brownian={report.particle_beats_brownian}")
    print(f"particle_beats_market={report.particle_beats_market}")
    print(f"particle_beats_current_calibrated={report.particle_beats_current_calibrated}")
    print(f"ev_rank_correlation_sign={report.ev_rank_correlation_sign:.6f}")
    print(f"top_ev_bucket_pnl_cents={report.top_ev_bucket_pnl_cents:.4f}")
    print(f"json_report={json_path}")
    print(f"md_report={md_path}")
    return 0


def _apply_online_logit(
    rows: Sequence[ReplayInput],
    raw_probs: Sequence[float],
    labels: Sequence[int],
    *,
    update_mode: str,
) -> list[ReplayInput]:
    calibrator = OnlineLogitCalibrator()
    pending_updates: list[tuple[datetime, float, int]] = []
    pending_market_updates = {}
    materialized: list[ReplayInput] = []
    for row, raw_p, label_int in zip(rows, raw_probs, labels):
        if update_mode == "candidate":
            _apply_available_updates(pending_updates, row.snapshot.decision_ts_utc, calibrator)
        elif update_mode == "market_mean":
            _apply_available_market_updates(
                pending_market_updates,
                row.snapshot.decision_ts_utc,
                calibrator,
            )
        else:
            raise ValueError(f"unsupported update_mode: {update_mode}")
        calibrated_p = _clamp01(calibrator.predict(raw_p))
        materialized.append(replace(row, particle_p_yes=calibrated_p))
        if update_mode == "candidate":
            pending_updates.append((row.label.label_available_ts_utc, raw_p, label_int))
        else:
            _add_market_update(
                pending_market_updates,
                row.snapshot.market_ticker,
                row.label.label_available_ts_utc,
                label_int,
                raw_p,
            )
    return materialized


def _variant_contexts(rows: Sequence[ReplayInput]) -> list[dict[str, float]]:
    specs = {
        spec.name: spec
        for spec in (
            DynamicParticleSpec("rolling_vol_120s", 120.0, 0.65, 0.20, 2.50, 3),
            DynamicParticleSpec("rolling_vol_300s", 300.0, 0.65, 0.20, 2.50, 3),
            DynamicParticleSpec("rolling_vol_600s", 600.0, 0.65, 0.20, 2.50, 3),
            DynamicParticleSpec("rolling_vol_300s_market25", 300.0, 0.65, 0.20, 2.50, 3, 0.25),
        )
    }
    estimators = {name: RollingVolEstimator(spec) for name, spec in specs.items()}
    contexts: list[dict[str, float]] = []
    for row in rows:
        seconds_to_close = max(
            0.0,
            (row.label.settlement_ts_utc - row.snapshot.decision_ts_utc).total_seconds(),
        )
        context = {
            "particle": row.particle_p_yes,
            "brownian": row.brownian_p_yes,
            "market": row.market_p_yes,
            "current_calibrated": row.current_calibrated_p_yes,
            "current": row.current_calibrated_p_yes,
        }
        for name, spec in specs.items():
            vol = estimators[name].observe_and_estimate(row.snapshot.decision_ts_utc, row.snapshot.spot)
            p_dynamic = brownian_terminal_probability(
                row.snapshot.spot,
                row.snapshot.strike,
                seconds_to_close,
                vol,
            )
            context[name] = (1.0 - spec.market_weight) * p_dynamic + spec.market_weight * row.market_p_yes
        contexts.append(context)
    return contexts


def _raw_probability(context: dict[str, float], variant: str) -> float:
    if variant in context:
        return _clamp01(context[variant])
    if variant == "median_current_rv300_rv600":
        return median((context["current"], context["rolling_vol_300s"], context["rolling_vol_600s"]))
    if variant == "mean_current_rv300_rv600":
        return (context["current"] + context["rolling_vol_300s"] + context["rolling_vol_600s"]) / 3.0
    if variant == "blend_40current_30rv300_30rv600":
        return 0.40 * context["current"] + 0.30 * context["rolling_vol_300s"] + 0.30 * context["rolling_vol_600s"]
    if variant == "blend_50rv600_30current_20market":
        return 0.50 * context["rolling_vol_600s"] + 0.30 * context["current"] + 0.20 * context["market"]
    if variant == "blend_40rv600_30rv300_20current_10market":
        return (
            0.40 * context["rolling_vol_600s"]
            + 0.30 * context["rolling_vol_300s"]
            + 0.20 * context["current"]
            + 0.10 * context["market"]
        )
    if variant == "median_market_current_rv600":
        return median((context["market"], context["current"], context["rolling_vol_600s"]))
    if variant == "mean_market_current_rv300_rv600":
        return (
            context["market"]
            + context["current"]
            + context["rolling_vol_300s"]
            + context["rolling_vol_600s"]
        ) / 4.0
    if variant == "blend_50current_25particle_25rv600":
        return 0.50 * context["current"] + 0.25 * context["particle"] + 0.25 * context["rolling_vol_600s"]
    if variant == "current_particle_75_25":
        return 0.75 * context["current"] + 0.25 * context["particle"]
    if variant == "market_current_50_50":
        return 0.50 * context["market"] + 0.50 * context["current"]
    if variant == "market_current_particle_40_40_20":
        return 0.40 * context["market"] + 0.40 * context["current"] + 0.20 * context["particle"]
    if variant == "market_particle_75_25":
        return 0.75 * context["market"] + 0.25 * context["particle"]
    raise ValueError(f"unknown variant: {variant}")


def _materialize_late_market_current_blend(
    rows: Sequence[ReplayInput],
    contexts: Sequence[dict[str, float]],
    labels: Sequence[int],
    variant: str,
) -> list[ReplayInput]:
    threshold_seconds = 300.0
    market_current_weight = 0.75
    consensus_only = False
    if variant == "late300_mc50_online_logit_rv600":
        market_current_weight = 0.50
    elif variant == "late300_mc75_online_logit_rv600":
        market_current_weight = 0.75
    elif variant == "late300_consensus_mc75_online_logit_rv600":
        market_current_weight = 0.75
        consensus_only = True
    elif variant == "late180_mc75_online_logit_rv600":
        threshold_seconds = 180.0
        market_current_weight = 0.75
    else:
        raise ValueError(f"unsupported late blend variant: {variant}")

    raw_probs = [_raw_probability(context, "rolling_vol_600s") for context in contexts]
    base_rows = _apply_online_logit(rows, raw_probs, labels, update_mode="market_mean")
    blended: list[ReplayInput] = []
    for base_row in base_rows:
        seconds_to_close = max(
            0.0,
            (base_row.label.settlement_ts_utc - base_row.snapshot.decision_ts_utc).total_seconds(),
        )
        p_base = _clamp01(base_row.particle_p_yes)
        p_market_current = _clamp01(
            0.5 * base_row.market_p_yes + 0.5 * base_row.current_calibrated_p_yes
        )
        should_blend = seconds_to_close <= threshold_seconds
        if consensus_only:
            should_blend = should_blend and _against_market_current_consensus(
                p_base,
                base_row.market_p_yes,
                base_row.current_calibrated_p_yes,
            )
        if should_blend:
            p = (1.0 - market_current_weight) * p_base + market_current_weight * p_market_current
            blended.append(replace(base_row, particle_p_yes=_clamp01(p)))
        else:
            blended.append(base_row)
    return blended


def _against_market_current_consensus(
    p_particle: float,
    p_market: float,
    p_current: float,
) -> bool:
    market_side = p_market >= 0.5
    current_side = p_current >= 0.5
    particle_side = p_particle >= 0.5
    return market_side == current_side and particle_side != market_side


def _line_count(path: Path) -> int:
    with path.open("r", encoding="utf-8", errors="replace") as handle:
        return sum(1 for line in handle if line.strip())


def _safe_stem(value: str) -> str:
    return "".join(ch if ch.isalnum() or ch in {"_", "-"} else "_" for ch in value)


def _clamp01(value: float) -> float:
    return max(0.0, min(1.0, float(value)))


if __name__ == "__main__":
    raise SystemExit(main())
