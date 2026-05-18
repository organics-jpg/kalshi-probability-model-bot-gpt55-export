"""Nonlinear EV models for the phi/social/pinball feature bakeoff.

Research-only supplement to probe_phi_social_pinball_ev.py. This checks whether
the pinball idea needs a shallow tree/path model rather than a linear ridge EV
model.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingRegressor, RandomForestRegressor
from sklearn.tree import DecisionTreeRegressor

import probe_phi_frame_feature_comparison as phi
import probe_phi_social_pinball_ev as ev
import probe_arxiv_strategy_priority_tests as priority


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "logs" / "edge_research"
OUT_JSON = OUT_DIR / "phi_social_pinball_ev_nonlinear_latest.json"
OUT_MD = OUT_DIR / "phi_social_pinball_ev_nonlinear_latest.md"
OUT_CSV = OUT_DIR / "phi_social_pinball_ev_nonlinear_summary_latest.csv"

MODEL_SPECS = {
    "tree_d2_leaf20": lambda: DecisionTreeRegressor(max_depth=2, min_samples_leaf=20, random_state=17),
    "tree_d3_leaf20": lambda: DecisionTreeRegressor(max_depth=3, min_samples_leaf=20, random_state=17),
    "rf_d3_leaf15": lambda: RandomForestRegressor(
        n_estimators=200,
        max_depth=3,
        min_samples_leaf=15,
        random_state=17,
        n_jobs=1,
    ),
    "hgb_leaf20_l2": lambda: HistGradientBoostingRegressor(
        max_iter=45,
        max_leaf_nodes=5,
        min_samples_leaf=20,
        learning_rate=0.05,
        l2_regularization=10.0,
        random_state=17,
    ),
}

FEATURE_SET_NAMES = (
    "base_ev",
    "phi_only",
    "social_only",
    "pinball_only",
    "social_pinball",
    "phi_pinball",
    "all3_phi_social_pinball",
    "standard6_social_pinball_control",
)


def fnum(value: Any, default: float = 0.0) -> float:
    return ev.fnum(value, default)


def fit_predict(model_name: str, train: list[dict[str, Any]], test: list[dict[str, Any]], features: list[str]) -> tuple[np.ndarray, np.ndarray]:
    model = MODEL_SPECS[model_name]()
    x_train = ev.make_matrix(train, features)
    y_train = np.array([fnum(row.get("pnl_cents")) for row in train], dtype=float)
    x_test = ev.make_matrix(test, features)
    model.fit(x_train, y_train)
    return np.asarray(model.predict(x_train), dtype=float), np.asarray(model.predict(x_test), dtype=float)


def evaluate_combo(rows: list[dict[str, Any]], feature_set: str, model_name: str) -> dict[str, Any]:
    features = ev.FEATURE_SETS[feature_set]
    split_reports = []
    all_test_rows: list[dict[str, Any]] = []
    all_test_preds: list[float] = []
    all_selected: dict[str, list[dict[str, Any]]] = {"ev_all": [], "robust_ev_overlay": []}

    for split in ev.WFA_SPLITS:
        train = ev.row_window(rows, *split["train"])
        test = ev.row_window(rows, *split["test"])
        train_preds, test_preds = fit_predict(model_name, train, test, features)
        gates = {
            "ev_all": ev.choose_ev_threshold(train, train_preds, robust_only=False),
            "robust_ev_overlay": ev.choose_ev_threshold(train, train_preds, robust_only=True),
        }
        gate_reports = {}
        for gate_name, gate in gates.items():
            selected = ev.select_by_ev_threshold(
                test,
                test_preds,
                float(gate["threshold_ev_cents"]),
                robust_only=gate_name == "robust_ev_overlay",
            )
            all_selected[gate_name].extend(selected)
            gate_reports[gate_name] = {
                "threshold_ev_cents": gate["threshold_ev_cents"],
                "test_stats": phi.pnl_stats(selected),
                "fallback_threshold": gate["fallback"],
            }
        all_test_rows.extend(test)
        all_test_preds.extend(float(v) for v in test_preds)
        split_reports.append(
            {
                "name": split["name"],
                "model_metrics": ev.ev_model_metrics(test, test_preds),
                "gates": gate_reports,
            }
        )

    aggregate_gates = {}
    for gate_name, selected in all_selected.items():
        nets = [fnum(split["gates"][gate_name]["test_stats"]["net_cents"]) for split in split_reports]
        entries = [int(split["gates"][gate_name]["test_stats"]["entries"]) for split in split_reports]
        aggregate_gates[gate_name] = {
            "stats": phi.pnl_stats(selected),
            "positive_windows": int(sum(1 for value in nets if value > 0)),
            "traded_windows": int(sum(1 for value in entries if value > 0)),
            "window_net_cents": nets,
            "window_entries": entries,
            "pnl_cv_abs": ev.safe_cv(nets),
        }

    locked = evaluate_locked(rows, feature_set, model_name)
    return {
        "feature_set": feature_set,
        "model": model_name,
        "feature_count": len(features),
        "aggregate_model_metrics": ev.ev_model_metrics(all_test_rows, np.array(all_test_preds, dtype=float)),
        "gates": aggregate_gates,
        "splits": split_reports,
        "locked_train200": locked,
    }


def evaluate_locked(rows: list[dict[str, Any]], feature_set: str, model_name: str) -> dict[str, Any]:
    features = ev.FEATURE_SETS[feature_set]
    train = ev.row_window(rows, 1, 200)
    test = ev.row_window(rows, 201, None)
    train_preds, test_preds = fit_predict(model_name, train, test, features)
    out = {"model_metrics": ev.ev_model_metrics(test, test_preds), "gates": {}}
    for gate_name, robust_only in (("ev_all", False), ("robust_ev_overlay", True)):
        gate = ev.choose_ev_threshold(train, train_preds, robust_only=robust_only)
        selected = ev.select_by_ev_threshold(test, test_preds, float(gate["threshold_ev_cents"]), robust_only=robust_only)
        out["gates"][gate_name] = {
            "threshold_ev_cents": gate["threshold_ev_cents"],
            "test_stats": phi.pnl_stats(selected),
            "fallback_threshold": gate["fallback"],
        }
    return out


def build_report() -> dict[str, Any]:
    rows, diagnostics = ev.build_rows(fetch_btc_candles=False)
    results = {}
    summary = []
    for model_name in MODEL_SPECS:
        for feature_set in FEATURE_SET_NAMES:
            key = f"{feature_set}__{model_name}"
            result = evaluate_combo(rows, feature_set, model_name)
            results[key] = result
            for gate_name, gate in result["gates"].items():
                stats = gate["stats"]
                locked = result["locked_train200"]["gates"][gate_name]["test_stats"]
                summary.append(
                    {
                        "feature_set": feature_set,
                        "model": model_name,
                        "gate": gate_name,
                        "feature_count": result["feature_count"],
                        "spearman_pred_vs_pnl": result["aggregate_model_metrics"]["spearman_pred_vs_pnl"],
                        "top_quartile_net_dollars": result["aggregate_model_metrics"]["top_quartile"]["net_dollars"],
                        "entries": stats["entries"],
                        "wins": stats["wins"],
                        "losses": stats["losses"],
                        "flats": stats["flats"],
                        "net_dollars": stats["net_dollars"],
                        "avg_cents_per_entry": stats["avg_cents_per_entry"],
                        "positive_windows": gate["positive_windows"],
                        "traded_windows": gate["traded_windows"],
                        "window_net_cents": ",".join(f"{v:.1f}" for v in gate["window_net_cents"]),
                        "locked_entries": locked["entries"],
                        "locked_net_dollars": locked["net_dollars"],
                        "locked_avg_cents_per_entry": locked["avg_cents_per_entry"],
                    }
                )
    summary.sort(
        key=lambda row: (
            fnum(row["positive_windows"]),
            fnum(row["net_dollars"]),
            fnum(row["spearman_pred_vs_pnl"], -99),
        ),
        reverse=True,
    )
    return {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "scope": "research_only_filled_trade_replay",
        "diagnostics": diagnostics,
        "models": list(MODEL_SPECS),
        "feature_sets": list(FEATURE_SET_NAMES),
        "results": results,
        "summary_rows": summary,
    }


def write_report(report: dict[str, Any]) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True, default=str), encoding="utf-8")
    pd.DataFrame(report["summary_rows"]).to_csv(OUT_CSV, index=False)
    lines = [
        "# Nonlinear Phi + Social + Pinball EV Bakeoff",
        "",
        "Research-only filled-trade replay. No live bot logic/state/order path was changed.",
        "",
        "## Top WFA Rows",
        "| rank | feature set | model | gate | rho | top-Q pnl | entries | W/L | pnl | avg | pos windows | window pnl c |",
        "|---:|---|---|---|---:|---:|---:|---:|---:|---:|---:|---|",
    ]
    for rank, row in enumerate(report["summary_rows"][:24], start=1):
        wl = f"{int(row['wins'])}/{int(row['losses'])}"
        if int(row["flats"]):
            wl += f" +{int(row['flats'])} flat"
        rho = row.get("spearman_pred_vs_pnl")
        lines.append(
            "| "
            + " | ".join(
                [
                    str(rank),
                    str(row["feature_set"]),
                    str(row["model"]),
                    str(row["gate"]),
                    "n/a" if rho is None else f"{float(rho):.3f}",
                    f"${fnum(row['top_quartile_net_dollars']):.2f}",
                    str(row["entries"]),
                    wl,
                    f"${fnum(row['net_dollars']):.2f}",
                    f"{fnum(row['avg_cents_per_entry']):.1f}c",
                    f"{int(row['positive_windows'])}/{int(row['traded_windows'])}",
                    str(row["window_net_cents"]),
                ]
            )
            + " |"
        )
    lines.extend(
        [
            "",
            "## Interpretation",
            "- This specifically checks whether the pinball idea behaves better as a shallow path model than as a linear EV model.",
            "- Promotion still requires positive ranking and fresh all-candidate shadow validation.",
        ]
    )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    report = build_report()
    write_report(report)
    print(f"wrote {OUT_MD}")
    print(f"wrote {OUT_JSON}")
    print(f"wrote {OUT_CSV}")


if __name__ == "__main__":
    main()
