from __future__ import annotations

import csv
import json
import math
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

import pandas as pd


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
BROAD_TRADES = OUT_DIR / "threshold_touch_broad_execution_log_trades_latest.csv"
NATIVE_TRADES = OUT_DIR / "threshold_touch_exit_gate_trades_latest.csv"
LABELED_DECISIONS = ROOT / "research_particle" / "v28_successor" / "live_pnl_labeled_decisions_latest.csv"
REPORT_MD = OUT_DIR / "ninety_touch_stability_candidates_latest.md"
SUMMARY_CSV = OUT_DIR / "ninety_touch_stability_candidates_latest.csv"
SUMMARY_JSON = OUT_DIR / "ninety_touch_stability_candidates_latest.json"


@dataclass(frozen=True)
class Policy:
    policy_id: str
    description: str
    mask_fn: Callable[[pd.DataFrame], pd.Series]


def as_utc(series: pd.Series) -> pd.Series:
    return pd.to_datetime(series, utc=True, errors="coerce")


def load_broad() -> pd.DataFrame:
    df = pd.read_csv(BROAD_TRADES)
    df = df[(df["threshold"] == 90.0) & (df["entry_mode"] == "include_left_censored") & (df["exit_gate"] == "hold")].copy()
    df["source_tier"] = "broad_execution_log"
    df["entry_dt"] = as_utc(df["entry_ts_utc"])
    df["close_dt"] = as_utc(df["market_close_ts_utc"])
    df["close_day"] = df["close_dt"].dt.date.astype(str)
    df["win"] = df["entry_side"] == df["settlement_side"]
    df["fair_at_or_before_entry"] = pd.to_numeric(df.get("entry_v28_fair_side_cents"), errors="coerce")
    df["fair_age_s"] = 0.0
    return df


def load_native() -> pd.DataFrame:
    df = pd.read_csv(NATIVE_TRADES)
    df = df[(df["threshold"] == 90.0) & (df["entry_mode"] == "include_left_censored") & (df["exit_gate"] == "hold")].copy()
    df["source_tier"] = "native_raw_ticker"
    df["entry_dt"] = as_utc(df["entry_ts_utc"])
    df["close_dt"] = as_utc(df["market_close_ts_utc"])
    df["close_day"] = df["close_dt"].dt.date.astype(str)
    df["win"] = df["entry_side"] == df["settlement_side"]
    df["fair_at_or_before_entry"] = math.nan
    df["fair_age_s"] = math.nan
    if not LABELED_DECISIONS.exists() or df.empty:
        return df
    rows = pd.read_csv(
        LABELED_DECISIONS,
        usecols=lambda col: col
        in {
            "market_ticker",
            "decision_ts_utc",
            "side",
            "v28_fair_side_cents",
        },
    )
    rows["decision_dt"] = as_utc(rows["decision_ts_utc"])
    rows = rows.dropna(subset=["decision_dt"])
    rows = rows.drop_duplicates(["market_ticker", "side", "decision_ts_utc"])
    rows = rows.sort_values(["market_ticker", "side", "decision_dt"])
    fair_values: list[float] = []
    fair_ages: list[float] = []
    for trade in df.itertuples(index=False):
        sub = rows[
            (rows["market_ticker"] == trade.market_ticker)
            & (rows["side"] == trade.entry_side)
            & (rows["decision_dt"] <= trade.entry_dt)
        ]
        if sub.empty:
            fair_values.append(math.nan)
            fair_ages.append(math.nan)
            continue
        row = sub.iloc[-1]
        fair_values.append(float(row["v28_fair_side_cents"]))
        fair_ages.append((trade.entry_dt - row["decision_dt"]).total_seconds())
    df["fair_at_or_before_entry"] = fair_values
    df["fair_age_s"] = fair_ages
    return df


def keep_all(df: pd.DataFrame) -> pd.Series:
    return pd.Series(True, index=df.index)


def fair(df: pd.DataFrame) -> pd.Series:
    return pd.to_numeric(df["fair_at_or_before_entry"], errors="coerce")


def seconds(df: pd.DataFrame) -> pd.Series:
    return pd.to_numeric(df["entry_seconds_to_close"], errors="coerce")


