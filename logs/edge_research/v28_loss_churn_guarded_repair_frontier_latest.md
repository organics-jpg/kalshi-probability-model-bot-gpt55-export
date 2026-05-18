# v28 Loss-Churn Guarded Repair Frontier

Research-only. No live bot logic changes, no orders.

- Generated UTC: `2026-05-07T16:46:45.232678+00:00`
- Promotion use: `diagnostic_loss_rows_only`
- Known loss rows / unresolved known rows: `71` / `54`
- Evaluated rules: `246`

## Read

- This is a diagnostic loss-row frontier, not a candidate or live exit rule.
- Rules are evaluated only on losing rows with known hold outcomes; any useful row needs full-denominator replay and its own freeze.
- Best clean diagnostic guard is not_fv_entry_timing with 34 loss flips, 34 selected loss rows, and 2426c ($24.26) hold delta.
- Best observable-only clean guard is recross_ge_045 with 4 loss flips, 4 selected loss rows, and 328c ($3.28) hold delta.
- Top risky rules still show false-hold exposure; worst selected examples should remain guardrail material.

## Clean Diagnostic Frontier

| rule | selected losses | flips | hold delta | helpful/harmful/unknown | blockers |
|---|---:|---:|---:|---:|---|
| `not_fv_entry_timing` | 34 | 34 | 2426c ($24.26) | 34/0/0 | diagnostic_loss_rows_only, not_frozen_forward, needs_full_denominator_replay |
| `not_fv_entry_timing__and__exit_cents_ge_50` | 32 | 32 | 2098c ($20.98) | 32/0/0 | diagnostic_loss_rows_only, not_frozen_forward, needs_full_denominator_replay |
| `not_fv_entry_timing__and__absd_ge_085` | 31 | 31 | 2238c ($22.38) | 31/0/0 | diagnostic_loss_rows_only, not_frozen_forward, needs_full_denominator_replay |
| `not_fv_entry_timing__and__ask_cents_ge_70` | 29 | 29 | 1830c ($18.30) | 29/0/0 | diagnostic_loss_rows_only, not_frozen_forward, needs_full_denominator_replay |
| `not_fv_entry_timing__and__exit_cents_ge_60` | 28 | 28 | 1716c ($17.16) | 28/0/0 | diagnostic_loss_rows_only, not_frozen_forward, needs_full_denominator_replay |
| `tag_near_boundary__and__not_fv_entry_timing` | 26 | 26 | 1856c ($18.56) | 26/0/0 | diagnostic_loss_rows_only, not_frozen_forward, needs_full_denominator_replay |
| `not_fv_entry_timing__and__not_medium_25_49` | 26 | 26 | 1794c ($17.94) | 26/0/0 | diagnostic_loss_rows_only, not_frozen_forward, needs_full_denominator_replay |
| `not_fv_entry_timing__and__depth_lte_384` | 22 | 22 | 1596c ($15.96) | 22/0/0 | diagnostic_loss_rows_only, not_frozen_forward, needs_full_denominator_replay |
| `not_fv_entry_timing__and__raw_edge_cents_le_10` | 22 | 22 | 1304c ($13.04) | 22/0/0 | diagnostic_loss_rows_only, not_frozen_forward, needs_full_denominator_replay |
| `not_fv_entry_timing__and__p_hold_ge_060` | 20 | 20 | 1346c ($13.46) | 20/0/0 | diagnostic_loss_rows_only, not_frozen_forward, needs_full_denominator_replay |
| `not_fv_entry_timing__and__depth_lte_150` | 17 | 17 | 1264c ($12.64) | 17/0/0 | diagnostic_loss_rows_only, not_frozen_forward, needs_full_denominator_replay |
| `tag_recross_high__and__not_fv_entry_timing` | 16 | 16 | 1164c ($11.64) | 16/0/0 | diagnostic_loss_rows_only, not_frozen_forward, needs_full_denominator_replay |
| `not_fv_entry_timing__and__recross_ge_030` | 14 | 14 | 960c ($9.60) | 14/0/0 | diagnostic_loss_rows_only, not_frozen_forward, needs_full_denominator_replay |
| `tag_rich_entry__and__not_fv_entry_timing` | 10 | 10 | 534c ($5.34) | 10/0/0 | diagnostic_loss_rows_only, not_frozen_forward, needs_full_denominator_replay |
| `not_fv_entry_timing__and__ask_cents_ge_80` | 10 | 10 | 534c ($5.34) | 10/0/0 | diagnostic_loss_rows_only, not_frozen_forward, needs_full_denominator_replay |
| `tag_thin_raw_edge__and__not_fv_entry_timing` | 8 | 8 | 448c ($4.48) | 8/0/0 | diagnostic_loss_rows_only, not_frozen_forward, needs_full_denominator_replay, selected_loss_rows_lt_10 |
| `not_fv_entry_timing__and__raw_edge_cents_ge_15` | 6 | 6 | 662c ($6.62) | 6/0/0 | diagnostic_loss_rows_only, not_frozen_forward, needs_full_denominator_replay, selected_loss_rows_lt_10 |
| `tag_crowded_depth__and__not_fv_entry_timing` | 6 | 6 | 402c ($4.02) | 6/0/0 | diagnostic_loss_rows_only, not_frozen_forward, needs_full_denominator_replay, selected_loss_rows_lt_10 |
| `tag_crowded_depth__and__not_medium_25_49` | 6 | 6 | 402c ($4.02) | 6/0/0 | diagnostic_loss_rows_only, not_frozen_forward, needs_full_denominator_replay, selected_loss_rows_lt_10 |
| `not_fv_entry_timing__and__p_hold_le_060` | 5 | 5 | 586c ($5.86) | 5/0/0 | diagnostic_loss_rows_only, not_frozen_forward, needs_full_denominator_replay, selected_loss_rows_lt_10 |

