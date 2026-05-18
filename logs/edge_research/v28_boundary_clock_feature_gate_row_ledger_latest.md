# v28 Boundary-Clock Feature-Gate Row Ledger

Research-only; no live bot changes or orders.

- Generated UTC: `2026-05-07T17:53:43.542387+00:00`
- Feature-gate freeze UTC: `2026-05-06T16:47:25.847566+00:00`

## Interpretation

- This ledger uses only observable gate features for pass/fail reasons; source labels are shown only for evidence-quality audit.
- post_feature_freeze_entry best current rule raw07_recross60_abs085 selects 38 of 82 denominator markets, net 454.0c, with omission reasons {'abs_d_below_min': 38, 'raw_edge_below_min': 7, 'recross_above_max': 10}.
- post_feature_freeze_bridge best current rule raw07_recross60_abs085 selects 38 of 82 denominator markets, net 454.0c, with omission reasons {'abs_d_below_min': 38, 'raw_edge_below_min': 7, 'recross_above_max': 10}.

## post_feature_freeze_entry

| rule | selected/den | settled | W/L | coverage | net c | observed markets | unobserved | omission reasons |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| raw07_recross60_abs085 | 38/82 | 38 | 29/9 | 46.341463 | 454.000000 | 82 | 0 | abs_d_below_min:38, raw_edge_below_min:7, recross_above_max:10 |
| raw05_recross60_abs085 | 55/82 | 55 | 39/16 | 67.073171 | 445.000000 | 82 | 0 | abs_d_below_min:26, recross_above_max:9, raw_edge_below_min:1 |
| raw05_recross60_abs085_ask65 | 47/82 | 47 | 42/5 | 57.317073 | 344.000000 | 82 | 0 | abs_d_below_min:34, ask_below_min:33, recross_above_max:10, raw_edge_below_min:1 |
| raw03_recross70_abs075 | 64/82 | 64 | 42/22 | 78.048780 | 307.000000 | 82 | 0 | abs_d_below_min:18, recross_above_max:1 |

### Omitted Examples

