# v28 Source-Aware FV Promotion Audit

- Ready for implementation planning: `False`
- Overlay: `book_probability`
- Settled/approved/simulated/share: `285/180/105/0.368421`
- Brier/delta: `0.159476/-0.008784`
- Logloss/delta: `0.492900/-0.040140`
- Calibration error: `0.039860`
- Robustness blockers: `leave_one_market_failure, single_market_contribution_gt_50pct`
- Leave-one-market failures / dominant share: `12/7.336170`

## Checks

| check | pass | actual | required | evidence |
|---|---:|---|---|---|
| expected_overlay_is_best | False | `book_probability` | `source_aware_approved_book_target_logit125_p60_only` | C:\Users\organ\Desktop\KALSHI PROBABILITY MODEL BOT\logs\edge_research\v28_source_aware_fv_overlay_validator_latest.json |
| settled_rows_gte_30 | True | `285` | `>= 30` | C:\Users\organ\Desktop\KALSHI PROBABILITY MODEL BOT\logs\edge_research\v28_source_aware_fv_overlay_validator_latest.json |
| approved_rows_gte_10 | True | `180` | `>= 10` | C:\Users\organ\Desktop\KALSHI PROBABILITY MODEL BOT\logs\edge_research\v28_source_aware_fv_overlay_validator_latest.json |
| simulated_share_lte_35pct | False | `0.3684210526315789` | `<= 0.35` | C:\Users\organ\Desktop\KALSHI PROBABILITY MODEL BOT\logs\edge_research\v28_source_aware_fv_overlay_validator_latest.json |
| brier_better_than_raw | True | `-0.008784259450245635` | `< 0` | C:\Users\organ\Desktop\KALSHI PROBABILITY MODEL BOT\logs\edge_research\v28_source_aware_fv_overlay_validator_latest.json |
| logloss_better_than_raw | True | `-0.04014041423512027` | `< 0` | C:\Users\organ\Desktop\KALSHI PROBABILITY MODEL BOT\logs\edge_research\v28_source_aware_fv_overlay_validator_latest.json |
| freeze_audit_no_failures | True | `0` | `0` | C:\Users\organ\Desktop\KALSHI PROBABILITY MODEL BOT\logs\edge_research\v28_anti_overfit_freeze_audit_latest.json |
| robustness_audit_no_blockers | False | `['leave_one_market_failure', 'single_market_contribution_gt_50pct']` | `none` | C:\Users\organ\Desktop\KALSHI PROBABILITY MODEL BOT\logs\edge_research\v28_source_aware_fv_robustness_audit_latest.json |

## Notes

- This is not live bot approval; it says whether the FV candidate has enough evidence quality to deserve planning/continued monitoring.
- The candidate is source-aware: approved rows use book anchoring; target-coverage rejected rows use strong-row logit sharpening.
- Robustness blockers mean the candidate remains a watch candidate, not an implementation candidate.
- A true live deployment would still need an implementation plan, tests, and a no-trade dry validation against current live telemetry.
