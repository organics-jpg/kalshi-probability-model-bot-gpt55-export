from __future__ import annotations

import argparse
import json
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from research_pipeline import build_dataset, dataset_paths


def load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding='utf-8'))
    except Exception:
        return {}


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2), encoding='utf-8')


def latest_raw_stats(raw_root: Path) -> dict[str, Any]:
    latest_mtime = 0.0
    latest_path = None
    file_count = 0
    for fp in raw_root.rglob('*.ndjson'):
        try:
            stat = fp.stat()
        except OSError:
            continue
        file_count += 1
        if stat.st_mtime > latest_mtime:
            latest_mtime = stat.st_mtime
            latest_path = fp
    return {
        'raw_file_count': file_count,
        'latest_raw_mtime': latest_mtime or None,
        'latest_raw_at': datetime.fromtimestamp(latest_mtime, timezone.utc).isoformat() if latest_mtime else None,
        'latest_raw_path': str(latest_path) if latest_path else None,
    }


def should_build(raw_stats: dict[str, Any], status: dict[str, Any]) -> bool:
    latest_raw_mtime = raw_stats.get('latest_raw_mtime')
    if not latest_raw_mtime:
        return False
    last_processed = status.get('last_processed_raw_mtime')
    if last_processed is None:
        return True
    try:
        return float(latest_raw_mtime) > float(last_processed) + 1e-9
    except Exception:
        return True


def run_once(dataset_tag: str, status_path: Path, interval_seconds: int, mode: str) -> dict[str, Any]:
    paths = dataset_paths(dataset_tag)
    raw_stats = latest_raw_stats(paths['raw_root'])
    previous = load_json(status_path)
    checked_at = datetime.now(timezone.utc).isoformat()
    payload: dict[str, Any] = {
        'dataset_tag': dataset_tag,
        'mode': mode,
        'interval_seconds': interval_seconds,
        'checked_at': checked_at,
        **raw_stats,
        'build_count': int(previous.get('build_count', 0) or 0),
        'last_build_at': previous.get('last_build_at'),
        'last_processed_raw_mtime': previous.get('last_processed_raw_mtime'),
        'last_processed_raw_at': previous.get('last_processed_raw_at'),
        'status': 'idle',
        'last_result': previous.get('last_result', {}),
        'last_error': previous.get('last_error'),
    }
    if should_build(raw_stats, previous):
        payload['status'] = 'building'
        write_json(status_path, payload)
        try:
            result = build_dataset(dataset_tag)
        except Exception as exc:
            payload['status'] = 'error'
            payload['last_error'] = str(exc)
            payload['checked_at'] = datetime.now(timezone.utc).isoformat()
            write_json(status_path, payload)
            raise
        payload['status'] = 'ok'
        payload['last_error'] = None
        payload['last_result'] = result
        payload['build_count'] = int(payload.get('build_count', 0)) + 1
        payload['last_build_at'] = datetime.now(timezone.utc).isoformat()
        payload['last_processed_raw_mtime'] = raw_stats.get('latest_raw_mtime')
        payload['last_processed_raw_at'] = raw_stats.get('latest_raw_at')
    else:
        payload['status'] = 'up_to_date'
    payload['checked_at'] = datetime.now(timezone.utc).isoformat()
    write_json(status_path, payload)
    return payload


def main() -> None:
    parser = argparse.ArgumentParser(description='Continuously ingest research raw events into normalized parquet datasets.')
    parser.add_argument('--dataset', required=True)
    parser.add_argument('--watch', action='store_true')
    parser.add_argument('--interval-seconds', type=int, default=300)
    args = parser.parse_args()

    paths = dataset_paths(args.dataset)
    status_path = paths['metadata_root'] / 'ingestion_status.json'

    if not args.watch:
        result = run_once(args.dataset, status_path, args.interval_seconds, mode='once')
        print(json.dumps(result, indent=2))
        return

    while True:
        result = run_once(args.dataset, status_path, args.interval_seconds, mode='watch')
        print(json.dumps(result, indent=2))
        time.sleep(max(int(args.interval_seconds), 5))


if __name__ == '__main__':
    main()
