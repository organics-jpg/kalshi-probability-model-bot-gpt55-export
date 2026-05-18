"""Edge-hole latent-state FV strategy probe.

Research-only. Tests whether the v38 edge-hole regime is better represented as
a fair-value probability correction instead of only an entry veto.

Hypothesis: a first qualifying raw-v38 edge in the mid-high band is not
monotonic extra edge. It is a hidden-state warning that the book is measuring a
path/liquidity condition missing from the pure FV surface. Candidate surfaces
therefore shrink or flatten v38 probabilities when that latent state appears.

No live bot files, processes, or order paths are touched.
"""
from __future__ import annotations

import json
import math
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

import probe_v39_entry_exit_strategy_projection as base
from probe_market_interval_80coverage import clean_json
from probe_v31_book_calibrated_probability import logit, sigmoid


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
INPUT = OUT_DIR / "mushroom_v29_fv_surface_predictions_two_side_all_heartbeats_latest.csv"
REPORT_MD = OUT_DIR / "v42_edgehole_latent_fv_strategy_latest.md"
REPORT_JSON = OUT_DIR / "v42_edgehole_latent_fv_strategy_latest.json"
SUMMARY_CSV = OUT_DIR / "v42_edgehole_latent_fv_strategy_summary_latest.csv"
PREDICTIONS_CSV = OUT_DIR / "v42_edgehole_latent_fv_predictions_latest.csv"
TRADES_CSV = OUT_DIR / "v42_edgehole_latent_fv_selected_trades_latest.csv"

MODEL = "v38_long60_antipersist"
PROB_EPS = 1e-6
MIN_SPLIT_COVERAGE = 0.80
ASK_FLOOR_CENTS = 1.0

ENTRY_POLICIES = [
    base.EntryPolicy(edge, 100.0, pside, max_stc, min_stc)
    for edge in [-2.0, 0.0, 1.0]
    for pside in [0.64, 0.65, 0.66]
    for max_stc in [570.0, 600.0, 780.0]
    for min_stc in [0.0, 60.0, 120.0]
    if min_stc < max_stc
]

EXIT_POLICIES = [
    base.ExitPolicy("hold"),
    base.ExitPolicy("prob50", probability_floor=0.50),
    base.ExitPolicy("prob52", probability_floor=0.52),
    base.ExitPolicy("prob54", probability_floor=0.54),
    base.ExitPolicy("prob56", probability_floor=0.56),
]


def pct(value: Any) -> str:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return "NA"
    if not math.isfinite(number):
        return "NA"
    return f"{100.0 * number:.2f}%"


def dollars(value: Any) -> str:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return "NA"
    if not math.isfinite(number):
        return "NA"
    return f"${number:.2f}"


def dollars_cents(value: Any) -> str:
    try:
        return f"${float(value) / 100.0:.2f}"
    except (TypeError, ValueError):
        return "NA"


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
        "split",
        f"{MODEL}_p_yes",
    }
    rows = pd.read_csv(INPUT, usecols=lambda col: col in usecols, low_memory=False)
    rows["entry_dt"] = pd.to_datetime(rows["entry_dt"], utc=True, errors="coerce")
    for col in ["ask_cents", "bid_cents", "book_mid_cents", "seconds_to_close", f"{MODEL}_p_yes"]:
        rows[col] = pd.to_numeric(rows[col], errors="coerce")
    rows["win_bool"] = rows["win"].astype(str).str.lower().isin({"true", "1", "yes"})
    return rows.dropna(subset=["opportunity_key", "entry_dt", "market", "side", "ask_cents", "seconds_to_close", "split"]).sort_values(
        ["market", "entry_dt", "side"]
    ).reset_index(drop=True)


