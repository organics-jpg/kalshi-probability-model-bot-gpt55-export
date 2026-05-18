# arXiv Strategy Projection

Research-only same-window replay over refreshed live v28 trades. These are projected gates over recorded entries, not live-trading instructions.

- Generated UTC: `2026-05-07T23:00:57.288806+00:00`
- Matched trades: `632` / `632`
- Live scorer net: `$13.61`

## Live-entry replay strategies

| strategy | ideas | entries | W/L | win rate | net PnL | avg/entry | coverage | train PnL | validation PnL | holdout PnL | rule |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| current_live_v28_replay | baseline | 632 | 285/336 (+11 flat) | 45.9% | $13.61 | 2.2c | 100.0% | $10.48 | $0.03 | $3.10 | All matched live v28 entries from the refreshed scorer window. |
| conformal_consensus_winrate_gate | conformal interval / ensemble agreement | 89 | 49/38 (+2 flat) | 56.3% | $10.57 | 11.9c | 14.1% | $5.95 | $2.64 | $1.98 | Keep current v28 entries only when v28-v22 probability gap <= 0.12 and v28 edge >= 4c. |
| depth_decay_fillability_gate | Dubach depth decay / Lokin state-dependent fill probability | 136 | 57/79 | 41.9% | $21.42 | 15.8c | 21.5% | $10.84 | $4.40 | $6.18 | Keep current v28 entries only when depth/required >= 3, book age <= 750ms, ask <= 80c, and seconds_to_close >= 600. |
| brownian_fpt_sanity_gate | Brownian first-passage / jump-diffusion baseline | 325 | 146/172 (+7 flat) | 45.9% | $27.37 | 8.4c | 51.4% | $15.30 | $7.97 | $4.10 | Keep current v28 entries only when v28 edge >= 3c, seconds_to_close >= 120, and 0.70 <= abs_d_sigma <= 1.10. |
| hybrid_fpt_depth_gate | Brownian FPT + LOB fillability | 163 | 77/85 (+1 flat) | 47.5% | $15.85 | 9.7c | 25.8% | $5.64 | $8.15 | $2.06 | Keep current v28 entries only when edge >= 3c, depth/required >= 8, book age <= 750ms, ask <= 83c, seconds_to_close >= 120, and 0.85 <= abs_d_sigma <= 1.10. |

## Existing candidate crosswalk

These are the strongest current candidate-table rows whose names already match the paper themes. They use existing candidate artifacts rather than the raw live-entry replay above.

| candidate | ideas | entries | W/L | win rate | coverage | net PnL | delta vs live | live ready | source share | blockers |
|---|---|---:|---:|---:|---:|---:|---:|---|---:|---|
| top_component_parent_fill_repair_child / diagnostic_observable_mid_confidence_parent_fill_quarter | Dubach/Lokin execution model | 76 | 67/9 | 88.2% | 75.2% | $22.33 | 872.0c | False | 0.34210526315789475 | diagnostic_prefreeze, source_gate_zero_row_margin |
| dual_lane_overlap_union / top_component_mix_portfolio:rescue_drop15_exit_clock_rows_only + post_penalty_birth_entry_cheap_penalty025_rank_only | Brownian/FPT or path physics | 83 | 68/15 | 81.9% | 82.2% | $18.43 | 481.5c | False | 0.2168674698795181 | needs_own_frozen_forward_birth, live_ready_false |
| raw_p52_book_disagreement_skip / raw_p52_skip_v28_minus_book_gt15pp | conformal/agreement/interval uncertainty | 88 | 52/36 | 59.1% | 87.1% | $-6.19 | -1,980.0c | False | 0.9318181818181818 | net_not_positive, simulated_share_gt_35pct, control_risk_stop_active |

## Notes

- The consensus/conformal row is a proxy using v22-v28 disagreement as interval width; it is not a real Venn-Abers/conformal calibrator yet.
- The Brownian/FPT row is the strongest same-window replay, but it is still retrospective. It needs frozen forward collection before promotion.
- Win rate and PnL diverge here: the best PnL row does not have the best hit rate because payoff size matters.
