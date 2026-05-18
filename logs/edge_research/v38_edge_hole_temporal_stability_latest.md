# v38 Edge-Hole Temporal Stability

Generated UTC: `2026-05-05T00:57:19.141466+00:00`

## Scope

- Temporal audit of saved retrospective candidate trades.
- Compares primary edge-hole candidate against the no-veto baseline.

## Overall

| candidate | trades | gross | fee net | fee+1c entry | fee ROI | positive days | worst 1c day |
|---|---:|---:|---:|---:|---:|---:|---:|
| `baseline_no_veto` | 314 | $18.64 | $7.23 | $0.95 | 1.47% | 2/4 | $-1.41 |
| `block_market_first_edge_8_20` | 267 | $20.82 | $11.84 | $6.50 | 2.76% | 4/4 | $0.38 |

## Primary By Day

| day UTC | trades | gross | fee net | fee+1c entry | exits |
|---|---:|---:|---:|---:|---:|
| `2026-05-01` | 65 | $4.08 | $1.68 | $0.38 | 20 |
| `2026-05-02` | 80 | $6.22 | $3.64 | $2.04 | 19 |
| `2026-05-03` | 70 | $5.30 | $3.12 | $1.72 | 16 |
| `2026-05-04` | 52 | $5.22 | $3.40 | $2.36 | 13 |

## Primary By Split

| split | trades | gross | fee net | fee+1c entry |
|---|---:|---:|---:|---:|
| `holdout` | 56 | $4.70 | $2.69 | $1.57 |
| `train` | 159 | $11.08 | $5.77 | $2.59 |
| `validation` | 52 | $5.04 | $3.38 | $2.34 |

## Read

- Primary candidate has 4/4 positive UTC days after fees plus a 1c entry haircut.
- Worst UTC day after fees plus 1c entry is $0.38.
- This improves the retrospective case but does not replace strict-forward validation.
