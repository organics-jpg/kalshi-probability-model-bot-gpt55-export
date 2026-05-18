from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable, Literal, Mapping, Sequence

from .calibrators import LabelGatedACICalibrator
from .ev_decision import expected_pnl_cents
from .replay import FutureDataLeakageError
from .schemas import CandidateSnapshot, SettlementLabel, Side
from .terminal_projection import brownian_terminal_probability
from .validation import brier_score, log_loss, pairwise_rank_correlation_sign, top_bucket_mean_pnl


FillPolicy = Literal["threshold", "always_fill", "never_fill"]


@dataclass(frozen=True)
class ReplayConfig:
    min_ev_cents: float = 0.0
    min_fill_prob: float = 0.0
    no_fill_penalty_cents: float = 0.0
    counterfactual_fill_policy: FillPolicy = "threshold"
    counterfactual_fill_threshold: float = 0.5


@dataclass(frozen=True)
class ReplayInput:
    snapshot: CandidateSnapshot
    label: SettlementLabel
    particle_p_yes: float
    brownian_p_yes: float
    market_p_yes: float
    current_calibrated_p_yes: float


@dataclass(frozen=True)
class ReplayDecision:
    market_ticker: str
    decision_ts_utc: datetime
    settlement_result_yes: bool
    particle_p_yes: float
    brownian_p_yes: float
    market_p_yes: float
    current_calibrated_p_yes: float
    ev_yes_cents: float
    ev_no_cents: float
    selected: bool
    side: Side | None
    filled_counterfactual: bool
    won: bool | None
    counterfactual_pnl_cents: float
    reason: str


@dataclass(frozen=True)
class ProbabilityScorecard:
    brier: float
    log_loss: float


@dataclass(frozen=True)
class ReplayReport:
    candidate_count: int
    selected_count: int
    all_candidate_denominator: bool
    total_counterfactual_pnl_cents: float
    avg_counterfactual_pnl_cents_per_candidate: float
    avg_counterfactual_pnl_cents_per_selected: float
    particle: ProbabilityScorecard
    brownian: ProbabilityScorecard
    market: ProbabilityScorecard
    current_calibrated: ProbabilityScorecard
    particle_beats_brownian: bool
    particle_beats_market: bool
    particle_beats_current_calibrated: bool
    ev_rank_correlation_sign: float
    top_ev_bucket_pnl_cents: float
    decisions: tuple[ReplayDecision, ...]
    source_candidate_count: int | None = None
    skipped_unlabeled_count: int = 0
    denominator_scope: str = "all_labeled_candidates"

    @property
    def shadow_counterfactual_positive(self) -> bool:
        return self.total_counterfactual_pnl_cents > 0.0


@dataclass(frozen=True)
class OnlineCalibrationStep:
    market_ticker: str
    decision_ts_utc: datetime
    label_available_ts_utc: datetime
    raw_particle_p_yes: float
    online_calibrated_p_yes: float
    p_low: float
    p_high: float
    q_at_decision: float
    covered: bool


@dataclass(frozen=True)
class OnlineCalibratedReplayReport:
    candidate_count: int
    selected_count: int
    all_candidate_denominator: bool
    total_counterfactual_pnl_cents: float
    avg_counterfactual_pnl_cents_per_candidate: float
    avg_counterfactual_pnl_cents_per_selected: float
    coverage_rate: float
    final_q: float
    online_calibrated: ProbabilityScorecard
    raw_particle: ProbabilityScorecard
    brownian: ProbabilityScorecard
    market: ProbabilityScorecard
    current_calibrated: ProbabilityScorecard
    online_beats_raw_particle: bool
    online_beats_brownian: bool
    online_beats_market: bool
    online_beats_current_calibrated: bool
    ev_rank_correlation_sign: float
    top_ev_bucket_pnl_cents: float
    steps: tuple[OnlineCalibrationStep, ...]
    decisions: tuple[ReplayDecision, ...]
    source_candidate_count: int | None = None
    skipped_unlabeled_count: int = 0
    denominator_scope: str = "all_labeled_candidates"

    @property
    def shadow_counterfactual_positive(self) -> bool:
        return self.total_counterfactual_pnl_cents > 0.0


