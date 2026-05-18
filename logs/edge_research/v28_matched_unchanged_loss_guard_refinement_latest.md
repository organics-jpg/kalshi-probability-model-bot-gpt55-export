# v28 Matched-Unchanged Loss Guard Refinement

Research-only diagnostic. No live bot changes or orders.

- Generated UTC: `2026-05-07T09:28:34.554975+00:00`
- Base rule: `abs_d_sigma <= 0.888798 AND exit_cents >= 51`
- Base selected/helpful/harmful: `30/26/3`
- Base hold delta: `933c`
- Minimum helpful rows for guard scan: `5`

## Interpretation

- Research-only guard scan; this does not freeze, promote, or change an exit rule.
- Base separator selects 30 full-denominator rows with 26/3 helpful/harmful and 933.0c hold delta.
- Best clean guard is `abs_d_sigma <= 0.888798 AND exit_cents >= 51 AND eligible_depth <= 326.6 AND exit_p_hold >= 0.718799`: 21 rows, 20/0 helpful/harmful, 919.0c delta, losses 14 -> 0.
- This is still diagnostic-only because it was selected on historical denominator rows and needs its own frozen post-birth watch before trust.

## Top Clean Guards

| rule | selected | helpful/harmful/flat | current net c | hold net c | hold delta c | losses current -> hold | removed harmful | worst harm c |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| `abs_d_sigma <= 0.888798 AND exit_cents >= 51 AND eligible_depth <= 326.6 AND exit_p_hold >= 0.718799` | 21 | 20/0/1 | 27c | 946c | 919c | 14 -> 0 | 3 | 0c |
| `abs_d_sigma <= 0.888798 AND exit_cents >= 51 AND eligible_depth <= 326.6 AND exit_p_hold >= 0.721102` | 20 | 19/0/1 | 57c | 908c | 851c | 13 -> 0 | 3 | 0c |
| `abs_d_sigma <= 0.888798 AND exit_cents >= 51 AND exit_p_hold >= 0.718799 AND exit_sigma_t_dollars <= 104.221` | 19 | 18/0/1 | 40c | 858c | 818c | 12 -> 0 | 3 | 0c |
| `abs_d_sigma <= 0.888798 AND exit_cents >= 51 AND eligible_depth >= 50 AND exit_sigma_t_dollars <= 104.221` | 17 | 16/0/1 | 14c | 832c | 818c | 10 -> 0 | 3 | 0c |
| `abs_d_sigma <= 0.888798 AND exit_cents >= 51 AND eligible_depth <= 295 AND exit_p_hold >= 0.718799` | 19 | 18/0/1 | 35c | 852c | 817c | 13 -> 0 | 3 | 0c |
| `abs_d_sigma <= 0.888798 AND exit_cents >= 51 AND eligible_depth <= 326.6 AND exit_fair_drawdown_cents <= 5.04976` | 19 | 18/0/1 | 75c | 866c | 791c | 12 -> 0 | 3 | 0c |
| `abs_d_sigma <= 0.888798 AND exit_cents >= 51 AND exit_fair_drawdown_cents <= 5.04976 AND exit_sigma_t_dollars <= 104.221` | 18 | 17/0/1 | 72c | 838c | 766c | 11 -> 0 | 3 | 0c |
| `abs_d_sigma <= 0.888798 AND exit_cents >= 51 AND exit_p_hold >= 0.721102 AND exit_sigma_t_dollars <= 104.221` | 18 | 17/0/1 | 70c | 820c | 750c | 11 -> 0 | 3 | 0c |
| `abs_d_sigma <= 0.888798 AND exit_cents >= 51 AND eligible_depth <= 295 AND exit_p_hold >= 0.721102` | 18 | 17/0/1 | 65c | 814c | 749c | 12 -> 0 | 3 | 0c |
| `abs_d_sigma <= 0.888798 AND exit_cents >= 51 AND exit_p_hold >= 0.718799 AND exit_sigma_t_dollars <= 99.7942` | 17 | 16/0/1 | 34c | 762c | 728c | 11 -> 0 | 3 | 0c |
| `abs_d_sigma <= 0.888798 AND exit_cents >= 51 AND eligible_depth >= 50 AND exit_sigma_t_dollars <= 99.7942` | 15 | 14/0/1 | 8c | 736c | 728c | 9 -> 0 | 3 | 0c |
| `abs_d_sigma <= 0.888798 AND exit_cents >= 51 AND eligible_depth >= 60 AND exit_sigma_t_dollars <= 104.221` | 14 | 13/0/1 | -20c | 708c | 728c | 9 -> 0 | 3 | 0c |
| `abs_d_sigma <= 0.888798 AND exit_cents >= 51 AND eligible_depth >= 50 AND p_side <= 0.853869` | 15 | 14/0/1 | 25c | 748c | 723c | 9 -> 0 | 3 | 0c |
| `abs_d_sigma <= 0.888798 AND exit_cents >= 51 AND eligible_depth <= 326.6 AND exit_p_hold >= 0.738185` | 18 | 17/0/1 | 93c | 806c | 713c | 11 -> 0 | 3 | 0c |
| `abs_d_sigma <= 0.888798 AND exit_cents >= 51 AND exit_sigma_t_dollars >= 54.1617 AND p_side <= 0.853869` | 12 | 12/0/0 | -107c | 600c | 707c | 9 -> 0 | 3 | 0c |
| `abs_d_sigma <= 0.888798 AND exit_cents >= 51 AND exit_sigma_t_dollars >= 59.4285 AND p_side <= 0.853869` | 12 | 12/0/0 | -107c | 600c | 707c | 9 -> 0 | 3 | 0c |
| `abs_d_sigma <= 0.888798 AND exit_cents >= 51 AND eligible_depth >= 50 AND eligible_depth <= 326.6` | 16 | 15/0/1 | 33c | 732c | 699c | 10 -> 0 | 3 | 0c |
| `abs_d_sigma <= 0.888798 AND exit_cents >= 51 AND exit_p_hold >= 0.718799 AND exit_sigma_t_dollars <= 93.0551` | 16 | 15/0/1 | 22c | 720c | 698c | 11 -> 0 | 3 | 0c |
| `abs_d_sigma <= 0.888798 AND exit_cents >= 51 AND eligible_depth <= 295 AND exit_fair_drawdown_cents <= 5.04976` | 17 | 16/0/1 | 83c | 772c | 689c | 11 -> 0 | 3 | 0c |
| `abs_d_sigma <= 0.888798 AND exit_cents >= 51 AND eligible_depth >= 50 AND exit_cents <= 70` | 10 | 10/0/0 | -172c | 516c | 688c | 9 -> 0 | 3 | 0c |

