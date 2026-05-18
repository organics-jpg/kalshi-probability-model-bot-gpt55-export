# Cross-Dataset Shared Loss Blockers

Generated UTC: `20260502_184820Z`

## Scope

- Research-only probe; no orders are submitted and no bot files or live processes are touched.
- Base policy: `choose=score_mean_book_rv15; score_mean_book_rv15>=0.8; ask<=95; sec_to_close>=60`.
- Blockers are physical/book/path constraints applied before the first eligible market selection.
- Volume denominator is recurring BTC 15-minute markets on both live captures.

## Data

- Current intervals: 159
- V21 intervals: 221
- Current chosen decision rows: 9190
- V21 chosen decision rows: 3277
- Single blockers generated: 87
- Candidate blocker rows evaluated: 341
- Both-dataset target passes: 0
- Both-dataset Wilson passes: 0

## Best Blockers

| rank | blockers | target | current acc/cov | v21 acc/cov | current holdout | v21 holdout | median ask |
|---:|---|---:|---:|---:|---:|---:|---:|
| 1 | `drift_p_5m_rv_15m>=0.8 AND book_p_side>=0.8` | False | 88.57%/88.05% | 88.71%/84.16% | 89.29%/87.50% | 91.89%/82.22% | 87.0 |
| 2 | `drift_p_5m_rv_15m>=0.8` | False | 87.94%/88.68% | 87.70%/84.62% | 89.29%/87.50% | 89.19%/82.22% | 87.0 |
| 3 | `drift_p_5m_rv_15m>=0.8 AND signed_move_5m>=0` | False | 87.94%/88.68% | 87.70%/84.62% | 89.29%/87.50% | 89.19%/82.22% | 87.0 |
| 4 | `drift_p_5m_rv_15m>=0.8 AND abs_book_rv15_gap<=0.3` | False | 87.94%/88.68% | 87.70%/84.62% | 89.29%/87.50% | 89.19%/82.22% | 87.0 |
| 5 | `drift_p_5m_rv_15m>=0.8 AND abs_book_rv15_gap<=0.4` | False | 87.94%/88.68% | 87.70%/84.62% | 89.29%/87.50% | 89.19%/82.22% | 87.0 |
| 6 | `drift_p_5m_rv_15m>=0.8 AND abs_book_rv30_gap<=0.3` | False | 87.94%/88.68% | 87.70%/84.62% | 89.29%/87.50% | 89.19%/82.22% | 87.0 |
| 7 | `drift_p_5m_rv_15m>=0.8 AND abs_book_rv30_gap<=0.4` | False | 87.94%/88.68% | 87.70%/84.62% | 89.29%/87.50% | 89.19%/82.22% | 87.0 |
| 8 | `drift_p_5m_rv_15m>=0.8 AND spread_cents<=3` | False | 87.94%/88.68% | 87.70%/84.62% | 89.29%/87.50% | 89.19%/82.22% | 87.0 |
| 9 | `drift_p_5m_rv_15m>=0.8 AND spread_cents<=4` | False | 87.94%/88.68% | 87.70%/84.62% | 89.29%/87.50% | 89.19%/82.22% | 87.0 |
| 10 | `drift_p_5m_rv_15m>=0.8 AND spread_cents<=5` | False | 87.94%/88.68% | 87.70%/84.62% | 89.29%/87.50% | 89.19%/82.22% | 87.0 |
| 11 | `drift_p_5m_rv_15m>=0.8 AND spread_cents<=8` | False | 87.94%/88.68% | 87.70%/84.62% | 89.29%/87.50% | 89.19%/82.22% | 87.0 |
| 12 | `drift_p_5m_rv_15m>=0.8 AND seconds_to_close<=900` | False | 87.94%/88.68% | 87.70%/84.62% | 89.29%/87.50% | 89.19%/82.22% | 87.0 |
| 13 | `drift_p_5m_rv_15m>=0.8 AND ask_cents<=95` | False | 87.94%/88.68% | 87.70%/84.62% | 89.29%/87.50% | 89.19%/82.22% | 87.0 |
| 14 | `drift_p_5m_rv_15m>=0.8 AND margin_per_rv_sigma_15m>=-0.5` | False | 87.94%/88.68% | 87.70%/84.62% | 89.29%/87.50% | 89.19%/82.22% | 87.0 |
| 15 | `drift_p_5m_rv_15m>=0.8 AND margin_per_rv_sigma_15m>=0` | False | 87.94%/88.68% | 87.70%/84.62% | 89.29%/87.50% | 89.19%/82.22% | 87.0 |
| 16 | `drift_p_5m_rv_15m>=0.8 AND margin_per_rv_sigma_15m>=0.25` | False | 87.94%/88.68% | 87.70%/84.62% | 89.29%/87.50% | 89.19%/82.22% | 87.0 |
| 17 | `drift_p_5m_rv_15m>=0.8 AND margin_per_rv_sigma_15m>=0.5` | False | 87.94%/88.68% | 87.70%/84.62% | 89.29%/87.50% | 89.19%/82.22% | 87.0 |
| 18 | `drift_p_5m_rv_15m>=0.8 AND margin_per_rv_sigma_30m>=-0.5` | False | 87.94%/88.68% | 87.70%/84.62% | 89.29%/87.50% | 89.19%/82.22% | 87.0 |
| 19 | `drift_p_5m_rv_15m>=0.8 AND margin_per_rv_sigma_30m>=0` | False | 87.94%/88.68% | 87.70%/84.62% | 89.29%/87.50% | 89.19%/82.22% | 87.0 |
| 20 | `drift_p_5m_rv_15m>=0.8 AND margin_per_rv_sigma_30m>=0.25` | False | 87.94%/88.68% | 87.70%/84.62% | 89.29%/87.50% | 89.19%/82.22% | 87.0 |

## Read

No physical blocker set clears the 95% accuracy / 80% recurring-market coverage target on both datasets.
The best ranked blocker set still bottoms out at 86.67% split accuracy with 84.16% minimum all-dataset coverage.