def market_probability_from_asks(snapshot: CandidateSnapshot) -> float:
    yes_bid_implied = 100.0 - snapshot.no_ask_cents
    return _clamp01(((snapshot.yes_ask_cents + yes_bid_implied) / 2.0) / 100.0)


def brownian_probability_from_snapshot(
    snapshot: CandidateSnapshot,
    *,
    settlement_ts_utc: datetime,
    annualized_vol: float,
) -> float:
    seconds_to_close = (settlement_ts_utc - snapshot.decision_ts_utc).total_seconds()
    return brownian_terminal_probability(
        snapshot.spot,
        snapshot.strike,
        seconds_to_close,
        annualized_vol,
    )


def evaluate_replay(
    rows: Sequence[ReplayInput],
    config: ReplayConfig | None = None,
) -> ReplayReport:
    cfg = config or ReplayConfig()
    if not rows:
        raise ValueError("at least one replay row is required")

    decisions: list[ReplayDecision] = []
    labels: list[int] = []
    particle_probs: list[float] = []
    brownian_probs: list[float] = []
    market_probs: list[float] = []
    current_probs: list[float] = []
    selected_ev: list[float] = []
    realized_pnl: list[float] = []

    for row in rows:
        _assert_replay_input_strict(row)
        label_yes = row.label.result_yes
        labels.append(1 if label_yes else 0)
        particle_probs.append(_clamp01(row.particle_p_yes))
        brownian_probs.append(_clamp01(row.brownian_p_yes))
        market_probs.append(_clamp01(row.market_p_yes))
        current_probs.append(_clamp01(row.current_calibrated_p_yes))

        decision = _decide(row, cfg)
        decisions.append(decision)
        selected_ev.append(max(decision.ev_yes_cents, decision.ev_no_cents))
        realized_pnl.append(decision.counterfactual_pnl_cents)

    particle = ProbabilityScorecard(brier_score(particle_probs, labels), log_loss(particle_probs, labels))
    brownian = ProbabilityScorecard(brier_score(brownian_probs, labels), log_loss(brownian_probs, labels))
    market = ProbabilityScorecard(brier_score(market_probs, labels), log_loss(market_probs, labels))
    current = ProbabilityScorecard(brier_score(current_probs, labels), log_loss(current_probs, labels))
    total_pnl = sum(realized_pnl)
    selected_count = sum(1 for d in decisions if d.selected)
    selected_pnls = [d.counterfactual_pnl_cents for d in decisions if d.selected]

    return ReplayReport(
        candidate_count=len(rows),
        selected_count=selected_count,
        all_candidate_denominator=True,
        total_counterfactual_pnl_cents=total_pnl,
        avg_counterfactual_pnl_cents_per_candidate=total_pnl / len(rows),
        avg_counterfactual_pnl_cents_per_selected=(sum(selected_pnls) / selected_count if selected_count else 0.0),
        particle=particle,
        brownian=brownian,
        market=market,
        current_calibrated=current,
        particle_beats_brownian=(
            particle.brier < brownian.brier and particle.log_loss < brownian.log_loss
        ),
        particle_beats_market=(particle.brier < market.brier and particle.log_loss < market.log_loss),
        particle_beats_current_calibrated=(
            particle.brier < current.brier and particle.log_loss < current.log_loss
        ),
        ev_rank_correlation_sign=pairwise_rank_correlation_sign(selected_ev, realized_pnl),
        top_ev_bucket_pnl_cents=top_bucket_mean_pnl(selected_ev, realized_pnl, top_fraction=0.25),
        decisions=tuple(decisions),
    )


