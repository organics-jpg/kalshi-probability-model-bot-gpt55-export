"""Research-only loss guard scan for the current live Mushroom v28 bot.

This script reads the live v28 fill tape and execution telemetry, joins each
filled trade to the v28 approval snapshot that created it, and scans simple
pre-entry guards that would have skipped weak entries. It does not import,
modify, or control the live bot, and it never submits orders.
"""
from __future__ import annotations

import csv
import json
import math
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable
from zoneinfo import ZoneInfo

import pandas as pd


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
TRADES_PATH = ROOT / "stats" / "live_mushroom_v28_size2" / "trades.csv"
MARKET_RESULTS_PATH = ROOT / "stats" / "live_mushroom_v28_size2" / "market_results.csv"
EXECUTION_EVENTS_PATH = ROOT / "logs" / "live_mushroom_v28_size2" / "execution_events.ndjson"
LOCAL_TZ = ZoneInfo("America/New_York")

MIN_TRADE_RETENTION = 0.80
MIN_MARKET_RETENTION = 0.80
MATCH_WINDOW_SECONDS = 3.0


FEATURE_COLS = [
    "p_side",
    "edge_cents",
    "raw_edge_cents",
    "net_edge_cents",
    "ask_cents",
    "fair_side_cents",
    "seconds_to_close",
    "d_sigma",
    "abs_d_sigma",
    "sigma_t_dollars",
    "btc_age_ms",
    "eligible_depth",
    "book_age_ms",
]


@dataclass(frozen=True)
class Condition:
    label: str
    column: str
    op: str
    threshold: float

    def mask(self, rows: pd.DataFrame) -> pd.Series:
        values = pd.to_numeric(rows[self.column], errors="coerce")
        if self.op == ">=":
            keep = values.ge(self.threshold)
        elif self.op == "<=":
            keep = values.le(self.threshold)
        else:
            raise ValueError(f"unsupported op: {self.op}")
        return keep | values.isna()


@dataclass(frozen=True)
class GuardSpec:
    label: str
    conditions: tuple[Condition, ...]

    def mask(self, rows: pd.DataFrame) -> pd.Series:
        keep = pd.Series(True, index=rows.index)
        for condition in self.conditions:
            keep &= condition.mask(rows)
        return keep


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


def local_entry_to_utc(value: Any) -> pd.Timestamp:
    ts = pd.to_datetime(value, errors="coerce")
    if pd.isna(ts):
        return pd.NaT
    if ts.tzinfo is None:
        ts = ts.tz_localize(LOCAL_TZ, nonexistent="shift_forward", ambiguous="NaT")
    return ts.tz_convert("UTC")


def load_trades() -> pd.DataFrame:
    if not TRADES_PATH.exists():
        raise SystemExit(f"Missing scored trades: {TRADES_PATH}. Run score_bot_log.py first.")
    rows = pd.read_csv(TRADES_PATH)
    if rows.empty:
        raise SystemExit(f"No scored trades in {TRADES_PATH}")
    rows["entry_dt_utc"] = rows["entry_ts"].map(local_entry_to_utc)
    for col in ["qty", "entry_fill_cents_used", "exit_fill_cents_used", "net_pnl_dollars"]:
        rows[col] = pd.to_numeric(rows.get(col), errors="coerce")
    rows["trade_negative"] = rows["net_pnl_dollars"].fillna(0.0).lt(0.0)
    rows["settled_loss"] = rows["outcome"].astype(str).str.lower().eq("loss")
    return rows


def load_observed_market_count() -> int:
    if not MARKET_RESULTS_PATH.exists():
        return 0
    rows = pd.read_csv(MARKET_RESULTS_PATH)
    if rows.empty:
        return 0
    resolved = rows[rows["result"].astype(str).str.lower().isin(["yes", "no"])]
    return int(len(resolved))


