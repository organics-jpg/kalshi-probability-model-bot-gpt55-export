# v28 FV Bridge Source-Quality Audit

Research-only; no live bot changes and no orders.

- Lead: `first_eligible_top80_escape_energy+escape_edge6_or_p65_or_far_edge4+continuous_recross_forget`

## Current Read

- diagnostic_existing_false_conviction_freeze: all-source lead entries/settled/coverage/net/recon 91/91/80.53097345132744/-407.0c/0.9120879120879121.
- diagnostic_existing_false_conviction_freeze: approved-only lead entries/settled/coverage/net 70/70/61.94690265486726/321.0c.
- post_freeze_candidate: all-source lead entries/settled/coverage/net/recon 75/75/80.64516129032258/-765.0c/0.8933333333333333.
- post_freeze_candidate: approved-only lead entries/settled/coverage/net 51/51/54.83870967741935/241.0c.
- If approved-only support stays thin, the bridge remains a research hypothesis, not a live candidate.

## diagnostic_existing_false_conviction_freeze

- Future denominator: `113`

| scenario | entries | settled | W/L | coverage | net c | recon share | approved/recon | avg edge | avg escape | blockers |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| `lead_reconstructed_only` | 91 | 91 | 56/35 | 80.530973 | -511.000000 | 1.000000 | 0/91 | 0.088287 | 0.313053 | net_not_positive, reconstructed_share_gt_35pct |
| `lead_all_sources` | 91 | 91 | 60/31 | 80.530973 | -407.000000 | 0.912088 | 8/83 | 0.089383 | 0.343270 | net_not_positive, reconstructed_share_gt_35pct |
| `lead_first_market_only` | 91 | 91 | 60/31 | 80.530973 | -407.000000 | 0.912088 | 8/83 | 0.089383 | 0.343270 | net_not_positive, reconstructed_share_gt_35pct |
| `lead_approved_preferred` | 91 | 91 | 60/31 | 80.530973 | -407.000000 | 0.912088 | 8/83 | 0.089383 | 0.343270 | net_not_positive, reconstructed_share_gt_35pct |
| `lead_approved_only` | 70 | 70 | 62/8 | 61.946903 | 321.000000 | 0.000000 | 70/0 | 0.104532 | 0.557836 | coverage_too_low |

## post_freeze_candidate

- Future denominator: `93`

| scenario | entries | settled | W/L | coverage | net c | recon share | approved/recon | avg edge | avg escape | blockers |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| `lead_all_sources` | 75 | 75 | 47/28 | 80.645161 | -765.000000 | 0.893333 | 8/67 | 0.097103 | 0.352441 | net_not_positive, reconstructed_share_gt_35pct |
| `lead_first_market_only` | 75 | 75 | 47/28 | 80.645161 | -765.000000 | 0.893333 | 8/67 | 0.097103 | 0.352441 | net_not_positive, reconstructed_share_gt_35pct |
| `lead_approved_preferred` | 75 | 75 | 47/28 | 80.645161 | -765.000000 | 0.893333 | 8/67 | 0.097103 | 0.352441 | net_not_positive, reconstructed_share_gt_35pct |
| `lead_reconstructed_only` | 75 | 75 | 44/31 | 80.645161 | -545.000000 | 1.000000 | 0/75 | 0.099725 | 0.314170 | net_not_positive, reconstructed_share_gt_35pct |
| `lead_approved_only` | 51 | 51 | 46/5 | 54.838710 | 241.000000 | 0.000000 | 51/0 | 0.103123 | 0.567863 | coverage_too_low |
