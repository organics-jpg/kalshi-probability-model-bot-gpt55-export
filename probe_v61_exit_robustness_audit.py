"""Audit robust exit alternatives around the v60 NO-side margin gate.

Research-only. Compares the v57-style baseline, the max-upside v60 NO-side
margin gate, a stricter prob56 NO-side margin compromise, and the best symmetric
held-side margin row.

No live bot files, processes, or order paths are touched.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd

import probe_v58_v55_exit_persistence_refine as v58
from probe_market_interval_80coverage import clean_json


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
REPORT_MD = OUT_DIR / "v61_exit_robustness_audit_latest.md"
REPORT_JSON = OUT_DIR / "v61_exit_robustness_audit_latest.json"
SLICE_CSV = OUT_DIR / "v61_exit_robustness_policy_slice_latest.csv"
DELTA_CSV = OUT_DIR / "v61_exit_robustness_delta_latest.csv"

BASELINE = "hold15_prob52"
MAX_UPSIDE = "hold15_prob52_noside_marginlte0p25"
COMPROMISE = "hold15_prob56_noside_marginlte0p25"
HELD_SIDE = "hold15_prob54_heldmarginlte0p5"
POLICIES = [BASELINE, MAX_UPSIDE, COMPROMISE, HELD_SIDE]
DELTA_POLICIES = [MAX_UPSIDE, COMPROMISE, HELD_SIDE]


def money(value: Any) -> str:
    try:
        return f"${float(value):.2f}"
    except (TypeError, ValueError):
        return "NA"


def fee_1c_cents(rows: pd.DataFrame) -> pd.Series:
    return pd.to_numeric(rows["pnl_cents"], errors="coerce").fillna(0.0) - pd.to_numeric(
        rows["total_fee_cents"], errors="coerce"
    ).fillna(0.0) - v58.base.QTY


def summarize(part: pd.DataFrame, label: str, value: str) -> dict[str, Any]:
    if part.empty:
        return {
            "slice": label,
            "value": value,
            "trades": 0,
            "fee_1c_dollars": 0.0,
            "exits": 0,
            "settled": 0,
            "wins": 0,
            "losses": 0,
        }
    win = part["win"].astype(bool)
    settled = part["settled"].astype(bool)
    return {
        "slice": label,
        "value": value,
        "trades": int(len(part)),
        "fee_1c_dollars": float(fee_1c_cents(part).sum() / 100.0),
        "avg_fee_1c_cents": float(fee_1c_cents(part).mean()),
        "exits": int((~settled).sum()),
        "settled": int(settled.sum()),
        "wins": int(win.sum()),
        "losses": int((~win).sum()),
        "win_rate": float(win.mean()) if len(part) else None,
    }


def policy_slices(trades: pd.DataFrame) -> pd.DataFrame:
    records: list[dict[str, Any]] = []
    for policy in POLICIES:
        rows = trades[trades["exit_policy"].eq(policy)].copy()
        records.append({"policy": policy, **summarize(rows, "all", "all")})
        for side, part in rows.groupby("side"):
            records.append({"policy": policy, **summarize(part, "side", str(side))})
        for split, part in rows.groupby("split"):
            records.append({"policy": policy, **summarize(part, "split", str(split))})
    return pd.DataFrame(records)


def deltas_vs_baseline(trades: pd.DataFrame) -> pd.DataFrame:
    key_cols = ["market", "entry_dt", "side"]
    base = trades[trades["exit_policy"].eq(BASELINE)].copy()
    base["fee_1c_cents"] = fee_1c_cents(base)
    cols = [
        *key_cols,
        "split",
        "outcome",
        "win",
        "entry_ask_cents",
        "entry_p_side",
        "entry_seconds_to_close",
        "exit_type",
        "exit_dt",
        "exit_bid_cents",
        "exit_p_side",
        "settled",
        "fee_1c_cents",
    ]
    joined_rows = []
    for policy in DELTA_POLICIES:
        candidate = trades[trades["exit_policy"].eq(policy)].copy()
        candidate["fee_1c_cents"] = fee_1c_cents(candidate)
        joined = base[cols].merge(candidate[cols], on=key_cols, suffixes=("_base", "_candidate"), how="inner")
        joined["candidate_policy"] = policy
        joined["delta_fee_1c_cents"] = joined["fee_1c_cents_candidate"] - joined["fee_1c_cents_base"]
        joined["abs_delta_fee_1c_cents"] = joined["delta_fee_1c_cents"].abs()
        joined_rows.append(joined)
    return pd.concat(joined_rows, ignore_index=True, sort=False)


def concentration_for_policy(delta: pd.DataFrame, policy: str) -> dict[str, Any]:
    part = delta[delta["candidate_policy"].eq(policy)].copy()
    if part.empty:
        return {"candidate_policy": policy}
    total = float(part["delta_fee_1c_cents"].sum())
    positive = part[part["delta_fee_1c_cents"].gt(0)].sort_values("delta_fee_1c_cents", ascending=False)
    negative = part[part["delta_fee_1c_cents"].lt(0)].sort_values("delta_fee_1c_cents")
    top5 = float(positive.head(5)["delta_fee_1c_cents"].sum()) if not positive.empty else 0.0
    top10 = float(positive.head(10)["delta_fee_1c_cents"].sum()) if not positive.empty else 0.0
    return {
        "candidate_policy": policy,
        "total_delta_dollars": total / 100.0,
        "positive_delta_markets": int(len(positive)),
        "negative_delta_markets": int(len(negative)),
        "top5_positive_delta_dollars": top5 / 100.0,
        "top10_positive_delta_dollars": top10 / 100.0,
        "top5_share_of_total_delta": float(top5 / total) if total > 0 else None,
        "top10_share_of_total_delta": float(top10 / total) if total > 0 else None,
        "worst_negative_delta_dollars": float(negative["delta_fee_1c_cents"].min() / 100.0) if not negative.empty else 0.0,
    }


def build_trades() -> pd.DataFrame:
    rows = v58.v47.load_rows()
    ops = v58.v42.opportunity_table(rows)
    ops, _, _ = v58.v55.build_probability_candidates(ops)
    frame = v58.v42.frame_for_candidate(rows, ops, v58.MODEL_COL)
    best = v58.base.best_side_per_opportunity(frame)
    paths = v58.quote_paths(frame)
    entries = v58.v42.choose_entries(best, v58.ENTRY)
    policy_by_name = {policy.name: policy for policy in v58.exit_policies()}
    missing = [name for name in POLICIES if name not in policy_by_name]
    if missing:
        raise RuntimeError(f"Missing exit policies from v58 sweep: {missing}")
    return pd.concat(
        [v58.simulate(entries, paths, policy_by_name[name]).assign(exit_policy=name) for name in POLICIES],
        ignore_index=True,
        sort=False,
    )


def write_report(slices: pd.DataFrame, delta: pd.DataFrame, concentration: list[dict[str, Any]]) -> None:
    generated = datetime.now(timezone.utc).isoformat()
    lines = [
        "# v61 Exit Robustness Audit",
        "",
        f"Generated UTC: `{generated}`",
        "",
        "## Scope",
        "",
        "- Research-only comparison of v57 baseline, v60 max-upside NO-side margin gate, a prob56 NO-side compromise, and a symmetric held-side margin row.",
        "- Same v55 entry/FV surface across policies.",
        "- Live bot untouched.",
        "",
        "## Policy Slices",
        "",
        "| policy | slice | value | trades | fee+1c | exits | settled | wins | losses |",
        "|---|---|---|---:|---:|---:|---:|---:|---:|",
    ]
    for _, row in slices[slices["slice"].isin(["all", "side", "split"])].iterrows():
        lines.append(
            f"| `{row['policy']}` | `{row['slice']}` | `{row['value']}` | {int(row['trades'])} | "
            f"{money(row['fee_1c_dollars'])} | {int(row['exits'])} | {int(row['settled'])} | "
            f"{int(row['wins'])} | {int(row['losses'])} |"
        )
    lines += [
        "",
        "## Delta Concentration Vs Baseline",
        "",
        "| candidate | delta | pos/neg markets | top5 positive | top5 share | worst negative |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for row in concentration:
        top5_share = row.get("top5_share_of_total_delta")
        lines.append(
            f"| `{row.get('candidate_policy')}` | {money(row.get('total_delta_dollars'))} | "
            f"{row.get('positive_delta_markets', 0)}/{row.get('negative_delta_markets', 0)} | "
            f"{money(row.get('top5_positive_delta_dollars'))} | "
            f"{'NA' if top5_share is None else f'{100.0 * float(top5_share):.1f}%'} | "
            f"{money(row.get('worst_negative_delta_dollars'))} |"
        )
    lines += [
        "",
        "## Largest Positive Deltas",
        "",
        "| candidate | market | side | split | base fee+1c | candidate fee+1c | delta | base exit | candidate exit |",
        "|---|---|---|---|---:|---:|---:|---|---|",
    ]
    largest = delta.sort_values("delta_fee_1c_cents", ascending=False).groupby("candidate_policy").head(6)
    for _, row in largest.iterrows():
        lines.append(
            f"| `{row['candidate_policy']}` | `{row['market']}` | `{row['side']}` | `{row['split_base']}` | "
            f"{money(float(row['fee_1c_cents_base']) / 100.0)} | "
            f"{money(float(row['fee_1c_cents_candidate']) / 100.0)} | "
            f"{money(float(row['delta_fee_1c_cents']) / 100.0)} | "
            f"`{row['exit_type_base']}` | `{row['exit_type_candidate']}` |"
        )
    lines += ["", "## Read", ""]
    lines.append(
        "- The prob56 NO-side margin compromise is the main robustness challenger: lower all-market PnL than v60, but a better min/holdout cushion than v57 in the current sweep."
    )
    lines.append(
        "- It still needs its own concentration and strict-forward behavior to justify promotion; this audit is retrospective only."
    )
    REPORT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")
    REPORT_JSON.write_text(
        json.dumps(
            clean_json(
                {
                    "generated_utc": generated,
                    "concentration": concentration,
                    "policy_slices": json.loads(slices.to_json(orient="records", date_format="iso")),
                    "top_deltas": json.loads(delta.sort_values("delta_fee_1c_cents", ascending=False).head(100).to_json(orient="records", date_format="iso")),
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
    slices = policy_slices(trades)
    delta = deltas_vs_baseline(trades)
    concentration = [concentration_for_policy(delta, policy) for policy in DELTA_POLICIES]
    slices.to_csv(SLICE_CSV, index=False)
    delta.to_csv(DELTA_CSV, index=False)
    write_report(slices, delta, concentration)
    print("v61 exit robustness audit complete")
    print(f"report={REPORT_MD}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