def load_v28_approval_events() -> pd.DataFrame:
    events: list[dict[str, Any]] = []
    with EXECUTION_EVENTS_PATH.open("r", encoding="utf-8", errors="replace") as handle:
        for line in handle:
            if not line.strip():
                continue
            try:
                event = json.loads(line)
            except json.JSONDecodeError:
                continue
            if event.get("event_type") != "mushroom_v28_approved":
                continue
            if str(event.get("mushroom_v28_approved")).lower() not in {"true", "1", "yes"}:
                continue
            side = str(event.get("mushroom_v28_side") or event.get("side") or "").lower()
            row = {
                "event_dt_utc": pd.to_datetime(event.get("ts_wall"), utc=True, errors="coerce"),
                "market": str(event.get("market") or ""),
                "side": side,
                "p_side": as_float(event.get("mushroom_v28_p_side")),
                "edge_cents": as_float(event.get("mushroom_v28_edge_cents")),
                "raw_edge_cents": as_float(event.get("mushroom_v28_raw_edge_cents")),
                "net_edge_cents": as_float(event.get("mushroom_v28_net_edge_cents")),
                "ask_cents": as_float(event.get("mushroom_v28_ask_cents")),
                "fair_side_cents": as_float(event.get("mushroom_v28_fair_side_cents")),
                "seconds_to_close": as_float(event.get("mushroom_v28_seconds_to_close")),
                "d_sigma": as_float(event.get("mushroom_v28_d_sigma")),
                "abs_d_sigma": as_float(event.get("mushroom_v28_abs_d_sigma")),
                "sigma_t_dollars": as_float(event.get("mushroom_v28_sigma_t_dollars")),
                "btc_age_ms": as_float(event.get("mushroom_v28_btc_age_ms")),
                "eligible_depth": as_float(event.get("mushroom_v28_eligible_depth") or event.get("eligible_depth")),
                "book_age_ms": as_float(event.get("mushroom_v28_book_age_ms") or event.get("book_age_ms")),
                "btc_price": as_float(event.get("mushroom_v28_btc_price")),
                "strike": as_float(event.get("mushroom_v28_strike")),
            }
            events.append(row)
    if not events:
        raise SystemExit(f"No v28 approval events found in {EXECUTION_EVENTS_PATH}")
    return pd.DataFrame(events).sort_values(["market", "side", "event_dt_utc"]).reset_index(drop=True)


def join_trade_features(trades: pd.DataFrame, events: pd.DataFrame) -> pd.DataFrame:
    joined: list[dict[str, Any]] = []
    grouped = {
        key: frame.reset_index(drop=True)
        for key, frame in events.groupby(["market", "side"], sort=False)
    }
    for _, trade in trades.iterrows():
        key = (str(trade.get("market") or ""), str(trade.get("side") or "").lower())
        candidates = grouped.get(key)
        if candidates is None or candidates.empty or pd.isna(trade["entry_dt_utc"]):
            joined.append({})
            continue
        diffs = (trade["entry_dt_utc"] - candidates["event_dt_utc"]).dt.total_seconds()
        window = candidates[diffs.ge(-1.0) & diffs.le(MATCH_WINDOW_SECONDS)].copy()
        if window.empty:
            joined.append({})
            continue
        window["match_abs_diff_seconds"] = (trade["entry_dt_utc"] - window["event_dt_utc"]).dt.total_seconds().abs()
        joined.append(window.sort_values("match_abs_diff_seconds").iloc[0].to_dict())
    features = pd.DataFrame(joined).add_prefix("feature_")
    out = pd.concat([trades.reset_index(drop=True), features.reset_index(drop=True)], axis=1)
    for col in FEATURE_COLS:
        source = f"feature_{col}"
        if source in out.columns:
            out[col] = pd.to_numeric(out[source], errors="coerce")
    out["matched_v28_approval"] = out["feature_event_dt_utc"].notna() if "feature_event_dt_utc" in out else False
    out = out[out["matched_v28_approval"]].copy()
    out = out.sort_values(["entry_dt_utc", "market", "side"]).reset_index(drop=True)
    return out


