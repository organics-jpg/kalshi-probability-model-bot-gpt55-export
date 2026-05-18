# v28 Shadow Entry Policy Bakeoff

- Scope: approved entries plus actionable rejected observations only.
- Rule: one selected side per market, first qualifying observation by telemetry time.
- Warning: this is not an optimizer; tiny samples are descriptive only.

- Watched markets: `181`
- Observation rows: `6798`

## Ranked Policies

| rank | policy | entries | resolved/settled | wins | losses | coverage | gross c | raw brier | book brier | best fv brier | best fv vs raw | added rejects |
|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | book_plus_03_cheap_convex | 92 | 92/92 | 32 | 60 | 50.82872928176796 | 916.0 | 0.22329008371484782 | 0.218825 | 0.2266109659033614 | 0.003320882188513591 | 92 |
| 2 | p50_book_plus_05_edge_nonnegative | 151 | 151/151 | 96 | 55 | 83.42541436464089 | 890.0 | 0.20385725773016555 | 0.19363509933774836 | 0.19489171166292715 | -0.0089655460672384 | 113 |
| 3 | book_plus_05_no_cheap_yes_boundary | 164 | 164/164 | 92 | 72 | 90.60773480662984 | 646.0 | 0.20840953194083536 | 0.19598353658536585 | 0.19587317732192683 | -0.012536354618908535 | 133 |
| 4 | baseline_v28_approved | 107 | 107/107 | 91 | 16 | 59.11602209944752 | 494.0 | 0.12616712376902806 | 0.1280448598130841 | 0.12616712376902806 | 0.0 | 0 |
| 5 | p55_edge_nonnegative | 151 | 151/151 | 100 | 51 | 83.42541436464089 | 305.0 | 0.21040178465788742 | 0.19560993377483443 | 0.20669907412318544 | -0.003702710534701975 | 126 |
| 6 | book_plus_05 | 169 | 169/169 | 89 | 80 | 93.37016574585635 | 132.0 | 0.20761872002145562 | 0.19221656804733728 | 0.19545326346819528 | -0.012165456553260345 | 139 |
| 7 | book_plus_02_avoid_coinflip | 171 | 171/171 | 91 | 80 | 94.47513812154696 | -27.0 | 0.21433770921084794 | 0.2073654970760234 | 0.21421567503366518 | -0.00012203417718276155 | 161 |
| 8 | book_plus_02_avoid_coinflip_liquid | 171 | 171/171 | 91 | 80 | 94.47513812154696 | -56.0 | 0.21358619017374855 | 0.20660526315789476 | 0.21336554323834794 | -0.0002206469354006091 | 160 |
| 9 | book_plus_03 | 175 | 175/175 | 87 | 88 | 96.68508287292818 | -303.0 | 0.21487392635148572 | 0.20329142857142857 | 0.20263374546558002 | -0.0122401808859057 | 167 |
| 10 | book_plus_03_avoid_coinflip | 171 | 171/171 | 88 | 83 | 94.47513812154696 | -873.0 | 0.20328542656537427 | 0.19226608187134503 | 0.2029254248085731 | -0.00036000175680117596 | 157 |
| 11 | p65_large_disagreement_anchor_plus_02 | 145 | 145/145 | 101 | 44 | 80.11049723756905 | -1198.0 | 0.2032607145886276 | 0.19431034482758622 | 0.20225100411206207 | -0.001009710476565534 | 118 |
| 12 | p65_v28_premium_anchor_plus_02 | 144 | 144/144 | 100 | 44 | 79.55801104972376 | -1376.0 | 0.2037920159712986 | 0.1945486111111111 | 0.20277529361642363 | -0.0010167223548749604 | 116 |
| 13 | p65_book_plus_03 | 145 | 145/145 | 97 | 48 | 80.11049723756905 | -1486.0 | 0.22036021485555862 | 0.19297931034482757 | 0.2198882122444569 | -0.0004720026111017239 | 112 |
| 14 | p65_book_plus_02 | 152 | 152/152 | 101 | 51 | 83.97790055248619 | -1542.0 | 0.21918507574884868 | 0.1941638157894737 | 0.21822186509686184 | -0.0009632106519868455 | 125 |

## Selected Rows

