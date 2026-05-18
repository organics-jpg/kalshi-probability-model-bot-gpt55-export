"""Book-observation probability blend for the v31 FV surface.

This is a probability calibration probe, not a trade scorer. It tests the prior
that the FV model should ignore the Kalshi book. The book is treated as a noisy
market observation of terminal probability and blended with the physics model
in log-odds space.

Important: better calibration from book probabilities is not proof of tradable
edge, because trades pay the ask and cross spread. This probe only measures
probability quality.
"""
from __future__ import annotations

import json
import math
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from probe_market_interval_80coverage import clean_json, pct
from probe_mushroom_v29_fv_surface import PROB_EPS


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
PREDICTIONS_PATH = OUT_DIR / "mushroom_v29_fv_surface_predictions_two_side_all_heartbeats_latest.csv"
REPORT_MD = OUT_DIR / "v31_book_observation_blend_latest.md"
REPORT_JSON = OUT_DIR / "v31_book_observation_blend_latest.json"
SUMMARY_CSV = OUT_DIR / "v31_book_observation_blend_summary_latest.csv"

WEIGHTS = [0.0, 0.05, 0.10, 0.15, 0.20, 0.25, 0.30, 0.35, 0.40, 0.50, 0.60, 0.70, 0.80, 1.0]


def logit(p: Any) -> np.ndarray:
    p_arr = np.clip(np.asarray(p, dtype=float), PROB_EPS, 1.0 - PROB_EPS)
    return np.log(p_arr / (1.0 - p_arr))


def sigmoid(x: Any) -> np.ndarray:
    x_arr = np.asarray(x, dtype=float)
    return 1.0 / (1.0 + np.exp(-x_arr))


def metrics(y: pd.Series, p: pd.Series | np.ndarray) -> dict[str, Any]:
    y_arr = np.asarray(y, dtype=float)
    p_arr = np.clip(np.asarray(p, dtype=float), PROB_EPS, 1.0 - PROB_EPS)
    mask = np.isfinite(p_arr)
    y_arr = y_arr[mask]
    p_arr = p_arr[mask]
    if len(p_arr) == 0:
        return {"n": 0, "brier": None, "logloss": None, "side_accuracy": None, "mean_p_yes": None, "yes_rate": None}
    return {
        "n": int(len(p_arr)),
        "brier": float(np.mean((p_arr - y_arr) ** 2)),
        "logloss": float(-(y_arr * np.log(p_arr) + (1.0 - y_arr) * np.log(1.0 - p_arr)).mean()),
        "side_accuracy": float(((p_arr >= 0.5) == (y_arr >= 0.5)).mean()),
        "mean_p_yes": float(p_arr.mean()),
        "yes_rate": float(y_arr.mean()),
    }


def opportunity_rows(rows: pd.DataFrame) -> pd.DataFrame:
    base = rows.drop_duplicates("opportunity_key").copy()
    piv = rows.pivot_table(index="opportunity_key", columns="side", values="book_mid_cents", aggfunc="first")
    piv = piv.rename(columns={"yes": "yes_mid", "no": "no_mid"})
    base = base.merge(piv, left_on="opportunity_key", right_index=True, how="left")
    base["yes_mid"] = pd.to_numeric(base["yes_mid"], errors="coerce")
    base["no_mid"] = pd.to_numeric(base["no_mid"], errors="coerce")
    denom = base["yes_mid"] + base["no_mid"]
    base["book_p_yes"] = base["yes_mid"] / denom
    base["v31_p_yes"] = pd.to_numeric(base["v31_avg90_final60_exact_p_yes"], errors="coerce")
    base["v28_p_yes"] = pd.to_numeric(base["v28_live_surface_p_yes"], errors="coerce")
    base["outcome_yes"] = base["outcome"].astype(str).str.lower().eq("yes").astype(float)
    return base[
        [
            "opportunity_key",
            "market",
            "entry_dt",
            "split",
            "outcome",
            "outcome_yes",
            "v28_p_yes",
            "v31_p_yes",
            "book_p_yes",
            "yes_mid",
            "no_mid",
        ]
    ].copy()


