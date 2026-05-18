# v28 FV Bridge Direction vs Realized PnL

Research-only; no live bot changes and no orders.

## Current Read

- diagnostic_existing_false_conviction_freeze: approved-only directional 62/70, realized 321.0c, hold 705.0c, exit-vs-hold -384.0c.
- post_freeze_candidate: approved-only directional 46/51, realized 241.0c, hold 552.0c, exit-vs-hold -311.0c.

## diagnostic_existing_false_conviction_freeze

| scenario | settled | directional W/L | dir win rate | realized c | hold c | exit-vs-hold c | negative realized winners |
|---|---:|---:|---:|---:|---:|---:|---:|
| `lead_reconstructed_only` | 91 | 56/35 | 0.615 | -511.000 | -91.000 | -420.000 | 0 |
| `lead_all_sources` | 91 | 60/31 | 0.659 | -407.000 | 113.000 | -520.000 | 2 |
| `lead_first_market_only` | 91 | 60/31 | 0.659 | -407.000 | 113.000 | -520.000 | 2 |
| `lead_approved_preferred` | 91 | 60/31 | 0.659 | -407.000 | 113.000 | -520.000 | 2 |
| `lead_approved_only` | 70 | 62/8 | 0.886 | 321.000 | 705.000 | -384.000 | 24 |

### Worst Exit Drag Rows

