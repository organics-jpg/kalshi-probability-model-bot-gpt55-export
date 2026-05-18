from __future__ import annotations

from datetime import datetime
from typing import Iterable

from .schemas import TimedRecord


class FutureDataLeakageError(ValueError):
    pass


def assert_records_available_at_decision(
    records: Iterable[TimedRecord],
    decision_ts_utc: datetime,
) -> None:
    leaked = [record for record in records if record.recv_ts_utc > decision_ts_utc]
    if leaked:
        names = ", ".join(record.name for record in leaked[:5])
        raise FutureDataLeakageError(
            f"{len(leaked)} record(s) were unavailable at decision time: {names}"
        )


def available_records(
    records: Iterable[TimedRecord],
    decision_ts_utc: datetime,
) -> list[TimedRecord]:
    available = [record for record in records if record.recv_ts_utc <= decision_ts_utc]
    assert_records_available_at_decision(available, decision_ts_utc)
    return available

