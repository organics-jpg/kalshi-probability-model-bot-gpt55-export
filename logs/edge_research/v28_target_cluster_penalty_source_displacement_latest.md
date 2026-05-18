# v28 Target Cluster-Penalty Source Displacement

Research-only; no live bot changes or orders.

- Generated UTC: `2026-05-11T01:10:29.700768+00:00`

## Interpretation

- This audit is diagnostic only; source labels are not deployable live features.
- diagnostic_target_window: selected rejected rows net -499.0c over 82 settled, omitted approved rows net 275.0c over 24 settled, approved-preferred net 767.0c.
- post_cluster_penalty_birth: selected rejected rows net -101.0c over 41 settled, omitted approved rows net 94.0c over 11 settled, approved-preferred net 367.0c.

## diagnostic_target_window

- Best variant: `cluster_penalty_heavy`

| group | rows | settled | W/L | net c | avg adjusted edge | avg raw edge | avg ask | avg abs d | avg recross | avg stc |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `selected_all` | 114 | 114 | 47/67 | 30.000000 | 0.221572 | 0.224089 | 0.383333 | 0.579337 | 0.363005 | 470.203140 |
| `selected_approved` | 32 | 32 | 28/4 | 529.000000 | 0.195390 | 0.195390 | 0.686250 | 1.087680 | 0.300100 | 560.908063 |
| `selected_rejected` | 82 | 82 | 19/63 | -499.000000 | 0.231789 | 0.235288 | 0.265122 | 0.380960 | 0.387554 | 434.806098 |
| `omitted_approved` | 24 | 24 | 23/1 | 275.000000 | 0.064749 | 0.064749 | 0.823333 | 1.046064 | 0.321950 | 617.670833 |
| `approved_preferred` | 114 | 114 | 87/27 | 767.000000 | 0.165404 | 0.166130 | 0.674035 | 0.951827 | 0.286381 | 517.697500 |

## post_cluster_penalty_birth

- Best variant: `cluster_penalty_heavy`

| group | rows | settled | W/L | net c | avg adjusted edge | avg raw edge | avg ask | avg abs d | avg recross | avg stc |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `selected_all` | 50 | 50 | 18/32 | 60.000000 | 0.264312 | 0.265743 | 0.321800 | 0.447196 | 0.402988 | 494.434640 |
| `selected_approved` | 9 | 9 | 8/1 | 161.000000 | 0.203272 | 0.203272 | 0.688889 | 1.076514 | 0.268492 | 552.986333 |
| `selected_rejected` | 41 | 41 | 10/31 | -101.000000 | 0.277711 | 0.279456 | 0.241220 | 0.309053 | 0.432512 | 481.581829 |
| `omitted_approved` | 11 | 11 | 10/1 | 94.000000 | 0.075632 | 0.075632 | 0.800000 | 0.975129 | 0.358438 | 621.055818 |
| `approved_preferred` | 50 | 50 | 37/13 | 367.000000 | 0.186071 | 0.186430 | 0.644800 | 0.899285 | 0.296052 | 530.776560 |
