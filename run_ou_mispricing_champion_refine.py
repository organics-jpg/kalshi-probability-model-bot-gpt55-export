from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import run_ou_mispricing_refinement_sweep as sweep


ROOT = Path(__file__).resolve().parent
REPORT_DIR = ROOT / "logs" / "particle_research" / "reports"
DOCS_DIR = ROOT / "docs" / "research"


CHAMPION_BASE: dict[str, Any] = {
    **sweep.BASE_VERY_STRICT,
    "allowed_sides": "no",
    "pt_values": "3,5,8",
    "sl_values": "8,12,20,35",
    "hold_values": "30,60,120,240",
    "sim_paths": 1600,
}


TARGET_VARIANTS: dict[str, dict[str, Any]] = {
    "champion_control_1600": {},
    "champion_hold_120": {
        "hold_values": "30,60,120",
    },
    "champion_hold_60": {
        "hold_values": "30,60",
    },
    "champion_preclose_60": {
        "exit_before_close_seconds": 60.0,
    },
    "champion_preclose_120": {
        "exit_before_close_seconds": 120.0,
    },
    "champion_entry_120_300": {
        "min_seconds_to_close": 120.0,
        "max_seconds_to_close": 300.0,
    },
    "champion_entry_90_420": {
        "min_seconds_to_close": 90.0,
        "max_seconds_to_close": 420.0,
    },
    "champion_ev4_loss44": {
        "min_sim_ev_cents": 4.0,
        "max_loss_prob": 0.44,
    },
    "champion_ev5_loss40": {
        "min_sim_ev_cents": 5.0,
        "max_loss_prob": 0.40,
    },
    "champion_z10": {
        "entry_z_min": 10.0,
    },
    "champion_spread2": {
        "max_spread_cents": 2.0,
    },
    "champion_sharpe_objective": {
        "choice_objective": "sharpe",
    },
    "champion_reentry": {
        "allow_reentry": True,
    },
    "champion_reentry_ev5_loss40": {
        "allow_reentry": True,
        "min_sim_ev_cents": 5.0,
        "max_loss_prob": 0.40,
    },
}


def render_report(payload: dict[str, Any]) -> str:
    ranked = sorted(payload["variants"], key=lambda row: row["summary"]["net_pnl_dollars"], reverse=True)
    lines = [
        "# OU Mispricing Champion Refinement",
        "",
        f"Generated: {payload['generated_utc']}",
        "",
        "Research-only. No live bot logic, state, processes, or orders were changed.",
        "",
        "This pass starts from the best broad sweep candidate: NO-only, small take-profit grid, wider stop grid.",
        "",
        "| Rank | Variant | Trades | Net PnL | Win rate | Avg/trade | Positive days |",
        "|---:|---|---:|---:|---:|---:|---:|",
    ]
    for idx, row in enumerate(ranked, start=1):
        summary = row["summary"]
        diag = row["diagnostics"]
        day_text = f"{diag['positive_days']}/{diag['positive_days'] + diag['nonpositive_days']}"
        lines.append(
            f"| {idx} | {row['variant']} | {summary['trade_count']} | ${summary['net_pnl_dollars']:.2f} | "
            f"{summary['win_rate']:.2%} | {summary['mean_trade_pnl_dollars'] * 100:.2f}c | {day_text} |"
        )
    if ranked:
        best = ranked[0]
        lines.extend(
            [
                "",
                "## Best Diagnostics",
                "",
                f"Best variant: `{best['variant']}`.",
                "",
                "| Exit reason | Trades | PnL |",
                "|---|---:|---:|",
            ]
        )
        for row in best["diagnostics"]["by_exit_reason"]:
            lines.append(f"| {row['exit_reason']} | {row['trades']} | ${row['pnl']:.2f} |")
        lines.extend(["", "| Segment | Trades | PnL | First entry | Last entry |", "|---:|---:|---:|---|---|"])
        for row in best["diagnostics"]["chronological_thirds"]:
            lines.append(
                f"| {row['segment']} | {row['trades']} | ${row['pnl']:.2f} | {row['first_entry']} | {row['last_entry']} |"
            )
    lines.extend(
        [
            "",
            "## Notes",
            "",
            "Repeated-entry variants are diagnostic only. They can improve PnL by using the same market multiple times, but they need stricter fill and inventory accounting before becoming a preferred shadow candidate.",
        ]
    )
    return "\n".join(lines) + "\n"


def main() -> None:
    snapshots, market_results, inputs = sweep.build_dataset()
    variants: list[dict[str, Any]] = []
    for name, overrides in TARGET_VARIANTS.items():
        settings = {**CHAMPION_BASE, **overrides}
        settings["one_entry_per_market"] = not bool(settings.get("allow_reentry", False))
        report = sweep.run_refined_backtest(snapshots, market_results, settings)
        variants.append(
            {
                "variant": name,
                "settings": settings,
                "summary": report["summary"],
                "diagnostics": sweep.diagnostics(report["trades"]),
                "trades_csv": sweep.write_variant_trades(name, report["trades"]),
            }
        )

    payload = {
        "generated_utc": sweep.utc_now_iso(),
        "inputs": inputs,
        "variants": variants,
    }
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    DOCS_DIR.mkdir(parents=True, exist_ok=True)
    json_path = REPORT_DIR / "ou_mispricing_champion_refine.json"
    md_path = DOCS_DIR / "OU_MISPRICING_CHAMPION_REFINE_VERDICT.md"
    json_path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    md_path.write_text(render_report(payload), encoding="utf-8")
    print(json.dumps({"summary_json": str(json_path), "summary_md": str(md_path)}, indent=2))
    for row in sorted(variants, key=lambda item: item["summary"]["net_pnl_dollars"], reverse=True):
        summary = row["summary"]
        print(
            f"{row['variant']}: trades={summary['trade_count']} pnl=${summary['net_pnl_dollars']:.2f} "
            f"win={summary['win_rate']:.2%} avg={summary['mean_trade_pnl_dollars'] * 100:.2f}c"
        )


if __name__ == "__main__":
    main()