def opportunity_table(rows: pd.DataFrame) -> pd.DataFrame:
    yes = rows[rows["side"].astype(str).eq("yes")].drop_duplicates("opportunity_key").copy()
    piv = rows.pivot_table(
        index="opportunity_key",
        columns="side",
        values=["ask_cents", "book_mid_cents"],
        aggfunc="first",
    )
    piv.columns = [f"{side}_{field}" for field, side in piv.columns]
    out = yes.merge(piv, left_on="opportunity_key", right_index=True, how="left")
    out = out.rename(columns={"yes_book_mid_cents": "yes_mid", "no_book_mid_cents": "no_mid"})
    denom = out["yes_mid"] + out["no_mid"]
    out["book_mid_p_yes"] = (out["yes_mid"] / denom).clip(PROB_EPS, 1.0 - PROB_EPS)
    out["v38_p_yes"] = pd.to_numeric(out[f"{MODEL}_p_yes"], errors="coerce").clip(PROB_EPS, 1.0 - PROB_EPS)
    out["outcome_yes"] = out["outcome"].astype(str).str.lower().eq("yes").astype(float)
    out["yes_edge_raw"] = 100.0 * out["v38_p_yes"] - out["yes_ask_cents"]
    out["no_edge_raw"] = 100.0 * (1.0 - out["v38_p_yes"]) - out["no_ask_cents"]
    yes_better = out["yes_edge_raw"].ge(out["no_edge_raw"])
    out["selected_side_raw"] = np.where(yes_better, "yes", "no")
    out["selected_ask_raw"] = np.where(yes_better, out["yes_ask_cents"], out["no_ask_cents"])
    out["selected_p_side_raw"] = np.where(yes_better, out["v38_p_yes"], 1.0 - out["v38_p_yes"])
    out["selected_edge_raw"] = np.where(yes_better, out["yes_edge_raw"], out["no_edge_raw"])
    return out.dropna(
        subset=[
            "opportunity_key",
            "entry_dt",
            "market",
            "split",
            "book_mid_p_yes",
            "v38_p_yes",
            "outcome_yes",
            "yes_ask_cents",
            "no_ask_cents",
            "selected_edge_raw",
        ]
    ).reset_index(drop=True)


def qualifying_mask(ops: pd.DataFrame, *, edge_floor: float, p_floor: float, min_stc: float, max_stc: float) -> pd.Series:
    return (
        ops["selected_edge_raw"].ge(edge_floor)
        & ops["selected_ask_raw"].ge(ASK_FLOOR_CENTS)
        & ops["selected_ask_raw"].le(100.0)
        & ops["selected_p_side_raw"].ge(p_floor)
        & ops["seconds_to_close"].ge(min_stc)
        & ops["seconds_to_close"].le(max_stc)
    )


def first_hole_markets(ops: pd.DataFrame, *, edge_floor: float, p_floor: float, min_stc: float, max_stc: float, low: float, high: float) -> dict[str, pd.Timestamp]:
    elig = ops[qualifying_mask(ops, edge_floor=edge_floor, p_floor=p_floor, min_stc=min_stc, max_stc=max_stc)].copy()
    if elig.empty:
        return {}
    first = elig.sort_values(["market", "entry_dt"]).drop_duplicates("market", keep="first").copy()
    hole = first[first["selected_edge_raw"].gt(low) & first["selected_edge_raw"].le(high)]
    return {str(row.market): pd.Timestamp(row.entry_dt) for row in hole.itertuples(index=False)}


def side_adjusted_p_yes(row: pd.Series, new_p_side: float) -> float:
    if str(row["selected_side_raw"]) == "yes":
        return float(np.clip(new_p_side, PROB_EPS, 1.0 - PROB_EPS))
    return float(np.clip(1.0 - new_p_side, PROB_EPS, 1.0 - PROB_EPS))


