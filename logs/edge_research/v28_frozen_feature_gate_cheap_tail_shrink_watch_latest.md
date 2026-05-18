# v28 Frozen Feature-Gate Cheap-Tail Shrink Watch

Research-only; no live bot changes or orders.

- Generated UTC: `2026-05-07T03:41:35.371979+00:00`
- Watch freeze UTC: `2026-05-07T03:27:13.050019+00:00`
- Parent feature-gate freeze UTC: `2026-05-06T16:47:25.847566+00:00`
- Rule: `raw03_recross70_abs075`

## Interpretation

- This is a frozen forward watch, not promotion evidence yet.
- Rows before this watch freeze are diagnostic only; only post-freeze rows below count for this cheap-tail shrink mechanism.
- post_cheap_tail_shrink_birth_entry best policy no_shrink_control has 0 settled, coverage 100.0%, weighted net 0.0c, row reconstructed share 1.0, blockers ['settled_lt_30', 'reconstructed_share_gt_35pct', 'net_not_positive', 'full_loss_cushion_lt_3'].
- post_cheap_tail_shrink_birth_bridge best policy no_shrink_control has 0 settled, coverage 100.0%, weighted net 0.0c, row reconstructed share 1.0, blockers ['settled_lt_30', 'reconstructed_share_gt_35pct', 'net_not_positive', 'full_loss_cushion_lt_3'].

## post_cheap_tail_shrink_birth_entry

- Future denominator: `1`

| rank | policy | entries | settled | coverage | weighted net c | W/L | row recon | weighted recon | weight | cheap rows/net | cushion | blockers |
|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| 1 | no_shrink_control | 1 | 0 | 100.000000 | 0.000000 | 0/0 | 1.000000 | 1.000000 | 1.000000 | 0/0 | 0 | settled_lt_30, reconstructed_share_gt_35pct, net_not_positive, full_loss_cushion_lt_3 |
| 2 | cheap_lt10_half | 1 | 0 | 100.000000 | 0.000000 | 0/0 | 1.000000 | 1.000000 | 1.000000 | 0/0 | 0 | settled_lt_30, reconstructed_share_gt_35pct, net_not_positive, full_loss_cushion_lt_3 |
| 3 | cheap_lt10_quarter | 1 | 0 | 100.000000 | 0.000000 | 0/0 | 1.000000 | 1.000000 | 1.000000 | 0/0 | 0 | settled_lt_30, reconstructed_share_gt_35pct, net_not_positive, full_loss_cushion_lt_3 |
| 4 | cheap_lt15_half | 1 | 0 | 100.000000 | 0.000000 | 0/0 | 1.000000 | 1.000000 | 0.500000 | 0/0 | 0 | settled_lt_30, reconstructed_share_gt_35pct, net_not_positive, full_loss_cushion_lt_3 |
| 5 | cheap_lt15_quarter | 1 | 0 | 100.000000 | 0.000000 | 0/0 | 1.000000 | 1.000000 | 0.250000 | 0/0 | 0 | settled_lt_30, reconstructed_share_gt_35pct, net_not_positive, full_loss_cushion_lt_3 |

## post_cheap_tail_shrink_birth_bridge

- Future denominator: `1`

| rank | policy | entries | settled | coverage | weighted net c | W/L | row recon | weighted recon | weight | cheap rows/net | cushion | blockers |
|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| 1 | no_shrink_control | 1 | 0 | 100.000000 | 0.000000 | 0/0 | 1.000000 | 1.000000 | 1.000000 | 0/0 | 0 | settled_lt_30, reconstructed_share_gt_35pct, net_not_positive, full_loss_cushion_lt_3 |
| 2 | cheap_lt10_half | 1 | 0 | 100.000000 | 0.000000 | 0/0 | 1.000000 | 1.000000 | 1.000000 | 0/0 | 0 | settled_lt_30, reconstructed_share_gt_35pct, net_not_positive, full_loss_cushion_lt_3 |
| 3 | cheap_lt10_quarter | 1 | 0 | 100.000000 | 0.000000 | 0/0 | 1.000000 | 1.000000 | 1.000000 | 0/0 | 0 | settled_lt_30, reconstructed_share_gt_35pct, net_not_positive, full_loss_cushion_lt_3 |
| 4 | cheap_lt15_half | 1 | 0 | 100.000000 | 0.000000 | 0/0 | 1.000000 | 1.000000 | 0.500000 | 0/0 | 0 | settled_lt_30, reconstructed_share_gt_35pct, net_not_positive, full_loss_cushion_lt_3 |
| 5 | cheap_lt15_quarter | 1 | 0 | 100.000000 | 0.000000 | 0/0 | 1.000000 | 1.000000 | 0.250000 | 0/0 | 0 | settled_lt_30, reconstructed_share_gt_35pct, net_not_positive, full_loss_cushion_lt_3 |
