from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import duckdb
import pandas as pd

ROOT = Path(__file__).resolve().parent
DEFAULT_OUTPUT_PATH = ROOT / "logs" / "u_shape_recovery_exits_latest.json"


def load_cases(dataset_tag: str, *, entry_low: int, entry_high: int, seconds: int) -> pd.DataFrame:
    trades = pd.read_csv(ROOT / "stats" / dataset_tag / "trades.csv")
    market_results = pd.read_csv(ROOT / "stats" / dataset_tag / "market_results.csv")[["market", "result"]]
    work = trades.merge(market_results, on="market", how="left", suffixes=("_trade", "_market"))
    work = work[work["outcome"].astype(str).str.contains("exited_before_settlement", na=False)].copy()
    work = work[work["entry_trigger_cents"].between(entry_low, entry_high)].copy()

    feature_root = ROOT / "research_data" / dataset_tag / "features"
    feature_map = {
        path.parent.name.split("=", 1)[1]: str(path)
        for path in feature_root.rglob("part-latest.parquet")
    }
    work = work[work["market"].isin(feature_map)].copy()
    if work.empty:
        return pd.DataFrame()

    work["entry_dt_local"] = pd.to_datetime(work["entry_ts"]).dt.tz_localize("America/New_York")
    work["day"] = work["entry_dt_local"].dt.strftime("%Y-%m-%d")

    con = duckdb.connect()
    rows: list[dict[str, Any]] = []
    for _, row in work.sort_values("entry_dt_local").iterrows():
        feature_path = feature_map[str(row["market"])]
        quote_df = con.execute(
            f"select ts, yes_bid_cents, yes_ask_cents, no_bid_cents, no_ask_cents from read_parquet('{feature_path}') order by ts"
        ).df()
        quote_df["ts"] = pd.to_datetime(quote_df["ts"])
        side = str(row["side"]).lower()
        bid_col = "yes_bid_cents" if side == "yes" else "no_bid_cents"
        series = quote_df[["ts", bid_col]].rename(columns={bid_col: "same_bid"}).dropna()
        series = series[series["ts"] >= row["entry_dt_local"]].copy()
        if series.empty:
            continue

        horizon = row["entry_dt_local"] + pd.Timedelta(seconds=int(seconds))
        early = series[series["ts"] <= horizon].copy()
        if early.empty:
            continue

        entry_fill = (
            float(row["entry_fill_cents_used"])
            if pd.notna(row["entry_fill_cents_used"])
            else float(row["entry_trigger_cents"])
        )
        qty = float(row["qty"]) if pd.notna(row["qty"]) else 10.0
        final_result = str(row["result_market"] or "")
        target_hold = final_result.lower() == side
        settlement_pnl = qty * ((100.0 - entry_fill) / 100.0 if target_hold else (-entry_fill / 100.0))
        rows.append(
            {
                "market": str(row["market"]),
                "day": str(row["day"]),
                "side": side,
                "entry_fill_cents": entry_fill,
                "qty": qty,
                "stop_pnl_dollars": float(row["net_pnl_dollars"]),
                "settlement_pnl_dollars": float(settlement_pnl),
                "target_hold": bool(target_hold),
                "current_same_bid": float(early.iloc[-1]["same_bid"]),
                "low_same_bid": float(early["same_bid"].min()),
                "rebound_from_low": float(early.iloc[-1]["same_bid"] - early["same_bid"].min()),
                "post_path": [
                    {"ts": ts.isoformat(), "same_bid": float(bid)}
                    for ts, bid in series[series["ts"] > horizon][["ts", "same_bid"]].itertuples(index=False, name=None)
                ],
            }
        )

    return pd.DataFrame(rows)


def simulate_reclaim_exit(row: pd.Series, reclaim_cents: int) -> float:
    entry_fill = float(row["entry_fill_cents"])
    qty = float(row["qty"]) if pd.notna(row["qty"]) else 10.0
    post_path = row["post_path"] if isinstance(row["post_path"], list) else []
    for point in post_path:
        bid = point.get("same_bid")
        if isinstance(bid, (int, float)) and float(bid) >= float(reclaim_cents):
            return qty * ((float(bid) - entry_fill) / 100.0)
    return float(row["settlement_pnl_dollars"])


