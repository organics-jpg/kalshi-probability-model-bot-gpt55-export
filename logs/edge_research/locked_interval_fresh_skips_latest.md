# Locked Interval Fresh Skip Audit

Generated UTC: `20260502_184745Z`

## Scope

- Research-only audit; no orders are submitted and no bot files are modified.
- Fresh denominator is recurring BTC 15-minute markets with close time after the frozen lock.
- Lock close time: `2026-05-02T15:00:00+00:00`
- Fresh resolved interval denominator: 12

## Candidate Fresh Coverage

| source | candidate | selected fresh | skipped fresh | fresh coverage |
|---|---|---:|---:|---:|
| `locked_interval_candidates` | `economical_score_min_book_rv15_20260502_1511` | 10/12 | 2 | 83.33% |
| `locked_interval_candidates` | `raw_regime_blend_high_price_20260502_1510` | 10/12 | 2 | 83.33% |
| `locked_interval_candidates` | `raw_score_min_book_rv15_existing_lock` | 10/12 | 2 | 83.33% |
| `locked_interval_candidates` | `staged_score_min_fallback_20260502_1511` | 10/12 | 2 | 83.33% |
| `locked_interval_pure_physics` | `pure_brownian_rv15_spread4_best_high_coverage_20260502_1522` | 10/12 | 2 | 83.33% |
| `locked_interval_pure_physics` | `pure_brownian_rv30_adverse15_high_price_20260502_1522` | 10/12 | 2 | 83.33% |
| `locked_interval_pure_physics` | `pure_brownian_rv30_economical_adverse15_20260502_1522` | 10/12 | 2 | 83.33% |
| `locked_interval_pure_physics` | `pure_physics_mean_rv15_rv30_high_price_20260502_1522` | 10/12 | 2 | 83.33% |
| `locked_interval_logit` | `locked_logit_book_physics_c005_p095_20260502_1512` | 10/12 | 2 | 83.33% |
| `market_interval_fixed` | `market_interval_80coverage` | 10/12 | 2 | 83.33% |

## Skipped Fresh Markets

