from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from datetime import datetime, timezone

import numpy as np
import pandas as pd

import research_replay as rr


@dataclass(frozen=True)
class StrategyScenario:
    name: str
    family: str
    base_entry_cents: float
    base_qty: int
    base_fill_mode: str
    min_seconds_to_close: int
    max_seconds_to_close: int
    allowed_sessions: tuple[str, ...]
    add_levels: tuple[tuple[float, int], ...]


def session_name(ts: pd.Timestamp) -> str:
    hour = pd.Timestamp(ts).tz_convert('America/New_York').hour
    if hour <= 5:
        return 'overnight'
    if hour <= 11:
        return 'morning'
    if hour <= 17:
        return 'afternoon'
    return 'evening'


def load_result_lookup(market_results_df: pd.DataFrame) -> dict[str, str]:
    lookup: dict[str, str] = {}
    if market_results_df.empty:
        return lookup
    market_col = 'market' if 'market' in market_results_df.columns else 'market_ticker'
    result_col = 'market_result' if 'market_result' in market_results_df.columns else 'result'
    for rec in market_results_df.to_dict('records'):
        market = str(rec.get(market_col) or '')
        result = str(rec.get(result_col) or '').lower()
        if market and result in {'yes', 'no'}:
            lookup[market] = result
    return lookup


def load_grouped_raw_events(dataset_tag: str) -> tuple[dict[str, pd.DataFrame], dict[str, str]]:
    paths = rr.dataset_paths(dataset_tag)
    market_results_df = rr.load_market_results(paths['market_results_path'])
    raw_df = rr.attach_market_close_times(rr.load_raw_ticker_events(paths['raw_root']), market_results_df)
    if raw_df.empty:
        return {}, {}
    raw_df = raw_df.sort_values(['market_ticker', 'ts']).copy()
    for col in ('yes_ask_cents', 'no_ask_cents', 'seconds_to_close'):
        raw_df[col] = pd.to_numeric(raw_df[col], errors='coerce')
    groups = {str(market): grp.sort_values('ts').copy() for market, grp in raw_df.groupby('market_ticker')}
    return groups, load_result_lookup(market_results_df)


def simulate_strategy(
    groups: dict[str, pd.DataFrame],
    result_lookup: dict[str, str],
    scenario: StrategyScenario,
) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    add_thresholds = [level for level, _ in scenario.add_levels]
    add_qtys = [qty for _, qty in scenario.add_levels]
    for market, grp in groups.items():
        market_result = result_lookup.get(market)
        if market_result not in {'yes', 'no'}:
            continue
        side: str | None = None
        levels: list[tuple[float, int]] = []
        entry_ts = None
        entry_date = None
        next_add_index = 0
        for rec in grp.itertuples(index=False):
            seconds_to_close = rec.seconds_to_close
            if pd.isna(seconds_to_close):
                continue
            if not (float(scenario.min_seconds_to_close) < float(seconds_to_close) <= float(scenario.max_seconds_to_close)):
                continue
            if side is None:
                session = session_name(rec.ts)
                if session not in scenario.allowed_sessions:
                    continue
                candidates: list[tuple[str, float]] = []
                if pd.notna(rec.yes_ask_cents) and float(rec.yes_ask_cents) >= scenario.base_entry_cents:
                    candidates.append(('yes', float(rec.yes_ask_cents)))
                if pd.notna(rec.no_ask_cents) and float(rec.no_ask_cents) >= scenario.base_entry_cents:
                    candidates.append(('no', float(rec.no_ask_cents)))
                if not candidates:
                    continue
                candidates.sort(key=lambda item: item[1], reverse=True)
                side, observed_entry = candidates[0]
                base_price = scenario.base_entry_cents if scenario.base_fill_mode == 'exact' else observed_entry
                entry_ts = pd.Timestamp(rec.ts)
                entry_date = entry_ts.tz_convert('America/New_York').strftime('%Y-%m-%d')
                levels.append((float(base_price), int(scenario.base_qty)))
                continue

            same_ask = rec.yes_ask_cents if side == 'yes' else rec.no_ask_cents
            if pd.isna(same_ask):
                continue
            while next_add_index < len(add_thresholds) and float(same_ask) <= float(add_thresholds[next_add_index]):
                levels.append((float(add_thresholds[next_add_index]), int(add_qtys[next_add_index])))
                next_add_index += 1

        if not levels or side is None or entry_ts is None or entry_date is None:
            continue
        total_qty = int(sum(qty for _, qty in levels))
        avg_entry = float(sum(price * qty for price, qty in levels) / total_qty)
        settlement_price = 100.0 if market_result == side else 0.0
        pnl = round((settlement_price - avg_entry) * total_qty / 100.0, 4)
        rows.append({
            'scenario': scenario.name,
            'family': scenario.family,
            'market': market,
            'entry_ts': entry_ts,
            'entry_date': entry_date,
            'side': side,
            'market_result': market_result,
            'base_entry_cents': float(scenario.base_entry_cents),
            'base_fill_mode': scenario.base_fill_mode,
            'entry_count': int(len(levels)),
            'total_qty': total_qty,
            'avg_entry_cents': avg_entry,
            'levels_json': json.dumps([{'price_cents': price, 'qty': qty} for price, qty in levels]),
            'net_pnl_dollars': pnl,
        })
    return pd.DataFrame(rows)


