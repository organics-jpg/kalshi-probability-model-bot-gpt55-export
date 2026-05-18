"""v64 analog audit for the fresh 97c NO forward loss.

Research-only. Replays the v57-style v55 entry/hold15/prob52 exit and slices
historical entries that resemble the fresh forward failure: expensive, tiny-edge,
high-confidence late entries.

No live bot files, processes, or order paths are touched.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd

import probe_v39_entry_exit_strategy_projection as base
import probe_v42_edgehole_latent_fv_strategy as v42
import probe_v47_recross_hazard_fv_strategy as v47
import probe_v55_book_anchor_recross_fv_strategy as v55
from probe_market_interval_80coverage import clean_json


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
REPORT_MD = OUT_DIR / "v64_forward_loss_analog_audit_latest.md"
REPORT_JSON = OUT_DIR / "v64_forward_loss_analog_audit_latest.json"
SLICE_CSV = OUT_DIR / "v64_forward_loss_analog_slices_latest.csv"
ANALOG_CSV = OUT_DIR / "v64_forward_loss_analog_trades_latest.csv"

MODEL = "v55_bookanchor_m10_v20_g05_book_plus2"
MODEL_COL = f"{MODEL}_p_yes_candidate"
ENTRY = base.EntryPolicy(0.0, 100.0, 0.65, 600.0, 0.0)
EXIT = base.ExitPolicy("hold15_prob52", probability_floor=0.52, min_hold_seconds=15.0)


def fee_1c_cents(rows: pd.DataFrame) -> pd.Series:
    return pd.to_numeric(rows["pnl_cents"], errors="coerce").fillna(0.0) - pd.to_numeric(
        rows["total_fee_cents"], errors="coerce"
    ).fillna(0.0) - base.QTY


def summarize(rows: pd.DataFrame, label: str) -> dict[str, Any]:
    if rows.empty:
        return {
            "slice": label,
            "trades": 0,
            "fee_1c_dollars": 0.0,
            "avg_fee_1c_cents": None,
            "exits": 0,
            "settled": 0,
            "wins": 0,
            "losses": 0,
            "no_trades": 0,
            "yes_trades": 0,
        }
    settled = rows["settled"].astype(bool)
    win = rows["win"].astype(bool)
    return {
        "slice": label,
        "trades": int(len(rows)),
        "fee_1c_dollars": float(fee_1c_cents(rows).sum() / 100.0),
        "avg_fee_1c_cents": float(fee_1c_cents(rows).mean()),
        "exits": int((~settled).sum()),
        "settled": int(settled.sum()),
        "wins": int(win.sum()),
        "losses": int((~win).sum()),
        "no_trades": int(rows["side"].astype(str).eq("no").sum()),
        "yes_trades": int(rows["side"].astype(str).eq("yes").sum()),
        "avg_ask": float(pd.to_numeric(rows["entry_ask_cents"], errors="coerce").mean()),
        "avg_edge": float(pd.to_numeric(rows["entry_edge_cents"], errors="coerce").mean()),
        "avg_p_side": float(pd.to_numeric(rows["entry_p_side"], errors="coerce").mean()),
        "avg_stc": float(pd.to_numeric(rows["entry_seconds_to_close"], errors="coerce").mean()),
    }


def build_trades() -> pd.DataFrame:
    rows = v47.load_rows()
    ops = v42.opportunity_table(rows)
    ops, _, _ = v55.build_probability_candidates(ops)
    frame = v42.frame_for_candidate(rows, ops, MODEL_COL)
    best = base.best_side_per_opportunity(frame)
    entries = v42.choose_entries(best, ENTRY)
    paths = base.quote_paths(frame)
    trades = base.simulate(entries, paths, EXIT)
    enrich_cols = [
        "market",
        "entry_dt",
        "side",
        "margin_per_rv_sigma_15m",
        "signed_velocity_dps_1m",
        "signed_velocity_dps_3m",
        "book_mid_p_yes",
        "raw_p_yes",
        "recross_side_margin_sigma15",
        "recross_side_velocity_3m",
        "thin_edge_certainty_active",
        "recross_hazard_active",
        "book_anchor_recross_active",
    ]
    available = [col for col in enrich_cols if col in entries.columns]
    enriched = trades.merge(entries[available], on=["market", "entry_dt", "side"], how="left")
    enriched["fee_1c_cents"] = fee_1c_cents(enriched)
    return enriched


def slice_masks(trades: pd.DataFrame) -> list[tuple[str, pd.Series]]:
    ask = pd.to_numeric(trades["entry_ask_cents"], errors="coerce")
    edge = pd.to_numeric(trades["entry_edge_cents"], errors="coerce")
    p_side = pd.to_numeric(trades["entry_p_side"], errors="coerce")
    stc = pd.to_numeric(trades["entry_seconds_to_close"], errors="coerce")
    side = trades["side"].astype(str)
    return [
        ("all_v57_style", pd.Series(True, index=trades.index)),
        ("ask>=95_edge<=2_stc120_600", ask.ge(95.0) & edge.le(2.0) & stc.between(120.0, 600.0)),
        ("ask>=95_edge<=2_p>=95_stc120_600", ask.ge(95.0) & edge.le(2.0) & p_side.ge(0.95) & stc.between(120.0, 600.0)),
        (
            "NO_ask>=95_edge<=2_p>=95_stc120_600",
            side.eq("no") & ask.ge(95.0) & edge.le(2.0) & p_side.ge(0.95) & stc.between(120.0, 600.0),
        ),
        (
            "NO_ask>=95_edge<=2_p>=95_stc120_450",
            side.eq("no") & ask.ge(95.0) & edge.le(2.0) & p_side.ge(0.95) & stc.between(120.0, 450.0),
        ),
        (
            "NO_ask>=97_edge<=1p5_p>=98_stc120_450",
            side.eq("no") & ask.ge(97.0) & edge.le(1.5) & p_side.ge(0.98) & stc.between(120.0, 450.0),
        ),
        (
            "YES_ask>=95_edge<=2_p>=95_stc120_600",
            side.eq("yes") & ask.ge(95.0) & edge.le(2.0) & p_side.ge(0.95) & stc.between(120.0, 600.0),
        ),
        ("ask>=97_edge<=1p5_stc120_450", ask.ge(97.0) & edge.le(1.5) & stc.between(120.0, 450.0)),
    ]


def write_report(trades: pd.DataFrame, slices: pd.DataFrame, analogs: pd.DataFrame) -> None:
    generated = datetime.now(timezone.utc).isoformat()

    def money(value: Any) -> str:
        try:
            return f"${float(value):.2f}"
        except (TypeError, ValueError):
            return "NA"

    lines = [
        "# v64 Forward Loss Analog Audit",
        "",
        f"Generated UTC: `{generated}`",
        "",
        "## Scope",
        "",
        "- Research-only historical analog audit for the fresh 97c NO forward loss.",
        "- Replays v55 entry with v57-style hold15/prob52 exit.",
        "- Live bot untouched.",
        "",
        "## Slices",
        "",
        "| slice | trades | fee+1c | avg c | exits | settled | wins | losses | NO/YES | avg ask | avg edge | avg p | avg stc |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for _, row in slices.iterrows():
        lines.append(
            f"| `{row['slice']}` | {int(row['trades'])} | {money(row['fee_1c_dollars'])} | "
            f"{'' if pd.isna(row['avg_fee_1c_cents']) else f'{float(row['avg_fee_1c_cents']):.1f}'} | "
            f"{int(row['exits'])} | {int(row['settled'])} | {int(row['wins'])} | {int(row['losses'])} | "
            f"{int(row['no_trades'])}/{int(row['yes_trades'])} | "
            f"{'' if pd.isna(row.get('avg_ask')) else f'{float(row['avg_ask']):.1f}'} | "
            f"{'' if pd.isna(row.get('avg_edge')) else f'{float(row['avg_edge']):.2f}'} | "
            f"{'' if pd.isna(row.get('avg_p_side')) else f'{float(row['avg_p_side']):.3f}'} | "
            f"{'' if pd.isna(row.get('avg_stc')) else f'{float(row['avg_stc']):.1f}'} |"
        )
    lines += [
        "",
        "## Exact Analog Rows",
        "",
        "| market | split | side | ask | edge | p_side | stc | exit | fee+1c | outcome |",
        "|---|---|---|---:|---:|---:|---:|---|---:|---|",
    ]
    for _, row in analogs.head(30).iterrows():
        lines.append(
            f"| `{row['market']}` | `{row['split']}` | `{row['side']}` | "
            f"{float(row['entry_ask_cents']):.0f} | {float(row['entry_edge_cents']):.2f} | "
            f"{float(row['entry_p_side']):.3f} | {float(row['entry_seconds_to_close']):.1f} | "
            f"`{row['exit_type']}` | {money(float(row['fee_1c_cents']) / 100.0)} | `{row['outcome']}` |"
        )
    lines += ["", "## Read", ""]
    exact = slices[slices["slice"].eq("NO_ask>=95_edge<=2_p>=95_stc120_450")]
    if not exact.empty and float(exact.iloc[0]["fee_1c_dollars"]) < 0.0:
        lines.append("- Exact NO-side analogs are historically negative; this subset deserves a narrow model/entry treatment.")
    else:
        lines.append("- Exact NO-side analogs are not historically negative enough to justify a narrow veto from this audit alone.")
    lines.append("- Any follow-up should preserve the 75-80% coverage requirement and be strict-forward validated.")
    REPORT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")
    REPORT_JSON.write_text(
        json.dumps(
            clean_json(
                {
                    "generated_utc": generated,
                    "slice_records": json.loads(slices.to_json(orient="records", date_format="iso")),
                    "exact_analogs": json.loads(analogs.to_json(orient="records", date_format="iso")),
                    "total_trades": int(len(trades)),
                }
            ),
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )


def main() -> int:
    trades = build_trades()
    records = []
    masks = slice_masks(trades)
    for label, mask in masks:
        records.append(summarize(trades[mask].copy(), label))
    slices = pd.DataFrame(records)
    exact_mask = dict(masks)["NO_ask>=95_edge<=2_p>=95_stc120_450"]
    analogs = trades[exact_mask].sort_values("fee_1c_cents").copy()
    slices.to_csv(SLICE_CSV, index=False)
    analogs.to_csv(ANALOG_CSV, index=False)
    write_report(trades, slices, analogs)
    print("v64 forward loss analog audit complete")
    print(f"report={REPORT_MD}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
