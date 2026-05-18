from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

try:
    import duckdb
except Exception:  # pragma: no cover - optional dependency for parquet recovery
    duckdb = None

ROOT = Path(__file__).resolve().parent
_DUCKDB_CONN = duckdb.connect(database=":memory:") if duckdb is not None else None


def dataset_paths(dataset_tag: str) -> dict[str, Path]:
    base = ROOT / 'research_data' / dataset_tag
    return {
        'root': base,
        'raw_root': base / 'raw_events',
        'features_root': base / 'features',
        'trade_labels_root': base / 'trade_labels',
        'replay_root': base / 'replay_runs',
        'metadata_root': base / 'metadata',
        'market_results_path': ROOT / 'stats' / dataset_tag / 'market_results.csv',
    }


def add_partition_columns(df: pd.DataFrame, root: Path, file_path: Path) -> pd.DataFrame:
    if df.empty:
        return df
    out = df.copy()
    try:
        relative_parts = file_path.relative_to(root).parts[:-1]
    except Exception:
        relative_parts = file_path.parts[:-1]
    for part in relative_parts:
        if '=' not in part:
            continue
        key, value = part.split('=', 1)
        if key and key not in out.columns:
            out[key] = value
    return out


def load_parquet_tree(root: Path) -> pd.DataFrame:
    if not root.exists():
        return pd.DataFrame()
    files = sorted(root.rglob('*.parquet'))
    if not files:
        return pd.DataFrame()
    frames: list[pd.DataFrame] = []
    for fp in files:
        try:
            frame = pd.read_parquet(fp)
        except Exception:
            if _DUCKDB_CONN is None:
                continue
            try:
                frame = _DUCKDB_CONN.execute(
                    "SELECT * FROM read_parquet(?)",
                    [str(fp.resolve())],
                ).df()
            except Exception:
                continue
        frames.append(add_partition_columns(frame, root, fp))
    return pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()


def load_market_results(path: Path) -> pd.DataFrame:
    if not path.exists():
        return pd.DataFrame()
    try:
        df = pd.read_csv(path)
    except Exception:
        return pd.DataFrame()
    for col in ('market', 'market_ticker', 'result', 'market_result'):
        if col in df.columns:
            df[col] = df[col].fillna('').astype(str)
    return df


def load_raw_ticker_events(raw_root: Path) -> pd.DataFrame:
    ticker_root = raw_root / 'type=ticker'
    if not ticker_root.exists():
        return pd.DataFrame()
    rows: list[dict[str, Any]] = []
    for fp in sorted(ticker_root.rglob('*.ndjson')):
        try:
            with fp.open('r', encoding='utf-8') as fh:
                for line in fh:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        rec = json.loads(line)
                    except Exception:
                        continue
                    payload = rec.get('payload_json') or {}
                    market = str(rec.get('market_ticker') or payload.get('market_ticker') or '').strip()
                    if not market:
                        continue
                    try:
                        local_ts = pd.Timestamp(rec.get('local_recv_ts'))
                    except Exception:
                        continue
                    yes_bid_dollars = pd.to_numeric(payload.get('yes_bid_dollars'), errors='coerce')
                    yes_ask_dollars = pd.to_numeric(payload.get('yes_ask_dollars'), errors='coerce')
                    rows.append({
                        'market_ticker': market,
                        'ts': local_ts,
                        'yes_bid_cents': float(yes_bid_dollars * 100.0) if pd.notna(yes_bid_dollars) else np.nan,
                        'yes_ask_cents': float(yes_ask_dollars * 100.0) if pd.notna(yes_ask_dollars) else np.nan,
                    })
        except Exception:
            continue
    if not rows:
        return pd.DataFrame()
    out = pd.DataFrame(rows)
    out['no_bid_cents'] = 100.0 - out['yes_ask_cents']
    out['no_ask_cents'] = 100.0 - out['yes_bid_cents']
    out = out.sort_values(['market_ticker', 'ts']).drop_duplicates(
        subset=['market_ticker', 'ts', 'yes_bid_cents', 'yes_ask_cents', 'no_bid_cents', 'no_ask_cents'],
        keep='last',
    )
    return out.reset_index(drop=True)


def attach_market_close_times(events_df: pd.DataFrame, market_results_df: pd.DataFrame) -> pd.DataFrame:
    if events_df.empty:
        return events_df
    out = events_df.copy()
    if market_results_df.empty or 'market' not in market_results_df.columns:
        out['close_dt'] = pd.NaT
        out['seconds_to_close'] = np.nan
        return out
    results = market_results_df.copy()
    results['market'] = results['market'].fillna('').astype(str)
    if 'close_time' in results.columns:
        results['close_dt'] = pd.to_datetime(results['close_time'], utc=True, errors='coerce')
    else:
        results['close_dt'] = pd.NaT
    close_map = dict(zip(results['market'], results['close_dt']))
    out['close_dt'] = out['market_ticker'].map(close_map)
    out['seconds_to_close'] = (out['close_dt'] - out['ts']).dt.total_seconds()
    return out


def enrich_trade_labels(labels_df: pd.DataFrame, features_df: pd.DataFrame) -> pd.DataFrame:
    if labels_df.empty:
        return labels_df
    out = labels_df.copy()
    out['entry_dt'] = pd.to_datetime(out.get('entry_dt'), utc=True, errors='coerce').astype('datetime64[ns, UTC]')
    out['net_pnl_dollars'] = pd.to_numeric(out.get('net_pnl_dollars'), errors='coerce')
    out['hold_duration_s'] = pd.to_numeric(out.get('hold_duration_s'), errors='coerce')
    out['feed_age_ms_at_entry'] = pd.to_numeric(out.get('feed_age_ms_at_entry'), errors='coerce')
    out['submit_latency_ms'] = pd.to_numeric(out.get('submit_latency_ms'), errors='coerce')
    out['book_age_ms_at_entry'] = pd.to_numeric(out.get('book_age_ms_at_entry'), errors='coerce')

    if features_df.empty or 'market_ticker' not in features_df.columns:
        return out

    feat = features_df.copy()
    feat['ts'] = pd.to_datetime(feat.get('ts'), utc=True, errors='coerce').astype('datetime64[ns, UTC]')
    feat = feat[feat['ts'].notna()].copy()
    feat['market_ticker'] = feat['market_ticker'].fillna('').astype(str)
    out['market'] = out.get('market', '').fillna('').astype(str)

    selected_cols = [
        'market_ticker', 'ts', 'yes_range_30s', 'yes_range_60s', 'no_range_30s', 'no_range_60s',
        'yes_move_30s', 'yes_move_60s', 'no_move_30s', 'no_move_60s', 'spread_yes', 'spread_no', 'depth_imbalance'
    ]
    feat = feat[[c for c in selected_cols if c in feat.columns]].sort_values(['market_ticker', 'ts'])
    merged_frames: list[pd.DataFrame] = []
    for market, grp in out.groupby('market', dropna=False):
        chunk = grp.sort_values('entry_dt').copy()
        market_feat = feat[feat['market_ticker'] == str(market)].sort_values('ts').copy()
        if market_feat.empty:
            merged_frames.append(chunk)
            continue
        merged = pd.merge_asof(
            chunk,
            market_feat,
            left_on='entry_dt',
            right_on='ts',
            direction='backward',
            tolerance=pd.Timedelta(seconds=120),
        )
        merged_frames.append(merged)
    return pd.concat(merged_frames, ignore_index=True) if merged_frames else out