def build_search_grid() -> list[StrategyScenario]:
    scenarios: list[StrategyScenario] = []
    session_modes = {
        'all': ('overnight', 'morning', 'afternoon', 'evening'),
        'overnight': ('overnight',),
        'overnight_morning': ('overnight', 'morning'),
    }
    for base in range(86, 91):
        for session_name_key, allowed_sessions in session_modes.items():
            for min_stc in (60, 120):
                scenarios.append(StrategyScenario(
                    name=f'exact_{base}_{session_name_key}_stc{min_stc}',
                    family='single_entry',
                    base_entry_cents=float(base),
                    base_qty=10,
                    base_fill_mode='exact',
                    min_seconds_to_close=min_stc,
                    max_seconds_to_close=900,
                    allowed_sessions=allowed_sessions,
                    add_levels=(),
                ))
    for base in range(86, 91):
        for add_qty in (5, 10):
            for add_count in (1, 2):
                for min_stc in (60, 120):
                    add_levels: list[tuple[float, int]] = []
                    if add_count >= 1:
                        add_levels.append((float(base - 10), int(add_qty)))
                    if add_count >= 2:
                        add_levels.append((float(base - 20), int(add_qty)))
                    scenarios.append(StrategyScenario(
                        name=f'ladder_{base}_q{add_qty}_n{add_count}_overnight_morning_stc{min_stc}',
                        family='ladder_no_stop',
                        base_entry_cents=float(base),
                        base_qty=10,
                        base_fill_mode='exact',
                        min_seconds_to_close=min_stc,
                        max_seconds_to_close=900,
                        allowed_sessions=('overnight', 'morning'),
                        add_levels=tuple(add_levels),
                    ))
    return scenarios


