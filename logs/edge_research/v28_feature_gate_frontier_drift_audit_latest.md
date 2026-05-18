# v28 Feature-Gate Frontier Drift Audit

Research-only. Compares the original feature-gate frontier audit to the strict clean-broad watch.

- Generated UTC: `2026-05-11T03:08:03.064134+00:00`
- Rule: `raw03_recross50_abs50_ask35`

## Interpretation

- The parent frontier remains useful as mechanism evidence only.
- The clean-broad rule is not promotable unless the strict watch clears its own gates.
- entry: parent 52 settled/514.0c/recon 0.1346153846153846 versus strict 44 settled/-76.0c/recon 0.4318181818181818; blockers ['strict_net_not_positive', 'strict_reconstructed_share_gt_35pct', 'strict_full_loss_cushion_lt_3'].
- bridge: parent 52 settled/514.0c/recon 0.1346153846153846 versus strict 44 settled/-76.0c/recon 0.4318181818181818; blockers ['strict_net_not_positive', 'strict_reconstructed_share_gt_35pct', 'strict_full_loss_cushion_lt_3'].

## Parent Vs Strict

| lane | parent settled | parent W/L | parent cov | parent net | parent recon | strict settled | strict W/L | strict cov | strict net | strict recon | net delta | recon delta | blockers |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| entry | 52 | 48/4 | 63.414634 | 514.000000 | 0.134615 | 44 | 34/10 | 83.018868 | -76.000000 | 0.431818 | -590.000000 | 0.297203 | strict_net_not_positive, strict_reconstructed_share_gt_35pct, strict_full_loss_cushion_lt_3 |
| bridge | 52 | 48/4 | 63.414634 | 514.000000 | 0.134615 | 44 | 34/10 | 83.018868 | -76.000000 | 0.431818 | -590.000000 | 0.297203 | strict_net_not_positive, strict_reconstructed_share_gt_35pct, strict_full_loss_cushion_lt_3 |

## Strict Rows

