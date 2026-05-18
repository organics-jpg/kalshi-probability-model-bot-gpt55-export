from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable, Mapping

from .particle_engine import NextSecondParticleEngine, ParticleEngineConfig
from .recorders import SettlementLabelRecorder
from .schemas import SettlementLabel
from .shadow_adapter import ShadowCandidateAdapter, snapshot_from_shadow_context


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Research-only collection of particle shadow candidate/label JSONL contexts."
    )
    sub = parser.add_subparsers(dest="command", required=True)

    candidates = sub.add_parser("candidates", help="record candidate contexts")
    candidates.add_argument("--input", required=True, type=Path, help="input JSONL candidate contexts")
    candidates.add_argument(
        "--root",
        default=Path("logs") / "particle_research" / "shadow_collection",
        type=Path,
        help="particle research artifact root",
    )
    candidates.add_argument("--decision-shadow", default="candidate")
    candidates.add_argument("--reason", default="shadow_collect")
    candidates.add_argument("--annualized-vol", default=None, type=float)
    candidates.add_argument("--sample-count", default=2000, type=int)
    candidates.add_argument("--seed", default=0, type=int)

    labels = sub.add_parser("labels", help="record settlement label contexts")
    labels.add_argument("--input", required=True, type=Path, help="input JSONL settlement label contexts")
    labels.add_argument(
        "--root",
        default=Path("logs") / "particle_research" / "shadow_collection",
        type=Path,
        help="particle research artifact root",
    )
    labels.add_argument("--source", default="shadow_collect")

    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.command == "candidates":
        return record_candidates(args)
    if args.command == "labels":
        return record_labels(args)
    raise ValueError(f"unknown command {args.command}")


def record_candidates(args: argparse.Namespace) -> int:
    adapter = ShadowCandidateAdapter(args.root)
    engine = (
        NextSecondParticleEngine(
            ParticleEngineConfig(
                annualized_vol=args.annualized_vol,
                sample_count=args.sample_count,
                seed=args.seed,
            )
        )
        if args.annualized_vol is not None
        else None
    )
    count = 0
    for context in _read_jsonl(args.input):
        if engine is not None:
            snapshot = snapshot_from_shadow_context(context)
            settlement_ts = _parse_dt_required(context, "settlement_ts_utc")
            prediction = engine.predict(snapshot, settlement_ts_utc=settlement_ts)
            current_baseline = context.get("current_calibrated_p_yes")
            context = dict(context)
            context.update(prediction.as_shadow_extra(current_baseline))
        adapter.record_context(context, decision_shadow=args.decision_shadow, reason=args.reason)
        count += 1
    print(f"recorded_candidates={count}")
    print(f"root={args.root}")
    return 0


def record_labels(args: argparse.Namespace) -> int:
    recorder = SettlementLabelRecorder(args.root)
    count = 0
    for context in _read_jsonl(args.input):
        label = SettlementLabel(
            market_ticker=str(context["market_ticker"]),
            settlement_ts_utc=_parse_dt_required(context, "settlement_ts_utc"),
            label_available_ts_utc=_parse_dt_required(context, "label_available_ts_utc"),
            settlement_price=float(context["settlement_price"]),
            strike=float(context["strike"]),
        )
        recorder.record(label, source=args.source)
        count += 1
    print(f"recorded_labels={count}")
    print(f"root={args.root}")
    return 0


def _read_jsonl(path: Path) -> Iterable[Mapping[str, Any]]:
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if line:
                yield json.loads(line)


def _parse_dt_required(context: Mapping[str, Any], key: str) -> datetime:
    if key not in context:
        raise ValueError(f"missing required {key}")
    value = context[key]
    if isinstance(value, datetime):
        dt = value
    else:
        dt = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


if __name__ == "__main__":
    raise SystemExit(main())
