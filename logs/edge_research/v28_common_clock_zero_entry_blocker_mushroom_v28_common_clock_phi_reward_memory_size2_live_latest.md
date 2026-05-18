# v28 Common-Clock Zero-Entry Blocker

Operational classifier for the active sourcefix size-1 live trial. It does not place orders or change live logic.

- Generated UTC: `2026-05-11T03:46:36.824455+00:00`
- Decision: `entry_path_active_rescore_and_reconcile`
- Strategy: `mushroom_v28_common_clock_phi_reward_memory_size2_live`
- Log source: `live_mushroom_v28_common_clock_phi_reward_memory_size2_live`
- Totals: `{'events': 6376, 'markets': 20, 'mature_markets': 17, 'approved': 1992, 'order_like': 632, 'filled': 430, 'otherwise_approved_book_stale': 86, 'otherwise_approved_btc_stale': 0, 'otherwise_approved_balance': 0, 'p_true_edge_or_price_false_rows': 1681, 'edge_price_true_p_false_rows': 0}`
- No-entry review due: `False`
- Markets until no-entry review: `0`
- Mature-market rule: `50` scored rows, review at `8` mature markets
- Decision counts: `{'entry_or_order_seen': 18, 'blocked_by_source_freshness': 1, 'selective_wait_price_or_edge': 1}`

## Markets

| market | events | scored | decision | max p | max edge c | p ok/price fail | edge ok/p fail | stale-only | orders/fills |
|---|---:|---:|---|---:|---:|---:|---:|---:|---:|
| `KXBTC15M-26MAY101400-00` | 182 | 73 | `entry_or_order_seen` | 1.000000 | 10.623535 | 42 | 0 | 1 | 53 |
| `KXBTC15M-26MAY101415-15` | 1668 | 1632 | `entry_or_order_seen` | 0.997073 | 7.160622 | 136 | 0 | 12 | 34 |
| `KXBTC15M-26MAY101430-30` | 290 | 180 | `entry_or_order_seen` | 0.999981 | 12.587681 | 107 | 0 | 1 | 96 |
| `KXBTC15M-26MAY101445-45` | 390 | 196 | `entry_or_order_seen` | 1.000000 | 21.894489 | 107 | 0 | 12 | 116 |
| `KXBTC15M-26MAY101500-00` | 231 | 214 | `entry_or_order_seen` | 0.962692 | 36.185640 | 123 | 0 | 21 | 15 |
| `KXBTC15M-26MAY101515-15` | 191 | 142 | `entry_or_order_seen` | 1.000000 | 8.334551 | 94 | 0 | 3 | 45 |
| `KXBTC15M-26MAY101530-30` | 179 | 134 | `entry_or_order_seen` | 1.000000 | 9.518431 | 114 | 0 | 0 | 37 |
| `KXBTC15M-26MAY101545-45` | 482 | 343 | `entry_or_order_seen` | 0.965994 | 11.151216 | 128 | 0 | 4 | 99 |
| `KXBTC15M-26MAY101600-00` | 256 | 172 | `entry_or_order_seen` | 0.981165 | 30.040090 | 118 | 0 | 3 | 62 |
| `KXBTC15M-26MAY101615-15` | 217 | 211 | `entry_or_order_seen` | 1.000000 | 13.688721 | 157 | 0 | 7 | 4 |
| `KXBTC15M-26MAY101630-30` | 181 | 107 | `entry_or_order_seen` | 0.998946 | 22.248303 | 58 | 0 | 6 | 40 |
| `KXBTC15M-26MAY101645-45` | 372 | 93 | `entry_or_order_seen` | 1.000000 | 14.965081 | 33 | 0 | 4 | 123 |
| `KXBTC15M-26MAY101700-00` | 114 | 18 | `entry_or_order_seen` | 0.974399 | 17.141828 | 4 | 0 | 2 | 28 |
| `KXBTC15M-26MAY101715-15` | 132 | 87 | `entry_or_order_seen` | 0.872569 | 6.194316 | 55 | 0 | 0 | 37 |
| `KXBTC15M-26MAY101815-15` | 349 | 17 | `entry_or_order_seen` | 0.978968 | 12.581742 | 4 | 0 | 1 | 80 |
| `KXBTC15M-26MAY101830-30` | 232 | 193 | `entry_or_order_seen` | 0.999986 | 8.528295 | 152 | 0 | 6 | 19 |
| `KXBTC15M-26MAY101845-45` | 215 | 60 | `entry_or_order_seen` | 0.821527 | 4.939654 | 24 | 0 | 1 | 60 |
| `KXBTC15M-26MAY101900-00` | 175 | 171 | `blocked_by_source_freshness` | 0.998757 | 5.182351 | 161 | 0 | 1 | 0 |
| `KXBTC15M-26MAY101915-15` | 458 | 28 | `entry_or_order_seen` | 0.833137 | 9.813186 | 7 | 0 | 1 | 114 |
| `KXBTC15M-26MAY101930-30` | 62 | 62 | `selective_wait_price_or_edge` | 0.695173 | 6.797645 | 57 | 0 | 0 | 0 |

## Operator Next Action

Keep active trial running. Do not widen p/edge/ask thresholds; the zero-entry state is currently explained by the policy gates, not by failed order submission.
