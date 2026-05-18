# v28 Feature-Gate Ask35 Omitted Split

Research-only. No live bot logic changes, no process control, no orders.

- Generated UTC: `2026-05-07T18:26:37.703788+00:00`
- Source: `C:\Users\organ\Desktop\KALSHI PROBABILITY MODEL BOT\logs\edge_research\v28_boundary_clock_feature_gate_frontier_mechanism_latest.json`

## Interpretation

- This is diagnostic only; rules are searched on omitted rows and need their own freeze before use.
- post_feature_freeze_entry: omitted 30 rows net 78.0c with W/L 9/21; best diagnostic add-on {'clauses': [('ask_prob', '>=', 0.4), ('raw_edge', '>=', 0.1)], 'side': None} summary {'rows': 6, 'net_cents': 282.0, 'avg_net_cents': 47.0, 'wins': 6, 'losses': 0, 'source_counts': {'rejected_actionable': 6}, 'side_counts': {'yes': 4, 'no': 2}, 'tag_counts': {'source_quality_risk': 6, 'mid_cheap_touch': 5, 'near_strike_boundary_pull': 3, 'very_near_strike': 3, 'high_recross_boundary_churn': 2}, 'fail_reason_counts': {'abs_d_below_min': 6, 'recross_above_max': 1}, 'feature_ranges': {'raw_edge': [0.10216400000000003, 0.17743399999999995, 0.34894699999999995], 'recross_hazard_score': [0.20173169569410354, 0.4080737171377116, 0.8305452261842349], 'abs_d_sigma': [0.187292, 0.39438700000000004, 0.734324], 'ask_prob': [0.4, 0.46499999999999997, 0.69]}}.
- post_feature_freeze_bridge: omitted 30 rows net 78.0c with W/L 9/21; best diagnostic add-on {'clauses': [('ask_prob', '>=', 0.4), ('raw_edge', '>=', 0.1)], 'side': None} summary {'rows': 6, 'net_cents': 282.0, 'avg_net_cents': 47.0, 'wins': 6, 'losses': 0, 'source_counts': {'rejected_actionable': 6}, 'side_counts': {'yes': 4, 'no': 2}, 'tag_counts': {'source_quality_risk': 6, 'mid_cheap_touch': 5, 'near_strike_boundary_pull': 3, 'very_near_strike': 3, 'high_recross_boundary_churn': 2}, 'fail_reason_counts': {'abs_d_below_min': 6, 'recross_above_max': 1}, 'feature_ranges': {'raw_edge': [0.10216400000000003, 0.17743399999999995, 0.34894699999999995], 'recross_hazard_score': [0.20173169569410354, 0.4080737171377116, 0.8305452261842349], 'abs_d_sigma': [0.187292, 0.39438700000000004, 0.734324], 'ask_prob': [0.4, 0.46499999999999997, 0.69]}}.

## post_feature_freeze_entry

- omitted: rows `30`, W/L `9/21`, net `78.0c`, side counts `{'no': 13, 'yes': 17}`, fail reasons `{'abs_d_below_min': 30, 'ask_below_min': 21, 'recross_above_max': 9}`
- omitted winners: rows `9`, W/L `9/0`, net `502.0c`, side counts `{'yes': 5, 'no': 4}`, fail reasons `{'abs_d_below_min': 9, 'ask_below_min': 3, 'recross_above_max': 2}`
- omitted losers: rows `21`, W/L `0/21`, net `-424.0c`, side counts `{'no': 9, 'yes': 12}`, fail reasons `{'abs_d_below_min': 21, 'ask_below_min': 18, 'recross_above_max': 7}`

### Best Diagnostic Add-On Rules

