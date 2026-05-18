# v28 Promotion Readiness

- Ready for promotion review: `False`
- Reason: `evidence_incomplete_or_failed`
- Current best variant: `book_ask_prior`
- Current best entry policy: `book_plus_03_cheap_convex`

## Checks

| check | pass | actual | required | evidence |
|---|---:|---|---|---|
| settled_forward_observation_sample | True | `795` | `>= 100` | C:\Users\organ\Desktop\KALSHI PROBABILITY MODEL BOT\logs\edge_research\v28_shadow_fv_variants_latest.json |
| watched_market_sample | True | `181` | `>= 50` | C:\Users\organ\Desktop\KALSHI PROBABILITY MODEL BOT\logs\edge_research\v28_continuous_scorecard_latest.json |
| coverage_target | False | `59.11602209944752` | `>= 75.0%` | C:\Users\organ\Desktop\KALSHI PROBABILITY MODEL BOT\logs\edge_research\v28_continuous_scorecard_latest.json |
| risk_stop_clear | False | `True` | `False` | C:\Users\organ\Desktop\KALSHI PROBABILITY MODEL BOT\logs\edge_research\v28_continuous_scorecard_latest.json |
| nonnegative_forward_pnl | True | `823.0` | `>= 0.0` | C:\Users\organ\Desktop\KALSHI PROBABILITY MODEL BOT\logs\edge_research\v28_continuous_scorecard_latest.json |
| v28_beats_book_brier | False | `0.007316655838284281` | `<= -0.001` | C:\Users\organ\Desktop\KALSHI PROBABILITY MODEL BOT\logs\edge_research\v28_shadow_fv_variants_latest.json |
| top_candidate_beats_book_brier | False | `{'variant': 'book_ask_prior', 'brier_minus_book_prior': 0.0}` | `<= -0.001` | C:\Users\organ\Desktop\KALSHI PROBABILITY MODEL BOT\logs\edge_research\v28_shadow_fv_variants_latest.json |
| book_disagreement_confirms_v28 | False | `0.007316655838284272` | `<= -0.001` | C:\Users\organ\Desktop\KALSHI PROBABILITY MODEL BOT\logs\edge_research\v28_book_disagreement_calibration_latest.json |
| calibration_error_bounded | True | `0.0015535597484276353` | `abs <= 0.05` | C:\Users\organ\Desktop\KALSHI PROBABILITY MODEL BOT\logs\edge_research\v28_forward_calibration_latest.json |
| candidate_not_worse_than_raw_v28 | True | `{'top_variant': 'book_ask_prior', 'top_brier': 0.1559896855345912, 'raw_brier': 0.16330634137287547}` | `top is raw v28 or strictly improves raw v28` | C:\Users\organ\Desktop\KALSHI PROBABILITY MODEL BOT\logs\edge_research\v28_shadow_fv_variants_latest.json |
| broad_entry_policy_has_sample | False | `{'policy': 'book_plus_03_cheap_convex', 'resolved': 92}` | `resolved >= 100` | C:\Users\organ\Desktop\KALSHI PROBABILITY MODEL BOT\logs\edge_research\v28_shadow_entry_policy_bakeoff_latest.json |
| broad_entry_policy_reaches_coverage | False | `{'policy': 'book_plus_03_cheap_convex', 'coverage_pct': 50.82872928176796}` | `>= 75.0%` | C:\Users\organ\Desktop\KALSHI PROBABILITY MODEL BOT\logs\edge_research\v28_shadow_entry_policy_bakeoff_latest.json |
| broad_entry_policy_nonnegative | False | `{'policy': 'book_plus_03_cheap_convex', 'gross_cents': 916.0, 'losses': 60}` | `nonnegative gross and losses not dominant` | C:\Users\organ\Desktop\KALSHI PROBABILITY MODEL BOT\logs\edge_research\v28_shadow_entry_policy_bakeoff_latest.json |

## Notes

- This audit only permits review; it does not approve live deployment.
- Coverage is checked because the original goal asked for 75-80% market participation.
- The updated v28 mandate treats coverage as soft, but low coverage still needs explicit ROI justification.
