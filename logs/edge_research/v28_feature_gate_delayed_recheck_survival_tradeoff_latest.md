# v28 Feature-Gate Delayed-Recheck Survival Tradeoff

Research-only consolidation. No live bot changes, no orders, no new candidate rule.

- Generated UTC: `2026-05-07T08:41:43.599403+00:00`

## Summary

| set | rows | delta vs live | adverse 10/25/50 | worst min-after-exit | reason groups |
|---|---:|---:|---:|---:|---|
| high-bid caught | 14 | 2676c | 5/4/3 | -56c | {'value_over_hold': 8, 'probability_reduce': 5, 'probability_collapse': 1} |
| delayed-recheck kept | 11 | 2272c | 2/2/1 | -55c | {'value_over_hold': 7, 'probability_reduce': 3, 'probability_collapse': 1} |
| delayed-recheck rejected | 3 | 404c | 3/2/2 | -56c | {'value_over_hold': 1, 'probability_reduce': 2} |

## Rejected By Delayed Recheck

| market | reason | high-bid delta | given up | exit bid | recheck bid | drop | min window | min-after-exit | adverse |
|---|---|---:|---:|---:|---:|---:|---:|---:|---|
| KXBTC15M-26MAY062115-15 | value_over_hold | 144c | 144c | 70.0 | 51.0 | 6.0 | 64.0 | -56c | 10/25/50 |
| KXBTC15M-26MAY062015-15 | probability_reduce | 116c | 116c | 60.0 | 53.0 | -1.0 | 61.0 | -51c | 10/25/50 |
| KXBTC15M-26MAY062030-30 | probability_reduce | 144c | 144c | 76.0 | 82.0 | 11.0 | 65.0 | -11c | 10 |

## Worst Kept Paths

| market | reason | delayed delta | exit bid | recheck bid | drop | min-after-exit | adverse |
|---|---|---:|---:|---:|---:|---:|---|
| KXBTC15M-26MAY062100-00 | value_over_hold | 212c | 75.0 | 82.0 | -2.0 | -55c | 10/25/50 |
| KXBTC15M-26MAY061800-00 | value_over_hold | 176c | 70.0 | 60.0 | 9.0 | -47c | 10/25 |
| KXBTC15M-26MAY062315-15 | probability_reduce | 340c | 67.0 | 76.0 | 0.0 | -9c |  |
| KXBTC15M-26MAY062215-15 | probability_collapse | 412c | 65.0 | 64.0 | 5.0 | -8c |  |
| KXBTC15M-26MAY070115-15 | value_over_hold | 156c | 85.0 | 88.0 | 6.0 | -6c |  |
| KXBTC15M-26MAY061400-00 | value_over_hold | 64c | 84.0 | 92.0 | 3.0 | -3c |  |
| KXBTC15M-26MAY062200-00 | value_over_hold | 16c | 98.0 | 99.0 | 3.0 | -3c |  |
| KXBTC15M-26MAY062045-45 | probability_reduce | 326c | 64.0 | 82.0 | 1.0 | -1c |  |

## Interpretation

- High-bid suppression catches every diagnostic winner clip but includes large adverse post-exit excursions.
- The frozen delayed-recheck rule gives up some diagnostic recovery to avoid the weakest air-pocket holds, but it does not eliminate all large adverse excursions.
- Rejected rows are not automatically bad exclusions; they are the survival guard doing its job and need strict post-freeze validation.
