# v28 Target-Coverage Source-Split FV

- Policy: `raw_p50_turbulence_valve_edge4_p60_recross75_near25`
- Entries/settled/denominator: `112/112/152`

## Current Read

- all best is logit125_p75 over 112 rows with Brier/logloss deltas -0.0015769093300218757/-0.00675303480588537.
- approved_entry best is logit125_p70 over 7 rows with Brier/logloss deltas -0.005753117335864851/-0.03925202238843982.
- rejected_actionable best is logit125_p75 over 105 rows with Brier/logloss deltas -0.0012984954629656775/-0.004586435633715074.

## Groups

### all

| variant | rows | W/L | net c | brier mean | brier -/+ | logloss mean | logloss -/+ |
|---|---:|---:|---:|---:|---:|---:|---:|
| `logit125_p75` | 112 | 64/48 | -626.000000 | -0.001577 | 20/1 | -0.006753 | 20/1 |
| `logit125_p70` | 112 | 64/48 | -626.000000 | -0.000377 | 26/5 | -0.003572 | 26/5 |
| `raw_probability` | 112 | 64/48 | -626.000000 | 0.000000 | 0/0 | 0.000000 | 0/0 |

### approved_entry

| variant | rows | W/L | net c | brier mean | brier -/+ | logloss mean | logloss -/+ |
|---|---:|---:|---:|---:|---:|---:|---:|
| `logit125_p70` | 7 | 7/0 | 63.000000 | -0.005753 | 7/0 | -0.039252 | 7/0 |
| `logit125_p75` | 7 | 7/0 | 63.000000 | -0.005753 | 7/0 | -0.039252 | 7/0 |
| `raw_probability` | 7 | 7/0 | 63.000000 | 0.000000 | 0/0 | 0.000000 | 0/0 |

### rejected_actionable

| variant | rows | W/L | net c | brier mean | brier -/+ | logloss mean | logloss -/+ |
|---|---:|---:|---:|---:|---:|---:|---:|
| `logit125_p75` | 105 | 57/48 | -689.000000 | -0.001298 | 13/1 | -0.004586 | 13/1 |
| `logit125_p70` | 105 | 57/48 | -689.000000 | -0.000019 | 19/5 | -0.001193 | 19/5 |
| `raw_probability` | 105 | 57/48 | -689.000000 | 0.000000 | 0/0 | 0.000000 | 0/0 |

