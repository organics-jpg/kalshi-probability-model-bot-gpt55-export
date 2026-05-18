# RV600 Latest Status - 2026-05-15

This is the current RV600 status after freezing `RV600NEAR001` and collecting
two additional read-only bounded shadow roots. All work remains research-only:
no live trades, no live v28 logic changes, and no bot restart.

## Frozen Candidate

- plan:
  `logs/particle_research/locked_oos_plans/rv600_breadth_nearmiss_RV600NEAR001_locked_plan.json`
- variant:
  `rv600_primary_side_flip_only_broad_70_600_ev4`
- evidence counted only after:
  `2026-05-15T04:53:47Z`

Why frozen:

- simple three-gate RV600 candidate
- already in the locked candidate set
- side-flip-only keeps repeated-entry accounting clean
- prior 22-root diagnostic cleared breadth, concentration, recency, and
  matched-v28 delta
- prior 22-root diagnostic failed average PnL per entry

## New Root

- root:
  `logs/particle_research/real_shadow/rv600_next_evidence_shadow_20260515T045448Z`
- checkpoint rows: `830`
- independent spot rows: `3837`
- offline v28 contexts: `828`
- pipeline contexts: `751`
- labels written: `2`
- label issues: `0`

Root score:

- report:
  `logs/particle_research/real_shadow/rv600_next_evidence_shadow_20260515T045448Z/rv600_native_forward_opportunity.json`
- best grid:
  `rv600_primary_max_3_entries_base_70_420_ev6`
- best grid PnL: `+201c`
- best grid rejection:
  `fewer_than_25_entries;positive_markets_below_60pct;single_market_share_above_25pct;does_not_beat_matched_v28_by_20pct`

`RV600NEAR001` on the new root:

- entries: `3`
- markets: `2`
- selected PnL: `+39c`
- average PnL per entry: `13.0c`
- matched-v28 delta: `0c`
- rejection:
  `fewer_than_25_entries;positive_markets_below_60pct;single_market_share_above_25pct;does_not_beat_matched_v28_by_20pct`

## Cumulative 23-Root State

- cumulative opportunity:
  `logs/particle_research/reports/rv600_next_evidence_shadow_cumulative_latest_opportunity.json`
- cumulative bounded audit:
  `logs/particle_research/reports/rv600_shadow_bounded_cumulative_audit_latest.json`
- current grid:
  `logs/particle_research/reports/rv600_bounded_current_grid_latest.json`
- objective audit:
  `logs/particle_research/reports/rv600_objective_state_latest.json`

Current cumulative metrics:

- roots: `23`
- settled markets: `44`
- candidate rows: `18121`
- locked entries: `228`
- locked PnL: `+4760c`
- best grid:
  `rv600_primary_max_3_entries_base_70_420_ev6`
- best grid PnL: `+1358c`
- best grid rejection:
  `positive_roots_below_60pct;positive_markets_below_60pct`

`RV600NEAR001` cumulative diagnostic state:

- entries: `44`
- markets: `30`
- selected PnL: `+378c`
- matched-v28 delta: `+218c`
- average PnL per entry: `8.5909c`
- positive root rate: `0.6522`
- positive market rate: `0.6000`
- max single-market PnL share: `0.1614`
- rejection:
  `avg_entry_below_10c`

## Refreshed 23-Root Rescues

- meta-label: failed, `train_gate_selection_count=0`, `test_selected_pnl_cents=+13c`
- probability calibration: failed, `train_gate_selection_count=0`, `test_selected_pnl_cents=+813c`
- conformal abstention: failed, `train_gate_selection_count=0`, `test_selected_pnl_cents=0c`
- online expert: failed, `train_gate_selection_count=0`, `test_selected_pnl_cents=+321c`
- market balance: failed, `gate_pass_rows=0`, `prequential_test_pnl_cents=+298c`
- regime filter: failed, `support_row_count=0`, `prequential_test_pnl_cents=+568c`
- group DRO: failed, `support_row_count=0`, `prequential_test_pnl_cents=+782c`
- PBO: failed, `pbo=0.546875`, `positive_split_rate=0.8223`
- stability selection: failed, `full_support_count=0`, selected-test average entry `3.2334c`

## Verdict

The goal is not complete. RV600 has positive slices and the frozen near-miss
remains worth observing forward-only, but there is still no deployable or
moderately validated RV600-derived strategy. The active blockers are average
entry on the near-miss, root/market breadth on the best grid, PBO rejection,
and stability-selection failure.

## Update: 24 Roots After Second RV600NEAR001 Forward Root

Collected another read-only bounded shadow root:

- root:
  `logs/particle_research/real_shadow/rv600_next_evidence_shadow_20260515T053557Z`
- checkpoint rows: `791`
- independent spot rows: `4360`
- offline v28 contexts: `790`
- pipeline contexts: `719`
- labels written after delayed refresh: `2`
- label issues: `0`

`RV600NEAR001` on this root:

- entries: `2`
- markets: `2`
- selected PnL: `-28c`
- matched-v28 delta: `-6c`
- average PnL per entry: `-14.0c`
- rejection:
  `nonpositive_pnl;avg_entry_below_10c;positive_markets_below_60pct;last_window_nonpositive`

Updated cumulative state:

- roots: `24`
- settled markets: `46`
- candidate rows: `18840`
- locked entries: `230`
- locked PnL: `+4732c`
- best grid:
  `rv600_primary_max_3_entries_base_70_420_ev6`
- best grid PnL: `+1358c`
- best grid rejection:
  `positive_roots_below_60pct;positive_markets_below_60pct;last_window_nonpositive`

`RV600NEAR001` cumulative diagnostic state after the second forward-only root:

- entries: `46`
- markets: `32`
- selected PnL: `+350c`
- matched-v28 delta: `+212c`
- average PnL per entry: `7.6087c`
- positive root rate: `0.6250`
- positive market rate: `0.5625`
- max single-market PnL share: `0.1743`
- last-window PnL: `-28c`
- rejection:
  `avg_entry_below_10c;positive_markets_below_60pct;last_window_nonpositive`

Refreshed 24-root rescue state:

- meta-label: failed, `train_gate_selection_count=0`, `test_selected_pnl_cents=+13c`
- probability calibration: failed, `train_gate_selection_count=0`, `test_selected_pnl_cents=+813c`
- conformal abstention: failed, `train_gate_selection_count=0`, `test_selected_pnl_cents=0c`
- online expert: failed, `train_gate_selection_count=0`, `test_selected_pnl_cents=+233c`
- market balance: failed, `gate_pass_rows=0`, `prequential_test_pnl_cents=+298c`
- regime filter: failed, `support_row_count=0`, `prequential_test_pnl_cents=+492c`
- group DRO: failed, `support_row_count=0`, `prequential_test_pnl_cents=+782c`
- PBO: failed, `pbo=0.5918`, `positive_split_rate=0.7852`
- stability selection: failed, `full_support_count=0`, `locked_selection_count=78`

Updated verdict: `RV600NEAR001` should be treated as weakening, not improving.
It now fails average-entry, positive-market, and recent-window gates. Continue
research-only evidence collection only if the purpose is to reject or
independently recover the candidate under pre-registered forward rules; do not
tune thresholds from these outcomes.

## Frozen-Plan Forward Audit

Added a dedicated future-only audit for the frozen plan:

- script:
  `probe_rv600_locked_plan_forward_audit.py`
- report:
  `logs/particle_research/reports/rv600_locked_plan_forward_audit_latest.json`
- markdown:
  `logs/particle_research/reports/rv600_locked_plan_forward_audit_latest.md`
- objective audit:
  `logs/particle_research/reports/rv600_objective_state_latest.json`

The audit only counts decisions after the pre-registration timestamp
`2026-05-15T04:53:47Z`. Current result:

- decision:
  `locked_plan_forward_incomplete_or_failed`
- post-registration roots: `2`
- calendar days: `1`
- weekend days: `0`
- entries: `5`
- markets: `4`
- selected PnL: `+11c`
- matched-v28 delta: `-6c`
- average PnL per entry: `2.2c`
- last-window PnL: `-28c`
- rejection:
  `fewer_than_25_entries;avg_entry_below_10c;positive_roots_below_60pct;positive_markets_below_60pct;single_market_share_above_25pct;last_window_nonpositive;does_not_beat_matched_v28_by_20pct`

The objective-state audit now includes this as an explicit blocker:
`locked_plan_forward_audit_failed`.

## Data-Snooping Reality Check

The current unresolved modeling problem is not a missing fill assumption; it is
selection risk across thousands of RV600 grid variants. I searched the
backtest-overfitting literature and implemented a root-bootstrap reality check
because it directly matches the question: did the best apparent RV600 variant
beat matched v28 by more than the expected max-statistic from the tested
candidate universe?

Sources considered:

