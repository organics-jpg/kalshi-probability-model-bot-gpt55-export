"""Forward shadow monitor for v28 entry-skip guard hypotheses.

The live v28 bot remains untouched. This monitor records future live v28 fills
that a candidate guard would have skipped, then scores the counterfactual:
skipping earns $0, so positive skip delta means avoiding the live fill would
have improved P&L.
"""
from __future__ import annotations

import csv
import json
import math
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

import pandas as pd


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
LOCK_PATH = OUT_DIR / "live_v28_entry_guard_shadow_locks.json"
REGISTRY_PATH = OUT_DIR / "live_v28_entry_guard_shadow_registry_latest.csv"
REPORT_LATEST = OUT_DIR / "live_v28_entry_guard_shadow_monitor_latest.md"
JSON_LATEST = OUT_DIR / "live_v28_entry_guard_shadow_monitor_latest.json"
SOURCE_ROWS_PATH = OUT_DIR / "live_v28_current_bot_loss_guard_rows_latest.csv"
LOSS_GUARD_JSON = OUT_DIR / "live_v28_current_bot_loss_guard_latest.json"
LOCAL_TZ = ZoneInfo("America/New_York")

REGISTRY_COLS = [
    "lock_name",
    "rule_label",
    "registered_utc",
    "entry_dt",
    "market",
    "side",
    "qty",
    "entry_fill_cents",
    "p_side",
    "edge_cents",
    "ask_cents",
    "fair_side_cents",
    "seconds_to_close",
    "d_sigma",
    "abs_d_sigma",
    "sigma_t_dollars",
    "btc_age_ms",
    "eligible_depth",
    "book_age_ms",
    "outcome_available",
    "outcome",
    "actual_net_pnl_dollars",
    "skip_delta_dollars",
]


def as_float(value: Any) -> float | None:
    if value is None or value == "":
        return None
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    if math.isnan(number) or math.isinf(number):
        return None
    return number


def as_bool(value: Any) -> bool:
    return str(value).lower() in {"true", "1", "yes"}


def next_full_15m_close(value: Any) -> pd.Timestamp:
    ts = pd.to_datetime(value, utc=True, errors="coerce")
    if pd.isna(ts):
        return pd.NaT
    return ts.floor("15min") + pd.Timedelta(minutes=15)


def local_to_utc(value: Any) -> pd.Timestamp:
    ts = pd.to_datetime(value, errors="coerce")
    if pd.isna(ts):
        return pd.NaT
    if ts.tzinfo is None:
        ts = ts.tz_localize(LOCAL_TZ, nonexistent="shift_forward", ambiguous="NaT")
    return ts.tz_convert("UTC")


