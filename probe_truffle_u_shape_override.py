from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import duckdb
import pandas as pd
import requests

from probe_truffle_ambiguity_router import extract_json_object
from truffle_regime_lease import load_prompt_text, resolve_truffle_chat_completion_endpoint, resolve_truffle_model_id

ROOT = Path(__file__).resolve().parent
DEFAULT_PROMPT_PATH = ROOT / "truffle_u_shape_override_prompt.txt"
DEFAULT_OUTPUT_PATH = ROOT / "logs" / "truffle_u_shape_override_latest.json"
VALID_DECISIONS = {"HOLD_OVERRIDE", "KEEP_STOP"}


def issue_u_shape_decision(
    payload: dict[str, Any],
    *,
    endpoint: str,
    model: str,
    timeout_ms: int,
    prompt_text: str,
    max_tokens: int,
) -> dict[str, Any]:
    resolved_endpoint = resolve_truffle_chat_completion_endpoint(endpoint)
    resolved_model = resolve_truffle_model_id(model, endpoint=resolved_endpoint, timeout_ms=timeout_ms) or model
    response = requests.post(
        resolved_endpoint,
        headers={"Content-Type": "application/json"},
        json={
            "model": resolved_model,
            "temperature": 0,
            "max_tokens": int(max_tokens),
            "response_format": {"type": "json_object"},
            "messages": [
                {"role": "system", "content": prompt_text},
                {"role": "user", "content": json.dumps(payload, sort_keys=True)},
            ],
        },
        timeout=max(1.0, float(timeout_ms) / 1000.0),
    )
    response.raise_for_status()
    body = response.json()
    content = ""
    finish_reason = ""
    if isinstance(body, dict):
        choices = body.get("choices")
        if isinstance(choices, list) and choices:
            choice = choices[0] if isinstance(choices[0], dict) else {}
            finish_reason = str(choice.get("finish_reason") or "")
            message = choice.get("message") if isinstance(choice, dict) else None
            if isinstance(message, dict):
                content = str(message.get("content") or "")
    parsed = extract_json_object(content)
    return {
        "parsed": parsed,
        "content": content,
        "finish_reason": finish_reason,
    }


def build_post_entry_snapshots(dataset_tag: str, *, seconds: int, entry_low: int, entry_high: int) -> pd.DataFrame:
    trades = pd.read_csv(ROOT / "stats" / dataset_tag / "trades.csv")
    market_results = pd.read_csv(ROOT / "stats" / dataset_tag / "market_results.csv")[["market", "result"]]
    work = trades.merge(market_results, on="market", how="left", suffixes=("_trade", "_market"))
    work = work[work["outcome"].astype(str).str.contains("exited_before_settlement", na=False)].copy()
    work = work[work["entry_trigger_cents"].between(entry_low, entry_high)].copy()

    feature_map = {
        path.parent.name.split("=", 1)[1]: str(path)
        for path in (ROOT / "research_data" / dataset_tag / "features").rglob("part-latest.parquet")
    }
    work = work[work["market"].isin(feature_map)].copy()
    if work.empty:
        return pd.DataFrame()

    work["entry_dt_local"] = pd.to_datetime(work["entry_ts"]).dt.tz_localize("America/New_York")
    work["exit_dt_local"] = pd.to_datetime(work["exit_ts"], errors="coerce").dt.tz_localize("America/New_York")

    rows: list[dict[str, Any]] = []
    con = duckdb.connect()
    for _, row in work.sort_values("entry_dt_local").iterrows():
        feature_path = feature_map[str(row["market"])]
        quote_df = con.execute(
            f"select ts, yes_bid_cents, yes_ask_cents, no_bid_cents, no_ask_cents from read_parquet('{feature_path}') order by ts"
        ).df()
        quote_df["ts"] = pd.to_datetime(quote_df["ts"])
        side = str(row["side"]).lower()
        bid_col = "yes_bid_cents" if side == "yes" else "no_bid_cents"
        ask_col = "yes_ask_cents" if side == "yes" else "no_ask_cents"
        series = quote_df[["ts", bid_col, ask_col]].rename(columns={bid_col: "same_bid", ask_col: "same_ask"}).dropna()
        series = series[series["ts"] >= row["entry_dt_local"]].copy()
        if series.empty:
            continue
        horizon = row["entry_dt_local"] + pd.Timedelta(seconds=int(seconds))
        sub = series[series["ts"] <= horizon].copy()
        if sub.empty:
            continue
        entry_fill = float(row["entry_fill_cents_used"]) if pd.notna(row["entry_fill_cents_used"]) else float(row["entry_trigger_cents"])
        qty = float(row["qty"]) if pd.notna(row["qty"]) else 10.0
        final_result = str(row["result_market"] or "")
        target_hold = final_result.lower() == side
        settlement_pnl_est = qty * ((100.0 - entry_fill) / 100.0 if target_hold else (-entry_fill / 100.0))
        low_bid = float(sub["same_bid"].min())
        current_bid = float(sub.iloc[-1]["same_bid"])
        current_ask = float(sub.iloc[-1]["same_ask"])
        rows.append(
            {
                "market": row["market"],
                "side": side,
                "entry_dt_local": row["entry_dt_local"].isoformat(),
                "exit_dt_local": row["exit_dt_local"].isoformat() if pd.notna(row["exit_dt_local"]) else "",
                "entry_fill_cents": entry_fill,
                "current_same_bid_120s": current_bid,
                "current_same_ask_120s": current_ask,
                "low_same_bid_120s": low_bid,
                "high_same_bid_120s": float(sub["same_bid"].max()),
                "drop_from_entry_120s": round(entry_fill - low_bid, 4),
                "rebound_from_low_to_current_120s": round(current_bid - low_bid, 4),
                "end_vs_entry_120s": round(current_bid - entry_fill, 4),
                "current_spread_120s": round(current_ask - current_bid, 4),
                "normal_stop_exit_fill_cents": float(row["exit_fill_cents_used"]) if pd.notna(row["exit_fill_cents_used"]) else None,
                "current_stop_net_pnl_dollars": float(row["net_pnl_dollars"]),
                "final_result": final_result,
                "target_hold_override": bool(target_hold),
                "settlement_pnl_est_dollars": round(settlement_pnl_est, 4),
            }
        )
    return pd.DataFrame(rows)


