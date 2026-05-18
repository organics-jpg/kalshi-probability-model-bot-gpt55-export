# Current Strategy Improvement Audit

Generated UTC: `20260505_031318Z`

## Objective Restatement

- Baseline strategy: `mushroom_v28_live_gate_ev_exit_size2`.
- Improve net P&L through research-only shadow analysis across entries, exits, sizing, fills, filters, and fair-value logic.
- Target: at least +50% projected net P&L versus baseline, which currently means $29.28.
- Never change live code, stop the bot, or place research trades under this goal.
- Require pre-registered forward proof and anti-overfit gates before any recommendation.

## Prompt-to-Artifact Checklist

| requirement | evidence artifact | current evidence | status |
|---|---|---|---|
| Current live baseline | `logs\edge_research\v39_entry_exit_strategy_projection_latest.json` | 226 entries; net $19.52; target $29.28 | pass |
| +50% net-P&L target | candidate rows below | target-pass candidates: 0; ready candidates: 0 | fail |
| 75-80% coverage | projection and strict rows below | broad floor 75.00%, preferred 80.00% | mixed |
| Forward sample size | `logs\edge_research\profit_lock_sample_size_requirements_latest.json` | broad gate 200; overlay gate 100 | fail |
| Bayesian/Wilson confidence | `logs\edge_research\profit_lock_bayesian_ev_monitor_latest.json` | strict ready count: 0 | fail |
| Pre-registration state | `logs\edge_research\profit_lock_pending_signal_registry_latest.csv` | pending registry rows: 33 | pass |
| Entry/exit/fair-value search | `logs\edge_research\v39_entry_exit_strategy_projection_latest.json` | projection candidates: 34 | diagnostic |
| Exit overlay search | `logs\edge_research\live_v28_exit_value_audit_latest.json` | exit candidates: 13 | diagnostic |
| Existing forward-shadow gates | `logs\edge_research\v38_edge_hole_promotion_gate_latest.json` | forward-gate candidates: 1 | in progress |
| Live safety | process/log checks in thread | no live-code edits required by this audit | pass |

## Baseline

- Strategy: `mushroom_v28_live_gate_ev_exit_size2`
- Entries: 226
- Completed round trips: 168
- Net P&L: $19.52 on $411.39
- ROI: 4.74%
- +50% target: $29.28; required delta: $9.76

## Entry/Exit Replay Candidates

| candidate | net | ROI | coverage | splits+ | target | forward proof | ready |
|---|---:|---:|---:|---|---|---|---|
| `v38_long60_antipersist | edge-2_ask100_p0.60_stc0-900 | hold` | $18.50 | 4.17% | 96.97% | False | False | False | False |
| `v38_long60_antipersist | edge0_ask100_p0.60_stc0-900 | hold` | $18.18 | 4.17% | 93.94% | True | False | False | False |
| `v39_midband_v28_fallback | edge-2_ask100_p0.60_stc0-900 | hold` | $18.18 | 4.10% | 96.97% | False | False | False | False |
| `v39_midband_v28_fallback | edge0_ask100_p0.60_stc0-900 | hold` | $17.92 | 4.11% | 93.94% | True | False | False | False |
| `v38_long60_antipersist | edge-2_ask80_p0.60_stc0-900 | hold` | $15.62 | 4.51% | 83.33% | True | False | False | False |
| `v39_midband_v28_fallback | edge-2_ask80_p0.60_stc0-900 | hold` | $14.86 | 4.33% | 82.32% | True | False | False | False |
| `v38_long60_antipersist | edge1_ask100_p0.60_stc0-900 | hold` | $14.86 | 3.60% | 92.42% | False | False | False | False |
| `v38_long60_antipersist | edge0_ask80_p0.60_stc0-900 | hold` | $14.62 | 4.26% | 81.82% | True | False | False | False |
| `v28_live_surface | edge-2_ask70_p0.50_stc0-900 | prob45` | $14.60 | 4.54% | 93.94% | True | False | False | False |
| `v39_midband_v28_fallback | edge0_ask80_p0.60_stc0-900 | hold` | $14.50 | 4.27% | 80.30% | True | False | False | False |

## Strict Shadow Candidates

| lock | fresh | acc | coverage | size2 observed | scaled to baseline entries | P(edge) | p05 edge | Wilson | target | ready |
|---|---:|---:|---:|---:|---:|---:|---:|---|---|---|
| `kinetic_combo_price_guard` | 67/33 of 100 | 67.00% | 63.29% | $3.84 | $8.68 | 0.642 | -6.242516860460857c | False | False | False |
| `logit_blend_edge10` | 48/27 of 75 | 64.00% | 96.15% | $2.62 | $7.89 | 0.608 | -7.761849586089448c | False | False | False |
| `impulse_reversal_book_margin_fade` | 33/25 of 58 | 56.90% | 95.08% | $1.66 | $6.47 | 0.579 | -9.34652783555591c | False | False | False |
| `book_margin` | 73/32 of 105 | 69.52% | 97.22% | $2.70 | $5.81 | 0.593 | -6.5198672251856085c | False | False | False |
| `book_margin_gap015` | 61/28 of 89 | 68.54% | 87.25% | $2.18 | $5.54 | 0.575 | -7.446035013199411c | False | False | False |
| `challenger` | 87/41 of 128 | 67.97% | 64.32% | $2.84 | $5.01 | 0.589 | -6.047183295485582c | False | False | False |
| `book_margin_early` | 70/31 of 101 | 69.31% | 97.12% | $2.10 | $4.70 | 0.569 | -6.970132639337107c | False | False | False |
| `touch_overlay` | 84/54 of 138 | 60.87% | 73.02% | $2.38 | $3.90 | 0.572 | -6.1464480673922415c | False | False | False |
| `original` | 92/45 of 137 | 67.15% | 68.50% | $2.16 | $3.56 | 0.563 | -6.094265385684958c | False | False | False |
| `kinetic_guard` | 89/37 of 126 | 70.63% | 67.74% | $1.44 | $2.58 | 0.536 | -6.536114534100007c | False | False | False |

## Exit Overlay Diagnostics

| rule | delta vs actual exits | adjusted net | suppressed | strict | target delta | ready |
|---|---:|---:|---:|---|---|---|
| `suppress_exit_if_exit_bid_cents<=65` | $3.11 | $-3.21 | 34 | False | False | False |
| `suppress_exit_if_btc_age_ms>=500` | $1.50 | $-4.82 | 39 | False | False | False |
| `suppress_exit_if_sigma_t_dollars>=100` | $-0.12 | $-6.44 | 36 | False | False | False |
| `suppress_exit_if_sigma_t_dollars>=150` | $-0.18 | $-6.50 | 13 | False | False | False |
| `suppress_exit_if_p_hold<=0.72` | $-0.26 | $-6.58 | 37 | False | False | False |

## Forward-Shadow Gates

| candidate | finalized/required | coverage | forward net | forward ROI | retro fee+1c net | gate pass | target | ready |
|---|---:|---:|---:|---:|---:|---|---|---|
| `block_market_first_edge_8_20` | 7/50 | 70.00% | $-0.09 | -0.78% | $6.50 | False | False | False |

## Decision

- Not complete: no candidate clears the +50% baseline P&L target with forward-proof and anti-overfit gates.
- Continue shadow collection and only report material changes: new leader, target pass, gate failure/pass, or major failure pattern.
