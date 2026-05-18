# Sidecar Spot Tick vs Candle Diagnostic

Research-only diagnostic comparing stale Coinbase candle spot with no-future independent tick spot on settled sidecar packets.

## Summary

- Generated UTC: `2026-05-13T02:01:40.091371+00:00`
- Promotion allowed: `False`
- Diagnostic ready: `True`
- Candidate ready for predeclared shadow: `False`
- Joined rows / markets: `18` / `1`
- Issue count: `0`
- Best model by Brier: `v28`
- Best model by log loss: `v28`
- Tick Brownian delta Brier vs candle: `-0.00520016147581337`
- Tick Brownian delta log loss vs candle: `-0.0112891269337147`

## Model Rows

| model | rows | markets | brier | logloss | selected | selected pnl | top bucket pnl |
|---|---:|---:|---:|---:|---:|---:|---:|
| `candidate` | 18 | 1 | 0.03615119911221907 | 0.1857639183862764 | 9 | 10.0 | -31.0 |
| `v28` | 18 | 1 | 0.015042948861030109 | 0.1308489362582989 | 9 | 126.0 | 56.0 |
| `candle_brownian` | 18 | 1 | 0.13200695510203653 | 0.4515000634192013 | 9 | -135.0 | -60.0 |
| `tick_brownian` | 18 | 1 | 0.12680679362622316 | 0.4402109364854866 | 9 | -135.0 | -60.0 |
| `market_side_ask` | 18 | 1 | 0.021050000000000003 | 0.1566709096161793 | 9 | -135.0 | -60.0 |

## Read

- This is not a promotion artifact and is too small unless `candidate_ready_for_predeclared_shadow=True`.
- It evaluates whether fresher independent spot changes terminal probability quality; it does not alter frozen sidecar evidence.
