"""Observed-FV posterior strategy projection.

Research-only. Tests whether a train-only book-observation posterior improves
the FV model enough to support high-coverage profitable entry/exit rules.

No live bot code/process/order path is touched.
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
from probe_v31_book_calibrated_probability import fit_logistic, logit, predict_logistic


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
INPUT = OUT_DIR / "mushroom_v29_fv_surface_predictions_two_side_all_heartbeats_latest.csv"
REPORT_MD = OUT_DIR / "v40_observed_fv_strategy_projection_latest.md"
REPORT_JSON = OUT_DIR / "v40_observed_fv_strategy_projection_latest.json"
SUMMARY_CSV = OUT_DIR / "v40_observed_fv_strategy_projection_summary_latest.csv"
PREDICTIONS_CSV = OUT_DIR / "v40_observed_fv_strategy_projection_predictions_latest.csv"

MIN_SPLIT_COVERAGE = 0.80
PROB_EPS = 1e-6

RAW_MODELS = [
    "v38_long60_antipersist",
    "v39_midband_v28_fallback",
]

ENTRY_POLICIES = [
    base.EntryPolicy(edge, ask, pside, max_stc, 0.0)
    for edge in [-3.0, -2.0, 0.0, 1.0, 2.0]
    for ask in [100.0, 95.0, 90.0]
    for pside in [0.55, 0.60, 0.65]
    for max_stc in [600.0, 780.0, 900.0]
]

EXIT_POLICIES = [
    base.ExitPolicy("hold"),
    base.ExitPolicy("prob50", probability_floor=0.50),
    base.ExitPolicy("prob52", probability_floor=0.52),
    base.ExitPolicy("prob54", probability_floor=0.54),
    base.ExitPolicy("take10_or_prob52", take_profit_cents=10.0, probability_floor=0.52),
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
    }
    for model in RAW_MODELS:
        usecols.add(f"{model}_p_yes")
    rows = pd.read_csv(INPUT, usecols=lambda col: col in usecols, low_memory=False)
    rows["entry_dt"] = pd.to_datetime(rows["entry_dt"], utc=True, errors="coerce")
    for col in ["ask_cents", "bid_cents", "book_mid_cents", "seconds_to_close"]:
        rows[col] = pd.to_numeric(rows[col], errors="coerce")
    rows["win_bool"] = rows["win"].astype(str).str.lower().isin({"true", "1", "yes"})
    rows = rows.dropna(subset=["opportunity_key", "entry_dt", "market", "side", "ask_cents", "split"]).copy()
    return rows.sort_values(["market", "entry_dt", "side"]).reset_index(drop=True)


def opportunity_table(rows: pd.DataFrame) -> pd.DataFrame:
    base_rows = rows.drop_duplicates("opportunity_key").copy()
    piv = rows.pivot_table(
        index="opportunity_key",
        columns="side",
        values="book_mid_cents",
        aggfunc="first",
    ).rename(columns={"yes": "yes_book_mid_cents", "no": "no_book_mid_cents"})
    out = base_rows.merge(piv, left_on="opportunity_key", right_index=True, how="left")
    denom = out["yes_book_mid_cents"] + out["no_book_mid_cents"]
    out["book_mid_p_yes"] = (out["yes_book_mid_cents"] / denom).clip(PROB_EPS, 1.0 - PROB_EPS)
    out["outcome_yes"] = out["outcome"].astype(str).str.lower().eq("yes").astype(float)
    out["log_time_to_close"] = np.log(np.clip(pd.to_numeric(out["seconds_to_close"], errors="coerce"), 1.0, None) / 900.0)
    for model in RAW_MODELS:
        out[f"{model}_p_yes"] = pd.to_numeric(out[f"{model}_p_yes"], errors="coerce").clip(PROB_EPS, 1.0 - PROB_EPS)
    return out.dropna(subset=["book_mid_p_yes", "outcome_yes", "split", *[f"{m}_p_yes" for m in RAW_MODELS]]).copy()


def build_probability_candidates(ops: pd.DataFrame) -> tuple[pd.DataFrame, dict[str, Any]]:
    train = ops[ops["split"].eq("train")].copy()
    y = train["outcome_yes"].to_numpy(dtype=float)
    book_l_train = logit(train["book_mid_p_yes"])
    coefs: dict[str, Any] = {
        "book_platt": fit_logistic(book_l_train, y, l2=1.0).tolist(),
    }
    out = ops.copy()
    book_l = logit(out["book_mid_p_yes"])
    out["book_mid_p_yes_candidate"] = out["book_mid_p_yes"]
    out["book_platt_p_yes_candidate"] = predict_logistic(np.asarray(coefs["book_platt"], dtype=float), book_l)

    for model in RAW_MODELS:
        train_model_l = logit(train[f"{model}_p_yes"])
        model_l = logit(out[f"{model}_p_yes"])
        name = model.replace("_long60_antipersist", "").replace("_midband_v28_fallback", "")
        coefs[f"book_{name}_platt"] = fit_logistic(np.column_stack([book_l_train, train_model_l]), y, l2=1.0).tolist()
        out[f"{model}_raw_p_yes_candidate"] = out[f"{model}_p_yes"]
        out[f"book_{name}_platt_p_yes_candidate"] = predict_logistic(
            np.asarray(coefs[f"book_{name}_platt"], dtype=float),
            np.column_stack([book_l, model_l]),
        )
        for w in [0.70, 0.85]:
            cand = f"book{int(w * 100)}_{name}{int((1.0 - w) * 100)}_logit_blend_p_yes_candidate"
            out[cand] = 1.0 / (1.0 + np.exp(-(w * book_l + (1.0 - w) * model_l)))
    return out, coefs


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


def row_1c_positive(record: dict[str, Any]) -> bool:
    return all(float(record[f"{split}_net_after_fees_1c_entry_dollars"]) > 0.0 for split in ["train", "validation", "holdout"])


def build_strategy(rows: pd.DataFrame, ops: pd.DataFrame, candidate_cols: list[str]) -> pd.DataFrame:
    universes = base.market_universes(rows)
    records: list[dict[str, Any]] = []
    for col in candidate_cols:
        frame = frame_for_candidate(rows, ops, col)
        best_opp = base.best_side_per_opportunity(frame)
        paths = base.quote_paths(frame)
        for entry_policy in ENTRY_POLICIES:
            entries = base.choose_entries(best_opp, entry_policy)
            if entries.empty:
                continue
            min_coverage = min(
                len(set(entries["market"].astype(str)) & universes[split]) / len(universes[split])
                for split in ["train", "validation", "holdout"]
            )
            if min_coverage < MIN_SPLIT_COVERAGE:
                continue
            for exit_policy in EXIT_POLICIES:
                trades = base.simulate(entries, paths, exit_policy)
                if trades.empty:
                    continue
                record = base.flatten_metrics(str(frame["model"].iloc[0]), entry_policy, exit_policy, trades, universes)
                record["min_split_net_after_fees_1c_entry_dollars"] = float(
                    min(record[f"{split}_net_after_fees_1c_entry_dollars"] for split in ["train", "validation", "holdout"])
                )
                record["all_splits_1c_entry_positive"] = row_1c_positive(record)
                records.append(record)
    return pd.DataFrame(records)


def selected_rows(summary: pd.DataFrame) -> pd.DataFrame:
    if summary.empty:
        return summary
    eligible = summary[summary["min_split_coverage"].ge(MIN_SPLIT_COVERAGE)].copy()
    if eligible.empty:
        return eligible
    pieces: list[pd.DataFrame] = []
    one_cent = eligible[eligible["all_splits_1c_entry_positive"]].copy()
    if not one_cent.empty:
        pieces.append(
            one_cent.sort_values(
                ["min_split_net_after_fees_1c_entry_dollars", "all_net_after_fees_1c_entry_dollars"],
                ascending=[False, False],
            ).head(25)
        )
    pieces.append(
        eligible.sort_values(
            ["min_split_net_after_fees_1c_entry_dollars", "all_net_after_fees_1c_entry_dollars"],
            ascending=[False, False],
        ).head(25)
    )
    return pd.concat(pieces, ignore_index=True, sort=False).drop_duplicates(["model", "entry_policy", "exit_policy"])


def write_report(
    summary: pd.DataFrame,
    selected: pd.DataFrame,
    prob_records: list[dict[str, Any]],
    coefs: dict[str, Any],
    candidate_cols: list[str],
) -> None:
    generated = datetime.now(timezone.utc).isoformat()
    eligible = summary[summary["min_split_coverage"].ge(MIN_SPLIT_COVERAGE)].copy() if not summary.empty else summary
    one_cent = eligible[eligible["all_splits_1c_entry_positive"]].copy() if not eligible.empty else eligible
    holdout_prob = pd.DataFrame(prob_records)
    holdout_prob = holdout_prob[holdout_prob["split"].eq("holdout")].sort_values(["brier", "logloss"]).head(12)
    lines = [
        "# v40 Observed-FV Strategy Projection",
        "",
        f"Generated UTC: `{generated}`",
        "",
        "## Scope",
        "",
        "- Train-only book/FV probability posterior test.",
        "- Strategy projection still requires at least 80% coverage in every split.",
        "- Research-only; live bot untouched.",
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
        "",
        "## Selected Strategy Rows",
        "",
        "| model | entry | exit | min cov | min 1c | all 1c | all fee | gross | trades |",
        "|---|---|---|---:|---:|---:|---:|---:|---:|",
    ]
    for _, row in selected.head(30).iterrows():
        lines.append(
            f"| `{row['model']}` | `{row['entry_policy']}` | `{row['exit_policy']}` | "
            f"{pct(row['min_split_coverage'])} | {dollars(row['min_split_net_after_fees_1c_entry_dollars'])} | "
            f"{dollars(row['all_net_after_fees_1c_entry_dollars'])} | "
            f"{dollars(row['all_net_after_fees_dollars'])} | {dollars(row['all_pnl_dollars'])} | "
            f"{int(row['all_trades'])} |"
        )
    lines += ["", "## Read", ""]
    if one_cent.empty:
        lines.append(
            "- Observed/book posterior improves raw probability calibration, but did not produce an 80%-coverage fee+1c-positive strategy row."
        )
    else:
        best = one_cent.sort_values(
            ["min_split_net_after_fees_1c_entry_dollars", "all_net_after_fees_1c_entry_dollars"],
            ascending=[False, False],
        ).iloc[0]
        lines.append(
            f"- Best observed-FV row is `{best['model']}` / `{best['entry_policy']}` / `{best['exit_policy']}` "
            f"with min split fee+1c {dollars(best['min_split_net_after_fees_1c_entry_dollars'])}."
        )
    REPORT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")
    REPORT_JSON.write_text(
        json.dumps(
            clean_json(
                {
                    "generated_utc": generated,
                    "coefs": coefs,
                    "probability_records": prob_records,
                    "summary_rows": int(len(summary)),
                    "one_cent_positive_rows": int(len(one_cent)),
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
    ops, coefs = build_probability_candidates(ops)
    candidate_cols = [col for col in ops.columns if col.endswith("_p_yes_candidate")]
    prob_records = probability_metrics(ops, candidate_cols)
    summary = build_strategy(rows, ops, candidate_cols)
    summary.to_csv(SUMMARY_CSV, index=False)
    ops[["opportunity_key", "entry_dt", "market", "split", *candidate_cols]].to_csv(PREDICTIONS_CSV, index=False)
    selected = selected_rows(summary)
    write_report(summary, selected, prob_records, coefs, candidate_cols)
    one_cent = summary[summary["all_splits_1c_entry_positive"]] if not summary.empty else summary
    print("v40 observed-FV strategy projection complete")
    print(f"summary_rows={len(summary)} one_cent_rows={len(one_cent)} report={REPORT_MD}")
    if not selected.empty:
        best = selected.iloc[0]
        print(
            f"best={best['model']} {best['entry_policy']} {best['exit_policy']} "
            f"min_1c={float(best['min_split_net_after_fees_1c_entry_dollars']):.2f} "
            f"all_1c={float(best['all_net_after_fees_1c_entry_dollars']):.2f}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
