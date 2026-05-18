from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from math import ceil

import pandas as pd

import research_replay as rr


@dataclass(frozen=True)
class SingleStrategy:
    name: str
    session_key: str
    allowed_sessions: tuple[str, ...]
    threshold_cents: float
    min_seconds_to_close: int
    max_seconds_to_close: int
    qty: int = 10


@dataclass(frozen=True)
class LadderStrategy:
    name: str
    session_key: str
    allowed_sessions: tuple[str, ...]
    base_threshold_cents: float
    add_levels: tuple[tuple[float, int], ...]
    min_seconds_to_close: int
    max_seconds_to_close: int
    base_qty: int = 10


def session_name(ts: pd.Timestamp) -> str:
    hour = pd.Timestamp(ts).tz_convert('America/New_York').hour
    if hour <= 5:
        return 'overnight'
    if hour <= 11:
        return 'morning'
    if hour <= 17:
        return 'afternoon'
    return 'evening'


def estimate_entry_fee_dollars(price_cents: float, qty: int) -> float:
    if qty <= 0 or price_cents <= 0 or price_cents >= 100:
        return 0.0
    probability = float(price_cents) / 100.0
    raw_fee_dollars = 0.07 * int(qty) * probability * (1.0 - probability)
    return float(ceil(raw_fee_dollars * 100.0) / 100.0)


def load_groups(dataset_tag: str) -> tuple[dict[str, pd.DataFrame], dict[str, str], list[str]]:
    paths = rr.dataset_paths(dataset_tag)
    market_results_df = rr.load_market_results(paths['market_results_path'])
    raw_df = rr.attach_market_close_times(rr.load_raw_ticker_events(paths['raw_root']), market_results_df)
    if raw_df.empty:
        return {}, {}, []
    raw_df = raw_df.sort_values(['market_ticker', 'ts']).copy()
    raw_df['session'] = raw_df['ts'].map(session_name)
    raw_df['entry_date'] = (
        pd.to_datetime(raw_df['ts'], utc=True)
        .dt.tz_convert('America/New_York')
        .dt.strftime('%Y-%m-%d')
    )
    result_lookup = {}
    market_col = 'market' if 'market' in market_results_df.columns else 'market_ticker'
    result_col = 'market_result' if 'market_result' in market_results_df.columns else 'result'
    for rec in market_results_df.to_dict('records'):
        market = str(rec.get(market_col) or '')
        result = str(rec.get(result_col) or '').lower()
        if market and result in {'yes', 'no'}:
            result_lookup[market] = result
    groups = {str(market): grp.sort_values('ts').copy() for market, grp in raw_df.groupby('market_ticker')}
    all_dates = sorted(raw_df['entry_date'].dropna().unique().tolist())
    return groups, result_lookup, all_dates


def empty_trades() -> pd.DataFrame:
    return pd.DataFrame(
        columns=['strategy', 'session_key', 'market', 'entry_ts', 'entry_date', 'side', 'entry', 'qty', 'gross', 'net', 'won']
    )


def simulate_single(
    groups: dict[str, pd.DataFrame],
    result_lookup: dict[str, str],
    config: SingleStrategy,
) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for market, grp in groups.items():
        result = result_lookup.get(market)
        if result not in {'yes', 'no'}:
            continue
        chosen: dict[str, object] | None = None
        for rec in grp.itertuples(index=False):
            seconds_to_close = pd.to_numeric(pd.Series([rec.seconds_to_close]), errors='coerce').iloc[0]
            if pd.isna(seconds_to_close):
                continue
            if not (float(config.min_seconds_to_close) < float(seconds_to_close) <= float(config.max_seconds_to_close)):
                continue
            if str(rec.session) not in config.allowed_sessions:
                continue
            candidates: list[tuple[str, float]] = []
            yes_ask = pd.to_numeric(pd.Series([rec.yes_ask_cents]), errors='coerce').iloc[0]
            no_ask = pd.to_numeric(pd.Series([rec.no_ask_cents]), errors='coerce').iloc[0]
            if pd.notna(yes_ask) and float(yes_ask) >= float(config.threshold_cents):
                candidates.append(('yes', float(yes_ask)))
            if pd.notna(no_ask) and float(no_ask) >= float(config.threshold_cents):
                candidates.append(('no', float(no_ask)))
            if not candidates:
                continue
            candidates.sort(key=lambda item: item[1], reverse=True)
            side, entry = candidates[0]
            gross = ((100.0 if result == side else 0.0) - entry) * int(config.qty) / 100.0
            net = gross - estimate_entry_fee_dollars(entry, int(config.qty))
            chosen = {
                'strategy': config.name,
                'session_key': config.session_key,
                'market': market,
                'entry_ts': pd.Timestamp(rec.ts),
                'entry_date': str(rec.entry_date),
                'side': side,
                'entry': float(entry),
                'qty': int(config.qty),
                'gross': float(gross),
                'net': float(net),
                'won': int(result == side),
            }
            break
        if chosen is not None:
            rows.append(chosen)
    return pd.DataFrame(rows) if rows else empty_trades()


