# v28 BTC Activity-Memory Escape Bridge

Research-only; no live bot changes and no orders.

- Freeze UTC: `2026-05-06T14:36:09.327250+00:00`
- Candidate: `btc_activity_memory_escape_bridge`

## Current Read

- diagnostic_existing_false_conviction_freeze: best base_escape_energy entries/settled/coverage/net 91/91/80.53097345132744/-407.0c; blockers ['net_not_positive', 'reconstructed_share_gt_35pct'].
- diagnostic_existing_false_conviction_freeze: activity memory delta vs base net 14.0c.
- post_freeze_candidate: best base_escape_energy entries/settled/coverage/net 73/73/80.21978021978022/-840.0c; blockers ['net_not_positive', 'reconstructed_share_gt_35pct'].
- post_freeze_candidate: activity memory delta vs base net 0.0c.
- If activity-memory ranking fails to beat base escape-energy, keep the simpler lead.

## diagnostic_existing_false_conviction_freeze

- Future denominator: `113`

| rank | mode | entries | settled | W/L | coverage | net c | avg escape | avg activity energy | avg activity memory | avg recross mem | avg sigma mem | approved/recon | blockers |
|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| 1 | `base_escape_energy` | 91 | 91 | 60/31 | 80.530973 | -407.000000 | 0.343270 | 0.321142 | 0.395920 | 0.554913 | 0.488603 | 8/83 | net_not_positive, reconstructed_share_gt_35pct |
| 2 | `activity_memory_escape_energy` | 91 | 91 | 60/31 | 80.530973 | -393.000000 | 0.343258 | 0.321261 | 0.392233 | 0.550057 | 0.484164 | 8/83 | net_not_positive, reconstructed_share_gt_35pct |

## post_freeze_candidate

- Future denominator: `91`

| rank | mode | entries | settled | W/L | coverage | net c | avg escape | avg activity energy | avg activity memory | avg recross mem | avg sigma mem | approved/recon | blockers |
|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| 1 | `base_escape_energy` | 73 | 73 | 45/28 | 80.219780 | -840.000000 | 0.351878 | 0.330358 | 0.384532 | 0.531311 | 0.469042 | 8/65 | net_not_positive, reconstructed_share_gt_35pct |
| 2 | `activity_memory_escape_energy` | 73 | 73 | 45/28 | 80.219780 | -840.000000 | 0.351878 | 0.330358 | 0.384532 | 0.531311 | 0.469042 | 8/65 | net_not_positive, reconstructed_share_gt_35pct |
