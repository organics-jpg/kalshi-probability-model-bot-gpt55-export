# v28 Boundary-Clock Feature-Gate Source Denominator Audit

Research-only; no live bot changes or orders.

- Generated UTC: `2026-05-07T17:55:03.636332+00:00`
- Feature-gate freeze UTC: `2026-05-06T16:47:25.847566+00:00`

## Interpretation

- Source labels are audit-only; no selection rule uses them.
- post_feature_freeze_entry best-by-PnL rule raw07_recross60_abs085 selects 38/82 markets, net 454.0c, selected reconstructed share 0.21052631578947367, approved-source market coverage 66.66666666666667%, reconstructed-source market coverage 9.75609756097561%, omitted net by source {'approved_entry': 56.0, 'reconstructed_or_rejected': -241.0}.
- post_feature_freeze_bridge best-by-PnL rule raw07_recross60_abs085 selects 38/82 markets, net 454.0c, selected reconstructed share 0.21052631578947367, approved-source market coverage 66.66666666666667%, reconstructed-source market coverage 9.75609756097561%, omitted net by source {'approved_entry': 56.0, 'reconstructed_or_rejected': -241.0}.

## post_feature_freeze_entry

| rule | selected/den | net c | total cov | selected recon | approved-source cov | recon-source cov | available source markets | primary den sources | selected sources | omitted sources | omitted net by source |
|---|---:|---:|---:|---:|---:|---:|---|---|---|---|
| raw07_recross60_abs085 | 38/82 | 454.000000 | 46.341463 | 0.210526 | 66.666667 | 9.756098 | {'approved_entry': 45, 'reconstructed_or_rejected': 82} | {'reconstructed_or_rejected': 63, 'approved_entry': 19} | {'approved_entry': 30, 'reconstructed_or_rejected': 8} | {'reconstructed_or_rejected': 39, 'approved_entry': 5} | {'approved_entry': 56.0, 'reconstructed_or_rejected': -241.0} |
| raw05_recross60_abs085 | 55/82 | 445.000000 | 67.073171 | 0.272727 | 88.888889 | 18.292683 | {'approved_entry': 45, 'reconstructed_or_rejected': 82} | {'reconstructed_or_rejected': 63, 'approved_entry': 19} | {'approved_entry': 40, 'reconstructed_or_rejected': 15} | {'reconstructed_or_rejected': 27} | {'reconstructed_or_rejected': -82.0} |
| raw05_recross60_abs085_ask65 | 47/82 | 344.000000 | 57.317073 | 0.042553 | 100.000000 | 2.439024 | {'approved_entry': 45, 'reconstructed_or_rejected': 82} | {'reconstructed_or_rejected': 63, 'approved_entry': 19} | {'approved_entry': 45, 'reconstructed_or_rejected': 2} | {'reconstructed_or_rejected': 35} | {'reconstructed_or_rejected': -65.0} |
| raw03_recross70_abs075 | 64/82 | 307.000000 | 78.048780 | 0.390625 | 86.666667 | 30.487805 | {'approved_entry': 45, 'reconstructed_or_rejected': 82} | {'reconstructed_or_rejected': 63, 'approved_entry': 19} | {'approved_entry': 39, 'reconstructed_or_rejected': 25} | {'reconstructed_or_rejected': 18} | {'reconstructed_or_rejected': 55.0} |

## post_feature_freeze_bridge

| rule | selected/den | net c | total cov | selected recon | approved-source cov | recon-source cov | available source markets | primary den sources | selected sources | omitted sources | omitted net by source |
|---|---:|---:|---:|---:|---:|---:|---|---|---|---|
| raw07_recross60_abs085 | 38/82 | 454.000000 | 46.341463 | 0.210526 | 66.666667 | 9.756098 | {'approved_entry': 45, 'reconstructed_or_rejected': 82} | {'reconstructed_or_rejected': 63, 'approved_entry': 19} | {'approved_entry': 30, 'reconstructed_or_rejected': 8} | {'reconstructed_or_rejected': 39, 'approved_entry': 5} | {'approved_entry': 56.0, 'reconstructed_or_rejected': -241.0} |
| raw05_recross60_abs085 | 55/82 | 445.000000 | 67.073171 | 0.272727 | 88.888889 | 18.292683 | {'approved_entry': 45, 'reconstructed_or_rejected': 82} | {'reconstructed_or_rejected': 63, 'approved_entry': 19} | {'approved_entry': 40, 'reconstructed_or_rejected': 15} | {'reconstructed_or_rejected': 27} | {'reconstructed_or_rejected': -82.0} |
| raw05_recross60_abs085_ask65 | 47/82 | 344.000000 | 57.317073 | 0.042553 | 100.000000 | 2.439024 | {'approved_entry': 45, 'reconstructed_or_rejected': 82} | {'reconstructed_or_rejected': 63, 'approved_entry': 19} | {'approved_entry': 45, 'reconstructed_or_rejected': 2} | {'reconstructed_or_rejected': 35} | {'reconstructed_or_rejected': -65.0} |
| raw03_recross70_abs075 | 64/82 | 307.000000 | 78.048780 | 0.390625 | 86.666667 | 30.487805 | {'approved_entry': 45, 'reconstructed_or_rejected': 82} | {'reconstructed_or_rejected': 63, 'approved_entry': 19} | {'approved_entry': 39, 'reconstructed_or_rejected': 25} | {'reconstructed_or_rejected': 18} | {'reconstructed_or_rejected': 55.0} |
