# v28 Dual-Lane Live Market Snapshot Ledger

Research-only. Append-only score ledger; no live bot logic changes, no orders.

- Generated UTC: `2026-05-11T03:47:38.013877+00:00`
- Rows: `445`
- Unique score states: `440`
- Appended this run: `False`
- Latest update UTC: `2026-05-11T03:46:17.885041+00:00`
- Freeze UTC/local: `2026-05-07T13:00:17.363339+00:00` / `2026-05-07T09:00:17.363339-04:00`
- Decision: `no_live_test`
- Live baseline: `-256c ($-2.56)`

## Latest Snapshot

| metric | sidecar | primary proxy | own-freeze promotion | parent-shrink repair | shrink frontier |
|---|---:|---:|---:|---:|---:|
| entries | 12 | 16 | 14 settled | 7 settled | 7 settled |
| W/L | 11/1 | 4/12 | 12/2 | 7/0 | 7/0 |
| PnL W/L | 10/2 | 4/12 | n/a | n/a | n/a |
| net | 304c ($3.04) | -40c ($-0.40) | 49c ($0.49) | 185c ($1.85) | 155c ($1.55) |
| coverage | 66.67% | 88.89% | 77.78% | 87.50% | 100.00% |
| recon | 0.00% | 100.00% | 14.29% | 42.86% | 42.86% |
| label | n/a | n/a | n/a | n/a | `shrink25_weight075` / `0.75` |

## Trend

- Sidecar net delta vs previous snapshot: `0c ($0.00)`
- Primary proxy net delta vs previous snapshot: `0c ($0.00)`
- Sidecar net delta since ledger start: `180c ($1.80)`
- Primary proxy net delta since ledger start: `70c ($0.70)`
- Windows since freeze / remaining: `347` / `0`
- Parent-shrink windows since freeze / remaining: `53` / `0`
- Frontier windows since freeze / remaining: `51` / `0`
- Post-freeze events / entry rows / markets: `2842` / `26` / `18`

## Current Blockers

- `minimum_forward_sample`
- `fragility_cushion`
- `strict_precheck_freshness`
- `loss_bottleneck_classified`
- `parent_shrink_forward_sample`
- `parent_shrink_frontier_forward_sample`
- `sidecar_safety_forward_sample`
- `same_window_live_edge`
- `overlay_filter_forward_sample`
- `overlay_v2_filter_forward_sample`

## Recent Rows

| update UTC | windows | markets | sidecar W/L | sidecar net | primary W/L | primary net | decision |
|---|---:|---:|---:|---:|---:|---:|---|
| `2026-05-11T02:42:36.366053+00:00` | 342 | 18 | 11/1 | 304c ($3.04) | 4/12 | -40c ($-0.40) | `no_live_test` |
| `2026-05-11T02:48:01.233056+00:00` | 343 | 18 | 11/1 | 304c ($3.04) | 4/12 | -40c ($-0.40) | `no_live_test` |
| `2026-05-11T02:54:42.010073+00:00` | 343 | 18 | 11/1 | 304c ($3.04) | 4/12 | -40c ($-0.40) | `no_live_test` |
| `2026-05-11T03:00:45.734998+00:00` | 344 | 18 | 11/1 | 304c ($3.04) | 4/12 | -40c ($-0.40) | `no_live_test` |
| `2026-05-11T03:06:48.134727+00:00` | 344 | 18 | 11/1 | 304c ($3.04) | 4/12 | -40c ($-0.40) | `no_live_test` |
| `2026-05-11T03:18:53.439073+00:00` | 345 | 18 | 11/1 | 304c ($3.04) | 4/12 | -40c ($-0.40) | `no_live_test` |
| `2026-05-11T03:30:58.328587+00:00` | 345 | 18 | 11/1 | 304c ($3.04) | 4/12 | -40c ($-0.40) | `no_live_test` |
| `2026-05-11T03:33:59.738600+00:00` | 346 | 18 | 11/1 | 304c ($3.04) | 4/12 | -40c ($-0.40) | `no_live_test` |
| `2026-05-11T03:43:03.433716+00:00` | 346 | 18 | 11/1 | 304c ($3.04) | 4/12 | -40c ($-0.40) | `no_live_test` |
| `2026-05-11T03:46:17.885041+00:00` | 347 | 18 | 11/1 | 304c ($3.04) | 4/12 | -40c ($-0.40) | `no_live_test` |