## Top Overall Guards

| rule | selected | helpful/harmful/flat | current net c | hold net c | hold delta c | losses current -> hold | removed harmful | worst harm c |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| `abs_d_sigma <= 0.888798 AND exit_cents >= 51 AND eligible_depth <= 326.6 AND exit_p_hold >= 0.718799` | 21 | 20/0/1 | 27c | 946c | 919c | 14 -> 0 | 3 | 0c |
| `abs_d_sigma <= 0.888798 AND exit_cents >= 51 AND eligible_depth <= 326.6 AND exit_p_hold >= 0.721102` | 20 | 19/0/1 | 57c | 908c | 851c | 13 -> 0 | 3 | 0c |
| `abs_d_sigma <= 0.888798 AND exit_cents >= 51 AND exit_p_hold >= 0.718799 AND exit_sigma_t_dollars <= 104.221` | 19 | 18/0/1 | 40c | 858c | 818c | 12 -> 0 | 3 | 0c |
| `abs_d_sigma <= 0.888798 AND exit_cents >= 51 AND eligible_depth >= 50 AND exit_sigma_t_dollars <= 104.221` | 17 | 16/0/1 | 14c | 832c | 818c | 10 -> 0 | 3 | 0c |
| `abs_d_sigma <= 0.888798 AND exit_cents >= 51 AND eligible_depth <= 295 AND exit_p_hold >= 0.718799` | 19 | 18/0/1 | 35c | 852c | 817c | 13 -> 0 | 3 | 0c |
| `abs_d_sigma <= 0.888798 AND exit_cents >= 51 AND eligible_depth <= 326.6 AND exit_fair_drawdown_cents <= 5.04976` | 19 | 18/0/1 | 75c | 866c | 791c | 12 -> 0 | 3 | 0c |
| `abs_d_sigma <= 0.888798 AND exit_cents >= 51 AND exit_fair_drawdown_cents <= 5.04976 AND exit_sigma_t_dollars <= 104.221` | 18 | 17/0/1 | 72c | 838c | 766c | 11 -> 0 | 3 | 0c |
| `abs_d_sigma <= 0.888798 AND exit_cents >= 51 AND exit_p_hold >= 0.721102 AND exit_sigma_t_dollars <= 104.221` | 18 | 17/0/1 | 70c | 820c | 750c | 11 -> 0 | 3 | 0c |
| `abs_d_sigma <= 0.888798 AND exit_cents >= 51 AND eligible_depth <= 295 AND exit_p_hold >= 0.721102` | 18 | 17/0/1 | 65c | 814c | 749c | 12 -> 0 | 3 | 0c |
| `abs_d_sigma <= 0.888798 AND exit_cents >= 51 AND exit_p_hold >= 0.718799 AND exit_sigma_t_dollars <= 99.7942` | 17 | 16/0/1 | 34c | 762c | 728c | 11 -> 0 | 3 | 0c |
| `abs_d_sigma <= 0.888798 AND exit_cents >= 51 AND eligible_depth >= 50 AND exit_sigma_t_dollars <= 99.7942` | 15 | 14/0/1 | 8c | 736c | 728c | 9 -> 0 | 3 | 0c |
| `abs_d_sigma <= 0.888798 AND exit_cents >= 51 AND eligible_depth >= 60 AND exit_sigma_t_dollars <= 104.221` | 14 | 13/0/1 | -20c | 708c | 728c | 9 -> 0 | 3 | 0c |
| `abs_d_sigma <= 0.888798 AND exit_cents >= 51 AND eligible_depth >= 50 AND p_side <= 0.853869` | 15 | 14/0/1 | 25c | 748c | 723c | 9 -> 0 | 3 | 0c |
| `abs_d_sigma <= 0.888798 AND exit_cents >= 51 AND eligible_depth <= 326.6 AND exit_p_hold >= 0.738185` | 18 | 17/0/1 | 93c | 806c | 713c | 11 -> 0 | 3 | 0c |
| `abs_d_sigma <= 0.888798 AND exit_cents >= 51 AND exit_sigma_t_dollars >= 54.1617 AND p_side <= 0.853869` | 12 | 12/0/0 | -107c | 600c | 707c | 9 -> 0 | 3 | 0c |
| `abs_d_sigma <= 0.888798 AND exit_cents >= 51 AND exit_sigma_t_dollars >= 59.4285 AND p_side <= 0.853869` | 12 | 12/0/0 | -107c | 600c | 707c | 9 -> 0 | 3 | 0c |
| `abs_d_sigma <= 0.888798 AND exit_cents >= 51 AND eligible_depth >= 50 AND eligible_depth <= 326.6` | 16 | 15/0/1 | 33c | 732c | 699c | 10 -> 0 | 3 | 0c |
| `abs_d_sigma <= 0.888798 AND exit_cents >= 51 AND exit_p_hold >= 0.718799 AND exit_sigma_t_dollars <= 93.0551` | 16 | 15/0/1 | 22c | 720c | 698c | 11 -> 0 | 3 | 0c |
| `abs_d_sigma <= 0.888798 AND exit_cents >= 51 AND eligible_depth <= 295 AND exit_fair_drawdown_cents <= 5.04976` | 17 | 16/0/1 | 83c | 772c | 689c | 11 -> 0 | 3 | 0c |
| `abs_d_sigma <= 0.888798 AND exit_cents >= 51 AND eligible_depth >= 50 AND exit_cents <= 70` | 10 | 10/0/0 | -172c | 516c | 688c | 9 -> 0 | 3 | 0c |