def cap_selected_edge(ops: pd.DataFrame, *, low: float, high: float, cap: float) -> pd.Series:
    out = ops["v38_p_yes"].copy()
    mask = (
        ops["selected_edge_raw"].gt(low)
        & ops["selected_edge_raw"].le(high)
        & ops["selected_p_side_raw"].ge(0.65)
        & ops["seconds_to_close"].between(0.0, 600.0)
    )
    capped_side_p = ((ops.loc[mask, "selected_ask_raw"] + cap) / 100.0).clip(PROB_EPS, 1.0 - PROB_EPS)
    for idx, value in capped_side_p.items():
        out.loc[idx] = side_adjusted_p_yes(ops.loc[idx], float(value))
    return out.clip(PROB_EPS, 1.0 - PROB_EPS)


def blend_on_band(ops: pd.DataFrame, *, low: float, high: float, weight: float) -> pd.Series:
    out = ops["v38_p_yes"].copy()
    mask = (
        ops["selected_edge_raw"].gt(low)
        & ops["selected_edge_raw"].le(high)
        & ops["selected_p_side_raw"].ge(0.65)
        & ops["seconds_to_close"].between(0.0, 600.0)
    )
    raw_l = logit(out.loc[mask])
    book_l = logit(ops.loc[mask, "book_mid_p_yes"])
    out.loc[mask] = sigmoid((1.0 - weight) * raw_l + weight * book_l)
    return out.clip(PROB_EPS, 1.0 - PROB_EPS)


def latent_after_first_hole(ops: pd.DataFrame, *, mode: str, weight: float = 1.0) -> pd.Series:
    out = ops["v38_p_yes"].copy()
    holes = first_hole_markets(ops, edge_floor=-2.0, p_floor=0.65, min_stc=60.0, max_stc=600.0, low=8.0, high=20.0)
    if not holes:
        return out
    for market, first_dt in holes.items():
        mask = ops["market"].astype(str).eq(market) & ops["entry_dt"].ge(first_dt)
        if mode == "flat":
            out.loc[mask] = 0.5
        elif mode == "book":
            out.loc[mask] = ops.loc[mask, "book_mid_p_yes"]
        elif mode == "book_blend":
            raw_l = logit(out.loc[mask])
            book_l = logit(ops.loc[mask, "book_mid_p_yes"])
            out.loc[mask] = sigmoid((1.0 - weight) * raw_l + weight * book_l)
        else:
            raise ValueError(f"unknown latent mode {mode}")
    return out.clip(PROB_EPS, 1.0 - PROB_EPS)


def build_probability_candidates(ops: pd.DataFrame) -> tuple[pd.DataFrame, list[str], dict[str, Any]]:
    out = ops.copy()
    out["v38_raw_p_yes_candidate"] = out["v38_p_yes"]
    out["v42_band_cap_edge0_p_yes_candidate"] = cap_selected_edge(out, low=8.0, high=20.0, cap=0.0)
    out["v42_band_cap_edge-2_p_yes_candidate"] = cap_selected_edge(out, low=8.0, high=20.0, cap=-2.0)
    out["v42_band_bookblend50_p_yes_candidate"] = blend_on_band(out, low=8.0, high=20.0, weight=0.50)
    out["v42_band_bookblend80_p_yes_candidate"] = blend_on_band(out, low=8.0, high=20.0, weight=0.80)
    out["v42_latent_hole_flat_p_yes_candidate"] = latent_after_first_hole(out, mode="flat")
    out["v42_latent_hole_book_p_yes_candidate"] = latent_after_first_hole(out, mode="book")
    out["v42_latent_hole_bookblend80_p_yes_candidate"] = latent_after_first_hole(out, mode="book_blend", weight=0.80)
    candidate_cols = [col for col in out.columns if col.endswith("_p_yes_candidate")]
    metadata = {
        "latent_hole_markets": len(first_hole_markets(out, edge_floor=-2.0, p_floor=0.65, min_stc=60.0, max_stc=600.0, low=8.0, high=20.0)),
        "band_rows": int(
            (
                out["selected_edge_raw"].gt(8.0)
                & out["selected_edge_raw"].le(20.0)
                & out["selected_p_side_raw"].ge(0.65)
                & out["seconds_to_close"].between(0.0, 600.0)
            ).sum()
        ),
    }
    return out, candidate_cols, metadata


