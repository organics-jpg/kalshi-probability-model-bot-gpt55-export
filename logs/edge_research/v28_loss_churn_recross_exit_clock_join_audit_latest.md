# v28 Loss-Churn Recross Exit-Clock Join Audit

Research-only. No live bot logic changes, no orders.

- Generated UTC: `2026-05-07T17:10:00.208127+00:00`
- Exit-clock source: `C:\Users\organ\Desktop\KALSHI PROBABILITY MODEL BOT\logs\edge_research\v28_exit_clock_materialized_snapshot_latest.json`
- Scorecard / exit-clock rows: `170` / `100`
- Exact join matched/unmatched/ambiguous: `0` / `100` / `0`
- Tolerance join seconds: `0.5`
- Tolerance join matched/unmatched/ambiguous: `100` / `0` / `0`
- Selected rows: `8`
- Delta / candidate net: `124c ($1.24)` / `487c ($4.87)`
- Helpful/harmful/flat/new-loss: `4` / `0` / `4` / `0`
- Max join diff seconds: `0.124754`
- Blockers: `research_only, not_frozen_forward, join_audit_not_watch, selected_decisions_lt_30`

## Read

- Exact entry timestamp join is not viable because artifacts differ by small capture offsets.
- A 0.5s join is stable if unmatched and ambiguous counts are zero.
- The joined exit-clock denominator is the relevant surface for any future recross exit watch; it is smaller than the continuous-scorecard replay.

## Selected Examples

| market | side | entry ts | scorecard ts | exit ts | recross | actual | hold | delta | join diff |
|---|---|---|---|---|---:|---:|---:|---:|---:|
| `KXBTC15M-26MAY061015-15` | no | `2026-05-06T14:02:01.281253+00:00` | `2026-05-06T14:02:01.255623+00:00` | `2026-05-06T14:03:26.021060+00:00` | 0.5588405505167043 | 0c ($0.00) | 60c ($0.60) | 60c ($0.60) | 0.02563 |
| `KXBTC15M-26MAY061015-15` | no | `2026-05-06T14:03:29.196191+00:00` | `2026-05-06T14:03:29.118515+00:00` | `` | 0.5053900102338842 | 54c ($0.54) | 54c ($0.54) | 0c ($0.00) | 0.077676 |
| `KXBTC15M-26MAY061130-30` | yes | `2026-05-06T15:16:07.783170+00:00` | `2026-05-06T15:16:07.754622+00:00` | `` | 0.5363298971132572 | 40c ($0.40) | 40c ($0.40) | 0c ($0.00) | 0.028548 |
| `KXBTC15M-26MAY061200-00` | yes | `2026-05-06T15:45:31.422761+00:00` | `2026-05-06T15:45:31.352501+00:00` | `2026-05-06T15:51:20.077451+00:00` | 0.5526871033269218 | 16c ($0.16) | 36c ($0.36) | 20c ($0.20) | 0.07026 |
| `KXBTC15M-26MAY071000-00` | no | `2026-05-07T13:47:02.591907+00:00` | `2026-05-07T13:47:02.487275+00:00` | `2026-05-07T13:57:21.055475+00:00` | 0.48411120022028664 | 16c ($0.16) | 58c ($0.58) | 42c ($0.42) | 0.104632 |
| `KXBTC15M-26MAY071030-30` | no | `2026-05-07T14:17:02.903080+00:00` | `2026-05-07T14:17:02.838976+00:00` | `` | 0.572086869997676 | 48c ($0.48) | 48c ($0.48) | 0c ($0.00) | 0.064104 |
| `KXBTC15M-26MAY071045-45` | no | `2026-05-07T14:32:42.856405+00:00` | `2026-05-07T14:32:42.750159+00:00` | `` | 0.4699176077596592 | 50c ($0.50) | 50c ($0.50) | 0c ($0.00) | 0.106246 |
| `KXBTC15M-26MAY071145-45` | yes | `2026-05-07T15:31:46.752356+00:00` | `2026-05-07T15:31:46.715348+00:00` | `2026-05-07T15:42:14.190856+00:00` | 0.5850484031165768 | 44c ($0.44) | 46c ($0.46) | 2c ($0.02) | 0.037008 |
