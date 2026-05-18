# v28 Exit Branch Diagnostic

Forward-only diagnostic. It compares actual exited P&L against holding the same filled position to settlement.

- Exits: `145`
- Resolved exits: `145`
- Actual exited P&L: `$-0.93`
- Comparable hold P&L: `$13.88`
- Exit value vs hold: `$-14.81`
- Winner clipped count: `117`
- Loss saved count: `25`
- Unresolved exits: `0`

## Branches

| branch | exits | resolved | actual c | hold c | exit value c | winner clipped | loss saved | unresolved | buckets |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| mushroom_v28_exit_value_over_hold | 77 | 77 | 1322.0 | 1584.0 | -262.0 | 67 | 7 | 0 | loss_saved:7,winner_clipped:67,winner_not_clipped:3 |
| mushroom_v28_probability_collapse_full | 26 | 26 | -946.0 | -690.0 | -256.0 | 15 | 11 | 0 | loss_saved:11,winner_clipped:15 |
| mushroom_v28_probability_reduce | 42 | 42 | -469.0 | 494.0 | -963.0 | 35 | 7 | 0 | loss_saved:7,winner_clipped:35 |

## Exit Rows

| market | side | entry | exit | result | actual c | hold c | exit value c | bucket | p_hold | fair drawdown | sigma |
|---|---|---:|---:|---|---:|---:|---:|---|---:|---:|---:|
| KXBTC15M-26MAY051300-00 | yes | 81 | 99 | yes | 36 | 38 | -2 | winner_clipped | 0.980404 | -17.040444 | 92.835513 |
| KXBTC15M-26MAY051330-30 | yes | 82 | 82 | yes | 0 | 36 | -36 | winner_clipped | 0.784419 | 3.558143 | 86.011363 |
| KXBTC15M-26MAY051545-45 | yes | 75 | 83 | yes | 16 | 50 | -34 | winner_clipped | 0.811651 | -6.165133 | 104.22086 |
| KXBTC15M-26MAY051615-15 | no | 76 | 64 | yes | -24 | -152 | 128 | loss_saved | 0.698446 | 6.155389 | 88.121911 |
| KXBTC15M-26MAY051615-15 | yes | 56 | 72 | yes | 32 | 88 | -56 | winner_clipped | 0.784724 | -22.47242 | 81.327361 |
| KXBTC15M-26MAY051715-15 | yes | 82 | 68 | no | -28 | -164 | 136 | loss_saved | 0.72802 | 9.198017 | 98.360062 |
| KXBTC15M-26MAY051715-15 | yes | 69 | 45 | no | -48 | -138 | 90 | loss_saved | 0.552818 | 13.718206 | 41.179918 |
| KXBTC15M-26MAY051715-15 | yes | 40 | 29 | no | -22 | -80 | 58 | loss_saved | 0.35183 | 4.816989 | 33.916848 |
| KXBTC15M-26MAY051745-45 | no | 77 | 72 | no | -10 | 46 | -56 | winner_clipped | 0.791105 | -2.11055 | 101.587041 |
| KXBTC15M-26MAY051745-45 | no | 80 | 79 | no | -2 | 40 | -42 | winner_clipped | 0.754469 | 9.553119 | 73.666114 |
| KXBTC15M-26MAY051800-00 | yes | 78 | 66 | yes | -24 | 44 | -68 | winner_clipped | 0.729502 | 5.049756 | 92.447801 |
| KXBTC15M-26MAY051800-00 | yes | 80 | 100 | yes | 40 | 40 | 0 | winner_not_clipped | 0.991914 | -19.191381 | 54.768906 |
| KXBTC15M-26MAY051815-15 | yes | 81 | 93 | no | 24 | -162 | 186 | loss_saved | 0.922242 | -9.224209 | 83.937761 |
| KXBTC15M-26MAY051830-30 | no | 80 | 34 | yes | -92 | -160 | 68 | loss_saved | 0.453866 | 34.613447 | 60.775686 |
| KXBTC15M-26MAY051915-15 | yes | 82 | 99 | yes | 34 | 36 | -2 | winner_clipped | 0.968105 | -14.810535 | 51.207207 |
| KXBTC15M-26MAY051945-45 | yes | 74 | 87 | yes | 26 | 52 | -26 | winner_clipped | 0.837318 | -9.731795 | 36.450294 |
| KXBTC15M-26MAY052045-45 | yes | 79 | 70 | no | -18 | -158 | 140 | loss_saved | 0.65091 | 15.909026 | 51.444097 |
| KXBTC15M-26MAY052045-45 | yes | 83 | 90 | no | 14 | -166 | 180 | loss_saved | 0.8407 | -1.070049 | 38.052176 |
| KXBTC15M-26MAY052100-00 | no | 79 | 64 | yes | -30 | -158 | 128 | loss_saved | 0.709559 | 8.044127 | 95.357563 |
| KXBTC15M-26MAY052100-00 | yes | 56 | 73 | yes | 34 | 88 | -54 | winner_clipped | 0.551181 | 0.881937 | 81.014353 |
| KXBTC15M-26MAY052100-00 | yes | 90 | 96 | yes | 12 | 20 | -8 | winner_clipped | 0.948823 | -4.882288 | 49.209482 |
| KXBTC15M-26MAY052145-45 | yes | 85 | 95 | yes | 20 | 30 | -10 | winner_clipped | 0.901383 | -7.138269 | 56.616925 |
| KXBTC15M-26MAY052200-00 | yes | 79 | 85 | yes | 12 | 42 | -30 | winner_clipped | 0.827933 | -3.793285 | 99.794187 |
| KXBTC15M-26MAY052215-15 | no | 83 | 76 | no | -14 | 34 | -48 | winner_clipped | 0.710513 | 11.948693 | 118.706767 |
| KXBTC15M-26MAY052245-45 | no | 40 | 27 | yes | -26 | -80 | 54 | loss_saved | 0.430723 | -3.072314 | 65.494307 |
| KXBTC15M-26MAY052300-00 | yes | 85 | 99 | yes | 28 | 30 | -2 | winner_clipped | 0.819882 | 3.011763 | 56.975408 |
| KXBTC15M-26MAY052315-15 | yes | 81 | 62 | yes | -38 | 38 | -76 | winner_clipped | 0.676259 | 13.37412 | 74.399364 |
| KXBTC15M-26MAY060045-45 | no | 79 | 74 | no | -10 | 42 | -52 | winner_clipped | 0.794727 | -0.472669 | 79.739194 |
| KXBTC15M-26MAY060045-45 | no | 85 | 95 | no | 20 | 30 | -10 | winner_clipped | 0.939879 | -8.987878 | 61.638236 |
| KXBTC15M-26MAY060100-00 | no | 78 | 76 | no | -4 | 44 | -48 | winner_clipped | 0.794947 | -1.494734 | 72.290768 |
| KXBTC15M-26MAY060145-45 | no | 88 | 99 | no | 22 | 24 | -2 | winner_clipped | 0.981135 | -10.113544 | 37.950327 |
| KXBTC15M-26MAY060200-00 | yes | 80 | 74 | yes | -12 | 40 | -52 | winner_clipped | 0.773728 | 2.627248 | 89.76735 |
| KXBTC15M-26MAY060200-00 | yes | 81 | 84 | yes | 6 | 38 | -32 | winner_clipped | 0.826858 | -0.685826 | 72.22618 |
| KXBTC15M-26MAY060215-15 | yes | 77 | 69 | no | -16 | -154 | 138 | loss_saved | 0.716457 | 5.354325 | 95.052944 |
| KXBTC15M-26MAY060215-15 | yes | 83 | 70 | no | -26 | -166 | 140 | loss_saved | 0.744634 | 8.53658 | 75.400334 |
| KXBTC15M-26MAY060215-15 | no | 80 | 97 | no | 34 | 40 | -6 | winner_clipped | 0.943338 | -14.333771 | 42.365922 |
| KXBTC15M-26MAY060230-30 | yes | 84 | 74 | yes | -20 | 32 | -52 | winner_clipped | 0.742942 | 9.705807 | 54.001257 |
| KXBTC15M-26MAY060245-45 | yes | 80 | 76 | yes | -8 | 40 | -48 | winner_clipped | 0.793334 | 2.666578 | 54.429671 |
| KXBTC15M-26MAY060245-45 | yes | 77 | 74 | yes | -6 | 46 | -52 | winner_clipped | 0.749392 | 2.06075 | 38.309815 |
| KXBTC15M-26MAY060245-45 | yes | 76 | 95 | yes | 38 | 48 | -10 | winner_clipped | 0.941979 | -18.197939 | 32.504394 |
| KXBTC15M-26MAY060300-00 | yes | 81 | 74 | yes | -14 | 38 | -52 | winner_clipped | 0.780402 | 2.95982 | 75.781532 |
| KXBTC15M-26MAY060300-00 | yes | 81 | 66 | yes | -30 | 38 | -68 | winner_clipped | 0.718799 | 9.120058 | 56.633388 |
| KXBTC15M-26MAY060300-00 | yes | 80 | 69 | yes | -22 | 40 | -62 | winner_clipped | 0.753164 | 4.683642 | 47.661178 |
| KXBTC15M-26MAY060300-00 | yes | 80 | 94 | yes | 28 | 40 | -12 | winner_clipped | 0.931555 | -13.155529 | 38.912899 |
| KXBTC15M-26MAY060315-15 | yes | 86 | 99 | yes | 26 | 28 | -2 | winner_clipped | 0.975084 | -11.508394 | 28.515873 |
| KXBTC15M-26MAY060330-30 | yes | 79 | 53 | yes | -52 | 42 | -94 | winner_clipped | 0.500862 | 28.913827 | 61.03679 |
| KXBTC15M-26MAY060345-45 | no | 78 | 95 | no | 34 | 44 | -10 | winner_clipped | 0.940325 | -16.032531 | 57.404629 |
| KXBTC15M-26MAY060445-45 | yes | 90 | 99 | yes | 18 | 20 | -2 | winner_clipped | 0.980285 | -8.028473 | 48.690524 |
| KXBTC15M-26MAY060515-15 | no | 79 | 66 | no | -26 | 42 | -68 | winner_clipped | 0.669735 | 16.026514 | 90.806669 |
| KXBTC15M-26MAY060515-15 | no | 74 | 95 | no | 42 | 52 | -10 | winner_clipped | 0.769032 | -2.90319 | 40.750631 |
| KXBTC15M-26MAY060530-30 | no | 78 | 95 | no | 34 | 44 | -10 | winner_clipped | 0.899953 | -11.995311 | 80.69081 |
| KXBTC15M-26MAY060600-00 | no | 75 | 81 | no | 12 | 50 | -38 | winner_clipped | 0.804105 | 1.589476 | 84.302961 |
| KXBTC15M-26MAY060615-15 | yes | 75 | 60 | yes | -30 | 50 | -80 | winner_clipped | 0.643484 | 10.651569 | 93.498873 |
| KXBTC15M-26MAY060630-30 | yes | 79 | 73 | yes | -12 | 42 | -54 | winner_clipped | 0.777774 | 1.222639 | 82.308304 |
| KXBTC15M-26MAY060630-30 | yes | 85 | 99 | yes | 28 | 30 | -2 | winner_clipped | 0.978151 | -12.815129 | 34.61806 |
| KXBTC15M-26MAY060645-45 | yes | 82 | 74 | yes | -16 | 36 | -52 | winner_clipped | 0.799349 | 2.065125 | 94.132945 |
| KXBTC15M-26MAY060645-45 | yes | 78 | 72 | yes | -12 | 44 | -56 | winner_clipped | 0.779789 | 0.021114 | 85.127577 |
| KXBTC15M-26MAY060645-45 | yes | 80 | 97 | yes | 34 | 40 | -6 | winner_clipped | 0.962354 | -16.235382 | 52.664491 |
| KXBTC15M-26MAY060700-00 | no | 84 | 80 | yes | -8 | -168 | 160 | loss_saved | 0.799603 | 4.039746 | 88.671268 |
| KXBTC15M-26MAY060700-00 | yes | 75 | 64 | yes | -22 | 50 | -72 | winner_clipped | 0.748579 | 0.142079 | 66.807671 |
| KXBTC15M-26MAY060700-00 | yes | 77 | 62 | yes | -30 | 46 | -76 | winner_clipped | 0.674479 | 9.552131 | 54.161741 |
| KXBTC15M-26MAY060700-00 | yes | 83 | 89 | yes | 12 | 34 | -22 | winner_clipped | 0.743339 | 8.666129 | 35.299607 |
| KXBTC15M-26MAY060715-15 | yes | 81 | 93 | yes | 24 | 38 | -14 | winner_clipped | 0.920907 | -11.09069 | 97.422366 |
| KXBTC15M-26MAY060715-15 | yes | 89 | 99 | yes | 20 | 22 | -2 | winner_clipped | 0.984061 | -8.406103 | 43.995187 |
| KXBTC15M-26MAY060745-45 | yes | 69 | 57 | no | -24 | -138 | 114 | loss_saved | 0.610349 | 7.965096 | 94.966015 |
| KXBTC15M-26MAY060745-45 | yes | 78 | 43 | no | -70 | -156 | 86 | loss_saved | 0.563569 | 21.643115 | 70.152311 |
| KXBTC15M-26MAY060800-00 | yes | 79 | 70 | yes | -18 | 42 | -60 | winner_clipped | 0.738185 | 5.181496 | 65.147535 |
| KXBTC15M-26MAY060800-00 | yes | 66 | 50 | yes | -32 | 68 | -100 | winner_clipped | 0.614703 | 4.529724 | 60.441055 |
| KXBTC15M-26MAY060830-30 | yes | 76 | 100 | yes | 48 | 48 | 0 | winner_not_clipped | 0.992185 | -23.218487 | 41.985539 |
| KXBTC15M-26MAY060900-00 | yes | 78 | 73 | no | -10 | -156 | 146 | loss_saved | 0.78999 | -0.998969 | 107.89274 |
| KXBTC15M-26MAY060900-00 | yes | 78 | 40 | no | -76 | -156 | 80 | loss_saved | 0.39732 | 41.268037 | 69.053628 |
| KXBTC15M-26MAY060900-00 | no | 73 | 65 | no | -16 | 54 | -70 | winner_clipped | 0.721102 | 0.88976 | 62.589641 |
| KXBTC15M-26MAY060900-00 | no | 79 | 96 | no | 34 | 42 | -8 | winner_clipped | 0.948348 | -15.834839 | 49.909191 |
| KXBTC15M-26MAY060915-15 | no | 70 | 70 | no | 0 | 60 | -60 | winner_clipped | 0.793762 | -9.376204 | 125.230299 |
| KXBTC15M-26MAY060915-15 | no | 75 | 100 | no | 50 | 50 | 0 | winner_not_clipped | 0.994245 | -17.424453 | 46.792069 |
| KXBTC15M-26MAY060930-30 | no | 76 | 66 | no | -20 | 48 | -68 | winner_clipped | 0.725946 | 3.405368 | 124.243609 |
| KXBTC15M-26MAY060930-30 | no | 76 | 69 | no | -14 | 48 | -62 | winner_clipped | 0.787606 | -2.760587 | 117.143469 |
| KXBTC15M-26MAY060930-30 | no | 73 | 72 | no | -3 | 54 | -57 | winner_clipped | 0.79918 | -6.91797 | 110.113616 |
| KXBTC15M-26MAY060945-45 | no | 59 | 51 | no | -16 | 82 | -98 | winner_clipped | 0.556556 | 3.344394 | 147.510554 |
| KXBTC15M-26MAY060945-45 | no | 70 | 62 | no | -16 | 60 | -76 | winner_clipped | 0.689159 | 1.084126 | 93.055121 |
| KXBTC15M-26MAY060945-45 | no | 71 | 65 | no | -12 | 58 | -70 | winner_clipped | 0.735773 | -2.577325 | 84.109368 |
| KXBTC15M-26MAY060945-45 | no | 72 | 96 | no | 48 | 56 | -8 | winner_clipped | 0.950787 | -23.078686 | 45.06315 |
| KXBTC15M-26MAY061015-15 | no | 68 | 65 | no | -6 | 64 | -70 | winner_clipped | 0.733426 | -5.34261 | 151.411668 |
| KXBTC15M-26MAY061015-15 | no | 70 | 70 | no | 0 | 60 | -60 | winner_clipped | 0.799979 | -9.997858 | 137.842477 |
| KXBTC15M-26MAY061030-30 | yes | 78 | 70 | yes | -16 | 44 | -60 | winner_clipped | 0.752739 | 2.726149 | 125.184173 |
| KXBTC15M-26MAY061030-30 | yes | 78 | 73 | yes | -10 | 44 | -54 | winner_clipped | 0.796458 | -1.645773 | 119.347449 |
| KXBTC15M-26MAY061045-45 | yes | 80 | 77 | yes | -6 | 40 | -46 | winner_clipped | 0.796949 | 0.305083 | 128.62317 |
| KXBTC15M-26MAY061045-45 | yes | 84 | 98 | yes | 28 | 32 | -4 | winner_clipped | 0.975987 | -13.598681 | 56.543772 |
| KXBTC15M-26MAY061100-00 | no | 83 | 63 | no | -40 | 34 | -74 | winner_clipped | 0.704126 | 12.587383 | 134.068939 |
| KXBTC15M-26MAY061200-00 | yes | 82 | 90 | yes | 16 | 36 | -20 | winner_clipped | 0.889296 | -7.929607 | 120.920742 |
| KXBTC15M-26MAY061300-00 | yes | 80 | 65 | no | -30 | -160 | 130 | loss_saved | 0.66643 | 13.356971 | 101.007081 |
| KXBTC15M-26MAY061400-00 | no | 89 | 84 | no | -10 | 22 | -32 | winner_clipped | 0.737977 | 15.202342 | 62.144844 |
| KXBTC15M-26MAY061445-45 | no | 88 | 77 | no | -22 | 24 | -46 | winner_clipped | 0.79783 | 8.216985 | 119.451977 |
| KXBTC15M-26MAY061445-45 | no | 90 | 99 | no | 18 | 20 | -2 | winner_clipped | 0.981991 | -8.199066 | 78.030873 |
| KXBTC15M-26MAY061545-45 | yes | 84 | 95 | yes | 22 | 32 | -10 | winner_clipped | 0.93541 | -9.540987 | 68.416747 |
| KXBTC15M-26MAY061615-15 | yes | 90 | 94 | yes | 8 | 20 | -12 | winner_clipped | 0.931218 | -3.121769 | 81.048511 |
| KXBTC15M-26MAY061800-00 | no | 67 | 24 | no | -86 | 66 | -152 | winner_clipped | 0.552607 | 11.739327 | 63.823324 |
| KXBTC15M-26MAY061815-15 | no | 84 | 96 | no | 24 | 32 | -8 | winner_clipped | 0.950684 | -11.068394 | 69.922793 |
| KXBTC15M-26MAY061830-30 | no | 89 | 99 | no | 20 | 22 | -2 | winner_clipped | 0.976718 | -8.671753 | 41.869598 |
| KXBTC15M-26MAY061915-15 | no | 87 | 99 | no | 24 | 26 | -2 | winner_clipped | 0.981987 | -11.198704 | 40.165658 |
| KXBTC15M-26MAY062015-15 | no | 42 | 12 | no | -60 | 116 | -176 | winner_clipped | 0.268932 | 15.106811 | 39.232844 |
| KXBTC15M-26MAY062015-15 | yes | 86 | 90 | no | 8 | -172 | 180 | loss_saved | 0.812359 | 4.764109 | 35.604988 |
| KXBTC15M-26MAY062030-30 | no | 67 | 83 | no | 32 | 66 | -34 | winner_clipped | 0.661475 | 0.852486 | 67.865845 |
| KXBTC15M-26MAY062045-45 | no | 80 | 92 | no | 24 | 40 | -16 | winner_clipped | 0.891386 | -9.138584 | 66.200789 |
| KXBTC15M-26MAY062100-00 | yes | 83 | 81 | yes | -4 | 34 | -38 | winner_clipped | 0.647591 | 18.240924 | 81.116041 |
| KXBTC15M-26MAY062100-00 | yes | 84 | 74 | yes | -20 | 32 | -52 | winner_clipped | 0.663692 | 17.63084 | 69.571991 |
| KXBTC15M-26MAY062100-00 | yes | 61 | 68 | yes | 14 | 78 | -64 | winner_clipped | 0.489234 | 12.076646 | 59.428499 |
| KXBTC15M-26MAY062115-15 | yes | 73 | 67 | yes | -12 | 54 | -66 | winner_clipped | 0.39575 | 33.425046 | 92.177359 |
| KXBTC15M-26MAY062115-15 | no | 69 | 52 | yes | -34 | -138 | 104 | loss_saved | 0.455777 | 14.422271 | 70.290722 |
| KXBTC15M-26MAY062115-15 | yes | 88 | 99 | yes | 22 | 24 | -2 | winner_clipped | 0.982461 | -10.246054 | 35.918348 |
| KXBTC15M-26MAY062130-30 | no | 76 | 60 | yes | -32 | -152 | 120 | loss_saved | 0.768407 | 6.159273 | 76.542004 |
| KXBTC15M-26MAY062215-15 | no | 65 | 72 | no | 14 | 70 | -56 | winner_clipped | 0.708248 | -5.824841 | 94.367362 |
| KXBTC15M-26MAY062215-15 | no | 84 | 89 | no | 10 | 32 | -22 | winner_clipped | 0.860673 | -2.067333 | 71.161296 |
| KXBTC15M-26MAY062245-45 | yes | 86 | 90 | yes | 8 | 28 | -20 | winner_clipped | 0.643812 | 15.618779 | 75.33736 |
| KXBTC15M-26MAY062300-00 | yes | 87 | 95 | yes | 16 | 26 | -10 | winner_clipped | 0.746374 | 10.362646 | 79.984282 |
| KXBTC15M-26MAY062315-15 | no | 84 | 87 | no | 6 | 32 | -26 | winner_clipped | 0.811182 | 2.881757 | 78.884361 |
| KXBTC15M-26MAY070000-00 | no | 78 | 79 | no | 2 | 44 | -42 | winner_clipped | 0.726702 | 5.329808 | 67.559729 |
| KXBTC15M-26MAY070015-15 | no | 70 | 69 | yes | -2 | -140 | 138 | loss_saved | 0.596562 | 10.343815 | 55.036148 |
| KXBTC15M-26MAY070030-30 | yes | 82 | 97 | yes | 30 | 36 | -6 | winner_clipped | 0.921778 | -10.177771 | 58.846319 |
| KXBTC15M-26MAY070115-15 | yes | 82 | 82 | yes | 0 | 36 | -36 | winner_clipped | 0.679619 | 18.038087 | 76.079815 |
| KXBTC15M-26MAY070545-45 | no | 82 | 91 | no | 18 | 36 | -18 | winner_clipped | 0.892567 | -7.256748 | 52.967613 |
| KXBTC15M-26MAY070745-45 | yes | 68 | 85 | yes | 34 | 64 | -30 | winner_clipped | 0.821701 | -14.170103 | 69.306307 |
| KXBTC15M-26MAY070815-15 | yes | 90 | 91 | yes | 2 | 20 | -18 | winner_clipped | 0.890464 | -1.046434 | 73.725947 |
| KXBTC15M-26MAY070830-30 | no | 82 | 91 | no | 18 | 36 | -18 | winner_clipped | 0.825354 | -0.535395 | 72.882276 |
| KXBTC15M-26MAY070830-30 | no | 77 | 70 | no | -14 | 46 | -60 | winner_clipped | 0.612998 | 15.700151 | 56.927146 |
| KXBTC15M-26MAY070930-30 | yes | 80 | 97 | yes | 34 | 40 | -6 | winner_clipped | 0.969995 | -13.999536 | 68.413047 |
| KXBTC15M-26MAY071000-00 | no | 73 | 55 | no | -36 | 54 | -90 | winner_clipped | 0.617577 | 11.2423 | 128.299466 |
| KXBTC15M-26MAY071000-00 | no | 71 | 79 | no | 16 | 58 | -42 | winner_clipped | 0.781361 | 6.863933 | 69.298788 |
| KXBTC15M-26MAY071015-15 | no | 78 | 79 | yes | 2 | -156 | 158 | loss_saved | 0.78913 | -0.913001 | 127.362008 |
| KXBTC15M-26MAY071015-15 | no | 81 | 73 | yes | -16 | -162 | 146 | loss_saved | 0.76398 | 4.602013 | 123.755074 |
| KXBTC15M-26MAY071015-15 | yes | 84 | 94 | yes | 20 | 32 | -12 | winner_clipped | 0.923102 | -8.310249 | 69.876743 |
| KXBTC15M-26MAY071030-30 | no | 77 | 65 | no | -24 | 46 | -70 | winner_clipped | 0.709831 | 6.016933 | 154.25932 |
| KXBTC15M-26MAY071045-45 | no | 74 | 69 | no | -10 | 52 | -62 | winner_clipped | 0.760529 | -2.052947 | 137.45498 |
| KXBTC15M-26MAY071100-00 | yes | 83 | 85 | no | 4 | -166 | 170 | loss_saved | 0.83675 | -0.675039 | 104.345128 |
| KXBTC15M-26MAY071115-15 | yes | 84 | 91 | yes | 14 | 32 | -18 | winner_clipped | 0.888844 | -4.884431 | 86.576464 |
| KXBTC15M-26MAY071145-45 | yes | 77 | 99 | yes | 44 | 46 | -2 | winner_clipped | 0.982146 | -17.214598 | 70.81325 |
| KXBTC15M-26MAY071200-00 | no | 77 | 98 | no | 42 | 46 | -4 | winner_clipped | 0.961165 | -19.116535 | 50.875261 |
| KXBTC15M-26MAY071215-15 | no | 84 | 76 | no | -16 | 32 | -48 | winner_clipped | 0.797661 | 4.233856 | 96.827686 |
| KXBTC15M-26MAY071215-15 | no | 78 | 79 | no | 2 | 44 | -42 | winner_clipped | 0.752304 | 2.769646 | 92.80836 |
| KXBTC15M-26MAY071215-15 | no | 80 | 76 | no | -8 | 40 | -48 | winner_clipped | 0.765822 | 3.417815 | 88.514362 |
| KXBTC15M-26MAY071230-30 | yes | 77 | 72 | yes | -10 | 46 | -56 | winner_clipped | 0.749378 | 2.062161 | 101.28484 |
| KXBTC15M-26MAY071230-30 | yes | 84 | 65 | yes | -38 | 32 | -70 | winner_clipped | 0.662903 | 17.709724 | 94.034749 |
| KXBTC15M-26MAY071315-15 | yes | 80 | 77 | yes | -6 | 40 | -46 | winner_clipped | 0.798341 | -0.834147 | 71.151858 |
| KXBTC15M-26MAY071315-15 | yes | 81 | 74 | yes | -14 | 38 | -52 | winner_clipped | 0.784166 | 2.583397 | 64.083804 |
| KXBTC15M-26MAY071315-15 | yes | 78 | 94 | yes | 32 | 44 | -12 | winner_clipped | 0.927498 | -14.749774 | 56.560376 |
