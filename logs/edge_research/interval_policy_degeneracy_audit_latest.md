# Interval Policy Degeneracy Audit

Generated UTC: `20260502_184704Z`

## Scope

- Research-only audit; no orders are submitted and no bot files are modified.
- Resolved recurring BTC 15-minute market intervals: 159
- P&L is held-to-settlement proxy before Kalshi fees.
- Wilson lower bounds are 95% confidence lower bounds for realized accuracy.

## Audited Policies

| policy | acc | Wilson low | coverage | gross P&L | ROI | median ask | ask>=95 | ask=100 | median sec | flags |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| `best_raw_target_pass` | 99.29% | 96.07% | 88.05% | 199.0c | 1.45% | 98.00 | 140 | 27 | 172.53 | median_ask_ge_95, p75_ask_ge_97, uses_ask_cap_100, not_non_degenerate |
| `best_economical_80coverage` | 87.76% | 81.47% | 92.45% | 158.0c | 1.24% | 86.00 | 8 | 0 | 468.64 | wilson_lower_below_95, not_non_degenerate |
| `best_economical_95accuracy` | 100.00% | 92.87% | 31.45% | 250.0c | 5.26% | 95.00 | 50 | 0 | 295.49 | median_ask_ge_95, wilson_lower_below_95, not_non_degenerate |
| `best_any_80coverage_by_test_accuracy` | 99.29% | 96.07% | 88.05% | 199.0c | 1.45% | 98.00 | 140 | 27 | 172.53 | median_ask_ge_95, p75_ask_ge_97, uses_ask_cap_100, not_non_degenerate |

## best_raw_target_pass

- Policy: `choose=score_min_book_rv15; score_min_book_rv15>=0.95; ask<=100; sec_to_close>=0`
- Target pass: True; coverage pass: True; nondegenerate pass: False
- train: 85/86 wins, 98.84% accuracy, 90.53% coverage, Wilson low 93.70%, P&L 76.0c
- validation: 27/27 wins, 100.00% accuracy, 84.38% coverage, Wilson low 87.54%, P&L 63.0c
- holdout: 27/27 wins, 100.00% accuracy, 84.38% coverage, Wilson low 87.54%, P&L 60.0c

| loss | entry utc | market | side | outcome | ask | sec left | book p | rv15 p | drift p | margin rv15 | adverse15 | pnl |
|---:|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 2026-05-01 16:07:12.630000+00:00 | `KXBTC15M-26MAY011215-15` | yes | no | 96.00 | 467.37 | 0.96 | 0.96 | 0.98 | 1.72 | 0.00 | -96.0c |

## best_economical_80coverage

- Policy: `choose=score_mean_book_rv15; score_mean_book_rv15>=0.8; ask<=95; sec_to_close>=60`
- Target pass: False; coverage pass: True; nondegenerate pass: False
- train: 77/88 wins, 87.50% accuracy, 92.63% coverage, Wilson low 78.99%, P&L 83.0c
- validation: 27/31 wins, 87.10% accuracy, 96.88% coverage, Wilson low 71.15%, P&L -10.0c
- holdout: 25/28 wins, 89.29% accuracy, 87.50% coverage, Wilson low 72.80%, P&L 85.0c

