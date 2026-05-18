# v28 Common-Clock Zero-Entry Blocker

Operational classifier for the active sourcefix size-1 live trial. It does not place orders or change live logic.

- Generated UTC: `2026-05-09T23:01:39.419274+00:00`
- Decision: `entry_path_active_rescore_and_reconcile`
- Strategy: `mushroom_v28_common_clock_phi_reward_memory_size2_live`
- Log source: `live_mushroom_v28_common_clock_phi_reward_memory_size2_live`
- Totals: `{'events': 3135, 'markets': 14, 'mature_markets': 13, 'approved': 311, 'order_like': 272, 'filled': 281, 'otherwise_approved_book_stale': 74, 'otherwise_approved_btc_stale': 0, 'otherwise_approved_balance': 0, 'p_true_edge_or_price_false_rows': 1569, 'edge_price_true_p_false_rows': 0}`
- No-entry review due: `False`
- Markets until no-entry review: `0`
- Mature-market rule: `50` scored rows, review at `8` mature markets
- Decision counts: `{'entry_or_order_seen': 12, 'blocked_by_source_freshness': 2}`

## Markets

| market | events | scored | decision | max p | max edge c | p ok/price fail | edge ok/p fail | stale-only | orders/fills |
|---|---:|---:|---|---:|---:|---:|---:|---:|---:|
| `KXBTC15M-26MAY091330-30` | 291 | 162 | `entry_or_order_seen` | 1.000000 | 10.563251 | 102 | 0 | 7 | 61 |
| `KXBTC15M-26MAY091345-45` | 159 | 119 | `entry_or_order_seen` | 0.996558 | 44.524717 | 77 | 0 | 7 | 28 |
| `KXBTC15M-26MAY091400-00` | 210 | 117 | `entry_or_order_seen` | 0.999699 | 8.806385 | 82 | 0 | 5 | 47 |
| `KXBTC15M-26MAY091415-15` | 295 | 209 | `entry_or_order_seen` | 0.947501 | 22.522558 | 103 | 0 | 15 | 74 |
| `KXBTC15M-26MAY091430-30` | 261 | 186 | `entry_or_order_seen` | 1.000000 | 10.617868 | 126 | 0 | 9 | 61 |
| `KXBTC15M-26MAY091445-45` | 207 | 173 | `entry_or_order_seen` | 1.000000 | 11.865739 | 136 | 0 | 4 | 30 |
| `KXBTC15M-26MAY091500-00` | 223 | 205 | `entry_or_order_seen` | 0.818567 | 37.724773 | 139 | 0 | 5 | 19 |
| `KXBTC15M-26MAY091515-15` | 292 | 228 | `entry_or_order_seen` | 0.880713 | 10.977509 | 136 | 0 | 4 | 56 |
| `KXBTC15M-26MAY091530-30` | 273 | 178 | `entry_or_order_seen` | 1.000000 | 13.503179 | 122 | 0 | 4 | 49 |
| `KXBTC15M-26MAY091545-45` | 214 | 199 | `entry_or_order_seen` | 0.992531 | 7.725327 | 153 | 0 | 5 | 11 |
| `KXBTC15M-26MAY091600-00` | 175 | 168 | `blocked_by_source_freshness` | 0.998002 | 6.958302 | 160 | 0 | 1 | 0 |
| `KXBTC15M-26MAY091615-15` | 313 | 183 | `entry_or_order_seen` | 1.000000 | 7.574096 | 136 | 0 | 1 | 84 |
| `KXBTC15M-26MAY091630-30` | 214 | 155 | `entry_or_order_seen` | 0.980893 | 18.854163 | 95 | 0 | 6 | 33 |
| `KXBTC15M-26MAY091645-45` | 8 | 6 | `blocked_by_source_freshness` | 0.558553 | 15.852090 | 2 | 0 | 1 | 0 |

## Operator Next Action

Keep active trial running. Do not widen p/edge/ask thresholds; the zero-entry state is currently explained by the policy gates, not by failed order submission.
