# v28 Control Risk-Stop Audit

Research-only; no live bot changes or orders.

- Generated UTC: `2026-05-11T03:42:25.356178+00:00`
- Source scorecard: `C:\Users\organ\Desktop\KALSHI PROBABILITY MODEL BOT\logs\edge_research\v28_continuous_scorecard_latest.json`

## Interpretation

- This audit is explanatory only; it does not clear live-readiness or weaken the risk stop.
- Risk stop is True by loss-count=True and drawdown=False.
- Control window is net positive 823.0c with max drawdown -196.0c (15.360501567398119%).
- Losses are 75 of 173 scored trades; full-loss events are 1 and 50-99c near-full losses are 6.
- The active blocker is churn/loss-count, not current drawdown-account-survival failure. Candidate exits still need to reduce loss clusters before any sidecar trial.

## Summary

- Risk stop: `True` `loss_count`
- Loss-count trigger: `True` (75 losses vs stop 5)
- Drawdown trigger: `False` (15.36% vs stop 40.00%)
- Gross PnL: `823c ($8.23)`
- Max drawdown: `-196c ($-1.96)`
- Full-loss events: `1`
- Near-full losses 50-99c: `6`
- Profit factor: `1.453944`

## Loss Buckets

| bucket | rows | net |
|---|---:|---:|
| `full_loss_ge_100c` | 1 | -134c ($-1.34) |
| `large_50_99c` | 6 | -436c ($-4.36) |
| `medium_25_49c` | 17 | -554c ($-5.54) |
| `micro_lt_10c` | 12 | -63c ($-0.63) |
| `small_10_24c` | 39 | -626c ($-6.26) |

## Losing Failure Classes

| class | rows | net |
|---|---:|---:|
| `exit_policy_cost` | 53 | -1029c ($-10.29) |
| `fv_or_entry_timing_error` | 22 | -784c ($-7.84) |

## Largest Loss Streaks

| rows | net | first market | last market | failure classes |
|---:|---:|---|---|---|
| 6 | -134c ($-1.34) | `KXBTC15M-26MAY051715-15` | `KXBTC15M-26MAY051800-00` | `{'fv_or_entry_timing_error': 3, 'exit_policy_cost': 3}` |
| 4 | -144c ($-1.44) | `KXBTC15M-26MAY060745-45` | `KXBTC15M-26MAY060800-00` | `{'fv_or_entry_timing_error': 2, 'exit_policy_cost': 2}` |
| 3 | -102c ($-1.02) | `KXBTC15M-26MAY060900-00` | `KXBTC15M-26MAY060900-00` | `{'fv_or_entry_timing_error': 2, 'exit_policy_cost': 1}` |
| 3 | -66c ($-0.66) | `KXBTC15M-26MAY060300-00` | `KXBTC15M-26MAY060300-00` | `{'exit_policy_cost': 3}` |
| 3 | -60c ($-0.60) | `KXBTC15M-26MAY060700-00` | `KXBTC15M-26MAY060700-00` | `{'fv_or_entry_timing_error': 1, 'exit_policy_cost': 2}` |
| 3 | -56c ($-0.56) | `KXBTC15M-26MAY071215-15` | `KXBTC15M-26MAY071230-30` | `{'exit_policy_cost': 3}` |
| 3 | -44c ($-0.44) | `KXBTC15M-26MAY060945-45` | `KXBTC15M-26MAY060945-45` | `{'exit_policy_cost': 3}` |
| 3 | -37c ($-0.37) | `KXBTC15M-26MAY060930-30` | `KXBTC15M-26MAY060930-30` | `{'exit_policy_cost': 3}` |

## Largest Losing Trades

| market | side | result | gross | hold | exit value | failure | flags |
|---|---|---|---:|---:|---:|---|---|
| `KXBTC15M-26MAY062015-15` | yes | no | -134c ($-1.34) | -134c ($-1.34) | 0c ($0.00) | `fv_or_entry_timing_error` | `h1_feed_fresh` |
| `KXBTC15M-26MAY051830-30` | no | yes | -92c ($-0.92) | -160c ($-1.60) | 68c ($0.68) | `fv_or_entry_timing_error` | `h1_feed_fresh` |
| `KXBTC15M-26MAY061800-00` | no | no | -86c ($-0.86) | 66c ($0.66) | -152c ($-1.52) | `exit_policy_cost` | `h1_feed_fresh,h6_recross_hazard_high` |
| `KXBTC15M-26MAY060900-00` | yes | no | -76c ($-0.76) | -156c ($-1.56) | 80c ($0.80) | `fv_or_entry_timing_error` | `h1_feed_fresh,h6_recross_hazard_high` |
| `KXBTC15M-26MAY060745-45` | yes | no | -70c ($-0.70) | -156c ($-1.56) | 86c ($0.86) | `fv_or_entry_timing_error` | `h1_feed_fresh` |
| `KXBTC15M-26MAY062015-15` | no | no | -60c ($-0.60) | 116c ($1.16) | -176c ($-1.76) | `exit_policy_cost` | `h1_feed_fresh` |
| `KXBTC15M-26MAY060330-30` | yes | yes | -52c ($-0.52) | 42c ($0.42) | -94c ($-0.94) | `exit_policy_cost` | `h1_feed_fresh,h2_crowded_depth` |
| `KXBTC15M-26MAY051715-15` | yes | no | -48c ($-0.48) | -138c ($-1.38) | 90c ($0.90) | `fv_or_entry_timing_error` | `h1_feed_fresh` |
| `KXBTC15M-26MAY061100-00` | no | no | -40c ($-0.40) | 34c ($0.34) | -74c ($-0.74) | `exit_policy_cost` | `h1_feed_fresh,h6_recross_hazard_high` |
| `KXBTC15M-26MAY052315-15` | yes | yes | -38c ($-0.38) | 38c ($0.38) | -76c ($-0.76) | `exit_policy_cost` | `h1_feed_fresh` |
| `KXBTC15M-26MAY071230-30` | yes | yes | -38c ($-0.38) | 32c ($0.32) | -70c ($-0.70) | `exit_policy_cost` | `h1_feed_fresh` |
| `KXBTC15M-26MAY071000-00` | no | no | -36c ($-0.36) | 54c ($0.54) | -90c ($-0.90) | `exit_policy_cost` | `h1_feed_fresh,h2_thin_touch_depth,h6_recross_hazard_high` |