def simulate_ladder(
    groups: dict[str, pd.DataFrame],
    result_lookup: dict[str, str],
    config: LadderStrategy,
) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for market, grp in groups.items():
        result = result_lookup.get(market)
        if result not in {'yes', 'no'}:
            continue
        side: str | None = None
        entry_ts: pd.Timestamp | None = None
        entry_date: str | None = None
        levels: list[tuple[float, int]] = []
        next_add_index = 0
        for rec in grp.itertuples(index=False):
            seconds_to_close = pd.to_numeric(pd.Series([rec.seconds_to_close]), errors='coerce').iloc[0]
            if pd.isna(seconds_to_close):
                continue
            if not (float(config.min_seconds_to_close) < float(seconds_to_close) <= float(config.max_seconds_to_close)):
                continue
            if str(rec.session) not in config.allowed_sessions:
                continue
            if side is None:
                candidates: list[tuple[str, float]] = []
                yes_ask = pd.to_numeric(pd.Series([rec.yes_ask_cents]), errors='coerce').iloc[0]
                no_ask = pd.to_numeric(pd.Series([rec.no_ask_cents]), errors='coerce').iloc[0]
                if pd.notna(yes_ask) and float(yes_ask) >= float(config.base_threshold_cents):
                    candidates.append(('yes', float(yes_ask)))
                if pd.notna(no_ask) and float(no_ask) >= float(config.base_threshold_cents):
                    candidates.append(('no', float(no_ask)))
                if not candidates:
                    continue
                candidates.sort(key=lambda item: item[1], reverse=True)
                side, observed_entry = candidates[0]
                entry_ts = pd.Timestamp(rec.ts)
                entry_date = str(rec.entry_date)
                levels.append((float(observed_entry), int(config.base_qty)))
                continue
            same_ask = pd.to_numeric(
                pd.Series([rec.yes_ask_cents if side == 'yes' else rec.no_ask_cents]),
                errors='coerce',
            ).iloc[0]
            if pd.isna(same_ask):
                continue
            while next_add_index < len(config.add_levels) and float(same_ask) <= float(config.add_levels[next_add_index][0]):
                add_price, add_qty = config.add_levels[next_add_index]
                levels.append((float(add_price), int(add_qty)))
                next_add_index += 1
        if not levels or side is None or entry_ts is None or entry_date is None:
            continue
        total_qty = int(sum(qty for _, qty in levels))
        avg_entry = float(sum(price * qty for price, qty in levels) / total_qty)
        gross = ((100.0 if result == side else 0.0) - avg_entry) * total_qty / 100.0
        total_fees = float(sum(estimate_entry_fee_dollars(price, qty) for price, qty in levels))
        net = gross - total_fees
        rows.append({
            'strategy': config.name,
            'session_key': config.session_key,
            'market': market,
            'entry_ts': entry_ts,
            'entry_date': entry_date,
            'side': side,
            'entry': avg_entry,
            'qty': total_qty,
            'gross': float(gross),
            'net': float(net),
            'won': int(result == side),
        })
    return pd.DataFrame(rows) if rows else empty_trades()