def probability_metrics(ops: pd.DataFrame, candidate_cols: list[str]) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for col in candidate_cols:
        for split in ["train", "validation", "holdout", "all"]:
            part = ops if split == "all" else ops[ops["split"].eq(split)]
            y = part["outcome_yes"].to_numpy(dtype=float)
            p = np.clip(part[col].to_numpy(dtype=float), PROB_EPS, 1.0 - PROB_EPS)
            records.append(
                {
                    "candidate": col.replace("_p_yes_candidate", ""),
                    "split": split,
                    "rows": int(len(part)),
                    "brier": float(np.mean((p - y) ** 2)),
                    "logloss": float(-(y * np.log(p) + (1.0 - y) * np.log(1.0 - p)).mean()),
                    "side_accuracy": float(((p >= 0.5) == (y >= 0.5)).mean()),
                    "mean_p_yes": float(p.mean()),
                    "yes_rate": float(y.mean()),
                }
            )
    return records


def frame_for_candidate(rows: pd.DataFrame, ops: pd.DataFrame, candidate_col: str) -> pd.DataFrame:
    probs = ops[["opportunity_key", candidate_col]].rename(columns={candidate_col: "p_yes"})
    frame = rows.merge(probs, on="opportunity_key", how="inner")
    frame["model"] = candidate_col.replace("_p_yes_candidate", "")
    frame["p_yes"] = pd.to_numeric(frame["p_yes"], errors="coerce").clip(PROB_EPS, 1.0 - PROB_EPS)
    frame["p_side"] = np.where(frame["side"].astype(str).eq("yes"), frame["p_yes"], 1.0 - frame["p_yes"])
    frame["entry_edge_cents"] = 100.0 * frame["p_side"] - frame["ask_cents"]
    frame["fair_side_cents"] = 100.0 * frame["p_side"]
    return frame.dropna(subset=["p_yes", "p_side", "entry_edge_cents"]).copy()


def choose_entries(best_opp: pd.DataFrame, policy: base.EntryPolicy) -> pd.DataFrame:
    eligible = best_opp[
        best_opp["entry_edge_cents"].ge(policy.edge_floor_cents)
        & best_opp["ask_cents"].ge(ASK_FLOOR_CENTS)
        & best_opp["ask_cents"].le(policy.ask_cap_cents)
        & best_opp["p_side"].ge(policy.min_p_side)
        & best_opp["seconds_to_close"].le(policy.max_seconds_to_close)
        & best_opp["seconds_to_close"].ge(policy.min_seconds_to_close)
    ].copy()
    if eligible.empty:
        return eligible
    return eligible.sort_values(["market", "entry_dt"]).drop_duplicates("market", keep="first").reset_index(drop=True)


def row_1c_positive(record: dict[str, Any]) -> bool:
    return all(float(record[f"{split}_net_after_fees_1c_entry_dollars"]) > 0.0 for split in ["train", "validation", "holdout"])


def day_metrics(trades: pd.DataFrame) -> dict[str, Any]:
    if trades.empty:
        return {"positive_days": 0, "total_days": 0, "worst_day_cents": None}
    rows = trades.copy()
    rows["entry_day_utc"] = pd.to_datetime(rows["entry_dt"], utc=True, errors="coerce").dt.strftime("%Y-%m-%d")
    rows["fee_net_1c_entry_cents"] = rows["pnl_cents"] - rows["total_fee_cents"] - base.QTY
    values = rows.groupby("entry_day_utc")["fee_net_1c_entry_cents"].sum().to_numpy(dtype=float)
    return {
        "positive_days": int((values > 0).sum()),
        "total_days": int(len(values)),
        "worst_day_cents": float(values.min()) if len(values) else None,
    }


