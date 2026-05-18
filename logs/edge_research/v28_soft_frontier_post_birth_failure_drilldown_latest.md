# v28 Soft-Frontier Post-Birth Failure Drilldown

Research-only; no live bot changes or orders.

- Generated UTC: `2026-05-07T04:22:24.664249+00:00`
- Soft-frontier freeze UTC: `2026-05-06T20:01:04.705640+00:00`
- Rule: `soft_raw03_recross50_abs65_ask35` / `{'raw_edge_min': 0.03, 'recross_max': 0.5, 'abs_d_min': 0.65, 'ask_min': 0.35, 'mechanism': 'Stricter distance version of the soft boundary rule.'}`

## Interpretation

- This is a strict post-birth failure drilldown; it is not a new candidate and does not change live logic.
- The rule is observable-only. Source labels are used only for evidence-quality audit.
- post_soft_frontier_birth_entry has 24/33 entries, 24 settled, coverage 72.72727272727273%, net 180.0c, reconstructed share 0.25, cushion 1, blockers ['settled_lt_30', 'coverage_too_low', 'full_loss_cushion_lt_3'].
- post_soft_frontier_birth_entry loss tags are {'boundary_churn_risk': 2, 'entry_timing_error': 2, 'execution_friction_or_thin_edge': 4, 'exit_helped_vs_hold': 2, 'fragility_error': 4, 'fv_error': 4, 'fv_overconfidence': 4, 'mid_cheap_tail_failure': 2, 'near_boundary_risk': 2, 'source_quality_error': 2} and current exits changed loss rows by 258.0c versus holding to settlement.
- post_soft_frontier_birth_bridge has 24/33 entries, 24 settled, coverage 72.72727272727273%, net 180.0c, reconstructed share 0.25, cushion 1, blockers ['settled_lt_30', 'coverage_too_low', 'full_loss_cushion_lt_3'].
- post_soft_frontier_birth_bridge loss tags are {'boundary_churn_risk': 2, 'entry_timing_error': 2, 'execution_friction_or_thin_edge': 4, 'exit_helped_vs_hold': 2, 'fragility_error': 4, 'fv_error': 4, 'fv_overconfidence': 4, 'mid_cheap_tail_failure': 2, 'near_boundary_risk': 2, 'source_quality_error': 2} and current exits changed loss rows by 258.0c versus holding to settlement.
- Physical read: if loss rows are mostly exit_helped_vs_hold, the next repair is FV/entry timing, not looser exits.

## post_soft_frontier_birth_entry

- Summary: `{'entries': 24, 'settled': 24, 'wins': 20, 'losses': 4, 'coverage_pct': 72.72727272727273, 'net_cents': 180.0, 'avg_net_cents': 7.5}`
- Source counts: `{'rejected_actionable': 6, 'approved_entry': 18}`
- Reconstructed share: `0.250000`
- Full-loss cushion: `1`
- Blockers: `settled_lt_30, coverage_too_low, full_loss_cushion_lt_3`
- Selected tag counts: `{'boundary_churn_risk': 7, 'clean_or_unclassified': 1, 'entry_timing_error': 2, 'execution_friction_or_thin_edge': 5, 'exit_helped_vs_hold': 2, 'exit_policy_error': 14, 'fragility_error': 4, 'fv_error': 4, 'fv_overconfidence': 4, 'mid_cheap_tail_failure': 2, 'near_boundary_risk': 5, 'source_quality_error': 6}`
- Loss tag counts: `{'boundary_churn_risk': 2, 'entry_timing_error': 2, 'execution_friction_or_thin_edge': 4, 'exit_helped_vs_hold': 2, 'fragility_error': 4, 'fv_error': 4, 'fv_overconfidence': 4, 'mid_cheap_tail_failure': 2, 'near_boundary_risk': 2, 'source_quality_error': 2}`
- Loss exit delta vs hold: `258.000000c`

### Loss Rows