| lane | market | source | side | won | net c | raw edge | ask | abs d | recross |
|---|---|---|---|---|---:|---:|---:|---:|---:|
| entry | KXBTC15M-26MAY062115-15 | approved_entry | yes | True | 25.000000 | 0.212571 | 0.730000 | 1.308547 | 0.239053 |
| entry | KXBTC15M-26MAY062130-30 | rejected_actionable | no | False | -65.000000 | 0.158416 | 0.610000 | 0.623877 | 0.267318 |
| entry | KXBTC15M-26MAY062145-45 | rejected_actionable | yes | True | 6.000000 | 0.054631 | 0.920000 | 1.770776 | 0.034761 |
| entry | KXBTC15M-26MAY062200-00 | rejected_actionable | no | True | 4.000000 | 0.042204 | 0.950000 | 2.370580 | 0.026847 |
| entry | KXBTC15M-26MAY062215-15 | approved_entry | no | True | 33.000000 | 0.239241 | 0.650000 | 1.024084 | 0.319525 |
| entry | KXBTC15M-26MAY062230-30 | rejected_actionable | yes | False | -58.000000 | 0.199006 | 0.540000 | 0.532659 | 0.243547 |
| entry | KXBTC15M-26MAY062245-45 | approved_entry | yes | True | 13.000000 | 0.089793 | 0.860000 | 1.416091 | 0.214352 |
| entry | KXBTC15M-26MAY062300-00 | approved_entry | yes | True | 12.000000 | 0.053042 | 0.870000 | 1.169169 | 0.297833 |
| entry | KXBTC15M-26MAY062315-15 | rejected_actionable | no | True | 39.000000 | 0.181505 | 0.570000 | 0.576357 | 0.264045 |
| entry | KXBTC15M-26MAY062345-45 | rejected_actionable | no | False | -60.000000 | 0.246238 | 0.560000 | 0.726970 | 0.264802 |
| entry | KXBTC15M-26MAY070000-00 | approved_entry | no | True | 20.000000 | 0.083962 | 0.780000 | 0.906372 | 0.193188 |
| entry | KXBTC15M-26MAY070015-15 | approved_entry | no | False | -72.000000 | 0.263659 | 0.700000 | 1.543579 | 0.073753 |
| entry | KXBTC15M-26MAY070030-30 | approved_entry | yes | True | 15.000000 | 0.104288 | 0.820000 | 1.178593 | 0.175127 |
| entry | KXBTC15M-26MAY070115-15 | approved_entry | yes | True | 16.000000 | 0.059857 | 0.820000 | 0.944285 | 0.321409 |
| entry | KXBTC15M-26MAY070200-00 | rejected_actionable | no | True | 26.000000 | 0.031860 | 0.710000 | 0.556916 | 0.201448 |
| entry | KXBTC15M-26MAY070530-30 | rejected_actionable | no | True | 7.000000 | 0.047387 | 0.910000 | 1.454914 | 0.085902 |
| entry | KXBTC15M-26MAY070545-45 | approved_entry | no | True | 16.000000 | 0.105171 | 0.820000 | 1.204817 | 0.124926 |
| entry | KXBTC15M-26MAY070600-00 | rejected_actionable | yes | True | 28.000000 | 0.122029 | 0.690000 | 0.734324 | 0.201732 |
| entry | KXBTC15M-26MAY070615-15 | rejected_actionable | yes | False | -47.000000 | 0.344827 | 0.430000 | 0.631490 | 0.143281 |
| entry | KXBTC15M-26MAY070630-30 | rejected_actionable | yes | False | -59.000000 | 0.238158 | 0.550000 | 0.658030 | 0.372304 |
| entry | KXBTC15M-26MAY070645-45 | approved_entry | yes | True | 16.000000 | 0.085399 | 0.810000 | 1.013529 | 0.368798 |
| entry | KXBTC15M-26MAY070715-15 | rejected_actionable | yes | True | 8.000000 | 0.081292 | 0.910000 | 2.281129 | 0.051347 |
| entry | KXBTC15M-26MAY070745-45 | approved_entry | yes | True | 30.000000 | 0.223807 | 0.680000 | 1.081343 | 0.197594 |
| entry | KXBTC15M-26MAY070815-15 | approved_entry | yes | True | 9.000000 | 0.050799 | 0.900000 | 1.397312 | 0.185582 |
| entry | KXBTC15M-26MAY070830-30 | approved_entry | no | True | 21.000000 | 0.120215 | 0.770000 | 1.007446 | 0.126622 |
| entry | KXBTC15M-26MAY070900-00 | rejected_actionable | no | False | -73.000000 | 0.055939 | 0.700000 | 0.591792 | 0.457207 |
| entry | KXBTC15M-26MAY070915-15 | approved_entry | no | True | 20.000000 | 0.106673 | 0.770000 | 0.951089 | 0.283812 |
| entry | KXBTC15M-26MAY070930-30 | approved_entry | yes | True | 17.000000 | 0.055936 | 0.800000 | 0.878792 | 0.375669 |
| entry | KXBTC15M-26MAY070945-45 | approved_entry | no | True | 28.000000 | 0.163699 | 0.690000 | 0.882733 | 0.436427 |
| entry | KXBTC15M-26MAY071000-00 | approved_entry | no | True | 27.000000 | 0.141825 | 0.710000 | 0.895147 | 0.484111 |
| entry | KXBTC15M-26MAY071015-15 | approved_entry | no | False | -80.000000 | 0.081092 | 0.780000 | 0.936079 | 0.417623 |
| entry | KXBTC15M-26MAY071030-30 | rejected_actionable | no | True | 7.000000 | 0.056530 | 0.910000 | 1.625821 | 0.179518 |
| entry | KXBTC15M-26MAY071045-45 | approved_entry | no | True | 22.000000 | 0.115260 | 0.750000 | 0.953688 | 0.469918 |
| entry | KXBTC15M-26MAY071100-00 | approved_entry | yes | False | -84.000000 | 0.054041 | 0.830000 | 1.010241 | 0.305006 |
| entry | KXBTC15M-26MAY071115-15 | approved_entry | yes | True | 15.000000 | 0.051894 | 0.840000 | 1.052672 | 0.219956 |
| entry | KXBTC15M-26MAY071130-30 | approved_entry | no | True | 13.000000 | 0.066601 | 0.850000 | 1.183451 | 0.331884 |
| entry | KXBTC15M-26MAY071145-45 | rejected_actionable | yes | True | 11.000000 | 0.047294 | 0.870000 | 1.182883 | 0.312125 |
| entry | KXBTC15M-26MAY071200-00 | approved_entry | no | True | 20.000000 | 0.089141 | 0.770000 | 0.918677 | 0.089529 |
| entry | KXBTC15M-26MAY071215-15 | rejected_actionable | yes | False | -75.000000 | 0.108282 | 0.720000 | 0.790551 | 0.487740 |
| entry | KXBTC15M-26MAY071230-30 | approved_entry | yes | True | 21.000000 | 0.082419 | 0.770000 | 0.882196 | 0.296037 |
| entry | KXBTC15M-26MAY071245-45 | rejected_actionable | no | True | 8.000000 | 0.034347 | 0.900000 | 1.285530 | 0.231360 |
| entry | KXBTC15M-26MAY071300-00 | rejected_actionable | no | True | 8.000000 | 0.038084 | 0.900000 | 1.290368 | 0.062061 |
| entry | KXBTC15M-26MAY071315-15 | approved_entry | yes | True | 20.000000 | 0.070827 | 0.780000 | 0.850077 | 0.132426 |
| entry | KXBTC15M-26MAY071330-30 | rejected_actionable | no | True | 16.000000 | 0.044780 | 0.820000 | 0.927901 | 0.391694 |
| bridge | KXBTC15M-26MAY062115-15 | approved_entry | yes | True | 25.000000 | 0.212571 | 0.730000 | 1.308547 | 0.239053 |
| bridge | KXBTC15M-26MAY062130-30 | rejected_actionable | no | False | -65.000000 | 0.158416 | 0.610000 | 0.623877 | 0.267318 |
| bridge | KXBTC15M-26MAY062145-45 | rejected_actionable | yes | True | 6.000000 | 0.054631 | 0.920000 | 1.770776 | 0.034761 |
| bridge | KXBTC15M-26MAY062200-00 | rejected_actionable | no | True | 4.000000 | 0.042204 | 0.950000 | 2.370580 | 0.026847 |
| bridge | KXBTC15M-26MAY062215-15 | approved_entry | no | True | 33.000000 | 0.239241 | 0.650000 | 1.024084 | 0.319525 |
| bridge | KXBTC15M-26MAY062230-30 | rejected_actionable | yes | False | -58.000000 | 0.199006 | 0.540000 | 0.532659 | 0.243547 |
| bridge | KXBTC15M-26MAY062245-45 | approved_entry | yes | True | 13.000000 | 0.089793 | 0.860000 | 1.416091 | 0.214352 |
| bridge | KXBTC15M-26MAY062300-00 | approved_entry | yes | True | 12.000000 | 0.053042 | 0.870000 | 1.169169 | 0.297833 |
| bridge | KXBTC15M-26MAY062315-15 | rejected_actionable | no | True | 39.000000 | 0.181505 | 0.570000 | 0.576357 | 0.264045 |
| bridge | KXBTC15M-26MAY062345-45 | rejected_actionable | no | False | -60.000000 | 0.246238 | 0.560000 | 0.726970 | 0.264802 |
| bridge | KXBTC15M-26MAY070000-00 | approved_entry | no | True | 20.000000 | 0.083962 | 0.780000 | 0.906372 | 0.193188 |
| bridge | KXBTC15M-26MAY070015-15 | approved_entry | no | False | -72.000000 | 0.263659 | 0.700000 | 1.543579 | 0.073753 |
| bridge | KXBTC15M-26MAY070030-30 | approved_entry | yes | True | 15.000000 | 0.104288 | 0.820000 | 1.178593 | 0.175127 |
| bridge | KXBTC15M-26MAY070115-15 | approved_entry | yes | True | 16.000000 | 0.059857 | 0.820000 | 0.944285 | 0.321409 |
| bridge | KXBTC15M-26MAY070200-00 | rejected_actionable | no | True | 26.000000 | 0.031860 | 0.710000 | 0.556916 | 0.201448 |
| bridge | KXBTC15M-26MAY070530-30 | rejected_actionable | no | True | 7.000000 | 0.047387 | 0.910000 | 1.454914 | 0.085902 |
| bridge | KXBTC15M-26MAY070545-45 | approved_entry | no | True | 16.000000 | 0.105171 | 0.820000 | 1.204817 | 0.124926 |
| bridge | KXBTC15M-26MAY070600-00 | rejected_actionable | yes | True | 28.000000 | 0.122029 | 0.690000 | 0.734324 | 0.201732 |
| bridge | KXBTC15M-26MAY070615-15 | rejected_actionable | yes | False | -47.000000 | 0.344827 | 0.430000 | 0.631490 | 0.143281 |
| bridge | KXBTC15M-26MAY070630-30 | rejected_actionable | yes | False | -59.000000 | 0.238158 | 0.550000 | 0.658030 | 0.372304 |
| bridge | KXBTC15M-26MAY070645-45 | approved_entry | yes | True | 16.000000 | 0.085399 | 0.810000 | 1.013529 | 0.368798 |
| bridge | KXBTC15M-26MAY070715-15 | rejected_actionable | yes | True | 8.000000 | 0.081292 | 0.910000 | 2.281129 | 0.051347 |
| bridge | KXBTC15M-26MAY070745-45 | approved_entry | yes | True | 30.000000 | 0.223807 | 0.680000 | 1.081343 | 0.197594 |
| bridge | KXBTC15M-26MAY070815-15 | approved_entry | yes | True | 9.000000 | 0.050799 | 0.900000 | 1.397312 | 0.185582 |
| bridge | KXBTC15M-26MAY070830-30 | approved_entry | no | True | 21.000000 | 0.120215 | 0.770000 | 1.007446 | 0.126622 |
| bridge | KXBTC15M-26MAY070900-00 | rejected_actionable | no | False | -73.000000 | 0.055939 | 0.700000 | 0.591792 | 0.457207 |
| bridge | KXBTC15M-26MAY070915-15 | approved_entry | no | True | 20.000000 | 0.106673 | 0.770000 | 0.951089 | 0.283812 |
| bridge | KXBTC15M-26MAY070930-30 | approved_entry | yes | True | 17.000000 | 0.055936 | 0.800000 | 0.878792 | 0.375669 |
| bridge | KXBTC15M-26MAY070945-45 | approved_entry | no | True | 28.000000 | 0.163699 | 0.690000 | 0.882733 | 0.436427 |
| bridge | KXBTC15M-26MAY071000-00 | approved_entry | no | True | 27.000000 | 0.141825 | 0.710000 | 0.895147 | 0.484111 |
| bridge | KXBTC15M-26MAY071015-15 | approved_entry | no | False | -80.000000 | 0.081092 | 0.780000 | 0.936079 | 0.417623 |
| bridge | KXBTC15M-26MAY071030-30 | rejected_actionable | no | True | 7.000000 | 0.056530 | 0.910000 | 1.625821 | 0.179518 |
| bridge | KXBTC15M-26MAY071045-45 | approved_entry | no | True | 22.000000 | 0.115260 | 0.750000 | 0.953688 | 0.469918 |
| bridge | KXBTC15M-26MAY071100-00 | approved_entry | yes | False | -84.000000 | 0.054041 | 0.830000 | 1.010241 | 0.305006 |
| bridge | KXBTC15M-26MAY071115-15 | approved_entry | yes | True | 15.000000 | 0.051894 | 0.840000 | 1.052672 | 0.219956 |
| bridge | KXBTC15M-26MAY071130-30 | approved_entry | no | True | 13.000000 | 0.066601 | 0.850000 | 1.183451 | 0.331884 |
| bridge | KXBTC15M-26MAY071145-45 | rejected_actionable | yes | True | 11.000000 | 0.047294 | 0.870000 | 1.182883 | 0.312125 |
| bridge | KXBTC15M-26MAY071200-00 | approved_entry | no | True | 20.000000 | 0.089141 | 0.770000 | 0.918677 | 0.089529 |
| bridge | KXBTC15M-26MAY071215-15 | rejected_actionable | yes | False | -75.000000 | 0.108282 | 0.720000 | 0.790551 | 0.487740 |
| bridge | KXBTC15M-26MAY071230-30 | approved_entry | yes | True | 21.000000 | 0.082419 | 0.770000 | 0.882196 | 0.296037 |
| bridge | KXBTC15M-26MAY071245-45 | rejected_actionable | no | True | 8.000000 | 0.034347 | 0.900000 | 1.285530 | 0.231360 |
| bridge | KXBTC15M-26MAY071300-00 | rejected_actionable | no | True | 8.000000 | 0.038084 | 0.900000 | 1.290368 | 0.062061 |
| bridge | KXBTC15M-26MAY071315-15 | approved_entry | yes | True | 20.000000 | 0.070827 | 0.780000 | 0.850077 | 0.132426 |
| bridge | KXBTC15M-26MAY071330-30 | rejected_actionable | no | True | 16.000000 | 0.044780 | 0.820000 | 0.927901 | 0.391694 |
