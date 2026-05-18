# v28 Boundary-Clock Feature-Gate Frontier Mechanism

Research-only drilldown; no live bot changes or orders.

- Generated UTC: `2026-05-11T02:29:13.931965+00:00`
- Feature-gate freeze UTC: `2026-05-06T16:47:25.847566+00:00`

## Interpretation

- This is a drilldown of the current frontier audit, not a new frozen promotion candidate.
- post_feature_freeze_entry: frontier raw03_recross60_abs85_ask35 selects 52/82 for 514.0c versus reference 47/82 for 344.0c; gained rows net 43.0c with tags {'source_quality_risk': 5, 'thin_or_negative_net': 1, 'thin_raw_edge': 5}; omitted rows net 78.0c with fail reasons {'abs_d_below_min': 30, 'ask_below_min': 21, 'recross_above_max': 9}.
- post_feature_freeze_bridge: frontier raw03_recross60_abs85_ask35 selects 52/82 for 514.0c versus reference 47/82 for 344.0c; gained rows net 43.0c with tags {'source_quality_risk': 5, 'thin_or_negative_net': 1, 'thin_raw_edge': 5}; omitted rows net 78.0c with fail reasons {'abs_d_below_min': 30, 'ask_below_min': 21, 'recross_above_max': 9}.

## post_feature_freeze_entry

- Frontier rule: `raw03_recross60_abs85_ask35`
- Reference rule: `raw05_recross60_abs085_ask65`
- Frontier selected: `52/82`, net `514.0c`, coverage `63.41463414634146%`
- Reference selected: `47/82`, net `344.0c`, coverage `57.31707317073171%`
- Gained rows: `5`, net `43.0c`, tags `{'source_quality_risk': 5, 'thin_or_negative_net': 1, 'thin_raw_edge': 5}`
- Omitted rows: `30`, net `78.0c`, fail reasons `{'abs_d_below_min': 30, 'ask_below_min': 21, 'recross_above_max': 9}`
- Omitted mechanism tags: `{'source_quality_risk': 30, 'realized_loss': 21, 'thin_or_negative_net': 21, 'near_strike_boundary_pull': 8, 'cheap_tail_touch': 21, 'very_near_strike': 22, 'mid_cheap_touch': 8, 'high_recross_boundary_churn': 10}`

### Gained Rows

| market | source | side | net c | edge | recross | abs d | ask | outcome | fail reasons | tags |
|---|---|---|---:|---:|---:|---:|---:|---|---|---|
| KXBTC15M-26MAY071330-30 | rejected_actionable | no | 16.000000 | 0.044780 | 0.391694 | 0.927901 | 0.820000 | win | none | source_quality_risk, thin_raw_edge |
| KXBTC15M-26MAY071245-45 | rejected_actionable | no | 8.000000 | 0.034347 | 0.231360 | 1.285530 | 0.900000 | win | none | source_quality_risk, thin_raw_edge |
| KXBTC15M-26MAY071300-00 | rejected_actionable | no | 8.000000 | 0.038084 | 0.062061 | 1.290368 | 0.900000 | win | none | source_quality_risk, thin_raw_edge |
| KXBTC15M-26MAY070530-30 | rejected_actionable | no | 7.000000 | 0.047387 | 0.085902 | 1.454914 | 0.910000 | win | none | source_quality_risk, thin_raw_edge |
| KXBTC15M-26MAY062200-00 | rejected_actionable | no | 4.000000 | 0.042204 | 0.026847 | 2.370580 | 0.950000 | win | none | source_quality_risk, thin_or_negative_net, thin_raw_edge |

### Omitted Rows

