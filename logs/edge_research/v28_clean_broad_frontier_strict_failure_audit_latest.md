# v28 Clean-Broad Frontier Strict Failure Audit

Research-only; no live bot changes or orders.

- Generated UTC: `2026-05-07T01:47:46.820760+00:00`
- Watch freeze UTC: `2026-05-07T00:59:58.526374+00:00`
- Watch rule: `raw03_recross50_abs50_ask35`

## Interpretation

- This is a strict-row failure audit, not a new candidate freeze.
- post_clean_broad_freeze_entry base raw03_recross50_abs50_ask35 has 3 settled, coverage 100.0%, net -34.0c, strict losses 1; best nearby variant raw03_recross50_abs65_ask35 has 3 settled and -47.0c.
- post_clean_broad_freeze_entry strict loss tags: {'source_quality_risk': 1, 'realized_loss': 1, 'thin_or_negative_net': 1, 'weak_boundary_distance_abs_lt_065': 1}.
- post_clean_broad_freeze_bridge base raw03_recross50_abs50_ask35 has 3 settled, coverage 100.0%, net -34.0c, strict losses 1; best nearby variant raw03_recross50_abs65_ask35 has 3 settled and -47.0c.
- post_clean_broad_freeze_bridge strict loss tags: {'source_quality_risk': 1, 'realized_loss': 1, 'thin_or_negative_net': 1, 'weak_boundary_distance_abs_lt_065': 1}.

## post_clean_broad_freeze_entry

| rule | settled/den | W/L | coverage | net c | recon | cushion | losses/net | blockers |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| raw03_recross50_abs65_ask35 | 3/3 | 2/1 | 100.000000 | -47.000000 | 0.333333 | 0 | 1/-78.000000 | settled_lt_30, net_not_positive, full_loss_cushion_lt_3 |
| raw03_recross50_abs50_ask35 | 3/3 | 2/1 | 100.000000 | -34.000000 | 0.666667 | 0 | 1/-65.000000 | settled_lt_30, net_not_positive, reconstructed_share_gt_35pct, full_loss_cushion_lt_3 |
| raw03_recross50_abs50_ask50 | 3/3 | 2/1 | 100.000000 | -34.000000 | 0.666667 | 0 | 1/-65.000000 | settled_lt_30, net_not_positive, reconstructed_share_gt_35pct, full_loss_cushion_lt_3 |
| raw03_recross40_abs50_ask35 | 3/3 | 2/1 | 100.000000 | -34.000000 | 0.666667 | 0 | 1/-65.000000 | settled_lt_30, net_not_positive, reconstructed_share_gt_35pct, full_loss_cushion_lt_3 |
| raw05_recross50_abs50_ask35 | 3/3 | 2/1 | 100.000000 | -34.000000 | 0.666667 | 0 | 1/-65.000000 | settled_lt_30, net_not_positive, reconstructed_share_gt_35pct, full_loss_cushion_lt_3 |

### Strict Loss Rows

| market | source | side | net c | edge | recross | abs d | ask | tags | included by variants |
|---|---|---|---:|---:|---:|---:|---:|---|---|
| KXBTC15M-26MAY062130-30 | rejected_actionable | no | -65.000000 | 0.158416 | 0.267318 | 0.623877 | 0.610000 | source_quality_risk, realized_loss, thin_or_negative_net, weak_boundary_distance_abs_lt_065 | raw03_recross50_abs50_ask35:True, raw03_recross50_abs65_ask35:True, raw03_recross50_abs50_ask50:True, raw03_recross40_abs50_ask35:True, raw05_recross50_abs50_ask35:True |

## post_clean_broad_freeze_bridge

| rule | settled/den | W/L | coverage | net c | recon | cushion | losses/net | blockers |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| raw03_recross50_abs65_ask35 | 3/3 | 2/1 | 100.000000 | -47.000000 | 0.333333 | 0 | 1/-78.000000 | settled_lt_30, net_not_positive, full_loss_cushion_lt_3 |
| raw03_recross50_abs50_ask35 | 3/3 | 2/1 | 100.000000 | -34.000000 | 0.666667 | 0 | 1/-65.000000 | settled_lt_30, net_not_positive, reconstructed_share_gt_35pct, full_loss_cushion_lt_3 |
| raw03_recross50_abs50_ask50 | 3/3 | 2/1 | 100.000000 | -34.000000 | 0.666667 | 0 | 1/-65.000000 | settled_lt_30, net_not_positive, reconstructed_share_gt_35pct, full_loss_cushion_lt_3 |
| raw03_recross40_abs50_ask35 | 3/3 | 2/1 | 100.000000 | -34.000000 | 0.666667 | 0 | 1/-65.000000 | settled_lt_30, net_not_positive, reconstructed_share_gt_35pct, full_loss_cushion_lt_3 |
| raw05_recross50_abs50_ask35 | 3/3 | 2/1 | 100.000000 | -34.000000 | 0.666667 | 0 | 1/-65.000000 | settled_lt_30, net_not_positive, reconstructed_share_gt_35pct, full_loss_cushion_lt_3 |

### Strict Loss Rows

| market | source | side | net c | edge | recross | abs d | ask | tags | included by variants |
|---|---|---|---:|---:|---:|---:|---:|---|---|
| KXBTC15M-26MAY062130-30 | rejected_actionable | no | -65.000000 | 0.158416 | 0.267318 | 0.623877 | 0.610000 | source_quality_risk, realized_loss, thin_or_negative_net, weak_boundary_distance_abs_lt_065 | raw03_recross50_abs50_ask35:True, raw03_recross50_abs65_ask35:True, raw03_recross50_abs50_ask50:True, raw03_recross40_abs50_ask35:True, raw05_recross50_abs50_ask35:True |
