# v28 Edge-Gate Opposite-Side Diagnostic

Research-only check: can an adjusted-FV skip become a coherent opposite-side trade instead of lost coverage?

- Policy: `raw_p50_turbulence_valve_edge4_p60_recross75_near25`
- Variant: `edge_phase_shrink`
- Adjusted edge floor: `-0.12`
- Target entries/skips/denominator: `112/1/152`
- Skips with opposite replacement: `1`
- Blockers: `coverage_too_low, net_not_positive`

## Interpretation

- 1 of 1 edge-gate skips had a same-or-later opposite-side replacement under the fixed physics requirements.
- Replacement-only net is 41.0c over 1 settled rows.
- Kept-plus-replacement coverage is 73.6842105263158 with net -424.0c.
- Still not promotable: coverage_too_low, net_not_positive.

## Summaries

| slice | entries | settled | W/L | coverage | net c | avg net c |
|---|---:|---:|---:|---:|---:|---:|
| kept_after_edge_gate | 111 | 111 | 64/47 | 73.026316 | -465.000000 | -4.189189 |
| replacement_only | 1 | 1 | 1/0 | 0.657895 | 41.000000 | 41.000000 |
| kept_plus_replacement | 112 | 112 | 65/47 | 73.684211 | -424.000000 | -3.785714 |

## Cases

| market | skipped side | skipped adj edge | opposite side | opposite raw edge | opposite adj edge | opposite won | opposite net c |
|---|---|---:|---|---:|---:|---|---:|
| KXBTC15M-26MAY060100-00 | yes | -0.140036 | no | 0.012335 | 0.012335 | True | 41.000000 |