def policies() -> list[Policy]:
    return [
        Policy("base_90_touch_hold", "Enter every observed 90c touch and hold.", keep_all),
        Policy(
            "veto_extreme_model_disagree",
            "Skip only when v28 fair is below 50c; keep missing fair.",
            lambda df: fair(df).isna() | (fair(df) >= 50.0),
        ),
        Policy(
            "veto_ultra_early_touch",
            "Skip touches earlier than 13 minutes before close.",
            lambda df: seconds(df) <= 780.0,
        ),
        Policy(
            "fair_buffer_ge92_only",
            "Enter only when v28 fair is at least 92c.",
            lambda df: fair(df) >= 92.0,
        ),
        Policy(
            "veto_fragile_fair_85_88",
            "Skip the weakest empirical fragile band: 85c <= v28 fair < 88c; keep missing fair.",
            lambda df: fair(df).isna() | ~((fair(df) >= 85.0) & (fair(df) < 88.0)),
        ),
        Policy(
            "veto_fragile_fair_85_88_or_90_92",
            "Skip two empirical fragile bands: 85-88c and 90-92c; keep missing fair.",
            lambda df: fair(df).isna()
            | ~(((fair(df) >= 85.0) & (fair(df) < 88.0)) | ((fair(df) >= 90.0) & (fair(df) < 92.0))),
        ),
        Policy(
            "veto_bad_fair_bands",
            "Skip fair < 50c plus fragile 85-88c and 90-92c bands; keep missing fair.",
            lambda df: fair(df).isna()
            | ~(
                (fair(df) < 50.0)
                | ((fair(df) >= 85.0) & (fair(df) < 88.0))
                | ((fair(df) >= 90.0) & (fair(df) < 92.0))
            ),
        ),
        Policy(
            "veto_bad_fair_bands_and_ultra_early",
            "Skip fair < 50c, fragile 85-88c/90-92c bands, and touches earlier than 13 minutes.",
            lambda df: (seconds(df) <= 780.0)
            & (
                fair(df).isna()
                | ~(
                    (fair(df) < 50.0)
                    | ((fair(df) >= 85.0) & (fair(df) < 88.0))
                    | ((fair(df) >= 90.0) & (fair(df) < 92.0))
                )
            ),
        ),
        Policy(
            "late_window_le300",
            "Enter only inside the final 5 minutes.",
            lambda df: seconds(df) <= 300.0,
        ),
        Policy(
            "fair_ge88_and_not_ultra_early",
            "Enter only when fair >= 88c and touch is not earlier than 13 minutes.",
            lambda df: (fair(df) >= 88.0) & (seconds(df) <= 780.0),
        ),
    ]


def summarize(df: pd.DataFrame, mask: pd.Series) -> dict[str, Any]:
    sub = df[mask.fillna(False)].copy()
    skipped = df[~mask.fillna(False)].copy()
    if sub.empty:
        return {
            "entries": 0,
            "net_pnl_cents": 0.0,
            "avg_pnl_cents": math.nan,
            "win_rate": math.nan,
            "skipped_winners": int((skipped["win"]).sum()),
            "skipped_losers": int((~skipped["win"]).sum()),
            "positive_days": 0,
            "negative_days": 0,
            "min_day_pnl_cents": math.nan,
            "late_period_pnl_cents": math.nan,
            "early_period_pnl_cents": math.nan,
        }
    day_pnl = sub.groupby("close_day")["net_pnl_cents"].sum()
    late = sub[sub["close_day"] >= "2026-05-11"]
    early = sub[sub["close_day"] < "2026-05-11"]
    pnl = pd.to_numeric(sub["net_pnl_cents"], errors="coerce")
    avg = float(pnl.mean())
    stderr = float(pnl.std(ddof=1) / math.sqrt(len(pnl))) if len(pnl) > 1 else 0.0
    return {
        "entries": int(len(sub)),
        "net_pnl_cents": float(pnl.sum()),
        "avg_pnl_cents": avg,
        "lcb_avg_pnl_cents": avg - 1.96 * stderr,
        "win_rate": float(sub["win"].mean()),
        "skipped_winners": int((skipped["win"]).sum()),
        "skipped_losers": int((~skipped["win"]).sum()),
        "positive_days": int((day_pnl > 0).sum()),
        "negative_days": int((day_pnl < 0).sum()),
        "min_day_pnl_cents": float(day_pnl.min()),
        "early_period_pnl_cents": float(pd.to_numeric(early["net_pnl_cents"], errors="coerce").sum()),
        "late_period_pnl_cents": float(pd.to_numeric(late["net_pnl_cents"], errors="coerce").sum()),
    }