## Observable-Only Clean Frontier

| rule | selected losses | flips | hold delta | helpful/harmful/unknown | blockers |
|---|---:|---:|---:|---:|---|
| `recross_ge_045` | 4 | 4 | 328c ($3.28) | 4/0/0 | diagnostic_loss_rows_only, not_frozen_forward, needs_full_denominator_replay, selected_loss_rows_lt_10 |
| `tag_near_boundary__and__recross_ge_045` | 4 | 4 | 328c ($3.28) | 4/0/0 | diagnostic_loss_rows_only, not_frozen_forward, needs_full_denominator_replay, selected_loss_rows_lt_10 |
| `tag_recross_high__and__recross_ge_045` | 4 | 4 | 328c ($3.28) | 4/0/0 | diagnostic_loss_rows_only, not_frozen_forward, needs_full_denominator_replay, selected_loss_rows_lt_10 |
| `exit_cents_ge_50__and__recross_ge_045` | 4 | 4 | 328c ($3.28) | 4/0/0 | diagnostic_loss_rows_only, not_frozen_forward, needs_full_denominator_replay, selected_loss_rows_lt_10 |
| `recross_ge_030__and__recross_ge_045` | 4 | 4 | 328c ($3.28) | 4/0/0 | diagnostic_loss_rows_only, not_frozen_forward, needs_full_denominator_replay, selected_loss_rows_lt_10 |
| `recross_ge_045__and__absd_ge_085` | 4 | 4 | 328c ($3.28) | 4/0/0 | diagnostic_loss_rows_only, not_frozen_forward, needs_full_denominator_replay, selected_loss_rows_lt_10 |
| `tag_recross_high__and__raw_edge_cents_ge_15` | 3 | 3 | 320c ($3.20) | 3/0/0 | diagnostic_loss_rows_only, not_frozen_forward, needs_full_denominator_replay, selected_loss_rows_lt_10 |
| `p_hold_ge_060__and__recross_ge_045` | 3 | 3 | 230c ($2.30) | 3/0/0 | diagnostic_loss_rows_only, not_frozen_forward, needs_full_denominator_replay, selected_loss_rows_lt_10 |
| `recross_ge_045__and__depth_lte_384` | 3 | 3 | 230c ($2.30) | 3/0/0 | diagnostic_loss_rows_only, not_frozen_forward, needs_full_denominator_replay, selected_loss_rows_lt_10 |
| `tag_crowded_depth__and__p_hold_le_060` | 2 | 2 | 192c ($1.92) | 2/0/0 | diagnostic_loss_rows_only, not_frozen_forward, needs_full_denominator_replay, selected_loss_rows_lt_10, loss_flips_lt_3 |
| `p_hold_ge_060__and__raw_edge_cents_ge_15` | 2 | 2 | 170c ($1.70) | 2/0/0 | diagnostic_loss_rows_only, not_frozen_forward, needs_full_denominator_replay, selected_loss_rows_lt_10, loss_flips_lt_3 |
| `raw_edge_cents_ge_15__and__recross_ge_030` | 2 | 2 | 168c ($1.68) | 2/0/0 | diagnostic_loss_rows_only, not_frozen_forward, needs_full_denominator_replay, selected_loss_rows_lt_10, loss_flips_lt_3 |
| `raw_edge_cents_ge_15__and__recross_ge_045` | 2 | 2 | 168c ($1.68) | 2/0/0 | diagnostic_loss_rows_only, not_frozen_forward, needs_full_denominator_replay, selected_loss_rows_lt_10, loss_flips_lt_3 |
| `ask_cents_ge_70__and__recross_ge_045` | 2 | 2 | 160c ($1.60) | 2/0/0 | diagnostic_loss_rows_only, not_frozen_forward, needs_full_denominator_replay, selected_loss_rows_lt_10, loss_flips_lt_3 |
| `exit_cents_ge_60__and__recross_ge_045` | 2 | 2 | 140c ($1.40) | 2/0/0 | diagnostic_loss_rows_only, not_frozen_forward, needs_full_denominator_replay, selected_loss_rows_lt_10, loss_flips_lt_3 |
| `tag_crowded_depth__and__raw_edge_cents_ge_15` | 1 | 1 | 98c ($0.98) | 1/0/0 | diagnostic_loss_rows_only, not_frozen_forward, needs_full_denominator_replay, selected_loss_rows_lt_10, loss_flips_lt_3 |
| `tag_crowded_depth__and__recross_ge_045` | 1 | 1 | 98c ($0.98) | 1/0/0 | diagnostic_loss_rows_only, not_frozen_forward, needs_full_denominator_replay, selected_loss_rows_lt_10, loss_flips_lt_3 |
| `p_hold_le_060__and__recross_ge_030` | 1 | 1 | 98c ($0.98) | 1/0/0 | diagnostic_loss_rows_only, not_frozen_forward, needs_full_denominator_replay, selected_loss_rows_lt_10, loss_flips_lt_3 |
| `p_hold_le_060__and__recross_ge_045` | 1 | 1 | 98c ($0.98) | 1/0/0 | diagnostic_loss_rows_only, not_frozen_forward, needs_full_denominator_replay, selected_loss_rows_lt_10, loss_flips_lt_3 |
| `tag_thin_touch_depth__and__recross_ge_045` | 1 | 1 | 90c ($0.90) | 1/0/0 | diagnostic_loss_rows_only, not_frozen_forward, needs_full_denominator_replay, selected_loss_rows_lt_10, loss_flips_lt_3 |

