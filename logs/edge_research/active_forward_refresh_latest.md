# Active Forward Refresh

Generated UTC: `2026-05-05T09:22:25.171358+00:00`

## Scope

- Research-only one-shot refresh of active strict-forward FV candidates.
- Runs scripts serially to avoid shared candle/cache races.
- Live bot and order paths untouched.

## Steps

| step | script | seconds | code |
|---|---|---:|---:|
| `v47_shadow` | `probe_v47_recross_hazard_shadow_monitor.py` | 57.8 | 0 |
| `v47_denominator` | `probe_v47_recross_hazard_forward_denominator.py` | 51.8 | 0 |
| `v50_shadow` | `probe_v50_thin_edge_certainty_shadow_monitor.py` | 54.7 | 0 |
| `v50_denominator` | `probe_v50_thin_edge_certainty_forward_denominator.py` | 52.5 | 0 |
| `v53_shadow` | `probe_v53_weak_recross_thin_edge_shadow_monitor.py` | 54.2 | 0 |
| `v53_denominator` | `probe_v53_weak_recross_thin_edge_forward_denominator.py` | 52.4 | 0 |
| `v55_shadow` | `probe_v55_book_anchor_recross_shadow_monitor.py` | 59.5 | 0 |
| `v55_denominator` | `probe_v55_book_anchor_recross_forward_denominator.py` | 51.2 | 0 |
| `v57_shadow` | `probe_v57_v55_hold15_shadow_monitor.py` | 49.2 | 0 |
| `v57_denominator` | `probe_v57_v55_hold15_forward_denominator.py` | 53.5 | 0 |
| `current_comparison` | `probe_current_fv_candidate_comparison.py` | 1.1 | 0 |

## Read

- Refresh completed successfully. Consolidated comparison was rebuilt.
