from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np

import ou_mispricing_strategy_lab as lab
import run_ou_mispricing_broad_backtest as broad


ROOT = Path(__file__).resolve().parent
REPORT_DIR = ROOT / "logs" / "particle_research" / "reports"
DOCS_DIR = ROOT / "docs" / "research"


BASE_VERY_STRICT: dict[str, Any] = {
    **broad.BASE_SETTINGS,
    "entry_z_min": 8.0,
    "min_raw_edge_cents": 4.0,
    "min_sim_ev_cents": 3.0,
    "max_loss_prob": 0.48,
    "max_spread_cents": 3.0,
    "sim_paths": 1200,
    "choice_objective": "expected",
    "allowed_sides": "yes,no",
    "exit_before_close_seconds": 0.0,
}


REFINEMENT_VARIANTS: dict[str, dict[str, Any]] = {
    "control_very_strict_1200": {},
    "no_only": {
        "allowed_sides": "no",
    },
    "yes_only": {
        "allowed_sides": "yes",
    },
    "no_only_fast_hold": {
        "allowed_sides": "no",
        "hold_values": "30,60,120",
        "pt_values": "3,5,8,12",
        "sl_values": "4,8,12,20",
    },
    "no_only_fast_hold_tight_gate": {
        "allowed_sides": "no",
        "hold_values": "30,60,120",
        "pt_values": "3,5,8,12",
        "sl_values": "4,8,12,20",
        "min_sim_ev_cents": 4.0,
        "max_loss_prob": 0.44,
    },
    "no_only_mid_window": {
        "allowed_sides": "no",
        "min_seconds_to_close": 90.0,
        "max_seconds_to_close": 420.0,
        "hold_values": "30,60,120,240",
    },
    "no_only_early_window": {
        "allowed_sides": "no",
        "min_seconds_to_close": 120.0,
        "max_seconds_to_close": 300.0,
        "hold_values": "30,60,120,240",
    },
    "no_only_preclose_90": {
        "allowed_sides": "no",
        "exit_before_close_seconds": 90.0,
    },
    "both_sides_preclose_90": {
        "exit_before_close_seconds": 90.0,
    },
    "both_sides_sharpe_objective": {
        "choice_objective": "sharpe",
    },
    "no_only_sharpe_objective": {
        "allowed_sides": "no",
        "choice_objective": "sharpe",
    },
    "no_only_small_tp_grid": {
        "allowed_sides": "no",
        "pt_values": "3,5,8",
        "sl_values": "8,12,20,35",
        "hold_values": "30,60,120,240",
    },
    "no_only_lossprob_40": {
        "allowed_sides": "no",
        "max_loss_prob": 0.40,
        "min_sim_ev_cents": 4.0,
    },
}


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def parse_allowed_sides(value: Any) -> set[str]:
    sides = {part.strip().lower() for part in str(value or "yes,no").split(",") if part.strip()}
    return {side for side in sides if side in {"yes", "no"}} or {"yes", "no"}


