# v46 v45 Entry Refinement

Generated UTC: `2026-05-05T05:58:49.729004+00:00`

## Scope

- Research-only local refinement around the refreshed v45 lead.
- Sweeps ask caps, p-side floors, edge floors, max seconds-to-close, and probability exits.
- Requires at least 80% split coverage for promotion-style rows.

## Search Result

- Rows evaluated at 75%+ coverage: 56
- Rows at 80%+ coverage: 16
- Rows positive across splits and all UTC days after fees plus 1c entry: 2

## Selected Rows

| entry | exit | min cov | min 1c | all 1c | days | block10 | trades | avg ask |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| `edge0_ask100_p0.65_stc0-600` | `prob54` | 81.33% | $0.45 | $10.55 | 5/5 | 8/10 | 334 | 80.8 |
| `edge0_ask100_p0.64_stc0-600` | `prob54` | 82.67% | $0.23 | $7.64 | 5/5 | 6/10 | 336 | 80.2 |

## Read

- Best split/day-positive row remains `edge0_ask100_p0.65_stc0-600` / `prob54` with min split fee+1c $0.45.
- Ask caps and stricter thresholds did not improve the current v45 lead while preserving the 80% coverage and all-day gates.