def summarize_search(trades_df: pd.DataFrame) -> pd.DataFrame:
    if trades_df.empty:
        return pd.DataFrame()
    all_dates = sorted(trades_df['entry_date'].dropna().unique())
    split_idx = len(all_dates) // 2
    train_dates = set(all_dates[:split_idx])
    test_dates = set(all_dates[split_idx:])
    rows: list[dict[str, object]] = []
    for scenario_name, grp in trades_df.groupby('scenario'):
        pnl = pd.to_numeric(grp['net_pnl_dollars'], errors='coerce').fillna(0.0)
        train = grp[grp['entry_date'].isin(train_dates)]
        test = grp[grp['entry_date'].isin(test_dates)]
        train_net = float(pd.to_numeric(train['net_pnl_dollars'], errors='coerce').fillna(0.0).sum()) if not train.empty else np.nan
        test_net = float(pd.to_numeric(test['net_pnl_dollars'], errors='coerce').fillna(0.0).sum()) if not test.empty else np.nan
        robust_score = float(min(train_net if not np.isnan(train_net) else -9999.0, test_net if not np.isnan(test_net) else -9999.0))
        entry_counts = pd.to_numeric(grp['entry_count'], errors='coerce')
        avg_qty = pd.to_numeric(grp['total_qty'], errors='coerce')
        avg_entry = pd.to_numeric(grp['avg_entry_cents'], errors='coerce')
        wins = pnl[pnl > 0]
        losses = pnl[pnl < 0]
        rows.append({
            'scenario': scenario_name,
            'family': str(grp.iloc[0]['family']),
            'base_entry_cents': float(pd.to_numeric(grp['base_entry_cents'], errors='coerce').dropna().iloc[0]),
            'base_fill_mode': str(grp.iloc[0]['base_fill_mode']),
            'trades': int(len(grp)),
            'wins': int((pnl > 0).sum()),
            'losses': int((pnl < 0).sum()),
            'win_rate': float((pnl > 0).mean() * 100.0),
            'net_pnl_dollars': float(pnl.sum()),
            'avg_pnl_dollars': float(pnl.mean()),
            'avg_win_dollars': float(wins.mean()) if len(wins) else np.nan,
            'avg_loss_dollars': float(losses.mean()) if len(losses) else np.nan,
            'worst_trade_dollars': float(pnl.min()),
            'avg_entry_count': float(entry_counts.mean()) if entry_counts.notna().any() else np.nan,
            'avg_total_qty': float(avg_qty.mean()) if avg_qty.notna().any() else np.nan,
            'avg_entry_cents': float(avg_entry.mean()) if avg_entry.notna().any() else np.nan,
            'train_net': train_net,
            'test_net': test_net,
            'robust_score': robust_score,
        })
    out = pd.DataFrame(rows)
    if out.empty:
        return out
    return out.sort_values(['robust_score', 'net_pnl_dollars', 'win_rate', 'trades'], ascending=[False, False, False, False]).reset_index(drop=True)


def recommended_scenario(summary_df: pd.DataFrame) -> pd.Series:
    eligible = summary_df[(summary_df['trades'] >= 200) & (summary_df['train_net'] > 0) & (summary_df['test_net'] > 0)].copy()
    if eligible.empty:
        eligible = summary_df.copy()
    return eligible.sort_values(['robust_score', 'net_pnl_dollars', 'win_rate', 'trades'], ascending=[False, False, False, False]).iloc[0]


def build_observed_variant(rec: pd.Series) -> StrategyScenario:
    add_levels_json = rec.get('scenario', '')
    # Reconstruct ladder levels from the scenario name convention.
    scenario_name = str(add_levels_json)
    add_levels: list[tuple[float, int]] = []
    if scenario_name.startswith('ladder_'):
        parts = scenario_name.split('_')
        base = float(parts[1])
        add_qty = int(parts[2].replace('q', ''))
        add_count = int(parts[3].replace('n', ''))
        if add_count >= 1:
            add_levels.append((base - 10.0, add_qty))
        if add_count >= 2:
            add_levels.append((base - 20.0, add_qty))
        min_stc = int(parts[-1].replace('stc', ''))
        return StrategyScenario(
            name=f'{scenario_name}_observed_base',
            family='ladder_no_stop_observed_base',
            base_entry_cents=base,
            base_qty=10,
            base_fill_mode='observed',
            min_seconds_to_close=min_stc,
            max_seconds_to_close=900,
            allowed_sessions=('overnight', 'morning'),
            add_levels=tuple(add_levels),
        )
    base = float(rec['base_entry_cents'])
    return StrategyScenario(
        name=f'{scenario_name}_observed_base',
        family=str(rec['family']) + '_observed_base',
        base_entry_cents=base,
        base_qty=10,
        base_fill_mode='observed',
        min_seconds_to_close=120,
        max_seconds_to_close=900,
        allowed_sessions=('overnight', 'morning'),
        add_levels=(),
    )