def simulate_choice(
    *,
    z0: float,
    side: str,
    fit: lab.OUFitted,
    entry_ask: float,
    entry_mid: float,
    exit_spread_cost: float,
    sample_seconds: float,
    pt_values: list[float],
    sl_values: list[float],
    hold_values: list[float],
    n_paths: int,
    rng: np.random.Generator,
    objective: str,
) -> lab.SimChoice:
    if not fit.ok:
        return lab.SimChoice(ok=False, reason=fit.reason)
    if not (-0.25 <= fit.phi <= 1.02):
        return lab.SimChoice(ok=False, reason="unstable_phi")
    max_steps = max(1, int(np.ceil(max(hold_values) / max(1.0, sample_seconds))))
    shocks = rng.standard_normal(size=(max_steps, int(n_paths)))
    paths = np.empty((max_steps + 1, int(n_paths)), dtype=float)
    paths[0] = float(z0)
    phi = max(-0.25, min(1.02, fit.phi))
    for step in range(1, max_steps + 1):
        paths[step] = fit.mu + phi * (paths[step - 1] - fit.mu) + fit.sigma * shocks[step - 1]

    direction = 1.0 if side == "yes" else -1.0
    entry_cost = max(0.0, entry_ask - entry_mid)
    fee_cents = lab.estimated_order_fee_cents(entry_ask, 1) + lab.estimated_order_fee_cents(entry_ask, 1)
    fixed_cost = entry_cost + max(0.0, exit_spread_cost) + fee_cents

    best: lab.SimChoice | None = None
    for hold_seconds in hold_values:
        steps = max(1, min(max_steps, int(np.ceil(hold_seconds / max(1.0, sample_seconds)))))
        deltas = direction * (paths[: steps + 1] - float(z0))
        for pt in pt_values:
            hit_pt = deltas >= float(pt)
            for sl in sl_values:
                hit_sl = deltas <= -float(sl)
                pnl = deltas[steps].copy()
                done = np.zeros(int(n_paths), dtype=bool)
                for step in range(1, steps + 1):
                    active = ~done
                    if not active.any():
                        break
                    sl_now = active & hit_sl[step]
                    pt_now = active & hit_pt[step] & ~sl_now
                    if pt_now.any():
                        pnl[pt_now] = float(pt)
                        done[pt_now] = True
                    if sl_now.any():
                        pnl[sl_now] = -float(sl)
                        done[sl_now] = True
                net = pnl - fixed_cost
                mean = float(net.mean())
                std = float(net.std(ddof=1))
                sharpe = mean / std if std > 1e-9 else (999.0 if mean > 0 else 0.0)
                loss_prob = float((net < 0).mean())
                choice = lab.SimChoice(
                    ok=True,
                    pt_cents=float(pt),
                    sl_cents=float(sl),
                    max_hold_seconds=float(hold_seconds),
                    expected_net_cents=mean,
                    std_net_cents=std,
                    sharpe_like=sharpe,
                    loss_prob=loss_prob,
                )
                if objective == "sharpe":
                    score = (choice.sharpe_like, choice.expected_net_cents, -choice.loss_prob)
                    best_score = None if best is None else (best.sharpe_like, best.expected_net_cents, -best.loss_prob)
                else:
                    score = (choice.expected_net_cents, choice.sharpe_like, -choice.loss_prob)
                    best_score = None if best is None else (best.expected_net_cents, best.sharpe_like, -best.loss_prob)
                if best is None or score > best_score:
                    best = choice
    return best or lab.SimChoice(ok=False, reason="no_candidates")


def choose_side(row: lab.Snapshot, allowed_sides: set[str]) -> tuple[str | None, float, bool]:
    yes_edge = row.fair_yes - row.yes_ask - lab.estimated_order_fee_cents(row.yes_ask, 1)
    no_edge = (100.0 - row.fair_yes) - row.no_ask - lab.estimated_order_fee_cents(row.no_ask, 1)
    candidates: list[tuple[float, str]] = []
    if "yes" in allowed_sides:
        candidates.append((yes_edge, "yes"))
    if "no" in allowed_sides:
        candidates.append((no_edge, "no"))
    if not candidates:
        return None, 0.0, False
    raw_edge, side = max(candidates, key=lambda item: item[0])
    aligned_z = row.z <= 0.0 if side == "yes" else row.z >= 0.0
    return side, raw_edge, aligned_z


def close_open_positions(
    *,
    row: lab.Snapshot,
    open_pos: dict[str, lab.Position],
    trades: list[dict[str, Any]],
    market_results: dict[str, lab.MarketResult],
    exit_before_close_seconds: float,
) -> None:
    pos = open_pos.get(row.market)
    if pos is None:
        return
    side_bid = row.side_bid(pos.side)
    pnl_cents = side_bid - pos.entry_price
    age = max(0.0, (row.ts - pos.entry_ts).total_seconds())
    close_reason = ""
    exit_price = side_bid
    settlement = False
    if pnl_cents >= pos.pt_cents:
        close_reason = "take_profit"
    elif pnl_cents <= -pos.sl_cents:
        close_reason = "stop_loss"
    elif age >= pos.max_hold_seconds:
        close_reason = "max_hold"
    elif exit_before_close_seconds > 0 and row.seconds_to_close <= exit_before_close_seconds:
        close_reason = "preclose_exit"
    elif row.seconds_to_close <= 1:
        settle = lab.result_settlement_cents(market_results.get(row.market), pos.side)
        if settle is not None:
            close_reason = "settlement"
            exit_price = settle
            settlement = True
    if close_reason:
        trades.append(lab.close_position(pos, row, exit_price=exit_price, exit_reason=close_reason, settlement=settlement))
        open_pos.pop(row.market, None)


