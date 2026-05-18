# v28 Side-Agreement Meta Candidate

Uses raw broad timing when p60 agrees on side; waits for p60 when side flips.

- Watched markets: `181`

## Summary

| policy | entries | settled | wins/losses | coverage | net c | avg net c | brier | same raw | flip wait | actual/shadow |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| raw_when_same_else_first_side_p60 | 172 | 172 | 101/71 | 95.027624 | -1906.000000 | -11.081395 | 0.227680 | 125 | 44 | 10/162 |
| raw_when_same_else_rmt_p60 | 172 | 172 | 104/68 | 95.027624 | -1541.000000 | -8.959302 | 0.222365 | 120 | 49 | 10/162 |

## Recent Rows

| meta | market | reason | side | p_eff | ask | edge | won | net c |
|---|---|---|---|---:|---:|---:|---|---:|
| raw_when_same_else_rmt_repetition_forget_p60_edge0 | KXBTC15M-26MAY070730-30 | same_side_use_raw | yes | 0.530778 | 0.460000 | 0.070778 | False | -96.000000 |
| raw_when_same_else_rmt_repetition_forget_p60_edge0 | KXBTC15M-26MAY070745-45 | same_side_use_raw | yes | 0.903807 | 0.680000 | 0.223807 | True | 32.000000 |
| raw_else_rmt_repetition_forget_p60_edge0_missing_wait | KXBTC15M-26MAY070800-00 | wait_missing_use_raw | yes | 0.536385 | 0.450000 | 0.086385 | False | -94.000000 |
| raw_when_same_else_rmt_repetition_forget_p60_edge0 | KXBTC15M-26MAY070815-15 | same_side_use_raw | yes | 0.501147 | 0.440000 | 0.061147 | True | 108.000000 |
| raw_when_same_else_rmt_repetition_forget_p60_edge0 | KXBTC15M-26MAY070830-30 | side_flip_use_wait | no | 0.660000 | 0.660000 | 0.000000 | True | 32.000000 |
| raw_when_same_else_rmt_repetition_forget_p60_edge0 | KXBTC15M-26MAY070845-45 | same_side_use_raw | yes | 0.596088 | 0.450000 | 0.146088 | True | 106.000000 |
| raw_when_same_else_rmt_repetition_forget_p60_edge0 | KXBTC15M-26MAY070900-00 | side_flip_use_wait | no | 0.600000 | 0.600000 | 0.000000 | False | -124.000000 |
| raw_when_same_else_rmt_repetition_forget_p60_edge0 | KXBTC15M-26MAY070915-15 | same_side_use_raw | no | 0.788001 | 0.750000 | 0.038001 | True | 47.000000 |
| raw_when_same_else_rmt_repetition_forget_p60_edge0 | KXBTC15M-26MAY070930-30 | same_side_use_raw | no | 0.511849 | 0.480000 | 0.031849 | False | -100.000000 |
| raw_when_same_else_rmt_repetition_forget_p60_edge0 | KXBTC15M-26MAY070945-45 | same_side_use_raw | no | 0.532085 | 0.480000 | 0.052085 | True | 100.000000 |
| raw_when_same_else_rmt_repetition_forget_p60_edge0 | KXBTC15M-26MAY071000-00 | side_flip_use_wait | no | 0.660000 | 0.660000 | 0.000000 | True | 64.000000 |
| raw_when_same_else_rmt_repetition_forget_p60_edge0 | KXBTC15M-26MAY071015-15 | same_side_use_raw | no | 0.609894 | 0.600000 | 0.009894 | False | -124.000000 |
| raw_when_same_else_rmt_repetition_forget_p60_edge0 | KXBTC15M-26MAY071030-30 | same_side_use_raw | no | 0.646380 | 0.620000 | 0.026380 | True | 72.000000 |
| raw_when_same_else_rmt_repetition_forget_p60_edge0 | KXBTC15M-26MAY071045-45 | side_flip_use_wait | no | 0.730000 | 0.730000 | 0.000000 | True | 51.000000 |
| raw_when_same_else_rmt_repetition_forget_p60_edge0 | KXBTC15M-26MAY071100-00 | side_flip_use_wait | yes | 0.650000 | 0.650000 | 0.000000 | False | -134.000000 |
| raw_when_same_else_rmt_repetition_forget_p60_edge0 | KXBTC15M-26MAY071115-15 | same_side_use_raw | no | 0.635838 | 0.620000 | 0.015838 | False | -128.000000 |
| raw_when_same_else_rmt_repetition_forget_p60_edge0 | KXBTC15M-26MAY071130-30 | side_flip_use_wait | yes | 0.600000 | 0.600000 | 0.000000 | False | -124.000000 |
| raw_when_same_else_rmt_repetition_forget_p60_edge0 | KXBTC15M-26MAY071145-45 | same_side_use_raw | yes | 0.645637 | 0.610000 | 0.035637 | True | 74.000000 |
| raw_when_same_else_rmt_repetition_forget_p60_edge0 | KXBTC15M-26MAY071200-00 | same_side_use_raw | yes | 0.606055 | 0.600000 | 0.006055 | False | -124.000000 |
| raw_when_same_else_rmt_repetition_forget_p60_edge0 | KXBTC15M-26MAY071215-15 | same_side_use_raw | yes | 0.509397 | 0.470000 | 0.039397 | False | -98.000000 |
| raw_when_same_else_rmt_repetition_forget_p60_edge0 | KXBTC15M-26MAY071230-30 | same_side_use_raw | no | 0.729882 | 0.700000 | 0.029882 | False | -143.000000 |
| raw_when_same_else_rmt_repetition_forget_p60_edge0 | KXBTC15M-26MAY071245-45 | same_side_use_raw | yes | 0.559979 | 0.550000 | 0.009979 | False | -114.000000 |
| raw_when_same_else_rmt_repetition_forget_p60_edge0 | KXBTC15M-26MAY071300-00 | same_side_use_raw | yes | 0.636040 | 0.590000 | 0.046040 | False | -122.000000 |
| raw_when_same_else_rmt_repetition_forget_p60_edge0 | KXBTC15M-26MAY071315-15 | same_side_use_raw | yes | 0.533442 | 0.510000 | 0.023442 | True | 94.000000 |
| raw_when_same_else_rmt_repetition_forget_p60_edge0 | KXBTC15M-26MAY071330-30 | side_flip_use_wait | no | 0.650000 | 0.650000 | 0.000000 | True | 66.000000 |