def evaluate_online_calibrated_replay(
    rows: Sequence[ReplayInput],
    config: ReplayConfig | None = None,
    calibrator: LabelGatedACICalibrator | None = None,
) -> OnlineCalibratedReplayReport:
    cfg = config or ReplayConfig()
    cal = calibrator or LabelGatedACICalibrator()
    if not rows:
        raise ValueError("at least one replay row is required")
    sorted_rows = sorted(rows, key=lambda row: row.snapshot.decision_ts_utc)
    pending_updates: list[tuple[datetime, float, int]] = []
    labels: list[int] = []
    raw_probs: list[float] = []
    online_probs: list[float] = []
    brownian_probs: list[float] = []
    market_probs: list[float] = []
    current_probs: list[float] = []
    selected_ev: list[float] = []
    realized_pnl: list[float] = []
    steps: list[OnlineCalibrationStep] = []
    decisions: list[ReplayDecision] = []

    for row in sorted_rows:
        _assert_replay_input_strict(row)
        _apply_available_updates(pending_updates, row.snapshot.decision_ts_utc, cal)
        raw_p = _clamp01(row.particle_p_yes)
        q_at_decision = cal.q
        online_p, (p_low, p_high) = cal.predict(raw_p)
        label_int = 1 if row.label.result_yes else 0
        labels.append(label_int)
        raw_probs.append(raw_p)
        online_probs.append(_clamp01(online_p))
        brownian_probs.append(_clamp01(row.brownian_p_yes))
        market_probs.append(_clamp01(row.market_p_yes))
        current_probs.append(_clamp01(row.current_calibrated_p_yes))
        step = OnlineCalibrationStep(
            market_ticker=row.snapshot.market_ticker,
            decision_ts_utc=row.snapshot.decision_ts_utc,
            label_available_ts_utc=row.label.label_available_ts_utc,
            raw_particle_p_yes=raw_p,
            online_calibrated_p_yes=_clamp01(online_p),
            p_low=p_low,
            p_high=p_high,
            q_at_decision=q_at_decision,
            covered=p_low <= label_int <= p_high,
        )
        steps.append(step)
        calibrated_row = ReplayInput(
            snapshot=row.snapshot,
            label=row.label,
            particle_p_yes=_clamp01(online_p),
            brownian_p_yes=row.brownian_p_yes,
            market_p_yes=row.market_p_yes,
            current_calibrated_p_yes=row.current_calibrated_p_yes,
        )
        decision = _decide(calibrated_row, cfg)
        decisions.append(decision)
        selected_ev.append(max(decision.ev_yes_cents, decision.ev_no_cents))
        realized_pnl.append(decision.counterfactual_pnl_cents)
        pending_updates.append((row.label.label_available_ts_utc, raw_p, label_int))

    _apply_available_updates(pending_updates, datetime.max.replace(tzinfo=timezone.utc), cal)
    online = ProbabilityScorecard(brier_score(online_probs, labels), log_loss(online_probs, labels))
    raw = ProbabilityScorecard(brier_score(raw_probs, labels), log_loss(raw_probs, labels))
    brownian = ProbabilityScorecard(brier_score(brownian_probs, labels), log_loss(brownian_probs, labels))
    market = ProbabilityScorecard(brier_score(market_probs, labels), log_loss(market_probs, labels))
    current = ProbabilityScorecard(brier_score(current_probs, labels), log_loss(current_probs, labels))
    total_pnl = sum(realized_pnl)
    selected_count = sum(1 for decision in decisions if decision.selected)
    selected_pnls = [decision.counterfactual_pnl_cents for decision in decisions if decision.selected]
    coverage_rate = sum(1 for step in steps if step.covered) / len(steps)
    return OnlineCalibratedReplayReport(
        candidate_count=len(sorted_rows),
        selected_count=selected_count,
        all_candidate_denominator=True,
        total_counterfactual_pnl_cents=total_pnl,
        avg_counterfactual_pnl_cents_per_candidate=total_pnl / len(sorted_rows),
        avg_counterfactual_pnl_cents_per_selected=(sum(selected_pnls) / selected_count if selected_count else 0.0),
        coverage_rate=coverage_rate,
        final_q=cal.q,
        online_calibrated=online,
        raw_particle=raw,
        brownian=brownian,
        market=market,
        current_calibrated=current,
        online_beats_raw_particle=(online.brier < raw.brier and online.log_loss < raw.log_loss),
        online_beats_brownian=(online.brier < brownian.brier and online.log_loss < brownian.log_loss),
        online_beats_market=(online.brier < market.brier and online.log_loss < market.log_loss),
        online_beats_current_calibrated=(online.brier < current.brier and online.log_loss < current.log_loss),
        ev_rank_correlation_sign=pairwise_rank_correlation_sign(selected_ev, realized_pnl),
        top_ev_bucket_pnl_cents=top_bucket_mean_pnl(selected_ev, realized_pnl, top_fraction=0.25),
        steps=tuple(steps),
        decisions=tuple(decisions),
    )