def summarize(results_df: pd.DataFrame) -> dict[str, Any]:
    if results_df.empty:
        return {
            "case_count": 0,
            "hold_override_count": 0,
            "current_total_pnl_dollars": 0.0,
            "sim_total_pnl_dollars": 0.0,
            "delta_dollars": 0.0,
        }
    hold_df = results_df[results_df["final_decision"] == "HOLD_OVERRIDE"]
    return {
        "case_count": int(len(results_df)),
        "hold_override_count": int(len(hold_df)),
        "current_total_pnl_dollars": round(float(results_df["current_stop_net_pnl_dollars"].sum()), 4),
        "sim_total_pnl_dollars": round(float(results_df["sim_pnl_dollars"].sum()), 4),
        "delta_dollars": round(
            float(results_df["sim_pnl_dollars"].sum() - results_df["current_stop_net_pnl_dollars"].sum()),
            4,
        ),
        "override_target_wins": int((hold_df["target_hold_override"] == True).sum()),
        "override_target_losses": int((hold_df["target_hold_override"] == False).sum()),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Probe Truffle as a U-shape stop-override classifier.")
    parser.add_argument("--dataset", default="live_90_70")
    parser.add_argument("--model", default="Qwen3.5-2B")
    parser.add_argument("--endpoint", default="")
    parser.add_argument("--prompt-path", default=str(DEFAULT_PROMPT_PATH))
    parser.add_argument("--timeout-ms", type=int, default=20000)
    parser.add_argument("--max-tokens", type=int, default=100)
    parser.add_argument("--seconds", type=int, default=120)
    parser.add_argument("--entry-low", type=int, default=89)
    parser.add_argument("--entry-high", type=int, default=91)
    parser.add_argument("--output-path", default=str(DEFAULT_OUTPUT_PATH))
    args = parser.parse_args()

    prompt_text = load_prompt_text(Path(args.prompt_path))
    snapshot_df = build_post_entry_snapshots(
        str(args.dataset),
        seconds=int(args.seconds),
        entry_low=int(args.entry_low),
        entry_high=int(args.entry_high),
    )
    rows: list[dict[str, Any]] = []
    for _, row in snapshot_df.iterrows():
        payload = {
            "schema_version": "u_shape_override_input_v1",
            "seconds_since_entry": int(args.seconds),
            "market": row["market"],
            "side": row["side"],
            "entry_fill_cents": float(row["entry_fill_cents"]),
            "current_same_bid_120s": float(row["current_same_bid_120s"]),
            "current_same_ask_120s": float(row["current_same_ask_120s"]),
            "low_same_bid_120s": float(row["low_same_bid_120s"]),
            "high_same_bid_120s": float(row["high_same_bid_120s"]),
            "drop_from_entry_120s": float(row["drop_from_entry_120s"]),
            "rebound_from_low_to_current_120s": float(row["rebound_from_low_to_current_120s"]),
            "end_vs_entry_120s": float(row["end_vs_entry_120s"]),
            "current_spread_120s": float(row["current_spread_120s"]),
        }
        response = issue_u_shape_decision(
            payload,
            endpoint=str(args.endpoint),
            model=str(args.model),
            timeout_ms=int(args.timeout_ms),
            prompt_text=prompt_text,
            max_tokens=int(args.max_tokens),
        )
        parsed = response.get("parsed") if isinstance(response, dict) else None
        decision = str(parsed.get("decision") or "").strip() if isinstance(parsed, dict) else ""
        if decision not in VALID_DECISIONS:
            decision = "KEEP_STOP"
        sim_pnl = float(row["current_stop_net_pnl_dollars"])
        if decision == "HOLD_OVERRIDE":
            sim_pnl = float(row["settlement_pnl_est_dollars"])
        rows.append(
            {
                **row.to_dict(),
                "router_payload": payload,
                "final_decision": decision,
                "confidence": parsed.get("confidence") if isinstance(parsed, dict) else None,
                "rationale_code": parsed.get("rationale_code") if isinstance(parsed, dict) else "",
                "summary_reason": parsed.get("summary_reason") if isinstance(parsed, dict) else "",
                "finish_reason": str(response.get("finish_reason") or ""),
                "parsed_ok": bool(isinstance(parsed, dict)),
                "sim_pnl_dollars": round(sim_pnl, 4),
            }
        )

    results_df = pd.DataFrame(rows)
    payload = {
        "generated_at": pd.Timestamp.utcnow().isoformat(),
        "dataset": args.dataset,
        "model": args.model,
        "prompt_path": str(Path(args.prompt_path).resolve()),
        "seconds": int(args.seconds),
        "entry_low": int(args.entry_low),
        "entry_high": int(args.entry_high),
        "summary": summarize(results_df),
        "rows": rows,
    }

    output_path = Path(args.output_path)
    if not output_path.is_absolute():
        output_path = ROOT / output_path
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")

    print(f"Saved Truffle U-shape override probe to {output_path}")
    print(payload["summary"])


if __name__ == "__main__":
    main()
