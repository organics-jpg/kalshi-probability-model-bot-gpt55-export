# v28 Frozen FV Bridge Exit Combo Stack

Research-only; no live bot changes and no orders.

- Freeze timestamp UTC: `2026-05-06T15:02:08.902210+00:00`
- Candidate: `lead_fv_bridge_plus_reduce_geometry_plus_collapse_drawdown_lte_12`
- FV bridge: `first_eligible_top80_escape_energy+escape_edge6_or_p65_or_far_edge4+continuous_recross_forget`
- Policy: `reduce_geometry_plus_collapse_drawdown_lte_12`

## Current Read

- Frozen combo timestamp is 2026-05-06T15:02:08.902210+00:00.
- Rows before that timestamp are excluded from promotion evidence.
- Approved-only future combo has 48 settled rows, coverage 66.66666666666666, candidate net 581.0c, matched exits 48, suppressed exits 6.

## diagnostic_existing_false_conviction_freeze

| scenario | settled | coverage | dir W/L | current c | candidate c | hold c | matched | suppressed | ready | blockers |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|---|
| `lead_reconstructed_only` | 68 | 94.444 | 40/28 | -535.000 | -471.000 | -152.000 | 21 | 4 | False | coverage_too_high, candidate_net_not_positive, matched_exit_share_lt_70pct |
| `lead_all_sources` | 72 | 100.000 | 45/27 | -697.000 | -425.000 | -73.000 | 28 | 6 | False | coverage_too_high, candidate_net_not_positive, matched_exit_share_lt_70pct |
| `lead_first_market_only` | 72 | 100.000 | 45/27 | -697.000 | -425.000 | -73.000 | 28 | 6 | False | coverage_too_high, candidate_net_not_positive, matched_exit_share_lt_70pct |
| `lead_approved_preferred` | 72 | 100.000 | 45/27 | -697.000 | -425.000 | -73.000 | 28 | 6 | False | coverage_too_high, candidate_net_not_positive, matched_exit_share_lt_70pct |
| `lead_approved_only` | 48 | 66.667 | 43/5 | 309.000 | 581.000 | 493.000 | 48 | 6 | False | coverage_too_low |

## post_freeze_candidate

| scenario | settled | coverage | dir W/L | current c | candidate c | hold c | matched | suppressed | ready | blockers |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|---|
| `lead_all_sources` | 72 | 100.000 | 45/27 | -697.000 | -425.000 | -73.000 | 28 | 6 | False | coverage_too_high, candidate_net_not_positive, matched_exit_share_lt_70pct |
| `lead_first_market_only` | 72 | 100.000 | 45/27 | -697.000 | -425.000 | -73.000 | 28 | 6 | False | coverage_too_high, candidate_net_not_positive, matched_exit_share_lt_70pct |
| `lead_approved_preferred` | 72 | 100.000 | 45/27 | -697.000 | -425.000 | -73.000 | 28 | 6 | False | coverage_too_high, candidate_net_not_positive, matched_exit_share_lt_70pct |
| `lead_reconstructed_only` | 72 | 100.000 | 42/30 | -477.000 | -413.000 | -115.000 | 22 | 4 | False | coverage_too_high, candidate_net_not_positive, matched_exit_share_lt_70pct |
| `lead_approved_only` | 48 | 66.667 | 43/5 | 309.000 | 581.000 | 493.000 | 48 | 6 | False | coverage_too_low |