def load_replay_inputs_from_jsonl(
    candidate_path: Path,
    label_path: Path,
    *,
    default_annualized_vol: float | None = None,
    allow_missing_labels: bool = False,
) -> list[ReplayInput]:
    labels = {
        label.market_ticker: label for label in load_settlement_labels_jsonl(label_path)
    }
    rows: list[ReplayInput] = []
    for payload in _read_jsonl(candidate_path):
        snapshot, extra = _parse_candidate_payload(payload)
        if snapshot.market_ticker not in labels:
            if allow_missing_labels:
                continue
            raise ValueError(f"missing settlement label for {snapshot.market_ticker}")
        label = labels[snapshot.market_ticker]
        particle_p_yes = _require_probability(extra, "particle_p_yes")
        current_p_yes = float(extra.get("current_calibrated_p_yes", particle_p_yes))
        brownian_p_yes = extra.get("brownian_p_yes")
        if brownian_p_yes is None:
            if default_annualized_vol is None:
                raise ValueError("brownian_p_yes missing and no default_annualized_vol supplied")
            brownian_p_yes = brownian_probability_from_snapshot(
                snapshot,
                settlement_ts_utc=label.settlement_ts_utc,
                annualized_vol=default_annualized_vol,
            )
        market_p_yes = float(extra.get("market_p_yes", market_probability_from_asks(snapshot)))
        rows.append(
            ReplayInput(
                snapshot=snapshot,
                label=label,
                particle_p_yes=float(particle_p_yes),
                brownian_p_yes=float(brownian_p_yes),
                market_p_yes=market_p_yes,
                current_calibrated_p_yes=current_p_yes,
            )
        )
    return rows


def load_settlement_labels_jsonl(path: Path) -> list[SettlementLabel]:
    labels: list[SettlementLabel] = []
    for payload in _read_jsonl(path):
        raw = payload.get("label", payload)
        labels.append(
            SettlementLabel(
                market_ticker=str(raw["market_ticker"]),
                settlement_ts_utc=_parse_dt(raw["settlement_ts_utc"]),
                label_available_ts_utc=_parse_dt(raw["label_available_ts_utc"]),
                settlement_price=float(raw["settlement_price"]),
                strike=float(raw["strike"]),
            )
        )
    return labels


def report_to_dict(report: ReplayReport, *, include_decisions: bool = True) -> dict[str, Any]:
    payload = asdict(report)
    if not include_decisions:
        payload.pop("decisions", None)
    return payload


