# Session Switch Executability Audit

Generated UTC: `20260504_053219Z`

## Scope

- Research-only audit; no orders are submitted and no bot files or live processes are touched.
- Flags switch rows that require observing a later reference before selecting an earlier anchor price.
- Executable metrics skip those stale-anchor rows or wait for the reference row, depending on the locked rule.

## Summary

| dataset | lock | legacy markets/cov/net | executable markets/cov/net | legacy not executable | stale anchor rows | net delta |
|---|---|---:|---:|---:|---:|---:|
| current | `book_hour04_v2_switch` | 285/99.30%/1595.0c | 285/99.30%/1595.0c | 0 | 0 | 0.0c |
| current | `book_refmargin_score_switch` | 285/99.30%/1557.0c | 284/98.95%/1201.0c | 60 | 59 | -356.0c |
| v21 | `book_hour04_v2_switch` | 219/99.10%/709.0c | 219/99.10%/709.0c | 0 | 0 | 0.0c |
| v21 | `book_refmargin_score_switch` | 219/99.10%/785.0c | 218/98.64%/534.0c | 27 | 26 | -251.0c |

## Read

- Non-executable legacy rows were found for: `book_refmargin_score_switch`/current, `book_refmargin_score_switch`/v21.
- Session-switch evidence should use the executable selector, not the legacy recomputed selector.
