# v28 Successor Live P&L Policy Score

Research-only score for the first inspectable live-P&L policy layer.

- Score status: `scored`
- Joined rows: `16302`
- Primary rows after policy hash: `314`
- No retroactive credit enforced: `True`

| slice | rows | markets | entered | net cents | v28 net | successor net | book net | skip net | delta vs v28 | max drawdown |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `all_joined_rows` | 16302 | 189 | 37 | 260.000000 | -36094.400000 | -38668.400000 | 0.000000 | 0.000000 | 36354.400000 | 481.000000 |
| `primary_live_forward_rows_after_policy_hash` | 314 | 12 | 3 | 70.000000 | -692.300000 | -1198.600000 | 0.000000 | 0.000000 | 762.300000 | 0.000000 |
| `diagnostic_rows_not_primary_credit` | 15988 | 189 | 34 | 190.000000 | -35402.100000 | -37469.800000 | 0.000000 | 0.000000 | 35592.100000 | 481.000000 |

Rows in `diagnostic_rows_not_primary_credit` are deliberately not proof of a forward policy edge when they predate the policy hash.
