# v28 Target-Coverage Promotion Audit

- Ready for promotion review: `False`
- Policy: `raw_p50_turbulence_valve_edge4_p60_recross75_near25`
- Overlay: `book_probability`
- Entries/settled/coverage: `112/112/73.684211`
- Net cents: `-626.000000`
- Brier mean/p95: `-0.014913/0.000643`
- Logloss mean/p95: `-0.026989/0.005781`
- Settled rows to 30: `0`

## Checks

| check | pass | actual | required | evidence |
|---|---:|---|---|---|
| target_coverage_band | False | `73.68421052631578` | `75.0-90.0` | C:\Users\organ\Desktop\KALSHI PROBABILITY MODEL BOT\logs\edge_research\v28_target_coverage_fv_sequential_evidence_latest.json |
| settled_forward_sample | True | `112` | `>= 30` | C:\Users\organ\Desktop\KALSHI PROBABILITY MODEL BOT\logs\edge_research\v28_target_coverage_fv_sequential_evidence_latest.json |
| positive_forward_pnl | False | `-626.0` | `> 0.0` | C:\Users\organ\Desktop\KALSHI PROBABILITY MODEL BOT\logs\edge_research\v28_target_coverage_fv_sequential_evidence_latest.json |
| brier_interval_strictly_better_than_raw | False | `0.0006431900556874973` | `< 0` | C:\Users\organ\Desktop\KALSHI PROBABILITY MODEL BOT\logs\edge_research\v28_target_coverage_fv_sequential_evidence_latest.json |
| logloss_interval_strictly_better_than_raw | False | `0.005780956177999605` | `< 0` | C:\Users\organ\Desktop\KALSHI PROBABILITY MODEL BOT\logs\edge_research\v28_target_coverage_fv_sequential_evidence_latest.json |
| live_gate_not_accidentally_ready | True | `False` | `False until all blockers clear intentionally` | C:\Users\organ\Desktop\KALSHI PROBABILITY MODEL BOT\logs\edge_research\v28_live_trade_readiness_latest.json |

## Notes

- This is only a promotion-review audit; it does not change live behavior.
- The live-readiness gate should remain false until sample size and risk controls are intentionally cleared.
