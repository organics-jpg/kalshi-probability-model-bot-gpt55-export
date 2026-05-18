# v28 Candidate PnL Tracker

Reporting-only consolidation of current v28 candidate lanes against live-market forward evidence.

## Counts

- Readiness candidates: `88`
- Frozen leaderboard candidates: `64`
- Unique gate/policy lanes after reconciliation: `995`
- Boundary-clock feature-gate forward lanes: `8`
- Feature-gate + book-gap exit stack forward lanes: `32`
- Feature-gate soft-frontier + exit stack forward lanes: `24`
- Boundary-clock continuous-penalty forward lanes: `8`
- Boundary-clock soft-frontier forward lanes: `6`
- Boundary-clock clean-broad frontier forward lanes: `2`
- Feature-gate cheap-tail quarantine forward lanes: `10`
- Feature-gate cheap-tail shrink forward lanes: `10`
- Feature-gate core/expansion mix lanes: `11`
- Feature-gate coverage size-shrink lanes: `20`
- Feature-gate middle-distance core lanes: `10`
- Feature-gate middle-core exit-guard lanes: `14`
- Feature-gate observable selection-mix lanes: `48`
- Feature-gate size-shrink exit-overlay lanes: `14`
- Feature-gate size-shrink delayed-recheck exit lanes: `10`
- Feature-gate size-shrink delayed-recheck rescue lanes: `10`
- Feature-gate source-confirmation replacement lanes: `2`
- Feature-gate late-collapse recheck rescue lanes: `12`
- Feature-gate dual-clock recheck rescue lanes: `14`
- Feature-gate confirmed dual-clock fill lanes: `14`
- Feature-gate source-quality proxy lanes: `66`
- Feature-gate source-proxy coverage-repair lanes: `24`
- Target cluster source-aware forward lanes: `5`
- Target cluster observable-stability forward lanes: `5`
- Exit reduce loss-control refinement forward lanes: `4`
- Exit reduce entry-depth gate forward lanes: `4`
- Exit reduce observable loss-control forward lanes: `8`
- Exit reduce drift-guard lanes: `10`
- Exit shallow-drawdown lanes: `2`
- Exit shallow-duration lanes: `2`
- Exit clip-separator watch lanes: `1`
- Matched-unchanged loss guard watch lanes: `1`
- RMT forgetting entry lanes: `32`
- Path/RMT fresh-gate lanes: `4`
- Boundary-memory FV lanes: `3`
- Phi-forgetting FV lanes: `5`
- Reward-memory FV lanes: `4`
- False-conviction family scorecard lanes: `7`
- Collapse/reentry registry lanes: `11`
- Soft-frontier size-shrink portfolio lanes: `30`
- Soft-frontier mid-price boundary shrink lanes: `15`
- Mid-price source-dilution watch lanes: `20`
- p50 book-edge NO-side shrink watch lanes: `1`
- Soft-frontier mid-price boundary exit-stack lanes: `60`
- Soft-frontier mid-price boundary clip-exit stack lanes: `15`
- Soft-frontier mid-price boundary dual-exit stack lanes: `60`
- Soft-frontier mid-price boundary dual-exit guard lanes: `60`
- Feature-gate exit-bid suppression watch lanes: `1`
- Feature-gate exit-bid delayed-recheck lanes: `1`
- Exit common-clock residual child lanes: `1`
- Soft-frontier mid-price delayed-recheck exit lanes: `2`
- Soft-frontier mid-price delayed-recheck rescue lanes: `2`
- Top-component mix portfolio lanes: `14`
- Top-component false-negative rescue lanes: `8`
- Top-component parent-fill repair lanes: `20`
- Top-component observable quarantine lanes: `24`
- Dual-lane own-freeze watch lanes: `2`
- Feature-gate value-exit watch lanes: `4`
- Value-exit feature-side guard lanes: `2`
- Lanes with settled PnL: `952`
- Lanes with explicit W/L fields: `966`
- Positive PnL lanes: `788`
- Target coverage lanes (75-90%): `643`
- Target coverage and positive PnL lanes: `582`
- Live-ready lanes: `1`
- Lanes with some approved-entry evidence: `658`
- Lanes over 35% simulated/rejected share: `629`

