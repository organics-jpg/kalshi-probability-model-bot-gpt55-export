# v28 Frozen Thin-Recross Mid-P Entry Gate

- Freeze timestamp UTC: `2026-05-06T03:39:03.842700+00:00`
- Candidate: `skip_midp60_75_edge_lt2pp_recross_ge85`
- Future denominator: `135`

## Current Read

- Frozen thin-recross entry gate has 88 entries versus 97 base entries.
- It has skipped 9 future rows so far; promotion requires settled forward rows, not this setup snapshot.
- This is entry-policy evidence, separate from the conservative FV overlay.

## Summary

| row | entries | settled | W/L | coverage | net c | blockers |
|---|---:|---:|---:|---:|---:|---|
| base | 97 | 97 | 53/44 | 71.851852 | -769.000000 | coverage_too_low, net_not_positive |
| candidate | 88 | 88 | 50/38 | 65.185185 | -209.000000 | coverage_too_low, net_not_positive |

## Skipped Rows

| market | side | p raw | ask | edge | recross | won | net c | reason |
|---|---|---:|---:|---:|---:|---|---:|---|
| KXBTC15M-26MAY060830-30 | no | 0.600730 | 0.590000 | 0.010730 | 0.943700 | False | -122.000000 | skip_thin_midp_high_recross |
| KXBTC15M-26MAY060930-30 | yes | 0.604377 | 0.600000 | 0.004377 | 1.150583 | False | -124.000000 | skip_thin_midp_high_recross |
| KXBTC15M-26MAY061030-30 | yes | 0.618153 | 0.610000 | 0.008153 | 1.168280 | True | 74.000000 | skip_thin_midp_high_recross |
| KXBTC15M-26MAY061130-30 | yes | 0.653101 | 0.650000 | 0.003101 | 1.056221 | True | 66.000000 | skip_thin_midp_high_recross |
| KXBTC15M-26MAY061230-30 | yes | 0.681329 | 0.680000 | 0.001329 | 0.862457 | False | -140.000000 | skip_thin_midp_high_recross |
| KXBTC15M-26MAY061430-30 | yes | 0.678512 | 0.670000 | 0.008512 | 0.893555 | True | 62.000000 | skip_thin_midp_high_recross |
| KXBTC15M-26MAY071015-15 | no | 0.609894 | 0.600000 | 0.009894 | 1.102864 | False | -124.000000 | skip_thin_midp_high_recross |
| KXBTC15M-26MAY071115-15 | no | 0.635838 | 0.620000 | 0.015838 | 0.982771 | False | -128.000000 | skip_thin_midp_high_recross |
| KXBTC15M-26MAY071200-00 | yes | 0.606055 | 0.600000 | 0.006055 | 1.096302 | False | -124.000000 | skip_thin_midp_high_recross |