def block_metrics(trades: pd.DataFrame, blocks: int) -> dict[str, Any]:
    if trades.empty:
        return {"positive_blocks": 0, "worst_cents": None}
    ordered = trades.sort_values(["entry_dt", "market"]).reset_index(drop=True)
    values = [
        float((ordered.iloc[idx]["pnl_cents"] - ordered.iloc[idx]["total_fee_cents"] - base.QTY).sum())
        for idx in np.array_split(np.arange(len(ordered)), blocks)
        if len(idx)
    ]
    return {"positive_blocks": int(sum(v > 0 for v in values)), "worst_cents": float(min(values)) if values else None}


def build_strategy(rows: pd.DataFrame, ops: pd.DataFrame, candidate_cols: list[str]) -> tuple[pd.DataFrame, pd.DataFrame]:
    universes = base.market_universes(rows)
    records: list[dict[str, Any]] = []
    selected_trade_frames: list[pd.DataFrame] = []
    frame_cache: dict[str, pd.DataFrame] = {}
    paths_cache: dict[str, dict[tuple[str, str], base.QuotePath]] = {}
    best_cache: dict[str, pd.DataFrame] = {}

    for col in candidate_cols:
        frame = frame_for_candidate(rows, ops, col)
        frame_cache[col] = frame
        best_cache[col] = base.best_side_per_opportunity(frame)
        paths_cache[col] = base.quote_paths(frame)
        for entry_policy in ENTRY_POLICIES:
            entries = choose_entries(best_cache[col], entry_policy)
            if entries.empty:
                continue
            min_coverage = min(
                len(set(entries["market"].astype(str)) & universes[split]) / len(universes[split])
                for split in ["train", "validation", "holdout"]
            )
            if min_coverage < MIN_SPLIT_COVERAGE:
                continue
            for exit_policy in EXIT_POLICIES:
                trades = base.simulate(entries, paths_cache[col], exit_policy)
                if trades.empty:
                    continue
                record = base.flatten_metrics(str(frame["model"].iloc[0]), entry_policy, exit_policy, trades, universes)
                record["min_split_net_after_fees_1c_entry_dollars"] = float(
                    min(record[f"{split}_net_after_fees_1c_entry_dollars"] for split in ["train", "validation", "holdout"])
                )
                record["all_splits_1c_entry_positive"] = row_1c_positive(record)
                days = day_metrics(trades)
                record["positive_1c_days"] = days["positive_days"]
                record["total_days"] = days["total_days"]
                record["worst_1c_day_cents"] = days["worst_day_cents"]
                block10 = block_metrics(trades, 10)
                record["block10_positive"] = block10["positive_blocks"]
                record["block10_worst_cents"] = block10["worst_cents"]
                records.append(record)

    summary = pd.DataFrame(records)
    if summary.empty:
        return summary, pd.DataFrame()

    selected = selected_rows(summary)
    for _, row in selected.head(12).iterrows():
        col = f"{row['model']}_p_yes_candidate"
        entry = base.EntryPolicy(
            float(row["entry_edge_floor_cents"]),
            float(row["entry_ask_cap_cents"]),
            float(row["entry_min_p_side"]),
            float(row["entry_max_seconds_to_close"]),
            float(row["entry_min_seconds_to_close"]),
        )
        exit_policy = exit_policy_from_name(str(row["exit_policy"]))
        trades = base.simulate(choose_entries(best_cache[col], entry), paths_cache[col], exit_policy)
        trades["entry_policy"] = row["entry_policy"]
        trades["exit_policy"] = row["exit_policy"]
        selected_trade_frames.append(trades)
    selected_trades = pd.concat(selected_trade_frames, ignore_index=True, sort=False) if selected_trade_frames else pd.DataFrame()
    return summary, selected_trades


def exit_policy_from_name(name: str) -> base.ExitPolicy:
    if name == "hold":
        return base.ExitPolicy("hold")
    if name.startswith("prob"):
        return base.ExitPolicy(name, probability_floor=float(name.replace("prob", "")) / 100.0)
    raise ValueError(f"Unknown exit policy: {name}")