def add_same_side_features(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return df
    out = df.copy()
    same_side_range_30s = []
    same_side_range_60s = []
    same_side_move_30s = []
    same_side_move_60s = []
    for rec in out.to_dict('records'):
        side = str(rec.get('side') or '').lower()
        prefix = 'yes' if side == 'yes' else 'no'
        same_side_range_30s.append(pd.to_numeric(pd.Series([rec.get(f'{prefix}_range_30s')]), errors='coerce').iloc[0])
        same_side_range_60s.append(pd.to_numeric(pd.Series([rec.get(f'{prefix}_range_60s')]), errors='coerce').iloc[0])
        same_side_move_30s.append(pd.to_numeric(pd.Series([rec.get(f'{prefix}_move_30s')]), errors='coerce').iloc[0])
        same_side_move_60s.append(pd.to_numeric(pd.Series([rec.get(f'{prefix}_move_60s')]), errors='coerce').iloc[0])
    out['same_side_range_30s'] = same_side_range_30s
    out['same_side_range_60s'] = same_side_range_60s
    out['same_side_move_30s'] = same_side_move_30s
    out['same_side_move_60s'] = same_side_move_60s
    return out


def scenario_mask(df: pd.DataFrame, scenario: dict[str, Any]) -> pd.Series:
    mask = pd.Series(True, index=df.index)
    if scenario.get('max_feed_age_ms') is not None and 'feed_age_ms_at_entry' in df.columns:
        series = pd.to_numeric(df['feed_age_ms_at_entry'], errors='coerce')
        mask &= series.isna() | (series <= float(scenario['max_feed_age_ms']))
    if scenario.get('max_submit_latency_ms') is not None and 'submit_latency_ms' in df.columns:
        series = pd.to_numeric(df['submit_latency_ms'], errors='coerce')
        mask &= series.isna() | (series <= float(scenario['max_submit_latency_ms']))
    if scenario.get('max_same_side_range_30s') is not None and 'same_side_range_30s' in df.columns:
        series = pd.to_numeric(df['same_side_range_30s'], errors='coerce')
        mask &= series.isna() | (series <= float(scenario['max_same_side_range_30s']))
    if scenario.get('max_same_side_range_60s') is not None and 'same_side_range_60s' in df.columns:
        series = pd.to_numeric(df['same_side_range_60s'], errors='coerce')
        mask &= series.isna() | (series <= float(scenario['max_same_side_range_60s']))
    if scenario.get('min_depth_imbalance') is not None and 'depth_imbalance' in df.columns:
        threshold = float(scenario['min_depth_imbalance'])
        series = pd.to_numeric(df['depth_imbalance'], errors='coerce').abs()
        mask &= series.isna() | (series >= threshold)
    return mask


def summarize_scenario(df: pd.DataFrame, name: str, mask: pd.Series) -> dict[str, Any]:
    kept = df[mask].copy()
    blocked = df[~mask].copy()
    kept_net = float(kept['net_pnl_dollars'].fillna(0.0).sum()) if 'net_pnl_dollars' in kept.columns else 0.0
    blocked_net = float(blocked['net_pnl_dollars'].fillna(0.0).sum()) if 'net_pnl_dollars' in blocked.columns else 0.0
    kept_win_rate = float((kept['net_pnl_dollars'].fillna(0.0) > 0).mean() * 100.0) if len(kept) else np.nan
    baseline_win_rate = float((df['net_pnl_dollars'].fillna(0.0) > 0).mean() * 100.0) if len(df) else np.nan
    return {
        'scenario': name,
        'trades_kept': int(mask.sum()),
        'trades_blocked': int((~mask).sum()),
        'kept_net_pnl_dollars': kept_net,
        'blocked_net_pnl_dollars': blocked_net,
        'baseline_net_pnl_dollars': float(df['net_pnl_dollars'].fillna(0.0).sum()) if 'net_pnl_dollars' in df.columns else 0.0,
        'kept_win_rate': kept_win_rate,
        'baseline_win_rate': baseline_win_rate,
        'avg_submit_latency_ms': float(kept['submit_latency_ms'].dropna().mean()) if 'submit_latency_ms' in kept.columns and kept['submit_latency_ms'].dropna().size else np.nan,
        'avg_feed_age_ms': float(kept['feed_age_ms_at_entry'].dropna().mean()) if 'feed_age_ms_at_entry' in kept.columns and kept['feed_age_ms_at_entry'].dropna().size else np.nan,
        'avg_same_side_range_30s': float(kept['same_side_range_30s'].dropna().mean()) if 'same_side_range_30s' in kept.columns and kept['same_side_range_30s'].dropna().size else np.nan,
    }


def simulate_quote_replay(features_df: pd.DataFrame, market_results_df: pd.DataFrame, scenario: dict[str, Any], *, position_size: int = 10) -> pd.DataFrame:
    if features_df.empty:
        return pd.DataFrame()
    work = features_df.copy()
    if 'market_ticker' not in work.columns or 'ts' not in work.columns:
        return pd.DataFrame()
    work['ts'] = pd.to_datetime(work['ts'], utc=True, errors='coerce')
    work = work[work['ts'].notna()].copy()
    work['market_ticker'] = work['market_ticker'].fillna('').astype(str)
    work = work.sort_values(['market_ticker', 'ts'])

    result_lookup: dict[str, str] = {}
    if not market_results_df.empty:
        market_col = 'market' if 'market' in market_results_df.columns else 'market_ticker'
        result_col = 'market_result' if 'market_result' in market_results_df.columns else 'result'
        for rec in market_results_df.to_dict('records'):
            market = str(rec.get(market_col) or '')
            result = str(rec.get(result_col) or '').lower()
            if market and result in {'yes', 'no'}:
                result_lookup[market] = result

    replay_rows: list[dict[str, Any]] = []
    for market, grp in work.groupby('market_ticker'):
        grp = grp.sort_values('ts').copy()
        market_result = result_lookup.get(market)
        if market_result not in {'yes', 'no'}:
            continue
        position = None
        for rec in grp.to_dict('records'):
            yes_bid = pd.to_numeric(pd.Series([rec.get('yes_bid_cents')]), errors='coerce').iloc[0]
            yes_ask = pd.to_numeric(pd.Series([rec.get('yes_ask_cents')]), errors='coerce').iloc[0]
            no_bid = pd.to_numeric(pd.Series([rec.get('no_bid_cents')]), errors='coerce').iloc[0]
            no_ask = pd.to_numeric(pd.Series([rec.get('no_ask_cents')]), errors='coerce').iloc[0]
            seconds_to_close = pd.to_numeric(pd.Series([rec.get('seconds_to_close')]), errors='coerce').iloc[0]
            if pd.isna(seconds_to_close) or seconds_to_close <= 15 or seconds_to_close > 900:
                continue
            if position is None:
                candidates = []
                if pd.notna(yes_ask) and float(scenario.get('entry_floor_cents', 88)) <= yes_ask <= float(scenario.get('entry_limit_cents', 90)):
                    yes_range = pd.to_numeric(pd.Series([rec.get('yes_range_30s')]), errors='coerce').iloc[0]
                    if pd.isna(yes_range) or yes_range <= float(scenario.get('max_range_30s', np.inf)):
                        candidates.append(('yes', float(yes_ask), float(yes_bid) if pd.notna(yes_bid) else -np.inf))
                if pd.notna(no_ask) and float(scenario.get('entry_floor_cents', 88)) <= no_ask <= float(scenario.get('entry_limit_cents', 90)):
                    no_range = pd.to_numeric(pd.Series([rec.get('no_range_30s')]), errors='coerce').iloc[0]
                    if pd.isna(no_range) or no_range <= float(scenario.get('max_range_30s', np.inf)):
                        candidates.append(('no', float(no_ask), float(no_bid) if pd.notna(no_bid) else -np.inf))
                if candidates:
                    candidates.sort(key=lambda item: (item[2], -item[1]), reverse=True)
                    side, entry_price, _ = candidates[0]
                    position = {
                        'market': market,
                        'side': side,
                        'entry_ts': rec['ts'],
                        'entry_price_cents': entry_price,
                    }
                continue

            same_bid = yes_bid if position['side'] == 'yes' else no_bid
            if pd.isna(same_bid):
                continue
            panic_cents = float(scenario.get('panic_cents', 68))
            stop_cents = float(scenario.get('stop_cents', 70))
            exit_reason = None
            if same_bid <= panic_cents:
                exit_reason = 'panic_stop'
            elif same_bid <= stop_cents:
                exit_reason = 'soft_stop'
            if exit_reason is None:
                continue
            exit_price = float(same_bid)
            pnl_dollars = round((exit_price - float(position['entry_price_cents'])) * position_size / 100.0, 4)
            replay_rows.append({
                'scenario': scenario['name'],
                'market': market,
                'side': position['side'],
                'entry_ts': position['entry_ts'],
                'exit_ts': rec['ts'],
                'entry_price_cents': position['entry_price_cents'],
                'exit_price_cents': exit_price,
                'qty': position_size,
                'exit_reason': exit_reason,
                'market_result': market_result,
                'net_pnl_dollars': pnl_dollars,
            })
            position = None
            break

        if position is not None:
            settlement_price = 100.0 if market_result == position['side'] else 0.0
            pnl_dollars = round((settlement_price - float(position['entry_price_cents'])) * position_size / 100.0, 4)
            replay_rows.append({
                'scenario': scenario['name'],
                'market': market,
                'side': position['side'],
                'entry_ts': position['entry_ts'],
                'exit_ts': None,
                'entry_price_cents': position['entry_price_cents'],
                'exit_price_cents': settlement_price,
                'qty': position_size,
                'exit_reason': 'settlement',
                'market_result': market_result,
                'net_pnl_dollars': pnl_dollars,
            })
    return pd.DataFrame(replay_rows)


def summarize_direct_replay(trades_df: pd.DataFrame) -> pd.DataFrame:
    if trades_df.empty:
        return pd.DataFrame()
    rows = []
    for scenario, grp in trades_df.groupby('scenario'):
        pnl = pd.to_numeric(grp['net_pnl_dollars'], errors='coerce').fillna(0.0)
        rows.append({
            'scenario': scenario,
            'trades': int(len(grp)),
            'wins': int((pnl > 0).sum()),
            'losses': int((pnl < 0).sum()),
            'stopped_trades': int(grp['exit_reason'].isin(['panic_stop', 'soft_stop']).sum()),
            'settled_trades': int((grp['exit_reason'] == 'settlement').sum()),
            'net_pnl_dollars': float(pnl.sum()),
            'avg_pnl_dollars': float(pnl.mean()) if len(pnl) else np.nan,
            'win_rate': float((pnl > 0).mean() * 100.0) if len(pnl) else np.nan,
        })
    return pd.DataFrame(rows).sort_values('net_pnl_dollars', ascending=False).reset_index(drop=True)


def simulate_failed_certainty_replay(raw_events_df: pd.DataFrame, market_results_df: pd.DataFrame, scenario: dict[str, Any], *, tranche_size: int = 10) -> pd.DataFrame:
    if raw_events_df.empty:
        return pd.DataFrame()
    work = raw_events_df.copy()
    if 'market_ticker' not in work.columns or 'ts' not in work.columns:
        return pd.DataFrame()
    work['ts'] = pd.to_datetime(work['ts'], utc=True, errors='coerce')
    work = work[work['ts'].notna()].copy()
    work['market_ticker'] = work['market_ticker'].fillna('').astype(str)
    for col in ('yes_bid_cents', 'yes_ask_cents', 'no_bid_cents', 'no_ask_cents', 'seconds_to_close'):
        if col in work.columns:
            work[col] = pd.to_numeric(work[col], errors='coerce')
    work = work.sort_values(['market_ticker', 'ts'])

    result_lookup: dict[str, str] = {}
    if not market_results_df.empty:
        market_col = 'market' if 'market' in market_results_df.columns else 'market_ticker'
        result_col = 'market_result' if 'market_result' in market_results_df.columns else 'result'
        for rec in market_results_df.to_dict('records'):
            market = str(rec.get(market_col) or '')
            result = str(rec.get(result_col) or '').lower()
            if market and result in {'yes', 'no'}:
                result_lookup[market] = result

    arm_cents = float(scenario.get('arm_cents', 90))
    arm_window_seconds = float(scenario.get('arm_window_seconds', 120))
    min_seconds_to_close = float(scenario.get('min_seconds_to_close', 60))
    max_seconds_to_close = float(scenario.get('max_seconds_to_close', 900))
    arm_entry_enabled = bool(scenario.get('arm_entry_enabled', False))
    arm_entry_qty = int(scenario.get('arm_entry_qty', tranche_size)) if arm_entry_enabled else 0
    arm_entry_price_override_raw = scenario.get('arm_entry_price_cents')
    arm_entry_price_override = float(arm_entry_price_override_raw) if arm_entry_price_override_raw is not None else None
    first_touch_cents = float(scenario.get('first_touch_cents', 80))
    first_reclaim_cents = float(scenario.get('first_reclaim_cents', first_touch_cents))
    second_touch_cents = float(scenario.get('second_touch_cents', 70))
    second_reclaim_cents = float(scenario.get('second_reclaim_cents', second_touch_cents))
    fail_exit_cents = float(scenario.get('fail_exit_cents', 40))
    flip_enabled = bool(scenario.get('flip_enabled', True))
    flip_size_ratio = float(scenario.get('flip_size_ratio', 1.75))
    flip_target_cents = float(scenario.get('flip_target_cents', 20))
    flip_max_hold_seconds_raw = scenario.get('flip_max_hold_seconds')
    flip_max_hold_seconds = float(flip_max_hold_seconds_raw) if flip_max_hold_seconds_raw is not None else None

    replay_rows: list[dict[str, Any]] = []
    for market, grp in work.groupby('market_ticker'):
        grp = grp.sort_values('ts').copy()
        market_result = result_lookup.get(market)
        if market_result not in {'yes', 'no'}:
            continue

        armed_side: str | None = None
        armed_ts = None
        arm_deadline = None
        first_touch_ts = None
        second_touch_ts = None
        original_entries: list[dict[str, Any]] = []
        original_exit: dict[str, Any] | None = None
        flip_entry: dict[str, Any] | None = None
        flip_exit: dict[str, Any] | None = None

        for rec in grp.itertuples(index=False):
            ts = rec.ts
            seconds_to_close = rec.seconds_to_close
            yes_bid = rec.yes_bid_cents
            yes_ask = rec.yes_ask_cents
            no_bid = rec.no_bid_cents
            no_ask = rec.no_ask_cents
            valid_entry_window = pd.notna(seconds_to_close) and min_seconds_to_close < float(seconds_to_close) <= max_seconds_to_close

            if armed_side is None:
                if not valid_entry_window:
                    continue
                candidates = []
                if pd.notna(yes_ask) and float(yes_ask) >= arm_cents:
                    candidates.append(('yes', float(yes_ask)))
                if pd.notna(no_ask) and float(no_ask) >= arm_cents:
                    candidates.append(('no', float(no_ask)))
                if not candidates:
                    continue
                candidates.sort(key=lambda item: item[1], reverse=True)
                armed_side = candidates[0][0]
                armed_ts = ts
                arm_deadline = ts + pd.Timedelta(seconds=arm_window_seconds)
                if arm_entry_enabled and arm_entry_qty > 0:
                    arm_entry_price = arm_entry_price_override if arm_entry_price_override is not None else candidates[0][1]
                    original_entries.append({
                        'level': 'arm',
                        'entry_ts': ts,
                        'entry_price_cents': float(arm_entry_price),
                        'qty': int(arm_entry_qty),
                    })
                continue

            same_bid = yes_bid if armed_side == 'yes' else no_bid
            same_ask = yes_ask if armed_side == 'yes' else no_ask
            flip_side = 'no' if armed_side == 'yes' else 'yes'
            opp_bid = no_bid if armed_side == 'yes' else yes_bid
            opp_ask = no_ask if armed_side == 'yes' else yes_ask

            if flip_entry is not None:
                flip_hold_seconds = (ts - flip_entry['entry_ts']).total_seconds()
                target_cents = float(flip_entry['entry_price_cents']) + flip_target_cents
                if pd.notna(opp_bid) and float(opp_bid) >= target_cents:
                    flip_exit = {
                        'exit_ts': ts,
                        'exit_price_cents': float(opp_bid),
                        'exit_reason': 'flip_target',
                        'target_hit': True,
                    }
                    break
                if flip_max_hold_seconds is not None and flip_hold_seconds >= flip_max_hold_seconds and pd.notna(opp_bid):
                    flip_exit = {
                        'exit_ts': ts,
                        'exit_price_cents': float(opp_bid),
                        'exit_reason': 'flip_time_stop',
                        'target_hit': False,
                    }
                    break
                if pd.notna(seconds_to_close) and float(seconds_to_close) <= 5 and pd.notna(opp_bid):
                    flip_exit = {
                        'exit_ts': ts,
                        'exit_price_cents': float(opp_bid),
                        'exit_reason': 'flip_close_out',
                        'target_hit': False,
                    }
                    break
                continue

            within_arm_window = arm_deadline is not None and ts <= arm_deadline
            first_entry_taken = any(entry['level'] == 'first' for entry in original_entries)
            second_entry_taken = any(entry['level'] == 'second' for entry in original_entries)
            if within_arm_window and valid_entry_window and pd.notna(same_ask):
                same_ask_float = float(same_ask)
                if first_touch_ts is None and same_ask_float <= first_touch_cents:
                    first_touch_ts = ts
                if second_touch_ts is None and same_ask_float <= second_touch_cents:
                    second_touch_ts = ts

                # If the market flushes to the deeper ladder first, only the deeper reclaim remains valid.
                if first_touch_ts is not None and second_touch_ts is None and not first_entry_taken and ts > first_touch_ts and same_ask_float >= first_reclaim_cents:
                    original_entries.append({
                        'level': 'first',
                        'entry_ts': ts,
                        'entry_price_cents': same_ask_float,
                        'qty': int(tranche_size),
                    })
                if second_touch_ts is not None and not second_entry_taken and ts > second_touch_ts and same_ask_float >= second_reclaim_cents:
                    original_entries.append({
                        'level': 'second',
                        'entry_ts': ts,
                        'entry_price_cents': same_ask_float,
                        'qty': int(tranche_size),
                    })

            if original_entries and valid_entry_window and pd.notna(same_bid) and float(same_bid) <= fail_exit_cents:
                original_exit = {
                    'exit_ts': ts,
                    'exit_price_cents': float(same_bid),
                    'exit_reason': 'fail_exit',
                }
                if flip_enabled and pd.notna(opp_ask):
                    original_qty = sum(int(entry['qty']) for entry in original_entries)
                    flip_qty = int(round(original_qty * flip_size_ratio))
                    if flip_qty > 0:
                        flip_entry = {
                            'side': flip_side,
                            'entry_ts': ts,
                            'entry_price_cents': float(opp_ask),
                            'qty': flip_qty,
                        }
                        continue
                break

        if not original_entries:
            continue

        original_exit_price_cents = float(original_exit['exit_price_cents']) if original_exit is not None else (100.0 if market_result == armed_side else 0.0)
        original_exit_reason = str(original_exit['exit_reason']) if original_exit is not None else 'original_settlement'
        original_exit_ts = original_exit['exit_ts'] if original_exit is not None else None
        original_pnl_dollars = round(sum(
            (original_exit_price_cents - float(entry['entry_price_cents'])) * int(entry['qty']) / 100.0
            for entry in original_entries
        ), 4)

        flip_taken = flip_entry is not None
        flip_entry_price_cents = np.nan
        flip_exit_price_cents = np.nan
        flip_exit_reason = None
        flip_exit_ts = None
        flip_target_hit = False
        flip_pnl_dollars = 0.0
        flip_qty = 0
        flip_side_out = None
        if flip_entry is not None:
            flip_side_out = str(flip_entry['side'])
            flip_qty = int(flip_entry['qty'])
            flip_entry_price_cents = float(flip_entry['entry_price_cents'])
            if flip_exit is None:
                flip_exit_price_cents = 100.0 if market_result == flip_side_out else 0.0
                flip_exit_reason = 'flip_settlement'
            else:
                flip_exit_price_cents = float(flip_exit['exit_price_cents'])
                flip_exit_reason = str(flip_exit['exit_reason'])
                flip_exit_ts = flip_exit['exit_ts']
                flip_target_hit = bool(flip_exit['target_hit'])
            flip_pnl_dollars = round((flip_exit_price_cents - flip_entry_price_cents) * flip_qty / 100.0, 4)

        original_qty = int(sum(int(entry['qty']) for entry in original_entries))
        original_avg_entry_cents = float(np.average(
            [float(entry['entry_price_cents']) for entry in original_entries],
            weights=[int(entry['qty']) for entry in original_entries],
        ))
        net_pnl_dollars = round(original_pnl_dollars + flip_pnl_dollars, 4)
        replay_rows.append({
            'scenario': scenario['name'],
            'market': market,
            'armed_side': armed_side,
            'armed_ts': armed_ts,
            'market_result': market_result,
            'original_entry_count': int(len(original_entries)),
            'original_qty': original_qty,
            'original_avg_entry_cents': original_avg_entry_cents,
            'first_entry_price_cents': float(original_entries[0]['entry_price_cents']) if original_entries else np.nan,
            'second_entry_price_cents': float(original_entries[1]['entry_price_cents']) if len(original_entries) > 1 else np.nan,
            'original_exit_ts': original_exit_ts,
            'original_exit_price_cents': original_exit_price_cents,
            'original_exit_reason': original_exit_reason,
            'original_pnl_dollars': original_pnl_dollars,
            'flip_taken': flip_taken,
            'flip_side': flip_side_out,
            'flip_qty': flip_qty,
            'flip_entry_ts': flip_entry['entry_ts'] if flip_entry is not None else None,
            'flip_entry_price_cents': flip_entry_price_cents,
            'flip_exit_ts': flip_exit_ts,
            'flip_exit_price_cents': flip_exit_price_cents,
            'flip_exit_reason': flip_exit_reason,
            'flip_target_hit': flip_target_hit,
            'flip_pnl_dollars': flip_pnl_dollars,
            'net_pnl_dollars': net_pnl_dollars,
        })
    return pd.DataFrame(replay_rows)


def summarize_failed_certainty_replay(trades_df: pd.DataFrame) -> pd.DataFrame:
    if trades_df.empty:
        return pd.DataFrame()
    rows = []
    for scenario, grp in trades_df.groupby('scenario'):
        pnl = pd.to_numeric(grp['net_pnl_dollars'], errors='coerce').fillna(0.0)
        wins = pnl[pnl > 0]
        losses = pnl[pnl < 0]
        flipped_mask = grp['flip_taken'].fillna(False).astype(bool)
        flip_hits = grp.loc[flipped_mask, 'flip_target_hit'].fillna(False).astype(bool)
        rows.append({
            'scenario': scenario,
            'trades': int(len(grp)),
            'wins': int((pnl > 0).sum()),
            'losses': int((pnl < 0).sum()),
            'win_rate': float((pnl > 0).mean() * 100.0) if len(pnl) else np.nan,
            'net_pnl_dollars': float(pnl.sum()),
            'avg_pnl_dollars': float(pnl.mean()) if len(pnl) else np.nan,
            'avg_win_dollars': float(wins.mean()) if len(wins) else np.nan,
            'avg_loss_dollars': float(losses.mean()) if len(losses) else np.nan,
            'worst_trade_dollars': float(pnl.min()) if len(pnl) else np.nan,
            'avg_original_entry_count': float(pd.to_numeric(grp['original_entry_count'], errors='coerce').dropna().mean()) if 'original_entry_count' in grp.columns else np.nan,
            'avg_original_entry_cents': float(pd.to_numeric(grp['original_avg_entry_cents'], errors='coerce').dropna().mean()) if 'original_avg_entry_cents' in grp.columns else np.nan,
            'flip_count': int(flipped_mask.sum()),
            'flip_rate': float(flipped_mask.mean() * 100.0) if len(grp) else np.nan,
            'flip_target_hits': int(flip_hits.sum()),
            'flip_target_hit_rate': float(flip_hits.mean() * 100.0) if flip_hits.size else np.nan,
        })
    out = pd.DataFrame(rows)
    if out.empty:
        return out
    return out.sort_values(['net_pnl_dollars', 'win_rate', 'trades'], ascending=[False, False, False]).reset_index(drop=True)


def simulate_quote_replay_with_hold(features_df: pd.DataFrame, market_results_df: pd.DataFrame, scenario: dict[str, Any], *, position_size: int = 10) -> pd.DataFrame:
    if features_df.empty:
        return pd.DataFrame()
    work = features_df.copy()
    if 'market_ticker' not in work.columns or 'ts' not in work.columns:
        return pd.DataFrame()
    work['ts'] = pd.to_datetime(work['ts'], utc=True, errors='coerce')
    work = work[work['ts'].notna()].copy()
    work['market_ticker'] = work['market_ticker'].fillna('').astype(str)
    work = work.sort_values(['market_ticker', 'ts'])

    result_lookup: dict[str, str] = {}
    if not market_results_df.empty:
        market_col = 'market' if 'market' in market_results_df.columns else 'market_ticker'
        result_col = 'market_result' if 'market_result' in market_results_df.columns else 'result'
        for rec in market_results_df.to_dict('records'):
            market = str(rec.get(market_col) or '')
            result = str(rec.get(result_col) or '').lower()
            if market and result in {'yes', 'no'}:
                result_lookup[market] = result

    replay_rows: list[dict[str, Any]] = []
    entry_floor_override = scenario.get('entry_floor_cents')
    entry_limit = float(scenario.get('entry_limit_cents', 90))
    entry_band_cents = float(scenario.get('entry_band_cents', 2))
    entry_floor = float(entry_floor_override) if entry_floor_override is not None else max(0.0, entry_limit - entry_band_cents)
    stop_cents = scenario.get('stop_cents')
    panic_cents = scenario.get('panic_cents')
    min_seconds_to_close = float(scenario.get('min_seconds_to_close', 15))
    max_seconds_to_close = float(scenario.get('max_seconds_to_close', 900))
    max_range_30s = scenario.get('max_range_30s')

    for market, grp in work.groupby('market_ticker'):
        grp = grp.sort_values('ts').copy()
        market_result = result_lookup.get(market)
        if market_result not in {'yes', 'no'}:
            continue
        position = None
        for rec in grp.to_dict('records'):
            seconds_to_close = pd.to_numeric(pd.Series([rec.get('seconds_to_close')]), errors='coerce').iloc[0]
            if pd.isna(seconds_to_close) or seconds_to_close <= min_seconds_to_close or seconds_to_close > max_seconds_to_close:
                continue
            yes_bid = pd.to_numeric(pd.Series([rec.get('yes_bid_cents')]), errors='coerce').iloc[0]
            yes_ask = pd.to_numeric(pd.Series([rec.get('yes_ask_cents')]), errors='coerce').iloc[0]
            no_bid = pd.to_numeric(pd.Series([rec.get('no_bid_cents')]), errors='coerce').iloc[0]
            no_ask = pd.to_numeric(pd.Series([rec.get('no_ask_cents')]), errors='coerce').iloc[0]
            if position is None:
                candidates = []
                if pd.notna(yes_ask) and entry_floor <= yes_ask <= entry_limit:
                    yes_range = pd.to_numeric(pd.Series([rec.get('yes_range_30s')]), errors='coerce').iloc[0]
                    if max_range_30s is None or pd.isna(yes_range) or yes_range <= float(max_range_30s):
                        candidates.append(('yes', float(yes_ask), float(yes_bid) if pd.notna(yes_bid) else -np.inf))
                if pd.notna(no_ask) and entry_floor <= no_ask <= entry_limit:
                    no_range = pd.to_numeric(pd.Series([rec.get('no_range_30s')]), errors='coerce').iloc[0]
                    if max_range_30s is None or pd.isna(no_range) or no_range <= float(max_range_30s):
                        candidates.append(('no', float(no_ask), float(no_bid) if pd.notna(no_bid) else -np.inf))
                if candidates:
                    candidates.sort(key=lambda item: (item[2], -item[1]), reverse=True)
                    side, entry_price, _ = candidates[0]
                    position = {
                        'market': market,
                        'side': side,
                        'entry_ts': rec['ts'],
                        'entry_price_cents': entry_price,
                    }
                continue

            same_bid = yes_bid if position['side'] == 'yes' else no_bid
            if pd.isna(same_bid):
                continue
            exit_reason = None
            if panic_cents is not None and same_bid <= float(panic_cents):
                exit_reason = 'panic_stop'
            elif stop_cents is not None and same_bid <= float(stop_cents):
                exit_reason = 'soft_stop'
            if exit_reason is None:
                continue
            exit_price = float(same_bid)
            pnl_dollars = round((exit_price - float(position['entry_price_cents'])) * position_size / 100.0, 4)
            replay_rows.append({
                'scenario': scenario['name'],
                'market': market,
                'side': position['side'],
                'entry_ts': position['entry_ts'],
                'exit_ts': rec['ts'],
                'entry_price_cents': position['entry_price_cents'],
                'exit_price_cents': exit_price,
                'qty': position_size,
                'exit_reason': exit_reason,
                'market_result': market_result,
                'net_pnl_dollars': pnl_dollars,
                'stopped_but_resolved_entry_side': bool(market_result == position['side']),
            })
            position = None
            break

        if position is not None:
            settlement_price = 100.0 if market_result == position['side'] else 0.0
            pnl_dollars = round((settlement_price - float(position['entry_price_cents'])) * position_size / 100.0, 4)
            replay_rows.append({
                'scenario': scenario['name'],
                'market': market,
                'side': position['side'],
                'entry_ts': position['entry_ts'],
                'exit_ts': None,
                'entry_price_cents': position['entry_price_cents'],
                'exit_price_cents': settlement_price,
                'qty': position_size,
                'exit_reason': 'settlement',
                'market_result': market_result,
                'net_pnl_dollars': pnl_dollars,
                'stopped_but_resolved_entry_side': False,
            })
    return pd.DataFrame(replay_rows)


def summarize_optimizer_replay(trades_df: pd.DataFrame) -> pd.DataFrame:
    if trades_df.empty:
        return pd.DataFrame()
    rows = []
    for scenario, grp in trades_df.groupby('scenario'):
        pnl = pd.to_numeric(grp['net_pnl_dollars'], errors='coerce').fillna(0.0)
        stopped_mask = grp['exit_reason'].isin(['panic_stop', 'soft_stop'])
        false_stops = pd.to_numeric(grp.loc[stopped_mask, 'stopped_but_resolved_entry_side'], errors='coerce').fillna(0).sum()
        losses = pnl[pnl < 0]
        wins = pnl[pnl > 0]
        entry_limit_series = pd.to_numeric(grp.get('entry_limit_cents'), errors='coerce') if 'entry_limit_cents' in grp.columns else pd.Series(dtype=float)
        entry_floor_series = pd.to_numeric(grp.get('entry_floor_cents'), errors='coerce') if 'entry_floor_cents' in grp.columns else pd.Series(dtype=float)
        stop_series = pd.to_numeric(grp.get('stop_cents'), errors='coerce') if 'stop_cents' in grp.columns else pd.Series(dtype=float)
        panic_series = pd.to_numeric(grp.get('panic_cents'), errors='coerce') if 'panic_cents' in grp.columns else pd.Series(dtype=float)
        rows.append({
            'scenario': scenario,
            'entry_limit_cents': entry_limit_series.dropna().iloc[0] if entry_limit_series.dropna().size else np.nan,
            'entry_floor_cents': entry_floor_series.dropna().iloc[0] if entry_floor_series.dropna().size else np.nan,
            'stop_cents': stop_series.dropna().iloc[0] if stop_series.dropna().size else np.nan,
            'panic_cents': panic_series.dropna().iloc[0] if panic_series.dropna().size else np.nan,
            'trades': int(len(grp)),
            'wins': int((pnl > 0).sum()),
            'losses': int((pnl < 0).sum()),
            'stopped_trades': int(stopped_mask.sum()),
            'settled_trades': int((grp['exit_reason'] == 'settlement').sum()),
            'false_stop_like_count': int(false_stops),
            'false_stop_like_rate': float(false_stops / stopped_mask.sum() * 100.0) if stopped_mask.sum() else np.nan,
            'net_pnl_dollars': float(pnl.sum()),
            'avg_pnl_dollars': float(pnl.mean()) if len(pnl) else np.nan,
            'win_rate': float((pnl > 0).mean() * 100.0) if len(pnl) else np.nan,
            'avg_win_dollars': float(wins.mean()) if len(wins) else np.nan,
            'avg_loss_dollars': float(losses.mean()) if len(losses) else np.nan,
            'worst_trade_dollars': float(pnl.min()) if len(pnl) else np.nan,
        })
    out = pd.DataFrame(rows)
    if out.empty:
        return out
    out['score_balanced'] = out['net_pnl_dollars'] - out['false_stop_like_count'] * 0.25 + out['win_rate'] * 0.02
    return out.sort_values(['score_balanced', 'net_pnl_dollars', 'win_rate', 'trades'], ascending=[False, False, False, False]).reset_index(drop=True)


def build_optimizer_grid(raw_events_df: pd.DataFrame, market_results_df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    if raw_events_df.empty:
        return pd.DataFrame(), pd.DataFrame()
    work = raw_events_df.copy()
    work['market_ticker'] = work['market_ticker'].fillna('').astype(str)
    work['ts'] = pd.to_datetime(work['ts'], utc=True, errors='coerce')
    work = work[work['ts'].notna()].sort_values(['market_ticker', 'ts'])
    market_lookup: dict[str, list[tuple[float, float, float, float, float]]] = {}
    for market, grp in work.groupby('market_ticker'):
        market_lookup[str(market)] = [
            (
                float(pd.to_numeric(pd.Series([rec.get('yes_bid_cents')]), errors='coerce').iloc[0]) if pd.notna(pd.to_numeric(pd.Series([rec.get('yes_bid_cents')]), errors='coerce').iloc[0]) else np.nan,
                float(pd.to_numeric(pd.Series([rec.get('yes_ask_cents')]), errors='coerce').iloc[0]) if pd.notna(pd.to_numeric(pd.Series([rec.get('yes_ask_cents')]), errors='coerce').iloc[0]) else np.nan,
                float(pd.to_numeric(pd.Series([rec.get('no_bid_cents')]), errors='coerce').iloc[0]) if pd.notna(pd.to_numeric(pd.Series([rec.get('no_bid_cents')]), errors='coerce').iloc[0]) else np.nan,
                float(pd.to_numeric(pd.Series([rec.get('no_ask_cents')]), errors='coerce').iloc[0]) if pd.notna(pd.to_numeric(pd.Series([rec.get('no_ask_cents')]), errors='coerce').iloc[0]) else np.nan,
                float(pd.to_numeric(pd.Series([rec.get('seconds_to_close')]), errors='coerce').iloc[0]) if pd.notna(pd.to_numeric(pd.Series([rec.get('seconds_to_close')]), errors='coerce').iloc[0]) else np.nan,
            )
            for rec in grp.to_dict('records')
        ]
    result_lookup: dict[str, str] = {}
    if not market_results_df.empty:
        market_col = 'market' if 'market' in market_results_df.columns else 'market_ticker'
        result_col = 'market_result' if 'market_result' in market_results_df.columns else 'result'
        for rec in market_results_df.to_dict('records'):
            market = str(rec.get(market_col) or '')
            result = str(rec.get(result_col) or '').lower()
            if market and result in {'yes', 'no'}:
                result_lookup[market] = result

    summary_rows: list[dict[str, Any]] = []
    trade_rows: list[dict[str, Any]] = []
    scenario_defs: list[tuple[int, float | None, float | None]] = []
    for entry_limit in range(88, 95):
        scenario_defs.append((entry_limit, None, None))
        for stop_cents in range(66, 75, 2):
            scenario_defs.append((entry_limit, float(stop_cents), None))
            for panic_cents in range(58, min(stop_cents, 67), 2):
                scenario_defs.append((entry_limit, float(stop_cents), float(panic_cents)))

    for entry_limit, stop_cents, panic_cents in scenario_defs:
        entry_floor = float(entry_limit - 2)
        scenario_name = f'entry_{entry_limit}_nostop' if stop_cents is None else (f'entry_{entry_limit}_stop_{int(stop_cents)}' if panic_cents is None else f'entry_{entry_limit}_stop_{int(stop_cents)}_panic_{int(panic_cents)}')
        pnls: list[float] = []
        wins = losses = stopped = settled = false_stop_like = 0
        worst_trade = np.nan
        avg_win_vals: list[float] = []
        avg_loss_vals: list[float] = []
        for market, events in market_lookup.items():
            market_result = result_lookup.get(market)
            if market_result not in {'yes', 'no'}:
                continue
            side = None
            entry_price = None
            exit_price = None
            exit_reason = 'settlement'
            for yes_bid, yes_ask, no_bid, no_ask, seconds_to_close in events:
                if np.isnan(seconds_to_close) or seconds_to_close <= 15 or seconds_to_close > 900:
                    continue
                if side is None:
                    candidates = []
                    if not np.isnan(yes_ask) and entry_floor <= yes_ask <= entry_limit:
                        candidates.append(('yes', yes_ask, yes_bid if not np.isnan(yes_bid) else -np.inf))
                    if not np.isnan(no_ask) and entry_floor <= no_ask <= entry_limit:
                        candidates.append(('no', no_ask, no_bid if not np.isnan(no_bid) else -np.inf))
                    if candidates:
                        candidates.sort(key=lambda item: (item[2], -item[1]), reverse=True)
                        side, entry_price, _ = candidates[0]
                    continue
                same_bid = yes_bid if side == 'yes' else no_bid
                if np.isnan(same_bid):
                    continue
                if panic_cents is not None and same_bid <= panic_cents:
                    exit_price = same_bid
                    exit_reason = 'panic_stop'
                    break
                if stop_cents is not None and same_bid <= stop_cents:
                    exit_price = same_bid
                    exit_reason = 'soft_stop'
                    break
            if side is None or entry_price is None:
                continue
            if exit_price is None:
                exit_price = 100.0 if market_result == side else 0.0
                settled += 1
            else:
                stopped += 1
                if market_result == side:
                    false_stop_like += 1
            pnl = round((float(exit_price) - float(entry_price)) * 10.0 / 100.0, 4)
            pnls.append(pnl)
            if pnl > 0:
                wins += 1
                avg_win_vals.append(pnl)
            elif pnl < 0:
                losses += 1
                avg_loss_vals.append(pnl)
            worst_trade = pnl if np.isnan(worst_trade) else min(worst_trade, pnl)
            trade_rows.append({
                'scenario': scenario_name,
                'market': market,
                'side': side,
                'entry_price_cents': float(entry_price),
                'exit_price_cents': float(exit_price),
                'exit_reason': exit_reason,
                'market_result': market_result,
                'net_pnl_dollars': pnl,
                'stopped_but_resolved_entry_side': bool(exit_reason != 'settlement' and market_result == side),
                'entry_limit_cents': entry_limit,
                'entry_floor_cents': entry_floor,
                'stop_cents': stop_cents,
                'panic_cents': panic_cents,
            })
        if not pnls:
            continue
        trades = len(pnls)
        net_pnl = float(np.sum(pnls))
        win_rate = float(wins / trades * 100.0) if trades else np.nan
        false_stop_rate = float(false_stop_like / stopped * 100.0) if stopped else np.nan
        score_balanced = net_pnl - false_stop_like * 0.25 + win_rate * 0.02
        summary_rows.append({
            'scenario': scenario_name,
            'entry_limit_cents': entry_limit,
            'entry_floor_cents': entry_floor,
            'stop_cents': stop_cents,
            'panic_cents': panic_cents,
            'trades': trades,
            'wins': wins,
            'losses': losses,
            'stopped_trades': stopped,
            'settled_trades': settled,
            'false_stop_like_count': false_stop_like,
            'false_stop_like_rate': false_stop_rate,
            'net_pnl_dollars': net_pnl,
            'avg_pnl_dollars': float(net_pnl / trades) if trades else np.nan,
            'win_rate': win_rate,
            'avg_win_dollars': float(np.mean(avg_win_vals)) if avg_win_vals else np.nan,
            'avg_loss_dollars': float(np.mean(avg_loss_vals)) if avg_loss_vals else np.nan,
            'worst_trade_dollars': float(worst_trade) if not np.isnan(worst_trade) else np.nan,
            'score_balanced': score_balanced,
        })

    summary_df = pd.DataFrame(summary_rows)
    trades_df = pd.DataFrame(trade_rows)
    if summary_df.empty:
        return summary_df, trades_df
    summary_df = summary_df.sort_values(['score_balanced', 'net_pnl_dollars', 'win_rate', 'trades'], ascending=[False, False, False, False]).reset_index(drop=True)
    return summary_df, trades_df


def build_replay(dataset_tag: str) -> dict[str, Any]:
    paths = dataset_paths(dataset_tag)
    labels_df = load_parquet_tree(paths['trade_labels_root'])
    features_df = load_parquet_tree(paths['features_root'])
    market_results_df = load_market_results(paths['market_results_path'])
    raw_ticker_df = attach_market_close_times(load_raw_ticker_events(paths['raw_root']), market_results_df)
    if labels_df.empty:
        raise RuntimeError(f'No trade labels found for dataset {dataset_tag}')

    enriched = add_same_side_features(enrich_trade_labels(labels_df, features_df))
    enriched['entry_day'] = pd.to_datetime(enriched.get('entry_dt'), utc=True, errors='coerce').dt.strftime('%Y-%m-%d')

    scenarios = [
        {'name': 'baseline'},
        {'name': 'feed_age_le_100', 'max_feed_age_ms': 100},
        {'name': 'feed_age_le_50', 'max_feed_age_ms': 50},
        {'name': 'submit_latency_le_75', 'max_submit_latency_ms': 75},
        {'name': 'range30_le_12', 'max_same_side_range_30s': 12},
        {'name': 'range30_le_8', 'max_same_side_range_30s': 8},
        {'name': 'fresh_and_calm', 'max_feed_age_ms': 100, 'max_same_side_range_30s': 12},
    ]

    summary_rows = []
    for scenario in scenarios:
        mask = scenario_mask(enriched, scenario)
        summary_rows.append(summarize_scenario(enriched, scenario['name'], mask))
    summary_df = pd.DataFrame(summary_rows).sort_values('kept_net_pnl_dollars', ascending=False).reset_index(drop=True)

    direct_scenarios = [
        {'name': 'quote_90_70', 'entry_floor_cents': 88, 'entry_limit_cents': 90, 'stop_cents': 70, 'panic_cents': 68},
        {'name': 'quote_90_70_calm12', 'entry_floor_cents': 88, 'entry_limit_cents': 90, 'stop_cents': 70, 'panic_cents': 68, 'max_range_30s': 12},
        {'name': 'quote_90_70_calm8', 'entry_floor_cents': 88, 'entry_limit_cents': 90, 'stop_cents': 70, 'panic_cents': 68, 'max_range_30s': 8},
    ]
    direct_trade_frames = [simulate_quote_replay(features_df, market_results_df, scenario) for scenario in direct_scenarios]
    non_empty_direct_frames = [df for df in direct_trade_frames if not df.empty]
    direct_trades_df = pd.concat(non_empty_direct_frames, ignore_index=True) if non_empty_direct_frames else pd.DataFrame()
    direct_summary_df = summarize_direct_replay(direct_trades_df)
    optimizer_summary_df, optimizer_trades_df = build_optimizer_grid(raw_ticker_df, market_results_df)

    run_id = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    run_dir = paths['replay_root'] / f'run_id={run_id}'
    run_dir.mkdir(parents=True, exist_ok=True)
    summary_df.to_parquet(run_dir / 'replay_summary.parquet', index=False)
    enriched.to_parquet(run_dir / 'replay_trade_table.parquet', index=False)
    direct_summary_df.to_parquet(run_dir / 'direct_replay_summary.parquet', index=False)
    direct_trades_df.to_parquet(run_dir / 'direct_replay_trades.parquet', index=False)
    optimizer_summary_df.to_parquet(run_dir / 'optimizer_summary.parquet', index=False)
    optimizer_trades_df.to_parquet(run_dir / 'optimizer_trades.parquet', index=False)
    manifest = {
        'dataset_tag': dataset_tag,
        'run_id': run_id,
        'built_at': datetime.now(timezone.utc).isoformat(),
        'trade_rows': int(len(enriched)),
        'scenario_rows': int(len(summary_df)),
        'best_scenario': str(summary_df.iloc[0]['scenario']) if not summary_df.empty else None,
        'best_scenario_net_pnl_dollars': float(summary_df.iloc[0]['kept_net_pnl_dollars']) if not summary_df.empty else None,
        'direct_replay_rows': int(len(direct_trades_df)),
        'direct_scenario_rows': int(len(direct_summary_df)),
        'best_direct_scenario': str(direct_summary_df.iloc[0]['scenario']) if not direct_summary_df.empty else None,
        'best_direct_net_pnl_dollars': float(direct_summary_df.iloc[0]['net_pnl_dollars']) if not direct_summary_df.empty else None,
        'optimizer_scenario_rows': int(len(optimizer_summary_df)),
        'optimizer_trade_rows': int(len(optimizer_trades_df)),
        'best_optimizer_scenario': str(optimizer_summary_df.iloc[0]['scenario']) if not optimizer_summary_df.empty else None,
        'best_optimizer_net_pnl_dollars': float(optimizer_summary_df.iloc[0]['net_pnl_dollars']) if not optimizer_summary_df.empty else None,
    }
    (paths['metadata_root'] / 'replay_status.json').write_text(json.dumps(manifest, indent=2), encoding='utf-8')
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser(description='Build Phase 3 replay summaries from trade labels and features.')
    parser.add_argument('--dataset', required=True)
    args = parser.parse_args()
    result = build_replay(args.dataset)
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()

