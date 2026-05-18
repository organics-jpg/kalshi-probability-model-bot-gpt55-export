# v28 Feature-Gate raw05 Coverage-Gap Audit

Research-only; source labels and outcomes are audit-only.

- Generated UTC: `2026-05-07T16:06:16.096042+00:00`
- Feature-gate freeze UTC: `2026-05-06T16:47:25.847566+00:00`
- Refreshed live baseline: `1463.000000c`

## Interpretation

- Audit-only source labels; approved-only oracle rows are not deployable evidence.
- post_feature_freeze_entry: raw05 needs 7 entries for 75% coverage; omitted approved/rejected counts are 0/26.
- post_feature_freeze_entry: approved-only oracle after adding missing rows has net 376.0c and blockers ['coverage_too_low']; best-any-source oracle has net 649.0c and blockers ['reconstructed_share_gt_35pct']; live baseline is 1463c.
- post_feature_freeze_entry: raw05 selected net 376.0c, coverage 66.23376623376623%, recon 0.27450980392156865.
- post_feature_freeze_bridge: raw05 needs 7 entries for 75% coverage; omitted approved/rejected counts are 0/26.
- post_feature_freeze_bridge: approved-only oracle after adding missing rows has net 150.0c and blockers ['coverage_too_low', 'full_loss_cushion_lt_3']; best-any-source oracle has net 452.0c and blockers ['reconstructed_share_gt_35pct']; live baseline is 1463c.
- post_feature_freeze_bridge: raw05 selected net 150.0c, coverage 66.23376623376623%, recon 0.27450980392156865.

## post_feature_freeze_entry

- Future denominator: `77`
- Required entries for 75%: `58`
- raw05 missing entries: `7`
- Omitted source counts: `{'rejected_actionable': 26}`
- Omitted fail reasons: `{'abs_d_below_min': 26, 'recross_above_max': 9}`

| scenario | entries | settled | coverage | net c | W/L | recon share | added source | blockers |
|---|---:|---:|---:|---:|---:|---:|---|---|
| raw05 | 51 | 38 | 66.233766 | 376.000000 | 26/12 | 0.274510 | {} | none |
| approved_only_oracle | 51 | 38 | 66.233766 | 376.000000 | 26/12 | 0.274510 | {} | coverage_too_low |
| best_any_source_oracle | 58 | 43 | 75.324675 | 649.000000 | 31/12 | 0.362069 | {'rejected_actionable': 7} | reconstructed_share_gt_35pct |

### Approved Omitted Rows

| market | side | won | net c | raw edge | recross | abs d | ask | p_side | stc | depth | fail reasons |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|

## post_feature_freeze_bridge

- Future denominator: `77`
- Required entries for 75%: `58`
- raw05 missing entries: `7`
- Omitted source counts: `{'rejected_actionable': 26}`
- Omitted fail reasons: `{'abs_d_below_min': 26, 'recross_above_max': 8}`

| scenario | entries | settled | coverage | net c | W/L | recon share | added source | blockers |
|---|---:|---:|---:|---:|---:|---:|---|---|
| raw05 | 51 | 35 | 66.233766 | 150.000000 | 21/14 | 0.274510 | {} | none |
| approved_only_oracle | 51 | 35 | 66.233766 | 150.000000 | 21/14 | 0.274510 | {} | coverage_too_low, full_loss_cushion_lt_3 |
| best_any_source_oracle | 58 | 41 | 75.324675 | 452.000000 | 27/14 | 0.362069 | {'rejected_actionable': 7} | reconstructed_share_gt_35pct |

### Approved Omitted Rows

| market | side | won | net c | raw edge | recross | abs d | ask | p_side | stc | depth | fail reasons |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
