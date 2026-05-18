# v28 Frozen Side-Asymmetry Registry

- Freeze timestamp UTC: `2026-05-06T07:47:04.735626+00:00`
- Registry: `side_asymmetry_no_p60_70_midboundary_midrecross`
- Rule: `side=no, 0.60<=p_side<0.70, 0.30<=abs_d_sigma<0.55, 0.45<=recross_hazard_score<0.75`
- Future denominator: `118`
- Target entries/settled: `87/87`
- Bucket entries/settled/WL/net/cal gap: `6/6/2/4/-187.000000c/0.305415`
- Non-clock entries/settled/WL/net/cal gap: `6/6/2/4/-187.000000c/0.305415`

## Interpretation

- Future denominator is 118; side-asymmetry bucket has 6 entries and 6 settled rows.
- Non-clock subset has 6 entries and 6 settled rows.
- This is a registry only; it becomes a candidate only after enough future evidence accumulates.

## Rows

| market | source | side | won | net c | p | ask | edge | stc | abs d | recross | clock |
|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|---|
| KXBTC15M-26MAY060445-45 | rejected_actionable | no | False | -94.000000 | 0.636374 | 0.450000 | 0.186374 | 864.716000 | 0.322198 | 0.666569 | False |
| KXBTC15M-26MAY060500-00 | rejected_actionable | no | False | -126.000000 | 0.674136 | 0.610000 | 0.064136 | 783.254000 | 0.377919 | 0.620318 | False |
| KXBTC15M-26MAY060545-45 | rejected_actionable | no | False | -92.000000 | 0.626642 | 0.440000 | 0.186642 | 807.560000 | 0.323422 | 0.689053 | False |
| KXBTC15M-26MAY062045-45 | rejected_actionable | no | True | 94.000000 | 0.617920 | 0.510000 | 0.107920 | 834.661000 | 0.321769 | 0.590304 | False |
| KXBTC15M-26MAY062100-00 | rejected_actionable | no | False | -47.000000 | 0.615588 | 0.220000 | 0.395588 | 683.547000 | 0.321159 | 0.515467 | False |
| KXBTC15M-26MAY062215-15 | rejected_actionable | no | True | 78.000000 | 0.661831 | 0.590000 | 0.071831 | 850.282000 | 0.404187 | 0.669869 | False |
