# v32 Blend Block Stability

Generated UTC: `2026-05-04T20:01:15.401713+00:00`

## Scope

- Research-only block-stability audit for FV edge candidates.
- No live bot code/process or orders are touched.
- Negative blocks mean the aggregate edge may still be regime-sensitive.

## Summary

| model | edge | cost | block kind | positive blocks | worst block net | min block coverage | total block net |
|---|---:|---:|---|---:|---:|---:|---:|
| `book_v31_time_platt` | 1.0 | 2.0 | `block10` | 7/10 | -186.0c | 96.97% | 995.0c |
| `book_time_v33drift85` | 1.0 | 2.0 | `block10` | 6/10 | -150.0c | 96.97% | 708.0c |
| `book_time_v32drift85` | 1.0 | 2.0 | `block10` | 6/10 | -157.0c | 96.97% | 712.0c |
| `book_v33_drift3_platt` | 1.0 | 2.0 | `block10` | 6/10 | -391.0c | 96.97% | 11.0c |
| `book_v33_platt` | 2.5 | 2.0 | `block10` | 5/10 | -331.0c | 63.64% | 520.0c |
| `book_v32_drift3_platt` | 2.0 | 2.0 | `block10` | 5/10 | -447.0c | 78.79% | 58.0c |
| `book_v31_platt` | 2.0 | 2.0 | `block10` | 4/10 | -333.0c | 81.82% | 327.0c |
| `book_v33_platt` | 2.5 | 2.0 | `block20` | 11/20 | -230.0c | 52.94% | 520.0c |
| `book_v32_drift3_platt` | 2.0 | 2.0 | `block20` | 11/20 | -360.0c | 76.47% | 58.0c |
| `book_time_v33drift85` | 1.0 | 2.0 | `block20` | 10/20 | -130.0c | 94.12% | 708.0c |
| `book_time_v32drift85` | 1.0 | 2.0 | `block20` | 10/20 | -137.0c | 94.12% | 712.0c |
| `book_v31_time_platt` | 1.0 | 2.0 | `block20` | 10/20 | -208.0c | 94.12% | 995.0c |
| `book_v31_platt` | 2.0 | 2.0 | `block20` | 10/20 | -319.0c | 76.47% | 327.0c |
| `book_v33_drift3_platt` | 1.0 | 2.0 | `block20` | 9/20 | -266.0c | 94.12% | 11.0c |
| `book_v31_time_platt` | 1.0 | 1.0 | `block10` | 8/10 | -153.0c | 96.97% | 1324.0c |
| `book_time_v33drift85` | 1.0 | 1.0 | `block10` | 7/10 | -117.0c | 96.97% | 1037.0c |
| `book_time_v32drift85` | 1.0 | 1.0 | `block10` | 6/10 | -124.0c | 96.97% | 1041.0c |
| `book_v33_drift3_platt` | 1.0 | 1.0 | `block10` | 6/10 | -358.0c | 96.97% | 340.0c |
| `book_v33_platt` | 2.5 | 1.0 | `block10` | 5/10 | -304.0c | 63.64% | 777.0c |
| `book_v32_drift3_platt` | 2.0 | 1.0 | `block10` | 5/10 | -416.0c | 78.79% | 348.0c |
| `book_v31_platt` | 2.0 | 1.0 | `block10` | 4/10 | -303.0c | 81.82% | 622.0c |
| `book_v33_platt` | 2.5 | 1.0 | `block20` | 12/20 | -219.0c | 52.94% | 777.0c |
| `book_v32_drift3_platt` | 2.0 | 1.0 | `block20` | 12/20 | -346.0c | 76.47% | 348.0c |
| `book_time_v33drift85` | 1.0 | 1.0 | `block20` | 11/20 | -114.0c | 94.12% | 1037.0c |
| `book_time_v32drift85` | 1.0 | 1.0 | `block20` | 11/20 | -121.0c | 94.12% | 1041.0c |
| `book_v31_time_platt` | 1.0 | 1.0 | `block20` | 11/20 | -191.0c | 94.12% | 1324.0c |
| `book_v31_platt` | 2.0 | 1.0 | `block20` | 10/20 | -305.0c | 76.47% | 622.0c |
| `book_v33_drift3_platt` | 1.0 | 1.0 | `block20` | 9/20 | -249.0c | 94.12% | 340.0c |
| `book_time_v33drift85` | 1.0 | 0.0 | `block10` | 8/10 | -84.0c | 96.97% | 1366.0c |
| `book_time_v32drift85` | 1.0 | 0.0 | `block10` | 8/10 | -91.0c | 96.97% | 1370.0c |
| `book_v31_time_platt` | 1.0 | 0.0 | `block10` | 8/10 | -120.0c | 96.97% | 1653.0c |
| `book_v33_drift3_platt` | 1.0 | 0.0 | `block10` | 6/10 | -325.0c | 96.97% | 669.0c |
| `book_v32_drift3_platt` | 2.0 | 0.0 | `block10` | 6/10 | -385.0c | 78.79% | 638.0c |
| `book_v31_platt` | 2.0 | 0.0 | `block10` | 5/10 | -273.0c | 81.82% | 917.0c |
| `book_v33_platt` | 2.5 | 0.0 | `block10` | 5/10 | -277.0c | 63.64% | 1034.0c |
| `book_time_v33drift85` | 1.0 | 0.0 | `block20` | 13/20 | -98.0c | 94.12% | 1366.0c |
| `book_time_v32drift85` | 1.0 | 0.0 | `block20` | 13/20 | -105.0c | 94.12% | 1370.0c |
| `book_v33_platt` | 2.5 | 0.0 | `block20` | 13/20 | -208.0c | 52.94% | 1034.0c |
| `book_v32_drift3_platt` | 2.0 | 0.0 | `block20` | 13/20 | -332.0c | 76.47% | 638.0c |
| `book_v31_time_platt` | 1.0 | 0.0 | `block20` | 12/20 | -174.0c | 94.12% | 1653.0c |
| `book_v31_platt` | 2.0 | 0.0 | `block20` | 12/20 | -291.0c | 76.47% | 917.0c |
| `book_v33_drift3_platt` | 1.0 | 0.0 | `block20` | 9/20 | -232.0c | 94.12% | 669.0c |

## Read

- The blended candidate can be the best aggregate candidate while still failing strict block stability.
- Treat this as a forward-shadow candidate until live sample size shows whether the bad blocks repeat.
