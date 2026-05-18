# Overnight Live Bot Performance

Generated UTC: `20260502_152443Z`
Window: `2026-05-01T18:00:00-04:00` to `2026-05-02T11:24:43.011006-04:00` local

## Trading Performance

- Entry fills: 37
- Contracts filled: 74
- Settlement winners: 25 / 37 trades = 67.57%
- Winning contracts: 50 / 74 = 67.57%
- Unique traded markets: 24
- Average / median entry ask: 75.3c / 78.0c
- Settlement-only gross P&L proxy: -572.0c
- Gross cash-flow plus settlement value proxy after exits: 169.0c
- Open contracts after parsed exits for overnight markets: 28

## Market Coverage

- Watched market intervals in window: 71
- Traded market intervals in window: 24
- Filled-trade market coverage: 33.80%

## Operational Health

- Entry approvals in bot log: 79
- Entry signals submitted: 78
- Zero-fill abandonments: 41
- Insufficient visible depth deferrals: 2
- Warnings: 50
  - account_refresh_timeout: 8
  - btc_market_context_timeout: 10
  - btc_tick_stream_reconnect: 7
  - closed_market_position_cleared: 13
  - kalshi_market_refresh_timeout: 8
  - kalshi_ws_loop_error: 4

## Overnight Entry Ledger