| policy | market | source | side | reason | p | ask | delta | edge c | abs d sigma | recross | stc | gross c | result |
|---|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| p50_book_plus_05_edge_nonnegative | KXBTC15M-26MAY070600-00 | rejected_actionable | yes | p_below_floor | 0.72396 | 67.0 | 0.05396000000000001 | 1.396006 | 0.495921 | 0.39442076468786447 | 534.677 | 66 | yes |
| p50_book_plus_05_edge_nonnegative | KXBTC15M-26MAY070615-15 | rejected_actionable | no | p_below_floor | 0.610872 | 28.0 | 0.33087199999999994 | 29.587162 | 0.275276 | 0.6454912835956723 | 702.26 | 144 | no |
| p50_book_plus_05_edge_nonnegative | KXBTC15M-26MAY070630-30 | rejected_actionable | yes | p_below_floor | 0.606974 | 47.0 | 0.13697400000000004 | 9.697411 | 0.230767 | 0.8264694476309769 | 875.963 | -94 | no |
| p50_book_plus_05_edge_nonnegative | KXBTC15M-26MAY070645-45 | approved_entry | yes | approved_entry | 0.895399 | 81.0 | 0.08539899999999989 | 5.039895 | 1.013529 | 0.36879792565874936 | 816.468 | 38 | yes |
| p50_book_plus_05_edge_nonnegative | KXBTC15M-26MAY070700-00 | rejected_actionable | yes | p_below_floor | 0.654812 | 56.0 | 0.0948119999999999 | 5.481241 | 0.375634 | 0.7601242607081649 | 869.636 | -112 | no |
| p50_book_plus_05_edge_nonnegative | KXBTC15M-26MAY070715-15 | rejected_actionable | yes | p_below_floor | 0.560435 | 51.0 | 0.05043500000000001 | 1.043473 | 0.157545 | 0.8772318276222708 | 812.253 | 98 | yes |
| p50_book_plus_05_edge_nonnegative | KXBTC15M-26MAY070730-30 | rejected_actionable | yes | p_below_floor | 0.530778 | 46.0 | 0.07077799999999995 | 3.077802 | 0.091964 | 0.9361206885177036 | 819.643 | -92 | no |
| p50_book_plus_05_edge_nonnegative | KXBTC15M-26MAY070745-45 | approved_entry | yes | approved_entry | 0.903807 | 68.0 | 0.22380699999999998 | 18.380737 | 1.081343 | 0.1975936328082862 | 474.481 | 34 | yes |
| p50_book_plus_05_edge_nonnegative | KXBTC15M-26MAY070800-00 | rejected_actionable | yes | p_below_floor | 0.536385 | 45.0 | 0.08638499999999999 | 4.638461 | 0.080069 | 0.8654745987079465 | 771.226 | -90 | no |
| p50_book_plus_05_edge_nonnegative | KXBTC15M-26MAY070815-15 | rejected_actionable | yes | p_below_floor | 0.501147 | 44.0 | 0.06114700000000001 | 2.114684 | 0.024626 | 1.0671612266357298 | 882.524 | 112 | yes |
| p50_book_plus_05_edge_nonnegative | KXBTC15M-26MAY070830-30 | rejected_actionable | yes | p_below_floor | 0.514492 | 41.0 | 0.10449199999999997 | 6.449161 | 0.078942 | 0.9527908104356088 | 811.825 | -82 | no |
| p50_book_plus_05_edge_nonnegative | KXBTC15M-26MAY070845-45 | rejected_actionable | yes | p_below_floor | 0.596088 | 45.0 | 0.14608799999999994 | 10.608794 | 0.236616 | 0.5965758829179154 | 593.135 | 110 | yes |
| p50_book_plus_05_edge_nonnegative | KXBTC15M-26MAY070900-00 | rejected_actionable | no | p_below_floor | 0.606083 | 52.0 | 0.08608300000000002 | 4.608252 | 0.253011 | 0.7010000307286993 | 713.192 | -104 | yes |
| p50_book_plus_05_edge_nonnegative | KXBTC15M-26MAY070915-15 | rejected_actionable | no | p_below_floor | 0.829868 | 77.0 | 0.05986800000000003 | 2.486843 | 0.794638 | 0.435112578184384 | 773.03 | 46 | no |
| p50_book_plus_05_edge_nonnegative | KXBTC15M-26MAY070930-30 | rejected_actionable | yes | edge_below_floor | 0.851432 | 80.0 | 0.05143199999999992 | 1.643179 | 0.861823 | 0.383161883619703 | 687.852 | 40 | yes |
| p50_book_plus_05_edge_nonnegative | KXBTC15M-26MAY070945-45 | rejected_actionable | no | p_below_floor | 0.532085 | 48.0 | 0.05208500000000005 | 1.208522 | 0.067417 | 1.0888633329884525 | 860.716 | 104 | no |
| p50_book_plus_05_edge_nonnegative | KXBTC15M-26MAY071000-00 | rejected_actionable | no | p_below_floor | 0.720981 | 66.0 | 0.06098099999999995 | 2.098125 | 0.560582 | 0.7052528853810713 | 848.956 | 68 | no |
| p50_book_plus_05_edge_nonnegative | KXBTC15M-26MAY071015-15 | approved_entry | no | approved_entry | 0.861092 | 78.0 | 0.08109199999999994 | 4.609185 | 0.936079 | 0.41762272221317515 | 583.765 | 2 | yes |
| p50_book_plus_05_edge_nonnegative | KXBTC15M-26MAY071030-30 | approved_entry | no | approved_entry | 0.852355 | 77.0 | 0.08235499999999996 | 4.735533 | 0.888885 | 0.5927426169341831 | 831.511 | -24 | no |
| p50_book_plus_05_edge_nonnegative | KXBTC15M-26MAY071045-45 | rejected_actionable | no | p_below_floor | 0.826507 | 73.0 | 0.09650700000000001 | 6.15074 | 0.817739 | 0.5931179124200848 | 822.844 | 54 | no |
| p50_book_plus_05_edge_nonnegative | KXBTC15M-26MAY071100-00 | approved_entry | yes | approved_entry | 0.884041 | 83.0 | 0.054041000000000006 | 2.404098 | 1.010241 | 0.30500573389101787 | 498.551 | 4 | no |
| p50_book_plus_05_edge_nonnegative | KXBTC15M-26MAY071115-15 | approved_entry | yes | approved_entry | 0.891894 | 84.0 | 0.051893999999999996 | 2.189408 | 1.052672 | 0.21995572150628764 | 388.98 | 14 | yes |
| p50_book_plus_05_edge_nonnegative | KXBTC15M-26MAY071130-30 | approved_entry | no | approved_entry | 0.916601 | 85.0 | 0.06660100000000002 | 3.660104 | 1.183451 | 0.33188369997953837 | 681.063 | 30 | no |
| p50_book_plus_05_edge_nonnegative | KXBTC15M-26MAY071145-45 | rejected_actionable | yes | p_below_floor | 0.742383 | 69.0 | 0.05238300000000007 | 1.738254 | 0.54163 | 0.8425684056643667 | 838.927 | 62 | yes |
| p50_book_plus_05_edge_nonnegative | KXBTC15M-26MAY071200-00 | rejected_actionable | yes | p_below_floor | 0.588818 | 53.0 | 0.058817999999999926 | 1.881758 | 0.195956 | 0.2279178112729362 | 165.619 | -106 | no |
| p50_book_plus_05_edge_nonnegative | KXBTC15M-26MAY071215-15 | rejected_actionable | yes | p_below_floor | 0.530384 | 47.0 | 0.06038399999999999 | 2.038384 | 0.026648 | 1.2451451719991744 | 782.308 | -94 | no |
| p50_book_plus_05_edge_nonnegative | KXBTC15M-26MAY071230-30 | rejected_actionable | yes | p_below_floor | 0.563905 | 51.0 | 0.05390499999999998 | 1.390518 | 0.13662 | 0.8384739774722361 | 562.23 | 98 | yes |
| p50_book_plus_05_edge_nonnegative | KXBTC15M-26MAY071245-45 | rejected_actionable | yes | p_below_floor | 0.6248 | 56.0 | 0.06479999999999997 | 2.479997 | 0.321099 | 0.8824764177724596 | 718.733 | -112 | no |
| p50_book_plus_05_edge_nonnegative | KXBTC15M-26MAY071300-00 | rejected_actionable | yes | p_below_floor | 0.502685 | 43.0 | 0.07268500000000006 | 3.268521 | 0.012349 | 0.5360356020400235 | 366.622 | -86 | no |
| p50_book_plus_05_edge_nonnegative | KXBTC15M-26MAY071315-15 | rejected_actionable | yes | p_below_floor | 0.581409 | 52.0 | 0.061408999999999936 | 2.140866 | 0.159495 | 1.030463505524254 | 818.854 | 96 | yes |
