# v28 Feature-Gate Ask35 Add-On Watch

Research-only; frozen watch, no live bot logic changes or orders.

- Generated UTC: `2026-05-07T18:29:13.386015+00:00`
- Freeze UTC: `2026-05-07T18:27:58.644953+00:00`
- Base rule: `{'raw_edge_min': 0.03, 'recross_max': 0.6, 'abs_d_min': 0.85, 'ask_min': 0.35}`
- Add-on rule: `{'raw_edge_min': 0.1, 'ask_min': 0.4, 'abs_d_max': 0.85}`

## Interpretation

- This watch starts from its own freeze timestamp; pre-freeze omitted-split strength is diagnostic only.
- post_addon_watch_entry: combo settled 0, coverage None%, net 0c, recon None, blockers ['settled_lt_30', 'coverage_too_low', 'net_not_positive', 'full_loss_cushion_lt_3']; addon-only settled 0, net 0c.
- post_addon_watch_bridge: combo settled 0, coverage None%, net 0c, recon None, blockers ['settled_lt_30', 'coverage_too_low', 'net_not_positive', 'full_loss_cushion_lt_3']; addon-only settled 0, net 0c.

## post_addon_watch_entry

- Future denominator: `0`

| candidate | settled | W/L | coverage | net c | recon | source counts | cushion | blockers |
|---|---:|---:|---:|---:|---:|---|---:|---|
| `post_addon_watch_entry_base_ask35` | 0 | 0/0 | None | 0 | None | `{}` | 0 | settled_lt_30, coverage_too_low, net_not_positive, full_loss_cushion_lt_3 |
| `post_addon_watch_entry_ask35_plus_midprice_high_edge_addon` | 0 | 0/0 | None | 0 | None | `{}` | 0 | settled_lt_30, coverage_too_low, net_not_positive, full_loss_cushion_lt_3 |
| `post_addon_watch_entry_addon_only_component` | 0 | 0/0 | None | 0 | None | `{}` | 0 | settled_lt_30, coverage_too_low, net_not_positive, full_loss_cushion_lt_3 |

## post_addon_watch_bridge

- Future denominator: `0`

| candidate | settled | W/L | coverage | net c | recon | source counts | cushion | blockers |
|---|---:|---:|---:|---:|---:|---|---:|---|
| `post_addon_watch_bridge_base_ask35` | 0 | 0/0 | None | 0 | None | `{}` | 0 | settled_lt_30, coverage_too_low, net_not_positive, full_loss_cushion_lt_3 |
| `post_addon_watch_bridge_ask35_plus_midprice_high_edge_addon` | 0 | 0/0 | None | 0 | None | `{}` | 0 | settled_lt_30, coverage_too_low, net_not_positive, full_loss_cushion_lt_3 |
| `post_addon_watch_bridge_addon_only_component` | 0 | 0/0 | None | 0 | None | `{}` | 0 | settled_lt_30, coverage_too_low, net_not_positive, full_loss_cushion_lt_3 |
