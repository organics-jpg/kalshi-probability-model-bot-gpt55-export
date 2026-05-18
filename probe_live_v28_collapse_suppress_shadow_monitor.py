"""Forward shadow monitor for the v28 probability-collapse exit hypothesis.

The live v28 bot remains untouched. This monitor only records future
`mushroom_v28_probability_collapse_full` exit signals where the diagnostic
rule says "maybe this is turbulence, not a true collapse" and later scores
whether holding to settlement would have beaten the actual live exit.
"""
from __future__ import annotations

import csv
import json
import math
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

import pandas as pd


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
LOCK_PATH = OUT_DIR / "live_v28_collapse_sigma_drawdown_suppress_shadow_lock.json"
REGISTRY_PATH = OUT_DIR / "live_v28_collapse_suppress_shadow_registry_latest.csv"
REPORT_LATEST = OUT_DIR / "live_v28_collapse_suppress_shadow_monitor_latest.md"
JSON_LATEST = OUT_DIR / "live_v28_collapse_suppress_shadow_monitor_latest.json"
EXECUTION_EVENTS_PATH = ROOT / "logs" / "live_mushroom_v28_size2" / "execution_events.ndjson"
BOT_LOG_PATH = ROOT / "logs" / "live_mushroom_v28_size2" / "bot.log"
MARKET_RESULTS_PATH = ROOT / "stats" / "live_mushroom_v28_size2" / "market_results.csv"
BRANCH_AUDIT_JSON = OUT_DIR / "live_v28_probability_collapse_branch_audit_latest.json"
LOCAL_TZ = ZoneInfo("America/New_York")

BRANCH_REASON = "mushroom_v28_probability_collapse_full"
RULE_LABEL = "suppress_collapse_exit_if_exit_fair_drawdown_cents<=15_AND_exit_sigma_t_dollars>=50"
FAIR_DRAWDOWN_MAX = 15.0
SIGMA_T_MIN = 50.0

WATCH_RE = re.compile(r"Watching market (?P<market>\S+) close_time=(?P<close_time>\S+)")
TICKER_RE = re.compile(r"KXBTC15M-(?P<yy>\d{2})(?P<mon>[A-Z]{3})(?P<dd>\d{2})(?P<hh>\d{2})(?P<mm>\d{2})-")
MONTHS = {
    "JAN": 1,
    "FEB": 2,
    "MAR": 3,
    "APR": 4,
    "MAY": 5,
    "JUN": 6,
    "JUL": 7,
    "AUG": 8,
    "SEP": 9,
    "OCT": 10,
    "NOV": 11,
    "DEC": 12,
}

