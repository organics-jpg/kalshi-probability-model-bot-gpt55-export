# v28 Top Observable Stack Coverage Gap

Research-only; no live bot changes or orders.

- Generated UTC: `2026-05-11T02:53:25.494665+00:00`
- Freeze UTC: `2026-05-07T10:29:46.104521+00:00`
- Future denominator: `28`
- Future observation rows: `1157`
- Selected settled/pending rows: `24/0`
- Missing predicate counts on gap markets: `{}`

## Coverage Gap Markets

| market | best side | source | won | pass count | missing | raw edge | recross | abs d | ask |
|---|---|---|---|---:|---|---:|---:|---:|---:|

## Selected Markets

| market | best side | source | won | pass count | raw edge | recross | abs d | ask |
|---|---|---|---|---:|---:|---:|---:|---:|
| KXBTC15M-26MAY070745-45 | yes | approved_entry | True | 4 | 0.224 | 0.198 | 1.081 | 0.680 |
| KXBTC15M-26MAY070830-30 | no | approved_entry | True | 4 | 0.120 | 0.127 | 1.007 | 0.770 |
| KXBTC15M-26MAY070915-15 | no | approved_entry | True | 4 | 0.107 | 0.284 | 0.951 | 0.770 |
| KXBTC15M-26MAY070945-45 | no | approved_entry | True | 4 | 0.164 | 0.436 | 0.883 | 0.690 |
| KXBTC15M-26MAY071000-00 | no | approved_entry | True | 4 | 0.142 | 0.484 | 0.895 | 0.710 |
| KXBTC15M-26MAY071045-45 | no | approved_entry | True | 4 | 0.115 | 0.470 | 0.954 | 0.750 |
| KXBTC15M-26MAY071215-15 | yes | rejected_actionable | False | 4 | 0.108 | 0.488 | 0.791 | 0.720 |

## Interpretation

- Research-only coverage-gap audit; no live bot changes or orders.
- Early strict coverage is thin because only one of the first two forward markets passed the broad observable parent rule.
- The current missing market is not settled yet, so it is not evidence to relax predicates.
- If this pattern repeats after settlement, recross and abs-d are the first predicate failures to inspect.