| rule | market | source | side | net c | edge | recross | abs d | ask | fail reasons |
|---|---|---|---|---:|---:|---:|---:|---:|---|
| raw07_recross60_abs085 | KXBTC15M-26MAY062145-45 | rejected_actionable | no | -14.000000 | 0.663823 | 0.195824 | 0.666418 | 0.120000 | abs_d_below_min |
| raw07_recross60_abs085 | KXBTC15M-26MAY070615-15 | rejected_actionable | yes | -2.000000 | 0.568996 | 0.142600 | 0.170925 | 0.010000 | abs_d_below_min |
| raw07_recross60_abs085 | KXBTC15M-26MAY062330-30 | rejected_actionable | yes | -5.000000 | 0.514636 | 0.307484 | 0.121467 | 0.040000 | abs_d_below_min |
| raw07_recross60_abs085 | KXBTC15M-26MAY070630-30 | rejected_actionable | yes | -6.000000 | 0.474276 | 0.335538 | 0.025583 | 0.050000 | abs_d_below_min |
| raw07_recross60_abs085 | KXBTC15M-26MAY070700-00 | rejected_actionable | yes | -28.000000 | 0.445361 | 0.421130 | 0.477812 | 0.250000 | abs_d_below_min |
| raw07_recross60_abs085 | KXBTC15M-26MAY061700-00 | rejected_actionable | no | -42.000000 | 0.408347 | 0.196391 | 0.665443 | 0.380000 | abs_d_below_min |
| raw07_recross60_abs085 | KXBTC15M-26MAY061745-45 | rejected_actionable | no | -16.000000 | 0.370383 | 0.689790 | 0.021042 | 0.140000 | recross_above_max, abs_d_below_min |
| raw07_recross60_abs085 | KXBTC15M-26MAY061945-45 | rejected_actionable | no | 51.000000 | 0.348947 | 0.396347 | 0.680058 | 0.450000 | abs_d_below_min |
| raw07_recross60_abs085 | KXBTC15M-26MAY062230-30 | rejected_actionable | yes | -42.000000 | 0.338015 | 0.349672 | 0.481781 | 0.380000 | abs_d_below_min |
| raw07_recross60_abs085 | KXBTC15M-26MAY070800-00 | rejected_actionable | yes | -12.000000 | 0.329038 | 0.628964 | 0.163026 | 0.100000 | recross_above_max, abs_d_below_min |
| raw07_recross60_abs085 | KXBTC15M-26MAY061830-30 | rejected_actionable | yes | -26.000000 | 0.323162 | 0.631576 | 0.098877 | 0.230000 | recross_above_max, abs_d_below_min |
| raw07_recross60_abs085 | KXBTC15M-26MAY061500-00 | rejected_actionable | yes | -13.000000 | 0.316725 | 0.094209 | 0.183718 | 0.110000 | abs_d_below_min |
| raw05_recross60_abs085 | KXBTC15M-26MAY070615-15 | rejected_actionable | yes | -2.000000 | 0.568996 | 0.142600 | 0.170925 | 0.010000 | abs_d_below_min |
| raw05_recross60_abs085 | KXBTC15M-26MAY062330-30 | rejected_actionable | yes | -5.000000 | 0.514636 | 0.307484 | 0.121467 | 0.040000 | abs_d_below_min |
| raw05_recross60_abs085 | KXBTC15M-26MAY070630-30 | rejected_actionable | yes | -6.000000 | 0.474276 | 0.335538 | 0.025583 | 0.050000 | abs_d_below_min |
| raw05_recross60_abs085 | KXBTC15M-26MAY070700-00 | rejected_actionable | yes | -28.000000 | 0.445361 | 0.421130 | 0.477812 | 0.250000 | abs_d_below_min |
| raw05_recross60_abs085 | KXBTC15M-26MAY061700-00 | rejected_actionable | no | -42.000000 | 0.408347 | 0.196391 | 0.665443 | 0.380000 | abs_d_below_min |
| raw05_recross60_abs085 | KXBTC15M-26MAY061745-45 | rejected_actionable | no | -16.000000 | 0.370383 | 0.689790 | 0.021042 | 0.140000 | recross_above_max, abs_d_below_min |
| raw05_recross60_abs085 | KXBTC15M-26MAY061945-45 | rejected_actionable | no | 51.000000 | 0.348947 | 0.396347 | 0.680058 | 0.450000 | abs_d_below_min |
| raw05_recross60_abs085 | KXBTC15M-26MAY062230-30 | rejected_actionable | yes | -42.000000 | 0.338015 | 0.349672 | 0.481781 | 0.380000 | abs_d_below_min |
| raw05_recross60_abs085 | KXBTC15M-26MAY070800-00 | rejected_actionable | yes | -12.000000 | 0.329038 | 0.628964 | 0.163026 | 0.100000 | recross_above_max, abs_d_below_min |
| raw05_recross60_abs085 | KXBTC15M-26MAY061500-00 | rejected_actionable | yes | -13.000000 | 0.316725 | 0.094209 | 0.183718 | 0.110000 | abs_d_below_min |
| raw05_recross60_abs085 | KXBTC15M-26MAY061930-30 | rejected_actionable | no | -28.000000 | 0.301840 | 0.688823 | 0.118494 | 0.250000 | recross_above_max, abs_d_below_min |
| raw05_recross60_abs085 | KXBTC15M-26MAY062345-45 | rejected_actionable | yes | 67.000000 | 0.298111 | 0.639973 | 0.214573 | 0.300000 | recross_above_max, abs_d_below_min |
| raw05_recross60_abs085_ask65 | KXBTC15M-26MAY070615-15 | rejected_actionable | yes | -2.000000 | 0.568996 | 0.142600 | 0.170925 | 0.010000 | abs_d_below_min, ask_below_min |
| raw05_recross60_abs085_ask65 | KXBTC15M-26MAY062330-30 | rejected_actionable | yes | -5.000000 | 0.514636 | 0.307484 | 0.121467 | 0.040000 | abs_d_below_min, ask_below_min |
| raw05_recross60_abs085_ask65 | KXBTC15M-26MAY070630-30 | rejected_actionable | yes | -6.000000 | 0.474276 | 0.335538 | 0.025583 | 0.050000 | abs_d_below_min, ask_below_min |
| raw05_recross60_abs085_ask65 | KXBTC15M-26MAY070700-00 | rejected_actionable | yes | -28.000000 | 0.445361 | 0.421130 | 0.477812 | 0.250000 | abs_d_below_min, ask_below_min |
| raw05_recross60_abs085_ask65 | KXBTC15M-26MAY061700-00 | rejected_actionable | no | -42.000000 | 0.408347 | 0.196391 | 0.665443 | 0.380000 | abs_d_below_min, ask_below_min |
| raw05_recross60_abs085_ask65 | KXBTC15M-26MAY061745-45 | rejected_actionable | no | -16.000000 | 0.370383 | 0.689790 | 0.021042 | 0.140000 | recross_above_max, abs_d_below_min, ask_below_min |
| raw05_recross60_abs085_ask65 | KXBTC15M-26MAY061945-45 | rejected_actionable | no | 51.000000 | 0.348947 | 0.396347 | 0.680058 | 0.450000 | abs_d_below_min, ask_below_min |
| raw05_recross60_abs085_ask65 | KXBTC15M-26MAY062230-30 | rejected_actionable | yes | -42.000000 | 0.338015 | 0.349672 | 0.481781 | 0.380000 | abs_d_below_min, ask_below_min |
| raw05_recross60_abs085_ask65 | KXBTC15M-26MAY070800-00 | rejected_actionable | yes | -12.000000 | 0.329038 | 0.628964 | 0.163026 | 0.100000 | recross_above_max, abs_d_below_min, ask_below_min |
| raw05_recross60_abs085_ask65 | KXBTC15M-26MAY061500-00 | rejected_actionable | yes | -13.000000 | 0.316725 | 0.094209 | 0.183718 | 0.110000 | abs_d_below_min, ask_below_min |
| raw05_recross60_abs085_ask65 | KXBTC15M-26MAY061930-30 | rejected_actionable | no | -28.000000 | 0.301840 | 0.688823 | 0.118494 | 0.250000 | recross_above_max, abs_d_below_min, ask_below_min |
| raw05_recross60_abs085_ask65 | KXBTC15M-26MAY062345-45 | rejected_actionable | yes | 67.000000 | 0.298111 | 0.639973 | 0.214573 | 0.300000 | recross_above_max, abs_d_below_min, ask_below_min |
| raw03_recross70_abs075 | KXBTC15M-26MAY062330-30 | rejected_actionable | yes | -5.000000 | 0.514636 | 0.307484 | 0.121467 | 0.040000 | abs_d_below_min |
| raw03_recross70_abs075 | KXBTC15M-26MAY070630-30 | rejected_actionable | yes | -6.000000 | 0.474276 | 0.335538 | 0.025583 | 0.050000 | abs_d_below_min |
| raw03_recross70_abs075 | KXBTC15M-26MAY070700-00 | rejected_actionable | yes | -28.000000 | 0.445361 | 0.421130 | 0.477812 | 0.250000 | abs_d_below_min |
| raw03_recross70_abs075 | KXBTC15M-26MAY061700-00 | rejected_actionable | no | -42.000000 | 0.408347 | 0.196391 | 0.665443 | 0.380000 | abs_d_below_min |
| raw03_recross70_abs075 | KXBTC15M-26MAY061745-45 | rejected_actionable | no | -16.000000 | 0.370383 | 0.689790 | 0.021042 | 0.140000 | abs_d_below_min |
| raw03_recross70_abs075 | KXBTC15M-26MAY061945-45 | rejected_actionable | no | 51.000000 | 0.348947 | 0.396347 | 0.680058 | 0.450000 | abs_d_below_min |
| raw03_recross70_abs075 | KXBTC15M-26MAY062230-30 | rejected_actionable | yes | -42.000000 | 0.338015 | 0.349672 | 0.481781 | 0.380000 | abs_d_below_min |
| raw03_recross70_abs075 | KXBTC15M-26MAY070800-00 | rejected_actionable | yes | -12.000000 | 0.329038 | 0.628964 | 0.163026 | 0.100000 | abs_d_below_min |
| raw03_recross70_abs075 | KXBTC15M-26MAY061500-00 | rejected_actionable | yes | -13.000000 | 0.316725 | 0.094209 | 0.183718 | 0.110000 | abs_d_below_min |
| raw03_recross70_abs075 | KXBTC15M-26MAY070100-00 | rejected_actionable | no | -25.000000 | 0.285013 | 0.647900 | 0.032616 | 0.220000 | abs_d_below_min |
| raw03_recross70_abs075 | KXBTC15M-26MAY062000-00 | rejected_actionable | yes | 48.000000 | 0.259489 | 0.419801 | 0.552158 | 0.480000 | abs_d_below_min |
| raw03_recross70_abs075 | KXBTC15M-26MAY061715-15 | rejected_actionable | yes | -2.000000 | 0.250844 | 0.072090 | 0.552786 | 0.010000 | abs_d_below_min |

