# v28 Value Exit / Feature-Gate Contrast

Research-only contrast. No live bot changes or orders.

- Generated UTC: `2026-05-11T01:55:00.727701+00:00`
- Feature candidate: `post_feature_freeze_entry_raw03_recross70_abs075`
- Value-exit variant: `value_only_gap15_or_p75`

## Interpretation

- Research-only contrast; no live bot changes or orders.
- Feature-gate side agreement is an observable guard: it uses the feature-gate selected side, not settlement outcome, to decide whether a value-over-hold exit belongs to the same thesis.
- Post-birth value-only net 240.0c versus feature-side-guard net 348.0c.
- Suppressed loser cost under value-only was -350.0c; the key test is whether feature-side agreement filters that loser without deleting too much winner recovery.

## Lanes

| lane | rows | value net c | guarded net c | guarded delta vs value c | value W/L | guarded W/L | suppressed | sup W/L | sup loser cost c | feature class counts |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| `diagnostic_from_book_gap_freeze` | 120 | 787.00 | 771.00 | -16.00 | 69/51 | 70/50 | 37 | 35/2 | -350.00 | `{'no_feature_gate_row': 13, 'feature_gate_same_side': 19, 'feature_gate_opposite_side': 5}` |
| `post_value_only_birth` | 54 | 240.00 | 348.00 | 108.00 | 33/21 | 34/20 | 18 | 16/2 | -350.00 | `{'feature_gate_opposite_side': 4, 'feature_gate_same_side': 14}` |

## Suppressed Losers

| lane | market | value side | result | feature side | feature class | value delta c | guarded delta c | p_hold | exit bid | raw edge | recross | abs d | ask |
|---|---|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| `diagnostic_from_book_gap_freeze` | KXBTC15M-26MAY062015-15 | yes | no | no | feature_gate_opposite_side | -180.00 | 0.00 | 0.81 | 0.90 | 0.45 | 0.09 | 0.92 | 0.42 |
| `diagnostic_from_book_gap_freeze` | KXBTC15M-26MAY071100-00 | yes | no | yes | feature_gate_same_side | -170.00 | -170.00 | 0.84 | 0.85 | 0.05 | 0.31 | 1.01 | 0.83 |
| `post_value_only_birth` | KXBTC15M-26MAY062015-15 | yes | no | no | feature_gate_opposite_side | -180.00 | 0.00 | 0.81 | 0.90 | 0.45 | 0.09 | 0.92 | 0.42 |
| `post_value_only_birth` | KXBTC15M-26MAY071100-00 | yes | no | yes | feature_gate_same_side | -170.00 | -170.00 | 0.84 | 0.85 | 0.05 | 0.31 | 1.01 | 0.83 |