def build_summary(ops: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    valid = ops.dropna(subset=["v31_p_yes", "book_p_yes", "outcome_yes"]).copy()
    model_logit = logit(valid["v31_p_yes"])
    book_logit = logit(valid["book_p_yes"])

    candidates: dict[str, np.ndarray] = {
        "v28_live_surface": np.asarray(valid["v28_p_yes"], dtype=float),
        "v31_avg90_final60_exact": np.asarray(valid["v31_p_yes"], dtype=float),
        "book_mid_probability": np.asarray(valid["book_p_yes"], dtype=float),
    }
    for weight in WEIGHTS:
        candidates[f"v31_book_logit_blend_w{weight:.2f}"] = sigmoid((1.0 - weight) * model_logit + weight * book_logit)

    for name, probs in candidates.items():
        for split in ["all", "validation", "holdout"]:
            part_mask = np.ones(len(valid), dtype=bool) if split == "all" else valid["split"].astype(str).eq(split).to_numpy()
            met = metrics(valid.loc[part_mask, "outcome_yes"], probs[part_mask])
            rows.append(
                {
                    "model": name,
                    "split": split,
                    **met,
                }
            )
    return pd.DataFrame(rows)


def write_report(summary: pd.DataFrame) -> None:
    holdout = summary[summary["split"].eq("holdout")].sort_values("brier")
    validation = summary[summary["split"].eq("validation")].sort_values("brier")
    best = holdout.iloc[0]
    lines = [
        "# v31 Book Observation Blend",
        "",
        f"Generated UTC: `{datetime.now(timezone.utc).isoformat()}`",
        "",
        "## Scope",
        "",
        "- Probability calibration only; not a trade scorer.",
        "- Treats Kalshi book mid as a noisy observation and blends it with v31 log-odds.",
        "- Better book calibration does not imply edge after crossing the ask/spread.",
        "",
        "## Holdout",
        "",
        "| model | n | Brier | logloss | side acc | mean p_yes | yes rate |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for _, row in holdout.head(12).iterrows():
        lines.append(
            f"| `{row['model']}` | {int(row['n'])} | {row['brier']:.5f} | {row['logloss']:.5f} | "
            f"{pct(row['side_accuracy'])} | {pct(row['mean_p_yes'])} | {pct(row['yes_rate'])} |"
        )
    lines += [
        "",
        "## Validation",
        "",
        "| model | n | Brier | logloss | side acc | mean p_yes | yes rate |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for _, row in validation.head(12).iterrows():
        lines.append(
            f"| `{row['model']}` | {int(row['n'])} | {row['brier']:.5f} | {row['logloss']:.5f} | "
            f"{pct(row['side_accuracy'])} | {pct(row['mean_p_yes'])} | {pct(row['yes_rate'])} |"
        )
    lines += [
        "",
        "## Read",
        "",
        f"- Best holdout probability model: `{best['model']}` at Brier/logloss {best['brier']:.5f}/{best['logloss']:.5f}.",
        "- The book mid dominates pure physics probability calibration in this sample.",
        "- The next FV question is how much book observation to trust without erasing tradable edge.",
    ]
    REPORT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    if not PREDICTIONS_PATH.exists():
        raise SystemExit(f"Missing predictions file: {PREDICTIONS_PATH}")
    rows = pd.read_csv(PREDICTIONS_PATH, low_memory=False)
    ops = opportunity_rows(rows)
    summary = build_summary(ops)
    summary.to_csv(SUMMARY_CSV, index=False)
    payload = {
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "predictions_path": str(PREDICTIONS_PATH),
        "weights": WEIGHTS,
        "summary": summary.to_dict("records"),
    }
    REPORT_JSON.write_text(json.dumps(clean_json(payload), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_report(summary)
    print("v31 book observation blend complete")
    print(f"summary_rows={len(summary)} report={REPORT_MD}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
