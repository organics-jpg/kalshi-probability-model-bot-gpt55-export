# Overnight Performance Summary

Window analyzed: `2026-04-30T23:45:00-04:00` to `2026-05-01T06:35:10.731328-04:00`.

- Filled entry orders: `16`.
- Filled exit orders: `13`.
- Entry contracts: `31`.
- Exit contracts: `22`.
- Gross closed/settled PnL before fees: `207c` = `$2.07`.
- Open lots at generation: `[]`.
- Full-log warnings: `12`.
- Full-log errors/tracebacks: `0`.
- Full-log stale mentions: `0`.

## Interpretation

Financially, the overnight run was positive before fees and had a winning open position when this bundle was generated. Behaviorally, it was not perfectly clean because live configuration allowed same-market re-entry and one market reached 4 same-side contracts.

The zero-fill count is also meaningful: fast IOC orders were often submitted against quotes that disappeared before fill. The bot generally handled this without corrupting state, but it makes telemetry and cooldown behavior important.

See `data/overnight_market_summary.csv` and `data/overnight_trade_ledger.csv` for details.
