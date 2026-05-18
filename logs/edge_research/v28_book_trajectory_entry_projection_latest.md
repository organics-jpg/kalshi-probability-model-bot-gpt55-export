# v28 Book-Trajectory Entry Projection

Discovery-only first-qualifying-entry projection for trajectory-adjusted FV.

- Surface: `first_qualifying_observation_per_market`
- Denominator markets: `176`
- Constraints: `{'max_ask': 0.9, 'min_seconds_to_close': 0.0, 'max_seconds_to_close': 600.0}`

## Current Read

- Best 75-90% coverage row is gap15_or_drawdown10_p50_edge0 with coverage 87.5 and gross 556.0c.
- Raw p50 baseline has coverage 88.06818181818181 and gross 539.0c.
- This is discovery-only because projected entries use observed shadow opportunities, not actual fills.

## Ranked Policies

| rank | policy | entries | W/L | coverage | gross c | avg p | avg ask | avg edge |
|---:|---|---:|---:|---:|---:|---:|---:|---:|
| 1 | `gap15_or_drawdown10_p50_edge0` | 154 | 115/39 | 87.500000 | 556.000000 | 0.748277 | 0.710649 | 0.037627 |
| 2 | `gap15_or_drawdown10_p52_edge0` | 153 | 115/38 | 86.931818 | 543.000000 | 0.753708 | 0.716144 | 0.037564 |
| 3 | `raw_probability_p50_edge0` | 155 | 113/42 | 88.068182 | 539.000000 | 0.744577 | 0.694258 | 0.050319 |
| 4 | `raw_probability_p52_edge0` | 154 | 114/40 | 87.500000 | 472.000000 | 0.756360 | 0.709610 | 0.046750 |
| 5 | `gap15_or_drawdown10_p60_edge0` | 149 | 114/35 | 84.659091 | 156.000000 | 0.794442 | 0.754631 | 0.039811 |
| 6 | `raw_probability_p60_edge0` | 152 | 112/40 | 86.363636 | 27.000000 | 0.794575 | 0.735066 | 0.059509 |
| 7 | `gap15_or_drawdown10_p60_edge2` | 135 | 103/32 | 76.704545 | -42.000000 | 0.818773 | 0.766074 | 0.052699 |
| 8 | `book_probability_p52_edge0` | 161 | 118/43 | 91.477273 | 417.000000 | 0.707019 | 0.707019 | 0.000000 |
| 9 | `book_probability_p50_edge0` | 161 | 116/45 | 91.477273 | 363.000000 | 0.697950 | 0.697950 | 0.000000 |
