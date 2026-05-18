from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone

import pandas as pd

import research_replay as rr


def build_scenarios() -> list[dict[str, float | int | str | bool]]:
    scenarios: list[dict[str, float | int | str | bool]] = []
    for reclaim_buffer in (0, 2):
        first_reclaim = 80 + reclaim_buffer
        second_reclaim = 70 + reclaim_buffer
        scenarios.append({
            'name': f'fork90_r{int(first_reclaim)}_{int(second_reclaim)}_hold',
            'arm_cents': 90,
            'arm_window_seconds': 120,
            'min_seconds_to_close': 60,
            'max_seconds_to_close': 900,
            'first_touch_cents': 80,
            'first_reclaim_cents': first_reclaim,
            'second_touch_cents': 70,
            'second_reclaim_cents': second_reclaim,
            'flip_enabled': False,
        })
        for fail_exit_cents in (40, 35):
            for flip_size_ratio in (1.75, 2.0):
                scenarios.append({
                    'name': f'fork90_r{int(first_reclaim)}_{int(second_reclaim)}_flip{int(fail_exit_cents)}_x{str(flip_size_ratio).replace(".", "p")}_t20_h120',
                    'arm_cents': 90,
                    'arm_window_seconds': 120,
                    'min_seconds_to_close': 60,
                    'max_seconds_to_close': 900,
                    'first_touch_cents': 80,
                    'first_reclaim_cents': first_reclaim,
                    'second_touch_cents': 70,
                    'second_reclaim_cents': second_reclaim,
                    'fail_exit_cents': fail_exit_cents,
                    'flip_enabled': True,
                    'flip_size_ratio': flip_size_ratio,
                    'flip_target_cents': 20,
                    'flip_max_hold_seconds': 120,
                })
    return scenarios


def main() -> None:
    parser = argparse.ArgumentParser(description='Backtest the failed-certainty 90/80/70 flip strategy against a research dataset.')
    parser.add_argument('--dataset', required=True)
    parser.add_argument('--tranche-size', type=int, default=10)
    args = parser.parse_args()

    paths = rr.dataset_paths(args.dataset)
    market_results_df = rr.load_market_results(paths['market_results_path'])
    raw_ticker_df = rr.attach_market_close_times(rr.load_raw_ticker_events(paths['raw_root']), market_results_df)
    scenarios = build_scenarios()
    trade_frames = [
        rr.simulate_failed_certainty_replay(raw_ticker_df, market_results_df, scenario, tranche_size=args.tranche_size)
        for scenario in scenarios
    ]
    non_empty_frames = [df for df in trade_frames if not df.empty]
    trades_df = pd.concat(non_empty_frames, ignore_index=True) if non_empty_frames else pd.DataFrame()
    summary_df = rr.summarize_failed_certainty_replay(trades_df)
    if summary_df.empty:
        raise RuntimeError(f'Failed-certainty replay returned no rows for dataset {args.dataset}')

    run_id = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    run_dir = paths['replay_root'] / f'run_id={run_id}'
    run_dir.mkdir(parents=True, exist_ok=True)
    summary_df.to_parquet(run_dir / 'failed_certainty_summary.parquet', index=False)
    trades_df.to_parquet(run_dir / 'failed_certainty_trades.parquet', index=False)

    payload = {
        'dataset_tag': args.dataset,
        'run_id': run_id,
        'built_at': datetime.now(timezone.utc).isoformat(),
        'scenario_rows': int(len(summary_df)),
        'trade_rows': int(len(trades_df)),
        'best_scenario': str(summary_df.iloc[0]['scenario']),
        'best_net_pnl_dollars': float(summary_df.iloc[0]['net_pnl_dollars']),
        'best_win_rate': float(summary_df.iloc[0]['win_rate']),
        'tranche_size': int(args.tranche_size),
        'assumptions': {
            'arm_cents': 90,
            'entry_ladders': ['80 touch then reclaim', '70 touch then reclaim'],
            'arm_window_seconds': 120,
            'flip_target_cents': 20,
            'flip_max_hold_seconds': 120,
            'grid': {
                'reclaim_buffers': [0, 2],
                'fail_exit_cents': [40, 35],
                'flip_size_ratios': [1.75, 2.0],
            },
        },
    }
    (paths['metadata_root'] / 'failed_certainty_status.json').write_text(json.dumps(payload, indent=2), encoding='utf-8')
    print(json.dumps(payload, indent=2))


if __name__ == '__main__':
    main()
