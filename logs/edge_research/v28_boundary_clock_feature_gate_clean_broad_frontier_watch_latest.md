# v28 Boundary-Clock Feature-Gate Clean Broad Frontier Watch

Research-only; frozen watch, no live logic changes.

- Generated UTC: `2026-05-11T02:32:06.407183+00:00`
- Watch freeze UTC: `2026-05-07T00:59:58.526374+00:00`
- Parent feature-gate freeze UTC: `2026-05-06T16:47:25.847566+00:00`
- Rule: `raw03_recross50_abs50_ask35` / `{'raw_edge_min': 0.03, 'recross_max': 0.5, 'abs_d_min': 0.5, 'ask_min': 0.35}`

## Interpretation

- This is a frozen watch-only branch; no live logic changes or orders.
- The rule uses observable features only. Source labels are audit-only.
- diagnostic_parent_entry: None/82 entries, None settled, coverage None%, net Nonec, W/L None/None, recon None, pending unsettled 0, blockers ['frontier_rule_not_available'].
- diagnostic_parent_bridge: None/82 entries, None settled, coverage None%, net Nonec, W/L None/None, recon None, pending unsettled 0, blockers ['frontier_rule_not_available'].
- post_clean_broad_freeze_entry: 44/53 entries, 44 settled, coverage 83.01886792452831%, net -76.0c, W/L 34/10, recon 0.4318181818181818, pending unsettled 0, blockers ['net_not_positive', 'reconstructed_share_gt_35pct', 'full_loss_cushion_lt_3'].
- post_clean_broad_freeze_bridge: 44/53 entries, 44 settled, coverage 83.01886792452831%, net -76.0c, W/L 34/10, recon 0.4318181818181818, pending unsettled 0, blockers ['net_not_positive', 'reconstructed_share_gt_35pct', 'full_loss_cushion_lt_3'].

## Lanes

| lane | entries/den | settled | pending | W/L | coverage | net c | recon | source counts | cushion | blockers |
|---|---:|---:|---:|---:|---:|---:|---:|---|---:|---|
| diagnostic_parent_entry | None/82 | None | 0 | None/None | None | None | None | {} | None | frontier_rule_not_available |
| diagnostic_parent_bridge | None/82 | None | 0 | None/None | None | None | None | {} | None | frontier_rule_not_available |
| post_clean_broad_freeze_entry | 44/53 | 44 | 0 | 34/10 | 83.018868 | -76.000000 | 0.431818 | {'approved_entry': 25, 'rejected_actionable': 19} | 0 | net_not_positive, reconstructed_share_gt_35pct, full_loss_cushion_lt_3 |
| post_clean_broad_freeze_bridge | 44/53 | 44 | 0 | 34/10 | 83.018868 | -76.000000 | 0.431818 | {'approved_entry': 25, 'rejected_actionable': 19} | 0 | net_not_positive, reconstructed_share_gt_35pct, full_loss_cushion_lt_3 |

## Strict Rows

