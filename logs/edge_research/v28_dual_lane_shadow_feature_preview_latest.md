# v28 Dual-Lane Shadow Feature Preview

Research-only. No live bot logic changes, no orders.

- Generated UTC: `2026-05-11T03:46:15.775179+00:00`
- Freeze UTC: `2026-05-07T13:00:17.363339+00:00`
- Freeze local time: `2026-05-07T09:00:17.363339-04:00`
- Live baseline: `-256c ($-2.56)`
- Post-freeze observations: `977`
- Post-freeze distinct markets: `18`
- Scope: Non-promotional preview over post-freeze shadow approved and rejected-actionable observations. Own-freeze strict scorer remains authoritative for live readiness.

## Interpretation

- This preview is useful for collection and feature-availability debugging only.
- A good preview row does not count as a live-readiness row until the heavy own-freeze scorer confirms it.
- If feature availability is high but own-freeze rows remain zero after the 30-window mark, the bottleneck is the scorer/surface replay path rather than shadow collection.
- The primary pocket preview is a risk proxy only; it does not reproduce the parent-fill composer.

## Feature Availability

| feature | rows present |
|---|---:|
| `raw_edge` | 977 |
| `recross_hazard_score` | 977 |
| `abs_d_sigma` | 977 |
| `ask_prob` | 977 |

## Preview Summaries

| preview | entries | settled | W/L | coverage | net | recon | cushion | source counts |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| sidecar exact observable rule | 12 | 12 | 11/1 | 66.67% | 304c ($3.04) | 0.00% | 3 | `{'approved_entry': 12}` |
| primary sizing-pocket risk proxy | 16 | 16 | 4/12 | 88.89% | -40c ($-0.40) | 100.00% | 0 | `{'rejected_actionable': 16}` |

## Realized PnL Sign

| preview | PnL wins | PnL losses | flats | note |
|---|---:|---:|---:|---|
| sidecar exact observable rule | 10 | 2 | 0 | settlement W/L can differ from realized exit PnL |
| primary sizing-pocket risk proxy | 4 | 12 | 0 | risk proxy only, not actual parent-fill selection |

## Primary Proxy Caution

- This is only the observable sizing-pocket proxy. The actual primary lane is selected by the parent-fill composer before this pocket can shrink size.
- Current proxy negative-raw-edge rows: `11`
- Current proxy sidecar-ineligible rows: `16`

## Sidecar Missing Counts

| reason | count |
|---|---:|
| `abs_d_lt_085` | 623 |
| `raw_edge_lt_05` | 936 |
| `recross_gt_60` | 360 |

## Recent Sidecar Preview Rows

| market | source | side | won | net | raw edge | adjusted | recross | abs d | ask | missing |
|---|---|---|---|---:|---:|---:|---:|---:|---:|---|
| `KXBTC15M-26MAY070915-15` | approved_entry | no | True | 46c ($0.46) | 0.092 | 0.092 | 0.284 | 0.951 | 0.770 | none |
| `KXBTC15M-26MAY070945-45` | approved_entry | no | True | 62c ($0.62) | 0.149 | 0.149 | 0.436 | 0.883 | 0.690 | none |
| `KXBTC15M-26MAY071000-00` | approved_entry | no | True | 16c ($0.16) | 0.127 | 0.127 | 0.484 | 0.895 | 0.710 | none |
| `KXBTC15M-26MAY071015-15` | approved_entry | no | False | 2c ($0.02) | 0.066 | 0.066 | 0.418 | 0.936 | 0.780 | none |
| `KXBTC15M-26MAY071030-30` | approved_entry | no | True | 48c ($0.48) | 0.077 | 0.077 | 0.572 | 0.891 | 0.760 | none |
| `KXBTC15M-26MAY071045-45` | approved_entry | no | True | -10c ($-0.10) | 0.101 | 0.101 | 0.537 | 0.917 | 0.740 | none |
| `KXBTC15M-26MAY071130-30` | approved_entry | no | True | 30c ($0.30) | 0.057 | 0.057 | 0.332 | 1.183 | 0.850 | none |
| `KXBTC15M-26MAY071145-45` | approved_entry | yes | True | 44c ($0.44) | 0.070 | 0.070 | 0.585 | 0.878 | 0.770 | none |
| `KXBTC15M-26MAY071200-00` | approved_entry | no | True | 42c ($0.42) | 0.074 | 0.074 | 0.090 | 0.919 | 0.770 | none |
| `KXBTC15M-26MAY071215-15` | approved_entry | no | True | 2c ($0.02) | 0.056 | 0.056 | 0.262 | 0.888 | 0.780 | none |
| `KXBTC15M-26MAY071230-30` | approved_entry | yes | True | -10c ($-0.10) | 0.067 | 0.067 | 0.296 | 0.882 | 0.770 | none |
| `KXBTC15M-26MAY071315-15` | approved_entry | yes | True | 32c ($0.32) | 0.056 | 0.056 | 0.132 | 0.850 | 0.780 | none |
