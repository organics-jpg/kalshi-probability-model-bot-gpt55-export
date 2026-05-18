from __future__ import annotations

import json
from dataclasses import asdict, is_dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

from .schemas import CandidateSnapshot, SettlementLabel


SCHEMA_VERSION = 1
DEFAULT_ROOT = Path("logs") / "particle_research"


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _json_default(value: Any) -> Any:
    if isinstance(value, datetime):
        return value.isoformat()
    if is_dataclass(value):
        return asdict(value)
    raise TypeError(f"Object of type {type(value).__name__} is not JSON serializable")


def append_jsonl(path: Path, row: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(row, default=_json_default, sort_keys=True) + "\n")


class CandidateSnapshotRecorder:
    """Append-only all-candidate snapshot writer.

    Callers are expected to record every candidate moment, including skipped,
    rejected, no-fill, and traded decisions. This writer intentionally has no
    order placement ability.
    """

    def __init__(self, root: Path = DEFAULT_ROOT) -> None:
        self.path = root / "candidate_snapshots" / "candidate_snapshots.ndjson"

    def record(
        self,
        snapshot: CandidateSnapshot,
        decision_shadow: str,
        reason: str,
        extra: Mapping[str, Any] | None = None,
    ) -> None:
        row: dict[str, Any] = {
            "schema_version": SCHEMA_VERSION,
            "recorded_ts_utc": utc_now_iso(),
            "record_type": "candidate_snapshot",
            "snapshot": snapshot,
            "decision_shadow": decision_shadow,
            "reason": reason,
        }
        if extra:
            row["extra"] = dict(extra)
        append_jsonl(self.path, row)


class SettlementLabelRecorder:
    def __init__(self, root: Path = DEFAULT_ROOT) -> None:
        self.path = root / "settlement_labels" / "settlement_labels.ndjson"

    def record(self, label: SettlementLabel, source: str) -> None:
        append_jsonl(
            self.path,
            {
                "schema_version": SCHEMA_VERSION,
                "recorded_ts_utc": utc_now_iso(),
                "record_type": "settlement_label",
                "label": label,
                "source": source,
                "result_yes": label.result_yes,
            },
        )