## Control

- Current v28 control entries: `173`
- Current v28 control gross PnL: `823c ($8.23)`
- Current v28 risk stop active: `True`

## Top Target-Coverage Positive Lanes

| gate | policy | entries | settled | W/L | coverage | net | sim share | live ready |
|---|---|---:|---:|---:|---:|---:|---:|---|
| `top_component_parent_fill_repair_child` | `diagnostic_observable_mid_confidence_parent_fill_quarter` | 76 | 76 | 67/9 | 75.25% | 2233c ($22.33) | 34.2% | False |
| `top_component_parent_fill_repair_child` | `diagnostic_mid_confidence_parent_fill_quarter` | 76 | 76 | 67/9 | 75.25% | 2233c ($22.33) | 34.2% | False |
| `top_component_parent_fill_repair_child` | `diagnostic_observable_mid_confidence_parent_fill_half` | 76 | 76 | 67/9 | 75.25% | 2190c ($21.89) | 34.2% | False |
| `top_component_parent_fill_repair_child` | `diagnostic_mid_confidence_parent_fill_half` | 76 | 76 | 67/9 | 75.25% | 2190c ($21.89) | 34.2% | False |
| `top_component_parent_fill_repair_child` | `diagnostic_parent_fill_wide_mid_absd_ask_notch` | 76 | 76 | 67/9 | 75.25% | 2145c ($21.45) | 34.2% | False |
| `top_component_parent_fill_repair_child` | `diagnostic_parent_fill_mid_absd_ask_notch` | 76 | 76 | 67/9 | 75.25% | 2142c ($21.42) | 34.2% | False |
| `top_component_parent_fill_repair_child` | `diagnostic_smooth_parent_fill_source_risk` | 76 | 76 | 67/9 | 75.25% | 2127c ($21.27) | 34.2% | False |
| `top_component_false_negative_rescue_child` | `diagnostic_union_rebound` | 76 | 76 | 67/9 | 75.25% | 2102c ($21.02) | 34.2% | False |
| `top_component_false_negative_rescue_child` | `diagnostic_approved_union_rebound` | 76 | 76 | 67/9 | 75.25% | 2102c ($21.02) | 34.2% | False |
| `top_component_parent_fill_repair_child` | `diagnostic_exit_child_only_control` | 76 | 76 | 67/9 | 75.25% | 2102c ($21.02) | 34.2% | False |
| `top_component_parent_fill_repair_child` | `diagnostic_parent_fill_all_rejected_half` | 76 | 76 | 67/9 | 75.25% | 2095c ($20.95) | 34.2% | False |
| `top_component_parent_fill_repair_child` | `diagnostic_parent_fill_all_rejected_quarter` | 76 | 76 | 67/9 | 75.25% | 2091c ($20.91) | 34.2% | False |

## Top Positive Lanes