| loss | entry utc | market | side | outcome | ask | sec left | book p | rv15 p | drift p | margin rv15 | adverse15 | pnl |
|---:|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 2026-05-01 06:51:08.236000+00:00 | `KXBTC15M-26MAY010300-00` | no | yes | 87.00 | 531.76 | 0.86 | 0.79 | 1.00 | 0.80 | 0.00 | -87.0c |
| 2 | 2026-05-01 08:04:01.059000+00:00 | `KXBTC15M-26MAY010415-15` | no | yes | 81.00 | 658.94 | 0.81 | 0.84 | 1.00 | 1.00 | 0.00 | -81.0c |
| 3 | 2026-05-01 11:51:06.653000+00:00 | `KXBTC15M-26MAY010800-00` | no | yes | 79.00 | 533.35 | 0.79 | 0.83 | 1.00 | 0.95 | 9.35 | -79.0c |
| 4 | 2026-05-01 12:11:38.261000+00:00 | `KXBTC15M-26MAY010815-15` | no | yes | 91.00 | 201.74 | 0.91 | 0.70 | 0.79 | 0.52 | 31.40 | -91.0c |
| 5 | 2026-05-01 13:34:00.118000+00:00 | `KXBTC15M-26MAY010945-45` | yes | no | 86.00 | 659.88 | 0.85 | 0.92 | 1.00 | 1.40 | 0.00 | -86.0c |
| 6 | 2026-05-01 14:11:17.735000+00:00 | `KXBTC15M-26MAY011015-15` | no | yes | 89.00 | 222.26 | 0.89 | 0.79 | 0.76 | 0.80 | 0.00 | -89.0c |
| 7 | 2026-05-01 15:07:37.321000+00:00 | `KXBTC15M-26MAY011115-15` | no | yes | 85.00 | 442.68 | 0.84 | 0.78 | 0.82 | 0.78 | 0.00 | -85.0c |
| 8 | 2026-05-01 16:05:12.463000+00:00 | `KXBTC15M-26MAY011215-15` | yes | no | 93.00 | 587.54 | 0.93 | 0.76 | 0.99 | 0.70 | 24.02 | -93.0c |
| 9 | 2026-05-02 00:04:11.439000+00:00 | `KXBTC15M-26MAY012015-15` | yes | no | 86.00 | 648.56 | 0.85 | 0.83 | 1.00 | 0.95 | 0.00 | -86.0c |
| 10 | 2026-05-02 00:40:00.080000+00:00 | `KXBTC15M-26MAY012045-45` | no | yes | 86.00 | 299.92 | 0.85 | 0.79 | 0.98 | 0.79 | 0.00 | -86.0c |
| 11 | 2026-05-02 01:33:19.548000+00:00 | `KXBTC15M-26MAY012145-45` | yes | no | 85.00 | 700.45 | 0.84 | 0.81 | 1.00 | 0.89 | 0.00 | -85.0c |
| 12 | 2026-05-02 02:08:53.173000+00:00 | `KXBTC15M-26MAY012215-15` | yes | no | 90.00 | 366.83 | 0.89 | 0.78 | 0.87 | 0.76 | 0.00 | -90.0c |
| 13 | 2026-05-02 02:52:26.889000+00:00 | `KXBTC15M-26MAY012300-00` | yes | no | 95.00 | 453.11 | 0.94 | 0.71 | 0.88 | 0.55 | 0.00 | -95.0c |
| 14 | 2026-05-02 08:52:13.724000+00:00 | `KXBTC15M-26MAY020500-00` | yes | no | 79.00 | 466.28 | 0.79 | 0.82 | 1.00 | 0.92 | 0.00 | -79.0c |
| 15 | 2026-05-02 09:31:02.261000+00:00 | `KXBTC15M-26MAY020545-45` | no | yes | 83.00 | 837.74 | 0.82 | 0.85 | 1.00 | 1.03 | 0.00 | -83.0c |
| 16 | 2026-05-02 11:49:45.477000+00:00 | `KXBTC15M-26MAY020800-00` | no | yes | 89.00 | 614.52 | 0.89 | 0.73 | 0.88 | 0.60 | 0.00 | -89.0c |
| 17 | 2026-05-02 13:52:13.777000+00:00 | `KXBTC15M-26MAY021000-00` | no | yes | 90.00 | 466.22 | 0.90 | 0.76 | 0.82 | 0.72 | 36.38 | -90.0c |
| 18 | 2026-05-02 17:36:10.907000+00:00 | `KXBTC15M-26MAY021345-45` | yes | no | 85.00 | 529.09 | 0.84 | 0.80 | 0.98 | 0.86 | 0.00 | -85.0c |

## best_economical_95accuracy

- Policy: `choose=book_p_side; book_p_side>=0.95; ask<=95; sec_to_close>=60`
- Target pass: False; coverage pass: False; nondegenerate pass: False
- train: 31/31 wins, 100.00% accuracy, 32.63% coverage, Wilson low 88.97%, P&L 155.0c
- validation: 10/10 wins, 100.00% accuracy, 31.25% coverage, Wilson low 72.25%, P&L 50.0c
- holdout: 9/9 wins, 100.00% accuracy, 28.12% coverage, Wilson low 70.09%, P&L 45.0c

## best_any_80coverage_by_test_accuracy

- Policy: `choose=score_min_book_rv15; score_min_book_rv15>=0.95; ask<=100; sec_to_close>=0`
- Target pass: True; coverage pass: True; nondegenerate pass: False
- train: 85/86 wins, 98.84% accuracy, 90.53% coverage, Wilson low 93.70%, P&L 76.0c
- validation: 27/27 wins, 100.00% accuracy, 84.38% coverage, Wilson low 87.54%, P&L 63.0c
- holdout: 27/27 wins, 100.00% accuracy, 84.38% coverage, Wilson low 87.54%, P&L 60.0c

| loss | entry utc | market | side | outcome | ask | sec left | book p | rv15 p | drift p | margin rv15 | adverse15 | pnl |
|---:|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 2026-05-01 16:07:12.630000+00:00 | `KXBTC15M-26MAY011215-15` | yes | no | 96.00 | 467.37 | 0.96 | 0.96 | 0.98 | 1.72 | 0.00 | -96.0c |

## Read

- The raw target pass covers 140/159 intervals at 99.29%, but its Wilson lower bound is only 96.07% and median ask is 98.00c.
- The best economical 80%-coverage policy covers 92.45%, but accuracy is only 87.76%.
- The best economical >=95%-accuracy policy reaches 100.00%, but coverage is only 31.45%.
- Current evidence does not verify a nondegenerate, sample-size-safe fair-value model that clears both 95% realized accuracy and >=80% recurring market coverage.
