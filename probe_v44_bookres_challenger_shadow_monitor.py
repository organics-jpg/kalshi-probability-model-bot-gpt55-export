"""Strict-forward shadow monitor for the v44 book-residual challenger.

Candidate:
- FV surface: v41_v38_physics_book_residual_l230 with latent-hole full book
  posterior from the v44 fast probe.
- Entry: edge >= 1c, p_side >= 0.64, ask 1-100c, 0-780s to close.
- Exit: first later same-side heartbeat with adjusted p_side <= 0.50,
  otherwise settlement.

Research-only. Reads replay artifacts and writes a shadow registry. It does not
touch the live bot, live files, or order path.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

import probe_v38_edge_hole_shadow_monitor as shadow
from probe_market_interval_80coverage import clean_json


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
BASE_ROWS = OUT_DIR / "mushroom_v29_fv_surface_predictions_two_side_all_heartbeats_latest.csv"
V44_PREDICTIONS = OUT_DIR / "v44_physics_latent_hole_fv_strategy_fast_predictions_latest.csv"

POLICY = "v44_bookres_l230_holeblend100_edge1_p64_stc0_780_prob50"
MODEL_COL = "v44_v41_v38_bookres_l230_holeblend100_p_yes_candidate"
LOCK_PATH = OUT_DIR / "v44_bookres_challenger_shadow_lock.json"
REGISTRY_PATH = OUT_DIR / "v44_bookres_challenger_shadow_registry_latest.csv"
REPORT_MD = OUT_DIR / "v44_bookres_challenger_shadow_monitor_latest.md"
REPORT_JSON = OUT_DIR / "v44_bookres_challenger_shadow_monitor_latest.json"
DENOM_JSON = OUT_DIR / "v44_bookres_challenger_forward_denominator_latest.json"
DENOM_CSV = OUT_DIR / "v44_bookres_challenger_forward_denominator_latest.csv"

ENTRY_EDGE_FLOOR_CENTS = 1.0
ENTRY_P_SIDE_FLOOR = 0.64
ENTRY_ASK_FLOOR_CENTS = 1.0
ENTRY_ASK_CAP_CENTS = 100.0
ENTRY_MIN_STC = 0.0
ENTRY_MAX_STC = 780.0
EXIT_PROB_FLOOR = 0.50
QTY = shadow.QTY


def utc_now() -> pd.Timestamp:
    return pd.Timestamp(datetime.now(timezone.utc))


def load_or_create_lock() -> dict[str, Any]:
    if LOCK_PATH.exists():
        try:
            payload = json.loads(LOCK_PATH.read_text(encoding="utf-8"))
            if isinstance(payload, dict):
                return payload
        except json.JSONDecodeError:
            pass
    now = datetime.now(timezone.utc).isoformat()
    lock = {
        "lock_id": "v44_bookres_challenger_shadow_v1",
        "created_utc": now,
        "model_defined_utc": now,
        "policy": POLICY,
        "model_col": MODEL_COL,
        "entry": {
            "edge_floor_cents": ENTRY_EDGE_FLOOR_CENTS,
            "p_side_floor": ENTRY_P_SIDE_FLOOR,
            "ask_floor_cents": ENTRY_ASK_FLOOR_CENTS,
            "ask_cap_cents": ENTRY_ASK_CAP_CENTS,
            "min_seconds_to_close": ENTRY_MIN_STC,
            "max_seconds_to_close": ENTRY_MAX_STC,
        },
        "exit": {"probability_floor": EXIT_PROB_FLOOR},
        "purpose": "Strict-forward shadow validation of v44 high-PnL book-residual FV challenger.",
    }
    LOCK_PATH.write_text(json.dumps(clean_json(lock), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return lock


def load_rows() -> pd.DataFrame:
    usecols = {
        "opportunity_key",
        "entry_dt",
        "market",
        "side",
        "outcome",
        "win",
        "ask_cents",
        "bid_cents",
        "book_mid_cents",
        "seconds_to_close",
        "source_line_no",
        "split",
    }
    rows = pd.read_csv(BASE_ROWS, usecols=lambda col: col in usecols, low_memory=False)
    rows["entry_dt"] = pd.to_datetime(rows["entry_dt"], utc=True, errors="coerce")
    for col in ["ask_cents", "bid_cents", "book_mid_cents", "seconds_to_close", "source_line_no"]:
        if col in rows.columns:
            rows[col] = pd.to_numeric(rows[col], errors="coerce")
    rows["close_time"] = rows["entry_dt"] + pd.to_timedelta(rows["seconds_to_close"], unit="s")
    rows["win_bool"] = rows["win"].astype(str).str.lower().isin({"true", "1", "yes"})
    return rows.dropna(subset=["opportunity_key", "entry_dt", "market", "side", "ask_cents", "seconds_to_close"]).sort_values(
        ["market", "entry_dt", "side"]
    ).reset_index(drop=True)


def load_predictions() -> pd.DataFrame:
    preds = pd.read_csv(V44_PREDICTIONS, usecols=["opportunity_key", MODEL_COL], low_memory=False)
    preds[MODEL_COL] = pd.to_numeric(preds[MODEL_COL], errors="coerce").clip(1e-6, 1.0 - 1e-6)
    return preds.dropna(subset=["opportunity_key", MODEL_COL]).drop_duplicates("opportunity_key")


def merged_rows() -> pd.DataFrame:
    rows = load_rows()
    preds = load_predictions()
    out = rows.merge(preds, on="opportunity_key", how="inner")
    out["p_yes"] = pd.to_numeric(out[MODEL_COL], errors="coerce").clip(1e-6, 1.0 - 1e-6)
    out["p_side"] = np.where(out["side"].astype(str).eq("yes"), out["p_yes"], 1.0 - out["p_yes"])
    out["entry_edge_cents"] = 100.0 * out["p_side"] - out["ask_cents"]
    return out.dropna(subset=["p_yes", "p_side", "entry_edge_cents"]).copy()


def opportunity_table(rows: pd.DataFrame, lock: dict[str, Any]) -> pd.DataFrame:
    best = (
        rows.sort_values(["opportunity_key", "entry_edge_cents"], ascending=[True, False])
        .groupby("opportunity_key", as_index=False)
        .head(1)
        .sort_values(["market", "entry_dt"])
        .reset_index(drop=True)
    )
    model_dt = pd.to_datetime(lock.get("model_defined_utc"), utc=True, errors="coerce")
    if not pd.isna(model_dt):
        best = best[best["entry_dt"].gt(model_dt)].copy()
    if best.empty:
        return best
    best = best.rename(
        columns={
            "side": "selected_side",
            "ask_cents": "selected_ask_cents",
            "p_side": "selected_p_side",
            "entry_edge_cents": "selected_edge_cents",
        }
    )
    return best


def opportunity_candidates(rows: pd.DataFrame, lock: dict[str, Any]) -> pd.DataFrame:
    opps = opportunity_table(rows, lock)
    if opps.empty:
        return opps
    eligible = opps[
        opps["selected_edge_cents"].ge(ENTRY_EDGE_FLOOR_CENTS)
        & opps["selected_ask_cents"].ge(ENTRY_ASK_FLOOR_CENTS)
        & opps["selected_ask_cents"].le(ENTRY_ASK_CAP_CENTS)
        & opps["selected_p_side"].ge(ENTRY_P_SIDE_FLOOR)
        & opps["seconds_to_close"].ge(ENTRY_MIN_STC)
        & opps["seconds_to_close"].le(ENTRY_MAX_STC)
    ].copy()
    if eligible.empty:
        return eligible
    return eligible.sort_values(["market", "entry_dt"]).drop_duplicates("market", keep="first").sort_values(
        ["entry_dt", "market"]
    ).reset_index(drop=True)


def load_registry() -> pd.DataFrame:
    if not REGISTRY_PATH.exists() or REGISTRY_PATH.stat().st_size == 0:
        return pd.DataFrame(columns=shadow.REGISTRY_COLUMNS)
    try:
        rows = pd.read_csv(REGISTRY_PATH, low_memory=False)
    except pd.errors.EmptyDataError:
        return pd.DataFrame(columns=shadow.REGISTRY_COLUMNS)
    for col in shadow.REGISTRY_COLUMNS:
        if col not in rows.columns:
            rows[col] = pd.NA
    for col in ["entry_dt", "close_time", "registered_utc", "exit_dt", "resolved_utc"]:
        rows[col] = pd.to_datetime(rows[col], utc=True, errors="coerce")
    return rows[shadow.REGISTRY_COLUMNS]


def new_registry_rows(candidates: pd.DataFrame, lock: dict[str, Any], existing_markets: set[str]) -> pd.DataFrame:
    now = utc_now()
    rows = candidates.copy()
    model_dt = pd.to_datetime(lock.get("model_defined_utc"), utc=True, errors="coerce")
    if not pd.isna(model_dt):
        rows = rows[rows["entry_dt"].gt(model_dt)].copy()
    rows = rows[rows["close_time"].notna() & rows["close_time"].gt(rows["entry_dt"])].copy()
    rows = rows[~rows["market"].astype(str).isin(existing_markets)].copy()
    if rows.empty:
        return pd.DataFrame(columns=shadow.REGISTRY_COLUMNS)
    out = rows[
        [
            "market",
            "opportunity_key",
            "entry_dt",
            "close_time",
            "source_line_no",
            "selected_side",
            "selected_ask_cents",
            "selected_edge_cents",
            "selected_p_side",
            "p_yes",
        ]
    ].copy()
    out.insert(0, "policy", POLICY)
    out["registered_utc"] = now
    out["exit_dt"] = pd.NaT
    out["exit_bid_cents"] = pd.NA
    out["exit_p_side"] = pd.NA
    out["exit_fee_cents"] = 0.0
    out["outcome"] = ""
    out["resolved_utc"] = pd.NaT
    out["win"] = pd.NA
    out["gross_pnl_cents"] = pd.NA
    out["entry_fee_cents"] = out["selected_ask_cents"].map(shadow.estimate_fee_cents)
    out["total_fee_cents"] = pd.NA
    out["fee_net_cents"] = pd.NA
    out["fee_net_1c_entry_cents"] = pd.NA
    out["status"] = np.where(out["close_time"].gt(now), "open", "late_registered")
    return out[shadow.REGISTRY_COLUMNS]


def canonical_registry_rows(candidates: pd.DataFrame, lock: dict[str, Any], existing: pd.DataFrame) -> tuple[pd.DataFrame, int]:
    existing_markets = set(existing["market"].astype(str)) if not existing.empty else set()
    rows = new_registry_rows(candidates, lock, set())
    if rows.empty:
        return rows, 0
    new_count = int((~rows["market"].astype(str).isin(existing_markets)).sum())
    if not existing.empty and "registered_utc" in existing.columns:
        registered_lookup = (
            existing[["market", "registered_utc"]]
            .dropna(subset=["market"])
            .drop_duplicates("market", keep="first")
            .assign(market=lambda frame: frame["market"].astype(str))
            .set_index("market")["registered_utc"]
        )
        mapped = rows["market"].astype(str).map(registered_lookup)
        rows.loc[mapped.notna(), "registered_utc"] = mapped[mapped.notna()].to_numpy()
    return rows[shadow.REGISTRY_COLUMNS], new_count


def update_exits_and_outcomes(registry: pd.DataFrame, rows: pd.DataFrame) -> pd.DataFrame:
    if registry.empty:
        return registry
    out = registry.copy()
    out["status"] = out["status"].fillna("open").astype(str)
    resolved_at = utc_now()
    for idx, row in out.iterrows():
        status = str(row.get("status") or "open").lower()
        if status in {"exited", "settled"}:
            continue
        market = str(row["market"])
        selected_side = str(row["selected_side"]).lower()
        entry_dt = pd.Timestamp(row["entry_dt"])
        ask = float(row["selected_ask_cents"])
        future = rows[
            rows["market"].astype(str).eq(market)
            & rows["side"].astype(str).eq(selected_side)
            & rows["entry_dt"].gt(entry_dt)
            & rows["bid_cents"].notna()
            & rows["bid_cents"].ge(1.0)
        ].copy()
        if not future.empty:
            future["exit_p_side"] = np.where(future["side"].astype(str).eq("yes"), future["p_yes"], 1.0 - future["p_yes"])
            trigger = future[future["exit_p_side"].le(EXIT_PROB_FLOOR)].sort_values("entry_dt").head(1)
            if not trigger.empty:
                hit = trigger.iloc[0]
                bid = float(hit["bid_cents"])
                gross = (bid - ask) * QTY
                updates = shadow.finalize_row(row, gross, shadow.estimate_fee_cents(bid), "exited")
                for key, value in updates.items():
                    out.at[idx, key] = value
                out.at[idx, "exit_dt"] = hit["entry_dt"]
                out.at[idx, "exit_bid_cents"] = bid
                out.at[idx, "exit_p_side"] = float(hit["exit_p_side"])
                continue
        outcomes = rows[rows["market"].astype(str).eq(market)]["outcome"].dropna().astype(str).str.lower()
        outcome = outcomes[outcomes.isin(["yes", "no"])].iloc[0] if outcomes.isin(["yes", "no"]).any() else ""
        if outcome in {"yes", "no"}:
            win = selected_side == outcome
            settlement = 100.0 if win else 0.0
            gross = (settlement - ask) * QTY
            updates = shadow.finalize_row(row, gross, 0.0, "settled")
            for key, value in updates.items():
                out.at[idx, key] = value
            out.at[idx, "outcome"] = outcome
            out.at[idx, "resolved_utc"] = resolved_at
            out.at[idx, "win"] = bool(win)
    return out


def denominator_table(rows: pd.DataFrame, candidates: pd.DataFrame, registry: pd.DataFrame, lock: dict[str, Any]) -> tuple[pd.DataFrame, dict[str, Any]]:
    opps = opportunity_table(rows, lock)
    if opps.empty:
        payload = {
            "generated_utc": datetime.now(timezone.utc).isoformat(),
            "lock_model_defined_utc": lock.get("model_defined_utc"),
            "market_count": 0,
            "registered_count": 0,
            "registered_coverage": None,
            "classification_counts": {},
        }
        return pd.DataFrame(), payload
    opps["entry_filters_ok"] = (
        opps["selected_edge_cents"].ge(ENTRY_EDGE_FLOOR_CENTS)
        & opps["selected_ask_cents"].ge(ENTRY_ASK_FLOOR_CENTS)
        & opps["selected_ask_cents"].le(ENTRY_ASK_CAP_CENTS)
        & opps["selected_p_side"].ge(ENTRY_P_SIDE_FLOOR)
        & opps["seconds_to_close"].ge(ENTRY_MIN_STC)
        & opps["seconds_to_close"].le(ENTRY_MAX_STC)
    )
    table = (
        opps.groupby("market", as_index=False)
        .agg(
            first_seen_dt=("entry_dt", "min"),
            last_seen_dt=("entry_dt", "max"),
            close_time=("close_time", "max"),
            opportunity_rows=("opportunity_key", "count"),
            max_selected_p_side=("selected_p_side", "max"),
            max_selected_edge_cents=("selected_edge_cents", "max"),
            min_seconds_to_close=("seconds_to_close", "min"),
            max_seconds_to_close=("seconds_to_close", "max"),
        )
        .sort_values("first_seen_dt")
    )
    first_eligible = opps[opps["entry_filters_ok"]].sort_values(["market", "entry_dt"]).drop_duplicates("market", keep="first")
    table = table.merge(
        first_eligible[
            ["market", "entry_dt", "selected_side", "selected_ask_cents", "selected_edge_cents", "selected_p_side", "seconds_to_close"]
        ].rename(columns={"entry_dt": "first_eligible_dt", "seconds_to_close": "first_eligible_stc"}),
        on="market",
        how="left",
    )
    if not registry.empty:
        reg_cols = ["market", "entry_dt", "status", "fee_net_cents", "fee_net_1c_entry_cents", "outcome", "win"]
        reg = registry[[c for c in reg_cols if c in registry.columns]].copy().rename(columns={"entry_dt": "registered_entry_dt"})
        table = table.merge(reg, on="market", how="left")
    else:
        table["status"] = pd.NA
    table["classification"] = "no_entry_filters"
    table.loc[table["first_eligible_dt"].notna(), "classification"] = "eligible_unregistered"
    table.loc[table["status"].notna(), "classification"] = "registered"
    market_count = int(table["market"].nunique())
    registered_count = int(table["classification"].eq("registered").sum())
    payload = {
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "lock_model_defined_utc": lock.get("model_defined_utc"),
        "market_count": market_count,
        "registered_count": registered_count,
        "registered_coverage": float(registered_count / market_count) if market_count else None,
        "classification_counts": {str(k): int(v) for k, v in table["classification"].value_counts().to_dict().items()},
        "eligible_markets": int(candidates["market"].nunique()) if not candidates.empty else 0,
    }
    return table.sort_values("first_seen_dt").reset_index(drop=True), payload


def write_report(lock: dict[str, Any], registry: pd.DataFrame, denom_payload: dict[str, Any], new_count: int) -> None:
    final = registry[registry["status"].astype(str).str.lower().isin(["exited", "settled"])].copy() if not registry.empty else registry
    open_rows = registry[~registry["status"].astype(str).str.lower().isin(["exited", "settled"])].copy() if not registry.empty else registry
    fee_net = float(pd.to_numeric(final.get("fee_net_cents"), errors="coerce").fillna(0.0).sum()) if not final.empty else 0.0
    gross = float(pd.to_numeric(final.get("gross_pnl_cents"), errors="coerce").fillna(0.0).sum()) if not final.empty else 0.0
    fee_net_1c = float(pd.to_numeric(final.get("fee_net_1c_entry_cents"), errors="coerce").fillna(0.0).sum()) if not final.empty else 0.0
    cost = float(pd.to_numeric(final.get("selected_ask_cents"), errors="coerce").fillna(0.0).sum() * QTY) if not final.empty else 0.0
    exited = int(final["status"].astype(str).str.lower().eq("exited").sum()) if not final.empty else 0
    settled = int(final["status"].astype(str).str.lower().eq("settled").sum()) if not final.empty else 0
    wins = int(final["win"].astype(str).str.lower().eq("true").sum()) if not final.empty else 0
    losses = int(settled - wins)
    lines = [
        "# v44 Book-Residual Challenger Shadow Monitor",
        "",
        f"Generated UTC: `{datetime.now(timezone.utc).isoformat()}`",
        "",
        "## Scope",
        "",
        "- Strict-forward shadow validation of the v44 high-PnL FV challenger.",
        "- Registers only rows after the lock/model-defined timestamp.",
        "- No live bot code/process/orders are touched.",
        "",
        "## Lock",
        "",
        f"- Created UTC: `{lock.get('created_utc')}`",
        f"- Model defined UTC: `{lock.get('model_defined_utc')}`",
        f"- Policy: `{POLICY}`",
        "",
        "## Registry",
        "",
        f"- Registered shadow entries: {len(registry)}",
        f"- New entries this run: {new_count}",
        f"- Finalized / open: {len(final)} / {len(open_rows)}",
        f"- Exited / settled: {exited} / {settled}",
        f"- Post-lock observed markets: {denom_payload.get('market_count')}",
        f"- Registered coverage: {shadow.pct(denom_payload.get('registered_coverage'))}",
        "",
        "## Finalized Performance",
        "",
        f"- Settlement W/L for settled rows: {wins}/{losses}",
        f"- Gross P&L: {shadow.dollars_from_cents(gross)}",
        f"- Fee-adjusted P&L: {shadow.dollars_from_cents(fee_net)}",
        f"- Fee-adjusted with 1c entry haircut: {shadow.dollars_from_cents(fee_net_1c)}",
        f"- Fee-adjusted ROI on entry cost: {shadow.pct(fee_net / cost if cost > 0 else None)}",
        "",
        "## Read",
        "",
        "- Too few strict-forward finalized rows for a model decision." if len(final) < 30 else "- Review live-forward sample size and stability before any promotion.",
    ]
    REPORT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    lock = load_or_create_lock()
    rows = merged_rows()
    candidates = opportunity_candidates(rows, lock)
    existing_registry = load_registry()
    registry, new_count = canonical_registry_rows(candidates, lock, existing_registry)
    registry = update_exits_and_outcomes(registry, rows)
    registry = registry.sort_values(["entry_dt", "market"]).reset_index(drop=True) if not registry.empty else registry
    registry.to_csv(REGISTRY_PATH, index=False)
    denom, denom_payload = denominator_table(rows, candidates, registry, lock)
    denom.to_csv(DENOM_CSV, index=False)
    DENOM_JSON.write_text(json.dumps(clean_json(denom_payload), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    payload = {
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "lock": lock,
        "registered": int(len(registry)),
        "new_rows": int(new_count),
        "denominator": denom_payload,
    }
    REPORT_JSON.write_text(json.dumps(clean_json(payload), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_report(lock, registry, denom_payload, int(new_count))
    print("v44 book-residual challenger shadow monitor complete")
    print(f"registered={len(registry)} new_rows={new_count} report={REPORT_MD}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