def load_loss_guard_diagnostic() -> dict[str, Any]:
    if not LOSS_GUARD_JSON.exists():
        return {}
    try:
        payload = json.loads(LOSS_GUARD_JSON.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
    top_candidates = payload.get("top_candidates") or []
    by_guard = {row.get("guard"): row for row in top_candidates}
    return {
        "source": "live_v28_current_bot_loss_guard_latest",
        "matched_trades": payload.get("matched_trades"),
        "current_v28_filled_markets": payload.get("current_v28_filled_markets"),
        "observed_resolved_recurring_markets": payload.get("observed_resolved_recurring_markets"),
        "current_v28_recurring_market_coverage": payload.get("current_v28_recurring_market_coverage"),
        "btc_age_ms<=600": by_guard.get("btc_age_ms<=600"),
        "edge_cents>=2.1 AND eligible_depth<=1300": by_guard.get("edge_cents>=2.1 AND eligible_depth<=1300"),
        "selection_warning": (
            "Research-only forward shadow. These guards improve the current v28 filled-entry stream, "
            "but the live v28 bot itself is far below the broad 80% recurring-market coverage target."
        ),
    }


def ensure_lock() -> dict[str, Any]:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    if LOCK_PATH.exists():
        return json.loads(LOCK_PATH.read_text(encoding="utf-8"))
    created = datetime.now(timezone.utc)
    lock = {
        "created_utc": created.isoformat(),
        "lock_close_dt": next_full_15m_close(created).isoformat(),
        "lock_name": "live_v28_entry_guard_shadow",
        "rules": [
            {
                "label": "skip_if_btc_age_ms_gt_600",
                "type": "btc_age_gt",
                "threshold": 600.0,
                "research_note": "Clean physics cue: do not trust an entry snapshot whose BTC spot tick is stale.",
            },
            {
                "label": "skip_if_edge_lt_2p1_or_eligible_depth_gt_1300",
                "type": "top_retrospective_guard_fail",
                "edge_min": 2.1,
                "eligible_depth_max": 1300.0,
                "research_note": "Higher retrospective P&L cue; more suspicious because depth can be a crowded-book artifact.",
            },
        ],
        "diagnostic_metrics": load_loss_guard_diagnostic(),
    }
    LOCK_PATH.write_text(json.dumps(lock, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return lock


def effective_lock_dt(lock: dict[str, Any]) -> pd.Timestamp:
    lock_close = pd.to_datetime(lock.get("lock_close_dt"), utc=True, errors="coerce")
    created = pd.to_datetime(lock.get("created_utc"), utc=True, errors="coerce")
    created_boundary = next_full_15m_close(created)
    if pd.isna(lock_close):
        return created_boundary
    if pd.isna(created_boundary):
        return lock_close
    return max(lock_close, created_boundary)


def load_source_rows() -> pd.DataFrame:
    if not SOURCE_ROWS_PATH.exists():
        raise SystemExit(f"Missing current-bot loss guard rows: {SOURCE_ROWS_PATH}")
    rows = pd.read_csv(SOURCE_ROWS_PATH)
    if rows.empty:
        return rows
    if "entry_dt_utc" in rows.columns:
        rows["entry_dt"] = pd.to_datetime(rows["entry_dt_utc"], utc=True, errors="coerce")
    else:
        rows["entry_dt"] = rows["entry_ts"].map(local_to_utc)
    for col in [
        "qty",
        "entry_fill_cents_used",
        "p_side",
        "edge_cents",
        "ask_cents",
        "fair_side_cents",
        "seconds_to_close",
        "d_sigma",
        "abs_d_sigma",
        "sigma_t_dollars",
        "btc_age_ms",
        "eligible_depth",
        "book_age_ms",
        "net_pnl_dollars",
    ]:
        rows[col] = pd.to_numeric(rows.get(col), errors="coerce")
    return rows.sort_values(["entry_dt", "market", "side"]).reset_index(drop=True)


def load_registry() -> pd.DataFrame:
    if not REGISTRY_PATH.exists():
        return pd.DataFrame(columns=REGISTRY_COLS)
    rows = pd.read_csv(REGISTRY_PATH)
    for col in REGISTRY_COLS:
        if col not in rows.columns:
            rows[col] = None
    return rows[REGISTRY_COLS].copy()


def rule_mask(rows: pd.DataFrame, rule: dict[str, Any]) -> pd.Series:
    rule_type = str(rule.get("type") or "")
    if rule_type == "btc_age_gt":
        threshold = float(rule.get("threshold", 600.0))
        return pd.to_numeric(rows["btc_age_ms"], errors="coerce").gt(threshold).fillna(False)
    if rule_type == "top_retrospective_guard_fail":
        edge_min = float(rule.get("edge_min", 2.1))
        depth_max = float(rule.get("eligible_depth_max", 1300.0))
        edge = pd.to_numeric(rows["edge_cents"], errors="coerce")
        depth = pd.to_numeric(rows["eligible_depth"], errors="coerce")
        return edge.lt(edge_min).fillna(False) | depth.gt(depth_max).fillna(False)
    raise ValueError(f"unsupported entry guard rule: {rule_type}")


def registry_key(row: pd.Series, rule_label: str) -> tuple[str, str, str, str]:
    return (
        rule_label,
        pd.to_datetime(row.get("entry_dt"), utc=True, errors="coerce").isoformat(),
        str(row.get("market") or ""),
        str(row.get("side") or ""),
    )


def outcome_available(row: pd.Series) -> bool:
    outcome = str(row.get("outcome") or "").lower()
    if outcome == "open":
        return False
    return as_float(row.get("net_pnl_dollars")) is not None


def record_from_source(row: pd.Series, rule_label: str, registered_utc: str) -> dict[str, Any]:
    net = as_float(row.get("net_pnl_dollars"))
    available = outcome_available(row)
    return {
        "lock_name": "live_v28_entry_guard_shadow",
        "rule_label": rule_label,
        "registered_utc": registered_utc,
        "entry_dt": pd.to_datetime(row.get("entry_dt"), utc=True, errors="coerce").isoformat(),
        "market": row.get("market"),
        "side": row.get("side"),
        "qty": row.get("qty"),
        "entry_fill_cents": row.get("entry_fill_cents_used"),
        "p_side": row.get("p_side"),
        "edge_cents": row.get("edge_cents"),
        "ask_cents": row.get("ask_cents"),
        "fair_side_cents": row.get("fair_side_cents"),
        "seconds_to_close": row.get("seconds_to_close"),
        "d_sigma": row.get("d_sigma"),
        "abs_d_sigma": row.get("abs_d_sigma"),
        "sigma_t_dollars": row.get("sigma_t_dollars"),
        "btc_age_ms": row.get("btc_age_ms"),
        "eligible_depth": row.get("eligible_depth"),
        "book_age_ms": row.get("book_age_ms"),
        "outcome_available": available,
        "outcome": row.get("outcome"),
        "actual_net_pnl_dollars": net if available else None,
        "skip_delta_dollars": -net if available and net is not None else None,
    }


def update_existing_outcomes(registry: pd.DataFrame, source_rows: pd.DataFrame) -> pd.DataFrame:
    if registry.empty:
        return registry
    source_by_key = {
        (
            pd.to_datetime(row.get("entry_dt"), utc=True, errors="coerce").isoformat(),
            str(row.get("market") or ""),
            str(row.get("side") or ""),
        ): row
        for _, row in source_rows.iterrows()
    }
    out = registry.copy()
    for idx, reg in out.iterrows():
        key = (
            pd.to_datetime(reg.get("entry_dt"), utc=True, errors="coerce").isoformat(),
            str(reg.get("market") or ""),
            str(reg.get("side") or ""),
        )
        row = source_by_key.get(key)
        if row is None or not outcome_available(row):
            continue
        net = as_float(row.get("net_pnl_dollars"))
        out.loc[idx, "outcome_available"] = True
        out.loc[idx, "outcome"] = row.get("outcome")
        out.loc[idx, "actual_net_pnl_dollars"] = net
        out.loc[idx, "skip_delta_dollars"] = -net if net is not None else None
    return out[REGISTRY_COLS]


def summarize(registry: pd.DataFrame) -> list[dict[str, Any]]:
    summaries: list[dict[str, Any]] = []
    if registry.empty:
        return summaries
    for rule_label, group in registry.groupby("rule_label", sort=False):
        resolved = group[group["outcome_available"].map(as_bool)].copy()
        pending = group[~group["outcome_available"].map(as_bool)].copy()
        actual = pd.to_numeric(resolved.get("actual_net_pnl_dollars"), errors="coerce")
        delta = pd.to_numeric(resolved.get("skip_delta_dollars"), errors="coerce")
        summaries.append(
            {
                "rule_label": rule_label,
                "registered": int(len(group)),
                "resolved": int(len(resolved)),
                "pending": int(len(pending)),
                "actual_net_pnl_dollars": float(actual.sum()),
                "skip_delta_dollars": float(delta.sum()),
                "skip_would_help": int(delta.gt(0).sum()),
                "skip_would_hurt": int(delta.lt(0).sum()),
            }
        )
    return summaries


def write_registry(path: Path, rows: pd.DataFrame) -> None:
    if rows.empty:
        with path.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=REGISTRY_COLS)
            writer.writeheader()
        return
    rows.to_csv(path, index=False)


def write_report(path: Path, generated: str, lock: dict[str, Any], new_records: int, summaries: list[dict[str, Any]]) -> None:
    lines = [
        "# Live v28 Entry Guard Shadow Monitor",
        "",
        f"Generated UTC: `{generated}`",
        "",
        "## Scope",
        "",
        "- Research-only forward registry for current-live-v28 entry skip hypotheses.",
        "- The live bot is not changed; actual entries still happen.",
        "- Positive skip delta means skipping the live fill would have beaten the actual live result.",
        "",
        f"- Effective boundary: `{effective_lock_dt(lock).isoformat()}`",
        f"- New records registered this run: {new_records}",
        "",
        "## State",
        "",
        "| rule | registered | resolved | pending | actual net | skip delta | help/hurt |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    if summaries:
        for row in summaries:
            lines.append(
                f"| `{row['rule_label']}` | {row['registered']} | {row['resolved']} | {row['pending']} | "
                f"${row['actual_net_pnl_dollars']:.2f} | ${row['skip_delta_dollars']:.2f} | "
                f"{row['skip_would_help']}/{row['skip_would_hurt']} |"
            )
    else:
        lines.append("| none | 0 | 0 | 0 | $0.00 | $0.00 | 0/0 |")
    lines += [
        "",
        "## Read",
        "",
    ]
    if not summaries:
        lines.append("- No forward entry-skip events have registered yet.")
    else:
        lines.append("- Forward counterfactual evidence is available; judge these only from registered rows.")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    lock = ensure_lock()
    boundary = effective_lock_dt(lock)
    generated = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%SZ")
    registered_utc = datetime.now(timezone.utc).isoformat()
    source = load_source_rows()
    registry = update_existing_outcomes(load_registry(), source)
    existing = set()
    if not registry.empty:
        existing = set(
            zip(
                registry["rule_label"].astype(str),
                registry["entry_dt"].astype(str),
                registry["market"].astype(str),
                registry["side"].astype(str),
            )
        )
    new_records: list[dict[str, Any]] = []
    future_rows = source[source["entry_dt"].gt(boundary)].copy()
    for rule in lock.get("rules", []):
        label = str(rule.get("label") or "")
        selected = future_rows[rule_mask(future_rows, rule)].copy()
        for _, row in selected.iterrows():
            key = registry_key(row, label)
            if key in existing:
                continue
            new_records.append(record_from_source(row, label, registered_utc))
            existing.add(key)
    if new_records:
        registry = pd.concat([registry, pd.DataFrame(new_records)], ignore_index=True)
    registry = registry[REGISTRY_COLS].sort_values(["entry_dt", "rule_label", "market", "side"]).reset_index(drop=True)
    summaries = summarize(registry)
    write_registry(REGISTRY_PATH, registry)
    write_registry(OUT_DIR / f"live_v28_entry_guard_shadow_registry_{generated}.csv", registry)
    payload = {
        "generated_utc": generated,
        "new_records": len(new_records),
        "lock_path": str(LOCK_PATH),
        "registry_path": str(REGISTRY_PATH),
        "effective_boundary": boundary.isoformat(),
        "summaries": summaries,
    }
    JSON_LATEST.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (OUT_DIR / f"live_v28_entry_guard_shadow_monitor_{generated}.json").write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    write_report(REPORT_LATEST, generated, lock, len(new_records), summaries)
    write_report(OUT_DIR / f"live_v28_entry_guard_shadow_monitor_{generated}.md", generated, lock, len(new_records), summaries)
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