| local time | market | side | outcome | win | qty | ask | p_side | edge | settlement pnl |
|---|---|---|---|---|---:|---:|---:|---:|---:|
| 2026-05-01 18:02:04 | `KXBTC15M-26MAY011815-15` | yes | yes | True | 2 | 78 | 0.8794 | 6.44 | 44.0 |
| 2026-05-01 18:03:25 | `KXBTC15M-26MAY011815-15` | yes | yes | True | 2 | 78 | 0.8607 | 4.57 | 44.0 |
| 2026-05-01 18:06:28 | `KXBTC15M-26MAY011815-15` | yes | yes | True | 2 | 87 | 0.9207 | 2.07 | 26.0 |
| 2026-05-01 18:20:29 | `KXBTC15M-26MAY011830-30` | yes | yes | True | 2 | 88 | 0.9368 | 2.68 | 24.0 |
| 2026-05-01 18:36:28 | `KXBTC15M-26MAY011845-45` | no | no | True | 2 | 85 | 0.9044 | 2.44 | 30.0 |
| 2026-05-01 19:11:14 | `KXBTC15M-26MAY011915-15` | yes | no | False | 2 | 88 | 0.9329 | 2.29 | -176.0 |
| 2026-05-01 19:20:41 | `KXBTC15M-26MAY011930-30` | no | no | True | 2 | 83 | 0.8898 | 2.98 | 34.0 |
| 2026-05-01 19:50:15 | `KXBTC15M-26MAY012000-00` | yes | yes | True | 2 | 69 | 0.8785 | 15.35 | 62.0 |
| 2026-05-01 19:54:54 | `KXBTC15M-26MAY012000-00` | yes | yes | True | 2 | 75 | 0.9099 | 12.49 | 50.0 |
| 2026-05-01 20:03:12 | `KXBTC15M-26MAY012015-15` | yes | no | False | 2 | 77 | 0.8547 | 4.97 | -154.0 |
| 2026-05-01 20:07:15 | `KXBTC15M-26MAY012015-15` | yes | no | False | 2 | 79 | 0.8523 | 2.73 | -158.0 |
| 2026-05-01 20:10:03 | `KXBTC15M-26MAY012015-15` | yes | no | False | 2 | 86 | 0.9101 | 2.01 | -172.0 |
| 2026-05-01 20:23:22 | `KXBTC15M-26MAY012030-30` | yes | yes | True | 2 | 76 | 0.8827 | 8.77 | 48.0 |
| 2026-05-01 20:32:15 | `KXBTC15M-26MAY012045-45` | yes | yes | True | 2 | 74 | 0.8501 | 7.51 | 52.0 |
| 2026-05-01 20:41:25 | `KXBTC15M-26MAY012045-45` | no | yes | False | 2 | 63 | 0.9157 | 24.57 | -126.0 |
| 2026-05-01 20:51:13 | `KXBTC15M-26MAY012100-00` | yes | yes | True | 2 | 84 | 0.9163 | 4.63 | 32.0 |
| 2026-05-01 20:53:33 | `KXBTC15M-26MAY012100-00` | yes | yes | True | 2 | 73 | 0.9577 | 19.27 | 54.0 |
| 2026-05-01 21:13:05 | `KXBTC15M-26MAY012115-15` | yes | yes | True | 2 | 87 | 0.9964 | 9.64 | 26.0 |
| 2026-05-01 21:33:36 | `KXBTC15M-26MAY012145-45` | yes | no | False | 2 | 86 | 0.9228 | 3.28 | -172.0 |
| 2026-05-01 21:36:03 | `KXBTC15M-26MAY012145-45` | yes | no | False | 2 | 64 | 0.9833 | 30.33 | -128.0 |
| 2026-05-01 21:42:02 | `KXBTC15M-26MAY012145-45` | yes | no | False | 2 | 25 | 0.9301 | 64.51 | -50.0 |
| 2026-05-01 22:06:50 | `KXBTC15M-26MAY012215-15` | yes | no | False | 2 | 77 | 0.8554 | 5.04 | -154.0 |
| 2026-05-01 22:09:45 | `KXBTC15M-26MAY012215-15` | yes | no | False | 2 | 43 | 0.9417 | 47.17 | -86.0 |
| 2026-05-01 22:34:04 | `KXBTC15M-26MAY012245-45` | yes | yes | True | 2 | 75 | 0.8954 | 11.04 | 50.0 |
| 2026-05-01 23:38:19 | `KXBTC15M-26MAY012345-45` | yes | yes | True | 2 | 87 | 0.9745 | 7.45 | 26.0 |
| 2026-05-02 00:48:07 | `KXBTC15M-26MAY020100-00` | no | no | True | 2 | 81 | 0.9247 | 7.97 | 38.0 |
| 2026-05-02 01:21:08 | `KXBTC15M-26MAY020130-30` | yes | no | False | 2 | 27 | 0.8850 | 58.00 | -54.0 |
| 2026-05-02 01:24:00 | `KXBTC15M-26MAY020130-30` | no | no | True | 2 | 65 | 0.8627 | 17.27 | 70.0 |
| 2026-05-02 03:23:36 | `KXBTC15M-26MAY020330-30` | yes | yes | True | 2 | 78 | 0.8635 | 4.85 | 44.0 |
| 2026-05-02 06:10:38 | `KXBTC15M-26MAY020615-15` | yes | yes | True | 2 | 61 | 0.8966 | 24.67 | 78.0 |
| 2026-05-02 07:03:32 | `KXBTC15M-26MAY020715-15` | no | no | True | 2 | 87 | 0.9266 | 2.66 | 26.0 |
| 2026-05-02 08:37:42 | `KXBTC15M-26MAY020845-45` | no | no | True | 2 | 85 | 0.9204 | 4.04 | 30.0 |
| 2026-05-02 10:35:02 | `KXBTC15M-26MAY021045-45` | yes | no | False | 2 | 74 | 0.8544 | 7.94 | -148.0 |
| 2026-05-02 10:53:36 | `KXBTC15M-26MAY021100-00` | yes | yes | True | 2 | 90 | 0.9564 | 2.64 | 20.0 |
| 2026-05-02 11:08:20 | `KXBTC15M-26MAY021115-15` | yes | yes | True | 2 | 87 | 0.9367 | 3.67 | 26.0 |
| 2026-05-02 11:10:20 | `KXBTC15M-26MAY021115-15` | yes | yes | True | 2 | 77 | 0.8577 | 5.27 | 46.0 |
| 2026-05-02 11:12:50 | `KXBTC15M-26MAY021115-15` | yes | yes | True | 2 | 87 | 0.9229 | 2.29 | 26.0 |

## Read

The settlement-only proxy was negative, and accuracy was 67.57%, below the 95% goal.
Exit fills materially improved the basket: gross cash-flow plus settlement value was slightly positive before fees.
It filled trades in only 33.80% of watched 15-minute markets, far below the newly clarified 80% market-coverage target.
The main execution issue was not signal generation; several approved entries became zero-fill abandonments or depth deferrals.
The bot stayed alive, but API/data timeouts and websocket reconnects were frequent enough to matter for coverage.