def run_refined_backtest(
    snapshots: list[lab.Snapshot],
    market_results: dict[str, lab.MarketResult],
    settings: dict[str, Any],
) -> dict[str, Any]:
    rng = np.random.default_rng(int(settings["seed"]))
    z_history: list[float] = []
    open_pos: dict[str, lab.Position] = {}
    traded_markets: set[str] = set()
    trades: list[dict[str, Any]] = []
    rejects = defaultdict(int)
    decisions = 0
    allowed_sides = parse_allowed_sides(settings.get("allowed_sides"))
    entry_z_min = float(settings["entry_z_min"])
    exit_before_close_seconds = float(settings.get("exit_before_close_seconds") or 0.0)

    for row in snapshots:
        close_open_positions(
            row=row,
            open_pos=open_pos,
            trades=trades,
            market_results=market_results,
            exit_before_close_seconds=exit_before_close_seconds,
        )

        z_history.append(row.z)
        if len(z_history) < int(settings["min_ou_points"]):
            rejects["warming"] += 1
            continue
        z_lookback = int(settings["z_lookback"])
        if len(z_history) > max(z_lookback * 2, z_lookback + 10):
            z_history = z_history[-z_lookback:]
        if bool(settings.get("one_entry_per_market", True)) and row.market in traded_markets:
            rejects["one_entry_per_market"] += 1
            continue
        if row.market in open_pos:
            rejects["already_open"] += 1
            continue
        if not (float(settings["min_seconds_to_close"]) <= row.seconds_to_close <= float(settings["max_seconds_to_close"])):
            rejects["time_window"] += 1
            continue

        side, raw_edge, coarse_aligned = choose_side(row, allowed_sides)
        if side is None:
            rejects["side_filter"] += 1
            continue
        aligned_z = row.z <= -entry_z_min if side == "yes" else row.z >= entry_z_min
        if raw_edge < float(settings["min_raw_edge_cents"]) or not coarse_aligned or not aligned_z:
            rejects["edge_or_z"] += 1
            continue
        if row.side_spread(side) > float(settings["max_spread_cents"]):
            rejects["spread"] += 1
            continue

        fit = lab.fit_ou(z_history[-z_lookback:], min_points=int(settings["min_ou_points"]))
        if not fit.ok:
            rejects[f"ou_{fit.reason}"] += 1
            continue
        choice = simulate_choice(
            z0=row.z,
            side=side,
            fit=fit,
            entry_ask=row.side_ask(side),
            entry_mid=row.side_mid(side),
            exit_spread_cost=row.side_spread(side) / 2.0,
            sample_seconds=float(settings["sample_seconds"]),
            pt_values=lab.parse_float_list(str(settings["pt_values"])),
            sl_values=lab.parse_float_list(str(settings["sl_values"])),
            hold_values=lab.parse_float_list(str(settings["hold_values"])),
            n_paths=int(settings["sim_paths"]),
            rng=rng,
            objective=str(settings.get("choice_objective") or "expected"),
        )
        decisions += 1
        if not choice.ok:
            rejects[f"sim_{choice.reason}"] += 1
            continue
        if choice.expected_net_cents < float(settings["min_sim_ev_cents"]) or choice.loss_prob > float(settings["max_loss_prob"]):
            rejects["sim_gate"] += 1
            continue

        open_pos[row.market] = lab.Position(
            entry_ts=row.ts,
            entry_market=row.market,
            side=side,
            entry_price=row.side_ask(side),
            entry_fee_cents=float(lab.estimated_order_fee_cents(row.side_ask(side), 1)),
            pt_cents=choice.pt_cents,
            sl_cents=choice.sl_cents,
            max_hold_seconds=choice.max_hold_seconds,
            sim_expected_net_cents=choice.expected_net_cents,
            sim_sharpe_like=choice.sharpe_like,
            entry_fair_side=row.fair_side(side),
            entry_z=row.z,
            entry_seconds_to_close=row.seconds_to_close,
        )
        traded_markets.add(row.market)

    rows_by_market: dict[str, list[lab.Snapshot]] = defaultdict(list)
    for row in snapshots:
        rows_by_market[row.market].append(row)
    for market, pos in list(open_pos.items()):
        market_rows = rows_by_market.get(market) or []
        if not market_rows:
            continue
        last = market_rows[-1]
        settle = lab.result_settlement_cents(market_results.get(market), pos.side)
        if settle is not None:
            trades.append(lab.close_position(pos, last, exit_price=settle, exit_reason="settlement_after_tape", settlement=True))
        else:
            trades.append(
                lab.close_position(pos, last, exit_price=last.side_bid(pos.side), exit_reason="last_bid_after_tape", settlement=False)
            )

    pnls = np.array([float(row["net_pnl_dollars"]) for row in trades], dtype=float)
    by_reason = Counter(str(row["exit_reason"]) for row in trades)
    return {
        "summary": {
            "snapshot_count": len(snapshots),
            "markets": len({row.market for row in snapshots}),
            "trade_count": len(trades),
            "net_pnl_dollars": round(float(pnls.sum()), 4) if len(pnls) else 0.0,
            "mean_trade_pnl_dollars": round(float(pnls.mean()), 6) if len(pnls) else 0.0,
            "std_trade_pnl_dollars": round(float(pnls.std(ddof=1)), 6) if len(pnls) > 1 else 0.0,
            "win_rate": round(float((pnls > 0).mean()), 4) if len(pnls) else None,
            "wins": int((pnls > 0).sum()) if len(pnls) else 0,
            "losses": int((pnls < 0).sum()) if len(pnls) else 0,
            "sim_decisions_scored": int(decisions),
            "rejects": dict(sorted(rejects.items())),
            "exit_reasons": dict(sorted(by_reason.items())),
        },
        "trades": trades,
    }