| market | source | side | net c | edge | recross | abs d | ask | outcome | fail reasons | tags |
|---|---|---|---:|---:|---:|---:|---:|---|---|---|
| KXBTC15M-26MAY070900-00 | rejected_actionable | no | -56.000000 | 0.086083 | 0.701000 | 0.253011 | 0.520000 | loss | recross_above_max, abs_d_below_min | source_quality_risk, realized_loss, thin_or_negative_net, high_recross_boundary_churn, very_near_strike, mid_cheap_touch |
| KXBTC15M-26MAY061700-00 | rejected_actionable | no | -42.000000 | 0.408347 | 0.196391 | 0.665443 | 0.380000 | loss | abs_d_below_min | source_quality_risk, realized_loss, thin_or_negative_net, near_strike_boundary_pull, mid_cheap_touch |
| KXBTC15M-26MAY062230-30 | rejected_actionable | yes | -42.000000 | 0.338015 | 0.349672 | 0.481781 | 0.380000 | loss | abs_d_below_min | source_quality_risk, realized_loss, thin_or_negative_net, very_near_strike, mid_cheap_touch |
| KXBTC15M-26MAY061515-15 | rejected_actionable | yes | -30.000000 | 0.109251 | 0.413930 | 0.289927 | 0.270000 | loss | abs_d_below_min, ask_below_min | source_quality_risk, realized_loss, thin_or_negative_net, very_near_strike, cheap_tail_touch |
| KXBTC15M-26MAY061730-30 | rejected_actionable | no | -29.000000 | 0.152854 | 0.721110 | 0.193064 | 0.260000 | loss | recross_above_max, abs_d_below_min, ask_below_min | source_quality_risk, realized_loss, thin_or_negative_net, high_recross_boundary_churn, very_near_strike, cheap_tail_touch |
| KXBTC15M-26MAY061930-30 | rejected_actionable | no | -28.000000 | 0.301840 | 0.688823 | 0.118494 | 0.250000 | loss | recross_above_max, abs_d_below_min, ask_below_min | source_quality_risk, realized_loss, thin_or_negative_net, high_recross_boundary_churn, very_near_strike, cheap_tail_touch |
| KXBTC15M-26MAY070700-00 | rejected_actionable | yes | -28.000000 | 0.445361 | 0.421130 | 0.477812 | 0.250000 | loss | abs_d_below_min, ask_below_min | source_quality_risk, realized_loss, thin_or_negative_net, very_near_strike, cheap_tail_touch |
| KXBTC15M-26MAY061845-45 | rejected_actionable | no | -26.000000 | 0.111076 | 0.613171 | 0.335691 | 0.230000 | loss | recross_above_max, abs_d_below_min, ask_below_min | source_quality_risk, realized_loss, thin_or_negative_net, high_recross_boundary_churn, very_near_strike, cheap_tail_touch |
| KXBTC15M-26MAY070100-00 | rejected_actionable | no | -25.000000 | 0.285013 | 0.647900 | 0.032616 | 0.220000 | loss | recross_above_max, abs_d_below_min, ask_below_min | source_quality_risk, realized_loss, thin_or_negative_net, high_recross_boundary_churn, very_near_strike, cheap_tail_touch |
| KXBTC15M-26MAY070145-45 | rejected_actionable | yes | -19.000000 | 0.174262 | 0.357178 | 0.363444 | 0.170000 | loss | abs_d_below_min, ask_below_min | source_quality_risk, realized_loss, thin_or_negative_net, very_near_strike, cheap_tail_touch |
| KXBTC15M-26MAY061430-30 | rejected_actionable | no | -17.000000 | 0.107061 | 0.231659 | 0.557394 | 0.150000 | loss | abs_d_below_min, ask_below_min | source_quality_risk, realized_loss, thin_or_negative_net, near_strike_boundary_pull, cheap_tail_touch |
| KXBTC15M-26MAY061745-45 | rejected_actionable | no | -16.000000 | 0.370383 | 0.689790 | 0.021042 | 0.140000 | loss | recross_above_max, abs_d_below_min, ask_below_min | source_quality_risk, realized_loss, thin_or_negative_net, high_recross_boundary_churn, very_near_strike, cheap_tail_touch |
| KXBTC15M-26MAY061500-00 | rejected_actionable | yes | -13.000000 | 0.316725 | 0.094209 | 0.183718 | 0.110000 | loss | abs_d_below_min, ask_below_min | source_quality_risk, realized_loss, thin_or_negative_net, very_near_strike, cheap_tail_touch |
| KXBTC15M-26MAY070200-00 | rejected_actionable | yes | -12.000000 | 0.260667 | 0.208918 | 0.323872 | 0.100000 | loss | abs_d_below_min, ask_below_min | source_quality_risk, realized_loss, thin_or_negative_net, very_near_strike, cheap_tail_touch |
| KXBTC15M-26MAY070800-00 | rejected_actionable | yes | -12.000000 | 0.329038 | 0.628964 | 0.163026 | 0.100000 | loss | recross_above_max, abs_d_below_min, ask_below_min | source_quality_risk, realized_loss, thin_or_negative_net, high_recross_boundary_churn, very_near_strike, cheap_tail_touch |
| KXBTC15M-26MAY061600-00 | rejected_actionable | no | -7.000000 | 0.104874 | 0.041740 | 0.791108 | 0.060000 | loss | abs_d_below_min, ask_below_min | source_quality_risk, realized_loss, thin_or_negative_net, near_strike_boundary_pull, cheap_tail_touch |
| KXBTC15M-26MAY070130-30 | rejected_actionable | yes | -7.000000 | 0.211426 | 0.174274 | 0.513769 | 0.060000 | loss | abs_d_below_min, ask_below_min | source_quality_risk, realized_loss, thin_or_negative_net, near_strike_boundary_pull, cheap_tail_touch |
| KXBTC15M-26MAY070630-30 | rejected_actionable | yes | -6.000000 | 0.474276 | 0.335538 | 0.025583 | 0.050000 | loss | abs_d_below_min, ask_below_min | source_quality_risk, realized_loss, thin_or_negative_net, very_near_strike, cheap_tail_touch |
| KXBTC15M-26MAY062330-30 | rejected_actionable | yes | -5.000000 | 0.514636 | 0.307484 | 0.121467 | 0.040000 | loss | abs_d_below_min, ask_below_min | source_quality_risk, realized_loss, thin_or_negative_net, very_near_strike, cheap_tail_touch |
| KXBTC15M-26MAY061715-15 | rejected_actionable | yes | -2.000000 | 0.250844 | 0.072090 | 0.552786 | 0.010000 | loss | abs_d_below_min, ask_below_min | source_quality_risk, realized_loss, thin_or_negative_net, near_strike_boundary_pull, cheap_tail_touch |
| KXBTC15M-26MAY070615-15 | rejected_actionable | yes | -2.000000 | 0.568996 | 0.142600 | 0.170925 | 0.010000 | loss | abs_d_below_min, ask_below_min | source_quality_risk, realized_loss, thin_or_negative_net, very_near_strike, cheap_tail_touch |
| KXBTC15M-26MAY070600-00 | rejected_actionable | yes | 28.000000 | 0.122029 | 0.201732 | 0.734324 | 0.690000 | win | abs_d_below_min | source_quality_risk, near_strike_boundary_pull |
| KXBTC15M-26MAY062000-00 | rejected_actionable | yes | 48.000000 | 0.259489 | 0.419801 | 0.552158 | 0.480000 | win | abs_d_below_min | source_quality_risk, near_strike_boundary_pull, mid_cheap_touch |
| KXBTC15M-26MAY070045-45 | rejected_actionable | no | 48.000000 | 0.102164 | 0.830545 | 0.187292 | 0.480000 | win | recross_above_max, abs_d_below_min | source_quality_risk, high_recross_boundary_churn, very_near_strike, mid_cheap_touch |
| KXBTC15M-26MAY061945-45 | rejected_actionable | no | 51.000000 | 0.348947 | 0.396347 | 0.680058 | 0.450000 | win | abs_d_below_min | source_quality_risk, near_strike_boundary_pull, mid_cheap_touch |
| KXBTC15M-26MAY070845-45 | rejected_actionable | yes | 51.000000 | 0.146088 | 0.596576 | 0.236616 | 0.450000 | win | abs_d_below_min | source_quality_risk, high_recross_boundary_churn, very_near_strike, mid_cheap_touch |
| KXBTC15M-26MAY061530-30 | rejected_actionable | yes | 56.000000 | 0.208780 | 0.228156 | 0.226282 | 0.400000 | win | abs_d_below_min | source_quality_risk, very_near_strike, mid_cheap_touch |
| KXBTC15M-26MAY062345-45 | rejected_actionable | yes | 67.000000 | 0.298111 | 0.639973 | 0.214573 | 0.300000 | win | recross_above_max, abs_d_below_min, ask_below_min | source_quality_risk, high_recross_boundary_churn, very_near_strike, cheap_tail_touch |
| KXBTC15M-26MAY070730-30 | rejected_actionable | no | 76.000000 | 0.227021 | 0.325301 | 0.144204 | 0.210000 | win | abs_d_below_min, ask_below_min | source_quality_risk, very_near_strike, cheap_tail_touch |
| KXBTC15M-26MAY061630-30 | rejected_actionable | no | 77.000000 | 0.162456 | 0.192548 | 0.343001 | 0.200000 | win | abs_d_below_min, ask_below_min | source_quality_risk, very_near_strike, cheap_tail_touch |