def evaluate_threshold(df: pd.DataFrame, *, threshold: float, reclaim_cents: int) -> dict[str, Any]:
    mask = df["current_same_bid"] >= float(threshold)
    sim_pnl = df["stop_pnl_dollars"].where(~mask, df.apply(simulate_reclaim_exit, axis=1, reclaim_cents=reclaim_cents))
    return {
        "threshold": float(threshold),
        "override_count": int(mask.sum()),
        "override_target_wins": int((mask & df["target_hold"]).sum()),
        "override_target_losses": int((mask & ~df["target_hold"]).sum()),
        "base_total_pnl_dollars": round(float(df["stop_pnl_dollars"].sum()), 4),
        "sim_total_pnl_dollars": round(float(sim_pnl.sum()), 4),
        "delta_dollars": round(float(sim_pnl.sum() - df["stop_pnl_dollars"].sum()), 4),
    }


def best_threshold(df: pd.DataFrame, *, reclaim_cents: int) -> dict[str, Any]:
    candidates = [
        evaluate_threshold(df, threshold=float(threshold), reclaim_cents=reclaim_cents)
        for threshold in sorted(x for x in df["current_same_bid"].dropna().unique())
    ]
    if not candidates:
        return {}
    return max(candidates, key=lambda item: float(item["delta_dollars"]))


def chronological_holdout(df: pd.DataFrame, *, reclaim_cents: int) -> dict[str, Any]:
    chron = df.sort_values(["day", "market"]).reset_index(drop=True)
    split = len(chron) // 2
    train = chron.iloc[:split].copy()
    test = chron.iloc[split:].copy()
    if train.empty or test.empty:
        return {}
    best = best_threshold(train, reclaim_cents=reclaim_cents)
    return {
        "train_size": int(len(train)),
        "test_size": int(len(test)),
        "train_best": best,
        "test_eval": evaluate_threshold(test, threshold=float(best["threshold"]), reclaim_cents=reclaim_cents),
    }


def day_walkforward(df: pd.DataFrame, *, reclaim_cents: int) -> dict[str, Any]:
    days = sorted(df["day"].unique().tolist())
    parts: list[dict[str, Any]] = []
    total_delta = 0.0
    for test_day in days:
        train = df[df["day"] < test_day].copy()
        test = df[df["day"] == test_day].copy()
        if train.empty or test.empty:
            continue
        best = best_threshold(train, reclaim_cents=reclaim_cents)
        test_eval = evaluate_threshold(test, threshold=float(best["threshold"]), reclaim_cents=reclaim_cents)
        total_delta += float(test_eval["delta_dollars"])
        parts.append({"test_day": str(test_day), "train_best": best, "test_eval": test_eval})
    return {"total_delta_dollars": round(total_delta, 4), "parts": parts}


def main() -> None:
    parser = argparse.ArgumentParser(description="Evaluate recovery-mode exits for U-shape stop overrides.")
    parser.add_argument("--dataset", default="live_90_70")
    parser.add_argument("--entry-low", type=int, default=89)
    parser.add_argument("--entry-high", type=int, default=91)
    parser.add_argument("--seconds", type=int, default=120)
    parser.add_argument("--reclaims", default="75,80,85,90")
    parser.add_argument("--output-path", default=str(DEFAULT_OUTPUT_PATH))
    args = parser.parse_args()

    df = load_cases(
        str(args.dataset),
        entry_low=int(args.entry_low),
        entry_high=int(args.entry_high),
        seconds=int(args.seconds),
    )
    reclaim_list = [int(chunk.strip()) for chunk in str(args.reclaims).split(",") if chunk.strip()]

    payload: dict[str, Any] = {
        "generated_at": pd.Timestamp.utcnow().isoformat(),
        "dataset": str(args.dataset),
        "entry_low": int(args.entry_low),
        "entry_high": int(args.entry_high),
        "seconds": int(args.seconds),
        "case_count": int(len(df)),
        "results": {},
    }
    for reclaim in reclaim_list:
        payload["results"][str(reclaim)] = {
            "best_in_sample": best_threshold(df, reclaim_cents=int(reclaim)),
            "chronological_holdout": chronological_holdout(df, reclaim_cents=int(reclaim)),
            "day_walkforward": day_walkforward(df, reclaim_cents=int(reclaim)),
        }

    output_path = Path(args.output_path)
    if not output_path.is_absolute():
        output_path = ROOT / output_path
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")

    print(f"Saved recovery exit probe to {output_path}")
    print(json.dumps(payload, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