def write_replay_report(report: ReplayReport, output_dir: Path, stem: str) -> tuple[Path, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    json_path = output_dir / f"{stem}.json"
    md_path = output_dir / f"{stem}.md"
    json_path.write_text(
        json.dumps(report_to_dict(report), default=_json_default, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    md_path.write_text(_report_markdown(report), encoding="utf-8")
    return json_path, md_path


def write_online_replay_report(
    report: OnlineCalibratedReplayReport,
    output_dir: Path,
    stem: str,
) -> tuple[Path, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    json_path = output_dir / f"{stem}.json"
    md_path = output_dir / f"{stem}.md"
    json_path.write_text(
        json.dumps(asdict(report), default=_json_default, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    md_path.write_text(_online_report_markdown(report), encoding="utf-8")
    return json_path, md_path


def _decide(row: ReplayInput, cfg: ReplayConfig) -> ReplayDecision:
    snapshot = row.snapshot
    p_yes = _clamp01(row.particle_p_yes)
    ev_yes = expected_pnl_cents(
        p_win=p_yes,
        ask_cents=snapshot.yes_ask_cents,
        fee_if_win_cents=snapshot.fee_cents,
        fill_prob=_fill_prob_for(snapshot, "yes"),
        no_fill_penalty_cents=cfg.no_fill_penalty_cents,
    )
    ev_no = expected_pnl_cents(
        p_win=1.0 - p_yes,
        ask_cents=snapshot.no_ask_cents,
        fee_if_win_cents=snapshot.fee_cents,
        fill_prob=_fill_prob_for(snapshot, "no"),
        no_fill_penalty_cents=cfg.no_fill_penalty_cents,
    )
    side: Side = "yes" if ev_yes >= ev_no else "no"
    best_ev = max(ev_yes, ev_no)
    selected_fill_prob = _fill_prob_for(snapshot, side)
    if selected_fill_prob < cfg.min_fill_prob:
        return _no_trade(row, ev_yes, ev_no, "below_min_fill")
    if best_ev < cfg.min_ev_cents:
        return _no_trade(row, ev_yes, ev_no, "below_min_ev")

    filled = _counterfactual_filled(selected_fill_prob, cfg)
    won = row.label.result_yes if side == "yes" else not row.label.result_yes
    if filled:
        ask_cents = snapshot.yes_ask_cents if side == "yes" else snapshot.no_ask_cents
        pnl = 100.0 - ask_cents - snapshot.fee_cents if won else -ask_cents
    else:
        pnl = -cfg.no_fill_penalty_cents
    return ReplayDecision(
        market_ticker=snapshot.market_ticker,
        decision_ts_utc=snapshot.decision_ts_utc,
        settlement_result_yes=row.label.result_yes,
        particle_p_yes=p_yes,
        brownian_p_yes=_clamp01(row.brownian_p_yes),
        market_p_yes=_clamp01(row.market_p_yes),
        current_calibrated_p_yes=_clamp01(row.current_calibrated_p_yes),
        ev_yes_cents=ev_yes,
        ev_no_cents=ev_no,
        selected=True,
        side=side,
        filled_counterfactual=filled,
        won=won,
        counterfactual_pnl_cents=pnl,
        reason="selected",
    )


def _no_trade(row: ReplayInput, ev_yes: float, ev_no: float, reason: str) -> ReplayDecision:
    snapshot = row.snapshot
    return ReplayDecision(
        market_ticker=snapshot.market_ticker,
        decision_ts_utc=snapshot.decision_ts_utc,
        settlement_result_yes=row.label.result_yes,
        particle_p_yes=_clamp01(row.particle_p_yes),
        brownian_p_yes=_clamp01(row.brownian_p_yes),
        market_p_yes=_clamp01(row.market_p_yes),
        current_calibrated_p_yes=_clamp01(row.current_calibrated_p_yes),
        ev_yes_cents=ev_yes,
        ev_no_cents=ev_no,
        selected=False,
        side=None,
        filled_counterfactual=False,
        won=None,
        counterfactual_pnl_cents=0.0,
        reason=reason,
    )


def _counterfactual_filled(fill_prob: float, cfg: ReplayConfig) -> bool:
    if cfg.counterfactual_fill_policy == "always_fill":
        return True
    if cfg.counterfactual_fill_policy == "never_fill":
        return False
    return fill_prob >= cfg.counterfactual_fill_threshold


def _assert_replay_input_strict(row: ReplayInput) -> None:
    snapshot = row.snapshot
    label = row.label
    if snapshot.market_ticker != label.market_ticker:
        raise ValueError("snapshot and label market_ticker differ")
    if snapshot.recv_ts_utc > snapshot.decision_ts_utc:
        raise FutureDataLeakageError(
            f"{snapshot.market_ticker} snapshot received after decision timestamp"
        )
    if label.label_available_ts_utc <= snapshot.decision_ts_utc:
        raise FutureDataLeakageError(
            f"{snapshot.market_ticker} settlement label was available at decision timestamp"
        )
    for name, prob in (
        ("particle_p_yes", row.particle_p_yes),
        ("brownian_p_yes", row.brownian_p_yes),
        ("market_p_yes", row.market_p_yes),
        ("current_calibrated_p_yes", row.current_calibrated_p_yes),
    ):
        if not 0.0 <= prob <= 1.0:
            raise ValueError(f"{name} must be in [0, 1]")


def _parse_candidate_payload(payload: Mapping[str, Any]) -> tuple[CandidateSnapshot, Mapping[str, Any]]:
    raw = payload.get("snapshot", payload)
    extra = payload.get("extra", {})
    snapshot = CandidateSnapshot(
        market_ticker=str(raw["market_ticker"]),
        decision_ts_utc=_parse_dt(raw["decision_ts_utc"]),
        recv_ts_utc=_parse_dt(raw["recv_ts_utc"]),
        strike=float(raw["strike"]),
        spot=float(raw["spot"]),
        yes_ask_cents=float(raw["yes_ask_cents"]),
        no_ask_cents=float(raw["no_ask_cents"]),
        fee_cents=float(raw["fee_cents"]),
        fill_prob=float(raw["fill_prob"]),
        yes_fill_prob=_optional_float(raw, "yes_fill_prob"),
        no_fill_prob=_optional_float(raw, "no_fill_prob"),
    )
    return snapshot, extra


def _require_probability(extra: Mapping[str, Any], name: str) -> float:
    if name not in extra:
        raise ValueError(f"candidate extra is missing required {name}")
    value = float(extra[name])
    if not 0.0 <= value <= 1.0:
        raise ValueError(f"{name} must be in [0, 1]")
    return value


def _read_jsonl(path: Path) -> Iterable[Mapping[str, Any]]:
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if line:
                yield json.loads(line)


def _parse_dt(value: str | datetime) -> datetime:
    if isinstance(value, datetime):
        return value
    parsed = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def _clamp01(value: float) -> float:
    return min(1.0, max(0.0, float(value)))


def _fill_prob_for(snapshot: CandidateSnapshot, side: Side) -> float:
    if side == "yes" and snapshot.yes_fill_prob is not None:
        return snapshot.yes_fill_prob
    if side == "no" and snapshot.no_fill_prob is not None:
        return snapshot.no_fill_prob
    return snapshot.fill_prob


def _optional_float(raw: Mapping[str, Any], name: str) -> float | None:
    if name not in raw or raw[name] in (None, ""):
        return None
    return float(raw[name])


def _json_default(value: Any) -> Any:
    if isinstance(value, datetime):
        return value.isoformat()
    raise TypeError(f"Object of type {type(value).__name__} is not JSON serializable")


def _apply_available_updates(
    pending_updates: list[tuple[datetime, float, int]],
    as_of_ts_utc: datetime,
    calibrator: LabelGatedACICalibrator,
) -> None:
    ready = [
        update for update in pending_updates
        if update[0] <= as_of_ts_utc
    ]
    if not ready:
        return
    ready.sort(key=lambda update: update[0])
    remaining = [
        update for update in pending_updates
        if update[0] > as_of_ts_utc
    ]
    pending_updates.clear()
    pending_updates.extend(remaining)
    for _, p_raw, label in ready:
        calibrator.update_with_label(p_raw, label)


def _report_markdown(report: ReplayReport) -> str:
    return "\n".join(
        [
            "# Particle Replay Report",
            "",
            f"- candidate_count: {report.candidate_count}",
            f"- source_candidate_count: {report.source_candidate_count if report.source_candidate_count is not None else report.candidate_count}",
            f"- skipped_unlabeled_count: {report.skipped_unlabeled_count}",
            f"- denominator_scope: {report.denominator_scope}",
            f"- selected_count: {report.selected_count}",
            f"- all_candidate_denominator: {report.all_candidate_denominator}",
            f"- total_counterfactual_pnl_cents: {report.total_counterfactual_pnl_cents:.4f}",
            f"- avg_selected_pnl_cents: {report.avg_counterfactual_pnl_cents_per_selected:.4f}",
            f"- particle_brier: {report.particle.brier:.6f}",
            f"- brownian_brier: {report.brownian.brier:.6f}",
            f"- market_brier: {report.market.brier:.6f}",
            f"- current_calibrated_brier: {report.current_calibrated.brier:.6f}",
            f"- particle_log_loss: {report.particle.log_loss:.6f}",
            f"- brownian_log_loss: {report.brownian.log_loss:.6f}",
            f"- market_log_loss: {report.market.log_loss:.6f}",
            f"- current_calibrated_log_loss: {report.current_calibrated.log_loss:.6f}",
            f"- particle_beats_brownian: {report.particle_beats_brownian}",
            f"- particle_beats_market: {report.particle_beats_market}",
            f"- particle_beats_current_calibrated: {report.particle_beats_current_calibrated}",
            f"- ev_rank_correlation_sign: {report.ev_rank_correlation_sign:.6f}",
            f"- top_ev_bucket_pnl_cents: {report.top_ev_bucket_pnl_cents:.4f}",
            f"- shadow_counterfactual_positive: {report.shadow_counterfactual_positive}",
            "",
        ]
    )


def _online_report_markdown(report: OnlineCalibratedReplayReport) -> str:
    return "\n".join(
        [
            "# Online Calibrated Particle Replay Report",
            "",
            f"- candidate_count: {report.candidate_count}",
            f"- source_candidate_count: {report.source_candidate_count if report.source_candidate_count is not None else report.candidate_count}",
            f"- skipped_unlabeled_count: {report.skipped_unlabeled_count}",
            f"- denominator_scope: {report.denominator_scope}",
            f"- selected_count: {report.selected_count}",
            f"- all_candidate_denominator: {report.all_candidate_denominator}",
            f"- coverage_rate: {report.coverage_rate:.6f}",
            f"- final_q: {report.final_q:.6f}",
            f"- total_counterfactual_pnl_cents: {report.total_counterfactual_pnl_cents:.4f}",
            f"- avg_selected_pnl_cents: {report.avg_counterfactual_pnl_cents_per_selected:.4f}",
            f"- online_brier: {report.online_calibrated.brier:.6f}",
            f"- raw_particle_brier: {report.raw_particle.brier:.6f}",
            f"- brownian_brier: {report.brownian.brier:.6f}",
            f"- market_brier: {report.market.brier:.6f}",
            f"- current_calibrated_brier: {report.current_calibrated.brier:.6f}",
            f"- online_log_loss: {report.online_calibrated.log_loss:.6f}",
            f"- raw_particle_log_loss: {report.raw_particle.log_loss:.6f}",
            f"- brownian_log_loss: {report.brownian.log_loss:.6f}",
            f"- market_log_loss: {report.market.log_loss:.6f}",
            f"- current_calibrated_log_loss: {report.current_calibrated.log_loss:.6f}",
            f"- online_beats_raw_particle: {report.online_beats_raw_particle}",
            f"- online_beats_brownian: {report.online_beats_brownian}",
            f"- online_beats_market: {report.online_beats_market}",
            f"- online_beats_current_calibrated: {report.online_beats_current_calibrated}",
            f"- ev_rank_correlation_sign: {report.ev_rank_correlation_sign:.6f}",
            f"- top_ev_bucket_pnl_cents: {report.top_ev_bucket_pnl_cents:.4f}",
            f"- shadow_counterfactual_positive: {report.shadow_counterfactual_positive}",
            "",
        ]
    )