## post_feature_freeze_bridge

- Frontier rule: `raw03_recross60_abs85_ask35`
- Reference rule: `raw05_recross60_abs085_ask65`
- Frontier selected: `52/82`, net `514.0c`, coverage `63.41463414634146%`
- Reference selected: `47/82`, net `344.0c`, coverage `57.31707317073171%`
- Gained rows: `5`, net `43.0c`, tags `{'source_quality_risk': 5, 'thin_or_negative_net': 1, 'thin_raw_edge': 5}`
- Omitted rows: `30`, net `78.0c`, fail reasons `{'abs_d_below_min': 30, 'ask_below_min': 21, 'recross_above_max': 9}`
- Omitted mechanism tags: `{'source_quality_risk': 30, 'realized_loss': 21, 'thin_or_negative_net': 21, 'near_strike_boundary_pull': 8, 'cheap_tail_touch': 21, 'very_near_strike': 22, 'mid_cheap_touch': 8, 'high_recross_boundary_churn': 10}`

### Gained Rows

| market | source | side | net c | edge | recross | abs d | ask | outcome | fail reasons | tags |
|---|---|---|---:|---:|---:|---:|---:|---|---|---|
| KXBTC15M-26MAY071330-30 | rejected_actionable | no | 16.000000 | 0.044780 | 0.391694 | 0.927901 | 0.820000 | win | none | source_quality_risk, thin_raw_edge |
| KXBTC15M-26MAY071245-45 | rejected_actionable | no | 8.000000 | 0.034347 | 0.231360 | 1.285530 | 0.900000 | win | none | source_quality_risk, thin_raw_edge |
| KXBTC15M-26MAY071300-00 | rejected_actionable | no | 8.000000 | 0.038084 | 0.062061 | 1.290368 | 0.900000 | win | none | source_quality_risk, thin_raw_edge |
| KXBTC15M-26MAY070530-30 | rejected_actionable | no | 7.000000 | 0.047387 | 0.085902 | 1.454914 | 0.910000 | win | none | source_quality_risk, thin_raw_edge |
| KXBTC15M-26MAY062200-00 | rejected_actionable | no | 4.000000 | 0.042204 | 0.026847 | 2.370580 | 0.950000 | win | none | source_quality_risk, thin_or_negative_net, thin_raw_edge |