| scenario | market | source | side | side won | ask | realized c | hold c | exit-vs-hold c |
|---|---|---|---|---:|---:|---:|---:|---:|
| `lead_reconstructed_only` | `KXBTC15M-26MAY061215-15` | `rejected_actionable` | `no` | False | 0.830 | -168.000 | -83.000 | -85.000 |
| `lead_reconstructed_only` | `KXBTC15M-26MAY060700-00` | `rejected_actionable` | `no` | False | 0.810 | -165.000 | -81.000 | -84.000 |
| `lead_reconstructed_only` | `KXBTC15M-26MAY071230-30` | `rejected_actionable` | `no` | False | 0.790 | -161.000 | -79.000 | -82.000 |
| `lead_reconstructed_only` | `KXBTC15M-26MAY070045-45` | `rejected_actionable` | `yes` | False | 0.780 | -159.000 | -78.000 | -81.000 |
| `lead_reconstructed_only` | `KXBTC15M-26MAY060900-00` | `rejected_actionable` | `yes` | False | 0.770 | -157.000 | -77.000 | -80.000 |
| `lead_reconstructed_only` | `KXBTC15M-26MAY071100-00` | `rejected_actionable` | `yes` | False | 0.770 | -157.000 | -77.000 | -80.000 |
| `lead_reconstructed_only` | `KXBTC15M-26MAY071300-00` | `rejected_actionable` | `yes` | False | 0.740 | -151.000 | -74.000 | -77.000 |
| `lead_reconstructed_only` | `KXBTC15M-26MAY071015-15` | `rejected_actionable` | `no` | False | 0.730 | -149.000 | -73.000 | -76.000 |
| `lead_all_sources` | `KXBTC15M-26MAY061800-00` | `approved_entry` | `no` | True | 0.670 | -91.000 | 33.000 | -124.000 |
| `lead_all_sources` | `KXBTC15M-26MAY061215-15` | `rejected_actionable` | `no` | False | 0.830 | -168.000 | -83.000 | -85.000 |
| `lead_all_sources` | `KXBTC15M-26MAY060700-00` | `rejected_actionable` | `no` | False | 0.810 | -165.000 | -81.000 | -84.000 |
| `lead_all_sources` | `KXBTC15M-26MAY071230-30` | `rejected_actionable` | `no` | False | 0.790 | -161.000 | -79.000 | -82.000 |
| `lead_all_sources` | `KXBTC15M-26MAY070045-45` | `rejected_actionable` | `yes` | False | 0.780 | -159.000 | -78.000 | -81.000 |
| `lead_all_sources` | `KXBTC15M-26MAY060900-00` | `rejected_actionable` | `yes` | False | 0.770 | -157.000 | -77.000 | -80.000 |
| `lead_all_sources` | `KXBTC15M-26MAY071100-00` | `rejected_actionable` | `yes` | False | 0.770 | -157.000 | -77.000 | -80.000 |
| `lead_all_sources` | `KXBTC15M-26MAY071300-00` | `rejected_actionable` | `yes` | False | 0.740 | -151.000 | -74.000 | -77.000 |
| `lead_first_market_only` | `KXBTC15M-26MAY061800-00` | `approved_entry` | `no` | True | 0.670 | -91.000 | 33.000 | -124.000 |
| `lead_first_market_only` | `KXBTC15M-26MAY061215-15` | `rejected_actionable` | `no` | False | 0.830 | -168.000 | -83.000 | -85.000 |
| `lead_first_market_only` | `KXBTC15M-26MAY060700-00` | `rejected_actionable` | `no` | False | 0.810 | -165.000 | -81.000 | -84.000 |
| `lead_first_market_only` | `KXBTC15M-26MAY071230-30` | `rejected_actionable` | `no` | False | 0.790 | -161.000 | -79.000 | -82.000 |
| `lead_first_market_only` | `KXBTC15M-26MAY070045-45` | `rejected_actionable` | `yes` | False | 0.780 | -159.000 | -78.000 | -81.000 |
| `lead_first_market_only` | `KXBTC15M-26MAY060900-00` | `rejected_actionable` | `yes` | False | 0.770 | -157.000 | -77.000 | -80.000 |
| `lead_first_market_only` | `KXBTC15M-26MAY071100-00` | `rejected_actionable` | `yes` | False | 0.770 | -157.000 | -77.000 | -80.000 |
| `lead_first_market_only` | `KXBTC15M-26MAY071300-00` | `rejected_actionable` | `yes` | False | 0.740 | -151.000 | -74.000 | -77.000 |
| `lead_approved_preferred` | `KXBTC15M-26MAY061800-00` | `approved_entry` | `no` | True | 0.670 | -91.000 | 33.000 | -124.000 |
| `lead_approved_preferred` | `KXBTC15M-26MAY061215-15` | `rejected_actionable` | `no` | False | 0.830 | -168.000 | -83.000 | -85.000 |
| `lead_approved_preferred` | `KXBTC15M-26MAY060700-00` | `rejected_actionable` | `no` | False | 0.810 | -165.000 | -81.000 | -84.000 |
| `lead_approved_preferred` | `KXBTC15M-26MAY071230-30` | `rejected_actionable` | `no` | False | 0.790 | -161.000 | -79.000 | -82.000 |
| `lead_approved_preferred` | `KXBTC15M-26MAY070045-45` | `rejected_actionable` | `yes` | False | 0.780 | -159.000 | -78.000 | -81.000 |
| `lead_approved_preferred` | `KXBTC15M-26MAY060900-00` | `rejected_actionable` | `yes` | False | 0.770 | -157.000 | -77.000 | -80.000 |
| `lead_approved_preferred` | `KXBTC15M-26MAY071100-00` | `rejected_actionable` | `yes` | False | 0.770 | -157.000 | -77.000 | -80.000 |
| `lead_approved_preferred` | `KXBTC15M-26MAY071300-00` | `rejected_actionable` | `yes` | False | 0.740 | -151.000 | -74.000 | -77.000 |
| `lead_approved_only` | `KXBTC15M-26MAY061800-00` | `approved_entry` | `no` | True | 0.670 | -91.000 | 33.000 | -124.000 |
| `lead_approved_only` | `KXBTC15M-26MAY062015-15` | `approved_entry` | `no` | True | 0.420 | -62.000 | 58.000 | -120.000 |
| `lead_approved_only` | `KXBTC15M-26MAY071000-00` | `approved_entry` | `no` | True | 0.730 | -38.000 | 27.000 | -65.000 |
| `lead_approved_only` | `KXBTC15M-26MAY060945-45` | `approved_entry` | `no` | True | 0.590 | -18.000 | 41.000 | -59.000 |
| `lead_approved_only` | `KXBTC15M-26MAY061100-00` | `approved_entry` | `no` | True | 0.830 | -42.000 | 17.000 | -59.000 |
| `lead_approved_only` | `KXBTC15M-26MAY060615-15` | `approved_entry` | `yes` | True | 0.750 | -32.000 | 25.000 | -57.000 |
| `lead_approved_only` | `KXBTC15M-26MAY071030-30` | `approved_entry` | `no` | True | 0.770 | -26.000 | 23.000 | -49.000 |
| `lead_approved_only` | `KXBTC15M-26MAY060930-30` | `approved_entry` | `no` | True | 0.760 | -22.000 | 24.000 | -46.000 |

