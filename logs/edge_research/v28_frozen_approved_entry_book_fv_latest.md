# v28 Frozen Approved-Entry Book FV

- Freeze timestamp UTC: `2026-05-06T06:20:06.824407+00:00`
- Entry surface: `actual_v28_approved_entries_only`
- Candidate: `book_probability`
- Future entries/settled: `133/133`

## Current Read

- Frozen approved-entry FV candidate book_probability has 133 future settled rows.
- Brier/logloss deltas versus raw are 0.006168655138428583/-0.025019035845109228.
- This is actual approved-entry calibration evidence only; it does not use rejected-actionable rows.

## Ranking

| rank | overlay | settled | W/L | avg p | win rate | cal err | brier | d brier | logloss | d logloss | gross c | blockers |
|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| 1 | `raw_probability` | 133 | 118/15 | 0.884838 | 0.887218 | 0.002380 | 0.101803 | 0.000000 | 0.401256 | 0.000000 | 701.000000 | none |
| 2 | `noise_shrink_light_probability` | 133 | 118/15 | 0.876267 | 0.887218 | 0.010951 | 0.102349 | 0.000547 | 0.374330 | -0.026927 | 701.000000 | none |
| 3 | `book_probability` | 133 | 118/15 | 0.779098 | 0.887218 | 0.108120 | 0.107971 | 0.006169 | 0.376237 | -0.025019 | 701.000000 | brier_not_better_than_raw |
