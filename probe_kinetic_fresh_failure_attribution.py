"""Attribution report for fresh kinetic-family failures.

This probe reads the pre-registered pending-signal registry and bot quote log to
describe fresh kinetic losses without changing any locks. It is meant to
separate physical failure modes from tempting post-loss threshold repairs.

Research-only: no orders are submitted and no bot files or live processes are
modified.
"""
from __future__ import annotations

import json
import math
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List
from zoneinfo import ZoneInfo

import numpy as np
import pandas as pd

from probe_live_v28_fv_accuracy_volume import BOT_LOG, as_float, parse_quote_token
from probe_market_interval_80coverage import OUT_DIR, clean_json, pct


REGISTRY_PATH = OUT_DIR / "profit_lock_pending_signal_registry_latest.csv"
REPORT_MD = OUT_DIR / "kinetic_fresh_failure_attribution_latest.md"
REPORT_JSON = OUT_DIR / "kinetic_fresh_failure_attribution_latest.json"

KINETIC_LOCKS = {"kinetic_touch", "kinetic_guard", "kinetic_price_guard"}
LOCAL_TZ = ZoneInfo("America/New_York")
FEATURE_COLS = [
    "ask_cents",
    "book_p_side",
    "brownian_p_rv_15m",
    "brownian_p_rv_30m",
    "margin_per_rv_sigma_15m",
    "adverse_move_15m",
    "touch_loss_rv_15m",
    "kinetic_touch_score_15",
    "seconds_to_close",
]


def clean_json_local(value: Any) -> Any:
    if isinstance(value, pd.Timestamp):
        return value.isoformat()
    if isinstance(value, dict):
        return {str(k): clean_json_local(v) for k, v in value.items()}
    if isinstance(value, list):
        return [clean_json_local(v) for v in value]
    return clean_json(value)