def selected_rows(summary: pd.DataFrame) -> pd.DataFrame:
    eligible = summary[summary["min_split_coverage"].ge(MIN_SPLIT_COVERAGE)].copy()
    if eligible.empty:
        return eligible
    pieces: list[pd.DataFrame] = []
    robust = eligible[eligible["all_splits_1c_entry_positive"] & eligible["positive_1c_days"].eq(eligible["total_days"])].copy()
    if not robust.empty:
        pieces.append(
            robust.sort_values(
                ["min_split_net_after_fees_1c_entry_dollars", "worst_1c_day_cents", "all_net_after_fees_1c_entry_dollars"],
                ascending=[False, False, False],
            ).head(30)
        )
    split_positive = eligible[eligible["all_splits_1c_entry_positive"]].copy()
    if not split_positive.empty:
        pieces.append(
            split_positive.sort_values(
                ["min_split_net_after_fees_1c_entry_dollars", "all_net_after_fees_1c_entry_dollars"],
                ascending=[False, False],
            ).head(30)
        )
    pieces.append(
        eligible.sort_values(
            ["min_split_net_after_fees_1c_entry_dollars", "positive_1c_days", "all_net_after_fees_1c_entry_dollars"],
            ascending=[False, False, False],
        ).head(30)
    )
    return pd.concat(pieces, ignore_index=True, sort=False).drop_duplicates(["model", "entry_policy", "exit_policy"])