| gate | policy | entries | settled | W/L | coverage | net | sim share | live ready |
|---|---|---:|---:|---:|---:|---:|---:|---|
| `top_component_parent_fill_repair_child` | `diagnostic_observable_mid_confidence_parent_fill_quarter` | 76 | 76 | 67/9 | 75.25% | 2233c ($22.33) | 34.2% | False |
| `top_component_parent_fill_repair_child` | `diagnostic_mid_confidence_parent_fill_quarter` | 76 | 76 | 67/9 | 75.25% | 2233c ($22.33) | 34.2% | False |
| `top_component_parent_fill_repair_child` | `diagnostic_observable_mid_confidence_parent_fill_half` | 76 | 76 | 67/9 | 75.25% | 2190c ($21.89) | 34.2% | False |
| `top_component_parent_fill_repair_child` | `diagnostic_mid_confidence_parent_fill_half` | 76 | 76 | 67/9 | 75.25% | 2190c ($21.89) | 34.2% | False |
| `top_component_parent_fill_repair_child` | `diagnostic_parent_fill_wide_mid_absd_ask_notch` | 76 | 76 | 67/9 | 75.25% | 2145c ($21.45) | 34.2% | False |
| `top_component_parent_fill_repair_child` | `diagnostic_parent_fill_mid_absd_ask_notch` | 76 | 76 | 67/9 | 75.25% | 2142c ($21.42) | 34.2% | False |
| `top_component_parent_fill_repair_child` | `diagnostic_smooth_parent_fill_source_risk` | 76 | 76 | 67/9 | 75.25% | 2127c ($21.27) | 34.2% | False |
| `top_component_false_negative_rescue_child` | `diagnostic_union_rebound` | 76 | 76 | 67/9 | 75.25% | 2102c ($21.02) | 34.2% | False |
| `top_component_false_negative_rescue_child` | `diagnostic_approved_union_rebound` | 76 | 76 | 67/9 | 75.25% | 2102c ($21.02) | 34.2% | False |
| `top_component_parent_fill_repair_child` | `diagnostic_exit_child_only_control` | 76 | 76 | 67/9 | 75.25% | 2102c ($21.02) | 34.2% | False |
| `top_component_parent_fill_repair_child` | `diagnostic_parent_fill_all_rejected_half` | 76 | 76 | 67/9 | 75.25% | 2095c ($20.95) | 34.2% | False |
| `top_component_parent_fill_repair_child` | `diagnostic_parent_fill_all_rejected_quarter` | 76 | 76 | 67/9 | 75.25% | 2091c ($20.91) | 34.2% | False |

## Top Positive Lanes With Approved-Entry Evidence

| gate | policy | entries | settled | W/L | coverage | net | sim share | live ready |
|---|---|---:|---:|---:|---:|---:|---:|---|
| `top_component_mix_portfolio` | `rescue_drop15_plus_ask_parent_fill_to75` | 76 | 76 | 65/11 | 75.25% | 1716c ($17.16) | 34.2% | False |
| `top_component_mix_portfolio` | `rescue_drop15_plus_absd_parent_fill_to75` | 76 | 76 | 64/12 | 75.25% | 1680c ($16.80) | 34.2% | False |
| `top_component_mix_portfolio` | `rescue_drop15_plus_all_parent_fill` | 79 | 79 | 66/13 | 78.22% | 1678c ($16.77) | 36.7% | False |
| `top_component_mix_portfolio` | `rescue_drop15_exit_clock_rows_only` | 59 | 59 | 52/7 | 58.42% | 1666c ($16.66) | 15.3% | False |
| `top_component_mix_portfolio` | `rescue_drop15_plus_approved_parent_fill` | 59 | 59 | 52/7 | 58.42% | 1666c ($16.66) | 15.3% | False |
| `soft_frontier_midprice_delayed_recheck_rescue` | `diagnostic_prefreeze_context_diagnostic_entry_quarter_midprice_boundary_latest_delay60_bid_ge60_drop_lte11` | 59 | 59 | 52/7 | 78.22% | 1602c ($16.02) | 15.3% | False |
| `top_component_mix_portfolio` | `rescue_drop15_plus_observable_parent_fill_to75` | 76 | 76 | 63/13 | 75.25% | 1596c ($15.96) | 34.2% | False |
| `top_component_mix_portfolio` | `rescue_drop15_plus_recross_parent_fill_to75` | 76 | 76 | 63/13 | 75.25% | 1556c ($15.56) | 34.2% | False |
| `soft_frontier_midprice_delayed_recheck_exit` | `diagnostic_prefreeze_context_diagnostic_entry_quarter_midprice_boundary_latest_delay60_bid_ge60_drop_lte10` | 59 | 59 | 51/8 | 78.22% | 1502c ($15.02) | 15.3% | False |
| `top_component_mix_portfolio` | `delayed_base_exit_clock_rows_only` | 59 | 59 | 51/8 | 58.42% | 1502c ($15.02) | 15.3% | False |
| `soft_frontier_midprice_boundary_dual_exit_guard` | `diagnostic_bridge_quarter_midprice_boundary_or_reduce_p_hold80` | 77 | 57 | 50/7 | 77.78% | 1418c ($14.18) | 36.4% | False |
| `soft_frontier_midprice_boundary_dual_exit_guard` | `diagnostic_bridge_half_midprice_boundary_or_reduce_p_hold80` | 77 | 57 | 50/7 | 77.78% | 1418c ($14.18) | 36.4% | False |

