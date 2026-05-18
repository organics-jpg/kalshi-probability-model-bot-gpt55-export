# v28 FV Bridge + Exit Geometry Stack

Research-only; no live bot changes and no orders.

## Current Read

- diagnostic_existing_false_conviction_freeze: approved-only realized 321.0c, stack 497.0c, hold 705.0c, matched 70/70, suppressed 7.
- post_freeze_candidate: approved-only realized 241.0c, stack 251.0c, hold 552.0c, matched 51/51, suppressed 4.

## diagnostic_existing_false_conviction_freeze

| scenario | settled | coverage | dir W/L | realized c | stack c | hold c | stack-realized c | stack-hold c | matched | suppressed | neg winners current/stack |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `lead_reconstructed_only` | 91 | 80.531 | 56/35 | -511.000 | -395.000 | -91.000 | 116.000 | -304.000 | 37 | 6 | 0/0 |
| `lead_all_sources` | 91 | 80.531 | 60/31 | -407.000 | -343.000 | 113.000 | 64.000 | -456.000 | 42 | 5 | 2/2 |
| `lead_first_market_only` | 91 | 80.531 | 60/31 | -407.000 | -343.000 | 113.000 | 64.000 | -456.000 | 42 | 5 | 2/2 |
| `lead_approved_preferred` | 91 | 80.531 | 60/31 | -407.000 | -343.000 | 113.000 | 64.000 | -456.000 | 42 | 5 | 2/2 |
| `lead_approved_only` | 70 | 61.947 | 62/8 | 321.000 | 497.000 | 705.000 | 176.000 | -208.000 | 70 | 7 | 24/18 |

### Suppressed Matched Rows