REGISTRY_COLS = [
    "lock_name",
    "registered_utc",
    "event_dt",
    "market",
    "close_dt",
    "side",
    "exit_reason",
    "entry_basis_cents",
    "exit_bid_cents",
    "exit_target_count",
    "p_hold",
    "fair_drawdown_cents",
    "d_sigma",
    "sigma_t_dollars",
    "btc_age_ms",
    "book_age_ms",
    "actual_exit_pnl_dollars",
    "outcome_available",
    "market_result",
    "hold_to_settlement_pnl_dollars",
    "suppress_exit_delta_dollars",
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


def load_branch_diagnostic() -> dict[str, Any]:
    if not BRANCH_AUDIT_JSON.exists():
        return {}
    try:
        payload = json.loads(BRANCH_AUDIT_JSON.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
    top = (payload.get("top_candidates") or [{}])[0]
    summary = payload.get("summary") or {}
    return {
        "source": "live_v28_probability_collapse_branch_audit_latest",
        "branch_exits": summary.get("n"),
        "actual_exit_net_dollars": summary.get("actual_exit_net_dollars"),
        "hold_to_settlement_net_dollars": summary.get("hold_to_settlement_net_dollars"),
        "branch_exit_value_delta_dollars": summary.get("exit_value_delta_dollars"),
        "candidate_rule": top.get("rule"),
        "candidate_adjusted_net_dollars": top.get("adjusted_net_dollars"),
        "candidate_delta_vs_branch_actual_dollars": top.get("delta_vs_branch_actual_dollars"),
        "candidate_suppressed_exits": top.get("suppressed_exits"),
        "candidate_suppressed_share": top.get("suppressed_share"),
        "candidate_hurtful_helpful_suppressed": [
            top.get("hurtful_exits_suppressed"),
            top.get("helpful_exits_suppressed"),
        ],
        "selection_warning": (
            "Research-only forward shadow. The historical branch sample is small, "
            "and the top rule suppressed no validation-split exits."
        ),
    }


def ensure_lock() -> dict[str, Any]:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    if LOCK_PATH.exists():
        return json.loads(LOCK_PATH.read_text(encoding="utf-8"))
    created = datetime.now(timezone.utc)
    lock_close = next_full_15m_close(created).isoformat()
    lock = {
        "created_utc": created.isoformat(),
        "lock_close_dt": lock_close,
        "lock_name": "live_v28_collapse_sigma_drawdown_suppress_shadow",
        "rule": {
            "label": RULE_LABEL,
            "exit_reason": BRANCH_REASON,
            "fair_drawdown_cents_op": "<=",
            "fair_drawdown_cents_threshold": FAIR_DRAWDOWN_MAX,
            "sigma_t_dollars_op": ">=",
            "sigma_t_dollars_threshold": SIGMA_T_MIN,
        },
        "diagnostic_metrics": load_branch_diagnostic(),
        "research_note": (
            "Physical hypothesis: a full probability-collapse exit is suspect when "
            "terminal sigma is still high and the model's fair drawdown is not deep. "
            "That state may be temporary path turbulence rather than terminal truth."
        ),
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


def close_from_ticker(market: str) -> pd.Timestamp:
    match = TICKER_RE.search(str(market))
    if not match:
        return pd.NaT
    mon = MONTHS.get(match.group("mon"))
    if not mon:
        return pd.NaT
    local_dt = datetime(
        2000 + int(match.group("yy")),
        mon,
        int(match.group("dd")),
        int(match.group("hh")),
        int(match.group("mm")),
        tzinfo=LOCAL_TZ,
    )
    return pd.Timestamp(local_dt).tz_convert("UTC")


def load_watch_close_times() -> dict[str, pd.Timestamp]:
    closes: dict[str, pd.Timestamp] = {}
    if not BOT_LOG_PATH.exists():
        return closes
    with BOT_LOG_PATH.open("r", encoding="utf-8", errors="replace") as handle:
        for line in handle:
            match = WATCH_RE.search(line)
            if not match:
                continue
            closes[match.group("market")] = pd.to_datetime(match.group("close_time"), utc=True, errors="coerce")
    return closes


def load_results() -> dict[str, str]:
    if not MARKET_RESULTS_PATH.exists():
        return {}
    rows = pd.read_csv(MARKET_RESULTS_PATH)
    return {
        str(row.get("market") or ""): str(row.get("result") or "").lower()
        for _, row in rows.iterrows()
    }


def load_registry() -> pd.DataFrame:
    if not REGISTRY_PATH.exists():
        return pd.DataFrame(columns=REGISTRY_COLS)
    rows = pd.read_csv(REGISTRY_PATH)
    for col in REGISTRY_COLS:
        if col not in rows.columns:
            rows[col] = None
    return rows[REGISTRY_COLS].copy()


def parse_exit_events(close_times: dict[str, pd.Timestamp]) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    with EXECUTION_EVENTS_PATH.open("r", encoding="utf-8", errors="replace") as handle:
        for line in handle:
            if not line.strip():
                continue
            try:
                event = json.loads(line)
            except json.JSONDecodeError:
                continue
            if event.get("event_type") != "exit_signal_seen":
                continue
            market = str(event.get("market") or "")
            event_dt = pd.to_datetime(event.get("ts_wall"), utc=True, errors="coerce")
            close_dt = close_times.get(market, pd.NaT)
            if pd.isna(close_dt):
                close_dt = close_from_ticker(market)
            rows.append(
                {
                    "event_dt": event_dt,
                    "market": market,
                    "close_dt": close_dt,
                    "side": str(event.get("side") or "").lower(),
                    "exit_reason": str(event.get("mushroom_v28_exit_reason") or ""),
                    "entry_basis_cents": as_float(event.get("mushroom_v28_entry_basis_cents")),
                    "exit_bid_cents": as_float(event.get("mushroom_v28_exit_bid_cents")),
                    "exit_target_count": as_float(event.get("mushroom_v28_exit_target_count"))
                    or as_float(event.get("position_size"))
                    or 1.0,
                    "p_hold": as_float(event.get("mushroom_v28_p_hold")),
                    "fair_drawdown_cents": as_float(event.get("mushroom_v28_fair_drawdown_cents")),
                    "d_sigma": as_float(event.get("mushroom_v28_d_sigma")),
                    "sigma_t_dollars": as_float(event.get("mushroom_v28_sigma_t_dollars")),
                    "btc_age_ms": as_float(event.get("mushroom_v28_btc_age_ms")),
                    "book_age_ms": as_float(event.get("mushroom_v28_book_age_ms") or event.get("book_age_ms")),
                }
            )
    return pd.DataFrame(rows)


def rule_mask(rows: pd.DataFrame, lock: dict[str, Any]) -> pd.Series:
    rule = lock.get("rule", {})
    fair_threshold = float(rule.get("fair_drawdown_cents_threshold", FAIR_DRAWDOWN_MAX))
    sigma_threshold = float(rule.get("sigma_t_dollars_threshold", SIGMA_T_MIN))
    fair = pd.to_numeric(rows["fair_drawdown_cents"], errors="coerce")
    sigma = pd.to_numeric(rows["sigma_t_dollars"], errors="coerce")
    return (
        rows["exit_reason"].astype(str).eq(str(rule.get("exit_reason") or BRANCH_REASON))
        & fair.le(fair_threshold).fillna(False)
        & sigma.ge(sigma_threshold).fillna(False)
    )


def record_from_event(row: pd.Series, registered_utc: str) -> dict[str, Any]:
    count = float(row.get("exit_target_count") or 1.0)
    entry = float(row.get("entry_basis_cents") or 0.0)
    exit_bid = float(row.get("exit_bid_cents") or 0.0)
    actual = (exit_bid - entry) * count / 100.0
    return {
        "lock_name": "live_v28_collapse_sigma_drawdown_suppress_shadow",
        "registered_utc": registered_utc,
        "event_dt": pd.to_datetime(row.get("event_dt"), utc=True, errors="coerce").isoformat(),
        "market": row.get("market"),
        "close_dt": pd.to_datetime(row.get("close_dt"), utc=True, errors="coerce").isoformat(),
        "side": row.get("side"),
        "exit_reason": row.get("exit_reason"),
        "entry_basis_cents": entry,
        "exit_bid_cents": exit_bid,
        "exit_target_count": count,
        "p_hold": row.get("p_hold"),
        "fair_drawdown_cents": row.get("fair_drawdown_cents"),
        "d_sigma": row.get("d_sigma"),
        "sigma_t_dollars": row.get("sigma_t_dollars"),
        "btc_age_ms": row.get("btc_age_ms"),
        "book_age_ms": row.get("book_age_ms"),
        "actual_exit_pnl_dollars": actual,
        "outcome_available": False,
        "market_result": "",
        "hold_to_settlement_pnl_dollars": None,
        "suppress_exit_delta_dollars": None,
    }


def update_outcomes(registry: pd.DataFrame, results: dict[str, str]) -> pd.DataFrame:
    if registry.empty:
        return registry
    out = registry.copy()
    for idx, row in out.iterrows():
        result = str(results.get(str(row.get("market") or ""), "")).lower()
        if result not in {"yes", "no"}:
            continue
        side = str(row.get("side") or "").lower()
        count = float(row.get("exit_target_count") or 1.0)
        entry = float(row.get("entry_basis_cents") or 0.0)
        hold = ((100.0 - entry) if side == result else -entry) * count / 100.0
        actual = float(row.get("actual_exit_pnl_dollars") or 0.0)
        out.loc[idx, "outcome_available"] = True
        out.loc[idx, "market_result"] = result
        out.loc[idx, "hold_to_settlement_pnl_dollars"] = hold
        out.loc[idx, "suppress_exit_delta_dollars"] = hold - actual
    return out[REGISTRY_COLS]


def summarize(registry: pd.DataFrame) -> dict[str, Any]:
    if registry.empty:
        return {
            "registered": 0,
            "resolved": 0,
            "pending": 0,
            "actual_exit_pnl_dollars": 0.0,
            "hold_to_settlement_pnl_dollars": 0.0,
            "suppress_exit_delta_dollars": 0.0,
            "suppression_would_help": 0,
            "suppression_would_hurt": 0,
        }
    resolved = registry[registry["outcome_available"].map(as_bool)].copy()
    pending = registry[~registry["outcome_available"].map(as_bool)].copy()
    delta = pd.to_numeric(resolved.get("suppress_exit_delta_dollars"), errors="coerce")
    return {
        "registered": int(len(registry)),
        "resolved": int(len(resolved)),
        "pending": int(len(pending)),
        "actual_exit_pnl_dollars": float(pd.to_numeric(resolved.get("actual_exit_pnl_dollars"), errors="coerce").sum()),
        "hold_to_settlement_pnl_dollars": float(pd.to_numeric(resolved.get("hold_to_settlement_pnl_dollars"), errors="coerce").sum()),
        "suppress_exit_delta_dollars": float(delta.sum()),
        "suppression_would_help": int(delta.gt(0).sum()),
        "suppression_would_hurt": int(delta.lt(0).sum()),
    }


def write_registry(path: Path, rows: pd.DataFrame) -> None:
    if rows.empty:
        with path.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=REGISTRY_COLS)
            writer.writeheader()
        return
    rows.to_csv(path, index=False)


def write_report(path: Path, generated: str, lock: dict[str, Any], new_records: int, summary: dict[str, Any]) -> None:
    lines = [
        "# Live v28 Collapse Suppress Shadow Monitor",
        "",
        f"Generated UTC: `{generated}`",
        "",
        "## Scope",
        "",
        "- Research-only forward registry for the v28 probability-collapse suppression hypothesis.",
        "- The live bot is not changed; actual exits still happen.",
        "- Positive suppress delta means holding would have beaten the live exit for that registered event.",
        "",
        f"- Rule: `{lock.get('rule', {}).get('label', '')}`",
        f"- Exit reason: `{BRANCH_REASON}`",
        f"- Effective boundary: `{effective_lock_dt(lock).isoformat()}`",
        f"- New records registered this run: {new_records}",
        "",
        "## State",
        "",
        "| registered | resolved | pending | actual exit net | hold net | suppress delta | help/hurt |",
        "|---:|---:|---:|---:|---:|---:|---:|",
        f"| {summary['registered']} | {summary['resolved']} | {summary['pending']} | "
        f"${summary['actual_exit_pnl_dollars']:.2f} | ${summary['hold_to_settlement_pnl_dollars']:.2f} | "
        f"${summary['suppress_exit_delta_dollars']:.2f} | "
        f"{summary['suppression_would_help']}/{summary['suppression_would_hurt']} |",
        "",
        "## Read",
        "",
    ]
    if summary["registered"] == 0:
        lines.append("- No forward collapse-suppression events have registered yet.")
    elif summary["resolved"] == 0:
        lines.append("- Forward events are registered, but none have resolved yet.")
    else:
        lines.append("- Forward counterfactual evidence is available; judge this only from registered rows.")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    lock = ensure_lock()
    boundary = effective_lock_dt(lock)
    generated = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%SZ")
    registered_utc = datetime.now(timezone.utc).isoformat()
    events = parse_exit_events(load_watch_close_times())
    if events.empty:
        raise SystemExit("No exit events available.")
    selected = events[
        events["event_dt"].gt(boundary)
        & events["close_dt"].gt(events["event_dt"])
        & rule_mask(events, lock)
    ].copy()
    registry = load_registry()
    existing = set()
    if not registry.empty:
        existing = set(
            zip(
                registry["event_dt"].astype(str),
                registry["market"].astype(str),
                registry["side"].astype(str),
            )
        )
    new_records: list[dict[str, Any]] = []
    for _, row in selected.iterrows():
        key = (
            pd.to_datetime(row["event_dt"], utc=True, errors="coerce").isoformat(),
            str(row.get("market") or ""),
            str(row.get("side") or ""),
        )
        if key in existing:
            continue
        new_records.append(record_from_event(row, registered_utc))
        existing.add(key)
    if new_records:
        registry = pd.concat([registry, pd.DataFrame(new_records)], ignore_index=True)
    registry = update_outcomes(registry, load_results())
    registry = registry[REGISTRY_COLS].sort_values(["event_dt", "market", "side"]).reset_index(drop=True)
    write_registry(REGISTRY_PATH, registry)
    write_registry(OUT_DIR / f"live_v28_collapse_suppress_shadow_registry_{generated}.csv", registry)
    summary = summarize(registry)
    payload = {
        "generated_utc": generated,
        "new_records": len(new_records),
        "lock_path": str(LOCK_PATH),
        "registry_path": str(REGISTRY_PATH),
        "effective_boundary": boundary.isoformat(),
        "summary": summary,
    }
    JSON_LATEST.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (OUT_DIR / f"live_v28_collapse_suppress_shadow_monitor_{generated}.json").write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    write_report(REPORT_LATEST, generated, lock, len(new_records), summary)
    write_report(OUT_DIR / f"live_v28_collapse_suppress_shadow_monitor_{generated}.md", generated, lock, len(new_records), summary)
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
