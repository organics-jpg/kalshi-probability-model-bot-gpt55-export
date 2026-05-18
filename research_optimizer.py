from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone

import research_replay as rr


def main() -> None:
    parser = argparse.ArgumentParser(description='Build raw-recorder optimizer artifacts for a research dataset.')
    parser.add_argument('--dataset', required=True)
    args = parser.parse_args()

    paths = rr.dataset_paths(args.dataset)
    market_results_df = rr.load_market_results(paths['market_results_path'])
    raw_ticker_df = rr.attach_market_close_times(rr.load_raw_ticker_events(paths['raw_root']), market_results_df)
    summary_df, trades_df = rr.build_optimizer_grid(raw_ticker_df, market_results_df)
    if summary_df.empty:
        raise RuntimeError(f'Optimizer grid returned no rows for dataset {args.dataset}')

    run_id = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    run_dir = paths['replay_root'] / f'run_id={run_id}'
    run_dir.mkdir(parents=True, exist_ok=True)
    summary_df.to_parquet(run_dir / 'optimizer_summary.parquet', index=False)
    trades_df.to_parquet(run_dir / 'optimizer_trades.parquet', index=False)

    payload = {
        'dataset_tag': args.dataset,
        'run_id': run_id,
        'built_at': datetime.now(timezone.utc).isoformat(),
        'optimizer_scenario_rows': int(len(summary_df)),
        'optimizer_trade_rows': int(len(trades_df)),
        'best_optimizer_scenario': str(summary_df.iloc[0]['scenario']),
        'best_optimizer_net_pnl_dollars': float(summary_df.iloc[0]['net_pnl_dollars']),
    }
    (paths['metadata_root'] / 'optimizer_status.json').write_text(json.dumps(payload, indent=2), encoding='utf-8')
    print(json.dumps(payload, indent=2))


if __name__ == '__main__':
    main()