| scenario | market | source | side | side won | realized c | stack c | delta c | exit reason | match sec |
|---|---|---|---|---:|---:|---:|---:|---|---:|
| `lead_reconstructed_only` | `KXBTC15M-26MAY060630-30` | `rejected_actionable` | `yes` | True | 59.000 | 113.000 | 54.000 | `mushroom_v28_probability_reduce` | 125.301 |
| `lead_reconstructed_only` | `KXBTC15M-26MAY060645-45` | `rejected_actionable` | `yes` | True | 68.000 | 120.000 | 52.000 | `mushroom_v28_probability_reduce` | 228.857 |
| `lead_reconstructed_only` | `KXBTC15M-26MAY060915-15` | `rejected_actionable` | `no` | True | 66.000 | 126.000 | 60.000 | `mushroom_v28_probability_reduce` | 12.715 |
| `lead_reconstructed_only` | `KXBTC15M-26MAY061045-45` | `rejected_actionable` | `yes` | True | 18.000 | 64.000 | 46.000 | `mushroom_v28_probability_reduce` | 12.141 |
| `lead_reconstructed_only` | `KXBTC15M-26MAY071015-15` | `rejected_actionable` | `no` | False | -149.000 | -307.000 | -158.000 | `mushroom_v28_probability_reduce` | 36.282 |
| `lead_reconstructed_only` | `KXBTC15M-26MAY071045-45` | `rejected_actionable` | `no` | True | 51.000 | 113.000 | 62.000 | `mushroom_v28_probability_reduce` | 0.555 |
| `lead_all_sources` | `KXBTC15M-26MAY060630-30` | `rejected_actionable` | `yes` | True | 59.000 | 113.000 | 54.000 | `mushroom_v28_probability_reduce` | 125.301 |
| `lead_all_sources` | `KXBTC15M-26MAY060915-15` | `rejected_actionable` | `no` | True | 66.000 | 126.000 | 60.000 | `mushroom_v28_probability_reduce` | 12.715 |
| `lead_all_sources` | `KXBTC15M-26MAY061045-45` | `rejected_actionable` | `yes` | True | 18.000 | 64.000 | 46.000 | `mushroom_v28_probability_reduce` | 12.141 |
| `lead_all_sources` | `KXBTC15M-26MAY071015-15` | `rejected_actionable` | `no` | False | -149.000 | -307.000 | -158.000 | `mushroom_v28_probability_reduce` | 36.282 |
| `lead_all_sources` | `KXBTC15M-26MAY071045-45` | `rejected_actionable` | `no` | True | 51.000 | 113.000 | 62.000 | `mushroom_v28_probability_reduce` | 0.555 |
| `lead_first_market_only` | `KXBTC15M-26MAY060630-30` | `rejected_actionable` | `yes` | True | 59.000 | 113.000 | 54.000 | `mushroom_v28_probability_reduce` | 125.301 |
| `lead_first_market_only` | `KXBTC15M-26MAY060915-15` | `rejected_actionable` | `no` | True | 66.000 | 126.000 | 60.000 | `mushroom_v28_probability_reduce` | 12.715 |
| `lead_first_market_only` | `KXBTC15M-26MAY061045-45` | `rejected_actionable` | `yes` | True | 18.000 | 64.000 | 46.000 | `mushroom_v28_probability_reduce` | 12.141 |
| `lead_first_market_only` | `KXBTC15M-26MAY071015-15` | `rejected_actionable` | `no` | False | -149.000 | -307.000 | -158.000 | `mushroom_v28_probability_reduce` | 36.282 |
| `lead_first_market_only` | `KXBTC15M-26MAY071045-45` | `rejected_actionable` | `no` | True | 51.000 | 113.000 | 62.000 | `mushroom_v28_probability_reduce` | 0.555 |
| `lead_approved_preferred` | `KXBTC15M-26MAY060630-30` | `rejected_actionable` | `yes` | True | 59.000 | 113.000 | 54.000 | `mushroom_v28_probability_reduce` | 125.301 |
| `lead_approved_preferred` | `KXBTC15M-26MAY060915-15` | `rejected_actionable` | `no` | True | 66.000 | 126.000 | 60.000 | `mushroom_v28_probability_reduce` | 12.715 |
| `lead_approved_preferred` | `KXBTC15M-26MAY061045-45` | `rejected_actionable` | `yes` | True | 18.000 | 64.000 | 46.000 | `mushroom_v28_probability_reduce` | 12.141 |
| `lead_approved_preferred` | `KXBTC15M-26MAY071015-15` | `rejected_actionable` | `no` | False | -149.000 | -307.000 | -158.000 | `mushroom_v28_probability_reduce` | 36.282 |
| `lead_approved_preferred` | `KXBTC15M-26MAY071045-45` | `rejected_actionable` | `no` | True | 51.000 | 113.000 | 62.000 | `mushroom_v28_probability_reduce` | 0.555 |
| `lead_approved_only` | `KXBTC15M-26MAY060630-30` | `approved_entry` | `yes` | True | -14.000 | 40.000 | 54.000 | `mushroom_v28_probability_reduce` | 0.021 |
| `lead_approved_only` | `KXBTC15M-26MAY060645-45` | `approved_entry` | `yes` | True | -18.000 | 34.000 | 52.000 | `mushroom_v28_probability_reduce` | 0.017 |
| `lead_approved_only` | `KXBTC15M-26MAY060915-15` | `approved_entry` | `no` | True | -2.000 | 58.000 | 60.000 | `mushroom_v28_probability_reduce` | 0.061 |
| `lead_approved_only` | `KXBTC15M-26MAY061030-30` | `approved_entry` | `yes` | True | -18.000 | 42.000 | 60.000 | `mushroom_v28_probability_reduce` | 0.034 |
| `lead_approved_only` | `KXBTC15M-26MAY061045-45` | `approved_entry` | `yes` | True | -8.000 | 38.000 | 46.000 | `mushroom_v28_probability_reduce` | 0.033 |
| `lead_approved_only` | `KXBTC15M-26MAY071015-15` | `approved_entry` | `no` | False | 0.000 | -158.000 | -158.000 | `mushroom_v28_probability_reduce` | 0.122 |
| `lead_approved_only` | `KXBTC15M-26MAY071045-45` | `approved_entry` | `no` | True | -12.000 | 50.000 | 62.000 | `mushroom_v28_probability_reduce` | 0.114 |

## post_freeze_candidate