def bool_value(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() in {"true", "1", "yes"}


def finite(value: Any, default: float = float("nan")) -> float:
    try:
        val = float(value)
    except (TypeError, ValueError):
        return default
    return val if math.isfinite(val) else default


def fmt_cents(value: Any) -> str:
    val = finite(value)
    if not math.isfinite(val):
        return "NA"
    return f"{val:.1f}c"


def fmt_num(value: Any, digits: int = 3) -> str:
    val = finite(value)
    if not math.isfinite(val):
        return "NA"
    return f"{val:.{digits}f}"


def load_registry() -> pd.DataFrame:
    if not REGISTRY_PATH.exists():
        return pd.DataFrame()
    df = pd.read_csv(REGISTRY_PATH)
    for col in ["entry_dt", "close_dt"]:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], utc=True, errors="coerce")
    for col in FEATURE_COLS + ["net_pnl_cents"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    df["outcome_available"] = df.get("outcome_available", False).map(bool_value)
    df["win_bool"] = df.get("win", False).map(bool_value)
    return df


def quote_rows_for_market(market: str) -> pd.DataFrame:
    heartbeat_re = re.compile(
        r"(?P<ts>[^|]+) \| INFO \| Heartbeat \| watch=(?P<market>\S+) "
        r"yes_bid=(?P<yes_bid>\S+) yes_ask=(?P<yes_ask>\S+) "
        r"no_bid=(?P<no_bid>\S+) no_ask=(?P<no_ask>\S+)"
    )
    rows: List[Dict[str, Any]] = []
    if not BOT_LOG.exists():
        return pd.DataFrame(rows)
    with BOT_LOG.open("r", encoding="utf-8", errors="replace") as handle:
        for line_no, line in enumerate(handle, start=1):
            match = heartbeat_re.search(line)
            if not match or match.group("market") != market:
                continue
            yes_bid = parse_quote_token(match.group("yes_bid"))
            yes_ask = parse_quote_token(match.group("yes_ask"))
            no_bid = parse_quote_token(match.group("no_bid"))
            no_ask = parse_quote_token(match.group("no_ask"))
            yes_mid = (yes_bid + yes_ask) / 2.0 if yes_bid is not None and yes_ask is not None else np.nan
            no_mid = (no_bid + no_ask) / 2.0 if no_bid is not None and no_ask is not None else np.nan
            ts = pd.to_datetime(match.group("ts").strip(), errors="coerce")
            if pd.isna(ts):
                ts_utc = pd.NaT
            elif ts.tzinfo is None:
                ts_utc = ts.tz_localize(LOCAL_TZ).tz_convert("UTC")
            else:
                ts_utc = ts.tz_convert("UTC")
            rows.append(
                {
                    "line_no": line_no,
                    "ts": ts_utc,
                    "yes_bid": yes_bid,
                    "yes_ask": yes_ask,
                    "no_bid": no_bid,
                    "no_ask": no_ask,
                    "yes_mid": yes_mid,
                    "no_mid": no_mid,
                }
            )
    return pd.DataFrame(rows)


def path_summary(market: str, entry_dt: pd.Timestamp, close_dt: pd.Timestamp, side: str) -> Dict[str, Any]:
    quotes = quote_rows_for_market(market)
    if quotes.empty or pd.isna(entry_dt):
        return {"market": market, "quotes": []}
    window = quotes[quotes["ts"].ge(entry_dt)].copy()
    if pd.notna(close_dt):
        window = window[window["ts"].le(close_dt)]
    if window.empty:
        return {"market": market, "quotes": []}

    side_mid_col = "yes_mid" if side == "yes" else "no_mid"
    other_mid_col = "no_mid" if side == "yes" else "yes_mid"
    checkpoints: List[Dict[str, Any]] = []
    for offset_sec in [0, 60, 180, 300, 600, 840]:
        target = entry_dt + pd.Timedelta(seconds=offset_sec)
        part = window[window["ts"].ge(target)]
        if part.empty:
            continue
        row = part.iloc[0]
        checkpoints.append(
            {
                "offset_sec": offset_sec,
                "ts": row["ts"],
                "yes_mid": finite(row["yes_mid"]),
                "no_mid": finite(row["no_mid"]),
                "side_mid": finite(row[side_mid_col]),
                "other_mid": finite(row[other_mid_col]),
            }
        )
    best_side = finite(window[side_mid_col].max())
    worst_side = finite(window[side_mid_col].min())
    best_other = finite(window[other_mid_col].max())
    return {
        "market": market,
        "quote_count": int(len(window)),
        "side_mid_at_entry": finite(window.iloc[0][side_mid_col]),
        "side_mid_min_after_entry": worst_side,
        "side_mid_max_after_entry": best_side,
        "other_mid_max_after_entry": best_other,
        "checkpoints": checkpoints,
    }


def feature_summary(rows: pd.DataFrame) -> pd.DataFrame:
    if rows.empty:
        return pd.DataFrame(columns=["feature", "wins_mean", "losses_mean", "loss_minus_win"])
    records: List[Dict[str, Any]] = []
    wins = rows[rows["win_bool"]]
    losses = rows[~rows["win_bool"]]
    for col in FEATURE_COLS:
        win_mean = finite(wins[col].mean()) if col in wins.columns and not wins.empty else float("nan")
        loss_mean = finite(losses[col].mean()) if col in losses.columns and not losses.empty else float("nan")
        records.append(
            {
                "feature": col,
                "wins_mean": win_mean,
                "losses_mean": loss_mean,
                "loss_minus_win": loss_mean - win_mean if math.isfinite(win_mean) and math.isfinite(loss_mean) else float("nan"),
            }
        )
    return pd.DataFrame(records)


def write_report(generated: str, resolved: pd.DataFrame, losses: pd.DataFrame, summaries: List[Dict[str, Any]]) -> None:
    lines: List[str] = [
        "# Kinetic Fresh Failure Attribution",
        "",
        f"Generated UTC: `{generated}`",
        "",
        "## Scope",
        "",
        "- Research-only diagnostic; no orders are submitted and no bot files or live processes are touched.",
        "- Uses only pre-registered kinetic-family signals and bot quote paths.",
        "- Post-loss explanations are diagnostics only; they do not update any lock.",
        "",
        "## Fresh Kinetic Registry State",
        "",
        "| lock | resolved | wins/losses | net P&L |",
        "|---|---:|---:|---:|",
    ]
    for lock_name, part in resolved.groupby("lock_name", sort=True):
        wins = int(part["win_bool"].sum())
        total = int(len(part))
        net = float(part["net_pnl_cents"].sum()) if total else 0.0
        lines.append(f"| `{lock_name}` | {total} | {wins}/{total - wins} | {fmt_cents(net)} |")

    lines += [
        "",
        "## Loss Rows",
        "",
        "| lock | market | entry | side | ask | outcome | book | brownian15 | adverse15 | touch_loss15 | kinetic | net |",
        "|---|---|---|---|---:|---|---:|---:|---:|---:|---:|---:|",
    ]
    for _, row in losses.sort_values(["market", "lock_name"]).iterrows():
        lines.append(
            f"| `{row['lock_name']}` | `{row['market']}` | `{row['entry_dt']}` | {row['side']} | "
            f"{fmt_cents(row['ask_cents'])} | {row['outcome']} | {fmt_num(row['book_p_side'])} | "
            f"{fmt_num(row['brownian_p_rv_15m'])} | {fmt_cents(row['adverse_move_15m'])} | "
            f"{fmt_num(row['touch_loss_rv_15m'])} | {fmt_num(row['kinetic_touch_score_15'])} | "
            f"{fmt_cents(row['net_pnl_cents'])} |"
        )

    lines += [
        "",
        "## Feature Means",
        "",
        "| feature | wins mean | losses mean | loss - win |",
        "|---|---:|---:|---:|",
    ]
    means = feature_summary(resolved)
    for _, row in means.iterrows():
        lines.append(
            f"| `{row['feature']}` | {fmt_num(row['wins_mean'])} | {fmt_num(row['losses_mean'])} | "
            f"{fmt_num(row['loss_minus_win'])} |"
        )

    lines += ["", "## Quote Path Checkpoints", ""]
    for summary in summaries:
        lines += [
            f"### `{summary['market']}`",
            "",
            f"- Quote count after entry: {summary.get('quote_count', 0)}",
            f"- Side mid at entry/min/max after entry: {fmt_cents(summary.get('side_mid_at_entry'))} / "
            f"{fmt_cents(summary.get('side_mid_min_after_entry'))} / {fmt_cents(summary.get('side_mid_max_after_entry'))}",
            f"- Opposite side max after entry: {fmt_cents(summary.get('other_mid_max_after_entry'))}",
            "",
            "| offset sec | timestamp | YES mid | NO mid | chosen side mid | opposite mid |",
            "|---:|---|---:|---:|---:|---:|",
        ]
        for point in summary.get("checkpoints", []):
            lines.append(
                f"| {point['offset_sec']} | `{point['ts']}` | {fmt_cents(point['yes_mid'])} | "
                f"{fmt_cents(point['no_mid'])} | {fmt_cents(point['side_mid'])} | {fmt_cents(point['other_mid'])} |"
            )
        lines.append("")

    lines += [
        "## Read",
        "",
        "- The latest loss is a live-path failure: the selected side was cheap and physically plausible at entry, but the order book flipped rapidly and stayed flipped.",
        "- A book-floor repair would have avoided this loss, but separate cross-split diagnostics show that book floors are not yet stable enough to promote without their own future lock.",
    ]
    REPORT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")
    REPORT_JSON.write_text(
        json.dumps(
            {
                "generated_utc": generated,
                "losses": clean_json_local(losses.to_dict(orient="records")),
                "feature_means": clean_json_local(means.to_dict(orient="records")),
                "path_summaries": clean_json_local(summaries),
            },
            indent=2,
            sort_keys=True,
        ),
        encoding="utf-8",
    )


def main() -> int:
    generated = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%SZ")
    registry = load_registry()
    if registry.empty:
        write_report(generated, registry, registry, [])
        print("Kinetic fresh failure attribution complete")
        print(f"report={REPORT_MD}")
        return 0
    kinetic = registry[registry["lock_name"].isin(KINETIC_LOCKS) & registry["outcome_available"]].copy()
    losses = kinetic[~kinetic["win_bool"]].copy()
    summaries = []
    for _, row in losses.drop_duplicates(["market", "side", "entry_dt"]).iterrows():
        summaries.append(path_summary(str(row["market"]), row["entry_dt"], row["close_dt"], str(row["side"])))
    write_report(generated, kinetic, losses, summaries)
    print("Kinetic fresh failure attribution complete")
    print(f"resolved={len(kinetic)} losses={len(losses)}")
    print(f"report={REPORT_MD}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