| rule | rows | W/L | net c | avg c | side counts | feature ranges |
|---|---:|---:|---:|---:|---|---|
| `ask_prob>=0.4 & raw_edge>=0.1` | 6 | 6/0 | 282.0 | 47.0 | `{'yes': 4, 'no': 2}` | `{'raw_edge': [0.10216400000000003, 0.17743399999999995, 0.34894699999999995], 'recross_hazard_score': [0.20173169569410354, 0.4080737171377116, 0.8305452261842349], 'abs_d_sigma': [0.187292, 0.39438700000000004, 0.734324], 'ask_prob': [0.4, 0.46499999999999997, 0.69]}` |
| `ask_prob>=0.1 & ask_prob>=0.4 & raw_edge>=0.1` | 6 | 6/0 | 282.0 | 47.0 | `{'yes': 4, 'no': 2}` | `{'raw_edge': [0.10216400000000003, 0.17743399999999995, 0.34894699999999995], 'recross_hazard_score': [0.20173169569410354, 0.4080737171377116, 0.8305452261842349], 'abs_d_sigma': [0.187292, 0.39438700000000004, 0.734324], 'ask_prob': [0.4, 0.46499999999999997, 0.69]}` |
| `ask_prob>=0.2 & ask_prob>=0.4 & raw_edge>=0.1` | 6 | 6/0 | 282.0 | 47.0 | `{'yes': 4, 'no': 2}` | `{'raw_edge': [0.10216400000000003, 0.17743399999999995, 0.34894699999999995], 'recross_hazard_score': [0.20173169569410354, 0.4080737171377116, 0.8305452261842349], 'abs_d_sigma': [0.187292, 0.39438700000000004, 0.734324], 'ask_prob': [0.4, 0.46499999999999997, 0.69]}` |
| `ask_prob>=0.3 & ask_prob>=0.4 & raw_edge>=0.1` | 6 | 6/0 | 282.0 | 47.0 | `{'yes': 4, 'no': 2}` | `{'raw_edge': [0.10216400000000003, 0.17743399999999995, 0.34894699999999995], 'recross_hazard_score': [0.20173169569410354, 0.4080737171377116, 0.8305452261842349], 'abs_d_sigma': [0.187292, 0.39438700000000004, 0.734324], 'ask_prob': [0.4, 0.46499999999999997, 0.69]}` |
| `ask_prob>=0.4 & abs_d_sigma>=0.1 & raw_edge>=0.1` | 6 | 6/0 | 282.0 | 47.0 | `{'yes': 4, 'no': 2}` | `{'raw_edge': [0.10216400000000003, 0.17743399999999995, 0.34894699999999995], 'recross_hazard_score': [0.20173169569410354, 0.4080737171377116, 0.8305452261842349], 'abs_d_sigma': [0.187292, 0.39438700000000004, 0.734324], 'ask_prob': [0.4, 0.46499999999999997, 0.69]}` |
| `ask_prob>=0.4 & raw_edge>=0.05 & raw_edge>=0.1` | 6 | 6/0 | 282.0 | 47.0 | `{'yes': 4, 'no': 2}` | `{'raw_edge': [0.10216400000000003, 0.17743399999999995, 0.34894699999999995], 'recross_hazard_score': [0.20173169569410354, 0.4080737171377116, 0.8305452261842349], 'abs_d_sigma': [0.187292, 0.39438700000000004, 0.734324], 'ask_prob': [0.4, 0.46499999999999997, 0.69]}` |
| `ask_prob>=0.4 & recross_hazard_score<=0.6` | 5 | 5/0 | 234.0 | 46.8 | `{'yes': 4, 'no': 1}` | `{'raw_edge': [0.12202900000000005, 0.20877999999999997, 0.34894699999999995], 'recross_hazard_score': [0.20173169569410354, 0.39634677763047876, 0.5965758829179154], 'abs_d_sigma': [0.226282, 0.552158, 0.734324], 'ask_prob': [0.4, 0.45, 0.69]}` |
| `ask_prob>=0.4 & recross_hazard_score<=0.7` | 5 | 5/0 | 234.0 | 46.8 | `{'yes': 4, 'no': 1}` | `{'raw_edge': [0.12202900000000005, 0.20877999999999997, 0.34894699999999995], 'recross_hazard_score': [0.20173169569410354, 0.39634677763047876, 0.5965758829179154], 'abs_d_sigma': [0.226282, 0.552158, 0.734324], 'ask_prob': [0.4, 0.45, 0.69]}` |
| `ask_prob>=0.1 & ask_prob>=0.4 & recross_hazard_score<=0.6` | 5 | 5/0 | 234.0 | 46.8 | `{'yes': 4, 'no': 1}` | `{'raw_edge': [0.12202900000000005, 0.20877999999999997, 0.34894699999999995], 'recross_hazard_score': [0.20173169569410354, 0.39634677763047876, 0.5965758829179154], 'abs_d_sigma': [0.226282, 0.552158, 0.734324], 'ask_prob': [0.4, 0.45, 0.69]}` |
| `ask_prob>=0.1 & ask_prob>=0.4 & recross_hazard_score<=0.7` | 5 | 5/0 | 234.0 | 46.8 | `{'yes': 4, 'no': 1}` | `{'raw_edge': [0.12202900000000005, 0.20877999999999997, 0.34894699999999995], 'recross_hazard_score': [0.20173169569410354, 0.39634677763047876, 0.5965758829179154], 'abs_d_sigma': [0.226282, 0.552158, 0.734324], 'ask_prob': [0.4, 0.45, 0.69]}` |
| `ask_prob>=0.2 & ask_prob>=0.4 & recross_hazard_score<=0.6` | 5 | 5/0 | 234.0 | 46.8 | `{'yes': 4, 'no': 1}` | `{'raw_edge': [0.12202900000000005, 0.20877999999999997, 0.34894699999999995], 'recross_hazard_score': [0.20173169569410354, 0.39634677763047876, 0.5965758829179154], 'abs_d_sigma': [0.226282, 0.552158, 0.734324], 'ask_prob': [0.4, 0.45, 0.69]}` |
| `ask_prob>=0.2 & ask_prob>=0.4 & recross_hazard_score<=0.7` | 5 | 5/0 | 234.0 | 46.8 | `{'yes': 4, 'no': 1}` | `{'raw_edge': [0.12202900000000005, 0.20877999999999997, 0.34894699999999995], 'recross_hazard_score': [0.20173169569410354, 0.39634677763047876, 0.5965758829179154], 'abs_d_sigma': [0.226282, 0.552158, 0.734324], 'ask_prob': [0.4, 0.45, 0.69]}` |
| `ask_prob>=0.3 & ask_prob>=0.4 & recross_hazard_score<=0.6` | 5 | 5/0 | 234.0 | 46.8 | `{'yes': 4, 'no': 1}` | `{'raw_edge': [0.12202900000000005, 0.20877999999999997, 0.34894699999999995], 'recross_hazard_score': [0.20173169569410354, 0.39634677763047876, 0.5965758829179154], 'abs_d_sigma': [0.226282, 0.552158, 0.734324], 'ask_prob': [0.4, 0.45, 0.69]}` |
| `ask_prob>=0.3 & ask_prob>=0.4 & recross_hazard_score<=0.7` | 5 | 5/0 | 234.0 | 46.8 | `{'yes': 4, 'no': 1}` | `{'raw_edge': [0.12202900000000005, 0.20877999999999997, 0.34894699999999995], 'recross_hazard_score': [0.20173169569410354, 0.39634677763047876, 0.5965758829179154], 'abs_d_sigma': [0.226282, 0.552158, 0.734324], 'ask_prob': [0.4, 0.45, 0.69]}` |
| `ask_prob>=0.4 & abs_d_sigma>=0.1 & recross_hazard_score<=0.6` | 5 | 5/0 | 234.0 | 46.8 | `{'yes': 4, 'no': 1}` | `{'raw_edge': [0.12202900000000005, 0.20877999999999997, 0.34894699999999995], 'recross_hazard_score': [0.20173169569410354, 0.39634677763047876, 0.5965758829179154], 'abs_d_sigma': [0.226282, 0.552158, 0.734324], 'ask_prob': [0.4, 0.45, 0.69]}` |
| `ask_prob>=0.4 & abs_d_sigma>=0.1 & recross_hazard_score<=0.7` | 5 | 5/0 | 234.0 | 46.8 | `{'yes': 4, 'no': 1}` | `{'raw_edge': [0.12202900000000005, 0.20877999999999997, 0.34894699999999995], 'recross_hazard_score': [0.20173169569410354, 0.39634677763047876, 0.5965758829179154], 'abs_d_sigma': [0.226282, 0.552158, 0.734324], 'ask_prob': [0.4, 0.45, 0.69]}` |
| `ask_prob>=0.4 & abs_d_sigma>=0.2 & recross_hazard_score<=0.6` | 5 | 5/0 | 234.0 | 46.8 | `{'yes': 4, 'no': 1}` | `{'raw_edge': [0.12202900000000005, 0.20877999999999997, 0.34894699999999995], 'recross_hazard_score': [0.20173169569410354, 0.39634677763047876, 0.5965758829179154], 'abs_d_sigma': [0.226282, 0.552158, 0.734324], 'ask_prob': [0.4, 0.45, 0.69]}` |
| `ask_prob>=0.4 & abs_d_sigma>=0.2 & recross_hazard_score<=0.7` | 5 | 5/0 | 234.0 | 46.8 | `{'yes': 4, 'no': 1}` | `{'raw_edge': [0.12202900000000005, 0.20877999999999997, 0.34894699999999995], 'recross_hazard_score': [0.20173169569410354, 0.39634677763047876, 0.5965758829179154], 'abs_d_sigma': [0.226282, 0.552158, 0.734324], 'ask_prob': [0.4, 0.45, 0.69]}` |
| `ask_prob>=0.4 & abs_d_sigma>=0.2 & raw_edge>=0.1` | 5 | 5/0 | 234.0 | 46.8 | `{'yes': 4, 'no': 1}` | `{'raw_edge': [0.12202900000000005, 0.20877999999999997, 0.34894699999999995], 'recross_hazard_score': [0.20173169569410354, 0.39634677763047876, 0.5965758829179154], 'abs_d_sigma': [0.226282, 0.552158, 0.734324], 'ask_prob': [0.4, 0.45, 0.69]}` |
| `ask_prob>=0.4 & recross_hazard_score<=0.6 & recross_hazard_score<=0.7` | 5 | 5/0 | 234.0 | 46.8 | `{'yes': 4, 'no': 1}` | `{'raw_edge': [0.12202900000000005, 0.20877999999999997, 0.34894699999999995], 'recross_hazard_score': [0.20173169569410354, 0.39634677763047876, 0.5965758829179154], 'abs_d_sigma': [0.226282, 0.552158, 0.734324], 'ask_prob': [0.4, 0.45, 0.69]}` |