| market | source | side | result | net c | gross c | hold gross c | exit delta vs hold | edge | recross | abs d | ask | tags |
|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| KXBTC15M-26MAY062130-30 | approved_entry | no | yes | -78.000000 | -32 | -152 | 120.000000 | 0.127777 | 0.303870 | 0.999156 | 0.760000 | boundary_churn_risk, entry_timing_error, execution_friction_or_thin_edge, exit_helped_vs_hold, fragility_error, fv_error, fv_overconfidence |
| KXBTC15M-26MAY070015-15 | approved_entry | no | yes | -72.000000 | -2 | -140 | 138.000000 | 0.263659 | 0.073753 | 1.543579 | 0.700000 | entry_timing_error, execution_friction_or_thin_edge, exit_helped_vs_hold, fragility_error, fv_error, fv_overconfidence |
| KXBTC15M-26MAY062345-45 | rejected_actionable | no | yes | -60.000000 | -112 | -112 | 0.000000 | 0.246238 | 0.264802 | 0.726970 | 0.560000 | boundary_churn_risk, execution_friction_or_thin_edge, fragility_error, fv_error, fv_overconfidence, mid_cheap_tail_failure, near_boundary_risk, source_quality_error |
| KXBTC15M-26MAY061700-00 | rejected_actionable | no | yes | -42.000000 | -76 | -76 | 0.000000 | 0.408347 | 0.196391 | 0.665443 | 0.380000 | execution_friction_or_thin_edge, fragility_error, fv_error, fv_overconfidence, mid_cheap_tail_failure, near_boundary_risk, source_quality_error |

### Pending Rows

| market | source | side | net c | edge | recross | abs d | ask | tags |
|---|---|---|---:|---:|---:|---:|---:|---|

## post_soft_frontier_birth_bridge

- Summary: `{'entries': 24, 'settled': 24, 'wins': 20, 'losses': 4, 'coverage_pct': 72.72727272727273, 'net_cents': 180.0, 'avg_net_cents': 7.5}`
- Source counts: `{'rejected_actionable': 6, 'approved_entry': 18}`
- Reconstructed share: `0.250000`
- Full-loss cushion: `1`
- Blockers: `settled_lt_30, coverage_too_low, full_loss_cushion_lt_3`
- Selected tag counts: `{'boundary_churn_risk': 7, 'clean_or_unclassified': 1, 'entry_timing_error': 2, 'execution_friction_or_thin_edge': 5, 'exit_helped_vs_hold': 2, 'exit_policy_error': 14, 'fragility_error': 4, 'fv_error': 4, 'fv_overconfidence': 4, 'mid_cheap_tail_failure': 2, 'near_boundary_risk': 5, 'source_quality_error': 6}`
- Loss tag counts: `{'boundary_churn_risk': 2, 'entry_timing_error': 2, 'execution_friction_or_thin_edge': 4, 'exit_helped_vs_hold': 2, 'fragility_error': 4, 'fv_error': 4, 'fv_overconfidence': 4, 'mid_cheap_tail_failure': 2, 'near_boundary_risk': 2, 'source_quality_error': 2}`
- Loss exit delta vs hold: `258.000000c`

### Loss Rows

| market | source | side | result | net c | gross c | hold gross c | exit delta vs hold | edge | recross | abs d | ask | tags |
|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| KXBTC15M-26MAY062130-30 | approved_entry | no | yes | -78.000000 | -32 | -152 | 120.000000 | 0.127777 | 0.303870 | 0.999156 | 0.760000 | boundary_churn_risk, entry_timing_error, execution_friction_or_thin_edge, exit_helped_vs_hold, fragility_error, fv_error, fv_overconfidence |
| KXBTC15M-26MAY070015-15 | approved_entry | no | yes | -72.000000 | -2 | -140 | 138.000000 | 0.263659 | 0.073753 | 1.543579 | 0.700000 | entry_timing_error, execution_friction_or_thin_edge, exit_helped_vs_hold, fragility_error, fv_error, fv_overconfidence |
| KXBTC15M-26MAY062345-45 | rejected_actionable | no | yes | -60.000000 | -112 | -112 | 0.000000 | 0.246238 | 0.264802 | 0.726970 | 0.560000 | boundary_churn_risk, execution_friction_or_thin_edge, fragility_error, fv_error, fv_overconfidence, mid_cheap_tail_failure, near_boundary_risk, source_quality_error |
| KXBTC15M-26MAY061700-00 | rejected_actionable | no | yes | -42.000000 | -76 | -76 | 0.000000 | 0.408347 | 0.196391 | 0.665443 | 0.380000 | execution_friction_or_thin_edge, fragility_error, fv_error, fv_overconfidence, mid_cheap_tail_failure, near_boundary_risk, source_quality_error |

### Pending Rows

| market | source | side | net c | edge | recross | abs d | ask | tags |
|---|---|---|---:|---:|---:|---:|---:|---|