## Top Approved-Entry Evidence Lanes

| gate | policy | entries | settled | W/L | coverage | net | sim share | live ready |
|---|---|---:|---:|---:|---:|---:|---:|---|
| `top_component_mix_portfolio` | `rescue_drop15_plus_ask_parent_fill_to75` | 76 | 76 | 65/11 | 75.25% | 1716c ($17.16) | 34.2% | False |
| `top_component_mix_portfolio` | `rescue_drop15_plus_absd_parent_fill_to75` | 76 | 76 | 64/12 | 75.25% | 1680c ($16.80) | 34.2% | False |
| `top_component_mix_portfolio` | `rescue_drop15_plus_all_parent_fill` | 79 | 79 | 66/13 | 78.22% | 1678c ($16.77) | 36.7% | False |
| `top_component_mix_portfolio` | `rescue_drop15_exit_clock_rows_only` | 59 | 59 | 52/7 | 58.42% | 1666c ($16.66) | 15.3% | False |
| `top_component_mix_portfolio` | `rescue_drop15_plus_approved_parent_fill` | 59 | 59 | 52/7 | 58.42% | 1666c ($16.66) | 15.3% | False |
| `soft_frontier_midprice_delayed_recheck_rescue` | `diagnostic_prefreeze_context_diagnostic_entry_quarter_midprice_boundary_latest_delay60_bid_ge60_drop_lte11` | 59 | 59 | 52/7 | 78.22% | 1602c ($16.02) | 15.3% | False |
| `top_component_mix_portfolio` | `rescue_drop15_plus_observable_parent_fill_to75` | 76 | 76 | 63/13 | 75.25% | 1596c ($15.96) | 34.2% | False |
| `top_component_mix_portfolio` | `rescue_drop15_plus_recross_parent_fill_to75` | 76 | 76 | 63/13 | 75.25% | 1556c ($15.56) | 34.2% | False |
| `soft_frontier_midprice_delayed_recheck_exit` | `diagnostic_prefreeze_context_diagnostic_entry_quarter_midprice_boundary_latest_delay60_bid_ge60_drop_lte10` | 59 | 59 | 51/8 | 78.22% | 1502c ($15.02) | 15.3% | False |
| `top_component_mix_portfolio` | `delayed_base_exit_clock_rows_only` | 59 | 59 | 51/8 | 58.42% | 1502c ($15.02) | 15.3% | False |
| `soft_frontier_midprice_boundary_dual_exit_guard` | `diagnostic_bridge_quarter_midprice_boundary_or_reduce_p_hold80` | 77 | 57 | 50/7 | 77.78% | 1418c ($14.18) | 36.4% | False |
| `soft_frontier_midprice_boundary_dual_exit_guard` | `diagnostic_bridge_half_midprice_boundary_or_reduce_p_hold80` | 77 | 57 | 50/7 | 77.78% | 1418c ($14.18) | 36.4% | False |

## Interpretation

- The readiness artifact is the widest current count; the frozen leaderboard carries W/L for fewer lanes.
- `live_ready=false` means the lane is still shadow/research-only even when its PnL is positive.
- High simulated/rejected share means the lane is mostly reconstructed opportunity evidence, not actual approved live entries.
