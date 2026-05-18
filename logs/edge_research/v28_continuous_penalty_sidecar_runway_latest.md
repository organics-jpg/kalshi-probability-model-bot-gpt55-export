# v28 Continuous-Penalty Sidecar Runway

Research-only runway audit. No live orders.

- Generated UTC: `2026-05-11T03:08:58.015726+00:00`
- Live baseline: `-116.990000c`
- Candidate live-ready: `False`
- Best candidate: `post_penalty_birth_bridge / post_penalty_birth_bridge_cheap_penalty025_rank_only`
- Best settled/W-L/net/source/cushion: `51/41-10/504.000000c/0.176471/5`
- Rows to sample / net to live / perfect wins to live: `0/0.000000c/0`
- Full losses before cushion breaks: `2`
- Blockers: `live_ready_false`

## Interpretation

- Best continuous-penalty sidecar has 51 settled, W/L 41/10, net 504.0c, and source share 0.17647058823529413.
- It needs 0 more settled row for sample, but 0.0c more PnL to beat the refreshed live baseline of -116.99c.
- At a 100c maximum single-row win assumption, it needs at least 0 additional perfect wins, not just one sample row.
- Current cushion can absorb 2 full-loss rows before falling below the three-full-loss gate.

## Rank-Only Rows

| lane | candidate | settled | W-L | net c | delta live | source | cushion | sample need | perfect wins to live | full-loss capacity | blockers |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| `post_penalty_birth_bridge` | `post_penalty_birth_bridge_cheap_penalty025_rank_only` | 51 | 41-10 | 504.000000 | 620.990000 | 0.176471 | 5 | 0 | 0 | 2 | `live_ready_false` |
| `post_penalty_birth_bridge` | `post_penalty_birth_bridge_cheap_penalty050_rank_only` | 51 | 41-10 | 504.000000 | 620.990000 | 0.176471 | 5 | 0 | 0 | 2 | `live_ready_false` |
| `post_penalty_birth_bridge` | `post_penalty_birth_bridge_cheap_penalty100_rank_only` | 51 | 41-10 | 504.000000 | 620.990000 | 0.176471 | 5 | 0 | 0 | 2 | `live_ready_false` |
| `post_penalty_birth_entry` | `post_penalty_birth_entry_cheap_penalty025_rank_only` | 51 | 41-10 | 504.000000 | 620.990000 | 0.176471 | 5 | 0 | 0 | 2 | `live_ready_false` |
| `post_penalty_birth_entry` | `post_penalty_birth_entry_cheap_penalty050_rank_only` | 51 | 41-10 | 504.000000 | 620.990000 | 0.176471 | 5 | 0 | 0 | 2 | `live_ready_false` |
| `post_penalty_birth_entry` | `post_penalty_birth_entry_cheap_penalty100_rank_only` | 51 | 41-10 | 504.000000 | 620.990000 | 0.176471 | 5 | 0 | 0 | 2 | `live_ready_false` |