def split_labels(rows: pd.DataFrame) -> pd.Series:
    ordered = rows.sort_values("entry_dt_utc").reset_index()
    n = len(ordered)
    labels = pd.Series("", index=rows.index, dtype=object)
    for pos, original_idx in enumerate(ordered["index"]):
        frac = pos / max(1, n)
        if frac < 0.50:
            labels.loc[original_idx] = "train"
        elif frac < 0.75:
            labels.loc[original_idx] = "validation"
        else:
            labels.loc[original_idx] = "holdout"
    return labels


def metrics(rows: pd.DataFrame, keep: pd.Series, observed_markets: int) -> dict[str, Any]:
    selected = rows[keep].copy()
    traded_markets = int(rows["market"].nunique())
    selected_markets = int(selected["market"].nunique()) if not selected.empty else 0
    return {
        "trades": int(len(selected)),
        "trade_retention": float(len(selected) / len(rows)) if len(rows) else 0.0,
        "markets": selected_markets,
        "market_retention": float(selected_markets / traded_markets) if traded_markets else 0.0,
        "recurring_market_coverage": float(selected_markets / observed_markets) if observed_markets else 0.0,
        "negative_trades": int(selected["trade_negative"].sum()) if not selected.empty else 0,
        "settled_losses": int(selected["settled_loss"].sum()) if not selected.empty else 0,
        "net_pnl_dollars": float(selected["net_pnl_dollars"].sum()) if not selected.empty else 0.0,
        "cost_basis_dollars": float(selected["entry_notional_dollars"].astype(float).sum()) if not selected.empty else 0.0,
    }


def split_metrics(rows: pd.DataFrame, keep: pd.Series, observed_markets: int) -> dict[str, dict[str, Any]]:
    result: dict[str, dict[str, Any]] = {}
    for split in ["all", "train", "validation", "holdout"]:
        if split == "all":
            mask = pd.Series(True, index=rows.index)
        else:
            mask = rows["split"].eq(split)
        split_rows = rows[mask].copy()
        split_keep = keep.loc[split_rows.index] if not split_rows.empty else pd.Series(dtype=bool)
        result[split] = metrics(split_rows, split_keep, observed_markets)
    return result


def condition_candidates(rows: pd.DataFrame) -> list[Condition]:
    hard_thresholds: dict[str, list[tuple[str, float]]] = {
        "p_side": [
            (">=", 0.85),
            (">=", 0.86),
            (">=", 0.87),
            (">=", 0.88),
            (">=", 0.90),
            ("<=", 0.945),
        ],
        "edge_cents": [
            (">=", 2.1),
            (">=", 2.5),
            (">=", 3.0),
            (">=", 4.0),
            (">=", 5.0),
            (">=", 8.0),
        ],
        "ask_cents": [
            ("<=", 87.0),
            ("<=", 85.0),
            ("<=", 82.0),
            (">=", 60.0),
            (">=", 70.0),
        ],
        "seconds_to_close": [
            ("<=", 750.0),
            ("<=", 700.0),
            ("<=", 650.0),
            ("<=", 600.0),
            (">=", 180.0),
            (">=", 240.0),
        ],
        "abs_d_sigma": [
            (">=", 0.80),
            (">=", 0.85),
            ("<=", 1.35),
            ("<=", 1.20),
        ],
        "sigma_t_dollars": [
            ("<=", 175.0),
            ("<=", 150.0),
            ("<=", 135.0),
            (">=", 35.0),
        ],
        "btc_age_ms": [
            ("<=", 600.0),
            ("<=", 350.0),
            ("<=", 200.0),
        ],
        "eligible_depth": [
            (">=", 10.0),
            (">=", 25.0),
            (">=", 40.0),
            ("<=", 2000.0),
            ("<=", 1300.0),
            ("<=", 1000.0),
            ("<=", 500.0),
        ],
    }
    conditions: list[Condition] = []
    for column, specs in hard_thresholds.items():
        if column not in rows.columns or pd.to_numeric(rows[column], errors="coerce").notna().sum() < 20:
            continue
        for op, threshold in specs:
            conditions.append(Condition(f"{column}{op}{threshold:g}", column, op, threshold))
    return conditions