## Best Guard Kept Helpful Examples

| market | side/result | actual | hold | delta | exit | p_hold | fair dd | gap | p_side | raw edge | abs d |
|---|---|---:|---:|---:|---|---:|---:|---:|---:|---:|---:|
| `KXBTC15M-26MAY060700-00` | yes/yes | -22c | 50c | 72c | exit_trigger@64.000000 | 0.748579 | 0.142079 | 0.108579 | 0.852084 | 8.708443 | 0.872216 |
| `KXBTC15M-26MAY060945-45` | no/no | -12c | 58c | 70c | exit_trigger@65.000000 | 0.735773 | -2.577325 | 0.085773 | 0.861162 | 13.616192 | 0.879528 |
| `KXBTC15M-26MAY051800-00` | yes/yes | -24c | 44c | 68c | exit_trigger@66.000000 | 0.729502 | 5.049756 | 0.069502 | 0.853820 | 5.882043 | 0.877954 |
| `KXBTC15M-26MAY060300-00` | yes/yes | -30c | 38c | 68c | exit_trigger@66.000000 | 0.718799 | 9.120058 | 0.058799 | 0.865870 | 4.086960 | 0.880452 |
| `KXBTC15M-26MAY060800-00` | yes/yes | -18c | 42c | 60c | exit_trigger@70.000000 | 0.738185 | 5.181496 | 0.038185 | 0.850000 | 4.500023 | 0.843583 |
| `KXBTC15M-26MAY061030-30` | yes/yes | -16c | 44c | 60c | exit_trigger@70.000000 | 0.752739 | 2.726149 | 0.052739 | 0.851204 | 5.620359 | 0.866678 |

## Best Guard Removed Harmful Examples

| market | side/result | actual | hold | delta | exit | p_hold | fair dd | gap | p_side | raw edge | abs d |
|---|---|---:|---:|---:|---|---:|---:|---:|---:|---:|---:|
| `KXBTC15M-26MAY060900-00` | yes/no | -10c | -156c | -146c | exit_trigger@73.000000 | 0.789990 | -0.998969 | 0.059990 | 0.856054 | 6.105411 | 0.872054 |
| `KXBTC15M-26MAY052045-45` | yes/no | -18c | -158c | -140c | exit_trigger@70.000000 | 0.650910 | 15.909026 | -0.049090 | 0.851889 | 4.688928 | 0.866186 |
| `KXBTC15M-26MAY051615-15` | no/yes | -24c | -152c | -128c | exit_trigger@64.000000 | 0.698446 | 6.155389 | 0.058446 | 0.855253 | 8.025310 | 0.878092 |
