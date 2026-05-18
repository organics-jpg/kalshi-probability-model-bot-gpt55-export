# v28 Boundary-Clock Promotion Runway

Research-only: no live bot changes and no orders.

- FV freeze: `2026-05-06T07:18:17.705020+00:00`
- Entry freeze: `2026-05-06T07:07:27.790042+00:00`
- FV entry bridge freeze: `2026-05-06T07:35:02.597585+00:00`
- Residual registry freeze: `2026-05-06T07:28:09.623811+00:00`
- Diagnostic robustness FV/entry: `True/True`
- Ready for consideration: `False`
- Residual registry ready: `True`

## Interpretation

- Diagnostic robustness: FV=True, entry=True.
- Frozen promotion blockers remaining: 3.
- The FV entry bridge is tracked as a separate promotion path because it converts the probability correction into entry economics.
- Residual registry is informational only and should not block the boundary-clock FV candidate.

## Checks

| check | pass | actual | required | note |
|---|---:|---:|---|---|
| fv_settled_rows | `True` | 88 | >=30 | need 0 more settled rows |
| fv_adjusted_rows | `True` | 38 | >=8 | need 0 more adjusted hazard rows |
| fv_brier_better | `True` | -0.007305 | <0 vs raw | future Brier delta must be negative |
| fv_logloss_better | `True` | -0.015397 | <0 vs raw | future logloss delta must be negative |
| fv_live_readiness_gate | `False` | False | true | control_risk_stop_active |
| entry_denominator | `True` | 121 | >=30 | need 0 more future markets |
| entry_settled_rows | `True` | 91 | >=30 | need 0 more settled rows |
| entry_coverage | `True` | 75.206612 | 75.0-90.0% | coverage must stay near target |
| entry_net_positive | `False` | -151.000000 | >0c | future candidate net must be positive |
| bridge_denominator | `True` | 119 | >=30 | need 0 more future markets |
| bridge_settled_rows | `True` | 90 | >=30 | need 0 more settled rows |
| bridge_coverage | `True` | 75.630252 | 75.0-90.0% | coverage must stay near target |
| bridge_net_positive | `True` | 229.000000 | >0c | future bridge candidate net must be positive |
| bridge_live_readiness_gate | `False` | False | true | control_risk_stop_active |
| residual_registry_settled | `True` | 9 | >=8 | registry only; enough rows decide whether to create a candidate |
| residual_registry_direction | `True` | -167.000000 | <0c if harmful | negative bucket net would support future modeling work |
