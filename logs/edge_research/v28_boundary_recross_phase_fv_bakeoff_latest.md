# v28 Boundary/Recross Phase FV Bakeoff

Diagnostic-only bakeoff on the fixed target-coverage forward rows.

- Policy: `raw_p50_turbulence_valve_edge4_p60_recross75_near25`
- Target freeze timestamp UTC: `2026-05-06T02:08:01.321286+00:00`
- Forward entries/settled/denominator: `112/112/152`

## Interpretation

- Best diagnostic variant by Brier delta is confidence_leak_shrink with 112 rows and Brier/logloss deltas -0.007520892107859286/-0.01637209176476722.
- The current shrink is not the diagnostic winner on this refreshed slice; treat this only as a hypothesis until frozen forward rows exist.
- The best diagnostic variant still does not have a strictly negative bootstrap p95; sample risk remains unresolved.

## Ranking

| rank | variant | rows | adjusted | W/L | net c | brier d | brier p95 | logloss d | logloss p95 | avg p | win rate | note |
|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| 1 | confidence_leak_shrink | 112 | 83 | 64/48 | -626.000000 | -0.007521 | 0.001211 | -0.016372 | 0.002996 | 0.612581 | 0.571429 | Shrink boundary turbulence, with stronger leak on expensive thin high-confidence touches. |
| 2 | boundary_recross_shrink_probability | 112 | 87 | 64/48 | -626.000000 | -0.007141 | 0.001566 | -0.015609 | 0.003569 | 0.611004 | 0.571429 | Current candidate: shrink shallow high-recross rows and thin turbulent touches. |
| 3 | edge_phase_shrink | 112 | 51 | 64/48 | -626.000000 | -0.006876 | 0.000339 | -0.015542 | 0.000435 | 0.626971 | 0.571429 | Shrink shallow turbulence only when edge is not wide, plus very thin deep-pressure touches. |
| 4 | near_recross_shrink_only | 112 | 76 | 64/48 | -626.000000 | -0.005614 | 0.001096 | -0.011664 | 0.002419 | 0.621851 | 0.571429 | Only boundary turbulence forgets; thin away-from-boundary touches keep raw confidence. |
| 5 | raw_probability | 112 | 0 | 64/48 | -626.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.653763 | 0.571429 | Control: no adjustment to v28 FV. |