def diagnostics(trades: list[dict[str, Any]]) -> dict[str, Any]:
    by_day: dict[str, dict[str, Any]] = defaultdict(lambda: {"trades": 0, "pnl": 0.0})
    by_side: dict[str, dict[str, Any]] = defaultdict(lambda: {"trades": 0, "pnl": 0.0})
    by_reason: dict[str, dict[str, Any]] = defaultdict(lambda: {"trades": 0, "pnl": 0.0})
    for trade in trades:
        pnl = float(trade.get("net_pnl_dollars") or 0.0)
        day = str(trade.get("entry_ts") or "")[:10]
        side = str(trade.get("side") or "")
        reason = str(trade.get("exit_reason") or "")
        for bucket, key in ((by_day, day), (by_side, side), (by_reason, reason)):
            bucket[key]["trades"] += 1
            bucket[key]["pnl"] += pnl
    days = [{"day": key, "trades": value["trades"], "pnl": round(value["pnl"], 4)} for key, value in sorted(by_day.items())]
    thirds = []
    sorted_trades = sorted(trades, key=lambda item: str(item.get("entry_ts") or ""))
    if sorted_trades:
        chunk = max(1, int(np.ceil(len(sorted_trades) / 3.0)))
        for idx in range(0, len(sorted_trades), chunk):
            part = sorted_trades[idx : idx + chunk]
            pnl = sum(float(row.get("net_pnl_dollars") or 0.0) for row in part)
            thirds.append(
                {
                    "segment": len(thirds) + 1,
                    "trades": len(part),
                    "pnl": round(pnl, 4),
                    "first_entry": str(part[0].get("entry_ts") or "")[:19],
                    "last_entry": str(part[-1].get("entry_ts") or "")[:19],
                }
            )
    return {
        "by_day": days,
        "positive_days": sum(1 for row in days if float(row["pnl"]) > 0.0),
        "nonpositive_days": sum(1 for row in days if float(row["pnl"]) <= 0.0),
        "by_side": [{"side": key, "trades": value["trades"], "pnl": round(value["pnl"], 4)} for key, value in sorted(by_side.items())],
        "by_exit_reason": [
            {"exit_reason": key, "trades": value["trades"], "pnl": round(value["pnl"], 4)}
            for key, value in sorted(by_reason.items())
        ],
        "chronological_thirds": thirds,
    }


def build_dataset() -> tuple[list[lab.Snapshot], dict[str, lab.MarketResult], dict[str, Any]]:
    event_paths, event_manifest = broad.discover_event_files()
    combined_results_path, market_results, label_meta = broad.combine_market_results()
    execution_raw = lab.load_snapshots(event_paths, market_results)
    native_raw, native_meta = broad.load_native_snapshots()
    raw, duplicate_snapshot_count = broad.dedupe_snapshots(execution_raw + native_raw)
    enriched = lab.add_fair_values(
        raw,
        vol_lookback_seconds=float(broad.BASE_SETTINGS["vol_lookback_seconds"]),
        min_vol_points=int(broad.BASE_SETTINGS["min_vol_points"]),
        fallback_sigma_per_sqrt_s=float(broad.BASE_SETTINGS["fallback_sigma_per_sqrt_s"]),
    )
    sampled = lab.downsample_snapshots(enriched, sample_seconds=float(broad.BASE_SETTINGS["sample_seconds"]))
    inputs = {
        "event_file_count": len(event_paths),
        "event_manifest": event_manifest,
        "selected_event_files": len(event_paths),
        "duplicate_event_files": sum(1 for row in event_manifest if row["duplicate_by_hash"]),
        "combined_market_results_csv": str(combined_results_path),
        "combined_market_result_rows": len(market_results),
        "label_meta": label_meta,
        "execution_snapshot_count": len(execution_raw),
        "native_snapshot_count": len(native_raw),
        "native_meta": native_meta,
        "duplicate_snapshot_count": duplicate_snapshot_count,
        "raw_snapshot_count": len(raw),
        "fair_snapshot_count": len(enriched),
        "sampled_snapshot_count": len(sampled),
        "sampled_markets": len({row.market for row in sampled}),
    }
    return sampled, market_results, inputs


