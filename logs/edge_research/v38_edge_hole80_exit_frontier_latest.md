# v38 Edge-Hole 80% Exit Frontier

Generated UTC: `2026-05-05T05:54:42.187189+00:00`

## Scope

- Research-only v38 FV entry/exit sweep.
- Requires at least 80% coverage in train, validation, and holdout.
- Uses fees plus a 1c adverse entry-fill haircut for split/day robustness.

## Search Result

- Rows evaluated after 80% coverage prefilter: 560
- Fee+1c positive in train/validation/holdout: 11
- Fee+1c positive in all splits and all UTC days: 0

## Selected Rows

| veto | entry | exit | min cov | min 1c | all 1c | days | worst day | block10 | worst block10 | trades |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| `block_first_edge_12_20` | `edge0_ask100_p0.65_stc0-600` | `prob54` | 81.33% | $0.92 | $7.00 | 4/5 | $-0.69 | 6/10 | $-2.23 | 331 |
| `block_first_edge_12_20` | `edge0_ask100_p0.65_stc60-600` | `prob54` | 81.33% | $0.92 | $6.75 | 4/5 | $-0.70 | 6/10 | $-2.23 | 325 |
| `block_first_edge_12_20` | `edge0_ask100_p0.64_stc0-600` | `prob54` | 82.67% | $0.70 | $6.15 | 4/5 | $-0.59 | 5/10 | $-3.46 | 328 |
| `block_first_edge_12_20` | `edge0_ask100_p0.64_stc60-600` | `prob54` | 82.67% | $0.70 | $5.90 | 4/5 | $-0.60 | 5/10 | $-2.13 | 322 |
| `block_first_edge_12_20` | `edge0_ask100_p0.64_stc0-600` | `prob53` | 82.67% | $0.06 | $4.45 | 4/5 | $-0.59 | 5/10 | $-3.46 | 328 |
| `block_first_edge_12_20` | `edge0_ask100_p0.64_stc60-600` | `prob53` | 82.67% | $0.06 | $4.20 | 4/5 | $-0.60 | 5/10 | $-2.13 | 322 |
| `block_first_edge_12_20` | `edge0_ask100_p0.65_stc0-600` | `prob52` | 81.33% | $0.28 | $6.00 | 3/5 | $-0.69 | 6/10 | $-2.23 | 331 |
| `block_first_edge_12_20` | `edge0_ask100_p0.65_stc60-600` | `prob52` | 81.33% | $0.28 | $5.75 | 3/5 | $-0.70 | 5/10 | $-2.23 | 325 |
| `block_first_edge_12_20` | `edge0_ask100_p0.65_stc0-600` | `prob53` | 81.33% | $0.28 | $5.46 | 3/5 | $-0.69 | 6/10 | $-2.23 | 331 |
| `block_first_edge_12_20` | `edge0_ask100_p0.65_stc60-600` | `prob53` | 81.33% | $0.28 | $5.21 | 3/5 | $-0.70 | 5/10 | $-2.23 | 325 |
| `block_first_edge_12_20` | `edge0_ask100_p0.65_stc0-570` | `prob54` | 80.00% | $0.11 | $2.46 | 3/5 | $-2.13 | 5/10 | $-4.39 | 319 |
| `block_first_edge_12_20` | `edge0_ask100_p0.64_stc120-600` | `prob54` | 80.00% | $-0.13 | $5.08 | 4/5 | $-0.59 | 5/10 | $-3.51 | 319 |
| `block_first_edge_12_20` | `edge0_ask100_p0.64_stc0-600` | `prob52` | 82.67% | $-0.34 | $4.59 | 4/5 | $-0.59 | 5/10 | $-3.46 | 328 |
| `block_first_edge_12_20` | `edge0_ask100_p0.64_stc60-600` | `prob52` | 82.67% | $-0.34 | $4.34 | 4/5 | $-0.60 | 5/10 | $-2.13 | 322 |
| `block_first_edge_12_20` | `edge0_ask100_p0.64_stc120-600` | `prob53` | 80.00% | $-0.77 | $3.38 | 4/5 | $-0.59 | 5/10 | $-3.51 | 319 |
| `block_first_edge_12_20` | `edge0_ask100_p0.64_stc120-600` | `prob52` | 80.00% | $-1.17 | $3.52 | 4/5 | $-0.59 | 5/10 | $-3.51 | 319 |
| `block_first_edge_10_20` | `edge-2_ask100_p0.64_stc0-570` | `prob54` | 80.00% | $-1.61 | $2.78 | 4/5 | $-2.01 | 6/10 | $-4.09 | 318 |
| `block_first_edge_10_18` | `edge-2_ask100_p0.64_stc0-570` | `prob54` | 80.00% | $-1.61 | $2.58 | 4/5 | $-2.03 | 6/10 | $-4.09 | 320 |
| `block_first_edge_10_25` | `edge-2_ask100_p0.64_stc0-570` | `prob54` | 80.00% | $-1.61 | $2.03 | 4/5 | $-2.01 | 6/10 | $-4.09 | 313 |
| `block_first_edge_10_22` | `edge-2_ask100_p0.64_stc0-570` | `prob54` | 80.00% | $-1.61 | $1.70 | 4/5 | $-2.01 | 6/10 | $-4.09 | 316 |
| `block_first_edge_8_20` | `edge-2_ask100_p0.65_stc0-600` | `prob54` | 80.00% | $-1.94 | $8.29 | 4/5 | $-0.15 | 6/10 | $-2.22 | 309 |
| `block_first_edge_8_20` | `edge-2_ask100_p0.65_stc0-600` | `prob52` | 80.00% | $-2.58 | $8.11 | 4/5 | $-0.15 | 6/10 | $-2.68 | 309 |
| `block_first_edge_8_20` | `edge-2_ask100_p0.65_stc0-600` | `prob53` | 80.00% | $-2.58 | $7.45 | 4/5 | $-0.15 | 6/10 | $-2.68 | 309 |
| `block_first_edge_8_20` | `edge-2_ask100_p0.64_stc0-600` | `prob54` | 82.67% | $-2.60 | $6.84 | 4/5 | $-0.15 | 6/10 | $-3.67 | 309 |
| `block_first_edge_8_20` | `edge-2_ask100_p0.64_stc0-600` | `prob53` | 82.67% | $-3.24 | $5.84 | 4/5 | $-0.15 | 6/10 | $-4.13 | 309 |
| `block_first_edge_8_20` | `edge-2_ask100_p0.64_stc0-600` | `prob52` | 82.67% | $-3.64 | $6.10 | 4/5 | $-0.15 | 5/10 | $-4.13 | 309 |
| `block_first_edge_8_20` | `edge-2_ask100_p0.65_stc0-600` | `prob51` | 80.00% | $-4.07 | $5.06 | 4/5 | $-1.64 | 5/10 | $-2.68 | 309 |
| `block_first_edge_8_20` | `edge-2_ask100_p0.64_stc0-600` | `prob51` | 82.67% | $-5.15 | $3.03 | 4/5 | $-1.64 | 5/10 | $-4.15 | 309 |

## Read

- No 80%-coverage row is positive across all splits and all UTC days after fees plus 1c entry haircut.
