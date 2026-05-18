# v28 Target Cluster-Penalty Source Feasibility

Research-only; no live bot changes or orders.

- Generated UTC: `2026-05-11T01:08:22.815476+00:00`

## Interpretation

- This audit checks source feasibility only; it does not change the frozen cluster-penalty rule.
- diagnostic_target_window: selected reconstructed share 0.7192982456140351, approved available 95/114 required entries, minimum reconstructed share 0.16666666666666666, source feasible True.
- post_cluster_penalty_birth: selected reconstructed share 0.82, approved available 39/50 required entries, minimum reconstructed share 0.22, source feasible True.

## diagnostic_target_window

| variant | required | approved available | selected | selected recon | min recon share | feasible | selected net c | approved-preferred net c |
|---|---:|---:|---:|---:|---:|---|---:|---:|
| `cluster_penalty_heavy` | 114 | 95 | 114 | 0.719298 | 0.166667 | True | 30.000000 | 767.000000 |
| `cluster_penalty_medium` | 114 | 95 | 114 | 0.728070 | 0.166667 | True | 14.000000 | 767.000000 |
| `cluster_penalty_light` | 114 | 95 | 114 | 0.736842 | 0.166667 | True | -5.000000 | 767.000000 |

## post_cluster_penalty_birth

| variant | required | approved available | selected | selected recon | min recon share | feasible | selected net c | approved-preferred net c |
|---|---:|---:|---:|---:|---:|---|---:|---:|
| `cluster_penalty_heavy` | 50 | 39 | 50 | 0.820000 | 0.220000 | True | 60.000000 | 367.000000 |
| `cluster_penalty_light` | 50 | 39 | 50 | 0.840000 | 0.220000 | True | 27.000000 | 367.000000 |
| `cluster_penalty_medium` | 50 | 39 | 50 | 0.840000 | 0.220000 | True | 27.000000 | 367.000000 |
