"""Shared strict freshness boundary helpers for profit-lock probes.

Locks are often created while the next 15-minute market is already open. A
post-lock validation must not count a row whose entry timestamp happened before
the lock existed, even if the market settled later. The effective boundary is
therefore the later of the stored lock close time and the next full 15-minute
close after the lock's creation timestamp.
"""
from __future__ import annotations

from typing import Any, Dict

import pandas as pd


def next_full_15m_close(ts: Any) -> pd.Timestamp:
    dt = pd.to_datetime(ts, utc=True, errors="coerce")
    if pd.isna(dt):
        return pd.NaT
    return dt.floor("15min") + pd.Timedelta(minutes=15)


def effective_lock_dt(lock: Dict[str, Any]) -> pd.Timestamp:
    lock_close = pd.to_datetime(lock.get("lock_close_dt"), utc=True, errors="coerce")
    created = pd.to_datetime(lock.get("created_utc"), utc=True, errors="coerce")
    if pd.isna(created):
        return lock_close
    created_boundary = next_full_15m_close(created)
    if pd.isna(lock_close):
        return created_boundary
    if pd.isna(created_boundary):
        return lock_close
    return max(lock_close, created_boundary)
