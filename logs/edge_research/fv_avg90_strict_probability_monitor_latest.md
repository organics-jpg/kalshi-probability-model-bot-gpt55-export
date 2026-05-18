# FV avg90 Strict Probability Monitor

Generated UTC: `2026-05-04T23:53:07.917206+00:00`

## Scope

- Research-only strict forward registry for FV probability calibration.
- New rows are registered only while their market close is still in the future.
- Later FV candidates are only present on rows registered after those candidates were added.
- No orders are submitted and no live bot code/process is touched.

## Lock

- Created UTC: `2026-05-04T17:23:26.783133+00:00`
- Initial max source line: `53941`
- Initial max entry: `2026-05-04T17:23:11.900000+00:00`

## Registry

- Total registered opportunities: 131
- New opportunities this run: 6
- Resolved / pending: 125 / 6

## Calibration

| model | resolved | Brier | logloss | side acc | mean p_yes | yes rate |
|---|---:|---:|---:|---:|---:|---:|
| `v28_live_surface` | 125 | 0.2214192085620189 | 0.6252493205964004 | 63.20% | 48.38% | 57.60% |
| `v28_avg90` | 125 | 0.2214258143680374 | 0.6244114260359678 | 63.20% | 48.44% | 57.60% |
| `v30_avg90_exact_var` | 120 | 0.22828802688165417 | 0.6395806059572678 | 61.67% | 47.23% | 55.83% |
| `v31_avg90_final60_exact` | 114 | 0.23196841963556994 | 0.6466003000697422 | 59.65% | 47.64% | 58.77% |
| `v32_avg110_final60_exact` | 81 | 0.2218851807612908 | 0.6285825774342966 | 75.31% | 44.16% | 65.43% |
| `v33_antipersist3` | 62 | 0.23246926465872395 | 0.6478321261639074 | 70.97% | 41.55% | 69.35% |
| `v34_material_antipersist3` | 51 | 0.17134422363930912 | 0.5109012837317641 | 86.27% | 44.41% | 62.75% |
| `v35_h150_t102_antipersist3` | 51 | 0.17163216655282745 | 0.5115304800885173 | 86.27% | 44.40% | 62.75% |
| `v36_piecewise_h150_t102_antipersist3` | 40 | 0.16731613068195744 | 0.4965632287419644 | 82.50% | 41.00% | 52.50% |
| `v37_piecewise_dynamic_temp_antipersist3` | 33 | 0.15674466035550236 | 0.46873916458748266 | 78.79% | 38.36% | 42.42% |
| `v38_long60_antipersist` | 24 | 0.1273392579236433 | 0.39694714030010925 | 87.50% | 32.61% | 45.83% |
| `v39_midband_v28_fallback` | 0 | NA | NA | NA | NA | NA |
| `book_mid_probability` | 109 | 0.20066123880733946 | 0.5776773100712819 | 70.64% | 45.52% | 60.55% |
| `book_platt` | 103 | 0.212809388214588 | 0.6100674424038538 | 69.90% | 42.26% | 58.25% |
| `book_v31_platt` | 103 | 0.2135877457918055 | 0.6139009390706495 | 69.90% | 41.88% | 58.25% |
| `book_v32_platt` | 81 | 0.2525923687362675 | 0.7125920773040951 | 62.96% | 39.57% | 65.43% |
| `book_v33_platt` | 62 | 0.28420994379132636 | 0.7848867911700971 | 54.84% | 36.16% | 69.35% |
| `book_v31_time_platt` | 88 | 0.2441811692076009 | 0.6914049071069086 | 65.91% | 39.75% | 60.23% |