## post_feature_freeze_bridge

| rule | selected/den | settled | W/L | coverage | net c | observed markets | unobserved | omission reasons |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| raw07_recross60_abs085 | 38/82 | 38 | 29/9 | 46.341463 | 454.000000 | 82 | 0 | abs_d_below_min:38, raw_edge_below_min:7, recross_above_max:10 |
| raw05_recross60_abs085 | 55/82 | 55 | 39/16 | 67.073171 | 445.000000 | 82 | 0 | abs_d_below_min:26, recross_above_max:9, raw_edge_below_min:1 |
| raw05_recross60_abs085_ask65 | 47/82 | 47 | 42/5 | 57.317073 | 344.000000 | 82 | 0 | abs_d_below_min:34, ask_below_min:33, recross_above_max:10, raw_edge_below_min:1 |
| raw03_recross70_abs075 | 64/82 | 64 | 42/22 | 78.048780 | 307.000000 | 82 | 0 | abs_d_below_min:18, recross_above_max:1 |

### Omitted Examples

| rule | market | source | side | net c | edge | recross | abs d | ask | fail reasons |
|---|---|---|---|---:|---:|---:|---:|---:|---|
| raw07_recross60_abs085 | KXBTC15M-26MAY062145-45 | rejected_actionable | no | -14.000000 | 0.663823 | 0.195824 | 0.666418 | 0.120000 | abs_d_below_min |
| raw07_recross60_abs085 | KXBTC15M-26MAY070615-15 | rejected_actionable | yes | -2.000000 | 0.568996 | 0.142600 | 0.170925 | 0.010000 | abs_d_below_min |
| raw07_recross60_abs085 | KXBTC15M-26MAY062330-30 | rejected_actionable | yes | -5.000000 | 0.514636 | 0.307484 | 0.121467 | 0.040000 | abs_d_below_min |
| raw07_recross60_abs085 | KXBTC15M-26MAY070630-30 | rejected_actionable | yes | -6.000000 | 0.474276 | 0.335538 | 0.025583 | 0.050000 | abs_d_below_min |
| raw07_recross60_abs085 | KXBTC15M-26MAY070700-00 | rejected_actionable | yes | -28.000000 | 0.445361 | 0.421130 | 0.477812 | 0.250000 | abs_d_below_min |
| raw07_recross60_abs085 | KXBTC15M-26MAY061700-00 | rejected_actionable | no | -42.000000 | 0.408347 | 0.196391 | 0.665443 | 0.380000 | abs_d_below_min |
| raw07_recross60_abs085 | KXBTC15M-26MAY061745-45 | rejected_actionable | no | -16.000000 | 0.370383 | 0.689790 | 0.021042 | 0.140000 | recross_above_max, abs_d_below_min |
| raw07_recross60_abs085 | KXBTC15M-26MAY061945-45 | rejected_actionable | no | 51.000000 | 0.348947 | 0.396347 | 0.680058 | 0.450000 | abs_d_below_min |
| raw07_recross60_abs085 | KXBTC15M-26MAY062230-30 | rejected_actionable | yes | -42.000000 | 0.338015 | 0.349672 | 0.481781 | 0.380000 | abs_d_below_min |
| raw07_recross60_abs085 | KXBTC15M-26MAY070800-00 | rejected_actionable | yes | -12.000000 | 0.329038 | 0.628964 | 0.163026 | 0.100000 | recross_above_max, abs_d_below_min |
| raw07_recross60_abs085 | KXBTC15M-26MAY061830-30 | rejected_actionable | yes | -26.000000 | 0.323162 | 0.631576 | 0.098877 | 0.230000 | recross_above_max, abs_d_below_min |
| raw07_recross60_abs085 | KXBTC15M-26MAY061500-00 | rejected_actionable | yes | -13.000000 | 0.316725 | 0.094209 | 0.183718 | 0.110000 | abs_d_below_min |
| raw05_recross60_abs085 | KXBTC15M-26MAY070615-15 | rejected_actionable | yes | -2.000000 | 0.568996 | 0.142600 | 0.170925 | 0.010000 | abs_d_below_min |
| raw05_recross60_abs085 | KXBTC15M-26MAY062330-30 | rejected_actionable | yes | -5.000000 | 0.514636 | 0.307484 | 0.121467 | 0.040000 | abs_d_below_min |
| raw05_recross60_abs085 | KXBTC15M-26MAY070630-30 | rejected_actionable | yes | -6.000000 | 0.474276 | 0.335538 | 0.025583 | 0.050000 | abs_d_below_min |
| raw05_recross60_abs085 | KXBTC15M-26MAY070700-00 | rejected_actionable | yes | -28.000000 | 0.445361 | 0.421130 | 0.477812 | 0.250000 | abs_d_below_min |
| raw05_recross60_abs085 | KXBTC15M-26MAY061700-00 | rejected_actionable | no | -42.000000 | 0.408347 | 0.196391 | 0.665443 | 0.380000 | abs_d_below_min |
| raw05_recross60_abs085 | KXBTC15M-26MAY061745-45 | rejected_actionable | no | -16.000000 | 0.370383 | 0.689790 | 0.021042 | 0.140000 | recross_above_max, abs_d_below_min |
| raw05_recross60_abs085 | KXBTC15M-26MAY061945-45 | rejected_actionable | no | 51.000000 | 0.348947 | 0.396347 | 0.680058 | 0.450000 | abs_d_below_min |
| raw05_recross60_abs085 | KXBTC15M-26MAY062230-30 | rejected_actionable | yes | -42.000000 | 0.338015 | 0.349672 | 0.481781 | 0.380000 | abs_d_below_min |
| raw05_recross60_abs085 | KXBTC15M-26MAY070800-00 | rejected_actionable | yes | -12.000000 | 0.329038 | 0.628964 | 0.163026 | 0.100000 | recross_above_max, abs_d_below_min |
| raw05_recross60_abs085 | KXBTC15M-26MAY061500-00 | rejected_actionable | yes | -13.000000 | 0.316725 | 0.094209 | 0.183718 | 0.110000 | abs_d_below_min |
| raw05_recross60_abs085 | KXBTC15M-26MAY061930-30 | rejected_actionable | no | -28.000000 | 0.301840 | 0.688823 | 0.118494 | 0.250000 | recross_above_max, abs_d_below_min |
| raw05_recross60_abs085 | KXBTC15M-26MAY062345-45 | rejected_actionable | yes | 67.000000 | 0.298111 | 0.639973 | 0.214573 | 0.300000 | recross_above_max, abs_d_below_min |
| raw05_recross60_abs085_ask65 | KXBTC15M-26MAY070615-15 | rejected_actionable | yes | -2.000000 | 0.568996 | 0.142600 | 0.170925 | 0.010000 | abs_d_below_min, ask_below_min |
| raw05_recross60_abs085_ask65 | KXBTC15M-26MAY062330-30 | rejected_actionable | yes | -5.000000 | 0.514636 | 0.307484 | 0.121467 | 0.040000 | abs_d_below_min, ask_below_min |
| raw05_recross60_abs085_ask65 | KXBTC15M-26MAY070630-30 | rejected_actionable | yes | -6.000000 | 0.474276 | 0.335538 | 0.025583 | 0.050000 | abs_d_below_min, ask_below_min |
| raw05_recross60_abs085_ask65 | KXBTC15M-26MAY070700-00 | rejected_actionable | yes | -28.000000 | 0.445361 | 0.421130 | 0.477812 | 0.250000 | abs_d_below_min, ask_below_min |
| raw05_recross60_abs085_ask65 | KXBTC15M-26MAY061700-00 | rejected_actionable | no | -42.000000 | 0.408347 | 0.196391 | 0.665443 | 0.380000 | abs_d_below_min, ask_below_min |
| raw05_recross60_abs085_ask65 | KXBTC15M-26MAY061745-45 | rejected_actionable | no | -16.000000 | 0.370383 | 0.689790 | 0.021042 | 0.140000 | recross_above_max, abs_d_below_min, ask_below_min |
| raw05_recross60_abs085_ask65 | KXBTC15M-26MAY061945-45 | rejected_actionable | no | 51.000000 | 0.348947 | 0.396347 | 0.680058 | 0.450000 | abs_d_below_min, ask_below_min |
| raw05_recross60_abs085_ask65 | KXBTC15M-26MAY062230-30 | rejected_actionable | yes | -42.000000 | 0.338015 | 0.349672 | 0.481781 | 0.380000 | abs_d_below_min, ask_below_min |
| raw05_recross60_abs085_ask65 | KXBTC15M-26MAY070800-00 | rejected_actionable | yes | -12.000000 | 0.329038 | 0.628964 | 0.163026 | 0.100000 | recross_above_max, abs_d_below_min, ask_below_min |
| raw05_recross60_abs085_ask65 | KXBTC15M-26MAY061500-00 | rejected_actionable | yes | -13.000000 | 0.316725 | 0.094209 | 0.183718 | 0.110000 | abs_d_below_min, ask_below_min |
| raw05_recross60_abs085_ask65 | KXBTC15M-26MAY061930-30 | rejected_actionable | no | -28.000000 | 0.301840 | 0.688823 | 0.118494 | 0.250000 | recross_above_max, abs_d_below_min, ask_below_min |
| raw05_recross60_abs085_ask65 | KXBTC15M-26MAY062345-45 | rejected_actionable | yes | 67.000000 | 0.298111 | 0.639973 | 0.214573 | 0.300000 | recross_above_max, abs_d_below_min, ask_below_min |
| raw03_recross70_abs075 | KXBTC15M-26MAY062330-30 | rejected_actionable | yes | -5.000000 | 0.514636 | 0.307484 | 0.121467 | 0.040000 | abs_d_below_min |
| raw03_recross70_abs075 | KXBTC15M-26MAY070630-30 | rejected_actionable | yes | -6.000000 | 0.474276 | 0.335538 | 0.025583 | 0.050000 | abs_d_below_min |
| raw03_recross70_abs075 | KXBTC15M-26MAY070700-00 | rejected_actionable | yes | -28.000000 | 0.445361 | 0.421130 | 0.477812 | 0.250000 | abs_d_below_min |
| raw03_recross70_abs075 | KXBTC15M-26MAY061700-00 | rejected_actionable | no | -42.000000 | 0.408347 | 0.196391 | 0.665443 | 0.380000 | abs_d_below_min |
| raw03_recross70_abs075 | KXBTC15M-26MAY061745-45 | rejected_actionable | no | -16.000000 | 0.370383 | 0.689790 | 0.021042 | 0.140000 | abs_d_below_min |
| raw03_recross70_abs075 | KXBTC15M-26MAY061945-45 | rejected_actionable | no | 51.000000 | 0.348947 | 0.396347 | 0.680058 | 0.450000 | abs_d_below_min |
| raw03_recross70_abs075 | KXBTC15M-26MAY062230-30 | rejected_actionable | yes | -42.000000 | 0.338015 | 0.349672 | 0.481781 | 0.380000 | abs_d_below_min |
| raw03_recross70_abs075 | KXBTC15M-26MAY070800-00 | rejected_actionable | yes | -12.000000 | 0.329038 | 0.628964 | 0.163026 | 0.100000 | abs_d_below_min |
| raw03_recross70_abs075 | KXBTC15M-26MAY061500-00 | rejected_actionable | yes | -13.000000 | 0.316725 | 0.094209 | 0.183718 | 0.110000 | abs_d_below_min |
| raw03_recross70_abs075 | KXBTC15M-26MAY070100-00 | rejected_actionable | no | -25.000000 | 0.285013 | 0.647900 | 0.032616 | 0.220000 | abs_d_below_min |
| raw03_recross70_abs075 | KXBTC15M-26MAY062000-00 | rejected_actionable | yes | 48.000000 | 0.259489 | 0.419801 | 0.552158 | 0.480000 | abs_d_below_min |
| raw03_recross70_abs075 | KXBTC15M-26MAY061715-15 | rejected_actionable | yes | -2.000000 | 0.250844 | 0.072090 | 0.552786 | 0.010000 | abs_d_below_min |
