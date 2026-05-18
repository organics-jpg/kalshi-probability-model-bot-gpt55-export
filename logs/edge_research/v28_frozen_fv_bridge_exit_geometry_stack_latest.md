# v28 Frozen FV Bridge + Exit Geometry Stack

Research-only; no live bot changes and no orders.

- Freeze timestamp UTC: `2026-05-06T14:53:53.830835+00:00`
- Candidate: `lead_fv_bridge_plus_side_geometry_reduce_suppression`
- FV bridge: `first_eligible_top80_escape_energy+escape_edge6_or_p65_or_far_edge4+continuous_recross_forget`
- Exit rule: `Suppress mushroom_v28_probability_reduce only when p_hold >= 0.75 and fair_drawdown sign agrees with held side.`

## Current Read

- Frozen stack timestamp is 2026-05-06T14:53:53.830835+00:00.
- Rows before that timestamp are excluded from promotion evidence.
- Approved-only future stack has 48 settled rows, coverage 66.66666666666666, stack net 213.0c, matched 48, suppressed 2.

## diagnostic_existing_false_conviction_freeze

| scenario | settled | coverage | dir W/L | realized c | stack c | hold c | matched | suppressed | ready | blockers |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|---|
| `lead_reconstructed_only` | 68 | 94.444 | 40/28 | -535.000 | -631.000 | -152.000 | 21 | 2 | False | coverage_too_high, stack_net_not_positive, matched_exit_share_lt_70pct |
| `lead_all_sources` | 72 | 100.000 | 45/27 | -697.000 | -793.000 | -73.000 | 28 | 2 | False | coverage_too_high, stack_net_not_positive, matched_exit_share_lt_70pct |
| `lead_first_market_only` | 72 | 100.000 | 45/27 | -697.000 | -793.000 | -73.000 | 28 | 2 | False | coverage_too_high, stack_net_not_positive, matched_exit_share_lt_70pct |
| `lead_approved_preferred` | 72 | 100.000 | 45/27 | -697.000 | -793.000 | -73.000 | 28 | 2 | False | coverage_too_high, stack_net_not_positive, matched_exit_share_lt_70pct |
| `lead_approved_only` | 48 | 66.667 | 43/5 | 309.000 | 213.000 | 493.000 | 48 | 2 | False | coverage_too_low |

## post_freeze_candidate

| scenario | settled | coverage | dir W/L | realized c | stack c | hold c | matched | suppressed | ready | blockers |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|---|
| `lead_all_sources` | 72 | 100.000 | 45/27 | -697.000 | -793.000 | -73.000 | 28 | 2 | False | coverage_too_high, stack_net_not_positive, matched_exit_share_lt_70pct |
| `lead_first_market_only` | 72 | 100.000 | 45/27 | -697.000 | -793.000 | -73.000 | 28 | 2 | False | coverage_too_high, stack_net_not_positive, matched_exit_share_lt_70pct |
| `lead_approved_preferred` | 72 | 100.000 | 45/27 | -697.000 | -793.000 | -73.000 | 28 | 2 | False | coverage_too_high, stack_net_not_positive, matched_exit_share_lt_70pct |
| `lead_reconstructed_only` | 72 | 100.000 | 42/30 | -477.000 | -573.000 | -115.000 | 22 | 2 | False | coverage_too_high, stack_net_not_positive, matched_exit_share_lt_70pct |
| `lead_approved_only` | 48 | 66.667 | 43/5 | 309.000 | 213.000 | 493.000 | 48 | 2 | False | coverage_too_low |
