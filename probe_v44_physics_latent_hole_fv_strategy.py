"""v44 physics posterior plus latent-hole FV strategy probe.

Research-only. This tests whether the best-calibrated v41 physics/book
posterior can be made more tradeable by treating the v38 edge-hole pattern as a
hidden market state rather than as an explicit entry veto.

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
import probe_v41_physics_path_posterior_strategy as v41
import probe_v42_edgehole_latent_fv_strategy as v42
from probe_market_interval_80coverage import clean_json
from probe_v31_book_calibrated_probability import logit, sigmoid


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
REPORT_MD = OUT_DIR / "v44_physics_latent_hole_fv_strategy_latest.md"
REPORT_JSON = OUT_DIR / "v44_physics_latent_hole_fv_strategy_latest.json"
SUMMARY_CSV = OUT_DIR / "v44_physics_latent_hole_fv_strategy_summary_latest.csv"
PREDICTIONS_CSV = OUT_DIR / "v44_physics_latent_hole_fv_predictions_latest.csv"
TRADES_CSV = OUT_DIR / "v44_physics_latent_hole_fv_selected_trades_latest.csv"

PROB_EPS = 1e-6
MIN_SPLIT_COVERAGE = 0.80
ASK_FLOOR_CENTS = 1.0

ENTRY_POLICIES = [
    base.EntryPolicy(edge, ask, pside, max_stc, min_stc)
    for edge in [-3.0, -2.0, 0.0, 1.0, 2.0]
    for ask in [100.0, 95.0]
    for pside in [0.60, 0.62, 0.64, 0.65]
    for max_stc in [600.0, 780.0, 900.0]
    for min_stc in [0.0, 60.0, 120.0]
    if min_stc < max_stc
]

EXIT_POLICIES = [
    base.ExitPolicy("hold"),
    base.ExitPolicy("prob50", probability_floor=0.50),
    base.ExitPolicy("prob52", probability_floor=0.52),
    base.ExitPolicy("prob54", probability_floor=0.54),
    base.ExitPolicy("prob56", probability_floor=0.56),
    base.ExitPolicy("take8_or_prob52", take_profit_cents=8.0, probability_floor=0.52),
    base.ExitPolicy("take10_or_prob52", take_profit_cents=10.0, probability_floor=0.52),
]

SOURCE_SURFACES = {
    "v38_raw": "v38_raw_p_yes_candidate",
    "v41_v38_bookres_l210": "v41_v38_physics_book_residual_l210_p_yes_candidate",
    "v41_v38_bookres_l230": "v41_v38_physics_book_residual_l230_p_yes_candidate",
    "v41_v39_bookres_l210": "v41_v39_physics_book_residual_l210_p_yes_candidate",
    "v41_v39_bookres_l230": "v41_v39_physics_book_residual_l230_p_yes_candidate",
    "v41_v39_path_l230": "v41_v39_physics_path_l230_p_yes_candidate",
}


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


def latent_hole_mask(ops: pd.DataFrame) -> tuple[pd.Series, dict[str, Any]]:
    trigger_rows = v42.load_rows()
    trigger_ops = v42.opportunity_table(trigger_rows)
    holes = v42.first_hole_markets(
        trigger_ops,
        edge_floor=-2.0,
        p_floor=0.65,
        min_stc=60.0,
        max_stc=600.0,
        low=8.0,
        high=20.0,
    )
    mask = pd.Series(False, index=ops.index)
    for market, first_dt in holes.items():
        mask |= ops["market"].astype(str).eq(str(market)) & ops["entry_dt"].ge(pd.Timestamp(first_dt))
    metadata = {
        "latent_hole_markets": len(holes),
        "latent_hole_rows": int(mask.sum()),
        "latent_hole_trigger": "first raw-v38 selected edge in (8c,20c], p_side>=0.65, stc 60-600",
    }
    return mask, metadata


def logit_blend(left: pd.Series, right: pd.Series, weight_right: float) -> pd.Series:
    return pd.Series(
        sigmoid((1.0 - weight_right) * logit(left) + weight_right * logit(right)),
        index=left.index,
    ).clip(PROB_EPS, 1.0 - PROB_EPS)


def build_probability_candidates(ops: pd.DataFrame) -> tuple[pd.DataFrame, dict[str, Any], list[str]]:
    out, specs, base_cols = v41.build_probability_candidates(ops)
    latent_mask, metadata = latent_hole_mask(out)
    metadata["v41_source_surfaces"] = list(SOURCE_SURFACES)
    metadata["base_candidate_count"] = len(base_cols)

    candidate_cols: list[str] = []
    for short_name, source_col in SOURCE_SURFACES.items():
        if source_col not in out.columns:
            continue
        copied = f"v44_source_{short_name}_p_yes_candidate"
        out[copied] = out[source_col].clip(PROB_EPS, 1.0 - PROB_EPS)
        candidate_cols.append(copied)

    raw = out["v38_raw_p_yes_candidate"].clip(PROB_EPS, 1.0 - PROB_EPS)
    book = out["book_mid_p_yes"].clip(PROB_EPS, 1.0 - PROB_EPS)
    v43_hole90 = raw.copy()
    v43_hole90.loc[latent_mask] = logit_blend(raw.loc[latent_mask], book.loc[latent_mask], 0.90)
    out["v44_v38_hole90_reference_p_yes_candidate"] = v43_hole90
    candidate_cols.append("v44_v38_hole90_reference_p_yes_candidate")

    for short_name, source_col in SOURCE_SURFACES.items():
        if source_col not in out.columns or short_name == "v38_raw":
            continue
        source = out[source_col].clip(PROB_EPS, 1.0 - PROB_EPS)
        for weight in [0.50, 0.70, 0.80, 0.90, 1.00]:
            label = int(round(weight * 100))
            col = f"v44_{short_name}_latent_bookblend{label}_p_yes_candidate"
            out[col] = source.copy()
            out.loc[latent_mask, col] = logit_blend(source.loc[latent_mask], book.loc[latent_mask], weight)
            candidate_cols.append(col)

        switch_col = f"v44_{short_name}_outside_hole_v41_inside_v43hole90_p_yes_candidate"
        out[switch_col] = source.copy()
        out.loc[latent_mask, switch_col] = v43_hole90.loc[latent_mask]
        candidate_cols.append(switch_col)

    metadata["candidate_count"] = len(candidate_cols)
    return out, {**specs, "v44_metadata": metadata}, candidate_cols


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


def exit_policy_from_name(name: str) -> base.ExitPolicy:
    if name == "hold":
        return base.ExitPolicy("hold")
    if name.startswith("prob"):
        return base.ExitPolicy(name, probability_floor=float(name.replace("prob", "")) / 100.0)
    if name.startswith("take"):
        pieces = name.split("_or_")
        take = float(pieces[0].replace("take", ""))
        prob = None
        if len(pieces) > 1 and pieces[1].startswith("prob"):
            prob = float(pieces[1].replace("prob", "")) / 100.0
        return base.ExitPolicy(name, take_profit_cents=take, probability_floor=prob)
    raise ValueError(f"Unknown exit policy: {name}")


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
    best_cache: dict[str, pd.DataFrame] = {}
    paths_cache: dict[str, dict[tuple[str, str], base.QuotePath]] = {}

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
    for _, row in selected.head(15).iterrows():
        col = f"{row['model']}_p_yes_candidate"
        entry = base.EntryPolicy(
            float(row["entry_edge_floor_cents"]),
            float(row["entry_ask_cap_cents"]),
            float(row["entry_min_p_side"]),
            float(row["entry_max_seconds_to_close"]),
            float(row["entry_min_seconds_to_close"]),
        )
        trades = base.simulate(choose_entries(best_cache[col], entry), paths_cache[col], exit_policy_from_name(str(row["exit_policy"])))
        trades["entry_policy"] = row["entry_policy"]
        trades["exit_policy"] = row["exit_policy"]
        selected_trade_frames.append(trades)
    selected_trades = pd.concat(selected_trade_frames, ignore_index=True, sort=False) if selected_trade_frames else pd.DataFrame()
    return summary, selected_trades


def selected_rows(summary: pd.DataFrame) -> pd.DataFrame:
    eligible = summary[summary["min_split_coverage"].ge(MIN_SPLIT_COVERAGE)].copy()
    if eligible.empty:
        return eligible
    pieces: list[pd.DataFrame] = []
    robust = eligible[
        eligible["all_splits_1c_entry_positive"]
        & eligible["positive_1c_days"].eq(eligible["total_days"])
        & eligible["block10_positive"].ge(7)
    ].copy()
    if not robust.empty:
        pieces.append(
            robust.sort_values(
                [
                    "min_split_net_after_fees_1c_entry_dollars",
                    "worst_1c_day_cents",
                    "block10_positive",
                    "all_net_after_fees_1c_entry_dollars",
                ],
                ascending=[False, False, False, False],
            ).head(35)
        )
    split_positive = eligible[eligible["all_splits_1c_entry_positive"]].copy()
    if not split_positive.empty:
        pieces.append(
            split_positive.sort_values(
                ["min_split_net_after_fees_1c_entry_dollars", "positive_1c_days", "all_net_after_fees_1c_entry_dollars"],
                ascending=[False, False, False],
            ).head(35)
        )
    pieces.append(
        eligible.sort_values(
            ["min_split_net_after_fees_1c_entry_dollars", "positive_1c_days", "block10_positive", "all_net_after_fees_1c_entry_dollars"],
            ascending=[False, False, False, False],
        ).head(35)
    )
    return pd.concat(pieces, ignore_index=True, sort=False).drop_duplicates(["model", "entry_policy", "exit_policy"])


def write_report(
    summary: pd.DataFrame,
    selected: pd.DataFrame,
    prob_records: list[dict[str, Any]],
    specs: dict[str, Any],
    candidate_cols: list[str],
) -> None:
    generated = datetime.now(timezone.utc).isoformat()
    eligible = summary[summary["min_split_coverage"].ge(MIN_SPLIT_COVERAGE)].copy() if not summary.empty else summary
    one_cent = eligible[eligible["all_splits_1c_entry_positive"]].copy() if not eligible.empty else eligible
    all_day = one_cent[one_cent["positive_1c_days"].eq(one_cent["total_days"])].copy() if not one_cent.empty else one_cent
    robust = all_day[all_day["block10_positive"].ge(7)].copy() if not all_day.empty else all_day
    holdout_prob = pd.DataFrame(prob_records)
    holdout_prob = holdout_prob[holdout_prob["split"].eq("holdout")].sort_values(["brier", "logloss"]).head(18)
    metadata = specs.get("v44_metadata", {})

    lines = [
        "# v44 Physics Latent-Hole FV Strategy",
        "",
        f"Generated UTC: `{generated}`",
        "",
        "## Scope",
        "",
        "- Research-only FV probability probe combining v41 physics/book posteriors with the v42/v43 latent edge-hole state.",
        "- The edge-hole state changes the probability surface itself; there is no explicit entry veto in this probe.",
        "- Strategy projection requires at least 80% coverage in every chronological split and includes fee plus 1c entry haircut.",
        "- Live bot untouched.",
        "",
        "## Model Notes",
        "",
        f"- Latent-hole markets: {metadata.get('latent_hole_markets')}",
        f"- Latent-hole opportunity rows: {metadata.get('latent_hole_rows')}",
        f"- Candidate probability surfaces: {len(candidate_cols)}",
        "",
        "## Holdout Probability",
        "",
        "| candidate | rows | Brier | logloss | side acc | mean p_yes | yes rate |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for _, row in holdout_prob.iterrows():
        lines.append(
            f"| `{row['candidate']}` | {int(row['rows'])} | {float(row['brier']):.5f} | "
            f"{float(row['logloss']):.5f} | {pct(row['side_accuracy'])} | {pct(row['mean_p_yes'])} | {pct(row['yes_rate'])} |"
        )
    lines += [
        "",
        "## Strategy Search",
        "",
        f"- Rows evaluated after 80% coverage prefilter: {len(summary)}",
        f"- Fee+1c positive train/validation/holdout rows: {len(one_cent)}",
        f"- Fee+1c positive all-day rows: {len(all_day)}",
        f"- All-day rows with at least 7/10 positive chronological blocks: {len(robust)}",
        "",
        "## Selected Strategy Rows",
        "",
        "| model | entry | exit | min cov | min 1c | all 1c | all fee | gross | days | b10 | trades |",
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
    if robust.empty:
        lines.append("- No v44 row cleared the stricter all-day plus 7/10 block gate.")
    else:
        best = robust.sort_values(
            ["min_split_net_after_fees_1c_entry_dollars", "all_net_after_fees_1c_entry_dollars"],
            ascending=[False, False],
        ).iloc[0]
        lines.append(
            f"- Best robust v44 row is `{best['model']}` / `{best['entry_policy']}` / `{best['exit_policy']}` "
            f"with min split fee+1c {dollars(best['min_split_net_after_fees_1c_entry_dollars'])}."
        )
    if not one_cent.empty:
        best_split = one_cent.sort_values(
            ["min_split_net_after_fees_1c_entry_dollars", "positive_1c_days", "block10_positive"],
            ascending=[False, False, False],
        ).iloc[0]
        lines.append(
            f"- Best split-positive v44 row is `{best_split['model']}` / `{best_split['entry_policy']}` / `{best_split['exit_policy']}` "
            f"with min split fee+1c {dollars(best_split['min_split_net_after_fees_1c_entry_dollars'])}."
        )

    REPORT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")
    REPORT_JSON.write_text(
        json.dumps(
            clean_json(
                {
                    "generated_utc": generated,
                    "metadata": metadata,
                    "candidate_count": len(candidate_cols),
                    "summary_rows": int(len(summary)),
                    "one_cent_positive_rows": int(len(one_cent)),
                    "all_day_positive_rows": int(len(all_day)),
                    "robust_rows": int(len(robust)),
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
    rows = v41.load_rows()
    ops = v41.opportunity_table(rows)
    ops, specs, candidate_cols = build_probability_candidates(ops)
    prob_records = probability_metrics(ops, candidate_cols)
    summary, selected_trades = build_strategy(rows, ops, candidate_cols)
    summary.to_csv(SUMMARY_CSV, index=False)
    ops[["opportunity_key", "entry_dt", "market", "split", *candidate_cols]].to_csv(PREDICTIONS_CSV, index=False)
    selected = selected_rows(summary) if not summary.empty else summary
    if not selected_trades.empty:
        selected_trades.to_csv(TRADES_CSV, index=False)
    write_report(summary, selected, prob_records, specs, candidate_cols)
    print("v44 physics latent-hole FV strategy complete")
    print(f"summary_rows={len(summary)} report={REPORT_MD}")
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