### Top Omitted Winners

| market | side | net c | edge | recross | abs d | ask | tags |
|---|---|---:|---:|---:|---:|---:|---|
| `KXBTC15M-26MAY061630-30` | `no` | 77.0 | 0.162456 | 0.19254835858215918 | 0.343001 | 0.2 | `['source_quality_risk', 'very_near_strike', 'cheap_tail_touch']` |
| `KXBTC15M-26MAY070730-30` | `no` | 76.0 | 0.227021 | 0.3253012001681479 | 0.144204 | 0.21 | `['source_quality_risk', 'very_near_strike', 'cheap_tail_touch']` |
| `KXBTC15M-26MAY062345-45` | `yes` | 67.0 | 0.29811099999999996 | 0.6399727981599007 | 0.214573 | 0.3 | `['source_quality_risk', 'high_recross_boundary_churn', 'very_near_strike', 'cheap_tail_touch']` |
| `KXBTC15M-26MAY061530-30` | `yes` | 56.0 | 0.20877999999999997 | 0.22815637451890164 | 0.226282 | 0.4 | `['source_quality_risk', 'very_near_strike', 'mid_cheap_touch']` |
| `KXBTC15M-26MAY061945-45` | `no` | 51.0 | 0.34894699999999995 | 0.39634677763047876 | 0.680058 | 0.45 | `['source_quality_risk', 'near_strike_boundary_pull', 'mid_cheap_touch']` |
| `KXBTC15M-26MAY070845-45` | `yes` | 51.0 | 0.14608799999999994 | 0.5965758829179154 | 0.236616 | 0.45 | `['source_quality_risk', 'high_recross_boundary_churn', 'very_near_strike', 'mid_cheap_touch']` |
| `KXBTC15M-26MAY062000-00` | `yes` | 48.0 | 0.25948899999999997 | 0.4198006566449445 | 0.552158 | 0.48 | `['source_quality_risk', 'near_strike_boundary_pull', 'mid_cheap_touch']` |
| `KXBTC15M-26MAY070045-45` | `no` | 48.0 | 0.10216400000000003 | 0.8305452261842349 | 0.187292 | 0.48 | `['source_quality_risk', 'high_recross_boundary_churn', 'very_near_strike', 'mid_cheap_touch']` |
| `KXBTC15M-26MAY070600-00` | `yes` | 28.0 | 0.12202900000000005 | 0.20173169569410354 | 0.734324 | 0.69 | `['source_quality_risk', 'near_strike_boundary_pull']` |

