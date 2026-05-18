# v28 Common-Clock Zero-Entry Blocker

Operational classifier for the active sourcefix size-1 live trial. It does not place orders or change live logic.

- Generated UTC: `2026-05-11T03:46:38.212844+00:00`
- Decision: `entry_path_active_rescore_and_reconcile`
- Strategy: `mushroom_v28_common_clock_exit_guard_v1_sourcefix_hybridfpt_robustrank1_btcrest_size2_multi_exactgate_depthratio_live`
- Log source: `live_mushroom_v28_common_clock_exit_guard_sourcefix_hybridfpt_robustrank1_btcrest_size2_multi_exactgate_depthratio`
- Totals: `{'events': 1042, 'markets': 5, 'mature_markets': 5, 'approved': 119, 'order_like': 92, 'filled': 93, 'otherwise_approved_book_stale': 80, 'otherwise_approved_btc_stale': 0, 'otherwise_approved_balance': 0, 'p_true_edge_or_price_false_rows': 454, 'edge_price_true_p_false_rows': 0}`
- No-entry review due: `False`
- Markets until no-entry review: `3`
- Mature-market rule: `50` scored rows, review at `8` mature markets
- Decision counts: `{'entry_or_order_seen': 4, 'blocked_by_source_freshness': 1}`

## Markets

| market | events | scored | decision | max p | max edge c | p ok/price fail | edge ok/p fail | stale-only | orders/fills |
|---|---:|---:|---|---:|---:|---:|---:|---:|---:|
| `KXBTC15M-26MAY081630-30` | 95 | 60 | `entry_or_order_seen` | 0.882375 | 15.453193 | 11 | 0 | 4 | 31 |
| `KXBTC15M-26MAY081645-45` | 228 | 194 | `entry_or_order_seen` | 0.996213 | 16.901259 | 115 | 0 | 23 | 26 |
| `KXBTC15M-26MAY081700-00` | 218 | 186 | `entry_or_order_seen` | 0.999715 | 15.641097 | 122 | 0 | 23 | 24 |
| `KXBTC15M-26MAY081715-15` | 186 | 184 | `blocked_by_source_freshness` | 0.860463 | 22.954641 | 136 | 0 | 17 | 0 |
| `KXBTC15M-26MAY081730-30` | 315 | 151 | `entry_or_order_seen` | 0.885195 | 13.951669 | 70 | 0 | 13 | 104 |

## Operator Next Action

Keep active trial running. Do not widen p/edge/ask thresholds; the zero-entry state is currently explained by the policy gates, not by failed order submission.