def candidate_specs(rows: pd.DataFrame) -> list[GuardSpec]:
    conditions = condition_candidates(rows)
    specs = [GuardSpec(condition.label, (condition,)) for condition in conditions]
    for i, first in enumerate(conditions):
        for second in conditions[i + 1 :]:
            if first.column == second.column and first.op == second.op:
                continue
            label = f"{first.label} AND {second.label}"
            specs.append(GuardSpec(label, (first, second)))
    return specs


def evaluate_guards(rows: pd.DataFrame, observed_markets: int) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    baseline_keep = pd.Series(True, index=rows.index)
    baseline = split_metrics(rows, baseline_keep, observed_markets)
    baseline_all = baseline["all"]

    candidates: list[dict[str, Any]] = []
    for spec in candidate_specs(rows):
        keep = spec.mask(rows)
        all_metrics = metrics(rows, keep, observed_markets)
        if all_metrics["trade_retention"] < MIN_TRADE_RETENTION:
            continue
        if all_metrics["market_retention"] < MIN_MARKET_RETENTION:
            continue
        splits = split_metrics(rows, keep, observed_markets)
        row = {
            "guard": spec.label,
            "trade_retention": all_metrics["trade_retention"],
            "market_retention": all_metrics["market_retention"],
            "recurring_market_coverage": all_metrics["recurring_market_coverage"],
            "trades": all_metrics["trades"],
            "markets": all_metrics["markets"],
            "net_pnl_dollars": all_metrics["net_pnl_dollars"],
            "net_delta_vs_baseline_dollars": all_metrics["net_pnl_dollars"] - baseline_all["net_pnl_dollars"],
            "negative_trades": all_metrics["negative_trades"],
            "negative_trades_delta": all_metrics["negative_trades"] - baseline_all["negative_trades"],
            "settled_losses": all_metrics["settled_losses"],
            "train_net": splits["train"]["net_pnl_dollars"],
            "validation_net": splits["validation"]["net_pnl_dollars"],
            "holdout_net": splits["holdout"]["net_pnl_dollars"],
            "train_retention": splits["train"]["trade_retention"],
            "validation_retention": splits["validation"]["trade_retention"],
            "holdout_retention": splits["holdout"]["trade_retention"],
            "strict_pass": bool(
                all_metrics["net_pnl_dollars"] > baseline_all["net_pnl_dollars"]
                and splits["validation"]["net_pnl_dollars"] >= 0.0
                and splits["holdout"]["net_pnl_dollars"] >= 0.0
                and splits["validation"]["trade_retention"] >= MIN_TRADE_RETENTION
                and splits["holdout"]["trade_retention"] >= MIN_TRADE_RETENTION
            ),
        }
        candidates.append(row)
    candidates.sort(
        key=lambda row: (
            row["strict_pass"],
            row["net_delta_vs_baseline_dollars"],
            row["holdout_net"],
            row["trade_retention"],
        ),
        reverse=True,
    )
    return baseline_all, candidates


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    fields = list(rows[0].keys())
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def fmt_pct(value: float) -> str:
    return f"{100.0 * value:.2f}%"