### Worst Omitted Losers

| market | side | net c | edge | recross | abs d | ask | tags |
|---|---|---:|---:|---:|---:|---:|---|
| `KXBTC15M-26MAY070900-00` | `no` | -56.0 | 0.08608300000000002 | 0.7010000307286993 | 0.253011 | 0.52 | `['source_quality_risk', 'realized_loss', 'thin_or_negative_net', 'high_recross_boundary_churn', 'very_near_strike', 'mid_cheap_touch']` |
| `KXBTC15M-26MAY061700-00` | `no` | -42.0 | 0.408347 | 0.19639134370333244 | 0.665443 | 0.38 | `['source_quality_risk', 'realized_loss', 'thin_or_negative_net', 'near_strike_boundary_pull', 'mid_cheap_touch']` |
| `KXBTC15M-26MAY062230-30` | `yes` | -42.0 | 0.33801499999999995 | 0.34967152719409217 | 0.481781 | 0.38 | `['source_quality_risk', 'realized_loss', 'thin_or_negative_net', 'very_near_strike', 'mid_cheap_touch']` |
| `KXBTC15M-26MAY061515-15` | `yes` | -30.0 | 0.10925099999999999 | 0.41393025340425893 | 0.289927 | 0.27 | `['source_quality_risk', 'realized_loss', 'thin_or_negative_net', 'very_near_strike', 'cheap_tail_touch']` |
| `KXBTC15M-26MAY061730-30` | `no` | -29.0 | 0.152854 | 0.7211101278549997 | 0.193064 | 0.26 | `['source_quality_risk', 'realized_loss', 'thin_or_negative_net', 'high_recross_boundary_churn', 'very_near_strike', 'cheap_tail_touch']` |
| `KXBTC15M-26MAY061930-30` | `no` | -28.0 | 0.30184 | 0.6888227956941311 | 0.118494 | 0.25 | `['source_quality_risk', 'realized_loss', 'thin_or_negative_net', 'high_recross_boundary_churn', 'very_near_strike', 'cheap_tail_touch']` |
| `KXBTC15M-26MAY070700-00` | `yes` | -28.0 | 0.445361 | 0.42112984035832196 | 0.477812 | 0.25 | `['source_quality_risk', 'realized_loss', 'thin_or_negative_net', 'very_near_strike', 'cheap_tail_touch']` |
| `KXBTC15M-26MAY061845-45` | `no` | -26.0 | 0.11107599999999998 | 0.6131714328215057 | 0.335691 | 0.23 | `['source_quality_risk', 'realized_loss', 'thin_or_negative_net', 'high_recross_boundary_churn', 'very_near_strike', 'cheap_tail_touch']` |
| `KXBTC15M-26MAY070100-00` | `no` | -25.0 | 0.28501300000000007 | 0.647900380591622 | 0.032616 | 0.22 | `['source_quality_risk', 'realized_loss', 'thin_or_negative_net', 'high_recross_boundary_churn', 'very_near_strike', 'cheap_tail_touch']` |
| `KXBTC15M-26MAY070145-45` | `yes` | -19.0 | 0.174262 | 0.3571782759435685 | 0.363444 | 0.17 | `['source_quality_risk', 'realized_loss', 'thin_or_negative_net', 'very_near_strike', 'cheap_tail_touch']` |

