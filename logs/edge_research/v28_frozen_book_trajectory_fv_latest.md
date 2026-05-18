# v28 Frozen Book-Trajectory FV

- Freeze timestamp UTC: `2026-05-06T02:47:06.099693+00:00`
- Candidate: `gap15_or_drawdown10`
- Future rows/markets/market-sides: `16371/139/278`

## Current Read

- View approved_only candidate rows 185 with Brier/logloss deltas -0.006465489121030052/-0.058536085976903574 and blockers [].
- View first_per_market_side candidate rows 278 with Brier/logloss deltas -0.005829965412330246/-0.025293489455758156 and blockers [].
- View last_per_market_side candidate rows 278 with Brier/logloss deltas -0.007015796044586763/-0.05085760273030587 and blockers [].
- View all_observations candidate rows 16371 with Brier/logloss deltas -0.0022175152031330414/-0.006440429569180506 and blockers [].

## Views

| view | rows | W/L | avg p | win rate | brier d | logloss d | blockers |
|---|---:|---:|---:|---:|---:|---:|---|
| `approved_only` | 185 | 165/20 | 0.876303 | 0.891892 | -0.006465 | -0.058536 | none |
| `first_per_market_side` | 278 | 139/139 | 0.493429 | 0.500000 | -0.005830 | -0.025293 | none |
| `last_per_market_side` | 278 | 139/139 | 0.509369 | 0.500000 | -0.007016 | -0.050858 | none |
| `all_observations` | 16371 | 8946/7425 | 0.539932 | 0.546454 | -0.002218 | -0.006440 | none |