def main() -> None:
    parser = argparse.ArgumentParser(description='Search for the strongest continuation strategy on a research dataset.')
    parser.add_argument('--dataset', required=True)
    args = parser.parse_args()

    groups, result_lookup = load_grouped_raw_events(args.dataset)
    if not groups:
        raise RuntimeError(f'No raw events found for dataset {args.dataset}')

    scenarios = build_search_grid()
    trade_frames = [simulate_strategy(groups, result_lookup, scenario) for scenario in scenarios]
    trades_df = pd.concat([df for df in trade_frames if not df.empty], ignore_index=True)
    if trades_df.empty:
        raise RuntimeError(f'Strategy search returned no trades for dataset {args.dataset}')
    summary_df = summarize_search(trades_df)
    if summary_df.empty:
        raise RuntimeError(f'Strategy search returned no summary rows for dataset {args.dataset}')

    recommended = recommended_scenario(summary_df)
    observed_variant = build_observed_variant(recommended)
    observed_trades_df = simulate_strategy(groups, result_lookup, observed_variant)
    observed_summary_df = summarize_search(observed_trades_df)

    run_id = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    paths = rr.dataset_paths(args.dataset)
    run_dir = paths['replay_root'] / f'run_id={run_id}'
    run_dir.mkdir(parents=True, exist_ok=True)
    summary_df.to_parquet(run_dir / 'best_strategy_search_summary.parquet', index=False)
    trades_df.to_parquet(run_dir / 'best_strategy_search_trades.parquet', index=False)
    observed_trades_df.to_parquet(run_dir / 'best_strategy_observed_variant_trades.parquet', index=False)
    observed_summary_df.to_parquet(run_dir / 'best_strategy_observed_variant_summary.parquet', index=False)

    payload = {
        'dataset_tag': args.dataset,
        'run_id': run_id,
        'built_at': datetime.now(timezone.utc).isoformat(),
        'scenario_rows': int(len(summary_df)),
        'trade_rows': int(len(trades_df)),
        'recommended_scenario': str(recommended['scenario']),
        'recommended_family': str(recommended['family']),
        'recommended_metrics': {
            'trades': int(recommended['trades']),
            'win_rate': float(recommended['win_rate']),
            'net_pnl_dollars': float(recommended['net_pnl_dollars']),
            'avg_pnl_dollars': float(recommended['avg_pnl_dollars']),
            'train_net': float(recommended['train_net']),
            'test_net': float(recommended['test_net']),
            'robust_score': float(recommended['robust_score']),
            'worst_trade_dollars': float(recommended['worst_trade_dollars']),
            'avg_total_qty': float(recommended['avg_total_qty']),
            'avg_entry_cents': float(recommended['avg_entry_cents']),
        },
        'top_net_scenario': str(summary_df.sort_values('net_pnl_dollars', ascending=False).iloc[0]['scenario']),
        'top_net_metrics': {
            'net_pnl_dollars': float(summary_df.sort_values('net_pnl_dollars', ascending=False).iloc[0]['net_pnl_dollars']),
            'win_rate': float(summary_df.sort_values('net_pnl_dollars', ascending=False).iloc[0]['win_rate']),
            'robust_score': float(summary_df.sort_values('net_pnl_dollars', ascending=False).iloc[0]['robust_score']),
        },
        'observed_base_variant': observed_summary_df.iloc[0].to_dict() if not observed_summary_df.empty else None,
    }
    (paths['metadata_root'] / 'best_strategy_status.json').write_text(json.dumps(payload, indent=2), encoding='utf-8')
    print(json.dumps(payload, indent=2))


if __name__ == '__main__':
    main()