def write_report(
    summary: pd.DataFrame,
    selected: pd.DataFrame,
    prob_records: list[dict[str, Any]],
    metadata: dict[str, Any],
    candidate_cols: list[str],
) -> None:
    generated = datetime.now(timezone.utc).isoformat()
    eligible = summary[summary["min_split_coverage"].ge(MIN_SPLIT_COVERAGE)].copy() if not summary.empty else summary
    one_cent = eligible[eligible["all_splits_1c_entry_positive"]].copy() if not eligible.empty else eligible
    all_day = one_cent[one_cent["positive_1c_days"].eq(one_cent["total_days"])].copy() if not one_cent.empty else one_cent
    holdout_prob = pd.DataFrame(prob_records)
    holdout_prob = holdout_prob[holdout_prob["split"].eq("holdout")].sort_values(["brier", "logloss"]).head(12)

    lines = [
        "# v42 Edge-Hole Latent FV Strategy",
        "",
        f"Generated UTC: `{generated}`",
        "",
        "## Scope",
        "",
        "- Research-only probability transformation probe on top of v38.",
        "- Tests edge-hole as a latent fair-value state, not only an explicit entry veto.",
        "- Strategy projection requires at least 80% coverage in every chronological split.",
        "- Live bot untouched.",
        "",
        "## Data Notes",
        "",
        f"- Latent first-hole markets under all-day rule: {metadata.get('latent_hole_markets')}",
        f"- Opportunity rows in local 8-20 edge band: {metadata.get('band_rows')}",
        "",
        "## Probability Holdout",
        "",
        "| candidate | rows | Brier | logloss | side acc | mean p_yes | yes rate |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for _, row in holdout_prob.iterrows():
        lines.append(
            f"| `{row['candidate']}` | {int(row['rows'])} | {float(row['brier']):.5f} | "
            f"{float(row['logloss']):.5f} | {pct(row['side_accuracy'])} | "
            f"{pct(row['mean_p_yes'])} | {pct(row['yes_rate'])} |"
        )
    lines += [
        "",
        "## Strategy Search",
        "",
        f"- Candidate probability surfaces: {len(candidate_cols)}",
        f"- Rows evaluated after 80% coverage prefilter: {len(summary)}",
        f"- Fee+1c positive train/validation/holdout rows: {len(one_cent)}",
        f"- Fee+1c positive across all UTC days rows: {len(all_day)}",
        "",
        "## Selected Strategy Rows",
        "",
        "| model | entry | exit | min cov | min 1c | all 1c | all fee | gross | days | block10 | trades |",
        "|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for _, row in selected.head(35).iterrows():
        lines.append(
            f"| `{row['model']}` | `{row['entry_policy']}` | `{row['exit_policy']}` | "
            f"{pct(row['min_split_coverage'])} | {dollars(row['min_split_net_after_fees_1c_entry_dollars'])} | "
            f"{dollars(row['all_net_after_fees_1c_entry_dollars'])} | {dollars(row['all_net_after_fees_dollars'])} | "
            f"{dollars(row['all_pnl_dollars'])} | {int(row['positive_1c_days'])}/{int(row['total_days'])} | "
            f"{int(row['block10_positive'])}/10 | {int(row['all_trades'])} |"
        )
    lines += ["", "## Read", ""]
    if one_cent.empty:
        lines.append("- No v42 latent FV transform cleared split-positive fee+1c P&L at 80% split coverage.")
    else:
        best = one_cent.sort_values(
            ["min_split_net_after_fees_1c_entry_dollars", "all_net_after_fees_1c_entry_dollars"],
            ascending=[False, False],
        ).iloc[0]
        lines.append(
            f"- Best split-positive v42 row is `{best['model']}` / `{best['entry_policy']}` / `{best['exit_policy']}` "
            f"with min split fee+1c {dollars(best['min_split_net_after_fees_1c_entry_dollars'])}."
        )
    if not all_day.empty:
        best_day = all_day.sort_values(
            ["min_split_net_after_fees_1c_entry_dollars", "all_net_after_fees_1c_entry_dollars"],
            ascending=[False, False],
        ).iloc[0]
        lines.append(
            f"- Best all-day-positive v42 row is `{best_day['model']}` / `{best_day['entry_policy']}` / `{best_day['exit_policy']}` "
            f"with min split fee+1c {dollars(best_day['min_split_net_after_fees_1c_entry_dollars'])}."
        )
    lines.append("- Compare this with the explicit-veto all-day v38 row before treating it as a candidate replacement.")

    REPORT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")
    REPORT_JSON.write_text(
        json.dumps(
            clean_json(
                {
                    "generated_utc": generated,
                    "candidate_count": len(candidate_cols),
                    "summary_rows": int(len(summary)),
                    "one_cent_positive_rows": int(len(one_cent)),
                    "all_day_positive_rows": int(len(all_day)),
                    "metadata": metadata,
                    "probability_records": prob_records,
                    "selected": selected.to_dict("records"),
                }
            ),
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )


def main() -> int:
    rows = load_rows()
    ops = opportunity_table(rows)
    ops, candidate_cols, metadata = build_probability_candidates(ops)
    prob_records = probability_metrics(ops, candidate_cols)
    summary, selected_trades = build_strategy(rows, ops, candidate_cols)
    summary.to_csv(SUMMARY_CSV, index=False)
    ops[["opportunity_key", "entry_dt", "market", "split", *candidate_cols]].to_csv(PREDICTIONS_CSV, index=False)
    selected = selected_rows(summary) if not summary.empty else summary
    if not selected_trades.empty:
        selected_trades.to_csv(TRADES_CSV, index=False)
    write_report(summary, selected, prob_records, metadata, candidate_cols)
    one_cent = summary[summary["all_splits_1c_entry_positive"]] if not summary.empty else summary
    print("v42 edge-hole latent FV strategy complete")
    print(f"summary_rows={len(summary)} one_cent_rows={len(one_cent)} report={REPORT_MD}")
    if not selected.empty:
        best = selected.iloc[0]
        print(
            f"best={best['model']} {best['entry_policy']} {best['exit_policy']} "
            f"min_1c={float(best['min_split_net_after_fees_1c_entry_dollars']):.2f} "
            f"all_1c={float(best['all_net_after_fees_1c_entry_dollars']):.2f} "
            f"coverage={float(best['min_split_coverage']):.4f}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