- selected:
  [White-style Reality Check for technical trading rules](https://www.fmg.ac.uk/publications/discussion-papers/data-snooping-technical-trading-rule-performance-and-bootstrap)
- partially used:
  [Hansen Superior Predictive Ability test](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=264569)
- not selected:
  [Deflated Sharpe Ratio](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2460551)
- not selected:
  [Backtest PnL discounting](https://arxiv.org/abs/1902.01802)
- not selected:
  [Optimal trading rules without backtesting](https://arxiv.org/abs/1408.1159)

New audit:

- script:
  `probe_rv600_reality_check_audit.py`
- report:
  `logs/particle_research/reports/rv600_reality_check_audit_latest.json`
- markdown:
  `logs/particle_research/reports/rv600_reality_check_audit_latest.md`
- decision:
  `reality_check_rejects_current_grid`
- roots: `24`
- candidates tested: `5454`
- best matched-v28-delta variant:
  `rv600_primary_max_3_entries_late_70_300_ev4`
- best matched-v28 delta: `+755c`
- best selected PnL: `+1102c`
- best average PnL per entry: `19.3333c`
- best rejection:
  `positive_roots_below_60pct;positive_markets_below_60pct;single_market_share_above_25pct;last_window_nonpositive`
- mean reality-check p-value: `0.2887`
- studentized reality-check p-value: `0.3497`

Interpretation: the best-looking matched-v28 edge is not strong after adjusting
for the fact that 5454 candidate/accounting variants were searched. The
objective-state audit now includes this as `reality_check_rejected`.

## Update: RV600REV001 Freeze And First Forward Root

Collected and scored two more read-only bounded shadow roots:

- root:
  `logs/particle_research/real_shadow/rv600_next_evidence_shadow_20260515T063046Z`
- checkpoint rows: `828`
- independent spot rows: `2714`
- offline v28 contexts: `827`
- pipeline contexts: `783`
- labels written after delayed refresh: `2`
- label issues: `0`

This 25th root briefly produced a local cumulative support row:

- variant:
  `rv600_primary_same_side_ev_step_3c_base_70_420_ev2`
- accounting:
  `position_capped`
- entries: `63`
- markets: `28`
- selected PnL: `+1198c`
- matched-v28 delta: `+542c`
- average PnL per entry: `19.0159c`
- positive root rate: `0.6000`
- positive market rate: `0.6071`
- max single-market share: `0.2362`
- last-window PnL: `+28c`
- rejection: none

The candidate was frozen before counting any future evidence:

- plan:
  `logs/particle_research/locked_oos_plans/rv600_revision_RV600REV001_locked_plan.json`
- markdown:
  `logs/particle_research/locked_oos_plans/rv600_revision_RV600REV001_locked_plan.md`
- plan_id:
  `RV600REV001`
- evidence counted only after:
  `2026-05-15T07:10:45Z`

This freeze was not a promotion. At the time of freeze, broader anti-overfit
audits still rejected the grid:

- PBO: `pbo_rejects_current_grid`, `pbo=0.5449`
- reality check: `reality_check_rejects_current_grid`, mean p-value `0.2498`,
  studentized p-value `0.2278`
- stability selection: `stability_selection_rescue_failed`

Then collected the first true post-freeze root:

- root:
  `logs/particle_research/real_shadow/rv600_next_evidence_shadow_20260515T071544Z`
- checkpoint rows: `789`
- independent spot rows: `3245`
- offline v28 contexts: `788`
- pipeline contexts: `743`
- labels written after delayed refresh: `2`
- label issues: `0`

`RV600REV001` on its first post-freeze root:

- report:
  `logs/particle_research/reports/rv600_locked_plan_forward_audit_latest.json`
- decision:
  `locked_plan_forward_incomplete_or_failed`
- post-freeze roots: `1`
- entries: `1`
- selected PnL: `-13c`
- average PnL per entry: `-13.0c`
- rejection:
  `fewer_than_25_entries;nonpositive_pnl;avg_entry_below_10c;positive_roots_below_60pct;positive_markets_below_60pct;last_window_nonpositive;does_not_beat_matched_v28_by_20pct;no_fill_penalty_nonpositive`

After this first true forward root, the broader current-grid state reverted to
blocked:

- cumulative roots: `26`
- candidate rows: `20366`
- settled markets: `50`
- cumulative bounded audit:
  `cumulative_bounded_scored_with_entries`
- best grid:
  `rv600_primary_max_3_entries_broad_70_600_ev0`
- best grid PnL: `+1553c`
- best grid rejection:
  `positive_roots_below_60pct;positive_markets_below_60pct`
- failure-pattern audit:
  `no_current_plan_revision_supported`, `support_row_count=0`
- PBO:
  `pbo_rejects_current_grid`, `pbo=0.4414`
- reality check:
  `reality_check_rejects_current_grid`, mean p-value `0.2637`,
  studentized p-value `0.3047`
- stability selection:
  `stability_selection_rescue_failed`, `full_support_count=0`

Secondary rescues refreshed on 26 roots:

- meta-label:
  failed, `train_gate_selection_count=0`, `test_selected_pnl_cents=0c`
- probability calibration:
  failed, `train_gate_selection_count=0`, `test_selected_pnl_cents=0c`
- conformal abstention:
  failed, `train_gate_selection_count=0`, `test_selected_pnl_cents=0c`
- online expert:
  failed, `train_gate_selection_count=0`, `test_selected_pnl_cents=0c`
- market balance:
  failed, `gate_pass_rows=0`, `prequential_test_pnl_cents=+501c`
- regime filter:
  failed, `support_row_count=0`, `prequential_test_pnl_cents=+479c`
- group DRO:
  failed, `support_row_count=0`, `prequential_test_pnl_cents=+797c`

Updated verdict: `RV600REV001` should be treated as a failed or at least
highly suspect freeze unless later future-only evidence reverses the first
root. The current 26-root grid still has positive PnL slices, but no RV600
family is complete or promotable under the anti-overfitting gates.

## Update: 27 Roots After Additional Forward Evidence

Collected one more read-only bounded shadow root:

- root:
  `logs/particle_research/real_shadow/rv600_next_evidence_shadow_20260515T080148Z`
- checkpoint rows: `800`
- independent spot rows: `2961`
- offline v28 contexts: `799`
- pipeline contexts: `706`
- labels written after delayed refresh: `2`
- label issues: `0`

Root score:

- report:
  `logs/particle_research/real_shadow/rv600_next_evidence_shadow_20260515T080148Z/rv600_native_forward_opportunity.json`
- locked entries: `1`
- locked PnL: `+14c`
- best grid:
  `blend_95_5_max_3_entries_broad_70_600_ev2`
- best grid PnL: `+42c`
- best grid rejection:
  `fewer_than_25_entries;single_market_share_above_25pct;does_not_beat_matched_v28_by_20pct`

`RV600REV001` future-only state:

- forward roots after freeze: `2`
- accepted entries: `1`
- selected PnL: `-13c`
- matched-v28 delta: `-24c`
- average PnL per entry: `-13.0c`
- rejection:
  `fewer_than_25_entries;nonpositive_pnl;avg_entry_below_10c;positive_roots_below_60pct;positive_markets_below_60pct;last_window_nonpositive;does_not_beat_matched_v28_by_20pct;no_fill_penalty_nonpositive`

Updated 27-root state:

- candidate rows: `21072`
- settled markets: `52`
- cumulative bounded audit:
  `cumulative_bounded_scored_with_entries`
- best cumulative grid:
  `rv600_primary_max_3_entries_broad_70_600_ev0`
- best cumulative grid PnL: `+1593c`
- best cumulative grid rejection:
  `positive_roots_below_60pct;positive_markets_below_60pct`
- failure-pattern audit:
  `no_current_plan_revision_supported`, `support_row_count=0`
- PBO:
  `pbo_rejects_current_grid`, `pbo=0.3711`
- reality check:
  `reality_check_rejects_current_grid`, mean p-value `0.2488`,
  studentized p-value `0.2987`
- stability selection:
  `stability_selection_rescue_failed`, `full_support_count=0`

Updated verdict: the additional root did not recover `RV600REV001` and did not
produce a replacement support row. RV600 remains research-only and incomplete.

## Update: 28 Roots After Additional Forward Evidence

Collected one more read-only bounded shadow root:

- root:
  `logs/particle_research/real_shadow/rv600_next_evidence_shadow_20260515T083925Z`
- checkpoint rows: `807`
- independent spot rows: `3815`
- offline v28 contexts: `805`
- pipeline contexts: `761`
- labels written after delayed refresh: `2`
- label issues: `0`

Root score:

- report:
  `logs/particle_research/real_shadow/rv600_next_evidence_shadow_20260515T083925Z/rv600_native_forward_opportunity.json`
- locked entries: `16`
- locked PnL: `-135c`
- best grid:
  `rv600_primary_max_3_entries_late_70_300_ev0`
- best grid PnL: `+11c`
- best grid rejection:
  `fewer_than_25_entries;avg_entry_below_10c;single_market_share_above_25pct`

`RV600REV001` future-only state:

- forward roots after freeze: `3`
- accepted entries: `4`
- selected PnL: `-27c`
- average PnL per entry: `-6.75c`
- rejection:
  `fewer_than_25_entries;nonpositive_pnl;avg_entry_below_10c;positive_roots_below_60pct;positive_markets_below_60pct;last_window_nonpositive;no_fill_penalty_nonpositive`

Updated 28-root state:

- candidate rows: `21833`
- settled markets: `54`
- cumulative bounded audit:
  `cumulative_bounded_scored_with_entries`
- best cumulative grid:
  `rv600_primary_max_3_entries_broad_70_600_ev0`
- best cumulative grid PnL: `+1482c`
- best cumulative grid rejection:
  `positive_roots_below_60pct;positive_markets_below_60pct;last_window_nonpositive`
- failure-pattern audit:
  `no_current_plan_revision_supported`, `support_row_count=0`
- PBO:
  `pbo_rejects_current_grid`, `pbo=0.4629`
- reality check:
  `reality_check_rejects_current_grid`, mean p-value `0.2607`,
  studentized p-value `0.3057`
- stability selection:
  `stability_selection_rescue_failed`, `full_support_count=0`
- market balance:
  `market_balance_rescue_failed`, `gate_pass_rows=0`,
  `prequential_test_pnl_cents=+430c`
- regime filter:
  `regime_filter_rescue_failed`, `support_row_count=0`,
  `prequential_test_pnl_cents=+368c`
- group DRO:
  `group_dro_rescue_failed`, `support_row_count=0`,
  `prequential_test_pnl_cents=+686c`

Updated verdict: the new root worsened the current picture. The positive
cumulative grid slices remain concentrated and unstable; `RV600REV001` remains
negative in future-only evidence.

## Update: 29 Roots After Additional Forward Evidence

Collected one more read-only bounded shadow root:

- root:
  `logs/particle_research/real_shadow/rv600_next_evidence_shadow_20260515T091646Z`
- checkpoint rows: `839`
- independent spot rows: `3817`
- offline v28 contexts: `838`
- pipeline contexts: `830`
- labels written after delayed refresh: `2`
- label issues: `0`

Root score:

- report:
  `logs/particle_research/real_shadow/rv600_next_evidence_shadow_20260515T091646Z/rv600_native_forward_opportunity.json`
- locked entries: `1`
- locked PnL: `-12c`
- best grid:
  `rv600_primary_single_market_late_70_180_ev12`
- best grid PnL: `0c`
- best grid rejection:
  `fewer_than_25_entries;nonpositive_pnl;avg_entry_below_10c;positive_roots_below_60pct;positive_markets_below_60pct;last_window_nonpositive;no_fill_penalty_nonpositive`

`RV600REV001` future-only state:

- forward roots after freeze: `4`
- accepted entries: `6`
- selected PnL: `-42c`
- average PnL per entry: `-7.0c`
- rejection:
  `fewer_than_25_entries;nonpositive_pnl;avg_entry_below_10c;positive_roots_below_60pct;positive_markets_below_60pct;last_window_nonpositive;no_fill_penalty_nonpositive`

Updated 29-root state:

- candidate rows: `22663`
- settled markets: `56`
- cumulative bounded audit:
  `cumulative_bounded_scored_with_entries`
- best cumulative grid:
  `rv600_primary_max_3_entries_broad_70_600_ev0`
- best cumulative grid PnL: `+1419c`
- best cumulative grid rejection:
  `positive_roots_below_60pct;positive_markets_below_60pct;last_window_nonpositive`
- failure-pattern audit:
  `no_current_plan_revision_supported`, `support_row_count=0`
- PBO:
  `pbo_rejects_current_grid`, `pbo=0.5059`
- reality check:
  `reality_check_rejects_current_grid`, mean p-value `0.2507`,
  studentized p-value `0.3037`
- stability selection:
  `stability_selection_rescue_failed`, `full_support_count=0`
- market balance:
  `market_balance_rescue_failed`, `gate_pass_rows=0`,
  `prequential_test_pnl_cents=+402c`
- regime filter:
  `regime_filter_rescue_failed`, `support_row_count=0`,
  `prequential_test_pnl_cents=+305c`
- group DRO:
  `group_dro_rescue_failed`, `support_row_count=0`,
  `prequential_test_pnl_cents=+671c`

Updated verdict: the additional root further weakens RV600. `RV600REV001` is
negative across four future-only roots, and no replacement candidate currently
survives the anti-overfitting gates.

## Update: 30 Roots After Additional Forward Evidence

Collected one more read-only bounded shadow root:

- root:
  `logs/particle_research/real_shadow/rv600_next_evidence_shadow_20260515T100014Z`
- checkpoint rows: `811`
- independent spot rows: `4634`
- offline v28 contexts: `810`
- offline v28 context issues: `1`
- pipeline contexts: `763`
- labels written after delayed refresh: `2`
- label issues after refresh: `0`

Root score:

- report:
  `logs/particle_research/real_shadow/rv600_next_evidence_shadow_20260515T100014Z/rv600_native_forward_opportunity.json`
- locked entries: `1`
- locked PnL: `+37c`
- best grid:
  `blend_95_5_max_3_entries_broad_70_600_ev2`
- best grid PnL: `+146c`
- best grid rejection:
  `fewer_than_25_entries;single_market_share_above_25pct;does_not_beat_matched_v28_by_20pct`
- best RV600-primary grid:
  `rv600_primary_max_3_entries_broad_70_600_ev0`
- best RV600-primary grid PnL: `+138c`
- best RV600-primary rejection:
  `fewer_than_25_entries;single_market_share_above_25pct;does_not_beat_matched_v28_by_20pct`

`RV600REV001` future-only state:

- forward roots after freeze: `5`
- accepted entries: `7`
- markets: `5`
- selected PnL: `-21c`
- matched-v28 delta: `-24c`
- average PnL per entry: `-3.0c`
- positive root rate: `0.2000`
- positive market rate: `0.2000`
- rejection:
  `fewer_than_25_entries;nonpositive_pnl;avg_entry_below_10c;positive_roots_below_60pct;positive_markets_below_60pct;does_not_beat_matched_v28_by_20pct;no_fill_penalty_nonpositive`

Updated 30-root state:

- candidate rows: `23426`
- settled markets: `58`
- cumulative bounded audit:
  `cumulative_bounded_scored_with_entries`
- best cumulative grid:
  `rv600_primary_max_3_entries_broad_70_600_ev0`
- best cumulative grid entries: `135`
- best cumulative grid PnL: `+1557c`
- best cumulative grid matched-v28 delta: `+651c`
- best cumulative grid average PnL per entry: `11.5333c`
- positive root rate: `0.5667`
- positive market rate: `0.5111`
- max single-market PnL share: `0.1567`
- last-window PnL: `+138c`
- best cumulative grid rejection:
  `positive_roots_below_60pct;positive_markets_below_60pct`

Refreshed 30-root anti-overfit state:

- failure-pattern audit:
  `no_current_plan_revision_supported`, `support_row_count=0`
- PBO:
  `pbo_rejects_current_grid`, `pbo=0.3848`, positive split rate `0.8516`
- reality check:
  `reality_check_rejects_current_grid`, best matched-v28 delta `+832c`,
  mean p-value `0.2607`, studentized p-value `0.3067`
- stability selection:
  `stability_selection_rescue_failed`, `full_support_count=0`,
  selected-test average entry `2.9570c`
- market balance:
  `market_balance_rescue_failed`, `gate_pass_rows=0`,
  `prequential_test_pnl_cents=+540c`,
  matched-v28 delta `-207c`
- regime filter:
  `regime_filter_rescue_failed`, `support_row_count=0`,
  `prequential_test_pnl_cents=+443c`,
  matched-v28 delta `-392c`
- group DRO:
  `group_dro_rescue_failed`, `support_row_count=0`,
  `prequential_test_pnl_cents=+692c`,
  matched-v28 delta `-272c`

Objective audit:

- report:
  `logs/particle_research/reports/rv600_objective_state_latest.json`
- decision:
  `blocked_not_complete`
- objective complete: `false`
- key blockers:
  `current_locked_family_rejected`,
  `no_existing_plan_family_viable`,
  `cumulative_bounded_shadow_insufficient`,
  `pbo_stability_rejected`,
  `reality_check_rejected`,
  `stability_selection_rescue_failed`,
  `locked_plan_forward_audit_failed`

Updated verdict: the new root improved the 30-root cumulative PnL slice, but it
did not clear the breadth or anti-overfitting gates. `RV600REV001` remains
negative in future-only accounting, no existing plan-defined family is viable,
and the objective remains incomplete. Continue research-only collection or
document a new plan revision before freezing any replacement candidate; do not
promote or live-test the current RV600 families.

## Update: 31 Roots After Additional Forward Evidence

Collected one more read-only bounded shadow root:

- root:
  `logs/particle_research/real_shadow/rv600_next_evidence_shadow_20260515T105111Z`
- checkpoint rows: `734`
- independent spot rows: `2846`
- offline v28 contexts: `733`
- offline v28 context issues: `1`
- pipeline contexts: `665`
- labels written after delayed refresh: `2`
- label issues after refresh: `0`

Root score:

- report:
  `logs/particle_research/real_shadow/rv600_next_evidence_shadow_20260515T105111Z/rv600_native_forward_opportunity.json`
- locked entries: `2`
- locked PnL: `+14c`
- best grid:
  `rv600_primary_max_3_entries_broad_70_600_ev0`
- best grid PnL: `+36c`
- best grid matched-v28 delta: `+84c`
- best grid average PnL per entry: `6.0c`
- best grid rejection:
  `fewer_than_25_entries;avg_entry_below_10c;positive_markets_below_60pct;single_market_share_above_25pct`

`RV600REV001` future-only state:

- forward roots after freeze: `6`
- accepted entries: `7`
- markets: `5`
- selected PnL: `-21c`
- matched-v28 delta: `-24c`
- average PnL per entry: `-3.0c`
- positive root rate: `0.1667`
- positive market rate: `0.2000`
- last-window PnL: `0c`
- rejection:
  `fewer_than_25_entries;nonpositive_pnl;avg_entry_below_10c;positive_roots_below_60pct;positive_markets_below_60pct;last_window_nonpositive;does_not_beat_matched_v28_by_20pct;no_fill_penalty_nonpositive`

Updated 31-root state:

- candidate rows: `24091`
- settled markets: `60`
- cumulative bounded audit:
  `cumulative_bounded_scored_with_entries`
- best cumulative grid:
  `rv600_primary_max_3_entries_broad_70_600_ev0`
- best cumulative grid entries: `141`
- best cumulative grid PnL: `+1593c`
- best cumulative grid matched-v28 delta: `+735c`
- best cumulative grid rejection:
  `positive_roots_below_60pct;positive_markets_below_60pct`

Refreshed 31-root anti-overfit state:

- failure-pattern audit:
  `no_current_plan_revision_supported`, `support_row_count=0`
- PBO:
  `pbo_rejects_current_grid`, `pbo=0.3594`, positive split rate `0.8711`
- reality check:
  `reality_check_rejects_current_grid`, best matched-v28 delta `+832c`,
  mean p-value `0.2677`, studentized p-value `0.3257`
- stability selection:
  `stability_selection_rescue_failed`, `full_support_count=0`,
  selected-test average entry `4.0589c`
- market balance:
  `market_balance_rescue_failed`, `gate_pass_rows=0`,
  `prequential_test_pnl_cents=+576c`,
  matched-v28 delta `-123c`
- regime filter:
  `regime_filter_rescue_failed`, `support_row_count=0`,
  `prequential_test_pnl_cents=+488c`,
  matched-v28 delta `-296c`
- group DRO:
  `group_dro_rescue_failed`, `support_row_count=0`,
  `prequential_test_pnl_cents=+692c`,
  matched-v28 delta `-272c`

Objective audit:

- report:
  `logs/particle_research/reports/rv600_objective_state_latest.json`
- decision:
  `blocked_not_complete`
- objective complete: `false`
- key blockers:
  `current_locked_family_rejected`,
  `no_existing_plan_family_viable`,
  `cumulative_bounded_shadow_insufficient`,
  `market_balance_rescue_failed`,
  `regime_filter_rescue_failed`,
  `group_dro_rescue_failed`,
  `pbo_stability_rejected`,
  `reality_check_rejected`,
  `stability_selection_rescue_failed`,
  `locked_plan_forward_audit_failed`

Updated verdict: the new root was positive but weak. It increased cumulative
PnL and matched-v28 delta, but the best cumulative grid still fails root and
market breadth; `RV600REV001` remains negative and sparse in future-only
accounting; and every anti-overfit rescue remains rejected. The goal remains
active and incomplete.

## Update: 32 Roots After Additional Forward Evidence

Collected one more read-only bounded shadow root:

- root:
  `logs/particle_research/real_shadow/rv600_next_evidence_shadow_20260515T113027Z`
- checkpoint rows: `832`
- independent spot rows: `3034`
- offline v28 contexts: `831`
- offline v28 context issues: `1`
- pipeline contexts: `831`
- labels written after delayed refresh: `2`
- label issues after refresh: `0`

Root score:

- report:
  `logs/particle_research/real_shadow/rv600_next_evidence_shadow_20260515T113027Z/rv600_native_forward_opportunity.json`
- locked entries: `2`
- locked PnL: `+47c`
- best grid:
  `rv600_primary_max_3_entries_late_70_180_ev8`
- best grid PnL: `+256c`
- best grid matched-v28 delta: `0c`
- best grid average PnL per entry: `85.3333c`
- best grid rejection:
  `fewer_than_25_entries;single_market_share_above_25pct;does_not_beat_matched_v28_by_20pct`

`RV600REV001` future-only state:

- forward roots after freeze: `7`
- accepted entries: `10`
- markets: `6`
- selected PnL: `+76c`
- matched-v28 delta: `-24c`
- average PnL per entry: `7.6c`
- positive root rate: `0.2857`
- positive market rate: `0.3333`
- max single-market PnL share: `1.2763`
- last-window PnL: `+97c`
- rejection:
  `fewer_than_25_entries;avg_entry_below_10c;positive_roots_below_60pct;positive_markets_below_60pct;single_market_share_above_25pct;does_not_beat_matched_v28_by_20pct`

Updated 32-root state:

- candidate rows: `24922`
- settled markets: `62`
- cumulative bounded audit:
  `cumulative_bounded_scored_with_entries`
- best cumulative grid:
  `rv600_primary_max_3_entries_broad_70_600_ev4`
- best cumulative grid entries: `118`
- best cumulative grid PnL: `+1664c`
- best cumulative grid matched-v28 delta: `+517c`
- best cumulative grid rejection:
  `positive_roots_below_60pct;positive_markets_below_60pct`

Refreshed 32-root anti-overfit state:

- failure-pattern audit:
  `no_current_plan_revision_supported`, `support_row_count=0`
- PBO:
  `pbo_rejects_current_grid`, `pbo=0.4570`, positive split rate `0.8359`
- reality check:
  `reality_check_rejects_current_grid`, best matched-v28 delta `+832c`,
  mean p-value `0.2677`, studentized p-value `0.3077`
- stability selection:
  `stability_selection_rescue_failed`, `full_support_count=0`,
  selected-test average entry `1.8709c`
- market balance:
  `market_balance_rescue_failed`, `gate_pass_rows=0`,
  `prequential_test_pnl_cents=+403c`,
  matched-v28 delta `-242c`
- regime filter:
  `regime_filter_rescue_failed`, `support_row_count=0`,
  `prequential_test_pnl_cents=+315c`,
  matched-v28 delta `-415c`
- group DRO:
  `group_dro_rescue_failed`, `support_row_count=0`,
  `prequential_test_pnl_cents=+519c`,
  matched-v28 delta `-391c`

Objective audit:

- report:
  `logs/particle_research/reports/rv600_objective_state_latest.json`
- decision:
  `blocked_not_complete`
- objective complete: `false`
- key blockers:
  `current_locked_family_rejected`,
  `no_existing_plan_family_viable`,
  `cumulative_bounded_shadow_insufficient`,
  `market_balance_rescue_failed`,
  `regime_filter_rescue_failed`,
  `group_dro_rescue_failed`,
  `pbo_stability_rejected`,
  `reality_check_rejected`,
  `stability_selection_rescue_failed`,
  `locked_plan_forward_audit_failed`

Updated verdict: this root was profitable, and `RV600REV001` recovered to
positive future-only PnL, but neither the frozen plan nor the best cumulative
grid clears the required gates. The remaining failures are not sample-size
only: breadth, concentration, matched-v28 edge, PBO, reality-check, and
stability-selection gates still reject the current RV600 families. The goal
remains active and incomplete.

## Parameter-Plateau Audit After 32 Roots

The current blocker is not a missing live sample command; it is parameter
fragility. High-PnL rows exist, but they do not survive root/market breadth
checks. Added a literature-backed local parameter-neighborhood audit that only
uses existing RV600 grid variants:

- script:
  `probe_rv600_parameter_plateau_audit.py`
- report:
  `logs/particle_research/reports/rv600_parameter_plateau_audit_latest.json`
- markdown:
  `logs/particle_research/reports/rv600_parameter_plateau_audit_latest.md`
- objective audit:
  `logs/particle_research/reports/rv600_objective_state_latest.json`

Modeling choice:

- use local timing-window and EV-threshold neighborhoods around existing
  position-capped RV600 variants
- require neighboring variants to keep positive PnL, positive matched-v28
  delta, and root/market breadth
- do not add a new broad live strategy family

Sources considered:

- selected:
  parameter-stability / robust-optimization plateau heuristic
- supporting:
  Probability of Backtest Overfitting / CSCV
- supporting:
  Model Confidence Set
- supporting:
  Stability Selection
- not selected as a new implementation:
  online expert weighting, because the existing online-expert rescue already
  covers that path

Result:

- decision:
  `parameter_plateau_rejected`
- support count: `0`
- root count: `32`
- variant count: `3948`
- position-capped parsed rows: `3780`
- best center:
  `rv600_primary_max_3_entries_base_70_420_ev0`
- best neighborhood positive PnL rate: `1.0000`
- best neighborhood positive matched-v28-delta rate: `1.0000`
- best neighborhood breadth-ok rate: `0.0000`
- median positive root rate: `0.4688`
- median positive market rate: `0.4292`
- top neighborhood rejection counts:
  `positive_roots_below_60pct=6; positive_markets_below_60pct=6; avg_entry_below_10c=2; single_market_share_above_25pct=2`

Updated objective-state blocker:

- `parameter_plateau_rejected`

Updated verdict: the strongest local parameter neighborhoods are profitable
and beat matched v28 in aggregate, but they are not broad or stable enough.
This rejects a new freeze from the current sample and supports the current
rule: continue only with materially new shadow evidence or a genuinely new,
documented RV600 clue before freezing another candidate.

## Update: Invalid Collection Attempts And 33rd Valid Root

Three attempted bounded read-only collections were reviewed before adding the
next valid root:

- `rv600_next_evidence_shadow_20260515T134212Z`
  - recorder succeeded with `779` checkpoint rows
  - Coinbase independent spot wrote `42748` ticks but recorded one reconnect
  - offline-v28 replay initially timed out on Coinbase REST; a manual retry
    wrote `778` contexts with one issue
  - the remaining offline issue was `checkpoint is not before settlement`
  - decision: not counted in cumulative evidence because the run manifest still
    records `offline_v28_returncode=1` and `independent_spot_issue_count=1`
- `rv600_next_evidence_shadow_20260515T140002Z`
  - recorder succeeded with `669` checkpoint rows
  - Coinbase independent spot recorded `7` reconnect issues
  - offline-v28 produced stale-spot gaps up to about `105s`
  - decision: invalid; not scored
- `rv600_next_evidence_shadow_20260515T141602Z`
  - attempted with `--independent-spot-feed binance`
  - Binance websocket returned repeated HTTP `451`
  - independent spot wrote `0` ticks and `150` issues
  - decision: invalid; not scored

Collected one clean read-only bounded shadow root:

- root:
  `logs/particle_research/real_shadow/rv600_next_evidence_shadow_20260515T143222Z`
- checkpoint rows: `846`
- independent Coinbase spot rows: `20224`
- independent spot issues: `0`
- offline v28 contexts: `843`
- offline v28 issues: `3`
- offline issue reason:
  `checkpoint is not before settlement`
- pipeline contexts: `809`
- pipeline context issues: `0`
- labels written after delayed refresh: `2`
- label issues after refresh: `0`

Root score:

- report:
  `logs/particle_research/real_shadow/rv600_next_evidence_shadow_20260515T143222Z/rv600_native_forward_opportunity.json`
- locked entries: `1`
- locked PnL: `-29c`
- best RV600-primary grid:
  `rv600_primary_single_market_late_70_180_ev10`
- best RV600-primary PnL: `0c`
- best RV600-primary rejection:
  `fewer_than_25_entries;nonpositive_pnl;avg_entry_below_10c;positive_roots_below_60pct;positive_markets_below_60pct;last_window_nonpositive;no_fill_penalty_nonpositive`

`RV600REV001` future-only state:

- forward roots after freeze: `8`
- accepted entries: `13`
- markets: `7`
- selected PnL: `-7c`
- matched-v28 delta: `-24c`
- average PnL per entry: `-0.5385c`
- positive root rate: `0.2500`
- positive market rate: `0.2857`
- last-window PnL: `-83c`
- rejection:
  `fewer_than_25_entries;nonpositive_pnl;avg_entry_below_10c;positive_roots_below_60pct;positive_markets_below_60pct;last_window_nonpositive;does_not_beat_matched_v28_by_20pct;no_fill_penalty_nonpositive`

Updated 33-root state:

- candidate rows: `25731`
- settled markets: `64`
- cumulative bounded audit:
  `cumulative_bounded_scored_with_entries`
- best cumulative grid:
  `rv600_primary_max_3_entries_broad_70_600_ev4`
- best cumulative grid entries: `121`
- best cumulative grid PnL: `+1576c`
- best cumulative grid matched-v28 delta: `+517c`
- best cumulative grid rejection:
  `positive_roots_below_60pct;positive_markets_below_60pct;last_window_nonpositive`

Refreshed 33-root anti-overfit state:

- failure-pattern audit:
  `no_current_plan_revision_supported`, `support_row_count=0`
- PBO:
  `pbo_rejects_current_grid`, `pbo=0.5293`, positive split rate `0.7949`
- reality check:
  `reality_check_rejects_current_grid`, best matched-v28 delta `+832c`,
  mean p-value `0.2557`, studentized p-value `0.3327`
- stability selection:
  `stability_selection_rescue_failed`, `full_support_count=0`,
  selected-test PnL `+706c`, selected-test average entry `0.2429c`
- market balance:
  `market_balance_rescue_failed`, `gate_pass_rows=0`,
  `prequential_test_pnl_cents=+315c`,
  matched-v28 delta `-242c`
- regime filter:
  `regime_filter_rescue_failed`, `support_row_count=0`,
  `prequential_test_pnl_cents=+227c`,
  matched-v28 delta `-415c`
- group DRO:
  `group_dro_rescue_failed`, `support_row_count=0`,
  `prequential_test_pnl_cents=+436c`,
  matched-v28 delta `-391c`
- parameter plateau:
  `parameter_plateau_rejected`, support count `0`,
  best median positive root rate `0.4545`,
  best median positive market rate `0.4170`

Objective audit:

- report:
  `logs/particle_research/reports/rv600_objective_state_latest.json`
- decision:
  `blocked_not_complete`
- objective complete: `false`
- added/active blockers:
  `parameter_plateau_rejected`,
  `locked_plan_forward_audit_failed`,
  `cumulative_bounded_shadow_insufficient`,
  `pbo_stability_rejected`,
  `reality_check_rejected`,
  `stability_selection_rescue_failed`

Updated verdict: the newest clean root materially weakened RV600. The frozen
revision flipped back negative, the best cumulative grid lost recent-window
support, PBO worsened above `0.50`, and the parameter plateau remains rejected.
No current RV600 family is eligible for freeze, promotion, or live testing.

## Update: 34 Roots After Additional Forward Evidence

Collected one more clean read-only bounded shadow root:

- root:
  `logs/particle_research/real_shadow/rv600_next_evidence_shadow_20260515T151536Z`
- checkpoint rows: `850`
- independent Coinbase spot rows: `10251`
- independent spot issues: `0`
- offline v28 contexts: `848`
- offline v28 issues: `2`
- offline issue reason:
  `checkpoint is not before settlement`
- pipeline contexts: `818`
- pipeline context issues: `0`
- labels written after delayed refresh: `2`
- label issues after refresh: `0`

Root score:

- report:
  `logs/particle_research/real_shadow/rv600_next_evidence_shadow_20260515T151536Z/rv600_native_forward_opportunity.json`
- locked entries: `1`
- locked PnL: `+70c`
- best grid:
  `blend_95_5_max_3_entries_broad_70_600_ev6`
- best grid PnL: `+236c`
- best grid rejection:
  `fewer_than_25_entries;single_market_share_above_25pct;does_not_beat_matched_v28_by_20pct`
- best RV600-primary grid:
  `rv600_primary_max_3_entries_broad_70_600_ev4`
- best RV600-primary PnL: `+231c`
- best RV600-primary rejection:
  `fewer_than_25_entries;single_market_share_above_25pct;does_not_beat_matched_v28_by_20pct`

`RV600REV001` future-only state:

- forward roots after freeze: `9`
- accepted entries: `16`
- markets: `8`
- selected PnL: `+110c`
- matched-v28 delta: `-24c`
- average PnL per entry: `6.875c`
- positive root rate: `0.3333`
- positive market rate: `0.3750`
- max single-market PnL share: `1.0636`
- last-window PnL: `+117c`
- rejection:
  `fewer_than_25_entries;avg_entry_below_10c;positive_roots_below_60pct;positive_markets_below_60pct;single_market_share_above_25pct;does_not_beat_matched_v28_by_20pct`

Updated 34-root state:

- candidate rows: `26549`
- settled markets: `66`
- cumulative bounded audit:
  `cumulative_bounded_scored_with_entries`
- best cumulative grid:
  `rv600_primary_max_3_entries_broad_70_600_ev4`
- best cumulative grid entries: `124`
- best cumulative grid PnL: `+1807c`
- best cumulative grid matched-v28 delta: `+517c`
- best cumulative grid rejection:
  `positive_roots_below_60pct;positive_markets_below_60pct`

Refreshed 34-root anti-overfit state:

- failure-pattern audit:
  `no_current_plan_revision_supported`, `support_row_count=0`
- PBO:
  `pbo_rejects_current_grid`, `pbo=0.4121`, positive split rate `0.8535`
- reality check:
  `reality_check_rejects_current_grid`, best matched-v28 delta `+832c`,
  mean p-value `0.2727`, studentized p-value `0.3497`
- stability selection:
  `stability_selection_rescue_failed`, `full_support_count=0`,
  selected-test PnL `+6599c`, selected-test average entry `1.2086c`
- market balance:
  `market_balance_rescue_failed`, `gate_pass_rows=0`,
  `prequential_test_pnl_cents=+546c`,
  matched-v28 delta `-242c`
- regime filter:
  `regime_filter_rescue_failed`, `support_row_count=0`,
  `prequential_test_pnl_cents=+458c`,
  matched-v28 delta `-415c`
- group DRO:
  `group_dro_rescue_failed`, `support_row_count=0`,
  `prequential_test_pnl_cents=+436c`,
  matched-v28 delta `-391c`
- parameter plateau:
  `parameter_plateau_rejected`, support count `0`,
  best median positive root rate `0.4706`,
  best median positive market rate `0.4330`

Objective audit:

- report:
  `logs/particle_research/reports/rv600_objective_state_latest.json`
- decision:
  `blocked_not_complete`
- objective complete: `false`
- active blockers include:
  `cumulative_bounded_shadow_insufficient`,
  `pbo_stability_rejected`,
  `reality_check_rejected`,
  `stability_selection_rescue_failed`,
  `parameter_plateau_rejected`,
  `locked_plan_forward_audit_failed`

Updated verdict: the new root helped raw PnL but did not change the conclusion.
The best cumulative grid still fails root and market breadth, the frozen
revision still loses to matched v28, and all anti-overfit checks remain
negative. No current RV600 family is eligible for freeze, promotion, or live
testing.

## Update: 35 Roots After Additional Forward Evidence

Collected one more clean read-only bounded shadow root:

- root:
  `logs/particle_research/real_shadow/rv600_next_evidence_shadow_20260515T160221Z`
- checkpoint rows: `837`
- independent Coinbase spot rows: `9359`
- independent spot issues: `0`
- offline v28 contexts: `835`
- offline v28 issues: `2`
- offline issue reason:
  `checkpoint is not before settlement`
- pipeline contexts: `824`
- pipeline context issues: `0`
- labels written after delayed refresh: `2`
- label issues after refresh: `0`

Root score:

- report:
  `logs/particle_research/real_shadow/rv600_next_evidence_shadow_20260515T160221Z/rv600_native_forward_opportunity.json`
- locked entries: `15`
- locked PnL: `-532c`
- best grid:
  `blend_90_10_same_side_ev_step_3c_late_70_240_ev0`
- best grid PnL: `+106c`
- best grid rejection:
  `fewer_than_25_entries;single_market_share_above_25pct;does_not_beat_matched_v28_by_20pct`
- best RV600-primary grid:
  `rv600_primary_single_market_late_70_180_ev20`
- best RV600-primary PnL: `0c`
- best RV600-primary rejection:
  `fewer_than_25_entries;nonpositive_pnl;avg_entry_below_10c;positive_roots_below_60pct;positive_markets_below_60pct;last_window_nonpositive;no_fill_penalty_nonpositive`

`RV600REV001` future-only state:

- forward roots after freeze: `10`
- accepted entries: `19`
- markets: `9`
- selected PnL: `-13c`
- matched-v28 delta: `-24c`
- average PnL per entry: `-0.6842c`
- positive root rate: `0.3000`
- positive market rate: `0.3333`
- last-window PnL: `-123c`
- rejection:
  `fewer_than_25_entries;nonpositive_pnl;avg_entry_below_10c;positive_roots_below_60pct;positive_markets_below_60pct;last_window_nonpositive;does_not_beat_matched_v28_by_20pct;no_fill_penalty_nonpositive`

Updated 35-root state:

- candidate rows: `27373`
- settled markets: `68`
- cumulative bounded audit:
  `cumulative_bounded_scored_with_entries`
- best cumulative grid:
  `rv600_primary_max_3_entries_broad_70_600_ev4`
- best cumulative grid entries: `127`
- best cumulative grid PnL: `+1682c`
- best cumulative grid matched-v28 delta: `+517c`
- best cumulative grid rejection:
  `positive_roots_below_60pct;positive_markets_below_60pct;last_window_nonpositive`

Refreshed 35-root anti-overfit state:

- failure-pattern audit:
  `no_current_plan_revision_supported`, `support_row_count=0`
- PBO:
  `pbo_rejects_current_grid`, `pbo=0.4551`, positive split rate `0.7969`
- reality check:
  `reality_check_rejects_current_grid`, best matched-v28 delta `+832c`,
  mean p-value `0.2527`, studentized p-value `0.3307`
- stability selection:
  `stability_selection_rescue_failed`, `full_support_count=0`,
  selected-test PnL `+389c`, selected-test average entry `0.1605c`
- market balance:
  `market_balance_rescue_failed`, `gate_pass_rows=0`,
  `prequential_test_pnl_cents=+421c`,
  matched-v28 delta `-242c`
- regime filter:
  `regime_filter_rescue_failed`, `support_row_count=0`,
  `prequential_test_pnl_cents=+333c`,
  matched-v28 delta `-415c`
- group DRO:
  `group_dro_rescue_failed`, `support_row_count=0`,
  `prequential_test_pnl_cents=+313c`,
  matched-v28 delta `-391c`
- parameter plateau:
  `parameter_plateau_rejected`, support count `0`,
  best median positive root rate `0.4571`,
  best median positive market rate `0.4214`

Objective audit:

- report:
  `logs/particle_research/reports/rv600_objective_state_latest.json`
- decision:
  `blocked_not_complete`
- objective complete: `false`

Updated verdict: this root materially weakened the live-shadow case. The
frozen revision is negative again, the best cumulative grid now also fails the
recent-window gate, and stability-selection selected-test average entry is
effectively zero. No current RV600 family is eligible for freeze, promotion, or
live testing.

## Update: 36 Roots After Additional Forward Evidence

Collected one more clean read-only bounded shadow root:

- root:
  `logs/particle_research/real_shadow/rv600_next_evidence_shadow_20260515T164836Z`
- checkpoint rows: `871`
- independent Coinbase spot rows: `7767`
- independent spot issues: `0`
- offline v28 contexts: `869`
- offline v28 issues: `2`
- offline issue reason:
  `checkpoint is not before settlement`
- pipeline contexts: `866`
- pipeline context issues: `0`
- labels written after delayed refresh: `2`
- label issues after refresh: `0`

Root score:

- report:
  `logs/particle_research/real_shadow/rv600_next_evidence_shadow_20260515T164836Z/rv600_native_forward_opportunity.json`
- locked entries: `8`
- locked PnL: `-111c`
- best grid:
  `blend_95_5_max_3_entries_base_70_420_ev4`
- best grid PnL: `+240c`
- best grid rejection:
  `fewer_than_25_entries;single_market_share_above_25pct;does_not_beat_matched_v28_by_20pct`
- best RV600-primary grid:
  `rv600_primary_max_2_entries_late_70_300_ev0`
- best RV600-primary PnL: `+142c`
- best RV600-primary rejection:
  `fewer_than_25_entries;single_market_share_above_25pct;does_not_beat_matched_v28_by_20pct`

`RV600REV001` future-only state:

- forward roots after freeze: `11`
- accepted entries: `22`
- markets: `10`
- selected PnL: `-142c`
- matched-v28 delta: `-159c`
- average PnL per entry: `-6.4545c`
- positive root rate: `0.2727`
- positive market rate: `0.3000`
- last-window PnL: `-129c`
- rejection:
  `fewer_than_25_entries;nonpositive_pnl;avg_entry_below_10c;positive_roots_below_60pct;positive_markets_below_60pct;last_window_nonpositive;does_not_beat_matched_v28_by_20pct;no_fill_penalty_nonpositive`

Updated 36-root state:

- candidate rows: `28239`
- settled markets: `70`
- cumulative bounded audit:
  `cumulative_bounded_scored_with_entries`
- locked cumulative entries: `281`
- locked cumulative PnL: `+4109c`
- best cumulative grid:
  `rv600_primary_max_3_entries_broad_70_600_ev4`
- best cumulative grid entries: `130`
- best cumulative grid PnL: `+1539c`
- best cumulative grid matched-v28 delta: `+517c`
- best cumulative grid rejection:
  `positive_roots_below_60pct;positive_markets_below_60pct;last_window_nonpositive`

Refreshed 36-root anti-overfit state:

- failure-pattern audit:
  `no_current_plan_revision_supported`, `support_row_count=0`
- PBO:
  `pbo_rejects_current_grid`, `pbo=0.4863`, positive split rate `0.7676`
- reality check:
  `reality_check_rejects_current_grid`, best matched-v28 delta `+788c`,
  mean p-value `0.3117`, studentized p-value `0.4496`
- stability selection:
  `stability_selection_rescue_failed`, `full_support_count=0`,
  selected-test PnL `-3878c`, selected-test matched-v28 delta `+452c`,
  selected-test average entry `-1.7398c`
- market balance:
  `market_balance_rescue_failed`, `gate_pass_rows=0`,
  `prequential_test_pnl_cents=+278c`,
  matched-v28 delta `-242c`
- regime filter:
  `regime_filter_rescue_failed`, `support_row_count=0`,
  `prequential_test_pnl_cents=+190c`,
  matched-v28 delta `-415c`
- group DRO:
  `group_dro_rescue_failed`, `support_row_count=0`,
  `prequential_test_pnl_cents=+205c`,
  matched-v28 delta `-526c`
- parameter plateau:
  `parameter_plateau_rejected`, support count `0`,
  best center `rv600_primary_max_3_entries_base_70_420_ev4`,
  best breadth-ok rate `0.0000`,
  best median positive root rate `0.3333`,
  best median positive market rate `0.4118`

Objective audit:

- report:
  `logs/particle_research/reports/rv600_objective_state_latest.json`
- decision:
  `blocked_not_complete`
- objective complete: `false`
- active blockers include:
  `cumulative_bounded_shadow_insufficient`,
  `pbo_stability_rejected`,
  `reality_check_rejected`,
  `stability_selection_rescue_failed`,
  `parameter_plateau_rejected`,
  `locked_plan_forward_audit_failed`

Updated verdict: the extra root did not rescue RV600. The frozen revision is
now negative across 11 future roots, the best cumulative grid remains positive
but fails breadth and recent-window gates, and the anti-overfit suite still
rejects every current rescue path. No current RV600 family is eligible for
freeze, promotion, or live testing.

## Update: 37 Roots After Additional Forward Evidence

Collected one more clean read-only bounded shadow root:

- root:
  `logs/particle_research/real_shadow/rv600_next_evidence_shadow_20260515T173507Z`
- checkpoint rows: `851`
- independent Coinbase spot rows: `7885`
- independent spot issues: `0`
- offline v28 contexts: `849`
- offline v28 issues: `2`
- offline issue reason:
  `checkpoint is not before settlement`
- pipeline contexts: `849`
- pipeline context issues: `0`
- labels written after delayed refresh: `2`
- label issues after refresh: `0`

Root score:

- report:
  `logs/particle_research/real_shadow/rv600_next_evidence_shadow_20260515T173507Z/rv600_native_forward_opportunity.json`
- locked entries: `16`
- locked PnL: `-500c`
- best grid:
  `blend_95_5_same_side_ev_step_5c_late_70_300_ev0`
- best grid PnL: `+134c`
- best grid rejection:
  `fewer_than_25_entries;single_market_share_above_25pct;does_not_beat_matched_v28_by_20pct`
- best RV600-primary grid:
  `rv600_primary_side_flip_only_late_70_300_ev0`
- best RV600-primary PnL: `+64c`
- best RV600-primary rejection:
  `fewer_than_25_entries;single_market_share_above_25pct;does_not_beat_matched_v28_by_20pct`

`RV600REV001` future-only state:

- forward roots after freeze: `12`
- accepted entries: `25`
- markets: `11`
- selected PnL: `-256c`
- matched-v28 delta: `-159c`
- average PnL per entry: `-10.2400c`
- positive root rate: `0.2500`
- positive market rate: `0.2727`
- last-window PnL: `-114c`
- rejection:
  `nonpositive_pnl;avg_entry_below_10c;positive_roots_below_60pct;positive_markets_below_60pct;last_window_nonpositive;no_fill_penalty_nonpositive`

Updated 37-root state:

- candidate rows: `29088`
- settled markets: `72`
- cumulative bounded audit:
  `cumulative_bounded_scored_with_entries`
- locked cumulative entries: `297`
- locked cumulative PnL: `+3609c`
- best cumulative grid:
  `rv600_primary_max_3_entries_broad_70_600_ev4`
- best cumulative grid entries: `133`
- best cumulative grid PnL: `+1507c`
- best cumulative grid matched-v28 delta: `+574c`
- best cumulative grid rejection:
  `positive_roots_below_60pct;positive_markets_below_60pct;last_window_nonpositive`

Refreshed 37-root anti-overfit state:

- failure-pattern audit:
  `no_current_plan_revision_supported`, `support_row_count=0`
- PBO:
  `pbo_rejects_current_grid`, `pbo=0.4668`, positive split rate `0.7402`
- reality check:
  `reality_check_rejects_current_grid`, best matched-v28 delta `+788c`,
  mean p-value `0.3506`, studentized p-value `0.4815`
- stability selection:
  `stability_selection_rescue_failed`, `full_support_count=0`,
  selected-test PnL `-3306c`, selected-test matched-v28 delta `-671c`,
  selected-test average entry `-3.0000c`
- market balance:
  `market_balance_rescue_failed`, `gate_pass_rows=0`,
  `prequential_test_pnl_cents=+237c`,
  matched-v28 delta `-242c`
- regime filter:
  `regime_filter_rescue_failed`, `support_row_count=0`,
  `prequential_test_pnl_cents=+158c`,
  matched-v28 delta `-358c`
- group DRO:
  `group_dro_rescue_failed`, `support_row_count=0`,
  `prequential_test_pnl_cents=+164c`,
  matched-v28 delta `-526c`
- parameter plateau:
  `parameter_plateau_rejected`, support count `0`,
  best center `rv600_primary_max_3_entries_base_70_420_ev4`,
  best breadth-ok rate `0.0000`,
  best median positive root rate `0.3243`,
  best median positive market rate `0.4000`

Objective audit:

- report:
  `logs/particle_research/reports/rv600_objective_state_latest.json`
- decision:
  `blocked_not_complete`
- objective complete: `false`
- active blockers include:
  `cumulative_bounded_shadow_insufficient`,
  `pbo_stability_rejected`,
  `reality_check_rejected`,
  `stability_selection_rescue_failed`,
  `parameter_plateau_rejected`,
  `locked_plan_forward_audit_failed`

Updated verdict: the 37th root materially worsened the RV600 case. The active
frozen revision is now both sample-incomplete and clearly negative after fees
and fills, while the best cumulative grid remains an unstable aggregate that
fails breadth and recent-window gates. No current RV600 family is eligible for
freeze, promotion, or live testing.

## Update: 38 Roots After Additional Forward Evidence

Collected one more clean read-only bounded shadow root:

- root:
  `logs/particle_research/real_shadow/rv600_next_evidence_shadow_20260515T182447Z`
- checkpoint rows: `814`
- independent Coinbase spot rows: `12586`
- independent spot issues: `0`
- offline v28 contexts: `811`
- offline v28 issues: `3`
- offline issue reason:
  `checkpoint is not before settlement`
- pipeline contexts: `744`
- pipeline context issues: `0`
- labels written after delayed refresh: `2`
- label issues after refresh: `0`

Root score:

- report:
  `logs/particle_research/real_shadow/rv600_next_evidence_shadow_20260515T182447Z/rv600_native_forward_opportunity.json`
- locked entries: `2`
- locked PnL: `+31c`
- best grid:
  `blend_95_5_max_3_entries_base_70_420_ev2`
- best grid PnL: `+168c`
- best grid rejection:
  `fewer_than_25_entries;single_market_share_above_25pct;does_not_beat_matched_v28_by_20pct`
- best RV600-primary grid:
  `rv600_primary_max_3_entries_base_70_420_ev2`
- best RV600-primary PnL: `+161c`
- best RV600-primary rejection:
  `fewer_than_25_entries;positive_markets_below_60pct;single_market_share_above_25pct;does_not_beat_matched_v28_by_20pct`

`RV600REV001` future-only state:

- forward roots after freeze: `13`
- accepted entries: `28`
- markets: `13`
- selected PnL: `-157c`
- matched-v28 delta: `-166c`
- average PnL per entry: `-5.6071c`
- positive root rate: `0.3077`
- positive market rate: `0.3077`
- last-window PnL: `+99c`
- rejection:
  `nonpositive_pnl;avg_entry_below_10c;positive_roots_below_60pct;positive_markets_below_60pct;does_not_beat_matched_v28_by_20pct;no_fill_penalty_nonpositive`

Updated 38-root state:

- candidate rows: `29832`
- settled markets: `74`
- cumulative bounded audit:
  `cumulative_bounded_scored_with_entries`
- locked cumulative entries: `299`
- locked cumulative PnL: `+3640c`
- best cumulative grid:
  `rv600_primary_max_3_entries_broad_70_600_ev4`
- best cumulative grid entries: `137`
- best cumulative grid PnL: `+1609c`
- best cumulative grid matched-v28 delta: `+569c`
- best cumulative grid rejection:
  `positive_roots_below_60pct;positive_markets_below_60pct`

Refreshed 38-root anti-overfit state:

- failure-pattern audit:
  `no_current_plan_revision_supported`, `support_row_count=0`
- PBO:
  `pbo_rejects_current_grid`, `pbo=0.4082`, positive split rate `0.7969`
- reality check:
  `reality_check_rejects_current_grid`, best matched-v28 delta `+788c`,
  mean p-value `0.3357`, studentized p-value `0.4685`
- stability selection:
  `stability_selection_rescue_failed`, `full_support_count=0`,
  selected-test PnL `-2412c`, selected-test matched-v28 delta `+1746c`,
  selected-test average entry `-1.5208c`
- market balance:
  `market_balance_rescue_failed`, `gate_pass_rows=0`,
  positive both-balance rows `3`,
  `prequential_test_pnl_cents=+339c`,
  matched-v28 delta `-247c`
- regime filter:
  `regime_filter_rescue_failed`, `support_row_count=0`,
  `prequential_test_pnl_cents=+260c`,
  matched-v28 delta `-363c`
- group DRO:
  `group_dro_rescue_failed`, `support_row_count=0`,
  `prequential_test_pnl_cents=+261c`,
  matched-v28 delta `-538c`
- parameter plateau:
  `parameter_plateau_rejected`, support count `0`,
  best center `rv600_primary_max_3_entries_base_70_420_ev6`,
  best breadth-ok rate `0.0000`,
  best median positive root rate `0.2895`,
  best median positive market rate `0.3793`

Objective audit:

- report:
  `logs/particle_research/reports/rv600_objective_state_latest.json`
- decision:
  `blocked_not_complete`
- objective complete: `false`
- active blockers include:
  `cumulative_bounded_shadow_insufficient`,
  `pbo_stability_rejected`,
  `reality_check_rejected`,
  `stability_selection_rescue_failed`,
  `parameter_plateau_rejected`,
  `locked_plan_forward_audit_failed`

Updated verdict: the 38th root was directionally helpful but not enough. It
removed the best cumulative grid's recent-window blocker, but the core breadth
problem remains, and the active frozen revision is still negative after
fee/fill accounting and still behind matched v28. No current RV600 family is
eligible for freeze, promotion, or live testing.

## Update: 39 Roots After Additional Forward Evidence

Collected one more clean read-only bounded shadow root:

- root:
  `logs/particle_research/real_shadow/rv600_next_evidence_shadow_20260515T190705Z`
- checkpoint rows: `813`
- independent Coinbase spot rows: `10088`
- independent spot issues: `0`
- offline v28 contexts: `810`
- offline v28 issues: `3`
- offline issue reason:
  `checkpoint is not before settlement`
- pipeline contexts: `795`
- pipeline context issues: `0`
- labels written after delayed refresh: `2`
- label issues after refresh: `0`

Root score:

- report:
  `logs/particle_research/real_shadow/rv600_next_evidence_shadow_20260515T190705Z/rv600_native_forward_opportunity.json`
- locked entries: `3`
- locked PnL: `-46c`
- best grid:
  `rv600_primary_max_3_entries_base_70_420_ev0`
- best grid PnL: `+27c`
- best grid rejection:
  `fewer_than_25_entries;avg_entry_below_10c;single_market_share_above_25pct;does_not_beat_matched_v28_by_20pct`
- best RV600-primary grid:
  `rv600_primary_max_3_entries_base_70_420_ev0`
- best RV600-primary PnL: `+27c`
- best RV600-primary rejection:
  `fewer_than_25_entries;avg_entry_below_10c;single_market_share_above_25pct;does_not_beat_matched_v28_by_20pct`

`RV600REV001` future-only state:

- forward roots after freeze: `14`
- accepted entries: `29`
- markets: `14`
- selected PnL: `-148c`
- matched-v28 delta: `-166c`
- average PnL per entry: `-5.1034c`
- positive root rate: `0.3571`
- positive market rate: `0.3571`
- last-window PnL: `+9c`
- rejection:
  `nonpositive_pnl;avg_entry_below_10c;positive_roots_below_60pct;positive_markets_below_60pct;does_not_beat_matched_v28_by_20pct;no_fill_penalty_nonpositive`

Updated 39-root state:

- candidate rows: `30627`
- settled markets: `76`
- cumulative bounded audit:
  `cumulative_bounded_scored_with_entries`
- locked cumulative entries: `302`
- locked cumulative PnL: `+3594c`
- best cumulative grid:
  `blend_90_10_max_3_entries_base_70_420_ev4`
- best cumulative grid entries: `97`
- best cumulative grid PnL: `+1609c`
- best cumulative grid matched-v28 delta: `0c`
- best cumulative grid rejection:
  `positive_roots_below_60pct;positive_markets_below_60pct;does_not_beat_matched_v28_by_20pct`

Refreshed 39-root anti-overfit state:

- failure-pattern audit:
  `no_current_plan_revision_supported`, `support_row_count=0`
- PBO:
  `pbo_rejects_current_grid`, `pbo=0.4336`, positive split rate `0.7617`
- reality check:
  `reality_check_rejects_current_grid`, best matched-v28 delta `+788c`,
  mean p-value `0.3417`, studentized p-value `0.4755`
- stability selection:
  `stability_selection_rescue_failed`, `full_support_count=0`,
  selected-test PnL `-5149c`, selected-test matched-v28 delta `-2237c`,
  selected-test average entry `-3.1843c`
- market balance:
  `market_balance_rescue_failed`, `gate_pass_rows=0`,
  positive both-balance rows `6`,
  `prequential_test_pnl_cents=+198c`,
  matched-v28 delta `-288c`
- regime filter:
  `regime_filter_rescue_failed`, `support_row_count=0`,
  `prequential_test_pnl_cents=+119c`,
  matched-v28 delta `-404c`
- group DRO:
  `group_dro_rescue_failed`, `support_row_count=0`,
  `prequential_test_pnl_cents=+267c`,
  matched-v28 delta `-538c`
- parameter plateau:
  `parameter_plateau_rejected`, support count `0`,
  best center `rv600_primary_max_3_entries_base_70_420_ev6`,
  best breadth-ok rate `0.0000`,
  best median positive root rate `0.2821`,
  best median positive market rate `0.4000`

Objective audit:

- report:
  `logs/particle_research/reports/rv600_objective_state_latest.json`
- decision:
  `blocked_not_complete`
- objective complete: `false`
- active blockers include:
  `cumulative_bounded_shadow_insufficient`,
  `pbo_stability_rejected`,
  `reality_check_rejected`,
  `stability_selection_rescue_failed`,
  `parameter_plateau_rejected`,
  `locked_plan_forward_audit_failed`

Updated verdict: the 39th root weakened the picture again. The best cumulative
row is now a conservative v28/RV600 blend with zero matched-v28 delta, so it is
not an RV600 edge under the spec. Breadth remains below the required bar and the
active frozen revision remains negative. No current RV600 family is eligible for
freeze, promotion, or live testing.

## Update: SPA Benchmark Audit After 39 Roots

Modeling blocker addressed: after 39 valid bounded shadow roots, some searched
RV600 rows still show positive raw PnL, but the candidates fail breadth gates and
do not establish a durable edge over matched v28 controls. I searched for
multiple-comparison and benchmark-comparison approaches and implemented a
Hansen-style superior-predictive-ability benchmark audit because it directly
tests whether any searched RV600 variant beats the matched v28 benchmark after
root-block bootstrap adjustment.

Sources considered:

- Hansen SPA test:
  <https://papers.ssrn.com/sol3/papers.cfm?abstract_id=264569>
- White Reality Check:
  <https://www.fmg.ac.uk/publications/discussion-papers/data-snooping-technical-trading-rule-performance-and-bootstrap>
- False-discovery-rate treatment of trading rules:
  <https://papers.ssrn.com/sol3/Delivery.cfm/SSRN_ID1095202_code517200.pdf?abstractid=1095202>
- Bayesian backtest overfitting:
  <https://www.mdpi.com/2227-9091/9/1/18>
- Hierarchical partial pooling:
  <https://mc-stan.org/rstanarm/articles/pooling.html>

Implemented:

- script:
  `probe_rv600_spa_benchmark_audit.py`
- report:
  `logs/particle_research/reports/rv600_spa_benchmark_audit_latest.json`
- objective-audit integration:
  `logs/particle_research/reports/rv600_objective_state_latest.json`

SPA result:

- decision:
  `spa_benchmark_rejects_current_grid`
- roots:
  `39`
- candidate count:
  `7343`
- positive matched-v28 delta candidates:
  `2854`
- candidates clearing the SPA screen plus normal RV600 gates:
  `0`
- best SPA-stat variant:
  `rv600_primary_max_2_entries_late_70_240_ev0`
- best SPA-stat matched-v28 delta:
  `+280c`
- best SPA-stat studentized p-value:
  `0.3956043956043956`
- best SPA-stat rejection:
  `avg_entry_below_10c;positive_roots_below_60pct;positive_markets_below_60pct;single_market_share_above_25pct;last_window_nonpositive`
- best raw matched-v28 delta:
  `+788c`
- best raw matched-v28 delta rejection:
  `avg_entry_below_10c;positive_roots_below_60pct;positive_markets_below_60pct;single_market_share_above_25pct;last_window_nonpositive`

Updated objective audit:

- decision:
  `blocked_not_complete`
- objective complete:
  `false`
- new explicit blocker:
  `spa_benchmark_rejected`

Verdict: the SPA audit rejects the current RV600 grid. The apparent positive
deltas are not enough after repeated-search adjustment and the normal
anti-overfitting gates. No current RV600 family is complete or eligible for
freeze, promotion, or live testing.

## Update: 40 Roots After Additional Forward Evidence

Collected one more clean read-only bounded shadow root:

- root:
  `logs/particle_research/real_shadow/rv600_next_evidence_shadow_20260515T200306Z`
- checkpoint rows:
  `868`
- independent Coinbase spot rows:
  `6406`
- independent spot issues:
  `0`
- offline v28 contexts:
  `865`
- offline v28 issues:
  `3`
- offline issue reason:
  `checkpoint is not before settlement`
- pipeline contexts:
  `853`
- pipeline context issues:
  `0`
- labels written after delayed refresh:
  `2`
- label issues after refresh:
  `0`

Root score:

- report:
  `logs/particle_research/real_shadow/rv600_next_evidence_shadow_20260515T200306Z/rv600_native_forward_opportunity.json`
- locked entries:
  `2`
- locked PnL:
  `+40c`
- best grid:
  `rv600_primary_max_3_entries_broad_70_600_ev0`
- best grid PnL:
  `+204c`
- best grid rejection:
  `fewer_than_25_entries;single_market_share_above_25pct;does_not_beat_matched_v28_by_20pct`
- best RV600-primary grid:
  `rv600_primary_max_3_entries_broad_70_600_ev0`
- best RV600-primary PnL:
  `+204c`
- best RV600-primary rejection:
  `fewer_than_25_entries;single_market_share_above_25pct;does_not_beat_matched_v28_by_20pct`

Updated cumulative bounded state:

- roots:
  `40`
- candidate rows:
  `31480`
- settled markets:
  `78`
- cumulative bounded audit:
  `cumulative_bounded_scored_with_entries`
- locked cumulative entries:
  `304`
- locked cumulative PnL:
  `+3634c`
- best cumulative grid:
  `blend_90_10_max_3_entries_base_70_420_ev4`
- best cumulative grid entries:
  `100`
- best cumulative grid PnL:
  `+1700c`
- best cumulative grid matched-v28 delta:
  `0c`
- best cumulative grid rejection:
  `positive_roots_below_60pct;positive_markets_below_60pct;does_not_beat_matched_v28_by_20pct`

Updated locked-plan forward state:

- report:
  `logs/particle_research/reports/rv600_locked_plan_forward_audit_latest.json`
- future roots:
  `18`
- accepted entries:
  `31`
- selected PnL:
  `+133c`
- average PnL per entry:
  `4.2903c`
- rejection:
  `avg_entry_below_10c;positive_roots_below_60pct;positive_markets_below_60pct;single_market_share_above_25pct;does_not_beat_matched_v28_by_20pct`

Refreshed 40-root anti-overfit state:

- failure-pattern audit:
  `no_current_plan_revision_supported`, `support_row_count=0`
- PBO:
  `pbo_rejects_current_grid`, `pbo=0.3574`, positive split rate `0.8047`
- reality check:
  `reality_check_rejects_current_grid`, best matched-v28 delta `+750c`,
  studentized p-value `0.7023`
- SPA benchmark:
  `spa_benchmark_rejects_current_grid`, candidate count `7482`,
  positive matched-v28 delta candidates `2890`,
  SPA-screen candidates `0`, studentized p-value `0.5295`
- stability selection:
  `stability_selection_rescue_failed`, `full_support_count=0`,
  selected-test PnL `-8458c`
- market balance:
  `market_balance_rescue_failed`, `gate_pass_rows=0`,
  `prequential_test_pnl_cents=+236c`
- regime filter:
  `regime_filter_rescue_failed`, `support_row_count=0`,
  `prequential_test_pnl_cents=+157c`,
  matched-v28 delta `-404c`
- group DRO:
  `group_dro_rescue_failed`, `support_row_count=0`,
  `prequential_test_pnl_cents=+240c`
- parameter plateau:
  `parameter_plateau_rejected`, support count `0`,
  best center `rv600_primary_max_3_entries_mid_120_420_ev4`,
  best breadth-ok rate `0.0000`
- meta-label, probability-calibration, conformal-abstention, and online-expert
  rescues:
  `no_train_gate_selection`

Objective audit:

- report:
  `logs/particle_research/reports/rv600_objective_state_latest.json`
- decision:
  `blocked_not_complete`
- objective complete:
  `false`
- active blockers include:
  `cumulative_bounded_shadow_insufficient`,
  `pbo_stability_rejected`,
  `reality_check_rejected`,
  `spa_benchmark_rejected`,
  `stability_selection_rescue_failed`,
  `parameter_plateau_rejected`,
  `locked_plan_forward_audit_failed`

Updated verdict: the 40th root helped the locked-plan raw PnL, but not the
actual completion case. Cumulative PnL remains positive, yet the leading row is
still a blend with zero matched-v28 delta and breadth below spec. The frozen
forward plan is positive but too sparse, too concentrated, below the average
entry threshold, and not better than matched v28. No current RV600 family is
complete or eligible for freeze, promotion, or live testing.

## Update: Repeated-Entry Gate Hardening After 40 Roots

Plan-coverage audit found a harness gap: the RV600 variation harness reported
added-entry metrics for all accounting modes, but summary-level repeated-entry
hard gates were only enforced for `all_entries`. Locked candidates are chosen
from non-`all_entries` modes, so `one_per_side_per_market` or `position_capped`
rows could theoretically become eligible without proving the plan's repeated
entry requirements against a matching single-market benchmark.

Implemented research-only hardening:

- updated:
  `research_particle/rv600_variation_test.py`
- repeated-entry summary gates now apply to repeated-entry variants across
  `all_entries`, `one_per_side_per_market`, and `position_capped`
- added-entry count/PnL now come from the accounting mode being summarized,
  not from uncapped `all_entries`
- repeated variants now require a matching single-market benchmark when one is
  available, with fallback to the original `rv600_single_70_420_ev10` benchmark
- locked-candidate eligibility now requires the repeated-entry gate to pass for
  repeated-entry variants
- updated:
  `probe_rv600_locked_plan_forward_audit.py`
- locked-plan forward audit now evaluates the frozen repeated-entry plan and its
  matching single-market benchmark in the same future-only window

Regression coverage:

- added test:
  `test_rv600_summary_blocks_repeated_entry_variants_with_negative_added_value`
- verified:
  `python -m py_compile .\research_particle\rv600_variation_test.py .\test_research_particle_synthetic.py .\probe_rv600_locked_plan_forward_audit.py`
- verified:
  `python -m unittest test_research_particle_synthetic.ResearchParticleSyntheticTests.test_rv600_summary_blocks_repeated_entry_variants_with_negative_added_value`
- verified:
  `python -m unittest test_research_particle_synthetic.ResearchParticleSyntheticTests.test_rv600_variation_test_accounts_for_repeated_entries_and_matched_v28`

After rescoring the 40-root state:

- cumulative locked PnL remains:
  `+3634c`
- best cumulative grid remains:
  `blend_90_10_max_3_entries_base_70_420_ev4`
- best cumulative grid PnL remains:
  `+1700c`
- best cumulative grid rejection now additionally includes:
  `market_drawdown_worse_than_25pct`
- locked-plan future-only audit remains:
  `locked_plan_forward_incomplete_or_failed`
- locked-plan future-only entries:
  `31`
- locked-plan future-only selected PnL:
  `+133c`
- locked-plan future-only average PnL per entry:
  `4.2903c`
- locked-plan future-only rejection:
  `avg_entry_below_10c;positive_roots_below_60pct;positive_markets_below_60pct;single_market_share_above_25pct;does_not_beat_matched_v28_by_20pct`
- PBO, reality check, and SPA benchmark still reject the 40-root grid
- failure-pattern audit remains:
  `no_current_plan_revision_supported`, `support_row_count=0`
- objective audit remains:
  `blocked_not_complete`

Updated verdict: this was a gate-correctness improvement, not a performance
breakthrough. It makes the repeated-entry standard stricter and closer to the
plan, and the current RV600 evidence remains insufficient for completion,
freeze, promotion, or live testing.