## post_feature_freeze_bridge

- omitted: rows `30`, W/L `9/21`, net `78.0c`, side counts `{'no': 13, 'yes': 17}`, fail reasons `{'abs_d_below_min': 30, 'ask_below_min': 21, 'recross_above_max': 9}`
- omitted winners: rows `9`, W/L `9/0`, net `502.0c`, side counts `{'yes': 5, 'no': 4}`, fail reasons `{'abs_d_below_min': 9, 'ask_below_min': 3, 'recross_above_max': 2}`
- omitted losers: rows `21`, W/L `0/21`, net `-424.0c`, side counts `{'no': 9, 'yes': 12}`, fail reasons `{'abs_d_below_min': 21, 'ask_below_min': 18, 'recross_above_max': 7}`

### Best Diagnostic Add-On Rules

| rule | rows | W/L | net c | avg c | side counts | feature ranges |
|---|---:|---:|---:|---:|---|---|
| `ask_prob>=0.4 & raw_edge>=0.1` | 6 | 6/0 | 282.0 | 47.0 | `{'yes': 4, 'no': 2}` | `{'raw_edge': [0.10216400000000003, 0.17743399999999995, 0.34894699999999995], 'recross_hazard_score': [0.20173169569410354, 0.4080737171377116, 0.8305452261842349], 'abs_d_sigma': [0.187292, 0.39438700000000004, 0.734324], 'ask_prob': [0.4, 0.46499999999999997, 0.69]}` |
| `ask_prob>=0.1 & ask_prob>=0.4 & raw_edge>=0.1` | 6 | 6/0 | 282.0 | 47.0 | `{'yes': 4, 'no': 2}` | `{'raw_edge': [0.10216400000000003, 0.17743399999999995, 0.34894699999999995], 'recross_hazard_score': [0.20173169569410354, 0.4080737171377116, 0.8305452261842349], 'abs_d_sigma': [0.187292, 0.39438700000000004, 0.734324], 'ask_prob': [0.4, 0.46499999999999997, 0.69]}` |
| `ask_prob>=0.2 & ask_prob>=0.4 & raw_edge>=0.1` | 6 | 6/0 | 282.0 | 47.0 | `{'yes': 4, 'no': 2}` | `{'raw_edge': [0.10216400000000003, 0.17743399999999995, 0.34894699999999995], 'recross_hazard_score': [0.20173169569410354, 0.4080737171377116, 0.8305452261842349], 'abs_d_sigma': [0.187292, 0.39438700000000004, 0.734324], 'ask_prob': [0.4, 0.46499999999999997, 0.69]}` |
| `ask_prob>=0.3 & ask_prob>=0.4 & raw_edge>=0.1` | 6 | 6/0 | 282.0 | 47.0 | `{'yes': 4, 'no': 2}` | `{'raw_edge': [0.10216400000000003, 0.17743399999999995, 0.34894699999999995], 'recross_hazard_score': [0.20173169569410354, 0.4080737171377116, 0.8305452261842349], 'abs_d_sigma': [0.187292, 0.39438700000000004, 0.734324], 'ask_prob': [0.4, 0.46499999999999997, 0.69]}` |
| `ask_prob>=0.4 & abs_d_sigma>=0.1 & raw_edge>=0.1` | 6 | 6/0 | 282.0 | 47.0 | `{'yes': 4, 'no': 2}` | `{'raw_edge': [0.10216400000000003, 0.17743399999999995, 0.34894699999999995], 'recross_hazard_score': [0.20173169569410354, 0.4080737171377116, 0.8305452261842349], 'abs_d_sigma': [0.187292, 0.39438700000000004, 0.734324], 'ask_prob': [0.4, 0.46499999999999997, 0.69]}` |
| `ask_prob>=0.4 & raw_edge>=0.05 & raw_edge>=0.1` | 6 | 6/0 | 282.0 | 47.0 | `{'yes': 4, 'no': 2}` | `{'raw_edge': [0.10216400000000003, 0.17743399999999995, 0.34894699999999995], 'recross_hazard_score': [0.20173169569410354, 0.4080737171377116, 0.8305452261842349], 'abs_d_sigma': [0.187292, 0.39438700000000004, 0.734324], 'ask_prob': [0.4, 0.46499999999999997, 0.69]}` |
| `ask_prob>=0.4 & recross_hazard_score<=0.6` | 5 | 5/0 | 234.0 | 46.8 | `{'yes': 4, 'no': 1}` | `{'raw_edge': [0.12202900000000005, 0.20877999999999997, 0.34894699999999995], 'recross_hazard_score': [0.20173169569410354, 0.39634677763047876, 0.5965758829179154], 'abs_d_sigma': [0.226282, 0.552158, 0.734324], 'ask_prob': [0.4, 0.45, 0.69]}` |
| `ask_prob>=0.4 & recross_hazard_score<=0.7` | 5 | 5/0 | 234.0 | 46.8 | `{'yes': 4, 'no': 1}` | `{'raw_edge': [0.12202900000000005, 0.20877999999999997, 0.34894699999999995], 'recross_hazard_score': [0.20173169569410354, 0.39634677763047876, 0.5965758829179154], 'abs_d_sigma': [0.226282, 0.552158, 0.734324], 'ask_prob': [0.4, 0.45, 0.69]}` |
| `ask_prob>=0.1 & ask_prob>=0.4 & recross_hazard_score<=0.6` | 5 | 5/0 | 234.0 | 46.8 | `{'yes': 4, 'no': 1}` | `{'raw_edge': [0.12202900000000005, 0.20877999999999997, 0.34894699999999995], 'recross_hazard_score': [0.20173169569410354, 0.39634677763047876, 0.5965758829179154], 'abs_d_sigma': [0.226282, 0.552158, 0.734324], 'ask_prob': [0.4, 0.45, 0.69]}` |
| `ask_prob>=0.1 & ask_prob>=0.4 & recross_hazard_score<=0.7` | 5 | 5/0 | 234.0 | 46.8 | `{'yes': 4, 'no': 1}` | `{'raw_edge': [0.12202900000000005, 0.20877999999999997, 0.34894699999999995], 'recross_hazard_score': [0.20173169569410354, 0.39634677763047876, 0.5965758829179154], 'abs_d_sigma': [0.226282, 0.552158, 0.734324], 'ask_prob': [0.4, 0.45, 0.69]}` |
| `ask_prob>=0.2 & ask_prob>=0.4 & recross_hazard_score<=0.6` | 5 | 5/0 | 234.0 | 46.8 | `{'yes': 4, 'no': 1}` | `{'raw_edge': [0.12202900000000005, 0.20877999999999997, 0.34894699999999995], 'recross_hazard_score': [0.20173169569410354, 0.39634677763047876, 0.5965758829179154], 'abs_d_sigma': [0.226282, 0.552158, 0.734324], 'ask_prob': [0.4, 0.45, 0.69]}` |
| `ask_prob>=0.2 & ask_prob>=0.4 & recross_hazard_score<=0.7` | 5 | 5/0 | 234.0 | 46.8 | `{'yes': 4, 'no': 1}` | `{'raw_edge': [0.12202900000000005, 0.20877999999999997, 0.34894699999999995], 'recross_hazard_score': [0.20173169569410354, 0.39634677763047876, 0.5965758829179154], 'abs_d_sigma': [0.226282, 0.552158, 0.734324], 'ask_prob': [0.4, 0.45, 0.69]}` |
| `ask_prob>=0.3 & ask_prob>=0.4 & recross_hazard_score<=0.6` | 5 | 5/0 | 234.0 | 46.8 | `{'yes': 4, 'no': 1}` | `{'raw_edge': [0.12202900000000005, 0.20877999999999997, 0.34894699999999995], 'recross_hazard_score': [0.20173169569410354, 0.39634677763047876, 0.5965758829179154], 'abs_d_sigma': [0.226282, 0.552158, 0.734324], 'ask_prob': [0.4, 0.45, 0.69]}` |
| `ask_prob>=0.3 & ask_prob>=0.4 & recross_hazard_score<=0.7` | 5 | 5/0 | 234.0 | 46.8 | `{'yes': 4, 'no': 1}` | `{'raw_edge': [0.12202900000000005, 0.20877999999999997, 0.34894699999999995], 'recross_hazard_score': [0.20173169569410354, 0.39634677763047876, 0.5965758829179154], 'abs_d_sigma': [0.226282, 0.552158, 0.734324], 'ask_prob': [0.4, 0.45, 0.69]}` |
| `ask_prob>=0.4 & abs_d_sigma>=0.1 & recross_hazard_score<=0.6` | 5 | 5/0 | 234.0 | 46.8 | `{'yes': 4, 'no': 1}` | `{'raw_edge': [0.12202900000000005, 0.20877999999999997, 0.34894699999999995], 'recross_hazard_score': [0.20173169569410354, 0.39634677763047876, 0.5965758829179154], 'abs_d_sigma': [0.226282, 0.552158, 0.734324], 'ask_prob': [0.4, 0.45, 0.69]}` |
| `ask_prob>=0.4 & abs_d_sigma>=0.1 & recross_hazard_score<=0.7` | 5 | 5/0 | 234.0 | 46.8 | `{'yes': 4, 'no': 1}` | `{'raw_edge': [0.12202900000000005, 0.20877999999999997, 0.34894699999999995], 'recross_hazard_score': [0.20173169569410354, 0.39634677763047876, 0.5965758829179154], 'abs_d_sigma': [0.226282, 0.552158, 0.734324], 'ask_prob': [0.4, 0.45, 0.69]}` |
| `ask_prob>=0.4 & abs_d_sigma>=0.2 & recross_hazard_score<=0.6` | 5 | 5/0 | 234.0 | 46.8 | `{'yes': 4, 'no': 1}` | `{'raw_edge': [0.12202900000000005, 0.20877999999999997, 0.34894699999999995], 'recross_hazard_score': [0.20173169569410354, 0.39634677763047876, 0.5965758829179154], 'abs_d_sigma': [0.226282, 0.552158, 0.734324], 'ask_prob': [0.4, 0.45, 0.69]}` |
| `ask_prob>=0.4 & abs_d_sigma>=0.2 & recross_hazard_score<=0.7` | 5 | 5/0 | 234.0 | 46.8 | `{'yes': 4, 'no': 1}` | `{'raw_edge': [0.12202900000000005, 0.20877999999999997, 0.34894699999999995], 'recross_hazard_score': [0.20173169569410354, 0.39634677763047876, 0.5965758829179154], 'abs_d_sigma': [0.226282, 0.552158, 0.734324], 'ask_prob': [0.4, 0.45, 0.69]}` |
| `ask_prob>=0.4 & abs_d_sigma>=0.2 & raw_edge>=0.1` | 5 | 5/0 | 234.0 | 46.8 | `{'yes': 4, 'no': 1}` | `{'raw_edge': [0.12202900000000005, 0.20877999999999997, 0.34894699999999995], 'recross_hazard_score': [0.20173169569410354, 0.39634677763047876, 0.5965758829179154], 'abs_d_sigma': [0.226282, 0.552158, 0.734324], 'ask_prob': [0.4, 0.45, 0.69]}` |
| `ask_prob>=0.4 & recross_hazard_score<=0.6 & recross_hazard_score<=0.7` | 5 | 5/0 | 234.0 | 46.8 | `{'yes': 4, 'no': 1}` | `{'raw_edge': [0.12202900000000005, 0.20877999999999997, 0.34894699999999995], 'recross_hazard_score': [0.20173169569410354, 0.39634677763047876, 0.5965758829179154], 'abs_d_sigma': [0.226282, 0.552158, 0.734324], 'ask_prob': [0.4, 0.45, 0.69]}` |

