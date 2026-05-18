# Paired Sidecar Online Calibration Diagnostic

Research-only diagnostic for label-gated online logit calibration of paired live-shadow sidecar rows.

## Summary

- Generated UTC: `2026-05-18T18:29:52.736002+00:00`
- Promotion allowed: `False`
- Prepared rows / input rows: `1410` / `1410`
- Input markets: `68`
- Issue count: `0`
- Best model by Brier: `v28`
- Best model by log loss: `blend_market_online_lr010_w05`
- Market-equal best model by Brier: `blend_v28_online_lr010_w15`
- Market-equal best model by log loss: `blend_market_online_lr010_w15`
- Raw candidate Brier / log loss: `0.27354961096998787` / `0.9144251002683972`
- Best calibrated Brier / log loss: `0.25797783001865826` / `0.7471244041728579`
- Raw / best calibrated top-EV bucket PnL: `-431.7` / `1988.9`
- Best calibrated model: `online_logit_candidate_lr003_row`
- Market stability count: `68`
- Raw / best calibrated positive market top-EV counts: `13` / `22`
- Best calibrated positive market selected-PnL count: `28`
- Best blend by market-equal Brier: `blend_v28_online_lr010_w15` / `0.21300474327155275`
- Best blend positive market top-EV / selected-PnL counts: `31` / `33`
- Conclusion: Label-gated online calibration improves raw candidate Brier/log-loss and has a positive top-EV bucket, but this remains retrospective research-only evidence until predeclared forward shadow passes.

## Row-Weighted Model Rows

| model | rows | markets | brier | logloss | selected | selected pnl | top bucket pnl |
|---|---:|---:|---:|---:|---:|---:|---:|
| `candidate_raw` | 1410 | 68 | 0.27354961096998787 | 0.9144251002683972 | 683 | 2108.1 | -431.7 |
| `v28` | 1410 | 68 | 0.21048805396487674 | 0.6199110108478341 | 658 | 4906.0 | 39.7 |
| `candle_brownian` | 1410 | 68 | 0.2160451395784026 | 0.6191320592106702 | 679 | 85.00000000000001 | 3393.4 |
| `tick_brownian` | 1410 | 68 | 0.21554355231562697 | 0.6181561569454457 | 679 | -788.0 | 2649.4 |
| `market_side_ask` | 1410 | 68 | 0.21136906950354611 | 0.605671800393208 | 199 | 1758.6000000000001 | 1758.6000000000001 |
| `online_logit_candidate_lr003_row` | 1410 | 68 | 0.25797783001865826 | 0.7471244041728579 | 692 | 1998.8 | -957.5 |
| `online_logit_candidate_lr010_row` | 1410 | 68 | 0.2591190047778481 | 0.7319062198952868 | 699 | 1172.6 | 181.4 |
| `online_logit_candidate_lr030_row` | 1410 | 68 | 0.2733133570358219 | 0.7775779661315305 | 701 | 2484.0 | 1988.9 |
| `online_logit_candidate_lr003_market_mean` | 1410 | 68 | 0.27353383485716004 | 0.9129973019061505 | 686 | 2081.2 | -427.7 |
| `online_logit_candidate_lr010_market_mean` | 1410 | 68 | 0.2735598815608939 | 0.9101285397616832 | 697 | 1523.1999999999998 | -366.7 |
| `online_logit_candidate_lr030_market_mean` | 1410 | 68 | 0.2739263426544053 | 0.9044006304931088 | 708 | 1475.3999999999999 | -541.0 |
| `blend_v28_online_lr010_w05` | 1410 | 68 | 0.2105403657489877 | 0.6162548074313745 | 662 | 4545.1 | 751.7 |
| `blend_market_online_lr010_w05` | 1410 | 68 | 0.21108100577168204 | 0.6055606828117327 | 699 | 1172.6 | 181.4 |
| `blend_v28_online_lr010_w10` | 1410 | 68 | 0.21084312340220793 | 0.6145380388818289 | 661 | 3741.4 | 595.7 |
| `blend_market_online_lr010_w10` | 1410 | 68 | 0.21107457998672108 | 0.6061153499322454 | 699 | 1172.6 | 181.4 |
| `blend_v28_online_lr010_w15` | 1410 | 68 | 0.21139632692453736 | 0.6141335675721924 | 651 | 3820.8 | 1380.7 |
| `blend_market_online_lr010_w15` | 1410 | 68 | 0.21134979214866317 | 0.6072829821699728 | 699 | 1172.6 | 181.4 |
| `blend_v28_online_lr010_w20` | 1410 | 68 | 0.21219997631597598 | 0.6147392196784486 | 661 | 4754.8 | 1296.7 |
| `blend_market_online_lr010_w20` | 1410 | 68 | 0.21190664225750835 | 0.6090282744006413 | 699 | 1172.6 | 181.4 |
| `blend_v28_online_lr010_w25` | 1410 | 68 | 0.21325407157652385 | 0.6161835266299648 | 666 | 4059.8 | 781.1 |
| `blend_market_online_lr010_w25` | 1410 | 68 | 0.21274513031325656 | 0.6113279686351121 | 699 | 1172.6 | 181.4 |

