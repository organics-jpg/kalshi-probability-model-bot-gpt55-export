# v28 Goldilocks Edge Repair Stress

Research-only; no live bot changes or orders.

- Candidate: `skip_false_edge_phase_repair_goldilocks`
- Freeze timestamp UTC: `2026-05-06T13:41:43.611538+00:00`

## Current Read

- Diagnostic candidate: 92 settled, 61/31, net 63.0c, coverage 75.40983606557377%.
- Diagnostic delta versus target: 495.0c versus target net -432.0c.
- Diagnostic source counts: {'target': {'rejected_actionable': 85, 'approved_entry': 5}, 'danger': {'rejected_actionable': 38}, 'repair': {'rejected_actionable': 39, 'approved_entry': 1}, 'candidate': {'rejected_actionable': 86, 'approved_entry': 6}}.
- Diagnostic warnings: ['All avoided danger rows are reconstructed rejected-actionable rows so far.', '39 repair rows are reconstructed.', 'Two ordinary full losses would erase current positive net.'].
- Frozen future settled rows: 48; this is the only promotion evidence.

## diagnostic_existing_forward

| scenario | entries | settled | W/L | coverage | net c | avg c |
|---|---:|---:|---:|---:|---:|---:|
| target_control | 90 | 90 | 52/38 | 73.770492 | -432.000000 | -4.800000 |
| candidate_full | 92 | 92 | 61/31 | 75.409836 | 63.000000 | 0.684783 |
| skip_only_no_repairs | 52 | 52 | 35/17 | 42.622951 | 300.000000 | 5.769231 |
| approved_repairs_only | 53 | 53 | 36/17 | 43.442623 | 319.000000 | 6.018868 |
| rejected_repairs_only | 91 | 91 | 60/31 | 74.590164 | 44.000000 | 0.483516 |
| approved_source_candidate_rows_only | 6 | 6 | 6/0 | 4.918033 | 35.000000 | 5.833333 |
| rejected_source_candidate_rows_only | 86 | 86 | 55/31 | 70.491803 | 28.000000 | 0.325581 |

### Candidate Source Split

| source | entries | settled | W/L | coverage | net c | avg c |
|---|---:|---:|---:|---:|---:|---:|
| approved_entry | 6 | 6 | 6/0 | 4.918033 | 35.000000 | 5.833333 |
| rejected_actionable | 86 | 86 | 55/31 | 70.491803 | 28.000000 | 0.325581 |

### Danger Source Split

| source | entries | settled | W/L | coverage | net c | avg c |
|---|---:|---:|---:|---:|---:|---:|
| rejected_actionable | 38 | 38 | 17/21 | 31.147541 | -732.000000 | -19.263158 |

### Repair Source Split

| source | entries | settled | W/L | coverage | net c | avg c |
|---|---:|---:|---:|---:|---:|---:|
| approved_entry | 1 | 1 | 1/0 | 0.819672 | 19.000000 | 19.000000 |
| rejected_actionable | 39 | 39 | 25/14 | 31.967213 | -256.000000 | -6.564103 |

### Full-Loss Runway

| added full losses | stressed settled | stressed net c | still positive | sample gate met |
|---:|---:|---:|---:|---:|
| 1 | 93 | -37.000000 | False | True |
| 2 | 94 | -137.000000 | False | True |
| 3 | 95 | -237.000000 | False | True |
| 4 | 96 | -337.000000 | False | True |
| 5 | 97 | -437.000000 | False | True |

## frozen_future

| scenario | entries | settled | W/L | coverage | net c | avg c |
|---|---:|---:|---:|---:|---:|---:|
| target_control | 51 | 50 | 30/20 | 78.461538 | 220.000000 | 4.400000 |
| candidate_full | 49 | 48 | 30/18 | 75.384615 | -90.000000 | -1.875000 |
| skip_only_no_repairs | 33 | 32 | 20/12 | 50.769231 | 20.000000 | 0.625000 |
| approved_repairs_only | 33 | 32 | 20/12 | 50.769231 | 20.000000 | 0.625000 |
| rejected_repairs_only | 49 | 48 | 30/18 | 75.384615 | -90.000000 | -1.875000 |
| approved_source_candidate_rows_only | 3 | 3 | 3/0 | 4.615385 | 31.000000 | 10.333333 |
| rejected_source_candidate_rows_only | 46 | 45 | 27/18 | 70.769231 | -121.000000 | -2.688889 |

### Candidate Source Split

| source | entries | settled | W/L | coverage | net c | avg c |
|---|---:|---:|---:|---:|---:|---:|
| approved_entry | 3 | 3 | 3/0 | 4.615385 | 31.000000 | 10.333333 |
| rejected_actionable | 46 | 45 | 27/18 | 70.769231 | -121.000000 | -2.688889 |

### Danger Source Split

| source | entries | settled | W/L | coverage | net c | avg c |
|---|---:|---:|---:|---:|---:|---:|
| rejected_actionable | 18 | 18 | 10/8 | 27.692308 | 200.000000 | 11.111111 |

### Repair Source Split

| source | entries | settled | W/L | coverage | net c | avg c |
|---|---:|---:|---:|---:|---:|---:|
| rejected_actionable | 16 | 16 | 10/6 | 24.615385 | -110.000000 | -6.875000 |

### Full-Loss Runway

| added full losses | stressed settled | stressed net c | still positive | sample gate met |
|---:|---:|---:|---:|---:|
| 1 | 49 | -190.000000 | False | True |
| 2 | 50 | -290.000000 | False | True |
| 3 | 51 | -390.000000 | False | True |
| 4 | 52 | -490.000000 | False | True |
| 5 | 53 | -590.000000 | False | True |