| scenario | settled | coverage | dir W/L | realized c | stack c | hold c | stack-realized c | stack-hold c | matched | suppressed | neg winners current/stack |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `lead_all_sources` | 75 | 80.645 | 47/28 | -765.000 | -815.000 | -93.000 | -50.000 | -722.000 | 29 | 3 | 2/2 |
| `lead_first_market_only` | 75 | 80.645 | 47/28 | -765.000 | -815.000 | -93.000 | -50.000 | -722.000 | 29 | 3 | 2/2 |
| `lead_approved_preferred` | 75 | 80.645 | 47/28 | -765.000 | -815.000 | -93.000 | -50.000 | -722.000 | 29 | 3 | 2/2 |
| `lead_reconstructed_only` | 75 | 80.645 | 44/31 | -545.000 | -595.000 | -135.000 | -50.000 | -460.000 | 23 | 3 | 0/0 |
| `lead_approved_only` | 51 | 54.839 | 46/5 | 241.000 | 251.000 | 552.000 | 10.000 | -301.000 | 51 | 4 | 16/13 |

### Suppressed Matched Rows

| scenario | market | source | side | side won | realized c | stack c | delta c | exit reason | match sec |
|---|---|---|---|---:|---:|---:|---:|---|---:|
| `lead_all_sources` | `KXBTC15M-26MAY061045-45` | `rejected_actionable` | `yes` | True | 18.000 | 64.000 | 46.000 | `mushroom_v28_probability_reduce` | 12.141 |
| `lead_all_sources` | `KXBTC15M-26MAY071015-15` | `rejected_actionable` | `no` | False | -149.000 | -307.000 | -158.000 | `mushroom_v28_probability_reduce` | 36.282 |
| `lead_all_sources` | `KXBTC15M-26MAY071045-45` | `rejected_actionable` | `no` | True | 51.000 | 113.000 | 62.000 | `mushroom_v28_probability_reduce` | 0.555 |
| `lead_first_market_only` | `KXBTC15M-26MAY061045-45` | `rejected_actionable` | `yes` | True | 18.000 | 64.000 | 46.000 | `mushroom_v28_probability_reduce` | 12.141 |
| `lead_first_market_only` | `KXBTC15M-26MAY071015-15` | `rejected_actionable` | `no` | False | -149.000 | -307.000 | -158.000 | `mushroom_v28_probability_reduce` | 36.282 |
| `lead_first_market_only` | `KXBTC15M-26MAY071045-45` | `rejected_actionable` | `no` | True | 51.000 | 113.000 | 62.000 | `mushroom_v28_probability_reduce` | 0.555 |
| `lead_approved_preferred` | `KXBTC15M-26MAY061045-45` | `rejected_actionable` | `yes` | True | 18.000 | 64.000 | 46.000 | `mushroom_v28_probability_reduce` | 12.141 |
| `lead_approved_preferred` | `KXBTC15M-26MAY071015-15` | `rejected_actionable` | `no` | False | -149.000 | -307.000 | -158.000 | `mushroom_v28_probability_reduce` | 36.282 |
| `lead_approved_preferred` | `KXBTC15M-26MAY071045-45` | `rejected_actionable` | `no` | True | 51.000 | 113.000 | 62.000 | `mushroom_v28_probability_reduce` | 0.555 |
| `lead_reconstructed_only` | `KXBTC15M-26MAY061045-45` | `rejected_actionable` | `yes` | True | 18.000 | 64.000 | 46.000 | `mushroom_v28_probability_reduce` | 12.141 |
| `lead_reconstructed_only` | `KXBTC15M-26MAY071015-15` | `rejected_actionable` | `no` | False | -149.000 | -307.000 | -158.000 | `mushroom_v28_probability_reduce` | 36.282 |
| `lead_reconstructed_only` | `KXBTC15M-26MAY071045-45` | `rejected_actionable` | `no` | True | 51.000 | 113.000 | 62.000 | `mushroom_v28_probability_reduce` | 0.555 |
| `lead_approved_only` | `KXBTC15M-26MAY061030-30` | `approved_entry` | `yes` | True | -18.000 | 42.000 | 60.000 | `mushroom_v28_probability_reduce` | 0.034 |
| `lead_approved_only` | `KXBTC15M-26MAY061045-45` | `approved_entry` | `yes` | True | -8.000 | 38.000 | 46.000 | `mushroom_v28_probability_reduce` | 0.033 |
| `lead_approved_only` | `KXBTC15M-26MAY071015-15` | `approved_entry` | `no` | False | 0.000 | -158.000 | -158.000 | `mushroom_v28_probability_reduce` | 0.122 |
| `lead_approved_only` | `KXBTC15M-26MAY071045-45` | `approved_entry` | `no` | True | -12.000 | 50.000 | 62.000 | `mushroom_v28_probability_reduce` | 0.114 |
