# v28 Feature-Gate Source Feasibility Bound

Research-only audit. No live bot changes.

- Generated UTC: `2026-05-11T01:59:04.169162+00:00`
- Feature-gate freeze UTC: `2026-05-06T16:47:25.847566+00:00`
- Max reconstructed/rejected share gate: `0.35`

## Interpretation

- Source labels are audit-only; this probe does not select trades.
- post_feature_freeze_entry: denominator 82, approved markets 45, reconstructed markets 82; 75% coverage source gate feasible=True, minimum reconstructed share needed 0.27419354838709675, max <=35% source-clean coverage 84.14634146341463%.
- post_feature_freeze_bridge: denominator 82, approved markets 45, reconstructed markets 82; 75% coverage source gate feasible=True, minimum reconstructed share needed 0.27419354838709675, max <=35% source-clean coverage 84.14634146341463%.

## post_feature_freeze_entry

- Denominator: `82`
- Approved markets available: `45`
- Reconstructed/rejected markets available: `82`
- Markets with both source types: `45`

| target coverage | required markets | min recon needed | min recon share | feasible under <=35% | max source-clean coverage |
|---:|---:|---:|---:|---|---:|
| 75.000000% | 62 | 17 | 0.274194 | True | 84.146341% |
| 80.000000% | 66 | 21 | 0.318182 | True | 84.146341% |
| 90.000000% | 74 | 29 | 0.391892 | False | 84.146341% |

## post_feature_freeze_bridge

- Denominator: `82`
- Approved markets available: `45`
- Reconstructed/rejected markets available: `82`
- Markets with both source types: `45`

| target coverage | required markets | min recon needed | min recon share | feasible under <=35% | max source-clean coverage |
|---:|---:|---:|---:|---|---:|
| 75.000000% | 62 | 17 | 0.274194 | True | 84.146341% |
| 80.000000% | 66 | 21 | 0.318182 | True | 84.146341% |
| 90.000000% | 74 | 29 | 0.391892 | False | 84.146341% |
