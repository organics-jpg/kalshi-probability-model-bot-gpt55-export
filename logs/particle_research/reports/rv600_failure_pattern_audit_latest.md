# RV600 Failure Pattern Audit

- generated_utc: 2026-05-15T21:24:28+00:00
- research_only: True
- decision: no_current_plan_revision_supported
- plan_revision_supported: False
- family_decision: `no_existing_plan_family_viable`
- futility_decision: `reject_current_locked_family_for_promotion`
- objective_decision: `blocked_not_complete`

## Grid Pattern

- grid_generated_utc: 2026-05-15T21:24:28+00:00
- phase: `grid`
- root_count: 40
- roots: rv600_next_evidence_shadow_20260513T195001Z, rv600_next_evidence_shadow_20260513T202034Z, rv600_next_evidence_shadow_20260513T205117Z, rv600_next_evidence_shadow_20260513T211949Z, rv600_next_evidence_shadow_20260513T215130Z, rv600_next_evidence_shadow_20260513T222021Z, rv600_next_evidence_shadow_20260513T230108Z, rv600_next_evidence_shadow_20260513T234759Z, rv600_next_evidence_shadow_20260514T002426Z, rv600_next_evidence_shadow_20260514T010859Z, rv600_next_evidence_shadow_20260514T014324Z, rv600_next_evidence_shadow_20260514T021209Z, rv600_next_evidence_shadow_20260514T024042Z, rv600_next_evidence_shadow_20260514T031420Z, rv600_next_evidence_shadow_20260514T035926Z, rv600_next_evidence_shadow_20260514T045722Z, rv600_next_evidence_shadow_20260514T053423Z, rv600_next_evidence_shadow_20260514T122254Z, rv600_next_evidence_shadow_20260514T130107Z, rv600_next_evidence_shadow_20260515T024708Z, rv600_next_evidence_shadow_20260515T032104Z, rv600_next_evidence_shadow_20260515T034820Z, rv600_next_evidence_shadow_20260515T045448Z, rv600_next_evidence_shadow_20260515T053557Z, rv600_next_evidence_shadow_20260515T063046Z, rv600_next_evidence_shadow_20260515T071544Z, rv600_next_evidence_shadow_20260515T080148Z, rv600_next_evidence_shadow_20260515T083925Z, rv600_next_evidence_shadow_20260515T091646Z, rv600_next_evidence_shadow_20260515T100014Z, rv600_next_evidence_shadow_20260515T105111Z, rv600_next_evidence_shadow_20260515T113027Z, rv600_next_evidence_shadow_20260515T143222Z, rv600_next_evidence_shadow_20260515T151536Z, rv600_next_evidence_shadow_20260515T160221Z, rv600_next_evidence_shadow_20260515T164836Z, rv600_next_evidence_shadow_20260515T173507Z, rv600_next_evidence_shadow_20260515T182447Z, rv600_next_evidence_shadow_20260515T190705Z, rv600_next_evidence_shadow_20260515T200306Z
- variant_count: 3948
- summary_row_count: 11844
- position_capped_row_count: 3948
- simple_position_capped_row_count: 630
- positive_position_capped_row_count: 3873
- positive_matched_v28_delta_row_count: 1093
- support_row_count: 0

Top position-capped rejection reasons:
- `positive_roots_below_60pct`: 3930
- `positive_markets_below_60pct`: 3853
- `single_market_share_above_25pct`: 3463
- `last_window_nonpositive`: 2893
- `does_not_beat_matched_v28_by_20pct`: 2801
- `market_drawdown_worse_than_25pct`: 2556
- `avg_entry_below_10c`: 1839
- `fewer_than_25_entries`: 1182
- `does_not_beat_single_market`: 931
- `added_entries_nonpositive`: 931

## Rescue Pattern

- rescue_gate_pass_count: 0

| report | gate pass | train gates | test entries | test pnl | v28 delta | rejection |
|---|---:|---:|---:|---:|---:|---|
| `logs\particle_research\reports\rv600_meta_label_rescue_latest.json` | False | 0 | 0 | 0.0 | 0.0 | `no_train_gate_selection;fewer_than_25_test_entries;nonpositive_test_pnl;does_not_beat_matched_v28` |
| `logs\particle_research\reports\rv600_probability_calibration_rescue_latest.json` | False | 0 | 0 | 0.0 | 0.0 | `no_train_gate_selection;fewer_than_25_test_entries;nonpositive_test_pnl;does_not_beat_matched_v28` |
| `logs\particle_research\reports\rv600_conformal_abstention_rescue_latest.json` | False | 0 | 0 | 0.0 | 0.0 | `no_train_gate_selection;fewer_than_25_test_entries;nonpositive_test_pnl;does_not_beat_matched_v28` |
| `logs\particle_research\reports\rv600_online_expert_rescue_latest.json` | False | 0 | 0 | 0.0 | 0.0 | `no_train_gate_selection;fewer_than_25_test_entries;nonpositive_test_pnl;does_not_beat_matched_v28` |
| `logs\particle_research\reports\rv600_market_balance_rescue_latest.json` | False | 37 | 140 | 236.0 | -288.0 | `market_balance_rescue_failed` |
| `logs\particle_research\reports\rv600_regime_filter_rescue_latest.json` | False | 37 | 115 | 157.0 | -404.0 | `regime_filter_rescue_failed` |
| `logs\particle_research\reports\rv600_group_dro_rescue_latest.json` | False | 37 | 94 | 240.0 | -538.0 | `group_dro_rescue_failed` |