## Risky High-Delta Frontier

| rule | selected losses | flips | hold delta | helpful/harmful/unknown | harmful delta | blockers |
|---|---:|---:|---:|---:|---:|---|
| `p_hold_ge_060` | 24 | 20 | 836c ($8.36) | 20/4/0 | -510c ($-5.10) | diagnostic_loss_rows_only, not_frozen_forward, needs_full_denominator_replay, hold_harmful_rows_present |
| `p_hold_ge_060__and__exit_cents_ge_50` | 24 | 20 | 836c ($8.36) | 20/4/0 | -510c ($-5.10) | diagnostic_loss_rows_only, not_frozen_forward, needs_full_denominator_replay, hold_harmful_rows_present |
| `p_hold_ge_060__and__ask_cents_ge_70` | 21 | 18 | 780c ($7.80) | 18/3/0 | -396c ($-3.96) | diagnostic_loss_rows_only, not_frozen_forward, needs_full_denominator_replay, hold_harmful_rows_present |
| `p_hold_ge_060__and__exit_cents_ge_60` | 21 | 18 | 760c ($7.60) | 18/3/0 | -396c ($-3.96) | diagnostic_loss_rows_only, not_frozen_forward, needs_full_denominator_replay, hold_harmful_rows_present |
| `p_hold_ge_060__and__absd_ge_085` | 22 | 18 | 700c ($7.00) | 18/4/0 | -510c ($-5.10) | diagnostic_loss_rows_only, not_frozen_forward, needs_full_denominator_replay, hold_harmful_rows_present |
| `not_medium_25_49` | 38 | 26 | 698c ($6.98) | 26/10/0 | -1096c ($-10.96) | diagnostic_loss_rows_only, not_frozen_forward, needs_full_denominator_replay, hold_harmful_rows_present |
| `not_medium_25_49__and__exit_cents_ge_50` | 30 | 24 | 662c ($6.62) | 24/6/0 | -804c ($-8.04) | diagnostic_loss_rows_only, not_frozen_forward, needs_full_denominator_replay, hold_harmful_rows_present |
| `tag_near_boundary__and__p_hold_ge_060` | 20 | 16 | 654c ($6.54) | 16/4/0 | -510c ($-5.10) | diagnostic_loss_rows_only, not_frozen_forward, needs_full_denominator_replay, hold_harmful_rows_present |
| `not_medium_25_49__and__absd_ge_085` | 34 | 23 | 590c ($5.90) | 23/9/0 | -1016c ($-10.16) | diagnostic_loss_rows_only, not_frozen_forward, needs_full_denominator_replay, hold_harmful_rows_present |
| `not_medium_25_49__and__exit_cents_ge_60` | 27 | 22 | 584c ($5.84) | 22/5/0 | -690c ($-6.90) | diagnostic_loss_rows_only, not_frozen_forward, needs_full_denominator_replay, hold_harmful_rows_present |
| `p_hold_ge_060__and__depth_lte_384` | 14 | 12 | 550c ($5.50) | 12/2/0 | -266c ($-2.66) | diagnostic_loss_rows_only, not_frozen_forward, needs_full_denominator_replay, hold_harmful_rows_present |
| `exit_cents_ge_50` | 44 | 32 | 536c ($5.36) | 32/12/0 | -1562c ($-15.62) | diagnostic_loss_rows_only, not_frozen_forward, needs_full_denominator_replay, hold_harmful_rows_present |
| `p_hold_ge_060__and__raw_edge_cents_le_10` | 15 | 13 | 534c ($5.34) | 13/2/0 | -276c ($-2.76) | diagnostic_loss_rows_only, not_frozen_forward, needs_full_denominator_replay, hold_harmful_rows_present |
| `not_medium_25_49__and__p_hold_ge_060` | 15 | 13 | 530c ($5.30) | 13/2/0 | -260c ($-2.60) | diagnostic_loss_rows_only, not_frozen_forward, needs_full_denominator_replay, hold_harmful_rows_present |
| `exit_cents_ge_50__and__ask_cents_ge_70` | 39 | 29 | 486c ($4.86) | 29/10/0 | -1344c ($-13.44) | diagnostic_loss_rows_only, not_frozen_forward, needs_full_denominator_replay, hold_harmful_rows_present |
| `not_medium_25_49__and__depth_lte_384` | 25 | 17 | 432c ($4.32) | 17/7/0 | -786c ($-7.86) | diagnostic_loss_rows_only, not_frozen_forward, needs_full_denominator_replay, hold_harmful_rows_present |
| `not_medium_25_49__and__ask_cents_ge_70` | 30 | 22 | 374c ($3.74) | 22/8/0 | -924c ($-9.24) | diagnostic_loss_rows_only, not_frozen_forward, needs_full_denominator_replay, hold_harmful_rows_present |
| `exit_cents_ge_60` | 38 | 28 | 372c ($3.72) | 28/10/0 | -1344c ($-13.44) | diagnostic_loss_rows_only, not_frozen_forward, needs_full_denominator_replay, hold_harmful_rows_present |
| `exit_cents_ge_60__and__exit_cents_ge_50` | 38 | 28 | 372c ($3.72) | 28/10/0 | -1344c ($-13.44) | diagnostic_loss_rows_only, not_frozen_forward, needs_full_denominator_replay, hold_harmful_rows_present |
| `not_medium_25_49__and__raw_edge_cents_ge_15` | 9 | 5 | 366c ($3.66) | 5/2/0 | -196c ($-1.96) | diagnostic_loss_rows_only, not_frozen_forward, needs_full_denominator_replay, hold_harmful_rows_present, selected_loss_rows_lt_10 |

