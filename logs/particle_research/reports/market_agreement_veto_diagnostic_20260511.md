# Market Agreement Veto Diagnostic

This diagnostic was run after the fresh live shadow capture `particle_shadow_readonly_fresh_20260511T113926Z` exposed a late-market failure: the particle replay selected NO while both market/current probabilities were strongly YES, and YES settled.

Reports evaluated:

- `particle_side_safety_oos_20260511TLOCKED/reports/materialized_online_logit_market_mean_rolling_vol_600s.json`
- `particle_dynamic_oos_20260511TLOCKEDNEXT/reports/materialized_online_logit_market_mean_rolling_vol_600s.json`
- `particle_dynamic600_oos_20260511TLOCKEDNEXT2/reports/materialized_online_logit_market_mean_rolling_vol_600s.json`
- `particle_shadow_readonly_fresh_20260511T113926Z/reports/fresh_live_particle_replay.json`

| run | base selected | base pnl c | agree market pnl c | agree current pnl c | agree both pnl c | not against both 5pp pnl c | not against both 10pp pnl c | not against both 20pp pnl c |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| side safety lock | 2941 | 39779 | 16962 | 22187 | 16396 | 28998 | 34116 | 36016 |
| dynamic 300 lock | 2884 | 39334 | 11579 | 22316 | 10788 | 29288 | 36082 | 41727 |
| dynamic 600 lock | 2690 | 3298 | -2733 | -7088 | -2682 | -10098 | -17255 | -11958 |
| fresh 20260511T113926Z | 174 | -1160 | 0 | 0 | 0 | 0 | 0 | 0 |
| aggregate | 8689 | 81251 | 25808 | 37415 | 24502 | 48188 | 52943 | 65785 |

Conclusion: a simple market/current agreement veto is useful as a warning diagnostic, but it is not promotable. It prevents the fresh late-market NO failure, yet it materially reduces aggregate locked-OOS PnL and does not fix the third locked run. The remaining problem is still side/regime instability, not merely a missing market-agreement threshold.
