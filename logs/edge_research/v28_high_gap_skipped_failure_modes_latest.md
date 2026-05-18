# v28 High-Gap Skipped Failure Modes

Research-only forensic readout; no live bot changes or orders.

- Input report: `C:\Users\organ\Desktop\KALSHI PROBABILITY MODEL BOT\logs\edge_research\v28_approved_entry_state_valve_full_surface_latest.json`
- Unique skipped rows: `5`
- W/L: `1/4`
- Net of skipped rows: `-65.000000c`
- Loss net / winner net: `-206.000000c` / `141.000000c`

## Interpretation

- The saved full-surface valve adapter has only 5 unique skipped high-gap rows, so this is mechanism evidence, not a candidate score.
- Skipping them would have improved the broad adapter by 65.0c because 4 losers summed to -206.0c while 1 winner summed to 141.0c.
- All skipped rows are rejected-actionable, so the dominant failure family remains source-quality plus FV/book dislocation, not approved-entry live behavior.
- The single +141c skipped winner is the important fragility warning: a hard high-gap cutoff can remove large right-tail wins even when the small sample is net helpful.

## Failure Buckets

- Mode counts: `{'source_quality_error': 5, 'fv_overconfidence_or_book_dislocation': 5, 'fv_error_side_lost_despite_large_edge': 4, 'entry_timing_first_touch_not_reentry': 5, 'fragility_error_hard_cutoff_misses_right_tail': 1}`
- Gap buckets: `{'gap_35_40pp': 2, 'gap_30_35pp': 3}`
- Ask buckets: `{'ask_lt_20c': 1, 'ask_20_30c': 3, 'ask_30_40c': 1}`
- Source counts: `{'rejected_actionable': 5}`
- Side counts: `{'no': 3, 'yes': 2}`

## Rows

| market | side | source | won | net c | p_side | ask | gap | failure modes |
|---|---|---|---:|---:|---:|---:|---:|---|
| `KXBTC15M-26MAY061745-45` | `no` | `rejected_actionable` | False | -30.000000 | 0.510383 | 0.140000 | 0.370383 | source_quality_error, fv_overconfidence_or_book_dislocation, fv_error_side_lost_despite_large_edge, entry_timing_first_touch_not_reentry |
| `KXBTC15M-26MAY061830-30` | `yes` | `rejected_actionable` | False | -49.000000 | 0.553162 | 0.230000 | 0.323162 | source_quality_error, fv_overconfidence_or_book_dislocation, fv_error_side_lost_despite_large_edge, entry_timing_first_touch_not_reentry |
| `KXBTC15M-26MAY062100-00` | `no` | `rejected_actionable` | False | -47.000000 | 0.615588 | 0.220000 | 0.395588 | source_quality_error, fv_overconfidence_or_book_dislocation, fv_error_side_lost_despite_large_edge, entry_timing_first_touch_not_reentry |
| `KXBTC15M-26MAY062230-30` | `yes` | `rejected_actionable` | False | -80.000000 | 0.718015 | 0.380000 | 0.338015 | source_quality_error, fv_overconfidence_or_book_dislocation, fv_error_side_lost_despite_large_edge, entry_timing_first_touch_not_reentry |
| `KXBTC15M-26MAY070615-15` | `no` | `rejected_actionable` | True | 141.000000 | 0.610872 | 0.280000 | 0.330872 | source_quality_error, fv_overconfidence_or_book_dislocation, fragility_error_hard_cutoff_misses_right_tail, entry_timing_first_touch_not_reentry |

## Limits

- Uses saved adapter skipped rows only; it does not rebuild selected/base rows.
- No exit-path fields are present here, so exit-policy error cannot be directly scored.
- No live-readiness or promotion gate is evaluated by this forensic probe.

## Next Research Implication

Treat high raw/book gap on rejected-actionable rows as a continuous confidence/shrinkage input, not as a promotable hard veto. A useful next candidate would need to test a soft penalty across the full surface with strict forward freeze, source-share control, and explicit tail-winner cost accounting.