## Best Clean Examples

| market | side | actual | hold | delta | failure | escape | tags |
|---|---|---:|---:|---:|---|---|---|
| `KXBTC15M-26MAY061400-00` | no | -10c ($-0.10) | 22c ($0.22) | 32c ($0.32) | `exit_policy_cost` | `loss_escapes_current_exit_repairs` | small_10_24c, exit_policy_cost, crowded_depth, exit_policy_clip_vs_hold, rich_entry |
| `KXBTC15M-26MAY062100-00` | yes | -4c ($-0.04) | 34c ($0.34) | 38c ($0.38) | `exit_policy_cost` | `loss_escapes_current_exit_repairs` | micro_lt_10c, exit_policy_cost, exit_policy_clip_vs_hold, rich_entry |
| `KXBTC15M-26MAY051745-45` | no | -2c ($-0.02) | 40c ($0.40) | 42c ($0.42) | `exit_policy_cost` | `no_exit_repair_observation` | micro_lt_10c, exit_policy_cost, recross_hazard_high, crowded_depth, exit_policy_clip_vs_hold, thin_raw_edge, rich_entry, near_boundary |
| `KXBTC15M-26MAY052215-15` | no | -14c ($-0.14) | 34c ($0.34) | 48c ($0.48) | `exit_policy_cost` | `no_exit_repair_observation` | small_10_24c, exit_policy_cost, recross_hazard_high, exit_policy_clip_vs_hold, thin_raw_edge, rich_entry, near_boundary |
| `KXBTC15M-26MAY060100-00` | no | -4c ($-0.04) | 44c ($0.44) | 48c ($0.48) | `exit_policy_cost` | `no_exit_repair_observation` | micro_lt_10c, exit_policy_cost, exit_policy_clip_vs_hold, near_boundary |
| `KXBTC15M-26MAY060045-45` | no | -10c ($-0.10) | 42c ($0.42) | 52c ($0.52) | `exit_policy_cost` | `no_exit_repair_observation` | small_10_24c, exit_policy_cost, recross_hazard_high, exit_policy_clip_vs_hold, thin_raw_edge, near_boundary |
| `KXBTC15M-26MAY060200-00` | yes | -12c ($-0.12) | 40c ($0.40) | 52c ($0.52) | `exit_policy_cost` | `no_exit_repair_observation` | small_10_24c, exit_policy_cost, recross_hazard_high, exit_policy_clip_vs_hold, thin_raw_edge, rich_entry, near_boundary |
| `KXBTC15M-26MAY060230-30` | yes | -20c ($-0.20) | 32c ($0.32) | 52c ($0.52) | `exit_policy_cost` | `no_exit_repair_observation` | small_10_24c, exit_policy_cost, exit_policy_clip_vs_hold, thin_raw_edge, rich_entry, near_boundary |