def write_report(path: Path, generated: str, rows: pd.DataFrame, baseline: dict[str, Any], candidates: list[dict[str, Any]], observed_markets: int) -> None:
    lines = [
        "# Live v28 Current Bot Loss Guard",
        "",
        f"Generated UTC: `{generated}`",
        "",
        "## Scope",
        "",
        "- Research-only audit of the current `live_mushroom_v28_size2` fill tape.",
        "- No orders are submitted and no live bot files or processes are touched.",
        "- Candidate guards are pre-entry only and must keep at least 80% of current v28 filled trades and filled markets.",
        "- This does not solve the separate requirement to trade 80% of all recurring BTC 15m markets; it only improves the current live bot's own filled-entry stream.",
        "",
        "## Baseline",
        "",
        f"- Matched filled trades: {len(rows)}",
        f"- Current v28 filled markets: {rows['market'].nunique()}",
        f"- Observed resolved recurring markets in scorer: {observed_markets}",
        f"- Current v28 recurring-market coverage: {fmt_pct(rows['market'].nunique() / observed_markets) if observed_markets else 'NA'}",
        f"- Net P&L: ${baseline['net_pnl_dollars']:.2f}",
        f"- Negative trades: {baseline['negative_trades']}",
        f"- Settled losses: {baseline['settled_losses']}",
        "",
        "## Top Guards",
        "",
        "| guard | strict | trades | trade ret | market ret | recurring cov | net | delta | neg trades | train/val/holdout net | val/hold ret |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for row in candidates[:20]:
        lines.append(
            f"| `{row['guard']}` | {row['strict_pass']} | {row['trades']} | {fmt_pct(row['trade_retention'])} | "
            f"{fmt_pct(row['market_retention'])} | {fmt_pct(row['recurring_market_coverage'])} | "
            f"${row['net_pnl_dollars']:.2f} | ${row['net_delta_vs_baseline_dollars']:.2f} | "
            f"{row['negative_trades']} ({row['negative_trades_delta']:+d}) | "
            f"${row['train_net']:.2f}/${row['validation_net']:.2f}/${row['holdout_net']:.2f} | "
            f"{fmt_pct(row['validation_retention'])}/{fmt_pct(row['holdout_retention'])} |"
        )
    if not candidates:
        lines.append("| none | False | 0 | 0.00% | 0.00% | 0.00% | $0.00 | $0.00 | 0 | $0.00/$0.00/$0.00 | 0.00%/0.00% |")
    strict_count = sum(1 for row in candidates if row["strict_pass"])
    lines += [
        "",
        "## Read",
        "",
        f"- Strict-pass guards: {strict_count}",
    ]
    if candidates:
        best = candidates[0]
        lines.append(
            f"- Best guard by this audit: `{best['guard']}` with ${best['net_delta_vs_baseline_dollars']:.2f} "
            f"delta at {fmt_pct(best['trade_retention'])} trade retention."
        )
    if strict_count == 0:
        lines.append("- No guard is promotion evidence; use this as loss-attribution until it survives future registered evidence.")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    generated = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%SZ")
    trades = load_trades()
    observed_markets = load_observed_market_count()
    events = load_v28_approval_events()
    rows = join_trade_features(trades, events)
    if rows.empty:
        raise SystemExit("No trade rows matched v28 approval events.")
    rows["split"] = split_labels(rows)
    baseline, candidates = evaluate_guards(rows, observed_markets)

    latest_csv = OUT_DIR / "live_v28_current_bot_loss_guard_latest.csv"
    stamp_csv = OUT_DIR / f"live_v28_current_bot_loss_guard_{generated}.csv"
    write_csv(latest_csv, candidates)
    write_csv(stamp_csv, candidates)

    latest_rows = OUT_DIR / "live_v28_current_bot_loss_guard_rows_latest.csv"
    rows.to_csv(latest_rows, index=False)

    payload = {
        "generated_utc": generated,
        "matched_trades": int(len(rows)),
        "current_v28_filled_markets": int(rows["market"].nunique()),
        "observed_resolved_recurring_markets": int(observed_markets),
        "current_v28_recurring_market_coverage": float(rows["market"].nunique() / observed_markets) if observed_markets else None,
        "baseline": baseline,
        "strict_pass_count": int(sum(1 for row in candidates if row["strict_pass"])),
        "top_candidates": candidates[:20],
    }
    json_latest = OUT_DIR / "live_v28_current_bot_loss_guard_latest.json"
    json_stamp = OUT_DIR / f"live_v28_current_bot_loss_guard_{generated}.json"
    json_latest.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    json_stamp.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    md_latest = OUT_DIR / "live_v28_current_bot_loss_guard_latest.md"
    md_stamp = OUT_DIR / f"live_v28_current_bot_loss_guard_{generated}.md"
    write_report(md_latest, generated, rows, baseline, candidates, observed_markets)
    write_report(md_stamp, generated, rows, baseline, candidates, observed_markets)

    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