def summarize_trades(trades_df: pd.DataFrame, train_dates: set[str], test_dates: set[str]) -> dict[str, float | int]:
    if trades_df.empty:
        return {
            'trades': 0,
            'gross': 0.0,
            'net': 0.0,
            'win_rate': float('nan'),
            'train_net': 0.0,
            'test_net': 0.0,
            'robust': 0.0,
            'worst_trade': 0.0,
        }
    train = trades_df[trades_df['entry_date'].isin(train_dates)]
    test = trades_df[trades_df['entry_date'].isin(test_dates)]
    train_net = float(pd.to_numeric(train['net'], errors='coerce').fillna(0.0).sum())
    test_net = float(pd.to_numeric(test['net'], errors='coerce').fillna(0.0).sum())
    return {
        'trades': int(len(trades_df)),
        'gross': float(pd.to_numeric(trades_df['gross'], errors='coerce').fillna(0.0).sum()),
        'net': float(pd.to_numeric(trades_df['net'], errors='coerce').fillna(0.0).sum()),
        'win_rate': float((pd.to_numeric(trades_df['won'], errors='coerce').fillna(0.0) > 0).mean() * 100.0),
        'train_net': train_net,
        'test_net': test_net,
        'robust': float(min(train_net, test_net)),
        'worst_trade': float(pd.to_numeric(trades_df['net'], errors='coerce').fillna(0.0).min()),
    }


def build_candidate_library(
    groups: dict[str, pd.DataFrame],
    result_lookup: dict[str, str],
) -> tuple[dict[str, pd.DataFrame], dict[str, list[str]], pd.DataFrame]:
    candidates = [
        LadderStrategy(
            name='overnight_ladder_87_77_67',
            session_key='overnight',
            allowed_sessions=('overnight',),
            base_threshold_cents=87.0,
            add_levels=((77.0, 10), (67.0, 10)),
            min_seconds_to_close=120,
            max_seconds_to_close=900,
        ),
        LadderStrategy(
            name='overnight_ladder_87_77',
            session_key='overnight',
            allowed_sessions=('overnight',),
            base_threshold_cents=87.0,
            add_levels=((77.0, 10),),
            min_seconds_to_close=120,
            max_seconds_to_close=900,
        ),
        SingleStrategy(
            name='overnight_single_87',
            session_key='overnight',
            allowed_sessions=('overnight',),
            threshold_cents=87.0,
            min_seconds_to_close=120,
            max_seconds_to_close=900,
        ),
        SingleStrategy(
            name='overnight_single_92',
            session_key='overnight',
            allowed_sessions=('overnight',),
            threshold_cents=92.0,
            min_seconds_to_close=120,
            max_seconds_to_close=900,
        ),
        SingleStrategy(
            name='morning_single_86',
            session_key='morning',
            allowed_sessions=('morning',),
            threshold_cents=86.0,
            min_seconds_to_close=60,
            max_seconds_to_close=900,
        ),
        SingleStrategy(
            name='morning_single_90_late',
            session_key='morning',
            allowed_sessions=('morning',),
            threshold_cents=90.0,
            min_seconds_to_close=600,
            max_seconds_to_close=900,
        ),
        SingleStrategy(
            name='morning_single_88_late',
            session_key='morning',
            allowed_sessions=('morning',),
            threshold_cents=88.0,
            min_seconds_to_close=600,
            max_seconds_to_close=900,
        ),
        SingleStrategy(
            name='morning_single_99',
            session_key='morning',
            allowed_sessions=('morning',),
            threshold_cents=99.0,
            min_seconds_to_close=120,
            max_seconds_to_close=600,
        ),
        SingleStrategy(
            name='afternoon_single_96',
            session_key='afternoon',
            allowed_sessions=('afternoon',),
            threshold_cents=96.0,
            min_seconds_to_close=300,
            max_seconds_to_close=900,
        ),
        SingleStrategy(
            name='afternoon_single_96_late',
            session_key='afternoon',
            allowed_sessions=('afternoon',),
            threshold_cents=96.0,
            min_seconds_to_close=600,
            max_seconds_to_close=900,
        ),
        SingleStrategy(
            name='afternoon_single_87_late',
            session_key='afternoon',
            allowed_sessions=('afternoon',),
            threshold_cents=87.0,
            min_seconds_to_close=600,
            max_seconds_to_close=900,
        ),
        SingleStrategy(
            name='evening_single_90_fast',
            session_key='evening',
            allowed_sessions=('evening',),
            threshold_cents=90.0,
            min_seconds_to_close=60,
            max_seconds_to_close=120,
        ),
        SingleStrategy(
            name='evening_single_93_fast',
            session_key='evening',
            allowed_sessions=('evening',),
            threshold_cents=93.0,
            min_seconds_to_close=60,
            max_seconds_to_close=120,
        ),
        SingleStrategy(
            name='evening_single_95_fast',
            session_key='evening',
            allowed_sessions=('evening',),
            threshold_cents=95.0,
            min_seconds_to_close=60,
            max_seconds_to_close=120,
        ),
    ]

    trades_lookup: dict[str, pd.DataFrame] = {'none': empty_trades()}
    session_options: dict[str, list[str]] = {
        'overnight': ['none'],
        'morning': ['none'],
        'afternoon': ['none'],
        'evening': ['none'],
    }
    summary_rows: list[dict[str, object]] = []
    all_dates = sorted({date for grp in groups.values() for date in grp['entry_date'].dropna().astype(str).unique().tolist()})
    split_index = len(all_dates) // 2
    train_dates = set(all_dates[:split_index])
    test_dates = set(all_dates[split_index:])

    for candidate in candidates:
        trades_df = (
            simulate_single(groups, result_lookup, candidate)
            if isinstance(candidate, SingleStrategy)
            else simulate_ladder(groups, result_lookup, candidate)
        )
        metrics = summarize_trades(trades_df, train_dates, test_dates)
        summary_rows.append({
            'strategy': candidate.name,
            'session_key': candidate.session_key,
            'type': 'single' if isinstance(candidate, SingleStrategy) else 'ladder',
            **metrics,
        })
        trades_lookup[candidate.name] = trades_df
        session_options[candidate.session_key].append(candidate.name)
    return trades_lookup, session_options, pd.DataFrame(summary_rows)