## Best Soft Rows

| variant | accounting | gates | entries | pnl | v28 delta | pos roots | pos markets | max share | rejection |
|---|---|---:|---:|---:|---:|---:|---:|---:|---|
| `rv600_primary_max_3_entries_late_70_300_ev4` | position_capped | 3 | 84 | 1120.0 | 750.0 | 0.28 | 0.37 | 0.25 | `positive_roots_below_60pct;positive_markets_below_60pct;single_market_share_above_25pct;last_window_nonpositive;market_drawdown_worse_than_25pct` |
| `rv600_softveto6_max_3_entries_late_70_300_ev4` | position_capped | 4 | 84 | 1120.0 | 750.0 | 0.28 | 0.37 | 0.25 | `positive_roots_below_60pct;positive_markets_below_60pct;single_market_share_above_25pct;last_window_nonpositive;market_drawdown_worse_than_25pct` |
| `rv600_softveto10_max_3_entries_late_70_300_ev4` | position_capped | 4 | 84 | 1120.0 | 750.0 | 0.28 | 0.37 | 0.25 | `positive_roots_below_60pct;positive_markets_below_60pct;single_market_share_above_25pct;last_window_nonpositive;market_drawdown_worse_than_25pct` |
| `rv600_primary_risk_cap_200c_late_70_300_ev4` | position_capped | 3 | 84 | 1134.0 | 689.0 | 0.28 | 0.37 | 0.25 | `positive_roots_below_60pct;positive_markets_below_60pct;single_market_share_above_25pct;last_window_nonpositive;market_drawdown_worse_than_25pct` |
| `rv600_softveto6_risk_cap_200c_late_70_300_ev4` | position_capped | 4 | 84 | 1134.0 | 689.0 | 0.28 | 0.37 | 0.25 | `positive_roots_below_60pct;positive_markets_below_60pct;single_market_share_above_25pct;last_window_nonpositive;market_drawdown_worse_than_25pct` |
| `rv600_softveto10_risk_cap_200c_late_70_300_ev4` | position_capped | 4 | 84 | 1134.0 | 689.0 | 0.28 | 0.37 | 0.25 | `positive_roots_below_60pct;positive_markets_below_60pct;single_market_share_above_25pct;last_window_nonpositive;market_drawdown_worse_than_25pct` |
| `rv600_primary_max_3_entries_late_70_240_ev0` | position_capped | 3 | 126 | 686.0 | 671.0 | 0.33 | 0.31 | 0.40 | `avg_entry_below_10c;positive_roots_below_60pct;positive_markets_below_60pct;single_market_share_above_25pct;last_window_nonpositive;market_drawdown_worse_than_25pct` |
| `rv600_softveto10_max_3_entries_late_70_240_ev0` | position_capped | 4 | 126 | 686.0 | 671.0 | 0.33 | 0.31 | 0.40 | `avg_entry_below_10c;positive_roots_below_60pct;positive_markets_below_60pct;single_market_share_above_25pct;last_window_nonpositive;market_drawdown_worse_than_25pct` |
| `rv600_primary_max_3_entries_base_70_420_ev6` | position_capped | 3 | 85 | 1451.0 | 670.0 | 0.38 | 0.50 | 0.19 | `positive_roots_below_60pct;positive_markets_below_60pct;market_drawdown_worse_than_25pct` |
| `rv600_softveto6_max_3_entries_base_70_420_ev6` | position_capped | 4 | 85 | 1451.0 | 670.0 | 0.38 | 0.50 | 0.19 | `positive_roots_below_60pct;positive_markets_below_60pct;market_drawdown_worse_than_25pct` |

## Interpretation

No current artifact supports a new RV600 plan revision. Positive grid rows are sparse or concentrated, matched-v28 delta is not positive enough, and every literature-backed rescue has zero train-gate selections. The next valid progress requires materially new shadow evidence or a genuinely new RV600 clue, not another promotion attempt from this sample.
