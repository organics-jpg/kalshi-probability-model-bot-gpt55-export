# v28 Exit Unresolved State Separator

Research-only diagnostic; no live bot changes or orders.

- Generated UTC: `2026-05-07T05:46:03.112410+00:00`
- Scope: `matched_but_unchanged_loss_rows_only`
- Rows: `31`
- Hold helpful/harmful: `22/7`
- Actual loss selected universe: `-984c`
- Hindsight hold delta in universe: `940c`
- Post first repair-freeze rows: `31`

## Interpretation

- This is a diagnostic separator only; it is selected on known loss rows and cannot be promoted.
- A useful next step is to freeze one simple observable rule only if the physical mechanism is defensible.
- Any frozen rule must then earn post-freeze suppressions, positive delta, no harmful loss-control cost, and enough cushion.

## Failure Split

| failure class | rows | hold helpful | hold harmful | actual loss c | hold delta c |
|---|---:|---:|---:|---:|---:|
| exit_policy_cost | 22 | 22 | 0 | -564 | 1712 |
| fv_or_entry_timing_error | 9 | 0 | 7 | -420 | -772 |

## Best Clean Diagnostic Rule

| field | value |
|---|---:|
| rule | `fair_drawdown_cents le 5.1815` |
| selected rows | 10 |
| helpful/harmful | 10/0 |
| hold delta c | 736 |
| actual loss c | -164 |
| blockers | `diagnostic_not_frozen, no_post_freeze_evidence` |

## Best Rounded Clean Diagnostic Rule

| field | value |
|---|---:|
| rule | `fair_drawdown_cents le 5` |
| selected rows | 9 |
| helpful/harmful | 9/0 |
| hold delta c | 676 |
| actual loss c | -146 |
| blockers | `diagnostic_not_frozen, no_post_freeze_evidence` |

## Best Tradeoff Diagnostic Rule

| field | value |
|---|---:|
| rule | `fair_drawdown_cents le 5.1815` |
| selected rows | 10 |
| helpful/harmful | 10/0 |
| helpful share | 100.00% |
| hold delta c | 736 |
| actual loss c | -164 |
| blockers | `diagnostic_not_frozen, no_post_freeze_evidence` |

## Top Clean Diagnostic Rules

| rule | rows | helpful | harmful | hold delta c | actual loss c |
|---|---:|---:|---:|---:|---:|
| `fair_drawdown_cents le 5.1815` | 10 | 10 | 0 | 736 | -164 |
| `fair_drawdown_cents le 4.52972` | 9 | 9 | 0 | 676 | -146 |
| `fair_drawdown_cents le 5` | 9 | 9 | 0 | 676 | -146 |
| `ask_cents le 68` | 7 | 5 | 0 | 596 | -352 |
| `fair_drawdown_cents le 3.40537` | 8 | 8 | 0 | 576 | -114 |
| `recross_hazard_score ge 0.328333` | 7 | 7 | 0 | 534 | -154 |
| `ask_cents le 67` | 6 | 4 | 0 | 526 | -346 |
| `fair_drawdown_cents le 3.34439` | 7 | 7 | 0 | 508 | -94 |
| `recross_hazard_score ge 0.332556` | 6 | 6 | 0 | 454 | -124 |
| `fair_drawdown_cents le 2.06075` | 6 | 6 | 0 | 410 | -78 |

## Top Rounded Clean Diagnostic Rules

| rule | rows | helpful | harmful | hold delta c | actual loss c |
|---|---:|---:|---:|---:|---:|
| `fair_drawdown_cents le 5` | 9 | 9 | 0 | 676 | -146 |
| `ask_cents le 68` | 7 | 5 | 0 | 596 | -352 |
| `fair_drawdown_cents le 2.5` | 6 | 6 | 0 | 410 | -78 |
| `recross_hazard_score ge 0.4` | 4 | 4 | 0 | 310 | -82 |
| `ask_cents le 60` | 3 | 2 | 0 | 274 | -94 |
| `ask_cents le 65` | 3 | 2 | 0 | 274 | -94 |
| `fair_drawdown_cents le 5 and ask_cents le 68` | 3 | 3 | 0 | 268 | -54 |
| `fair_drawdown_cents le 5 and recross_hazard_score ge 0.4` | 3 | 3 | 0 | 236 | -42 |
| `exit_cents ge 70` | 5 | 5 | 0 | 234 | -58 |

## Feature Ranges

| feature | exit_policy_cost median | fv_or_entry_timing_error median |
|---|---:|---:|
| p_hold | 0.689 | 0.597 |
| fair_drawdown_cents | 9.552 | 13.357 |
| exit_cents | 65.000 | 57.000 |
| p_side | 0.867 | 0.861 |
| raw_edge_cents | 9.183 | 14.684 |
| ask_cents | 76.000 | 70.000 |
| abs_d_sigma | 0.916 | 0.913 |
| recross_hazard_score | 0.226 | 0.247 |
| eligible_depth | 269.860 | 111.000 |
