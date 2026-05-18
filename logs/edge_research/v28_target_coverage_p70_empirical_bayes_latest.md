# v28 Target-Coverage p70 Empirical Bayes

- Rows: `112`
- Full target scale: `1.25`
- Best variant: `p70_empirical_bayes_prior48`

## Current Read

- Best empirical-Bayes p70 variant is p70_empirical_bayes_prior48 with scale 1.0981012658227849 and Brier/logloss p95 0.0008474887950797044/0.0013279133000561657.
- Light prior count 6 uses scale 1.2094594594594594; heavy prior count 48 uses scale 1.0981012658227849.
- Best variant first adverse p80 break count is 1.
- This is an anti-overfit throttle on certainty, not a new entry selector; it preserves target coverage.

## Ranking

| variant | prior count | evidence count | scale | rows | adjusted | brier mean | brier p95 | logloss mean | logloss p95 | adverse p80 p | first break | blockers |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| p70_empirical_bayes_prior48 | 48 | 31 | 1.098101 | 112 | 31 | -0.000322 | 0.000847 | -0.001935 | 0.001328 | 0.820876 | 1 | none |
| p70_empirical_bayes_prior24 | 24 | 31 | 1.140909 | 112 | 31 | -0.000386 | 0.001251 | -0.002555 | 0.002246 | 0.829436 | 1 | none |
| p70_empirical_bayes_prior12 | 12 | 31 | 1.180233 | 112 | 31 | -0.000410 | 0.001674 | -0.003011 | 0.003017 | 0.837010 | 1 | none |
| p70_empirical_bayes_prior6 | 6 | 31 | 1.209459 | 112 | 31 | -0.000407 | 0.001904 | -0.003284 | 0.003747 | 0.842463 | 1 | none |