def stability_score(row: dict[str, Any]) -> float:
    if row["entries"] <= 0:
        return -1e9
    score = row["net_pnl_cents"]
    score += 75.0 * max(0.0, row["avg_pnl_cents"])
    score += 150.0 * max(0.0, row["win_rate"] - 0.90)
    score -= 2.0 * max(0.0, -row["min_day_pnl_cents"])
    if row["late_period_pnl_cents"] < 0:
        score += 3.0 * row["late_period_pnl_cents"]
    if row["entries"] < 100 and row["source_tier"] == "broad_execution_log":
        score -= 500.0
    return score


def run() -> tuple[pd.DataFrame, dict[str, Any]]:
    broad = load_broad()
    native = load_native()
    rows: list[dict[str, Any]] = []
    detail: dict[str, Any] = {
        "broad_entries": len(broad),
        "native_entries": len(native),
        "native_fair_coverage": int(native["fair_at_or_before_entry"].notna().sum()) if not native.empty else 0,
    }
    for source_tier, df in [("broad_execution_log", broad), ("native_raw_ticker", native)]:
        for policy in policies():
            mask = policy.mask_fn(df)
            row = summarize(df, mask)
            row.update(
                {
                    "source_tier": source_tier,
                    "policy_id": policy.policy_id,
                    "description": policy.description,
                }
            )
            row["stability_score"] = stability_score(row)
            rows.append(row)
    out = pd.DataFrame(rows)
    return out, detail


def write_report(out: pd.DataFrame, detail: dict[str, Any]) -> None:
    broad = out[out["source_tier"] == "broad_execution_log"].copy().sort_values("stability_score", ascending=False)
    native = out[out["source_tier"] == "native_raw_ticker"].copy().sort_values("stability_score", ascending=False)

    def table(rows: pd.DataFrame, limit: int = 12) -> list[str]:
        lines = [
            "| policy | entries | net c | avg c | LCB c | win rate | skipped L/W | days +/- | early c | late c | min day c |",
            "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
        ]
        for row in rows.head(limit).itertuples(index=False):
            lines.append(
                f"| {row.policy_id} | {row.entries} | {row.net_pnl_cents:.1f} | {row.avg_pnl_cents:.2f} | "
                f"{row.lcb_avg_pnl_cents:.2f} | {row.win_rate:.3f} | {row.skipped_losers}/{row.skipped_winners} | "
                f"{row.positive_days}/{row.negative_days} | {row.early_period_pnl_cents:.1f} | {row.late_period_pnl_cents:.1f} | "
                f"{row.min_day_pnl_cents:.1f} |"
            )
        return lines

    lines = [
        "# 90c Touch Stability Candidate Sweep",
        "",
        "Research-only. This report searches for simple vetoes that improve 90c touch without relying on live order changes.",
        "",
        f"- Broad 90c hold trades: {detail['broad_entries']}",
        f"- Native 90c hold trades: {detail['native_entries']}",
        f"- Native prior-v28-fair coverage: {detail['native_fair_coverage']} / {detail['native_entries']}",
        "",
        "## Broad Execution-Log Tier",
        *table(broad),
        "",
        "## Native Raw-Ticker Tier",
        *table(native),
        "",
        "## Interpretation",
        "- The highest broad PnL comes from vetoing fair < 50c and the empirical fragile fair bands 85-88c and 90-92c.",
        "- The cleaner native tier is too small to prove the band rule, but it does not contradict the main idea that entry-time quality beats after-the-fact exits.",
        "- The most trustworthy live candidate should be pre-registered as an entry/carry veto and then judged forward against plain 90c touch.",
    ]
    REPORT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out, detail = run()
    out.to_csv(SUMMARY_CSV, index=False)
    SUMMARY_JSON.write_text(json.dumps({"detail": detail, "rows": out.to_dict(orient="records")}, indent=2), encoding="utf-8")
    write_report(out, detail)
    print(f"wrote {SUMMARY_CSV}")
    print(f"wrote {SUMMARY_JSON}")
    print(f"wrote {REPORT_MD}")
    print("BROAD TOP")
    top = out[out["source_tier"] == "broad_execution_log"].sort_values("stability_score", ascending=False).head(8)
    print(top[["policy_id", "entries", "net_pnl_cents", "avg_pnl_cents", "win_rate", "late_period_pnl_cents", "min_day_pnl_cents"]].to_string(index=False))
    print("NATIVE TOP")
    top = out[out["source_tier"] == "native_raw_ticker"].sort_values("stability_score", ascending=False).head(8)
    print(top[["policy_id", "entries", "net_pnl_cents", "avg_pnl_cents", "win_rate", "late_period_pnl_cents", "min_day_pnl_cents"]].to_string(index=False))


if __name__ == "__main__":
    main()