def render_report(payload: dict[str, Any]) -> str:
    lines = [
        "# OU Mispricing Refinement Sweep",
        "",
        f"Generated: {payload['generated_utc']}",
        "",
        "Research-only. No live bot logic, state, processes, or orders were changed.",
        "",
        "## Data",
        "",
        f"- Markets: {payload['inputs']['sampled_markets']}",
        f"- Downsampled snapshots: {payload['inputs']['sampled_snapshot_count']}",
        f"- Execution-event snapshots: {payload['inputs']['execution_snapshot_count']}",
        f"- Native passive snapshots: {payload['inputs']['native_snapshot_count']}",
        "",
        "## Results",
        "",
        "| Rank | Variant | Trades | Net PnL | Win rate | Avg/trade | Positive days | Sim decisions |",
        "|---:|---|---:|---:|---:|---:|---:|---:|",
    ]
    ranked = sorted(payload["variants"], key=lambda row: row["summary"]["net_pnl_dollars"], reverse=True)
    for idx, row in enumerate(ranked, start=1):
        summary = row["summary"]
        diag = row["diagnostics"]
        day_text = f"{diag['positive_days']}/{diag['positive_days'] + diag['nonpositive_days']}"
        lines.append(
            f"| {idx} | {row['variant']} | {summary['trade_count']} | ${summary['net_pnl_dollars']:.2f} | "
            f"{summary['win_rate']:.2%} | {summary['mean_trade_pnl_dollars'] * 100:.2f}c | "
            f"{day_text} | {summary['sim_decisions_scored']} |"
        )
    lines.extend(["", "## Best Variant Diagnostics", ""])
    if ranked:
        best = ranked[0]
        lines.extend(
            [
                f"Best by net PnL: `{best['variant']}`.",
                "",
                "| Side | Trades | PnL |",
                "|---|---:|---:|",
            ]
        )
        for row in best["diagnostics"]["by_side"]:
            lines.append(f"| {row['side']} | {row['trades']} | ${row['pnl']:.2f} |")
        lines.extend(["", "| Exit reason | Trades | PnL |", "|---|---:|---:|"])
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
            "## Interpretation",
            "",
            "This sweep is still retrospective. Treat it as a filter for the next shadow candidate, not as deployment proof.",
            "A refinement only matters if it improves broad PnL without collapsing sample size and without relying on a single late segment.",
        ]
    )
    return "\n".join(lines) + "\n"


def write_variant_trades(name: str, trades: list[dict[str, Any]]) -> str:
    path = REPORT_DIR / f"ou_mispricing_refinement_trades_{name}.csv"
    if not trades:
        path.write_text("", encoding="utf-8")
        return str(path)
    with path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(trades[0].keys()))
        writer.writeheader()
        writer.writerows(trades)
    return str(path)


def main() -> None:
    snapshots, market_results, inputs = build_dataset()
    variants: list[dict[str, Any]] = []
    for name, overrides in REFINEMENT_VARIANTS.items():
        settings = {**BASE_VERY_STRICT, **overrides}
        settings["one_entry_per_market"] = not bool(settings.get("allow_reentry", False))
        report = run_refined_backtest(snapshots, market_results, settings)
        diag = diagnostics(report["trades"])
        trades_csv = write_variant_trades(name, report["trades"])
        variants.append(
            {
                "variant": name,
                "settings": settings,
                "summary": report["summary"],
                "diagnostics": diag,
                "trades_csv": trades_csv,
            }
        )

    payload = {
        "generated_utc": utc_now_iso(),
        "inputs": inputs,
        "variants": variants,
    }
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    DOCS_DIR.mkdir(parents=True, exist_ok=True)
    json_path = REPORT_DIR / "ou_mispricing_refinement_sweep.json"
    md_path = DOCS_DIR / "OU_MISPRICING_REFINEMENT_SWEEP_VERDICT.md"
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