## Market-Equal Model Rows

| model | rows | markets | brier | logloss | selected | selected pnl | top bucket pnl |
|---|---:|---:|---:|---:|---:|---:|---:|
| `candidate_raw` | 1410 | 68 | 0.2706223564961122 | 0.8993564261101521 | 683 | 31.001470588235293 | -12.907352941176471 |
| `v28` | 1410 | 68 | 0.21412279521139604 | 0.6297893532933623 | 658 | 72.1470588235294 | 31.852941176470587 |
| `candle_brownian` | 1410 | 68 | 0.2153620230165443 | 0.6163186384833135 | 679 | 1.25 | 8.361764705882353 |
| `tick_brownian` | 1410 | 68 | 0.21463162743097236 | 0.6148854684563698 | 679 | -11.588235294117647 | 2.6558823529411764 |
| `market_side_ask` | 1410 | 68 | 0.21539175612745098 | 0.6144491089783476 | 199 | 25.861764705882354 | 13.539705882352942 |
| `online_logit_candidate_lr003_row` | 1410 | 68 | 0.25165284716659153 | 0.7184594138745747 | 692 | 29.394117647058824 | 5.179411764705883 |
| `online_logit_candidate_lr010_row` | 1410 | 68 | 0.24766705885025828 | 0.7000905738174454 | 699 | 17.24411764705882 | 6.635294117647058 |
| `online_logit_candidate_lr030_row` | 1410 | 68 | 0.256865650871896 | 0.732588488348121 | 701 | 36.529411764705884 | 31.125 |
| `online_logit_candidate_lr003_market_mean` | 1410 | 68 | 0.2705907546787766 | 0.8977009922495389 | 686 | 30.605882352941173 | -13.975000000000001 |
| `online_logit_candidate_lr010_market_mean` | 1410 | 68 | 0.2705879992331638 | 0.894344036954182 | 697 | 22.4 | -12.09264705882353 |
| `online_logit_candidate_lr030_market_mean` | 1410 | 68 | 0.27090629542933947 | 0.8875703286914094 | 708 | 21.69705882352941 | -7.84264705882353 |
| `blend_v28_online_lr010_w05` | 1410 | 68 | 0.21350894685946112 | 0.6238844006942595 | 662 | 66.83970588235294 | 25.248529411764704 |
| `blend_market_online_lr010_w05` | 1410 | 68 | 0.2146047673819055 | 0.6128586898021056 | 699 | 17.24411764705882 | 6.635294117647058 |
| `blend_v28_online_lr010_w10` | 1410 | 68 | 0.21313626287951337 | 0.6201571464900407 | 661 | 55.02058823529412 | 19.599999999999998 |
| `blend_market_online_lr010_w10` | 1410 | 68 | 0.21407048957127436 | 0.6119402758694565 | 699 | 17.24411764705882 | 6.635294117647058 |
| `blend_v28_online_lr010_w15` | 1410 | 68 | 0.21300474327155275 | 0.6178817127924487 | 651 | 56.188235294117646 | 19.355882352941176 |
| `blend_market_online_lr010_w15` | 1410 | 68 | 0.2137889226955575 | 0.6116323150056906 | 699 | 17.24411764705882 | 6.635294117647058 |
| `blend_v28_online_lr010_w20` | 1410 | 68 | 0.21311438803557933 | 0.616706114762713 | 661 | 69.9235294117647 | 31.120588235294115 |
| `blend_market_online_lr010_w20` | 1410 | 68 | 0.21376006675475492 | 0.6118923408547399 | 699 | 17.24411764705882 | 6.635294117647058 |
| `blend_v28_online_lr010_w25` | 1410 | 68 | 0.21346519717159304 | 0.6164283949142487 | 666 | 59.70294117647059 | 31.620588235294115 |
| `blend_market_online_lr010_w25` | 1410 | 68 | 0.21398392174886663 | 0.6126907188093982 | 699 | 17.24411764705882 | 6.635294117647058 |

## Read

- Calibrator updates are delayed until each source capture's market close timestamp.
- `market_mean` specs update once per settled market, avoiding repeated same-market row overweighting.
- This file is not a promotion artifact; it is a research diagnostic for the probability-calibration layer.
