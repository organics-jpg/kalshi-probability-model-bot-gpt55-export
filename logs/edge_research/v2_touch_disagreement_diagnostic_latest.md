# V2 Touch-Disagreement Diagnostic

Generated UTC: `20260503_222035Z`

## Scope

- Research-only diagnostic; no orders are submitted and no bot files or live processes are touched.
- Compares v2 first selected side against the locked touch-hazard first selected side on markets where both select.
- This is not forward promotion evidence; it tests whether touch disagreement is physically informative.

## Metrics

| dataset | bucket | rows | v2 acc/net | touch acc/net | touch-v2 delta | mean delta |
|---|---|---:|---:|---:|---:|---:|
| current | all_pairs | 258 | 63.18%/291.0c | 59.69%/206.0c | -85.0c | -0.3c |
| current | agree | 211 | 63.98%/338.0c | 63.98%/1017.0c | 679.0c | 3.2c |
| current | disagree | 47 | 59.57%/-47.0c | 40.43%/-811.0c | -764.0c | -16.3c |
| v21 | all_pairs | 218 | 67.89%/1276.0c | 61.93%/711.0c | -565.0c | -2.6c |
| v21 | agree | 177 | 68.36%/1130.0c | 68.36%/1670.0c | 540.0c | 3.1c |
| v21 | disagree | 41 | 65.85%/146.0c | 34.15%/-959.0c | -1105.0c | -27.0c |

## Read

- Disagreement delta current/v21: -764.0c/-1105.0c across 47/41 paired markets.
- Touch disagreement is not robustly positive across both datasets.