| lane | market | ts | status | result | side | won | stc | obs | net c | gross c | raw edge | ask | abs d | recross | source |
|---|---|---|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| post_clean_broad_freeze_entry | KXBTC15M-26MAY062115-15 | 2026-05-07T01:02:05.343442+00:00 | finalized | yes | yes | True | 774.658000 | 8/4 | 25.000000 | -12 | 0.212571 | 0.730000 | 1.308547 | 0.239053 | approved_entry |
| post_clean_broad_freeze_entry | KXBTC15M-26MAY062130-30 | 2026-05-07T01:23:37.668589+00:00 | finalized | yes | no | False | 382.333000 | 10/5 | -65.000000 | -122 | 0.158416 | 0.610000 | 0.623877 | 0.267318 | rejected_actionable |
| post_clean_broad_freeze_entry | KXBTC15M-26MAY062145-45 | 2026-05-07T01:42:21.944726+00:00 | finalized | yes | yes | True | 158.057000 | 16/9 | 6.000000 | 16 | 0.054631 | 0.920000 | 1.770776 | 0.034761 | rejected_actionable |
| post_clean_broad_freeze_entry | KXBTC15M-26MAY062200-00 | 2026-05-07T01:56:01.148379+00:00 | finalized | no | no | True | 238.854000 | 15/8 | 4.000000 | 10 | 0.042204 | 0.950000 | 2.370580 | 0.026847 | rejected_actionable |
| post_clean_broad_freeze_entry | KXBTC15M-26MAY062215-15 | 2026-05-07T02:02:18.109889+00:00 | finalized | no | no | True | 761.901000 | 6/3 | 33.000000 | 14 | 0.239241 | 0.650000 | 1.024084 | 0.319525 | approved_entry |
| post_clean_broad_freeze_entry | KXBTC15M-26MAY062230-30 | 2026-05-07T02:24:26.087288+00:00 | finalized | no | yes | False | 333.913000 | 8/4 | -58.000000 | -108 | 0.199006 | 0.540000 | 0.532659 | 0.243547 | rejected_actionable |
| post_clean_broad_freeze_entry | KXBTC15M-26MAY062245-45 | 2026-05-07T02:33:18.249412+00:00 | finalized | yes | yes | True | 701.753000 | 7/4 | 13.000000 | 8 | 0.089793 | 0.860000 | 1.416091 | 0.214352 | approved_entry |
| post_clean_broad_freeze_entry | KXBTC15M-26MAY062300-00 | 2026-05-07T02:47:13.718042+00:00 | finalized | yes | yes | True | 766.284000 | 4/2 | 12.000000 | 16 | 0.053042 | 0.870000 | 1.169169 | 0.297833 | approved_entry |
| post_clean_broad_freeze_entry | KXBTC15M-26MAY062315-15 | 2026-05-07T03:08:42.395778+00:00 | finalized | no | no | True | 377.606000 | 19/9 | 39.000000 | 86 | 0.181505 | 0.570000 | 0.576357 | 0.264045 | rejected_actionable |
| post_clean_broad_freeze_entry | KXBTC15M-26MAY062345-45 | 2026-05-07T03:37:35.836618+00:00 | finalized | yes | no | False | 444.165000 | 11/5 | -60.000000 | -112 | 0.246238 | 0.560000 | 0.726970 | 0.264802 | rejected_actionable |
| post_clean_broad_freeze_entry | KXBTC15M-26MAY070000-00 | 2026-05-07T03:53:32.799784+00:00 | finalized | no | no | True | 387.203000 | 9/4 | 20.000000 | 2 | 0.083962 | 0.780000 | 0.906372 | 0.193188 | approved_entry |
| post_clean_broad_freeze_entry | KXBTC15M-26MAY070015-15 | 2026-05-07T04:10:20.371309+00:00 | finalized | yes | no | False | 279.632000 | 26/13 | -72.000000 | -2 | 0.263659 | 0.700000 | 1.543579 | 0.073753 | approved_entry |
| post_clean_broad_freeze_entry | KXBTC15M-26MAY070030-30 | 2026-05-07T04:22:22.987474+00:00 | finalized | yes | yes | True | 457.016000 | 5/2 | 15.000000 | 30 | 0.104288 | 0.820000 | 1.178593 | 0.175127 | approved_entry |
| post_clean_broad_freeze_entry | KXBTC15M-26MAY070115-15 | 2026-05-07T05:03:36.061580+00:00 | finalized | yes | yes | True | 683.939000 | 9/5 | 16.000000 | 0 | 0.059857 | 0.820000 | 0.944285 | 0.321409 | approved_entry |
| post_clean_broad_freeze_entry | KXBTC15M-26MAY070200-00 | 2026-05-07T05:54:54.731769+00:00 | finalized | no | no | True | 305.270000 | 3/1 | 26.000000 | 58 | 0.031860 | 0.710000 | 0.556916 | 0.201448 | rejected_actionable |
| post_clean_broad_freeze_entry | KXBTC15M-26MAY070530-30 | 2026-05-07T09:24:40.682970+00:00 | finalized | no | no | True | 319.320000 | 11/5 | 7.000000 | 18 | 0.047387 | 0.910000 | 1.454914 | 0.085902 | rejected_actionable |
| post_clean_broad_freeze_entry | KXBTC15M-26MAY070545-45 | 2026-05-07T09:39:08.515673+00:00 | finalized | no | no | True | 351.487000 | 12/6 | 16.000000 | 18 | 0.105171 | 0.820000 | 1.204817 | 0.124926 | approved_entry |
| post_clean_broad_freeze_entry | KXBTC15M-26MAY070600-00 | 2026-05-07T09:54:12.860165+00:00 | finalized | yes | yes | True | 347.140000 | 4/2 | 28.000000 | 62 | 0.122029 | 0.690000 | 0.734324 | 0.201732 | rejected_actionable |
| post_clean_broad_freeze_entry | KXBTC15M-26MAY070615-15 | 2026-05-07T10:11:16.341648+00:00 | finalized | no | yes | False | 223.658000 | 4/2 | -47.000000 | -86 | 0.344827 | 0.430000 | 0.631490 | 0.143281 | rejected_actionable |
| post_clean_broad_freeze_entry | KXBTC15M-26MAY070630-30 | 2026-05-07T10:19:50.176186+00:00 | finalized | no | yes | False | 609.824000 | 4/2 | -59.000000 | -110 | 0.238158 | 0.550000 | 0.658030 | 0.372304 | rejected_actionable |
| post_clean_broad_freeze_entry | KXBTC15M-26MAY070645-45 | 2026-05-07T10:31:23.542448+00:00 | finalized | yes | yes | True | 816.468000 | 2/1 | 16.000000 | 38 | 0.085399 | 0.810000 | 1.013529 | 0.368798 | approved_entry |
| post_clean_broad_freeze_entry | KXBTC15M-26MAY070715-15 | 2026-05-07T11:08:34.160408+00:00 | finalized | yes | yes | True | 385.840000 | 13/7 | 8.000000 | 9 | 0.081292 | 0.910000 | 2.281129 | 0.051347 | rejected_actionable |
| post_clean_broad_freeze_entry | KXBTC15M-26MAY070745-45 | 2026-05-07T11:37:05.530271+00:00 | finalized | yes | yes | True | 474.481000 | 5/2 | 30.000000 | 34 | 0.223807 | 0.680000 | 1.081343 | 0.197594 | approved_entry |
| post_clean_broad_freeze_entry | KXBTC15M-26MAY070815-15 | 2026-05-07T12:04:59.759684+00:00 | finalized | yes | yes | True | 600.244000 | 7/3 | 9.000000 | 2 | 0.050799 | 0.900000 | 1.397312 | 0.185582 | approved_entry |
| post_clean_broad_freeze_entry | KXBTC15M-26MAY070830-30 | 2026-05-07T12:25:30.079423+00:00 | finalized | no | no | True | 269.931000 | 11/5 | 21.000000 | -14 | 0.120215 | 0.770000 | 1.007446 | 0.126622 | approved_entry |
| post_clean_broad_freeze_entry | KXBTC15M-26MAY070900-00 | 2026-05-07T12:49:06.859276+00:00 | finalized | yes | no | False | 653.141000 | 13/6 | -73.000000 | -140 | 0.055939 | 0.700000 | 0.591792 | 0.457207 | rejected_actionable |
| post_clean_broad_freeze_entry | KXBTC15M-26MAY070915-15 | 2026-05-07T13:05:15.668521+00:00 | finalized | no | no | True | 584.336000 | 24/12 | 20.000000 | 46 | 0.106673 | 0.770000 | 0.951089 | 0.283812 | approved_entry |
| post_clean_broad_freeze_entry | KXBTC15M-26MAY070930-30 | 2026-05-07T13:18:34.086601+00:00 | finalized | yes | yes | True | 685.928000 | 21/11 | 17.000000 | 34 | 0.055936 | 0.800000 | 0.878792 | 0.375669 | approved_entry |
| post_clean_broad_freeze_entry | KXBTC15M-26MAY070945-45 | 2026-05-07T13:32:04.718300+00:00 | finalized | no | no | True | 775.290000 | 10/5 | 28.000000 | 62 | 0.163699 | 0.690000 | 0.882733 | 0.436427 | approved_entry |
| post_clean_broad_freeze_entry | KXBTC15M-26MAY071000-00 | 2026-05-07T13:47:02.487275+00:00 | finalized | no | no | True | 777.523000 | 9/5 | 27.000000 | 16 | 0.141825 | 0.710000 | 0.895147 | 0.484111 | approved_entry |
| post_clean_broad_freeze_entry | KXBTC15M-26MAY071015-15 | 2026-05-07T14:05:16.239793+00:00 | finalized | yes | no | False | 583.765000 | 28/14 | -80.000000 | 2 | 0.081092 | 0.780000 | 0.936079 | 0.417623 | approved_entry |
| post_clean_broad_freeze_entry | KXBTC15M-26MAY071030-30 | 2026-05-07T14:21:03.033181+00:00 | finalized | no | no | True | 536.967000 | 10/6 | 7.000000 | 18 | 0.056530 | 0.910000 | 1.625821 | 0.179518 | rejected_actionable |
| post_clean_broad_freeze_entry | KXBTC15M-26MAY071045-45 | 2026-05-07T14:32:42.750159+00:00 | finalized | no | no | True | 737.262000 | 15/8 | 22.000000 | 50 | 0.115260 | 0.750000 | 0.953688 | 0.469918 | approved_entry |
| post_clean_broad_freeze_entry | KXBTC15M-26MAY071100-00 | 2026-05-07T14:51:41.459433+00:00 | finalized | no | yes | False | 498.551000 | 33/17 | -84.000000 | 4 | 0.054041 | 0.830000 | 1.010241 | 0.305006 | approved_entry |
| post_clean_broad_freeze_entry | KXBTC15M-26MAY071115-15 | 2026-05-07T15:08:31.022852+00:00 | finalized | yes | yes | True | 388.980000 | 51/26 | 15.000000 | 14 | 0.051894 | 0.840000 | 1.052672 | 0.219956 | approved_entry |
| post_clean_broad_freeze_entry | KXBTC15M-26MAY071130-30 | 2026-05-07T15:18:38.937985+00:00 | finalized | no | no | True | 681.063000 | 21/11 | 13.000000 | 30 | 0.066601 | 0.850000 | 1.183451 | 0.331884 | approved_entry |
| post_clean_broad_freeze_entry | KXBTC15M-26MAY071145-45 | 2026-05-07T15:35:48.103988+00:00 | finalized | yes | yes | True | 551.896000 | 9/5 | 11.000000 | 26 | 0.047294 | 0.870000 | 1.182883 | 0.312125 | rejected_actionable |
| post_clean_broad_freeze_entry | KXBTC15M-26MAY071200-00 | 2026-05-07T15:57:45.869204+00:00 | finalized | no | no | True | 134.131000 | 73/36 | 20.000000 | 42 | 0.089141 | 0.770000 | 0.918677 | 0.089529 | approved_entry |
| post_clean_broad_freeze_entry | KXBTC15M-26MAY071215-15 | 2026-05-07T16:03:58.125565+00:00 | finalized | no | yes | False | 661.875000 | 20/10 | -75.000000 | -144 | 0.108282 | 0.720000 | 0.790551 | 0.487740 | rejected_actionable |
| post_clean_broad_freeze_entry | KXBTC15M-26MAY071230-30 | 2026-05-07T16:23:06.054499+00:00 | finalized | yes | yes | True | 413.948000 | 48/24 | 21.000000 | -10 | 0.082419 | 0.770000 | 0.882196 | 0.296037 | approved_entry |
| post_clean_broad_freeze_entry | KXBTC15M-26MAY071245-45 | 2026-05-07T16:36:40.985336+00:00 | finalized | no | no | True | 499.016000 | 42/23 | 8.000000 | 20 | 0.034347 | 0.900000 | 1.285530 | 0.231360 | rejected_actionable |
| post_clean_broad_freeze_entry | KXBTC15M-26MAY071300-00 | 2026-05-07T16:57:26.436900+00:00 | finalized | no | no | True | 153.564000 | 69/35 | 8.000000 | 20 | 0.038084 | 0.900000 | 1.290368 | 0.062061 | rejected_actionable |
| post_clean_broad_freeze_entry | KXBTC15M-26MAY071315-15 | 2026-05-07T17:11:28.426726+00:00 | finalized | yes | yes | True | 211.581000 | 48/29 | 20.000000 | 32 | 0.070827 | 0.780000 | 0.850077 | 0.132426 | approved_entry |
| post_clean_broad_freeze_entry | KXBTC15M-26MAY071330-30 | 2026-05-07T17:18:30.266154+00:00 | finalized | no | no | True | 689.739000 | 18/9 | 16.000000 | 18 | 0.044780 | 0.820000 | 0.927901 | 0.391694 | rejected_actionable |
| post_clean_broad_freeze_bridge | KXBTC15M-26MAY062115-15 | 2026-05-07T01:02:05.343442+00:00 | finalized | yes | yes | True | 774.658000 | 8/4 | 25.000000 | -12 | 0.212571 | 0.730000 | 1.308547 | 0.239053 | approved_entry |
| post_clean_broad_freeze_bridge | KXBTC15M-26MAY062130-30 | 2026-05-07T01:23:37.668589+00:00 | finalized | yes | no | False | 382.333000 | 10/5 | -65.000000 | -122 | 0.158416 | 0.610000 | 0.623877 | 0.267318 | rejected_actionable |
| post_clean_broad_freeze_bridge | KXBTC15M-26MAY062145-45 | 2026-05-07T01:42:21.944726+00:00 | finalized | yes | yes | True | 158.057000 | 16/9 | 6.000000 | 16 | 0.054631 | 0.920000 | 1.770776 | 0.034761 | rejected_actionable |
| post_clean_broad_freeze_bridge | KXBTC15M-26MAY062200-00 | 2026-05-07T01:56:01.148379+00:00 | finalized | no | no | True | 238.854000 | 15/8 | 4.000000 | 10 | 0.042204 | 0.950000 | 2.370580 | 0.026847 | rejected_actionable |
| post_clean_broad_freeze_bridge | KXBTC15M-26MAY062215-15 | 2026-05-07T02:02:18.109889+00:00 | finalized | no | no | True | 761.901000 | 6/3 | 33.000000 | 14 | 0.239241 | 0.650000 | 1.024084 | 0.319525 | approved_entry |
| post_clean_broad_freeze_bridge | KXBTC15M-26MAY062230-30 | 2026-05-07T02:24:26.087288+00:00 | finalized | no | yes | False | 333.913000 | 8/4 | -58.000000 | -108 | 0.199006 | 0.540000 | 0.532659 | 0.243547 | rejected_actionable |
| post_clean_broad_freeze_bridge | KXBTC15M-26MAY062245-45 | 2026-05-07T02:33:18.249412+00:00 | finalized | yes | yes | True | 701.753000 | 7/4 | 13.000000 | 8 | 0.089793 | 0.860000 | 1.416091 | 0.214352 | approved_entry |
| post_clean_broad_freeze_bridge | KXBTC15M-26MAY062300-00 | 2026-05-07T02:47:13.718042+00:00 | finalized | yes | yes | True | 766.284000 | 4/2 | 12.000000 | 16 | 0.053042 | 0.870000 | 1.169169 | 0.297833 | approved_entry |
| post_clean_broad_freeze_bridge | KXBTC15M-26MAY062315-15 | 2026-05-07T03:08:42.395778+00:00 | finalized | no | no | True | 377.606000 | 19/9 | 39.000000 | 86 | 0.181505 | 0.570000 | 0.576357 | 0.264045 | rejected_actionable |
| post_clean_broad_freeze_bridge | KXBTC15M-26MAY062345-45 | 2026-05-07T03:37:35.836618+00:00 | finalized | yes | no | False | 444.165000 | 11/5 | -60.000000 | -112 | 0.246238 | 0.560000 | 0.726970 | 0.264802 | rejected_actionable |
| post_clean_broad_freeze_bridge | KXBTC15M-26MAY070000-00 | 2026-05-07T03:53:32.799784+00:00 | finalized | no | no | True | 387.203000 | 9/4 | 20.000000 | 2 | 0.083962 | 0.780000 | 0.906372 | 0.193188 | approved_entry |
| post_clean_broad_freeze_bridge | KXBTC15M-26MAY070015-15 | 2026-05-07T04:10:20.371309+00:00 | finalized | yes | no | False | 279.632000 | 26/13 | -72.000000 | -2 | 0.263659 | 0.700000 | 1.543579 | 0.073753 | approved_entry |
| post_clean_broad_freeze_bridge | KXBTC15M-26MAY070030-30 | 2026-05-07T04:22:22.987474+00:00 | finalized | yes | yes | True | 457.016000 | 5/2 | 15.000000 | 30 | 0.104288 | 0.820000 | 1.178593 | 0.175127 | approved_entry |
| post_clean_broad_freeze_bridge | KXBTC15M-26MAY070115-15 | 2026-05-07T05:03:36.061580+00:00 | finalized | yes | yes | True | 683.939000 | 9/5 | 16.000000 | 0 | 0.059857 | 0.820000 | 0.944285 | 0.321409 | approved_entry |
| post_clean_broad_freeze_bridge | KXBTC15M-26MAY070200-00 | 2026-05-07T05:54:54.731769+00:00 | finalized | no | no | True | 305.270000 | 3/1 | 26.000000 | 58 | 0.031860 | 0.710000 | 0.556916 | 0.201448 | rejected_actionable |
| post_clean_broad_freeze_bridge | KXBTC15M-26MAY070530-30 | 2026-05-07T09:24:40.682970+00:00 | finalized | no | no | True | 319.320000 | 11/5 | 7.000000 | 18 | 0.047387 | 0.910000 | 1.454914 | 0.085902 | rejected_actionable |
| post_clean_broad_freeze_bridge | KXBTC15M-26MAY070545-45 | 2026-05-07T09:39:08.515673+00:00 | finalized | no | no | True | 351.487000 | 12/6 | 16.000000 | 18 | 0.105171 | 0.820000 | 1.204817 | 0.124926 | approved_entry |
| post_clean_broad_freeze_bridge | KXBTC15M-26MAY070600-00 | 2026-05-07T09:54:12.860165+00:00 | finalized | yes | yes | True | 347.140000 | 4/2 | 28.000000 | 62 | 0.122029 | 0.690000 | 0.734324 | 0.201732 | rejected_actionable |
| post_clean_broad_freeze_bridge | KXBTC15M-26MAY070615-15 | 2026-05-07T10:11:16.341648+00:00 | finalized | no | yes | False | 223.658000 | 4/2 | -47.000000 | -86 | 0.344827 | 0.430000 | 0.631490 | 0.143281 | rejected_actionable |
| post_clean_broad_freeze_bridge | KXBTC15M-26MAY070630-30 | 2026-05-07T10:19:50.176186+00:00 | finalized | no | yes | False | 609.824000 | 4/2 | -59.000000 | -110 | 0.238158 | 0.550000 | 0.658030 | 0.372304 | rejected_actionable |
| post_clean_broad_freeze_bridge | KXBTC15M-26MAY070645-45 | 2026-05-07T10:31:23.542448+00:00 | finalized | yes | yes | True | 816.468000 | 2/1 | 16.000000 | 38 | 0.085399 | 0.810000 | 1.013529 | 0.368798 | approved_entry |
| post_clean_broad_freeze_bridge | KXBTC15M-26MAY070715-15 | 2026-05-07T11:08:34.160408+00:00 | finalized | yes | yes | True | 385.840000 | 13/7 | 8.000000 | 9 | 0.081292 | 0.910000 | 2.281129 | 0.051347 | rejected_actionable |
| post_clean_broad_freeze_bridge | KXBTC15M-26MAY070745-45 | 2026-05-07T11:37:05.530271+00:00 | finalized | yes | yes | True | 474.481000 | 5/2 | 30.000000 | 34 | 0.223807 | 0.680000 | 1.081343 | 0.197594 | approved_entry |
| post_clean_broad_freeze_bridge | KXBTC15M-26MAY070815-15 | 2026-05-07T12:04:59.759684+00:00 | finalized | yes | yes | True | 600.244000 | 7/3 | 9.000000 | 2 | 0.050799 | 0.900000 | 1.397312 | 0.185582 | approved_entry |
| post_clean_broad_freeze_bridge | KXBTC15M-26MAY070830-30 | 2026-05-07T12:25:30.079423+00:00 | finalized | no | no | True | 269.931000 | 11/5 | 21.000000 | -14 | 0.120215 | 0.770000 | 1.007446 | 0.126622 | approved_entry |
| post_clean_broad_freeze_bridge | KXBTC15M-26MAY070900-00 | 2026-05-07T12:49:06.859276+00:00 | finalized | yes | no | False | 653.141000 | 13/6 | -73.000000 | -140 | 0.055939 | 0.700000 | 0.591792 | 0.457207 | rejected_actionable |
| post_clean_broad_freeze_bridge | KXBTC15M-26MAY070915-15 | 2026-05-07T13:05:15.668521+00:00 | finalized | no | no | True | 584.336000 | 24/12 | 20.000000 | 46 | 0.106673 | 0.770000 | 0.951089 | 0.283812 | approved_entry |
| post_clean_broad_freeze_bridge | KXBTC15M-26MAY070930-30 | 2026-05-07T13:18:34.086601+00:00 | finalized | yes | yes | True | 685.928000 | 21/11 | 17.000000 | 34 | 0.055936 | 0.800000 | 0.878792 | 0.375669 | approved_entry |
| post_clean_broad_freeze_bridge | KXBTC15M-26MAY070945-45 | 2026-05-07T13:32:04.718300+00:00 | finalized | no | no | True | 775.290000 | 10/5 | 28.000000 | 62 | 0.163699 | 0.690000 | 0.882733 | 0.436427 | approved_entry |
| post_clean_broad_freeze_bridge | KXBTC15M-26MAY071000-00 | 2026-05-07T13:47:02.487275+00:00 | finalized | no | no | True | 777.523000 | 9/5 | 27.000000 | 16 | 0.141825 | 0.710000 | 0.895147 | 0.484111 | approved_entry |
| post_clean_broad_freeze_bridge | KXBTC15M-26MAY071015-15 | 2026-05-07T14:05:16.239793+00:00 | finalized | yes | no | False | 583.765000 | 28/14 | -80.000000 | 2 | 0.081092 | 0.780000 | 0.936079 | 0.417623 | approved_entry |
| post_clean_broad_freeze_bridge | KXBTC15M-26MAY071030-30 | 2026-05-07T14:21:03.033181+00:00 | finalized | no | no | True | 536.967000 | 10/6 | 7.000000 | 18 | 0.056530 | 0.910000 | 1.625821 | 0.179518 | rejected_actionable |
| post_clean_broad_freeze_bridge | KXBTC15M-26MAY071045-45 | 2026-05-07T14:32:42.750159+00:00 | finalized | no | no | True | 737.262000 | 15/8 | 22.000000 | 50 | 0.115260 | 0.750000 | 0.953688 | 0.469918 | approved_entry |
| post_clean_broad_freeze_bridge | KXBTC15M-26MAY071100-00 | 2026-05-07T14:51:41.459433+00:00 | finalized | no | yes | False | 498.551000 | 33/17 | -84.000000 | 4 | 0.054041 | 0.830000 | 1.010241 | 0.305006 | approved_entry |
| post_clean_broad_freeze_bridge | KXBTC15M-26MAY071115-15 | 2026-05-07T15:08:31.022852+00:00 | finalized | yes | yes | True | 388.980000 | 51/26 | 15.000000 | 14 | 0.051894 | 0.840000 | 1.052672 | 0.219956 | approved_entry |
| post_clean_broad_freeze_bridge | KXBTC15M-26MAY071130-30 | 2026-05-07T15:18:38.937985+00:00 | finalized | no | no | True | 681.063000 | 21/11 | 13.000000 | 30 | 0.066601 | 0.850000 | 1.183451 | 0.331884 | approved_entry |
| post_clean_broad_freeze_bridge | KXBTC15M-26MAY071145-45 | 2026-05-07T15:35:48.103988+00:00 | finalized | yes | yes | True | 551.896000 | 9/5 | 11.000000 | 26 | 0.047294 | 0.870000 | 1.182883 | 0.312125 | rejected_actionable |
| post_clean_broad_freeze_bridge | KXBTC15M-26MAY071200-00 | 2026-05-07T15:57:45.869204+00:00 | finalized | no | no | True | 134.131000 | 73/36 | 20.000000 | 42 | 0.089141 | 0.770000 | 0.918677 | 0.089529 | approved_entry |
| post_clean_broad_freeze_bridge | KXBTC15M-26MAY071215-15 | 2026-05-07T16:03:58.125565+00:00 | finalized | no | yes | False | 661.875000 | 20/10 | -75.000000 | -144 | 0.108282 | 0.720000 | 0.790551 | 0.487740 | rejected_actionable |
| post_clean_broad_freeze_bridge | KXBTC15M-26MAY071230-30 | 2026-05-07T16:23:06.054499+00:00 | finalized | yes | yes | True | 413.948000 | 48/24 | 21.000000 | -10 | 0.082419 | 0.770000 | 0.882196 | 0.296037 | approved_entry |
| post_clean_broad_freeze_bridge | KXBTC15M-26MAY071245-45 | 2026-05-07T16:36:40.985336+00:00 | finalized | no | no | True | 499.016000 | 42/23 | 8.000000 | 20 | 0.034347 | 0.900000 | 1.285530 | 0.231360 | rejected_actionable |
| post_clean_broad_freeze_bridge | KXBTC15M-26MAY071300-00 | 2026-05-07T16:57:26.436900+00:00 | finalized | no | no | True | 153.564000 | 69/35 | 8.000000 | 20 | 0.038084 | 0.900000 | 1.290368 | 0.062061 | rejected_actionable |
| post_clean_broad_freeze_bridge | KXBTC15M-26MAY071315-15 | 2026-05-07T17:11:28.426726+00:00 | finalized | yes | yes | True | 211.581000 | 48/29 | 20.000000 | 32 | 0.070827 | 0.780000 | 0.850077 | 0.132426 | approved_entry |
| post_clean_broad_freeze_bridge | KXBTC15M-26MAY071330-30 | 2026-05-07T17:18:30.266154+00:00 | finalized | no | no | True | 689.739000 | 18/9 | 16.000000 | 18 | 0.044780 | 0.820000 | 0.927901 | 0.391694 | rejected_actionable |