def search_portfolios(
    trades_lookup: dict[str, pd.DataFrame],
    session_options: dict[str, list[str]],
    train_dates: set[str],
    test_dates: set[str],
) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for overnight_name in session_options['overnight']:
        for morning_name in session_options['morning']:
            for afternoon_name in session_options['afternoon']:
                for evening_name in session_options['evening']:
                    active = [name for name in [overnight_name, morning_name, afternoon_name, evening_name] if name != 'none']
                    if not active:
                        continue
                    frames = [trades_lookup[name] for name in active]
                    combo = pd.concat(frames, ignore_index=True) if frames else empty_trades()
                    if combo.empty:
                        continue
                    combo = combo.sort_values(['market', 'entry_ts']).drop_duplicates(subset=['market'], keep='first')
                    metrics = summarize_trades(combo, train_dates, test_dates)
                    rows.append({
                        'portfolio': '|'.join([overnight_name, morning_name, afternoon_name, evening_name]),
                        'overnight': overnight_name,
                        'morning': morning_name,
                        'afternoon': afternoon_name,
                        'evening': evening_name,
                        'active_count': len(active),
                        'simple_score': float(metrics['robust']) - (2.5 * len(active)),
                        **metrics,
                    })
    out = pd.DataFrame(rows)
    if out.empty:
        return out
    return out.sort_values(['robust', 'net', 'trades'], ascending=[False, False, False]).reset_index(drop=True)


def portfolio_trades(portfolios_df: pd.DataFrame, trades_lookup: dict[str, pd.DataFrame], portfolio_name: str) -> pd.DataFrame:
    row = portfolios_df.loc[portfolios_df['portfolio'] == portfolio_name]
    if row.empty:
        return empty_trades()
    rec = row.iloc[0]
    active = [str(rec[key]) for key in ('overnight', 'morning', 'afternoon', 'evening') if str(rec[key]) != 'none']
    frames = [trades_lookup[name] for name in active]
    combo = pd.concat(frames, ignore_index=True) if frames else empty_trades()
    if combo.empty:
        return combo
    return combo.sort_values(['market', 'entry_ts']).drop_duplicates(subset=['market'], keep='first').reset_index(drop=True)


