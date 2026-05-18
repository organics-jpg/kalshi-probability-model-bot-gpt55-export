# v28 RMT Regime Diagnostic

Shadow-only test of whether recent feature covariance has a real spectral factor or is mostly noise.

- Rolling window: `48` actionable observations
- Minimum history: `24` observations
- Features: `p_side, ask_prob, v28_minus_ask_prob, edge_cents, seconds_to_close, sigma_t_dollars, abs_d_sigma, eligible_depth, recross_hazard_score, book_age_ms, btc_age_ms`

## Overall

- Observations: `6798`
- Settled/resolved: `6798/6798`
- Gross cents: `-3233.0`
- Avg top / MP edge: `31.403932`
- Avg outlier share: `0.872228`

## By Spectral Tag

| tag | obs | settled | wins | losses | gross c | top/edge | outlier share | best brier variant | best brier | best vs raw |
|---|---:|---:|---:|---:|---:|---:|---:|---|---:|---:|
| insufficient_history | 24 | 24 | 13 | 11 | 10.0 | None | None | book_ask_prior | 0.161917 | -0.008187 |
| spectral_dominant_factor | 6740 | 6740 | 3707 | 3033 | -3331.0 | 31.555333 | 0.875143 | book_ask_prior | 0.163247 | -0.005575 |
| spectral_factor | 33 | 33 | 18 | 15 | 250.0 | 1.403474 | 0.303427 | v28_raw | 0.173674 | 0.000000 |
| spectral_noise | 1 | 1 | 0 | 1 | -162.0 | 0.976321 | 0.000000 | v28_premium_book_anchor | 0.406462 | 0.000000 |

## Variant Brier By Tag

### insufficient_history
- `book_ask_prior`: count `24`, avg_brier `0.161917`, vs_raw `-0.008187`
- `large_disagreement_book_anchor`: count `24`, avg_brier `0.170104`, vs_raw `0.000000`
- `v28_premium_book_anchor`: count `24`, avg_brier `0.170104`, vs_raw `0.000000`
- `v28_raw`: count `24`, avg_brier `0.170104`, vs_raw `0.000000`

### spectral_dominant_factor
- `book_ask_prior`: count `6740`, avg_brier `0.163247`, vs_raw `-0.005575`
- `large_disagreement_book_anchor`: count `6740`, avg_brier `0.164503`, vs_raw `-0.004320`
- `v28_premium_book_anchor`: count `6740`, avg_brier `0.166643`, vs_raw `-0.002180`
- `v28_raw`: count `6740`, avg_brier `0.168823`, vs_raw `0.000000`

### spectral_factor
- `book_ask_prior`: count `33`, avg_brier `0.199173`, vs_raw `0.025498`
- `large_disagreement_book_anchor`: count `33`, avg_brier `0.193694`, vs_raw `0.020020`
- `v28_premium_book_anchor`: count `33`, avg_brier `0.187949`, vs_raw `0.014275`
- `v28_raw`: count `33`, avg_brier `0.173674`, vs_raw `0.000000`

### spectral_noise
- `book_ask_prior`: count `1`, avg_brier `0.656100`, vs_raw `0.249638`
- `large_disagreement_book_anchor`: count `1`, avg_brier `0.561961`, vs_raw `0.155498`
- `v28_premium_book_anchor`: count `1`, avg_brier `0.406462`, vs_raw `0.000000`
- `v28_raw`: count `1`, avg_brier `0.406462`, vs_raw `0.000000`

## Robustness Views

| view | obs | settled | gross c | best variant | best brier | best vs raw |
|---|---:|---:|---:|---|---:|---:|
| all_observations | 6798 | 6798 | -3233.0 | book_ask_prior | 0.163490 | -0.005396 |
| approved_entries | 173 | 173 | 823.0 | large_disagreement_book_anchor | 0.125893 | -0.007741 |
| rejected_actionable | 6625 | 6625 | -4056.0 | book_ask_prior | 0.164395 | -0.005411 |
| first_per_market_side_source | 464 | 464 | 10.0 | book_ask_prior | 0.202707 | -0.007774 |
| last_per_market_side_source | 464 | 464 | 116.0 | book_ask_prior | 0.060019 | -0.010809 |
