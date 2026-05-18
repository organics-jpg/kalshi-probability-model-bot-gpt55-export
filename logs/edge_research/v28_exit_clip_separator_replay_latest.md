# v28 Exit Clip Separator Replay

Research-only; no live bot changes or orders.

- Generated UTC: `2026-05-11T03:07:51.968936+00:00`
- Clip watch freeze UTC: `2026-05-07T04:04:23.876080+00:00`

## Interpretation

- Diagnostic replay includes rows before the clip-watch freeze; use it only as mechanism evidence.
- Diagnostic replay delta is 1187.0c with 29 fewer losses and 6 suppressed losers.
- Post-watch replay has 36 rows and remains promotion-blocked until fresh rows accumulate.

## Summaries

| label | rows | current W/L | candidate W/L | current net | candidate net | delta | suppressed | loss reduction | suppressed losers | cushion | blockers |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| `diagnostic_from_exit_reduce_freeze` | 132 | 73/56 | 104/27 | 721c | 1908c | 1187c | 40 | 29 | 6 | 19 | diagnostic_replay_not_clip_watch_forward, suppressed_losers_present |
| `post_clip_watch_freeze` | 36 | 23/12 | 29/6 | 478c | 598c | 120c | 10 | 6 | 2 | 5 | suppressed_decisions_lt_30, suppressed_losers_present, post_clip_watch_sample_pending |
