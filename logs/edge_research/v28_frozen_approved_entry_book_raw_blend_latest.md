# v28 Frozen Approved-Entry Book/Raw Blend FV

Research-only frozen FV calibration watch for actual v28-approved entries.

- Freeze timestamp UTC: `2026-05-06T22:58:06.332385+00:00`
- Primary candidate: `book_raw_blend_alpha_0p50`
- Rule: `p = book_probability + alpha * (raw_probability - book_probability)`
- Physics: Use the executable book as a humility anchor while retaining a continuous memory term from raw v28 when the model's conviction is physically supported. This avoids a hard book-vs-raw cutoff.
- Candidate live ready: `True`
- Blockers: `none`

## Interpretation

- Frozen primary `book_raw_blend_alpha_0p50` has future entries/settled 55/55.
- Future primary Brier/logloss deltas versus raw are -0.0024588753812227193/-0.023292898221775604.
- Pre-freeze primary deltas were -0.009893889048230936/-0.07531171519327284 over 118 settled rows.
- Promotion blockers: [].
- Pre-freeze context motivates the blend only; future rows are the validation evidence.

## Future Validation

| rank | overlay | settled | W/L | avg p | brier | d brier | logloss | d logloss | gross c | blockers |
|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| 1 | `book_raw_blend_alpha_0p5` | 55 | 47/8 | 0.833108 | 0.125583 | -0.002459 | 0.416307 | -0.023293 | 362.000000 | none |
| 2 | `book_raw_blend_alpha_0p75` | 55 | 47/8 | 0.860480 | 0.125732 | -0.002310 | 0.419670 | -0.019931 | 362.000000 | none |
| 3 | `book_raw_blend_alpha_0p35` | 55 | 47/8 | 0.816685 | 0.126531 | -0.001511 | 0.418377 | -0.021223 | 362.000000 | none |
| 4 | `raw_probability` | 55 | 47/8 | 0.887853 | 0.128042 | None | 0.439600 | None | 362.000000 | none |

## Pre-Freeze Context

| rank | overlay | settled | W/L | avg p | brier | d brier | logloss | d logloss | gross c | blockers |
|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| 1 | `book_raw_blend_alpha_0p35` | 118 | 99/19 | 0.813676 | 0.125521 | -0.010719 | 0.413810 | -0.075133 | 461.000000 | none |
| 2 | `book_raw_blend_alpha_0p5` | 118 | 99/19 | 0.829452 | 0.126347 | -0.009894 | 0.413631 | -0.075312 | 461.000000 | none |
| 3 | `book_raw_blend_alpha_0p75` | 118 | 99/19 | 0.855746 | 0.129920 | -0.006321 | 0.419831 | -0.069112 | 461.000000 | none |
| 4 | `raw_probability` | 118 | 99/19 | 0.882039 | 0.136241 | None | 0.488943 | None | 461.000000 | none |