## post_freeze_candidate

| scenario | settled | directional W/L | dir win rate | realized c | hold c | exit-vs-hold c | negative realized winners |
|---|---:|---:|---:|---:|---:|---:|---:|
| `lead_all_sources` | 75 | 47/28 | 0.627 | -765.000 | -93.000 | -672.000 | 2 |
| `lead_first_market_only` | 75 | 47/28 | 0.627 | -765.000 | -93.000 | -672.000 | 2 |
| `lead_approved_preferred` | 75 | 47/28 | 0.627 | -765.000 | -93.000 | -672.000 | 2 |
| `lead_reconstructed_only` | 75 | 44/31 | 0.587 | -545.000 | -135.000 | -410.000 | 0 |
| `lead_approved_only` | 51 | 46/5 | 0.902 | 241.000 | 552.000 | -311.000 | 16 |

### Worst Exit Drag Rows

| scenario | market | source | side | side won | ask | realized c | hold c | exit-vs-hold c |
|---|---|---|---|---:|---:|---:|---:|---:|
| `lead_all_sources` | `KXBTC15M-26MAY061800-00` | `approved_entry` | `no` | True | 0.670 | -91.000 | 33.000 | -124.000 |
| `lead_all_sources` | `KXBTC15M-26MAY061215-15` | `rejected_actionable` | `no` | False | 0.830 | -168.000 | -83.000 | -85.000 |
| `lead_all_sources` | `KXBTC15M-26MAY071230-30` | `rejected_actionable` | `no` | False | 0.790 | -161.000 | -79.000 | -82.000 |
| `lead_all_sources` | `KXBTC15M-26MAY070045-45` | `rejected_actionable` | `yes` | False | 0.780 | -159.000 | -78.000 | -81.000 |
| `lead_all_sources` | `KXBTC15M-26MAY071100-00` | `rejected_actionable` | `yes` | False | 0.770 | -157.000 | -77.000 | -80.000 |
| `lead_all_sources` | `KXBTC15M-26MAY071300-00` | `rejected_actionable` | `yes` | False | 0.740 | -151.000 | -74.000 | -77.000 |
| `lead_all_sources` | `KXBTC15M-26MAY071015-15` | `rejected_actionable` | `no` | False | 0.730 | -149.000 | -73.000 | -76.000 |
| `lead_all_sources` | `KXBTC15M-26MAY071115-15` | `rejected_actionable` | `no` | False | 0.710 | -145.000 | -71.000 | -74.000 |
| `lead_first_market_only` | `KXBTC15M-26MAY061800-00` | `approved_entry` | `no` | True | 0.670 | -91.000 | 33.000 | -124.000 |
| `lead_first_market_only` | `KXBTC15M-26MAY061215-15` | `rejected_actionable` | `no` | False | 0.830 | -168.000 | -83.000 | -85.000 |
| `lead_first_market_only` | `KXBTC15M-26MAY071230-30` | `rejected_actionable` | `no` | False | 0.790 | -161.000 | -79.000 | -82.000 |
| `lead_first_market_only` | `KXBTC15M-26MAY070045-45` | `rejected_actionable` | `yes` | False | 0.780 | -159.000 | -78.000 | -81.000 |
| `lead_first_market_only` | `KXBTC15M-26MAY071100-00` | `rejected_actionable` | `yes` | False | 0.770 | -157.000 | -77.000 | -80.000 |
| `lead_first_market_only` | `KXBTC15M-26MAY071300-00` | `rejected_actionable` | `yes` | False | 0.740 | -151.000 | -74.000 | -77.000 |
| `lead_first_market_only` | `KXBTC15M-26MAY071015-15` | `rejected_actionable` | `no` | False | 0.730 | -149.000 | -73.000 | -76.000 |
| `lead_first_market_only` | `KXBTC15M-26MAY071115-15` | `rejected_actionable` | `no` | False | 0.710 | -145.000 | -71.000 | -74.000 |
| `lead_approved_preferred` | `KXBTC15M-26MAY061800-00` | `approved_entry` | `no` | True | 0.670 | -91.000 | 33.000 | -124.000 |
| `lead_approved_preferred` | `KXBTC15M-26MAY061215-15` | `rejected_actionable` | `no` | False | 0.830 | -168.000 | -83.000 | -85.000 |
| `lead_approved_preferred` | `KXBTC15M-26MAY071230-30` | `rejected_actionable` | `no` | False | 0.790 | -161.000 | -79.000 | -82.000 |
| `lead_approved_preferred` | `KXBTC15M-26MAY070045-45` | `rejected_actionable` | `yes` | False | 0.780 | -159.000 | -78.000 | -81.000 |
| `lead_approved_preferred` | `KXBTC15M-26MAY071100-00` | `rejected_actionable` | `yes` | False | 0.770 | -157.000 | -77.000 | -80.000 |
| `lead_approved_preferred` | `KXBTC15M-26MAY071300-00` | `rejected_actionable` | `yes` | False | 0.740 | -151.000 | -74.000 | -77.000 |
| `lead_approved_preferred` | `KXBTC15M-26MAY071015-15` | `rejected_actionable` | `no` | False | 0.730 | -149.000 | -73.000 | -76.000 |
| `lead_approved_preferred` | `KXBTC15M-26MAY071115-15` | `rejected_actionable` | `no` | False | 0.710 | -145.000 | -71.000 | -74.000 |
| `lead_reconstructed_only` | `KXBTC15M-26MAY061215-15` | `rejected_actionable` | `no` | False | 0.830 | -168.000 | -83.000 | -85.000 |
| `lead_reconstructed_only` | `KXBTC15M-26MAY071230-30` | `rejected_actionable` | `no` | False | 0.790 | -161.000 | -79.000 | -82.000 |
| `lead_reconstructed_only` | `KXBTC15M-26MAY070045-45` | `rejected_actionable` | `yes` | False | 0.780 | -159.000 | -78.000 | -81.000 |
| `lead_reconstructed_only` | `KXBTC15M-26MAY071100-00` | `rejected_actionable` | `yes` | False | 0.770 | -157.000 | -77.000 | -80.000 |
| `lead_reconstructed_only` | `KXBTC15M-26MAY071300-00` | `rejected_actionable` | `yes` | False | 0.740 | -151.000 | -74.000 | -77.000 |
| `lead_reconstructed_only` | `KXBTC15M-26MAY071015-15` | `rejected_actionable` | `no` | False | 0.730 | -149.000 | -73.000 | -76.000 |
| `lead_reconstructed_only` | `KXBTC15M-26MAY071115-15` | `rejected_actionable` | `no` | False | 0.710 | -145.000 | -71.000 | -74.000 |
| `lead_reconstructed_only` | `KXBTC15M-26MAY061100-00` | `rejected_actionable` | `yes` | False | 0.700 | -143.000 | -70.000 | -73.000 |
| `lead_approved_only` | `KXBTC15M-26MAY061800-00` | `approved_entry` | `no` | True | 0.670 | -91.000 | 33.000 | -124.000 |
| `lead_approved_only` | `KXBTC15M-26MAY062015-15` | `approved_entry` | `no` | True | 0.420 | -62.000 | 58.000 | -120.000 |
| `lead_approved_only` | `KXBTC15M-26MAY071000-00` | `approved_entry` | `no` | True | 0.730 | -38.000 | 27.000 | -65.000 |
| `lead_approved_only` | `KXBTC15M-26MAY061100-00` | `approved_entry` | `no` | True | 0.830 | -42.000 | 17.000 | -59.000 |
| `lead_approved_only` | `KXBTC15M-26MAY071030-30` | `approved_entry` | `no` | True | 0.770 | -26.000 | 23.000 | -49.000 |
| `lead_approved_only` | `KXBTC15M-26MAY062115-15` | `approved_entry` | `yes` | True | 0.730 | -14.000 | 27.000 | -41.000 |
| `lead_approved_only` | `KXBTC15M-26MAY061030-30` | `approved_entry` | `yes` | True | 0.780 | -18.000 | 22.000 | -40.000 |
| `lead_approved_only` | `KXBTC15M-26MAY071045-45` | `approved_entry` | `no` | True | 0.740 | -12.000 | 26.000 | -38.000 |
