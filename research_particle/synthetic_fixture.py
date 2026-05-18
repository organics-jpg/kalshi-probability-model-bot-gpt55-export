from __future__ import annotations

import argparse
from datetime import datetime, timedelta, timezone
from pathlib import Path

from .recorders import CandidateSnapshotRecorder, SettlementLabelRecorder
from .replay_runner import ReplayConfig, evaluate_replay, load_replay_inputs_from_jsonl, write_replay_report
from .schemas import CandidateSnapshot, SettlementLabel


def build_synthetic_fixture(root: Path) -> tuple[Path, Path]:
    candidate_path = root / "candidate_snapshots" / "candidate_snapshots.ndjson"
    label_path = root / "settlement_labels" / "settlement_labels.ndjson"
    if candidate_path.exists() or label_path.exists():
        raise FileExistsError(
            f"synthetic fixture already exists under {root}; choose a fresh --root"
        )
    decision = datetime(2026, 5, 10, 12, 0, tzinfo=timezone.utc)
    rows = [
        ("KXBTC15M-SYN1", 100.0, 101.0, 60.0, 42.0, 0.85, 0.60, 0.55, 0.65, 101.2),
        ("KXBTC15M-SYN2", 100.0, 100.7, 65.0, 37.0, 0.75, 0.55, 0.52, 0.60, 100.4),
        ("KXBTC15M-SYN3", 100.0, 99.4, 38.0, 60.0, 0.25, 0.45, 0.48, 0.40, 99.0),
        ("KXBTC15M-SYN4", 100.0, 98.9, 30.0, 70.0, 0.15, 0.40, 0.45, 0.35, 99.6),
    ]
    candidate_recorder = CandidateSnapshotRecorder(root)
    label_recorder = SettlementLabelRecorder(root)
    for idx, (
        ticker,
        strike,
        spot,
        yes_ask,
        no_ask,
        particle_p,
        brownian_p,
        market_p,
        current_p,
        settlement,
    ) in enumerate(rows):
        snapshot = CandidateSnapshot(
            market_ticker=ticker,
            decision_ts_utc=decision + timedelta(seconds=idx),
            recv_ts_utc=decision + timedelta(seconds=idx),
            strike=strike,
            spot=spot,
            yes_ask_cents=yes_ask,
            no_ask_cents=no_ask,
            fee_cents=1.0,
            fill_prob=1.0,
        )
        label = SettlementLabel(
            market_ticker=ticker,
            settlement_ts_utc=decision + timedelta(minutes=15),
            label_available_ts_utc=decision + timedelta(minutes=16),
            settlement_price=settlement,
            strike=strike,
        )
        candidate_recorder.record(
            snapshot,
            decision_shadow="candidate",
            reason="synthetic_end_to_end",
            extra={
                "particle_p_yes": particle_p,
                "brownian_p_yes": brownian_p,
                "market_p_yes": market_p,
                "current_calibrated_p_yes": current_p,
            },
        )
        label_recorder.record(label, source="synthetic")
    return candidate_path, label_path


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Create and replay a durable synthetic particle fixture."
    )
    parser.add_argument(
        "--root",
        default=Path("logs") / "particle_research" / "synthetic_fixture",
        type=Path,
        help="fixture root directory",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    candidates, labels = build_synthetic_fixture(args.root)
    rows = load_replay_inputs_from_jsonl(candidates, labels)
    report = evaluate_replay(
        rows,
        ReplayConfig(
            min_ev_cents=1.0,
            min_fill_prob=0.5,
            counterfactual_fill_policy="threshold",
            counterfactual_fill_threshold=0.5,
        ),
    )
    json_path, md_path = write_replay_report(report, args.root / "reports", "synthetic_replay")
    print(f"candidates={candidates}")
    print(f"labels={labels}")
    print(f"json_report={json_path}")
    print(f"md_report={md_path}")
    print(f"candidate_count={report.candidate_count}")
    print(f"selected_count={report.selected_count}")
    print(f"total_counterfactual_pnl_cents={report.total_counterfactual_pnl_cents:.4f}")
    print(f"particle_beats_all_baselines={report.particle_beats_brownian and report.particle_beats_market and report.particle_beats_current_calibrated}")
    print(f"shadow_counterfactual_positive={report.shadow_counterfactual_positive}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
