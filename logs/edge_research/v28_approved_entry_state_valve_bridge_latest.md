# v28 Approved-Entry State Valve Bridge

Research-only bridge; no live bot changes or orders.

- Live baseline net: `1157.000000c`
- Positive approved-only frozen valves: `2`
- Promotion-ready valves: `False`

## Interpretation

- 2 approved-entry-only frozen valve(s) are positive versus approved-entry control.
- No valve is promotion-ready from this bridge because the validation surface is approved-entry-only and not yet in candidate-vs-live/live-readiness gates.
- The strongest immediate research action is a full-surface replay/adapter, not a live change.

## Gate Bridge

| valve | policy | settled | W/L | approved cov | gross c | delta vs approved control | naive delta vs live | skipped | source share | cushion gross/delta | in candidate-vs-live | promotion ready | blockers |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|---|---|
| `danger_zone_entry_valve` | `skip_reentry_gap15_or_gap30` | 110 | 98/12 | 100.000000% | 745.000000 | 258.000000 | -412.000000 | 8 | 0.000000 | 7/2 | False | False | approved_surface_coverage_above_90_not_broad_strategy_comparable, delta_full_loss_cushion_lt_3, not_in_candidate_vs_live_table, approved_entry_surface_only_not_full_strategy_surface, live_readiness_not_evaluated_for_valve, does_not_beat_live_on_naive_cents_comparison |
| `approved_entry_state_valve` | `same_side_reentry_gap_lte_15pp` | 114 | 101/13 | 100.000000% | 657.000000 | 180.000000 | -500.000000 | 6 | 0.000000 | 6/1 | False | False | approved_surface_coverage_above_90_not_broad_strategy_comparable, delta_full_loss_cushion_lt_3, not_in_candidate_vs_live_table, approved_entry_surface_only_not_full_strategy_surface, live_readiness_not_evaluated_for_valve, does_not_beat_live_on_naive_cents_comparison |

## Skipped Examples

### danger_zone_entry_valve
- `KXBTC15M-26MAY060330-30` `no` won `False`, gross/hold `-18/-18`, gap `0.909788`, same-side idx `0`
- `KXBTC15M-26MAY060800-00` `yes` won `True`, gross/hold `-32/68`, gap `0.214265`, same-side idx `1`
- `KXBTC15M-26MAY060945-45` `no` won `True`, gross/hold `-16/60`, gap `0.150231`, same-side idx `1`
- `KXBTC15M-26MAY060945-45` `no` won `True`, gross/hold `-12/58`, gap `0.151162`, same-side idx `2`
- `KXBTC15M-26MAY061015-15` `no` won `True`, gross/hold `0/60`, gap `0.155860`, same-side idx `1`
- `KXBTC15M-26MAY062015-15` `no` won `True`, gross/hold `-60/116`, gap `0.451622`, same-side idx `0`
- `KXBTC15M-26MAY062015-15` `yes` won `False`, gross/hold `-134/-134`, gap `0.215657`, same-side idx `1`
- `KXBTC15M-26MAY062100-00` `yes` won `True`, gross/hold `14/78`, gap `0.242359`, same-side idx `2`

## Next Steps

- Keep both valves research-only; they validate actual approved entries only.
- Before tracker integration, build a full-surface replay that computes market coverage against the same denominator used by broad entry lanes.
- Compare the valve output to current live-only baseline, source-quality gates, full-loss cushion, and live-readiness gates in one candidate row.
- Inspect skipped winners separately; danger-zone skips include some winners, so the physical rule must prove it removes more exit/state churn than upside.
