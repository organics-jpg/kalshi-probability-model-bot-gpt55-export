# v28 False-Conviction Source-Quality Repair

Research-only; no live bot changes and no orders.

## Current Read

- Coverage floor needs 85 entries from denominator 113; kept after danger skip is 53, so repairs needed are 32.
- To keep reconstructed share <=35%, at least 56 of 85 entries must be approved-entry rows.
- Approved kept rows: 5; approved clean repair rows currently available: 30.
- Source-quality plus 75% coverage is not feasible with the current forward pool.

## Pool

- Future denominator: `113`
- Needed repairs: `32`
- Pool counts: `{'clean_pool': 50, 'approved_clean_pool': 30, 'reconstructed_clean_pool': 20, 'missed_market_clean_pool': 25, 'same_surface_clean_pool': 25}`

## Scenarios

| scenario | entries | settled | W/L | coverage | net c | approved/recon | recon share | source pass | blockers |
|---|---:|---:|---:|---:|---:|---:|---:|---|---|
| `approved_first_missed_then_any` | 85 | 85 | 56/29 | 75.221239 | -144.000000 | 27/58 | 0.682353 | False | reconstructed_share_gt_35pct, net_not_positive |
| `min_reconstructed_high_p` | 85 | 85 | 56/29 | 75.221239 | -133.000000 | 27/58 | 0.682353 | False | reconstructed_share_gt_35pct, net_not_positive |
| `approved_only` | 83 | 83 | 58/25 | 73.451327 | 151.000000 | 35/48 | 0.578313 | False | coverage_too_low, reconstructed_share_gt_35pct |
