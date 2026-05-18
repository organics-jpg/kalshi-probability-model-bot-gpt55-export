# v28 Reentry Throttle Candidates

Shadow-only counterfactual. Physical question: after the model exits a side, does reentering the same side in the same 15m market add edge or just chase turbulence?

## Summary

| policy | trades | settled | wins | losses | markets | gross c | hold c | delta vs current c |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| current_v28 | 173 | 173 | 94 | 75 | 107 | 823.0 | 2304.0 | 0.0 |
| no_same_side_after_model_exit | 173 | 173 | 94 | 75 | 107 | 823.0 | 2304.0 | 0.0 |
| no_same_side_reentry | 116 | 116 | 62 | 51 | 107 | 532.0 | 1356.0 | -291.0 |
| first_entry_per_market | 107 | 107 | 57 | 47 | 107 | 494.0 | 1332.0 | -329.0 |

## Current Rows

| market | side | entry | exit | result | gross c | hold c | exit reason |
|---|---|---:|---:|---|---:|---:|---|
| KXBTC15M-26MAY051300-00 | yes | 81 | 99 | yes | 36 | 38 | exit_trigger |
| KXBTC15M-26MAY051330-30 | yes | 82 | 82 | yes | 0 | 36 | exit_trigger |
| KXBTC15M-26MAY051545-45 | yes | 75 | 83 | yes | 16 | 50 | exit_trigger |
| KXBTC15M-26MAY051615-15 | no | 76 | 64 | yes | -24 | -152 | exit_trigger |
| KXBTC15M-26MAY051615-15 | yes | 56 | 72 | yes | 32 | 88 | exit_trigger |
| KXBTC15M-26MAY051715-15 | yes | 82 | 68 | no | -28 | -164 | exit_trigger |
| KXBTC15M-26MAY051715-15 | yes | 69 | 45 | no | -48 | -138 | exit_trigger |
| KXBTC15M-26MAY051715-15 | yes | 40 | 29 | no | -22 | -80 | exit_trigger |
| KXBTC15M-26MAY051745-45 | no | 77 | 72 | no | -10 | 46 | exit_trigger |
| KXBTC15M-26MAY051745-45 | no | 80 | 79 | no | -2 | 40 | exit_trigger |
| KXBTC15M-26MAY051800-00 | yes | 78 | 66 | yes | -24 | 44 | exit_trigger |
| KXBTC15M-26MAY051800-00 | yes | 80 | 100 | yes | 40 | 40 | exit_trigger |
| KXBTC15M-26MAY051815-15 | yes | 81 | 93 | no | 24 | -162 | exit_trigger |
| KXBTC15M-26MAY051830-30 | no | 80 | 34 | yes | -92 | -160 | exit_trigger |
| KXBTC15M-26MAY051845-45 | no | 79 | None | no | 42 | 42 |  |
| KXBTC15M-26MAY051900-00 | yes | 80 | None | yes | 40 | 40 |  |
| KXBTC15M-26MAY051915-15 | yes | 82 | 99 | yes | 34 | 36 | exit_trigger |
| KXBTC15M-26MAY051945-45 | yes | 74 | 87 | yes | 26 | 52 | exit_trigger |
| KXBTC15M-26MAY052015-15 | yes | 85 | None | yes | 30 | 30 |  |
| KXBTC15M-26MAY052045-45 | yes | 79 | 70 | no | -18 | -158 | exit_trigger |
| KXBTC15M-26MAY052045-45 | yes | 83 | 90 | no | 14 | -166 | exit_trigger |
| KXBTC15M-26MAY052100-00 | no | 79 | 64 | yes | -30 | -158 | exit_trigger |
| KXBTC15M-26MAY052100-00 | yes | 56 | 73 | yes | 34 | 88 | exit_trigger |
| KXBTC15M-26MAY052100-00 | yes | 90 | 96 | yes | 12 | 20 | exit_trigger |
| KXBTC15M-26MAY052115-15 | yes | 78 | None | yes | 44 | 44 |  |
| KXBTC15M-26MAY052145-45 | yes | 85 | 95 | yes | 20 | 30 | exit_trigger |
| KXBTC15M-26MAY052200-00 | yes | 79 | 85 | yes | 12 | 42 | exit_trigger |
| KXBTC15M-26MAY052215-15 | no | 83 | 76 | no | -14 | 34 | exit_trigger |
| KXBTC15M-26MAY052245-45 | no | 40 | 27 | yes | -26 | -80 | exit_trigger |
| KXBTC15M-26MAY052300-00 | yes | 85 | 99 | yes | 28 | 30 | exit_trigger |
| KXBTC15M-26MAY052315-15 | yes | 81 | 62 | yes | -38 | 38 | exit_trigger |
| KXBTC15M-26MAY060045-45 | no | 79 | 74 | no | -10 | 42 | exit_trigger |
| KXBTC15M-26MAY060045-45 | no | 85 | 95 | no | 20 | 30 | exit_trigger |
| KXBTC15M-26MAY060100-00 | no | 78 | 76 | no | -4 | 44 | exit_trigger |
| KXBTC15M-26MAY060145-45 | no | 88 | 99 | no | 22 | 24 | exit_trigger |
| KXBTC15M-26MAY060200-00 | yes | 80 | 74 | yes | -12 | 40 | exit_trigger |
| KXBTC15M-26MAY060200-00 | yes | 81 | 84 | yes | 6 | 38 | exit_trigger |
| KXBTC15M-26MAY060215-15 | yes | 77 | 69 | no | -16 | -154 | exit_trigger |
| KXBTC15M-26MAY060215-15 | yes | 83 | 70 | no | -26 | -166 | exit_trigger |
| KXBTC15M-26MAY060215-15 | no | 80 | 97 | no | 34 | 40 | exit_trigger |
| KXBTC15M-26MAY060230-30 | yes | 84 | 74 | yes | -20 | 32 | exit_trigger |
| KXBTC15M-26MAY060245-45 | yes | 80 | 76 | yes | -8 | 40 | exit_trigger |
| KXBTC15M-26MAY060245-45 | yes | 77 | 74 | yes | -6 | 46 | exit_trigger |
| KXBTC15M-26MAY060245-45 | yes | 76 | 95 | yes | 38 | 48 | exit_trigger |
| KXBTC15M-26MAY060300-00 | yes | 81 | 74 | yes | -14 | 38 | exit_trigger |
| KXBTC15M-26MAY060300-00 | yes | 81 | 66 | yes | -30 | 38 | exit_trigger |
| KXBTC15M-26MAY060300-00 | yes | 80 | 69 | yes | -22 | 40 | exit_trigger |
| KXBTC15M-26MAY060300-00 | yes | 80 | 94 | yes | 28 | 40 | exit_trigger |
| KXBTC15M-26MAY060315-15 | yes | 86 | 99 | yes | 26 | 28 | exit_trigger |
| KXBTC15M-26MAY060330-30 | yes | 79 | 53 | yes | -52 | 42 | exit_trigger |
| KXBTC15M-26MAY060330-30 | no | 9 | None | yes | -18 | -18 |  |
| KXBTC15M-26MAY060345-45 | no | 78 | 95 | no | 34 | 44 | exit_trigger |
| KXBTC15M-26MAY060445-45 | yes | 90 | 99 | yes | 18 | 20 | exit_trigger |
| KXBTC15M-26MAY060500-00 | yes | 79 | None | yes | 42 | 42 |  |
| KXBTC15M-26MAY060515-15 | no | 79 | 66 | no | -26 | 42 | exit_trigger |
| KXBTC15M-26MAY060515-15 | no | 74 | 95 | no | 42 | 52 | exit_trigger |
| KXBTC15M-26MAY060530-30 | no | 78 | 95 | no | 34 | 44 | exit_trigger |
| KXBTC15M-26MAY060545-45 | yes | 90 | None | yes | 20 | 20 |  |
| KXBTC15M-26MAY060600-00 | no | 75 | 81 | no | 12 | 50 | exit_trigger |
| KXBTC15M-26MAY060615-15 | yes | 75 | 60 | yes | -30 | 50 | exit_trigger |
| KXBTC15M-26MAY060615-15 | yes | 88 | None | yes | 24 | 24 |  |
| KXBTC15M-26MAY060630-30 | yes | 79 | 73 | yes | -12 | 42 | exit_trigger |
| KXBTC15M-26MAY060630-30 | yes | 85 | 99 | yes | 28 | 30 | exit_trigger |
| KXBTC15M-26MAY060645-45 | yes | 82 | 74 | yes | -16 | 36 | exit_trigger |
| KXBTC15M-26MAY060645-45 | yes | 78 | 72 | yes | -12 | 44 | exit_trigger |
| KXBTC15M-26MAY060645-45 | yes | 80 | 97 | yes | 34 | 40 | exit_trigger |
| KXBTC15M-26MAY060700-00 | no | 84 | 80 | yes | -8 | -168 | exit_trigger |
| KXBTC15M-26MAY060700-00 | yes | 75 | 64 | yes | -22 | 50 | exit_trigger |
| KXBTC15M-26MAY060700-00 | yes | 77 | 62 | yes | -30 | 46 | exit_trigger |
| KXBTC15M-26MAY060700-00 | yes | 83 | 89 | yes | 12 | 34 | exit_trigger |
| KXBTC15M-26MAY060715-15 | yes | 81 | 93 | yes | 24 | 38 | exit_trigger |
| KXBTC15M-26MAY060715-15 | yes | 89 | 99 | yes | 20 | 22 | exit_trigger |
| KXBTC15M-26MAY060730-30 | yes | 84 | None | yes | 32 | 32 |  |
| KXBTC15M-26MAY060745-45 | yes | 69 | 57 | no | -24 | -138 | exit_trigger |
| KXBTC15M-26MAY060745-45 | yes | 78 | 43 | no | -70 | -156 | exit_trigger |
| KXBTC15M-26MAY060800-00 | yes | 79 | 70 | yes | -18 | 42 | exit_trigger |
| KXBTC15M-26MAY060800-00 | yes | 66 | 50 | yes | -32 | 68 | exit_trigger |
| KXBTC15M-26MAY060815-15 | no | 79 | None | no | 42 | 42 |  |
| KXBTC15M-26MAY060830-30 | yes | 76 | 100 | yes | 48 | 48 | exit_trigger |
| KXBTC15M-26MAY060900-00 | yes | 78 | 73 | no | -10 | -156 | exit_trigger |
| KXBTC15M-26MAY060900-00 | yes | 78 | 40 | no | -76 | -156 | exit_trigger |
| KXBTC15M-26MAY060900-00 | no | 73 | 65 | no | -16 | 54 | exit_trigger |
| KXBTC15M-26MAY060900-00 | no | 79 | 96 | no | 34 | 42 | exit_trigger |
| KXBTC15M-26MAY060915-15 | no | 70 | 70 | no | 0 | 60 | exit_trigger |
| KXBTC15M-26MAY060915-15 | no | 75 | 100 | no | 50 | 50 | exit_trigger |
| KXBTC15M-26MAY060930-30 | no | 76 | 66 | no | -20 | 48 | exit_trigger |
| KXBTC15M-26MAY060930-30 | no | 76 | 69 | no | -14 | 48 | exit_trigger |
| KXBTC15M-26MAY060930-30 | no | 73 | 72 | no | -3 | 54 | exit_trigger |
| KXBTC15M-26MAY060930-30 | no | 77 | None | no | 46 | 46 |  |
| KXBTC15M-26MAY060945-45 | no | 59 | 51 | no | -16 | 82 | exit_trigger |
| KXBTC15M-26MAY060945-45 | no | 70 | 62 | no | -16 | 60 | exit_trigger |
| KXBTC15M-26MAY060945-45 | no | 71 | 65 | no | -12 | 58 | exit_trigger |
| KXBTC15M-26MAY060945-45 | no | 72 | 96 | no | 48 | 56 | exit_trigger |
| KXBTC15M-26MAY061000-00 | no | 65 | None | no | 70 | 70 |  |
| KXBTC15M-26MAY061015-15 | no | 68 | 65 | no | -6 | 64 | exit_trigger |
| KXBTC15M-26MAY061015-15 | no | 70 | 70 | no | 0 | 60 | exit_trigger |
| KXBTC15M-26MAY061015-15 | no | 73 | None | no | 54 | 54 |  |
| KXBTC15M-26MAY061030-30 | yes | 78 | 70 | yes | -16 | 44 | exit_trigger |
| KXBTC15M-26MAY061030-30 | yes | 78 | 73 | yes | -10 | 44 | exit_trigger |
| KXBTC15M-26MAY061030-30 | yes | 74 | None | yes | 52 | 52 |  |
| KXBTC15M-26MAY061045-45 | yes | 80 | 77 | yes | -6 | 40 | exit_trigger |
| KXBTC15M-26MAY061045-45 | yes | 84 | 98 | yes | 28 | 32 | exit_trigger |
| KXBTC15M-26MAY061100-00 | no | 83 | 63 | no | -40 | 34 | exit_trigger |
| KXBTC15M-26MAY061100-00 | no | 81 | None | no | 38 | 38 |  |
| KXBTC15M-26MAY061130-30 | yes | 80 | None | yes | 40 | 40 |  |
| KXBTC15M-26MAY061200-00 | yes | 82 | 90 | yes | 16 | 36 | exit_trigger |
| KXBTC15M-26MAY061300-00 | yes | 80 | 65 | no | -30 | -160 | exit_trigger |
| KXBTC15M-26MAY061400-00 | no | 89 | 84 | no | -10 | 22 | exit_trigger |
| KXBTC15M-26MAY061415-15 | no | 88 | None | no | 24 | 24 |  |
| KXBTC15M-26MAY061445-45 | no | 88 | 77 | no | -22 | 24 | exit_trigger |
| KXBTC15M-26MAY061445-45 | no | 90 | 99 | no | 18 | 20 | exit_trigger |
| KXBTC15M-26MAY061545-45 | yes | 84 | 95 | yes | 22 | 32 | exit_trigger |
| KXBTC15M-26MAY061615-15 | yes | 90 | 94 | yes | 8 | 20 | exit_trigger |
| KXBTC15M-26MAY061645-45 | no | 76 | None | no | 48 | 48 |  |
| KXBTC15M-26MAY061800-00 | no | 67 | 24 | no | -86 | 66 | exit_trigger |
| KXBTC15M-26MAY061815-15 | no | 84 | 96 | no | 24 | 32 | exit_trigger |
| KXBTC15M-26MAY061830-30 | no | 89 | 99 | no | 20 | 22 | exit_trigger |
| KXBTC15M-26MAY061900-00 | yes | 90 | None | yes | 20 | 20 |  |
| KXBTC15M-26MAY061915-15 | no | 87 | 99 | no | 24 | 26 | exit_trigger |
| KXBTC15M-26MAY062015-15 | no | 42 | 12 | no | -60 | 116 | exit_trigger |
| KXBTC15M-26MAY062015-15 | yes | 86 | 90 | no | 8 | -172 | exit_trigger |
| KXBTC15M-26MAY062015-15 | yes | 67 | None | no | -134 | -134 |  |
| KXBTC15M-26MAY062030-30 | no | 67 | 83 | no | 32 | 66 | exit_trigger |
| KXBTC15M-26MAY062045-45 | no | 80 | 92 | no | 24 | 40 | exit_trigger |
| KXBTC15M-26MAY062100-00 | yes | 83 | 81 | yes | -4 | 34 | exit_trigger |
| KXBTC15M-26MAY062100-00 | yes | 84 | 74 | yes | -20 | 32 | exit_trigger |
| KXBTC15M-26MAY062100-00 | yes | 61 | 68 | yes | 14 | 78 | exit_trigger |
| KXBTC15M-26MAY062115-15 | yes | 73 | 67 | yes | -12 | 54 | exit_trigger |
| KXBTC15M-26MAY062115-15 | no | 69 | 52 | yes | -34 | -138 | exit_trigger |
| KXBTC15M-26MAY062115-15 | yes | 88 | 99 | yes | 22 | 24 | exit_trigger |
| KXBTC15M-26MAY062130-30 | no | 76 | 60 | yes | -32 | -152 | exit_trigger |
| KXBTC15M-26MAY062215-15 | no | 65 | 72 | no | 14 | 70 | exit_trigger |
| KXBTC15M-26MAY062215-15 | no | 84 | 89 | no | 10 | 32 | exit_trigger |
| KXBTC15M-26MAY062245-45 | yes | 86 | 90 | yes | 8 | 28 | exit_trigger |
| KXBTC15M-26MAY062300-00 | yes | 87 | 95 | yes | 16 | 26 | exit_trigger |
| KXBTC15M-26MAY062315-15 | no | 84 | 87 | no | 6 | 32 | exit_trigger |
| KXBTC15M-26MAY070000-00 | no | 78 | 79 | no | 2 | 44 | exit_trigger |
| KXBTC15M-26MAY070015-15 | no | 70 | 69 | yes | -2 | -140 | exit_trigger |
| KXBTC15M-26MAY070030-30 | yes | 82 | 97 | yes | 30 | 36 | exit_trigger |
| KXBTC15M-26MAY070115-15 | yes | 82 | 82 | yes | 0 | 36 | exit_trigger |
| KXBTC15M-26MAY070545-45 | no | 82 | 91 | no | 18 | 36 | exit_trigger |
| KXBTC15M-26MAY070645-45 | yes | 81 | None | yes | 38 | 38 |  |
| KXBTC15M-26MAY070745-45 | yes | 68 | 85 | yes | 34 | 64 | exit_trigger |
| KXBTC15M-26MAY070815-15 | yes | 90 | 91 | yes | 2 | 20 | exit_trigger |
| KXBTC15M-26MAY070830-30 | no | 82 | 91 | no | 18 | 36 | exit_trigger |
| KXBTC15M-26MAY070830-30 | no | 77 | 70 | no | -14 | 46 | exit_trigger |
| KXBTC15M-26MAY070830-30 | no | 77 | None | no | 46 | 46 |  |
| KXBTC15M-26MAY070915-15 | no | 77 | None | no | 46 | 46 |  |
| KXBTC15M-26MAY070930-30 | yes | 80 | 97 | yes | 34 | 40 | exit_trigger |
| KXBTC15M-26MAY070945-45 | no | 69 | None | no | 62 | 62 |  |
| KXBTC15M-26MAY071000-00 | no | 73 | 55 | no | -36 | 54 | exit_trigger |
| KXBTC15M-26MAY071000-00 | no | 71 | 79 | no | 16 | 58 | exit_trigger |
| KXBTC15M-26MAY071015-15 | no | 78 | 79 | yes | 2 | -156 | exit_trigger |
| KXBTC15M-26MAY071015-15 | no | 81 | 73 | yes | -16 | -162 | exit_trigger |
| KXBTC15M-26MAY071015-15 | yes | 84 | 94 | yes | 20 | 32 | exit_trigger |
| KXBTC15M-26MAY071030-30 | no | 77 | 65 | no | -24 | 46 | exit_trigger |
| KXBTC15M-26MAY071030-30 | no | 76 | None | no | 48 | 48 |  |
| KXBTC15M-26MAY071045-45 | no | 74 | 69 | no | -10 | 52 | exit_trigger |
| KXBTC15M-26MAY071045-45 | no | 75 | None | no | 50 | 50 |  |
| KXBTC15M-26MAY071100-00 | yes | 83 | 85 | no | 4 | -166 | exit_trigger |
| KXBTC15M-26MAY071115-15 | yes | 84 | 91 | yes | 14 | 32 | exit_trigger |
| KXBTC15M-26MAY071130-30 | no | 85 | None | no | 30 | 30 |  |
| KXBTC15M-26MAY071145-45 | yes | 77 | 99 | yes | 44 | 46 | exit_trigger |
| KXBTC15M-26MAY071200-00 | no | 77 | 98 | no | 42 | 46 | exit_trigger |
| KXBTC15M-26MAY071215-15 | no | 84 | 76 | no | -16 | 32 | exit_trigger |
| KXBTC15M-26MAY071215-15 | no | 78 | 79 | no | 2 | 44 | exit_trigger |
| KXBTC15M-26MAY071215-15 | no | 80 | 76 | no | -8 | 40 | exit_trigger |
| KXBTC15M-26MAY071230-30 | yes | 77 | 72 | yes | -10 | 46 | exit_trigger |
| KXBTC15M-26MAY071230-30 | yes | 84 | 65 | yes | -38 | 32 | exit_trigger |
| KXBTC15M-26MAY071230-30 | yes | 80 | None | yes | 40 | 40 |  |
| KXBTC15M-26MAY071315-15 | yes | 80 | 77 | yes | -6 | 40 | exit_trigger |
| KXBTC15M-26MAY071315-15 | yes | 81 | 74 | yes | -14 | 38 | exit_trigger |
| KXBTC15M-26MAY071315-15 | yes | 78 | 94 | yes | 32 | 44 | exit_trigger |