### Top Omitted Winners

| market | side | net c | edge | recross | abs d | ask | tags |
|---|---|---:|---:|---:|---:|---:|---|
| `KXBTC15M-26MAY061630-30` | `no` | 77.0 | 0.162456 | 0.19254835858215918 | 0.343001 | 0.2 | `['source_quality_risk', 'very_near_strike', 'cheap_tail_touch']` |
| `KXBTC15M-26MAY070730-30` | `no` | 76.0 | 0.227021 | 0.3253012001681479 | 0.144204 | 0.21 | `['source_quality_risk', 'very_near_strike', 'cheap_tail_touch']` |
| `KXBTC15M-26MAY062345-45` | `yes` | 67.0 | 0.29811099999999996 | 0.6399727981599007 | 0.214573 | 0.3 | `['source_quality_risk', 'high_recross_boundary_churn', 'very_near_strike', 'cheap_tail_touch']` |
| `KXBTC15M-26MAY061530-30` | `yes` | 56.0 | 0.20877999999999997 | 0.22815637451890164 | 0.226282 | 0.4 | `['source_quality_risk', 'very_near_strike', 'mid_cheap_touch']` |
| `KXBTC15M-26MAY061945-45` | `no` | 51.0 | 0.34894699999999995 | 0.39634677763047876 | 0.680058 | 0.45 | `['source_quality_risk', 'near_strike_boundary_pull', 'mid_cheap_touch']` |
| `KXBTC15M-26MAY070845-45` | `yes` | 51.0 | 0.14608799999999994 | 0.5965758829179154 | 0.236616 | 0.45 | `['source_quality_risk', 'high_recross_boundary_churn', 'very_near_strike', 'mid_cheap_touch']` |
| `KXBTC15M-26MAY062000-00` | `yes` | 48.0 | 0.25948899999999997 | 0.4198006566449445 | 0.552158 | 0.48 | `['source_quality_risk', 'near_strike_boundary_pull', 'mid_cheap_touch']` |
| `KXBTC15M-26MAY070045-45` | `no` | 48.0 | 0.10216400000000003 | 0.8305452261842349 | 0.187292 | 0.48 | `['source_quality_risk', 'high_recross_boundary_churn', 'very_near_strike', 'mid_cheap_touch']` |
| `KXBTC15M-26MAY070600-00` | `yes` | 28.0 | 0.12202900000000005 | 0.20173169569410354 | 0.734324 | 0.69 | `['source_quality_risk', 'near_strike_boundary_pull']` |

