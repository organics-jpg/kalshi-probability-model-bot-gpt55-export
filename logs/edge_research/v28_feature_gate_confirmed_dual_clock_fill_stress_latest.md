# v28 Feature-Gate Confirmed Dual-Clock Fill Stress

Research-only; no live bot changes or orders.

- Generated UTC: `2026-05-11T02:20:24.837563+00:00`
- Source artifact: `C:\Users\organ\Desktop\KALSHI PROBABILITY MODEL BOT\logs\edge_research\v28_feature_gate_confirmed_dual_clock_fill_latest.json`
- Policy: `late_collapse90_only`
- Candidate net: `611.250c`
- Delta vs live: `691.250c`
- W/L: `52/13`
- Coverage/source: `80.488%` / `0.364`

## Interpretation

- Research-only fragility stress; no live bot changes or orders.
- Diagnostic live margin is 691.2c.
- Removing the largest single suppression (KXBTC15M-26MAY062015-15, 176.0c) leaves 515.25c vs live.
- Largest component is remove_all_late_collapse90 worth 176.0c; without it the candidate is 515.25c vs live.
- Source gate row margin is -1; coverage is 80.49%.
- Stress blockers: ['source_gate_zero_row_margin', 'row_reconstructed_share_gt_35pct', 'diagnostic_prefreeze', 'dual_clock_rescue_not_independently_frozen', 'confirmed_dual_clock_fill_diagnostic']

## Rule Component Stress

| stress | rows removed | removed delta | stressed net | stressed vs live | still beats live |
|---|---:|---:|---:|---:|---|
| `remove_all_late_collapse90` | 1 | 176.000 | 435.250 | 515.250 | True |

## Top Single-Suppression Stress

| stress | removed delta | stressed net | stressed vs live | still beats live |
|---|---:|---:|---:|---|
| `remove_suppression_KXBTC15M-26MAY062015-15_late_collapse90` | 176.000 | 435.250 | 515.250 | True |