### Omitted Rows

| market | source | side | net c | edge | recross | abs d | ask | outcome | fail reasons | tags |
|---|---|---|---:|---:|---:|---:|---:|---|---|---|
| KXBTC15M-26MAY070900-00 | rejected_actionable | no | -56.000000 | 0.086083 | 0.701000 | 0.253011 | 0.520000 | loss | recross_above_max, abs_d_below_min | source_quality_risk, realized_loss, thin_or_negative_net, high_recross_boundary_churn, very_near_strike, mid_cheap_touch |
| KXBTC15M-26MAY061700-00 | rejected_actionable | no | -42.000000 | 0.408347 | 0.196391 | 0.665443 | 0.380000 | loss | abs_d_below_min | source_quality_risk, realized_loss, thin_or_negative_net, near_strike_boundary_pull, mid_cheap_touch |
| KXBTC15M-26MAY062230-30 | rejected_actionable | yes | -42.000000 | 0.338015 | 0.349672 | 0.481781 | 0.380000 | loss | abs_d_below_min | source_quality_risk, realized_loss, thin_or_negative_net, very_near_strike, mid_cheap_touch |
| KXBTC15M-26MAY061515-15 | rejected_actionable | yes | -30.000000 | 0.109251 | 0.413930 | 0.289927 | 0.270000 | loss | abs_d_below_min, ask_below_min | source_quality_risk, realized_loss, thin_or_negative_net, very_near_strike, cheap_tail_touch |
| KXBTC15M-26MAY061730-30 | rejected_actionable | no | -29.000000 | 0.152854 | 0.721110 | 0.193064 | 0.260000 | loss | recross_above_max, abs_d_below_min, ask_below_min | source_quality_risk, realized_loss, thin_or_negative_net, high_recross_boundary_churn, very_near_strike, cheap_tail_touch |
| KXBTC15M-26MAY061930-30 | rejected_actionable | no | -28.000000 | 0.301840 | 0.688823 | 0.118494 | 0.250000 | loss | recross_above_max, abs_d_below_min, ask_below_min | source_quality_risk, realized_loss, thin_or_negative_net, high_recross_boundary_churn, very_near_strike, cheap_tail_touch |
| KXBTC15M-26MAY070700-00 | rejected_actionable | yes | -28.000000 | 0.445361 | 0.421130 | 0.477812 | 0.250000 | loss | abs_d_below_min, ask_below_min | source_quality_risk, realized_loss, thin_or_negative_net, very_near_strike, cheap_tail_touch |
| KXBTC15M-26MAY061845-45 | rejected_actionable | no | -26.000000 | 0.111076 | 0.613171 | 0.335691 | 0.230000 | loss | recross_above_max, abs_d_below_min, ask_below_min | source_quality_risk, realized_loss, thin_or_negative_net, high_recross_boundary_churn, very_near_strike, cheap_tail_touch |
| KXBTC15M-26MAY070100-00 | rejected_actionable | no | -25.000000 | 0.285013 | 0.647900 | 0.032616 | 0.220000 | loss | recross_above_max, abs_d_below_min, ask_below_min | source_quality_risk, realized_loss, thin_or_negative_net, high_recross_boundary_churn, very_near_strike, cheap_tail_touch |
| KXBTC15M-26MAY070145-45 | rejected_actionable | yes | -19.000000 | 0.174262 | 0.357178 | 0.363444 | 0.170000 | loss | abs_d_below_min, ask_below_min | source_quality_risk, realized_loss, thin_or_negative_net, very_near_strike, cheap_tail_touch |
| KXBTC15M-26MAY061430-30 | rejected_actionable | no | -17.000000 | 0.107061 | 0.231659 | 0.557394 | 0.150000 | loss | abs_d_below_min, ask_below_min | source_quality_risk, realized_loss, thin_or_negative_net, near_strike_boundary_pull, cheap_tail_touch |
| KXBTC15M-26MAY061745-45 | rejected_actionable | no | -16.000000 | 0.370383 | 0.689790 | 0.021042 | 0.140000 | loss | recross_above_max, abs_d_below_min, ask_below_min | source_quality_risk, realized_loss, thin_or_negative_net, high_recross_boundary_churn, very_near_strike, cheap_tail_touch |
| KXBTC15M-26MAY061500-00 | rejected_actionable | yes | -13.000000 | 0.316725 | 0.094209 | 0.183718 | 0.110000 | loss | abs_d_below_min, ask_below_min | source_quality_risk, realized_loss, thin_or_negative_net, very_near_strike, cheap_tail_touch |
| KXBTC15M-26MAY070200-00 | rejected_actionable | yes | -12.000000 | 0.260667 | 0.208918 | 0.323872 | 0.100000 | loss | abs_d_below_min, ask_below_min | source_quality_risk, realized_loss, thin_or_negative_net, very_near_strike, cheap_tail_touch |
| KXBTC15M-26MAY070800-00 | rejected_actionable | yes | -12.000000 | 0.329038 | 0.628964 | 0.163026 | 0.100000 | loss | recross_above_max, abs_d_below_min, ask_below_min | source_quality_risk, realized_loss, thin_or_negative_net, high_recross_boundary_churn, very_near_strike, cheap_tail_touch |
| KXBTC15M-26MAY061600-00 | rejected_actionable | no | -7.000000 | 0.104874 | 0.041740 | 0.791108 | 0.060000 | loss | abs_d_below_min, ask_below_min | source_quality_risk, realized_loss, thin_or_negative_net, near_strike_boundary_pull, cheap_tail_touch |
| KXBTC15M-26MAY070130-30 | rejected_actionable | yes | -7.000000 | 0.211426 | 0.174274 | 0.513769 | 0.060000 | loss | abs_d_below_min, ask_below_min | source_quality_risk, realized_loss, thin_or_negative_net, near_strike_boundary_pull, cheap_tail_touch |
| KXBTC15M-26MAY070630-30 | rejected_actionable | yes | -6.000000 | 0.474276 | 0.335538 | 0.025583 | 0.050000 | loss | abs_d_below_min, ask_below_min | source_quality_risk, realized_loss, thin_or_negative_net, very_near_strike, cheap_tail_touch |
| KXBTC15M-26MAY062330-30 | rejected_actionable | yes | -5.000000 | 0.514636 | 0.307484 | 0.121467 | 0.040000 | loss | abs_d_below_min, ask_below_min | source_quality_risk, realized_loss, thin_or_negative_net, very_near_strike, cheap_tail_touch |
| KXBTC15M-26MAY061715-15 | rejected_actionable | yes | -2.000000 | 0.250844 | 0.072090 | 0.552786 | 0.010000 | loss | abs_d_below_min, ask_below_min | source_quality_risk, realized_loss, thin_or_negative_net, near_strike_boundary_pull, cheap_tail_touch |
| KXBTC15M-26MAY070615-15 | rejected_actionable | yes | -2.000000 | 0.568996 | 0.142600 | 0.170925 | 0.010000 | loss | abs_d_below_min, ask_below_min | source_quality_risk, realized_loss, thin_or_negative_net, very_near_strike, cheap_tail_touch |
| KXBTC15M-26MAY070600-00 | rejected_actionable | yes | 28.000000 | 0.122029 | 0.201732 | 0.734324 | 0.690000 | win | abs_d_below_min | source_quality_risk, near_strike_boundary_pull |
| KXBTC15M-26MAY062000-00 | rejected_actionable | yes | 48.000000 | 0.259489 | 0.419801 | 0.552158 | 0.480000 | win | abs_d_below_min | source_quality_risk, near_strike_boundary_pull, mid_cheap_touch |
| KXBTC15M-26MAY070045-45 | rejected_actionable | no | 48.000000 | 0.102164 | 0.830545 | 0.187292 | 0.480000 | win | recross_above_max, abs_d_below_min | source_quality_risk, high_recross_boundary_churn, very_near_strike, mid_cheap_touch |
| KXBTC15M-26MAY061945-45 | rejected_actionable | no | 51.000000 | 0.348947 | 0.396347 | 0.680058 | 0.450000 | win | abs_d_below_min | source_quality_risk, near_strike_boundary_pull, mid_cheap_touch |
| KXBTC15M-26MAY070845-45 | rejected_actionable | yes | 51.000000 | 0.146088 | 0.596576 | 0.236616 | 0.450000 | win | abs_d_below_min | source_quality_risk, high_recross_boundary_churn, very_near_strike, mid_cheap_touch |
| KXBTC15M-26MAY061530-30 | rejected_actionable | yes | 56.000000 | 0.208780 | 0.228156 | 0.226282 | 0.400000 | win | abs_d_below_min | source_quality_risk, very_near_strike, mid_cheap_touch |
| KXBTC15M-26MAY062345-45 | rejected_actionable | yes | 67.000000 | 0.298111 | 0.639973 | 0.214573 | 0.300000 | win | recross_above_max, abs_d_below_min, ask_below_min | source_quality_risk, high_recross_boundary_churn, very_near_strike, cheap_tail_touch |
| KXBTC15M-26MAY070730-30 | rejected_actionable | no | 76.000000 | 0.227021 | 0.325301 | 0.144204 | 0.210000 | win | abs_d_below_min, ask_below_min | source_quality_risk, very_near_strike, cheap_tail_touch |
| KXBTC15M-26MAY061630-30 | rejected_actionable | no | 77.000000 | 0.162456 | 0.192548 | 0.343001 | 0.200000 | win | abs_d_below_min, ask_below_min | source_quality_risk, very_near_strike, cheap_tail_touch |
