# v28 Danger-Zone Robustness Audit

- Surface: `actual_v28_approved_entries_only`
- Rows/markets: `173/107`
- Entry robustness pass: `True`
- FV robustness pass: `True`

## Current Read

- Full entry valve delta is 322.0c; leave-one-market entry failures: 0.
- Full danger-to-book FV Brier/logloss deltas are -0.011340997078595372/-0.0661185329043299; leave-one-market FV failures: 0.
- If entry robustness fails, treat the entry valve as a watched hypothesis, not a promotion candidate.

## Full Sample

- Entry control/candidate/delta: `823.000000c/1145.000000c/322.000000c`
- FV rows/danger rows: `173/12`
- FV Brier/logloss delta: `-0.011341/-0.066119`

## Worst Leave-One-Market Rows

| removed market | removed rows | removed danger | removed danger gross c | entry delta c | fv d brier | fv d logloss |
|---|---:|---:|---:|---:|---:|---:|
| `KXBTC15M-26MAY062015-15` | 3 | 2 | -194.000000 | 128.000000 | -0.011450 | -0.065345 |
| `KXBTC15M-26MAY051715-15` | 3 | 2 | -70.000000 | 252.000000 | -0.006282 | -0.052735 |
| `KXBTC15M-26MAY060800-00` | 2 | 1 | -32.000000 | 290.000000 | -0.012057 | -0.068536 |
| `KXBTC15M-26MAY060945-45` | 4 | 2 | -28.000000 | 294.000000 | -0.012393 | -0.069976 |
| `KXBTC15M-26MAY052245-45` | 1 | 1 | -26.000000 | 296.000000 | -0.007452 | -0.055029 |
| `KXBTC15M-26MAY060330-30` | 2 | 1 | -18.000000 | 304.000000 | -0.005676 | -0.017976 |
| `KXBTC15M-26MAY051300-00` | 1 | 0 | 0 | 322.000000 | -0.011407 | -0.066503 |
| `KXBTC15M-26MAY051330-30` | 1 | 0 | 0 | 322.000000 | -0.011407 | -0.066503 |
| `KXBTC15M-26MAY051545-45` | 1 | 0 | 0 | 322.000000 | -0.011407 | -0.066503 |
| `KXBTC15M-26MAY051745-45` | 2 | 0 | 0 | 322.000000 | -0.011474 | -0.066892 |