def main() -> None:
    parser = argparse.ArgumentParser(description='Search for a robust multi-regime BTC 15m portfolio strategy.')
    parser.add_argument('--dataset', required=True)
    args = parser.parse_args()

    groups, result_lookup, all_dates = load_groups(args.dataset)
    if not groups or not all_dates:
        raise RuntimeError(f'No raw events found for dataset {args.dataset}')
    split_index = len(all_dates) // 2
    train_dates = set(all_dates[:split_index])
    test_dates = set(all_dates[split_index:])

    trades_lookup, session_options, candidate_metrics_df = build_candidate_library(groups, result_lookup)
    portfolio_summary_df = search_portfolios(trades_lookup, session_options, train_dates, test_dates)
    if portfolio_summary_df.empty:
        raise RuntimeError(f'Portfolio search returned no rows for dataset {args.dataset}')

    best_portfolio = portfolio_summary_df.iloc[0]
    core_df = portfolio_summary_df[portfolio_summary_df['active_count'] <= 3].copy()
    best_core_portfolio = core_df.iloc[0] if not core_df.empty else best_portfolio
    benchmark_name = 'overnight_ladder_87_77_67|none|none|none'
    benchmark_row = portfolio_summary_df.loc[portfolio_summary_df['portfolio'] == benchmark_name]
    benchmark_portfolio = benchmark_row.iloc[0] if not benchmark_row.empty else None

    best_trades_df = portfolio_trades(portfolio_summary_df, trades_lookup, str(best_portfolio['portfolio']))
    best_core_trades_df = portfolio_trades(portfolio_summary_df, trades_lookup, str(best_core_portfolio['portfolio']))
    benchmark_trades_df = (
        portfolio_trades(portfolio_summary_df, trades_lookup, benchmark_name)
        if benchmark_portfolio is not None
        else empty_trades()
    )

    run_id = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    paths = rr.dataset_paths(args.dataset)
    run_dir = paths['replay_root'] / f'run_id={run_id}'
    run_dir.mkdir(parents=True, exist_ok=True)
    candidate_metrics_df.to_parquet(run_dir / 'regime_portfolio_candidate_summary.parquet', index=False)
    portfolio_summary_df.to_parquet(run_dir / 'regime_portfolio_summary.parquet', index=False)
    best_trades_df.to_parquet(run_dir / 'regime_portfolio_best_trades.parquet', index=False)
    best_core_trades_df.to_parquet(run_dir / 'regime_portfolio_core_trades.parquet', index=False)
    if not benchmark_trades_df.empty:
        benchmark_trades_df.to_parquet(run_dir / 'regime_portfolio_benchmark_trades.parquet', index=False)

    payload = {
        'dataset_tag': args.dataset,
        'run_id': run_id,
        'built_at': datetime.now(timezone.utc).isoformat(),
        'candidate_rows': int(len(candidate_metrics_df)),
        'portfolio_rows': int(len(portfolio_summary_df)),
        'best_portfolio': {
            'name': str(best_portfolio['portfolio']),
            'trades': int(best_portfolio['trades']),
            'gross': float(best_portfolio['gross']),
            'net': float(best_portfolio['net']),
            'win_rate': float(best_portfolio['win_rate']),
            'train_net': float(best_portfolio['train_net']),
            'test_net': float(best_portfolio['test_net']),
            'robust': float(best_portfolio['robust']),
            'worst_trade': float(best_portfolio['worst_trade']),
        },
        'best_core_portfolio': {
            'name': str(best_core_portfolio['portfolio']),
            'trades': int(best_core_portfolio['trades']),
            'gross': float(best_core_portfolio['gross']),
            'net': float(best_core_portfolio['net']),
            'win_rate': float(best_core_portfolio['win_rate']),
            'train_net': float(best_core_portfolio['train_net']),
            'test_net': float(best_core_portfolio['test_net']),
            'robust': float(best_core_portfolio['robust']),
            'worst_trade': float(best_core_portfolio['worst_trade']),
        },
        'benchmark_portfolio': (
            {
                'name': str(benchmark_portfolio['portfolio']),
                'net': float(benchmark_portfolio['net']),
                'robust': float(benchmark_portfolio['robust']),
            }
            if benchmark_portfolio is not None
            else None
        ),
    }
    (paths['metadata_root'] / 'regime_portfolio_status.json').write_text(json.dumps(payload, indent=2), encoding='utf-8')
    print(json.dumps(payload, indent=2))


if __name__ == '__main__':
    main()
