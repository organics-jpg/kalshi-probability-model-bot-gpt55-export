# v28 Boundary-Clock Feature-Gate Outlier Stress

Research-only; no live bot changes or orders.

- Generated UTC: `2026-05-11T02:30:38.257870+00:00`
- Frontier generated UTC: `2026-05-11T02:00:45.985877+00:00`
- Feature-gate freeze UTC: `2026-05-06T16:47:25.847566+00:00`

## Interpretation

- This is an outlier/source stress audit of the current observable frontier; it is not promotion evidence.
- post_feature_freeze_entry: raw03_recross60_abs85_ask35 has 52 settled, coverage 63.41463414634146%, net 514.0c, recon share 0.1346153846153846; top win 56.0c leaves 458.0c without it, approved-only net 457.0c, reconstructed-only net 57.0c, blockers ['coverage_too_low'].
- post_feature_freeze_bridge: raw03_recross60_abs85_ask35 has 52 settled, coverage 63.41463414634146%, net 514.0c, recon share 0.1346153846153846; top win 56.0c leaves 458.0c without it, approved-only net 457.0c, reconstructed-only net 57.0c, blockers ['coverage_too_low'].

## Lanes

| lane | rule | selected/den | settled | W/L | coverage | net c | recon | approved net | reconstructed net | top win | net ex top | one full loss | blockers |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| post_feature_freeze_entry | raw03_recross60_abs85_ask35 | 52/82 | 52 | 48/4 | 63.414634 | 514.000000 | 0.134615 | 457.000000 | 57.000000 | 56.000000 | 458.000000 | 414.000000 | coverage_too_low |
| post_feature_freeze_bridge | raw03_recross60_abs85_ask35 | 52/82 | 52 | 48/4 | 63.414634 | 514.000000 | 0.134615 | 457.000000 | 57.000000 | 56.000000 | 458.000000 | 414.000000 | coverage_too_low |

## post_feature_freeze_entry Details

- Source split: `{'approved_entry': {'rows': 45, 'wins': 41, 'losses': 4, 'net_cents': 457.0, 'avg_net_cents': 10.155555555555555}, 'rejected_actionable': {'rows': 7, 'wins': 7, 'losses': 0, 'net_cents': 57.0, 'avg_net_cents': 8.142857142857142}}`
- Mechanism tags: `{'clean_or_unclassified': 37, 'mid_cheap_touch': 1, 'realized_loss': 4, 'thin_or_negative_net': 5, 'source_quality_risk': 7, 'thin_raw_edge': 5, 'high_recross_boundary_churn': 3}`
- Top win row: `{'market': 'KXBTC15M-26MAY062015-15', 'source': 'approved_entry', 'side': 'no', 'side_won': True, 'outcome': 'win', 'net_cents': 56.0, 'raw_edge': 0.451622, 'recross_hazard_score': 0.09439569910943164, 'abs_d_sigma': 0.91646, 'ask_prob': 0.42, 'fail_reasons': [], 'mechanism_tags': ['mid_cheap_touch']}`
- Worst loss row: `{'market': 'KXBTC15M-26MAY071100-00', 'source': 'approved_entry', 'side': 'yes', 'side_won': False, 'outcome': 'loss', 'net_cents': -84.0, 'raw_edge': 0.054041000000000006, 'recross_hazard_score': 0.30500573389101787, 'abs_d_sigma': 1.010241, 'ask_prob': 0.83, 'fail_reasons': [], 'mechanism_tags': ['realized_loss', 'thin_or_negative_net']}`

## post_feature_freeze_bridge Details

- Source split: `{'approved_entry': {'rows': 45, 'wins': 41, 'losses': 4, 'net_cents': 457.0, 'avg_net_cents': 10.155555555555555}, 'rejected_actionable': {'rows': 7, 'wins': 7, 'losses': 0, 'net_cents': 57.0, 'avg_net_cents': 8.142857142857142}}`
- Mechanism tags: `{'clean_or_unclassified': 37, 'mid_cheap_touch': 1, 'realized_loss': 4, 'thin_or_negative_net': 5, 'source_quality_risk': 7, 'thin_raw_edge': 5, 'high_recross_boundary_churn': 3}`
- Top win row: `{'market': 'KXBTC15M-26MAY062015-15', 'source': 'approved_entry', 'side': 'no', 'side_won': True, 'outcome': 'win', 'net_cents': 56.0, 'raw_edge': 0.451622, 'recross_hazard_score': 0.09439569910943164, 'abs_d_sigma': 0.91646, 'ask_prob': 0.42, 'fail_reasons': [], 'mechanism_tags': ['mid_cheap_touch']}`
- Worst loss row: `{'market': 'KXBTC15M-26MAY071100-00', 'source': 'approved_entry', 'side': 'yes', 'side_won': False, 'outcome': 'loss', 'net_cents': -84.0, 'raw_edge': 0.054041000000000006, 'recross_hazard_score': 0.30500573389101787, 'abs_d_sigma': 1.010241, 'ask_prob': 0.83, 'fail_reasons': [], 'mechanism_tags': ['realized_loss', 'thin_or_negative_net']}`
