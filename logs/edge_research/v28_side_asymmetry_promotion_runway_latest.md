# v28 Side-Asymmetry Promotion Runway

Research-only: no live bot changes and no orders.

- Freeze timestamp UTC: `2026-05-06T07:52:22.405861+00:00`
- Variant: `clock_then_side_no_midboundary_0p00`
- Future entries/settled/denominator: `None/87/118`
- Adjusted rows clock/side/total: `37/6/43`
- Brier/logloss delta: `-0.011712/-0.024525`
- Ready for consideration: `False`

## Interpretation

- Frozen side-asymmetry has 87 settled rows and 43 adjusted rows.
- Current Brier/logloss deltas are -0.011711620895563213/-0.024525492188571918.
- Promotion blockers remaining: 2.
- Live readiness blockers: control_risk_stop_active.
- This lane can only improve FV calibration; it does not by itself fix negative broad-entry PnL.

## Checks

| check | pass | actual | required | note |
|---|---:|---:|---|---|
| settled_rows | `True` | 87 | >=30 | need 0 more settled rows |
| adjusted_rows | `True` | 43 | >=8 | need 0 more adjusted rows |
| coverage_band | `False` | 73.728814 | 75.0-90.0% | coverage must stay compatible with the goal |
| brier_better | `True` | -0.011712 | <0 vs raw | future Brier delta must remain negative |
| logloss_better | `True` | -0.024525 | <0 vs raw | future logloss delta must remain negative |
| live_readiness_gate | `False` | False | true | control_risk_stop_active |