| source | candidate | market | close | outcome | best score_min ask/sec/win | best regime ask/sec/win | best rv30 ask/sec/win | economical best ask/sec/win |
|---|---|---|---|---|---|---|---|---|
| `locked_interval_candidates` | `economical_score_min_book_rv15_20260502_1511` | `KXBTC15M-26MAY021300-00` | 2026-05-02 17:00:00+00:00 | no | 0.81 @ 100.0c/7.2s/True | 0.91 @ 100.0c/7.2s/True | 0.84 @ 100.0c/7.2s/True | 0.53 @ 59.0c/82.3s/False |
| `locked_interval_candidates` | `economical_score_min_book_rv15_20260502_1511` | `KXBTC15M-26MAY021330-30` | 2026-05-02 17:30:00+00:00 | yes | 0.89 @ 100.0c/4.6s/True | 0.94 @ 100.0c/4.6s/True | 0.87 @ 100.0c/4.6s/True | 0.72 @ 73.0c/79.6s/False |
| `locked_interval_candidates` | `raw_regime_blend_high_price_20260502_1510` | `KXBTC15M-26MAY021300-00` | 2026-05-02 17:00:00+00:00 | no | 0.81 @ 100.0c/7.2s/True | 0.91 @ 100.0c/7.2s/True | 0.84 @ 100.0c/7.2s/True | 0.53 @ 59.0c/82.3s/False |
| `locked_interval_candidates` | `raw_regime_blend_high_price_20260502_1510` | `KXBTC15M-26MAY021330-30` | 2026-05-02 17:30:00+00:00 | yes | 0.89 @ 100.0c/4.6s/True | 0.94 @ 100.0c/4.6s/True | 0.87 @ 100.0c/4.6s/True | 0.72 @ 73.0c/79.6s/False |
| `locked_interval_candidates` | `raw_score_min_book_rv15_existing_lock` | `KXBTC15M-26MAY021300-00` | 2026-05-02 17:00:00+00:00 | no | 0.81 @ 100.0c/7.2s/True | 0.91 @ 100.0c/7.2s/True | 0.84 @ 100.0c/7.2s/True | 0.53 @ 59.0c/82.3s/False |
| `locked_interval_candidates` | `raw_score_min_book_rv15_existing_lock` | `KXBTC15M-26MAY021330-30` | 2026-05-02 17:30:00+00:00 | yes | 0.89 @ 100.0c/4.6s/True | 0.94 @ 100.0c/4.6s/True | 0.87 @ 100.0c/4.6s/True | 0.72 @ 73.0c/79.6s/False |
| `locked_interval_candidates` | `staged_score_min_fallback_20260502_1511` | `KXBTC15M-26MAY021300-00` | 2026-05-02 17:00:00+00:00 | no | 0.81 @ 100.0c/7.2s/True | 0.91 @ 100.0c/7.2s/True | 0.84 @ 100.0c/7.2s/True | 0.53 @ 59.0c/82.3s/False |
| `locked_interval_candidates` | `staged_score_min_fallback_20260502_1511` | `KXBTC15M-26MAY021330-30` | 2026-05-02 17:30:00+00:00 | yes | 0.89 @ 100.0c/4.6s/True | 0.94 @ 100.0c/4.6s/True | 0.87 @ 100.0c/4.6s/True | 0.72 @ 73.0c/79.6s/False |
| `locked_interval_pure_physics` | `pure_brownian_rv15_spread4_best_high_coverage_20260502_1522` | `KXBTC15M-26MAY021300-00` | 2026-05-02 17:00:00+00:00 | no | 0.81 @ 100.0c/7.2s/True | 0.91 @ 100.0c/7.2s/True | 0.84 @ 100.0c/7.2s/True | 0.53 @ 59.0c/82.3s/False |
| `locked_interval_pure_physics` | `pure_brownian_rv15_spread4_best_high_coverage_20260502_1522` | `KXBTC15M-26MAY021330-30` | 2026-05-02 17:30:00+00:00 | yes | 0.89 @ 100.0c/4.6s/True | 0.94 @ 100.0c/4.6s/True | 0.87 @ 100.0c/4.6s/True | 0.72 @ 73.0c/79.6s/False |
| `locked_interval_pure_physics` | `pure_brownian_rv30_adverse15_high_price_20260502_1522` | `KXBTC15M-26MAY021300-00` | 2026-05-02 17:00:00+00:00 | no | 0.81 @ 100.0c/7.2s/True | 0.91 @ 100.0c/7.2s/True | 0.84 @ 100.0c/7.2s/True | 0.53 @ 59.0c/82.3s/False |
| `locked_interval_pure_physics` | `pure_brownian_rv30_adverse15_high_price_20260502_1522` | `KXBTC15M-26MAY021330-30` | 2026-05-02 17:30:00+00:00 | yes | 0.89 @ 100.0c/4.6s/True | 0.94 @ 100.0c/4.6s/True | 0.87 @ 100.0c/4.6s/True | 0.72 @ 73.0c/79.6s/False |
| `locked_interval_pure_physics` | `pure_brownian_rv30_economical_adverse15_20260502_1522` | `KXBTC15M-26MAY021300-00` | 2026-05-02 17:00:00+00:00 | no | 0.81 @ 100.0c/7.2s/True | 0.91 @ 100.0c/7.2s/True | 0.84 @ 100.0c/7.2s/True | 0.53 @ 59.0c/82.3s/False |
| `locked_interval_pure_physics` | `pure_brownian_rv30_economical_adverse15_20260502_1522` | `KXBTC15M-26MAY021330-30` | 2026-05-02 17:30:00+00:00 | yes | 0.89 @ 100.0c/4.6s/True | 0.94 @ 100.0c/4.6s/True | 0.87 @ 100.0c/4.6s/True | 0.72 @ 73.0c/79.6s/False |
| `locked_interval_pure_physics` | `pure_physics_mean_rv15_rv30_high_price_20260502_1522` | `KXBTC15M-26MAY021300-00` | 2026-05-02 17:00:00+00:00 | no | 0.81 @ 100.0c/7.2s/True | 0.91 @ 100.0c/7.2s/True | 0.84 @ 100.0c/7.2s/True | 0.53 @ 59.0c/82.3s/False |
| `locked_interval_pure_physics` | `pure_physics_mean_rv15_rv30_high_price_20260502_1522` | `KXBTC15M-26MAY021330-30` | 2026-05-02 17:30:00+00:00 | yes | 0.89 @ 100.0c/4.6s/True | 0.94 @ 100.0c/4.6s/True | 0.87 @ 100.0c/4.6s/True | 0.72 @ 73.0c/79.6s/False |
| `locked_interval_logit` | `locked_logit_book_physics_c005_p095_20260502_1512` | `KXBTC15M-26MAY021300-00` | 2026-05-02 17:00:00+00:00 | no | 0.81 @ 100.0c/7.2s/True | 0.91 @ 100.0c/7.2s/True | 0.84 @ 100.0c/7.2s/True | 0.53 @ 59.0c/82.3s/False |
| `locked_interval_logit` | `locked_logit_book_physics_c005_p095_20260502_1512` | `KXBTC15M-26MAY021330-30` | 2026-05-02 17:30:00+00:00 | yes | 0.89 @ 100.0c/4.6s/True | 0.94 @ 100.0c/4.6s/True | 0.87 @ 100.0c/4.6s/True | 0.72 @ 73.0c/79.6s/False |
| `market_interval_fixed` | `market_interval_80coverage` | `KXBTC15M-26MAY021300-00` | 2026-05-02 17:00:00+00:00 | no | 0.81 @ 100.0c/7.2s/True | 0.91 @ 100.0c/7.2s/True | 0.84 @ 100.0c/7.2s/True | 0.53 @ 59.0c/82.3s/False |
| `market_interval_fixed` | `market_interval_80coverage` | `KXBTC15M-26MAY021330-30` | 2026-05-02 17:30:00+00:00 | yes | 0.89 @ 100.0c/4.6s/True | 0.94 @ 100.0c/4.6s/True | 0.87 @ 100.0c/4.6s/True | 0.72 @ 73.0c/79.6s/False |

## Read

- Unique skipped fresh markets: 2 (KXBTC15M-26MAY021300-00, KXBTC15M-26MAY021330-30).
- Current fresh coverage is fragile until more post-lock markets resolve.