### Worst Omitted Losers

| market | side | net c | edge | recross | abs d | ask | tags |
|---|---|---:|---:|---:|---:|---:|---|
| `KXBTC15M-26MAY070900-00` | `no` | -56.0 | 0.08608300000000002 | 0.7010000307286993 | 0.253011 | 0.52 | `['source_quality_risk', 'realized_loss', 'thin_or_negative_net', 'high_recross_boundary_churn', 'very_near_strike', 'mid_cheap_touch']` |
| `KXBTC15M-26MAY061700-00` | `no` | -42.0 | 0.408347 | 0.19639134370333244 | 0.665443 | 0.38 | `['source_quality_risk', 'realized_loss', 'thin_or_negative_net', 'near_strike_boundary_pull', 'mid_cheap_touch']` |
| `KXBTC15M-26MAY062230-30` | `yes` | -42.0 | 0.33801499999999995 | 0.34967152719409217 | 0.481781 | 0.38 | `['source_quality_risk', 'realized_loss', 'thin_or_negative_net', 'very_near_strike', 'mid_cheap_touch']` |
| `KXBTC15M-26MAY061515-15` | `yes` | -30.0 | 0.10925099999999999 | 0.41393025340425893 | 0.289927 | 0.27 | `['source_quality_risk', 'realized_loss', 'thin_or_negative_net', 'very_near_strike', 'cheap_tail_touch']` |
| `KXBTC15M-26MAY061730-30` | `no` | -29.0 | 0.152854 | 0.7211101278549997 | 0.193064 | 0.26 | `['source_quality_risk', 'realized_loss', 'thin_or_negative_net', 'high_recross_boundary_churn', 'very_near_strike', 'cheap_tail_touch']` |
| `KXBTC15M-26MAY061930-30` | `no` | -28.0 | 0.30184 | 0.6888227956941311 | 0.118494 | 0.25 | `['source_quality_risk', 'realized_loss', 'thin_or_negative_net', 'high_recross_boundary_churn', 'very_near_strike', 'cheap_tail_touch']` |
| `KXBTC15M-26MAY070700-00` | `yes` | -28.0 | 0.445361 | 0.42112984035832196 | 0.477812 | 0.25 | `['source_quality_risk', 'realized_loss', 'thin_or_negative_net', 'very_near_strike', 'cheap_tail_touch']` |
| `KXBTC15M-26MAY061845-45` | `no` | -26.0 | 0.11107599999999998 | 0.6131714328215057 | 0.335691 | 0.23 | `['source_quality_risk', 'realized_loss', 'thin_or_negative_net', 'high_recross_boundary_churn', 'very_near_strike', 'cheap_tail_touch']` |
| `KXBTC15M-26MAY070100-00` | `no` | -25.0 | 0.28501300000000007 | 0.647900380591622 | 0.032616 | 0.22 | `['source_quality_risk', 'realized_loss', 'thin_or_negative_net', 'high_recross_boundary_churn', 'very_near_strike', 'cheap_tail_touch']` |
| `KXBTC15M-26MAY070145-45` | `yes` | -19.0 | 0.174262 | 0.3571782759435685 | 0.363444 | 0.17 | `['source_quality_risk', 'realized_loss', 'thin_or_negative_net', 'very_near_strike', 'cheap_tail_touch']` |
